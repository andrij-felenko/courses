# -*- coding: utf-8 -*-
import os
import sys

# Add scripts directory to path (4 levels up from book/physics/electromagnetism/surface-conductivity)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import (
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT,
    text, mtext, rect, line, arrow, circle, textbox, esc
)

def ensure_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    return img_dir

def make_svg_document(width, height, content):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        '  <defs>\n'
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{LINE}"/>\n'
        '    </marker>\n'
        '    <marker id="arrow-pos" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{POS}"/>\n'
        '    </marker>\n'
        '    <marker id="arrow-field" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{FIELD}"/>\n'
        '    </marker>\n'
        '  </defs>\n'
        f'  <rect width="100%" height="100%" fill="{BG}"/>\n'
        f'{content}\n'
        '</svg>\n'
    )

def fig1_surface_vs_volume():
    """Diagram 1: Surface current vs Volume current in a dielectric sample."""
    w, h = 760, 420
    out = []

    # Dielectric body
    out.append(rect(140, 120, 480, 200, fill="#eef2f7", stroke="#4a5568", sw=2, rx=4))
    out.append(text(380, 220, "Об'єм діелектрика (питомий опір ρ_v > 10¹⁴ Ом·м)", size=14, color="#2d3748", bold=True))

    # Surface film (top and bottom adsorbed water/impurity layers)
    out.append(rect(140, 108, 480, 12, fill="#bae6fd", stroke="#0284c7", sw=1.2, rx=2))
    out.append(rect(140, 320, 480, 12, fill="#bae6fd", stroke="#0284c7", sw=1.2, rx=2))

    # Electrodes
    out.append(rect(80, 100, 60, 240, fill="#cbd5e1", stroke="#334155", sw=2, rx=3))
    out.append(text(110, 225, "Електрод +V", size=13, color=POS, bold=True, anchor="middle"))
    
    out.append(rect(620, 100, 60, 240, fill="#cbd5e1", stroke="#334155", sw=2, rx=3))
    out.append(text(650, 225, "Електрод 0V", size=13, color=NEG, bold=True, anchor="middle"))

    # Volume current arrows (thin, sparse)
    for y_pos in [160, 270]:
        out.append(f'<line x1="145" y1="{y_pos}" x2="615" y2="{y_pos}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arrow)"/>')
    out.append(text(380, 175, "Об'ємний струм I_v (надмалий, ~10⁻¹³ А)", size=12, color=MUTED, italic=True))

    # Surface current arrows (thick, strong)
    out.append(f'<line x1="145" y1="114" x2="615" y2="114" stroke="{POS}" stroke-width="3" marker-end="url(#arrow-pos)"/>')
    out.append(f'<line x1="145" y1="326" x2="615" y2="326" stroke="{POS}" stroke-width="3" marker-end="url(#arrow-pos)"/>')

    # Labels for surface film
    box1, _, _ = textbox(380, 75, "Плівка адсорбованої вологи та забруднень\nПоверхневий струм I_s (~10⁻⁸ А)", size=13, pad=8, fill="#f0f9ff", stroke="#0284c7", color="#0369a1", bold=True)
    out.append(box1)

    # Current summation equation box
    box2, _, _ = textbox(380, 375, "Повний струм витоку: I_total = I_v + I_s  (де I_s >> I_v за вологих умов)", size=13, pad=8, fill="#fffbe6", stroke="#d97706", color="#92400e", bold=True)
    out.append(box2)

    return make_svg_document(w, h, "\n".join(out))


def fig2_guard_ring_system():
    """Diagram 2: Three-electrode Guard Ring System."""
    w, h = 780, 460
    out = []

    # Dielectric sample in center
    out.append(rect(140, 180, 500, 120, fill="#f1f5f9", stroke="#475569", sw=2, rx=4))

    # Bottom main electrode
    out.append(rect(140, 300, 500, 30, fill="#94a3b8", stroke="#334155", sw=2, rx=2))
    out.append(text(390, 320, "Нижній суцільний електрод (+V_test)", size=13, color=INK, bold=True))

    # Top Central measuring electrode
    out.append(rect(270, 150, 240, 30, fill="#cbd5e1", stroke="#1e293b", sw=2, rx=2))
    out.append(text(390, 170, "Центральний електрод (1)", size=13, color=POS, bold=True))

    # Top Guard Ring electrode (Left part & Right part)
    out.append(rect(140, 150, 100, 30, fill="#e2e8f0", stroke="#334155", sw=2, rx=2))
    out.append(text(190, 170, "Захисне кільце (2)", size=11, color="#0f172a", bold=True))

    out.append(rect(540, 150, 100, 30, fill="#e2e8f0", stroke="#334155", sw=2, rx=2))
    out.append(text(590, 170, "Захисне кільце (2)", size=11, color="#0f172a", bold=True))

    # Gaps highlight
    out.append(rect(240, 150, 30, 30, fill="#fee2e2", stroke="#ef4444", sw=1, rx=0))
    out.append(rect(510, 150, 30, 30, fill="#fee2e2", stroke="#ef4444", sw=1, rx=0))
    out.append(text(255, 140, "Зазор g", size=11, color=POS))
    out.append(text(525, 140, "Зазор g", size=11, color=POS))

    # Potential matching note & OP-AMP schematic representation
    box_opamp, _, _ = textbox(390, 80, "Принцип еквіпотенціальності: V_1 = V_2 = 0 В\nНапруженість у зазорі E_gap = (V_1 - V_2)/g = 0  =>  I_surface = 0", size=13, pad=10, fill="#ecfdf5", stroke="#10b981", color="#065f46", bold=True)
    out.append(box_opamp)

    # Label box in center of dielectric sample (y: 220 to 260)
    box_sample, w_box, h_box = textbox(390, 240, "Діелектричний зразок\nЧистий об'ємний струм I_v", size=13, pad=8, fill="#ffffff", stroke="#475569", color="#1e293b", bold=True)

    # Current flow lines inside volume: split into top half (y=180 to y=215) and bottom half (y=265 to y=300) so no line crosses box
    top_y1, top_y2 = 300, 266
    bot_y1, bot_y2 = 214, 180
    for x_c in [290, 340, 390, 440, 490]:
        out.append(f'<line x1="{x_c}" y1="{top_y1}" x2="{x_c}" y2="{top_y2}" stroke="{FIELD}" stroke-width="2"/>')
        out.append(f'<line x1="{x_c}" y1="{bot_y1}" x2="{x_c}" y2="{bot_y2}" stroke="{FIELD}" stroke-width="2" marker-end="url(#arrow-field)"/>')

    out.append(box_sample)

    # Surface currents trapped by guard ring on top
    out.append(f'<line x1="140" y1="175" x2="235" y2="175" stroke="{POS}" stroke-width="2.5" marker-end="url(#arrow-pos)"/>')
    out.append(f'<line x1="640" y1="175" x2="545" y2="175" stroke="{POS}" stroke-width="2.5" marker-end="url(#arrow-pos)"/>')

    # Wiring labels
    out.append(line(190, 150, 190, 115, color=LINE, sw=1.5))
    out.append(line(190, 115, 250, 115, color=LINE, sw=1.5))

    out.append(line(390, 150, 390, 115, color=LINE, sw=1.5))

    box_meter, _, _ = textbox(390, 400, "До електрометра / пікоамперметра (вимірює тільки I_v)", size=13, pad=8, fill="#f8fafc", stroke="#64748b", color="#1e293b", bold=True)
    out.append(box_meter)

    return make_svg_document(w, h, "\n".join(out))


def fig3_creepage_vs_clearance():
    """Diagram 3: Creepage distance vs Clearance distance on an insulator shape."""
    w, h = 760, 400
    out = []

    # High voltage conductors at two sides
    out.append(rect(60, 150, 80, 100, fill="#fca5a5", stroke="#dc2626", sw=2, rx=4))
    out.append(text(100, 205, "HV 1\n(+10 kV)", size=13, color="#991b1b", bold=True))

    out.append(rect(620, 150, 80, 100, fill="#93c5fd", stroke="#2563eb", sw=2, rx=4))
    out.append(text(660, 205, "HV 2\n(0 V)", size=13, color="#1e40af", bold=True))

    # Ribbed Insulator profile between conductors
    insulator_path = (
        "M 140 180 "
        "L 220 180 "
        "L 220 120 L 260 120 L 260 180 "
        "L 340 180 "
        "L 340 120 L 380 120 L 380 180 "
        "L 460 180 "
        "L 460 120 L 500 120 L 500 180 "
        "L 620 180 "
        "L 620 220 "
        "L 500 220 L 500 280 L 460 280 L 460 220 "
        "L 380 220 L 380 280 L 340 280 L 340 220 "
        "L 260 220 L 260 280 L 220 280 L 220 220 "
        "L 140 220 Z"
    )
    out.append(f'<path d="{insulator_path}" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    out.append(text(380, 205, "Ребристий діелектричний ізолятор", size=14, color="#334155", bold=True))

    # Clearance (Straight line through air)
    out.append(f'<line x1="140" y1="90" x2="620" y2="90" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-pos)"/>')
    box_clr, _, _ = textbox(380, 60, "Повітряний зазор (Clearance) — найкоротший шлях по повітрю (480 мм)", size=12, pad=6, fill="#fef2f2", stroke="#f87171", color="#991b1b", bold=True)
    out.append(box_clr)

    # Creepage (Path along the surface contours)
    creepage_line = (
        "M 140 180 "
        "H 220 V 120 H 260 V 180 "
        "H 340 V 120 H 380 V 180 "
        "H 460 V 120 H 500 V 180 "
        "H 620"
    )
    out.append(f'<path d="{creepage_line}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    box_crp, _, _ = textbox(380, 335, "Шлях витоку (Creepage distance) — огинає ребра ізолятора (840 мм)\nЗбільшує опір поверхневого перекриття та уповільнює трекінг", size=13, pad=8, fill="#ecfdf5", stroke="#34d399", color="#065f46", bold=True)
    out.append(box_crp)

    return make_svg_document(w, h, "\n".join(out))


def fig4_grotthuss_surface_hopping():
    """Diagram 4: Microscopic Grotthuss proton hopping mechanism on wet surface."""
    w, h = 760, 420
    out = []

    # Solid dielectric substrate at bottom
    out.append(rect(60, 280, 640, 90, fill="#e2e8f0", stroke="#64748b", sw=2, rx=4))
    out.append(text(380, 325, "Твердий діелектрик (наприклад, SiO₂ або кераміка) з полярними Si-OH групами", size=13, color="#1e293b", bold=True))

    mol_centers = [140, 260, 380, 500, 620]
    
    # Electric field arrow
    out.append(f'<line x1="80" y1="50" x2="680" y2="50" stroke="{FIELD}" stroke-width="2.5" marker-end="url(#arrow-field)"/>')
    out.append(text(380, 30, "Зовнішнє електричне поле E_s", size=14, color=FIELD, bold=True))

    # Draw water molecules H2O / H3O+
    for i, cx in enumerate(mol_centers):
        if i == 0:
            # H3O+ ion
            out.append(circle(cx, 180, 32, fill="#fca5a5", stroke="#ef4444", sw=2))
            out.append(text(cx, 185, "H₃O⁺", size=15, color="#991b1b", bold=True))
            out.append(text(cx, 130, "Гідроксоній", size=12, color="#991b1b"))
        else:
            # H2O molecule
            out.append(circle(cx, 180, 28, fill="#bae6fd", stroke="#0284c7", sw=2))
            out.append(text(cx, 185, "H₂O", size=14, color="#0369a1", bold=True))

    # Hydrogen bond dotted lines & Proton hopping arrows
    for i in range(len(mol_centers) - 1):
        x1 = mol_centers[i] + 30
        x2 = mol_centers[i+1] - 28
        out.append(f'<line x1="{x1}" y1="180" x2="{x2}" y2="180" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4,3"/>')
        # Proton transfer arc arrow above
        out.append(f'<path d="M {x1+5} 165 Q {(x1+x2)/2} 145 {x2-5} 165" fill="none" stroke="{POS}" stroke-width="2" marker-end="url(#arrow-pos)"/>')
        out.append(text((x1+x2)/2, 140, "H⁺", size=11, color=POS, bold=True))

    # Immediacies: impurity ions Na+ / Cl-
    out.append(circle(300, 240, 18, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    out.append(text(300, 244, "Na⁺", size=12, color="#854d0e", bold=True))
    out.append(f'<line x1="320" y1="240" x2="360" y2="240" stroke="#854d0e" stroke-width="1.8" marker-end="url(#arrow)"/>')

    out.append(circle(460, 240, 18, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    out.append(text(460, 244, "Cl⁻", size=12, color="#9a3412", bold=True))
    out.append(f'<line x1="440" y1="240" x2="400" y2="240" stroke="#9a3412" stroke-width="1.8" marker-end="url(#arrow)"/>')

    box_desc, _, _ = textbox(380, 385, "Естафетне перенесення протона H⁺ (механізм Ґротгусса) у плівці адсорбованої води\nшвидше за класичну іонну дифузію у 5–10 разів", size=12, pad=6, fill="#fffbe6", stroke="#f59e0b", color="#92400e", bold=True)
    out.append(box_desc)

    return make_svg_document(w, h, "\n".join(out))


def main():
    img_dir = ensure_img_dir()
    
    figures = [
        ("surface-vs-volume-current.svg", fig1_surface_vs_volume()),
        ("guard-ring-system.svg", fig2_guard_ring_system()),
        ("creepage-vs-clearance.svg", fig3_creepage_vs_clearance()),
        ("grotthuss-surface-hopping.svg", fig4_grotthuss_surface_hopping()),
    ]
    
    for filename, content in figures:
        filepath = os.path.join(img_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()
