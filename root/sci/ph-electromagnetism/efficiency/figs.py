# -*- coding: utf-8 -*-
"""Фігури до теми «Коефіцієнт корисної дії».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#6b7280"


def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts_str, color, sw, d))


def render_svg(filename, width, height, elements):
    """Компонує елементи у повноцінний SVG із макером стрілки."""
    svg_defs = """<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />
  </marker>
</defs>""" % LINE
    content = '\n'.join(elements)
    full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{svg_defs}
{content}
</svg>"""
    filepath = os.path.join(IMG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print(f"Записано {filepath}")


# ── Фігура 1: Потік енергії та структура втрат у системі ─────────────────────
def fig_energy_balance():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, "Баланс потужності: підведена енергія, корисна робота та втрати", size=15, bold=True, color=COLOR_DARK))

    # Вхідний блок (Джерело)
    f.append(fitbox(30, 130, 160, 90, "Підведена\nпотужність P_in\n(100% енергії)", size=13, fill="#eef2ff", stroke=COLOR_BLUE, sw=2, bold=True))

    # Центральний блок (Перетворювач / Машина)
    f.append(fitbox(270, 120, 210, 110, "Електромагнітний\nперетворювач\n(машина / трансформатор)", size=13, fill="#f0fdf4", stroke=COLOR_GREEN, sw=2, bold=True))

    # Вихідний блок (Корисне навантаження)
    f.append(fitbox(560, 130, 170, 90, "Корисна потужність\nP_out = η · P_in\n(корисна робота)", size=13, fill="#f0fdf4", stroke=COLOR_GREEN, sw=2, bold=True))

    # Стрілка від входу до машини
    f.append(arrow(190, 175, 270, 175, color=COLOR_BLUE, sw=2.5))

    # Стрілка від машини до виходу
    f.append(arrow(480, 175, 560, 175, color=COLOR_GREEN, sw=2.5))

    # Гілка втрат (донизу)
    f.append(line(375, 230, 375, 275, color=COLOR_RED, sw=2.5))
    f.append(arrow(375, 275, 375, 305, color=COLOR_RED, sw=2.5))

    # Блок втрат
    f.append(fitbox(220, 305, 310, 95, "Потужність втрат P_loss = P_in - P_out\n• Джоулеві втрати в міді (I²R)\n• Магнітні втрати в сталі (гістерезис, вихрові струми)\n• Механічні та додаткові втрати", size=11, fill="#fef2f2", stroke=COLOR_RED, sw=1.8, bold=False))

    render_svg("fig1-energy-balance.svg", W, H, f)


# ── Фігура 2: Залежність ККД та потужності від опору навантаження (Якобі) ────
def fig_efficiency_vs_power_transfer():
    W, H = 760, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, "Корисна потужність та ККД кола: теорема Якобі проти високого ККД", size=15, bold=True, color=COLOR_DARK))

    ox, oy = 80, 360
    gw, gh = 620, 250

    # Сітка (лише в межах графіка)
    for y_val in range(oy - 250, oy, 50):
        f.append(line(ox, y_val, ox + gw, y_val, color="#e2e8f0", sw=1, dash="4,4"))
    for x_val in range(ox + 100, ox + gw, 100):
        f.append(line(x_val, oy - gh, x_val, oy, color="#e2e8f0", sw=1, dash="4,4"))

    # Вісь X та Y
    f.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))

    # Позначки Y
    f.append(text(ox - 30, oy - 250, "100%", size=11, bold=True, color=INK))
    f.append(text(ox - 30, oy - 125, "50%", size=11, bold=True, color=INK))
    f.append(text(ox - 30, oy, "0%", size=11, bold=True, color=INK))

    # Позначки X (R_L / r)
    scale_x = 100  # 1 unit = 100px
    f.append(text(ox + scale_x, oy + 22, "1.0 (R_L = r)", size=11, bold=True, color=INK))
    f.append(text(ox + 3 * scale_x, oy + 22, "3.0", size=11, color=COLOR_GRAY))
    f.append(text(ox + 5 * scale_x, oy + 22, "5.0 (R_L >> r)", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(ox + gw - 40, oy + 38, "Відносини опорів (R_L / r)", size=12, bold=True, color=INK))

    # Вертикальна лінія узгодження R_L = r (x = ox + scale_x)
    match_x = ox + scale_x
    f.append(line(match_x, oy, match_x, oy - gh, color=COLOR_RED, sw=1.5, dash="6,4"))

    # Крива ККД η(x) = x / (1 + x)
    pts_eta = []
    for step in range(0, 600, 5):
        x_val = step / 100.0
        eta = x_val / (1.0 + x_val)
        px = ox + x_val * scale_x
        py = oy - eta * 250
        pts_eta.append((px, py))
    f.append(polyline(pts_eta, color=COLOR_GREEN, sw=3))

    # Крива Корисної Потужності P(x) = 4*x / (1+x)^2
    pts_p = []
    for step in range(0, 600, 5):
        x_val = step / 100.0
        p_ratio = (4.0 * x_val) / ((1.0 + x_val) ** 2)
        px = ox + x_val * scale_x
        py = oy - p_ratio * 250
        pts_p.append((px, py))
    f.append(polyline(pts_p, color=COLOR_RED, sw=2.5, dash="6,3"))

    # Точка узгодження (50% ККД, 100% P_max)
    f.append(circle(match_x, oy - 125, 5, fill=COLOR_RED, stroke=COLOR_DARK, sw=1.5))

    # Легенди та інформаційні блоки розміщуємо у верхньому полі (y=40..90) вище сітки
    f.append(fitbox(80, 42, 230, 48, "— — Корисна потужність P_L (макс. при R_L = r)\n—— ККД η = R_L / (R_L + r)", size=10, fill="#ffffff", stroke=COLOR_GRAY, sw=1))

    f.append(fitbox(320, 42, 210, 48, "Точка Якобі (R_L = r):\nP = P_max, але ККД η = 50%", size=10, fill="#fff1f2", stroke=COLOR_RED, sw=1.5, bold=True))

    f.append(fitbox(540, 42, 175, 48, "Область енергомереж:\nR_L >> r, ККД η > 90%", size=10, fill="#f0fdf4", stroke=COLOR_GREEN, sw=1.5, bold=True))

    render_svg("fig2-efficiency-vs-power-transfer.svg", W, H, f)


# ── Фігура 3: Крива ККД та втрат трансформатора від навантаження k ───────────
def fig_transformer_efficiency_curve():
    W, H = 760, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, "Залежність ККД та втрат трансформатора від коефіцієнта навантаження k", size=15, bold=True, color=COLOR_DARK))

    ox, oy = 80, 360
    gw, gh = 620, 250

    # Сітка
    for y_val in range(oy - 250, oy, 50):
        f.append(line(ox, y_val, ox + gw, y_val, color="#e2e8f0", sw=1, dash="4,4"))
    for x_val in range(ox + 100, ox + gw, 100):
        f.append(line(x_val, oy - gh, x_val, oy, color="#e2e8f0", sw=1, dash="4,4"))

    # Вісь X та Y
    f.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))

    # Позначки Y
    f.append(text(ox - 30, oy - 250, "100%", size=11, bold=True, color=INK))
    f.append(text(ox - 30, oy - 125, "50%", size=11, bold=True, color=INK))
    f.append(text(ox - 30, oy, "0%", size=11, bold=True, color=INK))

    # Позначки X (k = S / S_n)
    scale_k = 400  # k=1.0 at 400px
    f.append(text(ox + int(0.7 * scale_k), oy + 22, "k_opt ≈ 0.7", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(ox + scale_k, oy + 22, "1.0 (Номінал)", size=11, bold=True, color=INK))
    f.append(text(ox + gw - 40, oy + 38, "Навантаження k = S / S_n", size=12, bold=True, color=INK))

    # Втрати в сталі (постійні P_0)
    p0_y = oy - 30
    f.append(line(ox, p0_y, ox + gw, p0_y, color=COLOR_PURPLE, sw=2, dash="6,3"))

    # Втрати в міді (змінні P_Cu = k^2 * P_sc)
    pts_pcu = []
    for step in range(0, 500, 5):
        k_val = step / 350.0
        pcu = (k_val ** 2) * 0.04 * 250 / 0.1
        px = ox + k_val * scale_k
        py = oy - min(pcu, gh)
        pts_pcu.append((px, py))
    f.append(polyline(pts_pcu, color=COLOR_ORANGE, sw=2, dash="4,2"))

    # Крива ККД η(k)
    pts_eta_trans = []
    k_opt = math.sqrt(0.015 / 0.03)
    max_eta_y = 0
    opt_px = ox + k_opt * scale_k

    for step in range(2, 500, 3):
        k_val = step / 350.0
        if k_val > 1.35:
            break
        p_out = k_val * 1.0 * 0.9
        p_loss = 0.015 + (k_val ** 2) * 0.03
        eta = p_out / (p_out + p_loss)
        px = ox + k_val * scale_k
        py = oy - eta * 250
        pts_eta_trans.append((px, py))
        if abs(k_val - k_opt) < 0.01:
            max_eta_y = py

    f.append(polyline(pts_eta_trans, color=COLOR_GREEN, sw=3))

    # Пунктир на k_opt
    f.append(line(opt_px, oy, opt_px, max_eta_y + 10, color=COLOR_GREEN, sw=1.5, dash="4,4"))
    f.append(circle(opt_px, max_eta_y, 5, fill=COLOR_GREEN, stroke=COLOR_DARK, sw=1.5))

    # Блоки над сіткою у верхній зоні (y=40..90)
    f.append(fitbox(80, 42, 250, 48, "Максимум ККД (η_max ≈ 98%):\nРівність втрат P_0 = k²·P_sc (k_opt ≈ 0.7)", size=10, fill="#f0fdf4", stroke=COLOR_GREEN, sw=1.5, bold=True))

    f.append(fitbox(340, 42, 175, 48, "Постійні втрати P_0\n(магнітне перемагнічування)", size=10, fill="#faf5ff", stroke=COLOR_PURPLE, sw=1.2))

    f.append(fitbox(525, 42, 185, 48, "Змінні втрати P_Cu = k²·P_sc\n(джоулеве нагрівання обмоток)", size=10, fill="#fff7ed", stroke=COLOR_ORANGE, sw=1.2))

    render_svg("fig3-transformer-efficiency-curve.svg", W, H, f)


if __name__ == '__main__':
    fig_energy_balance()
    fig_efficiency_vs_power_transfer()
    fig_transformer_efficiency_curve()
    print("Усі фігури успішно згенеровано!")
