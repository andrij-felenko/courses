# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: parallelogram ───────────────────────────────────────────────────
# Площа паралелограма як основа |a| × висота |b|·sin θ — майбутня довжина a×b.
# a (червоний) уздовж осі x; b (синій) під кутом; висота — перпендикуляр від
# кінця b на лінію a (зелений); паралелограм добудований пунктиром.

def fig_parallelogram():
    W, H = 860, 440
    parts = []

    ox, oy = 110, 340          # спільний початок

    # Вектор a — уздовж осі x (основа)
    La = 420
    aex, aey = ox + La, oy

    # Вектор b — під кутом theta до a
    theta = math.radians(38)
    Lb = 270
    bex = ox + Lb * math.cos(theta)
    bey = oy - Lb * math.sin(theta)

    # Четверта вершина паралелограма C = a + b
    cx = aex + (bex - ox)
    cy = aey + (bey - oy)

    # Основа висоти: проєкція кінця b на лінію a
    px = ox + Lb * math.cos(theta)
    py = oy

    # --- заливка паралелограма (легка зелена) ---
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="#eafaf1" stroke="none"/>'
                 % (ox, oy, aex, aey, cx, cy, bex, bey))

    # --- дві пунктирні сторони паралелограма ---
    parts.append(line(aex, aey, cx, cy, color=MUTED, sw=1.3, dash="6,4"))
    parts.append(line(bex, bey, cx, cy, color=MUTED, sw=1.3, dash="6,4"))

    # --- висота: перпендикуляр від кінця b на лінію a (зелений) ---
    parts.append(line(bex, bey, px, py, color=FIELD, sw=2.6))
    # значок прямого кута біля основи висоти
    sq = 12
    parts.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="none" stroke="%s" stroke-width="1.3"/>'
                 % (px - sq, py, px - sq, py - sq, px, py - sq, MUTED))

    # --- вектор a (червоний) ---
    parts.append(arrow(ox, oy, aex, aey, color=POS, sw=2.8))
    parts.append(text(ox + La / 2, oy + 26, "a  (основа)", size=15, color=POS, bold=True, anchor="middle"))

    # --- вектор b (синій) ---
    parts.append(arrow(ox, oy, bex, bey, color=NEG, sw=2.8))
    parts.append(text(ox + (bex - ox) / 2 - 26, oy - (oy - bey) / 2 - 6, "b", size=17, color=NEG, bold=True, anchor="middle"))

    # --- кут theta (дуга між a і b) ---
    arc_r = 56
    sx, sy = ox + arc_r, oy
    aax = ox + arc_r * math.cos(theta)
    aay = oy - arc_r * math.sin(theta)
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (sx, sy, arc_r, arc_r, aax, aay, INK))
    parts.append(text(ox + arc_r + 14, oy - 16, "θ", size=16, color=INK, italic=True))

    # --- підпис висоти ---
    parts.append(text(px + 86, (bey + py) / 2, "висота = |b|·sin θ", size=13, color=FIELD, bold=True, anchor="middle"))

    # --- формула площі в рамці ---
    bx_c, by_c = 660, 90
    bbox, bw, bh = textbox(bx_c, by_c, "S = |a| · |b| · sin θ",
                           size=15, bold=True, fill="#fef9ec", stroke="#c8a000", sw=1.8, pad=14)
    parts.append(bbox)
    parts.append(text(bx_c, by_c + bh / 2 + 20, "площа паралелограма = |a × b|",
                      size=12, color=MUTED, anchor="middle"))

    # --- точки й мітка початку ---
    parts.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=0))
    parts.append(text(ox - 14, oy + 18, "O", size=14, color=INK))
    parts.append(circle(aex, aey, 4.5, fill=POS, stroke=POS, sw=0))
    parts.append(circle(bex, bey, 4.5, fill=NEG, stroke=NEG, sw=0))
    parts.append(circle(cx, cy, 4.5, fill=MUTED, stroke=MUTED, sw=0))

    # --- заголовок ---
    parts.append(text(W / 2, 30, "Площа паралелограма = основа × висота",
                      size=16, bold=True))

    render(os.path.join(OUT, "parallelogram.svg"), W, H, *parts)


# ── Фігура 2: right-hand (нормаль за правилом правої руки) ─────────────────────
# Площинка, задана a і b; поворот від a до b (дуга зі стрілкою) виштовхує
# нормаль a×b вгору. Поряд — протилежна нормаль b×a (вниз, пунктир).

def fig_right_hand():
    W, H = 760, 460
    parts = []

    cx, cy = 300, 290          # центр площинки

    # Площинка зображена ромбом (паралелограм у перспективі)
    # вектори a, b у плані площинки
    ax, ay = 175, 48           # a — вправо-вниз (перспектива)
    bx, by = 40, -70           # b — вправо-вгору

    Ax, Ay = cx + ax, cy + ay
    Bx, By = cx + bx, cy + by
    Cx, Cy = cx + ax + bx, cy + ay + by

    # --- заливка площинки ---
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="#eef2f7" stroke="%s" stroke-width="1.2"/>'
                 % (cx, cy, Ax, Ay, Cx, Cy, Bx, By, MUTED))

    # --- нормаль вгору: a × b (зелена, товста) ---
    nlen = 150
    parts.append(arrow(cx, cy, cx, cy - nlen, color=FIELD, sw=3.2))
    parts.append(text(cx + 16, cy - nlen + 4, "a × b", size=16, color=FIELD, bold=True, anchor="start"))
    parts.append(text(cx + 16, cy - nlen + 24, "(нормаль угору)", size=12, color=MUTED, anchor="start"))

    # --- нормаль вниз: b × a (пунктир, сіра) ---
    parts.append(line(cx, cy, cx, cy + 96, color=MUTED, sw=2.0, dash="6,5"))
    parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.0"/>'
                 % (cx - 6, cy + 88, cx, cy + 98, cx + 6, cy + 88, MUTED))
    parts.append(text(cx + 14, cy + 92, "b × a", size=14, color=MUTED, anchor="start"))

    # --- вектори a і b у площинці ---
    parts.append(arrow(cx, cy, Ax, Ay, color=POS, sw=2.8))
    parts.append(text(Ax + 12, Ay + 6, "a", size=17, color=POS, bold=True, anchor="start"))
    parts.append(arrow(cx, cy, Bx, By, color=NEG, sw=2.8))
    parts.append(text(Bx - 16, By - 4, "b", size=17, color=NEG, bold=True, anchor="end"))

    # --- дуга повороту a → b зі стрілкою (показує напрям обходу) ---
    r = 60
    a0 = math.atan2(-(ay), ax)      # кут a (екранні коорд., y вниз → інвертуємо)
    a1 = math.atan2(-(by), bx)      # кут b
    p0 = (cx + r * math.cos(a0), cy - r * math.sin(a0))
    p1 = (cx + r * math.cos(a1), cy - r * math.sin(a1))
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
                 % (p0[0], p0[1], r, r, p1[0], p1[1], INK))
    parts.append(text(cx + 4, cy - r - 6, "поворот a→b", size=12, color=INK, anchor="middle"))

    # --- центральна точка ---
    parts.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=0))

    # --- пояснювальна рамка праворуч ---
    bx_c, by_c = 600, 250
    box = fitbox(bx_c - 130, by_c - 70, 260, 140,
                 "Пальці правої руки —\nвід a до b.\n"
                 "Великий палець —\nнапрям a × b.\n\n"
                 "Зміна порядку →\nкрутиш у інший бік →\nнормаль протилежна.",
                 size=13, fill="#fafafa", stroke=MUTED, sw=1.2, color=INK)
    parts.append(box)

    # --- заголовок ---
    parts.append(text(W / 2, 30, "Напрям a × b за правилом правої руки",
                      size=16, bold=True))

    render(os.path.join(OUT, "right-hand.svg"), W, H, *parts)


fig_parallelogram()
fig_right_hand()
print("SVG figures generated in", OUT)
