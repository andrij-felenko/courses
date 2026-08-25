# -*- coding: utf-8 -*-
"""Фігури до теми «Точка Кюрі».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Температурна залежність намагніченості, сприйнятливості та теплоємності ───────
def fig_spontaneous_magnetization_temp():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Термодинамічні величини поблизу точки Кюрі (T_C)", size=16, bold=True, color=INK))

    x_zero = 80
    x_tc = 440
    x_max = 700
    y_top = 55
    y_bot = 370

    f.append(rect(x_zero, y_top, x_tc - x_zero, y_bot - y_top, fill="#eff6ff", stroke="none", rx=0))
    f.append(rect(x_tc, y_top, x_max - x_tc, y_bot - y_top, fill="#fff7ed", stroke="none", rx=0))

    f.append(path_svg(f"M {x_tc} {y_top} L {x_tc} {y_bot}", stroke="#dc2626", sw=2, dash="4,4"))
    f.append(text(x_tc, y_top + 16, "T = T_C", size=13, bold=True, color="#dc2626"))

    f.append(text((x_zero + x_tc) / 2, y_top + 18, "Феромагнітна фаза (M > 0)", size=12, bold=True, color="#1e40af"))
    f.append(text((x_tc + x_max) / 2, y_top + 18, "Парамагнітна фаза (M = 0)", size=12, bold=True, color="#c2410c"))

    f.append(arrow(x_zero, y_bot, x_max + 25, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 35, y_bot + 4, "T", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 10, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 5, "M, χ, C_p", size=12, bold=True, color=INK))

    f.append(text(x_zero, y_bot + 18, "0 K", size=11, color=MUTED))
    f.append(text(x_tc, y_bot + 18, "T_C", size=12, bold=True, color="#dc2626"))

    pts_m = []
    y_m0 = 100
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc - x_zero)
        val = (1.0 - t_ratio**1.8)**0.33 if t_ratio < 1.0 else 0.0
        y = y_bot - val * (y_bot - y_m0)
        pts_m.append((x, y))
    pts_m.append((x_max, y_bot))

    d_m = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_m)
    f.append(path_svg(d_m, stroke="#2563eb", sw=3))
    f.append(text(x_zero + 60, y_m0 + 20, "Спонтанна намагніченість M(T)", size=12, bold=True, color="#2563eb"))
    f.append(text(x_zero - 15, y_m0, "M_0", size=11, bold=True, color="#2563eb"))

    pts_chi = []
    y_chi_top = y_top + 40
    for i in range(1, 101):
        t_ratio = 1.0 + (i / 100.0) * 0.8
        x = x_tc + (i / 100.0) * (x_max - x_tc)
        val = 15.0 / (i + 5.0)
        y = y_bot - val * (y_bot - y_chi_top)
        pts_chi.append((x, y))

    d_chi = "M " + f"{x_tc:.1f} {y_chi_top:.1f} " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_chi)
    f.append(path_svg(d_chi, stroke="#059669", sw=2.5))
    f.append(text(x_tc + 90, y_top + 90, "Сприйнятливість χ ~ 1/(T - T_C)", size=11, bold=True, color="#059669"))

    pts_cp = []
    y_cp_peak = y_top + 35
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc - x_zero)
        val = 0.2 + 0.8 * (t_ratio**3)
        y = y_bot - val * (y_bot - y_cp_peak)
        pts_cp.append((x, y))
    pts_cp.append((x_tc, y_cp_peak))
    pts_cp.append((x_tc + 15, y_bot - 0.3 * (y_bot - y_cp_peak)))
    pts_cp.append((x_max, y_bot - 0.25 * (y_bot - y_cp_peak)))

    d_cp = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_cp)
    f.append(path_svg(d_cp, stroke="#9333ea", sw=2, dash="5,3"))
    f.append(text(x_tc - 140, y_cp_peak + 35, "Теплоємність C_p (λ-пік)", size=11, bold=True, color="#9333ea"))

    f.append(text(W / 2, H - 12, "При T → T_C спонтанна намагніченість спадає до нуля, а сприйнятливість розбігається (фазовий перехід II роду)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spontaneous-magnetization-temp.svg'), W, H, "\n".join(f))

# ── Фігура 2: Шкала температур Кюрі для різних матеріалів ────────────────────
def fig_curie_temperature_materials():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 25, "Шкала температур Кюрі T_C для феромагнетиків та сегнетоелектриків", size=15, bold=True, color=INK))

    x_start = 70
    x_end = 700
    y_axis = 200

    f.append(arrow(x_start - 20, y_axis, x_end + 30, y_axis, color=INK, sw=2))
    f.append(text(x_end + 40, y_axis + 4, "T (°C)", size=13, bold=True, color=INK))

    def temp_to_x(t_celsius):
        norm = (t_celsius - (-100)) / (1200 - (-100))
        return x_start + norm * (x_end - x_start)

    ticks = [-100, 0, 200, 400, 600, 800, 1000, 1200]
    for t in ticks:
        x = temp_to_x(t)
        f.append(line(x, y_axis - 5, x, y_axis + 5, color=LINE, sw=1.5))
        f.append(text(x, y_axis + 18, f"{t}°", size=10, color=MUTED))

    # 4 рівні висоти для запобігання перетину блоків
    materials = [
        ("Гадоліній (Gd)", 19, "#2563eb", -135, "19 °C (кімнатна T!)"),
        ("BaTiO3 (сегнето)", 120, "#7c3aed", -75, "120 °C (сегнетоточки)"),
        ("Nd2Fe14B (неодим)", 312, "#dc2626", 75, "312 °C (ліміт NdFeB)"),
        ("Нікель (Ni)", 354, "#059669", 135, "354 °C"),
        ("Ферит BaFe12O19", 450, "#d97706", -135, "450 °C (керамічний)"),
        ("Залізо (Fe)", 770, "#b91c1c", -75, "770 °C (чистий Fe)"),
        ("SmCo5 (самарій-кобальт)", 800, "#4338ca", 75, "800 °C (високотемп.)"),
        ("Кобальт (Co)", 1115, "#991b1b", 135, "1115 °C (рекорд елементів)")
    ]

    for name, t_c, color, y_off, label in materials:
        x = temp_to_x(t_c)
        y_label = y_axis + y_off

        # Пряма лінія від осі до картки
        line_target_y = y_label + (16 if y_off < 0 else -16)
        f.append(line(x, y_axis, x, line_target_y, color=color, sw=1.5, dash="2,2"))
        f.append(circle(x, y_axis, 4, fill=color, stroke="#ffffff", sw=1.5))

        bw = 125
        bh = 32
        bx = x - bw / 2
        by = y_label - bh / 2
        f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=color, sw=1.5, rx=5))
        f.append(text(x, by + 11, name, size=10, bold=True, color=INK))
        f.append(text(x, by + 24, label, size=9, color=color))

    render(os.path.join(IMG_DIR, 'curie-temperature-materials.svg'), W, H, "\n".join(f))

# ── Фігура 3: Механізм паяльника Weller з термовимикачем у точці Кюрі ────────
def fig_weller_curie_switch():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 25, "Термостатування паяльника Weller за точкою Кюрі наконечника", size=15, bold=True, color=INK))

    bw, bh = 335, 270
    y_top = 50

    # Ліва панель: T < T_C (Холодний / Нагрів увімкнено)
    x1 = 25
    f.append(rect(x1, y_top, bw, bh, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(x1 + bw / 2, y_top + 22, "T < T_C (Холодний): Нагрів УВІМКНЕНО", size=13, bold=True, color="#15803d"))

    f.append(rect(x1 + 30, y_top + 60, 60, 80, fill="#cbd5e1", stroke=INK, sw=1.5, rx=3))
    f.append(mtext(x1 + 60, y_top + 90, "Сплав Fe-Ni\n(T < T_C)", size=10, bold=True, color=INK))
    f.append(text(x1 + 60, y_top + 125, "Феромагнітний", size=9, bold=True, color="#15803d"))

    f.append(rect(x1 + 100, y_top + 70, 50, 60, fill="#ef4444", stroke=INK, sw=1.5, rx=3))
    f.append(text(x1 + 125, y_top + 105, "Магніт", size=10, bold=True, color="#ffffff"))
    f.append(arrow(x1 + 100, y_top + 100, x1 + 92, y_top + 100, color="#15803d", sw=2))

    f.append(path_svg(f"M {x1 + 150} {y_top + 100} L {x1 + 160} {y_top + 90} L {x1 + 170} {y_top + 110} L {x1 + 180} {y_top + 90} L {x1 + 190} {y_top + 100}", stroke=INK, sw=1.5))

    f.append(line(x1 + 190, y_top + 100, x1 + 240, y_top + 100, color=INK, sw=2))
    f.append(circle(x1 + 240, y_top + 95, 5, fill="#16a34a", stroke=INK, sw=1))
    f.append(circle(x1 + 240, y_top + 105, 5, fill="#16a34a", stroke=INK, sw=1))
    f.append(mtext(x1 + 285, y_top + 92, "Контакт\nЗАМКНЕНО", size=10, bold=True, color="#15803d"))

    f.append(rect(x1 + 30, y_top + 165, 275, 45, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=5))
    f.append(text(x1 + 167, y_top + 190, "Струм іде через нагрівальний елемент >>>", size=10, bold=True, color="#854d0e"))
    f.append(mtext(x1 + 167, y_top + 235, "Магніт притягується до феромагнітного\nнаконечника й тримає контакти замкнутими.", size=10, color=MUTED))

    # Права панель: T >= T_C (Гарячий / Нагрів вимкнено)
    x2 = 400
    f.append(rect(x2, y_top, bw, bh, fill="#fff1f2", stroke="#e11d48", sw=1.5, rx=8))
    f.append(text(x2 + bw / 2, y_top + 22, "T ≥ T_C (Гарячий): Нагрів ВИМКНЕНО", size=13, bold=True, color="#be123c"))

    f.append(rect(x2 + 30, y_top + 60, 60, 80, fill="#cbd5e1", stroke=INK, sw=1.5, rx=3))
    f.append(mtext(x2 + 60, y_top + 90, "Сплав Fe-Ni\n(T ≥ T_C)", size=10, bold=True, color=INK))
    f.append(text(x2 + 60, y_top + 125, "Парамагнітний!", size=9, bold=True, color="#be123c"))

    f.append(rect(x2 + 120, y_top + 70, 50, 60, fill="#ef4444", stroke=INK, sw=1.5, rx=3))
    f.append(text(x2 + 145, y_top + 105, "Магніт", size=10, bold=True, color="#ffffff"))
    f.append(arrow(x2 + 105, y_top + 100, x2 + 118, y_top + 100, color="#be123c", sw=2))

    f.append(path_svg(f"M {x2 + 170} {y_top + 100} L {x2 + 185} {y_top + 88} L {x2 + 200} {y_top + 112} L {x2 + 230} {y_top + 100}", stroke=INK, sw=1.5))

    f.append(line(x2 + 230, y_top + 100, x2 + 255, y_top + 90, color=INK, sw=2))
    f.append(circle(x2 + 255, y_top + 85, 5, fill="#e11d48", stroke=INK, sw=1))
    f.append(circle(x2 + 255, y_top + 115, 5, fill="#e11d48", stroke=INK, sw=1))
    f.append(mtext(x2 + 285, y_top + 92, "Контакт\nРОЗЗ'ЄДНАНО", size=10, bold=True, color="#be123c"))

    f.append(rect(x2 + 30, y_top + 165, 275, 45, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, rx=5))
    f.append(text(x2 + 167, y_top + 190, "Коло розімкнене — нагрів припинено", size=10, bold=True, color="#4b5563"))
    f.append(mtext(x2 + 167, y_top + 235, "Наконечник стає парамагнітним, сила зникає,\nпружина відтягує магніт і розмикає струм.", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, 'weller-curie-switch.svg'), W, H, "\n".join(f))

def main():
    fig_spontaneous_magnetization_temp()
    fig_curie_temperature_materials()
    fig_weller_curie_switch()
    print("Фігури успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
