# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-003 / KY-024 — давач Голла».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def block(cx, cy, w, h, s, size=13, fill=FILL, stroke=LINE):
    """Прямокутний блок фіксованої ширини з підписом усередині (fitbox)."""
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, fill=fill, stroke=stroke, sw=1.8)


# ── 1. Внутрішній тракт KY-003 (A3144) ────────────────────────────────────────
def fig_ky003_block():
    W, H = 1200, 330
    f = [text(W / 2, 32, "Усередині A3144 (KY-003): поле → перекид → лише притягання до землі",
              size=15, bold=True)]

    row = 155
    bw, bh = 158, 78
    xs = [135, 355, 575, 800]
    labels = ["пластинка\nГолла", "підсилювач", "тригер\nШмітта", "транзистор\nвідкр. колектор"]
    for x, lab in zip(xs, labels):
        f.append(block(x, row, bw, bh, lab))
    for i in range(len(xs) - 1):
        f.append(arrow(xs[i] + bw / 2, row, xs[i + 1] - bw / 2, row))

    # вхід поля згори в першу клітину
    f.append(text(135, row - bh / 2 - 30, "магнітне поле", size=12, color=FIELD, bold=True))
    f.append(arrow(135, row - bh / 2 - 16, 135, row - bh / 2 - 2, color=FIELD))

    # пояснення під блоками (рознесені, не накладаються)
    f.append(text(355, row + bh / 2 + 26, "мілівольти → вольти", size=11, color=MUTED))
    f.append(text(575, row + bh / 2 + 26, "різкий поріг + гістерезис", size=11, color=MUTED))

    # вихід: S праворуч, підтяжка до «+»
    sx = xs[3] + bw / 2
    node_x = sx + 60
    f.append(line(sx, row, node_x, row))
    f.append(circle(node_x, row, 3.5, fill=INK, stroke=INK))
    # сигнальна лінія тягнеться далі праворуч до підпису S
    f.append(line(node_x, row, node_x + 55, row))
    f.append(text(node_x + 62, row + 5, "S → «0» при магніті", size=12, bold=True, anchor="start"))
    # підтяжка вгору до +
    f.append(line(node_x, row, node_x, row - 58))
    f.append(plus(node_x, row - 68))
    f.append(text(node_x + 20, row - 64, "підтяжка (у МК)", size=10.5, color=MUTED, anchor="start"))
    return W, H, f


# ── 2. Внутрішній тракт KY-024 (49E + LM393) ──────────────────────────────────
def fig_ky024_block():
    W, H = 1000, 400
    f = [text(W / 2, 32, "Усередині KY-024: лінійна 49E → аналог + поріг на LM393",
              size=15, bold=True)]

    # 49E ліворуч
    x49, y49 = 175, 175
    bw, bh = 170, 82
    f.append(block(x49, y49, bw, bh, "49E\nлінійна Голла", stroke=NEG))
    f.append(text(x49, y49 - bh / 2 - 30, "магнітне поле", size=12, color=FIELD, bold=True))
    f.append(arrow(x49, y49 - bh / 2 - 16, x49, y49 - bh / 2 - 2, color=FIELD))
    f.append(text(x49, y49 + bh / 2 + 24, "напруга ≈ ½ живлення у спокої", size=11, color=MUTED))

    # вузол розгалуження
    node_x = x49 + bw / 2 + 70
    f.append(line(x49 + bw / 2, y49, node_x, y49))
    f.append(circle(node_x, y49, 3.5, fill=INK, stroke=INK))

    # верхня гілка → A0 (аналоговий вихід)
    f.append(line(node_x, y49, node_x, 100))
    f.append(arrow(node_x, 100, 815, 100))
    f.append(text(880, 105, "A0 (аналог)", size=12, bold=True, color=NEG))

    # нижня гілка → компаратор
    comp_x, comp_y = 640, 250
    f.append(line(node_x, y49, node_x, comp_y - 18))
    f.append(arrow(node_x, comp_y - 18, comp_x - 95, comp_y - 18))
    f.append(block(comp_x, comp_y, 190, 92, "LM393\nкомпаратор", stroke=INK))
    # другий вхід — поріг з потенціометра
    f.append(text(comp_x, comp_y + 92, "поріг ← гвинтик (потенціометр)", size=11, color=MUTED))
    f.append(arrow(comp_x, comp_y + 78, comp_x, comp_y + 46))

    # вихід компаратора → D0
    f.append(arrow(comp_x + 95, comp_y, 815, comp_y))
    f.append(text(880, comp_y + 5, "D0 (поріг)", size=12, bold=True))
    return W, H, f


# ── 3. Підключення обох модулів ───────────────────────────────────────────────
def fig_wiring():
    W, H = 1020, 470
    f = [text(W / 2, 30, "Підключення до мікроконтролера", size=16, bold=True)]

    # МК-блок посередині-праворуч
    mx, my, mw, mh = 690, 90, 260, 320
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=14))
    f.append(text(mx + mw / 2, my + 30, "мікроконтролер", size=14, bold=True))

    # точки входу на МК
    def mk_pin(y, lab, col=INK):
        f.append(circle(mx, y, 4, fill=col, stroke=col))
        f.append(text(mx + 14, y + 5, lab, size=12, anchor="start", color=col))

    # KY-003 ліворуч зверху
    b1x, b1y, bw, bh = 120, 95, 200, 130
    f.append(rect(b1x, b1y, bw, bh, fill=BG, stroke=NEG, sw=2.2, rx=12))
    f.append(text(b1x + bw / 2, b1y + 26, "KY-003", size=14, bold=True, color=NEG))
    f.append(text(b1x + bw / 2, b1y + 46, "цифровий вимикач", size=10.5, color=MUTED))
    # три ноги KY-003
    p003 = [("S", b1y + 74, POS), ("+  5В", b1y + 96, POS), ("−", b1y + 118, NEG)]
    for lab, y, col in p003:
        f.append(text(b1x + bw - 16, y, lab, size=11.5, anchor="end", color=col))

    # KY-024 ліворуч знизу
    b2x, b2y = 120, 280
    b2w, b2h = 200, 150
    f.append(rect(b2x, b2y, b2w, b2h, fill=BG, stroke=NEG, sw=2.2, rx=12))
    f.append(text(b2x + b2w / 2, b2y + 26, "KY-024", size=14, bold=True, color=NEG))
    f.append(text(b2x + b2w / 2, b2y + 46, "аналог + поріг", size=10.5, color=MUTED))
    p024 = [("A0", b2y + 74, NEG), ("G", b2y + 96, NEG), ("+ 3.3/5В", b2y + 118, POS), ("D0", b2y + 140, INK)]
    for lab, y, col in p024:
        f.append(text(b2x + b2w - 16, y, lab, size=11.5, anchor="end", color=col))

    # Дроти KY-003 → МК
    # S → цифровий вхід (PULLUP)
    y_dig = my + 80
    mk_pin(y_dig, "цифр. вхід (INPUT_PULLUP)", INK)
    f.append(line(b1x + bw, b1y + 74, mx - 40, b1y + 74))
    f.append(line(mx - 40, b1y + 74, mx - 40, y_dig))
    f.append(line(mx - 40, y_dig, mx, y_dig))
    # +5В
    y_v5 = my + 130
    mk_pin(y_v5, "5 В", POS)
    f.append(line(b1x + bw, b1y + 96, mx - 60, b1y + 96, color=POS))
    f.append(line(mx - 60, b1y + 96, mx - 60, y_v5, color=POS))
    f.append(line(mx - 60, y_v5, mx, y_v5, color=POS))
    # GND (спільний)
    y_gnd = my + 180
    mk_pin(y_gnd, "GND", NEG)
    f.append(line(b1x + bw, b1y + 118, mx - 80, b1y + 118, color=NEG))
    f.append(line(mx - 80, b1y + 118, mx - 80, y_gnd, color=NEG))
    f.append(line(mx - 80, y_gnd, mx, y_gnd, color=NEG))

    # Дроти KY-024 → МК
    # A0 → аналоговий вхід
    y_adc = my + 230
    mk_pin(y_adc, "аналог. вхід (АЦП)", NEG)
    f.append(line(b2x + b2w, b2y + 74, mx - 100, b2y + 74, color=NEG))
    f.append(line(mx - 100, b2y + 74, mx - 100, y_adc, color=NEG))
    f.append(line(mx - 100, y_adc, mx, y_adc, color=NEG))
    # G → спільний GND (у той самий вузол)
    f.append(line(b2x + b2w, b2y + 96, mx - 80, b2y + 96, color=NEG))
    f.append(line(mx - 80, b2y + 96, mx - 80, y_gnd, color=NEG))
    # + живлення (у той самий вузол 5В — але підпис 3.3/5)
    f.append(line(b2x + b2w, b2y + 118, mx - 60, b2y + 118, color=POS))
    f.append(line(mx - 60, b2y + 118, mx - 60, y_v5, color=POS))
    # D0 → цифровий вхід
    y_dig2 = my + 280
    mk_pin(y_dig2, "цифр. вхід", INK)
    f.append(line(b2x + b2w, b2y + 140, mx - 120, b2y + 140))
    f.append(line(mx - 120, b2y + 140, mx - 120, y_dig2))
    f.append(line(mx - 120, y_dig2, mx, y_dig2))
    return W, H, f


# ── 4. RPM: імпульси переривання й період між спадними фронтами (для proj-драйвера) ──
def fig_rpm_timing():
    W, H = 1120, 430
    f = [text(W / 2, 30, "Оберти → імпульси: один магніт на колесі, час між фронтами = період",
              size=15, bold=True)]

    y0 = 175            # рівень «1» (нема магніту, підтяжка вгору)
    y1 = 265            # рівень «0» (магніт навпроти → притиснуто)
    xL, xR = 90, 1020
    f.append(text(xL - 12, y0 + 5, "1", size=13, bold=True, anchor="end", color=POS))
    f.append(text(xL - 12, y1 + 5, "0", size=13, bold=True, anchor="end", color=NEG))
    f.append(text(xL - 40, (y0 + y1) / 2, "S", size=12, bold=True, anchor="middle", color=MUTED))

    edges = [180, 470, 760]      # позиції спадних фронтів (магніт зайшов у зону давача)
    pw = 46                       # ширина провалу (магніт перед давачем)
    path = "M %d %d" % (xL, y0)
    for e in edges:
        path += " L %d %d L %d %d L %d %d L %d %d" % (e, y0, e, y1, e + pw, y1, e + pw, y0)
    path += " L %d %d" % (xR, y0)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, INK))

    for e in edges:               # позначки спадних фронтів — те, що ловить FALLING
        f.append(circle(e, y1, 4, fill=NEG, stroke=NEG))
        f.append(text(e, y1 + 26, "FALLING", size=9.5, color=NEG))

    # період T між двома сусідніми фронтами
    ya = 120
    f.append(line(edges[0], y0 - 8, edges[0], ya, color=MUTED, dash="3,3"))
    f.append(line(edges[1], y0 - 8, edges[1], ya, color=MUTED, dash="3,3"))
    f.append(arrow(edges[0], ya, edges[1], ya, color=FIELD))
    f.append(arrow(edges[1], ya, edges[0], ya, color=FIELD))
    f.append(text((edges[0] + edges[1]) / 2, ya - 8, "T (мкс між фронтами)", size=12, bold=True, color=FIELD))

    f.append(text(xL, 70, "магніт на ободі проходить повз давач раз за оберт",
                  size=11.5, color=MUTED, anchor="start"))

    f.append(line(90, 330, W - 90, 330, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 360, "оберт за хвилину:", size=12, color=MUTED))
    f.append(text(W / 2, 392, "RPM = 60 000 000 / T   (T у мкс, один магніт на оберт)", size=15, bold=True))
    return W, H, f


# ── 5. KY-024: нульова лінія, мертва зона, полюс за знаком відхилення (для proj-драйвера) ──
def fig_baseline():
    W, H = 1000, 440
    f = [text(W / 2, 30, "KY-024: відхилення від нульової лінії → сила й полюс", size=15, bold=True)]

    ax = 210                       # x вертикальної осі шкали АЦП
    yTop, yBot = 90, 350
    yMid = (yTop + yBot) / 2        # нульова лінія (≈ ½ шкали)
    dz = 24                        # півширина мертвої зони

    f.append(rect(ax, yMid - dz, W - 120 - ax, 2 * dz, fill="#eef0f3", stroke="none", sw=0))

    f.append(line(ax, yTop, ax, yBot, color=INK, sw=1.8))
    for yy, lab, col, bold in [(yTop, "1023", MUTED, False),
                               (yMid, "≈512", INK, True),
                               (yBot, "0", MUTED, False)]:
        f.append(line(ax - 6, yy, ax, yy, color=INK, sw=1.6))
        f.append(text(ax - 12, yy + 4, lab, size=11, anchor="end", color=col, bold=bold))

    xLineR = W - 120
    f.append(line(ax, yMid, xLineR, yMid, color=INK, sw=1.6, dash="6,4"))

    arx = ax + 70                  # колонка стрілок відхилення (праворуч від осі)
    yN = yTop + 26
    yS = yBot - 26
    f.append(arrow(arx, yMid - dz, arx, yN, color=POS))
    f.append(arrow(arx, yMid + dz, arx, yS, color=NEG))

    tx = arx + 24                  # підписи — усі anchor=start, стрілок і осі не торкаються
    f.append(text(tx, yN + 4, "delta > 0", size=13, color=POS, anchor="start", bold=True))
    f.append(text(tx, yN + 24, "один полюс (N-бік): напруга росте", size=11.5, color=POS, anchor="start"))
    f.append(text(tx, yMid - 6, "мертва зона (шум АЦП)", size=11, color=MUTED, anchor="start"))
    f.append(text(tx, yMid + 14, "|delta| малий → «нема поля»", size=11, color=MUTED, anchor="start"))
    f.append(text(tx, yS - 18, "delta < 0", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(tx, yS + 2, "протилежний полюс (S-бік): напруга падає", size=11.5, color=NEG, anchor="start"))

    f.append(line(120, 392, W - 120, 392, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 420, "delta = analogRead(A0) − baseline   ·   |delta| = сила поля,   знак = полюс",
                  size=13, bold=True))
    return W, H, f


for name, fn in [("ky003-block", fig_ky003_block),
                 ("ky024-block", fig_ky024_block),
                 ("wiring", fig_wiring),
                 ("rpm-timing", fig_rpm_timing),
                 ("baseline", fig_baseline)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
