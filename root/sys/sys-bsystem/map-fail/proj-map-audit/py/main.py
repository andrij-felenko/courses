#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map_audit.py — Автономний парсер GNU ld Map-файлу для контролю бюджету пам'яті в CI.
Підтримує перевірку лімітів Flash/RAM, детекцію заборонених символів та експорт у JSON.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional


class SymbolEntry:
    def __init__(self, section: str, address: int, size: int, origin: str):
        self.section = section
        self.address = address
        self.size = size
        self.origin = origin

    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "address": f"0x{self.address:08X}",
            "size_bytes": self.size,
            "origin": self.origin
        }


class MemoryRegion:
    def __init__(self, name: str, origin: int, length: int, attributes: str = ""):
        self.name = name
        self.origin = origin
        self.length = length
        self.attributes = attributes
        self.used_bytes = 0

    @property
    def percentage(self) -> float:
        return (self.used_bytes / self.length * 100.0) if self.length > 0 else 0.0

    @property
    def free_bytes(self) -> int:
        return max(0, self.length - self.used_bytes)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "origin": f"0x{self.origin:08X}",
            "length_bytes": self.length,
            "used_bytes": self.used_bytes,
            "free_bytes": self.free_bytes,
            "percentage": round(self.percentage, 2),
            "attributes": self.attributes
        }


def parse_memory_regions(lines: List[str]) -> Dict[str, MemoryRegion]:
    regions: Dict[str, MemoryRegion] = {}
    in_section = False
    
    # Шаблон рядка: FLASH 0x08000000 0x00010000 xr
    reg_pattern = re.compile(
        r'^\s*([A-Za-z0-9_]+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s*([a-z!]+)?'
    )

    for line in lines:
        if 'Memory Configuration' in line:
            in_section = True
            continue
        if in_section:
            if line.startswith('Linker script and memory map') or line.startswith('Discarded input sections'):
                break
            match = reg_pattern.match(line)
            if match:
                name = match.group(1)
                origin = int(match.group(2), 16)
                length = int(match.group(3), 16)
                attrs = match.group(4) or ""
                if name != '*default*':
                    regions[name] = MemoryRegion(name, origin, length, attrs)
    return regions


def parse_symbols_and_calculate_usage(
    lines: List[str], regions: Dict[str, MemoryRegion]
) -> List[SymbolEntry]:
    symbols: List[SymbolEntry] = []
    in_map = False

    # Регулярні вирази для однорядкового та дворядкового форматів GNU ld
    sec_single_pattern = re.compile(
        r'^\s*(\.[a-zA-Z0-9_\.]+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(.+)$'
    )
    sec_start_pattern = re.compile(r'^\s*(\.[a-zA-Z0-9_\.]+)\s*$')
    sec_cont_pattern = re.compile(r'^\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(.+)$')

    pending_section_name: Optional[str] = None

    for line in lines:
        if 'Linker script and memory map' in line:
            in_map = True
            continue
        if not in_map:
            continue
        if line.startswith('Cross Reference Table') or line.startswith('OUTPUT('):
            break

        # Спроба однорядкового зіставлення
        m_single = sec_single_pattern.match(line)
        if m_single:
            sec_name = m_single.group(1)
            addr = int(m_single.group(2), 16)
            size = int(m_single.group(3), 16)
            origin = m_single.group(4).strip()

            if size > 0 and not origin.startswith('*fill*'):
                symbols.append(SymbolEntry(sec_name, addr, size, origin))
                for reg in regions.values():
                    if reg.origin <= addr < (reg.origin + reg.length):
                        reg.used_bytes = max(reg.used_bytes, (addr + size) - reg.origin)

            pending_section_name = None
            continue

        # Спроба дворядкового зіставлення (початок)
        m_start = sec_start_pattern.match(line)
        if m_start:
            pending_section_name = m_start.group(1)
            continue

        # Спроба дворядкового зіставлення (продовження)
        if pending_section_name:
            m_cont = sec_cont_pattern.match(line)
            if m_cont:
                addr = int(m_cont.group(1), 16)
                size = int(m_cont.group(2), 16)
                origin = m_cont.group(3).strip()

                if size > 0 and not origin.startswith('*fill*'):
                    symbols.append(SymbolEntry(pending_section_name, addr, size, origin))
                    for reg in regions.values():
                        if reg.origin <= addr < (reg.origin + reg.length):
                            reg.used_bytes = max(reg.used_bytes, (addr + size) - reg.origin)
                pending_section_name = None
            else:
                pending_section_name = None

    return symbols


def run_audit(
    map_file: str,
    flash_limit: float,
    ram_limit: float,
    banned_keywords: List[str],
    json_output_path: Optional[str] = None
) -> bool:
    try:
        with open(map_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except OSError as err:
        print(f"[!] ПОМИЛКА читання файлу {map_file}: {err}")
        return False

    regions = parse_memory_regions(lines)
    symbols = parse_symbols_and_calculate_usage(lines, regions)

    print("=" * 78)
    print(f"ЗВІТ АУДИТУ ПАМ'ЯТІ ПРОШИВКИ (GNU ld Map Audit)")
    print(f"Файл: {map_file}")
    print("=" * 78)

    # 1. Стан регіонів пам'яті
    print("\n[1] Апаратні регіони пам'яті:")
    print(f"{'Регіон':<12} {'Початок':<12} {'Розмір (Б)':<12} {'Зайнято (Б)':<12} {'Використання'}")
    print("-" * 78)

    has_violation = False
    for name, reg in regions.items():
        bar_count = int(reg.percentage / 5)
        bar_visual = "█" * bar_count + "░" * (20 - bar_count)
        print(
            f"{name:<12} 0x{reg.origin:08X}   {reg.length:<12} "
            f"{reg.used_bytes:<12} {reg.percentage:6.2f}% [{bar_visual}]"
        )

        limit = flash_limit if ('FLASH' in name.upper() or 'ROM' in name.upper()) else ram_limit
        if reg.percentage > limit:
            print(
                f"  [!] ПОМИЛКА: Регіон '{name}' перевищив допустимий ліміт {limit:.1f}% "
                f"(фактично: {reg.percentage:.2f}%)"
            )
            has_violation = True

    # 2. Топ найбільших символів
    print("\n[2] Топ-10 найбільших функцій та об'єктів за розміром:")
    print(f"{'Розмір (Б)':<12} {'Адреса':<12} {'Секція / Символ':<28} {'Джерело'}")
    print("-" * 78)

    sorted_symbols = sorted(symbols, key=lambda s: s.size, reverse=True)
    for sym in sorted_symbols[:10]:
        print(f"{sym.size:<12} 0x{sym.address:08X}   {sym.section[:26]:<28} {sym.origin}")

    # 3. Перевірка заборонених символів
    print("\n[3] Перевірка заборонених символів (Banned Symbols Check):")
    detected_banned: List[SymbolEntry] = []
    for sym in symbols:
        for keyword in banned_keywords:
            if keyword in sym.section or keyword in sym.origin:
                detected_banned.append(sym)
                break

    if detected_banned:
        for sym in detected_banned:
            print(
                f"  [!] ВИЯВЛЕНО ЗАБОРОНЕНИЙ СИМВОЛ: '{sym.section}' "
                f"({sym.size} байтів) у {sym.origin}"
            )
        has_violation = True
    else:
        print("  [OK] Заборонених символів (динамічна пам'ять, RTTI, винятки) не виявлено.")

    # Експорт у JSON для інтеграції з іншими кроками CI
    if json_output_path:
        report_data = {
            "map_file": map_file,
            "success": not has_violation,
            "regions": {name: reg.to_dict() for name, reg in regions.items()},
            "top_symbols": [s.to_dict() for s in sorted_symbols[:15]],
            "banned_violations": [s.to_dict() for s in detected_banned]
        }
        try:
            with open(json_output_path, 'w', encoding='utf-8') as jf:
                json.dump(report_data, jf, indent=2)
            print(f"\n[INFO] Звіт у форматі JSON успішно збережено в: {json_output_path}")
        except OSError as err:
            print(f"[!] Не вдалося зберегти JSON-звіт: {err}")

    print("\n" + "=" * 78)
    if has_violation:
        print("РЕЗУЛЬТАТ АУДИТУ: ПЕРЕВІРКУ ПРОВАЛЕНО (Збірку зупинено).")
        return False
    else:
        print("РЕЗУЛЬТАТ АУДИТУ: УСПІШНО (Бюджет пам'яті дотримано).")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Автоматичний аудит Map-файлу GNU ld для систем CI/CD."
    )
    parser.add_argument("--map", required=True, help="Шлях до вхідного .map файлу")
    parser.add_argument(
        "--flash-max",
        type=float,
        default=90.0,
        help="Максимальний відсоток заповнення Flash (за замовчуванням: 90.0)"
    )
    parser.add_argument(
        "--ram-max",
        type=float,
        default=80.0,
        help="Максимальний відсоток заповнення RAM (за замовчуванням: 80.0)"
    )
    parser.add_argument(
        "--ban",
        nargs="*",
        default=["malloc", "free", "__cxa_throw", "_dtoa_r", "__udivmoddi4"],
        help="Список заборонених підрядків у назвах символів"
    )
    parser.add_argument(
        "--json",
        default=None,
        help="Опціональний шлях для збереження JSON-звіту"
    )

    args = parser.parse_args()
    success = run_audit(
        map_file=args.map,
        flash_limit=args.flash_max,
        ram_limit=args.ram_max,
        banned_keywords=args.ban,
        json_output_path=args.json
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
