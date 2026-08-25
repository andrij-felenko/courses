# -*- coding: utf-8 -*-
"""Фігури для теми «Сортування злиттям (Merge Sort)» та її вставок.
Генерує 4 SVG-діаграми в img/:
1. merge-sort-tree.svg — повне дерево рекурсії «розділяй і володарюй» (поділ та злиття)
2. merge-two-pointers.svg — покрокова механіка злиття двох впорядкованих частин двома вказівниками
3. bottom-up-merge.svg — ітеративні проходи висхідного сортування злиттям (подвоєння ширини блоків)
4. linked-list-merge.svg — сортування однозв'язного списку злиттям з O(1) додаткової пам'яті
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_LEFT   = "#eef4fa"   # Лівий підмасив (світло-блакитний)
BG_RIGHT  = "#fdf2e9"   # Правий підмасив (світло-помаранчевий)
BG_MERGED = "#eafaf1"   # Злитий блок (світло-зелений)
BG_ACTIVE = "#fef9e7"   # Активний елемент / порівняння (світло-жовтий)
BG_EMPTY  = "#ffffff"   # Порожня комірка буфера

BORDER_LEFT   = "#2980b9"
BORDER_RIGHT  = "#d35400"
BORDER_MERGED = "#27ae60"
BORDER_ACTIVE = "#d4ac0d"
BORDER_BASE   = "#7f8c8d"

def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK, size=14, bold=True):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5, val, size=size, color=tc, bold=bold))

def array_bar(x, y, vals, cw, ch, fills, strokes, labels=None, label_color=MUTED):
    res = []
    for i, v in enumerate(vals):
        f = fills[i] if isinstance(fills, list) else fills
        s = strokes[i] if isinstance(strokes, list) else strokes
        res.append(cell(x + i * cw, y, cw, ch, str(v), fill=f, stroke=s, sw=1.5))
        if labels and i < len(labels) and labels[i]:
            res.append(text(x + i * cw + cw / 2, y + ch + 15, labels[i], size=11, color=label_color))
    return "".join(res)

# ── Фігура 1: Дерево рекурсії Merge Sort ──────────────────────────────────────
def fig_tree():
    W, H = 840, 470
    f = []
    cw, ch = 32, 28

    # Рівень 0 (Початковий масив)
    v0 = [38, 27, 43, 3, 9, 82, 10, 19]
    x0 = 420 - (8 * cw) / 2
    y0 = 55
    f.append(text(100, y0 + 18, "Рівень 0 (n=8):", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(array_bar(x0, y0, v0, cw, ch, [BG_LEFT]*4 + [BG_RIGHT]*4, [BORDER_LEFT]*4 + [BORDER_RIGHT]*4))

    # Стрілки вниз 0 -> 1
    f.append(line(370, y0 + ch + 2, 240, y0 + ch + 28, color=BORDER_LEFT, sw=1.5))
    f.append(line(470, y0 + ch + 2, 600, y0 + ch + 28, color=BORDER_RIGHT, sw=1.5))
    f.append(text(285, y0 + ch + 14, "поділ", size=10, color=BORDER_LEFT, italic=True))
    f.append(text(555, y0 + ch + 14, "поділ", size=10, color=BORDER_RIGHT, italic=True))

    # Рівень 1 (n=4)
    y1 = 115
    f.append(text(100, y1 + 18, "Рівень 1 (n=4):", size=12, bold=True, color=MUTED, anchor="start"))
    x1_1 = 160
    v1_1 = [38, 27, 43, 3]
    f.append(array_bar(x1_1, y1, v1_1, cw, ch, [BG_LEFT]*2 + [BG_RIGHT]*2, [BORDER_LEFT]*2 + [BORDER_RIGHT]*2))
    
    x1_2 = 520
    v1_2 = [9, 82, 10, 19]
    f.append(array_bar(x1_2, y1, v1_2, cw, ch, [BG_LEFT]*2 + [BG_RIGHT]*2, [BORDER_LEFT]*2 + [BORDER_RIGHT]*2))

    # Стрілки вниз 1 -> 2
    f.append(line(x1_1 + 2*cw - 15, y1 + ch + 2, 130, y1 + ch + 26, color=BORDER_LEFT, sw=1.2))
    f.append(line(x1_1 + 2*cw + 15, y1 + ch + 2, 270, y1 + ch + 26, color=BORDER_RIGHT, sw=1.2))
    f.append(line(x1_2 + 2*cw - 15, y1 + ch + 2, 490, y1 + ch + 26, color=BORDER_LEFT, sw=1.2))
    f.append(line(x1_2 + 2*cw + 15, y1 + ch + 2, 630, y1 + ch + 26, color=BORDER_RIGHT, sw=1.2))

    # Рівень 2 (n=2)
    y2 = 175
    f.append(text(100, y2 + 18, "Рівень 2 (n=2):", size=12, bold=True, color=MUTED, anchor="start"))
    blocks_r2 = [
        (100, [38, 27]),
        (240, [43, 3]),
        (460, [9, 82]),
        (600, [10, 19])
    ]
    for bx, bvals in blocks_r2:
        f.append(array_bar(bx, y2, bvals, cw, ch, [BG_LEFT, BG_RIGHT], [BORDER_LEFT, BORDER_RIGHT]))

    # Стрілки вниз 2 -> 3 (база)
    y_base = 235
    f.append(text(100, y_base + 18, "База (n=1):", size=12, bold=True, color=MUTED, anchor="start"))
    single_vals = [38, 27, 43, 3, 9, 82, 10, 19]
    single_xs = [80, 140, 220, 280, 440, 500, 580, 640]
    for sv, sx in zip(single_vals, single_xs):
        f.append(cell(sx, y_base, cw, ch, str(sv), fill="#f8f9fa", stroke=BORDER_BASE, sw=1.2))

    # Стрілки підйому (Злиття)
    y_m1 = 295
    f.append(text(100, y_m1 + 18, "Злиття 2x1:", size=12, bold=True, color=BORDER_MERGED, anchor="start"))
    merged_r1 = [
        (100, [27, 38]),
        (240, [3, 43]),
        (460, [9, 82]),
        (600, [10, 19])
    ]
    for bx, bvals in merged_r1:
        f.append(array_bar(bx, y_m1, bvals, cw, ch, BG_MERGED, BORDER_MERGED))

    y_m2 = 355
    f.append(text(100, y_m2 + 18, "Злиття 2x2:", size=12, bold=True, color=BORDER_MERGED, anchor="start"))
    f.append(array_bar(160, y_m2, [3, 27, 38, 43], cw, ch, BG_MERGED, BORDER_MERGED))
    f.append(array_bar(520, y_m2, [9, 10, 19, 82], cw, ch, BG_MERGED, BORDER_MERGED))

    y_m3 = 415
    f.append(text(100, y_m3 + 18, "Фінал (n=8):", size=12, bold=True, color=BORDER_MERGED, anchor="start"))
    f.append(array_bar(x0, y_m3, [3, 9, 10, 19, 27, 38, 43, 82], cw, ch, BG_MERGED, BORDER_MERGED))

    render(os.path.join(IMG, "merge-sort-tree.svg"), W, H, "".join(f),
           title="Дерево рекурсивного поділу та злиття")

# ── Фігура 2: Двопоінтерне злиття ─────────────────────────────────────────────
def fig_two_pointers():
    W, H = 820, 290
    f = []
    cw, ch = 52, 42
    x0 = 100

    # Лівий та правий підмасиви у вихідному масиві A
    y_src = 65
    f.append(text(x0 - 15, y_src + 25, "A:", size=14, bold=True, anchor="end"))
    
    # Підпис зон
    f.append(rect(x0, y_src - 24, 4 * cw, 20, fill=BG_LEFT, stroke=BORDER_LEFT, sw=1.0, rx=3))
    f.append(text(x0 + 2 * cw, y_src - 10, "Ліва частина A[lo..mid]", size=11, color=BORDER_LEFT, bold=True))
    
    f.append(rect(x0 + 4 * cw, y_src - 24, 4 * cw, 20, fill=BG_RIGHT, stroke=BORDER_RIGHT, sw=1.0, rx=3))
    f.append(text(x0 + 6 * cw, y_src - 10, "Права частина A[mid+1..hi]", size=11, color=BORDER_RIGHT, bold=True))

    vals_a = [3, 27, 38, 43, 9, 10, 19, 82]
    fills_a = [BG_LEFT, BG_ACTIVE, BG_LEFT, BG_LEFT, BG_ACTIVE, BG_RIGHT, BG_RIGHT, BG_RIGHT]
    strokes_a = [BORDER_LEFT, BORDER_ACTIVE, BORDER_LEFT, BORDER_LEFT, BORDER_ACTIVE, BORDER_RIGHT, BORDER_RIGHT, BORDER_RIGHT]
    labels_a = ["[0] взято", "[1] i", "[2]", "[3] mid", "[4] j", "[5]", "[6]", "[7] hi"]
    
    f.append(array_bar(x0, y_src, vals_a, cw, ch, fills_a, strokes_a, labels_a))

    # Стрілки та блок порівняння
    xi = x0 + 1 * cw + cw / 2
    xj = x0 + 4 * cw + cw / 2
    f.append(line(xi, y_src + ch + 22, xi, y_src + ch + 35, color=BORDER_ACTIVE, sw=2))
    f.append(line(xj, y_src + ch + 22, xj, y_src + ch + 35, color=BORDER_ACTIVE, sw=2))

    # Пояснення порівняння по центру
    f.append(rect(310, y_src + ch + 30, 200, 26, fill="#fff9e6", stroke=BORDER_ACTIVE, sw=1.5, rx=5))
    f.append(text(410, y_src + ch + 48, "A[j] (9) < A[i] (27)  ⇒  беремо 9", size=12, bold=True, color="#9a7d0a"))

    # Допоміжний масив aux / dest
    y_dst = 205
    f.append(text(x0 - 15, y_dst + 25, "aux:", size=14, bold=True, anchor="end"))
    
    vals_aux = [3, 9, "", "", "", "", "", ""]
    fills_aux = [BG_MERGED, BG_ACTIVE, BG_EMPTY, BG_EMPTY, BG_EMPTY, BG_EMPTY, BG_EMPTY, BG_EMPTY]
    strokes_aux = [BORDER_MERGED, BORDER_ACTIVE, LINE, LINE, LINE, LINE, LINE, LINE]
    labels_aux = ["[0] k=0", "[1] k=1", "[2] k=2", "[3]", "[4]", "[5]", "[6]", "[7]"]

    f.append(array_bar(x0, y_dst, vals_aux, cw, ch, fills_aux, strokes_aux, labels_aux))

    # Стрілка перенесення елемента 9 з A[j] в aux[k]
    f.append(line(xj, y_src + ch + 60, x0 + 1 * cw + cw / 2, y_dst - 5, color=BORDER_ACTIVE, sw=2))

    render(os.path.join(IMG, "merge-two-pointers.svg"), W, H, "".join(f),
           title="Механіка злиття двох впорядкованих частин у буфер")

# ── Фігура 3: Висхідне ітеративне злиття (Bottom-Up) ──────────────────────────
def fig_bottom_up():
    W, H = 820, 360
    f = []
    cw, ch = 48, 38
    x0 = 170

    # Початковий стан
    y0 = 55
    f.append(text(20, y0 + 24, "Початковий масив:", size=12, bold=True, color=MUTED, anchor="start"))
    v0 = [38, 27, 43, 3, 9, 82, 10, 19]
    f.append(array_bar(x0, y0, v0, cw, ch, [FILL]*8, [LINE]*8))

    # Прохід 1 (width = 1)
    y1 = 125
    f.append(text(20, y1 + 24, "Прохід 1 (width=1):", size=12, bold=True, color=BORDER_LEFT, anchor="start"))
    f.append(text(20, y1 + 38, "злиття пар по 1 ел.", size=10, color=MUTED, anchor="start"))
    v1 = [27, 38, 3, 43, 9, 82, 10, 19]
    f1 = [BG_LEFT, BG_LEFT, BG_RIGHT, BG_RIGHT, BG_LEFT, BG_LEFT, BG_RIGHT, BG_RIGHT]
    s1 = [BORDER_LEFT, BORDER_LEFT, BORDER_RIGHT, BORDER_RIGHT, BORDER_LEFT, BORDER_LEFT, BORDER_RIGHT, BORDER_RIGHT]
    f.append(array_bar(x0, y1, v1, cw, ch, f1, s1))
    # Розподільчі рамки для блоків розміру 2
    for b in range(4):
        bx = x0 + b * 2 * cw
        f.append(rect(bx - 2, y1 - 2, 2 * cw + 4, ch + 4, fill="none", stroke=BORDER_BASE, sw=1.2, rx=3))

    # Прохід 2 (width = 2)
    y2 = 205
    f.append(text(20, y2 + 24, "Прохід 2 (width=2):", size=12, bold=True, color=BORDER_LEFT, anchor="start"))
    f.append(text(20, y2 + 38, "злиття блоків по 2 ел.", size=10, color=MUTED, anchor="start"))
    v2 = [3, 27, 38, 43, 9, 10, 19, 82]
    f2 = [BG_LEFT]*4 + [BG_RIGHT]*4
    s2 = [BORDER_LEFT]*4 + [BORDER_RIGHT]*4
    f.append(array_bar(x0, y2, v2, cw, ch, f2, s2))
    # Розподільчі рамки для блоків розміру 4
    for b in range(2):
        bx = x0 + b * 4 * cw
        f.append(rect(bx - 2, y2 - 2, 4 * cw + 4, ch + 4, fill="none", stroke=BORDER_BASE, sw=1.5, rx=3))

    # Прохід 3 (width = 4)
    y3 = 285
    f.append(text(20, y3 + 24, "Прохід 3 (width=4):", size=12, bold=True, color=BORDER_MERGED, anchor="start"))
    f.append(text(20, y3 + 38, "злиття блоків по 4 ел.", size=10, color=MUTED, anchor="start"))
    v3 = [3, 9, 10, 19, 27, 38, 43, 82]
    f.append(array_bar(x0, y3, v3, cw, ch, BG_MERGED, BORDER_MERGED))
    f.append(rect(x0 - 2, y3 - 2, 8 * cw + 4, ch + 4, fill="none", stroke=BORDER_MERGED, sw=2.0, rx=4))

    render(os.path.join(IMG, "bottom-up-merge.svg"), W, H, "".join(f),
           title="Ітеративне сортування злиттям знизу вгору (Bottom-Up)")

# ── Фігура 4: Сортування однозв'язного списку ─────────────────────────────────
def fig_linked_list():
    W, H = 820, 310
    f = []
    nw, nh = 65, 34

    def node(x, y, val, next_txt="•", bg=FILL, stroke=LINE):
        res = []
        res.append(rect(x, y, nw, nh, fill=bg, stroke=stroke, sw=1.5, rx=4))
        res.append(line(x + 40, y, x + 40, y + nh, color=stroke, sw=1.2))
        res.append(text(x + 20, y + nh / 2 + 5, str(val), size=13, bold=True))
        res.append(text(x + 52, y + nh / 2 + 5, next_txt, size=14, color=BORDER_LEFT, bold=True))
        return "".join(res)

    def ptr_arrow(x1, y1, x2, y2, color=LINE):
        return line(x1, y1, x2, y2, color=color, sw=1.5) + circle(x2, y2, 2.5, fill=color, stroke=color)

    # Крок 1: Пошук середини списку (Fast & Slow pointers)
    y1 = 60
    f.append(text(20, y1 + 18, "1. Поділ (Slow/Fast):", size=12, bold=True, color=MUTED, anchor="start"))
    nodes_v1 = [4, 2, 1, 3]
    x_start = 180
    gap = 95
    for i, v in enumerate(nodes_v1):
        nx = x_start + i * gap
        f.append(node(nx, y1, v))
        if i < 3:
            f.append(ptr_arrow(nx + 52, y1 + nh / 2, nx + gap, y1 + nh / 2, color=BORDER_LEFT))
    
    # Позначки вказівників slow і fast
    f.append(text(x_start + 1 * gap + 20, y1 - 8, "slow (mid)", size=11, color=BORDER_RIGHT, bold=True))
    f.append(line(x_start + 1 * gap + 20, y1 - 4, x_start + 1 * gap + 20, y1, color=BORDER_RIGHT, sw=1.5))
    
    f.append(text(x_start + 3 * gap + 20, y1 - 8, "fast (null)", size=11, color=BORDER_RIGHT, bold=True))
    f.append(line(x_start + 3 * gap + 20, y1 - 4, x_start + 3 * gap + 20, y1, color=BORDER_RIGHT, sw=1.5))

    # Крок 2: Розрив зв'язку slow->next = nullptr
    y2 = 145
    f.append(text(20, y2 + 18, "2. Два списки:", size=12, bold=True, color=MUTED, anchor="start"))
    # Список L1: [2, 4]
    f.append(text(140, y2 + 18, "L1:", size=12, bold=True, color=BORDER_LEFT))
    f.append(node(170, y2, 2, bg=BG_LEFT, stroke=BORDER_LEFT))
    f.append(ptr_arrow(170 + 52, y2 + nh / 2, 170 + gap, y2 + nh / 2, color=BORDER_LEFT))
    f.append(node(170 + gap, y2, 4, next_txt="ø", bg=BG_LEFT, stroke=BORDER_LEFT))

    # Список L2: [1, 3]
    f.append(text(460, y2 + 18, "L2:", size=12, bold=True, color=BORDER_RIGHT))
    f.append(node(490, y2, 1, bg=BG_RIGHT, stroke=BORDER_RIGHT))
    f.append(ptr_arrow(490 + 52, y2 + nh / 2, 490 + gap, y2 + nh / 2, color=BORDER_RIGHT))
    f.append(node(490 + gap, y2, 3, next_txt="ø", bg=BG_RIGHT, stroke=BORDER_RIGHT))

    # Крок 3: Переплетення покажчиків у злитий список
    y3 = 230
    f.append(text(20, y3 + 18, "3. Злиття вказівників:", size=12, bold=True, color=BORDER_MERGED, anchor="start"))
    res_nodes = [(1, BG_RIGHT, BORDER_RIGHT), (2, BG_LEFT, BORDER_LEFT), 
                 (3, BG_RIGHT, BORDER_RIGHT), (4, BG_LEFT, BORDER_LEFT)]
    x_res = 180
    for i, (v, bg_c, str_c) in enumerate(res_nodes):
        nx = x_res + i * gap
        ntxt = "ø" if i == 3 else "•"
        f.append(node(nx, y3, v, next_txt=ntxt, bg=bg_c, stroke=str_c))
        if i < 3:
            f.append(ptr_arrow(nx + 52, y3 + nh / 2, nx + gap, y3 + nh / 2, color=BORDER_MERGED))

    f.append(text(x_res + 3.8 * gap + 50, y3 + nh / 2 + 5, "O(1) додаткової пам'яті", size=12, color=BORDER_MERGED, bold=True, anchor="start"))

    render(os.path.join(IMG, "linked-list-merge.svg"), W, H, "".join(f),
           title="Сортування однозв'язного списку злиттям без виділення пам'яті")

if __name__ == "__main__":
    fig_tree()
    fig_two_pointers()
    fig_bottom_up()
    fig_linked_list()
    print("Всі 4 фігури успішно згенеровано.")
