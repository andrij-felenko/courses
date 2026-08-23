# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── why-multimeter-lies: вікно усереднення розмазує короткі піки TX ───────────
# Ідея: реальний профіль — довгий сон у мкА з рідкими піками TX у сотні мА.
# Мультиметр інтегрує за широке вікно, ловить хвіст піку й показує число
# посередині — ні пік, ні чесне середнє.

def fig_why_multimeter_lies():
    W, H = 720, 300
    ox, oy = 60, 250                 # початок осей
    aw = 588                         # довжина горизонталі
    top = 60                         # верх піку

    # лог-сітка по струму: 10 мкА (низ) .. 100 мА (верх)
    decades = [("10 мкА", 0), ("1 мА", 1), ("10 мА", 2), ("100 мА", 3)]
    span = 190.0                     # від oy-? базова лінія сну до верху
    base_y = oy - 28                 # рівень сну (10 мкА)
    peak_y = top                     # рівень піку

    def ylevel(i):                   # i = номер декади над 10 мкА
        return base_y - (base_y - peak_y) * (i / 3.0)

    p = [text(W / 2, 28, "Реальний профіль проти того, що бачить мультиметр",
              size=15, bold=True)]
    p.append(line(ox, top - 5, ox, oy, color=LINE))
    p.append(line(ox, oy, ox + aw, oy, color=LINE))

    for lbl, i in decades:
        y = ylevel(i)
        p.append(line(ox - 5, y, ox, y, color=MUTED, sw=1.0))
        p.append(line(ox, y, ox + aw, y, color=MUTED, sw=0.4, dash="3,4"))
        p.append(text(ox - 8, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # три цикли «сон → пік TX → сон»
    cyc = aw / 3.0
    for k in range(3):
        x0 = ox + k * cyc
        x_rise = x0 + cyc * 0.27
        x_fall = x_rise + cyc * 0.07
        p.append(line(x0, base_y, x_rise, base_y, color=NEG, sw=2.0))      # сон
        p.append(line(x_rise, base_y, x_rise, peak_y, color=POS, sw=1.8))  # фронт
        p.append(line(x_rise, peak_y, x_fall, peak_y, color=POS, sw=3.0))  # пік TX
        p.append(line(x_fall, peak_y, x_fall, base_y, color=POS, sw=1.8))  # спад
        p.append(line(x_fall, base_y, x0 + cyc, base_y, color=NEG, sw=2.0))

    # вікно усереднення мультиметра — навколо першого піку
    wx, ww = ox + cyc * 0.13, cyc * 0.42
    p.append(rect(wx, top, ww, oy - top - 5, fill="#fef9e7", stroke="#f39c12", sw=2.0, rx=4))
    p.append(text(wx + ww / 2, top + 14, "вікно", size=10, color="#f39c12", bold=True))
    p.append(text(wx + ww / 2, top + 27, "усереднення", size=10, color="#f39c12", bold=True))
    # показане мультиметром (~3 мА)
    mm_y = ylevel(1.55)
    p.append(line(wx, mm_y, wx + ww, mm_y, color="#f39c12", sw=2.5, dash="6,4"))
    p.append(text(wx + ww + 6, mm_y + 4, "«3 мА» (мультиметр)", size=10, color="#f39c12",
                  anchor="start", bold=True))
    # реальне середнє (~90 мкА) — біля дна
    re_y = ylevel(0.42)
    p.append(line(ox, re_y, ox + aw, re_y, color=FIELD, sw=2.0, dash="10,5"))
    p.append(text(ox + aw - 4, re_y - 6, "~90 мкА (реальне середнє)", size=10,
                  color=FIELD, anchor="end", bold=True))

    render(os.path.join(OUT, "why-multimeter-lies.svg"), W, H, *p)


# ── correct-measurement: шунт + осцилограф, інтеграл профілю = I_сер ──────────

def fig_correct_measurement():
    W, H = 760, 320
    p = [text(W / 2, 28, "Чесний вимір: шунт + осцилограф, площа профілю = I_сер",
              size=15, bold=True)]
    y = 100
    # батарея
    b, bw, bh = textbox(50, y, "Батарея\n3.3 В", size=12, color=NEG, fill="#d6eaf8",
                        stroke=NEG, sw=2.0)
    p.append(b)
    p.append(line(50 + bw / 2, y, 178, y, color=LINE, sw=2.0))
    # шунт
    sh, sw_, shh = textbox(220, y, "Шунт\n0.1 Ом", size=12, color="#e67e22",
                           fill="#fdf2e9", stroke="#e67e22", sw=2.0)
    p.append(sh)
    p.append(line(220, y + shh / 2, 220, 158, color="#e67e22", sw=1.5))
    p.append(text(226, 150, "V_шунт = I × R", size=10, color="#e67e22", anchor="start"))
    p.append(line(220 + sw_ / 2, y, 360, y, color=LINE, sw=2.0))
    # чип
    c, cw, ch = textbox(392, y, "ESP32", size=12, color=NEG, fill="#d6eaf8",
                        stroke=NEG, sw=2.0, min_w=64)
    p.append(c)
    # зворотний провід (GND)
    p.append(line(392 + cw / 2, y, 520, y, color=LINE, sw=2.0))
    p.append(line(520, y, 520, 210, color=LINE, sw=2.0))
    p.append(line(520, 210, 50, 210, color=LINE, sw=2.0))
    p.append(line(50, 210, 50, y + bh / 2, color=LINE, sw=2.0))
    # осцилограф знімає V_шунт
    p.append(line(205, y + shh / 2, 175, 232, color="#1a7a73", sw=1.5, dash="4,3"))
    p.append(line(235, y + shh / 2, 265, 232, color="#1a7a73", sw=1.5, dash="4,3"))
    sc, scw, sch = textbox(220, 250, "Осцилограф /\nPower Profiler", size=12,
                           color="#1a7a73", fill="#e8f8f7", stroke="#1a7a73", sw=2.0)
    p.append(sc)
    # формула
    fb = fitbox(516, 76, 200, 80, "I(t) = V_шунт(t) / R\n\nI_сер = ∫I dt / T\n= площа ÷ час",
                size=12, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=2.0)
    p.append(fb)
    # попередження про burden voltage
    wb = fitbox(516, 230, 200, 60,
                "burden voltage: на піку\nI×R просаджує живлення\nчипа → brownout",
                size=11, color=POS, fill="#fff5f5", stroke=POS, sw=1.5)
    p.append(wb)
    render(os.path.join(OUT, "correct-measurement.svg"), W, H, *p)


# ── profiler-chain: тракт сигналу профілювальника + range-switching ──────────

def fig_profiler_chain():
    W, H = 860, 430
    p = [text(W / 2, 28, "Тракт сигналу профілювальника струму", size=16, bold=True)]
    yc = 200

    b1, w1, h1 = textbox(60, yc, "DUT\n(пристрій\nпід тестом)", size=12)
    p.append(b1)
    p.append(arrow(60 + w1 / 2, yc, 172, yc - 8, color=INK))

    # вузол range-switching
    p.append(rect(172, 110, 156, 162, fill="#e8f8f0", stroke=FIELD, sw=2.5, rx=10))
    p.append(text(250, 124, "range-switching", size=11, color=FIELD, bold=True))
    p.append(fitbox(195, 132, 110, 32, "нА-шунт\n(великий Ω)", size=10, fill="#dff5e8",
                    stroke=MUTED, sw=1.2))
    p.append(fitbox(195, 170, 110, 22, "мкА/мА-шунт", size=10, sw=1.2))
    p.append(fitbox(195, 198, 110, 32, "А-шунт\n(малий Ω)", size=10, fill="#fdf0e8",
                    stroke=MUTED, sw=1.2))
    p.append(text(250, 252, "автоперемикання за нс–мкс", size=10, color=MUTED))

    p.append(arrow(328, yc - 8, 372, yc, color=INK))
    b2, w2, h2 = textbox(440, yc, "підсилювач\nрізниці\n(CSA)", size=12)
    p.append(b2)
    p.append(arrow(440 + w2 / 2, yc, 540, yc, color=INK))
    b3, w3, h3 = textbox(600, yc, "швидкий\nАЦП", size=12)
    p.append(b3)
    p.append(arrow(600 + w3 / 2, yc, 672, yc, color=INK))
    b4, w4, h4 = textbox(710, yc, "USB /\nбуфер", size=12)
    p.append(b4)
    p.append(arrow(710 + w4 / 2, yc, 786, yc, color=INK))
    b5, w5, h5 = textbox(820, yc, "ПК\nI(t)", size=12, fill="#e8eaf6", stroke=NEG)
    p.append(b5)

    # burden voltage — підпис під вузлом
    p.append(line(250, 272, 250, 360, color=POS, sw=1.2, dash="4,3"))
    p.append(text(250, 376, "burden voltage — спад на шунті,", size=11, color=POS))
    p.append(text(250, 390, "критичний для сплячого МК", size=11, color=POS))
    p.append(text(W / 2, 418, "Range-switching склеює нА сну й сотні мА передачі в єдиний графік",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "profiler-chain.svg"), W, H, *p)


# ── profiler-wiring: два режими ввімкнення ───────────────────────────────────

def fig_profiler_wiring():
    W, H = 820, 400
    p = [text(W / 2, 28, "Два режими ввімкнення профілювальника", size=16, bold=True)]

    # ліва панель — ampere-meter
    p.append(rect(10, 50, 380, 268, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(200, 72, "ampere-meter mode", size=13, bold=True))
    p.append(text(200, 88, "(розрив плюсового проводу)", size=11, color=MUTED))
    p.append(fitbox(40, 140, 72, 44, "Джерело\nживлення", size=12))
    p.append(fitbox(174, 132, 72, 60, "Профіль-\nщик\nIN+→OUT+", size=11, fill="#e8f8f0",
                    stroke=FIELD, sw=2.0))
    p.append(fitbox(322, 140, 38, 44, "DUT\nVDD", size=11))
    p.append(arrow(116, 150, 168, 150, color=INK))
    p.append(arrow(250, 150, 316, 150, color=INK))
    p.append(line(30, 210, 375, 210, color=NEG, sw=1.8))
    p.append(text(200, 228, "спільна GND", size=11, color=NEG))
    p.append(plus(135, 140, r=8))
    p.append(minus(135, 210, r=8))
    p.append(text(200, 262, "Прилад — послідовно у розрив плюса.", size=11))
    p.append(text(200, 279, "Своє живлення — окремий USB до ПК.", size=11))

    # права панель — source-meter
    p.append(rect(420, 50, 390, 268, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(615, 72, "source-meter mode", size=13, bold=True))
    p.append(text(615, 88, "(прилад сам живить DUT)", size=11, color=MUTED))
    p.append(fitbox(512, 132, 116, 60, "Профілювальник\n3.3 В / source\n+ вимір I",
                    size=11, fill="#e8f8f0", stroke=FIELD, sw=2.0))
    p.append(fitbox(732, 140, 38, 44, "DUT\nVDD", size=11))
    p.append(arrow(632, 150, 726, 150, color=INK))
    p.append(line(440, 210, 795, 210, color=NEG, sw=1.8))
    p.append(text(615, 228, "спільна GND", size=11, color=NEG))
    p.append(line(570, 124, 570, 100, color=MUTED, sw=1.5, dash="4,3"))
    p.append(text(615, 96, "один USB до ПК: і джерело, і вимір", size=10, color=MUTED))
    p.append(text(615, 279, "Один кабель — і живлення, і захоплення.", size=11))

    # нижнє попередження
    p.append(rect(10, 332, 800, 58, fill="#fff5f5", stroke=POS, sw=1.5, rx=7))
    p.append(text(W / 2, 354, "НЕ вмикати в розрив після USB-роз'єму DevKit — USB-UART міст і LDO домішують своє споживання",
                  size=11, color=POS))
    p.append(text(W / 2, 374, "вмикати в розрив батарейного живлення або в jumper розриву струму", size=11))
    render(os.path.join(OUT, "profiler-wiring.svg"), W, H, *p)


# ── dynamic-range-ladder: лінійка магнітуд струму нА→А (лог-вісь) ─────────────

def fig_dynamic_range_ladder():
    W, H = 920, 500
    p = [text(W / 2, 26, "Лінійка магнітуд струму: нА → А (логарифмічна вісь)",
              size=15, bold=True)]
    ax, ay = 60, 200
    aw = 800
    # 10 декад: 1 нА .. 1 А
    labels = ["1 нА", "10 нА", "100 нА", "1 мкА", "10 мкА", "100 мкА",
              "1 мА", "10 мА", "100 мА", "1 А"]
    exps = ["10⁻⁹", "10⁻⁸", "10⁻⁷", "10⁻⁶", "10⁻⁵", "10⁻⁴",
            "10⁻³", "10⁻²", "10⁻¹", "10⁰"]
    n = len(labels)
    step = aw / (n - 1)

    def X(i):                         # i = індекс декади
        return ax + i * step

    p.append(arrow(ax - 10, ay, ax + aw + 18, ay, color=LINE, sw=2.0))
    for i in range(n):
        x = X(i)
        p.append(line(x, ay - 8, x, ay + 8, color=LINE, sw=1.5))
        p.append(mtext(x, ay + 22, [labels[i], exps[i]], size=10, color=MUTED))

    # смуги режимів (від..до в індексах декад)
    def band(i0, i1, y, fill, stroke):
        p.append(rect(X(i0), ay - 10, X(i1) - X(i0), 20, fill=fill, stroke=stroke, sw=1.8, rx=4))

    band(1, 4, ay, "#dff5e8", FIELD)          # deep-sleep 10 нА..10 мкА
    band(5, 6, ay, "#e8f0ff", NEG)            # light-sleep 0.1..1 мА
    band(7.5, 7.8, ay, "#f4f6f8", INK)        # modem ~20-40 мА (показово вузько)
    band(8.6, 8.75, ay, "#fff3cd", "#e0a020") # RX ~80-100 мА
    band(8.85, 9.0, ay, "#fdecea", POS)       # TX 300-500 мА

    # підписи режимів зверху з виносками
    def tag(cx, top, lines, fill, stroke, anchor_x):
        b, bw, bh = textbox(cx, top, "\n".join(lines), size=9, fill=fill, stroke=stroke, sw=1.2)
        p.append(b)
        p.append(line(cx, top + bh / 2, anchor_x, ay - 10, color=stroke, sw=1.0, dash="3,2"))

    tag(280, 80, ["Deep-sleep", "RTC+ULP", "~10 нА–10 мкА"], "#dff5e8", FIELD, X(2.5))
    tag(548, 120, ["Light-sleep", "~0.1–1 мА"], "#e8f0ff", NEG, X(5.5))
    tag(722, 80, ["Modem / ядро", "~20–40 мА"], "#f4f6f8", INK, X(7.6))
    tag(800, 120, ["RX", "~80–100 мА"], "#fff3cd", "#e0a020", X(8.68))
    tag(866, 86, ["TX-сплеск", "~300–500 мА"], "#fdecea", POS, X(8.9))

    # розмах — стрілка під віссю (1 нА..0.5 А ≈ 7.7 порядку ≈ 154 дБ)
    yb = 268
    p.append(line(X(1), yb - 6, X(1), yb + 6, color=INK, sw=1.5))
    p.append(line(X(8.7), yb - 6, X(8.7), yb + 6, color=INK, sw=1.5))
    p.append(line(X(1), yb, X(8.7), yb, color=INK, sw=1.5))
    rb, rbw, rbh = textbox(W / 2, yb + 22, "повний розмах ≈ 7.7 порядку ≈ 154 дБ",
                           size=11, bold=True, fill="#fffbe6", stroke="#c0a000", sw=1.5)
    p.append(rb)

    # вікно одного шунта (~2 порядки) + «діра»
    p.append(rect(X(1), 112, step * 2, 26, fill="#fffacc", stroke="#d4a000", sw=2.0, rx=4))
    p.append(text(X(2), 128, "~2 порядки", size=9, color="#b08000"))
    p.append(line(X(3), 138, X(7.5), 138, color=POS, sw=1.8, dash="5,3"))
    p.append(text((X(3) + X(7.5)) / 2, 128, "«діра» — невидима зона одного шунта",
                  size=9, color=POS))

    # автодіапазон: кілька шунтів сходами
    p.append(text(80, 322, "Автодіапазон (кілька шунтів — разом ≈ 7 порядків):",
                  size=10, bold=True, anchor="start"))
    rows = [(1, 4, "#dff5e8", FIELD, "нА-шунт"),
            (4, 6.5, "#e8f0ff", NEG, "мкА-шунт"),
            (6.5, 8.5, "#f4f6f8", INK, "мА-шунт"),
            (8.5, 9, "#fdecea", POS, "А-шунт")]
    ry = 338
    for i0, i1, fill, stroke, lbl in rows:
        p.append(rect(X(i0), ry, X(i1) - X(i0), 16, fill=fill, stroke=stroke, sw=1.5, rx=3))
        p.append(text((X(i0) + X(i1)) / 2, ry + 12, lbl, size=9))
        ry += 20

    p.append(text(W / 2, 460, "Одне фіксоване вікно (~2 порядки) не накриває розмах (~7 порядків) → автодіапазон або зовнішній АЦП",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "dynamic-range-ladder.svg"), W, H, *p)


# ── averaging-aliasing: три вікна мультиметра в різних фазах циклу ────────────
# Ідея (детальна): періодичний профіль сон→пік→сон; три незалежні вікна
# усереднення падають у різні фази → три різні показання, жодне ≠ середнє.

def fig_averaging_aliasing():
    W, H = 803, 340
    ox, oy = 56, 232                 # початок осей
    aw = 660
    top = 70                         # верх піку
    base_y = oy - 20                 # рівень сну
    peak_y = top + 6                 # рівень піку

    p = [text(W / 2, 26, "Одне споживання — три вікна усереднення — три показання",
              size=15, bold=True)]
    p.append(line(ox, top - 6, ox, oy, color=LINE))
    p.append(line(ox, oy, ox + aw, oy, color=LINE))
    p.append(text(ox - 6, base_y + 4, "сон", size=9, color=MUTED, anchor="end"))
    p.append(text(ox - 6, peak_y + 4, "пік", size=9, color=MUTED, anchor="end"))

    # три цикли сон→пік→сон
    cyc = aw / 3.0
    peaks_x = []
    for k in range(3):
        x0 = ox + k * cyc
        x_rise = x0 + cyc * 0.42
        x_fall = x_rise + cyc * 0.10
        peaks_x.append((x_rise, x_fall))
        p.append(line(x0, base_y, x_rise, base_y, color=NEG, sw=2.2))
        p.append(line(x_rise, base_y, x_rise, peak_y, color=POS, sw=1.8))
        p.append(line(x_rise, peak_y, x_fall, peak_y, color=POS, sw=3.0))
        p.append(line(x_fall, peak_y, x_fall, base_y, color=POS, sw=1.8))
        p.append(line(x_fall, base_y, x0 + cyc, base_y, color=NEG, sw=2.2))
    p.append(text(ox + cyc * 0.5, oy + 16, "T_цикл", size=9, color=MUTED))
    p.append(line(ox, oy + 8, ox + cyc, oy + 8, color=MUTED, sw=0.8, dash="3,3"))

    # три вікна усереднення в різних фазах
    wy, wh = top - 2, oy - top + 2
    # A — лише сон (між піками 1 і 2)
    ax0 = peaks_x[0][1] + cyc * 0.12
    aw0 = cyc * 0.24
    p.append(rect(ax0, wy, aw0, wh, fill="#eef7ee", stroke=FIELD, sw=1.6, rx=3))
    p.append(text(ax0 + aw0 / 2, wy - 6, "А", size=11, color=FIELD, bold=True))
    # Б — накрило пік 2 цілком
    bx0 = peaks_x[1][0] - cyc * 0.08
    bw0 = cyc * 0.30
    p.append(rect(bx0, wy, bw0, wh, fill="#fef9e7", stroke="#e0a020", sw=1.8, rx=3))
    p.append(text(bx0 + bw0 / 2, wy - 6, "Б", size=11, color="#e0a020", bold=True))
    # В — чіпляє пік 3 частково
    cx0 = peaks_x[2][0] - cyc * 0.02
    cw0 = cyc * 0.16
    p.append(rect(cx0, wy, cw0, wh, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    p.append(text(cx0 + cw0 / 2, wy - 6, "В", size=11, color=POS, bold=True))

    # чесне середнє — низько над сном
    mid_y = base_y - (base_y - peak_y) * 0.16
    p.append(line(ox, mid_y, ox + aw, mid_y, color=FIELD, sw=2.0, dash="9,5"))
    p.append(text(ox + aw - 2, mid_y - 6, "чесне середнє", size=10, color=FIELD,
                  anchor="end", bold=True))

    # три показання праворуч
    lx = ox + aw + 6
    p.append(text(lx, wy + 40, "А → «сон»", size=10, color=FIELD, anchor="start"))
    p.append(text(lx, wy + 40, "", size=10))
    labels = [("А → занижує", FIELD, 92),
              ("Б → завищує", "#e0a020", 116),
              ("В → проміжне", POS, 140)]
    for txt, col, yy in labels:
        p.append(text(lx, yy, txt, size=11, color=col, anchor="start", bold=True))
    p.append(text(W / 2, H - 14,
                  "Множник завищення вікна Б ≈ T_цикл / T_вікно",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "averaging-aliasing.svg"), W, H, *p)


# ── sampling-charge: густий проти рідкого семпла над імпульсом ────────────────

def fig_sampling_charge():
    W, H = 780, 340
    p = [text(W / 2, 26, "Швидкість вибірки — це про заряд, а не про красу графіка",
              size=15, bold=True)]

    def panel(x0, title, sub, col):
        p.append(rect(x0, 46, 360, 250, fill="#f9fafb", stroke=MUTED, sw=1.1, rx=8))
        p.append(text(x0 + 180, 66, title, size=13, bold=True))
        p.append(text(x0 + 180, 82, sub, size=10, color=col))

    panel(10, "Густий семпл", "площа відновлена точно", FIELD)
    panel(410, "Рідкий семпл", "площа втрачена або роздута", POS)

    # спільна геометрія імпульсу
    base_y = 250
    peak_y = 120
    def draw_pulse(bx, rise_frac, w_frac):
        x0 = bx + 20
        span = 300
        xr = x0 + span * rise_frac
        xf = xr + span * w_frac
        pts = [(x0, base_y), (xr, base_y), (xr, peak_y), (xf, peak_y),
               (xf, base_y), (x0 + span, base_y)]
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=INK, sw=1.6))
        return x0, span, xr, xf

    # ліва: густі відліки на вершині
    lx0, lspan, lxr, lxf = draw_pulse(10, 0.42, 0.14)
    n = 15
    for i in range(n + 1):
        sx = lx0 + lspan * i / n
        sy = peak_y if lxr <= sx <= lxf else base_y
        p.append(circle(sx, sy, 2.6, fill=FIELD, stroke=FIELD, sw=1.0))
        p.append(line(sx, sy, sx, base_y, color=FIELD, sw=0.5, dash="2,3"))
    p.append(text(190, 280, "Δt ≪ τ  → сума прямокутників = площа", size=10,
                  color=FIELD))

    # права: рідкі відліки — один випадковий у пік, решта повз
    rx0, rspan, rxr, rxf = draw_pulse(410, 0.42, 0.14)
    marks = [0.06, 0.30, 0.55, 0.80]     # жоден точно на вузькій вершині
    for f in marks:
        sx = rx0 + rspan * f
        sy = peak_y if rxr <= sx <= rxf else base_y
        p.append(circle(sx, sy, 3.2, fill=POS, stroke=POS, sw=1.0))
        p.append(line(sx, sy, sx, base_y, color=POS, sw=0.6, dash="2,3"))
    # роздутий прямокутник, якби відлік упав у пік
    bx = rx0 + rspan * 0.30
    p.append(rect(bx - 26, peak_y, 52, base_y - peak_y, fill="none",
                  stroke=POS, sw=1.2, rx=2))
    p.append(text(590, 280, "Δt ≫ τ  → пік у щілині або роздутий на крок",
                  size=10, color=POS))
    p.append(text(590, 296, "(немає відліку на вершині)", size=9, color=MUTED))
    render(os.path.join(OUT, "sampling-charge.svg"), W, H, *p)


# ── burden-feedback: петля напруги втрат + буферний конденсатор ───────────────

def fig_burden_feedback():
    W, H = 800, 380
    p = [text(W / 2, 26, "Напруга втрат — петля зворотного зв'язку, а не просте віднімання",
              size=15, bold=True)]
    y = 120
    # джерело
    src, sw1, sh1 = textbox(80, y, "Джерело\nV, R_дж", size=12, color=NEG,
                            fill="#d6eaf8", stroke=NEG, sw=2.0)
    p.append(src)
    p.append(line(80 + sw1 / 2, y, 210, y, color=LINE, sw=2.0))
    # шунт
    shb, sw2, sh2 = textbox(258, y, "Шунт R_ш", size=12, color="#e67e22",
                            fill="#fdf2e9", stroke="#e67e22", sw=2.0)
    p.append(shb)
    p.append(text(258, y - 26, "спад I·(R_дж+R_ш)", size=10, color="#e67e22"))
    p.append(line(258 + sw2 / 2, y, 400, y, color=LINE, sw=2.0))
    # вузол живлення чипа
    p.append(circle(400, y, 4, fill=INK, stroke=INK, sw=1.0))
    p.append(text(400, y - 12, "V_чип", size=10, color=INK))
    # буферний конденсатор після шунта
    p.append(line(400, y, 400, y + 46, color=FIELD, sw=1.6))
    p.append(line(388, y + 46, 412, y + 46, color=FIELD, sw=2.4))
    p.append(line(388, y + 52, 412, y + 52, color=FIELD, sw=2.4))
    p.append(line(400, y + 52, 400, y + 70, color=FIELD, sw=1.6))
    p.append(text(420, y + 52, "буферний C", size=10, color=FIELD, anchor="start"))
    p.append(line(400, y, 520, y, color=LINE, sw=2.0))
    # чип
    chip, sw3, sh3 = textbox(560, y, "Чип\n(радіо)", size=12, color=NEG,
                             fill="#d6eaf8", stroke=NEG, sw=2.0)
    p.append(chip)
    # земля
    p.append(line(560 + sw3 / 2, y, 700, y, color=LINE, sw=2.0))
    p.append(line(700, y, 700, y + 130, color=LINE, sw=2.0))
    p.append(line(700, y + 130, 80, y + 130, color=LINE, sw=2.0))
    p.append(line(80, y + 130, 80, y + sh1 / 2, color=LINE, sw=2.0))
    p.append(line(400, y + 70, 400, y + 130, color=FIELD, sw=1.4))

    # петля — стрілки коментарями
    ly = 236
    p.append(rect(120, ly, 560, 96, fill="#fff7f2", stroke=POS, sw=1.4, rx=8))
    p.append(text(W / 2, ly + 20, "Петля (навантаження сталої потужності):", size=12,
                  color=POS, bold=True))
    p.append(text(W / 2, ly + 42,
                  "струм ↑ → спад ↑ → V_чип ↓ → (P=V·I const) струм ↑ …",
                  size=12, color=INK))
    p.append(text(W / 2, ly + 64,
                  "аж до V_чип < V_BOR → штучний brown-out, профіль зруйновано",
                  size=11, color=POS))
    p.append(text(W / 2, ly + 84,
                  "буферний C: псує форму піку (занижує вершину), але зберігає заряд",
                  size=11, color=FIELD))
    render(os.path.join(OUT, "burden-feedback.svg"), W, H, *p)


# ── capacitor-discharge: V(t) ламана + дотична + лінія витоку ─────────────────

def fig_capacitor_discharge():
    W, H = 760, 360
    ox, oy = 60, 280
    aw, ah = 620, 210
    p = [text(W / 2, 26, "Конденсаторний метод: заряд = C·(V₀−V₁), поправка на виток",
              size=15, bold=True)]
    p.append(line(ox, oy - ah, ox, oy, color=LINE))
    p.append(line(ox, oy, ox + aw, oy, color=LINE))
    p.append(text(ox - 8, oy - ah + 6, "V", size=11, color=MUTED, anchor="end"))
    p.append(text(ox + aw, oy + 18, "t", size=11, color=MUTED))

    v0 = oy - ah + 20                # рівень V₀ (високо)
    v1 = oy - 40                     # рівень V₁ (нижче)
    x0, x1 = ox + 10, ox + aw - 40
    p.append(line(ox - 4, v0, ox + 4, v0, color=MUTED, sw=1.0))
    p.append(text(ox - 8, v0 + 4, "V₀", size=10, color=MUTED, anchor="end"))
    p.append(line(ox - 4, v1, ox + 4, v1, color=MUTED, sw=1.0))
    p.append(text(ox - 8, v1 + 4, "V₁", size=10, color=MUTED, anchor="end"))
    p.append(line(ox, oy, x0, oy, color=MUTED, sw=0.6, dash="2,3"))
    p.append(line(x1, oy - 6, x1, oy + 6, color=MUTED, sw=1.0))
    p.append(text((x0 + x1) / 2, oy + 18, "N секунд", size=10, color=MUTED))

    # ламана V(t): полого (сон) + круто (пік) + полого + круто …
    import math as _m
    n = 260
    seg = [(0.00, 0.28, "flat"), (0.28, 0.34, "steep"),
           (0.34, 0.64, "flat"), (0.64, 0.70, "steep"),
           (0.70, 1.00, "flat")]
    # будуємо кусково-лінійну криву від V₀ до V₁ з крутими сходинками на піках
    xs = []
    ys = []
    # ваги падіння: круті ділянки з'їдають більшу частку ΔV
    drop_flat = 0.10
    drop_steep = 0.35
    frac_used = 0.0
    total = 2 * drop_steep + 3 * drop_flat
    cur = v0
    pts = [(x0, cur)]
    for a, b, kind in seg:
        d = (drop_steep if kind == "steep" else drop_flat) / total
        xa = x0 + (x1 - x0) * a
        xb = x0 + (x1 - x0) * b
        nxt = cur + (v1 - v0) * d
        pts.append((xb, nxt))
        cur = nxt
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=NEG, sw=2.4))
    p.append(text(x1 - 60, v1 - 14, "V(t) розряду", size=11, color=NEG, bold=True))

    # пряма усереднення V₀→V₁ (пунктир)
    p.append(line(x0, v0, x1, v1, color="#e0a020", sw=1.8, dash="8,5"))
    p.append(text((x0 + x1) / 2 + 40, (v0 + v1) / 2 - 8,
                  "нахил = лише СЕРЕДНЄ", size=10, color="#c08000"))

    # лінія витоку конденсатора — окремий, майже пологий спад від V₀
    vleak = v0 + (v1 - v0) * 0.12
    p.append(line(x0, v0, x1, vleak, color=POS, sw=1.8, dash="4,4"))
    p.append(text(x1 - 4, vleak - 6, "лише виток C (віднімаємо)", size=10,
                  color=POS, anchor="end"))

    p.append(text(W / 2, H - 14,
                  "Крута ділянка = пік струму, полога = сон; інтеграл (V₀−V₁) чесний для середнього",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "capacitor-discharge.svg"), W, H, *p)


# ── coulomb-pipeline: конвеєр код→струм→заряд і два краї (дно/стеля) ──────────
# Ідея (proj): один крок лічильника кулонів як ланцюг перетворень одиниць,
# із наголосом ДЕ втрачається дно (мкА за крок округлюються до нуля в грубих
# одиницях) і ДЕ переповнюється стеля (int32 на проміжному добутку).

def fig_coulomb_pipeline():
    W, H = 820, 470
    p = [text(W / 2, 26, "Крок лічильника кулонів: ланцюг одиниць і два краї", size=15, bold=True)]

    # вертикальний ланцюг перетворень
    xc = 250
    boxes = [
        ("code (0..4095)", "код АЦП", "#eef2ff", NEG),
        ("V_adc [мкВ] = code·Vref/4095", "напруга на вході АЦП", FILL, LINE),
        ("V_shunt [нВ] = V_adc·1000 / GAIN", "спад на шунті (÷ підсилення CSA)", FILL, LINE),
        ("I [нА] = V_shunt·1000 / R_мОм", "струм (закон Ома на шунті)", "#eafaf1", FIELD),
        ("I -= offset_nA", "віднімання зсуву (калібр. нуля)", "#fff7e6", "#c08000"),
        ("dQ [пКл] = I·Δt / 1000", "заряд за крок (сума Рімана)", "#eafaf1", FIELD),
        ("charge_pC += dQ   (int64)", "накопичення в 64-бітному лічильнику", "#e8eaf6", NEG),
    ]
    y = 60
    dy = 54
    ys = []
    for i, (main, sub, fill, stroke) in enumerate(boxes):
        b = fitbox(xc - 200, y, 400, 40, main, size=12, fill=fill, stroke=stroke, sw=1.8, bold=True)
        p.append(b)
        p.append(text(xc + 210, y + 17, sub, size=10, color=MUTED, anchor="start"))
        ys.append(y)
        if i < len(boxes) - 1:
            p.append(arrow(xc, y + 40, xc, y + dy, color=INK, sw=1.6))
        y += dy

    # правий стовпчик — два краї
    # ДНО: втрата молодших розрядів
    p.append(rect(560, ys[3] - 6, 250, 96, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(685, ys[3] + 12, "КРАЙ 1 — дно", size=12, color=POS, bold=True))
    p.append(text(685, ys[3] + 30, "мкА за крок у грубих одиницях", size=10, color=INK))
    p.append(text(685, ys[3] + 44, "(мА·год) округлюються в 0 →", size=10, color=INK))
    p.append(text(685, ys[3] + 58, "за годину сну назбирається НУЛЬ.", size=10, color=INK))
    p.append(text(685, ys[3] + 74, "Ліки: копити в пКл (дрібно).", size=10, color=FIELD, bold=True))

    # СТЕЛЯ: переповнення int32 на проміжному добутку
    p.append(rect(560, ys[5] - 6, 250, 96, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(685, ys[5] + 12, "КРАЙ 2 — стеля", size=12, color=POS, bold=True))
    p.append(text(685, ys[5] + 30, "V_adc·1000 ≈ 3.3·10⁹ >", size=10, color=INK))
    p.append(text(685, ys[5] + 44, "INT32_MAX 2.1·10⁹ → переповнення", size=10, color=INK))
    p.append(text(685, ys[5] + 58, "тихо псує проміжний добуток.", size=10, color=INK))
    p.append(text(685, ys[5] + 74, "Ліки: множ у int64, копи в int64.", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 16,
                  "Дрібні одиниці (пКл) рятують дно; 64-бітні проміжки й лічильник рятують стелю",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "coulomb-pipeline.svg"), W, H, *p)


# ── adaptive-dt: адаптивний крок — густо в активній фазі, один доданок у сні ──
# Ідея (proj): активну фазу семплимо часто (багато прямокутників Рімана),
# а довгий сон складаємо ОДНИМ доданком I_сон·T_сон — не будячи АЦП даремно.

def fig_adaptive_dt():
    W, H = 800, 340
    ox, oy = 56, 232
    aw = 690
    top = 70
    base_y = oy - 18
    peak_y = top + 8
    p = [text(W / 2, 26, "Адаптивний крок Δt: густо в активній фазі, один доданок уві сні",
              size=15, bold=True)]
    p.append(line(ox, top - 6, ox, oy, color=LINE))
    p.append(line(ox, oy, ox + aw, oy, color=LINE))
    p.append(text(ox - 6, base_y + 4, "сон", size=9, color=MUTED, anchor="end"))
    p.append(text(ox - 6, peak_y + 4, "пік", size=9, color=MUTED, anchor="end"))

    # розкладка: [активна фаза густо] [ДОВГИЙ сон] [активна фаза густо]
    act1 = (ox + aw * 0.02, ox + aw * 0.24)
    sleep = (act1[1], ox + aw * 0.74)
    act2 = (sleep[1], ox + aw * 0.96)

    # активна фаза 1: сходинка піку + густі прямокутники
    def active(x0, x1, col):
        w = x1 - x0
        xr = x0 + w * 0.30
        xf = xr + w * 0.28
        # профіль
        p.append(line(x0, base_y, xr, base_y, color=NEG, sw=1.6))
        p.append(line(xr, base_y, xr, peak_y, color=POS, sw=1.6))
        p.append(line(xr, peak_y, xf, peak_y, color=POS, sw=2.6))
        p.append(line(xf, peak_y, xf, base_y, color=POS, sw=1.6))
        p.append(line(xf, base_y, x1, base_y, color=NEG, sw=1.6))
        # густі відліки (прямокутники Рімана)
        n = 12
        for i in range(n + 1):
            sx = x0 + w * i / n
            sy = peak_y if xr <= sx <= xf else base_y
            p.append(line(sx, sy, sx, base_y, color=col, sw=0.6, dash="2,3"))
            p.append(circle(sx, sy, 2.2, fill=col, stroke=col, sw=1.0))

    active(*act1, FIELD)
    active(*act2, FIELD)
    p.append(text((act1[0] + act1[1]) / 2, top + 2, "активна фаза", size=10, color=FIELD, bold=True))
    p.append(text((act1[0] + act1[1]) / 2, top + 16, "Δt = 100 мкс (густо)", size=9, color=FIELD))
    p.append(text((act2[0] + act2[1]) / 2, top + 2, "активна фаза", size=10, color=FIELD, bold=True))

    # сон — один широкий прямокутник, ОДИН доданок
    sy = base_y
    p.append(rect(sleep[0], sy, sleep[1] - sleep[0], oy - sy, fill="#eef7ff",
                  stroke=NEG, sw=1.4, rx=2))
    p.append(line(sleep[0], sy, sleep[1], sy, color=NEG, sw=2.2))
    p.append(text((sleep[0] + sleep[1]) / 2, top + 40,
                  "ГЛИБОКИЙ СОН — АЦП вимкнено", size=12, color=NEG, bold=True))
    p.append(text((sleep[0] + sleep[1]) / 2, top + 60,
                  "один доданок: dQ = I_сон · T_сон", size=12, color=NEG))
    p.append(text((sleep[0] + sleep[1]) / 2, top + 78,
                  "(струм сталий — не треба будити чип щокроку)", size=10, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Той самий інтеграл ∫I dt: густа сума там, де струм рветься; один прямокутник там, де сталий",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "adaptive-dt.svg"), W, H, *p)


if __name__ == "__main__":
    fig_why_multimeter_lies()
    fig_correct_measurement()
    fig_profiler_chain()
    fig_profiler_wiring()
    fig_dynamic_range_ladder()
    fig_averaging_aliasing()
    fig_sampling_charge()
    fig_burden_feedback()
    fig_capacitor_discharge()
    fig_coulomb_pipeline()
    fig_adaptive_dt()
    print("OK: figures generated")
