# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Довжина екранування Дебая"
(book/physics/condensed-matter-physics/debye-length)
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def polyline(pts_str, color=LINE, sw=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'

def save_svg(name, content):
    filepath = os.path.join(OUT_DIR, name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Збережено: {filepath}")

def make_defs():
    return '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
  </defs>'''

# 1. debye-potential-decay.svg
def gen_debye_potential_decay():
    w, h = 860, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 25, "Порівняння неекранованого потенціалу Кулона та потенціалу Дебая — Гюккеля", size=15, bold=True)[0])

    ox, oy = 90, 360
    pw, ph = 640, 260

    # Axes
    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw + 25, oy + 35, "r / λ_D (відстань)", size=12, bold=True, anchor="end"))
    out.append(text(ox + 40, oy - ph - 15, "Потенціал Φ(r) / Φ₀", size=12, bold=True, anchor="start"))

    # Grid & Reference lines for r/lambda_D = 1, 2, 3
    l_px = 150  # 1 lambda_D = 150 px

    y_scale = ph * 0.85
    y_base = oy

    # Marker lines at r = 1, 2, 3
    r_vals = [(1.0, "λ_D"), (2.0, "2λ_D"), (3.0, "3λ_D")]
    for r_val, r_lbl in r_vals:
        x_pos = ox + r_val * l_px
        out.append(line(x_pos, oy, x_pos, oy - ph + 20, color="#bdc3c7", sw=1, dash="4 4"))
        out.append(text(x_pos, oy + 22, r_lbl, size=13, bold=True, anchor="middle"))

    # Origin 0
    out.append(text(ox - 10, oy + 22, "0", size=13, anchor="end"))

    # Generate points for Coulomb V_c
    pts_coulomb = []
    pts_debye = []
    
    steps = 150
    r_start = 0.25
    r_end = 3.8

    for i in range(steps + 1):
        r = r_start + (i / steps) * (r_end - r_start)
        x_p = ox + r * l_px
        
        # Normalized values
        v_c = 0.25 / r
        v_d = (0.25 / r) * math.exp(-(r - 0.25))

        y_p_c = y_base - v_c * y_scale
        y_p_d = y_base - v_d * y_scale

        pts_coulomb.append(f"{x_p:.1f},{y_p_c:.1f}")
        pts_debye.append(f"{x_p:.1f},{y_p_d:.1f}")

    # Draw curves
    out.append(polyline(" ".join(pts_coulomb), color="#7f8c8d", sw=2.5, dash="6 4"))
    out.append(polyline(" ".join(pts_debye), color="#c0392b", sw=3))

    # Point at r = 1 lambda_D
    r_mark = 1.0
    x_mark = ox + r_mark * l_px
    v_d_mark = (0.25 / r_mark) * math.exp(-(r_mark - 0.25))
    y_mark = y_base - v_d_mark * y_scale

    out.append(circle(x_mark, y_mark, 5, fill="#c0392b"))
    out.append(line(ox, y_mark, x_mark, y_mark, color="#c0392b", sw=1, dash="3 3"))

    # Legend at top right (y = 115 and y = 135)
    out.append(line(ox + pw - 250, 115, ox + pw - 210, 115, color="#7f8c8d", sw=2.5, dash="6 4"))
    out.append(text(ox + pw - 200, 119, "Потенціал Кулона: Φ_C ∝ 1/r", size=11, anchor="start"))

    out.append(line(ox + pw - 250, 138, ox + pw - 210, 138, color="#c0392b", sw=3))
    out.append(text(ox + pw - 200, 142, "Потенціал Дебая: Φ_D ∝ (1/r)·exp(-r/λ_D)", size=11, bold=True, anchor="start", color="#c0392b"))

    # Callout Box placed at middle right (cx=480, cy=220)
    msg = "Експоненціальне екранування:\nНа відстані r = λ_D потенціал спадає в e разів\nшвидше за кулонівський закон завдяки\nперерозподілу вільних носіїв."
    out.append(fitbox(340, 175, 270, 75, msg, stroke="#c0392b", fill="#fdfefe", size=11))

    out.append("</svg>")
    save_svg("debye-potential-decay.svg", "\n".join(out))

# 2. debye-sphere-cloud.svg
def gen_debye_sphere_cloud():
    w, h = 860, 480
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 25, "Мікроскопічна будова дебаївської сфери навколо пробного заряду", size=15, bold=True)[0])

    cx, cy = 360, 240
    r_debye = 135

    # Background region outside Debye sphere
    out.append(rect(30, 70, 800, 380, fill="#f8f9fa", stroke="#bdc3c7", sw=1, rx=8))

    # Debye sphere boundary
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r_debye}" fill="#ebf5fb" stroke="#2980b9" stroke-width="2" stroke-dasharray="5 4"/>')

    # Central test charge +Q
    out.append(circle(cx, cy, 22, fill="#e74c3c", stroke="#c0392b", sw=2))
    out.append(text(cx, cy + 6, "+Q", size=16, bold=True, color="#ffffff", anchor="middle"))

    # Radius arrow
    r_angle = math.pi / 4
    rx_end = cx + r_debye * math.cos(r_angle)
    ry_end = cy - r_debye * math.sin(r_angle)
    out.append(line(cx, cy, rx_end, ry_end, color="#2980b9", sw=2, dash="3 3"))
    out.append(text(cx + 60, cy - 45, "Радіус Дебая λ_D", size=13, bold=True, color="#2980b9", anchor="start"))

    # Charges inside Debye sphere
    electron_coords_in = [
        (cx - 50, cy - 40), (cx + 60, cy - 30), (cx - 40, cy + 50),
        (cx + 45, cy + 60), (cx - 80, cy + 10), (cx + 85, cy - 10),
        (cx - 20, cy - 85), (cx + 30, cy - 90), (cx - 90, cy - 50),
        (cx + 70, cy - 80), (cx - 70, cy + 80), (cx + 90, cy + 40),
        (cx + 10, cy + 100), (cx - 100, cy - 10)
    ]

    ion_coords_in = [
        (cx + 110, cy - 60), (cx - 110, cy + 50)
    ]

    for ex, ey in electron_coords_in:
        out.append(circle(ex, ey, 9, fill="#3498db", stroke="#2980b9", sw=1))
        out.append(text(ex, ey + 4, "−", size=13, bold=True, color="#ffffff", anchor="middle"))

    for ix, iy in ion_coords_in:
        out.append(circle(ix, iy, 9, fill="#e74c3c", stroke="#c0392b", sw=1))
        out.append(text(ix, iy + 4, "+", size=12, bold=True, color="#ffffff", anchor="middle"))

    # Charges outside Debye sphere
    outside_charges = [
        (90, 110, "-"), (140, 150, "+"), (80, 230, "-"), (120, 280, "+"),
        (180, 90, "+"), (570, 100, "-"), (620, 130, "+"), (670, 90, "-"),
        (560, 210, "+"), (600, 270, "-"), (660, 220, "+"),
        (710, 310, "-"), (730, 170, "+")
    ]

    for ch_x, ch_y, ch_type in outside_charges:
        if ch_type == "-":
            out.append(circle(ch_x, ch_y, 9, fill="#3498db", stroke="#2980b9", sw=1))
            out.append(text(ch_x, ch_y + 4, "−", size=13, bold=True, color="#ffffff", anchor="middle"))
        else:
            out.append(circle(ch_x, ch_y, 9, fill="#e74c3c", stroke="#c0392b", sw=1))
            out.append(text(ch_x, ch_y + 4, "+", size=12, bold=True, color="#ffffff", anchor="middle"))

    # Annotations
    msg_neutral = "Квазінейтральна зона (r > λ_D)\nЗаряд +Q екранований повністю.\nПотенціал Φ ≈ 0, n_e ≈ n_i.\nТепловий рух k_B T переважає."
    out.append(fitbox(560, 335, 240, 85, msg_neutral, stroke="#bdc3c7", fill="#ffffff", size=11))

    msg_cloud = "Дебаївська хмара (r < λ_D)\nНадлишок протизарядів.\nКулонівське притягання\nформує екранування."
    out.append(fitbox(50, 335, 220, 85, msg_cloud, stroke="#2980b9", fill="#ffffff", size=11))

    out.append("</svg>")
    save_svg("debye-sphere-cloud.svg", "\n".join(out))

# 3. semiconductor-debye-tail.svg
def gen_semiconductor_debye_tail():
    w, h = 860, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 25, "Перехідна зона концентрації вільних носіїв (дебаївський хвіст) на межі збіднення", size=15, bold=True)[0])

    ox, oy = 90, 360
    pw, ph = 640, 260

    # Axes
    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw + 25, oy + 35, "x (координата)", size=12, bold=True, anchor="end"))
    out.append(text(ox + 40, oy - ph - 15, "Концентрація n(x)", size=12, bold=True, anchor="start"))

    # Depletion boundary at x_dep = 280 px from ox
    x_dep = ox + 260
    l_d_px = 90  # Debye length scale

    # Region shading
    out.append(rect(ox, oy - ph, 260, ph, fill="#fadbd8", stroke="none"))
    out.append(rect(ox + 260, oy - ph, pw - 260, ph, fill="#e8f8f5", stroke="none"))

    out.append(text(ox + 130, oy - ph + 25, "Збіднена зона (n ≈ 0)", size=12, bold=True, color="#c0392b", anchor="middle"))
    out.append(text(ox + 460, oy - ph + 25, "Нейтральний об'єм (n = N_D)", size=12, bold=True, color="#16a085", anchor="middle"))

    # Vertical boundary line x_dep (ideal depletion edge)
    out.append(line(x_dep, oy, x_dep, oy - ph, color="#7f8c8d", sw=1.5, dash="5 4"))
    out.append(text(x_dep, oy + 22, "x_n (межа)", size=12, bold=True, anchor="middle"))

    # Reference lines for N_D
    y_nd = oy - ph * 0.8
    out.append(line(ox, y_nd, ox + pw, y_nd, color="#bdc3c7", sw=1, dash="4 4"))
    out.append(text(ox - 10, y_nd + 4, "N_D", size=13, bold=True, anchor="end", color="#16a085"))

    # Ideal step-depletion model (dashed blue)
    pts_ideal = [f"{ox},{oy}", f"{x_dep},{oy}", f"{x_dep},{y_nd}", f"{ox+pw},{y_nd}"]
    out.append(polyline(" ".join(pts_ideal), color="#2980b9", sw=2, dash="6 4"))

    # Real smooth Debye transition curve (solid red)
    pts_real = []
    steps = 150
    for i in range(steps + 1):
        x_p = ox + (i / steps) * pw
        
        dx = (x_p - x_dep) / l_d_px
        if dx < -2.5:
            n_ratio = 0.0
        elif dx < 0:
            n_ratio = 0.5 * math.exp(2 * dx)
        else:
            n_ratio = 1.0 - 0.5 * math.exp(-2 * dx)

        y_p = oy - n_ratio * (ph * 0.8)
        pts_real.append(f"{x_p:.1f},{y_p:.1f}")

    out.append(polyline(" ".join(pts_real), color="#c0392b", sw=3))

    # Mark Debye tail width
    x_ld_left = x_dep - l_d_px * 0.8
    x_ld_right = x_dep + l_d_px * 0.8

    out.append(line(x_ld_left, oy - 40, x_ld_right, oy - 40, color="#c0392b", sw=1.5))
    out.append(text(x_dep, oy - 50, "Дебаївська розмитість ~ (2-3)·L_D", size=11, bold=True, color="#c0392b", anchor="middle"))

    # Callout box
    msg_tail = "Дебаївський хвіст носіїв:\nРеальний розподіл не є різким ступенем.\nНосії розмивають межу збіднення на\nдовжині екранування L_D = √(ε·k_B·T / q²·N_D)."
    out.append(fitbox(ox + 280, oy - 160, 300, 85, msg_tail, stroke="#c0392b", fill="#ffffff", size=11))

    out.append("</svg>")
    save_svg("semiconductor-debye-tail.svg", "\n".join(out))

if __name__ == "__main__":
    gen_debye_potential_decay()
    gen_debye_sphere_cloud()
    gen_semiconductor_debye_tail()
