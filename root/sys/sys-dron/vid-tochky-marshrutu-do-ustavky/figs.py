# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. fig-problem: Проблема прямолінійних відрізків і зріз кута ───────────────
def fig_problem():
    W, H = 760, 440
    p = []

    # Точки маршруту
    w1x, w1y = 90, 360
    w2x, w2y = 380, 100
    w3x, w3y = 670, 360

    # Прямолінійний маршрут (чорний пунктир)
    p.append(line(w1x, w1y, w2x, w2y, color=LINE, sw=2.0, dash="6 6"))
    p.append(line(w2x, w2y, w3x, w3y, color=LINE, sw=2.0, dash="6 6"))

    # Варіант 1: Переліт / занос при спробі пролетіти крізь точку на швидкості (червоний)
    p.append('<path d="M 90,360 Q 360,118 420,75 C 470,40 500,130 430,175 C 380,210 440,225 490,255 L 670,360" '
             'fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 4"/>' % POS)

    # Варіант 2: Зрізання кута / вписана дуга (зелена суцільна лінія)
    # Дотичні точки
    t1x, t1y = 280, 210
    t2x, t2y = 480, 210
    p.append('<path d="M 90,360 L %d,%d Q %d,%d %d,%d L 670,360" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (t1x, t1y, w2x, w2y + 40, t2x, t2y, FIELD))

    # Сфера/радіус досягнення (acceptance radius) навколо W2 (синій пунктир)
    r_acc = 115
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 4"/>'
             % (w2x, w2y, r_acc, NEG))

    # Вершини
    p.append(circle(w1x, w1y, 5.5, fill=INK, stroke=INK, sw=1))
    p.append(circle(w2x, w2y, 6.5, fill=POS, stroke=POS, sw=1))
    p.append(circle(w3x, w3y, 5.5, fill=INK, stroke=INK, sw=1))

    p.append(text(w1x - 10, w1y + 20, "WP₁ (Старт)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(w2x, w2y - 18, "WP₂ (Кут зламу)", size=13, color=POS, anchor="middle", bold=True))
    p.append(text(w3x - 20, w3y + 20, "WP₃ (Ціль)", size=12, color=INK, anchor="start", bold=True))

    # Точки входу й виходу зі скруглення
    p.append(circle(t1x, t1y, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(t2x, t2y, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(t1x - 14, t1y - 12, "Вхід у скруглення", size=11, color=FIELD, anchor="end", bold=True))
    p.append(text(t2x + 14, t2y - 12, "Вихід на відрізок", size=11, color=FIELD, anchor="start", bold=True))

    # Підписи зон і варіантів
    p.append(text(w2x + 85, w2y - 75, "R_acc (радіус досягнення)", size=11, color=NEG, anchor="start", italic=True))
    p.append(line(w2x, w2y, w2x + 80, w2y - 70, color=NEG, sw=1.2))

    tb1, _, _ = textbox(560, 95, "Переліт (overshoot):\nспроба тримати пряму\nбез гальмування",
                        size=11, fill="#fdf2f2", stroke=POS, sw=1.2, color=POS, bold=True)
    p.append(tb1)

    tb2, _, _ = textbox(190, 105, "Згладжена траєкторія:\nзрізання кута без зупинки,\nобмежене прискорення",
                        size=11, fill="#f2f9f4", stroke=FIELD, sw=1.2, color=FIELD, bold=True)
    p.append(tb2)

    render(os.path.join(OUT, "fig-problem.svg"), W, H, *p,
           title="Проблема прямолінійного прольоту точок та згладжування кута")


# ── 2. fig-fillet-geometry: Геометрія вписаного скруглення (Fillet Arc) ───────
def fig_fillet_geometry():
    W, H = 760, 480
    p = []

    # Геометричні координати
    wx, wy = 380, 80

    theta_deg = 80.0
    theta_rad = math.radians(theta_deg)
    half_theta = theta_rad / 2.0

    ang1 = math.pi + half_theta   # промінь від W назад-вліво
    ang2 = -half_theta            # промінь від W назад-вправо

    L = 340.0
    p1x = wx + L * math.cos(ang1)
    p1y = wy - L * math.sin(ang1)
    p2x = wx + L * math.cos(ang2)
    p2y = wy - L * math.sin(ang2)

    p.append(line(p1x, p1y, wx, wy, color=LINE, sw=2.0))
    p.append(line(wx, wy, p2x, p2y, color=LINE, sw=2.0))

    R = 170.0
    d = R * math.tan(half_theta)

    dist_WO = R / math.sin(half_theta)
    ox = wx
    oy = wy + dist_WO

    t1x = wx + d * math.cos(ang1)
    t1y = wy - d * math.sin(ang1)
    t2x = wx + d * math.cos(ang2)
    t2y = wy - d * math.sin(ang2)

    arc_pts = []
    a_start = math.atan2(oy - t1y, t1x - ox)
    a_end = math.atan2(oy - t2y, t2x - ox)
    steps = 60
    for i in range(steps + 1):
        a = a_start + (a_end - a_start) * (i / float(steps))
        arc_pts.append("%.1f,%.1f" % (ox + R * math.cos(a), oy - R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.5"/>'
             % (" ".join(arc_pts), FIELD))

    p.append(line(ox, oy, t1x, t1y, color=NEG, sw=1.6, dash="4 4"))
    p.append(line(ox, oy, t2x, t2y, color=NEG, sw=1.6, dash="4 4"))
    p.append(circle(ox, oy, 4.5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(ox, oy + 20, "Центр дуги O", size=12, color=NEG, anchor="middle", bold=True))

    p.append(text((ox + t1x) / 2 - 18, (oy + t1y) / 2 + 6, "R", size=13, color=NEG, bold=True, italic=True))
    p.append(text((ox + t2x) / 2 + 18, (oy + t2y) / 2 + 6, "R", size=13, color=NEG, bold=True, italic=True))

    p.append(circle(t1x, t1y, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(t2x, t2y, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(wx, wy, 5, fill=POS, stroke=POS, sw=1))

    p.append(text(t1x - 14, t1y - 12, "T₁ (початок дуги)", size=11, color=FIELD, anchor="end", bold=True))
    p.append(text(t2x + 14, t2y - 12, "T₂ (кінець дуги)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(wx, wy - 14, "Вершина W (кут зламу)", size=12, color=POS, anchor="middle", bold=True))

    p.append(line(t1x - 12, t1y - 8, wx - 12, wy - 8, color=POS, sw=1.4))
    p.append(text((t1x + wx) / 2 - 28, (t1y + wy) / 2 - 18, "d = R·tan(θ/2)", size=11, color=POS, bold=True))

    apex_y = oy - R
    p.append(line(wx, wy, wx, apex_y, color=MUTED, sw=1.5, dash="3 3"))
    p.append(text(wx + 10, (wy + apex_y) / 2, "h", size=12, color=MUTED, bold=True, italic=True))

    p.append(text(wx + 45, wy + 35, "θ (кут)", size=12, color=INK, italic=True))

    fb, _, _ = textbox(610, 110, "d = R · tan(θ / 2)\nh = R · (1/cos(θ/2) − 1)\na_lat = v² / R ≤ a_max",
                       size=12, bold=True, fill="#fcfbf7", stroke=INK, sw=1.5, pad=10)
    p.append(fb)

    render(os.path.join(OUT, "fig-fillet-geometry.svg"), W, H, *p,
           title="Геометрична побудова кругового скруглення між відрізками")


# ── 3. fig-velocity-profile: Профілювання швидкості (трапеція проти S-кривої) ──
def fig_velocity_profile():
    W, H = 760, 480
    p = []

    gx, gy, gw, gh = 90, 210, 610, 150

    p.append(line(gx, gy, gx + gw, gy, color=LINE, sw=1.8))
    p.append(line(gx, gy, gx, gy - gh, color=LINE, sw=1.8))
    p.append(arrow(gx + gw, gy, gx + gw + 25, gy, color=LINE, sw=1.8))
    p.append(arrow(gx, gy - gh, gx, gy - gh - 20, color=LINE, sw=1.8))
    p.append(text(gx + gw + 30, gy + 4, "t (час)", size=11, color=INK, anchor="start"))
    p.append(text(gx - 10, gy - gh - 15, "v(t)", size=12, color=INK, anchor="end", bold=True))

    v_max_y = gy - 130
    v_corner_y = gy - 55
    p.append(line(gx, v_max_y, gx + gw, v_max_y, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(gx, v_corner_y, gx + gw, v_corner_y, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(gx - 8, v_max_y + 4, "v_max (крейсерська)", size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 8, v_corner_y + 4, "v_corner (на куті)", size=10, color=MUTED, anchor="end"))

    p.append('<polyline points="90,210 180,80 280,80 360,155 420,155 490,80 540,80 610,210" '
             'fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>' % NEG)

    s_curve = (
        "M 90,210 "
        "C 130,210 140,80 180,80 "
        "L 280,80 "
        "C 315,80 325,155 360,155 "
        "L 420,155 "
        "C 450,155 460,80 490,80 "
        "L 540,80 "
        "C 575,80 585,210 620,210"
    )
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (s_curve, FIELD))

    gy2, gh2 = 430, 160
    a_zero_y = 355
    p.append(line(gx, a_zero_y, gx + gw, a_zero_y, color=MUTED, sw=1.2))
    p.append(line(gx, gy2, gx, gy2 - gh2, color=LINE, sw=1.8))
    p.append(arrow(gx + gw, a_zero_y, gx + gw + 25, a_zero_y, color=LINE, sw=1.8))
    p.append(text(gx - 10, gy2 - gh2 + 10, "a(t)", size=12, color=INK, anchor="end", bold=True))
    p.append(text(gx - 6, a_zero_y + 4, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 6, a_zero_y - 45, "+a_max", size=10, color=POS, anchor="end"))
    p.append(text(gx - 6, a_zero_y + 45, "−a_max", size=10, color=POS, anchor="end"))

    p.append('<polyline points="90,355 90,310 180,310 180,355 280,355 280,400 360,400 360,355 '
             '420,355 420,310 490,310 490,355 540,355 540,400 610,400 610,355" '
             'fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 4"/>' % NEG)

    a_scurve = (
        "M 90,355 "
        "L 115,310 L 155,310 L 180,355 "
        "L 280,355 "
        "L 300,400 L 340,400 L 360,355 "
        "L 420,355 "
        "L 440,310 L 470,310 L 490,355 "
        "L 540,355 "
        "L 560,400 L 600,400 L 620,355"
    )
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (a_scurve, FIELD))

    p.append(line(460, 30, 500, 30, color=FIELD, sw=3.0))
    p.append(text(510, 34, "S-крива (обмежений ривок j_max, плавні переходи)", size=11, color=INK, anchor="start", bold=True))

    p.append(line(460, 50, 500, 50, color=NEG, sw=1.8, dash="5 4"))
    p.append(text(510, 54, "Трапецоїдний профіль (стрибки прискорення, удари)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fig-velocity-profile.svg"), W, H, *p,
           title="Профілювання швидкості та прискорення: трапеція проти S-кривої")


# ── 4. fig-setpoint-cascade: Архітектура від місії до уставки в каскадному регуляторі ──
def fig_setpoint_cascade():
    W, H = 760, 420
    p = []

    tb1, _, _ = textbox(110, 100, "Список точок місії\n(WP₁, WP₂, WP₃...)\nНизька частота (0.1–1 Гц)",
                        size=11, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True, pad=10)
    p.append(tb1)

    p.append(arrow(195, 100, 245, 100, color=INK, sw=2.0))
    p.append(text(220, 88, "точки", size=10, color=MUTED, italic=True))

    tb2, _, _ = textbox(360, 100, "Генератор траєкторії\n• Зрізання кутів (дуги / Безьє)\n• S-криві швидкості\n• Висока частота (50–250 Гц)",
                        size=11, fill="#f2f9f4", stroke=FIELD, sw=2.0, color=FIELD, bold=True, pad=12)
    p.append(tb2)

    p.append(arrow(475, 100, 555, 100, color=POS, sw=2.4))
    p.append(text(515, 82, "Уставка щотакту:", size=11, color=POS, bold=True))
    p.append(text(515, 98, "p_sp (позиція)", size=10, color=INK))
    p.append(text(515, 114, "v_ff (швидкість)", size=10, color=INK))
    p.append(text(515, 130, "a_ff (прискорення)", size=10, color=INK))

    tb3, _, _ = textbox(650, 100, "Контур позиції\n(P-регулятор)\nv_target = v_ff + Kp·e_pos",
                        size=11, fill="#fdfaf2", stroke=INK, sw=1.5, bold=True, pad=10)
    p.append(tb3)

    p.append(arrow(650, 150, 650, 210, color=INK, sw=2.0))
    p.append(text(665, 180, "v_target", size=10, color=INK, italic=True))

    tb4, _, _ = textbox(650, 260, "Контур швидкості\n(PID + a_ff feedforward)\na_target = a_ff + PID(e_vel)",
                        size=11, fill="#fdfaf2", stroke=INK, sw=1.5, bold=True, pad=10)
    p.append(tb4)

    p.append(arrow(550, 260, 450, 260, color=INK, sw=2.0))
    p.append(text(500, 248, "a_target + g", size=10, color=INK, italic=True))

    tb5, _, _ = textbox(340, 260, "Перерахунок у тягу й кути\nRoll, Pitch = f(a_target, yaw)\nThrust = m · ||a_target − g||",
                        size=11, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True, pad=10)
    p.append(tb5)

    p.append(arrow(230, 260, 160, 260, color=INK, sw=2.0))

    tb6, _, _ = textbox(90, 260, "Кутові швидкості\nй мікшер моторів\n(500–1000 Гц)",
                        size=11, fill="#f4f6f8", stroke=LINE, sw=1.5, bold=True, pad=10)
    p.append(tb6)

    tb_ff, _, _ = textbox(380, 365, "Чому потрібен прямий канал (Feedforward):\nПряма передача v_ff та a_ff ліквідує фазове запізнення в каскаді,\nдозволяючи дрону летіти точно по гладкій кривій без відставання на динаміці.",
                          size=11, fill="#f2f9f4", stroke=FIELD, sw=1.4, color=FIELD, bold=True, pad=10)
    p.append(tb_ff)

    render(os.path.join(OUT, "fig-setpoint-cascade.svg"), W, H, *p,
           title="Місце генератора траєкторії в каскадному контурі керування")


# ── 5. fig-bezier-blend: Неперервність кривини (C0, C1 проти C2) ──────────────
def fig_bezier_blend():
    W, H = 760, 440
    p = []

    col_w = 215
    y_top = 70
    h_box = 320

    # Стовпчик 1: C0
    c1x = 110
    p.append(rect(c1x - col_w/2, y_top, col_w, h_box, fill="#fffaf9", stroke=POS, sw=1.5))
    p.append(text(c1x, y_top + 26, "Прямолінійний злам (C⁰)", size=12, color=POS, anchor="middle", bold=True))

    p.append(line(c1x - 70, y_top + 130, c1x, y_top + 65, color=LINE, sw=2.2))
    p.append(line(c1x, y_top + 65, c1x + 70, y_top + 130, color=LINE, sw=2.2))
    p.append(circle(c1x, y_top + 65, 4.5, fill=POS, stroke=POS, sw=1))

    p.append(line(c1x - 80, y_top + 230, c1x + 80, y_top + 230, color=MUTED, sw=1.0))
    p.append(line(c1x, y_top + 230, c1x, y_top + 170, color=POS, sw=2.0))
    p.append(arrow(c1x, y_top + 180, c1x, y_top + 165, color=POS, sw=2.0))
    p.append(text(c1x + 8, y_top + 175, "κ → ∞", size=11, color=POS, bold=True))
    p.append(text(c1x, y_top + 248, "Кривина κ(s)", size=10, color=MUTED, anchor="middle"))

    p.append(mtext(c1x, y_top + 275, ["• Нескінченне бічне a_lat", "• Вимагає повної зупинки", "• Або некерований занос"], size=10, color=INK, anchor="middle"))

    # Стовпчик 2: C1
    c2x = 380
    p.append(rect(c2x - col_w/2, y_top, col_w, h_box, fill="#f8fafc", stroke=NEG, sw=1.5))
    p.append(text(c2x, y_top + 26, "Дуга кола (C¹)", size=12, color=NEG, anchor="middle", bold=True))

    p.append('<path d="M %d,%d L %d,%d Q %d,%d %d,%d L %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (c2x - 70, y_top + 130, c2x - 30, y_top + 92, c2x, y_top + 70, c2x + 30, y_top + 92, c2x + 70, y_top + 130, LINE))
    p.append(circle(c2x - 30, y_top + 92, 3.5, fill=NEG, stroke=NEG, sw=1))
    p.append(circle(c2x + 30, y_top + 92, 3.5, fill=NEG, stroke=NEG, sw=1))

    p.append(line(c2x - 80, y_top + 230, c2x + 80, y_top + 230, color=MUTED, sw=1.0))
    p.append('<polyline points="%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.0"/>'
             % (c2x - 80, y_top + 230, c2x - 30, y_top + 230, c2x - 30, y_top + 180,
                c2x + 30, y_top + 180, c2x + 30, y_top + 230, c2x + 80, y_top + 230, NEG))
    p.append(text(c2x, y_top + 172, "κ = 1/R (стала)", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(c2x, y_top + 248, "Стрибок кривини на стиках", size=10, color=MUTED, anchor="middle"))

    p.append(mtext(c2x, y_top + 275, ["• Неперервна швидкість", "• Стрибок прискорення Δa", "• Нескінченний ривок j"], size=10, color=INK, anchor="middle"))

    # Стовпчик 3: C2
    c3x = 650
    p.append(rect(c3x - col_w/2, y_top, col_w, h_box, fill="#f2f9f4", stroke=FIELD, sw=1.8))
    p.append(text(c3x, y_top + 26, "Крива Безьє / Клотоїда (C²)", size=12, color=FIELD, anchor="middle", bold=True))

    p.append('<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (c3x - 70, y_top + 130, c3x - 10, y_top + 60, c3x + 10, y_top + 60, c3x + 70, y_top + 130, FIELD))
    p.append(circle(c3x - 70, y_top + 130, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(c3x + 70, y_top + 130, 3.5, fill=FIELD, stroke=FIELD, sw=1))

    p.append(line(c3x - 80, y_top + 230, c3x + 80, y_top + 230, color=MUTED, sw=1.0))
    p.append('<path d="M %d,%d C %d,%d %d,%d %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (c3x - 80, y_top + 230, c3x - 40, y_top + 230, c3x - 20, y_top + 180, c3x, y_top + 180,
                c3x + 20, y_top + 180, c3x + 40, y_top + 230, c3x + 80, y_top + 230, FIELD))
    p.append(text(c3x, y_top + 172, "κ(s) гладка", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(c3x, y_top + 248, "Нульова кривина на кінцях", size=10, color=MUTED, anchor="middle"))

    p.append(mtext(c3x, y_top + 275, ["• Гладке наростання a_lat", "• Обмежений ривок j_max", "• Без вібрацій рами й IMU"], size=10, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "fig-bezier-blend.svg"), W, H, *p,
           title="Порівняння порядків гладкості: C0, C1 та C2 скруглення")


if __name__ == "__main__":
    fig_problem()
    fig_fillet_geometry()
    fig_velocity_profile()
    fig_setpoint_cascade()
    fig_bezier_blend()
    print("All figures generated successfully.")
