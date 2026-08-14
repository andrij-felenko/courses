# -*- coding: utf-8 -*-
"""Фігури для статті «Швидке сортування (Quicksort)» та її вставок.
Генерує чотири SVG у ./img:
1. quicksort-partition.svg — анатомія схеми розбиття (поінтери, зони, опорний елемент)
2. quicksort-tree.svg — збалансоване дерево рекурсії проти зродженого лінійного ланцюга
3. quicksort-3way.svg — тристороннє розбиття (Dutch National Flag) для дублікатів
4. quicksort-introsort.svg — схема перемикання алгоритмів у гібридному Introsort
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_LEFT  = "#eef2f7"   # Зона <= pivot (світло-синьо-сіре)
BG_RIGHT = "#fdecea"   # Зона > pivot (світло-червоне)
BG_PIVOT = "#fef9e7"   # Опорний елемент (світло-жовте)
BG_EQUAL = "#e6f7ee"   # Зона == pivot у 3-way (світло-зелене)
BG_UNKN  = "#ffffff"   # Ще не оброблені елементи (біле)
HEAP     = "#eef2f7"   # Допоміжний світлий колір

BORDER_PIVOT = "#d4ac0d"
BORDER_EQUAL = "#1e824c"
BORDER_LEFT  = "#2980b9"
BORDER_RIGHT = "#c0392b"

def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK, bold=True):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5, val, size=15, color=tc, bold=bold))

# ── Фігура 1: Анатомія розбиття Ломуто ───────────────────────────────────────
def fig_partition():
    W, H = 760, 260
    cw, ch = 52, 42
    x0, y0 = 60, 110
    f = []

    vals = [3, 7, 1, 8, 2, 5, 9, 4]

    w_left = 4 * cw
    f.append(rect(x0, y0 - 35, w_left, 26, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.2, rx=3))
    f.append(text(x0 + w_left / 2, y0 - 18, "≤ pivot (елементи 3, 1, 2)", size=12, color=BORDER_LEFT, bold=True))

    w_right = 3 * cw
    f.append(rect(x0 + 4 * cw, y0 - 35, w_right, 26, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=3))
    f.append(text(x0 + 4 * cw + w_right / 2, y0 - 18, "> pivot (7, 8, 5, 9)", size=12, color=BORDER_RIGHT, bold=True))

    f.append(rect(x0 + 7 * cw, y0 - 35, cw, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.2, rx=3))
    f.append(text(x0 + 7 * cw + cw / 2, y0 - 18, "Pivot", size=12, color=BORDER_PIVOT, bold=True))

    for i, v in enumerate(vals):
        if i == 7:
            fill = BG_PIVOT
            stroke = BORDER_PIVOT
        elif v <= 4:
            fill = BG_LEFT
            stroke = BORDER_LEFT
        else:
            fill = BG_RIGHT
            stroke = BORDER_RIGHT

        f.append(cell(x0 + i * cw, y0, cw, ch, str(v), fill=fill, stroke=stroke, sw=1.8))
        f.append(text(x0 + i * cw + cw / 2, y0 + ch + 18, f"[{i}]", size=12, color=MUTED))

    xi = x0 + 2 * cw + cw / 2
    f.append(line(xi, y0 + ch + 30, xi, y0 + ch + 48, color=BORDER_LEFT, sw=2))
    f.append(text(xi, y0 + ch + 65, "i (межа ≤ pivot)", size=13, color=BORDER_LEFT, bold=True))

    xj = x0 + 6 * cw + cw / 2
    f.append(line(xj, y0 + ch + 30, xj, y0 + ch + 48, color=BORDER_RIGHT, sw=2))
    f.append(text(xj, y0 + ch + 65, "j (сканування)", size=13, color=BORDER_RIGHT, bold=True))

    render(os.path.join(IMG, "quicksort-partition.svg"), W, H, *f,
           title="Анатомія розбиття Ломуто")

# ── Фігура 2: Збалансоване дерево проти зродженого ──────────────────────────
def fig_tree():
    W, H = 840, 330
    f = []

    cx1 = 200
    f.append(text(cx1, 50, "Ідеальний випадок: збалансований поділ", size=13, bold=True))
    f.append(text(cx1, 68, "Глибина = log₂ n, Час = O(n log n)", size=11, color=POS, bold=True))

    f.append(rect(cx1 - 50, 85, 100, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=4))
    f.append(text(cx1, 102, "[ n елементів ]", size=11, bold=True))

    f.append(line(cx1 - 20, 111, cx1 - 60, 140, color=LINE, sw=1.5))
    f.append(line(cx1 + 20, 111, cx1 + 60, 140, color=LINE, sw=1.5))

    f.append(rect(cx1 - 105, 140, 90, 24, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.2, rx=4))
    f.append(text(cx1 - 60, 156, "n/2", size=11))
    f.append(rect(cx1 + 15, 140, 90, 24, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=4))
    f.append(text(cx1 + 60, 156, "n/2", size=11))

    f.append(line(cx1 - 80, 164, cx1 - 125, 190, color=LINE, sw=1.2))
    f.append(line(cx1 - 40, 164, cx1 - 30, 190, color=LINE, sw=1.2))
    f.append(line(cx1 + 40, 164, cx1 + 30, 190, color=LINE, sw=1.2))
    f.append(line(cx1 + 80, 164, cx1 + 125, 190, color=LINE, sw=1.2))

    f.append(rect(cx1 - 145, 190, 40, 22, fill=HEAP, stroke=LINE, sw=1.2, rx=3))
    f.append(text(cx1 - 125, 205, "n/4", size=10))
    f.append(rect(cx1 - 50, 190, 40, 22, fill=HEAP, stroke=LINE, sw=1.2, rx=3))
    f.append(text(cx1 - 30, 205, "n/4", size=10))
    f.append(rect(cx1 + 10, 190, 40, 22, fill=HEAP, stroke=LINE, sw=1.2, rx=3))
    f.append(text(cx1 + 30, 205, "n/4", size=10))
    f.append(rect(cx1 + 105, 190, 40, 22, fill=HEAP, stroke=LINE, sw=1.2, rx=3))
    f.append(text(cx1 + 125, 205, "n/4", size=10))

    f.append(text(cx1, 240, "⋮", size=18, color=MUTED))
    f.append(text(cx1, 285, "Опорний елемент щоразу ділить масив навпіл", size=11, color=MUTED))

    f.append(line(420, 45, 420, 300, color=LINE, sw=1, dash="4,4"))

    cx2 = 640
    f.append(text(cx2, 50, "Найгірший випадок: несбалансований поділ", size=13, bold=True))
    f.append(text(cx2, 68, "Глибина = n, Час = O(n²)", size=11, color=NEG, bold=True))

    f.append(rect(cx2 - 50, 85, 100, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=4))
    f.append(text(cx2, 102, "[ n елементів ]", size=11, bold=True))

    f.append(line(cx2 + 10, 111, cx2 + 45, 140, color=LINE, sw=1.5))
    f.append(line(cx2 - 20, 111, cx2 - 50, 140, color=LINE, sw=1.2))
    f.append(text(cx2 - 65, 156, "0", size=10, color=MUTED))

    f.append(rect(cx2, 140, 90, 24, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=4))
    f.append(text(cx2 + 45, 156, "n − 1", size=11))

    f.append(line(cx2 + 55, 164, cx2 + 85, 190, color=LINE, sw=1.5))
    f.append(rect(cx2 + 40, 190, 90, 22, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=4))
    f.append(text(cx2 + 85, 205, "n − 2", size=11))

    f.append(line(cx2 + 85, 212, cx2 + 105, 235, color=LINE, sw=1.5))
    f.append(text(cx2 + 105, 250, "⋮", size=18, color=MUTED))
    f.append(text(cx2, 285, "Поганий pivot (найменший або найбільший)", size=11, color=MUTED))

    render(os.path.join(IMG, "quicksort-tree.svg"), W, H, *f,
           title="Дерево рекурсії Quicksort")

# ── Фігура 3: Тристороннє розбиття (Dutch National Flag) ──────────────────────
def fig_3way():
    W, H = 760, 250
    cw, ch = 48, 40
    x0, y0 = 50, 110
    f = []

    vals = [2, 1, 3, 3, 3, 5, 4, 3]

    w1 = 2 * cw
    f.append(rect(x0, y0 - 35, w1, 26, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.2, rx=3))
    f.append(text(x0 + w1 / 2, y0 - 18, "< pivot", size=12, color=BORDER_LEFT, bold=True))

    w2 = 3 * cw
    f.append(rect(x0 + 2 * cw, y0 - 35, w2, 26, fill=BG_EQUAL, stroke=BORDER_EQUAL, sw=1.2, rx=3))
    f.append(text(x0 + 2 * cw + w2 / 2, y0 - 18, "= pivot", size=12, color=BORDER_EQUAL, bold=True))

    w3 = 2 * cw
    f.append(rect(x0 + 5 * cw, y0 - 35, w3, 26, fill=BG_UNKN, stroke=MUTED, sw=1.2, rx=3))
    f.append(text(x0 + 5 * cw + w3 / 2, y0 - 18, "нерозглянуто", size=12, color=MUTED))

    w4 = 1 * cw
    f.append(rect(x0 + 7 * cw, y0 - 35, w4, 26, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=3))
    f.append(text(x0 + 7 * cw + w4 / 2, y0 - 18, "> pivot", size=12, color=BORDER_RIGHT, bold=True))

    for i, v in enumerate(vals):
        if i < 2:
            fill, stroke = BG_LEFT, BORDER_LEFT
        elif i < 5:
            fill, stroke = BG_EQUAL, BORDER_EQUAL
        elif i < 7:
            fill, stroke = BG_UNKN, MUTED
        else:
            fill, stroke = BG_RIGHT, BORDER_RIGHT

        f.append(cell(x0 + i * cw, y0, cw, ch, str(v), fill=fill, stroke=stroke, sw=1.8))
        f.append(text(x0 + i * cw + cw / 2, y0 + ch + 16, f"[{i}]", size=11, color=MUTED))

    x_lt = x0 + 2 * cw + cw / 2
    f.append(line(x_lt, y0 + ch + 28, x_lt, y0 + ch + 45, color=BORDER_EQUAL, sw=2))
    f.append(text(x_lt, y0 + ch + 62, "lt", size=13, color=BORDER_EQUAL, bold=True))

    xi = x0 + 5 * cw + cw / 2
    f.append(line(xi, y0 + ch + 28, xi, y0 + ch + 45, color=BORDER_LEFT, sw=2))
    f.append(text(xi, y0 + ch + 62, "i (поточний)", size=13, color=BORDER_LEFT, bold=True))

    x_gt = x0 + 6 * cw + cw / 2
    f.append(line(x_gt, y0 + ch + 28, x_gt, y0 + ch + 45, color=BORDER_RIGHT, sw=2))
    f.append(text(x_gt, y0 + ch + 62, "gt", size=13, color=BORDER_RIGHT, bold=True))

    render(os.path.join(IMG, "quicksort-3way.svg"), W, H, *f,
           title="Тристороннє розбиття (Dutch National Flag)")

# ── Фігура 4: Схема роботи Introsort ─────────────────────────────────────────
def fig_introsort():
    W, H = 820, 290
    f = []

    bx, by, bw, bh = 40, 95, 140, 48
    f.append(rect(bx, by, bw, bh, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.8, rx=6))
    f.append(text(bx + bw / 2, by + 20, "Вхідний масив", size=13, bold=True))
    f.append(text(bx + bw / 2, by + 36, "розмір N", size=11, color=MUTED))

    f.append(arrow(bx + bw, by + bh / 2, bx + bw + 40, by + bh / 2, color=INK, sw=2))

    c1x, c1y, c1w, c1h = 220, 95, 160, 48
    f.append(rect(c1x, c1y, c1w, c1h, fill=HEAP, stroke=LINE, sw=1.5, rx=6))
    f.append(text(c1x + c1w / 2, c1y + 20, "N ≤ 16 ?", size=13, bold=True))
    f.append(text(c1x + c1w / 2, c1y + 36, "малий підмасив", size=11, color=MUTED))

    f.append(arrow(c1x + c1w / 2, c1y + c1h, c1x + c1w / 2, c1y + c1h + 45, color=LINE, sw=2))
    f.append(text(c1x + c1w / 2 + 30, c1y + c1h + 24, "Так", size=12, color=POS, bold=True))

    ins_x, ins_y, ins_w, ins_h = c1x - 10, c1y + c1h + 50, 180, 48
    f.append(rect(ins_x, ins_y, ins_w, ins_h, fill=BG_EQUAL, stroke=BORDER_EQUAL, sw=1.8, rx=6))
    f.append(text(ins_x + ins_w / 2, ins_y + 20, "Insertion Sort", size=13, color=BORDER_EQUAL, bold=True))
    f.append(text(ins_x + ins_w / 2, ins_y + 36, "O(N²) за малого N швидко", size=11, color=MUTED))

    f.append(arrow(c1x + c1w, c1y + c1h / 2, c1x + c1w + 50, c1y + c1h / 2, color=LINE, sw=2))
    f.append(text(c1x + c1w + 25, c1y + c1h / 2 - 12, "Ні", size=12, color=MUTED, bold=True))

    c2x, c2y, c2w, c2h = 430, 95, 170, 48
    f.append(rect(c2x, c2y, c2w, c2h, fill=HEAP, stroke=LINE, sw=1.5, rx=6))
    f.append(text(c2x + c2w / 2, c2y + 20, "Глибина > 2 log N ?", size=13, bold=True))
    f.append(text(c2x + c2w / 2, c2y + 36, "загроза O(N²)", size=11, color=MUTED))

    f.append(arrow(c2x + c2w / 2, c2y + c2h, c2x + c2w / 2, c2y + c2h + 45, color=LINE, sw=2))
    f.append(text(c2x + c2w / 2 + 30, c2y + c2h + 24, "Так", size=12, color=NEG, bold=True))

    heap_x, heap_y, heap_w, heap_h = c2x - 5, c2y + c2h + 50, 180, 48
    f.append(rect(heap_x, heap_y, heap_w, heap_h, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.8, rx=6))
    f.append(text(heap_x + heap_w / 2, heap_y + 20, "Heapsort", size=13, color=BORDER_RIGHT, bold=True))
    f.append(text(heap_x + heap_w / 2, heap_y + 36, "гарантовані O(N log N)", size=11, color=MUTED))

    f.append(arrow(c2x + c2w, c2y + c2h / 2, c2x + c2w + 50, c2y + c2h / 2, color=LINE, sw=2))
    f.append(text(c2x + c2w + 25, c2y + c2h / 2 - 12, "Ні", size=12, color=POS, bold=True))

    qs_x, qs_y, qs_w, qs_h = c2x + 55, c2y, 115, 48
    f.append(rect(qs_x, qs_y, qs_w, qs_h, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.8, rx=6))
    f.append(text(qs_x + qs_w / 2, qs_y + 20, "Quicksort", size=13, color=BORDER_LEFT, bold=True))
    f.append(text(qs_x + qs_w / 2, qs_y + 36, "partition", size=11, color=MUTED))

    f.append(line(qs_x + qs_w / 2, qs_y, qs_x + qs_w / 2, qs_y - 30, color=BORDER_LEFT, sw=1.5))
    f.append(line(qs_x + qs_w / 2, qs_y - 30, c1x + c1w / 2, qs_y - 30, color=BORDER_LEFT, sw=1.5))
    f.append(arrow(c1x + c1w / 2, qs_y - 30, c1x + c1w / 2, c1y, color=BORDER_LEFT, sw=1.5))
    f.append(text(410, qs_y - 38, "рекурсивні виклики для підмасивів", size=11, color=BORDER_LEFT))

    render(os.path.join(IMG, "quicksort-introsort.svg"), W, H, *f,
           title="Анатомія Introsort")

if __name__ == "__main__":
    fig_partition()
    fig_tree()
    fig_3way()
    fig_introsort()
    print("Всі SVG успішно згенеровано у ./img/")
