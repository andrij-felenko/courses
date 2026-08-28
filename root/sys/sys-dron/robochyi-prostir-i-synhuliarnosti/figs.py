# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Робочий простір і сингулярності».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

def out_path(filename):
    return os.path.join(IMG_DIR, filename)


# ── Фігура 1: Зона досяжності vs Простір маневреності ──────────────────────────
def fig_reachability_vs_dexterity():
    W, H = 960, 480
    parts = []

    # Заголовок зверху
    parts.append(text(W / 2, 30, "Структура робочого простору маніпулятора: досяжність проти маневреності", size=16, bold=True))

    # ЛІВА ПАНЕЛЬ: Геометрія 2-ланкового маніпулятора
    lx, ly = 210, 260
    l1, l2 = 100, 75

    parts.append(text(lx, 70, "Кінематична схема ланок", size=14, bold=True))
    parts.append(text(lx, 90, "довжини ланок L₁ та L₂", size=12, color=MUTED))

    # Основа
    parts.append(rect(lx - 25, ly + 60, 50, 16, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    parts.append(line(lx - 35, ly + 76, lx + 35, ly + 76, color=INK, sw=2))
    for hx in range(lx - 30, lx + 35, 10):
        parts.append(line(hx, ly + 76, hx - 6, ly + 86, color=MUTED, sw=1.2))

    # Шарнір 1
    p0 = (lx, ly + 60)
    # Ланка 1 (під кутом 50 град до горизонту)
    ang1 = math.radians(-65)
    p1 = (p0[0] + l1 * math.cos(ang1), p0[1] + l1 * math.sin(ang1))
    # Ланка 2 (під кутом -10 град)
    ang2 = math.radians(-15)
    p2 = (p1[0] + l2 * math.cos(ang2), p1[1] + l2 * math.sin(ang2))

    # Лінії ланок
    parts.append(line(p0[0], p0[1], p1[0], p1[1], color="#334155", sw=6))
    parts.append(line(p1[0], p1[1], p2[0], p2[1], color="#334155", sw=5))

    # Шарніри
    parts.append(circle(p0[0], p0[1], 8, fill="#ffffff", stroke=INK, sw=2))
    parts.append(circle(p1[0], p1[1], 7, fill="#ffffff", stroke=INK, sw=2))
    parts.append(circle(p2[0], p2[1], 6, fill=POS, stroke=INK, sw=2))

    # Підписи ланок і шарнірів
    parts.append(text(p0[0] - 18, p0[1] - 10, "q₁", size=12, color=NEG, bold=True))
    parts.append(text(p1[0] - 18, p1[1] - 10, "q₂", size=12, color=NEG, bold=True))
    parts.append(text((p0[0] + p1[0]) / 2 + 16, (p0[1] + p1[1]) / 2, "L₁", size=12, bold=True))
    parts.append(text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 14, "L₂", size=12, bold=True))
    parts.append(text(p2[0] + 15, p2[1] + 4, "Ефектор (x, y)", size=11.5, color=POS, bold=True, anchor="start"))

    # Пояснювальний бокс знизу лівої панелі
    box_geom, _, _ = textbox(lx, ly + 145, "R_max = L₁ + L₂ (макс. виліт)\nR_min = |L₁ − L₂| (мертва зона)", size=11.5, pad=6, fill="#f8fafc", stroke="#cbd5e1")
    parts.append(box_geom)

    # ПРАВА ПАНЕЛЬ: Переріз робочого простору
    rx, ry = 650, 260
    r_max = 160
    r_mid = 115
    r_min = 45

    parts.append(text(rx, 70, "Переріз робочого простору (XY)", size=14, bold=True))
    parts.append(text(rx, 90, "зони доступності орієнтацій кінцевого ефектора", size=12, color=MUTED))

    # Сектор або концентричні зони
    # Зона досяжності W_R (Reachable Workspace) — зовнішнє кільце
    parts.append(circle(rx, ry, r_max, fill="#eff6ff", stroke="#93c5fd", sw=2))
    # Вторинний робочий простір (Sub-dextrous Workspace)
    parts.append(circle(rx, ry, r_mid, fill="#e0f2fe", stroke="#38bdf8", sw=1.5))
    # Простір маневреності W_D (Dextrous Workspace)
    parts.append(circle(rx, ry, r_min + 35, fill="#dcfce7", stroke="#22c55e", sw=2))
    # Внутрішня мертва зона
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>' % (rx, ry, r_min))

    # Центр / основа
    parts.append(circle(rx, ry, 4, fill=LINE, stroke=LINE))
    parts.append(text(rx + 8, ry + 15, "Основа", size=11, color=MUTED, anchor="start"))

    # Сектор заборонених кутів (обмеження шарніра)
    dead_ang1, dead_ang2 = 120, 160
    # Намалюємо сектор штриховкою або конусом
    d_x1 = rx + r_max * math.cos(math.radians(dead_ang1))
    d_y1 = ry + r_max * math.sin(math.radians(dead_ang1))
    d_x2 = rx + r_max * math.cos(math.radians(dead_ang2))
    d_y2 = ry + r_max * math.sin(math.radians(dead_ang2))
    parts.append(line(rx, ry, d_x1, d_y1, color="#f87171", sw=1.2, dash="3,3"))
    parts.append(line(rx, ry, d_x2, d_y2, color="#f87171", sw=1.2, dash="3,3"))
    parts.append(text(rx - 120, ry + 100, "Кутовий упор шарніра", size=10.5, color=POS, italic=True))

    # Позначення зон стрілками та плашками
    # W_R (Зовнішня межа)
    parts.append(line(rx + r_max * math.cos(math.radians(-35)), ry + r_max * math.sin(math.radians(-35)), rx + 185, ry - 90, color="#2563eb", sw=1.2))
    parts.append(text(rx + 190, ry - 95, "Зона досяжності W_R (Reachable)", size=11.5, color="#1e40af", bold=True, anchor="start"))
    parts.append(text(rx + 190, ry - 80, "доступна бодай одна орієнтація", size=10.5, color=MUTED, anchor="start"))

    # W_D (Внутрішній простір маневреності)
    parts.append(line(rx + 35, ry - 40, rx + 185, ry - 25, color=FIELD, sw=1.2))
    parts.append(text(rx + 190, ry - 30, "Простір маневреності W_D (Dextrous)", size=11.5, color="#15803d", bold=True, anchor="start"))
    parts.append(text(rx + 190, ry - 15, "доступні ВСІ орієнтації SO(3) [360°]", size=10.5, color=MUTED, anchor="start"))

    # Вторинний простір
    parts.append(line(rx + r_mid * math.cos(math.radians(30)), ry + r_mid * math.sin(math.radians(30)), rx + 185, ry + 40, color="#0284c7", sw=1.2))
    parts.append(text(rx + 190, ry + 35, "Вторинний простір (Sub-dextrous)", size=11.5, color="#0369a1", bold=True, anchor="start"))
    parts.append(text(rx + 190, ry + 50, "обмежений конус орієнтацій Ω < 4π sr", size=10.5, color=MUTED, anchor="start"))

    # Мертва зона
    parts.append(line(rx - 20, ry + 20, rx - 140, ry + 155, color="#64748b", sw=1.2))
    parts.append(text(rx - 145, ry + 160, "Мертва зона r < |L₁ − L₂|", size=11, color="#475569", bold=True, anchor="end"))

    # Радіуси на малюнку
    parts.append(line(rx, ry, rx + r_max * math.cos(math.radians(-65)), ry + r_max * math.sin(math.radians(-65)), color="#64748b", sw=1, dash="2,2"))
    parts.append(text(rx + 85, ry - 80, "R_max", size=11, color="#1e40af", bold=True))

    return render(out_path("reachability-vs-dexterity.svg"), W, H, *parts)


# ── Фігура 2: Класифікація кінематичних сингулярностей ────────────────────────
def fig_singularity_types():
    W, H = 980, 420
    parts = []

    parts.append(text(W / 2, 28, "Типи кінематичних сингулярностей маніпулятора", size=16, bold=True))

    # ТРИ ПАНЕЛІ:
    # 1) Гранична сингулярність (повне випрямлення)
    # 2) Сингулярність зап'ястка (Wrist singularity / Gimbal Lock)
    # 3) Плечова сингулярність (Shoulder / Column singularity)

    col_w = 300
    y_top = 65

    # ── Панель 1: Гранична ───────────────────────────────────────────────────
    p1_cx = 170
    parts.append(rect(p1_cx - col_w / 2 + 10, y_top, col_w - 20, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(p1_cx, y_top + 25, "1. Гранична сингулярність", size=13.5, color=POS, bold=True))
    parts.append(text(p1_cx, y_top + 43, "зовнішня межа робочого простору", size=11, color=MUTED))

    # Схема випрямленої руки
    bx1, by1 = p1_cx - 85, y_top + 150
    p_mid = (bx1 + 80, by1)
    p_end = (bx1 + 160, by1)

    # Основа
    parts.append(rect(bx1 - 16, by1 - 16, 16, 32, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    # Ланки в одну лінію
    parts.append(line(bx1, by1, p_mid[0], p_mid[1], color="#334155", sw=5))
    parts.append(line(p_mid[0], p_mid[1], p_end[0], p_end[1], color="#334155", sw=5))

    parts.append(circle(bx1, by1, 6, fill="#ffffff", stroke=INK, sw=2))
    parts.append(circle(p_mid[0], p_mid[1], 6, fill="#ffffff", stroke=INK, sw=2))
    parts.append(circle(p_end[0], p_end[1], 6, fill=POS, stroke=INK, sw=2))

    parts.append(text(p_mid[0], p_mid[1] - 14, "θ₂ = 0° (лікоть)", size=11, color=NEG, bold=True))

    # Вектори швидкості
    # Радіальна швидкість заборонена
    parts.append(arrow(p_end[0], p_end[1], p_end[0] + 35, p_end[1], color=POS, sw=2))
    parts.append(text(p_end[0] + 40, p_end[1] + 4, "v_r = 0", size=11.5, color=POS, bold=True, anchor="start"))
    parts.append(line(p_end[0] + 33, p_end[1] - 8, p_end[0] + 47, p_end[1] + 8, color=POS, sw=2))

    # Тангенціальна швидкість дозволена
    parts.append(arrow(p_end[0], p_end[1], p_end[0], p_end[1] - 35, color=FIELD, sw=2))
    parts.append(text(p_end[0] - 10, p_end[1] - 40, "v_t ≠ 0", size=11, color=FIELD, bold=True, anchor="end"))

    # Пояснення
    fit_t1 = ("Втрата 1 ступеня вільності:\n"
              "радіальний рух назовні\n"
              "фізично неможливий;\n"
              "det(J) = 0 на краю W_R.")
    parts.append(fitbox(p1_cx - col_w / 2 + 22, y_top + 215, col_w - 44, 90, fit_t1, size=11.5, pad=6, fill="#ffffff", stroke="#e2e8f0"))

    # ── Панель 2: Зап'ясток ──────────────────────────────────────────────────
    p2_cx = W / 2
    parts.append(rect(p2_cx - col_w / 2 + 10, y_top, col_w - 20, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(p2_cx, y_top + 25, "2. Сингулярність зап'ястка", size=13.5, color=POS, bold=True))
    parts.append(text(p2_cx, y_top + 43, "вирівнювання осей (Gimbal Lock)", size=11, color=MUTED))

    # Схема 3-осьового зап'ястка: осі 4, 5, 6
    wx, wy = p2_cx, y_top + 145

    # Спільна вісь z4 та z6
    parts.append(line(wx - 75, wy, wx + 75, wy, color=NEG, sw=2, dash="5,3"))
    parts.append(text(wx - 65, wy - 12, "вісь z₄", size=11, color=NEG, bold=True))
    parts.append(text(wx + 65, wy - 12, "вісь z₆", size=11, color=NEG, bold=True))

    # Шарнір 5 під кутом 0 (вісь z5 перпендикулярна до площини)
    parts.append(circle(wx, wy, 14, fill="#ffffff", stroke="#334155", sw=2.5))
    parts.append(circle(wx, wy, 4, fill=POS, stroke=INK))
    parts.append(text(wx, wy - 22, "θ₅ = 0° (вісь z₅ ⊥)", size=11.5, color=POS, bold=True))

    # Дугові стрілки обертань навколо z4 та z6
    parts.append(arrow(wx - 45, wy - 18, wx - 45, wy + 18, color=NEG, sw=1.8))
    parts.append(arrow(wx + 45, wy - 18, wx + 45, wy + 18, color=NEG, sw=1.8))
    parts.append(text(wx, wy + 32, "z₄ || z₆ (колінеарні)", size=11.5, color=INK, bold=True))

    fit_t2 = ("Осі z₄ та z₆ збігаються:\n"
              "втрачено поворот вбік;\n"
              "намагання повернути рух\n"
              "вимагає q̇₄ = −q̇₆ → ∞.")
    parts.append(fitbox(p2_cx - col_w / 2 + 22, y_top + 215, col_w - 44, 90, fit_t2, size=11.5, pad=6, fill="#ffffff", stroke="#e2e8f0"))

    # ── Панель 3: Плечова / Колонна ──────────────────────────────────────────
    p3_cx = W - 170
    parts.append(rect(p3_cx - col_w / 2 + 10, y_top, col_w - 20, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(p3_cx, y_top + 25, "3. Плечова сингулярність", size=13.5, color=POS, bold=True))
    parts.append(text(p3_cx, y_top + 43, "зап'ясток на осі колони (x=0, y=0)", size=11, color=MUTED))

    # Схема: вертикальна вісь z1 основи і зап'ясток на ній
    sx, sy = p3_cx, y_top + 160

    # Вертикальна вісь z1
    parts.append(line(sx, sy - 55, sx, sy + 35, color=NEG, sw=2, dash="5,3"))
    parts.append(text(sx + 10, sy - 42, "вісь z₁", size=11, color=NEG, bold=True, anchor="start"))

    # Основа
    parts.append(rect(sx - 25, sy + 30, 50, 14, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))

    # Рука у формі арки, центр зап'ястка прямо на z1
    p_sh = (sx, sy + 15)
    p_elb = (sx + 45, sy - 15)
    p_wri = (sx, sy - 35)

    parts.append(line(p_sh[0], p_sh[1], p_elb[0], p_elb[1], color="#334155", sw=4))
    parts.append(line(p_elb[0], p_elb[1], p_wri[0], p_wri[1], color="#334155", sw=4))

    parts.append(circle(p_sh[0], p_sh[1], 5, fill="#ffffff", stroke=INK, sw=1.5))
    parts.append(circle(p_elb[0], p_elb[1], 5, fill="#ffffff", stroke=INK, sw=1.5))
    parts.append(circle(p_wri[0], p_wri[1], 6, fill=POS, stroke=INK, sw=2))

    # Поперечна швидкість вимагає нескінченного повороту q1
    parts.append(arrow(p_wri[0], p_wri[1], p_wri[0] - 30, p_wri[1], color=POS, sw=2))
    parts.append(text(p_wri[0] - 34, p_wri[1] - 6, "v_y", size=11, color=POS, bold=True, anchor="end"))
    parts.append(text(sx + 8, p_wri[1] + 4, "Зап'ясток P_w", size=10.5, color=POS, bold=True, anchor="start"))

    fit_t3 = ("Зап'ясток на осі обертання z₁:\n"
              "рух перпендикулярно руці\n"
              "вимагає миттєвого розвороту\n"
              "бази на 180° (q̇₁ → ∞).")
    parts.append(fitbox(p3_cx - col_w / 2 + 22, y_top + 215, col_w - 44, 90, fit_t3, size=11.5, pad=6, fill="#ffffff", stroke="#e2e8f0"))

    return render(out_path("singularity-types.svg"), W, H, *parts)


# ── Фігура 3: Еліпсоїд маніпулятивності Йошікави ──────────────────────────────
def fig_manipulability_ellipsoid():
    W, H = 960, 460
    parts = []

    parts.append(text(W / 2, 28, "Еліпсоїд маніпулятивності швидкостей та сил Йошікави", size=16, bold=True))

    # ЛІВОРУЧ: Одинична сфера швидкостей у шарнірному просторі ||q̇|| <= 1
    lx, ly = 160, 240
    parts.append(text(lx, 68, "Шарнірний простір q̇", size=14, bold=True))
    parts.append(text(lx, 88, "одинична сфера ||q̇||² ≤ 1", size=11.5, color=MUTED))

    # Одиничне коло
    r_j = 65
    parts.append(line(lx - 85, ly, lx + 85, ly, color="#cbd5e1", sw=1.2))
    parts.append(line(lx, ly - 85, lx, ly + 85, color="#cbd5e1", sw=1.2))
    parts.append(circle(lx, ly, r_j, fill="#f1f5f9", stroke="#64748b", sw=2))

    parts.append(text(lx + 88, ly - 6, "q̇₁", size=12, color=MUTED, anchor="start"))
    parts.append(text(lx + 6, ly - 88, "q̇₂", size=12, color=MUTED))
    parts.append(text(lx + 35, ly - 35, "||q̇|| ≤ 1", size=12, color="#475569", bold=True))

    # СТРІЛКА ВІДОБРАЖЕННЯ ЯКОБІАНА
    parts.append(arrow(lx + 95, ly, lx + 175, ly, color=LINE, sw=2.5))
    parts.append(text(lx + 135, ly - 14, "v = J(q) · q̇", size=12.5, color=INK, bold=True))

    # СЕРЕДИНА: Декартовий простір швидкостей (Еліпсоїд швидкостей)
    mx, my = 520, 160
    parts.append(text(mx, 68, "Еліпсоїд швидкостей: vᵀ (J Jᵀ)⁻¹ v ≤ 1", size=13.5, color="#1e40af", bold=True))

    # Випадок А: Ізотропна конфігурація
    ax, ay = mx - 100, my + 60
    parts.append(circle(ax, ay, 40, fill="#dcfce7", stroke=FIELD, sw=2))
    parts.append(line(ax - 50, ay, ax + 50, ay, color="#cbd5e1", sw=1))
    parts.append(line(ax, ay - 50, ax, ay + 50, color="#cbd5e1", sw=1))
    parts.append(text(ax, ay + 62, "Ізотропна (κ = 1)", size=11.5, color=FIELD, bold=True))
    parts.append(text(ax, ay + 78, "σ₁ = σ₂, w = max", size=10.5, color=MUTED))

    # Випадок Б: Біля сингулярності (сплющений еліпс)
    bx, by = mx + 110, my + 60
    # Малюємо еліпс повернутий
    ang = -25
    rx_e, ry_e = 65, 14
    # Намалюємо полігоном або SVG-еліпсом з transform
    rad = math.radians(ang)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    pts_ell = []
    for step in range(36):
        t_ang = math.radians(step * 10)
        ex = rx_e * math.cos(t_ang)
        ey = ry_e * math.sin(t_ang)
        px = bx + ex * cos_a - ey * sin_a
        py = by + ex * sin_a + ey * cos_a
        pts_ell.append("%.1f,%.1f" % (px, py))

    parts.append('<polygon points="%s" fill="#fee2e2" stroke="%s" stroke-width="2"/>' % (" ".join(pts_ell), POS))
    # Головні півосі
    parts.append(arrow(bx, by, bx + rx_e * cos_a, by + rx_e * sin_a, color=POS, sw=1.8))
    parts.append(arrow(bx, by, bx - ry_e * sin_a, by + ry_e * cos_a, color=POS, sw=1.5))
    parts.append(text(bx + 45, by - 32, "σ₁ u₁", size=11, color=POS, bold=True))
    parts.append(text(bx + 18, by + 28, "σ₂ u₂ → 0", size=11, color=POS, bold=True))

    parts.append(text(bx, by + 62, "Біля сингулярності", size=11.5, color=POS, bold=True))
    parts.append(text(bx, by + 78, "w = σ₁·σ₂ → 0", size=10.5, color=MUTED))

    # ЗНИЗУ ПРАВОРУЧ: Дуальний еліпсоїд зусиль
    fx, fy = mx + 110, my + 215
    # Еліпсоїд зусиль: витягнутий вздовж u2 (довжина 1/σ2), сплющений вздовж u1 (1/σ1)
    rx_f, ry_f = 16, 58
    pts_fell = []
    for step in range(36):
        t_ang = math.radians(step * 10)
        ex = rx_f * math.cos(t_ang)
        ey = ry_f * math.sin(t_ang)
        px = fx + ex * cos_a - ey * sin_a
        py = fy + ex * sin_a + ey * cos_a
        pts_fell.append("%.1f,%.1f" % (px, py))

    parts.append('<polygon points="%s" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>' % (" ".join(pts_fell), ))
    parts.append(arrow(fx, fy, fx - ry_f * sin_a, fy + ry_f * cos_a, color="#1d4ed8", sw=2))
    parts.append(text(fx - 40, fy + 48, "1/σ₂ → ∞ (витримка сили)", size=11, color="#1e40af", bold=True))

    parts.append(text(mx - 100, fy + 10, "Дуальний еліпсоїд сил:", size=12.5, color="#1e40af", bold=True))
    parts.append(text(mx - 100, fy + 30, "Fᵀ (J Jᵀ) F ≤ 1", size=12, color=INK))
    parts.append(text(mx - 100, fy + 50, "де швидкість v → 0, там", size=11, color=MUTED))
    parts.append(text(mx - 100, fy + 65, "сила F_max → ∞ без зусиль приводів", size=11, color=MUTED))

    return render(out_path("manipulability-ellipsoid.svg"), W, H, *parts)


# ── Фігура 4: Демпфовані найменші квадрати (DLS) ─────────────────────────────
def fig_damped_least_squares():
    W, H = 960, 440
    parts = []

    parts.append(text(W / 2, 28, "Порівняння псевдоінверсії та методу DLS біля сингулярності", size=16, bold=True))

    # ГРАФІК ЛІВОРУЧ
    gx, gy = 90, 360
    gw, gh = 400, 260

    # Вісі координат
    parts.append(line(gx, gy, gx + gw, gy, color=LINE, sw=2))
    parts.append(line(gx, gy, gx, gy - gh, color=LINE, sw=2))
    parts.append(arrow(gx + gw, gy, gx + gw + 20, gy, color=LINE, sw=2))
    parts.append(arrow(gx, gy - gh, gx, gy - gh - 20, color=LINE, sw=2))

    parts.append(text(gx + gw + 25, gy + 18, "Наближення до сингулярності: 1 / σ_min", size=11.5, bold=True, anchor="end"))
    parts.append(text(gx - 10, gy - gh - 22, "Швидкість шарнірів ||q̇||", size=12, bold=True, anchor="start"))

    # Вертикальна лінія сингулярності
    x_sing = gx + gw - 60
    parts.append(line(x_sing, gy, x_sing, gy - gh, color="#fca5a5", sw=1.5, dash="4,4"))
    parts.append(text(x_sing, gy + 18, "det(J) = 0", size=11, color=POS, bold=True))

    # Крива 1: Стандартна псевдоінверсія J⁺ (розбіжність до нескінченності)
    pts_pinv = []
    for step in range(35):
        t = step / 34.0
        cur_x = gx + t * (x_sing - gx - 15)
        # гіпербола
        sigma = 1.0 - 0.95 * t
        val_y = 15.0 / (sigma + 0.02)
        cur_y = gy - min(val_y, gh - 10)
        pts_pinv.append("%.1f,%.1f" % (cur_x, cur_y))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_pinv), POS))
    parts.append(text(gx + 180, gy - 200, "Псевдоінверсія J⁺:\nq̇ → ∞ (розрив струму)", size=11.5, color=POS, bold=True))

    # Крива 2: Damped Least Squares (DLS) з демпфуванням lambda
    pts_dls = []
    for step in range(45):
        t = step / 44.0
        cur_x = gx + t * (gw - 20)
        sigma = max(0.01, 1.0 - t)
        lam = 0.35 if sigma < 0.4 else 0.0
        # dls factor: sigma / (sigma^2 + lam^2)
        val_y = (sigma / (sigma**2 + lam**2)) * 32.0
        cur_y = gy - val_y
        pts_dls.append("%.1f,%.1f" % (cur_x, cur_y))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_dls), FIELD))
    parts.append(text(gx + 260, gy - 75, "DLS (Демпфовані найменші квадрати):\nшвидкість плавно обмежена", size=11.5, color="#15803d", bold=True))

    # Поріг насичення сервоприводів
    y_sat = gy - 160
    parts.append(line(gx, y_sat, gx + gw, y_sat, color="#f59e0b", sw=1.5, dash="5,3"))
    parts.append(text(gx + 10, y_sat - 6, "Межа швидкості / струму приводів q̇_max", size=11, color="#b45309", bold=True, anchor="start"))

    # ПРАВА ПАНЕЛЬ: Математичні формули та правила перемикання
    rx = 730
    parts.append(text(rx, 75, "Математичний алгоритм DLS", size=14, bold=True))

    box_form1, _, _ = textbox(rx, 140, "Цільовий функціонал оптимізації:\nmin ||J q̇ − v_e||² + λ² ||q̇||²", size=12, pad=8, fill="#f8fafc", stroke="#94a3b8", bold=True)
    parts.append(box_form1)

    box_form2, _, _ = textbox(rx, 225, "Аналітичний розв'язок:\nq̇ = Jᵀ (J Jᵀ + λ² I)⁻¹ · v_e", size=12.5, pad=8, fill="#eff6ff", stroke="#3b82f6", color="#1d4ed8", bold=True)
    parts.append(box_form2)

    box_form3, _, _ = textbox(rx, 330, "Адаптивний коефіцієнт λ(w):\n• λ² = 0, якщо w(q) ≥ w₀ (чиста IK)\n• λ² = λ_max² (1 − w/w₀)², якщо w < w₀", size=11.5, pad=8, fill="#f0fdf4", stroke=FIELD)
    parts.append(box_form3)

    return render(out_path("damped-least-squares.svg"), W, H, *parts)


if __name__ == "__main__":
    print("Генерація SVG-фігур...")
    fig_reachability_vs_dexterity()
    fig_singularity_types()
    fig_manipulability_ellipsoid()
    fig_damped_least_squares()
    print("Готово! Фігури збережено в ./img/")
