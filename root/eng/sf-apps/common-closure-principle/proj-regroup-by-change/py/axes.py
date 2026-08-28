# tools/axes.py — осі зміни: які файли історія вперто міняє разом
import re
import subprocess
from collections import defaultdict
from itertools import combinations

WINDOW = "18 months ago"   # осі старші за півтора року вже не ті
MAX_FILES = 8              # ширший коміт — це рефактор, а не «одна причина»
MIN_SUPPORT = 3            # рідше — випадковий збіг
MIN_STRENGTH = 0.4         # частка спільних комітів (Жаккар)

SRC_RE = re.compile(r"^src/.+\.tsx?$")


def history() -> list[list[str]]:
    raw = subprocess.run(
        ["git", "log", f"--since={WINDOW}", "--no-merges", "-M",
         "--name-only", "--pretty=format:%x00"],
        capture_output=True, text=True, check=True).stdout

    commits = []
    for block in raw.split("\0"):
        files = sorted({l for l in block.split("\n") if SRC_RE.match(l)})
        if 1 < len(files) <= MAX_FILES:
            commits.append(files)
    return commits


def co_change(commits: list[list[str]]):
    """total: файл → скільки разів мінявся; pair: пара → скільки разів разом"""
    total, pair = defaultdict(int), defaultdict(int)
    for files in commits:
        for f in files:
            total[f] += 1
        for a, b in combinations(files, 2):     # files відсортовані → ключ стабільний
            pair[a, b] += 1
    return total, pair


def strong_pairs(total, pair) -> list[tuple[float, str, str]]:
    out = []
    for (a, b), both in pair.items():
        either = total[a] + total[b] - both     # Жаккар: разом / бодай раз
        strength = both / either
        if both >= MIN_SUPPORT and strength >= MIN_STRENGTH:
            out.append((strength, a, b))
    return sorted(out, key=lambda t: (-t[0], t[1], t[2]))


def cluster(pairs, files) -> list[list[str]]:
    """зливаємо сильні пари в осі — класичний union-find"""
    parent = {f: f for f in files}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]        # стиснення шляху
            x = parent[x]
        return x

    for _, a, b in pairs:
        parent[find(a)] = find(b)

    groups = defaultdict(list)
    for f in files:
        groups[find(f)].append(f)
    return sorted((g for g in groups.values() if len(g) > 1), key=len, reverse=True)


if __name__ == "__main__":
    total, pair = co_change(history())
    pairs = strong_pairs(total, pair)

    print(f"пари, що міняються разом (сила ≥ {MIN_STRENGTH}):")
    for strength, a, b in pairs:
        print(f"  {strength:.2f}  {a}  ↔  {b}")

    print("\nосі зміни:")
    for i, axis in enumerate(cluster(pairs, list(total)), 1):
        print(f"  вісь #{i} — файлів: {len(axis)}")
        for f in sorted(axis):
            print(f"      {f:<36} змін: {total[f]}")
