# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Періодичні події» (планування реального часу).
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
GREYBG  = "#eef2f7"


# ── 1. Розклад як таблиця задач ─────────────────────────────────────────────
# Ідея: кожна періодична задача — рядок «що / як часто / коли востаннє».
# Опис даними замість десятка окремих if.
def fig_task_table():
    W, H = 940, 430
    P = [text(W / 2, 30, "Розклад: таблиця задач, у кожної свій період", size=17, bold=True),
         text(W / 2, 50, "замість купи окремих if — один список «що, як часто, коли востаннє»",
              size=11, color=MUTED, italic=True)]

    cols = [("ЗАДАЧА", 90, 250), ("ПЕРІОД", 350, 130), ("ВОСТАННЄ", 490, 140), ("ДІЯ", 640, 250)]
    head_y = 86
    for label, x, w in cols:
        P.append(fitbox(x, head_y, w, 32, label, size=12, bold=True,
                        color=NEG, fill=BLUEBG, stroke=NEG))

    rows = [
        ("блимати LED", "500 мс", "t1", "toggleLed()"),
        ("опитати давач", "100 мс", "t2", "readSensor()"),
        ("оновити екран", "1000 мс", "t3", "updateLcd()"),
    ]
    y0, dy = 130, 44
    for i, (task, per, last, act) in enumerate(rows):
        y = y0 + i * dy
        P.append(fitbox(90, y, 250, 36, task, size=12, bold=True, fill=BG, stroke=FIELD))
        P.append(fitbox(350, y, 130, 36, per, size=12, bold=True, color=AMBER, fill=BG, stroke=MUTED))
        P.append(fitbox(490, y, 140, 36, last, size=12, fill=BG, stroke=MUTED))
        P.append(fitbox(640, y, 250, 36, act, size=12, fill=BG, stroke=MUTED))

    fr, w, h = textbox(W / 2, 360,
                       "Кожен рядок — окрема періодична задача.\n"
                       "Цикл лише перебирає таблицю й запускає ті, чий час настав.\n"
                       "Це і є найпростіший планувальник.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/task-table.svg", W, H, *P)


# ── 2. Планувальник: цикл перебирає таблицю ─────────────────────────────────
# Ідея: один прохід for по таблиці замінює десяток if; дозрілі — запускає.
def fig_scheduler_loop():
    W, H = 940, 460
    P = [text(W / 2, 30, "Планувальник: один прохід по таблиці замість купи if", size=17, bold=True)]

    # ліворуч — цикл loop()
    lx, ly = 70, 80
    P.append(fitbox(lx, ly, 250, 40, "loop(): now = millis()", size=13, bold=True,
                    color=INK, fill=GREYBG, stroke=INK))
    P.append(fitbox(lx, ly + 56, 250, 40, "for t : tasks", size=13, bold=True,
                    color=NEG, fill=BLUEBG, stroke=NEG))
    P.append(arrow(lx + 125, ly + 40, lx + 125, ly + 56, color=MUTED))

    # перевірка дозрілості
    cx, cy = 195, 230
    fr, w, h = textbox(cx, cy, "now − t.last\n≥ t.period ?", size=12.5, bold=True,
                       color=AMBER, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    P.append(arrow(lx + 125, ly + 96, cx, cy - h / 2, color=MUTED))

    # так → запуск
    P.append(text(cx + 150, cy - 14, "так", size=11, color=FIELD, bold=True))
    fr, w, h = textbox(cx + 290, cy, "t.last += t.period\nt.run()", size=12.5, bold=True,
                       color=FIELD, fill=GRNBG, stroke=FIELD)
    P.append(fr)
    P.append(arrow(cx + 70, cy, cx + 290 - w / 2, cy, color=FIELD))

    # ні → наступний рядок
    P.append(text(cx, cy + 70, "ні → наступний рядок", size=11, color=MUTED))
    P.append(arrow(cx, cy + 40, cx, cy + 58, color=MUTED))

    fr, w, h = textbox(W / 2, 400,
                       "Один прохід for по таблиці замінює десяток окремих if.\n"
                       "Додати задачу = дописати рядок. Маленький «фреймворк часу» на millis().",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/scheduler-loop.svg", W, H, *P)


# ── 3. Межа кооперативності: довга задача затримує всіх ──────────────────────
# Ідея: кооперативний цикл не витісняє; поки тягнеться B, дозріла C чекає.
def fig_cooperative_limit():
    W, H = 940, 420
    P = [text(W / 2, 30, "Кооперативність: довга задача затримує всіх інших", size=17, bold=True)]

    # часова вісь
    ax_y = 150
    P.append(arrow(70, ax_y, 880, ax_y, color=INK, sw=1.8))
    P.append(text(880, ax_y + 22, "час →", size=12, color=INK, bold=True))

    # блоки задач на осі: A коротка, B довга, C мусить чекати
    def block(x, w, label, col, fill):
        P.append(rect(x, ax_y - 34, w, 34, fill=fill, stroke=col, sw=1.6))
        P.append(text(x + w / 2, ax_y - 13, label, size=12, color=col, bold=True))

    block(90, 80, "A", FIELD, GRNBG)
    block(180, 420, "B (довга)", POS, "#fdecea")
    block(610, 80, "C", NEG, BLUEBG)

    # «час C настав» — раніше, але мусить чекати кінця B
    P.append(line(300, ax_y + 6, 300, ax_y + 70, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(300, ax_y + 88, "час C настав", size=10.5, color=NEG, bold=True))
    P.append(line(610, ax_y + 6, 610, ax_y + 50, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(610, ax_y + 68, "C нарешті йде", size=10.5, color=NEG))
    P.append(arrow(310, ax_y + 40, 600, ax_y + 40, color=POS, sw=1.6))
    P.append(text(455, ax_y + 32, "C чекає кінця B", size=11, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 360,
                       "Жодна задача нікого не перебиває — лише чемно чекає черги.\n"
                       "Тому кожна МУСИТЬ бути короткою: одна «жадібна» псує таймінг усіх.",
                       size=12, bold=True, color=POS, fill="#fdecea", stroke=POS)
    P.append(fr)
    render("img/cooperative-limit.svg", W, H, *P)


# ── 4. М'який проти жорсткого реального часу ─────────────────────────────────
# Ідея: пропуск строку — або лише гірша якість (м'який), або відмова (жорсткий).
def fig_soft_vs_hard():
    W, H = 940, 430
    P = [text(W / 2, 30, "М'який і жорсткий реальний час: чого коштує пропуск строку",
              size=17, bold=True)]

    # дві колонки
    for cx, title, col, fill, deadline, miss, ex in [
        (255, "М'ЯКИЙ", FIELD, GRNBG, "строк бажаний",
         "пропуск → трохи гірша якість",
         "блимання збилося,\nдисплей оновився пізніше"),
        (685, "ЖОРСТКИЙ", POS, "#fdecea", "строк обов'язковий",
         "пропуск → відмова, інколи небезпека",
         "крок двигуна не в строк,\nподушка безпеки спізнилась"),
    ]:
        P.append(fitbox(cx - 150, 70, 300, 34, title, size=14, bold=True, color=col, fill=fill, stroke=col))
        fr, w, h = textbox(cx, 150, deadline, size=12, bold=True, color=INK, fill=BG, stroke=MUTED)
        P.append(fr)
        fr, w, h = textbox(cx, 215, miss, size=11.5, bold=True, color=col, fill=fill, stroke=col)
        P.append(fr)
        fr, w, h = textbox(cx, 290, ex, size=11, color=MUTED, fill=BG, stroke=MUTED)
        P.append(fr)

    P.append(line(W / 2, 60, W / 2, 320, color="#d0d5dd", sw=1.2, dash="5 4"))

    fr, w, h = textbox(W / 2, 380,
                       "Планувальник на millis() — для м'якого часу.\n"
                       "Жорсткий потребує апаратних таймерів або RTOS.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/soft-vs-hard.svg", W, H, *P)


# ── 5. Системний тік: рівне переривання задає ритм ───────────────────────────
# Ідея: апаратний таймер б'є рівно; задачі — на кратних тіках.
def fig_system_tick():
    W, H = 940, 400
    P = [text(W / 2, 30, "Системний тік: апаратний таймер задає рівний ритм", size=17, bold=True)]

    # лінія тіків
    ax_y = 150
    P.append(arrow(80, ax_y, 880, ax_y, color=INK, sw=1.8))
    P.append(text(470, 92, "тіки таймера (рівні, апаратні)", size=11, color=POS, bold=True))
    n = 9
    x0, step = 130, 85
    for i in range(n):
        x = x0 + i * step
        P.append(line(x, ax_y - 20, x, ax_y, color=POS, sw=2.2))
        P.append(text(x, ax_y - 26, "↯", size=12, color=POS, bold=True))
        P.append(text(x, ax_y + 18, str(i + 1), size=9.5, color=INK))

    fr, w, h = textbox(W / 2, 250,
                       "Планувальник дивиться лише на лічильник тіків:\n"
                       "A — щотіку,  B — щоп'ятого,  C — щосотого.",
                       size=12.5, bold=True, fill=GREYBG, stroke=INK)
    P.append(fr)

    fr, w, h = textbox(W / 2, 345,
                       "Той самий принцип, що в кварцовому дільнику годинника:\n"
                       "рівний тік + лічба = розклад подій.",
                       size=11.5, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/system-tick.svg", W, H, *P)


# ── 6. Від кооперативного суперциклу до витісняючого RTOS ────────────────────
# Ідея: ліворуч — черга без витіснення; праворуч — RTOS витісняє заради терміновішої.
def fig_toward_rtos():
    W, H = 940, 430
    P = [text(W / 2, 30, "Від кооперативного суперциклу до витісняючого планувальника",
              size=17, bold=True)]

    # ЛІВОРУЧ — суперцикл
    P.append(fitbox(60, 70, 360, 32, "СУПЕРЦИКЛ на millis()", size=13, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    ax_y = 160
    P.append(arrow(70, ax_y, 410, ax_y, color=INK, sw=1.6))
    for i, (lbl, col) in enumerate([("A", FIELD), ("B", NEG), ("C", AMBER), ("A", FIELD)]):
        x = 90 + i * 80
        P.append(rect(x, ax_y - 30, 60, 30, fill=BG, stroke=col, sw=1.5))
        P.append(text(x + 30, ax_y - 10, lbl, size=12, color=col, bold=True))
    P.append(text(240, ax_y + 24, "кожна коротка, чекає черги, без витіснення",
                  size=10.5, color=MUTED))

    # ПРАВОРУЧ — RTOS
    P.append(fitbox(520, 70, 360, 32, "RTOS: витісняючий планувальник", size=13, bold=True,
                    color=POS, fill="#fdecea", stroke=POS))
    bx = 690
    P.append(rect(bx - 70, 130, 140, 30, fill=GRNBG, stroke=FIELD, sw=1.5))
    P.append(text(bx, 150, "низький пріоритет", size=10.5, color=FIELD, bold=True))
    P.append(rect(bx - 70, 200, 140, 30, fill="#fdecea", stroke=POS, sw=1.6))
    P.append(text(bx, 220, "високий — витісняє", size=10.5, color=POS, bold=True))
    P.append(arrow(bx, 200, bx, 162, color=POS, sw=1.8))
    P.append(text(bx + 130, 185, "перебиває,\nяк переривання", size=10, color=POS, bold=True))

    P.append(line(W / 2, 60, W / 2, 300, color="#d0d5dd", sw=1.2, dash="5 4"))

    fr, w, h = textbox(W / 2, 370,
                       "Опанувавши неблокуючий розклад, ви вже мислите як планувальник —\n"
                       "і витіснення RTOS стає природним наступним поверхом.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/toward-rtos.svg", W, H, *P)


# ── insert: колесо таймерів ─────────────────────────────────────────────────
# Ідея: кільце слотів-«циферблат», стрілка «зараз», подія в слот (зараз+Δ).
def fig_wheel():
    import math
    W, H = 720, 560
    P = [text(W / 2, 30, "Колесо таймерів: подію через Δ — у слот (зараз + Δ)", size=16.5, bold=True)]

    cx, cy, R = W / 2, 300, 175
    N = 12
    P.append(circle(cx, cy, R, fill=BG, stroke=INK, sw=1.6))
    for i in range(N):
        a = -math.pi / 2 + 2 * math.pi * i / N
        sx, sy = cx + (R - 30) * math.cos(a), cy + (R - 30) * math.sin(a)
        slot = "#fdecea" if i in (0, 7) else FILL
        st = POS if i in (0, 7) else MUTED
        P.append(circle(sx, sy, 22, fill=slot, stroke=st, sw=1.6))
        P.append(text(sx, sy + 4, str(i), size=11, color=INK, bold=(i in (0, 7))))

    # стрілка «зараз» → слот 0
    a0 = -math.pi / 2
    P.append(arrow(cx, cy, cx + (R - 60) * math.cos(a0), cy + (R - 60) * math.sin(a0),
                   color=POS, sw=2.4))
    P.append(text(cx, cy - 8, "зараз", size=12, color=POS, bold=True))

    # підпис «зараз + Δ» біля слота 7
    a7 = -math.pi / 2 + 2 * math.pi * 7 / N
    lx, ly = cx + (R + 38) * math.cos(a7), cy + (R + 38) * math.sin(a7)
    P.append(text(lx, ly, "(зараз+Δ) mod РОЗМІР", size=11, color=POS, bold=True, anchor="middle"))

    fr, w, h = textbox(W / 2, 520,
                       "Стрілка щотіку йде на один слот і запускає все, що в ньому.\n"
                       "Торкаємось лише таймерів, чий час настав, — а не всіх щотіку.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/wheel.svg", W, H, *P)


# ── insert: лінійний список O(N) проти колеса O(1) ──────────────────────────
def fig_compare():
    W, H = 940, 380
    P = [text(W / 2, 30, "Перебрати всі N щотіку (O(N)) проти торкнутись лише слота (O(1))",
              size=16, bold=True)]

    # ліворуч — лінійний список
    P.append(fitbox(70, 75, 360, 32, "ЛІНІЙНИЙ СПИСОК — O(N)", size=13, bold=True,
                    color=POS, fill="#fdecea", stroke=POS))
    for i in range(6):
        x = 90 + i * 55
        P.append(rect(x, 140, 44, 34, fill=BG, stroke=MUTED, sw=1.3))
        P.append(text(x + 22, 162, "t%d" % (i + 1), size=10.5, color=INK))
    P.append(text(250, 205, "перевіряємо ВСІ N щотіку", size=11, color=POS, bold=True))
    P.append(text(250, 226, "добре для жмені", size=10.5, color=MUTED))

    # праворуч — колесо
    P.append(fitbox(520, 75, 360, 32, "КОЛЕСО — O(1)", size=13, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    for i in range(6):
        x = 540 + i * 55
        on = (i == 2)
        P.append(rect(x, 140, 44, 34, fill=(GRNBG if on else BG),
                      stroke=(FIELD if on else MUTED), sw=(1.8 if on else 1.3)))
        P.append(text(x + 22, 162, "s%d" % i, size=10.5, color=INK, bold=on))
    P.append(text(700, 205, "торкаємось лише поточного слота", size=11, color=FIELD, bold=True))
    P.append(text(700, 226, "тримає тисячі дешево", size=10.5, color=MUTED))

    P.append(line(W / 2, 65, W / 2, 250, color="#d0d5dd", sw=1.2, dash="5 4"))

    fr, w, h = textbox(W / 2, 330,
                       "Затримка довша за колесо — лічильник обертів або ярусні колеса.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/compare.svg", W, H, *P)


if __name__ == "__main__":
    fig_task_table()
    fig_scheduler_loop()
    fig_cooperative_limit()
    fig_soft_vs_hard()
    fig_system_tick()
    fig_toward_rtos()
    fig_wheel()
    fig_compare()
    print("OK: 8 figures -> img/")
