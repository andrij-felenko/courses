# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#c9881e"   # поріг / акцент бурштину


def sine_path(ox, oy, x0, x1, amp, period, color, sw=2.6, phase=0.0, clip_lo=None):
    """Полілінія синусоїди oy - amp*sin. clip_lo (px y) — лишити плоским до нього."""
    pts = []
    for px in range(int(x0), int(x1) + 1):
        v = amp * math.sin(2 * math.pi * (px - ox + phase) / period)
        y = oy - v
        if clip_lo is not None and px < clip_lo:
            y = oy
        pts.append("%.1f,%.1f" % (px, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))


# ── random-vs-zero: де комутувати — будь-де чи в нулі ─────────────────────────
# Ідея: ліворуч ключ вмикається на схилі (стрибок напруги → широкий спектр),
# праворуч — у нулі (плавний старт → майже без завад); унизу — два спектри.

def fig_random_vs_zero():
    W, H = 860, 360
    p = []
    oy = 140
    amp = 64
    period = 220

    # ── ліва панель: random-phase ──
    lx0, lx1 = 60, 412
    p.append(arrow(60, 212, 60, 60, color=INK, sw=1.6))
    p.append(arrow(60, oy, lx1, oy, color=INK, sw=1.6))
    p.append(text(230, 56, "будь-де (random-phase)", size=12, color=INK, bold=True))
    # бліда повна синусоїда
    p.append(sine_path(60, oy, lx0, lx1, amp, period, "#e0e0e0", sw=2.0))
    # увімкнена частина — від піку схилу
    fire_l = 186
    p.append(sine_path(60, oy, fire_l, lx1, amp, period, POS, sw=2.8, clip_lo=fire_l))
    yf = oy - amp * math.sin(2 * math.pi * (fire_l - 60) / period)
    p.append(line(fire_l, oy, fire_l, yf, color=POS, sw=2.8))
    p.append(circle(fire_l, yf, 4.5, fill=BG, stroke=POS, sw=2))
    p.append(text(fire_l, oy + 22, "стрибок!", size=10, color=POS, bold=True))

    # ── права панель: zero-cross ──
    rx0, rx1 = 480, 832
    p.append(arrow(480, 212, 480, 60, color=INK, sw=1.6))
    p.append(arrow(480, oy, rx1, oy, color=INK, sw=1.6))
    p.append(text(650, 56, "у нулі (zero-cross)", size=12, color=INK, bold=True))
    p.append(sine_path(480, oy, rx0, rx1, amp, period, "#e0e0e0", sw=2.0))
    fire_r = 480 + period   # рівно перехід нуля
    p.append(sine_path(480, oy, fire_r, rx1, amp, period, FIELD, sw=2.8, clip_lo=fire_r))
    p.append(circle(fire_r, oy, 4.5, fill=BG, stroke=FIELD, sw=2))
    p.append(text(fire_r, oy + 22, "0 В — без стрибка", size=10, color=FIELD, bold=True))

    # ── спектри внизу ──
    p.append(rect(60, 244, 352, 92, fill="#fbecec", stroke="#d8a0a0", sw=1.3, rx=8))
    p.append(text(236, 266, "різкий фронт → широкий спектр", size=11, color=POS, bold=True))
    for i in range(9):
        bh = 30 - i * 2
        p.append(rect(96 + i * 30, 320 - bh, 12, bh, fill="#e7a6a6", stroke=POS, sw=0, rx=0))
    p.append(text(236, 332, "багато ВЧ-завад (EMI)", size=9, color=POS))

    p.append(rect(480, 244, 352, 92, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=8))
    p.append(text(656, 266, "пологий старт → вузький спектр", size=11, color=FIELD, bold=True))
    for i in range(3):
        bh = 26 - i * 8
        p.append(rect(560 + i * 40, 320 - bh, 14, bh, fill="#a7d4b4", stroke=FIELD, sw=0, rx=0))
    p.append(text(656, 332, "майже без завад", size=9, color=FIELD))

    render(os.path.join(OUT, "random-vs-zero.svg"), W, H, *p,
           title="Вмикати на схилі синусоїди — стрибок і завади; вмикати в нулі — плавно й чисто")


# ── zero-detector: з синусоїди — імпульс щопівперіоду ────────────────────────
# Ідея: угорі синусоїда мережі; унизу короткі логічні імпульси рівно в кожному
# переході нуля (двічі за період), які йдуть у мікроконтролер.

def fig_zero_detector():
    W, H = 800, 300
    p = []
    ox, oy = 80, 150
    aw = 640
    amp = 70
    period = 213.3

    p.append(arrow(ox, 232, ox, 66, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 16, oy + 4, "час", size=11, color=INK, italic=True, anchor="start"))
    p.append(sine_path(ox, oy, ox, ox + aw, amp, period, POS, sw=2.4))
    p.append(text(ox + 120, 78, "напруга мережі", size=10, color=POS, bold=True, anchor="start"))

    # вертикальні засічки нулів
    zeros = [ox + i * period / 2 for i in range(int(aw / (period / 2)) + 1)]
    for zx in zeros:
        if zx <= ox + aw:
            p.append(line(zx, 80, zx, 260, color="#e4e4e4", sw=1, dash="3 3"))

    # імпульси внизу
    base = 280
    top = 248
    p.append(line(ox, base, ox + aw, base, color=INK, sw=1.4))
    p.append(text(ox - 8, base + 4, "0", size=9, color=INK, anchor="end"))
    for zx in zeros:
        if zx <= ox + aw:
            p.append(line(zx - 4, base, zx - 4, top, color=NEG, sw=2.4))
            p.append(line(zx - 4, top, zx + 4, top, color=NEG, sw=2.4))
            p.append(line(zx + 4, top, zx + 4, base, color=NEG, sw=2.4))
    p.append(text(W / 2, base + 18, "логічні імпульси «тут нуль» → у мікроконтролер",
                  size=11, color=NEG, bold=True))

    render(os.path.join(OUT, "zero-detector.svg"), W, H, *p,
           title="Детектор нуля: із синусоїди — короткий імпульс у кожному переході нуля")


# ── burst-control: пропускаємо цілі півперіоди ───────────────────────────────
# Ідея: суцільний ряд півхвиль, частина віддана повністю (зелені), частина
# пропущена (бліді); вмикання й вимикання — лише в нулі.

def fig_burst_control():
    W, H = 820, 250
    p = []
    ox, oy = 60, 130
    amp = 56
    period = 120          # повний період; півхвиля = period/2
    half = period / 2
    n = 12                # півперіодів
    on = [True] * 8 + [False] * 4   # 8 із 12 ≈ 67 %

    p.append(arrow(ox, 200, ox, 60, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + n * half + 16, oy, color=INK, sw=1.6))
    p.append(text(ox + n * half + 20, oy + 4, "час", size=11, color=INK, italic=True, anchor="start"))

    for i in range(n):
        x0 = ox + i * half
        x1 = x0 + half
        col = FIELD if on[i] else "#d7dbe0"
        sw = 2.8 if on[i] else 1.6
        sign = 1 if i % 2 == 0 else -1
        pts = []
        for px in range(int(x0), int(x1) + 1):
            v = sign * amp * abs(math.sin(math.pi * (px - x0) / half))
            pts.append("%.1f,%.1f" % (px, oy - v))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), col, sw))
        # кружок нуля на межі
        p.append(circle(x0, oy, 3.0, fill=BG, stroke=INK, sw=1.2))
    p.append(circle(ox + n * half, oy, 3.0, fill=BG, stroke=INK, sw=1.2))

    p.append(text(ox + 4 * half, 74, "8 півперіодів віддано", size=10, color=FIELD, bold=True))
    p.append(text(ox + 10 * half, 74, "4 пропущено", size=10, color=MUTED, bold=True))
    p.append(text(W / 2, 214, "вмикання й вимикання — лише в нулі (○): фронтів мало, завад мало",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "burst-control.svg"), W, H, *p,
           title="Burst: одні цілі півперіоди віддаємо, інші пропускаємо (тут ≈ 67 % потужності)")


# ── phase-vs-burst: дві дороги до 50 % (вставка proj) ────────────────────────
# Ідея: згори димер ріже КОЖЕН півперіод (круті фронти), знизу burst пропускає
# ЦІЛІ півперіоди (перемикання лише в нулі). Середня та сама, спектр різний.

def fig_phase_vs_burst():
    W, H = 820, 430
    p = []
    amp = 50
    period = 150
    half = period / 2
    ox = 70
    aw = 8 * half

    # ── верх: фазовий зріз ──
    oy1 = 150
    p.append(text(ox, 64, "фазовий зріз (димер): ріжемо КОЖЕН півперіод",
                  size=13, color=POS, bold=True, anchor="start"))
    p.append(arrow(ox, oy1 + 70, ox, oy1 - 70, color=INK, sw=1.5))
    p.append(arrow(ox, oy1, ox + aw + 14, oy1, color=INK, sw=1.5))
    p.append(text(ox + aw + 18, oy1 + 4, "t", size=12, color=INK, bold=True, anchor="start"))
    p.append(sine_path(ox, oy1, ox, ox + aw, amp, period, "#e0e0e0", sw=1.8))
    for i in range(8):
        x0 = ox + i * half
        fire = x0 + half * 0.5     # запуск посеред хвилі
        sign = 1 if i % 2 == 0 else -1
        pts = []
        for px in range(int(fire), int(x0 + half) + 1):
            v = sign * amp * abs(math.sin(math.pi * (px - x0) / half))
            pts.append("%.1f,%.1f" % (px, oy1 - v))
        yf = oy1 - sign * amp * abs(math.sin(math.pi * (fire - x0) / half))
        p.append(line(fire, oy1, fire, yf, color=POS, sw=2.4))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), POS))
    p.append(text(ox, oy1 + 92, "вмикання посеред хвилі → круті фронти → радіозавади (EMI)",
                  size=11, color=POS, italic=True, anchor="start"))

    # ── низ: burst ──
    oy2 = 330
    p.append(text(ox, 264, "burst: пропускаємо ЦІЛІ півперіоди (4 з 8)",
                  size=13, color=FIELD, bold=True, anchor="start"))
    p.append(arrow(ox, oy2 + 70, ox, oy2 - 70, color=INK, sw=1.5))
    p.append(arrow(ox, oy2, ox + aw + 14, oy2, color=INK, sw=1.5))
    p.append(text(ox + aw + 18, oy2 + 4, "t", size=12, color=INK, bold=True, anchor="start"))
    on = [True, False, True, False, True, False, True, False]
    for i in range(8):
        x0 = ox + i * half
        sign = 1 if i % 2 == 0 else -1
        col = FIELD if on[i] else "#d7dbe0"
        sw = 2.6 if on[i] else 1.6
        pts = []
        for px in range(int(x0), int(x0 + half) + 1):
            v = sign * amp * abs(math.sin(math.pi * (px - x0) / half))
            pts.append("%.1f,%.1f" % (px, oy2 - v))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), col, sw))
        p.append(circle(x0, oy2, 3.2, fill=BG, stroke=GOLD, sw=1.6))
    p.append(circle(ox + aw, oy2, 3.2, fill=BG, stroke=GOLD, sw=1.6))
    p.append(text(ox, oy2 + 92, "вмикання й вимикання лише в нулі (○) → фронтів нема → тихо",
                  size=11, color=FIELD, italic=True, anchor="start"))

    render(os.path.join(OUT, "phase-vs-burst.svg"), W, H, *p,
           title="Дві дороги до 50 % потужності: різати кожну хвилю чи пропускати цілі")


# ── duty-thermal: N/M задає потужність, інерція згладжує (вставка proj) ───────
# Ідея: три рядки вікон M=8 з різною часткою ввімкнених комірок (1/8, 4/8, 6/8),
# унизу — «миттєва» пилка потужності й майже рівна температура.

def fig_duty_thermal():
    W, H = 820, 410
    p = []
    ox = 90
    cell = 84
    M = 8
    rows = [
        (110, [1, 0, 0, 0, 0, 0, 0, 0], "1/8", "P ≈ 12.5 %"),
        (190, [1, 0, 1, 0, 1, 0, 1, 0], "4/8", "P ≈ 50 %"),
        (270, [1, 0, 1, 1, 0, 1, 1, 1], "6/8", "P ≈ 75 % (рівномірно)"),
    ]
    p.append(text(ox, 74, "вікно M = 8 півперіодів (≈ 80 мс у мережі 50 Гц):",
                  size=12, color=MUTED, italic=True, anchor="start"))
    for ry, cells, frac, lab in rows:
        for i in range(M):
            x0 = ox + i * cell
            on = cells[i]
            fill = "#fdecea" if on else "#eef0f2"
            stroke = POS if on else "#c4c9cf"
            p.append(rect(x0, ry, cell, 44, fill=fill, stroke=stroke, sw=1.4, rx=0))
            if on:
                p.append(text(x0 + cell / 2, ry + 28, "½", size=12, color=POS, bold=True))
        p.append(text(ox - 12, ry + 28, frac, size=12, color=MUTED, bold=True, anchor="end"))
        p.append(text(ox + M * cell + 12, ry + 28, lab, size=12, color=INK, bold=True, anchor="start"))

    # температура: пилка миттєвої потужності + рівна лінія
    ty = 360
    p.append(text(ox, 332, "температура нагрівача (інерція згладжує пакети):",
                  size=12, color=FIELD, bold=True, anchor="start"))
    p.append(arrow(ox, ty + 36, ox, ty - 40, color=INK, sw=1.5))
    p.append(arrow(ox, ty, ox + M * cell + 14, ty, color=INK, sw=1.5))
    p.append(text(ox + M * cell + 18, ty + 4, "t", size=12, color=INK, bold=True, anchor="start"))
    # пилка
    saw = []
    for i in range(M):
        x0 = ox + i * cell
        hi = ty - 30 if i % 2 == 0 else ty - 6
        saw.append("%.1f,%.1f" % (x0, hi))
        saw.append("%.1f,%.1f" % (x0 + cell, hi))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (" ".join(saw), MUTED))
    # рівна температура
    p.append(line(ox, ty - 20, ox + M * cell, ty - 20, color=FIELD, sw=2.6))
    p.append(text(ox + M * cell - 10, ty - 26, "температура ≈ рівна",
                  size=11, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(OUT, "duty-thermal.svg"), W, H, *p,
           title="Частка N/M задає середню потужність; теплова інерція згладжує пакети")


# ── zc-anatomy: будова модуля детектора нуля (вставка comp) ───────────────────
# Ідея: дві зони — мережева (баласт + дві антипаралельні LED) і логічна
# (фототранзистор + підтяжка до 3.3 В), розділені бар'єром ізоляції.

def fig_zc_anatomy():
    W, H = 760, 380
    p = []
    # зони
    p.append(rect(40, 60, 320, 280, fill="#fbecec", stroke="#d8a0a0", sw=1.4, rx=10))
    p.append(rect(400, 60, 320, 280, fill="#eef6ef", stroke="#a7d4b4", sw=1.4, rx=10))
    p.append(text(200, 84, "мережевий бік (небезпечно)", size=12, color=POS, bold=True))
    p.append(text(560, 84, "бік логіки (МК, безпечно)", size=12, color=FIELD, bold=True))
    # бар'єр ізоляції
    p.append(line(380, 70, 380, 330, color=MUTED, sw=2, dash="6 5"))
    p.append(text(380, 352, "бар'єр гальванічної ізоляції", size=11, color=MUTED, italic=True))

    # мережевий бік: L, баласт, дві LED
    p.append(text(70, 150, "L", size=14, color=INK, bold=True, anchor="end"))
    p.append(text(70, 270, "N", size=14, color=INK, bold=True, anchor="end"))
    b, bw, bh = textbox(150, 150, "R_баласт\n~30–47 кОм\n0.5–1 Вт", size=10, fill=BG, stroke=INK, sw=1.4)
    p.append(b)
    led = textbox(150, 270, "дві LED\nантипаралельно", size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.5)
    p.append(led[0])
    p.append(line(76, 150, 150 - bw / 2, 150, color=INK, sw=1.6))
    p.append(line(150, 150 + bh / 2, 150, 270 - led[2] / 2, color=INK, sw=1.6))
    p.append(line(76, 270, 150 - led[1] / 2, 270, color=INK, sw=1.6))
    p.append(mtext(290, 205, ["світить", "будь-яка", "півхвиля"], size=10, color=MUTED))

    # логічний бік: фототранзистор, підтяжка, GPIO
    pt = textbox(500, 270, "фото-\nтранзистор", size=10, fill=BG, stroke=INK, sw=1.4)
    p.append(pt[0])
    p.append(text(660, 130, "+3.3 В", size=12, color=POS, bold=True, anchor="end"))
    pu, puw, puh = textbox(560, 165, "R_pu 10 кОм", size=10, fill=BG, stroke=INK, sw=1.4)
    p.append(pu)
    p.append(line(620, 130, 620, 165 - puh / 2, color=INK, sw=1.6))
    p.append(line(560, 165 + puh / 2, 560, 270 - pt[2] / 2, color=INK, sw=1.6))
    p.append(line(560 + 0, 165, 660, 165, color=INK, sw=1.6))
    p.append(text(672, 169, "GPIO", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(672, 184, "(переривання)", size=9, color=FIELD, anchor="start"))
    p.append(mtext(560, 312, ["LED світить → транзистор веде → GPIO «0»",
                              "коло нуля LED гасне → GPIO стрибає в «1»"], size=10, color=INK))

    render(os.path.join(OUT, "zc-anatomy.svg"), W, H, *p,
           title="Будова модуля детектора нуля: дві землі, розв'язані оптопарою")


# ── zc-timing: синус, світіння LED по |U|, імпульси GPIO (вставка comp) ──────
# Ідея: три доріжки — напруга мережі, світіння світлодіодів за модулем |U|
# (гасне коло нуля), і логічні імпульси GPIO рівно в кожному переході нуля.

def fig_zc_timing():
    W, H = 780, 380
    p = []
    ox = 90
    aw = 600
    period = 200
    amp = 40

    # доріжка 1: напруга
    oy1 = 100
    p.append(text(20, oy1, "U мережі", size=11, color=INK, bold=True, anchor="start"))
    p.append(line(ox, oy1, ox + aw, oy1, color="#e4e4e4", sw=1))
    p.append(sine_path(ox, oy1, ox, ox + aw, amp, period, POS, sw=2.2))

    zeros = [ox + i * period / 2 for i in range(int(aw / (period / 2)) + 1)]
    for zx in zeros:
        if zx <= ox + aw:
            p.append(line(zx, 70, zx, 330, color="#eeeeee", sw=1, dash="3 3"))

    # доріжка 2: світіння LED ~ |U|, гасне коло нуля (поріг)
    oy2 = 200
    base2 = oy2 + 35
    p.append(text(20, oy2, "світло LED", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(20, oy2 + 14, "(|U| над порогом)", size=9, color=MUTED, anchor="start"))
    thr = base2 - 8
    p.append(line(ox, thr, ox + aw, thr, color=GOLD, sw=1.2, dash="4 3"))
    p.append(text(ox + aw + 4, thr + 4, "поріг", size=9, color=GOLD, anchor="start"))
    pts = []
    for px in range(ox, ox + aw + 1):
        v = abs(math.sin(2 * math.pi * (px - ox) / period)) * 70
        y = base2 - v
        pts.append("%.1f,%.1f" % (px, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))

    # доріжка 3: GPIO імпульс у кожному нулі
    oy3 = 300
    base3 = oy3 + 25
    top3 = oy3 - 10
    p.append(text(20, oy3, "GPIO", size=11, color=NEG, bold=True, anchor="start"))
    p.append(line(ox, base3, ox + aw, base3, color=INK, sw=1.3))
    p.append(text(ox + aw + 4, top3 + 4, "1", size=10, color=NEG, anchor="start"))
    p.append(text(ox + aw + 4, base3 + 4, "0", size=10, color=NEG, anchor="start"))
    for zx in zeros:
        if zx <= ox + aw:
            p.append(line(zx - 4, base3, zx - 4, top3, color=NEG, sw=2.2))
            p.append(line(zx - 4, top3, zx + 4, top3, color=NEG, sw=2.2))
            p.append(line(zx + 4, top3, zx + 4, base3, color=NEG, sw=2.2))

    # позначка 10 мс між сусідніми нулями
    if len(zeros) >= 3:
        z0, z1 = zeros[1], zeros[2]
        p.append(line(z0, 64, z1, 64, color=MUTED, sw=1.2))
        p.append(text((z0 + z1) / 2, 60, "10 мс (½ періоду 50 Гц)", size=10, color=MUTED, bold=True))

    p.append(text(W / 2, base3 + 22, "кожен фронт = переривання в мікроконтролері",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "zc-timing.svg"), W, H, *p,
           title="Один імпульс у кожному переході нуля (50 Гц → кожні 10 мс)")


if __name__ == "__main__":
    fig_random_vs_zero()
    fig_zero_detector()
    fig_burst_control()
    fig_phase_vs_burst()
    fig_duty_thermal()
    fig_zc_anatomy()
    fig_zc_timing()
    print("OK: figures written to", OUT)
