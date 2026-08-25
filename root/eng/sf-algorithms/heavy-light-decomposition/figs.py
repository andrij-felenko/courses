# -*- coding: utf-8 -*-
import sys
import os

# Four steps up to repo root scripts directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def build_figure_1():
    """Фігура 1: Розбиття дерева на важкі та легкі ребра (Heavy-Light Tree Structure)."""
    W, H = 960, 520
    frags = []

    # Дерево з 12 вузлів:
    # 1 (sz=12, root)
    # ├── 2 (sz=7) [HEAVY]
    # │   ├── 4 (sz=2) [LIGHT]
    # │   │   └── 8 (sz=1) [HEAVY]
    # │   └── 5 (sz=4) [HEAVY]
    # │       ├── 9 (sz=1) [LIGHT]
    # │       └── 10 (sz=2) [HEAVY]
    # │           └── 12 (sz=1) [HEAVY]
    # └── 3 (sz=4) [LIGHT]
    #     ├── 6 (sz=1) [LIGHT]
    #     └── 7 (sz=2) [HEAVY]
    #         └── 11 (sz=1) [HEAVY]

    # Координати вузлів (cx, cy, id, sz, is_heavy_child, head_id)
    # Ліві відступи та рівні глибини
    nodes = {
        1: (480, 60, "1", "sz=12", False, 1),
        2: (280, 160, "2", "sz=7", True, 1),
        3: (680, 160, "3", "sz=4", False, 3),
        4: (160, 260, "4", "sz=2", False, 4),
        5: (380, 260, "5", "sz=4", True, 1),
        6: (580, 260, "6", "sz=1", False, 6),
        7: (780, 260, "7", "sz=2", True, 3),
        8: (160, 360, "8", "sz=1", True, 4),
        9: (280, 360, "9", "sz=1", False, 9),
        10: (440, 360, "10", "sz=2", True, 1),
        11: (780, 360, "11", "sz=1", True, 3),
        12: (440, 450, "12", "sz=1", True, 1),
    }

    edges = [
        (1, 2, True),   # Heavy
        (1, 3, False),  # Light
        (2, 4, False),  # Light
        (2, 5, True),   # Heavy
        (3, 6, False),  # Light
        (3, 7, True),   # Heavy
        (4, 8, True),   # Heavy
        (5, 9, False),  # Light
        (5, 10, True),  # Heavy
        (7, 11, True),  # Heavy
        (10, 12, True), # Heavy
    ]

    # Малюємо ребра
    for u, v, is_heavy in edges:
        x1, y1 = nodes[u][0], nodes[u][1]
        x2, y2 = nodes[v][0], nodes[v][1]
        if is_heavy:
            # Суцільна товста синя лінія
            frags.append(line(x1, y1 + 22, x2, y2 - 22, color=NEG, sw=4.0))
        else:
            # Тонка пунктирна сіра лінія
            frags.append(line(x1, y1 + 22, x2, y2 - 22, color=MUTED, sw=2.0, dash="5,5"))

    # Малюємо вузли
    chain_colors = {
        1: ("#eaf0fd", NEG),     # Chain 1-2-5-10-12
        3: ("#e8f8f5", FIELD),   # Chain 3-7-11
        4: ("#fef9e7", "#d4ac0d"),# Chain 4-8
        6: ("#f4f6f8", LINE),    # Chain 6
        9: ("#f4f6f8", LINE),    # Chain 9
    }

    for nid, (cx, cy, label, sz_str, is_h, head_id) in nodes.items():
        bg, border = chain_colors[head_id]
        box = fitbox(cx - 36, cy - 22, 72, 44, f"v={label}\n{sz_str}", size=12, bold=True, fill=bg, stroke=border, sw=2.0)
        frags.append(box)

    # Легенда
    leg_x, leg_y = 50, 40
    frags.append(rect(leg_x, leg_y, 230, 120, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(leg_x + 115, leg_y + 22, "Класифікація ребер", size=13, bold=True))
    frags.append(line(leg_x + 15, leg_y + 50, leg_x + 65, leg_y + 50, color=NEG, sw=4.0))
    frags.append(text(leg_x + 75, leg_y + 54, "Важке ребро (sz > n/2)", size=11, anchor="start"))
    frags.append(line(leg_x + 15, leg_y + 80, leg_x + 65, leg_y + 80, color=MUTED, sw=2.0, dash="5,5"))
    frags.append(text(leg_x + 75, leg_y + 84, "Легке ребро (sz <= n/2)", size=11, anchor="start"))
    frags.append(text(leg_x + 15, leg_y + 106, "Колір вузла = належність до ланцюга", size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "heavy-light-tree-structure.svg"), W, H, *frags)


def build_figure_2():
    """Фігура 2: Лінеаризація важких ланцюгів у неперервні відрізки масиву."""
    W, H = 960, 440
    frags = []

    # Порядок обходу DFS (спочатку heavy child):
    # Ланцюг 1 (голова 1): 1 -> 2 -> 5 -> 10 -> 12  [поз. 0, 1, 2, 3, 4]
    # Піддерево вузла 5 (легка дитина 9): 9         [поз. 5]
    # Піддерево вузла 2 (легка дитина 4 -> 8): 4, 8 [поз. 6, 7]
    # Ланцюг 3 (голова 3, легка дитина 1): 3 -> 7 -> 11 [поз. 8, 9, 10]
    # Піддерево вузла 3 (легка дитина 6): 6         [поз. 11]

    # Таблиця масиву 1D (довжина 12)
    flat_order = [
        (0, "v=1", "Ланцюг 1 (гол. 1)", "#eaf0fd", NEG),
        (1, "v=2", "Ланцюг 1", "#eaf0fd", NEG),
        (2, "v=5", "Ланцюг 1", "#eaf0fd", NEG),
        (3, "v=10", "Ланцюг 1", "#eaf0fd", NEG),
        (4, "v=12", "Ланцюг 1", "#eaf0fd", NEG),
        (5, "v=9", "Ланцюг 9", "#f4f6f8", LINE),
        (6, "v=4", "Ланцюг 4 (гол. 4)", "#fef9e7", "#d4ac0d"),
        (7, "v=8", "Ланцюг 4", "#fef9e7", "#d4ac0d"),
        (8, "v=3", "Ланцюг 3 (гол. 3)", "#e8f8f5", FIELD),
        (9, "v=7", "Ланцюг 3", "#e8f8f5", FIELD),
        (10, "v=11", "Ланцюг 3", "#e8f8f5", FIELD),
        (11, "v=6", "Ланцюг 6", "#f4f6f8", LINE),
    ]

    cell_w = 70
    start_x = (W - (12 * cell_w)) / 2
    arr_y = 160

    frags.append(text(W / 2, 40, "Розподіл вершин дерева у лінійному масиві структури даних", size=16, bold=True))
    frags.append(text(W / 2, 70, "DFS-нумерація з першочерговим проходженням важкої дитини гарантує неперервність", size=13, color=MUTED))

    # Малюємо комірки
    for i, (pos, label, chain_name, bg, stroke_col) in enumerate(flat_order):
        cx = start_x + i * cell_w
        # Комірка
        frags.append(rect(cx, arr_y, cell_w, 65, fill=bg, stroke=stroke_col, sw=2.0))
        frags.append(text(cx + cell_w / 2, arr_y + 24, label, size=13, bold=True))
        frags.append(text(cx + cell_w / 2, arr_y + 48, f"idx={pos}", size=11, color=MUTED))

    # Дужки / виділення для важких ланцюгів та піддерев зверху та знизу
    # 1. Головний ланцюг [0..4] (вершини 1, 2, 5, 10, 12)
    c1_x1 = start_x
    c1_x2 = start_x + 5 * cell_w
    frags.append(rect(c1_x1, arr_y - 45, c1_x2 - c1_x1, 32, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text((c1_x1 + c1_x2) / 2, arr_y - 25, "Важкий ланцюг 1 [0..4]: вершини {1, 2, 5, 10, 12}", size=11, color=NEG, bold=True))

    # 2. Ланцюг 4 [6..7] (вершини 4, 8)
    c4_x1 = start_x + 6 * cell_w
    c4_x2 = start_x + 8 * cell_w
    frags.append(rect(c4_x1, arr_y - 45, c4_x2 - c4_x1, 32, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=4))
    frags.append(text((c4_x1 + c4_x2) / 2, arr_y - 25, "Ланцюг 4 [6..7]", size=11, color="#b7950b", bold=True))

    # 3. Ланцюг 3 [8..10] (вершини 3, 7, 11)
    c3_x1 = start_x + 8 * cell_w
    c3_x2 = start_x + 11 * cell_w
    frags.append(rect(c3_x1, arr_y - 45, c3_x2 - c3_x1, 32, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text((c3_x1 + c3_x2) / 2, arr_y - 25, "Важкий ланцюг 3 [8..10]: {3, 7, 11}", size=11, color=FIELD, bold=True))

    # Піддерева знизу
    # Піддерево вершини 2: охоплює [1..7] (розмір sz=7)
    sub2_x1 = start_x + 1 * cell_w
    sub2_x2 = start_x + 8 * cell_w
    frags.append(rect(sub2_x1, arr_y + 80, sub2_x2 - sub2_x1, 36, fill="#fdfefe", stroke=LINE, sw=1.5, rx=4))
    frags.append(text((sub2_x1 + sub2_x2) / 2, arr_y + 102, "Піддерево вершини v=2: відрізок [1..7] (довжина sz=7)", size=12, bold=True))

    # Піддерево вершини 3: охоплює [8..11] (розмір sz=4)
    sub3_x1 = start_x + 8 * cell_w
    sub3_x2 = start_x + 12 * cell_w
    frags.append(rect(sub3_x1, arr_y + 80, sub3_x2 - sub3_x1, 36, fill="#fdfefe", stroke=LINE, sw=1.5, rx=4))
    frags.append(text((sub3_x1 + sub3_x2) / 2, arr_y + 102, "Піддерево v=3: відрізок [8..11] (sz=4)", size=12, bold=True))

    # Пояснення знизу
    frags.append(text(W / 2, arr_y + 155, "Будь-який запит до піддерева v відповідає ОДНОМУ неперервному відрізку [pos[v]..pos[v]+sz[v]-1]", size=13, color=INK, bold=True))
    frags.append(text(W / 2, arr_y + 185, "Запити на шляху u~v розбиваються максимум на 2·log2(N) неперервних підвідрізків", size=13, color=MUTED))

    render(os.path.join(OUT, "hld-linearization-segments.svg"), W, H, *frags)


def build_figure_3():
    """Фігура 3: Траєкторія запиту на шляху та переходи між ланцюгами (Path Query Traversal)."""
    W, H = 960, 480
    frags = []

    # Показуємо шлях між u=8 (глибина 3, ланцюг 4) та v=11 (глибина 3, ланцюг 3)
    # Спільний предок: LCA = 1
    # Кроки підйому:
    # 1) u=8, head[8]=4. Запит на ланцюгу 4: [pos[4]..pos[8]] -> [6..7]. Підйом: u = parent[4] = 2.
    # 2) v=11, head[11]=3, u=2, head[2]=1. Глибша голова: depth[head[v]=3]=1 > depth[head[u]=1]=0.
    #    Запит на ланцюгу 3: [pos[3]..pos[11]] -> [8..10]. Підйом: v = parent[3] = 1.
    # 3) u=2 (head=1), v=1 (head=1). Однакова голова (head[u] == head[v]).
    #    Запит на спільному ланцюгу: [pos[1]..pos[2]] -> [0..1]. Завершення.

    # 3 великі інформаційні блоки-кроки
    step_w = 270
    step_h = 240
    step_y = 100

    steps_data = [
        (
            60,
            "Крок 1: Обробка вершини u=8",
            "head[8] = 4 (глибина голови = 2)\nhead[11] = 3 (глибина голови = 1)",
            "u глибше за v за головою:\n1. Запит відрізка [pos[4]..pos[8]]\n   у Segment Tree: [6..7]\n2. Стрибок u = parent[4] = 2",
            "#fef9e7",
            "#d4ac0d",
        ),
        (
            345,
            "Крок 2: Обробка вершини v=11",
            "u = 2 (head[2] = 1, depth=0)\nv = 11 (head[11] = 3, depth=1)",
            "v глибше за u за головою:\n1. Запит відрізка [pos[3]..pos[11]]\n   у Segment Tree: [8..10]\n2. Стрибок v = parent[3] = 1",
            "#e8f8f5",
            FIELD,
        ),
        (
            630,
            "Крок 3: Фінал на спільному ланцюгу",
            "u = 2, v = 1\nhead[u] == head[v] == 1 (LCA = 1)",
            "Обидві вершини в одному ланцюгу:\n1. Запит відрізка [pos[1]..pos[2]]\n   у Segment Tree: [0..1]\n2. Алгоритм завершено!",
            "#eaf0fd",
            NEG,
        ),
    ]

    frags.append(text(W / 2, 45, "Покрокова декомпозиція запиту на шляху між вершинами u=8 та v=11", size=16, bold=True))

    for x, title_txt, state_txt, action_txt, bg_col, stroke_col in steps_data:
        frags.append(rect(x, step_y, step_w, step_h, fill=bg_col, stroke=stroke_col, sw=2.0, rx=8))
        frags.append(text(x + step_w / 2, step_y + 28, title_txt, size=13, bold=True, color=stroke_col))
        frags.append(line(x + 15, step_y + 42, x + step_w - 15, step_y + 42, color=stroke_col, sw=1.0))

        frags.append(fitbox(x + 12, step_y + 52, step_w - 24, 60, state_txt, size=12, fill="#ffffff", stroke=MUTED, sw=1.0))
        frags.append(fitbox(x + 12, step_y + 120, step_w - 24, 105, action_txt, size=12, fill="#ffffff", stroke=stroke_col, sw=1.5, bold=True))

    # Стрілки переходів між кроками
    frags.append(arrow(330, step_y + step_h / 2, 345, step_y + step_h / 2, color=LINE, sw=2.5))
    frags.append(arrow(615, step_y + step_h / 2, 630, step_y + step_h / 2, color=LINE, sw=2.5))

    # Підсумок внизу
    bottom_box = fitbox(
        60,
        370,
        840,
        70,
        "Підсумок: Шлях 8 ~ 11 довжиною 5 ребер розбито на 3 запити до дерева відрізків: [6..7] + [8..10] + [0..1].\n"
        "Загальна складність запиту = O(кількість ланцюгів · час запиту Segment Tree) = O(log N · log N) = O(log² N).",
        size=12,
        bold=True,
        fill="#f4f6f8",
        stroke=LINE,
        sw=1.5,
    )
    frags.append(bottom_box)

    render(os.path.join(OUT, "hld-path-query-traversal.svg"), W, H, *frags)


if __name__ == "__main__":
    build_figure_1()
    build_figure_2()
    build_figure_3()
    print("Figures generated successfully.")
