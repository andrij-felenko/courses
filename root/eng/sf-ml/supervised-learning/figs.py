# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: мічений приклад = вхід + мітка ────────────────────────────────
def fig_labeled_example():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Мічений приклад = вхід + мітка", size=17, bold=True))

    rows = [
        ("фото кота",            "«кіт»"),
        ("темп. 87°, вібр. 2.1", "«тривога»"),
        ("площа 60, кімнат 2",   "ціна 95 000"),
    ]
    y0 = 78
    dy = 74
    inx = 150      # центр колонки «вхід»
    mx  = 560      # центр колонки «мітка»
    bw  = 250      # ширина рамки входу
    mw  = 200      # ширина рамки мітки

    # заголовки колонок
    f.append(text(inx, y0 - 22, "ВХІД (ознаки)", size=13, bold=True, color=NEG))
    f.append(text(mx,  y0 - 22, "МІТКА (відповідь)", size=13, bold=True, color=FIELD))

    for i, (a, b) in enumerate(rows):
        cy = y0 + i * dy
        f.append(fitbox(inx - bw/2, cy - 24, bw, 48, a, size=14, fill="#eaf0fd", stroke=NEG))
        # стрілка вхід → мітка
        f.append(arrow(inx + bw/2 + 6, cy, mx - mw/2 - 6, cy, color=MUTED, sw=2))
        f.append(fitbox(mx - mw/2, cy - 24, mw, 48, b, size=14, fill="#e9f7ef", stroke=FIELD, bold=True))

    # підсумковий рядок
    box, bwd, bhd = textbox(W/2, H - 30,
        "Набір таких пар → модель учиться вгадувати мітку для НОВОГО входу",
        size=13, pad=12, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'labeled-example.svg'), W, H, *f)


# ── Фігура 2: класифікація проти регресії ───────────────────────────────────
def fig_classification_regression():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Дві задачі: класифікація і регресія", size=17, bold=True))

    # ── ліва панель: класифікація ──
    lx, ly, lw, lh = 40, 70, 300, 240
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke=LINE))
    f.append(text(lx + lw/2, ly - 6, "КЛАСИФІКАЦІЯ  «що це?»", size=13, bold=True))
    # межа між двома класами (діагональ)
    f.append(line(lx + 20, ly + lh - 30, lx + lw - 20, ly + 40, color="#c9a227", sw=2.5, dash="7 5"))
    # клас 0 (низ-ліво) — сині мінуси
    import random
    random.seed(3)
    for _ in range(9):
        px = lx + 30 + random.random() * 120
        py = ly + lh - 90 + random.random() * 60
        f.append(minus(px, py, r=8))
    # клас 1 (верх-право) — червоні плюси
    for _ in range(9):
        px = lx + lw - 150 + random.random() * 120
        py = ly + 40 + random.random() * 60
        f.append(plus(px, py, r=8))
    f.append(text(lx + 70, ly + lh - 14, "клас A", size=12, color=NEG, bold=True))
    f.append(text(lx + lw - 66, ly + 30, "клас B", size=12, color=POS, bold=True))
    box, _, _ = textbox(lx + lw/2, ly + lh + 30, "мітка — розряд;  модель проводить МЕЖУ",
                        size=12, pad=8, fill="#f4f6f8", stroke=MUTED)
    f.append(box)

    # ── права панель: регресія ──
    rx, ry, rw, rh = 380, 70, 300, 240
    f.append(rect(rx, ry, rw, rh, fill=BG, stroke=LINE))
    f.append(text(rx + rw/2, ry - 6, "РЕГРЕСІЯ  «скільки?»", size=13, bold=True))
    # осі
    f.append(line(rx + 30, ry + rh - 30, rx + rw - 20, ry + rh - 30, color=MUTED, sw=1.5))
    f.append(line(rx + 30, ry + 20, rx + 30, ry + rh - 30, color=MUTED, sw=1.5))
    # пряма тренду
    x1, y1 = rx + 40, ry + rh - 50
    x2, y2 = rx + rw - 30, ry + 45
    f.append(line(x1, y1, x2, y2, color=FIELD, sw=2.8))
    # точки-приклади навколо прямої
    random.seed(7)
    for t in range(10):
        fr = t / 9.0
        bx = x1 + (x2 - x1) * fr
        by = y1 + (y2 - y1) * fr + (random.random() - 0.5) * 34
        f.append(circle(bx, by, 4.5, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    box, _, _ = textbox(rx + rw/2, ry + rh + 30, "мітка — число;  модель будує КРИВУ",
                        size=12, pad=8, fill="#f4f6f8", stroke=MUTED)
    f.append(box)

    render(os.path.join(OUT, 'classification-regression.svg'), W, H, *f)


# ── Фігура 3: цикл навчання через похибку ───────────────────────────────────
def fig_training_loop():
    W, H = 720, 350
    f = []
    f.append(text(W/2, 26, "Як учитель навчає: зменшуй похибку", size=17, bold=True))

    cy = 130
    # чотири блоки в ряд
    b1, w1, _ = textbox(110, cy, "приклад\n(вхід)", size=13, pad=12, fill="#eaf0fd", stroke=NEG)
    b2, w2, _ = textbox(300, cy, "модель →\nпередбачення", size=13, pad=12, fill="#f4f6f8", stroke=LINE)
    b3, w3, _ = textbox(500, cy, "порівняти\nз міткою", size=13, pad=12, fill="#e9f7ef", stroke=FIELD)
    b4, w4, _ = textbox(650, cy, "ПОХИБКА", size=14, pad=12, fill="#fdecea", stroke=POS, bold=True)
    f.append(arrow(110 + w1/2 + 4, cy, 300 - w2/2 - 4, cy, sw=2))
    f.append(arrow(300 + w2/2 + 4, cy, 500 - w3/2 - 4, cy, sw=2))
    f.append(arrow(500 + w3/2 + 4, cy, 650 - w4/2 - 4, cy, sw=2))
    f.append(b1); f.append(b2); f.append(b3); f.append(b4)

    # зворотна стрілка: похибка → підправити модель
    f.append(line(650, cy + 26, 650, cy + 78, color=POS, sw=2))
    f.append(line(650, cy + 78, 300, cy + 78, color=POS, sw=2))
    f.append(arrow(300, cy + 78, 300, cy + 26, color=POS, sw=2))
    fb = fitbox(390, cy + 60, 190, 36, "підправити ваги ← похибка", size=12,
                fill="#fdecea", stroke=POS)
    f.append(fb)

    # нижній банер: похибка меншає
    box, _, _ = textbox(W/2, H - 42,
        "коло повторюють на тисячах прикладів → похибка ПОСТУПОВО меншає → модель точнішає",
        size=13, pad=12, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'training-loop.svg'), W, H, *f)


# ── Фігура (hist): коридор межі Кавера–Гарта ────────────────────────────────
def fig_nn_bound():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Теорема Кавера–Гарта: помилка 1-NN у коридорі [R*, 2R*]", size=15, bold=True))

    # осі
    ox, oy = 90, 300            # початок координат (низ-ліво)
    ax, ay = 640, 70            # верх-право межі поля
    f.append(line(ox, oy, ax, oy, color=MUTED, sw=1.5))   # вісь X
    f.append(line(ox, oy, ox, ay, color=MUTED, sw=1.5))   # вісь Y
    f.append(text((ox+ax)/2, oy + 34, "кількість прикладів →", size=12, color=MUTED))
    f.append(text(ox - 60, (oy+ay)/2, "помилка", size=12, color=MUTED, anchor="middle"))

    # рівні R* і 2R*
    y_bayes = 250              # лінія R*
    y_two   = 130              # лінія 2R*
    f.append(line(ox, y_bayes, ax, y_bayes, color=NEG, sw=2.5))
    f.append(line(ox, y_two,   ax, y_two,   color=POS, sw=2.5))
    f.append(text(ax + 4, y_bayes + 4, "R*", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(ax + 4, y_two + 4, "2R*", size=13, color=POS, bold=True, anchor="start"))

    # заливка коридору між R* і 2R* (легка)
    f.append(rect(ox, y_two, ax - ox, y_bayes - y_two, fill="#eef6ee", stroke="none", sw=0))
    # повторно перекреслити осьові лінії коридору поверх заливки
    f.append(line(ox, y_bayes, ax, y_bayes, color=NEG, sw=2.5))
    f.append(line(ox, y_two,   ax, y_two,   color=POS, sw=2.5))

    # крива помилки 1-NN: старт високо, спадає й затискається трохи над R*
    import math
    pts = []
    x0, x1 = ox + 6, ax - 6
    for i in range(0, 61):
        fr = i / 60.0
        px = x0 + (x1 - x0) * fr
        # експоненційний спад від ~y=100 (над 2R*) до ~y_bayes+16
        top = 96
        target = y_bayes + 16
        py = target + (top - target) * math.exp(-4.2 * fr)
        pts.append((px, py))
    poly = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, FIELD))
    f.append(text(x1 - 4, y_bayes + 8, "помилка 1-NN", size=12, color=FIELD, bold=True, anchor="end"))

    # підпис-висновок
    box, _, _ = textbox(W/2, H - 26,
        "1 найближчий сусід ⇒ помилка ніколи не вище за 2R* (удвічі гірше за ідеал)",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'nn-bound.svg'), W, H, *f)


# ── Фігура (math): похибка — чаша над параметром; мінімум = найкраще припасування ─
def fig_loss_bowl_min():
    import math
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Мінімум похибки = нахил нуль = найкраще припасування", size=15, bold=True))

    ox, oy = 90, 310           # початок координат (низ-ліво)
    ax, ay = 640, 70           # межі поля
    f.append(line(ox, oy, ax, oy, color=MUTED, sw=1.5))     # вісь X (параметр)
    f.append(line(ox, oy, ox, ay, color=MUTED, sw=1.5))     # вісь Y (похибка)
    f.append(text((ox+ax)/2, oy + 34, "значення параметра →", size=12, color=MUTED))
    f.append(text(ox - 58, (oy+ay)/2, "похибка", size=12, color=MUTED, anchor="middle"))

    # парабола L(θ) = a·(θ−θ*)² + c  у координатах поля
    cx = ox + (ax - ox) * 0.52     # x мінімуму
    ymin = oy - 34                 # y дна чаші
    a = 0.0016
    pts = []
    for i in range(0, 111):
        px = ox + 8 + (ax - ox - 16) * (i / 110.0)
        dx = px - cx
        py = ymin - a * dx * dx * 1.0
        # обмежити зверху полем
        if py < ay + 6:
            py = ay + 6
        pts.append((px, py))
    poly = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, FIELD))

    # точка мінімуму
    f.append(circle(cx, ymin, 5.5, fill="#e9f7ef", stroke=FIELD, sw=2.2))
    f.append(line(cx, ymin, cx, oy, color=FIELD, sw=1.2, dash="4 4"))
    f.append(text(cx, oy + 16, "θ*", size=13, color=FIELD, bold=True))

    # дотична в мінімумі — горизонтальна (нахил 0)
    f.append(line(cx - 70, ymin, cx + 70, ymin, color=INK, sw=2))
    f.append(text(cx, ymin - 12, "нахил = 0", size=12, bold=True))

    # дотична ліворуч — спадна (веде вниз-праворуч)
    lx = ox + (ax - ox) * 0.20
    dxl = lx - cx
    lyv = ymin - a * dxl * dxl
    slope_l = -2 * a * dxl        # dY/dX у полі (Y росте вниз, тож знак так)
    f.append(line(lx - 55, lyv - slope_l * (-55), lx + 55, lyv - slope_l * (55),
                  color=POS, sw=2))
    f.append(text(lx - 4, lyv - 16, "нахил < 0", size=11, color=POS, bold=True, anchor="end"))

    # банер-висновок
    box, _, _ = textbox(W/2, H - 24,
        "спуск котиться, доки нахил не зникне; там похибка найменша — модель припасована найкраще",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'loss-bowl-min.svg'), W, H, *f)


# ── Фігура (math): ґаусів дзвін над кожним залишком → добуток → −log = Σ квадратів ─
def fig_gaussian_to_mse():
    import math
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Звідки MSE: ґаусів шум → правдоподібність → сума квадратів", size=15, bold=True))

    # три міні-осі з дзвоном, центрованим на передбаченні; мітка — вертикальна риска
    panels = [
        (150, "малий промах",  0.30),
        (360, "більший промах", 0.95),
        (570, "великий промах", 1.65),
    ]
    base = 250          # рівень осі кожної панелі
    span = 92           # піврозмах по x (щоб дзвони панелей не наскакували)
    amp  = 120          # висота дзвона
    for pcx, cap, off in panels:
        # вісь
        f.append(line(pcx - span, base, pcx + span, base, color=MUTED, sw=1.4))
        # дзвін N(μ=передбачення, σ), центр = pcx
        pts = []
        for i in range(0, 81):
            t = -3.0 + 6.0 * (i / 80.0)          # у стандартних відхиленнях
            px = pcx + (span / 3.0) * t
            py = base - amp * math.exp(-0.5 * t * t)
            pts.append((px, py))
        poly = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, NEG))
        # центр дзвона = передбачення
        f.append(line(pcx, base, pcx, base - amp, color=NEG, sw=1.1, dash="3 3"))
        f.append(text(pcx, base + 16, "ŷ", size=12, color=NEG, bold=True))
        # мітка y — зсунута на off·σ праворуч
        yx = pcx + (span / 3.0) * off
        yv = base - amp * math.exp(-0.5 * off * off)
        f.append(line(yx, base, yx, base - amp - 6, color=POS, sw=2))
        f.append(text(yx, base - amp - 12, "y", size=12, color=POS, bold=True))
        # висота дзвона в точці мітки = правдоподібність цього прикладу
        f.append(circle(yx, yv, 4.2, fill="#fdecea", stroke=POS, sw=1.8))
        f.append(text(pcx, base + 34, cap, size=11, color=MUTED))

    # ланцюг перетворень унизу
    chain = "L(кожного) = висота дзвона в точці y   →   −log добутку   =   const + (1/2σ²)·Σ(ŷ−y)²"
    box, _, _ = textbox(W/2, H - 24, chain, size=12, pad=10, fill="#eef2ff", stroke=NEG)
    f.append(box)

    render(os.path.join(OUT, 'gaussian-to-mse.svg'), W, H, *f)


# ── Фігура (math): перехресна ентропія проти квадрата на впевненій помилці ────
def fig_ce_vs_sq_confident():
    import math
    W, H = 720, 390
    f = []
    f.append(text(W/2, 24, "Впевнена помилка: −log p злітає, а квадрат (1−p)² упирається в 1", size=14, bold=True))

    ox, oy = 90, 310           # початок (низ-ліво): p=0 ліворуч
    ax, ay = 610, 60
    f.append(line(ox, oy, ax, oy, color=MUTED, sw=1.5))     # вісь p
    f.append(line(ox, oy, ox, ay, color=MUTED, sw=1.5))     # вісь штрафу
    f.append(text((ox+ax)/2, oy + 34, "p — упевненість у ПРАВИЛЬНОМУ класі →", size=12, color=MUTED))
    f.append(text(ox - 52, (oy+ay)/2, "штраф", size=12, color=MUTED, anchor="middle"))
    # позначки p
    for pv, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]:
        gx = ox + (ax - ox) * pv
        f.append(line(gx, oy, gx, oy + 5, color=MUTED, sw=1.2))
        f.append(text(gx, oy + 20, lab, size=11, color=MUTED))

    ytop = ay + 6              # відповідає штрафу = YMAX
    YMAX = 4.0                 # шкала штрафу (−log p зрізаємо на 4)
    def Y(v):
        v = min(v, YMAX)
        return oy - (oy - ytop) * (v / YMAX)

    # крива −log p (перехресна ентропія)
    pts = []
    for i in range(1, 100):
        pv = 0.02 + (1.0 - 0.02) * (i / 99.0)
        gx = ox + (ax - ox) * pv
        pts.append((gx, Y(-math.log(pv))))
    poly = "M " + " L ".join("%.1f %.1f" % (gx, gy) for gx, gy in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, POS))
    f.append(text(ox + 62, Y(3.4), "−log p", size=13, color=POS, bold=True, anchor="start"))

    # крива (1−p)² — квадратичний штраф за впевненість
    pts2 = []
    for i in range(0, 100):
        pv = i / 99.0
        gx = ox + (ax - ox) * pv
        pts2.append((gx, Y((1.0 - pv) ** 2)))
    poly2 = "M " + " L ".join("%.1f %.1f" % (gx, gy) for gx, gy in pts2)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly2, NEG))
    f.append(text(ox + (ax-ox)*0.30, Y(0.62), "(1−p)²", size=13, color=NEG, bold=True, anchor="start"))

    # горизонталь штрафу = 1 (стеля квадрата)
    f.append(line(ox, Y(1.0), ax, Y(1.0), color=NEG, sw=1.0, dash="5 5"))
    f.append(text(ax - 2, Y(1.0) - 6, "стеля квадрата = 1", size=10, color=NEG, anchor="end"))

    # зона впевненої помилки (p→0) — ліворуч
    f.append(mtext(ox + 118, ay + 96, ["тут модель", "впевнено ХИБИТЬ"],
                   size=11, color=POS, lh=1.25))

    box, _, _ = textbox(W/2, H - 22,
        "що впевненіша хибна відповідь (p→0), то нескінченно дорожча за −log p; квадрат же прощає її майже за ту саму 1",
        size=11, pad=9, fill="#fdecea", stroke=POS)
    f.append(box)

    render(os.path.join(OUT, 'ce-vs-sq-confident.svg'), W, H, *f)


if __name__ == '__main__':
    fig_labeled_example()
    fig_classification_regression()
    fig_training_loop()
    fig_nn_bound()
    fig_loss_bowl_min()
    fig_gaussian_to_mse()
    fig_ce_vs_sq_confident()
    print("OK: 7 figures written to", OUT)
