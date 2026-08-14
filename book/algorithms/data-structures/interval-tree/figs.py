# -*- coding: utf-8 -*-
"""Фігури до статті «Інтервальне дерево».
Генерує векторні схеми SVG у теці ./img/:
1. interval-representation.svg — Набір 1D інтервалів на числовій осі та їх представлення у вигляді доповненого бінарного дерева.
2. interval-search-trace.svg — Покрокова трасування пошуку перетину для запиту Q = [21, 23].
3. interval-rotation-max.svg — Перерахунок атрибута max при повороті дерева (Left-Rotate).
4. centered-interval-tree.svg — Структура центрованого інтервального дерева Едельсбруннера з медіанним розбиттям.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
NODE_BG = "#e0f2fe"       # Світло-блакитний для звичайного вузла
NODE_BORDER = "#0284c7"   # Синій контур
TEXT_COLOR = "#0f172a"
MAX_COLOR = "#dc2626"     # Червоний для атрибута max
QUERY_BG = "#fef08a"      # Жовтий для запиту
QUERY_BORDER = "#ca8a04"
MATCH_BG = "#bbf7d0"      # Зелений для знайденого збігу
MATCH_BORDER = "#16a34a"
AXIS_COLOR = "#64748b"

def draw_node_box(cx, cy, interval_str, max_val, bg=NODE_BG, border=NODE_BORDER, w=140, h=48):
    x = cx - w / 2
    y = cy - h / 2
    res = [
        rect(x, y, w, h, fill=bg, stroke=border, sw=2, rx=6),
        text(cx, cy - 6, interval_str, size=13, color=TEXT_COLOR, bold=True),
        text(cx, cy + 14, f"max = {max_val}", size=11, color=MAX_COLOR, bold=True)
    ]
    return res

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Представлення інтервалів на осі та в дереві
# ─────────────────────────────────────────────────────────────────────────────
def fig_interval_representation(path):
    W, H = 840, 480
    parts = []
    
    parts.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(425, 34, "Представлення 1D-інтервалів у доповненому бінарному дереві пошуку", size=16, color=INK, bold=True))
    
    # 1. Верхня секція: Числова вісь
    parts.append(rect(25, 50, 790, 165, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    parts.append(text(425, 68, "Множина 1D-інтервалів на числовій прямій", size=13, color=MUTED, bold=True))
    
    # Осі
    axis_y = 190
    parts.append(line(50, axis_y, 790, axis_y, color=AXIS_COLOR, sw=2))
    for val in range(0, 45, 5):
        px = 70 + val * 17.0
        parts.append(line(px, axis_y - 5, px, axis_y + 5, color=AXIS_COLOR, sw=1.5))
        parts.append(text(px, axis_y + 18, str(val), size=11, color=MUTED))
        
    intervals_data = [
        ("[15, 20]", 15, 20, 85, "#3b82f6"),
        ("[10, 30]", 10, 30, 105, "#8b5cf6"),
        ("[17, 19]", 17, 19, 125, "#ec4899"),
        ("[5, 20]", 5, 20, 145, "#10b981"),
        ("[12, 15]", 12, 15, 165, "#f59e0b"),
        ("[30, 40]", 30, 40, 145, "#06b6d4"),
    ]
    
    for label, low, high, iy, col in intervals_data:
        x1 = 70 + low * 17.0
        x2 = 70 + high * 17.0
        parts.append(line(x1, iy, x2, iy, color=col, sw=4))
        parts.append(circle(x1, iy, 4, fill=col, stroke=col))
        parts.append(circle(x2, iy, 4, fill=col, stroke=col))
        parts.append(text((x1 + x2) / 2, iy - 6, label, size=11, color=col, bold=True))
        
    # 2. Нижня секція: Дерево
    cx_root, cy_root = 425, 255
    cx_l1_1, cy_l1_1 = 250, 335
    cx_l1_2, cy_l1_2 = 600, 335
    
    cx_l2_1, cy_l2_1 = 150, 420
    cx_l2_2, cy_l2_2 = 350, 420
    cx_l2_3, cy_l2_3 = 510, 420
    
    tree_lines = [
        (cx_root, cy_root, cx_l1_1, cy_l1_1),
        (cx_root, cy_root, cx_l1_2, cy_l1_2),
        (cx_l1_1, cy_l1_1, cx_l2_1, cy_l2_1),
        (cx_l1_1, cy_l1_1, cx_l2_2, cy_l2_2),
        (cx_l1_2, cy_l1_2, cx_l2_3, cy_l2_3),
    ]
    for lx1, ly1, lx2, ly2 in tree_lines:
        parts.append(line(lx1, ly1, lx2, ly2, color="#94a3b8", sw=2))
        
    parts.extend(draw_node_box(cx_root, cy_root, "[15, 20]", 40))
    parts.extend(draw_node_box(cx_l1_1, cy_l1_1, "[10, 30]", 30))
    parts.extend(draw_node_box(cx_l1_2, cy_l1_2, "[30, 40]", 40))
    
    parts.extend(draw_node_box(cx_l2_1, cy_l2_1, "[5, 20]", 20))
    parts.extend(draw_node_box(cx_l2_2, cy_l2_2, "[12, 15]", 15))
    parts.extend(draw_node_box(cx_l2_3, cy_l2_3, "[17, 19]", 19))
    
    render(path, W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Трасування пошуку перетину для Q = [21, 23]
# ─────────────────────────────────────────────────────────────────────────────
def fig_interval_search_trace(path):
    W, H = 840, 460
    parts = []
    
    parts.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(425, 34, "Покрокова трасування пошуку перетину для Q = [21, 23]", size=16, color=INK, bold=True))
    
    parts.append(rect(25, 50, 790, 50, fill=QUERY_BG, stroke=QUERY_BORDER, sw=1.5, rx=6))
    parts.append(text(425, 72, "Запит Q = [21, 23] | q_low = 21, q_high = 23", size=14, color="#854d0e", bold=True))

    cx_root, cy_root = 425, 140
    cx_l1_1, cy_l1_1 = 250, 240
    cx_l1_2, cy_l1_2 = 600, 240
    cx_l2_1, cy_l2_1 = 150, 340
    cx_l2_2, cy_l2_2 = 350, 340
    cx_l2_3, cy_l2_3 = 510, 340

    parts.append(line(cx_root, cy_root, cx_l1_1, cy_l1_1, color="#2563eb", sw=3.5))
    parts.append(line(cx_root, cy_root, cx_l1_2, cy_l1_2, color="#cbd5e1", sw=1.5))
    parts.append(line(cx_l1_1, cy_l1_1, cx_l2_1, cy_l2_1, color="#cbd5e1", sw=1.5))
    parts.append(line(cx_l1_1, cy_l1_1, cx_l2_2, cy_l2_2, color="#cbd5e1", sw=1.5))
    parts.append(line(cx_l1_2, cy_l1_2, cx_l2_3, cy_l2_3, color="#cbd5e1", sw=1.5))

    parts.extend(draw_node_box(cx_root, cy_root, "[15, 20]", 40, bg="#dbeafe", border="#2563eb"))
    parts.append(rect(520, 120, 270, 42, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(655, 137, "Крок 1: [15,20] не перетинає [21,23]", size=11, color="#1e40af"))
    parts.append(text(655, 153, "left.max (30) ≥ q_low (21) → ЛІВОРУЧ", size=11, color="#1e40af", bold=True))
    parts.append(arrow(515, 140, cx_root + 75, cy_root, color="#2563eb", sw=1.5))

    parts.extend(draw_node_box(cx_l1_1, cy_l1_1, "[10, 30]", 30, bg=MATCH_BG, border=MATCH_BORDER))
    parts.append(rect(25, 220, 145, 48, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(97, 240, "Крок 2: [10, 30]", size=12, color="#15803d", bold=True))
    parts.append(text(97, 257, "ПЕРЕТИН ЗНАЙДЕНО!", size=10, color="#15803d", bold=True))
    parts.append(arrow(172, 240, cx_l1_1 - 75, cy_l1_1, color="#16a34a", sw=1.5))

    parts.extend(draw_node_box(cx_l1_2, cy_l1_2, "[30, 40]", 40, bg="#f1f5f9", border="#94a3b8"))
    parts.extend(draw_node_box(cx_l2_1, cy_l2_1, "[5, 20]", 20, bg="#f1f5f9", border="#94a3b8"))
    parts.extend(draw_node_box(cx_l2_2, cy_l2_2, "[12, 15]", 15, bg="#f1f5f9", border="#94a3b8"))
    parts.extend(draw_node_box(cx_l2_3, cy_l2_3, "[17, 19]", 19, bg="#f1f5f9", border="#94a3b8"))

    parts.append(rect(25, 395, 790, 35, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    parts.append(text(425, 417, "Теорема гарантує: якщо left.max ≥ q_low, перетинаючий інтервал ОБОВ'ЯЗКОВО існує в лівому піддереві.", size=12, color=INK))

    render(path, W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Перерахунок max при повороті дерева (Left-Rotate)
# ─────────────────────────────────────────────────────────────────────────────
def fig_interval_rotation_max(path):
    W, H = 840, 420
    parts = []
    
    parts.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(425, 34, "Підтримання інваріанта max при виконанні повороту Left-Rotate(X)", size=16, color=INK, bold=True))
    
    parts.append(text(220, 70, "До повороту (X — батько, Y — правий син)", size=13, color=MUTED, bold=True))
    
    cx_x1, cy_x1 = 180, 120
    cx_y1, cy_y1 = 280, 200
    cx_a1, cy_a1 = 100, 200
    cx_b1, cy_b1 = 220, 290
    cx_c1, cy_c1 = 340, 290
    
    lines1 = [
        (cx_x1, cy_x1, cx_a1, cy_a1),
        (cx_x1, cy_x1, cx_y1, cy_y1),
        (cx_y1, cy_y1, cx_b1, cy_b1),
        (cx_y1, cy_y1, cx_c1, cy_c1),
    ]
    for lx1, ly1, lx2, ly2 in lines1:
        parts.append(line(lx1, ly1, lx2, ly2, color="#94a3b8", sw=2))
        
    parts.extend(draw_node_box(cx_x1, cy_x1, "Вузол X", "max(X)", bg="#dbeafe", border="#2563eb", w=110, h=44))
    parts.extend(draw_node_box(cx_y1, cy_y1, "Вузол Y", "max(Y)", bg="#fef3c7", border="#d97706", w=110, h=44))
    parts.extend(draw_node_box(cx_a1, cy_a1, "Піддерево α", "max(α)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))
    parts.extend(draw_node_box(cx_b1, cy_b1, "Піддерево β", "max(β)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))
    parts.extend(draw_node_box(cx_c1, cy_c1, "Піддерево γ", "max(γ)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))
    
    parts.append(arrow(380, 190, 460, 190, color="#059669", sw=3))
    parts.append(text(420, 175, "Left-Rotate(X)", size=12, color="#059669", bold=True))
    
    parts.append(text(640, 70, "Після повороту (Y — корінь, X — лівий син)", size=13, color=MUTED, bold=True))
    
    cx_y2, cy_y2 = 640, 120
    cx_x2, cy_x2 = 540, 200
    cx_c2, cy_c2 = 740, 200
    cx_a2, cy_a2 = 480, 290
    cx_b2, cy_b2 = 600, 290
    
    lines2 = [
        (cx_y2, cy_y2, cx_x2, cy_x2),
        (cx_y2, cy_y2, cx_c2, cy_c2),
        (cx_x2, cy_x2, cx_a2, cy_a2),
        (cx_x2, cy_x2, cx_b2, cy_b2),
    ]
    for lx1, ly1, lx2, ly2 in lines2:
        parts.append(line(lx1, ly1, lx2, ly2, color="#94a3b8", sw=2))
        
    parts.extend(draw_node_box(cx_y2, cy_y2, "Вузол Y", "нов. max(Y)", bg="#fef3c7", border="#d97706", w=110, h=44))
    parts.extend(draw_node_box(cx_x2, cy_x2, "Вузол X", "нов. max(X)", bg="#dbeafe", border="#2563eb", w=110, h=44))
    parts.extend(draw_node_box(cx_c2, cy_c2, "Піддерево γ", "max(γ)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))
    parts.extend(draw_node_box(cx_a2, cy_a2, "Піддерево α", "max(α)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))
    parts.extend(draw_node_box(cx_b2, cy_b2, "Піддерево β", "max(β)", bg="#f1f5f9", border="#94a3b8", w=100, h=40))

    parts.append(rect(25, 345, 790, 50, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(425, 365, "Кроки перерахунку в O(1): 1. X.max = max(X.high, α.max, β.max)", size=12, color=INK, bold=True))
    parts.append(text(425, 383, "2. Y.max = max(Y.high, X.max, γ.max) — порядок перерахунку знизу вгору!", size=12, color=MAX_COLOR, bold=True))

    render(path, W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Центроване інтервальне дерево Едельсбруннера
# ─────────────────────────────────────────────────────────────────────────────
def fig_centered_interval_tree(path):
    W, H = 840, 440
    parts = []
    
    parts.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(425, 34, "Структура вузла у центрованому інтервальному дереві Едельсбруннера", size=16, color=INK, bold=True))
    
    cx, cy = 425, 140
    parts.append(rect(220, 70, 410, 140, fill="#f0f9ff", stroke="#0284c7", sw=2, rx=8))
    parts.append(text(cx, 93, "Вузол з медіаною x_mid", size=14, color="#0369a1", bold=True))
    
    parts.append(line(cx, 110, cx, 200, color="#e11d48", sw=2, dash="4,4"))
    parts.append(text(cx, 205, "x_mid", size=11, color="#e11d48", bold=True))
    
    parts.append(rect(235, 115, 170, 70, fill="#ffffff", stroke="#38bdf8", sw=1, rx=4))
    parts.append(text(320, 133, "Список A_L", size=12, color=INK, bold=True))
    parts.append(text(320, 152, "Інтервали, що перетинають x_mid", size=10, color=MUTED))
    parts.append(text(320, 168, "сорт. за low (зростання)", size=10, color="#0369a1", bold=True))

    parts.append(rect(445, 115, 170, 70, fill="#ffffff", stroke="#38bdf8", sw=1, rx=4))
    parts.append(text(530, 133, "Список A_R", size=12, color=INK, bold=True))
    parts.append(text(530, 152, "Інтервали, що перетинають x_mid", size=10, color=MUTED))
    parts.append(text(530, 168, "сорт. за high (спадання)", size=10, color="#0369a1", bold=True))

    cx_left, cy_left = 220, 310
    cx_right, cy_right = 630, 310
    
    parts.append(line(310, 210, cx_left, cy_left - 30, color="#64748b", sw=2))
    parts.append(line(540, 210, cx_right, cy_right - 30, color="#64748b", sw=2))

    parts.append(rect(cx_left - 130, cy_left - 30, 260, 100, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(cx_left, cy_left - 10, "Ліве піддерево (Left Subtree)", size=13, color=INK, bold=True))
    parts.append(text(cx_left, cy_left + 12, "Містить лише ті інтервали,", size=11, color=MUTED))
    parts.append(text(cx_left, cy_left + 30, "які строго ЛІВОРУЧ від x_mid (high < x_mid)", size=11, color="#0f172a"))

    parts.append(rect(cx_right - 130, cy_right - 30, 260, 100, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(cx_right, cy_right - 10, "Праве піддерево (Right Subtree)", size=13, color=INK, bold=True))
    parts.append(text(cx_right, cy_right + 12, "Містить лише ті інтервали,", size=11, color=MUTED))
    parts.append(text(cx_right, cy_right + 30, "які строго ПРАВОРУЧ від x_mid (low > x_mid)", size=11, color="#0f172a"))

    parts.append(rect(25, 385, 790, 30, fill="#eff6ff", stroke="#bfdbfe", sw=1, rx=4))
    parts.append(text(425, 404, "Забезпечує гарантований O(k + log n) пошук усіх k перетинів у станійних / напівдинамічних задачах.", size=11, color="#1e40af"))

    render(path, W, H, *parts)


def main():
    generators = [
        ("interval-representation.svg", fig_interval_representation),
        ("interval-search-trace.svg", fig_interval_search_trace),
        ("interval-rotation-max.svg", fig_interval_rotation_max),
        ("centered-interval-tree.svg", fig_centered_interval_tree),
    ]
    for fname, func in generators:
        path = os.path.join(OUT, fname)
        func(path)
        print(f"Згенеровано: {path}")

if __name__ == "__main__":
    main()
