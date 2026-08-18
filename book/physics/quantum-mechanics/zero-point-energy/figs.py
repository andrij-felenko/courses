# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_oscillator_figure(out_dir):
    """Фігура 1: Потенціальна яма квантового гармонічного осцилятора та нульовий рівень енергії."""
    w, h = 740, 440
    out = []
    
    # Координатні осі
    cx = 370
    cy_bottom = 350
    out.append(line(70, cy_bottom, 670, cy_bottom, color=MUTED, sw=1.5))
    out.append(line(cx, 40, cx, 380, color=MUTED, sw=1.5))
    out.append(text(675, cy_bottom + 4, "x", size=14, color=INK, bold=True))
    out.append(text(cx - 15, 35, "E, V(x)", size=14, color=INK, bold=True))
    
    # Потенціальна парабола V(x) = 0.5 * k * x^2
    points = []
    k_scale = 0.0032
    for x_val in range(120, 621, 5):
        dx = x_val - cx
        y_val = cy_bottom - k_scale * (dx ** 2)
        points.append((x_val, y_val))
    
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    out.append(f'<path d="{path_d}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    out.append(text(580, 110, "V(x) = ½ m ω² x²", size=14, color=INK, bold=True))
    
    # Класичний рівень E = 0
    out.append(line(cx - 40, cy_bottom, cx + 40, cy_bottom, color=POS, sw=2, dash="4,4"))
    out.append(circle(cx, cy_bottom, 5, fill=POS, stroke=LINE, sw=1))
    out.append(textbox(cx, cy_bottom + 32, "Класичний спокій (x = 0, p = 0, E = 0)\nЗаборонено принципом невизначеності", size=11, fill="#fdecea", stroke=POS)[0])
    
    # Квантовий рівень E0 = 0.5 * hbar * omega
    e0_y = cy_bottom - 110
    dx_e0 = math.sqrt(110.0 / k_scale)
    x_left_e0 = cx - dx_e0
    x_right_e0 = cx + dx_e0
    
    out.append(line(90, e0_y, 650, e0_y, color=FIELD, sw=2))
    out.append(text(120, e0_y - 10, "E₀ = ½ ℏω (Нульовий рівень)", size=14, color=FIELD, bold=True))
    
    # Хвильова функція psi_0(x) (Гаусова крива) над E0
    psi_points = []
    psi_amp = 65
    sigma = 60
    for x_val in range(100, 641, 4):
        dx = x_val - cx
        g = math.exp(- (dx**2) / (2 * sigma**2))
        y_val = e0_y - g * psi_amp
        psi_points.append((x_val, y_val))
    
    psi_d = f"M {100:.1f},{e0_y:.1f} L " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in psi_points) + f" L {640:.1f},{e0_y:.1f} Z"
    out.append(f'<path d="{psi_d}" fill="#eaf0fd" fill-opacity="0.6" stroke="{NEG}" stroke-width="2"/>')
    out.append(text(cx + 80, e0_y - 45, "Густина ймовірності |ψ₀(x)|²", size=12, color=NEG, bold=True))
    
    # Класично заборонені області
    out.append(line(x_left_e0, e0_y, x_left_e0, cy_bottom, color=MUTED, sw=1, dash="3,3"))
    out.append(line(x_right_e0, e0_y, x_right_e0, cy_bottom, color=MUTED, sw=1, dash="3,3"))
    
    out.append(textbox(160, 210, "Заборонена область\n(V(x) > E₀)", size=11, fill=FILL, stroke=MUTED)[0])
    out.append(textbox(580, 210, "Заборонена область\n(V(x) > E₀)", size=11, fill=FILL, stroke=MUTED)[0])
    
    # Стрілка невизначеності Δx
    out.append(line(x_left_e0, cy_bottom - 20, x_right_e0, cy_bottom - 20, color=INK, sw=1.5))
    out.append(text(cx, cy_bottom - 28, "Нульові коливання Δx₀ = √(ℏ / 2mω)", size=12, color=INK, bold=True))
    
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "oscillator-potential-well.svg")
    render(out_path, w, h, "".join(out))

def generate_casimir_figure(out_dir):
    """Фігура 2: Ефект Казимира — обмеження спектра вакуумних мод між пластинами."""
    w, h = 760, 420
    out = []
    
    # Пластини
    p1_x = 240
    p2_x = 520
    p_w = 24
    p_h = 300
    p_y = 60
    
    out.append(rect(p1_x, p_y, p_w, p_h, fill="#d1d5db", stroke=LINE, sw=2, rx=4))
    out.append(rect(p2_x, p_y, p_w, p_h, fill="#d1d5db", stroke=LINE, sw=2, rx=4))
    
    out.append(text(p1_x + p_w/2, p_y - 15, "Пластина 1", size=13, color=INK, bold=True))
    out.append(text(p2_x + p_w/2, p_y - 15, "Пластина 2", size=13, color=INK, bold=True))
    
    # Відстань d
    out.append(arrow(p1_x + p_w, p_y + p_h + 20, p2_x, p_y + p_h + 20, color=INK, sw=1.5))
    out.append(arrow(p2_x, p_y + p_h + 20, p1_x + p_w, p_y + p_h + 20, color=INK, sw=1.5))
    out.append(text((p1_x + p2_x + p_w)/2, p_y + p_h + 38, "Відстань d", size=13, color=INK, bold=True))
    
    # Внутрішні моди (стоячі хвилі)
    d_gap = p2_x - (p1_x + p_w)
    x0 = p1_x + p_w
    
    # Мода n=1
    y_m1 = 120
    m1_pts = []
    for i in range(101):
        t = i / 100.0
        x = x0 + t * d_gap
        y = y_m1 - 25 * math.sin(math.pi * t)
        m1_pts.append((x, y))
    d1 = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in m1_pts)
    out.append(f'<path d="{d1}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    out.append(text(x0 + d_gap/2, y_m1 - 32, "n = 1 (λ = 2d)", size=11, color=NEG))

    # Мода n=2
    y_m2 = 210
    m2_pts = []
    for i in range(101):
        t = i / 100.0
        x = x0 + t * d_gap
        y = y_m2 - 22 * math.sin(2 * math.pi * t)
        m2_pts.append((x, y))
    d2 = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in m2_pts)
    out.append(f'<path d="{d2}" fill="none" stroke="{FIELD}" stroke-width="2"/>')
    out.append(text(x0 + d_gap/2, y_m2 - 28, "n = 2 (λ = d)", size=11, color=FIELD))

    # Мода n=3
    y_m3 = 290
    m3_pts = []
    for i in range(101):
        t = i / 100.0
        x = x0 + t * d_gap
        y = y_m3 - 18 * math.sin(3 * math.pi * t)
        m3_pts.append((x, y))
    d3 = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in m3_pts)
    out.append(f'<path d="{d3}" fill="none" stroke="{POS}" stroke-width="2"/>')
    out.append(text(x0 + d_gap/2, y_m3 - 22, "n = 3 (λ = ⅔d)", size=11, color=POS))
    
    # Зовнішні флуктуації (довгі й короткі хвилі)
    for y_ext in [100, 160, 220, 280, 330]:
        pts = []
        wl = 15 + y_ext * 0.1
        for x in range(30, p1_x, 3):
            y = y_ext + 12 * math.sin((x - 30) / wl)
            pts.append((x, y))
        out.append(f'<path d="M {" L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3,2"/>')
        
    for y_ext in [100, 160, 220, 280, 330]:
        pts = []
        wl = 15 + y_ext * 0.1
        for x in range(p2_x + p_w, 730, 3):
            y = y_ext + 12 * math.sin((x - p2_x) / wl)
            pts.append((x, y))
        out.append(f'<path d="M {" L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3,2"/>')
    
    # Стрілки сили Казимира
    out.append(arrow(140, p_y + p_h/2, p1_x - 5, p_y + p_h/2, color=POS, sw=3.5))
    out.append(arrow(620, p_y + p_h/2, p2_x + p_w + 5, p_y + p_h/2, color=POS, sw=3.5))
    
    out.append(text(120, p_y + p_h/2 - 12, "Тиск зовні P_out", size=12, color=POS, bold=True))
    out.append(text(640, p_y + p_h/2 - 12, "Тиск зовні P_out", size=12, color=POS, bold=True))
    
    # Формула сили Казимира внизу
    out.append(textbox(w/2, 385, "Притягання Казимира: F / A = − π² ℏ c / (240 d⁴)", size=13, fill="#fdecea", stroke=POS, bold=True)[0])
    
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "casimir-effect-modes.svg")
    render(out_path, w, h, "".join(out))

def generate_liquid_helium_figure(out_dir):
    """Фігура 3: Потенціал взаємодії атомів гелію та нульова кінетична енергія."""
    w, h = 740, 420
    out = []
    
    cx = 120
    cy_zero = 240
    
    # Координатні осі
    out.append(line(cx - 30, cy_zero, 680, cy_zero, color=MUTED, sw=1.5))
    out.append(line(cx, 40, cx, 380, color=MUTED, sw=1.5))
    out.append(text(685, cy_zero + 4, "r (відстань між атомами)", size=13, color=INK, bold=True))
    out.append(text(cx - 15, 35, "V(r)", size=13, color=INK, bold=True))
    
    # Потенціал Леннард-Джонса
    sigma = 110.0
    eps = 70.0
    pts = []
    for x_pixel in range(cx + 45, 660, 3):
        r = x_pixel - cx
        sr6 = (sigma / r) ** 6
        v = 4 * eps * (sr6**2 - sr6)
        y_pixel = cy_zero - v
        if y_pixel < 50: y_pixel = 50
        if y_pixel > 390: y_pixel = 390
        pts.append((x_pixel, y_pixel))
        
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    out.append(f'<path d="{path_d}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    
    # Мінімум потенціальної ями
    r_min_x = cx + 123.4
    y_min = cy_zero + eps
    
    out.append(line(r_min_x, cy_zero, r_min_x, y_min, color=MUTED, sw=1, dash="3,3"))
    out.append(circle(r_min_x, y_min, 4, fill=POS, stroke=LINE, sw=1))
    out.append(text(r_min_x + 10, y_min + 15, "Глибина ями ε ≈ 10.2 K", size=11, color=POS))
    
    # Нульовий рівень енергії E0
    e0_y = cy_zero - 15
    out.append(line(cx + 50, e0_y, 650, e0_y, color=FIELD, sw=2))
    out.append(text(cx + 60, e0_y - 10, "Нульова кінетична енергія K₀ ≈ 25 K > ε", size=13, color=FIELD, bold=True))
    
    # Амплітуда коливань Δr0
    out.append(line(cx + 70, e0_y + 35, cx + 290, e0_y + 35, color=NEG, sw=2))
    out.append(arrow(cx + 180, e0_y + 35, cx + 70, e0_y + 35, color=NEG, sw=2))
    out.append(arrow(cx + 180, e0_y + 35, cx + 290, e0_y + 35, color=NEG, sw=2))
    out.append(text(cx + 180, e0_y + 55, "Амплітуда нульових коливань Δr₀ > r_min", size=12, color=NEG, bold=True))
    
    # Інформаційна рамка
    out.append(textbox(480, 110, "Чому гелій-4 не кристалізується при T → 0 K:\n1. Мала маса атома m (висока нульова енергія)\n2. Слабка вандерваальсова взаємодія ε\n3. Нульові коливання розмивають атомну ґратку", size=12, fill="#eaf0fd", stroke=NEG)[0])
    
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "liquid-helium-zero-point.svg")
    render(out_path, w, h, "".join(out))

def main():
    target_dir = os.path.dirname(__file__)
    img_dir = os.path.join(target_dir, "img")
    generate_oscillator_figure(img_dir)
    generate_casimir_figure(img_dir)
    generate_liquid_helium_figure(img_dir)
    print("Всі 3 фігури успішно згенеровано у", img_dir)

if __name__ == "__main__":
    main()
