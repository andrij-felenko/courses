# -*- coding: utf-8 -*-
"""Фігури до теми «Поляризаційне різноманіття».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

WAVE1 = "#c0392b"     # Канал 1 (+45°)
WAVE2 = "#2457d6"     # Канал 2 (-45°)
GOOD  = FIELD         # Зелений (виграш, MRC)
ACCENT = "#8e44ad"

# ── 1. Просторове проти Поляризаційного різноманіття ─────────────────────────
def fig_spatial_vs_polarization():
    W, H = 740, 360
    f = [text(W / 2, 25, "Просторове проти поляризаційного різноманіття", size=16, bold=True)]

    # Ліва панель: Просторове різноманіття (Spatial Diversity)
    xL = 190
    y_top = 70
    f.append(rect(20, y_top, 330, 260, fill="#f8fafc", stroke=LINE, sw=1))
    f.append(text(xL, y_top + 25, "Просторове різноманіття (Spatial)", size=14, bold=True))

    # Щогла та дві рознесені антени
    f.append(line(xL, y_top + 165, xL, y_top + 70, color=MUTED, sw=3))
    # Поперечна траверса
    f.append(line(xL - 110, y_top + 100, xL + 110, y_top + 100, color=INK, sw=3))
    # Антена 1
    f.append(rect(xL - 120, y_top + 75, 20, 50, fill=FILL, stroke=WAVE1, sw=2))
    f.append(line(xL - 110, y_top + 80, xL - 110, y_top + 120, color=WAVE1, sw=2.5))
    # Антена 2
    f.append(rect(xL + 100, y_top + 75, 20, 50, fill=FILL, stroke=WAVE2, sw=2))
    f.append(line(xL + 110, y_top + 80, xL + 110, y_top + 120, color=WAVE2, sw=2.5))

    # Відстань d >= 10 lambda: стрілка розміщена над текстом (y = y_top + 130), без перетинів з textbox
    f.append(arrow(xL - 90, y_top + 128, xL - 108, y_top + 128, color=LINE, sw=1.5))
    f.append(arrow(xL + 90, y_top + 128, xL + 108, y_top + 128, color=LINE, sw=1.5))
    tb1, _, _ = textbox(xL, y_top + 152, "d >= 10 lambda (1.5–3 м)", size=11, pad=4, fill="#ffffff", stroke=LINE)
    f.append(tb1)

    f.append(mtext(xL, y_top + 200, ["Потрібна велика вежа", "Велика парусність та вага", "Широка виносна траверса"], size=11, color=MUTED))

    # Права панель: Поляризаційне різноманіття (Polarization Diversity)
    xR = 550
    f.append(rect(380, y_top, 340, 260, fill="#f8fafc", stroke=LINE, sw=1))
    f.append(text(xR, y_top + 25, "Поляризаційне різноманіття (Polarization)", size=14, bold=True))

    # Щогла та ЄДИНА суміщена панель
    f.append(line(xR, y_top + 155, xR, y_top + 70, color=MUTED, sw=3))
    # Панельна антена
    f.append(rect(xR - 25, y_top + 65, 50, 90, fill="#ffffff", stroke=FIELD, sw=2.5, rx=4))

    # Схрещені вібратори всередині (+45° та -45°)
    f.append(line(xR - 15, y_top + 125, xR + 15, y_top + 95, color=WAVE1, sw=3))
    f.append(line(xR - 15, y_top + 95, xR + 15, y_top + 125, color=WAVE2, sw=3))

    tb2, _, _ = textbox(xR, y_top + 175, "Суміщені антени в 1 панелі\n(d = 0, один корпус)", size=11, pad=5, fill="#e8f8f0", stroke=FIELD)
    f.append(tb2)

    f.append(mtext(xR, y_top + 225, ["Мінімальні габарити", "Низьке вітрове навантаження", "Окремі RF-порти (+45° / -45°)"], size=11, color=MUTED))

    render(os.path.join(IMG, "spatial-vs-polarization.svg"), W, H, *f)


# ── 2. Симетрія похилої поляризації (+45° / -45°) ───────────────────────────
def fig_slant_45():
    W, H = 740, 340
    f = [text(W / 2, 25, "Перевага похилої поляризації (+45° / -45°) над V/H", size=16, bold=True)]

    # Ліворуч: V/H поляризація
    xL = 190
    y0 = 70
    f.append(rect(20, y0, 330, 245, fill="#fff5f5", stroke=POS, sw=1))
    f.append(text(xL, y0 + 25, "Вертикальна / Горизонтальна (V/H)", size=13, bold=True, color=POS))

    # Земля
    f.append(line(xL - 120, y0 + 170, xL + 120, y0 + 170, color=LINE, sw=2))
    f.append(text(xL, y0 + 188, "Поверхня землі / фасад", size=11, color=MUTED))

    # Вектори V та H
    f.append(arrow(xL - 50, y0 + 150, xL - 50, y0 + 70, color=WAVE1, sw=2.5))
    f.append(text(xL - 50, y0 + 60, "V (вертикаль)", size=11, bold=True, color=WAVE1))

    f.append(arrow(xL + 20, y0 + 110, xL + 90, y0 + 110, color=WAVE2, sw=2.5))
    f.append(text(xL + 55, y0 + 95, "H (горизонталь)", size=11, bold=True, color=WAVE2))

    tb_vh, _, _ = textbox(xL, y0 + 215, "Несиметричні відбиття від землі!\nКанал H слабший за V на 3–6 дБ (дисбаланс)", size=10.5, pad=4, fill="#ffffff", stroke=POS)
    f.append(tb_vh)

    # Праворуч: Slant +-45° поляризація
    xR = 550
    f.append(rect(380, y0, 340, 245, fill="#f0fff4", stroke=FIELD, sw=1))
    f.append(text(xR, y0 + 25, "Похила поляризація (+45° / -45° Slant)", size=13, bold=True, color=FIELD))

    # Земля
    f.append(line(xR - 120, y0 + 170, xR + 120, y0 + 170, color=LINE, sw=2))
    f.append(text(xR, y0 + 188, "Поверхня землі / фасад", size=11, color=MUTED))

    # Вектори +45 та -45
    f.append(arrow(xR - 40, y0 + 150, xR + 20, y0 + 90, color=WAVE1, sw=2.5))
    f.append(text(xR + 35, y0 + 85, "+45°", size=12, bold=True, color=WAVE1))

    f.append(arrow(xR + 40, y0 + 150, xR - 20, y0 + 90, color=WAVE2, sw=2.5))
    f.append(text(xR - 35, y0 + 85, "-45°", size=12, bold=True, color=WAVE2))

    tb_slant, _, _ = textbox(xR, y0 + 215, "Ідеальна симетрія відносно землі!\nОднаковий середній рівень потужності (0 дБ)", size=10.5, pad=4, fill="#ffffff", stroke=FIELD)
    f.append(tb_slant)

    render(os.path.join(IMG, "slant-45.svg"), W, H, *f)


# ── 3. Схеми об'єднання сигналів (SC та MRC) ────────────────────────────────
def fig_combining_schemes():
    W, H = 740, 350
    f = [text(W / 2, 25, "Схеми об'єднання сигналів рознесеного прийому", size=16, bold=True)]

    y0 = 65

    # Вхідні антени +45° та -45°
    f.append(rect(30, y0 + 30, 50, 40, fill="#ffffff", stroke=WAVE1, sw=2))
    f.append(text(55, y0 + 55, "+45°", size=12, bold=True, color=WAVE1))

    f.append(rect(30, y0 + 150, 50, 40, fill="#ffffff", stroke=WAVE2, sw=2))
    f.append(text(55, y0 + 175, "-45°", size=12, bold=True, color=WAVE2))

    # Радіочастотні канали RX1 та RX2
    tb_rx1, _, _ = textbox(160, y0 + 50, "Канал RX 1\nr1(t) = h1·s + n1", size=11, pad=5, fill=FILL, stroke=LINE)
    f.append(tb_rx1)

    tb_rx2, _, _ = textbox(160, y0 + 170, "Канал RX 2\nr2(t) = h2·s + n2", size=11, pad=5, fill=FILL, stroke=LINE)
    f.append(tb_rx2)

    f.append(arrow(80, y0 + 50, 105, y0 + 50, color=WAVE1, sw=2))
    f.append(arrow(80, y0 + 170, 105, y0 + 170, color=WAVE2, sw=2))

    # Стрілки від RX до обробки
    f.append(arrow(215, y0 + 50, 270, y0 + 50, color=LINE, sw=1.8))
    f.append(arrow(215, y0 + 170, 270, y0 + 170, color=LINE, sw=1.8))

    # Верхній блок: Selection Combining (SC)
    f.append(rect(275, y0 + 15, 230, 90, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(text(390, y0 + 35, "Selection Combining (SC)", size=12, bold=True))
    f.append(text(390, y0 + 58, "Вибір каналу з max(SNR)", size=11, color=MUTED))
    f.append(text(390, y0 + 80, "gamma_sc = max(gamma1, gamma2)", size=10.5, color=INK, bold=True))

    # Нижній блок: Maximal Ratio Combining (MRC)
    f.append(rect(275, y0 + 135, 230, 90, fill="#e8f8f0", stroke=FIELD, sw=2))
    f.append(text(390, y0 + 155, "Maximal Ratio Combining (MRC)", size=12, bold=True, color=FIELD))
    f.append(text(390, y0 + 178, "Вагове додавання w_i = h_i*", size=11, color=MUTED))
    f.append(text(390, y0 + 200, "gamma_mrc = gamma1 + gamma2", size=10.5, color=FIELD, bold=True))

    # Виходи
    f.append(arrow(505, y0 + 60, 560, y0 + 60, color=MUTED, sw=1.8))
    tb_out_sc, _, _ = textbox(635, y0 + 60, "Вихід SC\n(Простий)", size=11, pad=5, fill="#ffffff", stroke=MUTED)
    f.append(tb_out_sc)

    f.append(arrow(505, y0 + 180, 560, y0 + 180, color=FIELD, sw=2))
    tb_out_mrc, _, _ = textbox(635, y0 + 180, "Вихід MRC\n(Максимальний SNR)", size=11, pad=5, fill="#ffffff", stroke=FIELD)
    f.append(tb_out_mrc)

    # Примітка знизу
    f.append(text(W / 2, y0 + 260, "MRC забезпечує максимальний виграш рознесеного прийому завдяки накопиченню енергії обох ветвей", size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "combining-schemes.svg"), W, H, *f)


# ── 4. Криві ймовірності обриву зв'язку (CDF замирань) ──────────────────────
def fig_fading_cdf():
    W, H = 740, 360
    f = [text(W / 2, 25, "Зниження ймовірності обриву зв'язку (Outage Probability)", size=16, bold=True)]

    # Координатна сітка
    x0, y0 = 100, 280
    x_len, y_len = 580, 210

    # Осі
    f.append(arrow(x0, y0, x0 + x_len, y0, color=LINE, sw=2))
    f.append(text(x0 + x_len, y0 + 25, "Пороговий SNR / Середній SNR (дБ)", size=12, anchor="end"))

    f.append(arrow(x0, y0, x0, y0 - y_len, color=LINE, sw=2))
    f.append(text(x0 - 15, y0 - y_len + 10, "P_out", size=12, bold=True))

    # Поділки y (логарифмічна шкала P_out: 1, 0.1, 0.01, 0.001)
    y_levels = [
        (y0, "10⁰ = 1.0"),
        (y0 - 60, "10⁻¹ = 0.1"),
        (y0 - 120, "10⁻² = 0.01"),
        (y0 - 180, "10⁻³ = 0.001"),
    ]
    for y_val, lbl in y_levels:
        f.append(line(x0 - 5, y_val, x0 + x_len - 20, y_val, color="#e2e8f0", sw=1, dash="4,4"))
        f.append(text(x0 - 10, y_val + 4, lbl, size=10.5, color=MUTED, anchor="end"))

    # Поділки x (-30 dB ... 0 dB)
    x_ticks = [
        (x0, "-30 дБ"),
        (x0 + 140, "-20 дБ"),
        (x0 + 280, "-10 дБ"),
        (x0 + 420, "0 дБ"),
    ]
    for x_val, lbl in x_ticks:
        f.append(line(x_val, y0 + 5, x_val, y0 - y_len + 10, color="#e2e8f0", sw=1, dash="4,4"))
        f.append(text(x_val, y0 + 18, lbl, size=10.5, color=MUTED))

    # Крива 1: 1 антена (Rayleigh)
    pts1 = [
        (x0, y0 - 180),          # -30 dB -> 10^-3
        (x0 + 140, y0 - 120),    # -20 dB -> 10^-2
        (x0 + 280, y0 - 60),     # -10 dB -> 10^-1
        (x0 + 420, y0),          # 0 dB -> 1
    ]
    f.append(line_pts(pts1, color=POS, sw=2.5))
    f.append(text(x0 + 430, y0 - 15, "1 антена (без diversity)", size=11, color=POS, anchor="start", bold=True))

    # Крива 2: 2 антени SC (rho = 0)
    pts2 = [
        (x0 + 70, y0 - 180),     # -25 dB -> 10^-3
        (x0 + 140, y0 - 140),    # -20 dB -> 0.02
        (x0 + 210, y0 - 100),
        (x0 + 280, y0 - 60),
        (x0 + 380, y0),
    ]
    f.append(line_pts(pts2, color=MUTED, sw=2, dash="6,3"))
    f.append(text(x0 + 330, y0 - 105, "2 антени SC (rho=0)", size=11, color=MUTED, anchor="start"))

    # Крива 3: 2 антени MRC (rho = 0)
    pts3 = [
        (x0 + 120, y0 - 180),    # -21.5 dB -> 10^-3
        (x0 + 210, y0 - 120),    # -15 dB -> 10^-2
        (x0 + 310, y0 - 60),     # -8 dB -> 10^-1
        (x0 + 410, y0),
    ]
    f.append(line_pts(pts3, color=FIELD, sw=3))
    f.append(text(x0 + 330, y0 - 45, "2 антени MRC (rho=0)", size=11, color=FIELD, anchor="start", bold=True))

    # Стрілка виграшу на рівні P_out = 0.01 (10^-2)
    y_target = y0 - 120
    f.append(line(x0 + 140, y_target, x0 + 210, y_target, color=ACCENT, sw=2))
    f.append(arrow(x0 + 140, y_target, x0 + 210, y_target, color=ACCENT, sw=2))
    f.append(arrow(x0 + 210, y_target, x0 + 140, y_target, color=ACCENT, sw=2))

    tb_gain, _, _ = textbox(x0 + 175, y_target + 25, "Виграш ~12 дБ за P_out = 1%", size=10.5, pad=3, fill="#ffffff", stroke=ACCENT)
    f.append(tb_gain)

    render(os.path.join(IMG, "fading-cdf.svg"), W, H, *f)


def line_pts(pts, color=LINE, sw=1.5, dash=None):
    pt_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pt_str, color, sw, d)


if __name__ == "__main__":
    fig_spatial_vs_polarization()
    fig_slant_45()
    fig_combining_schemes()
    fig_fading_cdf()
    print("Успішно згенеровано 4 фігури в", IMG)
