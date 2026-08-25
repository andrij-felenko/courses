# -*- coding: utf-8 -*-
"""Фігури до теми «PN-послідовності».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Топології LFSR: Фібоначчі проти Галуа ──────────────────────────────────
def fig_lfsr_fibonacci_galois():
    W, H = 790, 340
    f = [text(W / 2, 26, "Топології генераторів LFSR: Фібоначчі та Галуа", size=16, bold=True)]

    # ── Верхня панель: Фібоначчі ──
    yA = 105
    f.append(text(50, yA - 42, "А · Структура Фібоначчі (суматор у ланцюзі зворотного зв'язку)",
                  size=12.5, color=INK, bold=True, anchor="start"))

    # Осередки регістру S0, S1, S2, S3
    stages_A = ["S0", "S1", "S2", "S3"]
    xs_A = [170, 270, 370, 470]
    cell_w, cell_h = 56, 36

    for i, (x, name) in enumerate(zip(xs_A, stages_A)):
        f.append(rect(x - cell_w/2, yA - cell_h/2, cell_w, cell_h, fill="#eef2fb", stroke=NEG, sw=1.8))
        f.append(text(x, yA + 5, name, size=13, color=NEG, bold=True))

    # Стрілки між осередками
    for i in range(len(xs_A) - 1):
        f.append(arrow(xs_A[i] + cell_w/2 + 2, yA, xs_A[i+1] - cell_w/2 - 2, yA, color=INK, sw=1.6))

    # Вихід
    f.append(arrow(xs_A[-1] + cell_w/2 + 2, yA, xs_A[-1] + cell_w/2 + 45, yA, color=INK, sw=1.8))
    f.append(text(xs_A[-1] + cell_w/2 + 52, yA + 4, "Вихід b[n]", size=11.5, color=INK, bold=True, anchor="start"))

    # Отводи зворотного зв'язку (від S2 та S3)
    plus_xA = 320
    plus_yA = yA - 48
    f.append(plus(plus_xA, plus_yA, r=10))

    # Лінії від S2 і S3 до XOR
    f.append(line(xs_A[2], yA - cell_h/2, xs_A[2], plus_yA, color=POS, sw=1.6))
    f.append(line(xs_A[2], plus_yA, plus_xA + 10, plus_yA, color=POS, sw=1.6))

    f.append(line(xs_A[3], yA - cell_h/2, xs_A[3], plus_yA - 16, color=POS, sw=1.6))
    f.append(line(xs_A[3], plus_yA - 16, plus_xA, plus_yA - 16, color=POS, sw=1.6))
    f.append(line(plus_xA, plus_yA - 16, plus_xA, plus_yA - 10, color=POS, sw=1.6))

    # Від XOR до входу S0
    f.append(line(plus_xA - 10, plus_yA, 90, plus_yA, color=POS, sw=1.6))
    f.append(line(90, plus_yA, 90, yA, color=POS, sw=1.6))
    f.append(arrow(90, yA, xs_A[0] - cell_w/2 - 2, yA, color=POS, sw=1.6))

    f.append(text(620, yA + 4, "Каскад XOR розростається\nз ростом кількості отводів",
                  size=10, color=MUTED, italic=True, anchor="start"))

    # ── Нижня панель: Галуа ──
    yB = 265
    f.append(text(50, yB - 42, "Б · Структура Галуа (модулі XOR між осередками регістру)",
                  size=12.5, color=INK, bold=True, anchor="start"))

    stages_B = ["S0", "S1", "S2", "S3"]
    xs_B = [170, 290, 410, 530]

    for i, (x, name) in enumerate(zip(xs_B, stages_B)):
        f.append(rect(x - cell_w/2, yB - cell_h/2, cell_w, cell_h, fill="#eaf6ef", stroke=FIELD, sw=1.8))
        f.append(text(x, yB + 5, name, size=13, color=FIELD, bold=True))

    # XOR між S1 та S2
    plus_xB = 350
    plus_yB = yB
    f.append(plus(plus_xB, plus_yB, r=9))

    # Стрілки між S0->S1, S1->XOR->S2, S2->S3
    f.append(arrow(xs_B[0] + cell_w/2 + 2, yB, xs_B[1] - cell_w/2 - 2, yB, color=INK, sw=1.6))
    f.append(line(xs_B[1] + cell_w/2 + 2, yB, plus_xB - 9, yB, color=INK, sw=1.6))
    f.append(arrow(plus_xB + 9, yB, xs_B[2] - cell_w/2 - 2, yB, color=INK, sw=1.6))
    f.append(arrow(xs_B[2] + cell_w/2 + 2, yB, xs_B[3] - cell_w/2 - 2, yB, color=INK, sw=1.6))

    # Вихід із S3
    f.append(arrow(xs_B[3] + cell_w/2 + 2, yB, xs_B[3] + cell_w/2 + 45, yB, color=INK, sw=1.8))
    f.append(text(xs_B[3] + cell_w/2 + 52, yB + 4, "Вихід b[n]", size=11.5, color=INK, bold=True, anchor="start"))

    # Зворотна шина від виходу S3 до XOR і S0
    fb_yB = yB + 42
    f.append(line(xs_B[3] + 25, yB, xs_B[3] + 25, fb_yB, color=POS, sw=1.6))
    f.append(line(xs_B[3] + 25, fb_yB, xs_B[0] - 40, fb_yB, color=POS, sw=1.6))

    # Подача на S0
    f.append(line(xs_B[0] - 40, fb_yB, xs_B[0] - 40, yB, color=POS, sw=1.6))
    f.append(arrow(xs_B[0] - 40, yB, xs_B[0] - cell_w/2 - 2, yB, color=POS, sw=1.6))

    # Відвід від зворотної шини до плюс-вузла між S1 і S2
    f.append(line(plus_xB, fb_yB, plus_xB, plus_yB + 9, color=POS, sw=1.6))

    f.append(text(620, yB + 4, "Паралельні XOR:\nсталий час затримки t_pd",
                  size=10, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(IMG, "lfsr-fibonacci-galois.svg"), W, H, *f)


# ── 2. Ідеальна дворівнева АКФ ────────────────────────────────────────────────
def fig_autocorrelation_ideal():
    W, H = 770, 290
    f = [text(W / 2, 26, "Автокореляційна функція m-послідовності періоду N = 2ᵐ − 1", size=16, bold=True)]

    x0, base = 90, 230
    x_max = 700
    N_px = 140  # крок періоду в пікселях

    # Осі
    f.append(line(x0 - 20, base, x_max + 20, base, color=INK, sw=1.6))
    f.append(arrow(x0 + 2*N_px, base + 20, x0 + 2*N_px, 50, color=INK, sw=1.6))

    f.append(text(x_max + 32, base + 4, "зсув k", size=11, color=MUTED, italic=True, anchor="start"))
    f.append(text(x0 + 2*N_px - 15, 48, "R(k)", size=11, color=MUTED, italic=True, anchor="end"))

    # Позначки періодів на осі X
    ticks = [
        (x0, "−2N"),
        (x0 + N_px, "−N"),
        (x0 + 2*N_px, "0"),
        (x0 + 3*N_px, "N"),
        (x0 + 4*N_px, "2N")
    ]

    for tx, tlab in ticks:
        f.append(line(tx, base - 4, tx, base + 6, color=INK, sw=1.2))
        f.append(text(tx, base + 22, tlab, size=11, color=INK, bold=(tlab == "0")))

    # Рівні Y: peak = N, off-peak = -1
    y_peak = 75
    y_off = base - 12  # трохи нижче нуля

    # Лінія рівня -1
    f.append(line(x0 - 15, y_off, x_max + 15, y_off, color=NEG, sw=1.2, dash="4,3"))
    f.append(text(x0 - 25, y_off + 4, "−1", size=11, color=NEG, bold=True, anchor="end"))

    # Графік АКФ: трикутники на нулі та ±N, ±2N
    tri_w = 30  # напівширина трикутника АКФ (1 чіп)

    pts = []
    # Лінія від лівого краю до першого трикутника
    pts.append((x0 - 15, y_off))
    for tx, _ in ticks:
        pts.append((tx - tri_w, y_off))
        pts.append((tx, y_peak))
        pts.append((tx + tri_w, y_off))
    pts.append((x0 + 4*N_px + 30, y_off))

    poly_str = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly_str, FIELD))

    # Виноски та пояснення
    f.append(line(x0 + 2*N_px + 5, y_peak, x0 + 2*N_px + 100, y_peak, color=FIELD, sw=1.4, dash="3,3"))
    f.append(text(x0 + 2*N_px + 108, y_peak + 4, "Гострий пік R(0) = N",
                  size=11, color=FIELD, bold=True, anchor="start"))

    f.append(text(x0 + 3*N_px + 40, y_off - 16, "Позапіковий рівень R(k) = −1",
                  size=10.5, color=NEG, bold=True, anchor="start"))

    # Стрілка періоду N
    f.append(arrow(x0 + 2*N_px + 10, base + 42, x0 + 3*N_px - 10, base + 42, color=INK, sw=1.4))
    f.append(arrow(x0 + 3*N_px - 10, base + 42, x0 + 2*N_px + 10, base + 42, color=INK, sw=1.4))
    f.append(text(x0 + 2.5*N_px, base + 40, "Період N = 2ᵐ − 1 бітів", size=10.5, color=INK, bold=True))

    render(os.path.join(IMG, "autocorrelation-ideal.svg"), W, H, *f)


# ── 3. Спектральне розширення DSSS ─────────────────────────────────────────────
def fig_dsss_spreading():
    W, H = 790, 350
    f = [text(W / 2, 26, "Спектральне розширення сигналу DSSS", size=16, bold=True)]

    # Ліва частина: часові діаграми
    x0 = 50

    # 1. Дані d(t)
    y1 = 80
    f.append(text(x0, y1 - 22, "1 · Інформаційний біт d(t) [тривалість T_b]", size=11, color=INK, bold=True, anchor="start"))
    f.append(line(x0, y1, x0 + 380, y1, color=MUTED, sw=1))
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (x0, y1+15, x0+190, y1+15, x0+190, y1-15, x0+380, y1-15, x0+380, y1+15, POS))
    f.append(text(x0 + 95, y1 + 30, "+1", size=10, color=POS, bold=True))
    f.append(text(x0 + 285, y1 - 25, "−1", size=10, color=POS, bold=True))

    # 2. PN-код c(t)
    y2 = 175
    f.append(text(x0, y2 - 22, "2 · Чіпова послідовність c(t) [тривалість T_c << T_b]", size=11, color=INK, bold=True, anchor="start"))
    f.append(line(x0, y2, x0 + 380, y2, color=MUTED, sw=1))
    
    chips = [+1, -1, +1, +1, -1, +1, -1, -1, +1, -1, +1, +1, -1, -1, +1, -1]
    chip_w = 380 / len(chips)
    pts_c = []
    curr_x = x0
    for i, c in enumerate(chips):
        cy = y2 - c * 14
        pts_c.append((curr_x, cy))
        pts_c.append((curr_x + chip_w, cy))
        curr_x += chip_w
    
    poly_c = " ".join("%.1f,%.1f" % p for p in pts_c)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (poly_c, NEG))

    # 3. Перемножений сигнал s(t) = d(t) · c(t)
    y3 = 270
    f.append(text(x0, y3 - 22, "3 · Розширений сигнал s(t) = d(t) · c(t)", size=11, color=INK, bold=True, anchor="start"))
    f.append(line(x0, y3, x0 + 380, y3, color=MUTED, sw=1))

    pts_s = []
    curr_x = x0
    for i, c in enumerate(chips):
        data_val = +1 if i < 8 else -1
        s_val = data_val * c
        sy = y3 - s_val * 14
        pts_s.append((curr_x, sy))
        pts_s.append((curr_x + chip_w, sy))
        curr_x += chip_w

    poly_s = " ".join("%.1f,%.1f" % p for p in pts_s)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (poly_s, FIELD))

    # Права частина: Спектри потужності
    rx0, ry0 = 480, 280
    f.append(text(rx0 + 130, 58, "Спектральна щільність потужності", size=12, color=INK, bold=True))
    f.append(arrow(rx0, ry0, rx0 + 260, ry0, color=INK, sw=1.6))
    f.append(arrow(rx0 + 130, ry0, rx0 + 130, 80, color=INK, sw=1.6))
    f.append(text(rx0 + 265, ry0 + 4, "f", size=11, color=MUTED, italic=True, anchor="start"))

    # Вузький високий спектр початкового сигналу
    f.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="%s" fill-opacity="0.3" stroke="%s" stroke-width="1.8"/>'
             % (rx0 + 105, ry0, rx0 + 130, 95, rx0 + 130, 95, rx0 + 130, 95, rx0 + 155, ry0, POS, POS))
    f.append(text(rx0 + 130, 115, "Інформаційний\nсигнал (вузький)", size=10, color=POS, bold=True))

    # Широкий низький спектр DSSS
    f.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2"/>'
             % (rx0 + 10, ry0, rx0 + 130, 160, rx0 + 130, 160, rx0 + 130, 160, rx0 + 250, ry0, FIELD, FIELD))
    f.append(text(rx0 + 130, 142, "Розширений сигнал DSSS", size=10, color=FIELD, bold=True))

    # Рівень теплового шуму
    y_noise = ry0 - 65
    f.append(line(rx0 + 5, y_noise, rx0 + 255, y_noise, color=NEG, sw=1.4, dash="5,4"))
    f.append(text(rx0 + 255, y_noise - 6, "Рівень шуму AWGN", size=10, color=NEG, bold=True, anchor="end"))

    render(os.path.join(IMG, "dsss-spreading.svg"), W, H, *f)


# ── 4. Взаємна кореляція кодів Ґолда ──────────────────────────────────────────
def fig_gold_cross_correlation():
    W, H = 770, 290
    f = [text(W / 2, 26, "Взаємна кореляція кодових послідовностей Ґолда", size=16, bold=True)]

    x0, base = 85, 170
    x_max = 700
    span = x_max - x0

    # Осі
    f.append(line(x0 - 15, base, x_max + 15, base, color=INK, sw=1.6))
    f.append(arrow(x0 + span/2, base + 80, x0 + span/2, 45, color=INK, sw=1.6))
    f.append(text(x_max + 22, base + 4, "зсув k", size=11, color=MUTED, italic=True, anchor="start"))
    f.append(text(x0 + span/2 - 12, 45, "R₁₂(k)", size=11, color=MUTED, italic=True, anchor="end"))

    # Рівні тризначної ВКФ Ґолда: +7, -1, -9 (для N = 31)
    y_p7 = base - 65
    y_m1 = base + 8
    y_m9 = base + 65

    # Межі завад (dashed)
    f.append(line(x0, y_p7, x_max, y_p7, color=POS, sw=1.2, dash="4,3"))
    f.append(line(x0, y_m9, x_max, y_m9, color=POS, sw=1.2, dash="4,3"))

    f.append(text(x0 - 20, y_p7 + 4, "+t(m)−2 = +7", size=10.5, color=POS, bold=True, anchor="end"))
    f.append(text(x0 - 20, y_m1 + 4, "−1", size=10.5, color=MUTED, bold=True, anchor="end"))
    f.append(text(x0 - 20, y_m9 + 4, "−t(m) = −9", size=10.5, color=POS, bold=True, anchor="end"))

    # Спектр відліків взаємної кореляції на зсувах
    import random
    random.seed(42)
    n_pts = 31
    dx = span / (n_pts - 1)

    possible_y = [y_p7, y_m1, y_m1, y_m1, y_m9]

    for i in range(n_pts):
        px = x0 + i * dx
        py = random.choice(possible_y)
        color_pt = POS if (py == y_p7 or py == y_m9) else NEG
        f.append(line(px, base, px, py, color=color_pt, sw=1.6))
        f.append(circle(px, py, 3, fill=color_pt, stroke=color_pt, sw=0))

    # Рамка пояснення
    f.append(rect(480, 52, 230, 70, fill="#fffdf5", stroke="#9a7a1e", sw=1.6))
    f.append(mtext(595, 76, ["ВКФ приймає лише 3 значення:", "{-t(m), -1, t(m)-2}", "Гарантована межа завади CDMA"],
                   size=10.5, color="#9a7a1e", bold=True))

    render(os.path.join(IMG, "gold-cross-correlation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lfsr_fibonacci_galois()
    fig_autocorrelation_ideal()
    fig_dsss_spreading()
    fig_gold_cross_correlation()
    print("OK: 4 figures created in ./img/")
