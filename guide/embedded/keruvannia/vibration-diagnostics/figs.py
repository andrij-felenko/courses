# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── маленькі помічники для цієї теми ──────────────────────────────────────────

def axes(x0, y0, w, h, xlabel, ylabel):
    """Осі: горизонтальна (частота/час) і вертикальна (амплітуда). y0 — низ осі."""
    s  = line(x0, y0, x0 + w, y0, color=INK, sw=1.6)          # вісь X
    s += line(x0, y0, x0, y0 - h, color=INK, sw=1.6)          # вісь Y
    s += text(x0 + w, y0 + 18, xlabel, size=11, color=MUTED, anchor="end")
    s += text(x0 - 6, y0 - h - 6, ylabel, size=11, color=MUTED, anchor="middle")
    return s

def bar(xc, y0, val, col, w=8):
    """Вертикальна смужка спектра: висота val (px) від низу осі y0."""
    return rect(xc - w / 2, y0 - val, w, val, fill=col, stroke=col, sw=1, rx=2)

def wave(x0, y0, w, amp, fn, col, n=240, sw=1.8):
    """Лінія сигналу: fn(t) для t у [0,1], масштаб по y = amp."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - fn(t) * amp
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join(pts), col, sw))

def smooth_noise(seed):
    """Детермінований «шум» як сума кількох синусів (без залежностей)."""
    import math as m
    def f(t):
        v = 0.0
        for k in range(1, 7):
            v += m.sin(2 * m.pi * (k * 3 + seed) * t + seed * k) / k
        return v * 0.18
    return f


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — три величини: зміщення / швидкість / прискорення
# ════════════════════════════════════════════════════════════════════════════
def fig_three_quantities():
    W, H = 760, 320
    panels = [
        ("Зміщення (мм)",   [9, 5, 2, 1, 0.5],            NEG,  "низькі гучніші"),
        ("Швидкість (мм/с)",[5, 6, 5, 5, 4],              FIELD,"рівно по смузі"),
        ("Прискорення (g)", [0.5, 1, 2, 4, 7],            POS,  "високі гучніші"),
    ]
    pw = 230
    gap = 18
    x = 26
    body = ""
    freqs_lbl = ["1×", "2×", "5×", "10×", "20×"]
    for title, vals, col, note in panels:
        x0, y0 = x + 8, 250
        h_ax, w_ax = 150, pw - 30
        body += axes(x0, y0, w_ax, h_ax, "частота", "")
        step = w_ax / (len(vals) + 0.5)
        mx = max(max(v for _, vv, _, _ in panels for v in vv) for _ in [0])
        for i, v in enumerate(vals):
            xc = x0 + step * (i + 0.7)
            body += bar(xc, y0, v / mx * h_ax * 0.92, col, w=14)
            body += text(xc, y0 + 16, freqs_lbl[i], size=9.5, color=MUTED)
        body += text(x + pw / 2, 40, title, size=13, color=col, bold=True)
        body += text(x + pw / 2, 286, note, size=11, color=MUTED, italic=True)
        x += pw + gap
    render(os.path.join(OUT, "three-quantities.svg"), W, H, body,
           title="Одне коливання — три величини, різна вага частот")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — карта несправностей на осі частот
# ════════════════════════════════════════════════════════════════════════════
def fig_fault_map():
    W, H = 760, 380
    x0, y0 = 70, 250
    w_ax, h_ax = 640, 180
    body = axes(x0, y0, w_ax, h_ax, "частота (× обертів)", "амплітуда")

    # позиції по осі: множники обертів
    def fx(mult):  # 0..6.2 × → px
        return x0 + (mult / 6.4) * w_ax
    for m in [1, 2, 3, 4, 5, 6]:
        xc = fx(m)
        body += line(xc, y0, xc, y0 + 5, color=MUTED, sw=1)
        body += text(xc, y0 + 18, "%d×" % m, size=10, color=MUTED)

    # здорова машина (зелене): сильний 1×, кволі гармоніки
    healthy = {1: 0.95, 2: 0.28, 3: 0.16, 4: 0.10, 5: 0.07, 6: 0.05}
    for m, v in healthy.items():
        body += bar(fx(m) - 6, y0, v * h_ax, FIELD, w=9)

    # хвора (червоне): роздутий 1× (дисбаланс), 2× (розцентрування),
    # гребінець (розхитаність) + неціловий пік підшипника 3.6×
    body += bar(fx(2) + 6, y0, 0.62 * h_ax, POS, w=9)        # 2× розцентрування
    body += bar(fx(3.6), y0, 0.50 * h_ax, POS, w=9)          # підшипник BPFO 3.6×

    # підписи-виноски
    body += text(fx(1), y0 - 0.95 * h_ax - 10, "1× дисбаланс", size=10.5, color=INK, bold=True)
    body += text(fx(2) + 22, y0 - 0.62 * h_ax - 8, "2× розцентрування", size=10, color=POS, anchor="start")
    bx = fx(3.6)
    body += text(bx, y0 - 0.50 * h_ax - 22, "3.6× підшипник", size=10, color=POS)
    body += text(bx, y0 - 0.50 * h_ax - 9, "(неціловий!)", size=9.5, color=POS, italic=True)
    body += text(fx(4.6), y0 - 0.16 * h_ax - 8, "цілі гармоніки → розхитаність", size=9.5, color=MUTED, anchor="middle")

    # легенда
    body += rect(x0 + 6, 44, 13, 13, fill=FIELD, stroke=FIELD, sw=1, rx=2)
    body += text(x0 + 26, 55, "здорова машина", size=11, color=INK, anchor="start")
    body += rect(x0 + 196, 44, 13, 13, fill=POS, stroke=POS, sw=1, rx=2)
    body += text(x0 + 216, 55, "виросли нові піки = несправність", size=11, color=INK, anchor="start")

    render(os.path.join(OUT, "fault-map.svg"), W, H, body,
           title="Кожна біда — на своїй адресі в спектрі")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — еталон і тренд (два панелі)
# ════════════════════════════════════════════════════════════════════════════
def fig_baseline_trend():
    W, H = 760, 420
    # --- верх: еталон vs поточний спектр ---
    x0, y0 = 70, 200
    w_ax, h_ax = 640, 130
    body = axes(x0, y0, w_ax, h_ax, "частота", "амплітуда")
    body += text(x0, 52, "Спектр: еталон vs поточний", size=12, color=INK, bold=True, anchor="start")

    def fx(mult): return x0 + (mult / 6.4) * w_ax
    base = {1: 0.9, 2: 0.3, 3: 0.16, 4: 0.1}
    for m, v in base.items():
        body += bar(fx(m) - 6, y0, v * h_ax, MUTED, w=9)        # еталон сірий
    for m, v in base.items():
        body += bar(fx(m) + 6, y0, v * h_ax, POS, w=9)          # поточний
    # новий пік підшипника, якого в еталоні нема
    body += bar(fx(3.6), y0, 0.55 * h_ax, POS, w=10)
    body += text(fx(3.6), y0 - 0.55 * h_ax - 8, "новий пік!", size=10, color=POS, bold=True)
    # легенда
    body += rect(x0 + 360, 40, 12, 12, fill=MUTED, stroke=MUTED, sw=1, rx=2)
    body += text(x0 + 377, 50, "еталон", size=10.5, color=INK, anchor="start")
    body += rect(x0 + 450, 40, 12, 12, fill=POS, stroke=POS, sw=1, rx=2)
    body += text(x0 + 467, 50, "поточний", size=10.5, color=INK, anchor="start")

    # --- низ: тренд піка в часі ---
    x1, y1 = 70, 388
    w2, h2 = 640, 120
    body += axes(x1, y1, w2, h2, "час (тижні)", "висота піка")
    body += text(x1, 244, "Тренд піка підшипника в часі", size=12, color=INK, bold=True, anchor="start")
    # абсолютний поріг
    thr = y1 - 0.82 * h2
    body += line(x1, thr, x1 + w2, thr, color=MUTED, sw=1.4, dash="6 5")
    body += text(x1 + w2, thr - 6, "абсолютний поріг", size=10, color=MUTED, anchor="end")
    # крива росту піка
    def grow(t):
        return 0.05 + 0.78 * (t ** 2.6)
    body += wave(x1, y1, w2, h2, grow, POS, n=120, sw=2.4)
    # точка раннього вияву
    ex = x1 + 0.55 * w2
    ey = y1 - grow(0.55) * h2
    body += circle(ex, ey, 5, fill=BG, stroke=FIELD, sw=2.4)
    body += text(ex - 8, ey - 10, "ловимо рано", size=10, color=FIELD, anchor="end", bold=True)

    render(os.path.join(OUT, "baseline-trend.svg"), W, H, body,
           title="Діагностика — це відхилення від власної норми")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — конвеєр аналізу обвідної (блок-схема ланок)
# ════════════════════════════════════════════════════════════════════════════
def fig_envelope_pipeline():
    W, H = 880, 250
    body = ""
    # п'ять ланок ланцюга + вхід/вихід
    stages = [
        ("вхід",            "сирий\nсигнал",              FILL,  MUTED),
        ("смуговий фільтр", "лишити смугу\nрезонансу",    "#eaf0fd", NEG),
        ("випрямлення",     "|x| модуль",                 "#fdecea", POS),
        ("ФНЧ",             "виділити\nобвідну",          "#eafaf0", FIELD),
        ("ШПФ обвідної",    "спектр\nобвідної",           FILL,  INK),
        ("вихід",           "пік на\nBPFO / BPFI",        "#eafaf0", FIELD),
    ]
    n = len(stages)
    bw, bh = 118, 70
    gap = (W - 24 - n * bw) / (n - 1)
    y = 96
    xs = []
    for i, (title, sub, fill, col) in enumerate(stages):
        x = 12 + i * (bw + gap)
        xs.append(x + bw / 2)
        body += rect(x, y, bw, bh, fill=fill, stroke=col, sw=2)
        body += text(x + bw / 2, y - 8, title, size=12, color=col, bold=True)
        body += mtext(x + bw / 2, y + bh / 2 - 4, sub, size=11, color=INK, lh=1.25)
        if i < n - 1:
            x2 = 12 + (i + 1) * (bw + gap)
            body += arrow(x + bw + 4, y + bh / 2, x2 - 4, y + bh / 2, color=INK, sw=2)
    # підписи знизу: що несе кожна стрілка
    notes = [
        (0, 1, "наскільки\nдзвенить корпус"),
        (1, 2, "лишився\nчистий дзвін"),
        (2, 3, "є низька\nскладова"),
        (3, 4, "сама\nобвідна"),
        (4, 5, "ритм\nударів"),
    ]
    for a, b, txt in notes:
        xm = (xs[a] + xs[b]) / 2
        body += mtext(xm, y + bh + 26, txt, size=9.5, color=MUTED, lh=1.2)
    # підпис ключової ідеї
    body += text(W / 2, 220, "демодуляція: випрямлення + ФНЧ переносять ритм ударів із кілогерців у одиниці-десятки герц",
                 size=11, color=INK, italic=True)
    render(os.path.join(OUT, "envelope-pipeline.svg"), W, H, body,
           title="Конвеєр аналізу обвідної на мікроконтролері")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 — чому випрямлення демодулює: сигнал у часі по ланках
# ════════════════════════════════════════════════════════════════════════════
def fig_demodulation():
    W, H = 760, 500
    x0 = 70
    w_ax = 640
    rate = 4.0          # «BPFO»: 4 удари за вікно
    carrier = 34.0      # високочастотний «дзвін»

    def burst_env(t):
        # обвідна: гострий сплеск на кожен удар, що швидко гасне
        v = 0.0
        for k in range(int(rate) + 1):
            tk = (k + 0.18) / rate
            d = t - tk
            if d >= 0:
                v = max(v, math.exp(-d * rate * 7.0))
        return v

    def ring(t):        # смуговий сигнал: дзвін, модульований сплесками
        return burst_env(t) * math.sin(2 * math.pi * carrier * t)

    panels = [
        ("Після смугового фільтра: спалахи дзвону", lambda t: ring(t), INK, False),
        ("Після випрямлення: |сигнал|",            lambda t: abs(ring(t)), POS, False),
        ("Після ФНЧ: обвідна (видно ритм ударів)",  burst_env, FIELD, True),
    ]
    ph = 120
    gap = 22
    yb = 60
    for idx, (title, fn, col, mark) in enumerate(panels):
        y0 = yb + idx * (ph + gap) + ph
        body_local = axes(x0, y0, w_ax, ph - 14, "час", "")
        body_local += text(x0, y0 - ph + 2, title, size=12, color=col, bold=True, anchor="start")
        if idx == 1:
            # для |x| малюємо тільки додатню частину від базової лінії
            body_local += wave(x0, y0, w_ax, ph - 22, fn, col, n=480, sw=1.5)
        elif idx == 0:
            # дзвін гойдається навколо середини панелі
            ymid = y0 - (ph - 14) / 2
            body_local += line(x0, ymid, x0 + w_ax, ymid, color=MUTED, sw=0.8, dash="3 4")
            body_local += wave(x0, ymid, w_ax, (ph - 22) / 2, fn, col, n=600, sw=1.3)
        else:
            body_local += wave(x0, y0, w_ax, ph - 22, fn, col, n=480, sw=2.4)
            # відмітити період між сплесками
            t1 = (0 + 0.18) / rate
            t2 = (1 + 0.18) / rate
            xa = x0 + t1 * w_ax
            xb = x0 + t2 * w_ax
            ytop = y0 - (ph - 22)
            body_local += line(xa, ytop - 6, xb, ytop - 6, color=INK, sw=1.4)
            body_local += line(xa, ytop - 10, xa, ytop - 2, color=INK, sw=1.4)
            body_local += line(xb, ytop - 10, xb, ytop - 2, color=INK, sw=1.4)
            body_local += text((xa + xb) / 2, ytop - 11, "період = 1/BPFO", size=10, color=INK)
        if idx == 0:
            globals()['_demo_body'] = body_local
        else:
            globals()['_demo_body'] += body_local
    render(os.path.join(OUT, "demodulation.svg"), W, H, globals()['_demo_body'],
           title="Випрямлення породжує обвідну з ритмом дефекту")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 6 — прямий спектр vs спектр обвідної
# ════════════════════════════════════════════════════════════════════════════
def fig_envelope_spectrum():
    W, H = 760, 420
    # --- верх: прямий спектр прискорення ---
    x0, y0 = 70, 196
    w_ax, h_ax = 640, 128
    body = axes(x0, y0, w_ax, h_ax, "частота (кГц)", "амплітуда")
    body += text(x0, 50, "Прямий спектр прискорення: пік BPFO тоне в шумі", size=12, color=INK, bold=True, anchor="start")
    # шумова підлога
    fn = smooth_noise(2)
    body += wave(x0, y0, w_ax, h_ax * 0.34, lambda t: 0.5 + 0.5 * fn(t), MUTED, n=320, sw=1.1)
    # широкий горб резонансу високо по частоті
    def hump(t):
        return 0.62 * math.exp(-((t - 0.72) ** 2) / (2 * 0.05 ** 2))
    body += wave(x0, y0, w_ax, h_ax, hump, NEG, n=320, sw=2.0)
    body += text(x0 + 0.72 * w_ax, y0 - hump(0.72) * h_ax - 8, "резонанс корпусу (≈ кГц)", size=10, color=NEG)
    # ледь помітний BPFO низько
    body += bar(x0 + 0.05 * w_ax, y0, 0.20 * h_ax, MUTED, w=6)
    body += text(x0 + 0.05 * w_ax + 4, y0 - 0.20 * h_ax - 6, "BPFO?", size=10, color=MUTED, anchor="start")

    # --- низ: спектр обвідної ---
    x1, y1 = 70, 392
    w2, h2 = 640, 128
    body += axes(x1, y1, w2, h2, "частота (Гц)", "амплітуда")
    body += text(x1, 240, "Спектр обвідної: чистий пік BPFO та його гармоніки", size=12, color=INK, bold=True, anchor="start")
    body += wave(x1, y1, w2, h2 * 0.16, lambda t: 0.5 + 0.5 * smooth_noise(5)(t), MUTED, n=320, sw=1.0)
    # піки на BPFO, 2×, 3×
    peaks = [(0.14, 0.92, "BPFO"), (0.28, 0.55, "2×"), (0.42, 0.34, "3×")]
    for pos, val, lbl in peaks:
        xc = x1 + pos * w2
        body += bar(xc, y1, val * h2, POS, w=9)
        body += text(xc, y1 - val * h2 - 7, lbl, size=10.5, color=POS, bold=True)
    render(os.path.join(OUT, "envelope-spectrum.svg"), W, H, body,
           title="Те, чого прямий спектр не бачить, обвідна показує чисто")


# ════════════════════════════════════════════════════════════════════════════
# Фігура (вставка hist) — три епохи обслуговування + родовід приладів/стандарту
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_timeline():
    W, H = 820, 470
    xL, xR = 70, 760            # межі осі часу
    y_axis = 250               # сама лінія часу

    # рік → x (1935..2022)
    Y0, Y1 = 1935.0, 2022.0
    def fx(year):
        return xL + (year - Y0) / (Y1 - Y0) * (xR - xL)

    body = ""

    # ── вісь часу з десятиліттями ──
    body += line(xL, y_axis, xR, y_axis, color=INK, sw=2.0)
    body += text(xR + 4, y_axis + 4, "рік", size=11, color=MUTED, anchor="start")
    for yr in [1940, 1960, 1970, 1980, 1990, 2000, 2010, 2020]:
        body += line(fx(yr), y_axis - 4, fx(yr), y_axis + 4, color=MUTED, sw=1.2)
        body += text(fx(yr), y_axis + 19, str(yr), size=9.5, color=MUTED)

    # ── ВЕРХ: три епохи способу думати (смуги) ──
    band_y = 96
    band_h = 26
    eras = [
        (1935, 1960, "до поломки (run-to-failure)", MUTED),
        (1960, 1978, "за графіком (preventive)",     NEG),
        (1978, 2022, "за станом (predictive)",        FIELD),
    ]
    body += text(xL, band_y - 12, "Спосіб думати про поломку", size=12, color=INK,
                 bold=True, anchor="start")
    for a, b, lbl, col in eras:
        xa, xb = fx(a), fx(b)
        body += rect(xa, band_y, xb - xa, band_h, fill=col, stroke=col, sw=1, rx=4)
        body += fitbox(xa + 2, band_y + 2, xb - xa - 4, band_h - 4, lbl,
                       size=11, color=BG, bold=True, fill="none", stroke="none", pad=3)

    # перелам: звіт Ноулена й Гіпа 1978
    xp = fx(1978)
    body += line(xp, band_y + band_h, xp, y_axis, color=POS, sw=1.6, dash="4 4")
    box, bw, bh = textbox(xp, band_y + band_h + 34,
                          ["перелам: Ноулен і Гіп, 1978", "«більшість відмов — випадкові»"],
                          size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.4)
    body += box

    # ── НИЗ: родовід шкали важкості (віхи під віссю) ──
    body += text(xL, y_axis + 52, "Шкала важкості вібрації (мм/с)", size=11.5,
                 color=INK, bold=True, anchor="start")
    scale_pts = [
        (1939, "Ратбоун\nперша шкала", -1),
        (1964, "VDI 2056", 1),
        (1974, "ISO 2372", -1),
        (1995, "ISO 10816", 1),
        (2016, "ISO 20816\n(злиття 7919)", -1),
    ]
    sy = y_axis + 74
    prev_x = None
    for yr, lbl, side in scale_pts:
        x = fx(yr)
        if prev_x is not None:
            body += line(prev_x, y_axis, x, y_axis, color=NEG, sw=2.6)
        prev_x = x
    for yr, lbl, side in scale_pts:
        x = fx(yr)
        body += circle(x, y_axis, 4, fill=NEG, stroke=NEG, sw=1)
        ty = sy + (0 if side < 0 else 34)
        body += line(x, y_axis + 6, x, ty - (18 if "\n" in lbl else 9),
                     color=MUTED, sw=0.8, dash="2 3")
        body += mtext(x, ty, lbl, size=9, color=INK)

    # ── НИЗ-2: прориви техніки й обчислення (над віссю, окремий ряд) ──
    # три віхи 1965/1969/1974 тісно стоять — розводимо підписи по висоті й убік,
    # щоб не накладались (короткі носки-лінії від точки до напису).
    # (Підпис кольорів — у легенді внизу; окремий заголовок ряду зайвий.)
    tech = [
        (1965, "ШПФ (Кулі–Тʼюкі)",   POS,   -52, -78),   # лівіше й вище
        (1969, "ударні імпульси",     MUTED,  64, -64),   # правіше, середній рівень
        (1974, "аналіз обвідної (HFRT)", FIELD, 18, -36), # нижче, ближче до осі
    ]
    for yr, lbl, col, dx, dy in tech:
        x = fx(yr)
        lx, ly_lbl = x + dx, y_axis + dy
        body += circle(x, y_axis, 4, fill=col, stroke=col, sw=1)
        body += line(x, y_axis - 6, lx, ly_lbl + 4, color=MUTED, sw=0.8, dash="2 3")
        anch = "end" if dx < 0 else "start"
        body += text(lx, ly_lbl, lbl, size=9.5, color=col, bold=True, anchor=anch)

    # легенда внизу
    ly = H - 16
    body += circle(xL + 6, ly - 4, 4, fill=NEG, stroke=NEG, sw=1)
    body += text(xL + 16, ly, "стандарт важкості", size=9.5, color=INK, anchor="start")
    body += circle(xL + 180, ly - 4, 4, fill=FIELD, stroke=FIELD, sw=1)
    body += text(xL + 190, ly, "техніка діагностики", size=9.5, color=INK, anchor="start")
    body += circle(xL + 360, ly - 4, 4, fill=POS, stroke=POS, sw=1)
    body += text(xL + 370, ly, "обчислювальна основа", size=9.5, color=INK, anchor="start")

    render(os.path.join(OUT, "maintenance-timeline.svg"), W, H, body,
           title="Дорога до передбачення: епохи, прилади, стандарт")


# ════════════════════════════════════════════════════════════════════════════
# Запуск
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_three_quantities()
    fig_fault_map()
    fig_baseline_trend()
    fig_envelope_pipeline()
    fig_demodulation()
    fig_envelope_spectrum()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
