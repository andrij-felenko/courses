# -*- coding: utf-8 -*-
import sys
import os
import math

# Add scripts directory to path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, circle, text, mtext,
    FILL, LINE, INK, MUTED, POS, NEG, FIELD, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def generate_bifurcation_tree():
    """Малюнок 1: Каскад подвоєння періоду та біфуркаційне дерево."""
    w, h = 820, 500
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Біфуркаційне дерево та каскад подвоєння періоду", size=18, bold=True))

    # Вісі координат
    x0, y0 = 90, 420
    x_len, y_len = 680, 340
    frags.append(line(x0, y0, x0 + x_len, y0, color=LINE, sw=2))
    frags.append(arrow(x0, y0, x0 + x_len + 15, y0, color=LINE, sw=2))
    frags.append(line(x0, y0, x0, y0 - y_len, color=LINE, sw=2))
    frags.append(arrow(x0, y0, x0, y0 - y_len - 15, color=LINE, sw=2))

    frags.append(text(x0 + x_len + 25, y0 + 5, "r", size=15, bold=True))
    frags.append(text(x0 - 15, y0 - y_len - 15, "x*", size=15, bold=True))

    # Шкала параметрів r (від 2.8 до 4.0)
    def r_to_x(r):
        return x0 + (r - 2.8) / (4.0 - 2.8) * x_len

    def x_val_to_y(v):
        return y0 - v * y_len

    # Позначки на осі r
    r_ticks = [
        (2.8, "2.8"),
        (3.0, "r₁=3.0"),
        (3.449, "r₂=3.45"),
        (3.544, "r₃=3.54"),
        (3.570, "r_∞=3.57"),
        (3.828, "r=3.83"),
        (4.0, "4.0")
    ]
    for r_val, label in r_ticks:
        rx = r_to_x(r_val)
        frags.append(line(rx, y0 - 4, rx, y0 + 4, color=MUTED, sw=1.5))
        frags.append(text(rx, y0 + 22, label, size=11, color=INK))

    # Позначки на осі x
    for val in [0.0, 0.5, 1.0]:
        ry = x_val_to_y(val)
        frags.append(line(x0 - 4, ry, x0 + 4, ry, color=MUTED, sw=1.5))
        frags.append(text(x0 - 25, ry + 4, "%.1f" % val, size=12, color=INK))

    # Зона 1: r in [2.8, 3.0] -> 1 непорушна точка x* = 1 - 1/r
    pts_1 = []
    for i in range(30):
        r = 2.8 + i * (3.0 - 2.8) / 29.0
        x = 1.0 - 1.0 / r
        pts_1.append((r_to_x(r), x_val_to_y(x)))
    for i in range(len(pts_1) - 1):
        frags.append(line(pts_1[i][0], pts_1[i][1], pts_1[i+1][0], pts_1[i+1][1], color=NEG, sw=2.5))

    # Зона 2: r in [3.0, 3.449] -> 2 гілки 2-циклу
    pts_2a, pts_2b = [], []
    for i in range(40):
        r = 3.0 + i * (3.449 - 3.0) / 39.0
        disc = math.sqrt(max(0, (r + 1) * (r - 3)))
        x_a = (r + 1 + disc) / (2 * r)
        x_b = (r + 1 - disc) / (2 * r)
        pts_2a.append((r_to_x(r), x_val_to_y(x_a)))
        pts_2b.append((r_to_x(r), x_val_to_y(x_b)))
    for i in range(len(pts_2a) - 1):
        frags.append(line(pts_2a[i][0], pts_2a[i][1], pts_2a[i+1][0], pts_2a[i+1][1], color=NEG, sw=2))
        frags.append(line(pts_2b[i][0], pts_2b[i][1], pts_2b[i+1][0], pts_2b[i+1][1], color=NEG, sw=2))

    # Зона 3: r in [3.449, 3.544] -> 4-цикл
    pts_4 = [[], [], [], []]
    for i in range(30):
        r = 3.449 + i * (3.544 - 3.449) / 29.0
        x = 0.5
        for _ in range(200):
            x = r * x * (1 - x)
        orb = []
        for _ in range(4):
            x = r * x * (1 - x)
            orb.append(x)
        orb.sort()
        for idx in range(4):
            pts_4[idx].append((r_to_x(r), x_val_to_y(orb[idx])))
    for branch in pts_4:
        for i in range(len(branch) - 1):
            frags.append(line(branch[i][0], branch[i][1], branch[i+1][0], branch[i+1][1], color=NEG, sw=1.8))

    # Зона 4: r in [3.544, 3.570] -> 8, 16, 32-цикли
    for i in range(40):
        r = 3.544 + i * (3.570 - 3.544) / 39.0
        x = 0.5
        for _ in range(300):
            x = r * x * (1 - x)
        for _ in range(16):
            x = r * x * (1 - x)
            frags.append(circle(r_to_x(r), x_val_to_y(x), 1.0, fill=NEG, stroke=NEG, sw=0.5))

    # Зона 5: r > 3.570 -> Хаос та вікно періоду 3
    rx_inf = r_to_x(3.570)
    frags.append(line(rx_inf, y0 - y_len, rx_inf, y0, color=POS, sw=1.8, dash="4,4"))
    frags.append(text(rx_inf + 5, y0 - y_len + 15, "r_∞ = 3.5699...", size=12, color=POS, anchor="start", bold=True))

    for i in range(120):
        r = 3.570 + i * (4.0 - 3.570) / 119.0
        if 3.825 <= r <= 3.855:
            x = 0.5
            for _ in range(400):
                x = r * x * (1 - x)
            for _ in range(3):
                x = r * x * (1 - x)
                frags.append(circle(r_to_x(r), x_val_to_y(x), 1.1, fill=FIELD, stroke=FIELD, sw=0.5))
        else:
            x = 0.5
            for _ in range(300):
                x = r * x * (1 - x)
            for _ in range(24):
                x = r * x * (1 - x)
                frags.append(circle(r_to_x(r), x_val_to_y(x), 0.8, fill=INK, stroke=INK, sw=0.2))

    # Інформаційні блоки
    b1, _, _ = textbox(210, 100, "1-цикл\n(стійка точка)", size=12, fill="#eaf0fd", stroke=NEG)
    frags.append(b1)

    b2, _, _ = textbox(360, 90, "2-цикл\nr₁ = 3.0", size=12, fill="#eaf0fd", stroke=NEG)
    frags.append(b2)

    b3, _, _ = textbox(480, 80, "4-цикл\nr₂ = 3.45", size=12, fill="#eaf0fd", stroke=NEG)
    frags.append(b3)

    b4, _, _ = textbox(600, 110, "Хаотична область\n(r > r_∞)", size=12, fill="#fdecea", stroke=POS)
    frags.append(b4)

    b5, _, _ = textbox(720, 240, "Вікно періоду 3\n(r ≈ 3.83)", size=11, fill="#eafaf1", stroke=FIELD)
    frags.append(b5)

    render(os.path.join(IMG_DIR, "bifurcation-tree.svg"), w, h, *frags)

def generate_feigenbaum_scaling():
    """Малюнок 2: Геометричне масштабування та виміри d_k, d_{k+1} константи alpha."""
    w, h = 780, 440
    frags = []

    frags.append(text(w / 2, 26, "Геометричне масштабування орбіт та константа α", size=18, bold=True))

    cx = 390
    frags.append(line(cx, 60, cx, 390, color=MUTED, sw=1.5, dash="5,5"))
    frags.append(text(cx, 50, "x = 1/2 (екстремум)", size=12, color=MUTED, anchor="middle"))

    levels = [
        (120, "r₁ = 3.000", "2-цикл"),
        (220, "r₂ = 3.449", "4-цикл"),
        (320, "r₃ = 3.544", "8-цикл")
    ]

    for y_lev, label, sub in levels:
        frags.append(line(80, y_lev, 700, y_lev, color=LINE, sw=1.2))
        frags.append(text(120, y_lev - 12, label, size=13, bold=True, anchor="start"))
        frags.append(text(120, y_lev + 16, sub, size=11, color=MUTED, anchor="start"))

    y1 = 120
    d1 = 160
    frags.append(circle(cx, y1, 5, fill=POS, stroke=POS))
    frags.append(circle(cx + d1, y1, 5, fill=NEG, stroke=NEG))
    frags.append(line(cx, y1 + 20, cx + d1, y1 + 20, color=POS, sw=2))
    frags.append(line(cx, y1 + 15, cx, y1 + 25, color=POS, sw=1.5))
    frags.append(line(cx + d1, y1 + 15, cx + d1, y1 + 25, color=POS, sw=1.5))
    frags.append(text(cx + d1 / 2, y1 + 38, "d₁", size=14, bold=True, color=POS))

    y2 = 220
    d2 = -64
    frags.append(circle(cx, y2, 5, fill=POS, stroke=POS))
    frags.append(circle(cx + d2, y2, 5, fill=NEG, stroke=NEG))
    frags.append(circle(cx + d1, y2, 4, fill=MUTED, stroke=MUTED))
    frags.append(line(cx, y2 + 20, cx + d2, y2 + 20, color=POS, sw=2))
    frags.append(line(cx, y2 + 15, cx, y2 + 25, color=POS, sw=1.5))
    frags.append(line(cx + d2, y2 + 15, cx + d2, y2 + 25, color=POS, sw=1.5))
    frags.append(text(cx + d2 / 2, y2 + 38, "d₂ = -d₁/α", size=13, bold=True, color=POS))

    y3 = 320
    d3 = 25.5
    frags.append(circle(cx, y3, 5, fill=POS, stroke=POS))
    frags.append(circle(cx + d3, y3, 5, fill=NEG, stroke=NEG))
    frags.append(line(cx, y3 + 20, cx + d3, y3 + 20, color=POS, sw=2))
    frags.append(line(cx, y3 + 15, cx, y3 + 25, color=POS, sw=1.5))
    frags.append(line(cx + d3, y3 + 15, cx + d3, y3 + 25, color=POS, sw=1.5))
    frags.append(text(cx + d3 / 2 + 18, y3 + 38, "d₃ = d₂/(-α)", size=12, bold=True, color=POS))

    box_alpha, _, _ = textbox(570, 220, "Універсальний масштаб маштабування:\nα = lim (d_k / d_{k+1}) = -2.5029078...\n\nЗнак «мінус» означає інверсію\nположення орбіти відносно x = 1/2", size=12, fill="#f4f6f8", stroke=LINE)
    frags.append(box_alpha)

    render(os.path.join(IMG_DIR, "feigenbaum-scaling.svg"), w, h, *frags)

def generate_renormalization_operator():
    """Малюнок 3: Оператор ренормалізації Твіса — Фейгенбаума — Каданова."""
    w, h = 800, 440
    frags = []

    frags.append(text(w / 2, 26, "Оператор ренормалізації T в функціональному просторі", size=18, bold=True))

    b_in, w_in, _ = textbox(160, 160, "Вхідне відображення f(x)\nз квадратичним максимумом\nв точці x = 0", size=13, fill="#eaf0fd", stroke=NEG)
    frags.append(b_in)

    frags.append(arrow(260, 160, 350, 160, color=LINE, sw=2))
    frags.append(text(305, 140, "1. Подвійна ітерація", size=11, bold=True, color=INK))
    frags.append(text(305, 180, "f(f(x))", size=12, italic=True, color=MUTED))

    b_mid, _, _ = textbox(440, 160, "Друга ітерація f⁽²⁾(x)\nМає 4 локальні екстремуми\nпоблизу центра", size=13, fill="#fef9e7", stroke="#f39c12")
    frags.append(b_mid)

    frags.append(arrow(530, 160, 620, 160, color=LINE, sw=2))
    frags.append(text(575, 140, "2. Масштабування -α", size=11, bold=True, color=INK))
    frags.append(text(575, 180, "x ↦ x / (-α)", size=12, italic=True, color=MUTED))

    b_out, _, _ = textbox(700, 160, "Ренормалізоване\nвідображення T f(x)\n= -α·f(f(x / -α))", size=13, fill="#eafaf1", stroke=FIELD)
    frags.append(b_out)

    frags.append(line(80, 260, 720, 260, color=MUTED, sw=1, dash="4,4"))

    box_g, _, _ = textbox(400, 340, "Універсальна непорушна функція g(x) = T g(x):\n\ng(x) = -α · g( g( x / -α ) )\n\nСпектр лінеаризованого оператора L = dT|_g містить єдине нестійке власне значення:\nλ₁ = δ = 4.6692016...", size=13, fill="#f4f6f8", stroke=LINE)
    frags.append(box_g)

    render(os.path.join(IMG_DIR, "renormalization-operator.svg"), w, h, *frags)

def generate_lyapunov_spectrum():
    """Малюнок 4: Спектр показника Ляпунова lambda(r) в залежності від r."""
    w, h = 800, 420
    frags = []

    frags.append(text(w / 2, 26, "Залежність показника Ляпунова λ(r) від параметра r", size=18, bold=True))

    x0, y0 = 90, 240
    x_len, y_len = 660, 150

    frags.append(line(x0, y0, x0 + x_len, y0, color=POS, sw=1.8, dash="4,4"))
    frags.append(text(x0 + x_len + 15, y0 + 4, "λ = 0", size=13, bold=True, color=POS))

    frags.append(line(x0, y0 + y_len, x0 + x_len, y0 + y_len, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0 + y_len, x0 + x_len + 15, y0 + y_len, color=LINE, sw=1.5))
    frags.append(line(x0, y0 + y_len, x0, y0 - y_len - 10, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0 + y_len, x0, y0 - y_len - 25, color=LINE, sw=1.5))

    frags.append(text(x0 + x_len + 25, y0 + y_len + 4, "r", size=14, bold=True))
    frags.append(text(x0 - 20, y0 - y_len - 20, "λ(r)", size=14, bold=True))

    def r_to_px(r):
        return x0 + (r - 2.8) / (4.0 - 2.8) * x_len

    def lyap_to_py(lyap):
        return y0 - (lyap / 1.0) * 110

    pts = []
    for i in range(160):
        r = 2.8 + i * (3.5699 - 2.8) / 159.0
        x = 0.5
        for _ in range(150):
            x = r * x * (1 - x)
        l_val = 0.0
        for _ in range(150):
            x = r * x * (1 - x)
            deriv = abs(r * (1 - 2 * x))
            if deriv > 1e-12:
                l_val += math.log(deriv)
            else:
                l_val += -10.0
        l_val /= 150.0
        l_val = max(-1.2, l_val)
        pts.append((r_to_px(r), lyap_to_py(l_val)))

    for i in range(len(pts) - 1):
        frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=1.8))

    pts_chaos = []
    for i in range(200):
        r = 3.570 + i * (4.0 - 3.570) / 199.0
        x = 0.5
        for _ in range(200):
            x = r * x * (1 - x)
        l_val = 0.0
        for _ in range(200):
            x = r * x * (1 - x)
            deriv = abs(r * (1 - 2 * x))
            if deriv > 1e-12:
                l_val += math.log(deriv)
            else:
                l_val += -10.0
        l_val /= 200.0
        l_val = max(-1.2, min(0.7, l_val))
        pts_chaos.append((r_to_px(r), lyap_to_py(l_val)))

    for i in range(len(pts_chaos) - 1):
        col = FIELD if pts_chaos[i][1] > y0 else NEG
        frags.append(line(pts_chaos[i][0], pts_chaos[i][1], pts_chaos[i+1][0], pts_chaos[i+1][1], color=col, sw=1.5))

    frags.append(text(r_to_px(3.2), y0 + 60, "Періодичні режими (λ < 0)", size=12, color=NEG, bold=True))
    frags.append(text(r_to_px(3.75), y0 - 50, "Хаотичний режим (λ > 0)", size=12, color=FIELD, bold=True))

    b_inf, _, _ = textbox(r_to_px(3.570), y0 + 110, "Точка накопичення r_∞\nλ = 0 (межа хаосу)", size=11, fill="#fdecea", stroke=POS)
    frags.append(b_inf)

    render(os.path.join(IMG_DIR, "lyapunov-spectrum.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_bifurcation_tree()
    generate_feigenbaum_scaling()
    generate_renormalization_operator()
    generate_lyapunov_spectrum()
    print("Figures generated successfully.")
