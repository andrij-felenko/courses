# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/electromagnetism/ampere-circuital-law/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_ampere_contour():
    width, height = 640, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
      <marker id="arrow-pos" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
      </marker>
      <marker id="arrow-field" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
      </marker>
      <marker id="arrow-neg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>
      </marker>
    </defs>''')

    # Closed contour L (ellipse-like path)
    cx, cy = 260, 200
    rx, ry = 170, 110
    
    # Surface S shaded region
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#f0fdf4" stroke="{FIELD}" stroke-width="2" stroke-dasharray="6,4"/>')
    out.append(text(cx, cy + 85, "Поверхня S", size=13, color=FIELD, italic=True))

    # Contour L path with orientation arrows
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    out.append(text(cx - 70, cy - ry - 12, "Контур L", size=15, color=INK, bold=True))
    
    # Direction arrows on contour L
    out.append(arrow(cx - 30, cy - ry, cx + 10, cy - ry, color=INK, sw=2.5))
    out.append(arrow(cx + 30, cy + ry, cx - 10, cy + ry, color=INK, sw=2.5))

    # Wires passing through surface S
    # Wire 1: I1 upwards (inside)
    w1x, w1y = 200, 170
    out.append(line(w1x, w1y - 70, w1x, w1y + 70, color=POS, sw=3))
    out.append(arrow(w1x, w1y + 30, w1x, w1y - 65, color=POS, sw=3))
    out.append(text(w1x - 28, w1y - 20, "I₁ (+)", size=14, color=POS, bold=True))

    # Wire 2: I2 downwards (inside)
    w2x, w2y = 300, 210
    out.append(line(w2x, w2y - 70, w2x, w2y + 70, color=NEG, sw=3))
    out.append(arrow(w2x, w2y - 30, w2x, w2y + 65, color=NEG, sw=3))
    out.append(text(w2x + 35, w2y + 50, "I₂ (−)", size=14, color=NEG, bold=True))

    # Wire 3: I3 outside contour L
    w3x, w3y = 510, 190
    out.append(line(w3x, w3y - 70, w3x, w3y + 70, color=MUTED, sw=2, dash="4,3"))
    out.append(arrow(w3x, w3y + 30, w3x, w3y - 65, color=MUTED, sw=2))
    out.append(text(w3x + 35, w3y - 45, "I₃ (зовні)", size=13, color=MUTED))

    # Element dl on contour and field B vector
    dlx, dly = cx - rx, cy
    out.append(circle(dlx, dly, 4, fill=POS, stroke=POS, sw=1))
    out.append(arrow(dlx, dly, dlx, dly - 40, color=POS, sw=2.5))
    out.append(text(dlx - 22, dly - 20, "dl", size=14, color=POS, bold=True, italic=True))

    # Magnetic field B at dl
    out.append(arrow(dlx, dly, dlx - 35, dly + 35, color=FIELD, sw=2.5))
    out.append(text(dlx - 50, dly + 35, "B", size=14, color=FIELD, bold=True))

    # Formula box on the right
    box_code, bw, bh = textbox(490, 310, "∮_L B · dl = μ₀ · I_охоп\n\nI_охоп = I₁ − I₂", size=14, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(box_code)

    # Right hand rule box top right
    rule_box, rw, rh = textbox(510, 75, "Правило правого гвинта:\nнапрямок обходу L виганяє\nпозитивний напрямок I", size=12, pad=10, fill="#f8fafc", stroke=MUTED, sw=1)
    out.append(rule_box)

    out.append('</svg>')
    return "\n".join(out)


def generate_solenoid_contour():
    width, height = 640, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
      <marker id="arrow-field" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
      </marker>
    </defs>''')

    # Solenoid upper and lower turn cross-sections
    # Upper turns (current out of page, dots)
    y_top = 110
    y_bot = 250
    x_start = 80
    dx = 40
    num_turns = 10

    for i in range(num_turns):
        x = x_start + i * dx
        # Top wire cross section (dot = current out of page)
        out.append(circle(x, y_top, 9, fill="#fef2f2", stroke=POS, sw=1.8))
        out.append(circle(x, y_top, 2.5, fill=POS, stroke=POS, sw=1))
        # Bottom wire cross section (cross = current into page)
        out.append(circle(x, y_bot, 9, fill="#eff6ff", stroke=NEG, sw=1.8))
        # X mark
        out.append(f'<line x1="{x-4}" y1="{y_bot-4}" x2="{x+4}" y2="{y_bot+4}" stroke="{NEG}" stroke-width="1.8"/>')
        out.append(f'<line x1="{x+4}" y1="{y_bot-4}" x2="{x-4}" y2="{y_bot+4}" stroke="{NEG}" stroke-width="1.8"/>')

    out.append(text(40, y_top + 4, "⊙ I", size=13, color=POS, bold=True))
    out.append(text(40, y_bot + 4, "⊗ I", size=13, color=NEG, bold=True))

    # Internal uniform magnetic field lines B
    y_mid = (y_top + y_bot) / 2
    for dy_offset in [-30, 0, 30]:
        out.append(line(60, y_mid + dy_offset, 480, y_mid + dy_offset, color=FIELD, sw=2, dash="6,4"))
        out.append(arrow(240, y_mid + dy_offset, 270, y_mid + dy_offset, color=FIELD, sw=2))

    out.append(text(120, y_mid - 40, "B_всередині", size=14, color=FIELD, bold=True))
    out.append(text(120, 50, "B_зовні ≈ 0", size=13, color=MUTED, italic=True))

    # Rectangular Ampèrian loop L (sides 1, 2, 3, 4)
    lx1, lx2 = 180, 340
    ly1, ly2 = y_mid, y_top - 45 # ly1 inside solenoid, ly2 outside above top turns
    
    out.append(rect(lx1, ly2, lx2 - lx1, ly1 - ly2, fill="none", stroke=INK, sw=2.5, rx=0))
    
    # Arrows on rectangle side 1 (bottom inside), side 2 (right), side 3 (top outside), side 4 (left)
    out.append(arrow(lx1 + 10, ly1, lx2 - 10, ly1, color=INK, sw=2.5)) # Side 1 (parallel to B)
    out.append(arrow(lx2, ly1 - 5, lx2, ly2 + 5, color=INK, sw=2))      # Side 2 (perpendicular)
    out.append(arrow(lx2 - 10, ly2, lx1 + 10, ly2, color=INK, sw=2))      # Side 3 (outside)
    out.append(arrow(lx1, ly2 + 5, lx1, ly1 - 5, color=INK, sw=2))      # Side 4 (perpendicular)

    # Labels for rectangle sides
    out.append(text((lx1 + lx2)/2, ly1 + 20, "Сторона 1 (h)", size=13, color=INK, bold=True))
    out.append(text(lx2 + 45, (ly1 + ly2)/2 + 4, "Сторона 2 (⊥)", size=12, color=MUTED))
    out.append(text((lx1 + lx2)/2, ly2 - 12, "Сторона 3 (зовні)", size=12, color=MUTED))
    out.append(text(lx1 - 45, (ly1 + ly2)/2 + 4, "Сторона 4 (⊥)", size=12, color=MUTED))

    # Formula box on the right
    fbox, fw, fh = textbox(550, 180, "∮ B · dl = B · h\n\nI_охоп = N · I\n\nB · h = μ₀ · N · I\n\nB = μ₀ · n · I", size=13, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    out.append(fbox)

    out.append('</svg>')
    return "\n".join(out)


def generate_thick_wire_profile():
    width, height = 640, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
    </defs>''')

    # Left half: Conductor cross section with two contours r < R and r > R
    ccx, ccy = 150, 190
    R = 80

    # Thick conductor cross-section
    out.append(circle(ccx, ccy, R, fill="#f1f5f9", stroke=LINE, sw=2))
    out.append(text(ccx, ccy + 25, "Провідник (R)", size=13, color=MUTED))

    # Radius R line
    out.append(line(ccx, ccy, ccx + R, ccy, color=LINE, sw=1.5, dash="4,3"))
    out.append(text(ccx + 40, ccy - 8, "R", size=13, color=LINE, bold=True))

    # Inner contour r < R
    r_in = 45
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{r_in}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="5,4"/>')
    out.append(line(ccx, ccy, ccx, ccy - r_in, color=POS, sw=1.5))
    out.append(text(ccx + 22, ccy - 22, "r < R", size=12, color=POS, bold=True))

    # Outer contour r > R
    r_out = 115
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{r_out}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4"/>')
    out.append(line(ccx, ccy, ccx - r_out * 0.866, ccy - r_out * 0.5, color=NEG, sw=1.5))
    out.append(text(ccx - r_out * 0.866 - 25, ccy - r_out * 0.5, "r > R", size=12, color=NEG, bold=True))

    # Right half: Graph B(r) vs r
    gx0, gy0 = 340, 280
    gw, gh = 260, 220

    # Graph axes
    out.append(arrow(gx0, gy0, gx0 + gw + 20, gy0, color=INK, sw=2)) # r axis
    out.append(arrow(gx0, gy0, gx0, gy0 - gh - 15, color=INK, sw=2))  # B axis
    out.append(text(gx0 + gw + 20, gy0 + 20, "r", size=14, color=INK, bold=True, italic=True))
    out.append(text(gx0 - 25, gy0 - gh - 10, "B(r)", size=14, color=INK, bold=True, italic=True))

    # Marker R on r axis
    R_px = 100 # pixel offset for R
    x_R = gx0 + R_px
    out.append(line(x_R, gy0 - 5, x_R, gy0 + 5, color=INK, sw=1.5))
    out.append(line(x_R, gy0, x_R, gy0 - gh + 40, color=MUTED, sw=1, dash="3,3"))
    out.append(text(x_R, gy0 + 20, "R", size=14, color=INK, bold=True))

    # Peak value B_max = μ0 I / (2π R)
    y_Bmax = gy0 - (gh - 50)
    out.append(line(gx0 - 5, y_Bmax, gx0 + 5, y_Bmax, color=INK, sw=1.5))
    out.append(line(gx0, y_Bmax, x_R, y_Bmax, color=MUTED, sw=1, dash="3,3"))
    out.append(text(gx0 - 55, y_Bmax + 4, "B_макс", size=12, color=FIELD, bold=True))

    # Linear part for r < R: B ~ r
    out.append(line(gx0, gy0, x_R, y_Bmax, color=POS, sw=3))
    out.append(text(gx0 + 30, gy0 - 60, "B ∝ r", size=13, color=POS, bold=True))

    # Hyperbolic part for r > R: B ~ 1/r
    path_pts = []
    for step in range(0, 140, 5):
        r_val = R_px + step
        # B = Bmax * (R_px / r_val)
        y_val = gy0 - (gh - 50) * (R_px / r_val)
        path_pts.append(f"{gx0 + r_val:.1f},{y_val:.1f}")

    path_str = "M " + " L ".join(path_pts)
    out.append(f'<path d="{path_str}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    out.append(text(gx0 + 175, gy0 - 45, "B ∝ 1/r", size=13, color=NEG, bold=True))

    out.append('</svg>')
    return "\n".join(out)


def generate_toroid_geometry():
    width, height = 620, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    # Toroid core and concentric magnetic field/contour lines
    cx, cy = 210, 180
    r_inner = 70
    r_outer = 130
    r_core = (r_inner + r_outer) / 2 # 100

    # Outer and inner physical boundaries of toroidal magnetic core
    out.append(circle(cx, cy, r_outer, fill="#f8fafc", stroke=LINE, sw=2))
    out.append(circle(cx, cy, r_inner, fill=BG, stroke=LINE, sw=2))
    out.append(text(cx, cy + 5, "Осердечник", size=13, color=MUTED))

    # Internal circular Ampèrian contour L inside the core
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="none" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    
    # Radius r line
    out.append(line(cx, cy, cx + r_core * 0.866, cy - r_core * 0.5, color=FIELD, sw=1.8))
    out.append(text(cx + 40, cy - 35, "r", size=14, color=FIELD, bold=True, italic=True))

    # Winding representation (dots inside inner radius, crosses outside outer radius)
    import math
    num_turns = 16
    for i in range(num_turns):
        angle = 2 * math.pi * i / num_turns
        # Inner turn wire (dots)
        ix = cx + (r_inner - 12) * math.cos(angle)
        iy = cy + (r_inner - 12) * math.sin(angle)
        out.append(circle(ix, iy, 4, fill=POS, stroke=POS, sw=1))
        
        # Outer turn wire (crosses)
        ox = cx + (r_outer + 12) * math.cos(angle)
        oy = cy + (r_outer + 12) * math.sin(angle)
        out.append(circle(ox, oy, 4, fill="none", stroke=NEG, sw=1.2))

    # Formula box on the right
    fbox, fw, fh = textbox(470, 180, "Тороїдальна котушка (N витків)\n\n∮_L B · dl = B · (2·π·r)\n\nI_охоп = N · I\n\nB(r) = (μ₀ · N · I) / (2·π·r)\n\nПоле поза тороїдом: B = 0", size=13, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(fbox)

    out.append('</svg>')
    return "\n".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    files = {
        'ampere-contour.svg': generate_ampere_contour(),
        'solenoid-contour.svg': generate_solenoid_contour(),
        'thick-wire-profile.svg': generate_thick_wire_profile(),
        'toroid-geometry.svg': generate_toroid_geometry()
    }

    for fname, content in files.items():
        path = os.path.join(img_dir, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == '__main__':
    main()
