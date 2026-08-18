# -*- coding: utf-8 -*-
"""Фігури до теми «Редефініція SI 2019».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_PURPLE = "#8e44ad"
COLOR_ORANGE = "#d35400"
COLOR_DARK = "#2c3e50"


def fig_si_constants_tree():
    """Фігура 1: Дерево 7 фундаментальних констант SI 2019 та електромагнітні одиниці."""
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    # Заголовок
    f.append(text(W / 2, 28, "Фундаментальні константи SI (2019) та електромагнітна ієрархія", size=16, bold=True, color=INK))

    # Верхній блок: Джерело фіксації констант
    b_top, w_top, h_top = textbox(W / 2, 62, "Фіксовані фундаментальні константи природи (без похибки)",
                                  size=13, pad=7, fill="#ebf5fb", stroke="#a9cce3", sw=1.4, bold=True, color=COLOR_BLUE)
    f.append(b_top)

    # 4 ключові константи електромагнетизму та механіки (4 блоки в ряд)
    constants = [
        ("Δν_Cs", "9 192 631 770 Гц", "Частота Cs-133", "#eafaf1", COLOR_GREEN, 115),
        ("c", "299 792 458 м/с", "Швидкість світла", "#eafaf1", COLOR_GREEN, 310),
        ("h", "6.626 070 15 × 10⁻³⁴ Дж·с", "Стала Планка", "#f4ecf7", COLOR_PURPLE, 510),
        ("e", "1.602 176 634 × 10⁻¹⁹ Кл", "Елементарний заряд", "#fef9e7", COLOR_ORANGE, 705)
    ]

    for sym, val, desc, bg_c, str_c, cx in constants:
        # Картка константи
        f.append(rect(cx - 85, 105, 170, 78, fill=bg_c, stroke=str_c, sw=1.6, rx=6))
        f.append(text(cx, 125, sym, size=15, bold=True, color=str_c))
        f.append(text(cx, 145, val, size=10, bold=True, color=INK))
        f.append(text(cx, 165, desc, size=10, color=MUTED))

        # Стрілка вниз до базових одиниць
        f.append(arrow(cx, 183, cx, 212, color=str_c, sw=1.5))

    # Рядок базових одиниць (Секунда, Метр, Кілограм, Ампер)
    base_units = [
        ("Секунда (с)", "одиниця часу", 115),
        ("Метр (м)", "одиниця довжини", 310),
        ("Кілограм (кг)", "одиниця маси", 510),
        ("Ампер (А)", "1 А = e / (1.602...×10⁻¹⁹ с)", 705)
    ]

    for uname, udesc, cx in base_units:
        f.append(rect(cx - 80, 215, 160, 52, fill=FILL, stroke=LINE, sw=1.5, rx=5))
        f.append(text(cx, 233, uname, size=12, bold=True, color=INK))
        f.append(text(cx, 252, udesc, size=9.5, color=MUTED))

    # Міжкомпонентні стрілки залежностей
    # c залежить від Δν_Cs (с)
    f.append(line(195, 241, 230, 241, color=MUTED, sw=1.2, dash="3,3"))
    # h залежить від м і с (Кілограм)
    f.append(line(390, 241, 430, 241, color=MUTED, sw=1.2, dash="3,3"))
    # e і s визначають Ампер
    f.append(line(590, 241, 625, 241, color=MUTED, sw=1.2, dash="3,3"))

    # Стрілки від базових одиниць до похідних квантових еталонів електромагнетизму
    f.append(arrow(510, 267, 430, 310, color=COLOR_PURPLE, sw=1.5)) # кг -> В, Ом
    f.append(arrow(705, 267, 570, 310, color=COLOR_ORANGE, sw=1.5)) # А -> В, Ом

    # Нижні квантові еталони (Вольт та Ом)
    b_v, w_v, h_v = textbox(340, 345, "Вольт (В) — Ефект Джозефсона\nKJ = 2e / h = 483 597.848... ГГц/В\n(Точний зв'язок частоти й напруги)",
                            size=11, pad=8, fill="#f4ecf7", stroke=COLOR_PURPLE, sw=1.4)
    f.append(b_v)

    b_r, w_r, h_r = textbox(630, 345, "Ом (Ом) — Квантовий ефект Холла\nRK = h / e² = 25 812.807... Ом\n(Точний квантовий опір)",
                            size=11, pad=8, fill="#fef9e7", stroke=COLOR_ORANGE, sw=1.4)
    f.append(b_r)

    # Підпис знизу
    f.append(text(W / 2, 415, "Фіксація h та e робить еталони Вольта і Ома абсолютно точними в SI", size=11, bold=True, color=COLOR_BLUE))

    return render(os.path.join(IMG_DIR, "si-constants-tree.svg"), W, H, *f)


def fig_before_vs_after_2019():
    """Фігура 2: Порівняння структури SI до та після редефініції 2019 року."""
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 26, "Фундаментальна зміна підвалин SI: до та після 20 травня 2019 року", size=15, bold=True, color=INK))

    midx = W / 2
    f.append(line(midx, 48, midx, H - 25, color="#d6dde6", sw=1.5, dash="6,4"))

    # --- ЛІВА ЧАСТИНА: До 2019 року ---
    cx_before = 205
    f.append(text(cx_before, 54, "До 2019 року (Класична SI)", size=14, bold=True, color=COLOR_RED))

    cards_before = [
        ("Означення Ампера (1948)", "Через безкінечно довгі паралельні дроти\nу вакуумі на відстані 1 м", "#fdf2e9", COLOR_ORANGE),
        ("Магнітна стала μ₀", "μ₀ = 4π × 10⁻⁷ Гн/м (ТОЧНА за означенням)\nε₀ = 1/(μ₀c²) — також точна", "#fef9e7", COLOR_ORANGE),
        ("Еталон маси (IPK)", "Платиново-іридієвий циліндр у Севрі\n(маса нестабільна, дрейфувала)", "#fadbd8", COLOR_RED),
        ("Константи e та h", "Вимірювалися експериментально\nмали похибку вимірювання (±10⁻⁸)", "#f4ecf7", COLOR_PURPLE),
        ("Електричні еталони", "V₉₀ та Ω₉₀ відірвані від SI через\nнеточність знань про e та h", "#ebedef", COLOR_DARK)
    ]

    y_curr = 80
    for title, body, bg_c, str_c in cards_before:
        f.append(rect(25, y_curr, 360, 52, fill=bg_c, stroke=str_c, sw=1.3, rx=4))
        f.append(text(cx_before, y_curr + 16, title, size=11, bold=True, color=str_c))
        lines = body.split('\n')
        f.append(text(cx_before, y_curr + 32, lines[0], size=9.5, color=INK))
        if len(lines) > 1:
            f.append(text(cx_before, y_curr + 44, lines[1], size=9.5, color=MUTED))
        y_curr += 60

    # --- ПРАВА ЧАСТИНА: Після 2019 року ---
    cx_after = 615
    f.append(text(cx_after, 54, "З 20 травня 2019 року (Нова SI)", size=14, bold=True, color=COLOR_GREEN))

    cards_after = [
        ("Означення Ампера (2019)", "Фіксацією елементарного заряду e:\n1 А = e / (1.602 176 634 × 10⁻¹⁹ с)", "#eafaf1", COLOR_GREEN),
        ("Магнітна стала μ₀", "μ₀ = 2αh / (e²c) (ВИМІРЮВАНА величина!)\nМає похибку через сталу тонкої структури α", "#eafaf1", COLOR_GREEN),
        ("Еталон маси (кг)", "Через сталу Планка h та ваги Кіббла\n(артефакт IPK відправлено в музей)", "#eafaf1", COLOR_GREEN),
        ("Константи e та h", "Зафіксовані ЗАКЛАДНИМИ ЧИСЛАМИ\nпохибка вимірювання дорівнює нулю!", "#f4ecf7", COLOR_PURPLE),
        ("Електричні еталони", "Джозефсон і Холл реалізують В і Ом\nПРЯМО в одиницях SI без коефіцієнтів V₉₀", "#eab8c4", COLOR_BLUE)
    ]

    y_curr = 80
    for title, body, bg_c, str_c in cards_after:
        f.append(rect(435, y_curr, 360, 52, fill=bg_c, stroke=str_c, sw=1.3, rx=4))
        f.append(text(cx_after, y_curr + 16, title, size=11, bold=True, color=str_c))
        lines = body.split('\n')
        f.append(text(cx_after, y_curr + 32, lines[0], size=9.5, color=INK))
        if len(lines) > 1:
            f.append(text(cx_after, y_curr + 44, lines[1], size=9.5, color=MUTED))
        y_curr += 60

    return render(os.path.join(IMG_DIR, "before-vs-after-2019.svg"), W, H, *f)


def fig_kibble_josephson_hall():
    """Фігура 3: Фундаментальний квантовий трикутник електромагнетизму."""
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Фундаментальний квантовий трикутник SI", size=16, bold=True, color=INK))

    # Вершина 1 (Верх): Фундаментальні константи e та h
    b_top, w_top, h_top = textbox(W / 2, 70, "Фундаментальні квантові константи\ne = 1.602 176 634 × 10⁻¹⁹ Кл (ТОЧНО)\nh = 6.626 070 15 × 10⁻³⁴ Дж·с (ТОЧНО)",
                                  size=12, pad=9, fill="#f4ecf7", stroke=COLOR_PURPLE, sw=1.6, bold=True, color=COLOR_PURPLE)
    f.append(b_top)

    # Вершина 2 (Ліво-низ): Ефект Джозефсона (Вольт)
    b_left, w_left, h_left = textbox(210, 250, "Ефект Джозефсона (Вольт)\nKJ = 2e / h\nV = fJ / KJ\nНапруга з частоти fJ",
                                     size=11.5, pad=9, fill="#ebf5fb", stroke=COLOR_BLUE, sw=1.5, bold=True, color=COLOR_BLUE)
    f.append(b_left)

    # Вершина 3 (Право-низ): Квантовий ефект Холла (Ом)
    b_right, w_right, h_right = textbox(610, 250, "Квантовий ефект Холла (Ом)\nRK = h / e²\nR = RK / i\nОпір із точних констант",
                                       size=11.5, pad=9, fill="#fef9e7", stroke=COLOR_ORANGE, sw=1.5, bold=True, color=COLOR_ORANGE)
    f.append(b_right)

    # Центр-низ: Ваги Кіббла (Кілограм)
    b_bot, w_bot, h_bot = textbox(W / 2, 380, "Ваги Кіббла (Watt Balance) — Рівновага потужностей:\nРмех = m·g·v  =  Рел = U·I = U² / R  →  Визначення маси (кг) через h та e",
                                  size=11.5, pad=8, fill="#eafaf1", stroke=COLOR_GREEN, sw=1.6, bold=True, color=COLOR_GREEN)
    f.append(b_bot)

    # З'єднувальні лінії та стрілки трикутника
    # Верх -> Ліво (Джозефсон)
    f.append(arrow(W / 2 - 80, 105, 230, 205, color=COLOR_PURPLE, sw=1.8))
    f.append(text(270, 145, "KJ = 2e/h", size=11, bold=True, color=COLOR_PURPLE))

    # Верх -> Право (Холл)
    f.append(arrow(W / 2 + 80, 105, 590, 205, color=COLOR_PURPLE, sw=1.8))
    f.append(text(530, 145, "RK = h/e²", size=11, bold=True, color=COLOR_PURPLE))

    # Ліво <-> Право (Закон Ома I = V/R)
    f.append(line(325, 250, 495, 250, color=COLOR_DARK, sw=1.5, dash="4,4"))
    f.append(text(W / 2, 240, "Закон Ома: I = V / R", size=11, bold=True, color=COLOR_DARK))

    # Джозефсон + Холл -> Ваги Кіббла
    f.append(arrow(210, 295, W / 2 - 100, 350, color=COLOR_BLUE, sw=1.5))
    f.append(arrow(610, 295, W / 2 + 100, 350, color=COLOR_ORANGE, sw=1.5))

    return render(os.path.join(IMG_DIR, "kibble-josephson-hall.svg"), W, H, *f)


if __name__ == '__main__':
    fig_si_constants_tree()
    fig_before_vs_after_2019()
    fig_kibble_josephson_hall()
    print("Всі 3 фігури успішно згенеровано у ./img/")
