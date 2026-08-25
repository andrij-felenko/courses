# -*- coding: utf-8 -*-
"""Фігури до статті «Найменший спільний предок».
Запуск: python figs.py -> пише SVG у ./img/
  tree-lca-concept, binary-lifting-powers, euler-tour-rmq, divisor-lattice-lca
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL   = "#fdecea"
BLUEFILL  = "#eaf0fd"
PURPLEFILL = "#f3e8ff"
GRAYFILL  = "#f4f6f8"

# ── 1. Концепція LCA у деревній топології ──────────────────────────────────
def fig_tree_lca_concept():
    W, H = 860, 420
    f = [
        text(W / 2, 26, "Найменший спільний предок (LCA) у деревній топології", size=18, bold=True),
        text(W / 2, 48, "Низхідні шляхи від кореня R до вершин u та v перетинаються у вершині w = LCA(u, v)",
             size=13, color=MUTED, italic=True)
    ]

    # Вісь глибини ліворуч
    f.append(line(70, 75, 70, 355, color=LINE, sw=1.2, dash="3,3"))
    for d, y in enumerate([85, 150, 215, 280, 345]):
        f.append(line(65, y, 75, y, color=MUTED, sw=1.2))
        f.append(text(52, y + 4, f"d={d}", size=11, color=MUTED, anchor="end"))

    nodes = {
        'R': (430, 85, "1 (R)", GRAYFILL, LINE, INK),
        'A': (280, 150, "2", BLUEFILL, FIELD, FIELD),
        'B': (580, 150, "3", GRAYFILL, LINE, INK),
        'W': (210, 215, "4 (w=LCA)", PURPLEFILL, POS, POS),
        'C': (350, 215, "5", GRAYFILL, LINE, INK),
        'D': (140, 280, "8", BLUEFILL, FIELD, FIELD),
        'E': (270, 280, "9", PURPLEFILL, POS, POS),
        'U': (90, 345, "14 (u)", REDFILL, NEG, NEG),
        'V': (320, 345, "15 (v)", GREENFILL, FIELD, FIELD)
    }

    edges = [
        ('R', 'A', BLUEFILL, FIELD, 2.5),
        ('R', 'B', GRAYFILL, LINE, 1.2),
        ('A', 'W', BLUEFILL, FIELD, 2.5),
        ('A', 'C', GRAYFILL, LINE, 1.2),
        ('W', 'D', REDFILL, NEG, 2.2),
        ('W', 'E', GREENFILL, FIELD, 2.2),
        ('D', 'U', REDFILL, NEG, 2.2),
        ('E', 'V', GREENFILL, FIELD, 2.2)
    ]

    for u_key, v_key, fill_c, st_c, sw_val in edges:
        x1, y1, _, _, _, _ = nodes[u_key]
        x2, y2, _, _, _, _ = nodes[v_key]
        f.append(line(x1, y1, x2, y2, color=st_c, sw=sw_val))

    for key, (x, y, lbl, fill_c, st_c, txt_c) in nodes.items():
        r_size = 22 if 'LCA' in lbl or key in ['U', 'V'] else 18
        f.append(circle(x, y, r_size, fill=fill_c, stroke=st_c, sw=2.0 if r_size > 18 else 1.2))
        f.append(text(x, y + 5, lbl.split()[0], size=13 if r_size > 18 else 11, bold=True, color=txt_c))

    f.append(fitbox(375, 48, 110, 22, "Корінь R=1", size=11, fill=GRAYFILL, stroke=LINE))
    f.append(fitbox(140, 173, 140, 24, "w = LCA(14, 15) = 4", size=11, bold=True, fill=PURPLEFILL, stroke=POS))
    f.append(fitbox(30, 374, 100, 22, "Вершина u=14", size=11, bold=True, fill=REDFILL, stroke=NEG))
    f.append(fitbox(280, 374, 100, 22, "Вершина v=15", size=11, bold=True, fill=GREENFILL, stroke=FIELD))

    info_x = 510
    f.append(rect(info_x, 210, 320, 160, fill=BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(info_x + 160, 232, "Фундаментальна метрика дерева:", size=13, bold=True, color=INK))
    f.append(text(info_x + 160, 260, "dist(u, v) = depth(u) + depth(v) − 2·depth(LCA)", size=12, bold=True, color=FIELD))
    f.append(text(info_x + 20, 290, "• depth(u = 14) = 4", size=12, anchor="start", color=INK))
    f.append(text(info_x + 20, 310, "• depth(v = 15) = 4", size=12, anchor="start", color=INK))
    f.append(text(info_x + 20, 330, "• depth(LCA = 4) = 2", size=12, anchor="start", color=POS))
    f.append(text(info_x + 20, 352, "Відстань: 4 + 4 − 2·2 = 4 ребра (14→8→4→9→15)", size=12, bold=True, anchor="start", color=INK))

    render(os.path.join(IMG, "tree-lca-concept.svg"), W, H, *f)


# ── 2. Метод бінарного підйому ─────────────────────────────────────────────
def fig_binary_lifting_powers():
    W, H = 860, 380
    f = [
        text(W / 2, 26, "Метод бінарного підйому: стрибки за степенями двійки", size=18, bold=True),
        text(W / 2, 48, "Таблиця up[u][k] зберігає 2^k-го предка вершини u, дозволяючи знайти LCA за O(log N)",
             size=13, color=MUTED, italic=True)
    ]

    y_coords = [330, 270, 210, 150, 90]
    labels = ["u (глибина 13)", "up[u][0] (+1)", "up[u][1] (+2)", "up[u][2] (+4)", "up[u][3] (+8)"]
    x_chain = 180

    for i, (y, lbl) in enumerate(zip(y_coords, labels)):
        bg = REDFILL if i == 0 else (BLUEFILL if i < 4 else PURPLEFILL)
        st = NEG if i == 0 else (FIELD if i < 4 else POS)
        f.append(circle(x_chain, y, 20, fill=bg, stroke=st, sw=1.8))
        f.append(text(x_chain, y + 4, str(i), size=12, bold=True, color=st))
        f.append(text(x_chain - 35, y + 4, lbl, size=12, bold=(i==0), anchor="end", color=INK))

    jumps = [
        (0, 1, "2⁰ = 1 крок", 35),
        (0, 2, "2¹ = 2 кроки", 90),
        (0, 3, "2² = 4 кроки", 145),
        (0, 4, "2³ = 8 кроків", 200)
    ]

    for start_i, end_i, j_lbl, offset_x in jumps:
        y1 = y_coords[start_i]
        y2 = y_coords[end_i]
        cur_x = x_chain + offset_x
        clr = POS if end_i == 4 else FIELD
        dash_str = ' stroke-dasharray="4,3"' if end_i < 4 else ''
        f.append(f'<path d="M {x_chain + 20:.1f} {y1:.1f} C {cur_x:.1f} {y1:.1f}, {cur_x:.1f} {y2:.1f}, {x_chain + 20:.1f} {y2:.1f}" fill="none" stroke="{clr}" stroke-width="1.8"{dash_str}/>')
        f.append(text(cur_x + 8, (y1 + y2) / 2 + 4, j_lbl, size=11, bold=(end_i==4), anchor="start", color=clr))

    box_x = 480
    f.append(rect(box_x, 90, 350, 260, fill=BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(box_x + 175, 115, "Рекурентна формула таблиці:", size=14, bold=True, color=INK))
    f.append(text(box_x + 175, 148, "up[u][k] = up[ up[u][k−1] ][ k−1 ]", size=13, bold=True, color=FIELD))

    f.append(text(box_x + 20, 185, "Алгоритм пошуку LCA(u, v):", size=13, bold=True, anchor="start", color=INK))
    f.append(text(box_x + 20, 215, "1. Вирівнювання глибин: якщо depth(u) > depth(v),", size=12, anchor="start", color=INK))
    f.append(text(box_x + 35, 235, "піднімаємо u на різницю Δd за двійковими бітами.", size=11, color=MUTED, anchor="start"))
    f.append(text(box_x + 20, 265, "2. Одночасний підйом: для k = ⌊log N⌋ .. 0,", size=12, anchor="start", color=INK))
    f.append(text(box_x + 35, 285, "якщо up[u][k] ≠ up[v][k], робимо u = up[u][k], v = up[v][k].", size=11, color=MUTED, anchor="start"))
    f.append(text(box_x + 20, 315, "3. Результат: LCA(u, v) = up[u][0].", size=12, bold=True, anchor="start", color=POS))

    render(os.path.join(IMG, "binary-lifting-powers.svg"), W, H, *f)


# ── 3. Зведення LCA до RMQ через обхід Ейлера ─────────────────────────────
def fig_euler_tour_rmq():
    W, H = 860, 400
    f = [
        text(W / 2, 26, "Зведення LCA до Range Minimum Query (RMQ)", size=18, bold=True),
        text(W / 2, 48, "Найменший спільний предок відповідає мінімальній глибині на відрізку обходу Ейлера [first[u] .. first[v]]",
             size=13, color=MUTED, italic=True)
    ]

    nodes_tour = [1, 2, 4, 2, 5, 2, 1, 3, 6, 3, 7, 3, 1]
    depth_tour = [0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1, 0]
    
    cell_w, cell_h = 56, 36
    start_x, start_y = 60, 100

    f.append(text(45, start_y - 12, "Індекс i:", size=11, color=MUTED, anchor="end"))
    f.append(text(45, start_y + 22, "Euler[i]:", size=12, bold=True, anchor="end"))
    f.append(text(45, start_y + cell_h + 22, "Depth[i]:", size=12, bold=True, anchor="end"))

    l_idx, r_idx = 2, 10
    min_idx = 6

    for i in range(len(nodes_tour)):
        x = start_x + i * cell_w
        is_range = (l_idx <= i <= r_idx)
        is_min = (i == min_idx)
        is_end = (i == l_idx or i == r_idx)

        bg = PURPLEFILL if is_min else (GREENFILL if is_end else (BLUEFILL if is_range else BG))
        st = POS if is_min else (FIELD if is_range else LINE)

        f.append(text(x + cell_w / 2, start_y - 12, str(i), size=11, color=MUTED))
        
        f.append(rect(x, start_y, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if is_range else 1.0, rx=3))
        f.append(text(x + cell_w / 2, start_y + 22, str(nodes_tour[i]), size=14, bold=is_range, color=POS if is_min else INK))

        f.append(rect(x, start_y + cell_h + 4, cell_w, cell_h, fill=bg, stroke=st, sw=1.8 if is_range else 1.0, rx=3))
        f.append(text(x + cell_w / 2, start_y + cell_h + 26, str(depth_tour[i]), size=14, bold=is_range, color=POS if is_min else INK))

    f.append(rect(start_x + l_idx * cell_w - 3, start_y - 4, (r_idx - l_idx + 1) * cell_w + 6, 2 * cell_h + 14,
                  fill="none", stroke=FIELD, sw=2.2, rx=6))

    x_u = start_x + l_idx * cell_w + cell_w / 2
    x_v = start_x + r_idx * cell_w + cell_w / 2
    x_min = start_x + min_idx * cell_w + cell_w / 2

    f.append(line(x_u, start_y + 2 * cell_h + 15, x_u, start_y + 2 * cell_h + 45, color=FIELD, sw=1.8))
    f.append(text(x_u, start_y + 2 * cell_h + 60, "first[u=4] = 2", size=11, bold=True, color=FIELD))

    f.append(line(x_v, start_y + 2 * cell_h + 15, x_v, start_y + 2 * cell_h + 45, color=FIELD, sw=1.8))
    f.append(text(x_v, start_y + 2 * cell_h + 60, "first[v=7] = 10", size=11, bold=True, color=FIELD))

    f.append(line(x_min, start_y + 2 * cell_h + 15, x_min, start_y + 2 * cell_h + 45, color=POS, sw=2.2))
    f.append(text(x_min, start_y + 2 * cell_h + 60, "min_depth = 0 (вершина 1)", size=12, bold=True, color=POS))

    f.append(rect(180, 320, 500, 55, fill=PURPLEFILL, stroke=POS, sw=1.5, rx=6))
    f.append(text(430, 342, "LCA(4, 7) = Euler[ argmin_{2 ≤ k ≤ 10} Depth[k] ] = Euler[6] = 1", size=14, bold=True, color=POS))
    f.append(text(430, 362, "Запит Range Minimum Query (RMQ) розв'язується за O(1) через Sparse Table", size=12, color=INK))

    render(os.path.join(IMG, "euler-tour-rmq.svg"), W, H, *f)


# ── 4. Ґрати подільності та НСК як LCA ─────────────────────────────────────
def fig_divisor_lattice_lca():
    W, H = 860, 420
    f = [
        text(W / 2, 26, "Дискретні ґрати подільності (ℕ, |): НСК та НСД", size=18, bold=True),
        text(W / 2, 48, "Найменше спільне кратне НСК(a, b) є супремумом (LCA), а НСД(a, b) — інфімумом у ґратах дільників",
             size=13, color=MUTED, italic=True)
    ]

    lattice_nodes = {
        '36': (430, 90, "36 = НСК(12, 18)", PURPLEFILL, POS, POS),
        '12': (280, 160, "12 (a)", REDFILL, NEG, NEG),
        '18': (580, 160, "18 (b)", GREENFILL, FIELD, FIELD),
        '4':  (200, 240, "4", GRAYFILL, LINE, INK),
        '6':  (430, 240, "6 = НСД(12, 18)", BLUEFILL, FIELD, FIELD),
        '9':  (660, 240, "9", GRAYFILL, LINE, INK),
        '2':  (310, 320, "2", GRAYFILL, LINE, INK),
        '3':  (550, 320, "3", GRAYFILL, LINE, INK),
        '1':  (430, 380, "1 (Мінімум)", GRAYFILL, LINE, INK)
    }

    lattice_edges = [
        ('1', '2'), ('1', '3'),
        ('2', '4'), ('2', '6'), ('3', '6'), ('3', '9'),
        ('4', '12'), ('6', '12'), ('6', '18'), ('9', '18'),
        ('12', '36'), ('18', '36')
    ]

    highlight_edges = [('6', '12'), ('6', '18'), ('12', '36'), ('18', '36')]

    for u_k, v_k in lattice_edges:
        x1, y1, _, _, _, _ = lattice_nodes[u_k]
        x2, y2, _, _, _, _ = lattice_nodes[v_k]
        is_hl = (u_k, v_k) in highlight_edges
        f.append(line(x1, y1, x2, y2, color=POS if is_hl else LINE, sw=2.2 if is_hl else 1.2, dash="none" if is_hl else "3,3"))

    for k, (x, y, lbl, fill_c, st_c, txt_c) in lattice_nodes.items():
        is_spec = k in ['36', '12', '18', '6']
        r_val = 24 if is_spec else 18
        f.append(circle(x, y, r_val, fill=fill_c, stroke=st_c, sw=2.0 if is_spec else 1.2))
        f.append(text(x, y + 5, k, size=14 if is_spec else 11, bold=is_spec, color=txt_c))

    f.append(fitbox(330, 48, 200, 24, "LCA = Join = НСК(12, 18) = 36", size=11, bold=True, fill=PURPLEFILL, stroke=POS))
    f.append(fitbox(330, 258, 200, 24, "GLB = Meet = НСД(12, 18) = 6", size=11, bold=True, fill=BLUEFILL, stroke=FIELD))
    f.append(fitbox(100, 149, 100, 22, "Елемент a = 12", size=11, bold=True, fill=REDFILL, stroke=NEG))
    f.append(fitbox(660, 149, 100, 22, "Елемент b = 18", size=11, bold=True, fill=GREENFILL, stroke=FIELD))

    render(os.path.join(IMG, "divisor-lattice-lca.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tree_lca_concept()
    fig_binary_lifting_powers()
    fig_euler_tour_rmq()
    fig_divisor_lattice_lca()
    print("Всі фігури успішно згенеровано у ./img/")
