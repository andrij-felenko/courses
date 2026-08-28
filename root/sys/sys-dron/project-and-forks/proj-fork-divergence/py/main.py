#!/usr/bin/env python3
"""Борг злиття форку: площа дотику зі спільним кодом і зона зіткнення."""
import argparse, subprocess, sys
from collections import Counter

# Консоль Windows за замовчуванням не вміє ні «←», ні пів-алфавіту звіту.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", check=True)
    return r.stdout


def changed(base, tip, exclude):
    """{шлях: статус} для змін base → tip. -M вмикає розпізнавання перейменувань."""
    cmd = ["diff", "--name-status", "-M", base, tip, "--"]
    cmd += [":(exclude)" + p for p in exclude]
    out = {}
    for ln in git(*cmd).splitlines():
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        # "M<tab>src/Vehicle.cc"  або  "R096<tab>стара<tab>нова" — беремо НОВИЙ шлях
        out[parts[-1]] = parts[0][0]
    return out


def chunks(seq, n=200):
    """Аргументів-шляхів може бути тисячі, а довжина командного рядка обмежена."""
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def upstream_churn(base, upstream, paths):
    """Скільки рядків апстрим змінив у кожному з paths (додані + вилучені)."""
    out = {}
    for part in chunks(paths):
        raw = git("diff", "--numstat", "--no-renames", base, upstream, "--", *part)
        for ln in raw.splitlines():
            cols = ln.split("\t")
            if len(cols) != 3:
                continue
            add, dele, path = cols
            out[path] = 0 if add == "-" else int(add) + int(dele)   # "-" = бінарний
    return out


def group(path, depth=2):
    """Тека файла, обрізана до depth сегментів: src/Vehicle/V.cc → src/Vehicle."""
    parts = path.split("/")[:-1]            # ім'я файла — не тека
    return "/".join(parts[:depth]) if parts else "(корінь)"


def plural(n, one, few, many):
    """Українське узгодження: 1 файл, 2 файли, 5 файлів, 12 файлів."""
    if n % 100 in (11, 12, 13, 14):
        return many
    if n % 10 == 1:
        return one
    return few if n % 10 in (2, 3, 4) else many


def main():
    ap = argparse.ArgumentParser(description="борг злиття форку в числах")
    ap.add_argument("--upstream", default="upstream/master")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--overlay", default="custom/",
                    help="тека накладки: того, що там, апстрим не бачить")
    ap.add_argument("--exclude", action="append", default=[],
                    help="шум: згенероване, переклади (можна кілька разів)")
    ap.add_argument("--budget", type=int, default=0,
                    help="межа зони зіткнення; більше — ненульовий код виходу")
    a = ap.parse_args()

    base = git("merge-base", a.upstream, a.head).strip()
    behind, ahead = git("rev-list", "--left-right", "--count",
                        a.upstream + "..." + a.head).split()

    mine = changed(base, a.head, a.exclude)
    theirs = changed(base, a.upstream, a.exclude)

    overlay = [p for p in mine if p.startswith(a.overlay)]
    rest = [p for p in mine if not p.startswith(a.overlay)]
    added = [p for p in rest if mine[p] == "A"]     # наше нове у спільних теках
    touched = [p for p in rest if mine[p] != "A"]   # ПРАВКИ чужого — площа дотику
    collide = sorted(p for p in touched if p in theirs)

    churn = upstream_churn(base, a.upstream, collide)
    files_by_dir, lines_by_dir = Counter(), Counter()
    for p in collide:
        files_by_dir[group(p)] += 1
        lines_by_dir[group(p)] += churn.get(p, 0)

    share = 100.0 * len(collide) / len(touched) if touched else 0.0
    print("точка розгалуження        : %s" % base[:10])
    print("комітів позаду / попереду : %s / %s" % (behind, ahead))
    print()
    print("ваші зміни від точки розгалуження")
    print("  у теці накладки %-14s %5d" % (a.overlay, len(overlay)))
    print("  нові файли у спільних теках  %5d" % len(added))
    print("  ПРАВКИ спільних файлів       %5d   ← площа дотику" % len(touched))
    print()
    print("апстрим від тієї ж точки зачепив %d %s"
          % (len(theirs), plural(len(theirs), "файл", "файли", "файлів")))
    print("зона зіткнення: %d із %d (%.0f%%) — тут буде ручна робота"
          % (len(collide), len(touched), share))
    print()
    for d, n in files_by_dir.most_common(12):
        ln = lines_by_dir[d]
        print("  %-32s %4d %-7s %7d %s апстриму"
              % (d, n, plural(n, "файл", "файли", "файлів"),
                 ln, plural(ln, "рядок", "рядки", "рядків")))

    return 1 if a.budget and len(collide) > a.budget else 0


if __name__ == "__main__":
    raise SystemExit(main())
