# -*- coding: utf-8 -*-
"""Фігури до статті «Еліптичні криві». Запуск: python figs.py
Виводить SVG у ./img/. Усі тексти та прямокутники вирівняно під svgcheck."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Додавання точок (P + Q = R') ─────────────────────────────────────
def fig_ec_point_addition():
    W, H = 780, 420
    f = []

    # Фон та заголовок
    f.append(rect(15, 45, 490, 355, fill="#fbfcfd", stroke=LINE, sw=1.5))
    f.append(rect(520, 45, 245, 355, fill="#f4f6f8", stroke=LINE, sw=1.5))

    # Лівий блок: крива та геометрія
    ox, oy = 210, 220
    f.append(line(40, oy, 470, oy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(ox, 65, ox, 380, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(460, oy - 8, "X", size=12, color=MUTED, bold=True))
    f.append(text(ox + 8, 80, "Y", size=12, color=MUTED, bold=True))

    pts_upper = []
    pts_lower = []
    for i in range(-21, 27):
        x = i / 10.0
        val = x**3 - 3*x + 3.5
        if val >= 0:
            y = math.sqrt(val)
            px = ox + x * 50
            py_u = oy - y * 45
            py_l = oy + y * 45
            pts_upper.append((px, py_u))
            pts_lower.append((px, py_l))

    path_u = "M " + " L ".join("%.1f,%.1f" % p for p in pts_upper)
    path_l = "M " + " L ".join("%.1f,%.1f" % p for p in pts_lower)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_u, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_l, NEG))

    px_P, py_P = 150.0, 115.7
    px_Q, py_Q = 235.0, 154.4

    line_x1, line_y1 = 70.0, 115.7 - (150 - 70) * 0.4553
    line_x2, line_y2 = 410.0, 115.7 + (410 - 150) * 0.4553
    f.append(line(line_x1, line_y1, line_x2, line_y2, color=POS, sw=2.0))

    px_R, py_R = 345.0, 204.5
    px_Rp, py_Rp = 345.0, 235.5

    f.append(line(px_R, py_R, px_Rp, py_Rp, color=MUTED, sw=1.5, dash="3,3"))

    f.append(circle(px_P, py_P, 5, fill=POS, stroke=POS))
    f.append(circle(px_Q, py_Q, 5, fill=POS, stroke=POS))
    f.append(circle(px_R, py_R, 5, fill=MUTED, stroke=MUTED))
    f.append(circle(px_Rp, py_Rp, 6, fill=FIELD, stroke=FIELD))

    f.append(text(px_P - 15, py_P - 10, "P", size=15, color=POS, bold=True))
    f.append(text(px_Q + 12, py_Q - 10, "Q", size=15, color=POS, bold=True))
    f.append(text(px_R + 14, py_R + 5, "R (P*Q)", size=13, color=MUTED, bold=True))
    f.append(text(px_Rp + 14, py_Rp + 15, "R' = P + Q", size=15, color=FIELD, bold=True))

    f.append(text(80, 85, "y² = x³ + a·x + b", size=13, color=NEG, bold=True, italic=True))

    f.append(text(642, 75, "Геометрія додавання", size=16, bold=True, color=INK))
    f.append(line(535, 92, 750, 92, color=MUTED, sw=1))

    b1 = ("1. Проводимо січну\n"
          "   пряму L через P та Q.")
    f.append(fitbox(535, 105, 215, 60, b1, size=12, fill="#ffffff", stroke=LINE))

    b2 = ("2. Пряма L перетинає\n"
          "   кубіку в 3-й точці R.")
    f.append(fitbox(535, 180, 215, 60, b2, size=12, fill="#ffffff", stroke=LINE))

    b3 = ("3. Віддзеркалюємо R\n"
          "   відносно осі X.\n"
          "   Отримуємо R' = P + Q.")
    f.append(fitbox(535, 255, 215, 70, b3, size=12, fill="#eafaf1", stroke=FIELD, bold=True))

    f.append(text(642, 355, "Правило колінеарності:", size=12, bold=True, color=MUTED))
    f.append(text(642, 375, "P + Q + R = O", size=14, bold=True, color=POS))

    render(os.path.join(IMG, "fig-ec-point-addition.svg"), W, H, *f)


# ── Фігура 2: Подвоєння точки (P + P = 2·P) ──────────────────────────────────
def fig_ec_point_doubling():
    W, H = 780, 420
    f = []

    f.append(rect(15, 45, 490, 355, fill="#fbfcfd", stroke=LINE, sw=1.5))
    f.append(rect(520, 45, 245, 355, fill="#f4f6f8", stroke=LINE, sw=1.5))

    ox, oy = 210, 220
    f.append(line(40, oy, 470, oy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(ox, 65, ox, 380, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(460, oy - 8, "X", size=12, color=MUTED, bold=True))
    f.append(text(ox + 8, 80, "Y", size=12, color=MUTED, bold=True))

    pts_upper = []
    pts_lower = []
    for i in range(-21, 27):
        x = i / 10.0
        val = x**3 - 3*x + 3.5
        if val >= 0:
            y = math.sqrt(val)
            px = ox + x * 50
            py_u = oy - y * 45
            py_l = oy + y * 45
            pts_upper.append((px, py_u))
            pts_lower.append((px, py_l))

    path_u = "M " + " L ".join("%.1f,%.1f" % p for p in pts_upper)
    path_l = "M " + " L ".join("%.1f,%.1f" % p for p in pts_lower)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_u, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_l, NEG))

    px_P, py_P = 170.0, 115.6

    lx1, ly1 = 60.0, 115.6 - (170 - 60) * 0.209
    lx2, ly2 = 430.0, 115.6 + (430 - 170) * 0.209
    f.append(line(lx1, ly1, lx2, ly2, color=POS, sw=2.0))

    px_R, py_R = 360.0, 155.3
    px_2P, py_2P = 360.0, 284.7

    f.append(line(px_R, py_R, px_2P, py_2P, color=MUTED, sw=1.5, dash="3,3"))

    f.append(circle(px_P, py_P, 6, fill=POS, stroke=POS))
    f.append(circle(px_R, py_R, 5, fill=MUTED, stroke=MUTED))
    f.append(circle(px_2P, py_2P, 6, fill=FIELD, stroke=FIELD))

    f.append(text(px_P - 18, py_P - 10, "P", size=15, color=POS, bold=True))
    f.append(text(px_R + 12, py_R - 8, "R (перетин)", size=12, color=MUTED, bold=True))
    f.append(text(px_2P + 12, py_2P + 15, "R' = 2·P", size=15, color=FIELD, bold=True))

    f.append(text(80, 85, "y² = x³ + a·x + b", size=13, color=NEG, bold=True, italic=True))
    f.append(text(270, 110, "Дотична в точці P", size=12, color=POS, bold=True))

    f.append(text(642, 75, "Геометрія подвоєння", size=16, bold=True, color=INK))
    f.append(line(535, 92, 750, 92, color=MUTED, sw=1))

    b1 = ("1. Проводити дотичну\n"
          "   пряму L до кривої в P.")
    f.append(fitbox(535, 105, 215, 60, b1, size=12, fill="#ffffff", stroke=LINE))

    b2 = ("2. Дотична кратністю 2\n"
          "   перетинає криву в R.")
    f.append(fitbox(535, 180, 215, 60, b2, size=12, fill="#ffffff", stroke=LINE))

    b3 = ("3. Віддзеркалюємо R\n"
          "   відносно осі X.\n"
          "   Отримуємо R' = 2·P.")
    f.append(fitbox(535, 255, 215, 70, b3, size=12, fill="#eafaf1", stroke=FIELD, bold=True))

    f.append(text(642, 355, "Граничний випадок:", size=12, bold=True, color=MUTED))
    f.append(text(642, 375, "P + P + R = O", size=14, bold=True, color=POS))

    render(os.path.join(IMG, "fig-ec-point-doubling.svg"), W, H, *f)


# ── Фігура 3: Дискримінант та морфологія ──────────────────────────────────────
def fig_ec_singularities():
    W, H = 820, 380
    f = []

    f.append(rect(15, 45, 250, 315, fill="#f2faf4", stroke=FIELD, sw=1.8))
    f.append(rect(285, 45, 250, 315, fill="#f4f6f8", stroke=LINE, sw=1.8))
    f.append(rect(555, 45, 250, 315, fill="#fdf4f3", stroke=POS, sw=1.8))

    f.append(text(140, 72, "Δ > 0 (Гладка)", size=16, bold=True, color=FIELD))
    f.append(text(140, 92, "2 зв'язані компоненти", size=12, color=MUTED, bold=True))

    ox1, oy1 = 140, 210
    f.append(line(35, oy1, 245, oy1, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox1, 115, ox1, 305, color=MUTED, sw=1, dash="3,3"))

    island_u, island_l = [], []
    for i in range(-17, 1):
        x = i / 10.0
        val = x**3 - 3*x
        if val >= 0:
            y = math.sqrt(val)
            island_u.append((ox1 + x*35, oy1 - y*30))
            island_l.append((ox1 + x*35, oy1 + y*30))
    path_is = ("M " + " L ".join("%.1f,%.1f" % p for p in island_u) +
               " L " + " L ".join("%.1f,%.1f" % p for p in reversed(island_l)) + " Z")
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_is, FIELD))

    branch_u, branch_l = [], []
    for i in range(173, 260):
        x = i / 100.0
        val = x**3 - 3*x
        if val >= 0:
            y = math.sqrt(val)
            branch_u.append((ox1 + x*35, oy1 - y*30))
            branch_l.append((ox1 + x*35, oy1 + y*30))
    path_bu = "M " + " L ".join("%.1f,%.1f" % p for p in branch_u)
    path_bl = "M " + " L ".join("%.1f,%.1f" % p for p in branch_l)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_bu, FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_bl, FIELD))

    f.append(fitbox(30, 315, 220, 35, "y² = x³ − 3·x (3 корені)", size=12, fill="#ffffff", stroke=FIELD))

    f.append(text(410, 72, "Δ < 0 (Гладка)", size=16, bold=True, color=INK))
    f.append(text(410, 92, "1 зв'язаний компонент", size=12, color=MUTED, bold=True))

    ox2, oy2 = 410, 210
    f.append(line(305, oy2, 515, oy2, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox2, 115, ox2, 305, color=MUTED, sw=1, dash="3,3"))

    branch2_u, branch2_l = [], []
    for i in range(-100, 180):
        x = i / 100.0
        val = x**3 + 1
        if val >= 0:
            y = math.sqrt(val)
            branch2_u.append((ox2 + x*35, oy2 - y*30))
            branch2_l.append((ox2 + x*35, oy2 + y*30))
    path_b2u = "M " + " L ".join("%.1f,%.1f" % p for p in branch2_u)
    path_b2l = "M " + " L ".join("%.1f,%.1f" % p for p in branch2_l)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_b2u, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path_b2l, NEG))

    f.append(fitbox(300, 315, 220, 35, "y² = x³ + 1 (1 корінь)", size=12, fill="#ffffff", stroke=LINE))

    f.append(text(680, 72, "Δ = 0 (Особливі)", size=16, bold=True, color=POS))
    f.append(text(680, 92, "Вузол та Касп (не еліптичні)", size=12, color=MUTED, bold=True))

    ox3, oy3 = 680, 210
    f.append(line(575, oy3, 785, oy3, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox3, 115, ox3, 305, color=MUTED, sw=1, dash="3,3"))

    cusp_u, cusp_l = [], []
    for i in range(0, 180):
        x = i / 100.0
        val = x**3
        y = math.sqrt(val)
        cusp_u.append((ox3 + x*35, oy3 - y*30))
        cusp_l.append((ox3 + x*35, oy3 + y*30))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % ("M " + " L ".join("%.1f,%.1f" % p for p in cusp_u), POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % ("M " + " L ".join("%.1f,%.1f" % p for p in cusp_l), POS))

    f.append(circle(ox3, oy3, 4, fill=POS, stroke=POS))
    f.append(text(ox3 + 12, oy3 + 15, "Касп (0,0)", size=11, color=POS, bold=True))

    f.append(fitbox(570, 315, 220, 35, "y² = x³ (Касп) / y² = x³+x² (Вузол)", size=11, fill="#ffffff", stroke=POS))

    render(os.path.join(IMG, "fig-ec-singularities.svg"), W, H, *f)


# ── Фігура 4: Дискретна крива над F_p ─────────────────────────────────────────
def fig_ec_finite_field():
    W, H = 780, 420
    f = []

    f.append(rect(15, 45, 490, 355, fill="#fbfcfd", stroke=LINE, sw=1.5))
    f.append(rect(520, 45, 245, 355, fill="#f4f6f8", stroke=LINE, sw=1.5))

    p = 17
    gx0, gy0 = 60, 360
    step = 22.0

    for i in range(p):
        f.append(line(gx0 + i*step, gy0, gx0 + i*step, gy0 - (p-1)*step, color="#e5e7eb", sw=1))
        f.append(line(gx0, gy0 - i*step, gx0 + (p-1)*step, gy0 - i*step, color="#e5e7eb", sw=1))

    f.append(line(gx0 - 10, gy0 - 8.5*step, gx0 + (p-1)*step + 10, gy0 - 8.5*step, color=POS, sw=1.2, dash="4,4"))
    f.append(text(gx0 + (p-1)*step + 20, gy0 - 8.5*step + 4, "y = p/2", size=10, color=POS, bold=True))

    ec_points = []
    for x in range(p):
        rhs = (x**3 + 2*x + 3) % p
        for y in range(p):
            if (y**2) % p == rhs:
                ec_points.append((x, y))

    for x, y in ec_points:
        px = gx0 + x * step
        py = gy0 - y * step
        if x == 5 and (y == 2 or y == 15):
            f.append(circle(px, py, 5, fill=FIELD, stroke=FIELD))
        else:
            f.append(circle(px, py, 4, fill=NEG, stroke=NEG))

    f.append(text(gx0 + (p-1)*step/2, gy0 + 22, "x (mod 17)", size=12, color=MUTED, bold=True))
    f.append(text(gx0 - 25, gy0 - (p-1)*step/2, "y", size=12, color=MUTED, bold=True))

    px_top = gx0 + 5 * step
    py_top = gy0 - 15 * step
    py_bot = gy0 - 2 * step
    f.append(line(px_top, py_top, px_top, py_bot, color=FIELD, sw=1.2, dash="2,2"))
    f.append(text(px_top + 8, py_top - 5, "(5, 15)", size=11, color=FIELD, bold=True))
    f.append(text(px_top + 8, py_bot + 12, "(5, 2)", size=11, color=FIELD, bold=True))

    f.append(text(642, 75, "Дискретна геометрія", size=16, bold=True, color=INK))
    f.append(line(535, 92, 750, 92, color=MUTED, sw=1))

    b1 = ("1. Точки утворюють\n"
          "   дискретну 2D сітку\n"
          "   розміру p × p.")
    f.append(fitbox(535, 105, 215, 65, b1, size=12, fill="#ffffff", stroke=LINE))

    b2 = ("2. Осіва симетрія:\n"
          "   y ↦ (p − y) mod p\n"
          "   відповідає -P.")
    f.append(fitbox(535, 185, 215, 65, b2, size=12, fill="#eafaf1", stroke=FIELD, bold=True))

    b3 = ("3. Прямі 'обгортаються'\n"
          "   на торі (mod p).\n"
          "   Хаос дає стійкість ECDLP.")
    f.append(fitbox(535, 265, 215, 75, b3, size=12, fill="#fdf4f3", stroke=POS, bold=True))

    f.append(text(642, 365, "Теорема Гассе:", size=12, bold=True, color=MUTED))
    f.append(text(642, 385, "|N - (p+1)| ≤ 2·√p", size=13, bold=True, color=NEG))

    render(os.path.join(IMG, "fig-ec-finite-field.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ec_point_addition()
    fig_ec_point_doubling()
    fig_ec_singularities()
    fig_ec_finite_field()
    print("Figures generated successfully in ./img/")
