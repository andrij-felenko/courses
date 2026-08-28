#!/usr/bin/env python3
"""Скрипт запуску IWYU та автоматичного виправлення заголовків."""
import subprocess
import sys
import os

def run_iwyu_cleanup(build_dir, source_dir):
    compile_commands = os.path.join(build_dir, "compile_commands.json")
    if not os.path.exists(compile_commands):
        print(f"Помилка: {compile_commands} не знайдено! Зберіть проєкт із -DCMAKE_EXPORT_COMPILE_COMMANDS=ON")
        sys.exit(1)

    print("=== Крок 1: Запуск аналізу через iwyu_tool.py ===")
    iwyu_report_file = os.path.join(build_dir, "iwyu_report.txt")
    mapping_path = os.path.join(source_dir, "iwyu_mappings.imp")
    
    cmd = [
        "iwyu_tool.py",
        "-p", build_dir,
        "--",
        "-Xiwyu", f"--mapping_file={mapping_path}",
        "-Xiwyu", "--no_default_mappings"
    ]
    
    with open(iwyu_report_file, "w", encoding="utf-8") as out:
        subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, text=True)
    
    print(f"Звіт IWYU збережено у: {iwyu_report_file}")
    
    print("=== Крок 2: Автоматичне виправлення коду через fix_includes.py ===")
    with open(iwyu_report_file, "r", encoding="utf-8") as report:
        fix_cmd = [
            "fix_includes.py",
            "--comments",        # Додавати коментарі з назвами символів біля include
            "--safe_headers",   # Захищати системні заголовки від агресивного видалення
            "--reorder"         # Сортувати заголовки за канонічним порядком
        ]
        subprocess.run(fix_cmd, stdin=report, text=True)
    
    print("Очищення заголовків успішно завершено.")

if __name__ == "__main__":
    b_dir = sys.argv[1] if len(sys.argv) > 1 else "build"
    s_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    run_iwyu_cleanup(b_dir, s_dir)
