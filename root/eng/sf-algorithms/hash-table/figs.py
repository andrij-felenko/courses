# -*- coding: utf-8 -*-
"""Фігури до статті «Хеш-таблиця». Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Розкладка — із запасом, підписи рознесено."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 72, 40          # ширина/висота комірки масиву
FILLED = "#eaf0fd"       # зайнята комірка
EMPTY  = BG              # порожня комірка
CLUST  = "#fdecea"       # комірка скупчення


def cell(x, y, label, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.6, tcolor=INK, tsize=15, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=5)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out


# ── Фігура 1: ланцюжки vs відкрита адресація ────────────────────────────────
def fig_collision():
    W, H = 940, 470
    parts = []
    # заголовки панелей
    parts.append(text(240, 62, "Ланцюжки (роздільне зчеплення)", size=17, bold=True))
    parts.append(text(700, 62, "Відкрита адресація", size=17, bold=True))
    parts.append(line(510, 90, 510, 430, color=MUTED, sw=1, dash="5,5"))

    # спільна підпис-нагадування вгорі
    parts.append(text(240, 88, "h(\"cat\") = 2,  h(\"act\") = 2  — колізія", size=13, color=MUTED))
    parts.append(text(700, 88, "h(\"cat\") = 2,  h(\"act\") = 2  — колізія", size=13, color=MUTED))

    # ── ліва панель: вертикальний масив, ланцюжок від комірки 2 ──
    ax, ay = 120, 110
    for i in range(6):
        y = ay + i * (CH + 8)
        fill = FILLED if i == 2 else EMPTY
        parts.append(text(ax - 16, y + CH / 2 + 5, str(i), size=13, color=MUTED, anchor="end"))
        if i == 2:
            parts.append(cell(ax, y, "•", fill=fill, tsize=22, bold=True))
        else:
            parts.append(cell(ax, y, "", fill=fill))
    # ланцюжок: комірка 2 → cat → act
    y2 = ay + 2 * (CH + 8) + CH / 2
    n1x, n2x = ax + CW + 60, ax + CW + 190
    parts.append(arrow(ax + CW + 4, y2, n1x - 4, y2, color=NEG, sw=1.8))
    parts.append(cell(n1x, y2 - CH / 2, "cat", w=90, fill=FILLED, tcolor=NEG, bold=True))
    parts.append(arrow(n1x + 90 + 4, y2, n2x - 4, y2, color=NEG, sw=1.8))
    parts.append(cell(n2x, y2 - CH / 2, "act", w=90, fill=FILLED, tcolor=NEG, bold=True))
    parts.append(text(240, 430, "колізія → додаємо вузол у список комірки", size=12.5, color=MUTED))

    # ── права панель: усе в масиві, act пробує в 3 ──
    bx, by = 690, 110
    contents = {2: "cat", 3: "act"}
    for i in range(6):
        y = by + i * (CH + 8)
        lab = contents.get(i, "")
        fill = FILLED if i in contents else EMPTY
        tcolor = NEG if i in contents else INK
        parts.append(text(bx - 16, y + CH / 2 + 5, str(i), size=13, color=MUTED, anchor="end"))
        parts.append(cell(bx, y, lab, w=90, fill=fill, tcolor=tcolor, bold=(i in contents)))
    # проба-стрілка від комірки 2 до 3 (збоку)
    y_from = by + 2 * (CH + 8) + CH / 2
    y_to = by + 3 * (CH + 8) + CH / 2
    px = bx + 90 + 26
    parts.append(line(bx + 90 + 4, y_from, px, y_from, color=POS, sw=1.8))
    parts.append(line(px, y_from, px, y_to, color=POS, sw=1.8))
    parts.append(arrow(px, y_to, bx + 90 + 4, y_to, color=POS, sw=1.8))
    parts.append(text(px + 44, (y_from + y_to) / 2 + 4, "проба", size=12, color=POS, anchor="start"))
    parts.append(text(700, 430, "колізія → шукаємо вільну комірку далі", size=12.5, color=MUTED))

    render(os.path.join(IMG, "collision-strategies.svg"), W, H, *parts)


# ── Фігура 2: первинне скупчення при лінійному пробуванні ────────────────────
def fig_clustering():
    W, H = 760, 380
    parts = []
    parts.append(text(W / 2, 40, "Лінійне пробування: скупчення росте саме на себе", size=16, bold=True))
    ax, ay = 70, 96
    contents = {2: "P", 3: "Q", 4: "R", 5: "S"}
    for i in range(8):
        x = ax + i * (CW + 6)
        parts.append(text(x + CW / 2, ay - 12, str(i), size=13, color=MUTED))
        lab = contents.get(i, "")
        if i in contents:
            parts.append(cell(x, ay, lab, fill=CLUST, tcolor=POS, bold=True))
        elif i == 6:
            parts.append(cell(x, ay, "", fill=FIELD_TINT()))
        else:
            parts.append(cell(x, ay, "", fill=EMPTY))
    # дужка над скупченням 2..5
    x2 = ax + 2 * (CW + 6)
    x5 = ax + 5 * (CW + 6) + CW
    parts.append(line(x2, ay - 34, x5, ay - 34, color=POS, sw=2))
    parts.append(line(x2, ay - 34, x2, ay - 28, color=POS, sw=2))
    parts.append(line(x5, ay - 34, x5, ay - 28, color=POS, sw=2))
    parts.append(text((x2 + x5) / 2, ay - 42, "скупчення", size=12.5, color=POS))
    # позначка вільної комірки 6
    x6 = ax + 6 * (CW + 6)
    parts.append(text(x6 + CW / 2, ay + CH + 22, "вільна", size=12, color=FIELD))

    # хто куди сів
    rows = ["P:  дім 2  →  сів у 2",
            "Q:  дім 2  →  2 зайнято  →  сів у 3",
            "R:  дім 3  →  3 зайнято  →  сів у 4",
            "S:  дім 2  →  2,3,4 зайнято  →  сів у 5"]
    for k, r in enumerate(rows):
        parts.append(text(ax, ay + CH + 60 + k * 26, r, size=13.5, color=INK, anchor="start"))
    parts.append(text(ax, ay + CH + 60 + 4 * 26 + 10,
                      "Новий ключ із домом будь-де в 2…5 мусить пройти все скупчення до вільної 6 — і подовжити його.",
                      size=13, color=POS, anchor="start"))

    render(os.path.join(IMG, "primary-clustering.svg"), W, H, *parts)


def FIELD_TINT():
    return "#eafaf0"


# ── Фігура 3: надгробок при видаленні ───────────────────────────────────────
def fig_tombstone():
    W, H = 780, 440
    parts = []
    parts.append(text(W / 2, 38, "Видалення у відкритій адресації  (B осів у 4, пройшовши повз зайняту 3)", size=15, bold=True))
    ax = 156                                  # 6 комірок по центру
    # ── верхній ряд: просто спорожнити → B недосяжний ──
    ay1 = 118
    parts.append(text(W / 2, ay1 - 40, "Спорожнити комірку 3 — і пошук B впирається в порожнечу та здається", size=13, color=POS, bold=True))
    top = {2: ("A", FILLED, INK), 3: ("", EMPTY, INK), 4: ("B", FILLED, NEG)}
    for i in range(6):
        x = ax + i * (CW + 6)
        parts.append(text(x + CW / 2, ay1 - 12, str(i), size=12, color=MUTED))
        lab, fill, tc = top.get(i, ("", EMPTY, INK))
        parts.append(cell(x, ay1, lab, fill=fill, tcolor=tc, bold=(lab != "")))
    x3 = ax + 3 * (CW + 6)
    x4 = ax + 4 * (CW + 6)
    parts.append(text(x3 + CW / 2, ay1 + CH + 20, "старт пошуку B", size=11.5, color=POS))
    parts.append(text(x3 + CW / 2, ay1 + CH + 37, "порожньо → стоп", size=11.5, color=POS))
    parts.append(text(x4 + CW / 2, ay1 + CH + 20, "B недосяжний", size=11.5, color=NEG))

    # ── нижній ряд: надгробок → B знаходиться ──
    ay2 = 316
    parts.append(text(W / 2, ay2 - 40, "Надгробок ✝ у комірці 3 — пошук переступає його й знаходить B", size=13, color=FIELD, bold=True))
    bot = {2: ("A", FILLED, INK), 3: ("✝", "#efeaf2", MUTED), 4: ("B", FILLED, NEG)}
    for i in range(6):
        x = ax + i * (CW + 6)
        parts.append(text(x + CW / 2, ay2 - 12, str(i), size=12, color=MUTED))
        lab, fill, tc = bot.get(i, ("", EMPTY, INK))
        parts.append(cell(x, ay2, lab, fill=fill, tcolor=tc, bold=(lab not in ("", "✝"))))
    x3b = ax + 3 * (CW + 6)
    x4b = ax + 4 * (CW + 6)
    parts.append(arrow(x3b + CW / 2, ay2 + CH + 8, x4b + CW / 2, ay2 + CH + 8, color=FIELD, sw=1.8))
    parts.append(text(x3b + CW / 2, ay2 + CH + 34, "переступ", size=11.5, color=FIELD))
    parts.append(text(x4b + CW / 2, ay2 + CH + 34, "B знайдено", size=11.5, color=FIELD))

    render(os.path.join(IMG, "tombstone.svg"), W, H, *parts)


# ── Фігура 4: середнє число проб vs коефіцієнт заповнення ────────────────────
def fig_loadfactor():
    W, H = 740, 470
    parts = []
    parts.append(text(W / 2, 40, "Середня робота на операцію залежно від заповнення", size=16, bold=True))
    # площина
    L, R = 96, 668
    T, B = 78, 386
    vmax = 10.0
    # осі
    parts.append(line(L, T, L, B, color=INK, sw=1.8))
    parts.append(line(L, B, R, B, color=INK, sw=1.8))
    # підписи осей
    parts.append(text((L + R) / 2, B + 46, "коефіцієнт заповнення  α", size=13.5))
    parts.append(text(L - 66, (T + B) / 2, "проби", size=13.5))
    parts.append(text(L - 66, (T + B) / 2 + 18, "(сер.)", size=12, color=MUTED))

    def X(a):
        return L + a * (R - L)

    def Y(v):
        v = min(v, vmax)
        return B - (v - 1) / (vmax - 1) * (B - T)

    # сітка/риски по осі α
    for a in [0.0, 0.25, 0.5, 0.75, 1.0]:
        parts.append(line(X(a), B, X(a), B + 6, color=INK, sw=1.4))
        parts.append(text(X(a), B + 24, ("%.2f" % a).rstrip("0").rstrip(".") if a not in (0.0,) else "0", size=12, color=MUTED))
    # риски по осі проб
    for v in [1, 2, 4, 6, 8, 10]:
        parts.append(line(L - 6, Y(v), L, Y(v), color=INK, sw=1.4))
        parts.append(text(L - 16, Y(v) + 4, str(v), size=12, color=MUTED, anchor="end"))

    # поріг α=0.75
    parts.append(line(X(0.75), T, X(0.75), B, color=MUTED, sw=1.3, dash="6,5"))
    parts.append(text(X(0.75), T - 8, "поріг ≈ 0.75", size=12, color=MUTED))

    # крива ланцюжків: 1 + α/2
    pts_chain = []
    a = 0.0
    while a <= 1.0001:
        pts_chain.append((X(a), Y(1 + a / 2)))
        a += 0.02
    parts.append(polyline(pts_chain, FIELD, 2.6))

    # крива відкритої адресації (успішний пошук): 0.5*(1 + 1/(1-α))
    pts_open = []
    a = 0.0
    while a <= 0.951:
        v = 0.5 * (1 + 1 / (1 - a))
        if v > vmax:
            break
        pts_open.append((X(a), Y(v)))
        a += 0.01
    parts.append(polyline(pts_open, POS, 2.6))

    # легенда
    lx, ly = R - 250, T + 6
    parts.append(line(lx, ly, lx + 30, ly, color=FIELD, sw=2.6))
    parts.append(text(lx + 38, ly + 4, "ланцюжки:  ≈ 1 + α/2", size=12.5, color=INK, anchor="start"))
    parts.append(line(lx, ly + 24, lx + 30, ly + 24, color=POS, sw=2.6))
    parts.append(text(lx + 38, ly + 28, "відкрита адр.:  ≈ ½(1 + 1/(1−α))", size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "load-factor.svg"), W, H, *parts)


def polyline(pts, color, sw):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (d, color, sw)


def poly(pts, color, sw, dash=None):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"%s/>' % (d, color, sw, da))


# ── Фігура 7 (вставка math «Ціна проби»): чотири криві проб vs α ─────────────
def fig_probes():
    import math
    W, H = 780, 500
    parts = []
    parts.append(text(W / 2, 38, "Середнє число проб: ідеальне хешування проти лінійного пробування",
                      size=15.5, bold=True))
    L, R = 100, 700
    T, B = 92, 410
    amax = 0.95
    vmax = 12.0

    def X(a):
        return L + (a / amax) * (R - L)

    def Y(v):
        v = min(v, vmax)
        return B - (v - 1) / (vmax - 1) * (B - T)

    parts.append(line(L, T, L, B, color=INK, sw=1.8))
    parts.append(line(L, B, R, B, color=INK, sw=1.8))
    parts.append(text((L + R) / 2, B + 44, "коефіцієнт заповнення  α", size=13.5))
    parts.append(text(L - 70, (T + B) / 2 - 6, "проби", size=13, color=INK))
    parts.append(text(L - 70, (T + B) / 2 + 12, "(сер.)", size=12, color=MUTED))
    for a in [0.0, 0.25, 0.5, 0.75, 0.9]:
        parts.append(line(X(a), B, X(a), B + 6, color=INK, sw=1.4))
        lab = "0" if a == 0.0 else ("%.2f" % a).rstrip("0").rstrip(".")
        parts.append(text(X(a), B + 24, lab, size=12, color=MUTED))
    for v in [1, 2, 4, 6, 8, 10, 12]:
        parts.append(line(L - 6, Y(v), L, Y(v), color=INK, sw=1.4))
        parts.append(text(L - 14, Y(v) + 4, str(v), size=12, color=MUTED, anchor="end"))
    parts.append(line(X(0.75), T, X(0.75), B, color=MUTED, sw=1.1, dash="6,5"))

    def curve(fn):
        pts = [(X(0.0), Y(1.0))]
        a = 0.005
        while a <= amax + 1e-9:
            v = fn(a)
            if v > vmax:
                pts.append((X(a), Y(vmax)))
                break
            pts.append((X(a), Y(v)))
            a += 0.005
        return pts

    uni_unsucc = curve(lambda a: 1.0 / (1.0 - a))
    uni_succ = curve(lambda a: (1.0 / a) * math.log(1.0 / (1.0 - a)))
    lin_unsucc = curve(lambda a: 0.5 * (1.0 + 1.0 / (1.0 - a) ** 2))
    lin_succ = curve(lambda a: 0.5 * (1.0 + 1.0 / (1.0 - a)))

    parts.append(poly(uni_unsucc, NEG, 2.6))
    parts.append(poly(uni_succ, NEG, 2.4, dash="7,5"))
    parts.append(poly(lin_unsucc, POS, 2.6))
    parts.append(poly(lin_succ, POS, 2.4, dash="7,5"))

    lx, ly = L + 20, T + 6
    rows = [(NEG, None, "ідеал, невдалий:  1/(1−α)"),
            (NEG, "7,5", "ідеал, успішний:  (1/α)·ln(1/(1−α))"),
            (POS, None, "лінійне, невдалий:  ½(1+1/(1−α)²)"),
            (POS, "7,5", "лінійне, успішний:  ½(1+1/(1−α))")]
    for k, (col, dsh, lab) in enumerate(rows):
        y = ly + k * 22
        parts.append(poly([(lx, y), (lx + 30, y)], col, 2.6, dash=dsh))
        parts.append(text(lx + 40, y + 4, lab, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "probes-uniform-vs-linear.svg"), W, H, *parts)


# ── Фігура 8 (вставка math «Ціна проби»): успішний пошук = площа = логарифм ──
def fig_harmonic():
    import math
    W, H = 740, 450
    parts = []
    parts.append(text(W / 2, 38, "Успішний пошук усереднює дешеві ранні вставки", size=15.5, bold=True))
    L, R = 100, 560
    T, B = 78, 356
    tmax = 0.85
    A = 0.8
    ymax = 7.0

    def X(t):
        return L + (t / tmax) * (R - L)

    def Y(v):
        return B - (min(v, ymax) / ymax) * (B - T)

    area = [(X(0.0), Y(0.0))]
    t = 0.0
    while t <= A + 1e-9:
        area.append((X(t), Y(1.0 / (1.0 - t))))
        t += 0.01
    area.append((X(A), Y(0.0)))
    dd = " ".join("%.1f,%.1f" % p for p in area)
    parts.append('<polygon points="%s" fill="#e8eefb" stroke="none"/>' % dd)

    parts.append(line(L, T, L, B, color=INK, sw=1.8))
    parts.append(line(L, B, R + 8, B, color=INK, sw=1.8))
    parts.append(text((L + R) / 2, B + 44, "частка заповнення при вставці  t", size=13))
    parts.append(text(L - 60, (T + B) / 2 - 4, "ціна", size=12.5, color=INK))
    parts.append(text(L - 60, (T + B) / 2 + 13, "вставки", size=12, color=MUTED))
    for t in [0.0, 0.25, 0.5, 0.8]:
        parts.append(line(X(t), B, X(t), B + 6, color=INK, sw=1.4))
        lab = "0" if t == 0.0 else ("%.2f" % t).rstrip("0").rstrip(".")
        parts.append(text(X(t), B + 22, lab, size=12, color=MUTED))
    for v in [0, 1, 2, 3, 4, 5]:
        parts.append(line(L - 6, Y(v), L, Y(v), color=INK, sw=1.4))
        parts.append(text(L - 13, Y(v) + 4, str(v), size=12, color=MUTED, anchor="end"))

    cpts = []
    t = 0.0
    while t <= tmax + 1e-9:
        v = 1.0 / (1.0 - t)
        if v > ymax:
            break
        cpts.append((X(t), Y(v)))
        t += 0.005
    parts.append(poly(cpts, NEG, 2.8))

    parts.append(line(X(A), Y(0.0), X(A), Y(5.0), color=MUTED, sw=1.2, dash="5,4"))
    parts.append(circle(X(A), Y(5.0), 3.5, fill=NEG, stroke=NEG))
    parts.append(text(X(A) + 8, Y(5.0) - 6, "1/(1−α) = 5", size=12.5, color=NEG, anchor="start"))
    parts.append(text(X(A) + 8, Y(5.0) + 12, "майбутній невдалий пошук", size=11, color=MUTED, anchor="start"))

    avg = (1.0 / A) * math.log(1.0 / (1.0 - A))
    parts.append(line(L, Y(avg), X(A), Y(avg), color=POS, sw=2.2, dash="8,5"))
    parts.append(text(X(0.02), Y(avg) - 8, "успішний пошук = площа / α ≈ 2.0", size=12.5, color=POS, anchor="start"))

    parts.append(text(X(0.30), Y(0.85), "площа = ln(1/(1−α))", size=12.5, color=NEG))
    parts.append(text(X(0.30), Y(0.85) + 17, "= ln 5 ≈ 1.61", size=12, color=NEG))

    render(os.path.join(IMG, "harmonic-area.svg"), W, H, *parts)


# ── Фігура 5 (вставка «Народження хешування»): часова смуга винаходу ─────────
IDEA = NEG      # ідея — синій
IMPL = FIELD    # реалізація — зелений
ANAL = POS      # аналіз — червоний
PUBL = MUTED    # публікація / огляд — сірий


def fig_timeline():
    W, H = 900, 610
    parts = []
    parts.append(text(W / 2, 34, "Народження хешування: ідея · реалізація · аналіз", size=18, bold=True))

    # ── легенда (фіксовані позиції, без накладань) ──
    legend = [(110, "ідея", IDEA), (240, "реалізація", IMPL),
              (400, "аналіз", ANAL), (532, "публікація / огляд", PUBL)]
    for lx, name, col in legend:
        parts.append(circle(lx, 66, 6, fill=col, stroke=col, sw=1))
        parts.append(text(lx + 14, 70, name, size=13, color=INK, anchor="start"))

    # ── вертикальна вісь часу ──
    axis_x = 214
    y_top, y_bot = 112, 556
    parts.append(line(axis_x, y_top, axis_x, y_bot, color=MUTED, sw=2))

    events = [
        ("1953", "Ганс Петер Лун · IBM",
         "ідея: розкидати ключі по «кошиках», колізії — в ланцюжок", IDEA),
        ("1954", "Амдал · Мак-Ґро · Семюел · IBM 701",
         "реалізація: відкрита адресація й лінійне пробування", IMPL),
        ("1957", "В. Веслі Петерсон",
         "перша публікація методу — у журналі IBM", PUBL),
        ("1958", "Андрій Єршов · СРСР",
         "незалежно доходить до того самого — і друкує", IMPL),
        ("1962–63", "Дональд Кнут",
         "перший аналіз — і початок «аналізу алгоритмів»", ANAL),
        ("1966", "Конгайм · Вайс",
         "перша публікація строгого аналізу", ANAL),
        ("1968", "Роберт Морріс · CACM",
         "огляд «Scatter Storage» виводить метод у відкриту науку", PUBL),
    ]
    n = len(events)
    step = (y_bot - y_top - 44) / (n - 1)
    for i, (yr, who, what, col) in enumerate(events):
        y = y_top + 22 + i * step
        parts.append(circle(axis_x, y, 8, fill=col, stroke=BG, sw=2))
        parts.append(text(axis_x - 24, y + 5, yr, size=15, color=INK, anchor="end", bold=True))
        parts.append(text(axis_x + 28, y - 6, who, size=14.5, color=col, anchor="start", bold=True))
        parts.append(text(axis_x + 28, y + 15, what, size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "hashing-timeline.svg"), W, H, *parts)


# ── Фігура 6 (вставка «Відкрита адресація на C»): розкладка в пам'яті ────────
def fig_memory():
    W, H = 860, 560
    OCC = "#eaf0fd"          # зайнята комірка
    TOMB = "#efeaf2"         # надгробок
    parts = []
    parts.append(text(W / 2, 38, "Розкладка в пам'яті: записи — у суцільному масиві, текст ключа — в купі", size=16, bold=True))
    parts.append(text(W / 2, 60, "стан комірки: EMPTY (порожня) · OCCUPIED (зайнята) · надгробок (прибрана)", size=12.5, color=MUTED))

    # ── struct HashTable ліворуч ──
    sx, sy, sw_, sh_ = 34, 150, 150, 176
    parts.append(rect(sx, sy, sw_, sh_, fill=FILL))
    parts.append(text(sx + sw_ / 2, sy + 26, "HashTable", size=14, bold=True))
    parts.append(text(sx + 18, sy + 58, "cap  = 8", size=13, anchor="start"))
    parts.append(text(sx + 18, sy + 84, "len  = 3", size=13, anchor="start", color=NEG))
    parts.append(text(sx + 18, sy + 110, "used = 4", size=13, anchor="start", color=POS))
    parts.append(text(sx + 18, sy + 146, "slots  ●", size=13, anchor="start"))
    parts.append(text(sx + sw_ / 2, sy + sh_ + 22, "used лічить і надгробок", size=11.5, color=MUTED))

    # ── масив: колонки  idx | стан | value | key ──
    ax = 232
    ay = 96
    rowh, gap = 48, 4
    st_x, st_w = ax + 34, 118
    v_x, v_w = st_x + st_w + 8, 66
    k_x, k_w = v_x + v_w + 8, 66
    heap_x, heap_w = k_x + k_w + 78, 74

    parts.append(text(st_x + st_w / 2, ay - 12, "стан", size=11.5, color=MUTED))
    parts.append(text(v_x + v_w / 2, ay - 12, "value", size=11.5, color=MUTED))
    parts.append(text(k_x + k_w / 2, ay - 12, "key", size=11.5, color=MUTED))
    parts.append(text(heap_x + heap_w / 2, ay - 12, "купа", size=11.5, color=MUTED))

    parts.append(arrow(sx + sw_ - 26, sy + 142, st_x - 6, ay + 20, color=MUTED, sw=1.6))

    contents = {
        2: ("OCCUPIED", "42", "cat"),
        3: ("надгробок", None, None),
        4: ("OCCUPIED", "3", "dog"),
        6: ("OCCUPIED", "7", "fox"),
    }
    for i in range(8):
        y = ay + i * (rowh + gap)
        parts.append(text(ax + 16, y + rowh / 2 + 5, str(i), size=12, color=MUTED))
        rec = contents.get(i)
        if rec is None:                                   # EMPTY
            for cx0, cw in ((st_x, st_w), (v_x, v_w), (k_x, k_w)):
                parts.append(rect(cx0, y, cw, rowh, fill=EMPTY))
            parts.append(text(st_x + st_w / 2, y + rowh / 2 + 5, "EMPTY", size=12, color=MUTED))
            parts.append(text(v_x + v_w / 2, y + rowh / 2 + 5, "—", size=13, color=MUTED))
            parts.append(text(k_x + k_w / 2, y + rowh / 2 + 5, "∅", size=15, color=MUTED))
            continue
        state, val, key = rec
        fill = OCC if state == "OCCUPIED" else TOMB
        tcol = NEG if state == "OCCUPIED" else MUTED
        for cx0, cw in ((st_x, st_w), (v_x, v_w), (k_x, k_w)):
            parts.append(rect(cx0, y, cw, rowh, fill=fill))
        parts.append(text(st_x + st_w / 2, y + rowh / 2 + 5, state, size=11.5, color=tcol, bold=(state == "OCCUPIED")))
        if state == "OCCUPIED":
            parts.append(text(v_x + v_w / 2, y + rowh / 2 + 5, val, size=13, bold=True))
            parts.append(text(k_x + k_w / 2, y + rowh / 2 + 5, "●", size=13, color=NEG))
            parts.append(rect(heap_x, y + 6, heap_w, rowh - 12, fill=OCC))
            parts.append(text(heap_x + heap_w / 2, y + rowh / 2 + 5, '"%s"' % key, size=13, color=NEG, bold=True))
            parts.append(arrow(k_x + k_w - 4, y + rowh / 2, heap_x - 4, y + rowh / 2, color=NEG, sw=1.6))
        else:                                             # надгробок
            parts.append(text(v_x + v_w / 2, y + rowh / 2 + 5, "—", size=13, color=MUTED))
            parts.append(text(k_x + k_w / 2, y + rowh / 2 + 5, "∅", size=15, color=MUTED))

    render(os.path.join(IMG, "memory-layout.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_collision()
    fig_clustering()
    fig_tombstone()
    fig_loadfactor()
    fig_timeline()
    fig_memory()
    fig_probes()
    fig_harmonic()
    print("OK: 8 SVG у", IMG)
