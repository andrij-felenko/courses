# -*- coding: utf-8 -*-
"""Фігури до кроку «Матеріалізація проти кешу проти читання наживо».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GOLD   = "#c9a93b"
GOLDF  = "#fff2cc"
GREENF = "#eafaf0"
REDF   = "#fdecea"
NEU    = "#eef2f6"


# ───────── Фіг. 1: одна вісь — коли робиться похідна робота ─────────
def fig_when_work():
    W, H = 1040, 520
    f = []

    # легенда під заголовком
    f.append(text(W / 2, 54,
                  "золотий круг = важке обчислення з джерела     ·     "
                  "W = запис     ·     R = читання",
                  size=13, color=MUTED, bold=True))

    x1, x2 = 250, 830
    writes = [300, 540]
    reads = [370, 440, 610, 680, 750]

    lanes = [
        (150, "Читання наживо", reads,
         "важке обчислення на КОЖНЕ читання — читач завжди чекає", POS),
        (300, "Кеш", [370, 610],
         "обчислення лише на першому читанні після зміни — далі влучання", GOLD),
        (450, "Матеріалізація", writes,
         "обчислення наперед на КОЖЕН запис — жоден читач не чекає", FIELD),
    ]

    for ly, lab, computes, ann, acol in lanes:
        # ліва мітка доріжки
        b, _, _ = textbox(120, ly, lab, size=13, bold=True,
                          fill=FILL, stroke=INK, sw=1.8)
        f.append(b)
        # часова вісь
        f.append(line(x1, ly, x2, ly, color=INK, sw=2))
        f.append(text(x2 + 6, ly + 4, "час", size=11, color=MUTED,
                      anchor="start", italic=True))
        # позначки записів і читань під віссю
        for wx in writes:
            f.append(line(wx, ly - 7, wx, ly + 7, color=NEG, sw=2.4))
            f.append(text(wx, ly + 25, "W", size=13, color=NEG, bold=True))
        for rx in reads:
            f.append(line(rx, ly - 6, rx, ly + 6, color=MUTED, sw=1.6))
            f.append(text(rx, ly + 25, "R", size=12, color=MUTED, bold=True))
        # золоті круги — важке обчислення — над віссю
        for cx in computes:
            f.append(line(cx, ly - 8, cx, ly - 24, color=GOLD, sw=1.4))
            f.append(circle(cx, ly - 35, 12, fill=GOLDF, stroke=GOLD, sw=2.4))
        # підпис-висновок під доріжкою
        f.append(text(540, ly + 52, ann, size=12.5, color=acol, bold=True))

    render(os.path.join(IMG, "when-work-happens.svg"), W, H, *f,
           title="Три стратегії — одна вісь: коли роблять похідну роботу")


# ───────── Фіг. 2: матриця порівняння за сімома вимірами ─────────
def fig_matrix():
    W, H = 1130, 430
    f = []

    labx, labw = 18, 152
    cxs = [176, 310, 444, 578, 712, 846, 980]
    cw = 128

    headers = ["Коли\nробота", "Свіжість", "Ціна\nчитання", "Ціна\nзапису",
               "Покриття", "Якщо копія\nзникла", "Джерело\nправди"]
    hy, hh = 60, 44
    f.append(fitbox(labx, hy, labw, hh, "стратегія \\ вимір",
                    size=11, fill=NEU, stroke=MUTED, bold=True))
    for x, hd in zip(cxs, headers):
        f.append(fitbox(x, hy, cw, hh, hd, size=12, fill=NEU, stroke=MUTED, bold=True))

    G = (GREENF, FIELD)
    A = (GOLDF, GOLD)
    R = (REDF, POS)
    N = (NEU, MUTED)

    rows = [
        ("Читання\nнаживо", (FILL, INK), [
            ("кожне\nчитання", N), ("завжди\nсвіже", G), ("висока", R),
            ("нуль", G), ("—", N), ("нема що\nзникати", G), ("одне", G)]),
        ("Кеш", (GOLDF, GOLD), [
            ("перший\nпромах", N), ("може\nзастаріти", A), ("низька\n(влучання)", G),
            ("інвалі-\nдація", A), ("гаряча\nпідмнож.", A),
            ("промах +\nперерахунок", G), ("друге,\nодноразове", A)]),
        ("Матеріалі-\nзація", (GREENF, FIELD), [
            ("кожен\nзапис", N), ("лаг\nоновлення", A), ("низька", G),
            ("підтримка\nщоразу", R), ("усі\nключі", G),
            ("простій,\nвідбудова", R), ("друге,\nпостійне", R)]),
    ]

    ry, rh = 110, 94
    for i, (name, (nf, ns), cells) in enumerate(rows):
        y = ry + i * (rh + 4)
        f.append(fitbox(labx, y, labw, rh, name, size=13, fill=nf, stroke=ns, bold=True))
        for x, (txt, (cf, cs)) in zip(cxs, cells):
            f.append(fitbox(x, y, cw, rh, txt, size=12, fill=cf, stroke=cs,
                            bold=(cf != NEU)))

    render(os.path.join(IMG, "three-way-matrix.svg"), W, H, *f,
           title="Читання наживо · Кеш · Матеріалізація — за сімома вимірами")


# ───────── Фіг. 3: три стратегії шаруються ─────────
def fig_layers():
    W, H = 1020, 480
    f = []

    b, cw_, _ = textbox(140, 120, "запит:\nмісячні\nкВт·год", size=13, bold=True,
                        fill=FILL, stroke=INK, sw=2)
    f.append(b)

    bx1, bx2 = 340, 800
    bh = 60
    rows = [
        (120, "1 · Кеш — гаряча жменя домів", GOLD, GOLDF),
        (250, "2 · Матеріалізований денний агрегат — усі доми", INK, NEU),
        (380, "3 · Сирі виміри — джерело правди · незмінні", FIELD, GREENF),
    ]
    for ly, lab, stroke, fill in rows:
        f.append(fitbox(bx1, ly - bh / 2, bx2 - bx1, bh, lab,
                        size=14, fill=fill, stroke=stroke, bold=True, sw=2.4))

    # запит → шар 1, і відповідь назад
    f.append(arrow(140 + cw_ / 2, 112, bx1, 112, color=INK, sw=2))
    f.append(arrow(bx1, 132, 140 + cw_ / 2, 132, color=FIELD, sw=2))
    f.append(text((140 + cw_ / 2 + bx1) / 2, 98, "відповідь",
                  size=11, color=FIELD, bold=True))

    # падіння вниз на промах (праворуч)
    downs = [(152, 218, "промах"), (282, 348, "діра — треба свіже")]
    for y1, y2, lab in downs:
        f.append(arrow(700, y1, 700, y2, color=POS, sw=2))
        f.append(text(716, (y1 + y2) / 2 + 4, lab, size=11.5, color=POS,
                      bold=True, anchor="start"))

    # повернення відповіді вгору (ліворуч)
    ups = [(348, 282, "порахувати,\nпідсипати вгору"),
           (218, 152, "сумувати,\nнаповнити кеш")]
    for y1, y2, lab in ups:
        f.append(arrow(440, y1, 440, y2, color=FIELD, sw=2))
        f.append(mtext(424, (y1 + y2) / 2 - 3, lab, size=11, color=FIELD,
                       anchor="end", bold=True))

    render(os.path.join(IMG, "layered-read-path.svg"), W, H, *f,
           title="Три стратегії не виключають одна одну — вони шаруються")


# ───────── Фіг. 4: три прямі ціни — беззбитковість від обсягу читань ─────────
def fig_three_costs():
    W, H = 1060, 560
    f = []

    # модельні параметри (умовні одиниці, щоб три регіони було видно)
    Cr = 1.00           # нахил живого читання
    s_cache, o_cache = 0.45, 0.50   # (1−h)·C_r  ·  W·C_i (інвалідація)
    s_mat,   o_mat   = 0.05, 2.20   # C_d        ·  W·C_m + S (підтримка+місце)
    Rmax, ymax = 8.0, 4.0

    x0, x1, yb, yt = 120, 960, 470, 110

    def X(r):
        return x0 + (x1 - x0) * (r / Rmax)

    def Y(c):
        c = min(c, ymax)
        return yb - (yb - yt) * (c / ymax)

    r1 = o_cache / (Cr - s_cache)                 # наживо × кеш
    r2 = (o_mat - o_cache) / (s_cache - s_mat)    # кеш × матеріалізація
    c1 = o_cache + s_cache * r1
    c2 = o_cache + s_cache * r2

    # смуги регіонів
    f.append(rect(x0, yt, X(r1) - x0, yb - yt, fill=GREENF, stroke=GREENF, sw=0))
    f.append(rect(X(r1), yt, X(r2) - X(r1), yb - yt, fill=GOLDF, stroke=GOLDF, sw=0))
    f.append(rect(X(r2), yt, x1 - X(r2), yb - yt, fill="#eaf1fb", stroke="#eaf1fb", sw=0))

    # осі
    f.append(line(x0, yb, x1, yb, color=INK, sw=2))
    f.append(line(x0, yt, x0, yb, color=INK, sw=2))
    f.append(text((x0 + x1) / 2, yb + 44, "читань за період   R  →", size=14, color=INK, bold=True))
    f.append(mtext(x0 - 12, (yt + yb) / 2 - 6, "сукупна\nціна за\nперіод", size=12, color=INK,
                   anchor="end", bold=True))

    # прямі: наживо (з нуля, круто), кеш, матеріалізація (пологá з відступом)
    r_live = ymax / Cr
    f.append(line(X(0), Y(0), X(r_live), Y(ymax), color=POS, sw=3))
    r_cache = min(Rmax, (ymax - o_cache) / s_cache)
    f.append(line(X(0), Y(o_cache), X(r_cache), Y(o_cache + s_cache * r_cache), color=GOLD, sw=3))
    f.append(line(X(0), Y(o_mat), X(Rmax), Y(o_mat + s_mat * Rmax), color=FIELD, sw=3))

    # точки беззбитковості
    for rr, cc, lab in [(r1, c1, "R₁"), (r2, c2, "R₂")]:
        f.append(line(X(rr), yb, X(rr), Y(cc), color=MUTED, sw=1.4, dash="5,4"))
        f.append(circle(X(rr), Y(cc), 6, fill=BG, stroke=INK, sw=2))
        f.append(text(X(rr), yb + 22, lab, size=13, color=INK, bold=True))

    # підписи регіонів угорі
    f.append(mtext((x0 + X(r1)) / 2, yt + 24, "читай\nнаживо", size=12.5, color=FIELD, bold=True))
    f.append(text((X(r1) + X(r2)) / 2, yt + 20, "кешуй", size=14, color="#9a7d16", bold=True))
    f.append(text((X(r2) + x1) / 2, yt + 20, "матеріалізуй", size=14, color=FIELD, bold=True))

    # підписи прямих
    f.append(text(X(r_live) + 6, Y(ymax) + 4, "наживо   R·C_r", size=12.5, color=POS,
                  bold=True, anchor="start"))
    f.append(text(X(6.0) - 4, Y(o_cache + s_cache * 6.0) - 10, "кеш   R·(1−h)·C_r + W·C_i",
                  size=12.5, color="#9a7d16", bold=True, anchor="end"))
    f.append(text(x1 - 6, Y(o_mat + s_mat * Rmax) + 20, "матеріалізація   W·C_m + R·C_d",
                  size=12.5, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(IMG, "math-three-costs.svg"), W, H, *f,
           title="Три стратегії — три прямі ціни; найдешевша міняється з обсягом читань")


# ───────── Фіг. 5: кеш — повзунок ефективної ціни між двома кутами ─────────
def fig_cache_ladder():
    import math
    W, H = 860, 520
    f = []

    xa, yt, yb = 250, 110, 460
    top, bot = 0.0, -3.0   # десяткові порядки: 10⁰ … 10⁻³

    def Y(cost):
        e = max(bot, min(top, math.log10(cost)))
        return yt + (yb - yt) * (top - e) / (top - bot)

    # зона, куди дотягується кеш (від живого до стелі влучності)
    yceil = Y(0.1)
    f.append(rect(xa - 6, Y(1.0), 470, yceil - Y(1.0), fill=GOLDF, stroke=GOLDF, sw=0))

    # вісь-стрілка вниз = дешевше
    f.append(arrow(xa, yt - 26, xa, yb + 26, color=INK, sw=2))
    f.append(mtext(xa - 16, (yt + yb) / 2 - 10, "ефективна\nціна одного\nчитання (log)",
                   size=12, color=INK, anchor="end", bold=True))
    f.append(text(xa - 16, yb + 20, "дешевше ↓", size=11.5, color=MUTED, anchor="end", italic=True))

    rungs = [
        (1.0,    POS,   "LIVE  ·  h = 0",   "ефективна ціна = C_r  — повний перерахунок щоразу"),
        (0.5,    GOLD,  "кеш  h = 0.5",     "→ 0.5 · C_r"),
        (0.1,    GOLD,  "кеш  h = 0.9",     "→ 0.1 · C_r"),
        (0.01,   GOLD,  "кеш  h = 0.99",    "→ 0.01 · C_r   (лише за рідкісних записів)"),
        (0.0013, FIELD, "МАТЕРІАЛІЗАЦІЯ",   "читання з готового ≈ C_d — підлога для всіх ключів"),
    ]
    for cost, col, lab, sub in rungs:
        y = Y(cost)
        f.append(line(xa, y, xa + 40, y, color=col, sw=3))
        f.append(circle(xa, y, 5, fill=BG, stroke=col, sw=2.4))
        f.append(text(xa + 52, y - 4, lab, size=13.5, color=col, anchor="start", bold=True))
        f.append(text(xa + 52, y + 14, sub, size=11.5, color=MUTED, anchor="start"))

    # стеля влучності від записів (підпис відсунуто правіше — щоб не лягав
    # на власний підпис рядка 0.1-h, який займає x≈302..362 у цьому ж рядку)
    ceil_x = xa + 410
    f.append(line(xa - 80, yceil, ceil_x, yceil, color=NEG, sw=1.8, dash="7,5"))
    f.append(text(ceil_x, yceil - 9, "стеля влучності від записів/TTL",
                  size=12, color=NEG, anchor="end", bold=True))
    f.append(text(ceil_x, yceil + 15, "нижче кеш не пускають записи — див. модуль 13",
                  size=11, color=NEG, anchor="end"))

    render(os.path.join(IMG, "math-cache-ladder.svg"), W, H, *f,
           title="Кеш — повзунок ефективної ціни між живим читанням і матеріалізацією")


# ═════════ Фігури ВСТАВКИ proj-derived-value-three-ways ═════════

# ───────── Проєкт-фіг. 1: три виміряні ціни (числа) ─────────
def fig_prices():
    W, H = 1180, 440
    f = []

    labx, labw = 18, 168
    cxs = [200, 396, 592, 788, 984]
    cw = 188

    headers = ["Затримка\nчитання", "Ціна\nзапису", "Застарілість",
               "Похідне\nсховище", "Якщо копію\nвтрачено"]
    hy, hh = 62, 46
    f.append(fitbox(labx, hy, labw, hh, "спосіб \\ ціна",
                    size=12, fill=NEU, stroke=MUTED, bold=True))
    for x, hd in zip(cxs, headers):
        f.append(fitbox(x, hy, cw, hh, hd, size=12.5, fill=NEU, stroke=MUTED, bold=True))

    G = (GREENF, FIELD)
    A = (GOLDF, GOLD)
    R = (REDF, POS)

    rows = [
        ("Наживо", (FILL, INK), [
            ("~60 мс\n(скан 260 тис.)", R), ("1×\n(базовий INSERT)", G),
            ("0 —\nзавжди свіже", G), ("0 байтів", G),
            ("нема що\nвтрачати", G)]),
        ("Матеріа-\nлізація", (GREENF, FIELD), [
            ("~0.3 мс\n(30 рядків)", G), ("2× + гарячий\nрядок дня", R),
            ("0 тригер …\nсек CDC", A), ("+30 рядків\n≈ 2 КБ / міс", G),
            ("простій +\nвідбудова", R)]),
        ("Кеш", (GOLDF, GOLD), [
            ("~0.2 мс\n(влучання)", G), ("+0\n(TTL, без інвал.)", G),
            ("≤ TTL\n(5 хв)", A), ("гаряча жменя,\nвитісненна", A),
            ("промах +\nперерахунок", G)]),
    ]

    ry, rh = 120, 98
    for i, (name, (nf, ns), cells) in enumerate(rows):
        y = ry + i * (rh + 6)
        f.append(fitbox(labx, y, labw, rh, name, size=13, fill=nf, stroke=ns, bold=True))
        for x, (txt, (cf, cs)) in zip(cxs, cells):
            f.append(fitbox(x, y, cw, rh, txt, size=12, fill=cf, stroke=cs, bold=True))

    render(os.path.join(IMG, "three-way-prices.svg"), W, H, *f,
           title="Те саме число 318 — три виміряні ціни (один дім, один місяць)")


# ───────── Проєкт-фіг. 2: однополітність гасить навалу на промах ─────────
def fig_single_flight():
    W, H = 1120, 480
    f = []

    # роздільник між панелями
    f.append(line(560, 96, 560, 440, color=MUTED, sw=1.4, dash="6,6"))

    # ── ліва панель: без однополітності ──
    f.append(fitbox(46, 70, 456, 42,
                    "без однополітності — сто промахів разом",
                    size=13.5, fill=REDF, stroke=POS, bold=True))
    lreq = [110, 190, 270, 350, 430]
    for rx in lreq:
        f.append(circle(rx, 158, 16, fill=FILL, stroke=INK, sw=1.8))
        f.append(text(rx, 163, "R", size=13, bold=True))
    lsrc, _, _ = textbox(270, 402, "ДЖЕРЕЛО\nсирі reading", size=13, bold=True,
                         fill=GREENF, stroke=FIELD, sw=2)
    for i, rx in enumerate(lreq):
        f.append(arrow(rx, 176, 270 + (i - 2) * 20, 372, color=POS, sw=1.8))
    f.append(lsrc)
    f.append(text(270, 262, "5 однакових важких сканів", size=13, color=POS, bold=True))

    # ── права панель: single-flight ──
    f.append(fitbox(618, 70, 456, 42,
                    "single-flight — збіг склеєно в один",
                    size=13.5, fill=GREENF, stroke=FIELD, bold=True))
    rreq = [660, 730, 800, 870, 940]
    for rx in rreq:
        f.append(circle(rx, 158, 16, fill=FILL, stroke=INK, sw=1.8))
        f.append(text(rx, 163, "R", size=13, bold=True))
    lockb, _, _ = textbox(800, 262, "замок за ключем\nkwh:home:month",
                          size=12.5, bold=True, fill=GOLDF, stroke=GOLD, sw=2)
    for i, rx in enumerate(rreq):
        f.append(arrow(rx, 176, 800 + (i - 2) * 16, 238, color=MUTED, sw=1.6))
    f.append(lockb)
    rsrc, _, _ = textbox(800, 412, "ДЖЕРЕЛО\nсирі reading", size=13, bold=True,
                         fill=GREENF, stroke=FIELD, sw=2)
    f.append(arrow(800, 288, 800, 384, color=FIELD, sw=2.4))
    f.append(rsrc)
    f.append(mtext(892, 330, "1 рахує,\nрешта чекають\n= 1 скан",
                   size=12.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG, "single-flight.svg"), W, H, *f,
           title="Навала на промах проти однополітності: сто промахів — один скан")


# ───────── Проєкт-фіг. 3: ніч, коли похідну копію втрачено ─────────
def fig_copy_lost():
    W, H = 1080, 480
    f = []

    x0, x1 = 250, 980
    mid = 560

    f.append(line(mid, 78, mid, 448, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(mid, 64, "опівночі: похідну копію втрачено",
                  size=12.5, color=MUTED, bold=True))

    # доріжка 1 — наживо
    b, _, _ = textbox(150, 132, "Наживо", size=13, bold=True, fill=FILL, stroke=INK)
    f.append(b)
    f.append(line(x0, 132, x1, 132, color=FIELD, sw=3))
    f.append(text((x0 + x1) / 2, 168, "нема похідного — опівночі не гине нічого",
                  size=12, color=FIELD, bold=True))

    # доріжка 2 — кеш (просадка й гоїння)
    b, _, _ = textbox(150, 252, "Кеш", size=13, bold=True, fill=FILL, stroke=INK)
    f.append(b)
    f.append(line(x0, 252, mid, 252, color=FIELD, sw=3))
    f.append(line(mid, 252, mid + 55, 278, color=GOLD, sw=3))
    f.append(line(mid + 55, 278, mid + 120, 252, color=GOLD, sw=3))
    f.append(line(mid + 120, 252, x1, 252, color=FIELD, sw=3))
    f.append(text((mid + x1) / 2 + 20, 300,
                  "промах + перерахунок — за секунди знову тепло",
                  size=12, color=GOLD, bold=True))

    # доріжка 3 — матеріалізація (довгий провал до відбудови)
    b, _, _ = textbox(150, 372, "Матеріалізація", size=13, bold=True, fill=FILL, stroke=INK)
    f.append(b)
    reb = x1 - 140
    f.append(line(x0, 372, mid, 372, color=FIELD, sw=3))
    f.append(line(mid, 406, reb, 406, color=POS, sw=4, dash="7,5"))
    f.append(text((mid + reb) / 2, 394, "простій / хибне число", size=11.5,
                  color=POS, bold=True))
    f.append(line(reb, 406, reb + 40, 372, color=FIELD, sw=3))
    f.append(line(reb + 40, 372, x1, 372, color=FIELD, sw=3))
    f.append(text((x0 + x1) / 2, 446, "поки повний скан із сирого не відбудує копію",
                  size=12, color=POS, bold=True))

    render(os.path.join(IMG, "copy-lost-night.svg"), W, H, *f,
           title="Та сама ніч утрати копії — три різні наслідки")


if __name__ == "__main__":
    fig_when_work()
    fig_matrix()
    fig_layers()
    fig_three_costs()
    fig_cache_ladder()
    fig_prices()
    fig_single_flight()
    fig_copy_lost()
    print("OK: when-work-happens.svg, three-way-matrix.svg, layered-read-path.svg, "
          "math-three-costs.svg, math-cache-ladder.svg, "
          "three-way-prices.svg, single-flight.svg, copy-lost-night.svg")
