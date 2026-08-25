# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Термоелектронна та автоелектронна емісія"
(book/physics/condensed-matter-physics/thermal-field-emission)
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def polyline(pts_str, color=LINE, sw=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'

def save_svg(name, content):
    filepath = os.path.join(OUT_DIR, name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Збережено: {filepath}")

def make_defs():
    return '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>
    </marker>
  </defs>'''

# 1. emission-regimes.svg
def gen_emission_regimes():
    w, h = 880, 500
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    t_box, _, _ = textbox(440, 25, "Основні режими електронної емісії з металу в вакуум", size=16, bold=True)
    out.append(t_box)

    panels = [
        ("а) Термоелектронна (Річардсон)", "Режим: T висока, E = 0", 40, 60, 380, 195),
        ("б) Ефект Шотткі", "Режим: T висока, E помірне", 460, 60, 380, 195),
        ("в) Автоелектронна (Фаулер — Нордгейм)", "Режим: T = 0 K, E сильне (~10⁹ V/m)", 40, 275, 380, 195),
        ("г) Термоавтоелектронна", "Режим: T підвищена, E сильне", 460, 275, 380, 195),
    ]

    for p_title, p_sub, px, py, pw, ph in panels:
        out.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
        out.append(text(px + 15, py + 22, p_title, size=12, bold=True, anchor="start", color=INK))
        out.append(text(px + 15, py + 38, p_sub, size=10, italic=True, anchor="start", color=MUTED))

        # Internal coordinate system for each panel
        mx = px + 60
        my_ef = py + 155
        my_vac = py + 75

        # Metal block
        out.append(rect(px + 10, py + 50, 50, 130, fill="#eaeeef", stroke="#95a5a6", sw=1, rx=0))
        out.append(text(px + 35, py + 120, "Метал", size=11, bold=True, color="#34495e", anchor="middle"))

        # Fermi level line
        out.append(line(px + 10, my_ef, px + pw - 25, my_ef, color=NEG, sw=1.5, dash="4 4"))
        out.append(text(px + pw - 30, my_ef - 6, "E_F", size=11, bold=True, color=NEG, anchor="end"))

        # Vacuum level step or barrier curve
        if "Термоелектронна" in p_title:
            out.append(line(mx, my_ef, mx, my_vac, color=POS, sw=2))
            out.append(line(mx, my_vac, px + pw - 30, my_vac, color=POS, sw=2))
            out.append(arrow(mx - 20, my_ef - 5, mx + 30, my_vac - 15, color=POS, sw=2))
            out.append(circle(mx + 30, my_vac - 15, 4, fill=POS, stroke=POS))
            out.append(text(mx + 45, my_vac - 15, "e⁻ over Φ", size=10, bold=True, color=POS, anchor="start"))
        elif "Шотткі" in p_title:
            pts = []
            for i in range(100):
                x_rel = i / 99.0
                x_curr = mx + x_rel * 240
                y_curr = my_vac + 15 + (my_ef - my_vac - 15) * math.exp(-x_rel * 3) - 25 * math.sin(x_rel * math.pi)
                pts.append(f"{x_curr:.1f},{y_curr:.1f}")
            out.append(polyline(" ".join(pts), color=POS, sw=2))
            out.append(arrow(mx - 20, my_ef - 5, mx + 40, my_vac + 10, color=POS, sw=2))
            out.append(circle(mx + 40, my_vac + 10, 4, fill=POS, stroke=POS))
            out.append(text(mx + 55, my_vac + 10, "e⁻ over (Φ-ΔΦ)", size=10, bold=True, color=POS, anchor="start"))
        elif "Автоелектронна" in p_title:
            out.append(line(mx, my_ef, mx, my_vac, color=POS, sw=2))
            out.append(line(mx, my_vac, px + pw - 30, my_ef + 10, color=POS, sw=2))
            out.append(arrow(mx - 25, my_ef - 10, mx + 85, my_ef - 10, color=NEG, sw=2))
            out.append(circle(mx + 85, my_ef - 10, 4, fill=NEG, stroke=NEG))
            out.append(text(mx + 95, my_ef - 22, "тунелювання", size=10, bold=True, color=NEG, anchor="start"))
        else:
            out.append(line(mx, my_ef, mx, my_vac, color=POS, sw=2))
            out.append(line(mx, my_vac, px + pw - 30, my_ef + 10, color=POS, sw=2))
            y_exc = my_ef - 45
            out.append(arrow(mx - 25, y_exc, mx + 65, y_exc, color="#8e44ad", sw=2))
            out.append(circle(mx + 65, y_exc, 4, fill="#8e44ad", stroke="#8e44ad"))
            out.append(text(mx + 75, y_exc - 12, "T-F тунелювання", size=10, bold=True, color="#8e44ad", anchor="start"))

    save_svg("emission-regimes.svg", "\n".join(out) + "\n</svg>")

# 2. schottky-barrier.svg
def gen_schottky_barrier():
    w, h = 880, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    t_box, _, _ = textbox(440, 25, "Потенціальний бар'єр Шотткі та ефект зниження роботи виходу", size=15, bold=True)
    out.append(t_box)

    ox, oy = 110, 380
    pw, ph = 660, 300

    # Axes
    out.append(line(ox, oy, ox + pw, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph, color=INK, sw=2))

    out.append(text(ox + pw - 10, oy + 25, "Відстань від поверхні x", size=12, bold=True, anchor="end"))
    out.append(text(ox - 15, oy - ph + 15, "Потенціальна енергія V(x)", size=12, bold=True, anchor="start"))

    # Metal interface at x = 0
    out.append(rect(40, oy - ph, ox - 40, ph + 10, fill="#eaeeef", stroke="#95a5a6", sw=1.5, rx=0))
    out.append(text(75, oy - ph / 2, "Метал", size=14, bold=True, color="#2c3e50", anchor="middle"))

    # Key horizontal levels
    y_ef = oy - 60
    y_vac0 = oy - 260

    out.append(line(ox, y_ef, ox + pw - 120, y_ef, color=NEG, sw=1.5, dash="5 5"))
    out.append(text(ox + pw - 10, y_ef + 4, "Рівень Фермі E_F", size=12, bold=True, color=NEG, anchor="end"))

    out.append(line(ox, y_vac0, ox + pw - 150, y_vac0, color=MUTED, sw=1.5, dash="5 5"))
    out.append(text(ox + pw - 10, y_vac0 + 4, "E_vac (без поля)", size=12, bold=True, color=MUTED, anchor="end"))

    # Generate potential curves
    pts_total = []
    pts_field = []
    pts_image = []

    x_peak = 140
    y_peak = y_vac0 + 45

    steps = 150
    for i in range(1, steps + 1):
        x_val = (i / steps) * (pw - 120)
        x_px = ox + x_val

        v_field = 0.45 * x_val
        v_img = 120.0 / (x_val + 12.0)
        v_tot = y_vac0 + v_img + v_field

        if v_tot <= oy:
            pts_total.append(f"{x_px:.1f},{v_tot:.1f}")

        y_f = y_vac0 + v_field
        if y_f <= oy:
            pts_field.append(f"{x_px:.1f},{y_f:.1f}")

        y_im = y_vac0 + v_img
        if y_im <= oy and x_val > 5:
            pts_image.append(f"{x_px:.1f},{y_im:.1f}")

    # Draw curves
    out.append(polyline(" ".join(pts_field), color="#8e44ad", sw=1.5, dash="4 4"))
    out.append(text(ox + 320, y_vac0 + 175, "Зовнішнє поле: -e E x", size=11, color="#8e44ad", anchor="start"))

    out.append(polyline(" ".join(pts_image), color=FIELD, sw=1.5, dash="4 4"))
    out.append(text(ox + 200, y_vac0 + 35, "Сила відображення", size=11, color=FIELD, anchor="start"))

    out.append(polyline(" ".join(pts_total), color=POS, sw=3))

    # Peak position markers
    peak_x_px = ox + x_peak
    out.append(line(peak_x_px, oy, peak_x_px, y_peak, color=POS, sw=1.5, dash="3 3"))
    out.append(circle(peak_x_px, y_peak, 5, fill=POS, stroke=POS))
    out.append(text(peak_x_px, oy + 22, "x_max", size=12, bold=True, color=POS, anchor="middle"))

    # Dimension lines for Phi and Delta Phi
    out.append(line(ox + 40, y_ef, ox + 40, y_vac0, color=INK, sw=1.5))
    out.append(arrow(ox + 40, y_ef, ox + 40, y_vac0, color=INK, sw=1.5))
    out.append(arrow(ox + 40, y_vac0, ox + 40, y_ef, color=INK, sw=1.5))
    out.append(text(ox + 48, (y_ef + y_vac0) / 2, "Φ (робота виходу)", size=12, bold=True, color=INK, anchor="start"))

    out.append(line(peak_x_px + 20, y_vac0, peak_x_px + 20, y_peak, color=POS, sw=1.5))
    out.append(arrow(peak_x_px + 20, y_vac0, peak_x_px + 20, y_peak, color=POS, sw=1.5))
    out.append(arrow(peak_x_px + 20, y_peak, peak_x_px + 20, y_vac0, color=POS, sw=1.5))
    out.append(text(peak_x_px + 28, (y_vac0 + y_peak) / 2 + 4, "ΔΦ", size=12, bold=True, color=POS, anchor="start"))

    save_svg("schottky-barrier.svg", "\n".join(out) + "\n</svg>")

# 3. fowler-nordheim-plot.svg
def gen_fowler_nordheim_plot():
    w, h = 860, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    t_box, _, _ = textbox(430, 25, "Графік Фаулера — Нордгейма: ln(J / E²) залежно від 1 / E", size=15, bold=True)
    out.append(t_box)

    ox, oy = 110, 380
    pw, ph = 680, 300

    # Axes
    out.append(line(ox, oy, ox + pw, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph, color=INK, sw=2))

    out.append(text(ox + pw - 10, oy + 30, "Обернене напружене поле 1 / E (10⁻⁹ m/V)", size=12, bold=True, anchor="end"))
    out.append(text(ox - 15, oy - ph + 15, "ln( J / E² )", size=12, bold=True, anchor="start"))

    # Cold Field Emission Line (Straight negative slope)
    x1, y1 = ox + 80, oy - 250
    x2, y2 = ox + 550, oy - 50

    out.append(line(x1, y1, x2, y2, color=NEG, sw=3))

    # Thermal-Field deviation curve (at higher temperature / lower field)
    pts_tf = []
    for i in range(80):
        t_rel = i / 79.0
        cx = ox + 350 + t_rel * 280
        cy = (oy - 120) - 0.25 * (cx - (ox + 350)) - 55 * math.sin(t_rel * math.pi * 0.7)
        pts_tf.append(f"{cx:.1f},{cy:.1f}")

    out.append(polyline(" ".join(pts_tf), color=POS, sw=2.5, dash="6 3"))

    # Slope triangle indicator
    tx1, ty1 = ox + 180, oy - 207
    tx2, ty2 = ox + 320, oy - 207
    tx3, ty3 = ox + 320, oy - 148

    out.append(line(tx1, ty1, tx2, ty2, color="#7f8c8d", sw=1.5, dash="3 3"))
    out.append(line(tx2, ty2, tx3, ty3, color="#7f8c8d", sw=1.5, dash="3 3"))
    out.append(text((tx1 + tx2) / 2, ty1 - 8, "Δ(1/E)", size=11, color="#7f8c8d", anchor="middle"))
    out.append(text(tx2 + 12, (ty1 + ty3) / 2, "Δ ln(J/E²)", size=11, color="#7f8c8d", anchor="start"))

    # Annotations and Callout Boxes
    b1, _, _ = textbox(ox + 200, oy - 260, "Прямолінійна ділянка (Холодна автоемісія)\nСхил k = -B_FN · Φ^(3/2) / β", size=11, fill="#eef6fb", stroke=NEG)
    out.append(b1)

    b2, _, _ = textbox(ox + 520, oy - 240, "Відхилення при високих T\n(Термоавтоелектронна емісія)", size=11, fill="#fdedec", stroke=POS)
    out.append(b2)

    # Position formula box b3 below axis or at ox + 430, oy - 35
    b3, _, _ = textbox(ox + 430, oy - 35, "Рівняння Фаулера — Нордгейма: J = C₁ · E² · exp( - C₂ · Φ^(3/2) / E )", size=11, fill="#f4f6f8", stroke=LINE)
    out.append(b3)

    save_svg("fowler-nordheim-plot.svg", "\n".join(out) + "\n</svg>")

# 4. tip-field-enhancement.svg
def gen_tip_field_enhancement():
    w, h = 860, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    t_box, _, _ = textbox(430, 25, "Геометричне підсилення електричного поля на мікроскопічному вістрі", size=15, bold=True)
    out.append(t_box)

    cx, cy = 320, 250

    # Draw Needle / Emitter Tip shape
    tip_path = f"M 80 120 L 220 210 Q 320 250 220 290 L 80 380 Z"
    out.append(f'<path d="{tip_path}" fill="#eaeeef" stroke="#2c3e50" stroke-width="2"/>')
    out.append(text(140, 250, "Катод (вістря)", size=14, bold=True, color="#2c3e50", anchor="middle"))

    # Anode plane on right
    out.append(rect(680, 80, 30, 340, fill="#d5dbdb", stroke="#7f8c8d", sw=2, rx=2))
    out.append(text(695, 250, "Анод (площина)", size=14, bold=True, color="#2c3e50", anchor="middle"))

    # Equipotential surfaces
    for r_idx, r_val in enumerate([40, 80, 140, 220, 310]):
        pts_eq = []
        steps = 60
        for i in range(steps + 1):
            ang = -math.pi/2 + (i / steps) * math.pi
            x_eq = 320 + r_val * math.cos(ang) * (1 - 0.5 * (r_val / 350))
            y_eq = 250 + r_val * math.sin(ang)
            pts_eq.append(f"{x_eq:.1f},{y_eq:.1f}")
        out.append(polyline(" ".join(pts_eq), color="#8e44ad", sw=1.2, dash="4 4"))

    out.append(text(460, 110, "Еквіпотенціальні поверхні", size=11, color="#8e44ad", anchor="middle"))

    # Electric Field vectors
    out.append(arrow(325, 250, 440, 250, color=POS, sw=3))
    out.append(arrow(320, 235, 430, 220, color=POS, sw=2.5))
    out.append(arrow(320, 265, 430, 280, color=POS, sw=2.5))

    out.append(text(390, 210, "E_local = β · E_macro", size=13, bold=True, color=POS, anchor="middle"))

    # Low macro field in middle
    out.append(arrow(520, 250, 620, 250, color=NEG, sw=1.8))
    out.append(arrow(520, 180, 620, 180, color=NEG, sw=1.8))
    out.append(arrow(520, 320, 620, 320, color=NEG, sw=1.8))
    out.append(text(570, 160, "Однорідне поле E_macro", size=11, color=NEG, anchor="middle"))

    # Explanatory Info Card
    info_str = "Коефіцієнт підсилення β:\n• Сферичне вістря: β ≈ r_anode / R_tip\n• Циліндрична нитка: β ≈ h / R\n• Нанотрубки / голки: β = 100 ... 1000"
    b_info, _, _ = textbox(430, 400, info_str, size=11, fill="#f8f9f9", stroke=LINE)
    out.append(b_info)

    save_svg("fowler-nordheim-plot.svg", "\n".join(out) + "\n</svg>")

if __name__ == "__main__":
    gen_emission_regimes()
    gen_schottky_barrier()
    gen_fowler_nordheim_plot()
    gen_tip_field_enhancement()
    print("Усі SVG-фігури згенеровано успішно.")
