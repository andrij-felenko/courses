# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/condensed-matter-physics/carrier-mobility/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. Mobility vs Temperature
def gen_mobility_vs_temperature():
    w, h = 660, 420
    frags = []
    
    # Title
    frags.append(text(w / 2, 28, "Залежність рухливості носіїв від температури та допування", size=16, bold=True))
    
    # Axes
    ox, oy = 80, 340
    ax_w, ax_h = 520, 270
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    # Axis labels
    frags.append(text(ox + ax_w / 2, oy + 42, "Температура T (К)", size=13, bold=True))
    frags.append(text(ox - 50, oy - ax_h / 2, "Рухливість μ", size=13, bold=True, anchor="middle"))
    
    # T ticks
    frags.append(line(ox + 60, oy, ox + 60, oy + 5, color=MUTED))
    frags.append(text(ox + 60, oy + 20, "20 K", size=11, color=MUTED))
    frags.append(line(ox + 220, oy, ox + 220, oy + 5, color=MUTED))
    frags.append(text(ox + 220, oy + 20, "100 K", size=11, color=MUTED))
    frags.append(line(ox + 440, oy, ox + 440, oy + 5, color=MUTED))
    frags.append(text(ox + 440, oy + 20, "300 K", size=11, color=MUTED))
    
    # Grid lines / dashed slopes
    # Asymptote T^3/2 slope
    frags.append(line(ox + 40, oy - 60, ox + 180, oy - 230, color="#bdc3c7", sw=1.5, dash="4,4"))
    frags.append(text(ox + 65, oy - 190, "μ ∝ T³ᐟ² (домішки)", size=11, color=POS, italic=True))
    
    # Asymptote T^-3/2 slope
    frags.append(line(ox + 240, oy - 230, ox + 480, oy - 70, color="#bdc3c7", sw=1.5, dash="4,4"))
    frags.append(text(ox + 390, oy - 180, "μ ∝ T⁻³ᐟ² (фонони)", size=11, color=NEG, italic=True))
    
    # Curve 1: Low Doping (Nd = 10^14 cm^-3) - high peak
    pts1 = [(ox + 30, oy - 40), (ox + 80, oy - 130), (ox + 160, oy - 245), (ox + 240, oy - 230), (ox + 350, oy - 140), (ox + 480, oy - 65)]
    path_d1 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts1)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d1, POS))
    frags.append(text(ox + 165, oy - 255, "N_d = 10¹⁴ см⁻³", size=11, color=POS, bold=True))
    
    # Curve 2: Medium Doping (Nd = 10^16 cm^-3) - medium peak
    pts2 = [(ox + 30, oy - 30), (ox + 90, oy - 85), (ox + 180, oy - 170), (ox + 260, oy - 175), (ox + 350, oy - 125), (ox + 480, oy - 62)]
    path_d2 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts2)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d2, FIELD))
    frags.append(text(ox + 270, oy - 185, "N_d = 10¹⁶ см⁻³", size=11, color=FIELD, bold=True))

    # Curve 3: High Doping (Nd = 10^18 cm^-3) - low peak
    pts3 = [(ox + 30, oy - 20), (ox + 100, oy - 50), (ox + 200, oy - 95), (ox + 290, oy - 110), (ox + 370, oy - 95), (ox + 480, oy - 55)]
    path_d3 = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts3)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d3, NEG))
    frags.append(text(ox + 300, oy - 120, "N_d = 10¹⁸ см⁻³", size=11, color=NEG, bold=True))

    # Explanatory Callout Boxes
    frags.append(textbox(150, 100, "Область низьких T:\nРозсіяння на іонізованих домішках\nповільні носії сильніше відхиляються", size=10, fill="#fdfefe", stroke=POS)[0])
    frags.append(textbox(510, 100, "Область високих T:\nРозсіяння на акустичних фононах\nінтенсивні коливання ґратки", size=10, fill="#fdfefe", stroke=NEG)[0])

    render(os.path.join(img_dir, "mobility-vs-temperature.svg"), w, h, *frags)

# 2. Velocity vs Electric Field
def gen_velocity_vs_electric_field():
    w, h = 660, 400
    frags = []
    
    frags.append(text(w / 2, 28, "Дрейфова швидкість носіїв у сильних електричних полях", size=16, bold=True))
    
    ox, oy = 80, 320
    ax_w, ax_h = 530, 240
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    frags.append(text(ox + ax_w / 2, oy + 42, "Електричне поле E (В/см)", size=13, bold=True))
    frags.append(text(ox - 50, oy - ax_h / 2, "Швидкість v_d (10⁷ см/с)", size=13, bold=True, anchor="middle"))
    
    # Saturation line
    frags.append(line(ox, oy - 180, ox + ax_w, oy - 180, color="#bdc3c7", sw=1.5, dash="5,5"))
    frags.append(text(ox + ax_w - 70, oy - 190, "v_sat ≈ 10⁷ см/с (Si)", size=11, color=MUTED, italic=True))
    
    # Linear Ohmic slope line
    frags.append(line(ox, oy, ox + 140, oy - 230, color="#bdc3c7", sw=1.2, dash="3,3"))
    frags.append(text(ox + 40, oy - 140, "v_d = μ₀·E (Ом)", size=11, color=MUTED, italic=True))
    
    # Silicon electrons (sub-linear saturation)
    pts_si_e = [(ox, oy), (ox + 50, oy - 80), (ox + 100, oy - 135), (ox + 160, oy - 165), (ox + 260, oy - 177), (ox + 400, oy - 180), (ox + 510, oy - 180)]
    path_si_e = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts_si_e)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_si_e, POS))
    frags.append(text(ox + 280, oy - 192, "Кремній (електрони)", size=11, color=POS, bold=True))
    
    # GaAs electrons (Negative Differential Mobility peak)
    pts_gaas = [(ox, oy), (ox + 40, oy - 90), (ox + 80, oy - 195), (ox + 120, oy - 220), (ox + 180, oy - 170), (ox + 280, oy - 150), (ox + 510, oy - 148)]
    path_gaas = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts_gaas)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_gaas, NEG))
    frags.append(text(ox + 125, oy - 232, "GaAs (пик NDM)", size=11, color=NEG, bold=True))
    
    # Silicon holes
    pts_si_h = [(ox, oy), (ox + 80, oy - 60), (ox + 160, oy - 105), (ox + 260, oy - 130), (ox + 400, oy - 142), (ox + 510, oy - 145)]
    path_si_h = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts_si_h)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_si_h, FIELD))
    frags.append(text(ox + 350, oy - 128, "Кремній (дірки)", size=11, color=FIELD, bold=True))

    # Annotations
    frags.append(textbox(150, 80, "Омічна область:\nμ = const, v_d ∝ E", size=10, fill="#fdfefe", stroke=MUTED)[0])
    frags.append(textbox(500, 80, "Область насичення:\nвипромінювання оптичних фононів\nv_d → v_sat", size=10, fill="#fdfefe", stroke=POS)[0])

    render(os.path.join(img_dir, "velocity-vs-electric-field.svg"), w, h, *frags)

# 3. Matthiessen Scattering Schematic
def gen_matthiessen_scattering_schematic():
    w, h = 660, 360
    frags = []
    
    frags.append(text(w / 2, 26, "Механізми розсіяння та додавання ймовірностей (правило Маттіссена)", size=15, bold=True))
    
    # Left box: Electron Wave packet
    frags.append(textbox(90, 160, "Вхідний носій\n(електрон, імпульс p)", size=12, fill="#eaf0fd", stroke=NEG, bold=True)[0])
    frags.append(arrow(155, 160, 210, 160, color=NEG, sw=2))
    
    # Middle: Scattering Channels (3 parallel boxes)
    # Channel 1: Phonons
    frags.append(rect(210, 60, 260, 60, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(340, 83, "Теплові коливання ґратки", size=12, color=POS, bold=True))
    frags.append(text(340, 103, "Частота розсіяння 1/τ_ph", size=11, color=INK))
    
    # Channel 2: Ionized Impurities
    frags.append(rect(210, 130, 260, 60, fill="#eafaf1", stroke=FIELD, sw=1.5))
    frags.append(text(340, 153, "Іонізовані домішки (N_d⁺, N_a⁻)", size=12, color=FIELD, bold=True))
    frags.append(text(340, 173, "Частота розсіяння 1/τ_imp", size=11, color=INK))

    # Channel 3: Surface / Defects
    frags.append(rect(210, 200, 260, 60, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(340, 223, "Дефекти та шорсткість межі", size=12, color=LINE, bold=True))
    frags.append(text(340, 243, "Частота розсіяння 1/τ_sr", size=11, color=INK))
    
    # Arrows entering channels
    frags.append(arrow(180, 160, 210, 90, color=LINE, sw=1.5))
    frags.append(arrow(180, 160, 210, 160, color=LINE, sw=1.5))
    frags.append(arrow(180, 160, 210, 230, color=LINE, sw=1.5))
    
    # Arrows leaving channels
    frags.append(arrow(470, 90, 500, 160, color=LINE, sw=1.5))
    frags.append(arrow(470, 160, 500, 160, color=LINE, sw=1.5))
    frags.append(arrow(470, 230, 500, 160, color=LINE, sw=1.5))
    
    # Right box: Resulting mobility
    frags.append(textbox(570, 160, "Підсумковий релаксований\nстан носія", size=11, fill="#f9f9f9", stroke=LINE)[0])
    
    # Bottom Formula Banner
    frags.append(fitbox(100, 285, 460, 55, "Правило Маттіссена:  1/μ_total = 1/μ_ph + 1/μ_imp + 1/μ_sr\nСумування частот зіткнень: 1/τ_total = Σ (1/τ_i)", size=12, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(img_dir, "matthiessen-scattering-schematic.svg"), w, h, *frags)

# 4. Haynes-Shockley Experiment
def gen_haynes_shockley_experiment():
    w, h = 660, 380
    frags = []
    
    frags.append(text(w / 2, 26, "Схема експерименту Хейнса — Шокли для вимірювання дрейфу", size=15, bold=True))
    
    # Semiconductor sample bar
    bx, by, bw, bh = 100, 120, 460, 70
    frags.append(rect(bx, by, bw, bh, fill="#eaeded", stroke=LINE, sw=2, rx=4))
    frags.append(text(bx + bw / 2, by + bh / 2 + 4, "Напівпровідниковий зразок (Ge / Si n-типу)", size=13, color=MUTED, bold=True))
    
    # Electric Field E_drift arrow
    frags.append(arrow(bx + 40, by - 25, bx + bw - 40, by - 25, color=NEG, sw=2.5))
    frags.append(text(bx + bw / 2, by - 35, "Зовнішнє дрейфове поле E", size=12, color=NEG, bold=True))
    
    # Voltage sources at ends
    frags.append(line(bx, by + bh / 2, bx - 40, by + bh / 2, color=LINE, sw=2))
    frags.append(line(bx + bw, by + bh / 2, bx + bw + 40, by + bh / 2, color=LINE, sw=2))
    frags.append(plus(bx - 45, by + bh / 2, r=10))
    frags.append(minus(bx + bw + 45, by + bh / 2, r=10))
    
    # Emitter contact (Pulse Injector)
    emit_x = bx + 90
    frags.append(line(emit_x, by, emit_x, by - 55, color=POS, sw=2))
    frags.append(textbox(emit_x, by - 70, "Емітер (інжекція t=0)", size=10, fill="#fdecea", stroke=POS, bold=True)[0])
    # Initial sharp injected pulse
    frags.append(circle(emit_x, by + bh / 2, 8, fill=POS, stroke="#ffffff", sw=1.5))
    
    # Collector contact (Detector)
    coll_x = bx + 370
    frags.append(line(coll_x, by, coll_x, by - 55, color=FIELD, sw=2))
    frags.append(textbox(coll_x, by - 70, "Колектор (детектування t=Δt)", size=10, fill="#eafaf1", stroke=FIELD, bold=True)[0])
    
    # Distance L arrow
    frags.append(arrow(emit_x, by + bh + 20, coll_x, by + bh + 20, color=LINE, sw=1.5))
    frags.append(arrow(coll_x, by + bh + 20, emit_x, by + bh + 20, color=LINE, sw=1.5))
    frags.append(text((emit_x + coll_x) / 2, by + bh + 38, "Відстань L", size=12, bold=True))
    
    # Drifted & Diffused Gaussian cloud
    frags.append(circle(coll_x, by + bh / 2, 22, fill="#a3e4d7", stroke=FIELD, sw=1.5))
    frags.append(text(coll_x, by + bh / 2 + 4, "Δw", size=11, color=FIELD, bold=True))
    
    # Bottom oscilloscope pulse traces
    frags.append(rect(100, 270, 460, 85, fill="#1a252f", stroke=LINE, sw=2, rx=6))
    frags.append(text(120, 290, "Сигнал осцилографа:", size=11, color="#ffffff", bold=True))
    
    # Pulse 1 (injector trigger)
    frags.append('<path d="M 180,335 L 188,335 L 190,295 L 194,335 L 205,335" fill="none" stroke="%s" stroke-width="2"/>' % POS)
    frags.append(text(190, 348, "t = 0", size=10, color="#ffffff"))
    
    # Pulse 2 (collector response: delayed by dt, broadened by D)
    frags.append('<path d="M 330,335 C 350,335 360,305 370,305 C 380,305 390,335 410,335" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)
    frags.append(text(370, 348, "t = Δt", size=10, color="#ffffff"))
    
    # Formulas box on oscilloscope right
    frags.append(text(500, 298, "v_d = L / Δt", size=11, color="#f1c40f", bold=True))
    frags.append(text(500, 318, "μ = v_d / E", size=11, color="#f1c40f", bold=True))
    frags.append(text(500, 338, "D = (Δw)² / (16·Δt)", size=10, color="#ffffff"))

    render(os.path.join(img_dir, "haynes-shockley-experiment.svg"), w, h, *frags)

if __name__ == '__main__':
    gen_mobility_vs_temperature()
    gen_velocity_vs_electric_field()
    gen_matthiessen_scattering_schematic()
    gen_haynes_shockley_experiment()
    print("All figures generated successfully.")
