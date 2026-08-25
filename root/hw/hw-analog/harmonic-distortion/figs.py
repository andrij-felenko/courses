# -*- coding: utf-8 -*-
"""Фігури до теми «Гармонічні спотворення» (аналогова електроніка, кутом теорії кіл).
Дві фігури:
  curve-makes-harmonics.svg — пряма характеристика зберігає синусоїду (одна частота);
                              зігнута приплюскує верхівки → форма спотворена → гармоніки.
  even-odd-harmonics.svg    — несиметричне викривлення дає парні гармоніки (друга),
                              симетричне — непарні (третя); поряд спектри-стовпчики.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _poly(pts, color, sw=2.0, dash=None):
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


def curve_makes_harmonics():
    """Дві панелі: лінійна передавальна характеристика проти зігнутої.
    На кожній — характеристика «вихід від входу», вхідна синусоїда знизу,
    вихідна синусоїда збоку (для зігнутої — з приплюснутими верхівками)."""
    W, H = 760, 440
    p = []

    def panel(x0, title, bend, col, note):
        # рамка координат характеристики
        gx, gy = x0 + 70, 90          # лівий-верхній кут поля
        gw, gh = 170, 170
        cx0 = gx                      # вісь входу (горизонт) — від лівого краю
        cy0 = gy + gh                 # вісь виходу (вертикаль) — від низу
        out = []
        out.append(text(x0 + 165, 64, title, size=14, bold=True, color=col))
        # осі
        out.append(line(cx0, gy, cx0, cy0 + 6, color=INK, sw=1.6))       # вертикальна (вихід)
        out.append(line(cx0 - 6, cy0, gx + gw, cy0, color=INK, sw=1.6))  # горизонтальна (вхід)
        out.append(text(gx + gw + 4, cy0 + 4, "вхід", size=11, color=MUTED, anchor="start"))
        out.append(text(cx0 - 6, gy - 6, "вихід", size=11, color=MUTED, anchor="end"))

        # характеристика «вихід від входу» в нормованих [-1,1] по обох осях
        def f(u):
            if bend == 0.0:
                return u
            # м'яке симетричне насичення (приплюскує обидві верхівки)
            return math.tanh(u * 1.7) / math.tanh(1.7)
        def to_xy(u):
            xx = cx0 + (u + 1) / 2 * gw
            yy = cy0 - (f(u) + 1) / 2 * gh
            return xx, yy
        curve = [to_xy(-1 + 2 * k / 80) for k in range(81)]
        out.append(_poly(curve, col, sw=2.4))
        # тонка ідеальна пряма для порівняння на зігнутій панелі
        if bend != 0.0:
            diag = [(cx0 + (u + 1) / 2 * gw, cy0 - (u + 1) / 2 * gh) for u in (-1, 1)]
            out.append(_poly(diag, MUTED, sw=1.0, dash="3 3"))

        # вхідна синусоїда — знизу під полем (горизонтальна вісь часу)
        iy = cy0 + 70
        in_pts = []
        amp = 26
        N = 90
        for k in range(N + 1):
            u = math.sin(2 * math.pi * 1.3 * k / N)
            xx = cx0 + gw * k / N
            in_pts.append((xx, iy - u * amp * 0.55))
        out.append(_poly(in_pts, NEG, sw=1.8))
        out.append(text(cx0 - 8, iy, "вхід:", size=11, color=NEG, anchor="end"))
        out.append(text(cx0 + gw / 2, iy + 34, "чиста синусоїда", size=11, color=NEG))

        # вихідна синусоїда — праворуч від поля (вертикальна вісь = вихід)
        ox = gx + gw + 56
        out_pts = []
        for k in range(N + 1):
            u = math.sin(2 * math.pi * 1.3 * k / N)
            yy = gy + gh * k / N
            out_pts.append((ox + f(u) * 36, yy))
        out.append(_poly(out_pts, col, sw=2.0))
        out.append(text(ox, gy - 10, "вихід", size=11, color=col))
        out.append(text(ox, gy + gh + 20, note, size=11, color=col))
        return out

    p += panel(20, "лінійна характеристика", 0.0, FIELD, "форма ціла")
    p += panel(400, "зігнута характеристика", 1.0, POS, "верхівки приплюснуті")

    b, _, _ = textbox(W / 2, 412,
                      "Пряма характеристика «вихід від входу» зберігає синусоїду — одна частота.\n"
                      "Зігнута приплюскує верхівки: форма спотворена — народжуються гармоніки.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'curve-makes-harmonics.svg'), W, H, *p,
           title="Чому крива характеристика породжує гармоніки, а пряма — ні")


def even_odd_harmonics():
    """Два роди викривлення: несиметричне (парні гармоніки) і симетричне (непарні).
    Зліва форма сигналу, справа спектр-стовпчики."""
    W, H = 760, 470
    p = []
    amp = 34

    def block(y0, title, kind, col, spectrum, note):
        # kind: 'asym' приплюскує лише верхню; 'sym' — обидві
        out = []
        out.append(text(140, y0 - 44, title, size=14, bold=True, color=col))
        # форма сигналу
        wx, ww = 40, 200
        midy = y0
        out.append(line(wx, midy, wx + ww, midy, color=MUTED, sw=1.0, dash="2 3"))
        pts = []
        N = 120
        for k in range(N + 1):
            u = math.sin(2 * math.pi * 1.4 * k / N)
            if kind == 'asym':
                v = u if u < 0 else math.tanh(u * 2.0) / math.tanh(2.0) * 0.72
            else:  # sym
                v = math.tanh(u * 2.0) / math.tanh(2.0)
            xx = wx + ww * k / N
            pts.append((xx, midy - v * amp))
        out.append(_poly(pts, col, sw=2.2))
        out.append(text(wx + ww / 2, y0 + 64, note, size=11, color=col))

        # спектр-стовпчики праворуч
        sx0 = 360
        base = y0 + 56
        bw = 34
        gap = 78
        maxh = 96
        labels = ["1", "2", "3", "4", "5"]
        out.append(line(sx0 - 16, base, sx0 + 4 * gap + bw + 16, base, color=INK, sw=1.4))
        for i, (frac) in enumerate(spectrum):
            cx = sx0 + i * gap
            h = max(2, maxh * frac)
            # основна — нейтральна, гармоніки — кольором роду
            c = INK if i == 0 else col
            fillc = "#eef0f2" if i == 0 else ("#fdecea" if col == POS else "#eaf0fd")
            out.append(rect(cx, base - h, bw, h, fill=fillc, stroke=c, sw=1.6, rx=2))
            out.append(text(cx + bw / 2, base + 16, labels[i], size=11, bold=True, color=c))
        out.append(text(sx0 + 2 * gap, base + 34, "номер гармоніки", size=11, color=MUTED))
        return out

    # несиметричне → переважає 2-га (парна)
    p += block(110, "несиметричне викривлення", 'asym', POS,
               [1.00, 0.34, 0.06, 0.04, 0.02], "приплюснута лише верхівка")
    # симетричне → 2-га гасне, лишається 3-тя (непарна)
    p += block(300, "симетричне викривлення", 'sym', NEG,
               [1.00, 0.02, 0.30, 0.02, 0.10], "приплюснуті обидві верхівки")

    b, _, _ = textbox(W / 2, 438,
                      "Несиметричне приплюскування дає ПАРНІ гармоніки (2-га, «октава», тепла).\n"
                      "Симетричне гасить парні — лишаються НЕПАРНІ (3-тя, на слух різка).",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'even-odd-harmonics.svg'), W, H, *p,
           title="Парні й непарні гармоніки: форма викривлення вирішує спектр")


def fourier_builds_shape():
    """До історичної вставки про Фур'є: як гострий «незграбний» профіль
    (пилка — саме така форма бентежила Ейлера) складається з синусоїд кратних
    частот. Три панелі-сходинки: 1 синусоїда → 3 → 8 доданків — наближення
    щоразу ближче до пилки. Внизу — спектр-стовпчики амплітуд гармонік 1/n."""
    W, H = 780, 470
    p = []

    # цільова пилка в нормованих [-1,1] на період t∈[0,1)
    def saw(t):
        # симетрична пилка з розмахом ±1, період 1
        return 2.0 * (t - math.floor(t + 0.5))

    # часткова сума ряду пилки: sum (2/π)(-1)^{k+1} sin(2π k t)/k
    def partial(t, n):
        s = 0.0
        for k in range(1, n + 1):
            s += ((-1) ** (k + 1)) * math.sin(2 * math.pi * k * t) / k
        return (2.0 / math.pi) * s

    def panel(x0, title, n, col):
        out = []
        gx, gy, gw, gh = x0 + 18, 84, 200, 130
        midy = gy + gh / 2
        amp = gh / 2 - 6
        # вісь часу
        out.append(line(gx, midy, gx + gw, midy, color=MUTED, sw=1.0, dash="2 3"))
        out.append(text(x0 + 118, 70, title, size=13, bold=True, color=col))
        # цільова пилка — тонко, сірим, як орієнтир
        N = 240
        tgt = [(gx + gw * j / N, midy - saw(j / N) * amp) for j in range(N + 1)]
        out.append(_poly(tgt, MUTED, sw=1.0, dash="4 3"))
        # часткова сума — кольором
        appr = [(gx + gw * j / N, midy - partial(j / N, n) * amp) for j in range(N + 1)]
        out.append(_poly(appr, col, sw=2.4))
        return out

    p += panel(10, "1 синусоїда", 1, NEG)
    p += panel(265, "3 доданки", 3, FIELD)
    p += panel(520, "8 доданків", 8, POS)

    # підпис-орієнтир пилки
    p.append(text(W / 2, 238,
                  "сіра пунктирна — ціль (пилка); кольорова — сума синусоїд кратних частот",
                  size=11, color=MUTED))

    # спектр амплітуд 1/n (стовпчики) — звідки беруться «гармоніки»
    sx0, base, bw, gap, maxh = 150, 372, 30, 70, 96
    p.append(text(W / 2, 286, "амплітуди гармонік пилки спадають як 1/n", size=13, bold=True))
    p.append(line(sx0 - 16, base, sx0 + 7 * gap + bw + 16, base, color=INK, sw=1.4))
    for i in range(8):
        n = i + 1
        frac = 1.0 / n
        cx = sx0 + i * gap
        h = maxh * frac
        c = INK if i == 0 else FIELD
        fillc = "#eef0f2" if i == 0 else "#eaf6ee"
        p.append(rect(cx, base - h, bw, h, fill=fillc, stroke=c, sw=1.6, rx=2))
        p.append(text(cx + bw / 2, base + 16, str(n), size=11, bold=True, color=c))
    p.append(text(sx0 + 3.5 * gap, base + 34, "номер гармоніки (кратність частоти)",
                  size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 444,
                      "Бернуллі стверджував, а Фур'є довів: будь-яку періодичну форму — навіть гостру пилку —\n"
                      "точно складають синусоїди кратних частот. Що більше доданків, то ближче до форми.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'fourier-builds-shape.svg'), W, H, *p,
           title="Як синусоїди кратних частот складають незграбну форму")


def power_terms_harmonics():
    """До вставки math-fourier-harmonics: чиста синусоїда проходить крізь
    степеневі члени кривої y(x). Кожен рядок — один член (a₁·x, a₂·x², a₃·x³):
    ліворуч що він робить із синусоїдою, праворуч який спектр-стовпчики дає.
    Видно правило: член n-го степеня доводить спектр рівно до n-ої гармоніки."""
    W, H = 760, 470
    p = []

    def sine_through(cx, cy, ww, amp, freq, fn, col, sw=2.2):
        N = 110
        pts = []
        for k in range(N + 1):
            u = math.sin(2 * math.pi * freq * k / N)
            v = fn(u)
            xx = cx + ww * k / N
            pts.append((xx, cy - v * amp))
        return _poly(pts, col, sw=sw)

    rows = [
        ("лінійний член  a₁·x",
         lambda u: u,                          # синус лишається синусом
         False, [("1", 1.00)],
         "форма ціла → лише 1-ша гармоніка", FIELD),
        ("квадрат  a₂·x²",
         lambda u: 2 * u * u - 1,              # невід'ємний двогорбий, центрований для показу
         True, [("0", 0.55), ("2", 0.55)],
         "постійна + 2-га гармоніка", POS),
        ("куб  a₃·x³",
         lambda u: u * u * u,                  # непарний, симетричний
         False, [("1", 0.62), ("3", 0.40)],
         "1-ша + 3-тя гармоніка", NEG),
    ]

    row_h = 116
    y_top = 80
    sx0 = 472          # ліва межа спектра
    gap = 46           # крок між позиціями гармонік
    bw = 26            # ширина стовпчика
    maxh = 62          # макс. висота стовпчика

    for ri, (title, fn, even, spec, note, col) in enumerate(rows):
        cy = y_top + ri * row_h
        p.append(text(40, cy - 38, title, size=14, bold=True, color=col, anchor="start"))

        # форма «синус крізь член» ліворуч
        gx, gw = 60, 196
        amp = 28
        p.append(line(gx - 6, cy, gx + gw + 6, cy, color=MUTED, sw=1.0, dash="2 3"))
        p.append(sine_through(gx, cy, gw, amp, 1.35, fn, col))
        p.append(text(gx + gw / 2, cy + 48, note, size=11, color=col))

        # стрілка «дає»
        p.append(arrow(gx + gw + 16, cy, sx0 - 22, cy, color=MUTED, sw=1.6))

        # спектр праворуч: позиції 0..3, наявні — кольором, відсутні — сірим підписом
        base = cy + 38
        p.append(line(sx0 - 12, base, sx0 + 3 * gap + bw + 12, base, color=INK, sw=1.4))
        present = {lbl: h for lbl, h in spec}
        for i, lbl in enumerate(["0", "1", "2", "3"]):
            bx = sx0 + i * gap
            if lbl in present:
                h = max(3, maxh * present[lbl])
                fillc = ("#eef7f0" if col == FIELD else
                         "#fdecea" if col == POS else "#eaf0fd")
                p.append(rect(bx, base - h, bw, h, fill=fillc, stroke=col, sw=1.7, rx=2))
                p.append(text(bx + bw / 2, base + 15, lbl, size=11, bold=True, color=col))
            else:
                p.append(text(bx + bw / 2, base + 15, lbl, size=11, color="#c4c9d0"))
        if ri == len(rows) - 1:
            p.append(text(sx0 + 1.5 * gap, base + 32,
                          "номер гармоніки (0 = постійна)", size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 438,
                      "Кожен степеневий член доводить спектр РІВНО до своєї гармоніки:\n"
                      "квадрат → 2-га, куб → 3-тя; парність члена = парність гармонік.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'power-terms-harmonics.svg'), W, H, *p,
           title="Степеневі члени кривої y(x) як фабрика гармонік")


if __name__ == '__main__':
    curve_makes_harmonics()
    even_odd_harmonics()
    fourier_builds_shape()
    power_terms_harmonics()
    print("OK: 4 figures ->", OUT)
