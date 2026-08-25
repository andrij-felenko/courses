# -*- coding: utf-8 -*-
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори за змістом
MSG = FIELD        # повідомлення / база (зелене)
CAR = NEG          # несуча / сигнал (синє)
HOT = POS          # акцент-небезпека (червоне): шум, неможливе
LO  = MUTED        # другорядні підписи


def polyline(pts, color, sw=2.0, fill="none"):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)


def path(pts, color, sw=2.0, fill="none", dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


def samp(x0, x1, n=240):
    return [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ «Навіщо модуляція» — 7 фігур
# ════════════════════════════════════════════════════════════════════════════

# ── 1: розмір антени — звук проти несучої ────────────────────────────────────

def fig_antenna():
    W, H = 760, 420
    p = []
    ground = 360

    # ЛІВОРУЧ: антена для прямого звуку — велетенська
    lx = 175
    p.append(line(60, ground, 350, ground, color=INK, sw=1.6))
    # «гора» антени до самого верху полотна
    top = 70
    p.append(line(lx, ground, lx, top, color=HOT, sw=5.0))
    p.append(line(lx - 9, top, lx + 9, top, color=HOT, sw=3.0))
    # людинка для масштабу
    px = 92
    p.append(circle(px, ground - 16, 5, fill=BG, stroke=INK, sw=1.6))
    p.append(line(px, ground - 11, px, ground - 2, color=INK, sw=1.6))
    p.append(text(px, ground + 16, "людина", size=10.5, color=MUTED))
    p.append(text(lx, top - 8, "≈ 25 км", size=13, color=HOT, bold=True))
    p.append(text(205, 150, "вища за хмари", size=11, color=HOT, anchor="start"))
    p.append(text(205, 168, "нездійсненно", size=11, color=HOT, anchor="start"))
    p.append(text(lx, 50, "звук 3 кГц напряму", size=13, color=INK, bold=True))
    p.append(text(lx, ground + 34, "λ/4 хвилі 100 км", size=11, color=MUTED))

    # ПРАВОРУЧ: антена для несучої — паличка
    rx = 560
    p.append(line(410, ground, 700, ground, color=INK, sw=1.6))
    p.append(line(rx, ground, rx, ground - 70, color=MSG, sw=5.0))
    p.append(line(rx - 8, ground - 70, rx + 8, ground - 70, color=MSG, sw=3.0))
    px2 = 480
    p.append(circle(px2, ground - 16, 5, fill=BG, stroke=INK, sw=1.6))
    p.append(line(px2, ground - 11, px2, ground - 2, color=INK, sw=1.6))
    p.append(text(px2, ground + 16, "людина", size=10.5, color=MUTED))
    p.append(text(rx, ground - 80, "≈ 0.75 м", size=13, color=MSG, bold=True))
    p.append(text(rx, 50, "несуча 100 МГц", size=13, color=INK, bold=True))
    p.append(text(rx, ground + 34, "λ/4 хвилі 3 м", size=11, color=MUTED))

    b, bw, bh = textbox(W / 2, 398, "Висока несуча → коротка хвиля → антена розумного розміру. У цьому перший сенс модуляції.",
                        size=12, color=INK, fill="#eef6ef", stroke=MSG, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "antenna.svg"), W, H, *p,
           title="Чому звук не випромінити напряму: розмір антени")


# ── 2: спільний ефір — частотний поділ ───────────────────────────────────────

def fig_sharing():
    W, H = 760, 400
    p = []

    def hump(cx, w, h, base):
        pts = []
        for i in range(60):
            t = i / 59
            x = cx - w / 2 + w * t
            y = base - h * math.exp(-((t - 0.5) * 4.2) ** 2)
            pts.append((x, y))
        return pts

    # ЛІВОРУЧ: усі в одній смузі — каша
    axL, ay = 60, 170
    p.append(line(axL, ay, axL + 300, ay, color=INK, sw=1.5))
    p.append(arrow(axL + 280, ay, axL + 300, ay, color=INK, sw=1.5))
    p.append(text(axL + 300, ay + 18, "f", size=14, color=INK, italic=True, anchor="start"))
    cmid = axL + 120
    for col, off in [(HOT, -14), (CAR, 0), (MSG, 14)]:
        p.append(path(hump(cmid + off, 120, 95, ay), col, sw=2.0))
    p.append(text(axL + 150, 56, "без несучих", size=13, color=INK, bold=True))
    p.append(text(axL + 150, 74, "усі голоси в одній смузі", size=10.5, color=MUTED))
    p.append(text(cmid, ay - 104, "накладаються → каша", size=11, color=HOT, bold=True))

    # ПРАВОРУЧ: рознесено по несучих
    axR = 410
    p.append(line(axR, ay, axR + 300, ay, color=INK, sw=1.5))
    p.append(arrow(axR + 280, ay, axR + 300, ay, color=INK, sw=1.5))
    p.append(text(axR + 300, ay + 18, "f", size=14, color=INK, italic=True, anchor="start"))
    for col, cx, lbl in [(HOT, axR + 70, "f₁"), (CAR, axR + 150, "f₂"), (MSG, axR + 230, "f₃")]:
        p.append(path(hump(cx, 64, 80, ay), col, sw=2.0))
        p.append(line(cx, ay, cx, ay + 6, color=MUTED, sw=1.2))
        p.append(text(cx, ay + 22, lbl, size=11.5, color=col, bold=True))
    p.append(text(axR + 150, 56, "кожна станція — своя несуча", size=12.5, color=INK, bold=True))
    p.append(text(axR + 150, 74, "мирно ділять ефір", size=10.5, color=MUTED))

    b, bw, bh = textbox(W / 2, 372, "Частотний поділ: кожному сигналу — власне «вікно» частот, і вони не заважають одне одному.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "sharing.svg"), W, H, *p,
           title="Спільний ефір: як багатьом станціям ужитися")


# ── 3: несуча сама собою нічого не повідомляє ────────────────────────────────

def fig_carrier():
    W, H = 760, 320
    x0, x1 = 60, 700
    p = []
    cy = 160
    p.append(line(x0, cy, x1, cy, color=MUTED, sw=1.0, dash="3 4"))
    pts = [(x, cy - 70 * math.sin(2 * math.pi * 14 * (x - x0) / (x1 - x0))) for x in samp(x0, x1, 600)]
    p.append(path(pts, CAR, sw=1.8))

    # підсвітити «перший період» зліва
    one = x0 + (x1 - x0) / 14
    p.append(rect(x0, cy - 86, one - x0, 172, fill="#eef2fd", stroke=CAR, sw=1.2, rx=4))
    p.append(text((x0 + one) / 2, cy - 96, "один період", size=11, color=CAR, bold=True))
    p.append(arrow(one + 6, cy - 70, one + 70, cy - 70, color=MUTED, sw=1.4))
    p.append(text(one + 80, cy - 66, "…і так на мільярд періодів уперед — усе передбачувано",
                  size=11.5, color=MUTED, anchor="start"))

    b, bw, bh = textbox(W / 2, 290, "Цілком передбачувана хвиля несе НУЛЬ інформації. Щоб щось переказати — несучу треба змінювати.",
                        size=12, color=INK, fill="#fdecea", stroke=HOT, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "carrier.svg"), W, H, *p,
           title="Несуча: чиста хвиля сама собою нічого не повідомляє")


# ── 4: три ручки несучої ─────────────────────────────────────────────────────

def fig_three_knobs():
    W, H = 760, 360
    p = []
    panel_w = 230
    gap = 18
    x = 40
    cy = 175
    A0 = 46

    def base(xx, n=160):
        return samp(xx + 12, xx + panel_w - 12, n)

    # AM — амплітуда
    xs = base(x)
    p.append(line(x + 12, cy, x + panel_w - 12, cy, color=MUTED, sw=1.0, dash="3 4"))
    pts = []
    for i, xx in enumerate(xs):
        t = i / (len(xs) - 1)
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(2 * math.pi * 1 * t))
        pts.append((xx, cy - A0 * a * math.sin(2 * math.pi * 9 * t)))
    p.append(path(pts, POS, sw=1.5))
    p.append(text(x + panel_w / 2, 56, "міняємо A", size=13, color=POS, bold=True))
    p.append(text(x + panel_w / 2, 74, "амплітудна — AM", size=11, color=MUTED))
    x += panel_w + gap

    # FM — частота
    xs = base(x)
    p.append(line(x + 12, cy, x + panel_w - 12, cy, color=MUTED, sw=1.0, dash="3 4"))
    phase = 0.0
    pts = []
    n = len(xs)
    for i, xx in enumerate(xs):
        t = i / (n - 1)
        inst = 7 + 5 * math.sin(2 * math.pi * 1 * t)
        phase += 2 * math.pi * inst / n
        pts.append((xx, cy - A0 * math.sin(phase)))
    p.append(path(pts, CAR, sw=1.5))
    p.append(text(x + panel_w / 2, 56, "міняємо f", size=13, color=CAR, bold=True))
    p.append(text(x + panel_w / 2, 74, "частотна — FM", size=11, color=MUTED))
    x += panel_w + gap

    # PM — фаза
    xs = base(x)
    p.append(line(x + 12, cy, x + panel_w - 12, cy, color=MUTED, sw=1.0, dash="3 4"))
    pts = []
    n = len(xs)
    for i, xx in enumerate(xs):
        t = i / (n - 1)
        ph = 2 * math.pi * 9 * t + (1.6 if t > 0.5 else 0.0)
        pts.append((xx, cy - A0 * math.sin(ph)))
    p.append(path(pts, FIELD, sw=1.5))
    p.append(line(x + 12 + (panel_w - 24) * 0.5, cy - A0 - 6, x + 12 + (panel_w - 24) * 0.5, cy + A0 + 6,
                  color=HOT, sw=1.2, dash="3 3"))
    p.append(text(x + panel_w / 2, 56, "міняємо φ", size=13, color=FIELD, bold=True))
    p.append(text(x + panel_w / 2, 74, "фазова — PM", size=11, color=MUTED))
    p.append(text(x + panel_w / 2, cy + A0 + 24, "скок фази", size=10, color=HOT, bold=True))

    b, bw, bh = textbox(W / 2, 332, "y(t) = A·sin(2π·f·t + φ) — рівно три параметри, отже рівно три родини модуляції.",
                        size=12.5, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "three-knobs.svg"), W, H, *p,
           title="Три ручки несучої: амплітуда, частота, фаза")


# ── 5: повний шлях — модулятор і демодулятор ─────────────────────────────────

def fig_chain():
    W, H = 760, 300
    p = []
    cy = 150
    bw, bh = 120, 64

    def box(cx, lines, col):
        x = cx - bw / 2
        return (fitbox(x, cy - bh / 2, bw, bh, lines, size=12.5, bold=True,
                       fill="#eef2fd", stroke=col, color=INK), cx + bw / 2)

    # повідомлення (вхід)
    p.append(text(70, cy - 30, "повідомлення", size=11.5, color=MSG, bold=True, anchor="start"))
    msg = [(70 + 10 * i, cy - 18 * math.sin(2 * math.pi * 1.2 * i / 30)) for i in range(31)]
    p.append(path(msg, MSG, sw=2.0))
    rxs = 70 + 300

    # модулятор
    frag, x_after = box(250, "МОДУЛЯТОР\nсадить на несучу", CAR)
    p.append(frag)
    p.append(arrow(120, cy, 250 - bw / 2 - 6, cy, color=INK, sw=1.6))

    # антени + ефір
    ax1, ax2 = 250 + bw / 2 + 6, 510 - bw / 2 - 6
    p.append(arrow(ax1, cy, ax2, cy, color=INK, sw=1.6))
    # модульована хвиля над стрілкою
    wav = [((ax1 + ax2) / 2 - 60 + 4 * i, cy - 26 - 8 * math.sin(2 * math.pi * 6 * i / 30)) for i in range(31)]
    p.append(path(wav, HOT, sw=1.4))
    p.append(text((ax1 + ax2) / 2, cy - 44, "ефір", size=11, color=MUTED, bold=True))

    # демодулятор
    frag, _ = box(510, "ДЕМОДУЛЯТОР\nзнімає назад", CAR)
    p.append(frag)

    # відновлене повідомлення (вихід)
    out = [(580 + 10 * i, cy - 18 * math.sin(2 * math.pi * 1.2 * i / 30)) for i in range(31)]
    p.append(arrow(510 + bw / 2 + 6, cy, 580, cy, color=INK, sw=1.6))
    p.append(path(out, MSG, sw=2.0))
    p.append(text(690, cy - 30, "те саме", size=11.5, color=MSG, bold=True))

    b, bw2, bh2 = textbox(W / 2, 270, "Симетрія: посадили інформацію на несучу — передали ефіром — зняли назад. Несуча — лише транспорт.",
                          size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Повний шлях: модулятор, ефір, демодулятор")


# ── 6: що робить модуляція зі спектром ───────────────────────────────────────

def fig_spectrum():
    W, H = 760, 340
    p = []
    ay = 230
    p.append(line(60, ay, 700, ay, color=INK, sw=1.6))
    p.append(arrow(680, ay, 700, ay, color=INK, sw=1.6))
    p.append(text(700, ay + 18, "f", size=14, color=INK, italic=True, anchor="start"))
    p.append(line(110, ay - 4, 110, ay + 4, color=MUTED, sw=1.2))
    p.append(text(110, ay + 20, "0", size=11, color=MUTED))

    def hump(cx, w, h, col, fillc):
        pts = [(cx, ay)]
        for i in range(40):
            t = i / 39
            x = cx - w / 2 + w * t
            y = ay - h * math.exp(-((t - 0.5) * 4.0) ** 2)
            pts.append((x, y))
        pts.append((cx + w / 2, ay))
        return path(pts, col, sw=2.0, fill=fillc)

    # база біля нуля
    p.append(hump(150, 80, 80, MSG, "#eef6ef"))
    p.append(text(150, ay - 92, "база", size=12, color=MSG, bold=True))
    p.append(text(150, ay - 108, "baseband", size=10, color=MUTED))

    # несуча fₒ + смугове вікно
    fo = 470
    p.append(line(fo, ay, fo, ay - 150, color=CAR, sw=2.6))
    p.append(text(fo, ay - 158, "fₒ", size=13, color=CAR, bold=True))
    p.append(hump(fo - 40, 56, 60, MSG, "#eef6ef"))
    p.append(hump(fo + 40, 56, 60, MSG, "#eef6ef"))
    p.append(text(fo, ay - 92, "passband", size=10.5, color=MUTED))

    # стрілка переносу
    p.append(arrow(200, ay - 60, fo - 80, ay - 60, color=HOT, sw=1.6))
    p.append(text((200 + fo - 80) / 2, ay - 68, "модуляція переносить угору", size=11, color=HOT, bold=True))
    p.append(arrow(fo - 60, ay - 110, 230, ay - 110, color=NEG, sw=1.4))
    p.append(text((230 + fo - 60) / 2, ay - 118, "демодуляція — назад до нуля", size=10.5, color=NEG))

    b, bw, bh = textbox(W / 2, 312, "Ширина вікна довкола fₒ — це смуга сигналу: що швидше передаємо дані, то вона ширша.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "spectrum.svg"), W, H, *p,
           title="Спектр: модуляція піднімає базу до несучої")


# ── 7: підсумок — три причини ────────────────────────────────────────────────

def fig_why():
    W, H = 760, 340
    p = []
    cw, ch = 224, 170
    y = 64
    gap = 18
    x = 30
    cards = [
        ("1 · Антена", MSG, "#eef6ef",
         ["висока несуча →", "коротка хвиля →", "антена реального", "розміру"]),
        ("2 · Спільний ефір", CAR, "#eef2fd",
         ["кожній станції —", "своя несуча;", "десятки сигналів", "без взаємних завад"]),
        ("3 · Середовище", POS, "#fdecea",
         ["несучу обирають", "під діапазон:", "дальність, стіни,", "розмір системи"]),
    ]
    for ttl, col, fillc, lines in cards:
        p.append(rect(x, y, cw, ch, fill=fillc, stroke=col, sw=2.0, rx=10))
        p.append(text(x + cw / 2, y + 30, ttl, size=14.5, color=col, bold=True))
        yy = y + 60
        for ln in lines:
            p.append(text(x + cw / 2, yy, ln, size=11.5, color=INK))
            yy += 22
        x += cw + gap

    b, bw, bh = textbox(W / 2, 300, "Низькочастотне повідомлення саме по собі радіо не зробить — усі три причини ведуть до модуляції.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "why.svg"), W, H, *p,
           title="Навіщо модуляція: три причини в одному погляді")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА «hist-armstrong» — 7 фігур
# ════════════════════════════════════════════════════════════════════════════

# ── h1: життя Армстронга в подіях (часова шкала) ─────────────────────────────

def fig_timeline():
    W, H = 800, 360
    p = []
    ay = 150
    x0, x1 = 60, 740
    p.append(line(x0, ay, x1, ay, color=INK, sw=2.0))
    p.append(arrow(x1 - 20, ay, x1, ay, color=INK, sw=2.0))

    events = [
        (1912, "регенерація", MSG, 1),
        (1918, "супергетеродин", MSG, -1),
        (1933, "патенти FM", CAR, 1),
        (1935, "демонстрація", CAR, -1),
        (1945, "FCC переносить\nдіапазон", HOT, 1),
        (1954, "загибель", HOT, -1),
        (1967, "перемога вдови\nу судах", MSG, 1),
    ]
    a, b = 1908, 1971
    for yr, lbl, col, side in events:
        fx = x0 + (x1 - x0) * (yr - a) / (b - a)
        p.append(circle(fx, ay, 5, fill=col, stroke=col, sw=1.5))
        p.append(text(fx, ay + (4 if side > 0 else 4), "", size=9))
        dy = -1 if side > 0 else 1
        ly = ay + dy * 30
        p.append(line(fx, ay, fx, ly, color=col, sw=1.2))
        lines = lbl.split("\n")
        ty = ly + (dy * (8 if dy < 0 else 16))
        for i, ln in enumerate(lines):
            p.append(text(fx, ty + (dy < 0) * (-(len(lines) - 1) * 15) + i * 15, ln,
                          size=11, color=col, bold=True))
        p.append(text(fx, ay + (-44 if side > 0 else 52), str(yr), size=11.5, color=INK, bold=True))

    b2, bw, bh = textbox(W / 2, 330, "Один інженер, що подарував світу чисте радіо — і програв особисто, хоча його ідея перемогла назавжди.",
                         size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b2)

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Едвін Армстронг: життя в подіях")


# ── h2: три дарунки винахідника ──────────────────────────────────────────────

def fig_three_gifts():
    W, H = 760, 320
    p = []
    cw, ch = 224, 180
    y = 60
    gap = 18
    x = 30
    cards = [
        ("Регенерація", "1912", MSG, "#eef6ef",
         ["позитивний", "зворотний зв'язок:", "радіо стало гучним", "і дешевим"]),
        ("Супергетеродин", "1918", CAR, "#eef2fd",
         ["перенос на сталу", "проміжну частоту;", "архітектура майже", "кожного приймача"]),
        ("Широкосмугова FM", "1933", POS, "#fdecea",
         ["звук у частоті:", "чистий, безшумний", "—  спадщина", "донині"]),
    ]
    for ttl, yr, col, fillc, lines in cards:
        p.append(rect(x, y, cw, ch, fill=fillc, stroke=col, sw=2.0, rx=10))
        p.append(text(x + cw / 2, y + 28, ttl, size=14, color=col, bold=True))
        p.append(text(x + cw / 2, y + 48, yr, size=11.5, color=MUTED, bold=True))
        yy = y + 78
        for ln in lines:
            p.append(text(x + cw / 2, yy, ln, size=11.5, color=INK))
            yy += 22
        x += cw + gap

    b, bw, bh = textbox(W / 2, 300, "Три фундаменти радіо — і всі троє від однієї людини.",
                        size=12.5, color=INK, bold=True, min_w=460)
    p.append(b)

    render(os.path.join(OUT, "three-gifts.svg"), W, H, *p,
           title="Три винаходи, на яких стоїть усе радіо")


# ── h3: чому AM тріщить — шум сідає на амплітуду ──────────────────────────────

def fig_am_noise():
    import random
    random.seed(11)
    W, H = 760, 340
    x0, x1 = 70, 700
    p = []
    cy = 170
    noise = [(random.random() - 0.5) for _ in range(640)]
    xs = samp(x0, x1, 640)
    p.append(line(x0, cy, x1, cy, color=MUTED, sw=1.0, dash="3 4"))

    A0 = 60
    amp = [0.5 + 0.42 * math.sin(2 * math.pi * 1.0 * (x - x0) / (x1 - x0)) for x in xs]
    sig, up = [], []
    for i, x in enumerate(xs):
        n = 18 * noise[i]
        sig.append((x, cy - (A0 * amp[i] * math.sin(2 * math.pi * 22 * (x - x0) / (x1 - x0)) + n)))
        up.append((x, cy - (A0 * amp[i] + 16 * abs(noise[i]))))
    p.append(path(sig, CAR, sw=1.2))
    p.append(path(up, HOT, sw=1.8, dash="4 3"))
    p.append(text(x1, cy - A0 - 36, "огинаюча = звук, але вже з тріском", size=11, color=HOT, bold=True, anchor="end"))

    # позначки джерел шуму
    for lbl, fx in [("блискавка", x0 + 120), ("іскри мотора", x0 + 330), ("мережа", x0 + 520)]:
        p.append(text(fx, cy + A0 + 40, lbl, size=10.5, color=HOT))
        p.append(arrow(fx, cy + A0 + 30, fx, cy + 20, color=HOT, sw=1.2))

    b, bw, bh = textbox(W / 2, 312, "Звук захований у амплітуді — а шум теж б'є по амплітуді. Приймач не відрізнить одне від одного.",
                        size=12, color=INK, fill="#fdecea", stroke=HOT, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "am-noise.svg"), W, H, *p,
           title="Чому AM-радіо тріщить: шум сідає на амплітуду")


# ── h4: парадокс — ширша смуга → тихіше ──────────────────────────────────────

def fig_wideband():
    W, H = 760, 360
    p = []

    def comb(ax, ay, df_px, peak, n, col):
        out = ""
        for k in range(-n, n + 1):
            fx = ax + k * (df_px / n)
            h = peak * math.exp(-(k / (n / 1.6)) ** 2)
            if h < 4:
                continue
            out += line(fx, ay, fx, ay - h, color=col, sw=2.0)
        return out

    ay = 240
    # вузька FM
    axL = 185
    p.append(line(60, ay, 350, ay, color=INK, sw=1.5))
    p.append(arrow(330, ay, 350, ay, color=INK, sw=1.5))
    p.append(comb(axL, ay, 60, 120, 6, NEG))
    p.append(text(axL, 64, "вузька FM", size=13, color=NEG, bold=True))
    p.append(text(axL, 82, "як AM — шумить так само", size=10.5, color=MUTED))
    p.append(line(axL - 30, ay + 20, axL + 30, ay + 20, color=INK, sw=1.3))

    # широка FM
    axR = 555
    p.append(line(410, ay, 700, ay, color=INK, sw=1.5))
    p.append(arrow(680, ay, 700, ay, color=INK, sw=1.5))
    p.append(comb(axR, ay, 130, 120, 12, MSG))
    p.append(text(axR, 64, "навмисне ШИРОКА FM", size=13, color=MSG, bold=True))
    p.append(text(axR, 82, "велика девіація → шум тоне", size=10.5, color=MUTED))
    p.append(line(axR - 65, ay + 20, axR + 65, ay + 20, color=INK, sw=1.3))
    p.append(text(axR, ay + 38, "ширше → тихіше", size=11, color=MSG, bold=True))

    p.append(arrow(360, 150, 410, 150, color=HOT, sw=1.8))
    p.append(text(385, 138, "контрінтуїтивно", size=10.5, color=HOT, bold=True))

    b, bw, bh = textbox(W / 2, 330, "Інформація — у частоті: приймач зрізає всю амплітуду, а з нею й шум.\nЧим ширша смуга, то глибше тоне статика.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "wideband.svg"), W, H, *p,
           title="Парадокс Армстронга: ширша смуга → тихіше")


# ── h5: удар 1945-го — перенос діапазону ─────────────────────────────────────

def fig_band_move():
    W, H = 760, 320
    p = []
    ay = 200
    x0, x1 = 60, 700
    p.append(line(x0, ay, x1, ay, color=INK, sw=1.6))
    p.append(arrow(x1 - 20, ay, x1, ay, color=INK, sw=1.6))
    p.append(text(x1, ay + 20, "МГц", size=11, color=MUTED, anchor="start"))

    def at(mhz):
        return x0 + (x1 - x0) * (mhz - 30) / (120 - 30)

    # старий діапазон 42–50
    p.append(rect(at(42), ay - 50, at(50) - at(42), 50, fill="#fdecea", stroke=HOT, sw=2.0, rx=4))
    p.append(text((at(42) + at(50)) / 2, ay - 60, "42–50", size=11.5, color=HOT, bold=True))
    p.append(text((at(42) + at(50)) / 2, ay - 26, "стара FM", size=10.5, color=HOT, bold=True))

    # новий діапазон 88–108
    p.append(rect(at(88), ay - 50, at(108) - at(88), 50, fill="#eef6ef", stroke=MSG, sw=2.0, rx=4))
    p.append(text((at(88) + at(108)) / 2, ay - 60, "88–108", size=11.5, color=MSG, bold=True))
    p.append(text((at(88) + at(108)) / 2, ay - 26, "нова FM", size=10.5, color=MSG, bold=True))

    p.append(arrow(at(50) + 6, ay - 25, at(88) - 6, ay - 25, color=INK, sw=1.8))
    p.append(text((at(50) + at(88)) / 2, ay - 34, "перенос 1945", size=11, color=INK, bold=True))

    for m in (30, 50, 88, 108, 120):
        p.append(line(at(m), ay - 4, at(m), ay + 4, color=MUTED, sw=1.1))
        p.append(text(at(m), ay + 18, str(m), size=10, color=MUTED))

    b, bw, bh = textbox(W / 2, 290, "Близько півмільйона FM-приймачів за ніч стали брухтом: на новому місці їхнє радіо вже не ловило нічого.",
                        size=12, color=INK, fill="#fdecea", stroke=HOT, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "band-move.svg"), W, H, *p,
           title="Удар 1945-го: FCC переносить FM-діапазон")


# ── h6: чесно про авторство — три випадки ────────────────────────────────────

def fig_collective():
    W, H = 760, 320
    p = []
    cw, ch = 224, 188
    y = 60
    gap = 18
    x = 30
    cards = [
        ("Широкосмугова FM", MSG, "#eef6ef", "безперечно його",
         ["ідею FM знали раніше", "(Карсон, 1922),", "але робочою —", "і тишу довів —", "саме Армстронг"]),
        ("Регенерація", POS, "#fdecea", "юридично спірна",
         ["Верховний суд 1934", "присудив де Форесту;", "інженери досі", "вважають це", "помилкою суду"]),
        ("Супергетеродин", CAR, "#eef2fd", "не на самоті",
         ["над переносом частоти", "працювали й інші", "(Леві, Франція);", "заслуга — робоча", "архітектура"]),
    ]
    for ttl, col, fillc, tag, lines in cards:
        p.append(rect(x, y, cw, ch, fill=fillc, stroke=col, sw=2.0, rx=10))
        p.append(text(x + cw / 2, y + 26, ttl, size=13, color=col, bold=True))
        p.append(text(x + cw / 2, y + 44, tag, size=11, color=MUTED, italic=True, bold=True))
        yy = y + 70
        for ln in lines:
            p.append(text(x + cw / 2, yy, ln, size=11, color=INK))
            yy += 21
        x += cw + gap

    b, bw, bh = textbox(W / 2, 300, "Винаходи колективні: розрізняти доведене, спірне й чуже — частина чесного розуміння історії.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "collective.svg"), W, H, *p,
           title="Чесно про авторство: безперечне й спірне")


# ── h7: трагедія і виправдання ───────────────────────────────────────────────

def fig_vindication():
    W, H = 760, 300
    p = []
    # ліва картка — трагедія
    p.append(rect(40, 60, 320, 170, fill="#fdecea", stroke=HOT, sw=2.0, rx=10))
    p.append(text(200, 90, "Трагедія", size=15, color=HOT, bold=True))
    for i, ln in enumerate(["суди проти RCA висотали", "статок і сили;", "1954 — хворий і самотній,", "він обірвав власне життя"]):
        p.append(text(200, 118 + i * 24, ln, size=11.5, color=INK))

    # права картка — виправдання
    p.append(rect(400, 60, 320, 170, fill="#eef6ef", stroke=MSG, sw=2.0, rx=10))
    p.append(text(560, 90, "Виправдання", size=15, color=MSG, bold=True))
    for i, ln in enumerate(["вдова Меріон підхопила позови:", "21 справа — усі виграні", "(RCA, Motorola, Zenith),", "понад $10 млн відшкодувань"]):
        p.append(text(560, 118 + i * 24, ln, size=11.5, color=INK))

    p.append(arrow(362, 145, 398, 145, color=INK, sw=1.8))

    b, bw, bh = textbox(W / 2, 270, "Пріоритет FM лишився за Армстронгом: справедливість прийшла — запізно для людини, вчасно для історії.",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "vindication.svg"), W, H, *p,
           title="Трагедія людини — і перемога правди")


if __name__ == "__main__":
    # стаття
    fig_antenna()
    fig_sharing()
    fig_carrier()
    fig_three_knobs()
    fig_chain()
    fig_spectrum()
    fig_why()
    # вставка
    fig_timeline()
    fig_three_gifts()
    fig_am_noise()
    fig_wideband()
    fig_band_move()
    fig_collective()
    fig_vindication()
    print("OK: figures written to", OUT)
