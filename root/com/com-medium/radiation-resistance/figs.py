# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path (4 levels up from book/communications/antennas/radiation-resistance)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_rad_resistance_concept():
    # Canvas size widened to 880 to accommodate right text labels
    w, h = 880, 320
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    # Defs for markers and filters
    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
      </marker>
      <marker id="arrow-field" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
      </marker>
    </defs>''' % (LINE, FIELD))

    # Left Section: Transmitter / Generator
    out.append(rect(30, 80, 160, 160, fill="#eef2ff", stroke=NEG, sw=2, rx=8))
    out.append(text(110, 115, "ВЧ Генератор", size=15, bold=True, color=NEG))
    out.append(text(110, 140, "P_вч (ВЧ потужність)", size=13, color=MUTED))
    out.append(text(110, 175, "~ V_g, Z_g", size=14, bold=True, color=INK))

    # Transmission line (Feeder)
    out.append(line(190, 120, 300, 120, color=LINE, sw=2))
    out.append(line(190, 200, 300, 200, color=LINE, sw=2))
    out.append(text(245, 110, "Фідер (Z₀ = 50 Ом)", size=12, color=MUTED, bold=True))

    # Center Section: Antenna Equivalent Circuit Box
    out.append(rect(300, 50, 240, 220, fill="#f9fafb", stroke=LINE, sw=2, rx=8))
    out.append(text(420, 75, "Еквівалентна схема антени Z_A", size=14, bold=True, color=INK))

    # Inside circuit elements
    # Reactive part X_A
    tx_box, _, _ = textbox(420, 115, "jX_A (Реактивність)", size=13, pad=8, fill="#ffffff", stroke=MUTED, sw=1.5)
    out.append(tx_box)

    # Ohmic loss R_loss
    rloss_box, _, _ = textbox(420, 165, "R_втрат (Теплові втрати)", size=13, pad=8, fill="#fee2e2", stroke=POS, sw=1.5)
    out.append(rloss_box)

    # Radiation resistance R_rad
    rrad_box, _, _ = textbox(420, 220, "R_рад (Опір випромінювання)", size=13, pad=8, fill="#dcfce7", stroke=FIELD, sw=2, bold=True)
    out.append(rrad_box)

    # Connections inside antenna box
    out.append(line(300, 120, 340, 120, color=LINE, sw=2))
    out.append(line(340, 120, 340, 115, color=LINE, sw=2))
    out.append(line(500, 115, 520, 115, color=LINE, sw=2))
    out.append(line(520, 115, 520, 165, color=LINE, sw=2))

    out.append(line(300, 200, 520, 200, color=LINE, sw=2))
    out.append(line(520, 200, 520, 220, color=LINE, sw=2))

    # Right Section: Energy Destinations
    # Arrow to Heat (from R_loss)
    out.append(line(540, 165, 590, 165, color=POS, sw=2, dash="4,4"))
    out.append(arrow(590, 165, 630, 165, color=POS, sw=2))
    out.append(text(640, 160, "Тепло P_втрат", size=13, bold=True, color=POS, anchor="start"))
    out.append(text(640, 178, "(Омічний нагрів)", size=11, color=MUTED, anchor="start"))

    # Arrow to EM Wave radiation (from R_rad)
    out.append(line(540, 220, 590, 220, color=FIELD, sw=2.5))
    out.append('<line x1="590" y1="220" x2="630" y2="220" stroke="%s" stroke-width="2.5" marker-end="url(#arrow-field)"/>' % FIELD)
    out.append(text(640, 215, "Електромагнітна хвиля P_рад", size=13, bold=True, color=FIELD, anchor="start"))
    out.append(text(640, 233, "(Випромінювання в простір)", size=11, color=MUTED, anchor="start"))

    out.append('</svg>')
    return "".join(out)


def generate_dipole_length_resistance():
    w, h = 760, 390
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    # Title & Axes Setup
    out.append(text(380, 25, "Залежність імпедансу симетричного диполя Z = R_рад + jX від довжини (l / λ)", size=15, bold=True, color=INK))

    # Graph origin and dimensions
    ox, oy = 90, 240
    gw, gh = 620, 210

    # Grid & Axes
    out.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5)) # zero reactance line
    out.append(line(ox, oy - gh/2, ox, oy + gh/2, color=LINE, sw=1.5)) # Y axis
    out.append(line(ox, oy + gh/2, ox + gw, oy + gh/2, color="#e5e7eb", sw=1)) # Bottom line

    # Y labels
    out.append(text(80, oy - 90, "+200 Ом", size=11, color=MUTED, anchor="end"))
    out.append(text(80, oy, "0 Ом", size=11, color=MUTED, anchor="end"))
    out.append(text(80, oy + 90, "-200 Ом", size=11, color=MUTED, anchor="end"))

    # X ticks and labels
    x_points = [
        (0.1, "0.1λ"), (0.25, "0.25λ"), (0.5, "0.5λ (λ/2)"), (0.75, "0.75λ"), (1.0, "1.0λ")
    ]
    for rel_x, label in x_points:
        px = ox + rel_x * gw
        out.append(line(px, oy - gh/2, px, oy + gh/2, color="#f3f4f6", sw=1, dash="2,2"))
        out.append(line(px, oy - 3, px, oy + 3, color=LINE, sw=1))
        out.append(text(px, oy + gh/2 + 20, label, size=12, color=INK))

    out.append(text(ox + gw/2, oy + gh/2 + 42, "Електрична довжина диполя l / λ", size=13, bold=True, color=INK))

    # Radiation Resistance Curve R_rad (Green / Solid)
    def map_pt(l_rel, val):
        px = ox + l_rel * gw
        py = oy - (val / 200.0) * 90.0
        py = max(oy - gh/2 - 10, min(oy + gh/2 + 10, py))
        return px, py

    # Curve for R_rad
    r_pts = [
        (0.05, 2), (0.1, 8), (0.2, 30), (0.3, 40), (0.4, 55),
        (0.5, 73.1), (0.6, 110), (0.7, 160), (0.75, 200)
    ]
    path_r = []
    for i, (l_rel, r_val) in enumerate(r_pts):
        px, py = map_pt(l_rel, r_val)
        cmd = "M" if i == 0 else "L"
        path_r.append("%s %.1f %.1f" % (cmd, px, py))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(path_r), FIELD))

    # Curve for X_A Reactance (Blue / Dashed)
    x_pts = [
        (0.1, -190), (0.2, -140), (0.3, -90), (0.4, -40), (0.48, 0),
        (0.5, 42.5), (0.6, 130), (0.7, 190)
    ]
    path_x = []
    for i, (l_rel, x_val) in enumerate(x_pts):
        px, py = map_pt(l_rel, x_val)
        cmd = "M" if i == 0 else "L"
        path_x.append("%s %.1f %.1f" % (cmd, px, py))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (" ".join(path_x), NEG))

    # Highlight point at λ/2 dipole: (0.5, 73.1)
    hx, hy = map_pt(0.5, 73.1)
    out.append(circle(hx, hy, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    tbox, _, _ = textbox(hx + 75, hy - 25, "R_рад = 73.1 Ом\n(Півхвильовий диполь)", size=11, pad=6, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True)
    out.append(tbox)

    # Highlight point at resonance (X = 0, l = 0.48λ)
    rx, ry = map_pt(0.48, 0)
    out.append(circle(rx, ry, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    rbox, _, _ = textbox(rx - 70, ry + 30, "Резонанс: X_A = 0 Ом\n(l ≈ 0.48λ, R ≈ 70 Ом)", size=11, pad=6, fill="#ffffff", stroke=NEG, sw=1.5)
    out.append(rbox)

    # Legend
    out.append(line(480, 50, 510, 50, color=FIELD, sw=3))
    out.append(text(520, 54, "Опір випромінювання R_рад", size=12, bold=True, color=FIELD, anchor="start"))

    out.append(line(480, 70, 510, 70, color=NEG, sw=2, dash="6,4"))
    out.append(text(520, 74, "Реактивний опір X_A", size=12, bold=True, color=NEG, anchor="start"))

    out.append('</svg>')
    return "".join(out)


def generate_wheeler_cap():
    w, h = 760, 310
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    out.append(text(380, 25, "Метод ковпака Вілера (Wheeler Cap) для розділення R_рад та R_втрат", size=15, bold=True, color=INK))

    # Left Panel: Free space measurement
    out.append(rect(40, 50, 320, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(200, 75, "1. Вимірювання у вільному просторі", size=13, bold=True, color=INK))

    # Antenna representation
    out.append(line(200, 110, 200, 190, color=LINE, sw=3)) # monopole
    out.append(line(140, 190, 260, 190, color=LINE, sw=2)) # ground plane
    out.append(circle(200, 190, 4, fill=NEG, stroke=LINE, sw=1))

    # Waves radiating into space
    out.append('<path d="M 220 130 A 30 30 0 0 1 220 170" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)
    out.append('<path d="M 235 120 A 50 50 0 0 1 235 180" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)
    out.append('<path d="M 180 130 A 30 30 0 0 0 180 170" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)

    # Result box left
    box1, _, _ = textbox(200, 230, "R_вільне = R_рад + R_втрат", size=13, pad=8, fill="#dcfce7", stroke=FIELD, sw=1.5, bold=True)
    out.append(box1)

    # Right Panel: Measurement inside conductor cap
    out.append(rect(400, 50, 320, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(560, 75, "2. Вимірювання у провідному ковпаку", size=13, bold=True, color=INK))

    # Metallic Wheeler Cap enclosure (dome radius 80)
    out.append('<path d="M 475 190 A 85 85 0 0 1 645 190 Z" fill="#e2e8f0" stroke="%s" stroke-width="2.5" stroke-dasharray="4,2"/>' % POS)

    # Label OUTSIDE dome above y=95
    out.append(text(560, 93, "Екранувальний ковпак (r = λ / 2π)", size=11, bold=True, color=POS))

    # Antenna inside cap
    out.append(line(560, 130, 560, 190, color=LINE, sw=3)) # monopole
    out.append(line(500, 190, 620, 190, color=LINE, sw=2)) # ground plane
    out.append(circle(560, 190, 4, fill=NEG, stroke=LINE, sw=1))

    # Text inside dome: centered at x=560, y=145 (antenna monopole is a thin vertical line 560,130->190)
    # To prevent line intersection warning, move text slightly to the right at x=595, y=145
    out.append(text(595, 145, "Випромінювання заблоковане", size=10, color=MUTED, anchor="start", italic=True))

    # Result box right
    box2, _, _ = textbox(560, 230, "R_ковпак = R_втрат", size=13, pad=8, fill="#fee2e2", stroke=POS, sw=1.5, bold=True)
    out.append(box2)

    # Bottom summary equation
    out.append(text(380, 290, "Опір випромінювання:  R_рад = R_вільне - R_ковпак", size=13, bold=True, color=INK))

    out.append('</svg>')
    return "".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    files = {
        'rad-resistance-concept.svg': generate_rad_resistance_concept(),
        'dipole-length-resistance.svg': generate_dipole_length_resistance(),
        'wheeler-cap.svg': generate_wheeler_cap()
    }

    for name, content in files.items():
        path = os.path.join(img_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == '__main__':
    main()
