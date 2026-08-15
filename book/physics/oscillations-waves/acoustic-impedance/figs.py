# -*- coding: utf-8 -*-
"""
Generator script for acoustic impedance figures.
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
# Figure 1: pressure-velocity-wave.svg
# -----------------------------------------------------------------------------
def gen_pressure_velocity_wave():
    path = os.path.join(IMG_DIR, 'pressure-velocity-wave.svg')
    w, h = 740, 310
    frags = []
    
    # Title / Header
    frags.append(text(w / 2, 22, "Розподіл тиску та коливальної швидкості в плоскій акустичній хвилі", size=15, bold=True))
    
    # Fluid tube
    x0, y0, tw, th = 60, 45, 620, 70
    frags.append(rect(x0, y0, tw, th, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    
    # Draw particles with density modulation to represent compression and rarefaction
    import random
    rng = random.Random(42)
    for _ in range(350):
        rx_val = rng.uniform(0, tw)
        ry_val = rng.uniform(5, th - 5)
        # Spatial compression factor sin(2pi * rx / lambda)
        phase = 2 * math.pi * rx_val / 260
        bias = 0.5 + 0.45 * math.sin(phase)
        if rng.random() < bias:
            px = x0 + rx_val
            py = y0 + ry_val
            frags.append(circle(px, py, 1.8, fill=INK, stroke="none"))
            
    # Labels on tube
    frags.append(textbox(190, y0 + 18, "Стиск (високий тиск)", size=11, fill="#fee2e2", stroke=POS, sw=1)[0])
    frags.append(textbox(320, y0 + 52, "Розрідження (низький тиск)", size=11, fill="#dbeafe", stroke=NEG, sw=1)[0])
    
    # Axis for plots
    py0 = 210
    frags.append(line(x0, py0, x0 + tw, py0, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(arrow(x0, py0 + 50, x0, py0 - 55, color=LINE, sw=1.5))
    frags.append(arrow(x0, py0, x0 + tw + 20, py0, color=LINE, sw=1.5))
    frags.append(text(x0 - 15, py0 - 45, "p, v", size=13, bold=True, anchor="end"))
    frags.append(text(x0 + tw + 25, py0 + 15, "x (координата)", size=12, anchor="start"))
    
    # Curves for p(x) and v(x)
    pts_p = []
    pts_v = []
    steps = 120
    for i in range(steps + 1):
        x = x0 + (tw * i / steps)
        phase = 2 * math.pi * (x - x0) / 260
        yp = py0 - 38 * math.sin(phase)
        pts_p.append("%.1f,%.1f" % (x, yp))
        # v is in phase with p for traveling plane wave
        yv = py0 - 28 * math.sin(phase)
        pts_v.append("%.1f,%.1f" % (x, yv))
        
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_p), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6,3"/>' % (" ".join(pts_v), NEG))
    
    # Legend & formula box
    frags.append(line(x0 + 440, py0 - 35, x0 + 470, py0 - 35, color=POS, sw=2.5))
    frags.append(text(x0 + 475, py0 - 31, "Надлишковий тиск p(x)", size=11, anchor="start", bold=True, color=POS))
    
    frags.append(line(x0 + 440, py0 - 15, x0 + 470, py0 - 15, color=NEG, sw=2, dash="6,3"))
    frags.append(text(x0 + 475, py0 - 11, "Коливальна швидкість v(x)", size=11, anchor="start", bold=True, color=NEG))
    
    # Impedance ratio formula box
    box_code, _, _ = textbox(w - 130, py0 + 32, "Питомий імпеданс:\nz₀ = p(x) / v(x) = ρ · c", size=12, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    frags.append(box_code)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 2: impedance-interface.svg
# -----------------------------------------------------------------------------
def gen_impedance_interface():
    path = os.path.join(IMG_DIR, 'impedance-interface.svg')
    w, h = 760, 320
    frags = []
    
    frags.append(text(w / 2, 22, "Відбиття й проходження акустичної хвилі на межі середовищ", size=15, bold=True))
    
    x_int = 380
    y_top, y_bot = 50, 240
    
    # Medium 1 background
    frags.append(rect(40, y_top, x_int - 40, y_bot - y_top, fill="#eff6ff", stroke="none"))
    # Medium 2 background
    frags.append(rect(x_int, y_top, 720 - x_int, y_bot - y_top, fill="#fef3c7", stroke="none"))
    
    # Interface line
    frags.append(line(x_int, y_top - 10, x_int, y_bot + 10, color=LINE, sw=2.5, dash="6,4"))
    frags.append(text(x_int, y_top - 18, "Межа середовищ (x = 0)", size=12, bold=True))
    
    # Medium 1 label
    frags.append(textbox(180, y_top + 30, "Середовище 1\nz₁ = ρ₁ · c₁", size=13, fill="#dbeafe", stroke=NEG, sw=1.5, bold=True)[0])
    # Medium 2 label
    frags.append(textbox(560, y_top + 30, "Середовище 2\nz₂ = ρ₂ · c₂", size=13, fill="#fef08a", stroke="#d97706", sw=1.5, bold=True)[0])
    
    # Incident wave arrow
    y_inc = 125
    frags.append(arrow(80, y_inc, x_int - 15, y_inc, color=POS, sw=3))
    frags.append(text(210, y_inc - 12, "Падна хвиля pᵢ (амплітуда Aᵢ)", size=12, color=POS, bold=True))
    
    # Reflected wave arrow
    y_ref = 175
    frags.append(arrow(x_int - 15, y_ref, 80, y_ref, color=NEG, sw=2.5))
    frags.append(text(210, y_ref + 16, "Відбита хвиля pᵣ = R · pᵢ", size=12, color=NEG, bold=True))
    
    # Transmitted wave arrow
    y_trn = 150
    frags.append(arrow(x_int + 15, y_trn, 660, y_trn, color=FIELD, sw=3))
    frags.append(text(520, y_trn - 12, "Прохідна хвиля pₜ = T · pᵢ", size=12, color=FIELD, bold=True))
    
    # Formula boxes below
    f_box1 = textbox(210, 275, "Коефіцієнт відбиття за тиском:\nR = (z₂ − z₁) / (z₂ + z₁)", size=12, fill=FILL, stroke=LINE, sw=1.5)[0]
    f_box2 = textbox(550, 275, "Коефіцієнт проходження за тиском:\nT = 2 · z₂ / (z₂ + z₁)", size=12, fill=FILL, stroke=LINE, sw=1.5)[0]
    frags.append(f_box1)
    frags.append(f_box2)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 3: matching-layer.svg
# -----------------------------------------------------------------------------
def gen_matching_layer():
    path = os.path.join(IMG_DIR, 'matching-layer.svg')
    w, h = 760, 330
    frags = []
    
    frags.append(text(w / 2, 22, "Принцип чвертьхвильового акустичного узгоджувального шару", size=15, bold=True))
    
    y0, bh = 55, 170
    
    # Transducer PZT block
    frags.append(rect(40, y0, 180, bh, fill="#e0e7ff", stroke="#3730a3", sw=2, rx=4))
    frags.append(mtext(130, y0 + 75, "П'єзокераміка (PZT)\nz₁ ≈ 30 МРайл", size=13, color="#1e1b4b", bold=True))
    
    # Quarter-wave matching layer
    frags.append(rect(220, y0, 150, bh, fill="#dcfce7", stroke=FIELD, sw=2, rx=4))
    frags.append(mtext(295, y0 + 65, "Узгоджувальний шар\nd = λ / 4\nzₘ = √(z₁ · z₂)", size=12, color="#14532d", bold=True))
    frags.append(text(295, y0 + 135, "zₘ ≈ 6.7 МРайл", size=12, color=FIELD, bold=True))
    
    # Acoustic Gel / Tissue
    frags.append(rect(370, y0, 340, bh, fill="#fff7ed", stroke="#c2410c", sw=2, rx=4))
    frags.append(mtext(540, y0 + 75, "Біологічна тканина / Гель\nz₂ ≈ 1.5 МРайл", size=13, color="#9a3412", bold=True))
    
    # Wave propagation paths and cancellation
    # Primary reflection at interface 1
    frags.append(arrow(110, y0 + 150, 215, y0 + 150, color=POS, sw=2.5))
    frags.append(text(162, y0 + 140, "Падна хвиля", size=11, color=POS))
    
    # Interference path in layer
    frags.append(arrow(225, y0 + 30, 365, y0 + 30, color=FIELD, sw=2))
    frags.append(line(365, y0 + 30, 225, y0 + 48, color=NEG, sw=1.8, dash="4,2"))
    frags.append(text(295, y0 + 20, "Проходження й внутрішні відбиття", size=11, color=MUTED))
    
    # Bottom explanation / result box
    res_box = textbox(w / 2, 275, 
                      "Протифазна інтерференція відбивачів на межах (фазовий набіг 2 · d = λ/2 = 180°)\n"
                      "попустовує відбиту хвилю й забезпечує майже 100% проходження енергії на частоті f₀", 
                      size=12, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)[0]
    frags.append(res_box)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 4: acoustic-horn.svg
# -----------------------------------------------------------------------------
def gen_acoustic_horn():
    path = os.path.join(IMG_DIR, 'acoustic-horn.svg')
    w, h = 740, 300
    frags = []
    
    frags.append(text(w / 2, 22, "Акустичний рупор як геометричний трансформатор імпедансу", size=15, bold=True))
    
    # Driver box
    y_mid = 135
    frags.append(rect(15, y_mid - 45, 110, 90, fill="#f3e8ff", stroke="#6b21a8", sw=2, rx=6))
    frags.append(mtext(70, y_mid - 10, "Випромінювач\n(Драйвер)\nВисокий p\nМала швидкість", size=11, color="#581c87", bold=True))
    
    # Horn geometry (exponential shape)
    x_throat = 150
    x_mouth = 560
    throat_h = 30
    mouth_h = 160
    
    # Build upper and lower horn contours
    pts_top = []
    pts_bot = []
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        x = x_throat + t * (x_mouth - x_throat)
        # exponential expansion
        h_x = throat_h * math.exp(t * math.log(mouth_h / throat_h))
        pts_top.append((x, y_mid - h_x / 2))
        pts_bot.append((x, y_mid + h_x / 2))
        
    path_d = ["M %.1f,%.1f" % pts_top[0]]
    for p_val in pts_top[1:]:
        path_d.append("L %.1f,%.1f" % p_val)
    for p_val in reversed(pts_bot):
        path_d.append("L %.1f,%.1f" % p_val)
    path_d.append("Z")
    
    frags.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="2"/>' % (" ".join(path_d), LINE))
    
    # Throat label
    frags.append(line(x_throat, y_mid - throat_h/2 - 10, x_throat, y_mid + throat_h/2 + 10, color=POS, sw=1.5, dash="3,3"))
    frags.append(textbox(x_throat, y_mid - throat_h/2 - 25, "Горло (S₁)\nВисокий Z_A1", size=11, fill="#fee2e2", stroke=POS, sw=1)[0])
    
    # Mouth label
    frags.append(line(x_mouth, y_mid - mouth_h/2 - 10, x_mouth, y_mid + mouth_h/2 + 10, color=NEG, sw=1.5, dash="3,3"))
    frags.append(textbox(x_mouth, y_mid - mouth_h/2 - 25, "Устя (S₂)\nНизький Z_A2 (довкілля)", size=11, fill="#dbeafe", stroke=NEG, sw=1)[0])
    
    # Free air right
    frags.append(rect(x_mouth + 10, y_mid - 85, 140, 170, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(mtext(x_mouth + 80, y_mid - 25, "Вільне повітря\nЗовнішній\nімпеданс z₀ = ρc\nПлавне узгодження!", size=12, color="#14532d", bold=True))
    
    # Bottom explanation formula
    f_box = textbox(w / 2, 260, "Акустичний імпеданс перерізу: Z_A(x) = p / U = ρ·c / S(x)\nРупор плавно знижує Z_A від горла до устя, запобігаючи відбиттю хвилі назад", size=12, fill=FILL, stroke=LINE, sw=1.5)[0]
    frags.append(f_box)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 5: helmholtz-equivalent.svg
# -----------------------------------------------------------------------------
def gen_helmholtz_equivalent():
    path = os.path.join(IMG_DIR, 'helmholtz-equivalent.svg')
    w, h = 760, 320
    frags = []
    
    frags.append(text(w / 2, 22, "Резонатор Гельмгольца та його акустико-електричний еквівалент", size=15, bold=True))
    
    # Left panel: Physical Resonator
    x_c = 190
    y_c = 135
    frags.append(text(x_c, y_c - 90, "Фізична система (Резонатор)", size=13, bold=True))
    
    # Cavity circle/box
    frags.append(rect(x_c - 80, y_c - 30, 160, 110, fill="#eff6ff", stroke=NEG, sw=2, rx=12))
    frags.append(mtext(x_c, y_c + 15, "Об'єм порожнини V\n(Акустична пружність C_A)", size=12, color=NEG, bold=True))
    
    # Neck box
    frags.append(rect(x_c - 25, y_c - 75, 50, 47, fill="#fee2e2", stroke=POS, sw=2, rx=2))
    frags.append(mtext(x_c, y_c - 58, "Шийка L, S\n(Маса M_A)", size=10, color=POS, bold=True))
    
    # Arrow showing air mass oscillating in neck
    frags.append(arrow(x_c + 40, y_c - 70, x_c + 40, y_c - 35, color=POS, sw=2))
    frags.append(arrow(x_c + 40, y_c - 35, x_c + 40, y_c - 70, color=POS, sw=2))
    frags.append(text(x_c + 55, y_c - 52, "v(t)", size=11, color=POS, bold=True, anchor="start"))
    
    # Separator
    frags.append(line(375, 50, 375, 230, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(375, 140, "≡", size=24, bold=True, color=MUTED))
    
    # Right panel: Electrical equivalent series RLC circuit
    x_e = 560
    frags.append(text(x_e, 45, "Електричний аналог (Послідовний RLC)", size=13, bold=True))
    
    # Generator P_in
    frags.append(circle(x_e - 130, y_c, 18, fill="#fef3c7", stroke="#d97706", sw=2))
    frags.append(text(x_e - 130, y_c + 4, "p(t)", size=11, bold=True, color="#b45309"))
    
    # Circuit wires and components
    y_wire = y_c - 40
    frags.append(line(x_e - 130, y_c - 18, x_e - 130, y_wire, color=LINE, sw=1.8))
    frags.append(line(x_e - 130, y_wire, x_e - 90, y_wire, color=LINE, sw=1.8))
    
    # Resistor R_A (Losses)
    frags.append(rect(x_e - 90, y_wire - 12, 45, 24, fill="#f8fafc", stroke=LINE, sw=1.8, rx=2))
    frags.append(text(x_e - 67, y_wire + 4, "R_A", size=11, bold=True))
    frags.append(text(x_e - 67, y_wire - 18, "Втрати", size=10, color=MUTED))
    
    frags.append(line(x_e - 45, y_wire, x_e - 15, y_wire, color=LINE, sw=1.8))
    
    # Inductor L_A (Mass of neck)
    frags.append(rect(x_e - 15, y_wire - 12, 45, 24, fill="#fee2e2", stroke=POS, sw=1.8, rx=2))
    frags.append(text(x_e + 7, y_wire + 4, "M_A", size=11, bold=True, color=POS))
    frags.append(text(x_e + 7, y_wire - 18, "Маса шийки", size=10, color=POS))
    
    frags.append(line(x_e + 30, y_wire, x_e + 60, y_wire, color=LINE, sw=1.8))
    
    # Capacitor C_A (Compliance of cavity)
    frags.append(rect(x_e + 60, y_wire - 12, 45, 24, fill="#eff6ff", stroke=NEG, sw=1.8, rx=2))
    frags.append(text(x_e + 82, y_wire + 4, "C_A", size=11, bold=True, color=NEG))
    frags.append(text(x_e + 82, y_wire - 18, "Гнучкість", size=10, color=NEG))
    
    frags.append(line(x_e + 105, y_wire, x_e + 130, y_wire, color=LINE, sw=1.8))
    frags.append(line(x_e + 130, y_wire, x_e + 130, y_c + 40, color=LINE, sw=1.8))
    frags.append(line(x_e + 130, y_c + 40, x_e - 130, y_c + 40, color=LINE, sw=1.8))
    frags.append(line(x_e - 130, y_c + 40, x_e - 130, y_c + 18, color=LINE, sw=1.8))
    
    # Resonant frequency box below
    res_box = textbox(w / 2, 275, "Резонансна частота: f₀ = (c / 2π) · √(S / (L' · V))\nНа частоті f₀ реактивний опір X_A = ω·M_A − 1/(ω·C_A) дорівнює нулю, а імпеданс мінімальний", size=12, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)[0]
    frags.append(res_box)
    
    render(path, w, h, *frags)

if __name__ == '__main__':
    gen_pressure_velocity_wave()
    gen_impedance_interface()
    gen_matching_layer()
    gen_acoustic_horn()
    gen_helmholtz_equivalent()
    print("All acoustic impedance figures generated successfully.")
