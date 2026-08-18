# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Опір Спітцера та провідність іонізованої плазми"
(book/physics/condensed-matter-physics/spitzer-resistivity)
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def save_svg(name, content):
    filepath = os.path.join(OUT_DIR, name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Збережено: {filepath}")

def polyline(pts_str, color=LINE, sw=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'

def make_defs():
    return '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2c3e50"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2980b9"/>
    </marker>
  </defs>'''

# 1. spitzer-coulomb-collision.svg
def gen_coulomb_collision():
    w, h = 860, 480
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    # Header title
    out.append(textbox(430, 25, "Геометрія Кулонівського розсіювання електрона на важкому іоні", size=15, bold=True)[0])

    # Ion position
    ix, iy = 380, 275
    r_debye = 175

    # Debye sphere background
    out.append(f'<circle cx="{ix}" cy="{iy}" r="{r_debye}" fill="#ebf5fb" stroke="#aed6f1" stroke-width="1.5" stroke-dasharray="6 4"/>')
    # Put label safely inside sphere using textbox with white fill
    tb_deb, _, _ = textbox(ix, iy - 135, "Сфера Дебая (радіус r = λ_D)", size=12, fill="#ffffff", stroke="#aed6f1", color="#2980b9", bold=True)
    out.append(tb_deb)

    # Asymptote / Axis
    out.append(line(50, iy, 800, iy, color="#95a5a6", sw=1.5, dash="4 4"))

    # Impact parameter line
    y_inc = iy - 105
    out.append(line(50, y_inc, 340, y_inc, color="#7f8c8d", sw=1, dash="3 3"))

    # Impact parameter b arrow & dimension
    out.append(arrow(ix, iy, ix, y_inc, color="#e67e22", sw=1.5))
    out.append(text(ix - 12, iy - 50, "Прицільний параметр b", size=13, bold=True, color="#d35400", anchor="end"))

    # Electron trajectory curve (Rutherford hyperbolic arc)
    pts = []
    for i in range(120):
        t = -4.0 + (i / 119.0) * 8.0
        x_val = ix + 90 * t
        if x_val < ix - 40:
            y_val = y_inc + 2.0 * math.exp((x_val - (ix - 40)) / 100.0)
        else:
            dx = x_val - (ix - 40)
            y_val = y_inc + 0.55 * dx + 15 * (1 - math.exp(-dx / 80.0))
        pts.append(f"{x_val:.1f},{y_val:.1f}")

    out.append(polyline(" ".join(pts), color="#c0392b", sw=3))

    # Incoming electron velocity arrow
    out.append(arrow(90, y_inc, 170, y_inc, color="#c0392b", sw=2))
    out.append(text(130, y_inc - 12, "Початкова швидкість v_e", size=12, bold=True, color="#c0392b", anchor="middle"))

    # Electron dot
    out.append(f'<circle cx="110" cy="{y_inc}" r="7" fill="#e74c3c" stroke="#922b21" stroke-width="1.5"/>')
    out.append(text(110, y_inc + 22, "Електрон (-e)", size=12, bold=True, color="#c0392b", anchor="middle"))

    # Deflected velocity arrow
    last_y = y_inc + 0.55 * (650 - (ix - 40)) + 15
    out.append(arrow(580, last_y - 38, 660, last_y + 6, color="#c0392b", sw=2))
    out.append(text(640, last_y - 25, "Розсіяна швидкість v_e'", size=12, bold=True, color="#c0392b", anchor="start"))

    # Deflection angle theta arc
    out.append(line(340, y_inc, 750, y_inc, color="#95a5a6", sw=1, dash="3 3"))
    out.append(line(340, y_inc, 720, y_inc + 0.55 * (720 - 340), color="#c0392b", sw=1, dash="3 3"))
    
    # Arc for theta
    arc_r = 90
    arc_start_x = 340 + arc_r
    arc_start_y = y_inc
    arc_end_x = 340 + arc_r * math.cos(math.radians(28))
    arc_end_y = y_inc + arc_r * math.sin(math.radians(28))
    out.append(f'<path d="M {arc_start_x} {arc_start_y} A {arc_r} {arc_r} 0 0 1 {arc_end_x:.1f} {arc_end_y:.1f}" fill="none" stroke="#27ae60" stroke-width="2"/>')
    tb_th, _, _ = textbox(490, y_inc + 35, "Кут відхилення θ", size=12, fill="#ffffff", stroke="#27ae60", color="#27ae60", bold=True)
    out.append(tb_th)

    # Heavy Ion at center
    out.append(f'<circle cx="{ix}" cy="{iy}" r="16" fill="#2980b9" stroke="#1b4f72" stroke-width="2"/>')
    out.append(text(ix, iy + 4, "Z e", size=13, bold=True, color="#ffffff", anchor="middle"))
    out.append(text(ix, iy + 36, "Непорушний іон (+Ze)", size=12, bold=True, color="#1b4f72", anchor="middle"))

    # Distance b_min label
    out.append(f'<circle cx="{ix}" cy="{iy}" r="35" fill="none" stroke="#e74c3c" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(text(ix - 45, iy - 25, "b_min (лобове)", size=11, color="#c0392b", anchor="end"))

    # Legend / Info box
    box_code = fitbox(50, 395, 760, 65, [
        "• Зіткнення з великим b (b >> b_min) дають малий кут θ << 1 рад, але їхня сума визначає 90% опору плазми.",
        "• Обмеження інтегрування: мінімальний параметр b_min (квантовий або класичний), максимальний b_max = λ_D."
    ], bg="#f8f9f9", border="#bdc3c7", padding=8, size=12)
    out.append(box_code)

    out.append("</svg>")
    save_svg("spitzer-coulomb-collision.svg", "\n".join(out))

# 2. spitzer-temperature-dependence.svg
def gen_temperature_dependence():
    w, h = 860, 480
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 25, "Залежність питомого опору плазми Спітцера від температури електронів", size=15, bold=True)[0])

    ox, oy = 90, 370
    pw, ph = 640, 280

    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw + 25, oy + 35, "Температура електронів T_e (еВ)", size=12, bold=True, anchor="end"))
    out.append(text(ox - 10, oy - ph - 15, "Питомий опір η (Ом·м)", size=12, bold=True, anchor="start"))

    def x_scale(t_ev):
        return ox + (math.log10(t_ev) / 4.0) * pw

    t_ticks = [(1, "1 еВ"), (10, "10 еВ"), (100, "100 еВ"), (1000, "1 кеВ"), (10000, "10 кеВ")]
    for t_val, t_lbl in t_ticks:
        xp = x_scale(t_val)
        out.append(line(xp, oy - 4, xp, oy + 6, color=INK, sw=1.5))
        out.append(text(xp, oy + 22, t_lbl, size=12, bold=True, anchor="middle"))

    def y_scale(eta_val):
        log_eta = math.log10(eta_val)
        frac = (-3.0 - log_eta) / 6.0
        return oy - ph + frac * ph

    eta_ticks = [(1e-3, "10⁻³"), (1e-4, "10⁻⁴"), (1e-5, "10⁻⁵"), (1e-6, "10⁻⁶"), (1e-7, "10⁻⁷"), (1e-8, "10⁻⁸"), (1e-9, "10⁻⁹")]
    for e_val, e_lbl in eta_ticks:
        yp = y_scale(e_val)
        out.append(line(ox - 6, yp, ox + 4, yp, color=INK, sw=1.5))
        out.append(text(ox - 12, yp + 4, e_lbl, size=11, bold=True, anchor="end"))

    # Reference line for Copper (eta_Cu ~ 1.7e-8 Ohm*m)
    y_cu = y_scale(1.7e-8)
    out.append(line(ox, y_cu, ox + pw, y_cu, color="#d35400", sw=2, dash="6 4"))
    
    out.append(text(ox + pw - 10, y_cu - 10, "Чиста мідь (300 K): η ≈ 1.7 × 10⁻⁸ Ом·м", size=11, color="#d35400", bold=True, anchor="end"))

    pts_spitzer = []
    steps = 150
    for i in range(steps + 1):
        t_ev = 1.0 * (10000.0 / 1.0) ** (i / steps)
        eta_spitz = 5.2e-5 * 1.0 * 15.0 / (t_ev ** 1.5)
        if eta_spitz > 1e-3:
            eta_spitz = 1e-3
        if eta_spitz < 1e-9:
            eta_spitz = 1e-9
        xp = x_scale(t_ev)
        yp = y_scale(eta_spitz)
        pts_spitzer.append(f"{xp:.1f},{yp:.1f}")

    out.append(polyline(" ".join(pts_spitzer), color="#2980b9", sw=3.5))

    # Formula label cleanly placed in top-right clear area
    out.append(text(ox + 480, oy - ph + 40, "Крива Спітцера: η_Spitzer ∝ T_e^(-3/2)", size=13, color="#2980b9", bold=True, anchor="start"))

    t_cross = 850
    x_cr = x_scale(t_cross)
    out.append(f'<circle cx="{x_cr:.1f}" cy="{y_cu:.1f}" r="6" fill="#e74c3c" stroke="#922b21" stroke-width="2"/>')
    # Dashed line only going down from y_cu to oy to avoid crossing top text
    out.append(line(x_cr, y_cu, x_cr, oy, color="#e74c3c", sw=1.5, dash="3 3"))

    out.append(text(x_cr - 15, y_cu + 25, "Точка перетину (~800 еВ)", size=11, color="#c0392b", bold=True, anchor="end"))
    out.append(text(x_cr - 15, y_cu + 40, "Плазма проводить краще за мідь!", size=11, color="#c0392b", bold=True, anchor="end"))

    out.append("</svg>")
    save_svg("spitzer-temperature-dependence.svg", "\n".join(out))

# 3. spitzer-anisotropy-parallel-perp.svg
def gen_anisotropy():
    w, h = 860, 480
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 25, "Анізотропія переносу струму та опору плазми в магнітному полі", size=15, bold=True)[0])

    # Left panel: Parallel field (E || B)
    out.append(f'<rect x="40" y="60" width="370" height="320" rx="8" fill="#fcf3cf" stroke="#f1c40f" stroke-width="1.5"/>')
    out.append(text(225, 85, "1. Паралельний перенос (E ∥ B)", size=14, bold=True, color="#b7950b", anchor="middle"))

    for y_b in [130, 180, 230, 280]:
        out.append(line(70, y_b, 380, y_b, color="#27ae60", sw=2))
        out.append(arrow(70, y_b, 375, y_b, color="#27ae60", sw=2))
    out.append(text(380, 115, "Магнітне поле B", size=12, bold=True, color="#27ae60", anchor="end"))

    out.append(line(70, 205, 330, 205, color="#c0392b", sw=3))
    out.append(arrow(70, 205, 330, 205, color="#c0392b", sw=3))
    out.append(text(200, 195, "Струм J_∥ та поле E_∥", size=13, bold=True, color="#c0392b", anchor="middle"))

    pts_hel = []
    for i in range(100):
        x_h = 80 + i * 2.5
        y_h = 205 + 18 * math.sin(i * 0.35)
        pts_hel.append(f"{x_h:.1f},{y_h:.1f}")
    out.append(polyline(" ".join(pts_hel), color="#2980b9", sw=2, dash="3 2"))

    out.append(text(225, 330, "Ларморівське обертання не заважає руху вздовж B", size=12, anchor="middle"))
    out.append(text(225, 355, "η_∥ = η_Spitzer (мінімальний опір)", size=13, bold=True, color="#9a7d0a", anchor="middle"))

    # Right panel: Perpendicular field (E perp B)
    out.append(f'<rect x="450" y="60" width="370" height="320" rx="8" fill="#e8f8f5" stroke="#1abc9c" stroke-width="1.5"/>')
    out.append(text(635, 85, "2. Перпендикулярний перенос (E ⊥ B)", size=14, bold=True, color="#16a085", anchor="middle"))

    for bx in [490, 560, 635, 710, 780]:
        for by in [130, 180, 230, 280]:
            out.append(f'<circle cx="{bx}" cy="{by}" r="10" fill="none" stroke="#27ae60" stroke-width="1.5"/>')
            out.append(line(bx - 6, by - 6, bx + 6, by + 6, color="#27ae60", sw=1.5))
            out.append(line(bx - 6, by + 6, bx + 6, by - 6, color="#27ae60", sw=1.5))
    out.append(text(780, 115, "Поле B (напрямлене від нас ⊗)", size=12, bold=True, color="#27ae60", anchor="end"))

    out.append(arrow(520, 310, 520, 130, color="#c0392b", sw=3))
    out.append(text(505, 220, "Поле E_⊥", size=13, bold=True, color="#c0392b", anchor="end"))

    pts_cyc = []
    for i in range(120):
        t = i * 0.1
        x_c = 540 + 20 * (t - math.sin(t))
        y_c = 280 - 18 * (1 - math.cos(t))
        if x_c <= 790:
            pts_cyc.append(f"{x_c:.1f},{y_c:.1f}")
    out.append(polyline(" ".join(pts_cyc), color="#2980b9", sw=2))

    out.append(text(635, 330, "Магнітне поле викривляє траєкторії в кола", size=12, anchor="middle"))
    out.append(text(635, 355, "η_⊥ ≈ 1.96 · η_∥ (у 1.96 раза вищий опір!)", size=13, bold=True, color="#117864", anchor="middle"))

    box_code = fitbox(40, 395, 780, 65, [
        "• Опір Спітцера анізотропний у магнітному полі через пригнічення поперечного дрейфу електронів.",
        "• Співвідношення η_⊥ / η_∥ ≈ 1.96 випливає із сумісного розв'язку кінетичного рівняння Больцмана для Z = 1."
    ], bg="#f8f9f9", border="#bdc3c7", padding=8, size=12)
    out.append(box_code)

    out.append("</svg>")
    save_svg("spitzer-anisotropy-parallel-perp.svg", "\n".join(out))

if __name__ == "__main__":
    gen_coulomb_collision()
    gen_temperature_dependence()
    gen_anisotropy()
