#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import time
import zlib

def run_git(cmd):
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def extract_version_info(is_release_mode=False):
    # Перевірка наявності каталогу .git
    git_dir = run_git(["git", "rev-parse", "--git-dir"])
    if not git_dir:
        # Режим fallback: читання статичного version.txt якщо зібрано з архіву без VCS
        if os.path.exists("version.txt"):
            with open("version.txt", "r", encoding="utf-8") as f:
                raw_ver = f.read().strip()
                return parse_version_string(raw_ver, is_dirty=False, timestamp=int(time.time()), is_git=False)
        sys.stderr.write("ПОМИЛКА: Каталог не є Git-репозиторієм і version.txt відсутній!\n")
        sys.exit(1)

    # 1. Отримання базового рядка версії через git describe
    raw_desc = run_git(["git", "describe", "--tags", "--always", "--dirty", "--long"])
    if not raw_desc:
        raw_desc = "v0.0.0-0-g0000000"

    # 2. Перевірка статусу робочого дерева
    status_out = run_git(["git", "status", "--porcelain"])
    is_dirty = bool(status_out) or raw_desc.endswith("-dirty")

    # 3. Ворота чистоти для релізного профілю
    if is_release_mode and is_dirty:
        sys.stderr.write("\n=======================================================\n")
        sys.stderr.write("КРИТИЧНА ПОМИЛКА ВОРОТ ЗБІРКИ: ВИЯВЛЕНО БРУДНЕ ДЕРЕВО!\n")
        sys.stderr.write("Заборонено випускати Release-бінарник із незбереженими сирцями.\n")
        sys.stderr.write("Незбережені або модифіковані файли:\n")
        sys.stderr.write(status_out if status_out else "Невідповідність індексу Git\n")
        sys.stderr.write("=======================================================\n\n")
        sys.exit(1)

    # 4. Часова мітка останнього коміту (SOURCE_DATE_EPOCH для детермінізму)
    ts_str = run_git(["git", "log", "-1", "--format=%ct"])
    timestamp = int(ts_str) if ts_str and ts_str.isdigit() else int(time.time())

    return parse_version_string(raw_desc, is_dirty, timestamp, is_git=True)

def parse_version_string(raw, is_dirty, timestamp, is_git):
    # Очікуваний формат: v<major>.<minor>.<patch>-<commits>-g<hash>
    clean_raw = raw.replace("-dirty", "")
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)(?:-(\d+)-g([0-9a-fA-F]+))?$", clean_raw)
    
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        commits = int(match.group(4)) if match.group(4) else 0
        git_hash = match.group(5) if match.group(5) else "0000000"
        tag_name = f"v{major}.{minor}.{patch}"
    else:
        # Fallback якщо тегів взагалі немає в репозиторії
        major, minor, patch, commits = 0, 0, 0, 0
        git_hash = run_git(["git", "rev-parse", "--short=8", "HEAD"]) or "0000000"
        tag_name = "v0.0.0-untagged"

    return {
        "major": major,
        "minor": minor,
        "patch": patch,
        "commits": commits,
        "hash": git_hash[:8].ljust(8, '\0'),
        "tag": tag_name,
        "dirty": is_dirty,
        "timestamp": timestamp,
        "is_git": is_git,
        "full_string": raw
    }
