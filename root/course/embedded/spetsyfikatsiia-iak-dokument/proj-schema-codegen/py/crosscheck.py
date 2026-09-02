"""Звіряє байти нативних самотестів із еталонними векторами Python.

Прошивка (c/main.c) і шлюз (cpp/main.cpp) друкують зібраний еталонний
кадр рядком «Golden frame:». Якщо хоч один із трьох боків розійдеться зі
схемою — байти не збіжаться, і конвеєр упаде тут, а не на об'єкті.

    ./telemetry_c   | tee c.log
    ./telemetry_cpp | tee cpp.log
    PYTHONPATH=py python py/crosscheck.py c.log cpp.log
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import golden_vectors as gv

VERDICT_OK = "усі вектори зійшлися"

_LABELLED = r"{label}\s*((?:[0-9A-Fa-f]{{2}}[ \t]*)+)"


def extract_labelled(text: str, label: str) -> bytes:
    """Байти з рядка «<label> AA 01 20 …   (17 байт)».

    Дужка з довжиною обриває збіг сама: '(' не шістнадцяткова цифра.
    """
    match = re.search(_LABELLED.format(label=re.escape(label)), text)
    if match is None:
        raise LookupError(f"у виводі немає рядка «{label}»")
    return bytes.fromhex(match.group(1).replace(" ", "").replace("\t", ""))


def check_log(path: Path) -> list[str]:
    """Список розбіжностей; порожній — цей бік зійшовся."""
    text = path.read_text(encoding="utf-8", errors="replace")
    problems: list[str] = []

    try:
        golden = extract_labelled(text, "Golden frame:")
    except LookupError as exc:
        return [str(exc)]

    if golden != gv.GOLDEN_TELEMETRY:
        problems.append(
            f"еталонний кадр розійшовся\n"
            f"  {path.name}: {golden.hex(' ')}\n"
            f"  python:      {gv.GOLDEN_TELEMETRY.hex(' ')}"
        )

    written, calculated = gv.frame_crc(golden)
    if written != calculated:
        problems.append(f"сума в кадрі 0x{written:04X}, порахували 0x{calculated:04X}")

    if VERDICT_OK not in text:
        problems.append(f"самотест не доповів «{VERDICT_OK}»")

    return problems


def main(argv: list[str] | None = None) -> int:
    logs = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not logs:
        print("usage: crosscheck.py <лог самотесту> [ще лог …]", file=sys.stderr)
        return 2

    failed = False
    for log in logs:
        if not log.is_file():
            print(f"{log}: немає такого файла", file=sys.stderr)
            failed = True
            continue
        problems = check_log(log)
        if problems:
            failed = True
            for problem in problems:
                print(f"{log.name}: {problem}", file=sys.stderr)
        else:
            print(f"{log.name}: байт-у-байт із еталонними векторами")
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
