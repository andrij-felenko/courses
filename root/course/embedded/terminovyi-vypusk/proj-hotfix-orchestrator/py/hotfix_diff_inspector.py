#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hotfix_diff_inspector.py — Автоматичний аудит чистоти та меж екстреного патчу."""

import sys
import os
import subprocess
import re

MAX_ALLOWED_CHANGED_LINES = 150
MAX_ALLOWED_CHANGED_FILES = 4

FORBIDDEN_PATH_PATTERNS = [
    r"^third_party/",
    r"^drivers/hal/",
    r"^linker/.*\.ld$",
    r"^cmake/toolchain-.*\.cmake$",
    r"^\.github/workflows/"
]

def run_git_command(args):
    """Виконання команди Git із перевіркою результату."""
    result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def validate_hotfix_branch(base_tag, hotfix_branch):
    """Повна валідація меж та чистоти екстреної гілки."""
    print(f"[*] Перевірка походження гілки: {hotfix_branch} від тегу {base_tag}")
    
    # 1. Перевірка, що base_tag є прямим предком гілки hotfix
    merge_base = run_git_command(["merge-base", base_tag, hotfix_branch])
    tag_commit = run_git_command(["rev-parse", f"{base_tag}^{{commit}}"])
    
    if merge_base != tag_commit:
        print(f"[!] ПОМИЛКА: Гілка {hotfix_branch} відгалужена НЕ від релізного тегу {base_tag}!")
        print(f"    Merge base: {merge_base}, Tag commit: {tag_commit}")
        sys.exit(1)
        
    print("[+] Базовий тег підтверджено. Аналіз змінених файлів...")
    
    # 2. Отримання списку змінених файлів
    diff_files = run_git_command(["diff", "--name-only", base_tag, hotfix_branch]).splitlines()
    diff_files = [f for f in diff_files if f.strip()]
    
    if len(diff_files) > MAX_ALLOWED_CHANGED_FILES:
        print(f"[!] ПОМИЛКА: Кількість змінених файлів ({len(diff_files)}) перевищує ліміт {MAX_ALLOWED_CHANGED_FILES}!")
        sys.exit(1)
        
    for file_path in diff_files:
        for pattern in FORBIDDEN_PATH_PATTERNS:
            if re.search(pattern, file_path):
                print(f"[!] ПОМИЛКА: Зміна критичного системного шляху заборонена в hotfix: {file_path}")
                sys.exit(1)
                
    # 3. Підрахунок кількості доданих/видалених рядків
    diff_stat = run_git_command(["diff", "--shortstat", base_tag, hotfix_branch])
    match = re.search(r"(\d+)\s+insertions?\(\+\),\s+(\d+)\s+deletions?\(-\)", diff_stat)
    if match:
        ins, dels = int(match.group(1)), int(match.group(2))
        total_changed = ins + dels
        if total_changed > MAX_ALLOWED_CHANGED_LINES:
            print(f"[!] ПОМИЛКА: Обсяг змін ({total_changed} рядків) перевищує бюджет hotfix ({MAX_ALLOWED_CHANGED_LINES})!")
            sys.exit(1)
            
    print(f"[+] Дифф чистий: {len(diff_files)} файлів, {diff_stat}. Перевірка пройдена успішно.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: python hotfix_diff_inspector.py <base_tag> <hotfix_branch>")
        sys.exit(1)
    validate_hotfix_branch(sys.argv[1], sys.argv[2])
