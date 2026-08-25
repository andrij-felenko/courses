# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Фундаментальні взаємодії»."""

import os
import sys
import math

# Підключаємо svgkit з кореневої теки scripts/ (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def make_fig1_comparison_scale():
    """Фігура 1: Порівняльна шкала та характеристики фундаментальних взаємодій."""
    w, h = 780, 360
    frags = []
    
    # Заголовок шкали
    frags.append(text(w / 2, 22, "Характеристики фундаментальних взаємодій", size=16, bold=True))
    
    interactions = [
        {"title": "Сильна", "color": "#c0392b", "bg": "#fdf2e9",
         "strength": "1", "radius": "~ 10⁻¹⁵ м (1 фм)", "boson": "8 ґлюонів", "mass": "0", "charge": "Колірний заряд"},
        {"title": "Електромагнітна", "color": "#2457d6", "bg": "#ebf5fb",
         "strength": "~ 1/137 (7.3·10⁻³)", "radius": "Нескінченний (∞)", "boson": "Фотон (γ)", "mass": "0", "charge": "Електричний заряд"},
        {"title": "Слабка", "color": "#8e44ad", "bg": "#f5eeed",
         "strength": "~ 10⁻⁶", "radius": "~ 10⁻¹⁸ м (0.001 фм)", "boson": "W⁺, W⁻, Z⁰ бозони", "mass": "80.4 / 91.2 ҐеВ/c²", "charge": "Слабкий ізоспін"},
        {"title": "Гравітаційна", "color": "#27ae60", "bg": "#eafaf1",
         "strength": "~ 10⁻³⁹", "radius": "Нескінченний (∞)", "boson": "Ґравітон (гіпотез.)", "mass": "0", "charge": "Маса-енергія (T_μν)"}
    ]
    
    col_w = 175
    col_gap = 14
    left_margin = (w - (4 * col_w + 3 * col_gap)) / 2
    
    for i, inter in enumerate(interactions):
        cx = left_margin + i * (col_w + col_gap) + col_w / 2
        cy_top = 50
        
        # Шапка стовпчика
        hdr_box, _, _ = textbox(cx, cy_top + 20, inter["title"], size=15, bold=True, color=inter["color"], fill=inter["bg"], stroke=inter["color"], min_w=col_w)
        frags.append(hdr_box)
        
        # Тіло параметрів
        content = [
            "Сила: " + inter["strength"],
            "Радіус: " + inter["radius"],
            "Носій: " + inter["boson"],
            "Маса носія: " + inter["mass"],
            "Джерело: " + inter["charge"]
        ]
        
        box_y = cy_top + 180
        body_text = "\n".join(content)
        t_box, _, _ = textbox(cx, box_y, body_text, size=11, fill="#ffffff", stroke="#bdc3c7", pad=8, min_w=col_w)
        frags.append(t_box)
        
        # Вертикальний покажчик
        frags.append(line(cx, cy_top + 42, cx, box_y - 65, color=inter["color"], sw=2))

    render(os.path.join(IMG_DIR, "interaction-comparison-scale.svg"), w, h, *frags)


def make_fig2_exchange_mechanism():
    """Фігура 2: Квантово-польовий механізм обміну віртуальним бозоном."""
    w, h = 740, 280
    frags = []
    
    frags.append(text(w / 2, 22, "Обмін віртуальним калібрувальним бозоном між ферміонами", size=15, bold=True))
    
    # Ліва частинка (Ферміон A)
    frags.append(line(80, 70, 220, 210, color="#2457d6", sw=3))
    frags.append(arrow(80, 70, 150, 140, color="#2457d6", sw=3))
    frags.append(text(75, 55, "Ферміон A (in)", size=13, bold=True, color="#2457d6", anchor="end"))
    frags.append(text(225, 230, "Ферміон A' (out)", size=13, bold=True, color="#2457d6", anchor="start"))
    
    # Права частинка (Ферміон B)
    frags.append(line(660, 70, 520, 210, color="#c0392b", sw=3))
    frags.append(arrow(660, 70, 590, 140, color="#c0392b", sw=3))
    frags.append(text(665, 55, "Ферміон B (in)", size=13, bold=True, color="#c0392b", anchor="start"))
    frags.append(text(515, 230, "Ферміон B' (out)", size=13, bold=True, color="#c0392b", anchor="end"))
    
    # Вузол 1 (ліворуч) та Вузол 2 (праворуч)
    frags.append(circle(150, 140, 6, fill="#16a085", stroke="#117a65", sw=2))
    frags.append(circle(590, 140, 6, fill="#16a085", stroke="#117a65", sw=2))
    
    # Хвиляста/пунктирна лінія носія (Віртуальний бозон)
    frags.append(line(156, 140, 584, 140, color="#27ae60", sw=2.5, dash="6,4"))
    
    # Написи на вузлах і бозоні
    frags.append(text(150, 118, "Вузол взаємодії (g₁)", size=12, color="#16a085", bold=True))
    frags.append(text(590, 118, "Вузол взаємодії (g₂)", size=12, color="#16a085", bold=True))
    
    # Блок характеристики проміжника
    boson_info = "Віртуальний калібрувальний бозон (маса m)\nПередача імпульсу q, амплітуда M ~ g₁g₂ / (q² - m²c²)"
    box_b, _, _ = textbox(370, 185, boson_info, size=12, fill="#e8f8f5", stroke="#27ae60", pad=8)
    frags.append(box_b)
    
    render(os.path.join(IMG_DIR, "exchange-boson-mechanism.svg"), w, h, *frags)


def make_fig3_yukawa_vs_coulomb():
    """Фігура 3: Порівняння потенціалів Юкави (масивний носій) та Кулона (безмасовий)."""
    w, h = 740, 320
    frags = []
    
    frags.append(text(w / 2, 22, "Порівняння кулонівського потенціалу та потенціалу Юкави", size=15, bold=True))
    
    # Осі координат
    ox, oy = 80, 260
    axis_w, axis_h = 600, 210
    
    frags.append(arrow(ox, oy, ox + axis_w, oy, color=INK, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - axis_h, color=INK, sw=1.5))
    
    frags.append(text(ox + axis_w - 10, oy + 25, "Відстань r (фм)", size=13, bold=True, anchor="end"))
    frags.append(text(ox - 15, oy - axis_h + 15, "Потенціал |V(r)|", size=13, bold=True, anchor="end"))
    
    # Побудова кривих
    # Coulomb: V ~ 1/r
    # Yukawa: V ~ exp(-r)/r
    pts_coulomb = []
    pts_yukawa = []
    
    for px in range(15, 540, 5):
        r = px / 80.0  # умовна відстань
        v_coul = 1.8 / (r + 0.2)
        v_yuk = (1.8 / (r + 0.2)) * math.exp(-1.4 * r)
        
        x_screen = ox + px
        y_coul = oy - min(v_coul * 75, axis_h - 20)
        y_yuk = oy - min(v_yuk * 75, axis_h - 20)
        
        pts_coulomb.append("%.1f,%.1f" % (x_screen, y_coul))
        pts_yukawa.append("%.1f,%.1f" % (x_screen, y_yuk))
    
    frags.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.5" stroke-dasharray="6,4"/>' % " ".join(pts_coulomb))
    frags.append('<polyline points="%s" fill="none" stroke="#c0392b" stroke-width="3"/>' % " ".join(pts_yukawa))
    
    # Позначення радіуса дії Юкави r_0 = 1/μ
    r0_px = ox + 80  # r = 1.0 фм
    frags.append(line(r0_px, oy, r0_px, oy - 120, color="#8e44ad", sw=1.5, dash="4,4"))
    frags.append(text(r0_px, oy + 20, "r₀ = ħ / (m c)", size=12, bold=True, color="#8e44ad"))
    
    # Легенда
    leg_box, _, _ = textbox(ox + 380, oy - 140, "— Потенціал Юкави: V(r) ~ -e^{-μr} / r (експоненційне загасання)\n- - Кулонівський потенціал: V(r) ~ -1 / r (нескінченний радіус)", size=11, fill="#f9f9f9", stroke="#bdc3c7", pad=8)
    frags.append(leg_box)
    
    render(os.path.join(IMG_DIR, "yukawa-vs-coulomb-potential.svg"), w, h, *frags)


def make_fig4_running_couplings():
    """Фігура 4: Залежність констант зв'язку від енергії (Running Couplings) та GUT."""
    w, h = 740, 340
    frags = []
    
    frags.append(text(w / 2, 22, "Еволюція констант зв'язку та Велике об'єднання (GUT)", size=15, bold=True))
    
    ox, oy = 80, 280
    axis_w, axis_h = 600, 230
    
    frags.append(arrow(ox, oy, ox + axis_w, oy, color=INK, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - axis_h, color=INK, sw=1.5))
    
    frags.append(text(ox + axis_w - 10, oy + 25, "Масштаб енергії Q (ҐеВ, логарифмічна шкала)", size=12, bold=True, anchor="end"))
    frags.append(text(ox - 15, oy - axis_h + 15, "1 / α_i (Обернена константа зв'язку)", size=12, bold=True, anchor="end"))
    
    # Шкала енергій (10^2, 10^16 GeV)
    frags.append(line(ox + 50, oy - 4, ox + 50, oy + 4, color=INK, sw=1.5))
    frags.append(text(ox + 50, oy + 20, "10² (M_Z)", size=11))
    
    gut_x = ox + 480
    frags.append(line(gut_x, oy - 4, gut_x, oy + 4, color=INK, sw=1.5))
    frags.append(text(gut_x, oy + 20, "10¹⁶ (GUT)", size=11, bold=True, color="#8e44ad"))
    
    # Криві 1/alpha
    # alpha_1 (U(1)): 1/alpha зростає -> спадає з енергією
    # alpha_2 (SU(2)): помірно зростає
    # alpha_3 (SU(3)): асимптотична свобода -> 1/alpha сильно зростає (константа alpha спадає)
    
    # P1 (U1): від (ox+50, oy-40) до (gut_x, oy-180)
    frags.append(line(ox + 50, oy - 40, gut_x, oy - 180, color="#2457d6", sw=2.5))
    frags.append(text(ox + 120, oy - 40, "1/α₁ (U(1) hypercharge)", size=11, color="#2457d6", bold=True))
    
    # P2 (SU2): від (ox+50, oy-100) до (gut_x, oy-180)
    frags.append(line(ox + 50, oy - 100, gut_x, oy - 180, color="#8e44ad", sw=2.5))
    frags.append(text(ox + 120, oy - 110, "1/α₂ (SU(2) weak)", size=11, color="#8e44ad", bold=True))
    
    # P3 (SU3): від (ox+50, oy-200) до (gut_x, oy-180)
    frags.append(line(ox + 50, oy - 200, gut_x, oy - 180, color="#c0392b", sw=2.5))
    frags.append(text(ox + 120, oy - 215, "1/α₃ (SU(3) strong / QCD)", size=11, color="#c0392b", bold=True))
    
    # Точка об'єднання GUT
    frags.append(circle(gut_x, oy - 180, 7, fill="#f1c40f", stroke="#b7950b", sw=2))
    frags.append(line(gut_x, oy, gut_x, oy - 180, color="#8e44ad", sw=1.5, dash="4,4"))
    
    gut_text = "Точка Великого об'єднання (GUT)\nE ~ 10¹⁶ ҐеВ, α_GUT ≈ 1/40"
    box_gut, _, _ = textbox(gut_x - 40, oy - 220, gut_text, size=11, fill="#fef9e7", stroke="#f1c40f", pad=6)
    frags.append(box_gut)
    
    render(os.path.join(IMG_DIR, "running-coupling-constants.svg"), w, h, *frags)


if __name__ == "__main__":
    make_fig1_comparison_scale()
    make_fig2_exchange_mechanism()
    make_fig3_yukawa_vs_coulomb()
    make_fig4_running_couplings()
    print("Всі SVG-фігури успішно згенеровано у", IMG_DIR)
