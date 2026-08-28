# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_l1_guidance_geometry():
    """
    Геометрія алгоритму нелінійного наведення L1 (L1 Nonlinear Guidance):
    позиція апарата p, вектор швидкості V, відрізок маршруту WA->WB,
    точка прицілювання p_ref на лінії на відстані L1 від p,
    кут eta між вектором швидкості V та вектором L1,
    дуга кола радіуса R, центр кривини C, вектор бічного прискорення a_s.
    """
    W, H = 840, 560
    frags = []

    # Точки сегмента шляху WA -> WB
    wax, way = 80.0, 360.0
    wbx, wby = 760.0, 360.0

    # Позиція апарата p (нижче лінії, тобто зміщений убік)
    px, py = 240.0, 470.0

    # Точка прицілювання p_ref на лінії шляху на відстані L1
    L1 = 260.0
    dx_ref = math.sqrt(L1 * L1 - (py - way) * (py - way))
    ref_x = px + dx_ref
    ref_y = way

    # Вектор швидкості V апарата (спрямований під кутом до лінії)
    v_len = 110.0
    gamma = math.radians(24.0)  # кут вектора швидкості до горизонту (вгору)
    vx = px + v_len * math.cos(gamma)
    vy = py - v_len * math.sin(gamma)

    # Вектор L1 від p до p_ref
    l1_angle = math.atan2(ref_y - py, ref_x - px)
    eta_rad = gamma + abs(l1_angle)

    # Радіус дуги кола R = L1 / (2 * sin(eta))
    R = L1 / (2.0 * math.sin(eta_rad))

    # Центр дуги кола C: перпендикулярно до вектора швидкості V
    perp_vx = -math.sin(gamma)
    perp_vy = -math.cos(gamma)
    cx = px + R * perp_vx
    cy = py + R * perp_vy

    # 1. Сітка / фоновий прямокутник
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # 2. Лінія шляху WA -> WB
    frags.append(line(40, way, W - 40, way, color="#cbd5e1", sw=2, dash="6 4"))
    frags.append(line(wax, way, wbx, wby, color=FIELD, sw=3.5))
    frags.append(arrow(wax, way, wbx, wby, color=FIELD, sw=2.5))
    frags.append(text(160, way - 14, "Лінія шляху W_A → W_B", size=13, color=FIELD, bold=True))

    # 3. Проєкція позиції p на лінію шляху та відхилення cross-track e_ct
    pproj_x, pproj_y = px, way
    frags.append(line(px, py, pproj_x, pproj_y, color=POS, sw=1.8, dash="4 4"))
    frags.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.5"/>' %
                 (pproj_x + 12, pproj_y, pproj_x + 12, pproj_y + 12, pproj_x, pproj_y + 12, POS))
    frags.append(text(px - 14, (py + pproj_y) / 2 + 4, "d = e_ct", size=13, color=POS, bold=True, anchor="end"))

    # 4. Дуга кола наведення від p до p_ref
    arc_d = ("M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" % (px, py, R, R, ref_x, ref_y))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>' % (arc_d, NEG))

    # Радіус-вектори від C до p і до p_ref
    frags.append(line(cx, cy, px, py, color="#94a3b8", sw=1.2, dash="3 3"))
    frags.append(line(cx, cy, ref_x, ref_y, color="#94a3b8", sw=1.2, dash="3 3"))
    mid_rx = (cx + px) / 2
    mid_ry = (cy + py) / 2
    frags.append(text(mid_rx - 16, mid_ry - 10, "R = L_1 / (2·sin η)", size=12, color=MUTED, italic=True))

    # Центр кола C
    frags.append(circle(cx, cy, 4, fill=NEG, stroke=INK, sw=1))
    frags.append(text(cx, cy - 10, "Центр кривини C", size=11, color=MUTED, italic=True))

    # 5. Вектор прицілювання L1 (від p до p_ref)
    frags.append(arrow(px, py, ref_x, ref_y, color=INK, sw=2.5))
    mid_l1_x = (px + ref_x) / 2
    mid_l1_y = (py + ref_y) / 2
    frags.append(text(mid_l1_x + 18, mid_l1_y + 24, "L_1 (вектор випередження)", size=13, color=INK, bold=True))

    # 6. Вектор швидкості V
    frags.append(arrow(px, py, vx, vy, color="#059669", sw=3.0))
    frags.append(text(vx + 14, vy - 6, "V (швидкість)", size=13, color="#059669", bold=True))

    # 7. Кут eta (дуга між вектором V та вектором L1)
    arc_r = 50.0
    ang_v = -gamma
    a1x = px + arc_r * math.cos(ang_v)
    a1y = py + arc_r * math.sin(ang_v)
    a2x = px + arc_r * math.cos(l1_angle)
    a2y = py + arc_r * math.sin(l1_angle)
    frags.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (a1x, a1y, arc_r, arc_r, a2x, a2y, POS))
    mid_eta_ang = (ang_v + l1_angle) / 2
    frags.append(text(px + (arc_r + 16) * math.cos(mid_eta_ang), py + (arc_r + 16) * math.sin(mid_eta_ang),
                      "η", size=15, color=POS, bold=True))

    # 8. Вектор бічного прискорення a_s (перпендикулярно до V)
    as_len = 65.0
    asx = px + as_len * perp_vx
    asy = py + as_len * perp_vy
    frags.append(arrow(px, py, asx, asy, color=POS, sw=2.6))
    frags.append(text(asx - 12, asy - 12, "a_s = 2·(V²/L_1)·sin(η)", size=13, color=POS, bold=True, anchor="end"))

    # 9. Точки та підписи
    frags.append(circle(wax, way, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(wax, way + 22, "W_A", size=13, color=INK, bold=True))

    frags.append(circle(wbx, wby, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(wbx, wby + 22, "W_B", size=13, color=INK, bold=True))

    frags.append(circle(px, py, 7, fill="#ef4444", stroke=INK, sw=2))
    frags.append(text(px - 14, py + 22, "p (позиція БПЛА)", size=13, color=INK, bold=True, anchor="end"))

    frags.append(circle(ref_x, ref_y, 6, fill="#f59e0b", stroke=INK, sw=2))
    frags.append(text(ref_x + 10, ref_y - 16, "p_ref (точка прицілювання)", size=12, color=INK, bold=True, anchor="start"))

    info_box, _, _ = textbox(W / 2, 515,
                             "L1-наведення: доцентрове прискорення a_s викривляє траєкторію в дугу кола,\n"
                             "яка проходить через позицію p під поточним вектором V та досягає точки p_ref.",
                             size=12, pad=8, fill="#f8fafc", stroke="#cbd5e1", color=INK)
    frags.append(info_box)

    render(os.path.join(OUT, "l1-guidance-geometry.svg"), W, H, *frags)


def fig_vector_field_guidance():
    """
    Векторне поле наведення на лінію (Vector Field Guidance):
    демонстрація розподілу бажаних векторів швидкості залежно від бічного відхилення d.
    Вдалині від осі вектори спрямовані під кутом захоплення chi_entry = 45..60 градусів.
    Поблизу осі поле плавно переходить у паралельний рух, з плавною траєкторією повернення.
    """
    W, H = 840, 520
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    cy = 240.0
    frags.append(line(60, cy, W - 60, cy, color=FIELD, sw=3.5))
    frags.append(arrow(60, cy, W - 60, cy, color=FIELD, sw=2.5))
    frags.append(text(140, cy - 14, "Лінія шляху (d = 0)", size=14, color=FIELD, bold=True))

    d_trans = 90.0
    frags.append(line(60, cy - d_trans, W - 60, cy - d_trans, color="#e2e8f0", sw=1.5, dash="4 4"))
    frags.append(line(60, cy + d_trans, W - 60, cy + d_trans, color="#e2e8f0", sw=1.5, dash="4 4"))
    frags.append(text(W - 70, cy - d_trans - 8, "+d_trans (зона насичення)", size=11, color=MUTED, anchor="end"))
    frags.append(text(W - 70, cy + d_trans + 18, "−d_trans (зона насичення)", size=11, color=MUTED, anchor="end"))

    chi_inf = math.radians(52.0)
    k_vf = 0.022

    # Малюємо сітку векторів векторного поля
    for y_offset in [-160.0, -120.0, -80.0, -40.0, 0.0, 40.0, 80.0, 120.0, 160.0]:
        y_pos = cy + y_offset
        d_val = -y_offset
        ang = chi_inf * (2.0 / math.pi) * math.atan(k_vf * d_val)
        vlen = 34.0
        # починаємо стрілки з x = 160, щоб звільнити місце для стартової плашки
        for x_pos in range(160, 740, 70):
            vx = x_pos + vlen * math.cos(ang)
            vy = y_pos - vlen * math.sin(ang)
            col = "#3b82f6" if abs(y_offset) > 10 else "#10b981"
            frags.append(arrow(x_pos, y_pos, vx, vy, color=col, sw=1.6))

    traj_pts = []
    curr_x, curr_y = 70.0, cy + 150.0
    dt = 1.2
    speed = 22.0
    for _ in range(36):
        traj_pts.append((curr_x, curr_y))
        d_val = -(curr_y - cy)
        ang = chi_inf * (2.0 / math.pi) * math.atan(k_vf * d_val)
        curr_x += speed * math.cos(ang) * dt * 0.45
        curr_y -= speed * math.sin(ang) * dt * 0.45

    traj_path = "M " + " L ".join("%.1f %.1f" % (pt[0], pt[1]) for pt in traj_pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (traj_path, POS))

    p0 = traj_pts[0]
    frags.append(circle(p0[0], p0[1], 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(p0[0], p0[1] + 24, "Старт (d = +150 м)", size=12, color=POS, bold=True, anchor="middle"))

    mid_idx = 10
    frags.append(circle(traj_pts[mid_idx][0], traj_pts[mid_idx][1], 4, fill=POS, stroke=INK, sw=1))
    frags.append(text(traj_pts[mid_idx][0] + 16, traj_pts[mid_idx][1] - 14,
                      "Кут входу χ_entry ≈ 50°", size=11, color=POS, italic=True))

    last_p = traj_pts[-1]
    frags.append(circle(last_p[0], last_p[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(last_p[0] - 10, last_p[1] - 18, "Асимптотичний вихід на лінію", size=12, color=FIELD, bold=True, anchor="end"))

    info_box, _, _ = textbox(W - 220, 68,
                             "Закон ведення векторним полем:\n"
                             "χ_cmd(d) = χ_path − χ_inf · (2/π) · arctg(k_vf · d)\n"
                             "• Велике d: апарат іде під сталим кутом χ_inf\n"
                             "• Мале d: експоненційне затухання без перерегулювання",
                             size=11, pad=8, fill="#f8fafc", stroke="#94a3b8", color=INK)
    frags.append(info_box)

    render(os.path.join(OUT, "vector-field-guidance.svg"), W, H, *frags)


def fig_crab_angle_wind_drift():
    """
    Трикутник швидкостей та кут зносу (Crab Angle / Wind Drift Triangle):
    повітряна швидкість V_a вздовж курсу літака psi,
    вектор вітру V_w,
    результуюча шляхова швидкість V_g строго вздовж лінії шляху chi,
    кут зносу beta_w = chi - psi.
    """
    W, H = 840, 520
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    path_y = 280.0
    frags.append(line(60, path_y, W - 60, path_y, color=FIELD, sw=3.0, dash="8 4"))
    frags.append(arrow(60, path_y, W - 60, path_y, color=FIELD, sw=2.5))
    frags.append(text(150, path_y - 14, "Бажана лінія шляху (шляховий курс χ)", size=13, color=FIELD, bold=True))

    ac_x = 260.0
    ac_y = path_y

    vg_len = 280.0
    vg_x = ac_x + vg_len
    vg_y = ac_y

    beta_deg = 22.0
    beta_rad = math.radians(beta_deg)
    va_len = 302.0
    va_x = ac_x + va_len * math.cos(beta_rad)
    va_y = ac_y - va_len * math.sin(beta_rad)

    frags.append(arrow(ac_x, ac_y, va_x, va_y, color=POS, sw=3.0))
    mid_vax = (ac_x + va_x) / 2
    mid_vay = (ac_y + va_y) / 2
    frags.append(text(mid_vax - 18, mid_vay - 14, "V_a (повітряна швидкість, курс ψ)", size=13, color=POS, bold=True))

    frags.append(arrow(va_x, va_y, vg_x, vg_y, color="#0284c7", sw=3.0))
    mid_vwx = (va_x + vg_x) / 2
    mid_vwy = (va_y + vg_y) / 2
    frags.append(text(mid_vwx + 18, mid_vwy, "V_w (боковий вітер)", size=13, color="#0284c7", bold=True, anchor="start"))

    frags.append(arrow(ac_x, ac_y, vg_x, vg_y, color=FIELD, sw=3.5))
    frags.append(text(ac_x + vg_len * 0.45, ac_y + 24, "V_g = V_a + V_w (шляхова швидкість)", size=13, color=FIELD, bold=True))

    arc_r = 90.0
    a1x = ac_x + arc_r
    a1y = ac_y
    a2x = ac_x + arc_r * math.cos(beta_rad)
    a2y = ac_y - arc_r * math.sin(beta_rad)
    frags.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (a1x, a1y, arc_r, arc_r, a2x, a2y, INK))
    mid_b_ang = beta_rad / 2
    frags.append(text(ac_x + (arc_r + 18) * math.cos(mid_b_ang), ac_y - (arc_r + 18) * math.sin(mid_b_ang),
                      "β_w", size=15, color=INK, bold=True))
    frags.append(text(ac_x + (arc_r + 34) * math.cos(mid_b_ang), ac_y - (arc_r + 34) * math.sin(mid_b_ang) + 16,
                      "(кут зносу / crab angle)", size=11, color=MUTED, italic=True))

    frags.append(circle(ac_x, ac_y, 7, fill="#ef4444", stroke=INK, sw=2))

    info_box, _, _ = textbox(W / 2, 440,
                             "Компенсація бокового вітру методом кута зносу (Crabbing):\n"
                             "• Ніс літака розвертається проти вітру на кут: β_w = arcsin(V_w_cross / V_a)\n"
                             "• Повна рівновага: V_g = V_a · cos(β_w) + V_w_along спрямована строго вздовж лінії шляху\n"
                             "• Інтегральний контур (ILOS / L1-integrator) оцінює β_w без прямого датчика вітру",
                             size=12, pad=10, fill="#f8fafc", stroke="#cbd5e1", color=INK)
    frags.append(info_box)

    render(os.path.join(OUT, "crab-angle-wind-drift.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_l1_guidance_geometry()
    fig_vector_field_guidance()
    fig_crab_angle_wind_drift()
    print("All figures generated successfully.")
