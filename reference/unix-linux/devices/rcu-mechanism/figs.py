# -*- coding: utf-8 -*-
"""Фігури до теми «RCU: читання без замків і відкладене звільнення»."""

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
AMBER = "#b8860b"


# ── 1. Що коштує читання ────────────────────────────────────────────────────
def fig_reader_cost():
    W, H = 1400, 780
    P = []

    P.append(text(W / 2, 36, "Чотири ядра читають той самий список", size=17, bold=True))

    # ── ліва панель: замок ──
    lx, lw = 40, 640
    P.append(rect(lx, 68, lw, 560, fill=BG, stroke=MUTED, sw=1.5))
    P.append(text(lx + lw / 2, 100, "із замком «багато читачів»", size=15, bold=True, color=POS))

    # спільний рядок кеша посередині панелі
    P.append(fitbox(lx + 190, 306, 260, 84,
                    "спільний рядок кеша\nлічильник читачів",
                    size=13, fill=RED_BG, stroke=POS, sw=2.5))

    core_pos = [(lx + 40, 140), (lx + 400, 140), (lx + 40, 470), (lx + 400, 470)]
    for i, (cx, cy) in enumerate(core_pos):
        P.append(fitbox(cx, cy, 200, 62, "ядро %d" % i, size=13.5,
                        fill=GREY_BG, stroke=INK, sw=1.8, bold=True))
    # стрілки до рядка кеша — від краю коробки до краю коробки
    P.append(arrow(lx + 240, 202, lx + 300, 300, color=POS, sw=1.8))
    P.append(arrow(lx + 500, 202, lx + 400, 300, color=POS, sw=1.8))
    P.append(arrow(lx + 240, 470, lx + 300, 396, color=POS, sw=1.8))
    P.append(arrow(lx + 500, 470, lx + 400, 396, color=POS, sw=1.8))

    P.append(fitbox(lx + 30, 560, lw - 60, 50,
                    "кожен читач ЗАПИСУЄ — рядок переїжджає між ядрами по колу",
                    size=13, fill=RED_BG, stroke=POS, sw=2))

    # ── права панель: RCU ──
    rx_, rw = 720, 640
    P.append(rect(rx_, 68, rw, 560, fill=BG, stroke=MUTED, sw=1.5))
    P.append(text(rx_ + rw / 2, 100, "з RCU", size=15, bold=True, color=FIELD))

    P.append(fitbox(rx_ + 190, 306, 260, 84,
                    "список пристроїв\nтільки читається",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2.5))

    core_pos_r = [(rx_ + 40, 140), (rx_ + 400, 140), (rx_ + 40, 470), (rx_ + 400, 470)]
    for i, (cx, cy) in enumerate(core_pos_r):
        P.append(fitbox(cx, cy, 200, 62, "ядро %d" % i, size=13.5,
                        fill=GREY_BG, stroke=INK, sw=1.8, bold=True))
    P.append(arrow(rx_ + 240, 202, rx_ + 300, 300, color=FIELD, sw=1.8))
    P.append(arrow(rx_ + 500, 202, rx_ + 400, 300, color=FIELD, sw=1.8))
    P.append(arrow(rx_ + 240, 470, rx_ + 300, 396, color=FIELD, sw=1.8))
    P.append(arrow(rx_ + 500, 470, rx_ + 400, 396, color=FIELD, sw=1.8))

    P.append(fitbox(rx_ + 30, 560, rw - 60, 50,
                    "жодного спільного запису — копії рядка живуть у всіх ядер одразу",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(text(W / 2, 690,
                  "ліворуч пропускна здатність падає з кожним новим ядром,",
                  size=14, color=INK))
    P.append(text(W / 2, 718,
                  "праворуч — росте прямо пропорційно їхній кількості",
                  size=14, color=INK))
    P.append(text(W / 2, 754,
                  "різниця не в замку, а в тому, чи лишає читач по собі слід",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "reader-cost.svg"), W, H, *P)


# ── 2. Три фази оновлення ───────────────────────────────────────────────────
def fig_rcu_update():
    W, H = 1320, 860
    P = []

    P.append(text(W / 2, 36, "Вилучення вузла: три фази замість однієї", size=17, bold=True))

    NW, NH, GAP = 150, 66, 74      # вузол списку
    x0 = 300

    def draw_list(y, removed, freed, bcolor, bfill, blabel):
        """Малює ланцюжок A → B → C на висоті y."""
        out = []
        names = ["A", "B", "C"]
        xs = [x0 + i * (NW + GAP) for i in range(3)]
        for name, x in zip(names, xs):
            if name == "B":
                out.append(fitbox(x, y, NW, NH, blabel, size=13,
                                  fill=bfill, stroke=bcolor, sw=2.5))
            else:
                out.append(fitbox(x, y, NW, NH, "вузол " + name, size=13,
                                  fill=GREY_BG, stroke=INK, sw=1.8))
        # A → B
        if removed:
            # обхідна стрілка A → C над вузлами
            out.append(arrow(xs[0] + NW / 2, y - 8, xs[2] + NW / 2, y - 8,
                             color=FIELD, sw=2.2))
            out.append(text((xs[0] + xs[2]) / 2 + NW / 2, y - 20,
                            "новий читач іде повз", size=12, color=FIELD))
        else:
            out.append(arrow(xs[0] + NW, y + NH / 2, xs[1] - 6, y + NH / 2,
                             color=INK, sw=2))
        # B → C
        if not freed:
            out.append(arrow(xs[1] + NW, y + NH / 2, xs[2] - 6, y + NH / 2,
                             color=INK if not removed else MUTED, sw=2))
        return out, xs

    # ── фаза 1 ──
    y1 = 130
    P.append(fitbox(40, y1 - 12, 230, 92,
                    "1. звичайний стан\n\nчитачі ходять списком\nбез жодного замка",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.5))
    frag, xs = draw_list(y1, removed=False, freed=False,
                         bcolor=INK, bfill=GREY_BG, blabel="вузол B")
    P += frag
    P.append(fitbox(xs[1] - 20, y1 + NH + 26, 190, 40, "читач стоїть тут",
                    size=12.5, fill=BLUE_BG, stroke=NEG, sw=1.8))

    # ── фаза 2 ──
    y2 = 350
    P.append(fitbox(40, y2 - 12, 230, 130,
                    "2. від'єднано\n\nlist_del_rcu()\n\nB зник із поля зору нових,\nале його next цілий",
                    size=12.5, fill=BG, stroke=AMBER, sw=1.8))
    frag, xs = draw_list(y2, removed=True, freed=False,
                         bcolor=AMBER, bfill=WARM_BG, blabel="вузол B\nживий, недосяжний")
    P += frag
    P.append(fitbox(xs[1] - 20, y2 + NH + 26, 190, 40, "старий читач ще тут",
                    size=12.5, fill=BLUE_BG, stroke=NEG, sw=1.8))
    P.append(text(xs[2] + NW / 2, y2 + NH + 48,
                  "і вийде сюди за вцілілим next", size=12.5, color=MUTED))

    # ── проміжок ──
    P.append(fitbox(300, 580, 700, 56,
                    "період відстрочки: чекаємо, доки кожне ядро процесора побуває у спокійному стані",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2.5))

    # ── фаза 3 ──
    y3 = 690
    P.append(fitbox(40, y3 - 12, 230, 92,
                    "3. звільнено\n\nстарих читачів не лишилось —\nпам'ять безпечно віддати",
                    size=12.5, fill=BG, stroke=FIELD, sw=1.8))
    frag, xs = draw_list(y3, removed=True, freed=True,
                         bcolor=POS, bfill=RED_BG, blabel="пам'ять\nвіддано")
    P += frag

    render(os.path.join(OUT, "rcu-update.svg"), W, H, *P)


# ── 3. Часова діаграма періоду відстрочки ──────────────────────────────────
def fig_grace_period():
    W, H = 1400, 720
    P = []

    P.append(text(W / 2, 36, "Період відстрочки накриває всіх, хто почав раніше", size=17, bold=True))

    T0, T1 = 300, 1210        # межі осі часу
    rows = [180, 300, 420]
    labels = ["ядро 0", "ядро 1", "ядро 2"]

    X_DEL = 430               # момент list_del_rcu
    X_END = 1030              # кінець періоду відстрочки

    # смуга періоду (лише контур — заливка ховала б читання, що перетинають межу)
    P.append(rect(X_DEL, 120, X_END - X_DEL, 370, fill="none", stroke=NEG,
                  sw=2, rx=4))

    for y, lbl in zip(rows, labels):
        P.append(text(T0 - 24, y + 5, lbl, size=13.5, color=INK, anchor="end"))
        P.append(line(T0, y, T1, y, color="#c9ccd2", sw=1.4))

    # ділянки читання: (рядок, початок, кінець, старий?)
    reads = [
        (0, 340, 620, True),
        (0, 700, 830, False),
        (1, 380, 950, True),
        (1, 1010, 1120, False),
        (2, 460, 560, False),
        (2, 640, 760, False),
    ]
    for r, a, b, old in reads:
        y = rows[r]
        col = POS if old else FIELD
        bg = RED_BG if old else GREEN_BG
        P.append(rect(a, y - 17, b - a, 34, fill=bg, stroke=col, sw=2.2, rx=5))

    # спокійні стани
    quiescent = [(0, 660), (1, 980), (2, 600), (2, 800)]
    for r, x in quiescent:
        y = rows[r]
        P.append(circle(x, y, 8, fill=BG, stroke=NEG, sw=2.5))

    # вертикалі подій
    P.append(line(X_DEL, 120, X_DEL, 500, color=AMBER, sw=2.4, dash="6,5"))
    P.append(line(X_END, 120, X_END, 500, color=NEG, sw=2.4, dash="6,5"))

    P.append(mtext(X_DEL, 92, ["вузол", "від'єднано"], size=12.5,
                   color=AMBER, bold=True, lh=1.25))
    P.append(mtext(X_END, 92, ["період скінчився —", "можна звільняти"], size=12.5,
                   color=NEG, bold=True, lh=1.25))

    # вісь
    P.append(arrow(T0, 520, T1, 520, color=MUTED, sw=1.6))
    P.append(text(T1 - 30, 546, "час", size=13, color=MUTED))

    # легенда
    LY = 592
    P.append(rect(150, LY, 30, 22, fill=RED_BG, stroke=POS, sw=2, rx=4))
    P.append(text(196, LY + 17, "почав ДО від'єднання — його й чекаємо",
                  size=12.5, color=INK, anchor="start"))
    P.append(rect(700, LY, 30, 22, fill=GREEN_BG, stroke=FIELD, sw=2, rx=4))
    P.append(text(746, LY + 17, "почав пізніше — вузла вже не бачить",
                  size=12.5, color=INK, anchor="start"))
    P.append(circle(164, LY + 58, 8, fill=BG, stroke=NEG, sw=2.5))
    P.append(text(196, LY + 63, "спокійний стан: перемикання контексту, простій або вихід у простір користувача",
                  size=12.5, color=INK, anchor="start"))

    P.append(text(W / 2, 700,
                  "останній старий читач скінчився раніше — період усе одно тривав до звіту всіх ядер",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "grace-period.svg"), W, H, *P)


# ── 4. Вивантаження модуля: черга зворотних викликів ───────────────────────
def fig_module_unload():
    W, H = 1400, 560
    P = []

    P.append(text(W / 2, 36, "rmmod: хто дочекався черги зворотних викликів, а хто ні",
                  size=17, bold=True))

    BW, BH, STEP = 236, 116, 272
    XS = [292 + i * STEP for i in range(4)]

    def row(y, label, lab_color, cells):
        out = [fitbox(40, y, 216, BH, label, size=13.5, bold=True,
                      fill=BG, stroke=lab_color, sw=2.2)]
        for x, (txt, fill, stroke) in zip(XS, cells):
            out.append(fitbox(x, y, BW, BH, txt, size=12.5,
                              fill=fill, stroke=stroke, sw=2))
        for i in range(3):
            out.append(arrow(XS[i] + BW, y + BH / 2, XS[i + 1] - 8, y + BH / 2,
                             color=MUTED, sw=1.8))
        return out

    P += row(96, "без\nrcu_barrier()", POS, [
        ("call_rcu()\nвиклик стає в чергу\nсвого ядра процесора", GREY_BG, INK),
        ("module_exit()\nповернувся,\nчерга не порожня", WARM_BG, AMBER),
        ("код модуля\nзвільнено", WARM_BG, AMBER),
        ("період скінчився —\nядро кличе адресу,\nде коду вже немає", RED_BG, POS),
    ])

    P += row(316, "з\nrcu_barrier()", FIELD, [
        ("call_rcu()\nвиклик стає в чергу\nсвого ядра процесора", GREY_BG, INK),
        ("rcu_barrier()\nставить свій виклик\nу чергу кожного ядра", BLUE_BG, NEG),
        ("черга йде по порядку —\nвсе попереду\nвже відпрацювало", GREEN_BG, FIELD),
        ("module_exit()\nповернувся, кликати\nвже нема кому", GREEN_BG, FIELD),
    ])

    P.append(text(W / 2, 492,
                  "synchronize_rcu() тут не рятує: він чекає періоду відстрочки,",
                  size=13.5, color=INK))
    P.append(text(W / 2, 520,
                  "а не виконання того, що вже стоїть у черзі",
                  size=13.5, color=INK))

    render(os.path.join(OUT, "module-unload.svg"), W, H, *P)


if __name__ == "__main__":
    fig_reader_cost()
    fig_rcu_update()
    fig_grace_period()
    fig_module_unload()
    print("ok")
