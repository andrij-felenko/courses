# -*- coding: utf-8 -*-
"""Розбір мапи компонувальника GNU ld (``-Wl,-Map=build/firmware.map``).

Мапа — єдине джерело правди про склад образу: список файлів у репозиторії бреше
(лежить, але не злінковано), а список бібліотек у CMake бреше двічі (архів
підключено, а взято з нього один модуль із десяти).

Мапа має чотири блоки, і плутати їх не можна:

``Archive member included to satisfy reference by file``
    хто саме витягнув члена архіву — корисно для пояснення, звідки взявся модуль;
``Discarded input sections``
    те, що викинув ``--gc-sections`` або перевизначення слабкого символу.
    **Це НЕ у Flash.** Наївний ``grep '\\.o'`` по всьому файлу зараховує ці рядки
    в SBOM і дає паспорт на компоненти, яких у виробі немає;
``Memory Configuration``
    межі регіонів, нам байдуже;
``Linker script and memory map``
    власне розміщення — адреса, розмір, об'єктний файл. Тільки це рахуємо.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class MapError(RuntimeError):
    """Мапу не вдалося прочитати або вона не схожа на вивід ld."""


# Секція без розміщення на своєму рядку:  " .text.vTaskDelay"
_SECTION_ONLY = re.compile(r"^ (?P<name>\.[^\s]+)\s*$")
# Секція, адреса, розмір і носій в одному рядку (короткі імена секцій)
_SECTION_FULL = re.compile(
    r"^ (?P<name>\.[^\s]+)\s+0x(?P<addr>[0-9a-fA-F]+)\s+0x(?P<size>[0-9a-fA-F]+)\s+(?P<obj>\S.*?)\s*$"
)
# Продовження попереднього рядка: адреса, розмір, носій
_PLACEMENT = re.compile(
    r"^\s{2,}0x(?P<addr>[0-9a-fA-F]+)\s+0x(?P<size>[0-9a-fA-F]+)\s+(?P<obj>\S.*?)\s*$"
)
# Символ усередині щойно розміщеної секції: адреса й ім'я
_SYMBOL = re.compile(r"^\s{2,}0x(?P<addr>[0-9a-fA-F]+)\s{2,}(?P<name>[A-Za-z_.$][\w.$]*)\s*$")
# Носій: шлях до .o або член архіву libfoo.a(bar.o)
_OBJECT = re.compile(r"^(?P<path>[^\s()]+\.(?:o|obj|a|lto))(?:\((?P<member>[^\s()]+)\))?$")

_SKIP_PREFIXES = ("*fill*", "*(", "LOAD ", "START GROUP", "END GROUP", "OUTPUT(")


@dataclass
class LinkedObject:
    """Об'єктний модуль, який реально зайняв байти в образі."""

    token: str                                   # як записано в мапі
    path: str                                    # шлях до .o або до архіву
    member: str | None = None                    # член архіву, якщо це .a(...)
    size: int = 0                                # сума розмірів розміщених секцій
    sections: set[str] = field(default_factory=set)
    symbols: list[str] = field(default_factory=list)

    @property
    def is_archive_member(self) -> bool:
        return self.member is not None

    @property
    def display(self) -> str:
        return f"{self.path}({self.member})" if self.member else self.path


@dataclass
class WeakOverride:
    """Секцію викинуто, бо ту саму реалізацію дав інший модуль."""

    section: str
    kept_by: str
    dropped_from: list[str]


@dataclass
class MapReport:
    objects: dict[str, LinkedObject]
    discarded: dict[str, list[str]]          # секція -> модулі, з яких її викинуто
    overrides: list[WeakOverride]
    gc_dropped_sections: int                 # викинуто й ніким не замінено (--gc-sections)
    total_bytes: int

    def objects_sorted(self) -> list[LinkedObject]:
        return sorted(self.objects.values(), key=lambda o: (-o.size, o.display))


def _parse_object(token: str) -> tuple[str, str | None] | None:
    m = _OBJECT.match(token)
    if not m:
        return None
    return m.group("path"), m.group("member")


def parse_map(map_path: str | Path) -> MapReport:
    """Прочитати мапу й повернути те, що справді потрапило в образ."""

    path = Path(map_path)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise MapError(f"мапи немає: {path}") from exc
    except OSError as exc:
        raise MapError(f"мапу не прочитати ({path}): {exc}") from exc

    objects: dict[str, LinkedObject] = {}
    discarded: dict[str, list[str]] = {}
    allocated_sections: dict[str, str] = {}      # секція -> модуль, що лишився

    region = "head"
    pending_section: str | None = None
    current_object: LinkedObject | None = None

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("Archive member included"):
            region, pending_section, current_object = "archive", None, None
            continue
        if stripped.startswith("Discarded input sections"):
            region, pending_section, current_object = "discarded", None, None
            continue
        if stripped.startswith("Memory Configuration"):
            region, pending_section, current_object = "memory", None, None
            continue
        if stripped.startswith("Linker script and memory map"):
            region, pending_section, current_object = "map", None, None
            continue

        if region not in ("map", "discarded") or not stripped:
            continue
        if any(stripped.startswith(p) for p in _SKIP_PREFIXES):
            pending_section, current_object = None, None
            continue

        m = _SECTION_FULL.match(line)
        if m:
            _record(region, m.group("name"), int(m.group("size"), 16), m.group("obj"),
                    objects, discarded, allocated_sections)
            pending_section, current_object = None, None
            if region == "map":
                current_object = objects.get(m.group("obj"))
            continue

        m = _SECTION_ONLY.match(line)
        if m:
            pending_section, current_object = m.group("name"), None
            continue

        m = _PLACEMENT.match(line)
        if m and pending_section is not None:
            _record(region, pending_section, int(m.group("size"), 16), m.group("obj"),
                    objects, discarded, allocated_sections)
            if region == "map":
                current_object = objects.get(m.group("obj"))
            pending_section = None
            continue

        m = _SYMBOL.match(line)
        if m and current_object is not None and region == "map":
            current_object.symbols.append(m.group("name"))
            continue

    if not objects:
        raise MapError(
            f"у {path} немає жодної розміщеної секції — це точно мапа ld, а не лог збірки?"
        )

    overrides: list[WeakOverride] = []
    gc_dropped = 0
    for section, sources in discarded.items():
        keeper = allocated_sections.get(section)
        if keeper is None:
            gc_dropped += 1
            continue
        others = [s for s in sources if s != keeper]
        if others:
            overrides.append(WeakOverride(section=section, kept_by=keeper, dropped_from=others))

    return MapReport(
        objects=objects,
        discarded=discarded,
        overrides=sorted(overrides, key=lambda o: o.section),
        gc_dropped_sections=gc_dropped,
        total_bytes=sum(o.size for o in objects.values()),
    )


def _record(region: str, section: str, size: int, token: str,
            objects: dict[str, LinkedObject],
            discarded: dict[str, list[str]],
            allocated_sections: dict[str, str]) -> None:
    """Зарахувати рядок розміщення або рядок викинутої секції."""

    parsed = _parse_object(token)
    if parsed is None:
        return                                    # не носій: символ лінкер-скрипта, коментар тощо
    obj_path, member = parsed

    if region == "discarded":
        discarded.setdefault(section, []).append(token)
        return

    # Секція нульового розміру не займає Flash; беремо її лише як слід секції,
    # але за таким модулем ліцензійних зобов'язань не виникає.
    entry = objects.get(token)
    if entry is None:
        if size == 0:
            return
        entry = LinkedObject(token=token, path=obj_path, member=member)
        objects[token] = entry
    entry.size += size
    entry.sections.add(section)
    allocated_sections.setdefault(section, token)
