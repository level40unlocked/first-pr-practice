"""Uploads videos to YouTube through the Data API v3 (resumable upload, optional thumbnail).

Credentials come from the environment: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and a
YOUTUBE_REFRESH_TOKEN issued once for the channel's Google account (see docs/api_setup.md).
Uploads default to private; a publish time turns them into a scheduled release.
Until the Google Cloud project passes YouTube's API audit, YouTube keeps API uploads private.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
THUMBNAIL_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
CHUNK = 8 * 1024 * 1024  # resumable upload chunk; must be a multiple of 256 KiB


class YouTubeError(RuntimeError):
    pass


@dataclass
class VideoMeta:
    title: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    category_id: str = "25"  # News & Politics
    privacy: str = "private"  # private / unlisted / public
    publish_at: datetime | None = None  # scheduled release (UTC); needs privacy "private"
    made_for_kids: bool = False
    language: str = "en"

    def body(self) -> dict:
        if len(self.title) > 100:
            raise YouTubeError(f"title is {len(self.title)} characters; YouTube allows 100")
        if self.privacy not in ("private", "unlisted", "public"):
            raise YouTubeError(f"unknown privacy '{self.privacy}'")
        status = {"privacyStatus": self.privacy, "selfDeclaredMadeForKids": self.made_for_kids}
        if self.publish_at is not None:
            if self.privacy != "private":
                raise YouTubeError("a scheduled video must be uploaded as private")
            when = self.publish_at.astimezone(timezone.utc)
            if when <= datetime.now(timezone.utc):
                raise YouTubeError("publish time is in the past")
            status["publishAt"] = when.strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "snippet": {
                "title": self.title,
                "description": self.description[:5000],
                "tags": self.tags,
                "categoryId": self.category_id,
                "defaultLanguage": self.language,
                "defaultAudioLanguage": self.language,
            },
            "status": status,
        }


def credentials_from_env() -> tuple[str, str, str]:
    names = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise YouTubeError(f"missing environment variables: {', '.join(missing)} (see docs/api_setup.md)")
    return tuple(os.environ[n] for n in names)


class YouTubeUploader:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str,
                 session: requests.Session | None = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.session = session or requests.Session()
        self._token: str | None = None

    @classmethod
    def from_env(cls, session: requests.Session | None = None) -> "YouTubeUploader":
        return cls(*credentials_from_env(), session=session)

    def access_token(self) -> str:
        if self._token is None:
            resp = self.session.post(TOKEN_URL, data={
                "client_id": self.client_id, "client_secret": self.client_secret,
                "refresh_token": self.refresh_token, "grant_type": "refresh_token"}, timeout=30)
            if resp.status_code != 200:
                raise YouTubeError(f"token refresh failed ({resp.status_code}): {resp.text[:300]}")
            self._token = resp.json()["access_token"]
        return self._token

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token()}"}

    def upload(self, video: Path, meta: VideoMeta, log=print) -> str:
        """Resumable upload; returns the new video id."""
        video = Path(video)
        size = video.stat().st_size
        start = self.session.post(
            UPLOAD_URL, params={"uploadType": "resumable", "part": "snippet,status"},
            headers={**self._auth(), "Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": "video/*", "X-Upload-Content-Length": str(size)},
            data=json.dumps(meta.body()), timeout=60)
        if start.status_code != 200 or "Location" not in start.headers:
            raise YouTubeError(f"could not start upload ({start.status_code}): {start.text[:300]}")
        location = start.headers["Location"]

        sent = 0
        with open(video, "rb") as f:
            while sent < size:
                chunk = f.read(CHUNK)
                end = sent + len(chunk) - 1
                resp = self.session.put(location, data=chunk, timeout=300, headers={
                    **self._auth(), "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {sent}-{end}/{size}"})
                if resp.status_code in (200, 201):
                    video_id = resp.json()["id"]
                    log(f"  uploaded {video.name} -> https://youtu.be/{video_id}")
                    return video_id
                if resp.status_code != 308:  # 308 = chunk stored, send the next one
                    raise YouTubeError(f"upload failed at byte {sent} ({resp.status_code}): {resp.text[:300]}")
                sent = int(resp.headers["Range"].split("-")[1]) + 1 if "Range" in resp.headers else end + 1
                f.seek(sent)
                log(f"  {sent * 100 // size}%")
        raise YouTubeError("upload ended without a video id")

    def set_thumbnail(self, video_id: str, image: Path) -> None:
        image = Path(image)
        kind = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
        resp = self.session.post(THUMBNAIL_URL, params={"videoId": video_id},
                                 headers={**self._auth(), "Content-Type": kind},
                                 data=image.read_bytes(), timeout=120)
        if resp.status_code != 200:
            raise YouTubeError(f"thumbnail failed ({resp.status_code}): {resp.text[:300]}")
