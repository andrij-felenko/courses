# -*- coding: utf-8 -*-
import sys
import os
import math

# Add path to scripts/ in repository root (4 levels up from topic directory)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

# ─────────────────────────────────────────────────────────────────────────────
# Figure 1: Comparison of Running Coupling Constants in QED and QCD
# ─────────────────────────────────────────────────────────────────────────────
def gen_fig1():
    w, h = 820, 400
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Порівняння залежності констант зв'язку в QED та КХД (QCD)", size=16, bold=True))

    # Graph Area
    gx, gy, gw, gh = 90, 65, 680, 285

    # Background grid & border
    frags.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))

    # Grid lines
    for i in range(1, 5):
        y_grid = gy + i * (gh / 5)
        frags.append(line(gx, y_grid, gx + gw, y_grid, color="#e2e8f0", sw=1.0, dash="3,3"))
    for j in range(1, 6):
        x_grid = gx + j * (gw / 6)
        frags.append(line(x_grid, gy, x_grid, gy + gh, color="#e2e8f0", sw=1.0, dash="3,3"))

    # Axes
    frags.append(line(gx, gy + gh, gx + gw + 10, gy + gh, color=INK, sw=2.0))
    frags.append(line(gx, gy - 10, gx, gy + gh, color=INK, sw=2.0))

    # Axis Labels
    frags.append(text(gx + gw / 2, gy + gh + 36, "Енергетичний масштаб переданого імпульсу Q² (логарифмічна шкала)", size=13, bold=True, color="#0f172a"))
    frags.append(mtext(gx - 45, gy + gh / 2 - 20, ["Ефективна", "константа", "зв'язку", "α(Q²)"], size=12, bold=True, color="#0f172a"))

    # QED Curve (Red/Pink): Screening -> increases with Q²
    qed_pts = []
    for step in range(101):
        t = step / 100.0
        x_val = gx + t * gw
        y_norm = 0.85 - 0.5 * (t**1.8)
        y_val = gy + y_norm * gh
        qed_pts.append((x_val, y_val))

    d_qed = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in qed_pts)
    frags.append(path(d_qed, fill="none", stroke=POS, sw=3.0))

    # QCD Curve (Blue): Anti-screening -> decreases with Q² (Asymptotic Freedom)
    qcd_pts = []
    for step in range(101):
        t = step / 100.0
        x_val = gx + t * gw
        y_norm = 0.18 + 0.65 * (math.log(1 + 9 * t) / math.log(10))
        y_val = gy + y_norm * gh
        qcd_pts.append((x_val, y_val))

    d_qcd_real = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in qcd_pts)
    frags.append(path(d_qcd_real, fill="none", stroke=NEG, sw=3.0))

    # Vertical threshold line: Lambda_QCD
    x_lambda = gx + 0.08 * gw
    frags.append(line(x_lambda, gy, x_lambda, gy + gh, color="#9333ea", sw=1.5, dash="4,4"))
    frags.append(rect(x_lambda - 45, gy + gh - 145, 90, 42, fill="#f3e8ff", stroke="#c084fc", sw=1.0, rx=4))
    frags.append(text(x_lambda, gy + gh - 130, "Λ_QCD ≈ 200 МеВ", size=11, bold=True, color="#6b21a8"))
    frags.append(text(x_lambda, gy + gh - 114, "Межа полону", size=10, italic=True, color="#6b21a8"))

    # Regions text boxes
    frags.append(rect(gx + 80, gy + 20, 200, 50, fill="#fee2e2", stroke="#fca5a5", sw=1.0, rx=4))
    frags.append(text(gx + 180, gy + 40, "Сильний зв'язок (α_s ~ 1)", size=12, bold=True, color="#991b1b"))
    frags.append(text(gx + 180, gy + 57, "Конфайнмент (полону кварків)", size=11, color="#991b1b"))

    frags.append(rect(gx + gw - 240, gy + gh - 90, 220, 50, fill="#dbeafe", stroke="#93c5fd", sw=1.0, rx=4))
    frags.append(text(gx + gw - 130, gy + gh - 70, "Асимптотична свобода (α_s « 1)", size=12, bold=True, color="#1e40af"))
    frags.append(text(gx + gw - 130, gy + gh - 53, "Теорія збурень (pQCD) працює", size=11, color="#1e40af"))

    # Curve Annotations
    frags.append(text(gx + gw - 120, gy + 80, "QED: Екранування (зростання α)", size=12, bold=True, color=POS))
    frags.append(text(gx + gw - 120, gy + gh - 115, "КХД: Антиекранування (асимптотична свобода)", size=12, bold=True, color=NEG))

    render(os.path.join(OUT_DIR, 'fig1-running-coupling-comparison.svg'), w, h, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: Quantum Vacuum Polarization Loops: Screening vs Anti-Screening
# ─────────────────────────────────────────────────────────────────────────────
def gen_fig2():
    w, h = 840, 380
    frags = []

    frags.append(text(w / 2, 26, "Механізми вакуумної поляризації: Екранування та Антиекранування", size=16, bold=True))

    # Panel 1: QED Screening (Electron loop)
    p1_x, p1_y, p1_w, p1_h = 20, 55, 250, 305
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 24, "QED: Ферміонна петля", size=14, bold=True, color="#991b1b"))
    frags.append(text(p1_x + p1_w/2, p1_y + 42, "Екранування електричного заряду", size=11, italic=True, color=MUTED))

    cy1 = p1_y + 135
    frags.append(line(p1_x + 25, cy1, p1_x + 85, cy1, color=INK, sw=2.0))
    frags.append(ellipse(p1_x + 125, cy1, 40, 25, fill="none", stroke=POS, sw=2.0))
    frags.append(line(p1_x + 165, cy1, p1_x + 225, cy1, color=INK, sw=2.0))
    frags.append(text(p1_x + 125, cy1 - 32, "e⁻", size=12, bold=True, color=POS))
    frags.append(text(p1_x + 125, cy1 + 42, "e⁺", size=12, bold=True, color=POS))

    frags.append(rect(p1_x + 15, p1_y + 205, p1_w - 30, 85, fill=BG, stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(p1_x + p1_w/2, p1_y + 224, "Внесок до бета-функції:", size=11, bold=True, color=INK))
    frags.append(text(p1_x + p1_w/2, p1_y + 244, "β_QED(e) = + (e³ / 12π²) > 0", size=12, bold=True, color=POS))
    frags.append(text(p1_x + p1_w/2, p1_y + 272, "Заряд зростає на малій відстані", size=11, color=MUTED))

    # Panel 2: QCD Quark Loop (Screening)
    p2_x, p2_y, p2_w, p2_h = 295, 55, 250, 305
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 24, "КХД: Кваркова петля q q̄", size=14, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w/2, p2_y + 42, "Колірне екранування (n_f ароматів)", size=11, italic=True, color=MUTED))

    cy2 = p2_y + 135
    frags.append(line(p2_x + 25, cy2, p2_x + 85, cy2, color=INK, sw=2.0, dash="5,3"))
    frags.append(ellipse(p2_x + 125, cy2, 40, 25, fill="none", stroke="#0284c7", sw=2.0))
    frags.append(line(p2_x + 165, cy2, p2_x + 225, cy2, color=INK, sw=2.0, dash="5,3"))
    frags.append(text(p2_x + 125, cy2 - 32, "q", size=12, bold=True, color="#0284c7"))
    frags.append(text(p2_x + 125, cy2 + 42, "q̄", size=12, bold=True, color="#0284c7"))

    frags.append(rect(p2_x + 15, p2_y + 205, p2_w - 30, 85, fill=BG, stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(p2_x + p2_w/2, p2_y + 224, "Внесок кварків до β₀:", size=11, bold=True, color=INK))
    frags.append(text(p2_x + p2_w/2, p2_y + 244, "Δβ₀(кварки) = - (2/3) · n_f", size=12, bold=True, color="#0284c7"))
    frags.append(text(p2_x + p2_w/2, p2_y + 272, "Зменшує антиекранування", size=11, color=MUTED))

    # Panel 3: QCD Gluon Loop (Anti-screening)
    p3_x, p3_y, p3_w, p3_h = 570, 55, 250, 305
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(p3_x + p3_w/2, p3_y + 24, "КХД: Ґлуонна петля", size=14, bold=True, color="#1e40af"))
    frags.append(text(p3_x + p3_w/2, p3_y + 42, "Антиекранування (самодія ґлуонів)", size=11, italic=True, color=MUTED))

    cy3 = p3_y + 135
    frags.append(line(p3_x + 25, cy3, p3_x + 85, cy3, color=NEG, sw=2.5))
    frags.append(ellipse(p3_x + 125, cy3, 40, 25, fill="none", stroke=NEG, sw=2.5))
    frags.append(line(p3_x + 165, cy3, p3_x + 225, cy3, color=NEG, sw=2.5))
    frags.append(text(p3_x + 125, cy3 - 32, "g (ґлуон)", size=12, bold=True, color=NEG))
    frags.append(text(p3_x + 125, cy3 + 42, "g (ґлуон)", size=12, bold=True, color=NEG))

    frags.append(rect(p3_x + 15, p3_y + 205, p3_w - 30, 85, fill=BG, stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(p3_x + p3_w/2, p3_y + 224, "Внесок калібрувальних ґлуонів:", size=11, bold=True, color=INK))
    frags.append(text(p3_x + p3_w/2, p3_y + 244, "Δβ₀(ґлуони) = + 11 (домінує!)", size=12, bold=True, color=NEG))
    frags.append(text(p3_x + p3_w/2, p3_y + 272, "β₀ = 11 - (2/3)n_f > 0", size=11, bold=True, color="#1e40af"))

    render(os.path.join(OUT_DIR, 'fig2-gluon-quark-loops.svg'), w, h, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3: Deep Inelastic Scattering & Color String Confinement
# ─────────────────────────────────────────────────────────────────────────────
def gen_fig3():
    w, h = 840, 390
    frags = []

    frags.append(text(w / 2, 26, "Глибоконепружне розсіяння (DIS) та формування колірної трубки взаємодії", size=16, bold=True))

    # Panel A: High-Q² DIS (Asymptotic Freedom)
    p1_x, p1_y, p1_w, p1_h = 20, 55, 390, 315
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 24, "А. Високі Q²: Вільні точкові кварки (DIS)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w/2, p1_y + 42, "Мала довжина хвилі λ ~ 1/√Q² (Бйоркенівське масштабування)", size=11, italic=True, color=MUTED))

    # Proton bag
    cx1, cy1 = p1_x + 220, p1_y + 185
    frags.append(ellipse(cx1, cy1, 120, 85, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(cx1, cy1 - 65, "Протон (u u d)", size=12, bold=True, color="#475569"))

    # Incident lepton (electron) trajectory
    frags.append(line(p1_x + 35, p1_y + 110, p1_x + 130, cy1 - 20, color=POS, sw=2.0))
    frags.append(line(p1_x + 130, cy1 - 20, p1_x + 45, p1_y + 260, color=POS, sw=2.0))
    frags.append(text(p1_x + 60, p1_y + 100, "e⁻ (початковий)", size=11, bold=True, color=POS))
    frags.append(text(p1_x + 60, p1_y + 275, "e⁻ (розсіяний)", size=11, bold=True, color=POS))

    # Virtual photon exchange
    frags.append(line(p1_x + 130, cy1 - 20, cx1 - 40, cy1 - 10, color="#9333ea", sw=2.0, dash="3,3"))
    frags.append(text(cx1 - 85, cy1 - 32, "γ* (віртуальний фотон)", size=11, bold=True, color="#6b21a8"))
    frags.append(text(cx1 - 85, cy1 - 16, "високий Q²", size=10, italic=True, color="#6b21a8"))

    # Quarks inside proton
    q_coords = [(cx1 - 40, cy1 - 10, "u", POS), (cx1 + 40, cy1 - 35, "u", NEG), (cx1 + 10, cy1 + 40, "d", FIELD)]
    for qx, qy, qlabel, qcol in q_coords:
        frags.append(circle(qx, qy, 14, fill=qcol, stroke="#1e293b", sw=1.5))
        frags.append(text(qx, qy + 4, qlabel, size=12, bold=True, color="#ffffff"))

    # Weak gluon exchanges (thin lines)
    frags.append(line(cx1 - 40, cy1 - 10, cx1 + 40, cy1 - 35, color="#cbd5e1", sw=1.0))
    frags.append(line(cx1 - 40, cy1 - 10, cx1 + 10, cy1 + 40, color="#cbd5e1", sw=1.0))

    # Bottom summary box
    frags.append(rect(p1_x + 20, p1_y + 250, p1_w - 40, 50, fill=BG, stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(p1_x + p1_w/2, p1_y + 270, "Кварки поводяться як квазівільні частинки", size=11, bold=True, color="#1e40af"))
    frags.append(text(p1_x + p1_w/2, p1_y + 287, "Непружне розсіння на поодиноких партонах", size=10, color=MUTED))

    # Panel B: Low Q² / Large Distance Confinement (Flux Tube)
    p2_x, p2_y, p2_w, p2_h = 430, 55, 390, 315
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fffbeb", stroke="#fde68a", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 24, "Б. Низькі Q² (r ~ 1 фм): Трубка колірного поля", size=14, bold=True, color="#b45309"))
    frags.append(text(p2_x + p2_w/2, p2_y + 42, "Лінійний потенціал конфайнменту V(r) = σ · r", size=11, italic=True, color=MUTED))

    # Separated Quark-Antiquark Pair
    qx1, qy1 = p2_x + 70, p2_y + 145
    qx2, qy2 = p2_x + 320, p2_y + 145

    # Color flux tube
    frags.append(rect(qx1 + 14, qy1 - 18, (qx2 - qx1) - 28, 36, fill="#fef08a", stroke="#f59e0b", sw=1.5, rx=6))
    for i in range(5):
        lx = qx1 + 35 + i * 50
        frags.append(line(lx, qy1 - 15, lx + 20, qy1 + 15, color="#d97706", sw=1.5))

    # Quarks
    frags.append(circle(qx1, qy1, 16, fill=POS, stroke="#1e293b", sw=1.5))
    frags.append(text(qx1, qy1 + 5, "q", size=13, bold=True, color="#ffffff"))

    frags.append(circle(qx2, qy2, 16, fill=NEG, stroke="#1e293b", sw=1.5))
    frags.append(text(qx2, qy2 + 5, "q̄", size=13, bold=True, color="#ffffff"))

    frags.append(text(p2_x + p2_w/2, qy1 - 25, "Глюонна струна (натяг σ ≈ 1 Гев/фм)", size=11, bold=True, color="#b45309"))

    # String breaking (Bottom part of Panel B)
    cy_br = p2_y + 235
    frags.append(text(p2_x + p2_w/2, cy_br - 22, "Розрив струни при розтягуванні → Народження нової пари q' q̄'", size=11, bold=True, color="#991b1b"))

    # Two smaller pairs after break
    frags.append(circle(p2_x + 80, cy_br, 11, fill=POS, stroke="#1e293b", sw=1.0))
    frags.append(circle(p2_x + 130, cy_br, 11, fill=FIELD, stroke="#1e293b", sw=1.0))
    frags.append(line(p2_x + 80, cy_br, p2_x + 130, cy_br, color="#f59e0b", sw=2.0))
    frags.append(text(p2_x + 105, cy_br + 26, "Мезон 1", size=10, bold=True, color=INK))

    frags.append(text(p2_x + p2_w/2, cy_br + 4, "⚡", size=16, color="#dc2626"))

    # Pair 2: q' - qbar
    frags.append(circle(p2_x + 260, cy_br, 11, fill=FIELD, stroke="#1e293b", sw=1.0))
    frags.append(circle(p2_x + 310, cy_br, 11, fill=NEG, stroke="#1e293b", sw=1.0))
    frags.append(line(p2_x + 260, cy_br, p2_x + 310, cy_br, color="#f59e0b", sw=2.0))
    frags.append(text(p2_x + 285, cy_br + 26, "Мезон 2", size=10, bold=True, color=INK))

    frags.append(rect(p2_x + 20, p2_y + 275, p2_w - 40, 30, fill=BG, stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(p2_x + p2_w/2, p2_y + 294, "Неможливість виділення поодинокого вільного кварка", size=10, bold=True, color="#991b1b"))

    render(os.path.join(OUT_DIR, 'fig3-deep-inelastic-scattering.svg'), w, h, *frags)


def main():
    gen_fig1()
    gen_fig2()
    gen_fig3()
    print("Figures successfully generated in:", OUT_DIR)

if __name__ == '__main__':
    main()
