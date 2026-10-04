"""Publishes Reels to Instagram through the Instagram API with Instagram Login (graph.instagram.com).

Credentials come from the environment: INSTAGRAM_ACCESS_TOKEN (long-lived, 60 days, refreshable) and
INSTAGRAM_USER_ID. The account must be a Business or Creator account. Setup: docs/instagram_api_setup.md.
The video goes up as a resumable upload straight to Meta, so no public file URL is needed.
The API only publishes immediately; scheduling means running this at the wanted time.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests

API = "https://graph.instagram.com/v21.0"


class InstagramError(RuntimeError):
    pass


def _check(r: requests.Response) -> dict:
    try:
        data = r.json()
    except ValueError:
        data = {"raw": r.text[:300]}
    if not r.ok or "error" in data:
        raise InstagramError(f"{r.status_code}: {data}")
    return data


class InstagramPublisher:
    def __init__(self, token: str, user_id: str):
        self.token, self.user_id = token, user_id

    @classmethod
    def from_env(cls) -> "InstagramPublisher":
        try:
            return cls(os.environ["INSTAGRAM_ACCESS_TOKEN"], os.environ["INSTAGRAM_USER_ID"])
        except KeyError as e:
            raise InstagramError(f"missing environment variable {e}") from None

    def whoami(self) -> dict:
        return _check(requests.get(f"{API}/me", params={"fields": "user_id,username,account_type", "access_token": self.token}, timeout=30))

    def refresh_token(self) -> dict:
        return _check(requests.get("https://graph.instagram.com/refresh_access_token",
                                   params={"grant_type": "ig_refresh_token", "access_token": self.token}, timeout=30))

    def publish_reel(self, video: Path, caption: str, share_to_feed: bool = True, timeout: int = 600) -> str:
        c = _check(requests.post(f"{API}/{self.user_id}/media", data={
            "media_type": "REELS", "upload_type": "resumable", "caption": caption,
            "share_to_feed": str(share_to_feed).lower(), "access_token": self.token}, timeout=60))
        size = video.stat().st_size
        with open(video, "rb") as f:
            _check(requests.post(c["uri"], headers={"Authorization": f"OAuth {self.token}", "offset": "0", "file_size": str(size)},
                                 data=f, timeout=600))
        end = time.time() + timeout
        while True:  # wait until Instagram has processed the video
            st = _check(requests.get(f"{API}/{c['id']}", params={"fields": "status_code,status", "access_token": self.token}, timeout=30))
            if st["status_code"] == "FINISHED":
                break
            if st["status_code"] in ("ERROR", "EXPIRED") or time.time() > end:
                raise InstagramError(f"processing failed: {st}")
            time.sleep(5)
        m = _check(requests.post(f"{API}/{self.user_id}/media_publish", data={"creation_id": c["id"], "access_token": self.token}, timeout=60))
        return m["id"]
