# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Практикум даташитів: BJT».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


def _legend_row(f, cx, y, color, label):
    f.append(rect(cx, y - 7, 16, 13, fill=color, stroke=color, sw=1, rx=2))
    f.append(text(cx + 22, y + 4, label, size=10.5, color=MUTED, anchor="start"))


def _row(f, x, y, name, color, fill, expl, val):
    """Один рядок-параметр: кольорова плашка з назвою + пояснення + умова."""
    f.append(rect(x, y, 128, 40, fill=fill, stroke=color, sw=1.6, rx=6))
    f.append(text(x + 64, y + 24, name, size=12.5, color=color, bold=True))
    fs = fit_font(expl, 250, 11)
    f.append(text(x + 140, y + 16, expl, size=fs, color=INK, anchor="start"))
    fs2 = fit_font(val, 250, 10.5)
    f.append(text(x + 140, y + 32, val, size=fs2, color=MUTED, anchor="start"))


# ── 1. Критичні рядки даташита BJT ───────────────────────────────────────────
def fig_rows():
    W, H = 720, 360
    f = [text(W / 2, 28, "Даташит BJT: рядки, що вирішують вибір", size=16, bold=True)]
    _legend_row(f, 56, 50, RED, "абсолютний максимум")
    _legend_row(f, 300, 50, GRN, "робоча межа")
    _legend_row(f, 520, 50, BLU, "параметр з умовою")
    x, y, dy = 44, 72, 44
    _row(f, x, y + 0 * dy, "Ic(max)", RED, "#fdecea",
         "найбільший струм колектора", "бери ≥ 2× до струму навантаження")
    _row(f, x, y + 1 * dy, "Vceo", RED, "#fdecea",
         "пробій колектор–емітер, база відкрита", "запас до шини + викиди")
    _row(f, x, y + 2 * dy, "Ptot", GRN, "#eafaf1",
         "розсіювана потужність при 25 °C", "падає з температурою (дератинг)")
    _row(f, x, y + 3 * dy, "hFE (β)", BLU, "#eaf0fd",
         "підсилення струму — діапазон, не число", "при заданих Ic і Vce; бери β(min)")
    _row(f, x, y + 4 * dy, "Vce(sat)", BLU, "#eaf0fd",
         "падіння на відкритому ключі", "при заданих Ic та Ib (forced β ≈ 10)")
    _row(f, x, y + 5 * dy, "fT, Cob", BLU, "#eaf0fd",
         "гранична частота й ємність колектора", "важать у швидкій комутації")
    render(os.path.join(IMG, "rows.svg"), W, H, *f)


# ── 2. β — це смуга, а не число ──────────────────────────────────────────────
def fig_beta_spread():
    W, H = 720, 360
    f = [text(W / 2, 26, "hFE (β) — смуга значень, а не одне число", size=16, bold=True)]

    # ЛІВА панель: три класи-біни (BC547 A/B/C) як вертикальні діапазони
    L, T, PW, PH = 48, 60, 300, 250
    f.append(rect(L, T, PW, PH, fill=BG, stroke="#c9d3dc", sw=1.3, rx=8))
    f.append(text(L + PW / 2, T + 20, "Класи за підсиленням (BC547 A/B/C)", size=11.5, bold=True))
    # вісь β зліва: 0..900 у px
    ax = L + 56
    ay0, ay1 = T + 230, T + 42        # низ / верх осі
    bmin, bmax = 0, 900

    def by(v):
        return ay0 + (ay1 - ay0) * (v - bmin) / (bmax - bmin)
    f.append(line(ax, ay0, ax, ay1, color=MUTED, sw=1.3))
    for v in (0, 200, 400, 600, 800):
        f.append(line(ax - 4, by(v), ax, by(v), color=MUTED, sw=1))
        f.append(text(ax - 8, by(v) + 4, str(v), size=9.5, color=MUTED, anchor="end"))
    f.append(text(ax - 30, T + 130, "β", size=12, color=INK, bold=True))
    bins = [("A", 110, 220, "#eaf0fd", BLU),
            ("B", 200, 450, "#eafaf1", GRN),
            ("C", 420, 800, "#fdf1dc", "#b8860b")]
    bx = ax + 28
    for i, (nm, lo, hi, fill, col) in enumerate(bins):
        cx = bx + i * 64
        f.append(rect(cx, by(hi), 40, by(lo) - by(hi), fill=fill, stroke=col, sw=1.7, rx=4))
        f.append(text(cx + 20, by(hi) - 6, nm, size=12, color=col, bold=True))
        f.append(text(cx + 20, by(lo) + 13, "%d" % lo, size=8.5, color=MUTED))
        f.append(text(cx + 20, by(hi) + 0, "%d" % hi, size=8.5, color=MUTED))
    f.append(text(L + PW / 2, T + PH - 8, "один номер — діапазон у 2-3 рази; клас звужує",
                  size=10, color=MUTED, italic=True))

    # ПРАВА панель: β vs Ic — горб
    R, RW = L + PW + 24, 300
    f.append(rect(R, T, RW, PH, fill=BG, stroke="#c9d3dc", sw=1.3, rx=8))
    f.append(text(R + RW / 2, T + 20, "β залежить від робочої точки", size=11.5, bold=True))
    gx0, gx1 = R + 46, R + RW - 24
    gy0, gy1 = T + 210, T + 42
    f.append(line(gx0, gy0, gx1, gy0, color=MUTED, sw=1.3))   # вісь Ic
    f.append(line(gx0, gy0, gx0, gy1, color=MUTED, sw=1.3))   # вісь β
    f.append(text((gx0 + gx1) / 2, gy0 + 26, "Ic (лог. шкала) →", size=10, color=MUTED))
    f.append(text(gx0 - 12, gy1 - 6, "β", size=11, color=INK, bold=True))
    # горб: низько на малих і великих струмах, максимум посередині
    import math
    pts = []
    for k in range(0, 101):
        t = k / 100.0
        xx = gx0 + (gx1 - gx0) * t
        # дзвін зі зсувом піка трохи правіше центру
        bump = math.exp(-((t - 0.55) ** 2) / 0.06)
        yy = gy0 - (gy0 - gy1) * (0.18 + 0.80 * bump)
        pts.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), NEG))
    # робоча зона-вікно
    wx0 = gx0 + (gx1 - gx0) * 0.40
    wx1 = gx0 + (gx1 - gx0) * 0.72
    f.append(rect(wx0, gy1 - 4, wx1 - wx0, gy0 - gy1 + 4, fill="#eafaf1", stroke="none", sw=0, rx=3))
    f.append(text((wx0 + wx1) / 2, gy1 + 8, "робоча зона", size=9.5, color=GRN, bold=True))
    f.append(text(gx0 + 30, gy0 - 6, "малий Ic:", size=9, color=MUTED, anchor="start"))
    f.append(text(gx0 + 30, gy0 + 4, "β провисає", size=9, color=MUTED, anchor="start"))
    f.append(text(gx1 - 4, gy0 - 6, "великий Ic:", size=9, color=MUTED, anchor="end"))
    f.append(text(gx1 - 4, gy0 + 4, "β падає", size=9, color=MUTED, anchor="end"))
    render(os.path.join(IMG, "beta-spread.svg"), W, H, *f)


# ── 3. Vce(sat) дають за forced β — читай умову ───────────────────────────────
def fig_vcesat():
    W, H = 720, 300
    f = [text(W / 2, 26, "Vce(sat): число важить лише з умовою Ic та Ib", size=16, bold=True)]

    # рядок даташита як приклад
    b, bw, bh = textbox(W / 2, 70, "Vce(sat) = 0.3 В (max)   при   Ic = 150 мА,  Ib = 15 мА",
                        size=13, fill="#eaf0fd", stroke=BLU, bold=True)
    f.append(b)
    f.append(text(W / 2, 70 + bh / 2 + 18, "Ic / Ib = 150 / 15 = 10  →  це «forced β = 10»",
                  size=11.5, color=MUTED, italic=True))

    # дві колонки: дали досить бази (насичення) vs замало (активний)
    colw, top = 320, 130
    lx, rx = 40, 40 + colw + 20
    f.append(rect(lx, top, colw, 140, fill="#eafaf1", stroke=GRN, sw=1.8, rx=10))
    f.append(rect(rx, top, colw, 140, fill="#fdecea", stroke=RED, sw=1.8, rx=10))
    f.append(text(lx + colw / 2, top + 24, "Дав Ib за умовою (forced β 10)", size=12, bold=True, color=GRN))
    f.append(text(rx + colw / 2, top + 24, "Дав менше Ib (взяв типове β)", size=12, bold=True, color=RED))
    left = ["ключ у глибокому насиченні",
            "Vce(sat) ≈ табличні 0.3 В",
            "грійка P = 0.3 · Ic — мала"]
    right = ["ключ застряг в активному",
            "Vce куди більша за 0.3 В",
            "грійка в рази більша — перегрів"]
    for i, s in enumerate(left):
        f.append(text(lx + 18, top + 52 + i * 28, "• " + s, size=11, color=INK, anchor="start"))
    for i, s in enumerate(right):
        f.append(text(rx + 18, top + 52 + i * 28, "• " + s, size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, "vcesat.svg"), W, H, *f)


# ── 4. SOA: другий пробій вигризає кут із гіперболи потужності ────────────────
def fig_soa():
    W, H = 700, 380
    f = [text(W / 2, 26, "Безпечна робоча зона (SOA): межа, якої немає в MOSFET так само", size=15, bold=True)]
    # осі (лог-лог за духом)
    ox0, oy0 = 90, 300        # початок
    ox1, oy1 = 600, 70
    f.append(line(ox0, oy0, ox1, oy0, color=INK, sw=1.6))   # Vce →
    f.append(line(ox0, oy0, ox0, oy1, color=INK, sw=1.6))   # Ic ↑
    f.append(text((ox0 + ox1) / 2, oy0 + 30, "Vce (лог) →", size=11.5, color=INK, bold=True))
    f.append(text(ox0 - 50, (oy0 + oy1) / 2, "Ic", size=12, color=INK, bold=True))
    f.append(text(ox0 - 50, (oy0 + oy1) / 2 + 16, "(лог)", size=9.5, color=MUTED))

    import math
    XL, XR = ox0 + 6, ox1 - 6
    YB, YT = oy0 - 6, oy1 + 6

    def X(t):
        return XL + (XR - XL) * t

    def Y(t):
        return YB - (YB - YT) * t
    # 1) стеля Ic(max) — горизонталь зверху-зліва
    icmax_t = 0.86
    f.append(line(X(0.04), Y(icmax_t), X(0.34), Y(icmax_t), color=RED, sw=2.4))
    # 2) гіпербола сталої потужності P=Vce·Ic  → на лог-лог пряма з нахилом -1
    hyp = []
    for k in range(0, 101):
        t = 0.20 + 0.72 * k / 100.0      # по Vce
        ic = icmax_t - 1.0 * (t - 0.20)  # нахил -1 у лог-лог
        if ic < 0.06:
            break
        hyp.append((t, ic))
    poly = " ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in hyp)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>'
             % (poly, MUTED))
    f.append(text(X(0.62), Y(0.62) - 10, "гіпербола P = Vce·Ic", size=10.5, color=MUTED, italic=True))
    # 3) ЗРІЗ другого пробою — крутіший спад правіше (вигризений кут)
    sb = []
    for k in range(0, 101):
        t = 0.55 + 0.40 * k / 100.0
        ic = (icmax_t - 1.0 * (0.55 - 0.20)) - 2.0 * (t - 0.55)  # крутіший нахил
        if ic < 0.06:
            break
        sb.append((t, ic))
    polysb = " ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in sb)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (polysb, RED))
    # 4) стеля Vceo — вертикаль праворуч
    f.append(line(X(0.92), Y(0.06), X(0.92), Y(0.34), color=RED, sw=2.4))
    # суцільна межа SOA (товста) по верхньому контуру до зламу
    border = []
    border.append((0.04, icmax_t))
    border.append((0.34, icmax_t))
    # відрізок гіперболи до початку другого пробою
    for t, ic in hyp:
        if 0.34 <= t <= 0.55:
            border.append((t, ic))
    polyb = " ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in border)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (polyb, RED))
    # підписи меж
    f.append(text(X(0.18), Y(icmax_t) - 8, "Ic(max)", size=10.5, color=RED, bold=True))
    f.append(text(X(0.92) + 4, Y(0.20), "Vceo", size=10.5, color=RED, bold=True, anchor="start"))
    # позначка зламу другого пробою
    bx, byy = X(0.66), Y(0.40)
    f.append(text(bx, byy, "другий пробій", size=11, color=RED, bold=True, anchor="start"))
    f.append(text(bx, byy + 15, "(зрізає кут більше,", size=9.5, color=RED, anchor="start"))
    f.append(text(bx, byy + 28, "ніж проста гіпербола)", size=9.5, color=RED, anchor="start"))
    # зелена «можна» зона-підпис
    f.append(text(X(0.16), Y(0.30), "можна", size=12, color=GRN, bold=True))
    render(os.path.join(IMG, "soa.svg"), W, H, *f)


# ── 5. Дератинг: пряма Ptot(T), нахил = −1/Rθ ────────────────────────────────
def fig_derating():
    import math
    W, H = 720, 380
    f = [text(W / 2, 26, "Крива дератингу — це пряма з нахилом −1/Rθ", size=16, bold=True)]
    # осі
    ox0, oy0 = 96, 300
    ox1, oy1 = 620, 72
    f.append(line(ox0, oy0, ox1, oy0, color=INK, sw=1.6))   # T →
    f.append(line(ox0, oy0, ox0, oy1, color=INK, sw=1.6))   # P ↑
    f.append(text((ox0 + ox1) / 2, oy0 + 34, "температура корпусу T (°C) →", size=11.5, color=INK, bold=True))
    f.append(text(ox0 - 66, (oy0 + oy1) / 2 - 6, "дозволена", size=10.5, color=INK, bold=True, anchor="start"))
    f.append(text(ox0 - 66, (oy0 + oy1) / 2 + 8, "Ptot (мВт)", size=10.5, color=INK, bold=True, anchor="start"))
    # шкала T: 25..150
    Tmin, Tmax = 25.0, 150.0
    Pmax = 625.0

    def X(T):
        return ox0 + (ox1 - ox0) * (T - Tmin) / (Tmax - Tmin)

    def Y(P):
        return oy0 - (oy0 - oy1) * (P / Pmax)
    for T in (25, 50, 75, 100, 125, 150):
        f.append(line(X(T), oy0, X(T), oy0 + 5, color=MUTED, sw=1))
        f.append(text(X(T), oy0 + 18, str(T), size=9.5, color=MUTED))
    for P in (0, 125, 250, 375, 500, 625):
        f.append(line(ox0 - 5, Y(P), ox0, Y(P), color=MUTED, sw=1))
        f.append(text(ox0 - 9, Y(P) + 4, str(P), size=9, color=MUTED, anchor="end"))
    # пряма дератингу від (25, 625) до (150, 0)
    f.append(line(X(25), Y(625), X(150), Y(0), color=NEG, sw=2.6))
    f.append(text(X(30), Y(625) - 10, "625 мВт при 25 °C", size=10.5, color=NEG, bold=True, anchor="start"))
    f.append(text(X(150) - 4, Y(0) - 10, "0 при Tj(max)=150 °C", size=10, color=NEG, anchor="end"))
    # робоча точка: T=85 °C → P = 5·(150−85) = 325 мВт
    Tw, Pw = 85.0, 325.0
    f.append(line(X(Tw), oy0, X(Tw), Y(Pw), color=FIELD, sw=1.4, dash="4 3"))
    f.append(line(ox0, Y(Pw), X(Tw), Y(Pw), color=FIELD, sw=1.4, dash="4 3"))
    f.append(circle(X(Tw), Y(Pw), 5, fill=FIELD, stroke=BG, sw=1.6))
    b, bw, bh = textbox(X(Tw) + 92, Y(Pw) - 24,
                        "твоя плата: T=85 °C\n→ лише 325 мВт,\nа не 625",
                        size=10.5, fill="#eafaf1", stroke=FIELD, color=INK, bold=False)
    f.append(b)
    # нахил = −1/Rθ
    f.append(text(X(110), Y(180) + 4, "нахил = −5 мВт/°C = −1/Rθ", size=10.5, color=MUTED, italic=True, anchor="start"))
    render(os.path.join(IMG, "derating.svg"), W, H, *f)


# ── 6. Тепловий опір: перехід → корпус → радіатор → повітря (послідовні Rθ) ────
def fig_thermal_stack():
    W, H = 720, 340
    f = [text(W / 2, 26, "Тепловий шлях — послідовні опори, Rθ додаються", size=16, bold=True)]
    # ланцюг «резисторів» зліва направо
    xs = 70
    boxw, gap = 118, 42
    y = 120
    stages = [
        ("кристал\n(перехід)", "Tj", "#fdecea", POS),
        ("корпус", "Tc", "#fdf1dc", "#b8860b"),
        ("радіатор", "Ts", "#eaf0fd", NEG),
        ("повітря", "Ta", "#eafaf1", FIELD),
    ]
    res = [("Rθjc", "перехід→корпус"), ("Rθcs", "корпус→радіатор"), ("Rθsa", "радіатор→повітря")]
    cx = []
    for i, (nm, node, fill, col) in enumerate(stages):
        x = xs + i * (boxw + gap)
        cx.append(x + boxw / 2)
        f.append(fitbox(x, y, boxw, 56, nm, size=12, fill=fill, stroke=col, sw=1.8, color=col, bold=True))
        f.append(text(x + boxw / 2, y - 10, node, size=12, color=col, bold=True))
    # опори між вузлами: з'єднувальна лінія НИЖЧЕ рівня плашки-опору,
    # сама плашка Rθ підведена вгору (щоб лінія не різала напис)
    for i, (rn, rl) in enumerate(res):
        x0 = xs + i * (boxw + gap) + boxw
        xm = x0 + gap / 2
        f.append(line(x0, y + 40, x0 + gap, y + 40, color=INK, sw=1.6))
        rb, rbw, rbh = textbox(xm, y + 18, rn, size=11, fill=BG, stroke=INK, color=INK, bold=True)
        f.append(rb)
        f.append(text(xm, y + 76, rl, size=9, color=MUTED))
    # стрілка теплового потоку зверху
    f.append(arrow(cx[0], y - 34, cx[-1], y - 34, color=MUTED, sw=1.6))
    f.append(text((cx[0] + cx[-1]) / 2, y - 40, "потік тепла P →", size=10.5, color=MUTED, italic=True))
    # формула під ланцюгом
    b, bw, bh = textbox(W / 2, 250,
                        "Tj − Ta = P · (Rθjc + Rθcs + Rθsa)      →      P(доз) = (Tj(max) − Ta) / ΣRθ",
                        size=12.5, fill=FILL, stroke=INK, color=INK, bold=True)
    f.append(b)
    f.append(text(W / 2, 296, "більший радіатор ⇒ менший Rθsa ⇒ менша сума ⇒ більша дозволена потужність",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "thermal-stack.svg"), W, H, *f)


# ── 7. SOA з робочою точкою і запасами до кожної межі ────────────────────────
def fig_soa_point():
    import math
    W, H = 720, 400
    f = [text(W / 2, 24, "Запас у SOA рахують до НАЙБЛИЖЧОЇ межі, не до потужності", size=15, bold=True)]
    ox0, oy0 = 96, 320
    ox1, oy1 = 620, 72
    f.append(line(ox0, oy0, ox1, oy0, color=INK, sw=1.6))
    f.append(line(ox0, oy0, ox0, oy1, color=INK, sw=1.6))
    f.append(text((ox0 + ox1) / 2, oy0 + 30, "Vce (лог) →", size=11.5, color=INK, bold=True))
    f.append(text(ox0 - 52, (oy0 + oy1) / 2, "Ic (лог) ↑", size=11.5, color=INK, bold=True, anchor="start"))
    XL, XR = ox0 + 6, ox1 - 6
    YB, YT = oy0 - 6, oy1 + 6

    def X(t):
        return XL + (XR - XL) * t

    def Y(t):
        return YB - (YB - YT) * t
    # межі: Ic(max) горизонталь
    icmax_t = 0.88
    f.append(line(X(0.04), Y(icmax_t), X(0.30), Y(icmax_t), color=RED, sw=2.4))
    f.append(text(X(0.16), Y(icmax_t) - 8, "Ic(max)", size=10.5, color=RED, bold=True))
    # гіпербола P (нахил -1), пунктир
    hyp = []
    for k in range(0, 101):
        t = 0.16 + 0.78 * k / 100.0
        ic = icmax_t - 1.0 * (t - 0.16)
        if ic < 0.05:
            break
        hyp.append((t, ic))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6 4"/>'
             % (" ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in hyp), MUTED))
    f.append(text(X(0.52), Y(0.60) - 8, "P = Vce·Ic (гіпербола)", size=10, color=MUTED, italic=True))
    # другий пробій — крутіший зріз праворуч
    sb = []
    for k in range(0, 101):
        t = 0.52 + 0.44 * k / 100.0
        ic = (icmax_t - 1.0 * (0.52 - 0.16)) - 2.1 * (t - 0.52)
        if ic < 0.05:
            break
        sb.append((t, ic))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in sb), RED))
    # суцільна межа SOA до зламу
    border = [(0.04, icmax_t), (0.30, icmax_t)]
    for t, ic in hyp:
        if 0.30 <= t <= 0.52:
            border.append((t, ic))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (X(t), Y(ic)) for t, ic in border), RED))
    # Vceo вертикаль
    f.append(line(X(0.93), Y(0.05), X(0.93), Y(0.30), color=RED, sw=2.4))
    f.append(text(X(0.93) + 4, Y(0.18), "Vceo", size=10.5, color=RED, bold=True, anchor="start"))
    f.append(text(X(0.70), Y(0.42), "другий пробій", size=10.5, color=RED, bold=True, anchor="start"))
    # РОБОЧА ТОЧКА на високій напрузі, під гіперболою, але близько до зрізу пробою
    wt, wi = 0.63, 0.30
    f.append(circle(X(wt), Y(wi), 6, fill=FIELD, stroke=BG, sw=1.8))
    f.append(text(X(wt) - 8, Y(wi) + 4, "робоча точка", size=10.5, color=FIELD, bold=True, anchor="end"))
    # запас ВГОРУ до гіперболи (виглядає великий) — вертикаль ліворуч від точки,
    # підпис ще лівіше, щоб лінія не різала напис
    ic_hyp = icmax_t - 1.0 * (wt - 0.16)
    f.append(line(X(wt), Y(wi), X(wt), Y(ic_hyp), color=MUTED, sw=1.3, dash="3 3"))
    f.append(text(X(wt) - 6, (Y(wi) + Y(ic_hyp)) / 2, "запас по P", size=9, color=MUTED, anchor="end"))
    # запас управо до другого пробою (близько!) — по горизонталі до кривої sb на рівні wi
    # sb: ic = (icmax_t-1.0*0.36) - 2.1*(t-0.52); розв'язати t при ic=wi
    t_sb = 0.52 + ((icmax_t - 0.36) - wi) / 2.1
    f.append(line(X(wt), Y(wi), X(t_sb), Y(wi), color=POS, sw=1.6))
    # підпис справжнього запасу — праворуч від вертикалі (anchor start за X(wt)),
    # у два рядки під горизонтальною лінією, щоб її не перетнути
    f.append(text(X(wt) + 8, Y(wi) + 16, "справжній запас", size=9.5, color=POS, bold=True, anchor="start"))
    f.append(text(X(wt) + 8, Y(wi) + 29, "(до пробою — мізерний)", size=9, color=POS, anchor="start"))
    # зелена зона підпис
    f.append(text(X(0.12), Y(0.28), "можна", size=12, color=GRN, bold=True))
    render(os.path.join(IMG, "soa-margin.svg"), W, H, *f)


# ── 8. [hist] Родовід желейних NPN: від металу до дешевого пластику ───────────
def fig_jellybean_timeline():
    W, H = 720, 320
    f = [text(W / 2, 26, "Родовід желейних NPN: дешевший корпус — ширше поширення", size=15, bold=True)]
    # горизонтальна вісь часу
    ax0, ax1, ay = 70, 650, 250
    f.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.4))
    f.append(arrow(ax1 - 2, ay, ax1 + 8, ay, color=MUTED, sw=1.4))
    f.append(text(ax1 + 4, ay + 16, "час", size=10, color=MUTED, anchor="end"))
    # чотири віхи; y-висота плашки кодує «дешевизну/поширеність» (нижче = дешевше/ширше)
    nodes = [
        (0.06, "2N2222", "1962 · TO-18", "метал\n(бляшанка)", "#eaf0fd", NEG, 96),
        (0.34, "2N2222A", "1964 · TO-18", "поліпшений\nметал", "#eaf0fd", NEG, 118),
        (0.62, "PN2222", "TO-92", "той самий кристал\nу пластику;\nвиводи E/C\nдзеркальні!", "#fdf1dc", "#b8860b", 150),
        (0.90, "2N3904", "сер. 1960-х · TO-92", "від народження\nпластик —\nнайдешевший", "#eafaf1", FIELD, 182),
    ]
    for t, nm, sub, note, fill, col, drop in nodes:
        x = ax0 + (ax1 - ax0) * t
        f.append(line(x, ay, x, ay - 6, color=MUTED, sw=1.2))
        # плашка над віссю
        by = ay - drop
        f.append(fitbox(x - 66, by, 132, drop - 30, note, size=10, fill=fill, stroke=col, sw=1.7, color=INK))
        f.append(text(x, by - 8, nm, size=13, color=col, bold=True))
        f.append(text(x, ay + 18, sub, size=9.5, color=MUTED))
    # підпис-стрілка «дешевшає» вниз ліворуч
    f.append(text(ax0 - 8, ay - 150, "дешевшає", size=10, color=MUTED, italic=True, anchor="start"))
    f.append(text(ax0 - 8, ay - 137, "ширшає", size=10, color=MUTED, italic=True, anchor="start"))
    f.append(arrow(ax0 - 2, ay - 128, ax0 - 2, ay - 40, color=MUTED, sw=1.3))
    render(os.path.join(IMG, "jellybean-timeline.svg"), W, H, *f)


# ── 9. [hist] Дві культури імен: JEDEC (порядковий) vs Pro Electron (значущий) ─
def fig_naming_systems():
    W, H = 720, 360
    f = [text(W / 2, 26, "Дві культури імен транзистора", size=16, bold=True)]
    colw, top = 320, 56
    lx, rx = 40, 40 + colw + 20
    # ЛІВА: JEDEC 2N2222 — порядковий номер
    f.append(rect(lx, top, colw, 268, fill="#eaf0fd", stroke=NEG, sw=1.7, rx=10))
    f.append(text(lx + colw / 2, top + 24, "JEDEC (США): 2N2222", size=13.5, bold=True, color=NEG))
    f.append(text(lx + colw / 2, top + 44, "ім'я = квиток у черзі реєстрації", size=10.5, color=MUTED, italic=True))
    # розбір «2N2222»
    f.append(text(lx + 40, top + 92, "2N", size=20, bold=True, color=INK, anchor="start"))
    f.append(text(lx + 96, top + 92, "2222", size=20, bold=True, color=MUTED, anchor="start"))
    f.append(text(lx + 18, top + 128, "2N — це «транзистор»", size=11, color=INK, anchor="start"))
    f.append(text(lx + 18, top + 150, "2222 — просто № за порядком", size=11, color=INK, anchor="start"))
    b1, _, _ = textbox(lx + colw / 2, top + 208,
                       "саме ім'я не каже НІЧОГО\nпро матеріал, функцію, β —\nусе лише в таблиці даташита",
                       size=10.5, fill=BG, stroke=NEG, color=INK)
    f.append(b1)
    # ПРАВА: Pro Electron BC547C — значущий код
    f.append(rect(rx, top, colw, 268, fill="#eafaf1", stroke=FIELD, sw=1.7, rx=10))
    f.append(text(rx + colw / 2, top + 24, "Pro Electron (Європа): BC547C", size=12.5, bold=True, color=FIELD))
    f.append(text(rx + colw / 2, top + 44, "ім'я = стиснутий рядок даташита", size=10.5, color=MUTED, italic=True))
    # розбір по літерах з підписами
    parts = [("B", "кремній", "#b8860b"),
             ("C", "малосигнальний", NEG),
             ("547", "модель", MUTED),
             ("C", "клас β≥420", POS)]
    px = rx + 30
    baseY = top + 92
    for ch, lab, col in parts:
        w = text_width(ch, 20, True) + 10
        f.append(text(px, baseY, ch, size=20, bold=True, color=col, anchor="start"))
        px += w + 4
    # підписи-виноски під кодом
    labs = [("B → кремній (A = германій)", "#b8860b"),
            ("C → малопотужний малосигнальний", NEG),
            ("547 → номер моделі", MUTED),
            ("C → клас підсилення: β ≥ 420", POS)]
    for i, (s, col) in enumerate(labs):
        f.append(text(rx + 18, top + 132 + i * 24, "• " + s, size=10.5, color=col, anchor="start", bold=True))
    b2, _, _ = textbox(rx + colw / 2, top + 244,
                       "глянув на ім'я — уже знаєш тип і гарантію β",
                       size=10, fill=BG, stroke=FIELD, color=INK)
    f.append(b2)
    render(os.path.join(IMG, "naming-systems.svg"), W, H, *f)


if __name__ == "__main__":
    fig_rows()
    fig_beta_spread()
    fig_vcesat()
    fig_soa()
    fig_derating()
    fig_thermal_stack()
    fig_soa_point()
    fig_jellybean_timeline()
    fig_naming_systems()
    print("OK: 9 figures ->", IMG)
