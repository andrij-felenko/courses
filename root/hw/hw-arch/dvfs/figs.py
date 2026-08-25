# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_vf_pair():
    """Напруга задає стелю частоти; разом дають потужність (V² · f)."""
    W, H = 720, 380
    frags = []
    # --- ліворуч: пов'язана пара V -> f_max (похила межа) ---
    ox, oy = 70, 300      # початок осей
    aw, ah = 250, 210     # довжина осей
    frags.append(text(ox + aw / 2, 60, "Напруга задає стелю частоти", size=15, bold=True))
    # осі
    frags.append(arrow(ox, oy, ox, oy - ah))          # вісь f_max (вгору)
    frags.append(arrow(ox, oy, ox + aw, oy))          # вісь V (праворуч)
    frags.append(text(ox - 10, oy - ah + 4, "f_max", size=13, color=MUTED, anchor="end"))
    frags.append(text(ox + aw, oy + 20, "напруга V", size=13, color=MUTED, anchor="end"))
    frags.append(text(ox - 46, oy - ah / 2, "гранична", size=11, color=MUTED, anchor="middle"))
    frags.append(text(ox - 46, oy - ah / 2 + 13, "частота", size=11, color=MUTED, anchor="middle"))
    # похила лінія f_max(V): вища напруга -> вища гранична частота
    x0, y0 = ox + 22, oy - 18
    x1, y1 = ox + aw - 20, oy - ah + 24
    frags.append(line(x0, y0, x1, y1, color=FIELD, sw=3))
    frags.append(text((x0 + x1) / 2 + 42, (y0 + y1) / 2 + 2, "f_max(V)", size=12, color=FIELD, bold=True, anchor="start"))
    # дві робочі точки на прямій
    frags.append(circle(x0 + 34, y0 - 28, 5, fill=NEG, stroke=NEG))
    frags.append(text(x0 + 34, y0 - 40, "низька", size=10, color=NEG))
    frags.append(circle(x1 - 34, y1 + 28, 5, fill=POS, stroke=POS))
    frags.append(text(x1 - 34, y1 + 20, "висока", size=10, color=POS))
    frags.append(text(ox + aw / 2, oy + 44, "нижча напруга → повільніші вентилі → нижча стеля", size=11, color=INK))

    # --- праворуч: внесок у потужність (V² проти f) ---
    bx = 430
    frags.append(text(bx + 120, 60, "Внесок у потужність", size=15, bold=True))
    b, w, h = textbox(bx + 120, 150, "P = α · C · V² · f", size=17, bold=True, pad=14, stroke=INK)
    frags.append(b)
    frags.append(text(bx + 120 - 18, 190, "V²", size=13, color=POS, bold=True, anchor="middle"))
    frags.append(text(bx + 120 - 18, 206, "квадрат", size=10, color=POS, anchor="middle"))
    frags.append(text(bx + 120 + 40, 190, "f", size=13, color=NEG, bold=True, anchor="middle"))
    frags.append(text(bx + 120 + 40, 206, "лінійно", size=10, color=NEG, anchor="middle"))
    # стовпчики впливу: -10% по кожній ручці
    base = 300
    frags.append(line(bx + 8, base, bx + 240, base, color=MUTED, sw=1))
    # напруга -10% -> ~-19% (квадрат)
    frags.append(rect(bx + 30, base - 110, 46, 110, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(bx + 53, base - 118, "−19%", size=12, color=POS, bold=True))
    frags.append(text(bx + 53, base + 18, "−10% V", size=11, color=INK))
    # частота -10% -> -10% (лінійно)
    frags.append(rect(bx + 150, base - 58, 46, 58, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(bx + 173, base - 66, "−10%", size=12, color=NEG, bold=True))
    frags.append(text(bx + 173, base + 18, "−10% f", size=11, color=INK))
    frags.append(text(bx + 120, base + 44, "та сама −10% дає більший ефект від напруги", size=11, color=INK))

    render(os.path.join(OUT, 'vf-pair.svg'), W, H, *frags)


def fig_energy_bars():
    """Та сама робота на двох парах V-f: площа (джоулі) — те, що важить."""
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 34, "Та сама робота — дві пари «напруга-частота»", size=16, bold=True))
    base = 300
    # спільна вісь часу
    frags.append(arrow(50, base, W - 40, base))
    frags.append(text(W - 40, base + 22, "час", size=12, color=MUTED, anchor="end"))
    frags.append(arrow(50, base, 50, 70))
    frags.append(text(50, 60, "потужність", size=12, color=MUTED, anchor="middle"))

    # ліворуч: низька пара — низько й широко (площа менша)
    lx = 70
    lw, lh = 300, 70
    frags.append(rect(lx, base - lh, lw, lh, fill="#eaf6ee", stroke=FIELD, sw=2.5))
    frags.append(text(lx + lw / 2, base - lh - 14, "низька пара V-f: довго, дешево за операцію", size=12, color=FIELD, bold=True))
    frags.append(text(lx + lw / 2, base - lh / 2 + 4, "менша площа = менше джоулів", size=12, color=INK))
    frags.append(line(lx, base + 6, lx + lw, base + 6, color=FIELD, sw=2))
    frags.append(text(lx + lw / 2, base + 22, "довший час", size=11, color=MUTED))

    # праворуч: висока пара — високо й вузько (площа більша)
    rx = 400
    rw, rh = 150, 150
    frags.append(rect(rx, base - rh, rw, rh, fill="#fdecea", stroke=POS, sw=2.5))
    frags.append(text(rx + rw / 2, base - rh - 14, "висока пара V-f:", size=12, color=POS, bold=True))
    frags.append(text(rx + rw / 2, base - rh + 4, "швидко,", size=12, color=INK))
    frags.append(text(rx + rw / 2, base - rh + 20, "дорого", size=12, color=INK))
    frags.append(text(rx + rw / 2, base - rh + 36, "за операцію", size=12, color=INK))
    frags.append(line(rx, base + 6, rx + rw, base + 6, color=POS, sw=2))
    frags.append(text(rx + rw / 2, base + 22, "коротший час", size=11, color=MUTED))

    frags.append(text(W / 2, H - 14, "Батарея платить за ПЛОЩУ (джоулі), не за висоту стовпчика", size=12, color=INK, bold=True))
    render(os.path.join(OUT, 'energy-bars.svg'), W, H, *frags)


def fig_switch_order():
    """Заборонена зона + правильний порядок перемикання пари."""
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 32, "Порядок перемикання: обійти заборонену зону", size=16, bold=True))
    # площина V (x) x f (y)
    ox, oy = 90, 330
    aw, ah = 400, 250
    frags.append(arrow(ox, oy, ox, oy - ah))       # f вгору
    frags.append(arrow(ox, oy, ox + aw, oy))       # V праворуч
    frags.append(text(ox - 10, oy - ah + 2, "частота f", size=13, color=MUTED, anchor="end"))
    frags.append(text(ox + aw, oy + 22, "напруга V", size=13, color=MUTED, anchor="end"))

    # похила межа f_max(V): над нею — заборонено
    x0, y0 = ox + 10, oy - 30
    x1, y1 = ox + aw - 20, oy - ah + 20
    frags.append(line(x0, y0, x1, y1, color=INK, sw=2, dash="6 5"))
    # заштрихована заборонена зона (трикутник над межею) — світло-червоний полігон
    poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" '
            'stroke="none" opacity="0.9"/>' % (x0, y0, x1, y1, x0, y1))
    frags.append(poly)
    frags.append(fitbox(ox + 30, oy - ah + 26, 150, 46,
                        "заборонена зона:\nf зависока для V", size=11, stroke=POS, fill="none", color=POS))
    frags.append(text((x0 + x1) / 2 + 70, (y0 + y1) / 2 + 26, "межа f_max(V)", size=11, color=INK, anchor="start"))

    # точки LOW і HIGH
    lowx, lowy = ox + 60, oy - 40
    hix, hiy = ox + aw - 70, oy - ah + 55
    frags.append(circle(lowx, lowy, 6, fill=NEG, stroke=NEG))
    frags.append(text(lowx - 6, lowy + 22, "LOW", size=12, color=NEG, bold=True, anchor="middle"))
    frags.append(circle(hix, hiy, 6, fill=POS, stroke=POS))
    frags.append(text(hix + 4, hiy - 12, "HIGH", size=12, color=POS, bold=True, anchor="middle"))

    # РОЗГІН (зелений): вправо (V+) потім вгору (f+) — обходить знизу-справа
    frags.append(arrow(lowx, lowy, hix, lowy, color=FIELD, sw=2.6))     # спершу V вгору (вправо)
    frags.append(arrow(hix, lowy, hix, hiy, color=FIELD, sw=2.6))       # потім f вгору
    frags.append(text((lowx + hix) / 2, lowy + 20, "1. напруга ↑", size=11, color=FIELD, bold=True))
    frags.append(text(hix + 52, (lowy + hiy) / 2, "2. частота ↑", size=11, color=FIELD, bold=True, anchor="middle"))

    # ГАЛЬМУВАННЯ (синій): вниз (f-) потім вліво (V-)
    frags.append(arrow(hix - 10, hiy, hix - 10, lowy, color=NEG, sw=2.6, ))  # f вниз
    frags.append(arrow(hix - 10, lowy, lowx, lowy, color=NEG, sw=2.6))       # V вниз (вліво)

    # легенда — у порожньому куті (висока V, низька f)
    lgx, lgy = ox + aw - 158, oy - 74
    frags.append(rect(lgx, lgy, 156, 46, fill=BG, stroke=MUTED, sw=1))
    frags.append(line(lgx + 12, lgy + 16, lgx + 34, lgy + 16, color=FIELD, sw=3))
    frags.append(text(lgx + 42, lgy + 20, "розгін", size=11, color=INK, anchor="start"))
    frags.append(line(lgx + 12, lgy + 34, lgx + 34, lgy + 34, color=NEG, sw=3))
    frags.append(text(lgx + 42, lgy + 38, "гальмування", size=11, color=INK, anchor="start"))

    frags.append(text(W / 2, H - 12, "Угору — напруга першою; униз — частота першою", size=12, color=INK, bold=True))
    render(os.path.join(OUT, 'switch-order.svg'), W, H, *frags)


def fig_hist_timeline():
    """Три ранні шляхи DVFS (2000–2004) + еволюція від 2 режимів до дрібної сітки."""
    W, H = 760, 470
    frags = []
    frags.append(text(W / 2, 30, "Ранній DVFS: від двох режимів до дрібної сітки", size=16, bold=True))

    # --- вісь часу (горизонталь) ---
    ax0, ax1 = 70, W - 40
    ay = 95
    frags.append(arrow(ax0, ay, ax1, ay))
    frags.append(text(ax1, ay - 12, "час", size=12, color=MUTED, anchor="end"))
    # позначки років
    years = [("2000", 0.06), ("2001", 0.33), ("2002", 0.55), ("2003", 0.72), ("2004", 0.9)]
    for lbl, t in years:
        x = ax0 + (ax1 - ax0 - 20) * t
        frags.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1))
        frags.append(text(x, ay + 20, lbl, size=11, color=MUTED))

    # --- три віхи-крапки на осі з підписами ---
    def milestone(t, top_lines, color, up=True):
        x = ax0 + (ax1 - ax0 - 20) * t
        frags.append(circle(x, ay, 5, fill=color, stroke=color))
        by = 52 if up else ay + 40
        b, w, h = textbox(x, by, top_lines, size=10, pad=6, stroke=color, fill=BG, color=INK)
        frags.append(b)
        # тонкий поводок від крапки до рамки
        frags.append(line(x, ay - 5 if up else ay + 5, x, by + (h / 2 if up else -h / 2), color=color, sw=1, dash="3 3"))
        return x

    milestone(0.06, "Intel SpeedStep\n18.01.2000", POS, up=True)
    milestone(0.15, "Transmeta LongRun\n19.01.2000", NEG, up=False)
    milestone(0.33, "AMD PowerNow!\nMobile Athlon 4 · 2001", FIELD, up=True)
    milestone(0.9, "AMD Cool'n'Quiet\nдесктоп · 2004", MUTED, up=False)

    # --- нижній ряд: дві сітки робочих точок (груба ліворуч → дрібна праворуч) ---
    gy = 250
    frags.append(text(W / 2, gy - 18, "Сітка робочих точок «напруга-частота»: грубшала стелею, дрібнішала знизу", size=12, bold=True))

    # ліва панель: 2 зашиті режими
    lx, lw = 80, 220
    ph = 150
    frags.append(rect(lx, gy, lw, ph, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(lx + lw / 2, gy + 22, "2 зашиті режими", size=12, color=POS, bold=True))
    frags.append(text(lx + lw / 2, gy + 38, "(перша SpeedStep)", size=10, color=MUTED))
    # осі мініатюри
    mox, moy = lx + 30, gy + ph - 24
    maw, mah = lw - 70, ph - 68
    frags.append(line(mox, moy, mox, moy - mah, color=MUTED, sw=1))
    frags.append(line(mox, moy, mox + maw, moy, color=MUTED, sw=1))
    frags.append(text(mox - 8, moy - mah, "f", size=10, color=MUTED, anchor="end"))
    frags.append(text(mox + maw, moy + 14, "V", size=10, color=MUTED, anchor="end"))
    # лише дві точки на діагоналі
    frags.append(circle(mox + 18, moy - 16, 4, fill=NEG, stroke=NEG))
    frags.append(circle(mox + maw - 18, moy - mah + 14, 4, fill=POS, stroke=POS))
    frags.append(line(mox + 18, moy - 16, mox + maw - 18, moy - mah + 14, color=MUTED, sw=1, dash="4 4"))

    # стрілка еволюції між панелями
    frags.append(arrow(lx + lw + 10, gy + ph / 2, lx + lw + 60, gy + ph / 2, color=INK, sw=2.4))
    frags.append(text(lx + lw + 35, gy + ph / 2 - 12, "дрібніше", size=10, color=INK))

    # права панель: багато точок
    rx = lx + lw + 70
    rw = 220
    frags.append(rect(rx, gy, rw, ph, fill="#eaf6ee", stroke=FIELD, sw=2))
    frags.append(text(rx + rw / 2, gy + 22, "32 робочі точки", size=12, color=FIELD, bold=True))
    frags.append(text(rx + rw / 2, gy + 38, "(PowerNow! / Enhanced SpeedStep)", size=9, color=MUTED))
    rox, roy = rx + 30, gy + ph - 24
    raw, rah = rw - 70, ph - 68
    frags.append(line(rox, roy, rox, roy - rah, color=MUTED, sw=1))
    frags.append(line(rox, roy, rox + raw, roy, color=MUTED, sw=1))
    frags.append(text(rox - 8, roy - rah, "f", size=10, color=MUTED, anchor="end"))
    frags.append(text(rox + raw, roy + 14, "V", size=10, color=MUTED, anchor="end"))
    # багато точок уздовж діагоналі
    n = 9
    for i in range(n):
        tt = i / (n - 1)
        px = rox + 14 + (raw - 28) * tt
        py = roy - 12 - (rah - 24) * tt
        frags.append(circle(px, py, 3, fill=FIELD, stroke=FIELD))
    frags.append(line(rox + 14, roy - 12, rox + raw - 14, roy - rah + 12, color=MUTED, sw=1, dash="4 4"))

    frags.append(text(W / 2, H - 16, "Дрібна сітка дає зупинитися рівно там, де задача ще встигає — і не спалити зайвого", size=11, color=INK, bold=True))
    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_vf_pair()
    fig_energy_bars()
    fig_switch_order()
    fig_hist_timeline()
    print("done")
