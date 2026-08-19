# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Мінковського про опуклі тіла» (book/algorithms/complexity-computability/minkowski-theorem)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_minkowski_convex_body():
    """Центральна симетрія та опукле тіло K у ґратці L, що захоплює ненульові вузли."""
    W, H = 1040, 520
    frags = []

    # Тло
    frags.append(rect(30, 45, 980, 445, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=12))

    ox, oy = 520, 270
    u1 = (130, 20)
    u2 = (40, 110)

    # Фундаментальна комірка F_0 біля початку координат
    f_pts = [
        (ox, oy),
        (ox + u1[0], oy - u1[1]),
        (ox + u1[0] + u2[0], oy - u1[1] - u2[1]),
        (ox + u2[0], oy - u2[1])
    ]
    f_path = "M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" % (
        f_pts[0][0], f_pts[0][1], f_pts[1][0], f_pts[1][1],
        f_pts[2][0], f_pts[2][1], f_pts[3][0], f_pts[3][1]
    )
    frags.append('<path d="%s" fill="#eaf0fd" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (f_path, NEG))
    frags.append(text(ox + 85, oy - 65, "F₀ [det(L)]", size=13, bold=True, color=NEG))

    # Опукле центрально-симетричне тіло K (еліпс під кутом)
    theta = math.radians(22)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    a, b = 210, 130
    steps = 72
    k_pts = []
    for s in range(steps):
        phi = 2 * math.pi * s / steps
        lx = a * math.cos(phi)
        ly = b * math.sin(phi)
        rx = ox + lx * cos_t - ly * sin_t
        ry = oy - (lx * sin_t + ly * cos_t)
        k_pts.append((rx, ry))

    k_d = "M " + " L ".join("%.1f,%.1f" % p for p in k_pts) + " Z"
    frags.append('<path d="%s" fill="#fdecea" fill-opacity="0.65" stroke="%s" stroke-width="2.5"/>' % (k_d, POS))

    # Вузли ґратки
    for i in range(-3, 4):
        for j in range(-3, 4):
            px = ox + i * u1[0] + j * u2[0]
            py = oy - i * u1[1] - j * u2[1]
            if 50 <= px <= 990 and 65 <= py <= 470:
                # Перевіряємо, чи точка всередині еліпса
                dx = px - ox
                dy = -(py - oy)
                ex = dx * cos_t + dy * sin_t
                ey = -dx * sin_t + dy * cos_t
                inside = (ex * ex) / (a * a) + (ey * ey) / (b * b) <= 1.0

                if i == 0 and j == 0:
                    frags.append(circle(px, py, 6, fill=INK, stroke="#ffffff", sw=2))
                    frags.append(text(px - 18, py + 18, "0", size=15, bold=True, color=INK))
                elif inside:
                    frags.append(circle(px, py, 6.5, fill=POS, stroke="#ffffff", sw=2))
                else:
                    frags.append(circle(px, py, 4, fill="#94a3b8", stroke="none", sw=0))

    # Позначення базисних векторів
    frags.append(arrow(ox, oy, ox + u1[0], oy - u1[1], color=INK, sw=2.5))
    frags.append(text(ox + u1[0] + 18, oy - u1[1] + 12, "b₁", size=15, bold=True, color=INK))

    frags.append(arrow(ox, oy, ox + u2[0], oy - u2[1], color=INK, sw=2.5))
    frags.append(text(ox + u2[0] - 18, oy - u2[1] - 10, "b₂", size=15, bold=True, color=INK))

    # Виділення знайдених точок v та -v
    vx1, vy1 = ox + u1[0], oy - u1[1]
    vx2, vy2 = ox - u1[0], oy + u1[1]
    frags.append(arrow(ox, oy, vx1, vy1, color=POS, sw=3))
    frags.append(text(vx1 + 22, vy1 - 10, "v ∈ L ∩ K", size=14, bold=True, color=POS))

    frags.append(arrow(ox, oy, vx2, vy2, color=POS, sw=3))
    frags.append(text(vx2 - 30, vy2 + 20, "−v ∈ L ∩ K", size=14, bold=True, color=POS))

    # Пояснювальний напис про об'єм тіла
    frags.append(text(ox + 160, oy + 120, "Опукле тіло K (vol(K) > 4·det(L))", size=15, bold=True, color=POS))
    frags.append(text(ox + 160, oy + 142, "Симетрія: x ∈ K ⇒ −x ∈ K", size=13, bold=False, color=MUTED))

    # Панель умови
    band, _, _ = textbox(520, 460,
                         "Теорема Мінковського: якщо vol(K) > 2ⁿ·det(L), то K обов'язково містить ненульову точку ґратки ±v ≠ 0.",
                         size=13, bold=True, fill="#fff6e5", stroke=AMBER_S, sw=1.8, pad=10)
    frags.append(band)

    render(os.path.join(IMG, "minkowski-convex-body.svg"), W, H, *frags,
           title="Геометрія теореми Мінковського: опукле центрально-симетричне тіло у ґратці")


def fig_blichfeldt_folding():
    """Доведення Бліхфельдта: стиснення (1/2)K, розбиття на комірки та накладання у F_0."""
    W, H = 1060, 490
    frags = []

    # Ліва панель: простір з тілом (1/2)K і розбиттям
    frags.append(rect(30, 45, 480, 410, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=10))
    frags.append(text(270, 75, "1. Тіло S = ½K у просторі ℝ²", size=16, bold=True, color=INK))
    frags.append(text(270, 96, "vol(S) = 2⁻ⁿ · vol(K) > det(L)", size=13, bold=True, color=POS))

    # Права панель: фундаментальна комірка F_0 з накладанням частин
    frags.append(rect(550, 45, 480, 410, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=10))
    frags.append(text(790, 75, "2. Згортання в комірку F₀ (mod L)", size=16, bold=True, color=INK))
    frags.append(text(790, 96, "Сума об'ємів частин перевищує det(L) ⇒ є перетин", size=13, bold=True, color=FIELD))

    # Координати лівої панелі
    lx0, ly0 = 240, 270
    dw, dh = 110, 80

    # Сітка фундаментальних комірок (обмежена, щоб не заходити на заголовок)
    for i in range(-1, 2):
        for j in range(-1, 2):
            cx = lx0 + i * dw
            cy = ly0 - j * dh
            frags.append(rect(cx, cy - dh, dw, dh, fill="none", stroke="#cbd5e1", sw=1.2, rx=0))

    # Тіло S = (1/2)K
    sa, sb = 95, 65
    stheta = math.radians(20)
    scos, ssin = math.cos(stheta), math.sin(stheta)
    s_pts = []
    for s in range(48):
        phi = 2 * math.pi * s / 48
        px = sa * math.cos(phi)
        py = sb * math.sin(phi)
        rx = lx0 + 50 + px * scos - py * ssin
        ry = ly0 - 35 - (px * ssin + py * scos)
        s_pts.append((rx, ry))
    s_d = "M " + " L ".join("%.1f,%.1f" % p for p in s_pts) + " Z"
    frags.append('<path d="%s" fill="#fdecea" fill-opacity="0.75" stroke="%s" stroke-width="2.2"/>' % (s_d, POS))

    # Дві точки x та y всередині S
    pt_x = (lx0 + 15, ly0 - 45)
    pt_y = (lx0 + 15 + dw, ly0 - 45 - dh)
    frags.append(circle(pt_x[0], pt_x[1], 5.5, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(text(pt_x[0] - 14, pt_x[1] - 8, "x", size=14, bold=True, color=NEG))

    frags.append(circle(pt_y[0], pt_y[1], 5.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    frags.append(text(pt_y[0] + 14, pt_y[1] - 8, "y", size=14, bold=True, color=FIELD))

    frags.append(text(270, 425, "Точки x, y ∈ S мають різницю x − y ∈ L", size=13, bold=True, color=INK))

    # Права панель: одна комірка F_0 з накладеними фрагментами через path (не rect-блоками)
    rx0, ry0 = 680, 310
    fw, fh = 200, 150
    frags.append(rect(rx0, ry0 - fh, fw, fh, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    frags.append(text(rx0 + 40, ry0 - fh + 24, "F₀", size=16, bold=True, color=NEG))

    # Фрагмент 1 (від x) - як path
    p1 = "M %d,%d h 110 v 80 h -110 Z" % (rx0 + 20, ry0 - fh + 40)
    frags.append('<path d="%s" fill="#fdecea" fill-opacity="0.7" stroke="%s" stroke-width="1.5"/>' % (p1, POS))

    # Фрагмент 2 (від y) - як path
    p2 = "M %d,%d h 100 v 75 h -100 Z" % (rx0 + 70, ry0 - fh + 60)
    frags.append('<path d="%s" fill="#e9f7ef" fill-opacity="0.7" stroke="%s" stroke-width="1.5"/>' % (p2, FIELD))

    # Точка спільного перекриття z
    zx, zy = rx0 + 95, ry0 - fh + 85
    frags.append(circle(zx, zy, 6.5, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(zx - 16, zy - 12, "z", size=14, bold=True, color=POS))
    frags.append(text(790, 345, "Точка перекриття: z = x mod L = y mod L", size=13, bold=True, color=POS))

    # Текстовий висновок
    frags.append(text(790, 425, "Звідси x − y = ½(2x) + ½(−2y) ∈ K ∩ (L \\ {0})", size=13, bold=True, color=POS))

    # Стрілка переходу між панелями
    frags.append(arrow(515, 250, 545, 250, color=INK, sw=2.5))

    render(os.path.join(IMG, "blichfeldt-folding.svg"), W, H, *frags,
           title="Принцип згортання Бліхфельдта: перекриття об'ємів у фундаментальній комірці")


def fig_minkowski_svp_bound():
    """Зв'язок радіуса Мінковського, послідовних мінімумів та редукції ґраток."""
    W, H = 1040, 480
    frags = []

    # Ліва панель: Куля Мінковського та перший мінімум λ_1
    frags.append(rect(30, 45, 475, 415, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=10))
    frags.append(text(265, 75, "Перший мінімум λ₁(L) та куля B(R_M)", size=15, bold=True, color=INK))

    ox1, oy1 = 265, 280
    # Вузли ґратки
    v1 = (110, 30)
    v2 = (-50, 100)

    # Куля радіуса R_M (перша оцінка Мінковського)
    r_m = 114
    frags.append(circle(ox1, oy1, r_m, fill="#fdecea", stroke=POS, sw=2))
    frags.append(line(ox1, oy1, ox1 + r_m * 0.707, oy1 - r_m * 0.707, color=POS, sw=1.8, dash="4,3"))
    frags.append(text(ox1 + 15, oy1 - 92, "R_M ≤ √n · det(L)¹/ⁿ", size=12, bold=True, color=POS))

    # Точки ґратки
    for i in range(-2, 3):
        for j in range(-2, 3):
            px = ox1 + i * v1[0] + j * v2[0]
            py = oy1 - i * v1[1] - j * v2[1]
            if 45 <= px <= 490 and 95 <= py <= 445:
                if i == 0 and j == 0:
                    frags.append(circle(px, py, 5, fill=INK, stroke="#ffffff", sw=1.5))
                elif (i, j) in [(1, 0), (-1, 0)]:
                    frags.append(circle(px, py, 6, fill=FIELD, stroke="#ffffff", sw=2))
                else:
                    frags.append(circle(px, py, 3.5, fill="#94a3b8", stroke="none", sw=0))

    # Найкоротший вектор lambda_1
    frags.append(arrow(ox1, oy1, ox1 + v1[0], oy1 - v1[1], color=FIELD, sw=2.8))
    frags.append(text(ox1 + v1[0] + 18, oy1 - v1[1] + 12, "v₁ (||v₁|| = λ₁ ≤ R_M)", size=13, bold=True, color=FIELD))

    frags.append(text(265, 435, "Існування гарантоване: λ₁(L) ≤ 2·(det(L)/V_n)¹/ⁿ", size=12, bold=True, color=INK))

    # Права панель: Ієрархія складності SVP та алгоритми наближення
    frags.append(rect(535, 45, 475, 415, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=10))
    frags.append(text(770, 75, "Ієрархія складності та алгоритми SVP", size=15, bold=True, color=INK))

    # Сходинки алгоритмів
    b1, _, _ = textbox(770, 130, "Точний SVP (Експоненційний час 2^O(n))\nПовний перебір у кулі Мінковського / Sieving",
                       size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=8)
    b2, _, _ = textbox(770, 215, "Блокова редукція BKZ (Субекспоненційний час)\nФактор наближення k^(n/2k) для блоку k",
                       size=12, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=1.8, pad=8)
    b3, _, _ = textbox(770, 300, "Алгоритм LLL (Поліноміальний час O(n⁶))\nФактор наближення 2^((n-1)/2) від λ₁(L)",
                       size=12, bold=True, fill="#e9f7ef", stroke=FIELD, sw=1.8, pad=8)
    b4, _, _ = textbox(770, 385, "Гарантія Мінковського: λ₁ ≤ √n · det(L)¹/ⁿ\nНевіддільна основа криптографічної стійкості (LWE/SIS)",
                       size=12, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=8)

    frags += [b1, b2, b3, b4]
    frags.append(arrow(770, 160, 770, 190, color=INK, sw=1.8))
    frags.append(arrow(770, 245, 770, 275, color=INK, sw=1.8))
    frags.append(arrow(770, 330, 770, 360, color=INK, sw=1.8))

    render(os.path.join(IMG, "minkowski-svp-bound.svg"), W, H, *frags,
           title="Оцінка Мінковського для задачі найкоротшого вектора та алгоритмічний спектр")


if __name__ == "__main__":
    fig_minkowski_convex_body()
    fig_blichfeldt_folding()
    fig_minkowski_svp_bound()
    print("OK:", sorted(os.listdir(IMG)))
