# -*- coding: utf-8 -*-
"""Фігури до статті «B-дерево».
Генерує векторні схеми SVG у теці ./img/:
1. node-structure.svg — структура вузла B-дерева та розгалуження
2. node-split.svg — процес розщеплення переповненого вузла при вставці
3. borrow-merge.svg — відновлення інваріанту при вилученні (запозичення та злиття)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Анатомія вузла B-дерева (порядок m=5, t=3)
# ─────────────────────────────────────────────────────────────────────────────
def fig_node_structure():
    W, H = 820, 360
    parts = []
    
    parts.append(rect(20, 20, 780, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 48, "Структура внутрішнього вузла B-дерева (порядок m = 5, t = 3)", size=16, color=INK, bold=True))
    parts.append(text(410, 72, "Вузол містить масив ключів (до 2t - 1 = 4) та масив вказівників на піддерева (до 2t = 5)", size=13, color="#64748b"))

    start_x = 70
    y_node = 110
    cell_w_p = 50
    cell_w_k = 90
    cell_h = 55
    
    # Outer box for entire node array
    total_w = 5 * cell_w_p + 4 * cell_w_k
    parts.append(rect(start_x, y_node, total_w, cell_h, fill="#ffffff", stroke="#94a3b8", sw=2, rx=4))
    
    x_curr = start_x
    p_centers = []
    keys = ["15", "32", "58", "81"]
    
    for i in range(4):
        # Pointer cell background P_i
        parts.append(rect(x_curr, y_node, cell_w_p, cell_h, fill="#e2e8f0", stroke="#94a3b8", sw=1))
        parts.append(text(x_curr + cell_w_p / 2, y_node + cell_h / 2 + 5, f"P{i}", size=13, color="#334155", bold=True))
        p_centers.append(x_curr + cell_w_p / 2)
        x_curr += cell_w_p
        
        # Key cell background K_{i+1}
        parts.append(rect(x_curr, y_node, cell_w_k, cell_h, fill="#dbeafe", stroke="#3b82f6", sw=1.5))
        parts.append(text(x_curr + cell_w_k / 2, y_node + cell_h / 2 + 5, keys[i], size=16, color="#1e40af", bold=True))
        x_curr += cell_w_k
        
    # Last Pointer P4
    parts.append(rect(x_curr, y_node, cell_w_p, cell_h, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    parts.append(text(x_curr + cell_w_p / 2, y_node + cell_h / 2 + 5, "P4", size=13, color="#334155", bold=True))
    p_centers.append(x_curr + cell_w_p / 2)

    # Subtrees
    y_sub = 250
    sub_w = 120
    sub_h = 50
    
    sub_ranges = [
        ("X < 15", "#f1f5f9"),
        ("15 < X < 32", "#f1f5f9"),
        ("32 < X < 58", "#f1f5f9"),
        ("58 < X < 81", "#f1f5f9"),
        ("X > 81", "#f1f5f9")
    ]
    
    sub_xs = [60, 210, 360, 510, 660]
    
    for i in range(5):
        sx = sub_xs[i]
        px = p_centers[i]
        parts.append(line(px, y_node + cell_h, sx + sub_w / 2, y_sub, color="#64748b", sw=1.8))
        parts.append(rect(sx, y_sub, sub_w, sub_h, fill=sub_ranges[i][1], stroke="#94a3b8", sw=1.5, rx=6))
        parts.append(text(sx + sub_w / 2, y_sub + 22, f"Піддерево {i}", size=12, color="#475569", bold=True))
        parts.append(text(sx + sub_w / 2, y_sub + 40, sub_ranges[i][0], size=11, color="#64748b"))

    render(os.path.join(OUT, "node-structure.svg"), W, H, "\n".join(parts))

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Процес розщеплення (Split) вузла
# ─────────────────────────────────────────────────────────────────────────────
def fig_node_split():
    W, H = 820, 500
    parts = []
    
    parts.append(rect(20, 20, 780, 460, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))
    parts.append(text(410, 45, "Процес розщеплення переповненого вузла (t = 3)", size=16, color=INK, bold=True))
    
    # Step 1
    y1 = 80
    parts.append(text(80, y1 + 20, "1. Стан до розщеплення (вузол переповнений: 5 ключів)", size=13, color="#334155", bold=True))
    
    # Parent node above
    parts.append(rect(340, y1 + 35, 140, 38, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))
    parts.append(text(410, y1 + 58, "Батьківський [10]", size=12, color="#475569"))
    
    # Full child node: one big box 400px wide (5 x 80)
    y_full = y1 + 115
    x_full = 210
    keys_full = ["18", "25", "37", "42", "50"]
    
    parts.append(line(410, y1 + 73, 410, y_full, color="#94a3b8", sw=1.5))
    
    # Outer frame
    parts.append(rect(x_full, y_full, 400, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    
    for i, k in enumerate(keys_full):
        cx = x_full + i * 80
        if i == 2: # median highlight
            parts.append(rect(cx, y_full, 80, 45, fill="#fef2f2", stroke="#ef4444", sw=2))
            parts.append(text(cx + 40, y_full + 28, k, size=15, color="#991b1b", bold=True))
        else:
            if i > 0:
                parts.append(line(cx, y_full, cx, y_full + 45, color="#93c5fd", sw=1.5))
            parts.append(text(cx + 40, y_full + 28, k, size=15, color="#1e40af", bold=True))
        
    parts.append(text(x_full + 200, y_full + 66, "Медіана (37) піднімається вгору", size=12, color="#b91c1c", bold=True))

    # Down arrow
    y_arrow = y_full + 85
    parts.append(arrow(410, y_arrow, 410, y_arrow + 30, color="#2563eb", sw=2.5))

    # Step 2
    y2 = y_arrow + 45
    parts.append(text(80, y2, "2. Стан після розщеплення (медіана у батька, 2 нових вузли по 2 ключі)", size=13, color="#334155", bold=True))

    # New Parent Node
    y_p_new = y2 + 20
    parts.append(rect(310, y_p_new, 200, 45, fill="#fef2f2", stroke="#ef4444", sw=2, rx=4))
    parts.append(text(410, y_p_new + 28, "Батьківський [10 | 37]", size=14, color="#991b1b", bold=True))

    # Two Children
    y_c_new = y_p_new + 80
    
    # Left child [18 | 25] as a single box (160x45)
    parts.append(line(360, y_p_new + 45, 230, y_c_new, color="#64748b", sw=1.8))
    parts.append(rect(150, y_c_new, 160, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(line(230, y_c_new, 230, y_c_new + 45, color="#93c5fd", sw=1.5))
    parts.append(text(190, y_c_new + 28, "18", size=15, color="#1e40af", bold=True))
    parts.append(text(270, y_c_new + 28, "25", size=15, color="#1e40af", bold=True))

    # Right child [42 | 50] as a single box (160x45)
    parts.append(line(460, y_p_new + 45, 590, y_c_new, color="#64748b", sw=1.8))
    parts.append(rect(510, y_c_new, 160, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(line(590, y_c_new, 590, y_c_new + 45, color="#93c5fd", sw=1.5))
    parts.append(text(550, y_c_new + 28, "42", size=15, color="#1e40af", bold=True))
    parts.append(text(630, y_c_new + 28, "50", size=15, color="#1e40af", bold=True))

    render(os.path.join(OUT, "node-split.svg"), W, H, "\n".join(parts))

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Запозичення та Злиття при вилученні
# ─────────────────────────────────────────────────────────────────────────────
def fig_borrow_merge():
    W, H = 820, 520
    parts = []
    
    parts.append(rect(20, 20, 780, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 48, "Відновлення інваріанту вузла при вилученні (t = 3, мін. ключів t-1 = 2)", size=16, color=INK, bold=True))

    # Секція A
    y_a = 80
    parts.append(text(50, y_a + 15, "Сценарій А: Запозичення у лівого сусіда (у сусіда є > t-1 ключів)", size=13, color="#1e293b", bold=True))
    
    parts.append(rect(360, y_a + 35, 100, 40, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))
    parts.append(text(410, y_a + 60, "Батько: [30]", size=13, color="#334155", bold=True))
    
    y_nodes_a = y_a + 105
    parts.append(line(380, y_a + 75, 230, y_nodes_a, color="#64748b", sw=1.5))
    parts.append(rect(140, y_nodes_a, 180, 40, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(230, y_nodes_a + 25, "Сусід: [10 | 20 | 25]", size=13, color="#15803d", bold=True))
    
    parts.append(line(440, y_a + 75, 570, y_nodes_a, color="#64748b", sw=1.5))
    parts.append(rect(490, y_nodes_a, 160, 40, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(570, y_nodes_a + 25, "Дефіцитний: [40]", size=13, color="#b91c1c", bold=True))

    parts.append(text(410, y_nodes_a + 65, "Обертання: 25 іде в батька, 30 спускається в дефіцитний вузол -> [30 | 40]", size=12, color="#2563eb", bold=True))

    # Секція B
    y_b = 270
    parts.append(line(40, y_b - 15, 780, y_b - 15, color="#cbd5e1", sw=1, dash="4 4"))
    parts.append(text(50, y_b + 10, "Сценарій Б: Злиття вузлів (в обидвох сусідів рівно t-1 = 2 ключі)", size=13, color="#1e293b", bold=True))

    y_b_top = y_b + 35
    parts.append(rect(360, y_b_top, 100, 40, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))
    parts.append(text(410, y_b_top + 25, "Батько: [50]", size=13, color="#334155", bold=True))

    y_b_kids = y_b_top + 65
    parts.append(line(380, y_b_top + 40, 250, y_b_kids, color="#64748b", sw=1.5))
    parts.append(rect(170, y_b_kids, 160, 40, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))
    parts.append(text(250, y_b_kids + 25, "Лівий: [10 | 20]", size=13, color="#334155"))

    parts.append(line(440, y_b_top + 40, 570, y_b_kids, color="#64748b", sw=1.5))
    parts.append(rect(500, y_b_kids, 140, 40, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(570, y_b_kids + 25, "Правий: [60]", size=13, color="#b91c1c"))

    y_b_res = y_b_kids + 65
    parts.append(arrow(410, y_b_kids + 10, 410, y_b_res - 5, color="#2563eb", sw=2))

    parts.append(rect(270, y_b_res + 5, 280, 40, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=4))
    parts.append(text(410, y_b_res + 30, "Об'єднаний вузол: [10 | 20 | 50 | 60]", size=14, color="#1e40af", bold=True))

    render(os.path.join(OUT, "borrow-merge.svg"), W, H, "\n".join(parts))

if __name__ == "__main__":
    fig_node_structure()
    fig_node_split()
    fig_borrow_merge()
    print("Всі 3 фігури B-дерева успішно згенеровано.")
