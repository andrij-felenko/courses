# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER = "#9a7d2e"   # світловод / люмінофор
GLASS = "#9bbdd6"   # скло панелі


# ── edge-lit: бокова підсвітка в розрізі ──────────────────────────────────────
# Ідея: світло кількох білих світлодіодів збоку входить у світловод, рівномірно
# виходить угору крізь розсіювач і заслінку; яскравість панелі йде за струмом.
def fig_edge_lit():
    W, H = 760, 320
    p = []
    lx, rw = 150, 430

    # шари знизу вгору: відбивач, світловод, розсіювач, LCD-панель
    p.append(rect(lx, 196, rw, 10, fill="#dcdcdc", stroke=MUTED, sw=1.2, rx=0))
    p.append(text(lx + rw + 8, 205, "відбивач", size=10, color=MUTED, anchor="start"))
    p.append(rect(lx, 152, rw, 42, fill="#fff8e0", stroke="#caa24a", sw=1.5, rx=0))
    p.append(text(lx + rw + 8, 177, "світловод", size=11, color=AMBER, anchor="start"))
    p.append(rect(lx, 136, rw, 12, fill="#f2f2f2", stroke=MUTED, sw=1.2, rx=0))
    p.append(text(lx + rw + 8, 146, "розсіювач", size=10, color=MUTED, anchor="start"))
    p.append(rect(lx, 106, rw, 26, fill="#eaf3ff", stroke=GLASS, sw=1.5, rx=0))
    p.append(text(lx + rw + 8, 123, "LCD-панель (заслінка)", size=11, color="#5d7e93", anchor="start"))

    # білі світлодіоди збоку (зліва), світять у світловод
    for yy in (156, 167, 178):
        p.append(rect(lx - 24, yy, 20, 8, fill="#fff4c2", stroke="#caa24a", sw=1.2, rx=0))
    p.append(text(lx - 26, 150, "білі LED", size=10, color=AMBER, anchor="end"))
    p.append(line(lx - 2, 172, lx + 150, 172, color="#caa24a", sw=1.6))

    # світло виходить угору крізь панель (зелені стрілки полем)
    for sx in (lx + 80, lx + 180, lx + 280, lx + 380):
        p.append(line(sx, 152, sx, 134, color=FIELD, sw=1.8))
        p.append(line(sx - 4, 142, sx, 134, color=FIELD, sw=1.8))
        p.append(line(sx + 4, 142, sx, 134, color=FIELD, sw=1.8))

    # око над панеллю
    cx = lx + rw / 2
    p.append(line(cx, 106, cx, 86, color=FIELD, sw=2))
    p.append(line(cx - 4, 94, cx, 86, color=FIELD, sw=2))
    p.append(line(cx + 4, 94, cx, 86, color=FIELD, sw=2))
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="16" ry="9" fill="%s" stroke="%s" stroke-width="2"/>'
             % (cx, 72, BG, INK))
    p.append(circle(cx, 74, 4.5, fill=INK, stroke=INK, sw=1))
    p.append(text(cx + 26, 77, "око", size=11, color=MUTED, anchor="start"))

    p.append(text(W / 2, 252, "Світло LED входить у світловод збоку, рівно виходить угору крізь заслінку до ока.",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 278, "Яскравість панелі йде за яскравістю підсвітки, а та — за СТРУМОМ крізь світлодіоди.",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "edge-lit.svg"), W, H, *p,
           title="Бокова підсвітка: світлодіоди + світловод розганяють світло вгору")


# ── led-iv: ВАХ світлодіода — керують струмом, а не напругою ──────────────────
# Ідея: на робочій ділянці характеристика майже вертикальна, тож крихітний ΔV
# дає величезний ΔI; задавати треба струм.
def fig_led_iv():
    W, H = 760, 380
    ox, oy = 92, 320          # початок осей
    ax_w, ax_h = 588, 248
    p = []

    # осі
    p.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    p.append(text(ox + ax_w, oy + 22, "Vf, В", size=12, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ax_h + 6, "I, мА", size=12, color=INK, anchor="start"))

    # засічки осі V (1..4)
    for i, vx in enumerate((1, 2, 3, 4)):
        gx = ox + ax_w * vx / 4.3
        p.append(line(gx, oy, gx, oy + 5, color=INK, sw=1.3))
        p.append(text(gx, oy + 19, str(vx), size=10, color=MUTED))
    # засічки осі I (10,20,30)
    for ma in (10, 20, 30):
        gy = oy - ax_h * ma / 33.0
        p.append(line(ox - 5, gy, ox, gy, color=INK, sw=1.3))
        p.append(text(ox - 9, gy + 4, str(ma), size=10, color=MUTED, anchor="end"))

    # експоненційна ВАХ: майже нуль до порогу ~2.7 В, далі майже вертикально
    def iv(v):  # v у В -> I у мА (0..33)
        return 33.0 / (1 + math.exp(-(v - 3.05) / 0.085))
    pts = []
    for k in range(0, 261):
        v = 4.3 * k / 260.0
        ii = iv(v)
        gx = ox + ax_w * v / 4.3
        gy = oy - ax_h * min(ii, 33.0) / 33.0
        pts.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # крихітний ΔV -> величезний ΔI на робочій ділянці
    v1, v2 = 3.0, 3.06
    gy1, gy2 = oy - ax_h * iv(v1) / 33.0, oy - ax_h * iv(v2) / 33.0
    gx1, gx2 = ox + ax_w * v1 / 4.3, ox + ax_w * v2 / 4.3
    p.append(line(gx1, oy, gx1, gy1, color=NEG, sw=1.4, dash="4 3"))
    p.append(line(gx2, oy, gx2, gy2, color=NEG, sw=1.4, dash="4 3"))
    p.append(line(ox, gy1, gx1, gy1, color=NEG, sw=1.4, dash="4 3"))
    p.append(line(ox, gy2, gx2, gy2, color=NEG, sw=1.4, dash="4 3"))
    p.append(text((gx1 + gx2) / 2, oy + 36, "ΔV крихітний", size=11, color=NEG, bold=True))
    p.append(text(ox - 14, (gy1 + gy2) / 2 - 4, "ΔI", size=11, color=NEG, bold=True, anchor="end"))
    p.append(text(ox - 14, (gy1 + gy2) / 2 + 12, "величезний", size=9, color=NEG, anchor="end"))

    p.append(text(ox + ax_w * 0.46, oy - ax_h * 0.52,
                  "Задаси напругу — струм\n(а отже яскравість) непередбачуваний.",
                  size=11, color=INK, anchor="start"))
    box = mtext(ox + ax_w * 0.46, oy - ax_h * 0.30,
                "Задаси СТРУМ — яскравість рівна\nй світлодіод у безпеці.",
                size=11, color=FIELD, anchor="start", bold=True)
    p.append(box)

    render(os.path.join(OUT, "led-iv.svg"), W, H, *p,
           title="Світлодіодом керують струмом, а не напругою")


# ── ballast: баластний резистор задає струм ──────────────────────────────────
# Ідея: послідовний резистор зʼїдає різницю напруг і грубо задає струм
# I = (V₊ − V_LED) ÷ R; просто й дешево, та неощадно й ненадійно.
def fig_ballast():
    W, H = 720, 300
    p = []
    yw = 180

    p.append(text(110, 116, "V₊", size=13, color=POS, bold=True))
    p.append(line(110, 126, 110, yw, color=INK, sw=2))
    p.append(line(110, yw, 230, yw, color=INK, sw=2))
    # резистор
    p.append(rect(230, yw - 12, 70, 24, fill=BG, stroke=INK, sw=1.6, rx=0))
    p.append(text(265, yw + 5, "R", size=13, color=INK, bold=True))
    p.append(line(300, yw, 400, yw, color=INK, sw=2))
    # світлодіод (трикутник + риска)
    p.append(line(400, yw - 12, 400, yw + 12, color=INK, sw=2))
    p.append(line(400, yw - 12, 424, yw, color=INK, sw=2))
    p.append(line(424, yw - 12, 424, yw + 12, color=INK, sw=2))
    p.append(line(400, yw + 12, 424, yw, color=INK, sw=2))
    p.append(text(412, yw - 22, "LED", size=10.5, color=AMBER))
    p.append(line(424, yw, 520, yw, color=INK, sw=2))
    # земля
    p.append(line(520, yw, 520, yw + 40, color=INK, sw=2))
    p.append(line(505, yw + 40, 535, yw + 40, color=INK, sw=2))
    p.append(text(540, yw + 44, "GND", size=11, color=MUTED, anchor="start"))
    # струм
    p.append(arrow(150, yw, 200, yw, color=INK, sw=1.8))
    p.append(text(175, yw - 10, "I", size=12, color=FIELD, bold=True))

    p.append(text(W / 2, 250,
                  "I = (V₊ − V_LED) ÷ R.  Просто й дешево, але резистор гріється,",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 270,
                  "а струм «гуляє» з напругою живлення й теплом.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "ballast.svg"), W, H, *p,
           title="Найпростіший струмовий регулятор: баластний резистор")


# ── boost-driver: підняти напругу й тримати заданий струм ─────────────────────
# Ідея: перетворювач піднімає Vout рівно до потрібного нитці струму; струм
# «читає» резистор Rₛ і повертає в регулятор (петля зворотного звʼязку).
def fig_boost():
    W, H = 760, 320
    p = []
    yw = 150

    p.append(text(60, yw + 4, "Vᵢₙ", size=12, color=INK, bold=True, anchor="end"))
    p.append(line(66, yw, 110, yw, color=INK, sw=2))
    # котушка L (зигзаг)
    zx = 110
    for i in range(8):
        y0 = yw - 10 if i % 2 == 0 else yw + 10
        p.append(line(zx, yw, zx + 7, y0, color=INK, sw=1.8))
        zx += 7
    p.append(line(zx, yw, zx + 6, yw, color=INK, sw=2))
    p.append(text(138, yw - 22, "L", size=11, color=INK))
    p.append(line(zx + 6, yw, 210, yw, color=INK, sw=2))
    # блок BOOST
    p.append(rect(210, 116, 150, 70, fill="#eef2f5", stroke=INK, sw=1.8, rx=6))
    p.append(text(285, 144, "BOOST", size=13, color=INK, bold=True))
    p.append(text(285, 164, "+ регулятор I", size=10, color=MUTED))
    p.append(line(360, yw, 430, yw, color=INK, sw=2))
    # нитка LED
    p.append(rect(430, yw - 24, 150, 48, fill="#fff8e0", stroke="#caa24a", sw=1.6, rx=5))
    p.append(text(505, yw + 4, "LED-нитка (N шт.)", size=11, color=AMBER))
    p.append(line(580, yw, 650, yw, color=INK, sw=2))
    # вимірювальний резистор Rs
    p.append(rect(650, yw - 12, 40, 24, fill=BG, stroke=INK, sw=1.6, rx=0))
    p.append(text(670, yw + 5, "Rₛ", size=11, color=INK, bold=True))
    p.append(line(690, yw, 720, yw, color=INK, sw=2))
    p.append(line(720, yw, 720, yw + 36, color=INK, sw=2))
    p.append(line(706, yw + 36, 734, yw + 36, color=INK, sw=2))
    # зворотний звʼязок Rs -> регулятор
    p.append(line(670, yw + 12, 670, 224, color=MUTED, sw=1.6))
    p.append(line(670, 224, 285, 224, color=MUTED, sw=1.6, dash="5 4"))
    p.append(arrow(285, 224, 285, 188, color=MUTED, sw=1.6))
    p.append(text(478, 240, "зворотний звʼязок: тримай I = заданому", size=10.5, color=FIELD, bold=True))

    p.append(text(W / 2, 286,
                  "Перетворювач піднімає напругу, доки крізь нитку не піде задане I; струм «читає» Rₛ.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "boost-driver.svg"), W, H, *p,
           title="Boost-драйвер: підняти напругу й тримати ЗАДАНИЙ струм")


# ── dimming: ШІМ (час) проти аналогового (рівень струму) ─────────────────────
# Ідея: ШІМ міняє ЧАС при повному струмі (колір сталий, важлива частота);
# аналог міняє РІВЕНЬ струму (без миготіння, та колір трохи «пливе»).
def fig_dimming():
    W, H = 760, 360
    p = []

    # верх: ШІМ
    ox, oy = 70, 150
    p.append(arrow(ox, oy, 720, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - 64, color=INK, sw=1.6))
    p.append(text(ox - 12, oy - 58, "I", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox, oy + 18, "ШІМ: повний струм, міняємо ЧАС", size=11, color=INK, bold=True))
    # імпульси
    top, x = oy - 50, ox + 20
    period, duty = 100, 40
    pts = []
    while x < 710:
        pts += [(x, oy), (x, top), (x + duty, top), (x + duty, oy)]
        x += period
    poly = " ".join("%.1f,%.1f" % q for q in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, POS))
    p.append(text(540, oy - 56, "колір сталий; важлива частота", size=10.5, color=MUTED, anchor="start"))

    # низ: аналог
    ox2, oy2 = 70, 320
    p.append(arrow(ox2, oy2, 720, oy2, color=INK, sw=1.6))
    p.append(arrow(ox2, oy2, ox2, oy2 - 64, color=INK, sw=1.6))
    p.append(text(ox2 - 12, oy2 - 58, "I", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox2, oy2 + 18, "аналог: рівний струм, міняємо РІВЕНЬ", size=11, color=INK, bold=True))
    lvl = oy2 - 26
    p.append(line(ox2 + 20, oy2, ox2 + 20, lvl, color=FIELD, sw=2.4))
    p.append(line(ox2 + 20, lvl, 700, lvl, color=FIELD, sw=2.4))
    p.append(text(250, lvl - 10, "рівень = яскравість", size=10.5, color=FIELD))
    p.append(text(470, lvl - 10, "без миготіння; на малих струмах колір трохи «пливе»",
                  size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "dimming.svg"), W, H, *p,
           title="Димінг: ШІМ (час) проти аналогового (рівень струму)")


# ── strings: нитки світлодіодів — послідовно проти паралельно ────────────────
# Ідея: послідовно — один струм крізь усіх (однакова яскравість даром, але
# висока напруга); паралельно — нижча напруга, та струм ділиться нерівно.
def fig_strings():
    W, H = 760, 320
    p = []

    def led(x, y):
        out = [line(x, y - 10, x, y + 10, color=INK, sw=1.8),
               line(x, y - 10, x + 18, y, color=INK, sw=1.8),
               line(x + 18, y - 10, x + 18, y + 10, color=INK, sw=1.8),
               line(x, y + 10, x + 18, y, color=INK, sw=1.8)]
        return out

    # послідовно (зліва)
    p.append(text(190, 78, "послідовно", size=13, color=INK, bold=True))
    y = 130
    p.append(line(70, y, 100, y, color=INK, sw=2))
    xs = 100
    for _ in range(3):
        p += led(xs, y)
        p.append(line(xs + 18, y, xs + 50, y, color=INK, sw=2))
        xs += 50
    p.append(arrow(75, y, 95, y, color=INK, sw=1.8))
    p.append(text(190, 168, "один струм крізь усі → яскравість однакова", size=10.5, color=FIELD))
    p.append(text(190, 184, "але треба висока напруга (N × V_LED)", size=10.5, color=MUTED))

    # паралельно (справа)
    p.append(text(560, 78, "паралельно", size=13, color=INK, bold=True))
    for yy in (120, 154):
        p.append(line(430, yy, 460, yy, color=INK, sw=2))
        xs = 460
        for _ in range(2):
            p += led(xs, yy)
            p.append(line(xs + 18, yy, xs + 22, yy, color=INK, sw=2))
            xs += 22
        p.append(line(xs, yy, 550, yy, color=INK, sw=2))
    p.append(text(560, 200, "нижча напруга, але струм між нитками", size=10.5, color="#b07d18"))
    p.append(text(560, 216, "ділиться нерівно — треба балансувати", size=10.5, color="#b07d18"))

    p.append(text(W / 2, 264,
                  "Послідовно — однаковий струм даром, та висока напруга (тут і потрібен boost).",
                  size=11.5, color=MUTED, italic=True))
    p.append(text(W / 2, 286,
                  "Бережися обриву нитки: boost задере напругу до межі — потрібен захист від перенапруги.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "strings.svg"), W, H, *p,
           title="Нитки світлодіодів: послідовно проти паралельно")


# ── ieee1789: три зони ризику миготіння (частота × глибина модуляції) ─────────
# Ідея (детальна версія): безпека визначається не частотою САМОЮ ПО СОБІ, а парою
# «частота + глибина модуляції». Нижче ~90 Гц — ризик за будь-якої глибини; від 90
# до 1250 Гц чим вища частота, тим глибша модуляція припустима; вище 1250 Гц —
# безпечно майже завжди.
def fig_ieee1789():
    W, H = 720, 380
    ox, oy = 80, 320
    ax_w, ax_h = 600, 250
    p = []

    # осі: X = частота (лог, 10..3000 Гц), Y = глибина модуляції 0..100 %
    p.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    p.append(text(ox + ax_w, oy + 22, "частота ШІМ (лог), Гц", size=12, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ax_h + 4, "глибина модуляції, %", size=12, color=INK, anchor="start"))

    import math as _m
    fmin, fmax = 10.0, 3000.0
    def fx(f):  # лог-вісь частоти -> X
        return ox + ax_w * (_m.log10(f) - _m.log10(fmin)) / (_m.log10(fmax) - _m.log10(fmin))
    def my(m):  # модуляція % -> Y
        return oy - ax_h * m / 100.0

    # засічки частоти
    for f in (10, 90, 1250, 3000):
        gx = fx(f)
        p.append(line(gx, oy, gx, oy + 5, color=INK, sw=1.3))
        p.append(text(gx, oy + 19, str(f), size=10, color=MUTED))
    # засічки модуляції
    for m in (25, 50, 75, 100):
        gy = my(m)
        p.append(line(ox - 5, gy, ox, gy, color=INK, sw=1.3))
        p.append(text(ox - 9, gy + 4, str(m), size=10, color=MUTED, anchor="end"))

    # межі зон: лінійні в лог-частоті (схематично, не точні константи стандарту)
    f90, f1250 = fx(90), fx(1250)
    # «зона ризику» (ліворуч від 90 Гц) — червоне тло
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="none"/>'
             % (ox, oy - ax_h, f90 - ox, ax_h))
    # похилі межі: low-risk і NOEL ростуть із частотою
    def band(slope, color, dash=None):
        pts = []
        for k in range(0, 101):
            f = 10 ** (_m.log10(90) + (_m.log10(3000) - _m.log10(90)) * k / 100.0)
            mod = min(100.0, slope * (f - 90))
            pts.append("%.1f,%.1f" % (fx(f), my(mod)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"%s/>' % (" ".join(pts), color, d)
    p.append(band(0.08, POS))          # межа «низький ризик»
    p.append(band(0.0333, FIELD, "5 4"))  # межа NOEL (без помітного впливу)

    # підписи зон
    p.append(text((ox + f90) / 2, oy - ax_h + 18, "ризик", size=11, color=POS, bold=True))
    p.append(text(fx(300), my(8), "NOEL: без впливу", size=10.5, color=FIELD, anchor="start"))
    p.append(text(fx(300), my(40), "низький ризик", size=10.5, color=POS, anchor="start"))
    p.append(text(fx(1700), my(80), "безпечно\n(будь-яка глибина)", size=10.5, color=INK, anchor="start"))
    p.append(line(f1250, oy, f1250, oy - ax_h, color=MUTED, sw=1.2, dash="3 3"))

    p.append(text(W / 2, H - 14,
                  "Безпека = частота + глибина модуляції разом, а не частота сама по собі (схема за IEEE 1789-2015).",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "ieee1789-regions.svg"), W, H, *p,
           title="Зони миготіння: що вища частота, то глибша модуляція припустима")


# ── local-dimming: зони підсвітки, контраст і ореол (blooming) ────────────────
# Ідея (детальна версія): масив зон гасне там, де темно, → глибокий чорний і
# контраст; але світло яскравої зони підтікає в сусідні темні — ореол. Більше
# зон (mini-LED) → менший ореол.
def fig_local_dimming():
    W, H = 740, 320
    p = []

    def panel(x0, title, nx, ny, bright_cell, halo):
        cell = 26
        gap = 3
        gw = nx * (cell + gap)
        y0 = 90
        p.append(text(x0 + gw / 2, 70, title, size=12, color=INK, bold=True))
        for j in range(ny):
            for i in range(nx):
                cx = x0 + i * (cell + gap)
                cy = y0 + j * (cell + gap)
                fill = "#15171a"   # темна зона (майже чорна)
                if (i, j) == bright_cell:
                    fill = "#fbe7a2"   # яскрава зона
                elif halo and abs(i - bright_cell[0]) <= 1 and abs(j - bright_cell[1]) <= 1:
                    fill = "#5a554a"   # ореол: підтікання у сусідні
                p.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2" '
                         'fill="%s" stroke="#2b2f34" stroke-width="0.8"/>' % (cx, cy, cell, cell, fill))
        return x0 + gw, y0 + ny * (cell + gap)

    # мало зон: помітний ореол
    ex, ey = panel(70, "мало зон → ореол", 6, 5, (3, 2), True)
    p.append(text(70 + 6 * 29 / 2, ey + 22, "світло яскравої зони підтікає в сусідні темні", size=10, color="#b07d18"))

    # багато зон (mini-LED): ореол стиснутий
    sx, sy = panel(440, "багато зон (mini-LED) → ореол стиснутий", 9, 7, (5, 3), False)
    # одна підсвічена + тонкий ореол лише навколо
    p.append(text(440 + 9 * 18, sy + 22, "", size=10, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "Гасіння темних зон дає глибокий чорний і контраст; ціна — ореол навколо яскравого. Більше зон — менший ореол.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "local-dimming.svg"), W, H, *p,
           title="Локальне затемнення: контраст ціною ореолу (blooming)")


# ── dc-vs-pwm-depth: глибина модуляції — DC, ШІМ, гібрид ──────────────────────
# Ідея (детальна версія): глибина модуляції = (Imax−Imin)/(Imax+Imin). Чистий DC
# має нульову глибину (рівна лінія), ШІМ — 100 % (повний розмах), гібрид тримає
# DC згори й вмикає ШІМ лише на дуже малій яскравості.
def fig_dc_vs_pwm():
    W, H = 740, 300
    p = []
    rows = [
        ("DC: рівень струму, глибина 0 %", FIELD, "dc"),
        ("ШІМ: повний розмах, глибина 100 %", POS, "pwm"),
        ("гібрид: DC згори, ШІМ лише внизу", NEG, "hyb"),
    ]
    x0, x1 = 80, 700
    for r, (lab, color, kind) in enumerate(rows):
        y = 80 + r * 70
        base = y + 28
        p.append(text(x0, y - 6, lab, size=11, color=color, bold=True))
        p.append(line(x0, base, x1, base, color="#cccccc", sw=1.0))
        if kind == "dc":
            p.append(line(x0, base - 16, x1, base - 16, color=color, sw=2.4))
        elif kind == "pwm":
            x = x0
            pts = []
            while x < x1 - 20:
                pts += [(x, base), (x, base - 30), (x + 24, base - 30), (x + 24, base)]
                x += 60
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                     'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % q for q in pts), color))
        else:
            # ліва половина — DC рівень; права — куці ШІМ-імпульси
            mid = (x0 + x1) / 2
            p.append(line(x0, base - 20, mid, base - 20, color=color, sw=2.4))
            x = mid
            while x < x1 - 14:
                p.append(line(x, base, x, base - 12, color=color, sw=2.0))
                p.append(line(x, base - 12, x + 8, base - 12, color=color, sw=2.0))
                p.append(line(x + 8, base - 12, x + 8, base, color=color, sw=2.0))
                x += 40
            p.append(text(mid, base + 16, "перемикання DC→ШІМ", size=9, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "глибина модуляції = (Iмакс − Iмін) ÷ (Iмакс + Iмін): у DC вона 0, у ШІМ — 100 %.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dc-vs-pwm.svg"), W, H, *p,
           title="Глибина модуляції: DC, ШІМ і гібрид")


if __name__ == "__main__":
    fig_edge_lit()
    fig_led_iv()
    fig_ballast()
    fig_boost()
    fig_dimming()
    fig_strings()
    fig_ieee1789()
    fig_local_dimming()
    fig_dc_vs_pwm()
    print("OK: figures written to", OUT)
