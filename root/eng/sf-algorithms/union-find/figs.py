# -*- coding: utf-8 -*-
"""Фігури до статті «Система неперетинних множин (union-find)».
Генерує SVG-діаграми для пояснення структур дерев DSU, стиснення шляхів,
функції Аккермана та стеку відкоту (Rollback DSU).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT_BLUE  = "#2457d6"
ACCENT_GREEN = FIELD
ACCENT_RED   = POS
FILL_CARD    = "#f8fafc"
STROKE_CARD  = "#cbd5e1"
FILL_ROOT    = "#e0f2fe"
STROKE_ROOT  = "#0284c7"
FILL_NODE    = "#f1f5f9"
STROKE_NODE  = "#64748b"
FILL_HIGHLIGHT = "#fef3c7"
STROKE_HIGHLIGHT = "#d97706"


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — Структура лісу дерев DSU (Quick-Union та Union by Rank)
# ─────────────────────────────────────────────────────────────────────────────
def fig_dsu_tree_structure():
    W, H = 840, 400
    p = []

    # Фон
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Множина A (Корінь 0)
    p.append(text(210, 40, "Множина A (Представник = 0)", size=16, color=STROKE_ROOT, bold=True))
    
    # Вузли дерев множини A
    p.append(circle(210, 100, 24, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2.5))
    p.append(text(210, 106, "0", size=16, color=STROKE_ROOT, bold=True))

    p.append(circle(140, 200, 22, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(140, 206, "1", size=15, color=INK, bold=True))

    p.append(circle(280, 200, 22, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(280, 206, "2", size=15, color=INK, bold=True))

    p.append(circle(90, 300, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=1.5))
    p.append(text(90, 305, "3", size=14, color=INK))

    p.append(circle(190, 300, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=1.5))
    p.append(text(190, 305, "4", size=14, color=INK))

    # Стрілки батьківських покажчиків parent[i] -> root
    p.append(arrow(140, 178, 195, 118, color=STROKE_NODE, sw=2))
    p.append(arrow(280, 178, 225, 118, color=STROKE_NODE, sw=2))
    p.append(arrow(90, 280, 130, 220, color=STROKE_NODE, sw=1.5))
    p.append(arrow(190, 280, 150, 220, color=STROKE_NODE, sw=1.5))

    p.append(text(210, 355, "Покажчик parent[i] спрямований догори до батька", size=13, color=MUTED, italic=True))

    # Перегородка
    p.append(line(420, 30, 420, 370, color=STROKE_CARD, sw=1.5, dash="4,4"))

    # Множина B (Корінь 5)
    p.append(text(630, 40, "Множина B (Представник = 5)", size=16, color=STROKE_ROOT, bold=True))

    p.append(circle(630, 100, 24, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2.5))
    p.append(text(630, 106, "5", size=16, color=STROKE_ROOT, bold=True))

    p.append(circle(570, 200, 22, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(570, 206, "6", size=15, color=INK, bold=True))

    p.append(circle(690, 200, 22, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(690, 206, "7", size=15, color=INK, bold=True))

    p.append(arrow(570, 178, 615, 118, color=STROKE_NODE, sw=2))
    p.append(arrow(690, 178, 645, 118, color=STROKE_NODE, sw=2))

    # Операція union(0, 5)
    p.append(arrow(460, 100, 595, 100, color=ACCENT_RED, sw=2.5))
    p.append(text(530, 85, "union: parent[5] = 0", size=13, color=ACCENT_RED, bold=True))

    p.append(text(630, 355, "Ранг(0) >= Ранг(5) ⇒ корінь 5 підпорядковується 0", size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "dsu-tree-structure.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — Стиснення шляху (Path Compression)
# ─────────────────────────────────────────────────────────────────────────────
def fig_path_compression():
    W, H = 840, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(200, 40, "До find(4): Глибоке дерево", size=16, color=STROKE_HIGHLIGHT, bold=True))

    p.append(circle(200, 90, 22, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2.5))
    p.append(text(200, 95, "0", size=15, color=STROKE_ROOT, bold=True))

    p.append(circle(200, 165, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(200, 170, "1", size=14, color=INK))

    p.append(circle(200, 240, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(200, 245, "2", size=14, color=INK))

    p.append(circle(200, 315, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(200, 320, "3", size=14, color=INK))

    p.append(circle(200, 380, 20, fill=FILL_HIGHLIGHT, stroke=STROKE_HIGHLIGHT, sw=2.5))
    p.append(text(200, 385, "4", size=14, color=STROKE_HIGHLIGHT, bold=True))

    p.append(arrow(200, 360, 200, 335, color=STROKE_NODE, sw=2))
    p.append(arrow(200, 295, 200, 260, color=STROKE_NODE, sw=2))
    p.append(arrow(200, 220, 200, 185, color=STROKE_NODE, sw=2))
    p.append(arrow(200, 145, 200, 112, color=STROKE_NODE, sw=2))

    p.append(arrow(340, 210, 480, 210, color=ACCENT_GREEN, sw=3))
    p.append(text(410, 195, "find(4)", size=15, color=ACCENT_GREEN, bold=True))
    p.append(text(410, 235, "Рекурсивне перевизначення parent[i] = root", size=12, color=MUTED))

    p.append(text(640, 40, "Після find(4): Пряме підключення", size=16, color=ACCENT_GREEN, bold=True))

    p.append(circle(640, 90, 24, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2.5))
    p.append(text(640, 95, "0", size=16, color=STROKE_ROOT, bold=True))

    p.append(circle(540, 240, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(540, 245, "1", size=14, color=INK))

    p.append(circle(600, 240, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(600, 245, "2", size=14, color=INK))

    p.append(circle(680, 240, 20, fill=FILL_NODE, stroke=STROKE_NODE, sw=2))
    p.append(text(680, 245, "3", size=14, color=INK))

    p.append(circle(740, 240, 20, fill=FILL_HIGHLIGHT, stroke=STROKE_HIGHLIGHT, sw=2.5))
    p.append(text(740, 245, "4", size=14, color=STROKE_HIGHLIGHT, bold=True))

    p.append(arrow(540, 220, 622, 108, color=ACCENT_GREEN, sw=2))
    p.append(arrow(600, 220, 632, 112, color=ACCENT_GREEN, sw=2))
    p.append(arrow(680, 220, 648, 112, color=ACCENT_GREEN, sw=2))
    p.append(arrow(740, 220, 658, 108, color=ACCENT_GREEN, sw=2))

    p.append(text(640, 355, "Усі вузли шляху тепер перенаправлені безпосередньо на корінь 0", size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "path-compression.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — Порівняння швидкості зростання складності: O(N) vs O(log N) vs O(alpha(N))
# ─────────────────────────────────────────────────────────────────────────────
def fig_ackermann_growth():
    W, H = 840, 360
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 35, "Порівняння швидкості зростання часової складності", size=16, color=INK, bold=True))

    ox, oy = 80, 300
    p.append(line(ox, oy, 780, oy, color=LINE, sw=2))
    p.append(line(ox, oy, ox, 60, color=LINE, sw=2))

    p.append(text(780, 325, "Розмір даних (N)", size=13, color=MUTED, anchor="end"))
    p.append(text(70, 50, "Операції / Час", size=13, color=MUTED, anchor="start"))

    p.append(line(ox, oy, 320, 80, color=ACCENT_RED, sw=3))
    p.append(text(330, 75, "O(N) — Без оптимізацій (Quick-Find/Union)", size=13, color=ACCENT_RED, bold=True))

    log_pts = [(ox, oy), (180, 260), (320, 230), (500, 205), (750, 185)]
    path_d = f"M {log_pts[0][0]} {log_pts[0][1]} " + " ".join([f"L {x} {y}" for x, y in log_pts[1:]])
    p.append(f'<path d="{path_d}" fill="none" stroke="{STROKE_HIGHLIGHT}" stroke-width="3" />')
    p.append(text(760, 175, "O(log N) — Лише Union by Rank", size=13, color=STROKE_HIGHLIGHT, bold=True))

    alpha_pts = [(ox, oy), (200, 290), (400, 287), (600, 285), (750, 284)]
    path_a = f"M {alpha_pts[0][0]} {alpha_pts[0][1]} " + " ".join([f"L {x} {y}" for x, y in alpha_pts[1:]])
    p.append(f'<path d="{path_a}" fill="none" stroke="{ACCENT_GREEN}" stroke-width="3.5" />')
    p.append(text(760, 275, "O(alpha(N)) <= 4 — Rank + Path Compression", size=13, color=ACCENT_GREEN, bold=True))

    p.append(circle(720, 284, 5, fill=ACCENT_GREEN, stroke=BG, sw=1))
    p.append(text(720, 310, "N = 10^80 (Атоми Всесвіту) -> alpha(N) = 4", size=12, color=ACCENT_GREEN, bold=True, anchor="middle"))

    render(os.path.join(OUT, "ackermann-growth.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — Стек відкоту у Rollback DSU (Персистентність без стиснення шляхів)
# ─────────────────────────────────────────────────────────────────────────────
def fig_dsu_rollback_stack():
    W, H = 840, 380
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 35, "Структура стеку відкоту у Rollback DSU", size=16, color=INK, bold=True))

    p.append(text(220, 75, "Стан масивів у пам'яті", size=15, color=STROKE_ROOT, bold=True))

    headers = ["Вузол (i)", "0", "1", "2", "3", "4"]
    parents = ["parent[i]", "0", "0", "1", "3", "3"]
    ranks   = ["rank[i]",   "2", "1", "0", "1", "0"]

    col_w = 60
    start_x = 70
    start_y = 100
    for c_idx, (h, p_val, r_val) in enumerate(zip(headers, parents, ranks)):
        x = start_x + c_idx * col_w
        p.append(rect(x, start_y, col_w, 30, fill=FILL_ROOT if c_idx==0 else FILL_CARD, stroke=STROKE_CARD))
        p.append(text(x + col_w/2, start_y + 20, h, size=12, color=INK, bold=(c_idx==0)))

        p.append(rect(x, start_y + 30, col_w, 30, fill=FILL_CARD, stroke=STROKE_CARD))
        p.append(text(x + col_w/2, start_y + 50, p_val, size=13, color=INK))

        p.append(rect(x, start_y + 60, col_w, 30, fill=FILL_CARD, stroke=STROKE_CARD))
        p.append(text(x + col_w/2, start_y + 80, r_val, size=13, color=MUTED))

    p.append(text(220, 220, "При union(u, v) зварюються лише корені.\nСтиснення шляхів ЗАБОРОНЕНО для збереження O(log N) історії.", size=12, color=MUTED))

    p.append(text(620, 75, "Стек відкоту змін (Undo Stack)", size=15, color=ACCENT_RED, bold=True))

    stack_items = [
        ("op #3: union(3, 4)", "parent[4]=3, rank_inc=0", STROKE_HIGHLIGHT, FILL_HIGHLIGHT),
        ("op #2: union(1, 3)", "parent[3]=1, rank_inc=1", ACCENT_BLUE, FILL_ROOT),
        ("op #1: union(0, 1)", "parent[1]=0, rank_inc=1", ACCENT_GREEN, FILL_CARD),
    ]

    sy = 100
    for idx, (title_text, details, strk, fll) in enumerate(stack_items):
        p.append(rect(490, sy, 260, 50, fill=fll, stroke=strk, sw=2, rx=4))
        p.append(text(500, sy + 22, title_text, size=13, color=strk, bold=True, anchor="start"))
        p.append(text(500, sy + 40, details, size=11, color=INK, anchor="start"))
        sy += 60

    p.append(arrow(770, 125, 770, 245, color=ACCENT_RED, sw=2.5))
    p.append(text(775, 185, "undo() вертає\nпопередній стан", size=12, color=ACCENT_RED, bold=True, anchor="start"))

    render(os.path.join(OUT, "dsu-rollback-stack.svg"), W, H, "".join(p))


if __name__ == "__main__":
    fig_dsu_tree_structure()
    fig_path_compression()
    fig_ackermann_growth()
    fig_dsu_rollback_stack()
    print("Усі 4 фігури успішно згенеровано у ./img/")
