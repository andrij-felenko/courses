#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebase_sync_engine.py — Автоматизований контролер оновлення форку."""

import os
import sys
import re
import subprocess
import tempfile
import shutil


def run_git(args, cwd=None, check=True):
    """Виконати команду Git та повернути текстовий вивід.
    
    У разі помилки формує докладне повідомлення з кодом повернення,
    командою та вмістом стандартних потоків виводу й помилок.
    """
    cmd = ["git"] + args
    res = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if check and res.returncode != 0:
        raise RuntimeError(
            f"Git command failed: {' '.join(cmd)}\n"
            f"Stdout: {res.stdout.strip()}\n"
            f"Stderr: {res.stderr.strip()}"
        )
    return res.stdout.strip()


def parse_patch_headers(patch_path):
    """Витягти структуровані заголовки метаданих із файлу латки.
    
    Зчитує блок коментарів до першого технічного роздільника '---'.
    Підтримує обов'язкові поля Upstream-Status, Upstream-Commit,
    Upstream-PR, CVE та юридичний підпис Signed-off-by.
    """
    metadata = {
        "status": "Pending",
        "commit": None,
        "pr": None,
        "cve": None,
        "subject": "",
        "signed_off_by": None
    }
    with open(patch_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("Subject:"):
                metadata["subject"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-Status:"):
                metadata["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-Commit:"):
                metadata["commit"] = line.split(":", 1)[1].strip()
            elif line.startswith("Upstream-PR:"):
                metadata["pr"] = line.split(":", 1)[1].strip()
            elif line.startswith("CVE:"):
                metadata["cve"] = line.split(":", 1)[1].strip()
            elif line.startswith("Signed-off-by:"):
                metadata["signed_off_by"] = line.split(":", 1)[1].strip()
            elif line.strip() == "---":
                break
    return metadata


def is_commit_in_upstream(repo_path, commit_hash, upstream_ref):
    """Перевірити, чи увійшов конкретний комміт до цільової гілки апстриму.
    
    Використовує фундаментальну команду git merge-base --is-ancestor,
    яка математично перевіряє досяжність комміта у графі DAG.
    """
    if not commit_hash or len(commit_hash) < 7:
        return False
    
    # Виконуємо перевірку без викидання винятку: returncode 0 означає істину
    res = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_hash, upstream_ref],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return res.returncode == 0


def run_automated_sync(repo_dir, patches_dir, upstream_remote, target_tag):
    """Головний контур аналізу латок, списання та тестового ребейзу."""
    print(f"[*] Ініціалізація аналізу латок у каталозі: {patches_dir}")
    if not os.path.exists(patches_dir):
        raise FileNotFoundError(f"Каталог латок не знайдено: {patches_dir}")

    patch_files = sorted([f for f in os.listdir(patches_dir) if f.endswith(".patch")])
    if not patch_files:
        print("[*] Локальних латок не виявлено. Дерево повністю синхронізоване з апстримом.")
        return True

    active_patches = []
    retired_patches = []

    # Фаза 1: Аудит метаданих та списання прийнятих патчів
    for pf in patch_files:
        ppath = os.path.join(patches_dir, pf)
        meta = parse_patch_headers(ppath)
        print(f" -> Аналіз {pf}: [{meta['status']}] {meta['subject'][:55]}...")

        # Якщо латка позначена як Accepted і містить хеш, перевіряємо її в апстримі
        if meta["status"] == "Accepted" and meta["commit"]:
            if is_commit_in_upstream(repo_dir, meta["commit"], target_tag):
                print(f"    [+] СПИСАНО: Комміт {meta['commit'][:10]} увійшов до {target_tag}")
                retired_patches.append((pf, meta))
                continue

        active_patches.append((pf, meta))

    print(f"\n[*] Результат аудиту: {len(active_patches)} активних латок, {len(retired_patches)} списано.")

    # Фаза 2: Створення ізольованого робочого дерева (Worktree)
    temp_worktree = tempfile.mkdtemp(prefix="rebase_sync_worktree_")
    try:
        print(f"[*] Створення тимчасового робочого дерева в {temp_worktree}")
        run_git(["worktree", "add", "--detach", temp_worktree, target_tag], cwd=repo_dir)

        # Фаза 3: Послідовне накладання активних латок
        print(f"[*] Накладання активних латок поверх цільової бази {target_tag}...")
        for pf, meta in active_patches:
            ppath = os.path.abspath(os.path.join(patches_dir, pf))
            apply_res = subprocess.run(
                ["git", "am", "-3", ppath],
                cwd=temp_worktree,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if apply_res.returncode != 0:
                print(f"\n[!] СТРУКТУРНИЙ КОНФЛІКТ при накладанні латки: {pf}")
                print(f"    Деталі Git:\n{apply_res.stderr.strip()}")
                run_git(["am", "--abort"], cwd=temp_worktree, check=False)
                return False
            else:
                print(f"    [✓] Успішно накладено: {pf}")

        print(f"\n[УСПІХ] Усі {len(active_patches)} активних латок успішно ребейзнуто на {target_tag}!")
        return True

    finally:
        # Гарантоване прибирання робочого простору навіть у разі збоїв
        print("[*] Видалення тимчасового робочого дерева...")
        run_git(["worktree", "remove", "--force", temp_worktree], cwd=repo_dir, check=False)
        shutil.rmtree(temp_worktree, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Використання: python rebase_sync_engine.py <шлях_до_репо> <каталог_латок> <цільовий_тег>")
        print("Приклад: python rebase_sync_engine.py ./firmware ./patches v3.6.0")
        sys.exit(0)
    
    success = run_automated_sync(sys.argv[1], sys.argv[2], "upstream", sys.argv[3])
    sys.exit(0 if success else 1)
