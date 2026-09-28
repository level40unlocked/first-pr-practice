from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from korea_decoded.youtube import CHUNK, VideoMeta, YouTubeError, YouTubeUploader, credentials_from_env


class FakeSession:
    """Answers the token, upload-start, chunk and thumbnail calls like the YouTube API."""

    def __init__(self, video_size):
        self.size = video_size
        self.calls = []

    def post(self, url, params=None, headers=None, data=None, timeout=None):
        self.calls.append(("POST", url, params, headers, data))
        if "oauth2" in url:
            return SimpleNamespace(status_code=200, json=lambda: {"access_token": "tok"}, text="")
        if "thumbnails" in url:
            return SimpleNamespace(status_code=200, text="")
        return SimpleNamespace(status_code=200, headers={"Location": "https://upload/session"}, text="")

    def put(self, url, data=None, headers=None, timeout=None):
        self.calls.append(("PUT", url, None, headers, len(data)))
        start, end = map(int, headers["Content-Range"].split()[1].split("/")[0].split("-"))
        if end + 1 < self.size:
            return SimpleNamespace(status_code=308, headers={"Range": f"bytes=0-{end}"}, text="")
        return SimpleNamespace(status_code=200, json=lambda: {"id": "abc123"}, text="")


def test_upload_sends_chunks_and_returns_the_id(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x" * (CHUNK + 1000))
    session = FakeSession(video.stat().st_size)
    up = YouTubeUploader("id", "secret", "refresh", session=session)
    assert up.upload(video, VideoMeta(title="Test"), log=lambda *_: None) == "abc123"
    puts = [c for c in session.calls if c[0] == "PUT"]
    assert [c[4] for c in puts] == [CHUNK, 1000]
    assert puts[0][3]["Authorization"] == "Bearer tok"
    up.set_thumbnail("abc123", _png(tmp_path))
    assert session.calls[-1][2] == {"videoId": "abc123"}


def _png(tmp_path):
    p = tmp_path / "t.png"
    p.write_bytes(b"\x89PNG")
    return p


def test_scheduled_release_is_private_with_utc_time():
    when = datetime.now(timezone(timedelta(hours=9))) + timedelta(days=2)
    status = VideoMeta(title="T", publish_at=when).body()["status"]
    assert status["privacyStatus"] == "private"
    assert status["publishAt"].endswith("Z")
    with pytest.raises(YouTubeError):
        VideoMeta(title="T", privacy="public", publish_at=when).body()
    with pytest.raises(YouTubeError):
        VideoMeta(title="T", publish_at=datetime.now(timezone.utc) - timedelta(hours=1)).body()


def test_rejects_long_titles_and_missing_credentials(monkeypatch):
    with pytest.raises(YouTubeError):
        VideoMeta(title="x" * 101).body()
    for name in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(YouTubeError, match="YOUTUBE_CLIENT_ID"):
        credentials_from_env()
