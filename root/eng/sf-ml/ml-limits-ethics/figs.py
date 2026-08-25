# -*- coding: utf-8 -*-
"""Фігури до теми «Межі й етика машинного навчання»."""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


def ellipse(cx, cy, rx, ry, fill, stroke, sw=1.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


# ── Фігура 1: гарантія тримається лише всередині хмари навчальних даних ──────
def fig_outside_the_cloud():
    W, H = 780, 400
    f = [text(W / 2, 28, "Гарантія тримається лише всередині баченого", size=17, bold=True)]

    # рамка простору ознак
    f.append(rect(50, 56, 430, 300, fill="#fcfcfd", stroke="#d5d9e0", sw=1.2))

    # хмара навчальних прикладів
    ecx, ecy, erx, ery = 262, 190, 152, 100
    f.append(ellipse(ecx, ecy, erx, ery, "#eef2ff", NEG, sw=1.6, dash="7 5"))

    rnd = random.Random(7)
    for _ in range(26):
        while True:
            dx = rnd.uniform(-1, 1)
            dy = rnd.uniform(-1, 1)
            if dx * dx + dy * dy <= 0.82:
                break
        f.append(circle(ecx + dx * erx, ecy + dy * ery, 4.2, fill=NEG, stroke=NEG, sw=1))

    # приклади поза хмарою
    for (px, py) in [(108, 104), (438, 292), (118, 300)]:
        f.append(circle(px, py, 5.6, fill="#fdecea", stroke=POS, sw=2.2))

    # межа рішення: суцільна там, де є дані, штрихова — там, де їх не було
    def on_curve(t):
        x = 78 + t * 380
        y = 322 - 250 * t + 90 * math.sin(t * 2.6)
        return (x, y)

    def inside(p):
        return ((p[0] - ecx) / erx) ** 2 + ((p[1] - ecy) / ery) ** 2 <= 1.0

    run, state = [], None
    for i in range(81):
        p = on_curve(i / 80.0)
        st = inside(p)
        if state is None:
            state = st
        if st != state:
            f.append(polyline(run + [p], color=INK, sw=2.2, dash=None if state else "6 5"))
            run, state = [p], st
        run.append(p)
    if len(run) > 1:
        f.append(polyline(run, color=INK, sw=2.2, dash=None if state else "6 5"))

    f.append(text(262, 336, "хмара навчальних прикладів", size=12, color=MUTED))
    f.append(text(400, 96, "межа рішення", size=11, color=MUTED))

    # правий стовпчик — два висновки
    f.append(fitbox(508, 76, 232, 92,
                    ["Усередині хмари:", "похибка на нових прикладах",
                     "близька до тестової"], size=12, bold=False,
                    fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(508, 196, 232, 122,
                    ["Поза нею:", "модель рахує ту саму функцію", "й повертає високу впевненість",
                      "— бо шкалу впевненості", "підганяли там-таки"], size=12,
                    fill="#fdecea", stroke=POS))

    # легенда
    f.append(circle(62, 374, 4.2, fill=NEG, stroke=NEG, sw=1))
    f.append(text(74, 378, "навчальний приклад", size=11, color=MUTED, anchor="start"))
    f.append(circle(266, 374, 5.6, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(280, 378, "вхід, якого модель не бачила", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'outside-the-cloud.svg'), W, H, *f)


# ── Фігура 2: оптимізація бере дешевшу ознаку, а не причину ─────────────────
def fig_cheapest_feature():
    W, H = 780, 420
    f = [text(W / 2, 28, "Дешевша ознака ділить зібрані дані не гірше за причину", size=17, bold=True)]

    f.append(text(210, 66, "Навчальні дані", size=13, bold=True))
    rows = [("вовк", "сніг", "#e8f0ff", NEG), ("хаскі", "трава", "#e9f7ec", FIELD)]
    for r, (animal, bg, fill, stroke) in enumerate(rows):
        cy = 108 + r * 74
        f.append(text(112, cy + 4, animal, size=12, bold=True, anchor="end"))
        for c in range(3):
            cx = 155 + c * 85
            f.append(rect(cx - 37, cy - 26, 74, 52, fill=fill, stroke=stroke, sw=1.4))
            f.append(text(cx, cy + 4, bg, size=11, color=MUTED))

    f.append(fitbox(58, 236, 306, 74,
                    ["«сніг» і «вовк» тут — те саме:", "обидві ознаки ділять приклади",
                     "бездоганно, вибрати нема з чого"], size=12,
                    fill="#f7f8fa", stroke="#c9ccd3"))

    f.append(line(396, 62, 396, 316, color="#d5d9e0", sw=1.2))

    f.append(text(590, 66, "Новий приклад", size=13, bold=True))
    f.append(rect(540, 86, 100, 54, fill="#e8f0ff", stroke=NEG, sw=1.4))
    f.append(text(590, 117, "сніг", size=11, color=MUTED))
    f.append(text(590, 160, "хаскі — але на снігу", size=12))
    f.append(arrow(590, 172, 590, 196, color=POS, sw=2))
    box, _, _ = textbox(590, 216, "модель: «вовк»", size=13, pad=10,
                        fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(box)

    f.append(fitbox(436, 250, 306, 66,
                    ["ознаки розійшлися вперше —", "і відповідь дала та з них,",
                     "яку було дешевше знайти"], size=12,
                    fill="#f7f8fa", stroke="#c9ccd3"))

    f.append(fitbox(58, 340, 684, 54,
                    ["На тестовому наборі, зібраному тим самим способом, супутник теж збігається з міткою —",
                     "тож метрика лишається високою і про підміну не повідомляє"], size=13,
                    fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'cheapest-feature.svg'), W, H, *f)


# ── Фігура 3: число дає модель, поріг ставить людина ────────────────────────
def fig_threshold_and_cost():
    W, H = 780, 400
    f = [text(W / 2, 28, "Число дає модель — поріг ставить той, хто платить за помилку", size=17, bold=True)]

    base = 300.0
    x0, x1 = 70.0, 520.0
    thr = 300.0

    def bell(cx, sigma, amp, x):
        return base - amp * math.exp(-((x - cx) ** 2) / (2.0 * sigma * sigma))

    curves = [(196.0, 52.0, 148.0, NEG, "#eef2ff"), (382.0, 52.0, 148.0, POS, "#fdecea")]

    # заливка «хвостів» за порогом
    for (cx, sg, amp, col, fill) in curves:
        if cx < thr:
            xs = [x for x in range(int(thr), int(x1) + 1, 3)]
        else:
            xs = [x for x in range(int(x0), int(thr) + 1, 3)]
        if len(xs) > 1:
            pts = ["%.1f,%.1f" % (x, bell(cx, sg, amp, x)) for x in xs]
            d = "M %.1f,%.1f L " % (xs[0], base) + " L ".join(pts) + " L %.1f,%.1f Z" % (xs[-1], base)
            f.append('<path d="%s" fill="%s" stroke="none" opacity="0.85"/>' % (d, fill))

    for (cx, sg, amp, col, fill) in curves:
        pts = [(x, bell(cx, sg, amp, x)) for x in range(int(x0), int(x1) + 1, 3)]
        f.append(polyline(pts, color=col, sw=2.2))

    f.append(line(x0, base, x1, base, color=LINE, sw=1.5))
    f.append(line(thr, 108, thr, 306, color=INK, sw=2.0, dash="6 4"))
    f.append(text(thr, 98, "поріг", size=12, bold=True))

    f.append(text(196, 138, "без події", size=12, color=NEG))
    f.append(text(382, 138, "з подією", size=12, color=POS))
    f.append(text(238, 326, "пропуски", size=12, color=MUTED))
    f.append(text(374, 326, "хибні тривоги", size=12, color=MUTED))
    f.append(text(x1 + 4, 322, "оцінка моделі →", size=11, color=MUTED, anchor="end"))

    f.append(fitbox(548, 76, 216, 92,
                    ["Поріг не є властивістю", "моделі: вона дає лише", "число. Де його різати —",
                     "питання ціни помилки."], size=12, fill="#f7f8fa", stroke="#c9ccd3"))
    f.append(fitbox(548, 196, 216, 116,
                    ["У фотоальбомі дорожча", "хибна тривога.", "У сортуванні пацієнтів —",
                     "пропуск. Модель та сама,", "поріг — різний."], size=12,
                    fill="#eef7f0", stroke=FIELD))

    f.append(fitbox(70, 348, 450, 44,
                    ["Що рідкісніша подія, то більша частка тривог хибна", "навіть за бездоганної моделі"],
                    size=12, fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'threshold-and-cost.svg'), W, H, *f)


# ── Фігура 4 (вставка proj): точкова оцінка зрізу проти нижньої межі ─────────
def fig_slice_ranking():
    W, H = 940, 500
    f = [text(W / 2, 30, "Точкова оцінка ставить зрізи в один ряд, нижня межа — в інший",
              size=17, bold=True)]

    # логарифмічна вісь часток хибних тривог: 1% … 40%
    LO, HI = 1.0, 40.0
    x0, x1 = 250.0, 700.0

    def X(v):
        return x0 + (math.log10(v) - math.log10(LO)) / (math.log10(HI) - math.log10(LO)) * (x1 - x0)

    rows = [
        # назва,      частка %, нижня %, верхня %, встановлено
        ("камера B · ніч",   8.51, 1.97, 30.10, False),
        ("камера C · ніч",   6.67, 2.92, 14.51, True),
        ("камера C · день",  4.21, 2.81,  6.26, True),
        ("камера A · ніч",   3.10, 2.24,  4.27, False),
        ("камера A · день",  2.32, 1.92,  2.80, False),
    ]
    counts = ["47 без події", "210 без події", "1450 без події",
              "3100 без події", "12 400 без події"]

    top = 128.0
    step = 56.0
    bot = top + step * (len(rows) - 1)

    # сітка й підписи осі
    f.append(text((x0 + x1) / 2, 62, "частка хибних тривог (логарифмічна вісь)",
                  size=12, color=MUTED))
    for v in (1, 2, 5, 10, 20, 40):
        f.append(line(X(v), 98, X(v), bot + 18, color="#e3e6ea", sw=1.0))
        f.append(text(X(v), 88, "%d%%" % v, size=11, color=MUTED))

    # загальний рівень
    f.append(line(X(2.5), 98, X(2.5), bot + 22, color=INK, sw=2.0, dash="6 4"))
    f.append(text(X(2.5), bot + 40, "загальний рівень 2.5%", size=12, bold=True))

    for i, (name, p, lo, hi, ok) in enumerate(rows):
        cy = top + i * step
        f.append(text(238, cy + 2, name, size=13, anchor="end", bold=True))
        f.append(text(238, cy + 20, counts[i], size=11, color=MUTED, anchor="end"))
        col = FIELD if ok else POS
        f.append(line(X(lo), cy, X(hi), cy, color=col, sw=6.0))
        f.append(line(X(lo), cy - 9, X(lo), cy + 9, color=col, sw=2.4))
        f.append(line(X(hi), cy - 9, X(hi), cy + 9, color=col, sw=2.4))
        f.append(circle(X(p), cy, 5.4, fill=BG, stroke=INK, sw=2.4))
        f.append(text(730, cy + 4, "гірше" if ok else "не видно",
                      size=13, color=col, bold=True, anchor="start"))

    f.append(fitbox(60, 410, 820, 46,
                    ["Праворуч від рядка — чи ВЕСЬ інтервал лежить вище загального рівня,",
                     "з поправкою на те, що зрізів переглянули сорок"],
                    size=13, fill="#f7f8fa", stroke="#c9ccd3"))

    f.append(circle(70, 478, 5.4, fill=BG, stroke=INK, sw=2.4))
    f.append(text(84, 482, "точкова оцінка", size=11, color=MUTED, anchor="start"))
    f.append(line(232, 478, 292, 478, color=MUTED, sw=6.0))
    f.append(text(304, 482, "інтервал Вілсона", size=11, color=MUTED, anchor="start"))
    f.append(text(452, 482, "вужчий інтервал = більший зріз", size=11,
                  color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'slice-ranking.svg'), W, H, *f)


# ── Фігура 5 (вставка proj): шумова підлога PSI проти сталих порогів ─────────
def fig_psi_noise_floor():
    W, H = 900, 470
    f = [text(W / 2, 30, "Стала межа PSI правильна рівно при одному розмірі вікна",
              size=17, bold=True)]

    N_TRAIN, B, Z = 20000.0, 10.0, 1.6449
    x0, x1 = 108.0, 618.0
    y0, y1 = 88.0, 356.0
    MLO, MHI = 100.0, 20000.0
    VLO, VHI = 0.0008, 0.5

    def X(m):
        return x0 + (math.log10(m) - math.log10(MLO)) / (math.log10(MHI) - math.log10(MLO)) * (x1 - x0)

    def Y(v):
        return y1 - (math.log10(v) - math.log10(VLO)) / (math.log10(VHI) - math.log10(VLO)) * (y1 - y0)

    def floor_(m):
        return (1.0 / N_TRAIN + 1.0 / m) * (B - 1.0)

    def thr(m):
        return (1.0 / N_TRAIN + 1.0 / m) * (B - 1.0 + Z * math.sqrt(2.0 * (B - 1.0)))

    # сітка
    for v in (0.001, 0.003, 0.01, 0.03, 0.1, 0.3):
        f.append(line(x0, Y(v), x1, Y(v), color="#e3e6ea", sw=1.0))
        f.append(text(x0 - 10, Y(v) + 4, ("%g" % v), size=11, color=MUTED, anchor="end"))
    for m in (100, 300, 1000, 3000, 10000, 20000):
        f.append(line(X(m), y0, X(m), y1, color="#eef0f3", sw=1.0))
        f.append(text(X(m), y1 + 20, str(m), size=11, color=MUTED))

    f.append(line(x0, y0, x0, y1, color=LINE, sw=1.4))
    f.append(line(x0, y1, x1, y1, color=LINE, sw=1.4))
    f.append(text((x0 + x1) / 2, y1 + 44, "розмір робочого вікна m (вибірка навчання — 20 000)",
                  size=12, color=MUTED))
    f.append(text(x0 - 62, (y0 + y1) / 2, "PSI", size=12, color=MUTED))

    ms = [MLO * (MHI / MLO) ** (i / 90.0) for i in range(91)]

    # сталі межі-повір'я
    for v, lbl in ((0.10, "0.10"), (0.25, "0.25")):
        f.append(line(x0, Y(v), x1, Y(v), color="#c9a227", sw=2.0, dash="7 5"))
        f.append(text(x1 + 8, Y(v) + 4, lbl, size=12, color="#9a7c1d",
                      bold=True, anchor="start"))

    f.append(polyline([(X(m), Y(floor_(m))) for m in ms], color=MUTED, sw=2.2, dash="5 4"))
    f.append(polyline([(X(m), Y(thr(m))) for m in ms], color=POS, sw=2.6))

    # точка, де чесна межа перетинає 0.10
    mc = 1.0 / (0.10 / (B - 1.0 + Z * math.sqrt(2.0 * (B - 1.0))) - 1.0 / N_TRAIN)
    f.append(circle(X(mc), Y(0.10), 5.4, fill=BG, stroke=INK, sw=2.4))
    f.append(text(X(mc) + 10, Y(0.10) - 12, "m ≈ %d" % int(round(mc)),
                  size=12, bold=True, anchor="start"))

    f.append(text(X(150), Y(floor_(150)) - 14, "шумова підлога", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(X(1600), Y(thr(1600)) + 22, "чесна межа тривоги (α = 0.05)",
                  size=12, color=POS, anchor="start"))

    f.append(fitbox(650, 88, 234, 106,
                    ["Ліворуч від точки:", "сталий поріг 0.10 нижчий", "за сам шум —",
                     "тривога на порожньому місці"], size=11,
                    fill="#fdecea", stroke=POS))
    f.append(fitbox(650, 208, 234, 106,
                    ["Праворуч: чесна межа", "падає з ростом вікна,", "а 0.10 стоїть —",
                     "справжній зсув проходить"], size=11,
                    fill="#eef7f0", stroke=FIELD))

    f.append(fitbox(108, 398, 776, 50,
                    ["PSI ≈ (1/n + 1/m)·χ²(B−1): і середнє, і розкид спадають із розміром вибірок,",
                     "тож одне й те саме число означає різні речі на вікні в 100 і в 10 000 записів"],
                    size=13, fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'psi-noise-floor.svg'), W, H, *f)


# ── Фігура (вставка hist): як здогад перетворився на переказ ────────────────
def fig_legend_timeline():
    W, H = 980, 430
    f = [text(W / 2, 30, "Як здогад зі знаком питання став переказом із крапкою",
              size=17, bold=True)]

    boxes = [
        ("початок 1960-х", ["Едвард Фредкін на", "конференції в Лос-",
                            "Анджелесі припускає:", "а раптом мережа ловить",
                            "яскравість знімка?"], "#eef2ff", NEG),
        ("тоді ж", ["Армію влаштовує", "результат, роботу",
                    "засекречують.", "Здогад не перевіряє", "ніхто."],
         "#f7f8fa", "#c9ccd3"),
        ("1991–92", ["Перші знайдені", "розповіді: серія BBC",
                     "і стаття Дрейфусів.", "Джерел не названо."],
         "#fff8e1", "#c9a227"),
        ("1998 і далі", ["Вебверсія: 200 знімків,", "показ у Пентагоні,",
                         "хмарний і сонячний", "день. Знак питання", "зник."],
         "#fdecea", POS),
    ]

    xs = [24, 268, 512, 756]
    for i, (year, lines, fill, stroke) in enumerate(boxes):
        x = xs[i]
        f.append(text(x + 100, 62, year, size=12, bold=True, color=MUTED))
        f.append(fitbox(x, 76, 200, 152, lines, size=12, fill=fill, stroke=stroke))
        if i < 3:
            f.append(arrow(x + 206, 152, x + 238, 152, color=MUTED, sw=1.8))

    f.append(text(120, 252, "здогад зі знаком питання", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(490, 252, "≈ 30 років переказування", size=12, color=MUTED))
    f.append(text(860, 252, "переказ із крапкою", size=12,
                  color=MUTED, anchor="end"))
    f.append(arrow(120, 270, 860, 270, color="#c9ccd3", sw=1.6))

    f.append(fitbox(24, 300, 932, 104,
                    ["Що справді робили: Лавін Канал і Ніл Рендолл (Philco-Ford, 1962–63) розпізнавали",
                     "танки на аерознімках. Фрагменти вирізали з одного високо знятого кадру — той самий",
                     "день, та сама плівка, те саме світло, а яскравість прибирали лапласіаном.",
                     "Описаної пастки в тих даних статися не могло."],
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'legend-timeline.svg'), W, H, *f)


# ── Фігура (вставка hist): чотири щаблі доказу ──────────────────────────────
def fig_evidence_ladder():
    W, H = 900, 470
    f = [text(W / 2, 30, "Чотири щаблі доказу: чим випадок відрізняється від переказу",
              size=17, bold=True)]

    rows = [
        (58, "Втручання",
         "підозрювану ознаку прибирають і додають — відповідь іде за нею",
         "водяний знак на знімках коней, Nature Communications, 2019",
         "#eef7f0", FIELD),
        (152, "Опублікований дослід",
         "описано, як зібрано дані й що виміряно; можна повторити",
         "хаскі, вовки і сніг, KDD 2016; рентгени трьох лікарень, 2018",
         "#eef2ff", NEG),
        (246, "Журналістський звіт",
         "названі видання й автор, джерела анонімні; повторити не можна",
         "інструмент добору кандидатів Amazon, Reuters, 2018",
         "#fff8e1", "#c9a227"),
        (340, "Переказ",
         "немає першоджерела; кожен переповідач змінює подробиці",
         "танки, що ловили погоду",
         "#fdecea", POS),
    ]

    for (y, name, desc, ex, fill, stroke) in rows:
        f.append(rect(150, y, 726, 84, fill=fill, stroke=stroke, sw=1.5))
        f.append(text(166, y + 46, name, size=13, bold=True, anchor="start"))
        f.append(text(396, y + 34, desc, size=12, anchor="start"))
        f.append(text(396, y + 62, ex, size=12, color=MUTED, anchor="start"))

    f.append(arrow(112, 424, 112, 58, color=MUTED, sw=1.8))
    f.append(text(60, 70, "сильніше", size=11, color=MUTED))
    f.append(text(60, 418, "слабше", size=11, color=MUTED))

    f.append(text(W / 2, 450,
                  "Що вище щабель, то менше лишається місця для «а може, було не так»",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'evidence-ladder.svg'), W, H, *f)


# ── Вставка math: базова частота — 99 справжніх тривог проти 999 хибних ─────
def fig_base_rate_tree():
    W, H = 830, 470
    f = [text(W / 2, 28, "Рідкісна подія: 99% на кожному класі дають 9% справджень",
              size=17, bold=True)]

    f.append(fitbox(315, 46, 200, 46, ["100 000 людей", "подія у 1 з 1000"], size=13))

    f.append(line(415, 92, 235, 132, color=LINE, sw=1.4))
    f.append(line(415, 92, 595, 132, color=LINE, sw=1.4))
    f.append(fitbox(120, 132, 230, 48, ["подія є: 100"], size=15,
                    fill="#fdecea", stroke=POS))
    f.append(fitbox(480, 132, 230, 48, ["події нема: 99 900"], size=15,
                    fill="#eef2ff", stroke=NEG))

    f.append(line(235, 180, 124, 222, color=LINE, sw=1.2))
    f.append(line(235, 180, 316, 222, color=LINE, sw=1.2))
    f.append(line(595, 180, 512, 222, color=LINE, sw=1.2))
    f.append(line(595, 180, 706, 222, color=LINE, sw=1.2))

    leaves = [
        (36,  ["TP = 99", "виявлено"],           "#e9f7ec", FIELD),
        (228, ["FN = 1", "пропущено"],           "#f7f8fa", "#c9ccd3"),
        (424, ["FP = 999", "хибних тривог"],     "#fdecea", POS),
        (618, ["TN = 98 901", "правильна мовчанка"], "#f7f8fa", "#c9ccd3"),
    ]
    for (lx, lines, fill, stroke) in leaves:
        f.append(fitbox(lx, 222, 176, 66, lines, size=14, fill=fill, stroke=stroke))

    f.append(text(415, 324, "усі тривоги: 99 + 999 = 1098", size=14, bold=True))
    f.append(rect(60, 336, 64, 30, fill="#e9f7ec", stroke=FIELD, sw=1.6, rx=3))
    f.append(rect(124, 336, 646, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    f.append(text(92, 392, "99 справжніх", size=12, color=FIELD))
    f.append(text(447, 392, "999 хибних — 91% усіх тривог", size=12, color=POS))

    f.append(fitbox(60, 408, 710, 46,
                    ["PPV = 99 / 1098 ≈ 9%  —  на кожну справжню тривогу дев'ять хибних"],
                    size=14, fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'base-rate-tree.svg'), W, H, *f)


# ── Вставка math: поріг найменших втрат — дотик прямої нахилу m до кривої ────
def fig_iso_cost_roc():
    W, H = 820, 460
    f = [text(W / 2, 28, "Найдешевший поріг: де пряма однакових втрат торкається кривої",
              size=17, bold=True)]

    X0, Y0, XMAX = 90.0, 400.0, 0.7
    KX, KY = 360.0 / XMAX, 330.0

    def sx(v):
        return X0 + v * KX

    def sy(v):
        return Y0 - v * KY

    f.append(line(X0, Y0, 462, Y0, color=LINE, sw=1.5))
    f.append(line(X0, Y0, X0, 62, color=LINE, sw=1.5))
    for v in (0.0, 0.2, 0.4, 0.6):
        f.append(line(sx(v), Y0, sx(v), Y0 + 5, color=LINE, sw=1.2))
        f.append(text(sx(v), Y0 + 20, "%.1f" % v, size=11, color=MUTED))
    for v in (0.0, 0.5, 1.0):
        f.append(line(X0 - 5, sy(v), X0, sy(v), color=LINE, sw=1.2))
        f.append(text(X0 - 10, sy(v) + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    f.append(text(96, 54, "чутливість TPR", size=12, color=MUTED, anchor="start"))
    f.append(text(275, 438, "FPR — хибні тривоги серед спокійних →", size=12, color=MUTED))

    pts = [(0.0, 0.0), (0.005, 0.30), (0.02, 0.55), (0.08, 0.80),
           (0.22, 0.93), (0.45, 0.98), (0.65, 0.995), (0.70, 0.997)]
    f.append(polyline([(sx(a), sy(b)) for (a, b) in pts], color=INK, sw=2.4))
    for (a, b) in pts[1:-1]:
        f.append(circle(sx(a), sy(b), 3.2, fill=BG, stroke=INK, sw=1.4))

    def cost_line(m, fpr0, tpr0, color):
        k = m * KY / KX
        x_top = sx(fpr0) + (sy(tpr0) - 70.0) / k
        p2 = (x_top, 70.0) if x_top <= 462 else (462.0, sy(tpr0) - k * (462.0 - sx(fpr0)))
        y_left = sy(tpr0) + k * (sx(fpr0) - X0)
        p1 = (X0, y_left) if y_left <= Y0 else (sx(fpr0) - (Y0 - sy(tpr0)) / k, Y0)
        return polyline([p1, p2], color=color, sw=2.0)

    f.append(cost_line(0.245, 0.22, 0.93, POS))
    f.append(cost_line(9.8, 0.02, 0.55, NEG))

    f.append(circle(sx(0.22), sy(0.93), 6.0, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(circle(sx(0.02), sy(0.55), 6.0, fill="#eef2ff", stroke=NEG, sw=2.4))

    f.append(line(205, 99, 243, 119, color=MUTED, sw=1.0))
    b1, _, _ = textbox(287, 132, "поріг 0.15 · m = 0.245", size=12, pad=9,
                       fill="#fdecea", stroke=POS, color=POS)
    f.append(b1)
    f.append(line(107, 222, 158, 232, color=MUTED, sw=1.0))
    b2, _, _ = textbox(238, 240, "поріг 0.70 · m = 9.8", size=12, pad=9,
                       fill="#eef2ff", stroke=NEG, color=NEG)
    f.append(b2)

    f.append(arrow(340, 236, 292, 198, color=MUTED, sw=1.6))
    f.append(text(348, 262, "втрати спадають", size=12, color=MUTED))

    f.append(fitbox(480, 62, 310, 76,
                    ["Прямі однакових втрат мають нахил",
                     "m = c_трив·(1 − p) / ( c_проп·p )"], size=13))
    f.append(fitbox(480, 154, 310, 92,
                    ["Пропуск коштує 200 тривог:", "m = 0.245 — пряма полога,",
                     "дотик далеко праворуч,", "найдешевший поріг 0.15"],
                    size=13, fill="#fdecea", stroke=POS))
    f.append(fitbox(480, 262, 310, 92,
                    ["Пропуск коштує 5 тривог:", "m = 9.8 — пряма крута,",
                     "дотик біля початку,", "найдешевший поріг 0.70"],
                    size=13, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(480, 370, 310, 68,
                    ["Крива та сама, дані ті самі.", "Точку дотику рухає лише",
                     "відношення цін і базова частота."],
                    size=13, fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'iso-cost-roc.svg'), W, H, *f)


# ── Вставка math: тотожність між p, PPV, FPR і FNR на двох групах ────────────
def fig_parity_identity():
    W, H = 830, 430
    f = [text(W / 2, 28, "Тотожність зв'язує чотири числа: вільні лише три",
              size=17, bold=True)]

    blocks = [
        (40, "Чорношкірі підсудні · p = 51.4%",
         ["1369", "805", "532", "990"],
         ["p = 1901/3696 = 0.514      PPV = 1369/2174 = 0.630",
          "FPR = 805/1795 = 0.449      FNR = 532/1901 = 0.280"]),
        (440, "Білі підсудні · p = 39.4%",
         ["505", "349", "461", "1139"],
         ["p = 966/2454 = 0.394      PPV = 505/854 = 0.591",
          "FPR = 349/1488 = 0.235      FNR = 461/966 = 0.477"]),
    ]

    for (bx, ttl, cells, rates) in blocks:
        f.append(text(bx + 195, 56, ttl, size=13, bold=True))
        f.append(text(bx + 160, 80, "подія є", size=12, color=MUTED))
        f.append(text(bx + 280, 80, "події нема", size=12, color=MUTED))
        f.append(text(bx + 98, 116, "тривога", size=12, anchor="end"))
        f.append(text(bx + 98, 164, "мовчанка", size=12, anchor="end"))
        style = [("#e9f7ec", FIELD), ("#fdecea", POS), ("#fdecea", POS), ("#e9f7ec", FIELD)]
        for i, val in enumerate(cells):
            fill, stroke = style[i]
            f.append(fitbox(bx + 105 + (i % 2) * 120, 88 + (i // 2) * 48, 110, 44,
                            [val], size=15, fill=fill, stroke=stroke))
        f.append(fitbox(bx, 194, 350, 66, rates, size=12))

    f.append(fitbox(40, 278, 750, 52,
                    ["FPR = ( p/(1 − p) ) · ( (1 − PPV)/PPV ) · (1 − FNR)"],
                    size=16, fill="#f7f8fa", stroke="#c9ccd3"))
    f.append(fitbox(40, 344, 750, 66,
                    ["Достовірність тривоги майже збіглася — 0.630 і 0.591.",
                     "Частки хибних тривог розійшлися вдвічі: 0.449 проти 0.235.",
                     "За різних базових частот тотожність не дозволяє інакше."],
                    size=14, fill="#fff8e1", stroke="#c9a227"))

    render(os.path.join(OUT, 'parity-identity.svg'), W, H, *f)


if __name__ == '__main__':
    fig_base_rate_tree()
    fig_iso_cost_roc()
    fig_parity_identity()
    fig_outside_the_cloud()
    fig_cheapest_feature()
    fig_threshold_and_cost()
    fig_slice_ranking()
    fig_psi_noise_floor()
    fig_legend_timeline()
    fig_evidence_ladder()
    print("ok")
