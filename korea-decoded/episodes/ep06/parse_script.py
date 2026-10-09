"""Parses script.md into L = [(who, en, ko, screen)] (index = line number)."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
L = []
for line in open(os.path.join(HERE, "script.md"), encoding="utf-8"):
    m = re.match(r"\| (\d+) \| (.+?) \| (.+?) \| (.+?) \| (.*?) \|\s*$", line)
    if m and m.group(1).isdigit():
        L.append((m.group(2), m.group(3), m.group(4), m.group(5)))
