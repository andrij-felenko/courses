# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Побудова першої зони Бріллюена та геометрична схема Евальда
# ════════════════════════════════════════════════════════════════════════════
def fig_brillouin_zone_construction():
    W, H = 840, 440
    f = []

    f.append(text(420, 24, "Побудова першої зони Бріллюена та умова дифракції Лауе — Евальда", size=15, bold=True, color=INK))

    # Розділювальна лінія між панелями
    f.append(line(420, 50, 420, 415, color=MUTED, sw=1.2, dash="4 4"))

    # ── ПАНЕЛЬ А: 2D Обернена ґратка та 1-ша зона Бріллюена (Ліворуч) ──
    f.append(text(210, 52, "А. Зона Бріллюена як комірка Вігнера — Зейтца", size=13, bold=True, color=INK))

    cx, cy = 210, 235
    scale = 65.0  # відстань між вузлами оберненої ґратки

    nodes = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            nx = cx + (i + 0.5 * (j & 1)) * scale
            ny = cy + j * scale * math.sqrt(3) / 2.0
            if 30 <= nx <= 390 and 80 <= ny <= 390:
                nodes.append((nx, ny, i, j))

    # 1-ша зона Бріллюена (шестикутник навколо центру cx, cy)
    r_bz = scale / math.sqrt(3)  # радіус описаного кола перпендикулярів
    bz_pts = []
    for a_deg in range(30, 390, 60):
        rad = math.radians(a_deg)
        bz_pts.append((cx + r_bz * math.cos(rad), cy + r_bz * math.sin(rad)))

    # Заповнення 1-ї зони Бріллюена
    f.append(polygon(bz_pts, fill="#d4efdf", stroke=POS, sw=2.0))

    # Лінії перпендикуляри (площини Бреґґа)
    for nx, ny, i, j in nodes:
        if i == 0 and j == 0:
            continue
        dist = math.hypot(nx - cx, ny - cy)
        if dist < scale * 1.2:
            f.append(line(cx, cy, nx, ny, color=MUTED, sw=1.2, dash="3 3"))
            mx, my = 0.5 * (cx + nx), 0.5 * (cy + ny)
            dx, dy = (ny - cy) / dist, -(nx - cx) / dist
            len_b = 35.0
            f.append(line(mx - dx * len_b, my - dy * len_b, mx + dx * len_b, my + dy * len_b, color="#8e44ad", sw=1.5))

    # Нанесення вузлів оберненої ґратки
    for nx, ny, i, j in nodes:
        if i == 0 and j == 0:
            f.append(circle(nx, ny, 6, fill=FIELD, stroke=INK, sw=1.5))
        else:
            f.append(circle(nx, ny, 4, fill=INK, stroke="none"))

    # Базисні вектори b1, b2
    b1_x, b1_y = cx + scale, cy
    b2_x, b2_y = cx + 0.5 * scale, cy - scale * math.sqrt(3) / 2.0

    f.append(arrow(cx, cy, b1_x, b1_y, color=POS, sw=2.2))
    f.append(arrow(cx, cy, b2_x, b2_y, color=POS, sw=2.2))

    # Підписи векторів
    f.append(text(cx + scale + 12, cy + 4, "b₁", size=13, bold=True, color=POS))
    f.append(text(b2_x + 8, b2_y - 8, "b₂", size=13, bold=True, color=POS))

    # Високосиметричні точки
    f.append(text(cx - 12, cy - 8, "Γ", size=12, bold=True, color=FIELD))
    f.append(circle(cx + r_bz * math.cos(math.radians(30)), cy + r_bz * math.sin(math.radians(30)), 3.5, fill=NEG, stroke="none"))
    f.append(text(cx + r_bz * math.cos(math.radians(30)) + 10, cy + r_bz * math.sin(math.radians(30)) + 4, "K", size=11, bold=True, color=NEG))

    mx_m = 0.5 * (bz_pts[0][0] + bz_pts[1][0])
    my_m = 0.5 * (bz_pts[0][1] + bz_pts[1][1])
    f.append(circle(mx_m, my_m, 3.5, fill="#8e44ad", stroke="none"))
    f.append(text(mx_m + 10, my_m - 4, "M", size=11, bold=True, color="#8e44ad"))

    # Підпис 1-ї зони Бріллюена
    f.append(rect(100, 375, 220, 26, fill="#ffffff", stroke=POS, sw=1.2))
    f.append(text(210, 392, "Перша зона Бріллюена (1-ша ЗБ)", size=11, bold=True, color="#196f3d"))

    # ── ПАНЕЛЬ Б: Сфера Евальда та векторне рівняння k - k₀ = G (Праворуч) ──
    f.append(text(630, 52, "Б. Геометрична побудова сфери Евальда", size=13, bold=True, color=INK))

    sq_scale = 60.0
    or_x, or_y = 660, 240  # Вузол G = 0

    # Сітка обернених вузлів
    for ix in range(-2, 3):
        for iy in range(-2, 3):
            px = or_x + ix * sq_scale
            py = or_y + iy * sq_scale
            if 440 <= px <= 820 and 80 <= py <= 410:
                if ix == 0 and iy == 0:
                    f.append(circle(px, py, 5, fill=FIELD, stroke=INK, sw=1.5))
                    f.append(text(px - 14, py + 16, "0", size=11, bold=True, color=FIELD))
                elif ix == 1 and iy == -1:
                    f.append(circle(px, py, 6, fill=NEG, stroke=INK, sw=1.5))
                    f.append(text(px + 12, py - 6, "G (hkl)", size=11, bold=True, color=NEG))
                else:
                    f.append(circle(px, py, 3.5, fill=INK, stroke="none"))

    cx_e, cy_e = 520, 120
    R_e = math.hypot(or_x - cx_e, or_y - cy_e)

    # Коло Евальда як path з пунктиром
    circle_path = "M %.1f %.1f A %.1f %.1f 0 1 0 %.1f %.1f A %.1f %.1f 0 1 0 %.1f %.1f" % (
        cx_e - R_e, cy_e, R_e, R_e, cx_e + R_e, cy_e, R_e, R_e, cx_e - R_e, cy_e
    )
    f.append(svg_path(circle_path, stroke=POS, sw=1.8, dash="4 3"))

    # Вектор incident k0 від C до G=0
    f.append(arrow(cx_e, cy_e, or_x, or_y, color=POS, sw=2.2))
    f.append(text(580, 205, "k₀", size=13, bold=True, color=POS))

    # Вектор scattered k від C до G(1,-1) = (720, 180)
    gx, gy = or_x + sq_scale, or_y - sq_scale
    f.append(arrow(cx_e, cy_e, gx, gy, color=NEG, sw=2.2))
    f.append(text(620, 135, "k", size=13, bold=True, color=NEG))

    # Вектор оберненої ґратки G від (660,240) до (720,180)
    f.append(arrow(or_x, or_y, gx, gy, color=FIELD, sw=2.5))
    f.append(text(705, 220, "G = k − k₀", size=12, bold=True, color=FIELD))

    # Центр сфери C
    f.append(circle(cx_e, cy_e, 4, fill=POS, stroke=INK, sw=1.0))
    f.append(text(cx_e - 15, cy_e - 10, "C", size=11, bold=True, color=POS))

    # Підпис умови Лауе
    f.append(rect(520, 375, 220, 26, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(text(630, 392, "Умова Лауе: Δk = k − k₀ = G", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "brillouin-zone-construction.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Зонні розриви, бреґґівські площини та стоячі хвилі на межі ЗБ
# ════════════════════════════════════════════════════════════════════════════
def fig_zone_boundary_reflection():
    W, H = 840, 420
    f = []

    f.append(text(420, 24, "Дисперсія E(k), Бреґґівське відбиття та виникнення заборонених зон", size=15, bold=True, color=INK))

    f.append(line(420, 50, 420, 395, color=MUTED, sw=1.2, dash="4 4"))

    # ── ПАНЕЛЬ А: Дисперсійна крива E(k) з розривами (Ліворуч) ──
    f.append(text(210, 52, "А. Зонна структура у розширеній та зведеній схемах", size=13, bold=True, color=INK))

    ox_a, oy_a = 210, 340

    f.append(line(50, oy_a, 370, oy_a, color=INK, sw=1.8))
    f.append(line(ox_a, oy_a, ox_a, 70, color=INK, sw=1.8))
    f.append(polygon([(370, oy_a - 4), (378, oy_a), (370, oy_a + 4)], fill=INK))
    f.append(polygon([(ox_a - 4, 70), (ox_a, 62), (ox_a + 4, 70)], fill=INK))

    f.append(text(380, oy_a + 18, "k", size=12, bold=True, color=INK))
    f.append(text(ox_a - 15, 60, "Енергія E", size=12, bold=True, color=INK, anchor="end"))

    k_zb1 = 80
    k_zb2 = 140

    f.append(line(ox_a - k_zb1, 70, ox_a - k_zb1, oy_a, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(ox_a + k_zb1, 70, ox_a + k_zb1, oy_a, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(ox_a - k_zb1, oy_a + 18, "−π/a", size=11, bold=True, color=MUTED))
    f.append(text(ox_a + k_zb1, oy_a + 18, "+π/a", size=11, bold=True, color=MUTED))

    f.append(line(ox_a - k_zb2, 70, ox_a - k_zb2, oy_a, color=MUTED, sw=1.0, dash="2 2"))
    f.append(line(ox_a + k_zb2, 70, ox_a + k_zb2, oy_a, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(ox_a - k_zb2, oy_a + 18, "−2π/a", size=10, color=MUTED))
    f.append(text(ox_a + k_zb2, oy_a + 18, "+2π/a", size=10, color=MUTED))

    # Крива вільного електрона E ~ k^2
    pts_free = []
    for px in range(ox_a - 150, ox_a + 151, 5):
        dk = (px - ox_a) / float(k_zb1)
        ey = oy_a - 50.0 * (dk ** 2)
        if ey >= 70:
            pts_free.append((px, ey))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_free), stroke=MUTED, sw=1.5, dash="4 3"))
    f.append(text(310, 110, "E ∝ k² (вільний e⁻)", size=10, color=MUTED))

    # Перша дозволена зона
    pts_band1 = []
    for px in range(ox_a - k_zb1, ox_a + k_zb1 + 1, 3):
        dk = (px - ox_a) / float(k_zb1)
        ey = oy_a - 60.0 * (1.0 - math.cos(math.pi * dk / 2.0))
        pts_band1.append((px, ey))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_band1), stroke=POS, sw=2.5))

    # Друга дозволена зона
    eg1 = 25.0
    pts_band2_r = []
    for px in range(ox_a + k_zb1, ox_a + k_zb2 + 1, 3):
        dk = (px - ox_a) / float(k_zb1)
        ey = oy_a - 60.0 - eg1 - 70.0 * (1.0 - math.cos(math.pi * (dk - 1.0) / 2.0))
        pts_band2_r.append((px, ey))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_band2_r), stroke=NEG, sw=2.5))

    pts_band2_l = []
    for px in range(ox_a - k_zb2, ox_a - k_zb1 + 1, 3):
        dk = (px - ox_a) / float(k_zb1)
        ey = oy_a - 60.0 - eg1 - 70.0 * (1.0 - math.cos(math.pi * (dk + 1.0) / 2.0))
        pts_band2_l.append((px, ey))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_band2_l), stroke=NEG, sw=2.5))

    # Виділення забороненої зони (Bandgap Eg)
    gap_y1 = oy_a - 60.0
    gap_y2 = gap_y1 - eg1
    f.append(rect(ox_a - k_zb1 - 15, gap_y2, 2 * k_zb1 + 30, eg1, fill="#fadbd8", stroke="none"))
    f.append(line(ox_a + k_zb1 + 8, gap_y1, ox_a + k_zb1 + 8, gap_y2, color=NEG, sw=1.5))
    f.append(polygon([(ox_a + k_zb1 + 5, gap_y1 - 3), (ox_a + k_zb1 + 8, gap_y1 + 3), (ox_a + k_zb1 + 11, gap_y1 - 3)], fill=NEG))
    f.append(polygon([(ox_a + k_zb1 + 5, gap_y2 + 3), (ox_a + k_zb1 + 8, gap_y2 - 3), (ox_a + k_zb1 + 11, gap_y2 + 3)], fill=NEG))
    f.append(text(ox_a + k_zb1 + 45, gap_y1 - 8, "Щілина E_g = 2|V_G|", size=11, bold=True, color=NEG))

    # ── ПАНЕЛЬ Б: Розподіл електронної густини стоячих хвиль ψ+ та ψ- (Праворуч) ──
    f.append(text(630, 52, "Б. Просторовий розподіл густини |ψ|² відносно іонів", size=13, bold=True, color=INK))

    ox_b, oy_b = 480, 260

    ions_x = [ox_b + 20, ox_b + 100, ox_b + 180, ox_b + 260, ox_b + 340]
    for ix in ions_x:
        f.append(line(ix, 80, ix, 360, color=MUTED, sw=1.0, dash="3 3"))
        f.append(circle(ix, 360, 7, fill=FIELD, stroke=INK, sw=1.5))
        f.append(text(ix, 358, "+", size=11, bold=True, color="#ffffff"))

    f.append(text(630, 390, "Атомні ядра ґратки з періодом a", size=11, bold=True, color=INK))

    # Стояча хвиля ψ+
    pts_psi_pos = []
    for px in range(ox_b + 20, ox_b + 341, 4):
        x_rel = (px - (ox_b + 20)) / 80.0
        rho_pos = math.cos(math.pi * x_rel) ** 2
        py = oy_b - 65.0 * rho_pos
        pts_psi_pos.append((px, py))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_psi_pos), stroke=POS, sw=2.5))
    f.append(text(ox_b + 60, oy_b - 72, "|ψ₊|² = cos²(πx/a) (нижній край, E₋)", size=11, bold=True, color=POS))

    # Стояча хвиля ψ-
    pts_psi_neg = []
    for px in range(ox_b + 20, ox_b + 341, 4):
        x_rel = (px - (ox_b + 20)) / 80.0
        rho_neg = math.sin(math.pi * x_rel) ** 2
        py = oy_b - 130.0 - 65.0 * rho_neg
        pts_psi_neg.append((px, py))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_psi_neg), stroke=NEG, sw=2.5))
    f.append(text(ox_b + 140, oy_b - 200, "|ψ₋|² = sin²(πx/a) (верхній край, E₊)", size=11, bold=True, color=NEG))

    f.append(rect(490, 275, 300, 45, fill="#eaf2f8", stroke=LINE, sw=1.2))
    f.append(text(640, 293, "ψ₊ накопичує електронний заряд на ядрах → E₋ нижча", size=10, color=POS))
    f.append(text(640, 309, "ψ₋ накопичує заряд між ядрами → E₊ вища", size=10, color=NEG))

    render(os.path.join(OUT, "zone-boundary-reflection.svg"), W, H, *f)


if __name__ == "__main__":
    fig_brillouin_zone_construction()
    fig_zone_boundary_reflection()
    print("Фігури reciprocal-lattice успішно згенеровано.")
