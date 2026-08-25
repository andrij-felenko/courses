# -*- coding: utf-8 -*-
"""
Generator script for Helmholtz resonator figures.
Uses svgkit from scripts directory.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#0284c7" # Accent blue color for cavity/curves

def svg_path(d, fill="none", stroke=LINE, sw=1.5, opacity=1.0, dash=None):
    o = f' opacity="{opacity}"' if opacity < 1.0 else ''
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{o}{ds}/>'

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: helmholtz-structure.svg
# -----------------------------------------------------------------------------
def gen_helmholtz_structure():
    filepath = os.path.join(IMG_DIR, 'helmholtz-structure.svg')
    w, h = 760, 440
    frags = []
    
    # Title
    frags.append(text(w / 2, 25, "Фізична структура резонатора Гельмгольца", size=16, bold=True))
    
    cx, cy = 460, 260
    rx, ry = 190, 140
    
    # Cavity volume representation
    frags.append(svg_path(
        f"M 200,60 L 200,140 A {rx},{ry} 0 1 0 260,140 L 260,60 Z",
        fill="#e0f2fe", stroke=ACCENT, sw=2.5
    ))
    
    # Air plug in neck (moving mass m)
    frags.append(rect(202, 75, 56, 50, fill="#bae6fd", stroke=POS, sw=1.5, rx=2))
    
    # Particles in neck plug to show mass density
    for py in range(82, 120, 8):
        for px in range(206, 222, 6):
            frags.append(circle(px, py, 2, fill="#0284c7", stroke="none"))
            
    # Arrow showing displacement xi(t) of neck air plug
    frags.append(arrow(235, 70, 235, 130, color=NEG, sw=2))
    frags.append(text(275, 105, "ξ(t), v(t)", size=12, bold=True, color=NEG))
    
    # Neck labels
    frags.append(line(175, 60, 175, 140, color=LINE, sw=1.5))
    frags.append(line(170, 60, 180, 60, color=LINE, sw=1.5))
    frags.append(line(170, 140, 180, 140, color=LINE, sw=1.5))
    frags.append(text(155, 104, "L", size=14, bold=True, anchor="end"))
    frags.append(text(155, 120, "(довжина)", size=10, color=MUTED, anchor="end"))
    
    frags.append(line(200, 48, 260, 48, color=LINE, sw=1.5))
    frags.append(line(200, 43, 200, 53, color=LINE, sw=1.5))
    frags.append(line(260, 43, 260, 53, color=LINE, sw=1.5))
    frags.append(text(230, 40, "S = π r²", size=13, bold=True))
    
    # Incoming sound wave p_in(t)
    frags.append(arrow(230, 10, 230, 45, color=NEG, sw=2.5))
    frags.append(text(230, 8, "Вхідний акустичний тиск p_in(t)", size=12, bold=True, color=NEG))
    
    # Cavity Volume V label
    frags.append(text(cx, cy - 20, "Об'єм каверни V", size=18, bold=True, color=ACCENT))
    frags.append(text(cx, cy + 5, "Акустична гнучкість C_a = V / (ρ c²)", size=13, color=MUTED))
    frags.append(text(cx, cy + 25, "Пружна повітряна подушка (стиск Δp)", size=12, color=MUTED))
    
    # Neck mass label
    frags.append(textbox(100, 210, "Маса повітря в шийці:\nm = ρ · S · L_eff\n(Акустична інертність M_a)", size=11, fill="#ffffff", stroke=POS, sw=1.2)[0])
    frags.append(line(165, 185, 205, 120, color=POS, sw=1.2, dash="3,3"))
    
    # Explanatory cards at bottom
    frags.append(fitbox(60, 345, 310, 75, [
        "Шийка (поршень масою m):",
        "• Чинить інерційний опір прискоренню",
        "• Акустична маса M_a = ρ L_eff / S"
    ], size=11, fill="#f1f5f9", stroke=LINE))
    
    frags.append(fitbox(390, 345, 310, 75, [
        "Об'єм V (пружна пружина):",
        "• Адіабатичний стиск повітря в об'ємі",
        "• Акустична гнучкість C_a = V / (ρ c²)"
    ], size=11, fill="#f1f5f9", stroke=LINE))
    
    render(filepath, w, h, *frags)
    print(f"Generated {filepath}")

# -----------------------------------------------------------------------------
# Figure 2: lumped-equivalent-circuit.svg
# -----------------------------------------------------------------------------
def gen_lumped_equivalent_circuit():
    filepath = os.path.join(IMG_DIR, 'lumped-equivalent-circuit.svg')
    w, h = 760, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Еквівалентні системи резонатора Гельмгольца", size=16, bold=True))
    
    # Left Block: Mechanical Mass-Spring-Damper Analogy
    frags.append(text(200, 60, "А) Механічна аналогія (маса-пружина-демпфер)", size=13, bold=True))
    
    # Wall/Ceiling
    frags.append(rect(80, 85, 240, 15, fill="#94a3b8", stroke=LINE, sw=1.5))
    for x in range(85, 320, 15):
        frags.append(line(x, 85, x - 8, 75, color=LINE, sw=1))
        
    # Spring (stiffness k)
    spring_pts = []
    sx, sy = 130, 100
    spring_pts.append((sx, sy))
    for i in range(6):
        sy += 15
        sx_off = 15 if i % 2 == 0 else -15
        spring_pts.append((130 + sx_off, sy))
    spring_pts.append((130, 205))
    
    path_str = f"M {spring_pts[0][0]},{spring_pts[0][1]} " + " ".join([f"L {px},{py}" for px, py in spring_pts[1:]])
    frags.append(svg_path(path_str, fill="none", stroke=ACCENT, sw=2))
    frags.append(text(95, 155, "Пружина k", size=12, bold=True, color=ACCENT))
    frags.append(text(75, 172, "k = ρ c² S² / V", size=10, color=MUTED))
    
    # Damper (viscous resistance R_m)
    dx = 270
    frags.append(line(dx, 100, dx, 135, color=LINE, sw=1.5))
    frags.append(rect(dx - 12, 135, 24, 35, fill="none", stroke=LINE, sw=1.5))
    frags.append(line(dx, 150, dx, 205, color=NEG, sw=1.5))
    frags.append(rect(dx - 8, 145, 16, 18, fill="#fecaca", stroke="none"))
    frags.append(text(290, 155, "Демпфер R_m", size=12, bold=True, color=NEG))
    
    # Mass block m
    frags.append(rect(100, 205, 200, 45, fill="#bae6fd", stroke=POS, sw=2, rx=4))
    frags.append(text(200, 232, "Поршень масою m = ρ S L_eff", size=12, bold=True))
    
    # Force F(t)
    frags.append(arrow(200, 285, 200, 255, color=NEG, sw=2))
    frags.append(text(200, 305, "Зовнішня сила F(t) = p_in(t) · S", size=11, bold=True, color=NEG))
    
    # Right Block: Electrical RLC Series Circuit Analogy
    frags.append(text(560, 60, "Б) Електричний акустичний контур (RLC)", size=13, bold=True))
    
    # Circuit loop
    frags.append(circle(430, 180, 18, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(430, 184, "p", size=14, bold=True))
    frags.append(line(430, 100, 430, 162, color=LINE, sw=1.5))
    frags.append(line(430, 198, 430, 260, color=LINE, sw=1.5))
    
    # Top horizontal wire with M_a (Inductor) and R_a (Resistor)
    frags.append(line(430, 100, 460, 100, color=LINE, sw=1.5))
    
    # Inductor M_a
    lx0 = 460
    for i in range(4):
        frags.append(svg_path(f"M {lx0 + i*15},100 A 7.5,7.5 0 0 1 {lx0 + (i+1)*15},100", fill="none", stroke=POS, sw=2))
    frags.append(text(490, 82, "M_a (Індуктивність)", size=11, bold=True, color=POS))
    frags.append(text(490, 68, "M_a = ρ L_eff / S", size=9, color=MUTED))
    
    # Resistor R_a
    rx0 = 540
    frags.append(line(520, 100, rx0, 100, color=LINE, sw=1.5))
    frags.append(rect(rx0, 92, 45, 16, fill="#fee2e2", stroke=NEG, sw=1.5))
    frags.append(text(rx0 + 22, 82, "R_a (Опір)", size=11, bold=True, color=NEG))
    frags.append(line(rx0 + 45, 100, 670, 100, color=LINE, sw=1.5))
    
    # Capacitor C_a
    frags.append(line(670, 100, 670, 168, color=LINE, sw=1.5))
    frags.append(line(655, 168, 685, 168, color=ACCENT, sw=2.5))
    frags.append(line(655, 176, 685, 176, color=ACCENT, sw=2.5))
    frags.append(line(670, 176, 670, 260, color=LINE, sw=1.5))
    frags.append(text(715, 172, "C_a (Ємність)", size=11, bold=True, color=ACCENT, anchor="middle"))
    frags.append(text(715, 188, "C_a = V / (ρ c²)", size=9, color=MUTED, anchor="middle"))
    
    # Bottom horizontal wire
    frags.append(line(430, 260, 670, 260, color=LINE, sw=1.5))
    
    # Current flow U_a
    frags.append(arrow(450, 245, 520, 245, color=ACCENT, sw=2))
    frags.append(text(485, 235, "Об'ємний потік U_a(t)", size=11, bold=True, color=ACCENT))
    
    # Resonance formula card at bottom
    frags.append(rect(60, 330, 640, 70, fill="#f8fafc", stroke=ACCENT, sw=1.5, rx=6))
    frags.append(text(w / 2, 352, "Резонансна частота у двох уявленнях:", size=13, bold=True))
    frags.append(text(w / 2, 380, "f_H = (1 / 2π) · √(k / m)  =  (1 / 2π) · √(1 / (M_a · C_a))  =  (c / 2π) · √(S / (V · L_eff))", size=14, bold=True, color=ACCENT))
    
    render(filepath, w, h, *frags)
    print(f"Generated {filepath}")

# -----------------------------------------------------------------------------
# Figure 3: end-correction-flow.svg
# -----------------------------------------------------------------------------
def gen_end_correction_flow():
    filepath = os.path.join(IMG_DIR, 'end-correction-flow.svg')
    w, h = 740, 380
    frags = []
    
    frags.append(text(w / 2, 25, "Ефект кінцевої поправки Релея (End Correction)", size=16, bold=True))
    
    # Physical neck channel
    x0, y0, nw, nh = 260, 100, 220, 120
    
    # Main tube walls
    frags.append(rect(x0, y0, nw, nh, fill="#f0f9ff", stroke="none"))
    frags.append(line(x0, y0, x0 + nw, y0, color=LINE, sw=3))
    frags.append(line(x0, y0 + nh, x0 + nw, y0 + nh, color=LINE, sw=3))
    
    # Internal cavity wall
    frags.append(line(x0, y0 - 50, x0, y0, color=LINE, sw=3))
    frags.append(line(x0, y0 + nh, x0, y0 + nh + 50, color=LINE, sw=3))
    
    # Extension regions
    delta_out = 55
    frags.append(rect(x0 + nw, y0, delta_out, nh, fill="#fef9c3", stroke=NEG, sw=1.2))
    
    delta_in = 75
    frags.append(rect(x0 - delta_in, y0, delta_in, nh, fill="#fef9c3", stroke=POS, sw=1.2))
    
    # Stream lines
    for offset_y in [20, 40, 60, 80, 100]:
        y_c = y0 + offset_y
        p_str = f"M {x0 - delta_in - 25},{y_c + (offset_y - 60)*0.5} Q {x0 - 20},{y_c} {x0},{y_c} L {x0 + nw},{y_c} Q {x0 + nw + 20},{y_c} {x0 + nw + delta_out + 20},{y_c + (offset_y - 60)*0.4}"
        frags.append(svg_path(p_str, fill="none", stroke=ACCENT, sw=1.2, opacity=0.7))
        
    # Radius r
    frags.append(line(x0 + nw / 2, y0, x0 + nw / 2, y0 + nh / 2, color=POS, sw=1.5))
    frags.append(arrow(x0 + nw / 2, y0 + nh / 2, x0 + nw / 2, y0, color=POS, sw=1.5))
    frags.append(text(x0 + nw / 2 + 15, y0 + nh / 4, "Радіус r", size=12, bold=True, color=POS))
    
    # Length L
    frags.append(line(x0, y0 + nh + 15, x0 + nw, y0 + nh + 15, color=LINE, sw=1.5))
    frags.append(line(x0, y0 + nh + 10, x0, y0 + nh + 20, color=LINE, sw=1.5))
    frags.append(line(x0 + nw, y0 + nh + 10, x0 + nw, y0 + nh + 20, color=LINE, sw=1.5))
    frags.append(text(x0 + nw / 2, y0 + nh + 32, "Фізична довжина L", size=12, bold=True))
    
    # Internal correction ΔL_in
    frags.append(line(x0 - delta_in, y0 + nh + 15, x0, y0 + nh + 15, color=POS, sw=1.5))
    frags.append(line(x0 - delta_in, y0 + nh + 10, x0 - delta_in, y0 + nh + 20, color=POS, sw=1.5))
    frags.append(text(x0 - delta_in / 2, y0 + nh + 32, "ΔL_in ≈ 0.85 r", size=11, bold=True, color=POS))
    
    # External correction ΔL_out
    frags.append(line(x0 + nw, y0 + nh + 15, x0 + nw + delta_out, y0 + nh + 15, color=NEG, sw=1.5))
    frags.append(line(x0 + nw + delta_out, y0 + nh + 10, x0 + nw + delta_out, y0 + nh + 20, color=NEG, sw=1.5))
    frags.append(text(x0 + nw + delta_out / 2, y0 + nh + 32, "ΔL_out ≈ 0.61 r", size=11, bold=True, color=NEG))
    
    # Effective length L_eff
    ly0 = y0 - 25
    frags.append(line(x0 - delta_in, ly0, x0 + nw + delta_out, ly0, color=ACCENT, sw=2))
    frags.append(line(x0 - delta_in, ly0 - 5, x0 - delta_in, ly0 + 5, color=ACCENT, sw=2))
    frags.append(line(x0 + nw + delta_out, ly0 - 5, x0 + nw + delta_out, ly0 + 5, color=ACCENT, sw=2))
    frags.append(text(x0 + nw / 2, ly0 - 10, "Ефективна акустична довжина: L_eff = L + ΔL_in + ΔL_out", size=13, bold=True, color=ACCENT))
    
    # Summary note cards at bottom
    frags.append(textbox(40, 290, "Внутрішній торець (фланець):\n• Повітря розтікається у півпростір каверни\n• Приєднана маса додає ΔL_in ≈ 0.8488 r", size=11, fill="#f0fdf4", stroke=POS, sw=1)[0])
    
    frags.append(textbox(430, 290, "Зовнішній торець (без фланця):\n• Вільне сферичне випромінювання у простір\n• Приєднана маса додає ΔL_out ≈ 0.6133 r", size=11, fill="#fffbebe", stroke=NEG, sw=1)[0])
    
    render(filepath, w, h, *frags)
    print(f"Generated {filepath}")

# -----------------------------------------------------------------------------
# Figure 4: impedance-frequency-response.svg
# -----------------------------------------------------------------------------
def gen_impedance_frequency_response():
    filepath = os.path.join(IMG_DIR, 'impedance-frequency-response.svg')
    w, h = 760, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Акустичний імпеданс та коефіцієнт поглинання резонатора", size=16, bold=True))
    
    x0, y0, pw, ph = 90, 310, 580, 230
    
    frags.append(rect(x0, y0 - ph, pw, ph, fill="#fafafa", stroke=LINE, sw=1))
    
    for i in range(1, 5):
        gy = y0 - i * (ph / 5)
        frags.append(line(x0, gy, x0 + pw, gy, color="#e2e8f0", sw=1))
        
    y_zero = y0 - ph / 2
    frags.append(line(x0, y_zero, x0 + pw, y_zero, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(x0 - 10, y_zero + 4, "0", size=11, anchor="end", color=MUTED))
    
    x_res = x0 + pw * 0.45
    frags.append(line(x_res, y0 - ph, x_res, y0, color=NEG, sw=1.5, dash="5,5"))
    frags.append(text(x_res, y0 + 20, "f_H (резонанс)", size=12, bold=True, color=NEG))
    
    frags.append(arrow(x0, y0, x0 + pw + 25, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0, x0, y0 - ph - 20, color=LINE, sw=1.5))
    frags.append(text(x0 + pw + 30, y0 + 15, "Частота f (Гц)", size=12, anchor="start"))
    frags.append(text(x0 - 45, y0 - ph - 10, "Імпеданс |Z|, Реактанс X, Поглинання α", size=11, bold=True))
    
    pts_react = []
    for i in range(101):
        rel_x = i / 100.0
        px = x0 + rel_x * pw
        xf = 0.2 + rel_x * 2.3
        val = 1.2 * (xf - 1.0 / xf)
        py = y_zero - val * 45
        py = max(y0 - ph + 5, min(y0 - 5, py))
        pts_react.append((px, py))
        
    path_react = f"M {pts_react[0][0]},{pts_react[0][1]} " + " ".join([f"L {px},{py}" for px, py in pts_react[1:]])
    frags.append(svg_path(path_react, fill="none", stroke=POS, sw=2))
    
    pts_imp = []
    for i in range(101):
        rel_x = i / 100.0
        px = x0 + rel_x * pw
        xf = 0.2 + rel_x * 2.3
        x_val = 1.2 * (xf - 1.0 / xf)
        r_val = 0.25
        z_val = math.sqrt(r_val**2 + x_val**2)
        py = y_zero - (z_val - 0.2) * 50
        py = max(y0 - ph + 5, min(y0 - 5, py))
        pts_imp.append((px, py))
        
    path_imp = f"M {pts_imp[0][0]},{pts_imp[0][1]} " + " ".join([f"L {px},{py}" for px, py in pts_imp[1:]])
    frags.append(svg_path(path_imp, fill="none", stroke=ACCENT, sw=2.5))
    
    pts_alpha = []
    for i in range(101):
        rel_x = i / 100.0
        px = x0 + rel_x * pw
        xf = 0.2 + rel_x * 2.3
        q_factor = 6.0
        alpha = 0.95 / (1.0 + q_factor**2 * (xf - 1.0/xf)**2)
        py = y0 - alpha * (ph - 30)
        pts_alpha.append((px, py))
        
    path_alpha = f"M {pts_alpha[0][0]},{pts_alpha[0][1]} " + " ".join([f"L {px},{py}" for px, py in pts_alpha[1:]])
    frags.append(svg_path(path_alpha, fill="none", stroke=NEG, sw=2, dash="6,3"))
    
    frags.append(circle(x_res, y_zero - (0.25 - 0.2)*50, 4, fill=ACCENT, stroke="none"))
    frags.append(text(x_res + 12, y_zero - 20, "Мін. імпедансу |Z| = R_a", size=11, bold=True, color=ACCENT))
    
    # Legend lines & labels directly without overlapping bounding box rect
    frags.append(line(495, 92, 525, 92, color=ACCENT, sw=2.5))
    frags.append(text(535, 96, "Модуль імпедансу |Z_A|", size=11, anchor="start"))
    
    frags.append(line(495, 117, 525, 117, color=POS, sw=2))
    frags.append(text(535, 121, "Реактанс X_A (пружний/інерційний)", size=11, anchor="start"))
    
    frags.append(line(495, 142, 525, 142, color=NEG, sw=2, dash="5,3"))
    frags.append(text(535, 146, "Поглинання α (пік на f_H)", size=11, anchor="start"))
    
    frags.append(text(w / 2, 380, "При f = f_H реактивна складова X_A дорівнює нулю: інерція повітря в шийці повністю компенсує пружність об'єму.", size=11, color=MUTED))
    
    render(filepath, w, h, *frags)
    print(f"Generated {filepath}")


if __name__ == '__main__':
    gen_helmholtz_structure()
    gen_lumped_equivalent_circuit()
    gen_end_correction_flow()
    gen_impedance_frequency_response()
