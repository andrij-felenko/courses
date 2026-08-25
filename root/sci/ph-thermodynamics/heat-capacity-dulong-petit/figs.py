# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Дюлонга — Пті та квантова теорія теплоємності Ейнштейна — Дебая».
Запуск: python figs.py -> пише SVG у ./img/
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

# ── Фігура 1: Порівняльний графік теплоємності (Дюлонг-Пті, Ейнштейн, Дебай) ─
def fig_heat_capacity_curves():
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 26, "Залежність молярної теплоємності C_v від температури T", size=15, bold=True, color=INK))

    x_zero = 90
    x_max = 690
    y_top = 65
    y_bot = 370

    # Сітка та зріз 3R
    y_3r = y_top + 45
    f.append(line(x_zero, y_3r, x_max, y_3r, color="#cbd5e1", sw=1.5, dash="4,4"))
    f.append(text(x_zero - 20, y_3r + 4, "3R", size=12, bold=True, color="#1e40af"))
    f.append(text(x_zero - 20, y_bot, "0", size=11, color=MUTED))

    # Осі
    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "T / Θ", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 20, color=INK, sw=1.5))
    f.append(text(x_zero - 30, y_top - 15, "C_v", size=13, bold=True, italic=True, color=INK))

    # Засічки по T/Theta
    for t_val in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
        x_tick = x_zero + (t_val / 1.5) * (x_max - x_zero)
        f.append(line(x_tick, y_bot - 4, x_tick, y_bot + 4, color=LINE, sw=1))
        f.append(text(x_tick, y_bot + 18, f"{t_val:.1f}", size=10, color=MUTED))

    # 1. Класична лінія Дюлонга — Пті (C_v = 3R)
    f.append(line(x_zero, y_3r, x_max, y_3r, color="#dc2626", sw=2.5))
    f.append(text(x_max - 90, y_3r - 10, "Дюлонг — Пті (3R)", size=11, bold=True, color="#dc2626"))

    # 2. Модель Ейнштейна: C_v/3R = (x^2 * e^x) / (e^x - 1)^2, де x = 1 / t
    pts_einstein = []
    for i in range(1, 151):
        t_rel = i * 1.5 / 150.0
        x_coord = x_zero + (t_rel / 1.5) * (x_max - x_zero)
        x_param = 1.0 / t_rel
        if x_param > 20:
            cv_rel = 0.0
        else:
            ex = math.exp(x_param)
            cv_rel = (x_param**2 * ex) / ((ex - 1.0)**2)
        y_coord = y_bot - cv_rel * (y_bot - y_3r)
        pts_einstein.append((x_coord, y_coord))

    d_einstein = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_einstein)
    f.append(path_svg(d_einstein, stroke="#2563eb", sw=2.5, dash="6,3"))
    f.append(text(340, 240, "Ейнштейн (експоненціальне виморожування)", size=10, bold=True, color="#2563eb"))

    # 3. Модель Дебая: наближення C_v/3R (з закону T^3 при низьких T і виходом на 3R)
    pts_debye = []
    for i in range(1, 151):
        t_rel = i * 1.5 / 150.0
        x_coord = x_zero + (t_rel / 1.5) * (x_max - x_zero)
        # Апроксимація функції Дебая D3(1/t)
        if t_rel < 0.15:
            cv_rel = (4.0 * math.pi**4 / 5.0) * (t_rel**3)
        else:
            # Плавне зшивання T^3 з 1/(1 + 0.05/t^2 + 0.015/t^3)
            cv_rel = 1.0 / (1.0 + 0.05 / (t_rel**2) + 0.015 / (t_rel**3))
        if cv_rel > 1.0:
            cv_rel = 1.0
        y_coord = y_bot - cv_rel * (y_bot - y_3r)
        pts_debye.append((x_coord, y_coord))

    d_debye = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_debye)
    f.append(path_svg(d_debye, stroke="#059669", sw=3))
    f.append(text(460, 140, "Дебай (закон T³ при T → 0)", size=11, bold=True, color="#059669"))

    # Акценти на низьких температурах
    f.append(rect(95, 310, 160, 50, fill="#ffffff", stroke="#059669", sw=1, rx=4))
    f.append(text(175, 327, "При T → 0 K:", size=10, bold=True, color=INK))
    f.append(text(175, 345, "Дебай: C_v ~ T³  (експеримент!)", size=9, bold=True, color="#059669"))

    f.append(rect(470, 310, 200, 50, fill="#ffffff", stroke="#1e40af", sw=1, rx=4))
    f.append(text(570, 327, "При T ≫ Θ (високі T):", size=10, bold=True, color=INK))
    f.append(text(570, 345, "Усі моделі → 3R (Дюлонг — Пті)", size=9, bold=True, color="#1e40af"))

    f.append(text(W / 2, H - 10, "Порівняння класичної границі 3R та квантових температурних залежностей Ейнштейна й Дебая", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'heat-capacity-curves.svg'), W, H, "\n".join(f))

# ── Фігура 2: Концептуальне порівняння коливань за Ейнштейном та Дебаєм ─────
def fig_lattice_modes_concept():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 24, "Фізична модель атомних коливань у кристалічному ґратці", size=15, bold=True, color=INK))

    bw, bh = 340, 270
    y_top = 50

    # Ліва частина: Модель Ейнштейна
    x1 = 25
    f.append(rect(x1, y_top, bw, bh, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=8))
    f.append(text(x1 + bw / 2, y_top + 22, "Модель Ейнштейна (1907)", size=13, bold=True, color="#1e40af"))
    f.append(text(x1 + bw / 2, y_top + 40, "Незалежні локалізовані осцилятори", size=10, color=MUTED))

    # Решітка атомів Ейнштейна з локальними пружинами
    for row in range(3):
        for col in range(4):
            ax = x1 + 50 + col * 75
            ay = y_top + 85 + row * 60
            f.append(circle(ax, ay, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
            f.append(circle(ax - 3, ay - 3, 3, fill="#ffffff", stroke="none"))
            # Стрілочки незалежних коливань в різних напрямках
            if (row + col) % 2 == 0:
                f.append(arrow(ax, ay - 14, ax, ay - 24, color="#dc2626", sw=1.5))
                f.append(arrow(ax, ay + 14, ax, ay + 24, color="#dc2626", sw=1.5))
            else:
                f.append(arrow(ax - 14, ay, ax - 24, ay, color="#dc2626", sw=1.5))
                f.append(arrow(ax + 14, ay, ax + 24, ay, color="#dc2626", sw=1.5))

    f.append(rect(x1 + 20, y_top + 215, 300, 45, fill="#ffffff", stroke="#2563eb", sw=1, rx=4))
    f.append(text(x1 + 170, y_top + 233, "Усі атоми коливаються з ОДНІЄЮ частотою ω_E", size=10, bold=True, color="#1e40af"))
    f.append(text(x1 + 170, y_top + 248, "Нівелюються акустичні хвилі та зв'язки між атомами", size=9, color=MUTED))

    # Права частина: Модель Дебая
    x2 = 395
    f.append(rect(x2, y_top, bw, bh, fill="#f0fdf4", stroke="#059669", sw=1.5, rx=8))
    f.append(text(x2 + bw / 2, y_top + 22, "Модель Дебая (1912)", size=13, bold=True, color="#047857"))
    f.append(text(x2 + bw / 2, y_top + 40, "Колективні акустичні хвилі (фонони)", size=10, color=MUTED))

    # Атоми, з'єднані колективною пружною хвилею
    pts_wave = []
    for col in range(8):
        ax = x2 + 35 + col * 38
        ay = y_top + 140 + math.sin(col * 0.9) * 35
        pts_wave.append((ax, ay))

    d_wave = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_wave)
    f.append(path_svg(d_wave, stroke="#059669", sw=2, dash="3,3"))

    for px, py in pts_wave:
        f.append(circle(px, py, 10, fill="#10b981", stroke="#047857", sw=1.5))
        f.append(circle(px - 2, py - 2, 2.5, fill="#ffffff", stroke="none"))

    f.append(text(x2 + bw / 2, y_top + 80, "Довжиннохвильові звукові хвилі λ ≫ a", size=10, bold=True, color="#047857"))

    f.append(rect(x2 + 20, y_top + 215, 300, 45, fill="#ffffff", stroke="#059669", sw=1, rx=4))
    f.append(text(x2 + 170, y_top + 233, "Спектр частот g(ω) ~ ω² до граничної ω_D", size=10, bold=True, color="#047857"))
    f.append(text(x2 + 170, y_top + 248, "Враховує колективний рух атомів у суцільному середовищі", size=9, color=MUTED))

    render(os.path.join(IMG_DIR, 'lattice-modes-concept.svg'), W, H, "\n".join(f))

# ── Фігура 3: Спектральна щільність станів g(omega) ──────────────────────────
def fig_phonon_density_of_states():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 24, "Спектральна щільність коливальних станів g(ω) у моделях Ейнштейна та Дебая", size=15, bold=True, color=INK))

    x_zero = 80
    x_max = 680
    y_top = 55
    y_bot = 300

    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "ω", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 30, y_top - 10, "g(ω)", size=13, bold=True, italic=True, color=INK))

    # 1. Модель Ейнштейна: Дельта-пік
    x_einstein = x_zero + 220
    f.append(line(x_einstein, y_bot, x_einstein, y_top + 20, color="#2563eb", sw=3.5))
    f.append(arrow(x_einstein, y_bot, x_einstein, y_top + 10, color="#2563eb", sw=3.5))
    f.append(text(x_einstein, y_bot + 18, "ω_E", size=12, bold=True, color="#2563eb"))
    f.append(text(x_einstein + 15, y_top + 30, "Пік Ейнштейна: 3N · δ(ω - ω_E)", size=11, bold=True, color="#2563eb"))

    # 2. Модель Дебая: Парабола g(ω) ~ ω^2 до cutoff ω_D
    x_debye = x_zero + 480
    pts_dos_debye = []
    for i in range(101):
        w_val = i / 100.0
        x_c = x_zero + w_val * (x_debye - x_zero)
        y_c = y_bot - (w_val**2) * (y_bot - (y_top + 40))
        pts_dos_debye.append((x_c, y_c))

    d_debye_dos = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_dos_debye)
    f.append(path_svg(d_debye_dos, stroke="#059669", sw=3))
    # Вертикальна лінія зрізу на w_D
    y_debye_top = y_bot - (y_bot - (y_top + 40))
    f.append(line(x_debye, y_bot, x_debye, y_debye_top, color="#059669", sw=2, dash="4,4"))
    f.append(text(x_debye, y_bot + 18, "ω_D", size=12, bold=True, color="#059669"))
    f.append(text(x_debye - 110, y_top + 80, "Парабола Дебая: g(ω) ~ ω²", size=11, bold=True, color="#059669"))

    # Штриховка площі Дебая під параболою
    pts_fill = [(x_zero, y_bot)] + pts_dos_debye + [(x_debye, y_bot)]
    d_fill = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_fill) + " Z"
    f.append(path_svg(d_fill, fill="#d1fae5", stroke="none"))

    f.append(rect(340, 240, 240, 40, fill="#ffffff", stroke="#059669", sw=1, rx=4))
    f.append(text(460, 256, "Площа під параболою = 3N", size=10, bold=True, color="#047857"))
    f.append(text(460, 271, "(загальне число мод кристала)", size=9, color=MUTED))

    f.append(text(W / 2, H - 10, "Порівняння дельта-функціонального спектра Ейнштейна та параболічного спектра Дебая з відсічкою", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'phonon-density-of-states.svg'), W, H, "\n".join(f))

def main():
    fig_heat_capacity_curves()
    fig_lattice_modes_concept()
    fig_phonon_density_of_states()
    print("Фігури успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
