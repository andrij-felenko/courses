# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = NEG          # передбачення / номінальний стан
RED    = POS          # вимір / викид / небезпека
GREEN  = FIELD        # прийнятий вимір / довірена зона
YELLOW = "#d97706"    # зона м'якого масштабування (адаптивна)
PURPLE = "#7c3aed"    # статистика / теоретичні криві


# ── 1. innovation-geometry: Еліпс Махаланобіса проти евклідової відстані ───────
def fig_innovation_geometry():
    W, H = 760, 440
    cx, cy = 340, 240
    p = []

    # Осі вимірів
    p.append(line(70, cy, 680, cy, color="#e5e7eb", sw=1.2))
    p.append(line(cx, 50, cx, 400, color="#e5e7eb", sw=1.2))
    p.append(text(675, cy - 12, "z₁ (позиція X)", size=11, color=MUTED, anchor="end"))
    p.append(text(cx + 12, 65, "z₂ (позиція Y)", size=11, color=MUTED, anchor="start"))

    # Похилий еліпс коваріації S (кут ~30 градусів, a=190, b=65)
    angle_rad = math.radians(-30)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    def ellipse_pts(rx, ry, n=100):
        pts = []
        for i in range(n + 1):
            t = 2.0 * math.pi * i / n
            ex = rx * math.cos(t)
            ey = ry * math.sin(t)
            rot_x = cx + ex * cos_a - ey * sin_a
            rot_y = cy + ex * sin_a + ey * cos_a
            pts.append((rot_x, rot_y))
        return pts

    # Зовнішній еліпс (брама γ = 9.21, 3σ)
    pts_gate = ellipse_pts(195, 75)
    poly_gate = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_gate)
    p.append('<polygon points="%s" fill="#ecfdf5" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>'
             % (poly_gate, GREEN))

    # Внутрішній еліпс (1σ)
    pts_1s = ellipse_pts(95, 36)
    poly_1s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_1s)
    p.append('<polygon points="%s" fill="#d1fae5" opacity="0.45" stroke="%s" stroke-width="1.4"/>'
             % (poly_1s, GREEN))

    # Головні осі еліпса (напрямки власних векторів S)
    ax1_x1 = cx - 215 * cos_a
    ax1_y1 = cy - 215 * sin_a
    ax1_x2 = cx + 215 * cos_a
    ax1_y2 = cy + 215 * sin_a
    p.append(line(ax1_x1, ax1_y1, ax1_x2, ax1_y2, color="#9ca3af", sw=1.0, dash="3,3"))

    # Центр: передбачене спостереження H*x_hat
    p.append(circle(cx, cy, 5, fill=BLUE, stroke=INK, sw=1.5))
    tb_c, _, _ = textbox(cx - 100, cy - 35, "Передбачення H·x̂\n(центр непевності)", size=11, fill="#eff6ff", stroke=BLUE, sw=1.2)
    p.append(tb_c)

    # Точка A: велика евклідова відстань, але вздовж великої осі непевності -> d² < γ (ПРИЙНЯТО)
    pt_a_x = cx + 155 * cos_a - 15 * sin_a
    pt_a_y = cy + 155 * sin_a + 15 * cos_a
    p.append(line(cx, cy, pt_a_x, pt_a_y, color=GREEN, sw=1.8))
    p.append(circle(pt_a_x, pt_a_y, 6, fill=GREEN, stroke=INK, sw=1.5))
    tb_a, _, _ = textbox(pt_a_x + 90, pt_a_y + 35, "Вимір A: велика евклідова нев'язка,\nале d² = 3.8 < γ  →  ПРИЙНЯТО\n(висока непевність моделі вздовж осі)",
                         size=10.5, fill="#f0fdf4", stroke=GREEN, sw=1.4, color=INK)
    p.append(tb_a)

    # Точка B: мала евклідова відстань, але вздовж малої осі непевності -> d² > γ (ВИКИНУТО)
    pt_b_x = cx - 20 * cos_a + 92 * sin_a
    pt_b_y = cy - 20 * sin_a - 92 * cos_a
    p.append(line(cx, cy, pt_b_x, pt_b_y, color=RED, sw=1.8))
    p.append(circle(pt_b_x, pt_b_y, 6, fill=RED, stroke=INK, sw=1.5))
    tb_b, _, _ = textbox(pt_b_x - 130, pt_b_y - 45, "Вимір B: мала евклідова нев'язка,\nале d² = 14.5 > γ  →  ВИКИНУТО\n(вздовж осі високої впевненості)",
                         size=10.5, fill="#fef2f2", stroke=RED, sw=1.4, color=INK)
    p.append(tb_b)

    # Підпис межі брами
    p.append(text(cx + 175 * cos_a + 85 * sin_a, cy + 175 * sin_a - 85 * cos_a,
                  "Межа брами валідації: d² = yᵀS⁻¹y = γ", size=11, color=GREEN, bold=True, anchor="start"))

    render(os.path.join(OUT, "innovation-geometry.svg"), W, H, *p,
           title="Геометрія брами валідації: відстань Махаланобіса проти евклідової")


# ── 2. validation-gate-chi2: Розподіл хі-квадрат і порогові зони ───────────────
def fig_validation_gate_chi2():
    W, H = 760, 390
    ox, oy = 80, 310
    gw, gh = 620, 230
    p = []

    # Осі координат
    p.append(arrow(ox, oy, ox + gw + 25, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=INK, sw=1.6))
    p.append(text(ox + gw + 20, oy + 24, "Нормована нев'язка d² (квадрат Махаланобіса)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - gh - 15, "Густина ймовірності f(d²)", size=11, color=INK, italic=True, anchor="end"))

    # Крива хі-квадрат для m=2: f(x) = 0.5 * exp(-x/2)
    def chi2_2d(d2):
        return 0.5 * math.exp(-0.5 * d2)

    scale_x = gw / 15.0
    scale_y = (gh * 0.82) / 0.5

    pts = []
    for i in range(0, 151):
        d2 = 15.0 * i / 150.0
        px = ox + d2 * scale_x
        py = oy - chi2_2d(d2) * scale_y
        pts.append((px, py, d2))

    g1, g2 = 5.99, 9.21

    # Заливка зеленої зони
    poly_green = ["%.1f,%.1f" % (ox, oy)]
    for px, py, d2 in pts:
        if d2 <= g1:
            poly_green.append("%.1f,%.1f" % (px, py))
    x_g1 = ox + g1 * scale_x
    poly_green.append("%.1f,%.1f" % (x_g1, oy))
    p.append('<polygon points="%s" fill="#dcfce7" opacity="0.85"/>' % " ".join(poly_green))

    # Заливка жовтої зони
    poly_yellow = ["%.1f,%.1f" % (x_g1, oy)]
    for px, py, d2 in pts:
        if g1 <= d2 <= g2:
            poly_yellow.append("%.1f,%.1f" % (px, py))
    x_g2 = ox + g2 * scale_x
    poly_yellow.append("%.1f,%.1f" % (x_g2, oy))
    p.append('<polygon points="%s" fill="#fef3c7" opacity="0.85"/>' % " ".join(poly_yellow))

    # Заливка червоної зони
    poly_red = ["%.1f,%.1f" % (x_g2, oy)]
    for px, py, d2 in pts:
        if d2 >= g2:
            poly_red.append("%.1f,%.1f" % (px, py))
    poly_red.append("%.1f,%.1f" % (ox + 15.0 * scale_x, oy))
    p.append('<polygon points="%s" fill="#fee2e2" opacity="0.85"/>' % " ".join(poly_red))

    # Сама лінія графіка
    poly_line = " ".join("%.1f,%.1f" % (px, py) for px, py, _ in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
             % (poly_line, INK))

    # Вертикальні порогові лінії
    p.append(line(x_g1, oy, x_g1, oy - chi2_2d(g1) * scale_y - 45, color=YELLOW, sw=1.8, dash="4,3"))
    p.append(line(x_g2, oy, x_g2, oy - chi2_2d(g2) * scale_y - 45, color=RED, sw=1.8, dash="4,3"))

    # Позначки на осі X
    p.append(text(ox, oy + 16, "0", size=11, color=INK))
    p.append(text(x_g1, oy + 16, "γ₁ = 5.99", size=11, color=YELLOW, bold=True))
    p.append(text(x_g2, oy + 16, "γ₂ = 9.21", size=11, color=RED, bold=True))

    # Описи зон
    tb_z1, _, _ = textbox(ox + 105, oy - 145, "Зона довіри (95%)\nd² ≤ γ₁\nСтандартне оновлення",
                          size=11, fill="#ffffff", stroke=GREEN, sw=1.4, color=GREEN, bold=True)
    tb_z2, _, _ = textbox(ox + 310, oy - 180, "Зона сумніву (95%..99%)\nγ₁ < d² ≤ γ₂\nМ'яке масштабування R",
                          size=11, fill="#ffffff", stroke=YELLOW, sw=1.4, color=YELLOW, bold=True)
    tb_z3, _, _ = textbox(ox + 500, oy - 120, "Зона викиду (хвіст α = 1%)\nd² > γ₂\nПовне відсікання виміру",
                          size=11, fill="#ffffff", stroke=RED, sw=1.4, color=RED, bold=True)
    p.append(tb_z1)
    p.append(tb_z2)
    p.append(tb_z3)

    # Стрілка на хвіст
    p.append(arrow(ox + 440, oy - 95, ox + 420, oy - 12, color=RED, sw=1.4))

    render(os.path.join(OUT, "validation-gate-chi2.svg"), W, H, *p,
           title="Критерій хі-квадрат для 2D виміру: зони довіри, м'якої корекції та відсікання")


# ── 3. gating-decision-pipeline: Повний пайплайн перевірки інновацій ───────────
def fig_gating_decision_pipeline():
    W, H = 760, 520
    p = []

    # Блоки зверху вниз і розгалуження
    # 1. Вхід: вимір z_k та прогноз стану x̂⁻, P⁻
    tb1, w1, h1 = textbox(180, 70, "Вхідні дані кроку k:\nВимір zₖ, Прогноз x̂⁻, Коваріація P⁻",
                          size=11.5, fill="#eff6ff", stroke=BLUE, sw=1.5, bold=True, color=BLUE)
    p.append(tb1)

    # 2. Обчислення нев'язки y та коваріації S
    tb2, w2, h2 = textbox(180, 165, "1. Нев'язка спостереження:\nyₖ = zₖ − H·x̂⁻\nSₖ = H·P⁻·Hᵀ + Rₖ",
                          size=11.5, fill="#f8fafc", stroke=LINE, sw=1.5, bold=True)
    p.append(tb2)
    p.append(arrow(180, 70 + h1/2, 180, 165 - h2/2, color=LINE, sw=1.6))

    # 3. Обчислення нормованого квадрата d²
    tb3, w3, h3 = textbox(180, 265, "2. Нормований квадрат (NIS):\nd² = yₖᵀ · Sₖ⁻¹ · yₖ",
                          size=11.5, fill="#f8fafc", stroke=PURPLE, sw=1.6, bold=True, color=PURPLE)
    p.append(tb3)
    p.append(arrow(180, 165 + h2/2, 180, 265 - h3/2, color=LINE, sw=1.6))

    # 4. Ромб розгалуження (вузол перевірки d²)
    cx_d, cy_d = 180, 380
    rw, rh = 110, 42
    pts_diamond = "%d,%d %d,%d %d,%d %d,%d" % (cx_d, cy_d - rh, cx_d + rw, cy_d, cx_d, cy_d + rh, cx_d - rw, cy_d)
    p.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="2.0"/>' % (pts_diamond, INK))
    p.append(text(cx_d, cy_d - 6, "Перевірка", size=11, bold=True, color=INK))
    p.append(text(cx_d, cy_d + 12, "критерію χ²", size=11, bold=True, color=INK))
    p.append(arrow(180, 265 + h3/2, 180, cy_d - rh, color=LINE, sw=1.6))

    # Три гілки з ромба:
    # Гілка 1: d² <= γ₁ -> Звичайне оновлення
    tb_b1, _, _ = textbox(470, 270, "A. Прийняти вимір (d² ≤ γ₁):\nK = P⁻·Hᵀ·S⁻¹\nx̂ = x̂⁻ + K·yₖ\nP = (I − K·H)·P⁻",
                          size=11, fill="#f0fdf4", stroke=GREEN, sw=1.5, color=GREEN, bold=True)
    p.append(tb_b1)

    # Гілка 2: γ₁ < d² <= γ₂ -> М'яке масштабування
    tb_b2, _, _ = textbox(470, 380, "B. М'яке оновлення (γ₁ < d² ≤ γ₂):\ns = d² / γ₁  (масштаб шуму)\nR* = s·Rₖ;  перерахунок S, K\nx̂ = x̂⁻ + K*·yₖ",
                          size=11, fill="#fffbeb", stroke=YELLOW, sw=1.5, color=YELLOW, bold=True)
    p.append(tb_b2)

    # Гілка 3: d² > γ₂ -> Відсікання
    tb_b3, _, _ = textbox(470, 475, "C. Відкинути вимір (d² > γ₂):\nx̂ = x̂⁻;  P = P⁻  (пропуск)\nЛічильник викидів++; монітор NIS",
                          size=11, fill="#fef2f2", stroke=RED, sw=1.5, color=RED, bold=True)
    p.append(tb_b3)

    # Стрілки від ромба до гілок
    # До A
    p.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (cx_d + rw - 15, cy_d - 20, 320, 270, 360, 270, GREEN))
    p.append(text(300, 260, "d² ≤ γ₁", size=10.5, color=GREEN, bold=True))

    # До B
    p.append(arrow(cx_d + rw, cy_d, 360, cy_d, color=YELLOW, sw=1.8))
    p.append(text(320, cy_d - 8, "γ₁ < d² ≤ γ₂", size=10.5, color=YELLOW, bold=True))

    # До C
    p.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (cx_d + rw - 15, cy_d + 20, 320, 475, 360, 475, RED))
    p.append(text(300, 460, "d² > γ₂", size=10.5, color=RED, bold=True))

    # Фінальне зведення
    p.append(line(580, 270, 670, 270, color=GREEN, sw=1.5))
    p.append(line(580, 380, 670, 380, color=YELLOW, sw=1.5))
    p.append(line(580, 475, 670, 475, color=RED, sw=1.5))
    p.append(line(670, 270, 670, 475, color=INK, sw=1.5))
    p.append(arrow(670, 380, 720, 380, color=INK, sw=1.8))

    p.append(text(715, 365, "Наступний", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(715, 380, "такт k+1", size=10.5, color=INK, bold=True, anchor="start"))

    render(os.path.join(OUT, "gating-decision-pipeline.svg"), W, H, *p,
           title="Повний алгоритм валідації вимірювань і розгалуження обробки")


# ── 4. nis-consistency-tracking: Моніторинг здоров'я фільтра через NIS ─────────
def fig_nis_consistency_tracking():
    W, H = 760, 420
    ox, oy = 75, 340
    gw, gh = 635, 230
    p = []

    # Осі
    p.append(arrow(ox, oy, ox + gw + 25, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - gh - 35, color=INK, sw=1.6))
    p.append(text(ox + gw + 20, oy + 24, "Час / Номер кроку k", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 10, oy - gh - 22, "Нормований квадрат NIS (dₖ²)", size=11, color=INK, italic=True, anchor="end"))

    # Порогові рівні для 2D вимірювання (m=2)
    # Середнє E[d²] = 2.0
    # 95% поріг = 5.99
    # 99% поріг = 9.21
    scale_y = gh / 14.0
    y_mean = oy - 2.0 * scale_y
    y_95   = oy - 5.99 * scale_y
    y_99   = oy - 9.21 * scale_y

    # Довірчі смуги
    p.append(line(ox, y_mean, ox + gw, y_mean, color="#9ca3af", sw=1.2, dash="3,3"))
    p.append(line(ox, y_95, ox + gw, y_95, color=YELLOW, sw=1.5, dash="5,4"))
    p.append(line(ox, y_99, ox + gw, y_99, color=RED, sw=1.6, dash="6,4"))

    p.append(text(ox + gw - 5, y_mean - 6, "Теоретичне середнє E[d²] = m = 2", size=10, color=MUTED, anchor="end"))
    p.append(text(ox + gw - 5, y_95 - 6, "95% довірча межа (γ₁ = 5.99)", size=10, color=YELLOW, bold=True, anchor="end"))
    p.append(text(ox + gw - 5, y_99 - 6, "99% поріг відсікання (γ₂ = 9.21)", size=10, color=RED, bold=True, anchor="end"))

    # Траєкторія d_k^2 (40 кроків)
    nis_values = [
        1.8, 2.4, 0.9, 3.1, 1.5, 2.8, 1.2, 4.2, 2.1, 1.7,
        3.5, 0.8, 2.6, 1.9, 3.8, 2.2, 1.4, 3.0, 12.8, 2.1,
        1.6, 2.9, 0.7, 3.4, 2.0, 1.8, 2.5, 4.8, 5.5, 6.8,
        7.4, 8.1, 8.9, 9.6, 10.2, 11.0, 11.5, 12.1, 12.7, 13.2
    ]

    n_pts = len(nis_values)
    step_x = gw / (n_pts + 1)

    pts_line = []
    for i, val in enumerate(nis_values):
        px = ox + (i + 1) * step_x
        py = oy - min(val, 13.8) * scale_y
        pts_line.append((px, py, val, i + 1))

    # З'єднувальна ламана
    poly_str = " ".join("%.1f,%.1f" % (px, py) for px, py, _, _ in pts_line)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (poly_str, INK))

    # Точки на графіку
    for px, py, val, k in pts_line:
        if val > 9.21:
            p.append(circle(px, py, 4.5, fill=RED, stroke=INK, sw=1.2))
        elif val > 5.99:
            p.append(circle(px, py, 4, fill=YELLOW, stroke=INK, sw=1.2))
        else:
            p.append(circle(px, py, 3.5, fill=GREEN, stroke=INK, sw=1.0))

    # Анотація 1: Поодинокий викид (крок 19)
    p19_x, p19_y = pts_line[18][0], pts_line[18][1]
    tb_spike, _, _ = textbox(p19_x - 70, 75, "Поодинокий викид (GNSS multipath):\nd² = 12.8 > γ₂  →  Відкинуто брамою.\nОцінка стану не спотворена!",
                             size=10, fill="#ffffff", stroke=RED, sw=1.4, color=RED, bold=True)
    p.append(tb_spike)
    p.append(arrow(p19_x - 30, 105, p19_x - 4, p19_y - 8, color=RED, sw=1.4))

    # Анотація 2: Систематичне зростання (маневр / розбіжність)
    p35_x, p35_y = pts_line[33][0], pts_line[33][1]
    tb_drift, _, _ = textbox(p35_x - 80, 75, "Систематичний дрейф (маневр / модель):\nКовзне середнє NIS стабільно вище норми.\nПотрібно підняти шум Q або увімкнути тривогу!",
                             size=10, fill="#ffffff", stroke=PURPLE, sw=1.4, color=PURPLE, bold=True)
    p.append(tb_drift)
    p.append(arrow(p35_x - 40, 105, p35_x - 10, p35_y - 12, color=PURPLE, sw=1.4))

    render(os.path.join(OUT, "nis-consistency-tracking.svg"), W, H, *p,
           title="Часовий ряд нормованої нев'язки (NIS): відсікання викидів та діагностика розбіжності")


if __name__ == "__main__":
    fig_innovation_geometry()
    fig_validation_gate_chi2()
    fig_gating_decision_pipeline()
    fig_nis_consistency_tracking()
    print("All figures generated successfully.")
