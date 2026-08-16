# -*- coding: utf-8 -*-
"""
Generator script for speed of sound figures.
Uses svgkit from scripts directory.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: speed-of-sound-media.svg
# -----------------------------------------------------------------------------
def gen_speed_of_sound_media():
    path = os.path.join(IMG_DIR, 'speed-of-sound-media.svg')
    w, h = 800, 360
    frags = []

    # Title
    frags.append(text(w / 2, 24, "Порівняння швидкості звуку в різних агрегатних станах речовини", size=15, bold=True))

    media = [
        {"name": "Гази (Повітря, 20°C)", "c": "343 м/с", "desc": "Слабка пружність стиску\nρ = 1.2 кг/м³\nМала жорсткість зв'язків", "color": "#e0f2fe", "border": NEG, "x": 50},
        {"name": "Рідини (Вода, 20°C)", "c": "1482 м/с", "desc": "Високий модуль стиску K\nρ = 998 кг/м³\nВільне зміщення молекул", "color": "#dbeafe", "border": "#2563eb", "x": 235},
        {"name": "Тверді тіла (Сталь)", "c_L": "5960 м/с", "c_S": "3230 м/с", "desc": "Сильний кристалічний зв'язок\nПоздовжні c_L та поперечні c_S\nЖорсткі пружини ґратки", "color": "#f1f5f9", "border": INK, "x": 420},
        {"name": "Кристали (Алмаз)", "c": "12 000+ м/с", "desc": "Екстремальна жорсткість K, G\nНизька атомарна маса C\nНайвища швидкість звуку", "color": "#fef3c7", "border": "#d97706", "x": 605}
    ]

    card_w = 150
    card_h = 240
    y0 = 60

    for m in media:
        x = m["x"]
        frags.append(rect(x, y0, card_w, card_h, fill=m["color"], stroke=m["border"], sw=1.8, rx=6))
        frags.append(text(x + card_w / 2, y0 + 25, m["name"], size=12, bold=True))
        frags.append(line(x + 10, y0 + 38, x + card_w - 10, y0 + 38, color=m["border"], sw=1))

        # Speed highlights
        if "c" in m:
            frags.append(text(x + card_w / 2, y0 + 68, m["c"], size=18, color=POS, bold=True))
        else:
            frags.append(text(x + card_w / 2, y0 + 60, "c_L = " + m["c_L"], size=13, color=POS, bold=True))
            frags.append(text(x + card_w / 2, y0 + 80, "c_S = " + m["c_S"], size=12, color=NEG, bold=True))

        # Spring-mass visual representation inside card
        cy = y0 + 125
        if m["name"].startswith("Гази"):
            # Scattered dots with weak dashed lines
            for px, py in [(x + 35, cy - 15), (x + 110, cy - 20), (x + 70, cy + 15), (x + 120, cy + 10)]:
                frags.append(circle(px, py, 4, fill=NEG, stroke=INK, sw=1))
        elif m["name"].startswith("Рідини"):
            # Packed circles touching
            for px, py in [(x + 40, cy - 10), (x + 70, cy - 10), (x + 100, cy - 10), (x + 55, cy + 15), (x + 85, cy + 15)]:
                frags.append(circle(px, py, 7, fill=NEG, stroke=INK, sw=1))
        elif m["name"].startswith("Тверді"):
            # Rigid lattice with springs
            pts = [(x + 40, cy - 15), (x + 110, cy - 15), (x + 40, cy + 15), (x + 110, cy + 15)]
            frags.append(line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=INK, sw=2))
            frags.append(line(pts[2][0], pts[2][1], pts[3][0], pts[3][1], color=INK, sw=2))
            frags.append(line(pts[0][0], pts[0][1], pts[2][0], pts[2][1], color=INK, sw=2))
            frags.append(line(pts[1][0], pts[1][1], pts[3][0], pts[3][1], color=INK, sw=2))
            for px, py in pts:
                frags.append(circle(px, py, 6, fill=FIELD, stroke=INK, sw=1))
        else:
            # Ultra dense crystal lattice
            pts = [(x + 40, cy - 15), (x + 75, cy - 15), (x + 110, cy - 15), (x + 40, cy + 15), (x + 75, cy + 15), (x + 110, cy + 15)]
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    if math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) < 45:
                        frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color=POS, sw=2))
            for px, py in pts:
                frags.append(circle(px, py, 5, fill="#f59e0b", stroke=INK, sw=1))

        # Description
        lines = m["desc"].split("\n")
        for idx, ln in enumerate(lines):
            frags.append(text(x + card_w / 2, y0 + 175 + idx * 17, ln, size=10, color=MUTED))

    # General formula box at bottom
    f_box, _, _ = textbox(w / 2, 325, "Фундаментальна формула: c = √( K / ρ )  [в рідинах/газах]    |    c_L = √( (K + 4/3·G) / ρ )  [в твердих тілах]", size=12, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    frags.append(f_box)

    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 2: thermodynamic-process.svg
# -----------------------------------------------------------------------------
def gen_thermodynamic_process():
    path = os.path.join(IMG_DIR, 'thermodynamic-process.svg')
    w, h = 780, 340
    frags = []

    frags.append(text(w / 2, 22, "Термодинаміка звукового стиску: Ізотерма Ньютона проти Адіабати Лапласа", size=15, bold=True))

    # Left diagram: Isothermal model
    x1, y1, bw, bh = 40, 55, 330, 220
    frags.append(rect(x1, y1, bw, bh, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x1 + bw / 2, y1 + 22, "Модель Ньютона (1687) — Ізотермічна", size=13, bold=True, color=POS))
    frags.append(text(x1 + bw / 2, y1 + 42, "Припущення: тепло встигає розсіюватися (T = const)", size=10, color=MUTED))

    frags.append(rect(x1 + 30, y1 + 65, 270, 45, fill=BG, stroke=LINE, sw=1, rx=4))
    frags.append(text(x1 + 165, y1 + 84, "dp / dρ = P / ρ  ⇒  c = √( P / ρ )", size=12, bold=True))
    frags.append(text(x1 + 165, y1 + 100, "Для повітря (0°C): c = 280 м/с  (помилка −16%)", size=11, color=POS, bold=True))

    frags.append(text(x1 + 165, y1 + 130, "Причина похибки:", size=11, bold=True))
    frags.append(text(x1 + 165, y1 + 150, "Частота звуку надто висока для теплопровідності.", size=10))
    frags.append(text(x1 + 165, y1 + 168, "Зони стиску не встигають охолонути,", size=10))
    frags.append(text(x1 + 165, y1 + 186, "а зони розрідження — нагрітися.", size=10))

    # Right diagram: Adiabatic model
    x2 = 410
    frags.append(rect(x2, y1, bw, bh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(x2 + bw / 2, y1 + 22, "Модель Лапласа (1816) — Адіабатична", size=13, bold=True, color=FIELD))
    frags.append(text(x2 + bw / 2, y1 + 42, "Реальність: теплообмін відсутній (dQ = 0, P·V^γ = const)", size=10, color=MUTED))

    frags.append(rect(x2 + 30, y1 + 65, 270, 45, fill=BG, stroke=LINE, sw=1, rx=4))
    frags.append(text(x2 + 165, y1 + 84, "dp / dρ = γ·P / ρ  ⇒  c = √( γ·P / ρ )", size=12, bold=True))
    frags.append(text(x2 + 165, y1 + 100, "Для повітря (0°C, γ=1.40): c = 331.3 м/с  (збіг 100%)", size=11, color=FIELD, bold=True))

    frags.append(text(x2 + 165, y1 + 130, "Фізичний механізм:", size=11, bold=True))
    frags.append(text(x2 + 165, y1 + 150, "Адіабатичний стиск підвищує температуру T,", size=10))
    frags.append(text(x2 + 165, y1 + 168, "що створює ДОДАТКОВИЙ пружний тиск.", size=10))
    frags.append(text(x2 + 165, y1 + 186, "Поправка Лапласа: √γ ≈ √1.40 ≈ 1.183 (+18%)", size=10, bold=True))

    # Bottom comparison summary
    s_box, _, _ = textbox(w / 2, 305, "Показник адіабати γ = Cp / Cv: для двоатомних газів (N₂, O₂) γ = 7/5 = 1.40, для одноатомних (He, Ar) γ = 5/3 = 1.67", size=11, fill="#f8fafc", stroke=MUTED, sw=1)
    frags.append(s_box)

    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 3: temperature-humidity-effect.svg
# -----------------------------------------------------------------------------
def gen_temperature_humidity_effect():
    path = os.path.join(IMG_DIR, 'temperature-humidity-effect.svg')
    w, h = 780, 350
    frags = []

    frags.append(text(w / 2, 22, "Залежність швидкості звуку в повітрі від температури та вологості", size=15, bold=True))

    # Chart box
    cx, cy, cw, ch = 80, 50, 430, 220
    frags.append(rect(cx, cy, cw, ch, fill="#fafafa", stroke=LINE, sw=1.2, rx=4))

    # Axes
    frags.append(line(cx + 30, cy + ch - 30, cx + cw - 20, cy + ch - 30, color=LINE, sw=1.5))
    frags.append(line(cx + 30, cy + ch - 30, cx + 30, cy + 20, color=LINE, sw=1.5))

    frags.append(text(cx + cw - 15, cy + ch - 15, "t (°C)", size=11))
    frags.append(text(cx + 15, cy + 15, "c (м/с)", size=11))

    # Temperature ticks (-40 to +50 °C)
    t_vals = [-40, -20, 0, 20, 40]
    for t_val in t_vals:
        px = cx + 30 + (t_val + 40) / 90.0 * (cw - 60)
        frags.append(line(px, cy + ch - 30, px, cy + ch - 25, color=LINE, sw=1))
        frags.append(text(px, cy + ch - 12, str(t_val), size=10))

    # Speed ticks (300 to 360 m/s)
    c_vals = [300, 320, 340, 360]
    for c_val in c_vals:
        py = cy + ch - 30 - (c_val - 300) / 60.0 * (ch - 50)
        frags.append(line(cx + 25, py, cx + 30, py, color=LINE, sw=1))
        frags.append(text(cx + 18, py + 4, str(c_val), size=10, anchor="end"))
        frags.append(line(cx + 30, py, cx + cw - 20, py, color="#e5e7eb", sw=1, dash="3,3"))

    # Plot Dry air c(t) = 331.3 * sqrt(1 + t/273.15)
    pts_dry = []
    pts_wet = []
    for step in range(50):
        t_val = -40 + step * (90 / 49)
        c_dry = 331.3 * math.sqrt(1 + t_val / 273.15)
        # Wet air is slightly faster due to lower density of H2O (M=18 vs M=29)
        # delta_c ~ 0.35% at 20C 100% RH
        wet_factor = 1.0 + 0.005 * math.exp(t_val / 25.0) if t_val > -10 else 1.0
        c_wet = c_dry * wet_factor

        px = cx + 30 + (t_val + 40) / 90.0 * (cw - 60)
        py_dry = cy + ch - 30 - (c_dry - 300) / 60.0 * (ch - 50)
        py_wet = cy + ch - 30 - (c_wet - 300) / 60.0 * (ch - 50)

        pts_dry.append("%.1f,%.1f" % (px, py_dry))
        pts_wet.append("%.1f,%.1f" % (px, py_wet))

    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_dry), NEG))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="5,3"/>' % (" ".join(pts_wet), POS))

    # Right side explanation panel
    rx = 530
    frags.append(rect(rx, cy, 230, ch, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(rx + 115, cy + 22, "Фізичні закономірності", size=12, bold=True))

    frags.append(line(rx + 15, cy + 35, rx + 45, cy + 35, color=NEG, sw=2.5))
    frags.append(text(rx + 52, cy + 39, "Сухе повітря (RH = 0%)", size=10, anchor="start", bold=True))

    frags.append(line(rx + 15, cy + 55, rx + 45, cy + 55, color=POS, sw=2, dash="5,3"))
    frags.append(text(rx + 52, cy + 59, "Вологе повітря (RH = 100%)", size=10, anchor="start", bold=True))

    frags.append(text(rx + 115, cy + 90, "1. Температура T:", size=11, bold=True))
    frags.append(text(rx + 115, cy + 108, "c ∝ √T (в Кельвінах)", size=10))
    frags.append(text(rx + 115, cy + 124, "Приблизно: c ≈ 331.3 + 0.606·t", size=10, color=NEG, bold=True))

    frags.append(text(rx + 115, cy + 155, "2. Молекулярна маса M:", size=11, bold=True))
    frags.append(text(rx + 115, cy + 173, "Водяна пара (H₂O: M=18)", size=10))
    frags.append(text(rx + 115, cy + 189, "легша за сухе повітря (M=29).", size=10))
    frags.append(text(rx + 115, cy + 205, "Вологе повітря менш густе!", size=10, color=POS, bold=True))

    # Formula at bottom
    b_box, _, _ = textbox(w / 2, 310, "Спрощена інженерна формула для повітря: c(t) ≈ 331.3 + 0.606 · t [°C]  (похибка < 0.2% в межах від -20°C до +40°C)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    frags.append(b_box)

    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 4: wave-speed-dispersion.svg
# -----------------------------------------------------------------------------
def gen_wave_speed_dispersion():
    path = os.path.join(IMG_DIR, 'wave-speed-dispersion.svg')
    w, h = 780, 320
    frags = []

    frags.append(text(w / 2, 22, "Дисперсія хвилі: відмінність фазової (vp) та групової (vg) швидкостей", size=15, bold=True))

    # Non-dispersive wave (Left)
    x1, y1, bw, bh = 40, 55, 330, 210
    frags.append(rect(x1, y1, bw, bh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(x1 + bw / 2, y1 + 22, "Недисперсійне середовище (Повітря)", size=12, bold=True, color=FIELD))
    frags.append(text(x1 + bw / 2, y1 + 40, "vp = vg = c = const (не залежить від частоти)", size=10, color=MUTED))

    # Wavepacket non-dispersive
    pw1 = []
    for i in range(120):
        px = x1 + 20 + i * 2.4
        env = math.exp(-((i - 60) / 25.0) ** 2)
        py = y1 + 115 - 35 * env * math.sin(i * 0.3)
        pw1.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pw1), FIELD))
    frags.append(arrow(x1 + 100, y1 + 170, x1 + 220, y1 + 170, color=FIELD, sw=2))
    frags.append(text(x1 + 160, y1 + 190, "Пакет зберігає форму при поширенні", size=10, bold=True))

    # Dispersive wave (Right)
    x2 = 410
    frags.append(rect(x2, y1, bw, bh, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x2 + bw / 2, y1 + 22, "Дисперсійне середовище (Пластини / Релаксація)", size=12, bold=True, color=POS))
    frags.append(text(x2 + bw / 2, y1 + 40, "vp(ω) ≠ vg(ω) — високі частоти біжать швидше/повільніше", size=10, color=MUTED))

    # Wavepacket dispersive (distorted)
    pw2 = []
    for i in range(120):
        px = x2 + 20 + i * 2.4
        env = math.exp(-((i - 60) / 35.0) ** 2)
        # Chirp / frequency change along packet
        py = y1 + 115 - 35 * env * math.sin(i * 0.15 + (i / 30.0) ** 2)
        pw2.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pw2), POS))
    frags.append(arrow(x2 + 100, y1 + 170, x2 + 220, y1 + 170, color=POS, sw=2))
    frags.append(text(x2 + 160, y1 + 190, "Імпульс розпливається та спотворюється", size=10, bold=True))

    # Bottom summary box
    d_box, _, _ = textbox(w / 2, 290, "Фазова швидкість vp = ω/k — швидкість окремої горбини. Групова швидкість vg = dω/dk — швидкість огинаючої (енергії та сигналу).", size=11, fill="#f8fafc", stroke=MUTED, sw=1)
    frags.append(d_box)

    render(path, w, h, *frags)


if __name__ == '__main__':
    gen_speed_of_sound_media()
    gen_thermodynamic_process()
    gen_temperature_humidity_effect()
    gen_wave_speed_dispersion()
    print("All figures generated successfully.")
