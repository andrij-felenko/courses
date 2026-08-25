# -*- coding: utf-8 -*-
"""Фігури до теми «kT/C-шум у ланцюгах вибірки» (аналогова, кутом теорії кіл).
Чотири фігури:
  sample-freeze.svg  — ключ замикає RC, на ємності тремтить тепловий шум; розмикання
                       заморожує випадковий миттєвий рівень як похибку відліку
  r-cancels.svg      — шум росте як √R, смуга падає як 1/R: добуток √(kT/C) від R не залежить
  cap-tradeoff.svg   — більша ємність тихіша (шум ∝ 1/√C), але повільніша й ненажерливіша
  cds.svg            — подвійна корельована вибірка: відняти заморожений рівень скидання
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _wiggle(seed):
    """Детермінований псевдошум у [-1,1] — без залежностей."""
    x = math.sin(seed * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def sample_freeze():
    """Ключ + R + C: на ємності тремтить теплова напруга; розмикання ловить її миттєвий рівень."""
    W, H = 720, 380
    p = []
    # ── ліворуч: схема ключ–резистор–ємність ──
    y = 150
    xj = 90
    p.append(text(xj - 40, y - 60, "джерело", size=12, color=MUTED, anchor="start"))
    p.append(line(40, y, xj, y, color=INK, sw=2))
    # ключ (розімкнений штрих угору)
    p.append(circle(xj, y, 3, fill=INK, stroke=INK, sw=1))
    p.append(line(xj, y, xj + 34, y - 20, color=POS, sw=2.4))
    p.append(circle(xj + 40, y, 3, fill=INK, stroke=INK, sw=1))
    p.append(text(xj + 20, y - 30, "ключ", size=11, color=POS))
    # резистор Rвкл
    rx = xj + 40
    p.append(line(rx, y, rx + 18, y, color=INK, sw=2))
    p.append(rect(rx + 18, y - 9, 46, 18, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    p.append(text(rx + 41, y + 5, "R", size=13, bold=True))
    p.append(text(rx + 41, y - 16, "опір ключа", size=10, color=MUTED))
    p.append(line(rx + 64, y, rx + 110, y, color=INK, sw=2))
    # вузол вибірки
    nx = rx + 110
    p.append(circle(nx, y, 3.5, fill=INK, stroke=INK, sw=1))
    p.append(text(nx + 6, y - 8, "вузол вибірки", size=11, color=NEG, anchor="start"))
    # ємність C на землю
    p.append(line(nx, y, nx, y + 30, color=INK, sw=2))
    p.append(line(nx - 16, y + 30, nx + 16, y + 30, color=INK, sw=2.4))
    p.append(line(nx - 16, y + 38, nx + 16, y + 38, color=INK, sw=2.4))
    p.append(text(nx + 22, y + 36, "C", size=14, bold=True, anchor="start"))
    # земля
    gy = y + 58
    p.append(line(nx, y + 38, nx, gy, color=INK, sw=2))
    p.append(line(nx - 14, gy, nx + 14, gy, color=INK, sw=2))
    p.append(line(nx - 9, gy + 5, nx + 9, gy + 5, color=INK, sw=2))
    p.append(line(nx - 4, gy + 10, nx + 4, gy + 10, color=INK, sw=2))

    # ── праворуч: напруга на ємності в часі — тремтить, тоді замерзає ──
    gx0, gx1 = 360, 690
    gy0 = 250
    span = gx1 - gx0
    midx = gx0 + span * 0.55       # момент розмикання ключа
    p.append(line(gx0, gy0, gx1, gy0, color=MUTED, sw=1))            # нуль
    p.append(text(gx0 - 6, gy0 + 4, "0", size=11, color=MUTED, anchor="end"))
    # тремтлива напруга, доки ключ замкнений
    amp = 30
    pts = []
    N = 70
    held = None
    for k in range(N + 1):
        xx = gx0 + span * k / N
        if xx <= midx:
            v = _wiggle(k * 1.7) * amp
            held = v
        else:
            v = held
        pts.append((xx, gy0 - v))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))
    # вертикаль «розмикання»
    p.append(line(midx, gy0 - amp - 18, midx, gy0 + amp + 18, color=POS, sw=1.4, dash="4 3"))
    p.append(text(midx, gy0 - amp - 24, "ключ розімкнено", size=11, bold=True, color=POS))
    # заморожений рівень як похибка
    p.append(line(midx, gy0, gx1, gy0 - held, color=FIELD, sw=1.2, dash="2 3"))
    p.append(text(gx1 - 4, gy0 - held - 6, "застиглий рівень", size=11, color=FIELD, anchor="end"))
    p.append(text((gx0 + midx) / 2, gy0 + amp + 30, "тремтить (RC згладжує)", size=11, color=MUTED))
    p.append(text((midx + gx1) / 2, gy0 + amp + 30, "застигло як похибка відліку", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 350,
                      "Замкнений ключ дає шуму резистора вилитися на ємність; розмикання «фотографує»\n"
                      "випадковий миттєвий рівень — і він лишається у відліку як похибка σ = √(kT/C).",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'sample-freeze.svg'), W, H, *p,
           title="Вибірка заморожує миттєвий тепловий шум на ємності")


def r_cancels():
    """Шум росте як √R, смуга падає як 1/R — їхній добуток від R не залежить."""
    W, H = 700, 380
    p = []
    ox, oy = 100, 300
    ax_w, ax_h = 470, 240
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # вісь R
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # вісь рівня
    p.append(text(ox + ax_w / 2, oy + 34, "опір шляху R  →", size=13, bold=True))
    p.append(text(ox - 60, oy - ax_h / 2, "рівень", size=13, bold=True))

    def curve(fn, col, sw=2.4, dash=None):
        pts = []
        for i in range(81):
            r = 0.12 + i / 80.0 * 1.0          # відносний R від 0.12 до 1.12
            xx = ox + (r - 0.12) / 1.0 * ax_w
            yy = oy - fn(r) * ax_h
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, da)

    # шумова напруга ∝ √R (нормуємо так, щоб у R=1 була 0.62)
    p.append(curve(lambda r: 0.62 * math.sqrt(r), POS))
    p.append(text(ox + ax_w + 4, oy - 0.62 * math.sqrt(1.12) * ax_h, "шум  ∝ √R", size=12, color=POS, anchor="start"))
    # смуга ∝ 1/R
    p.append(curve(lambda r: 0.55 / r * 0.12, NEG))
    p.append(text(ox + ax_w + 4, oy - 0.55 / 1.12 * 0.12 * ax_h - 2, "смуга  ∝ 1/R", size=12, color=NEG, anchor="start"))
    # добуток — рівна лінія √(kT/C)
    flat = 0.50
    p.append(line(ox, oy - flat * ax_h, ox + ax_w, oy - flat * ax_h, color=FIELD, sw=3))
    p.append(text(ox + ax_w + 4, oy - flat * ax_h + 4, "√(kT/C)", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(ox + ax_w / 2, oy - flat * ax_h - 10, "добуток сталий — від R не залежить", size=12, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 356,
                      "Більший опір додає шумової напруги (√R), але рівно настільки ж звужує смугу (1/R).\n"
                      "Заморожений на ємності шум — добуток цих двох — не залежить від R: лишається √(kT/C).",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'r-cancels.svg'), W, H, *p,
           title="Чому опір випадає: шум росте як √R, смуга падає як 1/R")


def cap_tradeoff():
    """Більша ємність: тихіша (1/√C), але повільніша (RC) й ненажерливіша (CV²f)."""
    W, H = 720, 360
    p = []
    cols3 = [("мала C", 0.6), ("середня C", 1.0), ("велика C", 1.7)]
    base_y = 250
    x0 = 120
    gap = 210
    bw = 58
    # три показники як висоти стовпчиків біля кожної ємності
    for i, (lbl, csc) in enumerate(cols3):
        cx = x0 + i * gap
        # шум ∝ 1/√C
        noise_h = 150 / math.sqrt(csc)
        # час осідання ∝ C
        sett_h = 70 * csc
        # заряд/енергія за такт ∝ C
        pow_h = 60 * csc
        trio = [
            ("шум √(kT/C)", noise_h, POS, "#fdecea", "1/√C"),
            ("час осідання", sett_h, NEG, "#eaf0fd", "∝ C"),
            ("заряд за такт", pow_h, FIELD, "#eafaf0", "∝ C"),
        ]
        sub = bw / 3 + 6
        for j, (nm, h, col, fillc, law) in enumerate(trio):
            bx = cx - sub + j * (sub)
            p.append(rect(bx - 9, base_y - h, 18, h, fill=fillc, stroke=col, sw=1.6))
        p.append(text(cx, base_y + 22, lbl, size=14, bold=True))
        # символ ємності
        p.append(line(cx - 14, base_y + 38, cx + 14, base_y + 38, color=INK, sw=2.2))
        p.append(line(cx - 14, base_y + 44, cx + 14, base_y + 44, color=INK, sw=2.2))
    p.append(line(x0 - 40, base_y, x0 + 2 * gap + 40, base_y, color=INK, sw=1.5))
    # легенда
    lx = 250
    ly = 70
    leg = [("шум √(kT/C) — менший при більшій C", POS, "#fdecea"),
           ("час осідання RC — більший при більшій C", NEG, "#eaf0fd"),
           ("заряд C·V за такт — більший при більшій C", FIELD, "#eafaf0")]
    for k, (t, col, fillc) in enumerate(leg):
        yy = ly + k * 20
        p.append(rect(lx, yy - 9, 14, 14, fill=fillc, stroke=col, sw=1.6))
        p.append(text(lx + 22, yy + 3, t, size=12, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 336,
                      "Збільшення ємності стишує шум лише як 1/√C — учетверо більша C дає вдвічі тихіше.\n"
                      "Ціна — пропорційно довше осідання й більший заряд за такт: тиша купується площею.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'cap-tradeoff.svg'), W, H, *p,
           title="Ціна тиші: більша ємність тихіша, але повільніша й ненажерливіша")


def cds():
    """Корельована подвійна вибірка: зміряти рівень скидання, тоді сигнал, відняти — kT/C-похибка геть."""
    W, H = 720, 360
    p = []
    gx0, gx1 = 70, 560
    gy0 = 170
    span = gx1 - gx0
    p.append(line(gx0, gy0, gx1, gy0, color=MUTED, sw=1))
    # фаза 1 — скидання: застиглий шумовий рівень V0
    t1 = gx0 + span * 0.22
    t2 = gx0 + span * 0.62
    v0 = 34            # заморожений шум скидання (та сама kT/C-похибка)
    sig = 70           # корисний приріст сигналу
    # рівень після скидання
    p.append(line(gx0, gy0 - v0, t1, gy0 - v0, color=POS, sw=2.4))
    p.append(line(t1, gy0 - v0, t2, gy0 - v0, color=POS, sw=2.4, dash="3 3"))
    p.append(text((gx0 + t1) / 2, gy0 - v0 - 10, "відлік 1: рівень скидання", size=11, bold=True, color=POS))
    # сигнал додається поверх ТОГО САМОГО зміщення
    p.append(line(t1, gy0 - v0, t1, gy0 - v0 - sig, color=INK, sw=1.4, dash="2 2"))
    p.append(line(t1, gy0 - v0 - sig, t2, gy0 - v0 - sig, color=NEG, sw=2.4))
    p.append(text((t1 + t2) / 2, gy0 - v0 - sig - 10, "відлік 2: сигнал + те саме зміщення", size=11, bold=True, color=NEG))
    # мітки відліків
    for tx, lab, col in [(t1, "вибірка A", POS), (t2, "вибірка B", NEG)]:
        p.append(line(tx, gy0 + 6, tx, gy0 - 100, color=col, sw=1, dash="4 3"))
        p.append(text(tx, gy0 + 22, lab, size=11, color=col))
    # стрілка віднімання → праворуч чистий результат
    rx = gx1 + 30
    p.append(arrow(t2 + 8, gy0 - v0 - sig / 2, rx, gy0 - v0 - sig / 2, color=INK, sw=2))
    p.append(text((t2 + rx) / 2 + 6, gy0 - v0 - sig / 2 - 8, "B − A", size=12, bold=True))
    # результат — лише сигнал, без зміщення
    p.append(line(rx, gy0, rx + 90, gy0, color=MUTED, sw=1))
    p.append(line(rx + 10, gy0, rx + 10, gy0 - sig, color=INK, sw=1.4, dash="2 2"))
    p.append(line(rx, gy0 - sig, rx + 90, gy0 - sig, color=FIELD, sw=2.8))
    p.append(text(rx + 45, gy0 - sig - 8, "чистий сигнал", size=11, bold=True, color=FIELD))
    p.append(text(rx + 45, gy0 + 18, "kT/C-зсув віднято", size=11, color=FIELD))

    b, _, _ = textbox(W / 2, 326,
                      "Та сама заморожена kT/C-похибка сидить в обох відліках. Зміряти рівень скидання,\n"
                      "тоді сигнал, і відняти — спільне випадкове зміщення зникає, лишається корисне.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'cds.svg'), W, H, *p,
           title="Корельована подвійна вибірка прибирає заморожений kT/C-зсув")


# ════════════════════════════════════════════════════════════════════════════
# Фігури math-вставки «Звідки береться kT/C»
# ════════════════════════════════════════════════════════════════════════════
def spectral():
    """Спектральний шлях: пласка щільність 4kTR × квадрат АЧХ RC-фільтра;
    площа під добутком = kT/C; ефективна смуга 1/(4RC) = (π/2)·f₋₃дБ."""
    W, H = 720, 420
    p = []

    ox, oy = 96, 320          # початок осей (низ-ліво)
    axw, axh = 540, 250
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))          # вісь частоти
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))          # вісь щільності
    p.append(text(ox + axw - 4, oy + 26, "частота f  →", size=12, color=INK, anchor="end"))
    p.append(text(ox - 10, oy - axh + 4, "В²/Гц", size=12, color=INK, anchor="end", bold=True))

    # пласка щільність 4kTR
    yflat = oy - 200
    p.append(line(ox, yflat, ox + axw, yflat, color=POS, sw=2.4, dash="7 5"))
    p.append(text(ox + 8, yflat - 10, "білий шум опору 4kTR — однаковий на всіх частотах",
                  size=12, color=POS, bold=True, anchor="start"))

    # частота зрізу
    fc_x = ox + 150
    p.append(line(fc_x, oy, fc_x, oy - axh + 18, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(fc_x, oy + 18, "f₋₃дБ", size=11, color=MUTED, anchor="middle"))
    p.append(text(fc_x, oy + 33, "1/(2πRC)", size=10, color=MUTED, anchor="middle"))

    def Hsq(fx):
        r = (fx - ox) / (fc_x - ox)        # f/fc
        return 1.0 / (1.0 + r * r)
    gain = oy - yflat
    pts = []
    N = 160
    for i in range(N + 1):
        fx = ox + axw * i / N
        pts.append((fx, oy - gain * Hsq(fx)))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % q for q in pts[1:])
    fill_path = path + " L %.1f %.1f L %.1f %.1f Z" % (ox + axw, oy, ox, oy)
    p.append('<path d="%s" fill="#e9f6ee" stroke="none"/>' % fill_path)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path, FIELD))
    p.append(text(fc_x + 150, yflat + 60, "× квадрат АЧХ RC-фільтра", size=12, color=FIELD, bold=True, anchor="middle"))
    p.append(text(fc_x + 150, yflat + 78, "|H|² = 1/(1+(2πfRC)²)", size=12, color=FIELD, anchor="middle"))

    body, w0, h0 = textbox(ox + 250, oy - 96,
                           "площа під добутком =\nуся шумова потужність ⟨U²⟩ =\n4kTR · 1/(4RC) = kT/C",
                           size=12, color=INK, fill="#ffffff", stroke=FIELD, sw=2)
    p.append(body)

    # ефективна (шумова) смуга: прямокутник тієї ж площі, висотою 4kTR
    nbw = (fc_x - ox) * (math.pi / 2)      # 1/(4RC) = (π/2)·f_c
    p.append(rect(ox, yflat, nbw, oy - yflat, fill="none", stroke=NEG, sw=1.8, rx=0))
    p.append(line(ox, oy - axh + 40, ox + nbw, oy - axh + 40, color=NEG, sw=1.4))
    p.append(text(ox + nbw / 2, oy - axh + 32,
                  "ефективна смуга 1/(4RC) = (π/2)·f₋₃дБ", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(line(ox + nbw, oy, ox + nbw, yflat, color=NEG, sw=1.2, dash="3 3"))

    render(os.path.join(OUT, "spectral.svg"), W, H, *p)


def two_roads():
    """Дві незалежні дороги (інтеграл по спектру ↔ рівнорозподіл) сходяться в kT/C."""
    W, H = 720, 400
    p = []

    lx = 70
    p.append(fitbox(lx, 70, 250, 150,
                    "ШЛЯХ 1 · по спектру\n\n4kTR проходить крізь\nRC-фільтр; інтегруємо\n⟨U²⟩ = ∫ 4kTR·|H|² df\nвід 0 до ∞;  R скорочується",
                    size=12, fill="#fdecea", stroke=POS, sw=2, color=INK))

    rx = 400
    p.append(fitbox(rx, 70, 250, 150,
                    "ШЛЯХ 2 · рівнорозподіл\n\nна 1 ступінь вільності\n½kT теплової енергії;\n½C⟨U²⟩ = ½kT\n→ ⟨U²⟩ = kT/C миттєво",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=2, color=INK))

    cy_res = 310
    p.append(arrow(lx + 125, 226, W / 2 - 70, cy_res - 34, color=POS, sw=2.4))
    p.append(arrow(rx + 125, 226, W / 2 + 70, cy_res - 34, color=NEG, sw=2.4))

    body, w0, h0 = textbox(W / 2, cy_res, "⟨U²⟩ = kT/C", size=22, color=INK,
                           fill="#e9f6ee", stroke=FIELD, sw=2.6, bold=True)
    p.append(body)

    p.append(text(W / 2, cy_res + 56, "той самий результат — не випадково:", size=12, color=INK, bold=True))
    p.append(text(W / 2, cy_res + 74,
                  "та сама теплова метушня і шумить (флуктуація), і гальмує заряд (дисипація)",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "two-roads.svg"), W, H, *p)


def cds_timeline():
    """Шлях прийому: CCD як пам'ять (1969) → шум скидання → CDS у Westinghouse (~1972)
    → публікація 1974 → телебачення, астрономія, CMOS-сенсори."""
    W, H = 760, 430
    p = []

    spine_y = 150
    p.append(line(60, spine_y, W - 60, spine_y, color=MUTED, sw=2))
    p.append(arrow(W - 80, spine_y, W - 50, spine_y, color=MUTED, sw=2))

    # три віхи на спині: рік + короткий підпис, рамка під ним
    milestones = [
        (170, "1969", "CCD у Bell Labs\n(Бойл, Сміт)\nзадуманий як ПАМ'ЯТЬ",
         "#eaf0fd", NEG),
        (385, "~1972", "CDS у Westinghouse\n(Марвін Вайт)\nшум скидання — відняти",
         "#e9f6ee", FIELD),
        (600, "1974", "публікація\nWhite et al.,\nIEEE JSSC",
         "#fdecea", POS),
    ]
    for x, year, label, fill, stroke in milestones:
        p.append(circle(x, spine_y, 6, fill=stroke, stroke=stroke, sw=1))
        p.append(text(x, spine_y - 16, year, size=15, color=stroke, bold=True))
        p.append(fitbox(x - 95, spine_y + 22, 190, 78, label,
                        size=12, fill=fill, stroke=stroke, sw=2, color=INK))

    # проблема, що звела 1969 і 1972 (над спиною, посередині)
    p.append(text(W / 2, 60, "слабкий піксель тоне в kT/C-шумі скидання → не зменшити, ємність задерти не можна",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 80, "ключ скидання щоразу саджає на вузол ≈√(kT/C) ~ сотні мкВ",
                  size=11, color=MUTED))

    # розгалуження «куди пішло» — від останньої віхи вниз до трьох застосувань
    fork_y = 330
    fanx = [180, 380, 580]
    fan = [
        ("телебачення", "перші твердотільні\nтелекамери бачать\nу тінях"),
        ("астрономія", "CCD-камери NASA;\nглибокий космос\nз кінця 1970-х"),
        ("CMOS-сенсори", "4T-піксель досі;\nкамера телефону\nщокадру"),
    ]
    p.append(text(W / 2, fork_y - 36, "звідти — у всю прецизійну вибірку:", size=12, color=INK, bold=True))
    for x, (head, body) in zip(fanx, fan):
        p.append(arrow(W / 2, fork_y - 24, x, fork_y - 4, color=MUTED, sw=1.6))
        p.append(textbox(x, fork_y + 14, head, size=12, fill=FILL, stroke=LINE, sw=1.6, color=INK, bold=True)[0])
        p.append(fitbox(x - 92, fork_y + 32, 184, 56, body, size=11,
                        fill=BG, stroke=MUTED, sw=1, color=MUTED))

    render(os.path.join(OUT, "cds-timeline.svg"), W, H, *p)


if __name__ == '__main__':
    sample_freeze()
    r_cancels()
    cap_tradeoff()
    cds()
    spectral()
    two_roads()
    cds_timeline()
    print("OK: 7 figures ->", OUT)
