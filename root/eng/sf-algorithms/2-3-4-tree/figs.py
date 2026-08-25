# -*- coding: utf-8 -*-
"""Фігури до статті «2-3-4 дерево».
Генерує векторні схеми SVG у теці ./img/:
1. node-types.svg — типи вузлів 2-3-4 дерева (2-вузол, 3-вузол, 4-вузол) та діапазони піддерев
2. top-down-insertion.svg — превентивне розщеплення 4-вузла під час спуску зверху вниз
3. top-down-deletion.svg — превентивне відновлення 2-вузлів (запозичення та злиття)
4. rb-isomorphism.svg — структурний ізоморфізм між 2-3-4 деревом та червоно-чорним деревом
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Типи вузлів 2-3-4 дерева (2-вузол, 3-вузол, 4-вузол)
# ─────────────────────────────────────────────────────────────────────────────
def fig_node_types():
    W, H = 840, 310
    parts = []
    
    parts.append(rect(15, 15, 810, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Вузли 2-3-4 дерева та діапазони ключів у піддеревах", size=15, color=INK, bold=True))

    # 1. 2-вузол
    x1, y1 = 40, 75
    w1, h1 = 220, 195
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x1 + w1/2, y1 + 24, "2-вузол (1 ключ, 2 нащадки)", size=12, color="#1e293b", bold=True))
    
    # Node block
    parts.append(rect(x1 + 75, y1 + 45, 70, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 110, y1 + 68, "K1", size=14, color="#1e40af", bold=True))
    
    # Subtrees
    parts.append(line(x1 + 85, y1 + 81, x1 + 45, y1 + 120, color="#64748b", sw=1.5))
    parts.append(line(x1 + 135, y1 + 81, x1 + 175, y1 + 120, color="#64748b", sw=1.5))
    
    parts.append(rect(x1 + 15, y1 + 120, 65, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x1 + 47, y1 + 141, "< K1", size=11, color="#334155"))
    
    parts.append(rect(x1 + 140, y1 + 120, 65, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x1 + 172, y1 + 141, "> K1", size=11, color="#334155"))
    parts.append(text(x1 + w1/2, y1 + 180, "Мінімальна ємність", size=11, color="#64748b", italic=True))

    # 2. 3-вузол
    x2, y2 = 285, 75
    w2, h2 = 250, 195
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x2 + w2/2, y2 + 24, "3-вузол (2 ключі, 3 нащадки)", size=12, color="#1e293b", bold=True))
    
    # Node block
    parts.append(rect(x2 + 65, y2 + 45, 60, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x2 + 95, y2 + 68, "K1", size=14, color="#1e40af", bold=True))
    parts.append(rect(x2 + 125, y2 + 45, 60, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x2 + 155, y2 + 68, "K2", size=14, color="#1e40af", bold=True))
    
    # Subtrees
    parts.append(line(x2 + 75, y2 + 81, x2 + 35, y2 + 120, color="#64748b", sw=1.5))
    parts.append(line(x2 + 125, y2 + 81, x2 + 125, y2 + 120, color="#64748b", sw=1.5))
    parts.append(line(x2 + 175, y2 + 81, x2 + 215, y2 + 120, color="#64748b", sw=1.5))
    
    parts.append(rect(x2 + 10, y2 + 120, 56, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x2 + 38, y2 + 141, "< K1", size=11, color="#334155"))
    
    parts.append(rect(x2 + 88, y2 + 120, 74, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x2 + 125, y2 + 141, "K1..K2", size=11, color="#334155"))
    
    parts.append(rect(x2 + 184, y2 + 120, 56, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x2 + 212, y2 + 141, "> K2", size=11, color="#334155"))
    parts.append(text(x2 + w2/2, y2 + 180, "Проміжна ємність", size=11, color="#64748b", italic=True))

    # 3. 4-вузол
    x3, y3 = 560, 75
    w3, h3 = 250, 195
    parts.append(rect(x3, y3, w3, h3, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x3 + w3/2, y2 + 24, "4-вузол (3 ключі, 4 нащадки)", size=12, color="#1e293b", bold=True))
    
    # Node block
    parts.append(rect(x3 + 45, y3 + 45, 52, 36, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x3 + 71, y3 + 68, "K1", size=13, color="#991b1b", bold=True))
    parts.append(rect(x3 + 97, y3 + 45, 56, 36, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x3 + 125, y3 + 68, "K2", size=13, color="#991b1b", bold=True))
    parts.append(rect(x3 + 153, y3 + 45, 52, 36, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x3 + 179, y3 + 68, "K3", size=13, color="#991b1b", bold=True))
    
    # Subtrees
    parts.append(line(x3 + 55, y3 + 81, x3 + 25, y3 + 120, color="#64748b", sw=1.5))
    parts.append(line(x3 + 97, y3 + 81, x3 + 85, y3 + 120, color="#64748b", sw=1.5))
    parts.append(line(x3 + 153, y3 + 81, x3 + 165, y3 + 120, color="#64748b", sw=1.5))
    parts.append(line(x3 + 195, y3 + 81, x3 + 225, y3 + 120, color="#64748b", sw=1.5))
    
    parts.append(rect(x3 + 6, y3 + 120, 48, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x3 + 30, y3 + 141, "< K1", size=10, color="#334155"))
    
    parts.append(rect(x3 + 60, y3 + 120, 56, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x3 + 88, y3 + 141, "K1..K2", size=10, color="#334155"))
    
    parts.append(rect(x3 + 134, y3 + 120, 56, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x3 + 162, y3 + 141, "K2..K3", size=10, color="#334155"))
    
    parts.append(rect(x3 + 196, y3 + 120, 48, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x3 + 220, y3 + 141, "> K3", size=10, color="#334155"))
    parts.append(text(x3 + w3/2, y3 + 180, "Повний вузол (вимагає спліту)", size=11, color="#dc2626", bold=True))

    render(os.path.join(OUT, "node-types.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Превентивне розщеплення 4-вузла (Top-Down Split)
# ─────────────────────────────────────────────────────────────────────────────
def fig_top_down_insertion():
    W, H = 840, 430
    parts = []
    
    parts.append(rect(15, 15, 810, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Превентивне розщеплення 4-вузла при спуску зверху вниз", size=15, color=INK, bold=True))

    # Ліва частина: До розщеплення
    x_l = 35
    parts.append(rect(x_l, 65, 360, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x_l + 180, 90, "Стан ДО розщеплення", size=13, color="#1e293b", bold=True))
    
    # Parent (2-node or 3-node)
    parts.append(rect(x_l + 130, 115, 80, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x_l + 170, 138, "P1", size=14, color="#1e40af", bold=True))
    parts.append(text(x_l + 170, 108, "Батько (гарантовано < 3 ключів)", size=11, color="#64748b"))

    # Child 4-node
    parts.append(rect(x_l + 40, 220, 150, 36, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x_l + 65, 243, "A", size=13, color="#991b1b", bold=True))
    parts.append(text(x_l + 115, 243, "B", size=13, color="#991b1b", bold=True))
    parts.append(text(x_l + 165, 243, "C", size=13, color="#991b1b", bold=True))
    parts.append(line(x_l + 90, 220, x_l + 90, 256, color="#f87171", sw=1))
    parts.append(line(x_l + 140, 220, x_l + 140, 256, color="#f87171", sw=1))
    
    # Right child (2-node)
    parts.append(rect(x_l + 240, 220, 60, 36, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(x_l + 270, 243, "R", size=13, color="#475569"))

    # Connections
    parts.append(line(x_l + 145, 151, x_l + 115, 220, color="#2563eb", sw=1.5))
    parts.append(line(x_l + 195, 151, x_l + 270, 220, color="#64748b", sw=1.5))
    
    # Subtrees of 4-node
    for i, lbl in enumerate(["T1", "T2", "T3", "T4"]):
        sx = x_l + 30 + i * 40
        parts.append(line(x_l + 50 + i * 35, 256, sx + 18, 310, color="#94a3b8", sw=1.2))
        parts.append(rect(sx, 310, 36, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
        parts.append(text(sx + 18, 328, lbl, size=11, color="#334155"))

    parts.append(text(x_l + 65, 195, "4-вузол", size=11, color="#dc2626", bold=True))
    parts.append(text(x_l + 180, 375, "Середній ключ B виштовхується вгору", size=11, color="#dc2626", italic=True))

    # Стрілка переходу
    parts.append(arrow(405, 230, 435, 230, color="#059669", sw=2.5))

    # Права частина: Після розщеплення
    x_r = 445
    parts.append(rect(x_r, 65, 360, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x_r + 180, 90, "Стан ПІСЛЯ розщеплення", size=13, color="#059669", bold=True))

    # Parent (now 3-node with B and P1)
    parts.append(rect(x_r + 100, 115, 120, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x_r + 130, 138, "B", size=14, color="#1e40af", bold=True))
    parts.append(text(x_r + 190, 138, "P1", size=14, color="#1e40af", bold=True))
    parts.append(line(x_r + 160, 115, x_r + 160, 151, color="#93c5fd", sw=1))
    parts.append(text(x_r + 160, 108, "Батько поглинув ключ B", size=11, color="#059669", bold=True))

    # Two new 2-nodes (A and C)
    parts.append(rect(x_r + 30, 220, 55, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x_r + 57, 243, "A", size=13, color="#1e40af", bold=True))

    parts.append(rect(x_r + 135, 220, 55, 36, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x_r + 162, 243, "C", size=13, color="#1e40af", bold=True))

    # Right child (R)
    parts.append(rect(x_r + 255, 220, 60, 36, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(x_r + 285, 243, "R", size=13, color="#475569"))

    # Connections
    parts.append(line(x_r + 110, 151, x_r + 57, 220, color="#2563eb", sw=1.5))
    parts.append(line(x_r + 160, 151, x_r + 162, 220, color="#2563eb", sw=1.5))
    parts.append(line(x_r + 210, 151, x_r + 285, 220, color="#64748b", sw=1.5))

    # Subtrees of A
    parts.append(line(x_r + 45, 256, x_r + 25, 310, color="#94a3b8", sw=1.2))
    parts.append(rect(x_r + 10, 310, 32, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x_r + 26, 328, "T1", size=11, color="#334155"))
    
    parts.append(line(x_r + 70, 256, x_r + 75, 310, color="#94a3b8", sw=1.2))
    parts.append(rect(x_r + 60, 310, 32, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x_r + 76, 328, "T2", size=11, color="#334155"))

    # Subtrees of C
    parts.append(line(x_r + 150, 256, x_r + 140, 310, color="#94a3b8", sw=1.2))
    parts.append(rect(x_r + 125, 310, 32, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x_r + 141, 328, "T3", size=11, color="#334155"))
    
    parts.append(line(x_r + 175, 256, x_r + 190, 310, color="#94a3b8", sw=1.2))
    parts.append(rect(x_r + 175, 310, 32, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(x_r + 191, 328, "T4", size=11, color="#334155"))

    parts.append(text(x_r + 180, 375, "4-вузол розпався на два 2-вузли", size=11, color="#059669", italic=True))

    render(os.path.join(OUT, "top-down-insertion.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Превентивні операції при видаленні (Borrow / Merge)
# ─────────────────────────────────────────────────────────────────────────────
def fig_top_down_deletion():
    W, H = 840, 440
    parts = []
    
    parts.append(rect(15, 15, 810, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Превентивне перетворення 2-вузла при спуску для видалення", size=15, color=INK, bold=True))

    # Випадок 1: Запозичення (Rotate / Borrow)
    x1 = 35
    parts.append(rect(x1, 65, 360, 345, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x1 + 180, 90, "Випадок 1: Запозичення (Брат має ≥ 2 ключі)", size=12, color="#1e293b", bold=True))
    
    # Parent
    parts.append(rect(x1 + 130, 115, 80, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 170, 137, "P", size=14, color="#1e40af", bold=True))
    
    # Left child (Target 2-node) & Right sibling (3-node with B, C)
    parts.append(rect(x1 + 40, 195, 60, 34, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x1 + 70, 217, "A", size=13, color="#991b1b", bold=True))
    parts.append(text(x1 + 70, 182, "Ціль (2-вузол)", size=10, color="#dc2626"))

    parts.append(rect(x1 + 200, 195, 100, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 225, 217, "B", size=13, color="#1e40af", bold=True))
    parts.append(text(x1 + 275, 217, "C", size=13, color="#1e40af", bold=True))
    parts.append(line(x1 + 250, 195, x1 + 250, 229, color="#93c5fd", sw=1))
    parts.append(text(x1 + 250, 182, "Брат (3-вузол)", size=10, color="#2563eb"))

    parts.append(line(x1 + 145, 149, x1 + 70, 195, color="#64748b", sw=1.2))
    parts.append(line(x1 + 195, 149, x1 + 250, 195, color="#64748b", sw=1.2))

    # Transformation Arrow down
    parts.append(arrow(x1 + 180, 245, x1 + 180, 275, color="#059669", sw=2.5))
    parts.append(text(x1 + 250, 262, "P опускається, B піднімається", size=10, color="#059669", italic=True))

    # Result state
    parts.append(rect(x1 + 130, 290, 80, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 170, 312, "B", size=14, color="#1e40af", bold=True))

    parts.append(rect(x1 + 30, 355, 95, 34, fill="#d1fae5", stroke="#059669", sw=1.5, rx=4))
    parts.append(text(x1 + 55, 377, "A", size=13, color="#065f46", bold=True))
    parts.append(text(x1 + 100, 377, "P", size=13, color="#065f46", bold=True))
    parts.append(line(x1 + 77, 355, x1 + 77, 389, color="#6ee7b7", sw=1))

    parts.append(rect(x1 + 220, 355, 60, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 250, 377, "C", size=13, color="#1e40af", bold=True))

    parts.append(line(x1 + 145, 324, x1 + 77, 355, color="#059669", sw=1.2))
    parts.append(line(x1 + 195, 324, x1 + 250, 355, color="#64748b", sw=1.2))
    parts.append(text(x1 + 77, 400, "Ціль стала 3-вузлом", size=10, color="#059669", bold=True))

    # Випадок 2: Злиття (Merge)
    x2 = 445
    parts.append(rect(x2, 65, 360, 345, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x2 + 180, 90, "Випадок 2: Злиття (Брат є 2-вузлом)", size=12, color="#1e293b", bold=True))

    # Parent (at least 2 keys or root)
    parts.append(rect(x2 + 110, 115, 120, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x2 + 140, 137, "P1", size=14, color="#1e40af", bold=True))
    parts.append(text(x2 + 200, 137, "P2", size=14, color="#1e40af", bold=True))
    parts.append(line(x2 + 170, 115, x2 + 170, 149, color="#93c5fd", sw=1))

    # Left child & Right sibling (both 2-nodes)
    parts.append(rect(x2 + 40, 195, 60, 34, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x2 + 70, 217, "A", size=13, color="#991b1b", bold=True))
    parts.append(text(x2 + 70, 182, "Ціль (2-вузол)", size=10, color="#dc2626"))

    parts.append(rect(x2 + 160, 195, 60, 34, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x2 + 190, 217, "B", size=13, color="#991b1b", bold=True))
    parts.append(text(x2 + 190, 182, "Брат (2-вузол)", size=10, color="#dc2626"))

    parts.append(rect(x2 + 270, 195, 50, 34, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(x2 + 295, 217, "R", size=13, color="#475569"))

    parts.append(line(x2 + 125, 149, x2 + 70, 195, color="#64748b", sw=1.2))
    parts.append(line(x2 + 170, 149, x2 + 190, 195, color="#64748b", sw=1.2))
    parts.append(line(x2 + 215, 149, x2 + 295, 195, color="#64748b", sw=1.2))

    # Transformation Arrow down
    parts.append(arrow(x2 + 180, 245, x2 + 180, 275, color="#059669", sw=2.5))
    parts.append(text(x2 + 255, 262, "P1 спускається між A та B", size=10, color="#059669", italic=True))

    # Result state
    parts.append(rect(x2 + 180, 290, 60, 34, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x2 + 210, 312, "P2", size=14, color="#1e40af", bold=True))

    # Merged 4-node (A, P1, B)
    parts.append(rect(x2 + 40, 355, 150, 34, fill="#d1fae5", stroke="#059669", sw=1.5, rx=4))
    parts.append(text(x2 + 65, 377, "A", size=13, color="#065f46", bold=True))
    parts.append(text(x2 + 115, 377, "P1", size=13, color="#065f46", bold=True))
    parts.append(text(x2 + 165, 377, "B", size=13, color="#065f46", bold=True))
    parts.append(line(x2 + 90, 355, x2 + 90, 389, color="#6ee7b7", sw=1))
    parts.append(line(x2 + 140, 355, x2 + 140, 389, color="#6ee7b7", sw=1))

    parts.append(rect(x2 + 250, 355, 50, 34, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(x2 + 275, 377, "R", size=13, color="#475569"))

    parts.append(line(x2 + 190, 324, x2 + 115, 355, color="#059669", sw=1.2))
    parts.append(line(x2 + 230, 324, x2 + 275, 355, color="#64748b", sw=1.2))
    parts.append(text(x2 + 115, 400, "Утворено 4-вузол (A, P1, B)", size=10, color="#059669", bold=True))

    render(os.path.join(OUT, "top-down-deletion.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Ізоморфізм 2-3-4 та червоно-чорних дерев (RB Isomorphism)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rb_isomorphism():
    W, H = 840, 390
    parts = []
    
    parts.append(rect(15, 15, 810, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Еквівалентність вузлів 2-3-4 дерева та червоно-чорних бінарних кластерів", size=15, color=INK, bold=True))

    # 1. 2-вузол -> 1 чорний вузол
    x1 = 40
    parts.append(rect(x1, 65, 220, 290, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x1 + 110, 88, "2-вузол", size=13, color="#1e293b", bold=True))
    
    # 2-3-4 node
    parts.append(rect(x1 + 75, 110, 70, 32, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x1 + 110, 131, "A", size=14, color="#1e40af", bold=True))
    parts.append(text(x1 + 110, 160, "ізоморфно", size=11, color="#64748b", italic=True))
    parts.append(arrow(x1 + 110, 168, x1 + 110, 195, color="#2563eb", sw=2))

    # RB Cluster
    parts.append(circle(x1 + 110, 235, 18, fill="#1e293b", stroke="#0f172a", sw=2))
    parts.append(text(x1 + 110, 241, "A", size=13, color="#ffffff", bold=True))
    
    parts.append(line(x1 + 97, 247, x1 + 65, 280, color="#64748b", sw=1.5))
    parts.append(line(x1 + 123, 247, x1 + 155, 280, color="#64748b", sw=1.5))
    parts.append(text(x1 + 65, 295, "T1", size=10, color="#64748b"))
    parts.append(text(x1 + 155, 295, "T2", size=10, color="#64748b"))
    parts.append(text(x1 + 110, 335, "1 чорний вузол", size=11, color="#1e293b", bold=True))

    # 2. 3-вузол -> 1 чорний + 1 червоний вузол
    x2 = 285
    parts.append(rect(x2, 65, 250, 290, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x2 + 125, 88, "3-вузол", size=13, color="#1e293b", bold=True))
    
    # 2-3-4 node
    parts.append(rect(x2 + 65, 110, 120, 32, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(x2 + 95, 131, "A", size=14, color="#1e40af", bold=True))
    parts.append(text(x2 + 155, 131, "B", size=14, color="#1e40af", bold=True))
    parts.append(line(x2 + 125, 110, x2 + 125, 142, color="#93c5fd", sw=1))
    parts.append(text(x2 + 125, 160, "ізоморфно", size=11, color="#64748b", italic=True))
    parts.append(arrow(x2 + 125, 168, x2 + 125, 195, color="#2563eb", sw=2))

    # RB Cluster (B black, A red left child)
    parts.append(circle(x2 + 155, 225, 18, fill="#1e293b", stroke="#0f172a", sw=2))
    parts.append(text(x2 + 155, 231, "B", size=13, color="#ffffff", bold=True))

    parts.append(line(x2 + 142, 237, x2 + 95, 265, color="#dc2626", sw=2.5))
    parts.append(circle(x2 + 85, 270, 17, fill="#ef4444", stroke="#dc2626", sw=2))
    parts.append(text(x2 + 85, 276, "A", size=13, color="#ffffff", bold=True))

    parts.append(line(x2 + 73, 281, x2 + 50, 305, color="#64748b", sw=1.5))
    parts.append(line(x2 + 97, 281, x2 + 115, 305, color="#64748b", sw=1.5))
    parts.append(line(x2 + 168, 237, x2 + 200, 275, color="#64748b", sw=1.5))
    parts.append(text(x2 + 50, 318, "T1", size=10, color="#64748b"))
    parts.append(text(x2 + 115, 318, "T2", size=10, color="#64748b"))
    parts.append(text(x2 + 200, 290, "T3", size=10, color="#64748b"))
    parts.append(text(x2 + 125, 335, "1 чорний + 1 червоний", size=11, color="#b91c1c", bold=True))

    # 3. 4-вузол -> 1 чорний + 2 червоні вузли
    x3 = 560
    parts.append(rect(x3, 65, 250, 290, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(x3 + 125, 88, "4-вузол", size=13, color="#1e293b", bold=True))
    
    # 2-3-4 node
    parts.append(rect(x3 + 45, 110, 160, 32, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(x3 + 70, 131, "A", size=13, color="#991b1b", bold=True))
    parts.append(text(x3 + 125, 131, "B", size=13, color="#991b1b", bold=True))
    parts.append(text(x3 + 180, 131, "C", size=13, color="#991b1b", bold=True))
    parts.append(line(x3 + 97, 110, x3 + 97, 142, color="#f87171", sw=1))
    parts.append(line(x3 + 153, 110, x3 + 153, 142, color="#f87171", sw=1))
    parts.append(text(x3 + 125, 160, "ізоморфно", size=11, color="#64748b", italic=True))
    parts.append(arrow(x3 + 125, 168, x3 + 125, 195, color="#2563eb", sw=2))

    # RB Cluster (B black, A red left, C red right)
    parts.append(circle(x3 + 125, 220, 18, fill="#1e293b", stroke="#0f172a", sw=2))
    parts.append(text(x3 + 125, 226, "B", size=13, color="#ffffff", bold=True))

    parts.append(line(x3 + 112, 231, x3 + 70, 260, color="#dc2626", sw=2.5))
    parts.append(circle(x3 + 60, 268, 17, fill="#ef4444", stroke="#dc2626", sw=2))
    parts.append(text(x3 + 60, 274, "A", size=13, color="#ffffff", bold=True))

    parts.append(line(x3 + 138, 231, x3 + 180, 260, color="#dc2626", sw=2.5))
    parts.append(circle(x3 + 190, 268, 17, fill="#ef4444", stroke="#dc2626", sw=2))
    parts.append(text(x3 + 190, 274, "C", size=13, color="#ffffff", bold=True))

    parts.append(line(x3 + 48, 280, x3 + 28, 305, color="#64748b", sw=1.5))
    parts.append(line(x3 + 72, 280, x3 + 88, 305, color="#64748b", sw=1.5))
    parts.append(line(x3 + 178, 280, x3 + 162, 305, color="#64748b", sw=1.5))
    parts.append(line(x3 + 202, 280, x3 + 222, 305, color="#64748b", sw=1.5))
    parts.append(text(x3 + 28, 318, "T1", size=10, color="#64748b"))
    parts.append(text(x3 + 88, 318, "T2", size=10, color="#64748b"))
    parts.append(text(x3 + 162, 318, "T3", size=10, color="#64748b"))
    parts.append(text(x3 + 222, 318, "T4", size=10, color="#64748b"))
    parts.append(text(x3 + 125, 335, "1 чорний + 2 червоних", size=11, color="#b91c1c", bold=True))

    render(os.path.join(OUT, "rb-isomorphism.svg"), W, H, *parts)

if __name__ == "__main__":
    fig_node_types()
    fig_top_down_insertion()
    fig_top_down_deletion()
    fig_rb_isomorphism()
    print("All figures generated successfully.")
