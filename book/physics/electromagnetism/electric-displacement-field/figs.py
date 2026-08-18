# -*- coding: utf-8 -*-
import sys, os

# Four levels up to root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle, plus, minus,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_d_vs_e_dielectric():
    w, h = 760, 420
    frags = []

    # Outer container / background
    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    # Electrodes (left positive, right negative)
    # Left electrode (+Q_free)
    frags.append(rect(40, 60, 30, 300, fill="#fadbd8", stroke=POS, sw=2, rx=4))
    # Right electrode (-Q_free)
    frags.append(rect(690, 60, 30, 300, fill="#d6eaf8", stroke=NEG, sw=2, rx=4))

    # Dielectric slab in middle
    frags.append(rect(180, 80, 400, 260, fill="#f4f6f7", stroke="#a6acaf", sw=2, rx=6))
    frags.append(text(380, 105, "Діелектричне середовище (ε_r > 1)", size=14, color=INK, bold=True))

    # Free charges on electrodes
    for y in range(90, 340, 40):
        frags.append(plus(55, y, r=8))
        frags.append(minus(705, y, r=8))

    # Bound charges on dielectric surfaces (+Q_bound on right surface inside, -Q_bound on left surface inside)
    for y in range(120, 320, 35):
        frags.append(minus(195, y, r=7))
        frags.append(plus(565, y, r=7))

    # Vector E (total electric field - weakened inside dielectric)
    # External field lines (vacuum gap left)
    frags.append(arrow(75, 140, 175, 140, color=POS, sw=2.5))
    frags.append(text(125, 125, "E_ext", size=13, color=POS, bold=True))

    # Total E field inside dielectric (shorter arrow, weakened by polarization)
    frags.append(arrow(210, 170, 550, 170, color=POS, sw=2))
    frags.append(text(380, 155, "E = E_ext - E_ind", size=13, color=POS, bold=True))

    # Polarization vector P (from - bound charge to + bound charge inside dielectric)
    frags.append(arrow(210, 230, 550, 230, color="#8e44ad", sw=2.5))
    frags.append(text(380, 215, "P = (ε_r - 1)·ε₀·E", size=13, color="#8e44ad", bold=True))

    # Electric displacement vector D (continuous, depends ONLY on free charge on electrodes)
    frags.append(arrow(75, 290, 685, 290, color=FIELD, sw=3))
    frags.append(text(380, 275, "D = ε₀·E + P = ε₀·ε_r·E", size=14, color=FIELD, bold=True))

    # Labels for charge types
    frags.append(fitbox(35, 370, 120, 30, "Вільні заряди +Q_free", size=11, fill="#fdecea", stroke=POS))
    frags.append(fitbox(605, 370, 120, 30, "Вільні заряди -Q_free", size=11, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(200, 370, 160, 30, "Зв'язаний заряд -Q_bound", size=11, fill="#eaeded", stroke="#7f8c8d"))
    frags.append(fitbox(420, 370, 160, 30, "Зв'язаний заряд +Q_bound", size=11, fill="#eaeded", stroke="#7f8c8d"))

    return render(os.path.join(IMG_DIR, "d-vs-e-dielectric.svg"), w, h, *frags)


def fig_boundary_conditions_d_e():
    w, h = 760, 440
    frags = []

    # Main panel
    frags.append(rect(10, 10, 740, 420, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    # Interface line (horizontal) at y=220
    iy = 220
    frags.append(rect(20, 20, 720, 200, fill="#eaf2f8", stroke="none"))
    frags.append(rect(20, 220, 720, 200, fill="#fef9e7", stroke="none"))
    frags.append(line(20, iy, 740, iy, color=INK, sw=2.5))

    # Medium labels
    frags.append(text(80, 50, "Середовище 1 (ε_r1)", size=15, color="#1b4f72", bold=True))
    frags.append(text(80, 390, "Середовище 2 (ε_r2 > ε_r1)", size=15, color="#7d6608", bold=True))
    frags.append(text(580, iy - 10, "Межа поділу діелектриків", size=12, color=INK, italic=True))

    # Free surface charge density σ_free on interface
    frags.append(text(380, iy + 16, "Вільний поверхневий заряд σ_free", size=12, color=POS, bold=True))

    # Gaussian Pillbox for normal components D_n
    # Pillbox spanning across interface (x: 190 to 290, y: 160 to 280)
    frags.append(rect(190, 160, 100, 120, fill="none", stroke=FIELD, sw=2, rx=4))
    frags.append(line(190, 160, 290, 160, color=FIELD, sw=3))
    frags.append(line(190, 280, 290, 280, color=FIELD, sw=3))

    # D_1n arrow pointing up out of top face
    frags.append(arrow(240, 160, 240, 90, color=FIELD, sw=2.5))
    frags.append(text(240, 75, "D_1n", size=13, color=FIELD, bold=True))

    # D_2n arrow pointing up into bottom face
    frags.append(arrow(240, 280, 240, 225, color=FIELD, sw=2.5))
    frags.append(text(240, 305, "D_2n", size=13, color=FIELD, bold=True))

    # Pillbox result text box
    frags.append(textbox(240, 370, "D_1n - D_2n = σ_free\n(Нормальна компонента)", size=12, fill="#e8f8f5", stroke=FIELD)[0])

    # Stokes loop for tangential components E_t
    # Loop spanning across interface (x: 480 to 620, y: 170 to 270)
    frags.append(rect(480, 170, 140, 100, fill="none", stroke=POS, sw=2, rx=2))

    # Tangential E_1t arrow top side
    frags.append(arrow(490, 170, 610, 170, color=POS, sw=2.5))
    frags.append(text(550, 155, "E_1t", size=13, color=POS, bold=True))

    # Tangential E_2t arrow bottom side
    frags.append(arrow(490, 270, 610, 270, color=POS, sw=2.5))
    frags.append(text(550, 290, "E_2t", size=13, color=POS, bold=True))

    # Stokes result text box
    frags.append(textbox(550, 370, "E_1t = E_2t  ⇒  D_1t / ε_1 = D_2t / ε_2\n(Тангенціальна компонента)", size=12, fill="#fdecea", stroke=POS)[0])

    # Refraction law formula in middle top
    frags.append(textbox(380, 80, "Закон заломлення ліній поля D:\ntan(θ_1) / tan(θ_2) = ε_r1 / ε_r2", size=13, fill="#ffffff", stroke=INK)[0])

    return render(os.path.join(IMG_DIR, "boundary-conditions-d-e.svg"), w, h, *frags)


def fig_dielectric_breakdown_saturation():
    w, h = 760, 420
    frags = []

    # Main background box
    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    # Coordinate axes
    ox, oy = 110, 350
    ax_w, ax_h = 590, 300
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))

    frags.append(text(ox + ax_w - 40, oy + 30, "Напруженість поля E", size=13, color=INK, bold=True))
    frags.append(text(ox + 80, oy - ax_h + 15, "Електричний зсув D", size=13, color=INK, bold=True))

    # Linear dielectric curve D = ε·E (straight green line)
    frags.append(line(ox, oy, ox + 480, oy - 210, color=FIELD, sw=3))
    frags.append(text(ox + 430, oy - 225, "Лінійний діелектрик: D = ε_0·ε_r·E", size=11, color=FIELD, bold=True))

    # Saturation curve (blue curve bending horizontally)
    path_sat = f"M {ox} {oy} Q {ox + 250} {oy - 160}, {ox + 500} {oy - 185}"
    frags.append(f'<path d="{path_sat}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    frags.append(text(ox + 340, oy - 150, "Насичення поляризації D_sat", size=11, color=NEG, bold=True))

    # Dielectric breakdown vertical line (dashed red)
    bx = ox + 450
    frags.append(line(bx, oy, bx, oy - 270, color=POS, sw=2, dash="5,4"))
    frags.append(fitbox(bx - 70, oy - 285, 140, 28, "Електричний пробій E_br", size=11, fill="#fadbd8", stroke=POS))

    # Explanatory card - fitbox at x=140, y=70 (well inside x>110 and above curve)
    frags.append(fitbox(140, 60, 280, 80, "Залежність D(E) у середовищі:\n• У слабких полях D ∝ E (лінійний режим)\n• У сильних полях виникає насичення диполів\n• При E > E_br середовище втрачає ізоляційні властивості", size=11, fill="#f8f9f9", stroke="#bdc3c7"))

    return render(os.path.join(IMG_DIR, "dielectric-breakdown-saturation.svg"), w, h, *frags)


def fig_free_vs_bound_charges_gauss():
    w, h = 760, 400
    frags = []

    frags.append(rect(10, 10, 740, 380, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))

    # Left panel: Gauss law for E (includes both free and bound charges)
    frags.append(rect(30, 30, 335, 340, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(197, 60, "Теорема Гаусса для вектора E", size=14, color="#b9770e", bold=True))

    # Dielectric region on left panel
    frags.append(rect(80, 120, 235, 160, fill="#eaeded", stroke="#bdc3c7", sw=1.5, rx=4))
    frags.append(text(197, 140, "Діелектрик", size=12, color=INK, italic=True))

    # Free charge Q_free
    frags.append(plus(140, 200, r=12))
    frags.append(text(140, 225, "+Q_free", size=11, color=POS, bold=True))

    # Bound charges on surface intersected by Gaussian surface
    frags.append(minus(240, 180, r=8))
    frags.append(minus(240, 220, r=8))
    frags.append(text(240, 245, "-Q_bound", size=11, color=NEG, bold=True))

    # Gaussian surface (dashed circle)
    frags.append(f'<circle cx="197" cy="200" r="85" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,3"/>')
    frags.append(text(197, 100, "Замкнена поверхня S", size=11, color=POS, italic=True))

    # Formula E
    frags.append(textbox(197, 325, "∯_S E·dA = (Q_free + Q_bound) / ε_0\nПотрібно знати Q_bound наперед!", size=12, fill="#ffffff", stroke="#f39c12")[0])

    # Right panel: Gauss law for D (only free charges)
    frags.append(rect(395, 30, 335, 340, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(562, 60, "Теорема Гаусса для вектора D", size=14, color=FIELD, bold=True))

    # Dielectric region on right panel
    frags.append(rect(445, 120, 235, 160, fill="#eaeded", stroke="#bdc3c7", sw=1.5, rx=4))
    frags.append(text(562, 140, "Діелектрик", size=12, color=INK, italic=True))

    # Free charge Q_free
    frags.append(plus(505, 200, r=12))
    frags.append(text(505, 225, "+Q_free", size=11, color=POS, bold=True))

    # Bound charges
    frags.append(minus(605, 180, r=8))
    frags.append(minus(605, 220, r=8))

    # Gaussian surface
    frags.append(f'<circle cx="562" cy="200" r="85" fill="none" stroke="{FIELD}" stroke-width="2" stroke-dasharray="4,3"/>')
    frags.append(text(562, 100, "Замкнена поверхня S", size=11, color=FIELD, italic=True))

    # Formula D
    frags.append(textbox(562, 325, "∯_S D·dA = Q_free\nЗалежить ЛИШЕ від вільних зарядів!", size=12, fill="#ffffff", stroke=FIELD)[0])

    return render(os.path.join(IMG_DIR, "free-vs-bound-charges-gauss.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_d_vs_e_dielectric()
    fig_boundary_conditions_d_e()
    fig_dielectric_breakdown_saturation()
    fig_free_vs_bound_charges_gauss()
    print("All figures generated successfully.")
