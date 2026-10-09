# EP.6 upload handoff
Files (episodes/ep06): render/ep06_review.mp4 (720p review copy), render/ep06_full.mp4 (full quality, ~200 MB, git-ignored; re-render with `./run_segments.sh 1 2` if missing), ep06_en.srt (English subtitles, 144 cues, total 8:39), thumbs/thumb_A.jpg (recommended), B, C, upload_meta.md.
Upload: `python -m korea_decoded upload render/ep06_full.mp4 --title ... --description <txt> --publish-at ... --thumbnail thumbs/thumb_A.jpg --dry-run` (needs a fresh YouTube refresh token; see docs/api_setup.md). Default private + scheduled, only after the operator approves.
No Shorts for EP.6 (operator decision). The hacking story was cut; its voice lines (audio/v1/ep06_006-034) and screens remain in the repo for later use.
