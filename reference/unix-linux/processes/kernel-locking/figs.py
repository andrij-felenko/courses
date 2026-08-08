# -*- coding: utf-8 -*-
"""Фігури до теми «Замки в ядрі й атомарний контекст: де спати не можна»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"


# ── 1. Шари контексту ────────────────────────────────────────────────────────
def fig_context_layers():
    W, H = 1180, 640
    P = []

    P.append(text(40, 52, "поле лічильника preempt_count", size=13, bold=True, anchor="start"))
    P.append(text(430, 52, "контекст", size=13, bold=True, anchor="start"))
    P.append(text(760, 52, "що тут іще дозволено", size=13, bold=True, anchor="start"))
    P.append(line(30, 66, 1150, 66, color=MUTED, sw=1))

    rows = [
        ("усі поля нульові",
         "задача в ядрі",
         ["заснути · взяти м'ютекс", "виділити пам'ять з GFP_KERNEL", "взяти будь-який спін-замок"],
         GREEN_BG, FIELD),
        ("PREEMPT > 0",
         "під спін-замком\nабо preempt_disable()",
         ["взяти інший спін-замок", "GFP_ATOMIC", "атомарні операції"],
         WARM_BG, "#b8860b"),
        ("SOFTIRQ > 0",
         "нижня половина\n(softirq, тасклет, таймер)",
         ["те саме, що вище", "розбудити задачу, complete()"],
         WARM_BG, "#b8860b"),
        ("HARDIRQ > 0",
         "обробник апаратного\nпереривання",
         ["коротка робота з регістрами", "відкласти решту в робочу чергу"],
         RED_BG, POS),
        ("NMI > 0",
         "немасковане\nпереривання",
         ["лише атомарні операції", "жодного замка, крім спеціальних"],
         RED_BG, POS),
    ]

    y = 92
    for name, ctx, allowed, bg, stroke in rows:
        h = 84
        P.append(fitbox(30, y, 350, h, name, size=14, bold=True, fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(420, y, 300, h, ctx, size=14, fill=bg, stroke=stroke, sw=2))
        P.append(mtext(760, y + 26, allowed, size=12.5, color=MUTED, anchor="start", lh=1.45))
        y += h + 22

    # межа, за якою засинання зникає з переліку дозволеного
    P.append(text(400, 84, "спати можна", size=12.5, color=FIELD, bold=True))
    P.append(text(400, 192, "↓ нижче спати не можна ніде", size=12.5, color=POS, bold=True))

    return render(os.path.join(OUT, "context-layers.svg"), W, H, *P)


# ── 2. Той самий замок у задачі й у перериванні на одному ядрі процесора ─────
def fig_irq_selflock():
    W, H = 1160, 620
    P = []

    def column(x0, title, title_color, steps, verdict, verdict_bg, verdict_color):
        frag = [fitbox(x0, 34, 480, 46, title, size=15, bold=True,
                       fill=GREY_BG, stroke=title_color, sw=2)]
        y = 108
        for i, (who, what, color) in enumerate(steps):
            frag.append(fitbox(x0, y, 150, 56, who, size=12.5, fill="#ffffff",
                               stroke=MUTED, sw=1.2))
            frag.append(fitbox(x0 + 168, y, 312, 56, what, size=12.5,
                               fill=color, stroke=MUTED, sw=1.2))
            if i < len(steps) - 1:
                frag.append(arrow(x0 + 324, y + 58, x0 + 324, y + 84, color=MUTED, sw=1.6))
            y += 84
        frag.append(fitbox(x0, y + 6, 480, 58, verdict, size=13.5, bold=True,
                           fill=verdict_bg, stroke=verdict_color, sw=2, color=verdict_color))
        return frag

    P += column(
        30, "spin_lock() — переривання відкриті", POS,
        [("задача", "взяла замок, змінює список", GREY_BG),
         ("пристрій", "переривання на цьому ж ядрі", WARM_BG),
         ("обробник", "хоче той самий замок → крутиться", RED_BG),
         ("задача", "не має де добігти: процесор зайнятий", RED_BG)],
        "глухий кут на одному ядрі процесора", RED_BG, POS)

    P += column(
        650, "spin_lock_irqsave() — переривання закриті", FIELD,
        [("задача", "закрила переривання, взяла замок", GREY_BG),
         ("пристрій", "сигнал є, але його відкладено", GREY_BG),
         ("задача", "дописала список, звільнила замок,\nвідновила попередній стан", GREEN_BG),
         ("обробник", "аж тепер біжить і бере замок вільним", GREEN_BG)],
        "черга замість змагання", GREEN_BG, FIELD)

    return render(os.path.join(OUT, "irq-selflock.svg"), W, H, *P)


# ── 3. Два питання, з яких випливає примітив ────────────────────────────────
def fig_lock_choice():
    W, H = 1280, 600
    P = []

    cols = [
        ("суперник —\nінше ядро процесора", 400),
        ("суперник —\nнижня половина", 720),
        ("суперник —\nапаратне переривання", 1040),
    ]
    for label, cx in cols:
        P.append(fitbox(cx - 140, 34, 280, 58, label, size=13.5, bold=True,
                        fill=GREY_BG, stroke=MUTED))

    rows = [
        ("чекаю, не сплю\n(ділянка коротка)", 200,
         [("spin_lock()", GREEN_BG, FIELD),
          ("spin_lock_bh()", GREEN_BG, FIELD),
          ("spin_lock_irqsave()", GREEN_BG, FIELD)]),
        ("чекаю сплячи\n(ділянка довга)", 340,
         [("mutex_lock()", GREEN_BG, FIELD),
          ("mutex_lock()", GREEN_BG, FIELD),
          ("неможливо:\nобробник не задача", RED_BG, POS)]),
        ("не змагаюся зовсім", 480,
         [("atomic_t · RCU", GREEN_BG, FIELD),
          ("seqlock · per-CPU", GREEN_BG, FIELD),
          ("completion:\nсповіщення, не замок", WARM_BG, "#b8860b")]),
    ]

    for label, cy, cells in rows:
        P.append(fitbox(20, cy - 40, 250, 80, label, size=13, bold=True,
                        fill=GREY_BG, stroke=MUTED))
        for (name, bg, stroke), (_, cx) in zip(cells, cols):
            P.append(fitbox(cx - 140, cy - 36, 280, 72, name, size=13.5,
                            fill=bg, stroke=stroke, sw=2))

    P.append(text(20, 560,
                  "Клітинка — не варіант на вибір, а єдина законна відповідь "
                  "на пару питань зліва і згори.",
                  size=12.5, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, "lock-choice.svg"), W, H, *P)


# ── 4. Трафік когерентності на одну передачу замка (до вставки math-lock-scaling) ──
def fig_lock_traffic():
    W, H = 1200, 900
    P = []

    CORES_X = [420, 620, 820, 1020]
    CW, CH = 150, 46

    def core(cx, cy, name, bg=GREY_BG, stroke=MUTED, sw=1.5):
        return fitbox(cx - CW / 2, cy - CH / 2, CW, CH, name, size=13,
                      fill=bg, stroke=stroke, sw=sw)

    # ── смуга A: наївний TAS ────────────────────────────────────────────────
    P.append(fitbox(24, 90, 240, 116,
                    "наївний спін-замок\n≈ 2n передач\nплюс биття\nувесь час утримання",
                    size=13.5, bold=True, fill=RED_BG, stroke=POS, sw=2))
    P.append(fitbox(600, 78, 300, 46, "слово замка · один рядок кеша",
                    size=13, fill=WARM_BG, stroke="#b8860b", sw=2))
    for i, cx in enumerate(CORES_X):
        P.append(core(cx, 232, "ядро %d" % (i + 1)))
        P.append(arrow(cx, 232 - CH / 2 - 4, 640 + i * 40, 128, color=POS, sw=2))
    P.append(text(24, 288,
                  "Кожен претендент б'є атомарною RMW-інструкцією по тому самому рядку — "
                  "і поки замок вільний, і поки його тримають.",
                  size=13, color=MUTED, anchor="start"))

    # ── смуга B: квитковий ──────────────────────────────────────────────────
    P.append(fitbox(24, 400, 240, 116,
                    "квитковий\n≈ n передач\nпід час утримання —\nповна тиша",
                    size=13.5, bold=True, fill=WARM_BG, stroke="#b8860b", sw=2))
    P.append(fitbox(600, 388, 300, 46, "now_serving · один рядок кеша",
                    size=13, fill=WARM_BG, stroke="#b8860b", sw=2))
    P.append(core(CORES_X[0], 542, "власник", bg=GREEN_BG, stroke=FIELD, sw=2))
    P.append(arrow(CORES_X[0], 542 - CH / 2 - 4, 620, 438, color=POS, sw=2.2))
    for i, cx in enumerate(CORES_X[1:]):
        P.append(core(cx, 542, "ядро %d" % (i + 2)))
        P.append(arrow(760 + i * 40, 438, cx, 542 - CH / 2 - 4, color=NEG, sw=2))
    P.append(text(24, 598,
                  "Один запис власника анулює всі спільні копії; далі кожен із n−1 претендентів "
                  "перечитує рядок наново.",
                  size=13, color=MUTED, anchor="start"))

    # ── смуга C: черговий (MCS / qspinlock) ─────────────────────────────────
    P.append(fitbox(24, 700, 240, 116,
                    "черговий (MCS)\nрівно 2 передачі\nскільки б не було\nпретендентів",
                    size=13.5, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    for i, cx in enumerate(CORES_X):
        bg, st, sw = (GREEN_BG, FIELD, 2) if i == 0 else (GREY_BG, MUTED, 1.5)
        P.append(core(cx, 712, "власник" if i == 0 else "ядро %d" % (i + 1),
                      bg=bg, stroke=st, sw=sw))
        P.append(fitbox(cx - CW / 2, 786, CW, 42, "своя комірка", size=12,
                        fill=FILL, stroke=MUTED))
        P.append(line(cx, 712 + CH / 2, cx, 786, color=MUTED, sw=1.2, dash="4 4"))
    P.append(arrow(CORES_X[0] + CW / 2 + 4, 716, CORES_X[1] - CW / 2 - 6, 800,
                   color=POS, sw=2.4))
    P.append(text(24, 866,
                  "Звільняючи замок, власник пише одне слово в комірку наступника — "
                  "решта черги про це навіть не дізнається.",
                  size=13, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "lock-traffic.svg"), W, H, *P)


# ── 5. Пропускна здатність замка залежно від числа претендентів ─────────────
def fig_lock_throughput():
    W, H = 1140, 700
    P = []

    X0, X1 = 190, 960
    Y0, Y1 = 600, 130          # Y0 — нуль, Y1 — верх шкали
    NS = [4, 8, 16, 32, 64]
    YMAX = 8.0

    def px(i):
        return X0 + i * (X1 - X0) / (len(NS) - 1)

    def py(v):
        return Y0 - v / YMAX * (Y0 - Y1)

    # сітка й осі
    for v in (2, 4, 6, 8):
        P.append(line(X0, py(v), X1, py(v), color="#dcdfe4", sw=1))
        P.append(text(X0 - 16, py(v) + 5, "%d" % v, size=12.5,
                      color=MUTED, anchor="end"))
    P.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))
    P.append(line(X0, Y0, X0, Y1 - 14, color=INK, sw=1.6))
    for i, n in enumerate(NS):
        P.append(line(px(i), Y0, px(i), Y0 + 7, color=INK, sw=1.4))
        P.append(text(px(i), Y0 + 27, "%d" % n, size=13, color=INK))
    P.append(text(X0 - 16, py(0) + 5, "0", size=12.5, color=MUTED, anchor="end"))
    P.append(text((X0 + X1) / 2, Y0 + 60, "число ядер, що змагаються за замок",
                  size=13.5, color=INK))
    P.append(mtext(84, 300, ["мільйонів", "критичних", "ділянок", "за секунду"],
                   size=13, color=INK, anchor="middle"))

    # три криві моделі: цикл = L + N(n)·T,  L = 200, T = 100
    def rate(cycles):
        return 3000.0 / cycles          # 3 ГГц → мільйонів за секунду

    series = [
        ("MCS / qspinlock", FIELD, [rate(200 + 2 * 100) for _ in NS]),
        ("квитковий", NEG, [rate(200 + n * 100) for n in NS]),
        ("наївний", POS, [rate(200 + (2 * n + 2) * 100) for n in NS]),
    ]
    for _, col, vals in series:
        for i in range(len(NS) - 1):
            P.append(line(px(i), py(vals[i]), px(i + 1), py(vals[i + 1]),
                          color=col, sw=3))
        for i, v in enumerate(vals):
            P.append(circle(px(i), py(v), 5, fill=BG, stroke=col, sw=2.5))

    # легенда в порожньому правому верхньому куті
    P.append(rect(690, 196, 262, 132, fill=BG, stroke=MUTED, sw=1.2))
    for k, (name, col, _) in enumerate(series):
        yy = 232 + k * 38
        P.append(line(708, yy, 748, yy, color=col, sw=3.4))
        P.append(text(760, yy + 5, name, size=13.5, color=INK, anchor="start"))

    P.append(text(24, 664,
                  "Модель: критична ділянка L = 200 тактів, передача рядка кеша "
                  "T = 100 тактів, частота 3 ГГц.",
                  size=13, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "lock-throughput.svg"), W, H, *P)


# ── 6. Що читає кожен макрос перевірки контексту ─────────────────────────────
def fig_context_macros():
    W, H = 1280, 760
    P = []

    # межі полів слова preempt_count (зліва старші біти)
    SEGS = [
        (400, 520, "біт 31\nпрапорець"),
        (520, 700, "NMI\nбіти 20–23"),
        (700, 900, "HARDIRQ\nбіти 16–19"),
        (900, 1080, "SOFTIRQ\nбіти 8–15"),
        (1080, 1250, "PREEMPT\nбіти 0–7"),
    ]
    BAR_Y, BAR_H = 74, 62

    P.append(text(30, 60, "одне слово preempt_count", size=14, bold=True, anchor="start"))
    for x0, x1, name in SEGS:
        P.append(fitbox(x0, BAR_Y, x1 - x0, BAR_H, name, size=12.5,
                        fill=GREY_BG, stroke=MUTED))

    P.append(text(30, 176, "макрос", size=13, bold=True, anchor="start"))
    P.append(text(400, 176, "які поля читає", size=13, bold=True, anchor="start"))
    P.append(line(24, 190, 1256, 190, color=MUTED, sw=1))

    # (макрос, x0, x1, підпис усередині смуги, колір рамки, заливка)
    rows = [
        ("in_nmi()", 520, 700, "≠ 0", FIELD, GREEN_BG),
        ("in_hardirq()", 700, 900, "≠ 0", FIELD, GREEN_BG),
        ("in_serving_softirq()", 900, 1080, "лише найнижчий біт поля", FIELD, GREEN_BG),
        ("in_task()", 520, 1080, "усі три = 0  (у softirq — лише найнижчий біт)", FIELD, GREEN_BG),
        ("in_softirq()  застаріле", 900, 1080, "усе поле: не розрізняє «я в softirq» і «BH заборонені»",
         "#b8860b", WARM_BG),
        ("in_interrupt()  застаріле", 520, 1080, "змішує переривання із забороною нижніх половин",
         "#b8860b", WARM_BG),
        ("in_atomic()  ненадійне", 520, 1250, "усе слово ≠ 0 — і цього замало", POS, RED_BG),
        ("preemptible()", 520, 1250, "усе слово = 0  І  переривання відкриті", FIELD, GREEN_BG),
    ]

    y = 218
    for name, x0, x1, note, stroke, bg in rows:
        P.append(fitbox(24, y, 360, 46, name, size=13, bold=True,
                        fill=FILL, stroke=MUTED))
        P.append(fitbox(x0, y, x1 - x0, 46, note, size=12,
                        fill=bg, stroke=stroke, sw=2))
        y += 60

    # регістр прапорців — поза словом
    FY = y + 30
    P.append(fitbox(400, FY, 500, 58,
                    "регістр прапорців процесора: чи закриті переривання",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2))
    P.append(fitbox(940, FY, 310, 58, "irqs_disabled()", size=14, bold=True,
                    fill=FILL, stroke=NEG, sw=2))
    P.append(line(400, FY + 29, 380, FY + 29, color=NEG, sw=1.5, dash="5 4"))
    P.append(text(24, FY + 34, "поза лічильником", size=13, bold=True, anchor="start"))

    P.append(text(24, FY + 110,
                  "Червона смуга — головна пастка: in_atomic() дивиться лише в це слово, "
                  "а закриті переривання живуть у регістрі прапорців і в нього не потрапляють.",
                  size=13, color=MUTED, anchor="start"))
    P.append(text(24, FY + 134,
                  "Плюс сам лічильник ведеться тільки з CONFIG_PREEMPT_COUNT — без нього "
                  "взятий spin_lock() не додає туди нічого.",
                  size=13, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "context-macros.svg"), W, H, *P)


# ── 7. Граф lockdep і час (вставка proj-lockdep-lab) ─────────────────────────
def fig_lockdep_graph_time():
    W, H = 1100, 600
    P = []

    # ── Панель А: вісь часу ─────────────────────────────────────────────
    P.append(text(40, 78, "Що бачить годинник", size=15, bold=True, anchor="start"))

    P.append(text(40, 146, "lab_ab", size=14, bold=True, anchor="start"))
    P.append(fitbox(200, 118, 300, 44, "тримає lock_a, бере lock_b",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(text(40, 236, "lab_ba", size=14, bold=True, anchor="start"))
    P.append(fitbox(620, 208, 300, 44, "тримає lock_b, бере lock_a",
                    size=13, fill=RED_BG, stroke=POS, sw=2))

    # межі паузи
    P.append(line(500, 112, 500, 285, color=MUTED, sw=1.2, dash="5 4"))
    P.append(line(620, 202, 620, 285, color=MUTED, sw=1.2, dash="5 4"))
    P.append(text(560, 270, "пауза 0.5 с", size=12, color=MUTED))

    P.append(arrow(200, 285, 1010, 285, color=MUTED, sw=1.6))
    P.append(text(1022, 290, "час", size=13, color=MUTED, anchor="start"))

    # ── Панель Б: граф класів ───────────────────────────────────────────
    P.append(text(40, 378, "Що бачить lockdep", size=15, bold=True, anchor="start"))

    P.append(fitbox(300, 430, 150, 52, "lock_a", size=17, bold=True,
                    fill=GREY_BG, stroke=LINE, sw=2))
    P.append(fitbox(700, 430, 150, 52, "lock_b", size=17, bold=True,
                    fill=GREY_BG, stroke=LINE, sw=2))

    P.append(arrow(460, 444, 690, 444, color=FIELD, sw=2.2))
    P.append(text(575, 412, "ребро від lab_ab: «взяв b, тримаючи a»",
                  size=13, color=FIELD))

    P.append(arrow(690, 468, 460, 468, color=POS, sw=2.2))
    P.append(text(575, 505, "нове ребро від lab_ba — і це замикає цикл",
                  size=13, color=POS))

    P.append(text(40, 556,
                  "Перевірка ставить одне питання: чи досяжний lock_a із lock_b "
                  "по вже наявних ребрах. Час у це питання не входить.",
                  size=13, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "lockdep-graph-time.svg"), W, H, *P)


# ── 8. Чотири символи стану класу (вставка proj-lockdep-lab) ─────────────────
def fig_lockdep_usage_bits():
    W, H = 1180, 580
    P = []

    LX, LW = 40, 290                      # стовпчик підпису рядка
    CX = [360, 522, 684, 846]             # чотири стовпчики символів
    CW = 150
    RX, RW = 1010, 150                    # стовпчик «як у звіті»

    heads = ["апаратні\nпереривання", "апаратні,\nна читання",
             "нижні\nполовини", "нижні,\nна читання"]

    P.append(fitbox(LX, 90, LW, 60, "історія класу", size=13, bold=True,
                    fill=BG, stroke=MUTED, sw=1.2))
    for x, h in zip(CX, heads):
        P.append(fitbox(x, 90, CW, 60, h, size=12, fill=BG, stroke=MUTED, sw=1.2))
    P.append(fitbox(RX, 90, RW, 60, "як стоїть\nу звіті", size=13, bold=True,
                    fill=BG, stroke=MUTED, sw=1.2))

    rows = [
        (165, "поки замок бере\nлише задача",
         ["+", ".", "+", "."], "{+.+.}", None),
        (240, "тасклет узяв\nтой самий замок",
         ["+", ".", "?", "."], "{+.?.}", (2, RED_BG, POS)),
        (315, "після spin_lock_bh()\nу задачі",
         ["+", ".", "-", "."], "{+.-.}", (2, GREEN_BG, FIELD)),
    ]

    for y, label, chars, shown, mark in rows:
        P.append(fitbox(LX, y, LW, 60, label, size=13, fill=FILL, stroke=LINE, sw=1.5))
        for i, (x, c) in enumerate(zip(CX, chars)):
            fill, stroke, col = BG, MUTED, INK
            if mark and mark[0] == i:
                fill, stroke, col = mark[1], mark[2], mark[2]
            P.append(fitbox(x, y, CW, 60, c, size=30, bold=True,
                            fill=fill, stroke=stroke, sw=2, color=col))
        P.append(fitbox(RX, y, RW, 60, shown, size=17, bold=True,
                        fill=FILL, stroke=LINE, sw=1.5))

    P.append(text(40, 428, "Що означає символ:", size=14, bold=True, anchor="start"))
    legend = [
        "«.»   брали при закритих перериваннях і поза контекстом переривання",
        "«+»   брали при відкритих перериваннях",
        "«-»   брали в контексті переривання",
        "«?»   і те, і те — саме це поєднання й неможливе",
    ]
    for i, ln in enumerate(legend):
        P.append(text(60, 460 + i * 27, ln, size=14, anchor="start"))

    return render(os.path.join(OUT, "lockdep-usage-bits.svg"), W, H, *P)


if __name__ == "__main__":
    for f in (fig_context_layers, fig_irq_selflock, fig_lock_choice,
              fig_lock_traffic, fig_lock_throughput, fig_context_macros,
              fig_lockdep_graph_time, fig_lockdep_usage_bits):
        print(f())
