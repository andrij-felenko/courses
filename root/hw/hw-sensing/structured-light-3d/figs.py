# -*- coding: utf-8 -*-
"""Фігури до статті «Структуроване світло: глибина з кадру» (structured-light-3d-d.md).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

П'ять фігур статті:
  1) triangulation-geometry.svg    — тріангуляція проектор-камера, база B, глибина Z = B·f/d;
  2) pattern-types.svg            — три патерни: спекл PrimeSense, смуги Грея, синусоїдальні смуги;
  3) phase-shifting-steps.svg     — 4-кроковий фазовий зсув, ортогональні компоненти та загорнута фаза;
  4) temporal-phase-unwrapping.svg — двочастотне часове розгортання фази (груба фаза + точна зсунута);
  5) shadows-and-calibration.svg   — оклюзії/тіні через базу B та калібрування стереопари (епіполярні лінії).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD  = "#d48806"
CYAN  = "#08979c"
PURP  = "#531dab"


def polyline(pts, color=INK, sw=2.0, dash=None):
    """Сирий <polyline>."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    """Сирий <polygon>."""
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (s, fill, stroke, sw))


# ── 1. Геометрія тріангуляції проектор–камера ──────────────────────────────
def fig_triangulation_geometry():
    W, H = 940, 520
    f = [
        text(W / 2, 28, "Оптична тріангуляція активної стереопари проектор–камера", size=18, bold=True),
        text(W / 2, 50, "зсув проектованого променя на матриці камери (паралакс d) визначає абсолютну глибину Z",
             size=11, color=MUTED, italic=True)
    ]

    # Центри камер і проектора
    xc_proj = 280
    xc_cam  = 660
    y_opt   = 430
    f_len   = 70

    # Оптична база B
    f.append(line(xc_proj, y_opt, xc_cam, y_opt, color=LINE, sw=1.5, dash="4 4"))
    f.append(arrow(xc_proj + 30, y_opt + 36, xc_proj, y_opt + 36, color=INK, sw=1.8))
    f.append(arrow(xc_cam - 30, y_opt + 36, xc_cam, y_opt + 36, color=INK, sw=1.8))
    f.append(line(xc_proj, y_opt + 20, xc_proj, y_opt + 50, color=MUTED, sw=1.2))
    f.append(line(xc_cam, y_opt + 20, xc_cam, y_opt + 50, color=MUTED, sw=1.2))
    f.append(text((xc_proj + xc_cam) / 2, y_opt + 40, "Оптична база B", size=13, bold=True))

    # Корпус проектора
    f.append(rect(xc_proj - 60, y_opt - 10, 120, 50, fill="#fff7e6", stroke=GOLD, sw=2, rx=6))
    f.append(text(xc_proj, y_opt + 18, "ІЧ-проектор", size=13, bold=True, color=GOLD))
    f.append(circle(xc_proj, y_opt, 5, fill=GOLD, stroke=LINE, sw=1.5))
    f.append(text(xc_proj, y_opt - 16, "Op (центр проектора)", size=10, bold=True, color=INK))

    # Корпус камери
    f.append(rect(xc_cam - 60, y_opt - 10, 120, 50, fill="#e6f7ff", stroke=NEG, sw=2, rx=6))
    f.append(text(xc_cam, y_opt + 18, "ІЧ-камера", size=13, bold=True, color=NEG))
    f.append(circle(xc_cam, y_opt, 5, fill=NEG, stroke=LINE, sw=1.5))
    f.append(text(xc_cam, y_opt - 16, "Oc (центр камери)", size=10, bold=True, color=INK))

    # Сенсор камери
    y_sensor = y_opt + f_len
    f.append(line(xc_cam - 55, y_sensor, xc_cam + 55, y_sensor, color=NEG, sw=3))
    f.append(text(xc_cam + 75, y_sensor + 4, "сенсор", size=10, color=NEG, anchor="start"))
    f.append(line(xc_cam - 80, y_opt, xc_cam - 80, y_sensor, color=MUTED, sw=1.2))
    f.append(text(xc_cam - 90, y_opt + f_len / 2 + 4, "f", size=12, bold=True, anchor="end"))

    # Поверхня об'єкта (близька) та опорна площина (далека)
    y_obj = 150
    y_ref = 90
    f.append(line(80, y_ref, 860, y_ref, color=MUTED, sw=1.8, dash="6 4"))
    f.append(text(90, y_ref - 10, "Опорна площина Z0", size=11, bold=True, color=MUTED, anchor="start"))

    # Об'єкт рельєфу
    pts_obj = [(180, 190), (320, 150), (450, 130), (550, 160), (760, 200)]
    f.append(polyline(pts_obj, color=FIELD, sw=3))
    f.append(circle(450, 130, 6, fill=FIELD, stroke=LINE, sw=2))
    f.append(text(450, 114, "Точка об'єкта P(X, Y, Z)", size=12, bold=True, color=FIELD))

    # Точка на опорній площині вздовж того самого променя
    x_pref = 280 + 1.1333 * (450 - 280)
    f.append(circle(x_pref, y_ref, 5, fill=MUTED, stroke=LINE, sw=1.5))
    f.append(text(x_pref + 8, y_ref - 10, "Pref (на Z0)", size=10, color=MUTED, anchor="start"))

    # Промінь проектора
    f.append(line(xc_proj, y_opt, x_pref, y_ref, color=GOLD, sw=2.5))
    f.append(text(330, 290, "проектований промінь", size=10, bold=True, color=GOLD, anchor="end"))

    # Відбиті промені в камеру:
    f.append(line(450, 130, xc_cam, y_opt, color=POS, sw=2.2))
    x_pix_p = xc_cam + f_len * (xc_cam - 450) / (y_opt - 130)
    f.append(line(xc_cam, y_opt, x_pix_p, y_sensor, color=POS, sw=2.2, dash="3 3"))
    f.append(circle(x_pix_p, y_sensor, 4, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(x_pix_p + 6, y_sensor + 18, "u(Z)", size=11, bold=True, color=POS, anchor="start"))

    f.append(line(x_pref, y_ref, xc_cam, y_opt, color=MUTED, sw=1.5, dash="4 3"))
    x_pix_ref = xc_cam + f_len * (xc_cam - x_pref) / (y_opt - y_ref)
    f.append(line(xc_cam, y_opt, x_pix_ref, y_sensor, color=MUTED, sw=1.5, dash="3 3"))
    f.append(circle(x_pix_ref, y_sensor, 4, fill=MUTED, stroke=LINE, sw=1.5))
    f.append(text(x_pix_ref - 6, y_sensor + 18, "u0 (Z0)", size=11, bold=True, color=MUTED, anchor="end"))

    # Зсув на сенсорі (паралакс / диспаратність d)
    f.append(line(x_pix_ref, y_sensor + 32, x_pix_p, y_sensor + 32, color=POS, sw=2))
    f.append(arrow(x_pix_ref + 10, y_sensor + 32, x_pix_ref, y_sensor + 32, color=POS, sw=1.5))
    f.append(arrow(x_pix_p - 10, y_sensor + 32, x_pix_p, y_sensor + 32, color=POS, sw=1.5))
    f.append(text((x_pix_ref + x_pix_p) / 2, y_sensor + 46, "паралакс d", size=11, bold=True, color=POS))

    # Вісь глибини Z
    f.append(arrow(890, y_opt, 890, 70, color=INK, sw=2))
    f.append(text(905, 80, "Z (глибина)", size=11, bold=True, anchor="start"))
    f.append(line(880, y_obj - 20, 900, y_obj - 20, color=MUTED, sw=1.2))
    f.append(line(880, y_ref, 900, y_ref, color=MUTED, sw=1.2))

    # Рамка формули
    f.append(fitbox(50, 440, 180, 56,
                    "Z = (B · f) / d\nΔZ ≈ (Z² / B·f) · Δd",
                    size=12, bold=True, fill="#f6ffed", stroke=FIELD, sw=1.5))

    return render(os.path.join(IMG, "triangulation-geometry.svg"), W, H, *f)


# ── 2. Три типи патернів структурованого світла ─────────────────────────────
def fig_pattern_types():
    W, H = 940, 400
    f = [
        text(W / 2, 28, "Порівняння трьох головних патернів підсвічування", size=18, bold=True),
        text(W / 2, 50, "компроміс між швидкістю зйомки (один кадр чи серія) та просторовою роздільністю карти глибини",
             size=11, color=MUTED, italic=True)
    ]

    w_p = 270
    h_p = 310
    y_p = 70

    # Панель 1: Спекл (PrimeSense / Kinect v1)
    x1 = 35
    f.append(rect(x1, y_p, w_p, h_p, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(textbox(x1 + w_p / 2, y_p + 24, "1. Псевдовипадковий спекл", size=13, bold=True, fill="#fff7e6", stroke=GOLD)[0])

    f.append(rect(x1 + 15, y_p + 50, w_p - 30, 110, fill="#141414", stroke=LINE, sw=1.2, rx=4))
    import random
    rng = random.Random(42)
    for _ in range(85):
        rx_pt = x1 + 25 + rng.random() * (w_p - 50)
        ry_pt = y_p + 60 + rng.random() * 90
        rad = 1.5 + rng.random() * 2.0
        f.append(circle(rx_pt, ry_pt, rad, fill="#52c41a", stroke="#52c41a", sw=0))

    f.append(fitbox(x1 + 15, y_p + 170, w_p - 30, 120,
                    "• Один кадр (Single-shot)\n"
                    "• 30–60 fps, рухомі сцени\n"
                    "• Кореляція вікна 9×9 пікселів\n"
                    "• Роздільність обмежена вікном\n"
                    "• Приклад: Kinect v1, FaceID",
                    size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Панель 2: Смуги коду Грея
    x2 = 335
    f.append(rect(x2, y_p, w_p, h_p, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(textbox(x2 + w_p / 2, y_p + 24, "2. Смуги коду Грея", size=13, bold=True, fill="#e6f7ff", stroke=NEG)[0])

    f.append(rect(x2 + 15, y_p + 50, w_p - 30, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    stripe_w = (w_p - 30) / 8
    for i in range(8):
        if i in (1, 2, 5, 6):
            f.append(rect(x2 + 15 + i * stripe_w, y_p + 50, stripe_w, 110, fill="#262626", stroke=LINE, sw=0.5, rx=0))

    f.append(fitbox(x2 + 15, y_p + 170, w_p - 30, 120,
                    "• Послідовність із N бінарних кадрів\n"
                    "• Відстань Геммінга = 1 на стиках\n"
                    "• Стійкий до перепадів яскравості\n"
                    "• Роздільність = ширині смуги\n"
                    "• Потребує нерухомої сцени",
                    size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Панель 3: Синусоїдальні смуги (FPP)
    x3 = 635
    f.append(rect(x3, y_p, w_p, h_p, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(textbox(x3 + w_p / 2, y_p + 24, "3. Синусоїдальний зсув фази", size=13, bold=True, fill="#f6ffed", stroke=FIELD)[0])

    f.append(rect(x3 + 15, y_p + 50, w_p - 30, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    n_strips = 40
    sw_strip = (w_p - 30) / n_strips
    for i in range(n_strips):
        val = int(128 + 120 * math.sin(2 * math.pi * i / 10))
        hex_c = "#%02x%02x%02x" % (val, val, val)
        f.append(rect(x3 + 15 + i * sw_strip, y_p + 50, sw_strip + 0.5, 110, fill=hex_c, stroke=hex_c, sw=0, rx=0))

    f.append(fitbox(x3 + 15, y_p + 170, w_p - 30, 120,
                    "• 3–4 синусоїдальні кадри зі зсувом\n"
                    "• Неперервна фаза φ(x,y)\n"
                    "• Субпіксельна точність (1/50 px)\n"
                    "• Промисловий метрологічний 3D\n"
                    "• Чутливий до гами проектора",
                    size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    return render(os.path.join(IMG, "pattern-types.svg"), W, H, *f)


# ── 3. Чотирикроковий фазовий зсув і загорнута фаза ─────────────────────────
def fig_phase_shifting_steps():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "4-кроковий алгоритм фазового зсуву та вилучення фази", size=18, bold=True),
        text(W / 2, 50, "чотири кадри зі зсувом фази на π/2 усувають фонову засвітку та дають точну загорнуту фазу φ",
             size=11, color=MUTED, italic=True)
    ]

    ox1, oy1 = 70, 220
    w_g, h_g = 400, 140

    f.append(textbox(ox1 + w_g / 2, 85, "Чотири кадри підсвічування: Ik = A + B·cos(φ + k·π/2)",
                     size=12, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    f.append(arrow(ox1, oy1, ox1 + w_g + 20, oy1, color=INK, sw=1.5))
    f.append(arrow(ox1, oy1 + h_g / 2 + 10, ox1, oy1 - h_g / 2 - 20, color=INK, sw=1.5))
    f.append(text(ox1 + w_g + 25, oy1 + 4, "x", size=12, bold=True, anchor="start"))
    f.append(text(ox1 - 10, oy1 - h_g / 2 - 15, "I(x)", size=12, bold=True, anchor="end"))

    f.append(line(ox1, oy1, ox1 + w_g, oy1, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ox1 - 8, oy1 + 4, "A (фон)", size=10, color=MUTED, anchor="end"))

    colors = [POS, GOLD, FIELD, NEG]
    labels = ["I0 (δ=0)", "I1 (δ=π/2)", "I2 (δ=π)", "I3 (δ=3π/2)"]
    for k in range(4):
        pts = []
        phase_shift = k * math.pi / 2
        for step in range(101):
            t = step / 100.0
            x = ox1 + t * w_g
            y = oy1 - 50 * math.cos(2 * math.pi * t * 2 + phase_shift)
            pts.append((x, y))
        f.append(polyline(pts, color=colors[k], sw=2.0))
        f.append(line(ox1 + 10 + k * 95, oy1 + 95, ox1 + 30 + k * 95, oy1 + 95, color=colors[k], sw=2.5))
        f.append(text(ox1 + 35 + k * 95, oy1 + 99, labels[k], size=10, bold=True, color=colors[k], anchor="start"))

    cx_v, cy_v = 700, 160
    r_v = 70
    f.append(textbox(cx_v, 85, "Ортогональні квадратури", size=12, bold=True, fill="#f4f6f8", stroke=LINE)[0])

    f.append(circle(cx_v, cy_v, r_v, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(line(cx_v - r_v - 15, cy_v, cx_v + r_v + 15, cy_v, color=LINE, sw=1.2))
    f.append(line(cx_v, cy_v + r_v + 15, cx_v, cy_v - r_v - 15, color=LINE, sw=1.2))
    f.append(text(cx_v + r_v + 20, cy_v + 4, "I0 − I2", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(cx_v, cy_v - r_v - 8, "I3 − I1", size=11, bold=True, color=NEG))

    ang = math.radians(50)
    vx = cx_v + r_v * math.cos(ang)
    vy = cy_v - r_v * math.sin(ang)
    f.append(arrow(cx_v, cy_v, vx, vy, color=PURP, sw=2.5))
    f.append(circle(vx, vy, 4, fill=PURP, stroke=LINE, sw=1.2))
    f.append(text(cx_v + 35, cy_v - 18, "φ", size=13, bold=True, color=PURP))

    ox2, oy2 = 140, 400
    w_p2 = 660
    h_p2 = 90
    f.append(arrow(ox2, oy2, ox2 + w_p2 + 20, oy2, color=INK, sw=1.5))
    f.append(arrow(ox2, oy2 + h_p2 / 2 + 10, ox2, oy2 - h_p2 / 2 - 15, color=INK, sw=1.5))
    f.append(text(ox2 + w_p2 + 25, oy2 + 4, "x (координата)", size=11, bold=True, anchor="start"))
    f.append(text(ox2 - 10, oy2 - h_p2 / 2 - 8, "φ(x)", size=11, bold=True, anchor="end"))

    f.append(text(ox2 - 8, oy2 - h_p2 / 2 + 6, "+π", size=10, bold=True, color=MUTED, anchor="end"))
    f.append(text(ox2 - 8, oy2 + h_p2 / 2 - 4, "−π", size=10, bold=True, color=MUTED, anchor="end"))
    f.append(line(ox2, oy2 - h_p2 / 2 + 6, ox2 + w_p2, oy2 - h_p2 / 2 + 6, color=MUTED, sw=1, dash="2 3"))
    f.append(line(ox2, oy2 + h_p2 / 2 - 4, ox2 + w_p2, oy2 + h_p2 / 2 - 4, color=MUTED, sw=1, dash="2 3"))

    n_periods = 4
    w_per = w_p2 / n_periods
    for p in range(n_periods):
        px0 = ox2 + p * w_per
        px1 = px0 + w_per
        f.append(line(px0, oy2 + h_p2 / 2 - 6, px1, oy2 - h_p2 / 2 + 8, color=PURP, sw=2.5))
        if p > 0:
            f.append(line(px0, oy2 - h_p2 / 2 + 8, px0, oy2 + h_p2 / 2 - 6, color=POS, sw=1.2, dash="3 2"))
            f.append(text(px0, oy2 + h_p2 / 2 + 16, "розрив 2π", size=9, color=POS, bold=True))

    f.append(fitbox(580, 240, 310, 64,
                    "φ(x,y) = atan2( I3 − I1, I0 − I2 )\n"
                    "B(x,y) = ½ √[ (I0−I2)² + (I3−I1)² ]",
                    size=12, bold=True, fill="#fff6e0", stroke=GOLD, sw=1.5))

    return render(os.path.join(IMG, "phase-shifting-steps.svg"), W, H, *f)


# ── 4. Багаточастотне часове розгортання фази ──────────────────────────────
def fig_temporal_phase_unwrapping():
    W, H = 940, 500
    f = [
        text(W / 2, 28, "Двочастотне часове розгортання фази (Temporal Phase Unwrapping)", size=18, bold=True),
        text(W / 2, 50, "груба одноперіодна фаза визначає цілий номер смуги k(x), а високочастотна — дає субпіксельну точність",
             size=11, color=MUTED, italic=True)
    ]

    ox, w_line = 160, 680

    # 1. Низька частота
    y1 = 110
    f.append(text(ox - 20, y1 + 4, "1. Груба фаза Φ1\n(1 період, без розривів)", size=11, bold=True, anchor="end"))
    f.append(arrow(ox, y1 + 25, ox + w_line + 20, y1 + 25, color=INK, sw=1.5))
    f.append(arrow(ox, y1 + 25, ox, y1 - 35, color=INK, sw=1.5))
    f.append(line(ox, y1 + 20, ox + w_line, y1 - 25, color=NEG, sw=2.5))
    f.append(text(ox + w_line / 2, y1 - 10, "Неперервна фаза Φ1 ∈ [−π, +π)", size=11, bold=True, color=NEG))

    # 2. Висока частота
    y2 = 220
    f.append(text(ox - 20, y2 + 4, "2. Точна фаза φ2\n(N=8 періодів, загорнута)", size=11, bold=True, anchor="end"))
    f.append(arrow(ox, y2 + 25, ox + w_line + 20, y2 + 25, color=INK, sw=1.5))
    f.append(arrow(ox, y2 + 25, ox, y2 - 35, color=INK, sw=1.5))
    n_per = 8
    wp = w_line / n_per
    for i in range(n_per):
        f.append(line(ox + i * wp, y2 + 20, ox + (i + 1) * wp, y2 - 25, color=PURP, sw=2.2))
        if i > 0:
            f.append(line(ox + i * wp, y2 - 25, ox + i * wp, y2 + 20, color=MUTED, sw=1, dash="2 2"))

    # 3. Сходинки порядку смуги k(x)
    y3 = 330
    f.append(text(ox - 20, y3 + 4, "3. Порядок смуги k(x)\nk = round( (8·Φ1 − φ2) / 2π )", size=11, bold=True, anchor="end"))
    f.append(arrow(ox, y3 + 25, ox + w_line + 20, y3 + 25, color=INK, sw=1.5))
    f.append(arrow(ox, y3 + 25, ox, y3 - 40, color=INK, sw=1.5))
    for i in range(n_per):
        yk = y3 + 18 - i * 6.5
        f.append(line(ox + i * wp, yk, ox + (i + 1) * wp, yk, color=GOLD, sw=3))
        if i > 0:
            f.append(line(ox + i * wp, yk + 6.5, ox + i * wp, yk, color=GOLD, sw=1.5, dash="2 2"))
        f.append(text(ox + (i + 0.5) * wp, yk - 5, "k=%d" % i, size=9, bold=True, color=GOLD))

    # 4. Розгорнута абсолютна фаза Φ(x)
    y4 = 440
    f.append(text(ox - 20, y4 + 4, "4. Абсолютна фаза Φ\nΦ(x) = φ2(x) + 2π·k(x)", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(arrow(ox, y4 + 25, ox + w_line + 20, y4 + 25, color=INK, sw=1.5))
    f.append(arrow(ox, y4 + 25, ox, y4 - 35, color=INK, sw=1.5))
    f.append(line(ox, y4 + 20, ox + w_line, y4 - 30, color=FIELD, sw=3.2))
    f.append(text(ox + w_line / 2, y4 - 15, "Неперервна абсолютна фаза Φ ∈ [0, 16π) → точна глибина Z",
                  size=12, bold=True, color=FIELD))

    return render(os.path.join(IMG, "temporal-phase-unwrapping.svg"), W, H, *f)


# ── 5. Оклюзії/тіні та калібрування стереопари ──────────────────────────────
def fig_shadows_and_calibration():
    W, H = 940, 440
    f = [
        text(W / 2, 28, "Оптичні оклюзії та епіполярна геометрія проектор–камера", size=18, bold=True),
        text(W / 2, 50, "база B неминуче створює зони тіні; калібрування вирівнює епіполярні лінії для 1D-пошуку зсуву",
             size=11, color=MUTED, italic=True)
    ]

    # Панель A: Тіні та оклюзії
    w_p, h_p = 410, 330
    f.append(rect(40, 75, w_p, h_p, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(textbox(40 + w_p / 2, 100, "А. Зони тіні та сліпі кути", size=13, bold=True, fill="#fff1f0", stroke=POS)[0])

    xp_a, xc_a, y_top = 100, 380, 150
    f.append(circle(xp_a, y_top, 7, fill=GOLD, stroke=LINE, sw=1.5))
    f.append(text(xp_a, y_top - 14, "Проектор", size=11, bold=True, color=GOLD))
    f.append(circle(xc_a, y_top, 7, fill=NEG, stroke=LINE, sw=1.5))
    f.append(text(xc_a, y_top - 14, "Камера", size=11, bold=True, color=NEG))
    f.append(line(xp_a, y_top, xc_a, y_top, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text((xp_a + xc_a) / 2, y_top - 8, "База B", size=10, bold=True))

    pts_step = [(80, 360), (220, 360), (220, 260), (290, 260), (290, 360), (410, 360)]
    f.append(polyline(pts_step, color=LINE, sw=2.5))
    f.append(rect(220, 260, 70, 100, fill="#e8e8e8", stroke=LINE, sw=1.5, rx=0))
    f.append(text(255, 310, "Об'єкт", size=11, bold=True))

    f.append(line(xp_a, y_top, 220, 260, color=GOLD, sw=2))
    f.append(line(220, 260, 329, 360, color=GOLD, sw=1.5, dash="3 3"))

    pts_shadow = [(220, 260), (290, 260), (290, 360), (329, 360), (220, 260)]
    f.append(polygon(pts_shadow, fill="#ffeef0", stroke=POS, sw=1.2))
    f.append(text(310, 295, "Тінь проектора", size=10, bold=True, color=POS))
    f.append(text(310, 312, "(камера бачить, нема світла)", size=9, color=POS))

    f.append(line(xc_a, y_top, 220, 260, color=NEG, sw=1.8))
    f.append(line(xc_a, y_top, 290, 260, color=NEG, sw=1.8))

    f.append(fitbox(55, 368, w_p - 30, 26,
                    "Маска модуляції B(x,y) < Bmin відсікає ці зони",
                    size=10, bold=True, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Панель B: Епіполярне вирівнювання
    x_b = 490
    f.append(rect(x_b, 75, w_p, h_p, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(textbox(x_b + w_p / 2, 100, "Б. Епіполярна геометрія та калібрування", size=13, bold=True, fill="#e6f7ff", stroke=NEG)[0])

    f.append(rect(x_b + 30, 140, 140, 110, fill="#ffffff", stroke=GOLD, sw=2, rx=4))
    f.append(text(x_b + 100, 160, "Площина проектора", size=11, bold=True, color=GOLD))
    for row in range(4):
        f.append(line(x_b + 35, 180 + row * 18, x_b + 165, 180 + row * 18, color=GOLD, sw=1.2, dash="3 3"))

    f.append(rect(x_b + 240, 140, 140, 110, fill="#ffffff", stroke=NEG, sw=2, rx=4))
    f.append(text(x_b + 310, 160, "Площина камери", size=11, bold=True, color=NEG))
    for row in range(4):
        f.append(line(x_b + 245, 180 + row * 18, x_b + 375, 180 + row * 18, color=NEG, sw=1.2, dash="3 3"))

    f.append(line(x_b + 165, 198, x_b + 245, 198, color=POS, sw=2.5))
    f.append(arrow(x_b + 200, 198, x_b + 240, 198, color=POS, sw=2.0))
    f.append(circle(x_b + 100, 198, 4, fill=GOLD, stroke=LINE, sw=1.2))
    f.append(circle(x_b + 310, 198, 4, fill=NEG, stroke=LINE, sw=1.2))
    f.append(text(x_b + 205, 185, "епіполярна лінія", size=10, bold=True, color=POS))

    f.append(fitbox(x_b + 15, 270, w_p - 30, 115,
                    "Калібрування шахівницею:\n"
                    "• Внутрішні матриці Kc, Kp (фокус, головна точка)\n"
                    "• Коефіцієнти дисторсії k1, k2, p1, p2\n"
                    "• Взаємне положення: поворот R та зсув T\n"
                    "• Ректифікація: пошук фази стає суто 1D по рядку!",
                    size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    return render(os.path.join(IMG, "shadows-and-calibration.svg"), W, H, *f)


if __name__ == "__main__":
    fig_triangulation_geometry()
    fig_pattern_types()
    fig_phase_shifting_steps()
    fig_temporal_phase_unwrapping()
    fig_shadows_and_calibration()
    print("Всі фігури згенеровано успішно.")
