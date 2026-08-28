import subprocess
from collections import Counter
from itertools import combinations

def read_commits(repo="."):
    """Список комітів; кожен — множина змінених у ньому файлів."""
    out = subprocess.run(
        ["git", "-C", repo, "log", "--no-merges",
         "--name-only", "--pretty=format:%x00%H"],
        capture_output=True, text=True, check=True,
    ).stdout
    commits = []
    for chunk in out.split("\x00"):        # \x00 — наш роздільник комітів
        lines = chunk.splitlines()
        if not lines:
            continue
        files = {ln for ln in lines[1:] if ln}   # рядок 0 — хеш; далі файли
        if files:
            commits.append(files)
    return commits
