# -*- coding: utf-8 -*-
"""
Генератор фігур для теми «Поглинання звуку в повітрі» (acoustic-absorption).
Вивід: SVG-файли у теці ./img/
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def fig_relaxation_mechanism():
    """Фігура 1: Фізичний механізм молекулярної релаксації."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 28, "Молекулярна релаксація та гістерезис акустичного стиснення", size=16, bold=True))

    # Схема 1: Молекулярне зіткнення та обмін енергією (ліва частина)
    frags.append(rect(20, 50, 350, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(195, 75, "1. Передача енергії при зіткненні", size=14, bold=True))

    frags.append(circle(110, 140, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(circle(140, 140, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(125, 145, "N₂ / O₂", size=13, color=NEG, bold=True))
    frags.append(arrow(55, 140, 80, 140, color=NEG, sw=2))
    frags.append(text(67, 126, "v_пост", size=11, color=NEG))

    frags.append(circle(270, 140, 26, fill="#fdecea", stroke=POS, sw=2))
    frags.append(circle(252, 162, 14, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(circle(288, 162, 14, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(270, 144, "H₂O", size=13, color=POS, bold=True))
    frags.append(arrow(330, 140, 303, 140, color=POS, sw=2))
    frags.append(text(315, 126, "v_пост", size=11, color=POS))

    frags.append(arrow(150, 190, 230, 190, color=FIELD, sw=2.5))
    frags.append(textbox(195, 225, "Ефективний обмін V-T:\nкороткий час релаксації τ", size=12, pad=6, fill="#e8f8f0", stroke=FIELD)[0])

    frags.append(line(50, 300, 130, 300, color=MUTED, sw=1.5))
    frags.append(line(50, 330, 130, 330, color=MUTED, sw=1.5))
    frags.append(line(50, 360, 130, 360, color=MUTED, sw=1.5))
    frags.append(text(90, 290, "E_колив (v=2)", size=10, color=MUTED))
    frags.append(text(90, 320, "E_колив (v=1)", size=10, color=MUTED))
    frags.append(text(90, 352, "E_основний (v=0)", size=10, color=MUTED))
    frags.append(arrow(90, 355, 90, 305, color=POS, sw=1.8))
    frags.append(text(150, 330, "Затримка фази Δφ = ωτ", size=12, color=INK, bold=True))

    # Схема 2: Гістерезис p-ρ (права частина)
    frags.append(rect(390, 50, 350, 340, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(565, 75, "2. Гістерезис p(ρ) і втрата енергії", size=14, bold=True))

    ox, oy = 440, 340
    frags.append(arrow(ox, oy, ox + 270, oy, color=LINE, sw=1.5))
    frags.append(text(ox + 260, oy + 20, "Густина ρ", size=12, bold=True))
    frags.append(arrow(ox, oy, ox, oy - 230, color=LINE, sw=1.5))
    frags.append(text(ox - 30, oy - 220, "Тиск p", size=12, bold=True))

    cx_p, cy_p = 560, 220
    rx_p, ry_p = 90, 60
    angle_deg = 35

    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    loop_path_up = []
    loop_path_dn = []
    for t in range(0, 181, 5):
        tr = math.radians(t)
        x_raw = rx_p * math.cos(tr)
        y_raw = -ry_p * math.sin(tr)
        x = cx_p + x_raw * cos_a - y_raw * sin_a
        y = cy_p + x_raw * sin_a + y_raw * cos_a
        loop_path_up.append((x, y))

    for t in range(180, 361, 5):
        tr = math.radians(t)
        x_raw = rx_p * math.cos(tr)
        y_raw = -ry_p * math.sin(tr)
        x = cx_p + x_raw * cos_a - y_raw * sin_a
        y = cy_p + x_raw * sin_a + y_raw * cos_a
        loop_path_dn.append((x, y))

    all_pts = loop_path_up + loop_path_dn
    pts_str = " ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in all_pts])
    frags.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2"/>' % (pts_str, POS))

    frags.append(arrow(loop_path_up[15][0], loop_path_up[15][1], loop_path_up[17][0], loop_path_up[17][1], color=POS, sw=2))
    frags.append(arrow(loop_path_dn[15][0], loop_path_dn[15][1], loop_path_dn[17][0], loop_path_dn[17][1], color=POS, sw=2))

    frags.append(line(cx_p - 110 * cos_a, cy_p - 110 * sin_a, cx_p + 110 * cos_a, cy_p + 110 * sin_a, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(cx_p + 50, cy_p + 95, "Рівноважна адіабата (τ=0)", size=10, color=MUTED))

    frags.append(textbox(575, 215, "Площа петлі =\nвтрачена енергія\nза один цикл Q⁻¹", size=11, pad=5, fill="#ffffff", stroke=POS)[0])

    render(os.path.join(IMG_DIR, "relaxation-mechanism.svg"), w, h, *frags)

def fig_attenuation_components():
    """Фігура 2: Компоненти поглинання звуку в повітрі залежно від частоти."""
    w, h = 760, 440
    frags = []

    frags.append(text(w / 2, 28, "Внесок механізмів у загальне поглинання (20°C, 1 атм, RH=50%)", size=16, bold=True))

    ox, oy = 80, 380
    gw, gh = 640, 300

    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafafa", stroke=LINE, sw=1.2, rx=4))

    freqs = [100, 1000, 10000, 100000]
    freq_labels = ["100 Гц", "1 кГц", "10 кГц", "100 кГц"]

    def f_to_x(f):
        lf = math.log10(f)
        return ox + (lf - 2.0) / 3.0 * gw

    def a_to_y(a):
        la = math.log10(max(a, 0.05))
        return oy - (la - (-1.0)) / 4.0 * gh

    for f, lbl in zip(freqs, freq_labels):
        x = f_to_x(f)
        frags.append(line(x, oy, x, oy - gh, color="#e0e0e0", sw=1, dash="2,2"))
        frags.append(text(x, oy + 20, lbl, size=12, bold=True))

    db_vals = [0.1, 1, 10, 100, 1000]
    db_labels = ["0.1", "1", "10", "100", "1000"]
    for v, lbl in zip(db_vals, db_labels):
        y = a_to_y(v)
        frags.append(line(ox, y, ox + gw, y, color="#e0e0e0", sw=1, dash="2,2"))
        frags.append(text(ox - 10, y + 4, lbl, size=11, anchor="end", color=MUTED))

    frags.append(text(ox - 45, oy - gh / 2, "Коефіцієнт поглинання α (дБ/км)", size=12, bold=True, anchor="middle"))

    pts_class = []
    for f_i in range(100, 100001, 1000):
        a_c = 1.6e-11 * (f_i ** 2) * 8686
        pts_class.append((f_to_x(f_i), a_to_y(a_c)))
    str_class = " ".join(["%.1f,%.1f" % pt for pt in pts_class])
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (str_class, MUTED))

    pts_total = []
    for f_i in range(100, 100001, 500):
        f_r_O2 = 32000
        f_r_N2 = 300
        a_c = 1.6e-11 * (f_i ** 2) * 8686
        a_O2 = 8.686 * f_i**2 * (1.2e-9 * f_r_O2 / (f_r_O2**2 + f_i**2)) * 1000
        a_N2 = 8.686 * f_i**2 * (1.1e-10 * f_r_N2 / (f_r_N2**2 + f_i**2)) * 1000
        a_tot = a_c + a_O2 + a_N2
        pts_total.append((f_to_x(f_i), a_to_y(a_tot)))

    str_tot = " ".join(["%.1f,%.1f" % pt for pt in pts_total])
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (str_tot, POS))

    frags.append(text(f_to_x(70000), a_to_y(15) - 15, "Класичне (в'язкість + теплопровідність) ~ f²", size=11, color=MUTED, anchor="end"))
    frags.append(textbox(450, 160, "Сумарне поглинання α_total\n(з урахуванням O₂ та N₂)", size=12, pad=6, fill="#fdecea", stroke=POS)[0])
    frags.append(textbox(210, 310, "Домінування релаксації N₂\n(низькі частоти < 1 кГц)", size=11, pad=5, fill="#eaf0fd", stroke=NEG)[0])
    frags.append(textbox(570, 240, "Домінування релаксації O₂\n(високі частоти > 10 кГц)", size=11, pad=5, fill="#e8f8f0", stroke=FIELD)[0])

    render(os.path.join(IMG_DIR, "attenuation-components.svg"), w, h, *frags)

def fig_absorption_vs_frequency():
    """Фігура 3: Залежність поглинання від відносної вологості повітря (RH)."""
    w, h = 760, 440
    frags = []

    frags.append(text(w / 2, 28, "Вплив відносної вологості (RH) на поглинання звуку при 20°C", size=16, bold=True))

    ox, oy = 80, 380
    gw, gh = 640, 300
    frags.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

    freqs = [100, 1000, 10000, 100000]
    freq_labels = ["100 Гц", "1 кГц", "10 кГц", "100 кГц"]
    def f_to_x(f):
        return ox + (math.log10(f) - 2.0) / 3.0 * gw

    def a_to_y(a):
        return oy - (math.log10(max(a, 0.1)) - (-1.0)) / 4.0 * gh

    for f, lbl in zip(freqs, freq_labels):
        x = f_to_x(f)
        frags.append(line(x, oy, x, oy - gh, color="#f0f0f0", sw=1))
        frags.append(text(x, oy + 20, lbl, size=12, bold=True))

    db_vals = [0.1, 1, 10, 100, 1000]
    for v in db_vals:
        y = a_to_y(v)
        frags.append(line(ox, y, ox + gw, y, color="#f0f0f0", sw=1))
        frags.append(text(ox - 10, y + 4, str(v), size=11, anchor="end", color=MUTED))

    frags.append(text(ox - 45, oy - gh / 2, "α (дБ/км)", size=12, bold=True, anchor="middle"))

    rhs = [(10, "#c0392b", "RH = 10% (сухе повітря)"),
           (30, "#27ae60", "RH = 30% (нормальне)"),
           (80, "#2457d6", "RH = 80% (вологе повітря)")]

    for rh_val, col, label in rhs:
        pts = []
        fr_O2 = 10000 + rh_val * 600
        fr_N2 = 100 + rh_val * 5
        for f_i in range(100, 100001, 1000):
            a_c = 1.6e-11 * (f_i ** 2) * 8686
            a_O2 = 8.686 * f_i**2 * (1.5e-9 * (100 / rh_val)**0.2 * fr_O2 / (fr_O2**2 + f_i**2)) * 1000
            a_N2 = 8.686 * f_i**2 * (1.2e-10 * fr_N2 / (fr_N2**2 + f_i**2)) * 1000
            a_tot = a_c + a_O2 + a_N2
            pts.append((f_to_x(f_i), a_to_y(a_tot)))

        str_pts = " ".join(["%.1f,%.1f" % pt for pt in pts])
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (str_pts, col))

    # Легенда без додаткового rect, використовуємо масив ліній та тексту
    lx, ly = 95, 95
    for i, (rh_val, col, label) in enumerate(rhs):
        frags.append(line(lx + 10, ly + i * 22, lx + 35, ly + i * 22, color=col, sw=3))
        frags.append(text(lx + 42, ly + 4 + i * 22, label, size=11, anchor="start", bold=True))

    frags.append(textbox(560, 160, "Сухе повітря (10% RH):\nбільше поглинання на 1-5 кГц!", size=11, pad=5, fill="#fdecea", stroke=POS)[0])
    frags.append(textbox(560, 310, "Вологе повітря (80% RH):\nменше поглинання середніх частот", size=11, pad=5, fill="#eaf0fd", stroke=NEG)[0])

    render(os.path.join(IMG_DIR, "absorption-vs-frequency.svg"), w, h, *frags)

def fig_humidity_effect():
    """Фігура 4: Зсув релаксаційних частот O2 та N2 залежно від молярної концентрації вологи."""
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 28, "Каталітичний зсув частот релаксації f_r(O₂) та f_r(N₂) від вмісту H₂O", size=16, bold=True))

    ox, oy = 90, 360
    gw, gh = 620, 270

    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafafa", stroke=LINE, sw=1.2, rx=4))

    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    frags.append(text(ox + gw / 2, oy + 35, "Молярна концентрація водяної пари h (% H₂O)", size=12, bold=True))

    for h_pct in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        x = ox + (h_pct / 3.0) * gw
        frags.append(line(x, oy, x, oy - gh, color="#e8e8e8", sw=1, dash="2,2"))
        frags.append(text(x, oy + 18, "%.1f%%" % h_pct, size=11, color=MUTED))

    frags.append(arrow(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.5))
    frags.append(text(ox - 45, oy - gh / 2, "Релаксаційна частота f_r (Гц)", size=12, bold=True, anchor="middle"))

    def fr_to_y(fr):
        lfr = math.log10(max(fr, 10))
        return oy - (lfr - 1.0) / 4.0 * gh

    for fr_val in [10, 100, 1000, 10000, 100000]:
        y = fr_to_y(fr_val)
        frags.append(line(ox, y, ox + gw, y, color="#e8e8e8", sw=1, dash="2,2"))
        frags.append(text(ox - 10, y + 4, str(fr_val), size=11, anchor="end", color=MUTED))

    pts_O2 = []
    for step in range(0, 301, 5):
        h_val = step / 100.0
        fr_O2 = 24 + 40400.0 * h_val * (0.02 + h_val) / (0.391 + h_val)
        x = ox + (h_val / 3.0) * gw
        y = fr_to_y(fr_O2)
        pts_O2.append((x, y))
    str_O2 = " ".join(["%.1f,%.1f" % pt for pt in pts_O2])
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (str_O2, POS))

    pts_N2 = []
    for step in range(0, 301, 5):
        h_val = step / 100.0
        fr_N2 = 9 + 280.0 * h_val
        x = ox + (h_val / 3.0) * gw
        y = fr_to_y(fr_N2)
        pts_N2.append((x, y))
    str_N2 = " ".join(["%.1f,%.1f" % pt for pt in pts_N2])
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (str_N2, NEG))

    frags.append(text(ox + 450, fr_to_y(70000) - 12, "f_r(O₂) — Кисень (до 60-100 кГц)", size=12, color=POS, bold=True))
    frags.append(text(ox + 450, fr_to_y(600) - 12, "f_r(N₂) — Азот (до 1 кГц)", size=12, color=NEG, bold=True))

    # Перенесено textbox вище, де немає перетину з кривими
    frags.append(textbox(210, 60, "Без H₂O (абсолютно сухе повітря):\nτ(N₂) > 1 с, τ(O₂) > 0.01 с (беззвучно).\nДодавання 1% H₂O прискорює V-T обмін у 1000 разів!", size=11, pad=6, fill="#f8fafc", stroke=FIELD)[0])

    render(os.path.join(IMG_DIR, "humidity-effect.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_relaxation_mechanism()
    fig_attenuation_components()
    fig_absorption_vs_frequency()
    fig_humidity_effect()
    print("Всі 4 фігури успішно згенеровано у ./img/")
