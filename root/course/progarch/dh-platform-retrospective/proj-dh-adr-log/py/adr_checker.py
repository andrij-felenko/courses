# adr_checker.py - Python CLI для валідації метаданих ADR та генерації звіту
import os
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["Статус", "Дата", "Контекст", "Незворотність"]

def validate_adr_file(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding="utf-8")
    
    for key in REQUIRED_KEYS:
        if not re.search(fr"\*\*_{key}_\*\*:|\*\*{key}\*\*:", content, re.IGNORECASE):
            errors.append(f"Відсутнє обов'язкове поле метаданих: '{key}'")
            
    if "One-Way" not in content and "Two-Way" not in content:
        errors.append("Не вказано тип незворотності рішення ('One-Way' або 'Two-Way')")
        
    return errors

def main():
    print("=== ADR Registry Metadata Validator ===")
    adr_dir = Path("docs/adr")
    
    if not adr_dir.exists():
        print(f"[WARN] Тека {adr_dir} не знайдена. Створення демо-теки.")
        adr_dir.mkdir(parents=True, exist_ok=True)
        demo_adr = adr_dir / "ADR-001-edge-autonomy.md"
        demo_adr.write_text(
            "# ADR-001: Локальна автономність хаба\n\n"
            "**Статус**: Прийнято\n"
            "**Дата**: 2022-03-15\n"
            "**Контекст**: Захист від втрати мережі\n"
            "**Незворотність**: One-Way Door\n\n"
            "## Рішення\nВикористовувати C++ engine на хабі.\n",
            encoding="utf-8"
        )

    total_errors = 0
    for adr_file in adr_dir.glob("*.md"):
        errs = validate_adr_file(adr_file)
        if errs:
            print(f"[FAIL] {adr_file.name}:")
            for e in errs:
                print(f"  - {e}")
            total_errors += len(errs)
        else:
            print(f"[OK] {adr_file.name}")

    if total_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
