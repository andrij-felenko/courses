# -*- coding: utf-8 -*-
"""Фігури до теми «Гілка реального часу PREEMPT_RT»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY = "#e9ecef"
GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
ORANGE_BG = "#fdf1e0"
ORANGE = "#c07a1e"
BLUE_BG = "#eaf0fd"


# ── 1. Шкала пріоритетів: хто на ній є, а хто збоку ─────────────────────────
def fig_priority_order():
    W, H = 1140, 620
    P = []

    P.append(text(300, 60, "звичайне ядро", size=16, bold=True))
    P.append(text(860, 60, "PREEMPT_RT", size=16, bold=True))

    # ── ліва шкала ─────────────────────────────────────────────────────────
    P.append(rect(60, 100, 300, 330, fill="#ffffff", stroke=MUTED, sw=1.2))
    P.append(text(210, 92, "шкала пріоритетів", size=12, color=MUTED))
    left_rows = [
        ("ваша задача · FIFO 99", GREEN_BG, FIELD),
        ("інша RT-задача · FIFO 50", BLUE_BG, NEG),
        ("звичайні задачі", GREY, MUTED),
    ]
    for i, (s, bg, st) in enumerate(left_rows):
        P.append(fitbox(80, 125 + i * 100, 260, 52, s, size=13, fill=bg, stroke=st))
    P.append(text(210, 452, "вище — раніше на процесор", size=12, color=MUTED))

    # ── те, що поза шкалою ─────────────────────────────────────────────────
    outs = ["обробник переривання", "softirq", "ділянка під спін-замком"]
    for i, s in enumerate(outs):
        cy = 151 + i * 100
        P.append(fitbox(430, cy - 26, 250, 52, s, size=13, fill=RED_BG, stroke=POS))
        P.append(arrow(428, cy, 366, cy, color=POS))
    P.append(mtext(555, 452, ["поза шкалою: забирають процесор,", "не проходячи через вибір"],
                   size=12, color=POS, lh=1.35))

    # ── права шкала ────────────────────────────────────────────────────────
    P.append(rect(700, 100, 380, 400, fill="#ffffff", stroke=MUTED, sw=1.2))
    P.append(text(890, 92, "шкала пріоритетів", size=12, color=MUTED))
    right_rows = [
        ("потік irq/24-eth0 · FIFO 60", BLUE_BG, NEG),
        ("ваша задача · FIFO 55", GREEN_BG, FIELD),
        ("потік irq/31-nvme0 · FIFO 45", BLUE_BG, NEG),
        ("ksoftirqd · звичайний клас", GREY, MUTED),
    ]
    for i, (s, bg, st) in enumerate(right_rows):
        P.append(fitbox(720, 122 + i * 94, 340, 52, s, size=13, fill=bg, stroke=st))
    P.append(mtext(890, 528, ["ділянка під замком лишилася витісненною:",
                              "її вага — це пріоритет власника замка"],
                   size=12, color=MUTED, lh=1.35))
    return render(os.path.join(OUT, "priority-order.svg"), W, H, *P)


# ── 2. Спін-замок проти сплячого: одне ядро процесора, дві задачі ───────────
def fig_sleeping_lock():
    W, H = 1120, 620
    P = []

    t0, t1, t2, t3, te = 250.0, 400.0, 620.0, 770.0, 1070.0
    lane_h = 44

    def bar(x1, x2, y, s, bg, st, color=INK):
        return fitbox(x1, y, x2 - x1, lane_h, s, size=12, fill=bg, stroke=st, color=color)

    def moment(x, y_top, y_bot, s):
        out = line(x, y_top, x, y_bot, color=MUTED, sw=1.2, dash="5 4")
        out += text(x, y_top - 10, s, size=12, color=MUTED)
        return out

    # ── рядок 1: звичайне ядро ─────────────────────────────────────────────
    yA, yR = 130.0, 190.0
    P.append(text(60, 112, "звичайне ядро", size=15, bold=True, anchor="start"))
    P.append(text(60, yA + 28, "A (низький)", size=12, anchor="start"))
    P.append(text(60, yR + 28, "R (високий)", size=12, anchor="start"))
    P.append(bar(t0, t3, yA, "тримає спін-замок · витіснення заборонене", RED_BG, POS))
    P.append(bar(t1, t3, yR, "чекає", GREY, MUTED, color=MUTED))
    P.append(bar(t3, te, yR, "біжить", GREEN_BG, FIELD, color=FIELD))
    P.append(moment(t1, yA - 22, yR + lane_h + 6, "R прокинулася"))
    P.append(line(t1, yR + lane_h + 24, t3, yR + lane_h + 24, color=POS, sw=1.6))
    P.append(text((t1 + t3) / 2, yR + lane_h + 44,
                  "затримка = решта ділянки під замком", size=12, color=POS))

    # ── рядок 2: PREEMPT_RT ────────────────────────────────────────────────
    yA2, yR2 = 380.0, 440.0
    P.append(text(60, 362, "PREEMPT_RT", size=15, bold=True, anchor="start"))
    P.append(text(60, yA2 + 28, "A (низький)", size=12, anchor="start"))
    P.append(text(60, yR2 + 28, "R (високий)", size=12, anchor="start"))
    P.append(bar(t0, t1, yA2, "тримає сплячий замок", ORANGE_BG, ORANGE))
    P.append(bar(t2, t3, yA2, "біжить із пріоритетом R", ORANGE_BG, ORANGE))
    P.append(bar(t1, t2, yR2, "біжить одразу", GREEN_BG, FIELD, color=FIELD))
    P.append(bar(t2, t3, yR2, "спить на замку", GREY, MUTED, color=MUTED))
    P.append(bar(t3, te, yR2, "біжить", GREEN_BG, FIELD, color=FIELD))
    P.append(moment(t1, yA2 - 22, yR2 + lane_h + 6, "R прокинулася"))
    P.append(text(t1 + 6, yA2 - 40, "A витіснена — і це вже не катастрофа",
                  size=12, color=MUTED, anchor="start"))
    P.append(text((t2 + t3) / 2, yR2 + lane_h + 30,
                  "R попросила той самий замок → власникові піднято пріоритет",
                  size=12, color=ORANGE))
    P.append(text(t3 + 10, yR2 + lane_h + 30, "замок звільнено", size=12, color=MUTED,
                  anchor="start"))

    P.append(line(t0 - 30, 560, te, 560, color=MUTED, sw=1))
    P.append(text(t0 - 30, 580, "час →", size=12, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, "sleeping-lock.svg"), W, H, *P)


# ── 3. Дві гарантії заборони й те, що з них лишилося ────────────────────────
def fig_migrate_disable():
    W, H = 1120, 560
    P = []

    # ── ліворуч: звичайне ядро ─────────────────────────────────────────────
    P.append(text(270, 60, "звичайне ядро", size=16, bold=True))
    P.append(fitbox(120, 90, 300, 54, "spin_lock()", size=14, bold=True, fill=BLUE_BG, stroke=NEG))
    P.append(arrow(200, 148, 200, 196, color=NEG))
    P.append(arrow(340, 148, 340, 196, color=NEG))
    P.append(fitbox(60, 200, 200, 76, "не перемикати\nзадачу", size=13, fill=GREEN_BG, stroke=FIELD))
    P.append(fitbox(280, 200, 200, 76, "не переносити\nна інше ядро", size=13, fill=GREEN_BG, stroke=FIELD))
    P.append(mtext(270, 306, ["обидві гарантії дає",
                              "одна дія — заборона витіснення"],
                   size=12, color=MUTED, lh=1.35))

    # ── праворуч: PREEMPT_RT ───────────────────────────────────────────────
    P.append(text(850, 60, "PREEMPT_RT", size=16, bold=True))
    P.append(fitbox(700, 90, 300, 54, "spin_lock()", size=14, bold=True, fill=BLUE_BG, stroke=NEG))
    P.append(arrow(780, 148, 780, 196, color=MUTED))
    P.append(arrow(920, 148, 920, 196, color=NEG))
    P.append(fitbox(640, 200, 200, 76, "перемикати\nМОЖНА", size=13, fill=GREY, stroke=MUTED, color=MUTED))
    P.append(fitbox(860, 200, 200, 76, "не переносити:\nmigrate_disable()", size=13,
                    fill=GREEN_BG, stroke=FIELD))
    P.append(mtext(850, 306, ["сплячий замок віддає першу гарантію,",
                              "тож другу довелося назвати окремо"],
                   size=12, color=MUTED, lh=1.35))

    # ── нижня стрічка: задача прокидається на тому самому ядрі ─────────────
    P.append(line(60, 350, 1060, 350, color=MUTED, sw=1))
    P.append(text(60, 384, "ядро 0", size=13, anchor="start"))
    P.append(text(60, 452, "ядро 1", size=13, anchor="start"))
    P.append(fitbox(180, 366, 190, 40, "A під замком", size=12, fill=ORANGE_BG, stroke=ORANGE))
    P.append(fitbox(390, 366, 190, 40, "B (важливіша)", size=12, fill=GREEN_BG, stroke=FIELD))
    P.append(fitbox(600, 366, 220, 40, "A доробляє тут само", size=12, fill=ORANGE_BG, stroke=ORANGE))
    P.append(fitbox(390, 434, 190, 40, "сюди — не можна", size=12, fill=GREY, stroke=MUTED, color=MUTED))
    P.append(line(430, 412, 540, 466, color=POS, sw=2))
    P.append(line(540, 412, 430, 466, color=POS, sw=2))
    P.append(text(860, 460, "вказівник на дані свого", size=12, color=MUTED, anchor="start"))
    P.append(text(860, 480, "ядра лишається чинним", size=12, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, "migrate-disable.svg"), W, H, *P)


# ── 4. Гарячий шлях і передача накопиченого (до вставки proj) ──────────────
def fig_hot_path_handoff():
    W, H = 1180, 660
    P = []

    P.append(text(230, 66, "гарячий потік · FIFO 55", size=15, bold=True))
    P.append(text(950, 66, "потік звіту · звичайний клас", size=15, bold=True))

    # ── ліва колонка: що робить гарячий потік щотакту ──────────────────────
    P.append(rect(60, 90, 340, 250, fill="#ffffff", stroke=FIELD, sw=1.4))
    P.append(text(230, 116, "щотакту, 1 мс", size=12, color=MUTED))
    steps = [
        "clock_nanosleep(ABSTIME)",
        "clock_gettime → запізнення",
        "hist[запізнення]++",
        "крок керування",
    ]
    for i, s in enumerate(steps):
        P.append(fitbox(80, 132 + i * 48, 300, 38, s, size=12, fill=GREEN_BG, stroke=FIELD))

    # ── заборонене ─────────────────────────────────────────────────────────
    P.append(rect(60, 376, 340, 176, fill="#ffffff", stroke=POS, sw=1.4))
    P.append(text(230, 402, "сюди не заходить ніколи", size=12, color=POS))
    banned = ["malloc / free", "printf і будь-який вивід", "замок без PRIO_INHERIT"]
    for i, s in enumerate(banned):
        P.append(fitbox(80, 414 + i * 46, 300, 36, s, size=12, fill=RED_BG, stroke=POS))

    # ── два кошики посередині ──────────────────────────────────────────────
    P.append(fitbox(500, 150, 190, 62, "кошик A\n(набирається)", size=12,
                    fill=GREEN_BG, stroke=FIELD))
    P.append(fitbox(500, 300, 190, 62, "кошик B\n(порожній)", size=12,
                    fill=GREY, stroke=MUTED, color=MUTED))
    P.append(arrow(402, 181, 496, 181, color=FIELD))

    # ── замок ──────────────────────────────────────────────────────────────
    P.append(rect(460, 402, 270, 118, fill=ORANGE_BG, stroke=ORANGE, sw=1.6))
    P.append(mtext(595, 432, ["раз на секунду:", "обмін вказівниками під m"],
                   size=12, color=ORANGE, lh=1.35))
    P.append(mtext(595, 478, ["m — PTHREAD_PRIO_INHERIT", "утримання ≈ 200 нс"],
                   size=12, color=INK, lh=1.35))
    P.append(arrow(595, 366, 595, 398, color=ORANGE))

    # ── права колонка ──────────────────────────────────────────────────────
    P.append(rect(790, 90, 330, 250, fill="#ffffff", stroke=MUTED, sw=1.4))
    P.append(text(955, 116, "раз на секунду", size=12, color=MUTED))
    rep = [
        "забрати повний кошик",
        "порахувати перцентилі",
        "надрукувати",
        "почистити й повернути",
    ]
    for i, s in enumerate(rep):
        P.append(fitbox(810, 132 + i * 48, 290, 38, s, size=12, fill=BLUE_BG, stroke=NEG))
    P.append(arrow(734, 460, 806, 460, color=NEG))
    P.append(mtext(955, 420, ["друк і чищення — уже", "поза замком"],
                   size=12, color=MUTED, lh=1.35))

    P.append(mtext(590, 596, ["Гарячий потік торкається замка раз на тисячу тактів;",
                              "решту часу він не має жодної спільної з кимось структури."],
                   size=13, color=MUTED, lh=1.4))
    return render(os.path.join(OUT, "hot-path-handoff.svg"), W, H, *P)


# ── 5. Запобіжник реальночасових класів ────────────────────────────────────
def fig_rt_throttle():
    W, H = 1160, 470
    P = []

    x0, x1, y = 90, 1090, 210
    span_ms = 2000.0

    def px(ms):
        return x0 + (x1 - x0) * ms / span_ms

    # ── дозволені й заборонені смуги ───────────────────────────────────────
    for start in (0.0, 1000.0):
        P.append(rect(px(start), y - 34, px(start + 950) - px(start), 68,
                      fill=GREEN_BG, stroke=FIELD, sw=1.2, rx=0))
        P.append(rect(px(start + 950), y - 34, px(start + 1000) - px(start + 950), 68,
                      fill=RED_BG, stroke=POS, sw=1.2, rx=0))

    P.append(text(px(475), y + 6, "реальночасовим класам дозволено · 950 мс",
                  size=13, color=FIELD))
    P.append(text(px(1475), y + 6, "дозволено · 950 мс", size=13, color=FIELD))

    # ── шкала часу ─────────────────────────────────────────────────────────
    P.append(line(x0, y + 62, x1, y + 62, color=MUTED, sw=1.2))
    for ms in (0, 950, 1000, 1950, 2000):
        P.append(line(px(ms), y + 56, px(ms), y + 68, color=MUTED, sw=1.2))
    P.append(text(px(0), y + 90, "0", size=12, color=MUTED))
    P.append(text(px(950) - 26, y + 90, "950 мс", size=12, color=MUTED))
    P.append(text(px(1000) + 34, y + 90, "1000 мс", size=12, color=MUTED))
    P.append(text(px(1975), y + 90, "2000 мс", size=12, color=MUTED))

    # ── пояснення до червоної смуги ────────────────────────────────────────
    P.append(mtext(px(975), y - 96, ["примусова пауза 50 мс:", "жодна RT-задача не біжить"],
                   size=13, color=POS, lh=1.4))
    P.append(arrow(px(975), y - 66, px(975), y - 40, color=POS))

    # ── пробудження, що потрапило під паузу ────────────────────────────────
    P.append(arrow(px(970), y + 150, px(970), y + 74, color=POS, sw=2))
    P.append(mtext(px(880), y + 186, ["такт замовлено", "на 970 мс"],
                   size=12, color=INK, lh=1.35))
    P.append(arrow(px(1000), y + 150, px(1000), y + 74, color=NEG, sw=2))
    P.append(mtext(px(1130), y + 186, ["виконано о 1000 мс:", "запізнення 30 мс"],
                   size=12, color=NEG, lh=1.35))

    P.append(mtext(580, y + 244, ["Бюджет спільний на всі реальночасові задачі системи —",
                                  "з'їсти його може сусід, а заплатить той, чий такт випав на паузу."],
                   size=13, color=MUTED, lh=1.4))
    return render(os.path.join(OUT, "rt-throttle.svg"), W, H, *P)


# ── Три категорії замків і напрямок вкладення ───────────────────────────────
def fig_lock_categories():
    W, H = 1160, 640
    P = []

    P.append(text(320, 66, "звичайне ядро", size=16, bold=True))
    P.append(text(880, 66, "PREEMPT_RT", size=16, bold=True))

    # ── верхня смуга: можна спати ──────────────────────────────────────────
    P.append(text(60, 100, "можна заснути, можна виділяти пам'ять",
                  size=12, color=MUTED, anchor="start"))
    P.append(rect(60, 112, 1040, 200, fill="#ffffff", stroke=FIELD, sw=1.2))
    P.append(fitbox(110, 150, 380, 120,
                    "mutex · rt_mutex\nsemaphore · rw_semaphore\nww_mutex",
                    size=13, fill=GREY, stroke=MUTED))
    P.append(fitbox(670, 132, 390, 80,
                    "mutex · rt_mutex\nsemaphore · rw_semaphore · ww_mutex",
                    size=13, fill=GREY, stroke=MUTED))
    P.append(fitbox(670, 226, 390, 70,
                    "spinlock_t · rwlock_t\nlocal_lock_t",
                    size=13, fill=ORANGE_BG, stroke=ORANGE))

    # ── нижня смуга: справді атомарний контекст ────────────────────────────
    P.append(text(60, 370, "спати не можна: ні сну, ні kmalloc, ні spin_lock",
                  size=12, color=MUTED, anchor="start"))
    P.append(rect(60, 382, 1040, 170, fill="#ffffff", stroke=POS, sw=1.2))
    P.append(fitbox(110, 400, 380, 62, "raw_spinlock_t · біт-спінлок",
                    size=13, fill=GREY, stroke=MUTED))
    P.append(fitbox(110, 474, 380, 62, "spinlock_t · rwlock_t · local_lock_t",
                    size=13, fill=ORANGE_BG, stroke=ORANGE))
    P.append(fitbox(670, 436, 390, 62, "raw_spinlock_t · біт-спінлок",
                    size=13, fill=GREY, stroke=MUTED))

    P.append(arrow(500, 505, 660, 265, color=ORANGE))
    P.append(text(560, 300, "переїхали під RT", size=12, color=ORANGE))

    P.append(mtext(580, 590,
                   ["вкладати можна лише згори вниз: під сплячим замком — будь-який,",
                    "під raw_spinlock_t — тільки raw_spinlock_t і біт-спінлок"],
                   size=12, color=MUTED, lh=1.35))
    return render(os.path.join(OUT, "lock-categories.svg"), W, H, *P)


if __name__ == "__main__":
    for f in (fig_priority_order, fig_sleeping_lock, fig_migrate_disable,
              fig_hot_path_handoff, fig_rt_throttle, fig_lock_categories):
        print(f())
