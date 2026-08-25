# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE  = NEG          # передбачення
RED   = POS          # вимір
GREEN = FIELD        # поєднана оцінка / правда


def _bell(cx, w, peak):
    """Точки гауса з центром cx, «шириною» w (px) і висотою peak (px). Повертає (xs,ys)-рядок."""
    pts = []
    for i in range(0, 121):
        t = -3.4 + 6.8 * i / 120.0
        x = cx + t * (w / 3.4)
        y = peak * math.exp(-0.5 * t * t)
        pts.append((x, y))
    return pts


def _curve(pts, oy, color, sw=2.4, fill=None):
    poly = " ".join("%.1f,%.1f" % (x, oy - y) for x, y in pts)
    out = ""
    if fill:
        out += ('<polygon points="%.1f,%.1f %s %.1f,%.1f" fill="%s" opacity="0.12"/>'
                % (pts[0][0], oy, poly, pts[-1][0], oy, color))
    out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (poly, color, sw))
    return out


# ── two-estimates: поєднання двох дзвонів дає вужчий третій ────────────────────
def fig_two_estimates():
    W, H = 700, 360
    ox, oy = 70, 300
    aw = 560
    p = []
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "значення (кут)", size=11, color=INK, italic=True, anchor="end"))

    pred = _bell(ox + aw * 0.34, 150, 150)   # ширший — менш певний
    meas = _bell(ox + aw * 0.64, 95, 200)    # вужчий — певніший
    comb = _bell(ox + aw * 0.555, 78, 235)   # ще вужчий, ближче до виміру

    p.append(_curve(pred, oy, BLUE, 2.4, fill=BLUE))
    p.append(_curve(meas, oy, RED, 2.4, fill=RED))
    p.append(_curve(comb, oy, GREEN, 3.0, fill=GREEN))

    p.append(text(ox + aw * 0.30, oy - 162, "передбачення", size=12, color=BLUE, bold=True))
    p.append(text(ox + aw * 0.70, oy - 212, "вимір", size=12, color=RED, bold=True, anchor="start"))
    p.append(text(ox + aw * 0.555, oy - 248, "поєднана оцінка", size=12, color=GREEN, bold=True))
    p.append(text(ox + aw * 0.555, oy - 234, "(вужча за обидві)", size=10, color=GREEN))

    render(os.path.join(OUT, "two-estimates.svg"), W, H, *p,
           title="Дві неточні оцінки дають одну, точнішу за обидві")


# ── predict-update-cycle: цикл передбачення ⇄ оновлення ───────────────────────
def fig_predict_update_cycle():
    W, H = 700, 300
    cx, cy = W / 2, 162
    p = []
    bw, bh = 210, 86
    lx, rx = cx - 175, cx + 175

    pb = fitbox(lx - bw / 2, cy - bh / 2, bw, bh,
                "ПЕРЕДБАЧЕННЯ\n(predict)\nмодель штовхає оцінку,\nневпевненість росте",
                size=12, fill="#eef2fc", stroke=BLUE, sw=2, bold=True, color=BLUE)
    ub = fitbox(rx - bw / 2, cy - bh / 2, bw, bh,
                "ОНОВЛЕННЯ\n(update)\nвимір виправляє оцінку,\nневпевненість падає",
                size=12, fill="#fdeeec", stroke=RED, sw=2, bold=True, color=RED)
    p.append(pb)
    p.append(ub)

    # дуги по колу між блоками
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (lx + bw / 2 - 6, cy - 18, cx - 40, cy - 78, cx + 40, cy - 78,
                rx - bw / 2 + 6, cy - 18, INK))
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (rx - bw / 2 + 6, cy + 18, cx + 40, cy + 78, cx - 40, cy + 78,
                lx + bw / 2 - 6, cy + 18, INK))

    p.append(text(cx, cy - 84, "проміж вимірами", size=11, color=MUTED))
    p.append(text(cx, cy + 96, "на кожному вимірі", size=11, color=MUTED))
    p.append(text(W / 2, H - 18, "десятки разів на секунду", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "predict-update-cycle.svg"), W, H, *p,
           title="Два кроки по колу: передбачити, тоді виправити")


# ── breathing-uncertainty: передбачення ширшає, оновлення вужчає ──────────────
def fig_breathing_uncertainty():
    W, H = 700, 320
    oy = 250
    p = []
    p.append(arrow(70, oy, 660, oy, color=INK, sw=1.6))
    p.append(text(648, oy + 20, "час →", size=11, color=INK, italic=True, anchor="end"))

    prior = _bell(180, 70, 175)
    wide  = _bell(330, 130, 110)
    meas  = _bell(470, 80, 180)
    post  = _bell(560, 62, 200)

    p.append(_curve(prior, oy, BLUE, 2.4, fill=BLUE))
    p.append(_curve(wide,  oy, BLUE, 2.0))
    p.append(_curve(meas,  oy, RED, 2.2, fill=RED))
    p.append(_curve(post,  oy, GREEN, 3.0, fill=GREEN))

    p.append(arrow(225, oy - 150, 300, oy - 118, color=INK, sw=1.4))
    p.append(text(258, oy - 162, "передбачення:\nдзвін ширшає", size=10, color=BLUE))
    p.append(text(470, oy - 196, "вимір", size=10, color=RED))
    p.append(arrow(498, oy - 150, 552, oy - 178, color=INK, sw=1.4))
    p.append(text(560, oy - 214, "оновлення:\nдзвін вужчає", size=10, color=GREEN))

    render(os.path.join(OUT, "breathing-uncertainty.svg"), W, H, *p,
           title="Невпевненість «дихає»: росте без виміру, падає на вимірі")


# ── kalman-gain: K як функція невпевненості виміру ────────────────────────────
def fig_kalman_gain():
    W, H = 700, 300
    ox, oy = 90, 240
    aw, ah = 540, 180
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 12, oy - ah - 4, "K", size=13, color=INK, bold=True, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah + 12, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy + 4, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(ox + aw, oy + 20, "невпевненість виміру  R →", size=11, color=INK, italic=True, anchor="end"))

    # K = P/(P+R): спадна крива від 1 до 0
    pts = []
    P = 1.0
    for i in range(0, 301):
        R = 6.0 * i / 300.0
        K = P / (P + R)
        pts.append("%.1f,%.1f" % (ox + (R / 6.0) * aw, oy - K * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), GREEN))

    p.append(text(ox + aw * 0.10, oy - ah * 0.86, "давач точний → K → 1\n(вір виміру)",
                  size=11, color=RED, anchor="start", bold=True))
    p.append(text(ox + aw * 0.52, oy - ah * 0.20, "давач шумний → K → 0\n(вір передбаченню)",
                  size=11, color=BLUE, anchor="start", bold=True))

    render(os.path.join(OUT, "kalman-gain.svg"), W, H, *p,
           title="Коефіцієнт K фільтр рахує сам — щокроку, з невпевненостей")


# ── self-tuning: K збігається, α — пряма ──────────────────────────────────────
def fig_self_tuning():
    W, H = 700, 290
    ox, oy = 80, 230
    aw, ah = 560, 176
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час (кроки) →", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 4, "довіра до виміру", size=11, color=INK, anchor="end"))

    # K стартує високим і спадає до сталого
    steady = 0.42
    pts = []
    for i in range(0, 301):
        t = i / 300.0
        K = steady + (0.95 - steady) * math.exp(-5.0 * t)
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - K * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), GREEN))
    p.append(text(ox + aw * 0.30, oy - 0.78 * ah, "K Калмана: сам збігається",
                  size=11, color=GREEN, anchor="start", bold=True))

    # α — фіксована пряма
    ay = oy - steady * ah
    p.append(line(ox, ay, ox + aw, ay, color=MUTED, sw=2.0, dash="7 5"))
    p.append(text(ox + aw * 0.55, ay + 18, "(1−α) комплементарного: фіксоване від початку",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "self-tuning.svg"), W, H, *p,
           title="Калман адаптує довіру сам; стале α — ні")


# ── confidence-band: оцінка з коридором ±σ, що звужується ─────────────────────
def fig_confidence_band():
    W, H = 700, 300
    ox, oy = 70, 250
    aw, ah = 580, 200
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час →", size=11, color=INK, italic=True, anchor="end"))

    def truth(t):
        return 0.55 + 0.12 * math.sin(3.3 * t)

    def sigma(t):
        return 0.30 * math.exp(-3.2 * t) + 0.035

    top, bot, est = [], [], []
    for i in range(0, 301):
        t = i / 300.0
        x = ox + t * aw
        c, s = truth(t), sigma(t)
        est.append("%.1f,%.1f" % (x, oy - c * ah))
        top.append((x, oy - (c + s) * ah))
        bot.append((x, oy - (c - s) * ah))
    band = " ".join("%.1f,%.1f" % q for q in top) + " " + \
           " ".join("%.1f,%.1f" % q for q in reversed(bot))
    p.append('<polygon points="%s" fill="%s" opacity="0.16"/>' % (band, GREEN))

    # правда
    tr = " ".join("%.1f,%.1f" % (ox + (i / 300.0) * aw, oy - truth(i / 300.0) * ah) for i in range(0, 301))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % (tr, MUTED))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-linejoin="round"/>' % (" ".join(est), GREEN))

    p.append(text(ox + aw * 0.12, oy - 0.93 * ah, "коридор ±σ широкий\n(фільтр невпевнений)",
                  size=10, color=INK, anchor="start"))
    p.append(text(ox + aw * 0.66, oy - 0.86 * ah, "коридор вузький\n(фільтр набрав певності)",
                  size=10, color=GREEN, anchor="start"))
    p.append(text(ox + aw * 0.66, oy - truth(0.7) * ah + 26, "оцінка", size=10, color=GREEN, anchor="start", bold=True))

    render(os.path.join(OUT, "confidence-band.svg"), W, H, *p,
           title="Калман видає кут і коридор довіри ±σ, що звужується")


# ── orientation-state: стан = кут + зсув нуля; predict гіро, update акс/маг ────
def fig_orientation_state():
    W, H = 720, 280
    p = []
    cy = 150
    # ліворуч — джерела передбачення; центр — стан; праворуч — корекція
    state, sw_, sh_ = textbox(W / 2, cy, "СТАН\nкут θ\n+ зсув нуля гіро b",
                              size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    gyro = fitbox(40, cy - 32, 150, 64, "гіроскоп\n(передбачення)",
                  size=11, fill="#eef2fc", stroke=BLUE, sw=1.8, bold=True, color=BLUE)
    corr = fitbox(W - 190, cy - 52, 150, 104,
                  "акселерометр\n+ магнітометр\n(корекція)",
                  size=11, fill="#fdeeec", stroke=RED, sw=1.8, bold=True, color=RED)
    out = fitbox(W - 190, cy + 72, 150, 44, "кут + його певність",
                 size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=FIELD)
    p += [gyro, corr, out, state]

    p.append(arrow(190, cy, W / 2 - sw_ / 2 - 4, cy, color=BLUE, sw=2.0))
    p.append(arrow(W - 190, cy, W / 2 + sw_ / 2 + 4, cy, color=RED, sw=2.0))
    p.append(arrow(W / 2, cy + sh_ / 2, W / 2, cy + 94, color=INK, sw=1.6))
    p.append(arrow(W / 2, cy + 94, W - 190 + 2, cy + 94, color=INK, sw=1.6))

    p.append(text(W / 2, H - 16, "повороти нелінійні → на практиці беруть розширений фільтр (EKF)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "orientation-state.svg"), W, H, *p,
           title="Калман для орієнтації: оцінює й сам дрейф гіроскопа")


# ════════════════ фігури історичної вставки (hist-kalman) ═════════════════════

# ── wiener-vs-kalman: вся історія проти двох згорток ──────────────────────────
def fig_wiener_vs_kalman():
    W, H = 720, 300
    p = []
    cy = 150
    # Вінер — стос усієї історії
    p.append(text(190, 70, "Фільтр Вінера", size=13, color=INK, bold=True))
    bx = 60
    for i in range(7):
        p.append(rect(bx + i * 34, cy - 18 - i * 3, 28, 60, fill="#eef2fc", stroke=BLUE, sw=1.4, rx=2))
    p.append(text(190, cy + 78, "потрібна ВСЯ історія сигналу\n+ стала статистика, частотна область",
                  size=11, color=BLUE))

    p.append(text(W / 2, cy, "≠", size=26, color=MUTED, bold=True))

    # Калман — дві згортки
    p.append(text(W - 200, 70, "Фільтр Калмана", size=13, color=INK, bold=True))
    p.append(rect(W - 300, cy - 18, 80, 56, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(mtext(W - 260, cy + 6, "оцінка x", size=11, color=FIELD, bold=True))
    p.append(rect(W - 200, cy - 18, 80, 56, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(mtext(W - 160, cy + 6, "невпевн. P", size=11, color=FIELD, bold=True))
    p.append(text(W - 200, cy + 78, "лише поточна оцінка та її невпевненість\n→ влазить у крихітну пам'ять",
                  size=11, color=FIELD))

    render(os.path.join(OUT, "wiener-vs-kalman.svg"), W, H, *p,
           title="Чому Вінера було замало для борту")


# ── recursive-memory: цикл стискає минуле у два числа ─────────────────────────
def fig_recursive_memory():
    W, H = 700, 280
    cx, cy = W / 2, 150
    p = []
    core, cw, ch = textbox(cx, cy, "x, P\n(оцінка + невпевненість)",
                           size=13, bold=True, fill="#eafaf0", stroke=FIELD, sw=2, pad=16)
    # кільце-стрілка навколо
    p.append('<path d="M %.0f %.0f A 96 80 0 1 1 %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (cx + 96, cy - 6, cx + 92, cy + 14, INK))
    p.append(text(cx, cy - 96, "передбачити вперед", size=11, color=BLUE, bold=True))
    p.append(text(cx, cy + 104, "виправити виміром, тоді відкинути вимір", size=11, color=RED, bold=True))
    p.append(core)

    # вхід-вимір, що відкидається
    p.append(arrow(70, cy, cx - cw / 2 - 6, cy, color=MUTED, sw=1.6))
    p.append(text(120, cy - 12, "новий вимір", size=10, color=MUTED, anchor="start"))
    p.append(text(W / 2, H - 16, "уся історія стиснута у два числа — стала, крихітна пам'ять",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "recursive-memory.svg"), W, H, *p,
           title="Прорив Калмана: рекурсія замість пам'яті")


# ── parallel-discovery: естафета відкриттів ───────────────────────────────────
def fig_parallel_discovery():
    W, H = 740, 300
    p = []
    p.append(text(W / 2, 56, "одну ідею знаходили знову й знову — по різні боки завіси",
                  size=11, color=MUTED, italic=True))
    west_y, east_y = 120, 220
    p.append(text(40, west_y - 30, "Захід", size=11, color=RED, bold=True, anchor="start"))
    p.append(text(40, east_y + 36, "СРСР", size=11, color=BLUE, bold=True, anchor="start"))

    def node(x, y, lab, col, fill):
        b, bw, bh = textbox(x, y, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.6, pad=7)
        return b

    p.append(node(110, west_y, "Вінер\n1940-ві", RED, "#fdeeec"))
    p.append(node(280, west_y, "Сверлінг\n1958", RED, "#fdeeec"))
    p.append(node(470, west_y, "Калман\n1960", RED, "#fdeeec"))
    p.append(node(640, west_y, "Калман–Б'юсі\n1961", RED, "#fdeeec"))

    p.append(node(110, east_y, "Колмогоров,\nКрейн", BLUE, "#eef2fc"))
    p.append(node(320, east_y, "Стратонович\n1958–60", BLUE, "#eef2fc"))

    # ранній корінь
    p.append(node(110, (west_y + east_y) / 2 - 2, "Тіле 1880", MUTED, "#f0f0f0"))

    for x0, x1, y in [(150, 240, west_y), (330, 425, west_y), (520, 575, west_y)]:
        p.append(arrow(x0, y, x1, y, color=INK, sw=1.6))
    p.append(arrow(165, east_y, 270, east_y, color=INK, sw=1.6))
    p.append(arrow(370, east_y - 14, 440, west_y + 18, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "parallel-discovery.svg"), W, H, *p,
           title="Естафета, а не самотній геній")


# ── resistance: стаття пішла в «чужий» журнал ─────────────────────────────────
def fig_resistance():
    W, H = 700, 250
    p = []
    cy = 140
    a, aw_, ah_ = textbox(150, cy, "рецензенти-\nелектротехніки",
                          size=12, bold=True, color=RED, fill="#fdeeec", stroke=RED, sw=1.8)
    b, bw_, bh_ = textbox(W - 180, cy, "журнал\nз машинобудування\n(Journal of Basic Engineering)",
                          size=12, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p += [a, b]
    # стіна
    p.append(text(150, cy - ah_ / 2 - 12, "✗ спротив", size=11, color=RED, bold=True))
    p.append(arrow(150 + aw_ / 2, cy + ah_ / 2 + 6, W - 180 - bw_ / 2, cy + 4, color=INK, sw=1.8))
    p.append(text(W / 2, cy + 70, "проривна стаття 1960 року вийшла «не за фахом» — і ледь не загубилась",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "resistance.svg"), W, H, *p,
           title="Опір новому: ідею мало не проґавили")


# ── apollo-nav: інерціальне передбачення + зоряні візування ───────────────────
def fig_apollo_nav():
    W, H = 720, 280
    p = []
    cy = 150
    state, sw_, sh_ = textbox(W / 2, cy, "EKF\nположення\n+ швидкість",
                              size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    pred = fitbox(40, cy - 42, 170, 84,
                  "інерціальний блок\n+ небесна механіка\n(передбачення)",
                  size=11, fill="#eef2fc", stroke=BLUE, sw=1.8, bold=True, color=BLUE)
    meas = fitbox(W - 210, cy - 42, 170, 84,
                  "секстант: візування\nзір (вимір —\nточний, але рідкий)",
                  size=11, fill="#fdeeec", stroke=RED, sw=1.8, bold=True, color=RED)
    p += [pred, meas, state]
    p.append(arrow(210, cy, W / 2 - sw_ / 2 - 4, cy, color=BLUE, sw=2.0))
    p.append(arrow(W - 210, cy, W / 2 + sw_ / 2 + 4, cy, color=RED, sw=2.0))
    p.append(text(W / 2, H - 16, "усе — в кількадесят кілобайт бортового комп'ютера",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "apollo-nav.svg"), W, H, *p,
           title="Фільтр Калмана веде «Аполлон» до Місяця")


# ── moon-to-drone: спадок від Місяця до дрона ─────────────────────────────────
def fig_moon_to_drone():
    W, H = 740, 220
    p = []
    y = 110
    bw, bh = 150, 60
    step = 188
    x = 30
    stages = [
        ("навігація\n«Аполлона»\n1960-ті", "#eef2fc", BLUE),
        ("авіація,\nGPS", FILL, INK),
        ("робототехніка,\nавто", FILL, INK),
        ("EKF у дроні\nсьогодні", "#eafaf0", FIELD),
    ]
    centers = []
    for i, (lab, fill, col) in enumerate(stages):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y, x - 2, y, color=INK, sw=1.8))
        x += step
    p.append(text(W / 2, y + 64, "об'єкти різні, ідея одна: передбачення + вимір, зважені за певністю",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "moon-to-drone.svg"), W, H, *p,
           title="Той самий фільтр: від Місяця до вашого дрона")


if __name__ == "__main__":
    fig_two_estimates()
    fig_predict_update_cycle()
    fig_breathing_uncertainty()
    fig_kalman_gain()
    fig_self_tuning()
    fig_confidence_band()
    fig_orientation_state()
    fig_wiener_vs_kalman()
    fig_recursive_memory()
    fig_parallel_discovery()
    fig_resistance()
    fig_apollo_nav()
    fig_moon_to_drone()
    print("OK: figures written to", OUT)
