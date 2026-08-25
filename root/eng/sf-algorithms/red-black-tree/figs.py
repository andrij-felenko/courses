# -*- coding: utf-8 -*-
"""Фігури до статті «Червоно-чорне дерево».
Генерує векторні схеми SVG у теці ./img/:
1. rb-properties.svg — Анатомія та інваріанти червоно-чорного дерева (із NIL-листками та чорною висотою).
2. rb-vs-234.svg — Еквівалентність між 2-3-4 деревом та червоно-чорним бінарним деревом.
3. rb-rotations.svg — Операції лівого та правого повороту (Left-Rotate / Right-Rotate).
4. rb-insert-cases.svg — Випадки балансування при вставці (перефарбування та повороти).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
BLACK_NODE_BG = "#1e293b" # Темно-сірий / чорний для чорних вузлів
BLACK_NODE_TEXT = "#ffffff"
RED_NODE_BG = "#dc2626"   # Яскраво-червоний для червоних вузлів
RED_NODE_TEXT = "#ffffff"
NIL_NODE_BG = "#64748b"   # Сірий для NIL листків
NIL_NODE_TEXT = "#ffffff"

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def node_circle(x, y, val, is_red=False, r=22):
    bg = RED_NODE_BG if is_red else BLACK_NODE_BG
    fg = RED_NODE_TEXT if is_red else BLACK_NODE_TEXT
    stroke_c = "#991b1b" if is_red else "#0f172a"
    res = [
        circle(x, y, r, fill=bg, stroke=stroke_c, sw=2),
        text(x, y + 5, str(val), size=14, color=fg, bold=True)
    ]
    return res

def nil_node(x, y, size=24):
    res = [
        rect(x - size/2, y - size/2, size, size, fill=NIL_NODE_BG, stroke="#334155", sw=1.5, rx=3),
        text(x, y + 4, "NIL", size=10, color=NIL_NODE_TEXT, bold=True)
    ]
    return res

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Анатомія та інваріанти червоно-чорного дерева
# ─────────────────────────────────────────────────────────────────────────────
def fig_rb_properties():
    W, H = 820, 440
    parts = []
    
    parts.append(rect(10, 10, 800, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 36, "Анатомія та 5 інваріантів червоно-чорного дерева", size=16, color=INK, bold=True))
    
    # Ліва частина: дерево
    # Корінь (чорний) 30
    x_root, y_root = 260, 85
    # L1: 15 (червоний), 45 (червоний)
    x_15, y_15 = 150, 160
    x_45, y_45 = 370, 160
    # L2 від 15: 10 (чорний), 20 (чорний)
    x_10, y_10 = 90, 245
    x_20, y_20 = 210, 245
    # L2 від 45: NIL, 50 (чорний)
    x_45_nil, y_45_nil = 320, 245
    x_50, y_50 = 420, 245
    
    # L3 NILs від 10
    x_10_l, y_10_l = 65, 320
    x_10_r, y_10_r = 115, 320
    # L3 NILs від 20
    x_20_l, y_20_l = 185, 320
    x_20_r, y_20_r = 235, 320
    # L3 NILs від 50
    x_50_l, y_50_l = 395, 320
    x_50_r, y_50_r = 445, 320
    
    # Зв'язки
    lines = [
        (x_root, y_root, x_15, y_15), (x_root, y_root, x_45, y_45),
        (x_15, y_15, x_10, y_10), (x_15, y_15, x_20, y_20),
        (x_45, y_45, x_45_nil, y_45_nil), (x_45, y_45, x_50, y_50),
        (x_10, y_10, x_10_l, y_10_l), (x_10, y_10, x_10_r, y_10_r),
        (x_20, y_20, x_20_l, y_20_l), (x_20, y_20, x_20_r, y_20_r),
        (x_50, y_50, x_50_l, y_50_l), (x_50, y_50, x_50_r, y_50_r),
    ]
    for lx1, ly1, lx2, ly2 in lines:
        parts.append(line(lx1, ly1, lx2, ly2, color="#94a3b8", sw=2))
        
    # Намалювати вузли
    parts.extend(node_circle(x_root, y_root, "30", is_red=False))
    parts.extend(node_circle(x_15, y_15, "15", is_red=True))
    parts.extend(node_circle(x_45, y_45, "45", is_red=True))
    
    parts.extend(node_circle(x_10, y_10, "10", is_red=False))
    parts.extend(node_circle(x_20, y_20, "20", is_red=False))
    parts.extend(nil_node(x_45_nil, y_45_nil))
    parts.extend(node_circle(x_50, y_50, "50", is_red=False))
    
    parts.extend(nil_node(x_10_l, y_10_l))
    parts.extend(nil_node(x_10_r, y_10_r))
    parts.extend(nil_node(x_20_l, y_20_l))
    parts.extend(nil_node(x_20_r, y_20_r))
    parts.extend(nil_node(x_50_l, y_50_l))
    parts.extend(nil_node(x_50_r, y_50_r))
    
    # Шлях та чорна висота
    parts.append(text(260, 375, "Чорна висота bh(корінь) = 2", size=13, color="#0f172a", bold=True))
    parts.append(text(260, 395, "(Усі шляхи до NIL мають рівно 2 чорні вузли)", size=11, color="#64748b"))
    
    # Права частина: Панель інваріантів
    px = 490
    parts.append(rect(px, 70, 305, 335, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    parts.append(text(px + 150, 95, "5 фундаментальних інваріантів:", size=13, color=INK, bold=True))
    
    rules = [
        ("1. Колір вузла", "Кожен вузол є або червоним, або чорним."),
        ("2. Інваріант кореня", "Корінь дерева завжди є чорним."),
        ("3. Інваріант листків", "Усі листки (NIL-вказівники) є чорними."),
        ("4. Червоний інваріант", "Червоний вузол має лише чорних дітей\n(немає двох червоних вузлів поспіль)."),
        ("5. Чорна висота", "Усі шляхи від вузла до будь-якого його\nлистка містять однакову кількість чорних.")
    ]
    
    ry = 125
    for title, desc in rules:
        parts.append(text(px + 15, ry, title, size=12, color="#b91c1c" if "Червоний" in title else "#0f172a", bold=True, anchor="start"))
        lines_desc = desc.split("\n")
        for ld in lines_desc:
            ry += 16
            parts.append(text(px + 15, ry, ld, size=11, color="#475569", anchor="start"))
        ry += 22

    render(os.path.join(OUT, "rb-properties.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Еквівалентність 2-3-4 дерева та червоно-чорного дерева
# ─────────────────────────────────────────────────────────────────────────────
def fig_rb_vs_234():
    W, H = 820, 380
    parts = []
    
    parts.append(rect(10, 10, 800, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 35, "Еквівалентність вузлів 2-3-4 дерева та червоно-чорних зв'язків", size=16, color=INK, bold=True))
    
    # Рядок 1: 2-вузол
    y1 = 80
    parts.append(text(80, y1 + 25, "2-вузол:", size=13, color=INK, bold=True, anchor="start"))
    # 2-3-4 репрезентація
    parts.append(rect(180, y1, 60, 40, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    parts.append(text(210, y1 + 25, "B", size=14, color=INK, bold=True))
    # Стрілка
    parts.append(line(270, y1 + 20, 340, y1 + 20, color="#94a3b8", sw=2))
    parts.append(text(305, y1 + 12, "≡", size=16, color="#64748b"))
    # RB репрезентація
    parts.extend(node_circle(400, y1 + 20, "B", is_red=False, r=18))
    parts.append(text(460, y1 + 25, "1 чорний вузол", size=12, color="#64748b", anchor="start"))
    
    # Рядок 2: 3-вузол
    y2 = 160
    parts.append(text(80, y2 + 25, "3-вузол:", size=13, color=INK, bold=True, anchor="start"))
    # 2-3-4 репрезентація
    parts.append(rect(170, y2, 100, 40, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    parts.append(line(220, y2, 220, y2 + 40, color="#475569", sw=1.5))
    parts.append(text(195, y2 + 25, "A", size=14, color=INK, bold=True))
    parts.append(text(245, y2 + 25, "B", size=14, color=INK, bold=True))
    # Стрілка
    parts.append(line(285, y2 + 20, 345, y2 + 20, color="#94a3b8", sw=2))
    parts.append(text(315, y2 + 12, "≡", size=16, color="#64748b"))
    # RB репрезентація (A або B червоний)
    parts.append(line(420, y2 + 10, 390, y2 + 35, color="#dc2626", sw=2.5))
    parts.extend(node_circle(420, y2 + 10, "B", is_red=False, r=16))
    parts.extend(node_circle(390, y2 + 35, "A", is_red=True, r=16))
    parts.append(text(460, y2 + 25, "Чорний батьківський + 1 червоний дитина (ліва або права)", size=12, color="#64748b", anchor="start"))

    # Рядок 3: 4-вузол
    y3 = 260
    parts.append(text(80, y3 + 25, "4-вузол:", size=13, color=INK, bold=True, anchor="start"))
    # 2-3-4 репрезентація
    parts.append(rect(150, y3, 140, 40, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    parts.append(line(196, y3, 196, y3 + 40, color="#475569", sw=1.5))
    parts.append(line(243, y3, 243, y3 + 40, color="#475569", sw=1.5))
    parts.append(text(173, y3 + 25, "A", size=14, color=INK, bold=True))
    parts.append(text(220, y3 + 25, "B", size=14, color=INK, bold=True))
    parts.append(text(266, y3 + 25, "C", size=14, color=INK, bold=True))
    # Стрілка
    parts.append(line(305, y3 + 20, 355, y3 + 20, color="#94a3b8", sw=2))
    parts.append(text(330, y3 + 12, "≡", size=16, color="#64748b"))
    # RB репрезентація
    parts.append(line(420, y3 + 5, 385, y3 + 35, color="#dc2626", sw=2.5))
    parts.append(line(420, y3 + 5, 455, y3 + 35, color="#dc2626", sw=2.5))
    parts.extend(node_circle(420, y3 + 5, "B", is_red=False, r=16))
    parts.extend(node_circle(385, y3 + 35, "A", is_red=True, r=16))
    parts.extend(node_circle(455, y3 + 35, "C", is_red=True, r=16))
    parts.append(text(490, y3 + 25, "Чорний батьківський + 2 червоні дитини", size=12, color="#64748b", anchor="start"))
    
    render(os.path.join(OUT, "rb-vs-234.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Базові повороти (Left-Rotate / Right-Rotate)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rb_rotations():
    W, H = 820, 340
    parts = []
    
    parts.append(rect(10, 10, 800, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 35, "Базові локальні трансформації: Лівий та Правий повороти", size=16, color=INK, bold=True))
    
    # Зліва: Стан до Лівого повороту (після Правого)
    x_x, y_x = 180, 85
    x_y, y_y = 250, 150
    x_a, y_a = 120, 220
    x_b, y_b = 200, 220
    x_c, y_c = 290, 220
    
    # Зв'язки ліворуч
    parts.append(line(x_x, y_x, x_y, y_y, color="#475569", sw=2))
    parts.append(line(x_x, y_x, x_a, y_a, color="#94a3b8", sw=1.5))
    parts.append(line(x_y, y_y, x_b, y_b, color="#94a3b8", sw=1.5))
    parts.append(line(x_y, y_y, x_c, y_c, color="#94a3b8", sw=1.5))
    
    parts.extend(node_circle(x_x, y_x, "X", is_red=False, r=20))
    parts.extend(node_circle(x_y, y_y, "Y", is_red=True, r=20))
    
    # Трикутники піддерев A, B, C
    def sub_triangle(cx, cy, label):
        return [
            polygon([(cx, cy), (cx - 25, cy + 40), (cx + 25, cy + 40)], fill="#f1f5f9", stroke="#94a3b8", sw=1.5),
            text(cx, cy + 26, label, size=13, color="#475569", bold=True)
        ]
        
    parts.extend(sub_triangle(x_a, y_a, "α"))
    parts.extend(sub_triangle(x_b, y_b, "β"))
    parts.extend(sub_triangle(x_c, y_c, "γ"))
    
    # Центр: Стрілки Left-Rotate / Right-Rotate
    parts.append(line(340, 115, 470, 115, color="#2563eb", sw=2.5))
    parts.append(polygon([(470, 115), (460, 109), (460, 121)], fill="#2563eb", stroke="#2563eb", sw=1))
    parts.append(text(405, 100, "Left-Rotate(X)", size=12, color="#2563eb", bold=True))
    
    parts.append(line(470, 175, 340, 175, color="#059669", sw=2.5))
    parts.append(polygon([(340, 175), (350, 169), (350, 181)], fill="#059669", stroke="#059669", sw=1))
    parts.append(text(405, 195, "Right-Rotate(Y)", size=12, color="#059669", bold=True))

    # Справа: Стан після Лівого повороту
    rx_y, ry_y = 620, 85
    rx_x, ry_x = 550, 150
    rx_a, ry_a = 500, 220
    rx_b, ry_b = 590, 220
    rx_c, ry_c = 670, 220
    
    # Зв'язки праворуч
    parts.append(line(rx_y, ry_y, rx_x, ry_x, color="#475569", sw=2))
    parts.append(line(rx_x, ry_x, rx_a, ry_a, color="#94a3b8", sw=1.5))
    parts.append(line(rx_x, ry_x, rx_b, ry_b, color="#94a3b8", sw=1.5))
    parts.append(line(rx_y, ry_y, rx_c, ry_c, color="#94a3b8", sw=1.5))
    
    parts.extend(node_circle(rx_y, ry_y, "Y", is_red=True, r=20))
    parts.extend(node_circle(rx_x, ry_x, "X", is_red=False, r=20))
    
    parts.extend(sub_triangle(rx_a, ry_a, "α"))
    parts.extend(sub_triangle(rx_b, ry_b, "β"))
    parts.extend(sub_triangle(rx_c, ry_c, "γ"))
    
    parts.append(text(410, 290, "Піддерево β змінює батьківського вузла з Y на X, зберігаючи порядок BST: α < X < β < Y < γ", size=12, color="#475569"))

    render(os.path.join(OUT, "rb-rotations.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Випадки балансування при вставці (Insert Fixup)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rb_insert_cases():
    W, H = 820, 520
    parts = []
    
    parts.append(rect(10, 10, 800, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 35, "Відновлення інваріантів після вставки нової червоної вершини N", size=16, color=INK, bold=True))
    
    # Панель 1: Випадок 1 — Дядько U є червоним (Перефарбування)
    y1 = 60
    parts.append(rect(25, y1, 770, 130, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    parts.append(text(40, y1 + 22, "Випадок 1: Дядько U червоний (Red Uncle) → Перефарбування (Recoloring)", size=13, color=INK, bold=True, anchor="start"))
    
    # До
    parts.append(text(120, y1 + 45, "До балансування:", size=11, color="#64748b"))
    parts.append(line(120, y1 + 60, 90, y1 + 85, color="#dc2626", sw=2))
    parts.append(line(120, y1 + 60, 150, y1 + 85, color="#dc2626", sw=2))
    parts.append(line(90, y1 + 85, 70, y1 + 110, color="#dc2626", sw=2))
    parts.extend(node_circle(120, y1 + 60, "G", is_red=False, r=14))
    parts.extend(node_circle(90, y1 + 85, "P", is_red=True, r=14))
    parts.extend(node_circle(150, y1 + 85, "U", is_red=True, r=14))
    parts.extend(node_circle(70, y1 + 110, "N", is_red=True, r=14))
    
    # Стрілка
    parts.append(line(200, y1 + 80, 270, y1 + 80, color="#2563eb", sw=2))
    parts.append(polygon([(270, y1 + 80), (260, y1 + 75), (260, y1 + 85)], fill="#2563eb", stroke="#2563eb", sw=1))
    parts.append(text(235, y1 + 70, "Recolor", size=11, color="#2563eb", bold=True))

    # Після
    parts.append(text(350, y1 + 45, "Після перефарбування:", size=11, color="#64748b"))
    parts.append(line(350, y1 + 60, 320, y1 + 85, color="#475569", sw=2))
    parts.append(line(350, y1 + 60, 380, y1 + 85, color="#475569", sw=2))
    parts.append(line(320, y1 + 85, 300, y1 + 110, color="#dc2626", sw=2))
    parts.extend(node_circle(350, y1 + 60, "G", is_red=True, r=14))
    parts.extend(node_circle(320, y1 + 85, "P", is_red=False, r=14))
    parts.extend(node_circle(380, y1 + 85, "U", is_red=False, r=14))
    parts.extend(node_circle(300, y1 + 110, "N", is_red=True, r=14))

    parts.append(text(450, y1 + 65, "P та U стають чорними, G стає червоним.", size=11, color="#334155", anchor="start"))
    parts.append(text(450, y1 + 85, "Конфлікт переноситься на рівень G (перевірка вище).", size=11, color="#64748b", anchor="start"))

    # Панель 2: Випадок 2 — Дядько U чорний, Zig-Zag (Внутрішній племінник)
    y2 = 205
    parts.append(rect(25, y2, 770, 140, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    parts.append(text(40, y2 + 22, "Випадок 2: Дядько U чорний, N — внутрішній племінник (Zig-Zag) → Поворот навколо P", size=13, color=INK, bold=True, anchor="start"))
    
    # До
    parts.append(text(120, y2 + 45, "До повороту P:", size=11, color="#64748b"))
    parts.append(line(120, y2 + 60, 90, y2 + 85, color="#dc2626", sw=2))
    parts.append(line(120, y2 + 60, 150, y2 + 85, color="#475569", sw=2))
    parts.append(line(90, y2 + 85, 110, y2 + 115, color="#dc2626", sw=2))
    parts.extend(node_circle(120, y2 + 60, "G", is_red=False, r=14))
    parts.extend(node_circle(90, y2 + 85, "P", is_red=True, r=14))
    parts.extend(node_circle(150, y2 + 85, "U", is_red=False, r=14))
    parts.extend(node_circle(110, y2 + 115, "N", is_red=True, r=14))
    
    # Стрілка
    parts.append(line(200, y2 + 85, 270, y2 + 85, color="#2563eb", sw=2))
    parts.append(polygon([(270, y2 + 85), (260, y2 + 80), (260, y2 + 90)], fill="#2563eb", stroke="#2563eb", sw=1))
    parts.append(text(235, y2 + 75, "Left-Rotate(P)", size=11, color="#2563eb", bold=True))

    # Після
    parts.append(text(350, y2 + 45, "Зведення до Випадку 3 (Line):", size=11, color="#64748b"))
    parts.append(line(350, y2 + 60, 330, y2 + 85, color="#dc2626", sw=2))
    parts.append(line(350, y2 + 60, 380, y2 + 85, color="#475569", sw=2))
    parts.append(line(330, y2 + 85, 310, y2 + 115, color="#dc2626", sw=2))
    parts.extend(node_circle(350, y2 + 60, "G", is_red=False, r=14))
    parts.extend(node_circle(330, y2 + 85, "N", is_red=True, r=14))
    parts.extend(node_circle(380, y2 + 85, "U", is_red=False, r=14))
    parts.extend(node_circle(310, y2 + 115, "P", is_red=True, r=14))

    parts.append(text(460, y2 + 65, "Поворот змінює ролі P та N.", size=11, color="#334155", anchor="start"))
    parts.append(text(460, y2 + 85, "Тепер N і P утворюють пряму лінію (Case 3).", size=11, color="#64748b", anchor="start"))

    # Панель 3: Випадок 3 — Дядько U чорний, Line (Зовнішній племінник)
    y3 = 360
    parts.append(rect(25, y3, 770, 140, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    parts.append(text(40, y3 + 22, "Випадок 3: Дядько U чорний, N — зовнішній племінник (Line) → Поворот G + Перефарбування", size=13, color=INK, bold=True, anchor="start"))
    
    # До
    parts.append(text(120, y3 + 45, "До повороту G:", size=11, color="#64748b"))
    parts.append(line(120, y3 + 60, 90, y3 + 85, color="#dc2626", sw=2))
    parts.append(line(120, y3 + 60, 150, y3 + 85, color="#475569", sw=2))
    parts.append(line(90, y3 + 85, 70, y3 + 115, color="#dc2626", sw=2))
    parts.extend(node_circle(120, y3 + 60, "G", is_red=False, r=14))
    parts.extend(node_circle(90, y3 + 85, "P", is_red=True, r=14))
    parts.extend(node_circle(150, y3 + 85, "U", is_red=False, r=14))
    parts.extend(node_circle(70, y3 + 115, "N", is_red=True, r=14))
    
    # Стрілка
    parts.append(line(200, y3 + 85, 270, y3 + 85, color="#059669", sw=2))
    parts.append(polygon([(270, y3 + 85), (260, y3 + 80), (260, y3 + 90)], fill="#059669", stroke="#059669", sw=1))
    parts.append(text(235, y3 + 70, "Right-Rotate(G)", size=11, color="#059669", bold=True))
    parts.append(text(235, y3 + 100, "+ Recolor", size=11, color="#059669", bold=True))

    # Після
    parts.append(text(350, y3 + 45, "Фінальний збалансований стан:", size=11, color="#64748b"))
    parts.append(line(350, y3 + 60, 320, y3 + 85, color="#dc2626", sw=2))
    parts.append(line(350, y3 + 60, 380, y3 + 85, color="#dc2626", sw=2))
    parts.extend(node_circle(350, y3 + 60, "P", is_red=False, r=14))
    parts.extend(node_circle(320, y3 + 85, "N", is_red=True, r=14))
    parts.extend(node_circle(380, y3 + 85, "G", is_red=True, r=14))

    parts.append(text(460, y3 + 65, "P стає чорним коренем піддерева,", size=11, color="#334155", anchor="start"))
    parts.append(text(460, y3 + 85, "G та N — його червоними дітьми. Дерево повністю збалансоване!", size=11, color="#059669", bold=True, anchor="start"))

    render(os.path.join(OUT, "rb-insert-cases.svg"), W, H, *parts)

if __name__ == "__main__":
    fig_rb_properties()
    fig_rb_vs_234()
    fig_rb_rotations()
    fig_rb_insert_cases()
    print("Фігури успішно згенеровано.")
