# -*- coding: utf-8 -*-
"""Фігури до теми «Сенсорне злиття (fusion): комплементарний фільтр і Калман».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GYRO = POS    # гіроскоп — «гарячий», швидкий верх спектра (червоний)
ACC  = NEG    # акселерометр — «холодний», повільний низ спектра (синій)
SUM  = FIELD  # зелене — сума/оптимум


# ── спільні примітиви ────────────────────────────────────────────────────────
def axis(x0, x1, y, color=INK, sw=1.6, label=None):
    out = line(x0, y, x1 + 6, y, color=color, sw=sw)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x1 + 14, y, x1 + 6, y - 4, x1 + 6, y + 4, color))
    if label:
        out += text(x1 + 12, y + 20, label, size=10.5, color=MUTED, italic=True, anchor="end")
    return out


def vaxis(x, y0, y1, color=INK, sw=1.6):
    """вертикальна вісь із стрілкою вгору (y1 < y0)"""
    out = line(x, y0, x, y1 - 6, color=color, sw=sw)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x, y1 - 14, x - 4, y1 - 6, x + 4, y1 - 6, color))
    return out


def polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round"/>' % (p, color, sw, d))


def area(pts, base_y, color, opacity=0.5, stroke=None, sw=1.6):
    stroke = stroke or color
    poly = [(pts[0][0], base_y)] + list(pts) + [(pts[-1][0], base_y)]
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, color, opacity, stroke, sw))


def gauss(mu, sig, x0v, x1v, X, Y, N=140):
    """точки гаусіани g(x)=exp(...)·(1/σ) у пікселях; X,Y — мапери в пікселі."""
    pts = []
    for i in range(N + 1):
        v = x0v + (x1v - x0v) * i / N
        g = (1.0 / (sig * math.sqrt(2 * math.pi))) * math.exp(-((v - mu) ** 2) / (2 * sig * sig))
        pts.append((X(v), Y(g)))
    return pts


# ── 1. Дзеркальні смуги похибок + доповняльні ваги, що в сумі дають 1 ──────────
def fig_complementary_spectrum():
    W, H = 770, 500
    f = [text(W / 2, 26, "Комплементарний поділ: кожен давач звучить лише там, де він правдивий",
              size=15, bold=True)]

    x0, x1 = 96, 664
    xc = x0 + 0.5 * (x1 - x0)          # частота переходу f_c (лог-центр)

    def X(u):                          # u = log10(f/f_c) ∈ [-2, 2]
        return x0 + (u + 2) / 4.0 * (x1 - x0)

    # ── верхня панель: доповняльні ваги ──
    yT0, top_h = 258, 176               # v=0 → yT0 ; v=1 → yT0-top_h
    def YT(v): return yT0 - v * top_h
    f.append(text(x0, 62, "Ваги злиття доповняльні — у кожній точці спектра дають рівно 1",
                  size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yT0, label="частота (лог)"))
    f.append(vaxis(x0, yT0, YT(1) - 4))
    f.append(text(x0 - 8, YT(1) + 4, "1", size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, YT(0.5) + 4, "½", size=10, color=MUTED, anchor="end"))

    # лінія суми = 1 (зелена)
    f.append(line(x0, YT(1), x1, YT(1), color=SUM, sw=2.6))
    f.append(text(x1, YT(1) - 9, "сума ваг = 1 → справжній кут проходить цілим",
                  size=10.5, color=SUM, bold=True, anchor="end"))

    def wL(u): return 1.0 / (1.0 + 10 ** (2 * u))     # акселерометр (ФНЧ)
    def wH(u): return 1.0 - wL(u)                      # гіроскоп (ФВЧ)
    accL = [(X(u), YT(wL(u))) for u in [i / 20.0 - 2 for i in range(81)]]
    gyrL = [(X(u), YT(wH(u))) for u in [i / 20.0 - 2 for i in range(81)]]
    f.append(polyline(accL, ACC, sw=2.8))
    f.append(polyline(gyrL, GYRO, sw=2.8))
    f.append(text(X(-1.55), YT(0.9) - 8, "акселерометр (ФНЧ): низ", size=10.5, color=ACC, bold=True, anchor="start"))
    f.append(text(X(1.55), YT(0.9) - 8, "гіроскоп (ФВЧ): верх", size=10.5, color=GYRO, bold=True, anchor="end"))

    # точка переходу
    f.append(circle(xc, YT(0.5), 4.2, fill=INK, stroke=INK, sw=0))
    f.append(text(xc + 10, YT(0.5) - 8, "f_c: кожен −3 дБ (½)", size=10.5, color=INK, bold=True, anchor="start"))

    # ── нижня панель: де в спектрі живе похибка кожного ──
    yB0, bot_h = 452, 120
    def YB(v): return yB0 - v * bot_h
    f.append(text(x0, 322, "А похибки дзеркальні: дрейф гіроскопа — унизу, шум акселерометра — угорі",
                  size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yB0, label="частота (лог)"))

    us = [i / 40.0 - 2 for i in range(161)]
    def edrift(u): return 1.0 / (1.0 + 10 ** (1.6 * (u + 0.35)))   # спадає з частотою
    def enoise(u): return 1.0 / (1.0 + 10 ** (-1.6 * (u - 0.35)))  # зростає з частотою
    dpts = [(X(u), YB(edrift(u))) for u in us]
    npts = [(X(u), YB(enoise(u))) for u in us]
    f.append(area(dpts, yB0, GYRO, opacity=0.32))
    f.append(area(npts, yB0, ACC, opacity=0.30))
    f.append(text(X(-1.5), YB(0.55), "дрейф гіроскопа", size=10.5, color=GYRO, bold=True, anchor="middle"))
    f.append(text(X(1.5), YB(0.55), "шум акселерометра", size=10.5, color=ACC, bold=True, anchor="middle"))
    f.append(text(X(-1.9), yB0 + 18, "низькі (повільне)", size=9.5, color=MUTED, italic=True, anchor="start"))
    f.append(text(X(1.9), yB0 + 18, "високі (швидке)", size=9.5, color=MUTED, italic=True, anchor="end"))

    # спільна вертикаль f_c крізь обидві панелі
    f.append(line(xc, YT(1) - 2, xc, yB0, color=MUTED, sw=1.4, dash="5,5"))
    f.append(text(xc, 300, "f_c", size=11, color=MUTED, bold=True, italic=True))

    render(os.path.join(IMG, "complementary-spectrum.svg"), W, H, *f)


# ── 2. Обернене до дисперсій злиття: добуток гаусіан вужчий за обидві ──────────
def fig_inverse_variance():
    W, H = 720, 380
    f = [text(W / 2, 26, "Оптимальне злиття: дві оцінки множаться у вужчу за обидві",
              size=15, bold=True)]

    x0, x1 = 84, 636
    base = 322
    x0v, x1v = 0.0, 10.0

    def X(v): return x0 + (v - x0v) / (x1v - x0v) * (x1 - x0)

    mu1, s1 = 3.0, 2.0     # передбачення (широке)
    mu2, s2 = 7.0, 1.2     # вимір (вужче)
    w1, w2 = 1 / s1 / s1, 1 / s2 / s2
    muF = (mu1 * w1 + mu2 * w2) / (w1 + w2)
    sF = math.sqrt(1 / (w1 + w2))

    peakF = 1.0 / (sF * math.sqrt(2 * math.pi))
    SCALE = 250.0 / peakF
    def Y(g): return base - g * SCALE

    f.append(axis(x0, x1, base, label="значення величини"))

    g1 = gauss(mu1, s1, x0v, x1v, X, Y)
    g2 = gauss(mu2, s2, x0v, x1v, X, Y)
    gF = gauss(muF, sF, x0v, x1v, X, Y)
    f.append(area(g1, base, ACC, opacity=0.20, sw=2.4))
    f.append(area(g2, base, GYRO, opacity=0.20, sw=2.4))
    f.append(area(gF, base, SUM, opacity=0.32, sw=2.8))

    # вертикалі центрів
    for mu, col in [(mu1, ACC), (mu2, GYRO), (muF, SUM)]:
        g = (1.0 / (({mu1: s1, mu2: s2}.get(mu, sF)) * math.sqrt(2 * math.pi)))
        f.append(line(X(mu), base, X(mu), Y(g), color=col, sw=1.4, dash="4,4"))

    # підписи (рознесені по висоті, щоб не накладались)
    f.append(text(X(mu1), Y(1 / s1 / math.sqrt(2 * math.pi)) - 12,
                  "передбачення", size=11, color=ACC, bold=True))
    f.append(text(X(mu1), Y(1 / s1 / math.sqrt(2 * math.pi)) + 2,
                  "широке, непевне", size=9.5, color=ACC))
    f.append(text(X(mu2) + 44, Y(1 / s2 / math.sqrt(2 * math.pi)) - 6,
                  "вимір", size=11, color=GYRO, bold=True, anchor="middle"))
    f.append(text(X(mu2) + 52, Y(1 / s2 / math.sqrt(2 * math.pi)) + 8,
                  "вужчий, певніший", size=9.5, color=GYRO, anchor="middle"))
    f.append(text(X(muF) - 6, Y(peakF) - 12, "злиття", size=11.5, color=SUM, bold=True, anchor="end"))
    f.append(text(X(muF) - 6, Y(peakF) + 1, "найвужче — точніше за обидва", size=9.5, color=SUM, anchor="end"))

    # «ближче до певнішого»
    f.append(text(X(muF) + 4, base - 20, "лягає ближче", size=9.5, color=MUTED, italic=True, anchor="start"))
    f.append(text(X(muF) + 4, base - 8, "до певнішого →", size=9.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(IMG, "inverse-variance.svg"), W, H, *f)


# ── 3. Коефіцієнт Калмана сходиться до фіксованої довіри комплементарного ─────
def fig_gain_convergence():
    W, H = 720, 360
    f = [text(W / 2, 26, "Комплементарний фільтр — це заморожений Калман",
              size=15, bold=True)]

    x0, x1 = 92, 662
    y0, y1 = 306, 66                 # K=0 → y0 ; K=1 → y1
    Nt = 14
    Q, R, P = 0.1, 1.0, 10.0        # реалістична збіжність за кілька тактів

    def X(n): return x0 + n / Nt * (x1 - x0)
    def Y(k): return y0 - k * (y0 - y1)

    # осі
    f.append(axis(x0, x1, y0, label="такти n"))
    f.append(vaxis(x0, y0, y1 - 2))
    for kv in [0.0, 0.5, 1.0]:
        f.append(line(x0 - 5, Y(kv), x0, Y(kv), color=INK, sw=1.2))
        f.append(text(x0 - 9, Y(kv) + 4, ("%.1f" % kv), size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 30, Y(0.5), "K", size=13, color=INK, bold=True, italic=True, anchor="middle"))

    # рекурсія коефіцієнта
    Ks = []
    for n in range(1, Nt + 1):
        Pm = P + Q
        K = Pm / (Pm + R)
        P = (1 - K) * Pm
        Ks.append((n, K))
    Kinf = (Q + math.sqrt(Q * Q + 4 * Q * R)) / 2
    Kinf = Kinf / (Kinf + R)

    # фіксована довіра комплементарного (1 − α = K_∞)
    f.append(line(x0, Y(Kinf), x1, Y(Kinf), color=MUTED, sw=2.2, dash="7,5"))
    f.append(text(x1, Y(Kinf) + 18, "1−α — фіксована довіра комплементарного",
                  size=10.5, color=MUTED, bold=True, anchor="end"))

    # крива K Калмана
    pts = [(X(n), Y(k)) for n, k in Ks]
    f.append(polyline(pts, SUM, sw=2.8))
    for n, k in Ks:
        f.append(circle(X(n), Y(k), 3.4, fill=SUM, stroke=SUM, sw=0))

    # анотації
    n1, k1 = Ks[0]
    f.append(text(X(n1) + 8, Y(k1) - 6, "стартує високим:", size=10.5, color=SUM, bold=True, anchor="start"))
    f.append(text(X(n1) + 8, Y(k1) + 8, "жадібно вбирає перші виміри", size=10, color=SUM, anchor="start"))
    f.append(text(X(Nt), Y(Kinf) - 12, "K сходиться до K_∞ = 1−α", size=10.5, color=INK, bold=True, anchor="end"))

    render(os.path.join(IMG, "gain-convergence.svg"), W, H, *f)


# ── 4. Простір станів: корекція кута через коваріацію править і зсув ───────────
def fig_state_space_bias():
    W, H = 780, 520
    f = [text(W / 2, 26, "Простір станів: акселерометр бачить лише кут, а виправляє й зсув",
              size=15, bold=True)]

    # ── сенсори згори ──
    gx, gw = 56, 214
    f.append(rect(gx, 54, gw, 52, fill="#fdecea", stroke=GYRO, sw=1.8))
    f.append(mtext(gx + gw / 2, 76, ["гіроскоп: ω", "кутова швидкість"], size=11, color=INK))
    ax_, aw = 510, 214
    f.append(rect(ax_, 54, aw, 52, fill="#eef2fb", stroke=ACC, sw=1.8))
    f.append(mtext(ax_ + aw / 2, 76, ["акселерометр: z", "прямий кут (шумний)"], size=11, color=INK))

    # ── центральний вектор стану ──
    sx, sy, sw_, sh = 300, 168, 180, 112
    f.append(rect(sx, sy, sw_, sh, fill="#f4f6f8", stroke=INK, sw=2))
    f.append(text(sx + sw_ / 2, sy - 8, "вектор стану  x", size=11.5, color=INK, bold=True))
    f.append(line(sx, sy + sh / 2, sx + sw_, sy + sh / 2, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(sx + sw_ / 2, sy + 34, "θ — кут нахилу", size=12, color=INK, bold=True))
    f.append(text(sx + sw_ / 2, sy + 88, "b — зсув нуля гіро", size=12, color=INK, bold=True))
    f.append(text(sx + sw_ / 2, sy + 72, "(прихований)", size=9.5, color=MUTED))

    # ── гіроскоп → передбачення (ω − b) → θ ──
    f.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (gx + gw / 2, 106, gx + gw / 2, 150, sx - 34, sy + 30, sx - 2, sy + 30, GYRO))
    f.append(text(gx + 2, 138, "передбачення:", size=10.5, color=GYRO, bold=True, anchor="start"))
    f.append(text(gx + 2, 152, "θ⁻ = θ + (ω − b)·dt", size=10.5, color=GYRO, bold=True, anchor="start"))

    # b подається у передбачення з мінусом (петля знизу зліва)
    f.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
             % (sx - 2, sy + 88, sx - 66, sy + 88, sx - 66, sy + 42, sx - 2, sy + 42, MUTED))
    f.append(text(sx - 74, sy + 68, "b віднімається", size=9.5, color=MUTED, italic=True, anchor="end"))

    # ── акселерометр → оновлення → лише θ ──
    f.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (ax_ + aw / 2, 106, ax_ + aw / 2, 150, sx + sw_ + 34, sy + 30, sx + sw_ + 2, sy + 30, ACC))
    f.append(text(ax_ + aw - 2, 138, "оновлення:", size=10.5, color=ACC, bold=True, anchor="end"))
    f.append(text(ax_ + aw - 2, 152, "бачить лише θ  (H = [1  0])", size=10.5, color=ACC, bold=True, anchor="end"))

    # ── ключова стрілка: корекція θ перетікає у b через коваріацію ──
    f.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.8" marker-end="url(#arrow)"/>'
             % (sx + sw_ / 2 + 24, sy + 34, sx + 156, sy + 54, sx + 156, sy + 150, sx + sw_ / 2 + 24, sy + 92, SUM))
    f.append(text(sx + 168, sy + 58, "корекція кута", size=10.5, color=SUM, bold=True, anchor="start"))
    f.append(text(sx + 168, sy + 74, "перетікає у зсув", size=10.5, color=SUM, bold=True, anchor="start"))

    # ── матриця коваріації P з підсвіченою поза-діагоналлю ──
    px, py, cell = 300, 336, 84
    f.append(text(px + cell, py - 12, "коваріація  P пам'ятає цей зв'язок", size=11.5, color=INK, bold=True))
    cells = [(0, 0, "σ²θ", FILL), (1, 0, "P_θb", "#eafaf1"),
             (0, 1, "P_bθ", "#eafaf1"), (1, 1, "σ²b", FILL)]
    for cxi, cyi, lab, fill in cells:
        rxp, ryp = px + cxi * cell, py + cyi * cell
        stroke = SUM if fill != FILL else LINE
        sw = 2.4 if fill != FILL else 1.4
        f.append(rect(rxp, ryp, cell, cell, fill=fill, stroke=stroke, sw=sw, rx=4))
        f.append(text(rxp + cell / 2, ryp + cell / 2 + 5, lab,
                      size=13, color=(SUM if fill != FILL else INK), bold=(fill != FILL)))
    f.append(text(px + 2 * cell + 18, py + cell - 6, "поза-діагональ", size=10.5, color=SUM, bold=True, anchor="start"))
    f.append(text(px + 2 * cell + 18, py + cell + 10, "зв'язує кут і зсув", size=10, color=SUM, anchor="start"))

    f.append(text(W / 2, 502,
                  "фільтр вивчає b і віднімає дрейф у корені — одне число α комплементарного так не може",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "state-space-bias.svg"), W, H, *f)


# ── 5. Добуток гаусіан = сума парабол: точності (кривини) додаються ────────────
def fig_gaussian_product():
    W, H = 780, 600
    f = [text(W / 2, 26, "Перемножити дзвони — це додати квадратичні вартості", size=15, bold=True)]

    x0px, x1px = 100, 700
    x0v, x1v = -4.0, 14.0
    def X(v): return x0px + (v - x0v) / (x1v - x0v) * (x1px - x0px)

    mu1, v1 = 2.0, 6.0     # джерело 1 — ширше (менш певне)
    mu2, v2 = 8.0, 3.0     # джерело 2 — вужче (певніше)
    s1, s2 = math.sqrt(v1), math.sqrt(v2)
    w1, w2 = 1.0 / v1, 1.0 / v2
    muF = (mu1 * w1 + mu2 * w2) / (w1 + w2)     # = 6.0
    vF = 1.0 / (w1 + w2)                        # = 2.0
    sF = math.sqrt(vF)
    xF = X(muF)
    r2pi = math.sqrt(2 * math.pi)

    # ── ВЕРХНЯ панель: густини (множаться) ──
    baseT = 250
    peakF = 1.0 / (sF * r2pi)
    SCT = 150.0 / peakF
    def YT(g): return baseT - g * SCT

    f.append(text(x0px, 54, "Густини: ПЕРЕМНОЖУЄМО", size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0px, x1px, baseT, label="x"))
    f.append(area(gauss(mu1, s1, x0v, x1v, X, YT), baseT, NEG, opacity=0.15, sw=2.2))
    f.append(area(gauss(mu2, s2, x0v, x1v, X, YT), baseT, POS, opacity=0.15, sw=2.2))
    f.append(area(gauss(muF, sF, x0v, x1v, X, YT), baseT, FIELD, opacity=0.30, sw=2.8))

    p1 = 1.0 / (s1 * r2pi); p2 = 1.0 / (s2 * r2pi)
    f.append(text(X(mu1), YT(p1) - 22, "джерело 1", size=10.5, color=NEG, bold=True))
    f.append(text(X(mu1), YT(p1) - 8, "μ₁=2, σ₁²=6", size=9.5, color=NEG))
    f.append(text(X(mu2), YT(p2) - 22, "джерело 2", size=10.5, color=POS, bold=True))
    f.append(text(X(mu2), YT(p2) - 8, "μ₂=8, σ₂²=3", size=9.5, color=POS))
    f.append(text(xF - 6, YT(peakF) - 20, "добуток", size=11, color=FIELD, bold=True, anchor="end"))
    f.append(text(xF - 6, YT(peakF) - 6, "σ̂²=2 — найвужчий", size=9.5, color=FIELD, anchor="end"))

    # ── НИЖНЯ панель: −ln густини = квадратична вартість (додається) ──
    baseB = 552
    SCB = 27.0
    CMAX = 7.6
    def YB(c): return baseB - min(c, CMAX) * SCB
    def J1(x): return (x - mu1) ** 2 / (2 * v1)
    def J2(x): return (x - mu2) ** 2 / (2 * v2)
    def S(x): return J1(x) + J2(x)

    f.append(text(x0px, 320, "−ln густини: ДОДАЄМО параболи вартості", size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0px, x1px, baseB, label="x"))

    def curve(fn):
        pts = []
        for i in range(361):
            v = x0v + (x1v - x0v) * i / 360.0
            c = fn(v)
            if c <= CMAX:
                pts.append((X(v), YB(c)))
        return pts
    f.append(polyline(curve(J1), NEG, sw=2.2))
    f.append(polyline(curve(J2), POS, sw=2.2))
    f.append(polyline(curve(S), FIELD, sw=3.0))

    # мінімуми парабол
    f.append(circle(X(mu1), YB(0), 3.6, fill=NEG, stroke=NEG, sw=0))
    f.append(circle(X(mu2), YB(0), 3.6, fill=POS, stroke=POS, sw=0))
    f.append(circle(xF, YB(S(muF)), 4.4, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(X(mu1), baseB + 20, "мін J₁ = μ₁", size=9.5, color=NEG, anchor="middle"))
    f.append(text(X(mu2), baseB + 20, "мін J₂ = μ₂", size=9.5, color=POS, anchor="middle"))

    # анотації суми (у порожньому верхньому-лівому куті нижньої панелі)
    f.append(text(X(-3.6), 356, "сума J₁+J₂ стрімкіша:", size=10.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(X(-3.6), 373, "кривини додаються", size=10.5, color=FIELD, anchor="start"))
    f.append(text(X(-3.6), 391, "1/σ̂² = 1/σ₁² + 1/σ₂²", size=11, color=INK, bold=True, anchor="start"))

    # спільна вертикаль x̂ крізь обидві панелі (пік добутку ↔ мінімум суми)
    f.append(line(xF, YT(peakF), xF, baseB, color=FIELD, sw=1.5, dash="5,5"))
    f.append(text(xF + 8, 302, "x̂ = 6 — мінімум суми", size=10.5, color=FIELD, bold=True, italic=True, anchor="start"))

    render(os.path.join(IMG, "gaussian-product.svg"), W, H, *f)


if __name__ == "__main__":
    fig_complementary_spectrum()
    fig_inverse_variance()
    fig_gain_convergence()
    fig_state_space_bias()
    fig_gaussian_product()
    print("OK: 5 figures ->", IMG)
