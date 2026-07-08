# -*- coding: utf-8 -*-
"""Фігури для статті Videx 14500. Запуск: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_construction():
    """Розріз циліндра: сталевий стакан, згорнутий рулет електродів, два виводи."""
    W, H = 760, 400
    frags = []
    # корпус (сталевий стакан), горизонтальний циліндр
    body_x, body_y, body_w, body_h = 150, 120, 430, 150
    frags.append(rect(body_x, body_y, body_w, body_h, fill="#e9edf1", stroke=LINE, sw=2, rx=14))

    # мінус — плаский торець зліва
    frags.append(rect(body_x - 14, body_y + 30, 14, body_h - 60, fill="#cfd6dd", stroke=LINE, sw=2, rx=3))
    b1, w1, h1 = textbox(body_x - 70, body_y + body_h/2, "−\nплаский\nторець", size=13, color=NEG, bold=True)
    frags.append(b1)

    # плюс — виступ-ковпачок справа
    cap_x = body_x + body_w
    frags.append(rect(cap_x, body_y + body_h/2 - 26, 16, 52, fill="#cfd6dd", stroke=LINE, sw=2, rx=3))
    frags.append(rect(cap_x + 16, body_y + body_h/2 - 12, 12, 24, fill="#d8dee5", stroke=LINE, sw=2, rx=3))
    b2, w2, h2 = textbox(cap_x + 96, body_y + body_h/2, "+\nковпачок\n(button top)", size=13, color=POS, bold=True)
    frags.append(b2)

    # згорнутий рулет — концентричні дуги-спіраль усередині
    cx, cy = body_x + body_w/2, body_y + body_h/2
    layers = [
        (58, POS,   2.4),   # катод
        (48, MUTED, 1.6),   # сепаратор
        (38, NEG,   2.4),   # анод
        (28, MUTED, 1.6),
        (18, POS,   2.4),
    ]
    for r, col, sw in layers:
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="%.1f"/>'
                     % (cx, cy, r, r*0.92, col, sw))

    # легенда шарів рулету — один стовпчик, кожен рядок на своєму y (без накладань)
    lx, ly = 150, 316
    frags.append(text(lx, ly, "Рулет («jelly-roll») — три довгі стрічки, згорнуті в спіраль:", size=13, anchor="start", color=INK))
    rows = [(POS,   "катод — LiCoO₂ на алюмінієвій фользі"),
            (NEG,   "анод — графіт на мідній фользі"),
            (MUTED, "сепаратор + рідкий електроліт між ними")]
    for i, (col, lab) in enumerate(rows):
        yy = ly + 24 + i * 22
        frags.append(line(lx+4, yy-4, lx+34, yy-4, color=col, sw=3))
        frags.append(text(lx+44, yy, lab, size=12, anchor="start", color=INK))

    # розмір
    frags.append(line(body_x, 96, body_x + body_w, 96, color=MUTED, sw=1.2))
    frags.append(line(body_x, 90, body_x, 102, color=MUTED, sw=1.2))
    frags.append(line(body_x+body_w, 90, body_x+body_w, 102, color=MUTED, sw=1.2))
    frags.append(text(cx, 90, "≈ 50 мм (як AA)", size=12, color=MUTED))
    # діаметр — вертикальний виносок унизу-праворуч, у порожньому полі під циліндром
    dxv = body_x + body_w - 40
    dyb = body_y + body_h + 26
    frags.append(line(dxv, dyb, dxv, dyb + 30, color=MUTED, sw=1.2))
    frags.append(line(dxv - 24, dyb, dxv - 24, dyb + 30, color=MUTED, sw=1.2))
    frags.append(line(dxv - 24, dyb + 15, dxv, dyb + 15, color=MUTED, sw=1.2))
    frags.append(text(dxv + 8, dyb + 20, "⌀14 мм", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'construction.svg'), W, H, *frags,
           title="Що всередині 14500: сталевий стакан і згорнутий рулет електродів")


def fig_curve():
    """Крива напруга–заряд: плато 3.7 В, стеля 4.2 В, поріг 3.0/2.5 В."""
    W, H = 760, 440
    frags = []
    # осі
    ox, oy = 110, 360          # початок координат (лівий нижній)
    ax_w, ax_h = 560, 280
    top = oy - ax_h
    frags.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))       # X
    frags.append(line(ox, oy, ox, top, color=INK, sw=2))             # Y
    frags.append(text(ox + ax_w/2, oy + 46, "віддано / прийнято ємності  →  (0 … 800 мА·год)", size=13, color=INK))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">напруга на виводах, В</text>'
                 % (30, (oy+top)/2, FONT, INK, 30, (oy+top)/2))

    # відображення напруги 2.4..4.3 В у Y
    vmin, vmax = 2.4, 4.3
    def vy(v): return oy - (v - vmin) / (vmax - vmin) * ax_h
    def qx(f): return ox + f * ax_w   # f: 0..1 частка розряду

    # горизонтальні орієнтири
    for v, lab, col in [(4.2, "4.2 В — стеля заряду", POS),
                        (3.7, "3.7 В — номінал (плато)", INK),
                        (3.0, "3.0 В — розумний поріг стоп", NEG),
                        (2.5, "2.5 В — абсолютний мінімум", MUTED)]:
        y = vy(v)
        frags.append(line(ox, y, ox + ax_w, y, color=col, sw=1.0, dash="4,5"))
        frags.append(text(ox + ax_w + 6, y + 4, lab, size=11, color=col, anchor="start"))

    # крива розряду: швидкий спад 4.2->3.8, довге плато ~3.7, обвал у кінці
    pts = [(0.00, 4.15), (0.05, 3.95), (0.12, 3.85), (0.30, 3.75),
           (0.55, 3.68), (0.75, 3.60), (0.88, 3.45), (0.95, 3.20), (1.00, 2.80)]
    d = "M %.1f %.1f " % (qx(pts[0][0]), vy(pts[0][1]))
    for f, v in pts[1:]:
        d += "L %.1f %.1f " % (qx(f), vy(v))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # підпис кривої біля плато
    frags.append(text(qx(0.42), vy(3.75) - 12, "розряд", size=13, color=POS, bold=True))

    # виноска: порівняння з 1.5 В (лужна AA) — у порожньому кутку графіка
    b, w, h = textbox(qx(0.28), vy(4.05),
                      "Лужна AA живе на 1.5 В —\nу 2.5 раза нижче цього плато.\nОт чому вона не взаємозамінна.",
                      size=12, color=INK, fill="#fff7ec", stroke=MUTED)
    frags.append(b)

    render(os.path.join(IMG, 'voltage-curve.svg'), W, H, *frags,
           title="Напруга 14500 від заряду: плато біля 3.7 В, стеля 4.2, поріг 3.0")


if __name__ == '__main__':
    fig_construction()
    fig_curve()
    print("OK figures written to", IMG)
