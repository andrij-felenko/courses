# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Час релаксації заряду"
(book/physics/electromagnetism/charge-relaxation)
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


def make_defs():
    return '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
    </marker>
  </defs>'''


# 1. charge-decay-timeline.svg
def gen_charge_decay_timeline():
    w, h = 820, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 30, "Динаміка експоненціального згасання об'ємного заряду ρ(t) = ρ₀ · exp(-t / τ)", size=15, bold=True)[0])

    ox, oy = 110, 330
    pw, ph = 400, 240
    
    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw + 40, oy + 5, "t / τ", size=13, bold=True, anchor="start"))
    out.append(text(ox - 10, oy - ph - 15, "ρ(t) / ρ₀", size=13, bold=True, anchor="end"))

    y1_0 = oy - ph
    y0_368 = oy - ph * 0.368
    y0_135 = oy - ph * 0.135

    out.append(line(ox - 5, y1_0, ox + pw, y1_0, color=MUTED, sw=1, dash="4,4"))
    out.append(text(ox - 10, y1_0 + 4, "1.00 (100%)", size=12, anchor="end"))

    out.append(line(ox - 5, y0_368, ox + pw, y0_368, color=MUTED, sw=1, dash="4,4"))
    out.append(text(ox - 10, y0_368 + 4, "0.368 (36.8%)", size=12, color=POS, bold=True, anchor="end"))

    out.append(line(ox - 5, y0_135, ox + pw, y0_135, color=MUTED, sw=1, dash="4,4"))
    out.append(text(ox - 10, y0_135 + 4, "0.135 (13.5%)", size=12, anchor="end"))

    t_ticks = [(0, "0"), (1, "1τ"), (2, "2τ"), (3, "3τ"), (4, "4τ"), (5, "5τ")]
    for t_val, t_lbl in t_ticks:
        tx = ox + (t_val / 5.0) * pw
        out.append(line(tx, oy - 4, tx, oy + 4, color=INK, sw=1.5))
        out.append(text(tx, oy + 20, t_lbl, size=13, bold=(t_val==1)))

    pts = []
    for step in range(101):
        t_norm = (step / 100.0) * 5.0
        val = math.exp(-t_norm)
        px = ox + (t_norm / 5.0) * pw
        py = oy - val * ph
        pts.append(f"{px:.1f},{py:.1f}")

    out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{POS}" stroke-width="3"/>')

    p1_x = ox + (1.0 / 5.0) * pw
    p1_y = y0_368
    out.append(circle(p1_x, p1_y, 5, fill=POS, stroke=INK, sw=1.5))
    out.append(line(p1_x, oy, p1_x, p1_y, color=POS, sw=1.5, dash="3,3"))

    right_x = 680
    out.append('<g transform="translate(0,0)">')
    out.append(rect(560, 80, 240, 300, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(right_x, 105, "Перерозподіл заряду", size=14, bold=True))

    out.append(text(right_x, 135, "Стан t = 0:", size=12, bold=True, color=POS))
    out.append(circle(right_x, 185, 35, fill="#fee2e2", stroke=POS, sw=1.5))
    out.append(text(right_x, 185, "+ρ₀ (в об'ємі)", size=11, color=POS, bold=True))

    out.append(arrow(right_x, 230, right_x, 260, color=LINE, sw=2))
    out.append(text(right_x + 15, 248, "t ≫ τ", size=12, italic=True))

    out.append(text(right_x, 280, "Стан t ≫ τ:", size=12, bold=True, color=FIELD))
    out.append(circle(right_x, 330, 35, fill="#f0fdf4", stroke=FIELD, sw=1.5))
    out.append(text(right_x, 330, "ρ = 0 (всередині)", size=11, color=INK))
    out.append(f'<circle cx="{right_x}" cy="330" r="38" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="3,3"/>')
    out.append(text(right_x, 375, "+σ (на поверхні)", size=11, color=POS, bold=True))
    out.append('</g>')

    out.append("</svg>")
    return "\n".join(out)


# 2. conductor-vs-dielectric-relaxation.svg
def gen_conductor_vs_dielectric_relaxation():
    w, h = 840, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(420, 30, "Спектр максвеллівського часу релаксації заряду τ = ε / σ у різних середовищах", size=15, bold=True)[0])

    ax_y = 200
    ax_x1, ax_x2 = 60, 780
    out.append(line(ax_x1, ax_y, ax_x2, ax_y, color=INK, sw=2))
    out.append(arrow(ax_x1, ax_y, ax_x2, ax_y, color=INK, sw=2))
    out.append(text(ax_x2 - 20, ax_y + 25, "Час релаксації τ (секунди)", size=13, bold=True, anchor="end"))

    materials = [
        ("Мідь (провідник)", "1.5 × 10⁻¹⁹ с", 110, POS, "Зверхшвидкий злив\nв об'ємі металів"),
        ("Легований кремній", "10⁻¹² ... 10⁻⁹ с", 260, "#e67e22", "Напівпровідники\n(піко/наносекунди)"),
        ("Очищена вода", "1.5 × 10⁻⁶ с", 410, FIELD, "Полярні діелектрики\n(мікросекунди)"),
        ("Сухе повітря", "10² ... 10⁴ с", 570, NEG, "Повільний витік\n(хвилини / години)"),
        ("Тефлон / Фторопласт", "10⁵ ... 10⁶ с", 710, "#8e44ad", "Ідеальний ізолятор\n(дні / тижні)")
    ]

    for i, (name, val_str, x_pos, col, desc) in enumerate(materials):
        out.append(line(x_pos, ax_y - 8, x_pos, ax_y + 8, color=col, sw=2.5))
        out.append(circle(x_pos, ax_y, 5, fill=col, stroke=INK, sw=1.5))
        
        tb, _, _ = textbox(x_pos, ax_y - 65, f"{name}\n{val_str}", size=12, fill="#ffffff", stroke=col, sw=1.5, bold=True)
        out.append(tb)

        out.append(mtext(x_pos, ax_y + 45, desc, size=11, color=INK, anchor="middle"))

    out.append("</svg>")
    return "\n".join(out)


# 3. bulk-to-surface-migration.svg
def gen_bulk_to_surface_migration():
    w, h = 820, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 30, "Механізм виштовхування заряду з об'єму на поверхню провідного тіла", size=15, bold=True)[0])

    out.append('<g transform="translate(0,0)">')
    out.append(rect(50, 70, 340, 320, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(220, 95, " Початковий стан (t = 0)", size=14, bold=True, color=POS))
    
    cx1, cy1 = 220, 230
    out.append(circle(cx1, cy1, 85, fill="#fee2e2", stroke=POS, sw=2))
    
    out.append(text(cx1, cy1 - 15, "+ + +", size=16, color=POS, bold=True))
    out.append(text(cx1, cy1 + 15, "+ ρ(0) +", size=14, color=POS, bold=True))

    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        x1 = cx1 + 30 * math.cos(rad)
        y1 = cy1 + 30 * math.sin(rad)
        x2 = cx1 + 75 * math.cos(rad)
        y2 = cy1 + 75 * math.sin(rad)
        out.append(arrow(x1, y1, x2, y2, color=POS, sw=1.5))

    out.append(text(220, 355, "Струм провідності J = σ·E\nвиштовхує однакові заряди", size=12, anchor="middle"))
    out.append('</g>')

    out.append(arrow(405, 230, 445, 230, color=INK, sw=2.5))
    out.append(text(425, 210, "t ≫ τ", size=13, bold=True))

    out.append('<g transform="translate(0,0)">')
    out.append(rect(460, 70, 310, 320, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(615, 95, " Рівноважний стан (t ≫ τ)", size=14, bold=True, color=FIELD))

    cx2, cy2 = 615, 230
    out.append(circle(cx2, cy2, 85, fill="#f0fdf4", stroke=FIELD, sw=2))
    
    out.append(textbox(cx2, cy2, "ρ_bulk = 0\nE_int = 0", size=13, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True)[0])

    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        sx = cx2 + 94 * math.cos(rad)
        sy = cy2 + 94 * math.sin(rad)
        out.append(text(sx, sy + 4, "+", size=14, color=POS, bold=True))

    out.append(text(615, 355, "Весь заряд локалізовано\nу тонкому поверхневому шарі σ_surf", size=12, anchor="middle"))
    out.append('</g>')

    out.append("</svg>")
    return "\n".join(out)


# 4. maxwell-wagner-interface.svg
def gen_maxwell_wagner_interface():
    w, h = 820, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 30, "Міжфазна релаксація Максвелла-Вагнера на межі двох середовищ", size=15, bold=True)[0])

    ox, oy = 80, 80
    w_slab, h_slab = 320, 260
    
    out.append('<g transform="translate(0,0)">')
    out.append(rect(ox, oy, w_slab, h_slab, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=0))
    tb1, _, _ = textbox(ox + w_slab/2, oy + 40, "Середовище 1\nε₁, σ₁  (τ₁ = ε₁/σ₁)", size=13, fill="#ffffff", stroke="#3b82f6", sw=1.5, bold=True)
    out.append(tb1)

    out.append(rect(ox + w_slab, oy, w_slab, h_slab, fill="#fef3c7", stroke="#d97706", sw=2, rx=0))
    tb2, _, _ = textbox(ox + w_slab + w_slab/2, oy + 40, "Середовище 2\nε₂, σ₂  (τ₂ = ε₂/σ₂)", size=13, fill="#ffffff", stroke="#d97706", sw=1.5, bold=True)
    out.append(tb2)

    ix = ox + w_slab
    out.append(line(ix, oy, ix, oy + 150, color=POS, sw=3))
    out.append(line(ix, oy + 260, ix, oy + h_slab, color=POS, sw=3))
    out.append(text(ix, oy - 12, "Межа розділу (Interface)", size=13, color=POS, bold=True))

    out.append(arrow(ox + 30, oy + 110, ix - 10, oy + 110, color="#2563eb", sw=2.5))
    out.append(text(ox + 120, oy + 95, "Струм J₁ = σ₁·E₁", size=12, color="#2563eb", bold=True))

    out.append(arrow(ix + 10, oy + 110, ix + w_slab - 30, oy + 110, color="#d97706", sw=2.5))
    out.append(text(ix + 100, oy + 95, "Струм J₂ = σ₂·E₂", size=12, color="#d97706", bold=True))

    out.append(rect(ix - 70, oy + 160, 140, 90, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    out.append(mtext(ix, oy + 190, "+ σ_f(t) +\nВільний заряд\nна межі", size=12, color=POS, bold=True))
    out.append('</g>')

    out.append(rect(80, 360, 660, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    out.append(text(410, 382, "Якщо τ₁ ≠ τ₂, струми J₁ та J₂ не рівні у перехідному режимі:", size=13, bold=True))
    out.append(text(410, 405, "σ_f(∞) = E₀ · (ε₁·σ₂ - ε₂·σ₁) / (σ₁ + σ₂),  з часом релаксації τ_MW = (ε₁ + ε₂)/(σ₁ + σ₂)", size=12, color=POS, bold=True))

    out.append("</svg>")
    return "\n".join(out)


# 5. drude-plasma-limit.svg
def gen_drude_plasma_limit():
    w, h = 820, 400
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 30, "Межа застосовності: макроскопічна релаксація vs плазмові коливання Друде", size=15, bold=True)[0])

    ox, oy = 130, 320
    pw, ph = 400, 220

    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw + 35, oy + 5, "Час t (фемтосекунди)", size=13, bold=True, anchor="start"))
    out.append(text(ox + 10, oy - ph - 15, "Густина заряду ρ(t)", size=13, bold=True, anchor="start"))

    pts_damped = []
    for step in range(120):
        t = (step / 120.0) * 15.0
        val = math.exp(-t / 4.0) * math.cos(2.0 * math.pi * t / 2.5)
        px = ox + (t / 15.0) * pw
        py = oy - (val * 0.7 + 0.1) * ph
        pts_damped.append(f"{px:.1f},{py:.1f}")

    out.append(f'<polyline points="{" ".join(pts_damped)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    pts_maxwell = []
    for step in range(120):
        t = (step / 120.0) * 15.0
        val = math.exp(-t / 0.5)
        px = ox + (t / 15.0) * pw
        py = oy - val * ph
        pts_maxwell.append(f"{px:.1f},{py:.1f}")
    out.append(f'<polyline points="{" ".join(pts_maxwell)}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,4"/>')

    out.append(line(ox + (4.0/15.0)*pw, oy - 5, ox + (4.0/15.0)*pw, oy + 5, color=FIELD, sw=2))
    out.append(text(ox + (4.0/15.0)*pw, oy + 22, "τ_drude ≈ 10 fs", size=12, color=FIELD, bold=True))

    box_x = 560
    out.append('<g transform="translate(0,0)">')
    out.append(rect(box_x, 75, 240, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    out.append(text(box_x + 120, 98, "Фізичні параметри", size=14, bold=True))

    tb1, _, _ = textbox(box_x + 120, 150, "Континуальна теорія:\nτ_m = ε / σ ≈ 10⁻¹⁹ с\n(Формальний розрахунок)", size=11, stroke="#94a3b8", fill="#ffffff")
    out.append(tb1)

    tb2, _, _ = textbox(box_x + 120, 260, "Реальна фізика металу:\n• Час розсіяння: τ_drude ~ 10 fs\n• Плазмова частота: ω_p ~ 10¹⁶ рад/с\n• Фізична межа релаксації ~ 1 fs", size=11, stroke=POS, fill="#ffffff", bold=True)
    out.append(tb2)
    out.append('</g>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    save_svg("charge-decay-timeline.svg", gen_charge_decay_timeline())
    save_svg("conductor-vs-dielectric-relaxation.svg", gen_conductor_vs_dielectric_relaxation())
    save_svg("bulk-to-surface-migration.svg", gen_bulk_to_surface_migration())
    save_svg("maxwell-wagner-interface.svg", gen_maxwell_wagner_interface())
    save_svg("drude-plasma-limit.svg", gen_drude_plasma_limit())
    print("Усі фігури згенеровано!")

if __name__ == "__main__":
    main()
