# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
GREY = "#9aa1ab"
GREENBG = "#eefaf1"
GREYBG = "#f0f1f3"


# ── 1. Ідеальна машина проти реальної; борг як вертикальна відстань ──────────
def fig_ideal_vs_real():
    W, H = 1020, 620
    p = []

    X0, X1 = 110.0, 920.0          # вісь часу
    SLOTS = 9
    dx = (X1 - X0) / SLOTS
    YB = 520.0                     # нуль отриманого часу
    unit = 95.0                    # висота однієї повної частки

    order = ["A", "B", "C"]
    col = {"A": POS, "B": NEG, "C": FIELD}

    # ── смуга «хто біжить» ───────────────────────────────────────────────────
    p.append(text(X0 - 18, 92, "хто", size=12, color=MUTED, anchor="end"))
    p.append(text(X0 - 18, 108, "біжить", size=12, color=MUTED, anchor="end"))
    for i in range(SLOTS):
        name = order[i % 3]
        p.append(rect(X0 + i * dx + 3, 74, dx - 6, 44,
                      fill=SOFT, stroke=col[name], sw=1.8, rx=5))
        p.append(text(X0 + i * dx + dx / 2, 102, name, size=17,
                      color=col[name], bold=True))

    # ── осі ──────────────────────────────────────────────────────────────────
    p.append(line(X0, YB, X1 + 22, YB, color=INK, sw=1.6))
    p.append(line(X0, YB, X0, 176, color=INK, sw=1.6))
    p.append(text(X1 + 26, YB + 22, "реальний час", size=12,
                  color=MUTED, anchor="end"))
    p.append(text(X0 - 18, 196, "отриманий", size=12, color=MUTED, anchor="end"))
    p.append(text(X0 - 18, 212, "час", size=12, color=MUTED, anchor="end"))

    for i in range(SLOTS + 1):
        p.append(line(X0 + i * dx, YB, X0 + i * dx, YB + 7, color=MUTED, sw=1.1))

    # ── ідеальна пряма: за 9 відрізків кожен дістає 3 ────────────────────────
    p.append(line(X0, YB, X1, YB - 3 * unit, color=GREY, sw=2.2, dash="7 5"))
    p.append(text(X1 - 6, YB - 3 * unit - 16, "ідеальна машина: по ⅓ швидкості кожній",
                  size=12, color=GREY, anchor="end"))

    # ── сходинки трьох задач ────────────────────────────────────────────────
    # за 9 слотів усі три задачі рівно приходять до однієї висоти (по 3 повні
    # частки кожній) — тож підписи в кінці збігаються й потребують рознесення
    # по вертикалі з короткими лідер-лініями до спільної точки.
    end_y = None
    for k, name in enumerate(order):
        got = 0.0
        x = X0
        for i in range(SLOTS):
            runs = (i % 3 == k)
            y = YB - got * unit
            if runs:
                p.append(line(x, y, x + dx, y - unit, color=col[name], sw=2.6))
                got += 1.0
            else:
                p.append(line(x, y, x + dx, y, color=col[name], sw=2.6))
            x += dx
        end_y = YB - got * unit
        ly = end_y + 5 + (k - 1) * 22
        p.append(line(X1 + 6, end_y, X1 + 22, ly - 4, color=col[name], sw=1.1, dash="2 3"))
        p.append(text(X1 + 26, ly, name, size=15,
                      color=col[name], bold=True, anchor="start"))

    # ── борг: задача C у момент, коли ще жодного разу не бігла ───────────────
    xc = X0 + 2 * dx
    p.append(line(xc, YB, xc, YB - (2.0 / 3.0) * unit, color=INK, sw=2.4))
    p.append(circle(xc, YB - (2.0 / 3.0) * unit, 4, fill=INK, stroke=INK, sw=1))
    p.append(circle(xc, YB, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(fitbox(xc - 132, YB + 40, 264, 46,
                    "борг перед C: належало ⅔,\nотримано 0 — черга її",
                    size=12, fill=GREENBG, stroke=FIELD, sw=1.5))

    # ── випередження: задача A після свого першого відрізка ──────────────────
    xa = X0 + 1 * dx
    p.append(line(xa, YB - unit, xa, YB - (1.0 / 3.0) * unit, color=INK, sw=2.4))
    p.append(circle(xa, YB - unit, 4, fill=POS, stroke=POS, sw=1))
    p.append(fitbox(xa + 34, YB - unit - 78, 268, 46,
                    "A забрала наперед:\nдоки не наздожене — не претендент",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5))

    render(os.path.join(OUT, "ideal-vs-real.svg"), W, H, *p,
           title="Борг = скільки задача мала б отримати мінус скільки отримала")


# ── 2. Коли викликається планувальник ───────────────────────────────────────
def fig_when_schedule():
    W, H = 1020, 560
    p = []

    BW = 296.0
    xs = [30.0, 362.0, 694.0]
    y1, h1 = 72.0, 84.0

    trig = [
        ("Задача чекає на дані",
         "порожній сокет, зайнятий\nм'ютекс, sleep — віддає сама", NEG),
        ("Хтось став готовим",
         "прийшов пакет, звільнився замок:\nчи не відстав новий більше?", FIELD),
        ("Тік таймера",
         "переривання з частотою HZ —\nєдиний спосіб забрати силоміць", POS),
    ]
    for i, (head, body, c) in enumerate(trig):
        p.append(rect(xs[i], y1, BW, h1, fill=SOFT, stroke=c, sw=2, rx=8))
        p.append(text(xs[i] + BW / 2, y1 + 26, head, size=14, color=c, bold=True))
        p.append(mtext(xs[i] + BW / 2, y1 + 48, body, size=11.5, color=INK))

    # ланцюг під третім приводом
    p.append(fitbox(xs[2], 202, BW, 66,
                    "прапорець TIF_NEED_RESCHED\n«зняти за першої безпечної нагоди»",
                    size=12, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(fitbox(xs[2], 306, BW, 106,
                    "безпечна межа:\nвихід із ядра в простір користувача\nзвільнення останнього замка\ncond_resched() у довгому циклі",
                    size=11.5, fill=SOFT, stroke=POS, sw=1.8))

    # стрілки
    p.append(arrow(xs[0] + BW / 2, y1 + h1, xs[0] + BW / 2, 448, color=NEG))
    p.append(arrow(xs[1] + BW / 2, y1 + h1, xs[1] + BW / 2, 448, color=FIELD))
    p.append(arrow(xs[2] + BW / 2, y1 + h1, xs[2] + BW / 2, 200, color=POS))
    p.append(arrow(xs[2] + BW / 2, 268, xs[2] + BW / 2, 304, color=POS))
    p.append(arrow(xs[2] + BW / 2, 412, xs[2] + BW / 2, 448, color=POS))

    p.append(fitbox(30, 450, 960, 62,
                    "schedule() — узяти з дерева найлівішого й перемкнутися на нього",
                    size=15, fill="#eef3ff", stroke=INK, sw=2, bold=True))

    # пояснення, чому тік не перемикає одразу
    p.append(fitbox(30, 222, 604, 70,
                    "Обробник переривання перемкнути задачу не може:\nперерваний код міг тримати спін-замок — перемикання зависло б назавжди",
                    size=12, fill="#fffdf0", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "when-schedule.svg"), W, H, *p,
           title="Три приводи покликати планувальник — і чому тік лише ставить прапорець")


# ── 3. EEVDF: спершу придатність, потім найближчий строк ────────────────────
def fig_eevdf_choice():
    W, H = 1020, 660
    p = []

    # ── панель 1: вісь боргу ────────────────────────────────────────────────
    AX0, AX1, AY = 150.0, 900.0, 148.0
    ZERO = 480.0
    p.append(rect(ZERO, AY - 34, AX1 - ZERO, 68, fill=GREENBG, stroke=FIELD, sw=1.2, rx=4))
    p.append(rect(AX0, AY - 34, ZERO - AX0, 68, fill=GREYBG, stroke=GREY, sw=1.2, rx=4))
    p.append(line(AX0, AY, AX1 + 18, AY, color=INK, sw=1.6))
    p.append(line(ZERO, AY - 44, ZERO, AY + 44, color=INK, sw=1.8))
    p.append(text(ZERO, AY - 54, "борг = 0", size=12, color=INK, bold=True))
    p.append(text(ZERO - 16, AY + 62, "уже забрали наперед — поза розглядом",
                  size=12, color=GREY, anchor="end"))
    p.append(text(ZERO + 16, AY + 62, "придатні: система їм ще винна",
                  size=12, color=FIELD, anchor="start"))

    marks = [("A", 760.0, POS, True), ("B", 620.0, NEG, True), ("C", 300.0, GREY, False)]
    for name, x, c, ok in marks:
        p.append(circle(x, AY, 12, fill="#ffffff", stroke=c, sw=2.6))
        p.append(text(x, AY + 5, name, size=13, color=c, bold=True))

    # ── панель 2: строки придатних ──────────────────────────────────────────
    BY = 330.0
    p.append(text(AX0 - 22, BY - 6, "запитаний", size=12, color=MUTED, anchor="end"))
    p.append(text(AX0 - 22, BY + 10, "відрізок", size=12, color=MUTED, anchor="end"))

    p.append(rect(AX0, BY - 30, 300, 42, fill="#fdecea", stroke=POS, sw=2, rx=5))
    p.append(text(AX0 + 150, BY - 3, "A: 3 мс", size=13, color=POS, bold=True))
    p.append(line(AX0 + 300, BY - 9, AX0 + 300, BY + 96, color=POS, sw=2, dash="5 4"))
    p.append(text(AX0 + 300, BY + 116, "строк A", size=12, color=POS, bold=True))

    p.append(rect(AX0, BY + 34, 100, 42, fill="#eaf0fd", stroke=NEG, sw=2, rx=5))
    p.append(text(AX0 + 50, BY + 61, "B: 1 мс", size=13, color=NEG, bold=True))
    p.append(line(AX0 + 100, BY + 55, AX0 + 100, BY + 96, color=NEG, sw=2, dash="5 4"))
    p.append(text(AX0 + 100, BY + 116, "строк B", size=12, color=NEG, bold=True))

    p.append(line(AX0, BY + 96, AX1, BY + 96, color=INK, sw=1.6))
    p.append(text(AX1 + 4, BY + 116, "віртуальний час", size=12, color=MUTED, anchor="end"))
    p.append(fitbox(560, BY + 6, 400, 62,
                    "ближчий строк виграє: B пролізе вперед,\nхоча вага, а отже й частка, в обох однакова",
                    size=12, fill=SOFT, stroke=NEG, sw=1.6))

    # ── панель 3: що з цього виходить у часі ────────────────────────────────
    CY = 520.0
    p.append(text(AX0 - 22, CY + 24, "як лягає", size=12, color=MUTED, anchor="end"))
    p.append(text(AX0 - 22, CY + 40, "в час", size=12, color=MUTED, anchor="end"))
    p.append(line(AX0, CY + 68, AX1, CY + 68, color=INK, sw=1.4))

    x = AX0
    step = 0
    while x < AX1 - 8 and step < 12:
        if step % 2 == 0:
            p.append(rect(x, CY, 34, 62, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
            p.append(text(x + 17, CY + 38, "B", size=12, color=NEG, bold=True))
            x += 34
        else:
            p.append(rect(x, CY, 102, 62, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
            p.append(text(x + 51, CY + 38, "A", size=13, color=POS, bold=True))
            x += 102
        step += 1

    p.append(fitbox(AX0, CY + 84, 750, 34,
                    "B прокидається втричі частіше й з'їдає щоразу втричі менше — сумарно порівну",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.3))

    render(os.path.join(OUT, "eevdf-choice.svg"), W, H, *p,
           title="EEVDF: спершу відсіяти тих, хто забрав наперед, потім узяти найближчий строк")


# ── 4. Чотири планувальники: механізм і навантаження, що його зламало ───────
def fig_four_schedulers():
    W, H = 1060, 600
    p = []

    xs = [30.0, 288.0, 546.0, 804.0]
    BW = 226.0

    cols = [
        ("Обхід усіх", "1991 — 2.4", GREY,
         "перебрати ВСІ готові задачі,\nкожній порахувати goodness(),\nузяти найкращу;\nодна черга на всю машину\nпід одним замком",
         "сервер із тисячами задач:\nвибір коштує тим більше,\nчим більше охочих,\nа спільний замок черги\nне ділиться між процесорами"),
        ("Сталий час", "O(1), 2002 → 2.6.0", NEG,
         "черга на КОЖЕН процесор;\n140 рівнів, масиви\nactive / expired,\nвибір — один пошук\nпо бітовій мапі",
         "інтерактивність — ЗДОГАДКА\nза середнім часом сну:\nевристика хибно судила\nпро ігри, звук і відео,\nа кожна латка родила виняток"),
        ("Чесний облік", "CFS, 2.6.23, 2007", FIELD,
         "жодних здогадок про наміри:\nвіртуальний час і борг,\nчервоно-чорне дерево,\nбіжить найлівіший",
         "одна ручка nice керувала\nЧАСТКОЮ; попросити\n«часто й потроху»\nбуло нічим — доводилося\nпросити зайвий відсоток"),
        ("Придатність і строк", "EEVDF, 6.6, 2023", POS,
         "борг відсіює тих, хто забрав\nнаперед; серед решти —\nнайближчий віртуальний строк;\nдовжина відрізка стала\nокремою, другою віссю",
         "тримається; але відповіддю\nна наступний тиск\nстав не п'ятий алгоритм,\nа sched_ext (6.12):\nполітика як програма eBPF"),
    ]

    for i, (name, ver, c, mech, broke) in enumerate(cols):
        x = xs[i]
        p.append(rect(x, 46, BW, 62, fill=SOFT, stroke=c, sw=2.2, rx=8))
        p.append(text(x + BW / 2, 72, name, size=15, color=c, bold=True))
        p.append(text(x + BW / 2, 94, ver, size=12, color=MUTED))

        p.append(text(x + BW / 2, 142, "як обирає", size=12, color=MUTED))
        p.append(fitbox(x, 152, BW, 152, mech, size=11.5,
                        fill="#ffffff", stroke=c, sw=1.6))

        p.append(text(x + BW / 2, 348, "що на нього натиснуло", size=12, color=MUTED))
        p.append(fitbox(x, 358, BW, 152, broke, size=11.5,
                        fill=GREYBG if i < 3 else GREENBG,
                        stroke=MUTED if i < 3 else FIELD, sw=1.4))

    for i in range(3):
        xg = xs[i] + BW + 6
        p.append(arrow(xg, 78, xg + 18, 78, color=INK))

    p.append(fitbox(30, 530, 1000, 44,
                    "Щоразу переписували не через кращу теорію, а через навантаження, якого попередній автор не бачив",
                    size=13, fill="#eef3ff", stroke=INK, sw=1.8, bold=True))

    render(os.path.join(OUT, "four-schedulers.svg"), W, H, *p,
           title="Чотири планувальники Linux: чим обирали і що кожного зламало")


# ── 5. V як центр мас годинників; придатність = ліворуч від опори ───────────
def fig_lag_balance():
    W, H = 1020, 570
    p = []

    X0, X1 = 150.0, 880.0
    T0, T1 = 3.2, 10.8

    def X(v):
        return X0 + (v - T0) * (X1 - X0) / (T1 - T0)

    YAX = 300.0
    V = 7.1406

    p.append(rect(X0 - 20, YAX - 30, X(V) - X0 + 20, 60, fill=GREENBG,
                  stroke=FIELD, sw=1.2, rx=4))
    p.append(rect(X(V), YAX - 30, X1 - X(V) + 20, 60, fill=GREYBG,
                  stroke=GREY, sw=1.2, rx=4))
    p.append(line(X0 - 30, YAX, X1 + 40, YAX, color=INK, sw=1.6))
    p.append(text(X1 + 36, YAX - 44, "віртуальний час", size=12,
                  color=MUTED, anchor="end"))

    # опора в точці V
    p.append(line(X(V), YAX - 34, X(V), YAX + 36, color=INK, sw=2.2))
    p.append("<polygon points='%.1f,%.1f %.1f,%.1f %.1f,%.1f' "
             "fill='%s' stroke='%s' stroke-width='1.5'/>"
             % (X(V), YAX + 36, X(V) - 17, YAX + 68, X(V) + 17, YAX + 68,
                INK, INK))
    p.append(text(X(V), YAX + 94, "V = 7.14", size=13, color=INK, bold=True))

    marks = [("B", 4.0, NEG), ("C", 8.0, FIELD), ("A", 10.0, POS)]
    for name, v, c in marks:
        p.append(circle(X(v), YAX, 14, fill="#ffffff", stroke=c, sw=2.8))
        p.append(text(X(v), YAX + 5, name, size=14, color=c, bold=True))

    p.append(text(X(4.0), YAX + 94, "v = 4,  w = 1024", size=12, color=NEG))
    p.append(text(X(8.0), YAX + 130, "v = 8,  w = 335", size=12, color=FIELD))
    p.append(text(X(10.0), YAX + 94, "v = 10,  w = 1024", size=12, color=POS))

    arms = [(4.0, 128.0, NEG, "борг B = 1 · (V − 4) = +3.14 мс"),
            (8.0, 184.0, FIELD, "борг C = (335/1024) · (V − 8) = −0.28 мс"),
            (10.0, 240.0, POS, "борг A = 1 · (V − 10) = −2.86 мс")]
    for v, y, c, lab in arms:
        p.append(line(X(v), YAX - 18, X(v), y, color=c, sw=1.3, dash="4 4"))
        p.append(line(X(V), y, X(v), y, color=c, sw=2.4))
        p.append(circle(X(v), y, 4, fill=c, stroke=c, sw=1))
        if v < V:
            p.append(text(X(v) - 18, y + 5, lab, size=12, color=c, anchor="end"))
        else:
            p.append(text(X(v) + 20, y + 5, lab, size=12, color=c, anchor="start"))
    p.append(line(X(V), 116, X(V), 252, color=INK, sw=1.2, dash="3 4"))

    p.append(text(X0 - 26, YAX + 168, "придатні: v ≤ V, борг невід'ємний",
                  size=12, color=FIELD, anchor="start"))
    p.append(text(X1 + 36, YAX + 168, "забрали наперед: v > V", size=12,
                  color=GREY, anchor="end"))

    p.append(fitbox(150, 496, 720, 58,
                    "Σ wᵢ · (V − vᵢ) = 0   ⇒   V = Σ wᵢvᵢ / Σ wᵢ",
                    size=16, fill="#eef3ff", stroke=INK, sw=2, bold=True))

    render(os.path.join(OUT, "lag-balance.svg"), W, H, *p,
           title="Системний віртуальний час — точка рівноваги зважених годинників")


# ── 6. Один цикл: борги дзеркальні, сума нуль ───────────────────────────────
def fig_lag_cycle():
    W, H = 1020, 660
    p = []

    X0, X1 = 150.0, 930.0
    TMAX = 13.0

    def X(t):
        return X0 + t * (X1 - X0) / TMAX

    YZ = 386.0
    SC = 96.0

    def Y(g):
        return YZ - g * SC

    GY, GH = 104.0, 52.0
    p.append(text(X0 - 16, GY + 22, "хто", size=12, color=MUTED, anchor="end"))
    p.append(text(X0 - 16, GY + 40, "біжить", size=12, color=MUTED, anchor="end"))
    blocks = [(0, 1, "B"), (1, 4, "A"), (4, 5, "B"), (5, 6, "B"), (6, 7, "B"),
              (7, 10, "A"), (10, 11, "B"), (11, 12, "B"), (12, 13, "B")]
    for a, b, name in blocks:
        c = POS if name == "A" else NEG
        bg = "#fdecea" if name == "A" else "#eaf0fd"
        p.append(rect(X(a) + 2, GY, X(b) - X(a) - 4, GH, fill=bg,
                      stroke=c, sw=1.8, rx=4))
        p.append(text((X(a) + X(b)) / 2, GY + 33, name, size=14,
                      color=c, bold=True))

    p.append(text(X0 - 16, GY - 26, "A просить відрізок 3 мс, B — 1 мс; вага в обох однакова",
                  size=12, color=MUTED, anchor="start"))

    p.append(line(X0, GY + GH + 16, X(13), GY + GH + 16, color=MUTED, sw=1.2))
    for t in range(0, 14):
        p.append(line(X(t), GY + GH + 12, X(t), GY + GH + 20, color=MUTED, sw=1.0))
        if t % 2 == 0:
            p.append(text(X(t), GY + GH + 38, str(t), size=11, color=MUTED))
    p.append(text(X(13) + 26, GY + GH + 38, "мс", size=11, color=MUTED, anchor="end"))

    for t in (1, 4, 7, 10, 13):
        p.append(line(X(t), GY + GH + 46, X(t), Y(-1.62), color="#dfe3e8", sw=1.1))

    p.append(line(X0 - 20, YZ, X(13) + 20, YZ, color=INK, sw=1.6))
    p.append(text(X0 - 26, YZ + 5, "борг 0", size=12, color=INK,
                  anchor="end", bold=True))
    p.append(line(X0, Y(-1.5), X(13), Y(-1.5), color=GREY, sw=1.5, dash="7 5"))
    p.append(text(X0 + 8, Y(-1.5) + 24,
                  "нижня межа для A:  −r · (1 − w/W) = −1.5 мс",
                  size=12, color=GREY, anchor="start"))

    lag_a = [(0, 0.0), (1, 0.5), (4, -1.0), (7, 0.5), (10, -1.0), (13, 0.5)]
    for i in range(len(lag_a) - 1):
        t1, g1 = lag_a[i]
        t2, g2 = lag_a[i + 1]
        p.append(line(X(t1), Y(g1), X(t2), Y(g2), color=POS, sw=2.8))
        p.append(line(X(t1), Y(-g1), X(t2), Y(-g2), color=NEG, sw=2.8))
    for t, g in lag_a:
        p.append(circle(X(t), Y(g), 3.5, fill=POS, stroke=POS, sw=1))
        p.append(circle(X(t), Y(-g), 3.5, fill=NEG, stroke=NEG, sw=1))

    p.append(text(X(13) + 24, Y(0.5) + 5, "A", size=14, color=POS,
                  bold=True, anchor="start"))
    p.append(text(X(13) + 24, Y(-0.5) + 5, "B", size=14, color=NEG,
                  bold=True, anchor="start"))

    p.append(fitbox(150, 566, 720, 58,
                    "борг A + борг B = 0 у кожну мить",
                    size=15, fill="#eef3ff", stroke=INK, sw=2, bold=True))

    render(os.path.join(OUT, "lag-cycle.svg"), W, H, *p,
           title="Борги двох задач дзеркальні, а їхня сума — точний нуль")


# ── 7. (базова) Хто біжить: найбільший борг ─────────────────────────────────
def fig_debt_pick():
    W, H = 1040, 560
    p = []

    XZ = 520.0          # нуль боргу
    PX = 100.0          # пікселів на мілісекунду
    NAMEX = 250.0       # правий край стовпця імен
    LANE = 44.0
    WINX = 860.0

    def X(v):
        return XZ + v * PX

    panels = [
        (110.0, "щойно редактор прокинувся",
         [("редактор", 2.4, POS), ("компілятор A", -1.5, NEG),
          ("компілятор B", -0.9, FIELD)], "редактор"),
        (330.0, "після відрізка редактора (4 мс)",
         [("редактор", -0.3, POS), ("компілятор A", -0.2, NEG),
          ("компілятор B", 0.4, FIELD)], "компілятор B"),
    ]

    for ytop, cap, items, winner in panels:
        p.append(text(60, ytop - 32, cap, size=16, color=INK,
                      bold=True, anchor="start"))
        ybot = ytop + LANE * (len(items) - 1)
        p.append(line(XZ, ytop - 22, XZ, ybot + 24, color=MUTED,
                      sw=1.6, dash="6 5"))
        p.append(text(XZ, ytop - 30, "борг 0", size=12, color=MUTED))

        for k, (name, val, col) in enumerate(items):
            y = ytop + k * LANE
            big = (name == winner)
            p.append(text(NAMEX, y + 5, name, size=14, color=col,
                          bold=big, anchor="end"))
            x = X(val)
            p.append(line(XZ, y, x, y, color=col, sw=11 if big else 6))
            p.append(circle(x, y, 10 if big else 7,
                            fill="#ffffff", stroke=col, sw=3 if big else 2))
            off = 22 if val >= 0 else -22
            p.append(text(x + off, y + 5, ("%+.1f мс" % val), size=13,
                          color=col, anchor="start" if val >= 0 else "end"))
            if big:
                p.append(arrow(WINX + 80, y, WINX + 20, y, color=INK, sw=2.2))
                p.append(text(WINX + 88, y + 5, "біжить", size=15,
                              color=INK, bold=True, anchor="start"))

    p.append(text(300, 490, "борг < 0: узяв більше, ніж належало",
                  size=13, color=MUTED, anchor="middle"))
    p.append(text(760, 490, "борг > 0: недобрав", size=13,
                  color=MUTED, anchor="middle"))
    p.append(fitbox(220, 512, 600, 40,
                    "процесор дістає той, перед ким борг найбільший",
                    size=16, fill="#eef3ff", stroke=INK, sw=2, bold=True))

    render(os.path.join(OUT, "debt-pick.svg"), W, H, *p,
           title="Планувальник щоразу віддає процесор найбільшому боргові")


fig_debt_pick()
fig_ideal_vs_real()
fig_when_schedule()
fig_eevdf_choice()
fig_four_schedulers()
fig_lag_balance()
fig_lag_cycle()
print("ok")
