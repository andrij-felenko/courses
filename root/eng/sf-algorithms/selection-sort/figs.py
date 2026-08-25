# -*- coding: utf-8 -*-
"""Фігури для статті «Сортування вибором (Selection Sort)».
Генерує чотири SVG у ./img:
  1. selection-sort-phases.svg — один масив: відсортована зона (ліворуч) і невідсортована зона (праворуч).
  2. selection-sort-trace.svg — покрокова анатомія виконання на прикладі [64, 25, 12, 22, 11].
  3. selection-sort-reads-writes.svg — порівняння кількості читань і перезаписів пам'яті (Selection vs Bubble vs Insertion).
  4. double-selection-sort.svg — двостороннє сортування вибором (Min-Max Selection Sort).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

ZONE_SORTED = "#e6f7ee"  # світло-зелений (відсортована зона)
ZONE_UNSORT = "#eef2f7"  # світло-сірий (невідсортована зона)
SWAP_HIGHLIGHT = "#fdecea"  # світло-червоний (обмін)
MIN_HIGHLIGHT = "#fbf4e6"  # світло-жовтий (пошук мінімуму)
COLOR_GREEN = "#1e824c"
COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"


def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 6, val, size=16, color=tc, bold=True))


# ── Фігура 1: Поділ масиву на дві зони ─────────────────────────────────────────
def fig_phases():
    W, H = 620, 290
    cw, ch = 52, 42
    x0 = 170
    rows = [
        ("Крок i = 0", [11, 25, 12, 22, 64], 1),
        ("Крок i = 1", [11, 12, 25, 22, 64], 2),
        ("Крок i = 2", [11, 12, 22, 25, 64], 3),
    ]
    f = []
    # Легенда
    ly = 48
    f.append(rect(140, ly - 13, 16, 16, fill=ZONE_SORTED, stroke=LINE, sw=1.2, rx=3))
    f.append(text(162, ly, "відсортована зона (росте)", size=13, anchor="start", color=MUTED))
    f.append(rect(340, ly - 13, 16, 16, fill=ZONE_UNSORT, stroke=LINE, sw=1.2, rx=3))
    f.append(text(362, ly, "невідсортована зона (тане)", size=13, anchor="start", color=MUTED))

    y = 86
    for label, vals, sc in rows:
        f.append(text(x0 - 16, y + ch / 2 + 5, label, size=13, anchor="end", color=MUTED, bold=True))
        for idx, v in enumerate(vals):
            fill = ZONE_SORTED if idx < sc else ZONE_UNSORT
            f.append(cell(x0 + idx * cw, y, cw, ch, str(v), fill=fill))
        bx = x0 + sc * cw
        f.append(line(bx, y - 8, bx, y + ch + 8, color=COLOR_RED, sw=3.5))
        y += 58

    f.append(text(x0 + 2.5 * cw, y + 6, "межа відсортованого префіксу зсувається праворуч →", size=13,
                  anchor="middle", color=COLOR_RED, bold=True))

    render(os.path.join(IMG, "selection-sort-phases.svg"), W, H, *f,
           title="Поділ масиву на дві зони під час сортування вибором")


# ── Фігура 2: Анатомія покрокового виконання ────────────────────────────────────
def fig_trace():
    W, H = 760, 360
    cw, ch = 48, 38
    x0 = 240
    y0 = 60

    trace_data = [
        ("Початковий масив", [64, 25, 12, 22, 11], -1, -1, "Початок"),
        ("Крок 0 (i=0)", [11, 25, 12, 22, 64], 0, 4, "min=11 (idx 4) ⇄ A[0]=64"),
        ("Крок 1 (i=1)", [11, 12, 25, 22, 64], 1, 2, "min=12 (idx 2) ⇄ A[1]=25"),
        ("Крок 2 (i=2)", [11, 12, 22, 25, 64], 2, 3, "min=22 (idx 3) ⇄ A[2]=25"),
        ("Крок 3 (i=3)", [11, 12, 22, 25, 64], 3, 3, "min=25 (idx 3) — на місці"),
    ]

    f = []
    # Заголовок стовпчиків
    f.append(text(x0 - 20, y0 - 15, "Етап", size=13, anchor="end", color=MUTED, bold=True))
    for i in range(5):
        f.append(text(x0 + i * cw + cw / 2, y0 - 15, "[%d]" % i, size=13, anchor="middle", color=MUTED))
    f.append(text(x0 + 5 * cw + 20, y0 - 15, "Дія / Перестановки", size=13, anchor="start", color=MUTED, bold=True))

    y = y0
    for step_idx, (label, vals, pos1, pos2, note) in enumerate(trace_data):
        f.append(text(x0 - 20, y + ch / 2 + 5, label, size=13, anchor="end", color=INK, bold=True))
        for i, v in enumerate(vals):
            is_sorted = (i < step_idx)
            is_swapped = (i == pos1 or i == pos2) and (pos1 != -1)
            fill = SWAP_HIGHLIGHT if is_swapped else (ZONE_SORTED if is_sorted else ZONE_UNSORT)
            tc = COLOR_RED if is_swapped else INK
            f.append(cell(x0 + i * cw, y, cw, ch, str(v), fill=fill, tc=tc))

        f.append(text(x0 + 5 * cw + 20, y + ch / 2 + 5, note, size=13, anchor="start", color=COLOR_BLUE))
        y += 54

    # Підсумковий коментар
    f.append(text(W / 2, y + 16, "Результат: 4 проходи, не більше 4 обмінів для N=5 елементів", size=14, color=COLOR_GREEN, bold=True))

    render(os.path.join(IMG, "selection-sort-trace.svg"), W, H, *f,
           title="Покрокова анатомія сортування вибором")


# ── Фігура 3: Динаміка читань та записів пам'яті ──────────────────────────────
def fig_reads_writes():
    W, H = 760, 290
    f = []

    px, py, pw, ph = 70, 70, 620, 150
    # Порівняльні блоки трьох алгоритмів при N = 100
    algos = [
        ("Selection Sort", "4 950", "99", "O(N²) читань / O(N) записів — ідеально для Flash/EEPROM", ZONE_SORTED, COLOR_GREEN),
        ("Bubble Sort", "4 950", "2 475", "O(N²) читань / O(N²) записів — масові перезаписи", ZONE_UNSORT, COLOR_BLUE),
        ("Insertion Sort (Worst)", "4 950", "4 950", "O(N²) читань / O(N²) записів — зсув кожного елемента", SWAP_HIGHLIGHT, COLOR_RED),
    ]

    # Легенда та опис
    f.append(text(W / 2, 38, "Кількість операцій читання та перезапису при N = 100 елементів", size=14, bold=True))

    bx = 60
    by = 70
    bw = 200
    bh = 150
    gap = 20

    for idx, (name, reads, writes, desc, bg_color, border_color) in enumerate(algos):
        cur_x = bx + idx * (bw + gap)
        f.append(rect(cur_x, by, bw, bh, fill=bg_color, stroke=border_color, sw=1.8, rx=6))
        f.append(text(cur_x + bw / 2, by + 28, name, size=15, color=border_color, bold=True))
        f.append(line(cur_x + 15, by + 40, cur_x + bw - 15, by + 40, color=LINE, sw=1.0))

        f.append(text(cur_x + 20, by + 68, "Читання:", size=13, anchor="start", color=MUTED))
        f.append(text(cur_x + bw - 20, by + 68, reads, size=14, anchor="end", bold=True, color=INK))

        f.append(text(cur_x + 20, by + 96, "Записи (swaps):", size=13, anchor="start", color=MUTED))
        f.append(text(cur_x + bw - 20, by + 96, writes, size=14, anchor="end", bold=True, color=border_color))

        # Коротка характеристика під прямокутником
        f.append(mtext(cur_x + bw / 2, by + 124, desc.split(" — "), size=11, color=MUTED, anchor="middle", lh=1.25))

    f.append(text(W / 2, 255, "Висновок: Selection Sort мінімізує фізичний знос енергонезалежної пам'яті", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "selection-sort-reads-writes.svg"), W, H, *f,
           title="Порівняння читань та записів у сортуваннях O(N²)")


# ── Фігура 4: Двостороннє сортування вибором (Min-Max Selection Sort) ──────────
def fig_double_selection():
    W, H = 720, 280
    cw, ch = 52, 42
    x0 = 130
    y0 = 90
    f = []

    vals = [14, 88, 23, 5, 67, 42, 91, 31]
    n = len(vals)

    f.append(text(W / 2, 40, "Двосторонній прохід: одночасне знаходження MIN та MAX", size=15, bold=True))

    # Омальовка осередків
    for i, v in enumerate(vals):
        if i == 0:
            fill = ZONE_SORTED
        elif i == 3:  # MIN (5)
            fill = MIN_HIGHLIGHT
        elif i == 6:  # MAX (91)
            fill = SWAP_HIGHLIGHT
        elif i == n - 1:
            fill = ZONE_SORTED
        else:
            fill = ZONE_UNSORT

        f.append(cell(x0 + i * cw, y0, cw, ch, str(v), fill=fill))

    # Покажчики left і right
    f.append(arrow(x0 + 1 * cw + cw / 2, y0 - 30, x0 + 1 * cw + cw / 2, y0 - 5, color=COLOR_BLUE, sw=2.0))
    f.append(text(x0 + 1 * cw + cw / 2, y0 - 36, "left (idx 1)", size=12, color=COLOR_BLUE, bold=True))

    f.append(arrow(x0 + 6 * cw + cw / 2, y0 - 30, x0 + 6 * cw + cw / 2, y0 - 5, color=COLOR_BLUE, sw=2.0))
    f.append(text(x0 + 6 * cw + cw / 2, y0 - 36, "right (idx 6)", size=12, color=COLOR_BLUE, bold=True))

    # Виділення знайдених Min і Max
    f.append(arrow(x0 + 3 * cw + cw / 2, y0 + ch + 30, x0 + 3 * cw + cw / 2, y0 + ch + 5, color=COLOR_GREEN, sw=2.0))
    f.append(text(x0 + 3 * cw + cw / 2, y0 + ch + 45, "Знайдено MIN=5 (idx 3)", size=12, color=COLOR_GREEN, bold=True))

    f.append(arrow(x0 + 6 * cw + cw / 2, y0 + ch + 30, x0 + 6 * cw + cw / 2, y0 + ch + 5, color=COLOR_RED, sw=2.0))
    f.append(text(x0 + 6 * cw + cw / 2, y0 + ch + 45, "Знайдено MAX=91 (idx 6)", size=12, color=COLOR_RED, bold=True))

    # Дії обміну
    f.append(text(W / 2, y0 + ch + 80, "MIN (5) ⇄ A[left], MAX (91) ⇄ A[right]  →  Межі зсуваються (left++, right--)", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "double-selection-sort.svg"), W, H, *f,
           title="Схема двостороннього сортування вибором")


if __name__ == "__main__":
    fig_phases()
    fig_trace()
    fig_reads_writes()
    fig_double_selection()
    print("OK: generated SVGs successfully")
