# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Кінематика маніпулятора: пряма й обернена».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Допоміжна функція малювання координатної осі з наконечником ─────────────
def draw_frame_axis(x, y, dx, dy, label, color=LINE, size=13):
    parts = []
    x2, y2 = x + dx, y + dy
    parts.append(arrow(x, y, x2, y2, color=color, sw=2))
    lx = x2 + (14 if dx > 0 else (-14 if dx < 0 else 0))
    ly = y2 + (14 if dy > 0 else (-14 if dy < 0 else 0))
    if dx > 0 and dy == 0:
        lx, ly = x2 + 12, y2 + 4
    elif dx == 0 and dy < 0:
        lx, ly = x2, y2 - 10
    elif dx < 0 and dy == 0:
        lx, ly = x2 - 12, y2 + 4
    parts.append(text(lx, ly, label, size=size, color=color, bold=True))
    return "".join(parts)


# ── Фігура 1: Геометрія DH-параметрів між сусідніми ланками ─────────────────
def fig_dh_parameters():
    W, H = 960, 520
    parts = []

    parts.append(text(W / 2, 34, "Чотири параметри Денавіта-Гартенберга (DH)", size=18, bold=True))
    parts.append(text(W / 2, 58, "геометричне перетворення між осями зчленувань i-1 та i", size=13, color=MUTED))

    z1_x, z1_y_top, z1_y_bot = 220, 110, 430
    z2_x, z2_y_top, z2_y_bot = 680, 110, 430

    o_prev_x, o_prev_y = z1_x, 370
    inter_x, inter_y = z1_x, 230
    o_curr_x, o_curr_y = z2_x, 230

    parts.append(rect(z1_x - 22, 160, 44, 230, fill="#f1f5f9", stroke="#cbd5e1", sw=2, rx=10))
    parts.append(rect(z2_x - 22, 160, 44, 230, fill="#f1f5f9", stroke="#cbd5e1", sw=2, rx=10))

    parts.append(line(inter_x, inter_y, o_curr_x, o_curr_y, color="#475569", sw=6))
    parts.append(rect(inter_x + 30, inter_y - 12, (o_curr_x - inter_x) - 60, 24, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))

    parts.append(line(z1_x, z1_y_bot, z1_x, z1_y_top, color=NEG, sw=2, dash="6,4"))
    parts.append(arrow(z1_x, z1_y_bot, z1_x, z1_y_top + 15, color=NEG, sw=2.5))
    parts.append(text(z1_x - 30, z1_y_top + 20, "Z_{i-1}", size=14, color=NEG, bold=True))

    parts.append(line(z2_x, z2_y_bot, z2_x, z2_y_top, color=NEG, sw=2, dash="6,4"))
    parts.append(arrow(z2_x, z2_y_bot, z2_x, z2_y_top + 15, color=NEG, sw=2.5))
    parts.append(text(z2_x + 30, z2_y_top + 20, "Z_i", size=14, color=NEG, bold=True))

    parts.append(arrow(o_prev_x, o_prev_y, o_prev_x + 100, o_prev_y, color=POS, sw=2.2))
    parts.append(text(o_prev_x + 120, o_prev_y + 4, "X_{i-1}", size=14, color=POS, bold=True))

    parts.append(arrow(inter_x, inter_y, o_curr_x + 110, inter_y, color=POS, sw=2.5))
    parts.append(text(o_curr_x + 135, inter_y + 4, "X_i", size=14, color=POS, bold=True))

    parts.append(line(o_prev_x, o_prev_y, o_prev_x + 85, o_prev_y - 45, color=FIELD, sw=2, dash="4,4"))
    parts.append(line(o_prev_x, o_prev_y, o_prev_x + 85, o_prev_y, color=POS, sw=1.5))

    parts.append(circle(o_prev_x, o_prev_y, 5, fill="#ffffff", stroke=INK, sw=2))
    parts.append(text(o_prev_x - 30, o_prev_y + 4, "O_{i-1}", size=13, bold=True))

    parts.append(circle(o_curr_x, o_curr_y, 5, fill="#ffffff", stroke=INK, sw=2))
    parts.append(text(o_curr_x + 22, o_curr_y + 20, "O_i", size=13, bold=True))

    parts.append(circle(inter_x, inter_y, 4, fill=FIELD, stroke=INK, sw=1.5))

    parts.append(line(z1_x - 50, o_prev_y, z1_x - 50, inter_y, color=LINE, sw=1.8))
    parts.append(line(z1_x - 60, o_prev_y, z1_x - 10, o_prev_y, color=MUTED, sw=1, dash="2,2"))
    parts.append(line(z1_x - 60, inter_y, z1_x - 10, inter_y, color=MUTED, sw=1, dash="2,2"))
    b1, _, _ = textbox(z1_x - 100, (o_prev_y + inter_y) / 2, "d_i: зміщення вздовж Z_{i-1}\n(link offset)", size=12, pad=6, fill="#f8fafc", stroke=LINE)
    parts.append(b1)

    parts.append(line(o_prev_x + 45, o_prev_y, o_prev_x + 40, o_prev_y - 20, color=FIELD, sw=2))
    b2, _, _ = textbox(o_prev_x + 115, o_prev_y - 35, "θ_i: кут між X_{i-1} та X_i\nнавколо осі Z_{i-1}", size=12, pad=6, fill="#eefaf2", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b2)

    parts.append(line(inter_x, inter_y - 45, o_curr_x, inter_y - 45, color=POS, sw=1.8))
    parts.append(line(inter_x, inter_y - 55, inter_x, inter_y - 10, color=MUTED, sw=1, dash="2,2"))
    parts.append(line(o_curr_x, inter_y - 55, o_curr_x, inter_y - 10, color=MUTED, sw=1, dash="2,2"))
    b3, _, _ = textbox((inter_x + o_curr_x) / 2, inter_y - 75, "a_i: довжина спільного перпендикуляра вздовж X_i (link length)", size=12, pad=6, fill="#fdf2f2", stroke=POS, color=POS, bold=True)
    parts.append(b3)

    b4, _, _ = textbox(z2_x + 130, z2_y_top + 75, "α_i: кут між Z_{i-1} та Z_i\nнавколо осі X_i (link twist)", size=12, pad=6, fill="#f0f4ff", stroke=NEG, color=NEG, bold=True)
    parts.append(b4)

    rule_box, _, _ = textbox(W / 2, 475, "T_i^(i-1) = Rot(Z, θ_i) · Trans(Z, d_i) · Trans(X, a_i) · Rot(X, α_i)", size=14, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    parts.append(rule_box)

    return render("img/dh-parameters-frame.svg", W, H, *parts)


# ── Фігура 2: Геометрична обернена кінематика 2-DOF / 3-DOF ─────────────────
def fig_geometric_ik():
    W, H = 960, 500
    parts = []

    parts.append(text(W / 2, 32, "Геометрична обернена кінематика: розв'язки ліктем угору та ліктем униз", size=18, bold=True))
    parts.append(text(W / 2, 54, "розщеплення просторової задачі 3-DOF на азимут основи та плоску руку 2-DOF", size=13, color=MUTED))

    cx1, cy1 = 200, 260
    parts.append(text(cx1, 95, "1. Азимут основи (вид зверху X-Y)", size=14, bold=True))
    parts.append(line(cx1 - 120, cy1, cx1 + 140, cy1, color="#cbd5e1", sw=1.5))
    parts.append(line(cx1, cy1 + 120, cx1, cy1 - 140, color="#cbd5e1", sw=1.5))
    parts.append(arrow(cx1, cy1, cx1 + 130, cy1, color=POS, sw=1.8))
    parts.append(text(cx1 + 145, cy1 + 4, "X_0", size=13, color=POS, bold=True))
    parts.append(arrow(cx1, cy1, cx1, cy1 - 130, color=NEG, sw=1.8))
    parts.append(text(cx1, cy1 - 145, "Y_0", size=13, color=NEG, bold=True))

    tx, ty = cx1 + 95, cy1 - 75
    parts.append(line(cx1, cy1, tx, ty, color=FIELD, sw=2.5))
    parts.append(circle(tx, ty, 5, fill=POS, stroke=INK, sw=1.5))
    parts.append(text(tx + 22, ty - 8, "P(x, y)", size=12, bold=True))
    parts.append(line(tx, ty, tx, cy1, color=MUTED, sw=1.2, dash="3,3"))
    parts.append(line(tx, ty, cx1, ty, color=MUTED, sw=1.2, dash="3,3"))
    parts.append(text(tx, cy1 + 16, "x", size=12, color=MUTED))
    parts.append(text(cx1 - 16, ty, "y", size=12, color=MUTED))

    parts.append(line(cx1 + 40, cy1, cx1 + 33, cy1 - 25, color=FIELD, sw=1.8))
    parts.append(text(cx1 + 55, cy1 - 14, "θ_1", size=13, color=FIELD, bold=True))

    b_azimuth, _, _ = textbox(cx1, 420, "θ_1 = atan2(y, x)\nr = √(x² + y²)", size=13, pad=8, fill="#f8fafc", stroke=LINE, bold=True)
    parts.append(b_azimuth)

    cx2, cy2 = 640, 360
    parts.append(text(cx2 + 40, 95, "2. Плоска рука в осях r–Z (дві конфігурації)", size=14, bold=True))

    parts.append(line(cx2 - 40, cy2, cx2 + 250, cy2, color=POS, sw=1.5))
    parts.append(arrow(cx2, cy2, cx2 + 240, cy2, color=POS, sw=1.8))
    parts.append(text(cx2 + 255, cy2 + 4, "r", size=13, color=POS, bold=True))

    parts.append(line(cx2, cy2 + 40, cx2, cy2 - 240, color=NEG, sw=1.5))
    parts.append(arrow(cx2, cy2, cx2, cy2 - 230, color=NEG, sw=1.8))
    parts.append(text(cx2, cy2 - 245, "Z_0", size=13, color=NEG, bold=True))

    px, py = cx2 + 170, cy2 - 130
    parts.append(circle(px, py, 6, fill=POS, stroke=INK, sw=2))
    parts.append(text(px + 45, py, "Ціль (r, z)", size=13, color=POS, bold=True))

    parts.append(line(cx2, cy2, px, py, color="#94a3b8", sw=1.8, dash="4,4"))
    parts.append(text(cx2 + 75, cy2 - 50, "s", size=12, color=MUTED, bold=True))

    e1_x, e1_y = cx2 + 45, cy2 - 122
    parts.append(line(cx2, cy2, e1_x, e1_y, color=FIELD, sw=3.5))
    parts.append(line(e1_x, e1_y, px, py, color=FIELD, sw=3.5))
    parts.append(circle(e1_x, e1_y, 5, fill="#ffffff", stroke=FIELD, sw=2))
    parts.append(text(e1_x - 45, e1_y - 10, "Лікоть угору", size=12, color=FIELD, bold=True))
    parts.append(text(cx2 + 15, cy2 - 70, "L_1", size=12, color=FIELD, bold=True))
    parts.append(text(e1_x + 65, e1_y - 12, "L_2", size=12, color=FIELD, bold=True))

    e2_x, e2_y = cx2 + 125, cy2 - 8
    parts.append(line(cx2, cy2, e2_x, e2_y, color=NEG, sw=2.5, dash="6,3"))
    parts.append(line(e2_x, e2_y, px, py, color=NEG, sw=2.5, dash="6,3"))
    parts.append(circle(e2_x, e2_y, 5, fill="#ffffff", stroke=NEG, sw=2))
    parts.append(text(e2_x + 35, e2_y + 20, "Лікоть униз", size=12, color=NEG, bold=True))

    parts.append(circle(cx2, cy2, 6, fill=INK, stroke=INK))
    parts.append(text(cx2 - 18, cy2 + 18, "O_0", size=12, bold=True))

    b_ik, _, _ = textbox(cx2 + 40, 435, "cos(θ_3) = (s² − L_1² − L_2²) / (2 · L_1 · L_2)\nθ_3 = ± atan2(√(1 − cos²θ_3), cos θ_3)", size=12.5, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    parts.append(b_ik)

    return render("img/geometric-ik-2dof-3dof.svg", W, H, *parts)


# ── Фігура 3: Матриця Якобі та еліпсоїд маніпулятивності ────────────────────
def fig_jacobian_mapping():
    W, H = 960, 480
    parts = []

    parts.append(text(W / 2, 32, "Диференціальна кінематика: відображення швидкостей через матрицю Якобі J(q)", size=18, bold=True))
    parts.append(text(W / 2, 54, "перетворення одиничної сфери швидкостей суглобів у декартів еліпсоїд швидкостей", size=13, color=MUTED))

    lx, ly = 200, 240
    parts.append(text(lx, 95, "Простір зчленувань (Joint Space)", size=14, bold=True))
    parts.append(text(lx, 115, "вектор кутових швидкостей q̇ = [q̇_1, q̇_2, ..., q̇_n]ᵀ", size=11.5, color=MUTED))

    parts.append(line(lx - 90, ly, lx + 90, ly, color="#cbd5e1", sw=1.5))
    parts.append(line(lx, ly - 90, lx, ly + 90, color="#cbd5e1", sw=1.5))
    parts.append(circle(lx, ly, 65, fill="#f0fdf4", stroke=FIELD, sw=2))
    parts.append(circle(lx, ly, 3, fill=INK, stroke=INK))
    parts.append(arrow(lx, ly, lx + 45, ly - 45, color=FIELD, sw=2))
    parts.append(text(lx + 55, ly - 50, "q̇", size=13, color=FIELD, bold=True))
    parts.append(text(lx, ly + 85, "‖q̇‖ ≤ 1 (одинична сфера)", size=12, color=FIELD, bold=True))

    cx = 440
    parts.append(arrow(cx - 30, ly, cx + 40, ly, color=LINE, sw=3))
    b_map, _, _ = textbox(cx + 5, ly - 45, "Пряма: v_ee = J(q) · q̇\nОбернена: q̇ = J⁺ · v_ee", size=13, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    parts.append(b_map)

    rx1, ry1 = 740, 170
    parts.append(text(rx1, 95, "Декартів простір: Регулярна поза (Regular)", size=13.5, bold=True, color=FIELD))
    parts.append('<ellipse cx="%d" cy="%d" rx="90" ry="45" fill="#f0f9ff" stroke="%s" stroke-width="2" transform="rotate(-20 %d %d)"/>' % (rx1, ry1, NEG, rx1, ry1))
    parts.append(circle(rx1, ry1, 3, fill=INK, stroke=INK))
    parts.append(arrow(rx1, ry1, rx1 + 75, ry1 - 25, color=NEG, sw=2))
    parts.append(text(rx1 + 85, ry1 - 32, "σ_1 · u_1", size=11.5, color=NEG, bold=True))
    parts.append(arrow(rx1, ry1, rx1 - 15, ry1 - 40, color=NEG, sw=1.8))
    parts.append(text(rx1 - 25, ry1 - 48, "σ_2 · u_2", size=11.5, color=NEG, bold=True))
    parts.append(text(rx1, ry1 + 55, "Рух вільний у всіх напрямках (det(J) ≠ 0)", size=11.5, color=MUTED))

    rx2, ry2 = 740, 360
    parts.append(text(rx2, 280, "Сингулярна поза (Singularity): втрата DOF", size=13.5, bold=True, color=POS))
    parts.append('<ellipse cx="%d" cy="%d" rx="95" ry="4" fill="#fef2f2" stroke="%s" stroke-width="2.5" transform="rotate(-20 %d %d)"/>' % (rx2, ry2, POS, rx2, ry2))
    parts.append(circle(rx2, ry2, 3, fill=INK, stroke=INK))
    parts.append(arrow(rx2, ry2, rx2 + 80, ry2 - 27, color=POS, sw=2))
    parts.append(text(rx2 + 95, ry2 - 32, "σ_1", size=12, color=POS, bold=True))
    parts.append(line(rx2 - 20, ry2 - 35, rx2 + 20, ry2 + 35, color=POS, sw=1.5, dash="3,3"))
    parts.append(text(rx2 - 40, ry2 + 25, "σ_min = 0", size=12, color=POS, bold=True))
    parts.append(text(rx2, ry2 + 45, "Рух поперек сплющення НЕМОЖЛИВИЙ (q̇ → ∞)", size=11.5, color=POS, bold=True))

    b_bot, _, _ = textbox(W / 2, 445, "Маніпулятивність Йошикави: w(q) = √(det(J · Jᵀ)) = σ_1 · σ_2 · ... · σ_m  (w = 0 у точці сингулярності)", size=12.5, pad=6, fill="#f8fafc", stroke=LINE)
    parts.append(b_bot)

    return render("img/jacobian-mapping-velocities.svg", W, H, *parts)


# ── Фігура 4: Затухаючий метод найменших квадратів (DLS / Levenberg-Marquardt)
def fig_dls_singularity():
    W, H = 960, 480
    parts = []

    parts.append(text(W / 2, 32, "Поведінка біля сингулярності: Псевдоінверсія Мура-Пенроуза vs DLS", size=18, bold=True))
    parts.append(text(W / 2, 54, "регуляризація матриці Якобі запобігає вибуховому насиченню приводів", size=13, color=MUTED))

    lx, ly = 240, 240
    parts.append(text(lx, 95, "Псевдоінверсія Мура-Пенроуза (J⁺)", size=15, bold=True, color=POS))
    parts.append(text(lx, 118, "q̇ = Jᵀ · (J · Jᵀ)⁻¹ · v_cmd", size=13, color=LINE, bold=True))

    gx, gy = lx - 140, ly + 90
    gw, gh = 280, 140
    parts.append(rect(gx, gy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    parts.append(line(gx + 30, gy - 15, gx + gw - 15, gy - 15, color=LINE, sw=1.5))
    parts.append(line(gx + 30, gy - 15, gx + 30, gy - gh + 15, color=LINE, sw=1.5))
    parts.append(text(gx + gw - 25, gy - 2, "σ_min → 0", size=11, color=MUTED))
    parts.append(text(gx + 25, gy - gh + 10, "‖q̇‖", size=12, color=POS, bold=True))

    curve_pts = []
    for step in range(10, 230, 5):
        s = step / 100.0
        val = 1.0 / (s + 0.05)
        px = gx + gw - 20 - step
        py = gy - 15 - min(val * 8, gh - 25)
        curve_pts.append("%.1f,%.1f" % (px, py))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(curve_pts), POS))

    parts.append(line(gx + 30, gy - 80, gx + gw - 15, gy - 80, color="#dc2626", sw=1.5, dash="4,4"))
    parts.append(text(gx + 120, gy - 86, "Межа швидкості двигуна (q̇_max)", size=11, color="#dc2626", bold=True))

    b_mp_res, _, _ = textbox(lx, 420, "Критичний стрибок швидкості: q̇ → ∞\nЗрив сервоприводів, коливання, аварія", size=12, pad=6, fill="#fef2f2", stroke=POS, color=POS, bold=True)
    parts.append(b_mp_res)

    rx, ry = 720, 240
    parts.append(text(rx, 95, "Затухаючий метод DLS (Levenberg-Marquardt)", size=15, bold=True, color=FIELD))
    parts.append(text(rx, 118, "q̇ = Jᵀ · (J · Jᵀ + λ² · I)⁻¹ · v_cmd", size=13, color=LINE, bold=True))

    rgx, rgy = rx - 140, ry + 90
    parts.append(rect(rgx, rgy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    parts.append(line(rgx + 30, rgy - 15, rgx + gw - 15, rgy - 15, color=LINE, sw=1.5))
    parts.append(line(rgx + 30, rgy - 15, rgx + 30, rgy - gh + 15, color=LINE, sw=1.5))
    parts.append(text(rgx + gw - 25, rgy - 2, "σ_min → 0", size=11, color=MUTED))
    parts.append(text(rgx + 25, rgy - gh + 10, "‖q̇‖", size=12, color=FIELD, bold=True))

    dls_pts = []
    lam2 = 0.35
    for step in range(0, 230, 5):
        s = step / 80.0
        val = s / (s * s + lam2)
        px = rgx + gw - 20 - step
        py = rgy - 15 - min(val * 42, gh - 25)
        dls_pts.append("%.1f,%.1f" % (px, py))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(dls_pts), FIELD))

    parts.append(line(rgx + 30, rgy - 80, rgx + gw - 15, rgy - 80, color="#dc2626", sw=1.5, dash="4,4"))
    parts.append(text(rgx + 120, rgy - 86, "Межа швидкості двигуна (q̇_max)", size=11, color="#dc2626", bold=True))

    b_dls_res, _, _ = textbox(rx, 420, "Швидкість строго обмежена (‖q̇‖ < q̇_max)\nПлавний рух з контрольованою похибкою e", size=12, pad=6, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_dls_res)

    return render("img/dls-singularity-damping.svg", W, H, *parts)


if __name__ == "__main__":
    fig_dh_parameters()
    fig_geometric_ik()
    fig_jacobian_mapping()
    fig_dls_singularity()
    print("Всі фігури згенеровано успішно!")
