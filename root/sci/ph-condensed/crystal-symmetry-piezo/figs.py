# -*- coding: utf-8 -*-
import sys
import os
import math

# Add path to scripts/ in repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

def dashed_rect(x, y, w, h, stroke="#94a3b8", sw=1.2, dash="4,4"):
    return (line(x, y, x + w, y, color=stroke, sw=sw, dash=dash) +
            line(x + w, y, x + w, y + h, color=stroke, sw=sw, dash=dash) +
            line(x + w, y + h, x, y + h, color=stroke, sw=sw, dash=dash) +
            line(x, y + h, x, y, color=stroke, sw=sw, dash=dash))

# 1. Direct vs Converse Piezoelectric Effect
def gen_direct_converse_piezo():
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 25, "Прямий та зворотний п'єзоелектричний ефект", size=16, bold=True))

    # Left Panel: Direct Piezoelectric Effect (Stress -> Charge/Field)
    p1_x, p1_y, p1_w, p1_h = 30, 55, 360, 280
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Прямий п'єзоефект: P_i = d_ijk · σ_jk", size=14, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w/2, p1_y + 45, "Механічне напруження створює електричний заряд", size=12, color=MUTED, italic=True))

    # Unstressed Crystal outline (dashed)
    cx1, cy1 = p1_x + p1_w/2, p1_y + 160
    frags.append(dashed_rect(cx1 - 75, cy1 - 50, 150, 100, stroke="#94a3b8", sw=1.2, dash="4,4"))

    # Deformed Crystal (compressed vertically)
    frags.append(rect(cx1 - 85, cy1 - 38, 170, 76, fill="#dbeafe", stroke="#2563eb", sw=1.8, rx=4))
    frags.append(text(cx1, cy1 + 4, "П'єзокристал", size=13, bold=True, color="#1e3a8a"))

    # Stress arrows (Mechanical force F / sigma)
    frags.append(arrow(cx1, cy1 - 80, cx1, cy1 - 44, color="#dc2626", sw=2.5))
    frags.append(text(cx1 + 18, cy1 - 62, "F (стискання)", size=12, bold=True, color="#dc2626", anchor="start"))

    frags.append(arrow(cx1, cy1 + 80, cx1, cy1 + 44, color="#dc2626", sw=2.5))
    frags.append(text(cx1 + 18, cy1 + 62, "F (стискання)", size=12, bold=True, color="#dc2626", anchor="start"))

    # Surface charges (+ on top, - on bottom)
    for qx in range(int(cx1 - 70), int(cx1 + 75), 24):
        frags.append(text(qx, cy1 - 44, "+", size=14, bold=True, color="#dc2626"))
        frags.append(text(qx, cy1 + 52, "−", size=14, bold=True, color="#2563eb"))

    # Polarization vector P
    frags.append(arrow(cx1 + 110, cy1 + 30, cx1 + 110, cy1 - 30, color="#7c3aed", sw=2.2))
    frags.append(text(cx1 + 120, cy1 + 4, "Поляризація P", size=12, bold=True, color="#7c3aed", anchor="start"))

    # Right Panel: Converse Piezoelectric Effect (Electric Field -> Mechanical Strain)
    p2_x, p2_y, p2_w, p2_h = 430, 55, 360, 280
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Зворотний п'єзоефект: ε_jk = d_ijk · E_i", size=14, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w/2, p2_y + 45, "Зовнішнє поле викликає механічну деформацію", size=12, color=MUTED, italic=True))

    cx2, cy2 = p2_x + p2_w/2, p2_y + 160

    # Original state (dashed)
    frags.append(dashed_rect(cx2 - 75, cy2 - 50, 150, 100, stroke="#94a3b8", sw=1.2, dash="4,4"))

    # Elongated crystal under electric field
    frags.append(rect(cx2 - 68, cy2 - 66, 136, 132, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=4))
    frags.append(text(cx2, cy2 + 4, "П'єзокристал", size=13, bold=True, color="#78350f"))

    # Electrodes & Voltage source V
    frags.append(rect(cx2 - 72, cy2 - 72, 144, 6, fill="#475569", stroke="#334155", sw=1.0))
    frags.append(rect(cx2 - 72, cy2 + 66, 144, 6, fill="#475569", stroke="#334155", sw=1.0))

    # Applied Electric Field E
    frags.append(arrow(cx2 - 100, cy2 - 55, cx2 - 100, cy2 + 55, color="#0284c7", sw=2.2))
    frags.append(text(cx2 - 110, cy2 + 4, "Поле E", size=12, bold=True, color="#0284c7", anchor="end"))

    # Strain delta L
    frags.append(arrow(cx2 + 90, cy2 - 50, cx2 + 90, cy2 - 66, color="#d97706", sw=1.8))
    frags.append(arrow(cx2 + 90, cy2 + 50, cx2 + 90, cy2 + 66, color="#d97706", sw=1.8))
    frags.append(text(cx2 + 100, cy2 - 58, "+ΔL", size=12, bold=True, color="#d97706", anchor="start"))
    frags.append(text(cx2 + 100, cy2 + 62, "+ΔL", size=12, bold=True, color="#d97706", anchor="start"))

    render(os.path.join(OUT_DIR, "direct-vs-converse-piezo.svg"), w, h, *frags)

# 2. Inversion Symmetry vs Non-Centrosymmetric Lattice Deformation
def gen_inversion_symmetry_dipoles():
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 25, "Мікроскопічний механізм: Центросиметрична vs Нецентросиметрична ґратка", size=16, bold=True))

    # Left Panel: Centrosymmetric Unit Cell (Inversion Center I)
    p1_x, p1_y, p1_w, p1_h = 30, 55, 360, 310
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Центросиметрична ґратка (є центр I)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w/2, p1_y + 45, "Симетричний зсув: P = 0 навіть при деформації", size=12, color="#dc2626", bold=True))

    cx1, cy1 = p1_x + p1_w/2, p1_y + 170

    # Square cell (dashed)
    frags.append(dashed_rect(cx1 - 65, cy1 - 65, 130, 130, stroke="#94a3b8", sw=1.5, dash="3,3"))

    # Anions (corners, negative charge -e)
    for dx in [-65, 65]:
        for dy in [-65, 65]:
            frags.append(circle(cx1 + dx, cy1 + dy, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))
            frags.append(text(cx1 + dx, cy1 + dy + 4, "−", size=14, bold=True, color="#ffffff"))

    # Central Cation (positive charge +4e)
    frags.append(circle(cx1, cy1, 14, fill="#ef4444", stroke="#b91c1c", sw=1.2))
    frags.append(text(cx1, cy1 + 4, "+", size=14, bold=True, color="#ffffff"))

    # Inversion Center marker
    frags.append(circle(cx1, cy1, 3, fill="#ffffff", stroke="#000000", sw=1.0))
    frags.append(text(cx1, cy1 + 95, "Центр мас позитивних і негативних зарядів збігається", size=11, color=INK))
    frags.append(text(cx1, cy1 + 115, "Сумарний дипольний момент p = 0", size=12, bold=True, color="#0f172a"))

    # Right Panel: Non-Centrosymmetric Unit Cell (No Inversion Center)
    p2_x, p2_y, p2_w, p2_h = 430, 55, 360, 310
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Нецентросиметрична ґратка (без центра I)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w/2, p2_y + 45, "Асиметричний зсув: виникає поляризація P ≠ 0", size=12, color="#059669", bold=True))

    cx2, cy2 = p2_x + p2_w/2, p2_y + 170

    # Deformed triangular/asymmetric cell under compression
    frags.append(path(f"M {cx2-75} {cy2+65} L {cx2+75} {cy2+65} L {cx2} {cy2-65} Z", fill="none", stroke="#94a3b8", sw=1.5, dash="3,3"))

    # Anions (base corners and top)
    frags.append(circle(cx2 - 75, cy2 + 65, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))
    frags.append(text(cx2 - 75, cy2 + 69, "−", size=14, bold=True, color="#ffffff"))

    frags.append(circle(cx2 + 75, cy2 + 65, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))
    frags.append(text(cx2 + 75, cy2 + 69, "−", size=14, bold=True, color="#ffffff"))

    frags.append(circle(cx2, cy2 - 65, 12, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))
    frags.append(text(cx2, cy2 - 61, "−", size=14, bold=True, color="#ffffff"))

    # Central Cation shifted upwards under vertical stress F
    cation_y = cy2 - 15
    frags.append(circle(cx2, cation_y, 14, fill="#ef4444", stroke="#b91c1c", sw=1.2))
    frags.append(text(cx2, cation_y + 4, "+", size=14, bold=True, color="#ffffff"))

    # Dipole vector p
    frags.append(arrow(cx2 + 45, cy2 + 25, cx2 + 45, cation_y - 15, color="#7c3aed", sw=2.2))
    frags.append(text(cx2 + 55, cy2 + 5, "Диполь p ≠ 0", size=12, bold=True, color="#7c3aed", anchor="start"))

    frags.append(text(cx2, cy2 + 95, "Деформація розділяє центри + та − зарядів", size=11, color=INK))
    frags.append(text(cx2, cy2 + 115, "Макроскопічна поляризація P = ∑ p / V ≠ 0", size=12, bold=True, color="#059669"))

    render(os.path.join(OUT_DIR, "inversion-symmetry-dipoles.svg"), w, h, *frags)

# 3. Voigt Notation Mapping Matrix structure
def gen_voigt_tensor_matrix():
    w, h = 800, 360
    frags = []

    frags.append(text(w / 2, 25, "Згортка тензора п'єзомодулів у нотацію Фойгта: d_ijk (3×3×3) → d_iα (3×6)", size=16, bold=True))

    # Left: Stress tensor symmetry mapping
    p1_x, p1_y, p1_w, p1_h = 30, 55, 340, 280
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Мапування індексів напруження (jk)", size=14, bold=True, color="#0f172a"))

    mapping_data = [
        ("σ_11 (нормальне х)", "(11)", "α = 1"),
        ("σ_22 (нормальне y)", "(22)", "α = 2"),
        ("σ_33 (нормальне z)", "(33)", "α = 3"),
        ("σ_23 = σ_32 (зсув yz)", "(23, 32)", "α = 4"),
        ("σ_13 = σ_31 (зсув xz)", "(13, 31)", "α = 5"),
        ("σ_12 = σ_21 (зсув xy)", "(12, 21)", "α = 6")
    ]

    for idx, (label, jk, alpha) in enumerate(mapping_data):
        my = p1_y + 60 + idx * 34
        frags.append(rect(p1_x + 20, my, 130, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=3))
        frags.append(text(p1_x + 85, my + 17, label, size=11, color="#1e293b"))

        frags.append(arrow(p1_x + 155, my + 13, p1_x + 210, my + 13, color="#64748b", sw=1.2))

        frags.append(rect(p1_x + 215, my, 105, 26, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=3))
        frags.append(text(p1_x + 267, my + 17, f"{jk} → {alpha}", size=11, bold=True, color="#1e40af"))

    # Right: Matrix d_iα (3x6) representation
    p2_x, p2_y, p2_w, p2_h = 400, 55, 370, 280
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Структура матриці п'єзомодулів d_iα", size=14, bold=True, color="#0f172a"))

    # Grid for 3 rows (i=1,2,3) x 6 columns (alpha=1..6)
    mx0, my0 = p2_x + 50, p2_y + 75
    cw, rh = 48, 36

    # Column headers alpha = 1..6
    for a in range(1, 7):
        frags.append(text(mx0 + (a-1)*cw + cw/2, my0 - 10, f"α={a}", size=11, bold=True, color="#0369a1"))

    # Row headers i = 1,2,3
    for i in range(1, 4):
        frags.append(text(mx0 - 25, my0 + (i-1)*rh + rh/2 + 4, f"i={i}", size=11, bold=True, color="#b91c1c"))

    # Matrix bracket
    frags.append(path(f"M {mx0-5} {my0-18} L {mx0-12} {my0-18} L {mx0-12} {my0+3*rh+5} L {mx0-5} {my0+3*rh+5}", fill="none", stroke="#0f172a", sw=2.0))
    frags.append(path(f"M {mx0+6*cw+5} {my0-18} L {mx0+6*cw+12} {my0-18} L {mx0+6*cw+12} {my0+3*rh+5} L {mx0+6*cw+5} {my0+3*rh+5}", fill="none", stroke="#0f172a", sw=2.0))

    # Cells
    for i in range(1, 4):
        for a in range(1, 7):
            cx = mx0 + (a-1)*cw
            cy = my0 + (i-1)*rh
            bg = "#eff6ff" if (i==1 and a in [1,4]) or (i==2 and a in [5,6]) or (i==3 and a==3) else "#ffffff"
            stroke_c = "#93c5fd" if bg == "#eff6ff" else "#e2e8f0"
            frags.append(rect(cx + 2, cy + 2, cw - 4, rh - 4, fill=bg, stroke=stroke_c, sw=1.0, rx=3))
            frags.append(text(cx + cw/2, cy + rh/2 + 4, f"d_{i}{a}", size=10, color="#1e293b"))

    frags.append(text(p2_x + p2_w/2, p2_y + p2_h - 25, "18 незалежних коефіцієнтів у найнижчій (триклінній) симетрії", size=11, color=MUTED, italic=True))
    frags.append(text(p2_x + p2_w/2, p2_y + p2_h - 10, "Симетрія кристала обнуляє або пов'язує елементи матриці", size=11, bold=True, color="#0f172a"))

    render(os.path.join(OUT_DIR, "voigt-tensor-matrix.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_direct_converse_piezo()
    gen_inversion_symmetry_dipoles()
    gen_voigt_tensor_matrix()
    print("SVG generation complete.")
