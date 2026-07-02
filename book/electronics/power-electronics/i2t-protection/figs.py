# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HOT  = "#c0392b"   # струм / енергія
COOL = "#2457d6"
OK   = "#27ae60"


# ── 1. Що таке доза I²t: площа під i²(t) ────────────────────────────────────
def fig_dose():
    W, H = 720, 380
    x0, y0 = 90, 300          # початок осей
    axw, axh = 560, 240
    frags = []

    # осі
    frags.append(line(x0, y0, x0 + axw, y0, INK, 2))          # час
    frags.append(line(x0, y0, x0, y0 - axh, INK, 2))          # струм
    frags.append(arrow(x0 + axw, y0, x0 + axw + 14, y0, INK, 2))
    frags.append(arrow(x0, y0 - axh, x0, y0 - axh - 14, INK, 2))
    frags.append(text(x0 + axw + 6, y0 + 22, "час t", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, y0 - axh - 4, "струм i", size=13, color=MUTED, anchor="start"))

    # прямокутний імпульс аварійного струму: короткий і високий
    t1, t2 = x0 + 150, x0 + 250
    ipk = y0 - 200
    # заливка області під i² (енергія) — просто прямокутник під імпульсом
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.16"/>'
                 % (t1, ipk, t2 - t1, y0 - ipk, HOT))
    frags.append(line(x0, y0, t1, y0, HOT, 3))
    frags.append(line(t1, y0, t1, ipk, HOT, 3))
    frags.append(line(t1, ipk, t2, ipk, HOT, 3))
    frags.append(line(t2, ipk, t2, y0, HOT, 3))
    frags.append(line(t2, y0, x0 + axw - 20, y0, HOT, 3))

    # позначки I та t
    frags.append(line(t1, ipk, x0, ipk, MUTED, 1, dash="4 4"))
    frags.append(text(x0 - 8, ipk + 4, "I", size=15, color=HOT, anchor="end", bold=True))
    frags.append(line(t1, y0 + 8, t1, y0 + 26, MUTED, 1))
    frags.append(line(t2, y0 + 8, t2, y0 + 26, MUTED, 1))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
                 % (t1, y0 + 20, t2, y0 + 20, MUTED))
    frags.append(text((t1 + t2) / 2, y0 + 40, "t", size=15, color=INK, bold=True))

    # напис у центрі області
    frags.append(text((t1 + t2) / 2, (ipk + y0) / 2 + 5, "I² · t", size=22, color=HOT, bold=True))

    b, _, _ = textbox(x0 + 430, y0 - 150,
                      ["теплова доза,", "що дісталася", "провіднику:", "∫ i² dt  (А²·с)"],
                      size=13, fill="#fdf0ee", stroke=HOT)
    frags.append(b)

    render(os.path.join(OUT, "i2t-dose.svg"), W, H, *frags,
           title="I²t — накопичена теплова доза струму")


# ── 2. Правило узгодження: I²t запобіжника < I²t приладу ─────────────────────
def fig_coordination():
    W, H = 720, 340
    frags = []
    xL = 60
    barw = 560
    # три горизонтальні смуги: withstand приладу (найдовша), clearing, melting
    def bar(cx_y, frac, color, label, sub):
        w = barw * frac
        frags.append(rect(xL, cx_y - 20, w, 40, fill=color + "22" if len(color) == 7 else color, stroke=color, sw=2))
        frags.append(text(xL + 10, cx_y + 5, label, size=14, color=INK, anchor="start", bold=True))
        frags.append(text(xL + w + 10, cx_y + 5, sub, size=12, color=MUTED, anchor="start"))

    y1, y2, y3 = 110, 185, 260
    # прилад — найбільша стійкість
    frags.append(rect(xL, y1 - 22, barw, 44, fill="#eaf7ef", stroke=OK, sw=2.5))
    frags.append(text(xL + 12, y1 + 5, "I²t приладу (withstand)", size=14, color=INK, anchor="start", bold=True))
    frags.append(text(xL + barw - 12, y1 + 5, "скільки витримає тиристор/діод", size=11, color=MUTED, anchor="end"))

    # clearing — має бути коротшим
    wc = barw * 0.62
    frags.append(rect(xL, y2 - 20, wc, 40, fill="#fdecea", stroke=HOT, sw=2.5))
    frags.append(text(xL + 12, y2 + 5, "I²t clearing запобіжника", size=13, color=INK, anchor="start", bold=True))
    # melting всередині clearing
    wm = barw * 0.40
    frags.append(rect(xL, y2 - 20, wm, 40, fill="#f7c9c2", stroke=HOT, sw=1.5))
    frags.append(text(xL + wm / 2, y2 - 30, "melting", size=11, color=HOT))
    frags.append(text(xL + (wm + wc) / 2, y2 - 30, "arcing", size=11, color=HOT))

    # шкала-стрілка порівняння
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
                 % (xL + wc, y2 - 24, xL + wc, y1 + 24, OK))

    # підпис-нерівність
    b, _, _ = textbox(W / 2, y3 + 5,
                      "I²t clearing (запобіжник)  <  I²t withstand (прилад)",
                      size=15, fill="#f4f6f8", stroke=INK, bold=True)
    frags.append(b)
    frags.append(text(W / 2, y3 + 42, "запобіжник мусить згоріти РАНІШЕ, ніж прилад дійде до межі",
                      size=12, color=MUTED))

    render(os.path.join(OUT, "i2t-coordination.svg"), W, H, *frags,
           title="Узгодження: запобіжник пропускає менше, ніж витримає прилад")


# ── 3. Час-струмова крива: адіабатична (плоский I²t) vs повільна зона ────────
def fig_curve():
    W, H = 720, 380
    x0, y0 = 90, 310
    axw, axh = 560, 250
    frags = []
    frags.append(line(x0, y0, x0 + axw, y0, INK, 2))
    frags.append(line(x0, y0, x0, y0 - axh, INK, 2))
    frags.append(arrow(x0 + axw, y0, x0 + axw + 14, y0, INK, 2))
    frags.append(arrow(x0, y0 - axh, x0, y0 - axh - 14, INK, 2))
    frags.append(text(x0 + axw + 6, y0 + 22, "струм I (лог)", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 6, y0 - axh - 4, "час до згоряння t (лог)", size=13, color=MUTED, anchor="start"))

    # крива t(I): при малих струмах — майже вертикальна (тепло встигає піти),
    # далі спадає; праворуч виходить на пологу пряму нахилу −2 (I²t = const у лог-лог).
    pts = []
    for i in range(0, 101):
        fx = i / 100.0
        X = x0 + 40 + fx * (axw - 80)
        # струм росте зліва направо; час спадає. Ліворуч — коліно (майже стеля).
        # проста форма: t ~ 1/(I-Imin)^k у лівій частині, потім прямий нахил.
        u = 0.12 + fx * 0.88
        t = 1.0 / (u ** 2)               # у лог-лог це пряма нахилу -2 → адіабата
        # додати «коліно» ліворуч: підняти час різко коло малих струмів
        knee = 1.0 / max(u - 0.10, 0.02)
        val = t + knee * 2.2
        Y = y0 - (math.log10(val) / math.log10(230)) * (axh - 30)
        pts.append((X, Y))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path, HOT))

    # позначити дві зони
    # ліва зона — повільна (тепло тече геть)
    frags.append(line(x0 + 175, y0, x0 + 175, y0 - axh, MUTED, 1.2, dash="5 5"))
    bl, _, _ = textbox(x0 + 90, y0 - axh + 46,
                       ["повільна зона:", "тепло встигає", "піти → I²t росте"],
                       size=12, fill="#eef1f4", stroke=MUTED)
    frags.append(bl)
    # права зона — адіабатична
    br, _, _ = textbox(x0 + 400, y0 - 70,
                       ["адіабатична зона:", "тепло не встигає піти", "I²t ≈ const  (t < ~10 мс)"],
                       size=12, fill="#fdf0ee", stroke=HOT)
    frags.append(br)

    render(os.path.join(OUT, "i2t-curve.svg"), W, H, *frags,
           title="Чому I²t стала лише на швидкому струмі")


# ── 4. Будова напівпровідникового запобіжника: срібний елемент із насічками ──
def fig_fuse_build():
    W, H = 720, 360
    frags = []
    # керамічний корпус
    bx, by, bw, bh = 70, 90, 580, 180
    frags.append(rect(bx, by, bw, bh, fill="#f3efe7", stroke="#8a7a5c", sw=2.5, rx=10))
    frags.append(text(bx + 12, by - 12, "керамічний корпус", size=12, color="#8a7a5c", anchor="start"))

    # кварцовий пісок — крапки-зерна всередині
    import random
    random.seed(7)
    grains = []
    for _ in range(150):
        gx = bx + 20 + random.random() * (bw - 40)
        gy = by + 18 + random.random() * (bh - 36)
        r = 1.3 + random.random() * 1.3
        grains.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#d9c9a3" opacity="0.55"/>' % (gx, gy, r))
    frags.append("".join(grains))
    frags.append(text(bx + bw - 12, by + bh - 12, "кварцовий пісок", size=12, color="#a08a5c", anchor="end"))

    # торцеві контакти (ножі/шайби)
    frags.append(rect(bx - 26, by + 30, 26, bh - 60, fill="#b0b0b8", stroke=INK, sw=1.5, rx=3))
    frags.append(rect(bx + bw, by + 30, 26, bh - 60, fill="#b0b0b8", stroke=INK, sw=1.5, rx=3))

    # срібна стрічка з насічками (звужена в кількох місцях)
    midy = by + bh / 2
    ribbon = []
    x = bx
    seg = (bw) / 10.0
    notch_at = [2, 4, 6, 8]      # де вужчі перемички
    full_h = 30
    thin_h = 10
    # верхня й нижня межа стрічки як ламана
    top_pts, bot_pts = [], []
    for i in range(11):
        xi = bx + i * seg
        # у точці насічки — вужче
        h = thin_h if (i in [2.5]) else full_h
        top_pts.append((xi, midy - full_h / 2))
        bot_pts.append((xi, midy + full_h / 2))
    # намалюємо як низку прямокутників-широких і вузьких перемичок
    for i in range(10):
        x0 = bx + i * seg
        if i in notch_at:
            # вузька перемичка посередині сегмента
            wnar = seg * 0.34
            frags.append(rect(x0, midy - full_h / 2, seg, full_h, fill="#e8e8ee", stroke="#c0c0c8", sw=1))
            frags.append(rect(x0 + (seg - wnar) / 2, midy - thin_h / 2, wnar, thin_h,
                              fill="#c8c8d0", stroke=INK, sw=1.4))
        else:
            frags.append(rect(x0, midy - full_h / 2, seg, full_h, fill="#e8e8ee", stroke="#c0c0c8", sw=1))
    # суцільна срібна лінія по центру, щоб читалось «елемент»
    frags.append(line(bx - 26, midy, bx + bw + 26, midy, "#9a9aa6", 2))
    frags.append(text(bx + bw / 2, by - 12, "срібна стрічка з насічками", size=13, color=INK, bold=True))

    # виноска на одну насічку
    ni = 4
    nx = bx + ni * seg + seg / 2
    frags.append(line(nx, midy - full_h / 2, nx, by + bh + 34, HOT, 1.4, dash="4 3"))
    b, _, _ = textbox(nx, by + bh + 54,
                      ["насічка — тонка перемичка:", "тут переріз найменший →", "тут елемент розплавиться першим"],
                      size=11, fill="#fdf0ee", stroke=HOT)
    frags.append(b)

    render(os.path.join(OUT, "fuse-build.svg"), W, H, *frags,
           title="Напівпровідниковий запобіжник зсередини")


# ── 5. Насічки → кілька дуг послідовно → дугова напруга гасить струм ─────────
def fig_arc_voltage():
    W, H = 720, 400
    x0, y0 = 90, 300
    axw, axh = 560, 230
    frags = []
    frags.append(line(x0, y0, x0 + axw, y0, INK, 2))
    frags.append(line(x0, y0, x0, y0 - axh, INK, 2))
    frags.append(arrow(x0 + axw, y0, x0 + axw + 14, y0, INK, 2))
    frags.append(arrow(x0, y0 - axh, x0, y0 - axh - 14, INK, 2))
    frags.append(text(x0 + axw + 6, y0 + 22, "час t", size=13, color=MUTED, anchor="end"))

    # рівень напруги мережі (пунктир)
    vsys = y0 - 90
    frags.append(line(x0, vsys, x0 + axw, vsys, MUTED, 1.4, dash="6 4"))
    frags.append(text(x0 + 6, vsys - 8, "напруга кола Uж", size=12, color=MUTED, anchor="start"))

    # струм: наростає, тоді запобіжник спрацював — різко вниз до нуля
    tmelt = x0 + 210
    ipk = y0 - 150
    ipath = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x0 + 10, y0 - 6, x0 + 120, y0 - 160, tmelt, ipk)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ipath, HOT))
    # після розплавлення струм швидко спадає
    down = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (tmelt, ipk, tmelt + 60, y0 - 40, tmelt + 150, y0 - 4)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (down, HOT))
    frags.append(text(x0 + 150, y0 - 165, "струм", size=13, color=HOT, bold=True, anchor="start"))

    # дугова напруга: після розплавлення підскакує ВИЩЕ Uж
    varc_pk = y0 - 190
    vpath = ("M %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f"
             % (x0 + 10, y0 - 6, tmelt, y0 - 6,
                tmelt + 20, varc_pk, tmelt + 55, varc_pk,
                tmelt + 130, y0 - 6, tmelt + 150, y0 - 6))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="2 0"/>' % (vpath, COOL))
    frags.append(text(tmelt + 95, varc_pk + 22, "дугова напруга", size=13, color=COOL, bold=True, anchor="start"))

    # позначка «елемент розплавився»
    frags.append(line(tmelt, y0 + 4, tmelt, y0 + 22, MUTED, 1))
    frags.append(text(tmelt, y0 + 38, "елемент розплавився", size=11, color=INK))

    # виділити перевищення дугової над Uж
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.12"/>'
                 % (tmelt + 18, varc_pk, 44, vsys - varc_pk, COOL))
    frags.append(text(tmelt + 175, (varc_pk + vsys) / 2, "перевищення", size=11, color=COOL, anchor="start"))
    frags.append(text(tmelt + 175, (varc_pk + vsys) / 2 + 16, "над Uж", size=11, color=COOL, anchor="start"))

    b, _, _ = textbox(x0 + 150, y0 - axh + 8,
                      ["насічки → кілька дуг послідовно →", "сумарна дугова напруга > Uж →", "струм примусово падає до нуля"],
                      size=12, fill="#eef1fb", stroke=COOL)
    frags.append(b)

    render(os.path.join(OUT, "fuse-arc-voltage.svg"), W, H, *frags,
           title="Як насічки обривають струм — і чому виникає перенапруга")


# ── 6. Класи aR (лише КЗ) vs gR (повний діапазон) на час-струмовій площині ───
def fig_classes():
    W, H = 720, 380
    x0, y0 = 100, 300
    axw, axh = 540, 240
    frags = []
    frags.append(line(x0, y0, x0 + axw, y0, INK, 2))
    frags.append(line(x0, y0, x0, y0 - axh, INK, 2))
    frags.append(arrow(x0 + axw, y0, x0 + axw + 14, y0, INK, 2))
    frags.append(arrow(x0, y0 - axh, x0, y0 - axh - 14, INK, 2))
    frags.append(text(x0 + axw + 6, y0 + 22, "струм (× In, лог)", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 6, y0 - axh - 4, "час спрацювання (лог)", size=13, color=MUTED, anchor="start"))

    # позначки кратності струму
    for mult, lbl in [(0.10, "In"), (0.42, "~4·In"), (0.95, "КЗ")]:
        xx = x0 + 30 + mult * (axw - 60)
        frags.append(line(xx, y0, xx, y0 + 6, MUTED, 1))
        frags.append(text(xx, y0 + 22, lbl, size=11, color=MUTED))

    import math
    def curve(color, xstart_frac, dash=None, sw=3):
        pts = []
        for i in range(0, 101):
            fx = i / 100.0
            if fx < xstart_frac:
                continue
            X = x0 + 30 + fx * (axw - 60)
            u = 0.10 + fx * 0.90
            val = 1.0 / (u ** 2)
            Y = y0 - (math.log10(val * 60 + 1) / math.log10(700)) * (axh - 30)
            pts.append((X, Y))
        if not pts:
            return ""
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (path, color, sw, d)

    # gR — повний діапазон: крива тягнеться від малих перевантажень (лівий край)
    frags.append(curve(OK, 0.05))
    # aR — лише КЗ: крива існує тільки праворуч (від ~4·In)
    frags.append(curve(HOT, 0.42))

    # зона, де aR НЕ спрацьовує надійно (ліворуч від ~4·In)
    xcut = x0 + 30 + 0.42 * (axw - 60)
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.08"/>'
                 % (x0, y0 - axh, xcut - x0, axh, HOT))
    b0, _, _ = textbox((x0 + xcut) / 2, y0 - axh + 40,
                       ["зона перевантажень:", "aR тут НЕ рве надійно →", "потрібен окремий захист"],
                       size=11, fill="#fdf0ee", stroke=HOT)
    frags.append(b0)

    # підписи кривих
    frags.append(text(x0 + axw - 10, y0 - axh + 30, "gR — повний діапазон", size=13, color=OK, bold=True, anchor="end"))
    frags.append(text(x0 + axw - 10, y0 - axh + 52, "(перевантаження + КЗ)", size=11, color=OK, anchor="end"))
    frags.append(text(x0 + axw - 10, y0 - 60, "aR — лише КЗ", size=13, color=HOT, bold=True, anchor="end"))

    render(os.path.join(OUT, "fuse-classes.svg"), W, H, *frags,
           title="aR vs gR: що саме кожен клас покриває")


# ── math-вставка: адіабатичне виведення I²t = K·A² ──────────────────────────

# 7. Адіабатичний баланс: усе джоулеве тепло → у нагрів маси (нема відтоку)
def fig_adiabatic_balance():
    W, H = 720, 400
    frags = []

    # «посудина» металу — прямокутник із закритою кришкою
    bx, by, bw, bh = 250, 120, 210, 200
    frags.append(rect(bx, by, bw, bh, fill="#fbe9e7", stroke=HOT, sw=2.5))
    frags.append(rect(bx - 14, by - 18, bw + 28, 20, fill="#d0d4da", stroke=INK, sw=2))
    frags.append(text(bx + bw / 2, by + 34, "маса металу", size=14, color=INK, bold=True))
    frags.append(text(bx + bw / 2, by + 62, "m · c · ΔT", size=20, color=HOT, bold=True))
    frags.append(text(bx + bw / 2, by + 104, "уся енергія", size=12, color=MUTED))
    frags.append(text(bx + bw / 2, by + 122, "лишається тут", size=12, color=MUTED))

    # приплив тепла зліва — стрілка «i²R dt»
    frags.append(arrow(120, by + bh / 2, bx - 4, by + bh / 2, HOT, 3))
    b1, _, _ = textbox(120, by + bh / 2 - 46,
                       ["джоулеве тепло", "∫ i²R dt"], size=13,
                       fill="#fdf0ee", stroke=HOT)
    frags.append(b1)

    # перекреслені стрілки відтоку (нема відтоку за короткий час)
    for dy in (by + 40, by + bh - 40):
        dx = bx + bw + 4
        frags.append(line(dx, dy, dx + 55, dy, MUTED, 2, dash="4 4"))
        frags.append(arrow(dx + 46, dy, dx + 66, dy, MUTED, 2))
        frags.append(line(dx + 22, dy - 11, dx + 44, dy + 11, HOT, 2.4))
        frags.append(line(dx + 44, dy - 11, dx + 22, dy + 11, HOT, 2.4))
    frags.append(text(bx + bw + 84, by + bh / 2 - 4, "нема", size=12, color=HOT, anchor="start", bold=True))
    frags.append(text(bx + bw + 84, by + bh / 2 + 12, "відтоку", size=12, color=HOT, anchor="start"))

    # термометр праворуч — до точки плавлення
    tx = bx + bw + 168
    frags.append(line(tx, by + 6, tx, by + bh - 6, INK, 3))
    frags.append(circle(tx, by + bh - 6, 12, fill=HOT, stroke=HOT, sw=1))
    frags.append('<rect x="%.1f" y="%.1f" width="6" height="%.1f" fill="%s"/>'
                 % (tx - 3, by + 44, bh - 50, HOT))
    frags.append(line(tx + 8, by + 22, tx + 24, by + 22, INK, 1.5))
    frags.append(text(tx + 28, by + 26, "плавлення", size=12, color=HOT, anchor="start", bold=True))
    frags.append(text(tx + 28, by + 42, "Cu 1085 °C", size=11, color=MUTED, anchor="start"))

    # рівняння балансу знизу
    b2, _, _ = textbox(W / 2, by + bh + 44,
                       "∫ i²R dt  =  m · c · ΔT   (усе тепло — на нагрів)",
                       size=15, fill="#f4f6f8", stroke=INK, bold=True)
    frags.append(b2)

    render(os.path.join(OUT, "i2t-balance.svg"), W, H, *frags,
           title="Адіабатичний баланс: приплив тепла = нагрів маси")


# 8. I²t = K·A²: квадратичний закон від перерізу
def fig_square_law():
    W, H = 720, 400
    frags = []
    y0 = 210                              # спільна лінія: над нею квадрат, під нею стовпчик
    specs = [(1, "A", "K·A²"), (2, "2A", "4·K·A²"), (3, "3A", "9·K·A²")]
    xc = [150, 360, 585]
    unit = 22
    bar_unit = 13                         # висота стовпчика на одиницю mult²
    for (mult, alab, dlab), cx in zip(specs, xc):
        s = unit * mult
        frags.append(rect(cx - s / 2, y0 - s, s, s, fill="#fdecea", stroke=HOT, sw=2))
        frags.append(text(cx, y0 - s - 12, "переріз " + alab, size=13, color=INK, bold=True))
        bh = mult * mult * bar_unit       # mult=3 → 9·13 = 117
        frags.append(rect(cx - 22, y0 + 18, 44, bh, fill="#eaf7ef", stroke=OK, sw=2))
        frags.append(text(cx, y0 + 18 + bh + 17, dlab, size=13, color=OK, bold=True))

    frags.append(text(66, y0 - 4, "площа", size=12, color=MUTED, anchor="start"))
    frags.append(text(66, y0 + 34, "доза I²t", size=12, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 372,
                      "подвоїв переріз → доза вчетверо:  I²t = K · A²",
                      size=15, fill="#f4f6f8", stroke=INK, bold=True)
    frags.append(b)

    render(os.path.join(OUT, "i2t-square-law.svg"), W, H, *frags,
           title="Доза росте як квадрат перерізу")


# 9. Стала залежить від цільової температури: куди гріємо — таке й K
def fig_target_temp():
    W, H = 720, 420
    frags = []
    x0, y0 = 130, 360
    axh = 300
    Tmax = 3000.0
    frags.append(line(x0, y0, x0, y0 - axh, INK, 2))
    frags.append(arrow(x0, y0 - axh, x0, y0 - axh - 14, INK, 2))
    frags.append(text(x0 - 8, y0 - axh - 4, "T, °C", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 + 6, y0 + 22, "20 °C (старт)", size=12, color=MUTED, anchor="start"))

    def Y(T):
        return y0 - (T / Tmax) * axh

    levels = [
        (160,  "межа ізоляції (PVC) 160 °C", "K ≈ 13 000",  COOL),
        (1085, "плавлення міді 1085 °C",     "K ≈ 85 000",  HOT),
        (2560, "випаровування ~2560 °C",     "K ≈ 210 000", INK),
    ]
    for T, lab, kv, col in levels:
        yy = Y(T)
        frags.append(line(x0, yy, x0 + 300, yy, col, 2, dash="6 4"))
        frags.append(circle(x0, yy, 5, fill=col, stroke=col, sw=1))
        frags.append(text(x0 + 312, yy - 4, lab, size=12.5, color=INK, anchor="start", bold=True))
        frags.append(text(x0 + 312, yy + 15, kv + " А²·с/мм⁴", size=12, color=col, anchor="start"))

    frags.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" fill="%s" opacity="0.25"/>'
                 % (x0 - 7, Y(1085), y0 - Y(1085), HOT))

    b, _, _ = textbox(W / 2, y0 + 46,
                      "що вище цільова T — то більша доза K (те саме A²)",
                      size=14, fill="#f4f6f8", stroke=INK, bold=True)
    frags.append(b)

    render(os.path.join(OUT, "i2t-target-temp.svg"), W, H, *frags,
           title="Число K залежить від того, доки гріємо метал")


if __name__ == "__main__":
    fig_dose()
    fig_coordination()
    fig_curve()
    fig_fuse_build()
    fig_arc_voltage()
    fig_classes()
    fig_adiabatic_balance()
    fig_square_law()
    fig_target_temp()
    print("ok: 9 figs")
