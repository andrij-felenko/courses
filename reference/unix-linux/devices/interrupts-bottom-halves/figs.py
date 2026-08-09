# -*- coding: utf-8 -*-
"""Фігури до теми «Переривання, softirq і робочі черги»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
GOLD     = "#b8860b"


# ── 1. Три маршрути однієї події ─────────────────────────────────────────────
def fig_three_routes():
    W, H = 1260, 620
    P = []
    X0, X1 = 210, 1190

    P.append(arrow(X0, 88, X1, 88, color=MUTED, sw=1.2))
    P.append(text(X0, 70, "сигнал від пристрою", size=12, color=MUTED, anchor="start"))
    P.append(text(X1, 70, "час", size=12, color=MUTED, anchor="end"))
    P.append(line(X0, 100, X0, 566, color=MUTED, sw=1, dash="5 5"))

    rows = [
        ("softirq",
         [(210, 340, "верхня\nполовина", RED_BG, POS),
          (340, 640, "softirq", WARM_BG, GOLD),
          (640, 1190, "перервана задача біжить далі", GREY_BG, MUTED)],
         "доробка просто на виході з переривання: той самий процесор і той самий стек — спати не можна"),
        ("потік переривання",
         [(210, 300, "верхня\nполовина", RED_BG, POS),
          (300, 430, "перемикання", GREY_BG, MUTED),
          (430, 790, "потік irq/42-sensor", GREEN_BG, FIELD),
          (790, 1190, "інші задачі", GREY_BG, MUTED)],
         "верхня половина лише будить свій потік; тіло обробника виконує задача, тож спати можна"),
        ("робоча черга",
         [(210, 300, "верхня\nполовина", RED_BG, POS),
          (300, 620, "хто завгодно", GREY_BG, MUTED),
          (620, 960, "kworker/0:2", GREEN_BG, FIELD),
          (960, 1190, "інші задачі", GREY_BG, MUTED)],
         "робочий елемент чекає в черзі пулу: виконає kworker, коли планувальник дасть йому час"),
    ]

    y = 190
    for name, bars, note in rows:
        P.append(text(195, y + 5, name, size=13, bold=True, anchor="end"))
        for x0, x1, label, bg, stroke in bars:
            P.append(fitbox(x0, y - 26, x1 - x0, 52, label, size=12,
                            fill=bg, stroke=stroke, sw=1.8))
        P.append(text(210, y + 50, note, size=12, color=MUTED, anchor="start"))
        y += 160

    render(os.path.join(OUT, "three-routes.svg"), W, H, *P,
           title="Три маршрути відкладеної роботи в часі")


# ── 2. Вектор softirq ────────────────────────────────────────────────────────
def fig_softirq_vector():
    W, H = 1180, 600
    P = []

    b, _, _ = textbox(300, 66, "raise_softirq(NET_RX_SOFTIRQ)", size=13,
                      fill=WARM_BG, stroke=GOLD, sw=1.8)
    P.append(b)
    b, _, _ = textbox(870, 66, "tasklet_schedule(&t)", size=13,
                      fill=WARM_BG, stroke=GOLD, sw=1.8)
    P.append(b)

    names = ["HI", "TIMER", "NET_TX", "NET_RX", "BLOCK",
             "IRQ_POLL", "TASKLET", "SCHED", "HRTIMER", "RCU"]
    CW, X0, YT, CH = 96, 100, 150, 58
    for i, nm in enumerate(names):
        on = nm in ("NET_RX", "TASKLET")
        P.append(fitbox(X0 + i * CW, YT, CW, CH, nm, size=11,
                        fill=(WARM_BG if on else GREY_BG),
                        stroke=(GOLD if on else MUTED), sw=(1.8 if on else 1.2)))
        P.append(text(X0 + i * CW + CW / 2, YT + CH + 20, str(i),
                      size=11, color=MUTED))

    P.append(arrow(300, 92, 436, YT - 6, color=GOLD))
    P.append(arrow(870, 92, 772, YT - 6, color=GOLD))

    P.append(text(100, 260, "поле відкладеного — своє на кожному процесорі; обхід іде за номерами",
                  size=12, color=MUTED, anchor="start"))

    P.append(arrow(400, YT + CH + 32, 400, 296, color=LINE))
    b, _, _ = textbox(400, 320, "irq_exit() → __do_softirq():\nпройти позначені біти від 0 до 9",
                      size=13, fill=GREY_BG, stroke=LINE, sw=1.8)
    P.append(b)

    P.append(arrow(772, YT + CH + 32, 900, 296, color=LINE))
    b, _, _ = textbox(920, 320, "список тасклетів\nцього процесора", size=13,
                      fill=GREY_BG, stroke=MUTED, sw=1.5)
    P.append(b)

    P.append(arrow(340, 356, 250, 424, color=LINE))
    P.append(arrow(470, 356, 640, 424, color=LINE))

    b, _, _ = textbox(240, 448, "усе встигли —\nназад у перервану задачу", size=12,
                      fill=GREEN_BG, stroke=FIELD, sw=1.8)
    P.append(b)
    b, _, _ = textbox(700, 448, "бюджет вичерпано:\n10 проходів або 2 мс", size=12,
                      fill=RED_BG, stroke=POS, sw=1.8)
    P.append(b)

    P.append(arrow(700, 492, 700, 534, color=POS))
    b, _, _ = textbox(700, 558, "ksoftirqd/N доробить як звичайна задача", size=12,
                      fill=GREY_BG, stroke=LINE, sw=1.5)
    P.append(b)

    render(os.path.join(OUT, "softirq-vector.svg"), W, H, *P,
           title="Поле відкладених softirq і хто його розгрібає")


# ── 3. Хто врешті платить за відкладену роботу ───────────────────────────────
def fig_who_pays():
    W, H = 1200, 520
    P = []

    cols = [(40, 250, "механізм"), (300, 300, "хто виконує"),
            (620, 160, "контекст"), (800, 360, "спати / чий пріоритет")]
    for x, w, head in cols:
        P.append(text(x, 52, head, size=13, bold=True, anchor="start"))
    P.append(line(30, 66, 1170, 66, color=MUTED, sw=1))

    rows = [
        ("softirq", "перервана задача,\nдалі ksoftirqd/N", "атомарний",
         "ні · спершу нічий, потім nice 0", WARM_BG, GOLD),
        ("тасклет (застарілий)", "те саме, через\nsoftirq TASKLET", "атомарний",
         "ні · те саме, плюс серіалізація", WARM_BG, GOLD),
        ("потік переривання", "irq/NN-‹пристрій›", "задача",
         "так · SCHED_FIFO 50, свій на пристрій", GREEN_BG, FIELD),
        ("робоча черга", "kworker/N:x", "задача",
         "так · nice 0, як усі інші задачі", GREEN_BG, FIELD),
    ]

    y = 92
    for mech, who, ctx, sleep, bg, stroke in rows:
        h = 82
        P.append(fitbox(40, y, 250, h, mech, size=13, bold=True,
                        fill=bg, stroke=stroke, sw=1.8))
        P.append(fitbox(300, y, 300, h, who, size=12.5, fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(620, y, 160, h, ctx, size=12.5, fill=GREY_BG, stroke=MUTED))
        P.append(mtext(800, y + h / 2 + 4, sleep, size=12.5, color=MUTED, anchor="start"))
        y += h + 22

    render(os.path.join(OUT, "who-pays.svg"), W, H, *P,
           title="Кожен маршрут врешті стає чиїмось процесорним часом")


# ── 4. Хроніка відкладеної роботи ───────────────────────────────────────────
def fig_bh_timeline():
    W, H = 1180, 900
    P = []

    P.append(text(40, 46, "коли · версія", size=13, bold=True, anchor="start"))
    P.append(text(330, 46, "що змінилося", size=13, bold=True, anchor="start"))
    P.append(line(30, 60, 1150, 60, color=MUTED, sw=1))

    rows = [
        ("до 2000\n2.0 — 2.2", "BH: 32 статичні гнізда,\nодне BH на всю машину", GREY_BG, MUTED),
        ("10 лютого 2000\n2.3.43", "softirq на кожне ядро; тасклети;\nстарі BH — шар сумісності згори", WARM_BG, GOLD),
        ("1 жовтня 2002\n2.5.40", "старі BH прибрано зовсім\n(Ingo Molnar)", GREEN_BG, FIELD),
        ("7 жовтня 2002\n2.5.41", "черги завдань → робочі черги\n(Ingo Molnar)", GREEN_BG, FIELD),
        ("10 червня 2009\n2.6.30", "потоки переривань із гілки PREEMPT_RT\n(Thomas Gleixner)", GREEN_BG, FIELD),
        ("20 жовтня 2010\n2.6.36", "спільний пул працівників, cmwq\n(Tejun Heo)", GREEN_BG, FIELD),
        ("жовтень 2020\n5.9", "у заголовку ядра: API тасклетів\nзастаріле", RED_BG, POS),
        ("12 травня 2024\n6.9", "робочі черги з ознакою WQ_BH —\nзаміна тасклетам", GREEN_BG, FIELD),
    ]

    y = 80
    for when, what, bg, stroke in rows:
        h = 86
        P.append(fitbox(40, y, 260, h, when, size=12.5, bold=True,
                        fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(330, y, 820, h, what, size=13, fill=bg, stroke=stroke, sw=1.8))
        y += h + 14

    render(os.path.join(OUT, "bh-timeline.svg"), W, H, *P,
           title="Хроніка поділу роботи переривання на дві половини")


# ── 5. Ланцюжок виконавців у драйвері з трьома нижніми половинами ────────────
def fig_driver_chain():
    W, H = 1340, 500
    P = []

    # Смуга «доки лінія замаскована»
    P.append(text(350, 56, "лінію замасковано, доки не повернеться потік (IRQF_ONESHOT)",
                  size=13, color=POS))
    P.append(line(70, 74, 630, 74, color=POS, sw=1.5, dash="6 4"))
    P.append(line(70, 74, 70, 86, color=POS, sw=1.5))
    P.append(line(630, 74, 630, 86, color=POS, sw=1.5))

    boxes = [
        (70,  "верхня половина\nапаратний контекст\nспати не можна", RED_BG, POS,
         "мітка часу, IRQ_WAKE_THREAD", "мікросекунди"),
        (370, "потік irq/NN-davach\nзадача, SCHED_FIFO 50\nспати можна", GREEN_BG, FIELD,
         "читає блок вибірок по шині", "сотні мікросекунд"),
        (690, "BH-робота, WQ_BH\nsoftirq на тому ж ядрі\nспати не можна", WARM_BG, GOLD,
         "перерахунок і штовх у кільце", "мікросекунди"),
        (990, "kworker\nзадача, nice 0\nспати можна", GREEN_BG, FIELD,
         "зводить статистику", "коли дасть планувальник"),
    ]
    for x, label, bg, stroke, what, when in boxes:
        P.append(fitbox(x, 100, 260, 86, label, size=12.5, fill=bg, stroke=stroke, sw=1.8))
        P.append(text(x + 130, 210, what, size=12))
        P.append(text(x + 130, 231, when, size=12, color=MUTED))

    P.append(arrow(332, 143, 366, 143))
    P.append(arrow(632, 143, 686, 143))
    P.append(arrow(952, 143, 986, 143))

    P.append(fitbox(70, 300, 300, 72, "read()\nспить на черзі очікування",
                    size=13, fill=GREY_BG, stroke=MUTED, sw=1.8))
    P.append(fitbox(560, 300, 340, 72, "кільце на 64 вибірки й пакет\nспін-замок",
                    size=13, fill=GREY_BG, stroke=MUTED, sw=1.8))
    P.append(fitbox(990, 300, 260, 72, "зведена статистика\nм'ютекс",
                    size=13, fill=GREY_BG, stroke=MUTED, sw=1.8))

    P.append(arrow(800, 250, 780, 296))
    P.append(arrow(1120, 250, 1120, 296))
    P.append(arrow(556, 336, 374, 336))
    P.append(text(465, 322, "одна вибірка на виклик", size=11, color=MUTED))
    P.append(arrow(904, 336, 984, 336, color=MUTED))
    P.append(text(944, 322, "пакет", size=11, color=MUTED))

    P.append(arrow(1250, 450, 70, 450, color=MUTED))
    P.append(text(660, 432,
                  "розбирання — проти течії: free_irq → cancel(BH-робота) → "
                  "cancel(статистика) → звільнення пам'яті", size=13, color=MUTED))

    render(os.path.join(OUT, "driver-chain.svg"), W, H, *P,
           title="Хто що виконує в драйвері з трьома нижніми половинами")


if __name__ == "__main__":
    fig_three_routes()
    fig_softirq_vector()
    fig_who_pays()
    fig_bh_timeline()
    fig_driver_chain()
    print("ok")
