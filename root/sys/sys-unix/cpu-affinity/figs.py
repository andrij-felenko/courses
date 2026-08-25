# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARMF  = "#fdecea"
COOLF  = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"


# ── 1. Ціна переїзду залежить від відстані ────────────────────────────────────
def fig_migration_distance():
    W, H = 1160, 580
    p = []

    cols = [
        (40, "сусідня нитка\nтого самого ядра",
         [("L1 і L2", "тепла", True),
          ("L3", "тепла", True),
          ("пам'ять", "своя", True)],
         "нічого не охолоджується —\nале блок виконання спільний",
         "ціна не в кеші"),
        (400, "інше ядро\nтого самого кристала",
         [("L1 і L2", "холодна", False),
          ("L3", "тепла", True),
          ("пам'ять", "своя", True)],
         "дані ще на кристалі,\nале доступ до них подовшав",
         "до ≈0.17 мс на 1 МіБ набору"),
        (760, "ядро\nіншого гнізда",
         [("L1 і L2", "холодна", False),
          ("L3", "холодна", False),
          ("пам'ять", "чужа", False)],
         "холодне все, і сторінки\nлишилися на старому гнізді",
         "до ≈2 мс на 1 МіБ набору"),
    ]

    CW = 360
    for x, head, rows, verdict, price in cols:
        p.append(fitbox(x, 56, CW, 56, head, size=15,
                        fill=SOFT, stroke=INK, sw=1.8, color=INK, bold=True))
        for i, (name, state, warm) in enumerate(rows):
            y = 132 + i * 62
            col = FIELD if warm else NEG
            bg = GREENF if warm else COOLF
            p.append(fitbox(x, y, 168, 50, name, size=14,
                            fill=PALE, stroke=MUTED, sw=1.2, color=INK))
            p.append(fitbox(x + 176, y, CW - 176, 50, state, size=14,
                            fill=bg, stroke=col, sw=1.6, color=col, bold=True))
        p.append(fitbox(x, 326, CW, 74, verdict, size=13,
                        fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(x, 416, CW, 48, price, size=13,
                        fill=PALE, stroke=INK, sw=1.4, color=INK, bold=True))

    p.append(fitbox(40, 486, 1080, 56,
                    "переїзд коштує не перемикання контексту, а наповнення холодних сходинок наново;\n"
                    "разова ціна стає податком лише тоді, коли переїзди часті",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "migration-distance.svg"), W, H, *p,
           title="Що охолоджується при переїзді на різну відстань")


# ── 2. Маска задачі проти розділу cpuset ──────────────────────────────────────
def fig_mask_vs_partition():
    W, H = 1180, 600
    p = []

    NC = 8
    BW, GAP = 54, 8
    STRIP = NC * BW + (NC - 1) * GAP          # 496

    def panel(ox, head, headcol, fenced, verdict):
        out = []
        out.append(fitbox(ox, 56, 520, 42, head, size=15,
                          fill=SOFT, stroke=headcol, sw=1.8, color=headcol, bold=True))

        sx = ox + (520 - STRIP) / 2
        cx6 = sx + 6 * (BW + GAP) + BW / 2

        # ваш потік — згори, стрілка вниз рівно на ядро 6
        out.append(fitbox(ox + 150, 116, 220, 44, "ваш потік", size=14,
                          fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))
        out.append(arrow(cx6, 164, cx6, 204, color=FIELD, sw=2.0))

        if fenced:
            fx = sx + 6 * (BW + GAP) - 10
            out.append(rect(fx, 198, 2 * BW + GAP + 20, 74,
                            fill=GREENF, stroke=FIELD, sw=3.0, rx=10))

        for i in range(NC):
            bx = sx + i * (BW + GAP)
            inside = fenced and i >= 6
            out.append(fitbox(bx, 208, BW, 54, str(i), size=15,
                              fill="#ffffff" if not inside else GREENF,
                              stroke=FIELD if inside else MUTED,
                              sw=1.8 if inside else 1.3,
                              color=INK, bold=True))

        # чужі задачі — знизу, стрілки вгору
        out.append(fitbox(ox + 60, 396, 400, 44, "інші задачі системи", size=14,
                          fill=WARMF, stroke=POS, sw=1.6, color=POS, bold=True))

        targets = [0, 2, 5, 6]
        for i in targets:
            bx = sx + i * (BW + GAP) + BW / 2
            if fenced and i == 6:
                out.append(line(bx, 392, bx, 300, color=POS, sw=2.0, dash="6 5"))
            else:
                out.append(arrow(bx, 392, bx, 268, color=POS, sw=2.0))

        out.append(fitbox(ox, 460, 520, 76, verdict, size=13,
                          fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))
        return out

    p.extend(panel(40, "лише маска: sched_setaffinity / taskset", POS, False,
                   "ваш потік більше нікуди не поїде,\n"
                   "але чужі задачі приходять на ядро 6, як приходили"))
    p.extend(panel(620, "розділ cpuset: cpuset.cpus.partition", FIELD, True,
                   "ядра 6–7 вилучено із загального набору;\n"
                   "для чужих задач їх просто немає"))

    p.append(line(590, 56, 590, 536, color="#d7dbe0", sw=1.4, dash="6 6"))

    render(os.path.join(OUT, "mask-vs-partition.svg"), W, H, *p,
           title="Маска обмежує одну задачу, розділ звільняє ядро")


# ── 3. Що все одно потрапляє на ізольоване ядро ───────────────────────────────
def fig_what_still_lands():
    W, H = 1140, 620
    p = []

    left = [
        (70,  "переривання пристроїв", "/proc/irq/<n>/smp_affinity_list"),
        (196, "потоки ядра цього ядра", "перенести не можна;\nRCU виносять через rcu_nocbs="),
        (322, "тік таймера", "nohz_full= (поки задача одна)"),
    ]
    right = [
        (70,  "міжпроцесорні виклики", "вимикача немає взагалі"),
        (196, "сусідня нитка SMT", "брати в розділ ОБИДВІ нитки"),
    ]

    LW, RW = 330, 330
    LX, RX = 40, W - 40 - RW

    for y, name, knob in left:
        p.append(fitbox(LX, y, LW, 44, name, size=14,
                        fill=WARMF, stroke=POS, sw=1.6, color=POS, bold=True))
        p.append(fitbox(LX, y + 46, LW, 50, knob, size=12,
                        fill=PALE, stroke=MUTED, sw=1.1, color=INK))

    for y, name, knob in right:
        p.append(fitbox(RX, y, RW, 44, name, size=14,
                        fill=WARMF, stroke=POS, sw=1.6, color=POS, bold=True))
        p.append(fitbox(RX, y + 46, RW, 50, knob, size=12,
                        fill=PALE, stroke=MUTED, sw=1.1, color=INK))

    CX, CY, CWD, CHT = 420, 176, 300, 128
    p.append(fitbox(CX, CY, CWD, CHT,
                    "ізольоване ядро\n\ncpuset і маска керують\nтут лише задачами",
                    size=14, fill=GREENF, stroke=FIELD, sw=2.4, color=INK, bold=True))

    p.append(arrow(LX + LW + 8, 104, CX - 8, 206, color=POS, sw=1.8))
    p.append(arrow(LX + LW + 8, 230, CX - 8, 240, color=POS, sw=1.8))
    p.append(arrow(LX + LW + 8, 356, CX - 8, 274, color=POS, sw=1.8))
    p.append(arrow(RX - 8, 104, CX + CWD + 8, 212, color=POS, sw=1.8))
    p.append(arrow(RX - 8, 230, CX + CWD + 8, 258, color=POS, sw=1.8))

    p.append(fitbox(40, 440, W - 80, 72,
                    "порядок дій не переставляється: спершу відвести ядра розділом (парами SMT-сусідів),\n"
                    "потім перенести переривання, потім вимкнути тік і зворотні виклики RCU —\n"
                    "і аж наприкінці прив'язувати власні потоки масками",
                    size=13, fill=SOFT, stroke=INK, sw=1.4, color=INK))

    p.append(text(W / 2, 552,
                  "зроблена лише остання дія дає прив'язку без ізоляції",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "what-still-lands.svg"), W, H, *p,
           title="Що потрапляє на ізольоване ядро попри cpuset")


# ── 4. Як прилад ловить украдений час ─────────────────────────────────────────
def fig_stolen_time():
    import math
    W, H = 1120, 562
    p = []

    # верхній ряд підписів
    p.append(fitbox(80, 58, 350, 48,
                    "тісний цикл: різниця між\nсусідніми читаннями ≈ 25 нс",
                    size=13, fill=COOLF, stroke=NEG, sw=1.6, color=INK))
    p.append(fitbox(452, 58, 316, 48,
                    "пауза 180 мкс —\nтут біг хтось інший",
                    size=13, fill=WARMF, stroke=POS, sw=1.8, color=INK, bold=True))
    p.append(fitbox(790, 58, 270, 48,
                    "і знову ≈ 25 нс",
                    size=13, fill=COOLF, stroke=NEG, sw=1.6, color=INK))

    for cx in (255, 610, 925):
        p.append(line(cx, 106, cx, 143, color=MUTED, sw=1.2, dash="4,4"))

    # вісь часу з позначками читань годинника
    AY = 156
    p.append(line(60, AY, 1060, AY, color=INK, sw=2))
    x = 74
    while x < 468:
        p.append(line(x, AY - 11, x, AY + 11, color=NEG, sw=1.6))
        x += 16
    x = 764
    while x < 1054:
        p.append(line(x, AY - 11, x, AY + 11, color=NEG, sw=1.6))
        x += 16
    p.append(rect(472, 132, 288, 48, fill=WARMF, stroke=POS, sw=2, rx=8))
    p.append(text(1058, 202, "час →", size=12, color=MUTED, anchor="end"))

    # розділювальний підпис
    p.append(fitbox(60, 216, 1000, 38,
                    "кожну різницю кладемо в кошик за старшим бітом — так на одному рисунку "
                    "видно і мільйони дрібниць, і одиничні паузи",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))

    # гістограма
    BY = 452
    counts = [1180000000, 62000000, 1200000, 3800, 610, 44, 6, 1]
    shown  = ["1.18 млрд", "62 млн", "1.2 млн", "3 800", "610", "44", "6", "1"]
    names  = ["16–32\nнс", "32–64\nнс", "64–128\nнс", "512–1024\nнс",
              "4–8\nмкс", "32–64\nмкс", "128–256\nмкс", "1–2\nмс"]
    p.append(line(72, BY, 1048, BY, color=INK, sw=1.8))
    for i, c in enumerate(counts):
        bx = 100 + i * 120
        h = 16 + 17 * math.log10(c) if c > 1 else 16
        cool = i <= 2
        p.append(rect(bx, BY - h, 88, h,
                      fill=COOLF if cool else WARMF,
                      stroke=NEG if cool else POS, sw=1.8, rx=4))
        p.append(text(bx + 44, BY - h - 8, shown[i], size=12,
                      color=NEG if cool else POS, bold=True))
        p.append(fitbox(bx, 458, 88, 36, names[i], size=11,
                        fill=PALE, stroke=MUTED, sw=1.1, color=INK))

    p.append(fitbox(60, 504, 1000, 44,
                    "сині кошики — власна вартість вимірювання (читання годинника й виток циклу);\n"
                    "червоні — час, коли задача не бігла: саме його прибирає ізоляція. Висота стовпчика логарифмічна.",
                    size=12, fill=SOFT, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "stolen-time.svg"), W, H, *p,
           title="Прилад: різниця між сусідніми читаннями годинника")


fig_migration_distance()
fig_mask_vs_partition()
fig_what_still_lands()
fig_stolen_time()
print("ok")
