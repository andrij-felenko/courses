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


if __name__ == "__main__":
    fig_why_multimeter_lies()
    fig_correct_measurement()
    fig_profiler_chain()
    fig_profiler_wiring()
    fig_dynamic_range_ladder()
    print("OK: figures generated")
