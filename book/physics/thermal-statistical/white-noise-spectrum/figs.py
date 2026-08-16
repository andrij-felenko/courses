# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Білий шум і спектральна щільність'."""

import sys
import os
import random

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')

def make_white_noise_time_freq():
    w, h = 720, 260
    elements = []
    
    # Left Panel: Time Domain
    ox1, oy1 = 50, 140
    elements.append(arrow(ox1, oy1, 330, oy1, color=INK, sw=1.5)) # t axis
    elements.append(arrow(ox1, 230, ox1, 30, color=INK, sw=1.5))   # x(t) axis
    elements.append(text(335, oy1 + 4, "t", size=13, italic=True))
    elements.append(text(ox1 - 15, 35, "x(t)", size=13, italic=True))
    elements.append(text(190, 20, "Часова область: x(t)", size=14, bold=True))
    
    # Grid & Zero line
    elements.append(line(ox1, oy1, 320, oy1, color=MUTED, sw=1.0, dash="3,3"))
    
    # Random white noise waveform
    rng = random.Random(42)
    pts = []
    num_pts = 100
    dx = (310 - ox1) / (num_pts - 1)
    for i in range(num_pts):
        x = ox1 + i * dx
        y = oy1 + rng.gauss(0, 35)
        pts.append((x, y))
    
    path_data = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (path_data, POS))
    elements.append(text(190, 245, "Хаотичні, некорельовані флуктуації", size=11, color=MUTED))

    # Divider
    elements.append(line(360, 20, 360, 240, color="#e0e0e0", sw=1.5, dash="4,4"))

    # Right Panel: Frequency Domain
    ox2, oy2 = 410, 200
    elements.append(arrow(ox2, oy2, 680, oy2, color=INK, sw=1.5)) # f axis
    elements.append(arrow(ox2, oy2, ox2, 30, color=INK, sw=1.5))   # S_x(f) axis
    elements.append(text(685, oy2 + 4, "f", size=13, italic=True))
    elements.append(text(ox2 - 20, 35, "S_x(f)", size=13, italic=True))
    elements.append(text(545, 20, "Частотна область: S_x(f)", size=14, bold=True))
    
    # Constant spectral density line
    psd_y = 100
    elements.append(line(ox2, psd_y, 670, psd_y, color=NEG, sw=2.5))
    elements.append(line(ox2, psd_y, 670, psd_y, color=NEG, sw=1.0, dash="4,4"))
    
    # Shading under PSD
    elements.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" opacity="0.15"/>' %
                    (ox2, psd_y, 670 - ox2, oy2 - psd_y, NEG))
    
    elements.append(text(540, psd_y - 12, "S_x(f) = N₀ / 2 = const", size=13, color=NEG, bold=True))
    elements.append(text(545, 245, "Рівномірний спектр на всіх частотах", size=11, color=MUTED))

    out_path = os.path.join(OUT_DIR, "white-noise-time-freq.svg")
    render(out_path, w, h, *elements)

def make_wiener_khinchin_concept():
    w, h = 700, 280
    elements = []
    
    # Title
    elements.append(text(w/2, 25, "Теорема Вінера — Хінчина: часова та частотна дуальність", size=15, bold=True))
    
    # Left Box: Autocorrelation R_x(tau)
    bx1, by1 = 50, 60
    bw, bh = 240, 180
    elements.append(rect(bx1, by1, bw, bh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(bx1 + bw/2, by1 + 25, "Автокореляційна функція R_x(τ)", size=13, bold=True))
    
    # Mini plot inside left box
    cox1, coy1 = bx1 + 30, by1 + 140
    elements.append(arrow(cox1, coy1, bx1 + bw - 20, coy1, color=INK, sw=1.2))
    elements.append(arrow(bx1 + bw/2, coy1 + 20, bx1 + bw/2, by1 + 45, color=INK, sw=1.2))
    elements.append(text(bx1 + bw - 15, coy1 + 12, "τ", size=11, italic=True))
    elements.append(text(bx1 + bw/2 + 10, by1 + 55, "R(0)", size=10, italic=True))
    
    # Delta peak
    px = bx1 + bw/2
    elements.append(arrow(px, coy1, px, by1 + 60, color=POS, sw=2.5))
    elements.append(circle(px, by1 + 60, 3, fill=POS, stroke=POS))
    elements.append(text(bx1 + bw/2, coy1 + 30, "R_x(τ) = (N₀/2) · δ(τ)", size=12, color=POS, bold=True))
    
    # Center Arrow & Transformations
    cx1, cx2 = 320, 380
    cy_mid = by1 + bh/2
    elements.append(arrow(cx1, cy_mid - 20, cx2 + 20, cy_mid - 20, color=FIELD, sw=2.0))
    elements.append(text(cx1 + 40, cy_mid - 30, "Перетворення Фурьє ℱ", size=11, color=FIELD, bold=True))
    
    elements.append(arrow(cx2 + 20, cy_mid + 20, cx1, cy_mid + 20, color=FIELD, sw=2.0))
    elements.append(text(cx1 + 40, cy_mid + 35, "Зворотне ℱ⁻¹", size=11, color=FIELD, bold=True))

    # Right Box: Spectral Density S_x(f)
    bx2 = 410
    elements.append(rect(bx2, by1, bw, bh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(bx2 + bw/2, by1 + 25, "Спектральна щільність S_x(f)", size=13, bold=True))
    
    # Mini plot inside right box
    cox2, coy2 = bx2 + 30, by1 + 140
    elements.append(arrow(cox2, coy2, bx2 + bw - 20, coy2, color=INK, sw=1.2))
    elements.append(arrow(cox2, coy2, cox2, by1 + 45, color=INK, sw=1.2))
    elements.append(text(bx2 + bw - 15, coy2 + 12, "f", size=11, italic=True))
    
    # Flat line
    elements.append(line(cox2, by1 + 75, bx2 + bw - 30, by1 + 75, color=NEG, sw=2.5))
    elements.append(text(bx2 + bw/2, coy2 + 30, "S_x(f) = N₀/2 = const", size=12, color=NEG, bold=True))

    out_path = os.path.join(OUT_DIR, "wiener-khinchin-concept.svg")
    render(out_path, w, h, *elements)

def make_filtering_colored_noise():
    w, h = 720, 280
    elements = []
    
    elements.append(text(w/2, 22, "Проходження білого шуму через лінійний RC-фільтр", size=15, bold=True))
    
    # System Diagram Blocks
    tb1, _, _ = textbox(110, 80, "Білий шум X(t)\nS_in(f) = N₀/2", size=12, fill="#eef2ff", stroke=NEG)
    elements.append(tb1)
    
    elements.append(arrow(180, 80, 240, 80, color=INK, sw=1.8))
    
    tb2, _, _ = textbox(340, 80, "RC-Фільтр Низьких Частот\nH(f) = 1 / (1 + j 2πf RC)", size=12, fill="#e8f8f0", stroke=FIELD)
    elements.append(tb2)
    
    elements.append(arrow(440, 80, 500, 80, color=INK, sw=1.8))
    
    tb3, _, _ = textbox(610, 80, "Офарбований шум Y(t)\nS_out(f) = S_in · |H(f)|²", size=12, fill="#fdf2f2", stroke=POS)
    elements.append(tb3)

    # Spectral Response Curves Plot (Bottom)
    ox, oy = 80, 250
    pw, ph = 580, 110
    elements.append(arrow(ox, oy, ox + pw, oy, color=INK, sw=1.5))
    elements.append(arrow(ox, oy, ox, oy - ph - 10, color=INK, sw=1.5))
    elements.append(text(ox + pw + 10, oy + 4, "f", size=13, italic=True))
    elements.append(text(ox - 15, oy - ph - 5, "S(f)", size=13, italic=True))
    
    # White noise curve
    elements.append(line(ox, oy - 80, ox + pw - 20, oy - 80, color=NEG, sw=2.0, dash="5,5"))
    elements.append(text(ox + pw - 80, oy - 87, "Вхід S_in(f)", size=11, color=NEG))
    
    # RC filter output response curve S_out(f) = N0/2 / (1 + (f/f_c)^2)
    pts = []
    fc = 120.0
    for i in range(100):
        fx = i * (pw - 40) / 99.0
        f_val = fx / (fc / 2.0)
        h_sq = 1.0 / (1.0 + f_val * f_val)
        y = oy - 80.0 * h_sq
        pts.append((ox + fx, y))
    
    path_data = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_data, POS))
    elements.append(text(ox + 180, oy - 45, "Вихід S_out(f) [Процес Орнштейна-Уленбека]", size=11, color=POS, bold=True))
    
    elements.append(line(ox + fc, oy, ox + fc, oy - 40, color=MUTED, sw=1.0, dash="3,3"))
    elements.append(text(ox + fc, oy + 15, "f_c = 1/(2πRC)", size=11, color=MUTED, anchor="middle"))

    out_path = os.path.join(OUT_DIR, "filtering-colored-noise.svg")
    render(out_path, w, h, *elements)

def make_spectral_density_measurement():
    w, h = 740, 260
    elements = []
    
    elements.append(text(w/2, 22, "Конвеєр цифрового спектрального аналізу за методом Велча", size=15, bold=True))
    
    # Pipeline stages
    stages = [
        ("Вхідний сигнал\nx[n]", 70),
        ("Сегментація та\nВікно Хенна w[n]", 210),
        ("БПФ (FFT)\nX_k(f)", 360),
        ("Періодограма\n|X_k|² / (f_s S_w)", 510),
        ("Усереднення K\nперіодограм → Ĝ(f)", 660)
    ]
    
    for i, (label, cx) in enumerate(stages):
        fill_col = "#f4f6f8" if i != 4 else "#e8f8f0"
        strk_col = LINE if i != 4 else FIELD
        b, _, _ = textbox(cx, 110, label, size=11, fill=fill_col, stroke=strk_col, pad=8)
        elements.append(b)
        
        if i < len(stages) - 1:
            next_cx = stages[i+1][1]
            elements.append(arrow(cx + 55, 110, next_cx - 55, 110, color=INK, sw=1.6))
            
    tb_note, _, _ = textbox(w/2, 210, 
                            "50% перекриття сегментів компенсує втрату потужності на краях вікна Хенна\n"
                            "Відносна середньоквадратична похибка оцінки спадає як ε_rms = 1 / √K", 
                            size=12, fill="#fffde7", stroke="#f39c12", pad=10)
    elements.append(tb_note)

    out_path = os.path.join(OUT_DIR, "spectral-density-measurement.svg")
    render(out_path, w, h, *elements)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    make_white_noise_time_freq()
    make_wiener_khinchin_concept()
    make_filtering_colored_noise()
    make_spectral_density_measurement()
    print("All figures successfully generated in img/")

if __name__ == "__main__":
    main()
