# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ──────────────────────────────────────────────────────────
COLOR_BG_LIGHT   = "#f8fafc"
COLOR_NODE_BG    = "#ffffff"
COLOR_NODE_DONE  = "#e0f2fe"  # Блакитний (початкові ребра / досяжні)
COLOR_NODE_PIVOT = "#fef3c7"  # Жовтий/Помаранчевий (вузол-стрижень k)
COLOR_NODE_TRANS = "#dcfce7"  # Зелений (додані транзитивні ребра)

BORDER_NORMAL  = "#475569"
BORDER_PRIMARY = "#0284c7"
BORDER_PIVOT   = "#d97706"
BORDER_TRANS   = "#16a34a"

LINE_MUTED    = "#94a3b8"
LINE_TRANS    = "#16a34a"
LINE_PRIMARY  = "#0284c7"

def dashed_arrow(x1, y1, x2, y2, color=LINE_TRANS, sw=2.2, dash="5 4"):
    """Малює штриховану стрілку через line та arrow-голівку."""
    # Лінія зі штрихом
    out = line(x1, y1, x2, y2, color=color, sw=sw, dash=dash)
    # Коротка стрілка на кінці для голівки
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    out += arrow(x2 - ux * 4, y2 - uy * 4, x2, y2, color=color, sw=sw)
    return out

# ── ФІГ. 1: Концепт транзитивного замикання (Граф G та його замикання G*) ───
def fig_transitive_closure_concept():
    path = os.path.join(OUT, "transitive-closure-concept.svg")
    W, H = 820, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=COLOR_BG_LIGHT, stroke="#cbd5e1", sw=1.0, rx=8))

    p.append(text(210, 38, "Вихідний орієнтований граф G", size=15, color=INK, bold=True))
    p.append(text(610, 38, "Транзитивне замикання G*", size=15, color=INK, bold=True))

    nodes_g = {
        0: (70, 120),
        1: (180, 80),
        2: (290, 120),
        3: (180, 200),
        4: (310, 220)
    }

    nodes_gstar = {k: (v[0] + 400, v[1]) for k, v in nodes_g.items()}

    edges_g = [(0, 1), (1, 2), (2, 3), (3, 4), (1, 3)]
    edges_trans = [(0, 2), (0, 3), (0, 4), (1, 4), (2, 4)]

    for u, v in edges_g:
        x1, y1 = nodes_g[u]
        x2, y2 = nodes_g[v]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        r = 18
        p.append(arrow(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, color=BORDER_PRIMARY, sw=2.0))

    for u, v in edges_g:
        x1, y1 = nodes_gstar[u]
        x2, y2 = nodes_gstar[v]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        r = 18
        p.append(arrow(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, color=BORDER_PRIMARY, sw=1.8))

    for u, v in edges_trans:
        x1, y1 = nodes_gstar[u]
        x2, y2 = nodes_gstar[v]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        r = 18
        p.append(dashed_arrow(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, color=LINE_TRANS, sw=2.2, dash="5 4"))

    for nid, (cx, cy) in nodes_g.items():
        p.append(circle(cx, cy, 18, fill=COLOR_NODE_DONE, stroke=BORDER_PRIMARY, sw=2.0))
        p.append(text(cx, cy + 5, str(nid), size=14, color=INK, bold=True))

    for nid, (cx, cy) in nodes_gstar.items():
        p.append(circle(cx, cy, 18, fill=COLOR_NODE_TRANS, stroke=BORDER_TRANS, sw=2.0))
        p.append(text(cx, cy + 5, str(nid), size=14, color=INK, bold=True))

    p.append(text(190, 268, "Матриця суміжності A (0/1)", size=12, color=MUTED, bold=True))
    matrix_a = [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0]
    ]
    for r_idx in range(5):
        for c_idx in range(5):
            val = matrix_a[r_idx][c_idx]
            col = BORDER_PRIMARY if val == 1 else "#94a3b8"
            bg_c = COLOR_NODE_DONE if val == 1 else "#ffffff"
            x_pos = 120 + c_idx * 28
            y_pos = 282 + r_idx * 14
            p.append(rect(x_pos - 10, y_pos - 10, 22, 13, fill=bg_c, stroke=col, sw=1.0, rx=2))
            p.append(text(x_pos, y_pos, str(val), size=10, color=col, bold=(val==1)))

    p.append(text(590, 268, "Матриця досяжності T (G*)", size=12, color=MUTED, bold=True))
    matrix_t = [
        [0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0]
    ]
    for r_idx in range(5):
        for c_idx in range(5):
            val = matrix_t[r_idx][c_idx]
            is_orig = matrix_a[r_idx][c_idx] == 1
            col = BORDER_PRIMARY if is_orig else (BORDER_TRANS if val == 1 else "#94a3b8")
            bg_c = COLOR_NODE_DONE if is_orig else (COLOR_NODE_TRANS if val == 1 else "#ffffff")
            x_pos = 520 + c_idx * 28
            y_pos = 282 + r_idx * 14
            p.append(rect(x_pos - 10, y_pos - 10, 22, 13, fill=bg_c, stroke=col, sw=1.0, rx=2))
            p.append(text(x_pos, y_pos, str(val), size=10, color=col, bold=(val==1)))

    p.append(rect(345, 140, 120, 70, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(arrow(355, 160, 390, 160, color=BORDER_PRIMARY, sw=1.8))
    p.append(text(425, 164, "Пряме ребро", size=10, color=INK))
    p.append(dashed_arrow(355, 190, 390, 190, color=LINE_TRANS, sw=2.0, dash="4 3"))
    p.append(text(425, 194, "Транзитивне", size=10, color=BORDER_TRANS, bold=True))

    render(path, W, H, *p)


# ── ФІГ. 2: Крок опорного вузла k (Warshall's pivot step) ───────────────────
def fig_warshall_pivot_step():
    path = os.path.join(OUT, "warshall-pivot-step.svg")
    W, H = 760, 300
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=COLOR_BG_LIGHT, stroke="#cbd5e1", sw=1.0, rx=8))
    p.append(text(380, 38, "Крок динамічного програмування: транзитивний міст через k", size=15, color=INK, bold=True))

    cx_i, cy_i = 140, 190
    cx_k, cy_k = 380, 100
    cx_j, cy_j = 620, 190

    r = 24
    p.append(arrow(cx_i + 16, cy_i - 16, cx_k - 20, cy_k + 14, color=BORDER_PRIMARY, sw=2.5))
    p.append(arrow(cx_k + 20, cy_k + 14, cx_j - 16, cy_j - 16, color=BORDER_PRIMARY, sw=2.5))

    p.append(rect(220, 115, 105, 24, fill="#ffffff", stroke=BORDER_PRIMARY, sw=1.0, rx=4))
    p.append(text(272, 131, "T[i][k] == 1", size=11, color=BORDER_PRIMARY, bold=True))

    p.append(rect(435, 115, 105, 24, fill="#ffffff", stroke=BORDER_PRIMARY, sw=1.0, rx=4))
    p.append(text(487, 131, "T[k][j] == 1", size=11, color=BORDER_PRIMARY, bold=True))

    p.append(dashed_arrow(cx_i + 24, cy_i, cx_j - 24, cy_j, color=LINE_TRANS, sw=3.0, dash="6 4"))

    p.append(rect(310, 210, 140, 28, fill=COLOR_NODE_TRANS, stroke=BORDER_TRANS, sw=1.5, rx=4))
    p.append(text(380, 228, "T[i][j] |= (1 && 1)", size=12, color=BORDER_TRANS, bold=True))

    p.append(circle(cx_i, cy_i, r, fill=COLOR_NODE_DONE, stroke=BORDER_PRIMARY, sw=2.5))
    p.append(text(cx_i, cy_i + 6, "i", size=16, color=INK, bold=True))
    p.append(text(cx_i, cy_i + r + 18, "Початковий вузол", size=11, color=MUTED))

    p.append(circle(cx_k, cy_k, r + 2, fill=COLOR_NODE_PIVOT, stroke=BORDER_PIVOT, sw=2.5))
    p.append(text(cx_k, cy_k + 6, "k", size=17, color=INK, bold=True))
    p.append(text(cx_k, cy_k - r - 10, "Опорний міст (Pivot)", size=12, color=BORDER_PIVOT, bold=True))

    p.append(circle(cx_j, cy_j, r, fill=COLOR_NODE_DONE, stroke=BORDER_PRIMARY, sw=2.5))
    p.append(text(cx_j, cy_j + 6, "j", size=16, color=INK, bold=True))
    p.append(text(cx_j, cy_j + r + 18, "Цільовий вузол", size=11, color=MUTED))

    p.append(text(380, 275, "Правило Уоршелла: T[i][j] = T[i][j] ∨ (T[i][k] ∧ T[k][j])", size=13, color=INK, bold=True))

    render(path, W, H, *p)


# ── ФІГ. 3: Бітова векторизація рядка матриці T[i] |= T[k] ───────────────────
def fig_bitset_warshall_row():
    path = os.path.join(OUT, "bitset-warshall-row.svg")
    W, H = 780, 290
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=COLOR_BG_LIGHT, stroke="#cbd5e1", sw=1.0, rx=8))
    p.append(text(390, 36, "Поклітинний цикл vs Побітове АБО машинного слова (w = 64 біти)", size=15, color=INK, bold=True))

    p.append(text(80, 85, "Рядок T[i]:", size=13, color=INK, bold=True))
    bits_i = [0, 1, 0, 0, 1, 1, 0, 1]
    for b_idx, val in enumerate(bits_i):
        col = BORDER_PRIMARY if val == 1 else "#94a3b8"
        bg_c = COLOR_NODE_DONE if val == 1 else "#ffffff"
        x_pos = 170 + b_idx * 38
        p.append(rect(x_pos, 68, 34, 26, fill=bg_c, stroke=col, sw=1.5, rx=3))
        p.append(text(x_pos + 17, 85, str(val), size=13, color=col, bold=True))

    p.append(text(480, 85, "OR", size=13, color=BORDER_PIVOT, bold=True))

    p.append(text(80, 135, "Рядок T[k]:", size=13, color=BORDER_PIVOT, bold=True))
    bits_k = [1, 0, 0, 1, 0, 1, 0, 0]
    for b_idx, val in enumerate(bits_k):
        col = BORDER_PIVOT if val == 1 else "#94a3b8"
        bg_c = COLOR_NODE_PIVOT if val == 1 else "#ffffff"
        x_pos = 170 + b_idx * 38
        p.append(rect(x_pos, 118, 34, 26, fill=bg_c, stroke=col, sw=1.5, rx=3))
        p.append(text(x_pos + 17, 135, str(val), size=13, color=col, bold=True))

    p.append(line(150, 156, 480, 156, color="#64748b", sw=2.0))

    p.append(text(80, 190, "Результат:", size=13, color=BORDER_TRANS, bold=True))
    bits_res = [b1 | b2 for b1, b2 in zip(bits_i, bits_k)]
    for b_idx, val in enumerate(bits_res):
        is_new = (bits_i[b_idx] == 0 and val == 1)
        col = BORDER_TRANS if is_new else (BORDER_PRIMARY if val == 1 else "#94a3b8")
        bg_c = COLOR_NODE_TRANS if is_new else (COLOR_NODE_DONE if val == 1 else "#ffffff")
        x_pos = 170 + b_idx * 38
        p.append(rect(x_pos, 173, 34, 26, fill=bg_c, stroke=col, sw=2.0 if is_new else 1.5, rx=3))
        p.append(text(x_pos + 17, 190, str(val), size=13, color=col, bold=True))

    p.append(rect(515, 68, 240, 131, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=6))
    p.append(text(635, 92, "Прискорення векторизації", size=13, color=INK, bold=True))
    p.append(text(635, 116, "Замість 64 ітерацій inner-loop", size=11, color=MUTED))
    p.append(text(635, 136, "виконується 1 інструкція:", size=11, color=MUTED))
    p.append(text(635, 160, "T[i] |= T[k];  // uint64_t", size=12, color=BORDER_PRIMARY, bold=True))
    p.append(text(635, 182, "Складність: O(V³ / 64)", size=12, color=BORDER_TRANS, bold=True))

    p.append(text(390, 255, "При T[i][k] == 1 весь рядок T[i] оновлюється побітовим поєднанням із T[k] за паралельні 64 біти за такт", size=12, color=MUTED))

    render(path, W, H, *p)


# ── ФІГ. 4: Хронологія розвитку транзитивного замикання (для hist-вставки) ───
def fig_hist_warshall_timeline():
    path = os.path.join(OUT, "hist-warshall-timeline.svg")
    W, H = 800, 320
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=COLOR_BG_LIGHT, stroke="#cbd5e1", sw=1.0, rx=8))
    p.append(text(400, 38, "Еволюція алгоритмів досяжності та транзитивного замикання", size=15, color=INK, bold=True))

    axis_y = 160
    p.append(line(50, axis_y, 750, axis_y, color=BORDER_NORMAL, sw=2.5))
    p.append(arrow(740, axis_y, 755, axis_y, color=BORDER_NORMAL, sw=2.5))

    events = [
        (1959, 100, "Бернар Руа (Bernard Roy)", "Перша формалізація замикання у графах", True),
        (1962, 240, "Стівен Уоршелл (Warshall)", "Булевий O(V³) алгоритм досяжності", False),
        (1962, 380, "Роберт Флойд (Floyd)", "Узагальнення для найкоротших шляхів", True),
        (1970, 520, "Манро, Фішер і Майєр", "Зведення транзитивного замикання до BMM", False),
        (1975, 660, "Роберт Тар'ян (Tarjan)", "Конденсація SCC та алгоритми на DAG", True),
    ]

    for year, x_pos, author, desc, is_top in events:
        p.append(circle(x_pos, axis_y, 6, fill=COLOR_NODE_PIVOT, stroke=BORDER_PIVOT, sw=2.0))
        p.append(text(x_pos, axis_y + 20, str(year), size=12, color=INK, bold=True))

        box_y = axis_y - 75 if is_top else axis_y + 35
        line_y_end = axis_y - 12 if is_top else axis_y + 12

        p.append(line(x_pos, axis_y, x_pos, line_y_end, color=BORDER_PRIMARY, sw=1.5, dash="3 3"))

        p.append(rect(x_pos - 65, box_y, 130, 48, fill="#ffffff", stroke=BORDER_PRIMARY, sw=1.2, rx=4))
        p.append(text(x_pos, box_y + 18, author, size=10, color=BORDER_PRIMARY, bold=True))
        p.append(text(x_pos, box_y + 36, desc, size=9, color=MUTED))

    render(path, W, H, *p)


if __name__ == "__main__":
    fig_transitive_closure_concept()
    fig_warshall_pivot_step()
    fig_bitset_warshall_row()
    fig_hist_warshall_timeline()
    print("Всі фігури успішно згенеровано в ./img/")
