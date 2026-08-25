# -*- coding: utf-8 -*-
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GRN = "#27ae60"   # FIELD — переможець / поле
RED = "#c0392b"   # POS — програш / вибух перебору
BLU = "#2457d6"   # NEG
GREY = "#c2c8d0"

# спільна модель автомата на 4 стани (для ілюстрацій ґратки)
NEXT = {0: {0: 0, 1: 2}, 1: {0: 0, 1: 2}, 2: {0: 1, 1: 3}, 3: {0: 1, 1: 3}}
SNAME = ["00", "01", "10", "11"]


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── Фіг. 1: дерево перебору (2ᴸ) проти ґратки сталої ширини ────────────────────

def fig_explosion():
    W, H = 1140, 560
    p = []

    # роздільник посередині
    p.append(line(W / 2, 66, W / 2, H - 96, color="#e3e7ec", sw=1.6, dash="6 6"))

    # ── ЛІВА панель: двійкове дерево, що вибухає ──
    p.append(text(285, 66, "перебір: кожен вхідний біт подвоює число шляхів", size=13.5, color=RED, bold=True))
    depth = 4
    x0, x1 = 70, 470              # від кореня до листя
    ytop, ybot = 108, 470
    levels = []                  # levels[d] = список y-центрів вузлів рівня d
    for d in range(depth + 1):
        n = 2 ** d
        xs = x0 + (x1 - x0) * d / depth
        step = (ybot - ytop) / (n)
        ys = [ytop + step * (i + 0.5) for i in range(n)]
        levels.append((xs, ys))
    # ребра
    for d in range(depth):
        xs, ys = levels[d]
        xs2, ys2 = levels[d + 1]
        for i, y in enumerate(ys):
            for c in (0, 1):
                p.append(line(xs + 5, y, xs2 - 5, ys2[2 * i + c], color=GREY, sw=1.1))
    # вузли
    for d in range(depth + 1):
        xs, ys = levels[d]
        r = 6 if d <= 2 else (4 if d == 3 else 3)
        for y in ys:
            p.append(circle(xs, y, r, fill=BG, stroke=RED if d == depth else MUTED, sw=1.5))
    # підписи рівнів (число шляхів)
    for d, lab in [(0, "1"), (1, "2"), (2, "4"), (3, "8"), (4, "16")]:
        xs, _ = levels[d]
        p.append(text(xs, ybot + 26, lab, size=13, color=(RED if d == depth else MUTED), bold=(d == depth)))
    p.append(text((x0 + x1) / 2, ybot + 50, "число шляхів на кожному такті: 1, 2, 4, 8, 16, …", size=12, color=MUTED, italic=True))
    b, bw, bh = textbox(285, H - 52, "L бітів  →  2ᴸ шляхів  —  перебір вибухає", size=13.5,
                        bold=True, color=RED, fill="#fdecea", stroke=RED, sw=1.8, pad=11)
    p.append(b)

    # ── ПРАВА панель: ґратка сталої ширини ──
    p.append(text(855, 66, "ґратка: шляхи, що зійшлися в стані, зливаються", size=13.5, color=GRN, bold=True))
    ncol = 6
    gx = [640 + i * 78 for i in range(ncol)]
    gyr = [140, 224, 308, 392]
    # мітки станів
    for s in range(4):
        p.append(text(gx[0] - 30, gyr[s] + 5, SNAME[s], size=12, color=MUTED, bold=True, anchor="middle"))
    # усі переходи тонко
    for t in range(ncol - 1):
        for s in range(4):
            for u in (0, 1):
                ns = NEXT[s][u]
                p.append(line(gx[t] + 8, gyr[s], gx[t + 1] - 8, gyr[ns], color=GREY, sw=1.1,
                              dash="5 4" if u else None))
    # два шляхи, що зливаються в один стан (демонстрація злиття)
    pathA = [0, 2, 1, 0, 0, 0]
    pathB = [0, 0, 0, 0, 0, 0]
    for pth, col in [(pathB, BLU), (pathA, GRN)]:
        for t in range(ncol - 1):
            p.append(line(gx[t] + 8, gyr[pth[t]], gx[t + 1] - 8, gyr[pth[t + 1]], color=col, sw=3.0))
    # вузли
    for t in range(ncol):
        for s in range(4):
            p.append(circle(gx[t], gyr[s], 6.5, fill=BG, stroke="#aeb4bc", sw=1.5))
    # позначка місця злиття
    mx = gx[3]
    p.append(circle(mx, gyr[0], 9, fill="#eafaf0", stroke=GRN, sw=2.6))
    p.append(text(mx, gyr[0] - 20, "тут два шляхи злилися", size=11, color=GRN, bold=True))
    p.append(text(mx, gyr[0] - 6, "↓", size=12, color=GRN, bold=True))
    b, bw, bh = textbox(855, H - 52, "стала ширина  →  2^(K−1) станів на такт", size=13.5,
                        bold=True, color=GRN, fill="#eafaf0", stroke=GRN, sw=1.8, pad=11)
    p.append(b)

    render(os.path.join(OUT, "explosion.svg"), W, H, *p,
           title="Дерево перебору (2ᴸ) проти ґратки сталої ширини")


# ── Фіг. 2: add-compare-select у одному вузлі ─────────────────────────────────

def fig_acs():
    W, H = 860, 470
    p = []

    # попередники ліворуч, s′ праворуч
    ptop = (215, 140)
    pbot = (215, 320)
    snew = (615, 230)
    R = 30

    # ребра (спершу лінії, потім вузли зверху)
    # верхнє ребро — програшне
    p.append(line(ptop[0] + R, ptop[1] + 6, snew[0] - R, snew[1] - 8, color=GREY, sw=2.4, dash="6 5"))
    # нижнє ребро — переможне
    p.append(line(pbot[0] + R, pbot[1] - 6, snew[0] - R, snew[1] + 8, color=GRN, sw=3.4))

    # мітки метрик ребер
    p.append(text((ptop[0] + snew[0]) / 2 - 6, (ptop[1] + snew[1]) / 2 - 22, "ребро +2", size=13, color=MUTED, bold=True))
    p.append(text((pbot[0] + snew[0]) / 2 - 6, (pbot[1] + snew[1]) / 2 + 30, "ребро +0", size=13, color=GRN, bold=True))

    # вузли-попередники
    for (cx, cy), m, col, fill in [(ptop, "3", MUTED, "#f4f6f8"), (pbot, "1", GRN, "#eafaf0")]:
        p.append(circle(cx, cy, R, fill=fill, stroke=col, sw=2.4))
        p.append(text(cx, cy + 6, "M=" + m, size=15, color=col, bold=True))
    p.append(text(ptop[0], ptop[1] - R - 12, "попередник", size=11.5, color=MUTED, italic=True))
    p.append(text(pbot[0], pbot[1] + R + 22, "попередник", size=11.5, color=MUTED, italic=True))

    # вузол s′
    p.append(circle(snew[0], snew[1], R + 4, fill="#eafaf0", stroke=GRN, sw=2.8))
    p.append(text(snew[0], snew[1] + 6, "s′", size=18, color=GRN, bold=True))
    p.append(text(snew[0], snew[1] - R - 14, "новий стан", size=11.5, color=MUTED, italic=True))

    # обчислення претендентів — стовпчиком праворуч
    cx = 740
    p.append(text(cx, 150, "add:", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(cx, 172, "3 + 2 = 5", size=13.5, color=MUTED, anchor="start"))
    p.append(text(cx, 196, "1 + 0 = 1", size=13.5, color=GRN, bold=True, anchor="start"))
    p.append(text(cx, 232, "compare:", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(cx, 254, "5  проти  1", size=13.5, color=INK, anchor="start"))
    p.append(text(cx, 290, "select:", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(cx, 312, "лишаємо 1", size=13.5, color=GRN, bold=True, anchor="start"))

    # підсумкова плашка
    b, bw, bh = textbox(W / 2, H - 42,
                        "M(s′) = 1  ·  вказівник назад → нижній попередник  ·  верхній шлях (5) гине назавжди",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "acs.svg"), W, H, *p,
           title="Додати — порівняти — вибрати: одна клітина роботи декодера")


# ── Фіг. 3: один алгоритм, багато втілень ─────────────────────────────────────

def fig_general():
    W, H = 1060, 660
    p = []

    # ── центральна абстрактна ґратка ──
    cxs = [452, 528, 604]        # 3 стовпці
    cyr = [286, 340, 394]        # 3 стани
    # ребра
    for t in range(len(cxs) - 1):
        for s in range(3):
            for ns in range(3):
                if abs(s - ns) <= 1:
                    p.append(line(cxs[t] + 7, cyr[s], cxs[t + 1] - 7, cyr[ns], color=GREY, sw=1.2))
    for t in range(len(cxs)):
        for s in range(3):
            p.append(circle(cxs[t], cyr[s], 7, fill=BG, stroke=INK, sw=1.7))
    # рамка навколо центру
    p.append(rect(410, 250, 236, 180, fill="none", stroke=INK, sw=1.6, rx=12))
    p.append(text(528, 244, "абстрактна ґратка станів", size=12.5, color=INK, bold=True))
    b, bw, bh = textbox(528, 462, "додати · порівняти · вибрати", size=13.5, bold=True,
                        fill="#f6f4ec", stroke=INK, sw=1.8, pad=11)
    p.append(b)
    p.append(text(528, 498, "той самий прохід у всіх чотирьох", size=11.5, color=MUTED, italic=True))

    # ── чотири картки-втілення по кутах ──
    cards = [
        (232, 120, GRN, "Згортковий код", "стани = біти регістра;\nспостереження = биті пари"),
        (826, 120, BLU, "Розпізнавання мовлення", "стани = фонеми;\nспостереження = звук"),
        (232, 548, "#8e44ad", "Пошук генів у ДНК", "стани = ген / міжгення;\nспостереження = нуклеотиди"),
        (826, 548, "#d35400", "Вирівнювання каналу", "стани = символи в пам'яті;\nспостереження = вибірки"),
    ]
    cw, chh = 300, 92
    for (cx, cy, col, ttl, body) in cards:
        p.append(rect(cx - cw / 2, cy - chh / 2, cw, chh, fill=BG, stroke=col, sw=2.2, rx=10))
        p.append(text(cx, cy - chh / 2 + 24, ttl, size=14, color=col, bold=True))
        p.append(mtext(cx, cy - chh / 2 + 46, body, size=12, color=INK, lh=1.25))

    # з'єднувачі: від кутів центральної рамки до ЗОВНІШНІХ кутів карток —
    # так лінії розходяться назовні й не перетинають ані текст карток, ані
    # центральну плашку (кінці — на кутах-рамках, де тексту немає).
    frame_corners = [(410, 250), (646, 250), (410, 430), (646, 430)]
    for (ax, ay), (cx, cy, col, _, _) in zip(frame_corners, cards):
        tx = cx - cw / 2 if cx < 528 else cx + cw / 2     # зовнішній бік картки
        ty = cy + chh / 2 if cy < 340 else cy - chh / 2   # край, повернутий до центру
        p.append(line(ax, ay, tx, ty, color=col, sw=1.7, dash="4 4"))

    render(os.path.join(OUT, "general.svg"), W, H, *p,
           title="Один алгоритм — багато втілень: ґратка не знає, що означають її стани")


def polygon(pts, fill, stroke="none", sw=0.0, opacity=1.0):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s opacity="%.2f"/>' % (s, fill, st, opacity)


# ── Фіг. 4: м'яка метрика (парабола) проти жорсткої (щабель) ──────────────────
# Показує, що жорстке рішення — це двоуровнева квантизація гладкої параболи:
# уся аналогова величина r викидається, лишається сам знак.

def fig_metric_soft_hard():
    W, H = 900, 560
    p = []

    R0, R1 = -1.5, 3.5                      # діапазон прийнятої вибірки r
    PX0, PX1 = 118, 812
    def xr(r): return PX0 + (r - R0) / (R1 - R0) * (PX1 - PX0)

    # верхня панель — м'яка метрика (r−1)²
    TS_top, TS_bot = 78, 250                # верх/низ області кривої
    Mmax = 6.5
    def ys(m): return TS_bot - min(m, Mmax) / Mmax * (TS_bot - TS_top)
    # нижня панель — жорстка метрика {0,1}
    HB0, HB1 = 470, 372                     # рівень 0 і рівень 1
    def yh(m): return HB0 - m * (HB0 - HB1)

    # вертикальні орієнтири крізь обидві панелі: поріг r=0 і сигнал r=+1
    for r, lab, col in [(0.0, "поріг", MUTED), (1.0, "сигнал c=+1", FIELD)]:
        p.append(line(xr(r), TS_top - 8, xr(r), HB0 + 8, color=col, sw=1.3, dash="4 5"))
    # осі-бази панелей
    p.append(line(PX0 - 8, TS_bot, PX1 + 8, TS_bot, color=INK, sw=1.4))
    p.append(line(PX0 - 8, HB0, PX1 + 8, HB0, color=INK, sw=1.4))

    # ── ВЕРХ: гладка парабола ──
    p.append(text(PX0 - 6, TS_top - 14, "м'яка метрика", size=14, color=NEG, bold=True, anchor="start"))
    p.append(text(PX0 - 6 + 150, TS_top - 14, "λ = (r − c)²  — уся аналогова відстань", size=12.5, color=MUTED, anchor="start"))
    pts = []
    r = R0
    while r <= R1 + 1e-9:
        pts.append((xr(r), ys((r - 1.0) ** 2)))
        r += 0.05
    p.append(polyline(pts, color=NEG, sw=3.0))
    # дві проби на «правильному» боці: близька й далека — різні λ
    for r in (0.2, 2.8):
        m = (r - 1.0) ** 2
        p.append(circle(xr(r), ys(m), 5.5, fill=BG, stroke=NEG, sw=2.2))
        p.append(line(xr(r), ys(m), xr(r), yh(0), color=GREY, sw=1.2, dash="3 4"))
        p.append(text(xr(r), ys(m) - 12, "λ=%.2f" % m, size=11.5, color=NEG, bold=True))

    # ── НИЗ: щабель на два рівні ──
    p.append(text(PX0 - 6, HB1 - 18, "жорстка метрика", size=14, color=POS, bold=True, anchor="start"))
    p.append(text(PX0 - 6 + 168, HB1 - 18, "лише знак r  →  два рівні {0, 1}", size=12.5, color=MUTED, anchor="start"))
    # r<0 → розбіг (1), r>0 → збіг (0)
    p.append(line(xr(R0), yh(1), xr(0), yh(1), color=POS, sw=3.4))
    p.append(line(xr(0), yh(1), xr(0), yh(0), color=POS, sw=3.4, dash="5 4"))
    p.append(line(xr(0), yh(0), xr(R1), yh(0), color=POS, sw=3.4))
    p.append(text(xr(-0.75), yh(1) - 12, "розбіг → 1", size=12, color=POS, bold=True))
    p.append(text(xr(2.4), yh(0) + 20, "збіг → 0", size=12, color=POS, bold=True))
    # обидві проби падають на той самий рівень 0
    for r in (0.2, 2.8):
        p.append(circle(xr(r), yh(0), 5.5, fill=BG, stroke=POS, sw=2.2))

    # підписи осі r
    for r, lab in [(-1.0, "−1"), (0.0, "0"), (1.0, "+1"), (2.0, "+2"), (3.0, "+3")]:
        p.append(text(xr(r), HB0 + 26, lab, size=12, color=MUTED))
    p.append(text((PX0 + PX1) / 2, HB0 + 46, "прийнята вибірка r", size=12.5, color=INK, italic=True))

    b, bw, bh = textbox((PX0 + PX1) / 2, H - 28,
                        "дві проби на «своєму» боці (λ=0.64 і λ=3.24) жорстке рішення зрівнює в один рівень 0 — величина r загублена",
                        size=12, color=INK, fill="#f6f4ec", stroke=INK, sw=1.6, pad=10)
    p.append(b)

    render(os.path.join(OUT, "metric-soft-hard.svg"), W, H, *p,
           title="М'яка метрика — гладка парабола; жорстка — її двоуровнева квантизація")


# ── Фіг. 5: перекриття правдоподібностей D — джерело ~2 дБ ────────────────────
# Ліворуч — два гаусіани (м'яке), їхнє перекриття мале; праворуч — стовпці BSC
# (жорстке), перекриття більше. Менше перекриття → нижча ймовірність помилки.

def fig_overlap():
    W, H = 980, 500
    p = []

    m, sig = 0.906, 0.707                   # центри ±√E та σ для p=0.1
    # ── ЛІВА панель: гаусіани ──
    LX0, LX1 = 96, 452
    BASE, PEAK = 372, 118
    XR0, XR1 = -3.0, 3.0
    def lx(r): return LX0 + (r - XR0) / (XR1 - XR0) * (LX1 - LX0)
    def ly(v): return BASE - v * (BASE - PEAK)     # v — висота 0..1
    def g(r, mu): return math.exp(-(r - mu) ** 2 / (2 * sig * sig))

    p.append(text((LX0 + LX1) / 2, 60, "м'яке рішення", size=14, color=INK, bold=True))
    p.append(text((LX0 + LX1) / 2, 78, "перекриття двох гаусіанів", size=12, color=MUTED, italic=True))
    p.append(line(LX0 - 8, BASE, LX1 + 10, BASE, color=INK, sw=1.4))

    # заштрихована зона перекриття = min(g₊, g₋)
    ov = []
    r = XR0
    while r <= XR1 + 1e-9:
        ov.append((lx(r), ly(min(g(r, m), g(r, -m)))))
        r += 0.05
    ov = [(lx(XR0), BASE)] + ov + [(lx(XR1), BASE)]
    p.append(polygon(ov, fill=GREY, opacity=0.55))

    for mu, col, lab in [(-m, NEG, "c = −√E"), (m, POS, "c = +√E")]:
        pts = []
        r = XR0
        while r <= XR1 + 1e-9:
            pts.append((lx(r), ly(g(r, mu))))
            r += 0.05
        p.append(polyline(pts, color=col, sw=2.8))
        p.append(text(lx(mu), ly(1.0) - 10, lab, size=11.5, color=col, bold=True))
    p.append(text(lx(0), BASE + 22, "0", size=11.5, color=MUTED))
    p.append(text(lx(0), BASE + 62, "зона плутанини — де\nгіпотези перекриваються", size=11, color=MUTED, italic=True))
    b, bw, bh = textbox((LX0 + LX1) / 2, BASE + 108, "D_м = e^(−E/N₀) = 0.44      −ln D_м = 0.82",
                        size=12.5, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, pad=9)
    p.append(b)

    # ── ПРАВА панель: стовпці BSC ──
    RX0, RX1 = 560, 916
    p.append(text((RX0 + RX1) / 2, 60, "жорстке рішення", size=14, color=INK, bold=True))
    p.append(text((RX0 + RX1) / 2, 78, "перекриття на {0, 1},  p = 0.1", size=12, color=MUTED, italic=True))
    p.append(line(RX0 - 8, BASE, RX1 + 10, BASE, color=INK, sw=1.4))

    # дві групи (вхід 0 і вхід 1), у кожній стовпці ймовірностей отримати 0 та 1
    def bar(cx, h, col, lab):
        w = 46
        p.append(rect(cx - w / 2, BASE - h, w, h, fill=col, stroke=INK, sw=1.2, rx=3))
        p.append(text(cx, BASE - h - 8, lab, size=11, color=INK))
    HH = (BASE - PEAK)                      # висота під імовірність 1.0
    gx0, gx1 = RX0 + 90, RX1 - 90
    # вхід 0: P(0)=0.9 (синій, «свій»), P(1)=0.1 (сірий, «протічка»)
    bar(gx0 - 28, 0.9 * HH, NEG, "0.9")
    bar(gx0 + 28, 0.1 * HH, GREY, "0.1")
    p.append(text(gx0, BASE + 22, "передано 0", size=11.5, color=NEG, bold=True))
    # вхід 1: P(0)=0.1, P(1)=0.9
    bar(gx1 - 28, 0.1 * HH, GREY, "0.1")
    bar(gx1 + 28, 0.9 * HH, POS, "0.9")
    p.append(text(gx1, BASE + 22, "передано 1", size=11.5, color=POS, bold=True))
    p.append(text((RX0 + RX1) / 2, BASE + 62, "перекриття «протічок» більше,\nніж хвости гаусіанів", size=11, color=MUTED, italic=True))
    b, bw, bh = textbox((RX0 + RX1) / 2, BASE + 108, "D_ж = 2√(p(1−p)) = 0.60      −ln D_ж = 0.51",
                        size=12.5, color=POS, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=9)
    p.append(b)

    render(os.path.join(OUT, "overlap.svg"), W, H, *p,
           title="Перекриття правдоподібностей: менше перекриття → 10·log(0.82/0.51) ≈ 2.06 дБ на користь м'якого")


# ── Фіг. 6: пожадливо проти Вітербі на прогоні казино ─────────────────────────
# Двадцять кидків; під ними дві розмітки. Пожадлива ставить «шахрай» на кожній
# шістці (зокрема одинокій п'ятій); Вітербі лишає одиноку чесною, а вмикає
# шахрайство лише на суцільній серії. Осердя всієї вставки — в одній картинці.

def fig_casino_strip():
    W, H = 1180, 430
    p = []
    obs = [2, 4, 1, 3, 6, 5, 2, 1, 6, 6, 6, 6, 6, 6, 3, 1, 4, 2, 5, 3]
    greedy = ["L" if f == 6 else "F" for f in obs]
    vit = ["F"] * 8 + ["L"] * 6 + ["F"] * 6
    w = 49
    x0 = 150

    def cx(i): return x0 + i * w + w / 2
    def cellx(i): return x0 + i * w
    y_roll, y_greedy, y_vit = 96, 190, 264
    ch = 36
    F_fill, F_line = "#eafaf0", FIELD
    L_fill, L_line = "#fdecea", POS

    # підсвічена колонка одинокої шістки (індекс 4) — позаду решти
    p.append(rect(cellx(4) - 3, y_roll - 26, w + 6, (y_vit + 26) - (y_roll - 26),
                  fill="#fff6da", stroke="#e0b000", sw=1.6, rx=8))

    # рядок кидків
    for i, f in enumerate(obs):
        tint = "#fdf0ec" if f == 6 else BG
        p.append(rect(cx(i) - 19, y_roll - ch / 2, 38, ch, fill=tint, stroke="#b8bec6", sw=1.4, rx=6))
        p.append(text(cx(i), y_roll + 6, str(f), size=17, color=INK, bold=(f == 6)))
    # рядки станів (пожадливо, Вітербі)
    for row_y, seq in [(y_greedy, greedy), (y_vit, vit)]:
        for i, s in enumerate(seq):
            fill, ln = (L_fill, L_line) if s == "L" else (F_fill, F_line)
            p.append(rect(cx(i) - 19, row_y - ch / 2, 38, ch, fill=fill, stroke=ln, sw=1.8, rx=6))
            p.append(text(cx(i), row_y + 6, s, size=16, color=ln, bold=True))

    # мітки рядків ліворуч
    for ry, lab in [(y_roll, "кидки"), (y_greedy, "пожадливо"), (y_vit, "Вітербі")]:
        p.append(text(x0 - 16, ry + 5, lab, size=13.5, color=INK, bold=True, anchor="end"))

    # виноска до одинокої шістки (згори, над підсвіченою смугою)
    b, bw, bh = textbox(cx(4), 50, "одинока шістка", size=12.5, bold=True,
                        color="#9a6600", fill="#fff6da", stroke="#e0b000", sw=1.6, pad=8)
    p.append(b)
    p.append(line(cx(4), 50 + bh / 2, cx(4), y_roll - 26, color="#e0b000", sw=1.5, dash="4 4"))

    # дужка під серією шісток (індекси 8..13)
    bx0, bx1 = cellx(8) + 3, cellx(13) + w - 3
    by = y_vit + ch / 2 + 16
    p.append(line(bx0, by, bx1, by, color=POS, sw=2.2))
    p.append(line(bx0, by, bx0, by - 8, color=POS, sw=2.2))
    p.append(line(bx1, by, bx1, by - 8, color=POS, sw=2.2))
    p.append(text((bx0 + bx1) / 2, by + 20, "серія шісток — підміну впіймано", size=12.5, color=POS, bold=True))

    # легенда праворуч угорі
    lx, ly = W - 252, 50
    p.append(rect(lx, ly - 12, 18, 18, fill=F_fill, stroke=F_line, sw=1.8, rx=4))
    p.append(text(lx + 26, ly + 3, "чесний кубик", size=12.5, color=INK, anchor="start"))
    p.append(rect(lx, ly + 14, 18, 18, fill=L_fill, stroke=L_line, sw=1.8, rx=4))
    p.append(text(lx + 26, ly + 29, "шахрайський кубик", size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "casino-strip.svg"), W, H, *p,
           title="Пожадливо проти Вітербі: та сама шістка — дві відповіді")


# ── Фіг. 7: бухгалтерія одинокої шістки ───────────────────────────────────────
# Дві «квитанції»: лишити кубик чесним проти гака в шахрайство й назад. Гак
# коштує 3.70 за два переходи, а купує лише 1.28 на грані — не окуповується.

def fig_ledger():
    W, H = 940, 430
    p = []
    cw, chh, cy0 = 366, 232, 60
    lx = 56
    rx = W - 56 - cw

    def card(x, title, tcol, rows, total):
        q = [rect(x, cy0, cw, chh, fill=BG, stroke=tcol, sw=2.2, rx=12),
             text(x + cw / 2, cy0 + 30, title, size=14.5, color=tcol, bold=True)]
        yy = cy0 + 72
        for lab, val in rows:
            q.append(text(x + 24, yy, lab, size=13.5, color=INK, anchor="start"))
            q.append(text(x + cw - 24, yy, val, size=13.5, color=MUTED, anchor="end"))
            yy += 30
        q.append(line(x + 24, yy - 10, x + cw - 24, yy - 10, color="#d0d5db", sw=1.4))
        q.append(text(x + 24, yy + 14, "разом", size=14, color=INK, anchor="start", bold=True))
        q.append(text(x + cw - 24, yy + 14, total, size=15.5, color=tcol, anchor="end", bold=True))
        return q

    p += card(lx, "лишити чесним  (F→F→F)", FIELD,
              [("log 0.90   лишитись", "−0.105"),
               ("log 0.90   лишитись", "−0.105"),
               ("log B[F][6]   грань 6", "−1.792")], "−2.002")
    p += card(rx, "звинуватити  (F→L→F)", POS,
              [("log 0.10   підмінити", "−2.303"),
               ("log 0.20   повернути", "−1.609"),
               ("log B[L][6]   грань 6", "−0.511")], "−4.423")

    b, bw, bh = textbox(W / 2, cy0 + chh + 60, "чесний виграє на 2.42", size=15.5, bold=True,
                        color=INK, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=12)
    p.append(b)
    p.append(text(W / 2, cy0 + chh + 60 + bh / 2 + 24,
                  "перехідний штраф за гак  −3.70      виграш на грані  +1.28",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "ledger.svg"), W, H, *p,
           title="Ціна одинокої шістки: гак у шахрайство не окуповується")


if __name__ == "__main__":
    fig_explosion()
    fig_acs()
    fig_general()
    fig_metric_soft_hard()
    fig_overlap()
    fig_casino_strip()
    fig_ledger()
    print("OK: figures written to", OUT)
