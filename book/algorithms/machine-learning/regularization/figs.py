# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC1 = "#0ea5e9"   # блакитна — «спокійна» крива / L2
ACC2 = "#9333ea"   # фіолетова — L1
ACC3 = "#e08a1e"   # тепла — валідація
DATA = "#334155"   # точки даних


# ── big-weights: та сама модель, малі ваги (плавно) vs великі ваги (звивисто) ──
# Ідея: перенавчання — це не «зайві нейрони», а РОЗДУТІ ваги. Дай моделі
# скрутитися крізь кожну точку — коефіцієнти шаленіють, крива смикається;
# притисни ваги до нуля — крива випрямляється в закономірність.
def fig_big_weights():
    W, H = 760, 380
    p = []
    # спільні дані-точки (тренд угору + шум) — однакові на обох панелях
    import random
    random.seed(7)
    xs = [0.10, 0.22, 0.34, 0.46, 0.58, 0.70, 0.82, 0.92]
    base = [0.20, 0.34, 0.40, 0.58, 0.55, 0.74, 0.80, 0.90]

    def panel(x0, title, weights_big):
        pw, ph = 300.0, 250.0
        y0 = 300.0
        out = [rect(x0, y0 - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8)]

        def PX(t):
            return x0 + 24 + t * (pw - 44)

        def PY(v):
            return y0 - 22 - v * (ph - 44)

        # крива
        pts = []
        t = 0.0
        while t <= 1.0 + 1e-9:
            if weights_big:
                # звивиста: сильні осциляції (великі ваги) поверх тренду
                v = 0.5 + 0.42 * t + 0.16 * math.sin(t * 34) * (0.4 + t) \
                    + 0.10 * math.sin(t * 61)
            else:
                v = 0.16 + 0.78 * t   # майже пряма — притиснуті ваги
            v = max(0.02, min(0.98, v))
            pts.append("%.1f,%.1f" % (PX(t), PY(v)))
            t += 0.006
        col = ACC2 if weights_big else ACC1
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                   % (" ".join(pts), col))
        # точки
        for tx, vy in zip(xs, base):
            out.append(circle(PX(tx), PY(vy), 4.2, fill=DATA, stroke=BG, sw=1.4))
        out.append(text(x0 + pw / 2, y0 - ph - 10, title, size=13, color=col, bold=True))
        return out

    p += panel(60, "малі ваги → плавна крива", False)
    p += panel(400, "великі ваги → крива смикається", True)
    # підписи-ярлики під панелями
    p.append(text(60 + 150, 340, "ловить закономірність", size=11.5, color=ACC1, bold=True))
    p.append(text(400 + 150, 340, "продирається крізь шум", size=11.5, color=ACC2, bold=True))
    render(os.path.join(OUT, "big-weights.svg"), W, H, *p,
           title="Перенавчання живе у РОЗДУТИХ вагах")


# ── l1-vs-l2: форма штрафу за вагу; L2 біля нуля майже дарма, L1 тягне до 0 ─────
# Ідея: показати ДВІ криві штрафу від значення однієї ваги. L2 = w² —
# парабола, біля нуля пласка (малу вагу майже не чіпає). L1 = |w| — галочка з
# гострим злам-кутом у нулі: біля нуля тягне з тією ж силою → занулює.
def fig_l1_vs_l2():
    W, H = 760, 420
    p = []
    ox, oy = 110.0, 340.0
    pw, ph = 560.0, 280.0
    p.append(rect(ox, oy - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8))
    wmax = 2.0
    ymax = 2.0
    cx = ox + pw / 2.0

    def X(w):
        return cx + (pw / 2.0) * w / wmax

    def Y(v):
        return oy - ph * min(v, ymax) / ymax

    # осі
    p.append(line(cx, oy, cx, oy - ph, color="#dfe4ea", sw=1.0))
    for w in (-2, -1, 1, 2):
        p.append(line(X(w), oy, X(w), oy - ph, color="#eef1f4", sw=1.0))
        p.append(text(X(w), oy + 18, "%d" % w, size=11, color=MUTED))
    for v in (1, 2):
        p.append(line(ox, Y(v), ox + pw, Y(v), color="#eef1f4", sw=1.0))
        p.append(text(ox - 8, Y(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    p.append(text(cx, oy + 36, "значення однієї ваги  w", size=12, color=INK))
    p.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 26 %.1f)">штраф за цю вагу</text>'
             % (oy - ph / 2, FONT, INK, oy - ph / 2))

    # L2: w² — парабола (блакитна)
    pts = []
    w = -wmax
    while w <= wmax + 1e-9:
        pts.append("%.1f,%.1f" % (X(w), Y(w * w)))
        w += 0.02
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), ACC1))
    # L1: |w| — галочка (фіолетова)
    p.append(line(X(-wmax), Y(wmax), cx, Y(0), color=ACC2, sw=2.8))
    p.append(line(cx, Y(0), X(wmax), Y(wmax), color=ACC2, sw=2.8))

    p.append(text(X(1.5), Y(1.9), "w²  (L2)", size=12.5, color=ACC1, bold=True, anchor="start"))
    p.append(text(X(1.5), Y(0.9), "|w|  (L1)", size=12.5, color=ACC2, bold=True, anchor="start"))

    # виноска на кут у нулі (коробку зсунуто вліво-вгору, щоб не лягала на галочку)
    p.append(circle(cx, Y(0), 4.5, fill=ACC2, stroke=BG, sw=1.5))
    bx, by = X(-1.02), Y(1.35)
    b, bw, bh = textbox(bx, by, ["у нулі L1 має гострий кут:", "тягне вагу до 0 навіть з нуля"],
                        size=11, fill="#faf5ff", stroke=ACC2)
    p.append(b)
    p.append(line(bx + bw / 2 - 6, by + bh / 2 - 4, cx - 6, Y(0) - 6, color=ACC2, sw=1.2, dash="3 3"))
    # виноска на пласке дно L2 (праворуч-унизу, під галочкою L1, де порожньо)
    b2, bw2, bh2 = textbox(X(1.0), Y(0.28), ["L2 біля нуля майже пласка", "→ лишає малі ваги жити"],
                           size=10.5, fill="#eef7fd", stroke=ACC1, color=ACC1)
    p.append(b2)
    render(os.path.join(OUT, "l1-vs-l2.svg"), W, H, *p,
           title="Форма штрафу вирішує: L2 стискає, L1 занулює")


# ── lambda-sweep: сила регуляризації λ vs похибка train/val (U-подібна) ────────
# Ідея: λ малий → модель вільна, перенавчання (val високо, train низько);
# λ великий → модель задушена, недонавчання (обидві високо). Посередині —
# мінімум валідаційної: найкраще узагальнення.
def fig_lambda_sweep():
    W, H = 760, 420
    p = []
    ox, oy = 110.0, 340.0
    pw, ph = 560.0, 280.0
    p.append(rect(ox, oy - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8))

    # X — log λ (зліва слабка регуляризація, справа сильна), Y — похибка
    def X(t):   # t у [0,1]
        return ox + t * pw

    def Y(v):   # v у [0,1] похибка
        return oy - ph * v

    # тренувальна: монотонно РОСТЕ з λ (сильніший штраф — гірше на тренуванні)
    tr = []
    t = 0.0
    while t <= 1.0 + 1e-9:
        v = 0.08 + 0.62 * (t ** 1.7)
        tr.append("%.1f,%.1f" % (X(t), Y(v)))
        t += 0.01
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(tr), ACC1))

    # валідаційна: U — спершу падає (менше перенавчання), тоді росте (недонавчання)
    va = []
    best_t, best_v = 0.0, 9.0
    t = 0.0
    while t <= 1.0 + 1e-9:
        v = 0.72 - 1.55 * t + 1.65 * t * t   # парабола-ковш
        v = max(0.05, min(0.95, v))
        va.append((t, v))
        if v < best_v:
            best_v, best_t = v, t
        t += 0.01
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % (X(tt), Y(vv)) for tt, vv in va), ACC3))

    # позначка оптимуму
    p.append(line(X(best_t), oy, X(best_t), Y(best_v), color=FIELD, sw=1.4, dash="5 4"))
    p.append(circle(X(best_t), Y(best_v), 5.5, fill=FIELD, stroke=BG, sw=1.6))
    b, bw, bh = textbox(X(best_t), Y(best_v) - 34, "тут λ саме враз",
                        size=11.5, bold=True, fill="#eafaf1", stroke=FIELD)
    p.append(b)

    # зони
    p.append(mtext(X(0.13), Y(0.92), ["λ малий", "перенавчання"], size=11, color=MUTED))
    p.append(mtext(X(0.88), Y(0.92), ["λ великий", "недонавчання"], size=11, color=MUTED))
    # підписи кривих
    p.append(text(X(0.62), Y(0.30), "тренувальна", size=12, color=ACC1, bold=True, anchor="start"))
    p.append(text(X(0.30), Y(0.20), "валідаційна", size=12, color=ACC3, bold=True))

    p.append(text(ox + pw / 2, oy + 26, "сила регуляризації  λ  →", size=12, color=INK))
    p.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 26 %.1f)">похибка</text>'
             % (oy - ph / 2, FONT, INK, oy - ph / 2))
    render(os.path.join(OUT, "lambda-sweep.svg"), W, H, *p,
           title="λ — ручка між перенавчанням і недонавчанням")


# ── hist-timeline: одна ідея (штраф за складність) тричі народжується окремо ──
# Три доріжки (інверсні задачі · статистика · нейромережі) на спільній осі
# часу; штучні дуги показують, що це та сама думка, перевідкрита незалежно.
def fig_hist_timeline():
    W, H = 900, 470
    p = []
    x0, x1 = 96.0, 730.0          # ліва/права межі осі (запас справа під підписи-коробки)
    ytop = 90.0                    # верх смуг
    ROWH = 96.0                    # висота рядка-доріжки
    Y1943, Y2014 = 1940.0, 2016.0  # діапазон років на осі

    def X(year):
        return x0 + (x1 - x0) * (year - Y1943) / (Y2014 - Y1943)

    # три доріжки (назва галузі, колір, y-центр)
    lanes = [
        ("інверсні задачі (математична фізика)", ACC1, ytop + ROWH * 0 + 34),
        ("статистика",                            ACC3, ytop + ROWH * 1 + 34),
        ("нейромережі",                           ACC2, ytop + ROWH * 2 + 34),
    ]
    for name, col, yc in lanes:
        p.append(line(x0, yc, x1, yc, color="#e3e8ee", sw=1.4))
        p.append(text(x0 - 4, yc - 40, name, size=11.5, color=col, bold=True, anchor="start"))

    # ── доріжка 1: Тихонов
    yc1 = lanes[0][2]
    for yr, lab in [(1943, ["Тихонов:", "стійкість інверсних задач"]),
                    (1963, ["Тихонов:", "метод регуляризації"])]:
        cx = X(yr)
        p.append(circle(cx, yc1, 6.0, fill=ACC1, stroke=BG, sw=1.8))
        p.append(text(cx, yc1 + 22, str(yr), size=11, color=INK, bold=True))
        b, bw, bh = textbox(cx, yc1 - 26, lab, size=10, fill="#eef7fd", stroke=ACC1, color=INK)
        p.append(b)

    # ── доріжка 2: Гоерл–Кеннард, Тібширані
    yc2 = lanes[1][2]
    for yr, lab, side in [(1970, ["Гоерл і Кеннард:", "гребенева регресія (L2)"], "up"),
                          (1996, ["Тібширані:", "LASSO (L1), розрідженість"], "down")]:
        cx = X(yr)
        p.append(circle(cx, yc2, 6.0, fill=ACC3, stroke=BG, sw=1.8))
        p.append(text(cx, yc2 + 22, str(yr), size=11, color=INK, bold=True))
        yy = yc2 - 26 if side == "up" else yc2 + 34
        b, bw, bh = textbox(cx, yy, lab, size=10, fill="#fdf4e8", stroke=ACC3, color=INK)
        p.append(b)

    # ── доріжка 3: dropout
    yc3 = lanes[2][2]
    cx = X(2014)
    p.append(circle(cx, yc3, 6.0, fill=ACC2, stroke=BG, sw=1.8))
    p.append(text(cx, yc3 + 22, "2014", size=11, color=INK, bold=True))
    b, bw, bh = textbox(cx, yc3 - 26, ["Срівастава, Гінтон та ін.:", "dropout"],
                        size=10, fill="#faf5ff", stroke=ACC2, color=INK)
    p.append(b)

    # дуга «та сама ідея» від Тихонова-1963 до ridge-1970
    ax1, ay1 = X(1963), yc1 + 8
    ax2, ay2 = X(1970), yc2 - 8
    midx = (ax1 + ax2) / 2
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="4 4"/>'
             % (ax1, ay1, midx, (ay1 + ay2) / 2 + 26, ax2, ay2, MUTED))
    p.append(text(midx, (ay1 + ay2) / 2 + 44, "та сама ідея, перевідкрита", size=10,
                  color=MUTED, italic=True))

    # спільний підпис-стрічка внизу
    p.append(text(W / 2, ytop + ROWH * 3 + 26,
                  "штраф за складність: L2 «стискає», L1 «занулює»", size=12.5,
                  color=INK, bold=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Одна думка, три незалежні народження")


# ── l1-l2-geometry: обмежена оптимізація — еліпси похибки vs круг(L2)/ромб(L1) ──
# Ідея: надуваємо еліпс похибки з центра ŵ, поки він не діткнеться дозволеної
# області. Круг гладкий → дотик збоку, обидві координати != 0. Ромб має кути
# на осях → еліпс чіпляється за кут → одна координата = 0. Це — вся розрідженість.
def fig_l1_l2_geometry():
    W, H = 780, 430
    p = []

    def panel(x0, title, kind, col):
        pw, ph = 320.0, 320.0
        cx, cy = x0 + pw / 2.0, 250.0     # центр осей панелі
        out = [rect(x0, 66, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8)]
        # осі координат ваг
        out.append(line(x0 + 20, cy, x0 + pw - 16, cy, color="#c9d2db", sw=1.2))
        out.append(line(cx, 78, cx, 66 + ph - 14, color="#c9d2db", sw=1.2))
        out.append(text(x0 + pw - 12, cy + 15, "w₁", size=12, color=MUTED, anchor="end"))
        out.append(text(cx + 15, 90, "w₂", size=12, color=MUTED, anchor="start"))

        R = 78.0                          # «радіус» бюджету в px
        # дозволена область
        if kind == "circle":
            out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" '
                       'fill-opacity="0.14" stroke="%s" stroke-width="2.4"/>'
                       % (cx, cy, R, col, col))
        else:  # ромб: вершини точно на осях
            d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
                cx, cy - R, cx + R, cy, cx, cy + R, cx - R, cy)
            out.append('<path d="%s" fill="%s" fill-opacity="0.14" '
                       'stroke="%s" stroke-width="2.4"/>' % (d, col, col))

        # точка дотику (де найменший еліпс уперше чіпляє область) — своя на панель
        if kind == "circle":
            tx, ty = cx + R * math.cos(-0.72), cy + R * math.sin(-0.72)   # збоку кола
        else:
            tx, ty = cx, cy - R                                          # верхня вершина ромба на осі

        # центр еліпсів похибки ŵ — у верхній частині панелі, поза дозволеною зоною
        # (напрям зсуву свій на панель, щоб великий еліпс не торкнувся стінки панелі)
        if kind == "circle":
            ex, ey = cx + 28.0, cy - 92.0     # трохи праворуч і високо над кругом
        else:
            ex, ey = cx + 40.0, cy - 96.0     # праворуч-угору від верхньої вершини ромба
        # нахилений еліпс похибки: параметрично, поворот на кут th
        th = -0.62
        ct, st = math.cos(th), math.sin(th)

        def ellipse_at(a, b):
            pts = []
            t = 0.0
            while t <= 2 * math.pi + 1e-9:
                lx, ly = a * math.cos(t), b * math.sin(t)
                gx = ex + lx * ct - ly * st
                gy = ey + lx * st + ly * ct
                pts.append("%.1f,%.1f" % (gx, gy))
                t += 0.10
            return " ".join(pts)

        # кілька вкладених еліпсів однакової похибки (розміри стримані — не вилазять із панелі)
        for a, b in ((66, 40), (48, 29), (32, 19)):
            out.append('<polyline points="%s" fill="none" stroke="#b8c2cd" '
                       'stroke-width="1.3"/>' % ellipse_at(a, b))
        # найменший, «дотичний» еліпс кольором панелі + мітка дотику
        out.append('<polyline points="%s" fill="none" stroke="%s" '
                   'stroke-width="2.4"/>' % (ellipse_at(20, 12), col))
        if kind == "circle":
            note = ["дотик ЗБОКУ:", "w₁≠0, w₂≠0"]
            nb_x, nb_y = cx + 4, cy + 96
        else:
            out.append(line(tx, ty, tx, cy, color=col, sw=1.1, dash="3 3"))
            note = ["дотик у КУТІ на осі:", "w₁ = 0"]
            nb_x, nb_y = cx - 2, cy + 96
        out.append(circle(ex, ey, 3.6, fill=DATA, stroke=BG, sw=1.2))
        out.append(text(ex + 11, ey - 4, "ŵ", size=12.5, color=DATA, bold=True, anchor="start"))
        out.append(circle(tx, ty, 5.2, fill=col, stroke=BG, sw=1.7))
        nb, _, _ = textbox(nb_x, nb_y, note, size=10.5, fill="#ffffff", stroke=col, color=col)
        out.append(nb)
        out.append(text(cx, 60, title, size=13, color=col, bold=True))
        return out

    p += panel(30, "L2: круг — гладкий скрізь", "circle", ACC1)
    p += panel(430, "L1: ромб — кути на осях", "diamond", ACC2)
    render(os.path.join(OUT, "l1-l2-geometry.svg"), W, H, *p,
           title="Форма бюджету вирішує: гладкий круг vs ромб із кутами")


# ── soft-threshold: w_нове(z) — тотожність, L2-масштаб, L1-порогування ──────────
# Ідея: показати, ЩО кожен штраф робить із вагою за крок. L2 — пряма крізь 0 з
# нахилом <1 (нуль лише в z=0). L1 — ламана з ПЛАСКИМ дном на [−ηλ, ηλ] (цілий
# діапазон малих z → точний 0), поза ним — паралель до тотожності, зсунута на ηλ.
def fig_soft_threshold():
    W, H = 700, 470
    p = []
    ox, oy = 350.0, 250.0                 # центр осей (по центру полотна)
    S = 150.0                             # піврозмах по осях у px
    thr = 0.32                            # поріг ηλ у частках піврозмаху
    p.append(rect(ox - S - 24, oy - S - 24, 2 * (S + 24), 2 * (S + 24),
                  fill="#fbfdff", stroke=INK, sw=1.3, rx=8))
    # осі
    p.append(line(ox - S - 8, oy, ox + S + 8, oy, color="#c9d2db", sw=1.2))
    p.append(line(ox, oy + S + 8, ox, oy - S - 8, color="#c9d2db", sw=1.2))
    p.append(text(ox + S + 2, oy + 18, "z", size=12.5, color=MUTED, anchor="end"))
    p.append(text(ox + 14, oy - S - 6, "w після штрафу", size=11.5, color=INK, anchor="start"))

    def X(z):  return ox + z * S
    def Y(w):  return oy - w * S

    # тотожність w = z (штрафу нема)
    p.append(line(X(-1), Y(-1), X(1), Y(1), color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(X(0.78), Y(0.98), "w = z", size=11.5, color=MUTED, anchor="start"))

    # L2: w = z/(1+2ηλ) — пряма крізь 0, нахил <1
    k = 0.62
    p.append(line(X(-1), Y(-k), X(1), Y(k), color=ACC1, sw=2.6))
    p.append(text(X(0.60), Y(0.28), "L2: масштаб", size=11.5, color=ACC1, bold=True, anchor="start"))

    # L1: м'яке порогування — пласке дно на [−thr, thr], тоді зсунуті гілки
    p.append(line(X(-thr), Y(0), X(thr), Y(0), color=ACC2, sw=3.0))          # пласке дно
    p.append(line(X(thr), Y(0), X(1), Y(1 - thr), color=ACC2, sw=3.0))       # права гілка
    p.append(line(X(-thr), Y(0), X(-1), Y(-(1 - thr)), color=ACC2, sw=3.0))  # ліва гілка
    p.append(text(X(0.30), Y(0.64), "L1: порогування", size=11.5, color=ACC2, bold=True, anchor="start"))

    # позначки порога ±ηλ на осі z
    for s, lab in ((thr, "+ηλ"), (-thr, "−ηλ")):
        p.append(line(X(s), oy - 4, X(s), oy + 4, color=INK, sw=1.4))
        p.append(text(X(s), oy + 20, lab, size=11, color=INK))
    # виноска на пласке дно
    b, bw, bh = textbox(X(-0.02), Y(-0.56), ["пласке дно на |z| ≤ ηλ:", "цілий діапазон → точний 0"],
                        size=10.5, fill="#faf5ff", stroke=ACC2, color=ACC2)
    p.append(b)
    p.append(line(X(-0.02), Y(-0.56) - bh / 2, X(0.0), Y(0) + 3, color=ACC2, sw=1.2, dash="3 3"))
    # виноска: L2 торкається 0 лише в z=0
    p.append(circle(X(0), Y(0), 4.0, fill=ACC1, stroke=BG, sw=1.5))
    b2, _, _ = textbox(X(0.62), Y(-0.32), ["L2 = 0 лише тут", "(в z = 0)"],
                       size=10, fill="#eef7fd", stroke=ACC1, color=ACC1)
    p.append(b2)
    render(os.path.join(OUT, "soft-threshold.svg"), W, H, *p,
           title="Крок штрафу над вагою: L2 масштабує, L1 занулює діапазон")


if __name__ == "__main__":
    fig_big_weights()
    fig_l1_vs_l2()
    fig_lambda_sweep()
    fig_hist_timeline()
    fig_l1_l2_geometry()
    fig_soft_threshold()
    print("OK figs")
