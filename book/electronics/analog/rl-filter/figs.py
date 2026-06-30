# -*- coding: utf-8 -*-
"""Фігури до теми «RL-фільтри: частотна характеристика» (аналогова, кутом теорії кіл).
Фігури статті:
  two-circuits.svg — ті самі R і L, два знімання виходу: на R → ФНЧ, на L → ФВЧ
  rolloff.svg      — АЧХ ФНЧ і ФВЧ: спад/підйом 6 дБ/окт; ролі частот ДЗЕРКАЛЬНІ до RC
  mag-phase.svg    — модуль (−3 дБ) і фаза (−45°) на зламі fc = R/(2πL)
Фігури вставки math-rl-transfer.md:
  divider-triangle.svg — трикутник опорів R⊥XL: звідки |H|, фаза й множник 0.707 на XL=R
  one-pole-slope.svg   — чому асимптота саме −6.02 дБ/окт = −20 дБ/дек (один полюс)
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _res_h(x, y, w=46, h=15):
    """Резистор-прямокутник горизонтальний; повертає (svg, лівий_x, правий_x)."""
    return rect(x, y - h / 2, w, h, fill=BG, stroke=LINE, sw=1.6, rx=2), x, x + w


def _coil_h(x, y, n=4, r=7):
    """Котушка горизонтальна — n півкіл (бугрів) угору; виводи зліва й справа."""
    out = []
    step = 2 * r
    d = "M%.1f %.1f" % (x, y)
    for i in range(n):
        cx = x + r + i * step
        d += " A%.1f %.1f 0 0 1 %.1f %.1f" % (r, r, cx + r, y)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, LINE))
    return "".join(out), x, x + n * step


def _coil_v(cx, y0, n=4, r=7):
    """Котушка вертикальна — n півкіл праворуч; виводи зверху (y0) й знизу."""
    step = 2 * r
    d = "M%.1f %.1f" % (cx, y0)
    for i in range(n):
        cy = y0 + r + i * step
        d += " A%.1f %.1f 0 0 0 %.1f %.1f" % (r, r, cx, cy + r)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, LINE), y0, y0 + n * step


def _ground(x, y):
    out = []
    for i, ww in enumerate((16, 10, 4)):
        out.append(line(x - ww, y + i * 5, x + ww, y + i * 5, color=LINE, sw=1.6))
    return "".join(out)


def two_circuits():
    """Один RL-дільник, два варіанти виходу: на R — ФНЧ, на L — ФВЧ."""
    W, H = 720, 380
    p = []

    def lowpass(ox, oy):
        # вхід -> L (послідовно) -> вузол -> R (на землю); вихід на R
        out = []
        out.append(text(ox - 6, oy + 4, "вхід", size=12, color=MUTED, anchor="end"))
        out.append(line(ox, oy, ox + 14, oy, color=LINE, sw=1.6))
        csvg, cl, cr = _coil_h(ox + 14, oy, n=4, r=8)
        out.append(csvg)
        out.append(text(cl + 32, oy - 16, "L", size=14, bold=True))
        nx = cr + 30
        out.append(line(cr, oy, nx, oy, color=LINE, sw=1.6))
        out.append(circle(nx, oy, 2.6, fill=INK, stroke=INK))
        # R вниз
        out.append(line(nx, oy, nx, oy + 22, color=LINE, sw=1.6))
        out.append(rect(nx - 7, oy + 22, 14, 40, fill=BG, stroke=LINE, sw=1.6, rx=2))
        out.append(text(nx + 18, oy + 46, "R", size=14, bold=True, anchor="start"))
        out.append(line(nx, oy + 62, nx, oy + 78, color=LINE, sw=1.6))
        out.append(_ground(nx, oy + 78))
        # вихід
        out.append(line(nx, oy, nx + 58, oy, color=LINE, sw=1.6))
        out.append(circle(nx + 58, oy, 3, fill=BG, stroke=LINE, sw=1.6))
        out.append(text(nx + 68, oy + 4, "вихід", size=12, color=MUTED, anchor="start"))
        out.append(text(ox + 78, oy - 72, "ВИХІД НА R", size=14, bold=True, color=NEG))
        out.append(text(ox + 78, oy - 54, "→ ФНЧ (нижні)", size=13, bold=True, color=NEG))
        return out

    def highpass(ox, oy):
        # вхід -> R (послідовно) -> вузол -> L (на землю); вихід на L
        out = []
        out.append(text(ox - 6, oy + 4, "вхід", size=12, color=MUTED, anchor="end"))
        out.append(line(ox, oy, ox + 14, oy, color=LINE, sw=1.6))
        rsvg, rl, rr = _res_h(ox + 14, oy)
        out.append(rsvg)
        out.append(text(rl + 23, oy - 14, "R", size=14, bold=True))
        nx = rr + 30
        out.append(line(rr, oy, nx, oy, color=LINE, sw=1.6))
        out.append(circle(nx, oy, 2.6, fill=INK, stroke=INK))
        # L вниз до землі
        out.append(line(nx, oy, nx, oy + 18, color=LINE, sw=1.6))
        cvert, cy0, cy1 = _coil_v(nx, oy + 18, n=4, r=8)
        out.append(cvert)
        out.append(text(nx + 18, oy + 40, "L", size=14, bold=True, anchor="start"))
        out.append(line(nx, cy1, nx, cy1 + 14, color=LINE, sw=1.6))
        out.append(_ground(nx, cy1 + 14))
        # вихід
        out.append(line(nx, oy, nx + 58, oy, color=LINE, sw=1.6))
        out.append(circle(nx + 58, oy, 3, fill=BG, stroke=LINE, sw=1.6))
        out.append(text(nx + 68, oy + 4, "вихід", size=12, color=MUTED, anchor="start"))
        out.append(text(ox + 78, oy - 72, "ВИХІД НА L", size=14, bold=True, color=POS))
        out.append(text(ox + 78, oy - 54, "→ ФВЧ (верхні)", size=13, bold=True, color=POS))
        return out

    p += lowpass(70, 150)
    p += highpass(430, 150)
    p.append(line(360, 64, 360, 252, color=MUTED, sw=1, dash="4 4"))

    b, _, _ = textbox(W / 2, 320,
                      "Ті самі два елементи, R і L. Котушка важка для швидкого, легка для повільного — тому її\n"
                      "роль протилежна конденсаторовій. Вихід на R пропускає нижні (ФНЧ); вихід на L — верхні (ФВЧ).",
                      size=12, fill=FILL, stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'two-circuits.svg'), W, H, *p,
           title="Один RL, два виходи: на R — ФНЧ, на L — ФВЧ")


def rolloff():
    """Дві АЧХ у log-log: ФНЧ (вихід на R, спад −6 дБ/окт) і ФВЧ (вихід на L, +6 дБ/окт);
    підкреслено, що ролі частот ДЗЕРКАЛЬНІ до RC (бо XL росте з f, а не спадає)."""
    W, H = 720, 410
    p = []
    ox, oy = 95, 320
    aw, ah = 535, 250
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 34, "частота (log)", size=13, bold=True))
    p.append(text(ox - 64, oy - ah / 2, "|вихід|", size=13, bold=True))
    p.append(text(ox - 64, oy - ah / 2 + 18, "(log)", size=12, color=MUTED))

    fc = ox + aw * 0.46
    p.append(line(fc, oy, fc, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text(fc, oy - ah - 8, "fc = R/(2πL)", size=12, bold=True, color=MUTED))

    # ── ФНЧ (вихід на R): плато до fc, далі спад ──
    yflat = oy - ah * 0.80
    p.append(line(ox, yflat, fc, yflat, color=NEG, sw=2.6))
    p.append(line(fc, yflat, ox + aw, yflat + ah * 0.60, color=NEG, sw=2.6))
    p.append(text(ox + 8, yflat - 8, "ФНЧ — вихід на R", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(fc + 86, yflat + ah * 0.36, "−6 дБ/окт", size=12, bold=True, color=NEG))

    # ── ФВЧ (вихід на L): підйом до fc, далі плато ──
    ylow = oy - ah * 0.16
    p.append(line(ox, ylow, fc, ylow - ah * 0.56, color=POS, sw=2.6))
    p.append(line(fc, ylow - ah * 0.56, ox + aw, ylow - ah * 0.56, color=POS, sw=2.6))
    p.append(text(ox + 8, ylow + 16, "ФВЧ — вихід на L", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 56, ylow - ah * 0.30, "+6 дБ/окт", size=12, bold=True, color=POS))

    # пояснення, що пропускається
    p.append(text((ox + fc) / 2, oy - 12, "нижні проходять на R", size=11, color=NEG))
    p.append(text((fc + ox + aw) / 2, oy - 12, "верхні проходять на L", size=11, color=POS))

    b, _, _ = textbox(W / 2, 382,
                      "Котушка опирається швидкому струму (XL = ωL росте з частотою): на верхніх вона майже\n"
                      "розрив, на нижніх — майже дріт. Тому ролі частот ДЗЕРКАЛЬНІ до RC при тому самому виході.",
                      size=12, fill=FILL, stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'rolloff.svg'), W, H, *p,
           title="АЧХ RL-фільтрів: нахил 6 дБ/окт, ролі частот — дзеркало RC")


def mag_phase():
    """Модуль і фаза ФНЧ навколо зламу: |H| падає на 3 дБ (×0.707), фаза = −45° на fc."""
    W, H = 720, 430
    p = []
    ox, oy = 95, 200
    aw, ah = 535, 150
    # верхня панель — модуль (лінійний, частка)
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.7))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.7))
    p.append(text(ox - 64, oy - ah / 2, "|H|", size=13, bold=True))

    def X(r):  # log-вісь ωτ від 0.1 до 10
        return ox + (math.log10(r) + 1.0) / 2.0 * aw

    # криві модуля й фази через справжню H = 1/√(1+(ωτ)²) — спільні для подачі
    fc = X(1.0)
    p.append(line(fc, oy, fc, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text(fc, oy - ah - 6, "fc: ωτ = 1  (XL = R)", size=12, bold=True, color=MUTED))

    # сітка по ωτ
    for rr, lab in [(0.1, "0.1·fc"), (1.0, "fc"), (10.0, "10·fc")]:
        gx = X(rr)
        p.append(text(gx, oy + 16, lab, size=10, color=MUTED))

    # модуль
    di = []
    rr = 0.1
    while rr <= 10.001:
        m = 1.0 / math.sqrt(1 + rr * rr)
        di.append((X(rr), oy - m * ah))
        rr *= 1.05
    d = "M%.1f %.1f" % di[0]
    for x, y in di[1:]:
        d += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    # рівень 0.707
    y707 = oy - 0.707 * ah
    p.append(line(ox, y707, fc, y707, color=NEG, sw=1, dash="3 3"))
    p.append(text(ox - 6, y707 + 4, "0.707", size=10, color=NEG, anchor="end"))
    p.append(circle(fc, y707, 4, fill=BG, stroke=NEG, sw=2))
    p.append(text(fc + 8, y707 - 6, "−3 дБ", size=11, bold=True, color=NEG, anchor="start"))

    # нижня панель — фаза
    oy2 = oy + 130
    ah2 = 130
    p.append(line(ox, oy2, ox + aw, oy2, color=INK, sw=1.7))             # 0°
    p.append(line(ox, oy2 - ah2 / 2, ox, oy2 + ah2 / 2, color=INK, sw=1.7))
    p.append(text(ox - 64, oy2, "фаза", size=13, bold=True))
    p.append(text(ox + aw / 2, oy2 + ah2 / 2 + 30, "частота (log)", size=13, bold=True))
    p.append(line(fc, oy2 - ah2 / 2, fc, oy2 + ah2 / 2, color=MUTED, sw=1, dash="4 4"))
    # позначки 0 / −45 / −90
    p.append(text(ox - 6, oy2 + 4, "0°", size=10, color=MUTED, anchor="end"))
    y45 = oy2 + ah2 / 2 * 0.5
    y90 = oy2 + ah2 / 2 * 0.95
    p.append(text(ox - 6, y45 + 4, "−45°", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 6, y90 + 4, "−90°", size=10, color=MUTED, anchor="end"))
    p.append(line(ox, y45, fc, y45, color=POS, sw=1, dash="3 3"))

    df = []
    rr = 0.1
    while rr <= 10.001:
        ph = math.atan(rr)              # для ФНЧ фаза = −arctan(ωτ)
        df.append((X(rr), oy2 + (ph / (math.pi / 2)) * (ah2 / 2) * 0.95))
        rr *= 1.05
    d2 = "M%.1f %.1f" % df[0]
    for x, y in df[1:]:
        d2 += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d2, POS))
    p.append(circle(fc, y45, 4, fill=BG, stroke=POS, sw=2))
    p.append(text(fc + 8, y45 - 6, "−45° рівно на зламі", size=11, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 408,
                      "На зламі fc реактивність котушки дорівнює опору (XL = R): амплітуда падає до 0.707 (−3 дБ),\n"
                      "а фаза проходить рівно −45°. Точка −3 дБ і фаза −45° — той самий момент XL = R.",
                      size=12, fill=FILL, stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'mag-phase.svg'), W, H, *p,
           title="ФНЧ навколо зламу: −3 дБ за модулем і −45° за фазою")


def divider_triangle():
    """Трикутник опорів для вставки: R (по горизонталі) ⊥ XL (по вертикалі),
    гіпотенуза √(R²+XL²). Показано і загальний кут, і окремо випадок XL = R → 45°, 0.707."""
    W, H = 720, 410
    p = []

    # ── загальний трикутник ліворуч ──
    ax, ay = 95, 300          # вершина прямого кута (початок векторів)
    R = 150.0
    XL = 110.0
    # R — праворуч по горизонталі (активна вісь)
    p.append(line(ax, ay, ax + R, ay, color=NEG, sw=3))
    p.append(text(ax + R / 2, ay + 22, "R", size=15, bold=True, color=NEG))
    # XL — вгору по вертикалі (реактивна вісь)
    p.append(line(ax + R, ay, ax + R, ay - XL, color=POS, sw=3))
    p.append(text(ax + R + 16, ay - XL / 2, "XL = ωL", size=14, bold=True, color=POS, anchor="start"))
    # гіпотенуза — повний імпеданс
    p.append(line(ax, ay, ax + R, ay - XL, color=INK, sw=3))
    hx, hy = ax + R * 0.42, ay - XL * 0.42
    p.append(text(hx - 8, hy - 8, "√(R²+XL²)", size=14, bold=True, anchor="end"))
    # прямий кут
    p.append(line(ax + R - 12, ay, ax + R - 12, ay - 12, color=MUTED, sw=1.2))
    p.append(line(ax + R - 12, ay - 12, ax + R, ay - 12, color=MUTED, sw=1.2))
    # дуга кута φ при вершині
    import math as _m
    phi = _m.atan2(XL, R)
    ar = 46
    a0 = "M%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f" % (
        ax + ar, ay, ar, ar, ax + ar * _m.cos(phi), ay - ar * _m.sin(phi))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (a0, MUTED))
    p.append(text(ax + ar + 16, ay - 12, "φ", size=15, bold=True, color=MUTED, anchor="start"))
    p.append(text(ax + 6, ay - XL - 26, "ВЕКТОРИ СКЛАДАЮТЬСЯ ПІД 90°", size=12, bold=True, anchor="start"))
    p.append(text(ax + 6, ay - XL - 10, "tg φ = XL/R = ωτ", size=12, color=MUTED, anchor="start"))

    # ── окремий випадок XL = R праворуч ──
    bx, by = 470, 300
    S = 130.0
    p.append(line(bx, by, bx + S, by, color=NEG, sw=3))
    p.append(text(bx + S / 2, by + 22, "R", size=15, bold=True, color=NEG))
    p.append(line(bx + S, by, bx + S, by - S, color=POS, sw=3))
    p.append(text(bx + S + 14, by - S / 2, "XL = R", size=14, bold=True, color=POS, anchor="start"))
    p.append(line(bx, by, bx + S, by - S, color=INK, sw=3))
    p.append(text(bx + S * 0.30, by - S * 0.62, "R·√2", size=14, bold=True, anchor="end"))
    p.append(line(bx + S - 12, by, bx + S - 12, by - 12, color=MUTED, sw=1.2))
    p.append(line(bx + S - 12, by - 12, bx + S, by - 12, color=MUTED, sw=1.2))
    ar2 = 42
    a1 = "M%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f" % (
        bx + ar2, by, ar2, ar2, bx + ar2 * _m.cos(_m.pi / 4), by - ar2 * _m.sin(_m.pi / 4))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (a1, FIELD))
    p.append(text(bx + ar2 + 12, by - 16, "45°", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(bx + 4, by - S - 26, "НА ЗЛАМІ: XL = R", size=12, bold=True, anchor="start"))
    p.append(text(bx + 4, by - S - 10, "|H| = R/(R·√2) = 0.707", size=12, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 372,
                      "R і XL — катети під прямим кутом (між ними рівно 90°), тож повний опір — гіпотенуза\n"
                      "√(R²+XL²), а НЕ сума R+XL. Коли XL = R, гіпотенуза = R·√2, кут = 45°, частка = 0.707.",
                      size=12, fill=FILL, stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'divider-triangle.svg'), W, H, *p,
           title="Трикутник опорів: чому √(R²+XL²), 45° і 0.707")


def one_pole_slope():
    """Чому асимптота саме −6.02 дБ/окт. Лог-лог: точна крива |H|=1/√(1+(ωτ)²)
    і її дві асимптоти; на декаду частоти — рівно −20 дБ, на октаву — −6.02 дБ."""
    W, H = 720, 440
    p = []
    ox, oy = 100, 330
    aw, ah = 520, 250

    def X(d):   # вісь log10(ωτ) від −1 (0.1) до 3 (1000)
        return ox + (d + 1.0) / 4.0 * aw

    def Ydb(db):  # вісь дБ: 0 угорі (oy-ah) … −80 унизу (oy)
        return oy - (db + 80.0) / 80.0 * ah

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 50, "частота, ωτ (log)", size=13, bold=True))
    p.append(text(ox - 70, oy - ah / 2, "|H|, дБ", size=13, bold=True))

    # сітка по декадах
    for d, lab in [(-1, "0.1"), (0, "1 (fc)"), (1, "10"), (2, "100"), (3, "1000")]:
        gx = X(d)
        p.append(line(gx, oy, gx, oy - ah, color="#e3e6ea", sw=1))
        p.append(text(gx, oy + 18, lab, size=10, color=MUTED))
    for db in [0, -20, -40, -60]:
        gy = Ydb(db)
        p.append(line(ox, gy, ox + aw, gy, color="#e3e6ea", sw=1))
        p.append(text(ox - 8, gy + 4, "%d" % db, size=10, color=MUTED, anchor="end"))

    # точна крива |H| = 1/√(1+(ωτ)²)
    import math as _m
    pts = []
    d = -1.0
    while d <= 3.0001:
        wt = 10 ** d
        mag = 1.0 / _m.sqrt(1 + wt * wt)
        db = 20 * _m.log10(mag)
        pts.append((X(d), Ydb(db)))
        d += 0.04
    path = "M%.1f %.1f" % pts[0]
    for x, y in pts[1:]:
        path += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path, NEG))

    # асимптоти: 0 дБ до fc, далі −20 дБ/дек
    p.append(line(X(-1), Ydb(0), X(0), Ydb(0), color=MUTED, sw=1.6, dash="6 4"))
    p.append(line(X(0), Ydb(0), X(3), Ydb(-60), color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(X(-0.9), Ydb(0) - 8, "асимптота 0 дБ", size=11, color=MUTED, anchor="start"))

    # позначка −3 дБ на зламі
    p.append(circle(X(0), Ydb(-3), 4, fill=BG, stroke=NEG, sw=2))
    p.append(text(X(0) + 8, Ydb(-3) - 6, "−3 дБ", size=11, bold=True, color=NEG, anchor="start"))

    # сходинка «одна декада = −20 дБ»
    p.append(line(X(1), Ydb(-20), X(2), Ydb(-20), color=POS, sw=1.4, dash="3 3"))
    p.append(line(X(2), Ydb(-20), X(2), Ydb(-40), color=POS, sw=1.4, dash="3 3"))
    p.append(text(X(1.5), Ydb(-20) - 8, "декада ×10", size=11, bold=True, color=POS))
    p.append(text(X(2) + 8, Ydb(-30), "−20 дБ", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(X(2) + 8, Ydb(-30) + 16, "(= −6.02 дБ/окт)", size=10, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 410,
                      "Високо над зламом |H| ≈ R/XL = 1/(ωτ): подвоїв частоту — удвічі менший вихід (−6.02 дБ),\n"
                      "помножив на 10 — у 10 разів менший (−20 дБ). Один полюс — одна стала «сходинка» нахилу.",
                      size=12, fill=FILL, stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'one-pole-slope.svg'), W, H, *p,
           title="Нахил одного полюса: −20 дБ/дек = −6.02 дБ/окт")


if __name__ == '__main__':
    two_circuits()
    rolloff()
    mag_phase()
    divider_triangle()
    one_pole_slope()
    print("OK: 5 figures ->", OUT)
