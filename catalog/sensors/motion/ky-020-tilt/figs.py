# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-020 — давач нахилу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

BALLC = "#8a8f98"   # металева кулька
BALLE = "#4b4f57"


# ── 1. Кулька в капсулі: рівно (розрив) vs нахил (замкнено) ────────────────────
def fig_ball():
    import math
    W, H = 860, 480
    f = [text(W / 2, 32, "Усередині нахилового вимикача: кулька, дві ніжки, сила тяжіння",
              size=15, bold=True)]

    def capsule(cx, cy, tilt_deg, closed, caption):
        """Малюємо капсулу-циліндр АБСОЛЮТНИМИ координатами (без <g transform>),
        щоб не було від'ємних коорд і svgcheck бачив реальні межі.
        Локальні координати (капсула горизонтальна, центр 0,0) обертаємо в Python."""
        cw, ch = 150, 82
        a = math.radians(tilt_deg)
        ca, sa = math.cos(a), math.sin(a)

        def T(lx, ly):
            return (cx + lx * ca - ly * sa, cy + lx * sa + ly * ca)

        parts = []
        # корпус — заокруглений прямокутник як полігон (грубе заокруглення кутів фаскою)
        hw, hh = cw / 2, ch / 2
        r = hh  # радіус торців
        outline = []
        # верхня грань зліва-направо, правий півкруг, нижня грань, лівий півкруг
        outline.append((-hw + r, -hh))
        outline.append((hw - r, -hh))
        for k in range(1, 6):
            th = -math.pi / 2 + math.pi * k / 6
            outline.append((hw - r + r * math.cos(th), r * math.sin(th)))
        outline.append((hw - r, hh))
        outline.append((-hw + r, hh))
        for k in range(1, 6):
            th = math.pi / 2 + math.pi * k / 6
            outline.append((-hw + r + r * math.cos(th), r * math.sin(th)))
        pts = " ".join("%.1f,%.1f" % T(px, py) for px, py in outline)
        parts.append('<polygon points="%s" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (pts, BALLE))

        # дві контактні ніжки в ПРАВОМУ нижньому куті (сходяться до дна)
        nx = hw - 34
        for dx, col in ((0, POS), (14, NEG)):
            x1, y1 = T(nx + dx, hh)
            x2, y2 = T(nx + dx + 4, hh - 26)
            parts.append(line(x1, y1, x2, y2, color=col, sw=3.0))

        # кулька у найнижчій точці капсули
        br = 16
        if not closed:
            blx, bly = -hw + 32, hh - br - 2      # рівно: ліворуч на дні
        else:
            blx, bly = nx + 6, hh - br - 2        # нахил: скотилась до ніжок
        bx, by = T(blx, bly)
        parts.append(circle(bx, by, br, fill=BALLC, stroke=BALLE, sw=1.8))
        hlx, hly = T(blx - 5, bly - 5)
        parts.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#c7ccd2"/>' % (hlx, hly))
        f.append("".join(parts))

        # підпис (поза капсулою, знизу)
        f.append(text(cx, cy + 96, caption, size=12, bold=True))
        badge = "коло ЗАМКНЕНО" if closed else "коло РОЗІМКНЕНО"
        f.append(text(cx, cy + 116, badge, size=11.5, bold=True, color=(FIELD if closed else MUTED)))
        # стрілка тяжіння над капсулою
        f.append(arrow(cx, cy - 74, cx, cy - 104, color=MUTED, sw=1.4))
        f.append(text(cx + 12, cy - 96, "g", size=12, italic=True, color=MUTED, anchor="start"))

    capsule(230, 220, 0, False, "рівно: кулька осторонь ніжок")
    capsule(630, 220, 22, True, "нахил ≈10°+: кулька на обох ніжках")

    # стрілки переходу між станами
    f.append(arrow(348, 214, 500, 214, color=INK, sw=2.0))
    f.append(text(424, 204, "нахилили", size=11, bold=True))
    f.append(arrow(500, 244, 348, 244, color=MUTED, sw=1.6))
    f.append(text(424, 262, "вирівняли", size=10.5, color=MUTED))

    b, _, _ = textbox(W / 2, 432,
                      "нахил читає сама гравітація: важка кулька завжди котиться в найнижчу точку —\n"
                      "рівно вона осторонь контактів (розрив), нахил зводить її на обидві ніжки (замкнено)",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "ball.svg"), W, H, *f)


# ── 2. Схема KY-020: підтяжка 10к до +, кулька садить S на землю ───────────────
def fig_schematic():
    W, H = 820, 460
    f = [text(W / 2, 30, "Схема KY-020: різистор 10 кОм тягне S до «+», кулька садить S на землю",
              size=14.5, bold=True)]

    # шина + зверху, земля знизу
    xL, xR = 120, 560
    yPlus, yGnd = 90, 370
    f.append(line(xL, yPlus, xR, yPlus, color=POS, sw=2.2))
    f.append(text(xL - 14, yPlus + 5, "+", size=18, bold=True, color=POS, anchor="end"))
    f.append(text(xR + 12, yPlus + 5, "живлення 3.3–5 В", size=10.5, color=POS, anchor="start"))
    f.append(line(xL, yGnd, xR, yGnd, color=INK, sw=2.2))
    f.append(text(xL - 14, yGnd + 5, "−", size=18, bold=True, color=NEG, anchor="end"))
    f.append(text(xR + 12, yGnd + 5, "земля (GND)", size=10.5, color=INK, anchor="start"))

    # вертикаль сигналу по центру
    xS = 300
    yNode = 230   # вузол S
    # різистор 10к: від + до вузла (зигзаг)
    def resistor(x, y1, y2):
        seg = (y2 - y1)
        zig = ['<polyline points="']
        n = 6
        pts = ["%.1f,%.1f" % (x, y1)]
        for i in range(n):
            yy = y1 + seg * (i + 0.5) / n
            xx = x + (12 if i % 2 == 0 else -12)
            pts.append("%.1f,%.1f" % (xx, yy))
        pts.append("%.1f,%.1f" % (x, y2))
        zig.append(" ".join(pts))
        zig.append('" fill="none" stroke="%s" stroke-width="2"/>' % INK)
        return "".join(zig)
    f.append(line(xS, yPlus, xS, yPlus + 20, color=INK, sw=2))
    f.append(resistor(xS, yPlus + 20, yNode - 20))
    f.append(line(xS, yNode - 20, xS, yNode, color=INK, sw=2))
    f.append(text(xS + 28, (yPlus + yNode) / 2, "10 кОм", size=12, bold=True, anchor="start"))
    f.append(text(xS + 28, (yPlus + yNode) / 2 + 16, "підтяжка", size=10, color=MUTED, anchor="start"))

    # вузол S
    f.append(circle(xS, yNode, 4.5, fill=INK, stroke=INK, sw=1))
    # відведення на пін S праворуч
    f.append(line(xS, yNode, 470, yNode, color=NEG, sw=2))
    f.append(rect(470, yNode - 14, 54, 28, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    f.append(text(497, yNode + 5, "S", size=14, bold=True, color=NEG))
    f.append(text(497, yNode - 22, "вихід", size=9.5, color=MUTED))

    # вимикач-кулька: від вузла вниз до землі
    swy1, swy2 = yNode + 18, yGnd
    f.append(line(xS, yNode, xS, swy1, color=INK, sw=2))
    # символ вимикача — дві точки й похила риска (розімкнено)
    f.append(circle(xS, swy1, 3.5, fill=BG, stroke=INK, sw=1.6))
    f.append(circle(xS, swy2 - 40, 3.5, fill=BG, stroke=INK, sw=1.6))
    f.append(line(xS, swy1, xS + 22, swy1 + 30, color=INK, sw=2.2))  # похила = розімкнено
    # кулька біля вимикача
    f.append(circle(xS + 34, swy1 + 20, 11, fill=BALLC, stroke=BALLE, sw=1.6))
    f.append(text(xS + 52, swy1 + 6, "кулька", size=10.5, bold=True, anchor="start"))
    f.append(text(xS + 52, swy1 + 22, "(нахил → замкне", size=9.5, color=MUTED, anchor="start"))
    f.append(text(xS + 52, swy1 + 36, "S на землю)", size=9.5, color=MUTED, anchor="start"))
    f.append(line(xS, swy2 - 40, xS, swy2, color=INK, sw=2))

    # дві плашки-стани праворуч унизу
    b1 = fitbox(600, 150, 200, 66,
                "РІВНО (розімкнено):\nрізистор тягне S до + →\nS = «1» (HIGH)",
                size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    b2 = fitbox(600, 250, 200, 66,
                "НАХИЛ (замкнено):\nкулька садить S на землю →\nS = «0» (LOW)",
                size=10.5, fill="#fdf0ee", stroke=POS)
    f.append(b2)

    b, _, _ = textbox(W / 2, 425,
                      "звідси перевернута логіка: спокій рівно = «1», нахил = «0». "
                      "Ніякої мікросхеми — лише різистор і контакт.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "schematic.svg"), W, H, *f)


# ── 3. Підключення трьома дротами ─────────────────────────────────────────────
def fig_wiring():
    W, H = 820, 420
    f = [text(W / 2, 28, "Підключення: три дроти, S просто в цифровий вхід (підтяжка вже на платі)",
              size=14.5, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 90, 120, 200, 180
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 28, "KY-020", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 48, "нахиловий вимикач", size=9.5, color=MUTED))
    # капсула-кулька схематично
    f.append(rect(mx + 55, my + 66, 90, 34, fill="#eef1f4", stroke=BALLE, sw=1.6, rx=17))
    f.append(circle(mx + 78, my + 83, 10, fill=BALLC, stroke=BALLE, sw=1.4))
    # три піни знизу модуля (+ у середині)
    pins = [("S", NEG, "#eaf0fd"), ("+", POS, "#fdecea"), ("−", INK, "#f2f2f2")]
    for i, (nm, col, fl) in enumerate(pins):
        px = mx + 42 + i * 58
        f.append(rect(px - 16, my + mh - 4, 32, 22, fill=fl, stroke=col, sw=1.4, rx=3))
        f.append(text(px, my + mh + 11, nm, size=12, bold=True, color=col))

    # МК праворуч
    cx, cy, cw, ch = 540, 130, 190, 170
    f.append(rect(cx, cy, cw, ch, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(cx + cw / 2, cy + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(cx + cw / 2, cy + 44, "(Arduino / ESP32 …)", size=9.5, color=MUTED))
    cpins = [("GPIO", NEG), ("3.3/5 В", POS), ("GND", INK)]
    for i, (nm, col) in enumerate(cpins):
        py = cy + 74 + i * 34
        f.append(rect(cx - 4, py - 12, 8, 22, fill="#fff", stroke=col, sw=1.4, rx=2))
        f.append(text(cx - 46, py + 4, nm, size=10, bold=True, color=col, anchor="middle"))

    # дроти: S-GPIO, + -живлення, − -GND
    sx = mx + 42
    vx = mx + 100
    gx = mx + 158
    ylow = my + mh + 40
    # S → GPIO
    f.append(line(sx, my + mh + 18, sx, ylow, color=NEG, sw=1.8))
    f.append(line(sx, ylow, cx - 4, cy + 74, color=NEG, sw=1.8))
    # + → живлення
    f.append(line(vx, my + mh + 18, vx, ylow + 22, color=POS, sw=1.8))
    f.append(line(vx, ylow + 22, cx - 4, cy + 108, color=POS, sw=1.8))
    # − → GND
    f.append(line(gx, my + mh + 18, gx, ylow + 44, color=INK, sw=1.8))
    f.append(line(gx, ylow + 44, cx - 4, cy + 142, color=INK, sw=1.8))

    b, _, _ = textbox(W / 2, 392,
                      "середній штир (+) — на живлення під логіку плати, (−) — на землю, "
                      "S — у будь-який цифровий вхід;\nзовнішня підтяжка не потрібна (10 кОм уже на модулі), "
                      "струм із піна S не беруть",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Брязкіт: один нахил → зубчаста черга стрибків; чиста подія після витримки ─
def fig_bounce():
    W, H = 840, 400
    f = [text(W / 2, 28, "Брязкіт кульки: один нахил дає чергу коротких стрибків «0↔1»",
              size=14.5, bold=True)]

    x0, x1 = 110, 760
    hi, lo = 90, 150        # рівні «1» і «0»
    f.append(text(x0 - 22, hi + 5, "1", size=12, bold=True, color=INK, anchor="end"))
    f.append(text(x0 - 22, lo + 5, "0", size=12, bold=True, color=INK, anchor="end"))
    f.append(line(x0, hi, x1, hi, color="#dfe3e8", sw=1.0, dash="4,4"))
    f.append(line(x0, lo, x1, lo, color="#dfe3e8", sw=1.0, dash="4,4"))

    # сирий сигнал: 1 → зубці → усталений 0
    tstart = 250   # момент нахилу
    # будуємо ламану
    pts = [(x0, hi), (tstart, hi)]
    # брязкіт: серія стрибків між tstart і tstart+120
    bx = tstart
    seq = [(0, lo, 14), (lo, hi, 8), (hi, lo, 10), (lo, hi, 6),
           (hi, lo, 12), (lo, hi, 5), (hi, lo, 9)]
    y = hi
    # вертикальний стрибок donw
    x = tstart
    zz = [(x, hi)]
    steps = [lo, hi, lo, hi, lo, hi, lo]
    widths = [16, 9, 12, 7, 13, 6, 10]
    for tgt, w in zip(steps, widths):
        zz.append((x, tgt))       # вертикаль
        x += w
        zz.append((x, tgt))       # горизонталь
    # після останнього — усталений 0 до кінця
    zz.append((x, lo))
    zz.append((x1 - 180, lo))
    poly = " ".join("%.1f,%.1f" % (px, py) for px, py in zz)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, INK))

    # зона брязкоту — підсвітка й підпис
    bz0, bz1 = tstart, x
    f.append(rect(bz0, hi - 18, bz1 - bz0, lo - hi + 36, fill="none", stroke=POS, sw=1.2, rx=4, ))
    f.append(text((bz0 + bz1) / 2, hi - 26, "брязкіт (кулька підстрибує, ~кілька мс)",
                  size=10.5, bold=True, color=POS))

    # вертикаль моменту нахилу
    f.append(line(tstart, hi - 40, tstart, lo + 60, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(tstart, lo + 76, "нахилили", size=10.5, bold=True, anchor="middle"))

    # усталена ділянка
    f.append(text((x + x1 - 180) / 2, lo + 20, "усталений «0»", size=10, color=MUTED))

    # праворуч: що бачить наївний код vs після гасіння
    gx = x1 - 150
    f.append(line(gx, hi - 40, gx, lo + 60, color=FIELD, sw=1.2, dash="3,3"))
    b1 = fitbox(gx + 6, 78, 180, 44,
                "наївний код нарахує\nбагато «спрацювань»",
                size=10, fill="#fdf0ee", stroke=POS)
    f.append(b1)
    b2 = fitbox(gx + 6, 135, 180, 44,
                "після гасіння (20–50 мс\nсталого) — ОДНА подія",
                size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b2)

    b, _, _ = textbox(W / 2, 350,
                      "debounce: приймати новий рівень лише коли він протримався сталим певний час "
                      "(довше за всі\nпідстрибування) — тоді з усього деренчання лишається рівно одне чисте спрацювання",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bounce.svg"), W, H, *f)


# ── 5. Переривання: голий брязкучий пін vs RC+Шмітт — один чистий фронт ────────
def fig_isr_chain():
    W, H = 900, 470
    f = [text(W / 2, 30, "Переривання на нахилі: голий пін дає купу хибних, RC+Шмітт — один чистий фронт",
              size=14, bold=True)]

    # спільна вісь часу для обох доріжок
    x0, x1 = 150, 560
    def waveform(y_top, hi_dy, lo_dy, edges, color, label):
        """Малюємо ламану 1↔0. edges — список (x, рівень) де рівень 1=hi, 0=lo."""
        hi, lo = y_top + hi_dy, y_top + lo_dy
        f.append(text(x0 - 16, hi + 4, "1", size=11, bold=True, anchor="end"))
        f.append(text(x0 - 16, lo + 4, "0", size=11, bold=True, anchor="end"))
        f.append(line(x0, hi, x1, hi, color="#dfe3e8", sw=0.9, dash="4,4"))
        f.append(line(x0, lo, x1, lo, color="#dfe3e8", sw=0.9, dash="4,4"))
        zz = []
        for i, (xx, lv) in enumerate(edges):
            yy = hi if lv else lo
            if i > 0:
                zz.append((xx, hi if edges[i - 1][1] else lo))  # вертикаль
            zz.append((xx, yy))
        poly = " ".join("%.1f,%.1f" % p for p in zz)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, color))
        f.append(text(x0 - 16, y_top - 6, label, size=11, bold=True, color=color, anchor="end"))

    # верхня доріжка: сирий сигнал з піна — при нахилі зубчаста черга
    ty = 90
    raw = [(x0, 1), (250, 1)]
    x = 250
    for lv, w in zip([0, 1, 0, 1, 0, 1, 0], [14, 8, 11, 6, 12, 7, 10]):
        raw.append((x, lv)); x += w; raw.append((x, lv))
    raw += [(x, 0), (x1, 0)]
    waveform(ty, 24, 66, raw, INK, "голий S")
    # позначки «фронт!» на КОЖНОМУ спадному краї — усі йдуть у переривання
    downs = [250, 250 + 14 + 8, 250 + 14 + 8 + 11 + 6]
    for dx in downs[:3]:
        f.append(arrow(dx, ty + 78, dx, ty + 96, color=POS, sw=1.4))
    f.append(text(300, ty + 112, "кожен стрибок → окреме переривання (хибні!)",
                  size=10.5, bold=True, color=POS, anchor="middle"))

    # нижня доріжка: після RC+Шмітт — один чистий спад
    by = 270
    clean = [(x0, 1), (250, 1), (262, 0), (x1, 0)]   # RC згладив, Шмітт дав один різкий спад
    waveform(by, 24, 66, clean, FIELD, "після RC+Шмітт")
    f.append(arrow(262, by + 78, 262, by + 96, color=FIELD, sw=1.6))
    f.append(text(320, by + 112, "рівно ОДИН фронт → одне переривання",
                  size=10.5, bold=True, color=FIELD, anchor="middle"))

    # праворуч — ланцюжок обробки як блоки
    bx = 610
    b1 = fitbox(bx, 96, 250, 46, "голий пін → переривання:\nбрязкіт = буря фронтів",
                size=10.5, fill="#fdf0ee", stroke=POS)
    f.append(b1)
    b2 = fitbox(bx, 250, 250, 62,
                "RC-ланка (R·C ≈ 1 мс) гладить\nсходинку, тригер Шмітта знову\nробить фронт різким",
                size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    f.append(text(bx + 125, 330, "τ = R · C,  fₒ = 1 / (2π·R·C)", size=10.5, bold=True))

    b, _, _ = textbox(W / 2, 435,
                      "переривання зривається на КОЖНОМУ фронті — тож брязкучий пін дає бурю хибних; "
                      "щоб узяти нахил на\nперериванні, спершу очисти фронт апаратно (RC + тригер Шмітта) "
                      "або лови в ISR лише факт і гаси час у loop()",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "isr-chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ball()
    fig_schematic()
    fig_wiring()
    fig_bounce()
    fig_isr_chain()
    print("OK: 5 figures ->", IMG)
