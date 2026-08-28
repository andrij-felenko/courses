#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pth_trace.py — повертає кожному елементу sys.path його автора."""

from __future__ import annotations

import io
import os
import site
import stat
import sys
from dataclasses import dataclass


def makepath(*parts: str) -> tuple[str, str]:
    """Точний відповідник site.makepath: абсолютний шлях і його ключ порівняння."""
    joined = os.path.abspath(os.path.join(*parts))
    return joined, os.path.normcase(joined)


@dataclass(frozen=True)
class PthLine:
    file: str
    lineno: int
    raw: str
    kind: str                    # "path" | "exec" | "comment" | "blank" | "hidden"
    target: str | None = None    # розрахований каталог для kind == "path"
    note: str = ""               # чому рядок не спрацював

    def where(self) -> str:
        return f"{os.path.basename(self.file)}:{self.lineno}"


class PthReplay:
    """Повторює site.addsitedir() без побічних дій."""

    def __init__(self, sitedirs: list[str]) -> None:
        self.sitedirs = sitedirs
        self.lines: list[PthLine] = []
        self.owner: dict[str, PthLine] = {}   # ключ normcase → рядок-автор
        self.known: set[str] = set()

    def run(self) -> "PthReplay":
        cases = {makepath(d)[1] for d in self.sitedirs}
        for entry in sys.path:                 # усе до першого site-packages
            if entry and makepath(entry)[1] in cases:
                break
            if entry:
                self.known.add(makepath(entry)[1])
        for sitedir in self.sitedirs:
            self._scan_dir(sitedir)
        return self

    def _scan_dir(self, sitedir: str) -> None:
        base, basecase = makepath(sitedir)
        if not os.path.isdir(base):
            return
        self.known.add(basecase)               # site додає саму теку перед скануванням
        names = sorted(n for n in os.listdir(base) if n.endswith(".pth"))
        for name in names:
            self._scan_file(base, name)

    def _scan_file(self, base: str, name: str) -> None:
        full = os.path.join(base, name)
        try:
            st = os.lstat(full)
        except OSError:
            return
        hidden = ((getattr(st, "st_flags", 0) & getattr(stat, "UF_HIDDEN", 0)) or
                  (getattr(st, "st_file_attributes", 0)
                   & getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 0)))
        if hidden:
            self.lines.append(PthLine(full, 0, "", "hidden",
                                      note="прихований файл — site його не читає"))
            return

        with io.open_code(full) as fh:
            blob = fh.read()
        try:
            text = blob.decode()
        except UnicodeDecodeError:
            text = blob.decode(sys.getfilesystemencoding())

        for n, raw in enumerate(text.splitlines(), 1):
            self.lines.append(self._classify(base, full, n, raw))

    def _classify(self, base: str, full: str, n: int, raw: str) -> PthLine:
        if raw.startswith("#"):
            return PthLine(full, n, raw, "comment")
        if not raw.strip():
            return PthLine(full, n, raw, "blank")
        if raw.startswith(("import ", "import\t")):
            return PthLine(full, n, raw, "exec",
                           note="виконано під час старту процесу")

        target, case = makepath(base, raw.rstrip())
        if case in self.known:
            return PthLine(full, n, raw, "path", target,
                           "дублікат — каталог уже був у списку")
        if not os.path.exists(target):
            return PthLine(full, n, raw, "path", target,
                           "каталогу нема на диску — рядок мовчки пропущено")

        line = PthLine(full, n, raw, "path", target, "додано в кінець sys.path")
        self.known.add(case)
        self.owner[case] = line
        return line
