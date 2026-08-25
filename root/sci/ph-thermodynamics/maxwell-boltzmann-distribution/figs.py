# -*- coding: utf-8 -*-
"""Фігури для теми «Розподіл Максвелла — Больцмана за швидкостями та енергіями» 
(book/physics/thermodynamics/maxwell-boltzmann-distribution)."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
RED_F, RED_S = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S = "#f8fafc", "#475569"


def polyline(pts, color="#333333", sw=1.5, fill="none", dash=None):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (pts_str, fill, color, sw, d)


def maxwell_f(v, T, m=4.65e-26, kB=1.38e-23):
    """ Maxwell speed distribution function f(v) = 4 pi v^2 (m / (2 pi kB T))^(3/2) exp(- m v^2 / (2 kB T)) """
    if v < 0:
        return 0.0
    a = m / (2.0 * kB * T)
    norm = 4.0 * math.pi * math.pow(a / math.pi, 1.5)
    return norm * v * v * math.exp(-a * v * v)


def fig_maxwell_speed_distribution():
    """maxwell-speed-distribution.svg: Розподіл Максвелла за швидкостями для різних температур та характеристичні швидкості."""
    W, H = 880, 460
    frags = []

    # Фон кадру
    frags.append(rect(10, 10, 860, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Розподіл Максвелла за швидкостями та характеристичні швидкості", size=16, bold=True, color="#1e293b"))

    # Область графіка
    gx, gy, gw, gh = 80, 70, 750, 310
    frags.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))

    # Масштаби
    v_max = 1600.0  # м/с
    f_max = 0.0028  # 1/(м/с)

    def to_canvas(v, f):
        x = gx + (v / v_max) * gw
        y = (gy + gh) - (f / f_max) * gh
        return x, y

    # Сітка та подільки
    for v_val in range(200, 1600, 200):
        cx, _ = to_canvas(v_val, 0)
        frags.append(line(cx, gy, cx, gy + gh, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(text(cx, gy + gh + 18, "%d" % v_val, size=11, color="#475569"))

    for f_tick in [0.0005, 0.0010, 0.0015, 0.0020, 0.0025]:
        _, cy = to_canvas(0, f_tick)
        frags.append(line(gx, cy, gx + gw, cy, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(text(gx - 8, cy + 4, "%.1f" % (f_tick * 1000), size=11, anchor="end", color="#475569"))

    # Підписи осей
    frags.append(text(gx + gw / 2, gy + gh + 42, "Модуль швидкості v (м/с)", size=13, bold=True, color="#1e293b"))
    frags.append(text(24, gy + gh / 2, "Щільність f(v) (×10⁻³ с/м)", size=12, bold=True, color="#1e293b", anchor="middle"))

    # Криві для N2 при 300K, 600K, 1200K
    temps = [
        (300, BLUE_S, "T₁ = 300 K (холодний газ)"),
        (600, GREEN_S, "T₂ = 600 K"),
        (1200, AMBER_S, "T₃ = 1200 K (гарячий газ)")
    ]

    for T_val, color_val, label_text in temps:
        pts = []
        for step in range(0, 161):
            v_val = step * 10.0
            f_val = maxwell_f(v_val, T_val)
            cx, cy = to_canvas(v_val, f_val)
            pts.append((cx, cy))
        frags.append(polyline(pts, color=color_val, sw=2.5))

    # Легенда температур
    lx, ly = gx + gw - 240, gy + 15
    frags.append(rect(lx, ly, 230, 85, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(lx + 115, ly + 18, "Залежність від T (N₂)", size=11, bold=True, color="#1e293b"))
    for idx, (T_val, color_val, label_text) in enumerate(temps):
        frags.append(line(lx + 15, ly + 36 + idx * 20, lx + 45, ly + 36 + idx * 20, color=color_val, sw=2.5))
        frags.append(text(lx + 52, ly + 40 + idx * 20, label_text, size=11, anchor="start", color="#334155"))

    # Характеристичні швидкості для T = 300 K
    m_N2 = 4.65e-26
    kB = 1.38e-23
    T_ref = 300.0

    vp = math.sqrt(2.0 * kB * T_ref / m_N2)      # ~422 м/с
    vavg = math.sqrt(8.0 * kB * T_ref / (math.pi * m_N2)) # ~476 м/с
    vrms = math.sqrt(3.0 * kB * T_ref / m_N2)     # ~517 м/с

    xp, yp = to_canvas(vp, maxwell_f(vp, T_ref))
    xavg, yavg = to_canvas(vavg, maxwell_f(vavg, T_ref))
    xrms, yrms = to_canvas(vrms, maxwell_f(vrms, T_ref))

    # Пунктирні лінії до осі
    frags.append(line(xp, yp, xp, gy + gh, color=RED_S, sw=1.8, dash="4,3"))
    frags.append(line(xavg, yavg, xavg, gy + gh, color=PURPLE_S, sw=1.8, dash="4,3"))
    frags.append(line(xrms, yrms, xrms, gy + gh, color=GREEN_S, sw=1.8, dash="4,3"))

    # Точки на кривій 300K
    frags.append(circle(xp, yp, 5, fill=RED_S, stroke="#ffffff", sw=1.5))
    frags.append(circle(xavg, yavg, 5, fill=PURPLE_S, stroke="#ffffff", sw=1.5))
    frags.append(circle(xrms, yrms, 5, fill=GREEN_S, stroke="#ffffff", sw=1.5))

    # Пояснювальні виносні рамки вгорі
    frags.append(textbox(xp - 65, yp - 25, "v_p = √(2kT/m)\n422 м/с (пік)", size=10, pad=5, fill=RED_F, stroke=RED_S, color=RED_S, bold=True)[0])
    frags.append(textbox(xavg + 15, yavg - 45, "v_сер = √(8kT/πm)\n476 м/с", size=10, pad=5, fill=PURPLE_F, stroke=PURPLE_S, color=PURPLE_S, bold=True)[0])
    frags.append(textbox(xrms + 85, yrms - 15, "v_кв = √(3kT/m)\n517 м/с", size=10, pad=5, fill=GREEN_F, stroke=GREEN_S, color=GREEN_S, bold=True)[0])

    # Нижня узагальнююча виноска
    frags.append(text(440, H - 12, "Зростання температури розширює та виполажує криву, зміщуючи характеристичні швидкості вбік більших значень.", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "maxwell-speed-distribution.svg"), W, H, "".join(frags))


def fig_velocity_space_shell():
    """velocity-space-shell.svg: Сферичний шар 4πv² dv у просторі швидкостей та формування піку f(v)."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 32, "Формування розподілу Максвелла: геометричний фактор × множник Больцмана", size=15, bold=True, color="#1e293b"))

    # Ліва панель: 3D простір швидкостей зі сферичним шаром
    frags.append(rect(30, 55, 370, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(215, 78, "1. Простір швидкостей (v_x, v_y, v_z)", size=12, bold=True, color=BLUE_S))

    cx, cy = 200, 230
    # Осі v_x, v_y, v_z
    frags.append(line(cx, cy, cx + 130, cy, color="#64748b", sw=1.8))  # v_x
    frags.append(text(cx + 142, cy + 4, "v_x", size=11, bold=True, color="#334155"))

    frags.append(line(cx, cy, cx, cy - 130, color="#64748b", sw=1.8))  # v_z
    frags.append(text(cx, cy - 138, "v_z", size=11, bold=True, color="#334155"))

    frags.append(line(cx, cy, cx - 90, cy + 90, color="#64748b", sw=1.8))  # v_y
    frags.append(text(cx - 102, cy + 102, "v_y", size=11, bold=True, color="#334155"))

    # Внутрішня сфера v та зовнішній шар dv
    frags.append(circle(cx, cy, 70, fill=BLUE_F, stroke=BLUE_S, sw=1.5))
    frags.append(circle(cx, cy, 82, fill="none", stroke=BLUE_S, sw=1.2))

    # Еліпси перспективного 3D вигляду
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="70" ry="25" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="2,2"/>' % (cx, cy, BLUE_S))
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="82" ry="30" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="2,2"/>' % (cx, cy, BLUE_S))

    # Стрілка радіуса v та товщини dv
    frags.append(line(cx, cy, cx + 50, cy - 49, color=RED_S, sw=1.8))
    frags.append(circle(cx + 50, cy - 49, 3, fill=RED_S, stroke=RED_S, sw=1.0))
    frags.append(text(cx + 20, cy - 30, "v", size=11, bold=True, color=RED_S))

    frags.append(line(cx + 50, cy - 49, cx + 59, cy - 57, color=GREEN_S, sw=2.0))
    frags.append(text(cx + 64, cy - 62, "dv", size=11, bold=True, color=GREEN_S))

    # Текстове пояснення під графіком
    frags.append(textbox(215, 355, "Об'єм сферичного шару: d³v = 4π v² dv\nСтатистична вага зростає як ~ v²", size=11, pad=6, fill=BLUE_F, stroke=BLUE_S, color="#1e3a8a")[0])

    # Права панель: Перемноження факторів та підсумковий пік
    frags.append(rect(430, 55, 380, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(620, 78, "2. Комбінація факторів у f(v)", size=12, bold=True, color=PURPLE_S))

    # Маленькі схематичні графіки
    # Графік 1: v^2 (зростання)
    px1, py1, pw1, ph1 = 460, 100, 150, 80
    frags.append(rect(px1, py1, pw1, ph1, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(line(px1 + 10, py1 + ph1 - 10, px1 + pw1 - 10, py1 + ph1 - 10, color="#64748b", sw=1.2))
    frags.append(line(px1 + 10, py1 + ph1 - 10, px1 + 10, py1 + 10, color="#64748b", sw=1.2))
    # Парабола
    parab_pts = [(px1 + 10 + i, py1 + ph1 - 10 - (i / 130.0)**2 * 60) for i in range(131)]
    frags.append(polyline(parab_pts, color=BLUE_S, sw=2.0))
    frags.append(text(px1 + 75, py1 + 22, "Геометрія: ~ v²", size=10, bold=True, color=BLUE_S))

    # Знак множення
    frags.append(text(625, 140, "×", size=20, bold=True, color="#475569"))

    # Графік 2: exp(-mv^2/2kT) (згасання)
    px2, py2, pw2, ph2 = 640, 100, 150, 80
    frags.append(rect(px2, py2, pw2, ph2, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(line(px2 + 10, py2 + ph2 - 10, px2 + pw2 - 10, py2 + ph2 - 10, color="#64748b", sw=1.2))
    frags.append(line(px2 + 10, py2 + ph2 - 10, px2 + 10, py2 + 10, color="#64748b", sw=1.2))
    # Експонента
    exp_pts = [(px2 + 10 + i, py2 + 10 + (1.0 - math.exp(-i / 35.0)) * 60) for i in range(131)]
    frags.append(polyline(exp_pts, color=RED_S, sw=2.0))
    frags.append(text(px2 + 75, py2 + 22, "Больцман: ~ e⁻ᶜᵛ²", size=10, bold=True, color=RED_S))

    # Стрілка вниз (= Підсумковий кривий розподіл)
    frags.append(line(620, 195, 620, 220, color="#475569", sw=2.0))
    frags.append(text(635, 212, "=", size=18, bold=True, color="#1e293b"))

    # Графік 3: Результуючий розподіл Максвелла з піком
    px3, py3, pw3, ph3 = 480, 230, 280, 110
    frags.append(rect(px3, py3, pw3, ph3, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(line(px3 + 15, py3 + ph3 - 15, px3 + pw3 - 15, py3 + ph3 - 15, color="#475569", sw=1.5))
    frags.append(line(px3 + 15, py3 + ph3 - 15, px3 + 15, py3 + 15, color="#475569", sw=1.5))

    res_pts = []
    for i in range(251):
        v_norm = i / 60.0
        f_norm = (v_norm ** 2) * math.exp(-v_norm ** 2)
        cx_r = px3 + 15 + i
        cy_r = (py3 + ph3 - 15) - (f_norm / 0.3679) * 75
        res_pts.append((cx_r, cy_r))

    frags.append(polyline(res_pts, color=PURPLE_S, sw=2.5))
    frags.append(text(px3 + 140, py3 + 25, "Підсумковий розподіл f(v)", size=11, bold=True, color=PURPLE_S))
    frags.append(circle(px3 + 15 + 60, (py3 + ph3 - 15) - 75, 4, fill=PURPLE_S, stroke="#ffffff", sw=1.2))
    frags.append(text(px3 + 15 + 60, (py3 + ph3 - 15) - 82, "Пік (v_p)", size=10, bold=True, color=PURPLE_S))

    frags.append(text(420, H - 12, "Сферичний об'єм у просторі швидкостей росте як v², тоді як больцманівська ймовірність спадає як e⁻ᵐᵛ²/²ᵏᵀ.", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "velocity-space-shell.svg"), W, H, "".join(frags))


if __name__ == "__main__":
    fig_maxwell_speed_distribution()
    fig_velocity_space_shell()
    print("SVGs successfully generated!")
