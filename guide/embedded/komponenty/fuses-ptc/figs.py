# -*- coding: utf-8 -*-
"""Фігури детальної теми «Запобіжники». Запуск: python figs.py  → ./img/*.svg
Ідуть ГЛИБШЕ за базові: два режими плавлення (адіабата ↔ рівновага),
відсічка струму, електротеплова робоча точка PTC, зсув утримання від температури.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фіг.1 — два режими на кривій t(I): адіабата (I²t=const) ↔ рівновага (Preece) ──
def fig_two_regimes():
    W, H = 760, 470
    x0, y0 = 96, 62
    gw, gh = 560, 330
    xb, yb = x0, y0 + gh

    # логарифмічні осі: X = lg(I/In), Y = lg(t)
    # I від In (×1) до ×30; t від 1 мс до 100 с
    imin, imax = 1.0, 30.0
    tmin, tmax = 1e-3, 1e2
    def X(i): return xb + (math.log10(i) - math.log10(imin)) / (math.log10(imax) - math.log10(imin)) * gw
    def Y(t): return yb - (math.log10(t) - math.log10(tmin)) / (math.log10(tmax) - math.log10(tmin)) * gh

    frs = []
    # осі
    frs.append(line(xb, y0, xb, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 48, "струм / номінал  (log)", size=13, color=MUTED))
    frs.append(text(x0 - 62, y0 + gh / 2, "час до розриву", size=13, color=MUTED, anchor="middle"))
    frs.append(text(x0 - 62, y0 + gh / 2 + 17, "(log)", size=13, color=MUTED, anchor="middle"))

    # сітка + підписи по X
    for i in (1, 2, 3, 5, 10, 20, 30):
        xx = X(i)
        frs.append(line(xx, y0, xx, yb, color="#eef1f4", sw=1))
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, ("%d×" % i), size=11, color=INK))
    # сітка + підписи по Y
    for t, lab in ((1e-3, "1 мс"), (1e-2, "10 мс"), (1e-1, "0.1 с"), (1e0, "1 с"), (1e1, "10 с"), (1e2, "100 с")):
        yy = Y(t)
        frs.append(line(xb, yy, xb + gw, yy, color="#eef1f4", sw=1))
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.5))
        frs.append(text(xb - 10, yy + 4, lab, size=11, color=INK, anchor="end"))

    # Адіабатна гілка: I²·t = const  →  t = K / I²  →  lg t = lg K - 2 lg I  (нахил -2)
    # підберемо так, щоб при I=10× було t≈2 мс (типова відсічка короткого)
    K = (10.0 ** 2) * 2e-3
    pts = []
    i = 4.0
    while i <= imax:
        t = K / (i * i)
        if t <= tmax and t >= tmin:
            pts.append("%.1f,%.1f" % (X(i), Y(t)))
        i *= 1.03
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), POS))

    # Гілка рівноваги (Preece): при малому надлишку час злітає — крива задирається вертикально
    # асимптота біля I≈1.35× (умовний поріг сталого плавлення)
    Ia = 1.35
    pts2 = []
    i = 1.9
    while i >= Ia + 0.02:
        # емпірична форма: t росте як 1/(i-Ia) — вертикальна асимптота
        t = 0.9 / (i - Ia) ** 1.7
        if t <= tmax and t >= 3e-3:
            pts2.append("%.1f,%.1f" % (X(i), Y(t)))
        i -= 0.02
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts2), NEG))

    # з'єднати коліном (перехідна зона) пунктиром
    frs.append(line(X(4.0), Y(K / 16.0), X(1.9), Y(0.9 / (1.9 - Ia) ** 1.7), color=MUTED, sw=2, dash="5 5"))

    # вертикальна асимптота In-порогу
    frs.append(line(X(Ia), y0, X(Ia), yb, color=NEG, sw=1.3, dash="3 4"))

    # підписи гілок
    b1 = fitbox(X(9), Y(2e-2), 232, 46, "адіабата (швидко):\nI²·t = const  →  нахил −2",
                size=12, fill="#fdecea", stroke=POS, color=POS); frs.append(b1)
    b2 = fitbox(X(1.42), Y(6.0), 232, 46, "рівновага (повільно):\nасимптота Preece I ≈ C·d^1.5",
                size=12, fill="#eaf0fd", stroke=NEG, color=NEG); frs.append(b2)
    b3 = fitbox(X(3.4), Y(0.25), 150, 40, "коліно:\nтепло почало\nтекти назовні",
                size=11, fill=FILL, stroke=MUTED, color=MUTED); frs.append(b3)

    render(os.path.join(IMG, "two-regimes.svg"), W, H, *frs,
           title="Дві фізики одного плавлення: адіабата коротко ↔ рівновага довго")


# ── Фіг.2 — струмовідсічка: очікуваний струм короткого ↔ пропущений пік ──────
def fig_let_through():
    W, H = 760, 430
    x0, y0 = 80, 70
    gw, gh = 600, 280
    xb = x0
    axis_y = y0 + gh / 2          # нульова лінія (змінний струм)

    frs = []
    # осі
    frs.append(line(xb, y0, xb, y0 + gh, color=INK, sw=2))
    frs.append(line(xb, axis_y, xb + gw, axis_y, color=INK, sw=1.6))
    frs.append(text(xb + gw / 2, y0 + gh + 40, "час (перший півперіод аварії)", size=13, color=MUTED))
    frs.append(text(x0 - 50, y0 + gh / 2, "струм", size=13, color=MUTED, anchor="middle"))

    A = gh / 2 - 12               # амплітуда очікуваного струму
    def sy(v): return axis_y - v  # v у частках амплітуди (0..A)

    # очікуваний струм короткого (prospective): повна синусоїда, якби нічого не рвало
    pts = []
    n = 240
    for k in range(n + 1):
        t = k / n
        x = xb + t * gw
        v = A * math.sin(math.pi * t)      # перший додатний півхвиля
        pts.append("%.1f,%.1f" % (x, sy(v)))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 5"/>' % (" ".join(pts), MUTED))

    # відсічка: запобіжник рве на піку-let-through (частка ~0.42 амплітуди), далі струм зникає
    clip = 0.42
    tcut = math.asin(clip) / math.pi        # момент, коли синус досяг рівня clip
    # let-through крива: слідує синусу до tcut, тоді круто падає до 0 (дуга гасне)
    pts2 = []
    k = 0
    while True:
        t = k / n
        if t > tcut:
            break
        x = xb + t * gw
        v = A * math.sin(math.pi * t)
        pts2.append("%.1f,%.1f" % (x, sy(v)))
        k += 1
    # спад до нуля
    xcut = xb + tcut * gw
    pts2.append("%.1f,%.1f" % (xcut, sy(A * clip)))
    pts2.append("%.1f,%.1f" % (xcut + 26, sy(0)))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts2), POS))

    # заливка I²t «пропущеної енергії» під let-through
    fill_pts = ["%.1f,%.1f" % (xb, sy(0))]
    k = 0
    while True:
        t = k / n
        if t > tcut:
            break
        x = xb + t * gw
        v = A * math.sin(math.pi * t)
        fill_pts.append("%.1f,%.1f" % (x, sy(v)))
        k += 1
    fill_pts.append("%.1f,%.1f" % (xcut, sy(0)))
    frs.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.75"/>' % " ".join(fill_pts))

    # рівень піка-let-through + очікуваного піка
    frs.append(line(xb, sy(A), xb + gw, sy(A), color=MUTED, sw=1, dash="3 4"))
    frs.append(line(xb, sy(A * clip), xcut, sy(A * clip), color=POS, sw=1, dash="3 4"))
    frs.append(text(xb + gw - 4, sy(A) - 6, "очікуваний пік короткого (I_prosp)", size=11, color=MUTED, anchor="end"))
    frs.append(text(xcut + 34, sy(A * clip) + 4, "пропущений пік (I_let-through)", size=11, color=POS, anchor="start"))

    b = fitbox(xb + 16, sy(A * clip) + 26, 150, 40, "площа = I²t,\nщо проскочила", size=11,
               fill="none", stroke=POS, color=POS); frs.append(b)

    render(os.path.join(IMG, "let-through.svg"), W, H, *frs,
           title="Струмовідсічка: запобіжник рве ДО піка, обрізаючи I²t")


# ── Фіг.3 — електротеплова робоча точка PTC: генерація I²R(T) ↔ відведення ────
def fig_ptc_balance():
    W, H = 760, 470
    x0, y0 = 92, 64
    gw, gh = 570, 330
    xb, yb = x0, y0 + gh

    Ta = 25.0
    Tmax = 200.0
    Pmax = 1.0            # умовна шкала потужності (норм.)
    def X(T): return xb + (T - Ta) / (Tmax - Ta) * gw
    def Y(P): return yb - P / Pmax * gh

    frs = []
    frs.append(line(xb, y0, xb, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 46, "температура тіла PTC, °C", size=13, color=MUTED))
    frs.append(text(x0 - 60, y0 + gh / 2, "потужність", size=13, color=MUTED, anchor="middle"))
    frs.append(text(x0 - 60, y0 + gh / 2 + 17, "(норм.)", size=13, color=MUTED, anchor="middle"))

    for T in (25, 75, 125, 175):
        xx = X(T)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, "%d" % T, size=11, color=INK))

    # R(T): майже плаский до Ts≈120, тоді стрибок у тисячі разів; беремо R(T) для генерації
    Ts = 120.0
    def Rrel(T):
        # плавний перехід «сигмоїдою» від 1 до ~1000 біля Ts
        return 1.0 + 999.0 / (1.0 + math.exp(-(T - Ts) / 6.0))

    # Крива відведення: P_dis = (T - Ta)/Rθ  → пряма.
    def dissip(T): return (T - Ta) / (Tmax - Ta) * 0.92
    frs.append(line(X(Ta), Y(dissip(Ta)), X(Tmax), Y(dissip(Tmax)), color=NEG, sw=3))
    frs.append(text(X(Tmax) - 4, Y(dissip(Tmax)) - 8, "відведення  P = (T−Ta)/Rθ", size=12, color=NEG, anchor="end"))

    # Криві генерації P_gen ~ I²·R(T). Холодна гілка дуже низька, біля Ts різко злітає.
    # утримання: насичення нижче стелі прямої → лишається ЛИШЕ холодний перетин у полі.
    # спрацювання: крива вилітає вгору за поле → лишається ЛИШЕ гарячий перетин.
    def gen(I2, T, cap): return min(I2 * Rrel(T) / 1400.0, cap)
    def gen_curve(I2, color, cap):
        pts = []
        T = Ta
        while T <= Tmax:
            pts.append("%.1f,%.1f" % (X(T), Y(gen(I2, T, cap))))
            T += 1.0
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), color)

    def cross_T(I2, cap):
        prev = None; out = []
        T = Ta
        while T <= Tmax:
            d = gen(I2, T, cap) - dissip(T)
            if prev is not None and (prev < 0) != (d < 0):
                out.append(T)
            prev = d; T += 0.5
        return out

    # струм утримання: генерація нижча за відведення, поки тіло не дуже гаряче → холодна точка
    Ih, cap_h = 0.95, 0.80
    frs.append(gen_curve(Ih, FIELD, cap_h))
    ch = cross_T(Ih, cap_h)[0]
    frs.append(circle(X(ch), Y(dissip(ch)), 5, fill=FIELD, stroke=INK, sw=1.5))
    b1 = fitbox(X(24), Y(0.44), 170, 44, "утримання:\nхолодна стійка точка\n(генерація < відведення)",
                size=11, fill="#eafaf0", stroke=FIELD, color="#1e7a45"); frs.append(b1)

    # струм спрацювання: генерація піднялась і вилітає вгору → лишилась гаряча засувлена точка
    It, cap_t = 1.9, 1.30
    frs.append(gen_curve(It, POS, cap_t))
    ct = cross_T(It, cap_t)[-1]
    frs.append(circle(X(ct), Y(dissip(ct)), 5, fill=POS, stroke=INK, sw=1.5))
    b2 = fitbox(X(126), Y(0.86), 176, 44, "спрацював (засув):\nгаряча точка, цівка струму\nгріє й тримає",
                size=11, fill="#fdecea", stroke=POS, color=POS); frs.append(b2)

    # лінія Ts
    frs.append(line(X(Ts), y0, X(Ts), yb, color=MUTED, sw=1.2, dash="3 4"))
    frs.append(text(X(Ts), y0 - 6, "Ts (перехід)", size=11, color=MUTED))

    render(os.path.join(IMG, "ptc-balance.svg"), W, H, *frs,
           title="PTC = рівновага двох потужностей: де генерація дорівнює відведенню")


# ── Фіг.4 — R(T) з різким коліном і зсув утримання від температури довкілля ──
def fig_ptc_derate():
    W, H = 760, 430
    x0, y0 = 92, 62
    gw, gh = 560, 300
    xb, yb = x0, y0 + gh

    Tmin, Tmax = -20.0, 140.0
    def X(T): return xb + (T - Tmin) / (Tmax - Tmin) * gw
    # лог-вісь опору (від 0.1× до 1000×)
    rlo, rhi = 0.1, 1000.0
    def Y(R): return yb - (math.log10(R) - math.log10(rlo)) / (math.log10(rhi) - math.log10(rlo)) * gh

    frs = []
    frs.append(line(xb, y0, xb, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 46, "температура тіла, °C", size=13, color=MUTED))
    frs.append(text(x0 - 60, y0 + gh / 2, "опір (log,", size=13, color=MUTED, anchor="middle"))
    frs.append(text(x0 - 60, y0 + gh / 2 + 17, "× холодного)", size=13, color=MUTED, anchor="middle"))

    for T in (-20, 20, 60, 100, 140):
        xx = X(T)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, "%d" % T, size=11, color=INK))
    for R, lab in ((0.1, "0.1×"), (1, "1×"), (10, "10×"), (100, "100×"), (1000, "1000×")):
        yy = Y(R)
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.5))
        frs.append(text(xb - 10, yy + 4, lab, size=11, color=INK, anchor="end"))

    # R(T): майже плаский, тоді різкий злам біля Ts=120
    Ts = 120.0
    pts = []
    T = Tmin
    while T <= Tmax:
        R = 1.0 * (1 + 0.004 * (T - 25)) + (1000.0 - 1) / (1.0 + math.exp(-(T - Ts) / 4.0))
        R = max(R, rlo)
        pts.append("%.1f,%.1f" % (X(T), Y(R)))
        T += 1.0
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), INK))

    # два довкілля: холодне (−10) і тепле (+60). Тіло має дійти до Ts, тож «запас нагріву» різний.
    # запас = Ts - Tamb; менший запас → менший струм утримання
    for Tamb, color, lab in ((-10.0, NEG, "довкілля −10 °C"), (60.0, POS, "довкілля +60 °C")):
        frs.append(line(X(Tamb), yb, X(Tamb), Y(1.4), color=color, sw=1.6, dash="4 4"))
        frs.append(circle(X(Tamb), Y(1.0 * (1 + 0.004 * (Tamb - 25))), 4.5, fill=color, stroke=INK, sw=1.3))
        # стрілка «запас нагріву до Ts»
        frs.append(arrow(X(Tamb), Y(1.4), X(Ts) - 2, Y(1.4), color=color, sw=1.6))
        frs.append(text((X(Tamb) + X(Ts)) / 2, Y(1.4) - 7, "запас нагріву", size=10, color=color))

    frs.append(line(X(Ts), y0, X(Ts), yb, color=MUTED, sw=1.2, dash="3 4"))
    frs.append(text(X(Ts) + 4, y0 + 6, "Ts", size=12, color=MUTED, anchor="start"))

    b = fitbox(X(-16), Y(300), 250, 60,
               "більший запас (холод) → тіло гріється\nдовше → більший струм утримання;\nу теплі запас малий → утримання падає",
               size=11, fill=FILL, stroke=MUTED, color=INK); frs.append(b)

    render(os.path.join(IMG, "ptc-derate.svg"), W, H, *frs,
           title="Різке коліно R(T) і чому струм утримання падає в теплі")


# ── Фіг.5 (hist) — баланс Пріса: нагрів 1/d² ↔ відведення d → I ∝ d^1.5 ──────
def fig_preece_law():
    W, H = 780, 470
    # ── ліва панель: два потоки тепла проти діаметра ──
    x0, y0 = 74, 76
    gw, gh = 372, 300
    xb, yb = x0, y0 + gh

    dmin, dmax = 0.4, 3.0          # умовний діаметр (норм.)
    pmax = 1.0
    def X(d): return xb + (d - dmin) / (dmax - dmin) * gw
    def Y(p): return yb - min(p, pmax) / pmax * gh

    frs = []
    frs.append(text(x0 + gw / 2, y0 - 26, "два потоки тепла проти діаметра", size=13, bold=True))
    frs.append(line(xb, y0, xb, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 42, "діаметр дротика d", size=12, color=MUTED))
    frs.append(text(x0 - 54, y0 + gh / 2, "потужність", size=12, color=MUTED, anchor="middle"))
    frs.append(text(x0 - 54, y0 + gh / 2 + 16, "(норм.)", size=12, color=MUTED, anchor="middle"))

    # нагрів ∝ 1/d² (спадає з товщиною) — червоний
    kg = 0.34
    pts = []
    d = dmin
    while d <= dmax:
        pts.append("%.1f,%.1f" % (X(d), Y(kg / (d * d))))
        d += 0.02
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), POS))

    # відведення ∝ d (росте з товщиною) — синій
    kd = 0.30
    frs.append(line(X(dmin), Y(kd * dmin), X(dmax), Y(kd * dmax), color=NEG, sw=3))

    # точка рівноваги: kg/d² = kd·d → d³ = kg/kd
    deq = (kg / kd) ** (1.0 / 3.0)
    peq = kd * deq
    frs.append(line(X(deq), yb, X(deq), Y(peq), color=MUTED, sw=1.2, dash="3 4"))
    frs.append(circle(X(deq), Y(peq), 5.5, fill="#fff", stroke=INK, sw=2))
    frs.append(text(X(deq), yb + 20, "рівновага", size=11, color=INK))

    frs.append(fitbox(X(1.5), Y(0.86), 176, 40, "нагрів  I²R ∝ 1/d²\n(тонше → гарячіше)",
                      size=11, fill="#fdecea", stroke=POS, color=POS))
    frs.append(fitbox(X(1.62), Y(0.30), 176, 38, "відведення ∝ d\n(товще → більша поверхня)",
                      size=11, fill="#eaf0fd", stroke=NEG, color=NEG))

    # ── права панель: сам закон I = C·d^1.5 ──
    x1 = 470
    gw2, gh2 = 250, 300
    xb2, yb2 = x1, y0 + gh2
    def X2(d): return xb2 + (d - dmin) / (dmax - dmin) * gw2
    imax = dmax ** 1.5
    def Y2(i): return yb2 - i / imax * gh2

    frs.append(text(x1 + gw2 / 2, y0 - 26, "закон плавлення", size=13, bold=True))
    frs.append(line(xb2, y0, xb2, yb2, color=INK, sw=2))
    frs.append(line(xb2, yb2, xb2 + gw2, yb2, color=INK, sw=2))
    frs.append(text(xb2 + gw2 / 2, yb2 + 42, "діаметр d", size=12, color=MUTED))
    frs.append(text(x1 - 40, y0 + gh2 / 2, "струм", size=12, color=MUTED, anchor="middle"))
    frs.append(text(x1 - 40, y0 + gh2 / 2 + 16, "плавлення", size=12, color=MUTED, anchor="middle"))

    pts2 = []
    d = dmin
    while d <= dmax:
        pts2.append("%.1f,%.1f" % (X2(d), Y2(d ** 1.5)))
        d += 0.02
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (" ".join(pts2), FIELD))

    # ілюстрація «×2 діаметра → ×2.8 струму»
    da, db = 1.0, 2.0
    for dd in (da, db):
        frs.append(line(X2(dd), yb2, X2(dd), Y2(dd ** 1.5), color=MUTED, sw=1, dash="3 4"))
        frs.append(line(xb2, Y2(dd ** 1.5), X2(dd), Y2(dd ** 1.5), color=MUTED, sw=1, dash="3 4"))
        frs.append(circle(X2(dd), Y2(dd ** 1.5), 4.5, fill=FIELD, stroke=INK, sw=1.4))
    frs.append(text(X2(da), yb2 + 18, "d", size=11, color=INK))
    frs.append(text(X2(db), yb2 + 18, "2d", size=11, color=INK))

    frs.append(fitbox(X2(1.05), Y2(imax * 0.9), 150, 52, "I = C·d^1.5\n\n×2 діаметра →\n×2.8 струму (2^1.5)",
                      size=11, fill=FILL, stroke=FIELD, color="#1e7a45"))

    render(os.path.join(IMG, "preece-law.svg"), W, H, *frs,
           title="Баланс Пріса: 1/d² проти d дає закон I ∝ d^1.5")


if __name__ == "__main__":
    fig_two_regimes()
    fig_let_through()
    fig_ptc_balance()
    fig_ptc_derate()
    fig_preece_law()
    print("OK: 5 фігур у", IMG)
