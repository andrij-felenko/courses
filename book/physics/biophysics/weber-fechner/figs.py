# -*- coding: utf-8 -*-
import sys
import os
import math

# Four levels up to reach scripts/ from book/physics/biophysics/weber-fechner/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig1_weber_fraction():
    """Малюнок 1: Поріг розрізнення (JND) та пропорційність Вебера."""
    w, h = 760, 420
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(380, 35, "Закон Вебера: ΔI / I = k_W (поріг розрізнення пропорційний стимулу)", size=14, bold=True, fill="#eef2f7", stroke=LINE)
    out.append(tb)

    out.append(rect(40, 75, 320, 310, fill=FILL, stroke=LINE, rx=8))
    out.append(text(200, 105, "Малий початковий стимул (I₁ = 100 г)", size=13, bold=True, color=INK))

    out.append(rect(140, 135, 120, 90, fill="#d9e2ec", stroke=LINE, rx=4))
    out.append(text(200, 185, "Базова вага I₁", size=13, bold=True, color=INK))

    out.append(rect(160, 240, 80, 40, fill="#f8d7da", stroke=POS, rx=4))
    out.append(text(200, 265, "ΔI₁ = 2 г", size=13, bold=True, color=POS))

    tb1, _, _ = textbox(200, 335, "Відношення: ΔI₁ / I₁ = 2 / 100 = 0.02 (2%)", size=11.5, fill="#ffffff", stroke=MUTED)
    out.append(tb1)

    out.append(rect(400, 75, 320, 310, fill=FILL, stroke=LINE, rx=8))
    out.append(text(560, 105, "Великий початковий стимул (I₂ = 1000 г)", size=13, bold=True, color=INK))

    out.append(rect(480, 135, 160, 90, fill="#bccadc", stroke=LINE, rx=4))
    out.append(text(560, 185, "Базова вага I₂", size=13, bold=True, color=INK))

    out.append(rect(510, 240, 100, 40, fill="#f8d7da", stroke=POS, rx=4))
    out.append(text(560, 265, "ΔI₂ = 20 г", size=13, bold=True, color=POS))

    tb2, _, _ = textbox(560, 335, "Відношення: ΔI₂ / I₂ = 20 / 1000 = 0.02 (2%)", size=11.5, fill="#ffffff", stroke=MUTED)
    out.append(tb2)

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'weber-fraction-jnd.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))


def fig2_log_vs_linear():
    """Малюнок 2: Порівняння лінійної та логарифмічної шкали відчуття."""
    w, h = 760, 440
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(380, 30, "Стиснення динамічного діапазону: S = k · ln(I / I₀)", size=14, bold=True, fill="#eef2f7", stroke=LINE)
    out.append(tb)

    ox, oy = 110, 360
    ax_w, ax_h = 600, 280

    out.append(arrow(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    out.append(arrow(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    out.append(text(ox + ax_w - 10, oy + 25, "Інтенсивність стимулу (I / I₀)", size=12, bold=True, color=INK, anchor="end"))
    out.append(text(ox + 15, oy - ax_h + 15, "Суб'єктивне відчуття (S)", size=12, bold=True, color=INK, anchor="start"))

    for val, x_off in [(1, 0), (20, 110), (40, 220), (60, 330), (80, 440), (100, 550)]:
        xp = ox + x_off
        out.append(line(xp, oy, xp, oy + 5, color=LINE, sw=1.5))
        out.append(text(xp, oy + 20, str(val), size=11, color=MUTED))
        if x_off > 0:
            out.append(line(xp, oy, xp, oy - ax_h + 20, color="#e5e7eb", sw=1, dash="4,4"))

    lin_pts = []
    for x_val in range(1, 101, 2):
        xp = ox + (x_val - 1) * (550 / 99)
        yp = oy - (x_val - 1) * (240 / 35)
        if yp < oy - ax_h + 20:
            yp = oy - ax_h + 20
        lin_pts.append(f"{xp:.1f},{yp:.1f}")

    out.append(f'<polyline points="{" ".join(lin_pts)}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6,4"/>')

    log_pts = []
    k_scale = 240 / math.log(100)
    for x_val in range(1, 101, 1):
        xp = ox + (x_val - 1) * (550 / 99)
        yp = oy - math.log(x_val) * k_scale
        log_pts.append(f"{xp:.1f},{yp:.1f}")

    out.append(f'<polyline points="{" ".join(log_pts)}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    out.append(rect(430, 80, 260, 85, fill="#ffffff", stroke=LINE, rx=6))
    out.append(line(445, 105, 475, 105, color=POS, sw=2.5, dash="6,4"))
    out.append(text(485, 109, "Лінійна шкала (перевантаження)", size=11, color=INK, anchor="start", bold=True))

    out.append(line(445, 138, 475, 138, color=NEG, sw=3))
    out.append(text(485, 142, "Логарифм (Вебера–Фехнера)", size=11, color=INK, anchor="start", bold=True))

    out.append(circle(ox, oy, 4, fill=NEG, stroke=LINE))
    out.append(text(ox + 10, oy - 10, "Поріг чутливості I₀", size=11, color=NEG, anchor="start", bold=True))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'log-vs-linear-response.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))


def fig3_stevens_vs_fechner():
    """Малюнок 3: Степенний закон Стівенса S = k · Iⁿ проти закону Фехнера."""
    w, h = 760, 440
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    tb, _, _ = textbox(380, 30, "Закон Стівенса S = k · Iⁿ для різних модальностей відчуттів", size=14, bold=True, fill="#eef2f7", stroke=LINE)
    out.append(tb)

    ox, oy = 110, 360
    ax_w, ax_h = 600, 280

    out.append(arrow(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    out.append(arrow(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    out.append(text(ox + ax_w - 10, oy + 25, "Інтенсивність стимулу (I)", size=12, bold=True, color=INK, anchor="end"))
    out.append(text(ox + 15, oy - ax_h + 15, "Відчуття (S)", size=12, bold=True, color=INK, anchor="start"))

    pts_pain = []
    for i in range(0, 101, 2):
        xp = ox + i * 5.5
        norm_i = i / 100.0
        yp = oy - (norm_i ** 2.5) * 230
        pts_pain.append(f"{xp:.1f},{yp:.1f}")
    out.append(f'<polyline points="{" ".join(pts_pain)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    pts_len = []
    for i in range(0, 101, 2):
        xp = ox + i * 5.5
        norm_i = i / 100.0
        yp = oy - norm_i * 230
        pts_len.append(f"{xp:.1f},{yp:.1f}")
    out.append(f'<polyline points="{" ".join(pts_len)}" fill="none" stroke="{FIELD}" stroke-width="2" stroke-dasharray="5,5"/>')

    pts_bright = []
    for i in range(0, 101, 2):
        xp = ox + i * 5.5
        norm_i = i / 100.0
        yp = oy - (norm_i ** 0.5) * 230
        pts_bright.append(f"{xp:.1f},{yp:.1f}")
    out.append(f'<polyline points="{" ".join(pts_bright)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    out.append(rect(140, 70, 310, 115, fill="#ffffff", stroke=LINE, rx=6))
    out.append(line(155, 95, 185, 95, color=POS, sw=2.5))
    out.append(text(195, 99, "Електричний струм / Біль (n > 1)", size=11, color=INK, anchor="start", bold=True))

    out.append(line(155, 127, 185, 127, color=FIELD, sw=2, dash="5,5"))
    out.append(text(195, 131, "Видима довжина відрізка (n = 1)", size=11, color=INK, anchor="start", bold=True))

    out.append(line(155, 159, 185, 159, color=NEG, sw=2.5))
    out.append(text(195, 163, "Яскравість світла / Гучність (n < 1)", size=11, color=INK, anchor="start", bold=True))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'stevens-vs-fechner.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    fig1_weber_fraction()
    fig2_log_vs_linear()
    fig3_stevens_vs_fechner()
    print("SVG figures generated successfully in img/")
