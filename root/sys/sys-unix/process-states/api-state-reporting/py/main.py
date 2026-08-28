#!/usr/bin/env python3
"""Літера стану й місце сну для кожного потоку процесу."""
import pathlib
import sys

pid = sys.argv[1]

for task in sorted(pathlib.Path(f"/proc/{pid}/task").iterdir(), key=lambda p: int(p.name)):
    try:
        stat = (task / "stat").read_text()
        # поле 2 — ім'я в дужках, у ньому бувають пробіли й ')',
        # тому відлік починаємо від ОСТАННЬОЇ дужки
        state = stat[stat.rindex(")") + 2]
        wchan = (task / "wchan").read_text().strip()   # «0» = біжить або немає прав
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        continue                                        # потік уже вийшов
    print(f"{task.name:<7} {state}  {wchan}")
