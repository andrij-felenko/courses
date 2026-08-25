# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для статті «Таблиця розрідження (Sparse Table)».
Фігури:
1. interval-decomposition.svg — Ієрархія інтервалів степенів двійки та DP-перехід.
2. rmq-overlapping.svg — Константний O(1) запит через перекриття двох блоків довжини 2^k.
3. memory-layout-cache.svg — Організація пам'яті ST[j][i] проти ST[i][j] та локальність кешу.
4. disjoint-binary-lift.svg — Диз'юнктне двійкове розбиття для неідемпотентних операцій O(log N).
5. data-structure-tradeoffs.svg — Порівняння Sparse Table, Segment Tree, Fenwick Tree, Treap.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
CLR_BG_L0 = "#eef6ff"
CLR_STR_L0 = NEG
CLR_BG_L1 = "#eafaf0"
CLR_STR_L1 = FIELD
CLR_BG_L2 = "#fef9e7"
CLR_STR_L2 = "#d4ac0d"
CLR_BG_L3 = "#fdecea"
CLR_STR_L3 = POS

# ─────────────────────────────────────────────────────────────────────────────
# 1. interval-decomposition.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_interval_decomposition():
    W, H = 860, 490
    p = []
    
    p.append(text(W/2, 26, "Ієрархічна структура блоків степенів двійки в таблиці розрідження", size=16, bold=True, color=INK))
    
    # Вихідний масив A (8 елементів)
    arr = [7, 2, 3, 0, 5, 10, 3, 12]
    cell_w = 84
    x0 = 85
    y_arr = 65
    
    p.append(text(x0 - 15, y_arr + 22, "A[i]:", size=13, bold=True, color=MUTED, anchor="end"))
    for i, val in enumerate(arr):
        bx = x0 + i * cell_w
        p.append(rect(bx, y_arr, cell_w - 6, 36, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))
        p.append(text(bx + (cell_w - 6)/2, y_arr + 15, f"i={i}", size=10, color=MUTED))
        p.append(text(bx + (cell_w - 6)/2, y_arr + 30, str(val), size=14, bold=True, color=INK))
    
    # Рівень j = 0 (довжина 2^0 = 1)
    y_l0 = 130
    p.append(text(x0 - 15, y_l0 + 20, "j = 0 (len=1):", size=12, bold=True, color=CLR_STR_L0, anchor="end"))
    for i in range(8):
        bx = x0 + i * cell_w
        p.append(rect(bx, y_l0, cell_w - 6, 32, fill=CLR_BG_L0, stroke=CLR_STR_L0, sw=1.2, rx=4))
        p.append(text(bx + (cell_w - 6)/2, y_l0 + 21, f"ST[0][{i}]={arr[i]}", size=11, color=CLR_STR_L0, bold=True))
        
    # Рівень j = 1 (довжина 2^1 = 2) - показуємо розбиття на пари (i=0, 2, 4, 6)
    y_l1 = 195
    p.append(text(x0 - 15, y_l1 + 20, "j = 1 (len=2):", size=12, bold=True, color=CLR_STR_L1, anchor="end"))
    for idx in range(4):
        i = idx * 2
        bx = x0 + i * cell_w
        w_block = cell_w * 2 - 6
        min_v = min(arr[i], arr[i+1])
        p.append(rect(bx, y_l1, w_block, 32, fill=CLR_BG_L1, stroke=CLR_STR_L1, sw=1.3, rx=4))
        p.append(text(bx + w_block/2, y_l1 + 21, f"ST[1][{i}] = min({arr[i]}, {arr[i+1]}) = {min_v}", size=11, color=CLR_STR_L1, bold=True))
        
    # Рівень j = 2 (довжина 2^2 = 4) - показуємо блоки довжини 4 (i=0, 4)
    y_l2 = 260
    p.append(text(x0 - 15, y_l2 + 20, "j = 2 (len=4):", size=12, bold=True, color="#b7950b", anchor="end"))
    for idx in range(2):
        i = idx * 4
        bx = x0 + i * cell_w
        w_block = cell_w * 4 - 6
        min_v = min(arr[i:i+4])
        p.append(rect(bx, y_l2, w_block, 32, fill=CLR_BG_L2, stroke=CLR_STR_L2, sw=1.3, rx=4))
        p.append(text(bx + w_block/2, y_l2 + 21, f"ST[2][{i}] = min(ST[1][{i}], ST[1][{i+2}]) = {min_v}", size=11, color="#7d6608", bold=True))
        
    # Рівень j = 3 (довжина 2^3 = 8)
    y_l3 = 325
    p.append(text(x0 - 15, y_l3 + 20, "j = 3 (len=8):", size=12, bold=True, color=CLR_STR_L3, anchor="end"))
    bx = x0
    w_block = cell_w * 8 - 6
    min_v = min(arr)
    p.append(rect(bx, y_l3, w_block, 34, fill=CLR_BG_L3, stroke=CLR_STR_L3, sw=1.5, rx=5))
    p.append(text(bx + w_block/2, y_l3 + 22, f"ST[3][0] = min(ST[2][0], ST[2][4]) = min(0, 3) = {min_v}", size=12, color=CLR_STR_L3, bold=True))

    # Стрілки DP переходу та формула
    p.append(rect(30, 385, 800, 75, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(430, 412, "Рівняння динамічного програмування:  ST[j][i] = min( ST[j - 1][i],  ST[j - 1][i + 2^(j - 1)] )", size=13, bold=True, color=INK))
    p.append(text(430, 436, "Кожен блок довжини 2^j обчислюється об'єднанням двох суміжних блоків довжини 2^(j-1) за O(1)", size=11, color=MUTED))

    render(os.path.join(OUT, "interval-decomposition.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 2. rmq-overlapping.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_rmq_overlapping():
    W, H = 840, 400
    p = []
    
    p.append(text(W/2, 28, "Константний запит Range Minimum Query O(1) через перекриття блоків", size=16, bold=True, color=INK))
    
    arr = [9, 3, 7, 1, 8, 2, 14, 10, 5, 4, 11]
    cell_w = 66
    x0 = 55
    y_arr = 70
    
    # Відрізок запиту [L=2, R=8] -> довжина len = 7
    L_idx, R_idx = 2, 8
    
    for i, val in enumerate(arr):
        bx = x0 + i * cell_w
        is_in = (L_idx <= i <= R_idx)
        bg = "#eef6ff" if is_in else "#ffffff"
        bd = NEG if is_in else "#cbd5e1"
        p.append(rect(bx, y_arr, cell_w - 4, 46, fill=bg, stroke=bd, sw=1.6 if is_in else 1.0, rx=4))
        p.append(text(bx + (cell_w - 4)/2, y_arr + 16, f"i={i}", size=11, color=MUTED))
        p.append(text(bx + (cell_w - 4)/2, y_arr + 36, str(val), size=15, bold=True, color=INK))
        
    # Рамка запиту [L, R]
    p.append(rect(x0 + L_idx * cell_w - 3, y_arr - 4, (R_idx - L_idx + 1) * cell_w - 2, 54, fill="none", stroke=POS, sw=2, rx=6))
    p.append(text(x0 + L_idx * cell_w, y_arr - 10, "L = 2", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(x0 + (R_idx + 1) * cell_w - 6, y_arr - 10, "R = 8", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(x0 + ((L_idx + R_idx + 1) * cell_w)/2, y_arr - 10, "Довжина відрізка = R - L + 1 = 7,   k = ⌊log₂(7)⌋ = 2   (2^k = 4)", size=12, bold=True, color=INK))

    # Лівий блок: [L, L + 2^k - 1] = [2, 5]
    y_b1 = 150
    bx1 = x0 + L_idx * cell_w
    bw1 = 4 * cell_w - 4
    p.append(rect(bx1, y_b1, bw1, 38, fill=CLR_BG_L1, stroke=CLR_STR_L1, sw=1.8, rx=6))
    p.append(text(bx1 + bw1/2, y_b1 + 16, "Лівий блок: [L .. L + 2^k - 1] = [2 .. 5]", size=12, bold=True, color=CLR_STR_L1))
    p.append(text(bx1 + bw1/2, y_b1 + 31, "ST[2][2] = min(7, 1, 8, 2) = 1", size=11, color=INK))

    # Правий блок: [R - 2^k + 1, R] = [5, 8]
    y_b2 = 210
    bx2 = x0 + (R_idx - 4 + 1) * cell_w
    bw2 = 4 * cell_w - 4
    p.append(rect(bx2, y_b2, bw2, 38, fill=CLR_BG_L0, stroke=CLR_STR_L0, sw=1.8, rx=6))
    p.append(text(bx2 + bw2/2, y_b2 + 16, "Правий блок: [R - 2^k + 1 .. R] = [5 .. 8]", size=12, bold=True, color=CLR_STR_L0))
    p.append(text(bx2 + bw2/2, y_b2 + 31, "ST[2][5] = min(2, 14, 10, 5) = 2", size=11, color=INK))

    # Область перекриття
    bx_ov = x0 + 5 * cell_w
    bw_ov = cell_w - 4
    p.append(rect(bx_ov, y_b1, bw_ov, 98, fill="none", stroke=POS, sw=2, rx=4))
    p.append(text(bx_ov + bw_ov/2, 275, "Перекриття (i=5)", size=11, bold=True, color=POS))

    # Підсумковий блок формули
    p.append(rect(30, 305, 780, 75, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(420, 332, "RMQ(L, R) = min( ST[k][L],  ST[k][R - 2^k + 1] ) = min( ST[2][2],  ST[2][5] ) = min(1, 2) = 1", size=14, bold=True, color=POS))
    p.append(text(420, 358, "Ідемпотентність min(x, x) = x гарантує правильність результату навіть при повторному врахуванні елементів перекриття", size=12, color=MUTED))

    render(os.path.join(OUT, "rmq-overlapping.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 3. memory-layout-cache.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_memory_layout_cache():
    W, H = 840, 420
    p = []
    
    p.append(text(W/2, 28, "Вплив організації вимірів масиву на кеш-локальність процесора", size=16, bold=True, color=INK))
    
    # Ліва колонка: ST[j][i] (Рівнево-послідовний макет - ОПТИМАЛЬНИЙ)
    p.append(rect(30, 60, 375, 335, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(217, 88, "Оптимально: ST[j][i] (рівні в рядках)", size=14, bold=True, color=FIELD))
    p.append(text(217, 108, "Рівень j займає неперервний блок у пам'яті", size=11, color=MUTED))

    # Схема пам'яті для ST[j][i]
    y_m1 = 130
    for j in range(3):
        p.append(rect(50, y_m1 + j * 42, 335, 30, fill=CLR_BG_L1, stroke=FIELD, sw=1.2, rx=4))
        p.append(text(60, y_m1 + j * 42 + 20, f"Рівень j={j}:", size=11, bold=True, color=FIELD, anchor="start"))
        p.append(text(145, y_m1 + j * 42 + 20, f"ST[{j}][0]   ST[{j}][1]   ST[{j}][2] ... ST[{j}][N-1]", size=10, color=INK, anchor="start"))

    # Пояснення кеш-ефекту ліворуч
    p.append(rect(50, 270, 335, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(217, 292, "Переваги для процесорного кешу:", size=11, bold=True, color=FIELD))
    p.append(text(60, 314, "• Лінійне завантаження кеш-ліній (64 байти)", size=10, color=INK, anchor="start"))
    p.append(text(60, 334, "• Ефективна робота апаратного Prefetcher L1/L2", size=10, color=INK, anchor="start"))
    p.append(text(60, 354, "• Запит RMQ зчитує лише з 1 фіксованого рядка j=k", size=10, color=INK, anchor="start"))
    p.append(text(60, 372, "• Прискорення побудови у 2.5–4.2 рази", size=10, bold=True, color=POS, anchor="start"))

    # Права колонка: ST[i][j] (Індексно-послідовний макет - НЕОПТИМАЛЬНИЙ)
    p.append(rect(435, 60, 375, 335, fill="#f8fafc", stroke=POS, sw=1.8, rx=8))
    p.append(text(622, 88, "Неоптимально: ST[i][j] (індекси в рядках)", size=14, bold=True, color=POS))
    p.append(text(622, 108, "Елементи одного рівня розкидані з кроком K", size=11, color=MUTED))

    # Схема пам'яті для ST[i][j]
    y_m2 = 130
    for i in range(3):
        p.append(rect(455, y_m2 + i * 42, 335, 30, fill=CLR_BG_L3, stroke=POS, sw=1.2, rx=4))
        p.append(text(465, y_m2 + i * 42 + 20, f"Вузол i={i}:", size=11, bold=True, color=POS, anchor="start"))
        p.append(text(545, y_m2 + i * 42 + 20, f"ST[{i}][0]   ST[{i}][1]   ST[{i}][2] ... ST[{i}][K-1]", size=10, color=INK, anchor="start"))

    # Пояснення кеш-ефекту праворуч
    p.append(rect(455, 270, 335, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(622, 292, "Проблеми з пам'яттю:", size=11, bold=True, color=POS))
    p.append(text(465, 314, "• Stride-доступ із кроком K = log₂(N) слів", size=10, color=INK, anchor="start"))
    p.append(text(465, 334, "• Постійні промахи кешу (L1/L2 Cache Misses)", size=10, color=INK, anchor="start"))
    p.append(text(465, 354, "• Знецінення кеш-ліній: з 64 байтів береться 4", size=10, color=INK, anchor="start"))
    p.append(text(465, 372, "• Просідання throughput при N > 100 000", size=10, bold=True, color=POS, anchor="start"))

    render(os.path.join(OUT, "memory-layout-cache.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 4. disjoint-binary-lift.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_disjoint_binary_lift():
    W, H = 840, 420
    p = []
    
    p.append(text(W/2, 28, "Диз'юнктне двійкове розбиття для неідемпотентних операцій (Сума/Добуток)", size=16, bold=True, color=INK))
    
    # Відрізок довжини 13: 13 = 8 + 4 + 1 = (1101)₂
    # Нехай L = 1, R = 13 (довжина 13)
    x0 = 60
    y_top = 70
    w_total = 720
    unit = w_total / 13.0
    
    # Загальний відрізок
    p.append(rect(x0, y_top, w_total, 45, fill="#f1f5f9", stroke="#64748b", sw=1.8, rx=6))
    p.append(text(x0 + w_total/2, y_top + 28, "Загальний відрізок запиту: [L=1 .. R=13],  Довжина len = 13 = 8 + 4 + 1 = (1101)₂", size=13, bold=True, color=INK))

    # Блок 1: 2^3 = 8
    w1 = 8 * unit
    x1 = x0
    y_b = 145
    p.append(rect(x1, y_b, w1 - 4, 50, fill=CLR_BG_L3, stroke=CLR_STR_L3, sw=1.6, rx=5))
    p.append(text(x1 + (w1-4)/2, y_b + 22, "Блок 1 (степінь 2³ = 8): [1 .. 8]", size=12, bold=True, color=CLR_STR_L3))
    p.append(text(x1 + (w1-4)/2, y_b + 39, "ST[3][1] = Sum(A[1..8])", size=11, color=INK))

    # Блок 2: 2^2 = 4
    w2 = 4 * unit
    x2 = x1 + w1
    p.append(rect(x2, y_b, w2 - 4, 50, fill=CLR_BG_L2, stroke="#b7950b", sw=1.6, rx=5))
    p.append(text(x2 + (w2-4)/2, y_b + 22, "Блок 2 (2² = 4): [9 .. 12]", size=12, bold=True, color="#b7950b"))
    p.append(text(x2 + (w2-4)/2, y_b + 39, "ST[2][9] = Sum(A[9..12])", size=11, color=INK))

    # Блок 3: 2^0 = 1
    w3 = 1 * unit
    x3 = x2 + w2
    p.append(rect(x3, y_b, w3, 50, fill=CLR_BG_L0, stroke=CLR_STR_L0, sw=1.6, rx=5))
    p.append(text(x3 + w3/2, y_b + 22, "2⁰=1", size=11, bold=True, color=CLR_STR_L0))
    p.append(text(x3 + w3/2, y_b + 39, "[13]", size=11, color=INK))

    # Стрілки покрокової комбінації
    y_flow = 225
    p.append(rect(30, y_flow, 780, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(420, y_flow + 25, "Алгоритм диз'юнктного накопичення: O(popcount(len)) ≤ O(log₂ N) кроків", size=13, bold=True, color=POS))
    p.append(text(420, y_flow + 48, "res = ST[3][1] ⊕ ST[2][9] ⊕ ST[0][13]", size=13, bold=True, color=INK))
    p.append(text(420, y_flow + 68, "Відрізки не перетинаються (disjoint), тому операція не вимагає ідемпотентності", size=11, color=MUTED))

    # Порівняльний підсумок унизу
    p.append(rect(30, 325, 780, 75, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    p.append(text(420, 348, "Ідемпотентні оператори (min, max, gcd, AND, OR):  1 перекриття  →  O(1) час", size=12, bold=True, color=FIELD))
    p.append(text(420, 370, "Неідемпотентні оператори (+, *, матриці, XOR):   розбиття на біти  →  O(log N) час", size=12, bold=True, color=POS))
    p.append(text(420, 388, "(Для сум на статичному масиві краще застосовувати масив префіксних сум з O(1) запитом)", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "disjoint-binary-lift.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# 5. data-structure-tradeoffs.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_data_structure_tradeoffs():
    W, H = 840, 440
    p = []
    
    p.append(text(W/2, 28, "Порівняльний ландшафт структур даних для запитів на відрізках", size=16, bold=True, color=INK))
    
    # Заголовки таблиці / колонок
    col_w = 185
    x_base = 35
    y_h = 60
    
    headers = [
        ("Таблиця розрідження\n(Sparse Table)", POS, CLR_BG_L3),
        ("Відрізкове дерево\n(Segment Tree)", FIELD, CLR_BG_L1),
        ("Дерево Фенвіка\n(Fenwick Tree)", NEG, CLR_BG_L0),
        ("Декартове дерево\n(Treap)", "#d4ac0d", CLR_BG_L2)
    ]
    
    for idx, (title, stroke_c, fill_c) in enumerate(headers):
        cx = x_base + idx * (col_w + 10)
        p.append(rect(cx, y_h, col_w, 355, fill="#f8fafc", stroke=stroke_c, sw=1.8, rx=6))
        p.append(rect(cx, y_h, col_w, 52, fill=fill_c, stroke=stroke_c, sw=1.2, rx=6))
        lines = title.split("\n")
        p.append(text(cx + col_w/2, y_h + 20, lines[0], size=12, bold=True, color=stroke_c))
        p.append(text(cx + col_w/2, y_h + 38, lines[1], size=11, bold=True, color=INK))
        
    # Вміст для кожної структури
    # 1. Sparse Table
    x1 = x_base
    p.append(text(x1 + 10, 135, "Побудова: O(N log N)", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(x1 + 10, 155, "RMQ запит: O(1)", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(x1 + 10, 175, "Загальний запит: O(log N)", size=11, color=MUTED, anchor="start"))
    p.append(text(x1 + 10, 195, "Оновлення: O(N) (статична)", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(x1 + 10, 215, "Пам'ять: O(N log N)", size=11, color=INK, anchor="start"))
    p.append(line(x1 + 10, 230, x1 + col_w - 10, 230, color="#cbd5e1", sw=1.0))
    p.append(text(x1 + 10, 250, "Головний фокус:", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(x1 + 10, 270, "Мільйони статичних RMQ,", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 10, 288, "LCA у деревах,", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 10, 306, "ідемпотентні напівгрупи.", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 10, 335, "Плюси: миттєвий O(1) RMQ,", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x1 + 10, 353, "компактний масив, кеш.", size=10, color=FIELD, anchor="start"))
    p.append(text(x1 + 10, 380, "Мінуси: незмінність даних.", size=10, color=POS, bold=True, anchor="start"))

    # 2. Segment Tree
    x2 = x_base + 1 * (col_w + 10)
    p.append(text(x2 + 10, 135, "Побудова: O(N)", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(x2 + 10, 155, "RMQ запит: O(log N)", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 10, 175, "Загальний запит: O(log N)", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 10, 195, "Оновлення: O(log N)", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(x2 + 10, 215, "Пам'ять: O(N) (4N вузлів)", size=11, color=INK, anchor="start"))
    p.append(line(x2 + 10, 230, x2 + col_w - 10, 230, color="#cbd5e1", sw=1.0))
    p.append(text(x2 + 10, 250, "Головний фокус:", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(x2 + 10, 270, "Динамічні масиви,", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 10, 288, "групові модифікації", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 10, 306, "(Lazy Propagation).", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 10, 335, "Плюси: повна універсальність,", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 10, 353, "гнучкість операцій.", size=10, color=FIELD, anchor="start"))
    p.append(text(x2 + 10, 380, "Мінуси: O(log N) на RMQ.", size=10, color=POS, bold=True, anchor="start"))

    # 3. Fenwick Tree
    x3 = x_base + 2 * (col_w + 10)
    p.append(text(x3 + 10, 135, "Побудова: O(N)", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(x3 + 10, 155, "Префіксний запит: O(log N)", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 10, 175, "RMQ запит: O(log² N) (обмеж.)", size=11, color=MUTED, anchor="start"))
    p.append(text(x3 + 10, 195, "Оновлення: O(log N)", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(x3 + 10, 215, "Пам'ять: O(N) (суворо N)", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(line(x3 + 10, 230, x3 + col_w - 10, 230, color="#cbd5e1", sw=1.0))
    p.append(text(x3 + 10, 250, "Головний фокус:", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(x3 + 10, 270, "Динамічні префіксні суми,", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 10, 288, "підрахунок інверсій,", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 10, 306, "мінімальний оверхед.", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 10, 335, "Плюси: 1 масив розміру N,", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 10, 353, "побітові операції LSB.", size=10, color=FIELD, anchor="start"))
    p.append(text(x3 + 10, 380, "Мінуси: важкий RMQ.", size=10, color=POS, bold=True, anchor="start"))

    # 4. Treap (Декартове дерево)
    x4 = x_base + 3 * (col_w + 10)
    p.append(text(x4 + 10, 135, "Побудова: O(N) / O(N log N)", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 10, 155, "RMQ запит: O(log N)", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 10, 175, "Вставка/Видалення: O(log N)", size=12, bold=True, color="#b7950b", anchor="start"))
    p.append(text(x4 + 10, 195, "Злиття/Розрізання: O(log N)", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 10, 215, "Пам'ять: O(N) (вказівники)", size=11, color=POS, anchor="start"))
    p.append(line(x4 + 10, 230, x4 + col_w - 10, 230, color="#cbd5e1", sw=1.0))
    p.append(text(x4 + 10, 250, "Головний фокус:", size=11, bold=True, color="#b7950b", anchor="start"))
    p.append(text(x4 + 10, 270, "Неявні ключі, динамічні", size=10, color=INK, anchor="start"))
    p.append(text(x4 + 10, 288, "перестановки відрізків,", size=10, color=INK, anchor="start"))
    p.append(text(x4 + 10, 306, "розрізання та склеювання.", size=10, color=INK, anchor="start"))
    p.append(text(x4 + 10, 335, "Плюси: довільні мутації масиву,", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x4 + 10, 353, "циклічні зсуви, реверси.", size=10, color=FIELD, anchor="start"))
    p.append(text(x4 + 10, 380, "Мінуси: оверхед вказівників.", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "data-structure-tradeoffs.svg"), W, H, *p)

if __name__ == "__main__":
    fig_interval_decomposition()
    fig_rmq_overlapping()
    fig_memory_layout_cache()
    fig_disjoint_binary_lift()
    fig_data_structure_tradeoffs()
    print("All figures successfully generated in", OUT)
