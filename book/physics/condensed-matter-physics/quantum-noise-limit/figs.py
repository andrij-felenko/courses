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

# 1. Thermal to Quantum Noise Crossover Graph
def gen_thermal_quantum_crossover():
    w, h = 780, 430
    frags = []

    frags.append(text(w / 2, 25, "Спектральна густина шуму провідника S_V(ν): класичний vs квантовий режим", size=16, bold=True))

    cx, cy = 90, 350
    pw, ph = 620, 260

    # Axes
    frags.append(arrow(cx, cy, cx + pw + 25, cy, color="#1e293b", sw=2.0))
    frags.append(arrow(cx, cy, cx, cy - ph - 10, color="#1e293b", sw=2.0))
    frags.append(text(cx + pw + 32, cy + 4, "Частота ν", size=13, bold=True, anchor="start"))
    frags.append(text(cx + 10, cy - ph - 22, "Спектральна густина S_V(ν)", size=13, bold=True, anchor="start"))

    # Classical Rayleigh-Jeans horizontal line (4 k_B T R)
    y_rj = cy - 80
    frags.append(line(cx, y_rj, cx + pw, y_rj, color="#3b82f6", sw=2.0, dash="6,4"))
    frags.append(text(cx + pw + 10, y_rj + 4, "Класичне плато: 4 R k_B T", size=12, bold=True, color="#2563eb", anchor="start"))

    # Pure zero-point quantum noise line (2 R h ν)
    pts_zp = []
    for i in range(101):
        x = cx + (i / 100.0) * pw
        y = cy - (i / 100.0) * 220.0
        pts_zp.append(f"{x:.1f},{y:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_zp)}" fill="none" stroke="#9333ea" stroke-width="2.0" stroke-dasharray="4,4"/>')
    frags.append(text(cx + pw - 40, cy - 235, "Нульові флуктуації: 2 R h ν", size=12, bold=True, color="#7e22ce"))

    # Full Quantum Callen-Welton FDT curve: 2 R h ν coth(h ν / 2 k_B T)
    pts_cw = []
    for i in range(101):
        x_val = (i / 100.0) * 4.0  # x = h nu / (k_B T)
        if x_val < 0.05:
            val = 2.0  # limit thermal floor = 4 R k_B T
        else:
            val = x_val * (math.exp(x_val/2.0) + math.exp(-x_val/2.0)) / (math.exp(x_val/2.0) - math.exp(-x_val/2.0))
        
        px = cx + (i / 100.0) * pw
        py = cy - (val / 4.0) * 160.0
        pts_cw.append(f"{px:.1f},{py:.1f}")

    frags.append(f'<polyline points="{" ".join(pts_cw)}" fill="none" stroke="#dc2626" stroke-width="2.8"/>')
    frags.append(text(cx + pw/2 + 20, cy - 170, "Повна теорема Каллена — Велтона", size=13, bold=True, color="#b91c1c"))

    # Crossover point annotation
    x_cross = cx + (1.0 / 4.0) * pw
    y_cross = cy - 80
    frags.append(circle(x_cross, y_cross, 5.0, fill="#dc2626", stroke="#ffffff", sw=1.5))
    frags.append(line(x_cross, cy, x_cross, y_cross, color="#94a3b8", sw=1.2, dash="3,3"))
    frags.append(text(x_cross, cy + 20, "h ν ≈ k_B T", size=12, bold=True, color="#0f172a"))

    # Region highlights
    frags.append(rect(cx + 15, cy - 65, 140, 45, fill="#eff6ff", stroke="#bfdbfe", sw=1.0, rx=4))
    frags.append(text(cx + 85, cy - 42, "Термічний шум (h ν ≪ k_B T)", size=11, color="#1e40af"))

    frags.append(rect(cx + 380, cy - 205, 160, 45, fill="#faf5ff", stroke="#e9d5ff", sw=1.0, rx=4))
    frags.append(text(cx + 460, cy - 182, "Квантовий шум (h ν ≫ k_B T)", size=11, color="#6b21a8"))

    render(os.path.join(OUT_DIR, "thermal-quantum-crossover.svg"), w, h, *frags)

# 2. Standard Quantum Limit (SQL) Backaction Tradeoff Graph
def gen_sql_backaction_tradeoff():
    w, h = 780, 440
    frags = []

    frags.append(text(w / 2, 25, "Стандартна квантова межа (SQL): компроміс вимірювання та зворотного впливу", size=16, bold=True))

    cx, cy = 90, 360
    pw, ph = 620, 270

    # Axes
    frags.append(arrow(cx, cy, cx + pw + 25, cy, color="#1e293b", sw=2.0))
    frags.append(arrow(cx, cy, cx, cy - ph - 10, color="#1e293b", sw=2.0))
    frags.append(text(cx + pw + 32, cy + 4, "Потужність зондування P (або зв'язок)", size=13, bold=True, anchor="start"))
    frags.append(text(cx + 10, cy - ph - 22, "Спектральна густина шуму S_x(ω)", size=13, bold=True, anchor="start"))

    # Measurement Imprecision Noise S_imp ~ 1/P (blue)
    pts_imp = []
    for i in range(1, 101):
        p = i / 100.0 * 4.0 + 0.15
        val = 0.8 / p
        px = cx + (i / 100.0) * pw
        py = cy - val * 90.0
        if py > cy - ph - 10:
            pts_imp.append(f"{px:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_imp)}" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-dasharray="5,4"/>')
    frags.append(text(cx + 90, cy - 245, "Неточність вимірювання S_imp ∝ 1/P (дробовий шум)", size=12, bold=True, color="#1d4ed8"))

    # Quantum Backaction Noise S_back ~ P (green)
    pts_back = []
    for i in range(101):
        p = i / 100.0 * 4.0 + 0.15
        val = 0.8 * p
        px = cx + (i / 100.0) * pw
        py = cy - val * 55.0
        pts_back.append(f"{px:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_back)}" fill="none" stroke="#059669" stroke-width="2.2" stroke-dasharray="5,4"/>')
    frags.append(text(cx + pw - 20, cy - 165, "Зворотний вплив S_back ∝ P (тиск світла)", size=12, bold=True, color="#047857", anchor="end"))

    # Total Noise S_tot = S_imp + S_back (red)
    pts_tot = []
    min_py = 9999
    min_px = 0
    for i in range(1, 101):
        p = i / 100.0 * 4.0 + 0.15
        val = 0.8 / p + 0.8 * p
        px = cx + (i / 100.0) * pw
        py = cy - val * 52.0
        pts_tot.append(f"{px:.1f},{py:.1f}")
        if py < min_py:
            min_py = py
            min_px = px

    frags.append(f'<polyline points="{" ".join(pts_tot)}" fill="none" stroke="#dc2626" stroke-width="3.0"/>')
    frags.append(text(cx + pw/2 + 70, cy - 225, "Загальний шум S_x(ω)", size=14, bold=True, color="#b91c1c"))

    # SQL Point Highlight
    frags.append(circle(min_px, min_py, 6.0, fill="#dc2626", stroke="#ffffff", sw=2.0))
    frags.append(line(min_px, cy, min_px, min_py, color="#475569", sw=1.2, dash="3,3"))
    frags.append(line(cx, min_py, min_px, min_py, color="#475569", sw=1.2, dash="3,3"))

    frags.append(text(min_px, cy + 20, "Оптимальна потужність P_opt", size=12, bold=True, color="#0f172a"))
    frags.append(text(cx - 12, min_py + 4, "S_SQL", size=12, bold=True, color="#b91c1c", anchor="end"))

    # Squeezed State Curve below SQL (purple)
    pts_sq = []
    for i in range(1, 101):
        p = i / 100.0 * 4.0 + 0.15
        val = (0.8 / p + 0.8 * p) * 0.55
        px = cx + (i / 100.0) * pw
        py = cy - val * 52.0
        pts_sq.append(f"{px:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_sq)}" fill="none" stroke="#9333ea" stroke-width="2.2" stroke-dasharray="3,3"/>')
    frags.append(text(cx + pw/2 + 70, cy - 90, "Подолання SQL зі стисненим світлом (Squeezed Light)", size=12, bold=True, color="#7e22ce"))

    render(os.path.join(OUT_DIR, "sql-backaction-tradeoff.svg"), w, h, *frags)

# 3. Quantum Amplifier Noise in Phase Space
def gen_quantum_amplifier_noise():
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 25, "Шумові еліпси у квантовому фазовому просторі (квадратури X_1 та X_2)", size=16, bold=True))

    # Panel 1: Vacuum State
    p1_x, p1_y, p1_w, p1_h = 30, 55, 230, 300
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Вакуумний стан |0⟩", size=14, bold=True))
    
    c1_x, c1_y = p1_x + p1_w/2, p1_y + 160
    frags.append(arrow(c1_x - 80, c1_y, c1_x + 80, c1_y, color="#94a3b8", sw=1.2))
    frags.append(arrow(c1_x, c1_y + 80, c1_x, c1_y - 80, color="#94a3b8", sw=1.2))
    frags.append(text(c1_x + 85, c1_y + 4, "X_1", size=11, bold=True, anchor="start"))
    frags.append(text(c1_x + 10, c1_y - 85, "X_2", size=11, bold=True, anchor="start"))

    frags.append(circle(c1_x, c1_y, 40, fill="#e0f2fe", stroke="#0284c7", sw=1.8))
    frags.append(circle(c1_x, c1_y, 3, fill="#0369a1", stroke="none"))
    frags.append(text(p1_x + p1_w/2, p1_y + p1_h - 20, "Симетричний круг: ΔX₁ = ΔX₂ = ½", size=11, color="#0369a1", bold=True))

    # Panel 2: Phase-Preserving Amplifier
    p2_x, p2_y, p2_w, p2_h = 295, 55, 230, 300
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Фазозберігаючий підсилювач", size=14, bold=True))
    
    c2_x, c2_y = p2_x + p2_w/2, p2_y + 160
    frags.append(arrow(c2_x - 80, c2_y, c2_x + 80, c2_y, color="#94a3b8", sw=1.2))
    frags.append(arrow(c2_x, c2_y + 80, c2_x, c2_y - 80, color="#94a3b8", sw=1.2))
    frags.append(text(c2_x + 85, c2_y + 4, "X_1", size=11, bold=True, anchor="start"))
    frags.append(text(c2_x + 10, c2_y - 85, "X_2", size=11, bold=True, anchor="start"))

    # Large circle (Amplified + Added Noise)
    frags.append(circle(c2_x + 25, c2_y - 25, 58, fill="#fee2e2", stroke="#dc2626", sw=1.8))
    frags.append(circle(c2_x + 25, c2_y - 25, 4, fill="#b91c1c", stroke="none"))
    frags.append(arrow(c2_x, c2_y, c2_x + 25, c2_y - 25, color="#b91c1c", sw=1.5))
    frags.append(text(p2_x + p2_w/2, p2_y + p2_h - 20, "Підсилений шум: N_added ≥ ½", size=11, color="#b91c1c", bold=True))

    # Panel 3: Phase-Sensitive / Squeezed Amplifier
    p3_x, p3_y, p3_w, p3_h = 560, 55, 230, 300
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p3_x + p3_w/2, p3_y + 25, "Фазочутливий (стиснений) стан", size=14, bold=True))
    
    c3_x, c3_y = p3_x + p3_w/2, p3_y + 160
    frags.append(arrow(c3_x - 80, c3_y, c3_x + 80, c3_y, color="#94a3b8", sw=1.2))
    frags.append(arrow(c3_x, c3_y + 80, c3_x, c3_y - 80, color="#94a3b8", sw=1.2))
    frags.append(text(c3_x + 85, c3_y + 4, "X_1", size=11, bold=True, anchor="start"))
    frags.append(text(c3_x + 10, c3_y - 85, "X_2", size=11, bold=True, anchor="start"))

    # Rotated/Squeezed Ellipse
    frags.append(ellipse(c3_x + 20, c3_y - 20, 65, 18, fill="#f3e8ff", stroke="#9333ea", sw=1.8))
    frags.append(circle(c3_x + 20, c3_y - 20, 3, fill="#7e22ce", stroke="none"))
    frags.append(text(p3_x + p3_w/2, p3_y + p3_h - 20, "ΔX₁ < ½ за рахунок ΔX₂ > ½", size=11, color="#7e22ce", bold=True))

    render(os.path.join(OUT_DIR, "quantum-amplifier-noise.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_thermal_quantum_crossover()
    gen_sql_backaction_tradeoff()
    gen_quantum_amplifier_noise()
    print("SVG generation complete.")
