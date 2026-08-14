# -*- coding: utf-8 -*-
"""Фігури до статті «Хешування з урахуванням локальності (LSH)».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=LINE, sw=1.5):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def fig_lsh_concept():
    W, H = 880, 360
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Принцип хешування з урахуванням локальності (LSH)", size=16, bold=True))

    # --- Лівий блок: Класичне хешування ---
    bx1, by1, bw1, bh1 = 30, 55, 390, 280
    parts.append(rect(bx1, by1, bw1, bh1, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    parts.append(text(bx1 + bw1/2, by1 + 25, "Класичне хешування (SHA-256 / Murmur3)", size=13.5, bold=True, color=POS))
    parts.append(text(bx1 + bw1/2, by1 + 45, "Лавинний ефект: схожі дані → повністю різні хеші", size=11, color=MUTED))

    # Об'єкти
    parts.append(rect(bx1 + 20, by1 + 75, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx1 + 100, by1 + 93, "Вектор A [1.0, 2.0, 3.0]", size=11, bold=True))
    parts.append(text(bx1 + 100, by1 + 110, "Початковий вектор", size=10, color=MUTED))

    parts.append(rect(bx1 + 20, by1 + 140, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx1 + 100, by1 + 158, "Вектор B [1.0, 2.0, 3.1]", size=11, bold=True))
    parts.append(text(bx1 + 100, by1 + 175, "Дуже схожий вектор (Δ=0.1)", size=10, color=MUTED))

    parts.append(rect(bx1 + 20, by1 + 205, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx1 + 100, by1 + 223, "Вектор C [9.0, 8.0, 7.0]", size=11, bold=True))
    parts.append(text(bx1 + 100, by1 + 240, "Далекий вектор", size=10, color=MUTED))

    # Стрілки та бакети
    parts.append(arrow(bx1 + 185, by1 + 97, bx1 + 245, by1 + 97, color=POS))
    parts.append(arrow(bx1 + 185, by1 + 162, bx1 + 245, by1 + 162, color=POS))
    parts.append(arrow(bx1 + 185, by1 + 227, bx1 + 245, by1 + 227, color=POS))

    parts.append(rect(bx1 + 250, by1 + 75, 120, 45, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(bx1 + 310, by1 + 101, "Комірка #0x8f3a", size=11, bold=True, color=POS))

    parts.append(rect(bx1 + 250, by1 + 140, 120, 45, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(bx1 + 310, by1 + 166, "Комірка #0x12b9", size=11, bold=True, color=POS))

    parts.append(rect(bx1 + 250, by1 + 205, 120, 45, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(bx1 + 310, by1 + 231, "Комірка #0x77c4", size=11, bold=True, color=POS))

    parts.append(text(bx1 + bw1/2, by1 + 268, "Результат: схожі елементи потрапляють у різні комірки!", size=10.5, italic=True, color=POS))

    # --- Правий блок: LSH хешування ---
    bx2, by2, bw2, bh2 = 460, 55, 390, 280
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(bx2 + bw2/2, by2 + 25, "LSH хешування (Locality-Sensitive)", size=13.5, bold=True, color=FIELD))
    parts.append(text(bx2 + bw2/2, by2 + 45, "Збереження локальності: схожі дані → одна комірка", size=11, color=MUTED))

    # Об'єкти
    parts.append(rect(bx2 + 20, by2 + 75, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx2 + 100, by2 + 93, "Вектор A [1.0, 2.0, 3.0]", size=11, bold=True))
    parts.append(text(bx2 + 100, by2 + 110, "Початковий вектор", size=10, color=MUTED))

    parts.append(rect(bx2 + 20, by2 + 140, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx2 + 100, by2 + 158, "Вектор B [1.0, 2.0, 3.1]", size=11, bold=True))
    parts.append(text(bx2 + 100, by2 + 175, "Дуже схожий вектор (Δ=0.1)", size=10, color=MUTED))

    parts.append(rect(bx2 + 20, by2 + 205, 160, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx2 + 100, by2 + 223, "Вектор C [9.0, 8.0, 7.0]", size=11, bold=True))
    parts.append(text(bx2 + 100, by2 + 240, "Далекий вектор", size=10, color=MUTED))

    # Стрілки та бакети
    parts.append(arrow(bx2 + 185, by2 + 97, bx2 + 245, by2 + 115, color=FIELD))
    parts.append(arrow(bx2 + 185, by2 + 162, bx2 + 245, by2 + 125, color=FIELD))
    parts.append(arrow(bx2 + 185, by2 + 227, bx2 + 245, by2 + 227, color=MUTED))

    parts.append(rect(bx2 + 250, by2 + 90, 120, 60, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(bx2 + 310, by2 + 112, "Комірка #42", size=11.5, bold=True, color=FIELD))
    parts.append(text(bx2 + 310, by2 + 132, "Вектори {A, B}", size=10.5, color=INK))

    parts.append(rect(bx2 + 250, by2 + 205, 120, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    parts.append(text(bx2 + 310, by2 + 223, "Комірка #109", size=11, bold=True, color=INK))
    parts.append(text(bx2 + 310, by2 + 240, "Вектор {C}", size=10, color=MUTED))

    parts.append(text(bx2 + bw2/2, by2 + 268, "Результат: колізія є бажаною для близьких об'єктів!", size=10.5, italic=True, color=FIELD))

    # Підпис під фігурою
    parts.append(text(W / 2, H - 10, "Порівняння класичної хеш-функції з лавинним ефектом та LSH-функції, що колідує близькі вектори.", size=12, italic=True, color=MUTED))

    return "\n".join(parts)


def fig_banding_s_curve():
    W, H = 900, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 26, "Підсилення ймовірності колізії (Banding) та S-подібна крива", size=16, bold=True))

    # --- Ліва панель: Структура смуг (AND-OR дерево) ---
    bx1, by1, bw1, bh1 = 25, 50, 400, 335
    parts.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(bx1 + bw1/2, by1 + 22, "Схема смуг (L = 4 смуги, k = 3 функції)", size=13, bold=True))

    bands = [
        ("Смуга 1", ["h_11", "h_12", "h_13"]),
        ("Смуга 2", ["h_21", "h_22", "h_23"]),
        ("Смуга 3", ["h_31", "h_32", "h_33"]),
        ("Смуга 4", ["h_41", "h_42", "h_43"]),
    ]

    for i, (bname, hfuncs) in enumerate(bands):
        y_band = by1 + 50 + i * 65
        parts.append(rect(bx1 + 15, y_band, 70, 50, fill="#edf2f7", stroke=LINE, sw=1, rx=4))
        parts.append(text(bx1 + 50, y_band + 30, bname, size=11, bold=True))

        # 3 хеш-функції (AND)
        for j, hf in enumerate(hfuncs):
            x_h = bx1 + 100 + j * 55
            parts.append(rect(x_h, y_band + 8, 48, 34, fill="#ffffff", stroke=NEG, sw=1, rx=3))
            parts.append(text(x_h + 24, y_band + 29, hf, size=10.5, color=NEG))

        # AND логіка
        parts.append(rect(bx1 + 275, y_band + 12, 45, 26, fill="#e1f5fe", stroke=NEG, sw=1, rx=3))
        parts.append(text(bx1 + 297, y_band + 29, "AND", size=10, bold=True, color=NEG))
        parts.append(arrow(bx1 + 266, y_band + 25, bx1 + 275, y_band + 25, color=NEG))

        # Лінія до OR
        parts.append(line(bx1 + 320, y_band + 25, bx1 + 355, y_band + 25, color=FIELD, sw=1.5))

    # Блок OR
    parts.append(rect(bx1 + 355, by1 + 55, 32, 240, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(bx1 + 371, by1 + 175, "O R", size=12, bold=True, color=FIELD))

    parts.append(text(bx1 + bw1/2, by1 + 315, "Кандидат: збіг в УСІХ k функціях ХОЧ Б ОДНІЄЇ смуги", size=10.5, italic=True))

    # --- Права панель: Графік S-кривої ---
    gx, gy, gw, gh = 465, 75, 400, 270
    parts.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d0d0", sw=1))

    # Осі
    parts.append(line(gx + 40, gy + gh - 40, gx + gw - 20, gy + gh - 40, color=LINE, sw=1.5))
    parts.append(line(gx + 40, gy + gh - 40, gx + 40, gy + 20, color=LINE, sw=1.5))

    # Подписи осей
    parts.append(text(gx + gw / 2 + 10, gy + gh - 10, "Схожість s ∈ [0, 1]", size=11.5, bold=True))
    parts.append(text(gx + 15, gy + 15, "P(Кандидат)", size=11, bold=True, anchor="start"))

    # Поділки y (0.0, 0.5, 1.0)
    parts.append(text(gx + 32, gy + gh - 40, "0", size=10, anchor="end"))
    parts.append(text(gx + 32, gy + gh - 150, "0.5", size=10, anchor="end"))
    parts.append(text(gx + 32, gy + 30, "1", size=10, anchor="end"))

    parts.append(line(gx + 37, gy + gh - 150, gx + gw - 20, gy + gh - 150, color="#e2e8f0", dash="3,3"))
    parts.append(line(gx + 37, gy + 30, gx + gw - 20, gy + 30, color="#e2e8f0", dash="3,3"))

    # Поділки x (0.0, s0, 1.0)
    # Побудова S-кривої: P(s) = 1 - (1 - s^k)^L для k=3, L=10 -> s0 = (1/10)^(1/3) ~ 0.464
    k_val, L_val = 3, 10
    pts = []
    num_pts = 40
    for step in range(num_pts + 1):
        s = step / float(num_pts)
        p = 1.0 - math.pow(1.0 - math.pow(s, k_val), L_val)
        px = gx + 40 + s * (gw - 60)
        py = (gy + gh - 40) - p * (gh - 70)
        pts.append((px, py))

    # Пряма без підсилення (k=1, L=1)
    pts_single = []
    for step in range(num_pts + 1):
        s = step / float(num_pts)
        px = gx + 40 + s * (gw - 60)
        py = (gy + gh - 40) - s * (gh - 70)
        pts_single.append((px, py))

    parts.append(polyline(pts_single, color=MUTED, sw=1.5))
    parts.append(polyline(pts, color=FIELD, sw=2.5))

    # Поріг s0
    s0 = math.pow(1.0 / L_val, 1.0 / k_val)
    s0_x = gx + 40 + s0 * (gw - 60)
    s0_y = (gy + gh - 40) - 0.5 * (gh - 70)

    parts.append(line(s0_x, gy + gh - 40, s0_x, gy + 30, color=POS, dash="4,4", sw=1.5))
    parts.append(circle(s0_x, s0_y, 4, fill=POS, stroke="#ffffff", sw=1))
    parts.append(text(s0_x, gy + gh - 25, "s₀ ≈ 0.46", size=10.5, bold=True, color=POS))

    # Аннотації на графіку
    parts.append(text(gx + 120, gy + 60, "Без підсилення: P = s", size=10, color=MUTED))
    parts.append(text(gx + 180, gy + 110, "S-крива: P = 1-(1-sᵏ)ᴸ", size=11, bold=True, color=FIELD))

    parts.append(text(gx + 90, gy + gh - 65, "False Positives", size=9.5, color=POS))
    parts.append(text(gx + 320, gy + 50, "High Recall", size=9.5, color=FIELD))

    # Підпис фігури
    parts.append(text(W / 2, H - 10, "Структура AND-OR смуг (ліворуч) перетворює лінійну ймовірність на гостру S-подібну порогову криву (праворуч).", size=12, italic=True, color=MUTED))

    return "\n".join(parts)


def fig_lsh_query_pipeline():
    W, H = 920, 350
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 25, "Конвеєр виконання пошуку за LSH-індексом", size=16, bold=True))

    steps = [
        ("1. Запит q", "Вектор запиту\nq ∈ Rᵈ", "#edf2f7", LINE),
        ("2. Хешування", "Обчислення L\nбакетових хешів", "#e1f5fe", NEG),
        ("3. Пошук", "Вибірка з L\nхеш-таблиць", "#e8f8f0", FIELD),
        ("4. Кандидати", "Об'єднання ID\n(Union without Dup)", "#fff5f5", POS),
        ("5. Переперевірка", "Точний розрахунок\nвідстані d(q, x)", "#fefcbf", LINE),
        ("6. Результат", "Top-K найближчих\nсусідів", "#e8f8f0", FIELD),
    ]

    box_w, box_h = 125, 95
    start_x, start_y = 20, 65
    gap_x = 25

    for i, (stitle, sdesc, fill_c, stroke_c) in enumerate(steps):
        x = start_x + i * (box_w + gap_x)
        y = start_y

        parts.append(rect(x, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        parts.append(text(x + box_w/2, y + 24, stitle, size=11.5, bold=True, color=INK if stroke_c==LINE else stroke_c))
        parts.append(line(x + 10, y + 36, x + box_w - 10, y + 36, color=stroke_c, sw=0.8))

        lines = sdesc.split("\n")
        for j, ln in enumerate(lines):
            parts.append(text(x + box_w/2, y + 56 + j * 18, ln, size=10.5, color=INK))

        # Стрілка між кроками
        if i < len(steps) - 1:
            arr_x1 = x + box_w
            arr_x2 = x + box_w + gap_x
            arr_y = y + box_h / 2
            parts.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=1.5))

    # Додатковий детальне роз'яснення під блоками
    by = 185
    parts.append(rect(20, by, 880, 125, fill="#fafafa", stroke="#d0d0d0", sw=1, rx=6))
    parts.append(text(40, by + 22, "Деталізація конвеєра:", size=12, bold=True, anchor="start"))

    details = [
        "• Етап 1-3 (O(L) операцій): LSH швидким відбором звужує пошуковий простір з N мільйонів записів до C (декількох десятків) кандидатів.",
        "• Етап 4 (Об'єднання): Кандидатом стає будь-який вектор, що потрапив у той самий бакет хоч в одній із L хеш-таблиць.",
        "• Етап 5-6 (Точний перерахунок): Точна відстань d(q, x) обчислюється ЛИШЕ для відібраних C кандидатів, скасовуючи лінійне сканування всієї бази.",
    ]

    for idx, dt in enumerate(details):
        parts.append(text(40, by + 48 + idx * 24, dt, size=11, anchor="start", color=INK))

    parts.append(text(W / 2, H - 10, "LSH працює як ймовірнісний фільтр: 99.9% бази відсікається за O(L), а важкі векторні обчислення робляться лише для кандидатів.", size=11.5, italic=True, color=MUTED))

    return "\n".join(parts)


def main():
    figs = [
        ("lsh-concept.svg", 880, 360, fig_lsh_concept),
        ("banding-s-curve.svg", 900, 420, fig_banding_s_curve),
        ("lsh-query-pipeline.svg", 920, 350, fig_lsh_query_pipeline),
    ]

    for fname, w, h, func in figs:
        fpath = os.path.join(IMG, fname)
        render(fpath, w, h, func())
        print(f"Generated: {fpath}")


if __name__ == "__main__":
    main()
