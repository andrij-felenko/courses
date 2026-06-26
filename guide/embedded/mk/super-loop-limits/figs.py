# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Межі super-loop».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
REDBG   = "#fdecea"
GREYBG  = "#eef2f7"


# ── 1. Блокування: одна пауза заморожує весь цикл ────────────────────────────
# Ідея: на осі часу процесора блокувальний крок — суцільна червона смуга,
# під час якої все інше («не блимає, не помічено, не оновлено») мертве.
def fig_blocking():
    W, H = 940, 360
    P = [text(W / 2, 30, "Блокування: одна пауза заморожує весь цикл", size=17, bold=True),
         text(W / 2, 50, "будь-який виклик, що чекає (delay, повільне читання, мережа), спиняє все інше",
              size=11, color=MUTED, italic=True)]

    ax_y = 150
    P.append(text(70, ax_y - 22, "час процесора →", size=11, color=INK, bold=True, anchor="start"))
    P.append(line(70, ax_y, 880, ax_y, color="#d0d5dd", sw=1.2))

    P.append(rect(70, ax_y, 90, 34, fill=GRNBG, stroke=FIELD, sw=1.4))
    P.append(text(115, ax_y + 22, "робота", size=10, color=FIELD, bold=True))
    P.append(rect(165, ax_y, 520, 34, fill=REDBG, stroke=POS, sw=1.8))
    P.append(text(425, ax_y + 22, "delay(1000) / повільне читання — чекаємо", size=12, color=POS, bold=True))
    P.append(rect(690, ax_y, 90, 34, fill=GRNBG, stroke=FIELD, sw=1.4))
    P.append(text(735, ax_y + 22, "робота", size=10, color=FIELD, bold=True))
    P.append(text(425, ax_y - 12, "ціла секунда — а пристрій «мертвий»", size=10, color=POS, bold=True))

    for i, s in enumerate(("LED не блимає", "кнопку не помічено", "екран не оновлюється")):
        P.append(text(210, ax_y + 70 + i * 22, "✗ " + s, size=11, color=POS, bold=True, anchor="start"))
    P.append(mtext(560, ax_y + 70, ["процесор простоює,", "та зайнятий очікуванням —", "користі нуль"],
                   size=10.5, color=MUTED, anchor="start"))

    fr, w, h = textbox(W / 2, 330,
                       "У super-loop усе йде по черзі: поки один крок чекає, решта просто не виконується.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/blocking.svg", W, H, *P)


# ── 2. Чуйність = тривалість найдовшого проходу ──────────────────────────────
# Ідея: подія трапилась на початку довгого кроку, помічена аж наприкінці проходу;
# стрілка очікування = найгірша затримка реакції.
def fig_responsiveness():
    W, H = 940, 360
    P = [text(W / 2, 30, "Чуйність = тривалість найдовшого проходу циклу", size=17, bold=True),
         text(W / 2, 50, "подію помітять лише тоді, коли цикл дійде до її кроку",
              size=11, color=MUTED, italic=True)]

    ax_y = 150
    P.append(arrow(70, ax_y, 880, ax_y, color=INK, sw=1.8))
    P.append(text(880, ax_y + 24, "час →", size=12, color=INK, bold=True))

    P.append(rect(90, ax_y - 34, 70, 34, fill=GRNBG, stroke=FIELD, sw=1.5))
    P.append(text(125, ax_y - 13, "крок A", size=10.5, color=FIELD, bold=True))
    P.append(rect(170, ax_y - 34, 430, 34, fill=REDBG, stroke=POS, sw=1.7))
    P.append(text(385, ax_y - 13, "довгий крок B", size=12, color=POS, bold=True))
    P.append(rect(610, ax_y - 34, 70, 34, fill=BLUEBG, stroke=NEG, sw=1.5))
    P.append(text(645, ax_y - 13, "крок C", size=10.5, color=NEG, bold=True))

    P.append(line(180, ax_y + 6, 180, ax_y + 64, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(180, ax_y + 82, "кнопку натиснули", size=10.5, color=NEG, bold=True))
    P.append(line(610, ax_y + 6, 610, ax_y + 44, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(610, ax_y + 62, "аж тепер помічено", size=10.5, color=NEG))
    P.append(arrow(190, ax_y + 40, 600, ax_y + 40, color=POS, sw=1.7))
    P.append(text(395, ax_y + 32, "затримка реакції (найгірший випадок)", size=11, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 330,
                       "Найгірша затримка дорівнює найдовшому проходу: більше роботи в циклі — млявіший пристрій.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/responsiveness.svg", W, H, *P)


# ── 3. millis рятує, лише якщо все можна «нарізати» ──────────────────────────
# Ідея: ліворуч — справа, що ріжеться на шматочки; праворуч — суцільний блок,
# який не поділиш (мережа, SD, повільний давач).
def fig_millis_limit():
    W, H = 940, 380
    P = [text(W / 2, 30, "Патерн millis працює, лише якщо все можна «нарізати»", size=17, bold=True)]

    # ліворуч — порізана справа
    P.append(fitbox(70, 75, 360, 32, "МОЖНА ПОРІЗАТИ — блимання, лічба", size=12.5, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    for i in range(6):
        x = 90 + i * 55
        P.append(rect(x, 140, 44, 34, fill=GRNBG, stroke=FIELD, sw=1.4))
        P.append(text(x + 22, 162, "•", size=14, color=FIELD, bold=True))
    P.append(text(250, 205, "крихітні шматочки по одному щооберту", size=10.5, color=FIELD, bold=True))
    P.append(text(250, 226, "між ними цикл займається іншими", size=10, color=MUTED))

    # праворуч — суцільний блок
    P.append(fitbox(520, 75, 360, 32, "НЕ ПОРІЗАТИ — мережа, SD, давач", size=12.5, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    P.append(rect(540, 140, 320, 34, fill=REDBG, stroke=POS, sw=1.8))
    P.append(text(700, 162, "блокує зсередини — суцільний блок", size=11, color=POS, bold=True))
    P.append(text(700, 205, "ділити нíчого — хіба переписати з нуля", size=10.5, color=POS, bold=True))
    P.append(text(700, 226, "до того ж потік один: довгий шматок тримає решту", size=10, color=MUTED))

    P.append(line(W / 2, 65, W / 2, 250, color="#d0d5dd", sw=1.2, dash="5 4"))

    fr, w, h = textbox(W / 2, 335,
                       "millis лише вручну імітує одночасність; під нею завжди той самий єдиний цикл по черзі.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/millis-limit.svg", W, H, *P)


# ── 4. Проста послідовність вивертається в плутану машину станів ─────────────
# Ідея: ліворуч — лінійна «зроби-чекай-зроби» згори вниз; праворуч — клубок станів.
def fig_state_explosion():
    import math
    W, H = 940, 420
    P = [text(W / 2, 30, "Проста послідовність вивертається у плутану машину станів", size=17, bold=True)]

    # ліворуч — лінійна думка
    P.append(fitbox(70, 70, 300, 30, "ЯК ХОЧЕТЬСЯ ДУМАТИ", size=12.5, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    steps = ["увімкни мотор", "почекай 2 с", "вимкни мотор"]
    for i, s in enumerate(steps):
        y = 130 + i * 70
        fr, w, h = textbox(220, y, s, size=12, bold=True, color=INK, fill=BG, stroke=FIELD)
        P.append(fr)
        if i < len(steps) - 1:
            P.append(arrow(220, y + h / 2, 220, y + 70 - h / 2, color=FIELD, sw=1.6))
    P.append(text(220, 350, "читається згори вниз", size=10.5, color=MUTED))

    # праворуч — клубок станів
    P.append(fitbox(570, 70, 300, 30, "НА ЩО ПЕРЕТВОРЮЄТЬСЯ", size=12.5, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    nodes = {"S0": (640, 150), "S1": (790, 150), "S2": (860, 250),
             "S3": (715, 300), "S4": (600, 250)}
    order = ["S0", "S1", "S2", "S3", "S4"]
    for i, a in enumerate(order):
        b = order[(i + 1) % len(order)]
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        P.append(arrow(x1, y1, x2, y2, color=MUTED, sw=1.3))
    # одна «зайва» плутана дуга
    P.append(arrow(nodes["S2"][0], nodes["S2"][1], nodes["S0"][0], nodes["S0"][1], color=POS, sw=1.3))
    for n, (x, y) in nodes.items():
        P.append(circle(x, y, 20, fill=REDBG, stroke=POS, sw=1.6))
        P.append(text(x, y + 4, n, size=10.5, color=POS, bold=True))
    P.append(text(730, 360, "прапорці, таймери, переходи — і це лише ОДНА справа", size=10, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 398,
                       "Кожна нова справа не додає коду, а множить заплутаність — це межа не машини, а людини.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/state-explosion.svg", W, H, *P)


# ── 5. Немає пріоритетів: усе строго в порядку коду ─────────────────────────
# Ідея: цикл перебирає рутину в порядку коду; терміновий «аварійний стоп» —
# останній у списку й мусить чекати всіх перед ним.
def fig_no_priority():
    W, H = 940, 380
    P = [text(W / 2, 30, "Немає пріоритетів: усе строго в порядку коду", size=17, bold=True)]

    items = [("оновити екран", MUTED, BG), ("записати лог", MUTED, BG),
             ("порахувати", MUTED, BG), ("аварійний стоп (терміново!)", POS, REDBG)]
    x0 = 150
    for i, (lbl, col, fill) in enumerate(items):
        x = x0 + i * 195
        P.append(rect(x, 120, 175, 46, fill=fill, stroke=col, sw=1.8 if col == POS else 1.3))
        P.append(fitbox(x, 120, 175, 46, lbl, size=11, bold=(col == POS), color=col, fill=fill,
                        stroke=col, sw=1.8 if col == POS else 1.3))
        if i < len(items) - 1:
            P.append(arrow(x + 175, 143, x + 195, 143, color=MUTED, sw=1.5))

    P.append(text(150 + 3 * 195 + 87, 200, "чекає, доки відпрацює вся рутина перед ним",
                  size=11, color=POS, bold=True))
    P.append(line(150 + 3 * 195 + 87, 168, 150 + 3 * 195 + 87, 188, color=POS, sw=1.4, dash="4 3"))

    fr, w, h = textbox(W / 2, 300,
                       "Сказати «це важливіше, виконай негайно» super-loop не вміє.\n"
                       "Саме це дає операційна система — пріоритет однієї роботи над іншою.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/no-priority.svg", W, H, *P)


# ── 6. Чого ми хочемо: кожна справа — проста програма, планувальник перемикає ─
# Ідея: три самостійні «програми» з власними «чекай», під ними планувальник,
# що перемикає між ними — кожна гадає, що володіє процесором сама.
def fig_what_we_want():
    W, H = 940, 400
    P = [text(W / 2, 30, "Чого ми хочемо: кожна справа — окрема проста програма", size=17, bold=True),
         text(W / 2, 50, "писати послідовно, ніби сама на машині, а перемикання довірити планувальникові",
              size=11, color=MUTED, italic=True)]

    cards = [
        ("Задача: блимати", FIELD, GRNBG, ["увімкни → чекай", "вимкни → чекай"]),
        ("Задача: давач", NEG, BLUEBG, ["читай → чекай", "повтори"]),
        ("Задача: зв'язок", AMBER, AMBERBG, ["прийми → відповідж", "чекай"]),
    ]
    xs = [80, 370, 660]
    for (title_, col, fill, body), x in zip(cards, xs):
        P.append(rect(x, 80, 200, 110, fill=BG, stroke=col, sw=1.8))
        P.append(fitbox(x, 80, 200, 28, title_, size=11.5, bold=True, color=col, fill=fill, stroke=col))
        P.append(mtext(x + 100, 132, body, size=10.5, color=INK))
        P.append(text(x + 100, 178, "з власними «чекай»", size=9.5, color=MUTED, italic=True))
        P.append(arrow(x + 100, 190, x + 100, 250, color=MUTED, sw=1.4))

    fr, w, h = textbox(W / 2, 275,
                       "ПЛАНУВАЛЬНИК перемикає між задачами — кожна гадає, що володіє процесором сама",
                       size=12, bold=True, color=AMBER, fill=AMBERBG, stroke=AMBER)
    P.append(fr)

    fr, w, h = textbox(W / 2, 350,
                       "Те, що колись дало багатьом людям ілюзію особистого комп'ютера (поділ часу),\n"
                       "тут дає нашим справам ілюзію особистого процесора — на одному чипі.",
                       size=11.5, bold=True, fill=GRNBG, stroke=FIELD)
    P.append(fr)
    render("img/what-we-want.svg", W, H, *P)


if __name__ == "__main__":
    fig_blocking()
    fig_responsiveness()
    fig_millis_limit()
    fig_state_explosion()
    fig_no_priority()
    fig_what_we_want()
    print("OK: 6 figures -> img/")
