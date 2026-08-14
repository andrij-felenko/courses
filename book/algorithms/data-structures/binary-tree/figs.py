# -*- coding: utf-8 -*-
"""Фігури до статті «Двійкове дерево (Binary Tree)».
Малюємо анатомію дерева, схеми пам'яті, класифікацію дерев та обходи.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Допоміжна структура та алгоритми розкладки ──────────────────────────────
class TN:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def assign_pos(root):
    """Присвоює кожному вузлу (in-order rank, depth)."""
    pos = {}
    counter = [0]
    def walk(n, d):
        if n is None:
            return
        walk(n.left, d + 1)
        pos[n] = (counter[0], d)
        counter[0] += 1
        walk(n.right, d + 1)
    walk(root, 0)
    return pos

def collect_nodes(root):
    res = []
    def walk(n):
        if n is None:
            return
        walk(n.left)
        res.append(n)
        walk(n.right)
    walk(root)
    return res

# ── Фігура 1: Анатомія двійкового дерева ─────────────────────────────────────
def fig_anatomy():
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    node_G = TN('G')
    node_E = TN('E', node_G, None)
    node_D = TN('D')
    node_B = TN('B', node_D, node_E)
    node_F = TN('F')
    node_C = TN('C', None, node_F)
    root = TN('A', node_B, node_C)
    
    X0, Y0 = 140, 90
    COL_W, ROW_H = 85, 95
    R = 24
    
    pos = assign_pos(root)
    coords = {n: (X0 + pos[n][0] * COL_W, Y0 + pos[n][1] * ROW_H) for n in pos}
    
    levels = [
        (Y0, "Рівень 0 (корінь, h=3)"),
        (Y0 + ROW_H, "Рівень 1 (глибина 1)"),
        (Y0 + 2 * ROW_H, "Рівень 2 (глибина 2)"),
        (Y0 + 3 * ROW_H, "Рівень 3 (листки, глибина 3)")
    ]
    for y_lvl, lbl in levels:
        p.append(line(50, y_lvl, W - 40, y_lvl, color="#e2e8f0", sw=1.2, dash="4,4"))
        p.append(text(55, y_lvl - 10, lbl, size=12, color=MUTED, anchor="start", italic=True))
    
    pts_left = [
        (coords[node_B][0], coords[node_B][1] - 32),
        (coords[node_D][0] - 35, coords[node_D][1] + 35),
        (coords[node_E][0] + 35, coords[node_E][1] + 35)
    ]
    poly_pts = f"{pts_left[0][0]},{pts_left[0][1]} {pts_left[1][0]},{pts_left[1][1]} {pts_left[2][0]},{pts_left[2][1]}"
    p.append(f'<polygon points="{poly_pts}" fill="#edf2f7" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3,3"/>')
    p.append(text(coords[node_D][0] - 10, coords[node_D][1] + 52, "Ліве піддерево вузла A", size=13, color=MUTED, anchor="start", italic=True))
    
    for n in collect_nodes(root):
        for child in (n.left, n.right):
            if child is not None:
                x1, y1 = coords[n]
                x2, y2 = coords[child]
                p.append(line(x1, y1, x2, y2, color=LINE, sw=2.0))
    
    node_styles = {
        'A': (FIELD, "#ffffff", "Корінь (Root)"),
        'B': ("#3b82f6", "#ffffff", "Внутрішній вузол"),
        'C': ("#3b82f6", "#ffffff", "Внутрішній вузол"),
        'D': ("#8b5cf6", "#ffffff", "Листок (Leaf)"),
        'E': ("#3b82f6", "#ffffff", "Внутрішній вузол"),
        'F': ("#8b5cf6", "#ffffff", "Листок (Leaf)"),
        'G': ("#8b5cf6", "#ffffff", "Листок (Leaf)")
    }
    
    for n in collect_nodes(root):
        cx, cy = coords[n]
        bg_col, txt_col, lbl = node_styles[n.val]
        p.append(circle(cx, cy, R, fill=bg_col, stroke=LINE, sw=2.0))
        p.append(text(cx, cy + 5, n.val, size=16, color=txt_col, bold=True))
    
    callouts = [
        (coords[root][0] + 35, coords[root][1], "Корінь дерева (не має батька)"),
        (coords[node_B][0] - 35, coords[node_B][1], "Ліва дитина (Left child)"),
        (coords[node_C][0] + 35, coords[node_C][1], "Права дитина (Right child)"),
        (coords[node_F][0] + 35, coords[node_F][1], "Листок (степінь = 0, дітей немає)"),
    ]
    for x, y, txt_lbl in callouts:
        anchor = "end" if x < 250 else "start"
        dx = -10 if anchor == "end" else 10
        p.append(line(x - dx, y, x + dx * 0.5, y, color=MUTED, sw=1.2))
        p.append(text(x + dx * 0.8, y + 4, txt_lbl, size=13, color=INK, anchor=anchor, bold=False))
    
    p.append(rect(40, 15, W - 80, 40, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    p.append(text(W / 2, 40, "Анатомія двійкового дерева: корінь, піддерева, рівні та листки", size=16, color=INK, bold=True))
    
    render(os.path.join(OUT, "tree-anatomy.svg"), W, H, *p)

# ── Фігура 2: Схеми пам'яті (Вказівники vs Суцільний масив) ───────────────────
def fig_memory_layout():
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    p.append(rect(30, 15, W - 60, 40, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    p.append(text(W / 2, 40, "Представлення двійкового дерева в пам'яті: вказівники проти масиву", size=16, color=INK, bold=True))
    
    # ── Ліва частина: Зв'язані вузли на купі ─────────────────────────────────
    p.append(rect(30, 75, 375, 420, fill="#ffffff", stroke="#cbd5e1", rx=8))
    p.append(text(217, 105, "1. Динамічні вузли (вказівники)", size=15, color=INK, bold=True))
    p.append(text(217, 125, "Гнучка структура, довільне розташування в RAM", size=12, color=MUTED, italic=True))
    
    def draw_ptr_node(x, y, label, addr):
        p.append(rect(x, y, 140, 45, fill="#f1f5f9", stroke=LINE, rx=4, sw=1.5))
        p.append(line(x + 40, y, x + 40, y + 45, color=LINE, sw=1.2))
        p.append(line(x + 100, y, x + 100, y + 45, color=LINE, sw=1.2))
        p.append(text(x + 20, y + 27, "left", size=11, color=MUTED))
        p.append(text(x + 70, y + 28, label, size=15, color=INK, bold=True))
        p.append(text(x + 120, y + 27, "right", size=11, color=MUTED))
        p.append(text(x + 70, y - 6, f"Addr: {addr}", size=11, color=NEG, anchor="middle"))
        return (x + 20, y + 22.5), (x + 120, y + 22.5)
    
    n1_l, n1_r = draw_ptr_node(145, 175, "A", "0x1008")
    n2_l, n2_r = draw_ptr_node(60, 290, "B", "0x1040")
    n3_l, n3_r = draw_ptr_node(230, 290, "C", "0x1090")
    n4_l, n4_r = draw_ptr_node(60, 400, "D", "0x1120")
    
    p.append(line(n1_l[0], n1_l[1], 130, 285, color=LINE, sw=1.8))
    p.append(line(n1_r[0], n1_r[1], 300, 285, color=LINE, sw=1.8))
    p.append(line(n2_l[0], n2_l[1], 130, 395, color=LINE, sw=1.8))
    
    p.append(text(n2_r[0] + 15, n2_r[1] + 4, "nullptr", size=11, color=POS, anchor="start"))
    p.append(text(n3_l[0] - 15, n3_l[1] + 4, "nullptr", size=11, color=POS, anchor="end"))
    p.append(text(n3_r[0] + 15, n3_r[1] + 4, "nullptr", size=11, color=POS, anchor="start"))
    p.append(text(n4_l[0] - 15, n4_l[1] + 4, "nullptr", size=11, color=POS, anchor="end"))
    p.append(text(n4_r[0] + 15, n4_r[1] + 4, "nullptr", size=11, color=POS, anchor="start"))
    
    # ── Права частина: Суцільний масив (Implicit Tree) ──────────────────────
    p.append(rect(435, 75, 375, 420, fill="#ffffff", stroke="#cbd5e1", rx=8))
    p.append(text(622, 105, "2. Компактний масив (Implicit Tree)", size=15, color=INK, bold=True))
    p.append(text(622, 125, "Повне двійкове дерево без вказівників", size=12, color=MUTED, italic=True))
    
    p.append(rect(455, 150, 335, 75, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    p.append(text(622, 172, "Формули обчислення індексів (0-based):", size=12, color=INK, bold=True))
    p.append(text(622, 195, "Left(i) = 2i + 1   |   Right(i) = 2i + 2", size=13, color=NEG, bold=True))
    p.append(text(622, 215, "Parent(i) = ⌊(i - 1) / 2⌋", size=13, color=POS, bold=True))
    
    root_m = TN('A', TN('B', TN('D'), TN('E')), TN('C'))
    pos_m = assign_pos(root_m)
    coords_m = {n: (485 + pos_m[n][0] * 68, 260 + pos_m[n][1] * 55) for n in pos_m}
    
    for n in collect_nodes(root_m):
        for ch in (n.left, n.right):
            if ch:
                p.append(line(coords_m[n][0], coords_m[n][1], coords_m[ch][0], coords_m[ch][1], color="#94a3b8", sw=1.5))
    
    idx_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
    for n in collect_nodes(root_m):
        cx, cy = coords_m[n]
        p.append(circle(cx, cy, 16, fill="#e0f2fe", stroke=NEG, sw=1.8))
        p.append(text(cx, cy + 4, n.val, size=13, color=INK, bold=True))
        p.append(text(cx, cy - 20, f"[{idx_map[n.val]}]", size=11, color=NEG, bold=True))
    
    arr_y = 430
    arr_x0 = 460
    cell_w = 52
    cell_h = 40
    
    p.append(text(622, arr_y - 12, "Масив у неперервній пам'яті (RAM):", size=13, color=INK, bold=True))
    
    arr_vals = [('A', '0'), ('B', '1'), ('C', '2'), ('D', '3'), ('E', '4'), ('-', '5')]
    for i, (val, idx) in enumerate(arr_vals):
        cx = arr_x0 + i * cell_w
        bg = "#e0f2fe" if val != '-' else "#f1f5f9"
        p.append(rect(cx, arr_y, cell_w, cell_h, fill=bg, stroke=LINE, sw=1.5))
        p.append(text(cx + cell_w / 2, arr_y + 25, val, size=15, color=INK if val != '-' else MUTED, bold=True))
        p.append(text(cx + cell_w / 2, arr_y + cell_h + 16, f"i={idx}", size=11, color=NEG))
    
    render(os.path.join(OUT, "memory-layout.svg"), W, H, *p)

# ── Фігура 3: Види двійкових дерев ───────────────────────────────────────────
def fig_tree_varieties():
    W, H = 840, 500
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    p.append(rect(30, 15, W - 60, 40, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    p.append(text(W / 2, 40, "Формоутворення двійкових дерев: від виродженого до ідеального", size=16, color=INK, bold=True))
    
    panels = [
        ("1. Вироджене (Skewed)", "Зведена до списку: h = n - 1", 40, 75, 175, 400),
        ("2. Строге (Full)", "Кожен вузол має 0 або 2 дітей", 230, 75, 185, 400),
        ("3. Майже повне (Complete)", "Заповнене за рівнями зліва", 430, 75, 185, 400),
        ("4. Ідеальне (Perfect)", "Усі рівні повністю заповнені", 630, 75, 170, 400)
    ]
    
    for title, subtitle, px, py, pw, ph in panels:
        p.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#cbd5e1", rx=8))
        p.append(text(px + pw / 2, py + 25, title, size=13, color=INK, bold=True))
        p.append(text(px + pw / 2, py + 43, subtitle, size=10, color=MUTED, italic=True))
    
    # 1. Skewed Tree
    t1 = TN('1', None, TN('2', None, TN('3', None, TN('4'))))
    pos1 = assign_pos(t1)
    for n in collect_nodes(t1):
        cx = 65 + pos1[n][0] * 32
        cy = 150 + pos1[n][1] * 75
        if n.right:
            nx = 65 + pos1[n.right][0] * 32
            ny = 150 + pos1[n.right][1] * 75
            p.append(line(cx, cy, nx, ny, color=POS, sw=2.0))
        p.append(circle(cx, cy, 15, fill="#fdecea", stroke=POS, sw=1.8))
        p.append(text(cx, cy + 4, n.val, size=12, color=INK, bold=True))
    p.append(text(127, 445, "Пошук / Обхід: O(n)", size=12, color=POS, bold=True))
    
    # 2. Strict / Full Tree
    t2 = TN('1', TN('2', TN('4'), TN('5')), TN('3'))
    pos2 = assign_pos(t2)
    coords2 = {n: (240 + pos2[n][0] * 30, 160 + pos2[n][1] * 70) for n in pos2}
    for n in collect_nodes(t2):
        for ch in (n.left, n.right):
            if ch:
                p.append(line(coords2[n][0], coords2[n][1], coords2[ch][0], coords2[ch][1], color=LINE, sw=1.5))
    for n in collect_nodes(t2):
        cx, cy = coords2[n]
        p.append(circle(cx, cy, 14, fill="#f4f6f8", stroke=LINE, sw=1.5))
        p.append(text(cx, cy + 4, n.val, size=11, color=INK, bold=True))
    p.append(text(322, 445, "L = I + 1 завжди", size=12, color=INK, bold=True))
    
    # 3. Complete Tree
    t3 = TN('1', TN('2', TN('4'), TN('5')), TN('3', TN('6'), None))
    pos3 = assign_pos(t3)
    coords3 = {n: (440 + pos3[n][0] * 28, 160 + pos3[n][1] * 70) for n in pos3}
    for n in collect_nodes(t3):
        for ch in (n.left, n.right):
            if ch:
                p.append(line(coords3[n][0], coords3[n][1], coords3[ch][0], coords3[ch][1], color=FIELD, sw=1.8))
    for n in collect_nodes(t3):
        cx, cy = coords3[n]
        p.append(circle(cx, cy, 14, fill="#eafaf0", stroke=FIELD, sw=1.8))
        p.append(text(cx, cy + 4, n.val, size=11, color=INK, bold=True))
    p.append(text(522, 445, "Основа для Купи (Heap)", size=12, color=FIELD, bold=True))
    
    # 4. Perfect Tree
    t4 = TN('1', TN('2', TN('4'), TN('5')), TN('3', TN('6'), TN('7')))
    pos4 = assign_pos(t4)
    coords4 = {n: (638 + pos4[n][0] * 23, 160 + pos4[n][1] * 70) for n in pos4}
    for n in collect_nodes(t4):
        for ch in (n.left, n.right):
            if ch:
                p.append(line(coords4[n][0], coords4[n][1], coords4[ch][0], coords4[ch][1], color=NEG, sw=1.8))
    for n in collect_nodes(t4):
        cx, cy = coords4[n]
        p.append(circle(cx, cy, 13, fill="#e0f2fe", stroke=NEG, sw=1.8))
        p.append(text(cx, cy + 4, n.val, size=11, color=INK, bold=True))
    p.append(text(715, 445, "n = 2ʰ⁺¹ - 1 вузлів", size=12, color=NEG, bold=True))
    
    render(os.path.join(OUT, "tree-varieties.svg"), W, H, *p)

# ── Фігура 4: Трасування алгоритмів обходу ───────────────────────────────────
def fig_traversals_trace():
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    p.append(rect(30, 15, W - 60, 40, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    p.append(text(W / 2, 40, "Чотири класичні порядку обходу двійкового дерева", size=16, color=INK, bold=True))
    
    root = TN('F',
              TN('B', TN('A'), TN('D', TN('C'), TN('E'))),
              TN('G', None, TN('I', TN('H'), None)))
    
    pos = assign_pos(root)
    coords = {n: (80 + pos[n][0] * 82, 100 + pos[n][1] * 55) for n in pos}
    
    for n in collect_nodes(root):
        for ch in (n.left, n.right):
            if ch:
                p.append(line(coords[n][0], coords[n][1], coords[ch][0], coords[ch][1], color=LINE, sw=1.8))
    
    for n in collect_nodes(root):
        cx, cy = coords[n]
        p.append(circle(cx, cy, 18, fill="#ffffff", stroke=LINE, sw=2.0))
        p.append(text(cx, cy + 5, n.val, size=15, color=INK, bold=True))
    
    tab_y = 310
    p.append(rect(40, tab_y, 760, 185, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    
    traversals = [
        ("Прямий обхід (Pre-order):", "F → B → A → D → C → E → G → I → H", "Корінь → Ліве піддерево → Праве піддерево", POS),
        ("Серединний обхід (In-order):", "A → B → C → D → E → F → G → H → I", "Ліве піддерево → Корінь → Праве піддерево (для BST дає сортування)", FIELD),
        ("Зворотний обхід (Post-order):", "A → C → E → D → B → H → I → G → F", "Ліве піддерево → Праве піддерево → Корінь (для видалення/обчислення)", NEG),
        ("Порівневий обхід (Level-order / BFS):", "F → B → G → A → D → I → C → E → H", "Обхід за рівнем згори вниз, зліва направо (через чергу FIFO)", "#8b5cf6")
    ]
    
    for i, (name, seq, rule, col) in enumerate(traversals):
        y_row = tab_y + 25 + i * 40
        p.append(rect(55, y_row - 14, 12, 18, fill=col, stroke="none", rx=2))
        p.append(text(80, y_row, name, size=13, color=INK, anchor="start", bold=True))
        p.append(text(350, y_row, seq, size=13, color=col, anchor="start", bold=True))
        p.append(text(780, y_row, rule, size=11, color=MUTED, anchor="end", italic=True))
        if i < 3:
            p.append(line(55, y_row + 12, 785, y_row + 12, color="#e2e8f0", sw=1.0))
    
    render(os.path.join(OUT, "traversals-trace.svg"), W, H, *p)

if __name__ == "__main__":
    fig_anatomy()
    fig_memory_layout()
    fig_tree_varieties()
    fig_traversals_trace()
    print("Всі 4 фігури двійкового дерева успішно згенеровано у img/")
