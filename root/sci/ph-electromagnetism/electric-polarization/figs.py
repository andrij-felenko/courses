# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle, plus, minus,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_bound_charges_dipole():
    w, h = 760, 400
    frags = []

    # Main container
    frags.append(rect(10, 10, 740, 380, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    # Title
    frags.append(text(380, 35, "Зв'язані заряди та вектор поляризації P у діелектрику", size=15, color=INK, bold=True))

    # Left plate (+Q_free)
    frags.append(rect(40, 60, 30, 280, fill="#fadbd8", stroke=POS, sw=2, rx=4))
    # Right plate (-Q_free)
    frags.append(rect(690, 60, 30, 280, fill="#d6eaf8", stroke=NEG, sw=2, rx=4))

    # Free charge indicators on plates
    for y in range(85, 325, 45):
        frags.append(plus(55, y, r=7))
        frags.append(minus(705, y, r=7))

    # Dielectric slab in middle
    frags.append(rect(160, 60, 440, 280, fill="#f4f6f7", stroke="#bdc3c7", sw=2, rx=6))
    frags.append(text(380, 85, "Поляризоване середовище (вектор P)", size=13, color=INK, bold=True))

    # Dipoles inside dielectric
    dipole_coords = [
        (220, 130), (310, 130), (400, 130), (490, 130),
        (220, 190), (310, 190), (400, 190), (490, 190),
        (220, 250), (310, 250), (400, 250), (490, 250),
    ]

    for cx, cy in dipole_coords:
        # Ellipse body of dipole
        frags.append(f'<ellipse cx="{cx}" cy="{cy}" rx="32" ry="16" fill="#ffffff" stroke="#95a5a6" stroke-width="1.5"/>')
        # - charge inside dipole (left side)
        frags.append(minus(cx - 16, cy, r=6))
        # + charge inside dipole (right side)
        frags.append(plus(cx + 16, cy, r=6))
        # Dipole moment arrow inside
        frags.append(arrow(cx - 10, cy, cx + 10, cy, color="#8e44ad", sw=1.5))

    # Surface bound charge -σ_bound on left face
    for y in range(110, 310, 40):
        frags.append(minus(175, y, r=7))

    # Surface bound charge +σ_bound on right face
    for y in range(110, 310, 40):
        frags.append(plus(585, y, r=7))

    # Polarization vector P arrow across dielectric
    frags.append(arrow(190, 310, 570, 310, color="#8e44ad", sw=3))
    frags.append(text(380, 295, "Вектор поляризації P (напрямлений від - до +)", size=12, color="#8e44ad", bold=True))

    # Electric field E_ext arrow top
    frags.append(arrow(75, 50, 685, 50, color=POS, sw=2))
    frags.append(text(115, 45, "E_ext", size=12, color=POS, bold=True))

    # Labels at bottom
    frags.append(fitbox(100, 360, 140, 26, "Поверхня: σ_bound = P·n", size=11, fill="#fadbd8", stroke=POS))
    frags.append(fitbox(380, 360, 180, 26, "Об'єм: ρ_bound = - ∇·P", size=11, fill="#e8daef", stroke="#8e44ad"))
    frags.append(fitbox(640, 360, 140, 26, "Поверхня: σ_bound = P·n", size=11, fill="#d6eaf8", stroke=NEG))

    return render(os.path.join(IMG_DIR, "bound-charges-dipole.svg"), w, h, *frags)


def fig_polarization_mechanisms():
    w, h = 760, 440
    frags = []

    frags.append(rect(10, 10, 740, 420, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    frags.append(text(380, 32, "Чотири мікроскопічні механізми поляризації діелектриків", size=15, color=INK, bold=True))

    # 4 Panels grid
    # Panel 1: Electronic (top left)
    frags.append(rect(25, 50, 345, 170, fill="#f9f9fb", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(197, 72, "1. Електронна поляризація (α_e)", size=13, color="#2980b9", bold=True))

    # E=0 atom vs E>0 atom
    # E=0 nucleus + symmetric cloud
    frags.append(circle(100, 130, 28, fill="#ebf5fb", stroke="#5dade2", sw=1.5))
    frags.append(circle(100, 130, 6, fill=POS, stroke=POS))
    frags.append(text(100, 172, "E = 0", size=11, color=MUTED))

    # Arrow E
    frags.append(arrow(145, 130, 185, 130, color=POS, sw=1.8))
    frags.append(text(165, 118, "E", size=11, color=POS, bold=True))

    # E>0 deformed cloud
    frags.append(f'<ellipse cx="260" cy="130" rx="36" ry="24" fill="#ebf5fb" stroke="#5dade2" stroke-width="1.5"/>')
    frags.append(circle(270, 130, 6, fill=POS, stroke=POS))
    frags.append(minus(240, 130, r=5))
    frags.append(text(260, 172, "E > 0 (зсув хмари)", size=11, color=INK))
    frags.append(text(197, 205, "Швидка (~10⁻¹⁵ с), UV-резонанс, без Т-залежності", size=10, color=MUTED, italic=True))

    # Panel 2: Ionic (top right)
    frags.append(rect(390, 50, 345, 170, fill="#f9f9fb", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(562, 72, "2. Іонна поляризація (α_i)", size=13, color="#27ae60", bold=True))

    # Ionic lattice E=0 vs E>0
    # E=0: + and - at equilibrium
    frags.append(circle(440, 130, 14, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(plus(440, 130, r=6))
    frags.append(line(454, 130, 486, 130, color="#bdc3c7", sw=2))
    frags.append(circle(500, 130, 14, fill="#d6eaf8", stroke=NEG, sw=1.5))
    frags.append(minus(500, 130, r=6))
    frags.append(text(470, 172, "E = 0", size=11, color=MUTED))

    # Arrow E
    frags.append(arrow(530, 130, 560, 130, color=POS, sw=1.8))
    frags.append(text(545, 118, "E", size=11, color=POS, bold=True))

    # E>0: ions stretched
    frags.append(circle(600, 130, 14, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(plus(600, 130, r=6))
    frags.append(line(614, 130, 666, 130, color="#bdc3c7", sw=2, dash="3,2"))
    frags.append(circle(680, 130, 14, fill="#d6eaf8", stroke=NEG, sw=1.5))
    frags.append(minus(680, 130, r=6))
    frags.append(text(640, 172, "E > 0 (деформація ґратки)", size=11, color=INK))
    frags.append(text(562, 205, "Швидка (~10⁻¹³ с), ИК-резонанс, слабка Т-залежність", size=10, color=MUTED, italic=True))

    # Panel 3: Orientational (bottom left)
    frags.append(rect(25, 235, 345, 170, fill="#f9f9fb", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(197, 257, "3. Орієнтаційна поляризація (α_orient)", size=13, color="#8e44ad", bold=True))

    # Random dipoles E=0 vs aligned dipoles E>0
    # E=0 random
    frags.append(circle(75, 315, 8, fill="#ffffff", stroke="#8e44ad"))
    frags.append(arrow(75, 315, 65, 305, color="#8e44ad", sw=1.2))
    frags.append(circle(115, 345, 8, fill="#ffffff", stroke="#8e44ad"))
    frags.append(arrow(115, 345, 125, 355, color="#8e44ad", sw=1.2))
    frags.append(text(95, 372, "E = 0 (хаос)", size=11, color=MUTED))

    # Arrow E
    frags.append(arrow(145, 330, 185, 330, color=POS, sw=1.8))
    frags.append(text(165, 318, "E", size=11, color=POS, bold=True))

    # E>0 aligned
    frags.append(arrow(220, 320, 260, 320, color="#8e44ad", sw=2))
    frags.append(plus(260, 320, r=6))
    frags.append(minus(220, 320, r=6))

    frags.append(arrow(260, 345, 300, 345, color="#8e44ad", sw=2))
    frags.append(plus(300, 345, r=6))
    frags.append(minus(260, 345, r=6))

    frags.append(text(270, 372, "E > 0 (орієнтація за E)", size=11, color=INK))
    frags.append(text(197, 390, "Релаксаційна (Дебай), 10⁹–10¹¹ Гц, ~1/T", size=10, color=MUTED, italic=True))

    # Panel 4: Interfacial / Space charge (bottom right)
    frags.append(rect(390, 235, 345, 170, fill="#f9f9fb", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(562, 257, "4. Міжповерхнева (структурна) (α_s)", size=13, color="#d35400", bold=True))

    # Grain boundary with trapped ions
    frags.append(line(562, 280, 562, 360, color=INK, sw=2, dash="4,3"))
    frags.append(text(480, 295, "Зерно A", size=11, color=MUTED))
    frags.append(text(640, 295, "Зерно B", size=11, color=MUTED))

    # Trapped charges at interface
    for y in range(305, 355, 15):
        frags.append(plus(552, y, r=6))
        frags.append(minus(572, y, r=6))

    frags.append(arrow(460, 330, 520, 330, color=POS, sw=1.8))
    frags.append(text(490, 318, "E", size=11, color=POS, bold=True))

    frags.append(text(562, 372, "Локалізація іонів на межах", size=11, color=INK))
    frags.append(text(562, 390, "Повільна (10⁻³–10³ Гц), низькочастотні втрати", size=10, color=MUTED, italic=True))

    return render(os.path.join(IMG_DIR, "polarization-mechanisms.svg"), w, h, *frags)


def fig_dielectric_dispersion():
    w, h = 760, 420
    frags = []

    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    frags.append(text(380, 32, "Спектр частотної дисперсії діелектричної проникності ε*(ω)", size=15, color=INK, bold=True))

    # Axes
    ox, oy = 90, 330
    ax_w, ax_h = 620, 260
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))

    frags.append(text(ox + ax_w - 30, oy + 30, "Частота f (Гц), логарифмічна шкала", size=12, color=INK, bold=True))
    frags.append(text(ox + 50, oy - ax_h + 15, "Проникність ε' та втрати ε''", size=12, color=INK, bold=True))

    # Frequency tick marks (10^2, 10^6, 10^10, 10^13, 10^15)
    ticks = [
        (ox + 70, "10² Гц"),
        (ox + 200, "10⁶ Гц"),
        (ox + 350, "10¹⁰ Гц\n(мікрохвилі)"),
        (ox + 480, "10¹³ Гц\n(ІЧ)"),
        (ox + 580, "10¹⁵ Гц\n(УФ)"),
    ]
    for tx, tlabel in ticks:
        frags.append(line(tx, oy - 5, tx, oy + 5, color=INK, sw=1.5))
        frags.append(mtext(tx, oy + 22, tlabel, size=10, color=MUTED))

    # Real permittivity curve ε' (step-like decreases at each cutoff)
    path_eps_real = (
        f"M {ox} {oy - 230} "
        f"L {ox + 60} {oy - 230} "
        f"Q {ox + 90} {oy - 230}, {ox + 100} {oy - 180} "
        f"Q {ox + 110} {oy - 170}, {ox + 150} {oy - 170} "
        f"L {ox + 300} {oy - 170} "
        f"Q {ox + 350} {oy - 170}, {ox + 370} {oy - 100} "
        f"Q {ox + 390} {oy - 80}, {ox + 440} {oy - 80} "
        f"L {ox + 460} {oy - 80} "
        f"Q {ox + 480} {oy - 80}, {ox + 490} {oy - 40} "
        f"Q {ox + 500} {oy - 30}, {ox + 550} {oy - 30} "
        f"Q {ox + 580} {oy - 30}, {ox + 590} {oy - 15} "
        f"L {ox + 610} {oy - 15}"
    )
    frags.append(f'<path d="{path_eps_real}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    frags.append(text(ox + 220, oy - 185, "Дійсна частина ε' (накопичення енергії)", size=12, color=FIELD, bold=True))

    # Imaginary permittivity curve ε'' (peaks at drop regions)
    path_eps_imag = (
        f"M {ox} {oy - 10} "
        f"Q {ox + 90} {oy - 90}, {ox + 120} {oy - 10} "
        f"L {ox + 300} {oy - 10} "
        f"Q {ox + 360} {oy - 120}, {ox + 410} {oy - 10} "
        f"L {ox + 450} {oy - 10} "
        f"Q {ox + 485} {oy - 100}, {ox + 520} {oy - 10} "
        f"L {ox + 550} {oy - 10} "
        f"Q {ox + 585} {oy - 80}, {ox + 610} {oy - 10}"
    )
    frags.append(f'<path d="{path_eps_imag}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6,3"/>')
    frags.append(text(ox + 360, oy - 135, "Множник втрат ε'' (тепловиділення)", size=12, color=POS, bold=True))

    # Region labels
    frags.append(fitbox(ox + 75, oy - 270, 110, 24, "Структурна", size=10, fill="#fdfefe", stroke=MUTED))
    frags.append(fitbox(ox + 220, oy - 270, 110, 24, "Орієнтаційна", size=10, fill="#fdfefe", stroke=MUTED))
    frags.append(fitbox(ox + 460, oy - 270, 90, 24, "Іонна", size=10, fill="#fdfefe", stroke=MUTED))
    frags.append(fitbox(ox + 575, oy - 270, 90, 24, "Електронна", size=10, fill="#fdfefe", stroke=MUTED))

    return render(os.path.join(IMG_DIR, "dielectric-dispersion.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_bound_charges_dipole()
    fig_polarization_mechanisms()
    fig_dielectric_dispersion()
    print("All electric-polarization figures generated successfully.")
