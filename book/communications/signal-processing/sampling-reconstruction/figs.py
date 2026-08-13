# -*- coding: utf-8 -*-
import sys
import os
import math

# Add path to scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def sinc(x):
    if abs(x) < 1e-9:
        return 1.0
    return math.sin(math.pi * x) / (math.pi * x)

def fig_ideal_reconstruction():
    """Diagram 1: Spectral view of ideal reconstruction (periodic spectrum + ideal LPF = baseband spectrum)"""
    w, h = 760, 300
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    # Panel 1: Periodic Spectrum of Samples (left)
    cx1, cy1 = 200, 180
    svg.append(text(cx1, 28, "1. Спектр відліків (періодичний)", size=15, bold=True, anchor="middle", color=INK))
    
    # Axis
    svg.append(f'<line x1="30" y1="{cy1}" x2="370" y2="{cy1}" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(f'<line x1="{cx1}" y1="{cy1}" x2="{cx1}" y2="50" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(text(370, cy1+18, "f", size=13, italic=True, anchor="end", color=MUTED))

    # Baseband and replicas (triangles)
    centers = [cx1 - 120, cx1, cx1 + 120]
    labels = ["-fs", "0", "+fs"]
    for cnt, lbl in zip(centers, labels):
        # Draw spectral triangle
        p1 = f"{cnt - 40},{cy1}"
        p2 = f"{cnt},{cy1 - 70}"
        p3 = f"{cnt + 40},{cy1}"
        clr = FIELD if cnt == cx1 else MUTED
        opac = "0.2" if cnt != cx1 else "0.35"
        svg.append(f'<polygon points="{p1} {p2} {p3}" fill="{clr}" fill-opacity="{opac}" stroke="{clr}" stroke-width="1.5"/>')
        svg.append(f'<line x1="{cnt}" y1="{cy1}" x2="{cnt}" y2="{cy1+5}" stroke="{LINE}" stroke-width="1"/>')
        svg.append(text(cnt, cy1+18, lbl, size=12, anchor="middle", color=INK))

    # Ideal LPF rectangular window overlay
    lpf_left = cx1 - 60
    lpf_right = cx1 + 60
    lpf_top = cy1 - 80
    svg.append(f'<rect x="{lpf_left}" y="{lpf_top}" width="120" height="80" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,4"/>')
    svg.append(fitbox(cx1 - 55, lpf_top - 26, 110, 22, "ФНЧ (fc = fs/2)", size=11, color=POS, fill=BG, stroke=POS))

    # Plus / Arrow in middle
    svg.append(f'<line x1="390" y1="130" x2="430" y2="130" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<polygon points="430,125 440,130 430,135" fill="{LINE}"/>')
    svg.append(text(415, 115, "Фільтрація", size=11, color=MUTED, anchor="middle"))

    # Panel 2: Reconstructed Baseband Spectrum (right)
    cx2, cy2 = 590, 180
    svg.append(text(cx2, 28, "2. Відновлений спектр", size=15, bold=True, anchor="middle", color=INK))
    
    # Axis
    svg.append(f'<line x1="460" y1="{cy2}" x2="730" y2="{cy2}" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(f'<line x1="{cx2}" y1="{cy2}" x2="{cx2}" y2="50" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(text(730, cy2+18, "f", size=13, italic=True, anchor="end", color=MUTED))

    # Single triangle
    p1 = f"{cx2 - 40},{cy2}"
    p2 = f"{cx2},{cy2 - 70}"
    p3 = f"{cx2 + 40},{cy2}"
    svg.append(f'<polygon points="{p1} {p2} {p3}" fill="{FIELD}" fill-opacity="0.4" stroke="{FIELD}" stroke-width="2"/>')
    svg.append(text(cx2 - 40, cy2+18, "-fs/2", size=11, anchor="middle", color=MUTED))
    svg.append(text(cx2 + 40, cy2+18, "+fs/2", size=11, anchor="middle", color=MUTED))
    svg.append(text(cx2, cy2+18, "0", size=12, anchor="middle", color=INK))

    # Caption box at bottom
    tb = fitbox(15, 248, 730, 42, "Дискретизація мультиплікує спектр сигналу з періодом fs. Ідеальний ФНЧ вирізає лише базову смугу [-fs/2, fs/2], знищуючи всі дзеркальні копії.", size=12, fill=FILL, stroke=LINE)
    svg.append(tb)

    svg.append('</svg>')
    return '\n'.join(svg)

def fig_zoh_vs_sinc():
    """Diagram 2: Time domain comparison of ZOH (staircase), FOH (linear), and Sinc (smooth continuous)"""
    w, h = 760, 320
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    svg.append(text(w/2, 28, "Порівняння методів відновлення у часовій області", size=16, bold=True, anchor="middle", color=INK))

    # Sample points
    pts = [(80, 190), (160, 110), (240, 210), (320, 90), (400, 150), (480, 230), (560, 120), (640, 180)]
    
    # Grid lines & ticks
    cy = 250
    svg.append(f'<line x1="50" y1="{cy}" x2="710" y2="{cy}" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(text(710, cy+18, "t", size=13, italic=True, anchor="end", color=MUTED))

    # 1. ZOH (Staircase) in POS color (red-ish) / dashed or thin
    zoh_path = [f"M {pts[0][0]} {cy}"]
    for i in range(len(pts)-1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        zoh_path.append(f"L {x1} {y1} L {x2} {y1}")
    zoh_path.append(f"L {pts[-1][0]} {pts[-1][1]}")
    svg.append(f'<path d="{" ".join(zoh_path)}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,3"/>')

    # 2. Linear (FOH) in NEG color (blue) / dotted
    foh_path = [f"M {pts[0][0]} {pts[0][1]}"]
    for pt in pts[1:]:
        foh_path.append(f"L {pt[0]} {pt[1]}")
    svg.append(f'<path d="{" ".join(foh_path)}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="2,2"/>')

    # 3. Smooth Sinc Curve in FIELD color (green) / thick solid
    # Smooth bezier curve passing through points
    sinc_path = [f"M {pts[0][0]} {pts[0][1]}"]
    for i in range(len(pts)-1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        # Smooth control points
        cx1_pt = x1 + (x2 - x1)*0.4
        cy1_pt = y1
        cx2_pt = x1 + (x2 - x1)*0.6
        cy2_pt = y2
        sinc_path.append(f"C {cx1_pt} {cy1_pt}, {cx2_pt} {cy2_pt}, {x2} {y2}")
    svg.append(f'<path d="{" ".join(sinc_path)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    # Draw sample stems and dots
    for i, (px, py) in enumerate(pts):
        svg.append(f'<line x1="{px}" y1="{cy}" x2="{px}" y2="{py}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
        svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{INK}"/>')
        svg.append(text(px, cy+18, f"t{i}", size=11, anchor="middle", color=MUTED))

    # Legend at top right
    leg_x = 420
    svg.append(f'<rect x="{leg_x}" y="45" width="300" height="55" fill="{FILL}" rx="4" stroke="{LINE}" stroke-width="1"/>')
    
    # Legend items
    svg.append(f'<line x1="{leg_x+15}" y1="58" x2="{leg_x+45}" y2="58" stroke="{POS}" stroke-width="2" stroke-dasharray="4,3"/>')
    svg.append(text(leg_x+52, 62, "ZOH (Фіксатор нульового порядку)", size=11, anchor="start", color=INK))

    svg.append(f'<line x1="{leg_x+15}" y1="73" x2="{leg_x+45}" y2="73" stroke="{NEG}" stroke-width="2" stroke-dasharray="2,2"/>')
    svg.append(text(leg_x+52, 77, "FOH (Лінійна інтерполяція)", size=11, anchor="start", color=INK))

    svg.append(f'<line x1="{leg_x+15}" y1="88" x2="{leg_x+45}" y2="88" stroke="{FIELD}" stroke-width="3"/>')
    svg.append(text(leg_x+52, 92, "Sinc-інтерполяція (Точне відновлення)", size=11, bold=True, anchor="start", color=FIELD))

    # Explanatory note
    tb = fitbox(20, 275, 720, 36, "ZOH дає сходинки з багатим ВЧ-спектром; лінійна — ламану лінію; ідеальна Sinc-інтерполяція дає єдино точну гладеньку аналогову хвилю.", size=12, fill=BG, stroke=LINE)
    svg.append(tb)

    svg.append('</svg>')
    return '\n'.join(svg)

def fig_sinc_overlap():
    """Diagram 3: Summation of shifted sinc functions passing through zero at other sampling instants"""
    w, h = 760, 320
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    svg.append(text(w/2, 26, "Магія sinc-функції: нулі в сусідніх відліках", size=16, bold=True, anchor="middle", color=INK))

    cy = 200
    svg.append(f'<line x1="40" y1="{cy}" x2="720" y2="{cy}" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(text(720, cy+18, "t", size=13, italic=True, anchor="end", color=MUTED))

    # Grid of sampling instants
    sample_xs = [120, 240, 360, 480, 600]
    sample_vals = [0.4, 0.95, -0.6, 0.7, 0.2]
    
    Ts_px = 120 # 1 Ts = 120px

    # Colors for individual sinc components
    colors = ["#e67e22", NEG, POS, FIELD, "#8e44ad"]

    # Draw individual sinc curves
    for i, (cx, val) in enumerate(zip(sample_xs, sample_vals)):
        amp = val * 110 # scale amplitude
        sinc_pts = []
        for px in range(40, 720, 4):
            t_norm = (px - cx) / Ts_px
            y_val = cy - amp * sinc(t_norm)
            sinc_pts.append(f"{px:.1f},{y_val:.1f}")
        
        svg.append(f'<polyline points="{" ".join(sinc_pts)}" fill="none" stroke="{colors[i]}" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="3,3"/>')

    # Draw total sum curve
    total_pts = []
    for px in range(40, 720, 3):
        y_sum = cy
        for cx, val in zip(sample_xs, sample_vals):
            amp = val * 110
            t_norm = (px - cx) / Ts_px
            y_sum -= amp * sinc(t_norm)
        total_pts.append(f"{px:.1f},{y_sum:.1f}")

    svg.append(f'<polyline points="{" ".join(total_pts)}" fill="none" stroke="{INK}" stroke-width="3"/>')

    # Draw sample stems and dots
    for i, (cx, val) in enumerate(zip(sample_xs, sample_vals)):
        cy_pt = cy - val * 110
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy_pt}" stroke="{INK}" stroke-width="2"/>')
        svg.append(f'<circle cx="{cx}" cy="{cy_pt}" r="5" fill="{colors[i]}"/>')
        lbl = f"n={i-2}"
        lbl_y = cy - 12 if val < 0 else cy + 18
        svg.append(text(cx, lbl_y, lbl, size=11, anchor="middle", color=INK))

    # Callouts
    svg.append(text(sample_xs[1], cy - sample_vals[1]*110 - 12, "x[n]·sinc(t)", size=12, bold=True, color=NEG, anchor="middle"))
    svg.append(text(660, cy - 65, "Сумарний x(t)", size=13, bold=True, color=INK, anchor="middle"))

    # Bottom explanation
    tb = fitbox(15, 275, 730, 36, "Кожен відлік x[n] збуджує окрему sinc-хвилю. У точці будь-якого іншого відліку всі чужі sinc-функції дорівнюють РІВНО 0, тож сума x(t) точно дорівнює відліку x[n].", size=12, fill=FILL, stroke=LINE)
    svg.append(tb)

    svg.append('</svg>')
    return '\n'.join(svg)

def fig_dac_anti_imaging():
    """Diagram 4: Block diagram of real DAC + Anti-imaging filter with spectrum plots"""
    w, h = 760, 320
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    svg.append(text(w/2, 26, "Апаратне відновлення: ЦАП та згладжувальний ФНЧ (Anti-imaging)", size=16, bold=True, anchor="middle", color=INK))

    # Stage 1: Digital Stream
    b1_x, b1_y, b1_w, b1_h = 40, 70, 130, 75
    svg.append(f'<rect x="{b1_x}" y="{b1_y}" width="{b1_w}" height="{b1_h}" fill="{FILL}" rx="6" stroke="{LINE}" stroke-width="1.5"/>')
    svg.append(text(b1_x + b1_w/2, b1_y + 30, "Цифрові", size=13, bold=True, anchor="middle", color=INK))
    svg.append(text(b1_x + b1_w/2, b1_y + 50, "відліки x[n]", size=13, bold=True, anchor="middle", color=INK))

    # Arrow 1 -> 2
    svg.append(f'<line x1="{b1_x+b1_w}" y1="107" x2="220" y2="107" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<polygon points="220,102 230,107 220,112" fill="{LINE}"/>')

    # Stage 2: DAC (ZOH)
    b2_x, b2_y, b2_w, b2_h = 230, 70, 140, 75
    svg.append(f'<rect x="{b2_x}" y="{b2_y}" width="{b2_w}" height="{b2_h}" fill="{FILL}" rx="6" stroke="{POS}" stroke-width="2"/>')
    svg.append(text(b2_x + b2_w/2, b2_y + 30, "ЦАП (DAC)", size=14, bold=True, anchor="middle", color=POS))
    svg.append(text(b2_x + b2_w/2, b2_y + 52, "Фіксатор ZOH", size=12, anchor="middle", color=INK))

    # Arrow 2 -> 3
    svg.append(f'<line x1="{b2_x+b2_w}" y1="107" x2="420" y2="107" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<polygon points="420,102 430,107 420,112" fill="{LINE}"/>')
    svg.append(text(400, 95, "Ступені", size=11, color=MUTED, anchor="middle"))

    # Stage 3: Anti-Imaging Filter
    b3_x, b3_y, b3_w, b3_h = 430, 70, 160, 75
    svg.append(f'<rect x="{b3_x}" y="{b3_y}" width="{b3_w}" height="{b3_h}" fill="{FILL}" rx="6" stroke="{FIELD}" stroke-width="2"/>')
    svg.append(text(b3_x + b3_w/2, b3_y + 30, "Згладжувальний", size=13, bold=True, anchor="middle", color=FIELD))
    svg.append(text(b3_x + b3_w/2, b3_y + 50, "ФНЧ (Anti-imaging)", size=13, bold=True, anchor="middle", color=FIELD))

    # Arrow 3 -> Out
    svg.append(f'<line x1="{b3_x+b3_w}" y1="107" x2="710" y2="107" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<polygon points="710,102 720,107 710,112" fill="{LINE}"/>')

    # Output text
    svg.append(text(655, 92, "Аналоговий", size=12, bold=True, anchor="middle", color=INK))
    svg.append(text(655, 125, "сигнал x(t)", size=12, bold=True, anchor="middle", color=INK))

    # Spectral illustrations below blocks
    # Under DAC: spectrum with sinc envelope and image replicas
    spec1_cx, spec1_cy = 300, 230
    svg.append(text(spec1_cx, 165, "Спектр після ЦАП (з образами):", size=12, bold=True, anchor="middle", color=POS))
    svg.append(f'<line x1="190" y1="{spec1_cy}" x2="410" y2="{spec1_cy}" stroke="{LINE}" stroke-width="1.5"/>')
    
    # Baseband + Images
    for offset, alpha in [(-90, 0.3), (0, 0.8), (90, 0.3)]:
        cx = spec1_cx + offset
        p1 = f"{cx-30},{spec1_cy}"
        p2 = f"{cx},{spec1_cy-40}"
        p3 = f"{cx+30},{spec1_cy}"
        svg.append(f'<polygon points="{p1} {p2} {p3}" fill="{POS}" fill-opacity="{alpha}" stroke="{POS}"/>')
    
    # Sinc envelope curve (dashed)
    sinc_env = []
    for px in range(190, 415, 5):
        fnorm = (px - spec1_cx) / 90.0
        env_y = spec1_cy - 48 * abs(sinc(fnorm))
        sinc_env.append(f"{px},{env_y:.1f}")
    svg.append(f'<polyline points="{" ".join(sinc_env)}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="3,3"/>')
    svg.append(text(spec1_cx + 80, spec1_cy - 45, "sinc-обвідна ЦАП", size=10, color=MUTED, anchor="start"))

    # Under Filter: spectrum after LPF (only baseband left)
    spec2_cx, spec2_cy = 550, 230
    svg.append(text(spec2_cx, 165, "Спектр після ФНЧ (чистий):", size=12, bold=True, anchor="middle", color=FIELD))
    svg.append(f'<line x1="460" y1="{spec2_cy}" x2="640" y2="{spec2_cy}" stroke="{LINE}" stroke-width="1.5"/>')
    
    # Single Baseband triangle
    p1 = f"{spec2_cx-30},{spec2_cy}"
    p2 = f"{spec2_cx},{spec2_cy-40}"
    p3 = f"{spec2_cx+30},{spec2_cy}"
    svg.append(f'<polygon points="{p1} {p2} {p3}" fill="{FIELD}" fill-opacity="0.5" stroke="{FIELD}" stroke-width="2"/>')
    svg.append(text(spec2_cx, spec2_cy+16, "0", size=11, anchor="middle", color=INK))

    # Bottom summary box
    tb = fitbox(15, 275, 730, 36, "ЦАП створює ступені з вищими гармоніками (образами). Аналоговий ФНЧ (anti-imaging filter) зрізає ці образи вище fs/2, перетворюючи ступені на гладеньку напругу.", size=12, fill=FILL, stroke=LINE)
    svg.append(tb)

    svg.append('</svg>')
    return '\n'.join(svg)

def main():
    figs = {
        'ideal-reconstruction.svg': fig_ideal_reconstruction(),
        'zoh-vs-sinc.svg': fig_zoh_vs_sinc(),
        'sinc-overlap.svg': fig_sinc_overlap(),
        'dac-anti-imaging.svg': fig_dac_anti_imaging(),
    }
    
    for filename, content in figs.items():
        filepath = os.path.join(IMG_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {filepath}")

if __name__ == '__main__':
    main()
