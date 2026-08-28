# -*- coding: utf-8 -*-
"""Фігури до теми «Крива момент–оберти мотора».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Лінійна електромеханічна характеристика DC/BLDC мотора ───────────────
def fig_linear_torque_speed_curve():
    W, H = 760, 480
    f = [text(W / 2, 28, "Механічна характеристика двигуна постійного струму та корисна потужність",
              size=16, bold=True)]

    ox, oy = 110, 400
    ax_w, ax_h = 580, 320

    # Осі координат
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "крутний момент  M  (Н·м)  →", size=12, color=INK))
    f.append(mtext(ox - 70, oy - ax_h / 2 - 10, ["кутова швидкість", "ω  (рад/с або RPM)", "та потужність P"],
                   size=11, color=INK, lh=1.2))

    # Характерні точки на осі X (момент)
    f.append(line(ox + ax_w * 0.5, oy, ox + ax_w * 0.5, oy + 5, color=INK, sw=1.4))
    f.append(text(ox + ax_w * 0.5, oy + 20, "½ M_stall", size=11, color=MUTED))

    f.append(line(ox + ax_w * 0.9, oy, ox + ax_w * 0.9, oy + 5, color=INK, sw=1.4))
    f.append(text(ox + ax_w * 0.9, oy + 20, "M_stall  (стопор)", size=11, color=POS, bold=True))

    # Характерні точки на осі Y (швидкість)
    f.append(line(ox - 5, oy - ax_h * 0.9, ox, oy - ax_h * 0.9, color=INK, sw=1.4))
    f.append(text(ox - 14, oy - ax_h * 0.9 + 4, "ω_0  (холості)", size=11, color=NEG, anchor="end", bold=True))

    f.append(line(ox - 5, oy - ax_h * 0.45, ox, oy - ax_h * 0.45, color=INK, sw=1.4))
    f.append(text(ox - 14, oy - ax_h * 0.45 + 4, "½ ω_0", size=11, color=MUTED, anchor="end"))

    # Лінія механічної характеристики: ω(M)
    x_w0, y_w0 = ox, oy - ax_h * 0.9
    x_ms, y_ms = ox + ax_w * 0.9, oy
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>'
             % (x_w0, y_w0, x_ms, y_ms, NEG))
    f.append(text(ox + ax_w * 0.62, oy - ax_h * 0.40, "ω(M) = ω_0 − (R / (k_e·k_t)) · M",
                  size=12, color=NEG, bold=True))

    # Крива механічної потужності: P_mech = M * ω (парабола)
    pts_p = []
    N = 50
    for i in range(N + 1):
        m_norm = (i / float(N)) * 0.9
        w_norm = 0.9 * (1.0 - m_norm / 0.9)
        p_val = (m_norm * w_norm) / (0.45 * 0.45) * 0.75
        px = ox + m_norm * ax_w
        py = oy - p_val * ax_h
        pts_p.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>'
             % (" ".join(pts_p), FIELD))

    # Максимум потужності P_max
    px_mid = ox + ax_w * 0.45
    py_mid = oy - 0.75 * ax_h
    f.append(circle(px_mid, py_mid, 5, fill=BG, stroke=FIELD, sw=2.4))
    f.append(line(px_mid, oy, px_mid, py_mid, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text(px_mid, py_mid - 12, "P_max = ¼ · M_stall · ω_0", size=12, color=FIELD, bold=True))

    # Робоча точка під навантаженням
    op_m = 0.22
    op_w = 0.9 * (1.0 - op_m / 0.9)
    x_op = ox + op_m * ax_w
    y_op = oy - op_w * ax_h
    f.append(circle(x_op, y_op, 5.5, fill=BG, stroke=POS, sw=2.5))
    f.append(line(x_op, oy, x_op, y_op, color=POS, sw=1.2, dash="4,4"))
    f.append(line(ox, y_op, x_op, y_op, color=POS, sw=1.2, dash="4,4"))

    b, _, _ = textbox(x_op + 100, y_op - 20, "Робоча точка (M_op, ω_op)\nПеретин із M_навант.",
                      size=11, fill="#fdecea", stroke=POS, bold=True)
    f.append(b)

    render(os.path.join(IMG, "linear-torque-speed-curve.svg"), W, H, *f)


# ── 2. Зони роботи: тривалий режим S1 та пікове перевантаження ───────────────
def fig_operating_zones():
    W, H = 760, 480
    f = [text(W / 2, 28, "Зони роботи електродвигуна: неперервний режим S1 та пікова область",
              size=16, bold=True)]

    ox, oy = 110, 400
    ax_w, ax_h = 580, 320

    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "крутний момент  M  →", size=12, color=INK))
    f.append(mtext(ox - 70, oy - ax_h / 2 - 10, ["кутова", "швидкість", "ω  →"], size=11, color=INK, lh=1.2))

    m_nom_x = ox + ax_w * 0.28
    m_stall_x = ox + ax_w * 0.88
    w0_y = oy - ax_h * 0.85

    # Заливка зони S1 (Continuous operating area - зелена)
    pts_s1 = [
        "%.1f,%.1f" % (ox, oy),
        "%.1f,%.1f" % (ox, w0_y),
        "%.1f,%.1f" % (m_nom_x, oy - ax_h * 0.85 * (1.0 - 0.28 / 0.88)),
        "%.1f,%.1f" % (m_nom_x, oy)
    ]
    f.append('<polygon points="%s" fill="#e8f8f0" stroke="none"/>' % " ".join(pts_s1))

    # Заливка пікової зони (Intermittent operating area - жовта/помаранчева)
    pts_peak = [
        "%.1f,%.1f" % (m_nom_x, oy),
        "%.1f,%.1f" % (m_nom_x, oy - ax_h * 0.85 * (1.0 - 0.28 / 0.88)),
        "%.1f,%.1f" % (m_stall_x, oy),
    ]
    f.append('<polygon points="%s" fill="#fdf4e8" stroke="none"/>' % " ".join(pts_peak))

    # Лінія механічної характеристики
    f.append(line(ox, w0_y, m_stall_x, oy, color=NEG, sw=2.5))

    # Межа номінального струму / теплова межа M_N
    f.append(line(m_nom_x, oy, m_nom_x, oy - ax_h * 0.85 * (1.0 - 0.28 / 0.88), color=FIELD, sw=2, dash="5,4"))
    f.append(circle(m_nom_x, oy, 4, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(m_nom_x, oy + 20, "M_N  (номінальний S1)", size=11, color=FIELD, bold=True))

    f.append(circle(m_stall_x, oy, 4, fill=POS, stroke=INK, sw=1.2))
    f.append(text(m_stall_x, oy + 20, "M_stall  (піковий)", size=11, color=POS, bold=True))

    # Підписи зон
    b1, _, _ = textbox(ox + ax_w * 0.14, oy - ax_h * 0.35,
                       "Зона S1 (Continuous)\nТривала безпечна робота\nI ≤ I_ном, нагрів стабільний",
                       size=11, fill="#ffffff", stroke=FIELD, bold=True)
    f.append(b1)

    b2, _, _ = textbox(ox + ax_w * 0.52, oy - ax_h * 0.22,
                       "Пікова зона (Intermittent)\nКороткочасні прискорення\nt < τ_теплова, I_RMS ≤ I_ном",
                       size=11, fill="#ffffff", stroke="#d97706", bold=True)
    f.append(b2)

    # Межа максимальних механічних обертів ω_max
    w_max_y = oy - ax_h * 0.95
    f.append(line(ox, w_max_y, ox + ax_w * 0.6, w_max_y, color=POS, sw=1.4, dash="6,4"))
    f.append(text(ox + ax_w * 0.32, w_max_y - 8, "ω_max — механічна межа підшипників та ротора",
                  size=11, color=POS, bold=True))

    render(os.path.join(IMG, "operating-zones-s1-peak.svg"), W, H, *f)


# ── 3. Вплив напруги живлення та ШІМ на механічну характеристику ──────────────
def fig_pwm_voltage_family():
    W, H = 760, 480
    f = [text(W / 2, 28, "Зсув характеристики при зміні напруги живлення та коефіцієнта заповнення ШІМ",
              size=16, bold=True)]

    ox, oy = 110, 400
    ax_w, ax_h = 580, 320

    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "крутний момент  M  →", size=12, color=INK))
    f.append(mtext(ox - 70, oy - ax_h / 2 - 10, ["кутова", "швидкість", "ω  →"], size=11, color=INK, lh=1.2))

    duties = [
        (1.0, "100% ШІМ (U_ном)", NEG),
        (0.75, "75% ШІМ", "#2563eb"),
        (0.50, "50% ШІМ", "#0284c7"),
        (0.25, "25% ШІМ", "#0d9488"),
    ]

    base_w0_h = 0.88 * ax_h
    base_ms_w = 0.85 * ax_w

    # Крива навантаження (вентиляторне M_load ∝ ω²)
    pts_load = []
    for i in range(41):
        fr = i / 40.0
        w_curr = fr * base_w0_h
        m_curr = (0.06 + 0.32 * (fr * fr)) * base_ms_w
        pts_load.append("%.1f,%.1f" % (ox + m_curr, oy - w_curr))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>'
             % (" ".join(pts_load), POS))
    f.append(text(ox + 0.44 * base_ms_w, oy - base_w0_h - 10, "Крива навантаження M_навант(ω)",
                  size=11.5, color=POS, bold=True))

    for duty, lab, col in duties:
        x0, y0 = ox, oy - duty * base_w0_h
        x1, y1 = ox + duty * base_ms_w, oy
        f.append(line(x0, y0, x1, y1, color=col, sw=2.2))
        f.append(circle(x0, y0, 3.5, fill=col, stroke=INK, sw=1))
        f.append(text(x0 + 8, y0 - 6, "%.0f%%" % (duty * 100), size=10.5, color=col, bold=True, anchor="start"))

    # Пояснювальний блок
    b, _, _ = textbox(ox + ax_w * 0.68, oy - ax_h * 0.65,
                      "Властивість ШІМ:\n"
                      "• Швидкість ω_0 зміщується ∝ D\n"
                      "• Нахил прямої незмінний:\n"
                      "  Δω/ΔM = −R / (k_e·k_t)\n"
                      "• Робочі точки опускаються вниз",
                      size=11, fill="#f8fafc", stroke=MUTED, min_w=200)
    f.append(b)

    render(os.path.join(IMG, "pwm-voltage-family.svg"), W, H, *f)


# ── 4. Трансформація механічної характеристики редуктором ────────────────────
def fig_gearbox_load_matching():
    W, H = 760, 480
    f = [text(W / 2, 28, "Трансформація механічної характеристики редуктором (передавальне число i)",
              size=16, bold=True)]

    ox, oy = 110, 400
    ax_w, ax_h = 580, 320

    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "крутний момент  M  (Н·м)  →", size=12, color=INK))
    f.append(mtext(ox - 70, oy - ax_h / 2 - 10, ["кутова", "швидкість", "ω  (рад/с)  →"], size=11, color=INK, lh=1.2))

    # Голий мотор: висока швидкість, малий момент
    m_motor_stall = ox + ax_w * 0.20
    w_motor_0 = oy - ax_h * 0.88
    f.append(line(ox, w_motor_0, m_motor_stall, oy, color=NEG, sw=2.5))
    f.append(circle(m_motor_stall, oy, 4, fill=NEG, stroke=INK, sw=1))
    f.append(circle(ox, w_motor_0, 4, fill=NEG, stroke=INK, sw=1))

    b_m, _, _ = textbox(ox + ax_w * 0.18, oy - ax_h * 0.72,
                        "Голий мотор:\nω_0 велика, M_stall малий\n(швидкий, але слабкий)",
                        size=11, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b_m)

    # Вихід редуктора (наприклад i = 4, η = 0.85): швидкість / i, момент * (i * η)
    m_gear_stall = ox + ax_w * 0.84
    w_gear_0 = oy - (ax_h * 0.88) / 4.0
    f.append(line(ox, w_gear_0, m_gear_stall, oy, color=FIELD, sw=2.8))
    f.append(circle(m_gear_stall, oy, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(circle(ox, w_gear_0, 4, fill=FIELD, stroke=INK, sw=1))

    b_g, _, _ = textbox(ox + ax_w * 0.65, oy - ax_h * 0.65,
                        "Після редуктора (передача i = 4, ККД η = 85%):\n"
                        "• Оберти: ω_вих = ω_мотор / i\n"
                        "• Момент: M_вих = M_мотор · i · η\n"
                        "• Потужність: P_вих = P_мотор · η",
                        size=11, fill="#e8f8f0", stroke=FIELD, bold=True)
    f.append(b_g)

    # Позначка трансформації біля стрілки
    f.append(arrow(ox + ax_w * 0.15, oy - ax_h * 0.40, ox + ax_w * 0.40, oy - ax_h * 0.18,
                   color=MUTED, sw=2.0))
    f.append(text(ox + ax_w * 0.26, oy - ax_h * 0.24, "редуктор i", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, "gearbox-load-matching.svg"), W, H, *f)


if __name__ == "__main__":
    fig_linear_torque_speed_curve()
    fig_operating_zones()
    fig_pwm_voltage_family()
    fig_gearbox_load_matching()
    print("OK: 4 figures ->", IMG)
