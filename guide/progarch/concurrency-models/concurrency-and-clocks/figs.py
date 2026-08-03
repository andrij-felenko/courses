# -*- coding: utf-8 -*-
"""Фігури до кроку «Годинник і монотонність у конкурентності»
(guide/progarch/concurrency-models/concurrency-and-clocks)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")

GREEN_F = "#eafaf1"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"
RED_F = "#fdecea"


def cbox(cx, cy, w, h, s, **kw):
    """Рамка з центром (cx,cy) — текст автоматично влазить (fitbox)."""
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def two_clocks():
    """Два прилади під одним словом «годинник»: настінний (стрибає) vs монотонний (тільки вгору)."""
    W, H = 880, 430
    f = []
    # роздільник
    f.append(line(440, 40, 440, 392, color=MUTED, dash="5 5"))

    # ── ЛІВОРУЧ: настінний годинник ──
    LX = 228
    f.append(circle(LX, 168, 60, fill=FILL, stroke=LINE, sw=2))
    f.append(line(LX, 168, LX, 120))          # хвилинна вгору
    f.append(line(LX, 168, LX + 42, 168))     # годинна праворуч
    f.append(circle(LX, 168, 4, fill=INK, stroke=INK))
    # стрибки в обидва боки
    f.append(arrow(158, 168, 104, 168, color=POS))
    f.append(text(128, 158, "назад", size=12, color=POS))
    f.append(arrow(298, 168, 352, 168, color=POS))
    f.append(text(326, 158, "вперед", size=12, color=POS))
    f.append(cbox(LX, 288, 280, 46, "коригується ззовні:\nNTP · висока секунда · адмін",
                  size=12, fill=AMBER_F, stroke=AMBER_S))
    f.append(text(LX, 360, "питання: котра година?", size=15, bold=True))

    # ── ПРАВОРУЧ: монотонний годинник ──
    RX = 650
    f.append(cbox(RX, 150, 168, 54, "0 0 4 7 2 3", size=20, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(arrow(RX, 250, RX, 210, color=FIELD))
    f.append(text(RX, 272, "тільки вперед · без корекції", size=12, color=FIELD))
    f.append(cbox(RX, 320, 220, 40, "не знає дати", size=13, fill=GREEN_F, stroke=FIELD))
    f.append(text(RX, 380, "питання: скільки минуло?", size=15, bold=True))

    render(os.path.join(IMG, "two-clocks.svg"), W, H, *f)


def timeout_jump():
    """Той самий 30-с дедлайн на настінному (стрибок ламає) і монотонному (виміряно чесно)."""
    W, H = 900, 500
    f = []

    # ── ВЕРХНЯ доріжка: настінний ──
    ay = 175
    f.append(cbox(82, ay, 104, 46, "настінний\nгодинник", size=12, fill=AMBER_F, stroke=AMBER_S))
    f.append(arrow(150, ay, 840, ay))
    # старт
    f.append(line(200, ay - 8, 200, ay + 8))
    f.append(text(200, ay + 28, "старт", size=12, color=MUTED))
    # дедлайн
    f.append(line(600, ay - 12, 600, ay + 12))
    f.append(text(600, ay - 24, "дедлайн = старт + 30 с", size=12))
    # стрибок
    f.append(arrow(250, ay - 62, 690, ay - 62, color=POS))
    f.append(text(410, ay - 74, "NTP смикнув годинник уперед", size=12, color=POS))
    f.append(line(690, ay - 8, 690, ay + 8, color=POS, sw=2))
    f.append(text(690, ay + 28, "тепер", size=12, color=POS))
    f.append(cbox(500, ay + 78, 380, 40, "тепер уже за дедлайном → чекали 0 с",
                  size=13, fill=RED_F, stroke=POS))

    # ── НИЖНЯ доріжка: монотонний ──
    by = 375
    f.append(cbox(82, by, 104, 46, "монотонний\nгодинник", size=12, fill=GREEN_F, stroke=FIELD))
    f.append(arrow(150, by, 840, by))
    f.append(line(200, by - 8, 200, by + 8))
    f.append(text(200, by + 28, "старт (лічильник = 0)", size=12, color=MUTED))
    # рівномірні поділки — «рахує рівно»
    for x in (300, 400, 500):
        f.append(line(x, by - 5, x, by + 5, color=FIELD))
    f.append(line(600, by - 12, 600, by + 12, color=FIELD, sw=2))
    f.append(text(600, by - 24, "минуло рівно 30 с", size=12, color=FIELD))
    f.append(cbox(500, by + 78, 380, 40, "тривалість виміряно чесно → таймаут о 30 с",
                  size=13, fill=GREEN_F, stroke=FIELD))

    render(os.path.join(IMG, "timeout-jump.svg"), W, H, *f)


def order_from_sync():
    """Мітки часу двох потоків не дають порядку; його дає ребро синхронізації."""
    W, H = 1012, 430
    f = []
    # доріжки
    f.append(text(96, 150, "потік A", size=13, color=MUTED, anchor="end"))
    f.append(line(140, 155, 800, 155, color=LINE))
    f.append(text(96, 300, "потік B", size=13, color=MUTED, anchor="end"))
    f.append(line(140, 300, 800, 300, color=LINE))

    # події A
    f.append(circle(250, 155, 7, fill=FILL, stroke=LINE))
    f.append(text(250, 133, "10.7", size=12))
    f.append(circle(520, 155, 8, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(520, 133, "10.9", size=12))
    f.append(text(520, 116, "пише X", size=11, color=FIELD))
    # події B
    f.append(circle(300, 300, 7, fill=FILL, stroke=LINE))
    f.append(text(300, 326, "10.7", size=12))
    f.append(circle(560, 300, 8, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(560, 326, "10.9", size=12))
    f.append(text(560, 344, "читає X", size=11, color=FIELD))

    # однакові мітки — порядок невідомий
    f.append(line(250, 165, 300, 290, color=POS, dash="4 4"))
    f.append(text(238, 235, "?", size=26, color=POS, bold=True))
    f.append(text(300, 235, "однакова мітка —\nхто раніше?", size=12, color=POS, anchor="start"))

    # ребро «відбулося-до»
    f.append(arrow(520, 165, 560, 290, color=FIELD, sw=2))
    f.append(text(600, 225, "ребро «відбулося-до»:\nB читає те, що записав A\n→ ось тут порядок є",
                  size=12, color=FIELD, anchor="start"))
    render(os.path.join(IMG, "order-from-sync.svg"), W, H, *f)


def monotonic_ladder():
    """Сходи «щось, що тільки росте»: від монотонного годинника до логічних годинників."""
    W, H = 900, 460
    f = []
    steps = [
        (185, 385, 190, 56, "годиннику\nне можна вірити", RED_F, POS, 13),
        (375, 308, 196, 56, "монотонний годинник\n→ тривалості", GREEN_F, FIELD, 13),
        (595, 231, 226, 56, "номер · версія · епоха ·\nжетон → порядок", GREEN_F, FIELD, 12),
        (785, 154, 208, 56, "логічні годинники\n(далі, з мережею)", FILL, MUTED, 13),
    ]
    for cx, cy, w, h, s, fill, stroke, sz in steps:
        f.append(cbox(cx, cy, w, h, s, size=sz, fill=fill, stroke=stroke,
                      bold=(fill == GREEN_F)))
    # короткі стрілки-сходинки між боксами (не перетинають текст)
    f.append(arrow(282, 360, 300, 335, color=FIELD))
    f.append(arrow(475, 283, 495, 258, color=FIELD))
    f.append(arrow(700, 206, 690, 181, color=FIELD))
    f.append(text(452, 438, "кожна сходинка — щось, що тільки зростає", size=13, color=MUTED))
    render(os.path.join(IMG, "monotonic-ladder.svg"), W, H, *f)


def leap_timeline():
    """Хроніка високосної секунди: народження 1972 → аварії 2012 і 2017 → скасування 2022."""
    W, H = 1000, 430
    f = []
    axy = 215
    f.append(arrow(56, axy, 944, axy))
    # довга пауза 1972 → 2012 (злам-позначка + підпис)
    f.append(line(298, axy - 7, 292, axy + 7, color=MUTED))
    f.append(line(312, axy - 7, 306, axy + 7, color=MUTED))
    f.append(text(345, axy - 12, "…сорок років…", size=12, color=MUTED, italic=True))

    # (x, рік, центр_бокса_y, «above»/«below», заливка, обвід, підпис)
    events = [
        (150, "1972", 320, "below", FILL,    MUTED,
         "висока секунда народжується:\nIERS латає час вручну"),
        (470, "2012", 108, "above", RED_F,   POS,
         "Linux: таймери спрацьовують\nна секунду раніше → 100% CPU"),
        (690, "2017", 322, "below", RED_F,   POS,
         "Cloudflare: t₂ − t₁ < 0\n→ Go панікує на rand.Int63n"),
        (870, "2022", 108, "above", GREEN_F, FIELD,
         "CGPM №4: скасувати\nвисоку секунду до 2035"),
    ]
    for x, year, bcy, side, fill, stroke, label in events:
        f.append(circle(x, axy, 7, fill=fill, stroke=stroke, sw=2.5))
        if side == "above":
            f.append(line(x, axy - 7, x, bcy + 27, color=MUTED, dash="3 3"))
            f.append(text(x, axy + 26, year, size=16, bold=True))
        else:
            f.append(line(x, axy + 7, x, bcy - 27, color=MUTED, dash="3 3"))
            f.append(text(x, axy - 15, year, size=16, bold=True))
        f.append(cbox(x, bcy, 244, 54, label, size=13, fill=fill, stroke=stroke,
                      bold=(fill != FILL)))

    f.append(text(W / 2.0, 404,
                  "щоразу настінний час хитнувся — і ламався код, що міряв ним тривалість",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "leap-timeline.svg"), W, H, *f)


def budget_chain():
    """Один бюджет 30 с тече крізь connect→read→parse; кожен крок бере залишок."""
    W, H = 940, 240
    f = []
    X0, X1, TOP, BOT = 120, 860, 110, 155
    pps = (X1 - X0) / 30.0                      # пікселів на секунду

    def at(sec):
        return X0 + sec * pps

    f.append(text(X0, 92, "монотонний бюджет: 30 с", size=13, color=MUTED, anchor="start"))
    segs = [(0, 8, "connect", GREEN_F, FIELD),
            (8, 22, "read", GREEN_F, FIELD),
            (22, 27, "parse", GREEN_F, FIELD),
            (27, 30, "запас", FILL, MUTED)]
    for a, b, name, fill, stroke in segs:
        x, w = at(a), (b - a) * pps
        f.append(rect(x, TOP, w, BOT - TOP, fill=fill, stroke=stroke))
        f.append(text(x + w / 2, TOP + 29, name, size=14, bold=True,
                      color=(INK if fill == GREEN_F else MUTED)))
    marks = [(0, "старт · 30 с", "start"), (8, "лишилось 22 с", "middle"),
             (22, "лишилось 8 с", "middle"), (27, "лишилось 3 с", "middle")]
    for sec, lbl, anc in marks:
        x = at(sec)
        f.append(line(x, BOT, x, BOT + 15, color=MUTED))
        f.append(text(x, 192, lbl, size=12, anchor=anc))
    render(os.path.join(IMG, "budget-chain.svg"), W, H, *f)


def backoff_jitter():
    """Повний джитер: вікно росте вдвічі, впирається в cap, обрізається дедлайном."""
    W, H = 940, 370
    f = []
    X0 = 160
    pps = 480.0                                 # 1 с = 480 px
    rows = [80, 135, 190, 245, 300]
    wins = [0.1, 0.2, 0.4, 0.8, 1.0]            # 4-та спроба: 1.6 обрізано до cap=1.0
    fracs = [0.55, 0.30, 0.70, 0.40, 0.82]      # де випав кубик усередині вікна
    for i, (y, win, fr) in enumerate(zip(rows, wins, fracs)):
        w = win * pps
        f.append(rect(X0, y - 13, w, 26, fill=FILL, stroke=MUTED))
        f.append(circle(X0 + w * fr, y, 6, fill=FIELD, stroke=FIELD))
        f.append(text(140, y + 5, "спроба %d" % i, size=13, color=MUTED, anchor="end"))
    f.append(arrow(X0, 335, 800, 335))
    for sec, lbl in ((0.5, "0,5 с"), (1.0, "1,0 с")):
        x = X0 + sec * pps
        f.append(line(x, 331, x, 339, color=MUTED))
        f.append(text(x, 353, lbl, size=12, color=MUTED))
    f.append(text(730, 353, "пауза, с", size=12, color=MUTED, anchor="start"))
    xc = X0 + 1.0 * pps
    f.append(line(xc, 60, xc, 320, color=AMBER_S, dash="5 5"))
    f.append(text(xc - 8, 50, "стеля cap = 1 с", size=12, color=AMBER_S, anchor="end"))
    xd = X0 + 1.25 * pps
    f.append(line(xd, 60, xd, 320, color=POS, dash="4 4"))
    f.append(text(xd + 8, 50, "дедлайн бюджету", size=12, color=POS, anchor="start"))
    f.append(text(xd + 8, 68, "далі — стоп", size=11, color=POS, anchor="start"))
    render(os.path.join(IMG, "backoff-jitter.svg"), W, H, *f)


def fencing_race():
    """Гонка застряглого власника ліза (Клеппманн): жетон 33 vs 34."""
    W, H = 980, 440
    f = []
    ay, by = 150, 330
    f.append(text(95, ay + 5, "робітник А", size=13, color=MUTED, anchor="end"))
    f.append(line(110, ay, 720, ay, color=LINE))
    f.append(text(95, by + 5, "робітник Б", size=13, color=MUTED, anchor="end"))
    f.append(line(110, by, 720, by, color=LINE))

    f.append(circle(175, ay, 7, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(175, ay - 25, "бере лізу · жетон 33", size=12))
    f.append(rect(215, ay - 56, 250, 32, fill=AMBER_F, stroke=AMBER_S))
    f.append(text(340, ay - 35, "пауза GC (stop-the-world)", size=12, color=AMBER_S))
    f.append(line(430, ay + 16, 430, ay + 55, color=POS, dash="4 4"))
    f.append(text(430, ay + 72, "ліза збігла", size=11, color=POS))
    f.append(circle(560, ay, 7, fill=RED_F, stroke=POS, sw=2))
    f.append(text(560, ay - 25, "прокинувся · write(33)", size=12, color=POS))
    f.append(line(568, ay, 568, 208, color=POS))
    f.append(arrow(568, 208, 748, 208, color=POS))
    f.append(text(658, 189, "33 < 34  ✗ відкинуто", size=12, color=POS))

    f.append(circle(300, by, 7, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(300, by + 26, "бере лізу · жетон 34", size=12))
    f.append(circle(470, by, 7, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(470, by + 26, "write(34)", size=12, color=FIELD))
    f.append(line(478, by, 478, 258, color=FIELD))
    f.append(arrow(478, 258, 748, 258, color=FIELD))
    f.append(text(613, 276, "34  ✓ прийнято", size=12, color=FIELD))

    f.append(cbox(850, 232, 194, 96, "СХОВИЩЕ\nбачений максимум\nжетон = 34",
                  size=13, fill=FILL, stroke=LINE, bold=True))
    render(os.path.join(IMG, "fencing-race.svg"), W, H, *f)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    two_clocks()
    timeout_jump()
    order_from_sync()
    monotonic_ladder()
    leap_timeline()
    budget_chain()
    backoff_jitter()
    fencing_race()
    print("ok")
