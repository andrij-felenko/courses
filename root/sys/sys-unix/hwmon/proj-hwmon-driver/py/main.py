#!/usr/bin/env python3
"""Знайти пристрій hwmon за вмістом name і прочитати temp1_input."""
import sys
from pathlib import Path

want = sys.argv[1] if len(sys.argv) > 1 else "minisens"

for node in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
    try:
        if (node / "name").read_text().strip() != want:
            continue
        milli = int((node / "temp1_input").read_text())
    except OSError:
        continue          # пристрій міг зникнути між переліком і читанням
    print(f"{node.name}: {milli / 1000:.3f} °C")
    sys.exit(0)

sys.exit(f"пристрій «{want}» не знайдено")
