# -*- coding: utf-8 -*-
"""Фігури до вставки «Обхід графа: DFS/BFS і пошук незалежних контурів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

TREE = FIELD       # гілки дерева — зелені
CHORD = POS        # хорди — червоні
EDGE = "#9aa3ad"   # звичайне ребро (сіре)


def node(cx, cy, label, r=19):
    """Вузол графа: кружок із номером."""
    return (circle(cx, cy, r, fill="#eef2fb", stroke=NEG, sw=2.2) +
            text(cx, cy + 5, label, size=13, bold=True))


# ── 1. Кістякове дерево й хорди ───────────────────────────────────────────────
def fig_spanning_tree():
    W, H = 860, 400
    f = [text(W / 2, 28, "Кістякове дерево й хорди: звідки беруться незалежні контури",
              size=17, bold=True),
         text(W / 2, 50, "обхід будує дерево без петель; кожна зайва гілка-хорда замикає один контур",
              size=12, color=MUTED, italic=True)]

    # квадрат вузлів 1-2-3-4 (плюс діагональ) ліворуч
    P = {1: (170, 150), 2: (380, 150), 3: (380, 330), 4: (170, 330)}
    # гілки дерева (зелені суцільні): 1-2 (a), 2-3 (b), 3-4 (c)
    tree = [((1, 2), "a"), ((2, 3), "b"), ((3, 4), "c")]
    # хорди (червоні пунктир): 4-1 (d), 1-3 (e)
    chords = [((4, 1), "d"), ((1, 3), "e")]

    for (n1, n2), lab in tree:
        (x1, y1), (x2, y2) = P[n1], P[n2]
        f.append(line(x1, y1, x2, y2, color=TREE, sw=3))
        f.append(text((x1 + x2) / 2, (y1 + y2) / 2 - 8, lab, size=12, color=TREE, bold=True, italic=True))
    for (n1, n2), lab in chords:
        (x1, y1), (x2, y2) = P[n1], P[n2]
        f.append(line(x1, y1, x2, y2, color=CHORD, sw=2.4, dash="7 5"))
    f.append(text(150, 245, "d", size=12, color=CHORD, bold=True, italic=True))
    f.append(text(298, 252, "e", size=12, color=CHORD, bold=True, italic=True))
    for n, (x, y) in P.items():
        f.append(node(x, y, str(n)))

    # легенда + панель-висновок праворуч
    f.append(line(470, 112, 510, 112, color=TREE, sw=3))
    f.append(text(520, 116, "гілка дерева (N−1 = 3): без петель", size=11, anchor="start"))
    f.append(line(470, 140, 510, 140, color=CHORD, sw=2.4, dash="7 5"))
    f.append(text(520, 144, "хорда (B−N+1 = 2): замикає контур", size=11, anchor="start"))

    px, py, pw, ph = 470, 176, 366, 168
    f.append(rect(px, py, pw, ph, fill=FILL, stroke=MUTED, sw=1.5, rx=10))
    f.append(text(px + 18, py + 26, "Хорда + шлях по дереву між її кінцями", size=11, anchor="start"))
    f.append(text(px + 18, py + 44, "= один фундаментальний контур:", size=11, anchor="start"))
    f.append(text(px + 18, py + 72, "• хорда d (4–1) → контур 1-2-3-4", size=11, color=CHORD, bold=True, anchor="start"))
    f.append(text(px + 18, py + 92, "• хорда e (1–3) → контур 1-2-3", size=11, color=CHORD, bold=True, anchor="start"))
    f.append(text(px + 18, py + 122, "Разом L = 2 незалежні контури —", size=11, color=TREE, bold=True, anchor="start"))
    f.append(text(px + 18, py + 142, "рівно B − N + 1.", size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "spanning-tree.svg"), W, H, *f)


# ── 2. DFS проти BFS на тому самому графі ─────────────────────────────────────
def fig_dfs_vs_bfs():
    W, H = 880, 380
    f = [text(W / 2, 28, "Два способи обходу: вглиб (DFS) і вшир (BFS)", size=17, bold=True),
         text(W / 2, 50, "обидва відвідують усі вузли по разу за O(N+B); на МК — ітеративно, не рекурсією",
              size=12, color=MUTED, italic=True)]
    f.append(line(W / 2, 70, W / 2, 332, color="#e4e4e4", sw=1.5))

    def panel( cx0, title, color, order, hint):
        P = {1: (cx0 - 60, 130), 2: (cx0 + 60, 130), 3: (cx0 + 60, 250), 4: (cx0 - 60, 250)}
        edges = [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)]
        out = [text(cx0, 96, title, size=12.5, color=color, bold=True)]
        for n1, n2 in edges:
            (x1, y1), (x2, y2) = P[n1], P[n2]
            out.append(line(x1, y1, x2, y2, color=EDGE, sw=2))
        for n, (x, y) in P.items():
            out.append(node(x, y, str(n), r=16))
        out.append(text(cx0, 292, order, size=11, bold=True))
        out.append(text(cx0, 312, hint, size=10, color=MUTED, italic=True))
        return out

    f += panel(225, "DFS — вглиб (стек, LIFO)", NEG,
               "порядок: 1 → 2 → 3 → 4 (вглиб, тоді назад)",
               "стек: кладемо сусідів, беремо з вершини")
    f += panel(655, "BFS — вшир (черга, FIFO)", TREE,
               "порядок: 1 → (2, 3) → 4 (рівнями)",
               "черга: беремо з початку, додаємо в кінець")

    f.append(fitbox(110, 338, 660, 30,
                    "На мікроконтролері — ЯВНИЙ стек/черга в пам'яті, а не рекурсія: глибокий граф переповнив би стек МК",
                    size=10.5, fill="#fff8ee", stroke="#e08030", bold=True))
    render(os.path.join(IMG, "dfs-vs-bfs.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spanning_tree()
    fig_dfs_vs_bfs()
    print("OK: 2 SVG -> img/")
