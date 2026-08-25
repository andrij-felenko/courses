# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_biot_savart_element():
    width, height = 620, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Definitions for arrows
    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
      <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>
      </marker>
    </defs>''')

    # Curved wire segment
    wire_path = "M 80 280 C 140 240, 180 180, 240 100"
    out.append(f'<path d="{wire_path}" fill="none" stroke="{LINE}" stroke-width="4"/>')
    out.append(arrow(180, 175, 200, 150, color=POS, sw=2.5))
    out.append(text(155, 185, "I", size=16, color=POS, bold=True))

    # Differential element dl on wire
    x1, y1 = 160, 200
    x2, y2 = 200, 150
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{POS}" stroke-width="5" marker-end="url(#arrow-red)"/>')
    out.append(text(160, 155, "dl", size=15, color=POS, bold=True, italic=True))

    # Observation point P
    px, py = 450, 110
    out.append(circle(px, py, 5, fill=INK, stroke=INK, sw=1))
    out.append(text(px + 18, py - 5, "P", size=16, color=INK, bold=True))

    # Distance vector r from element dl to point P
    out.append(f'<line x1="{x2}" y1="{y2}" x2="{px}" y2="{py}" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-blue)"/>')
    out.append(text(330, 115, "r (відстань)", size=14, color=NEG, italic=True))

    # Angle theta arc
    out.append(text(240, 160, "θ", size=16, color=INK, bold=True))
    out.append(f'<path d="M 230 144 A 40 40 0 0 0 215 135" fill="none" stroke="{INK}" stroke-width="1.5"/>')

    # Resulting field dB at P (perpendicular to plane dl and r, pointing into page / perpendicular vector)
    out.append(arrow(px, py, px + 50, py + 120, color=FIELD, sw=3))
    out.append(text(px + 60, py + 130, "dB ⊥ (dl, r)", size=15, color=FIELD, bold=True))

    # Formula textbox
    tbox, tw, th = textbox(310, 310, "dB = (μ₀ / 4π) · (I · dl × r̂) / r²\n|dB| = (μ₀ · I · dl · sin θ) / (4π · r²)", size=14, pad=10, fill=FILL, stroke=FIELD, sw=1.5, color=INK)
    out.append(tbox)

    out.append('</svg>')
    return "\n".join(out)

def generate_wire_field_geometry():
    width, height = 620, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
      <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
      </marker>
    </defs>''')

    # Straight vertical wire
    wx = 180
    out.append(line(wx, 30, wx, 320, color=LINE, sw=4))
    out.append(arrow(wx, 280, wx, 50, color=POS, sw=2.5))
    out.append(text(wx - 25, 60, "I", size=16, color=POS, bold=True))

    # Observation point P
    px, py = 420, 180
    out.append(circle(px, py, 4, fill=INK, stroke=INK))
    out.append(text(px + 15, py + 5, "P", size=15, bold=True))

    # Perpendicular distance R
    out.append(line(wx, py, px, py, color=NEG, sw=2, dash="4,4"))
    out.append(text(295, py - 10, "R (відстань)", size=14, color=NEG, bold=True))
    out.append(circle(wx, py, 3, fill=NEG, stroke=NEG))

    # Element dz on wire
    ez = 100
    out.append(line(wx, ez - 15, wx, ez + 15, color=POS, sw=6))
    out.append(text(wx - 30, ez, "dz", size=14, color=POS, bold=True))

    # Hypotenuse r from dz to P
    out.append(line(wx, ez, px, py, color=MUTED, sw=1.5, dash="3,3"))
    out.append(text(310, ez + 25, "r = √(R² + z²)", size=13, color=MUTED, italic=True))

    # Magnetic field vector B (concentric circle representation / tangent vector)
    out.append(arrow(px, py, px, py + 70, color=FIELD, sw=2.5))
    out.append(text(px + 15, py + 75, "B (напрямок за правилом правої руки)", size=14, color=FIELD, bold=True))

    # Concentric magnetic field line ellipse
    out.append(f'<ellipse cx="{wx}" cy="{py}" rx="240" ry="45" fill="none" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="6,4"/>')

    # Formula textbox
    tbox, tw, th = textbox(310, 345, "Для нескінченного прямого провідника: B = (μ₀ · I) / (2π · R)", size=14, pad=8, fill=FILL, stroke=FIELD, sw=1.5, color=INK)
    out.append(tbox)

    out.append('</svg>')
    return "\n".join(out)

def generate_loop_axis_field():
    width, height = 660, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>
      </marker>
    </defs>''')

    # Symmetry Z axis
    out.append(line(40, 190, 600, 190, color=MUTED, sw=1.5, dash="5,4"))
    out.append(text(590, 210, "Вісь Z", size=13, color=MUTED, italic=True))

    # Loop centered at X=140
    lx = 140
    out.append(f'<ellipse cx="{lx}" cy="190" rx="35" ry="110" fill="none" stroke="{LINE}" stroke-width="3"/>')
    out.append(arrow(lx + 35, 190, lx + 35, 170, color=POS, sw=2))
    out.append(text(lx + 45, 160, "I", size=15, color=POS, bold=True))

    # Loop Radius R
    out.append(line(lx, 190, lx, 80, color=NEG, sw=2))
    out.append(text(lx - 20, 135, "R", size=15, color=NEG, bold=True))

    # Observation point P on axis at z
    pz = 410
    out.append(circle(pz, 190, 4, fill=INK, stroke=INK))
    out.append(text(pz, 215, "P (z)", size=15, bold=True))

    # Distance z label
    out.append(line(lx, 190, pz, 190, color=INK, sw=1))
    out.append(text((lx + pz) / 2, 175, "z", size=15, bold=True, italic=True))

    # Distance r from top of loop to point P
    out.append(line(lx, 80, pz, 190, color=NEG, sw=1.8, dash="4,3"))
    out.append(text(265, 115, "r = √(R² + z²)", size=13, color=NEG, italic=True))

    # dB vector and its components at P
    out.append(arrow(pz, 190, pz + 65, 150, color=FIELD, sw=2))
    out.append(text(pz + 75, 145, "dB", size=14, color=FIELD, bold=True, anchor="start"))

    # Axial component dB_z
    out.append(arrow(pz, 190, pz + 65, 190, color=POS, sw=2.5))
    out.append(text(pz + 45, 215, "dB_z", size=14, color=POS, bold=True))

    # Transverse component dB_perp (dashed line)
    out.append(line(pz + 65, 190, pz + 65, 150, color=MUTED, sw=1.5, dash="3,3"))
    out.append(text(pz + 72, 170, "dB_⊥ (сума = 0)", size=12, color=MUTED, italic=True, anchor="start"))

    # Resulting field B_z textbox
    tbox, tw, th = textbox(330, 335, "Поле на осі витка: B_z = (μ₀ · I · R²) / [2 · (R² + z²)^(3/2)]\nУ центрі витка (z = 0): B = (μ₀ · I) / (2 · R)", size=14, pad=10, fill=FILL, stroke=FIELD, sw=1.5, color=INK)
    out.append(tbox)

    out.append('</svg>')
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    figs = {
        "biot-savart-element.svg": generate_biot_savart_element(),
        "wire-field-geometry.svg": generate_wire_field_geometry(),
        "loop-axis-field.svg": generate_loop_axis_field()
    }

    for name, content in figs.items():
        path = os.path.join(img_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == "__main__":
    main()
