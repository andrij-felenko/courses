# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Логер споживання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Стенд бачить чистий профіль, поле додає сплески, яких стенд не творить ──
def fig_bench_vs_field():
    W, H = 760, 430
    f = [text(W / 2, 28,
              "Стенд бачить лабораторний профіль; поле додає те, чого стенд не творить",
              size=14.5, bold=True)]

    def panel(px, title, extra_spikes, sub, scol):
        col_w = 320
        ox, oy = px + 18, 300
        top = 78
        span = col_w - 36
        f.append(text(px + col_w / 2, 58, title, size=12.5, bold=True, color=scol))
        f.append(line(ox, oy, ox + span, oy, color=MUTED, sw=1.2))
        f.append(line(ox, oy, ox, top, color=MUTED, sw=1.2))
        f.append(text(ox - 6, top - 4, "I", size=11, color=MUTED, anchor="end"))
        f.append(text(ox + span, oy + 18, "час →", size=10.5, color=MUTED, anchor="end"))

        def y_of(ma):
            return oy - (math.log10(ma + 1) / math.log10(241)) * (oy - top)

        sleep_y = y_of(0.01)
        # рівний фон сну
        f.append(line(ox, sleep_y, ox + span, sleep_y, color=NEG, sw=1.6))
        # один штатний цикл: boot + TX
        def cycle(x0):
            f.append(line(x0, sleep_y, x0, y_of(60), color=POS, sw=1.4))
            f.append(line(x0, y_of(60), x0 + 8, y_of(60), color=POS, sw=1.4))
            f.append(line(x0 + 8, y_of(60), x0 + 8, sleep_y, color=POS, sw=1.4))
            f.append(line(x0 + 22, sleep_y, x0 + 22, y_of(190), color=POS, sw=1.6))
            f.append(line(x0 + 22, y_of(190), x0 + 30, y_of(190), color=POS, sw=1.6))
            f.append(line(x0 + 30, y_of(190), x0 + 30, sleep_y, color=POS, sw=1.6))
        cycle(ox + 40)
        cycle(ox + 150)
        if extra_spikes:
            # поле: довгі ретраї передачі (вищі й ширші), холод підіймає фон
            f.append(line(ox + 40, sleep_y, ox + 110, sleep_y, color="#e08e3c", sw=2.2))
            for xx, w, h in [(ox + 60, 26, 235), (ox + 92, 18, 220),
                             (ox + 200, 30, 240), (ox + 236, 16, 215)]:
                f.append(line(xx, sleep_y, xx, y_of(h), color="#e08e3c", sw=1.8))
                f.append(line(xx, y_of(h), xx + w, y_of(h), color="#e08e3c", sw=1.8))
                f.append(line(xx + w, y_of(h), xx + w, sleep_y, color="#e08e3c", sw=1.8))
        f.append(text(px + col_w / 2, oy + 36, sub, size=10.5, color=MUTED, anchor="middle"))

    panel(30, "(а) на стенді", False,
          "чисто, тепло, сильний сигнал — кілька штатних циклів", NEG)
    panel(380, "(б) у полі: мороз, слабкий сигнал", True,
          "ретраї передачі, фон піднятий холодом — стенд цього не показав", "#c0392b")

    b, _, _ = textbox(W / 2, 406,
                      "Профілювальник лишається на столі; у полі справжній заряд диктують ретраї та холод. Свідок там — лише сам пристрій",
                      size=11, fill="#fff4ec", stroke="#e08e3c")
    f.append(b)
    render(os.path.join(IMG, "bench-vs-field.svg"), W, H, *f)


# ── 2. Шлях даних логера: давач → накопичення заряду → кільце у Flash → дамп ──
def fig_data_path():
    W, H = 780, 430
    f = [text(W / 2, 28,
              "Шлях логера: виміряти струм → накопичити заряд → кільце у Flash → дамп",
              size=14.5, bold=True)]

    y = 120
    boxes = [
        ("шунт + давач\nструму", ["I → число"], FIELD, "#eafaf1"),
        ("вибірка\nз таймера", ["кожні Δt"], NEG, "#eaf0fd"),
        ("акумулятор\nзаряду  ΣI·Δt", ["кулони"], POS, "#fdecea"),
        ("кільце\nу Flash", ["затирає", "найстаріше"], INK, FILL),
    ]
    bx = 30
    bw = 150
    gap = (W - 2 * 30 - len(boxes) * bw) / (len(boxes) - 1)
    centers = []
    for i, (title, sub, col, fill) in enumerate(boxes):
        x = bx + i * (bw + gap)
        f.append(fitbox(x, y, bw, 64, title, size=12.5, bold=True, fill=fill, stroke=col))
        f.append(mtext(x + bw / 2, y + 84, sub, size=10.5, color=MUTED))
        centers.append(x + bw / 2)
        if i:
            f.append(arrow(centers[i - 1] + bw / 2 + 4, y + 32, x - 4, y + 32, color=LINE))

    # знизу: RTC-памʼять зберігає індекс кільця крізь глибокий сон
    ry = 250
    f.append(line(centers[3], y + 64, centers[3], ry, color=MUTED, sw=1.3, dash="4,3"))
    f.append(fitbox(centers[3] - 95, ry, 190, 50,
                    "індекс кільця живе\nв RTC-памʼяті крізь сон", size=11,
                    fill="#fffbe6", stroke="#b8860b"))

    # дамп при події
    f.append(arrow(centers[3] + bw / 2 + 4, y + 32, W - 36, y + 32, color=POS))
    f.append(mtext(W - 40, y - 14, ["дамп при", "події/запиті"], size=10.5,
                   color=POS, anchor="end"))

    # підпис під акумулятором — це і є чесна метрика
    f.append(line(centers[2], y + 100, centers[2], 330, color=MUTED, sw=1.2, dash="4,3"))
    b, _, _ = textbox(centers[2], 352,
                      "Акумулятор робить саме той інтеграл площі, що єдиний чесно міряє автономність",
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "data-path.svg"), W, H, *f)


# ── 3. Підрахунок кулонів: кожна вибірка — тонкий прямокутник I·Δt у суму ──────
def fig_coulomb_counting():
    W, H = 760, 440
    f = [text(W / 2, 28,
              "Підрахунок кулонів: кожна вибірка — стовпчик I·Δt, сума стовпчиків — заряд",
              size=14.5, bold=True)]

    ox, oy = 70, 300
    span = 540
    top = 80
    f.append(line(ox, oy, ox + span, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox - 8, top - 2, "I", size=12, color=MUTED, anchor="end"))
    f.append(text(ox + span, oy + 20, "час →", size=11, color=MUTED, anchor="end"))

    # гладка «справжня» крива струму (один сплеск передачі)
    def curve(t):  # t у [0,1] → струм у мА
        base = 6
        peak = 150 * math.exp(-((t - 0.5) * 6.0) ** 2)
        bump = 28 * math.exp(-((t - 0.18) * 11.0) ** 2)
        return base + peak + bump

    def y_of(ma):
        return oy - (ma / 170.0) * (oy - top)

    # стовпчики вибірок (дискретні Δt)
    n = 18
    for i in range(n):
        t = (i + 0.5) / n
        ma = curve(t)
        x = ox + (i / n) * span
        w = span / n
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                 'fill-opacity="0.28" stroke="%s" stroke-width="1.0"/>'
                 % (x, y_of(ma), w - 1.5, oy - y_of(ma), FIELD, FIELD))

    # сама крива поверх
    pts = []
    for k in range(121):
        t = k / 120.0
        pts.append("%.1f,%.1f" % (ox + t * span, y_of(curve(t))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), POS))

    # позначка одного стовпчика
    xi = ox + (5.5 / n) * span
    f.append(text(xi, y_of(curve(5.5 / n)) - 10, "I·Δt", size=11, bold=True, color=FIELD))
    f.append(text(ox + span * 0.5, top + 4, "справжній I(t)", size=11, color=POS))

    # накопичувач унизу: сходинки суми ростуть
    sy = 360
    f.append(text(ox - 8, sy - 30, "Σ", size=13, bold=True, color=INK, anchor="end"))
    acc = 0.0
    total = sum(curve((i + 0.5) / n) for i in range(n))
    prevx, prevy = ox, sy
    for i in range(n):
        acc += curve((i + 0.5) / n)
        x = ox + ((i + 1) / n) * span
        yv = sy - (acc / total) * 36
        f.append(line(prevx, prevy, x, prevy, color=INK, sw=1.3))
        f.append(line(x, prevy, x, yv, color=INK, sw=1.3))
        prevx, prevy = x, yv
    f.append(text(ox + span + 6, prevy + 4, "= заряд Q", size=11, bold=True,
                  color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 418,
                      "Менший Δt — точніший інтеграл, але більше записів. Сума не скидається в нуль: вона і є накопичений заряд",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "coulomb-counting.svg"), W, H, *f)


# ── 4. Цілочисельний накопичувач: ділимо на ціле + перенос залишку ────────────
def fig_carry_remainder():
    W, H = 770, 430
    f = [text(W / 2, 28,
              "Ціла частина — у підсумок, залишок — у перенос; жодна порція не гине",
              size=14.5, bold=True)]

    # три такти вибірки; у кожному малий приріст мкКл, який сам по собі < одиниці виводу
    ticks = [("такт 1", "+730", "0", "730", "0"),
             ("такт 2", "+730", "730", "1460", "1"),
             ("такт 3", "+730", "460", "1190", "0")]
    # пояснення: одиниця виводу = 1000 мкКл (мілікулон). 730 < 1000 → накопичуємо залишок.
    colx = [70, 250, 420, 590]
    head = ["вибірка", "приріст\nмкКл", "залишок\nдо такту", "сума\nмкКл", "у підсумок\nмКл"]
    hy = 80
    for cx, h in zip(colx, head):
        f.append(mtext(cx, hy, h, size=11.5, bold=True, color=INK))
    rowy = 140
    for i, (lbl, inc, rem0, summ, out) in enumerate(ticks):
        y = rowy + i * 64
        f.append(text(colx[0], y, lbl, size=12, color=MUTED))
        f.append(text(colx[1], y, inc, size=12.5, color=FIELD, bold=True))
        f.append(text(colx[2], y, rem0, size=12.5, color=NEG))
        f.append(text(colx[3], y, summ, size=12.5, color=INK, bold=True))
        # стрілка: ціла частина суми/1000 іде у вивід, решта лишається переносом
        emit_col = POS if out != "0" else MUTED
        f.append(text(colx[3] + 70, y, "÷1000 →", size=10.5, color=MUTED, anchor="start"))
        f.append(circle(colx[3] + 138, y - 4, 13, fill="#fdecea" if out != "0" else FILL,
                        stroke=emit_col, sw=1.6))
        f.append(text(colx[3] + 138, y + 1, out, size=12.5, color=emit_col, bold=True))
        if i < len(ticks) - 1:
            # залишок переноситься в наступний такт похилою стрілкою
            f.append(arrow(colx[2] + 22, y + 12, colx[2] - 18, y + 52, color=NEG, sw=1.4))

    f.append(text(colx[2] + 2, rowy + 3 * 64 - 2, "залишок 190 мкКл живе далі →",
                  size=10.5, color=NEG, anchor="middle"))

    b, _, _ = textbox(W / 2, 400,
                      ["Ділення на 1000 з остачею: ціла частина — у Flash як мілікулони,",
                       "остача лишається в накопичувачі. Викинеш остачу — за тиждень загубиш кулони"],
                      size=11, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "carry-remainder.svg"), W, H, *f)


# ── 5. Кільце у Flash: знайти найновіший запис проходом за лічильником ─────────
def fig_ring_scan():
    W, H = 770, 430
    f = [text(W / 2, 28,
              "Після сну: найновіший запис — той, де лічильник найбільший (тоді стрибок униз)",
              size=14.5, bold=True)]

    cx, cy, R = W / 2, 232, 132
    n = 12
    # у кожній комірці — монотонний лічильник seq; після запису № filled далі стерте (0xFFFF)
    filled = 8
    seqs = []
    for i in range(n):
        seqs.append(str(1000 + i) if i < filled else "FFFF")
    import math as _m
    head_i = filled - 1  # остання записана комірка = найновіша
    for i in range(n):
        a = -_m.pi / 2 + 2 * _m.pi * i / n
        x = cx + R * _m.cos(a)
        y = cy + R * _m.sin(a)
        is_written = i < filled
        col = INK if is_written else MUTED
        fill = FILL if is_written else "#fafafa"
        if i == head_i:
            fill, col = "#fdecea", POS
        f.append(circle(x, y, 26, fill=fill, stroke=col, sw=2 if i == head_i else 1.4))
        f.append(text(x, y - 2, seqs[i], size=10.5, color=col,
                      bold=(i == head_i)))
        f.append(text(x, y + 12, "#%d" % i, size=8.5, color=MUTED))
    # стрілка напрямку запису по колу
    a0 = -_m.pi / 2 + 2 * _m.pi * (head_i + 0.5) / n
    f.append(arrow(cx + (R + 30) * _m.cos(a0 - 0.18), cy + (R + 30) * _m.sin(a0 - 0.18),
                   cx + (R + 30) * _m.cos(a0 + 0.18), cy + (R + 30) * _m.sin(a0 + 0.18),
                   color=NEG, sw=1.6))
    f.append(mtext(cx, cy - 12, ["найновіший —", "де seq падає", "до 0xFFFF"],
                   size=11, color=POS, bold=True))
    f.append(text(cx, cy + 30, "(стерта комірка = порожня)", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 404,
                      ["Монотонний лічильник seq у кожному записі: голова кільця — найбільший seq",
                       "перед стертою коміркою. Так індекс відновлюється навіть без RTC-памʼяті"],
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "ring-scan.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bench_vs_field()
    fig_data_path()
    fig_coulomb_counting()
    fig_carry_remainder()
    fig_ring_scan()
    print("OK: 5 figures ->", IMG)
