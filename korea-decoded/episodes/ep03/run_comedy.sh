#!/bin/sh
# renders the two EP.3 comedy shorts (YouTube) and their Reels versions; the lines are in audio/comedy_lines_v1.json
cd "$(dirname "$0")"
for f in comedy_ppalli comedy_indoor comedyreel_ppalli comedyreel_indoor; do
  python3 ../../prototypes/episode.py render/$f.json > render/$f.log 2>&1 &
done
wait
