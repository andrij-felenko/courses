# -*- coding: utf-8 -*-
"""Фігури до теми «Сироти й перепідпорядкування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_before_after():
    """Дерево до і після смерті батька."""
    W, H = 1060, 520
    f = []
    f.append(rect(30, 52, 480, 420, fill=BG, stroke=MUTED, sw=1, rx=10))
    f.append(rect(550, 52, 480, 420, fill=BG, stroke=MUTED, sw=1, rx=10))
    f.append(text(270, 84, "поки батько живий", size=14, bold=True))
    f.append(text(790, 84, "після завершення батька", size=14, bold=True))

    ys = [130, 210, 290, 370]

    # ── ліва панель ────────────────────────────────────────────────
    left = [("PID 1\ninit", LINE), ("PID 812\nsshd", LINE),
            ("PID 3120\nbash", LINE), ("PID 3455\nsleep", LINE)]
    for (s, st), cy in zip(left, ys):
        b, _, _ = textbox(250, cy, s, size=13, stroke=st)
        f.append(b)
    for i in range(3):
        f.append(arrow(250, ys[i] + 28, 250, ys[i + 1] - 28))
    f.append(text(300, 400, "PPID = 3120", size=12, color=MUTED, anchor="start"))

    # ── права панель ───────────────────────────────────────────────
    right = [("PID 1\ninit", LINE, FILL, INK),
             ("PID 812\nsshd", LINE, FILL, INK),
             ("PID 3120\nзавершився", POS, "#fdecea", POS),
             ("PID 3455\nsleep", LINE, FILL, INK)]
    for (s, st, fl, col), cy in zip(right, ys):
        b, _, _ = textbox(770, cy, s, size=13, stroke=st, fill=fl, color=col)
        f.append(b)
    f.append(arrow(770, ys[0] + 28, 770, ys[1] - 28))
    f.append(arrow(770, ys[1] + 28, 770, ys[2] - 28, color=MUTED))

    # нове батьківство: обхідний пунктир
    f.append(line(813, 370, 940, 370, color=NEG, sw=1.6, dash="7 5"))
    f.append(line(940, 370, 940, 130, color=NEG, sw=1.6, dash="7 5"))
    f.append(arrow(940, 130, 802, 130, color=NEG))
    f.append(text(930, 250, "перепідпорядковано", size=11, color=NEG, anchor="end"))
    f.append(text(820, 400, "PPID = 1", size=12, color=MUTED, anchor="start"))

    f.append(text(530, 500, "суцільна стрілка — «створив»;    пунктир — нове батьківство",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'reparent-before-after.svg'), W, H, *f,
           title="Смерть батька не розриває дерева")


def fig_ladder():
    """Три кроки пошуку нового батька."""
    W, H = 1000, 440
    f = []
    rows = [
        (62, "1. Інший живий потік того самого процесу",
             "процес насправді живий — діти лишаються в родині, ззовні не змінюється нічого"),
        (182, "2. Найближчий предок, що оголосив себе проміжним прибирачем",
              "prctl(PR_SET_CHILD_SUBREAPER, 1) — менеджер служб ловить своїх нащадків"),
        (302, "3. init того простору імен, у якому живе процес",
              "останній крок, безумовний: саме тут пошук завершується завжди"),
    ]
    for y, head, sub in rows:
        f.append(rect(120, y, 760, 86, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(140, y + 34, head, size=15, bold=True, anchor="start"))
        f.append(text(140, y + 62, sub, size=13, color=MUTED, anchor="start"))
    for y in (148, 268):
        f.append(arrow(500, y + 4, 500, y + 30))
        f.append(text(516, y + 24, "не знайшлося", size=12, color=MUTED, anchor="start"))
    f.append(text(500, 418,
                  "другий крок узагалі не виконується, якщо в роду процесу немає жодного проміжного прибирача",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'reaper-ladder.svg'), W, H, *f,
           title="Кому дістанеться сирота: три кроки пошуку")


def fig_double_fork():
    """Що купує кожен крок демонізації."""
    W, H = 1240, 330
    f = []
    stages = [
        (120, "оболонка\nзапускає програму"),
        (370, "fork\nбатько виходить"),
        (620, "setsid()"),
        (870, "fork\nбатько виходить"),
        (1120, "демон\nпрацює"),
    ]
    edges = []
    for cx, s in stages:
        b, w, h = textbox(cx, 110, s, size=13)
        f.append(b)
        edges.append((cx - w / 2, cx + w / 2, h))
    for i in range(4):
        f.append(arrow(edges[i][1] + 6, 110, edges[i + 1][0] - 6, 110))

    gains = [
        (370, "сирота під прибирачем;\nбільше не лідер групи"),
        (620, "новий сеанс:\nнема керуючого термінала"),
        (870, "не лідер сеансу:\nтермінал не здобути"),
    ]
    for i, (cx, s) in enumerate(gains):
        b, _, _ = textbox(cx, 250, s, size=13, fill="#eaf7ef", stroke=FIELD)
        f.append(b)
        top = 110 + edges[i + 1][2] / 2
        f.append(line(cx, top + 4, cx, 224, color=FIELD, sw=1.4, dash="6 4"))
    f.append(text(620, 308, "кожен крок купує окрему властивість — і жодну з них не дає інший",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'double-fork.svg'), W, H, *f,
           title="Подвійне розділення: навіщо два fork")


def _pgrp_panel(f, x0, dead):
    """Одна панель фігури про осиротілу групу; x0 — лівий край панелі."""
    d = x0 - 30
    f.append(rect(30 + d, 52, 580, 420, fill=BG, stroke=MUTED, sw=1, rx=10))
    # сеанс
    f.append(rect(60 + d, 150, 520, 270, fill="#f8f9fb", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(72 + d, 172, "сеанс", size=12, color=MUTED, anchor="start"))
    # група оболонки
    f.append(rect(180 + d, 190, 220, 76, fill=BG, stroke=LINE, sw=1.4))
    f.append(text(290 + d, 208, "група оболонки", size=11, color=MUTED))
    if dead:
        b, _, _ = textbox(290 + d, 240, "bash — завершився", size=13,
                          stroke=POS, fill="#fdecea", color=POS)
    else:
        b, _, _ = textbox(290 + d, 240, "bash", size=13)
    f.append(b)
    # група завдання
    f.append(rect(130 + d, 302, 320, 110, fill=BG, stroke=LINE, sw=1.4))
    f.append(text(290 + d, 320, "група завдання", size=11, color=MUTED))
    for cx, s in ((215, "make"), (365, "cc")):
        b, _, _ = textbox(cx + d, 352, s, size=13)
        f.append(b)
    f.append(text(290 + d, 396, "обидва зупинені", size=11, color=POS))


def fig_orphaned_pgrp():
    """Осиротіла група процесів."""
    W, H = 1260, 520
    f = []
    _pgrp_panel(f, 30, dead=False)
    _pgrp_panel(f, 650, dead=True)
    f.append(text(320, 84, "поки оболонка жива", size=14, bold=True))
    f.append(text(940, 84, "оболонка завершилася", size=14, bold=True))

    # ліва панель: живий зв'язок
    f.append(arrow(290, 268, 290, 298))
    f.append(text(302, 288, "батько", size=12, color=MUTED, anchor="start"))
    b, _, _ = textbox(320, 446, "зв'язок є — оболонка може подати SIGCONT",
                      size=13, fill="#eaf7ef", stroke=FIELD)
    f.append(b)

    # права панель: зв'язок зник, нове батьківство поза сеансом
    b, _, _ = textbox(940, 120, "прибирач\n(поза сеансом)", size=13, stroke=NEG)
    f.append(b)
    f.append(line(910, 268, 910, 298, color=MUTED, sw=1.4, dash="5 4"))
    f.append(line(902, 275, 918, 291, color=POS, sw=2))
    f.append(line(918, 275, 902, 291, color=POS, sw=2))
    f.append(text(924, 288, "зв'язок зник", size=12, color=POS, anchor="start"))
    f.append(line(1074, 352, 1150, 352, color=NEG, sw=1.6, dash="7 5"))
    f.append(line(1150, 352, 1150, 120, color=NEG, sw=1.6, dash="7 5"))
    f.append(arrow(1150, 120, 1006, 120, color=NEG))
    f.append(text(1140, 250, "новий батько", size=11, color=NEG, anchor="end"))
    b, _, _ = textbox(940, 446, "група осиротіла → SIGHUP, далі SIGCONT",
                      size=13, fill="#fdecea", stroke=POS)
    f.append(b)

    f.append(text(630, 500,
                  "група осиротіла, коли в її учасників не лишилося батька в тому ж сеансі, але в іншій групі",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'orphaned-pgrp.svg'), W, H, *f,
           title="Осиротіла група процесів: нема кому подати SIGCONT")


def fig_two_windows():
    """Два вікна, у яких наївний код бреше (для вставки-лабораторії)."""
    W, H = 1120, 530
    f = []

    # ── панель A: EOF раніше за перепідпорядкування ────────────────
    f.append(rect(30, 52, 1060, 200, fill=BG, stroke=MUTED, sw=1, rx=10))
    f.append(text(560, 78, "Вікно 1: EOF на трубі приходить раніше, ніж переписано PPID",
                  size=14, bold=True))

    def lane(y, label, marks, x0=150, x1=1060, size=12):
        """Часова доріжка: пунктир малюється ВІДРІЗКАМИ між рамками,
        щоб жодна лінія не проходила крізь напис."""
        out = [text(50, y + 4, label, size=size, color=MUTED, anchor="start")]
        spans = []
        for cx, s, kw in marks:
            b, w, _ = textbox(cx, y, s, size=size, **kw)
            out.append(b)
            spans.append((cx - w / 2 - 4, cx + w / 2 + 4))
        spans.sort()
        cur = x0
        for a, bnd in spans:
            if a > cur:
                out.append(line(cur, y, a, y, color=MUTED, sw=1.2, dash="4 4"))
            cur = max(cur, bnd)
        if cur < x1:
            out.append(line(cur, y, x1, y, color=MUTED, sw=1.2, dash="4 4"))
        return out

    f.append(text(330, 108, "дескриптори закрито", size=12, color=MUTED))
    f.append(text(640, 108, "PPID переписано", size=12, color=MUTED))
    f.extend(lane(130, "батько", [
        (330, "exit_files()", {}),
        (640, "exit_notify()", {}),
        (880, "батько — зомбі", dict(stroke=MUTED, color=MUTED)),
    ]))

    f.append(text(485, 166, "вікно", size=12, color=POS))
    f.append(arrow(485, 178, 387, 178, color=POS))
    f.append(arrow(485, 178, 583, 178, color=POS))

    f.extend(lane(210, "дитина", [
        (400, "read() → 0", {}),
        (560, "getppid() ще старий", dict(fill="#fdecea", stroke=POS, color=POS)),
        (800, "getppid() уже новий", dict(stroke=FIELD, color=FIELD)),
    ]))

    # ── панель B: fork → prctl ─────────────────────────────────────
    f.append(rect(30, 272, 1060, 210, fill=BG, stroke=MUTED, sw=1, rx=10))
    f.append(text(560, 298, "Вікно 2: між fork() і prctl(PR_SET_PDEATHSIG)",
                  size=14, bold=True))

    f.append(text(470, 328, "перепідпорядкування сталося", size=11, color=MUTED))
    f.extend(lane(350, "батько", [
        (300, "fork()", {}),
        (470, "_exit()", dict(stroke=POS, color=POS)),
    ]))

    f.append(text(570, 384, "вікно", size=12, color=POS))
    f.append(arrow(570, 396, 508, 396, color=POS))
    f.append(arrow(570, 396, 631, 396, color=POS))

    f.extend(lane(430, "робітник", [
        (300, "старт", {}),
        (700, "prctl(PDEATHSIG)", dict(fill="#fdecea", stroke=POS, color=POS)),
        (920, "getppid() ≠ батько → вихід", dict(stroke=FIELD, color=FIELD)),
    ]))

    f.append(text(560, 508,
                  "обидва вікна закриваються однаково: не вірити події, а перевіряти факт",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'lab-two-windows.svg'), W, H, *f)


def fig_wait_strangers():
    """Дослід із проміжним прибирачем: що саме віддає wait."""
    W, H = 1080, 420
    f = []
    f.append(line(600, 80, 600, 340, color=MUTED, sw=1, dash="5 5"))

    # ── ліворуч: дерево під час досліду ────────────────────────────
    f.append(text(300, 60, "дерево під час досліду", size=13, bold=True))
    b, _, _ = textbox(300, 110, "lab (PID 51602)\nPR_SET_CHILD_SUBREAPER = 1",
                      size=13, stroke=NEG, color=NEG)
    f.append(b)
    f.append(arrow(300, 138, 300, 180))
    b, _, _ = textbox(300, 207, "середній (51603)\nprctl-прапорця не має",
                      size=13, stroke=POS, color=POS)
    f.append(b)
    f.append(text(200, 258, "вийшов", size=11, color=POS, anchor="end"))
    f.append(arrow(300, 233, 300, 284))
    b, _, _ = textbox(300, 303, "онук (51604)", size=13)
    f.append(b)

    f.append(line(352, 303, 480, 303, color=NEG, sw=1.6, dash="7 5"))
    f.append(line(480, 303, 480, 110, color=NEG, sw=1.6, dash="7 5"))
    f.append(arrow(480, 110, 411, 110, color=NEG))
    f.append(text(492, 205, "новий батько", size=11, color=NEG, anchor="start"))

    # ── праворуч: що повертає wait ─────────────────────────────────
    f.append(text(825, 60, "що повертає waitpid(-1)", size=13, bold=True))
    b, _, _ = textbox(825, 110, "51603, код 3 — мій", size=13)
    f.append(b)
    b, _, _ = textbox(825, 175, "51604, код 42 — ЧУЖИЙ", size=13,
                      fill="#fdecea", stroke=POS, color=POS)
    f.append(b)
    b, _, _ = textbox(825, 240, "−1, errno = ECHILD", size=13,
                      stroke=MUTED, color=MUTED)
    f.append(b)
    f.append(text(825, 300, "«чужий» — це онук, якого lab не створював",
                  size=11, color=MUTED))

    f.append(text(540, 390,
                  "прапорець прибирача не успадковується через fork — тому онук минає середнього",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'lab-wait-strangers.svg'), W, H, *f,
           title="Дослід із проміжним прибирачем: wait віддає чужого онука")


if __name__ == '__main__':
    fig_before_after()
    fig_ladder()
    fig_double_fork()
    fig_orphaned_pgrp()
    fig_two_windows()
    fig_wait_strangers()
    print("готово:", OUT)
