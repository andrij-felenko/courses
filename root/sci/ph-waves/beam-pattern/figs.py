# -*- coding: utf-8 -*-
"""Фігури до статті «Діаграма спрямованості перетворювача».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def curve(x0, W, fn, color, sw=1.6, n=720, dash=None):
    """Полілінія y=fn(t), t∈[0,1], x=x0+t·W. fn повертає піксельний y."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append("%.1f,%.1f" % (x0 + t * W, fn(t)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s"/>'
            % (color, sw, d, " ".join(pts)))


# ── Фігура 1: Геометрія далекого поля та інтерференція хвиль ──────────────────
def fig_interference_farfield():
    W, H = 880, 500

    ax_x, ax_y = 120, 250
    d_h = 220
    top_y = ax_y - d_h / 2
    bot_y = ax_y + d_h / 2

    trans = rect(ax_x - 20, top_y, 25, d_h, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=4)
    trans_lbl = text(ax_x - 8, ax_y, "Апертура D", size=14, color=NEG, anchor="middle", bold=True)

    axis = line(ax_x + 10, ax_y, ax_x + 720, ax_y, MUTED, 1.2, dash="4,4")
    axis_lbl = text(ax_x + 710, ax_y + 24, "Оптична вісь (θ = 0)", size=13, color=MUTED, anchor="end")

    theta_deg = 25.0
    theta_rad = math.radians(theta_deg)
    r_len = 680

    ray_c = line(ax_x + 5, ax_y, ax_x + 5 + r_len * math.cos(theta_rad), ax_y - r_len * math.sin(theta_rad), POS, 1.8)
    ray_t = line(ax_x + 5, top_y, ax_x + 5 + (r_len - 50) * math.cos(theta_rad), top_y - (r_len - 50) * math.sin(theta_rad), MUTED, 1.2, dash="3,3")
    ray_b = line(ax_x + 5, bot_y, ax_x + 5 + (r_len + 50) * math.cos(theta_rad), bot_y - (r_len + 50) * math.sin(theta_rad), MUTED, 1.2, dash="3,3")

    front_len = d_h * math.cos(theta_rad)
    fx2 = (ax_x + 5) + front_len * math.sin(theta_rad)
    fy2 = top_y + front_len * math.cos(theta_rad)

    front_line = line(ax_x + 5, top_y, fx2, fy2, FIELD, 2.0)
    front_lbl = text(fx2 + 30, fy2 - 10, "Хвильовий фронт", size=13, color=FIELD, anchor="start", bold=True)

    delta_line = line(fx2, fy2, ax_x + 5, bot_y, POS, 2.2)
    delta_lbl = text(ax_x + 45, bot_y + 15, "Різниця ходу Δr = D · sin(θ)", size=14, color=POS, anchor="start", bold=True)

    arc_r = 140
    arc_pts = []
    for i in range(26):
        a = math.radians(i)
        arc_pts.append("%.1f,%.1f" % (ax_x + 5 + arc_r * math.cos(a), ax_y - arc_r * math.sin(a)))
    arc_path = ('<polyline fill="none" stroke="%s" stroke-width="1.4" points="%s"/>'
                % (INK, " ".join(arc_pts)))
    theta_lbl = text(ax_x + 5 + arc_r + 15, ax_y - 20, "θ", size=16, color=INK, bold=True)

    info_box, _, _ = textbox(ax_x + 540, 410,
                             "У далекій зоні (зона Фраунгофера):\n"
                             "• При θ = 0 промені синфазні → максимуми\n"
                             "• При Δr = λ крайові елементи гасяться\n"
                             "• Перший нуль: sin(θ₀) = λ / D",
                             size=13, fill="#f4f6f8", stroke=LINE, pad=10)

    render(os.path.join(IMG, "interference-farfield.svg"), W, H,
           trans, trans_lbl, axis, axis_lbl, ray_c, ray_t, ray_b,
           front_line, front_lbl, delta_line, delta_lbl, arc_path, theta_lbl, info_box,
           title="Геометрія далекого поля та інтерференція хвиль")


# ── Фігура 2: Порівняння діаграм спрямованості ────────────────────────────────
def fig_polar_pattern_compare():
    W, H = 880, 520

    x0, wide = 80, 360
    yc = 380
    h_db = 280

    grid = []
    grid.append(line(x0, yc, x0 + wide, yc, MUTED, 1.0))
    grid.append(line(x0, yc - h_db, x0 + wide, yc - h_db, MUTED, 1.0))
    grid.append(line(x0 + wide / 2, yc, x0 + wide / 2, yc - h_db - 20, MUTED, 1.0, dash="3,3"))

    grid.append(text(x0, yc + 22, "-90°", size=12, color=MUTED, anchor="middle"))
    grid.append(text(x0 + wide / 4, yc + 22, "-45°", size=12, color=MUTED, anchor="middle"))
    grid.append(text(x0 + wide / 2, yc + 22, "0°", size=12, color=MUTED, anchor="middle", bold=True))
    grid.append(text(x0 + 3 * wide / 4, yc + 22, "+45°", size=12, color=MUTED, anchor="middle"))
    grid.append(text(x0 + wide, yc + 22, "+90°", size=12, color=MUTED, anchor="middle"))

    grid.append(text(x0 - 10, yc - h_db + 5, "0 dB", size=12, color=MUTED, anchor="end"))
    grid.append(text(x0 - 10, yc - h_db * 0.75 + 5, "-10 dB", size=12, color=MUTED, anchor="end"))
    grid.append(text(x0 - 10, yc - h_db * 0.5 + 5, "-20 dB", size=12, color=MUTED, anchor="end"))
    grid.append(text(x0 - 10, yc - h_db * 0.25 + 5, "-30 dB", size=12, color=MUTED, anchor="end"))
    grid.append(text(x0 - 10, yc + 5, "-40 dB", size=12, color=MUTED, anchor="end"))

    def sinc_db(t):
        th = (t - 0.5) * math.pi
        u = 4.5 * math.sin(th)
        val = abs(math.sin(u) / u) if abs(u) > 1e-5 else 1.0
        db = 20 * math.log10(max(val, 1e-2))
        norm = max(0.0, min(1.0, (db + 40.0) / 40.0))
        return yc - norm * h_db

    def j1_db(t):
        th = (t - 0.5) * math.pi
        v = 4.5 * math.sin(th)
        v2 = v * v
        if abs(v) < 1e-4:
            val = 1.0
        else:
            val = abs(2.0 * (math.sin(v) / (v * v) - math.cos(v) / v)) if abs(v) > 0.1 else abs(1.0 - v2 / 8.0)
        db = 20 * math.log10(max(val, 1e-2))
        norm = max(0.0, min(1.0, (db + 40.0) / 40.0))
        return yc - norm * h_db

    rect_curve = curve(x0, wide, sinc_db, NEG, 1.8)
    circ_curve = curve(x0, wide, j1_db, POS, 1.8)

    cap_left = text(x0 + wide / 2, 70, "Амплітуда R(θ) в дБ", size=15, color=INK, anchor="middle", bold=True)
    leg_rect = text(x0 + 40, 95, "Прямокутне (sinc): бічна -13.5 dB", size=13, color=NEG, anchor="start", bold=True)
    leg_circ = text(x0 + 40, 115, "Кругове (2J₁/v): бічна -17.6 dB", size=13, color=POS, anchor="start", bold=True)

    pcx, pcy, pr = 660, 260, 170

    pol_grid = []
    pol_grid.append(circle(pcx, pcy, pr, fill="none", stroke=MUTED, sw=1.2))
    pol_grid.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="2,3"/>' % (pcx, pcy, pr * 0.75, MUTED))
    pol_grid.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="2,3"/>' % (pcx, pcy, pr * 0.5, MUTED))
    pol_grid.append(line(pcx - pr - 20, pcy, pcx + pr + 20, pcy, MUTED, 1.0, dash="3,3"))
    pol_grid.append(line(pcx, pcy - pr - 20, pcx, pcy + pr + 20, MUTED, 1.0, dash="3,3"))

    pol_grid.append(text(pcx, pcy - pr - 8, "0° (Головна пелюстка)", size=13, color=INK, anchor="middle", bold=True))
    pol_grid.append(text(pcx + pr + 10, pcy + 4, "90°", size=12, color=MUTED, anchor="start"))
    pol_grid.append(text(pcx - pr - 10, pcy + 4, "-90°", size=12, color=MUTED, anchor="end"))

    pts_pol = []
    for i in range(361):
        ang_deg = i - 180
        th = math.radians(ang_deg)
        u = 4.5 * math.sin(th)
        val = abs(math.sin(u) / u) if abs(u) > 1e-5 else 1.0
        db = 20 * math.log10(max(val, 1e-2))
        r_norm = max(0.0, (db + 40.0) / 40.0) * pr
        px = pcx + r_norm * math.sin(th)
        py = pcy - r_norm * math.cos(th)
        pts_pol.append("%.1f,%.1f" % (px, py))

    pol_shape = ('<polygon fill="#eaf0fd" stroke="%s" stroke-width="1.8" points="%s"/>'
                 % (NEG, " ".join(pts_pol)))

    lbl_main = text(pcx, pcy - pr * 0.5, "Головний промінь", size=13, color=NEG, anchor="middle", bold=True)
    lbl_side = text(pcx + pr * 0.45, pcy - pr * 0.25, "Бічна пелюстка", size=12, color=POS, anchor="start", bold=True)
    arr_side = arrow(pcx + pr * 0.42, pcy - pr * 0.25, pcx + pr * 0.22, pcy - pr * 0.32, POS, 1.4)

    render(os.path.join(IMG, "polar-pattern-compare.svg"), W, H,
           "\n".join(grid), rect_curve, circ_curve, cap_left, leg_rect, leg_circ,
           "\n".join(pol_grid), pol_shape, lbl_main, lbl_side, arr_side,
           title="Діаграма спрямованості у полярних та логарифмічних координатах")


# ── Фігура 3: Вплив співвідношення D / lambda ─────────────────────────────────
def fig_ratio_d_lambda():
    W, H = 880, 420

    w_p, h_p = 250, 300
    y_p = 80

    panels = []

    xa = 40
    panels.append(rect(xa, y_p, w_p, h_p, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    panels.append(text(xa + w_p / 2, y_p + 25, "А: D ≪ λ (D = 0.3λ)", size=14, color=INK, anchor="middle", bold=True))

    cx_a, cy_a = xa + w_p / 2, y_p + h_p / 2 + 10
    for r_val in [30, 60, 90]:
        panels.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (cx_a, cy_a, r_val, FIELD))
    panels.append(circle(cx_a, cy_a, 8, fill=NEG, stroke=NEG))

    panels.append(textbox(xa + w_p / 2, y_p + h_p - 30,
                          "Ізотропне випромінювання\nПромінь широкий (360°)\nБічні пелюстки відсутні",
                          size=12, fill="#f4f6f8", stroke=MUTED, pad=6)[0])

    xb = 315
    panels.append(rect(xb, y_p, w_p, h_p, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    panels.append(text(xb + w_p / 2, y_p + 25, "Б: D ≈ λ (D = 1.5λ)", size=14, color=INK, anchor="middle", bold=True))

    cx_b, cy_b = xb + w_p / 2, y_p + h_p / 2 + 10
    pts_b = []
    for i in range(181):
        th = math.radians(i - 90)
        u = 1.5 * math.pi * math.sin(th)
        val = abs(math.sin(u) / u) if abs(u) > 1e-5 else 1.0
        r_norm = val * 105
        px = cx_b + r_norm * math.sin(th)
        py = cy_b - r_norm * math.cos(th)
        pts_b.append("%.1f,%.1f" % (px, py))
    panels.append('<polygon fill="#eaf0fd" stroke="%s" stroke-width="1.8" points="%s"/>' % (NEG, " ".join(pts_b)))
    panels.append(circle(cx_b, cy_b, 10, fill=NEG, stroke=NEG))

    panels.append(textbox(xb + w_p / 2, y_p + h_p - 30,
                          "Помірно вузький промінь\nКут променя θ₃dB ≈ 35°\nМалі бічні пелюстки",
                          size=12, fill="#f4f6f8", stroke=MUTED, pad=6)[0])

    xc = 590
    panels.append(rect(xc, y_p, w_p, h_p, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    panels.append(text(xc + w_p / 2, y_p + 25, "В: D ≫ λ (D = 6λ)", size=14, color=INK, anchor="middle", bold=True))

    cx_c, cy_c = xc + w_p / 2, y_p + h_p / 2 + 10
    pts_c = []
    for i in range(181):
        th = math.radians(i - 90)
        u = 6.0 * math.sin(th)
        val = abs(math.sin(u) / u) if abs(u) > 1e-5 else 1.0
        r_norm = val * 105
        px = cx_c + r_norm * math.sin(th)
        py = cy_c - r_norm * math.cos(th)
        pts_c.append("%.1f,%.1f" % (px, py))
    panels.append('<polygon fill="#fdecea" stroke="%s" stroke-width="1.8" points="%s"/>' % (POS, " ".join(pts_c)))
    panels.append(rect(cx_c - 20, cy_c - 4, 40, 8, fill=POS, stroke=POS))

    panels.append(textbox(xc + w_p / 2, y_p + h_p - 30,
                          "Гострий промінь-голка\nКут променя θ₃dB ≈ 8°\nРозвинена структура пелюсток",
                          size=12, fill="#f4f6f8", stroke=MUTED, pad=6)[0])

    render(os.path.join(IMG, "ratio-d-lambda.svg"), W, H,
           "\n".join(panels),
           title="Залежність спрямованості від співвідношення розміру апертури D та довжини хвилі λ")


# ── Фігура 4: Фазована решітка та електронне сканування ───────────────────────
def fig_phased_array_steering():
    W, H = 880, 500

    n_elem = 8
    d_step = 55
    x_start = 240
    y_arr = 360

    elems = []
    elems.append(line(x_start - 30, y_arr, x_start + (n_elem - 1) * d_step + 30, y_arr, MUTED, 1.5))

    theta_s_deg = 30.0
    theta_s_rad = math.radians(theta_s_deg)

    for i in range(n_elem):
        ex = x_start + i * d_step
        elems.append(rect(ex - 15, y_arr - 10, 30, 20, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
        elems.append(text(ex, y_arr + 4, str(i + 1), size=12, color=NEG, anchor="middle", bold=True))

        elems.append(line(ex, y_arr - 10, ex, y_arr - 30, POS, 1.5))
        elems.append(text(ex, y_arr - 36, "Δφ%d" % i, size=11, color=POS, anchor="middle"))

        ray_len = 220
        rx2 = ex + ray_len * math.sin(theta_s_rad)
        ry2 = (y_arr - 45) - ray_len * math.cos(theta_s_rad)
        elems.append(line(ex, y_arr - 45, rx2, ry2, FIELD, 1.2, dash="3,3"))

    fx1, fy1 = x_start, y_arr - 80
    fx2 = fx1 + (n_elem - 1) * d_step
    fy2 = fy1 - (n_elem - 1) * d_step * math.tan(theta_s_rad)
    elems.append(line(fx1 - 20, fy1 + 10, fx2 + 20, fy2 - 10, FIELD, 2.5))
    elems.append(text(fx2 + 40, fy2 - 10, "Сформований фронт", size=14, color=FIELD, anchor="start", bold=True))

    steer_arrow = arrow(x_start + 180, y_arr - 120, x_start + 180 + 100 * math.sin(theta_s_rad), (y_arr - 120) - 100 * math.cos(theta_s_rad), POS, 2.0)
    steer_lbl = text(x_start + 260, y_arr - 200, "Напрямок сканування θₛ = 30°", size=14, color=POS, anchor="start", bold=True)

    box_grating, _, _ = textbox(190, 130,
                                "Умова відсутності ґратчастих часток:\n"
                                "Крок елементів: d ≤ λ / (1 + |sin θₛ|)\n"
                                "При d > λ/2 виникають паразитні\n"
                                "побічні максимуми (Grating Lobes)",
                                size=12, fill="#fdecea", stroke=POS, pad=8)

    render(os.path.join(IMG, "phased-array-steering.svg"), W, H,
           "\n".join(elems), steer_arrow, steer_lbl, box_grating,
           title="Фазована решітка: електронне сканування та формування фронту")


if __name__ == "__main__":
    fig_interference_farfield()
    fig_polar_pattern_compare()
    fig_ratio_d_lambda()
    fig_phased_array_steering()
    print("Усі фігури згенеровано успішно.")
