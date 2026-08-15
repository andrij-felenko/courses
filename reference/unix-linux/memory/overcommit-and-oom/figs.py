# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: обіцянка і матеріалізація — два різні моменти ───────────────────
# Ідея: адреса з'являється в один момент, фізична сторінка — в інший, і саме
# ця щілина дозволяє роздати зобов'язань більше, ніж є сторінок.
def fig_promise_vs_page():
    W, H = 1080, 630
    p = []

    BW, BH, GAP = 290, 84, 65
    X = [40, 40 + BW + GAP, 40 + 2 * (BW + GAP)]   # 40, 395, 750

    p.append(text(W / 2, 40, "ОБІЦЯНКА — коштує майже нічого",
                  size=14.5, color=MUTED, bold=True))

    rowA = [
        "malloc(1 ГіБ)\nповернув вказівник",
        "ядро дописало VMA:\nдіапазон адрес — твій",
        "фізичних сторінок 0\nRSS не зріс",
    ]
    for x, s in zip(X, rowA):
        p.append(fitbox(x, 62, BW, BH, s, size=14, fill="#eef3fb", stroke=NEG, sw=1.6))
    for i in (0, 1):
        p.append(arrow(X[i] + BW + 8, 62 + BH / 2, X[i + 1] - 8, 62 + BH / 2, color=MUTED, sw=1.8))

    p.append(arrow(W / 2, 158, W / 2, 214, color=INK, sw=2.2))
    p.append(fitbox(660, 162, 380, 46, "перший запис за цією адресою",
                    size=13.5, fill="#ffffff", stroke=MUTED, sw=1.3))

    p.append(text(W / 2, 244, "МАТЕРІАЛІЗАЦІЯ — ось тут платимо",
                  size=14.5, color=MUTED, bold=True))

    rowB = [
        "збій сторінки:\nадреса є, сторінки нема",
        "ядро шукає вільну\nфізичну сторінку",
        "знайшло — RSS зріс.\nА могло й не знайти",
    ]
    for x, s in zip(X, rowB):
        p.append(fitbox(x, 266, BW, BH, s, size=14, fill="#fdeeec", stroke=POS, sw=1.6))
    for i in (0, 1):
        p.append(arrow(X[i] + BW + 8, 266 + BH / 2, X[i + 1] - 8, 266 + BH / 2, color=MUTED, sw=1.8))

    p.append(line(40, 396, W - 40, 396, color=MUTED, sw=1.2, dash="6,5"))

    p.append(text(40, 432, "сума всіх обіцянок · Committed_AS",
                  size=13.5, color=INK, anchor="start", bold=True))
    p.append(rect(40, 444, 1000, 42, fill="#eef3fb", stroke=NEG, sw=1.8))
    p.append(text(540, 471, "27 ГіБ роздано", size=14.5, color=NEG, bold=True))

    p.append(text(40, 524, "фізична пам'ять + своп — усе, що справді існує",
                  size=13.5, color=INK, anchor="start", bold=True))
    p.append(rect(40, 536, 600, 42, fill="#fdeeec", stroke=POS, sw=1.8))
    p.append(text(340, 563, "20 ГіБ існує", size=14.5, color=POS, bold=True))

    p.append(text(W / 2, 606,
                  "система живе доти, доки роздане не почали забирати все й одразу",
                  size=13.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "promise-vs-page.svg"), W, H, *p)


# ── Фіг. 2: три режими обліку як троє різних воріт ──────────────────────────
# Ідея: «ні» можна сказати тільки в момент обіцянки, і кожен режим каже його
# за своїм правилом — аж до режиму 1, який не каже «ні» ніколи.
def fig_three_modes():
    W, H = 1120, 590
    p = []

    p.append(fitbox(310, 26, 500, 52,
                    "запит: приватне записуване відображення на 8 ГіБ",
                    size=14.5, fill="#ffffff", stroke=INK, sw=1.8, bold=True))

    CW, CGAP = 340, 40
    X0 = (W - (3 * CW + 2 * CGAP)) / 2      # 30
    X = [X0 + i * (CW + CGAP) for i in range(3)]

    for x in X:
        p.append(arrow(560, 82, x + CW / 2, 130, color=MUTED, sw=1.6))

    heads = ["0 — евристика (типово)", "1 — завжди дозволяти", "2 — суворий облік"]
    hcol = [NEG, MUTED, POS]
    checks = [
        "відмова лише тоді, коли ОДИН\nзапит більший за всю RAM\nплюс своп. Суму обіцянок\nніхто не звіряє",
        "перевірки немає взагалі:\nядро відповідає «так»\nне дивлячись. Для розріджених\nі свідомо ледачих карт",
        "Committed_AS плюс запит мусить\nвлізти в CommitLimit =\n(RAM − hugetlb)·ratio/100\nплюс своп",
    ]
    verdicts = [
        "8 ГіБ на машині з 16 ГіБ:\nдозволено, навіть якщо\nроздано вже 40",
        "дозволено завжди —\nхоч терабайт на ноутбуці",
        "не влізло → ENOMEM,\nхоча фізична пам'ять\nзараз вільна",
    ]
    notes = [
        "Committed_AS рахується,\nале нікого не стримує",
        "malloc практично ніколи\nне поверне NULL",
        "єдиний режим, де malloc\nчесно каже «ні»",
    ]
    fills = ["#eef3fb", "#f4f6f8", "#fdeeec"]

    for i, x in enumerate(X):
        p.append(fitbox(x, 132, CW, 46, heads[i], size=14.5,
                        fill=fills[i], stroke=hcol[i], sw=1.8, bold=True))
        p.append(fitbox(x, 194, CW, 108, checks[i], size=13.5,
                        fill="#ffffff", stroke=MUTED, sw=1.3))
        p.append(arrow(x + CW / 2, 306, x + CW / 2, 342, color=MUTED, sw=1.8))
        p.append(fitbox(x, 346, CW, 92, verdicts[i], size=13.5,
                        fill=fills[i], stroke=hcol[i], sw=1.6))
        p.append(fitbox(x, 458, CW, 66, notes[i], size=13,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))

    p.append(text(W / 2, 566,
                  "ворота стоять на роздачі адрес, а не на видачі сторінок",
                  size=13.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-modes.svg"), W, H, *p)


# ── Фіг. 3: куди подіти помилку ─────────────────────────────────────────────
# Ідея: помилку є куди повернути лише на воротах обліку; після них шлях веде
# через збій сторінки, у якого немає зворотного каналу взагалі.
def fig_where_error_goes():
    W, H = 1000, 812
    p = []

    p.append(fitbox(300, 26, 400, 54, "malloc(N) — просимо адреси",
                    size=14.5, fill="#ffffff", stroke=INK, sw=1.8, bold=True))
    p.append(arrow(500, 84, 500, 106, color=INK, sw=2.0))

    p.append(fitbox(250, 110, 500, 74,
                    "ворота обліку: чи можна ПООБІЦЯТИ N?",
                    size=14.5, fill="#f4f6f8", stroke=INK, sw=1.8, bold=True))

    p.append(arrow(460, 188, 230, 222, color=MUTED, sw=1.8))
    p.append(arrow(560, 188, 600, 222, color=MUTED, sw=1.8))

    p.append(fitbox(60, 226, 340, 76,
                    "ні → ENOMEM,\nmalloc повертає NULL",
                    size=14, fill="#eef7f0", stroke=FIELD, sw=1.8, bold=True))
    p.append(fitbox(440, 226, 360, 76,
                    "так → VMA додано,\nсторінок досі 0",
                    size=14, fill="#eef3fb", stroke=NEG, sw=1.8))

    p.append(arrow(620, 306, 620, 338, color=INK, sw=2.0))
    p.append(fitbox(440, 342, 360, 62,
                    "перший запис → збій сторінки",
                    size=14, fill="#fdeeec", stroke=POS, sw=1.8, bold=True))

    rungs = [
        "вільна сторінка є → віддали",
        "kswapd, потім прямий витіск",
        "своп і ущільнення, ще прохід",
    ]
    y = 434
    p.append(arrow(620, 406, 620, y - 4, color=INK, sw=2.0))
    for i, s in enumerate(rungs):
        yy = y + i * 70
        p.append(fitbox(440, yy, 360, 54, s, size=13.5,
                        fill="#ffffff", stroke=MUTED, sw=1.4))
        if i < len(rungs) - 1:
            p.append(arrow(620, yy + 54, 620, yy + 66, color=MUTED, sw=1.8))

    p.append(fitbox(60, 470, 330, 168,
                    "Тут повертати нікуди.\nЗбій стався на звичайній\nінструкції запису,\nа в неї немає ані коду\nповернення, ані errno.\nЛишається чекати вічно,\nпанікувати — або вбити.",
                    size=13.5, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    p.append(arrow(620, 628, 620, 660, color=INK, sw=2.0))
    p.append(fitbox(390, 664, 460, 62,
                    "жодної вільної сторінки нема",
                    size=14, fill="#fdeeec", stroke=POS, sw=2.0, bold=True))
    p.append(arrow(620, 728, 620, 748, color=POS, sw=2.2))
    p.append(fitbox(420, 752, 400, 50,
                    "OOM-killer обирає жертву",
                    size=14.5, fill="#fdeeec", stroke=POS, sw=2.0, bold=True))

    render(os.path.join(OUT, "where-error-goes.svg"), W, H, *p)


# ── Фіг. 4: як рахується бал жертви ─────────────────────────────────────────
# Ідея: бал — це просто скільки сторінок звільнить смерть, і поправка
# oom_score_adj теж переводиться у сторінки, тому вона зсуває саме цю суму.
def fig_badness():
    W, H = 1100, 520
    p = []

    p.append(text(W / 2, 40, "машина: 16 ГіБ RAM, свопу нема → totalpages = 4 194 304",
                  size=14, color=INK, bold=True))

    CW = [230, 300, 310, 210]
    X0 = 25
    XS = [X0]
    for w in CW[:-1]:
        XS.append(XS[-1] + w)

    heads = ["задача", "RSS + своп + таблиці,\nсторінок", "поправка oom_score_adj,\nпереведена в сторінки", "бал"]
    HY, HH = 62, 58
    for x, w, s in zip(XS, CW, heads):
        p.append(fitbox(x, HY, w, HH, s, size=13, fill="#f4f6f8",
                        stroke=INK, sw=1.5, bold=True, color=MUTED))

    rows = [
        ("postgres", "1 572 864 + 0 + 3 072", "0 · 4 194 = 0", "1 575 936", "#fdeeec", POS),
        ("cc1 — один із 32", "89 600 + 0 + 256", "0 · 4 194 = 0", "89 856", "#ffffff", MUTED),
        ("postgres, adj = −800", "1 575 936", "−800 · 4 194 = −3 355 200", "−1 779 264", "#eef7f0", FIELD),
    ]
    RY, RH = 126, 76
    for i, (a, b, c, d, fill, stroke) in enumerate(rows):
        yy = RY + i * (RH + 8)
        for x, w, s in zip(XS, CW, (a, b, c, d)):
            p.append(fitbox(x, yy, w, RH, s, size=13.5, fill=fill, stroke=stroke, sw=1.5))

    p.append(fitbox(25, 380, 1050, 58,
                    "найбільший бал — у postgres, хоча пам'ять з'їли 32 компілятори",
                    size=14.5, fill="#fdeeec", stroke=POS, sw=1.8, bold=True))
    p.append(fitbox(25, 448, 1050, 52,
                    "поправка −800 опускає базу нижче за будь-який компілятор — гине cc1",
                    size=14, fill="#eef7f0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "badness.svg"), W, H, *p)


fig_promise_vs_page()
fig_three_modes()
fig_where_error_goes()
fig_badness()
print("ok")


# ── Фіг. 5: історія OOM-killer'а — п'ять поворотних точок ───────────────────
# Ідея: не механіка, а хронологія суперечки — коли й чиїми руками мінявся
# спосіб вибирати жертву.
def fig_oom_history():
    W, H = 1080, 760
    p = []

    p.append(text(W / 2, 38, "ХТО І КОЛИ МІНЯВ ВИБІР ЖЕРТВИ",
                  size=15, color=MUTED, bold=True))

    YX, YW = 30, 130          # колонка року
    CX, CW = 190, 860         # колонка змісту
    RH, GAP = 108, 22
    Y0 = 66

    p.append(line(CX - 22, Y0, CX - 22, Y0 + 5 * (RH + GAP) - GAP,
                  color=MUTED, sw=1.4, dash="5,6"))

    rows = [
        ("1998–2000",
         "Рік ван Ріл (Rik van Riel) пише mm/oom_kill.c.\n"
         "Евристика badness зважує провину: розмір, час роботи,\nnice, привілеї, кількість дітей.",
         "#eef3fb", NEG),
        ("24.09.2004",
         "LKML, гілка «oom_pardon, aka don't kill my xlock».\n"
         "Андріс Броуер (Andries Brouwer) відповідає притчею\nпро літак і механізм OOF.",
         "#fdeeec", POS),
        ("червень 2010",
         "Девід Рієнджес (David Rientjes) переписує евристику з нуля\n"
         "(ядро 2.6.36): бал — частка пам'яті машини.\noom_adj змінюється на oom_score_adj у проміле.",
         "#eef3fb", NEG),
        ("2015 → 4.6 (2016)",
         "Ідея Мела Ґормана (Mel Gorman) на LSF/MM, незалежно —\n"
         "Олег Нестеров. OOM reaper Міхала Гоцка (Michal Hocko)\nвідбирає сторінки, не чекаючи смерті жертви.",
         "#eef7f0", FIELD),
        ("донині",
         "Строгий режим без overcommit майже ніхто не вмикає.\n"
         "Рішення про смерть виносять у простір користувача —\nтуди, де є знання про застосунок.",
         "#f4f6f8", MUTED),
    ]

    for i, (yr, body, fill, stroke) in enumerate(rows):
        yy = Y0 + i * (RH + GAP)
        p.append(fitbox(YX, yy + 26, YW, RH - 52, yr, size=14,
                        fill="#ffffff", stroke=stroke, sw=1.8, bold=True))
        p.append(circle(CX - 22, yy + RH / 2, 7, fill=fill, stroke=stroke, sw=2))
        p.append(fitbox(CX, yy, CW, RH, body, size=14.5,
                        fill=fill, stroke=stroke, sw=1.6))

    render(os.path.join(OUT, "oom-history.svg"), W, H, *p)


fig_oom_history()


# ── Фіг. 6: важелі досліду й точки, де кожен чіпляється ─────────────────────
# Ідея: шість перемикачів, якими міняють поведінку ОДНІЄЇ програми, стають
# системою, щойно видно, до якої ланки шляху кожен із них прив'язаний.
def fig_levers():
    W, H = 1140, 742
    p = []

    p.append(text(W / 2, 36, "ШЛЯХ ОДНОГО ЗАПИТУ Й ВАЖЕЛІ НАД НИМ",
                  size=15, color=MUTED, bold=True))

    SX, SW = 400, 340          # колонка шляху
    LX, LW = 24, 344           # важелі ліворуч
    RX, RW = 772, 344          # важелі праворуч
    Y0, SH, DY = 62, 62, 90

    stages = [
        ("malloc(N) — просимо адреси", "#ffffff", INK),
        ("ворота обліку:\nчи можна ПООБІЦЯТИ N", "#f4f6f8", INK),
        ("VMA додано,\nсторінок досі нуль", "#eef3fb", NEG),
        ("перший запис → збій сторінки", "#fdeeec", POS),
        ("витіснення: kswapd,\nпотім прямий", "#ffffff", MUTED),
        ("вільної сторінки нема →\nвибір жертви", "#fdeeec", POS),
        ("SIGKILL — повернення з запису\nне буде", "#fdeeec", POS),
    ]

    ys = [Y0 + i * DY for i in range(len(stages))]
    for i, (s, fill, stroke) in enumerate(stages):
        p.append(fitbox(SX, ys[i], SW, SH, s, size=13.5,
                        fill=fill, stroke=stroke, sw=1.8,
                        bold=(i in (1, 3, 5))))
        if i + 1 < len(stages):
            p.append(arrow(SX + SW / 2, ys[i] + SH, SX + SW / 2, ys[i + 1] - 4,
                           color=INK, sw=2.0))

    LH = 84
    levers = [
        # (індекс ланки, бік, текст, заливка, обвід)
        (1, "L", "vm.overcommit_memory = 2\nмашина рахує суму обіцянок\n→ malloc повертає NULL",
         "#eef7f0", FIELD),
        (1, "R", "setrlimit(RLIMIT_AS)\nте саме, але лише для себе\nі без прав root",
         "#eef7f0", FIELD),
        (2, "L", "MAP_NORESERVE\nвзагалі не рахувати —\nале ЛИШЕ в режимах 0 і 1",
         "#eef3fb", NEG),
        (3, "R", "madvise(MADV_DONTNEED)\nсторінки назад системі,\nобіцянка лишається",
         "#eef3fb", NEG),
        (4, "L", "cgroup v2: memory.max\nвитіснення й OOM\nу межах однієї групи",
         "#eef7f0", FIELD),
        (5, "R", "oom_score_adj\nпереставляє чергу жертв,\nвід OOM не рятує",
         "#fdeeec", POS),
    ]

    for idx, side, s, fill, stroke in levers:
        cy = ys[idx] + SH / 2
        ly = cy - LH / 2
        if side == "L":
            p.append(fitbox(LX, ly, LW, LH, s, size=13,
                            fill=fill, stroke=stroke, sw=1.6))
            p.append(arrow(LX + LW + 6, cy, SX - 6, cy, color=stroke, sw=1.8))
        else:
            p.append(fitbox(RX, ly, RW, LH, s, size=13,
                            fill=fill, stroke=stroke, sw=1.6))
            p.append(arrow(RX - 6, cy, SX + SW + 6, cy, color=stroke, sw=1.8))

    p.append(text(W / 2, 716,
                  "зелене відмовляє чесно, синє міняє облік, червоне тільки обирає, кому вмерти",
                  size=13.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "levers.svg"), W, H, *p)


fig_levers()


# ── Фіг. 6: карта ручок — де саме діє кожен файл ────────────────────────────
# Ідея довідки: перемикачів багато, але кожен чіпляється до СВОЄЇ ланки шляху,
# і головна ланка — друга — не має жодної ручки взагалі.
def fig_knob_map():
    W, H = 1210, 730
    p = []

    p.append(text(W / 2, 34, "ЯКА РУЧКА НА ЯКІЙ ЛАНЦІ ДІЄ", size=15,
                  color=MUTED, bold=True))

    XS = [25, 295, 880]
    CW = [250, 565, 305]
    HY, HH = 54, 40
    heads = ["ланка шляху", "чим керують", "де це видно"]
    for x, w, s in zip(XS, CW, heads):
        p.append(fitbox(x, HY, w, HH, s, size=13, fill="#f4f6f8",
                        stroke=MUTED, sw=1.3, bold=True, color=MUTED))

    rows = [
        ("1 · роздача адрес\nmmap · brk · fork",
         "vm.overcommit_memory · vm.overcommit_ratio\n"
         "vm.overcommit_kbytes · vm.admin_reserve_kbytes\n"
         "vm.user_reserve_kbytes · MAP_NORESERVE · RLIMIT_AS",
         "/proc/meminfo:\nCommitLimit\nCommitted_AS",
         "#eef3fb", NEG),
        ("2 · перший запис\nзбій сторінки",
         "ЖОДНОЇ РУЧКИ. Відмовити тут уже нема як:\n"
         "у запису в пам'ять немає коду повернення",
         "/proc/<pid>/status: VmRSS\n/proc/vmstat: pgfault",
         "#ffffff", MUTED),
        ("3 · витіснення\nkswapd · прямий витіск",
         "vm.min_free_kbytes · vm.swappiness\n"
         "memory.high · memory.low · memory.min\n"
         "memory.swap.max",
         "memory.pressure\n/proc/pressure/memory\nmemory.events: low, high",
         "#eef7f0", FIELD),
        ("4 · вибір жертви",
         "oom_score_adj · vm.oom_kill_allocating_task\n"
         "vm.panic_on_oom · vm.oom_dump_tasks\n"
         "memory.max — межа, у якій шукають",
         "/proc/<pid>/oom_score\ndmesg: таблиця задач",
         "#fdeeec", POS),
        ("5 · убивство",
         "memory.oom.group · OOMPolicy= у юніті systemd",
         "dmesg: «Killed process …»\nmemory.events: oom, oom_kill",
         "#fdeeec", POS),
    ]

    RY, RH, GAP = 108, 110, 14
    for i, (stage, knobs, seen, fill, stroke) in enumerate(rows):
        yy = RY + i * (RH + GAP)
        p.append(fitbox(XS[0], yy, CW[0], RH, stage, size=13.5,
                        fill=fill, stroke=stroke, sw=1.8, bold=True))
        p.append(fitbox(XS[1], yy, CW[1], RH, knobs, size=13,
                        fill="#ffffff", stroke=stroke, sw=1.4))
        p.append(fitbox(XS[2], yy, CW[2], RH, seen, size=13,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))

    p.append(text(W / 2, 712,
                  "усі ручки роздачі стоять до ланки 2, усі ручки вбивства — після неї",
                  size=13.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "knob-map.svg"), W, H, *p)


fig_knob_map()


# ── Фіг. 8: що рухається на кожному кроці прогону лабораторії ───────────────
# Ідея: обіцянка стрибає одразу і повністю, RSS росте сходинками, а стеля —
# нерухома; там, де сходинки дістають стелі, прогін уривається.
def fig_lab_run():
    W, H = 1080, 548
    p = []

    X0, X1 = 110, 880          # межі поля по горизонталі
    YT, YB = 90, 400           # межі поля по вертикалі
    VMAX = 10000.0             # верх шкали, МіБ

    def Y(v):
        return YB - v / VMAX * (YB - YT)

    p.append(text(W / 2, 44, "Один прогін: 8 ГіБ обіцянки на машині з 4 ГіБ пам'яті",
                  size=15, color=INK, bold=True))
    p.append(text(W / 2, 66, "шкала — мебібайти", size=12.5, color=MUTED, italic=True))

    # осі й поділки
    p.append(line(X0, YT, X0, YB, color=MUTED, sw=1.4))
    p.append(line(X0, YB, X1, YB, color=MUTED, sw=1.4))
    for v in (0, 2000, 4000, 6000, 8000, 10000):
        p.append(line(X0 - 5, Y(v), X0, Y(v), color=MUTED, sw=1.2))
        p.append(text(X0 - 12, Y(v) + 4, "%d" % v, size=12, color=MUTED, anchor="end"))

    XM, XW = 202, 765          # мить malloc і мить стіни

    # Committed_AS: стрибок на всі 8 ГіБ у мить malloc
    p.append(line(X0, Y(1454), XM, Y(1454), color=NEG, sw=2.6))
    p.append(line(XM, Y(1454), XM, Y(9646), color=NEG, sw=2.6))
    p.append(line(XM, Y(9646), X1, Y(9646), color=NEG, sw=2.6))
    p.append(text(X1 + 12, Y(9646) - 5, "Committed_AS", size=13.5, color=NEG,
                  anchor="start", bold=True))
    p.append(text(X1 + 12, Y(9646) + 14, "1454 → 9646", size=12.5, color=MUTED,
                  anchor="start"))

    # фізична стеля
    p.append(line(X0, Y(3450), X1, Y(3450), color=MUTED, sw=1.6, dash="7,6"))
    p.append(text(X0 + 12, Y(3450) - 12, "стеля дотику: скільки ядро ще могло віддати",
                  size=12.5, color=MUTED, anchor="start"))

    # VmRSS: сходинки від першого дотику до стіни
    XS, N, TOPV = 264, 10, 3400.0
    px, pv = XS, 0.0
    for i in range(1, N + 1):
        x = XS + (XW - XS) * i / N
        v = TOPV * i / N
        p.append(line(px, Y(pv), x, Y(pv), color=POS, sw=2.6))
        p.append(line(x, Y(pv), x, Y(v), color=POS, sw=2.6))
        px, pv = x, v
    p.append(text(X1 + 12, Y(3400) + 4, "VmRSS", size=13.5, color=POS,
                  anchor="start", bold=True))
    p.append(text(X1 + 12, Y(3400) + 23, "0 → 3400", size=12.5, color=MUTED,
                  anchor="start"))

    # мітки митей під віссю
    for x, s in ((XM, "malloc(8 ГіБ)"), ((XS + XW) / 2, "торкання сторінок"), (XW, "стіна")):
        p.append(line(x, YT, x, YB, color=MUTED, sw=1.0, dash="3,6"))
        p.append(text(x, YB + 24, s, size=12.5, color=MUTED))

    # позначка вбивства
    p.append(line(XW - 9, Y(3400) - 9, XW + 9, Y(3400) + 9, color=POS, sw=3))
    p.append(line(XW - 9, Y(3400) + 9, XW + 9, Y(3400) - 9, color=POS, sw=3))
    p.append(fitbox(786, 186, 268, 62,
                    "звідси процес не повернувся:\nз інструкції запису нікуди",
                    size=12.5, fill="#fdeeec", stroke=POS, sw=1.6))
    p.append(arrow(800, 250, 776, Y(3400) - 14, color=POS, sw=1.8))

    # два висновки внизу, кожен своєю колонкою
    p.append(fitbox(110, 452, 400, 72,
                    "обіцянка: два лічильники стрибнули\nодразу й на весь розмір",
                    size=13, fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(fitbox(560, 452, 410, 72,
                    "дотик: росте лише RSS,\nCommitted_AS стоїть — борг записали раніше",
                    size=13, fill="#fdeeec", stroke=POS, sw=1.6))

    render(os.path.join(OUT, "lab-run.svg"), W, H, *p)


fig_lab_run()
