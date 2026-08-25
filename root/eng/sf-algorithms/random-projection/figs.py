# -*- coding: utf-8 -*-
"""Фігури до теми «Випадкова проєкція і лема Джонсона — Лінденштрауса»."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def rnd(seed):
    """Детермінований генератор ПВЧ для відтворюваності фігур."""
    x = seed & ((1 << 64) - 1)
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) % (1 << 64)
        yield (x >> 33) / float(1 << 31)


def dot(x, y, r=3.0, color=INK):
    return circle(x, y, r, fill=color, stroke=color, sw=0.6)


def polyline(pts, color=POS, sw=2.4):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


# ── 1. Зростання розмірності k за лемою Джонсона — Лінденштрауса ─────────────
def fig_jl_scaling():
    W, H = 880, 490
    out = []

    # Тло фігури
    out.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Межі графіка
    GX, GY, GW, GH = 95, 65, 720, 340

    # Сітка та осі
    out.append(line(GX, GY + GH, GX + GW, GY + GH, color=LINE, sw=1.6))
    out.append(line(GX, GY, GX, GY + GH, color=LINE, sw=1.6))

    # Вісь Y: k від 0 до 6000
    y_ticks = [(0, "0"), (1000, "1000"), (2000, "2000"), (3000, "3000"), (4000, "4000"), (5000, "5000"), (6000, "6000")]
    for val, lab in y_ticks:
        y = GY + GH - GH * (val / 6000.0)
        out.append(line(GX - 6, y, GX + GW, y, color=FILL if val > 0 else LINE, sw=1.0))
        out.append(text(GX - 14, y + 4, lab, size=12, color=MUTED, anchor="end"))

    # Вісь X: N від 10^2 до 10^7 у логарифмічній шкалі
    x_ticks = [
        (2, "100"),
        (3, "1 тис."),
        (4, "10 тис."),
        (5, "100 тис."),
        (6, "1 млн"),
        (7, "10 млн"),
    ]
    for log_val, lab in x_ticks:
        x = GX + GW * ((log_val - 2) / 5.0)
        out.append(line(x, GY, x, GY + GH + 6, color=FILL if log_val > 2 else LINE, sw=1.0))
        out.append(text(x, GY + GH + 24, lab, size=12, color=MUTED, anchor="middle"))

    out.append(text(GX + GW / 2, GY + GH + 54, "Кількість точок у вибірці N (логарифмічна шкала)", size=13, bold=True))
    out.append(text(GX - 55, GY + GH / 2, "Цільова розмірність k", size=13, bold=True, anchor="middle"))

    # Криві: k = (4 * ln(N)) / (ε^2 / 2 - ε^3 / 3)
    epsilons = [
        (0.15, POS, "ε = 0.15 (похибка ±15%)"),
        (0.20, NEG, "ε = 0.20 (похибка ±20%)"),
        (0.30, FIELD, "ε = 0.30 (похибка ±30%)"),
        (0.40, "#7f8c8d", "ε = 0.40 (похибка ±40%)"),
    ]

    for eps, col, label in epsilons:
        pts = []
        denom = (eps * eps / 2.0) - (eps * eps * eps / 3.0)
        for i in range(101):
            log_n = 2.0 + 5.0 * (i / 100.0)
            n_val = 10.0 ** log_n
            k_val = (4.0 * math.log(n_val)) / denom
            if k_val <= 6000:
                x = GX + GW * (i / 100.0)
                y = GY + GH - GH * (k_val / 6000.0)
                pts.append((x, y))
        out.append(polyline(pts, color=col, sw=2.6))
        if pts:
            last_x, last_y = pts[-1]
            out.append(text(last_x - 145, last_y - 10, label, size=11, color=col, bold=True, anchor="start"))

    # Пояснювальна плашка
    box_txt = "Зростання N від 10³ до 10⁶ подвоює k,\nале зміна ε з 0.30 до 0.15 збільшує k у 4 рази (закон 1/ε²)"
    box_body, _, _ = textbox(GX + 220, GY + 50, box_txt, size=11, pad=8, color=INK, fill="#fdfefe", stroke=MUTED)
    out.append(box_body)

    return render(os.path.join(OUT, 'jl-bound-scaling.svg'), W, H, *out,
                  title="Залежність цільової розмірності k від кількості точок N та похибки ε")


# ── 2. Геометрія випадкової проєкції: високий простір -> низький ────────────
def fig_rp_geometry():
    W, H = 880, 420
    out = []
    out.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Ліва панель: d-вимірний простір
    LX0, LY0, LW, LH = 40, 50, 360, 320
    out.append(rect(LX0, LY0, LW, LH, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    out.append(text(LX0 + LW / 2, LY0 + 26, "Початковий простір Rᵈ (d = 1000+)", size=14, bold=True))

    # Точки u, v, w у лівій панелі
    u_x, u_y = LX0 + 90, LY0 + 130
    v_x, v_y = LX0 + 260, LY0 + 110
    w_x, w_y = LX0 + 180, LY0 + 250

    # Лінії між ними (відстані)
    out.append(line(u_x, u_y, v_x, v_y, color=POS, sw=2.0))
    out.append(line(u_x, u_y, w_x, w_y, color=NEG, sw=1.8, dash="4 3"))
    out.append(line(v_x, v_y, w_x, w_y, color=FIELD, sw=1.8, dash="4 3"))

    out.append(dot(u_x, u_y, 6.0, POS))
    out.append(dot(v_x, v_y, 6.0, POS))
    out.append(dot(w_x, w_y, 5.0, INK))

    out.append(text(u_x - 14, u_y - 6, "u", size=15, bold=True, color=POS))
    out.append(text(v_x + 14, v_y - 6, "v", size=15, bold=True, color=POS))
    out.append(text(w_x, w_y + 20, "w", size=14, color=INK))

    out.append(text((u_x + v_x) / 2, (u_y + v_y) / 2 - 12, "||u - v|| = L", size=13, bold=True, color=POS))

    # Центральна стрілка-трансформація: f(x) = (1/√k) R x
    AX, AY = LX0 + LW + 20, LY0 + LH / 2
    out.append(arrow(AX, AY, AX + 75, AY, color=INK, sw=2.4))
    out.append(text(AX + 40, AY - 20, "f(x) = R·x / √k", size=12, bold=True, color=NEG))
    out.append(text(AX + 40, AY + 22, "Випадкова", size=11, color=MUTED))
    out.append(text(AX + 40, AY + 38, "матриця R", size=11, color=MUTED))

    # Права панель: k-вимірний простір (k << d)
    RX0, RY0, RW, RH = AX + 100, LY0, 360, 320
    out.append(rect(RX0, RY0, RW, RH, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    out.append(text(RX0 + RW / 2, RY0 + 26, "Проєктований простір Rᵏ (k ≈ 100)", size=14, bold=True))

    # Проєктовані точки
    pu_x, pu_y = RX0 + 85, RY0 + 135
    pv_x, pv_y = RX0 + 265, RY0 + 105
    pw_x, pw_y = RX0 + 175, RY0 + 245

    out.append(line(pu_x, pu_y, pv_x, pv_y, color=POS, sw=2.0))
    out.append(line(pu_x, pu_y, pw_x, pw_y, color=NEG, sw=1.8, dash="4 3"))
    out.append(line(pv_x, pv_y, pw_x, pw_y, color=FIELD, sw=1.8, dash="4 3"))

    out.append(dot(pu_x, pu_y, 6.0, POS))
    out.append(dot(pv_x, pv_y, 6.0, POS))
    out.append(dot(pw_x, pw_y, 5.0, INK))

    out.append(text(pu_x - 16, pu_y - 6, "f(u)", size=14, bold=True, color=POS))
    out.append(text(pv_x + 18, pv_y - 6, "f(v)", size=14, bold=True, color=POS))
    out.append(text(pw_x, pw_y + 20, "f(w)", size=13, color=INK))

    out.append(text((pu_x + pv_x) / 2, (pu_y + pv_y) / 2 - 12, "||f(u) - f(v)|| ≈ L ± εL", size=13, bold=True, color=POS))

    # Нижній висновок
    out.append(text(W / 2, H - 24, "Всі попарні відстані зберігаються з відносною похибкою не більше ε", size=13, bold=True, color=INK))

    return render(os.path.join(OUT, 'random-projection-geometry.svg'), W, H, *out,
                  title="Збереження попарних відстаней при випадковому проєктуванні")


# ── 3. Структура матриць проєктування: Гаусова vs Розріджена vs FJLT ────────
def fig_sparse_matrices():
    W, H = 880, 440
    out = []
    out.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    BW = 250
    BH = 320
    Y0 = 50

    # Блок 1: Dense Gaussian
    X1 = 35
    out.append(rect(X1, Y0, BW, BH, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    out.append(text(X1 + BW / 2, Y0 + 26, "Гаусова (Dense)", size=14, bold=True))
    out.append(text(X1 + BW / 2, Y0 + 46, "R[i,j] ~ N(0, 1)", size=12, color=MUTED))

    grid_seed = rnd(12345)
    MX1, MY1 = X1 + 25, Y0 + 65
    cell_s = 20
    for r in range(8):
        for c in range(10):
            val = next(grid_seed)
            col = "#d5dbdb" if val < 0.33 else ("#aeb6bf" if val < 0.66 else "#85929e")
            out.append(rect(MX1 + c * cell_s, MY1 + r * cell_s, cell_s - 2, cell_s - 2, fill=col, stroke="none"))

    out.append(text(X1 + BW / 2, Y0 + 245, "100% ненульових чисел", size=12, bold=True, color=POS))
    out.append(text(X1 + BW / 2, Y0 + 265, "Обчислення: O(d · k) множень", size=11, color=INK))
    out.append(text(X1 + BW / 2, Y0 + 285, "Повна матриця у пам'яті", size=11, color=MUTED))

    # Блок 2: Sparse Achlioptas
    X2 = X1 + BW + 30
    out.append(rect(X2, Y0, BW, BH, fill=FILL, stroke=FIELD, sw=1.6, rx=6))
    out.append(text(X2 + BW / 2, Y0 + 26, "Розріджена Ахіоптаса", size=14, bold=True, color=FIELD))
    out.append(text(X2 + BW / 2, Y0 + 46, "значення {+√3, 0, -√3}", size=12, color=MUTED))

    grid_seed2 = rnd(67890)
    MX2, MY2 = X2 + 25, Y0 + 65
    for r in range(8):
        for c in range(10):
            val = next(grid_seed2)
            if val < 0.166:
                col = POS
            elif val > 0.833:
                col = NEG
            else:
                col = BG
            out.append(rect(MX2 + c * cell_s, MY2 + r * cell_s, cell_s - 2, cell_s - 2,
                            fill=col, stroke=LINE if col == BG else "none", sw=0.5))

    out.append(text(X2 + BW / 2, Y0 + 245, "66.7% нулів (2/3 комірок)", size=12, bold=True, color=FIELD))
    out.append(text(X2 + BW / 2, Y0 + 265, "Прискорення у 3 рази", size=11, color=INK))
    out.append(text(X2 + BW / 2, Y0 + 285, "Лише додавання та віднімання", size=11, color=MUTED))

    # Блок 3: Fast JL Transform
    X3 = X2 + BW + 30
    out.append(rect(X3, Y0, BW, BH, fill=FILL, stroke=NEG, sw=1.2, rx=6))
    out.append(text(X3 + BW / 2, Y0 + 26, "Fast JL (FJLT)", size=14, bold=True, color=NEG))
    out.append(text(X3 + BW / 2, Y0 + 46, "Матриця P = S · H · D", size=12, color=MUTED))

    SX, SY = X3 + 30, Y0 + 75
    # D: діагональна
    out.append(rect(SX, SY, 45, 140, fill="#f2f4f4", stroke=INK, sw=1.0))
    out.append(line(SX, SY, SX + 45, SY + 140, color=POS, sw=2.0))
    out.append(text(SX + 22, SY + 160, "D (±1)", size=11, bold=True))

    out.append(text(SX + 55, SY + 70, "×", size=14, bold=True))

    # H: Адамара
    out.append(rect(SX + 70, SY, 55, 140, fill="#eaf2f8", stroke=NEG, sw=1.2))
    out.append(text(SX + 97, SY + 70, "H", size=16, bold=True, color=NEG))
    out.append(text(SX + 97, SY + 160, "Адамар", size=11, bold=True))

    out.append(text(SX + 135, SY + 70, "×", size=14, bold=True))

    # S: вибірка
    out.append(rect(SX + 148, SY, 40, 140, fill="#e8f8f5", stroke=FIELD, sw=1.2))
    out.append(text(SX + 168, SY + 70, "S", size=16, bold=True, color=FIELD))
    out.append(text(SX + 168, SY + 160, "Вибірка", size=11, bold=True))

    out.append(text(X3 + BW / 2, Y0 + 245, "Складність: O(d · log d)", size=12, bold=True, color=NEG))
    out.append(text(X3 + BW / 2, Y0 + 265, "Швидке перетворення Уолша", size=11, color=INK))
    out.append(text(X3 + BW / 2, Y0 + 285, "Оптимально при великих d", size=11, color=MUTED))

    out.append(text(W / 2, H - 20, "Порівняння обчислювальної складності та структури матриць проєктування", size=13, color=MUTED))

    return render(os.path.join(OUT, 'sparse-matrix-structure.svg'), W, H, *out,
                  title="Структура та типи матриць випадкового проєктування")


# ── 4. Емпіричний розподіл спотворення відстаней (гістограма) ────────────────
def fig_distortion_hist():
    W, H = 880, 440
    out = []
    out.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    GX, GY, GW, GH = 90, 60, 720, 310

    out.append(line(GX, GY + GH, GX + GW, GY + GH, color=LINE, sw=1.6))
    out.append(line(GX, GY, GX, GY + GH, color=LINE, sw=1.6))

    nb = 35
    min_v, max_v = 0.65, 1.35

    bins = []
    for b in range(nb):
        mid = min_v + (max_v - min_v) * (b + 0.5) / float(nb)
        val = math.exp(-0.5 * ((mid - 1.0) / 0.055) ** 2)
        bins.append(val)

    max_b = max(bins)
    bin_w = (GW / float(nb)) - 2.0

    for b in range(nb):
        mid = min_v + (max_v - min_v) * (b + 0.5) / float(nb)
        h = (bins[b] / max_b) * (GH - 40)
        bx = GX + b * (GW / float(nb)) + 1.0
        by = GY + GH - h
        col = FIELD if (0.85 <= mid <= 1.15) else POS
        out.append(rect(bx, by, bin_w, h, fill=col, stroke="none"))

    cx = GX + GW * ((1.0 - min_v) / (max_v - min_v))
    out.append(line(cx, GY, cx, GY + GH, color=INK, sw=2.0, dash="4 3"))
    out.append(text(cx, GY - 12, "Ідеальна відстань (коефіцієнт 1.0)", size=12, bold=True, color=INK))

    e_left = GX + GW * ((0.85 - min_v) / (max_v - min_v))
    e_right = GX + GW * ((1.15 - min_v) / (max_v - min_v))
    out.append(line(e_left, GY + 20, e_left, GY + GH, color=POS, sw=1.6, dash="3 3"))
    out.append(line(e_right, GY + 20, e_right, GY + GH, color=POS, sw=1.6, dash="3 3"))

    out.append(text(e_left, GY + 14, "1 − ε (0.85)", size=11, bold=True, color=POS))
    out.append(text(e_right, GY + 14, "1 + ε (1.15)", size=11, bold=True, color=POS))

    for val in (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3):
        x = GX + GW * ((val - min_v) / (max_v - min_v))
        out.append(line(x, GY + GH, x, GY + GH + 6, color=LINE, sw=1.2))
        out.append(text(x, GY + GH + 22, "%.1f" % val, size=12, color=MUTED))

    out.append(text(GX + GW / 2, GY + GH + 48, "Відношення відстаней у проєктованому просторі до початкового: ||f(u) - f(v)|| / ||u - v||", size=13, bold=True))
    out.append(text(GX - 50, GY + GH / 2, "Кількість пар точок", size=13, bold=True, anchor="middle"))

    badge_txt = "99.8% пар потрапляють у коридор [1−ε, 1+ε]\nпри стисканні розмірності з d=2048 до k=256"
    badge_body, _, _ = textbox(GX + 530, GY + 70, badge_txt, size=11, pad=8, color=INK, fill="#fdfefe", stroke=FIELD)
    out.append(badge_body)

    return render(os.path.join(OUT, 'distortion-histogram.svg'), W, H, *out,
                  title="Розподіл спотворення відстаней при стисканні розмірності")


def main():
    fig_jl_scaling()
    fig_rp_geometry()
    fig_sparse_matrices()
    fig_distortion_hist()
    print("Фігури успішно згенеровано у %s" % OUT)


if __name__ == '__main__':
    main()
