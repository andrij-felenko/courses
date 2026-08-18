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

# 1. LJ Potential Energy Curve
def gen_lj_potential_curve():
    w, h = 820, 480
    frags = []

    # Header title
    frags.append(text(w / 2, 28, "Потенціальна енергія Леннард-Джонса V(r) та її компоненти", size=16, bold=True, color="#0f172a"))

    # Plot axes area
    ox, oy = 90, 360
    pw, ph = 680, 300

    # Grid lines
    for vy in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
        py = oy - (vy / 2.0) * (ph * 0.6)
        frags.append(line(ox, py, ox + pw, py, color="#f1f5f9" if vy != 0 else "#94a3b8", sw=1.0 if vy != 0 else 1.5))
        frags.append(text(ox - 15, py + 4, f"{vy:+.1f}", size=11, color="#64748b", anchor="end"))

    # X axis ticks (r / sigma)
    def r_to_x(r_sig):
        return ox + ((r_sig - 0.8) / 2.0) * pw

    for r_val in [0.9, 1.0, 1.122, 1.244, 1.5, 2.0, 2.5]:
        px = r_to_x(r_val)
        if ox <= px <= ox + pw:
            frags.append(line(px, oy + 5, px, oy - ph * 0.65, color="#f1f5f9", sw=1.0))
            frags.append(line(px, oy - 2, px, oy + 4, color="#64748b", sw=1.2))
            lbl = "σ" if abs(r_val - 1.0) < 0.01 else ("r_min" if abs(r_val - 1.122) < 0.01 else f"{r_val:.1f}")
            frags.append(text(px, oy + 20, lbl, size=11, color="#475569"))

    # Axes lines
    frags.append(line(ox, oy - ph * 0.65, ox, oy + 35, color="#334155", sw=1.8))
    frags.append(line(ox - 15, oy, ox + pw + 15, oy, color="#334155", sw=1.8))
    frags.append(text(ox - 45, oy - ph * 0.3, "V(r) / ε", size=13, bold=True, color="#0f172a"))
    frags.append(text(ox + pw + 5, oy + 35, "r / σ", size=13, bold=True, color="#0f172a"))

    # Curves calculation
    pts_total = []
    pts_rep = []
    pts_att = []

    steps = 150
    for i in range(steps + 1):
        r = 0.88 + (i / steps) * 1.92
        inv_r = 1.0 / r
        inv_r6 = inv_r ** 6
        inv_r12 = inv_r6 ** 2

        v_rep = 4.0 * inv_r12
        v_att = -4.0 * inv_r6
        v_tot = v_rep + v_att

        px = r_to_x(r)
        
        py_tot = oy - (v_tot / 2.0) * (ph * 0.6)
        py_rep = oy - (v_rep / 2.0) * (ph * 0.6)
        py_att = oy - (v_att / 2.0) * (ph * 0.6)

        if py_tot >= oy - ph * 0.68 and py_tot <= oy + 45:
            pts_total.append((px, py_tot))
        if py_rep >= oy - ph * 0.68 and py_rep <= oy + 45:
            pts_rep.append((px, py_rep))
        if py_att >= oy - ph * 0.68 and py_att <= oy + 45:
            pts_att.append((px, py_att))

    # Draw Repulsive Curve (dashed purple)
    d_rep = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_rep)
    frags.append(path(d_rep, fill="none", stroke="#8b5cf6", sw=2.0, dash="5,4"))

    # Draw Attractive Curve (dashed cyan)
    d_att = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_att)
    frags.append(path(d_att, fill="none", stroke="#06b6d4", sw=2.0, dash="5,4"))

    # Draw Total Potential Curve (solid dark blue)
    d_tot = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_total)
    frags.append(path(d_tot, fill="none", stroke="#1e3a8a", sw=3.2))

    # Mark key points
    # Point 1: Zero crossing at r = sigma (1.0, 0)
    x_sig = r_to_x(1.0)
    frags.append(circle(x_sig, oy, 5.0, fill="#3b82f6", stroke="#1e3a8a", sw=1.5))
    frags.append(line(x_sig, oy, x_sig - 40, oy - 45, color="#64748b", sw=1.0, dash="2,2"))
    frags.append(rect(x_sig - 130, oy - 75, 120, 36, fill="#eff6ff", stroke="#bfdbfe", sw=1.0, rx=4))
    frags.append(text(x_sig - 70, oy - 62, "V(σ) = 0", size=11, bold=True, color="#1e40af"))
    frags.append(text(x_sig - 70, oy - 48, "Нуль потенціалу", size=10, color="#3b82f6"))

    # Point 2: Minimum at r_min = 2^(1/6) * sigma approx 1.122 sigma, V = -1.0 epsilon
    r_min = 2.0 ** (1.0 / 6.0)
    x_min = r_to_x(r_min)
    y_min = oy - (-1.0 / 2.0) * (ph * 0.6)
    frags.append(circle(x_min, y_min, 6.0, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(line(x_min, oy, x_min, y_min, color="#ef4444", sw=1.2, dash="3,3"))
    frags.append(line(ox, y_min, x_min, y_min, color="#ef4444", sw=1.2, dash="3,3"))

    # Depth arrow and annotation
    frags.append(line(x_min + 30, oy, x_min + 30, y_min, color="#dc2626", sw=1.5))
    frags.append(polygon([(x_min + 30, oy), (x_min + 26, oy + 8), (x_min + 34, oy + 8)], fill="#dc2626"))
    frags.append(polygon([(x_min + 30, y_min), (x_min + 26, y_min - 8), (x_min + 34, y_min - 8)], fill="#dc2626"))
    frags.append(rect(x_min + 45, y_min - 45, 160, 44, fill="#fef2f2", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(x_min + 125, y_min - 32, "Глибина ями -ε", size=11, bold=True, color="#991b1b"))
    frags.append(text(x_min + 125, y_min - 16, f"r_min = 2¹/⁶ σ ≈ {r_min:.3f} σ", size=10, color="#b91c1c"))

    # Legend box top-right
    leg_x, leg_y = ox + pw - 240, oy - ph * 0.62
    frags.append(rect(leg_x, leg_y, 230, 95, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=6))
    frags.append(line(leg_x + 15, leg_y + 22, leg_x + 45, leg_y + 22, color="#1e3a8a", sw=3.0))
    frags.append(text(leg_x + 55, leg_y + 26, "V(r) — повний потенціал", size=11, bold=True, color="#0f172a", anchor="start"))

    frags.append(line(leg_x + 15, leg_y + 47, leg_x + 45, leg_y + 47, color="#8b5cf6", sw=2.0, dash="5,4"))
    frags.append(text(leg_x + 55, leg_y + 51, "Відштовхування Паулі ∝ +1/r¹²", size=10, color="#6b21a8", anchor="start"))

    frags.append(line(leg_x + 15, leg_y + 72, leg_x + 45, leg_y + 72, color="#06b6d4", sw=2.0, dash="5,4"))
    frags.append(text(leg_x + 55, leg_y + 76, "Притягання Ван-дер-Ваальса ∝ -1/r⁶", size=10, color="#0e7490", anchor="start"))

    # Save SVG using svgkit render
    out_path = os.path.join(OUT_DIR, "lj-potential-curve.svg")
    render(out_path, w, h, *frags)
    print("Generated lj-potential-curve.svg")

# 2. Interatomic Forces & Atomic Interactions
def gen_interatomic_forces():
    w, h = 820, 480
    frags = []

    frags.append(text(w / 2, 28, "Міжатомна сила F(r) = -dV/dr та режими взаємодії", size=16, bold=True, color="#0f172a"))

    ox, oy = 90, 250
    pw, ph = 680, 200

    def r_to_x(r_sig):
        return ox + ((r_sig - 0.8) / 2.0) * pw

    # Grid & zero axis
    frags.append(line(ox, oy, ox + pw, oy, color="#64748b", sw=1.5))
    frags.append(line(ox, oy - 160, ox, oy + 160, color="#334155", sw=1.8))
    frags.append(text(ox - 45, oy - 130, "Сила F(r)", size=13, bold=True, color="#0f172a"))
    frags.append(text(ox + pw + 5, oy + 25, "r / σ", size=13, bold=True, color="#0f172a"))

    # X axis ticks
    for r_val in [0.9, 1.0, 1.122, 1.244, 1.5, 2.0, 2.5]:
        px = r_to_x(r_val)
        if ox <= px <= ox + pw:
            frags.append(line(px, oy - 4, px, oy + 4, color="#64748b", sw=1.2))
            lbl = "r_min" if abs(r_val - 1.122) < 0.01 else ("r_inf" if abs(r_val - 1.244) < 0.01 else f"{r_val:.1f}")
            frags.append(text(px, oy + 20, lbl, size=11, color="#475569"))

    # Force Points
    pts_f = []
    steps = 150
    for i in range(steps + 1):
        r = 0.92 + (i / steps) * 1.88
        inv_r = 1.0 / r
        inv_r7 = inv_r ** 7
        inv_r13 = inv_r ** 13

        f_norm = 2.0 * inv_r13 - inv_r7
        px = r_to_x(r)
        py = oy - f_norm * 450.0

        if oy - 160 <= py <= oy + 160:
            pts_f.append((px, py))

    d_force = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_f)
    frags.append(path(d_force, fill="none", stroke="#059669", sw=3.0))

    # Mark Equilibrium F=0 at r_min
    r_min = 2.0 ** (1.0 / 6.0)
    x_min = r_to_x(r_min)
    frags.append(circle(x_min, oy, 6.0, fill="#10b981", stroke="#047857", sw=1.5))
    frags.append(rect(x_min - 60, oy - 55, 120, 36, fill="#ecfdf5", stroke="#a7f3d0", sw=1.0, rx=4))
    frags.append(text(x_min, oy - 42, "F(r_min) = 0", size=11, bold=True, color="#047857"))
    frags.append(text(x_min, oy - 28, "Рівновага сил", size=10, color="#059669"))

    # Mark Inflection Point r_inf (Max Attraction)
    r_inf = (26.0 / 7.0) ** (1.0 / 6.0)
    x_inf = r_to_x(r_inf)
    f_inf = 2.0 * (1.0/r_inf)**13 - (1.0/r_inf)**7
    y_inf = oy - f_inf * 450.0

    frags.append(circle(x_inf, y_inf, 6.0, fill="#f59e0b", stroke="#b45309", sw=1.5))
    frags.append(line(x_inf, oy, x_inf, y_inf, color="#f59e0b", sw=1.2, dash="3,3"))
    frags.append(rect(x_inf + 15, y_inf - 18, 175, 38, fill="#fffbebe", stroke="#fde68a", sw=1.0, rx=4))
    frags.append(text(x_inf + 102, y_inf - 5, "Макс. притягання (r_inf)", size=10, bold=True, color="#b45309"))
    frags.append(text(x_inf + 102, y_inf + 9, "F_max ≈ -2.69 ε/σ", size=10, color="#d97706"))

    # Two Atom Schematics at Bottom
    bot_y = 390
    frags.append(rect(50, bot_y - 45, 720, 115, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(75, bot_y - 28, "Фізичні режими залежно від відстані r:", size=12, bold=True, color="#0f172a", anchor="start"))

    # Region 1: r < r_min (Repulsion)
    frags.append(rect(65, bot_y - 12, 210, 72, fill="#fef2f2", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(170, bot_y + 4, "r < r_min: Відштовхування (F > 0)", size=11, bold=True, color="#991b1b"))
    frags.append(circle(140, bot_y + 36, 16, fill="#fca5a5", stroke="#dc2626", sw=1.2))
    frags.append(circle(162, bot_y + 36, 16, fill="#fca5a5", stroke="#dc2626", sw=1.2))
    frags.append(text(170, bot_y + 54, "Перекриття оболонок Паулі", size=10, color="#b91c1c"))

    # Region 2: r = r_min (Equilibrium)
    frags.append(rect(305, bot_y - 12, 210, 72, fill="#ecfdf5", stroke="#a7f3d0", sw=1.0, rx=4))
    frags.append(text(410, bot_y + 4, "r = r_min: Рівновага (F = 0)", size=11, bold=True, color="#047857"))
    frags.append(circle(375, bot_y + 36, 16, fill="#6ee7b7", stroke="#059669", sw=1.2))
    frags.append(circle(445, bot_y + 36, 16, fill="#6ee7b7", stroke="#059669", sw=1.2))
    frags.append(text(410, bot_y + 54, "Мінімальна енергія -ε", size=10, color="#047857"))

    # Region 3: r > r_min (Attraction)
    frags.append(rect(545, bot_y - 12, 210, 72, fill="#eff6ff", stroke="#bfdbfe", sw=1.0, rx=4))
    frags.append(text(650, bot_y + 4, "r > r_min: Притягання (F < 0)", size=11, bold=True, color="#1e40af"))
    frags.append(circle(600, bot_y + 36, 16, fill="#93c5fd", stroke="#2563eb", sw=1.2))
    frags.append(circle(700, bot_y + 36, 16, fill="#93c5fd", stroke="#2563eb", sw=1.2))
    frags.append(text(650, bot_y + 54, "Дисперсійні диполі Лондона", size=10, color="#1d4ed8"))

    out_path = os.path.join(OUT_DIR, "interatomic-forces.svg")
    render(out_path, w, h, *frags)
    print("Generated interatomic-forces.svg")

# 3. Quantum Origin of van der Waals & Pauli Repulsion
def gen_vdw_dispersion_quantum_origin():
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Квантово-механічна природа міжатомних сил", size=16, bold=True, color="#0f172a"))

    # Left Panel: London Dispersion Attraction (vdW)
    p1_x, p1_y, p1_w, p1_h = 20, 50, 380, 290
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 22, "1. Дисперсійне притягання Лондона (∝ -1/r⁶)", size=13, bold=True, color="#0369a1"))

    # Atom A (Instantaneous Dipole)
    ca_x, ca_y = p1_x + 90, p1_y + 110
    frags.append(circle(ca_x, ca_y, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(circle(ca_x - 10, ca_y, 7, fill="#ef4444", stroke="#b91c1c", sw=1.0))
    frags.append(circle(ca_x + 18, ca_y + 5, 5, fill="#0284c7", stroke="#0369a1", sw=1.0))
    frags.append(text(ca_x, ca_y + 58, "Атом A: Миттєвий диполь", size=11, bold=True, color="#0f172a"))
    frags.append(text(ca_x, ca_y + 74, "μ₁ = q · δx(t)", size=10, color="#475569"))

    # Electric field lines arrow
    frags.append(line(ca_x + 48, ca_y, ca_x + 142, ca_y, color="#0284c7", sw=1.8))
    frags.append(polygon([(ca_x + 142, ca_y), (ca_x + 134, ca_y - 4), (ca_x + 134, ca_y + 4)], fill="#0284c7"))
    frags.append(text(ca_x + 95, ca_y - 10, "Поле E ∝ μ₁/r³", size=10, bold=True, color="#0284c7"))

    # Atom B (Induced Dipole)
    cb_x, cb_y = p1_x + 290, p1_y + 110
    frags.append(circle(cb_x, cb_y, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(circle(cb_x - 12, cb_y, 7, fill="#ef4444", stroke="#b91c1c", sw=1.0))
    frags.append(circle(cb_x + 16, cb_y - 5, 5, fill="#0284c7", stroke="#0369a1", sw=1.0))
    frags.append(text(cb_x, cb_y + 58, "Атом B: Наводнений диполь", size=11, bold=True, color="#0f172a"))
    frags.append(text(cb_x, cb_y + 74, "μ₂ = α · E ∝ α·μ₁/r³", size=10, color="#475569"))

    # Formula card bottom left
    frags.append(rect(p1_x + 20, p1_y + 205, p1_w - 40, 68, fill="#eff6ff", stroke="#bfdbfe", sw=1.0, rx=4))
    frags.append(text(p1_x + p1_w/2, p1_y + 225, "Енергія зв'язку диполів:", size=11, bold=True, color="#1e40af"))
    frags.append(text(p1_x + p1_w/2, p1_y + 243, "V_att ∝ - (μ₁ · μ₂) / r³ ∝ - α · μ₁² / r⁶", size=11, color="#1d4ed8"))

    # Right Panel: Pauli Exchange Repulsion
    p2_x, p2_y, p2_w, p2_h = 420, 50, 380, 290
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 22, "2. Відштовхування Паулі (∝ +1/r¹²)", size=13, bold=True, color="#6b21a8"))

    c1_x, c1_y = p2_x + 130, p2_y + 110
    c2_x, c2_y = p2_x + 250, p2_y + 110
    frags.append(circle(c1_x, c1_y, 45, fill="#f3e8ff", stroke="#a855f7", sw=1.5))
    frags.append(circle(c2_x, c2_y, 45, fill="#f3e8ff", stroke="#a855f7", sw=1.5))
    frags.append(circle(c1_x, c1_y, 7, fill="#6b21a8", stroke="#581c87", sw=1.0))
    frags.append(circle(c2_x, c2_y, 7, fill="#6b21a8", stroke="#581c87", sw=1.0))

    frags.append(ellipse(p2_x + 190, p2_y + 110, 18, 32, fill="#e9d5ff", stroke="#c084fc", sw=1.5))
    frags.append(text(p2_x + 190, p2_y + 106, "Зона", size=10, bold=True, color="#581c87"))
    frags.append(text(p2_x + 190, p2_y + 118, "перекриття", size=10, bold=True, color="#581c87"))

    frags.append(text(p2_x + p2_w/2, p2_y + 172, "Перекриття електронних хмар при r < σ", size=11, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w/2, p2_y + 188, "Принцип заборони Паулі забороняє однаковий стан", size=10, color="#475569"))

    frags.append(rect(p2_x + 20, p2_y + 205, p2_w - 40, 68, fill="#faf5ff", stroke="#e9d5ff", sw=1.0, rx=4))
    frags.append(text(p2_x + p2_w/2, p2_y + 225, "Ортогоналізація квантових станів:", size=11, bold=True, color="#6b21a8"))
    frags.append(text(p2_x + p2_w/2, p2_y + 243, "Різке зростання кінетичної енергії ∝ 1/r¹²", size=11, color="#7e22ce"))

    out_path = os.path.join(OUT_DIR, "vdw-dispersion-quantum-origin.svg")
    render(out_path, w, h, *frags)
    print("Generated vdw-dispersion-quantum-origin.svg")

# 4. LJ Phase Diagram & Simulation Cutoff
def gen_lj_phase_diagram_md():
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 26, "Фазова діаграма та зріз потенціалу в комп'ютерному моделюванні", size=16, bold=True, color="#0f172a"))

    p1_x, p1_y, p1_w, p1_h = 25, 55, 370, 340
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 22, "Фази речовини Леннард-Джонса", size=13, bold=True, color="#0f172a"))

    pox, poy = p1_x + 55, p1_y + 280
    ppw, pph = 280, 220

    frags.append(line(pox, poy, pox + ppw, poy, color="#334155", sw=1.5))
    frags.append(line(pox, poy, pox, poy - pph, color="#334155", sw=1.5))
    frags.append(text(pox - 35, poy - pph / 2, "T*", size=12, bold=True, color="#0f172a"))
    frags.append(text(pox + ppw / 2, poy + 30, "Густина ρ*", size=12, bold=True, color="#0f172a"))

    pts_dome = [
        (pox + 10, poy - 20),
        (pox + 40, poy - 80),
        (pox + 85, poy - 145),
        (pox + 140, poy - 110),
        (pox + 220, poy - 20)
    ]
    d_dome = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_dome)
    frags.append(path(d_dome, fill="#e0f2fe", stroke="#0284c7", sw=2.0))

    pts_solid = [
        (pox + 230, poy - 20),
        (pox + 240, poy - 180),
        (pox + ppw, poy - 180),
        (pox + ppw, poy - 20)
    ]
    d_solid = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_solid)
    frags.append(path(d_solid, fill="#f3e8ff", stroke="#a855f7", sw=1.5))

    frags.append(text(pox + 40, poy - 40, "Газ", size=11, bold=True, color="#0369a1"))
    frags.append(text(pox + 140, poy - 50, "Рідина", size=11, bold=True, color="#0284c7"))
    frags.append(text(pox + 260, poy - 90, "Кристал", size=11, bold=True, color="#6b21a8"))
    frags.append(text(pox + 260, poy - 72, "(ГЦК)", size=10, color="#7e22ce"))
    frags.append(text(pox + 130, poy - 180, "Надкритичний флюїд", size=11, italic=True, color="#475569"))

    frags.append(circle(pox + 85, poy - 145, 5.0, fill="#ef4444", stroke="#991b1b", sw=1.2))
    frags.append(text(pox + 85, poy - 158, "Критична точка (T_c* ≈ 1.32)", size=10, bold=True, color="#b91c1c"))

    # Right Box: MD Cutoff Radius r_c
    p2_x, p2_y, p2_w, p2_h = 425, 55, 370, 340
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 22, "Радіус зрізу r_c та поправка хвоста", size=13, bold=True, color="#0f172a"))

    cox, coy = p2_x + 55, p2_y + 200
    cpw, cph = 280, 150

    frags.append(line(cox, coy, cox + cpw, coy, color="#64748b", sw=1.2))
    frags.append(line(cox, coy - 120, cox, coy + 40, color="#334155", sw=1.5))

    x_rc = cox + 210
    frags.append(line(x_rc, coy - 120, x_rc, coy + 40, color="#ef4444", sw=1.5, dash="4,3"))
    frags.append(text(x_rc, coy + 22, "r_c = 2.5 σ", size=11, bold=True, color="#b91c1c"))

    pts_cut = []
    for i in range(100):
        r = 0.95 + (i / 100.0) * 1.55
        inv_r = 1.0 / r
        inv_r6 = inv_r ** 6
        v_tot = 4.0 * (inv_r6**2 - inv_r6)
        px = cox + ((r - 0.8) / 2.0) * cpw
        py = coy - (v_tot / 2.0) * 60.0
        if coy - 120 <= py <= coy + 40:
            pts_cut.append((px, py))

    d_cut = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_cut)
    frags.append(path(d_cut, fill="none", stroke="#2563eb", sw=2.5))

    frags.append(rect(x_rc, coy - 10, cox + cpw - x_rc, 15, fill="#fee2e2", stroke="none"))
    frags.append(text(p2_x + p2_w/2, p2_y + 250, "Хвіст потенціалу при r > r_c нехтується", size=11, bold=True, color="#991b1b"))
    frags.append(text(p2_x + p2_w/2, p2_y + 270, "Поправка тиску та енергії (Tail correction):", size=10, color="#475569"))

    frags.append(rect(p2_x + 25, p2_y + 285, p2_w - 50, 42, fill="#fef2f2", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(p2_x + p2_w/2, p2_y + 310, "U_tail = (8/9) · π · N · ρ* · ε · (σ / r_c)⁹", size=11, bold=True, color="#991b1b"))

    out_path = os.path.join(OUT_DIR, "lj-phase-diagram-md.svg")
    render(out_path, w, h, *frags)
    print("Generated lj-phase-diagram-md.svg")

if __name__ == "__main__":
    gen_lj_potential_curve()
    gen_interatomic_forces()
    gen_vdw_dispersion_quantum_origin()
    gen_lj_phase_diagram_md()
