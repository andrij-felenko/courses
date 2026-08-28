# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def naca4_points(chord, m, p, t_thick, n_pts=80):
    """Генерує координати верхньої та нижньої поверхонь NACA 4-digit."""
    x_coords = []
    # Косинусоподібне згущення точок біля передньої та задньої кромок
    for i in range(n_pts + 1):
        beta = math.pi * i / n_pts
        x_norm = 0.5 * (1.0 - math.cos(beta))
        x_coords.append(x_norm)

    upper = []
    lower = []
    camber_line = []

    for x_norm in x_coords:
        x = x_norm * chord
        # Товщина y_t
        yt = 5.0 * t_thick * chord * (
            0.2969 * math.sqrt(max(0.0, x_norm))
            - 0.1260 * x_norm
            - 0.3516 * (x_norm ** 2)
            + 0.2843 * (x_norm ** 3)
            - 0.1015 * (x_norm ** 4)
        )

        # Лінія кривини y_c та її похідна dy_c/dx
        if p == 0.0 or m == 0.0:
            yc = 0.0
            dy_dx = 0.0
        else:
            if x_norm <= p:
                yc = (m * chord / (p ** 2)) * (2.0 * p * x_norm - x_norm ** 2)
                dy_dx = (2.0 * m / (p ** 2)) * (p - x_norm)
            else:
                yc = (m * chord / ((1.0 - p) ** 2)) * ((1.0 - 2.0 * p) + 2.0 * p * x_norm - x_norm ** 2)
                dy_dx = (2.0 * m / ((1.0 - p) ** 2)) * (p - x_norm)

        theta = math.atan(dy_dx)
        xu = x - yt * math.sin(theta)
        yu = yc + yt * math.cos(theta)
        xl = x + yt * math.sin(theta)
        yl = yc - yt * math.cos(theta)

        camber_line.append((x, yc))
        upper.append((xu, yu))
        lower.append((xl, yl))

    return upper, lower, camber_line


# ── Фігура 1: Геометрія профілю крила (NACA 2412) ──────────────────────────────
def fig_naca_geometry():
    W, H = 840, 480
    body = []

    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    ox = 80
    oy = 280
    chord = 580
    m = 0.04   # 4% для виразнішої наочності на малюнку
    p = 0.40   # 40%
    t = 0.14   # 14%

    upper, lower, camber = naca4_points(chord, m, p, t, n_pts=100)

    # 1. Допоміжні осі та сітка
    # Лінія хорди (пунктир)
    body.append(line(ox - 30, oy, ox + chord + 40, oy, color=MUTED, sw=1.4, dash="6 4"))

    # 2. Шлях середньої лінії кривини (camber line)
    d_camber = ["M %.1f %.1f" % (ox + camber[0][0], oy - camber[0][1])]
    for x, y in camber[1:]:
        d_camber.append("L %.1f %.1f" % (ox + x, oy - y))
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % (" ".join(d_camber), POS))

    # 3. Шлях контуру профілю
    d_airfoil = ["M %.1f %.1f" % (ox + upper[0][0], oy - upper[0][1])]
    for x, y in upper[1:]:
        d_airfoil.append("L %.1f %.1f" % (ox + x, oy - y))
    for x, y in reversed(lower):
        d_airfoil.append("L %.1f %.1f" % (ox + x, oy - y))
    d_airfoil.append("Z")
    body.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="2.4"/>' % (" ".join(d_airfoil), INK))

    # 4. Точки та лінії вимірювання
    # Передня кромка (LE)
    body.append(circle(ox, oy, 4.5, fill=POS, stroke=INK, sw=1.5))
    tb_le, _, _ = textbox(ox - 25, oy - 80, "Передня кромка\n(LE, Leading Edge)", size=11, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_le)
    body.append(arrow(ox - 25, oy - 48, ox, oy - 6, color=POS, sw=1.4))

    # Радіус передньої кромки (r_le)
    r_le_val = 1.1019 * (t ** 2) * chord
    body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3 3"/>' % (ox + r_le_val, oy, r_le_val, POS))
    body.append(text(ox + r_le_val + 18, oy + 28, "r_LE", size=11, color=POS, bold=True))

    # Задня кромка (TE)
    body.append(circle(ox + chord, oy, 4.5, fill=POS, stroke=INK, sw=1.5))
    tb_te, _, _ = textbox(ox + chord + 35, oy - 70, "Задня кромка\n(TE, Trailing Edge)", size=11, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_te)
    body.append(arrow(ox + chord + 35, oy - 38, ox + chord + 4, oy - 6, color=POS, sw=1.4))

    # Хорда (Chord c)
    body.append(line(ox, oy + 90, ox + chord, oy + 90, color=INK, sw=1.6))
    body.append(line(ox, oy + 10, ox, oy + 105, color=MUTED, sw=1.2, dash="4 3"))
    body.append(line(ox + chord, oy + 10, ox + chord, oy + 105, color=MUTED, sw=1.2, dash="4 3"))
    body.append(arrow(ox + chord / 2 - 30, oy + 90, ox, oy + 90, color=INK, sw=1.4))
    body.append(arrow(ox + chord / 2 + 30, oy + 90, ox + chord, oy + 90, color=INK, sw=1.4))
    tb_c, _, _ = textbox(ox + chord / 2, oy + 90, "Хорда профілю (c)", size=12, fill="#ffffff", stroke=INK, sw=1.2, bold=True)
    body.append(tb_c)

    # Максимальна кривина (Max Camber m на x_p)
    xp_coord = ox + p * chord
    yp_camber = oy - (m * chord)
    body.append(line(xp_coord, oy, xp_coord, yp_camber, color=POS, sw=1.8))
    body.append(circle(xp_coord, yp_camber, 3.5, fill=POS, stroke=INK, sw=1.2))
    tb_cam, _, _ = textbox(xp_coord - 90, yp_camber - 45, "Макс. кривина (m)\nна позиції x = p·c", size=11, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_cam)
    body.append(arrow(xp_coord - 45, yp_camber - 30, xp_coord - 2, yp_camber + 2, color=POS, sw=1.4))

    # Максимальна товщина (Max Thickness t на x_t)
    xt_norm = 0.30
    xt_coord = ox + xt_norm * chord
    yt_val = 5.0 * t * chord * (0.2969 * math.sqrt(xt_norm) - 0.1260 * xt_norm - 0.3516 * (xt_norm**2) + 0.2843 * (xt_norm**3) - 0.1015 * (xt_norm**4))
    yc_val = (m * chord / (p ** 2)) * (2.0 * p * xt_norm - xt_norm ** 2)
    y_upper = oy - (yc_val + yt_val)
    y_lower = oy - (yc_val - yt_val)
    body.append(line(xt_coord, y_upper, xt_coord, y_lower, color=NEG, sw=2.0))
    body.append(circle(xt_coord, y_upper, 3.5, fill=NEG, stroke=INK, sw=1.2))
    body.append(circle(xt_coord, y_lower, 3.5, fill=NEG, stroke=INK, sw=1.2))
    tb_th, _, _ = textbox(xt_coord + 85, y_upper - 35, "Макс. товщина (t_max)\nна позиції x_t ≈ 0.3c", size=11, fill="#eff6ff", stroke=NEG, sw=1.2)
    body.append(tb_th)
    body.append(arrow(xt_coord + 35, y_upper - 20, xt_coord + 2, (y_upper + y_lower) / 2, color=NEG, sw=1.4))

    # Пояснювальні підписи поверхонь
    body.append(text(ox + 0.65 * chord, oy - 55, "Верхня поверхня (спинка / suction side)", size=11, color=INK, bold=True))
    body.append(text(ox + 0.65 * chord, oy + 45, "Нижня поверхня (черево / pressure side)", size=11, color=INK, bold=True))
    body.append(text(ox + 0.48 * chord, oy - 18, "Середня лінія кривини y_c(x)", size=11, color=POS, italic=True))

    out_svg = os.path.join(OUT, "naca-geometry.svg")
    render(out_svg, W, H, *body)


# ── Фігура 2: Розподіл коефіцієнта тиску Cp навколо профілю ───────────────────
def fig_cp_distribution():
    W, H = 840, 520
    body = []

    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    ox = 110
    oy_profile = 430
    chord = 600

    # 1. Профіль крила внизу
    upper, lower, camber = naca4_points(chord, 0.03, 0.40, 0.12, n_pts=80)
    d_airfoil = ["M %.1f %.1f" % (ox + upper[0][0], oy_profile - upper[0][1])]
    for x, y in upper[1:]:
        d_airfoil.append("L %.1f %.1f" % (ox + x, oy_profile - y))
    for x, y in reversed(lower):
        d_airfoil.append("L %.1f %.1f" % (ox + x, oy_profile - y))
    d_airfoil.append("Z")
    body.append('<path d="%s" fill="#f1f5f9" stroke="%s" stroke-width="1.8"/>' % (" ".join(d_airfoil), INK))
    body.append(line(ox, oy_profile, ox + chord, oy_profile, color=MUTED, sw=1.0, dash="4 4"))

    # 2. Графік Cp(x/c)
    oy_cp0 = 240
    scale_y = 90

    # Осі координат
    body.append(line(ox - 30, oy_cp0, ox + chord + 30, oy_cp0, color=LINE, sw=1.4))
    body.append(line(ox, oy_cp0 - 2.6 * scale_y, ox, oy_cp0 + 1.3 * scale_y, color=LINE, sw=1.4))

    # Стрілки осей
    body.append(arrow(ox + chord, oy_cp0, ox + chord + 35, oy_cp0, color=LINE, sw=1.4))
    body.append(arrow(ox, oy_cp0 - 2.5 * scale_y, ox, oy_cp0 - 2.7 * scale_y, color=LINE, sw=1.4))

    body.append(text(ox + chord + 40, oy_cp0 + 15, "x / c", size=12, color=INK, bold=True))
    body.append(text(ox - 45, oy_cp0 - 2.6 * scale_y, "−C_p", size=13, color=POS, bold=True))
    body.append(text(ox - 45, oy_cp0 + 1.2 * scale_y, "+C_p", size=13, color=NEG, bold=True))

    # Поділки на осі Cp
    for cp_val, label in [(-2.0, "−2.0"), (-1.0, "−1.0"), (0.0, " 0.0"), (1.0, "+1.0")]:
        y_pos = oy_cp0 + cp_val * scale_y
        body.append(line(ox - 5, y_pos, ox + chord, y_pos, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(ox - 18, y_pos + 4, label, size=11, color=MUTED, anchor="end"))

    # Поділки на осі x/c
    for xc_val, label in [(0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1.0, "1.0")]:
        x_pos = ox + xc_val * chord
        body.append(line(x_pos, oy_cp0 - 2.4 * scale_y, x_pos, oy_cp0 + 1.1 * scale_y, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(x_pos, oy_cp0 + 20, label, size=11, color=MUTED, anchor="middle"))

    # Розрахунок кривих Cp для альфа = 5 градусів
    pts_upper_cp = []
    pts_lower_cp = []
    n_cp = 60

    for i in range(n_cp + 1):
        xc = i / float(n_cp)
        if xc == 0:
            cp_u = 1.0
            cp_l = 1.0
        else:
            cp_u = -2.2 * math.exp(-xc / 0.12) - 0.4 * (1.0 - xc) + 0.15 * math.sin(math.pi * xc)
            cp_l = 0.8 * math.exp(-xc / 0.08) + 0.3 * (1.0 - xc) ** 1.5 - 0.05
        
        y_u = oy_cp0 + cp_u * scale_y
        y_l = oy_cp0 + cp_l * scale_y
        pts_upper_cp.append((ox + xc * chord, y_u))
        pts_lower_cp.append((ox + xc * chord, y_l))

    # Зафарбована область між кривими
    d_area = ["M %.1f %.1f" % pts_upper_cp[0]]
    for pt in pts_upper_cp[1:]:
        d_area.append("L %.1f %.1f" % pt)
    for pt in reversed(pts_lower_cp):
        d_area.append("L %.1f %.1f" % pt)
    d_area.append("Z")
    body.append('<path d="%s" fill="#eff6ff" stroke="none" opacity="0.8"/>' % " ".join(d_area))

    d_cpu = ["M %.1f %.1f" % pts_upper_cp[0]]
    for pt in pts_upper_cp[1:]:
        d_cpu.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(d_cpu), POS))

    d_cpl = ["M %.1f %.1f" % pts_lower_cp[0]]
    for pt in pts_lower_cp[1:]:
        d_cpl.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(d_cpl), NEG))

    # Стрілочки перепаду тиску
    for k in (6, 15, 25, 38, 50):
        xc_k = k / float(n_cp)
        xk = ox + xc_k * chord
        yu_k = pts_upper_cp[k][1]
        yl_k = pts_lower_cp[k][1]
        body.append(arrow(xk, yl_k, xk, yu_k, color=POS, sw=1.2))

    # Підписи та виноски
    x_peak, y_peak = pts_upper_cp[4]
    body.append(circle(x_peak, y_peak, 4.0, fill=POS, stroke=INK, sw=1.4))
    tb_peak, _, _ = textbox(x_peak + 110, y_peak - 15, "Пік розрідження (Suction Peak)\nC_p < 0  (v > v_inf)", size=11, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_peak)
    body.append(arrow(x_peak + 45, y_peak - 10, x_peak + 6, y_peak, color=POS, sw=1.3))

    body.append(circle(ox, oy_cp0 + 1.0 * scale_y, 4.0, fill=INK, stroke=INK, sw=1.4))
    tb_stag, _, _ = textbox(ox + 85, oy_cp0 + 1.0 * scale_y + 35, "Точка гальмування\nC_p = +1.0  (v = 0)", size=11, fill="#ffffff", stroke=INK, sw=1.2)
    body.append(tb_stag)
    body.append(arrow(ox + 40, oy_cp0 + 1.0 * scale_y + 25, ox + 5, oy_cp0 + 1.0 * scale_y + 4, color=INK, sw=1.3))

    tb_cl, _, _ = textbox(ox + 0.45 * chord, oy_cp0 - 0.7 * scale_y, "Заштрихована площа ∮(C_p,l − C_p,u) d(x/c)\n= коефіцієнт підіймальної сили C_l", size=12, fill="#ffffff", stroke=POS, sw=1.4, bold=True)
    body.append(tb_cl)

    tb_leg, _, _ = textbox(ox + 0.78 * chord, oy_cp0 - 1.8 * scale_y, "— Спинка (верхня поверхня)\n— Черево (нижня поверхня)", size=11, fill="#ffffff", stroke=LINE, sw=1.0)
    body.append(tb_leg)

    out_svg = os.path.join(OUT, "cp-distribution.svg")
    render(out_svg, W, H, *body)


# ── Фігура 3: Примежовий шар та відривна бульбашка (LSB) ──────────────────────
def fig_boundary_layer_separation():
    W, H = 840, 500
    body = []

    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    ox = 80
    oy = 340
    chord = 680

    body.append(line(ox - 30, oy, ox + chord + 30, oy, color=MUTED, sw=1.0, dash="5 4"))
    
    pts_surface = []
    for i in range(101):
        t_val = i / 100.0
        x = ox + t_val * chord
        y = oy - 85.0 * math.sin(math.pi * t_val) * (1.0 - 0.3 * t_val)
        pts_surface.append((x, y))

    d_surf = ["M %.1f %.1f" % pts_surface[0]]
    for pt in pts_surface[1:]:
        d_surf.append("L %.1f %.1f" % pt)
    d_surf.append("L %.1f %.1f" % (ox + chord, oy + 40))
    d_surf.append("L %.1f %.1f" % (ox, oy + 40))
    d_surf.append("Z")
    body.append('<path d="%s" fill="#e2e8f0" stroke="%s" stroke-width="2.2"/>' % (" ".join(d_surf), INK))

    x_sep = ox + 0.28 * chord
    x_reatt = ox + 0.56 * chord

    pts_bl = []
    for i in range(101):
        t_val = i / 100.0
        x = ox + t_val * chord
        y_surf = oy - 85.0 * math.sin(math.pi * t_val) * (1.0 - 0.3 * t_val)
        if t_val <= 0.25:
            delta = 16.0 * math.sqrt(max(0.01, t_val))
        elif t_val <= 0.55:
            delta = 22.0 + 20.0 * math.sin(math.pi * (t_val - 0.25) / 0.30)
        else:
            delta = 35.0 + 45.0 * (t_val - 0.55) ** 0.8
        pts_bl.append((x, y_surf - delta))

    d_bl = ["M %.1f %.1f" % pts_bl[0]]
    for pt in pts_bl[1:]:
        d_bl.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4 3"/>' % (" ".join(d_bl), POS))

    pts_bubble = []
    for i in range(25, 57):
        t_val = i / 100.0
        x = ox + t_val * chord
        y_surf = oy - 85.0 * math.sin(math.pi * t_val) * (1.0 - 0.3 * t_val)
        delta_b = 20.0 * math.sin(math.pi * (t_val - 0.25) / 0.30)
        pts_bubble.append((x, y_surf - delta_b))
    for i in range(56, 24, -1):
        t_val = i / 100.0
        x = ox + t_val * chord
        y_surf = oy - 85.0 * math.sin(math.pi * t_val) * (1.0 - 0.3 * t_val)
        pts_bubble.append((x, y_surf))
    
    d_bub = ["M %.1f %.1f" % pts_bubble[0]]
    for pt in pts_bubble[1:]:
        d_bub.append("L %.1f %.1f" % pt)
    d_bub.append("Z")
    body.append('<path d="%s" fill="#fee2e2" stroke="%s" stroke-width="1.4" stroke-dasharray="3 2"/>' % (" ".join(d_bub), POS))

    body.append('<circle cx="%.1f" cy="%.1f" r="7" fill="none" stroke="%s" stroke-width="1.4"/>' % (ox + 0.38 * chord, oy - 92, POS))
    body.append('<circle cx="%.1f" cy="%.1f" r="9" fill="none" stroke="%s" stroke-width="1.4"/>' % (ox + 0.47 * chord, oy - 85, POS))

    # Профілі швидкості
    x1 = ox + 0.12 * chord
    y1_s = oy - 85.0 * math.sin(math.pi * 0.12) * (1.0 - 0.3 * 0.12)
    body.append(line(x1, y1_s, x1, y1_s - 30, color=LINE, sw=1.2))
    for dy in (6, 14, 22):
        u_len = 18.0 * math.sqrt(dy / 30.0)
        body.append(arrow(x1, y1_s - dy, x1 + u_len, y1_s - dy, color=NEG, sw=1.1))

    x2 = ox + 0.28 * chord
    y2_s = oy - 85.0 * math.sin(math.pi * 0.28) * (1.0 - 0.3 * 0.28)
    body.append(circle(x2, y2_s, 4.0, fill=POS, stroke=INK, sw=1.4))
    body.append(line(x2, y2_s, x2, y2_s - 35, color=LINE, sw=1.2))
    for dy in (8, 18, 28):
        u_len = 16.0 * (dy / 35.0) ** 2
        body.append(arrow(x2, y2_s - dy, x2 + u_len, y2_s - dy, color=NEG, sw=1.1))

    x3 = ox + 0.65 * chord
    y3_s = oy - 85.0 * math.sin(math.pi * 0.65) * (1.0 - 0.3 * 0.65)
    body.append(line(x3, y3_s, x3, y3_s - 50, color=LINE, sw=1.2))
    for dy in (8, 18, 30, 42):
        u_len = 22.0 * (dy / 50.0) ** (1.0 / 7.0)
        body.append(arrow(x3, y3_s - dy, x3 + u_len, y3_s - dy, color=NEG, sw=1.1))

    # Текстові панелі
    tb_1, _, _ = textbox(ox + 0.12 * chord, 100, "1. Ламінарний шар\nСприятливий градієнт (dp/dx < 0)\nМале тертя, впорядкований рух", size=11, fill="#f8fafc", stroke=MUTED, sw=1.0)
    body.append(tb_1)
    body.append(arrow(ox + 0.12 * chord, 135, ox + 0.12 * chord, y1_s - 35, color=MUTED, sw=1.2))

    tb_2, _, _ = textbox(ox + 0.42 * chord, 75, "2. Ламінарна відривна бульбашка (LSB)\nНесприятливий градієнт (dp/dx > 0) → Відрив\nПерехід у шарі зсуву → Турбулентне приєднання", size=11, fill="#fef2f2", stroke=POS, sw=1.4, bold=True)
    body.append(tb_2)
    body.append(arrow(ox + 0.42 * chord, 115, ox + 0.42 * chord, oy - 105, color=POS, sw=1.3))

    tb_3, _, _ = textbox(ox + 0.78 * chord, 110, "3. Турбулентний шар\nНаповнений профіль швидкості u(y)\nВисоке тертя, стійкість до зриву", size=11, fill="#eff6ff", stroke=NEG, sw=1.0)
    body.append(tb_3)
    body.append(arrow(ox + 0.78 * chord, 145, x3, y3_s - 55, color=NEG, sw=1.2))

    body.append(text(x2 - 10, y2_s + 20, "S (відрив)", size=11, color=POS, bold=True))
    body.append(text(x_reatt + 10, oy - 85.0 * math.sin(math.pi * 0.56) * (1.0 - 0.3 * 0.56) + 20, "R (приєднання)", size=11, color=NEG, bold=True))

    out_svg = os.path.join(OUT, "boundary-layer-separation.svg")
    render(out_svg, W, H, *body)


# ── Фігура 4: Аеродинамічні поляри та вплив числа Рейнольдса ─────────────────
def fig_polar_reynolds_effect():
    W, H = 840, 480
    body = []

    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    w_plot = 340
    ox1 = 75
    oy1_zero = 310
    ox1_alpha0 = ox1 + 100

    body.append(line(ox1, oy1_zero, ox1 + w_plot, oy1_zero, color=LINE, sw=1.3))
    body.append(line(ox1_alpha0, oy1_zero - 220, ox1_alpha0, oy1_zero + 60, color=LINE, sw=1.3))

    body.append(text(ox1 + w_plot + 15, oy1_zero + 4, "α (°)", size=12, color=INK, bold=True))
    body.append(text(ox1_alpha0 - 15, oy1_zero - 225, "C_l", size=13, color=INK, bold=True))

    for cl_val, label in [(0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5")]:
        yp = oy1_zero - cl_val * 130
        body.append(line(ox1_alpha0 - 4, yp, ox1 + w_plot, yp, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(ox1_alpha0 - 12, yp + 4, label, size=10, color=MUTED, anchor="end"))

    for a_val, label in [(-4, "−4"), (0, "0"), (5, "5"), (10, "10"), (15, "15"), (20, "20")]:
        xp = ox1_alpha0 + a_val * 11.0
        body.append(line(xp, oy1_zero - 210, xp, oy1_zero + 50, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(xp, oy1_zero + 18, label, size=10, color=MUTED, anchor="middle"))

    pts_cl_high = []
    pts_cl_low = []

    for a_deg in range(-4, 22):
        xp = ox1_alpha0 + a_deg * 11.0
        if a_deg < 14:
            cl_h = 0.25 + 0.105 * a_deg
        elif a_deg <= 16:
            cl_h = 1.50 + 0.05 * (a_deg - 14) - 0.04 * ((a_deg - 14) ** 2)
        else:
            cl_h = 1.55 - 0.06 * (a_deg - 16) - 0.015 * ((a_deg - 16) ** 2)
        
        if a_deg < 8:
            cl_l = 0.20 + 0.088 * a_deg
        elif a_deg <= 11:
            cl_l = 0.90 + 0.05 * (a_deg - 8) - 0.03 * ((a_deg - 8) ** 2)
        else:
            cl_l = 1.05 - 0.09 * (a_deg - 11) - 0.01 * ((a_deg - 11) ** 2)

        pts_cl_high.append((xp, oy1_zero - cl_h * 130))
        pts_cl_low.append((xp, oy1_zero - cl_l * 130))

    d_cl_h = ["M %.1f %.1f" % pts_cl_high[0]]
    for pt in pts_cl_high[1:]:
        d_cl_h.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(d_cl_h), NEG))

    d_cl_l = ["M %.1f %.1f" % pts_cl_low[0]]
    for pt in pts_cl_low[1:]:
        d_cl_l.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 3"/>' % (" ".join(d_cl_l), POS))

    body.append(text(ox1 + w_plot / 2, 40, "Залежність C_l(α)", size=13, color=INK, bold=True))

    ox2 = 475
    oy2_zero = oy1_zero
    body.append(line(ox2, oy2_zero, ox2 + w_plot, oy2_zero, color=LINE, sw=1.3))
    body.append(line(ox2, oy2_zero - 220, ox2, oy2_zero + 60, color=LINE, sw=1.3))

    body.append(text(ox2 + w_plot + 15, oy2_zero + 4, "C_d", size=12, color=INK, bold=True))
    body.append(text(ox2 - 15, oy2_zero - 225, "C_l", size=13, color=INK, bold=True))

    for cd_val, label in [(0.02, "0.02"), (0.04, "0.04"), (0.06, "0.06"), (0.08, "0.08")]:
        xp = ox2 + cd_val * 3500
        body.append(line(xp, oy2_zero - 210, xp, oy2_zero + 50, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(xp, oy2_zero + 18, label, size=10, color=MUTED, anchor="middle"))

    for cl_val, label in [(0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5")]:
        yp = oy2_zero - cl_val * 130
        body.append(line(ox2 - 4, yp, ox2 + w_plot, yp, color="#e2e8f0", sw=1.0, dash="3 3"))
        body.append(text(ox2 - 12, yp + 4, label, size=10, color=MUTED, anchor="end"))

    pts_polar_high = []
    for i in range(len(pts_cl_high)):
        a_deg = -4 + i
        if a_deg < 14:
            cl_h = 0.25 + 0.105 * a_deg
            cd_h = 0.007 + 0.018 * ((cl_h - 0.3) ** 2)
        elif a_deg <= 16:
            cl_h = 1.50 + 0.05 * (a_deg - 14) - 0.04 * ((a_deg - 14) ** 2)
            cd_h = 0.020 + 0.04 * (a_deg - 14)
        else:
            cl_h = 1.55 - 0.06 * (a_deg - 16) - 0.015 * ((a_deg - 16) ** 2)
            cd_h = 0.040 + 0.012 * ((a_deg - 16) ** 1.5)
        pts_polar_high.append((ox2 + cd_h * 3500, oy2_zero - cl_h * 130))

    pts_polar_low = []
    for i in range(len(pts_cl_low)):
        a_deg = -4 + i
        if a_deg < 8:
            cl_l = 0.20 + 0.088 * a_deg
            cd_l = 0.022 + 0.045 * ((cl_l - 0.25) ** 2)
        elif a_deg <= 11:
            cl_l = 0.90 + 0.05 * (a_deg - 8) - 0.03 * ((a_deg - 8) ** 2)
            cd_l = 0.045 + 0.03 * (a_deg - 8)
        else:
            cl_l = 1.05 - 0.09 * (a_deg - 11) - 0.01 * ((a_deg - 11) ** 2)
            cd_l = 0.065 + 0.015 * ((a_deg - 11) ** 1.3)
        pts_polar_low.append((ox2 + cd_l * 3500, oy2_zero - cl_l * 130))

    d_pol_h = ["M %.1f %.1f" % pts_polar_high[0]]
    for pt in pts_polar_high[1:]:
        d_pol_h.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(d_pol_h), NEG))

    d_pol_l = ["M %.1f %.1f" % pts_polar_low[0]]
    for pt in pts_polar_low[1:]:
        d_pol_l.append("L %.1f %.1f" % pt)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 3"/>' % (" ".join(d_pol_l), POS))

    body.append(line(ox2, oy2_zero, ox2 + 0.025 * 3500, oy2_zero - 1.25 * 130, color="#16a34a", sw=1.6, dash="5 3"))
    body.append(text(ox2 + 0.027 * 3500 + 10, oy2_zero - 1.25 * 130 + 4, "K_max = (C_l/C_d)_max", size=11, color="#16a34a", bold=True))

    body.append(text(ox2 + w_plot / 2, 40, "Поляра C_l(C_d)", size=13, color=INK, bold=True))

    tb_leg, _, _ = textbox(W / 2, 435, "— Re = 1 000 000 (пілотована авіація, високий C_l_max, малий C_d)\n- - Re = 100 000 (малі БПЛА, деградація C_l, зростання опору C_d через LSB)", size=11, fill="#f8fafc", stroke=LINE, sw=1.2)
    body.append(tb_leg)

    out_svg = os.path.join(OUT, "polar-reynolds-effect.svg")
    render(out_svg, W, H, *body)


# ── Фігура 5: Дискретизація профілю панельним методом ─────────────────────────
def fig_panel_method_discretization():
    W, H = 840, 480
    body = []

    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    ox = 100
    oy = 250
    chord = 600

    upper, lower, camber = naca4_points(chord, 0.04, 0.40, 0.14, n_pts=8)
    
    nodes = upper + lower[::-1][1:-1]
    n_panels = len(nodes)

    for i in range(n_panels):
        p1 = nodes[i]
        p2 = nodes[(i + 1) % n_panels]
        x1, y1 = ox + p1[0], oy - p1[1]
        x2, y2 = ox + p2[0], oy - p2[1]
        
        body.append(line(x1, y1, x2, y2, color=INK, sw=2.2))
        body.append(circle(x1, y1, 3.5, fill=MUTED, stroke=INK, sw=1.2))

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        body.append(circle(cx, cy, 3.8, fill=POS, stroke=INK, sw=1.4))

        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            nx = -dy / length
            ny = dx / length
            body.append(arrow(cx, cy, cx + nx * 22, cy + ny * 22, color=NEG, sw=1.4))

    k_sel = 3
    p1 = nodes[k_sel]
    p2 = nodes[k_sel + 1]
    x1, y1 = ox + p1[0], oy - p1[1]
    x2, y2 = ox + p2[0], oy - p2[1]
    cx_sel = (x1 + x2) / 2.0
    cy_sel = (y1 + y2) / 2.0

    body.append(line(x1, y1, x2, y2, color=POS, sw=3.6))
    body.append(circle(cx_sel, cy_sel, 5.5, fill=POS, stroke=INK, sw=1.8))

    tb_panel, _, _ = textbox(cx_sel + 80, cy_sel - 85, "Панель i (відрізок між вузлами):\n• Контрольна точка (x_cp, y_cp)\n• Нормаль n_i: умова v · n_i = 0\n• Інтенсивність вихрового шару γ_i", size=11, fill="#fef2f2", stroke=POS, sw=1.3, bold=True)
    body.append(tb_panel)
    body.append(arrow(cx_sel + 40, cy_sel - 50, cx_sel + 3, cy_sel - 7, color=POS, sw=1.4))

    te_x = ox + chord
    te_y = oy
    body.append(circle(te_x, te_y, 5.0, fill=INK, stroke=POS, sw=2.0))
    tb_kutta, _, _ = textbox(te_x - 30, te_y + 110, "Дискретна умова Кутти:\nγ_1 + γ_N = 0  або  v_t,1 = v_t,N\n(потік гладко сходить із задньої кромки)", size=11, fill="#eff6ff", stroke=NEG, sw=1.3, bold=True)
    body.append(tb_kutta)
    body.append(arrow(te_x - 30, te_y + 65, te_x - 2, te_y + 8, color=NEG, sw=1.4))

    for y_off in (-100, -50, 0, 50, 100):
        body.append(arrow(30, oy + y_off, 80, oy + y_off, color=LINE, sw=1.4))
    body.append(text(55, oy - 118, "v_inf", size=13, color=LINE, bold=True))

    tb_mat, _, _ = textbox(W / 2, 435, "Система лінійних рівнянь:  ∑ A_ij · γ_j = − (v_inf · n_i)  для всіх i = 1..N + умова Кутти", size=12, fill="#f8fafc", stroke=LINE, sw=1.2, bold=True)
    body.append(tb_mat)

    out_svg = os.path.join(OUT, "panel-method-discretization.svg")
    render(out_svg, W, H, *body)


if __name__ == "__main__":
    fig_naca_geometry()
    fig_cp_distribution()
    fig_boundary_layer_separation()
    fig_polar_reynolds_effect()
    fig_panel_method_discretization()
    print("Всі фігури успішно згенеровано.")
