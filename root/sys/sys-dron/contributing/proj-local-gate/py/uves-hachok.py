#!/usr/bin/env python3
"""Дві проєктні перевірки QGroundControl для pre-commit:
   no-qassert   — Q_ASSERT у продакшн-коді;
   vehicle-null — результат activeVehicle() вжито без перевірки на нуль.
Читає лише ті файли, що передані аргументами (їх дає pre-commit)."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass

WINDOW = 10          # скільки рядків тому ми ще вважаємо перевірку чинною
SUFFIXES = (".cpp", ".cc", ".h", ".hpp")

ALLOW = re.compile(r"//\s*qgc-lint:\s*allow\((?P<rule>[\w-]+)\)\s*(?P<why>\S.*)?")

_NOISE = re.compile(
    r"//[^\n]*"
    r"|/\*.*?\*/"
    r"|R\"(?P<d>[^()\\\s]{0,16})\(.*?\)(?P=d)\""
    r"|\"(?:[^\"\\\n]|\\.)*\""
    r"|(?<![\w'])(?:u8|[LuU])?'(?:[^'\\\n]|\\.)*'",
    re.DOTALL)


def scrub(src: str) -> str:
    """Вміст коментарів і літералів -> пробіли. Довжина й переводи рядка цілі."""
    return _NOISE.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), src)


QASSERT = re.compile(r"\bQ_ASSERT(?:_X)?\s*\(")
DIRECT = re.compile(r"\bactiveVehicle\s*\(\s*\)\s*->")
ASSIGN = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\s*=\s*[^;]*\bactiveVehicle\s*\(\s*\)")
BLOCK_END = re.compile(r"^\}")

_use_cache: dict[str, re.Pattern] = {}
_guard_cache: dict[str, re.Pattern] = {}


def use_re(var: str) -> re.Pattern:
    if var not in _use_cache:
        _use_cache[var] = re.compile(r"\b" + re.escape(var) + r"\s*(?:->|\.\w)")
    return _use_cache[var]


def guard_re(var: str) -> re.Pattern:
    if var not in _guard_cache:
        v = re.escape(var)
        _guard_cache[var] = re.compile(
            r"\bif\s*\([^)]*\b" + v + r"\b"                    # if (!v), if (v == nullptr)
            r"|\b" + v + r"\b\s*\?"                            # v ? a : b
            r"|\b" + v + r"\b\s*(?:==|!=)\s*(?:nullptr|NULL)"  # v != nullptr
            r"|&&\s*!?\s*" + v + r"\b")                        # ... && v->...
    return _guard_cache[var]


@dataclass
class Hit:
    path: str
    line: int
    rule: str
    message: str


def analyze(path: str, src: str) -> list[Hit]:
    raw = src.splitlines()
    code = scrub(src).splitlines()
    origin: dict[str, int] = {}     # змінна -> рядок, де вона взялася з activeVehicle()
    guarded: dict[str, int] = {}    # змінна -> рядок останньої перевірки
    hits: list[Hit] = []

    for n, line in enumerate(code, 1):
        if BLOCK_END.match(line):          # закривна дужка на нульовому стовпці
            origin.clear()
            guarded.clear()
            continue

        if QASSERT.search(line):
            hits.append(Hit(path, n, "no-qassert",
                            "Q_ASSERT зникає в релізі — зробіть захисну перевірку "
                            "з раннім поверненням"))

        if DIRECT.search(line):
            hits.append(Hit(path, n, "vehicle-null",
                            "activeVehicle() може повернути нуль — не викликайте "
                            "метод одразу на результаті"))

        m = ASSIGN.search(line)
        if m:
            origin[m.group("var")] = n
            guarded.pop(m.group("var"), None)

        for var in origin:                 # спершу перевірки…
            if guard_re(var).search(line):
                guarded[var] = n

        for var in origin:                 # …і лише потім вживання
            if use_re(var).search(line):
                seen = guarded.get(var)
                if seen is None or n - seen > WINDOW:
                    hits.append(Hit(path, n, "vehicle-null",
                                    "«%s» узято з activeVehicle() і вжито без "
                                    "перевірки на нуль" % var))

    return [h for h in hits if not allowed(raw, h)]


def allowed(raw: list[str], hit: Hit) -> bool:
    """Позначку шукаємо в СИРИХ рядках: scrub() вигриз би її разом із коментарем."""
    for idx in (hit.line - 1, hit.line - 2):
        if 0 <= idx < len(raw):
            m = ALLOW.search(raw[idx])
            if m and m.group("rule") == hit.rule and m.group("why"):
                return True
    return False


def staged_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, check=True).stdout.split()
    return [p for p in out if p.endswith(SUFFIXES)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="шляхи; порожньо — узяти індекс git")
    ap.add_argument("--ci", action="store_true", help="вивід анотаціями GitHub Actions")
    args = ap.parse_args(argv)

    hits: list[Hit] = []
    for path in (args.files or staged_files()):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                hits += analyze(path, fh.read())
        except OSError as err:
            print("не прочитав %s: %s" % (path, err), file=sys.stderr)
            return 2

    for h in hits:
        if args.ci:
            print("::error file=%s,line=%d::%s: %s" % (h.path, h.line, h.rule, h.message))
        else:
            print("%s:%d: %s: %s" % (h.path, h.line, h.rule, h.message))

    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
