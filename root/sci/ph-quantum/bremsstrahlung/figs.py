# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_mechanism():
    width, height = 720, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Nucleus Ze
    nx, ny = 360, 270
    out.append(f'<circle cx="{nx}" cy="{ny}" r="32" fill="#fee2e2" stroke="{POS}" stroke-width="2.5"/>')
    out.append(text(nx, ny + 5, "Ядро +Ze", size=15, color=POS, bold=True, anchor="middle"))

    # Coulomb field circles (concentric dash)
    for r_c in [70, 120, 170]:
        out.append(f'<circle cx="{nx}" cy="{ny}" r="{r_c}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4" opacity="0.5"/>')
    out.append(text(nx + 175, ny + 20, "Кулонівське поле", size=12, color=MUTED, italic=True, anchor="start"))

    # Trajectory of electron
    e_path = "M 80 110 L 240 110 C 310 110 340 140 360 165 C 380 190 430 210 500 205 L 660 200"
    out.append(f'<path d="{e_path}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    out.append(arrow(160, 110, 200, 110, color=NEG, sw=3))
    out.append(arrow(550, 203, 600, 201, color=NEG, sw=3))

    # Electron markers
    out.append(f'<circle cx="120" cy="110" r="8" fill="{NEG}"/>')
    out.append(text(120, 85, "Вхідний електрон e⁻ (E_i)", size=13, color=NEG, bold=True, anchor="middle"))

    out.append(f'<circle cx="610" cy="201" r="8" fill="{NEG}"/>')
    out.append(text(610, 230, "Загальмований e⁻ (E_f)", size=13, color=NEG, bold=True, anchor="middle"))

    # Deceleration point
    vx, vy = 375, 180
    out.append(f'<circle cx="{vx}" cy="{vy}" r="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    out.append(text(vx, vy - 25, "Прискорення a", size=12, color="#b45309", bold=True, anchor="middle"))

    # Emitted photon
    out.append(line(vx + 10, vy - 10, 600, 50, color="#7c3aed", sw=2.5, dash="6,3"))
    out.append(arrow(vx + 100, vy - 70, 600, 50, color="#7c3aed", sw=2.5))
    out.append(text(500, 35, "Випромінений фотон hν = E_i − E_f", size=13, color="#7c3aed", bold=True, anchor="middle"))

    # Impact parameter b
    out.append(line(80, ny, 320, ny, color=MUTED, sw=1.2, dash="3,3"))
    out.append(line(240, 110, 240, ny, color=INK, sw=1.2))
    out.append(text(225, (110 + ny) / 2, "b", size=13, color=INK, bold=True, anchor="end"))
    out.append(text(160, ny + 35, "Прицільний параметр b", size=12, color=MUTED, italic=True, anchor="middle"))

    out.append('</svg>')
    return '\n'.join(out)

def generate_spectrum():
    width, height = 720, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    ox, oy = 90, 340
    w_ax, h_ax = 580, 270

    # Axes
    out.append(line(ox, oy, ox + w_ax, oy, color=INK, sw=2))
    out.append(arrow(ox + w_ax - 20, oy, ox + w_ax, oy, color=INK, sw=2))
    out.append(text(ox + w_ax, oy + 30, "Частота ν", size=13, color=INK, bold=True, anchor="end"))

    out.append(line(ox, oy, ox, oy - h_ax, color=INK, sw=2))
    out.append(arrow(ox, oy - h_ax + 20, ox, oy - h_ax, color=INK, sw=2))
    out.append(text(ox, oy - h_ax - 15, "Спектральна інтенсивність I(ν)", size=13, color=INK, bold=True, anchor="start"))

    # Three voltage curves
    curves = [
        (580, 100, POS, "U₃ = 50 кВ"),
        (470, 160, "#d97706", "U₂ = 40 кВ"),
        (360, 220, NEG, "U₁ = 30 кВ"),
    ]

    for x_max, y_top, col, lbl in curves:
        path_d = f"M {ox+30} {oy-10} Q {ox+110} {y_top-15} {ox+190} {y_top} L {x_max} {oy}"
        out.append(f'<path d="{path_d}" fill="none" stroke="{col}" stroke-width="2.8"/>')
        out.append(line(ox, oy - (340 - y_top) * 1.25, ox + 190, y_top, color=col, sw=1.5, dash="4,4"))
        out.append(line(x_max, oy, x_max, oy + 8, color=col, sw=2))
        out.append(text(x_max, oy + 24, f"ν_max ({lbl.split(' = ')[1]})", size=11, color=col, bold=True, anchor="middle"))

    # Duane-Hunt box
    out.append(rect(480, 50, 200, 80, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, rx=6))
    out.append(text(580, 72, "Закон Дуана — Ганта", size=13, color="#7c3aed", bold=True, anchor="middle"))
    out.append(text(580, 93, "h · ν_max = e · U", size=14, color="#7c3aed", bold=True, anchor="middle"))
    out.append(text(580, 114, "λ_min = h c / (e U)", size=12, color="#7c3aed", anchor="middle"))

    # Filtration note
    out.append(arrow(ox + 100, oy - 140, ox + 50, oy - 45, color=MUTED, sw=1.5))
    out.append(text(ox + 110, oy - 150, "Поглинання низьких частот", size=11, color=MUTED, italic=True, anchor="start"))

    out.append('</svg>')
    return '\n'.join(out)

def generate_cross_section():
    width, height = 720, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    ox, oy = 90, 330
    w_ax, h_ax = 580, 260

    # Axes
    out.append(line(ox, oy, ox + w_ax, oy, color=INK, sw=2))
    out.append(arrow(ox + w_ax - 20, oy, ox + w_ax, oy, color=INK, sw=2))
    out.append(text(ox + w_ax, oy + 30, "Відносна енергія фотона x = hν / E_k", size=13, color=INK, bold=True, anchor="end"))

    out.append(line(ox, oy, ox, oy - h_ax, color=INK, sw=2))
    out.append(arrow(ox, oy - h_ax + 20, ox, oy - h_ax, color=INK, sw=2))
    out.append(text(ox, oy - h_ax - 15, "Диференціальний переріз dσ/dω", size=13, color=INK, bold=True, anchor="start"))

    # Cutoff x = 1
    x_cut = ox + 460
    out.append(line(x_cut, oy - h_ax + 20, x_cut, oy, color=MUTED, sw=1.5, dash="4,4"))
    out.append(text(x_cut, oy + 24, "x = 1 (hν = E_k)", size=12, color=MUTED, bold=True, anchor="middle"))

    # Classical Kramers
    out.append(line(ox + 50, oy - 150, x_cut, oy - 150, color=NEG, sw=2.5, dash="6,3"))
    out.append(text(ox + 190, oy - 165, "Крамерс: ω·dσ/dω = const", size=12, color=NEG, bold=True, anchor="start"))

    # Quantum Bethe-Heitler
    bh_path = f"M {ox+30} {oy-230} Q {ox+70} {oy-170} {ox+190} {oy-155} T {ox+370} {oy-130} L {x_cut} {oy-35}"
    out.append(f'<path d="{bh_path}" fill="none" stroke="{POS}" stroke-width="3"/>')
    out.append(text(ox + 250, oy - 60, "Квантова теорія Бете — Гайтлера", size=13, color=POS, bold=True, anchor="start"))

    # Infrared divergence annotation
    out.append(arrow(ox + 150, oy - 235, ox + 45, oy - 220, color="#7c3aed", sw=1.5))
    out.append(text(ox + 160, oy - 238, "Інфрачервона дивергенція (ω → 0)", size=12, color="#7c3aed", bold=True, anchor="start"))

    # Beyond cutoff
    out.append(line(x_cut, oy, ox + w_ax - 20, oy, color=POS, sw=3))
    out.append(text(x_cut + 40, oy - 20, "dσ/dω = 0 при hν > E_k", size=12, color=POS, italic=True, anchor="start"))

    out.append('</svg>')
    return '\n'.join(out)

def generate_target_losses():
    width, height = 720, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    tx, ty, tw, th = 280, 70, 380, 240
    out.append(rect(tx, ty, tw, th, fill="#f3f4f6", stroke=INK, sw=2, rx=8))
    out.append(text(tx + tw/2, ty + 30, "Вольфрамовий анод (Z = 74)", size=15, color=INK, bold=True, anchor="middle"))

    # Electron beam
    out.append(line(30, ty + th/2, tx - 10, ty + th/2, color=NEG, sw=4))
    out.append(arrow(tx - 90, ty + th/2, tx - 10, ty + th/2, color=NEG, sw=4))
    out.append(text(130, ty + th/2 - 16, "Пучок електронів (P_el = U·I)", size=14, color=NEG, bold=True, anchor="middle"))

    # Thermal losses
    out.append(f'<rect x="{tx+30}" y="{ty+65}" width="{tw-60}" height="60" rx="6" fill="#fee2e2" stroke="{POS}" stroke-width="1.8"/>')
    out.append(text(tx + tw/2, ty + 90, "Теплові втрати в ґратці (~99.3%)", size=13, color=POS, bold=True, anchor="middle"))
    out.append(text(tx + tw/2, ty + 110, "Збудження фононів та іонізація", size=11, color=MUTED, italic=True, anchor="middle"))

    # Bremsstrahlung output
    out.append(f'<rect x="{tx+30}" y="{ty+140}" width="{tw-60}" height="60" rx="6" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.8"/>')
    out.append(text(tx + tw/2, ty + 165, "Гальмівне випромінювання (< 1%)", size=13, color="#7c3aed", bold=True, anchor="middle"))
    out.append(text(tx + tw/2, ty + 185, "ККД η ≈ k · Z · U (k ≈ 10⁻⁹ В⁻¹)", size=11, color="#7c3aed", italic=True, anchor="middle"))

    out.append(text(tx + tw/2, ty + th - 15, "Потрібне примусове водяне або олійне охолодження", size=11, color=INK, italic=True, anchor="middle"))

    out.append('</svg>')
    return '\n'.join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    with open(os.path.join(img_dir, 'fig1-bremsstrahlung-mechanism.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_mechanism())

    with open(os.path.join(img_dir, 'fig2-xray-spectrum-duane-hunt.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_spectrum())

    with open(os.path.join(img_dir, 'fig3-bethe-heitler-cross-section.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_cross_section())

    with open(os.path.join(img_dir, 'fig4-xray-target-losses.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_target_losses())

    print("All figures created successfully.")

if __name__ == '__main__':
    main()
