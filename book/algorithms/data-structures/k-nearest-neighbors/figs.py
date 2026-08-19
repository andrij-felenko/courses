# -*- coding: utf-8 -*-
"""Фігури до теми «Пошук найближчих сусідів (k-NN)»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def rnd(seed):
    """Детермінований генератор — щоб фігури не мінялися між запусками."""
    x = seed
    while True:
        x = (1103515245 * x + 12345) % (1 << 31)
        yield x / float(1 << 31)


def dot(x, y, r=3.0, color=INK):
    return circle(x, y, r, fill=color, stroke=color, sw=0.5)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def dashcircle(cx, cy, r, color=POS, sw=1.8, dash="5,4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, color, sw, dash))


# ── 1. Простір компромісів: Точний пошук проти ANN ─────────────────────────────
def fig_exact_vs_ann_tradeoff():
    W, H = 860, 480
    frags = []

    X0, Y0, GW, GH = 100, 380, 680, 280

    frags.append(line(X0, Y0, X0 + GW, Y0, color=LINE, sw=2.0))
    frags.append(line(X0, Y0, X0, Y0 - GH, color=LINE, sw=2.0))
    frags.append(arrow(X0 + GW, Y0, X0 + GW + 20, Y0, color=LINE, sw=2.0))
    frags.append(arrow(X0, Y0 - GH, X0, Y0 - GH - 20, color=LINE, sw=2.0))

    frags.append(text(X0 + GW + 30, Y0 + 5, "Затримка (мс) / Обчислення", size=13, color=INK, anchor="start", bold=True))
    frags.append(text(X0 - 15, Y0 - GH - 25, "Повнота (Recall@k)", size=13, color=INK, anchor="middle", bold=True))

    for pct, y_off in [(50, 0.5), (80, 0.8), (95, 0.95), (100, 1.0)]:
        y_pos = Y0 - y_off * (GH - 20)
        frags.append(line(X0 - 6, y_pos, X0, y_pos, color=MUTED, sw=1.2))
        frags.append(text(X0 - 12, y_pos + 4, "%d%%" % pct, size=11, color=MUTED, anchor="end"))
        frags.append(line(X0, y_pos, X0 + GW, y_pos, color="#e5e7eb", sw=1.0, dash="4,4"))

    ticks = [(120, "0.1 мс"), (280, "1 мс"), (460, "10 мс"), (640, "100 мс (Flat scan)")]
    for x_pos, lbl in ticks:
        frags.append(line(X0 + x_pos, Y0, X0 + x_pos, Y0 + 6, color=MUTED, sw=1.2))
        frags.append(text(X0 + x_pos, Y0 + 22, lbl, size=11, color=MUTED, anchor="middle"))

    px1, py1 = X0 + 640, Y0 - 1.0 * (GH - 20)
    frags.append(circle(px1, py1, 8, fill=POS, stroke=LINE, sw=1.5))
    frags.append(tb(px1, py1 - 36, "Повний перебір (Flat L2)\nRecall: 100% · O(N·d)\nПам'ять: 100% (raw float32)", size=11, fill="#fdedec", stroke=POS, bold=True))

    px2, py2 = X0 + 540, Y0 - 0.99 * (GH - 20)
    frags.append(circle(px2, py2, 7, fill=POS, stroke=LINE, sw=1.5))
    frags.append(tb(px2 - 60, py2 + 42, "kd-tree / Ball tree (d>30)\nКолапс до повного скану\nНакладні витрати на дерево", size=10, fill="#fdedec", stroke=POS))

    px3, py3 = X0 + 220, Y0 - 0.97 * (GH - 20)
    frags.append(circle(px3, py3, 8, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(tb(px3, py3 - 38, "HNSW (Графовий індекс)\nRecall: 95–99% · Затримка: 0.5–2 мс\nПам'ять: 120–180% (вектори + ребра)", size=11, fill="#e8f8f0", stroke=FIELD, bold=True))

    px4, py4 = X0 + 160, Y0 - 0.88 * (GH - 20)
    frags.append(circle(px4, py4, 8, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(tb(px4 - 20, py4 + 42, "IVF-PQ (Квантування)\nRecall: 85–95% · Затримка: 0.2–1 мс\nПам'ять: 3–10% (стиснення 16–32×)", size=11, fill="#e8effb", stroke=NEG, bold=True))

    px5, py5 = X0 + 340, Y0 - 0.78 * (GH - 20)
    frags.append(circle(px5, py5, 7, fill=MUTED, stroke=LINE, sw=1.5))
    frags.append(tb(px5 + 50, py5 + 38, "LSH (Хешування)\nRecall: 70–85%\nВелика кількість таблиць", size=10, fill=FILL, stroke=MUTED))

    frags.append('<path d="M %d %d Q %d %d %d %d T %d %d" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' %
                 (X0 + 100, Y0 - 0.75 * (GH - 20), X0 + 200, Y0 - 0.96 * (GH - 20), px3, py3, px1, py1, FIELD))

    render(os.path.join(OUT, 'exact-vs-ann-tradeoff.svg'), W, H, *frags,
           title="Компроміс між точністю (Recall) та швидкістю запиту для методів k-NN")


# ── 2. kd-дерево проти Ball tree: коробки проти куль ───────────────────────────
def fig_kd_vs_ball_tree():
    W, H = 940, 480
    frags = []

    X1, Y1, S1 = 40, 50, 380
    frags.append(rect(X1, Y1, S1, S1, fill="#fafbfc", stroke=LINE, sw=1.5))
    frags.append(text(X1 + S1 / 2, Y1 + 24, "kd-дерево: прямокутні коробки (AABB)", size=14, color=INK, anchor="middle", bold=True))

    x_split = X1 + 0.45 * S1
    y_split1 = Y1 + 0.58 * S1
    y_split2 = Y1 + 0.38 * S1

    frags.append(line(x_split, Y1 + 35, x_split, Y1 + S1, color=NEG, sw=2.2))
    frags.append(line(X1, y_split1, x_split, y_split1, color=FIELD, sw=1.8))
    frags.append(line(x_split, y_split2, X1 + S1, y_split2, color=FIELD, sw=1.8))

    g = rnd(42)
    pts_left = []
    for _ in range(25):
        px = X1 + 20 + next(g) * (S1 - 40)
        py = Y1 + 45 + next(g) * (S1 - 65)
        pts_left.append((px, py))
        frags.append(dot(px, py, r=3.0, color="#4b5563"))

    qx1, qy1 = X1 + 0.35 * S1, Y1 + 0.48 * S1
    r_nn1 = 65
    frags.append(circle(qx1, qy1, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(qx1 - 10, qy1 - 10, "q", size=13, color=POS, anchor="end", bold=True))
    frags.append(dashcircle(qx1, qy1, r_nn1, color=POS, sw=1.8))

    frags.append(line(qx1, qy1, x_split, qy1, color=POS, sw=1.8, dash="3,3"))
    frags.append(text((qx1 + x_split) / 2, qy1 - 8, "|q_x - s_x| < r_max", size=11, color=POS, anchor="middle"))
    frags.append(tb(X1 + S1 / 2, Y1 + S1 - 25, "Коло пошуку перетинає площину:\nвідсікання не спрацьовує, шукаємо в обох гілках", size=11, fill="#fff5f5", stroke=POS))

    X2, Y2, S2 = 520, 50, 380
    frags.append(rect(X2, Y2, S2, S2, fill="#fafbfc", stroke=LINE, sw=1.5))
    frags.append(text(X2 + S2 / 2, Y2 + 24, "Ball tree: метричні сферичні оболонки", size=14, color=INK, anchor="middle", bold=True))

    c1x, c1y, r1 = X2 + 0.30 * S2, Y2 + 0.65 * S2, 75
    c2x, c2y, r2 = X2 + 0.70 * S2, Y2 + 0.35 * S2, 85

    frags.append(circle(c1x, c1y, r1, fill="#e8f8f0", stroke=FIELD, sw=1.8))
    frags.append(circle(c2x, c2y, r2, fill="#e8effb", stroke=NEG, sw=1.8))

    frags.append(circle(c1x, c1y, 4, fill=FIELD, stroke=LINE, sw=1.2))
    frags.append(text(c1x + 8, c1y + 4, "C₁ (R₁)", size=11, color=FIELD, anchor="start", bold=True))
    frags.append(circle(c2x, c2y, 4, fill=NEG, stroke=LINE, sw=1.2))
    frags.append(text(c2x + 8, c2y + 4, "C₂ (R₂)", size=11, color=NEG, anchor="start", bold=True))

    g2 = rnd(101)
    for _ in range(12):
        rad = next(g2) * (r1 - 10)
        ang = next(g2) * 6.28
        frags.append(dot(c1x + rad * 0.9 * (1 if ang < 3.14 else -1), c1y + rad * 0.9 * (1 if ang > 1.57 and ang < 4.71 else -1), r=2.8, color="#1b4332"))

    for _ in range(14):
        rad = next(g2) * (r2 - 10)
        ang = next(g2) * 6.28
        frags.append(dot(c2x + rad * 0.9 * (1 if ang < 3.14 else -1), c2y + rad * 0.9 * (1 if ang > 1.57 and ang < 4.71 else -1), r=2.8, color="#1e3a8a"))

    qx2, qy2 = X2 + 0.28 * S2, Y2 + 0.30 * S2
    r_nn2 = 50
    frags.append(circle(qx2, qy2, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(qx2 - 10, qy2 - 10, "q", size=13, color=POS, anchor="end", bold=True))
    frags.append(dashcircle(qx2, qy2, r_nn2, color=POS, sw=1.8))

    frags.append(line(qx2, qy2, c2x, c2y, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(text((qx2 + c2x) / 2 + 5, (qy2 + c2y) / 2 - 8, "d(q, C₂)", size=11, color=MUTED, anchor="start"))

    frags.append(tb(X2 + S2 / 2, Y2 + S2 - 25, "Нерівність трикутника: d(q, C₂) - R₂ > r_max\nГілка C₂ гарантовано відсікається цілком!", size=11, fill="#e8f8f0", stroke=FIELD, bold=True))

    render(os.path.join(OUT, 'kd-vs-ball-tree.svg'), W, H, *frags,
           title="Геометрія просторового розбиття: прямокутники kd-дерева проти сферичних оболонок Ball tree")


# ── 3. Прокляття розмірності: геометрія колапсу ────────────────────────────────
def fig_curse_geometry():
    W, H = 920, 460
    frags = []

    X1, Y1, S = 50, 60, 240
    frags.append(rect(X1, Y1, S, S, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(circle(X1 + S / 2, Y1 + S / 2, S / 2, fill="#e8effb", stroke=NEG, sw=1.8))
    frags.append(text(X1 + S / 2, Y1 + 24, "2D: Площина", size=14, color=INK, anchor="middle", bold=True))
    frags.append(tb(X1 + S / 2, Y1 + S / 2, "V_сфери / V_куба\n= π / 4 ≈ 78.5%", size=12, fill="#ffffff", stroke=NEG))
    frags.append(tb(X1 + S / 2, Y1 + S - 20, "Кути займають 21.5% об'єму", size=10, fill=FILL, stroke=MUTED))

    X2 = X1 + S + 60
    frags.append(rect(X2, Y2 := Y1, S, S, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(circle(X2 + S / 2, Y2 + S / 2, S / 2, fill="#e8f8f0", stroke=FIELD, sw=1.8))
    frags.append(text(X2 + S / 2, Y2 + 24, "3D: Простір", size=14, color=INK, anchor="middle", bold=True))
    frags.append(tb(X2 + S / 2, Y2 + S / 2, "V_сфери / V_куба\n= π / 6 ≈ 52.4%", size=12, fill="#ffffff", stroke=FIELD))
    frags.append(tb(X2 + S / 2, Y2 + S - 20, "Кути займають 47.6% об'єму", size=10, fill=FILL, stroke=MUTED))

    X3 = X2 + S + 60
    frags.append(rect(X3, Y3 := Y1, S, S, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(circle(X3 + S / 2, Y3 + S / 2, 22, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(X3 + S / 2, Y3 + 24, "d = 100: Гіперпростір", size=14, color=INK, anchor="middle", bold=True))
    frags.append(tb(X3 + S / 2, Y3 + S / 2 + 50, "V_сфери / V_куба\n≈ 1.86 · 10⁻⁷⁰ → 0\nКути займають ~100%", size=11, fill="#ffffff", stroke=POS, bold=True))
    frags.append(tb(X3 + S / 2, Y3 + S - 20, "Вся маса — у тонкій оболонці", size=10, fill=FILL, stroke=MUTED))

    frags.append(tb(W / 2, 390, "Концентрація відстаней (Beyer et al.):\nlim_{d → ∞} (d_max - d_min) / d_min = 0\nУсі точки стають однаково віддаленими від запиту — радіус пошуку накриває весь простір, відсікання падає до 0%.",
                    size=12, fill="#fdedec", stroke=POS, bold=True))

    render(os.path.join(OUT, 'curse-geometry.svg'), W, H, *frags,
           title="Прокляття розмірності: зникнення об'єму вписаної сфери та концентрація міжточкових відстаней")


# ── 4. Граф HNSW: ієрархія малих світів ─────────────────────────────────────────
def fig_ann_hnsw_graph():
    W, H = 940, 540
    frags = []

    layers = [
        ("Шар 2 (Розріджений: експрес-магістралі, ef=1)", 95, 4, NEG),
        ("Шар 1 (Середня щільність, швидке наближення)", 235, 8, FIELD),
        ("Шар 0 (Повний граф усіх точок бази даних, efSearch)", 375, 16, INK)
    ]

    g = rnd(777)
    l0_pts = []
    base_x, base_y = 120, 395
    for i in range(14):
        px = base_x + i * 52 + (next(g) - 0.5) * 30
        py = base_y + (next(g) - 0.5) * 50
        l0_pts.append((px, py))

    l1_indices = [0, 2, 5, 8, 11, 13]
    l1_pts = [(l0_pts[i][0], 245 + (l0_pts[i][1] - base_y) * 0.6) for i in l1_indices]

    l2_indices = [0, 5, 13]
    l2_pts = [(l0_pts[i][0], 105 + (l0_pts[i][1] - base_y) * 0.4) for i in l2_indices]

    for title, y_top, count, col in layers:
        frags.append(rect(60, y_top - 45, 820, 110, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=6))
        frags.append(text(75, y_top - 26, title, size=12, color=col, anchor="start", bold=True))

    for i in range(len(l2_pts) - 1):
        frags.append(line(l2_pts[i][0], l2_pts[i][1], l2_pts[i+1][0], l2_pts[i+1][1], color=NEG, sw=2.5))

    for i in range(len(l1_pts) - 1):
        frags.append(line(l1_pts[i][0], l1_pts[i][1], l1_pts[i+1][0], l1_pts[i+1][1], color=FIELD, sw=1.8))
        if i + 2 < len(l1_pts):
            frags.append(line(l1_pts[i][0], l1_pts[i][1], l1_pts[i+2][0], l1_pts[i+2][1], color=FIELD, sw=1.2, dash="4,3"))

    for i in range(len(l0_pts) - 1):
        frags.append(line(l0_pts[i][0], l0_pts[i][1], l0_pts[i+1][0], l0_pts[i+1][1], color=LINE, sw=1.4))
        if i + 2 < len(l0_pts):
            frags.append(line(l0_pts[i][0], l0_pts[i][1], l0_pts[i+2][0], l0_pts[i+2][1], color=MUTED, sw=1.0))
        if i + 3 < len(l0_pts):
            frags.append(line(l0_pts[i][0], l0_pts[i][1], l0_pts[i+3][0], l0_pts[i+3][1], color="#9ca3af", sw=0.8, dash="3,3"))

    for p in l0_pts:
        frags.append(circle(p[0], p[1], 4, fill="#ffffff", stroke=INK, sw=1.5))
    for p in l1_pts:
        frags.append(circle(p[0], p[1], 5, fill="#e8f8f0", stroke=FIELD, sw=1.8))
    for p in l2_pts:
        frags.append(circle(p[0], p[1], 6, fill="#e8effb", stroke=NEG, sw=2.2))

    ep_x, ep_y = l2_pts[0][0], l2_pts[0][1]
    frags.append(tb(ep_x + 90, ep_y - 12, "Точка входу (Entry Point)", size=10, fill="#e8effb", stroke=NEG, bold=True))

    target_x, target_y = l0_pts[11][0] + 15, l0_pts[11][1] - 5
    frags.append(circle(target_x, target_y, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(target_x + 12, target_y + 4, "Запит q", size=12, color=POS, anchor="start", bold=True))

    frags.append(arrow(ep_x, ep_y, l2_pts[1][0], l2_pts[1][1], color=POS, sw=2.2))
    frags.append(arrow(l2_pts[1][0], l2_pts[1][1], l1_pts[2][0], l1_pts[2][1], color=POS, sw=2.0))
    frags.append(arrow(l1_pts[2][0], l1_pts[2][1], l1_pts[4][0], l1_pts[4][1], color=POS, sw=2.2))
    frags.append(arrow(l1_pts[4][0], l1_pts[4][1], l0_pts[11][0], l0_pts[11][1], color=POS, sw=2.0))
    frags.append(arrow(l0_pts[11][0], l0_pts[11][1], target_x, target_y, color=POS, sw=2.2))

    frags.append(tb(W / 2, 495, "Ієрархія Skip-list для графів: на верхніх шарах жадібний рух долає великі відстані за O(1) кроків,\nна шарі 0 beam search знаходить точних k сусідів у вузькому околі за сумарний час O(log N).",
                    size=11, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, 'ann-hnsw-graph.svg'), W, H, *frags,
           title="Ієрархічний малий світ (HNSW): багаторівневий графовий індекс для швидкого пошуку")


# ── 5. IVF-PQ: Інвертований індекс + Продуктове квантування ────────────────────
def fig_ann_ivf_pq():
    W, H = 960, 540
    frags = []

    X1, Y1, SW, SH = 50, 50, 380, 430
    frags.append(rect(X1, Y1, SW, SH, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(X1 + SW / 2, Y1 + 25, "1. IVF (Інвертований файл)", size=14, color=INK, anchor="middle", bold=True))

    c_pts = [
        (X1 + 90, Y1 + 100, "C₁"),
        (X1 + 260, Y1 + 90, "C₂"),
        (X1 + 140, Y1 + 240, "C₃"),
        (X1 + 290, Y1 + 230, "C₄"),
        (X1 + 190, Y1 + 340, "C₅")
    ]
    for cx, cy, lbl in c_pts:
        frags.append(circle(cx, cy, 7, fill=FIELD, stroke=LINE, sw=1.5))
        frags.append(text(cx + 12, cy + 4, lbl, size=12, color=FIELD, anchor="start", bold=True))

    frags.append(line(X1 + 180, Y1 + 40, X1 + 170, Y1 + 170, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(X1 + 170, Y1 + 170, X1 + 370, Y1 + 160, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(X1 + 170, Y1 + 170, X1 + 70, Y1 + 380, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(X1 + 170, Y1 + 170, X1 + 230, Y1 + 290, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(X1 + 230, Y1 + 290, X1 + 370, Y1 + 310, color=MUTED, sw=1.0, dash="4,4"))

    qx, qy = X1 + 230, Y1 + 140
    frags.append(circle(qx, qy, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(qx - 10, qy - 8, "q", size=13, color=POS, anchor="end", bold=True))

    frags.append(arrow(qx, qy, X1 + 260, Y1 + 90, color=POS, sw=1.6))
    frags.append(arrow(qx, qy, X1 + 290, Y1 + 230, color=POS, sw=1.6))

    frags.append(tb(X1 + SW / 2, Y1 + SH - 36, "Знаходимо nprobe=2 найближчі центроїди (C₂, C₄).\nСкануємо лише їхні інвертовані списки (відсікаємо 60–95% бази).",
                    size=10, fill="#e8f8f0", stroke=FIELD))

    X2 = 470
    frags.append(rect(X2, Y1, SW + 40, SH, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(X2 + (SW + 40) / 2, Y1 + 25, "2. Продуктове квантування (PQ + ADC)", size=14, color=INK, anchor="middle", bold=True))

    frags.append(text(X2 + 20, Y1 + 60, "Вектор 768 float32 (3072 байти) ділиться на M=8 підпросторів:", size=11, color=INK, anchor="start"))

    sub_w = 46
    for m in range(8):
        sx = X2 + 24 + m * sub_w
        frags.append(rect(sx, Y1 + 75, sub_w - 4, 30, fill="#e8effb", stroke=NEG, sw=1.2, rx=3))
        frags.append(text(sx + (sub_w - 4) / 2, Y1 + 95, "v%d" % (m + 1), size=11, color=NEG, anchor="middle", bold=True))

    frags.append(arrow(X2 + 210, Y1 + 115, X2 + 210, Y1 + 145, color=LINE, sw=1.8))
    frags.append(text(X2 + 225, Y1 + 135, "Кожен v_m квантується у k*=256 центроїдів (1 байт)", size=10, color=MUTED, anchor="start"))

    frags.append(text(X2 + 20, Y1 + 165, "Стиснений код у пам'яті: 8 байтів (стиснення 384×!):", size=11, color=INK, anchor="start", bold=True))
    bytes_demo = [14, 203, 5, 88, 12, 199, 42, 73]
    for m, bval in enumerate(bytes_demo):
        sx = X2 + 24 + m * sub_w
        frags.append(rect(sx, Y1 + 180, sub_w - 4, 28, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=3))
        frags.append(text(sx + (sub_w - 4) / 2, Y1 + 198, "%d" % bval, size=11, color=FIELD, anchor="middle", bold=True))

    frags.append(text(X2 + 20, Y1 + 235, "Асиметричне обчислення відстані (ADC):", size=12, color=INK, anchor="start", bold=True))
    frags.append(tb(X2 + (SW + 40) / 2, Y1 + 300,
                    "Попередньо рахуємо таблицю: DistTable[m][k] = ||q_m - Centroid_m,k||²\n"
                    "Для кожного вектора бази: Dist(q, x) = ∑ DistTable[m][x_code[m]]\n"
                    "Замість 768 множень float32 — рівно 8 читань із таблиці та 8 доданків!",
                    size=10, fill="#ffffff", stroke=LINE))

    frags.append(tb(X2 + (SW + 40) / 2, Y1 + SH - 36, "Швидкість: мільйони векторів/с на 1 ядрі CPU\nзавдяки векторним інструкціям SIMD (AVX2/AVX-512).",
                    size=10, fill="#e8effb", stroke=NEG, bold=True))

    render(os.path.join(OUT, 'ann-ivf-pq.svg'), W, H, *frags,
           title="Архітектура IVF-PQ: грубе відсікання списків та швидке сканування квантованих кодів через таблиці ADC")


if __name__ == '__main__':
    fig_exact_vs_ann_tradeoff()
    fig_kd_vs_ball_tree()
    fig_curse_geometry()
    fig_ann_hnsw_graph()
    fig_ann_ivf_pq()
    print('All figures generated successfully.')
