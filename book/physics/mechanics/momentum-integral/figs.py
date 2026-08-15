# -*- coding: utf-8 -*-
import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

def make_control_volume():
    w, h = 750, 410
    frags = []

    frags.append(text(w / 2, 25, "Контрольний об'єм у примежовому шарі (баланс імпульсу)", size=16, bold=True))

    wall_y = 330
    frags.append(line(50, wall_y, 700, wall_y, color=LINE, sw=3))
    for x in range(50, 700, 15):
        frags.append(line(x, wall_y, x - 10, wall_y + 12, color=MUTED, sw=1))

    bl_curve = "M 120 330 Q 250 250 630 190 L 630 330 Z"
    frags.append('<path d="%s" fill="#eaf2f8" opacity="0.6" stroke="none"/>' % bl_curve)
    bl_edge = "M 120 330 Q 250 250 630 190"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (bl_edge, NEG))

    x1, x2, y_top = 180, 560, 110
    frags.append(line(x1, wall_y, x1, y_top, color=POS, sw=2, dash="4,3"))
    frags.append(line(x2, wall_y, x2, y_top, color=POS, sw=2, dash="4,3"))
    frags.append(line(x1, y_top, x2, y_top, color=POS, sw=2, dash="4,3"))

    frags.append(text(x1 - 40, (wall_y + y_top) / 2, "Вхід (x)", size=13, color=POS, bold=True))
    frags.append(text(x2 + 45, (wall_y + y_top) / 2, "Вихід (x+dx)", size=13, color=POS, bold=True))

    frags.append(textbox(280, y_top - 25, "Верхня межа y = h > δ(x)", size=12, pad=5, fill="#ffffff", stroke=POS)[0])

    frags.append(text(460, 225, "Межа шару y = δ(x)", size=12, color=NEG, bold=True))

    frags.append(arrow(100, 230, 165, 230, color=LINE, sw=2))
    frags.append(textbox(125, 200, "Вхідний потік імпульсу\n∫ ρ u² dy", size=11, pad=5, fill="#ffffff")[0])

    frags.append(arrow(575, 230, 640, 230, color=LINE, sw=2))
    frags.append(textbox(610, 200, "Вихідний потік імпульсу\n∫ ρ u² dy + d(...)", size=11, pad=5, fill="#ffffff")[0])

    frags.append(arrow(470, y_top - 35, 470, y_top + 15, color=FIELD, sw=2))
    frags.append(textbox(470, y_top - 50, "Масообмін v_h · ρ · dx", size=11, pad=5, fill="#eafaf1", stroke=FIELD)[0])

    frags.append(arrow(120, 295, 175, 295, color=POS, sw=2))
    frags.append(text(125, 280, "Сила тиску P·h", size=11, color=POS, bold=True))

    frags.append(arrow(610, 295, 565, 295, color=POS, sw=2))
    frags.append(text(620, 280, "Сила тиску (P+dP)·h", size=11, color=POS, bold=True))

    frags.append(arrow(420, wall_y, 340, wall_y, color=POS, sw=2.5))
    frags.append(textbox(380, wall_y + 35, "Тертя об стінку τ_w · dx", size=12, pad=6, fill="#fdecea", stroke=POS)[0])

    render(os.path.join(IMG_DIR, "control-volume.svg"), w, h, *frags)

def make_velocity_profile():
    w, h = 760, 380
    frags = []

    frags.append(text(w / 2, 25, "Профілі швидкості та товщини примежового шару", size=16, bold=True))

    panel_w = 210
    centers = [140, 380, 620]
    wy = 310

    # 1. Favorable gradient
    cx1 = centers[0]
    frags.append(fitbox(cx1 - panel_w / 2, 50, panel_w, 310, "", fill="#fdfefe", stroke=LINE, sw=1))
    frags.append(text(cx1, 75, "Прискорення (dP/dx < 0)", size=13, color=FIELD, bold=True))
    frags.append(text(cx1, 95, "Наповнений профіль (H ≈ 2.2)", size=11, color=MUTED))
    frags.append(line(cx1 - 70, wy, cx1 + 80, wy, color=LINE, sw=2))
    frags.append(line(cx1 - 60, wy, cx1 - 60, 120, color=LINE, sw=1.5))
    frags.append(line(cx1 + 50, wy, cx1 + 50, 120, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(cx1 + 50, 110, "U_e", size=12, color=MUTED, bold=True))
    pts1 = []
    for i in range(21):
        yn = i / 20.0
        u = (math.sin(yn * math.pi / 2) ** 0.5) * 110
        pts1.append("%.1f,%.1f" % (cx1 - 60 + u, wy - yn * 170))
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(pts1), FIELD))
    frags.append(text(cx1, 335, "Стійка течія без відриву", size=12, color=FIELD))

    # 2. Zero gradient
    cx2 = centers[1]
    frags.append(fitbox(cx2 - panel_w / 2, 50, panel_w, 310, "", fill="#fdfefe", stroke=LINE, sw=1))
    frags.append(text(cx2, 75, "Градієнт нульовий (dP/dx = 0)", size=13, color=NEG, bold=True))
    frags.append(text(cx2, 95, "Профіль Блазіуса (H = 2.59)", size=11, color=MUTED))
    frags.append(line(cx2 - 70, wy, cx2 + 80, wy, color=LINE, sw=2))
    frags.append(line(cx2 - 60, wy, cx2 - 60, 120, color=LINE, sw=1.5))
    frags.append(line(cx2 + 50, wy, cx2 + 50, 120, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(cx2 + 50, 110, "U_e", size=12, color=MUTED, bold=True))
    pts2 = []
    for i in range(21):
        yn = i / 20.0
        u = (1.5 * yn - 0.5 * (yn ** 3)) * 110
        pts2.append("%.1f,%.1f" % (cx2 - 60 + u, wy - yn * 170))
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(pts2), NEG))
    frags.append(text(cx2, 335, "Плоска пластина", size=12, color=NEG))

    # 3. Adverse gradient
    cx3 = centers[2]
    frags.append(fitbox(cx3 - panel_w / 2, 50, panel_w, 310, "", fill="#fdfefe", stroke=LINE, sw=1))
    frags.append(text(cx3, 75, "Гальмування (dP/dx > 0)", size=13, color=POS, bold=True))
    frags.append(text(cx3, 95, "Точка відриву (H ≈ 3.5)", size=11, color=POS, bold=True))
    frags.append(line(cx3 - 70, wy, cx3 + 80, wy, color=LINE, sw=2))
    frags.append(line(cx3 - 60, wy, cx3 - 60, 120, color=LINE, sw=1.5))
    frags.append(line(cx3 + 50, wy, cx3 + 50, 120, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(cx3 + 50, 110, "U_e", size=12, color=MUTED, bold=True))
    pts3 = []
    for i in range(21):
        yn = i / 20.0
        u = (2 * (yn ** 2) - (yn ** 3)) * 110
        pts3.append("%.1f,%.1f" % (cx3 - 60 + u, wy - yn * 170))
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(pts3), POS))
    frags.append(circle(cx3 - 60, wy, 5, fill=POS, stroke=POS))
    frags.append(textbox(cx3 + 15, wy - 30, "(∂u/∂y)|_w = 0\nτ_w = 0", size=11, pad=5, fill="#fdecea", stroke=POS)[0])
    frags.append(text(cx3, 335, "Зоровий орієнтир відриву", size=12, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "velocity-profile.svg"), w, h, *frags)

def make_shape_factor():
    w, h = 700, 380
    frags = []

    frags.append(text(w / 2, 25, "Параметри Полгаузена/Твейтса: коефіцієнт форми H та параметр тертя l", size=15, bold=True))

    ox, oy = 100, 300
    chart_w, chart_h = 520, 220

    frags.append(line(ox, oy, ox + chart_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - chart_h, color=LINE, sw=2))

    frags.append(text(ox + chart_w / 2, oy + 40, "Параметр градієнта тиску λ_T = (θ²/ν)·(dU_e/dx)", size=13, bold=True))
    frags.append(text(ox - 45, oy - chart_h / 2, "H(λ), l(λ)", size=13, bold=True))

    lambdas = [-0.09, -0.05, 0.0, 0.05, 0.08]
    for lam in lambdas:
        px = ox + (lam + 0.10) / 0.20 * chart_w
        frags.append(line(px, oy, px, oy - chart_h, color="#e5e7eb", sw=1, dash="2,2"))
        frags.append(text(px, oy + 18, "%.2f" % lam, size=11, color=MUTED))

    px0 = ox + 0.10 / 0.20 * chart_w
    frags.append(line(px0, oy, px0, oy - chart_h, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(text(px0, oy - chart_h + 15, "λ = 0 (ZPG, H=2.59)", size=11, color=NEG, bold=True))

    px_sep = ox + 0.01 / 0.20 * chart_w
    frags.append(line(px_sep, oy, px_sep, oy - chart_h, color=POS, sw=1.5, dash="4,3"))
    frags.append(textbox(px_sep + 65, oy - 140, "Точка відриву\nλ_T = -0.09\nH ≈ 3.55, l = 0", size=11, pad=5, fill="#fdecea", stroke=POS)[0])

    pts_h = []
    pts_l = []
    for i in range(41):
        lam = -0.09 + i * (0.17 / 40.0)
        px = ox + (lam + 0.10) / 0.20 * chart_w
        if lam < 0:
            H_val = 2.61 - 3.75 * lam + 80.0 * (lam ** 2)
            l_val = 0.225 + 2.3 * lam - 6.0 * (lam ** 2)
        else:
            H_val = 2.61 - 3.75 * lam + 15.0 * (lam ** 2)
            l_val = 0.225 + 2.3 * lam - 2.0 * (lam ** 2)

        py_h = oy - (H_val - 1.8) / 2.0 * chart_h
        py_l = oy - (max(0.0, l_val)) / 0.45 * chart_h

        pts_h.append("%.1f,%.1f" % (px, py_h))
        pts_l.append("%.1f,%.1f" % (px, py_l))

    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(pts_h), POS))
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(pts_l), NEG))

    frags.append(text(ox + 340, oy - 160, "Коефіцієнт форми H(λ_T)", size=12, color=POS, bold=True))
    frags.append(text(ox + 340, oy - 85, "Параметр тертя l(λ_T) = (θ/U_e)·(∂u/∂y)", size=12, color=NEG, bold=True))

    render(os.path.join(IMG_DIR, "shape-factor.svg"), w, h, *frags)

def make_thwaites_flow():
    w, h = 750, 320
    frags = []

    frags.append(text(w / 2, 25, "Алгоритм чисельного розв'язання за методом Твейтса", size=16, bold=True))

    step_w = 125
    step_h = 90
    y_box = 100

    boxes = [
        (70, "1. Вхідні дані", "Розподіл U_e(x)\nі в'язкість ν", "#f4f6f8", LINE),
        (215, "2. Квадратура", "θ²(x) = (0.45ν/U_e⁶)\n· ∫₀ˣ U_e⁵ dξ", "#eaf0fd", NEG),
        (360, "3. Градієнт", "λ_T(x) = \n(θ²/ν)·(dU_e/dx)", "#eaf0fd", NEG),
        (505, "4. Перевірка", "Якщо λ_T ≤ -0.09\n→ ВІДРИВ!", "#fdecea", POS),
        (650, "5. Вихідні дані", "Товщини θ, δ*\nі тертя C_f(x)", "#eafaf1", FIELD)
    ]

    for cx, btitle, bdesc, bfill, bstroke in boxes:
        frags.append(fitbox(cx - step_w / 2, y_box, step_w, step_h, btitle + "\n" + bdesc, size=11, fill=bfill, stroke=bstroke, sw=1.8))

    for i in range(4):
        x_from = boxes[i][0] + step_w / 2
        x_to = boxes[i + 1][0] - step_w / 2
        frags.append(arrow(x_from + 2, y_box + step_h / 2, x_to - 2, y_box + step_h / 2, color=LINE, sw=2))

    frags.append(arrow(505, y_box + step_h, 505, y_box + step_h + 45, color=POS, sw=2))
    frags.append(textbox(505, y_box + step_h + 65, "Фіксація координати x_sep\nі зупинка ламінарного розрахунку", size=11, pad=6, fill="#fdecea", stroke=POS)[0])

    render(os.path.join(IMG_DIR, "thwaites-flow.svg"), w, h, *frags)

if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)
    make_control_volume()
    make_velocity_profile()
    make_shape_factor()
    make_thwaites_flow()
    print("Generated 4 SVG figures successfully.")
