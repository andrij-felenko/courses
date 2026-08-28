# -*- coding: utf-8 -*-
"""Фігури до теми «Холл-енкодери».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Фізика ефекту Холла ──────────────────────────────────────────────────
def fig_hall_physics():
    W, H = 760, 420
    f = [text(W / 2, 28, "Фізика ефекту Холла: сила Лоренца та поперечна різниця потенціалів", size=16, bold=True)]

    # Тіло напівпровідникової пластинки (3D-аксонометрія або ізометричний паралелепіпед)
    # Координати базової передньої грані
    ox, oy = 210, 190
    pw, ph, pd = 240, 80, 70  # ширина, висота, глибина

    # Задні грані пластинки (легка заливка)
    dx_iso, dy_iso = 60, -35
    top_face = ("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"
                % (ox, oy, ox + pw, oy, ox + pw + dx_iso, oy + dy_iso, ox + dx_iso, oy + dy_iso))
    f.append('<path d="%s" fill="#e8eff9" stroke="%s" stroke-width="1.5"/>' % (top_face, LINE))

    # Права грань
    right_face = ("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"
                  % (ox + pw, oy, ox + pw + dx_iso, oy + dy_iso, ox + pw + dx_iso, oy + ph + dy_iso, ox + pw, oy + ph))
    f.append('<path d="%s" fill="#d0dfef" stroke="%s" stroke-width="1.5"/>' % (right_face, LINE))

    # Передня грань
    front_face = rect(ox, oy, pw, ph, fill="#f2f6fc", stroke=LINE, sw=1.8, rx=0)
    f.append(front_face)

    # Напрямок струму I (вздовж пластини: зліва направо)
    f.append(arrow(ox - 70, oy + ph / 2, ox - 10, oy + ph / 2, color=POS, sw=2.5))
    f.append(text(ox - 45, oy + ph / 2 - 12, "Струм I (вздовж X)", size=12, color=POS, bold=True))

    f.append(arrow(ox + pw + dx_iso + 10, oy + ph / 2 + dy_iso, ox + pw + dx_iso + 70, oy + ph / 2 + dy_iso, color=POS, sw=2.5))

    # Магнітне поле B (вертикально вгору: перпендикулярно пластині)
    for bx_off in [50, 120, 190]:
        f.append(arrow(ox + bx_off + dx_iso * 0.5, oy + ph + 45 + dy_iso * 0.5,
                       ox + bx_off + dx_iso * 0.5, oy - 45 + dy_iso * 0.5, color=FIELD, sw=2.2))
    f.append(text(ox + 120 + dx_iso * 0.5, oy - 55 + dy_iso * 0.5, "Магнітне поле B (вздовж Z)", size=12, color=FIELD, bold=True))

    # Рухомі носії заряду (електрони з дрейфовою швидкістю v_d вліво)
    f.append(circle(ox + 80, oy + ph / 2 - 8, 11, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(ox + 80, oy + ph / 2 - 4, "e⁻", size=11, color=NEG, bold=True))
    f.append(arrow(ox + 65, oy + ph / 2 - 8, ox + 35, oy + ph / 2 - 8, color=MUTED, sw=1.5))
    f.append(text(ox + 50, oy + ph / 2 - 20, "v_d", size=10, color=MUTED, italic=True))

    # Стрілка сили Лоренца F_L
    f.append(arrow(ox + 80, oy + ph / 2 + 6, ox + 80, oy + ph - 14, color="#d35400", sw=2.2))
    f.append(text(ox + 94, oy + ph / 2 + 22, "Сила F_L", size=10.5, color="#d35400", bold=True, anchor="start"))

    # Накопичення негативних зарядів на передній грані та позитивних на задній
    for i in range(5):
        f.append(text(ox + 35 + i * 42, oy + ph - 6, "−", size=15, color=NEG, bold=True))
        f.append(text(ox + 35 + i * 42 + dx_iso, oy + 12 + dy_iso, "+", size=15, color=POS, bold=True))

    # Поперечне електричне поле Холла E_H (від плюса до мінуса)
    f.append(arrow(ox + 165 + dx_iso * 0.6, oy + 18 + dy_iso * 0.6, ox + 165, oy + ph - 18, color=POS, sw=1.8))
    f.append(text(ox + 175, oy + ph / 2 - 10, "Поле E_H", size=10.5, color=POS, bold=True, anchor="start"))

    # Вольтметр поперечної напруги Холла V_H
    vx, vy = ox + pw / 2, oy + ph + 60
    f.append(line(ox + pw / 2, oy + ph, vx, vy - 20, color=LINE, sw=1.5))
    f.append(line(ox + pw / 2 + dx_iso, oy + dy_iso, vx + 90, oy + dy_iso - 15, color=LINE, sw=1.2, dash="3 3"))
    f.append(line(vx + 90, oy + dy_iso - 15, vx + 20, vy, color=LINE, sw=1.2, dash="3 3"))

    f.append(circle(vx, vy, 20, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(vx, vy + 5, "V_H", size=12.5, bold=True))
    f.append(text(vx, vy + 38, "Напруга Холла: V_H = (R_H / d) · I · B", size=11.5, bold=True))

    # Пояснювальний блок праворуч
    info_box = fitbox(550, 110, 190, 240,
                      "Рівновага сил:\n"
                      "q · E_H = q · v_d · B\n\n"
                      "Густина струму:\n"
                      "j = n · q · v_d\n\n"
                      "Коефіцієнт Холла:\n"
                      "R_H = 1 / (n · q)\n\n"
                      "У напівпровіднику n мала,\n"
                      "тому v_d і V_H у 10⁶ разів\n"
                      "вищі, ніж у металі.",
                      size=11, fill="#fdfbf7", stroke="#dcd6cd")
    f.append(info_box)

    render(os.path.join(IMG, "hall-physics.svg"), W, H, *f)


# ── 2. Дискретні датчики Холла в BLDC ───────────────────────────────────────
def fig_bldc_hall_commutation():
    W, H = 760, 420
    f = [text(W / 2, 28, "Комутація BLDC-двигуна за трьома датчиками Холла (120°)", size=16, bold=True)]

    # Ліва частина: Ротор BLDC з трьома датчиками H1, H2, H3
    cx, cy = 180, 220
    R_stator = 110
    R_rotor = 75

    # Статор (зовнішнє кільце)
    f.append(circle(cx, cy, R_stator, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(circle(cx, cy, R_rotor, fill="#ffffff", stroke=LINE, sw=1.5))

    # Полюси ротора (2-полюсний N-S ротор, N - червоний, S - синій)
    ang = math.radians(25)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    path_n = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f Z"
              % (cx - R_rotor * sin_a, cy + R_rotor * cos_a, R_rotor, R_rotor, cx + R_rotor * sin_a, cy - R_rotor * cos_a))
    path_s = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f Z"
              % (cx + R_rotor * sin_a, cy - R_rotor * cos_a, R_rotor, R_rotor, cx - R_rotor * sin_a, cy + R_rotor * cos_a))
    f.append('<path d="%s" fill="#fdecea" stroke="%s" stroke-width="1.2"/>' % (path_n, POS))
    f.append('<path d="%s" fill="#eaf0fd" stroke="%s" stroke-width="1.2"/>' % (path_s, NEG))
    f.append(text(cx + 25 * cos_a, cy + 25 * sin_a, "N", size=15, color=POS, bold=True))
    f.append(text(cx - 25 * cos_a, cy - 25 * sin_a, "S", size=15, color=NEG, bold=True))
    f.append(circle(cx, cy, 14, fill="#d8dde4", stroke=LINE, sw=1.2))

    # Стрілка обертання ротора
    f.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + 45, cy - 55, 60, 60, cx + 65, cy - 20, LINE))

    # 3 датчики Холла: H1 при 0°, H2 при 120°, H3 при 240°
    h_angles = [0, 120, 240]
    h_labels = ["H1 (0°)", "H2 (120°)", "H3 (240°)"]
    h_colors = ["#d97706", "#2563eb", "#059669"]

    for i, (ha, hl, hc) in enumerate(zip(h_angles, h_labels, h_colors)):
        rad = math.radians(ha - 90)  # 0° вгорі
        hx = cx + (R_stator + 4) * math.cos(rad)
        hy = cy + (R_stator + 4) * math.sin(rad)
        f.append(rect(hx - 14, hy - 10, 28, 20, fill="#ffffff", stroke=hc, sw=2, rx=4))
        f.append(text(hx, hy + 4, "H%d" % (i + 1), size=10.5, color=hc, bold=True))

    f.append(text(cx, cy + R_stator + 36, "3 датчики зі зсувом 120° ел.", size=12, bold=True))

    # Права частина: Часові діаграми шести кроків комутації
    gx = 390
    gw = 330
    step_w = gw / 6.0

    f.append(text(gx + gw / 2, 60, "6 кроків комутації (сектори по 60° ел.)", size=13, bold=True))

    for s in range(6):
        sx = gx + s * step_w
        f.append(line(sx, 75, sx, 340, color="#e5e7eb", sw=1, dash="4 2"))
        f.append(text(sx + step_w / 2, 90, "Крок %d" % (s + 1), size=10, color=MUTED, bold=True))

    patterns = [
        ("H1", [1, 1, 1, 0, 0, 0], 120, "#d97706"),
        ("H2", [0, 0, 1, 1, 1, 0], 180, "#2563eb"),
        ("H3", [1, 0, 0, 0, 1, 1], 240, "#059669"),
    ]

    for name, bits, y_base, col in patterns:
        f.append(text(gx - 25, y_base + 12, name, size=11.5, color=col, bold=True, anchor="end"))
        path_d = ["M%.1f %.1f" % (gx, y_base + (20 if bits[0] == 0 else 0))]
        for s in range(6):
            b = bits[s]
            y_val = y_base if b == 1 else y_base + 20
            path_d.append("L%.1f %.1f" % (gx + (s + 1) * step_w, y_val))
            if s < 5 and bits[s + 1] != b:
                next_y = y_base if bits[s + 1] == 1 else y_base + 20
                path_d.append("L%.1f %.1f" % (gx + (s + 1) * step_w, next_y))
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), col))

    states = ["101 (5)", "100 (4)", "110 (6)", "010 (2)", "011 (3)", "001 (1)"]
    for s in range(6):
        sx = gx + s * step_w + step_w / 2
        f.append(textbox(sx, 305, states[s], size=10, pad=4, fill="#f3f4f6", stroke=MUTED, sw=1)[0])

    f.append(text(gx + gw / 2, 345, "Заборонені стани помилки: 000 та 111", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "bldc-hall-commutation.svg"), W, H, *f)


# ── 3. 2D Диференційний масив Холла та компенсація завад ────────────────────
def fig_differential_hall_array():
    W, H = 760, 420
    f = [text(W / 2, 28, "2D диференційний масив Холла: придушення синфазної магнітної завади", size=16, bold=True)]

    # Ліва частина: Кремнієвий кристал із 4 сенсорами (X1, X2, Y1, Y2) та магнітом над ними
    cx, cy = 180, 220

    f.append(rect(cx - 100, cy - 100, 200, 200, fill="#f4f6f8", stroke="#64748b", sw=2, rx=8))
    f.append(text(cx, cy - 80, "Кристал мікросхеми (AS5048 / MA730)", size=11, color=MUTED, bold=True))

    dist = 50
    sensors = [
        ("X+", cx - dist, cy, "#d97706"),
        ("X−", cx + dist, cy, "#d97706"),
        ("Y+", cx, cy - dist, "#2563eb"),
        ("Y−", cx, cy + dist, "#2563eb"),
    ]

    for label, sx, sy, col in sensors:
        f.append(rect(sx - 16, sy - 16, 32, 32, fill="#ffffff", stroke=col, sw=2, rx=4))
        f.append(text(sx, sy + 4, label, size=11, color=col, bold=True))

    f.append(arrow(cx - dist, cy + 22, cx - dist, cy + 38, color="#d97706", sw=2))
    f.append(text(cx - dist, cy + 50, "+Bx", size=10, color="#d97706", bold=True))

    f.append(arrow(cx + dist, cy - 22, cx + dist, cy - 38, color="#d97706", sw=2))
    f.append(text(cx + dist, cy - 50, "−Bx", size=10, color="#d97706", bold=True))

    for zx in [cx - 80, cx - 30, cx + 30, cx + 80]:
        f.append(arrow(zx, cy - 65, zx, cy - 35, color=FIELD, sw=1.5))
    f.append(text(cx, cy + 85, "Зовнішня завада B_ext (однорідна)", size=10.5, color=FIELD, bold=True))

    rx = 390
    rw = 340

    box1 = fitbox(rx, 65, rw, 130,
                  "Диференційне вимірювання X-каналу:\n\n"
                  "V(X+) = +Bx_магніт + B_ext\n"
                  "V(X−) = −Bx_магніт + B_ext\n\n"
                  "Vx = V(X+) − V(X−) = 2 · Bx_магніт\n"
                  "→ Завада B_ext ідеально компенсується!",
                  size=11.5, fill="#fef9ee", stroke="#d97706")
    f.append(box1)

    box2 = fitbox(rx, 210, rw, 100,
                  "Ортогональні компоненти поля:\n\n"
                  "Bx(θ) = B₀ · cos(θ)\n"
                  "By(θ) = B₀ · sin(θ)",
                  size=12, fill="#eff6ff", stroke="#2563eb")
    f.append(box2)

    box3 = fitbox(rx, 325, rw, 75,
                  "Обчислення абсолютного кута (CORDIC / DSP):\n\n"
                  "θ = atan2(By, Bx) = atan2(sin θ, cos θ)",
                  size=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    f.append(box3)

    render(os.path.join(IMG, "differential-hall-array.svg"), W, H, *f)


# ── 4. Зазор і механічні похибки ───────────────────────────────────────────
def fig_air_gap_and_misalignment():
    W, H = 760, 420
    f = [text(W / 2, 28, "Механічне встановлення: робочий зазор, ексцентриситет та перекіс", size=16, bold=True)]

    bw = 220
    bh = 320
    gap = 20
    y_top = 60

    # Блок 1: Робочий зазор (Air Gap)
    b1_x = 20
    f.append(rect(b1_x, y_top, bw, bh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(b1_x + bw / 2, y_top + 24, "1. Робочий зазор (Air Gap)", size=12.5, bold=True))

    mx1, my1 = b1_x + bw / 2, y_top + 90
    f.append(rect(mx1 - 35, my1 - 25, 35, 30, fill="#fdecea", stroke=POS, sw=1.5, rx=0))
    f.append(rect(mx1, my1 - 25, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=0))
    f.append(text(mx1 - 18, my1 - 6, "N", size=13, color=POS, bold=True))
    f.append(text(mx1 + 18, my1 - 6, "S", size=13, color=NEG, bold=True))
    f.append(rect(mx1 - 12, my1 - 50, 24, 25, fill="#e5e7eb", stroke=LINE, sw=1.2))

    cx1, cy1 = mx1, my1 + 65
    f.append(rect(cx1 - 45, cy1, 90, 20, fill="#334155", stroke=LINE, sw=1.5, rx=2))
    f.append(text(cx1, cy1 + 14, "IC Sensor", size=10, color="#ffffff", bold=True))

    f.append(arrow(cx1 + 55, my1 + 5, cx1 + 55, cy1, color=FIELD, sw=1.8))
    f.append(arrow(cx1 + 55, cy1, cx1 + 55, my1 + 5, color=FIELD, sw=1.8))
    f.append(text(cx1 + 65, my1 + 35, "0.5–2 мм", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(textbox(b1_x + bw / 2, y_top + 235,
                     "Залежність індукції: B ∝ 1/z³\n"
                     "Занадто близько → насичення\n"
                     "Занадто далеко → шум АЦП\n"
                     "АРУ (AGC) стабілізує сигнал",
                     size=10.5, pad=6, fill="#f8fafc", stroke=MUTED)[0])

    # Блок 2: Радіальний ексцентриситет (Off-Axis)
    b2_x = b1_x + bw + gap
    f.append(rect(b2_x, y_top, bw, bh, fill="#ffffff", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(b2_x + bw / 2, y_top + 24, "2. Радіальний зсув (Δr)", size=12.5, color="#d97706", bold=True))

    mx2, my2 = b2_x + bw / 2 - 22, y_top + 90
    f.append(rect(mx2 - 35, my2 - 25, 35, 30, fill="#fdecea", stroke=POS, sw=1.5, rx=0))
    f.append(rect(mx2, my2 - 25, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=0))
    f.append(text(mx2 - 18, my2 - 6, "N", size=13, color=POS, bold=True))
    f.append(text(mx2 + 18, my2 - 6, "S", size=13, color=NEG, bold=True))
    f.append(rect(mx2 - 12, my2 - 50, 24, 25, fill="#e5e7eb", stroke=LINE, sw=1.2))

    cx2, cy2 = b2_x + bw / 2, my2 + 65
    f.append(rect(cx2 - 45, cy2, 90, 20, fill="#334155", stroke=LINE, sw=1.5, rx=2))
    f.append(text(cx2, cy2 + 14, "IC Sensor", size=10, color="#ffffff", bold=True))

    f.append(line(cx2, y_top + 45, cx2, cy2 + 25, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(mx2, y_top + 45, mx2, cy2, color="#d97706", sw=1.2, dash="3 3"))
    f.append(arrow(cx2, y_top + 48, mx2, y_top + 48, color="#d97706", sw=1.5))
    f.append(text((cx2 + mx2) / 2, y_top + 40, "Δr", size=11, color="#d97706", bold=True))

    f.append(textbox(b2_x + bw / 2, y_top + 235,
                     "Незбіг осей обертання\n"
                     "Породжує 1-шу гармоніку:\n"
                     "Δθ₁ = A₁ · sin(θ + φ₁)\n"
                     "Зсув на 0.2 мм → похибка ~1°",
                     size=10.5, pad=6, fill="#fef9ee", stroke="#d97706")[0])

    # Блок 3: Кутовий перекіс (Tilt)
    b3_x = b2_x + bw + gap
    f.append(rect(b3_x, y_top, bw, bh, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=6))
    f.append(text(b3_x + bw / 2, y_top + 24, "3. Кутовий перекіс (Tilt)", size=12.5, color="#2563eb", bold=True))

    mx3, my3 = b3_x + bw / 2, y_top + 90
    tilt_ang = math.radians(15)
    cos_t, sin_t = math.cos(tilt_ang), math.sin(tilt_ang)
    w_m, h_m = 35, 30
    p_n = ("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"
           % (mx3 - w_m * cos_t, my3 - w_m * sin_t - h_m / 2,
              mx3, my3 - h_m / 2,
              mx3, my3 + h_m / 2,
              mx3 - w_m * cos_t, my3 - w_m * sin_t + h_m / 2))
    p_s = ("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"
           % (mx3, my3 - h_m / 2,
              mx3 + w_m * cos_t, my3 + w_m * sin_t - h_m / 2,
              mx3 + w_m * cos_t, my3 + w_m * sin_t + h_m / 2,
              mx3, my3 + h_m / 2))
    f.append('<path d="%s" fill="#fdecea" stroke="%s" stroke-width="1.5"/>' % (p_n, POS))
    f.append('<path d="%s" fill="#eaf0fd" stroke="%s" stroke-width="1.5"/>' % (p_s, NEG))
    f.append(text(mx3 - 18 * cos_t, my3 - 18 * sin_t + 4, "N", size=12, color=POS, bold=True))
    f.append(text(mx3 + 18 * cos_t, my3 + 18 * sin_t + 4, "S", size=12, color=NEG, bold=True))

    cx3, cy3 = mx3, my3 + 65
    f.append(rect(cx3 - 45, cy3, 90, 20, fill="#334155", stroke=LINE, sw=1.5, rx=2))
    f.append(text(cx3, cy3 + 14, "IC Sensor", size=10, color="#ffffff", bold=True))

    f.append(textbox(b3_x + bw / 2, y_top + 235,
                     "Кутовий нахил магніту\n"
                     "Породжує 2-гу гармоніку:\n"
                     "Δθ₂ = A₂ · sin(2θ + φ₂)\n"
                     "Амплітуди Bx ≠ By (еліпс)",
                     size=10.5, pad=6, fill="#eff6ff", stroke="#2563eb")[0])

    render(os.path.join(IMG, "air-gap-and-misalignment.svg"), W, H, *f)


# ── 5. Фазова площина: еліпс → ідеальне коло ────────────────────────────────
def fig_ellipse_to_circle():
    W, H = 760, 420
    f = [text(W / 2, 28, "Лінеаризація траєкторії сигналів: усунення зміщення та еліптичності", size=16, bold=True)]

    # Лівий графік: Реальний зміщений еліпс (Bx_raw, By_raw)
    ox1, oy1 = 180, 220
    R = 85

    f.append(line(ox1 - 120, oy1, ox1 + 120, oy1, color=MUTED, sw=1.2))
    f.append(line(ox1, oy1 - 120, ox1, oy1 + 120, color=MUTED, sw=1.2))
    f.append(text(ox1 + 115, oy1 - 10, "Bx", size=12, color=MUTED, bold=True))
    f.append(text(ox1 + 10, oy1 - 110, "By", size=12, color=MUTED, bold=True))

    ex, ey = ox1 + 25, oy1 - 18
    erx, ery = 95, 68
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#fef2f2" stroke="%s" stroke-width="2.2" stroke-dasharray="4 2"/>'
             % (ex, ey, erx, ery, POS))

    f.append(circle(ex, ey, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(ex + 8, ey - 8, "Зміщення (Ox, Oy)", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(circle(ox1, oy1, 3, fill=LINE, stroke=LINE, sw=1))

    f.append(text(ox1, oy1 + 125, "Сирі сигнали: зміщення + різниця амплітуд", size=11.5, color=POS, bold=True))

    # Стрілка перетворення
    f.append(arrow(ox1 + 135, oy1, ox1 + 215, oy1, color=FIELD, sw=3))
    f.append(textbox(355, oy1 - 35, "1. Зняття зсуву (Offset)\n2. Нормування (Gain)\n3. Ортогоналізація",
                     size=10.5, pad=5, fill="#f0fdf4", stroke=FIELD)[0])

    # Правий графік: Ідеальне відкаліброване коло (Bx_cal, By_cal)
    ox2, oy2 = 540, 220

    f.append(line(ox2 - 120, oy2, ox2 + 120, oy2, color=MUTED, sw=1.2))
    f.append(line(ox2, oy2 - 120, ox2, oy2 + 120, color=MUTED, sw=1.2))
    f.append(text(ox2 + 115, oy2 - 10, "Bx_cal", size=12, color=MUTED, bold=True))
    f.append(text(ox2 + 10, oy2 - 110, "By_cal", size=12, color=MUTED, bold=True))

    f.append(circle(ox2, oy2, R, fill="#eff6ff", stroke="#2563eb", sw=2.2))
    f.append(circle(ox2, oy2, 4, fill="#2563eb", stroke="#2563eb", sw=1))

    ang_rad = math.radians(50)
    vx, vy = ox2 + R * math.cos(ang_rad), oy2 - R * math.sin(ang_rad)
    f.append(arrow(ox2, oy2, vx, vy, color=LINE, sw=2))
    f.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (ox2 + 30, oy2, 30, 30, ox2 + 30 * math.cos(ang_rad), oy2 - 30 * math.sin(ang_rad), FIELD))
    f.append(text(ox2 + 38, oy2 - 12, "θ", size=13, color=FIELD, bold=True))

    f.append(text(ox2, oy2 + 125, "Ідеальне коло: точний кут θ = atan2(By, Bx)", size=11.5, color="#2563eb", bold=True))

    render(os.path.join(IMG, "ellipse-to-circle-linearization.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hall_physics()
    fig_bldc_hall_commutation()
    fig_differential_hall_array()
    fig_air_gap_and_misalignment()
    fig_ellipse_to_circle()
    print("All figures generated successfully in ./img/")
