"""Upload a video to the Four Eyes Report YouTube channel as private, scheduled to flip public
at a given UTC time (same private-then-auto-public pattern EP.2 used).

    python3 upload_scheduled.py <video_path> <title> <description_file> <publish_at_utc_iso> [tags_csv]

publish_at_utc_iso example: 2026-10-05T21:57:00Z
"""
import sys
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = r"C:\clipfactory\secrets\youtube_token_foureyes.json"


def get_youtube():
    tok = json.load(open(TOKEN_PATH, encoding="utf-8"))
    creds = Credentials.from_authorized_user_info(tok)
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        open(TOKEN_PATH, "w", encoding="utf-8").write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main():
    video_path, title, desc_file, publish_at = sys.argv[1:5]
    tags = sys.argv[5].split(",") if len(sys.argv) > 5 else []
    description = open(desc_file, encoding="utf-8").read()
    yt = get_youtube()
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "25"},
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "publicStatsViewable": True,
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"upload progress: {int(status.progress() * 100)}%")
    print("video_id:", resp["id"])
    print("url: https://youtu.be/" + resp["id"])
    print("scheduled publishAt:", publish_at)


if __name__ == "__main__":
    main()
