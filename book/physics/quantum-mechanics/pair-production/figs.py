# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_pair_production():
    width, height = 640, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Heavy Nucleus Z
    nx, ny = 220, 180
    out.append(f'<circle cx="{nx}" cy="{ny}" r="28" fill="#fee2e2" stroke="{POS}" stroke-width="2.5"/>')
    out.append(text(nx, ny + 5, "Ядро Z", size=14, color=POS, bold=True, anchor="middle"))

    # Interaction region circle
    out.append(f'<circle cx="{nx}" cy="{ny}" r="65" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Incoming Gamma Photon
    out.append(line(30, ny, nx - 25, ny, color="#7c3aed", sw=2.5, dash="6,3"))
    out.append(arrow(110, ny, 160, ny, color="#7c3aed", sw=2.5))
    out.append(text(90, ny - 16, "γ-фотон (E ≥ 2m_e c²)", size=14, color="#7c3aed", bold=True, anchor="middle"))

    # Nucleus recoil vector
    out.append(arrow(nx, ny + 28, nx - 45, ny + 85, color=MUTED, sw=2))
    out.append(text(nx - 75, ny + 95, "Віддача ядра q_N", size=12, color=MUTED, italic=True))

    # Created Electron e- curved path
    e_path = f"M {nx+25} {ny-10} Q {nx+120} {ny-90} {width-60} {ny-110}"
    out.append(f'<path d="{e_path}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    out.append(arrow(nx+150, ny-75, nx+180, ny-87, color=NEG, sw=3))
    out.append(f'<circle cx="{width-60}" cy="{ny-110}" r="7" fill="{NEG}"/>')
    out.append(text(width-60, ny-128, "Електрон e⁻", size=14, color=NEG, bold=True, anchor="middle"))

    # Created Positron e+ curved path
    p_path = f"M {nx+25} {ny+10} Q {nx+120} {ny+90} {width-60} {ny+110}"
    out.append(f'<path d="{p_path}" fill="none" stroke="{POS}" stroke-width="3"/>')
    out.append(arrow(nx+150, ny+75, nx+180, ny+87, color=POS, sw=3))
    out.append(f'<circle cx="{width-60}" cy="{ny+110}" r="7" fill="{POS}"/>')
    out.append(text(width-60, ny+130, "Позитрон e⁺", size=14, color=POS, bold=True, anchor="middle"))

    # Magnetic field indicator B (into page)
    out.append(text(width-180, 30, "Магнітне поле B (перпендикулярно)", size=12, color=MUTED, italic=True, anchor="middle"))

    out.append('</svg>')
    return '\n'.join(out)

def generate_annihilation():
    width, height = 640, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    cx, cy = 320, 180

    # Incoming Electron from left
    out.append(line(60, cy, cx - 35, cy, color=NEG, sw=3))
    out.append(arrow(140, cy, 190, cy, color=NEG, sw=3))
    out.append(f'<circle cx="{100}" cy="{cy}" r="8" fill="{NEG}"/>')
    out.append(text(100, cy - 16, "Електрон e⁻ (511 кеВ)", size=13, color=NEG, bold=True, anchor="middle"))

    # Incoming Positron from right
    out.append(line(width - 60, cy, cx + 35, cy, color=POS, sw=3))
    out.append(arrow(width - 140, cy, width - 190, cy, color=POS, sw=3))
    out.append(f'<circle cx="{width - 100}" cy="{cy}" r="8" fill="{POS}"/>')
    out.append(text(width - 100, cy - 16, "Позитрон e⁺ (511 кеВ)", size=13, color=POS, bold=True, anchor="middle"))

    # Annihilation vertex / Positronium state
    out.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    out.append(text(cx, cy + 4, "Анігіляція", size=11, color="#b45309", bold=True, anchor="middle"))

    # Emitted Photon 1 (upward)
    out.append(line(cx, cy - 22, cx, 50, color="#7c3aed", sw=2.5, dash="6,3"))
    out.append(arrow(cx, cy - 70, cx, cy - 110, color="#7c3aed", sw=2.5))
    out.append(text(cx + 18, 60, "γ₁ (511 кеВ)", size=14, color="#7c3aed", bold=True, anchor="start"))

    # Emitted Photon 2 (downward)
    out.append(line(cx, cy + 22, cx, height - 50, color="#7c3aed", sw=2.5, dash="6,3"))
    out.append(arrow(cx, cy + 70, cx, cy + 110, color="#7c3aed", sw=2.5))
    out.append(text(cx + 18, height - 50, "γ₂ (511 кеВ)", size=14, color="#7c3aed", bold=True, anchor="start"))

    # Angle 180 degrees notation
    out.append(text(cx - 85, cy - 50, "Кут розльоту 180°", size=13, color=INK, italic=True, anchor="middle"))

    out.append('</svg>')
    return '\n'.join(out)

def generate_dirac_sea():
    width, height = 640, 400
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Energy axis E
    ax = 80
    out.append(line(ax, height - 40, ax, 30, color=INK, sw=2))
    out.append(arrow(ax, 70, ax, 30, color=INK, sw=2))
    out.append(text(ax - 20, 35, "Енергія E", size=14, color=INK, bold=True, anchor="middle"))

    # Energy levels boundaries
    y_pos = 120  # +m_e c^2
    y_neg = 280  # -m_e c^2

    out.append(line(ax, y_pos, width - 60, y_pos, color=POS, sw=2))
    out.append(text(ax + 10, y_pos - 10, "E = +m_e c² (додатні стани)", size=13, color=POS, bold=True, anchor="start"))

    out.append(line(ax, y_neg, width - 60, y_neg, color=NEG, sw=2))
    out.append(text(ax + 10, y_neg + 20, "E = −m_e c² (заповнене море Дірака)", size=13, color=NEG, bold=True, anchor="start"))

    # Forbidden gap
    out.append(f'<rect x="{ax+1}" y="{y_pos+1}" width="{width-ax-61}" height="{y_neg-y_pos-2}" fill="#f3f4f6" opacity="0.6"/>')
    out.append(text(ax + 110, (y_pos + y_neg)/2 + 4, "Заборонена зона (ΔE = 2m_e c²)", size=13, color=MUTED, italic=True, anchor="middle"))

    # Dirac sea electrons (filled negative states)
    for x in range(ax + 40, width - 80, 45):
        for y in range(y_neg + 40, height - 30, 30):
            out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{NEG}"/>')

    # Excitation process: Photon absorbed
    ex_x = 420
    # Filled state before jump (hole)
    out.append(f'<circle cx="{ex_x}" cy="{y_neg + 50}" r="8" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="3,3"/>')
    out.append(text(ex_x + 15, y_neg + 55, "Дірка = Позитрон (e⁺)", size=13, color=POS, bold=True, anchor="start"))

    # Arrow jumping up
    out.append(arrow(ex_x, y_neg + 40, ex_x, y_pos - 40, color="#7c3aed", sw=2.5))
    out.append(text(ex_x + 15, (y_pos + y_neg)/2 + 4, "γ-фотон (hν ≥ 2m_e c²)", size=13, color="#7c3aed", bold=True, anchor="start"))

    # Electron in positive energy state
    out.append(f'<circle cx="{ex_x}" cy="{y_pos - 50}" r="8" fill="{NEG}"/>')
    out.append(text(ex_x + 15, y_pos - 45, "Вільний електрон (e⁻)", size=13, color=NEG, bold=True, anchor="start"))

    out.append('</svg>')
    return '\n'.join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    with open(os.path.join(img_dir, 'pair-production-process.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_pair_production())

    with open(os.path.join(img_dir, 'annihilation-process.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_annihilation())

    with open(os.path.join(img_dir, 'dirac-sea.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_dirac_sea())

    print("Figures generated successfully!")

if __name__ == '__main__':
    main()
