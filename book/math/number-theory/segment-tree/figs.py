# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_segment_tree_structure():
    # Render structure diagram of Segment Tree for interval [0, 7]
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 35, "Ієрархічна структура дерева відрізків для масиву з N = 8 елементів", size=16, bold=True))
    p.append(text(W / 2, 60, "Кожен вузол зберігає агреговану величину на відрізку [L, R] та індекс у масиві дерева", size=13, color=MUTED))

    # Nodes definition: (id, x, y, range_str, index_str, fill_color)
    # Level 0 (Root)
    nodes = [
        ("r", 480, 110, "[0, 7]", "v=1", "#eafaf0"),
        
        # Level 1
        ("l1_0", 240, 190, "[0, 3]", "v=2", "#eafaf0"),
        ("l1_1", 720, 190, "[4, 7]", "v=3", "#eafaf0"),

        # Level 2
        ("l2_0", 120, 270, "[0, 1]", "v=4", "#f8f9fa"),
        ("l2_1", 360, 270, "[2, 3]", "v=5", "#f8f9fa"),
        ("l2_2", 600, 270, "[4, 5]", "v=6", "#f8f9fa"),
        ("l2_3", 840, 270, "[6, 7]", "v=7", "#f8f9fa"),

        # Level 3 (Leaves)
        ("l3_0", 60,  350, "[0, 0]", "v=8", "#e8f0fe"),
        ("l3_1", 180, 350, "[1, 1]", "v=9", "#e8f0fe"),
        ("l3_2", 300, 350, "[2, 2]", "v=10", "#e8f0fe"),
        ("l3_3", 420, 350, "[3, 3]", "v=11", "#e8f0fe"),
        ("l3_4", 540, 350, "[4, 4]", "v=12", "#e8f0fe"),
        ("l3_5", 660, 350, "[5, 5]", "v=13", "#e8f0fe"),
        ("l3_6", 780, 350, "[6, 6]", "v=14", "#e8f0fe"),
        ("l3_7", 900, 350, "[7, 7]", "v=15", "#e8f0fe"),
    ]

    edges = [
        ("r", "l1_0"), ("r", "l1_1"),
        ("l1_0", "l2_0"), ("l1_0", "l2_1"),
        ("l1_1", "l2_2"), ("l1_1", "l2_3"),
        ("l2_0", "l3_0"), ("l2_0", "l3_1"),
        ("l2_1", "l3_2"), ("l2_1", "l3_3"),
        ("l2_2", "l3_4"), ("l2_2", "l3_5"),
        ("l2_3", "l3_6"), ("l2_3", "l3_7"),
    ]

    node_dict = {n[0]: n for n in nodes}

    # Draw edges
    for src, dst in edges:
        x1, y1 = node_dict[src][1], node_dict[src][2] + 20
        x2, y2 = node_dict[dst][1], node_dict[dst][2] - 20
        p.append(line(x1, y1, x2, y2, color=LINE, sw=1.5))

    # Draw nodes
    for nid, x, y, rstr, vstr, bg in nodes:
        w, h = 84, 42
        p.append(rect(x - w/2, y - h/2, w, h, fill=bg, stroke=FIELD if bg == "#eafaf0" else LINE, sw=1.5, rx=6))
        p.append(text(x, y - 5, rstr, size=13, bold=True, color=INK))
        p.append(text(x, y + 13, vstr, size=11, color=MUTED))

    # Linear array mapping at the bottom
    p.append(rect(40, 410, 880, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(W / 2, 428, "Лінійний масив дерева (розмір 2^4 = 16 комірок):", size=12, bold=True, color=INK))
    p.append(text(W / 2, 448, "tree = [-, [0..7], [0..3], [4..7], [0..1], [2..3], [4..5], [6..7], [0..0], [1..1], ...]", size=11, color=MUTED))

    render(os.path.join(OUT, "fig-segment-tree-structure.svg"), W, H, *p, title="Структура дерева відрізків")


def fig_segment_tree_range_query():
    # Render diagram of Range Query execution for range [1, 6]
    W, H = 960, 460
    p = []

    p.append(text(W / 2, 35, "Обчислення інтервального запиту query(1, 6) в дереві відрізків", size=16, bold=True))
    p.append(text(W / 2, 60, "Виділені зеленим вузли дають точне покриття інтервалу [1, 6] без подальшого спуску", size=13, color=MUTED))

    # Node status: 'cover' (fully inside query), 'partial' (partially inside), 'outside' (completely outside)
    nodes = [
        ("r", 480, 110, "[0, 7]", "partial"),
        
        ("l1_0", 240, 190, "[0, 3]", "partial"),
        ("l1_1", 720, 190, "[4, 7]", "partial"),

        ("l2_0", 120, 270, "[0, 1]", "partial"),
        ("l2_1", 360, 270, "[2, 3]", "cover"),
        ("l2_2", 600, 270, "[4, 5]", "cover"),
        ("l2_3", 840, 270, "[6, 7]", "partial"),

        ("l3_0", 60,  350, "[0, 0]", "outside"),
        ("l3_1", 180, 350, "[1, 1]", "cover"),
        ("l3_6", 780, 350, "[6, 6]", "cover"),
        ("l3_7", 900, 350, "[7, 7]", "outside"),
    ]

    edges = [
        ("r", "l1_0", LINE), ("r", "l1_1", LINE),
        ("l1_0", "l2_0", LINE), ("l1_0", "l2_1", FIELD),
        ("l1_1", "l2_2", FIELD), ("l1_1", "l2_3", LINE),
        ("l2_0", "l3_0", LINE), ("l2_0", "l3_1", FIELD),
        ("l2_3", "l3_6", FIELD), ("l2_3", "l3_7", LINE),
    ]

    node_dict = {n[0]: n for n in nodes}

    for src, dst, c in edges:
        x1, y1 = node_dict[src][1], node_dict[src][2] + 20
        x2, y2 = node_dict[dst][1], node_dict[dst][2] - 20
        p.append(line(x1, y1, x2, y2, color=c, sw=2.0 if c == FIELD else 1.2))

    for nid, x, y, rstr, st in nodes:
        w, h = 84, 40
        if st == "cover":
            bg, border, tc = "#eafaf0", FIELD, FIELD
            label_sub = "Покриває"
        elif st == "partial":
            bg, border, tc = "#fff9e6", "#f0b400", INK
            label_sub = "Частково"
        else:
            bg, border, tc = "#f8f9fa", LINE, MUTED
            label_sub = "Відсічено"

        p.append(rect(x - w/2, y - h/2, w, h, fill=bg, stroke=border, sw=2.0 if st != "outside" else 1.0, rx=6))
        p.append(text(x, y - 5, rstr, size=13, bold=True, color=tc))
        p.append(text(x, y + 13, label_sub, size=10.5, color=tc))

    # Summary box at bottom
    b, _, _ = textbox(W / 2, 420, "Результат query(1, 6) = val[1, 1] ⊗ val[2, 3] ⊗ val[4, 5] ⊗ val[6, 6]  (всього 4 вузли замість 6)",
                      size=13, pad=10, fill="#ffffff", stroke=FIELD, sw=1.8, bold=True)
    p.append(b)

    render(os.path.join(OUT, "fig-segment-tree-range-query.svg"), W, H, *p, title="Інтервальний запит у дереві відрізків")


def fig_lazy_propagation():
    # Render diagram of Lazy Propagation mechanism
    W, H = 960, 440
    p = []

    p.append(text(W / 2, 35, "Принцип відкладеної пропогації (Lazy Propagation)", size=16, bold=True))
    p.append(text(W / 2, 60, "Відкладений прапорець (lazy tag) зберігається у вузлі й проштовхується вниз лише при потребі", size=13, color=MUTED))

    # Left panel: Lazy tag set at node
    p.append(rect(40, 90, 420, 320, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=10))
    p.append(text(250, 115, "Крок 1: Встановлення відкладеного прапорця", size=14, bold=True, color=INK))
    p.append(text(250, 140, "Оновлення update(2, 5, +10) повністю накриває [2, 3]", size=12, color=MUTED))

    p.append(rect(200, 175, 100, 50, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(250, 195, "Вузол [2, 3]", size=13, bold=True, color=FIELD))
    p.append(text(250, 215, "lazy = +10", size=11.5, bold=True, color="#d9534f"))

    p.append(line(230, 225, 170, 275, color=LINE, sw=1.2))
    p.append(line(270, 225, 330, 275, color=LINE, sw=1.2))

    p.append(rect(120, 275, 100, 45, fill="#f8f9fa", stroke=LINE, sw=1.0, rx=6))
    p.append(text(170, 292, "Вузол [2, 2]", size=12, color=INK))
    p.append(text(170, 310, "старі дані", size=10.5, color=MUTED))

    p.append(rect(280, 275, 100, 45, fill="#f8f9fa", stroke=LINE, sw=1.0, rx=6))
    p.append(text(330, 292, "Вузол [3, 3]", size=12, color=INK))
    p.append(text(330, 310, "старі дані", size=10.5, color=MUTED))

    p.append(text(250, 375, "Діти НЕ оновлюються негайно — економія O(log N)", size=12, bold=True, color=FIELD))

    # Right panel: Push down on access
    p.append(rect(500, 90, 420, 320, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(710, 115, "Крок 2: Проштовхування вниз (Push Down)", size=14, bold=True, color=FIELD))
    p.append(text(710, 140, "При подальшому запиті push(v) передає lazy дітям", size=12, color=MUTED))

    p.append(rect(660, 175, 100, 50, fill="#f8f9fa", stroke=LINE, sw=1.2, rx=6))
    p.append(text(710, 195, "Вузол [2, 3]", size=13, bold=True, color=INK))
    p.append(text(710, 215, "lazy = 0 (скинуто)", size=11, color=MUTED))

    p.append(arrow(690, 225, 630, 275, color=FIELD, sw=2.0))
    p.append(arrow(730, 225, 790, 275, color=FIELD, sw=2.0))

    p.append(rect(580, 275, 100, 45, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(630, 292, "Вузол [2, 2]", size=12, bold=True, color=FIELD))
    p.append(text(630, 310, "lazy += +10", size=11, bold=True, color="#d9534f"))

    p.append(rect(740, 275, 100, 45, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(790, 292, "Вузол [3, 3]", size=12, bold=True, color=FIELD))
    p.append(text(790, 310, "lazy += +10", size=11, bold=True, color="#d9534f"))

    p.append(text(710, 375, "Інваріант коректності збережено для всіх піддерев", size=12, bold=True, color=FIELD))

    render(os.path.join(OUT, "fig-lazy-propagation.svg"), W, H, *p, title="Механізм Lazy Propagation")


if __name__ == "__main__":
    fig_segment_tree_structure()
    fig_segment_tree_range_query()
    fig_lazy_propagation()
    print("All segment tree figures generated successfully!")
