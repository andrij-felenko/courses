# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/electromagnetism/electrophoresis/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_force_balance():
    width, height = 660, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Electric field background arrows (avoid y = 260 where textbox sits)
    for y_pos in [45, 90, 320]:
        out.append(line(30, y_pos, 630, y_pos, color="#e2e8f0", sw=1.5, dash="6,4"))
        out.append(arrow(320, y_pos, 360, y_pos, color="#cbd5e1", sw=1.5))
    out.append(text(570, 30, "Поле E →", size=13, color=FIELD, bold=True))

    # Central charged particle
    cx, cy = 230, 180
    radius = 50

    # Fluid environment representation (solvent molecules / water dipoles)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{radius + 20}" fill="#f0fdf4" stroke="#bbf7d0" stroke-width="1.5" stroke-dasharray="4,3"/>')
    out.append(text(cx, cy - radius - 26, "Рідке середовище (в'язкість η)", size=12, color=MUTED, italic=True))

    # Spherical particle
    out.append(circle(cx, cy, radius, fill="#fef2f2", stroke=POS, sw=2.5))
    out.append(text(cx, cy - 8, "Заряд q (+)", size=14, color=POS, bold=True))
    out.append(text(cx, cy + 14, "Радіус r", size=12, color=MUTED))

    # Electric force vector (Fe = q*E) pointing right
    fe_len = 150
    out.append(line(cx + radius, cy, cx + radius + fe_len, cy, color=POS, sw=3.5))
    out.append(arrow(cx + radius + fe_len - 10, cy, cx + radius + fe_len, cy, color=POS, sw=3.5))
    out.append(text(cx + radius + fe_len / 2, cy - 14, "F_e = q · E", size=14, color=POS, bold=True))

    # Drag force vector (Fd = 6*pi*eta*r*v) pointing left
    fd_len = 150
    out.append(line(cx - radius, cy, cx - radius - fd_len, cy, color=NEG, sw=3.5))
    out.append(arrow(cx - radius - fd_len + 10, cy, cx - radius - fd_len, cy, color=NEG, sw=3.5))
    out.append(text(cx - radius - fd_len / 2, cy - 14, "F_d = 6·π·η·r·v", size=14, color=NEG, bold=True))

    # Velocity vector v pointing right
    out.append(arrow(cx, cy + radius + 25, cx + 90, cy + radius + 25, color=FIELD, sw=2.5))
    out.append(text(cx + 45, cy + radius + 45, "Дрейфова швидкість v", size=13, color=FIELD, bold=True))

    # Formula box at bottom right
    fbox, fw, fh = textbox(520, 260, "Усталений режим (F_e = F_d):\n\nq · E = 6 · π · η · r · v\n\nv = μ_e · E\n\nμ_e = q / (6 · π · η · r)", size=13, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(fbox)

    out.append('</svg>')
    return "\n".join(out)


def generate_double_layer():
    width, height = 760, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Left side: Charged surface
    wall_x = 110
    out.append(rect(25, 45, wall_x - 25, 335, fill="#f1f5f9", stroke=LINE, sw=2, rx=0))
    out.append(mtext(68, 200, "Тверда\nповерхня\n(заряд −)", size=13, color=INK, bold=True))

    # Negative surface charges
    for y_pos in range(65, 360, 48):
        out.append(circle(wall_x - 12, y_pos, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
        out.append(text(wall_x - 12, y_pos + 3.5, "−", size=14, color=NEG, bold=True))

    # Stern Layer boundary (bound counter-ions)
    stern_x = 185
    out.append(line(stern_x, 50, stern_x, 370, color=MUTED, sw=1.5, dash="4,3"))
    out.append(text(stern_x, 28, "Шар Штерна", size=12, color=MUTED, bold=True))

    # Stern layer cations (tightly bound)
    for y_pos in range(80, 350, 55):
        out.append(circle(stern_x - 30, y_pos, 10, fill="#fdecea", stroke=POS, sw=2))
        out.append(text(stern_x - 30, y_pos + 4, "+", size=15, color=POS, bold=True))

    # Hydrodynamic Shear Plane (Slip Plane / площина ковзання)
    slip_x = 285
    out.append(line(slip_x, 50, slip_x, 370, color=FIELD, sw=2, dash="6,3"))
    out.append(text(slip_x, 28, "Площина ковзання", size=12, color=FIELD, bold=True))

    # Diffuse Layer ions (mobile cations and anions)
    diffuse_cations = [(325, 95), (355, 175), (405, 105), (335, 255), (385, 315), (445, 205)]
    for cx, cy in diffuse_cations:
        out.append(circle(cx, cy, 9, fill="#fdecea", stroke=POS, sw=1.5))
        out.append(text(cx, cy + 3.5, "+", size=13, color=POS, bold=True))

    diffuse_anions = [(375, 145), (425, 85), (405, 245), (455, 305), (455, 135)]
    for ax, ay in diffuse_anions:
        out.append(circle(ax, ay, 9, fill="#eaf0fd", stroke=NEG, sw=1.5))
        out.append(text(ax, ay + 3.5, "−", size=13, color=NEG, bold=True))

    # Potential graph on the right bottom
    gx0, gy0 = 510, 340
    gw, gh = 200, 240

    out.append(arrow(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.5)) # x axis (distance r)
    out.append(arrow(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.5)) # potential axis psi
    out.append(text(gx0 + gw - 15, gy0 + 22, "Відстань x", size=12, color=INK))
    out.append(text(gx0 - 35, gy0 - gh - 8, "Потенціал ψ", size=12, color=INK, bold=True))

    # Key potential levels
    y_psi0 = gy0 - 200
    out.append(line(gx0 - 4, y_psi0, gx0 + 4, y_psi0, color=INK, sw=1.5))
    out.append(text(gx0 - 15, y_psi0 + 4, "ψ₀", size=12, color=INK, bold=True, anchor="end"))

    x_stern_g = gx0 + 35
    y_psid = gy0 - 140
    out.append(line(x_stern_g, gy0, x_stern_g, y_psi0 - 10, color=MUTED, sw=1, dash="2,2"))

    x_slip_g = gx0 + 75
    y_zeta = gy0 - 100
    out.append(line(x_slip_g, gy0, x_slip_g, y_psi0 - 10, color=FIELD, sw=1.5, dash="3,3"))
    out.append(text(x_slip_g, gy0 + 22, "x_ковз", size=11, color=FIELD))
    out.append(line(gx0 - 4, y_zeta, x_slip_g + 40, y_zeta, color=FIELD, sw=1.5, dash="3,3"))
    out.append(text(x_slip_g + 45, y_zeta + 4, "Дзета ζ", size=12, color=FIELD, bold=True, anchor="start"))

    import math
    curve_pts = [f"{gx0},{y_psi0}", f"{x_stern_g},{y_psid}", f"{x_slip_g},{y_zeta}"]
    for step in range(x_slip_g - gx0, gw - 20, 5):
        x_val = gx0 + step
        dx_diff = x_val - x_slip_g
        y_val = gy0 - (gy0 - y_zeta) * math.exp(-dx_diff / 35.0)
        curve_pts.append(f"{x_val:.1f},{y_val:.1f}")

    path_str = "M " + " L ".join(curve_pts)
    out.append(f'<path d="{path_str}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    out.append('</svg>')
    return "\n".join(out)


def generate_gel_electrophoresis():
    width, height = 720, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Gel slab
    gx, gy, gw, gh = 150, 50, 440, 260
    out.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke=LINE, sw=2, rx=4))
    out.append(text(gx + gw / 2, gy - 15, "Пористий гель (агароза / поліакриламід)", size=14, color=INK, bold=True))

    # Electrodes (placed strictly outside gel)
    # Cathode (-) at left (x = gx - 50)
    out.append(line(gx - 50, gy, gx - 50, gy + gh, color=NEG, sw=4))
    out.append(circle(gx - 50, gy + 20, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    out.append(text(gx - 50, gy + 24, "−", size=18, color=NEG, bold=True))
    out.append(text(gx - 90, gy + gh / 2, "Катод (−)", size=13, color=NEG, bold=True, anchor="middle"))

    # Anode (+) at right (x = gx + gw + 50)
    out.append(line(gx + gw + 50, gy, gx + gw + 50, gy + gh, color=POS, sw=4))
    out.append(circle(gx + gw + 50, gy + 20, 12, fill="#fdecea", stroke=POS, sw=2))
    out.append(text(gx + gw + 50, gy + 24, "+", size=18, color=POS, bold=True))
    out.append(text(gx + gw + 90, gy + gh / 2, "Анод (+)", size=13, color=POS, bold=True, anchor="middle"))

    # Electric field direction arrow
    out.append(arrow(gx + 20, gy + gh + 25, gx + gw - 20, gy + gh + 25, color=FIELD, sw=2.5))
    out.append(text(gx + gw / 2, gy + gh + 45, "Напрямок електричного поля E (і дрейфу негативних молекул ДНК)", size=12, color=FIELD, bold=True))

    # Sample wells (лунки) at the cathode end inside gel
    well_x = gx + 30
    well_ys = [gy + 40, gy + 120, gy + 200]
    for wy in well_ys:
        out.append(rect(well_x, wy, 15, 35, fill="#cbd5e1", stroke=MUTED, sw=1.5, rx=2))
    out.append(text(well_x + 7, gy + 25, "Лунки", size=12, color=MUTED, bold=True))

    # DNA Bands migrating through gel mesh
    lane1_y = gy + 57
    out.append(rect(gx + 100, lane1_y - 12, 12, 24, fill="#1e293b", stroke="#0f172a", sw=1, rx=2))
    out.append(text(gx + 100, lane1_y - 20, "1000 п.н.", size=11, color=MUTED))

    out.append(rect(gx + 220, lane1_y - 12, 10, 24, fill="#334155", stroke="#0f172a", sw=1, rx=2))
    out.append(text(gx + 220, lane1_y - 20, "500 п.н.", size=11, color=MUTED))

    out.append(rect(gx + 360, lane1_y - 12, 8, 24, fill="#475569", stroke="#0f172a", sw=1, rx=2))
    out.append(text(gx + 360, lane1_y - 20, "100 п.н.", size=11, color=MUTED))

    # Lane 2: Sample A
    lane2_y = gy + 137
    out.append(rect(gx + 220, lane2_y - 12, 10, 24, fill=POS, stroke="#991b1b", sw=1, rx=2))
    out.append(rect(gx + 360, lane2_y - 12, 8, 24, fill=POS, stroke="#991b1b", sw=1, rx=2))

    # Lane 3: Sample B
    lane3_y = gy + 217
    out.append(rect(gx + 100, lane3_y - 12, 12, 24, fill=NEG, stroke="#1e40af", sw=1, rx=2))

    # Gel mesh texture representation in middle
    for mx in range(gx + 150, gx + 320, 30):
        for my in range(gy + 35, gy + gh - 30, 35):
            out.append(line(mx, my, mx + 15, my + 15, color="#e2e8f0", sw=1))
            out.append(line(mx + 15, my, mx, my + 15, color="#e2e8f0", sw=1))

    out.append('</svg>')
    return "\n".join(out)


def generate_capillary_eof():
    width, height = 720, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Capillary tube boundaries (top and bottom silica walls)
    cap_x1, cap_x2 = 60, 660
    top_y = 80
    bot_y = 260

    # Upper silica wall
    out.append(rect(cap_x1, top_y - 25, cap_x2 - cap_x1, 25, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=0))
    out.append(text((cap_x1 + cap_x2)/2, top_y - 10, "Стінка кварцового капіляра (SiO₂)", size=13, color=INK, bold=True))

    # Lower silica wall
    out.append(rect(cap_x1, bot_y, cap_x2 - cap_x1, 25, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=0))
    out.append(text((cap_x1 + cap_x2)/2, bot_y + 17, "Стінка кварцового капіляра (SiO₂)", size=13, color=INK, bold=True))

    # Negatively charged silanol groups (Si-O-) on top and bottom inner surfaces
    for x_pos in range(cap_x1 + 30, cap_x2 - 20, 50):
        out.append(circle(x_pos, top_y + 8, 7, fill="#eaf0fd", stroke=NEG, sw=1.2))
        out.append(text(x_pos, top_y + 11.5, "−", size=11, color=NEG, bold=True))
        out.append(circle(x_pos, bot_y - 8, 7, fill="#eaf0fd", stroke=NEG, sw=1.2))
        out.append(text(x_pos, bot_y - 4.5, "−", size=11, color=NEG, bold=True))

    # Cation layer (Na+) dragged by electric field
    for x_pos in range(cap_x1 + 30, cap_x2 - 20, 50):
        out.append(circle(x_pos, top_y + 24, 7, fill="#fdecea", stroke=POS, sw=1.2))
        out.append(text(x_pos, top_y + 27.5, "+", size=11, color=POS, bold=True))
        out.append(circle(x_pos, bot_y - 24, 7, fill="#fdecea", stroke=POS, sw=1.2))
        out.append(text(x_pos, bot_y - 20.5, "+", size=11, color=POS, bold=True))

    # Velocity profiles comparison (Plug Flow EOF vs Parabolic Poiseuille Flow)
    prof_x = 100
    mid_y = (top_y + bot_y) / 2
    out.append(line(prof_x, top_y + 35, prof_x, bot_y - 35, color=MUTED, sw=1.5, dash="3,3"))
    for y_arr in range(top_y + 42, bot_y - 32, 22):
        out.append(arrow(prof_x, y_arr, prof_x + 60, y_arr, color=FIELD, sw=2))
    out.append(line(prof_x + 60, top_y + 38, prof_x + 60, bot_y - 38, color=FIELD, sw=2.5))
    out.append(text(prof_x + 30, top_y + 48, "Плоский ЕОП", size=12, color=FIELD, bold=True))

    # Separation zones moving to Cathode (Detector on the right)
    # Cations (Fastest: mu_e + mu_eof)
    out.append(circle(prof_x + 360, mid_y, 18, fill="#fdecea", stroke=POS, sw=2))
    out.append(text(prof_x + 360, mid_y + 5, "Катіони", size=11, color=POS, bold=True))

    # Neutrals (Medium: mu_eof)
    out.append(circle(prof_x + 260, mid_y, 18, fill="#f4f6f8", stroke=MUTED, sw=2))
    out.append(text(prof_x + 260, mid_y + 5, "Нейтральні", size=10, color=MUTED, bold=True))

    # Anions (Slowest: mu_eof - |mu_e|)
    out.append(circle(prof_x + 160, mid_y, 18, fill="#eaf0fd", stroke=NEG, sw=2))
    out.append(text(prof_x + 160, mid_y + 5, "Аніони", size=11, color=NEG, bold=True))

    # Right Detector / Cathode (-) label
    out.append(mtext(cap_x2 - 50, bot_y + 45, "До детектора\n(Катод −)", size=12, color=NEG, bold=True))

    out.append('</svg>')
    return "\n".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    files = {
        'electrophoretic-force-balance.svg': generate_force_balance(),
        'electric-double-layer.svg': generate_double_layer(),
        'gel-electrophoresis-principle.svg': generate_gel_electrophoresis(),
        'capillary-electrophoresis-eof.svg': generate_capillary_eof()
    }

    for fname, content in files.items():
        path = os.path.join(img_dir, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == '__main__':
    main()
