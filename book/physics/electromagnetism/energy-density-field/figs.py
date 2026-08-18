# -*- coding: utf-8 -*-
import sys
import os
import math

# Four levels up to reach scripts/ from book/physics/electromagnetism/energy-density-field/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_capacitor_energy_flow(filepath):
    width, height = 640, 380
    frags = []

    # Capacitor Plates
    plate_left = 140
    plate_right = 360
    top_y = 110
    bot_y = 270

    frags.append(rect(plate_left, top_y - 14, plate_right - plate_left, 14, fill="#fee2e2", stroke=POS, sw=2, rx=2))
    frags.append(text((plate_left + plate_right) / 2, top_y - 24, "Верхня пластина (+Q)", size=13, color=POS, bold=True))

    frags.append(rect(plate_left, bot_y, plate_right - plate_left, 14, fill="#dbeafe", stroke=NEG, sw=2, rx=2))
    frags.append(text((plate_left + plate_right) / 2, bot_y + 30, "Нижня пластина (−Q)", size=13, color=NEG, bold=True))

    # Electric Field E lines downwards
    for x_pos in range(plate_left + 35, plate_right, 45):
        frags.append(line(x_pos, top_y, x_pos, bot_y, color=POS, sw=1.8, dash="4,3"))
        frags.append(arrow(x_pos, top_y + 10, x_pos, bot_y - 10, color=POS, sw=2))

    frags.append(text(plate_left + 15, (top_y + bot_y) / 2, "Поле E", size=13, color=POS, bold=True))

    # Poynting Vector S entering radially into the capacitor volume from sides
    # Left side Poynting vector S (pointing right)
    frags.append(arrow(35, (top_y + bot_y) / 2, plate_left - 10, (top_y + bot_y) / 2, color="#d97706", sw=3))
    frags.append(text(80, (top_y + bot_y) / 2 - 15, "S = E × H", size=13, color="#d97706", bold=True))

    # Right side Poynting vector S (pointing left)
    frags.append(arrow(460, (top_y + bot_y) / 2, plate_right + 10, (top_y + bot_y) / 2, color="#d97706", sw=3))
    frags.append(text(415, (top_y + bot_y) / 2 - 15, "S (всередину)", size=13, color="#d97706", bold=True))

    # Volume shaded region representing stored field energy w_e
    frags.append(rect(plate_left + 5, top_y + 5, (plate_right - plate_left) - 10, (bot_y - top_y) - 10, fill="#f0fdf4", stroke="none", rx=4))

    # Formula Box on the right
    fbox, fw, fh = textbox(540, 190, "Об'ємна густина:\n\nw_e = ½ · ε₀ · E²\n\nПовна енергія:\nW = ∭ w_e dV\nW = ½ · C · U²\n\nВектор S входить\nу зазор збоку.", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(fbox)

    return render(filepath, width, height, *frags)


def generate_solenoid_energy_density(filepath):
    width, height = 640, 360
    frags = []

    y_top = 110
    y_bot = 250
    x_start = 80
    dx = 35
    num_turns = 9

    # Shaded volume storing magnetic energy w_m
    frags.append(rect(x_start - 5, y_top + 10, num_turns * dx + 10, y_bot - y_top - 20, fill="#f0fdf4", stroke="none"))

    for i in range(num_turns):
        x = x_start + i * dx
        # Top wire cross section (dots)
        frags.append(circle(x, y_top, 8, fill="#fef2f2", stroke=POS, sw=1.8))
        frags.append(circle(x, y_top, 2, fill=POS, stroke=POS, sw=1))
        # Bottom wire cross section (crosses)
        frags.append(circle(x, y_bot, 8, fill="#eff6ff", stroke=NEG, sw=1.8))
        frags.append(line(x - 3.5, y_bot - 3.5, x + 3.5, y_bot + 3.5, color=NEG, sw=1.6))
        frags.append(line(x + 3.5, y_bot - 3.5, x - 3.5, y_bot + 3.5, color=NEG, sw=1.6))

    frags.append(text(x_start - 45, y_top + 4, "⊙ I", size=13, color=POS, bold=True))
    frags.append(text(x_start - 45, y_bot + 4, "⊗ I", size=13, color=NEG, bold=True))

    # Magnetic field B inside solenoid (pointing right)
    y_mid = (y_top + y_bot) / 2
    for dy in [-40, 0, 40]:
        frags.append(line(x_start - 10, y_mid + dy, x_start + num_turns * dx + 10, y_mid + dy, color=FIELD, sw=2, dash="5,4"))
        frags.append(arrow(x_start + 120, y_mid + dy, x_start + 160, y_mid + dy, color=FIELD, sw=2))

    frags.append(text(x_start + 40, y_mid - 20, "Магнітне поле B", size=13, color=FIELD, bold=True))

    # Radial Poynting vector S during current rise (pointing inwards from windings)
    frags.append(arrow(x_start + 260, y_top + 15, x_start + 260, y_mid - 25, color="#d97706", sw=2.5))
    frags.append(arrow(x_start + 260, y_bot - 15, x_start + 260, y_mid + 25, color="#d97706", sw=2.5))
    frags.append(text(x_start + 295, y_top + 35, "S (всередину)", size=12, color="#d97706", bold=True))

    # Formula Box
    fbox, fw, fh = textbox(530, 180, "Густина енергії:\n\nw_m = ½ · (B² / μ₀)\n\nЕнергія котушки:\nW = ∭ w_m dV\nW = ½ · L · I²\n\nПотік S вкачує\nенергію всередину.", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(fbox)

    return render(filepath, width, height, *frags)


def generate_poynting_vector_wave(filepath):
    width, height = 640, 360
    frags = []

    # 3D Cartesian Coordinate Axes
    ox, oy = 70, 200
    z_len = 340

    frags.append(arrow(ox, oy, ox + z_len + 30, oy, color=INK, sw=2)) # z axis
    frags.append(text(ox + z_len + 20, oy + 25, "z (напрямок)", size=13, color=INK, bold=True))

    frags.append(arrow(ox, oy, ox, oy - 140, color=POS, sw=2)) # E axis (y)
    frags.append(text(ox - 25, oy - 140, "E", size=14, color=POS, bold=True))

    frags.append(arrow(ox, oy, ox - 45, oy + 65, color=FIELD, sw=2)) # B axis (x)
    frags.append(text(ox - 65, oy + 70, "B", size=14, color=FIELD, bold=True))

    # Sine waves E(z) and B(z)
    e_pts = []
    b_pts = []

    for z in range(0, z_len + 1, 4):
        rad = 2 * math.pi * z / 170
        # E wave vertical
        ey = oy - 75 * math.sin(rad)
        e_pts.append(f"{ox + z:.1f},{ey:.1f}")

        # B wave oblique
        b_val = 55 * math.sin(rad)
        bx = ox + z - b_val * 0.55
        by = oy + b_val * 0.55
        b_pts.append(f"{bx:.1f},{by:.1f}")

    # Draw E wave path
    frags.append(f'<path d="M {" L ".join(e_pts)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    # Draw B wave path
    frags.append(f'<path d="M {" L ".join(b_pts)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Poynting Vector S along z axis
    frags.append(arrow(ox + 85, oy, ox + 175, oy, color="#d97706", sw=4))
    frags.append(text(ox + 130, oy - 15, "S = E × H", size=13, color="#d97706", bold=True))

    # Formula Box
    fbox, fw, fh = textbox(530, 180, "Плоска ЕМ-хвиля:\n\nw_e = w_m = ½·ε₀·E²\n\nw = ε₀ · E²\n\nМодуль Пойнтінга:\nS = c · w\n\nІнтенсивність:\nI = ⟨S⟩ = ½·ε₀·c·E₀²", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(fbox)

    return render(filepath, width, height, *frags)


def generate_coaxial_energy_transport(filepath):
    width, height = 640, 360
    frags = []

    # Coaxial Cable Cross-Section (Left) and Longitudinal View (Right)
    cx, cy = 130, 180
    r_core = 20
    r_shld = 80

    # Outer Shield conductor
    frags.append(circle(cx, cy, r_shld + 10, fill="#e2e8f0", stroke=LINE, sw=1.5))
    frags.append(circle(cx, cy, r_shld, fill="#f0fdf4", stroke=NEG, sw=2.5))
    frags.append(text(cx, cy - r_shld - 18, "Зовнішній екран", size=12, color=NEG, bold=True))

    # Inner Core conductor
    frags.append(circle(cx, cy, r_core, fill="#fee2e2", stroke=POS, sw=2.5))
    frags.append(text(cx, cy + 4, "⊙ I", size=13, color=POS, bold=True))

    # Radial E lines
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        x1 = cx + (r_core + 2) * math.cos(rad)
        y1 = cy + (r_core + 2) * math.sin(rad)
        x2 = cx + (r_shld - 2) * math.cos(rad)
        y2 = cy + (r_shld - 2) * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color=POS, sw=1.5, dash="3,3"))

    # Concentric B field circle
    frags.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="50.0" fill="none" stroke="{FIELD}" stroke-width="2" stroke-dasharray="6,4"/>')

    # Longitudinal View of Cable
    lx1, lx2 = 280, 420
    y_top_shld = 100
    y_top_core = 150
    y_bot_core = 210
    y_bot_shld = 260

    frags.append(rect(lx1, y_top_shld - 10, lx2 - lx1, 10, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(rect(lx1, y_bot_shld, lx2 - lx1, 10, fill="#dbeafe", stroke=NEG, sw=1.5))

    frags.append(rect(lx1, y_top_core, lx2 - lx1, y_bot_core - y_top_core, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text((lx1 + lx2)/2, (y_top_core + y_bot_core)/2 + 4, "Жила (+U)", size=12, color=POS, bold=True))

    # Radial E field arrows
    frags.append(arrow(320, y_top_core, 320, y_top_shld, color=POS, sw=1.5))
    frags.append(arrow(320, y_bot_core, 320, y_bot_shld, color=POS, sw=1.5))

    # Poynting Vector S flowing inside the dielectric gap to the right
    frags.append(arrow(lx1 + 15, (y_top_shld + y_top_core)/2, lx2 - 15, (y_top_shld + y_top_core)/2, color="#d97706", sw=3))
    frags.append(arrow(lx1 + 15, (y_bot_shld + y_bot_core)/2, lx2 - 15, (y_bot_shld + y_bot_core)/2, color="#d97706", sw=3))
    frags.append(text((lx1 + lx2)/2, (y_top_shld + y_top_core)/2 - 14, "Потік S", size=12, color="#d97706", bold=True))

    # Formula Box
    fbox, fw, fh = textbox(530, 180, "Парадокс кабелю:\n\nЕнергія передається\nу діелектричному\nпросторі МІЖ\nпровідниками!\n\nP = ∬ S · dS = U · I", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(fbox)

    return render(filepath, width, height, *frags)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    generate_capacitor_energy_flow(os.path.join(img_dir, 'capacitor-energy-flow.svg'))
    generate_solenoid_energy_density(os.path.join(img_dir, 'solenoid-energy-density.svg'))
    generate_poynting_vector_wave(os.path.join(img_dir, 'poynting-vector-wave.svg'))
    generate_coaxial_energy_transport(os.path.join(img_dir, 'coaxial-energy-transport.svg'))
    print("Generated all figures successfully.")

if __name__ == '__main__':
    main()
