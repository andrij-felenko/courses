# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-018 — фоторезистор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дільник: фоторезистор угорі, 10 кОм унизу; світло валить R → напруга на S росте ──
def fig_divider_idea():
    W, H = 960, 520
    f = [text(W / 2, 30, "Чому яскравіше = вища напруга: дільник із фоторезистора і сталого 10 кОм",
              size=15, bold=True)]

    def divider(cx, top, bright):
        """Одна колонка дільника. bright=True → LDR малоомний → S близько до +."""
        vcc_y = top
        gnd_y = top + 210
        node_y = (vcc_y + gnd_y) / 2
        # шини
        f.append(line(cx - 70, vcc_y, cx + 70, vcc_y, color=POS, sw=2.2))
        f.append(text(cx, vcc_y - 10, "+  (VCC)", size=11, bold=True, color=POS))
        f.append(line(cx - 70, gnd_y, cx + 70, gnd_y, color=NEG, sw=2.2))
        f.append(text(cx, gnd_y + 22, "−  (GND)", size=11, bold=True, color=NEG))

        # верхнє плече — фоторезистор (LDR) між VCC і вузлом
        f.append(line(cx, vcc_y, cx, node_y - 40, color=INK, sw=1.8))
        ldr_fill = "#fff6d8" if bright else "#e9edf2"
        f.append(rect(cx - 18, node_y - 40, 36, 34, fill=ldr_fill, stroke=INK, sw=1.7, rx=3))
        # стрілочки-світло в бік LDR
        for k in range(3):
            ay = node_y - 34 + k * 10
            f.append(arrow(cx - 62, ay - 6, cx - 22, ay, color=(FIELD if bright else MUTED), sw=1.6))
        f.append(line(cx, node_y - 6, cx, node_y, color=INK, sw=1.8))

        # вузол S
        f.append(circle(cx, node_y, 3.6, fill=INK, stroke=INK, sw=1))
        # вивід S праворуч
        f.append(line(cx, node_y, cx + 70, node_y, color=FIELD, sw=1.8))
        f.append(circle(cx + 70, node_y, 5, fill=BG, stroke=FIELD, sw=2))
        f.append(text(cx + 80, node_y + 4, "S", size=12, bold=True, color=FIELD, anchor="start"))

        # нижнє плече — сталий 10 кОм між вузлом і GND
        f.append(line(cx, node_y, cx, node_y + 40, color=INK, sw=1.8))
        f.append(rect(cx - 18, node_y + 40, 36, 34, fill=BG, stroke=INK, sw=1.7, rx=3))
        f.append(line(cx, node_y + 74, cx, gnd_y, color=INK, sw=1.8))
        f.append(text(cx - 26, node_y + 60, "10 кОм", size=10, color=MUTED, anchor="end"))

        # мітка LDR ліворуч від резистора
        f.append(text(cx - 26, node_y - 20, "LDR", size=10, bold=True, color=INK, anchor="end"))
        return node_y

    # Ліва колонка — темно
    lx = 250
    ny = divider(lx, 80, bright=False)
    b, _, _ = textbox(lx, 360, "ТЕМНО\nопір LDR великий (сотні кОм)\nдільник тягне S донизу\nS ≈ мала напруга → analogRead малий",
                      size=10.5, fill="#eef1f5", stroke=NEG)
    f.append(b)

    # Права колонка — світло
    rx = 690
    ny2 = divider(rx, 80, bright=True)
    b, _, _ = textbox(rx, 360, "СВІТЛО\nопір LDR малий (сотні Ом)\nверхнє плече майже «дріт»\nS ≈ близько до + → analogRead великий",
                      size=10.5, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    # формула дільника внизу окремим блоком
    b, _, _ = textbox(W / 2, 470, "S = VCC · 10кОм / (R_LDR + 10кОм)   —   падає R_LDR, росте частка → росте напруга на S",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "divider-idea.svg"), W, H, *f)


# ── 2. Внутрішня схема KY-018: LDR + 10 кОм = дільник, вихід тільки аналоговий S ────
def fig_ky018_schematic():
    W, H = 900, 470
    f = [text(W / 2, 30, "Що всередині KY-018: фоторезистор і сталий 10 кОм у дільнику напруги",
              size=15, bold=True)]

    bx, by, bw, bh = 120, 66, 660, 300
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-018", size=11, bold=True, color=MUTED, anchor="start"))

    vcc_y = by + 56
    gnd_y = by + bh - 40
    f.append(line(bx + 40, vcc_y, bx + bw - 40, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 40, vcc_y - 10, "+  (VCC 3.3–5 В, середній штир)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(bx + 40, gnd_y, bx + bw - 40, gnd_y, color=NEG, sw=2.2))
    f.append(text(bx + 40, gnd_y + 22, "−  (GND)", size=11, bold=True, color=NEG, anchor="start"))

    node_x = bx + bw * 0.42
    node_y = (vcc_y + gnd_y) / 2

    # верхнє плече: фоторезистор від VCC до вузла
    f.append(line(node_x, vcc_y, node_x, node_y - 46, color=INK, sw=1.8))
    f.append(rect(node_x - 18, node_y - 46, 36, 40, fill="#fff6d8", stroke=INK, sw=1.7, rx=3))
    # промінчики світла
    for k in range(3):
        ay = node_y - 40 + k * 11
        f.append(arrow(node_x - 70, ay - 8, node_x - 22, ay, color=FIELD, sw=1.5))
    f.append(text(node_x - 78, node_y - 44, "світло", size=10, color=FIELD, anchor="end"))
    f.append(text(node_x + 26, node_y - 30, "фоторезистор (LDR)", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(node_x, node_y - 6, node_x, node_y, color=INK, sw=1.8))

    # вузол S
    f.append(circle(node_x, node_y, 3.6, fill=INK, stroke=INK, sw=1))

    # нижнє плече: сталий 10 кОм від вузла до GND
    f.append(line(node_x, node_y, node_x, node_y + 40, color=INK, sw=1.8))
    f.append(rect(node_x - 18, node_y + 40, 36, 40, fill=BG, stroke=INK, sw=1.7, rx=3))
    f.append(text(node_x + 26, node_y + 62, "R  10 кОм (сталий)", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(node_x, node_y + 80, node_x, gnd_y, color=INK, sw=1.8))

    # вивід S праворуч
    f.append(line(node_x, node_y, bx + bw - 40, node_y, color=FIELD, sw=1.8))
    f.append(circle(bx + bw - 40, node_y, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(bx + bw - 30, node_y - 8, "S  (аналоговий вихід)", size=11, bold=True, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 418, "яскравіше → опір LDR падає → вузол S тягнеться до + → напруга на S росте\n"
                                  "лінія S іде на АНАЛОГОВИЙ вхід (АЦП): читаємо не «0/1», а число",
                      size=11, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky018-schematic.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: KY-018 ↔ мікроконтролер, S на АЦП-вхід ────────────
def fig_ky018_wiring():
    W, H = 920, 430
    f = [text(W / 2, 30, "Підключення KY-018: сигнал S — на аналоговий (АЦП) вхід, не на цифровий",
              size=15, bold=True)]

    mx, my, mw, mh = 70, 90, 250, 210
    f.append(rect(mx, my, mw, mh, fill="#fff8e6", stroke=INK, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-018", size=15, bold=True, color=INK))
    f.append(text(mx + mw / 2, my + 48, "фоторезистор", size=10, color=MUTED))
    pads = [("S", FIELD, my + 90), ("+", POS, my + 135), ("−", NEG, my + 180)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    bx, by, bw, bh = 610, 90, 250, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("A0", FIELD, by + 90, "аналоговий вхід (АЦП)"),
            ("3.3–5 В", POS, by + 135, "живлення"),
            ("GND", NEG, by + 180, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    b, _, _ = textbox(W / 2, 372, "S — на АНАЛОГОВИЙ пін (A0 на Uno; будь-який ADC-GPIO на ESP32), читаємо analogRead.\n"
                                  "Живлення (+, середній штир) бери під логіку плати: для ESP32 — 3.3 В, не 5 В.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky018-wiring.svg"), W, H, *f)


# ── 4. Гістерезис: два пороги й «мертва зона» проти блимання на межі ──────────
def fig_hysteresis():
    W, H = 940, 460
    f = [text(W / 2, 30, "Гістерезис: увімкнення й вимкнення на РІЗНИХ порогах — між ними стан не міняється",
              size=14.5, bold=True)]

    # осі: X — час, Y — відлік освітленості
    ax0, ay0 = 90, 90          # верх-ліво графіка
    axw, axh = 640, 250        # ширина/висота поля
    ax1, ay1 = ax0 + axw, ay0 + axh
    f.append(line(ax0, ay0, ax0, ay1, color=INK, sw=1.6))       # вісь Y
    f.append(line(ax0, ay1, ax1, ay1, color=INK, sw=1.6))       # вісь X
    f.append(text(ax0 - 12, ay0 + 6, "світло", size=10, color=MUTED, anchor="end"))
    f.append(text(ax0 - 12, ay1 - 2, "темно", size=10, color=MUTED, anchor="end"))
    f.append(text(ax1, ay1 + 22, "час →", size=11, color=MUTED, anchor="end"))

    # два пороги (Y): вимкнення (світліше, вище) і ввімкнення (темніше, нижче)
    y_off = ay0 + axh * 0.30    # ВИМКНУТИ світло при відліку вище (світло)
    y_on = ay0 + axh * 0.62     # УВІМКНУТИ світло при відліку нижче (темно)
    f.append(line(ax0, y_off, ax1, y_off, color=FIELD, sw=1.4, dash="7 5"))
    f.append(line(ax0, y_on, ax1, y_on, color=POS, sw=1.4, dash="7 5"))
    f.append(text(ax1 + 8, y_off + 4, "поріг ВИМК (400)", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(text(ax1 + 8, y_on + 4, "поріг УВІМК (300)", size=10, bold=True, color=POS, anchor="start"))

    # «мертва зона» між порогами — легка заливка
    f.append(rect(ax0, y_off, axw, y_on - y_off, fill="#fff8e6", stroke="none", sw=0, rx=0))
    f.append(text(ax0 + 12, (y_off + y_on) / 2 + 4, "мертва зона: стан НЕ міняється",
                  size=10, italic=True, color=MUTED, anchor="start"))

    # крива освітленості, що топчеться біля порогів (сутінки з тремтінням)
    import math as _m
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        x = ax0 + t * axw
        # плавний спад із дрібним тремтінням, щоб перетинав зону
        base = ay0 + axh * (0.18 + 0.60 * t)
        jit = 10 * _m.sin(i * 0.9) + 6 * _m.sin(i * 2.3)
        pts.append((x, base + jit))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (poly, INK))

    # позначки перемикань: перше перетинання y_on донизу → УВІМК
    on_x = None
    for (x, y) in pts:
        if y >= y_on:
            on_x = x
            break
    if on_x:
        f.append(line(on_x, ay0, on_x, ay1, color=POS, sw=1.0, dash="2 4"))
        f.append(circle(on_x, y_on, 4, fill=POS, stroke=POS, sw=1))
        f.append(text(on_x, ay1 + 18, "тут увімкнули", size=9.5, bold=True, color=POS))

    # підпис-висновок під графіком, з великим відступом (щоб не накрити вісь)
    b, _, _ = textbox(W / 2, 420,
                      "Без гістерезису один поріг: коли відлік тремтить біля нього — світло нервово блимає.\n"
                      "Два пороги лишають зазор: увімкнули в темряві (нижче 300), вимкнемо аж посвітлішавши (вище 400).",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "hysteresis.svg"), W, H, *f)


# ── 5. Згладжування: сирий тремкий відлік vs експоненційний фільтр (EMA) ──────
def fig_smoothing():
    W, H = 940, 420
    f = [text(W / 2, 30, "Згладжування проти шуму АЦП: сирий відлік тремтить, фільтр веде плавну лінію",
              size=14.5, bold=True)]

    ax0, ay0 = 80, 80
    axw, axh = 700, 220
    ax1, ay1 = ax0 + axw, ay0 + axh
    f.append(line(ax0, ay0, ax0, ay1, color=INK, sw=1.6))
    f.append(line(ax0, ay1, ax1, ay1, color=INK, sw=1.6))
    f.append(text(ax0 - 10, ay0 + 6, "відлік", size=10, color=MUTED, anchor="end"))
    f.append(text(ax1, ay1 + 22, "час →", size=11, color=MUTED, anchor="end"))

    import math as _m
    import random as _r
    _r.seed(7)
    N = 90
    raw = []
    # справжня освітленість — сходинка вгору посередині
    for i in range(N + 1):
        t = i / N
        true_v = 0.35 if t < 0.5 else 0.68
        noise = _r.uniform(-0.09, 0.09)
        raw.append(true_v + noise)

    # EMA: y[i] = y[i-1] + α(x[i] − y[i-1]), α = 0.2
    alpha = 0.2
    ema = [raw[0]]
    for i in range(1, len(raw)):
        ema.append(ema[-1] + alpha * (raw[i] - ema[-1]))

    def toxy(seq):
        out = []
        for i, v in enumerate(seq):
            x = ax0 + (i / N) * axw
            y = ay1 - v * axh
            out.append((x, y))
        return out

    rawxy = toxy(raw)
    emaxy = toxy(ema)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3" opacity="0.55"/>'
             % (" ".join("%.1f,%.1f" % p for p in rawxy), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in emaxy), FIELD))

    # легенда — праворуч угорі поля, з відступом
    lx = ax0 + axw * 0.60
    f.append(line(lx, ay0 + 14, lx + 26, ay0 + 14, color=MUTED, sw=1.3))
    f.append(text(lx + 32, ay0 + 18, "сирий analogRead (тремтить)", size=10, color=MUTED, anchor="start"))
    f.append(line(lx, ay0 + 34, lx + 26, ay0 + 34, color=FIELD, sw=2.4))
    f.append(text(lx + 32, ay0 + 38, "після фільтра (α = 0.2)", size=10, bold=True, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 384,
                      "Фільтр памʼятає попереднє значення й підмішує нове потроху: y ← y + α·(нове − y).\n"
                      "Менший α — гладкіше, але лінива реакція (більша затримка); більший α — жвавіше, але шумніше.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "smoothing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_divider_idea()
    fig_ky018_schematic()
    fig_ky018_wiring()
    fig_hysteresis()
    fig_smoothing()
    print("KY-018 figs done ->", IMG)
