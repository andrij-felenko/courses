# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── window-shift: чому кут = зміна в ОБИДВОХ напрямах ──────────────────────────
# Три латки — рівне поле, край, кут. Зсуваємо віконце й дивимось, як міняється
# картинка. Рівне — не міняється ніяк; край — не міняється вздовж себе; кут —
# міняється, куди не зсунь. Це й є критерій кута.

def fig_window_shift():
    W, H = 900, 360
    p = []

    def patch(x0, y0, name, kind, note):
        s = 128                      # сторона латки
        # фон латки залежно від типу
        if kind == "flat":
            p.append(rect(x0, y0, s, s, fill="#e8ecf1", stroke=LINE, sw=1.4, rx=6))
        elif kind == "edge":
            # темна половина ліворуч, світла праворуч (вертикальний край)
            p.append(rect(x0, y0, s, s, fill="#e8ecf1", stroke=LINE, sw=1.4, rx=6))
            p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f Z" '
                     'fill="#2b3440"/>' % (x0 + 6, y0 + 6, x0 + s / 2, y0 + 6,
                                           x0 + s / 2, y0 + s - 6, x0 + 6, y0 + s - 6))
        else:  # corner — темний куток (лівий-верхній), решта світла
            p.append(rect(x0, y0, s, s, fill="#e8ecf1", stroke=LINE, sw=1.4, rx=6))
            p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f Z" '
                     'fill="#2b3440"/>' % (x0 + 6, y0 + 6, x0 + s * 0.6, y0 + 6,
                                           x0 + s * 0.6, y0 + s * 0.6, x0 + 6, y0 + s * 0.6))
        # віконце (жовте) у центрі + стрілки зсуву на 4 боки
        wc, wsz = (x0 + s / 2, y0 + s / 2), 30
        wx, wy = wc[0] - wsz / 2, wc[1] - wsz / 2
        p.append(rect(wx, wy, wsz, wsz, fill="none", stroke=POS, sw=2.4, rx=3))
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            p.append(arrow(wc[0], wc[1], wc[0] + dx * 26, wc[1] + dy * 26,
                           color=POS, sw=1.6))
        p.append(text(x0 + s / 2, y0 - 12, name, size=13, bold=True))
        # висновок під латкою — рамка, гарантовано вміщає текст
        p.append(fitbox(x0 - 20, y0 + s + 12, s + 40, 58, note,
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.4,
                        color=INK, bold=True))

    patch(70, 70, "рівне поле", "flat", "зсунь куди хоч —\nзмін нема")
    patch(390, 70, "край", "edge", "уздовж краю нема,\nупоперек — є")
    patch(710, 70, "кут", "corner", "куди не зсунь —\nкартинка інша")

    render(os.path.join(OUT, "window-shift.svg"), W, H, *p,
           title="Зсунь віконце: кут — там, де змінюється в ОБИДВОХ напрямах")


# ── eig-plane: площина (λ₁, λ₂) — де рівне / край / кут; Гарріс vs Ші–Томасі ────
# Дві власні числа матриці M кажуть, наскільки різко міняється яскравість по
# двох головних осях. Обидва малі — рівне; одне велике — край; обидва великі —
# кут. Ші–Томасі бере поріг по min(λ₁,λ₂) — чверть-квадрат; Гарріс — крива R=0.

def fig_eig_plane():
    W, H = 620, 560
    p = []
    ox, oy = 110, H - 90          # початок координат
    ax = W - 190                  # довжина осі
    ay = H - 160

    # осі
    p.append(arrow(ox, oy, ox + ax, oy, color=INK, sw=1.7))
    p.append(arrow(ox, oy, ox, oy - ay, color=INK, sw=1.7))
    p.append(text(ox + ax, oy + 24, "λ₁ (різкість уздовж осі 1)", size=11,
                  color=MUTED, anchor="end"))
    p.append(text(ox - 14, oy - ay + 4, "λ₂", size=13, color=MUTED, anchor="end"))

    def X(v): return ox + v * ax          # v у [0,1]
    def Y(v): return oy - v * ay

    thr = 0.42                              # поріг λ_min для Ші–Томасі

    # зона КУТА (Ші–Томасі): λ₁≥thr І λ₂≥thr — правий-верхній квадрат
    p.append(rect(X(thr), Y(1.0), X(1.0) - X(thr), Y(thr) - Y(1.0),
                  fill="#eafaf0", stroke="none"))
    # зони краю: одне велике, друге мале (дві смуги)
    p.append(rect(X(thr), oy - (Y(thr) - oy) if False else Y(thr),
                  X(1.0) - X(thr), oy - Y(thr), fill="#eaf0fd", stroke="none"))
    p.append(rect(X(0), Y(1.0), X(thr) - X(0), Y(thr) - Y(1.0),
                  fill="#eaf0fd", stroke="none"))

    # лінії порогу
    p.append(line(X(thr), oy, X(thr), Y(1.0), color=FIELD, sw=1.6, dash="6 4"))
    p.append(line(ox, Y(thr), X(1.0), Y(thr), color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(X(thr), oy + 16, "λ_min", size=10, color=FIELD, bold=True))

    # крива Гарріса R=0: λ₂ = k'·λ₁/(λ₁ − k'·... ) — намалюємо як гіперболу-межу
    # де корисно: R>0 (кут) приблизно там, де добуток великий → крива, що
    # відсікає ріг. Візьмемо λ₁·λ₂ = c як межу «кут / не кут» для наочності.
    c = thr * thr * 1.15
    pts = []
    v = thr * 0.62
    while v <= 1.001:
        l2 = c / v
        if l2 <= 1.0:
            pts.append("%.1f,%.1f" % (X(v), Y(l2)))
        v += 0.01
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-dasharray="2 0"/>' % (" ".join(pts), POS))
    p.append(text(X(0.82), Y(c / 0.82) - 12, "Гарріс: R = 0", size=10.5,
                  color=POS, bold=True, anchor="start"))

    # підписи зон
    p.append(text(X(0.16), Y(0.14), "РІВНЕ", size=12, color=MUTED, bold=True))
    p.append(text(X(0.16), Y(0.14) + 16, "λ₁,λ₂ малі", size=9, color=MUTED))
    p.append(text(X(0.72), Y(0.16), "КРАЙ", size=12, color=NEG, bold=True))
    p.append(text(X(0.72), Y(0.16) + 16, "λ₁≫λ₂", size=9, color=NEG))
    p.append(text(X(0.18), Y(0.74), "КРАЙ", size=12, color=NEG, bold=True))
    p.append(text(X(0.18), Y(0.74) + 16, "λ₂≫λ₁", size=9, color=NEG))
    p.append(text(X(0.70), Y(0.74), "КУТ", size=13, color=FIELD, bold=True))
    p.append(text(X(0.70), Y(0.74) + 16, "λ₁,λ₂ великі", size=9, color=FIELD))

    render(os.path.join(OUT, "eig-plane.svg"), W, H, *p,
           title="Дві власні числа: рівне / край / кут (Гарріс і Ші–Томасі)")


# ── fast-circle: 16 пікселів кола + суцільна дуга + швидкий тест 1/5/9/13 ──────
# FAST дивиться на кільце з 16 пікселів (радіус 3). Кут — якщо є суцільна дуга
# з N (тут 9) підряд, усі яскравіші p+t або темніші p−t. Спершу — 4 «хрестові»
# пікселі 1,5,9,13: якщо серед них немає ≥3 однобічних, це не кут — кидаємо.

def fig_fast_circle():
    W, H = 760, 470
    p = []
    cx, cy = 250, 240
    step = 34                     # крок клітинки-пікселя

    # координати 16 пікселів кола Брезенгема (радіус 3) відносно центру
    off = [(0, -3), (1, -3), (2, -2), (3, -1), (3, 0), (3, 1), (2, 2), (1, 3),
           (0, 3), (-1, 3), (-2, 2), (-3, 1), (-3, 0), (-3, -1), (-2, -2), (-1, -3)]
    # яскравіші за p+t — «дуга»: індекси 0..8 (9 підряд) → кут
    bright = set(range(0, 9))     # 9 суцільних → FAST-9 спрацював

    # центральний піксель p
    p.append(rect(cx - step / 2, cy - step / 2, step, step,
                  fill="#fff3bf", stroke=INK, sw=2, rx=4))
    p.append(text(cx, cy + 5, "p", size=15, bold=True))

    for i, (dx, dy) in enumerate(off):
        x = cx + dx * step - step / 2
        y = cy + dy * step - step / 2
        n = i + 1                             # людська нумерація 1..16
        cross = n in (1, 5, 9, 13)
        isbright = i in bright
        fill = "#fdecea" if isbright else "#eaf0fd"
        stroke = POS if isbright else NEG
        sw = 2.6 if cross else 1.4
        p.append(rect(x, y, step, step, fill=fill, stroke=stroke, sw=sw, rx=4))
        p.append(text(x + step / 2, y + step / 2 + 5, str(n), size=11,
                      color=INK, bold=cross))

    # позначити суцільну дугу дугою-обідком поверх
    p.append(text(cx, cy - 4 * step + 4, "суцільна дуга ≥ 9 «яскравіших» → КУТ",
                  size=10.5, color=POS, bold=True))

    # легенда праворуч
    lx = 470
    p.append(text(lx, 70, "яскравіші p+t", size=11, color=POS, bold=True, anchor="start"))
    p.append(rect(lx - 26, 62, 16, 12, fill="#fdecea", stroke=POS, sw=1.6, rx=2))
    p.append(text(lx, 96, "темніші p−t", size=11, color=NEG, bold=True, anchor="start"))
    p.append(rect(lx - 26, 88, 16, 12, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=2))
    p.append(text(lx, 122, "1,5,9,13 — швидкий тест", size=11, color=INK,
                  bold=True, anchor="start"))

    p.append(fitbox(lx - 26, 150, 268, 128,
                    "Швидкий відсів:\nглянь лише 1,5,9,13.\nБракує ≥3 однобічних —\nне кут, кидаємо відразу.\nВ середньому ~3.8\nпікселя на кандидата.",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, bold=True))

    render(os.path.join(OUT, "fast-circle.svg"), W, H, *p,
           title="FAST: кільце з 16 пікселів, суцільна дуга, швидкий тест")


# ── m-build: як з латки народжується M (латка → градієнти → добутки → сума) ────
# Механіка структурного тензора: беремо латку, у кожному пікселі рахуємо (Iₓ,I_y),
# перемножуємо в три карти Iₓ², I_y², IₓI_y, кожну підсумовуємо по вікну — три
# числа стають чотирма клітинками M. Показуємо ланцюг «поле похідних → сума → M».

def fig_m_build():
    W, H = 720, 300
    p = []

    # 1) латка з градієнтним полем (стрілки градієнта в кількох точках)
    x0, y0, s = 40, 90, 150
    p.append(rect(x0, y0, s, s, fill="#eef2f6", stroke=LINE, sw=1.4, rx=6))
    # темний ріг у лівому-верхньому куті → градієнти дивляться від межі
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#2b3440"/>'
             % (x0 + 6, y0 + 6, x0 + s * 0.55, y0 + 6,
                x0 + s * 0.55, y0 + s * 0.55, x0 + 6, y0 + s * 0.55))
    # стрілки-градієнти вздовж двох меж рогу (по вертикальній і горизонтальній)
    import math as _m
    for t in range(1, 5):
        gy = y0 + 6 + t * (s * 0.55 - 6) / 5.0
        p.append(arrow(x0 + s * 0.55, gy, x0 + s * 0.55 + 22, gy, color=POS, sw=1.5))
        gx = x0 + 6 + t * (s * 0.55 - 6) / 5.0
        p.append(arrow(gx, y0 + s * 0.55, gx, y0 + s * 0.55 + 22, color=NEG, sw=1.5))
    p.append(text(x0 + s / 2, y0 - 12, "латка + поле (Iₓ, I_y)", size=12, bold=True))
    p.append(text(x0 + s / 2, y0 + s + 22, "у кожному пікселі — свій градієнт",
                  size=10, color=MUTED))

    # стрілка «перемножуємо»
    ax1 = x0 + s + 20
    p.append(arrow(ax1, y0 + s / 2, ax1 + 54, y0 + s / 2, color=INK, sw=2))
    p.append(text(ax1 + 27, y0 + s / 2 - 10, "квадрати", size=10, color=MUTED))
    p.append(text(ax1 + 27, y0 + s / 2 + 22, "й добутки", size=10, color=MUTED))

    # 2) три карти добутків
    mx = ax1 + 74
    mw, mh, gap = 96, 42, 12
    maps = [("Iₓ²", "#fdecea", POS), ("I_y²", "#eaf0fd", NEG), ("IₓI_y", "#eafaf0", FIELD)]
    for i, (lbl, fl, st) in enumerate(maps):
        my = y0 + i * (mh + gap)
        p.append(rect(mx, my, mw, mh, fill=fl, stroke=st, sw=1.6, rx=5))
        p.append(text(mx + mw / 2, my + mh / 2 + 5, lbl, size=15, color=INK, bold=True))
    p.append(text(mx + mw / 2, y0 - 12, "три карти", size=12, bold=True))

    # стрілка «Σ по вікну»
    ax2 = mx + mw + 16
    p.append(arrow(ax2, y0 + s / 2, ax2 + 54, y0 + s / 2, color=INK, sw=2))
    p.append(text(ax2 + 27, y0 + s / 2 - 10, "Σ по", size=10, color=MUTED))
    p.append(text(ax2 + 27, y0 + s / 2 + 22, "вікну", size=10, color=MUTED))

    # 3) матриця M 2×2
    Mx = ax2 + 74
    Mw = 210
    p.append(rect(Mx, y0 + 8, Mw, s - 16, fill="#fbfcfd", stroke=INK, sw=1.8, rx=8))
    p.append(text(Mx + Mw / 2, y0 - 12, "M = структурний тензор", size=12, bold=True))
    cyc = y0 + s / 2
    # дужки
    p.append(text(Mx + 20, cyc + 8, "⎡", size=40, color=INK))
    p.append(text(Mx + 20, cyc + 34, "⎣", size=40, color=INK))
    p.append(text(Mx + Mw - 20, cyc + 8, "⎤", size=40, color=INK))
    p.append(text(Mx + Mw - 20, cyc + 34, "⎦", size=40, color=INK))
    p.append(text(Mx + Mw * 0.40, cyc - 12, "Σ Iₓ²", size=13, color=POS, bold=True))
    p.append(text(Mx + Mw * 0.74, cyc - 12, "Σ IₓI_y", size=13, color=FIELD, bold=True))
    p.append(text(Mx + Mw * 0.40, cyc + 30, "Σ IₓI_y", size=13, color=FIELD, bold=True))
    p.append(text(Mx + Mw * 0.74, cyc + 30, "Σ I_y²", size=13, color=NEG, bold=True))

    render(os.path.join(OUT, "m-build.svg"), W, H, *p,
           title="Народження M: латка → градієнти → добутки → сума")


# ── e-ellipse: ізолінія E = const — еліпс; півосі ~1/√λ, вектори = головні осі ──
# Форма E(u,v)=[u v]M[u v]ᵀ — це чаша; її горизонтальний зріз E=const — еліпс.
# Головні осі еліпса — власні вектори M; що більше λ уздовж осі, то КОРОТША піввісь
# (E росте швидше → однакову висоту набираєш за менший крок). Кут = обидві півосі
# короткі (коло малого радіуса); край = один бік довгий (жолоб).

def fig_e_ellipse():
    W, H = 900, 380
    p = []

    def panel(cx, cy, a, b, ang, title, sub, col):
        # осі u,v
        R = 96
        p.append(line(cx - R, cy, cx + R, cy, color=MUTED, sw=1.2))
        p.append(line(cx, cy - R, cx, cy + R, color=MUTED, sw=1.2))
        p.append(text(cx + R + 4, cy + 4, "u", size=11, color=MUTED, anchor="start"))
        p.append(text(cx + 6, cy - R - 2, "v", size=11, color=MUTED))
        # еліпс E=const (обернений на ang градусів)
        p.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                 'fill-opacity="0.16" stroke="%s" stroke-width="2.4" '
                 'transform="rotate(%.1f %.1f %.1f)"/>'
                 % (cx, cy, a, b, col, col, ang, cx, cy))
        # головні осі-стрілки (власні вектори): вздовж малої півосі — велике λ
        import math as _m
        rad = _m.radians(ang)
        ca, sa = _m.cos(rad), _m.sin(rad)
        # піввісь a (по локальному x)
        p.append(arrow(cx, cy, cx + a * ca, cy + a * sa, color=col, sw=1.8))
        # піввісь b (по локальному y)
        p.append(arrow(cx, cy, cx - b * sa, cy + b * ca, color=col, sw=1.8))
        p.append(text(cx, cy - R - 24, title, size=13, bold=True))
        p.append(text(cx, cy - R - 8, sub, size=10, color=MUTED))

    # рівне: E майже не росте → величезний пологий еліпс (обидва λ малі)
    panel(150, 200, 92, 84, 0, "рівне поле",
          "λ₁,λ₂ малі → еліпс велетенський", MUTED)
    # край: круто впоперек, полого вздовж → довгий вузький жолоб (λ₁≫λ₂)
    panel(450, 200, 90, 22, 28, "край",
          "λ₁≫λ₂ → довгий вузький жолоб", NEG)
    # кут: круто в обидва боки → маленьке коло (обидва λ великі)
    panel(750, 200, 30, 24, 18, "кут",
          "λ₁,λ₂ великі → тісне коло", FIELD)

    # підпис-ключ унизу
    p.append(fitbox(150, 312, 600, 50,
                    "Одна ізолінія E = const. Що БІЛЬШЕ λ уздовж осі — то КОРОТША піввісь:\n"
                    "E набирає ту саму висоту за менший крок. Півосі ≈ 1/√λ.",
                    size=12, fill="#fbfcfd", stroke=LINE, sw=1.4, color=INK))

    render(os.path.join(OUT, "e-ellipse.svg"), W, H, *p,
           title="Ізолінія E = const — еліпс; його осі — власні вектори M")


# ── lineage: одна думка, чотири втілення (історія детекторів кутів) ────────────
# Часова вісь 1980→2006. Кожна віха: хто, чим міряв кут, і що саме додала —
# «точніше сформулювала» (зелене) чи «порахувала дешевше» (синє). Наскрізна
# думка (кут = зміна в усіх напрямах) незмінна; міняється лише як і чим лічать.

def fig_lineage():
    W, H = 980, 440
    p = []
    ax0, ax1 = 90, W - 60          # кінці осі часу
    ay = 100                       # рівень осі

    # наскрізна думка — стрічкою над віссю
    band, bw, bh = textbox(W / 2, 46,
                           "думка НЕЗМІННА: кут = різка зміна яскравості В УСІХ напрямах",
                           size=13, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.5)
    p.append(band)

    # сама вісь часу
    p.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2))
    p.append(text(ax1, ay - 12, "час", size=11, color=MUTED, anchor="end"))

    # чотири віхи: (частка по осі, рік, хто, формула, що додав, колір-акцент)
    #   колір: FIELD = «сказав точніше», NEG = «порахував дешевше»
    marks = [
        (0.02, "1980", "Моравек", "min(SSD) у 4 напрямах",
         "поставив питання:\nвіконце · зсув · мінімум", FIELD),
        (0.33, "1988", "Гарріс–Стівенз", "R = det − k·trace²",
         "матриця замість перебору;\nбез кореня — дешево", NEG),
        (0.62, "1994", "Ші–Томазі", "R = min(λ₁, λ₂)",
         "критерій прямо з трекінгу;\nчесніше, ціна — корінь", FIELD),
        (0.88, "2006", "Ростен–Драммонд", "кільце 16 + дерево ID3",
         "геть градієнти;\nправило ВИВЧЕНЕ з даних", NEG),
    ]

    cw, ch = 206, 152
    for frac, year, who, formula, gain, accent in marks:
        x = ax0 + frac * (ax1 - ax0)
        # вузол на осі + рік
        p.append(circle(x, ay, 7, fill=accent, stroke=BG, sw=2))
        p.append(text(x, ay - 22, year, size=14, color=INK, bold=True))
        # картка під віхою: хто / формула / що додав; не вилазити за поле
        cx = min(max(x, ax0 + cw / 2 - 26), ax1 - cw / 2 + 26)
        cy = ay + 42
        p.append(rect(cx - cw / 2, cy, cw, ch, fill=FILL, stroke=accent, sw=1.8, rx=8))
        p.append(text(cx, cy + 26, who, size=13, color=INK, bold=True))
        p.append(line(cx - cw / 2 + 14, cy + 38, cx + cw / 2 - 14, cy + 38,
                      color=MUTED, sw=1))
        p.append(fitbox(cx - cw / 2 + 10, cy + 46, cw - 20, 30, formula,
                        size=12, fill="#eef1f5", stroke=MUTED, sw=1.1,
                        color=INK, bold=True))
        p.append(fitbox(cx - cw / 2 + 10, cy + 84, cw - 20, 54, gain,
                        size=11, fill=BG, stroke="none", color=accent, bold=True))
        # тонка «пуповина» від осі до картки
        p.append(line(x, ay + 7, cx, cy, color=accent, sw=1.2, dash="3 3"))

    # легенда під усім
    ly = H - 24
    p.append(rect(140, ly - 11, 14, 14, fill=FIELD, stroke=BG, sw=1.5, rx=3))
    p.append(text(162, ly + 1, "сказав ТОЧНІШЕ, що таке кут",
                  size=11, color=INK, anchor="start"))
    p.append(rect(470, ly - 11, 14, 14, fill=NEG, stroke=BG, sw=1.5, rx=3))
    p.append(text(492, ly + 1, "порахував ДЕШЕВШЕ те саме",
                  size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Історія детекторів кутів: одна думка, чотири втілення")


if __name__ == "__main__":
    fig_window_shift()
    fig_eig_plane()
    fig_fast_circle()
    fig_m_build()
    fig_e_ellipse()
    fig_lineage()
    print("OK: figures written to", OUT)
