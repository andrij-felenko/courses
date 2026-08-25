# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/condensed-matter-physics/matthiessens-rule/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. Resistivity vs Temperature for various impurity levels
def gen_resistivity_vs_temperature():
    w, h = 700, 440
    frags = []
    
    # Title
    frags.append(text(w / 2, 28, "Температурна залежність питомого опору металів різної чистоти", size=16, bold=True))
    
    # Axes
    ox, oy = 90, 350
    ax_w, ax_h = 540, 270
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    # Axis labels
    frags.append(text(ox + ax_w / 2, oy + 44, "Температура T (К)", size=13, bold=True))
    frags.append(text(ox - 65, oy - ax_h / 2, "Питомий опір ρ", size=13, bold=True, anchor="middle"))
    
    # Temperature ticks & grid
    frags.append(line(ox + 40, oy, ox + 40, oy + 6, color=MUTED))
    frags.append(text(ox + 40, oy + 22, "0 K", size=11, color=MUTED))
    
    frags.append(line(ox + 160, oy, ox + 160, oy + 6, color=MUTED))
    frags.append(text(ox + 160, oy + 22, "T ≪ Θ_D (T⁵)", size=11, color=MUTED))
    
    frags.append(line(ox + 380, oy, ox + 380, oy + 6, color=MUTED))
    frags.append(text(ox + 380, oy + 22, "T ~ Θ_D", size=11, color=MUTED))
    
    frags.append(line(ox + 500, oy, ox + 500, oy + 6, color=MUTED))
    frags.append(text(ox + 500, oy + 22, "T ≫ Θ_D (лінійний)", size=11, color=MUTED))

    # Base phonon curve
    pts1 = [
        (ox, oy - 10),
        (ox + 60, oy - 11),
        (ox + 120, oy - 25),
        (ox + 180, oy - 65),
        (ox + 260, oy - 120),
        (ox + 360, oy - 175),
        (ox + 500, oy - 245)
    ]
    path_d1 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts1)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d1, POS))
    frags.append(text(ox + 508, oy - 245, "Чистий метал (c = 0)", size=11, color=POS, bold=True, anchor="start"))

    # Curve 2: Low impurity (c1)
    offset2 = 45
    pts2 = [(x, y - offset2) for x, y in pts1]
    path_d2 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts2)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d2, FIELD))
    frags.append(text(ox + 508, oy - 245 - offset2, "Сплав c₁ (низька домішка)", size=11, color=FIELD, bold=True, anchor="start"))

    # Curve 3: High impurity (c2)
    offset3 = 95
    pts3 = [(x, y - offset3) for x, y in pts1]
    path_d3 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts3)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d3, NEG))
    frags.append(text(ox + 508, oy - 245 - offset3, "Сплав c₂ > c₁ (висока домішка)", size=11, color=NEG, bold=True, anchor="start"))

    # Residual resistivity ticks and annotations on y-axis
    frags.append(line(ox - 5, oy - 10 - offset2, ox, oy - 10 - offset2, color=FIELD, sw=2))
    frags.append(text(ox - 12, oy - 10 - offset2, "ρ₀(c₁)", size=11, color=FIELD, bold=True, anchor="end"))

    frags.append(line(ox - 5, oy - 10 - offset3, ox, oy - 10 - offset3, color=NEG, sw=2))
    frags.append(text(ox - 12, oy - 10 - offset3, "ρ₀(c₂)", size=11, color=NEG, bold=True, anchor="end"))

    # Dashed line showing constant shift
    frags.append(line(ox + 260, oy - 120 - offset3, ox + 260, oy - 120, color="#7f8c8d", sw=1.5, dash="4,4"))

    # Explanatory Callout Boxes
    frags.append(textbox(ox + 120, oy - 190, "Область T → 0 K:\nρ(T) → ρ₀ = const\nРозсіяння лише на домішках", size=10, fill="#f8f9f9", stroke="#7f8c8d")[0])
    frags.append(textbox(ox + 370, oy - 50, "Область T ≫ Θ_D:\nρ_ph(T) ∝ T\nФононне розсіяння домінує", size=10, fill="#f8f9f9", stroke="#7f8c8d")[0])

    render(os.path.join(img_dir, "resistivity-vs-temperature.svg"), w, h, *frags)


# 2. Scattering Mechanisms Addition
def gen_scattering_mechanisms_addition():
    w, h = 680, 420
    frags = []
    
    frags.append(text(w / 2, 28, "Схема адитивності швидкостей розсіяння електронів", size=16, bold=True))

    # Left Box: Static Impurity Scattering
    b1_x, b1_y, b1_w, b1_h = 40, 70, 270, 160
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#ebf5fb", stroke=FIELD, sw=2, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 25, "1. Статичні дефекти (домішки)", size=13, color=FIELD, bold=True))
    frags.append(text(b1_x + 15, b1_y + 55, "• Точкові домішки, вакансії", size=11, anchor="start"))
    frags.append(text(b1_x + 15, b1_y + 80, "• Пружне розсіяння (без зміни Е)", size=11, anchor="start"))
    frags.append(text(b1_x + 15, b1_y + 105, "• Не залежить від температури", size=11, anchor="start"))
    frags.append(text(b1_x + b1_w / 2, b1_y + 140, "Швидкість розсіяння: 1 / τ_imp", size=12, color=FIELD, bold=True))

    # Right Box: Dynamic Phonon Scattering
    b2_x, b2_y, b2_w, b2_h = 370, 70, 270, 160
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fef9e7", stroke=POS, sw=2, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 25, "2. Динамічні коливання (фонони)", size=13, color=POS, bold=True))
    frags.append(text(b2_x + 15, b2_y + 55, "• Теплові коливання ґратки", size=11, anchor="start"))
    frags.append(text(b2_x + 15, b2_y + 80, "• Непружне розсіяння носіїв", size=11, anchor="start"))
    frags.append(text(b2_x + 15, b2_y + 105, "• Температурна залежність τ_ph(T)", size=11, anchor="start"))
    frags.append(text(b2_x + b2_w / 2, b2_y + 140, "Швидкість розсіяння: 1 / τ_ph(T)", size=12, color=POS, bold=True))

    # Connecting lines down to Central Combination Box
    frags.append(line(b1_x + b1_w / 2, b1_y + b1_h, b1_x + b1_w / 2, b1_y + b1_h + 35, color=LINE, sw=2))
    frags.append(line(b2_x + b2_w / 2, b2_y + b2_h, b2_x + b2_w / 2, b2_y + b2_h + 35, color=LINE, sw=2))
    
    frags.append(line(b1_x + b1_w / 2, b1_y + b1_h + 35, w / 2, b1_y + b1_h + 35, color=LINE, sw=2))
    frags.append(line(b2_x + b2_w / 2, b2_y + b2_h + 35, w / 2, b2_y + b2_h + 35, color=LINE, sw=2))
    frags.append(line(w / 2, b1_y + b1_h + 35, w / 2, b1_y + b1_h + 55, color=LINE, sw=2))

    # Bottom Central Box: Matthiessen Rule Sum
    b3_x, b3_y, b3_w, b3_h = 100, 290, 480, 115
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f4f6f7", stroke=LINE, sw=2, rx=8))
    frags.append(text(w / 2, b3_y + 25, "Правило Матіссена (адитивність імовірностей)", size=14, bold=True))
    frags.append(text(w / 2, b3_y + 55, "1 / τ = 1 / τ_imp + 1 / τ_ph(T)", size=15, color=NEG, bold=True))
    frags.append(text(w / 2, b3_y + 88, "Питомий опір:  ρ(T) = (m* / n e²) · (1/τ) = ρ₀ + ρ_ph(T)", size=12, color=LINE, bold=True))

    render(os.path.join(img_dir, "scattering-mechanisms-addition.svg"), w, h, *frags)


# 3. Deviations from Matthiessen's Rule
def gen_matthiessen_deviations():
    w, h = 680, 410
    frags = []
    
    frags.append(text(w / 2, 28, "Причини відхилень від правила Матіссена (DMR)", size=16, bold=True))

    box_w, box_h = 195, 290
    y_top = 75

    # Panel 1: Anisotropy
    x1 = 30
    frags.append(rect(x1, y_top, box_w, box_h, fill="#fcf3cf", stroke="#f39c12", sw=2, rx=6))
    frags.append(text(x1 + box_w / 2, y_top + 25, "1. Анізотропія", size=13, color="#b9770e", bold=True))
    frags.append(text(x1 + box_w / 2, y_top + 45, "поверхні Фермі", size=13, color="#b9770e", bold=True))
    frags.append(line(x1 + 15, y_top + 60, x1 + box_w - 15, y_top + 60, color="#f39c12", sw=1))
    
    frags.append(text(x1 + 12, y_top + 85, "• Різні ділянки к-простору", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 105, "  мають різну кутову", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 125, "  інтенсивність розсіяння", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 150, "• Фонони й домішки", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 170, "  перерозподіляють", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 190, "  функцію розподілу", size=10, anchor="start"))
    frags.append(text(x1 + 12, y_top + 220, "Варіаційний принцип", size=10, bold=True, anchor="start"))
    frags.append(text(x1 + 12, y_top + 240, "Колера: Δρ > 0", size=11, color="#b9770e", bold=True, anchor="start"))

    # Panel 2: Two-band conduction
    x2 = 242
    frags.append(rect(x2, y_top, box_w, box_h, fill="#e8f8f5", stroke="#16a085", sw=2, rx=6))
    frags.append(text(x2 + box_w / 2, y_top + 25, "2. Двозонна", size=13, color="#117864", bold=True))
    frags.append(text(x2 + box_w / 2, y_top + 45, "провідність", size=13, color="#117864", bold=True))
    frags.append(line(x2 + 15, y_top + 60, x2 + box_w - 15, y_top + 60, color="#16a085", sw=1))
    
    frags.append(text(x2 + 12, y_top + 85, "• Паралельні канали:", size=10, anchor="start"))
    frags.append(text(x2 + 12, y_top + 105, "  s-зоні та d-зоні металу", size=10, anchor="start"))
    frags.append(text(x2 + 12, y_top + 130, "• Додаються провідності", size=10, anchor="start"))
    frags.append(text(x2 + 12, y_top + 150, "  σ = σ_s + σ_d , а не", size=10, anchor="start"))
    frags.append(text(x2 + 12, y_top + 170, "  питомі опори ρ!", size=10, anchor="start"))
    frags.append(text(x2 + 12, y_top + 200, "Формула Зондгаймера:", size=10, bold=True, anchor="start"))
    frags.append(text(x2 + 12, y_top + 225, "ρ = ρ₁ ρ₂ / (ρ₁ + ρ₂)", size=10, color="#117864", bold=True, anchor="start"))
    frags.append(text(x2 + 12, y_top + 245, "порушує адитивність", size=10, italic=True, anchor="start"))

    # Panel 3: Interference / Kagan-Zhernov
    x3 = 454
    frags.append(rect(x3, y_top, box_w, box_h, fill="#fadbd8", stroke="#e74c3c", sw=2, rx=6))
    frags.append(text(x3 + box_w / 2, y_top + 25, "3. Інтерференція", size=13, color="#c0392b", bold=True))
    frags.append(text(x3 + box_w / 2, y_top + 45, "(Каган–Жернов)", size=13, color="#c0392b", bold=True))
    frags.append(line(x3 + 15, y_top + 60, x3 + box_w - 15, y_top + 60, color="#e74c3c", sw=1))
    
    frags.append(text(x3 + 12, y_top + 85, "• Електрон-фонон-домішкове", size=10, anchor="start"))
    frags.append(text(x3 + 12, y_top + 105, "  зв'язування", size=10, anchor="start"))
    frags.append(text(x3 + 12, y_top + 130, "• Важкі домішки змінюють", size=10, anchor="start"))
    frags.append(text(x3 + 12, y_top + 150, "  коливальний спектр", size=10, anchor="start"))
    frags.append(text(x3 + 12, y_top + 170, "  (квазілокальні моди)", size=10, anchor="start"))
    frags.append(text(x3 + 12, y_top + 200, "Температурний член:", size=10, bold=True, anchor="start"))
    frags.append(text(x3 + 12, y_top + 225, "Δρ(T, c) ∝ c · T⁵", size=11, color="#c0392b", bold=True, anchor="start"))
    frags.append(text(x3 + 12, y_top + 245, "неадитивний внесок", size=10, italic=True, anchor="start"))

    render(os.path.join(img_dir, "matthiessen-deviations.svg"), w, h, *frags)


if __name__ == "__main__":
    gen_resistivity_vs_temperature()
    gen_scattering_mechanisms_addition()
    gen_matthiessen_deviations()
    print("Generated 3 SVG figures successfully.")
