# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: вкладені контури каскаду ────────────────────────────────────────
# Ідея: показати, що зовнішній контур видає НЕ тягу, а бажану швидкість, яка
# стає завданням внутрішнього; внутрішній «загорнутий» у зовнішній.

def fig_nested_loops():
    W, H = 1040, 420
    p = []

    # сумаційні вузли (кружок з «−» зворотного зв'язку)
    sum_outer = (150, 150)
    sum_inner = (430, 150)

    # блоки
    bw, bh = 150, 64
    outer_box = (sum_outer[0] + 56, sum_outer[1] - bh / 2, bw, bh)
    inner_box = (sum_inner[0] + 56, sum_inner[1] - bh / 2, bw, bh)
    motor_box = (inner_box[0] + bw + 60, sum_inner[1] - bh / 2, 110, bh)
    plant_box = (motor_box[0] + 110 + 36, sum_inner[1] - bh / 2, 120, bh)

    # вхід: завдання кута
    p.append(text(40, sum_outer[1] - 12, "завдання", size=12, color=INK, anchor="start"))
    p.append(text(40, sum_outer[1] + 4, "кута", size=12, color=INK, anchor="start"))
    p.append(arrow(86, sum_outer[1], sum_outer[0] - 11, sum_outer[1], color=INK, sw=1.8))

    # сумаційні вузли
    p.append(minus(*sum_outer, r=11))
    p.append(minus(*sum_inner, r=11))

    # зовнішній блок
    p.append(rect(*outer_box, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(outer_box[0] + bw / 2, outer_box[1] + 26, "ЗОВНІШНІЙ ПІД", size=13, color=NEG, bold=True))
    p.append(text(outer_box[0] + bw / 2, outer_box[1] + 46, "(по куту)", size=12, color=MUTED))
    p.append(arrow(sum_outer[0] + 11, sum_outer[1], outer_box[0] - 4, sum_outer[1], color=INK, sw=1.8))

    # зв'язок: вихід зовнішнього = бажана швидкість → вхід внутрішнього суматора
    midx = (outer_box[0] + bw + sum_inner[0]) / 2
    p.append(arrow(outer_box[0] + bw, sum_outer[1], sum_inner[0] - 11, sum_inner[1], color=POS, sw=2.4))
    b_rate, _, _ = textbox(midx, sum_outer[1] - 26, "бажана\nшвидкість",
                           size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b_rate)

    # внутрішній блок
    p.append(rect(*inner_box, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(inner_box[0] + bw / 2, inner_box[1] + 26, "ВНУТРІШНІЙ ПІД", size=13, color=NEG, bold=True))
    p.append(text(inner_box[0] + bw / 2, inner_box[1] + 46, "(по швидкості)", size=12, color=MUTED))
    p.append(arrow(sum_inner[0] + 11, sum_inner[1], inner_box[0] - 4, sum_inner[1], color=INK, sw=1.8))

    # мотори
    p.append(rect(*motor_box, fill=FILL, stroke=LINE, sw=1.6))
    p.append(text(motor_box[0] + 55, motor_box[1] + 38, "МОТОРИ", size=13, color=INK, bold=True))
    p.append(arrow(inner_box[0] + bw, sum_inner[1], motor_box[0] - 4, sum_inner[1], color=INK, sw=1.8))
    p.append(text((inner_box[0] + bw + motor_box[0]) / 2, sum_inner[1] - 12, "тяга", size=11, color=MUTED))

    # апарат
    p.append(rect(*plant_box, fill=FILL, stroke=LINE, sw=1.6))
    p.append(text(plant_box[0] + 60, plant_box[1] + 38, "АПАРАТ", size=13, color=INK, bold=True))
    p.append(arrow(motor_box[0] + 110, sum_inner[1], plant_box[0] - 4, sum_inner[1], color=INK, sw=1.8))

    # вихідна лінія з апарата
    out_x = plant_box[0] + 120
    p.append(line(out_x, sum_inner[1], out_x + 30, sum_inner[1], color=INK, sw=1.8))

    # ── зворотний зв'язок внутрішнього (кутова швидкість, гіроскоп) ──
    fb_in_y = 300
    p.append(line(out_x + 30, sum_inner[1], out_x + 30, fb_in_y, color=FIELD, sw=1.8))
    p.append(line(out_x + 30, fb_in_y, sum_inner[0], fb_in_y, color=FIELD, sw=1.8))
    p.append(arrow(sum_inner[0], fb_in_y, sum_inner[0], sum_inner[1] + 11, color=FIELD, sw=1.8))
    p.append(text((sum_inner[0] + out_x) / 2, fb_in_y + 18,
                  "виміряна кутова швидкість (гіроскоп)", size=11, color=FIELD))

    # ── зворотний зв'язок зовнішнього (кут) ──
    fb_out_y = 360
    p.append(line(out_x + 30, fb_in_y, out_x + 30, fb_out_y, color=NEG, sw=1.8))
    p.append(line(out_x + 30, fb_out_y, sum_outer[0], fb_out_y, color=NEG, sw=1.8))
    p.append(arrow(sum_outer[0], fb_out_y, sum_outer[0], sum_outer[1] + 11, color=NEG, sw=1.8))
    p.append(text((sum_outer[0] + out_x) / 2 - 40, fb_out_y + 18,
                  "виміряний кут", size=11, color=NEG))

    render(os.path.join(OUT, "nested-loops.svg"), W, H, *p,
           title="Каскад: зовнішній контур по куту задає швидкість внутрішньому по швидкості")


# ── Фігура 2: сходинка інтеграторів і де її розриває каскад ───────────────────
# Ідея: від моменту до кута — два інтегрування; один контур долає обидва (важко),
# каскад розриває ланцюг посередині — кожному контуру по одному інтегратору.

def fig_integrator_ladder():
    W, H = 860, 360
    p = []

    # ланцюжок вузлів зліва направо
    ys = 120
    xs = [110, 320, 540, 760]
    labels = ["момент\n(керуємо)", "кутове\nприскорення", "кутова\nшвидкість", "кут\n(мета)"]
    colors = [INK, MUTED, INK, INK]
    for x, lab, c in zip(xs, labels, colors):
        b, _, _ = textbox(x, ys, lab, size=12, color=c, bold=(c == INK),
                          fill=FILL, stroke=LINE)
        p.append(b)

    # стрілки-інтегратори між вузлами
    def inthop(x1, x2, lab):
        out = []
        out.append(arrow(x1 + 56, ys, x2 - 56, ys, color=INK, sw=2.0))
        out.append(text((x1 + x2) / 2, ys - 18, lab, size=12, color=NEG, bold=True))
        return out
    p += inthop(xs[0], xs[1], "")        # момент→прискорення: майже зразу (не інтеграл)
    p.append(text((xs[0] + xs[1]) / 2, ys - 18, "зразу", size=11, color=MUTED))
    p += inthop(xs[1], xs[2], "∫ інтеграл")
    p += inthop(xs[2], xs[3], "∫ інтеграл")

    # ── внизу: внутрішній контур охоплює лише ОДИН інтегратор ──
    yi = 250
    # дуга внутрішнього (від кутової швидкості назад до моменту)
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (xs[2], ys + 26, xs[2], yi, xs[0], yi, xs[0], ys + 26, FIELD))
    bi, _, _ = textbox((xs[0] + xs[2]) / 2, yi + 8,
                       "ВНУТРІШНІЙ контур: один інтегратор → легко зробити швидким",
                       size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bi)

    # ── зверху: зовнішній контур охоплює другий інтегратор ──
    yo = 56
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (xs[3], ys - 26, xs[3], yo, xs[2], yo, xs[2], ys - 26, NEG))
    bo, _, _ = textbox((xs[2] + xs[3]) / 2 + 10, yo - 0,
                       "ЗОВНІШНІЙ контур:\nдругий інтегратор",
                       size=11, color=NEG, bold=True, fill="#eef4ff", stroke=NEG)
    p.append(bo)

    render(os.path.join(OUT, "integrator-ladder.svg"), W, H, *p,
           title="Від моменту до кута — два інтегратори; каскад дає кожному контуру по одному")


# ── Фігура 3: один контур проти каскаду під збуренням ─────────────────────────
# Ідея: після поштовху одноконтурна схема або в'яла, або розгойдується;
# каскад швидко гасить і повертає кут без коливань.

def fig_one_vs_cascade():
    W, H = 820, 380
    ox = 80
    Ax = 660
    oy_top = 130
    oy_bot = 300
    Ay = 70
    span = 10.0          # умовний час
    sx = Ax / span

    def axis(oy, title_txt):
        q = []
        q.append(line(ox - 10, oy, ox + Ax + 30, oy, color=MUTED, sw=1.3))
        q.append(arrow(ox + Ax + 14, oy, ox + Ax + 32, oy, color=MUTED, sw=1.3))
        q.append(text(ox + Ax + 38, oy + 4, "час", size=11, color=MUTED, italic=True, anchor="end"))
        # рівень нуля (бажаний кут)
        q.append(line(ox, oy, ox + Ax, oy, color=NEG, sw=1.0, dash="5 5"))
        q.append(text(ox - 14, oy + 4, "0°", size=11, color=NEG, anchor="end"))
        q.append(text(ox - 14, oy - Ay - 6, title_txt, size=13, color=INK, bold=True, anchor="start"))
        return q

    # момент збурення
    t_dist = 1.2

    def disturb_mark(oy):
        x = ox + t_dist * sx
        return [line(x, oy - Ay - 4, x, oy + Ay * 0.5, color=POS, sw=1.2, dash="3 3"),
                text(x, oy - Ay - 12, "поштовх", size=11, color=POS)]

    def curve(oy, fn, color, sw=2.6):
        pts = []
        for i in range(0, 401):
            t = span * i / 400.0
            y = oy - fn(t) * Ay
            pts.append("%.1f,%.1f" % (ox + t * sx, y))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), color, sw)

    p = []

    # ── верх: один контур ──
    p += axis(oy_top, "ОДИН контур (по куту)")
    p += disturb_mark(oy_top)

    def one_loop(t):
        if t < t_dist:
            return 0.0
        u = t - t_dist
        # запізніла реакція + слабке згасання → переліт і розгойдування
        return 0.95 * math.exp(-0.22 * u) * math.cos(2.2 * u - 0.3) - 0.95 * math.exp(-0.22 * u) * 0.0 + \
               0.0
    # перша реакція — апарат спершу ЗАВАЛЮЄТЬСЯ (збурення штовхнуло кут), тоді гойдання
    def one_loop2(t):
        if t < t_dist:
            return 0.0
        u = t - t_dist
        rise = 1.0 - math.exp(-3.0 * u)              # швидкий початковий заброс від поштовху
        osc = math.exp(-0.25 * u) * math.cos(2.3 * u)  # повільно згасальне гойдання
        return 0.9 * rise * osc
    p.append(curve(oy_top, one_loop2, POS))
    b1, _, _ = textbox(ox + Ax * 0.72, oy_top - Ay - 2,
                       "переліт і довге розгойдування",
                       size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b1)

    # ── низ: каскад ──
    p += axis(oy_bot, "КАСКАД (швидкість усередині)")
    p += disturb_mark(oy_bot)

    def cascade(t):
        if t < t_dist:
            return 0.0
        u = t - t_dist
        # малий короткий заброс, швидко й майже без коливань повертається до 0
        return 0.42 * math.exp(-2.4 * u) * (1.0 - 0.15 * math.cos(3.0 * u))
    p.append(curve(oy_bot, cascade, FIELD))
    b2, _, _ = textbox(ox + Ax * 0.62, oy_bot - Ay * 0.55,
                       "малий заброс, швидко в нуль, без гойдання",
                       size=11, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(b2)

    render(os.path.join(OUT, "one-vs-cascade.svg"), W, H, *p,
           title="Той самий поштовх: один контур розгойдується, каскад гасить його одразу")


if __name__ == "__main__":
    fig_nested_loops()
    fig_integrator_ladder()
    fig_one_vs_cascade()
    print("OK: figures written to", OUT)
