#!/usr/bin/env python3
"""Утиліта аудиту системного оточення Python та перевірки маркерів PEP 668."""

from __future__ import annotations
import configparser
import os
import sys
import sysconfig
from pathlib import Path


def check_virtual_environment() -> dict[str, str | bool]:
    """Перевіряє, чи активне віртуальне середовище venv."""
    is_venv = (
        hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix
    ) or (
        hasattr(sys, "real_prefix") and sys.prefix != sys.real_prefix
    )
    
    return {
        "is_venv": is_venv,
        "prefix": sys.prefix,
        "base_prefix": getattr(sys, "base_prefix", sys.prefix),
        "executable": sys.executable,
    }


def check_pep668_marker() -> dict[str, str | bool | None]:
    """Перевіряє наявність та зміст файлу EXTERNALLY-MANAGED."""
    paths_to_check = [
        sysconfig.get_path("stdlib"),
        sysconfig.get_path("platstdlib"),
    ]
    
    for base_dir in dict.fromkeys(paths_to_check):
        if not base_dir:
            continue
        marker_path = Path(base_dir) / "EXTERNALLY-MANAGED"
        if marker_path.is_file():
            parser = configparser.RawConfigParser()
            try:
                parser.read(marker_path, encoding="utf-8")
                msg = parser.get("externally-managed", "Error", fallback=None)
                if msg is None:
                    msg = parser.get("externally-managed", "error", fallback="[Повідомлення за замовчуванням]")
            except Exception:
                msg = "[Помилка парсингу INI файлу EXTERNALLY-MANAGED]"
                
            return {
                "present": True,
                "path": str(marker_path),
                "error_message": msg.strip(),
            }
            
    return {
        "present": False,
        "path": None,
        "error_message": None,
    }


def audit_shadowed_packages() -> list[dict[str, str]]:
    """Виявляє модулі в /usr/local, які затіняють системні пакети в /usr/lib."""
    local_site = None
    system_site = None
    
    for p in sys.path:
        p_path = Path(p)
        if not p_path.is_dir():
            continue
        if "/usr/local/" in p and ("dist-packages" in p or "site-packages" in p):
            local_site = p_path
        elif "/usr/lib/" in p and ("dist-packages" in p or "site-packages" in p):
            if system_site is None:
                system_site = p_path

    if not local_site or not system_site or not local_site.exists() or not system_site.exists():
        return []

    def get_top_level_names(directory: Path) -> set[str]:
        names = set()
        for item in directory.iterdir():
            if item.name.startswith((".", "_")) or item.name.endswith(".dist-info"):
                continue
            if item.is_dir():
                names.add(item.name)
            elif item.suffix in (".py", ".so"):
                names.add(item.stem)
        return names

    local_names = get_top_level_names(local_site)
    system_names = get_top_level_names(system_site)
    conflicts = local_names.intersection(system_names)

    result = []
    for name in sorted(conflicts):
        result.append({
            "package": name,
            "shadow_path": str(local_site / name),
            "system_path": str(system_site / name),
        })
    return result


def main() -> int:
    print("=== АУДИТ СИСТЕМНОГО ОТОЧЕННЯ PYTHON ===")
    venv_info = check_virtual_environment()
    if venv_info["is_venv"]:
        print("Статус: [ВІРТУАЛЬНЕ СЕРЕДОВИЩЕ]")
        print(f"Префікс venv : {venv_info['prefix']}")
        print(f"Базовий CPython: {venv_info['base_prefix']}")
    else:
        print("Статус: [СИСТЕМНИЙ ІНТЕРПРЕТАТОР]")
        print(f"Шлях префікса: {venv_info['prefix']}")

    print("\n--- Перевірка стандарту PEP 668 ---")
    pep668 = check_pep668_marker()
    if pep668["present"]:
        print("Маркер EXTERNALLY-MANAGED : ЗНАЙДЕНО (Захист активний)")
        print(f"Файл: {pep668['path']}")
        print(f"Текст дистрибутива:\n>>> {pep668['error_message']}")
    else:
        print("Маркер EXTERNALLY-MANAGED : ВІДСУТНІЙ (Прямий pip install не блокується)")

    print("\n--- Перевірка затінення системних модулів ---")
    shadows = audit_shadowed_packages()
    if shadows:
        print(f"УВАГА: Виявлено {len(shadows)} затінених системних пакетів!")
        for s in shadows:
            print(f" [!] Модуль '{s['package']}':")
            print(f"     Локальний (активний): {s['shadow_path']}")
            print(f"     Системний (затінений): {s['system_path']}")
    else:
        print("Конфліктів затінення між /usr/local та /usr/lib не виявлено.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
