# -*- coding: utf-8 -*-
"""Фігури для теми resonant-converter (резонансні перетворювачі LLC/LCC).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # осердя / магнітне
COILC = "#8a6d1f"  # котушка


def _coil(x, y_top, y_bot, n=5, r=9, left=True):
    """Обмотка як ланцюжок півдуг уздовж вертикалі (декоративна котушка)."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    sweep = 0 if left else 1
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, step / 2, sweep, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, COILC)


def _coil_h(y, x_left, x_right, n=5, r=9, up=True):
    """Обмотка горизонтальна (ланцюжок півдуг уздовж горизонталі)."""
    step = (x_right - x_left) / n
    d = "M %.1f %.1f " % (x_left, y)
    sweep = 1 if up else 0
    xx = x_left
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (step / 2, r, sweep, xx + step, y)
        xx += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, COILC)


def fig_hard_vs_soft():
    """Втрати комутації: жорсткий ключ бачить перекриття U·I у мить перемикання
    (спалах тепла), м'який (ZVS) вмикається, коли напруга на ньому вже нуль —
    добуток U·I ≈ 0, спалаху нема."""
    W, H = 900, 440
    f = []
    midx = W / 2

    for col, (x0, title, soft) in enumerate([
        (40, "Жорстка комутація", False),
        (midx + 20, "М'яка комутація (ZVS)", True),
    ]):
        x1 = x0 + (midx - 60)
        f.append(rect(x0, 60, x1 - x0, 340, fill="#fafafa", stroke=MUTED, sw=1.5))
        f.append(text((x0 + x1) / 2, 86, title, size=15, color=INK, bold=True))

        L = x0 + 46
        R = x1 - 20
        base = 300           # вісь часу
        top = 130
        f.append(line(L, top - 6, L, base, color=INK, sw=1.6))
        f.append(line(L, base, R, base, color=INK, sw=1.6))
        f.append(text(R, base + 20, "час", size=11, color=INK))

        xsw = L + (R - L) * 0.42     # мить перемикання
        f.append(line(xsw, top - 4, xsw, base + 6, color=MUTED, sw=1, dash="3 4"))
        f.append(text(xsw, base + 20, "вмикання", size=10, color=MUTED))

        hi = top + 12
        # струм: наростає під час/після перемикання
        # напруга: до перемикання висока, після — падає до нуля
        if not soft:
            # НАПРУГА на ключі — падає РІЗКО прямо в мить вмикання (ще висока, коли струм уже пішов)
            v = ["%.1f,%.1f" % (L, hi), "%.1f,%.1f" % (xsw, hi),
                 "%.1f,%.1f" % (xsw + 30, base - 4), "%.1f,%.1f" % (R, base - 4)]
            # СТРУМ — наростає прямо в мить вмикання (перекриття з напругою)
            i = ["%.1f,%.1f" % (L, base - 4), "%.1f,%.1f" % (xsw, base - 4),
                 "%.1f,%.1f" % (xsw + 30, base - 90), "%.1f,%.1f" % (R, base - 90)]
        else:
            # НАПРУГА вже впала до нуля ДО вмикання (резонанс дотиснув її раніше)
            v = ["%.1f,%.1f" % (L, hi), "%.1f,%.1f" % (xsw - 40, hi),
                 "%.1f,%.1f" % (xsw - 6, base - 4), "%.1f,%.1f" % (R, base - 4)]
            i = ["%.1f,%.1f" % (L, base - 4), "%.1f,%.1f" % (xsw, base - 4),
                 "%.1f,%.1f" % (xsw + 30, base - 90), "%.1f,%.1f" % (R, base - 90)]

        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(v), POS))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(i), NEG))
        f.append(text(L + 6, hi - 8, "U", size=12, color=POS, bold=True, anchor="start"))
        f.append(text(R - 6, base - 96, "I", size=12, color=NEG, bold=True, anchor="end"))

        # зона перекриття U·I
        if not soft:
            f.append(rect(xsw, base - 90, 30, 86, fill="#c0392b", stroke="none", sw=0))
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.20"/>'
                     % (xsw, base - 90, 30, 86, POS))
            f.append(text(xsw + 15, top + 2, "U·I", size=13, color=POS, bold=True))
            f.append(text((L + R) / 2, base + 44, "перекриття → СПАЛАХ тепла", size=12, color=POS, bold=True))
        else:
            f.append(text((L + R) / 2, base + 44, "U вже = 0 → U·I ≈ 0, втрат нема", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, "hard-vs-soft.svg"), W, H, *f)


def fig_llc_tank():
    """Топологія LLC: півміст рубає квадрат → резонансний бак Lr+Cr (послідовно)
    з Lm (паралельно первинній) → трансформатор → випрямляч → вихід.
    Три реактивні елементи: L, L, C — звідси «LLC»."""
    W, H = 940, 430
    f = []
    y = 200

    # ── півміст (генератор квадрата) ──
    hx = 120
    f.append(rect(60, 120, 120, 160, fill="#fafafa", stroke=MUTED, sw=1.5))
    f.append(text(hx, 108, "півміст", size=13, color=INK, bold=True))
    f.append(rect(hx - 26, 140, 52, 40, fill="#ffffff", stroke=POS, sw=1.6, rx=4))
    f.append(text(hx, 164, "ключ", size=11, color=POS))
    f.append(rect(hx - 26, 220, 52, 40, fill="#ffffff", stroke=POS, sw=1.6, rx=4))
    f.append(text(hx, 244, "ключ", size=11, color=POS))
    f.append(text(hx, 300, "квадрат ±Vвх/2", size=11, color=INK, bold=True))

    # вихід півмоста → бак
    f.append(line(hx + 26, y, 230, y, color=INK, sw=2))

    # ── Lr (послідовна котушка) ──
    f.append(_coil_h(y, 230, 320, n=4, r=9, up=True))
    f.append(text(275, y - 24, "Lr", size=14, color=COILC, bold=True))
    f.append(text(275, 300, "резонансна", size=10, color=MUTED))

    # ── Cr (послідовний конденсатор) ──
    cx = 360
    f.append(line(320, y, cx - 8, y, color=INK, sw=2))
    f.append(line(cx - 8, y - 16, cx - 8, y + 16, color=INK, sw=2.6))
    f.append(line(cx + 8, y - 16, cx + 8, y + 16, color=INK, sw=2.6))
    f.append(text(cx, y - 26, "Cr", size=14, color=NEG, bold=True))
    f.append(line(cx + 8, y, 430, y, color=INK, sw=2))

    # вузол перед Lm / первинною
    nx = 430
    f.append(circle(nx, y, 3, fill=INK, stroke=INK))

    # ── Lm (паралельно первинній, вертикально вниз) ──
    f.append(_coil(nx, y + 10, y + 90, n=4, r=8, left=True))
    f.append(text(nx - 24, y + 52, "Lm", size=14, color=GOLD, bold=True))
    f.append(text(nx - 24, y + 108, "намагнічув.", size=10, color=MUTED, anchor="middle"))

    # ── трансформатор (первинна = права гілка вузла) ──
    tx = 560
    f.append(line(nx, y, tx - 16, y, color=INK, sw=2))
    f.append(_coil(tx - 16, y - 45, y + 45, n=5, r=10, left=True))
    f.append(_coil(tx + 16, y - 45, y + 45, n=5, r=10, left=False))
    f.append(line(tx - 4, y - 50, tx - 4, y + 50, color=GOLD, sw=2))
    f.append(line(tx + 4, y - 50, tx + 4, y + 50, color=GOLD, sw=2))
    f.append(text(tx, 108, "трансформатор", size=13, color=GOLD, bold=True))
    f.append(text(tx, 300, "ізоляція + витки", size=10, color=MUTED))
    # нижній зворотний дріт первинної
    f.append(line(nx, y + 90, nx, y + 120, color=INK, sw=2))
    f.append(line(nx, y + 120, tx - 16, y + 120, color=INK, sw=2))
    f.append(line(tx - 16, y + 45, tx - 16, y + 120, color=INK, sw=2))

    # ── випрямляч + вихід ──
    rx = 720
    f.append(line(tx + 16, y - 45, rx, y - 45, color=INK, sw=2))
    f.append(line(tx + 16, y + 45, rx, y + 45, color=INK, sw=2))
    b, w, h = textbox(rx + 60, y, "випрямляч\n+ конденсатор", size=12,
                      fill="#ffffff", stroke=FIELD, sw=1.6)
    f.append(b)
    f.append(line(rx, y - 45, rx + 60 - w / 2, y - 20, color=INK, sw=2))
    f.append(line(rx, y + 45, rx + 60 - w / 2, y + 20, color=INK, sw=2))
    f.append(text(rx + 60, 300, "Vвих", size=13, color=FIELD, bold=True))
    f.append(text(rx + 60, 108, "вихід", size=13, color=FIELD, bold=True))

    # підпис «L L C»
    f.append(text(W / 2, 390, "L (Lr) · L (Lm) · C (Cr)  →  «LLC»", size=15, color=INK, bold=True))

    return render(os.path.join(IMG, "llc-tank.svg"), W, H, *f)


def fig_gain_curve():
    """Крива підсилення LLC від частоти: коефіцієнт напруги M(f) з піком біля
    fr, спадом угору. На fr0 (Lr+Cr) підсилення = 1 незалежно від навантаження;
    ліворуч M може бути >1 (підвищення), праворуч <1 (зниження). Робоча зона —
    праворуч від піка, там ZVS."""
    W, H = 900, 470
    f = []
    L, R = 110, 800
    T, B = 70, 360
    # осі
    f.append(line(L, T - 6, L, B, color=INK, sw=1.8))
    f.append(line(L, B, R + 6, B, color=INK, sw=1.8))
    f.append(text(L - 10, T + 4, "M = Vвих/Vвх", size=12, color=INK, anchor="end"))
    f.append(text(R + 6, B + 24, "частота fsw →", size=12, color=INK, anchor="end"))

    # рівень M=1
    y1 = B - 120
    f.append(line(L, y1, R, y1, color=MUTED, sw=1, dash="5 4"))
    f.append(text(L - 8, y1 + 4, "M = 1", size=11, color=MUTED, anchor="end"))

    # криві підсилення для кількох навантажень (пік ліворуч від fr, спад угору).
    # Стандартна перша-гармонічна модель LLC: на fn=1 (fr0) M=1 за будь-якого Q.
    FN_LO, FN_HI = 0.45, 1.9
    LN = 5.0   # Lm/Lr — визначає висоту піка на низьких частотах

    def gain(fn, q):
        a = (1.0 + 1.0 / LN * (1.0 - 1.0 / (fn * fn))) ** 2
        b = (q * (fn - 1.0 / fn)) ** 2
        return 1.0 / math.sqrt(a + b)

    def fn_to_x(fn):
        return L + (fn - FN_LO) / (FN_HI - FN_LO) * (R - L)

    fr_x = fn_to_x(1.0)          # fr0 (Lr+Cr): усі криві сходяться в M=1 при fn=1
    curves = [(0.30, "#2457d6", "легке навантаження"),
              (0.55, "#7a3fb0", "середнє"),
              (1.0, "#c0392b", "важке навантаження")]
    for q, col, _lbl in curves:
        pts = []
        for k in range(0, 141):
            fn = FN_LO + k / 140.0 * (FN_HI - FN_LO)
            g = gain(fn, q)
            x = fn_to_x(fn)
            yv = B - g * 120  # M=1 лягає на y1 (=B-120)
            yv = max(T + 2, yv)
            pts.append("%.1f,%.1f" % (x, yv))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), col))

    # лінія fr0 (точка сходження M=1 для всіх навантажень)
    f.append(line(fr_x, T - 2, fr_x, B, color=FIELD, sw=1.4, dash="6 4"))
    f.append(circle(fr_x, y1, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(fr_x, T - 10, "fr0 (Lr+Cr): M=1 за будь-якого навантаження", size=11, color=FIELD, bold=True))

    # зони підвищення/зниження
    f.append(text(L + (fr_x - L) * 0.45, B - 200, "M > 1", size=15, color=POS, bold=True))
    f.append(text(L + (fr_x - L) * 0.45, B - 182, "(підвищення)", size=11, color=POS))
    f.append(text(fr_x + (R - fr_x) * 0.5, B - 60, "M < 1", size=15, color=NEG, bold=True))
    f.append(text(fr_x + (R - fr_x) * 0.5, B - 42, "(зниження)", size=11, color=NEG))

    # робоча зона ZVS (праворуч від піка)
    zx0 = fr_x - 20
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.10"/>'
             % (zx0, T, R - zx0, B - T, FIELD))
    f.append(text((zx0 + R) / 2, B - 250, "робоча зона: ZVS", size=13, color=FIELD, bold=True))

    # легенда навантажень
    lx, ly = L + 20, B + 44
    for i, (q, col, lbl) in enumerate(curves):
        yy = ly + i * 20
        f.append(line(lx, yy, lx + 26, yy, color=col, sw=2.6))
        f.append(text(lx + 34, yy + 4, lbl, size=11, color=INK, anchor="start"))

    return render(os.path.join(IMG, "gain-curve.svg"), W, H, *f)


def fig_frequency_knob():
    """Керування частотою замість шпаруватості: контролер РУХАЄ fsw уздовж кривої
    підсилення — вихід просів → підійти до fr (підсилення росте), вихід високий →
    піти вгору за частотою (підсилення падає). Ключі завжди 50 % — «крутиться»
    сама частота."""
    W, H = 880, 380
    f = []

    f.append(text(W / 2, 40, "Замість «крутити D» — рухати частоту fsw", size=17, color=INK, bold=True))

    # лівий блок: вимірювання
    b, w, h = textbox(W * 0.17, 130, "вихід Vвих\nвиміряти", size=13,
                      fill="#e9f7ef", stroke=FIELD, sw=1.8, bold=True)
    f.append(b)

    # стрілка
    f.append(arrow(W * 0.17 + w / 2, 130, W * 0.40, 130, color=INK, sw=2))

    # центр: рішення контролера
    b, w, h = textbox(W * 0.53, 130, "контролер:\nзсунути fsw", size=13,
                      fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True)
    f.append(b)

    # дві гілки: просів / завищений
    f.append(arrow(W * 0.53, 165, W * 0.30, 235, color=POS, sw=2))
    f.append(arrow(W * 0.53, 165, W * 0.76, 235, color=NEG, sw=2))

    b, w, h = textbox(W * 0.28, 265, "просів → fsw ближче до fr\n(підсилення ↑)", size=12,
                      fill="#fdecea", stroke=POS, sw=1.6)
    f.append(b)
    b, w, h = textbox(W * 0.76, 265, "завищений → fsw вгору\n(підсилення ↓)", size=12,
                      fill="#eaf0fd", stroke=NEG, sw=1.6)
    f.append(b)

    # знизу: ключі 50%
    f.append(text(W / 2, 345, "ключі щоцикл 50 % / 50 % — змінюється лише ЧАСТОТА", size=13, color=GOLD, bold=True))

    return render(os.path.join(IMG, "frequency-knob.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [
        fig_hard_vs_soft(),
        fig_llc_tank(),
        fig_gain_curve(),
        fig_frequency_knob(),
    ]
    for o in outs:
        print("written:", o)
