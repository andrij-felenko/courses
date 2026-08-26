# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Зони Френеля й перешкода на шляху»."""

import os
import sys
import math

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def draw_fresnel_geometry():
    """Фігура 1: Геометрія 1-ї та 2-ї зон Френеля між передавачем і приймачем."""
    w, h = 860, 420
    frags = []

    # Фонова координатна розмітка / вісь
    y_axis = 210
    x_tx, x_rx = 100, 760
    d_total = x_rx - x_tx  # 660 px
    x_mid = (x_tx + x_rx) / 2  # 430

    # Еліпси зон Френеля
    # 2-га зона (зовнішня)
    r2_y = 135
    frags.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#f0f4f8" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>'
        % (x_mid, y_axis, d_total / 2, r2_y)
    )

    # 1-ша зона (внутрішня, головна)
    r1_y = 95
    frags.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#e8f4fd" stroke="#2457d6" stroke-width="2"/>'
        % (x_mid, y_axis, d_total / 2, r1_y)
    )

    # 60% просвіт 1-ї зони
    r06_y = r1_y * 0.6
    frags.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eafaf1" stroke="#27ae60" stroke-width="1.5" stroke-dasharray="4 3"/>'
        % (x_mid, y_axis, d_total / 2, r06_y)
    )

    # Пряма лінія прямої видимості (Line of Sight - LOS)
    frags.append(line(x_tx, y_axis, x_rx, y_axis, color="#c0392b", sw=2.5))

    # Довільна точка M на межі 1-ї зони Френеля
    x_m = 320
    norm_x = (x_m - x_mid) / (d_total / 2)
    y_m = y_axis - r1_y * math.sqrt(max(0.0, 1.0 - norm_x * norm_x))

    # Промені d1 та d2 до точки M
    frags.append(line(x_tx, y_axis, x_m, y_m, color="#2457d6", sw=1.8, dash="3 3"))
    frags.append(line(x_m, y_m, x_rx, y_axis, color="#2457d6", sw=1.8, dash="3 3"))
    frags.append(circle(x_m, y_m, 4.5, fill="#2457d6", stroke="#ffffff", sw=1.5))

    # Антени Tx та Rx
    def draw_antenna(x, y, label, is_tx=True):
        f = []
        f.append(line(x, y + 45, x, y - 20, color="#333333", sw=2.5))
        f.append(line(x - 18, y + 45, x + 18, y + 45, color="#333333", sw=3))
        f.append(line(x - 12, y + 45, x - 18, y + 53, color="#666666", sw=1.5))
        f.append(line(x, y + 45, x - 6, y + 53, color="#666666", sw=1.5))
        f.append(line(x + 12, y + 45, x + 6, y + 53, color="#666666", sw=1.5))
        f.append(line(x, y - 20, x - 10, y - 35, color="#c0392b", sw=2))
        f.append(line(x, y - 20, x + 10, y - 35, color="#c0392b", sw=2))
        f.append(circle(x, y, 4, fill="#c0392b", stroke="#ffffff", sw=1.5))
        box, _, _ = textbox(x, y + 72, label, size=13, pad=6, fill="#ffffff", stroke="#333333", bold=True)
        f.append(box)
        return "".join(f)

    frags.append(draw_antenna(x_tx, y_axis, "Передавач Tx", is_tx=True))
    frags.append(draw_antenna(x_rx, y_axis, "Приймач Rx", is_tx=False))

    # Виносні лінії та стрілки вимірювання радіусів у центрі
    frags.append(line(x_mid, y_axis, x_mid, y_axis - r1_y, color="#2457d6", sw=1.8))
    frags.append(arrow(x_mid, y_axis - 30, x_mid, y_axis - r1_y, color="#2457d6", sw=1.5))
    frags.append(arrow(x_mid, y_axis - 50, x_mid, y_axis, color="#2457d6", sw=1.5))

    box_r1, _, _ = textbox(x_mid + 60, y_axis - 60, "r₁ (макс)", size=12, pad=4, fill="#ffffff", stroke="#2457d6", bold=True, color="#2457d6")
    frags.append(box_r1)

    # Підписи зон і променів
    box_m, _, _ = textbox(x_m - 30, y_m - 20, "Точка M на межі\nd₁ + d₂ = D + λ/2", size=11, pad=5, fill="#ffffff", stroke="#2457d6")
    frags.append(box_m)

    box_los, _, _ = textbox(x_mid - 70, y_axis + 16, "Пряма видимість (LOS, відстань D)", size=12, pad=4, fill="#ffffff", stroke="#c0392b", color="#c0392b")
    frags.append(box_los)

    # Інформаційні плашки зверху
    box_z1, _, _ = textbox(240, 50, "1-ша зона Френеля (конструктивна фаза 0...180°)\nПереносить >85% енергії радіохвилі", size=12, pad=6, fill="#e8f4fd", stroke="#2457d6")
    frags.append(box_z1)

    box_z60, _, _ = textbox(620, 50, "Кліренс 60% r₁ (зона вільного простору)\nПерешкоди нижче цієї межі не дають втрат", size=12, pad=6, fill="#eafaf1", stroke="#27ae60")
    frags.append(box_z60)

    # Розмітка d1 та d2 знизу
    y_dist = y_axis + 140
    frags.append(line(x_tx, y_dist, x_rx, y_dist, color="#64748b", sw=1.5))
    frags.append(line(x_tx, y_dist - 8, x_tx, y_dist + 8, color="#64748b", sw=1.5))
    frags.append(line(x_rx, y_dist - 8, x_rx, y_dist + 8, color="#64748b", sw=1.5))
    frags.append(line(x_m, y_dist - 5, x_m, y_dist + 5, color="#64748b", sw=1.5, dash="2 2"))

    box_d1, _, _ = textbox((x_tx + x_m) / 2, y_dist + 22, "Відстань d₁", size=12, pad=4, fill="#ffffff", stroke="#64748b")
    box_d2, _, _ = textbox((x_m + x_rx) / 2, y_dist + 22, "Відстань d₂", size=12, pad=4, fill="#ffffff", stroke="#64748b")
    frags.append(box_d1)
    frags.append(box_d2)

    render(os.path.join(OUT_DIR, "fresnel-ellipsoid-geometry.svg"), w, h, *frags)


def draw_diffraction_loss_curve():
    """Фігура 2: Графік дифракційних втрат J(v) на перешкоді типу «лезо ножа» залежно від просвіту."""
    w, h = 860, 430
    frags = []

    # Графічна область
    gx, gy, gw, gh = 90, 45, 680, 310

    # Функція розрахунку кривої дифракційних втрат за ITU-R P.526
    def diff_loss(hr):
        v = hr * math.sqrt(2.0)
        if v <= -0.8:
            return 0.0
        elif v <= 0.0:
            return 6.0 + 7.19 * v + 2.27 * v * v
        elif v <= 1.0:
            return 6.0 + 9.0 * v - 1.27 * v * v
        elif v <= 2.4:
            return 13.0 + 20.0 * math.log10(v)
        else:
            return 16.0 + 20.0 * math.log10(v)

    def x_from_h_ratio(hr):
        return gx + (hr - (-1.5)) / 3.0 * gw

    def y_from_db(db):
        return gy + (db / 30.0) * gh

    # Горизонтальні пунктирні рівні сітки (короткі або тонкі)
    for db in [0, 5, 10, 15, 20, 25, 30]:
        y_pos = y_from_db(db)
        frags.append(line(gx, y_pos, gx + gw, y_pos, color="#f1f5f9", sw=1.0))
        frags.append(text(gx - 12, y_pos + 4, "%d дБ" % db, size=11, color=MUTED, anchor="end"))

    # Окремий рівень 6 дБ
    y_6db = y_from_db(6.0)
    frags.append(line(gx, y_6db, x_from_h_ratio(0.0), y_6db, color="#fca5a5", sw=1.2, dash="3 3"))
    frags.append(text(gx - 12, y_6db + 4, "6 дБ", size=11, color="#c0392b", anchor="end", bold=True))

    # Вертикальні пунктирні рівні
    for hr in [-1.5, -1.0, -0.6, 0.0, 0.5, 1.0, 1.5]:
        x_pos = x_from_h_ratio(hr)
        lbl = ("+%.1f" % hr) if hr > 0 else ("%.1f" % hr)
        frags.append(text(x_pos, gy + gh + 18, lbl, size=11, color=INK, anchor="middle", bold=(hr in [-0.6, 0.0])))

    # Осі координат
    frags.append(line(gx, gy, gx + gw, gy, color=LINE, sw=1.8))
    frags.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.8))
    frags.append(line(gx + gw, gy, gx + gw, gy + gh, color=LINE, sw=1.8))
    frags.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.8))

    # Підписи осей
    frags.append(text(gx + gw / 2, gy + gh + 42, "Кліренс перешкоди відносно радіуса 1-ї зони: h / r₁", size=13, bold=True, anchor="middle"))
    frags.append(text(gx - 50, gy + gh / 2, "Дифракційні втрати, дБ", size=13, bold=True, anchor="middle"))

    # Полілінія кривої втрат
    pts = []
    num_steps = 150
    for i in range(num_steps + 1):
        hr = -1.5 + (3.0 * i) / num_steps
        loss = diff_loss(hr)
        loss_clamped = min(30.0, max(0.0, loss))
        px = x_from_h_ratio(hr)
        py = y_from_db(loss_clamped)
        pts.append((px, py))

    path_d = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in pts])
    frags.append('<path d="%s" fill="none" stroke="#2457d6" stroke-width="3"/>' % path_d)

    # Точки та виносні підписи
    # Точка 1: h/r1 = -0.6 (кліренс 60%)
    x_06 = x_from_h_ratio(-0.6)
    y_06 = y_from_db(diff_loss(-0.6))
    frags.append(line(x_06, gy, x_06, y_06, color="#86efac", sw=1.2, dash="3 3"))
    frags.append(circle(x_06, y_06, 5, fill="#27ae60", stroke="#ffffff", sw=2))
    b1, _, _ = textbox(x_06 - 105, y_06 + 55, "Кліренс 60% (h = −0.6 r₁)\nВтрати < 0.5 дБ (вільний простір)", size=11, pad=5, fill="#ffffff", stroke="#27ae60", bold=True, color="#27ae60")
    frags.append(b1)
    frags.append(arrow(x_06 - 105, y_06 + 32, x_06 - 5, y_06 + 6, color="#27ae60", sw=1.4))

    # Точка 2: h/r1 = 0.0 (лінія прямої видимості)
    x_0 = x_from_h_ratio(0.0)
    y_0 = y_from_db(6.0)
    frags.append(line(x_0, gy, x_0, gy + gh, color="#fca5a5", sw=1.2, dash="3 3"))
    frags.append(circle(x_0, y_0, 5, fill="#c0392b", stroke="#ffffff", sw=2))
    b2, _, _ = textbox(x_0 + 135, y_0 + 40, "Лінія LOS (h = 0)\nВтрати = 6.0 дБ (−50% напруги поля)", size=11, pad=5, fill="#ffffff", stroke="#c0392b", bold=True, color="#c0392b")
    frags.append(b2)
    frags.append(arrow(x_0 + 40, y_0 + 30, x_0 + 6, y_0 + 4, color="#c0392b", sw=1.4))

    # Точка 3: h/r1 = +1.0 (глибоке затінення)
    x_1 = x_from_h_ratio(1.0)
    y_1 = y_from_db(diff_loss(1.0))
    frags.append(line(x_1, gy, x_1, y_1, color="#cbd5e1", sw=1.2, dash="3 3"))
    frags.append(circle(x_1, y_1, 5, fill="#334155", stroke="#ffffff", sw=2))
    b3, _, _ = textbox(x_1 - 120, y_1 + 55, "Перекриття (h = +1.0 r₁)\nВтрати ≈ 16.0 дБ (потужність −97.5%)", size=11, pad=5, fill="#ffffff", stroke="#334155")
    frags.append(b3)
    frags.append(arrow(x_1 - 40, y_1 + 45, x_1 - 6, y_1 + 6, color="#334155", sw=1.4))

    render(os.path.join(OUT_DIR, "diffraction-loss-curve.svg"), w, h, *frags)


def draw_earth_bulge_and_clearance():
    """Фігура 3: Профіль радіотраси з урахуванням кривини Землі, пагорба та висоти підвісу антен."""
    w, h = 880, 450
    frags = []

    # Точки Tx та Rx
    x1, x2 = 90, 790
    d_span = x2 - x1  # 700 px

    # Рівень моря (базова крива Землі)
    y_ground_base = 360

    # Крива поверхні Землі (параболічний прогин)
    max_earth_bulge = 45  # px на графіку для наочності
    ground_pts = []
    num_pts = 80
    for i in range(num_pts + 1):
        gx = x1 + (d_span * i) / num_pts
        t = i / float(num_pts)
        gy = y_ground_base - 4.0 * max_earth_bulge * t * (1.0 - t)
        ground_pts.append((gx, gy))

    # Додаємо пагорб посередині
    hill_center_x = x1 + d_span * 0.45
    hill_width = d_span * 0.28
    hill_height = 55  # px

    terrain_pts = []
    for gx, gy in ground_pts:
        dx = abs(gx - hill_center_x)
        if dx < hill_width:
            hill_lift = hill_height * 0.5 * (1.0 + math.cos(math.pi * dx / hill_width))
        else:
            hill_lift = 0.0
        terrain_pts.append((gx, gy - hill_lift))

    # Малюємо заповнення рельєфу землі
    poly_pts = [(x1, h)] + terrain_pts + [(x2, h)]
    path_ground = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in poly_pts]) + " Z"
    frags.append('<path d="%s" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>' % path_ground)

    # Дерева на пагорбі
    tree_x = hill_center_x - 15
    tree_y = y_ground_base - 4.0 * max_earth_bulge * 0.45 * (1.0 - 0.45) - hill_height
    frags.append(rect(tree_x - 30, tree_y - 20, 60, 20, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(tree_x, tree_y - 6, "Ліс (15 м)", size=11, color="#166534", anchor="middle", bold=True))

    # Щогли на кінцях
    mast1_h = 95
    mast2_h = 105
    y_tx_top = terrain_pts[0][1] - mast1_h
    y_rx_top = terrain_pts[-1][1] - mast2_h

    # Щогла Tx
    frags.append(line(x1, terrain_pts[0][1], x1, y_tx_top, color="#334155", sw=3))
    frags.append(circle(x1, y_tx_top, 5, fill="#c0392b", stroke="#ffffff", sw=2))
    box_tx, _, _ = textbox(x1, y_tx_top - 25, "Антена Tx (h₁ = 12 м)", size=12, pad=5, fill="#ffffff", stroke="#c0392b", bold=True)
    frags.append(box_tx)

    # Щогла Rx
    frags.append(line(x2, terrain_pts[-1][1], x2, y_rx_top, color="#334155", sw=3))
    frags.append(circle(x2, y_rx_top, 5, fill="#2457d6", stroke="#ffffff", sw=2))
    box_rx, _, _ = textbox(x2, y_rx_top - 25, "Антена Rx (h₂ = 15 м)", size=12, pad=5, fill="#ffffff", stroke="#2457d6", bold=True)
    frags.append(box_rx)

    # Лінія прямої видимості (LOS)
    frags.append(line(x1, y_tx_top, x2, y_rx_top, color="#c0392b", sw=2, dash="5 3"))

    # 1-ша зона Френеля вздовж прямої
    fresnel_top_pts = []
    fresnel_bot_pts = []
    fresnel_06_bot_pts = []

    for i in range(num_pts + 1):
        gx = x1 + (d_span * i) / num_pts
        t = i / float(num_pts)
        los_y = y_tx_top + t * (y_rx_top - y_tx_top)
        r1_px = 65.0 * math.sin(math.pi * t)
        fresnel_top_pts.append((gx, los_y - r1_px))
        fresnel_bot_pts.append((gx, los_y + r1_px))
        fresnel_06_bot_pts.append((gx, los_y + r1_px * 0.6))

    # Малюємо 1-шу зону Френеля
    path_fresnel = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in fresnel_top_pts]) + " L " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in reversed(fresnel_bot_pts)]) + " Z"
    frags.append('<path d="%s" fill="#3b82f6" fill-opacity="0.12" stroke="#2563eb" stroke-width="1.5"/>' % path_fresnel)

    # 60% межа кліренсу
    path_06 = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in fresnel_06_bot_pts])
    frags.append('<path d="%s" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="4 3"/>' % path_06)

    # Виносні лінії та стрілки кліренсу на пагорбі
    obs_t = 0.45
    obs_x = x1 + d_span * obs_t
    los_y_obs = y_tx_top + obs_t * (y_rx_top - y_tx_top)
    r1_obs = 65.0 * math.sin(math.pi * obs_t)
    r06_y_obs = los_y_obs + r1_obs * 0.6
    obs_top_y = tree_y - 20

    # Стрілка кліренсу
    frags.append(line(obs_x, obs_top_y, obs_x, los_y_obs, color="#e11d48", sw=1.8))
    frags.append(arrow(obs_x - 30, r06_y_obs, obs_x - 30, obs_top_y, color="#16a34a", sw=1.5))

    box_clear, _, _ = textbox(obs_x + 90, tree_y - 45, "Необхідний просвіт:\nКліренс ≥ 0.6 · r₁", size=11, pad=5, fill="#ffffff", stroke="#16a34a", color="#166534", bold=True)
    frags.append(box_clear)

    # Пояснення стріли прогину Землі
    mid_x = (x1 + x2) / 2
    y_straight = y_ground_base
    y_curved = y_ground_base - max_earth_bulge
    frags.append(line(x1, y_straight, x2, y_straight, color="#94a3b8", sw=1.2, dash="3 3"))
    frags.append(line(mid_x + 80, y_straight, mid_x + 80, y_curved, color="#64748b", sw=1.5))
    frags.append(arrow(mid_x + 80, y_straight - 10, mid_x + 80, y_straight, color="#64748b", sw=1.2))
    frags.append(arrow(mid_x + 80, y_curved + 10, mid_x + 80, y_curved, color="#64748b", sw=1.2))

    box_bulge, _, _ = textbox(mid_x + 165, y_straight - 20, "Горб Землі h_bulge\n≈ (d₁ · d₂) / 17", size=11, pad=4, fill="#ffffff", stroke="#64748b")
    frags.append(box_bulge)

    # Інформаційна плашка знизу
    box_formula, _, _ = textbox(w / 2, h - 30, "Повна висота лінії над перешкодою = Рельєф + Висота дерев + Горб Землі + 0.6 · r₁", size=12, pad=6, fill="#f8fafc", stroke="#334155", bold=True)
    frags.append(box_formula)

    render(os.path.join(OUT_DIR, "earth-bulge-and-clearance.svg"), w, h, *frags)


if __name__ == "__main__":
    draw_fresnel_geometry()
    draw_diffraction_loss_curve()
    draw_earth_bulge_and_clearance()
    print("Всі 3 фігури успішно згенеровано у теці img/")
