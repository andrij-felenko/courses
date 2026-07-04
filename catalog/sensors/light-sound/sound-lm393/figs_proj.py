# -*- coding: utf-8 -*-
"""Фігури до ВСТАВКИ proj «API/прошивка звукового давача на LM393».
Три SVG про КОД: торохтіння+дебаунс, опитування проти переривання, розмах по AO.
Запуск: python figs_proj.py  → пише у ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Торохтіння одного плеску і вікно дебаунсу
# ─────────────────────────────────────────────────────────────────────────────
def fig_rattle():
    W, H = 860, 400
    p = []

    x0, x1 = 90, 800          # межі осі часу
    hi, lo = 90, 150          # рівні цифрового сигналу DO (hi=1, lo=0)
    axis_y = 230

    # осьова підпис-легенда рівнів (зліва, поза сигналом)
    p.append(text(x0 - 14, hi + 5, "1", size=14, color=POS, anchor="end", bold=True))
    p.append(text(x0 - 14, lo + 5, "0", size=14, color=NEG, anchor="end", bold=True))
    p.append(text(x0 - 42, (hi + lo) / 2 + 4, "DO", size=13, color=MUTED, anchor="end", bold=True))

    # сам сигнал: спокій=1, потім серія коротких провалів у 0 (торохтіння), тоді знов 1
    # опишемо як список сегментів рівня
    segs = [
        (x0, 205, 1),          # спокій
        (205, 225, 0),         # провал 1
        (225, 250, 1),
        (250, 262, 0),         # провал 2
        (262, 300, 1),
        (300, 322, 0),         # провал 3
        (322, 360, 1),
        (360, 372, 0),         # провал 4
        (372, 640, 1),         # плеск згас — знову спокій
    ]
    def yl(v):
        return hi if v == 1 else lo
    prev = None
    for (a, b, v) in segs:
        y = yl(v)
        p.append(line(a, y, b, y, color=INK, sw=2.4))
        if prev is not None:
            # вертикальний фронт
            p.append(line(a, yl(prev), a, y, color=INK, sw=2.4))
        prev = v

    # дужка «один плеск» над усією серією провалів
    p.append(line(205, 60, 372, 60, color=MUTED, sw=1.4))
    p.append(line(205, 60, 205, 74, color=MUTED, sw=1.4))
    p.append(line(372, 60, 372, 74, color=MUTED, sw=1.4))
    p.append(text((205 + 372) / 2, 52, "один плеск = купа провалів", size=13, color=MUTED))

    # вікно дебаунсу: від першого фронту, ширина ~150 мс, заштриховане
    win_a, win_b = 205, 560
    p.append(rect(win_a, hi - 22, win_b - win_a, (lo - hi) + 44,
                  fill="#eef7ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text((win_a + win_b) / 2, lo + 44, "вікно дебаунсу ~150 мс: нові провали ІГНОРУЄМО",
                  size=13, color=NEG))

    # зелена галочка на ПЕРШОМУ фронті — тут рахуємо +1 (напис ЛІВОРУЧ від фронту, поза сигналом)
    p.append(circle(205, lo, 7, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(150, lo + 5, "рахуємо +1", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(line(154, lo, 197, lo, color=FIELD, sw=1.4))
    p.append(text(205, hi - 30, "фронт ↓", size=12, color=FIELD, bold=True))

    # червоні хрестики на провалах усередині вікна — НЕ рахуємо
    for xx in (250, 300, 360):
        p.append(text(xx, lo + 22, "×", size=18, color=POS, bold=True))
    p.append(text(300, lo + 62, "× × × — пропущені, той самий плеск", size=12, color=POS))

    # вісь часу
    p.append(arrow(x0, axis_y + 120, x1, axis_y + 120, color=MUTED, sw=1.4))
    p.append(text(x1, axis_y + 140, "час", size=13, color=MUTED, anchor="end"))

    return render(os.path.join(IMG, 'rattle-debounce.svg'), W, H, *p,
                  title="Торохтіння одного плеску і неблокуюче вікно дебаунсу")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Опитування проти переривання: хто ловить вузький імпульс
# ─────────────────────────────────────────────────────────────────────────────
def fig_poll_vs_int():
    W, H = 860, 430
    p = []

    x0, x1 = 110, 790
    hi, lo = 0, 0             # заповнимо нижче для двох доріжок

    # ── верхня доріжка: опитування ──
    top_hi, top_lo = 90, 140
    p.append(text(x0 - 16, top_hi + 5, "1", size=13, color=POS, anchor="end", bold=True))
    p.append(text(x0 - 16, top_lo + 5, "0", size=13, color=NEG, anchor="end", bold=True))
    p.append(text(x0 - 40, (top_hi + top_lo) / 2 + 4, "DO", size=12, color=MUTED, anchor="end", bold=True))
    p.append(text(x0 - 40, top_hi - 30, "Опитування раз на 50 мс (рідкий digitalRead)",
                  size=14, color=INK, anchor="start", bold=True))

    # сигнал спільний для обох доріжок: два вузькі провали
    dips = [(300, 316), (470, 486)]
    # верхня: намалюємо сигнал
    prev_y = top_hi
    p.append(line(x0, top_hi, dips[0][0], top_hi, color=INK, sw=2.2))
    p.append(line(dips[0][0], top_hi, dips[0][0], top_lo, color=INK, sw=2.2))
    p.append(line(dips[0][0], top_lo, dips[0][1], top_lo, color=INK, sw=2.2))
    p.append(line(dips[0][1], top_lo, dips[0][1], top_hi, color=INK, sw=2.2))
    p.append(line(dips[0][1], top_hi, dips[1][0], top_hi, color=INK, sw=2.2))
    p.append(line(dips[1][0], top_hi, dips[1][0], top_lo, color=INK, sw=2.2))
    p.append(line(dips[1][0], top_lo, dips[1][1], top_lo, color=INK, sw=2.2))
    p.append(line(dips[1][1], top_lo, dips[1][1], top_hi, color=INK, sw=2.2))
    p.append(line(dips[1][1], top_hi, x1 - 10, top_hi, color=INK, sw=2.2))

    # моменти опитування — вертикальні пунктири, рідко (закінчуються трохи нижче сигналу, БЕЗ заходу в смугу підписів)
    poll_bot = top_lo + 12
    polls = list(range(x0 + 20, x1 - 10, 70))
    for px in polls:
        p.append(line(px, top_hi - 10, px, poll_bot, color=MUTED, sw=1, dash="3 4"))
        p.append(circle(px, poll_bot, 3, fill=MUTED, stroke=MUTED))
    p.append(text(x0, top_lo + 66, "↑ моменти читання — рідко; між ними МК не дивиться на вивід",
                  size=12, color=MUTED, anchor="start"))
    # обидва провали між опитуваннями → жодне не влучає (підпис у ЧИСТІЙ смузі під пунктирами)
    p.append(text((dips[0][0] + dips[1][1]) / 2, top_lo + 40,
                  "обидва провали впали МІЖ опитуваннями → проґавлені",
                  size=13, color=POS, bold=True))

    # ── нижня доріжка: переривання ──
    bot_hi, bot_lo = 260, 310
    p.append(text(x0 - 16, bot_hi + 5, "1", size=13, color=POS, anchor="end", bold=True))
    p.append(text(x0 - 16, bot_lo + 5, "0", size=13, color=NEG, anchor="end", bold=True))
    p.append(text(x0 - 40, (bot_hi + bot_lo) / 2 + 4, "DO", size=12, color=MUTED, anchor="end", bold=True))
    p.append(text(x0 - 40, bot_hi - 30, "Переривання по фронту (attachInterrupt, FALLING)",
                  size=14, color=INK, anchor="start", bold=True))

    # той самий сигнал знизу
    p.append(line(x0, bot_hi, dips[0][0], bot_hi, color=INK, sw=2.2))
    p.append(line(dips[0][0], bot_hi, dips[0][0], bot_lo, color=INK, sw=2.2))
    p.append(line(dips[0][0], bot_lo, dips[0][1], bot_lo, color=INK, sw=2.2))
    p.append(line(dips[0][1], bot_lo, dips[0][1], bot_hi, color=INK, sw=2.2))
    p.append(line(dips[0][1], bot_hi, dips[1][0], bot_hi, color=INK, sw=2.2))
    p.append(line(dips[1][0], bot_hi, dips[1][0], bot_lo, color=INK, sw=2.2))
    p.append(line(dips[1][0], bot_lo, dips[1][1], bot_lo, color=INK, sw=2.2))
    p.append(line(dips[1][1], bot_lo, dips[1][1], bot_hi, color=INK, sw=2.2))
    p.append(line(dips[1][1], bot_hi, x1 - 10, bot_hi, color=INK, sw=2.2))

    # на кожному спадному фронті — зелена стрілка «зловили»
    for (a, b) in dips:
        p.append(line(a, bot_hi, a, bot_hi - 18, color=FIELD, sw=1.6))
        p.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s"/>'
                 % (a - 5, bot_hi - 18, a + 5, bot_hi - 18, a, bot_hi - 28, FIELD))
        p.append(circle(a, bot_lo, 6, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text((dips[0][0] + dips[1][1]) / 2, bot_lo + 40,
                  "залізо ловить КОЖЕН спадний фронт — навіть коротший за цикл",
                  size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, 'poll-vs-interrupt.svg'), W, H, *p,
                  title="Опитування проти переривання: вузький провал легко проґавити")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Розмах (peak-to-peak) по аналоговому AO у вікні
# ─────────────────────────────────────────────────────────────────────────────
def fig_p2p():
    W, H = 860, 430
    p = []

    import math
    x0, x1 = 110, 790
    mid = 235                 # середня лінія (спокій ≈ Vcc/2)
    top_lim, bot_lim = 70, 360

    # вісь-рамка вікна
    p.append(rect(x0, top_lim, x1 - x0, bot_lim - top_lim, fill="#fbfbfd", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(x0 - 46, mid + 4, "AO", size=13, color=MUTED, anchor="end", bold=True))
    p.append(line(x0, mid, x1, mid, color=MUTED, sw=1, dash="5 5"))
    p.append(text(x1 - 6, mid - 8, "спокій ≈ Vcc/2", size=11, color=MUTED, anchor="end"))

    # хвиля: загасаючий сплеск довкола середини
    pts = []
    N = 240
    for i in range(N + 1):
        t = i / N
        xx = x0 + (x1 - x0 - 20) * t + 10
        # пакет: наростає й спадає, з коливанням
        env = math.exp(-((t - 0.42) ** 2) / 0.02) * 120
        yy = mid - env * math.sin(t * 34)
        pts.append((xx, yy))
    d = "M " + " L ".join("%.1f %.1f" % (a, b) for (a, b) in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))

    # знайдемо min/max у вікні для ліній піків
    ymin = min(b for (_, b) in pts)     # верхній пік (найменший y)
    ymax = max(b for (_, b) in pts)     # нижній пік (найбільший y)
    # горизонтальні пунктири на піках
    p.append(line(x0, ymin, x1, ymin, color=POS, sw=1.2, dash="4 4"))
    p.append(line(x0, ymax, x1, ymax, color=POS, sw=1.2, dash="4 4"))
    p.append(text(x0 + 6, ymin - 6, "max (найгучніший гребінь)", size=11, color=POS, anchor="start"))
    p.append(text(x0 + 6, ymax + 16, "min (найглибша западина)", size=11, color=POS, anchor="start"))

    # стрілка розмаху праворуч
    ax = x1 - 40
    p.append(arrow(ax, ymin, ax, ymax, color=FIELD, sw=2))
    p.append(arrow(ax, ymax, ax, ymin, color=FIELD, sw=2))
    p.append(text(ax + 12, (ymin + ymax) / 2, "розмах", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(ax + 12, (ymin + ymax) / 2 + 18, "= max − min", size=12, color=FIELD, anchor="start"))

    # підпис вікна знизу
    p.append(text((x0 + x1) / 2, bot_lim + 26,
                  "вікно ~50 мс: беремо купу відліків, тримаємо найменший і найбільший",
                  size=13, color=INK))
    p.append(text((x0 + x1) / 2, bot_lim + 46,
                  "розмах росте з гучністю — груба оцінка, НЕ децибели",
                  size=12, color=MUTED))

    return render(os.path.join(IMG, 'peak-to-peak.svg'), W, H, *p,
                  title="Аналоговий AO: розмах (peak-to-peak) у вікні як груба гучність")


if __name__ == '__main__':
    fig_rattle()
    fig_poll_vs_int()
    fig_p2p()
    print("OK: rattle-debounce.svg, poll-vs-interrupt.svg, peak-to-peak.svg")
