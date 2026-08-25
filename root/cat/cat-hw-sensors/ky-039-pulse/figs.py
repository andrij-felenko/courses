# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-039 — давач пульсу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

IR = "#8e44ad"  # інфрачервоний промінь


# ── 1. Просвітна фотоплетизмографія: палець між IR-LED і фототранзистором ──
def fig_ppg():
    W, H = 980, 560
    f = [text(W / 2, 30,
              "Як KY-039 «бачить» пульс: IR-світло проходить крізь палець наскрізь",
              size=16, bold=True)]

    # ── верх: палець між випромінювачем і приймачем ──
    led_x, det_x = 250, 620
    mid_y = 165

    # IR-світлодіод (ліворуч)
    f.append(rect(led_x - 46, mid_y - 34, 44, 68, fill="#f3e8fb", stroke=IR, sw=2, rx=6))
    f.append(text(led_x - 24, mid_y - 44, "IR-LED", size=12, bold=True, color=IR))
    f.append(text(led_x - 24, mid_y + 52, "джерело", size=11, color=MUTED))

    # палець (овал) посередині
    fcx = 435
    f.append(circle(fcx, mid_y, 66, fill="#ffe6d5", stroke="#d98a5a", sw=2))
    f.append(text(fcx, mid_y - 84, "палець", size=12, bold=True, color="#b5673a"))
    # кістка/капіляри натяком
    f.append(circle(fcx, mid_y, 20, fill="#f6c9b0", stroke="#d98a5a", sw=1.3))

    # промені IR крізь палець → приймач
    for k in range(3):
        yy = mid_y - 18 + k * 18
        f.append(arrow(led_x + 2, yy, det_x - 44, yy, color=IR, sw=2))

    # фототранзистор (праворуч)
    f.append(rect(det_x - 2, mid_y - 34, 46, 68, fill="#eafaf0", stroke=FIELD, sw=2, rx=6))
    f.append(text(det_x + 22, mid_y - 44, "фото-", size=12, bold=True, color=FIELD))
    f.append(text(det_x + 22, mid_y - 30, "транзистор", size=12, bold=True, color=FIELD))
    f.append(text(det_x + 22, mid_y + 52, "приймач", size=11, color=MUTED))

    # підпис під верхньою сценою
    f.append(text(fcx, mid_y + 104,
                  "світло проходить наскрізь; кров у пальці ледь-ледь міняє, скільки його дійде",
                  size=12, color=INK))

    # ── низ: пульсова хвиля ──
    base_y = 430
    x0, x1 = 120, 880
    f.append(line(x0, base_y, x1, base_y, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(x0 - 8, base_y + 4, "світло на приймачі", size=11, color=MUTED, anchor="end"))

    pts = []
    n = 260
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        # три удари серця: різкий підйом + повільний спад (типова PPG-форма)
        ph = (t * 3.0) % 1.0
        beat = math.exp(-((ph - 0.18) ** 2) / 0.010) - 0.35 * math.exp(-((ph - 0.42) ** 2) / 0.02)
        y = base_y - 24 - beat * 70
        pts.append((x, y))
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    f.append(f'<path d="{d}" fill="none" stroke="{POS}" stroke-width="2.4"/>')

    # позначки піків = удари
    for b in range(3):
        px = x0 + (x1 - x0) * ((b + 0.18) / 3.0)
        f.append(circle(px, base_y - 24 - 65, 4.5, fill=POS, stroke=POS))
    f.append(text((x0 + x1) / 2, base_y + 44,
                  "кожен гострий пік — один удар серця; відстань між піками задає пульс",
                  size=12, color=INK))
    f.append(text((x0 + x1) / 2, base_y + 66,
                  "корисне пульсування — лічені відсотки сигналу, решта — стала «підсвітка»",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'ppg.svg'), W, H, *f)


# ── 2. Внутрішня схема KY-039: IR-LED через резистор + фототранзистор → аналог S ──
def fig_schematic():
    W, H = 940, 520
    f = [text(W / 2, 30, "Що всередині KY-039: дві прості вітки між + і −",
              size=16, bold=True)]

    vcc_y = 90
    gnd_y = 430
    # шини живлення
    f.append(line(120, vcc_y, 820, vcc_y, color=POS, sw=2.4))
    f.append(text(150, vcc_y - 12, "+  (VCC, 3.3–5 В)", size=12, bold=True, color=POS, anchor="start"))
    f.append(line(120, gnd_y, 820, gnd_y, color=NEG, sw=2.4))
    f.append(text(150, gnd_y + 24, "−  (GND)", size=12, bold=True, color=NEG, anchor="start"))

    # ── ЛІВА вітка: резистор + IR-LED (тільки світить) ──
    lx = 290
    f.append(text(lx - 30, vcc_y + 26, "вітка світла", size=12, bold=True, color=IR, anchor="end"))
    f.append(line(lx, vcc_y, lx, vcc_y + 46, color=INK, sw=1.8))
    # резистор R (обмежує струм світлодіода)
    f.append(rect(lx - 20, vcc_y + 46, 40, 34, fill=BG, stroke=INK, sw=1.7, rx=3))
    f.append(text(lx + 34, vcc_y + 63, "R  ~220 Ом", size=11, color=INK, anchor="start"))
    f.append(line(lx, vcc_y + 80, lx, 250, color=INK, sw=1.8))
    # IR-LED символ
    f.append(rect(lx - 18, 250, 36, 40, fill="#f3e8fb", stroke=IR, sw=2, rx=5))
    f.append(text(lx + 34, 272, "IR-LED", size=11, bold=True, color=IR, anchor="start"))
    for k in range(2):
        f.append(arrow(lx + 20, 258 + k * 12, lx + 44, 250 + k * 12, color=IR, sw=1.6))
    f.append(line(lx, 290, lx, gnd_y, color=INK, sw=1.8))

    # ── ПРАВА вітка: високоомний резистор (верх) + фототранзистор (низ), вузол S між ними ──
    rx = 600
    node_y = 250
    f.append(text(rx + 30, vcc_y + 26, "вітка вимірювання", size=12, bold=True, color=FIELD, anchor="start"))
    # високоомний резистор R_h — верхнє плече (між + і вузлом)
    f.append(line(rx, vcc_y, rx, 150, color=INK, sw=1.8))
    f.append(rect(rx - 20, 150, 40, 34, fill=BG, stroke=INK, sw=1.7, rx=3))
    f.append(text(rx + 36, 167, "R_h  великий", size=11, color=INK, anchor="start"))
    f.append(line(rx, 184, rx, node_y, color=INK, sw=1.8))

    # вузол S
    f.append(circle(rx, node_y, 4, fill=INK, stroke=INK))
    f.append(line(rx, node_y, 780, node_y, color=FIELD, sw=1.9))
    f.append(circle(780, node_y, 5.5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(792, node_y + 4, "S (аналог)", size=12, bold=True, color=FIELD, anchor="start"))

    # фототранзистор — нижнє плече (між вузлом і −)
    f.append(line(rx, node_y, rx, node_y + 40, color=INK, sw=1.8))
    f.append(rect(rx - 20, node_y + 40, 40, 44, fill="#eafaf0", stroke=FIELD, sw=2, rx=5))
    f.append(text(rx + 36, node_y + 58, "фото-", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(rx + 36, node_y + 74, "транзистор", size=11, bold=True, color=FIELD, anchor="start"))
    for k in range(2):
        f.append(arrow(rx - 44, node_y + 50 + k * 12, rx - 20, node_y + 58 + k * 12, color=IR, sw=1.6))
    f.append(line(rx, node_y + 84, rx, gnd_y, color=INK, sw=1.8))

    # пояснення внизу
    f.append(text(W / 2, gnd_y + 62,
                  "Більше світла на фототранзисторі → він сильніше проводить → тягне S униз, до 0 В.",
                  size=12, color=INK))
    f.append(text(W / 2, gnd_y + 82,
                  "Темно → струму мало → S підтягується до +. Вихід S — плавний аналог, читаємо з АЦП.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 3. Розводка пін-у-пін: S на аналоговий вхід, + середній штир, − на GND ──
def fig_wiring():
    W, H = 940, 470
    f = [text(W / 2, 30, "Підключення KY-039: три дроти, сигнал — на аналоговий вхід",
              size=16, bold=True)]

    # плата давача (ліворуч)
    bx, by, bw, bh = 90, 110, 250, 240
    f.append(rect(bx, by, bw, bh, fill="#eef2ff", stroke=NEG, sw=2, rx=10))
    f.append(text(bx + bw / 2, by - 12, "KY-039", size=14, bold=True, color=NEG))
    # чорне віконце (щілина під палець)
    f.append(rect(bx + 20, by + 26, bw - 100, 150, fill="#222", stroke="#111", sw=1.5, rx=6))
    f.append(text(bx + 20 + (bw - 100) / 2, by + 92, "щілина", size=11, color="#eee"))
    f.append(text(bx + 20 + (bw - 100) / 2, by + 110, "під палець", size=11, color="#eee"))
    f.append(text(bx + 20 + (bw - 100) / 2, by + 132, "IR-LED ↕", size=9.5, color="#ccc"))
    f.append(text(bx + 20 + (bw - 100) / 2, by + 146, "фототранзистор", size=9.5, color="#ccc"))

    # гребінка 3 штирі — ВЕРТИКАЛЬНА колонка біля правого краю плати
    pin_rows = [("S", FIELD, "сигнал"), ("+", POS, "живлення"), ("−", NEG, "земля")]
    pin_x = bx + bw - 22
    pin_y0 = by + 56
    pin_dy = 62
    pxs = []
    for i, (lbl, col, note) in enumerate(pin_rows):
        cy = pin_y0 + i * pin_dy
        pxs.append((pin_x, cy, col))
        f.append(circle(pin_x, cy, 8, fill=BG, stroke=col, sw=2.6))
        f.append(text(pin_x - 14, cy + 4, lbl, size=13, bold=True, color=col, anchor="end"))
        f.append(text(pin_x - 30, cy + 4, note, size=9.5, color=MUTED, anchor="end"))

    # мікроконтролер (праворуч)
    mx, my, mw, mh = 640, 110, 220, 240
    f.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=INK, sw=2, rx=10))
    f.append(text(mx + mw / 2, my - 12, "мікроконтролер", size=14, bold=True))
    targets = [
        ("A0  (АЦП-вхід)", FIELD, pin_y0),
        ("3.3 В / 5 В", POS, pin_y0 + pin_dy),
        ("GND", NEG, pin_y0 + 2 * pin_dy),
    ]
    tps = []
    for lbl, col, ty in targets:
        f.append(circle(mx, ty, 7, fill=BG, stroke=col, sw=2.6))
        f.append(text(mx + 16, ty + 4, lbl, size=12, bold=True, color=col, anchor="start"))
        tps.append((mx, ty, col))

    # дроти: кожен штир прямо на свою ціль (однакова висота рядків → прямі лінії, нічого не перетинають)
    for (sx, sy, scol), (tx, ty, _) in zip(pxs, tps):
        f.append(line(sx + 8, sy, tx - 7, ty, color=scol, sw=2.4))

    f.append(text(W / 2, H - 40,
                  "середній штир — живлення (за літерами, не за позицією!)",
                  size=11, color=MUTED))
    f.append(text(W / 2, H - 20,
                  "S → аналоговий пін (A0 на Uno; ADC1-GPIO на ESP32) · + → живлення під логіку плати · − → GND",
                  size=11.5, color=INK))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


BEAT = "#c0392b"   # позначка удару / піка


# ── 4. Конвеєр обробки: сирий відлік → нуль → згладити → піки → BPM ──
def fig_pipeline():
    W, H = 1180, 320
    f = [text(W / 2, 34, "Від сирого відліку до пульсу: пʼять кроків обробки в коді",
              size=16, bold=True)]

    # пʼять блоків-етапів у ряд, стрілки між ними
    labels = [
        ("1. читати", ["analogRead", "рівно за", "таймером ~50 Гц"], "#eef2ff", NEG),
        ("2. прибрати нуль", ["мінус ковзне", "середнє —", "«поточний нуль»"], "#f3e8fb", "#8e44ad"),
        ("3. згладити", ["простий фільтр", "проти дрібного", "шуму"], "#fff7e6", "#b8860b"),
        ("4. знайти піки", ["перетин нуля", "вгору +", "захист 250 мс"], "#eafaf0", FIELD),
        ("5. порахувати", ["beatMs → BPM,", "усереднити", "кілька ударів"], "#fdecea", BEAT),
    ]
    n = len(labels)
    bw, bh = 190, 150
    gap = (W - 60 - n * bw) / (n - 1)
    y = 92
    cx_list = []
    for i, (head, body, fillc, edge) in enumerate(labels):
        x = 30 + i * (bw + gap)
        cx_list.append(x + bw / 2)
        f.append(rect(x, y, bw, bh, fill=fillc, stroke=edge, sw=2, rx=10))
        f.append(text(x + bw / 2, y + 26, head, size=13, bold=True, color=edge))
        for k, ln in enumerate(body):
            f.append(text(x + bw / 2, y + 52 + k * 20, ln, size=11.5, color=INK))
    # стрілки між блоками
    for i in range(n - 1):
        x1 = 30 + i * (bw + gap) + bw
        x2 = x1 + gap
        f.append(arrow(x1 + 4, y + bh / 2, x2 - 4, y + bh / 2, color=INK, sw=2.2))

    f.append(text(W / 2, y + bh + 40,
                  "Кроки 1–3 очищають хвилю; крок 4 — найтонший (не порахувати шум за удар); крок 5 — арифметика.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'pipeline.svg'), W, H, *f)


# ── 5. Ковзне середнє як «поточний нуль»: сирий плавучий сигнал → центрований ──
def fig_baseline():
    W, H = 1060, 560
    f = [text(W / 2, 32, "Ковзне середнє = «поточний нуль»: як відкинути сталу складову",
              size=16, bold=True)]

    x0, x1 = 110, 970
    n = 300

    def beats(t, drift):
        # три удари: різкий підйом + слабкий спад, на повільно плавучому тлі
        ph = (t * 3.0) % 1.0
        b = math.exp(-((ph - 0.16) ** 2) / 0.006) - 0.28 * math.exp(-((ph - 0.40) ** 2) / 0.02)
        return b + drift

    # ── верх: СИРИЙ сигнал (плаває високо) + ковзне середнє крізь нього ──
    top_c = 150
    span = 78
    raw_pts, base_pts = [], []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        drift = 0.55 + 0.45 * math.sin(t * 2.3)     # повільна «підсвітка» пливе
        val = beats(t, drift)
        raw_pts.append((x, top_c - val * span * 0.5))
        # ковзне середнє йде по дрейфу, ігноруючи гострі піки
        base_pts.append((x, top_c - drift * span * 0.5))
    d_raw = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in raw_pts)
    d_base = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in base_pts)
    f.append(f'<path d="{d_raw}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    f.append(f'<path d="{d_base}" fill="none" stroke="{NEG}" stroke-width="2.2" stroke-dasharray="7,5"/>')
    f.append(text(x0 - 10, top_c - 44, "сирий analogRead", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(x1 - 4, top_c + 62, "ковзне середнє (нуль, що пливе)", size=12, bold=True, color=NEG, anchor="end"))

    # ── низ: РІЗНИЦЯ (сирий − нуль): центрована пульсова хвиля навколо 0 ──
    zero_y = 420
    f.append(line(x0, zero_y, x1, zero_y, color=MUTED, sw=1.4, dash="5,5"))
    f.append(text(x0 - 10, zero_y + 4, "0", size=12, bold=True, color=MUTED, anchor="end"))
    ac_pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        drift = 0.55 + 0.45 * math.sin(t * 2.3)
        ac = beats(t, drift) - drift            # рівно та частина, що коливається
        ac_pts.append((x, zero_y - ac * span))
    d_ac = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in ac_pts)
    f.append(f'<path d="{d_ac}" fill="none" stroke="{FIELD}" stroke-width="2.6"/>')
    f.append(text(x0 - 10, zero_y - 70, "сирий − нуль = чиста пульсова хвиля", size=12, bold=True, color=FIELD, anchor="start"))

    # стрілка «відняли»
    f.append(arrow(W / 2, top_c + 92, W / 2, zero_y - 96, color=INK, sw=2))
    f.append(text(W / 2 + 14, (top_c + zero_y) / 2 - 4, "віднімаємо нуль", size=12, bold=True, color=INK, anchor="start"))

    f.append(text(W / 2, H - 26,
                  "Сталу «підсвітку» тканини (повільний дрейф) знімає ковзне середнє; лишається тільки те, що бʼється в такт серцю.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'baseline.svg'), W, H, *f)


# ── 6. Пошук піків: перетин нуля вгору + «глухе» вікно проти подвійного рахунку ──
def fig_peaks():
    W, H = 1060, 470
    f = [text(W / 2, 32, "Надійний пошук піків: перетин нуля вгору + захист від подвійного рахунку",
              size=16, bold=True)]

    x0, x1 = 110, 970
    zero_y = 250
    amp = 120
    n = 340

    # хвиля: три справжні удари + один шумовий горбик між першим і другим
    def wave(t):
        ph = (t * 3.0) % 1.0
        beat = math.exp(-((ph - 0.16) ** 2) / 0.006) - 0.25 * math.exp(-((ph - 0.40) ** 2) / 0.02)
        noise = 0.16 * math.exp(-((t - 0.235) ** 2) / 0.00035)   # дрібний шумовий горбик
        return beat + noise

    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        pts.append((x, zero_y - wave(t) * amp))
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)

    beat_ts = [0.16, 0.50, 0.83]

    # ── ШАР 1 (тло): «глухі» вікна одразу після кожного удару — під усім ──
    for bt in beat_ts:
        bx = x0 + (x1 - x0) * bt
        wx1 = bx + (x1 - x0) * 0.085
        f.append(rect(bx, zero_y - amp - 6, wx1 - bx, amp + 12, fill="#eef0f2", stroke="none", sw=0, rx=4))

    # ── ШАР 2: опорні лінії (нуль і мін. амплітуда) ──
    f.append(line(x0, zero_y, x1, zero_y, color=NEG, sw=1.8, dash="6,5"))
    f.append(text(x1 + 6, zero_y + 4, "нуль", size=12, bold=True, color=NEG, anchor="start"))
    thr_y = zero_y - 0.34 * amp
    f.append(line(x0, thr_y, x1, thr_y, color=MUTED, sw=1.3, dash="3,4"))
    f.append(text(x1 + 6, thr_y + 4, "мін. амплітуда", size=10.5, color=MUTED, anchor="start"))

    # ── ШАР 3: сама хвиля поверх тла й ліній ──
    f.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.4"/>')

    # ── ШАР 4: позначки зарахованих ударів (поверх хвилі) ──
    for bt in beat_ts:
        bx = x0 + (x1 - x0) * bt
        by = zero_y - wave(bt) * amp
        f.append(circle(bx, by, 6, fill=BEAT, stroke=BEAT))
        f.append(text(bx, by - 16, "удар ✓", size=11, bold=True, color=BEAT))
    # підпис глухого вікна (на першому)
    f.append(text(x0 + (x1 - x0) * (0.16 + 0.043), zero_y + amp - 6, "«глухе» ≈250 мс", size=10.5, color=MUTED))

    # шумовий горбик — не зарахований (нижче мін. амплітуди / у глухому вікні)
    nx = x0 + (x1 - x0) * 0.235
    ny = zero_y - wave(0.235) * amp
    f.append(circle(nx, ny, 5.5, fill=BG, stroke=MUTED, sw=2))
    f.append(line(nx - 7, ny - 7, nx + 7, ny + 7, color=MUTED, sw=2))
    f.append(line(nx - 7, ny + 7, nx + 7, ny - 7, color=MUTED, sw=2))
    f.append(text(nx, ny - 16, "шум — відкинуто", size=10.5, bold=True, color=MUTED))

    # інтервал між двома ударами = beatMs
    ax_ = x0 + (x1 - x0) * 0.16
    bx_ = x0 + (x1 - x0) * 0.50
    iy = zero_y + amp + 22
    f.append(arrow(ax_, iy, bx_, iy, color=INK, sw=1.8))
    f.append(arrow(bx_, iy, ax_, iy, color=INK, sw=1.8))
    f.append(text((ax_ + bx_) / 2, iy - 8, "beatMs — час між ударами → BPM = 60000/beatMs", size=12, bold=True, color=INK))

    f.append(text(W / 2, H - 22,
                  "Удар = перший перетин нуля вгору вище мін. амплітуди; після нього — «глухе» вікно, де хвіст і шум не рахуються.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'peaks.svg'), W, H, *f)


if __name__ == "__main__":
    fig_ppg()
    fig_schematic()
    fig_wiring()
    fig_pipeline()
    fig_baseline()
    fig_peaks()
    print("OK: ppg, schematic, wiring, pipeline, baseline, peaks")
