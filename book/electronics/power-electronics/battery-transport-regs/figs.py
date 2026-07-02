# -*- coding: utf-8 -*-
"""Фігури до теми «Норми перевезення літієвих батарей»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Смуга ват-годин: пороги, що визначають режим ─────────────────────────
def fig_wh_ladder():
    W, H = 720, 340
    frags = []
    # вертикальна вісь енергії злизу
    x0 = 120
    top, bot = 70, 300
    frags.append(line(x0, bot, x0, top, INK, 2.0))
    frags.append(text(x0, top - 16, "енергія однієї батареї, Вт·год", size=13, bold=True, anchor="middle"))

    # пороги (значення Вт·год -> частка висоти, логарифмічно на око)
    marks = [
        (0,   "0"),
        (100, "100"),
        (160, "160"),
    ]
    def y_of(frac):  # frac 0..1 знизу вгору
        return bot - frac * (bot - top)

    # три зони як кольорові смуги праворуч від осі
    zx, zw = x0 + 10, 300
    # зелена: <100
    frags.append(rect(zx, y_of(0.66), zw, y_of(0.0) - y_of(0.66), fill="#e8f6ee", stroke=FIELD, sw=1.5))
    frags.append(fitbox(zx + 8, y_of(0.30) - 22, zw - 16, 44,
                        "до 100 Вт·год\nпасажирський салон — без дозволу",
                        size=13, fill="none", stroke="none", color="#1e7a44"))
    # жовта: 100..160
    frags.append(rect(zx, y_of(0.86), zw, y_of(0.66) - y_of(0.86), fill="#fef6e0", stroke="#c9911f", sw=1.5))
    frags.append(fitbox(zx + 8, y_of(0.76) - 18, zw - 16, 36,
                        "100–160 Вт·год\nлише з дозволу авіакомпанії, ≤2 шт",
                        size=12, fill="none", stroke="none", color="#8a6410"))
    # червона: >160
    frags.append(rect(zx, y_of(1.0), zw, y_of(0.86) - y_of(1.0), fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(fitbox(zx + 8, y_of(0.93) - 16, zw - 16, 32,
                        "понад 160 Вт·год\nзаборонено на пасажирських рейсах",
                        size=12, fill="none", stroke="none", color="#a5281c"))

    # позначки порогів на осі
    for val, lbl in marks:
        frac = {0: 0.0, 100: 0.66, 160: 0.86}[val]
        yy = y_of(frac)
        frags.append(line(x0 - 6, yy, x0 + 6, yy, INK, 2.0))
        frags.append(text(x0 - 12, yy + 4, lbl, size=13, anchor="end", bold=True))

    # приклад повербанка збоку
    frags.append(text(zx + zw / 2, bot + 28, "27 000 мА·год × 3.7 В = 99.9 Вт·год  →  ще зелена зона",
                      size=12, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(IMG, 'wh-ladder.svg'), W, H, *frags,
           title="Поріг рахують за енергією, не за ємністю")


# ── 2. Шість UN-номерів: хімія × упаковка ───────────────────────────────────
def fig_un_matrix():
    W, H = 720, 360
    frags = []
    # дві осі підпису
    col_x = [270, 430, 590]
    row_y = [150, 250]
    ch = 130   # ширина клітини
    cw = 130

    # заголовки колонок (спосіб упаковки)
    heads = ["сама\n(окремо)", "з приладом\n(поряд)", "у приладі\n(всередині)"]
    for i, hx in enumerate(col_x):
        frags.append(fitbox(hx - cw / 2, 70, cw, 46, heads[i], size=12,
                            fill="#eef2f7", stroke=LINE, color=INK, bold=True))

    # підписи рядків (хімія)
    frags.append(fitbox(70, row_y[0] - 26, 150, 52, "літій-іонна\n(акумулятор)",
                        size=13, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    frags.append(fitbox(70, row_y[1] - 26, 150, 52, "літій-металева\n(одноразова)",
                        size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # клітини з UN-номерами
    cells = {
        (0, 0): ("UN 3480", "#eaf0fd", NEG),
        (0, 1): ("UN 3481", "#eaf0fd", NEG),
        (0, 2): ("UN 3481", "#eaf0fd", NEG),
        (1, 0): ("UN 3090", "#fdecea", POS),
        (1, 1): ("UN 3091", "#fdecea", POS),
        (1, 2): ("UN 3091", "#fdecea", POS),
    }
    for (r, c), (un, fill, stroke) in cells.items():
        frags.append(fitbox(col_x[c] - cw / 2, row_y[r] - ch / 2 + 10, cw, ch - 40,
                            un, size=17, fill=fill, stroke=stroke, color=stroke, bold=True))

    frags.append(text(W / 2, 330, "Той самий елемент дістає РІЗНИЙ номер залежно від упаковки — бо різний ризик.",
                      size=12, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(IMG, 'un-matrix.svg'), W, H, *frags,
           title="Чотири UN-номери літію: хімія × спосіб упаковки")


# ── 3. Ланцюг теплового розгону: чому халон у трюмі не гасить ────────────────
def fig_runaway():
    W, H = 720, 300
    frags = []
    y = 150
    boxes = [
        (110, "коротке\nзамикання\nчи перегрів", "#fef0ee", POS),
        (285, "перша\nкомірка\nрозганяється", "#fdecea", POS),
        (460, "виділяє\nтепло + власний\nкисень", "#fbe3df", POS),
        (635, "підпалює\nсусідні\nкомірки", "#f7cfc8", POS),
    ]
    bw = 130
    for cx, txt, fill, st in boxes:
        frags.append(fitbox(cx - bw / 2, y - 45, bw, 90, txt, size=12,
                            fill=fill, stroke=st, color="#8a1f13", bold=True))
    # стрілки між ними
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + bw / 2 + 4
        x2 = boxes[i + 1][0] - bw / 2 - 4
        frags.append(arrow(x1, y, x2, y, POS, 2.2))

    # знизу — чому халон не рятує
    frags.append(fitbox(110, y + 78, 500, 54,
                        "Халон гасить, перериваючи горіння киснем ззовні.\n"
                        "Тут кисень народжується ВСЕРЕДИНІ — гасити нема чого перервати.",
                        size=13, fill="#eef2f7", stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'runaway.svg'), W, H, *frags,
           title="Тепловий розгін: пожежа сама себе живить киснем")


# ── 4. Хроніка інцидентів (для вставки hist) ────────────────────────────────
def fig_incident_timeline():
    W, H = 760, 300
    frags = []
    # горизонтальна вісь часу
    ax_x0, ax_x1 = 60, 690
    ax_y = 150
    frags.append(line(ax_x0, ax_y, ax_x1, ax_y, INK, 2.2))
    frags.append(arrow(ax_x1 - 2, ax_y, ax_x1 + 14, ax_y, INK, 2.2))

    # рік · назва · короткий підпис · колір крапки · заливка · над віссю?
    events = [
        (1996, "FedEx 1406", "вантажна пожежа,\nлітак згорів",      MUTED, "#eef2f7", True),
        (2006, "UPS 1307",   "перша підозра\nна літій",             NEG,   "#eaf0fd", False),
        (2010, "UPS 6",      "катастрофа, 2 жертви;\nхалон безсилий", POS, "#fdecea", True),
        (2013, "787",        "штатна батарея\nв розгоні",           POS,   "#fbe3df", False),
        (2016, "ІКАО",       "заборона голих;\nзаряд ≤30 %",        FIELD, "#e8f6ee", True),
        (2024, "89 випадків","≈2/тиждень, +16 %\n(лише підтверджені)", POS, "#f7cfc8", False),
    ]
    xs = [95, 205, 320, 435, 545, 655]
    bw, bh = 122, 54

    for (yr, name, desc, col, fill, above), x in zip(events, xs):
        frags.append(circle(x, ax_y, 6, fill=col, stroke=INK, sw=1.6))
        yr_y = ax_y - 14 if above else ax_y + 22
        frags.append(text(x, yr_y, str(yr), size=13, bold=True, color=INK))
        if above:
            by = ax_y - 30 - bh
            frags.append(line(x, ax_y - 8, x, by + bh, col, 1.4, dash="3,3"))
        else:
            by = ax_y + 32
            frags.append(line(x, ax_y + 8, x, by, col, 1.4, dash="3,3"))
        frags.append(fitbox(x - bw / 2, by, bw, bh,
                            name + "\n" + desc, size=11,
                            fill=fill, stroke=col, color=INK, bold=True))

    frags.append(text(W / 2, H - 12,
                      "Кожна цифра норм — слід від пожежі; крива інцидентів не спадає.",
                      size=12, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(IMG, 'incident-timeline.svg'), W, H, *frags,
           title="Літій у повітрі: від першої пожежі до статистики, що росте")


if __name__ == '__main__':
    fig_wh_ladder()
    fig_un_matrix()
    fig_runaway()
    fig_incident_timeline()
    print("figs done ->", IMG)
