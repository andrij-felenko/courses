# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Helper for ellipse primitive
def ellipse_tag(cx, cy, rx_val, ry_val, fill="none", stroke=LINE, sw=1.5, transform=None):
    tr = f' transform="{transform}"' if transform else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx_val:.1f}" ry="{ry_val:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{tr}/>'

def path_tag(d_str, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def polyline_tag(pts_str, fill="none", stroke=LINE, sw=1.5):
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Деформація оптичної індикатриси подіянням електричного поля
# ═══════════════════════════════════════════════════════════════════════════
def fig_pockels_indicatrix():
    W, H = 760, 420
    f = []

    # Left panel: Unperturbed Indicatrix (Circle cross-section)
    cx1, cy1 = 200, 210
    rx1, ry1 = 110, 110
    
    # Title left
    f.append(text(cx1, 62, '1. Без електричного поля (E = 0)', 14, INK, 'middle', bold=True))
    f.append(text(cx1, 80, 'Одноосний кристал (KDP), n_x = n_y = n_o', 12, MUTED, 'middle'))

    # Axes x, y
    f.append(line(cx1 - 135, cy1, cx1 + 135, cy1, color=MUTED, sw=1.2, dash='4,4'))
    f.append(line(cx1, cy1 - 135, cx1, cy1 + 135, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(cx1 + 143, cy1 + 4, 'x', 13, INK, 'start', bold=True, italic=True))
    f.append(text(cx1 - 4, cy1 - 142, 'y', 13, INK, 'end', bold=True, italic=True))

    # Circle (isocurve n_o)
    f.append(ellipse_tag(cx1, cy1, rx1, ry1, fill='none', stroke=POS, sw=2.5))
    f.append(text(cx1 + 60, cy1 - 70, 'n_o', 13, POS, 'start', bold=True))
    f.append(text(cx1 - 75, cy1 + 75, 'n_o', 13, POS, 'end', bold=True))

    # Divider line
    f.append(line(380, 55, 380, 385, color=MUTED, sw=1.2, dash='2,4'))

    # Right panel: Perturbed & Rotated Indicatrix (Ellipse at 45 degrees)
    cx2, cy2 = 570, 210
    rx2, ry2 = 135, 85 # Elongated ellipse
    
    # Title right
    f.append(text(cx2, 62, '2. Прикладено поле E_z ≠ 0', 14, INK, 'middle', bold=True))
    f.append(text(cx2, 80, 'Поворот головних осей на 45°, n_x\' ≠ n_y\'', 12, MUTED, 'middle'))

    # Original axes (dashed)
    f.append(line(cx2 - 135, cy2, cx2 + 135, cy2, color=MUTED, sw=1.0, dash='3,3'))
    f.append(line(cx2, cy2 - 135, cx2, cy2 + 135, color=MUTED, sw=1.0, dash='3,3'))
    f.append(text(cx2 + 143, cy2 + 4, 'x', 12, MUTED, 'start', italic=True))
    f.append(text(cx2 - 4, cy2 - 142, 'y', 12, MUTED, 'end', italic=True))

    # Rotated new principal axes x', y' (at 45 deg)
    ang = math.radians(45)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    
    # New x' axis (45 deg)
    x_p1, y_p1 = cx2 + 140 * cos_a, cy2 - 140 * sin_a
    x_p2, y_p2 = cx2 - 140 * cos_a, cy2 + 140 * sin_a
    f.append(line(x_p2, y_p2, x_p1, y_p1, color=NEG, sw=1.8))
    f.append(text(x_p1 + 8, y_p1 - 2, 'x\'', 14, NEG, 'start', bold=True, italic=True))

    # New y' axis (135 deg)
    y_p1_x, y_p1_y = cx2 - 140 * sin_a, cy2 - 140 * cos_a
    y_p2_x, y_p2_y = cx2 + 140 * sin_a, cy2 + 140 * cos_a
    f.append(line(y_p2_x, y_p2_y, y_p1_x, y_p1_y, color=FIELD, sw=1.8))
    f.append(text(y_p1_x - 12, y_p1_y - 6, 'y\'', 14, FIELD, 'end', bold=True, italic=True))

    # Angle arc (45 deg)
    f.append(path_tag(f'M {cx2 + 40} {cy2} A 40 40 0 0 0 {cx2 + 40 * cos_a:.1f} {cy2 - 40 * sin_a:.1f}', fill='none', stroke=INK, sw=1.2))
    f.append(text(cx2 + 48, cy2 - 14, '45°', 12, INK, 'start', bold=True))

    # Ellipse rotated by 45 deg
    f.append(ellipse_tag(cx2, cy2, rx2, ry2, fill='none', stroke=POS, sw=2.5, transform=f'rotate(-45 {cx2} {cy2})'))

    # Axis lengths annotations
    # n_x' along x'
    f.append(text(cx2 + 85 * cos_a + 12, cy2 - 85 * sin_a - 12, 'n_x\' = n_o + Δn', 12, NEG, 'start', bold=True))
    # n_y' along y'
    f.append(text(cx2 - 55 * sin_a - 20, cy2 - 55 * cos_a + 18, 'n_y\' = n_o - Δn', 12, FIELD, 'end', bold=True))

    # Bottom summary box
    f.append(rect(40, 360, 680, 42, fill=BG, stroke=MUTED, sw=1, rx=6))
    f.append(text(380, 386, 'Індуковане двозаломлення: Δn = n_x\' - n_y\' = n_o³ · r_63 · E_z', 13, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'pockels-indicatrix.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Конфігурації комірки Поккельса: поздовжня та поперечна
# ═══════════════════════════════════════════════════════════════════════════
def fig_longitudinal_vs_transverse():
    W, H = 760, 430
    f = []

    # Left: Longitudinal Geometry
    f.append(text(200, 65, 'Поздовжня геометрія (Longitudinal)', 14, INK, 'middle', bold=True))
    f.append(text(200, 84, 'Кристал KDP / DKDP, напрямок світла k ∥ E_z', 12, MUTED, 'middle'))

    # Crystal 1
    lx, ly, lw, lh = 120, 130, 160, 140
    f.append(rect(lx, ly, lw, lh, fill="#e8f8f0", stroke=INK, sw=2, rx=4))
    f.append(text(lx + lw/2, ly + lh/2 - 10, 'Кристал KDP', 13, INK, 'middle', bold=True))
    f.append(text(lx + lw/2, ly + lh/2 + 10, 'Довжина L', 12, MUTED, 'middle'))

    # Ring Electrodes on entrance & exit faces (drawn slightly detached or side-by-side)
    f.append(rect(lx - 12, ly, 10, lh, fill=NEG, stroke=INK, sw=1.5, rx=2))
    f.append(rect(lx + lw + 2, ly, 10, lh, fill=POS, stroke=INK, sw=1.5, rx=2))
    f.append(text(lx - 25, ly - 12, 'Електрод (-)', 11, NEG, 'middle', bold=True))
    f.append(text(lx + lw + 25, ly - 12, 'Електрод (+)', 11, POS, 'middle', bold=True))

    # Light ray
    f.append(arrow(30, ly + lh/2, lx - 14, ly + lh/2, color=POS, sw=3))
    f.append(arrow(lx, ly + lh/2, lx + lw, ly + lh/2, color=POS, sw=3))
    f.append(arrow(lx + lw + 14, ly + lh/2, 370, ly + lh/2, color=POS, sw=3))
    f.append(text(60, ly + lh/2 - 12, 'Світло k', 12, POS, 'middle', bold=True, italic=True))

    # Electric field vectors inside
    for y_offset in [ly + 35, ly + lh - 35]:
        f.append(arrow(lx + 20, y_offset, lx + lw - 20, y_offset, color=NEG, sw=1.5))
    f.append(text(lx + lw/2, ly + lh - 20, 'Поле E_z ∥ k', 12, NEG, 'middle', bold=True))

    # Formula box left
    f.append(rect(50, 310, 300, 95, fill=BG, stroke=MUTED, sw=1, rx=6))
    f.append(text(200, 332, 'V_π не залежить від довжини L!', 12, INK, 'middle', bold=True))
    f.append(text(200, 357, 'Γ = (2π / λ) · n_o³ · r_63 · V', 13, NEG, 'middle', bold=True))
    f.append(text(200, 385, 'V_π = λ / (2 · n_o³ · r_63)  ≈ 3..7 кВ', 13, POS, 'middle', bold=True))

    # Vertical separator
    f.append(line(390, 55, 390, 410, color=MUTED, sw=1.2, dash='2,4'))

    # Right: Transverse Geometry
    f.append(text(570, 65, 'Поперечна геометрія (Transverse)', 14, INK, 'middle', bold=True))
    f.append(text(570, 84, 'Кристал LiNbO3 / BBO, напрямок світла k ⊥ E_z', 12, MUTED, 'middle'))

    # Crystal 2
    rx, ry, rw, rh = 470, 130, 200, 140
    f.append(rect(rx, ry, rw, rh, fill="#e8f8f0", stroke=INK, sw=2, rx=4))
    f.append(text(rx + rw/2, ry + rh/2 - 10, 'Кристал LiNbO3', 13, INK, 'middle', bold=True))
    f.append(text(rx + rw/2, ry + rh/2 + 10, 'Довжина L, товщина d', 12, MUTED, 'middle'))

    # Top & Bottom Electrodes
    f.append(rect(rx, ry - 12, rw, 10, fill=POS, stroke=INK, sw=1.5, rx=2))
    f.append(rect(rx, ry + rh + 2, rw, 10, fill=NEG, stroke=INK, sw=1.5, rx=2))
    f.append(text(rx + rw/2, ry - 18, 'Верхній електрод (+V)', 11, POS, 'middle', bold=True))
    f.append(text(rx + rw/2, ry + rh + 22, 'Нижній електрод (0V)', 11, NEG, 'middle', bold=True))

    # Dimension d annotation
    f.append(line(rx - 25, ry, rx - 25, ry + rh, color=INK, sw=1.2))
    f.append(line(rx - 30, ry, rx - 20, ry, color=INK, sw=1.2))
    f.append(line(rx - 30, ry + rh, rx - 20, ry + rh, color=INK, sw=1.2))
    f.append(text(rx - 35, ry + rh/2 + 4, 'd', 13, INK, 'end', bold=True, italic=True))

    # Light ray
    f.append(arrow(410, ry + rh/2, rx - 10, ry + rh/2, color=POS, sw=3))
    f.append(arrow(rx, ry + rh/2, rx + rw, ry + rh/2, color=POS, sw=3))
    f.append(arrow(rx + rw + 10, ry + rh/2, 740, ry + rh/2, color=POS, sw=3))

    # Electric field arrows (top to bottom, offset from center text)
    for x_offset in [rx + 35, rx + rw - 35]:
        f.append(arrow(x_offset, ry + 15, x_offset, ry + rh - 15, color=NEG, sw=1.5))
    f.append(text(rx + rw - 35, ry + rh/2 + 4, 'E_z ⊥ k', 12, NEG, 'start', bold=True))

    # Formula box right
    f.append(rect(420, 310, 300, 95, fill=BG, stroke=MUTED, sw=1, rx=6))
    f.append(text(570, 332, 'V_π зменшується фактор L / d!', 12, INK, 'middle', bold=True))
    f.append(text(570, 357, 'Γ = (2π / λ) · n_e³ · r_33 · V · (L / d)', 13, NEG, 'middle', bold=True))
    f.append(text(570, 385, 'V_π = (λ / (2 · n_e³ · r_33)) · (d / L)  ≈ 50..300 В', 13, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'longitudinal-vs-transverse.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Оптичний амплітудний модулятор на комірці Поккельса
# ═══════════════════════════════════════════════════════════════════════════
def fig_pockels_cell_setup():
    W, H = 760, 420
    f = []

    # Top Optical Train Diagram
    y_opt = 130
    
    # Unpolarized Input Beam
    f.append(arrow(35, y_opt, 80, y_opt, color=POS, sw=3))
    f.append(text(58, y_opt - 18, 'Вхідне світло I_0', 12, INK, 'middle', bold=True))

    # Polarizer P1 (at 45 deg)
    f.append(rect(80, y_opt - 40, 20, 80, fill="#f1f5f9", stroke=INK, sw=1.5, rx=3))
    f.append(line(83, y_opt + 30, 97, y_opt - 30, color=INK, sw=2)) # 45 deg line indicator
    f.append(text(90, y_opt + 55, 'Поляризатор P1 (45°)', 11, INK, 'middle', bold=True))

    # Beam 1
    f.append(arrow(100, y_opt, 180, y_opt, color=POS, sw=2.5))

    # Pockels Cell Crystal
    f.append(rect(180, y_opt - 35, 120, 70, fill="#e8f8f0", stroke=INK, sw=2, rx=4))
    # Electrodes
    f.append(rect(180, y_opt - 43, 120, 8, fill=NEG, stroke=INK, sw=1))
    f.append(rect(180, y_opt + 35, 120, 8, fill=POS, stroke=INK, sw=1))
    f.append(text(240, y_opt - 14, 'Комірка Поккельса', 12, INK, 'middle', bold=True))
    f.append(text(240, y_opt + 18, 'Напруга V(t)', 11, NEG, 'middle', bold=True))

    # Beam 2 (Elliptically polarized)
    f.append(arrow(300, y_opt, 390, y_opt, color=POS, sw=2.5))
    f.append(text(345, y_opt - 22, 'Фазовий набіг Γ(V)', 11, MUTED, 'middle'))

    # Analyzer P2 (at -45 deg / 90 deg relative to P1)
    f.append(rect(390, y_opt - 40, 20, 80, fill="#f1f5f9", stroke=INK, sw=1.5, rx=3))
    f.append(line(393, y_opt - 30, 407, y_opt + 30, color=INK, sw=2)) # -45 deg line indicator
    f.append(text(400, y_opt + 55, 'Аналізатор P2 (-45°)', 11, INK, 'middle', bold=True))

    # Modulated Output Beam
    f.append(arrow(410, y_opt, 480, y_opt, color=POS, sw=3))
    f.append(text(445, y_opt - 22, 'Модульоване I(V)', 12, POS, 'middle', bold=True))

    # Transmission Characteristic Curve (Sin^2) on the right
    cx_plot, cy_plot = 610, 230
    w_plot, h_plot = 220, 160

    # Axes
    f.append(line(cx_plot - 80, cy_plot + 60, cx_plot + 110, cy_plot + 60, color=INK, sw=1.5))
    f.append(line(cx_plot - 80, cy_plot + 60, cx_plot - 80, cy_plot - 65, color=INK, sw=1.5))
    f.append(text(cx_plot + 115, cy_plot + 64, 'V', 13, INK, 'start', bold=True, italic=True))
    f.append(text(cx_plot - 80, cy_plot - 75, 'I / I_0', 12, INK, 'middle', bold=True, italic=True))

    # Sin^2 curve points
    pts = []
    for px in range(-70, 105, 3):
        # Map px to voltage V/V_pi: range 0 to 2 V_pi
        v_ratio = (px + 70) / 80.0 # 0 to 2.18
        intensity = math.sin(math.pi * v_ratio / 2.0)**2
        py = cy_plot + 60 - intensity * 120
        pts.append(f"{cx_plot + px:.1f},{py:.1f}")
    
    f.append(polyline_tag(' '.join(pts), fill="none", stroke=POS, sw=2.5))

    # Key Voltage Points on X axis
    # V = 0
    f.append(line(cx_plot - 70, cy_plot + 56, cx_plot - 70, cy_plot + 64, color=INK, sw=1.2))
    f.append(text(cx_plot - 70, cy_plot + 78, '0', 11, INK, 'middle'))

    # V = V_pi / 2 (Quarter wave bias)
    v_bias_x = cx_plot - 30
    f.append(line(v_bias_x, cy_plot + 56, v_bias_x, cy_plot + 64, color=INK, sw=1.2))
    f.append(line(v_bias_x, cy_plot + 60, v_bias_x, cy_plot - 0, color=NEG, sw=1, dash='3,3'))
    f.append(text(v_bias_x, cy_plot + 78, 'V_π/2', 11, NEG, 'middle', bold=True))
    f.append(circle(v_bias_x, cy_plot, 4, fill=NEG, stroke='none'))
    f.append(text(v_bias_x + 8, cy_plot - 8, 'Робоча точка (Bias)', 10, NEG, 'start', bold=True))

    # V = V_pi (Half wave voltage)
    v_pi_x = cx_plot + 10
    f.append(line(v_pi_x, cy_plot + 56, v_pi_x, cy_plot + 64, color=INK, sw=1.2))
    f.append(line(v_pi_x, cy_plot + 60, v_pi_x, cy_plot - 60, color=POS, sw=1, dash='3,3'))
    f.append(text(v_pi_x, cy_plot + 78, 'V_π', 11, POS, 'middle', bold=True))
    f.append(text(v_pi_x + 18, cy_plot - 68, '100% I_0', 10, POS, 'start', bold=True))

    # Formula Callout at Bottom
    f.append(rect(40, 340, 440, 65, fill=BG, stroke=MUTED, sw=1, rx=6))
    f.append(text(260, 362, 'Функція пропускання:  I(V) = I_0 · sin²( π · V / 2V_π )', 13, INK, 'middle', bold=True))
    f.append(text(260, 388, 'При робочій точці V_bias = V_π/2 відклик є максимально лінійним', 12, MUTED, 'middle'))

    render(os.path.join(IMG, 'pockels-cell-setup.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Інтегральний електрооптичний модулятор Маха — Цендера
# ═══════════════════════════════════════════════════════════════════════════
def fig_eom_mach_zehnder():
    W, H = 760, 420
    f = []

    # Substrate LiNbO3
    sx, sy, sw, sh = 50, 65, 660, 260
    f.append(rect(sx, sy, sw, sh, fill="#f0fdf4", stroke=INK, sw=1.5, rx=8))
    f.append(text(sx + 80, sy + 25, 'Подкладка ніобату літію (LiNbO3)', 12, INK, 'start', bold=True))

    # Optical Waveguide Paths (Y-splitter -> 2 arms -> Y-combiner)
    y_center = sy + sh/2
    arm_sep = 50
    
    # Input waveguide
    f.append(line(sx + 20, y_center, sx + 130, y_center, color=POS, sw=4))
    f.append(arrow(sx - 15, y_center, sx + 20, y_center, color=POS, sw=3))
    f.append(text(sx + 20, y_center - 15, 'Вхідне світло E_in', 11, POS, 'middle', bold=True))

    # Y-splitter 1
    f.append(line(sx + 130, y_center, sx + 200, y_center - arm_sep, color=POS, sw=3))
    f.append(line(sx + 130, y_center, sx + 200, y_center + arm_sep, color=POS, sw=3))

    # Arm 1 (Top) & Arm 2 (Bottom)
    f.append(line(sx + 200, y_center - arm_sep, sx + 460, y_center - arm_sep, color=POS, sw=3))
    f.append(line(sx + 200, y_center + arm_sep, sx + 460, y_center + arm_sep, color=POS, sw=3))
    f.append(text(sx + 330, y_center - arm_sep - 12, 'Оптичне плече 1 (Фаза +Δφ)', 11, INK, 'middle', bold=True))
    f.append(text(sx + 330, y_center + arm_sep + 20, 'Оптичне плече 2 (Фаза -Δφ)', 11, INK, 'middle', bold=True))

    # Y-combiner 2
    f.append(line(sx + 460, y_center - arm_sep, sx + 530, y_center, color=POS, sw=3))
    f.append(line(sx + 460, y_center + arm_sep, sx + 530, y_center, color=POS, sw=3))

    # Output waveguide
    f.append(line(sx + 530, y_center, sx + 640, y_center, color=POS, sw=4))
    f.append(arrow(sx + 640, y_center, sx + 675, y_center, color=POS, sw=3))
    f.append(text(sx + 620, y_center - 15, 'Вихід E_out(t)', 11, POS, 'middle', bold=True))

    # Push-Pull Coplanar Waveguide Electrodes (CPW)
    # Ground Electrode 1 (above Arm 1)
    f.append(rect(sx + 210, y_center - arm_sep - 35, 230, 16, fill=MUTED, stroke=INK, sw=1.2, rx=3))
    f.append(text(sx + 325, y_center - arm_sep - 27, 'Земля (GND)', 10, INK, 'middle', bold=True))

    # Signal RF Electrode (Between Arm 1 and Arm 2)
    f.append(rect(sx + 210, y_center - 12, 230, 24, fill=NEG, stroke=INK, sw=1.2, rx=3))
    f.append(text(sx + 325, y_center + 4, 'ВЧ-сигнал RF (+V(t)) [Push-Pull]', 11, NEG, 'middle', bold=True))

    # Ground Electrode 2 (below Arm 2)
    f.append(rect(sx + 210, y_center + arm_sep + 25, 230, 16, fill=MUTED, stroke=INK, sw=1.2, rx=3))
    f.append(text(sx + 325, y_center + arm_sep + 37, 'Земля (GND)', 10, INK, 'middle', bold=True))

    # Bottom summary box
    f.append(rect(60, 345, 640, 55, fill=BG, stroke=MUTED, sw=1, rx=6))
    f.append(text(380, 366, 'Конфігурація Push-Pull подвоює фазову різницю 2·Δφ та зменшує V_π у 2 рази', 12, INK, 'middle', bold=True))
    f.append(text(380, 388, 'Інтерференція плечей: I_out = I_in · cos²( Δφ(V) )  — швидкодія понад 100 ГГц', 12, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'eom-mach-zehnder.svg'), W, H, *f)


if __name__ == '__main__':
    fig_pockels_indicatrix()
    fig_longitudinal_vs_transverse()
    fig_pockels_cell_setup()
    fig_eom_mach_zehnder()
    print("All figures generated successfully.")
