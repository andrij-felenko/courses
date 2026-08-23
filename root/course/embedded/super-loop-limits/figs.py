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


# ── D-1. Виведення затримки: подія чекає майже цілий оберт ────────────────────
# Ідея: подія трапилась одразу по кроку k; чекає решту оберту (k+1..n),
# початок наступного (1..k-1) і свій крок k → рівно один повний оберт.
def fig_latency_derivation():
    W, H = 940, 380
    P = [text(W / 2, 30, "Найгірша затримка реакції = сума ВСІХ кроків, а не найдовшого",
              size=16, bold=True),
         text(W / 2, 50, "подію обробляє крок k; вона трапилась одразу по тому, як цикл його проминув",
              size=11, color=MUTED, italic=True)]

    ax_y = 150
    P.append(arrow(60, ax_y, 890, ax_y, color=INK, sw=1.8))
    P.append(text(888, ax_y + 24, "час →", size=11, color=INK, bold=True))

    # два оберти поспіль; крок k підсвічено
    seg = [("1", GREYBG, MUTED, 70), ("k", GRNBG, FIELD, 70),
           ("k+1", GREYBG, MUTED, 90), ("…", BG, MUTED, 50), ("n", GREYBG, MUTED, 70)]
    # оберт 1: показуємо хвіст після k
    x = 70
    xs_k_first = None
    for lbl, fill, col, w in seg:
        P.append(rect(x, ax_y - 30, w, 30, fill=fill, stroke=col, sw=1.5))
        P.append(text(x + w / 2, ax_y - 10, lbl, size=10.5, color=col, bold=(lbl == "k")))
        if lbl == "k":
            xs_k_first = x + w / 2
        x += w + 4
    x += 14
    # оберт 2: голова до k
    xs_k_second = None
    for lbl, fill, col, w in seg:
        P.append(rect(x, ax_y - 30, w, 30, fill=fill, stroke=col, sw=1.5))
        P.append(text(x + w / 2, ax_y - 10, lbl, size=10.5, color=col, bold=(lbl == "k")))
        if lbl == "k":
            xs_k_second = x + w / 2
        x += w + 4

    # подія одразу після першого k
    ev_x = xs_k_first + 40
    P.append(line(ev_x, ax_y - 34, ev_x, ax_y + 70, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(ev_x, ax_y + 88, "подія (одразу по кроку k)", size=10.5, color=NEG, bold=True))
    # помічено на другому k
    P.append(line(xs_k_second, ax_y - 34, xs_k_second, ax_y + 44, color=NEG, sw=1.4, dash="4 3"))
    P.append(text(xs_k_second, ax_y + 62, "аж тут виконано крок k", size=10.5, color=NEG))
    P.append(arrow(ev_x, ax_y + 40, xs_k_second, ax_y + 40, color=POS, sw=1.7))
    P.append(text((ev_x + xs_k_second) / 2, ax_y + 32,
                  "чекання = один ПОВНИЙ оберт = Σ Cᵢ", size=11.5, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 350,
                       "L_worst = (C_{k+1}+…+Cₙ) + (C₁+…+C_{k−1}) + C_k = Σ Cᵢ = T_loop",
                       size=12.5, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/latency-derivation.svg", W, H, *P)


# ── D-2. Затинка: розкид тривалості оберту = jitter ──────────────────────────
# Ідея: згори рівні оберти → рівний ритм; знизу один довгий оберт зсуває момент
# періодичного кроку; різниця = jitter ≈ T_max − T_min.
def fig_jitter():
    W, H = 940, 400
    P = [text(W / 2, 30, "Затинка (jitter) = розкид тривалості оберту", size=17, bold=True),
         text(W / 2, 50, "періодичний крок спрацьовує тоді, коли цикл до нього дійде — а це плаває",
              size=11, color=MUTED, italic=True)]

    tick = "▲"
    # згори: рівні оберти
    y1 = 120
    P.append(text(70, y1 - 18, "рівні оберти:", size=11, color=FIELD, bold=True, anchor="start"))
    P.append(line(70, y1, 880, y1, color="#d0d5dd", sw=1.2))
    for i in range(6):
        x = 90 + i * 130
        P.append(rect(x, y1 - 14, 118, 28, fill=GRNBG, stroke=FIELD, sw=1.3))
        P.append(text(x + 59, y1 + 5, "оберт", size=9.5, color=FIELD))
        P.append(text(x + 118, y1 + 32, tick, size=12, color=FIELD, bold=True))
    P.append(text(475, y1 + 56, "момент кроку рівний → ритм чистий", size=10.5, color=FIELD, bold=True))

    # знизу: один довгий оберт
    y2 = 250
    P.append(text(70, y2 - 18, "один довгий оберт:", size=11, color=POS, bold=True, anchor="start"))
    P.append(line(70, y2, 880, y2, color="#d0d5dd", sw=1.2))
    widths = [118, 118, 300, 118, 118]     # третій — роздутий блокуванням
    x = 90
    xs_ticks = []
    for i, w in enumerate(widths):
        fill = REDBG if w > 150 else GREYBG
        col = POS if w > 150 else MUTED
        P.append(rect(x, y2 - 14, w, 28, fill=fill, stroke=col, sw=1.6 if w > 150 else 1.3))
        lbl = "блокування!" if w > 150 else "оберт"
        P.append(text(x + w / 2, y2 + 5, lbl, size=9.5, color=col, bold=(w > 150)))
        P.append(text(x + w, y2 + 32, tick, size=12, color=col, bold=True))
        xs_ticks.append(x + w)
        x += w + 4

    # стрілка затинки між рівним і зсунутим моментом
    ideal_x = xs_ticks[1] + 118 + 4       # де тік мав би бути без роздування
    real_x = xs_ticks[2]
    P.append(line(ideal_x, y2 + 20, ideal_x, y2 + 58, color=NEG, sw=1.2, dash="4 3"))
    P.append(arrow(ideal_x, y2 + 52, real_x, y2 + 52, color=POS, sw=1.7))
    P.append(text((ideal_x + real_x) / 2 + 20, y2 + 46, "затинка", size=11, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 372,
                       "jitter ≈ T_max − T_min = час найдовшого «поганого» оберту.\n"
                       "Для звуку й мотора болить саме цей розкид, а не середня швидкість.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/jitter.svg", W, H, *P)


# ── D-3. Дрейф способу Б проти планової сітки способу А ───────────────────────
# Ідея: спосіб А тримає жорстку сітку 0,P,2P…; спосіб Б відлічує від фактичного
# (запізнілого) спрацювання, тож інтервали повзуть управо — дрейф.
def fig_millis_drift():
    W, H = 940, 380
    P = [text(W / 2, 30, "Два способи рахувати період: сітка (А) проти дрейфу (Б)", size=16, bold=True)]

    ax = lambda y: (P.append(arrow(70, y, 880, y, color=INK, sw=1.6)),
                    P.append(text(878, y + 22, "час →", size=10.5, color=INK, bold=True)))

    P.append(text(70, 90, "Спосіб А: next += PERIOD — жорстка сітка", size=12, color=FIELD,
                  bold=True, anchor="start"))
    y1 = 120
    ax(y1)
    for i in range(6):
        x = 90 + i * 150
        P.append(line(x, y1 - 8, x, y1 + 8, color=FIELD, sw=2))
        P.append(text(x, y1 + 26, "%d·P" % i, size=10, color=FIELD, bold=True))
    P.append(text(475, y1 + 52, "планові моменти прибиті до сітки — довгострокова частота точна",
                  size=10.5, color=FIELD))

    P.append(text(70, 220, "Спосіб Б: last = millis() — відлік від фактичного спрацювання",
                  size=12, color=POS, bold=True, anchor="start"))
    y2 = 250
    ax(y2)
    # кроки з наростаючим зсувом
    off = 0
    for i in range(6):
        x = 90 + i * 150 + off
        P.append(line(x, y2 - 8, x, y2 + 8, color=POS, sw=2))
        # тінь ідеального моменту
        xi = 90 + i * 150
        if i > 0:
            P.append(line(xi, y2 - 6, xi, y2 + 6, color=MUTED, sw=1, dash="2 2"))
        off += 12          # щоразу трохи пізніше — накопичення
    P.append(text(475, y2 + 40, "кожне спрацювання трохи пізніше → зсуви накопичуються",
                  size=10.5, color=POS, bold=True))
    P.append(text(475, y2 + 58, "(сірі риски — де момент мав би бути)", size=9.5, color=MUTED, italic=True))

    fr, w, h = textbox(W / 2, 352,
                       "Для періодичного бери А (сітка); Б повільно тікає — дрейф росте з часом.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/millis-drift.svg", W, H, *P)


# ── D-4. Стани множаться в декартів добуток ──────────────────────────────────
# Ідея: три окремі машини (a,b,c) — сума a+b+c; переплетені в одному циклі —
# добуток a×b×c: сітка комбінованих станів.
def fig_state_product():
    W, H = 940, 420
    P = [text(W / 2, 30, "Переплетені справи: стани не додаються, а множаться", size=17, bold=True)]

    # ліворуч — три окремі маленькі автомати (сума)
    P.append(fitbox(60, 70, 360, 30, "ОКРЕМО — тримаєш суму a + b + c", size=12, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    labels = [("A", FIELD), ("B", NEG), ("C", AMBER)]
    for i, (lb, col) in enumerate(labels):
        cy = 140 + i * 80
        for j in range(3):
            cx = 110 + j * 70
            P.append(circle(cx, cy, 16, fill=BG, stroke=col, sw=1.5))
            P.append(text(cx, cy + 4, "%s%d" % (lb, j), size=9, color=col, bold=True))
            if j < 2:
                P.append(arrow(cx + 16, cy, cx + 54, cy, color=col, sw=1.2))
    P.append(text(230, 370, "3 прості автомати — 3+3+3 = 9 станів у голові", size=10.5,
                  color=FIELD, bold=True))

    # праворуч — добуток: сітка a×b (зріз), із поміткою ×c
    P.append(fitbox(520, 70, 360, 30, "РАЗОМ — простір станів a × b × c", size=12, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    gx, gy, cell = 560, 130, 44
    for r in range(3):
        for c in range(3):
            x = gx + c * cell
            y = gy + r * cell
            P.append(rect(x, y, cell - 4, cell - 4, fill=REDBG, stroke=POS, sw=1.2))
            P.append(text(x + (cell - 4) / 2, y + (cell - 4) / 2 + 4,
                          "A%dB%d" % (r, c), size=9, color=POS))
    P.append(text(gx + 1.5 * cell, gy + 3 * cell + 22,
                  "лише зріз A×B = 9; × C = 27 комбінацій", size=10.5, color=POS, bold=True))
    P.append(text(gx + 1.5 * cell, gy + 3 * cell + 42,
                  "додав 4-ту справу → ×ще раз", size=10.5, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 398,
                       "Кожна нова справа МНОЖИТЬ простір станів — комбінаторний вибух; межа не машини, а людини.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/state-product.svg", W, H, *P)


# ── D-5. Чого хочемо: задачі з власним стеком + витискний планувальник ────────
# Ідея: три задачі, кожна з ВЛАСНИМ стеком (стан у точці виконання); під ними
# планувальник, що зберігає контекст і перериває заради пріоритету.
def fig_what_we_want_d():
    W, H = 940, 420
    P = [text(W / 2, 30, "Чого хочемо: окремий стек на справу + право перервати", size=16, bold=True),
         text(W / 2, 50, "стан живе у точці виконання (не в ручній змінній); планувальник керує часом",
              size=11, color=MUTED, italic=True)]

    cards = [
        ("Задача: керування", POS, REDBG, ["крок → чекай", "(пріоритет ↑)"], "стек"),
        ("Задача: давач", NEG, BLUEBG, ["читай → чекай", "повтори"], "стек"),
        ("Задача: зв'язок", FIELD, GRNBG, ["прийми → відповідж", "чекай"], "стек"),
    ]
    xs = [80, 370, 660]
    for (title_, col, fill, body, stk), x in zip(cards, xs):
        P.append(rect(x, 80, 200, 120, fill=BG, stroke=col, sw=1.8))
        P.append(fitbox(x, 80, 200, 26, title_, size=11, bold=True, color=col, fill=fill, stroke=col))
        P.append(mtext(x + 100, 128, body, size=10.5, color=INK))
        # власний стек як окрема плашка
        P.append(rect(x + 55, 165, 90, 24, fill=fill, stroke=col, sw=1.2))
        P.append(text(x + 100, 181, "власний " + stk, size=9.5, color=col, bold=True))
        P.append(arrow(x + 100, 200, x + 100, 258, color=MUTED, sw=1.4))

    fr, w, h = textbox(W / 2, 283,
                       "ПЛАНУВАЛЬНИК: зберігає/відновлює контекст, перериває менш пріоритетну заради термінової",
                       size=12, bold=True, color=AMBER, fill=AMBERBG, stroke=AMBER)
    P.append(fr)

    fr, w, h = textbox(W / 2, 360,
                       "Добуток станів розпадається назад на суму (стан — у стеку кожної задачі),\n"
                       "блокування однієї не морозить інших, найгіршій затримці можна поставити стелю.",
                       size=11.5, bold=True, fill=GRNBG, stroke=FIELD)
    P.append(fr)
    render("img/what-we-want-d.svg", W, H, *P)


# ── math-вставка: три стелі планованості (U≤1, RMS, EDF) ─────────────────────
# Ідея: три горизонтальні «планки» завантаженості одна над одною —
# фізична стеля U=1 (=EDF), сувора межа RMS ln2≈0.693, і сіра зона між ними,
# де EDF ще встигає, а фіксовані пріоритети вже можуть зірватись.
def fig_three_ceilings():
    W, H = 940, 420
    P = [text(W / 2, 30, "Три стелі завантаженості: скільки процесора можна віддати роботі", size=17, bold=True),
         text(W / 2, 50, "одна періодична робота — частка Cᵢ/Tᵢ; сума часток U = Σ Cᵢ/Tᵢ",
              size=11, color=MUTED, italic=True)]

    # вертикальна шкала U від 0 (низ) до 1 (верх)
    x0, y_top, y_bot = 150, 90, 340
    span = y_bot - y_top
    bar_w = 560

    def y_of(u):
        return y_bot - u * span

    # рамка-шкала
    P.append(line(x0, y_top, x0, y_bot, color=INK, sw=1.6))
    P.append(text(x0 - 12, y_top - 14, "U", size=13, color=INK, bold=True, anchor="end"))
    for u, lab in ((0.0, "0"), (0.693, "ln2 ≈ 0.693"), (1.0, "1.0")):
        yy = y_of(u)
        P.append(line(x0 - 6, yy, x0, yy, color=INK, sw=1.4))
        P.append(text(x0 - 12, yy + 4, lab, size=11, color=INK, anchor="end", bold=(u != 0)))

    # зона «завжди встигає будь-хто» (0..0.693) — зелена
    P.append(rect(x0, y_of(0.693), bar_w, y_of(0) - y_of(0.693), fill=GRNBG, stroke=FIELD, sw=1.2))
    P.append(text(x0 + bar_w / 2, (y_of(0) + y_of(0.693)) / 2 + 4,
                  "тут устигає навіть RMS (і будь-хто розумніший)", size=12, color=FIELD, bold=True))

    # сіра зона (0.693..1.0) — EDF так, фіксовані пріоритети «як пощастить»
    P.append(rect(x0, y_of(1.0), bar_w, y_of(0.693) - y_of(1.0), fill=GREYBG, stroke=MUTED, sw=1.2))
    P.append(mtext(x0 + bar_w / 2, y_of(0.85) - 6,
                   ["EDF ще гарантовано встигає;", "RMS — лише «якщо пощастить» з періодами"],
                   size=11.5, color=MUTED, bold=True))

    # червона лінія-стеля U=1 (фізика)
    P.append(line(x0, y_of(1.0), x0 + bar_w, y_of(1.0), color=POS, sw=2.6))
    P.append(text(x0 + bar_w + 12, y_of(1.0) + 4, "U = 1 — фізична стеля", size=11.5, color=POS, bold=True, anchor="start"))
    P.append(text(x0 + bar_w + 12, y_of(1.0) + 22, "(і точна межа EDF)", size=10.5, color=NEG, anchor="start"))

    # синя лінія-межа RMS
    P.append(line(x0, y_of(0.693), x0 + bar_w, y_of(0.693), color=NEG, sw=2.2, dash="7,5"))
    P.append(text(x0 + bar_w + 12, y_of(0.693) + 4, "межа RMS: n(2^(1/n)−1)", size=11.5, color=NEG, bold=True, anchor="start"))

    # зона понад 1 — ніхто
    P.append(text(x0 + bar_w / 2, y_of(1.0) - 14, "U > 1 — не встигає ніхто (робота накопичується)",
                  size=11, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 392,
                       "EDF викуповує всю смугу до фізичної стелі; фіксовані пріоритети гарантують лише до ln2 ≈ 69 %.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/util-three-ceilings.svg", W, H, *P)


# ── math-вставка: крива межі RMS n(2^(1/n)−1) → ln2 ──────────────────────────
# Ідея: зі зростанням числа задач гарантована межа RMS падає з 1.0 (n=1)
# і сідає на асимптоту ln2≈0.693; EDF тримає рівну 1.0.
def fig_rms_curve():
    import math
    W, H = 940, 430
    P = [text(W / 2, 30, "Гарантована межа RMS падає з ростом числа задач", size=17, bold=True),
         text(W / 2, 50, "U(n) = n·(2^(1/n) − 1) сідає на ln2 ≈ 0.693; EDF тримає рівну 1.0",
              size=11, color=MUTED, italic=True)]

    # осі
    ox, oy = 120, 340          # початок координат (лівий низ)
    x_len, y_len = 700, 240
    n_max = 12
    u_lo, u_hi = 0.6, 1.02     # діапазон по вертикалі

    def px(n):
        return ox + (n - 1) / (n_max - 1) * x_len

    def py(u):
        return oy - (u - u_lo) / (u_hi - u_lo) * y_len

    # осі й підписи
    P.append(arrow(ox, oy, ox + x_len + 20, oy, color=INK, sw=1.6))
    P.append(arrow(ox, oy, ox, oy - y_len - 12, color=INK, sw=1.6))
    P.append(text(ox + x_len + 20, oy + 26, "n — число задач", size=12, color=INK, bold=True))
    P.append(text(ox - 14, oy - y_len - 8, "U", size=13, color=INK, bold=True, anchor="end"))

    # горизонтальні орієнтири
    for u in (0.693, 1.0):
        yy = py(u)
        P.append(line(ox, yy, ox + x_len, yy, color="#d0d5dd", sw=1.0, dash="3,4"))
        P.append(text(ox - 12, yy + 4, ("ln2" if u < 1 else "1.0"), size=11, color=INK, anchor="end", bold=True))

    # мітки n
    for n in (1, 2, 3, 5, 8, 12):
        xx = px(n)
        P.append(line(xx, oy, xx, oy + 6, color=INK, sw=1.2))
        P.append(text(xx, oy + 22, str(n), size=11, color=INK))

    # EDF — рівна лінія 1.0
    P.append(line(px(1), py(1.0), px(n_max), py(1.0), color=FIELD, sw=2.6))
    P.append(text(px(n_max) - 4, py(1.0) - 10, "EDF — завжди 1.0", size=12, color=FIELD, bold=True, anchor="end"))

    # RMS-крива
    pts = []
    for i in range(0, (n_max - 1) * 6 + 1):
        n = 1 + i / 6.0
        u = n * (2 ** (1.0 / n) - 1)
        pts.append((px(n), py(u)))
    poly = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, NEG))

    # точки-значення для кількох n
    for n in (1, 2, 3, 5):
        u = n * (2 ** (1.0 / n) - 1)
        P.append(circle(px(n), py(u), 4, fill=NEG, stroke=BG, sw=1.5))
        P.append(text(px(n) + 8, py(u) - 8, "%.3f" % u, size=10.5, color=NEG, bold=True, anchor="start"))
    P.append(text(px(9), py(0.70) + 2, "RMS: n(2^(1/n)−1)", size=12, color=NEG, bold=True, anchor="start"))

    # сіра зона між кривою й 1.0 (те, що RMS лишає на столі при великому n)
    P.append(mtext(px(7.5), py(0.86),
                   ["цю смугу RMS", "лишає на столі —", "EDF її забирає"],
                   size=10.5, color=MUTED, bold=True, anchor="middle"))

    fr, w, h = textbox(W / 2, 405,
                       "Що більше задач, то нижча гарантія фіксованих пріоритетів — але ніколи не нижче 69.3 %.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/rms-bound-curve.svg", W, H, *P)


# ── math-вставка: той самий набір — RMS встигає, super-loop зриває ────────────
# Ідея: дві доріжки часу. Згори — витісняючий RMS: короткий терміновий крок
# перериває довгий і встигає до дедлайну. Знизу — super-loop: довгий крок
# монолітний, терміновий чекає його кінця й зриває дедлайн.
def fig_preempt_vs_superloop():
    W, H = 960, 500
    P = [text(W / 2, 30, "Один набір задач: витісняючий RMS встигає, super-loop зриває", size=17, bold=True),
         text(W / 2, 50, "τ_A: C=1, T=4 (терміновий) · τ_B: C=6, T=12 (довгий) — U = 1/4 + 6/12 = 0.75 < ln2",
              size=11, color=MUTED, italic=True)]

    x0, x_len = 90, 800
    t_max = 12.0

    def tx(t):
        return x0 + t / t_max * x_len

    # сітка часу
    for t in range(0, 13):
        xx = tx(t)
        P.append(line(xx, 78, xx, 430, color="#eef2f7", sw=1.0))
        P.append(text(xx, 448, str(t), size=10, color=MUTED))
    P.append(text(x0 + x_len + 18, 448, "мс", size=10.5, color=MUTED, anchor="start"))

    # дедлайни τ_A (стрілки вниз на 4, 8, 12)
    lane1_y = 150
    lane2_y = 320

    def deadline_marks(y):
        for d in (4, 8, 12):
            P.append(line(tx(d), y - 46, tx(d), y - 10, color=POS, sw=1.4, dash="2,3"))
            P.append(text(tx(d), y - 50, "дедлайн A", size=9, color=POS, anchor="middle"))

    # ── доріжка 1: витісняючий RMS ──
    P.append(text(x0, lane1_y - 62, "Витісняючий RMS (τ_A має вищий пріоритет — коротший період)",
                  size=12.5, color=FIELD, bold=True, anchor="start"))
    deadline_marks(lane1_y)
    P.append(line(x0, lane1_y, tx(12), lane1_y, color="#d0d5dd", sw=1.2))

    # A біжить на 0..1, 4..5, 8..9 (перериває B)
    for a0 in (0, 4, 8):
        P.append(rect(tx(a0), lane1_y - 26, tx(a0 + 1) - tx(a0), 26, fill=REDBG, stroke=POS, sw=1.6))
        P.append(text((tx(a0) + tx(a0 + 1)) / 2, lane1_y - 8, "A", size=11, color=POS, bold=True))
    # B біжить у щілинах: 1..4 (3), 5..8 (3) => 6 всього, кінчає на 8, до дедлайну 12
    for b0, b1 in ((1, 4), (5, 8)):
        P.append(rect(tx(b0), lane1_y - 26, tx(b1) - tx(b0), 26, fill=BLUEBG, stroke=NEG, sw=1.4))
        P.append(text((tx(b0) + tx(b1)) / 2, lane1_y - 8, "B (перервано)", size=10, color=NEG, bold=True))
    P.append(text(tx(8) + 6, lane1_y + 20, "✓ B готове до 8, обидва дедлайни виконано", size=11, color=FIELD, bold=True, anchor="start"))

    # ── доріжка 2: super-loop ──
    P.append(text(x0, lane2_y - 62, "Super-loop (крок B монолітний, перервати нема кому)",
                  size=12.5, color=POS, bold=True, anchor="start"))
    deadline_marks(lane2_y)
    P.append(line(x0, lane2_y, tx(12), lane2_y, color="#d0d5dd", sw=1.2))

    # A на 0..1, далі B суцільно 1..7 (6 мс), A наступний хоче о 4 — але чекає до 7
    P.append(rect(tx(0), lane2_y - 26, tx(1) - tx(0), 26, fill=REDBG, stroke=POS, sw=1.6))
    P.append(text((tx(0) + tx(1)) / 2, lane2_y - 8, "A", size=11, color=POS, bold=True))
    P.append(rect(tx(1), lane2_y - 26, tx(7) - tx(1), 26, fill=BLUEBG, stroke=NEG, sw=1.8))
    P.append(text((tx(1) + tx(7)) / 2, lane2_y - 8, "B — суцільні 6 мс, НЕ перервати", size=11, color=NEG, bold=True))
    # промах: A мав о 4, побіг о 7
    P.append(rect(tx(7), lane2_y - 26, tx(8) - tx(7), 26, fill=REDBG, stroke=POS, sw=1.6))
    P.append(text((tx(7) + tx(8)) / 2, lane2_y - 8, "A", size=11, color=POS, bold=True))
    # стрілка запізнення від 4 до 7
    P.append(arrow(tx(4), lane2_y + 20, tx(7), lane2_y + 20, color=POS, sw=1.6))
    P.append(text(tx(5.5), lane2_y + 36, "A чекав до 7 — дедлайн о 4 ЗІРВАНО", size=11, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 478,
                       "Однакове U = 0.75. Різниця не в завантаженні, а в праві перервати довгий крок заради термінового.",
                       size=11.5, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/preempt-vs-superloop.svg", W, H, *P)


if __name__ == "__main__":
    fig_blocking()
    fig_responsiveness()
    fig_millis_limit()
    fig_state_explosion()
    fig_no_priority()
    fig_what_we_want()
    fig_latency_derivation()
    fig_jitter()
    fig_millis_drift()
    fig_state_product()
    fig_what_we_want_d()
    fig_three_ceilings()
    fig_rms_curve()
    fig_preempt_vs_superloop()
    print("OK: 14 figures -> img/")
