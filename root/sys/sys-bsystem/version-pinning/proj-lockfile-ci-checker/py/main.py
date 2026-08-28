#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI Lockfile Integrity Checker.

Перевіряє суворість закріплення версій та валідність хешів у замкових файлах.
"""

import sys
import os
import argparse
import hashlib
from pathlib import Path


def is_strictly_pinned(version: str) -> bool:
    """Перевіряє, чи не містить версія плаваючих операторів діапазонів."""
    forbidden_chars = {'^', '~', '>', '<', '*', '='}
    return not any(c in forbidden_chars for c in version)


def validate_lockfile(lock_path: Path) -> list[dict]:
    """Зчитує та валідує записи замкового файлу."""
    if not lock_path.is_file():
        raise FileNotFoundError(f"Замковий файл не знайдено: {lock_path}")

    packages = []
    with open(lock_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Рядок {idx}: очікується '<ім'я> <версія> <sha256>', отримано: {line}")

            name, version, sha256 = parts
            if not is_strictly_pinned(version):
                raise ValueError(f"Рядок {idx}: версія '{name} {version}' містить плаваючий діапазон!")

            if len(sha256) != 64 or not all(c in "0123456789abcdefABCDEF" for c in sha256):
                raise ValueError(f"Рядок {idx}: некоректний SHA-256 хеш для '{name}': {sha256}")

            packages.append({
                "name": name,
                "version": version,
                "sha256": sha256.lower()
            })

    return packages


def main() -> int:
    parser = argparse.ArgumentParser(description="CI Lockfile Validator")
    parser.add_argument("lockfile", type=Path, help="Шлях до замкового файлу")
    args = parser.parse_args()

    print(f"[CI-SECURITY] Сканування замкового файлу: {args.lockfile}")
    try:
        packages = validate_lockfile(args.lockfile)
    except Exception as e:
        print(f"[FAIL] Помилка валідації: {e}", file=sys.stderr)
        return 2

    print(f"[OK] Перевірено {len(packages)} заблокованих залежностей:")
    for pkg in packages:
        print(f"  ✓ {pkg['name']:<20} версія: {pkg['version']:<10} [SHA-256: {pkg['sha256'][:12]}...]")

    print("[CI-SECURITY] Усі версії суворо детерміновані. Збірку дозволено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
