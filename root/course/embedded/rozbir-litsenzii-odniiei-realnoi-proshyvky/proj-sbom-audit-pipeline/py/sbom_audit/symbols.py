# -*- coding: utf-8 -*-
"""Перехресна звірка складу образу через ``arm-none-eabi-nm``.

Мапу можна обдурити перейменуванням файлів: скопіювали чужий модуль у
``Core/Src/crypto_helper.c`` — і за шаблонами шляхів він виглядає як власний код.
А от імена функцій переживають перейменування файлу майже завжди, бо їх викликає
решта запозиченого коду. Тому після аудиту мапи ми додатково дивимося на таблицю
символів ELF і шукаємо характерні префікси чужих бібліотек.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class NmError(RuntimeError):
    """Утиліти nm немає або вона відмовилася читати файл."""


@dataclass
class Symbol:
    address: int
    kind: str            # T/t — код, R/r — .rodata, D/d, B/b — дані
    name: str


@dataclass
class SymbolFinding:
    code: str
    message: str


_NM_LINE = re.compile(r"^(?P<addr>[0-9a-fA-F]+)\s+(?P<kind>[A-Za-z])\s+(?P<name>\S+)\s*$")


def collect_defined_symbols(elf_path: str | Path,
                            nm_tool: str = "arm-none-eabi-nm",
                            timeout: float = 60.0) -> list[Symbol]:
    """``arm-none-eabi-nm --defined-only --numeric-sort firmware.elf``."""

    elf = Path(elf_path)
    if not elf.is_file():
        raise NmError(f"ELF-файла немає: {elf}")
    if shutil.which(nm_tool) is None:
        raise NmError(f"утиліти '{nm_tool}' немає в PATH — перехресну звірку пропущено")

    try:
        proc = subprocess.run(
            [nm_tool, "--defined-only", "--numeric-sort", str(elf)],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise NmError(f"'{nm_tool}' не завершився за {timeout:.0f} с") from exc
    except OSError as exc:
        raise NmError(f"'{nm_tool}' не запустився: {exc}") from exc

    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()
        hint = tail[-1] if tail else "без повідомлення"
        raise NmError(f"'{nm_tool}' повернув {proc.returncode}: {hint}")

    symbols: list[Symbol] = []
    for line in proc.stdout.splitlines():
        m = _NM_LINE.match(line.strip())
        if m:
            symbols.append(Symbol(int(m.group("addr"), 16), m.group("kind"), m.group("name")))
    if not symbols:
        raise NmError(f"{elf}: nm не знайшов жодного визначеного символу")
    return symbols


def audit_symbols(symbols: list[Symbol],
                  watch_prefixes: dict[str, str],
                  declared_prefixes: dict[str, str],
                  detected_ids: set[str]) -> list[SymbolFinding]:
    """Знайти символи підозрілих бібліотек, не покриті задекларованими компонентами."""

    findings: list[SymbolFinding] = []
    unregistered: dict[str, list[Symbol]] = {}
    ghosts: dict[str, list[str]] = {}

    for sym in symbols:
        owner = _owner(sym.name, declared_prefixes)

        if owner is None:
            for prefix, hint in watch_prefixes.items():
                if sym.name.startswith(prefix):
                    unregistered.setdefault(f"{prefix} — {hint}", []).append(sym)
                    break
            continue

        # Символ належить компоненту, якого мапа не показала: або шаблони шляхів
        # застаріли, або код вкопіювали в дерево проєкту руками.
        if owner not in detected_ids:
            ghosts.setdefault(owner, []).append(sym.name)

    for group, found in sorted(unregistered.items()):
        sample = ", ".join(f"{s.name}@0x{s.address:08x}" for s in found[:4])
        more = f" (+{len(found) - 4})" if len(found) > 4 else ""
        findings.append(SymbolFinding(
            "UNREGISTERED_SYMBOL_DETECTED",
            f"{group}: {len(found)} символів у Flash — {sample}{more}",
        ))

    for comp_id, names in sorted(ghosts.items()):
        sample = ", ".join(sorted(names)[:4])
        findings.append(SymbolFinding(
            "SYMBOLS_WITHOUT_MAP_MATCH",
            f"символи компонента '{comp_id}' в образі є ({sample}…), "
            f"але жодного його модуля мапа не показала",
        ))

    return findings


def _owner(symbol_name: str, declared_prefixes: dict[str, str]) -> str | None:
    """Найдовший збіг префікса виграє: 'ff_' у FatFs vs 'f_' у FatFs."""

    best: tuple[int, str] | None = None
    for prefix, comp_id in declared_prefixes.items():
        if symbol_name.startswith(prefix) and (best is None or len(prefix) > best[0]):
            best = (len(prefix), comp_id)
    return best[1] if best else None
