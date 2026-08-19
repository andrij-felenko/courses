# -*- coding: utf-8 -*-
"""Фігури до теми «Стрічковий фільтр (Ribbon Filter)».
Генерація SVG у ./img/ за допомогою svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── Фігура 1: Стрічкова структура матриці над GF(2) ───────────────────────────
def fig_band_matrix():
    W, H = 840, 480
    parts = []
    
    parts.append(text(W / 2, 28, "Стрічкова структура системи лінійних рівнянь A · B = f над GF(2)", size=16, bold=True))
    
    # Пояснювальний блок зліва
    tx1, ty1, tw1, th1 = 40, 56, 760, 48
    parts.append(rect(tx1, ty1, tw1, th1, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, 75, "Кожен ключ k_i генерує ненульові коефіцієнти лише у вузькому вікні ширини w бітів (стрічці)", size=13, color=INK))
    parts.append(text(W / 2, 93, "Поза вікном [p_i, p_i + w - 1] усі коефіцієнти вектора рядка дорівнюють строго 0", size=12, color=MUTED))

    # Схема матриці: N рядків (ключів) x M стовпців (слотів фільтра)
    mx, my = 90, 130
    mw, mh = 400, 240
    
    # Фон матриці A
    parts.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    parts.append(text(mx + mw / 2, my - 12, "Матриця коефіцієнтів A (N × M над GF(2))", size=13, bold=True))
    
    # Стовпці 0 ... M-1
    parts.append(text(mx + 20, my + mh + 18, "стовпець 0", size=11, color=MUTED))
    parts.append(text(mx + mw - 30, my + mh + 18, "стовпець M-1", size=11, color=MUTED))
    
    # Рядки: намалюємо 6 характерних стрічок, що спускаються по діагоналі
    bands = [
        (0, 0, 100, 28, "k₀: p=0, mask=10110..."),
        (1, 40, 100, 28, "k₁: p=4, mask=11001..."),
        (2, 95, 100, 28, "k₂: p=10, mask=10101..."),
        (3, 160, 100, 28, "k₃: p=17, mask=11110..."),
        (4, 220, 100, 28, "k₄: p=23, mask=10011..."),
        (5, 290, 100, 28, "k₅: p=31, mask=11010..."),
    ]
    
    for row_idx, bx, bw, bh, label in bands:
        ry = my + 15 + row_idx * 36
        rx = mx + 10 + bx
        # Лінія рядка
        parts.append(line(mx + 4, ry + bh / 2, mx + mw - 4, ry + bh / 2, color="#e2e8f0", sw=1))
        # Стрічка (вікно w бітів)
        parts.append(rect(rx, ry, bw, bh, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
        parts.append(text(rx + bw / 2, ry + 18, "w бітів", size=11, color=NEG, bold=True))
        # Підпис рядка зліва
        parts.append(text(mx - 10, ry + 18, "Рядок " + str(row_idx), size=11, color=INK, anchor="end"))

    # Знак множення
    parts.append(text(mx + mw + 25, my + mh / 2 + 6, "×", size=22, bold=True, color=LINE))
    
    # Невідомий вектор B (слоти фільтра розв'язку)
    bx_pos, by_pos, bw_pos = mx + mw + 50, my, 80
    parts.append(rect(bx_pos, by_pos, bw_pos, mh, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=4))
    parts.append(text(bx_pos + bw_pos / 2, by_pos - 12, "Слоти B", size=13, bold=True, color="#b45309"))
    parts.append(text(bx_pos + bw_pos / 2, by_pos + 30, "B[0]", size=12, color="#b45309"))
    parts.append(text(bx_pos + bw_pos / 2, by_pos + mh / 2, "⋮ (M слів)", size=13, bold=True, color="#b45309"))
    parts.append(text(bx_pos + bw_pos / 2, by_pos + mh - 20, "B[M-1]", size=12, color="#b45309"))

    # Знак рівності
    parts.append(text(bx_pos + bw_pos + 25, my + mh / 2 + 6, "=", size=22, bold=True, color=LINE))

    # Вектор відбитків f (цільові значення r бітів)
    fx_pos, fy_pos, fw_pos = bx_pos + bw_pos + 50, my, 110
    parts.append(rect(fx_pos, fy_pos, fw_pos, mh, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    parts.append(text(fx_pos + fw_pos / 2, fy_pos - 12, "Відбитки f", size=13, bold=True, color=FIELD))
    parts.append(text(fx_pos + fw_pos / 2, fy_pos + 30, "f(k₀) [r біт]", size=11, color=FIELD))
    parts.append(text(fx_pos + fw_pos / 2, fy_pos + mh / 2, "⋮ (N рядків)", size=13, bold=True, color=FIELD))
    parts.append(text(fx_pos + fw_pos / 2, fy_pos + mh - 20, "f(k_{N-1})", size=11, color=FIELD))

    # Нижній висновок
    bx2, by2, bw2, bh2 = 40, 400, 760, 56
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, by2 + 22, "Розв'язання системи: визначення значень B[0..M-1], що задовольняють ⊕_{j=0}^{w-1} (c_i[j] · B[p_i + j]) = f(k_i)", size=12.5, bold=True, color=INK))
    parts.append(text(W / 2, by2 + 42, "Стрічкова форма дозволяє знайти B за лінійний час O(N · w) замість O(N³) кубічного Гаусса", size=12, color=MUTED))

    render(os.path.join(IMG, "ribbon-band-matrix.svg"), W, H, *parts)


# ── Фігура 2: Інкрементне стрічкове виключення Гаусса ──────────────────────────
def fig_band_elimination():
    W, H = 840, 460
    parts = []
    
    parts.append(text(W / 2, 28, "Алгоритм інкрементного стрічкового виключення Гаусса (Band Elimination)", size=16, bold=True))
    
    # Крок 1: Вхід нового рядка
    s1_x, s1_y, s1_w, s1_h = 40, 60, 230, 260
    parts.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(s1_x + s1_w / 2, s1_y + 24, "1. Нове рівняння k_x", size=13, bold=True, color=POS))
    parts.append(line(s1_x + 10, s1_y + 36, s1_x + s1_w - 10, s1_y + 36, color="#cbd5e1", sw=1))
    parts.append(text(s1_x + s1_w / 2, s1_y + 60, "Обчислення старту p та маски:", size=11, color=MUTED))
    parts.append(rect(s1_x + 20, s1_y + 75, 190, 32, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    parts.append(text(s1_x + s1_w / 2, s1_y + 95, "p = 12, mask = 1101001...", size=11, bold=True))
    parts.append(text(s1_x + s1_w / 2, s1_y + 130, "Старший біт стоїть", size=11, color=INK))
    parts.append(text(s1_x + s1_w / 2, s1_y + 148, "у позиції col = 12", size=11, bold=True, color=POS))
    parts.append(rect(s1_x + 20, s1_y + 170, 190, 68, fill="#eff6ff", stroke=NEG, sw=1, rx=4))
    parts.append(text(s1_x + s1_w / 2, s1_y + 190, "Перевірка слота 12:", size=11, bold=True, color=NEG))
    parts.append(text(s1_x + s1_w / 2, s1_y + 210, "Чи є вже опорний рядок", size=11, color=MUTED))
    parts.append(text(s1_x + s1_w / 2, s1_y + 226, "(pivot) у pivot[12]?", size=11, color=MUTED))

    # Стрілка 1 -> 2
    parts.append(arrow(s1_x + s1_w + 5, s1_y + s1_h / 2, s1_x + s1_w + 30, s1_y + s1_h / 2, color=LINE, sw=1.8))

    # Крок 2: Розв'язання колізії (XOR редукція)
    s2_x, s2_y, s2_w, s2_h = 305, 60, 240, 260
    parts.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(s2_x + s2_w / 2, s2_y + 24, "2. Колізія опорних рядків", size=13, bold=True, color="#d97706"))
    parts.append(line(s2_x + 10, s2_y + 36, s2_x + s2_w - 10, s2_y + 36, color="#cbd5e1", sw=1))
    parts.append(text(s2_x + s2_w / 2, s2_y + 58, "Слот 12 вже зайнятий!", size=11, bold=True, color="#d97706"))
    parts.append(text(s2_x + s2_w / 2, s2_y + 76, "Виконуємо побітове XOR:", size=11, color=MUTED))
    
    # Формула XOR
    parts.append(rect(s2_x + 15, s2_y + 92, 210, 72, fill="#fffbeb", stroke="#d97706", sw=1, rx=4))
    parts.append(text(s2_x + s2_w / 2, s2_y + 110, "mask = mask ⊕ pivot[12].mask", size=10.5, bold=True))
    parts.append(text(s2_x + s2_w / 2, s2_y + 130, "target = target ⊕ pivot[12].tgt", size=10.5, bold=True))
    parts.append(text(s2_x + s2_w / 2, s2_y + 150, "Операція за 1 такт CPU (64-біт)", size=10, color=MUTED))

    parts.append(text(s2_x + s2_w / 2, s2_y + 184, "Старший 12-й біт зникає (стає 0)", size=11, color=INK))
    parts.append(text(s2_x + s2_w / 2, s2_y + 202, "Наступний біт '1' на позиції col=15", size=11, bold=True, color=FIELD))
    parts.append(text(s2_x + s2_w / 2, s2_y + 224, "Переходимо до слота 15...", size=11, color=MUTED))

    # Стрілка 2 -> 3
    parts.append(arrow(s2_x + s2_w + 5, s2_y + s2_h / 2, s2_x + s2_w + 30, s2_y + s2_h / 2, color=LINE, sw=1.8))

    # Крок 3: Фіксація опорного рядка
    s3_x, s3_y, s3_w, s3_h = 580, 60, 220, 260
    parts.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(s3_x + s3_w / 2, s3_y + 24, "3. Фіксація у порожній слот", size=13, bold=True, color=FIELD))
    parts.append(line(s3_x + 10, s3_y + 36, s3_x + s3_w - 10, s3_y + 36, color="#cbd5e1", sw=1))
    parts.append(text(s3_x + s3_w / 2, s3_y + 60, "Слот 15 вільний!", size=11.5, bold=True, color=FIELD))
    parts.append(rect(s3_x + 15, s3_y + 80, 190, 52, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(s3_x + s3_w / 2, s3_y + 100, "pivot[15] = {mask, target}", size=11, bold=True, color=FIELD))
    parts.append(text(s3_x + s3_w / 2, s3_y + 120, "Рядок успішно закріплено", size=11, color=MUTED))

    parts.append(text(s3_x + s3_w / 2, s3_y + 156, "Після обробки всіх N ключів:", size=11, bold=True, color=INK))
    parts.append(text(s3_x + s3_w / 2, s3_y + 176, "Матриця стає верхньотрикутною", size=11, color=INK))
    parts.append(rect(s3_x + 15, s3_y + 195, 190, 48, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    parts.append(text(s3_x + s3_w / 2, s3_y + 214, "Зворотна підстановка", size=11, bold=True))
    parts.append(text(s3_x + s3_w / 2, s3_y + 232, "обчислює B[i] від M-1 до 0", size=10.5, color=MUTED))

    # Нижній банер про складність
    bx2, by2, bw2, bh2 = 40, 345, 760, 85
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, by2 + 22, "Чому складність строго O(N): ширина стрічки обмежена w бітами (w = 32 або 64)", size=12.5, bold=True, color=INK))
    parts.append(text(W / 2, by2 + 44, "Кожен рядок може зазнати не більше w операцій XOR перед потраплянням у вільний слот", size=11.5, color=MUTED))
    parts.append(text(W / 2, by2 + 64, "Загальна кількість бітових операцій для побудови всього фільтра становить ≤ N · w", size=11.5, color=MUTED))

    render(os.path.join(IMG, "band-gaussian-elimination.svg"), W, H, *parts)


# ── Фігура 3: Швидка перевірка належності (Query Evaluation) ───────────────────
def fig_query_eval():
    W, H = 840, 440
    parts = []
    
    parts.append(text(W / 2, 28, "Перевірка належності ключа (Query) за константний час O(1)", size=16, bold=True))
    
    # 1. Запит ключа K
    kx, ky, kw, kh = 40, 65, 200, 100
    parts.append(rect(kx, ky, kw, kh, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    parts.append(text(kx + kw / 2, ky + 25, "Запит ключа K_query", size=13, bold=True, color=POS))
    parts.append(text(kx + kw / 2, ky + 48, "Хешування 64-бітним хешем:", size=11, color=MUTED))
    parts.append(text(kx + kw / 2, ky + 68, "• Старт: p = Hash_start(K)", size=11, bold=True))
    parts.append(text(kx + kw / 2, ky + 86, "• Маска: c = Hash_mask(K)", size=11, bold=True))

    # Стрілка від ключа до екстракції
    parts.append(arrow(kx + kw, ky + 50, kx + kw + 40, ky + 50, color=LINE, sw=1.8))

    # 2. Зчитування вікна слотів
    wx, wy, ww, wh = 280, 65, 270, 155
    parts.append(rect(wx, wy, ww, wh, fill="#ffffff", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(wx + ww / 2, wy + 24, "Вибірка слотів B[p .. p+w-1]", size=13, bold=True, color=NEG))
    parts.append(line(wx + 10, wy + 35, wx + ww - 10, wy + 35, color="#cbd5e1", sw=1))
    parts.append(text(wx + ww / 2, wy + 55, "Зчитування w послідовних слотів:", size=11, color=MUTED))
    
    # Схематичні комірки пам'яті
    for i in range(4):
        cx = wx + 20 + i * 58
        parts.append(rect(cx, wy + 70, 52, 32, fill="#dbeafe", stroke=NEG, sw=1, rx=3))
        parts.append(text(cx + 26, wy + 89, "B[p+" + str(i) + "]", size=10, bold=True, color=NEG))
    parts.append(text(wx + ww / 2, wy + 120, "... разом w слотів (по r бітів кожен)", size=10.5, color=MUTED))
    parts.append(text(wx + ww / 2, wy + 140, "У Interleaved Ribbon — 1 звернення до L1/L2", size=10.5, bold=True, color=FIELD))

    # Стрілка від слотів до обчислення
    parts.append(arrow(wx + ww, wy + 50, wx + ww + 40, wy + 50, color=LINE, sw=1.8))

    # 3. Скалярний добуток над GF(2)
    dx, dy, dw, dh = 590, 65, 210, 155
    parts.append(rect(dx, dy, dw, dh, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    parts.append(text(dx + dw / 2, dy + 24, "Скалярний добуток ⊕", size=13, bold=True, color=FIELD))
    parts.append(line(dx + 10, dy + 35, dx + dw - 10, dy + 35, color="#cbd5e1", sw=1))
    parts.append(text(dx + dw / 2, dy + 55, "Обчислення відбитка:", size=11, color=MUTED))
    parts.append(rect(dx + 15, dy + 70, 180, 36, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    parts.append(text(dx + dw / 2, dy + 92, "res = ⊕_{j=0}^{w-1} (c[j] · B[p+j])", size=11, bold=True, color=FIELD))
    parts.append(text(dx + dw / 2, dy + 124, "Паралельно для всіх r біт", size=11, color=MUTED))
    parts.append(text(dx + dw / 2, dy + 142, "через SIMD або bit-parallel", size=11, bold=True, color=INK))

    # Стрілка вниз до порівняння
    parts.append(arrow(dx + dw / 2, dy + dh, dx + dw / 2, dy + dh + 35, color=LINE, sw=1.8))

    # 4. Блок перевірки результату
    cx, cy, cw, ch = 200, 260, 600, 80
    parts.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(cx + cw / 2, cy + 24, "Порівняння обчисленого res з очікуваним відбитком f(K_query)", size=12.5, bold=True, color=INK))
    
    # Гілка Рівно
    parts.append(rect(cx + 30, cy + 38, 250, 30, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(cx + 155, cy + 57, "res == f(K)  →  Можливо у множині (TRUE)", size=11, bold=True, color=FIELD))
    
    # Гілка Не рівно
    parts.append(rect(cx + 320, cy + 38, 250, 30, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    parts.append(text(cx + 445, cy + 57, "res != f(K)  →  ТОЧНО немає (FALSE)", size=11, bold=True, color=POS))

    # Нижній висновок
    bx2, by2, bw2, bh2 = 40, 360, 760, 58
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, by2 + 22, "Якщо елемента немає у множині, ймовірність випадкового збігу res == f(K) становить рівно 2^(-r)", size=12, bold=True, color=INK))
    parts.append(text(W / 2, by2 + 42, "При r = 7 бітів FPR ≈ 0.78% при споживанні лише ~7.1 бітів пам'яті на один ключ", size=11.5, color=MUTED))

    render(os.path.join(IMG, "ribbon-query-evaluation.svg"), W, H, *parts)


# ── Фігура 4: Порівняння ймовірнісних фільтрів (Trade-offs) ───────────────────
def fig_tradeoffs():
    W, H = 840, 480
    parts = []
    
    parts.append(text(W / 2, 28, "Порівняння фільтрів при цільовій ймовірності помилки 1% (FPR = 0.01)", size=16, bold=True))
    
    # Заголовки таблиці-діаграми
    cols = [
        ("Тип фільтра", 170),
        ("Пам'ять (біт/ключ)", 150),
        ("Оверхед над порогом", 150),
        ("Звернень до кешу", 140),
        ("Побудова / Вставка", 150),
    ]
    
    table_x, table_y = 40, 60
    cur_x = table_x
    
    # Заголовок таблиці
    for name, cw in cols:
        parts.append(rect(cur_x, table_y, cw, 34, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=0))
        parts.append(text(cur_x + cw / 2, table_y + 22, name, size=11.5, bold=True, color="#ffffff"))
        cur_x += cw

    # Дані фільтрів:
    # (Назва, Пам'ять, Оверхед, Кеш, Побудова, Колір заливки, Колір акценту)
    rows_data = [
        ("Теоретична межа Шеннона", "6.64 біт", "0% (база)", "—", "—", "#f8fafc", MUTED),
        ("Фільтр Блума (Bloom Filter)", "9.60–10.0 біт", "+44% оверхед", "2–7 звернень", "O(1) потокова вставка", "#fee2e2", POS),
        ("Фільтр Кукушки (Cuckoo Filter)", "8.40–9.0 біт", "+26% оверхед", "2 лінії кешу", "Витіснення (eviction loop)", "#fef3c7", "#d97706"),
        ("Xor Filter (Graf & Lemire)", "8.15–8.30 біт", "+23% оверхед", "3 звернення", "O(N) peeling 3-гіперграфа", "#eff6ff", NEG),
        ("Ribbon Filter (Meta / Dillinger)", "7.00–7.30 біт", "+5% оверхед", "1 лінія (Interleaved)", "O(N) Band Gaussian", "#dcfce7", FIELD),
    ]
    
    for r_idx, (fname, fmem, fover, fcache, fbuild, fill_col, text_col) in enumerate(rows_data):
        ry = table_y + 34 + r_idx * 48
        cur_x = table_x
        row_vals = [fname, fmem, fover, fcache, fbuild]
        
        for c_idx, val in enumerate(row_vals):
            cw = cols[c_idx][1]
            is_bold = (r_idx == 4) or (c_idx == 1 and r_idx > 0)
            t_col = text_col if (c_idx == 1 or c_idx == 2 or r_idx == 4) else INK
            parts.append(rect(cur_x, ry, cw, 48, fill=fill_col, stroke="#cbd5e1", sw=1, rx=0))
            parts.append(text(cur_x + cw / 2, ry + 28, val, size=11, bold=is_bold, color=t_col))
            cur_x += cw

    # Нижній блок: Візуальний стовпчиковий графік пам'яті
    gy = 340
    parts.append(text(W / 2, gy, "Порівняльний обсяг пам'яті (менше — краще):", size=13, bold=True))
    
    bars = [
        ("Шеннон (log₂ 1/ε)", 6.64, 6.64 * 28, MUTED, "#94a3b8"),
        ("Ribbon Filter", 7.05, 7.05 * 28, FIELD, "#86efac"),
        ("Xor Filter", 8.20, 8.20 * 28, NEG, "#93c5fd"),
        ("Cuckoo Filter", 8.50, 8.50 * 28, "#d97706", "#fde047"),
        ("Bloom Filter", 9.80, 9.80 * 28, POS, "#fca5a5"),
    ]
    
    for idx, (label, val, bar_w, stroke_c, fill_c) in enumerate(bars):
        by = gy + 20 + idx * 22
        parts.append(text(190, by + 14, label, size=11, color=INK, anchor="end"))
        parts.append(rect(200, by, bar_w, 16, fill=fill_c, stroke=stroke_c, sw=1.2, rx=3))
        parts.append(text(210 + bar_w, by + 13, str(val) + " біт/ключ", size=11, bold=True, color=stroke_c, anchor="start"))

    render(os.path.join(IMG, "filter-tradeoffs-comparison.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_band_matrix()
    fig_band_elimination()
    fig_query_eval()
    fig_tradeoffs()
    print("Всі фігури згенеровано у", IMG)
