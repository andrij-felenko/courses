# -*- coding: utf-8 -*-
"""Фігури до статті «Просторово-векторна ШІМ (SVPWM)».
  inverter-topology.svg          — трифазний інвертор напруги (VSI) та обмотки зіркою
  voltage-hexagon.svg            — гексагон 6 активних і 2 нульових векторів на (alpha, beta)
  volt-second-balance.svg        — вольт-секундний баланс і розклад вектора в секторі I
  seven-segment-switching.svg    — 7-сегментна симетрична комутація та таймери CCR1..CCR3
  common-mode-third-harmonic.svg — сідлоподібна фазна напруга та підмішування 3-ї гармоніки
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

A_COL = "#c0392b"   # Фаза A / червоний
B_COL = "#2457d6"   # Фаза B / синій
C_COL = "#27ae60"   # Фаза C / зелений
V_COL = "#8e44ad"   # Вектор V_ref / фіолетовий
N_COL = "#d35400"   # Нейтраль / помаранчевий
GRID  = "#dcdfe6"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Топологія трифазного інвертора напруги (VSI)
# ─────────────────────────────────────────────────────────────────────────────
def fig_inverter_topology():
    W, H = 840, 480
    f = []

    # Шини живлення
    f.append(line(40, 60, 520, 60, color=POS, sw=3))
    f.append(text(25, 65, "+V_dc", size=14, color=POS, bold=True))

    f.append(line(40, 420, 520, 420, color=NEG, sw=3))
    f.append(text(25, 425, "GND (0 В)", size=13, color=NEG, bold=True))

    # Конденсатор шини DC
    f.append(line(70, 60, 70, 220, color=POS, sw=1.8))
    f.append(line(50, 220, 90, 220, color=INK, sw=2.5))
    f.append(line(50, 235, 90, 235, color=INK, sw=2.5))
    f.append(line(70, 235, 70, 420, color=NEG, sw=1.8))
    f.append(text(38, 232, "C_dc", size=12, color=MUTED, anchor="end"))

    # Стійки інвертора A, B, C
    legs = [
        (170, 'A', A_COL, 'S_a'),
        (300, 'B', B_COL, 'S_b'),
        (430, 'C', C_COL, 'S_c')
    ]

    for x, name, col, s_var in legs:
        # Верхній ключ
        f.append(line(x, 60, x, 110, color=POS, sw=2))
        f.append(rect(x - 28, 110, 56, 50, fill="#fdfefe", stroke=col, sw=1.8))
        f.append(text(x, 132, "%s+" % name, size=13, bold=True, color=col))
        f.append(text(x, 148, "(верхній)", size=10, color=MUTED))

        # Діод паралельно верхньому ключу
        f.append(line(x + 28, 115, x + 28, 155, color=MUTED, sw=1.2))

        # Середня точка фази
        f.append(line(x, 160, x, 240, color=col, sw=2.2))
        f.append(circle(x, 240, 4.5, fill=col, stroke=col))
        f.append(text(x - 12, 236, "фаза %s" % name, size=12, bold=True, color=col, anchor="end"))

        # Нижній ключ
        f.append(line(x, 240, x, 290, color=col, sw=2))
        f.append(rect(x - 28, 290, 56, 50, fill="#fdfefe", stroke=col, sw=1.8))
        f.append(text(x, 312, "%s−" % name, size=13, bold=True, color=col))
        f.append(text(x, 328, "(нижній)", size=10, color=MUTED))

        # З'єднання з землею
        f.append(line(x, 340, x, 420, color=NEG, sw=2))

        # Керувальний сигнал
        f.append(fitbox(x - 38, 18, 76, 26, "%s ∈ {0, 1}" % s_var, size=11, bold=True, fill="#eef2f7", stroke=col))

    # Двигун зіркою (праворуч)
    mx, my = 680, 240
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fcfdfd" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' % (mx, my, 85, INK))
    f.append(text(mx, my - 95, "Статор BLDC / PMSM (зірка)", size=12, bold=True, color=INK))

    # Нейтраль
    nx, ny = mx, my
    f.append(circle(nx, ny, 5, fill=N_COL, stroke=N_COL))
    f.append(text(nx + 14, ny + 5, "N (нейтраль)", size=12, bold=True, color=N_COL, anchor="start"))
    f.append(text(nx + 14, ny + 20, "V_N = (V_a+V_b+V_c)/3", size=10, color=MUTED, anchor="start"))

    # Обмотка A (вгору-вліво)
    ax, ay = mx - 45, my - 45
    f.append(line(170, 240, 530, 240, color=A_COL, sw=2))
    f.append(line(530, 240, ax, ay, color=A_COL, sw=2))
    f.append(line(ax, ay, nx, ny, color=A_COL, sw=3))
    f.append(text(ax - 10, ay - 6, "обмотка A", size=11, bold=True, color=A_COL, anchor="end"))

    # Обмотка B (вниз-вліво)
    bx, by = mx - 45, my + 45
    f.append(line(300, 240, 500, 240, color=B_COL, sw=2))
    f.append(line(500, 240, 520, 310, color=B_COL, sw=2))
    f.append(line(520, 310, bx, by, color=B_COL, sw=2))
    f.append(line(bx, by, nx, ny, color=B_COL, sw=3))
    f.append(text(bx - 10, by + 16, "обмотка B", size=11, bold=True, color=B_COL, anchor="end"))

    # Обмотка C (праворуч)
    cx, cy = mx + 60, my
    f.append(line(430, 240, 480, 240, color=C_COL, sw=2))
    f.append(line(480, 240, 500, 380, color=C_COL, sw=2))
    f.append(line(500, 380, 750, 380, color=C_COL, sw=2))
    f.append(line(750, 380, cx, cy, color=C_COL, sw=2))
    f.append(line(cx, cy, nx, ny, color=C_COL, sw=3))
    f.append(text(cx + 8, cy - 8, "обмотка C", size=11, bold=True, color=C_COL, anchor="start"))

    render(os.path.join(IMG, "inverter-topology.svg"), W, H, *f, title="Топологія трифазного інвертора напруги (VSI)")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Гексагон базових векторів напруги на площині (alpha, beta)
# ─────────────────────────────────────────────────────────────────────────────
def fig_voltage_hexagon():
    W, H = 820, 620
    f = []

    cx, cy = 390, 310
    R = 210.0   # радіус вершин гексагона: |V_k| = 2/3 * V_dc
    R_in = R * math.sqrt(3) / 2.0  # R_inscribed = V_dc / sqrt(3) ≈ 181.86
    R_spwm = R * 3.0 / 4.0          # R_spwm = V_dc / 2 ≈ 157.5 (бо R = 2/3 Vdc -> Vdc/2 = 3/4 R)

    # Осі координат
    f.append(line(cx - 270, cy, cx + 270, cy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx + 285, cy + 5, "α", size=15, bold=True, color=INK, anchor="start"))

    f.append(line(cx, cy + 260, cx, cy - 260, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx, cy - 270, "β", size=15, bold=True, color=INK))

    # Коло SPWM (V_dc / 2)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#e74c3c" stroke-width="1.6" stroke-dasharray="5,4"/>' % (cx, cy, R_spwm))

    # Вписане коло SVPWM (V_dc / sqrt(3))
    f.append(circle(cx, cy, R_in, fill="#f4fbf7", stroke="#27ae60", sw=2.0))

    # Обчислення вершин гексагона
    vecs = [
        (0,   "V₁ (100)", "0°",   POS,   18,  5),
        (60,  "V₂ (110)", "60°",  POS,   14, -14),
        (120, "V₃ (010)", "120°", B_COL, -14, -14),
        (180, "V₄ (011)", "180°", B_COL, -18,  5),
        (240, "V₅ (001)", "240°", C_COL, -14,  18),
        (300, "V₆ (101)", "300°", C_COL,  14,  18),
    ]

    pts = []
    for deg, name, angle_str, col, tx_off, ty_off in vecs:
        rad = math.radians(deg)
        vx = cx + R * math.cos(rad)
        vy = cy - R * math.sin(rad)
        pts.append((vx, vy))

    # Лінії гексагона
    for i in range(6):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 6]
        f.append(line(x1, y1, x2, y2, color=INK, sw=2.2))

    # Сектори (I .. VI)
    sec_names = ["Сектор I", "Сектор II", "Сектор III", "Сектор IV", "Сектор V", "Сектор VI"]
    for s in range(6):
        mid_deg = 30 + s * 60
        mid_rad = math.radians(mid_deg)
        sx = cx + (R_in * 0.58) * math.cos(mid_rad)
        sy = cy - (R_in * 0.58) * math.sin(mid_rad)
        f.append(text(sx, sy, sec_names[s], size=13, bold=True, color="#4a5568"))

    # Стрілки активних векторів
    for i, (deg, name, angle_str, col, tx_off, ty_off) in enumerate(vecs):
        vx, vy = pts[i]
        f.append(arrow(cx, cy, vx, vy, color=col, sw=2.4))
        anchor = "start" if tx_off > 0 else ("end" if tx_off < 0 else "middle")
        f.append(text(vx + tx_off, vy + ty_off, name, size=13, bold=True, color=col, anchor=anchor))
        f.append(text(vx + tx_off, vy + ty_off + 14, "(%s)" % angle_str, size=10, color=MUTED, anchor=anchor))

    # Центр (нульові вектори)
    f.append(circle(cx, cy, 6, fill="#2c3e50", stroke="#2c3e50"))
    f.append(textbox(cx, cy + 32, "V₀ (000)\nV₇ (111)", size=11, bold=True, fill="#ffffff", stroke="#2c3e50")[0])

    # Легенда меж
    lx, ly = 635, 100
    f.append(textbox(lx, ly, "Межа SPWM:\nR = V_dc / 2", size=11, color="#c0392b", fill="#fdf2f2", stroke="#e74c3c")[0])
    f.append(textbox(lx, ly + 65, "Межа SVPWM:\nR = V_dc / √3\n(+15.5 %)", size=11, bold=True, color="#27ae60", fill="#ebfaf0", stroke="#27ae60")[0])

    render(os.path.join(IMG, "voltage-hexagon.svg"), W, H, *f, title="Шестикутник базових векторів напруги на площині (α, β)")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Вольт-секундний баланс у Секторі I
# ─────────────────────────────────────────────────────────────────────────────
def fig_volt_second_balance():
    W, H = 880, 520
    f = []

    ox, oy = 100, 430
    L = 320.0   # довжина векторів V1, V2

    # Вектор V1 (0°)
    v1x, v1y = ox + L, oy
    f.append(arrow(ox, oy, v1x, v1y, color=POS, sw=2.8))
    f.append(text(v1x + 14, v1y + 6, "V₁ (100) [2/3·V_dc]", size=13, bold=True, color=POS, anchor="start"))

    # Вектор V2 (60°)
    v2_rad = math.radians(60)
    v2x = ox + L * math.cos(v2_rad)
    v2y = oy - L * math.sin(v2_rad)
    f.append(arrow(ox, oy, v2x, v2y, color=B_COL, sw=2.8))
    f.append(text(v2x + 10, v2y - 12, "V₂ (110) [2/3·V_dc]", size=13, bold=True, color=B_COL, anchor="start"))

    # Заданий референсний вектор V_ref під кутом theta = 28°
    theta = 28.0
    th_rad = math.radians(theta)
    m = 0.82
    k1 = m * math.sin(math.radians(60 - theta)) / math.sin(math.radians(60))
    k2 = m * math.sin(math.radians(theta)) / math.sin(math.radians(60))

    # Точки проекцій
    p1x = ox + k1 * L
    p1y = oy

    p2x = ox + k2 * L * math.cos(v2_rad)
    p2y = oy - k2 * L * math.sin(v2_rad)

    vrx = p1x + (p2x - ox)
    vry = p1y + (p2y - oy)

    # Паралелограм (пунктирні лінії)
    f.append(line(p1x, p1y, vrx, vry, color=MUTED, sw=1.6, dash="5,4"))
    f.append(line(p2x, p2y, vrx, vry, color=MUTED, sw=1.6, dash="5,4"))

    # Проекції вздовж V1 і V2
    f.append(line(ox, oy, p1x, p1y, color=POS, sw=4.5))
    f.append(line(ox, oy, p2x, p2y, color=B_COL, sw=4.5))

    # Стрілка V_ref
    f.append(arrow(ox, oy, vrx, vry, color=V_COL, sw=3.2))
    f.append(textbox(vrx + 85, vry - 18, "V_ref (заданий вектор)\nV_ref·T_s = V₁·T₁ + V₂·T₂", size=11, bold=True, color=V_COL, fill="#fbf8fd", stroke=V_COL)[0])

    # Дуга кута theta
    arc_r = 75
    arc_pts = []
    for deg in range(0, int(theta) + 1):
        r = math.radians(deg)
        arc_pts.append((ox + arc_r * math.cos(r), oy - arc_r * math.sin(r)))
    d_str = "M " + " L ".join("%.1f,%.1f" % p for p in arc_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_str, INK))
    f.append(text(ox + 92, oy - 18, "θ", size=14, bold=True, color=INK))

    # Підписи T1 і T2 на осях
    f.append(textbox(p1x / 2 + ox / 2 + 10, oy + 28, "V₁ · (T₁ / T_s)", size=12, bold=True, color=POS, fill="#fdf2f2", stroke=POS)[0])
    f.append(textbox(p2x / 2 + ox / 2 - 45, p2y / 2 + oy / 2 - 20, "V₂ · (T₂ / T_s)", size=12, bold=True, color=B_COL, fill="#f0f4fd", stroke=B_COL)[0])

    # Блок формул праворуч
    bx, by = 680, 230
    formulas = (
        "Вольт-секундний баланс:\n"
        "V_ref · T_s = V₁ · T₁ + V₂ · T₂ + V₀ · T₀\n\n"
        "Часи активних векторів:\n"
        "T₁ = √3 · (T_s·|V_ref| / V_dc) · sin(60° − θ)\n"
        "T₂ = √3 · (T_s·|V_ref| / V_dc) · sin(θ)\n\n"
        "Час нульових векторів:\n"
        "T₀ = T_s − T₁ − T₂   (ділиться між V₀ і V₇)"
    )
    f.append(textbox(bx, by, formulas, size=11, pad=12, fill="#f8fafc", stroke=MUTED)[0])

    render(os.path.join(IMG, "volt-second-balance.svg"), W, H, *f, title="Вольт-секундний баланс і розклад вектора в Секторі I")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Симетричний 7-сегментний патерн комутації та таймери
# ─────────────────────────────────────────────────────────────────────────────
def fig_seven_segment_switching():
    W, H = 840, 520
    f = []

    # Часова вісь
    x0, x1 = 120, 760
    ts_w = x1 - x0
    mid_x = (x0 + x1) / 2

    # Межі 7 сегментів у Секторі I:
    # T0/4, T1/2, T2/2, T0/2 (center), T2/2, T1/2, T0/4
    # Відносні частки (приклад): T0 = 0.28 Ts, T1 = 0.44 Ts, T2 = 0.28 Ts
    # w0_4 = 0.07, w1_2 = 0.22, w2_2 = 0.14, w7_2 = 0.14 ...
    segs_frac = [0.07, 0.22, 0.14, 0.14, 0.14, 0.22, 0.07]
    seg_names = ["V₀ (000)", "V₁ (100)", "V₂ (110)", "V₇ (111)", "V₂ (110)", "V₁ (100)", "V₀ (000)"]
    seg_cols  = ["#e2e8f0",   "#fadbd8",   "#d4efdf",   "#d6eaf8",   "#d4efdf",   "#fadbd8",   "#e2e8f0"]
    seg_times = ["T₀/4",      "T₁/2",      "T₂/2",      "T₀/2",      "T₂/2",      "T₁/2",      "T₀/4"]

    # Обчислення X-координат меж сегментів
    boundaries = [x0]
    cur = x0
    for fr in segs_frac:
        cur += fr * ts_w
        boundaries.append(cur)
    boundaries[-1] = x1

    # 1. Верхній графік: Трикутний лічильник таймера (Center-Aligned)
    cy0, cy1 = 50, 160
    f.append(text(50, (cy0 + cy1) / 2, "Лічильник\nтаймера", size=12, bold=True, color=INK, anchor="start"))
    f.append(line(x0, cy1, x1, cy1, color=MUTED, sw=1.2))
    f.append(line(x0, cy1, mid_x, cy0, color="#8e44ad", sw=2.2))
    f.append(line(mid_x, cy0, x1, cy1, color="#8e44ad", sw=2.2))

    # Рівні порівняння CCR1, CCR2, CCR3
    ccr_a_y = cy1 - (cy1 - cy0) * (1.0 - 0.07)
    ccr_b_y = cy1 - (cy1 - cy0) * (1.0 - (0.07 + 0.22))
    ccr_c_y = cy1 - (cy1 - cy0) * (1.0 - (0.07 + 0.22 + 0.14))

    f.append(line(x0, ccr_a_y, x1, ccr_a_y, color=A_COL, sw=1.4, dash="4,4"))
    f.append(text(x1 + 10, ccr_a_y + 4, "CCR_A (фаза A)", size=11, bold=True, color=A_COL, anchor="start"))

    f.append(line(x0, ccr_b_y, x1, ccr_b_y, color=B_COL, sw=1.4, dash="4,4"))
    f.append(text(x1 + 10, ccr_b_y + 4, "CCR_B (фаза B)", size=11, bold=True, color=B_COL, anchor="start"))

    f.append(line(x0, ccr_c_y, x1, ccr_c_y, color=C_COL, sw=1.4, dash="4,4"))
    f.append(text(x1 + 10, ccr_c_y + 4, "CCR_C (фаза C)", size=11, bold=True, color=C_COL, anchor="start"))

    # 2. Графіки логічних сигналів фаз S_a, S_b, S_c
    phase_y = [
        (210, 'S_a', A_COL, 1),  # ввімкнено від сегмента 1 до 5
        (270, 'S_b', B_COL, 2),  # ввімкнено від сегмента 2 до 4
        (330, 'S_c', C_COL, 3),  # ввімкнено тільки в сегменті 3
    ]

    for py, pname, pcol, start_seg in phase_y:
        f.append(text(60, py - 5, "%s" % pname, size=14, bold=True, color=pcol, anchor="start"))
        on_x_start = boundaries[start_seg]
        on_x_end   = boundaries[7 - start_seg]

        # Базові лінії нуля
        f.append(line(x0, py, on_x_start, py, color=pcol, sw=2.2))
        f.append(line(on_x_end, py, x1, py, color=pcol, sw=2.2))

        # Перепад вгору
        f.append(line(on_x_start, py, on_x_start, py - 30, color=pcol, sw=2.2))
        # Високий рівень
        f.append(line(on_x_start, py - 30, on_x_end, py - 30, color=pcol, sw=2.5))
        # Перепад вниз
        f.append(line(on_x_end, py - 30, on_x_end, py, color=pcol, sw=2.2))

    # Вертикальні роздільники сегментів (пунктир)
    for bx in boundaries:
        f.append(line(bx, cy0, bx, 440, color="#cbd5e1", sw=1.0, dash="3,3"))

    # 3. Блоки 7 сегментів унизу
    seg_y = 390
    for i in range(7):
        bx0 = boundaries[i]
        bx1 = boundaries[i + 1]
        bw  = bx1 - bx0
        f.append(rect(bx0 + 1, seg_y, bw - 2, 45, fill=seg_cols[i], stroke=MUTED, sw=1.0))
        f.append(text(bx0 + bw / 2, seg_y + 18, seg_names[i], size=10, bold=True, color=INK))
        f.append(text(bx0 + bw / 2, seg_y + 34, seg_times[i], size=10, color=MUTED))

    # Стрілка періоду T_s
    f.append(line(x0, 465, x1, 465, color=INK, sw=1.5))
    f.append(circle(x0, 465, 3, fill=INK, stroke=INK))
    f.append(circle(x1, 465, 3, fill=INK, stroke=INK))
    f.append(text(mid_x, 485, "Повний період ШІМ T_s (симетрично відносно центру)", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "seven-segment-switching.svg"), W, H, *f, title="Симетричний 7-сегментний патерн комутації та таймери порівняння")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Сідлоподібна форма напруги та підмішування 3-ї гармоніки
# ─────────────────────────────────────────────────────────────────────────────
def fig_common_mode_third_harmonic():
    W, H = 840, 560
    f = []

    # 3 графіки по вертикалі:
    # 1. Фазна напруга відносно землі V_a(t) (сідлоподібна форма)
    # 2. Синфазна нульова напруга V_zero(t) (3-тя гармоніка)
    # 3. Фазно-нейтральна напруга V_an(t) та лінійна V_ab(t) (чисті синуси!)

    x0, x1 = 120, 760
    w_graph = x1 - x0

    plots = [
        (90,  "1. Фазна напруга V_a(t) (ключ до землі GND): «сідло» (0..V_dc)", POS),
        (260, "2. Синфазна нульова напруга V_zero(t) (3-тя гармоніка)", "#d35400"),
        (430, "3. Напруга на обмотці V_an(t) = V_a(t) − V_zero(t) (чистий синус!)", "#27ae60"),
    ]

    for base_y, label, col in plots:
        f.append(text(x0, base_y - 45, label, size=13, bold=True, color=col, anchor="start"))
        # Нульова вісь
        f.append(line(x0, base_y, x1, base_y, color=MUTED, sw=1.2))
        # Межі періоду 0° .. 360°
        f.append(line(x0, base_y - 35, x0, base_y + 35, color=MUTED, sw=1.0))
        f.append(line(x1, base_y - 35, x1, base_y + 35, color=MUTED, sw=1.0))
        f.append(line(x0 + w_graph / 2, base_y - 35, x0 + w_graph / 2, base_y + 35, color=MUTED, sw=1.0, dash="3,3"))

        f.append(text(x0, base_y + 20, "0°", size=10, color=MUTED))
        f.append(text(x0 + w_graph / 2, base_y + 20, "180°", size=10, color=MUTED))
        f.append(text(x1, base_y + 20, "360°", size=10, color=MUTED))

    # Побудова кривих по точках
    n_pts = 180
    pts_va = []
    pts_v0 = []
    pts_van = []

    amp = 30.0   # пікселів амплітуди

    for i in range(n_pts + 1):
        deg = i * (360.0 / n_pts)
        rad = math.radians(deg)
        x = x0 + (deg / 360.0) * w_graph

        # 3 фази
        va_sin = math.sin(rad)
        vb_sin = math.sin(rad - 2 * math.pi / 3)
        vc_sin = math.sin(rad - 4 * math.pi / 3)

        # Синфазний зсув нульової послідовності SVPWM:
        # v_zero = -0.5 * (max(va, vb, vc) + min(va, vb, vc))
        v_max = max(va_sin, vb_sin, vc_sin)
        v_min = min(va_sin, vb_sin, vc_sin)
        v_zero = -0.5 * (v_max + v_min)

        # Сідлоподібна напруга
        va_saddle = (va_sin + v_zero) * 1.1547  # помножена на 2/sqrt(3)

        # y-координати
        y1 = 90  - va_saddle * amp
        y2 = 260 - v_zero * 1.1547 * amp * 1.8
        y3 = 430 - va_sin * 1.1547 * amp

        pts_va.append((x, y1))
        pts_v0.append((x, y2))
        pts_van.append((x, y3))

    def to_path(pts):
        return "M " + " L ".join("%.1f,%.1f" % p for p in pts)

    # Малювання кривих
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (to_path(pts_va), POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (to_path(pts_v0), "#d35400"))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (to_path(pts_van), "#27ae60"))

    # Позначки сплющеної верхівки
    f.append(line(x0 + w_graph * 0.18, 90 - 1.0 * amp * 1.1547, x0 + w_graph * 0.32, 90 - 1.0 * amp * 1.1547, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(x0 + w_graph * 0.25, 90 - 1.0 * amp * 1.1547 - 8, "сплющена верхівка (без кліпінгу)", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "common-mode-third-harmonic.svg"), W, H, *f, title="Сідлоподібна форма фазної напруги та компенсація 3-ї гармоніки")


if __name__ == "__main__":
    fig_inverter_topology()
    fig_voltage_hexagon()
    fig_volt_second_balance()
    fig_seven_segment_switching()
    fig_common_mode_third_harmonic()
    print("OK: generated 5 figures in img/")
