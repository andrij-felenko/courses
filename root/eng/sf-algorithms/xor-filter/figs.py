# -*- coding: utf-8 -*-
"""Фігури до теми «Xor-фільтр (XOR Filter)».
Генерація SVG у ./img/ за допомогою svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектура та операція перевірки (Lookup) в Xor-фільтрі ────────
def fig_xor_lookup():
    W, H = 880, 480
    parts = []

    parts.append(text(W / 2, 28, "Архітектура 3-блокового Xor-фільтра та операція перевірки належності", size=16, bold=True))

    # Верхня плашка з описом
    tx, ty, tw, th = 40, 48, 800, 44
    parts.append(rect(tx, ty, tw, th, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, 66, "Умова належності: B[h₀(x)] ⊕ B[h₁(x)] ⊕ B[h₂(x)] == fingerprint(x)", size=13, color=INK, bold=True))
    parts.append(text(W / 2, 82, "Хеш-функції h₀, h₁, h₂ відображають ключ у три неперетинні сегменти масиву B₀, B₁, B₂", size=11.5, color=MUTED))

    # Ключ запиту
    kx, ky, kw, kh = 40, 116, 170, 70
    parts.append(rect(kx, ky, kw, kh, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(kx + kw / 2, ky + 24, "Ключ запиту x", size=13, color=NEG, bold=True))
    parts.append(text(kx + kw / 2, ky + 44, "рядок, UUID або int64", size=11, color=MUTED))
    parts.append(text(kx + kw / 2, ky + 60, "x = \"session-9481\"", size=10.5, color=INK))

    # Блок обчислення хешів
    hx, hy, hw, hh = 260, 110, 190, 130
    parts.append(rect(hx, hy, hw, hh, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(hx + hw / 2, hy + 20, "Хешування ключа", size=12.5, bold=True))
    parts.append(line(hx + 10, hy + 28, hx + hw - 10, hy + 28, color="#e2e8f0", sw=1))
    parts.append(text(hx + 16, hy + 48, "h₀(x) ∈ [0, L)", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(hx + 16, hy + 70, "h₁(x) ∈ [L, 2L)", size=11, color=FIELD, anchor="start", bold=True))
    parts.append(text(hx + 16, hy + 92, "h₂(x) ∈ [2L, 3L)", size=11, color=NEG, anchor="start", bold=True))
    parts.append(text(hx + 16, hy + 116, "f(x) = fingerprint (r біт)", size=11, color="#8b5cf6", anchor="start", bold=True))

    # Стрілка від ключа до хеш-блоку
    parts.append(arrow(kx + kw, ky + kh / 2, hx, hy + 45, color=LINE, sw=1.5))

    # Масив слотів B (розбитий на 3 блоки B0, B1, B2)
    ax, ay, aw, ah = 500, 110, 340, 240
    parts.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    parts.append(text(ax + aw / 2, ay + 20, "Масив слотів B (розмір M = 3 × L, де L = 0.41 · N)", size=12, bold=True))

    # Блок B0
    b0_y = ay + 34
    parts.append(rect(ax + 10, b0_y, aw - 20, 58, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    parts.append(text(ax + 20, b0_y + 18, "Блок B₀ [0 .. L-1]", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(ax + 20, b0_y + 36, "Слот h₀(x) = 0x4A", size=11, color=INK, anchor="start"))
    parts.append(text(ax + aw - 30, b0_y + 36, "B[h₀(x)] = 0x5C", size=11, color=POS, anchor="end", bold=True))

    # Блок B1
    b1_y = ay + 100
    parts.append(rect(ax + 10, b1_y, aw - 20, 58, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(ax + 20, b1_y + 18, "Блок B₁ [L .. 2L-1]", size=11, color=FIELD, anchor="start", bold=True))
    parts.append(text(ax + 20, b1_y + 36, "Слот h₁(x) = L + 0x12", size=11, color=INK, anchor="start"))
    parts.append(text(ax + aw - 30, b1_y + 36, "B[h₁(x)] = 0x3F", size=11, color=FIELD, anchor="end", bold=True))

    # Блок B2
    b2_y = ay + 166
    parts.append(rect(ax + 10, b2_y, aw - 20, 58, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    parts.append(text(ax + 20, b2_y + 18, "Блок B₂ [2L .. 3L-1]", size=11, color=NEG, anchor="start", bold=True))
    parts.append(text(ax + 20, b2_y + 36, "Слот h₂(x) = 2L + 0x7B", size=11, color=INK, anchor="start"))
    parts.append(text(ax + aw - 30, b2_y + 36, "B[h₂(x)] = 0x86", size=11, color=NEG, anchor="end", bold=True))

    # Стрілки від хешів до блоків
    parts.append(arrow(hx + hw, hy + 45, ax + 10, b0_y + 25, color=POS, sw=1.4))
    parts.append(arrow(hx + hw, hy + 67, ax + 10, b1_y + 25, color=FIELD, sw=1.4))
    parts.append(arrow(hx + hw, hy + 89, ax + 10, b2_y + 25, color=NEG, sw=1.4))

    # Блок операції XOR
    xx, xy, xw, xh = 240, 270, 210, 80
    parts.append(rect(xx, xy, xw, xh, fill="#faf5ff", stroke="#8b5cf6", sw=1.5, rx=6))
    parts.append(text(xx + xw / 2, xy + 20, "Операція XOR (⊕)", size=12.5, color="#6b21a8", bold=True))
    parts.append(text(xx + xw / 2, xy + 40, "0x5C ⊕ 0x3F ⊕ 0x86", size=11, color=INK))
    parts.append(text(xx + xw / 2, xy + 60, "= 0xE5 (обчислений відбиток)", size=11.5, color="#6b21a8", bold=True))

    # Стрілки від блоків до XOR
    parts.append(arrow(ax + 10, b0_y + 45, xx + xw, xy + 20, color=POS, sw=1.2))
    parts.append(arrow(ax + 10, b1_y + 45, xx + xw, xy + 40, color=FIELD, sw=1.2))
    parts.append(arrow(ax + 10, b2_y + 45, xx + xw, xy + 60, color=NEG, sw=1.2))

    # Блок порівняння та вердикт
    vx, vy, vw, vh = 40, 270, 170, 80
    parts.append(rect(vx, vy, vw, vh, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(vx + vw / 2, vy + 20, "Порівняння з f(x)", size=12, bold=True))
    parts.append(text(vx + vw / 2, vy + 38, "0xE5 == f(x) (0xE5)?", size=11, color=INK))
    parts.append(text(vx + vw / 2, vy + 62, "ТАК: елемент є", size=12, color=FIELD, bold=True))

    # Стрілка від XOR до порівняння
    parts.append(arrow(xx, xy + xh / 2, vx + vw, vy + vh / 2, color="#8b5cf6", sw=1.5))

    # Нижнє резюме
    bx, by, bw, bh = 40, 390, 800, 70
    parts.append(rect(bx, by, bw, bh, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, by + 22, "Гарантії: Якщо x ∈ S, фільтр завжди повертає ТАК (0% хибнонегативних помилок)", size=12.5, bold=True, color=INK))
    parts.append(text(W / 2, by + 42, "Якщо x ∉ S, результат XOR є псевдовипадковим 8-бітним числом; ймовірність збігу ε = 1/256 ≈ 0.39%", size=11.5, color=MUTED))
    parts.append(text(W / 2, by + 58, "Усього 3 звернення до пам'яті (B₀, B₁, B₂) без розгалужень та складних переходів", size=11.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "xor-filter-lookup.svg"), W, H, *parts)


# ── Фігура 2: Двоетапний алгоритм побудови (Peeling + Back-substitution) ───────
def fig_xor_peeling():
    W, H = 880, 520
    parts = []

    parts.append(text(W / 2, 28, "Двоетапна побудова Xor-фільтра: Лущення гіперграфа та Зворотна підстановка", size=16, bold=True))

    # Ліва колонка: Етап 1 (Лущення 3-гіперграфа)
    e1_x, e1_y, e1_w, e1_h = 40, 56, 380, 390
    parts.append(rect(e1_x, e1_y, e1_w, e1_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(e1_x + e1_w / 2, e1_y + 24, "Етап 1: Лущення 3-гіперграфа (Peeling)", size=13, color=POS, bold=True))
    parts.append(line(e1_x + 10, e1_y + 36, e1_x + e1_w - 10, e1_y + 36, color="#cbd5e1", sw=1))

    # Крок 1.1
    p1_y = e1_y + 50
    parts.append(rect(e1_x + 15, p1_y, e1_w - 30, 70, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    parts.append(text(e1_x + 25, p1_y + 18, "1. Підрахунок степенів комірок", size=11.5, color=POS, anchor="start", bold=True))
    parts.append(text(e1_x + 25, p1_y + 36, "Кожен ключ k додає ребро (h₀(k), h₁(k), h₂(k))", size=11, color=INK, anchor="start"))
    parts.append(text(e1_x + 25, p1_y + 54, "Зберігаємо HCount[c] та HXor[c] (XOR ключів)", size=10.5, color=MUTED, anchor="start"))

    # Крок 1.2
    p2_y = e1_y + 132
    parts.append(rect(e1_x + 15, p2_y, e1_w - 30, 70, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(e1_x + 25, p2_y + 18, "2. Черга комірок степеня 1", size=11.5, color=INK, anchor="start", bold=True))
    parts.append(text(e1_x + 25, p2_y + 36, "Знаходимо всі слоти c, де HCount[c] == 1", size=11, color=INK, anchor="start"))
    parts.append(text(e1_x + 25, p2_y + 54, "У таких слотах єдиний ключ k = HXor[c]", size=10.5, color=MUTED, anchor="start"))

    # Крок 1.3
    p3_y = e1_y + 214
    parts.append(rect(e1_x + 15, p3_y, e1_w - 30, 80, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    parts.append(text(e1_x + 25, p3_y + 18, "3. Видалення ребра та запис у стек", size=11.5, color=NEG, anchor="start", bold=True))
    parts.append(text(e1_x + 25, p3_y + 36, "Кладемо пару (k, c) у стек LIFO", size=11, color=INK, anchor="start"))
    parts.append(text(e1_x + 25, p3_y + 52, "Зменшуємо лічильники для двох інших слотів k", size=10.5, color=INK, anchor="start"))
    parts.append(text(e1_x + 25, p3_y + 68, "Нові слоти зі степенем 1 додаємо в чергу", size=10.5, color=MUTED, anchor="start"))

    # Результат етапу 1
    p4_y = e1_y + 306
    parts.append(rect(e1_x + 15, p4_y, e1_w - 30, 70, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(e1_x + 25, p4_y + 20, "Успіх лущення: Усі N ключів у стеку!", size=11.5, color=FIELD, anchor="start", bold=True))
    parts.append(text(e1_x + 25, p4_y + 38, "Якщо черга спорожніла раніше (є 2-ядро) —", size=10.5, color=INK, anchor="start"))
    parts.append(text(e1_x + 25, p4_y + 54, "змінюємо seed хешування і повторюємо (O(N))", size=10.5, color=MUTED, anchor="start"))

    # Стек LIFO посередині (вертикальна колонка зв'язку)
    sx, sy, sw, sh = 445, 120, 70, 240
    parts.append(rect(sx, sy, sw, sh, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    parts.append(text(sx + sw / 2, sy - 10, "Стек LIFO", size=12, bold=True, color="#b45309"))
    parts.append(text(sx + sw / 2, sy + 25, "(k_N, c_N)", size=10.5, color="#b45309", bold=True))
    parts.append(text(sx + sw / 2, sy + 45, "(k_N-1, c_N-1)", size=10, color=MUTED))
    parts.append(text(sx + sw / 2, sy + 120, "⋮ (N пар)", size=12, bold=True, color="#b45309"))
    parts.append(text(sx + sw / 2, sy + 195, "(k₂, c₂)", size=10, color=MUTED))
    parts.append(text(sx + sw / 2, sy + 220, "(k₁, c₁)", size=10.5, color="#b45309", bold=True))

    # Стрілка запису в стек
    parts.append(arrow(e1_x + e1_w - 15, p3_y + 40, sx, sy + 60, color=NEG, sw=1.5))
    parts.append(text(430, sy + 45, "push", size=10, color=NEG, bold=True, anchor="end"))

    # Права колонка: Етап 2 (Зворотна підстановка)
    e2_x, e2_y, e2_w, e2_h = 540, 56, 300, 390
    parts.append(rect(e2_x, e2_y, e2_w, e2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(e2_x + e2_w / 2, e2_y + 24, "Етап 2: Зворотна підстановка", size=13, color=FIELD, bold=True))
    parts.append(line(e2_x + 10, e2_y + 36, e2_x + e2_w - 10, e2_y + 36, color="#cbd5e1", sw=1))

    # Крок 2.1
    b1_y = e2_y + 50
    parts.append(rect(e2_x + 15, b1_y, e2_w - 30, 85, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(e2_x + 25, b1_y + 18, "1. Витягування зі стеку (pop)", size=11.5, color=INK, anchor="start", bold=True))
    parts.append(text(e2_x + 25, b1_y + 36, "Зчитуємо пару (k, c) у зворотному", size=10.5, color=INK, anchor="start"))
    parts.append(text(e2_x + 25, b1_y + 52, "порядку до моменту лущення.", size=10.5, color=INK, anchor="start"))
    parts.append(text(e2_x + 25, b1_y + 70, "Слот c був ізольованим для k!", size=10.5, color=POS, anchor="start", bold=True))

    # Крок 2.2
    b2_y = e2_y + 147
    parts.append(rect(e2_x + 15, b2_y, e2_w - 30, 110, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(e2_x + 25, b2_y + 18, "2. Присвоєння значення B[c]", size=11.5, color=FIELD, anchor="start", bold=True))
    parts.append(text(e2_x + 25, b2_y + 36, "Знаходимо дві інші позиції k:", size=10.5, color=INK, anchor="start"))
    parts.append(text(e2_x + 25, b2_y + 52, "c_a та c_b (вони вже мають фінал)", size=10.5, color=MUTED, anchor="start"))
    parts.append(text(e2_x + 25, b2_y + 74, "B[c] = f(k) ⊕ B[c_a] ⊕ B[c_b]", size=11.5, color=FIELD, anchor="start", bold=True))
    parts.append(text(e2_x + 25, b2_y + 94, "Рівняння для k точно виконано!", size=10.5, color=POS, anchor="start"))

    # Крок 2.3
    b3_y = e2_y + 269
    parts.append(rect(e2_x + 15, b3_y, e2_w - 30, 95, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    parts.append(text(e2_x + 25, b3_y + 18, "3. Готовий фільтр", size=11.5, color=NEG, anchor="start", bold=True))
    parts.append(text(e2_x + 25, b3_y + 36, "Порожні (незадіяні) слоти B", size=10.5, color=INK, anchor="start"))
    parts.append(text(e2_x + 25, b3_y + 52, "заповнюються нулями.", size=10.5, color=INK, anchor="start"))
    parts.append(text(e2_x + 25, b3_y + 72, "Фільтр стає незмінним (immutable)", size=10.5, color=MUTED, anchor="start"))

    # Стрілка зчитування зі стеку
    parts.append(arrow(sx + sw, sy + 60, e2_x + 15, b1_y + 40, color=FIELD, sw=1.5))
    parts.append(text(sx + sw + 5, sy + 45, "pop", size=10, color=FIELD, bold=True, anchor="start"))

    # Нижній висновок
    bx, by, bw, bh = 40, 458, 800, 50
    parts.append(rect(bx, by, bw, bh, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(W / 2, by + 20, "Часова складність побудови: O(N) у середньому завдяки фактору розширення M = 1.23 · N", size=12.5, bold=True, color=INK))
    parts.append(text(W / 2, by + 38, "При c = 1.23 ймовірність успішного лущення з першої спроби перевищує 80%, а з 3 спроб — понад 99%", size=11, color=MUTED))

    render(os.path.join(IMG, "xor-filter-peeling.svg"), W, H, *parts)


# ── Фігура 3: Порівняння ймовірнісних фільтрів належності ──────────────────────
def fig_xor_tradeoffs():
    W, H = 880, 480
    parts = []

    parts.append(text(W / 2, 28, "Порівняння архітектур: Bloom, Cuckoo, XOR та Ribbon фільтри", size=16, bold=True))

    # Стовпчики таблиці
    cols = [
        ("Властивість", 170),
        ("Bloom Filter", 170),
        ("Cuckoo Filter", 170),
        ("Xor Filter", 180),
        ("Ribbon Filter", 150),
    ]

    x_start = 40
    y_start = 56
    row_h = 50

    # Шапка таблиці
    cx = x_start
    for title, w in cols:
        bg = "#e2e8f0" if title == "Властивість" else "#dbeafe" if "Xor" in title else "#f1f5f9"
        tc = NEG if "Xor" in title else INK
        parts.append(rect(cx, y_start, w, 40, fill=bg, stroke=LINE, sw=1.2, rx=0))
        parts.append(text(cx + w / 2, y_start + 25, title, size=12, bold=True, color=tc))
        cx += w

    # Рядки таблиці
    rows_data = [
        ("Пам'ять при 1% FPR", "9.6 – 10.0 біт/ключ", "8.4 – 9.0 біт/ключ", "8.15 – 8.30 біт/ключ", "7.1 – 7.3 біт/ключ"),
        ("Звернення до кешу (запит)", "k звернень (7–10)", "2 звернення", "3 звернення (1 якщо блок)", "1 звернення"),
        ("Динамічні вставки", "Так (без видалень)", "Так (вставка + видалення)", "Ні (статичний набір)", "Ні (статичний набір)"),
        ("Швидкість запиту", "Помірна (багато хешів)", "Висока (2 комірки)", "Дуже висока (3 XOR)", "Висока (маска)"),
        ("Швидкість побудови", "Дуже швидка O(N)", "Повільна при >90% заповн.", "Швидка O(N) лущення", "O(N · w) Гаусс"),
        ("Розмір структури", "Фіксований бітовий масив", "Таблиця з бакетами", "3 сегменти слотів", "Стрічкові бакети"),
        ("Незмінність (Immutability)", "Можна дописувати біти", "Мутабельний", "Незмінний після білду", "Незмінний після білду"),
    ]

    curr_y = y_start + 40
    for r_idx, r_data in enumerate(rows_data):
        cx = x_start
        prop_name = r_data[0]
        v_bloom = r_data[1]
        v_cuckoo = r_data[2]
        v_xor = r_data[3]
        v_ribbon = r_data[4]

        # Підсвітка для Xor Filter
        row_bg = "#ffffff" if r_idx % 2 == 0 else "#f8fafc"
        
        parts.append(rect(cx, curr_y, cols[0][1], row_h, fill="#f1f5f9", stroke=LINE, sw=0.8, rx=0))
        parts.append(text(cx + 12, curr_y + 30, prop_name, size=11, bold=True, color=INK, anchor="start"))
        cx += cols[0][1]

        parts.append(rect(cx, curr_y, cols[1][1], row_h, fill=row_bg, stroke=LINE, sw=0.8, rx=0))
        parts.append(text(cx + cols[1][1] / 2, curr_y + 30, v_bloom, size=10.5, color=INK))
        cx += cols[1][1]

        parts.append(rect(cx, curr_y, cols[2][1], row_h, fill=row_bg, stroke=LINE, sw=0.8, rx=0))
        parts.append(text(cx + cols[2][1] / 2, curr_y + 30, v_cuckoo, size=10.5, color=INK))
        cx += cols[2][1]

        # Xor колонка з легким виділенням
        parts.append(rect(cx, curr_y, cols[3][1], row_h, fill="#eff6ff" if r_idx % 2 == 0 else "#e0f2fe", stroke=NEG, sw=1.2, rx=0))
        parts.append(text(cx + cols[3][1] / 2, curr_y + 30, v_xor, size=11, bold=True, color=NEG))
        cx += cols[3][1]

        parts.append(rect(cx, curr_y, cols[4][1], row_h, fill=row_bg, stroke=LINE, sw=0.8, rx=0))
        parts.append(text(cx + cols[4][1] / 2, curr_y + 30, v_ribbon, size=10.5, color=INK))
        
        curr_y += row_h

    # Нижня рамка з висновком
    bx, by, bw, bh = 40, curr_y + 12, 800, 48
    parts.append(rect(bx, by, bw, bh, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    parts.append(text(W / 2, by + 20, "Ніша Xor-фільтра: Незмінні набори даних (SSTables, статичні індекси, словники, CD-ROM/RO-образи)", size=12, bold=True, color=FIELD))
    parts.append(text(W / 2, by + 36, "Переваги: на 20% компактніший за Bloom, на 20–30% швидший за Cuckoo, вільний від колізій переміщення", size=11, color=INK))

    render(os.path.join(IMG, "xor-vs-bloom-cuckoo-tradeoffs.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_xor_lookup()
    fig_xor_peeling()
    fig_xor_tradeoffs()
    print("XOR filter figures generated successfully in ./img/")
