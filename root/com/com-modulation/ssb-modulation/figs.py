# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори за змістом (як у сусідній статті AM/FM)
MSG = FIELD   # корисне / бічна смуга (зелене)
CAR = NEG     # несуча / опора (синє)
HOT = POS     # акцент-небезпека / зсув (червоне)
LO = MUTED    # другорядне


# ── Фігура 1: еволюція спектра AM → DSB-SC → SSB ─────────────────────────────

def fig_spectrum_cut():
    W, H = 800, 640
    x0, x1 = 110, 700
    fc = 430          # несуча по центру
    fm = 95           # відступ бічної смуги
    fl, fu = fc - fm, fc + fm

    def stick(ay, fx, h, col, lbl):
        out = line(fx, ay, fx, ay - h, color=col, sw=3.4)
        out += line(fx, ay - 3, fx, ay + 3, color=MUTED, sw=1.2)
        out += text(fx, ay + 18, lbl, size=11, color=col, bold=True)
        return out

    p = []

    def row(ay, name, note, note_col, carrier, draw_lower, band):
        out = line(x0, ay, x1, ay, color=INK, sw=1.5)
        out += arrow(x1 - 20, ay, x1, ay, color=INK, sw=1.5)
        out += text(x1 + 8, ay + 5, "f", size=14, color=INK, italic=True, anchor="start")
        out += text(24, ay + 5, name, size=15, color=INK, bold=True, anchor="start")
        if carrier == "on":
            out += stick(ay, fc, 104, CAR, "fₒ")
        elif carrier == "off":
            out += line(fc, ay, fc, ay - 104, color=MUTED, sw=1.4, dash="4 5")
            out += text(fc, ay - 114, "✕ несучу вимкнено", size=11, color=HOT, bold=True)
        if draw_lower:
            out += stick(ay, fl, 50, MSG, "fₒ−fₘ")
        out += stick(ay, fu, 50, MSG, "fₒ+fₘ")
        if note:
            out += text((x0 + x1) / 2 + 55, ay - 125, note, size=11.5, color=note_col, bold=True)
        if band:
            bl, br, blbl = band
            yb = ay + 36
            out += line(bl, yb, br, yb, color=INK, sw=1.4)
            out += line(bl, yb - 5, bl, yb + 5, color=INK, sw=1.4)
            out += line(br, yb - 5, br, yb + 5, color=INK, sw=1.4)
            out += text((bl + br) / 2, yb + 16, blbl, size=11.5, color=INK, bold=True)
        return out

    p.append(row(185, "AM", "несуча: 2/3 потужності, 0 інформації", HOT,
                 "on", True, (fl, fu, "смуга = 2·fₘ")))
    p.append(row(375, "DSB-SC", None, LO,
                 "off", True, None))
    p.append(row(565, "SSB", "одна смуга — уся потужність у ділі", MSG,
                 None, False, (fc, fu, "смуга = fₘ")))

    render(os.path.join(OUT, "spectrum-cut.svg"), W, H, *p,
           title="Від AM до SSB: викидаємо несучу й зайву бічну смугу")


# ── Фігура 2: зсув гетеродина ламає голос («каченя Дональд») ──────────────────

def fig_pitch_shift():
    W, H = 820, 420
    p = []
    SC = 0.27          # px на Гц
    ay = 250
    harm = [(200, 92), (400, 74), (600, 58), (800, 48)]

    def panel(px, title, tcol, shifted):
        ax0 = px + 30
        ax1 = px + 350
        out = line(ax0, ay, ax1, ay, color=INK, sw=1.5)
        out += arrow(ax1 - 20, ay, ax1, ay, color=INK, sw=1.5)
        out += text(ax1 + 4, ay + 16, "частота", size=10.5, color=MUTED, anchor="end")
        out += text(px + 190, 62, title, size=13, color=tcol, bold=True)
        sub = "усе піднялося на однакове Δf" if shifted else "гармоніки на своїх місцях"
        out += text(px + 190, 82, sub, size=10.5, color=LO)
        df = 150 if shifted else 0
        for hz, h in harm:
            if shifted:
                gx = ax0 + hz * SC
                out += line(gx, ay, gx, ay - h, color=MUTED, sw=1.4, dash="3 4")
                sx = ax0 + (hz + df) * SC
                out += line(sx, ay, sx, ay - h, color=HOT, sw=3.4)
                out += arrow(gx + 3, ay - h - 8, sx - 3, ay - h - 8, color=MUTED, sw=1.2)
                out += text(sx, ay + 18, "%d" % (hz + df), size=10.5, color=HOT, bold=True)
            else:
                sx = ax0 + hz * SC
                out += line(sx, ay, sx, ay - h, color=MSG, sw=3.4)
                out += text(sx, ay + 18, "%d" % hz, size=10.5, color=MSG, bold=True)
        ratio = "350 : 550 : 750  ≠  1 : 2 : 3" if shifted else "200 : 400 : 600  =  1 : 2 : 3"
        out += text(px + 190, ay + 52, ratio, size=12, color=(HOT if shifted else MSG), bold=True)
        return out

    p.append(panel(10, "гетеродин точний", MSG, False))
    p.append(panel(420, "гетеродин зсунуто на Δf", HOT, True))
    p.append(line(410, 58, 410, 328, color=MUTED, sw=1.0, dash="2 5"))

    b, bw, bh = textbox(W / 2, 398,
                        "Зсув, а не розтяг: відношення гармонік ламаються — і голос звучить «каченям».",
                        size=12, color=INK, bold=True, min_w=560)
    p.append(b)

    render(os.path.join(OUT, "pitch-shift.svg"), W, H, *p,
           title="Похибка гетеродина зсуває весь голос угору")


# ── Фігура 3: два способи вирізати одну смугу ────────────────────────────────

def blk(x, y, w, h, s, col=CAR, fill="#eef2fd"):
    return fitbox(x, y, w, h, s, size=11.5, bold=True, stroke=col, fill=fill, color=INK)


def fig_generation():
    W, H = 860, 380
    p = []

    # ── Рядок 1: фільтровий метод ──
    p.append(text(26, 74, "Фільтром", size=14, color=INK, bold=True, anchor="start"))
    y1, h1, w1 = 86, 60, 138
    cy1 = y1 + h1 / 2
    xs = [25, 185, 345, 505, 665]
    labels = ["звук\nm(t)", "балансний\nмодулятор\n(× несуча)", "DSB-SC:\nдві смуги",
              "гострий\nфільтр", "SSB:\nодна смуга"]
    cols = [MSG, CAR, CAR, HOT, MSG]
    fills = ["#eef6ef", "#eef2fd", "#eef2fd", "#fdecea", "#eef6ef"]
    for x, s, c, f in zip(xs, labels, cols, fills):
        p.append(blk(x, y1, w1, h1, s, col=c, fill=f))
    for i in range(len(xs) - 1):
        p.append(arrow(xs[i] + w1, cy1, xs[i + 1], cy1, color=INK, sw=1.8))

    # ── Рядок 2: фазовий метод ──
    p.append(text(26, 186, "Фазуванням", size=14, color=INK, bold=True, anchor="start"))
    a0 = (25, 250, 92, 46)     # звук
    a1 = (255, 205, 150, 46)   # × несуча 0°
    a2 = (210, 300, 150, 46)   # Гільберт 90°
    a3 = (410, 300, 150, 46)   # × несуча 90°
    aS = (615, 250, 60, 46)    # Σ
    aO = (715, 250, 125, 46)   # SSB

    p.append(blk(*a0, "звук", col=MSG, fill="#eef6ef"))
    p.append(blk(*a1, "× несуча (0°)", col=CAR))
    p.append(blk(*a2, "Гільберт:\nзсув 90°", col=CAR))
    p.append(blk(*a3, "× несуча (90°)", col=CAR))
    p.append(blk(*aS, "Σ\nдодати", col=HOT, fill="#fdecea"))
    p.append(blk(*aO, "SSB:\nодна смуга", col=MSG, fill="#eef6ef"))

    ox, oy = a0[0] + a0[2], a0[1] + a0[3] / 2   # правий центр «звуку»
    p.append(arrow(ox, oy - 4, a1[0], a1[1] + a1[3] / 2, color=INK, sw=1.7))
    p.append(arrow(ox, oy + 4, a2[0], a2[1] + a2[3] / 2, color=INK, sw=1.7))
    p.append(arrow(a2[0] + a2[2], a2[1] + a2[3] / 2, a3[0], a3[1] + a3[3] / 2, color=INK, sw=1.7))
    p.append(arrow(a1[0] + a1[2], a1[1] + a1[3] / 2, aS[0], aS[1] + aS[3] / 2 - 4, color=INK, sw=1.7))
    p.append(arrow(a3[0] + a3[2], a3[1] + a3[3] / 2, aS[0], aS[1] + aS[3] / 2 + 4, color=INK, sw=1.7))
    p.append(arrow(aS[0] + aS[2], aS[1] + aS[3] / 2, aO[0], aO[1] + aO[3] / 2, color=INK, sw=1.8))
    p.append(text(aO[0] + aO[2] / 2, aO[1] + aO[3] + 18, "одна смуга гаситься",
                  size=10.5, color=MSG, bold=True))

    render(os.path.join(OUT, "generation.svg"), W, H, *p,
           title="Дві дороги до однієї смуги: різати фільтром чи гасити фазою")


# ── Фігура 4 (hist): часова вісь народження SSB ──────────────────────────────

def fig_timeline():
    W, H = 940, 480
    x0, x1 = 118, 852
    axy = 250
    yr0, yr1 = 1915, 1928

    def X(y):
        return x0 + (y - yr0) / (yr1 - yr0) * (x1 - x0)

    p = []
    # вісь часу
    p.append(line(x0 - 26, axy, x1 + 34, axy, color=INK, sw=2))
    p.append(arrow(x1 + 14, axy, x1 + 40, axy, color=INK, sw=2))
    p.append(text(x1 + 46, axy + 5, "рік", size=12, color=MUTED, anchor="start"))

    # (рік, бік: +1 угору / −1 униз, колір, заливка, рядки)
    events = [
        (1915, +1, CAR, "#eef2fd", ["1 груд. 1915", "Карсон подає", "заявку на SSB"]),
        (1918, -1, MSG, "#eef6ef", ["1918", "SSB — стандарт", "дротових ліній"]),
        (1923, +1, CAR, "#eef2fd", ["27 бер. 1923", "патент США", "№ 1 449 382"]),
        (1924, -1, CAR, "#eef2fd", ["1924", "Гартлі:", "фазовий метод"]),
        (1927, +1, MSG, "#eef6ef", ["7 січ. 1927", "трансатлантик", "Н-Й ↔ Лондон"]),
        (1928, -1, CAR, "#eef2fd", ["1928", "патент Гартлі", "№ 1 666 206"]),
    ]
    for yr, side, col, fill, lines in events:
        x = X(yr)
        cy = 148 if side > 0 else 352
        box, w, h = textbox(x, cy, "\n".join(lines), size=12, bold=True,
                            stroke=col, fill=fill, color=INK, min_w=120)
        edge = cy + (h / 2 if side > 0 else -h / 2)
        p.append(line(x, axy, x, edge, color=col, sw=1.6, dash="4 3"))
        p.append(circle(x, axy, 6, fill=col, stroke=col, sw=1.5))
        p.append(box)

    # легенда — розрізнення «ідея/патент» vs «робоча система»
    ly = 446
    p.append(circle(150, ly, 7, fill=CAR, stroke=CAR, sw=1.5))
    p.append(text(164, ly + 5, "ідея та патент", size=12.5, color=INK, anchor="start", bold=True))
    p.append(circle(360, ly, 7, fill=MSG, stroke=MSG, sw=1.5))
    p.append(text(374, ly + 5, "перша робоча система (спершу дріт, тоді ефір)",
                  size=12.5, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Народження SSB: від заявки Карсона до лінії через океан")


# ── Вставка math-phasing-cancellation ────────────────────────────────────────

def arc_arrow(cx, cy, r, a0, a1, color, sw=2.2):
    """Дугова стрілка; кути в градусах, матем. конвенція (CCW+, 0=+x). SVG y — вниз."""
    a0r, a1r = math.radians(a0), math.radians(a1)
    x0, y0 = cx + r * math.cos(a0r), cy - r * math.sin(a0r)
    x1, y1 = cx + r * math.cos(a1r), cy - r * math.sin(a1r)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 0 if a1 > a0 else 1
    return ('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))


# ── Фігура 5: гра знаків у частотній області (одна смуга гасне) ───────────────

def fig_sideband_cancel():
    W, H = 880, 640
    x0, x1 = 210, 700
    fc = 455
    fm = 85
    fl, fu = fc - fm, fc + fm
    SC = 116          # px на «½»

    def stick(ay, fx, val, col, lbl):
        h = abs(val) * SC
        y2 = ay - h if val > 0 else ay + h
        out = line(fx, ay, fx, y2, color=col, sw=4)
        out += line(fx - 3, ay, fx + 3, ay, color=INK, sw=1.0)
        ly = y2 - 10 if val > 0 else y2 + 20
        out += text(fx, ly, lbl, size=13, color=col, bold=True)
        return out

    def row(ay, name, sub, sticks):
        out = line(x0, ay, x1, ay, color=INK, sw=1.5)
        out += arrow(x1 - 20, ay, x1, ay, color=INK, sw=1.5)
        out += text(x1 + 8, ay + 5, "ω", size=14, color=INK, italic=True, anchor="start")
        out += text(30, ay - 6, name, size=14, color=INK, bold=True, anchor="start")
        out += text(30, ay + 13, sub, size=11.5, color=MUTED, anchor="start")
        out += line(fc, ay - 130, fc, ay + 30, color=MUTED, sw=1.0, dash="3 6")
        for fx, val, col, lbl in sticks:
            out += stick(ay, fx, val, col, lbl)
        return out

    p = []
    p.append(row(165, "шлях I", "m·cos(ωc t)",
                 [(fl, +0.5, CAR, "+½"), (fu, +0.5, CAR, "+½")]))
    p.append(row(340, "шлях Q", "−m̂·sin(ωc t)",
                 [(fl, -0.5, HOT, "−½"), (fu, +0.5, CAR, "+½")]))
    p.append(row(505, "сума  I + Q", "нижня гасне, верхня подвоюється",
                 [(fu, +1.0, MSG, "+1")]))
    p.append(text(fl, 505 - 8, "0", size=13, color=HOT, bold=True))
    p.append(text(fl, 505 + 22, "гасне", size=11, color=HOT, bold=True))

    p.append(text(fl, 505 + 46, "ωc−ωₘ", size=12, color=INK))
    p.append(text(fu, 505 + 46, "ωc+ωₘ", size=12, color=INK))
    p.append(text(fc, 505 + 46, "ωc", size=11, color=MUTED))

    b, bw, bh = textbox(W / 2, 610,
                        "Різницева частота ωc−ωₘ стоїть у двох шляхів однаково → при відніманні гасне.\n"
                        "Сумарна ωc+ωₘ, навпаки, додається у фазі → подвоюється: лишається верхня смуга.",
                        size=12, color=INK, bold=True, min_w=720)
    p.append(b)

    render(os.path.join(OUT, "sideband-cancel.svg"), W, H, *p,
           title="Гра знаків: одна смуга додається, друга сама себе гасить")


# ── Фігура 6: обертання на IQ-площині — напрям задає смугу ────────────────────

def fig_iq_rotation():
    W, H = 900, 400
    p = []
    R = 72
    th = 52                      # миттєвий кут ωₘt
    cy = 168
    centers = [168, 460, 752]

    def axes(cx):
        out = line(cx - 100, cy, cx + 100, cy, color=MUTED, sw=1.2)
        out += arrow(cx + 90, cy, cx + 100, cy, color=MUTED, sw=1.2)
        out += line(cx, cy + 100, cx, cy - 100, color=MUTED, sw=1.2)
        out += arrow(cx, cy - 90, cx, cy - 100, color=MUTED, sw=1.2)
        out += text(cx + 106, cy + 5, "I", size=12, color=MUTED, italic=True, anchor="start")
        out += text(cx + 8, cy - 104, "Q", size=12, color=MUTED, italic=True, anchor="start")
        return out

    def phasor(cx, ang, length, col, sw=3.4, dot=True):
        ar = math.radians(ang)
        x = cx + length * math.cos(ar)
        y = cy - length * math.sin(ar)
        out = arrow(cx, cy, x, y, color=col, sw=sw)
        if dot:
            out += circle(x, y, 3.6, fill=col, stroke=col, sw=1)
        return out, x, y

    # Панель 1: справжній звук = дві протилежні обертанки
    cx = centers[0]
    p.append(axes(cx))
    ph1, x1p, y1p = phasor(cx, th, R * 0.5, MSG, sw=3.0)
    ph2, x2p, y2p = phasor(cx, -th, R * 0.5, HOT, sw=3.0)
    p.append(ph1)
    p.append(ph2)
    sx = cx + R * math.cos(math.radians(th))
    p.append(line(x1p, y1p, sx, cy, color=MUTED, sw=1.0, dash="2 4"))
    p.append(line(x2p, y2p, sx, cy, color=MUTED, sw=1.0, dash="2 4"))
    p.append(circle(sx, cy, 4.2, fill=INK, stroke=INK, sw=1))
    p.append(arc_arrow(cx, cy, R * 0.5 + 12, th + 12, th + 44, MSG, 2.0))
    p.append(arc_arrow(cx, cy, R * 0.5 + 12, -th - 12, -th - 44, HOT, 2.0))

    # Панель 2: аналітичний сигнал = одна CCW
    cx = centers[1]
    p.append(axes(cx))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1" stroke-dasharray="3 4"/>' % (cx, cy, R, MUTED))
    ph, _, _ = phasor(cx, th, R, MSG, sw=3.6)
    p.append(ph)
    p.append(arc_arrow(cx, cy, R + 12, th + 14, th + 58, MSG, 2.2))

    # Панель 3: зміна знаку → одна CW
    cx = centers[2]
    p.append(axes(cx))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1" stroke-dasharray="3 4"/>' % (cx, cy, R, MUTED))
    ph, _, _ = phasor(cx, -th, R, HOT, sw=3.6)
    p.append(ph)
    p.append(arc_arrow(cx, cy, R + 12, -th - 14, -th - 58, HOT, 2.2))

    caps = [
        (centers[0], "справжній звук  cos(ωₘt)", "½ ⟲  +  ½ ⟳  →  дві смуги", INK),
        (centers[1], "аналітичний  exp(+iωₘt)", "лише ⟲ проти год. →  USB", MSG),
        (centers[2], "зміна знаку  exp(−iωₘt)", "лише ⟳ за год. →  LSB", HOT),
    ]
    for cx, t1, t2, col in caps:
        p.append(text(cx, cy + 128, t1, size=13, color=INK, bold=True))
        p.append(text(cx, cy + 150, t2, size=12, color=col, bold=True))

    p.append(line(304, 70, 304, 300, color=MUTED, sw=1.0, dash="2 6"))
    p.append(line(600, 70, 600, 300, color=MUTED, sw=1.0, dash="2 6"))

    render(os.path.join(OUT, "iq-rotation.svg"), W, H, *p,
           title="Напрям обертання комплексної обвідної задає бічну смугу")


# ── Фігура 7: пригнічення чужої смуги від похибки фази ────────────────────────

def fig_suppression():
    W, H = 760, 490
    px0, px1 = 120, 680          # ε: 0 … 5°
    py0, py1 = 70, 390           # dB: 60 (верх) … 20 (низ)
    emax = 5.0

    def X(e):
        return px0 + (e / emax) * (px1 - px0)

    def Y(db):
        return py1 - (db - 20) / 40.0 * (py1 - py0)

    p = []
    for db in range(20, 61, 10):
        y = Y(db)
        p.append(line(px0, y, px1, y, color="#e5e7eb", sw=1.0))
        p.append(text(px0 - 12, y + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
    for e in range(0, 6):
        x = X(e)
        p.append(line(x, py0, x, py1, color="#eef0f2", sw=1.0))
        p.append(text(x, py1 + 20, "%d°" % e, size=11, color=MUTED))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.5))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.5))
    p.append(text(px1, py1 + 40, "похибка фази ε", size=12.5, color=INK, anchor="end"))
    p.append(text(px0 - 44, py0 - 18, "пригнічення, дБ", size=12.5, color=INK, anchor="start"))

    # крива S(ε) = −20·log₁₀( tan(ε/2) )
    pts = []
    e = 0.2
    while e <= emax + 1e-9:
        db = -20.0 * math.log10(math.tan(math.radians(e) / 2.0))
        if db <= 60:
            pts.append((X(e), Y(db)))
        e += 0.1
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, MSG))

    ex, ey = X(1.0), Y(41.2)
    p.append(line(ex, py1, ex, ey, color=HOT, sw=1.2, dash="4 4"))
    p.append(line(px0, ey, ex, ey, color=HOT, sw=1.2, dash="4 4"))
    p.append(circle(ex, ey, 5, fill=HOT, stroke=HOT, sw=1))
    p.append(text(ex + 12, ey - 8, "1°  →  41 дБ", size=13, color=HOT, bold=True, anchor="start"))

    for e, db in [(2.0, 35.2), (5.0, 27.2)]:
        x, y = X(e), Y(db)
        p.append(circle(x, y, 3.6, fill=CAR, stroke=CAR, sw=1))
        p.append(text(x + 8, y - 6, "%.0f°→%.0f дБ" % (e, db), size=10.5, color=CAR, anchor="start"))

    b, bw, bh = textbox(W / 2, 458,
                        "Ідеальні 90° дають нескінченне пригнічення чужої смуги.\n"
                        "Кожен градус похибки коштує десятки децибелів її витоку.",
                        size=12, color=INK, bold=True, min_w=560)
    p.append(b)

    render(os.path.join(OUT, "suppression.svg"), W, H, *p,
           title="Ціна неточності: пригнічення чужої смуги проти похибки фази")


if __name__ == "__main__":
    fig_spectrum_cut()
    fig_pitch_shift()
    fig_generation()
    fig_timeline()
    fig_sideband_cancel()
    fig_iq_rotation()
    fig_suppression()
    print("OK: figures written to", OUT)
