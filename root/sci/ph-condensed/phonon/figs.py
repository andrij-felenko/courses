# -*- coding: utf-8 -*-
import sys
import os
import math

# Add path to scripts/ in repository root (4 levels up from book/physics/condensed-matter-physics/phonon)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

# 1. Dispersion acoustic & optical branches
def gen_dispersion(filepath):
    w, h = 820, 440
    frags = []
    
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="none"))
    frags.append(text(w / 2, 28, "Дисперсійна крива ω(k) для двоатомного одновимірного кристала", size=16, bold=True))

    # Plot area
    ox, oy = 110, 360
    pw, ph = 640, 290
    
    # Axes
    frags.append(arrow(ox - 30, oy, ox + pw + 30, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox + pw / 2, oy + 20, ox + pw / 2, oy - ph - 15, color=LINE, sw=1.8))
    
    frags.append(text(ox + pw + 40, oy + 5, "k", size=15, bold=True, italic=True))
    frags.append(text(ox + pw / 2 - 25, oy - ph - 20, "ω", size=15, bold=True, italic=True))
    
    # Brillouin zone boundaries
    x_min = ox
    x_mid = ox + pw / 2
    x_max = ox + pw
    
    frags.append(line(x_min, oy - ph - 10, x_min, oy + 10, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(x_max, oy - ph - 10, x_max, oy + 10, color=MUTED, sw=1.2, dash="4,4"))
    
    frags.append(text(x_min, oy + 25, "-π/a", size=13, color=INK, bold=True))
    frags.append(text(x_mid, oy + 25, "0", size=13, color=INK, bold=True))
    frags.append(text(x_max, oy + 25, "+π/a", size=13, color=INK, bold=True))
    
    scale_y = ph / 1.85
    
    def get_w_ac(ka):
        m1, m2 = 3.0, 1.0
        term1 = 1.0/m1 + 1.0/m2
        term2 = (4.0 * (math.sin(ka/2.0)**2)) / (m1 * m2)
        w2 = term1 - math.sqrt(max(0.0, term1**2 - term2))
        return math.sqrt(max(0.0, w2))
        
    def get_w_opt(ka):
        m1, m2 = 3.0, 1.0
        term1 = 1.0/m1 + 1.0/m2
        term2 = (4.0 * (math.sin(ka/2.0)**2)) / (m1 * m2)
        w2 = term1 + math.sqrt(max(0.0, term1**2 - term2))
        return math.sqrt(max(0.0, w2))

    # Shaded band gap
    y_gap_bottom = oy - get_w_ac(math.pi) * scale_y
    y_gap_top = oy - get_w_opt(math.pi) * scale_y
    frags.append(rect(x_min, y_gap_top, pw, y_gap_bottom - y_gap_top, fill="#fee2e2", stroke="none", rx=0))
    
    # Band gap label using textbox
    tb_gap, _, _ = textbox(x_mid, (y_gap_top + y_gap_bottom)/2, "Заборонена смуга частот (Band Gap)", size=12, fill="#fef2f2", stroke="#ef4444", color="#991b1b")
    frags.append(tb_gap)

    # Plot acoustic curve
    pts_ac = []
    steps = 100
    for i in range(steps + 1):
        ka = -math.pi + (2.0 * math.pi * i / steps)
        px = ox + (i / steps) * pw
        py = oy - get_w_ac(ka) * scale_y
        pts_ac.append((px, py))
        
    path_ac = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_ac)
    frags.append(path(path_ac, stroke=NEG, sw=3.0))

    # Plot optical curve
    pts_opt = []
    for i in range(steps + 1):
        ka = -math.pi + (2.0 * math.pi * i / steps)
        px = ox + (i / steps) * pw
        py = oy - get_w_opt(ka) * scale_y
        pts_opt.append((px, py))
        
    path_opt = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_opt)
    frags.append(path(path_opt, stroke=POS, sw=3.0))

    # Sound velocity tangent at k=0
    dx_tan = 90
    vs_slope = (get_w_ac(0.5) * scale_y) / (0.5 * (pw / (2*math.pi)))
    frags.append(line(x_mid - dx_tan, oy - vs_slope * 0.45, x_mid + dx_tan, oy - vs_slope * 1.35, color="#16a34a", sw=1.8, dash="5,4"))
    
    tb_vs, _, _ = textbox(x_mid + 110, oy - 45, "v_s = dω/dk (швидкість звуку)", size=11, fill="#f0fdf4", stroke="#16a34a", color="#14532d")
    frags.append(tb_vs)

    # Labels for branches
    tb_opt_lbl, _, _ = textbox(x_mid - 160, oy - get_w_opt(0)*scale_y + 5, "Оптична гілка (протифазні коливання)", size=12, fill="#eff6ff", stroke=POS, color="#991b1b")
    frags.append(tb_opt_lbl)

    tb_ac_lbl, _, _ = textbox(x_mid - 170, oy - 70, "Акустична гілка (синфазні коливання)", size=12, fill="#eff6ff", stroke=NEG, color="#1e3a8a")
    frags.append(tb_ac_lbl)

    # Frequency tick marks on Y axis
    frags.append(line(ox - 5, oy - get_w_opt(0)*scale_y, ox + 5, oy - get_w_opt(0)*scale_y, color=LINE, sw=1.5))
    frags.append(text(ox - 45, oy - get_w_opt(0)*scale_y + 4, "ω_O(0)", size=11, color=INK, bold=True))

    frags.append(line(ox - 5, y_gap_top, ox + 5, y_gap_top, color=LINE, sw=1.5))
    frags.append(text(ox - 45, y_gap_top + 4, "√(2C/M₂)", size=11, color=INK))

    frags.append(line(ox - 5, y_gap_bottom, ox + 5, y_gap_bottom, color=LINE, sw=1.5))
    frags.append(text(ox - 45, y_gap_bottom + 4, "√(2C/M₁)", size=11, color=INK))

    return render(filepath, w, h, *frags)

# 2. Normal vs Umklapp scattering processes
def gen_normal_vs_umklapp(filepath):
    w, h = 840, 410
    frags = []
    
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="none"))
    frags.append(text(w / 2, 26, "Фонон-фононне розсіювання: N-процеси та U-процеси (Umklapp)", size=16, bold=True))

    # Panel 1: Normal process (N-process)
    p1_x, p1_y, p1_w, p1_h = 20, 55, 385, 335
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(p1_x + p1_w/2, p1_y + 24, "Нормальний процес (N-процес)", size=14, bold=True, color="#1e293b"))
    
    # 1st BZ square in Panel 1
    bz1_cx, bz1_cy = p1_x + 190, p1_y + 175
    bz1_size = 140
    frags.append(rect(bz1_cx - bz1_size/2, bz1_cy - bz1_size/2, bz1_size, bz1_size, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=0))
    frags.append(text(bz1_cx, bz1_cy - bz1_size/2 - 10, "Перша зона Бріллюена", size=11, color=MUTED, bold=True))

    # Vectors inside BZ1
    k1_end = (bz1_cx + 45, bz1_cy - 40)
    frags.append(arrow(bz1_cx, bz1_cy, k1_end[0], k1_end[1], color=NEG, sw=2.2))
    frags.append(text(bz1_cx + 15, bz1_cy - 25, "k₁", size=13, color=NEG, bold=True, italic=True))

    k3_end = (bz1_cx + 60, bz1_cy + 25)
    frags.append(arrow(k1_end[0], k1_end[1], k3_end[0], k3_end[1], color=FIELD, sw=2.2))
    frags.append(text(k1_end[0] + 15, k1_end[1] + 30, "k₂", size=13, color=FIELD, bold=True, italic=True))

    frags.append(arrow(bz1_cx, bz1_cy, k3_end[0], k3_end[1], color=POS, sw=2.5))
    frags.append(text(bz1_cx + 35, bz1_cy + 25, "k₃ = k₁ + k₂", size=13, color=POS, bold=True, italic=True))

    tb_n, _, _ = textbox(p1_x + p1_w/2, p1_y + p1_h - 35, "k₁ + k₂ = k₃\nСумарний квазіімпульс зберігається.\nНіма опірність: тепловий потік не гальмується.", size=11, fill="#f0fdf4", stroke="#16a34a", color="#14532d")
    frags.append(tb_n)

    # Panel 2: Umklapp process (U-process)
    p2_x, p2_y, p2_w, p2_h = 430, 55, 390, 335
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(p2_x + p2_w/2, p2_y + 24, "Процес перекидання (U-процес / Umklapp)", size=14, bold=True, color="#991b1b"))

    bz2_cx1, bz2_cy = p2_x + 120, p2_y + 175
    bz2_size = 130
    bz2_cx2 = bz2_cx1 + bz2_size
    
    frags.append(rect(bz2_cx1 - bz2_size/2, bz2_cy - bz2_size/2, bz2_size, bz2_size, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=0))
    frags.append(rect(bz2_cx2 - bz2_size/2, bz2_cy - bz2_size/2, bz2_size, bz2_size, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=0))
    
    frags.append(text(bz2_cx1, bz2_cy - bz2_size/2 - 10, "1-ша зона Бріллюена", size=11, color=MUTED, bold=True))
    frags.append(text(bz2_cx2, bz2_cy - bz2_size/2 - 10, "2-га зона", size=11, color=MUTED, italic=True))

    u_k1_end = (bz2_cx1 + 55, bz2_cy - 45)
    frags.append(arrow(bz2_cx1, bz2_cy, u_k1_end[0], u_k1_end[1], color=NEG, sw=2.2))
    frags.append(text(bz2_cx1 + 20, bz2_cy - 25, "k₁", size=13, color=NEG, bold=True, italic=True))

    u_sum_end = (bz2_cx1 + 140, bz2_cy - 15)
    frags.append(arrow(u_k1_end[0], u_k1_end[1], u_sum_end[0], u_sum_end[1], color=FIELD, sw=2.2))
    frags.append(text(u_k1_end[0] + 40, u_k1_end[1] - 10, "k₂", size=13, color=FIELD, bold=True, italic=True))

    frags.append(arrow(u_sum_end[0], u_sum_end[1], u_sum_end[0] - bz2_size, u_sum_end[1], color="#7c3aed", sw=2.2))
    frags.append(text(u_sum_end[0] - bz2_size/2, u_sum_end[1] - 12, "G", size=14, color="#7c3aed", bold=True, italic=True))

    u_k3_end = (u_sum_end[0] - bz2_size, u_sum_end[1])
    frags.append(arrow(bz2_cx1, bz2_cy, u_k3_end[0], u_k3_end[1], color=POS, sw=2.5))
    frags.append(text(bz2_cx1 - 35, bz2_cy + 10, "k₃'", size=13, color=POS, bold=True, italic=True))

    tb_u, _, _ = textbox(p2_x + p2_w/2, p2_y + p2_h - 35, "k₁ + k₂ = k₃' + G\nРезультуючий квазіімпульс повертається назад!\nСтворює тепловий опір у чистому кристалі.", size=11, fill="#fef2f2", stroke="#ef4444", color="#991b1b")
    frags.append(tb_u)

    return render(filepath, w, h, *frags)

# 3. Debye vs Einstein DOS
def gen_debye_vs_einstein_dos(filepath):
    w, h = 800, 420
    frags = []
    
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="none"))
    frags.append(text(w / 2, 28, "Густина фононних станів D(ω): модель Дебая та реальний 3D спектр", size=16, bold=True))

    ox, oy = 100, 350
    pw, ph = 640, 270

    # Axes
    frags.append(arrow(ox - 20, oy, ox + pw + 25, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy + 15, ox, oy - ph - 15, color=LINE, sw=1.8))
    
    frags.append(text(ox + pw + 35, oy + 5, "ω", size=15, bold=True, italic=True))
    frags.append(text(ox - 35, oy - ph - 15, "D(ω)", size=15, bold=True, italic=True))

    wD_x = ox + pw * 0.70
    frags.append(line(wD_x, oy - ph + 20, wD_x, oy + 10, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(text(wD_x, oy + 25, "ω_D (частота Дебая)", size=12, color=INK, bold=True))

    scale_x = wD_x - ox
    scale_y = ph * 0.75
    
    pts_debye = []
    steps = 60
    for i in range(steps + 1):
        frac = i / steps
        px = ox + frac * scale_x
        py = oy - (frac**2) * scale_y
        pts_debye.append((px, py))
    
    path_debye = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_debye) + f" L {wD_x:.1f},{oy:.1f}"
    frags.append(path(path_debye, fill="#eff6ff", stroke=NEG, sw=2.5))

    pts_real = [
        (ox, oy),
        (ox + scale_x * 0.2, oy - scale_y * 0.12),
        (ox + scale_x * 0.35, oy - scale_y * 0.65),
        (ox + scale_x * 0.42, oy - scale_y * 0.35),
        (ox + scale_x * 0.58, oy - scale_y * 0.85),
        (ox + scale_x * 0.75, oy - scale_y * 0.40),
        (ox + scale_x * 0.90, oy - scale_y * 1.05),
        (ox + scale_x * 1.02, oy - scale_y * 0.10),
        (ox + scale_x * 1.05, oy)
    ]
    path_real = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_real)
    frags.append(path(path_real, stroke=FIELD, sw=2.8))

    wE_x = ox + scale_x * 0.85
    frags.append(arrow(wE_x, oy, wE_x, oy - ph * 0.9, color=POS, sw=3.0))
    frags.append(circle(wE_x, oy - ph * 0.9, 5, fill=POS, stroke="#991b1b", sw=1.0))
    
    tb_ein, _, _ = textbox(wE_x + 65, oy - ph * 0.85, "Модель Ейнштейна:\nδ-пік при ω = ω_E", size=11, fill="#fef2f2", stroke=POS, color="#991b1b")
    frags.append(tb_ein)

    tb_deb, _, _ = textbox(ox + scale_x * 0.4, oy - scale_y * 0.15, "Модель Дебая: D(ω) ∝ ω²", size=12, fill="#eff6ff", stroke=NEG, color="#1e3a8a")
    frags.append(tb_deb)

    tb_vh, _, _ = textbox(ox + scale_x * 0.65, oy - scale_y * 0.95, "Реальний спектр з сингулярностями\nВан Хова (dω/dk = 0)", size=11, fill="#f0fdf4", stroke=FIELD, color="#14532d")
    frags.append(tb_vh)

    return render(filepath, w, h, *frags)

# 4. Thermal conductivity curve kappa(T)
def gen_thermal_conductivity(filepath):
    w, h = 820, 430
    frags = []
    
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="none"))
    frags.append(text(w / 2, 28, "Температурна залежність решіткової теплопровідності κ(T)", size=16, bold=True))

    ox, oy = 100, 360
    pw, ph = 660, 280

    # Axes
    frags.append(arrow(ox - 20, oy, ox + pw + 25, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy + 15, ox, oy - ph - 15, color=LINE, sw=1.8))
    
    frags.append(text(ox + pw + 35, oy + 5, "T", size=15, bold=True, italic=True))
    frags.append(text(ox - 35, oy - ph - 15, "κ(T)", size=15, bold=True, italic=True))

    peak_x = ox + pw * 0.22
    peak_y = oy - ph * 0.88
    
    pts_kappa = [
        (ox, oy),
        (ox + pw * 0.08, oy - ph * 0.25),
        (ox + pw * 0.15, oy - ph * 0.70),
        (peak_x, peak_y),
        (ox + pw * 0.32, oy - ph * 0.55),
        (ox + pw * 0.48, oy - ph * 0.30),
        (ox + pw * 0.70, oy - ph * 0.18),
        (ox + pw * 0.95, oy - ph * 0.10)
    ]
    
    path_kappa = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_kappa)
    frags.append(path(path_kappa, stroke=NEG, sw=3.0))

    frags.append(line(peak_x, peak_y, peak_x, oy + 10, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(text(peak_x, oy + 25, "T_peak ≈ 0.05 Θ_D", size=11, color=INK, bold=True))

    td_x = ox + pw * 0.60
    frags.append(line(td_x, oy - ph * 0.23, td_x, oy + 10, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(text(td_x, oy + 25, "Θ_D", size=12, color=INK, bold=True))

    tb_reg1, _, _ = textbox(ox + pw * 0.08, oy - ph * 0.62, "1. Межеве розсіювання\nκ ∝ C_v ∝ T³\n(довжина пробігу ℓ ≈ L)", size=11, fill="#eff6ff", stroke=NEG, color="#1e3a8a")
    frags.append(tb_reg1)

    tb_reg2, _, _ = textbox(peak_x + 85, peak_y + 10, "2. Максимум κ_max\n(баланс між дефектами\nта U-процесами)", size=11, fill="#f0fdf4", stroke=FIELD, color="#14532d")
    frags.append(tb_reg2)

    tb_reg3, _, _ = textbox(ox + pw * 0.48, oy - ph * 0.50, "3. Експоненціальні U-процеси\nκ ∝ exp(Θ_D / b T)", size=11, fill="#fff7ed", stroke="#f97316", color="#9a3412")
    frags.append(tb_reg3)

    tb_reg4, _, _ = textbox(ox + pw * 0.80, oy - ph * 0.30, "4. Високі T (T >> Θ_D)\nκ ∝ 1/T\n(число фононів n ∝ T)", size=11, fill="#fef2f2", stroke=POS, color="#991b1b")
    frags.append(tb_reg4)

    return render(filepath, w, h, *frags)

def main():
    generators = {
        "fig1-dispersion-acoustic-optical.svg": gen_dispersion,
        "fig2-normal-vs-umklapp.svg": gen_normal_vs_umklapp,
        "fig3-debye-vs-einstein-dos.svg": gen_debye_vs_einstein_dos,
        "fig4-thermal-conductivity-curve.svg": gen_thermal_conductivity,
    }
    for filename, fn in generators.items():
        filepath = os.path.join(OUT_DIR, filename)
        fn(filepath)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
