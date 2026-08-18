# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Palette
CORE_BG = "#eaf2fb"
CLAD_BG = "#f4f6f8"
AIR_BG  = "#ffffff"
RAY_OK  = "#27ae60"
RAY_BAD = "#c0392b"
RAY_AX  = "#2457d6"
GUIDE   = "#888888"

# ═══════════════════════════════════════════════════════════════════════════
# Fig 1: fiber-geometry-and-tpi.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_fiber_geometry():
    W, H = 760, 420
    frags = []
    
    # Background panel
    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 28, "Геометрія введення світла та числова апертура (NA)", 16, INK, "middle", bold=True))

    # Fiber dimensions
    fx, fy = 220, 70
    fw, fh = 480, 280
    core_h = 130
    clad_h = (fh - core_h) / 2

    # Cladding top and bottom
    frags.append(rect(fx, fy, fw, clad_h, fill="#e8ecef", stroke=LINE, sw=1.2, rx=0))
    frags.append(rect(fx, fy + clad_h + core_h, fw, clad_h, fill="#e8ecef", stroke=LINE, sw=1.2, rx=0))
    
    # Core
    frags.append(rect(fx, fy + clad_h, fw, core_h, fill=CORE_BG, stroke=LINE, sw=1.5, rx=0))

    # Fiber axis (dash line)
    cy = fy + fh / 2
    frags.append(line(fx - 40, cy, fx + fw + 20, cy, color=MUTED, sw=1.2, dash="6,4"))
    frags.append(text(fx + fw + 25, cy + 4, "вісь волокна", 11, MUTED, "start", italic=True))

    # Core and Cladding labels
    frags.append(text(fx + fw - 70, fy + clad_h / 2 + 4, "Оболонка n₂", 12, MUTED, "middle", bold=True))
    frags.append(text(fx + fw - 70, fy + clad_h + core_h / 2 + 4, "Серцевина n₁ (n₁ > n₂)", 13, INK, "middle", bold=True))
    frags.append(text(fx + fw - 70, fy + clad_h + core_h + clad_h / 2 + 4, "Оболонка n₂", 12, MUTED, "middle", bold=True))

    # Normal at entrance face
    frags.append(line(fx, fy + 20, fx, fy + fh - 20, color=LINE, sw=2))

    # Acceptance cone ray (guided ray)
    theta_a_deg = 24.0
    t_a = math.radians(theta_a_deg)
    L_in = 150
    rx_in = fx - L_in * math.cos(t_a)
    ry_in = cy - L_in * math.sin(t_a)
    
    # Incident ray (green)
    frags.append(arrow(rx_in, ry_in, fx, cy, color=RAY_OK, sw=2.2))
    
    # Refracted angle inside core
    n0, n1, n2 = 1.0, 1.48, 1.45
    t1 = math.asin((n0 / n1) * math.sin(t_a))
    
    # First hit on core-cladding boundary
    hit1_x = fx + (core_h / 2) / math.tan(t1)
    hit1_y = fy + clad_h
    frags.append(arrow(fx, cy, hit1_x, hit1_y, color=RAY_OK, sw=2.2))

    # Second hit on bottom boundary
    hit2_x = hit1_x + core_h / math.tan(t1)
    hit2_y = fy + clad_h + core_h
    frags.append(arrow(hit1_x, hit1_y, hit2_x, hit2_y, color=RAY_OK, sw=2.2))
    
    # Third segment
    hit3_x = hit2_x + (core_h / 2) / math.tan(t1)
    hit3_y = cy
    frags.append(line(hit2_x, hit2_y, min(hit3_x, fx + fw - 100), hit3_y, color=RAY_OK, sw=2.2))

    # Normal at core-cladding boundary
    frags.append(line(hit1_x, hit1_y - 30, hit1_x, hit1_y + 40, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(hit1_x + 6, hit1_y - 18, "нормаль", 10, MUTED, "start"))

    # Angle labels
    frags.append(text(fx - 45, cy - 14, "θₐ", 13, RAY_OK, "middle", bold=True))
    frags.append(text(fx + 35, cy - 10, "θ₁", 12, INK, "middle", bold=True))
    frags.append(text(hit1_x - 22, hit1_y + 18, "90°−θ₁ ≥ θc", 11, RAY_OK, "end", bold=True))

    # Unbound / escaping ray (red)
    t_bad = math.radians(42.0)
    rx_bad_in = fx - L_in * math.cos(t_bad)
    ry_bad_in = cy - L_in * math.sin(t_bad)
    frags.append(arrow(rx_bad_in, ry_bad_in, fx, cy, color=RAY_BAD, sw=1.8))
    
    t1_bad = math.asin((n0 / n1) * math.sin(t_bad))
    hit_bad_x = fx + (core_h / 2) / math.tan(t1_bad)
    hit_bad_y = fy + clad_h
    frags.append(line(fx, cy, hit_bad_x, hit_bad_y, color=RAY_BAD, sw=1.8, dash="5,3"))
    
    # Escaping into cladding
    t2_bad = math.asin((n1 / n2) * math.sin(math.pi/2 - t1_bad))
    esc_x = hit_bad_x + 60 * math.cos(t2_bad)
    esc_y = hit_bad_y - 60 * math.sin(t2_bad)
    frags.append(arrow(hit_bad_x, hit_bad_y, esc_x, esc_y, color=RAY_BAD, sw=1.8))
    frags.append(text(esc_x + 8, esc_y - 4, "промінь витікає (θ > θₐ)", 11, RAY_BAD, "start"))

    # Acceptance cone representation (dashed arcs)
    frags.append(line(rx_in, cy + (cy - ry_in), fx, cy, color=MUTED, sw=1, dash="3,3"))

    # NA Formula Box at top left
    tb_text = "Числова апертура:\nNA = sin θₐ = √(n₁² − n₂²)"
    box_markup = fitbox(25, 60, 180, 65, tb_text, size=13, fill="#fdfefe", stroke=RAY_OK, sw=1.5, bold=True)
    frags.append(box_markup)

    # Medium markers
    frags.append(text(80, cy + 30, "Повітря n₀ = 1.0", 12, MUTED, "middle"))

    render(os.path.join(IMG, "fiber-geometry-and-tpi.svg"), W, H, *frags)

# ═══════════════════════════════════════════════════════════════════════════
# Fig 2: index-profiles-comparison.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_index_profiles():
    W, H = 760, 440
    frags = []
    
    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 26, "Порівняння профілів показника заломлення та модової дисперсії", 16, INK, "middle", bold=True))

    # Section 1: Step-Index (Left)
    # -------------------------------------------------------------
    x1_c, y1_c = 190, 80
    frags.append(text(x1_c, y1_c, "1. Ступінчастий профіль (Step-Index)", 14, INK, "middle", bold=True))
    
    # Profile chart
    px, py, pw, ph = 40, 105, 110, 140
    frags.append(rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1))
    frags.append(line(px + pw/2, py, px + pw/2, py + ph, color=MUTED, sw=1, dash="3,3"))
    # Step shape
    n1_w = 70
    frags.append(line(px + 10, py + 20, px + (pw - n1_w)/2, py + 20, color=NEG, sw=2))
    frags.append(line(px + (pw - n1_w)/2, py + 20, px + (pw - n1_w)/2, py + ph - 20, color=NEG, sw=2))
    frags.append(line(px + (pw - n1_w)/2, py + ph - 20, px + (pw + n1_w)/2, py + ph - 20, color=NEG, sw=2))
    frags.append(line(px + (pw + n1_w)/2, py + ph - 20, px + (pw + n1_w)/2, py + 20, color=NEG, sw=2))
    frags.append(line(px + (pw + n1_w)/2, py + 20, px + pw - 10, py + 20, color=NEG, sw=2))
    frags.append(text(px + pw/2, py + ph + 16, "n(r) - стрибок", 11, MUTED, "middle"))

    # Ray trajectories
    tx, ty, tw, th = 170, 105, 180, 140
    frags.append(rect(tx, ty, tw, th, fill=CORE_BG, stroke=LINE, sw=1.2))
    frags.append(line(tx, ty + th/2, tx + tw, ty + th/2, color=MUTED, sw=1, dash="4,4"))
    
    # Axial ray (straight blue)
    frags.append(line(tx, ty + th/2, tx + tw, ty + th/2, color=RAY_AX, sw=2))
    # Oblique ray (zigzag red)
    frags.append(line(tx, ty + th/2, tx + tw/3, ty + 15, color=RAY_BAD, sw=1.8))
    frags.append(line(tx + tw/3, ty + 15, tx + 2*tw/3, ty + th - 15, color=RAY_BAD, sw=1.8))
    frags.append(line(tx + 2*tw/3, ty + th - 15, tx + tw, ty + th/2, color=RAY_BAD, sw=1.8))

    # Pulse broadening graphic
    frags.append(text(x1_c, py + th + 35, "Вхідний вузький імпульс → Вихідний розмитий імпульс", 11, POS, "middle", bold=True))
    frags.append(text(x1_c, py + th + 52, "Сильна міжмодова дисперсія", 12, POS, "middle", bold=True))

    # Divider line
    frags.append(line(W/2, 60, W/2, H - 30, color=LINE, sw=1, dash="6,4"))

    # Section 2: Graded-Index (Right)
    # -------------------------------------------------------------
    x2_c = 570
    frags.append(text(x2_c, y1_c, "2. Градієнтний профіль (Graded-Index)", 14, INK, "middle", bold=True))

    # Parabolic Profile chart
    px2, py2 = 420, 105
    frags.append(rect(px2, py2, pw, ph, fill=FILL, stroke=LINE, sw=1))
    frags.append(line(px2 + pw/2, py2, px2 + pw/2, py2 + ph, color=MUTED, sw=1, dash="3,3"))
    
    # Parabola
    pts = []
    for i in range(21):
        t = i / 20.0
        r_val = (t - 0.5) * 2.0
        n_val = 1.0 - 0.7 * (r_val ** 2) if abs(r_val) <= 0.8 else 0.3
        x_p = px2 + pw * t
        y_p = py2 + ph - (n_val * (ph - 30) + 15)
        pts.append("%.1f,%.1f" % (x_p, y_p))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts), FIELD))
    frags.append(text(px2 + pw/2, py2 + ph + 16, "n(r) - парабола", 11, MUTED, "middle"))

    # Sinusoidal Ray trajectories
    tx2, ty2 = 550, 105
    frags.append(rect(tx2, ty2, tw, th, fill=CORE_BG, stroke=LINE, sw=1.2))
    frags.append(line(tx2, ty2 + th/2, tx2 + tw, ty2 + th/2, color=MUTED, sw=1, dash="4,4"))
    
    # Axial ray
    frags.append(line(tx2, ty2 + th/2, tx2 + tw, ty2 + th/2, color=RAY_AX, sw=2))
    
    # Sinusoidal ray
    sin_pts = []
    for i in range(41):
        t = i / 40.0
        x_s = tx2 + tw * t
        y_s = ty2 + th/2 - (th/2 - 20) * math.sin(2 * math.pi * t)
        sin_pts.append("%.1f,%.1f" % (x_s, y_s))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(sin_pts), RAY_OK))

    frags.append(text(x2_c, py2 + th + 35, "Швидше поширення на периферії вирівнює час", 11, RAY_OK, "middle", bold=True))
    frags.append(text(x2_c, py2 + th + 52, "Мінімальна дисперсія", 12, RAY_OK, "middle", bold=True))

    # Bottom summary box
    summary_txt = "Ступінчастий профіль розмиває імпульси через різну довжину шляхів.\nГрадієнтний профіль прискорює периферійні промені в шарах із меншим n(r), вирівнюючи час прольоту."
    frags.append(fitbox(60, 345, 640, 60, summary_txt, size=12, fill="#fdfefe", stroke=LINE, sw=1.5))

    render(os.path.join(IMG, "index-profiles-comparison.svg"), W, H, *frags)

# ═══════════════════════════════════════════════════════════════════════════
# Fig 3: modal-structure-v-number.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_modal_structure():
    W, H = 760, 420
    frags = []
    
    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 26, "Модовий склад та відсічка одномодового режиму (V-число)", 16, INK, "middle", bold=True))

    # Left chart: V-number axis vs mode capacity
    cx, cy, cw, ch = 50, 70, 360, 270
    frags.append(rect(cx, cy, cw, ch, fill=FILL, stroke=LINE, sw=1.2))

    # V-number cutoff line (V = 2.405)
    cutoff_x = cx + (2.405 / 6.0) * cw
    frags.append(rect(cx, cy, cutoff_x - cx, ch, fill="#eafaf1", stroke="none"))
    frags.append(line(cutoff_x, cy, cutoff_x, cy + ch, color=RAY_OK, sw=2, dash="4,3"))
    frags.append(text(cutoff_x + 6, cy + 20, "V c = 2.405", 12, RAY_OK, "start", bold=True))

    # Single-mode region text
    frags.append(text(cx + (cutoff_x - cx)/2, cy + ch/2 - 10, "Одномодовий\nрежим (SMF)\nлише HE₁₁", 12, RAY_OK, "middle", bold=True))

    # Multimode region text
    frags.append(text(cutoff_x + (cx + cw - cutoff_x)/2, cy + 50, "Багатомодовий режим (MMF)", 13, POS, "middle", bold=True))
    frags.append(text(cutoff_x + (cx + cw - cutoff_x)/2, cy + 75, "Кількість мод M ≈ V² / 2", 12, MUTED, "middle"))

    # Curve for M = V^2 / 2
    curve_pts = []
    for i in range(31):
        v_val = 6.0 * (i / 30.0)
        m_val = (v_val ** 2) / 2.0
        x_p = cx + (v_val / 6.0) * cw
        y_p = cy + ch - (m_val / 18.0) * ch
        y_p = max(cy + 10, y_p)
        curve_pts.append("%.1f,%.1f" % (x_p, y_p))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(curve_pts), POS))

    # Axis labels
    frags.append(text(cx + cw / 2, cy + ch + 25, "Параметр V = (2π·a / λ) · NA", 12, INK, "middle", bold=True))
    frags.append(text(cx - 15, cy + ch / 2, "Кількість мод M", 12, INK, "middle", bold=True))

    # Right side: Field Intensity Patterns
    rx_c = 580
    frags.append(text(rx_c, 70, "Профілі інтенсивності мод", 14, INK, "middle", bold=True))

    # Fundamental HE11 mode (Gaussian spot)
    frags.append(circle(rx_c - 60, 150, 35, fill=CORE_BG, stroke=LINE, sw=1.5))
    frags.append(circle(rx_c - 60, 150, 20, fill="#aed6f1", stroke="none"))
    frags.append(circle(rx_c - 60, 150, 10, fill=RAY_AX, stroke="none"))
    frags.append(text(rx_c - 60, 202, "HE₁₁ (Основна)", 11, INK, "middle", bold=True))

    # Higher order TE01 / TM01 mode (Donut / 2 lobes)
    frags.append(circle(rx_c + 60, 150, 35, fill=CORE_BG, stroke=LINE, sw=1.5))
    frags.append(circle(rx_c + 48, 150, 12, fill=POS, stroke="none"))
    frags.append(circle(rx_c + 72, 150, 12, fill=POS, stroke="none"))
    frags.append(text(rx_c + 60, 202, "TE₀₁ / TM₀₁ (Вища)", 11, INK, "middle", bold=True))

    # Formula Box
    v_formula = "Параметр нормованої частоти:\nV = (2π · a / λ) · √(n₁² − n₂²)\nКоли V < 2.405 → волокно одномодове"
    frags.append(fitbox(450, 240, 260, 80, v_formula, size=12, fill="#fdfefe", stroke=RAY_OK, sw=1.5, bold=True))

    # Bottom summary line
    frags.append(text(W/2, H - 20, "При зменшенні діаметра серцевини a чи різниці показників Δ число V спадає нижче 2.405, виключаючи вищі моди.", 11, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "modal-structure-v-number.svg"), W, H, *frags)

# ═══════════════════════════════════════════════════════════════════════════
# Fig 4: attenuation-spectrum-windows.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_attenuation_spectrum():
    W, H = 760, 440
    frags = []
    
    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 26, "Спектр згасання світла в кварцовому оптичному волокні", 16, INK, "middle", bold=True))

    # Graph plotting area
    gx, gy, gw, gh = 70, 65, 640, 280
    frags.append(rect(gx, gy, gw, gh, fill=FILL, stroke=LINE, sw=1.2))

    # Grid lines
    for w_val in [850, 1310, 1550]:
        x_p = gx + ((w_val - 700) / 1000.0) * gw
        frags.append(line(x_p, gy, x_p, gy + gh, color=MUTED, sw=1, dash="4,4"))

    # Rayleigh scattering curve (~ 1 / lambda^4)
    ray_pts = []
    for i in range(41):
        lam = 700 + i * 25.0
        loss = 2.5 * ((850.0 / lam) ** 4)
        x_p = gx + ((lam - 700) / 1000.0) * gw
        y_p = gy + gh - (loss / 4.0) * gh
        y_p = max(gy + 5, min(gy + gh - 5, y_p))
        ray_pts.append("%.1f,%.1f" % (x_p, y_p))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' % (" ".join(ray_pts), RAY_AX))

    # IR Absorption curve (rises above 1600 nm)
    ir_pts = []
    for i in range(41):
        lam = 700 + i * 25.0
        loss = 0.01 * math.exp((lam - 1300) / 80.0) if lam > 1300 else 0.01
        x_p = gx + ((lam - 700) / 1000.0) * gw
        y_p = gy + gh - (loss / 4.0) * gh
        y_p = max(gy + 5, min(gy + gh - 5, y_p))
        ir_pts.append("%.1f,%.1f" % (x_p, y_p))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' % (" ".join(ir_pts), POS))

    # Total Attenuation Curve (with OH- peak around 1383 nm)
    tot_pts = []
    for i in range(81):
        lam = 700 + i * 12.5
        ray_l = 2.2 * ((850.0 / lam) ** 4)
        ir_l = 0.01 * math.exp((lam - 1300) / 80.0) if lam > 1300 else 0.01
        # OH peak around 1383 nm
        oh_l = 1.2 * math.exp(-((lam - 1383) / 25.0) ** 2)
        total_l = ray_l + ir_l + oh_l + 0.15
        
        x_p = gx + ((lam - 700) / 1000.0) * gw
        y_p = gy + gh - (total_l / 4.0) * gh
        y_p = max(gy + 5, min(gy + gh - 5, y_p))
        tot_pts.append("%.1f,%.1f" % (x_p, y_p))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(tot_pts), INK))

    # Highlighted Transmission Windows
    # 1st Window (850 nm)
    w1_x = gx + ((850 - 700) / 1000.0) * gw
    frags.append(circle(w1_x, gy + gh - (2.4 / 4.0) * gh, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(w1_x, gy + gh - (2.4 / 4.0) * gh - 15, "1-ше вікно (850 нм)\n~ 2.5 дБ/км", 10, FIELD, "middle", bold=True))

    # 2nd Window (1310 nm)
    w2_x = gx + ((1310 - 700) / 1000.0) * gw
    frags.append(circle(w2_x, gy + gh - (0.35 / 4.0) * gh, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(w2_x - 10, gy + gh - (0.35 / 4.0) * gh - 22, "2-ге вікно (1310 нм)\n~ 0.35 дБ/км (D=0)", 10, FIELD, "end", bold=True))

    # 3rd Window (1550 nm)
    w3_x = gx + ((1550 - 700) / 1000.0) * gw
    frags.append(circle(w3_x, gy + gh - (0.19 / 4.0) * gh, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(w3_x + 10, gy + gh - (0.19 / 4.0) * gh - 22, "3-тє вікно (1550 нм)\n~ 0.19 дБ/км (мін. втрат)", 10, FIELD, "start", bold=True))

    # Hydroxyl peak annotation
    oh_x = gx + ((1383 - 700) / 1000.0) * gw
    frags.append(text(oh_x + 15, gy + 75, "Водяний пік OH⁻ (1383 нм)", 10, POS, "start", italic=True))

    # Curve labels
    frags.append(text(gx + 120, gy + 40, "Розсіювання Релея (~ 1/λ⁴)", 11, RAY_AX, "start"))
    frags.append(text(gx + gw - 40, gy + 60, "ІФ поглинання", 11, POS, "end"))

    # Axes text
    frags.append(text(gx + gw / 2, gy + gh + 32, "Довжина хвилі λ (нм)", 12, INK, "middle", bold=True))
    frags.append(text(gx - 25, gy + gh / 2, "Згасання α (дБ/км)", 12, INK, "middle", bold=True))

    render(os.path.join(IMG, "attenuation-spectrum-windows.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_fiber_geometry()
    fig_index_profiles()
    fig_modal_structure()
    fig_attenuation_spectrum()
    print("All figures generated successfully.")
