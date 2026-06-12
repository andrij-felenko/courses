# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 §4.13.8c — «LDO проти buck-конвертера для батареї: quiescent current вирішує».
Запуск: python figs-r13-s8-c-ldo-vs-buck.py

Вивід → ./img/
  fig-13-8c-1-iq-budget.svg   — Рис. 4.13.8c.1
  fig-13-8c-2-crossover.svg   — Рис. 4.13.8c.2
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.8c.1 — Стек-діаграма середнього струму сплячого циклу
# Три колонки: (1) без стабілізатора, (2) з AMS1117, (3) з low-I_Q LDO
# Вісь Y розривна: нижній діапазон 0..50 мкА, верхній 4800..5100 мкА
# ─────────────────────────────────────────────────────────────────────────────
def fig1_iq_budget():
    W, H = 760, 480
    title_h = 38

    # Колонки
    col_labels = ["Корисне\nспоживання", "AMS1117-клас\n(I_Q ≈ 5 мА)", "Low-I_Q LDO\n(I_Q ≈ 3 мкА)"]
    col_x = [150, 380, 610]
    bar_w = 110

    # Значення мкА
    useful_sleep = 10.0    # МК deep-sleep
    useful_periph = 5.0    # корисна периферія (датчик у sleep)
    iq_ams = 5000.0        # AMS1117
    iq_lowiq = 3.0         # low-I_Q LDO

    # Параметри двох зон (в мкА)
    # Нижня зона: 0..60 мкА → відображається від y=430 до y=200
    # Верхня зона: 4800..5200 мкА → відображається від y=180 до y=60
    y_bottom = 430
    y_break_lo = 200   # нижня межа розриву
    y_break_hi = 185   # верхня межа розриву
    y_top = 65

    lo_range = 60.0        # мкА, нижня зона
    hi_min = 4800.0        # мкА, верхня зона мін
    hi_max = 5200.0        # мкА, верхня зона макс

    px_lo = y_bottom - y_break_lo   # пікселів на нижню зону
    px_hi = y_break_hi - y_top      # пікселів на верхню зону

    def y_for_lo(uA):
        """Координата Y для значення в нижній зоні (0..lo_range мкА)."""
        frac = min(uA, lo_range) / lo_range
        return y_bottom - frac * px_lo

    def y_for_hi(uA):
        """Координата Y для значення у верхній зоні (hi_min..hi_max мкА)."""
        frac = (min(uA, hi_max) - hi_min) / (hi_max - hi_min)
        return y_break_hi - frac * px_hi

    parts = []

    # Заголовок
    parts.append(text(W // 2, 26, "Куди тече струм сплячого пристрою", size=16, bold=True))

    # ── Вісь Y (ліворуч) ──
    axis_x = 60
    parts.append(line(axis_x, y_top - 5, axis_x, y_bottom + 5, sw=1.5))

    # Мітки нижньої зони
    for val, label in [(0, "0"), (10, "10"), (30, "30"), (60, "60 мкА")]:
        yy = y_for_lo(val)
        parts.append(line(axis_x - 5, yy, axis_x, yy, sw=1))
        parts.append(text(axis_x - 8, yy + 5, label, size=11, anchor="end", color=MUTED))

    # Мітки верхньої зони
    for val, label in [(5000, "5000 мкА"), (5200, "5200")]:
        yy = y_for_hi(val)
        parts.append(line(axis_x - 5, yy, axis_x, yy, sw=1))
        parts.append(text(axis_x - 8, yy + 5, label, size=11, anchor="end", color=MUTED))

    # Знак розриву осі
    brk_cx = axis_x
    for yy in [y_break_lo + 2, y_break_hi - 2]:
        parts.append(line(brk_cx - 8, yy - 5, brk_cx + 5, yy + 5, color=MUTED, sw=2))

    # Зона розриву (заштрихована смужка)
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#f0f0f0" stroke="none"/>' % (
        axis_x - 2, y_break_hi, W - axis_x + 2, y_break_lo - y_break_hi))
    parts.append(text(axis_x + (W - axis_x) // 2, (y_break_lo + y_break_hi) // 2 + 5,
                      "// розрив осі //", size=11, color=MUTED))

    # ── Колонка 1: тільки корисне споживання ──
    cx1 = col_x[0]

    # МК deep-sleep ~10 мкА
    y1_top = y_for_lo(useful_sleep + useful_periph)
    y1_bot = y_bottom
    h1 = y1_bot - y1_top
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="3"/>' % (
        cx1 - bar_w // 2, y1_top, bar_w, h1, NEG + "44", NEG))

    # Підпис усередині
    parts.append(fitbox(cx1 - bar_w // 2, y1_top, bar_w, h1,
                        "МК ~10 мкА\n+ периферія ~5 мкА",
                        size=11, fill=NEG + "22", stroke=NEG, color=INK))

    # ── Колонка 2: AMS1117 ──
    cx2 = col_x[1]

    # Корисне — нижня зона
    y2_useful_top = y_for_lo(useful_sleep + useful_periph)
    h2_useful = y_bottom - y2_useful_top
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="0"/>' % (
        cx2 - bar_w // 2, y2_useful_top, bar_w, h2_useful, NEG + "33", NEG))

    # I_Q AMS1117 — перекриває від дна нижньої зони до верхньої (суцільний товстий блок)
    y2_iq_top = y_for_hi(iq_ams)
    y2_iq_bot = y_bottom
    # Нижня частина (видима в нижній зоні — весь стовпець)
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="0"/>' % (
        cx2 - bar_w // 2, y_break_hi, bar_w, y_break_lo - y_break_hi, POS + "dd", POS))
    # Верхня частина (у верхній зоні)
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="3"/>' % (
        cx2 - bar_w // 2, y2_iq_top, bar_w, y_break_hi - y2_iq_top, POS + "dd", POS))

    # Підпис I_Q всередині (верхня зона)
    lbl2, lw2, lh2 = textbox(cx2, y2_iq_top + 30, "I_Q AMS1117\n≈ 5000 мкА",
                              size=12, fill=POS + "33", stroke=POS, color=INK, bold=True)
    parts.append(lbl2)

    # Стрілка "в 500 разів більше"
    parts.append(arrow(cx2 + bar_w // 2 + 5, y2_iq_top + 20,
                       cx2 + bar_w // 2 + 5, y_bottom - 5, color=POS, sw=1.5))
    ratio_lbl, _, _ = textbox(cx2 + bar_w // 2 + 48, (y2_iq_top + y_bottom) // 2,
                              "×500\nбільше", size=11, fill="#fff0f0", stroke=POS, color=POS, bold=True)
    parts.append(ratio_lbl)

    # ── Колонка 3: low-I_Q LDO ──
    cx3 = col_x[2]

    # Корисне + малий I_Q — всі в нижній зоні
    total3 = useful_sleep + useful_periph + iq_lowiq   # ~18 мкА
    y3_top = y_for_lo(total3)
    h3 = y_bottom - y3_top

    # Основний бар (корисне)
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="3"/>' % (
        cx3 - bar_w // 2, y_for_lo(useful_sleep + useful_periph), bar_w,
        y_bottom - y_for_lo(useful_sleep + useful_periph), NEG + "44", NEG))

    # I_Q low-IQ LDO (3 мкА — маленька смужка зверху)
    y3_iq_top = y_for_lo(total3)
    y3_iq_bot = y_for_lo(useful_sleep + useful_periph)
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5" rx="3"/>' % (
        cx3 - bar_w // 2, y3_iq_top, bar_w, y3_iq_bot - y3_iq_top, FIELD + "cc", FIELD))

    parts.append(fitbox(cx3 - bar_w // 2, y_for_lo(useful_sleep + useful_periph), bar_w,
                        y_bottom - y_for_lo(useful_sleep + useful_periph),
                        "МК ~10 мкА\n+ периферія ~5 мкА",
                        size=11, fill=NEG + "22", stroke=NEG, color=INK))

    lbl3, _, _ = textbox(cx3, y3_iq_top - 18, "I_Q low-IQ\n≈ 3 мкА",
                         size=11, fill="#f0fff0", stroke=FIELD, color=FIELD, bold=True)
    parts.append(lbl3)

    # ── Підписи колонок ──
    for i, (cx, lbl) in enumerate(zip(col_x, col_labels)):
        lbox, bw, bh = textbox(cx, H - 32, lbl, size=12, fill=FILL, stroke=LINE, color=INK)
        parts.append(lbox)

    # Підсумковий висновок
    concl, _, _ = textbox(W // 2, H - 5,
                          "На батареї бюджет з'їдає не корисне споживання, а I_Q стабілізатора.",
                          size=12, fill="#fffde7", stroke="#f39c12", color=INK)
    # (не додаємо — вставляємо в caption)

    render(os.path.join(OUT, "fig-13-8c-1-iq-budget.svg"), W, H, *parts)
    print("fig-13-8c-1-iq-budget.svg  OK")


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.8c.2 — Криві ефективної втрати проти струму навантаження (лог X)
# LDO low-I_Q та Buck-PFM; точка перетину «межа доцільності»
# ─────────────────────────────────────────────────────────────────────────────
def fig2_crossover():
    W, H = 760, 420
    title_h = 38

    left_m = 70
    right_m = 30
    top_m = title_h + 20
    bottom_m = H - 80

    chart_w = W - left_m - right_m
    chart_h = bottom_m - top_m

    # Лог-шкала X: 10 мкА … 300 мА
    x_min_log = math.log10(10e-3)       # 10 мкА в мА
    x_max_log = math.log10(300.0)       # 300 мА

    def x_for(mA):
        lv = math.log10(max(mA, 10e-3))
        frac = (lv - x_min_log) / (x_max_log - x_min_log)
        return left_m + frac * chart_w

    # Вісь Y: відносна «неефективність» (умовні одиниці, 0..1, лінійна)
    y_max_val = 1.0
    y_min_val = 0.0

    def y_for(v):
        frac = (v - y_min_val) / (y_max_val - y_min_val)
        return bottom_m - frac * chart_h

    # Параметри кривих
    # LDO (low-I_Q, I_Q = 3 мкА = 0.003 мА):
    #   loss = I_Q / I_load * (1 + delta_V/V_out) + delta_V/V_out
    #   спрощено: loss ~ I_Q_norm + linear_term
    #   Показуємо: при малих I — плоска (I_Q домінує), при великих — лінійно росте
    IQ_ldo = 0.003      # мА
    Vdrop_ldo = 0.5     # В спаду LDO (Vin=3.7, Vout=3.3)
    Vout = 3.3

    def ldo_loss(mA):
        # Відносна втрата: (I_Q + I_load * Vdrop/Vout) / (I_Q + I_load)
        # нормалізована для відображення
        heat_frac = (IQ_ldo * (Vdrop_ldo / Vout + 1) + mA * Vdrop_ldo / Vout) / (IQ_ldo + mA)
        return min(heat_frac * 0.85, 0.95)

    # Buck-PFM (I_Q ~ 0.02 мА = 20 мкА):
    #   На малих струмах I_Q домінує (крива висока),
    #   на великих — ефективність 88 % → втрата 12 %
    IQ_buck = 0.020     # мА
    eff_max = 0.88      # ефективність при великому струмі

    def buck_loss(mA):
        # Плавний перехід: при малих I — I_Q/I_load «розмазаний» по виходу
        # При великих — (1 - eff_max)
        base_loss = 1.0 - eff_max   # 0.12
        iq_contrib = IQ_buck / (IQ_buck + mA) * 0.7
        return min(base_loss + iq_contrib, 0.95)

    # Точки кривих
    currents = []
    cur = 0.010   # 10 мкА в мА
    while cur <= 300.0:
        currents.append(cur)
        cur *= 1.15

    def polyline_pts(fn):
        pts = []
        for c in currents:
            px = x_for(c)
            py = y_for(fn(c))
            pts.append("%.1f,%.1f" % (px, py))
        return " ".join(pts)

    parts = []

    # Заголовок
    parts.append(text(W // 2, 26, "Хто виграє — залежить від струму навантаження", size=16, bold=True))

    # Фон зон «сон» і «активність»
    x_sleep_right = x_for(0.1)   # 100 мкА ≈ межа «зони сну»
    parts.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#eaf4fb" stroke="none" rx="0"/>' % (
        left_m, top_m, x_sleep_right - left_m, chart_h))
    parts.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#fef9e7" stroke="none" rx="0"/>' % (
        x_sleep_right, top_m, left_m + chart_w - x_sleep_right, chart_h))

    # Крива LDO
    pts_ldo = polyline_pts(ldo_loss)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_ldo, NEG))

    # Крива Buck-PFM
    pts_buck = polyline_pts(buck_loss)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_buck, POS))

    # Точка перетину (аналітично ~0.07 мА = 70 мкА)
    cross_mA = 0.070
    cross_x = x_for(cross_mA)
    cross_y = y_for(ldo_loss(cross_mA))
    parts.append(circle(cross_x, cross_y, 7, fill="#fff", stroke=FIELD, sw=2.5))
    cross_lbl, _, _ = textbox(cross_x + 10, cross_y - 28,
                              "межа\nдоцільності\n(~70 мкА)",
                              size=11, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=False)
    parts.append(cross_lbl)

    # Підписи кривих
    ldo_end_x = x_for(300) - 5
    ldo_end_y = y_for(ldo_loss(300))
    lbl_ldo, _, _ = textbox(ldo_end_x - 55, ldo_end_y - 22,
                            "LDO\n(low-I_Q)", size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(lbl_ldo)

    buck_end_x = x_for(300) - 5
    buck_end_y = y_for(buck_loss(300))
    lbl_buck, _, _ = textbox(buck_end_x - 55, buck_end_y + 22,
                             "Buck-PFM", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(lbl_buck)

    # Підписи зон
    zone_y = top_m + 18
    parts.append(text((left_m + x_sleep_right) / 2, zone_y,
                      "тут живе «сон»", size=12, color=NEG, anchor="middle"))
    parts.append(text((x_sleep_right + left_m + chart_w) / 2, zone_y,
                      "тут живе «передача»", size=12, color="#e67e22", anchor="middle"))

    # Вісь X
    parts.append(line(left_m, bottom_m, left_m + chart_w, bottom_m, sw=1.5))
    x_ticks = [(0.010, "10 мкА"), (0.050, "50"), (0.100, "100 мкА"),
               (1.0, "1 мА"), (10.0, "10"), (100.0, "100"), (300.0, "300 мА")]
    for mA, lbl in x_ticks:
        xx = x_for(mA)
        parts.append(line(xx, bottom_m, xx, bottom_m + 5, sw=1))
        parts.append(text(xx, bottom_m + 18, lbl, size=10, color=MUTED, anchor="middle"))

    parts.append(text(left_m + chart_w / 2, bottom_m + 38,
                      "Струм навантаження (лог. шкала)", size=12, color=MUTED))

    # Вісь Y
    parts.append(line(left_m, top_m, left_m, bottom_m, sw=1.5))
    for frac, lbl in [(0, "мін"), (0.5, ""), (1.0, "макс")]:
        yy = y_for(frac)
        parts.append(line(left_m - 5, yy, left_m, yy, sw=1))
        if lbl:
            parts.append(text(left_m - 8, yy + 5, lbl, size=10, color=MUTED, anchor="end"))

    rot_lbl = ('<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s" '
               'text-anchor="middle" transform="rotate(-90, %d, %d)">Ефективна втрата / неефективність</text>' % (
                   20, top_m + chart_h // 2, FONT, MUTED, 20, top_m + chart_h // 2))
    parts.append(rot_lbl)

    render(os.path.join(OUT, "fig-13-8c-2-crossover.svg"), W, H, *parts)
    print("fig-13-8c-2-crossover.svg  OK")


if __name__ == "__main__":
    fig1_iq_budget()
    fig2_crossover()
    print("Усі фігури згенеровано у", OUT)
