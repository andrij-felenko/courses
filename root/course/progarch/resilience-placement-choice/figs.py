# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір: де живе стійкість»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER  = "#b06d0f"   # семантичне — «зміст виклику»
AMBERF = "#fbf1dd"


def fig_retry_amplification():
    """Стек повторів множиться, а не додається: 1 → 3 → 9 → 27 на трьох шарах."""
    W, H = 1050, 560
    frags = []

    counts = [1, 3, 9, 27]
    labels = [
        "один запит користувача",
        "+ шлюз повторює ×3",
        "+ сайдкар сітки повторює ×3",
        "+ застосунок повторює ×3",
    ]
    bar_x = 470.0
    scale = 480.0 / 27.0          # 27 → 480 px
    ys = [96, 178, 260, 342]
    bh = 46

    for lbl, c, y in zip(labels, counts, ys):
        # лівий підпис — окремо від смуги, не накладається
        frags.append(text(44, y + bh / 2 + 5, lbl, size=13.5, color=INK, anchor="start"))
        w = max(10.0, c * scale)
        frags.append(rect(bar_x, y, w, bh, fill=POS, stroke=POS, sw=1.5, rx=5))
        frags.append(text(bar_x + w + 14, y + bh / 2 + 6, "= %d" % c,
                          size=17, color=POS, bold=True, anchor="start"))

    # формула — у вільному кутку вгорі праворуч (над короткими смугами)
    b, _, _ = textbox(792, 150, "3 × 3 × 3 = 27\nдодай 4-й шар → 3⁴ = 81",
                      size=13.5, fill=BG, stroke=MUTED, min_w=300)
    frags.append(b)

    # залежність унизу — саме в неї б'є роздутий залп
    dep_y = 452
    frags.append(rect(300, dep_y, 500, 54, fill="#fff6f5", stroke=POS, sw=2, rx=8))
    frags.append(text(550, dep_y + 32, "повільна залежність B — уже задихається",
                      size=14, color=POS, bold=True))
    # стрілка від смуги «27» вниз у залежність
    frags.append(arrow(690, ys[3] + bh, 620, dep_y - 2, color=POS, sw=2.2))

    render(os.path.join(IMG, "retry-amplification.svg"), W, H, *frags,
           title="Стек повторів множиться, а не додається")


def fig_placement_map():
    """Три доми стійкості: зміст → застосунок, труба → сітка, вхід → шлюз.
    Кожен ґард — рівно в одному домі, обраному за тим, чи треба знати сенс виклику."""
    W, H = 1140, 600
    frags = []

    # розділювачі трьох панелей
    for sx in (380, 760):
        frags.append(line(sx, 44, sx, 402, color=MUTED, sw=1, dash="4,5"))

    # заголовки панелей + кольорові підзаголовки (дім ↔ вид знання)
    frags.append(text(190, 62, "Бібліотека / у застосунку", size=15, bold=True, color=AMBER))
    frags.append(text(570, 62, "Сайдкар / сітка", size=15, bold=True, color=NEG))
    frags.append(text(950, 62, "Шлюз / край", size=15, bold=True, color=FIELD))
    frags.append(text(190, 86, "знає ЗМІСТ виклику", size=12.5, color=AMBER, italic=True))
    frags.append(text(570, 86, "бачить лише трубу", size=12.5, color=NEG, italic=True))
    frags.append(text(950, 86, "одна брама на вході", size=12.5, color=FIELD, italic=True))

    # ── застосунок (семантичні ґарди, бурштин) ──
    app = ["повтор ЛИШЕ за ключем\nідемпотентності",
           "fallback на\nостанній твін",
           "бюджет за орендарем\nі пріоритетом",
           "запобіжник за\nзмістом помилки"]
    for s, y in zip(app, (130, 200, 270, 340)):
        b, _, _ = textbox(190, y, s, size=12.5, fill=AMBERF, stroke=AMBER, min_w=250)
        frags.append(b)

    # ── сітка (транспортні ґарди, синій) ──
    mesh = ["mTLS між сервісами",
            "таймаут з'єднання,\nбалансування реплік",
            "повтор на\n«з'єднання відмовлено»",
            "запобіжник на\nнедосяжний хост"]
    for s, y in zip(mesh, (130, 200, 270, 340)):
        b, _, _ = textbox(570, y, s, size=12.5, fill="#eef2fb", stroke=NEG, min_w=250)
        frags.append(b)

    # ── шлюз (грубі вхідні ґарди, зелений) ──
    gw = ["глобальний ліміт\nна орендаря",
          "груба вхідна\nстеля часу",
          "автентифікація"]
    for s, y in zip(gw, (130, 208, 286)):
        b, _, _ = textbox(950, y, s, size=12.5, fill="#eafaf0", stroke=FIELD, min_w=230)
        frags.append(b)
    frags.append(text(950, 348, "лише вхід, не глибину", size=12, color=MUTED, italic=True))

    # ── нижній банер: одне питання, що розводить доми ──
    frags.append(rect(40, 424, 1060, 150, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    frags.append(text(570, 462, "Одне питання: чи потрібно знати, ЩО означає виклик?",
                      size=15.5, bold=True))
    frags.append(text(570, 500,
                      "так → застосунок      ·      ні, лише труба → сітка/сайдкар      ·      груба брама на вході → шлюз",
                      size=13.5))
    frags.append(text(570, 538,
                      "і головне — кожен прийом живе рівно в ОДНОМУ домі, інакше шари перемножуються",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "placement-map.svg"), W, H, *frags,
           title="Кожен ґард — у тому домі, де живе його знання")


def fig_path_retry_switches():
    """Шлях команди DH з перемикачами повтору:
    ДО — усі шари ×3 (множник ×27); ПІСЛЯ — власник один, решта ×1 (множник ×3)."""
    W, H = 1180, 560
    frags = []
    nodes = ["застосунок", "шлюз", "сайдкар\nсітки", "сервіс команд\n(залежність)"]
    xs = [250, 500, 750, 1010]

    def lane(y, tries, badges, total, tcolor, owner=None):
        out, widths = [], []
        for i, (nm, x) in enumerate(zip(nodes, xs)):
            is_dep = (i == len(nodes) - 1)
            fill, stroke = (("#fff6f5", POS) if is_dep else (FILL, LINE))
            if owner is not None and i == owner:
                fill, stroke = AMBERF, AMBER
            b, w, h = textbox(x, y, nm, size=13, fill=fill, stroke=stroke, sw=1.8, min_w=150)
            out.append(b)
            widths.append(w)
        for i in range(len(nodes) - 1):
            x_from = xs[i] + widths[i] / 2 + 4
            x_to = xs[i + 1] - widths[i + 1] / 2 - 6
            out.append(arrow(x_from, y, x_to, y, color=MUTED, sw=1.8))
            t, kind = tries[i], badges[i]
            if kind == "off":
                col, bg, lbl = MUTED, BG, "×1 off"
            elif kind == "owner":
                col, bg, lbl = AMBER, AMBERF, "×%d власник" % t
            else:
                col, bg, lbl = POS, "#fdecea", "×%d" % t
            bx = (x_from + x_to) / 2
            bb, _, _ = textbox(bx, y - 32, lbl, size=12.5, bold=True,
                               color=col, fill=bg, stroke=col, min_w=48)
            out.append(bb)
        cb, _, _ = textbox(xs[-1], y + 76, total, size=15, bold=True,
                           color=tcolor, fill=BG, stroke=tcolor, min_w=214)
        out.append(cb)
        return out

    frags.append(text(70, 100, "ДО: повтор на кожному шарі", size=15, bold=True,
                      color=POS, anchor="start"))
    frags += lane(172, [3, 3, 3], ["storm", "storm", "storm"],
                  "= ×27  →  13 500 req/s", POS)

    frags.append(text(70, 320, "ПІСЛЯ: власник один, решта пропускає", size=15, bold=True,
                      color=FIELD, anchor="start"))
    frags += lane(392, [3, 1, 1], ["owner", "off", "off"],
                  "= ×3  →  1 500 req/s", FIELD, owner=0)

    render(os.path.join(IMG, "path-retry-switches.svg"), W, H, *frags,
           title="Той самий шлях, два конфіги: множник ×27 і множник ×3")


def fig_retry_budget_cap():
    """Бюджет Linkerd як стеля-частка: шторм хоче сотні повторів, бюджет пускає лише +20%+10/с."""
    W, H = 1000, 512
    frags = []
    base_y = 400
    scale = 0.95
    bw = 130

    def bar(cx, val, color, fill, caption, sub):
        out, h = [], val * scale
        out.append(rect(cx - bw / 2, base_y - h, bw, h, fill=fill, stroke=color, sw=2))
        out.append(text(cx, base_y - h - 12, "%d req/s" % val, size=15, bold=True, color=color))
        out.append(text(cx, base_y + 26, caption, size=13.5, bold=True))
        out.append(text(cx, base_y + 47, sub, size=12, color=MUTED))
        return out

    frags.append(line(70, base_y, 940, base_y, color=INK, sw=1.6))
    frags += bar(190, 100, NEG, "#eaf0fd", "живий трафік", "100 req/s на маршруті")
    frags += bar(500, 300, POS, "#fdecea", "чого просить шторм", "фіксовані повтори на шарах")

    # привид «шторму» пунктиром до 300, тоді суцільна зелена стеля 30
    frags.append(rect(810 - bw / 2, base_y - 300 * scale, bw, 300 * scale,
                      fill="none", stroke=POS, sw=1.3, rx=6))
    frags += bar(810, 30, FIELD, "#eafaf0", "бюджет пускає", "0.2·100 + 10 = 30 req/s")
    frags.append(arrow(810, base_y - 300 * scale + 8, 810, base_y - 30 * scale - 6,
                       color=POS, sw=2))
    b, _, _ = textbox(932, base_y - 178, "сітка\nвідкидає\nрешту", size=12, color=POS,
                      fill=BG, stroke=POS, min_w=92)
    frags.append(b)

    p, _, _ = textbox(430, 484, "retryRatio 0.2   ·   minRetriesPerSecond 10   ·   ttl 10s",
                      size=13, fill=FILL, stroke=MUTED, min_w=560)
    frags.append(p)

    render(os.path.join(IMG, "retry-budget-cap.svg"), W, H, *frags,
           title="Бюджет повторів: стеля як частка трафіку, не число на запит")


def fig_resilience_lineage_timeline():
    """Двадцять років переїздів: у коді (2007) → бібліотека (2012) →
    сайдкар/сітка (2016–2017) → бібліотечний дім живий (2018). Колір = дім."""
    W, H = 1200, 430
    frags = []
    axis_y = 250

    frags.append(line(64, axis_y, 1120, axis_y, color=INK, sw=2))
    frags.append(arrow(1092, axis_y, 1128, axis_y, color=INK, sw=2))
    frags.append(text(1128, axis_y + 22, "час →", size=12, color=MUTED, anchor="end", italic=True))

    nodes = [
        (150,  MUTED, FILL,      "у коді",
         "2007\nМайкл Нюґард\n«Release It!»\nприйом НАЗВАНО,\nпишуть руками"),
        (380,  AMBER, AMBERF,    "бібліотека",
         "2011–2012\nNetflix Hystrix\nприйом у БІБЛІОТЕЦІ\nв застосунку"),
        (610,  NEG,   "#eef2fb", "сайдкар",
         "2016\nEnvoy · Linkerd\nтермін «service mesh»\nстійкість → САЙДКАР"),
        (830,  NEG,   "#eef2fb", "сітка",
         "2017\nIstio (на Envoy)\nсітка стає\nмасовою"),
        (1050, AMBER, AMBERF,    "бібліотека",
         "2018\nHystrix → підтримка\nспадкоємець\nResilience4j"),
    ]
    for cx, col, fillc, home, s in nodes:
        b, _, _ = textbox(cx, 150, s, size=12.5, fill=fillc, stroke=col, min_w=196)
        frags.append(b)
        frags.append(line(cx, 208, cx, axis_y - 3, color=col, sw=1.6))
        frags.append(circle(cx, axis_y, 5, fill=col, stroke=col))
        frags.append(text(cx, axis_y + 22, home, size=12, color=col, italic=True))

    # легенда: колір рамки = ДІМ, у якому жив прийом
    ly = 372
    frags.append(rect(292, ly - 12, 22, 16, fill=FILL, stroke=MUTED, sw=1.4, rx=3))
    frags.append(text(322, ly + 1, "у коді, вручну", size=13, color=MUTED, anchor="start"))
    frags.append(rect(500, ly - 12, 22, 16, fill=AMBERF, stroke=AMBER, sw=1.4, rx=3))
    frags.append(text(530, ly + 1, "бібліотека в застосунку", size=13, color=AMBER, anchor="start"))
    frags.append(rect(788, ly - 12, 22, 16, fill="#eef2fb", stroke=NEG, sw=1.4, rx=3))
    frags.append(text(818, ly + 1, "сайдкар/сітка", size=13, color=NEG, anchor="start"))

    render(os.path.join(IMG, "resilience-lineage-timeline.svg"), W, H, *frags,
           title="Куди переїжджала стійкість: двадцять років")


def fig_pendulum_split():
    """Маятник ішов з коду в інфраструктуру, але на півдорозі розколовся:
    труба доїхала в сітку, зміст завернув назад у застосунок."""
    W, H = 1020, 440
    frags = []

    b, _, _ = textbox(150, 100, "СТАРТ · 2007\nу коді, вручну",
                      size=12.5, fill=FILL, stroke=MUTED, min_w=150)
    frags.append(b)

    frags.append(text(430, 74, "куди штовхав маятник — у інфраструктуру",
                      size=12, color=MUTED, italic=True))
    frags.append(arrow(238, 100, 545, 100, color=MUTED, sw=2.2))

    # тріщина-розкол на півдорозі
    frags.append('<polyline points="556,84 566,100 552,114 568,130" '
                 'fill="none" stroke="%s" stroke-width="2.6"/>' % POS)
    frags.append(text(560, 150, "розкол", size=11.5, color=POS, italic=True))

    # гілка ТРУБА → сітка (синій), вниз-праворуч, доїхала в інфру
    b, _, _ = textbox(818, 205, "ТРУБА → сітка\nmTLS · стеля з'єднання\nбалансування реплік",
                      size=12.5, fill="#eef2fb", stroke=NEG, min_w=250)
    frags.append(b)
    frags.append(arrow(578, 108, 720, 176, color=NEG, sw=2.2))

    # гілка ЗМІСТ → застосунок (бурштин), вниз-ліворуч, завертає назад до коду
    b, _, _ = textbox(250, 300, "ЗМІСТ → застосунок\nповтор за ключем\nfallback на твін",
                      size=12.5, fill=AMBERF, stroke=AMBER, min_w=250)
    frags.append(b)
    frags.append(arrow(548, 118, 372, 268, color=AMBER, sw=2.2))

    frags.append(rect(40, 360, 940, 62, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    frags.append(text(510, 386, "Розкол не за модою, а за знанням", size=14.5, bold=True))
    frags.append(text(510, 408,
                      "що вирішується самими байтами → сітка   ·   що вимагає сенсу виклику → застосунок",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "pendulum-split.svg"), W, H, *frags,
           title="Маятник, що розколовся по лінії знання")


if __name__ == "__main__":
    fig_retry_amplification()
    fig_placement_map()
    fig_path_retry_switches()
    fig_retry_budget_cap()
    fig_resilience_lineage_timeline()
    fig_pendulum_split()
    print("OK: retry-amplification.svg, placement-map.svg, "
          "path-retry-switches.svg, retry-budget-cap.svg, "
          "resilience-lineage-timeline.svg, pendulum-split.svg")
