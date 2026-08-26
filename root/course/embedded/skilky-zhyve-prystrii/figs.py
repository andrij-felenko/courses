# -*- coding: utf-8 -*-
"""Фігури до теми «Скільки живе пристрій: від мА·год до діб».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Водоспад втрат ємності: від номіналу до реальної віддачі ──────────────
def fig_derating_waterfall():
    """Водоспадний графік втрат ємності батареї від номіналу до реальної віддачі."""
    W, H = 780, 430
    f = [text(W / 2, 28, "Водоспад ємності: від паспорта (2400 мА·год) до реальної віддачі", size=15, bold=True)]

    bx, by = 60, 340
    top = 70
    max_cap = 2600.0
    sc = (by - top) / max_cap

    # Вісь Y
    f.append(line(bx, by, bx, top, color=INK, sw=1.5))
    for cap_val in [0, 500, 1000, 1500, 2000, 2500]:
        yy = by - cap_val * sc
        f.append(line(bx - 5, yy, bx, yy, color=LINE, sw=1))
        f.append(text(bx - 10, yy + 4, str(cap_val), size=10, color=MUTED, anchor="end"))
    f.append(text(bx - 10, top - 10, "мА·год", size=11, bold=True, anchor="end"))

    # Вісь X
    f.append(line(bx, by, W - 40, by, color=INK, sw=1.5))

    # Стовпчики водоспаду:
    # 1. Номінал: 0 -> 2400 (синій)
    # 2. Відсічка 2.8 В: 2400 -> 2050 (-350) (червоний)
    # 3. Мороз -20 °C: 2050 -> 1600 (-450) (червоний)
    # 4. Імпульсний струм: 1600 -> 1400 (-200) (червоний)
    # 5. Фактична ємність: 0 -> 1400 (зелений)

    bars = [
        ("Номінал", 0, 2400, NEG, "2400 мА·год", "(100 %)"),
        ("Відсічка 2.8 В", 2050, 2400, POS, "−350 мА·год", "(−14.6 %)"),
        ("Мороз −20 °C", 1600, 2050, POS, "−450 мА·год", "(−18.8 %)"),
        ("Імпульси TX", 1400, 1600, POS, "−200 мА·год", "(−8.3 %)"),
        ("Реальна віддача", 0, 1400, FIELD, "1400 мА·год", "(58.3 %)")
    ]

    bw = 88
    gap = 42
    start_x = bx + 35

    for i, (label, y_start, y_end, col, val_str, pct_str) in enumerate(bars):
        cx = start_x + i * (bw + gap)
        y_hi = by - y_end * sc
        y_lo = by - y_start * sc
        h_bar = y_lo - y_hi

        # Прямокутник
        f.append(rect(cx, y_hi, bw, h_bar, fill=col, stroke=col, sw=1.5, rx=4))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" fill-opacity="0.2"/>'
                 % (cx, y_hi, bw, h_bar, col))

        # Текст значення зверху або всередині
        if y_start == 0:
            f.append(text(cx + bw / 2, y_hi - 18, val_str, size=11, color=col, bold=True))
            f.append(text(cx + bw / 2, y_hi - 5, pct_str, size=10, color=col))
        else:
            f.append(text(cx + bw / 2, y_hi - 18, val_str, size=11, color=col, bold=True))
            f.append(text(cx + bw / 2, y_hi - 5, pct_str, size=10, color=col))

        # Підпис знизу осі X
        f.append(text(cx + bw / 2, by + 18, label, size=11, color=INK, bold=True))

        # Пунктирні з'єднувачі між стовпчиками
        if i < len(bars) - 1 and y_start != 0:
            next_x = start_x + (i + 1) * (bw + gap)
            f.append(line(cx + bw, y_lo, next_x, y_lo, color=MUTED, sw=1.2, dash="3,3"))
        elif i == 0:
            next_x = start_x + (i + 1) * (bw + gap)
            f.append(line(cx + bw, y_hi, next_x, y_hi, color=MUTED, sw=1.2, dash="3,3"))

    f.append(fitbox(bx, by + 42, W - bx - 40, 28,
                    "Майже 42 % паспорта втрачається через відсічку напруги, мороз та імпульсний розряд.",
                    size=11, fill="#fdf2f2", stroke=POS, sw=1.2))

    render(os.path.join(IMG, "battery-derating-waterfall.svg"), W, H, *f)


# ── 2. Профіль струму циклу: фази активності, передачі та сну ────────────────
def fig_current_profile():
    """Осцилографічний профіль струму автономного вузла за чотирма фазами."""
    W, H = 780, 420
    f = [text(W / 2, 28, "Профіль споживання струму: 99.6 % часу у сні проти міліамперних піків", size=15, bold=True)]

    bx, by = 70, 320
    top = 70
    pw = 650

    # Вісі координат
    f.append(line(bx, by, bx + pw + 20, by, color=INK, sw=1.5))
    f.append(line(bx, by, bx, top, color=INK, sw=1.5))

    f.append(text(bx + pw + 25, by + 4, "t", size=12, bold=True, anchor="start"))
    f.append(text(bx - 10, top - 8, "I", size=12, bold=True, anchor="end"))

    # Позначки струму по осі Y (нелінійна шкала для наочності)
    y_sleep = by - 15
    y_act = by - 100
    y_tx = by - 210
    y_log = by - 70

    f.append(line(bx - 5, y_sleep, bx, y_sleep, color=LINE, sw=1))
    f.append(text(bx - 10, y_sleep + 4, "5 мкА", size=10, color=MUTED, anchor="end"))

    f.append(line(bx - 5, y_act, bx, y_act, color=LINE, sw=1))
    f.append(text(bx - 10, y_act + 4, "8 мА", size=10, color=MUTED, anchor="end"))

    f.append(line(bx - 5, y_tx, bx, y_tx, color=LINE, sw=1))
    f.append(text(bx - 10, y_tx + 4, "45 мА", size=10, color=MUTED, anchor="end"))

    # Фази в часі
    # Заливка областей під кривою
    # Фаза 1: Сон
    f.append('<rect x="%.1f" y="%.1f" width="120" height="%.1f" fill="%s" fill-opacity="0.1"/>'
             % (bx, y_sleep, by - y_sleep, MUTED))
    # Фаза 2: Активність
    f.append('<rect x="%.1f" y="%.1f" width="80" height="%.1f" fill="%s" fill-opacity="0.2"/>'
             % (bx + 120, y_act, by - y_act, NEG))
    # Фаза 3: Передача TX
    f.append('<rect x="%.1f" y="%.1f" width="180" height="%.1f" fill="%s" fill-opacity="0.25"/>'
             % (bx + 200, y_tx, by - y_tx, POS))
    # Фаза 4: Лог
    f.append('<rect x="%.1f" y="%.1f" width="60" height="%.1f" fill="%s" fill-opacity="0.15"/>'
             % (bx + 380, y_log, by - y_log, FIELD))
    # Фаза 5: Сон 2
    f.append('<rect x="%.1f" y="%.1f" width="190" height="%.1f" fill="%s" fill-opacity="0.1"/>'
             % (bx + 440, y_sleep, by - y_sleep, MUTED))

    # Контур сигналу
    poly_pts = [
        (bx, y_sleep),
        (bx + 120, y_sleep),
        (bx + 120, y_act),
        (bx + 200, y_act),
        (bx + 200, y_tx),
        (bx + 380, y_tx),
        (bx + 380, y_log),
        (bx + 440, y_log),
        (bx + 440, y_sleep),
        (bx + 630, y_sleep)
    ]
    poly_str = " ".join("%.1f,%.1f" % p for p in poly_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_str, INK))

    # Підписи фаз
    f.append(text(bx + 60, y_sleep - 10, "Сон (59.8 с)", size=10, color=MUTED, bold=True))
    f.append(text(bx + 160, y_act - 12, "Вимір (50 мс)", size=10, color=NEG, bold=True))
    f.append(text(bx + 290, y_tx - 14, "Радіо TX (150 мс, 45 мА)", size=11, color=POS, bold=True))
    f.append(text(bx + 410, y_log - 10, "Лог (10 мс)", size=9, color=FIELD, bold=True))

    # Лінія середнього струму I_avg
    y_avg = by - 45
    f.append(line(bx, y_avg, bx + 630, y_avg, color=POS, sw=1.8, dash="5,4"))
    f.append(text(bx + 540, y_avg - 8, "I_avg = 112 мкА", size=11, color=POS, bold=True))

    # Підсумковий блок
    f.append(fitbox(bx, by + 30, pw, 38,
                    "Короткий імпульс передачі (150 мс) забирає 90 % усього заряду циклу (Q = I · t),\n"
                    "хоча 99.6 % часу пристрій перебуває в мікроамперному сні.",
                    size=10, fill="#f4f6f8", stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "current-profile-phases.svg"), W, H, *f)


# ── 3. Стеля автономності: струм сну проти саморозряду хімії ─────────────────
def fig_lifetime_self_discharge():
    """Графік залежності років автономності від струму сну при різному саморозряді."""
    W, H = 780, 430
    f = [text(W / 2, 28, "Стеля автономності: де саморозряд батареї перемагає мікроампери", size=15, bold=True)]

    bx, by = 80, 330
    top = 70
    pw = 640
    ph = by - top

    # Вісі координат
    f.append(line(bx, by, bx + pw, by, color=INK, sw=1.5))
    f.append(line(bx, by, bx, top, color=INK, sw=1.5))

    f.append(text(bx + pw - 10, by + 28, "Струм сну I_sleep (мкА)", size=11, bold=True, anchor="end"))
    f.append(text(bx - 10, top - 10, "Роки автономності", size=11, bold=True, anchor="end"))

    # Позначки осі Y (0..20 років)
    for y_yr in [0, 5, 10, 15, 20]:
        yy = by - (y_yr / 20.0) * ph
        f.append(line(bx - 5, yy, bx, yy, color=LINE, sw=1))
        f.append(text(bx - 10, yy + 4, "%d р." % y_yr, size=10, color=MUTED, anchor="end"))
        if y_yr > 0:
            f.append(line(bx, yy, bx + pw, yy, color="#e5e7eb", sw=1, dash="2,3"))

    # Позначки осі X
    import math
    x_ticks = [(0.5, "0.5"), (2, "2"), (5, "5"), (10, "10"), (20, "20"), (50, "50")]
    for val, lbl in x_ticks:
        xx = bx + (math.log10(val / 0.3) / math.log10(60.0 / 0.3)) * pw
        f.append(line(xx, by, xx, by + 5, color=LINE, sw=1))
        f.append(text(xx, by + 18, lbl, size=10, color=MUTED))

    # Три криві (Li-SOCl2 1%/рік, Li-MnO2 3%/рік, Li-ion 25%/рік)
    def get_curve(self_pct_yr):
        pts = []
        i_self = (2000.0 * (self_pct_yr / 100.0)) / (365.25 * 24.0) * 1000.0 # в мкА
        for step in range(60):
            val = 0.3 * (60.0 / 0.3) ** (step / 59.0)
            xx = bx + (math.log10(val / 0.3) / math.log10(60.0 / 0.3)) * pw
            i_total = val + 4.0 + i_self # мкА
            t_hours = (2000.0 * 1000.0) / i_total
            t_years = min(20.0, t_hours / (365.25 * 24.0))
            yy = by - (t_years / 20.0) * ph
            pts.append((xx, yy))
        return pts

    # 1. Li-SOCl2 (1%/рік)
    pts1 = get_curve(1.0)
    poly1 = " ".join("%.1f,%.1f" % p for p in pts1)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly1, FIELD))
    f.append(text(bx + 110, pts1[5][1] - 12, "Li-SOCl2 (1 %/рік саморозряд) → стеля ~16 років", size=10, color=FIELD, bold=True, anchor="start"))

    # 2. Li-MnO2 (3%/рік)
    pts2 = get_curve(3.0)
    poly2 = " ".join("%.1f,%.1f" % p for p in pts2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly2, NEG))
    f.append(text(bx + 170, pts2[12][1] - 12, "Li-MnO2 (3 %/рік) → стеля ~10 років", size=10, color=NEG, bold=True, anchor="start"))

    # 3. Li-ion акумулятор (25%/рік)
    pts3 = get_curve(25.0)
    poly3 = " ".join("%.1f,%.1f" % p for p in pts3)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly3, POS))
    f.append(text(bx + 260, pts3[25][1] - 12, "Li-ion акумулятор (25 %/рік) → стеля ~3 роки", size=10, color=POS, bold=True, anchor="start"))

    # Зона насичення зліва
    f.append(rect(bx + 1, top, 140, ph, fill="#fdf2e9", stroke="none"))
    f.append(text(bx + 70, top + 25, "Зона насичення:", size=10, color="#d35400", bold=True))
    f.append(text(bx + 70, top + 42, "I_sleep < 1 мкА", size=10, color="#d35400"))
    f.append(text(bx + 70, top + 58, "саморозряд", size=9, color=MUTED))
    f.append(text(bx + 70, top + 72, "переважає сон", size=9, color=MUTED))

    # Підсумковий напис
    f.append(fitbox(bx, by + 40, pw, 32,
                    "Коли струм сну опускається нижче 2 мкА, час життя обмежує виключно саморозряд хімії.",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, "lifetime-vs-sleep-self-discharge.svg"), W, H, *f)


# ── 4. Просадка напруги під імпульсом TX: пасивація та буферний конденсатор ──
def fig_passivation_sag():
    """Динаміка напруги під час імпульсу струму: пасивація проти буферного конденсатора."""
    W, H = 780, 420
    f = [text(W / 2, 28, "Імпульсний провал напруги: пасивація Li-SOCl2 проти буферного HLC", size=15, bold=True)]

    bx, by = 70, 320
    top = 70
    pw = 650
    ph = by - top

    # Вісі координат
    f.append(line(bx, by, bx + pw + 20, by, color=INK, sw=1.5))
    f.append(line(bx, by, bx, top, color=INK, sw=1.5))

    f.append(text(bx + pw + 25, by + 4, "t (мс)", size=11, bold=True, anchor="start"))
    f.append(text(bx - 10, top - 8, "U (В)", size=11, bold=True, anchor="end"))

    # Позначки напруги по осі Y (2.0 В .. 3.8 В)
    v_min, v_max = 2.0, 3.8
    sc_v = ph / (v_max - v_min)

    def v_to_y(v):
        return by - (v - v_min) * sc_v

    for v_val in [2.2, 2.5, 2.8, 3.0, 3.3, 3.6]:
        yy = v_to_y(v_val)
        f.append(line(bx - 5, yy, bx, yy, color=LINE, sw=1))
        f.append(text(bx - 10, yy + 4, "%.1f В" % v_val, size=10, color=MUTED, anchor="end"))

    # Лінія порогу вимикання (BOD / Cutoff = 2.7 В)
    y_bod = v_to_y(2.7)
    f.append(line(bx, y_bod, bx + pw, y_bod, color=POS, sw=1.5, dash="4,4"))
    f.append(text(bx + pw - 10, y_bod - 8, "Поріг скидання МК (Brown-out Reset = 2.7 В)", size=10, color=POS, bold=True, anchor="end"))

    # Сіра смуга імпульсу навантаження (TX Pulse 100 мА)
    x_pulse_start = bx + 140
    x_pulse_end = bx + 420
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.08"/>'
             % (x_pulse_start, top, x_pulse_end - x_pulse_start, ph, INK))
    f.append(text((x_pulse_start + x_pulse_end) / 2, top + 18, "Імпульс передачі радіо (100 мА, 100 мс)", size=10, color=INK, bold=True))

    # Крива 1: Пасивована комірка без буфера (провал нижче 2.7 В -> Crash!)
    pts_unbuf = [
        (bx, v_to_y(3.6)),
        (x_pulse_start, v_to_y(3.6)),
        (x_pulse_start + 10, v_to_y(2.3)),  # різкий провал через шар LiCl
        (x_pulse_start + 60, v_to_y(2.45)), # повільне відновлення (розсмоктування плівки)
        (x_pulse_start + 120, v_to_y(2.8)),
        (x_pulse_end, v_to_y(2.9)),
        (x_pulse_end + 10, v_to_y(3.55)),
        (bx + pw, v_to_y(3.6))
    ]
    poly_unbuf = " ".join("%.1f,%.1f" % p for p in pts_unbuf)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_unbuf, POS))
    f.append(text(x_pulse_start + 45, v_to_y(2.3) + 20, "Провал напруги (Voltage Delay)", size=10, color=POS, bold=True))
    f.append(text(x_pulse_start + 45, v_to_y(2.3) + 34, "→ Brown-out Reset (Краш!)", size=10, color=POS))

    # Крива 2: З паралельним буферним конденсатором / HLC
    pts_buf = [
        (bx, v_to_y(3.6)),
        (x_pulse_start, v_to_y(3.6)),
        (x_pulse_start + 10, v_to_y(3.35)),
        (x_pulse_start + 80, v_to_y(3.25)),
        (x_pulse_end, v_to_y(3.18)),
        (x_pulse_end + 15, v_to_y(3.5)),
        (bx + pw, v_to_y(3.6))
    ]
    poly_buf = " ".join("%.1f,%.1f" % p for p in pts_buf)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_buf, FIELD))
    f.append(text(x_pulse_start + 160, v_to_y(3.25) - 12, "З буферним HLC / суперконденсатором (стабільна робота)", size=10, color=FIELD, bold=True))

    # Підсумковий блок
    f.append(fitbox(bx, by + 30, pw, 38,
                    "Пасивація літієвого анода (плівка LiCl) викликає затримку віддачі напруги під час кидка струму.\n"
                    "Без буферного накопичувача напруга падає нижче 2.7 В, викликаючи несподіваний перезапуск вузла.",
                    size=10, fill="#fdf2f2", stroke=POS, sw=1.2))

    render(os.path.join(IMG, "passivation-voltage-sag.svg"), W, H, *f)


if __name__ == "__main__":
    fig_derating_waterfall()
    fig_current_profile()
    fig_lifetime_self_discharge()
    fig_passivation_sag()
    print("All figures generated successfully.")
