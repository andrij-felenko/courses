# -*- coding: utf-8 -*-
"""Фігури теми «Діючий струм (RMS) у перетворювачах».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід — у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_same_average():
    """Дві форми струму з ОДНАКОВИМ середнім, але різним RMS → різний нагрів.
    Зліва гладкий постійний 2 А; справа імпульси 0/4 А зі шпаруватістю 0.5.
    Середнє в обох 2 А, а RMS у другій більший → гріє сильніше."""
    W, H = 860, 430
    mid_y = 250            # рівень осі часу
    scale = 34            # пікселів на ампер
    frags = []

    def panel(x0, w, title, col):
        frags.append(rect(x0, 60, w, 300, fill=FILL, stroke=col, sw=1.8, rx=12))
        frags.append(text(x0 + w / 2, 88, title, size=14, color=col, bold=True))

    # ── ліва панель: гладкий постійний струм 2 А ──
    Lx, Lw = 40, 380
    panel(Lx, Lw, "Гладкий струм: рівно 2 А", NEG)
    ax, aw = Lx + 40, Lw - 80
    frags.append(line(ax, mid_y, ax + aw, mid_y, color=MUTED, sw=1.2))
    yflat = mid_y - 2 * scale
    frags.append(line(ax, yflat, ax + aw, yflat, color=NEG, sw=2.8))
    frags.append(line(ax, mid_y, ax, yflat, color=NEG, sw=1.2, dash="3,3"))
    frags.append(text(ax + aw / 2, yflat - 12, "i = 2 А весь час", size=12, color=NEG, bold=True))
    box, _, _ = textbox(Lx + Lw / 2, 322,
                        ["сер = 2 А    RMS = 2 А", "нагрів ∝ 2² = 4"],
                        size=13, fill="#eaf0fd", stroke=NEG)
    frags.append(box)

    # ── права панель: імпульси 0/4 А, D = 0.5 ──
    Rx, Rw = 440, 380
    panel(Rx, Rw, "Імпульси: 4 А половину часу", POS)
    bx, bw = Rx + 40, Rw - 80
    frags.append(line(bx, mid_y, bx + bw, mid_y, color=MUTED, sw=1.2))
    ypk = mid_y - 4 * scale
    yavg = mid_y - 2 * scale
    # меандр 0/4 А
    seg = bw / 4.0
    pts = []
    x = bx
    for k in range(2):
        pts += ["%.1f,%.1f" % (x, mid_y), "%.1f,%.1f" % (x, ypk),
                "%.1f,%.1f" % (x + seg, ypk), "%.1f,%.1f" % (x + seg, mid_y),
                "%.1f,%.1f" % (x + 2 * seg, mid_y)]
        x += 2 * seg
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), POS))
    frags.append(line(bx, yavg, bx + bw, yavg, color=NEG, sw=1.8, dash="6,4"))
    frags.append(text(bx + bw - 4, yavg - 8, "те саме середнє 2 А", size=11, color=NEG, anchor="end", bold=True))
    frags.append(text(bx + seg / 2, ypk - 10, "4 А", size=12, color=POS, bold=True))
    box, _, _ = textbox(Rx + Rw / 2, 322,
                        ["сер = 2 А    RMS = 2.83 А", "нагрів ∝ 2.83² = 8  — удвічі!"],
                        size=13, fill="#fdecea", stroke=POS)
    frags.append(box)

    render(os.path.join(OUT, "same-average.svg"), W, H, *frags,
           title="Однакове середнє — різний нагрів: гріє RMS, не середнє")


def fig_where_it_bites():
    """Мапа понижувального перетворювача: у КОЖНОМУ силовому вузлі свій діючий
    струм, і саме він задає нагрів. Вхідний кондер, верхній ключ, котушка,
    вихідний кондер — кожен зі своєю формулою RMS."""
    W, H = 900, 460
    frags = []
    y = 150               # рівень силової лінії
    # вузли зліва направо
    xin, xsw, xL, xout = 120, 340, 560, 780
    r = 26

    def node(cx, label, col):
        frags.append(circle(cx, y, r, fill=FILL, stroke=col, sw=2.2))
        frags.append(text(cx, y + 5, label, size=15, color=col, bold=True))

    # силова лінія
    frags.append(line(60, y, 840, y, color=INK, sw=2.4))
    frags.append(text(60, y - 12, "Vвх", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(840, y - 12, "Vвих", size=12, color=INK, anchor="end", bold=True))

    node(xsw, "SW", POS)          # верхній ключ
    node(xL, "L", FIELD)         # котушка
    # вхідний і вихідний конденсатори — вертикальні відводи на землю
    gy = y + 90
    frags.append(line(60, gy, 840, gy, color=INK, sw=2.4))          # земля
    for cx, col in ((xin, POS), (xout, NEG)):
        frags.append(line(cx, y, cx, y + 34, color=INK, sw=2))
        frags.append(line(cx - 16, y + 34, cx + 16, y + 34, color=col, sw=3))
        frags.append(line(cx - 16, y + 44, cx + 16, y + 44, color=col, sw=3))
        frags.append(line(cx, y + 44, cx, gy, color=INK, sw=2))
    frags.append(text(xin, y - 16, "Cвх", size=13, color=POS, bold=True))
    frags.append(text(xout, y - 16, "Cвих", size=13, color=NEG, bold=True))

    # картки з формулами RMS під кожним вузлом
    cards = [
        (xin, "Вхідний кондер", "RMS = I·√(D(1−D))", "рвані імпульси входу", POS),
        (xsw, "Верхній ключ", "RMS = I·√D", "струм тільки коли відкритий", POS),
        (xL, "Котушка", "RMS ≈ I (+ пульсація)", "гріє мідь обмотки", FIELD),
        (xout, "Вихідний кондер", "RMS = ΔI/√12", "лише трикутник пульсації", NEG),
    ]
    cy0 = 300
    for cx, name, formula, note, col in cards:
        w = 200
        frags.append(fitbox(cx - w / 2, cy0, w, 96,
                            name + "\n" + formula + "\n" + note,
                            size=12, fill=FILL, stroke=col, bold=False))

    frags.append(text(W / 2, 430, "у кожному вузлі свій діючий струм — за ним і рахують нагрів (I²·R) та добір деталі",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "where-it-bites.svg"), W, H, *frags,
           title="Де RMS кусає: чотири силові вузли понижувального перетворювача")


def fig_duty_curve():
    """Прямокутні імпульси амплітуди Ipk зі шпаруватістю D: як залежать від D
    середнє (D·Ipk), RMS (√D·Ipk) і форм-фактор RMS/сер = 1/√D. Малий D →
    гострі рідкі імпульси → форм-фактор злітає, RMS набагато вищий за середнє."""
    W, H = 820, 470
    L, R = 90, 700
    T, B = 80, 340
    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(text((L + R) / 2, B + 46, "шпаруватість D (частка часу, коли тече струм)", size=13, color=INK))
    frags.append(text(L - 54, (T + B) / 2, "частка від Ipk", size=13, color=INK))

    # осі: D від 0 до 1, значення від 0 до 1 (у частках Ipk)
    for k in range(0, 11, 2):
        d = k / 10.0
        x = L + d * (R - L)
        frags.append(line(x, B, x, B + 5, color=INK, sw=1.1))
        frags.append(text(x, B + 22, "%.1f" % d, size=11, color=MUTED))
    for k in range(0, 11, 2):
        v = k / 10.0
        yy = B - v * (B - T)
        frags.append(line(L - 5, yy, L, yy, color=INK, sw=1.1))
        frags.append(text(L - 12, yy + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))

    def curve(fn, col, sw=2.8, dash=None):
        pts = []
        for k in range(2, 101):
            d = k / 100.0
            v = fn(d)
            pts.append("%.1f,%.1f" % (L + d * (R - L), B - min(v, 1.0) * (B - T)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (" ".join(pts), col, sw, d))

    curve(lambda d: d, NEG)                     # середнє = D·Ipk
    curve(lambda d: math.sqrt(d), POS)          # RMS = √D·Ipk
    frags.append(text(L + 0.72 * (R - L), B - 0.86 * (B - T) - 6, "RMS = √D · Ipk", size=13, color=POS, bold=True))
    frags.append(text(L + 0.80 * (R - L), B - 0.80 * (B - T) + 20, "середнє = D · Ipk", size=13, color=NEG, bold=True))

    # відмітка: при малому D розрив великий
    dmark = 0.1
    xm = L + dmark * (R - L)
    yavg = B - dmark * (B - T)
    yrms = B - math.sqrt(dmark) * (B - T)
    frags.append(line(xm, yavg, xm, yrms, color=INK, sw=1.4, dash="3,3"))
    frags.append(circle(xm, yrms, 4, fill=POS, stroke=POS))
    frags.append(circle(xm, yavg, 4, fill=NEG, stroke=NEG))
    frags.append(text(xm + 10, (yavg + yrms) / 2, "D=0.1: RMS/сер = √10 ≈ 3.2×", size=12, color=INK, anchor="start", bold=True))

    box, _, _ = textbox((L + R) / 2, 420,
                        "форм-фактор RMS/середнє = 1/√D — що рідші й гостріші імпульси, то більший розрив",
                        size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "duty-curve.svg"), W, H, *frags,
           title="Прямокутні імпульси: середнє, RMS і форм-фактор від шпаруватості")


def fig_triangle_third():
    """Пилка від нуля до Ipk і її КВАДРАТ (парабола). Квадрат просідає біля нуля,
    злітає до вершини; площа під ним — третина прямокутника → RMS = Ipk/√3.
    Ліворуч форма, праворуч її квадрат із зафарбованою площею-третиною."""
    W, H = 860, 430
    frags = []

    def panel(x0, w, title, col):
        frags.append(rect(x0, 58, w, 300, fill=FILL, stroke=col, sw=1.8, rx=12))
        frags.append(text(x0 + w / 2, 84, title, size=14, color=col, bold=True))

    # ── ліва панель: пилка i(t) = Ipk·t/T ──
    Lx, Lw = 40, 380
    panel(Lx, Lw, "Струм: пилка 0 → Ipk", NEG)
    ax, aw = Lx + 46, Lw - 92
    base = 330                       # рівень осі часу
    top = 110                        # рівень вершини Ipk
    frags.append(line(ax, base, ax + aw, base, color=MUTED, sw=1.2))
    frags.append(line(ax, base, ax, top, color=MUTED, sw=1.2))
    # пилка: два зуби
    seg = aw / 2.0
    pts = []
    x = ax
    for k in range(2):
        pts += ["%.1f,%.1f" % (x, base), "%.1f,%.1f" % (x + seg, top),
                "%.1f,%.1f" % (x + seg, base)]
        x += seg
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), NEG))
    frags.append(text(ax - 8, top + 4, "Ipk", size=12, color=NEG, anchor="end", bold=True))
    # позначка половини часу → половина висоти
    hx = ax + seg / 2
    hy = (base + top) / 2
    frags.append(line(hx, base, hx, hy, color=INK, sw=1.0, dash="3,3"))
    frags.append(circle(hx, hy, 3.2, fill=NEG, stroke=NEG))
    frags.append(text(hx + 6, hy - 6, "½ часу → ½ висоти", size=10.5, color=INK, anchor="start"))

    # ── права панель: квадрат i² = Ipk²·(t/T)² — парабола ──
    Rx, Rw = 440, 380
    panel(Rx, Rw, "Квадрат i²: парабола", POS)
    bx, bw = Rx + 46, Rw - 92
    frags.append(line(bx, base, bx + bw, base, color=MUTED, sw=1.2))
    frags.append(line(bx, base, bx, top, color=MUTED, sw=1.2))
    # парабола (один зуб на всю ширину для наочності площі)
    ppts = ["%.1f,%.1f" % (bx, base)]
    N = 60
    for k in range(N + 1):
        f = k / float(N)
        px = bx + f * bw
        py = base - (f * f) * (base - top)
        ppts.append("%.1f,%.1f" % (px, py))
    ppts.append("%.1f,%.1f" % (bx + bw, base))
    frags.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(ppts), POS))
    # хорда-пряма (де був би трикутник — половина)
    frags.append(line(bx, base, bx + bw, top, color=MUTED, sw=1.4, dash="5,4"))
    frags.append(text(bx + bw - 4, top + 2, "Ipk²", size=12, color=POS, anchor="end", bold=True))
    frags.append(text(bx + bw * 0.30, base - (0.30 ** 2) * (base - top) - 34,
                      "пряма-хорда", size=10.5, color=MUTED, anchor="middle"))
    frags.append(text(bx + bw * 0.62, base - 22, "площа = ⅓", size=13, color=POS, bold=True))

    box, _, _ = textbox(W / 2, 398,
                        "⟨i²⟩ = Ipk²/3   →   Irms = Ipk/√3 ≈ 0.577·Ipk",
                        size=13.5, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "triangle-third.svg"), W, H, *frags,
           title="Чому Irms трикутника = Ipk/√3: квадрат — парабола, площа — третина")


def fig_trapezoid_split():
    """Трапеція струму котушки = стала I + трикутна пульсація a(t) навколо нуля.
    У квадраті (I+a)² перехресний член 2·I·a усереднюється в нуль (⟨a⟩=0), тож
    діючі складаються пітагорійськи: √(I² + ΔI²/12). Три панелі: трапеція,
    її розклад, і прямокутний трикутник складання діючих."""
    W, H = 900, 440
    frags = []
    base = 250
    scaleI = 90                      # де рівень I
    amp = 40                         # піврозмах пульсації у px

    # ── панель 1: трапеція котушки ──
    Lx, Lw = 30, 300
    frags.append(rect(Lx, 56, Lw, 250, fill=FILL, stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(Lx + Lw / 2, 82, "Струм котушки: трапеція", size=13, color=FIELD, bold=True))
    ax, aw = Lx + 40, Lw - 70
    frags.append(line(ax, base, ax + aw, base, color=MUTED, sw=1.2))
    yI = base - scaleI
    # трапеція: гойдання навколо yI
    seg = aw / 2.0
    tp = []
    x = ax
    for k in range(2):
        tp += ["%.1f,%.1f" % (x, yI + amp), "%.1f,%.1f" % (x + seg, yI - amp)]
        x += seg
    tp.append("%.1f,%.1f" % (ax + aw, yI + amp))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(tp), FIELD))
    frags.append(line(ax, yI, ax + aw, yI, color=NEG, sw=1.4, dash="6,4"))
    frags.append(text(ax - 8, yI + 4, "I", size=13, color=NEG, anchor="end", bold=True))
    frags.append(line(ax + aw + 6, yI - amp, ax + aw + 6, yI + amp, color=INK, sw=1.2))
    frags.append(text(ax + aw + 12, yI, "ΔI", size=11, color=INK, anchor="start", bold=True))

    # ── панель 2: розклад на I та a(t) ──
    Mx, Mw = 350, 250
    frags.append(rect(Mx, 56, Mw, 250, fill=FILL, stroke=INK, sw=1.4, rx=12))
    frags.append(text(Mx + Mw / 2, 82, "= стала I  +  пульсація a(t)", size=12.5, color=INK, bold=True))
    mx, mw = Mx + 34, Mw - 60
    # верх: стала I
    yc1 = 130
    frags.append(line(mx, yc1, mx + mw, yc1, color=NEG, sw=2.4))
    frags.append(text(mx - 6, yc1 + 4, "I", size=12, color=NEG, anchor="end", bold=True))
    frags.append(text(mx + mw + 6, yc1 + 4, "⟨I⟩=I", size=10, color=MUTED, anchor="start"))
    # низ: пульсація навколо нуля
    yc2 = 240
    frags.append(line(mx, yc2, mx + mw, yc2, color=MUTED, sw=1.1, dash="3,3"))
    seg2 = mw / 2.0
    ap = []
    x = mx
    for k in range(2):
        ap += ["%.1f,%.1f" % (x, yc2 + 22), "%.1f,%.1f" % (x + seg2, yc2 - 22)]
        x += seg2
    ap.append("%.1f,%.1f" % (mx + mw, yc2 + 22))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(ap), POS))
    frags.append(text(mx - 6, yc2 + 4, "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(mx + mw + 6, yc2 + 4, "⟨a⟩=0", size=10, color=POS, anchor="start", bold=True))

    # ── панель 3: пітагорійське складання діючих ──
    Rx, Rw = 620, 250
    frags.append(rect(Rx, 56, Rw, 250, fill=FILL, stroke=POS, sw=1.6, rx=12))
    frags.append(text(Rx + Rw / 2, 82, "Діючі складаються пітагорійськи", size=12, color=POS, bold=True))
    # прямокутний трикутник: катет I (гор.), катет ΔI/√12 (верт.), гіпотенуза RMS
    ox, oy = Rx + 55, 250
    catI = 150
    catA = 90
    frags.append(line(ox, oy, ox + catI, oy, color=NEG, sw=2.6))           # I
    frags.append(line(ox + catI, oy, ox + catI, oy - catA, color=POS, sw=2.6))  # ΔI/√12
    frags.append(line(ox, oy, ox + catI, oy - catA, color=INK, sw=2.6))    # RMS
    # прямий кут
    frags.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.1"/>'
                 % (ox + catI - 12, oy, ox + catI - 12, oy - 12, ox + catI, oy - 12, MUTED))
    frags.append(text(ox + catI / 2, oy + 18, "I", size=12, color=NEG, bold=True))
    frags.append(text(ox + catI + 8, oy - catA / 2, "ΔI/√12", size=11, color=POS, anchor="start", bold=True))
    frags.append(text(ox + catI / 2 - 16, oy - catA / 2 - 8, "IL(rms)", size=12, color=INK, bold=True))

    box, _, _ = textbox(W / 2, 396,
                        "IL(rms) = √(I² + ΔI²/12)   —   перехресний член 2·I·⟨a⟩ = 0, тож катети складаються під коренем",
                        size=12.5, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "trapezoid-split.svg"), W, H, *frags,
           title="Трапеція котушки: постійна + змінна складові, діючі — по Пітагору")


def fig_input_cap_shape():
    """Струм вхідного конденсатора: два рівні різного знаку — +I(1−D) частку D
    і −D·I решту. Ліворуч форма; праворуч функція D(1−D) (перевернута парабола,
    макс 0.25 при D=0.5) → RMS = I·√(D(1−D)), максимум 0.5·I."""
    W, H = 900, 450
    frags = []

    # ── ліва панель: форма струму конденсатора ──
    Lx, Lw = 30, 400
    frags.append(rect(Lx, 58, Lw, 300, fill=FILL, stroke=POS, sw=1.8, rx=12))
    frags.append(text(Lx + Lw / 2, 84, "Струм Cвх: два рівні, різний знак", size=13, color=POS, bold=True))
    ax, aw = Lx + 50, Lw - 90
    zero = 220                       # рівень нуля
    frags.append(line(ax, zero, ax + aw, zero, color=INK, sw=1.4))
    frags.append(text(ax - 8, zero + 4, "0", size=12, color=INK, anchor="end", bold=True))
    D = 0.35
    up = 70                          # +I(1−D) у px
    dn = 40                          # −D·I у px
    seg = aw / 2.0
    # два періоди меандру різної висоти вгору/вниз
    mp = []
    x = ax
    for k in range(2):
        mp += ["%.1f,%.1f" % (x, zero - up), "%.1f,%.1f" % (x + D * seg, zero - up),
               "%.1f,%.1f" % (x + D * seg, zero + dn), "%.1f,%.1f" % (x + seg, zero + dn),
               "%.1f,%.1f" % (x + seg, zero - up)]
        x += seg
    # прибрати останній стрибок вгору за межу
    mp = mp[:-1]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(mp), POS))
    frags.append(text(ax + D * seg / 2, zero - up - 8, "+I(1−D)", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(ax + (D + (1 - D) / 2) * seg, zero + dn + 16, "−D·I", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(ax + D * seg / 2, zero + 40, "D", size=10, color=MUTED))
    frags.append(text(ax + (D + (1 - D) / 2) * seg, zero - 8, "1−D", size=10, color=MUTED))
    box, _, _ = textbox(Lx + Lw / 2, 336,
                        "⟨iC²⟩ = I²·D(1−D)   (степені D скоротились)",
                        size=12, fill="#fdecea", stroke=POS)
    frags.append(box)

    # ── права панель: функція D(1−D) ──
    Rx, Rw = 460, 410
    frags.append(rect(Rx, 58, Rw, 300, fill=FILL, stroke=NEG, sw=1.6, rx=12))
    frags.append(text(Rx + Rw / 2, 84, "D(1−D): де найгарячіше", size=13, color=NEG, bold=True))
    gL, gR = Rx + 55, Rx + Rw - 30
    gT, gB = 120, 300
    frags.append(line(gL, gT, gL, gB, color=INK, sw=1.6))
    frags.append(line(gL, gB, gR, gB, color=INK, sw=1.6))
    frags.append(text((gL + gR) / 2, gB + 34, "шпаруватість D", size=12, color=INK))
    # осі
    for k in (0, 5, 10):
        d = k / 10.0
        x = gL + d * (gR - gL)
        frags.append(line(x, gB, x, gB + 4, color=INK, sw=1.0))
        frags.append(text(x, gB + 18, "%.1f" % d, size=10, color=MUTED))
    frags.append(text(gL - 8, gT + 4, "0.25", size=10, color=MUTED, anchor="end"))
    frags.append(line(gL - 4, gT, gL, gT, color=INK, sw=1.0))
    # парабола D(1−D), максимум 0.25 при 0.5 → відобразимо у висоту (gB..gT)
    pp = []
    N = 60
    for k in range(N + 1):
        d = k / float(N)
        v = d * (1 - d)              # 0..0.25
        px = gL + d * (gR - gL)
        py = gB - (v / 0.25) * (gB - gT)
        pp.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pp), NEG))
    # відмітка максимуму
    xm = gL + 0.5 * (gR - gL)
    frags.append(line(xm, gB, xm, gT, color=INK, sw=1.0, dash="3,3"))
    frags.append(circle(xm, gT, 4, fill=POS, stroke=POS))
    frags.append(text(xm + 8, gT + 16, "макс 0.25 → RMS = 0.5·I", size=11, color=POS, anchor="start", bold=True))

    box, _, _ = textbox(W / 2, 402,
                        "Iвх(rms) = I·√(D(1−D))   —   максимум 0.5·I при D = 0.5, нуль на кінцях",
                        size=12.5, fill="#eaf0fd", stroke=NEG)
    frags.append(box)
    render(os.path.join(OUT, "input-cap-shape.svg"), W, H, *frags,
           title="Вхідний конденсатор: два рівні різного знаку → RMS = I·√(D(1−D))")


if __name__ == "__main__":
    fig_same_average()
    fig_where_it_bites()
    fig_duty_curve()
    fig_triangle_third()
    fig_trapezoid_split()
    fig_input_cap_shape()
    print("ok figs")
