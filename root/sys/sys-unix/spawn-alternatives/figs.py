# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: три способи прожити вікно між народженням і exec ────────────────
# Ідея: усі три шляхи ведуть до однієї точки — exec. Різняться вони тим, ЩО
# відбувається у проміжку: хто там виконується, чи живий у цей час батько і
# чиєю пам'яттю користується дитина.
def fig_spawn_window():
    W, H = 1060, 820
    p = []

    TOPS = [60, 310, 560]
    X0, X1 = 250.0, 760.0
    XB, XE = 375.0, 590.0        # точка народження й точка exec

    PANELS = [
        ("fork + exec",
         False,
         ["вікно відкрите для будь-якого коду:",
          "dup2, setuid, setrlimit, unshare"],
         ["копія таблиць сторінок",
          "власний адресний простір",
          "батько працює паралельно",
          "після — сторінкові винятки"]),
        ("vfork + exec",
         True,
         ["дитина пише в пам'ять батька,",
          "зокрема в його стек: майже нічого не можна"],
         ["таблиць сторінок не створюють",
          "простір і стек спільні",
          "батько спинений",
          "найдешевше й найнебезпечніше"]),
        ("posix_spawn",
         True,
         ["вікно виконує бібліотека за закритим списком дій;",
          "дитина — на власному стеку"],
         ["clone(CLONE_VM | CLONE_VFORK)",
          "простір спільний, стек власний",
          "батько спинений на мить",
          "помилку exec видно з виклику"]),
    ]

    for i, (name, frozen, band, cost) in enumerate(PANELS):
        T = TOPS[i]
        yp, yc = T + 55.0, T + 135.0

        p.append(text(30, T + 32, "%d · %s" % (i + 1, name), size=15.5,
                      color=INK, anchor="start", bold=True))
        p.append(text(240, yp + 5, "батько", size=13, color=NEG, anchor="end"))
        p.append(text(240, yc + 5, "дитина", size=13, color=POS, anchor="end"))

        # лінія батька: суцільна до народження, далі — залежно від способу
        p.append(line(X0, yp, XB, yp, color=NEG, sw=2.6))
        if frozen:
            p.append(line(XB, yp, XE, yp, color=MUTED, sw=2.2, dash="6 5"))
            p.append(text((XB + XE) / 2, yp - 14, "спинений", size=12.5,
                          color=MUTED, italic=True))
        else:
            p.append(line(XB, yp, X1, yp, color=NEG, sw=2.6))
            p.append(text((XB + XE) / 2, yp - 14, "працює далі", size=12.5,
                          color=NEG, italic=True))
        if frozen:
            p.append(line(XE, yp, X1, yp, color=NEG, sw=2.6))

        # лінія дитини
        p.append(line(XB, yc, X1, yc, color=POS, sw=2.6))
        p.append(arrow(XB, yp + 6, XB, yc - 6, color=POS, sw=1.8))
        p.append(circle(XE, yc, 7, fill="#ffffff", stroke=POS, sw=2.4))
        p.append(text(XE, yc + 28, "exec", size=13, color=POS, bold=True))
        p.append(text(XB, yc + 28, "народження", size=12.5, color=MUTED))

        # смуга вікна між лініями
        p.append(fitbox(XB + 22, yp + 16, 330, 48, band, size=12,
                        fill="#f4f6f8", stroke="#c8ced6", sw=1.2))

        # ціна й властивості — праворуч, поза лініями
        p.append(fitbox(800, T + 38, 230, 120, cost, size=12.5,
                        fill="#ffffff", stroke=INK if i == 0 else
                        (POS if i == 1 else FIELD), sw=1.4))

    p.append(fitbox(60, 742, 940, 56,
                    ["Точка призначення в усіх трьох однакова — exec. Способи різняться лише тим,",
                     "хто і з чиєю пам'яттю живе у проміжку між народженням дитини й заміною програми."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "spawn-window.svg"), W, H, *p,
           title="Три способи прожити проміжок між народженням і exec")


# ── Фіг. 2: спільність як набір перемикачів ─────────────────────────────────
# Ідея: fork, vfork, потік і контейнер — не чотири різні механізми, а чотири
# набори тих самих перемикачів. Стовпці читаються як пресети одного виклику.
def fig_clone_presets():
    W, H = 1120, 620
    p = []

    LX, LW = 30.0, 268.0
    CW, GAP = 152.0, 8.0
    CX0 = LX + LW + 14

    COLS = ["fork", "vfork", "pthread_create", "posix_spawn\n(glibc ≥ 2.24)", "контейнер\n(clone3)"]

    ROWS = [
        ("адресний простір  ·  CLONE_VM",
         ["власний", "спільний", "спільний", "спільний", "власний"]),
        ("таблиця дескрипторів  ·  CLONE_FILES",
         ["власна", "власна", "спільна", "власна", "власна"]),
        ("корінь, каталог, umask  ·  CLONE_FS",
         ["власні", "власні", "спільні", "власні", "власні"]),
        ("обробники сигналів  ·  CLONE_SIGHAND",
         ["власні", "власні", "спільні", "власні", "власні"]),
        ("одна група потоків  ·  CLONE_THREAD",
         ["—", "—", "так", "—", "—"]),
        ("батько спинений до exec  ·  CLONE_VFORK",
         ["—", "так", "—", "так", "—"]),
        ("простори імен  ·  CLONE_NEW*",
         ["—", "—", "—", "—", "нові"]),
    ]

    p.append(text(W / 2, 44, "Один виклик clone, різні набори перемикачів",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 68, "у кожній клітинці — що дитина дістає щодо цього ресурсу",
                  size=12.5, color=MUTED))

    HY, HH = 88.0, 54.0
    p.append(fitbox(LX, HY, LW, HH, ["що саме ділять", "(прапорець clone)"], size=12.5,
                    fill="#f4f6f8", stroke=INK, sw=1.4))
    for j, name in enumerate(COLS):
        x = CX0 + j * (CW + GAP)
        p.append(fitbox(x, HY, CW, HH, name.split("\n"), size=12.5,
                        fill="#eef3fb", stroke=NEG, sw=1.4))

    RY, RH, RSTEP = 154.0, 46.0, 52.0
    for k, (label, cells) in enumerate(ROWS):
        y = RY + k * RSTEP
        p.append(fitbox(LX, y, LW, RH, label, size=12, pad=7,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))
        for j, v in enumerate(cells):
            x = CX0 + j * (CW + GAP)
            if v.startswith("спіль") or v == "так":
                fill, stroke = "#fbe0dc", POS
            elif v == "—":
                fill, stroke = "#f4f6f8", "#c8ced6"
            elif v == "нові":
                fill, stroke = "#eef7f0", FIELD
            else:
                fill, stroke = "#eef7f0", FIELD
            p.append(fitbox(x, y, CW, RH, v, size=12.5, fill=fill, stroke=stroke, sw=1.3))

    p.append(fitbox(LX, RY + 7 * RSTEP + 14, W - 2 * LX, 54,
                    ["Червоне — спільне з тим, хто покликав; зелене — власне у дитини.",
                     "fork і vfork у ядрі Linux не існують окремо: це виклик clone із заздалегідь заданими прапорцями."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "clone-presets.svg"), W, H, *p,
           title="fork, vfork, потік і контейнер як пресети одного clone")


# ── Фіг. 3: чому дитині vfork не можна повертатися з функції ────────────────
# Ідея: стек один на двох. Поки дитина тільки заглиблюється, рамки батька під
# нею недоторканні. Щойно вона повернулася з функції — її наступні виклики
# лягають на ту саму пам'ять, і батько прокинеться в затертій рамці.
def fig_vfork_one_stack():
    W, H = 1020, 640
    p = []

    p.append(text(W / 2, 44, "Стек один на двох: чому дитині vfork не можна повертатися",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 68, "нижче = глибший виклик; батько спинений на рамці spawn_child()",
                  size=12.5, color=MUTED))

    PANELS = [
        (100.0, "дитина тільки заглиблюється",
         [("main()", "keep"), ("spawn_child()  ·  тут покликано vfork", "keep"),
          ("execvp() — рамка дитини", "child"), ("(глибше нічого немає)", "free")],
         "рамки батька під дитиною недоторканні"),
        (560.0, "дитина повернулася з spawn_child()",
         [("main()", "keep"), ("printf() дитини — лягло сюди", "bad"),
          ("snprintf() дитини", "bad"), ("(глибше нічого немає)", "free")],
         "батько прокинеться в затертій рамці"),
    ]

    BW = 360.0
    RY, RH, RSTEP = 150.0, 52.0, 60.0

    for x, title, rows, foot in PANELS:
        b, bw, bh = textbox(x + BW / 2, 112, title, size=13.5, pad=10,
                            fill="#ffffff", stroke="#c8ced6", sw=1.3)
        p.append(b)
        for k, (label, kind) in enumerate(rows):
            y = RY + k * RSTEP
            if kind == "keep":
                fill, stroke = "#eef3fb", NEG
            elif kind == "child":
                fill, stroke = "#eef7f0", FIELD
            elif kind == "bad":
                fill, stroke = "#fbe0dc", POS
            else:
                fill, stroke = "#ffffff", "#c8ced6"
            p.append(fitbox(x, y, BW, RH, label, size=12.5, fill=fill, stroke=stroke, sw=1.4))
        p.append(fitbox(x, RY + 4 * RSTEP + 6, BW, 46, foot, size=13,
                        fill="#f4f6f8", stroke=INK, sw=1.3))

    p.append(fitbox(60, 512, 900, 100,
                    ["Рамка spawn_child() — та, у яку батько повернеться, коли його розбудять.",
                     "Поки дитина лише викликає глибші функції, вона пише під цією рамкою й нічого не псує.",
                     "Щойно вона з неї вийшла, ця пам'ять стала вільною — і будь-який наступний виклик дитини лягає в неї.",
                     "Тому контракт vfork забороняє і return, і exit: обидва означають вихід із рамки."],
                    size=13, fill="#ffffff", stroke=POS, sw=1.6))

    render(os.path.join(OUT, "vfork-one-stack.svg"), W, H, *p,
           title="Спільний стек: що ламає return у дитині vfork")


# ── Фіг. 4: що має вийти на вимірі ──────────────────────────────────────────
# Ідея: результат виміру — не одне число, а ФОРМА. Один спосіб росте разом із
# пам'яттю батька, решта не росте зовсім; праворуч ту саму нижню зону
# збільшено, бо там три криві злипаються в одну смугу.
def fig_spawn_cost_curves():
    W, H = 1060, 660
    p = []

    p.append(text(W / 2, 40, "Що має вийти: одна крива росте, три — ні",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 64, "час одного запуску залежно від обсягу торкнутої пам'яті батька",
                  size=12.5, color=MUTED))

    ATOP, ABOT = 110.0, 430.0
    AX0, AX1 = 140.0, 500.0
    BX0, BX1 = 640.0, 1000.0

    def gx(x0, x1, g):
        return x0 + (g / 8.0) * (x1 - x0)

    def vy(vmax, v):
        return ABOT - (v / vmax) * (ABOT - ATOP)

    # моделі: fork росте як 0.10 + 0.62·ГіБ, решта — сталі
    FORK_A, FORK_B = 0.10, 0.62
    FLAT = [(0.38, "posix_spawn", NEG),
            (0.30, "vfork + exec", FIELD),
            (0.13, "fork, великі сторінки", MUTED)]

    def axes(x0, x1, vmax, ticks, caption):
        q = []
        q.append(line(x0, ATOP, x0, ABOT, color=INK, sw=1.6))
        q.append(line(x0, ABOT, x1, ABOT, color=INK, sw=1.6))
        for g in (0, 2, 4, 6, 8):
            x = gx(x0, x1, g)
            q.append(line(x, ABOT, x, ABOT + 6, color=MUTED, sw=1.2))
            q.append(text(x, ABOT + 24, str(g), size=12, color=MUTED))
        for tv, lab in ticks:
            y = vy(vmax, tv)
            q.append(line(x0 - 6, y, x0, y, color=MUTED, sw=1.2))
            q.append(text(x0 - 11, y + 4, lab, size=12, color=MUTED, anchor="end"))
        q.append(text((x0 + x1) / 2, ABOT + 48, caption, size=12.5, color=MUTED))
        return q

    # ── панель A: повна шкала ──
    p.append(text((AX0 + AX1) / 2, 94, "повна шкала", size=13, color=INK, bold=True))
    p += axes(AX0, AX1, 6.0, [(0, "0"), (2, "2"), (4, "4"), (6, "6")], "ГіБ у батька")
    p.append(text(AX0 - 11, ATOP - 14, "мс", size=12, color=MUTED, anchor="end"))
    p.append(line(gx(AX0, AX1, 0), vy(6.0, FORK_A),
                  gx(AX0, AX1, 8), vy(6.0, FORK_A + 8 * FORK_B), color=POS, sw=2.8))
    for v, _, col in FLAT:
        p.append(line(AX0, vy(6.0, v), AX1, vy(6.0, v), color=col, sw=1.8))
    p.append(fitbox(150, 122, 196, 48, ["fork + exec", "сторінки 4 КіБ"],
                    size=12.5, fill="#ffffff", stroke=POS, sw=1.6))

    # перехід до збільшеної панелі
    p.append(arrow(508, 418, 622, 336, color=MUTED, sw=1.6))
    p.append(text(570, 300, "збільшено ×10", size=12.5, color=MUTED))

    # ── панель B: збільшена нижня зона ──
    p.append(text((BX0 + BX1) / 2, 94, "нижня зона, збільшено", size=13, color=INK, bold=True))
    p += axes(BX0, BX1, 0.6,
              [(0, "0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6")], "ГіБ у батька")
    p.append(text(BX0 - 11, ATOP - 14, "мс", size=12, color=MUTED, anchor="end"))
    g_top = (0.6 - FORK_A) / FORK_B
    p.append(line(BX0, vy(0.6, FORK_A), gx(BX0, BX1, g_top), ATOP, color=POS, sw=2.8))
    p.append(text(705, 128, "fork + exec", size=12.5, color=POS, anchor="start", bold=True))
    for v, lab, col in FLAT:
        y = vy(0.6, v)
        p.append(line(BX0, y, BX1, y, color=col, sw=2.4))
        p.append(text(700, y - 14, lab, size=12.5, color=col, anchor="start"))

    p.append(fitbox(70, 502, 920, 132,
                    ["Нахил єдиної висхідної кривої — стала машини, а не програми: на кожен гігабайт",
                     "торкнутої пам'яті ядро копіює приблизно два мегабайти статей таблиць сторінок.",
                     "Три горизонтальні криві пласкі з різних причин: vfork і posix_spawn не створюють",
                     "адресного простору взагалі, а fork із великими сторінками копіює у 512 разів менше статей.",
                     "Якщо в тебе posix_spawn росте разом із батьком — бібліотека реалізує його через fork."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "spawn-cost-curves.svg"), W, H, *p,
           title="Час запуску залежно від обсягу пам'яті батька")


# ── Фіг. 5: порядок кроків усередині posix_spawn ────────────────────────────
# Ідея: увесь контракт posix_spawn — це послідовність. Атрибути лягають ПЕРЕД
# діями з файлами, закриття CLOEXEC — ПІСЛЯ них, а канал помилки йде назад до
# батька спільною пам'яттю. Хто плутає порядок, той дивується результату.
def fig_spawn_order():
    W, H = 1040, 712
    p = []

    PX, PW = 60, 280
    CX, CW = 420, 560

    p.append(fitbox(PX, 52, PW, 40, "батько", size=15, bold=True,
                    fill="#eef0f4", stroke=MUTED, sw=1.3))
    p.append(fitbox(CX, 52, CW, 40, "дитина — той самий адресний простір",
                    size=15, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.3))

    # ── смуга батька ────────────────────────────────────────────────────────
    p.append(fitbox(PX, 110, PW, 76,
                    ["posix_spawn(&pid, …)", "дії та атрибути вже складені"],
                    size=13, fill="#eef3fb", stroke=NEG, sw=1.5))
    p.append(fitbox(PX, 250, PW, 76,
                    ["спить", "аж доки дитина не зробить exec"],
                    size=13, fill="#ffffff", stroke=NEG, sw=1.5))
    p.append(fitbox(PX, 470, PW, 88,
                    ["прокидається:", "0 і pid — або код помилки",
                     "(невдалу дитину вже прибрано)"],
                    size=13, fill="#eef3fb", stroke=NEG, sw=1.5))

    # ── смуга дитини ────────────────────────────────────────────────────────
    STEPS = [
        (110, 54, ["1 · дескриптори — копія батькового набору"]),
        (184, 72, ["2 · атрибути: сеанс, група процесів, RESETIDS,",
                   "планування, маска сигналів, SETSIGDEF"]),
        (290, 54, ["3 · дії з файлами — строго в порядку додавання"]),
        (364, 54, ["4 · закриваються всі дескриптори з FD_CLOEXEC"]),
        (438, 54, ["5 · execve або execvpe — програма замінена"]),
    ]
    for y, h, lines in STEPS:
        p.append(fitbox(CX, y, CW, h, lines, size=13,
                        fill="#f7fbf8", stroke=FIELD, sw=1.5))
    for i in range(len(STEPS) - 1):
        y0 = STEPS[i][0] + STEPS[i][1]
        y1 = STEPS[i + 1][0]
        p.append(arrow(CX + CW / 2, y0, CX + CW / 2, y1, color=FIELD, sw=1.8))

    # клонування й зворотний канал помилки
    p.append(arrow(PX + PW, 148, CX, 137, color=NEG, sw=1.8))
    p.append(arrow(CX, 465, PX + PW + 8, 505, color=POS, sw=1.8))

    p.append(fitbox(60, 590, 920, 86,
                    ["Невдача на будь-якому з кроків 1–5 не мовчить: код помилки лягає в пам'ять, спільну з батьком,",
                     "і glibc повертає його прямо з posix_spawn — саме тому «спільна пам'ять» тут вигода, а не ризик.",
                     "Стандарт дозволяє й інший шлях: дитина виходить із кодом 127. Переносний код перевіряє обидва."],
                    size=13, fill="#ffffff", stroke=POS, sw=1.6))

    render(os.path.join(OUT, "spawn-order.svg"), W, H, *p,
           title="Що і в якій послідовності робить posix_spawn")


# ── Фіг. (вставка api): 64-бітове слово прапорців ───────────────────────────
# Ідея: старий clone склав дві різні речі — номер сигналу й набір прапорців —
# в одне машинне слово. Молодший байт зайнятий сигналом, решта 24 біти
# розібрані до останнього; усе, що вище 32-го біта, тим викликом не передати.
def fig_clone_flag_word():
    W, H = 1160, 600
    p = []

    p.append(text(W / 2, 44, "Одне слово на дві різні речі — і чому воно скінчилося",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 70, "розкладка бітів, які clone і clone3 приймають як «прапорці»",
                  size=12.5, color=MUTED))

    ZONES = [
        (40.0, 286.0, ["біти 0–7", "CSIGNAL = 0x000000ff"], "#fdecea", POS,
         ["номер сигналу, який ядро надішле",
          "батькові, коли дитина завершиться;",
          "fork ставить сюди SIGCHLD",
          "",
          "сюди ж утиснули CLONE_NEWTIME",
          "(0x00000080) — у clone його не",
          "передати, лише clone3 і unshare"]),
        (336.0, 436.0, ["біти 8–31", "класичні прапорці clone"], "#eef3fb", NEG,
         ["24 біти — і всі зайняті:",
          "CLONE_VM = 0x00000100",
          "…",
          "CLONE_IO = 0x80000000",
          "",
          "в обгортці glibc flags — це int,",
          "у сирому виклику — unsigned long;",
          "вище 31-го біта не проходить ні там, ні там"]),
        (782.0, 338.0, ["біти 32–63", "лише clone3"], "#eef7f0", FIELD,
         ["CLONE_CLEAR_SIGHAND = 1 << 32",
          "CLONE_INTO_CGROUP = 1 << 33",
          "далі — нові біти свіжих ядер",
          "",
          "передати їх можна лише полем",
          "clone_args.flags завширшки 64 біти"]),
    ]

    for x, w, head, fill, stroke, body in ZONES:
        p.append(fitbox(x, 100, w, 86, head, size=13.5, fill=fill, stroke=stroke, sw=1.8))
        p.append(fitbox(x, 204, w, 190, body, size=12.5, pad=10,
                        fill="#ffffff", stroke="#c8ced6", sw=1.3))

    p.append(fitbox(40, 424, 540, 64,
                    ["clone(): прапорці й номер сигналу лежать в одному слові —",
                     "дописати 33-й прапорець нікуди"],
                    size=13, fill="#f4f6f8", stroke=POS, sw=1.5))
    p.append(fitbox(620, 424, 500, 64,
                    ["clone3(): cl_args.flags і cl_args.exit_signal —",
                     "два різні поля, і обидва по 64 біти"],
                    size=13, fill="#f4f6f8", stroke=FIELD, sw=1.5))

    p.append(fitbox(40, 510, 1080, 64,
                    ["Старий виклик вичерпався не через хибний задум, а через те, що склав дві незалежні речі в одне машинне слово.",
                     "Щоб додати наступний прапорець, довелося зробити новий виклик — зі структурою замість набору регістрів."],
                    size=13, fill="#ffffff", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "clone-flag-word.svg"), W, H, *p,
           title="Розкладка слова прапорців clone і clone3")


# ── Фіг. (вставка api): розкладка struct clone_args ─────────────────────────
# Ідея: структура росте лише в хвіст, і кожен приріст має власний розмір-версію.
# Саме аргумент size вирішує, як ядро прочитає структуру від чужої версії.
def fig_clone_args_layout():
    W, H = 1080, 790
    p = []

    p.append(text(W / 2, 44, "struct clone_args: усі поля по 8 байтів, ріст лише в хвіст",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 70, "зсув у байтах від початку структури; праворуч — розмір, який знає кожне ядро",
                  size=12.5, color=MUTED))

    CX = [(40.0, 90.0), (138.0, 230.0), (376.0, 470.0)]
    p.append(fitbox(CX[0][0], 92, CX[0][1], 36, "зсув", size=12.5,
                    fill="#f4f6f8", stroke=INK, sw=1.3))
    p.append(fitbox(CX[1][0], 92, CX[1][1], 36, "поле", size=12.5,
                    fill="#f4f6f8", stroke=INK, sw=1.3))
    p.append(fitbox(CX[2][0], 92, CX[2][1], 36, "що це", size=12.5,
                    fill="#f4f6f8", stroke=INK, sw=1.3))

    ROWS = [
        ("0",  "flags",        "бітова маска спільності, 64 біти", 0),
        ("8",  "pidfd",        "куди покласти дескриптор на дитину", 0),
        ("16", "child_tid",    "адреса в пам'яті дитини під її TID", 0),
        ("24", "parent_tid",   "адреса в пам'яті батька під TID дитини", 0),
        ("32", "exit_signal",  "сигнал батькові, коли дитина завершиться", 0),
        ("40", "stack",        "найнижчий байт стека дитини", 0),
        ("48", "stack_size",   "розмір цього стека в байтах", 0),
        ("56", "tls",          "блок даних, локальних до потоку", 0),
        ("64", "set_tid",      "масив бажаних номерів по рівнях просторів", 1),
        ("72", "set_tid_size", "скільки елементів у тому масиві", 1),
        ("80", "cgroup",       "дескриптор цільової контрольної групи", 2),
    ]
    PAL = [("#eef3fb", NEG), ("#eef7f0", FIELD), ("#fdecea", POS)]

    RY, RH, RSTEP = 136.0, 42.0, 47.0
    for k, (off, name, what, grp) in enumerate(ROWS):
        y = RY + k * RSTEP
        fill, stroke = PAL[grp]
        p.append(fitbox(CX[0][0], y, CX[0][1], RH, off, size=12.5,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))
        p.append(fitbox(CX[1][0], y, CX[1][1], RH, name, size=13,
                        fill=fill, stroke=stroke, sw=1.4))
        p.append(fitbox(CX[2][0], y, CX[2][1], RH, what, size=12.5,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))

    VX, VW = 856.0, 190.0
    p.append(fitbox(VX, RY, VW, 7 * RSTEP + RH,
                    ["CLONE_ARGS_SIZE_VER0", "= 64 байти", "", "ядро 5.3"],
                    size=12.5, fill=PAL[0][0], stroke=PAL[0][1], sw=1.6))
    p.append(fitbox(VX, RY + 8 * RSTEP, VW, RSTEP + RH,
                    ["VER1 = 80", "ядро 5.5"],
                    size=12.5, fill=PAL[1][0], stroke=PAL[1][1], sw=1.6))
    p.append(fitbox(VX, RY + 10 * RSTEP, VW, RH,
                    "VER2 = 88   ·   ядро 5.7",
                    size=12, fill=PAL[2][0], stroke=PAL[2][1], sw=1.6))

    p.append(fitbox(40, 668, 1000, 96,
                    ["size менший за 64 → EINVAL.   size більший за розмір сторінки → E2BIG.",
                     "size менший за той, що знає ядро → відсутні поля ядро вважає нулями.",
                     "size більший за той, що знає ядро → хвіст мусить бути нульовим, інакше E2BIG.",
                     "Тому sizeof(struct clone_args) із нового заголовка безпечний і на старому ядрі — поки нові поля нульові."],
                    size=12.5, fill="#ffffff", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "clone-args-layout.svg"), W, H, *p,
           title="Поля й зсуви struct clone_args")


fig_spawn_window()
fig_clone_presets()
fig_vfork_one_stack()
fig_spawn_cost_curves()
fig_spawn_order()
fig_clone_flag_word()
fig_clone_args_layout()
print("готово:", OUT)
