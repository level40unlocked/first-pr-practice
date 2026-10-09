#!/bin/sh
# Renders the intro reel: cd episodes/intro && ./run_render.sh
cd "$(dirname "$0")"
mkdir -p render
python3 build_scene.py && python3 ../../prototypes/episode.py intro_scene.json
