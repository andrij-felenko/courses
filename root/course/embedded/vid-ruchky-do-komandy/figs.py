# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. stick-pipeline: повний конвеєр перетворення сигналу стіка ───────────
def fig_stick_pipeline():
    W, H = 940, 480
    p = []

    blocks_r1 = [
        ("Давач осі", ["Потенціометр / Холл", "напруга V_in (0..V_cc)"], "#2457d6"),
        ("АЦП мікроконтролера", ["10..12 біт оцифрування", "сирий код 0..4095"], "#2457d6"),
        ("Калібрування", ["Min / Center / Max", "нормалізація [-1.0 .. +1.0]"], "#27ae60"),
        ("Мертва зона центру", ["Center Deadband", "ремасштабування без стрибка"], "#27ae60"),
    ]

    blocks_r2 = [
        ("Вихід уставки", ["Цільова кутова швидкість ω", "уставка для PID (deg/s)"], "#c0392b"),
        ("RC Smoothing", ["Фільтр PT1 / Biquad", "усунення джитера пакетів"], "#c0392b"),
        ("Модель Rates", ["Actual / Betaflight Rates", "максимальна швидкість deg/s"], "#27ae60"),
        ("RC Expo", ["Кубічна експонента", "пом'якшення біля нуля"], "#27ae60"),
    ]

    bw, bh = 200, 75
    y_r1 = 70
    y_r2 = 270

    # Ряд 1
    for i, (title, lines, col) in enumerate(blocks_r1):
        x = 30 + i * (bw + 30)
        p.append(rect(x, y_r1, bw, bh, fill="#ffffff", stroke=col, sw=2, rx=6))
        p.append(rect(x, y_r1, bw, 24, fill=col, stroke="none", rx=6))
        p.append(rect(x, y_r1 + 18, bw, 6, fill=col, stroke="none"))
        p.append(text(x + bw / 2, y_r1 + 16, title, size=11, color="#ffffff", bold=True))
        p.append(text(x + bw / 2, y_r1 + 44, lines[0], size=10, color=INK))
        p.append(text(x + bw / 2, y_r1 + 62, lines[1], size=9, color=MUTED))

        # Стрілка вправо
        if i < 3:
            p.append(arrow(x + bw + 2, y_r1 + bh / 2, x + bw + 28, y_r1 + bh / 2, color=LINE, sw=1.8))

    # Перехід між рядами
    x_turn = 30 + 3 * (bw + 30) + bw / 2
    p.append(arrow(x_turn, y_r1 + bh, x_turn, y_r2 - 8, color=LINE, sw=1.8))
    p.append(text(x_turn + 8, (y_r1 + bh + y_r2) / 2, "нормалізований стік x", size=9, color=MUTED, anchor="start"))

    # Ряд 2 (зворотний потік: 3 -> 2 -> 1 -> 0)
    for i, (title, lines, col) in enumerate(blocks_r2):
        x = 30 + i * (bw + 30)
        p.append(rect(x, y_r2, bw, bh, fill="#ffffff", stroke=col, sw=2, rx=6))
        p.append(rect(x, y_r2, bw, 24, fill=col, stroke="none", rx=6))
        p.append(rect(x, y_r2 + 18, bw, 6, fill=col, stroke="none"))
        p.append(text(x + bw / 2, y_r2 + 16, title, size=11, color="#ffffff", bold=True))
        p.append(text(x + bw / 2, y_r2 + 44, lines[0], size=10, color=INK))
        p.append(text(x + bw / 2, y_r2 + 62, lines[1], size=9, color=MUTED))

        if i < 3:
            p.append(arrow(x + bw + 28, y_r2 + bh / 2, x + bw + 2, y_r2 + bh / 2, color=LINE, sw=1.8))

    p.append(rect(30, 390, 880, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(50, 415, "1. Апаратний шар: оцифрування напруги з датчика та усунення шумів контакту/наведень", size=10, color=INK, anchor="start"))
    p.append(text(50, 432, "2. Геометрія входу: калібрування діапазону, відсікання дрейфу центру й експоненційний вигин", size=10, color=INK, anchor="start"))
    p.append(text(50, 449, "3. Динамічний шар: переведення в фізичну швидкість кута (deg/s) та згладжування сходинок пакетів", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "stick-pipeline.svg"), W, H, *p, title="Конвеєр обробки сигналу стіка керування")


# ── 2. deadband-curves: порівняння мертвої зони ────────────────────────────
def fig_deadband_curves():
    W, H = 840, 420
    p = []

    # Графік 1: Наївне
    ox1, oy1 = 200, 240
    w_axis = 140
    h_axis = 140

    p.append(text(ox1, 55, "Наївне відсікання (зі стрибком)", size=12, color=POS, bold=True))
    p.append(text(ox1, 72, "if (|x| &lt; db) y = 0; else y = x;", size=10, color=MUTED))

    p.append(arrow(ox1 - w_axis, oy1, ox1 + w_axis, oy1, color=LINE, sw=1.2))
    p.append(arrow(ox1, oy1 + h_axis, ox1, oy1 - h_axis, color=LINE, sw=1.2))
    p.append(text(ox1 + w_axis + 8, oy1 + 4, "Вхід x", size=10, color=MUTED, anchor="start"))
    p.append(text(ox1, oy1 - h_axis - 10, "Вихід y", size=10, color=MUTED))

    db_px = 35
    p.append(rect(ox1 - db_px, oy1 - h_axis + 20, 2 * db_px, 2 * h_axis - 40, fill="#fee2e2", stroke="none"))
    p.append(line(ox1 - db_px, oy1 - 6, ox1 - db_px, oy1 + 6, color=POS, sw=1.5))
    p.append(line(ox1 + db_px, oy1 - 6, ox1 + db_px, oy1 + 6, color=POS, sw=1.5))
    p.append(text(ox1 - db_px, oy1 + 18, "-db", size=9, color=POS))
    p.append(text(ox1 + db_px, oy1 + 18, "+db", size=9, color=POS))

    p.append(line(ox1 - w_axis + 15, oy1 + w_axis - 15, ox1 - db_px, oy1 + db_px, color=POS, sw=2.5))
    p.append(line(ox1 - db_px, oy1, ox1 + db_px, oy1, color=POS, sw=2.5))
    p.append(line(ox1 + db_px, oy1 - db_px, ox1 + w_axis - 15, oy1 - w_axis + 15, color=POS, sw=2.5))

    p.append(line(ox1 + db_px, oy1, ox1 + db_px, oy1 - db_px, color=POS, sw=1.2, dash="3 3"))
    p.append(line(ox1 - db_px, oy1, ox1 - db_px, oy1 + db_px, color=POS, sw=1.2, dash="3 3"))
    p.append(circle(ox1 + db_px, oy1, 3.5, fill="#ffffff", stroke=POS, sw=1.5))
    p.append(circle(ox1 + db_px, oy1 - db_px, 3.5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(ox1 + db_px + 10, oy1 - db_px / 2, "Стрибок!", size=10, color=POS, bold=True, anchor="start"))

    # Графік 2: Плавне
    ox2, oy2 = 620, 240
    p.append(text(ox2, 55, "Плавне масштабування (C⁰ неперервне)", size=12, color=FIELD, bold=True))
    p.append(text(ox2, 72, "y = sgn(x) · (|x| - db) / (1 - db)", size=10, color=MUTED))

    p.append(arrow(ox2 - w_axis, oy2, ox2 + w_axis, oy2, color=LINE, sw=1.2))
    p.append(arrow(ox2, oy2 + h_axis, ox2, oy2 - h_axis, color=LINE, sw=1.2))
    p.append(text(ox2 + w_axis + 8, oy2 + 4, "Вхід x", size=10, color=MUTED, anchor="start"))
    p.append(text(ox2, oy2 - h_axis - 10, "Вихід y", size=10, color=MUTED))

    p.append(rect(ox2 - db_px, oy2 - h_axis + 20, 2 * db_px, 2 * h_axis - 40, fill="#dcfce7", stroke="none"))
    p.append(line(ox2 - db_px, oy2 - 6, ox2 - db_px, oy2 + 6, color=FIELD, sw=1.5))
    p.append(line(ox2 + db_px, oy2 - 6, ox2 + db_px, oy2 + 6, color=FIELD, sw=1.5))
    p.append(text(ox2 - db_px, oy2 + 18, "-db", size=9, color=FIELD))
    p.append(text(ox2 + db_px, oy2 + 18, "+db", size=9, color=FIELD))

    p.append(line(ox2 - w_axis + 15, oy2 + w_axis - 15, ox2 - db_px, oy2, color=FIELD, sw=2.5))
    p.append(line(ox2 - db_px, oy2, ox2 + db_px, oy2, color=FIELD, sw=2.5))
    p.append(line(ox2 + db_px, oy2, ox2 + w_axis - 15, oy2 - w_axis + 15, color=FIELD, sw=2.5))

    p.append(circle(ox2 + db_px, oy2, 3.5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(circle(ox2 - db_px, oy2, 3.5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(text(ox2 + db_px + 8, oy2 - 14, "Плавний нуль", size=10, color=FIELD, bold=True, anchor="start"))

    p.append(rect(80, 375, 680, 32, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(420, 395, "Плавне масштабування виключає ривок моторів у момент виходу стіка з мертвої зони", size=10, color=INK))

    render(os.path.join(OUT, "deadband-curves.svg"), W, H, *p, title="Мертва зона: розрив першого роду проти плавного ремасштабування")


# ── 3. expo-curvature: експоненційні криві ────────────────────────────────
def fig_expo_curvature():
    W, H = 840, 440
    p = []

    ox, oy = 100, 360
    gw, gh = 640, 280

    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e2e8f0", sw=1))
    for v in [0.25, 0.5, 0.75, 1.0]:
        xx = ox + v * gw
        yy = oy - v * gh
        p.append(line(xx, oy, xx, oy - gh, color="#e5e7eb", sw=1))
        p.append(line(ox, yy, ox + gw, yy, color="#e5e7eb", sw=1))
        p.append(text(xx, oy + 16, "%.2f" % v, size=9, color=MUTED))
        p.append(text(ox - 10, yy + 4, "%.2f" % v, size=9, color=MUTED, anchor="end"))

    p.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    p.append(text(ox + gw + 10, oy + 24, "Відхилення стіка x →", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - gh - 8, "Вихідний коефіцієнт y", size=10, color=MUTED, anchor="end"))

    expos = [
        (0.0, "Expo = 0.0 (чисто лінійно)", "#6b7280", 1.8, "none"),
        (0.3, "Expo = 0.3 (легке пом'якшення)", "#2457d6", 2.2, "none"),
        (0.6, "Expo = 0.6 (класичний фрістайл)", "#27ae60", 2.6, "none"),
        (0.85, "Expo = 0.85 (глибокий мікроконтроль)", "#c0392b", 2.6, "none"),
    ]

    steps = 100
    for expo, label, col, sw, dash in expos:
        pts = []
        for s in range(steps + 1):
            x = s / float(steps)
            y = x * (1.0 - expo) + (x ** 3) * expo
            px = ox + x * gw
            py = oy - y * gh
            pts.append("%.1f,%.1f" % (px, py))
        dash_attr = (' stroke-dasharray="%s"' % dash) if dash != "none" else ""
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (" ".join(pts), col, sw, dash_attr))

    lx, ly = ox + 30, oy - gh + 30
    p.append(rect(lx, ly, 300, 110, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    for i, (expo, label, col, sw, dash) in enumerate(expos):
        yy = ly + 20 + i * 22
        p.append(line(lx + 15, yy, lx + 45, yy, color=col, sw=sw))
        p.append(circle(lx + 30, yy, 3, fill=col, stroke="none"))
        p.append(text(lx + 55, yy + 4, label, size=10, color=INK, anchor="start"))

    p.append(text(ox + 0.18 * gw, oy - 0.04 * gh - 18, "Мала крутизна біля нуля", size=10, color="#c0392b", bold=True, anchor="start"))
    p.append(text(ox + 0.18 * gw, oy - 0.04 * gh - 4, "dy/dx = 1 - expo = 0.15", size=9, color=MUTED, anchor="start"))

    p.append(text(ox + 0.82 * gw, oy - 0.72 * gh, "Крутий відгук на краю", size=10, color="#c0392b", bold=True, anchor="end"))
    p.append(text(ox + 0.82 * gw, oy - 0.72 * gh + 14, "dy/dx = 1 + 2·expo = 2.70", size=9, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "expo-curvature.svg"), W, H, *p, title="Кубічна експонента: баланс мікроприцілювання та різкого маневру")


# ── 4. rate-models-comparison: порівняння моделей швидкості ───────────────
def fig_rate_models():
    W, H = 860, 460
    p = []

    ox, oy = 100, 370
    gw, gh = 660, 290

    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e2e8f0", sw=1))
    max_rate = 1000.0

    for r_val in [200, 400, 600, 800, 1000]:
        yy = oy - (r_val / max_rate) * gh
        p.append(line(ox, yy, ox + gw, yy, color="#e5e7eb", sw=1))
        p.append(text(ox - 10, yy + 4, "%d °/с" % r_val, size=9, color=MUTED, anchor="end"))

    for x_val in [0.25, 0.5, 0.75, 1.0]:
        xx = ox + x_val * gw
        p.append(line(xx, oy, xx, oy - gh, color="#e5e7eb", sw=1))
        p.append(text(xx, oy + 16, "%.2f" % x_val, size=9, color=MUTED))

    p.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    p.append(text(ox + gw + 10, oy + 24, "Відхилення стіка x →", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - gh - 8, "Кутова швидкість ω (deg/s)", size=10, color=MUTED, anchor="end"))

    steps = 100
    pts_lin = []
    for s in range(steps + 1):
        x = s / float(steps)
        rate = 600.0 * x
        pts_lin.append("%.1f,%.1f" % (ox + x * gw, oy - (rate / max_rate) * gh))
    p.append('<polyline points="%s" fill="none" stroke="#9ca3af" stroke-width="1.8" stroke-dasharray="4 4"/>' % " ".join(pts_lin))

    pts_bf = []
    for s in range(steps + 1):
        x = s / float(steps)
        x_exp = x * (1.0 - 0.2) + (x ** 3) * 0.2
        denom = 1.0 - x * 0.70
        if denom < 0.01: denom = 0.01
        rate = (200.0 * 1.2 * x_exp) / denom
        if rate > max_rate: rate = max_rate
        pts_bf.append("%.1f,%.1f" % (ox + x * gw, oy - (rate / max_rate) * gh))
    p.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.6"/>' % " ".join(pts_bf))

    pts_actual = []
    for s in range(steps + 1):
        x = s / float(steps)
        center = 200.0
        max_r = 850.0
        expo = 0.55
        x_curve = x * (1.0 - expo) + (x ** 5) * expo
        rate = x * center + (max_r - center) * x_curve
        pts_actual.append("%.1f,%.1f" % (ox + x * gw, oy - (rate / max_rate) * gh))
    p.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="2.6"/>' % " ".join(pts_actual))

    lx, ly = ox + 30, oy - gh + 25
    p.append(rect(lx, ly, 360, 110, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))

    legend_items = [
        ("Лінійна уставка (Rate = 600 · x)", "#9ca3af", 1.8, "4 4"),
        ("Betaflight SuperRate (RC=1.2, Super=0.70, Expo=0.2)", "#2457d6", 2.6, "none"),
        ("Actual Rates (Center=200, Max=850, Expo=0.55)", "#27ae60", 2.6, "none"),
    ]
    for i, (label, col, sw, dash) in enumerate(legend_items):
        yy = ly + 20 + i * 26
        dash_attr = (' stroke-dasharray="%s"' % dash) if dash != "none" else ""
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s/>' % (lx + 15, yy, lx + 45, yy, col, sw, dash_attr))
        p.append(circle(lx + 30, yy, 3, fill=col, stroke="none"))
        p.append(text(lx + 55, yy + 4, label, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "rate-models-comparison.svg"), W, H, *p, title="Порівняння моделей розрахунку кутової швидкості (Rate Models)")


if __name__ == "__main__":
    fig_stick_pipeline()
    fig_deadband_curves()
    fig_expo_curvature()
    fig_rate_models()
    print("All figures generated successfully.")
