# -*- coding: utf-8 -*-
"""Фігури до теми «Тактований зсувний регістр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ff(x, y, w, h, top, inner=None, qlabel="Q"):
    """Один тригер: прямокутник, вхід D зліва, вихід Q справа,
    трикутник такту знизу. top — підпис над тригером, inner — біт усередині."""
    f = [rect(x, y, w, h, fill=FILL, stroke=LINE, sw=2)]
    if top:
        f.append(text(x + w / 2, y - 8, top, size=12, bold=True, color=MUTED))
    f.append(text(x + 12, y + h / 2 + 4, "D", size=11, bold=True))
    f.append(text(x + w - 12, y + h / 2 + 4, qlabel, size=11, bold=True))
    cy = y + h - 10
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" '
             'stroke-width="1.6"/>' % (x + 5, cy - 6, x + 15, cy, x + 5, cy + 6, LINE))
    if inner is not None:
        f.append(text(x + w / 2, y + h / 2 + 6, inner, size=18, bold=True, color=NEG))
    return "".join(f), x + w, x


# ── 1. Такт — єдиний диригент: на фронті кожна комірка фотографує сусіда ─────
def fig_clock_engine():
    W, H = 760, 410
    f = [text(W / 2, 26, "Спільний такт — один диригент на всі комірки", size=16, bold=True)]

    bw, bh, gap = 110, 66, 56
    x0, yT = 150, 78
    bits = ["1", "0", "1"]
    rights, lefts, mids = [], [], []
    for i, b in enumerate(bits):
        x = x0 + i * (bw + gap)
        frag, r, l = ff(x, yT, bw, bh, "комірка %d" % i, b)
        f.append(frag)
        rights.append(r); lefts.append(l); mids.append(x + bw / 2)
        if i > 0:
            f.append(arrow(rights[i - 1], yT + bh / 2, lefts[i], yT + bh / 2, sw=2))

    # вхід нового біта зліва
    f.append(text(x0 - 56, yT + bh / 2 - 12, "новий", size=11, bold=True, color=POS, anchor="middle"))
    f.append(arrow(x0 - 54, yT + bh / 2 + 4, lefts[0], yT + bh / 2 + 4, color=POS, sw=2.2))

    # СПІЛЬНА тактова лінія — одна на всіх, підкреслено
    yC = yT + bh + 56
    f.append(line(x0 - 30, yC, rights[-1] + 6, yC, color=NEG, sw=2.6))
    for m in mids:
        f.append(line(m - bw / 2 + 10, yC, m - bw / 2 + 10, yT + bh, color=NEG, sw=1.8))
    f.append(text(x0 - 36, yC + 5, "CLK", size=12, bold=True, anchor="end", color=NEG))
    # символ фронту на лінії
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="2"/>'
             % (rights[-1] + 14, yC + 8, rights[-1] + 14, yC - 8,
                rights[-1] + 26, yC - 8, rights[-1] + 26, yC + 8, POS))
    f.append(text(rights[-1] + 20, yC + 22, "↑", size=14, bold=True, color=POS))

    # пояснення «фотографує доперехідне» — стрілка від виходу 0 до входу 1, з міткою
    f.append(text(mids[0] + (gap + bw) / 2 - bw / 2, yT - 30,
                  "хапає СТАРИЙ вихід сусіда", size=11, bold=True, color=FIELD))

    b, w, h = textbox(W / 2, yC + 78,
                      "На фронті ↑ кожна комірка фотографує те, що було на виході сусіда ДО переходу.\n"
                      "Усі спрацьовують в ту саму мить — низка зсувається рівно на щабель, без гонитви.",
                      size=12.5, fill="#eef6ef", stroke=FIELD, pad=12)
    f.append(b)
    return W, H, f


# ── 2. Таймінг: вікно setup/hold і стеля частоти ────────────────────────────
def fig_setup_hold():
    W, H = 760, 430
    f = [text(W / 2, 26, "Чому є стеля частоти: дані мусять устигнути до фронту", size=15.5, bold=True)]

    left, right = 130, W - 50
    lo = 30

    # CLK з двома фронтами
    yclk = 80
    e1 = left + 90
    e2 = right - 90
    f.append(text(left - 14, yclk - lo / 2, "CLK", size=12, bold=True, anchor="end", color=NEG))
    pts = [(left, yclk)]
    for ex in (e1, e2):
        w = 26
        pts += [(ex, yclk), (ex, yclk - lo), (ex + w, yclk - lo), (ex + w, yclk)]
    pts.append((right, yclk))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))
    for ex in (e1, e2):
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                 % (ex - 5, yclk - lo - 4, ex + 5, yclk - lo - 4, ex, yclk - lo + 4, POS))

    # D на вході наступної комірки — стає валідним після t_pd попередньої
    yd = 168
    f.append(text(left - 14, yd - lo / 2, "D", size=12, bold=True, anchor="end"))
    valid_from = e1 + 70           # дані сусіда «доїхали» (t_pd)
    valid_to = e2 - 18
    f.append(line(left, yd - lo / 2, valid_from, yd - lo / 2, color=MUTED, sw=2, dash="5 4"))
    f.append(rect(valid_from, yd - lo, valid_to - valid_from, lo, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text((valid_from + valid_to) / 2, yd - lo / 2 + 4, "дані валідні", size=11, bold=True, color=FIELD))

    # t_pd дужка від e1 до valid_from
    f.append(line(e1, yd + 22, valid_from, yd + 22, color=NEG, sw=1.6))
    f.append(text((e1 + valid_from) / 2, yd + 38, "t_pd сусіда", size=11, bold=True, color=NEG))

    # вікно setup перед e2
    setup_x = e2 - 40
    f.append(line(setup_x, 60, setup_x, yd + 6, color=POS, sw=1.4, dash="4 4"))
    f.append(line(e2, 60, e2, yd + 6, color=POS, sw=1.4, dash="4 4"))
    f.append(line(setup_x, yd - lo - 14, e2, yd - lo - 14, color=POS, sw=1.6))
    f.append(text((setup_x + e2) / 2, yd - lo - 20, "setup", size=11, bold=True, color=POS))

    # бюджет періоду
    f.append(line(e1, yclk - lo - 22, e2, yclk - lo - 22, color=INK, sw=1.4))
    f.append(text((e1 + e2) / 2, yclk - lo - 28, "період T", size=11, bold=True))

    b, w, h = textbox(W / 2, 320,
                      "Між двома фронтами вихід сусіда мусить «доїхати» (t_pd) і ще постояти стабільно\n"
                      "до фронту (setup).  Звідси стеля:   t_pd + t_setup  ≤  T  =  1 / f_max .",
                      size=12.5, fill=FILL, stroke=LINE, pad=12)
    f.append(b)

    b2, w2, h2 = textbox(W / 2, 392,
                         "Внутрішня збірка чесна: кожна комірка живить лише сусіда, hold майже завжди в нормі.",
                         size=11.5, fill="#eef6ef", stroke=FIELD, pad=10)
    f.append(b2)
    return W, H, f


# ── 3. Лінія затримки з відводами = ядро FIR-фільтра ────────────────────────
def fig_tapped_delay():
    W, H = 760, 430
    f = [text(W / 2, 24, "Тактований регістр — це лінія затримки з відводами (ядро FIR)", size=15, bold=True)]

    bw, bh, gap = 96, 58, 40
    x0, yT = 96, 70
    taps = ["x[n]", "x[n−1]", "x[n−2]", "x[n−3]"]
    coeffs = ["b₀", "b₁", "b₂", "b₃"]
    mids, rights, lefts = [], [], []
    for i, t in enumerate(taps):
        x = x0 + i * (bw + gap)
        frag, r, l = ff(x, yT, bw, bh, "", None)
        f.append(frag)
        f.append(text(x + bw / 2, yT + bh / 2 + 5, t, size=12, bold=True, color=NEG))
        mids.append(x + bw / 2); rights.append(r); lefts.append(l)
        if i > 0:
            f.append(arrow(rights[i - 1], yT + bh / 2, lefts[i], yT + bh / 2, sw=1.8))

    # вхід нового відліку зліва
    f.append(text(x0 - 50, yT + bh / 2 - 12, "новий", size=11, bold=True, color=POS))
    f.append(text(x0 - 50, yT + bh / 2 + 4, "відлік", size=11, bold=True, color=POS))
    f.append(arrow(x0 - 50, yT + bh / 2 + 16, lefts[0], yT + bh / 2 + 16, color=POS, sw=2.2))

    # відводи вниз → множники ·b_k
    ym = yT + bh + 46
    for i, m in enumerate(mids):
        f.append(arrow(m, yT + bh, m, ym - 14, color=MUTED, sw=1.6))
        f.append(circle(m, ym, 15, fill="#fdecea", stroke=POS, sw=1.8))
        f.append(text(m, ym + 5, "×", size=15, bold=True, color=POS))
        f.append(text(m + 22, ym - 4, coeffs[i], size=12, bold=True, color=POS, anchor="start"))

    # суматор
    ys = ym + 70
    sx = (mids[0] + mids[-1]) / 2
    f.append(circle(sx, ys, 22, fill="#eef6ef", stroke=FIELD, sw=2.2))
    f.append(text(sx, ys + 7, "Σ", size=22, bold=True, color=FIELD))
    for m in mids:
        f.append(arrow(m, ym + 15, sx, ys - 20, color=MUTED, sw=1.4))
    f.append(arrow(sx, ys + 22, sx, ys + 50, color=FIELD, sw=2.2))
    f.append(text(sx, ys + 66, "y[n]", size=13, bold=True, color=FIELD))

    b, w, h = textbox(W / 2, H - 22,
                      "Кожен такт відліки зсуваються; відвід k — це x[n−k]. "
                      "Помнож на bₖ, склади →  y[n] = Σ bₖ · x[n−k].",
                      size=12, fill="#eef6ef", stroke=FIELD, pad=11)
    f.append(b)
    return W, H, f


# ── 4. Родовід лінії затримки крізь покоління (для hist-вставки) ────────────
def fig_delay_line_genealogy():
    W, H = 780, 580
    f = [text(W / 2, 26, "Одна ідея «затримати на такт» — крізь чотири носії", size=16, bold=True)]

    # чотири покоління: підпис-епоха, носій, як зберігає біт, дійові особи
    gens = [
        ("1943",  "Ртутна акустична лінія",
         "звукова хвиля біжить\nстовпом ртуті ~1.45 мм/мкс",
         "Шоклі · Еккерт · Моклі",  NEG),
        ("1950-і", "Магнітострикційний дріт",
         "крутильна хвиля біжить\nсталевим/нікелевим дротом",
         "калькулятори: Olivetti P101", FIELD),
        ("1969",  "Ківшовий ланцюг (BBD)",
         "заряд перекочується\nз ємності в ємність по такту",
         "Санґстер · Теер (Philips)", POS),
        ("1970-і", "Тактований зсувний регістр / CCD",
         "біт стоїть у тригері,\nна фронті стрибає до сусіда",
         "Бойл · Сміт (CCD, Bell)", INK),
    ]

    bx, bw, bh = 60, W - 120, 96
    y0, gap = 66, 22
    for i, (era, medium, how, who, col) in enumerate(gens):
        y = y0 + i * (bh + gap)
        f.append(rect(bx, y, bw, bh, fill=FILL, stroke=col, sw=2.4))
        # смужка-епоха зліва
        f.append(rect(bx, y, 84, bh, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(bx + 42, y + bh / 2 - 4, era, size=15, bold=True, color=col))
        f.append(text(bx + 42, y + bh / 2 + 16, "рік", size=10, color=MUTED))
        # носій — заголовок
        f.append(text(bx + 104, y + 26, medium, size=14, bold=True, anchor="start", color=col))
        # як зберігає — два рядки
        f.append(mtext(bx + 104, y + 48, how, size=11.5, color=INK, anchor="start", lh=1.25))
        # хто — праворуч
        f.append(text(bx + bw - 14, y + bh - 12, who, size=11, bold=True, anchor="end", color=MUTED))
        # стрілка «успадкування» вниз
        if i < len(gens) - 1:
            ax = bx + bw / 2
            f.append(arrow(ax, y + bh + 2, ax, y + bh + gap - 2, color=MUTED, sw=2))

    b, w, h = textbox(W / 2, H - 24,
                      "Носій щоразу інший — ртуть, дріт, ланцюг ємностей, кремнієвий тригер, —\n"
                      "а дія та сама: затримати сигнал рівно на один такт і передати далі.",
                      size=12.5, fill="#eef6ef", stroke=FIELD, pad=12)
    f.append(b)
    return W, H, f


# ════════════════════════════════════════════════════════════════════════════
# Фігури до вставки math-fir-tapped-delay.md (виведення FIR-суми)
# ════════════════════════════════════════════════════════════════════════════
import math, random


def _polyline(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, fill, color, sw, d))


def _stem(x, y0, y1, color, sw=2.0, dot=3.2):
    """Стеблинка відліку: вертикаль від осі до значення + кружечок на вершині."""
    return (line(x, y0, x, y1, color=color, sw=sw) +
            circle(x, y1, dot, fill=color, stroke=color, sw=1))


# ── mA. Ковзне середнє згладжує дрижання (інтуїція «чому усереднення») ────────
def fig_moving_average():
    W, H = 780, 420
    f = [text(W / 2, 26, "Ковзне середнє: складаєш кілька сусідів — дрижання гасне",
              size=16, bold=True)]

    x0, xW = 70, W - 110
    yMid = 220
    amp = 96
    f.append(line(x0, yMid, x0 + xW, yMid, color=MUTED, sw=1.4, dash="4 4"))
    f.append(arrow(x0 + xW, yMid, x0 + xW + 20, yMid, color=INK, sw=1.8))
    f.append(text(x0 + xW + 12, yMid + 20, "n", size=12, italic=True, color=MUTED))
    f.append(text(x0 - 10, yMid - amp - 2, "значення", size=11, color=MUTED, anchor="end"))

    Npt = 30
    random.seed(7)
    xs = [x0 + 14 + i * (xW - 28) / (Npt - 1) for i in range(Npt)]
    true_v = [math.sin(2 * math.pi * i / (Npt - 1) * 1.15) for i in range(Npt)]
    noise = [(random.random() - 0.5) * 1.05 for _ in range(Npt)]
    raw = [true_v[i] + noise[i] for i in range(Npt)]

    def yv(v):
        return yMid - v * amp * 0.6

    for i in range(Npt):
        f.append(line(xs[i], yMid, xs[i], yv(raw[i]), color="#c7ccd4", sw=1.6))
        f.append(circle(xs[i], yv(raw[i]), 2.6, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(xs[1], yv(raw[1]) - 14, "сирі відліки x[n]", size=11, color=MUTED,
                  anchor="start", bold=True))

    K = 5
    ma = []
    for i in range(Npt):
        lo = max(0, i - K + 1)
        seg = raw[lo:i + 1]
        ma.append(sum(seg) / len(seg))
    f.append(_polyline([(xs[i], yv(ma[i])) for i in range(Npt)], color=FIELD, sw=3.0))

    j = 18
    for k in range(j - K + 1, j + 1):
        f.append(circle(xs[k], yv(raw[k]), 4.2, fill="none", stroke=POS, sw=2))
    f.append(line(xs[j - K + 1] - 6, yMid + amp * 0.52, xs[j] + 6, yMid + amp * 0.52,
                  color=POS, sw=1.6))
    f.append(text((xs[j - K + 1] + xs[j]) / 2, yMid + amp * 0.52 + 16,
                  "вікно з 5 сусідів", size=11, color=POS, bold=True))
    f.append(arrow((xs[j - K + 1] + xs[j]) / 2, yMid + amp * 0.52 + 4, xs[j], yv(ma[j]) + 6,
                   color=POS, sw=1.6))
    f.append(text(xs[j] + 8, yv(ma[j]) - 8, "y[n] — середнє вікна", size=11, color=FIELD,
                  anchor="start", bold=True))

    b, w, h = textbox(W / 2, H - 34,
                      "Кожен вихід — середнє останніх K відліків. Випадкові стрибки в різні боки\n"
                      "гасять одне одного, повільна форма лишається: вийшов плавний слід.",
                      size=12.5, fill="#eef6ef", stroke=FIELD, pad=12)
    f.append(b)
    return W, H, f


# ── mB. Імпульсна відповідь: подай одну 1 → на виході САМІ коефіцієнти ────────
def fig_impulse_response():
    W, H = 780, 430
    f = [text(W / 2, 26, "Чому «скінченно-імпульсний»: подай одну 1 — вийдуть самі bₖ",
              size=15.5, bold=True)]

    x0 = 70
    axW = 300
    gap = 96
    yBase = 250
    amp = 120

    def panel(px, title, vals, colors, labels):
        out = [text(px + axW / 2, 66, title, size=13, bold=True)]
        out.append(line(px, yBase, px + axW, yBase, color=INK, sw=2))
        out.append(arrow(px + axW, yBase, px + axW + 16, yBase, color=INK, sw=1.8))
        out.append(text(px + axW + 10, yBase + 18, "n", size=11, italic=True, color=MUTED))
        n = len(vals)
        step = axW / (n + 0.5)
        for i, v in enumerate(vals):
            xx = px + step * (i + 0.7)
            yy = yBase - v * amp
            col = colors[i] if isinstance(colors, list) else colors
            out.append(_stem(xx, yBase, yy, col, sw=2.4, dot=4))
            out.append(text(xx, yBase + 18, "%d" % i, size=10, color=MUTED))
            if labels and labels[i]:
                out.append(text(xx, yy - 12, labels[i], size=11, color=col, bold=True))
        return out

    inp = [1, 0, 0, 0, 0, 0]
    f += panel(x0, "вхід: одиничний імпульс δ[n]", inp, NEG,
               ["1", "0", "0", "0", "0", "0"])

    px2 = x0 + axW + gap
    outv = [0.9, 0.65, 0.45, 0.25, 0, 0]
    f += panel(px2, "вихід: h[n] = послідовність bₖ", outv,
               [POS, POS, POS, POS, MUTED, MUTED],
               ["b₀", "b₁", "b₂", "b₃", "0", "0"])

    f.append(arrow(x0 + axW + 8, 150, px2 - 8, 150, color=INK, sw=2))
    f.append(text((x0 + axW + px2) / 2, 140, "FIR", size=12, bold=True))

    b, w, h = textbox(W / 2, H - 34,
                      "Одна 1 заходить у регістр і крокує по комірках: на такті k вона стоїть у k-му\n"
                      "відводі, множиться на bₖ — і виходить bₖ. Пройшла всі N комірок → вихід згас.\n"
                      "Тому відповідь на імпульс СКІНЧЕННА, а коефіцієнти bₖ — це і є ця відповідь.",
                      size=12, fill="#eef6ef", stroke=FIELD, pad=12)
    f.append(b)
    return W, H, f


# ── mC. Частотний відбір: повільне проходить, швидке-змінне гаситься ──────────
def fig_freq_select():
    W, H = 780, 440
    f = [text(W / 2, 26, "Той самий усереднювач: повільне пропускає, швидке-змінне гасить",
              size=15, bold=True)]

    x0 = 84
    axW = W - 168
    K = 4

    def track(yMid, amp, gen, glabel, gcol, note):
        out = []
        out.append(line(x0, yMid, x0 + axW, yMid, color=MUTED, sw=1.2, dash="4 4"))
        Npt = 26
        xs = [x0 + 12 + i * (axW - 24) / (Npt - 1) for i in range(Npt)]
        raw = [gen(i) for i in range(Npt)]

        def yv(v):
            return yMid - v * amp

        for i in range(Npt):
            out.append(line(xs[i], yMid, xs[i], yv(raw[i]), color=gcol, sw=1.6))
            out.append(circle(xs[i], yv(raw[i]), 2.4, fill=gcol, stroke=gcol, sw=1))
        ma = []
        for i in range(Npt):
            lo = max(0, i - K + 1)
            seg = raw[lo:i + 1]
            ma.append(sum(seg) / len(seg))
        out.append(_polyline([(xs[i], yv(ma[i])) for i in range(Npt)], color=INK, sw=3.0))
        out.append(text(x0 - 8, yMid - amp - 2, glabel, size=11, color=gcol,
                        anchor="end", bold=True))
        out.append(text(x0 + axW - 4, yMid - amp - 2, note, size=11.5, color=INK,
                        anchor="end", bold=True))
        return out

    f += track(140, 72, lambda i: math.sin(2 * math.pi * i / 25 * 1.0),
               "повільний вхід", NEG, "середнє (жирне) ≈ сам сигнал")
    f += track(320, 72, lambda i: 1.0 if i % 2 == 0 else -1.0,
               "швидкий ±1", POS, "середнє ≈ 0 — вирізано")

    b, w, h = textbox(W / 2, H - 30,
                      "У вікні усереднення повільний сигнал майже сталий — сума ≈ сам сигнал (проходить).\n"
                      "Знакозмінний +1,−1,… у сумі гаситься в нуль (вирізаний). Ось звідки «пропускає\n"
                      "низькі частоти»: усереднення — це фільтр, а коефіцієнти задають, ЩО пропустити.",
                      size=12, fill=FILL, stroke=LINE, pad=12)
    f.append(b)
    return W, H, f


def main():
    jobs = [
        ("clock-engine.svg", fig_clock_engine),
        ("setup-hold-fmax.svg", fig_setup_hold),
        ("tapped-delay-fir.svg", fig_tapped_delay),
        ("delay-line-genealogy.svg", fig_delay_line_genealogy),
        ("fir-moving-average.svg", fig_moving_average),
        ("fir-impulse-response.svg", fig_impulse_response),
        ("fir-freq-select.svg", fig_freq_select),
    ]
    for name, fn in jobs:
        W, H, frags = fn()
        render(os.path.join(IMG, name), W, H, *frags)
        print("wrote", name)


if __name__ == "__main__":
    main()
