#!/usr/bin/env python3
import subprocess
import sys
import os
import re

def get_git_churn(days=90):
    """Збирає кількість модифікацій (додано + видалено рядків) по кожному файлу за N днів."""
    cmd = ["git", "log", f"--since={days}.days.ago", "--numstat", "--pretty=format:"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    churn_map = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) == 3:
            added, deleted, filepath = parts
            if added == '-' or deleted == '-':
                continue  # Пропускаємо бінарні файли (зображення, бінарники)
            changes = int(added) + int(deleted)
            churn_map[filepath] = churn_map.get(filepath, 0) + changes
    return churn_map

def get_file_complexity(filepath):
    """Оцінка складності за кількістю рядків коду та розгалужень (if/for/while/switch)."""
    if not os.path.exists(filepath):
        return 0
    complexity = 1
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Рахуємо ключові слова управляючих конструкцій
                if re.search(r'\b(if|else|for|while|switch|case|catch)\b', line):
                    complexity += 1
    except Exception:
        pass
    return complexity

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    churn = get_git_churn(days)
    results = []

    for filepath, churn_score in churn.items():
        # Фільтруємо теки тестування, генерований код та вендорські залежності
        if filepath.startswith("vendor/") or filepath.startswith("node_modules/") or filepath.startswith("build/"):
            continue
        complexity = get_file_complexity(filepath)
        hotspot_score = churn_score * complexity
        results.append((filepath, churn_score, complexity, hotspot_score))

    # Сортуємо за спаданням Hotspot Score
    results.sort(key=lambda x: x[3], reverse=True)

    print(f"{'File Path':<60} | {'Churn':<8} | {'Complexity':<10} | {'Hotspot Score':<12}")
    print("-" * 98)
    for path, ch, comp, score in results[:20]:
        print(f"{path:<60} | {ch:<8} | {comp:<10} | {score:<12}")

if __name__ == "__main__":
    main()
