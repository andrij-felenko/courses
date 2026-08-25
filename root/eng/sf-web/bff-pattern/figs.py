# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#b8860b"


def box_at(cx, cy, s, **kw):
    """textbox at center → (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: клієнт збирає сам (багато кругорейсів) проти BFF (один кругорейс) ──
def chatty_vs_bff():
    W, H = 1040, 600
    parts = []
    parts.append(text(W / 2, 30, "Хто зшиває екран: клієнт по мобільній мережі чи BFF у ЦОД",
                      size=17, bold=True))
    parts.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 56, "БЕЗ BFF · клієнт збирає сам", size=13, bold=True, color=POS))
    parts.append(text(W * 3 / 4, 56, "З BFF · збірка на сервері", size=13, bold=True, color=FIELD))

    svc = ["профіль", "замовлення", "поради"]

    # ── ЛІВА половина: телефон угорі, три сервіси внизу, три повільні кругорейси ──
    lx = W / 4
    (ph_l, pw, phh) = box_at(lx, 110, "телефон\n(клієнт)", size=12, bold=True,
                             fill="#fdecea", stroke=POS, min_w=150)
    parts.append(ph_l)
    lsx = [lx - 150, lx, lx + 150]
    for x, name in zip(lsx, svc):
        b, bw, bh = box_at(x, 360, name, size=12, fill=FILL, stroke=MUTED, min_w=118)
        parts.append(b)
        parts.append(line(lx, 110 + phh, x, 360 - bh, color=POS, sw=1.8, dash="6 5"))
    parts.append(text(lx, 235, "3 повільні кругорейси", size=12, bold=True, color=POS))
    parts.append(text(lx, 255, "по мобільній мережі", size=11, italic=True, color=MUTED))
    parts.append(text(lx, 452, "клієнт сам робить N викликів", size=12, italic=True, color=POS))
    parts.append(text(lx, 473, "і сам зшиває відповіді", size=12, italic=True, color=POS))
    parts.append(text(lx, 494, "затримка = сума кругорейсів", size=12, italic=True, color=POS))

    # ── ПРАВА половина: телефон → BFF (один кругорейс) → три сервіси швидкою мережею ──
    rx = W * 3 / 4
    (ph_r, rpw, rphh) = box_at(rx, 105, "телефон\n(клієнт)", size=12, bold=True,
                               fill="#eaf7ef", stroke=FIELD, min_w=150)
    parts.append(ph_r)
    (bff, bfw, bfh) = box_at(rx, 235, "BFF\n(бекенд цього екрана)", size=12, bold=True,
                             fill="#eaf7ef", stroke=FIELD, min_w=230)
    parts.append(bff)
    parts.append(arrow(rx, 105 + rphh, rx, 235 - bfh, color=FIELD, sw=2.4))
    parts.append(text(rx + 130, 170, "1 кругорейс", size=12, bold=True, color=FIELD, anchor="middle"))
    rsx = [rx - 150, rx, rx + 150]
    for x, name in zip(rsx, svc):
        b, bw, bh = box_at(x, 400, name, size=12, fill=FILL, stroke=MUTED, min_w=118)
        parts.append(b)
        parts.append(arrow(rx, 235 + bfh, x, 400 - bh, color=FIELD, sw=1.6))
    parts.append(text(rx - 155, 320, "фанаут", size=11, italic=True, color=MUTED, anchor="middle"))
    parts.append(text(rx - 155, 337, "швидкою", size=11, italic=True, color=MUTED, anchor="middle"))
    parts.append(text(rx - 155, 354, "мережею ЦОД", size=11, italic=True, color=MUTED, anchor="middle"))
    parts.append(text(rx, 470, "один запит клієнта; BFF фанаутить,", size=12, italic=True, color=FIELD))
    parts.append(text(rx, 491, "зшиває й повертає рівно те, що треба екрану", size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "chatty-vs-bff.svg"), W, H, *parts)


# ── Фігура 2: спільний бекенд (один на всіх) проти BFF (один на кожен досвід) ──
def gateway_vs_bff():
    W, H = 1060, 660
    parts = []
    parts.append(text(W / 2, 30, "Один бекенд на всіх проти одного бекенда на кожен досвід",
                      size=17, bold=True))
    parts.append(line(70, H / 2, W - 70, H / 2, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 2, H / 2 - 12, "ЗАГАЛЬНИЙ бекенд / API-шлюз — компроміс на всіх", size=13, bold=True, color=POS))
    parts.append(text(W / 2, H / 2 + 26, "BFF — свій бекенд для кожного клієнта", size=13, bold=True, color=FIELD))

    clients = ["веб", "iOS", "Android"]
    cx3 = [W / 2 - 300, W / 2, W / 2 + 300]
    services_lbl = "сервіси: профіль · каталог · замовлення · оплата"

    # ── ВЕРХ: три клієнти → один спільний бекенд → сервіси ──
    top_client_y = 78
    shared_y = 168
    top_svc_y = 245
    tops = []
    for x, name in zip(cx3, clients):
        b, bw, bh = box_at(x, top_client_y, name, size=12, bold=True,
                           fill="#fdecea", stroke=POS, min_w=120)
        parts.append(b)
        tops.append((x, bh))
    (sh, shw, shh) = box_at(W / 2, shared_y, "ОДИН загальний бекенд", size=13, bold=True,
                            fill=FILL, stroke=POS, min_w=320)
    parts.append(sh)
    for x, bh in tops:
        parts.append(line(x, top_client_y + bh, W / 2 + (x - W / 2) * 0.30, shared_y - shh,
                          color=POS, sw=1.6))
    (tsv, tsw, tsh) = box_at(W / 2, top_svc_y, services_lbl, size=11,
                             fill="#f0f0f0", stroke=MUTED, min_w=470)
    parts.append(tsv)
    parts.append(arrow(W / 2, shared_y + shh, W / 2, top_svc_y - tsh, color=MUTED, sw=1.6))
    parts.append(text(W / 2, top_svc_y + tsh + 22,
                      "усе через одну відповідь-компроміс: кожному клієнту або замало, або забагато",
                      size=11.5, italic=True, color=POS))

    # ── НИЗ: кожен клієнт → свій BFF → ті самі спільні сервіси ──
    bot_client_y = H / 2 + 66
    bff_y = H / 2 + 158
    bot_svc_y = H - 66
    for x, name in zip(cx3, clients):
        b, bw, bh = box_at(x, bot_client_y, name, size=12, bold=True,
                           fill="#eaf7ef", stroke=FIELD, min_w=120)
        parts.append(b)
        d, dw, dh = box_at(x, bff_y, "BFF\n" + name, size=11, bold=True,
                           fill=FILL, stroke=FIELD, min_w=130)
        parts.append(d)
        parts.append(arrow(x, bot_client_y + bh, x, bff_y - dh, color=FIELD, sw=1.8))
    (bsv, bsw, bsh) = box_at(W / 2, bot_svc_y, services_lbl, size=11,
                             fill="#f0f0f0", stroke=MUTED, min_w=470)
    parts.append(bsv)
    for x in cx3:
        parts.append(line(x, bff_y + 22, W / 2 + (x - W / 2) * 0.28, bot_svc_y - bsh,
                          color=FIELD, sw=1.4, dash="5 4"))
    parts.append(text(W / 2, bot_svc_y + bsh + 22,
                      "у кожного BFF — своя команда фронтенду; сервіси внизу спільні",
                      size=11.5, italic=True, color=FIELD))

    render(os.path.join(IMG, "gateway-vs-bff.svg"), W, H, *parts)


# ── Фігура 3: послідовний фанаут (сума) проти паралельного (максимум) ──
def fanout_timing():
    W, H = 940, 470
    parts = []
    parts.append(text(W / 2, 30, "Три виклики: послідовно (сума) проти паралельно (максимум)",
                      size=17, bold=True))

    x0 = 210
    scale = 2.2  # px на 1 ms
    bar_h = 26

    def ms(t):
        return x0 + t * scale

    # осьові підписи часу
    def time_axis(y):
        parts.append(line(x0, y, ms(280), y, color=MUTED, sw=1))
        for t in (0, 80, 120, 200, 260):
            parts.append(line(ms(t), y - 3, ms(t), y + 3, color=MUTED, sw=1))
        parts.append(text(ms(280) + 26, y + 4, "мс", size=11, color=MUTED, anchor="middle"))

    # ── ВЕРХ: послідовно A(80)→B(120)→C(60) = 260 ──
    y1 = 110
    parts.append(text(x0 - 12, y1 - 22, "ПОСЛІДОВНО", size=13, bold=True, color=POS, anchor="start"))
    segs = [("A", 0, 80), ("B", 80, 200), ("C", 200, 260)]
    for name, t1, t2 in segs:
        parts.append(rect(ms(t1), y1, (t2 - t1) * scale, bar_h, fill="#fdecea", stroke=POS, sw=1.5))
        parts.append(text((ms(t1) + ms(t2)) / 2, y1 + 18, "%s %d" % (name, t2 - t1),
                          size=11, color=POS))
    time_axis(y1 + bar_h + 20)
    parts.append(line(ms(260), y1 - 8, ms(260), y1 + bar_h + 28, color=POS, sw=1.6, dash="4 3"))
    parts.append(text(ms(260) + 8, y1 - 2, "разом 260 мс", size=12, bold=True, color=POS, anchor="start"))
    parts.append(text(x0 - 12, y1 + bar_h + 48, "кожен чекає на попередній → затримка = сума",
                      size=11.5, italic=True, color=POS, anchor="start"))

    # ── НИЗ: паралельно, усі з t=0; разом = max = 120 ──
    y2 = 270
    parts.append(text(x0 - 12, y2 - 22, "ПАРАЛЕЛЬНО", size=13, bold=True, color=FIELD, anchor="start"))
    rows = [("A", 80), ("B", 120), ("C", 60)]
    for i, (name, dur) in enumerate(rows):
        yy = y2 + i * (bar_h + 8)
        parts.append(rect(ms(0), yy, dur * scale, bar_h, fill="#eaf7ef", stroke=FIELD, sw=1.5))
        parts.append(text(ms(0) + dur * scale / 2, yy + 18, "%s %d" % (name, dur),
                          size=11, color=FIELD))
    ybot = y2 + 3 * (bar_h + 8)
    time_axis(ybot + 6)
    parts.append(line(ms(120), y2 - 8, ms(120), ybot + 14, color=FIELD, sw=1.6, dash="4 3"))
    parts.append(text(ms(120) + 8, y2 - 2, "разом 120 мс", size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(text(x0 - 12, ybot + 40, "усі стартують разом → затримка = найповільніший",
                      size=11.5, italic=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "fanout-timing.svg"), W, H, *parts)


# ── Фігура 4 (для hist-вставки): пʼять кроків народження BFF, різні люди ──
def birth_timeline():
    W, H = 1200, 560
    parts = []
    parts.append(text(W / 2, 34, "Пʼять кроків, а не один геній: як зʼявився BFF",
                      size=18, bold=True))
    parts.append(text(W / 2, 58,
                      "кожен крок — інша дійова особа: патерн визрів у практиці, тоді дістав імʼя, опис і розголос",
                      size=12.5, italic=True, color=MUTED))

    spine_y = 300
    parts.append(line(80, spine_y, W - 80, spine_y, color=MUTED, sw=2))

    xs = [130, 362.5, 595, 827.5, 1060]
    # (текст, дата, заливка, обвід, зверху?, наголос?)
    nodes = [
        ("ВИХІД ІЗ МОНОЛІТУ\nлишають «Mothership»,\nдробляться в мікросервіси",
         "≈ 2012", "#fdecea", POS, True, False),
        ("ПАТЕРН ПОБУДОВАНО\nновий iOS-застосунок →\nбекенд під кожен фронтенд",
         "2013–14", "#eaf7ef", FIELD, False, True),
        ("ДІСТАВ ІМʼЯ\nNick Fisher: «BFF»\n(«BEFFE» відхилено)",
         "≈ 2014–15", FILL, MUTED, True, False),
        ("ЗАДОКУМЕНТОВАНО\nPhil Calçado,\nблог-пост",
         "18.09.2015", "#faf3e0", AMBER, False, False),
        ("РОЗНЕСЕНО\nSam Newman:\n«один досвід — один BFF»",
         "листопад 2015", "#eaf0fd", NEG, True, False),
    ]

    for x, (body_txt, date, fill, stroke, above, hot) in zip(xs, nodes):
        cy = 196 if above else 404
        mw = 262 if hot else 244
        sw = 2.4 if hot else 1.6
        b, hw, hh = box_at(x, cy, body_txt, size=13, fill=fill, stroke=stroke,
                           sw=sw, min_w=mw)
        r = 10 if hot else 7
        # конектор рамка↔вузол (по свій бік осі, дата — по протилежний)
        if above:
            parts.append(line(x, cy + hh, x, spine_y - r, color=stroke, sw=1.4))
            parts.append(text(x, spine_y + 28, date, size=12.5, bold=True, color=stroke))
        else:
            parts.append(line(x, spine_y + r, x, cy - hh, color=stroke, sw=1.4))
            parts.append(text(x, spine_y - 18, date, size=12.5, bold=True, color=stroke))
        parts.append(b)
        parts.append(circle(x, spine_y, r, fill=fill, stroke=stroke, sw=2.2))

    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *parts)


def _polyline(pts, color, sw=2.4, dash=None):
    s = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


# ── Фігура 5 (математика): P(хоч один повільний) = 1 − pᴺ проти ширини фанауту ──
def tail_fanout_curve():
    W, H = 950, 580
    Lx, Rx, Ty, By = 96, 726, 96, 486
    plotW, plotH = Rx - Lx, By - Ty
    parts = []
    parts.append(text(W / 2, 34, "Ймовірність зловити повільний хвіст росте з шириною фанауту",
                      size=16, bold=True))

    def X(n):
        return Lx + (n - 1) / 99.0 * plotW

    def Y(p):
        return By - p * plotH

    # сітка + осі
    for gp in (0.2, 0.4, 0.6, 0.8):
        parts.append(line(Lx, Y(gp), Rx, Y(gp), color=MUTED, sw=0.7, dash="3 5"))
    parts.append(line(Lx, Ty, Lx, By, color=INK, sw=1.4))
    parts.append(line(Lx, By, Rx, By, color=INK, sw=1.4))
    for pct in (0, 20, 40, 60, 80, 100):
        parts.append(text(Lx - 12, Y(pct / 100.0) + 4, str(pct), size=11, color=MUTED, anchor="end"))
    for n in (1, 20, 40, 60, 80, 100):
        parts.append(line(X(n), By, X(n), By + 4, color=INK, sw=1))
        parts.append(text(X(n), By + 22, str(n), size=11, color=MUTED))
    parts.append(text(Lx - 44, Ty - 16, "P(хоч один повільний), %", size=12, bold=True, anchor="start"))
    parts.append(text((Lx + Rx) / 2, By + 48, "N — ширина фанауту (скільки паралельних викликів)",
                      size=12, italic=True, color=MUTED))

    curves = [(0.90, POS, "p = 0.90"), (0.99, AMBER, "p = 0.99"), (0.999, FIELD, "p = 0.999")]
    for p, col, lbl in curves:
        pts = [(X(n), Y(1 - p ** n)) for n in range(1, 101)]
        parts.append(_polyline(pts, col, sw=2.6))
        endv = 1 - p ** 100
        parts.append(circle(X(100), Y(endv), 3.2, fill=col, stroke=col, sw=1))
        parts.append(text(Rx + 10, Y(endv) + 4, "%s · %d%%" % (lbl, round(endv * 100)),
                          size=12, bold=True, color=col, anchor="start"))

    # орієнтир: N=10, p=0.99 → 9.6 %
    y10 = Y(1 - 0.99 ** 10)
    parts.append(circle(X(10), y10, 3.4, fill=AMBER, stroke=AMBER, sw=1))
    parts.append(text(X(10) + 10, y10 - 10, "N=10 → 9.6%", size=11, bold=True, color=AMBER, anchor="start"))

    render(os.path.join(IMG, "tail-fanout-curve.svg"), W, H, *parts)


# ── Фігура 6 (математика): очікуваний максимум із N — легкий хвіст проти важкого ──
def expected_max_tails():
    W, H = 950, 560
    Lx, Rx, Ty, By = 100, 690, 92, 470
    plotW, plotH = Rx - Lx, By - Ty
    ymax = 10.5
    parts = []
    parts.append(text(W / 2, 32, "Очікуваний максимум із N: легкий хвіст росте як ln N, важкий — як √N",
                      size=15.5, bold=True))

    def X(n):
        return Lx + (n - 1) / 99.0 * plotW

    def Y(r):
        return By - r / ymax * plotH

    for g in (2, 4, 6, 8, 10):
        parts.append(line(Lx, Y(g), Rx, Y(g), color=MUTED, sw=0.7, dash="3 5"))
        parts.append(text(Lx - 12, Y(g) + 4, "×%d" % g, size=11, color=MUTED, anchor="end"))
    parts.append(line(Lx, Ty, Lx, By, color=INK, sw=1.4))
    parts.append(line(Lx, By, Rx, By, color=INK, sw=1.4))
    for n in (1, 20, 40, 60, 80, 100):
        parts.append(line(X(n), By, X(n), By + 4, color=INK, sw=1))
        parts.append(text(X(n), By + 22, str(n), size=11, color=MUTED))
    parts.append(text(Lx - 56, Ty - 14, "E[максимум] ÷ середній час одного виклику",
                      size=12, bold=True, anchor="start"))
    parts.append(text((Lx + Rx) / 2, By + 48, "N — ширина фанауту", size=12, italic=True, color=MUTED))

    # базова лінія «один виклик = ×1»
    parts.append(line(Lx, Y(1), Rx, Y(1), color=NEG, sw=1.1, dash="6 4"))
    parts.append(text(Rx - 4, Y(1) - 8, "один виклик = ×1", size=11, italic=True, color=NEG, anchor="end"))

    # легкий хвіст: гармонічне число H_N
    Hn, s = [], 0.0
    for n in range(1, 101):
        s += 1.0 / n
        Hn.append(s)
    light = [(X(n), Y(Hn[n - 1])) for n in range(1, 101)]
    heavy = [(X(n), Y(n ** 0.5)) for n in range(1, 101)]
    parts.append(_polyline(light, FIELD, sw=2.6))
    parts.append(_polyline(heavy, POS, sw=2.6))

    parts.append(circle(X(100), Y(Hn[99]), 3.2, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(circle(X(100), Y(10.0), 3.2, fill=POS, stroke=POS, sw=1))
    parts.append(text(X(100) - 6, Y(Hn[99]) + 24, "легкий хвіст (експонента) ∝ ln N  →  ×5.2",
                      size=12, bold=True, color=FIELD, anchor="end"))
    parts.append(text(X(100) - 6, Y(10.0) - 10, "важкий хвіст ∝ √N  →  ×10",
                      size=12, bold=True, color=POS, anchor="end"))

    render(os.path.join(IMG, "expected-max-tails.svg"), W, H, *parts)


# ── Фігура 7 (proj): часова смуга — фанаут під спільним бюджетом, tips обривають ──
def budget_clamp():
    W, H = 1000, 432
    parts = []
    parts.append(text(W / 2, 32,
                      "Три виклики стартують разом; кожен під власним дедлайном, усі — під бюджетом запиту",
                      size=15, bold=True))

    x0 = 250
    scale = 1.55  # px на 1 ms

    def ms(t):
        return x0 + t * scale

    bar_h = 30
    y_prof, y_ord, y_tips = 96, 162, 228
    axis_y = 296
    GREEN_FILL = "#eaf7ef"
    AMBER_FILL = "#faf3e0"

    # ── спільний бюджет запиту: одна лінія на всю висоту ──
    bx = ms(400)
    parts.append(line(bx, 74, bx, axis_y + 8, color=POS, sw=2.2, dash="5 4"))
    parts.append(text(bx - 8, 68, "стеля бюджету запиту · 400 мс",
                      size=12, bold=True, color=POS, anchor="end"))

    # ── profile: критичний, устигає за 175 мс (свій дедлайн 300) ──
    parts.append(text(x0 - 16, y_prof + 20, "profile · критичний",
                      size=12, bold=True, color=INK, anchor="end"))
    parts.append(rect(ms(0), y_prof, 175 * scale, bar_h, fill=GREEN_FILL, stroke=FIELD, sw=1.7))
    parts.append(text(ms(175) + 12, y_prof + 20, "✓ 175 мс",
                      size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(line(ms(300), y_prof - 6, ms(300), y_prof + bar_h + 6, color=MUTED, sw=1.3, dash="3 3"))
    parts.append(text(ms(300) + 7, y_prof - 9, "дедлайн 300", size=11, color=MUTED, anchor="start"))

    # ── orders: необов'язковий, устигає за 235 мс (свій дедлайн 300) ──
    parts.append(text(x0 - 16, y_ord + 20, "orders · необов'язковий",
                      size=12, bold=True, color=INK, anchor="end"))
    parts.append(rect(ms(0), y_ord, 235 * scale, bar_h, fill=GREEN_FILL, stroke=FIELD, sw=1.7))
    parts.append(text(ms(235) + 12, y_ord + 20, "✓ 235 мс",
                      size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(line(ms(300), y_ord - 6, ms(300), y_ord + bar_h + 6, color=MUTED, sw=1.3, dash="3 3"))

    # ── tips: необов'язковий, ПОВІЛЬНИЙ — обрив на власному дедлайні 250 ──
    parts.append(text(x0 - 16, y_tips + 20, "tips · необов'язковий",
                      size=12, bold=True, color=INK, anchor="end"))
    parts.append(rect(ms(0), y_tips, 250 * scale, bar_h, fill=AMBER_FILL, stroke=AMBER, sw=1.7))
    parts.append(line(ms(250), y_tips - 9, ms(250), y_tips + bar_h + 9, color=AMBER, sw=2.6))
    parts.append(line(ms(250), y_tips + bar_h / 2, ms(348), y_tips + bar_h / 2,
                      color=AMBER, sw=1.4, dash="4 4"))
    parts.append(text(ms(348) + 8, y_tips + bar_h / 2 + 4, "обірвано",
                      size=11, italic=True, color=AMBER, anchor="start"))
    parts.append(text(ms(250) + 8, y_tips - 12, "дедлайн tips 250 мс — обрив",
                      size=11, bold=True, color=AMBER, anchor="start"))

    # ── вісь часу ──
    parts.append(line(x0, axis_y, ms(415), axis_y, color=MUTED, sw=1))
    for t in (0, 100, 200, 250, 300, 400):
        parts.append(line(ms(t), axis_y - 3, ms(t), axis_y + 3, color=MUTED, sw=1))
        parts.append(text(ms(t), axis_y + 19, str(t), size=11, color=MUTED))
    parts.append(text(ms(415) + 20, axis_y + 4, "мс", size=11, color=MUTED, anchor="middle"))

    parts.append(text(W / 2, H - 22,
                      "Дедлайн виклику = min(власний ліміт, залишок бюджету). Повільний tips обривають на 250 — екран збирається без порад.",
                      size=11.5, italic=True, color=INK))

    render(os.path.join(IMG, "budget-clamp.svg"), W, H, *parts)


# ── Фігура 8 (proj): критичне проти необов'язкового + макет деградованого екрана ──
def critical_vs_optional():
    W, H = 1080, 560
    parts = []
    parts.append(text(W / 2, 32,
                      "Три сервіси, дві долі: критичне валить екран, необов'язкове лише ховає свій блок",
                      size=15, bold=True))

    divx = 704
    parts.append(line(divx, 58, divx, H - 26, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(362, 62, "яка доля в кожного виклику", size=13, bold=True, color=MUTED))
    parts.append(text((divx + W) / 2, 62, "що бачить користувач", size=13, bold=True, color=MUTED))

    # ── ЛІВОРУЧ: три рядки «сервіс → доля» ──
    rows = [
        ("profile", "КРИТИЧНИЙ", "503 — увесь екран лягає\n(нема імені —\nнема персонального)", True),
        ("orders", "НЕОБОВ'ЯЗКОВИЙ", "порожня стрічка\nзамовлень —\nекран лишається живим", False),
        ("tips", "НЕОБОВ'ЯЗКОВИЙ", "блок порад\nтихо схований —\nекран лишається живим", False),
    ]
    ys = [154, 300, 446]
    svc_x, out_x = 150, 476
    for (svc, tag, fate, crit), cy in zip(rows, ys):
        stroke = POS if crit else FIELD
        fill = "#fdecea" if crit else "#eaf7ef"
        b, hw, hh = box_at(svc_x, cy, svc, size=14, bold=True, fill=fill, stroke=stroke, min_w=132)
        parts.append(text(svc_x, cy - hh - 12, tag, size=11, bold=True, color=stroke))
        ob, ow, oh = box_at(out_x, cy, fate, size=12, fill=FILL, stroke=stroke, min_w=248)
        parts.append(arrow(svc_x + hw + 6, cy, out_x - ow - 8, cy, color=stroke, sw=1.9))
        parts.append(text((svc_x + hw + out_x - ow) / 2, cy - 12, "провал",
                          size=11, italic=True, color=stroke))
        parts.append(b)
        parts.append(ob)

    # ── ПРАВОРУЧ: макет деградованого екрана в рамці телефона ──
    px, py, pw, ph = 812, 92, 208, 402
    cx = px + pw / 2
    parts.append(rect(px, py, pw, ph, fill="#ffffff", stroke=INK, sw=2, rx=24))
    parts.append(rect(px + pw / 2 - 24, py + 12, 48, 7, fill=MUTED, stroke="none", sw=0, rx=4))

    # шапка: аватар + імʼя (КРИТИЧНЕ — на місці)
    parts.append(circle(px + 36, py + 62, 20, fill="#eaf7ef", stroke=FIELD, sw=2))
    parts.append(text(px + 68, py + 57, "Привіт, Оля", size=13, bold=True, color=INK, anchor="start"))
    parts.append(text(px + 68, py + 75, "профіль на місці", size=10.5, italic=True, color=FIELD, anchor="start"))
    parts.append(line(px + 16, py + 96, px + pw - 16, py + 96, color="#e5e7eb", sw=1.4))

    # останні замовлення (необов'язкове, цього разу є)
    oy = py + 118
    parts.append(text(px + 18, oy, "останні замовлення", size=11, bold=True, color=INK, anchor="start"))
    card_w, card_h, gap = 52, 68, 13
    total = 3 * card_w + 2 * gap
    startx = px + (pw - total) / 2
    for i in range(3):
        cxx = startx + i * (card_w + gap)
        parts.append(rect(cxx, oy + 14, card_w, card_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
        parts.append(rect(cxx + 8, oy + 22, card_w - 16, card_h - 32, fill="#e5e7eb", stroke="none", sw=0, rx=4))
        parts.append(line(cxx + 8, oy + card_h + 2, cxx + card_w - 8, oy + card_h + 2, color=MUTED, sw=3))

    # блок порад — СХОВАНО (привид пунктирною рамкою)
    ty = oy + 116
    gx, gw, gh = px + 16, pw - 32, 78
    for (a, bb, c, d) in [(gx, ty, gx + gw, ty), (gx + gw, ty, gx + gw, ty + gh),
                          (gx + gw, ty + gh, gx, ty + gh), (gx, ty + gh, gx, ty)]:
        parts.append(line(a, bb, c, d, color=MUTED, sw=1.2, dash="5 4"))
    parts.append(text(cx, ty + gh / 2 - 5, "блок порад", size=11, italic=True, color=MUTED))
    parts.append(text(cx, ty + gh / 2 + 13, "тихо схований", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "critical-vs-optional.svg"), W, H, *parts)


if __name__ == "__main__":
    chatty_vs_bff()
    gateway_vs_bff()
    fanout_timing()
    budget_clamp()
    critical_vs_optional()
    birth_timeline()
    tail_fanout_curve()
    expected_max_tails()
    print("figures written to", IMG)
