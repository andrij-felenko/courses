# -*- coding: utf-8 -*-
"""Фігури до теми «Пріоритети, nice і реальночасові класи»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Ешелони класів планування ────────────────────────────────────────────
def classes_ladder():
    W, H = 900, 530
    f = []

    f.append(text(W / 2, 54, 'Ядро питає класи згори вниз і бере перший, у якого є готова задача',
                  size=14, color=MUTED))

    rows = [
        ('SCHED_DEADLINE',
         'договір: скільки часу і до якого моменту',
         'термін у мікросекундах'),
        ('SCHED_FIFO  ·  SCHED_RR',
         'безумовна перевага вищого пріоритету',
         'пріоритет 1 … 99'),
        ('SCHED_OTHER  ·  BATCH  ·  IDLE',
         'пропорційна частка процесора за вагами',
         'nice −20 … 19'),
    ]

    x0, bw, bh = 70, 480, 92
    rx0, rbw = 610, 230
    ys = [78, 208, 338]

    for i, (title_, sub, unit) in enumerate(rows):
        y = ys[i]
        f.append(rect(x0, y, bw, bh))
        f.append(mtext(x0 + bw / 2, y + 36, [title_], size=16, bold=True))
        f.append(mtext(x0 + bw / 2, y + 64, [sub], size=13, color=MUTED))
        f.append(fitbox(rx0, y + 24, rbw, 44, unit, size=13))
        if i < 2:
            f.append(arrow(x0 + bw / 2, y + bh + 2, x0 + bw / 2, ys[i + 1] - 4))
            f.append(text(x0 + bw / 2 + 16, y + bh + 24, 'якщо черга порожня',
                          size=12, color=MUTED, anchor='start'))

    note, _, _ = textbox(W / 2, 472,
                         'Між ешелонами немає зважування: одна задача з пріоритетом 1\n'
                         'витісняє будь-яку кількість звичайних задач із nice −20',
                         size=13, fill='#eef4ff', stroke=NEG)
    f.append(note)

    render(os.path.join(IMG, 'classes-ladder.svg'), W, H, *f,
           title='Три ешелони планування')


# ── 2. nice → вага → частка ─────────────────────────────────────────────────
def nice_weights():
    W, H = 860, 360
    f = []

    bx, bw, bh = 250, 540, 78

    def bar(y, label, items):
        f.append(text(bx - 16, y + bh / 2 + 5, label, size=14, anchor='end'))
        total = sum(w for _, w in items)
        cx = bx
        for nice_v, w in items:
            seg = bw * w / total
            share = 100.0 * w / total
            f.append(fitbox(cx, y, seg, bh,
                            'nice %d\nвага %d\n%.1f %%' % (nice_v, w, share),
                            size=13, pad=6))
            cx += seg

    bar(90, 'усі три однакові', [(0, 1024), (0, 1024), (0, 1024)])
    bar(210, 'третій став ввічливішим', [(0, 1024), (0, 1024), (5, 335)])

    f.append(text(W / 2, 320,
                  'частка = власна вага / сума ваг усіх готових задач',
                  size=14, color=NEG, bold=True))

    render(os.path.join(IMG, 'nice-weights.svg'), W, H, *f,
           title='Вага задає частку — але знаменник спільний')


# ── 3. Чесний клас проти SCHED_FIFO ─────────────────────────────────────────
def fifo_vs_fair():
    W, H = 880, 400
    f = []

    x0, x1 = 190, 830
    span = x1 - x0          # 100 мс
    px = span / 100.0

    def blocks(y, label, segs, fill):
        f.append(text(x0 - 16, y + 24, label, size=13, anchor='end'))
        for a, b in segs:
            f.append(rect(x0 + a * px, y, (b - a) * px, 34, fill=fill))

    f.append(text(W / 2, 62, 'R прокидається на 30-й і 66-й мілісекунді',
                  size=13, color=MUTED))

    blocks(84, 'R — SCHED_FIFO 50', [(30, 36), (66, 72)], '#fdecea')
    blocks(140, 'A — nice 0', [(0, 15), (36, 51), (72, 87)], '#eef4ff')
    blocks(196, 'B — nice 0', [(15, 30), (51, 66), (87, 100)], '#eef4ff')

    axis_y = 254
    f.append(line(x0, axis_y, x1, axis_y))
    for t in (0, 20, 40, 60, 80, 100):
        f.append(line(x0 + t * px, axis_y, x0 + t * px, axis_y + 7))
        lab = '100 мс' if t == 100 else str(t)
        f.append(text(x0 + t * px, axis_y + 26, lab, size=12, color=MUTED))

    note, _, _ = textbox(W / 2, 330,
                         'Звичайні задачі чергуються між собою, поки R спить;\n'
                         'щойно R готовий, він забирає процесор і тримає його, доки не засне',
                         size=13, fill='#f7f7f7')
    f.append(note)

    render(os.path.join(IMG, 'fifo-vs-fair.svg'), W, H, *f,
           title='Хто на процесорі: звичайні задачі та реальночасова')


# ── 4. Бюджет SCHED_DEADLINE ────────────────────────────────────────────────
def deadline_budget():
    W, H = 900, 430
    f = []

    x0, x1 = 150, 860
    P = (x1 - x0) / 3.0

    # смуга періодів
    for i in range(3):
        f.append(fitbox(x0 + i * P, 52, P, 30, 'період %d' % (i + 1),
                        size=13, fill='#f7f7f7', color=MUTED))

    # межі періодів
    for i in range(4):
        xb = x0 + i * P
        f.append(line(xb, 50, xb, 322, color=MUTED, sw=1.0, dash='5,5'))

    # смуга виконання
    run_y, run_h = 104, 34
    f.append(text(x0 - 16, run_y + 23, 'на процесорі', size=13, anchor='end'))
    runs = [(0.05, 0.35), (1.05, 1.42), (2.05, 2.35)]
    for a, b in runs:
        f.append(rect(x0 + a * P, run_y, (b - a) * P, run_h, fill='#eef4ff'))
    f.append(fitbox(x0 + 1.42 * P, run_y, 0.58 * P, run_h, 'спинено',
                    size=13, fill='#fdecea', stroke=POS, color=POS))

    # графік залишку бюджету
    top, bot = 190, 300
    f.append(text(x0 - 16, top + 5, 'бюджет', size=12, color=MUTED, anchor='end'))
    f.append(text(x0 - 16, bot + 5, '0', size=12, color=MUTED, anchor='end'))
    f.append(line(x0, bot, x1, bot, color=MUTED, sw=1.0))

    pts = [(0.00, 1.0), (0.05, 1.0), (0.35, 0.2), (1.00, 0.2),
           (1.00, 1.0), (1.05, 1.0), (1.42, 0.0), (2.00, 0.0),
           (2.00, 1.0), (2.05, 1.0), (2.35, 0.2), (3.00, 0.2)]
    for j in range(len(pts) - 1):
        ax, av = pts[j]
        bxp, bv = pts[j + 1]
        f.append(line(x0 + ax * P, bot - av * (bot - top),
                      x0 + bxp * P, bot - bv * (bot - top),
                      color=NEG, sw=2.4))

    note, _, _ = textbox(W / 2, 372,
                         'Бюджет поповнюється до повного runtime на початку кожного періоду;\n'
                         'вичерпаний бюджет спиняє задачу, і перевитрата лишається всередині її договору',
                         size=13, fill='#f7f7f7')
    f.append(note)

    render(os.path.join(IMG, 'deadline-budget.svg'), W, H, *f,
           title='Облік бюджету в SCHED_DEADLINE')


# ── 5. Абсолютний сон проти відносного (вставка proj-realtime-thread) ───────
def absolute_vs_relative():
    W, H = 940, 440
    f = []

    f.append(text(W / 2, 52,
                  'Цикл на 1 кГц: робота 250 мкс, пробудження запізнюється на 15–200 мкс',
                  size=13, color=MUTED))

    x0, x1 = 250, 890
    P = (x1 - x0) / 5.0          # 1000 мкс
    s = P / 1000.0               # px на мікросекунду
    work = 250
    delays = [20, 60, 15, 200, 30]

    for i in range(6):
        gx = x0 + i * P
        f.append(line(gx, 70, gx, 286, color=MUTED, sw=1.0, dash='5,5'))

    # ── ряд A: сон до абсолютного моменту
    ya, hb = 84, 34
    f.append(text(x0 - 16, ya + 22, 'сон до моменту t₀ + k·T', size=13, anchor='end'))
    for i, d in enumerate(delays):
        gx = x0 + i * P
        wx = gx + d * s
        f.append(line(gx, ya + hb / 2, max(wx, gx + 2), ya + hb / 2, color=POS, sw=3.0))
        f.append(rect(wx, ya, work * s, hb, fill='#eef4ff'))

    # ── ряд B: сон «ще T» після роботи
    yb = 170
    f.append(text(x0 - 16, yb + 22, 'сон «ще T» після роботи', size=13, anchor='end'))
    start = 0.0
    last_wake = 0.0
    for i, d in enumerate(delays):
        wake = start + d
        if wake * s > (x1 - x0):
            break
        f.append(rect(x0 + wake * s, yb, work * s, hb, fill='#fdecea'))
        last_wake = wake
        start = wake + work + 1000

    # ── скільки набігло
    ax, bx = x0 + 3 * P, x0 + last_wake * s
    f.append(line(ax, yb + hb + 18, bx, yb + hb + 18, color=POS, sw=1.8))
    f.append(text((ax + bx) / 2, yb + hb + 40, 'накопичений зсув ≈ 1 мс',
                  size=12, color=POS))

    # ── вісь часу
    f.append(line(x0, 286, x1, 286))
    for i in range(6):
        gx = x0 + i * P
        f.append(line(gx, 286, gx, 293))
        f.append(text(gx, 312, '5 мс' if i == 5 else str(i), size=12, color=MUTED))

    note, _, _ = textbox(W / 2, 375,
                         'Абсолютний сон повертає нас на сітку t₀ + k·T: запізнення однієї ітерації\n'
                         'не переходить у наступну. Відносний сон додає до періоду і роботу, і запізнення.',
                         size=13, fill='#f7f7f7')
    f.append(note)

    render(os.path.join(IMG, 'absolute-vs-relative.svg'), W, H, *f,
           title='Куди прив’язаний наступний момент пробудження')


# ── 6. Гістограма запізнень: хвіст важить більше за пік ─────────────────────
def latency_histogram():
    import math
    W, H = 920, 440
    f = []

    px0, px1 = 200, 840
    top, bot = 110, 300
    us_max = 180.0
    k = (px1 - px0) / us_max

    counts = [2900000, 600000, 80000, 12000, 4000, 1500, 700, 400, 260,
              170, 110, 70, 40, 25, 14, 8, 3, 1]
    logs = [math.log10(c + 1) for c in counts]
    top_log = max(logs)
    bw = (px1 - px0) / len(counts)

    f.append(mtext(105, 168, ['кількість', 'зразків', '(лог. шкала)'],
                   size=12, color=MUTED))

    f.append(line(px0, bot, px1, bot))
    for i, v in enumerate(logs):
        h = (bot - top) * v / top_log
        f.append(rect(px0 + i * bw + 2, bot - h, bw - 4, h, fill='#eef4ff', sw=1.0))

    for t in range(0, 181, 20):
        xt = px0 + t * k
        f.append(line(xt, bot, xt, bot + 7, color=MUTED, sw=1.0))
        f.append(text(xt, bot + 26, str(t), size=12, color=MUTED))
    f.append(text((px0 + px1) / 2, bot + 50, 'запізнення пробудження, мкс',
                  size=13, color=MUTED))

    marks = [(11.0, 'середнє 11 мкс', 72), (28.0, 'p99 = 28 мкс', 94),
             (174.0, 'максимум 174 мкс', 94)]
    for us, lab, ly in marks:
        xm = px0 + us * k
        f.append(line(xm, top, xm, bot, color=POS, sw=1.4, dash='4,4'))
        f.append(text(xm, ly, lab, size=13, color=POS, bold=True))

    note, _, _ = textbox(W / 2, 400,
                         'З 3 600 000 зразків майже всі лягли до 30 мкс,\n'
                         'а контур керування ламає той єдиний, що спізнився на 174.',
                         size=13, fill='#f7f7f7')
    f.append(note)

    render(os.path.join(IMG, 'latency-histogram.svg'), W, H, *f,
           title='Що показує гістограма запізнень')


# ── 7. П'ять означень важливості (вставка hist-nice-to-deadline) ────────────
def importance_eras():
    W, H = 1000, 610
    f = []

    c1, w1 = 30, 150
    c2, w2 = 195, 225
    c3, w3 = 435, 405
    c4, w4 = 855, 130

    f.append(text(c1 + w1 / 2, 40, 'коли', size=13, color=MUTED, bold=True))
    f.append(text(c2 + w2 / 2, 40, 'механізм', size=13, color=MUTED, bold=True))
    f.append(text(c3 + w3 / 2, 40, 'чим була «важливість»', size=13, color=MUTED, bold=True))
    f.append(text(c4 + w4 / 2, 40, 'одиниця', size=13, color=MUTED, bold=True))

    rows = [
        ('1973\nUnix V4…V7',
         'p_cpu/16 + PUSER + nice',
         'доданок до штрафу за спожитий час:\nnice зсуває всю криву згасання',
         'одиниці\nпріоритету'),
        ('1994–2003\nLinux 1.0 – 2.4',
         'goodness() і епохи',
         'квота тиків на епоху; недобрана половина\nпереходить у наступну',
         'тики\n(jiffies)'),
        ('2003–2007\nLinux 2.6.0 – 2.6.22',
         'O(1): два масиви',
         'довжина кванта плюс евристична добавка\nза те, скільки задача спала',
         'мілісекунди\n5 … 800'),
        ('2007–2023\nLinux 2.6.23 – 6.5',
         'CFS: віртуальний час',
         'вага, що задає частку процесора;\nважить лише різниця рівнів nice',
         'вага\n15 … 88761'),
        ('з 2023\nLinux 6.6+',
         'EEVDF: відставання й дедлайн',
         'і частка, і черговість: та сама вага\nще й стискає віртуальний дедлайн',
         'вага\n+ термін'),
    ]

    y = 60
    rh, gap = 88, 10
    for when, how, what, unit in rows:
        f.append(fitbox(c1, y, w1, rh, when, size=13, pad=6, fill='#f7f7f7'))
        f.append(fitbox(c2, y, w2, rh, how, size=13, pad=8))
        f.append(fitbox(c3, y, w3, rh, what, size=13, pad=8, fill='#eef4ff'))
        f.append(fitbox(c4, y, w4, rh, unit, size=13, pad=6, fill='#f7f7f7', color=MUTED))
        y += rh + gap

    f.append(text(W / 2, y + 30,
                  'Саме число nice лишалося тим самим −20 … 19 — мінялося те, '
                  'на що воно перетворюється всередині',
                  size=13, color=NEG))

    render(os.path.join(IMG, 'importance-eras.svg'), W, H, *f,
           title='П’ять означень важливості')


classes_ladder()
nice_weights()
fifo_vs_fair()
deadline_budget()
absolute_vs_relative()
latency_histogram()
importance_eras()
# ── Вставка math: ідеальна пряма й реальні сходинки ─────────────────────────
def math_fluid_lag():
    W, H = 920, 500
    f = []

    x0, x1 = 130, 770
    ybot, ytop = 380, 110
    px = (x1 - x0) / 24.0
    py = (ybot - ytop) / 18.0

    def X(t):
        return x0 + t * px

    def Y(s):
        return ybot - s * py

    f.append(text(x0, ytop - 26, 'отримано процесора, мс', size=12,
                  color=MUTED, anchor='start'))
    f.append(line(x0, ybot, x1 + 14, ybot))
    f.append(line(x0, ybot, x0, ytop - 12))

    for t in (0, 4, 8, 12, 16, 20, 24):
        f.append(line(X(t), ybot, X(t), ybot + 7, color=MUTED, sw=1.0))
        f.append(text(X(t), ybot + 26, str(t), size=12, color=MUTED))
    f.append(text(X(24) + 22, ybot + 26, 'реальний час, мс', size=12,
                  color=MUTED, anchor='start'))
    for s in (6, 12, 18):
        f.append(line(x0 - 6, Y(s), x0, Y(s), color=MUTED, sw=1.0))
        f.append(text(x0 - 12, Y(s) + 4, str(s), size=12, color=MUTED, anchor='end'))

    # ідеальні прямі: нахил = частка за вагами
    f.append(line(X(0), Y(0), X(24), Y(18), color=NEG, sw=1.6, dash='7,5'))
    f.append(line(X(0), Y(0), X(24), Y(6), color=POS, sw=1.6, dash='7,5'))

    def stair(pts, color):
        for i in range(len(pts) - 1):
            ax, av = pts[i]
            bx, bv = pts[i + 1]
            f.append(line(X(ax), Y(av), X(bx), Y(bv), color=color, sw=2.6))

    stair([(0, 0), (2, 0), (8, 6), (10, 6), (16, 12), (18, 12), (24, 18)], NEG)
    stair([(0, 0), (2, 2), (8, 2), (10, 4), (16, 4), (18, 6), (24, 6)], POS)

    f.append(text(X(24) + 16, Y(18) + 5, 'A · nice 0', size=13, color=NEG,
                  anchor='start', bold=True))
    f.append(text(X(24) + 16, Y(6) + 5, 'B · nice 5', size=13, color=POS,
                  anchor='start', bold=True))

    # розриви в момент t = 10
    f.append(line(X(10), Y(6), X(10), Y(7.5), color=NEG, sw=2.4))
    f.append(text(X(10) - 6, Y(7.5) - 10, 'лаг A', size=12, color=NEG, anchor='end'))
    f.append(line(X(10), Y(2.5), X(10), Y(4), color=POS, sw=2.4))
    f.append(text(X(10) + 8, Y(2.5) + 26, 'лаг B', size=12, color=POS, anchor='start'))

    leg, _, _ = textbox(300, 165,
                        'суцільне — скільки отримано насправді\n'
                        'пунктир — ідеальний поділ за вагами\n'
                        'розрив між ними — лаг',
                        size=12, fill='#ffffff')
    f.append(leg)

    note, _, _ = textbox(W / 2, 455,
                         'Хто відстає від своєї прямої (лаг > 0), той і біжить; хто вирвався вперед — чекає.\n'
                         'Сума лагів усіх задач у кожен момент дорівнює нулю: борг одного — це аванс іншого',
                         size=13, fill='#f7f7f7')
    f.append(note)

    render(os.path.join(IMG, 'math-fluid-lag.svg'), W, H, *f,
           title='Лаг як розрив між ідеальною прямою і сходинками')


# ── Вставка math: рівний крок ваг проти нерівного кроку квантів ─────────────
def math_nice_steps():
    W, H = 920, 430
    f = []

    weights = [88761, 71755, 56483, 46273, 36291,
               29154, 23254, 18705, 14949, 11916,
               9548, 7620, 6100, 4904, 3906,
               3121, 2501, 1991, 1586, 1277,
               1024, 820, 655, 526, 423,
               335, 272, 215, 172, 137,
               110, 87, 70, 56, 45,
               36, 29, 23, 18, 15]

    def slice_ms(n):
        prio = 120 + n
        return (140 - prio) * (20 if prio < 120 else 5)

    steps = list(range(-20, 19))
    w_ratio = [weights[n + 20] / float(weights[n + 21]) for n in steps]
    t_ratio = [slice_ms(n) / float(slice_ms(n + 1)) for n in steps]

    px0, px1 = 105, 855
    ybase, ytop = 350, 105
    top_val = 4.5
    bw = (px1 - px0) / float(len(steps))

    def Y(v):
        return ybase - (v - 1.0) / (top_val - 1.0) * (ybase - ytop)

    f.append(line(px0 - 10, ybase, px1 + 10, ybase))
    for v in (2, 3, 4):
        f.append(line(px0 - 6, Y(v), px1, Y(v), color='#e5e7eb', sw=1.0))
        f.append(text(px0 - 14, Y(v) + 4, '×%d' % v, size=12, color=MUTED, anchor='end'))
    f.append(text(px0 - 14, ybase + 4, '×1', size=12, color=MUTED, anchor='end'))

    for i in range(len(steps)):
        cx = px0 + i * bw
        f.append(rect(cx + 2, Y(t_ratio[i]), bw - 4, ybase - Y(t_ratio[i]),
                      fill='#fdecea', stroke=POS, sw=1.0, rx=2))

    for i in range(len(steps)):
        cx = px0 + i * bw + bw / 2
        if i:
            pcx = px0 + (i - 1) * bw + bw / 2
            f.append(line(pcx, Y(w_ratio[i - 1]), cx, Y(w_ratio[i]), color=NEG, sw=1.8))
        f.append(circle(cx, Y(w_ratio[i]), 3.2, fill=NEG, stroke=NEG, sw=1.0))

    for n in (-20, -10, 0, 10, 18):
        cx = px0 + (n + 20) * bw + bw / 2
        f.append(line(cx, ybase, cx, ybase + 7, color=MUTED, sw=1.0))
        f.append(text(cx, ybase + 26, ('%d' % n).replace('-', '−'),
                      size=12, color=MUTED))
    f.append(text((px0 + px1) / 2, ybase + 50,
                  'крок угору з рівня nice n на n+1', size=12, color=MUTED))

    spike = px0 + 19 * bw + bw / 2
    f.append(text(spike + 20, 175,
                  'O(1): крок −1 → 0 різав квант учетверо', size=13, color=POS,
                  anchor='start'))
    f.append(text(px1 - 6, Y(2.0) - 18,
                  'а крок 18 → 19 — рівно вдвічі', size=13, color=POS, anchor='end'))
    f.append(text(px0 + 10, Y(1.25) - 20,
                  'таблиця ваг: скрізь ×1.25', size=13, color=NEG, anchor='start'))

    render(os.path.join(IMG, 'math-nice-steps.svg'), W, H, *f,
           title='У скільки разів один крок nice міняє частку')


# ── Вставка math: ефект Дхалла ──────────────────────────────────────────────
def math_dhall():
    W, H = 980, 440
    f = []

    x0, x1 = 150, 830
    px = (x1 - x0) / 11.0

    def X(t):
        return x0 + t * px

    rows = [96, 146, 196, 246]
    rh = 34

    for i, y in enumerate(rows):
        f.append(text(x0 - 14, y + 22, 'ЦП %d' % i, size=13, anchor='end'))
        f.append(line(x0, y + rh + 8, x1, y + rh + 8, color='#e5e7eb', sw=1.0))
        f.append(rect(X(0), y, X(0.5) - X(0), rh, fill='#fdecea', stroke=POS, sw=1.2, rx=2))

    f.append(fitbox(X(0.5), rows[0], X(10.2) - X(0.5), rh,
                    'важка задача: 10 000 мкс роботи, дедлайн 10 200 мкс',
                    size=13, fill='#eef4ff', stroke=NEG))
    f.append(rect(X(10.2), rows[0], X(10.5) - X(10.2), rh,
                  fill='#fdecea', stroke=POS, sw=1.2, rx=2))

    f.append(text(X(1.2), 70, '4 легкі задачі: по 500 мкс, дедлайн 10 000 мкс',
                  size=13, color=POS, anchor='start'))
    f.append(arrow(X(1.15), 72, X(0.35), 92, color=POS))
    f.append(text(X(10.4), 78, 'дедлайни 10.0 і 10.2 мс', size=12,
                  color=MUTED, anchor='end'))

    for t in (10.0, 10.2):
        f.append(line(X(t), 88, X(t), 292, color=MUTED, sw=1.4, dash='5,5'))

    f.append(text(X(10.5) + 8, rows[0] + 22, 'запізно на 300 мкс',
                  size=12, color=POS, anchor='start'))

    axis_y = 292
    f.append(line(x0, axis_y, x1, axis_y))
    for t in (0, 2, 4, 6, 8, 10):
        f.append(line(X(t), axis_y, X(t), axis_y + 7, color=MUTED, sw=1.0))
        f.append(text(X(t), axis_y + 26, str(t), size=12, color=MUTED))
    f.append(text(x1, axis_y + 26, 'мс', size=12, color=MUTED, anchor='end'))

    note, _, _ = textbox(W / 2, 382,
                         'Σu = 4·0.05 + 0.98 = 1.18 при дозволених 0.95·4 = 3.80 — ядро приймає всіх;\n'
                         'легкі мають раніший дедлайн, займають усі чотири процесори, і важка стартує запізно',
                         size=13, fill='#f7f7f7', stroke=POS)
    f.append(note)

    render(os.path.join(IMG, 'math-dhall.svg'), W, H, *f,
           title='Ефект Дхалла: сума часток мала, дедлайн зірвано')


math_fluid_lag()
math_nice_steps()
math_dhall()
print('ok')
