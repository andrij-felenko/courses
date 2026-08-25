# -*- coding: utf-8 -*-
"""Фігури до статті «Алгоритм Гошена–Копельмана».
Генерує SVG-діаграми для пояснення растрового сканування ґратки,
вирішення колізій міток через ліс неперетинних множин, двопрохідного маркування
та фізики виявлення протікаючого кластера (spanning cluster).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT_BLUE   = "#2457d6"
ACCENT_GREEN  = FIELD
ACCENT_RED    = POS
FILL_CARD     = "#f8fafc"
STROKE_CARD   = "#cbd5e1"
FILL_ROOT     = "#e0f2fe"
STROKE_ROOT   = "#0284c7"
FILL_NODE     = "#f1f5f9"
STROKE_NODE   = "#64748b"
FILL_ACTIVE   = "#fef3c7"
STROKE_ACTIVE = "#d97706"
FILL_EMPTY    = "#ffffff"
STROKE_GRID   = "#e2e8f0"
FILL_OCCUPIED = "#93c5fd"
STROKE_OCCUPIED = "#3b82f6"


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — Растрове сканування та причинний окіл сайту (Top та Left)
# ─────────────────────────────────────────────────────────────────────────────
def fig_raster_neighborhood():
    W, H = 840, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 32, "Растрове сканування ґратки: причинний окіл 4-зв'язності", size=16, color=INK, bold=True))

    # Ліва панель: Ґратка з активним сайтом
    grid_x0, grid_y0 = 60, 70
    cell_s = 48
    grid_n = 5

    # Сітка та комірки
    grid_data = [
        [0, 1, 1, 0, 1],
        [1, 1, 0, 1, 1],
        [0, 1, 2, 0, 0],  # 2 - поточний активний сайт
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    p.append(text(grid_x0 + 120, grid_y0 + 20, "Двовимірна ґратка (L × L)", size=14, color=STROKE_ROOT, bold=True))

    # Растровий напрямок (стрілка сканування)
    p.append(arrow(grid_x0 + 20, grid_y0 + 40, grid_x0 + 230, grid_y0 + 40, color=STROKE_NODE, sw=2))
    p.append(text(grid_x0 + 125, grid_y0 + 35, "Напрямок обходу рядка", size=11, color=STROKE_NODE))

    for r in range(grid_n):
        for c in range(grid_n):
            cx = grid_x0 + c * cell_s
            cy = grid_y0 + 55 + r * cell_s
            val = grid_data[r][c]

            if r == 2 and c == 2:  # Поточний сайт (i, j)
                p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_ACTIVE, stroke=STROKE_ACTIVE, sw=2.5, rx=4))
                p.append(text(cx + cell_s/2, cy + cell_s/2 + 5, "(i, j)", size=13, color=STROKE_ACTIVE, bold=True))
            elif r == 1 and c == 2:  # Верхній сусід Top (i-1, j)
                p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2, rx=4))
                p.append(text(cx + cell_s/2, cy + cell_s/2 - 4, "Top", size=12, color=STROKE_ROOT, bold=True))
                p.append(text(cx + cell_s/2, cy + cell_s/2 + 12, "L_top", size=11, color=STROKE_ROOT))
            elif r == 2 and c == 1:  # Лівий сусід Left (i, j-1)
                p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=2, rx=4))
                p.append(text(cx + cell_s/2, cy + cell_s/2 - 4, "Left", size=12, color=STROKE_ROOT, bold=True))
                p.append(text(cx + cell_s/2, cy + cell_s/2 + 12, "L_left", size=11, color=STROKE_ROOT))
            elif r < 2 or (r == 2 and c < 1):  # Уже оброблені сайти
                if val == 1:
                    p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_OCCUPIED, stroke=STROKE_OCCUPIED, sw=1.5, rx=4))
                    p.append(text(cx + cell_s/2, cy + cell_s/2 + 5, "1", size=14, color=INK, bold=True))
                else:
                    p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_CARD, stroke=STROKE_CARD, sw=1, rx=4))
                    p.append(text(cx + cell_s/2, cy + cell_s/2 + 5, "0", size=13, color=MUTED))
            else:  # Ще не відвідані сайти (майбутнє)
                p.append(rect(cx, cy, cell_s, cell_s, fill=FILL_EMPTY, stroke=STROKE_GRID, sw=1, rx=4))
                p.append(text(cx + cell_s/2, cy + cell_s/2 + 5, "?", size=13, color=MUTED))

    # Права панель: Буфер пам'яті O(L) та 4 стани сусідок
    bx0 = 360
    p.append(text(bx0 + 220, 75, "Буферний рядок у пам'яті: O(L) замість O(L²)", size=15, color=ACCENT_BLUE, bold=True))

    # Візуалізація 1D буфера
    buf_labels = ["0", "1", "1", "0", "2"]
    for i, lbl in enumerate(buf_labels):
        bx = bx0 + 30 + i * 75
        p.append(rect(bx, 100, 70, 38, fill=FILL_CARD if lbl=="0" else FILL_ROOT, stroke=STROKE_ROOT if lbl!="0" else STROKE_CARD, sw=1.5, rx=4))
        p.append(text(bx + 35, 118, f"col [{i}]", size=11, color=MUTED))
        p.append(text(bx + 35, 132, f"мітка: {lbl}", size=12, color=STROKE_ROOT if lbl!="0" else MUTED, bold=(lbl!="0")))

    # 4 можливі комбінації сусідок
    p.append(text(bx0 + 220, 175, "Чотири стани локального оточення сайту:", size=14, color=INK, bold=True))

    cases = [
        ("1. Top = 0, Left = 0", "Ізольований сайт: нова мітка k_new, розмір = 1", ACCENT_GREEN),
        ("2. Top > 0, Left = 0", "Успадкування мітки Top: корінь r = find(Top), size++", ACCENT_BLUE),
        ("3. Top = 0, Left > 0", "Успадкування мітки Left: корінь r = find(Left), size++", ACCENT_BLUE),
        ("4. Top > 0, Left > 0", "Колізія міток: union(find(Top), find(Left)) + size++", ACCENT_RED),
    ]

    for idx, (title_t, desc_t, col) in enumerate(cases):
        cy = 205 + idx * 50
        p.append(rect(bx0 + 10, cy, 440, 42, fill=FILL_CARD, stroke=col, sw=1.5, rx=4))
        p.append(circle(bx0 + 25, cy + 21, 6, fill=col, stroke=col))
        p.append(text(bx0 + 40, cy + 18, title_t, size=13, color=col, bold=True, anchor="start"))
        p.append(text(bx0 + 40, cy + 33, desc_t, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig1-raster-neighborhood.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — Обробка колізії міток та злиття у лісі множин (Union-Find)
# ─────────────────────────────────────────────────────────────────────────────
def fig_label_collision_union():
    W, H = 840, 410
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 32, "Вирішення колізії міток: замикання кластера та операція Union", size=16, color=INK, bold=True))

    # Ліва частина: U-подібний міст на ґратці
    lx0 = 50
    p.append(text(lx0 + 140, 70, "Топологічне замикання (U-контур)", size=14, color=STROKE_ROOT, bold=True))

    # Спрощена схема U-контуру
    u_cells = [
        (0, 0, "1", FILL_OCCUPIED), (0, 1, "1", FILL_OCCUPIED), (0, 2, "0", FILL_CARD), (0, 3, "2", FILL_ROOT), (0, 4, "2", FILL_ROOT),
        (1, 0, "1", FILL_OCCUPIED), (1, 1, "0", FILL_CARD),     (1, 2, "0", FILL_CARD), (1, 3, "0", FILL_CARD), (1, 4, "2", FILL_ROOT),
        (2, 0, "1", FILL_OCCUPIED), (2, 1, "1", FILL_OCCUPIED), (2, 2, "X", FILL_ACTIVE), (2, 3, "2", FILL_ROOT), (2, 4, "2", FILL_ROOT),
    ]

    cs = 44
    for r, c, val, fill_c in u_cells:
        cx = lx0 + 30 + c * cs
        cy = 95 + r * cs
        strk = STROKE_ACTIVE if val == "X" else (STROKE_OCCUPIED if val == "1" else (STROKE_ROOT if val == "2" else STROKE_CARD))
        p.append(rect(cx, cy, cs, cs, fill=fill_c, stroke=strk, sw=2 if val=="X" else 1.2, rx=4))
        p.append(text(cx + cs/2, cy + cs/2 + 5, val, size=14, color=ACCENT_RED if val=="X" else INK, bold=True))

    # Пояснювальний блок для сайту X
    p.append(rect(lx0 + 20, 245, 240, 140, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=6))
    p.append(text(lx0 + 140, 270, "Міст у точці X (i, j):", size=13, color=ACCENT_RED, bold=True))
    p.append(text(lx0 + 140, 292, "Top = 0, Left = 1 (корінь 1)", size=12, color=INK))
    p.append(text(lx0 + 140, 312, "Right = 2 (корінь 2)", size=12, color=INK))
    p.append(text(lx0 + 140, 335, "Різні мітки об'єднуються:", size=12, color=STROKE_ROOT, bold=True))
    p.append(text(lx0 + 140, 355, "union(1, 2) без повернення назад!", size=12, color=ACCENT_GREEN, bold=True))

    # Центральна стрілка перетворення
    p.append(arrow(340, 200, 410, 200, color=STROKE_NODE, sw=3))
    p.append(text(375, 185, "Злиття", size=12, color=STROKE_NODE, bold=True))

    # Права частина: Стан масиву еквівалентностей labels[]
    rx0 = 430
    p.append(text(rx0 + 190, 70, "Масив еквівалентностей та розмірів labels[]", size=14, color=STROKE_ROOT, bold=True))

    # Таблиця ДО злиття
    p.append(text(rx0 + 20, 105, "До обробки сайту X:", size=13, color=INK, bold=True, anchor="start"))
    t_headers = ["Мітка (k)", "1", "2", "3", "4"]
    t_before  = ["labels[k]", "-5", "-4", "1", "2"]  # Від'ємні = корені (розміри 5 та 4)
    
    col_w = 68
    for i, (h, v) in enumerate(zip(t_headers, t_before)):
        bx = rx0 + 20 + i * col_w
        p.append(rect(bx, 120, col_w, 26, fill=FILL_ROOT if i==0 else FILL_CARD, stroke=STROKE_CARD))
        p.append(text(bx + col_w/2, 137, h, size=11, color=INK, bold=(i==0)))
        p.append(rect(bx, 146, col_w, 26, fill=FILL_CARD, stroke=STROKE_CARD))
        p.append(text(bx + col_w/2, 163, v, size=12, color=STROKE_ROOT if "-" in v else INK, bold=("-" in v)))

    p.append(text(rx0 + 20, 195, "Корінь 1: розмір = |-5| = 5    |    Корінь 2: розмір = |-4| = 4", size=11, color=MUTED, anchor="start"))

    # Таблиця ПІСЛЯ злиття
    p.append(text(rx0 + 20, 235, "Після union(1, 2) і додавання сайту X:", size=13, color=ACCENT_RED, bold=True, anchor="start"))
    t_after = ["labels[k]", "-10", "1", "1", "2"]  # Корінь 1 тепер розмір 5 + 4 + 1 = 10, мітка 2 вказує на 1
    
    for i, (h, v) in enumerate(zip(t_headers, t_after)):
        bx = rx0 + 20 + i * col_w
        p.append(rect(bx, 250, col_w, 26, fill=FILL_ACTIVE if i==0 else FILL_CARD, stroke=STROKE_ACTIVE if i==0 else STROKE_CARD))
        p.append(text(bx + col_w/2, 267, h, size=11, color=INK, bold=(i==0)))
        p.append(rect(bx, 276, col_w, 26, fill=FILL_CARD, stroke=STROKE_ACTIVE if i in (1,2) else STROKE_CARD))
        p.append(text(bx + col_w/2, 293, v, size=12, color=ACCENT_RED if i in (1,2) else INK, bold=(i in (1,2))))

    p.append(text(rx0 + 20, 325, "1. Сума розмірів: labels[1] = (-5) + (-4) - 1 = -10 (новий розмір 10)", size=12, color=ACCENT_GREEN, bold=True, anchor="start"))
    p.append(text(rx0 + 20, 348, "2. Перепризначення батька: labels[2] = 1 (корінь 2 підпорядковано кореню 1)", size=12, color=STROKE_ROOT, bold=True, anchor="start"))
    p.append(text(rx0 + 20, 370, "3. Стиснення шляхів (Path Compression) робить наступні find(4) = O(1)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fig2-label-collision-union.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — Двопрохідне маркування: Тимчасові мітки -> Канонічна перенумерація
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_pass_relabeling():
    W, H = 840, 400
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 32, "Двопрохідна схема алгоритму Гошена–Копельмана", size=16, color=INK, bold=True))

    # Блок 1: Початкова бінарна ґратка
    b1_x = 40
    p.append(rect(b1_x, 65, 210, 300, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=6))
    p.append(text(b1_x + 105, 90, "1. Вхідна ґратка", size=14, color=INK, bold=True))
    p.append(text(b1_x + 105, 108, "Сайт: 1 (зайнятий), 0 (порожній)", size=11, color=MUTED))

    grid1 = [
        [1, 1, 0, 1],
        [0, 1, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
    ]
    cs = 34
    for r in range(4):
        for c in range(4):
            cx = b1_x + 37 + c * cs
            cy = 130 + r * cs
            v = grid1[r][c]
            p.append(rect(cx, cy, cs, cs, fill=FILL_OCCUPIED if v==1 else FILL_EMPTY, stroke=STROKE_OCCUPIED if v==1 else STROKE_GRID, sw=1, rx=3))
            p.append(text(cx + cs/2, cy + cs/2 + 4, str(v), size=12, color=INK, bold=(v==1)))

    p.append(text(b1_x + 105, 300, "Прохід 1: Растрове", size=12, color=STROKE_ROOT, bold=True))
    p.append(text(b1_x + 105, 318, "сканування + DSU", size=12, color=STROKE_ROOT, bold=True))
    p.append(text(b1_x + 105, 342, "Час: O(N) | Пам'ять: O(L)", size=11, color=MUTED))

    # Стрілка 1 -> 2
    p.append(arrow(b1_x + 215, 215, b1_x + 270, 215, color=STROKE_NODE, sw=2))

    # Блок 2: Тимчасові мітки після Проходу 1
    b2_x = 285
    p.append(rect(b2_x, 65, 235, 300, fill=FILL_CARD, stroke=STROKE_ROOT, sw=1.5, rx=6))
    p.append(text(b2_x + 117, 90, "2. Тимчасові мітки", size=14, color=STROKE_ROOT, bold=True))
    p.append(text(b2_x + 117, 108, "Еквівалентність: labels[2]=1", size=11, color=ACCENT_RED, bold=True))

    grid2 = [
        [1, 1, 0, 2],
        [0, 1, 0, 2],
        [1, 1, 1, 2],  # Мітки 1 і 2 зустрілись
        [0, 0, 0, 2],
    ]
    for r in range(4):
        for c in range(4):
            cx = b2_x + 50 + c * cs
            cy = 130 + r * cs
            v = grid2[r][c]
            f_col = FILL_ROOT if v==1 else (FILL_ACTIVE if v==2 else FILL_EMPTY)
            s_col = STROKE_ROOT if v==1 else (STROKE_ACTIVE if v==2 else STROKE_GRID)
            p.append(rect(cx, cy, cs, cs, fill=f_col, stroke=s_col, sw=1, rx=3))
            p.append(text(cx + cs/2, cy + cs/2 + 4, str(v) if v!=0 else "·", size=12, color=INK, bold=(v!=0)))

    p.append(text(b2_x + 117, 300, "Прохід 2: Заміна", size=12, color=ACCENT_GREEN, bold=True))
    p.append(text(b2_x + 117, 318, "міток на find(k)", size=12, color=ACCENT_GREEN, bold=True))
    p.append(text(b2_x + 117, 342, "Нормалізація: 1..K", size=11, color=MUTED))

    # Стрілка 2 -> 3
    p.append(arrow(b2_x + 240, 215, b2_x + 295, 215, color=STROKE_NODE, sw=2))

    # Блок 3: Канонічні номери кластерів
    b3_x = 550
    p.append(rect(b3_x, 65, 250, 300, fill=FILL_CARD, stroke=ACCENT_GREEN, sw=1.5, rx=6))
    p.append(text(b3_x + 125, 90, "3. Канонічний результат", size=14, color=ACCENT_GREEN, bold=True))
    p.append(text(b3_x + 125, 108, "Усі вузли кластера мають спільну мітку", size=11, color=MUTED))

    grid3 = [
        [1, 1, 0, 1],
        [0, 1, 0, 1],
        [1, 1, 1, 1],  # Всі стали 1
        [0, 0, 0, 1],
    ]
    for r in range(4):
        for c in range(4):
            cx = b3_x + 57 + c * cs
            cy = 130 + r * cs
            v = grid3[r][c]
            p.append(rect(cx, cy, cs, cs, fill=FILL_OCCUPIED if v==1 else FILL_EMPTY, stroke=STROKE_OCCUPIED if v==1 else STROKE_GRID, sw=1.2, rx=3))
            p.append(text(cx + cs/2, cy + cs/2 + 4, str(v) if v!=0 else "·", size=12, color=INK, bold=(v!=0)))

    p.append(text(b3_x + 125, 300, "Фізична статистика:", size=12, color=INK, bold=True))
    p.append(text(b3_x + 125, 320, "Кількість кластерів K = 1", size=11, color=STROKE_ROOT))
    p.append(text(b3_x + 125, 342, "Розмір кластера s = 9 (протікає!)", size=11, color=ACCENT_RED, bold=True))

    render(os.path.join(OUT, "fig3-two-pass-relabeling.svg"), W, H, "".join(p))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — Фізика перколації: скінченні кластери та протікаючий кластер
# ─────────────────────────────────────────────────────────────────────────────
def fig_percolation_spanning_cluster():
    W, H = 840, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(420, 32, "Теорія перколації: скінченні острови та протікаючий кластер", size=16, color=INK, bold=True))

    # Ліва панель: Ґратка з нескінченним протікаючим кластером
    lx = 75
    p.append(text(lx + 130, 68, "Ґратка при p ≈ p_c (поріг перколації)", size=14, color=STROKE_ROOT, bold=True))

    # Матриця кластерів: 0-порожньо, 1-протікаючий кластер (червоний), 2,3,4-ізольовані кластери (сині/зелені)
    perc_grid = [
        [0, 1, 1, 0, 2, 2, 0],
        [0, 0, 1, 0, 0, 0, 3],
        [4, 0, 1, 1, 1, 0, 3],
        [4, 4, 0, 0, 1, 0, 0],
        [0, 0, 5, 0, 1, 1, 1],
        [6, 0, 5, 0, 0, 0, 1],
        [6, 6, 0, 7, 7, 0, 1],
    ]

    cs = 38
    for r in range(7):
        for c in range(7):
            cx = lx + c * cs
            cy = 88 + r * cs
            v = perc_grid[r][c]
            if v == 1:  # Spanning cluster
                p.append(rect(cx, cy, cs, cs, fill="#fee2e2", stroke=POS, sw=1.8, rx=3))
                p.append(text(cx + cs/2, cy + cs/2 + 4, "S", size=12, color=POS, bold=True))
            elif v > 1:  # Finite clusters
                p.append(rect(cx, cy, cs, cs, fill=FILL_ROOT, stroke=STROKE_ROOT, sw=1, rx=3))
                p.append(text(cx + cs/2, cy + cs/2 + 4, str(v), size=11, color=STROKE_ROOT))
            else:
                p.append(rect(cx, cy, cs, cs, fill=FILL_EMPTY, stroke=STROKE_GRID, sw=0.8, rx=3))

    # Стрілка зв'язності від верхньої до нижньої межі
    p.append(arrow(lx - 25, 95, lx - 25, 345, color=POS, sw=2.5))
    p.append(text(lx - 32, 220, "Протікання (Top ↔ Bottom)", size=11, color=POS, bold=True, anchor="end"))

    # Права панель: Статистика кластерів n_s(p) та властивості
    rx = 390
    p.append(text(rx + 210, 68, "Ключові статистичні характеристики", size=14, color=INK, bold=True))

    stats_cards = [
        ("Розподіл за розмірами n_s(p)",
         "Число кластерів розміру s на один вузол ґратки.\nПри p = p_c спадає за степеневим законом: n_s ∝ s^(-τ)\nде для 2D систем критичний індекс τ = 187/91 ≈ 2.05.",
         ACCENT_BLUE),
        ("Радіус гірації R_s (просторова протяжність)",
         "Середньоквадратична відстань між сайтами всередині кластера:\nR_s² = (1 / 2s²) ∑ |r_i - r_j|² ∝ s^(1/d_f)\nде d_f = 91/48 ≈ 1.896 — фрактальна розмірність кластера.",
         ACCENT_GREEN),
        ("Критерій перколації (Spanning Condition)",
         "Кластер вважається протікаючим, якщо він одночасно містить\nсайти на протилежних границях системи (x=0 та x=L-1),\nзабезпечуючи макроскопічну провідність середовища.",
         ACCENT_RED),
    ]

    sy = 95
    for title_t, body_t, col in stats_cards:
        p.append(rect(rx + 10, sy, 400, 85, fill=FILL_CARD, stroke=col, sw=1.5, rx=6))
        p.append(circle(rx + 26, sy + 20, 5, fill=col, stroke=col))
        p.append(text(rx + 40, sy + 24, title_t, size=13, color=col, bold=True, anchor="start"))
        lines = body_t.split("\n")
        for l_i, ln in enumerate(lines):
            p.append(text(rx + 40, sy + 44 + l_i * 16, ln, size=11, color=INK, anchor="start"))
        sy += 98

    render(os.path.join(OUT, "fig4-percolation-spanning-cluster.svg"), W, H, "".join(p))


if __name__ == "__main__":
    fig_raster_neighborhood()
    fig_label_collision_union()
    fig_two_pass_relabeling()
    fig_percolation_spanning_cluster()
    print("Усі 4 фігури успішно згенеровано у ./img/")
