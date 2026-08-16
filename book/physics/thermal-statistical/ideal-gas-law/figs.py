# -*- coding: utf-8 -*-
"""Фігури для теми «Рівняння стану ідеального газу» (book/physics/thermal-statistical/ideal-gas-law)."""
import sys, os
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

def polyline(pts, color="#333333", sw=1.5, fill="none"):
    pts_str = " ".join("%g,%g" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, color, sw)

def fig_microscopic_pressure():
    """microscopic-pressure.svg: Мікроскопічна модель тиску: пружні удари молекул об стінку посудини та передача імпульсу."""
    W, H = 880, 420
    frags = []

    # Загальне тло
    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Мікроскопічна природа тиску: хаотичний рух частинок та удари об стінки", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Посудина з молекулами газу
    frags.append(rect(30, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(230, 78, "Хаотичний тепловий рух газу в об'ємі V", size=13, bold=True, color=BLUE_S))

    # Молекули в об'ємі (кульки з векторами швидкостей)
    particles = [
        (80, 140, 15, -10, "#2563eb"),
        (150, 220, -12, 18, "#2563eb"),
        (120, 310, 18, 8, "#2563eb"),
        (220, 150, -8, -14, "#2563eb"),
        (260, 280, 14, -12, "#2563eb"),
        (310, 120, -18, 10, "#2563eb"),
        (350, 230, -10, -15, "#2563eb"),
        (190, 230, 20, -5, "#dc2626"),  # молекула біля стінки
    ]

    for px, py, vx, vy, color in particles:
        frags.append(circle(px, py, 7, fill=color, stroke="#1e293b", sw=1))
        # Вектор швидкості
        frags.append(line(px, py, px + vx, py + vy, color=color, sw=1.8))
        # Накінечник стрілки
        frags.append(circle(px + vx, py + vy, 2, fill=color, stroke=color, sw=1))

    # Стінка посудини з правого боку лівої панелі
    frags.append(rect(410, 55, 20, 340, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    frags.append(text(420, 225, "С Т І Н К А", size=11, bold=True, color="#475569", anchor="middle"))

    # Підпис під лівою панеллю
    frags.append(text(230, 375, "N молекул масою m₀, концентрація nᵥ = N / V", size=11, italic=True, color="#475569"))

    # Права панель: Удар однієї молекули об стінку (деталізація передачі імпульсу)
    frags.append(rect(450, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(650, 78, "Пружне відбивання: зміна імпульсу Δpₓ", size=13, bold=True, color=RED_S))

    # Стінка на правій панелі
    frags.append(rect(800, 95, 35, 270, fill="#cbd5e1", stroke="#475569", sw=2))

    # Початкова молекула (рух до стінки)
    frags.append(circle(560, 160, 10, fill=BLUE_S, stroke="#1e293b", sw=1.5))
    frags.append(text(560, 138, "Падаюча: v⃗ = (vₓ, vᵧ)", size=11, bold=True, color=BLUE_S))
    frags.append(line(560, 160, 785, 230, color=BLUE_S, sw=2.5))
    # Стрілка налітання
    frags.append(line(765, 224, 785, 230, color=BLUE_S, sw=2.5))
    frags.append(line(770, 212, 785, 230, color=BLUE_S, sw=2.5))

    # Точка удару
    frags.append(circle(790, 231, 5, fill=RED_S, stroke=RED_S, sw=1))

    # Відбита молекула (рух від стінки)
    frags.append(circle(560, 300, 10, fill=GREEN_S, stroke="#1e293b", sw=1.5))
    frags.append(text(560, 325, "Відбита: v⃗' = (-vₓ, vᵧ)", size=11, bold=True, color=GREEN_S))
    frags.append(line(790, 231, 560, 300, color=GREEN_S, sw=2.5))
    # Стрілка відльоту
    frags.append(line(580, 294, 560, 300, color=GREEN_S, sw=2.5))
    frags.append(line(575, 282, 560, 300, color=GREEN_S, sw=2.5))

    # Формула передачі імпульсу та тиску
    b_formula, _, _ = textbox(650, 230, "Δpₓ = m₀vₓ - (-m₀vₓ) = 2 m₀vₓ\nF_ст = Δp / Δt = 2 m₀vₓ² / (2L)\nТиск P = F / A = ⅓ nᵥ m₀ ⟨v²⟩", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_formula)

    render(os.path.join(IMG, "microscopic-pressure.svg"), W, H, *frags)


def fig_pvt_surface():
    """pvt-surface.svg: Графіки трьох часткових газових законів (ізопроцеси): ізотерми, ізобари, ізохори."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Ізопроцеси ідеального газу: P-V, V-T та P-T діаграми", size=16, bold=True, color="#1e293b"))

    # Спліт 1: Ізотерми P-V (Закон Бойля — Маріотта)
    frags.append(rect(25, 55, 265, 295, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(157, 75, "Ізотерми (T = const)", size=12, bold=True, color=BLUE_S))
    frags.append(text(157, 92, "P ∝ 1 / V  (P·V = const)", size=10, italic=True, color="#475569"))

    # Осі P-V
    frags.append(line(50, 310, 260, 310, color="#475569", sw=1.5)) # V
    frags.append(line(50, 310, 50, 105, color="#475569", sw=1.5))  # P
    frags.append(text(265, 314, "V", size=11, bold=True, color="#1e293b"))
    frags.append(text(46, 100, "P", size=11, bold=True, color="#1e293b"))

    # Гіперболи P = C/V
    pts_t1 = [(60, 300), (70, 250), (90, 195), (120, 160), (160, 140), (220, 128)]
    frags.append(polyline(pts_t1, color=BLUE_S, sw=2, fill="none"))
    frags.append(text(225, 125, "T₁", size=10, bold=True, color=BLUE_S))

    pts_t2 = [(70, 300), (85, 230), (110, 175), (150, 140), (200, 120), (245, 110)]
    frags.append(polyline(pts_t2, color=GREEN_S, sw=2, fill="none"))
    frags.append(text(250, 108, "T₂ > T₁", size=10, bold=True, color=GREEN_S))

    # Спліт 2: Ізобари V-T (Закон Гей-Люссака)
    frags.append(rect(307, 55, 265, 295, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(440, 75, "Ізобари (P = const)", size=12, bold=True, color=GREEN_S))
    frags.append(text(440, 92, "V ∝ T  (V / T = const)", size=10, italic=True, color="#475569"))

    # Осі V-T
    frags.append(line(330, 310, 540, 310, color="#475569", sw=1.5)) # T
    frags.append(line(330, 310, 330, 105, color="#475569", sw=1.5)) # V
    frags.append(text(545, 314, "T", size=11, bold=True, color="#1e293b"))
    frags.append(text(326, 100, "V", size=11, bold=True, color="#1e293b"))

    # Прямі через початок координат V = k*T
    frags.append(line(330, 310, 530, 130, color=GREEN_S, sw=2))
    frags.append(text(535, 130, "P₁", size=10, bold=True, color=GREEN_S))

    frags.append(line(330, 310, 530, 190, color=RED_S, sw=2))
    frags.append(text(535, 190, "P₂ > P₁", size=10, bold=True, color=RED_S))

    # Пунктирна екстраполяція до 0 K
    frags.append(line(330, 310, 315, 323, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(315, 335, "0 K", size=9, color="#64748b"))

    # Спліт 3: Ізохори P-T (Закон Шарля)
    frags.append(rect(590, 55, 265, 295, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(722, 75, "Ізохори (V = const)", size=12, bold=True, color=AMBER_S))
    frags.append(text(722, 92, "P ∝ T  (P / T = const)", size=10, italic=True, color="#475569"))

    # Осі P-T
    frags.append(line(610, 310, 820, 310, color="#475569", sw=1.5)) # T
    frags.append(line(610, 310, 610, 105, color="#475569", sw=1.5)) # P
    frags.append(text(825, 314, "T", size=11, bold=True, color="#1e293b"))
    frags.append(text(606, 100, "P", size=11, bold=True, color="#1e293b"))

    # Прямі через початок координат P = k*T
    frags.append(line(610, 310, 810, 120, color=AMBER_S, sw=2))
    frags.append(text(815, 120, "V₁", size=10, bold=True, color=AMBER_S))

    frags.append(line(610, 310, 810, 180, color=PURPLE_S, sw=2))
    frags.append(text(815, 180, "V₂ > V₁", size=10, bold=True, color=PURPLE_S))

    # Пунктир до 0 K
    frags.append(line(610, 310, 595, 323, color="#94a3b8", sw=1, dash="3,3"))

    render(os.path.join(IMG, "pvt-surface.svg"), W, H, *frags)


def fig_compressibility_z():
    """compressibility-z.svg: Коефіцієнт стисливості Z = PV / (nRT) реальних газів та відхилення від ідеальної моделі."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Коефіцієнт стисливості Z = PV / (nRT) для реальних газів при 300 K", size=16, bold=True, color="#1e293b"))

    # Поле графіку
    frags.append(rect(80, 55, 750, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))

    # Осі
    frags.append(line(80, 355, 830, 355, color="#475569", sw=1.5)) # P
    frags.append(line(80, 355, 80, 55, color="#475569", sw=1.5))   # Z

    frags.append(text(455, 390, "Тиск P (МПа)", size=12, bold=True, color="#1e293b"))
    frags.append(text(45, 205, "Z = PV / nRT", size=12, bold=True, color="#1e293b", anchor="middle"))

    # Поділки Y (Z = 0.5, 1.0, 1.5)
    frags.append(line(75, 305, 80, 305, color="#475569", sw=1))
    frags.append(text(65, 309, "0.5", size=10, color="#475569"))

    frags.append(line(75, 205, 80, 205, color="#475569", sw=1))
    frags.append(text(65, 209, "1.0", size=10, bold=True, color="#1e293b"))

    frags.append(line(75, 105, 80, 105, color="#475569", sw=1))
    frags.append(text(65, 109, "1.5", size=10, color="#475569"))

    # Еталонна лінія Ідеального Газу Z = 1
    frags.append(line(80, 205, 830, 205, color=GREEN_S, sw=2, dash="6,4"))
    frags.append(text(710, 195, "Ідеальний газ (Z = 1)", size=11, bold=True, color=GREEN_S))

    # Крива N2 (Азот)
    pts_n2 = [(80, 205), (140, 218), (220, 225), (320, 215), (450, 180), (600, 130), (780, 75)]
    frags.append(polyline(pts_n2, color=BLUE_S, sw=2.2, fill="none"))
    frags.append(text(785, 75, "N₂ (Азот)", size=11, bold=True, color=BLUE_S))

    # Крива CO2 (Вуглекислий газ)
    pts_co2 = [(80, 205), (120, 250), (180, 315), (240, 330), (300, 290), (420, 190), (580, 95)]
    frags.append(polyline(pts_co2, color=RED_S, sw=2.2, fill="none"))
    frags.append(text(585, 95, "CO₂", size=11, bold=True, color=RED_S))

    # Крива H2 (Водень)
    pts_h2 = [(80, 205), (180, 195), (320, 178), (500, 150), (700, 115), (820, 95)]
    frags.append(polyline(pts_h2, color=PURPLE_S, sw=2.2, fill="none"))
    frags.append(text(825, 95, "H₂", size=11, bold=True, color=PURPLE_S))

    # Пояснювальні блоки двох режимів відхилень у вільних областях
    b_attract, _, _ = textbox(240, 280, "Z < 1: переважає притягання між молекулами\n(поправка 'a' у рівнянні Ван дер Ваальса)", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_attract)

    b_repul, _, _ = textbox(660, 280, "Z > 1: переважає власний об'єм молекул 'b'\n(нестисливість частинок при високому тиску)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_repul)

    render(os.path.join(IMG, "compressibility-z.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_microscopic_pressure()
    fig_pvt_surface()
    fig_compressibility_z()
    print("Успішно згенеровано фігури для ideal-gas-law.")
