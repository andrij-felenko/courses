# -*- coding: utf-8 -*-
"""Фігури для теми porih-i-histerezys («Поріг і гістерезис: чому реле клацає щохвилини»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. relay-chattering: аналоговий шум на межі порогу та деренчання ──────────
def fig_relay_chattering():
    W, H = 760, 360
    ox, oy_top = 70, 110
    oy_bot = 270
    aw = 580
    amp = 45
    p = []

    # Вісь часу та напруги для верхнього графіка (сенсор)
    p.append(arrow(ox, oy_top, ox + aw, oy_top, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy_top + amp + 25, ox, oy_top - amp - 25, color=MUTED, sw=1.2))
    p.append(text(ox + aw - 10, oy_top + 18, "t", size=11, color=MUTED, italic=True))
    p.append(text(ox - 15, oy_top - amp - 12, "T, °C", size=11, color=INK, bold=True))

    # Поріг T_set = 25.0 °C
    p.append(line(ox, oy_top, ox + aw - 30, oy_top, color=POS, sw=1.4, dash="5 4"))
    p.append(text(ox + aw - 25, oy_top - 5, "T_set (25.0 °C)", size=10, color=POS, anchor="start", bold=True))

    # Сигнал сенсора з шумом, що повільно перетинає поріг
    pts = []
    noise_vals = [
        0, 3, -4, 2, -5, 4, -2, 6, -3, 5, -6, 2, -4, 5, -3, 4,
        -5, 6, -4, 7, -5, 3, -6, 5, -4, 6, -5, 4, -3, 5, -4, 2,
        -5, 6, -3, 5, -7, 4, -5, 6, -4, 5, -3, 6, -5, 4, -2, 0
    ]
    n_pts = len(noise_vals)
    cross_start_x = None
    cross_end_x = None

    for i, nv in enumerate(noise_vals):
        t_norm = i / float(n_pts - 1)
        trend = (t_norm - 0.5) * 50.0
        val = trend + nv * 1.8
        x_pt = ox + t_norm * (aw - 60)
        y_pt = oy_top - val
        pts.append("%.1f,%.1f" % (x_pt, y_pt))
        if 0.25 <= t_norm <= 0.75:
            if cross_start_x is None:
                cross_start_x = x_pt
            cross_end_x = x_pt

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    if cross_start_x and cross_end_x:
        zw = cross_end_x - cross_start_x
        p.append(rect(cross_start_x, oy_top - 20, zw, 40, fill="#fdecea", stroke="none", rx=0))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), NEG))
        p.append(line(ox, oy_top, ox + aw - 30, oy_top, color=POS, sw=1.4, dash="5 4"))
        p.append(text(cross_start_x + zw/2, oy_top - 28, "шум біля порогу: багаторазовий перетин", size=10, color=POS, bold=True))

    # Нижній графік: вихід на котушку реле (0 або 1)
    p.append(arrow(ox, oy_bot, ox + aw, oy_bot, color=MUTED, sw=1.2))
    p.append(arrow(ox, oy_bot + 15, ox, oy_bot - 45, color=MUTED, sw=1.2))
    p.append(text(ox + aw - 10, oy_bot + 18, "t", size=11, color=MUTED, italic=True))
    p.append(text(ox - 15, oy_bot - 38, "Реле", size=11, color=INK, bold=True))
    p.append(text(ox - 8, oy_bot - 28, "УВІМК", size=9, color=FIELD, anchor="end"))
    p.append(text(ox - 8, oy_bot - 4, "ВИМК", size=9, color=MUTED, anchor="end"))

    relay_pts = []
    relay_pts.append((ox, oy_bot - 30))
    relay_pts.append((cross_start_x, oy_bot - 30))

    chatter_steps = 14
    for k in range(chatter_steps):
        xk = cross_start_x + (k / float(chatter_steps)) * (cross_end_x - cross_start_x)
        yk = (oy_bot - 30) if (k % 2 == 0) else oy_bot
        relay_pts.append((xk, yk))

    relay_pts.append((cross_end_x, oy_bot))
    relay_pts.append((ox + aw - 60, oy_bot))

    relay_poly = []
    for i in range(len(relay_pts) - 1):
        x1, y1 = relay_pts[i]
        x2, y2 = relay_pts[i+1]
        relay_poly.append("%.1f,%.1f %.1f,%.1f" % (x1, y1, x2, y1))
        relay_poly.append("%.1f,%.1f" % (x2, y2))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="miter"/>' % (" ".join(relay_poly), POS))

    b_chatt, bw, bh = textbox(cross_start_x + (cross_end_x - cross_start_x)/2, oy_bot + 45,
                              "Високочастотне деренчання контактів (Chattering)\n"
                              "Дуговий розряд, ерозія сплаву, підгоряння, ЕМ-завади на МК",
                              size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.2, color=POS, bold=True)
    p.append(b_chatt)

    render(os.path.join(OUT, "relay-chattering.svg"), W, H, *p,
           title="Аналоговий шум на одному порозі спричиняє деренчання реле")


# ── 2. schmitt-hysteresis-loop: амплітудна петля гістерезису ──────────────────
def fig_schmitt_hysteresis_loop():
    W, H = 760, 340
    ox, oy = 110, 240
    aw = 540
    ah = 180
    p = []

    p.append(arrow(ox, oy, ox + aw, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy + 20, ox, oy - ah - 20, color=LINE, sw=1.5))
    p.append(text(ox + aw - 10, oy + 22, "Вхідний сигнал x (наприклад, T, °C)", size=11, color=INK, italic=True))
    p.append(text(ox - 15, oy - ah - 10, "Стан u(x)", size=12, color=INK, bold=True))

    y_off = oy
    y_on = oy - ah
    p.append(text(ox - 12, y_off - 4, "0 (ВИМК)", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, y_on + 4, "1 (УВІМК)", size=10, color=FIELD, anchor="end", bold=True))
    p.append(line(ox, y_on, ox + aw - 40, y_on, color=MUTED, sw=1.0, dash="4 4"))

    x_low = ox + 170
    x_high = ox + 360

    p.append(line(x_low, oy + 10, x_low, y_on - 15, color=NEG, sw=1.4, dash="5 4"))
    p.append(line(x_high, oy + 10, x_high, y_on - 15, color=POS, sw=1.4, dash="5 4"))
    p.append(text(x_low, oy + 22, "T_low (нижній поріг)", size=11, color=NEG, bold=True))
    p.append(text(x_high, oy + 22, "T_high (верхній поріг)", size=11, color=POS, bold=True))

    p.append(rect(x_low, y_on, x_high - x_low, ah, fill="#f4f8fb", stroke="none", rx=0))
    p.append(arrow(x_low + 5, oy - ah/2, x_high - 5, oy - ah/2, color=INK, sw=1.4))
    p.append(arrow(x_high - 5, oy - ah/2, x_low + 5, oy - ah/2, color=INK, sw=1.4))
    p.append(mtext((x_low + x_high)/2, oy - ah/2 - 22,
                   ["Зона нечутливості ΔT = T_high − T_low", "(Пам'ять: стан зберігається)"],
                   size=10, color=INK, bold=True))

    p.append(line(ox, y_off, x_high, y_off, color=NEG, sw=2.5))
    p.append(line(x_high, y_off, x_high, y_on, color=POS, sw=2.5))
    p.append(arrow(x_low + 50, y_off - 8, x_low + 90, y_off - 8, color=POS, sw=1.6))
    p.append(text(x_low + 70, y_off - 16, "зростання x →", size=9, color=POS, bold=True))

    p.append(line(x_low, y_on, ox + aw - 50, y_on, color=FIELD, sw=2.5))
    p.append(line(x_low, y_on, x_low, y_off, color=NEG, sw=2.5))
    p.append(arrow(x_high - 50, y_on + 8, x_high - 90, y_on + 8, color=NEG, sw=1.6))
    p.append(text(x_high - 70, y_on + 18, "← спадання x", size=9, color=NEG, bold=True))

    p.append(circle(x_high, y_off, 4, fill=POS, stroke=LINE, sw=1.2))
    p.append(circle(x_high, y_on, 4, fill=POS, stroke=LINE, sw=1.2))
    p.append(circle(x_low, y_on, 4, fill=NEG, stroke=LINE, sw=1.2))
    p.append(circle(x_low, y_off, 4, fill=NEG, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "schmitt-hysteresis-loop.svg"), W, H, *p,
           title="Петля гістерезису: два пороги перемикання та зона пам'яті")


# ── 3. time-hysteresis-holdoff: часовий гістерезис (Hold-off Time) ────────────
def fig_time_hysteresis_holdoff():
    W, H = 760, 360
    ox = 80
    aw = 580
    p = []

    y1, y2, y3 = 80, 190, 290

    # Доріжка 1
    p.append(arrow(ox, y1, ox + aw, y1, color=MUTED, sw=1.2))
    p.append(arrow(ox, y1 + 35, ox, y1 - 35, color=MUTED, sw=1.2))
    p.append(text(ox - 15, y1 - 25, "Температура", size=11, color=INK, bold=True))
    p.append(line(ox, y1 - 18, ox + aw - 30, y1 - 18, color=POS, sw=1.2, dash="4 4"))
    p.append(line(ox, y1 + 18, ox + aw - 30, y1 + 18, color=NEG, sw=1.2, dash="4 4"))
    p.append(text(ox + aw - 25, y1 - 18, "T_high", size=10, color=POS, anchor="start"))
    p.append(text(ox + aw - 25, y1 + 18, "T_low", size=10, color=NEG, anchor="start"))

    temp_pts = [
        (ox, y1 - 10), (ox + 60, y1 + 25), (ox + 100, y1 + 10),
        (ox + 130, y1 + 22), (ox + 200, y1 - 25), (ox + 240, y1 - 10),
        (ox + 280, y1 - 26), (ox + 350, y1 + 26), (ox + 420, y1 - 24),
        (ox + 500, y1 + 5), (ox + aw - 40, y1 - 15)
    ]
    poly_str = " ".join("%.1f,%.1f" % pt for pt in temp_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (poly_str, INK))

    # Доріжка 2
    p.append(arrow(ox, y2, ox + aw, y2, color=MUTED, sw=1.2))
    p.append(text(ox - 15, y2 - 20, "Лише амплітудний\nгістерезис", size=10, color=MUTED, bold=True))
    raw_on = [(ox, y2), (ox + 60, y2), (ox + 60, y2 - 25), (ox + 200, y2 - 25),
              (ox + 200, y2), (ox + 350, y2), (ox + 350, y2 - 25), (ox + 420, y2 - 25),
              (ox + 420, y2), (ox + aw - 40, y2)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-linejoin="miter"/>' % (" ".join("%.1f,%.1f" % pt for pt in raw_on), "#e67e22"))

    # Доріжка 3
    p.append(arrow(ox, y3, ox + aw, y3, color=MUTED, sw=1.2))
    p.append(text(ox - 15, y3 - 20, "Амплітудний +\nЧасовий (Hold-off)", size=10, color=FIELD, bold=True))
    t_min_w = 170
    guarded_on = [(ox, y3), (ox + 60, y3), (ox + 60, y3 - 25), (ox + 60 + t_min_w, y3 - 25),
                  (ox + 60 + t_min_w, y3), (ox + 350, y3), (ox + 350, y3 - 25),
                  (ox + 350 + t_min_w, y3 - 25), (ox + 350 + t_min_w, y3), (ox + aw - 40, y3)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="miter"/>' % (" ".join("%.1f,%.1f" % pt for pt in guarded_on), FIELD))

    p.append(rect(ox + 60, y3 - 32, t_min_w, 32, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=2))
    p.append(text(ox + 60 + t_min_w/2, y3 - 38, "t_min_on (гарантований робочий хід)", size=9, color=FIELD, bold=True))

    p.append(rect(ox + 60 + t_min_w, y3 - 32, 120, 32, fill="#fdecea", stroke=POS, sw=1.0, rx=2))
    p.append(text(ox + 60 + t_min_w + 60, y3 + 18, "t_min_off (пауза компресора / анти-старт)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "time-hysteresis-holdoff.svg"), W, H, *p,
           title="Часовий гістерезис (Hold-off): захист від коротких циклів комутації")


# ── 4. signal-pipeline: повний конвеєр обробки сигналу ────────────────────────
def fig_signal_pipeline():
    W, H = 760, 260
    p = []

    stages = [
        ("1. Сенсор / АЦП", "Шум квантування,\nсплески завад,\nнаведення 50 Гц", "#7f8c8d", "#f8f9fa"),
        ("2. Медіана N=3..5", "Нелінійний фільтр:\nвідсікає поодинокі\nімпульсні викиди", "#2980b9", "#ebf5fb"),
        ("3. EMA / IIR ФНЧ", "Експоненційне\nзгладжування шуму:\ny[n]=α·x+(1-α)·y", "#8e44ad", "#f4ecf7"),
        ("4. Тригер Шмітта", "Два пороги T_low/high:\nамплітудна зона\nнечутливості ΔT", "#d35400", "#fef5e7"),
        ("5. Часовий бар'єр", "Hold-off таймери:\nмін. час увімкнення\nй паузи (t_dwell)", "#27ae60", "#eafaf0"),
    ]

    card_w = 125
    gap = 22
    start_x = 42
    cy = 110

    for i, (title, desc, col, fill) in enumerate(stages):
        cx = start_x + i * (card_w + gap) + card_w / 2
        ht = fitbox(cx - card_w/2, cy - 55, card_w, 110,
                    "%s\n\n%s" % (title, desc),
                    size=11, pad=6, fill=fill, stroke=col, sw=1.6, color=INK, bold=False)
        p.append(ht)

        if i < len(stages) - 1:
            ax1 = cx + card_w / 2 + 2
            ax2 = ax1 + gap - 4
            p.append(arrow(ax1, cy, ax2, cy, color=LINE, sw=1.8))

    last_cx = start_x + 4 * (card_w + gap) + card_w / 2
    out_x = last_cx + card_w / 2 + 2
    p.append(arrow(out_x, cy, out_x + 25, cy, color=POS, sw=2.2))
    p.append(text(out_x + 30, cy + 4, "Ключ / Реле", size=10, color=POS, anchor="start", bold=True))

    p.append(text(W / 2, H - 25, "Конвеєр перетворює зашумлені відліки на стабільні, безпечні команди комутації",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "signal-pipeline.svg"), W, H, *p,
           title="П'ять ланок обробки сигналу: від сирого АЦП до надійного реле")


if __name__ == "__main__":
    fig_relay_chattering()
    fig_schmitt_hysteresis_loop()
    fig_time_hysteresis_holdoff()
    fig_signal_pipeline()
    print("All figures generated successfully in", OUT)
