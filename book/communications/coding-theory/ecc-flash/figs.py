# -*- coding: utf-8 -*-
"""Фігури до теми «ECC у флеш-пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
from math import exp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

STEEL = "#3b6fb0"     # дзвони порогів / рівні
STEELF = "#e8eef7"    # світла заливка «сталевого»
AMBER = "#b9770e"     # зношений стан / м'яка інформація
OVL = "#f0aca3"       # заливка зони перекриття (світло-червона)
UNSURE = "#f7d3ce"    # смуга сумніву
SURE = "#cdeae0"      # впевнена смуга


def _bell(cx, sigma, h, base_y, xa, xb, step=2.0):
    """Точки гаусового дзвона (список (x,y)) над лінією base_y."""
    pts, x = [], xa
    while x <= xb + 1e-6:
        y = base_y - h * exp(-((x - cx) ** 2) / (2.0 * sigma * sigma))
        pts.append((x, y))
        x += step
    return pts


def _poly(pts, fill, stroke="none", sw=1.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), fill, stroke, sw, d))


def _overlap(c1, c2, sigma, h, base_y, xa, xb, fill=OVL, step=2.0):
    """Заповнена «лінза» перекриття двох дзвонів = площа під min(дзвін1, дзвін2)."""
    top, x = [], xa
    while x <= xb + 1e-6:
        y1 = h * exp(-((x - c1) ** 2) / (2.0 * sigma * sigma))
        y2 = h * exp(-((x - c2) ** 2) / (2.0 * sigma * sigma))
        top.append((x, base_y - min(y1, y2)))
        x += step
    pts = top + [(xb, base_y), (xa, base_y)]
    return '<polygon points="%s" fill="%s" stroke="none"/>' % (
        " ".join("%.1f,%.1f" % p for p in pts), fill)


def _tail(c, sigma, h, base_y, x0, x1, fill=OVL, step=2.0):
    """Заповнена площа під ОДНИМ дзвоном (центр c) між x0 і x1 — хвіст за лінією."""
    top, x = [], x0
    while x <= x1 + 1e-6:
        y = h * exp(-((x - c) ** 2) / (2.0 * sigma * sigma))
        top.append((x, base_y - y))
        x += step
    pts = top + [(x1, base_y), (x0, base_y)]
    return '<polygon points="%s" fill="%s" stroke="none"/>' % (
        " ".join("%.1f,%.1f" % p for p in pts), fill)


# ── 1. Флеш як аналоговий канал: SLC проти TLC ────────────────────────────────
def fig_levels():
    W, H = 920, 470
    f = [text(W / 2, 30, "Флеш — аналоговий канал під цифровим фасадом", size=17, bold=True)]
    f.append(text(W / 2, 52, "заряд комірки задає поріг напруги; читання розрізає неперервну шкалу на біти — помилки там, де хмарки перекриваються",
                  size=11, color=MUTED, italic=True))

    base = 366

    # ── ліва панель: SLC ──
    f.append(text(245, 92, "SLC — 1 біт на комірку", size=13.5, bold=True, color=STEEL))
    lxa, lxb = 62, 428
    cA, cB, sig, h = 150, 340, 30, 150
    f.append(line(lxa, base, lxb, base, color=INK, sw=1.7))
    f.append(_poly(_bell(cA, sig, h, base, lxa, lxb), "none", STEEL, 2.4))
    f.append(_poly(_bell(cB, sig, h, base, lxa, lxb), "none", STEEL, 2.4))
    # опорна лінія у чистому проміжку
    f.append(line(245, base, 245, base - 176, color=FIELD, sw=1.8, dash="6 4"))
    f.append(text(245, base - 186, "опорна лінія", size=10.5, color=FIELD, bold=True))
    # позначки станів
    f.append(text(150, base + 20, "стерта (1)", size=10.5, color=INK))
    f.append(text(340, base + 20, "записана (0)", size=10.5, color=INK))
    # зелений двобічний маркер «чистий проміжок»
    f.append(line(196, base - 44, 294, base - 44, color=FIELD, sw=1.5))
    f.append(line(196, base - 49, 196, base - 39, color=FIELD, sw=1.5))
    f.append(line(294, base - 49, 294, base - 39, color=FIELD, sw=1.5))
    f.append(text(245, base - 54, "чистий проміжок → 0 помилок", size=10, color=FIELD, bold=True))
    f.append(text(lxb, base + 40, "поріг напруги Vth →", size=11, color=INK, anchor="end", bold=True))

    # роздільник панелей
    f.append(line(462, 84, 462, base + 30, color="#dddddd", sw=1.2))

    # ── права панель: TLC ──
    f.append(text(690, 92, "TLC — 3 біти на комірку (8 рівнів)", size=13.5, bold=True, color=STEEL))
    rxa, rxb = 496, 884
    n = 8
    c0, dx = 520, 48
    centers = [c0 + i * dx for i in range(n)]
    sig2, h2 = 16.5, 120
    # спершу — заливка перекриттів (під дзвонами)
    for i in range(n - 1):
        f.append(_overlap(centers[i], centers[i + 1], sig2, h2, base, centers[i], centers[i + 1]))
    # опорні лінії між рівнями (тонкі, приглушені)
    for i in range(n - 1):
        xm = (centers[i] + centers[i + 1]) / 2
        f.append(line(xm, base, xm, base - h2 - 6, color=MUTED, sw=0.8, dash="3 3"))
    # дзвони
    for c in centers:
        f.append(_poly(_bell(c, sig2, h2, base, rxa, rxb), "none", STEEL, 2.0))
    f.append(line(rxa, base, rxb, base, color=INK, sw=1.7))
    f.append(text(rxb, base + 40, "поріг напруги Vth →", size=11, color=INK, anchor="end", bold=True))
    f.append(text(690, base + 20, "8 тісних рівнів у тому самому діапазоні", size=10.5, color=MUTED))

    # виноска на зону перекриття
    lens_x = (centers[3] + centers[4]) / 2
    f.append(text(690, 128, "перекриття хвостів → биті біти", size=11.5, color=POS, bold=True))
    f.append(line(690, 136, lens_x, base - 20, color=POS, sw=1.2))
    f.append(circle(lens_x, base - 20, 3.2, fill=POS, stroke=BG, sw=1.2))

    render(os.path.join(IMG, "levels-overlap.svg"), W, H, *f)


# ── 2. Чому RBER росте: пороги розповзаються ──────────────────────────────────
def fig_drift():
    W, H = 920, 500
    f = [text(W / 2, 30, "Чому фон помилок росте: пороги розповзаються", size=17, bold=True)]
    f.append(text(W / 2, 52, "знос, витікання й збурення читанням розширюють і зсувають дзвони, аж поки хвости перелізуть опорну лінію",
                  size=11, color=MUTED, italic=True))

    base = 392
    xa, xb = 92, 828
    ref = 452
    f.append(line(xa, base, xb, base, color=INK, sw=1.7))
    f.append(text(xb, base + 40, "поріг напруги Vth →", size=11, color=INK, anchor="end", bold=True))

    # опорна лінія
    f.append(line(ref, base, ref, 150, color=FIELD, sw=1.8, dash="6 4"))
    f.append(text(ref, 142, "опорна лінія", size=10.5, color=FIELD, bold=True))

    # свіжі дзвони (суцільні, вузькі)
    cA, cB, sig, h = 322, 566, 26, 156
    f.append(_poly(_bell(cA, sig, h, base, xa, xb), "none", STEEL, 2.4))
    f.append(_poly(_bell(cB, sig, h, base, xa, xb), "none", STEEL, 2.4))

    # зношені дзвони (штрихові, ширші, зсунуті всередину)
    cA2, cB2, sig2, h2 = 360, 528, 44, 118
    f.append(_overlap(cA2, cB2, sig2, h2, base, cA2, cB2, fill=OVL))
    f.append(_poly(_bell(cA2, sig2, h2, base, xa, xb), "none", AMBER, 2.2, dash="7 4"))
    f.append(_poly(_bell(cB2, sig2, h2, base, xa, xb), "none", AMBER, 2.2, dash="7 4"))

    # легенда «свіжий / зношений»
    f.append(line(120, 138, 156, 138, color=STEEL, sw=2.4))
    f.append(text(162, 142, "свіжий чип: вузькі дзвони", size=10.5, color=STEEL, anchor="start", bold=True))
    f.append(line(120, 160, 156, 160, color=AMBER, sw=2.2, dash="7 4"))
    f.append(text(162, 164, "зношений чип: ширші + зсунуті", size=10.5, color=AMBER, anchor="start", bold=True))

    # стрілки-механізми: розповзання й зсув
    f.append(arrow(cA, base - h - 14, cA2 + 30, base - h2 - 8, color=MUTED, sw=1.4))
    f.append(text(300, base - h - 24, "знос → дзвін ширшає", size=10, color=MUTED, anchor="middle"))
    f.append(arrow(600, 250, 545, 250, color=MUTED, sw=1.4))
    f.append(text(660, 254, "витікання → зсув", size=10, color=MUTED, anchor="middle"))

    # виноска на червону лінзу
    f.append(text(452, 300, "хвости перелізли опорну лінію", size=11.5, color=POS, bold=True))
    f.append(text(452, 318, "→ нові помилки", size=11.5, color=POS, bold=True))
    f.append(line(452, 326, 452, base - 26, color=POS, sw=1.2))
    f.append(circle(452, base - 26, 3.2, fill=POS, stroke=BG, sw=1.2))

    # нижня смуга: три механізми
    f.append(rect(92, 448, 736, 34, fill=FILL, stroke=INK, sw=1.3, rx=10))
    f.append(text(W / 2, 470, "розповзання жене троє: знос стиранням · витікання заряду з часом · збурення читанням",
                  size=11.5, color=INK, bold=True))

    render(os.path.join(IMG, "drift-mechanisms.svg"), W, H, *f)


# ── 3. Тверде проти м'якого рішення ───────────────────────────────────────────
def fig_hard_soft():
    W, H = 940, 480
    f = [text(W / 2, 30, "Тверде рішення викидає те, що м'яке зберігає", size=17, bold=True)]
    f.append(text(W / 2, 52, "звичайне читання дає голий біт; кілька зсунутих перечитувань дають ще й певність — і нею живиться LDPC",
                  size=11, color=MUTED, italic=True))

    base = 372
    sig, h = 34, 150

    # ── ліва панель: тверде рішення ──
    f.append(text(250, 92, "Тверде рішення — 1 читання", size=13, bold=True, color=INK))
    lxa, lxb = 64, 456
    cA, cB = 176, 344
    ref = 260
    f.append(line(lxa, base, lxb, base, color=INK, sw=1.7))
    f.append(_poly(_bell(cA, sig, h, base, lxa, lxb), "none", STEEL, 2.3))
    f.append(_poly(_bell(cB, sig, h, base, lxa, lxb), "none", STEEL, 2.3))
    f.append(line(ref, base, ref, 128, color=FIELD, sw=1.8, dash="6 4"))
    f.append(text(ref, 120, "одна опорна лінія", size=10.5, color=FIELD, bold=True))
    # дві комірки: глибока й гранична — обидві дають той самий біт
    yd = base - h * exp(-((150 - cA) ** 2) / (2 * sig * sig))
    yn = base - h * exp(-((248 - cA) ** 2) / (2 * sig * sig))
    f.append(circle(150, yd, 5.2, fill=NEG, stroke=BG, sw=1.5))
    f.append(text(150, yd - 12, "глибоко", size=10, color=NEG, bold=True))
    f.append(circle(248, yn, 5.2, fill=POS, stroke=BG, sw=1.5))
    f.append(text(250, base - 150, "майже на межі", size=10, color=POS, bold=True))
    f.append(line(248, yn, 250, base - 142, color=POS, sw=1))
    f.append(fitbox(96, base + 22, 320, 32, "обидві → той самий біт: різниця в певності згубилась",
                    size=10.5, color=INK, fill="#fbeeec", stroke=POS, sw=1.3))

    # роздільник
    f.append(line(478, 84, 478, base + 30, color="#dddddd", sw=1.2))

    # ── права панель: м'яке рішення ──
    f.append(text(706, 92, "М'яке рішення — кілька зсунутих читань", size=13, bold=True, color=INK))
    rxa, rxb = 500, 892
    cA2, cB2 = 612, 780
    refc = 696
    offs = [-46, -22, 0, 22, 46]           # зсунуті опорні лінії (read-retry)
    lines_x = [refc + o for o in offs]
    top_band = 150
    edges = [refc - 68] + lines_x + [refc + 68]   # 7 меж → 6 смуг
    # зовнішні дві смуги — «впевнено» (зелені), внутрішні чотири — «сумнів» (червоні)
    band_fill = [SURE, UNSURE, UNSURE, UNSURE, UNSURE, SURE]
    for i in range(len(edges) - 1):
        x0, x1 = edges[i], edges[i + 1]
        f.append(rect(x0, top_band, x1 - x0, base - top_band, fill=band_fill[i], stroke="none", rx=0))
    # дзвони поверх смуг
    f.append(_poly(_bell(cA2, sig, h, base, rxa, rxb), "none", STEEL, 2.3))
    f.append(_poly(_bell(cB2, sig, h, base, rxa, rxb), "none", STEEL, 2.3))
    # зсунуті опорні лінії
    for x in lines_x:
        f.append(line(x, base, x, top_band, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(refc, top_band - 10, "5 зсунутих читань → смуги певності", size=10.5, color=MUTED, bold=True))
    # підписи смуг
    f.append(text(refc, base - 12, "сумнів", size=10, color=POS, bold=True))
    f.append(text(refc - 96, base - 12, "певно", size=10, color=FIELD, bold=True))
    f.append(text(refc + 96, base - 12, "певно", size=10, color=FIELD, bold=True))
    # ті самі дві комірки
    yd2 = base - h * exp(-((586 - cA2) ** 2) / (2 * sig * sig))
    yn2 = base - h * exp(-((684 - cA2) ** 2) / (2 * sig * sig))
    f.append(circle(586, yd2, 5.2, fill=NEG, stroke=BG, sw=1.5))
    f.append(text(586, yd2 - 12, "глибоко → 0 певно", size=10, color=NEG, bold=True))
    f.append(circle(684, yn2, 5.2, fill=POS, stroke=BG, sw=1.5))
    f.append(text(700, base - 150, "на межі → 0 непевно", size=10, color=POS, bold=True))
    f.append(line(684, yn2, 700, base - 142, color=POS, sw=1))
    f.append(fitbox(540, base + 22, 320, 32, "кожна комірка дістає біт + міру довіри → вхід для LDPC",
                    size=10.5, color=INK, fill="#eef6f1", stroke=FIELD, sw=1.3))

    render(os.path.join(IMG, "hard-vs-soft.svg"), W, H, *f)


def _pill(cx, cy, s, size=11, color=INK, stroke=None, fill=BG, bold=False):
    """Маленька «пігулка» з написом — рамка сама під текст (textbox повертає кортеж)."""
    return textbox(cx, cy, s, size=size, pad=6, fill=fill,
                   stroke=stroke or color, sw=1.2, color=color, bold=bold, rx=8)[0]


# ── 4. Полиця кодів була готова ще до флешу (історія-ескалація) ────────────────
def fig_code_shelf():
    W, H = 980, 560
    f = [text(W / 2, 30, "Полиця кодів була готова ще до флешу", size=17, bold=True)]
    f.append(text(W / 2, 52, "усі три коди винайшли в 1950–1963 рр.; флеш наступні пів століття лише сходив полицею вниз, беручи щоразу глибший код",
                  size=11, color=MUTED, italic=True))

    def yx(yr):
        return 100 + (yr - 1945) * 10.649

    ax = 300
    f.append(line(100, ax, 920, ax, color=INK, sw=1.6))
    for yr in range(1950, 2021, 10):
        xx = yx(yr)
        f.append(line(xx, ax - 5, xx, ax + 5, color=MUTED, sw=1.0))
        f.append(text(xx, ax + 20, str(yr), size=10, color=MUTED))

    f.append(text(104, 92, "ПОЛИЦЯ КОДІВ  (усі готові до 1963)", size=12, bold=True, color=STEEL, anchor="start"))
    f.append(text(104, 452, "ФЛЕШ КЛИЧЕ  (щоразу глибший код)", size=12, bold=True, color=AMBER, anchor="start"))

    yc = 182
    # коди на полиці
    xH, xB, xL = yx(1950), yx(1960), yx(1963)
    f.append(_pill(182, 138, "Код Геммінга · 1950", color=MUTED))
    f.append(line(182, 150, xH, yc - 7, color=MUTED, sw=1.0, dash="2 2"))
    f.append(circle(xH, yc, 6.2, fill=BG, stroke=MUTED, sw=2.4))
    f.append(_pill(312, 104, "BCH · 1959–1960", color=AMBER))
    f.append(line(312, 116, xB, yc - 7, color=AMBER, sw=1.0, dash="2 2"))
    f.append(circle(xB, yc, 6.2, fill=BG, stroke=AMBER, sw=2.4))
    f.append(_pill(452, 150, "LDPC · 1960–1963", color=FIELD))
    f.append(line(452, 162, xL, yc - 7, color=FIELD, sw=1.0, dash="2 2"))
    f.append(circle(xL, yc, 6.2, fill=BG, stroke=FIELD, sw=2.4))

    yfl = 402
    xSLC, xMLC, xTLC, xQLC = yx(1987), yx(1997), yx(2010), yx(2015)
    f.append(arrow(xH, yc + 9, xSLC, yfl - 9, color=MUTED, sw=1.6))
    f.append(arrow(xB, yc + 9, xMLC, yfl - 9, color=AMBER, sw=1.6))
    f.append(arrow(xL, yc + 9, xTLC, yfl - 9, color=FIELD, sw=1.6))

    f.append(circle(xSLC, yfl, 6.2, fill=BG, stroke=MUTED, sw=2.4))
    f.append(_pill(xSLC, 472, "SLC — NAND 1987", color=MUTED))
    f.append(text(xSLC, 496, "1 біт · тихий канал", size=9.5, color=MUTED))
    f.append(circle(xMLC, yfl, 6.2, fill=BG, stroke=AMBER, sw=2.4))
    f.append(_pill(xMLC, 472, "MLC 1996–1997", color=AMBER))
    f.append(text(xMLC, 496, "2 біти · фон стрибнув", size=9.5, color=AMBER))
    f.append(circle(xTLC, yfl, 6.2, fill=BG, stroke=FIELD, sw=2.4))
    f.append(circle(xQLC, yfl, 5.0, fill=BG, stroke=FIELD, sw=1.9))
    f.append(_pill(xTLC + 24, 472, "TLC 2010 · далі QLC / 3D", color=FIELD))
    f.append(text(xTLC + 24, 496, "3–4 біти · шумно", size=9.5, color=FIELD))

    f.append(_pill(332, 250, "≈ 37 років на полиці", size=10, color=MUTED))
    f.append(_pill(457, 344, "≈ 37 років", size=10, color=AMBER))
    f.append(_pill(586, 256, "≈ 47 років", size=10, color=FIELD))

    f.append(fitbox(150, 520, 680, 32,
                    "Полицю заповнили до 1963-го. Флеш не гнав винахід уперед — він сам робив свій канал шумнішим і брав дедалі глибший код.",
                    size=11, color=INK, fill=STEELF, stroke=STEEL, sw=1.2))

    render(os.path.join(IMG, "code-shelf-timeline.svg"), W, H, *f)


# ── 5. Сходи ескалації: щільніша комірка → міцніший код ───────────────────────
def fig_escalation():
    W, H = 980, 540
    f = [text(W / 2, 30, "Сходи ескалації: дешевша комірка — міцніший код", size=17, bold=True)]
    f.append(text(W / 2, 52, "кожен біт, доданий у комірку, згущує фон помилок і жене галузь на щабель глибший у коді",
                  size=11, color=MUTED, italic=True))

    f.append(arrow(70, 470, 950, 470, color=MUTED, sw=1.5))
    f.append(text(560, 492, "щільніша комірка · дешевший біт →", size=11, color=MUTED))
    f.append(arrow(70, 470, 70, 96, color=MUTED, sw=1.5))
    f.append(text(80, 90, "густіший фон помилок ↑", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(316, 92, 400, 30, "що дешевша пам'ять, то міцніший код мусить її рятувати",
                    size=11, color=INK, fill=BG, stroke=MUTED, sw=1.1))

    def step(x, y, cell, sub, rber, code, cc):
        w, h = 196, 104
        s = rect(x, y, w, h, fill=STEELF, stroke=STEEL, sw=1.6, rx=12)
        s += text(x + w / 2, y + 26, cell, size=15, bold=True, color=STEEL)
        s += text(x + w / 2, y + 46, sub, size=10.5, color=MUTED)
        s += text(x + w / 2, y + 68, rber, size=11, color=INK)
        s += text(x + w / 2, y + 90, "код: " + code, size=12.5, bold=True, color=cc)
        return s

    f.append(step(96, 348, "SLC · 1 біт", "широкий чистий проміжок", "RBER ~ 10⁻⁶…10⁻⁴", "Геммінг", MUTED))
    f.append(step(320, 278, "MLC · 2 біти", "проміжки вдвічі тісніші", "RBER ~ 10⁻³", "BCH", AMBER))
    f.append(step(544, 208, "TLC · 3 біти", "вісім тісних рівнів", "RBER ~ 10⁻²", "LDPC", FIELD))
    f.append(step(768, 138, "QLC · 4 біти", "шістнадцять рівнів", "RBER > 10⁻²", "LDPC + м'яке", FIELD))

    f.append(arrow(292, 400, 320, 340, color=INK, sw=1.4))
    f.append(arrow(516, 330, 544, 270, color=INK, sw=1.4))
    f.append(arrow(740, 260, 768, 200, color=INK, sw=1.4))

    render(os.path.join(IMG, "escalation-staircase.svg"), W, H, *f)


# ── 6. Числова розплата: WER тверде проти м'якого (до proj-soft-read) ─────────
def fig_soft_gain():
    from math import erfc, sqrt, comb, log10
    W, H = 860, 560
    XL, XW, YT, YH = 122, 648, 98, 344
    XR, YB = XL + XW, YT + YH
    lo_r, hi_r = -3.0, -1.0      # RBER: 10⁻³ … 10⁻¹ (вісь x, лог)
    NW = 9                        # WER: 1 … 10⁻⁹ (вісь y, лог)

    def xm(rb):
        return XL + (log10(rb) - lo_r) / (hi_r - lo_r) * XW

    def ym(w):
        return YT + (-log10(w)) / NW * YH

    def Qf(x):
        return 0.5 * erfc(x / sqrt(2))

    def qinv(p):
        a, b = 0.0, 15.0
        for _ in range(120):
            m = 0.5 * (a + b)
            if Qf(m) > p:
                a = m
            else:
                b = m
        return 0.5 * (a + b)

    N = 5
    hard = lambda rb: sum(comb(N, k) * rb**k * (1-rb)**(N-k) for k in range(N//2+1, N+1))
    soft = lambda rb: Qf(sqrt(N) * qinv(rb))
    uncoded = lambda rb: rb

    f = [text(W/2, 30, "М'яке рішення виграє на тому самому каналі", size=17, bold=True)]
    f.append(text(W/2, 52, "та сама пам'ять (5 комірок на біт) — різниця лише в тім, чи декодер бачить певність, чи лише голий біт",
                  size=11, color=MUTED, italic=True))

    # рамка графіка
    f.append(rect(XL, YT, XW, YH, fill=BG, stroke=INK, sw=1.4, rx=0))

    # горизонтальні лінії-декади WER + підписи
    ylab = ["1", "10⁻¹", "10⁻²", "10⁻³", "10⁻⁴", "10⁻⁵", "10⁻⁶", "10⁻⁷", "10⁻⁸", "10⁻⁹"]
    for i in range(NW + 1):
        yy = YT + i / NW * YH
        f.append(line(XL, yy, XR, yy, color="#e6e6e6", sw=1.0))
        f.append(text(XL - 10, yy + 4, ylab[i], size=10, color=MUTED, anchor="end"))
    # вертикальні лінії-декади RBER
    xlab = {-3: "10⁻³", -2: "10⁻²", -1: "10⁻¹"}
    for e in (-3, -2, -1):
        xx = xm(10.0**e)
        f.append(line(xx, YT, xx, YB, color="#e6e6e6", sw=1.0))
        f.append(text(xx, YB + 20, xlab[e], size=10.5, color=MUTED))
    # осі підписи
    f.append(text((XL+XR)/2, YB + 44, "сирий фон помилок RBER →", size=11.5, color=INK, bold=True))
    yc = (YT + YB) / 2
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (XL - 52, yc, FONT, INK, XL - 52, yc, "частка невиправних слів (WER)"))

    def curve(fn, color, sw, dash=None):
        pts, x = [], lo_r
        while x <= hi_r + 1e-9:
            rb = 10.0**x
            w = fn(rb)
            if 1e-9 <= w <= 1.0:
                pts.append((xm(rb), ym(w)))
            x += (hi_r - lo_r) / 90.0
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
                'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))

    f.append(curve(uncoded, MUTED, 2.0, dash="6 4"))
    f.append(curve(hard, STEEL, 2.8))
    f.append(curve(soft, AMBER, 2.8))

    # робоча точка RBER = 0.05 + дужка розриву
    xo = xm(0.05)
    yh, ys = ym(hard(0.05)), ym(soft(0.05))
    f.append(line(xo, YT, xo, YB, color=INK, sw=1.0, dash="2 4"))
    f.append(line(xo, yh, xo, ys, color=POS, sw=2.2))
    f.append(line(xo-5, yh, xo+5, yh, color=POS, sw=2.2))
    f.append(line(xo-5, ys, xo+5, ys, color=POS, sw=2.2))
    f.append(text(xo + 12, (yh+ys)/2 + 4, "≈ 10×", size=12, color=POS, bold=True, anchor="start"))

    # легенда (верхній лівий кут — там порожньо)
    lx, ly = XL + 30, YT + 26
    f.append(line(lx, ly, lx+30, ly, color=MUTED, sw=2.0, dash="6 4"))
    f.append(text(lx+38, ly+4, "без коду — 1 комірка на біт", size=10.5, color=MUTED, anchor="start"))
    f.append(line(lx, ly+22, lx+30, ly+22, color=STEEL, sw=2.8))
    f.append(text(lx+38, ly+26, "тверде: більшість голосів (5 комірок)", size=10.5, color=STEEL, anchor="start", bold=True))
    f.append(line(lx, ly+44, lx+30, ly+44, color=AMBER, sw=2.8))
    f.append(text(lx+38, ly+48, "м'яке: сума певностей (5 комірок)", size=10.5, color=AMBER, anchor="start", bold=True))

    f.append(fitbox(XL, YB + 58, XW, 46,
                    "Ті самі 5 комірок на біт. Тверде рахує голоси, м'яке підсумовує певності —\n"
                    "і лишає вдесятеро менше невиправних слів. Ліворуч (тихіший канал) розрив ще ширший.",
                    size=10.5, color=INK, fill=STEELF, stroke=STEEL, sw=1.1))

    render(os.path.join(IMG, "soft-gain-curve.svg"), W, H, *f)


# ── 7. Геометрія хвоста: звідки береться RBER = Q(d/2σ) ───────────────────────
def fig_qtail():
    W, H = 960, 500
    f = [text(W / 2, 30, "Звідки береться RBER: геометрія двох дзвонів і лінії", size=17, bold=True)]
    f.append(text(W / 2, 52, "проміжок d між серединами, спільна ширина σ, опорна лінія посередині; заштрихований хвіст — площа Q(z)",
                  size=11, color=MUTED, italic=True))

    base = 366
    xa, xb = 60, 900
    cx1, cx2 = 268, 600
    sigma, h = 82, 150
    line_x = (cx1 + cx2) / 2.0     # опорна лінія посередині: d/2 від кожної середини

    # вісь
    f.append(line(xa, base, xb, base, color=INK, sw=1.6))
    f.append(text(xb, base + 38, "поріг напруги Vth →", size=11, color=INK, anchor="end", bold=True))

    # заштрихований правий хвіст НИЖНЬОГО дзвона за лінією = Q(z)
    tail_xb = min(xb, cx1 + 4.6 * sigma)
    f.append(_tail(cx1, sigma, h, base, line_x, tail_xb, fill=OVL))

    # самі дзвони (поверх заливки)
    f.append(_poly(_bell(cx1, sigma, h, base, xa, xb), "none", STEEL, 2.4))
    f.append(_poly(_bell(cx2, sigma, h, base, xa, xb), "none", STEEL, 2.4))

    # середини рівнів
    f.append(line(cx1, base, cx1, base + 8, color=STEEL, sw=1.6))
    f.append(text(cx1, base + 26, "μ₀ — нижній рівень", size=11, color=STEEL, bold=True))
    f.append(line(cx2, base, cx2, base + 8, color=STEEL, sw=1.6))
    f.append(text(cx2, base + 26, "μ₁ — верхній рівень", size=11, color=STEEL, bold=True))

    # опорна лінія L
    f.append(line(line_x, base, line_x, 150, color=FIELD, sw=1.8, dash="6 4"))
    f.append(text(line_x, 140, "опорна лінія L", size=11, color=FIELD, bold=True))

    # дужка проміжку d (між μ0 і μ1), над дзвонами
    dy = base - h - 46
    f.append(line(cx1, dy, cx2, dy, color=INK, sw=1.3))
    f.append(line(cx1, dy - 6, cx1, dy + 6, color=INK, sw=1.3))
    f.append(line(cx2, dy - 6, cx2, dy + 6, color=INK, sw=1.3))
    f.append(text((cx1 + cx2) / 2.0, dy - 12, "d — проміжок середин", size=11, color=INK, bold=True))

    # дужка половини проміжку d/2 = zσ (μ0 до лінії), нижче першої
    d2y = base - h - 18
    f.append(line(cx1, d2y, line_x, d2y, color=MUTED, sw=1.2))
    f.append(line(cx1, d2y - 5, cx1, d2y + 5, color=MUTED, sw=1.2))
    f.append(line(line_x, d2y - 5, line_x, d2y + 5, color=MUTED, sw=1.2))
    f.append(text((cx1 + line_x) / 2.0, d2y + 18, "d/2 = zσ", size=10.5, color=MUTED, bold=True))

    # позначка ширини σ на нижньому дзвоні (від середини до перегину)
    sx = cx1 + sigma
    sy = base - h * exp(-0.5)
    f.append(line(cx1, sy, sx, sy, color=AMBER, sw=1.4, dash="3 3"))
    f.append(text((cx1 + sx) / 2.0, sy - 10, "σ", size=12, color=AMBER, bold=True))

    # виноска на заштриховану площу
    f.append(text(line_x + 150, base - 110, "площа хвоста за лінією = Q(z)", size=11.5, color=POS, bold=True))
    f.append(line(line_x + 150, base - 100, line_x + 46, base - 62, color=POS, sw=1.1))
    f.append(circle(line_x + 46, base - 62, 3.0, fill=POS, stroke=BG, sw=1.1))

    # формула
    f.append(fitbox(60, 424, 420, 44, "z = d / (2σ)          RBER = Q(z)",
                    size=13.5, bold=True, color=INK, fill=STEELF, stroke=STEEL, sw=1.3))

    render(os.path.join(IMG, "qtail-geometry.svg"), W, H, *f)


# ── 8. Водоспад надійності: RBER = Q(z) як крута парабола від запасу z ────────
def fig_rber_cliff():
    from math import erfc, sqrt, log10
    W, H = 900, 580
    XL, XW, YT, YH = 118, 660, 100, 356
    XR, YB = XL + XW, YT + YH
    zlo, zhi = 1.0, 6.0
    lo_e, hi_e = -8, 0     # верх графіка — 10⁻⁸ (безпечно), низ — 10⁰ (обвал)

    def xm(z):
        return XL + (z - zlo) / (zhi - zlo) * XW

    def ym(v):
        t = (log10(v) - lo_e) / (hi_e - lo_e)
        return YT + t * YH

    def Qf(z):
        return 0.5 * erfc(z / sqrt(2))

    f = [text(W / 2, 30, "Водоспад надійності: RBER = Q(z) проти запасу в сигмах", size=17, bold=True)]
    f.append(text(W / 2, 52, "z = d/2σ — один рух ліворуч (менше d, більше σ) обвалює RBER надекспоненційно",
                  size=11, color=MUTED, italic=True))

    # рамка графіка
    f.append(rect(XL, YT, XW, YH, fill=BG, stroke=INK, sw=1.4, rx=0))

    # горизонтальні лінії-декади RBER (лог, зверху безпечно, знизу обвал)
    ylab = ["10⁻⁸", "10⁻⁷", "10⁻⁶", "10⁻⁵", "10⁻⁴", "10⁻³", "10⁻²", "10⁻¹", "1"]
    for i in range(9):
        yy = YT + i / 8.0 * YH
        f.append(line(XL, yy, XR, yy, color="#e6e6e6", sw=1.0))
        f.append(text(XL - 10, yy + 4, ylab[i], size=10, color=MUTED, anchor="end"))
    # вертикальні лінії-поділки запасу z
    for z in range(1, 7):
        xx = xm(float(z))
        f.append(line(xx, YT, xx, YB, color="#e6e6e6", sw=1.0))
        f.append(text(xx, YB + 20, str(z), size=10.5, color=MUTED))

    f.append(text((XL + XR) / 2.0, YB + 44, "запас z = d/2σ, сигм →", size=11.5, color=INK, bold=True))
    yc = (YT + YB) / 2.0
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (XL - 58, yc, FONT, INK, XL - 58, yc, "RBER = Q(z), лог — обвал ↓"))

    # сама крива
    pts, z = [], zlo
    while z <= zhi + 1e-9:
        v = Qf(z)
        if v > 0:
            pts.append((xm(z), ym(max(v, 10 ** lo_e))))
        z += (zhi - zlo) / 140.0
    f.append(_poly(pts, "none", STEEL, 2.8))

    # заливка «крутого лівого схилу» (z від 1 до 2.2) — тут живуть QLC і TLC
    f.append(rect(XL, YT, xm(2.2) - XL, YH, fill="#fbeeec", stroke="none", rx=0))

    # робочі точки QLC і TLC
    zq, zt = 1.44, 3.08
    vq, vt = Qf(zq), Qf(zt)
    xq, yq = xm(zq), ym(vq)
    xt, yt_ = xm(zt), ym(vt)
    f.append(circle(xq, yq, 5.0, fill=POS, stroke=BG, sw=1.4))
    f.append(_pill(xq + 4, yq - 34, "QLC: z≈1.44, RBER≈7.5·10⁻²", size=10, color=POS))
    f.append(line(xq, yq - 8, xq + 4, yq - 24, color=POS, sw=1.0))
    f.append(circle(xt, yt_, 5.0, fill=FIELD, stroke=BG, sw=1.4))
    f.append(_pill(xt + 40, yt_ - 30, "TLC: z≈3.08, RBER≈10⁻³", size=10, color=FIELD))
    f.append(line(xt, yt_ - 8, xt + 40, yt_ - 20, color=FIELD, sw=1.0))

    # стрілка зносу: σ↑ → z↓, уздовж кривої ліворуч-униз
    za, zb = 2.55, 1.75
    xa2, ya2 = xm(za), ym(Qf(za))
    xb2, yb2 = xm(zb), ym(Qf(zb))
    f.append(arrow(xa2, ya2, xb2, yb2, color=AMBER, sw=2.0))
    f.append(_pill((xa2 + xb2) / 2.0 - 10, (ya2 + yb2) / 2.0 - 30, "знос: σ↑ → z↓", size=10.5, color=AMBER, bold=True))

    # правий край — SLC/MLC, де хвіст практично зникає
    f.append(text(XR - 8, YT + 22, "SLC, MLC — далеко праворуч,", size=10, color=MUTED, anchor="end"))
    f.append(text(XR - 8, YT + 36, "z ≫ 6, хвіст зникає", size=10, color=MUTED, anchor="end"))
    f.append(arrow(XR - 8, YT + 44, XR - 8, YT + 14, color=MUTED, sw=1.3))

    f.append(text(XL + (xm(2.2) - XL) / 2.0, YB - 12, "крутий лівий схил — тут TLC і QLC",
                  size=10.5, color=POS, bold=True))

    f.append(fitbox(XL, YB + 56, XW, 32,
                    "RBER ≈ exp(−d²/8σ²): показник квадратичний за d, тому рух ліворуч по z обвалює надійність на порядки, а не в рази.",
                    size=10.5, color=INK, fill=STEELF, stroke=STEEL, sw=1.1))

    render(os.path.join(IMG, "rber-cliff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_levels()
    fig_drift()
    fig_hard_soft()
    fig_code_shelf()
    fig_escalation()
    fig_soft_gain()
    fig_qtail()
    fig_rber_cliff()
    print("OK: 8 figures ->", IMG)
