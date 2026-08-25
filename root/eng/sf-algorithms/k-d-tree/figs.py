# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_kd_tree_space_partition():
    W, H = 1040, 540
    p = []

    p.append(text(W / 2, 28, "Двовимірне розбиття площини та структура K-d дерева", size=16, bold=True))
    p.append(text(W / 2, 50, "Чергування осей розбиття (X на парних рівнях, Y на непарних) розсікає простір на прямокутні комірки", size=12, color=MUTED))

    # Left panel: 2D plane coordinate system
    plane_x, plane_y = 40, 80
    plane_w, plane_h = 390, 390

    p.append(rect(plane_x, plane_y, plane_w, plane_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=4))

    # Grid background lines
    for i in range(1, 5):
        gx = plane_x + i * (plane_w / 5.0)
        gy = plane_y + i * (plane_h / 5.0)
        p.append(line(gx, plane_y, gx, plane_y + plane_h, color="#edf2f7", sw=1.0, dash="3,3"))
        p.append(line(plane_x, gy, plane_x + plane_w, gy, color="#edf2f7", sw=1.0, dash="3,3"))

    # Coordinate axes markers
    p.append(text(plane_x + 18, plane_y + plane_h - 12, "(0, 0)", size=11, color=MUTED, anchor="start"))
    p.append(text(plane_x + plane_w - 18, plane_y + plane_h - 12, "X (100)", size=11, bold=True, color=POS, anchor="end"))
    p.append(text(plane_x + 18, plane_y + 22, "Y (100)", size=11, bold=True, color=NEG, anchor="start"))

    # Scale mapping: [0, 100] -> [plane_x, plane_x + plane_w], Y inverted
    def sx(val): return plane_x + (val / 100.0) * plane_w
    def sy(val): return plane_y + plane_h - (val / 100.0) * plane_h

    # Root split: P1(50, 45), split along X = 50 (Vertical line, Red)
    p.append(line(sx(50), sy(0), sx(50), sy(100), color=POS, sw=2.5))
    p.append(text(sx(50) + 6, sy(96), "X = 50", size=10, bold=True, color=POS, anchor="start"))

    # Left subtree Y-splits: P2(25, 65), split along Y = 65 for X in [0, 50] (Horizontal line, Blue)
    p.append(line(sx(0), sy(65), sx(50), sy(65), color=NEG, sw=2.2))
    p.append(text(sx(6), sy(65) - 6, "Y = 65", size=10, bold=True, color=NEG, anchor="start"))

    # Right subtree Y-splits: P3(75, 25), split along Y = 25 for X in [50, 100] (Horizontal line, Blue)
    p.append(line(sx(50), sy(25), sx(100), sy(25), color=NEG, sw=2.2))
    p.append(text(sx(94), sy(25) - 6, "Y = 25", size=10, bold=True, color=NEG, anchor="end"))

    # Leaves X-splits:
    # P4(12, 30) in [0, 50] x [0, 65] -> split along X = 12 from Y=0 to Y=65
    p.append(line(sx(12), sy(0), sx(12), sy(65), color=POS, sw=1.5, dash="4,3"))
    p.append(text(sx(12) + 4, sy(6), "X=12", size=9.5, bold=True, color=POS, anchor="start"))

    # P5(38, 85) in [0, 50] x [65, 100] -> split along X = 38 from Y=65 to Y=100
    p.append(line(sx(38), sy(65), sx(38), sy(100), color=POS, sw=1.5, dash="4,3"))
    p.append(text(sx(38) + 4, sy(96), "X=38", size=9.5, bold=True, color=POS, anchor="start"))

    # P6(62, 75) in [50, 100] x [25, 100] -> split along X = 62 from Y=25 to Y=100
    p.append(line(sx(62), sy(25), sx(62), sy(100), color=POS, sw=1.5, dash="4,3"))
    p.append(text(sx(62) + 4, sy(96), "X=62", size=9.5, bold=True, color=POS, anchor="start"))

    # P7(88, 12) in [50, 100] x [0, 25] -> split along X = 88 from Y=0 to Y=25
    p.append(line(sx(88), sy(0), sx(88), sy(25), color=POS, sw=1.5, dash="4,3"))
    p.append(text(sx(88) - 4, sy(6), "X=88", size=9.5, bold=True, color=POS, anchor="end"))

    # Draw Points with coordinates
    pts = [
        ("P1 (50, 45)", 50, 45, 0, -14),
        ("P2 (25, 65)", 25, 65, 0, -14),
        ("P3 (75, 25)", 75, 25, 0, -14),
        ("P4 (12, 30)", 12, 30, 26, 12),
        ("P5 (38, 85)", 38, 85, -26, 12),
        ("P6 (62, 75)", 62, 75, 26, -12),
        ("P7 (88, 12)", 88, 12, -26, 14),
    ]
    for lbl, px, py, ox, oy in pts:
        p.append(circle(sx(px), sy(py), 4.5, fill=INK, stroke=BG, sw=1.5))
        p.append(text(sx(px) + ox, sy(py) + oy, lbl, size=10, bold=True, color=INK, anchor="middle"))

    p.append(text(plane_x + plane_w / 2, plane_y + plane_h + 30, "Геометричний простір: почерговий поділ площини", size=12, bold=True, color=INK))

    # Right panel: Tree hierarchy graph
    tree_x, tree_y = 470, 80
    tree_w, tree_h = 530, 390
    p.append(rect(tree_x, tree_y, tree_w, tree_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))

    p.append(text(tree_x + tree_w / 2, tree_y + 25, "Ієрархічне бінарне дерево", size=14, bold=True, color=INK))

    # Levels: L0 (depth 0, split X), L1 (depth 1, split Y), L2 (depth 2, split X)
    n_r  = (tree_x + 265, tree_y + 70)
    n_l1 = (tree_x + 135, tree_y + 160)
    n_r1 = (tree_x + 395, tree_y + 160)
    n_l2_0 = (tree_x + 70,  tree_y + 265)
    n_l2_1 = (tree_x + 200, tree_y + 265)
    n_l2_2 = (tree_x + 330, tree_y + 265)
    n_l2_3 = (tree_x + 460, tree_y + 265)

    tree_edges = [
        (n_r, n_l1, "X ≤ 50"), (n_r, n_r1, "X > 50"),
        (n_l1, n_l2_0, "Y ≤ 65"), (n_l1, n_l2_1, "Y > 65"),
        (n_r1, n_l2_2, "Y > 25"), (n_r1, n_l2_3, "Y ≤ 25"),
    ]

    for (x1, y1), (x2, y2), elbl in tree_edges:
        p.append(line(x1, y1 + 18, x2, y2 - 18, color=LINE, sw=1.4))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        p.append(text(mx, my - 5, elbl, size=9.5, color=MUTED, bold=True))

    def tree_node(pos, name, pt_str, split_str, fill_col, border_col):
        nx, ny = pos
        p.append(rect(nx - 48, ny - 18, 96, 36, fill=fill_col, stroke=border_col, sw=1.5, rx=5))
        p.append(text(nx, ny - 4, f"{name}: {pt_str}", size=10, bold=True, color=INK))
        p.append(text(nx, ny + 11, split_str, size=9.5, color=border_col, bold=True))

    tree_node(n_r, "P1", "(50, 45)", "Розбиття X=50", "#fee2e2", POS)
    tree_node(n_l1, "P2", "(25, 65)", "Розбиття Y=65", "#dbeafe", NEG)
    tree_node(n_r1, "P3", "(75, 25)", "Розбиття Y=25", "#dbeafe", NEG)

    tree_node(n_l2_0, "P4", "(12, 30)", "Розбиття X=12", "#fee2e2", POS)
    tree_node(n_l2_1, "P5", "(38, 85)", "Розбиття X=38", "#fee2e2", POS)
    tree_node(n_l2_2, "P6", "(62, 75)", "Розбиття X=62", "#fee2e2", POS)
    tree_node(n_l2_3, "P7", "(88, 12)", "Розбиття X=88", "#fee2e2", POS)

    # Legend / explanation at bottom of tree
    p.append(rect(tree_x + 40, tree_y + tree_h - 55, tree_w - 80, 40, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
    p.append(circle(tree_x + 70, tree_y + tree_h - 35, 5, fill=POS, stroke=LINE, sw=1))
    p.append(text(tree_x + 85, tree_y + tree_h - 31, "Вертикальний спліт (X)", size=10.5, anchor="start", color=INK))
    p.append(circle(tree_x + 280, tree_y + tree_h - 35, 5, fill=NEG, stroke=LINE, sw=1))
    p.append(text(tree_x + 295, tree_y + tree_h - 31, "Горизонтальний спліт (Y)", size=10.5, anchor="start", color=INK))

    render(os.path.join(OUT, "fig-kd-tree-space-partition.svg"), W, H, *p)


def fig_kd_tree_nns_pruning():
    W, H = 980, 480
    p = []

    p.append(text(W / 2, 28, "Геометричне відсікання гілок (Pruning) під час пошуку найближчого сусіда", size=16, bold=True))
    p.append(text(W / 2, 50, "Якщо відстань до розділової площини більша за поточний радіус кандидата, усе протилежне піддерево ігнорується", size=12, color=MUTED))

    # Panel A: Subtree is pruned (D_plane >= R_best)
    pa_x, pa_y, pa_w, pa_h = 40, 75, 430, 370
    p.append(rect(pa_x, pa_y, pa_w, pa_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(pa_x + pa_w / 2, pa_y + 25, "Випадок 1: Відсікання гілки (D_площини ≥ R)", size=13.5, bold=True, color=FIELD))

    # Coordinate sub-box
    box_a_x, box_a_y = pa_x + 25, pa_y + 45
    box_a_w, box_a_h = 380, 250
    p.append(rect(box_a_x, box_a_y, box_a_w, box_a_h, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))

    # Split line at X = 240
    split_ax = box_a_x + 210
    p.append(rect(split_ax, box_a_y, box_a_w - (split_ax - box_a_x), box_a_h, fill="#fef2f2", stroke="none"))
    p.append(line(split_ax, box_a_y, split_ax, box_a_y + box_a_h, color=POS, sw=2.0))
    p.append(text(split_ax + 8, box_a_y + 20, "Площина X = X_split", size=10.5, bold=True, color=POS, anchor="start"))

    # Query Q and candidate P_best in Left Zone
    qx_a, qy_a = box_a_x + 85, box_a_y + 125
    px_a, py_a = box_a_x + 125, box_a_y + 155
    r_a = 50.0

    p.append(circle(qx_a, qy_a, r_a, fill="#eff6ff", stroke=NEG, sw=1.5))
    p.append(circle(qx_a, qy_a, 4.5, fill=NEG, stroke=BG, sw=1.5))
    p.append(text(qx_a - 15, qy_a - 15, "Запит Q", size=11, bold=True, color=NEG))

    p.append(circle(px_a, py_a, 4.5, fill=FIELD, stroke=BG, sw=1.5))
    p.append(text(px_a + 12, py_a + 16, "P_best", size=11, bold=True, color=FIELD))

    p.append(line(qx_a, qy_a, px_a, py_a, color=FIELD, sw=1.5, dash="3,2"))
    p.append(text((qx_a + px_a) / 2 + 14, (qy_a + py_a) / 2 - 8, "R_best", size=10, bold=True, color=FIELD))

    p.append(line(qx_a, qy_a, split_ax, qy_a, color=POS, sw=1.5, dash="4,3"))
    p.append(text(qx_a + (split_ax - qx_a) / 2, qy_a - 10, "D_площини", size=10, bold=True, color=POS))

    # Cross mark on pruned side
    p.append(rect(split_ax + 20, box_a_y + 80, 120, 75, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(split_ax + 80, box_a_y + 105, "ПІДДЕРЕВО", size=11, bold=True, color=POS))
    p.append(text(split_ax + 80, box_a_y + 125, "ВІДСІЧЕНО ✗", size=11.5, bold=True, color=POS))
    p.append(text(split_ax + 80, box_a_y + 145, "(0 перевірок)", size=10, color=MUTED))

    p.append(text(pa_x + pa_w / 2, pa_y + pa_h - 20, "D_площини > R_best  ⇒  Сфера не перетинає площину", size=11, bold=True, color=FIELD))

    # Panel B: Subtree must be explored (D_plane < R_best)
    pb_x, pb_y, pb_w, pb_h = 510, 75, 430, 370
    p.append(rect(pb_x, pb_y, pb_w, pb_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(pb_x + pb_w / 2, pa_y + 25, "Випадок 2: Перетин площини (D_площини < R)", size=13.5, bold=True, color="#d97706"))

    box_b_x, box_b_y = pb_x + 25, pb_y + 45
    box_b_w, box_b_h = 380, 250
    p.append(rect(box_b_x, box_b_y, box_b_w, box_b_h, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))

    split_bx = box_b_x + 170
    p.append(rect(split_bx, box_b_y, box_b_w - (split_bx - box_b_x), box_b_h, fill="#fefce8", stroke="none"))
    p.append(line(split_bx, box_b_y, split_bx, box_b_y + box_b_h, color=POS, sw=2.0))
    p.append(text(split_bx + 8, box_b_y + 20, "Площина X = X_split", size=10.5, bold=True, color=POS, anchor="start"))

    qx_b, qy_b = box_b_x + 130, box_b_y + 125
    px_b, py_b = box_b_x + 85, box_b_y + 160
    r_b = 65.0

    p.append(circle(qx_b, qy_b, r_b, fill="#fef9c3", stroke="#ca8a04", sw=1.5))
    p.append(circle(qx_b, qy_b, 4.5, fill=NEG, stroke=BG, sw=1.5))
    p.append(text(qx_b - 15, qy_b - 15, "Запит Q", size=11, bold=True, color=NEG))

    p.append(circle(px_b, py_b, 4.5, fill=FIELD, stroke=BG, sw=1.5))
    p.append(text(px_b - 12, py_b + 18, "P_best", size=11, bold=True, color=FIELD))

    p.append(line(qx_b, qy_b, px_b, py_b, color=FIELD, sw=1.5, dash="3,2"))
    p.append(text((qx_b + px_b) / 2 - 14, (qy_b + py_b) / 2 + 14, "R_best", size=10, bold=True, color=FIELD))

    p.append(line(qx_b, qy_b, split_bx, qy_b, color=POS, sw=1.5, dash="4,3"))
    p.append(text(qx_b + (split_bx - qx_b) / 2, qy_b - 10, "D_пл.", size=10, bold=True, color=POS))

    # Check mark on explored side
    p.append(rect(split_bx + 20, box_b_y + 80, 135, 75, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=4))
    p.append(text(split_bx + 87, box_b_y + 105, "ПІДДЕРЕВО", size=11, bold=True, color="#854d0e"))
    p.append(text(split_bx + 87, box_b_y + 125, "РОЗГОРТАЄТЬСЯ ✓", size=11.5, bold=True, color="#854d0e"))
    p.append(text(split_bx + 87, box_b_y + 145, "(можливий ближчий)", size=9.5, color=MUTED))

    p.append(text(pb_x + pb_w / 2, pb_y + pb_h - 20, "D_площини < R_best  ⇒  Сфера перетинає підпростір", size=11, bold=True, color="#d97706"))

    render(os.path.join(OUT, "fig-kd-tree-nns-pruning.svg"), W, H, *p)


def fig_kd_tree_curse_dimensionality():
    W, H = 1000, 500
    p = []

    p.append(text(W / 2, 28, "Прокляття вимірності: колапс об'єму вписаної гіперсфери", size=16, bold=True))
    p.append(text(W / 2, 50, "З ростом розмірності k об'єм сфери у кубі спадає до нуля — простір концентрується у кутах куба", size=12, color=MUTED))

    col_w = 280
    col_h = 380
    y_top = 80

    # Col 1: 2D
    c1_x = 40
    p.append(rect(c1_x, y_top, col_w, col_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    p.append(text(c1_x + col_w / 2, y_top + 25, "2D Простір (Площина)", size=14, bold=True, color=INK))
    p.append(text(c1_x + col_w / 2, y_top + 45, "Коло вписане у квадрат", size=11.5, color=MUTED))

    box2_s = 140
    box2_x = c1_x + (col_w - box2_s) / 2
    box2_y = y_top + 65
    p.append(rect(box2_x, box2_y, box2_s, box2_s, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    p.append(circle(box2_x + box2_s / 2, box2_y + box2_s / 2, box2_s / 2, fill="#dbeafe", stroke=NEG, sw=1.5))

    p.append(text(c1_x + col_w / 2, y_top + 235, "Частка об'єму сфери:", size=11, color=MUTED))
    p.append(text(c1_x + col_w / 2, y_top + 260, "V_сфери / V_куба = π / 4", size=13, bold=True, color=NEG))
    p.append(text(c1_x + col_w / 2, y_top + 290, "≈ 78.54%", size=16, bold=True, color=FIELD))
    p.append(text(c1_x + col_w / 2, y_top + 335, "K-d дерево ефективне", size=11, color=FIELD, bold=True))

    # Col 2: 3D
    c2_x = 360
    p.append(rect(c2_x, y_top, col_w, col_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    p.append(text(c2_x + col_w / 2, y_top + 25, "3D Простір (Об'єм)", size=14, bold=True, color=INK))
    p.append(text(c2_x + col_w / 2, y_top + 45, "Сфера вписана в куб", size=11.5, color=MUTED))

    box3_x = c2_x + (col_w - box2_s) / 2
    box3_y = y_top + 65
    p.append(rect(box3_x, box3_y + 15, box2_s - 20, box2_s - 20, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(circle(box3_x + (box2_s - 20) / 2, box3_y + 15 + (box2_s - 20) / 2, (box2_s - 20) / 2, fill="#dbeafe", stroke=NEG, sw=1.5))

    p.append(text(c2_x + col_w / 2, y_top + 235, "Частка об'єму сфери:", size=11, color=MUTED))
    p.append(text(c2_x + col_w / 2, y_top + 260, "V_сфери / V_куба = π / 6", size=13, bold=True, color=NEG))
    p.append(text(c2_x + col_w / 2, y_top + 290, "≈ 52.36%", size=16, bold=True, color="#d97706"))
    p.append(text(c2_x + col_w / 2, y_top + 335, "Швидкий пошук (графіка)", size=11, color=INK))

    # Col 3: High-D (k >= 15-20)
    c3_x = 680
    p.append(rect(c3_x, y_top, col_w, col_h, fill="#fff7ed", stroke=POS, sw=1.5, rx=6))
    p.append(text(c3_x + col_w / 2, y_top + 25, "Висока вимірність (k ≥ 15)", size=14, bold=True, color=POS))
    p.append(text(c3_x + col_w / 2, y_top + 45, "Гіперсфера у гіперкубі", size=11.5, color=MUTED))

    box10_x = c3_x + (col_w - box2_s) / 2
    box10_y = y_top + 65
    p.append(rect(box10_x, box10_y, box2_s, box2_s, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(circle(box10_x + box2_s / 2, box10_y + box2_s / 2, 9, fill=NEG, stroke=LINE, sw=1.0))
    p.append(text(box10_x + box2_s / 2, box10_y + box2_s / 2 + 26, "V_сфери ≈ 0", size=10, bold=True, color=NEG))
    p.append(text(box10_x + 10, box10_y + 18, "Кути куба: 99.99% об'єму", size=9.5, color=POS, bold=True, anchor="start"))

    p.append(text(c3_x + col_w / 2, y_top + 235, "Частка об'єму сфери (k = 20):", size=11, color=MUTED))
    p.append(text(c3_x + col_w / 2, y_top + 260, "V_сфери / V_куба", size=13, bold=True, color=NEG))
    p.append(text(c3_x + col_w / 2, y_top + 290, "≈ 2.46 · 10⁻⁸", size=16, bold=True, color=POS))
    p.append(text(c3_x + col_w / 2, y_top + 335, "Деградація до O(N) — повний обхід", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "fig-kd-tree-curse-dimensionality.svg"), W, H, *p)


def fig_kd_tree_range_search():
    W, H = 980, 480
    p = []

    p.append(text(W / 2, 28, "Ортогональний діапазонний пошук та перетин паралелепіпедів", size=16, bold=True))
    p.append(text(W / 2, 50, "Три стани вузла: повне входження піддерева, частковий перетин межі або повна неперетинність", size=12, color=MUTED))

    # Left: 2D plane with query window
    p_x, p_y = 40, 75
    p_w, p_h = 430, 370
    p.append(rect(p_x, p_y, p_w, p_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))

    # Tree cell divisions
    def rx(v): return p_x + (v / 100.0) * p_w
    def ry(v): return p_y + p_h - (v / 100.0) * p_h

    # X=50
    p.append(line(rx(50), ry(0), rx(50), ry(100), color=POS, sw=2.0))
    # Y=50 in left
    p.append(line(rx(0), ry(50), rx(50), ry(50), color=NEG, sw=1.5))
    # Y=50 in right
    p.append(line(rx(50), ry(50), rx(100), ry(50), color=NEG, sw=1.5))

    # Query bounding box [20, 70] x [25, 75]
    qx1, qy1 = rx(20), ry(75)
    qw, qh = rx(70) - rx(20), ry(25) - ry(75)
    p.append(rect(qx1, qy1, qw, qh, fill="#fef3c7", stroke="#d97706", sw=2.5, rx=4))
    p.append(text(qx1 + 10, qy1 + 20, "Вікно запиту [X_min, X_max] × [Y_min, Y_max]", size=11, bold=True, color="#92400e", anchor="start"))

    # Points
    inside_pts = [(30, 40), (45, 60), (60, 65)]
    outside_pts = [(10, 15), (15, 85), (85, 20), (90, 80)]

    for px, py in inside_pts:
        p.append(circle(rx(px), ry(py), 5, fill=FIELD, stroke=LINE, sw=1.5))
        p.append(text(rx(px) + 8, ry(py) - 8, f"({px},{py}) ∈ W", size=9.5, bold=True, color=FIELD, anchor="start"))

    for px, py in outside_pts:
        p.append(circle(rx(px), ry(py), 4, fill=MUTED, stroke=LINE, sw=1.0))
        p.append(text(rx(px) + 8, ry(py) - 6, f"({px},{py})", size=9.5, color=MUTED, anchor="start"))

    p.append(text(p_x + p_w / 2, p_y + p_h - 15, "Просторове вікно запиту перетинає комірки дерева", size=11.5, bold=True, color=INK))

    # Right: Decision tree logic
    dt_x, dt_y = 500, 75
    dt_w, dt_h = 440, 370
    p.append(rect(dt_x, dt_y, dt_w, dt_h, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))

    p.append(text(dt_x + dt_w / 2, dt_y + 25, "Класифікація вузлів та дії", size=14, bold=True, color=INK))

    # 3 Action Cards
    # Card 1: Inside
    c1_y = dt_y + 50
    p.append(rect(dt_x + 20, c1_y, dt_w - 40, 80, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(dt_x + 35, c1_y + 24, "1. Комірка ПОВНІСТЮ всередині вікна", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(dt_x + 35, c1_y + 46, "• Усі точки піддерева додаються до відповіді", size=11, color=INK, anchor="start"))
    p.append(text(dt_x + 35, c1_y + 66, "• Немає потреби у поодиноких перевірках координат", size=10, color=MUTED, anchor="start"))

    # Card 2: Intersecting
    c2_y = dt_y + 145
    p.append(rect(dt_x + 20, c2_y, dt_w - 40, 95, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=5))
    p.append(text(dt_x + 35, c2_y + 24, "2. Комірка ЧАСТКОВО перетинає вікно", size=12, bold=True, color="#854d0e", anchor="start"))
    p.append(text(dt_x + 35, c2_y + 46, "• Перевіряється точка поточного вузла", size=11, color=INK, anchor="start"))
    p.append(text(dt_x + 35, c2_y + 66, "• Рекурсивний спуск в обох дочірніх напрямках", size=11, color=INK, anchor="start"))
    p.append(text(dt_x + 35, c2_y + 84, "• Складність для 2D: O(√N + M)", size=10, bold=True, color="#854d0e", anchor="start"))

    # Card 3: Disjoint / Outside
    c3_y = dt_y + 255
    p.append(rect(dt_x + 20, c3_y, dt_w - 40, 85, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    p.append(text(dt_x + 35, c3_y + 24, "3. Комірка НЕ ПЕРЕТИНАЄ вікно (Поза межами)", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(dt_x + 35, c3_y + 46, "• Піддерево негайно відсікається (Pruning)", size=11, color=INK, anchor="start"))
    p.append(text(dt_x + 35, c3_y + 66, "• Жоден нащадок не відвідується — O(1)", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "fig-kd-tree-range-search.svg"), W, H, *p)


if __name__ == "__main__":
    fig_kd_tree_space_partition()
    fig_kd_tree_nns_pruning()
    fig_kd_tree_curse_dimensionality()
    fig_kd_tree_range_search()
    print("All k-d tree figures generated successfully!")
