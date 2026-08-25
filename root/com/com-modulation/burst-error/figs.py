# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HOT = "#e8897d"   # зіпсований біт (пачка)


# ── Фігура 1: однакова кількість помилок, різна будова ────────────────────────
def fig_burst_vs_random():
    n, cw, x0 = 20, 30, 58
    W = x0 * 2 + n * cw           # 116 + 600 = 716
    H = 300
    p = []

    def bitrow(y, errs, label):
        p.append(text(x0, y - 15, label, size=15, anchor="start", bold=True))
        for i in range(n):
            x = x0 + i * cw
            if i in errs:
                p.append(rect(x, y, cw - 5, cw - 5, fill=HOT, stroke=POS, sw=2, rx=4))
                p.append(line(x + 7, y + 7, x + cw - 12, y + cw - 12, color="#7a1c12", sw=2))
                p.append(line(x + cw - 12, y + 7, x + 7, y + cw - 12, color="#7a1c12", sw=2))
            else:
                p.append(rect(x, y, cw - 5, cw - 5, fill=FILL, stroke="#cfd6dd", sw=1.2, rx=4))

    bitrow(74, {2, 8, 13, 17}, "Незалежні помилки — по одній подекуди (4 шт.)")
    bitrow(190, {9, 10, 11, 12}, "Пакетна помилка — ті самі 4, але підряд")

    # дужка довжини пачки під нижнім рядком
    bx1 = x0 + 9 * cw
    bx2 = x0 + 12 * cw + (cw - 5)
    by = 190 + (cw - 5) + 16
    p.append(line(bx1, by, bx2, by, color=INK, sw=1.6))
    p.append(line(bx1, by - 6, bx1, by + 6, color=INK, sw=1.6))
    p.append(line(bx2, by - 6, bx2, by + 6, color=INK, sw=1.6))
    p.append(text((bx1 + bx2) / 2, by + 22, "довжина пачки b = 4", size=14, color=INK))

    render(os.path.join(OUT, "burst-vs-random.svg"), W, H, *p,
           title="Однакова кількість помилок, різна будова")


# ── Фігура 2: перемішування розкидає пачку по словах ──────────────────────────
def fig_interleaving():
    cw, cols, rows = 38, 8, 4
    gw, gh = cols * cw, rows * cw     # 304 x 152
    gap = 96
    x0a = 74
    x0b = x0a + gw + gap              # 474
    y0 = 116
    W = x0b + gw + 46                 # 824
    H = 372
    labels = ["A", "B", "C", "D"]
    p = []

    def grid(gx, burst_cells, panel_title, subtitle, verdict, vcolor):
        p.append(text(gx + gw / 2, y0 - 44, panel_title, size=16, bold=True))
        p.append(text(gx + gw / 2, y0 - 24, subtitle, size=12.5, color=MUTED))
        for r in range(rows):
            p.append(text(gx - 15, y0 + r * cw + cw / 2 + 5, labels[r],
                          size=14, color=MUTED, anchor="end", bold=True))
            for c in range(cols):
                x, y = gx + c * cw, y0 + r * cw
                if (r, c) in burst_cells:
                    p.append(rect(x, y, cw, cw, fill=HOT, stroke=POS, sw=2, rx=3))
                    p.append(line(x + 9, y + 9, x + cw - 9, y + cw - 9, color="#7a1c12", sw=1.8))
                    p.append(line(x + cw - 9, y + 9, x + 9, y + cw - 9, color="#7a1c12", sw=1.8))
                else:
                    p.append(rect(x, y, cw, cw, fill=FILL, stroke="#cfd6dd", sw=1.2, rx=3))
        b, _, _ = textbox(gx + gw / 2, y0 + gh + 40, verdict, size=13,
                          fill="#ffffff", stroke=vcolor, color=vcolor, bold=True)
        p.append(b)

    grid(x0a, {(1, 2), (1, 3), (1, 4), (1, 5)},
         "Без перемішування", "сусіди в ефірі — з одного слова",
         "слово B: 4 помилки\nне виправити", POS)
    grid(x0b, {(0, 3), (1, 3), (2, 3), (3, 3)},
         "З перемішуванням", "сусіди в ефірі — з різних слів",
         "кожне слово: 1 помилка\nусі виправні", FIELD)

    render(os.path.join(OUT, "interleaving-spreads.svg"), W, H, *p,
           title="Перемішування перетворює пачку на розсіяні помилки")


# ── Фігура 3: модель Гілберта–Елліота (канал з пам'яттю) ──────────────────────
def fig_gilbert_elliott():
    W, H = 780, 392
    p = []
    gx, gy = 235, 205
    bx, by = 545, 205
    R = 70

    p.append(circle(gx, gy, R, fill="#eafaf0", stroke=FIELD, sw=2.5))
    p.append(text(gx, gy - 12, "Добрий", size=17, bold=True, color=FIELD))
    p.append(text(gx, gy + 10, "стан G", size=15, bold=True, color=FIELD))
    p.append(text(gx, gy + 34, "помилки рідко", size=12, color=MUTED))

    p.append(circle(bx, by, R, fill="#fdecea", stroke=POS, sw=2.5))
    p.append(text(bx, by - 12, "Поганий", size=17, bold=True, color=POS))
    p.append(text(bx, by + 10, "стан B", size=15, bold=True, color=POS))
    p.append(text(bx, by + 34, "помилки густо", size=12, color=MUTED))

    # переходи: G→B зверху, B→G знизу
    p.append(arrow(gx + R + 4, gy - 24, bx - R - 4, by - 24, color=INK, sw=2))
    p.append(text((gx + bx) / 2, gy - 34, "p (мала)", size=13, color=INK))
    p.append(arrow(bx - R - 4, by + 24, gx + R + 4, gy + 24, color=INK, sw=2))
    p.append(text((gx + bx) / 2, gy + 44, "r", size=13, color=INK))

    # самопетлі зверху кожного стану
    def selfloop(cx, cy, label):
        x1, x2, yt = cx - 24, cx + 24, cy - R
        p.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                 % (x1, yt, cx - 50, cy - R - 66, cx + 50, cy - R - 66, x2, yt, INK))
        p.append(text(cx, cy - R - 60, label, size=12, color=MUTED))

    selfloop(gx, gy, "1−p  (лишитись у доброму)")
    selfloop(bx, by, "1−r  (лишитись у поганому)")

    p.append(text(W / 2, H - 22, "поганий стан «липкий» — тому помилки йдуть пачкою",
                  size=13, color=INK, italic=True))

    render(os.path.join(OUT, "gilbert-elliott.svg"), W, H, *p,
           title="Модель Гілберта–Елліота: канал із пам'яттю")


# ── Фігура 4 (hist): дорога кодів проти пачок 1959 → 1982 ─────────────────────
def fig_fire_timeline():
    W, H = 1040, 300
    axis_y = 156
    p = []

    # вісь
    p.append(line(70, axis_y, W - 70, axis_y, color=MUTED, sw=2.5))
    p.append(arrow(W - 90, axis_y, W - 62, axis_y, color=MUTED, sw=2.5))

    centers = [150, 397, 643, 890]
    milestones = [
        ("1959", ["Коди Файра", "перші циклічні", "коди проти пачок"], True),
        ("1960", ["Рід–Соломон", "(лік символами);", "межа Райґера 2b"], False),
        ("1970", ["IBM 3330:", "код Файра в", "контролері диска"], False),
        ("1980–82", ["CD — CIRC:", "Рід–Соломон +", "перемішування"], False),
    ]

    for cx, (year, lines, hot) in zip(centers, milestones):
        yc = POS if hot else INK
        dot = HOT if hot else FILL
        dsr = POS if hot else MUTED
        r = 11 if hot else 8
        # рік над віссю
        p.append(text(cx, axis_y - 26, year, size=21, bold=True, color=yc))
        # вузол на осі
        p.append(circle(cx, axis_y, r, fill=dot, stroke=dsr, sw=2.5))
        # з'єднувач до рамки
        p.append(line(cx, axis_y + r, cx, axis_y + 34, color=MUTED, sw=1.4))
        # рамка-опис під віссю
        b, _, _ = textbox(cx, axis_y + 76, "\n".join(lines), size=13,
                          fill=("#fdecea" if hot else "#ffffff"),
                          stroke=dsr, color=INK, bold=False, min_w=150)
        p.append(b)

    render(os.path.join(OUT, "fire-timeline.svg"), W, H, *p,
           title="Дорога кодів проти пачок: 1959 → 1982")


# ── Фігура 5 (proj): розподіл помилок на слово — до і після перемішування ─────
def fig_proj_perword():
    W, H = 840, 452
    p = []
    # частка УРАЖЕНИХ слів (k≥1) з рівно k помилками каналу — спільна шкала 0..1
    left  = [("1", 0.209, False), ("2", 0.278, True), ("3", 0.275, True),
             ("4", 0.180, True), ("5", 0.048, True), ("6", 0.009, True), ("7", 0.003, True)]
    right = [("1", 0.937, False), ("2", 0.061, True), ("3", 0.002, True)]

    y0, Hbar = 350, 200          # базова лінія й повна висота (частка = 1.0)
    slotw, bw = 36, 24

    def yfor(f):
        return y0 - f * Hbar

    # горизонтальні лінії сітки 0/25/50/75/100 % через обидві панелі
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = yfor(f)
        p.append(line(74, gy, W - 26, gy, color="#e3e8ee", sw=1))
        p.append(text(62, gy + 4, "%d%%" % int(f * 100), size=11, color=MUTED, anchor="end"))

    def panel(px, bars, title, sub):
        barx0 = px + 34
        p.append(text(px + 154, 78, title, size=15, bold=True))
        p.append(text(px + 154, 98, sub, size=12, color=MUTED))
        for i, (lab, f, dead) in enumerate(bars):
            cx = barx0 + i * slotw + bw / 2
            h = f * Hbar
            col = HOT if dead else "#bfe8cf"
            p.append(rect(cx - bw / 2, y0 - h, bw, h, fill=col,
                          stroke=(POS if dead else FIELD), sw=1.4, rx=3))
            p.append(text(cx, y0 - h - 7, "%d%%" % round(f * 100), size=10.5, color=INK))
            p.append(text(cx, y0 + 18, lab, size=12, color=MUTED))
        # межа бюджету коду: між k=1 і k=2
        bxl = barx0 + slotw * 0.83
        p.append(line(bxl, y0 + 6, bxl, yfor(1.0) - 8, color=INK, sw=1.4, dash="4 4"))
        p.append(text(px + 154, y0 + 40, "помилок каналу у слові", size=12, color=MUTED))

    p.append(line(74, y0, W - 26, y0, color=INK, sw=1.6))   # базова лінія
    panel(94,  left,  "Без перемішування (D = 1)",  "мертвих слів (≥2): 516")
    panel(474, right, "Глибоке перемішування (D = 64)", "мертвих слів (≥2): лише 101")

    p.append(text(W / 2, 126, "ліворуч від пунктиру код лагодить; праворуч — мертві слова",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "proj-per-word.svg"), W, H, *p,
           title="Скільки помилок на слово: до і після перемішування")


# ── Фігура 6 (proj): залишковий BER залежно від глибини перемішування ─────────
def fig_proj_depth():
    import math
    W, H = 800, 452
    p = []
    depths = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    ber    = [0.003973, 0.004031, 0.003457, 0.003277, 0.002625,
              0.001500, 0.000629, 0.000145, 0.000145]

    xL, xR, yTop, yBot = 120, 700, 100, 366
    step = (xR - xL) / (len(depths) - 1)

    def xfor(i):
        return xL + i * step

    def yfor(b):     # напівлог: декади −2..−4 -> yTop..yBot
        return yTop + ((-2) - math.log10(b)) / ((-2) - (-4)) * (yBot - yTop)

    for d, lab in [(-2, "10⁻²"), (-3, "10⁻³"), (-4, "10⁻⁴")]:
        gy = yfor(10.0 ** d)
        p.append(line(xL, gy, xR, gy, color="#e3e8ee", sw=1))
        p.append(text(xL - 12, gy + 4, lab, size=12, color=MUTED, anchor="end"))

    p.append(line(xL, yTop - 12, xL, yBot, color=INK, sw=1.6))
    p.append(line(xL, yBot, xR, yBot, color=INK, sw=1.6))

    fy = yfor(0.000145)
    p.append(line(xL, fy, xR, fy, color=MUTED, sw=1.3, dash="5 4"))
    p.append(text(xR - 4, fy - 8, "підлога ≈ 1.4·10⁻⁴", size=11.5, color=MUTED, anchor="end"))

    for span, lab, ty in [(33.4, "середня пачка ≈ 33 біт", 66),
                          (169.0, "найдовша ≈ 169 біт", 84)]:
        gx = xfor(math.log2(span))          # depths = 2⁰..2⁸, індекс = log2
        p.append(line(gx, yTop - 12, gx, yBot, color=POS, sw=1.2, dash="3 4"))
        p.append(text(gx, ty, lab, size=11.5, color=POS))

    pts = [(xfor(i), yfor(b)) for i, b in enumerate(ber)]
    for a, bpt in zip(pts, pts[1:]):
        p.append(line(a[0], a[1], bpt[0], bpt[1], color=NEG, sw=2.4))
    for (x, y), d in zip(pts, depths):
        p.append(circle(x, y, 4.5, fill=NEG, stroke="#ffffff", sw=1.5))
        p.append(text(x, yBot + 20, str(d), size=11.5, color=INK))

    p.append(text((xL + xR) / 2, yBot + 42, "глибина перемішування D (слів)", size=13, color=INK))
    p.append(text(xL - 6, yTop - 24, "залишковий BER даних (напівлог)", size=12.5,
                  color=INK, anchor="start"))

    render(os.path.join(OUT, "proj-residual-depth.svg"), W, H, *p,
           title="Залишок помилок vs глибина: обрив за довжиною пачки")


# ── Фігура 7 (math): чому множник два — вікно 2b (виведення межі Райґера) ──────
def fig_reiger_window():
    n, pitch, cs = 16, 34, 30
    x0, yrow = 70, 108
    W = x0 * 2 + n * pitch            # 140 + 544 = 684
    H = 300
    b, a0 = 4, 4                      # ширина пачки; початок пачки A
    p = []

    for i in range(n):
        x = x0 + i * pitch
        if a0 <= i < a0 + b:
            p.append(rect(x, yrow, cs, cs, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
        elif a0 + b <= i < a0 + 2 * b:
            p.append(rect(x, yrow, cs, cs, fill="#fdecea", stroke=POS, sw=2, rx=4))
        else:
            p.append(rect(x, yrow, cs, cs, fill=FILL, stroke="#cfd6dd", sw=1.2, rx=4))

    axc = x0 + (a0 + b / 2) * pitch
    bxc = x0 + (a0 + b + b / 2) * pitch
    p.append(text(axc, yrow - 16, "пачка тут", size=13, color=NEG, bold=True))
    p.append(text(bxc, yrow - 16, "пачка на b далі", size=13, color=POS, bold=True))

    sx = x0 + (a0 + b) * pitch - (pitch - cs) / 2
    p.append(line(sx, yrow - 6, sx, yrow + cs + 6, color=INK, sw=1.4, dash="4 3"))

    wx1 = x0 + a0 * pitch - 2
    wx2 = x0 + (a0 + 2 * b - 1) * pitch + cs + 2
    by = yrow + cs + 24
    p.append(line(wx1, by, wx2, by, color=INK, sw=1.6))
    p.append(line(wx1, by - 7, wx1, by + 7, color=INK, sw=1.6))
    p.append(line(wx2, by - 7, wx2, by + 7, color=INK, sw=1.6))
    p.append(text((wx1 + wx2) / 2, by + 22, "вікно 2b = 8 позицій", size=14, color=INK, bold=True))

    p.append(text(W / 2, by + 50,
                  "усі 2²ᵇ візерунки цього вікна потребують різних синдромів  →  n − k ≥ 2b",
                  size=13, color=INK))

    render(os.path.join(OUT, "reiger-window.svg"), W, H, *p,
           title="Пачка вміє зсуватися — і зсув коштує ще b")


# ── Фігура 8 (math): де стоять коди відносно межі (ефективність z) ─────────────
def fig_burst_efficiency():
    W, H = 720, 300
    ax0, ax1, ay = 100, 620, 168
    span = ax1 - ax0                 # 520
    p = []

    def zx(z):
        return ax0 + z * span

    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    for z, lab in [(0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")]:
        x = zx(z)
        p.append(line(x, ay - 5, x, ay + 5, color=INK, sw=1.5))
        p.append(text(x, ay + 22, lab, size=12, color=MUTED))

    p.append(text(ax0 - 8, ay - 44, "ефективність  z = 2b / (n − k)", size=14,
                  anchor="start", bold=True))

    xc = zx(1.0)
    p.append(line(xc, ay - 60, xc, ay + 8, color=FIELD, sw=2, dash="5 4"))
    p.append(circle(xc, ay, 7, fill=FIELD, stroke=FIELD, sw=2))
    b1, _, _ = textbox(xc - 96, ay - 84, "межа Райґера\nоптимум: перемішане [3λ, λ]",
                       size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    p.append(b1)

    xf = zx(0.6875)
    p.append(circle(xf, ay, 7, fill=POS, stroke=POS, sw=2))
    b2, _, _ = textbox(xf, ay + 68, "Fire 802.3ap (2112, 2080)\nb = 11 · 32 надлишок · z ≈ 0.69",
                       size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    p.append(b2)

    p.append(arrow(xf + 9, ay - 30, xc - 9, ay - 30, color=INK, sw=1.6))
    p.append(arrow(xc - 9, ay - 30, xf + 9, ay - 30, color=INK, sw=1.6))
    p.append(text((xf + xc) / 2, ay - 38, "змарновано ≈ 1/3", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "burst-efficiency.svg"), W, H, *p,
           title="Де стоять коди відносно межі Райґера")


# ── Фігура 9 (math): перемішування [3,1] сідає точно на межу ───────────────────
def fig_interleave_bound():
    W, H = 760, 450
    p = []
    rows = ["A", "B", "C"]
    cell = 50
    gx, gy = 120, 92
    burst_slots = {3, 4, 5}

    def slot(r, c):
        return c * 3 + r + 1          # передаємо стовпець за стовпцем

    p.append(text(gx + 1.5 * cell, gy - 34, "таблиця перемішувача (рядок = слово [3,1])",
                  size=13, bold=True))
    for r in range(3):
        p.append(text(gx - 16, gy + r * cell + cell / 2 + 5, rows[r],
                      size=15, color=MUTED, anchor="end", bold=True))
        for c in range(3):
            x, y = gx + c * cell, gy + r * cell
            s = slot(r, c)
            hot = s in burst_slots
            p.append(rect(x, y, cell, cell,
                          fill="#fdecea" if hot else FILL,
                          stroke=POS if hot else "#cfd6dd", sw=2 if hot else 1.2, rx=4))
            p.append(text(x + cell / 2, y + cell / 2 + 6, str(s),
                          size=16, color=POS if hot else INK, bold=hot))
    p.append(text(gx + 1.5 * cell, gy + 3 * cell + 26,
                  "передаємо стовпець за стовпцем:  1,2,3 · 4,5,6 · 7,8,9",
                  size=12, color=MUTED))

    sx, sy, cw2 = 120, 302, 46
    p.append(text(sx, sy - 14, "ефір (порядок передачі)", size=13, anchor="start", bold=True))
    for i in range(9):
        s = i + 1
        x = sx + i * (cw2 + 6)
        hot = s in burst_slots
        p.append(rect(x, sy, cw2, cw2,
                      fill="#fdecea" if hot else FILL,
                      stroke=POS if hot else "#cfd6dd", sw=2 if hot else 1.2, rx=4))
        p.append(text(x + cw2 / 2, sy + cw2 / 2 + 6, str(s),
                      size=15, color=POS if hot else INK, bold=hot))
    bx1 = sx + 2 * (cw2 + 6)
    bx2 = sx + 4 * (cw2 + 6) + cw2
    by = sy + cw2 + 14
    p.append(line(bx1, by, bx2, by, color=POS, sw=1.6))
    p.append(line(bx1, by - 6, bx1, by + 6, color=POS, sw=1.6))
    p.append(line(bx2, by - 6, bx2, by + 6, color=POS, sw=1.6))
    p.append(text((bx1 + bx2) / 2, by + 20, "пачка завдовжки 3", size=13, color=POS, bold=True))

    box, _, _ = textbox(W / 2, H - 36,
                        "рядки C, A, B — по одній помилці на слово   ·   b = 3,  n − k = 3·2 = 6 = 2b   ·   z = 1",
                        size=13, fill="#eafaf0", stroke=FIELD, color=INK)
    p.append(box)

    render(os.path.join(OUT, "interleave-meets-bound.svg"), W, H, *p,
           title="Перемішування [3,1] сідає точно на межу")


if __name__ == "__main__":
    fig_burst_vs_random()
    fig_interleaving()
    fig_gilbert_elliott()
    fig_fire_timeline()
    fig_proj_perword()
    fig_proj_depth()
    fig_reiger_window()
    fig_burst_efficiency()
    fig_interleave_bound()
    print("OK: figures written to", OUT)
