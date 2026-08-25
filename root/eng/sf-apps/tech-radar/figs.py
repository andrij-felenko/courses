# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: дві осі радара — квадранти (що) × кільця (наскільки довіряємо) ──
def fig_two_axes():
    W, H = 760, 560
    cx, cy = W / 2, H / 2 + 6
    rings = [190, 145, 100, 55]          # зовнішнє → внутрішнє
    ring_names = ["Hold", "Assess", "Trial", "Adopt"]
    ring_fill = ["#f4f6f8", "#eef1f4", "#e7ebef", "#dfe4e9"]

    parts = []
    # кільця (від найбільшого, щоб менші лягали поверх)
    for r, fill in zip(rings, ring_fill):
        parts.append(circle(cx, cy, r, fill=fill, stroke=LINE, sw=1.4))
    # осьові лінії квадрантів
    parts.append(line(cx - rings[0], cy, cx + rings[0], cy, color=LINE, sw=1.4))
    parts.append(line(cx, cy - rings[0], cx, cy + rings[0], color=LINE, sw=1.4))

    # підписи кілець — уздовж верхньої вертикалі, кожен у своєму проміжку, поза лініями
    band_mid = [(rings[0] + rings[1]) / 2, (rings[1] + rings[2]) / 2,
                (rings[2] + rings[3]) / 2, rings[3] / 2]
    for name, rm in zip(ring_names, band_mid):
        parts.append(text(cx + 8, cy - rm + 4, name, size=13, color=INK,
                          anchor="start", bold=(name == "Adopt")))

    # назви квадрантів — по кутах, з добрим відступом від кола
    q = rings[0] + 14
    parts.append(text(cx - q + 6, cy - q + 20, "Техніки", size=15, color=INK, anchor="start", bold=True))
    parts.append(text(cx + q - 6, cy - q + 20, "Інструменти", size=15, color=INK, anchor="end", bold=True))
    parts.append(text(cx - q + 6, cy + q - 8, "Платформи", size=15, color=INK, anchor="start", bold=True))
    parts.append(text(cx + q - 6, cy + q - 8, "Мови й фреймворки", size=15, color=INK, anchor="end", bold=True))

    # кілька блипів-крапок у різних секторах і кільцях
    def blip(ang_deg, r, hot=False):
        a = math.radians(ang_deg)
        bx, by = cx + r * math.cos(a), cy - r * math.sin(a)
        col = POS if hot else FIELD
        fillc = "#fdecea" if hot else "#e8f6ee"
        return circle(bx, by, 6, fill=fillc, stroke=col, sw=2)

    parts.append(blip(120, 80))    # техніка в Trial
    parts.append(blip(135, 40))    # техніка в Adopt
    parts.append(blip(55, 125))    # інструмент в Assess
    parts.append(blip(50, 75))     # інструмент в Trial
    parts.append(blip(225, 90))    # платформа в Trial
    parts.append(blip(200, 165, hot=True))  # платформа в Hold
    parts.append(blip(315, 45))    # мова в Adopt
    parts.append(blip(300, 170, hot=True))  # мова в Hold

    # напрямна стрілка «довіра / зобов'язання росте до центру» — збоку, поза колом
    ax = cx + rings[0] + 96
    parts.append(text(ax, cy - 150, "зобов'язання", size=12, color=MUTED, anchor="middle"))
    parts.append(text(ax, cy - 134, "росте", size=12, color=MUTED, anchor="middle"))
    parts.append(arrow(ax, cy - 118, ax, cy + 40, color=MUTED, sw=1.6))
    parts.append(text(ax, cy + 58, "до центру", size=12, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'two-axes.svg'), W, H, *parts,
           title="Радар: квадрант каже ЩО, кільце каже НАСКІЛЬКИ ми готові на це покластися")


# ── Фігура 2: труба довіри Assess → Trial → Adopt, і вихід у Hold ────────────
def fig_pipeline():
    W, H = 820, 430
    y0 = 150
    box_w, box_h, gap = 170, 92, 62
    xs = [60, 60 + box_w + gap, 60 + 2 * (box_w + gap)]
    labels = ["Assess", "Trial", "Adopt"]
    subs = ["варте вивчення —\nпробуємо на макеті,\nбез ставки на продукт",
            "готове до бою —\nставимо в один\nреальний проєкт",
            "дефолт —\nбери це без\nзайвих питань"]
    fills = ["#eef1f4", "#e7ebef", "#dfe4e9"]

    parts = []
    for x, lab, sub, fl in zip(xs, labels, subs, fills):
        parts.append(rect(x, y0, box_w, box_h, fill=fl, stroke=LINE, sw=1.6))
        parts.append(text(x + box_w / 2, y0 + 24, lab, size=17, bold=True))
        parts.append(mtext(x + box_w / 2, y0 + 44, sub, size=11, color=MUTED, lh=1.25))

    # стрілки просування (докази накопичуються)
    for i in range(2):
        x1 = xs[i] + box_w
        x2 = xs[i + 1]
        parts.append(arrow(x1 + 6, y0 + box_h / 2, x2 - 6, y0 + box_h / 2, color=FIELD, sw=2.4))
        parts.append(text((x1 + x2) / 2, y0 - 12, "докази", size=11, color=FIELD))
        parts.append(text((x1 + x2) / 2, y0 + box_h + 22, "ok", size=11, color=FIELD))

    # верхній підпис осі
    parts.append(text(60, y0 - 40, "докази накопичуються → зобов'язання росте", size=13, color=INK, anchor="start", bold=True))

    # Hold — куди падає те, що не склалося / застаріло (окремий блок нижче)
    hx = xs[1]
    hy = y0 + box_h + 78
    parts.append(rect(hx, hy, box_w, box_h - 10, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(hx + box_w / 2, hy + 24, "Hold", size=17, bold=True, color=POS))
    parts.append(mtext(hx + box_w / 2, hy + 44, "нового на цьому\nне починаємо —\nтихо згортаємо",
                      size=11, color=INK, lh=1.25))

    # стрілки в Hold: з будь-якого кільця (з Assess — «не склалося», з Adopt — «застаріло»)
    parts.append(arrow(xs[0] + box_w / 2, y0 + box_h + 4, hx + 12, hy - 4, color=POS, sw=1.6))
    parts.append(text(xs[0] + box_w / 2 + 34, hy - 22, "не склалося", size=10, color=POS, anchor="start"))
    parts.append(arrow(xs[2] + box_w / 2, y0 + box_h + 4, hx + box_w - 12, hy - 4, color=POS, sw=1.6))
    parts.append(text(xs[2] + box_w / 2 - 34, hy - 22, "застаріло", size=10, color=POS, anchor="end"))

    render(os.path.join(IMG, 'pipeline.svg'), W, H, *parts,
           title="Кільця — це шлях під невизначеністю: доводь дешево, лише тоді став дорого")


# ── Фігура 3: розсип рішень vs один спільний портфель ────────────────────────
def fig_sprawl_vs_portfolio():
    W, H = 820, 400
    parts = []
    # ліва панель — хаос
    lx, lw = 40, 320
    parts.append(text(lx + lw / 2, 40, "Без радара: кожен вирішує сам", size=15, bold=True))
    parts.append(rect(lx, 60, lw, 300, fill="#fbfcfd", stroke=MUTED, sw=1.3, rx=10))
    teams = [("Команда A", "Kafka"), ("Команда B", "RabbitMQ"),
             ("Команда C", "SQS"), ("Команда D", "своя черга")]
    ty = 100
    for name, tech in teams:
        b, w, h = textbox(lx + lw / 2, ty, name + " → " + tech, size=12, pad=9,
                          fill="#eef1f4", min_w=190)
        parts.append(b)
        ty += 62
    parts.append(text(lx + lw / 2, 348, "4 черги, 0 спільного досвіду", size=12, color=POS))

    # права панель — портфель
    rx0, rw = 460, 320
    parts.append(text(rx0 + rw / 2, 40, "З радаром: один спільний вибір", size=15, bold=True))
    parts.append(rect(rx0, 60, rw, 300, fill="#fbfcfd", stroke=FIELD, sw=1.3, rx=10))
    b, w, h = textbox(rx0 + rw / 2, 118, "Adopt: Kafka", size=14, pad=11,
                      fill="#e8f6ee", stroke=FIELD, sw=1.8, bold=True, min_w=200)
    parts.append(b)
    for name in ["Команда A", "Команда B", "Команда C", "Команда D"]:
        pass
    # чотири команди сходяться на один блип
    conv_y = 250
    xs4 = [rx0 + 55, rx0 + 130, rx0 + 190, rx0 + 265]
    for x, name in zip(xs4, ["A", "B", "C", "D"]):
        parts.append(circle(x, conv_y, 15, fill="#eef1f4", stroke=LINE, sw=1.4))
        parts.append(text(x, conv_y + 5, name, size=12, bold=True))
        parts.append(arrow(x, conv_y - 16, rx0 + rw / 2, 140, color=FIELD, sw=1.3))
    parts.append(text(rx0 + rw / 2, 348, "1 черга, спільний досвід і глибина", size=12, color=FIELD))

    render(os.path.join(IMG, 'sprawl-vs-portfolio.svg'), W, H, *parts,
           title="Радар зводить розсіяні поодинокі вибори в один спільний портфель")


if __name__ == '__main__':
    fig_two_axes()
    fig_pipeline()
    fig_sprawl_vs_portfolio()
    print("figures written")
