#!/bin/sh
# usage: ./run_segments.sh 1 2 3 4   (renders those segments of EP.5 side by side)
cd "$(dirname "$0")"
mkdir -p render
python3 build_episode.py >/dev/null
python3 - <<'PY'
import json,sys
sys.path.insert(0,"../../prototypes")
import render_episode as r
ep=json.load(open("ep05_episode.json"))
for i,s in enumerate(r.split_episode(ep,"render/ep05")):
    json.dump(s,open(f"render/ep05_s{i+1}.json","w"),ensure_ascii=False,indent=1)
PY
for n in "$@"; do
  python3 ../../prototypes/episode.py render/ep05_s$n.json > render/s$n.log 2>&1 &
done
wait
