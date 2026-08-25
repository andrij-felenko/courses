# -*- coding: utf-8 -*-
"""Фігури до теми «stop_machine: зупинити всю машину, щоб змінити недоторканне»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
BLUE_BG = "#eaf0fd"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"


# ── 1. Рандеву: чотири стани й вікно тиші ───────────────────────────────────
def fig_rendezvous():
    W, H = 1340, 540
    P = []

    x0, xe = 275, 1300
    b1, b2, b3 = 620, 815, 1095          # межі станів
    zones = [
        (x0, b1, "MULTI_STOP_PREPARE\nусі зійшлися в циклі"),
        (b1, b2, "MULTI_STOP_DISABLE_IRQ\nпереривання геть"),
        (b2, b3, "MULTI_STOP_RUN\nвиконується fn"),
        (b3, xe, "MULTI_STOP_EXIT\nрозходимося"),
    ]
    for zx, zx2, label in zones:
        P.append(fitbox(zx + 8, 54, zx2 - zx - 16, 54, label, size=13,
                        fill=GREY_BG, stroke=MUTED, sw=1.2))

    # дужка «переривання вимкнено»
    P.append(text((b1 + b3) / 2, 130, "переривання вимкнено на всіх ядрах процесора",
                  size=13.5, color=POS, bold=True))
    P.append(arrow(b1 + 4, 144, b3 - 4, 144, color=POS, sw=1.6))
    P.append(arrow(b3 - 4, 144, b1 + 4, 144, color=POS, sw=1.6))

    # вертикальні межі станів
    for bx in (b1, b2, b3):
        P.append(line(bx, 158, bx, 442, color=MUTED, sw=1.2, dash="5,5"))

    lanes = [
        ("ядро 0\nактивне", 300, True),
        ("ядро 1", 355, False),
        ("ядро 2", 440, False),
        ("ядро 3", 565, False),
    ]
    ly = 172
    for name, start, active in lanes:
        P.append(fitbox(30, ly, 225, 46, name, size=13.5, fill=BG, stroke=MUTED, sw=1.2))
        # смуга очікування в PREPARE
        P.append(rect(start, ly + 6, b1 - start, 34, fill=GREY_BG, stroke=MUTED, sw=1.2))
        # вікно з вимкненими перериваннями
        P.append(rect(b1, ly + 6, b2 - b1, 34, fill=BLUE_BG, stroke=NEG, sw=1.4))
        if active:
            P.append(fitbox(b2, ly + 6, b3 - b2, 34, "fn(arg)", size=13.5,
                            fill=GREEN_BG, stroke=FIELD, sw=1.6))
        else:
            P.append(fitbox(b2, ly + 6, b3 - b2, 34, "стоїть", size=13,
                            fill=BLUE_BG, stroke=NEG, sw=1.4))
        P.append(rect(b3, ly + 6, xe - b3, 34, fill=GREY_BG, stroke=MUTED, sw=1.2))
        ly += 70

    P.append(text(x0 + 120, 466, "своя робота", size=12.5, color=MUTED, anchor="start"))
    P.append(mtext(670, 496,
                   ["темп задає найповільніше ядро процесора: поки воно не дійшло до циклу,",
                    "переривання ще нікому не можна вимикати"],
                   size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, "rendezvous.svg"), W, H, *P,
           title="Чотири стани рандеву: перехід відбувається лише тоді, коли підтвердили всі")


# ── 2. Хто кого витісняє і що проходить попри все ───────────────────────────
def fig_silence_layers():
    W, H = 1080, 500
    P = []

    P.append(text(205, 92, "класи планування", size=15, bold=True))
    ladder = [
        ("клас stop — потік migration/N", GREEN_BG, FIELD, True),
        ("SCHED_DEADLINE", BG, MUTED, False),
        ("SCHED_FIFO / SCHED_RR", BG, MUTED, False),
        ("SCHED_OTHER (CFS/EEVDF)", BG, MUTED, False),
        ("SCHED_IDLE", BG, MUTED, False),
    ]
    ly = 112
    for name, bg, st, bold in ladder:
        P.append(fitbox(60, ly, 290, 56, name, size=13.5, fill=bg, stroke=st,
                        sw=2 if bold else 1.2, bold=bold))
        ly += 66
    P.append(mtext(205, 462, ["вищий клас витісняє всі нижчі;", "клас stop не витісняє ніхто"],
                   size=12.5, color=MUTED, lh=1.4))

    P.append(text(720, 92, "повз планувальник", size=15, bold=True))
    P.append(fitbox(430, 112, 190, 60, "апаратне\nпереривання", size=13,
                    fill=WARM_BG, stroke=MUTED, sw=1.4))
    P.append(fitbox(820, 112, 190, 60, "NMI, SMI,\nмашинний виняток", size=13,
                    fill=RED_BG, stroke=POS, sw=1.8))

    P.append(arrow(525, 178, 525, 232, color=MUTED, sw=1.6))
    P.append(arrow(915, 178, 915, 344, color=POS, sw=1.8))

    P.append(rect(410, 238, 610, 46, fill=RED_BG, stroke=POS, sw=1.6))
    P.append(text(715, 267, "local_irq_disable() на кожному ядрі", size=13.5, color=POS))

    P.append(fitbox(430, 300, 190, 56, "чекає до кінця", size=13,
                    fill=GREY_BG, stroke=MUTED, sw=1.2))
    P.append(fitbox(820, 350, 190, 56, "виконується", size=13,
                    fill=RED_BG, stroke=POS, sw=1.8))
    P.append(mtext(715, 442, ["stop_machine глушить усе, чим керує ядро,", "і нічого не обіцяє про решту"],
                   size=12.5, color=MUTED, lh=1.4))

    render(os.path.join(OUT, "silence-layers.svg"), W, H, *P,
           title="Три перепони на шляху чужого коду — і те, що проходить крізь усі")


# ── 3. Хто справді виконує fn ───────────────────────────────────────────────
def fig_active_cpus():
    W, H = 1140, 400
    P = []

    P.append(line(570, 58, 570, 300, color=MUTED, sw=1.2, dash="6,6"))

    def panel(x_left, code, boxes, caption):
        P.append(text(x_left + 245, 82, code, size=14.5, bold=True))
        bx = x_left + 12
        for label, active in boxes:
            P.append(fitbox(bx, 108, 108, 88,
                            label + ("\nfn(arg)" if active else "\nстоїть"), size=13,
                            fill=GREEN_BG if active else BLUE_BG,
                            stroke=FIELD if active else NEG, sw=1.8 if active else 1.4))
            bx += 122
        P.append(mtext(x_left + 245, 232, caption, size=13, color=MUTED, lh=1.4))

    panel(30, "stop_machine(fn, arg, NULL)",
          [("ядро 0", True), ("ядро 1", False), ("ядро 2", False), ("ядро 3", False)],
          ["fn виконується РІВНО ОДИН раз —", "на першому онлайновому ядрі"])

    panel(610, "stop_machine(fn, arg, cpu_online_mask)",
          [("ядро 0", True), ("ядро 1", True), ("ядро 2", True), ("ядро 3", True)],
          ["fn виконується на КОЖНОМУ ядрі —", "стільки разів, скільки ядер"])

    P.append(mtext(570, 336,
                   ["Зупиняються в обох випадках усі: третій аргумент не звужує зупинку,",
                    "а лише каже, хто саме всередині неї виконує роботу."],
                   size=13.5, lh=1.5))

    render(os.path.join(OUT, "active-cpus.svg"), W, H, *P,
           title="Третій аргумент: хто виконує функцію, а хто просто мовчить")


# ── 4. Три прилади, три вкладені виміри (вставка proj-freeze-cost) ──────────
def fig_three_rulers():
    W, H = 1340, 486
    P = []

    A, B, C, D, E, F = 70, 420, 560, 740, 880, 1270
    top, bh = 112, 58

    def bracket(x1, x2, y, color, cap=8):
        return (line(x1, y, x2, y, color=color, sw=2.2) +
                line(x1, y - cap, x1, y + cap, color=color, sw=2.2) +
                line(x2, y - cap, x2, y + cap, color=color, sw=2.2))

    # смуга подій
    segs = [
        (A, B, "пробудження зупинників і рандеву", GREY_BG, MUTED, False),
        (B, C, "бар'єр", GREY_BG, MUTED, False),
        (C, D, "fn", GREEN_BG, FIELD, True),
        (D, E, "бар'єр", GREY_BG, MUTED, False),
        (E, F, "розхід і повернення процесора викликачеві", GREY_BG, MUTED, False),
    ]
    for x1, x2, label, bg, st, bold in segs:
        P.append(fitbox(x1, top, x2 - x1, bh, label, size=13.5,
                        fill=bg, stroke=st, sw=2 if bold else 1.2, bold=bold))

    # позначки часу над смугою
    P.append(text(A, 96, "t0", size=13, color=NEG, anchor="start", bold=True))
    P.append(text(C, 96, "p->in", size=13, color=FIELD, bold=True))
    P.append(text(D, 96, "p->out", size=13, color=FIELD, bold=True))
    P.append(text(F, 96, "t1", size=13, color=NEG, anchor="end", bold=True))

    # напрямні (проведені так, щоб не перетинати жодного напису)
    for x in (C, D):
        P.append(line(x, top + bh, x, 236, color=MUTED, sw=1, dash="4 4"))
    for x in (B, E):
        P.append(line(x, top + bh, x, 316, color=MUTED, sw=1, dash="4 4"))
    for x in (A, F):
        P.append(line(x, top + bh, x, 396, color=MUTED, sw=1, dash="4 4"))

    P.append(bracket(C, D, 240, FIELD))
    P.append(mtext(650, 266, ["робота, заради якої все затівалося",
                              "міряє сама fn: ktime_get_mono_fast_ns()"],
                   size=13.5, color=FIELD, lh=1.35))

    P.append(bracket(B, E, 320, POS))
    P.append(mtext(650, 346, ["справжня зупинка: переривання вимкнені на всіх ядрах",
                              "міряє ftrace: трасувальник затримок irqsoff"],
                   size=13.5, color=POS, lh=1.35))

    P.append(bracket(A, F, 400, NEG))
    P.append(mtext(670, 426, ["те, що відчула задача, яка замовила зміну",
                              "міряє викликач: ktime_get_ns() до і після"],
                   size=13.5, color=NEG, lh=1.35))

    render(os.path.join(OUT, "three-rulers.svg"), W, H, *P,
           title="Три прилади міряють три різні тривалості однієї паузи")


if __name__ == "__main__":
    fig_rendezvous()
    fig_silence_layers()
    fig_active_cpus()
    fig_three_rulers()
    print("ok")
