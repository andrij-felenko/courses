#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Утиліта аналізу соціотехнічного незбігу (Conway Mismatch Audit) мовою Python."""

import subprocess
import sys
import json
from collections import defaultdict
from typing import Dict, Set, Tuple

def parse_team_mapping(mapping_file: str) -> Dict[str, str]:
    """Зчитує відповідність email -> команда з JSON-файлу."""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def analyze_git_history(team_map: Dict[str, str]) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Set[str]]]:
    """Парсить git log та обчислює внесок кожної команди у файли."""
    cmd = ["git", "log", "--numstat", "--no-merges", "--format=COMMIT|%ae"]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        print(f"Помилка запуску git log: {e}", file=sys.stderr)
        sys.exit(1)

    file_team_lines: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    file_teams: Dict[str, Set[str]] = defaultdict(set)

    current_team = "Unknown"

    for line in process.stdout:
        line = line.strip()
        if not line:
            continue

        if line.startswith("COMMIT|"):
            email = line.split("|")[1].lower()
            current_team = team_map.get(email, "ExternalTeam")
        else:
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, filepath = parts
                if added != "-" and deleted != "-":
                    changes = int(added) + int(deleted)
                    file_team_lines[filepath][current_team] += changes
                    file_teams[filepath].add(current_team)

    process.wait()
    return file_team_lines, file_teams

def calculate_cmi(file_team_lines: Dict[str, Dict[str, int]], file_teams: Dict[str, Set[str]]):
    """Обчислює метрики TOR та CMI й виводить соціотехнічний звіт."""
    total_files = len(file_teams)
    mismatched_files = 0

    print("=== СОЦІОТЕХНІЧНИЙ АУДИТ КОДОВОЇ БАЗИ (Python) ===")
    print(f"Загалом аналізовано файлів: {total_files}\n")

    for filepath, teams in file_teams.items():
        if len(teams) > 1:
            mismatched_files += 1

        lines_per_team = file_team_lines[filepath]
        total_changes = sum(lines_per_team.values())
        top_team, top_lines = max(lines_per_team.items(), key=lambda item: item[1])
        tor = top_lines / total_changes if total_changes > 0 else 0.0

        if tor < 0.60 and len(teams) > 1:
            print(f"[УВАГА: ТРАГЕДІЯ СПІЛЬНОГО] {filepath}")
            print(f"  Головний власник: {top_team} (TOR = {tor:.2%})")
            print(f"  Усі команди: {', '.join(teams)}\n")

    cmi = (mismatched_files / total_files) if total_files > 0 else 0.0
    print(f"Індекс соціотехнічного незбігу (CMI): {cmi:.2%}")
    if cmi > 0.15:
        print("РЕЗУЛЬТАТ: Небезпечно високий соціотехнічний розрив! Необхідний маневр Конвея.")
    else:
        print("РЕЗУЛЬТАТ: Соціотехнічний стан кодової бази в межах норми.")

if __name__ == "__main__":
    fake_map = {
        "alice@dh.org": "TwinTeam",
        "bob@dh.org": "AutomationTeam",
        "charlie@dh.org": "PlatformTeam"
    }
    lines, teams = analyze_git_history(fake_map)
    calculate_cmi(lines, teams)
