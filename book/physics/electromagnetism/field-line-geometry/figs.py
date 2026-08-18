# -*- coding: utf-8 -*-
"""
Generator of SVG figures for field-line-geometry topic.
Run: python figs.py
"""

import os
import sys
import math

# Add scripts dir to path (4 steps up from book/physics/electromagnetism/field-line-geometry)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig1_field_line_definition():
    """Fig 1: Field line definition - tangent vector E and trajectory vs field line."""
    w, h = 760, 380
    els = []
    
    # Title / Header text
    els.append(text(w/2, 28, "Векторне визначення силової лінії та траєкторія частинки", size=16, bold=True))
    
    # Left side: Tangent definition
    path_d = "M 80 260 C 140 120, 240 100, 320 220"
    els.append(f'<path d="{path_d}" fill="none" stroke="{FIELD}" stroke-width="3.0"/>')
    
    els.append(arrow(220, 125, 245, 135, color=FIELD, sw=2.5))
    
    px, py = 190, 128
    els.append(circle(px, py, 5, fill=POS, stroke=INK, sw=1.5))
    els.append(text(px - 15, py + 22, "P (x, y, z)", size=13, bold=True))
    
    tx, ty = px + 80, py - 35
    els.append(arrow(px, py, tx, ty, color=POS, sw=2.5))
    tb = textbox(tx + 45, ty - 12, "E(r) — вектор поля\n(дотичний до лінії)", size=12, fill="#fdedec", stroke=POS)[0]
    els.append(tb)
    
    drx, dry = px + 40, py - 18
    els.append(arrow(px, py, drx, dry, color=LINE, sw=2.0))
    tb_dr = textbox(drx + 25, dry + 25, "dr (елемент дуги)\ndr × E = 0", size=12, fill="#f4f6f8", stroke=LINE)[0]
    els.append(tb_dr)
    
    tb_left = textbox(200, 320, "Силова лінія: у кожній точці дотична\nзбігається з вектором напруженості E", size=13, fill="#e8f8f5", stroke=FIELD)[0]
    els.append(tb_left)
    
    # Separator
    els.append(line(390, 50, 390, 350, color=MUTED, sw=1.0, dash="4,4"))
    
    # Right side: Field line vs trajectory of massive particle
    els.append(f'<path d="M 430 270 C 500 130, 620 110, 710 250" fill="none" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    els.append(text(670, 200, "Силова лінія E", size=13, color=FIELD, bold=True))
    
    els.append(f'<path d="M 430 270 C 540 250, 630 190, 720 150" fill="none" stroke="{NEG}" stroke-width="3.0"/>')
    els.append(text(660, 130, "Траєкторія частинки (m > 0)", size=13, color=NEG, bold=True))
    
    els.append(circle(430, 270, 6, fill=NEG, stroke=INK, sw=1.5))
    els.append(arrow(430, 270, 480, 240, color=NEG, sw=2.0))
    els.append(text(460, 275, "v₀ (інерція)", size=12, color=NEG, bold=True))
    
    tb_right = textbox(570, 320, "Увага: масивна частинка (m > 0)\nвідхиляється від силової лінії через інерцію!", size=13, fill="#ebf5fb", stroke=NEG)[0]
    els.append(tb_right)
    
    filepath = os.path.join(IMG_DIR, "field-line-definition.svg")
    render(filepath, w, h, *els)


def fig2_orthogonality_conductor():
    """Fig 2: Orthogonality between field lines E and equipotentials V=const, conductor surface."""
    w, h = 760, 400
    els = []
    
    els.append(text(w/2, 28, "Ортогональність силових ліній і еквіпотенціальних поверхонь", size=16, bold=True))
    
    y_levels = [100, 160, 220, 280]
    v_labels = ["V = 40 В", "V = 30 В", "V = 20 В", "V = 10 В"]
    for i, y in enumerate(y_levels):
        els.append(line(60, y, 340, y, color="#8e44ad", sw=2.0, dash="6,4"))
        els.append(text(45, y + 4, v_labels[i], size=12, color="#8e44ad", anchor="end", bold=True))
        
    x_lines = [110, 180, 250, 310]
    for x in x_lines:
        els.append(arrow(x, 80, x, 300, color=FIELD, sw=2.2))
        
    ix, iy = 180, 160
    els.append(f'<path d="M {ix+12} {iy} L {ix+12} {iy+12} L {ix} {iy+12}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    els.append(circle(ix+5, iy+5, 1.5, fill=INK, stroke=INK, sw=1))
    els.append(text(ix + 25, iy - 8, "90° (E ⊥ V=const)", size=12, bold=True, color=POS))
    
    tb_grad = textbox(200, 340, "E = −∇V: поле вказує в бік\nнайшвидшого спаду потенціалу", size=13, fill="#f4ecf7", stroke="#8e44ad")[0]
    els.append(tb_grad)
    
    # Separator
    els.append(line(380, 50, 380, 360, color=MUTED, sw=1.0, dash="4,4"))
    
    # Right side: Conductor surface
    path_cond = "M 420 300 C 460 220, 540 180, 620 200 C 670 215, 710 260, 730 300 Z"
    els.append(f'<path d="{path_cond}" fill="#d5dbdb" stroke="#7f8c8d" stroke-width="2.5"/>')
    els.append(text(580, 260, "Провідник (V = const)", size=14, color=INK, bold=True))
    els.append(text(580, 280, "E_всередині = 0", size=12, color=MUTED, bold=True))
    
    normals = [
        (450, 240, 420, 140),
        (510, 200, 500, 90),
        (570, 190, 570, 80),
        (630, 205, 650, 95),
        (690, 245, 720, 145)
    ]
    for x1, y1, x2, y2 in normals:
        els.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.2))
        els.append(circle(x1, y1, 4, fill=POS, stroke=INK, sw=1))
        
    tb_cond = textbox(570, 340, "Поверхня провідника — еквіпотенціаль.\nСилові лінії виходять строго під 90°!", size=13, fill="#e8f8f5", stroke=FIELD)[0]
    els.append(tb_cond)
    
    filepath = os.path.join(IMG_DIR, "orthogonality-conductor.svg")
    render(filepath, w, h, *els)


def fig3_tube_of_force():
    """Fig 3: Tube of force (flux tube), cross sectional area vs line density, 1/r^2 law."""
    w, h = 760, 380
    els = []
    
    els.append(text(w/2, 28, "Силова трубка (потік) і закон обернених квадратів", size=16, bold=True))
    
    els.append(f'<path d="M 60 120 C 160 140, 260 170, 340 190" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    els.append(f'<path d="M 60 260 C 160 240, 260 210, 340 190" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    
    els.append(f'<path d="M 60 166 C 160 173, 260 183, 340 190" fill="none" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    els.append(f'<path d="M 60 214 C 160 207, 260 197, 340 190" fill="none" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    
    els.append(f'<ellipse cx="100" cy="190" rx="15" ry="65" fill="#e8f8f5" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(text(100, 195, "A₁", size=14, color=FIELD, bold=True))
    els.append(text(100, 275, "E₁ (рідке поле)", size=12, color=INK))
    
    els.append(f'<ellipse cx="280" cy="190" rx="8" ry="30" fill="#e8f8f5" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(text(280, 194, "A₂", size=13, color=FIELD, bold=True))
    els.append(text(280, 240, "E₂ (густе)", size=12, color=INK))
    
    tb_flux = textbox(200, 330, "Потік Φ = E₁·A₁ = E₂·A₂ = const\nЗменшення площі A → зростання E", size=13, fill="#e8f8f5", stroke=FIELD)[0]
    els.append(tb_flux)
    
    # Separator
    els.append(line(390, 50, 390, 350, color=MUTED, sw=1.0, dash="4,4"))
    
    # Right side: Spherical expansion 1/r^2
    qx, qy = 440, 190
    els.append(circle(qx, qy, 14, fill=POS, stroke=INK, sw=2.0))
    els.append(text(qx, qy + 5, "+Q", size=12, color="#ffffff", bold=True))
    
    els.append(f'<path d="M 520 110 A 90 90 0 0 1 520 270" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="5,4"/>')
    els.append(text(535, 115, "Сфера r (площа 4πr²)", size=12, color=MUTED, bold=True))
    
    els.append(f'<path d="M 640 50 A 180 180 0 0 1 640 330" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="5,4"/>')
    els.append(text(650, 60, "Сфера 2r (площа 16πr²)", size=12, color=MUTED, bold=True))
    
    angles = [-35, -20, -5, 10, 25, 40]
    for ang in angles:
        rad = math.radians(ang)
        x2 = qx + 280 * math.cos(rad)
        y2 = qy + 280 * math.sin(rad)
        els.append(arrow(qx + 15 * math.cos(rad), qy + 15 * math.sin(rad), min(x2, 730), max(min(y2, 340), 50), color=FIELD, sw=1.8))
        
    tb_sq = textbox(570, 330, "У 3D просторі площа поверхні ∝ r²\nТому густина ліній E(r) ∝ 1/r²", size=13, fill="#fef9e7", stroke="#f39c12")[0]
    els.append(tb_sq)
    
    filepath = os.path.join(IMG_DIR, "tube-of-force.svg")
    render(filepath, w, h, *els)


def fig4_dipole_vs_samecharge():
    """Fig 4: Dipole (+q, -q) vs Pair of same charges (+q, +q) showing saddle point."""
    w, h = 760, 420
    els = []
    
    els.append(text(w/2, 26, "Топологія полів: диполь (+q, −q) та два однойменні заряди (+q, +q)", size=16, bold=True))
    
    # Left side: Dipole (+q and -q)
    els.append(text(190, 55, "Електричний диполь (+q і −q)", size=14, bold=True, color=INK))
    
    q1x, q1y = 120, 200
    q2x, q2y = 260, 200
    
    for r in [25, 45, 65]:
        els.append(f'<circle cx="{q1x}" cy="{q1y}" r="{r}" fill="none" stroke="#8e44ad" stroke-width="1.2" stroke-dasharray="4,3"/>')
        els.append(f'<circle cx="{q2x}" cy="{q2y}" r="{r}" fill="none" stroke="#8e44ad" stroke-width="1.2" stroke-dasharray="4,3"/>')
    els.append(line(190, 80, 190, 320, color="#8e44ad", sw=2.0))
    els.append(text(190, 72, "V = 0", size=12, color="#8e44ad", bold=True))
    
    els.append(arrow(q1x + 14, q1y, q2x - 14, q2y, color=FIELD, sw=2.0))
    els.append(f'<path d="M {q1x} {q1y-14} C {q1x+20} {q1y-80}, {q2x-20} {q2y-80}, {q2x} {q2y-14}" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(arrow(185, 140, 195, 140, color=FIELD, sw=2.0))
    
    els.append(f'<path d="M {q1x} {q1y+14} C {q1x+20} {q1y+80}, {q2x-20} {q2y+80}, {q2x} {q2y+14}" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(arrow(185, 260, 195, 260, color=FIELD, sw=2.0))
    
    els.append(circle(q1x, q1y, 14, fill=POS, stroke=INK, sw=2))
    els.append(text(q1x, q1y + 5, "+q", size=13, color="#ffffff", bold=True))
    
    els.append(circle(q2x, q2y, 14, fill=NEG, stroke=INK, sw=2))
    els.append(text(q2x, q2y + 5, "−q", size=13, color="#ffffff", bold=True))
    
    tb_dip = textbox(190, 365, "Силові лінії починаються на +q\nі закінчуються на −q", size=13, fill="#e8f8f5", stroke=FIELD)[0]
    els.append(tb_dip)
    
    # Separator
    els.append(line(380, 50, 380, 390, color=MUTED, sw=1.0, dash="4,4"))
    
    # Right side: Two positive charges (+q and +q)
    els.append(text(570, 55, "Два однакові заряди (+q і +q)", size=14, bold=True, color=INK))
    
    q3x, q3y = 490, 200
    q4x, q4y = 650, 200
    
    for r in [25, 45]:
        els.append(f'<circle cx="{q3x}" cy="{q3y}" r="{r}" fill="none" stroke="#8e44ad" stroke-width="1.2" stroke-dasharray="4,3"/>')
        els.append(f'<circle cx="{q4x}" cy="{q4y}" r="{r}" fill="none" stroke="#8e44ad" stroke-width="1.2" stroke-dasharray="4,3"/>')
        
    els.append(f'<path d="M 570 200 C 530 130, 430 130, 430 200 C 430 270, 530 270, 570 200 C 610 130, 710 130, 710 200 C 710 270, 610 270, 570 200" fill="none" stroke="#8e44ad" stroke-width="2.0"/>')
    
    spx, spy = 570, 200
    els.append(circle(spx, spy, 6, fill="#f1c40f", stroke=INK, sw=1.8))
    tb_sad = textbox(570, 130, "Точка застою (E = 0)\nСідлова точка еквіпотенціалі", size=12, fill="#fef9e7", stroke="#f39c12")[0]
    els.append(tb_sad)
    
    els.append(f'<path d="M {q3x} {q3y-14} C {q3x+10} {q3y-70}, 560 110, 560 70" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(arrow(545, 115, 555, 80, color=FIELD, sw=2.0))
    
    els.append(f'<path d="M {q4x} {q4y-14} C {q4x-10} {q4y-70}, 580 110, 580 70" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')
    els.append(arrow(595, 115, 585, 80, color=FIELD, sw=2.0))
    
    els.append(circle(q3x, q3y, 14, fill=POS, stroke=INK, sw=2))
    els.append(text(q3x, q3y + 5, "+q", size=13, color="#ffffff", bold=True))
    
    els.append(circle(q4x, q4y, 14, fill=POS, stroke=INK, sw=2))
    els.append(text(q4x, q4y + 5, "+q", size=13, color="#ffffff", bold=True))
    
    tb_same = textbox(570, 365, "Силові лінії відштовхуються;\nу точці застою поле E = 0", size=13, fill="#fef9e7", stroke="#f39c12")[0]
    els.append(tb_same)
    
    filepath = os.path.join(IMG_DIR, "dipole-vs-samecharge.svg")
    render(filepath, w, h, *els)


def fig5_curvilinear_squares():
    """Fig 5: Curvilinear squares grid between conductors of complex geometry."""
    w, h = 760, 380
    els = []
    
    els.append(text(w/2, 28, "Метод криволінійних квадратів (конформна сітка поля)", size=16, bold=True))
    
    els.append(rect(140, 140, 100, 100, fill="#d5dbdb", stroke="#7f8c8d", sw=2.5, rx=20))
    els.append(text(190, 195, "V = V₁", size=14, color=INK, bold=True))
    
    els.append(rect(60, 60, 500, 260, fill="none", stroke="#7f8c8d", sw=3.0, rx=40))
    els.append(text(310, 85, "Зовнішній провідник (V = V₀)", size=14, color=INK, bold=True))
    
    for rx_val, ry_val, w_v, h_v in [(110, 110, 200, 160), (80, 80, 340, 210)]:
        els.append(f'<rect x="{190 - w_v/2:.1f}" y="{190 - h_v/2:.1f}" width="{w_v:.1f}" height="{h_v:.1f}" rx="{rx_val//3}" fill="none" stroke="#8e44ad" stroke-width="1.8" stroke-dasharray="5,4"/>')
        
    flines = [
        (140, 190, 60, 190),
        (240, 190, 560, 190),
        (190, 140, 190, 60),
        (190, 240, 190, 320),
        (150, 150, 90, 90),
        (230, 150, 480, 90),
        (150, 230, 90, 290),
        (230, 230, 480, 290)
    ]
    for x1, y1, x2, y2 in flines:
        els.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.0))
        
    els.append(rect(340, 140, 60, 50, fill="#abebc6", stroke=FIELD, sw=2.0, rx=4))
    els.append(text(370, 160, "Δn ≈ Δs", size=12, color=INK, bold=True))
    els.append(text(370, 178, "(квадрат)", size=11, color=FIELD, bold=True))
    
    tb_info = textbox(650, 190, "Властивості сітки:\n• ΔV = const між шарами\n• ΔU = const між лініями\n• Співвідношення сторін Δn/Δs ≈ 1\n• Ємність C = ε₀ · (N_паралельних / N_послідовних)", size=12, fill="#f4f6f8", stroke=LINE)[0]
    els.append(tb_info)
    
    filepath = os.path.join(IMG_DIR, "curvilinear-squares.svg")
    render(filepath, w, h, *els)


def fig6_sharp_tip_concentration():
    """Fig 6: Field line crowding and equipotential squeezing at a sharp tip."""
    w, h = 760, 380
    els = []
    
    els.append(text(w/2, 28, "Концентрація поля та згущення еквіпотенціалей біля вістря", size=16, bold=True))
    
    els.append(rect(60, 320, 640, 20, fill="#d5dbdb", stroke="#7f8c8d", sw=2.0))
    els.append(text(380, 335, "Заземлена площина (V = 0)", size=13, color=INK, bold=True))
    
    path_tip = "M 320 60 L 440 60 L 400 200 L 380 235 L 360 200 Z"
    els.append(f'<path d="{path_tip}" fill="#b2babb" stroke="#7f8c8d" stroke-width="2.0"/>')
    els.append(text(380, 100, "Вістря (V = V₀)", size=14, color=INK, bold=True))
    
    eq_paths = [
        "M 80 120 C 250 120, 360 220, 380 230 C 400 220, 510 120, 680 120",
        "M 80 170 C 250 170, 365 227, 380 232 C 395 227, 510 170, 680 170",
        "M 80 220 C 250 220, 370 233, 380 234 C 390 233, 510 220, 680 220",
        "M 80 270 L 680 270"
    ]
    for p in eq_paths:
        els.append(f'<path d="{p}" fill="none" stroke="#8e44ad" stroke-width="1.8" stroke-dasharray="5,4"/>')
        
    tip_lines = [
        (380, 235, 380, 320),
        (375, 233, 340, 320),
        (385, 233, 420, 320),
        (370, 230, 280, 320),
        (390, 230, 480, 320),
        (360, 220, 200, 320),
        (400, 220, 560, 320)
    ]
    for x1, y1, x2, y2 in tip_lines:
        els.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.0))
        
    tb_high = textbox(560, 230, "Згущення еквіпотенціалей!\n|∇V| = E → ∞\nРизик коронного пробою", size=13, fill="#fdedec", stroke=POS)[0]
    els.append(tb_high)
    
    tb_tip_exp = textbox(190, 230, "Малий радіус кривини R\n→ велика густина заряду σ ∝ 1/R\n→ гігантська напруженість E", size=12, fill="#f4f6f8", stroke=LINE)[0]
    els.append(tb_tip_exp)
    
    filepath = os.path.join(IMG_DIR, "sharp-tip-concentration.svg")
    render(filepath, w, h, *els)


def main():
    fig1_field_line_definition()
    fig2_orthogonality_conductor()
    fig3_tube_of_force()
    fig4_dipole_vs_samecharge()
    fig5_curvilinear_squares()
    fig6_sharp_tip_concentration()
    print("All 6 figures generated successfully!")

if __name__ == "__main__":
    main()
