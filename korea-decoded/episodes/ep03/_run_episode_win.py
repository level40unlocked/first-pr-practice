"""Windows-only shim: episode.py's charts.py hardcodes a Linux emoji font path
(/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf) for the "icons" chart type, which
crashes with OSError on this machine. Patch it to a Windows emoji font before running,
without touching the shared cross-platform charts.py/episode.py files.

    python3 _run_episode_win.py render/ep03_s1.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "prototypes"))
import charts  # noqa: E402

charts.EMOJI_FONT = "C:/Windows/Fonts/seguiemj.ttf"

sys.argv = ["episode.py"] + sys.argv[1:]
import runpy

runpy.run_path(os.path.join(os.path.dirname(__file__), "..", "..", "prototypes", "episode.py"), run_name="__main__")
