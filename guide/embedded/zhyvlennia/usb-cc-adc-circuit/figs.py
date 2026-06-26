# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # лінія CC — теплий акцент


# ── pipeline: весь тракт читання CC ──────────────────────────────────────────
# Ідея: від ноги CC до бюджету струму — п'ять ланок, кожна лікує свою болячку.
# Аналоговий бік (RC) і цифровий бік (усереднення/гістерезис/дебаунс) разом.

def fig_pipeline():
    W, H = 880, 320
    p = []

    # джерело: дільник на CC
    usbx = 70
    p.append(text(usbx, 95, "USB-C", size=11, color=GOLD, bold=True))
    p.append(text(usbx, 112, "лінія CC", size=9, color=MUTED))
    p.append(line(usbx, 130, usbx, 230, color=GOLD, sw=2.4))
    p.append(text(usbx - 4, 250, "Rd 5.1к", size=9, color=MUTED, anchor="middle"))

    stages = [
        ("RC-фільтр", "на нозі CC", "глушить ВЧ-наводку", "#fff7e6", GOLD),
        ("АЦП", "повільна вибірка", "не вантажить дільник", "#eef3fb", NEG),
        ("Усереднення", "N відліків", "прибирає випадковий шум", "#eef3fb", NEG),
        ("Гістерезис", "пороги вгору/вниз", "не дрижить на межі", "#eafaf0", FIELD),
        ("Дебаунс", "M однакових поспіль", "чекає сталого рівня", "#eafaf0", FIELD),
    ]
    x = 150
    bw, gap = 132, 14
    y = 150
    prev_r = usbx
    for i, (lab, sub, foot, fill, col) in enumerate(stages):
        b = fitbox(x, y - 32, bw, 64, lab + "\n" + sub, size=12, bold=True,
                   color=col, fill=fill, stroke=col, sw=1.8)
        p.append(b)
        p.append(text(x + bw / 2, y + 52, foot, size=9, color=MUTED, italic=True))
        p.append(arrow(prev_r + 2, y, x - 2, y, color=INK, sw=1.7))
        prev_r = x + bw
        x += bw + gap

    # підпис аналог/цифра
    p.append(line(150, 235, 150 + bw, 235, color=GOLD, sw=1.0, dash="3 3"))
    p.append(text(150 + bw / 2, 252, "аналоговий бік", size=9, color=GOLD, italic=True))
    p.append(line(150 + bw + gap, 235, x - gap, 235, color=NEG, sw=1.0, dash="3 3"))
    p.append(text((150 + bw + gap + x - gap) / 2, 252, "цифровий бік (прошивка)", size=9, color=NEG, italic=True))

    # вихід
    p.append(arrow(prev_r + 2, y, W - 70, y, color=POS, sw=2.0))
    ob, _, _ = textbox(W - 70, y, "Бюджет\nструму", size=11, bold=True,
                       color=POS, fill="#fdecea", stroke=POS, sw=2, min_w=96)
    p.append(ob)

    p.append(text(W / 2, H - 16,
                  "один відлік бреше; правду дає весь ланцюг — фільтр, усереднення, гістерезис, дебаунс",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Тракт читання CC: від ноги роз'єму до дозволеного струму")


# ── bands: три смуги декодування на осі напруги + зони невизначеності ─────────
# Ідея: рівні стоять на 0.41 / 0.92 / 1.68 В; біля кожної межі — вузька зона,
# де один відлік легко перескакує — саме там потрібен гістерезис.

def fig_bands():
    W, H = 820, 330
    p = []
    x0, x1 = 90, W - 60
    ay = 210
    vmax = 2.0

    def vx(v):
        return x0 + (x1 - x0) * (v / vmax)

    # вісь
    p.append(line(x0, ay, x1, ay, color=INK, sw=2))
    for v in [0, 0.5, 1.0, 1.5, 2.0]:
        p.append(line(vx(v), ay - 5, vx(v), ay + 5, color=INK, sw=1.4))
        p.append(text(vx(v), ay + 22, "%.1f" % v, size=10, color=MUTED))
    p.append(text(x1, ay + 40, "U(CC), В", size=11, color=INK, bold=True, anchor="end"))

    # смуги (низ → верх): висить / Default / 1.5 А / 3 А
    bands = [
        (0.00, 0.20, "висить\n(нема джерела)", "#f0f0f0", MUTED, "0 мА"),
        (0.20, 0.66, "Default USB\n≈0.41 В", "#eef3fb", NEG, "0.5/0.9 А"),
        (0.66, 1.23, "1.5 А\n≈0.92 В", "#fff7e6", GOLD, "1.5 А"),
        (1.23, 2.00, "3.0 А\n≈1.68 В", "#eafaf0", FIELD, "3 А = 15 Вт"),
    ]
    top = 70
    for lo, hi, lab, fill, col, cur in bands:
        xl, xr = vx(lo), vx(hi)
        p.append(rect(xl, top, xr - xl, ay - top, fill=fill, stroke=col, sw=1.6))
        p.append(mtext((xl + xr) / 2, top + 38, lab, size=11, color=col, bold=True))
        p.append(text((xl + xr) / 2, ay - 14, cur, size=10, color=col, bold=True))

    # пороги-межі + зони дрижання
    for vth in [0.66, 1.23]:
        p.append(line(vx(vth), top - 8, vx(vth), ay, color=POS, sw=1.6, dash="4 3"))
        # вузька «небезпечна» зона навколо порога
        p.append(rect(vx(vth) - 9, top, 18, ay - top, fill="#fdecea", stroke="none", sw=0))
    p.append(text(vx(0.66), top - 16, "поріг", size=9, color=POS, bold=True))
    p.append(text(vx(1.23), top - 16, "поріг", size=9, color=POS, bold=True))

    p.append(text(W / 2, H - 18,
                  "червоні смужки — околиці порогів: один зашумлений відлік перекидає рівень туди-сюди",
                  size=11, color=POS, italic=True))
    render(os.path.join(OUT, "bands.svg"), W, H, *p,
           title="Три смуги дозволеного струму на осі напруги CC")


# ── loading: чому наївне читання дає НЕ ту напругу ────────────────────────────
# Ідея: вхідний конденсатор АЦП за вибірку «висмоктує» заряд із високоомного
# дільника CC; швидка вибірка → занижене число. Ліки: повільна вибірка / RC / буфер.

def fig_loading():
    W, H = 820, 360
    p = []

    def panel(x0, title, col, ok):
        p.append(text(x0 + 170, 64, title, size=13, color=col, bold=True))
        # дільник CC
        nodey = 150
        p.append(text(x0 + 30, 110, "CC", size=10, color=GOLD, bold=True))
        p.append(line(x0 + 40, 120, x0 + 40, nodey, color=GOLD, sw=2))
        p.append(circle(x0 + 40, nodey, 4, fill=GOLD, stroke=GOLD))
        p.append(text(x0 + 40, nodey + 40, "дільник\n5.1к (високоомний)", size=9, color=MUTED))
        p.append(line(x0 + 40, nodey, x0 + 40, nodey + 22, color=MUTED, sw=1.4))
        # шлях до АЦП
        p.append(line(x0 + 40, nodey, x0 + 150, nodey, color=INK, sw=1.6))
        # ключ вибірки + Csh
        sw_x = x0 + 150
        p.append(text(sw_x, nodey - 16, "ключ", size=9, color=MUTED))
        p.append(line(sw_x, nodey, sw_x + 26, nodey - 14, color=INK, sw=1.8))  # ключ
        p.append(line(sw_x + 30, nodey, sw_x + 30, nodey + 30, color=INK, sw=1.6))
        p.append(line(sw_x + 18, nodey + 30, sw_x + 42, nodey + 30, color=INK, sw=2.4))
        p.append(line(sw_x + 22, nodey + 38, sw_x + 38, nodey + 38, color=INK, sw=2.4))
        p.append(text(sw_x + 58, nodey + 30, "Csh", size=9, color=NEG, bold=True))
        p.append(text(sw_x + 50, nodey, "АЦП", size=10, color=NEG, bold=True))
        # вердикт
        vcol = FIELD if ok else POS
        vb = fitbox(x0 + 30, 250, 290, 56,
                    ("Повільна вибірка / RC / буфер:\nдільник встигає дозарядити Csh → вірне число"
                     if ok else
                     "Швидка вибірка:\nCsh висмоктує заряд → ЗАНИЖЕНА напруга, хибний рівень"),
                    size=10, bold=True, color=vcol, fill=("#eafaf0" if ok else "#fdecea"),
                    stroke=vcol, sw=1.6)
        p.append(vb)

    panel(30, "Наївно: швидкий відлік", POS, ok=False)
    panel(430, "Правильно: дати час", FIELD, ok=True)
    p.append(line(W / 2, 60, W / 2, H - 40, color=MUTED, sw=1.0, dash="4 4"))

    render(os.path.join(OUT, "loading.svg"), W, H, *p,
           title="Високоомний дільник + вхід АЦП: чому квапливе читання бреше")


# ── hysteresis: два пороги проти дрижання на межі ────────────────────────────
# Ідея: напруга CC гуляє навколо межі 0.92 В; з одним порогом рівень скаче;
# з парою порогів (вгору 0.99 / вниз 0.85) рішення залипає, доки реально не змінилось.

def fig_hysteresis():
    W, H = 820, 380
    p = []
    x0, x1 = 70, W - 60
    yb, yt = 300, 90
    n = 120

    import math
    # сигнал: середнє трохи нижче порога 0.92, з шумом перетинає його
    def sig(i):
        t = i / n
        base = 0.90 + 0.05 * math.sin(t * 6.0)
        noise = 0.045 * math.sin(t * 47.0) + 0.03 * math.sin(t * 113.0 + 1.0)
        return base + noise

    vmin, vmax = 0.7, 1.15

    def X(i):
        return x0 + (x1 - x0) * (i / n)

    def Y(v):
        return yb - (yb - yt) * ((v - vmin) / (vmax - vmin))

    # пороги
    vth = 0.92
    vup, vdn = 0.99, 0.85
    p.append(line(x0, Y(vth), x1, Y(vth), color=MUTED, sw=1.0, dash="2 3"))
    p.append(text(x1 + 4, Y(vth) + 4, "межа 0.92", size=9, color=MUTED, anchor="start"))
    p.append(line(x0, Y(vup), x1, Y(vup), color=POS, sw=1.2, dash="5 3"))
    p.append(text(x1 + 4, Y(vup) + 4, "вгору 0.99", size=9, color=POS, anchor="start", bold=True))
    p.append(line(x0, Y(vdn), x1, Y(vdn), color=NEG, sw=1.2, dash="5 3"))
    p.append(text(x1 + 4, Y(vdn) + 4, "вниз 0.85", size=9, color=NEG, anchor="start", bold=True))
    # смуга гістерезису
    p.append(rect(x0, Y(vup), x1 - x0, Y(vdn) - Y(vup), fill="#fbf3e0", stroke="none", sw=0))
    p.append(text(x0 + 8, Y(vth) - 6, "смуга гістерезису", size=9, color=GOLD, italic=True, anchor="start"))

    # крива напруги
    pts = " ".join("%.1f,%.1f" % (X(i), Y(sig(i))) for i in range(n + 1))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts, INK))

    # рішення з одним порогом (вгорі) — дрижить
    yd1 = 60
    p.append(text(x0, yd1 - 6, "один поріг → дрижить:", size=10, color=POS, bold=True, anchor="start"))
    state = 0
    seg = []
    for i in range(n + 1):
        s = 1 if sig(i) > vth else 0
        seg.append((X(i), s))
    # намалюємо як вертикальні мітки перемикань
    for i in range(1, n + 1):
        if seg[i][1] != seg[i - 1][1]:
            p.append(line(seg[i][0], yd1, seg[i][0], yd1 + 14, color=POS, sw=1.4))

    # рішення з гістерезисом (внизу осі) — стабільне
    yd2 = 330
    p.append(text(x0, yd2 + 26, "гістерезис → стабільно:", size=10, color=FIELD, bold=True, anchor="start"))
    st = 0
    flips = 0
    last = x0
    for i in range(1, n + 1):
        v = sig(i)
        ns = st
        if st == 0 and v > vup:
            ns = 1
        elif st == 1 and v < vdn:
            ns = 0
        if ns != st:
            p.append(line(X(i), yd2 + 4, X(i), yd2 + 18, color=FIELD, sw=1.6))
            flips += 1
            st = ns
    p.append(text(x1, yd2 + 26, "перемикань: %d" % flips, size=9, color=FIELD, anchor="end", italic=True))

    p.append(text(W / 2, H - 12,
                  "та сама зашумлена напруга: з одним порогом рівень скаче, з парою порогів — залипає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hysteresis.svg"), W, H, *p,
           title="Гістерезис на межі рівнів: пара порогів убиває дрижання")


# ── debounce: бовтанка при втиканні + N однакових відліків ───────────────────
# Ідея: під час встромляння CC «бовтається» мілісекунди; вмикати навантаження
# можна лише коли рівень M разів поспіль однаковий.

def fig_debounce():
    W, H = 820, 320
    p = []
    x0, x1 = 70, W - 60
    yb, yt = 230, 80

    import math
    n = 140

    def X(i):
        return x0 + (x1 - x0) * (i / n)

    # фаза 1: висить (0), фаза бовтанки, фаза стабільних ~1.68 В (3 А)
    def sig(i):
        if i < 30:
            return 0.02 + 0.01 * math.sin(i)
        if i < 70:
            # бовтанка при контакті
            return 0.9 + 0.8 * abs(math.sin(i * 0.9)) * (1 - (i - 30) / 60.0)
        return 1.68 + 0.02 * math.sin(i * 0.5)

    vmin, vmax = 0.0, 2.0

    def Y(v):
        return yb - (yb - yt) * ((v - vmin) / (vmax - vmin))

    # осі/пороги
    p.append(line(x0, yb, x1, yb, color=INK, sw=1.6))
    p.append(line(x0, Y(1.23), x1, Y(1.23), color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(x1 + 4, Y(1.23) + 4, "поріг 3 А", size=9, color=MUTED, anchor="start"))

    pts = " ".join("%.1f,%.1f" % (X(i), Y(sig(i))) for i in range(n + 1))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts, GOLD))

    # зони
    def zone(a, b, lab, col, fill):
        p.append(rect(X(a), yt - 6, X(b) - X(a), yb - yt + 6, fill=fill, stroke="none", sw=0))
        p.append(text((X(a) + X(b)) / 2, yt - 14, lab, size=10, color=col, bold=True))

    zone(0, 30, "висить", MUTED, "#f3f3f3")
    zone(30, 70, "бовтанка контакту", POS, "#fdecea")
    zone(70, n, "стабільно 3 А", FIELD, "#eafaf0")

    # точка ухвалення рішення — після M однакових відліків у стабільній зоні
    dec = 88
    p.append(line(X(dec), yt - 6, X(dec), yb + 24, color=FIELD, sw=1.8, dash="5 3"))
    p.append(text(X(dec), yb + 40, "M однакових поспіль → вмикаємо навантаження",
                  size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 12,
                  "поки рівень бовтається, рішення відкладене; дію дозволяємо лише на сталому рівні",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "debounce.svg"), W, H, *p,
           title="Дебаунс при втиканні: дій лише після M однакових відліків")


# ── thr_models: два способи рахунку дають ті самі круглі числа ────────────────
# Ідея: дільник Rp/Rd при ~5 В і модель струмового джерела I·Rd сходяться на
# 0.41 / 0.92 / 1.68 В — тому числа й виходять рівними.

def fig_thr_models():
    W, H = 820, 330
    p = []
    rows = [
        ("Default", "56 кОм", "80 мкА", 0.417, 0.408, "≈0.41 В", NEG),
        ("1.5 А",   "22 кОм", "180 мкА", 0.941, 0.918, "≈0.92 В", FIELD),
        ("3.0 А",   "10 кОм", "330 мкА", 1.689, 1.683, "≈1.68 В", GOLD),
    ]
    colx = [70, 250, 470, 690]
    p.append(text(colx[0] + 60, 64, "рівень", size=12, color=MUTED, bold=True))
    p.append(text(colx[1] + 20, 50, "дільник Rp/Rd", size=12, color=NEG, bold=True))
    p.append(text(colx[1] + 20, 66, "при Vпідт ≈ 5 В", size=10, color=MUTED))
    p.append(text(colx[2] + 20, 50, "струмове джерело", size=12, color=POS, bold=True))
    p.append(text(colx[2] + 20, 66, "I · Rd (Rd = 5.1 кОм)", size=10, color=MUTED))
    p.append(text(colx[3] + 20, 64, "номінал", size=12, color=INK, bold=True))
    y = 110
    for lvl, rp, ia, vdiv, vcs, nom, col in rows:
        b, w, h = textbox(colx[0] + 50, y, lvl, size=13, bold=True, color=col,
                          fill="#fff", stroke=col, sw=1.8, min_w=110)
        p.append(b)
        p.append(text(colx[1] + 70, y - 6, "Rp = " + rp, size=11, color=INK))
        p.append(text(colx[1] + 70, y + 12, "%.3f В" % vdiv, size=12, color=NEG, bold=True))
        p.append(text(colx[2] + 80, y - 6, "I = " + ia, size=11, color=INK))
        p.append(text(colx[2] + 80, y + 12, "%.3f В" % vcs, size=12, color=POS, bold=True))
        # стрілки до спільного номіналу
        p.append(arrow(colx[1] + 150, y, colx[3] + 4, y, color=MUTED, sw=1.4))
        p.append(arrow(colx[2] + 170, y, colx[3] + 4, y, color=MUTED, sw=1.4))
        nb, nw, nh = textbox(colx[3] + 60, y, nom, size=13, bold=True, color=col,
                             fill="#f4f6f8", stroke=col, sw=1.8, min_w=92)
        p.append(nb)
        y += 70
    p.append(text(W / 2, H - 14,
                  "обидві моделі сходяться: круглі 0.41 / 0.92 / 1.68 В — не випадковість, а I·Rd",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "thr_models.svg"), W, H, *p,
           title="Звідки беруться напруги на CC: дільник і струмове джерело")


# ── thr_spread: розкид зсуває рівні; пороги живуть у щілинах між смугами ──────
# Ідея: кожен номінал розпливається у смугу від допуску Rp/Rd/Vпідт. Три пороги
# (0.2/0.66/1.23) сидять у зазорах між сусідніми смугами із запасом з обох боків.

def fig_thr_spread():
    W, H = 880, 340
    p = []
    x0, x1 = 90, W - 60
    vmin, vmax = 0.0, 2.15
    axy = 250

    def X(v):
        return x0 + (x1 - x0) * ((v - vmin) / (vmax - vmin))

    # вісь
    p.append(line(x0, axy, x1, axy, color=INK, sw=1.8))
    for v in [0.0, 0.5, 1.0, 1.5, 2.0]:
        p.append(line(X(v), axy - 4, X(v), axy + 4, color=INK, sw=1.4))
        p.append(text(X(v), axy + 20, "%.1f" % v, size=10, color=MUTED))
    p.append(text(x1, axy + 38, "напруга CC, В", size=10, color=MUTED, anchor="end"))

    # смуги розкиду (струмова модель, гарантована спеком): lo, hi, nom, label, col
    bands = [
        (0.294, 0.539, 0.41, "Default", NEG, 130),
        (0.760, 1.091, 0.92, "1.5 А",   FIELD, 95),
        (1.394, 1.999, 1.68, "3.0 А",   GOLD, 130),
    ]
    bh = 26
    for lo, hi, nom, lab, col, laby in bands:
        p.append(rect(X(lo), axy - bh / 2, X(hi) - X(lo), bh, fill=col, stroke=col, sw=1.2, rx=4))
        # світліша заливка
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="white" fill-opacity="0.55"/>'
                 % (X(lo), axy - bh / 2, X(hi) - X(lo), bh))
        p.append(line(X(nom), axy - bh / 2 - 4, X(nom), axy + bh / 2 + 4, color=col, sw=2.4))
        p.append(text((X(lo) + X(hi)) / 2, laby, lab, size=12, color=col, bold=True))
        p.append(text((X(lo) + X(hi)) / 2, laby + 16, "%.2f…%.2f" % (lo, hi), size=9, color=MUTED))
        p.append(text(X(nom), laby + 32 if laby < axy else laby - 30, "ном %.2f" % nom,
                      size=9, color=col, italic=True))

    # пороги в зазорах
    for vth, lab in [(0.20, "0.20"), (0.66, "0.66"), (1.23, "1.23")]:
        p.append(line(X(vth), axy - 70, X(vth), axy + bh / 2 + 6, color=POS, sw=1.8, dash="5 3"))
        p.append(text(X(vth), axy - 76, lab, size=11, color=POS, bold=True))
    p.append(text(X(0.20), axy - 92, "поріг", size=9, color=POS))
    p.append(text(X(0.66), axy - 92, "поріг", size=9, color=POS))
    p.append(text(X(1.23), axy - 92, "поріг", size=9, color=POS))

    # «висить» зліва
    p.append(text(X(0.10), 130, "висить", size=11, color=MUTED, bold=True))
    p.append(text(X(0.10), 146, "0 В", size=9, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "допуск Rp/Rd/Vпідт розпливає кожен рівень у смугу; пороги сидять у зазорах між смугами",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "thr_spread.svg"), W, H, *p,
           title="Розкид рівнів і пороги в зазорах між смугами")


# ── thr_scales: ланцюг масштабів біля порога (квант ≪ шум < смуга < зазор) ────
# Ідея: чотири довжини в напрузі, складені згори вниз, показують ланцюг нерівностей,
# який мусить виконуватись, щоб читання було надійним.

def fig_thr_scales():
    W, H = 820, 360
    p = []
    x0 = 320
    scale = 1400.0  # px на вольт (щоб дрібні величини було видно)
    items = [
        ("Квант АЦП (12 біт, 3.3 В)", 0.0008, NEG, "1 LSB ≈ 0.8 мВ"),
        ("Залишковий шум (розмах)",   0.080, POS, "±0.04 В після RC+усереднення"),
        ("Смуга гістерезису",          0.140, GOLD, "вгору − вниз = 0.14 В"),
        ("Зазор до сусідньої смуги",   0.221, FIELD, "Default.max → 1.5А.min"),
    ]
    y = 80
    gap = 70
    for lab, val, col, note in items:
        w = max(2.0, val * scale)
        p.append(rect(x0, y - 12, w, 24, fill=col, stroke=col, sw=1.2, rx=4))
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="white" fill-opacity="0.5"/>'
                 % (x0, y - 12, w, 24))
        p.append(text(x0 - 12, y - 2, lab, size=12, color=col, bold=True, anchor="end"))
        p.append(text(x0 - 12, y + 14, note, size=9, color=MUTED, anchor="end"))
        p.append(text(x0 + w + 10, y + 4, "%.0f мВ" % (val * 1000), size=11, color=col,
                      bold=True, anchor="start"))
        y += gap

    # знаки нерівностей між брусками
    rel = ["≪", "<", "<"]
    yy = 80
    for r in rel:
        p.append(text(x0 - 200, yy + gap / 2 + 4, r, size=20, color=INK, bold=True))
        yy += gap

    p.append(text(W / 2, H - 16,
                  "ланцюг масштабів: квант ≪ шум < смуга гістерезису < зазор між смугами",
                  size=11, color=INK, italic=True))
    p.append(text(W / 2, H - 34,
                  "поки нерівність тримається — читання надійне; зламалась ланка — звідти й баг",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "thr_scales.svg"), W, H, *p,
           title="Чотири масштаби напруги біля порога CC")


# ── states: машина станів драйвера читача CC (proj-cc-reader) ─────────────────
# Ідея: три стани життя під'єднання й переходи між ними. Угору — поява й сталий
# рівень (вибір активної CC + дебаунс); спільна зворотна стрілка — від'єднання.

def fig_states():
    W, H = 860, 360
    p = []

    # три стани як рамки в ряд
    cy = 150
    boxes = [
        (150, "DETACHED", "джерела нема\nCC ≈ 0 В", "#f4f6f8", MUTED),
        (430, "DEBOUNCING", "обрано CC1/CC2\nчекаємо M однакових", "#fff7e6", GOLD),
        (710, "ATTACHED", "рівень сталий\nнавантаження ON", "#eafaf0", FIELD),
    ]
    bw, bh = 170, 70
    cxs = []
    for cx, lab, sub, fill, col in boxes:
        cxs.append(cx)
        p.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, lab + "\n" + sub,
                        size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.9))

    # перехід DETACHED → DEBOUNCING (поява)
    p.append(arrow(cxs[0] + bw / 2, cy - 14, cxs[1] - bw / 2, cy - 14, color=FIELD, sw=2.2))
    p.append(text((cxs[0] + cxs[1]) / 2, cy - 24, "напруга > порога присутності",
                  size=10, color=FIELD))
    p.append(text((cxs[0] + cxs[1]) / 2, cy - 38, "(фіксуємо активну лінію)",
                  size=9, color=MUTED))

    # перехід DEBOUNCING → ATTACHED (сталий рівень)
    p.append(arrow(cxs[1] + bw / 2, cy - 14, cxs[2] - bw / 2, cy - 14, color=FIELD, sw=2.2))
    p.append(text((cxs[1] + cxs[2]) / 2, cy - 24, "M відліків поспіль, рівень ≠ нема",
                  size=10, color=FIELD))
    p.append(text((cxs[1] + cxs[2]) / 2, cy - 38, "→ подія on_attach", size=9, color=MUTED))

    # самопетля на ATTACHED: переуклали рівень
    lx = cxs[2]
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (lx + 30, cy - bh / 2, lx + 95, cy - 70, lx - 30, cy - 70, lx - 22, cy - bh / 2,
                MUTED))
    p.append(text(lx + 36, cy - 78, "рівень змінився → on_level", size=9, color=MUTED))

    # спільна зворотна шина: ATTACHED і DEBOUNCING → DETACHED (від'єднання)
    ry = cy + bh / 2 + 60
    # вертикалі вниз від двох робочих станів
    p.append(line(cxs[1], cy + bh / 2, cxs[1], ry, color=POS, sw=2.0))
    p.append(line(cxs[2], cy + bh / 2, cxs[2], ry, color=POS, sw=2.0))
    # горизонтальна шина до-під DETACHED
    p.append(line(cxs[0], ry, cxs[2], ry, color=POS, sw=2.0))
    p.append(arrow(cxs[0], ry, cxs[0], cy + bh / 2, color=POS, sw=2.2))
    p.append(text((cxs[0] + cxs[2]) / 2, ry + 20,
                  "напруга на активній лінії < порога присутності  →  on_detach, навантаження OFF",
                  size=10, color=POS))

    p.append(text(W / 2, H - 14,
                  "уся логіка живе в одному poll(): без блокувань, callback — з контексту poll",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "states.svg"), W, H, *p,
           title="Машина станів драйвера читача CC")


if __name__ == "__main__":
    fig_pipeline()
    fig_bands()
    fig_loading()
    fig_hysteresis()
    fig_debounce()
    fig_thr_models()
    fig_thr_spread()
    fig_thr_scales()
    fig_states()
    print("OK: figures written to", OUT)
