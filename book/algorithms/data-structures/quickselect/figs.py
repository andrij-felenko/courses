# -*- coding: utf-8 -*-
"""Фігури для статті «Алгоритм Quickselect» та її вставок.
Генерує три SVG у ./img:
1. quickselect-execution-path.svg — порівняння дерева рекурсії Quicksort та зрізаного шляху Quickselect
2. quickselect-partition.svg — анатомія кроку розбиття та вибір гілки за індексом k
3. quickselect-introselect.svg — схема гібридного алгоритму Introselect (захист від найгіршого випадку)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_LEFT   = "#eef2f7"   # Зона < pivot (світло-синьо-сіре)
BG_RIGHT  = "#fdecea"   # Зона > pivot (світло-червоне)
BG_PIVOT  = "#fef9e7"   # Опорний елемент (світло-жовте)
BG_TARGET = "#e6f7ee"   # Зона шуканої порядкової статистики k (світло-зелене)
BG_PRUNED = "#f2f4f4"   # Відкинута гілка / масив (сіре)

BORDER_PIVOT  = "#d4ac0d"
BORDER_TARGET = "#1e824c"
BORDER_LEFT   = "#2980b9"
BORDER_RIGHT  = "#c0392b"
BORDER_PRUNED = "#bdc3c7"

def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK, bold=True):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5, val, size=15, color=tc, bold=bold))

# ── Фігура 1: Порівняння дерева Quicksort та шляху Quickselect ───────────────
def fig_execution_path():
    W, H = 820, 310
    f = []

    # Ліва колона: Quicksort (обхід усіх гілок)
    cx1 = 210
    f.append(text(cx1, 35, "Quicksort: обхід двох гілок O(n log n)", size=13, bold=True, color=INK))
    
    # Рівень 0
    f.append(rect(cx1 - 70, 55, 140, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=4))
    f.append(text(cx1, 72, "[ n елементів ]", size=11, bold=True))

    # Стрілки рівень 0 -> 1
    f.append(line(cx1 - 25, 81, cx1 - 65, 110, color=BORDER_LEFT, sw=1.5))
    f.append(line(cx1 + 25, 81, cx1 + 65, 110, color=BORDER_RIGHT, sw=1.5))

    # Рівень 1
    f.append(rect(cx1 - 110, 110, 90, 24, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.2, rx=4))
    f.append(text(cx1 - 65, 126, "n / 2", size=11))
    f.append(rect(cx1 + 20, 110, 90, 24, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=4))
    f.append(text(cx1 + 65, 126, "n / 2", size=11))

    # Стрілки рівень 1 -> 2
    f.append(line(cx1 - 85, 134, cx1 - 110, 165, color=BORDER_LEFT, sw=1.2))
    f.append(line(cx1 - 45, 134, cx1 - 30, 165, color=BORDER_LEFT, sw=1.2))
    f.append(line(cx1 + 45, 134, cx1 + 30, 165, color=BORDER_RIGHT, sw=1.2))
    f.append(line(cx1 + 85, 134, cx1 + 110, 165, color=BORDER_RIGHT, sw=1.2))

    # Рівень 2
    f.append(rect(cx1 - 130, 165, 42, 22, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.0, rx=3))
    f.append(text(cx1 - 109, 180, "n/4", size=10))
    f.append(rect(cx1 - 50, 165, 42, 22, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.0, rx=3))
    f.append(text(cx1 - 29, 180, "n/4", size=10))

    f.append(rect(cx1 + 10, 165, 42, 22, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.0, rx=3))
    f.append(text(cx1 + 31, 180, "n/4", size=10))
    f.append(rect(cx1 + 90, 165, 42, 22, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.0, rx=3))
    f.append(text(cx1 + 111, 180, "n/4", size=10))

    f.append(text(cx1, 230, "Повне дерево: кожна підзадача обробляється", size=11, color=MUTED))

    # Вертикальна розділова лінія
    f.append(line(410, 30, 410, 270, color=LINE, sw=1.0, dash="4,4"))

    # Права колона: Quickselect (відкидання однієї гілки)
    cx2 = 610
    f.append(text(cx2, 35, "Quickselect: вибір лише однієї гілки O(n)", size=13, bold=True, color=BORDER_TARGET))

    # Рівень 0
    f.append(rect(cx2 - 70, 55, 140, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=4))
    f.append(text(cx2, 72, "[ n елементів ]", size=11, bold=True))

    # Стрілки рівень 0 -> 1 (одна активна, одна відкинута)
    f.append(line(cx2 - 25, 81, cx2 - 65, 110, color=BORDER_LEFT, sw=2.0))
    f.append(line(cx2 + 25, 81, cx2 + 65, 110, color=BORDER_PRUNED, sw=1.0, dash="3,3"))

    # Рівень 1
    f.append(rect(cx2 - 110, 110, 90, 24, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.5, rx=4))
    f.append(text(cx2 - 65, 126, "n / 2 (обрано)", size=11, bold=True, color=BORDER_LEFT))
    
    f.append(rect(cx2 + 20, 110, 90, 24, fill=BG_PRUNED, stroke=BORDER_PRUNED, sw=1.0, rx=4))
    f.append(text(cx2 + 65, 126, "n / 2 (відкинуто)", size=10, color=MUTED))

    # Стрілки рівень 1 -> 2
    f.append(line(cx2 - 85, 134, cx2 - 110, 165, color=BORDER_PRUNED, sw=1.0, dash="3,3"))
    f.append(line(cx2 - 45, 134, cx2 - 30, 165, color=BORDER_TARGET, sw=2.0))

    # Рівень 2
    f.append(rect(cx2 - 130, 165, 42, 22, fill=BG_PRUNED, stroke=BORDER_PRUNED, sw=1.0, rx=3))
    f.append(text(cx2 - 109, 180, "відкид", size=9, color=MUTED))

    f.append(rect(cx2 - 50, 165, 64, 24, fill=BG_TARGET, stroke=BORDER_TARGET, sw=1.8, rx=4))
    f.append(text(cx2 - 18, 181, "k-й елемент", size=10, bold=True, color=BORDER_TARGET))

    f.append(text(cx2, 230, "Однобічна рекурсія: n + n/2 + n/4 + ... = 2n", size=11, color=BORDER_TARGET, bold=True))

    render(os.path.join(IMG, "quickselect-execution-path.svg"), W, H, *f,
           title="Порівняння дерева Quicksort та зрізаного шляху Quickselect")


# ── Фігура 2: Анатомія кроку розбиття та вибір гілки за індексом k ───────────────
def fig_partition():
    W, H = 780, 270
    cw, ch = 52, 42
    x0, y0 = 50, 100
    f = []

    vals = [2, 5, 1, 4, 8, 9, 7]
    pivot_idx = 3 # Елемент '4' на індексі 3

    # Підписи зон зверху
    w_left = 3 * cw
    f.append(rect(x0, y0 - 36, w_left, 26, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.2, rx=3))
    f.append(text(x0 + w_left / 2, y0 - 19, "Зона ≤ pivot (індекси 0..2)", size=11, color=BORDER_LEFT, bold=True))

    f.append(rect(x0 + 3 * cw, y0 - 36, cw, 26, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=3))
    f.append(text(x0 + 3 * cw + cw / 2, y0 - 19, "Pivot (idx=3)", size=11, color=BORDER_PIVOT, bold=True))

    w_right = 3 * cw
    f.append(rect(x0 + 4 * cw, y0 - 36, w_right, 26, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.2, rx=3))
    f.append(text(x0 + 4 * cw + w_right / 2, y0 - 19, "Зона > pivot (індекси 4..6)", size=11, color=BORDER_RIGHT, bold=True))

    # Комірці масиву
    for i, v in enumerate(vals):
        if i < pivot_idx:
            fill = BG_LEFT
            stroke = BORDER_LEFT
        elif i == pivot_idx:
            fill = BG_PIVOT
            stroke = BORDER_PIVOT
        else:
            fill = BG_RIGHT
            stroke = BORDER_RIGHT

        f.append(cell(x0 + i * cw, y0, cw, ch, str(v), fill=fill, stroke=stroke, sw=1.8))
        f.append(text(x0 + i * cw + cw / 2, y0 + ch + 18, f"[{i}]", size=11, color=MUTED))

    # Стрілка рішення для k
    # Приклад: k = 1 (шукаємо елемент в лівій зоні)
    xk = x0 + 1 * cw + cw / 2
    f.append(line(xk, y0 + ch + 28, xk, y0 + ch + 48, color=BORDER_TARGET, sw=2))
    f.append(text(xk, y0 + ch + 65, "k = 1 (k < pivot_idx)", size=12, color=BORDER_TARGET, bold=True))
    f.append(text(xk, y0 + ch + 82, "→ Рекурсія в ліву зону [0..2]", size=11, color=BORDER_LEFT))

    # Рішення якщо k == pivot_idx
    xp = x0 + 3 * cw + cw / 2
    f.append(text(xp, y0 + ch + 65, "k == pivot_idx", size=12, color=BORDER_PIVOT, bold=True))
    f.append(text(xp, y0 + ch + 82, "→ Елемент знайдено!", size=11, color=BORDER_TARGET, bold=True))

    # Рішення якщо k > pivot_idx
    xr = x0 + 5 * cw + cw / 2
    f.append(text(xr, y0 + ch + 65, "k > pivot_idx", size=12, color=BORDER_RIGHT, bold=True))
    f.append(text(xr, y0 + ch + 82, "→ Рекурсія в праву зону [4..6]", size=11, color=BORDER_RIGHT))

    render(os.path.join(IMG, "quickselect-partition.svg"), W, H, *f,
           title="Анатомія кроку розбиття та вибір гілки за індексом k")


# ── Фігура 3: Схема гібридного алгоритму Introselect ───────────────────────
def fig_introselect():
    W, H = 840, 260
    f = []

    # Блок 1: Старт
    f.append(rect(40, 90, 140, 45, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.5, rx=5))
    f.append(text(110, 110, "Початок Introselect", size=12, bold=True, color=BORDER_LEFT))
    f.append(text(110, 125, "depth_limit = 2·log₂(n)", size=10, color=MUTED))

    f.append(line(180, 112, 230, 112, color=INK, sw=1.5))

    # Блок 2: Перевірка глибини
    f.append(rect(230, 85, 170, 55, fill=BG_PIVOT, stroke=BORDER_PIVOT, sw=1.5, rx=5))
    f.append(text(315, 107, "depth_limit > 0 ?", size=12, bold=True, color=BORDER_PIVOT))
    f.append(text(315, 125, "Глибина не перевищена?", size=10, color=MUTED))

    # Гілка ТАК -> Звичайний Quickselect
    f.append(line(315, 140, 315, 185, color=BORDER_TARGET, sw=1.5))
    f.append(text(325, 160, "ТАК", size=11, bold=True, color=BORDER_TARGET))

    f.append(rect(220, 185, 190, 45, fill=BG_TARGET, stroke=BORDER_TARGET, sw=1.5, rx=5))
    f.append(text(315, 205, "Швидкий Quickselect", size=12, bold=True, color=BORDER_TARGET))
    f.append(text(315, 220, "Опорний елемент: Median-of-3", size=10, color=MUTED))

    # Гілка НІ -> Аварійне перемикання
    f.append(line(400, 112, 470, 112, color=BORDER_RIGHT, sw=1.5))
    f.append(text(430, 102, "НІ (деградація)", size=11, bold=True, color=BORDER_RIGHT))

    f.append(rect(470, 85, 210, 55, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.5, rx=5))
    f.append(text(575, 107, "Перемикання на Median-of-Medians", size=12, bold=True, color=BORDER_RIGHT))
    f.append(text(575, 125, "або Heapsort / Introselect", size=10, color=MUTED))

    # Завершення
    f.append(line(410, 207, 740, 207, color=BORDER_TARGET, sw=1.5))
    f.append(line(680, 112, 740, 112, color=BORDER_RIGHT, sw=1.5))
    f.append(line(740, 112, 740, 207, color=INK, sw=1.5))
    f.append(line(740, 160, 770, 160, color=INK, sw=1.5))

    f.append(rect(770, 138, 50, 44, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.5, rx=5))
    f.append(text(795, 165, "O(n)", size=14, bold=True, color=BORDER_LEFT))

    render(os.path.join(IMG, "quickselect-introselect.svg"), W, H, *f,
           title="Схема гібридного алгоритму Introselect")

if __name__ == '__main__':
    fig_execution_path()
    fig_partition()
    fig_introselect()
    print("Успішно згенеровано 3 фігури у ./img/")
