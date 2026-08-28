# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_cross_track_geometry():
    """
    Геометрія похибки відхилення: відрізок WA->WB, поточна позиція апарата p,
    вектор зміщення a = p - WA, вектор шляху b = WB - WA, проєкція p_proj,
    поперечна похибка e_ct (зі знаком), поздовжня відстань s (along-track),
    базисні вектори t_hat (дотичний) та n_hat (нормальний).
    """
    W, H = 800, 520
    frags = []

    # Точки сегмента шляху
    wax, way = 120, 420
    wbx, wby = 680, 140

    dx = wbx - wax
    dy = wby - way
    L = math.hypot(dx, dy)
    tx = dx / L
    ty = dy / L
    nx = -ty
    ny = tx

    # Позиція апарата p: праворуч від лінії (якщо дивитися від WA до WB)
    # Рухаємося від WA на відстань s = 0.52 * L уздовж t_hat і відхиляємося на e_ct = +95 px уздовж n_hat
    s = 0.52 * L
    ect = 95.0

    ppx = wax + s * tx
    ppy = way + s * ty

    px = ppx + ect * nx
    py = ppy + ect * ny

    # 1. Сітка / допоміжні координатні лінії
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # 2. Лінія шляху WA -> WB (товста зелена)
    frags.append(line(wax - 40 * tx, way - 40 * ty, wbx + 40 * tx, wby + 40 * ty, color="#cbd5e1", sw=2, dash="6 4"))
    frags.append(line(wax, way, wbx, wby, color=FIELD, sw=3.5))

    # 3. Вектор шляху b = WB - WA (стрілка)
    frags.append(arrow(wax, way, wbx, wby, color=FIELD, sw=2.5))
    frags.append(text(wax + 0.28 * dx - 18 * nx, way + 0.28 * dy - 18 * ny, "b = W_B − W_A  (лінія шляху)", size=13, color=FIELD, bold=True, anchor="middle"))

    # 4. Одиничні вектори t_hat та n_hat у точці WA
    vlen = 65.0
    frags.append(arrow(wax, way, wax + vlen * tx, way + vlen * ty, color=INK, sw=2.2))
    frags.append(text(wax + (vlen + 14) * tx, way + (vlen + 14) * ty, "t̂", size=14, color=INK, bold=True, italic=True))

    frags.append(arrow(wax, way, wax + vlen * nx, way + vlen * ny, color=POS, sw=2.2))
    frags.append(text(wax + (vlen + 14) * nx, way + (vlen + 14) * ny, "n̂", size=14, color=POS, bold=True, italic=True))

    # 5. Вектор a = p - WA (синя стрілка)
    frags.append(arrow(wax, way, px, py, color=NEG, sw=2.0))
    mid_ax = (wax + px) / 2
    mid_ay = (way + py) / 2
    frags.append(text(mid_ax - 20, mid_ay + 24, "a = p − W_A", size=13, color=NEG, bold=True, italic=True, anchor="middle"))

    # 6. Проєкція: пунктир від p до p_proj (нормаль)
    frags.append(line(px, py, ppx, ppy, color=POS, sw=2.0, dash="5 4"))

    # Прямий кут у точці p_proj
    sq = 14.0
    c1x, c1y = ppx + sq * nx, ppy + sq * ny
    c2x, c2y = ppx + sq * nx - sq * tx, ppy + sq * ny - sq * ty
    c3x, c3y = ppx - sq * tx, ppy - sq * ty
    frags.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.5"/>' %
                 (c1x, c1y, c2x, c2y, c3x, c3y, POS))

    # 7. Поперечна похибка e_ct (виділена червоним, праворуч від пунктиру)
    mid_ect_x = (px + ppx) / 2
    mid_ect_y = (py + ppy) / 2
    frags.append(text(mid_ect_x + 26, mid_ect_y + 6, "e_ct = a × t̂", size=14, color=POS, bold=True, anchor="start"))
    frags.append(text(mid_ect_x + 26, mid_ect_y + 24, "(cross-track > 0)", size=11, color=POS, italic=True, anchor="start"))

    # 8. Поздовжня відстань s (along-track) вздовж лінії
    # Виносна лінія під відрізком
    off_s = 38.0
    sx1, sy1 = wax - off_s * nx, way - off_s * ny
    sx2, sy2 = ppx - off_s * nx, ppy - off_s * ny
    frags.append(line(wax, way, sx1, sy1, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(line(ppx, ppy, sx2, sy2, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(arrow(sx1, sy1, sx2, sy2, color=MUTED, sw=1.5))
    frags.append(arrow(sx2, sy2, sx1, sy1, color=MUTED, sw=1.5))
    mid_sx = (sx1 + sx2) / 2
    mid_sy = (sy1 + sy2) / 2
    frags.append(text(mid_sx - 16 * nx, mid_sy - 16 * ny, "s = a · t̂  (along-track distance)", size=12, color=INK, bold=True, anchor="middle"))

    # 9. Точки та підписи
    # Точка WA
    frags.append(circle(wax, way, 6, fill="#ffffff", stroke=FIELD, sw=3))
    frags.append(text(wax - 12, way + 26, "W_A (початок відрізка)", size=13, color=INK, bold=True, anchor="middle"))

    # Точка WB
    frags.append(circle(wbx, wby, 6, fill="#ffffff", stroke=FIELD, sw=3))
    frags.append(text(wbx + 10, wby - 18, "W_B (цільова точка)", size=13, color=INK, bold=True, anchor="middle"))

    # Точка проєкції p_proj
    frags.append(circle(ppx, ppy, 5, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(ppx - 22, ppy - 16, "p_proj", size=12, color=POS, bold=True, italic=True))

    # Поточна позиція апарата p
    frags.append(circle(px, py, 7, fill=NEG, stroke="#ffffff", sw=2.5))
    frags.append(text(px + 14, py - 12, "p (позиція дрона)", size=13, color=NEG, bold=True))

    # Вектор курсу/швидкості апарата
    heading_ang = math.atan2(dy, dx) - 0.45
    vx = px + 70 * math.cos(heading_ang)
    vy = py + 70 * math.sin(heading_ang)
    frags.append(arrow(px, py, vx, vy, color="#8b5cf6", sw=2.5))
    frags.append(text(vx + 12, vy + 4, "v (вектор швидкості)", size=12, color="#8b5cf6", bold=True))

    render(os.path.join(OUT, "cross-track-geometry.svg"), W, H, *frags)


def fig_carrot_vs_pure_pursuit():
    """
    Порівняння двох підходів до цілевказівки:
    Ліворуч — Carrot Chaser (морквина на зміщенні Delta попереду проєкції p_proj).
    Праворуч — Pure Pursuit (перетин кола радіуса L_d з лінією шляху, дуга радіуса R з кривиною kappa).
    """
    W, H = 820, 440
    frags = []

    # 1. Рамка та розподільча лінія
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))
    frags.append(line(W / 2, 20, W / 2, H - 20, color="#e2e8f0", sw=1.5, dash="6 4"))

    # ------------------ ЛІВА ЧАСТИНА: Carrot Chaser ------------------
    cx_l = W / 4
    frags.append(text(cx_l, 40, "Carrot Chaser (гонитва за морквиною)", size=15, color=INK, bold=True))

    # Лінія шляху (горизонтальна для простоти сприйняття)
    py_path_l = 260
    frags.append(line(40, py_path_l, 380, py_path_l, color=FIELD, sw=3))
    frags.append(arrow(40, py_path_l, 390, py_path_l, color=FIELD, sw=2.5))
    frags.append(text(210, py_path_l + 24, "лінія шляху (W_A → W_B)", size=11, color=FIELD, italic=True))

    # Апарат
    px_l, py_l = 110, 130
    frags.append(circle(px_l, py_l, 6, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(text(px_l, py_l - 16, "p (дрон)", size=12, color=NEG, bold=True))

    # Проєкція
    pproj_x_l = px_l
    frags.append(line(px_l, py_l, pproj_x_l, py_path_l, color=POS, sw=1.8, dash="4 3"))
    frags.append(circle(pproj_x_l, py_path_l, 4, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(pproj_x_l - 24, py_path_l - 10, "p_proj", size=11, color=POS, bold=True))
    frags.append(text(px_l - 26, (py_l + py_path_l) / 2, "e_ct", size=12, color=POS, bold=True))

    # Морквина p_carrot = p_proj + Delta
    delta_l = 150
    pcarrot_x = pproj_x_l + delta_l
    pcarrot_y = py_path_l

    # Відрізок Delta
    frags.append(line(pproj_x_l, py_path_l - 25, pcarrot_x, py_path_l - 25, color=MUTED, sw=1.5))
    frags.append(arrow(pproj_x_l, py_path_l - 25, pcarrot_x, py_path_l - 25, color=MUTED, sw=1.5))
    frags.append(arrow(pcarrot_x, py_path_l - 25, pproj_x_l, py_path_l - 25, color=MUTED, sw=1.5))
    frags.append(text((pproj_x_l + pcarrot_x) / 2, py_path_l - 33, "упередження Δ", size=11, color=MUTED, bold=True))

    # Точка морквини
    frags.append(circle(pcarrot_x, pcarrot_y, 7, fill="#e67e22", stroke="#ffffff", sw=2))
    frags.append(text(pcarrot_x + 12, pcarrot_y + 20, "p_carrot", size=12, color="#e67e22", bold=True))

    # Вектор націлювання на морквину
    frags.append(arrow(px_l, py_l, pcarrot_x, pcarrot_y, color="#e67e22", sw=2.5))
    frags.append(text((px_l + pcarrot_x) / 2 - 18, (py_l + pcarrot_y) / 2 - 10, "напрям на ціль χ_cmd", size=12, color="#e67e22", bold=True))

    # Пояснювальний блок знизу
    frags.append(rect(40, 320, 330, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(205, 345, "Ціль:  p_carrot = p_proj + Δ · t̂", size=12, color=INK, bold=True))
    frags.append(text(205, 368, "Керування:  курс на ціль χ_cmd", size=12, color=INK))
    frags.append(text(205, 388, "Динаміка:  не враховує радіус повороту", size=11, color=MUTED, italic=True))

    # ------------------ ПРАВА ЧАСТИНА: Pure Pursuit ------------------
    cx_r = 3 * W / 4
    frags.append(text(cx_r, 40, "Pure Pursuit (чиста погоня за дугою)", size=15, color=INK, bold=True))

    py_path_r = 260
    frags.append(line(430, py_path_r, 770, py_path_r, color=FIELD, sw=3))
    frags.append(arrow(430, py_path_r, 780, py_path_r, color=FIELD, sw=2.5))
    frags.append(text(600, py_path_r + 24, "лінія шляху (W_A → W_B)", size=11, color=FIELD, italic=True))

    # Апарат
    px_r, py_r = 500, 130
    frags.append(circle(px_r, py_r, 6, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(text(px_r - 26, py_r - 12, "p (дрон)", size=12, color=NEG, bold=True))

    # Курс апарата (напрямок вздовж)
    heading_r = 0.15
    frags.append(arrow(px_r, py_r, px_r + 60 * math.cos(heading_r), py_r + 60 * math.sin(heading_r), color=INK, sw=2.0))
    frags.append(text(px_r + 70, py_r + 4, "курс ψ", size=11, color=INK, italic=True))

    # Коло випередження L_d навколо апарата
    ld_r = 185.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="4 4"/>' % (px_r, py_r, ld_r))

    # Точка перетину кола з прямою шляху (y = py_path_r)
    # (x - px_r)^2 + (py_path_r - py_r)^2 = L_d^2
    dy_r = py_path_r - py_r
    dx_r = math.sqrt(ld_r * ld_r - dy_r * dy_r)
    ptarget_x = px_r + dx_r
    ptarget_y = py_path_r

    # Хорда L_d (лінія погляду на ціль)
    frags.append(line(px_r, py_r, ptarget_x, ptarget_y, color=NEG, sw=2.0, dash="5 3"))
    frags.append(text((px_r + ptarget_x) / 2 + 10, (py_r + ptarget_y) / 2 - 12, "L_d (радіус огляду)", size=11, color=NEG, bold=True))

    # Цільова точка
    frags.append(circle(ptarget_x, ptarget_y, 7, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(ptarget_x + 12, ptarget_y + 20, "p_target", size=12, color=FIELD, bold=True))

    # Дуга кола між дроном та ціллю (траєкторія руху)
    # Геометрія дуги: дотична в p має кут heading_r, проходить через ptarget
    # Кут між курсом і хордою eta:
    chord_angle = math.atan2(ptarget_y - py_r, ptarget_x - px_r)
    eta = chord_angle - heading_r
    R_arc = ld_r / (2.0 * math.sin(eta))

    # Центр кола дуги
    arc_center_x = px_r - R_arc * math.sin(heading_r)
    arc_center_y = py_r + R_arc * math.cos(heading_r)

    # Малюємо дугу
    start_ang = math.atan2(py_r - arc_center_y, px_r - arc_center_x)
    end_ang = math.atan2(ptarget_y - arc_center_y, ptarget_x - arc_center_x)
    arc_pts = []
    for i in range(51):
        th = start_ang + (end_ang - start_ang) * (i / 50.0)
        arc_pts.append("%.1f,%.1f" % (arc_center_x + R_arc * math.cos(th), arc_center_y + R_arc * math.sin(th)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' %
                 (" ".join(arc_pts), "#8b5cf6"))
    frags.append(text(px_r + 45, py_r + 75, "дуга кривини κ", size=12, color="#8b5cf6", bold=True))

    # Пояснювальний блок знизу
    frags.append(rect(430, 320, 350, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(605, 345, "Кривина:  κ = 2 · sin(η) / L_d", size=12, color=INK, bold=True))
    frags.append(text(605, 368, "Керування:  прискорення a_y = v² · κ", size=12, color=INK))
    frags.append(text(605, 388, "Динаміка:  гладкий вхід без перерегулювання", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "carrot-vs-pure-pursuit.svg"), W, H, *frags)


def fig_los_vector_field():
    """
    Векторне поле наведення LOS (Line-of-Sight Guidance):
    Показує стрілки поля швидкостей під різними кутами, що плавно сходяться до лінії шляху,
    трикутник наведення з кутом упередження Delta_los, кут корекції chi_cross = atan(-e_ct / Delta_los)
    та вплив кута зносу вітром (crab angle beta_w).
    """
    W, H = 840, 500
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # Центральна горизонтальна лінія шляху WA -> WB
    path_y = 250
    frags.append(line(50, path_y, 790, path_y, color=FIELD, sw=3.5))
    frags.append(arrow(50, path_y, 800, path_y, color=FIELD, sw=2.5))
    frags.append(text(120, path_y - 12, "Лінія шляху  (χ_F = 0°)", size=13, color=FIELD, bold=True))

    delta_los = 140.0

    # 1. Сітка векторного поля LOS
    grid_xs = [80, 160, 240, 320, 400, 480, 560, 640, 720]
    grid_ys = [70, 120, 170, 210, 290, 330, 380, 430]

    for gx in grid_xs:
        for gy in grid_ys:
            ect_local = gy - path_y
            chi_cross = math.atan2(-ect_local, delta_los)
            arrow_len = 26.0
            ax2 = gx + arrow_len * math.cos(chi_cross)
            ay2 = gy + arrow_len * math.sin(chi_cross)
            mag = min(1.0, abs(ect_local) / 180.0)
            col = "#3b82f6" if mag > 0.4 else "#10b981"
            frags.append(arrow(gx, gy, ax2, ay2, color=col, sw=1.4))

    # 2. Окремий детальний трикутник наведення для вибраної позиції дрона
    drone_x = 420
    drone_y = 110

    # Позиція дрона
    frags.append(circle(drone_x, drone_y, 7, fill=POS, stroke="#ffffff", sw=2.5))
    frags.append(text(drone_x - 14, drone_y - 14, "p (позиція дрона)", size=13, color=POS, bold=True, anchor="end"))

    # Проєкція на лінію шляху
    proj_x = drone_x
    proj_y = path_y
    frags.append(line(drone_x, drone_y, proj_x, proj_y, color=POS, sw=2.0, dash="5 4"))
    frags.append(circle(proj_x, proj_y, 5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(proj_x - 16, proj_y + 20, "p_proj", size=12, color=POS, bold=True, italic=True))
    frags.append(text(drone_x - 12, (drone_y + proj_y) / 2, "e_ct", size=13, color=POS, bold=True, anchor="end"))

    # Точка LOS випередження на лінії шляху: p_los = p_proj + Delta_los
    los_x = proj_x + delta_los
    los_y = path_y

    # Відрізок Delta_los на осі шляху
    frags.append(line(proj_x, proj_y + 14, los_x, proj_y + 14, color=NEG, sw=2.0))
    frags.append(arrow(proj_x, proj_y + 14, los_x, proj_y + 14, color=NEG, sw=2.0))
    frags.append(arrow(los_x, proj_y + 14, proj_x, proj_y + 14, color=NEG, sw=2.0))
    frags.append(text((proj_x + los_x) / 2, proj_y + 32, "дистанція випередження Δ_los", size=12, color=NEG, bold=True))

    # Точка p_los
    frags.append(circle(los_x, los_y, 6, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(text(los_x + 10, los_y - 12, "p_los", size=13, color=NEG, bold=True))

    # Вектор націлювання (гіпотенуза трикутника наведення)
    frags.append(line(drone_x, drone_y, los_x, los_y, color=INK, sw=2.2, dash="6 3"))

    # Вектор заданої шляхової швидкості v_cmd вздовж лінії наведення
    cmd_ang = math.atan2(los_y - drone_y, los_x - drone_x)
    vcmd_len = 110.0
    vcmd_x = drone_x + vcmd_len * math.cos(cmd_ang)
    vcmd_y = drone_y + vcmd_len * math.sin(cmd_ang)
    frags.append(arrow(drone_x, drone_y, vcmd_x, vcmd_y, color="#8b5cf6", sw=3.0))
    frags.append(text(vcmd_x + 12, vcmd_y - 8, "v_cmd (бажана швидкість)", size=13, color="#8b5cf6", bold=True))

    # Дужка кута korektsii chi_cross біля дрона
    frags.append(line(drone_x, drone_y, drone_x + 90, drone_y, color=MUTED, sw=1.5, dash="3 3"))
    frags.append(text(drone_x + 96, drone_y - 6, "напрям шляху χ_F", size=11, color=MUTED, italic=True))

    # Дуга кута chi_cross
    arc_r = 50.0
    arc_chi = []
    for i in range(21):
        a = 0.0 + cmd_ang * (i / 20.0)
        arc_chi.append("%.1f,%.1f" % (drone_x + arc_r * math.cos(a), drone_y + arc_r * math.sin(a)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(arc_chi), "#8b5cf6"))
    frags.append(text(drone_x + 64, drone_y + 24, "χ_cross", size=12, color="#8b5cf6", bold=True, italic=True))

    # Формульний блок у правому нижньому кутку
    frags.append(rect(460, 360, 360, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(640, 385, "Закон наведення LOS:", size=13, color=INK, bold=True))
    frags.append(text(640, 410, "χ_cmd = χ_F + arctan(−e_ct / Δ_los)", size=13, color=INK, bold=True))
    frags.append(text(640, 435, "Збіжність:  ė_ct = −v · sin(χ_cross) ≈ −(v / Δ_los) · e_ct", size=11, color=FIELD))
    frags.append(text(640, 455, "Експоненційне затухання зі сталою часу  τ = Δ_los / v", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "los-vector-field.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_cross_track_geometry()
    fig_carrot_vs_pure_pursuit()
    fig_los_vector_field()
    print("All figures generated successfully.")
