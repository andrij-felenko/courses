# -*- coding: utf-8 -*-
"""Фігури до теми «Суматор і перенос».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_half_and_full_adder():
    """Порівняння структури напівсуматора та повного суматора."""
    W, H = 840, 400
    f = []

    # Заголовки половин
    f.append(text(210, 25, "Напівсуматор (Half Adder)", size=16, bold=True, color=INK))
    f.append(text(210, 45, "2 входи → 2 виходи (без Cin)", size=12, color=MUTED))

    f.append(text(630, 25, "Повний суматор (Full Adder)", size=16, bold=True, color=INK))
    f.append(text(630, 45, "3 входи (A, B, Cin) → 2 виходи (S, Cout)", size=12, color=MUTED))

    # Розділювач
    f.append(line(420, 15, 420, 385, color=MUTED, sw=1.2, dash="4,4"))

    # --- Ліва частина: Напівсуматор ---
    # Входи
    f.append(line(50, 110, 110, 110, color=LINE, sw=1.8))
    f.append(text(40, 114, "A", size=14, bold=True, color=INK))
    f.append(line(50, 170, 110, 170, color=LINE, sw=1.8))
    f.append(text(40, 174, "B", size=14, bold=True, color=INK))

    # Розгалуження входів
    f.append(circle(80, 110, 3.5, fill=LINE, stroke=LINE))
    f.append(circle(95, 170, 3.5, fill=LINE, stroke=LINE))
    f.append(line(80, 110, 80, 240, color=LINE, sw=1.8))
    f.append(line(80, 240, 110, 240, color=LINE, sw=1.8))
    f.append(line(95, 170, 95, 290, color=LINE, sw=1.8))
    f.append(line(95, 290, 110, 290, color=LINE, sw=1.8))

    # Блоки XOR та AND
    f.append(fitbox(110, 100, 90, 80, "XOR\n(A ⊕ B)", size=13, fill="#eaf0fd", stroke=NEG, bold=True))
    f.append(fitbox(110, 230, 90, 80, "AND\n(A · B)", size=13, fill="#fdecea", stroke=POS, bold=True))

    # Виходи напівсуматора
    f.append(arrow(200, 140, 340, 140, color=NEG, sw=1.8))
    f.append(text(370, 144, "S (Сума)", size=13, bold=True, color=NEG))

    f.append(arrow(200, 270, 340, 270, color=POS, sw=1.8))
    f.append(text(375, 274, "Cout (Перенос)", size=13, bold=True, color=POS))

    # Пояснення внизу ліворуч
    f.append(text(210, 350, "S = A ⊕ B,  Cout = A · B", size=13, bold=True, color=INK))
    f.append(text(210, 370, "Не має входу для переносу з молодшого біта", size=11, color=MUTED))

    # --- Права частина: Повний суматор на 2 напівсуматорах і OR ---
    # Блок HA 1
    f.append(fitbox(460, 90, 100, 100, "Напівсуматор 1\n(HA₁)", size=12, fill="#f4f6f8", stroke=LINE, bold=True))
    # Блок HA 2
    f.append(fitbox(600, 140, 100, 100, "Напівсуматор 2\n(HA₂)", size=12, fill="#f4f6f8", stroke=LINE, bold=True))
    # Блок OR
    f.append(fitbox(730, 250, 80, 60, "OR\n(+)", size=13, fill="#fdecea", stroke=POS, bold=True))

    # Входи A та B до HA1
    f.append(arrow(430, 120, 460, 120, color=LINE, sw=1.8))
    f.append(text(420, 124, "A", size=13, bold=True, color=INK))
    f.append(arrow(430, 160, 460, 160, color=LINE, sw=1.8))
    f.append(text(420, 164, "B", size=13, bold=True, color=INK))

    # Вхід Cin до HA2
    f.append(arrow(430, 210, 600, 210, color=LINE, sw=1.8))
    f.append(text(420, 214, "Cin", size=13, bold=True, color=POS))

    # З'єднання між HA1 і HA2
    f.append(arrow(560, 120, 600, 160, color=NEG, sw=1.8))
    f.append(text(580, 130, "A⊕B", size=10, color=NEG))

    # Вихід S з HA2
    f.append(arrow(700, 190, 800, 190, color=NEG, sw=1.8))
    f.append(text(815, 194, "S", size=14, bold=True, color=NEG))

    # Переноси з HA1 та HA2 до OR
    f.append(line(560, 170, 580, 170, color=POS, sw=1.8))
    f.append(line(580, 170, 580, 270, color=POS, sw=1.8))
    f.append(arrow(580, 270, 730, 270, color=POS, sw=1.8))
    f.append(text(635, 260, "A·B", size=10, color=POS))

    f.append(line(700, 220, 715, 220, color=POS, sw=1.8))
    f.append(line(715, 220, 715, 290, color=POS, sw=1.8))
    f.append(arrow(715, 290, 730, 290, color=POS, sw=1.8))
    f.append(text(675, 305, "Cin·(A⊕B)", size=10, color=POS))

    # Вихід Cout
    f.append(arrow(810, 280, 830, 280, color=POS, sw=1.8))
    f.append(text(820, 305, "Cout", size=13, bold=True, color=POS))

    # Формула внизу
    f.append(text(630, 350, "S = A ⊕ B ⊕ Cin,  Cout = (A · B) + (Cin · (A ⊕ B))", size=12, bold=True, color=INK))
    f.append(text(630, 370, "Повний каскад забезпечує наскрізне додавання розрядів", size=11, color=MUTED))

    render(os.path.join(OUT, 'half-and-full-adder.svg'), W, H, *f)


def fig_ripple_carry_4bit():
    """Ланцюговий суматор (Ripple Carry Adder) на 4 розряди та критичний шлях переносу."""
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 28, "4-розрядний ланцюговий суматор (Ripple Carry Adder, RCA)", size=16, bold=True, color=INK))
    f.append(text(W / 2, 48, "Критичний шлях: перенос послідовно пробігає крізь кожен повний суматор", size=12, color=MUTED))

    # 4 блоки повних суматорів справа наліво (від біта 0 до біта 3)
    n = 4
    bw, bh = 110, 110
    gap = 65
    bx0 = 80
    by = 100

    # Початковий перенос C0 справа
    f.append(arrow(bx0 + n * (bw + gap) + 40, by + bh / 2, bx0 + (n - 1) * (bw + gap) + bw, by + bh / 2, color=POS, sw=2.2))
    f.append(text(bx0 + n * (bw + gap) + 60, by + bh / 2 + 5, "C₀ (Cin)", size=13, bold=True, color=POS))

    for i in range(n):
        # x-координата для розряду i (3, 2, 1, 0 зліва направо)
        x = bx0 + (n - 1 - i) * (bw + gap)
        f.append(fitbox(x, by, bw, bh, f"Повний\nсуматор {i}\n(FA{i})", size=13, fill="#fdfefe", stroke=LINE, bold=True))

        # Входи Ai, Bi згори
        f.append(arrow(x + bw * 0.35, by - 35, x + bw * 0.35, by, color=INK, sw=1.8))
        f.append(text(x + bw * 0.35, by - 42, f"A{i}", size=13, bold=True, color=INK))

        f.append(arrow(x + bw * 0.65, by - 35, x + bw * 0.65, by, color=INK, sw=1.8))
        f.append(text(x + bw * 0.65, by - 42, f"B{i}", size=13, bold=True, color=INK))

        # Вихід суми Si знизу
        f.append(arrow(x + bw / 2, by + bh, x + bw / 2, by + bh + 45, color=NEG, sw=1.8))
        f.append(text(x + bw / 2, by + bh + 62, f"S{i}", size=14, bold=True, color=NEG))

        # Перенос між блоками (C_{i+1})
        if i < n - 1:
            xl = bx0 + (n - 2 - i) * (bw + gap) + bw
            xr = x
            f.append(arrow(xr, by + bh / 2, xl, by + bh / 2, color=POS, sw=2.5))
            f.append(text((xr + xl) / 2, by + bh / 2 - 10, f"C{i+1}", size=12, bold=True, color=POS))

    # Вихідний перенос C4 зліва
    f.append(arrow(bx0, by + bh / 2, bx0 - 50, by + bh / 2, color=POS, sw=2.5))
    f.append(text(bx0 - 65, by + bh / 2 + 5, "C₄ (Cout)", size=13, bold=True, color=POS))

    # Червона стрічка критичного шляху
    f.append(text(W / 2, 290, "Затримка: t_total = t_setup + 4 · t_carry + t_sum  (лінійна складність O(N))", size=13, bold=True, color=POS))
    f.append(text(W / 2, 315, "Кожен наступний біт чекає стабілізації переносу з попереднього розряду", size=11, color=MUTED))

    render(os.path.join(OUT, 'ripple-carry-4bit.svg'), W, H, *f)


def fig_generate_propagate_cell():
    """Логіка генерації (G) і проходження (P) переносу для одного розряду."""
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 25, "Формування сигналів генерації (G) і проходження (P)", size=16, bold=True, color=INK))
    f.append(text(W / 2, 45, "Аналіз стану розряду заздалегідь без очікування сигналу Cin", size=12, color=MUTED))

    # Ліва частина: таблиця режимів розряду
    f.append(text(200, 80, "Таблиця режимів бітової пари (Aᵢ, Bᵢ)", size=14, bold=True, color=INK))

    tx = 40
    ty = 100
    tw = 320
    th = 230
    f.append(rect(tx, ty, tw, th, fill="#fdfefe", stroke=MUTED, sw=1.2))

    # Шапка таблиці
    f.append(rect(tx, ty, tw, 35, fill="#eef2f7", stroke=MUTED, sw=1.2))
    f.append(text(tx + 40, ty + 23, "Aᵢ  Bᵢ", size=12, bold=True, color=INK))
    f.append(text(tx + 125, ty + 23, "Cout (при Cin)", size=12, bold=True, color=INK))
    f.append(text(tx + 240, ty + 23, "Режим і назва", size=12, bold=True, color=INK))

    rows = [
        ("0   0", "завжди 0", "Гасіння (Kill, K=1)", "#f4f6f8", INK),
        ("0   1", "дорівнює Cin", "Проходження (P=1)", "#eaf0fd", NEG),
        ("1   0", "дорівнює Cin", "Проходження (P=1)", "#eaf0fd", NEG),
        ("1   1", "завжди 1", "Генерація (G=1)", "#fdecea", POS),
    ]

    for idx, (ab, cout, mode, bg_col, txt_col) in enumerate(rows):
        ry = ty + 35 + idx * 48
        f.append(rect(tx, ry, tw, 48, fill=bg_col, stroke="#e2e8f0", sw=1))
        f.append(text(tx + 40, ry + 28, ab, size=12, bold=True, color=INK))
        f.append(text(tx + 125, ry + 28, cout, size=11, color=INK))
        f.append(text(tx + 240, ry + 28, mode, size=11, bold=True, color=txt_col))

    # Права частина: Схема формування G, P, Cout і Суми
    f.append(text(610, 80, "Логічна комірка розряду", size=14, bold=True, color=INK))

    # Входи Ai, Bi
    f.append(line(420, 120, 470, 120, color=LINE, sw=1.8))
    f.append(text(410, 124, "Aᵢ", size=13, bold=True, color=INK))

    f.append(line(420, 170, 470, 170, color=LINE, sw=1.8))
    f.append(text(410, 174, "Bᵢ", size=13, bold=True, color=INK))

    # Точки розгалуження
    f.append(circle(440, 120, 3.5, fill=LINE, stroke=LINE))
    f.append(circle(455, 170, 3.5, fill=LINE, stroke=LINE))
    f.append(line(440, 120, 440, 240, color=LINE, sw=1.8))
    f.append(line(440, 240, 470, 240, color=LINE, sw=1.8))
    f.append(line(455, 170, 455, 290, color=LINE, sw=1.8))
    f.append(line(455, 290, 470, 290, color=LINE, sw=1.8))

    # Блоки G та P
    f.append(fitbox(470, 110, 90, 70, "AND\nGᵢ = Aᵢ·Bᵢ", size=12, fill="#fdecea", stroke=POS, bold=True))
    f.append(fitbox(470, 230, 90, 70, "XOR\nPᵢ = Aᵢ⊕Bᵢ", size=12, fill="#eaf0fd", stroke=NEG, bold=True))

    # Блок обчислення переносу: Cout = G + P·Cin
    f.append(fitbox(640, 150, 140, 90, "Логіка переносу\nCᵢ₊₁ = Gᵢ + Pᵢ·Cᵢ", size=12, fill="#eafaf1", stroke=FIELD, bold=True))

    # Блок суми: S = P ⊕ Cin
    f.append(fitbox(640, 290, 140, 70, "XOR (Сума)\nSᵢ = Pᵢ ⊕ Cᵢ", size=12, fill="#f4f6f8", stroke=LINE, bold=True))

    # З'єднання G до переносу
    f.append(arrow(560, 145, 640, 175, color=POS, sw=1.8))

    # З'єднання P до переносу та суми
    f.append(line(560, 265, 590, 265, color=NEG, sw=1.8))
    f.append(circle(590, 265, 3.5, fill=NEG, stroke=NEG))
    f.append(arrow(590, 265, 640, 210, color=NEG, sw=1.8))
    f.append(arrow(590, 265, 640, 315, color=NEG, sw=1.8))

    # Вхід Cin
    f.append(line(420, 360, 610, 360, color=FIELD, sw=1.8))
    f.append(text(410, 364, "Cᵢ", size=13, bold=True, color=FIELD))
    f.append(circle(610, 360, 3.5, fill=FIELD, stroke=FIELD))
    f.append(arrow(610, 360, 640, 225, color=FIELD, sw=1.8))
    f.append(arrow(610, 360, 640, 340, color=FIELD, sw=1.8))

    # Виходи
    f.append(arrow(780, 195, 830, 195, color=POS, sw=2))
    f.append(text(810, 180, "Cᵢ₊₁", size=14, bold=True, color=POS))

    f.append(arrow(780, 325, 830, 325, color=NEG, sw=2))
    f.append(text(810, 310, "Sᵢ", size=14, bold=True, color=NEG))

    # Нижній висновок
    f.append(text(W / 2, 395, "Сигнали Gᵢ та Pᵢ готуються миттєво й паралельно для всіх розрядів слова", size=12, bold=True, color=INK))

    render(os.path.join(OUT, 'generate-propagate-cell.svg'), W, H, *f)


def fig_kogge_stone_8bit():
    """Паралельне префіксне дерево Коггі-Стоуна (Kogge-Stone) на 8 бітів."""
    W, H = 840, 450
    f = []

    f.append(text(W / 2, 25, "8-розрядний паралельний префіксний суматор Коггі-Стоуна (Kogge-Stone)", size=16, bold=True, color=INK))
    f.append(text(W / 2, 45, "Глибина дерева: ⌈log₂ 8⌉ = 3 логічні яруси префіксного об'єднання", size=12, color=MUTED))

    # 8 колонок для бітів від 7 до 0 зліва направо
    n = 8
    col_w = 85
    start_x = 110

    # Шари (y-координати)
    y_in = 80       # Входи
    y_st0 = 120     # Рівень 0: Генерація початкових (G, P)
    y_st1 = 200     # Рівень 1: Префіксний зсув 1
    y_st2 = 280     # Рівень 2: Префіксний зсув 2
    y_st3 = 350     # Рівень 3: Префіксний зсув 4
    y_out = 410     # Виходи суми Si

    # Підписи розрядів згори
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        f.append(text(cx, y_in - 10, f"A{i}, B{i}", size=12, bold=True, color=INK))
        f.append(arrow(cx, y_in, cx, y_st0 - 15, color=LINE, sw=1.5))

    # Ярус 0: Генерація (G_i, P_i)
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        f.append(fitbox(cx - 30, y_st0 - 15, 60, 30, f"g{i}, p{i}", size=11, fill="#f4f6f8", stroke=LINE, bold=True))

    # Стрілки вертикальні вниз крізь рівні
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        f.append(line(cx, y_st0 + 15, cx, y_out - 15, color=MUTED, sw=1.2, dash="3,3"))

    # Ярус 1 (Крок = 1): вузли для всіх i >= 1
    f.append(text(40, y_st1 + 10, "Ярус 1\n(зсув 1)", size=11, bold=True, color=MUTED))
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        if i >= 1:
            cx_prev = start_x + (n - 1 - (i - 1)) * col_w
            # Вузол об'єднання (чорна крапка / префіксна комірка)
            f.append(fitbox(cx - 24, y_st1 - 12, 48, 24, "●", size=14, fill="#fdecea", stroke=POS, bold=True))
            # Зв'язок від (i-1)
            f.append(arrow(cx_prev, y_st0 + 15, cx, y_st1 - 12, color=POS, sw=1.5))
        else:
            # Буферна комірка
            f.append(circle(cx, y_st1, 5, fill=MUTED, stroke=MUTED))

    # Ярус 2 (Крок = 2): вузли для всіх i >= 2
    f.append(text(40, y_st2 + 10, "Ярус 2\n(зсув 2)", size=11, bold=True, color=MUTED))
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        if i >= 2:
            cx_prev = start_x + (n - 1 - (i - 2)) * col_w
            f.append(fitbox(cx - 24, y_st2 - 12, 48, 24, "●", size=14, fill="#eafaf1", stroke=FIELD, bold=True))
            f.append(arrow(cx_prev, y_st1 + 12, cx, y_st2 - 12, color=FIELD, sw=1.5))
        else:
            f.append(circle(cx, y_st2, 5, fill=MUTED, stroke=MUTED))

    # Ярус 3 (Крок = 4): вузли для всіх i >= 4
    f.append(text(40, y_st3 + 10, "Ярус 3\n(зсув 4)", size=11, bold=True, color=MUTED))
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        if i >= 4:
            cx_prev = start_x + (n - 1 - (i - 4)) * col_w
            f.append(fitbox(cx - 24, y_st3 - 12, 48, 24, "●", size=14, fill="#eaf0fd", stroke=NEG, bold=True))
            f.append(arrow(cx_prev, y_st2 + 12, cx, y_st3 - 12, color=NEG, sw=1.5))
        else:
            f.append(circle(cx, y_st3, 5, fill=MUTED, stroke=MUTED))

    # Виходи суми Si
    for i in range(n):
        cx = start_x + (n - 1 - i) * col_w
        f.append(arrow(cx, y_st3 + 12 if i >= 4 else (y_st2 + 12 if i >= 2 else (y_st1 + 12 if i >= 1 else y_st0 + 15)), cx, y_out - 5, color=LINE, sw=1.8))
        f.append(fitbox(cx - 20, y_out - 5, 40, 25, f"S{i}", size=12, fill="#fdfefe", stroke=NEG, bold=True))

    render(os.path.join(OUT, 'kogge-stone-8bit.svg'), W, H, *f)


if __name__ == '__main__':
    fig_half_and_full_adder()
    fig_ripple_carry_4bit()
    fig_generate_propagate_cell()
    fig_kogge_stone_8bit()
    print("Всі фігури згенеровано успішно.")
