# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/thermodynamics/maxwell-relations/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_thermodynamic_square():
    width, height = 640, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
    </defs>''')

    # Main Born Square coordinates
    cx, cy = 210, 215
    side = 180
    x_left, x_right = cx - side // 2, cx + side // 2
    y_top, y_bot = cy - side // 2, cy + side // 2

    # Draw main square outline
    out.append(rect(x_left, y_top, side, side, fill="#f8fafc", stroke=LINE, sw=2, rx=8))

    # Diagonal dashed lines across square for mnemonic rule
    out.append(line(x_left + 45, y_top + 45, x_right - 45, y_bot - 45, color=MUTED, sw=1.5, dash="4,4"))
    out.append(line(x_left + 45, y_bot - 45, x_right - 45, y_top + 45, color=MUTED, sw=1.5, dash="4,4"))

    # Four Corners: Natural Variables V, S, P, T
    # Top-Left: V (Volume)
    out.append(circle(x_left, y_top, 20, fill="#eaf0fd", stroke=NEG, sw=2))
    out.append(text(x_left, y_top + 5, "V", size=16, color=NEG, bold=True))
    out.append(text(x_left - 35, y_top - 10, "Об'єм", size=12, color=MUTED))

    # Bottom-Left: S (Entropy)
    out.append(circle(x_left, y_bot, 20, fill="#fdecea", stroke=POS, sw=2))
    out.append(text(x_left, y_bot + 5, "S", size=16, color=POS, bold=True))
    out.append(text(x_left - 40, y_bot + 22, "Ентропія", size=12, color=MUTED))

    # Top-Right: P (Pressure)
    out.append(circle(x_right, y_top, 20, fill="#eaf0fd", stroke=NEG, sw=2))
    out.append(text(x_right, y_top + 5, "P", size=16, color=NEG, bold=True))
    out.append(text(x_right + 35, y_top - 10, "Тиск", size=12, color=MUTED))

    # Bottom-Right: T (Temperature)
    out.append(circle(x_right, y_bot, 20, fill="#fdecea", stroke=POS, sw=2))
    out.append(text(x_right, y_bot + 5, "T", size=16, color=POS, bold=True))
    out.append(text(x_right + 45, y_bot + 22, "Температура", size=12, color=MUTED))

    # Four Sides: Thermodynamic Potentials U, H, F, G placed outside or in center
    # Left Side: U(S, V)
    b_u, _, _ = textbox(x_left - 35, cy, "U(S,V)\nВнутр. енергія", size=10, pad=4, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(b_u)

    # Right Side: H(S, P)
    b_h, _, _ = textbox(x_right + 35, cy, "H(S,P)\nЕнтальпія", size=10, pad=4, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(b_h)

    # Top Side: F(T, V)
    b_f, _, _ = textbox(cx, y_top - 20, "F(T,V) — Гельмгольц", size=11, pad=5, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(b_f)

    # Bottom Side: G(T, P)
    b_g, _, _ = textbox(cx, y_bot + 20, "G(T,P) — Гіббс", size=11, pad=5, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(b_g)

    # Mnemonic Guide Box on the Right
    guide_text = (
        "Як читати квадрат Борна:\n\n"
        "1. Потенціал лежить між\n"
        "   своїми природними змінними.\n"
        "   Наприклад: F(T,V), G(T,P).\n\n"
        "2. Сусідні кути дають часткові\n"
        "   похідні співвідношень Максвелла.\n\n"
        "3. (∂S/∂V)ᵀ = (∂P/∂T)ᵥ  [F(T,V)]\n"
        "   (∂S/∂P)ᵀ = −(∂V/∂T)ₚ [G(T,P)]"
    )
    fbox, fw, fh = textbox(485, 215, guide_text, size=12, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(fbox)

    out.append('</svg>')
    return "\n".join(out)


def generate_state_surface_derivatives():
    width, height = 640, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
    </defs>''')

    # Left Panel: P-V Isotherms showing (∂P/∂T)_V slope
    lx0, ly0 = 70, 300
    lw, lh = 200, 210

    # Axes
    out.append(arrow(lx0, ly0, lx0 + lw + 20, ly0, color=INK, sw=2))
    out.append(arrow(lx0, ly0, lx0, ly0 - lh - 10, color=INK, sw=2))
    out.append(text(lx0 + lw + 20, ly0 + 18, "V", size=14, color=INK, bold=True, italic=True))
    out.append(text(lx0 - 18, ly0 - lh - 5, "P", size=14, color=INK, bold=True, italic=True))

    # Two Isotherms T1 and T2 (T2 > T1)
    pts_t1 = []
    pts_t2 = []
    for x in range(25, 180, 5):
        y1 = ly0 - (3500 / (x + 10))
        y2 = ly0 - (4900 / (x + 10))
        pts_t1.append(f"{lx0 + x:.1f},{y1:.1f}")
        pts_t2.append(f"{lx0 + x:.1f},{y2:.1f}")

    out.append(f'<path d="M {" L ".join(pts_t1)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(f'<path d="M {" L ".join(pts_t2)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    out.append(text(lx0 + 175, ly0 - 25, "T₁", size=13, color=NEG, bold=True))
    out.append(text(lx0 + 175, ly0 - 60, "T₂ > T₁", size=13, color=POS, bold=True))

    # Constant Volume line V = V0
    v0_x = lx0 + 90
    out.append(line(v0_x, ly0, v0_x, ly0 - lh + 20, color=FIELD, sw=2, dash="5,4"))
    out.append(text(v0_x, ly0 + 20, "V₀ = const", size=12, color=FIELD, bold=True))

    # Pressure increment ΔP at constant V0
    p1_y = ly0 - (3500 / (90 + 10))
    p2_y = ly0 - (4900 / (90 + 10))
    out.append(circle(v0_x, p1_y, 4, fill=NEG, stroke=NEG, sw=1))
    out.append(circle(v0_x, p2_y, 4, fill=POS, stroke=POS, sw=1))
    out.append(line(v0_x + 10, p1_y, v0_x + 10, p2_y, color=INK, sw=1.5))
    out.append(text(v0_x + 42, (p1_y + p2_y) / 2 + 4, "(∂P/∂T)ᵥ", size=13, color=INK, bold=True))

    # Right Panel: Equivalence to (∂S/∂V)_T
    rx0 = 320
    rbox, rw, rh = textbox(rx0 + 130, 180, 
                           "Геометрична рівність похідних:\n\n"
                           "1. Градієнт тиску з температурою\n"
                           "   при сталому об'ємі (∂P/∂T)ᵥ\n"
                           "   визначений кривою стану.\n\n"
                           "2. За співвідношенням Максвелла F(T,V):\n"
                           "   (∂S/∂V)ᵀ = (∂P/∂T)ᵥ\n\n"
                           "3. Приріст ентропії при ізотермічному\n"
                           "   розширенні точно дорівнює\n"
                           "   термічному коефіцієнту тиску!",
                           size=12, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(rbox)

    out.append('</svg>')
    return "\n".join(out)


def generate_joule_thomson_cascade():
    width, height = 640, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">']
    out.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a1a1a"/>
      </marker>
    </defs>''')

    # Title box at top
    out.append(text(320, 30, "Каскад заміни похідних у термодинаміці", size=16, color=INK, bold=True))

    # Step 1: Inaccessible Entropy Derivative (∂S/∂P)_T
    b1, _, _ = textbox(150, 110, "Невимірювана похідна\n(∂S/∂P)ᵀ", size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    out.append(b1)

    # Arrow from Step 1 to Step 2 with Maxwell Relation label
    out.append(arrow(240, 110, 380, 110, color=INK, sw=2))
    out.append(text(310, 95, "Заміна за Максвеллом (G)", size=12, color=MUTED, bold=True))
    out.append(text(310, 130, "(∂S/∂P)ᵀ = −(∂V/∂T)ₚ", size=12, color=FIELD, bold=True))

    # Step 2: Measurable Thermal Expansion (∂V/∂T)_P
    b2, _, _ = textbox(490, 110, "Вимірювана величина\n−(∂V/∂T)ₚ = −V·α", size=13, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True)
    out.append(b2)

    # Downward arrow to Practical Applications
    out.append(arrow(490, 155, 490, 220, color=INK, sw=2))
    out.append(arrow(150, 155, 150, 220, color=INK, sw=2))

    # Bottom Left: Heat Capacity Difference C_P - C_V
    b3, _, _ = textbox(150, 270, "Різниця теплоємностей\nCₚ − Cᵥ = T·V·α² / κₜ", size=13, pad=12, fill=FILL, stroke=LINE, sw=1.5, bold=True)
    out.append(b3)

    # Bottom Right: Joule-Thomson Coefficient μ_JT
    b4, _, _ = textbox(490, 270, "Ефект Джоуля — Томсона\nμ_JT = (V / Cₚ) · (T·α − 1)", size=13, pad=12, fill=FILL, stroke=LINE, sw=1.5, bold=True)
    out.append(b4)

    out.append('</svg>')
    return "\n".join(out)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    files = {
        'thermodynamic-square.svg': generate_thermodynamic_square(),
        'state-surface-derivatives.svg': generate_state_surface_derivatives(),
        'joule-thomson-cascade.svg': generate_joule_thomson_cascade()
    }

    for fname, content in files.items():
        path = os.path.join(img_dir, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {path}")

if __name__ == '__main__':
    main()
