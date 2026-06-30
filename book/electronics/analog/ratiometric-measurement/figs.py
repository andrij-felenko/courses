# -*- coding: utf-8 -*-
"""Фігури до статті «Рейтіометричне вимірювання»
(book/electronics/analog/ratiometric-measurement).
Фігури:
  drift.svg      — біда: давач і Vref живляться з РІЗНИХ джерел → просіла напруга = похибка
  cancel.svg     — ідея: одне джерело живить і давач, і Vref → джерело скорочується
  ladder.svg     — резистивний випадок: один струм крізь R_оп і давач → код = відношення опорів
  capweights.svg — (вставка math) матриця конденсаторів: кожна гілка будує частку Vref
  budget.svg     — (вставка math) бюджет похибок: що скорочується, а що ні
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def gnd(cx, y):
    return "".join([
        line(cx, y, cx, y + 7, color=INK, sw=1.8),
        line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.4),
        line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=2.0),
        line(cx - 2, y + 17, cx + 2, y + 17, color=INK, sw=1.8),
    ])


def res(cx, cy, w=20, h=46, label=None, lab_dx=None, color=INK):
    """Резистор-прямокутник (вертикальний). Повертає svg-рядок."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#ffffff", stroke=color, sw=1.8, rx=3)]
    if label:
        dx = lab_dx if lab_dx is not None else (w / 2 + 8)
        out.append(text(cx + dx, cy + 4, label, size=13, color=color, anchor="start"))
    return "".join(out)


def supply(cx, cy, label, color=POS):
    """Кружечок-джерело з підписом усередині."""
    return circle(cx, cy, 16, fill="#fdecea" if color == POS else "#eaf0fd",
                  stroke=color, sw=2) + text(cx, cy + 5, label, size=12, color=color, bold=True)


def adc_box(x, y, w=78, h=64):
    out = [rect(x, y, w, h, fill=FILL, stroke=INK, sw=1.8, rx=6),
           text(x + w / 2, y + h / 2 - 4, "АЦП", size=15, color=INK, bold=True),
           text(x + w / 2, y + h / 2 + 15, "Vвх / Vref", size=11, color=MUTED)]
    return "".join(out)


# ── Фігура 1: біда — окремий Vref дрейфує ───────────────────────────────────
def fig_drift():
    W, H = 660, 300
    out = []
    # джерело живлення давача (просіле)
    sx, sy = 95, 150
    out.append(supply(sx, sy, "Vж", POS))
    out.append(text(sx, sy - 28, "живлення", size=11, color=MUTED))
    out.append(text(sx, sy + 36, "просідає,", size=11, color=POS))
    out.append(text(sx, sy + 50, "шумить", size=11, color=POS))
    # давач-дільник
    dx = 215
    out.append(line(sx + 16, sy, dx, sy, color=POS, sw=2))
    out.append(line(dx, sy, dx, sy - 22, color=INK, sw=1.6))
    out.append(res(dx, sy - 47, label="R_дав", lab_dx=14))
    out.append(line(dx, sy - 70, dx, sy - 86, color=INK, sw=1.6))
    out.append(text(dx, sy - 92, "Vвх", size=13, color=INK, bold=True))
    out.append(line(dx, sy + 22, dx, sy + 50, color=INK, sw=1.6))
    out.append(gnd(dx, sy + 50))
    # сигнал у АЦП
    ax, ay = 365, sy - 16
    out.append(arrow(dx + 6, sy - 86, ax - 2, ay - 20, color=INK))
    out.append(adc_box(ax, ay - 32))
    # окреме опорне джерело — НЕ зв'язане
    rx, ry = ax + 39, ay + 78
    out.append(supply(rx, ry, "Vref", NEG))
    out.append(text(rx, ry + 28, "власне, стабільне,", size=11, color=MUTED))
    out.append(text(rx, ry + 42, "але НЕ те саме", size=11, color=NEG))
    out.append(arrow(rx, ry - 16, ax + 39, ay + 32 + 2, color=NEG))
    # вихід-біда
    bx = ax + 78 + 24
    out.append(arrow(ax + 78, ay, bx, ay, color=INK))
    box, bw, bh = textbox(bx + 90, ay, "код пливе разом\nз Vж — ПОХИБКА",
                          size=12, color=POS, stroke=POS, fill="#fdecea")
    out.append(box)
    render(os.path.join(IMG, 'drift.svg'), W, H, *out,
           title="Окремий Vref: дрейф живлення тече прямо в результат")


# ── Фігура 2: ідея — спільне джерело, скорочення ────────────────────────────
def fig_cancel():
    W, H = 740, 330
    out = []
    sx, sy = 95, 150
    out.append(supply(sx, sy, "Vж", FIELD))
    out.append(text(sx, sy - 30, "одне джерело", size=11, color=MUTED))
    out.append(text(sx, sy + 42, "хай дрейфує —", size=11, color=FIELD))
    out.append(text(sx, sy + 58, "однаково", size=11, color=FIELD))
    # розгалуження
    jx = 175
    out.append(line(sx + 16, sy, jx, sy, color=FIELD, sw=2.4))
    out.append(circle(jx, sy, 3.2, fill=FIELD, stroke=FIELD, sw=1))
    # гілка вгору — давач
    dx = 270
    out.append(line(jx, sy, jx, sy - 70, color=FIELD, sw=2.2))
    out.append(line(jx, sy - 70, dx, sy - 70, color=FIELD, sw=2.2))
    out.append(line(dx, sy - 70, dx, sy - 55, color=INK, sw=1.6))
    out.append(res(dx, sy - 30, label="R_дав", lab_dx=14))
    out.append(line(dx, sy - 5, dx, sy + 18, color=INK, sw=1.6))
    out.append(text(dx + 6, sy - 78, "Vвх", size=13, color=INK, bold=True, anchor="start"))
    out.append(gnd(dx, sy + 18))
    out.append(text(dx - 4, sy - 78, "Vвх = R_дав/(R_дав+…)·Vж", size=10, color=MUTED, anchor="end"))
    # гілка вниз — той самий Vж як Vref
    out.append(line(jx, sy, jx, sy + 70, color=FIELD, sw=2.2))
    out.append(line(jx, sy + 70, dx, sy + 70, color=FIELD, sw=2.2))
    out.append(text(dx + 6, sy + 74, "Vref = Vж", size=12, color=FIELD, bold=True, anchor="start"))
    # АЦП
    ax, ay = 400, sy - 32
    out.append(arrow(dx + 6, sy - 70, ax - 2, ay - 22, color=INK))
    out.append(arrow(dx + 70, sy + 70, ax + 39, ay + 64, color=FIELD))
    out.append(adc_box(ax, ay))
    # вихід — скорочення
    bx = ax + 78 + 28
    out.append(arrow(ax + 78, ay + 32, bx, ay + 32, color=INK))
    box, bw, bh = textbox(bx + 92, ay + 32,
                          "код = R_дав/(R_дав+R)\nVж зникло — СТАБІЛЬНО",
                          size=12, color=FIELD, stroke=FIELD, fill="#eafaf0")
    out.append(box)
    render(os.path.join(IMG, 'cancel.svg'), W, H, *out,
           title="Спільне джерело: Vж стоїть і в Vвх, і в Vref — і скорочується")


# ── Фігура 3: резистивний ланцюг — код = відношення опорів ──────────────────
def fig_ladder():
    W, H = 600, 350
    out = []
    cx = 170
    # джерело струму: кружечок зі стрілкою вгору
    ix, iy = cx, 78
    out.append(circle(ix, iy, 17, fill="#fdecea", stroke=POS, sw=2))
    out.append(arrow(ix, iy + 9, ix, iy - 9, color=POS, sw=2.2))
    out.append(text(ix - 26, iy + 4, "I", size=15, color=POS, bold=True, anchor="end"))
    out.append(text(ix, iy - 28, "джерело струму", size=11, color=MUTED))
    out.append(text(ix, iy + 38, "точність I — байдужа", size=11, color=FIELD))
    # вертикальний стовп: I → R_оп → R_дав → земля
    yA = 118
    out.append(line(cx, iy + 17, cx, yA, color=POS, sw=2))
    out.append(circle(cx, yA, 3.2, fill=INK, stroke=INK, sw=1))
    out.append(res(cx, yA + 35))
    out.append(text(cx + 18, yA + 39, "R_оп (точний)", size=12, color=INK, anchor="start"))
    yB = yA + 70
    out.append(line(cx, yA + 35 + 23, cx, yB, color=INK, sw=1.6))
    out.append(circle(cx, yB, 3.2, fill=INK, stroke=INK, sw=1))
    out.append(res(cx, yB + 35, color=NEG))
    out.append(text(cx + 18, yB + 39, "R_дав (давач)", size=12, color=NEG, anchor="start"))
    yC = yB + 70
    out.append(line(cx, yB + 35 + 23, cx, yC, color=INK, sw=1.6))
    out.append(gnd(cx, yC))
    # відведення напруг ліворуч
    out.append(line(cx - 14, yA, cx - 55, yA, color=INK, sw=1.4, dash="4 3"))
    out.append(line(cx - 14, yB, cx - 55, yB, color=INK, sw=1.4, dash="4 3"))
    out.append(text(cx - 60, (yA + yB) / 2 + 4, "Vref = I·R_оп", size=12, color=INK, anchor="end"))
    out.append(line(cx - 14, yB, cx - 100, yB, color=NEG, sw=1.4, dash="4 3"))
    out.append(line(cx - 14, yC, cx - 100, yC, color=NEG, sw=1.4, dash="4 3"))
    out.append(text(cx - 105, (yB + yC) / 2 + 4, "Vвх = I·R_дав", size=12, color=NEG, anchor="end"))
    # АЦП праворуч
    ax, ay = 405, 178
    out.append(rect(ax, ay - 28, 92, 70, fill=FILL, stroke=INK, sw=1.8, rx=6))
    out.append(text(ax + 46, ay - 5, "АЦП", size=15, color=INK, bold=True))
    out.append(text(ax + 46, ay + 17, "Vвх/Vref", size=11, color=MUTED))
    out.append(arrow(cx + 95, yA, ax - 2, ay - 18, color=INK))
    out.append(text((cx + ax) / 2 + 40, yA - 8, "Vref → опорний", size=10, color=MUTED))
    out.append(arrow(cx + 95, yB, ax - 2, ay + 22, color=NEG))
    out.append(text((cx + ax) / 2 + 40, yB + 24, "Vвх → вхід", size=10, color=MUTED))
    # результат
    box, bw, bh = textbox(ax + 46, ay + 100,
                          "код = R_дав / R_оп\nI скоротилось",
                          size=12, color=FIELD, stroke=FIELD, fill="#eafaf0")
    out.append(box)
    render(os.path.join(IMG, 'ladder.svg'), W, H, *out,
           title="Один струм крізь R_оп і давач: АЦП читає відношення опорів")


# ── Вставка math: конденсатор-символ ────────────────────────────────────────
def cap_sym(cx, cy, w=34, plate_gap=7, color=INK):
    """Конденсатор-символ (горизонтальні пластини), центр (cx,cy)."""
    half = w / 2
    return "".join([
        line(cx - half, cy - plate_gap, cx + half, cy - plate_gap, color=color, sw=2.6),
        line(cx - half, cy + plate_gap, cx + half, cy + plate_gap, color=color, sw=2.6),
    ])


# ── Вставка math, фігура 1: матриця конденсаторів будує частки Vref ──────────
def fig_capweights():
    W, H = 720, 360
    out = []
    busx0, busx1, busy = 70, 560, 96
    out.append(line(busx0, busy, busx1, busy, color=INK, sw=2.6))
    out.append(text(busx0 - 4, busy - 10, "вузол Vx  (вхід компаратора)", size=12,
                    color=INK, bold=True, anchor="start"))
    cmpx = 605
    out.append(line(busx1, busy, cmpx, busy, color=INK, sw=2.2))
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" '
           'stroke-width="1.8"/>' % (cmpx, busy - 22, cmpx, busy + 22, cmpx + 44, busy, FILL, INK))
    out.append(tri)
    out.append(text(cmpx + 14, busy + 4, ">", size=16, color=INK, bold=True))
    out.append(text(cmpx + 22, busy - 30, "Vx ⋛ 0 ?", size=11, color=MUTED))

    labels = [
        ("2³C", "Vref·8/16 = Vref/2", "старший біт b₃"),
        ("2²C", "Vref·4/16 = Vref/4", "b₂"),
        ("2¹C", "Vref·2/16 = Vref/8", "b₁"),
        ("2⁰C", "Vref·1/16 = Vref/16", "молодший біт b₀"),
    ]
    xs = [130, 250, 370, 490]
    capy = busy + 64
    swy = capy + 70
    railG = swy + 34
    for (xc, (wlab, frac, blab)) in zip(xs, labels):
        out.append(line(xc, busy, xc, capy - 7, color=INK, sw=1.8))
        out.append(cap_sym(xc, capy))
        out.append(text(xc - 22, capy + 4, wlab, size=12, color=NEG, bold=True, anchor="end"))
        out.append(line(xc, capy + 7, xc, swy - 6, color=INK, sw=1.8))
        out.append(circle(xc, swy - 6, 2.6, fill=INK, stroke=INK, sw=1))
        out.append(line(xc, swy - 6, xc + 16, swy + 8, color=POS, sw=2.2))
        out.append(circle(xc + 16, swy + 8, 2.6, fill=POS, stroke=POS, sw=1))
        out.append(circle(xc - 16, swy + 8, 2.6, fill=MUTED, stroke=MUTED, sw=1))
        out.append(text(xc, railG + 22, frac, size=10.5, color=FIELD, anchor="middle"))
        out.append(text(xc, railG + 38, blab, size=10, color=MUTED, anchor="middle"))

    out.append(text(xs[0] - 70, swy + 8, "до «0»", size=10, color=MUTED, anchor="end"))
    out.append(text(xs[-1] + 70, swy + 8, "до Vref", size=10, color=POS, anchor="start"))
    out.append(line(xs[0] - 64, swy + 8, xs[0] - 30, swy + 8, color=MUTED, sw=1.4, dash="3 3"))
    out.append(line(xs[-1] + 30, swy + 8, xs[-1] + 64, swy + 8, color=POS, sw=1.4, dash="3 3"))

    render(os.path.join(IMG, 'capweights.svg'), W, H, *out,
           title="Матриця конденсаторів: кожна гілка додає у Vx частку Vref")


# ── Вставка math: рамка-джерело Vж ──────────────────────────────────────────
def _supply_box(x, y):
    return (rect(x, y - 18, 54, 36, fill="#eafaf0", stroke=FIELD, sw=2, rx=6) +
            text(x + 27, y + 5, "Vж", size=14, color=FIELD, bold=True))


# ── Вставка math, фігура 2: бюджет похибок — що скорочується, що ні ──────────
def fig_budget():
    W, H = 720, 400
    out = []
    sx, sy = 80, 120
    out.append(_supply_box(sx, sy))
    jx = 230
    out.append(line(sx + 54, sy, jx, sy, color=FIELD, sw=2.6))
    out.append(circle(jx, sy, 3.4, fill=FIELD, stroke=FIELD, sw=1))
    out.append(text(jx, sy - 14, "розгалуження", size=11, color=MUTED))
    out.append(line(jx, sy, jx, sy - 46, color=FIELD, sw=2.2))
    out.append(line(jx, sy - 46, jx + 120, sy - 46, color=FIELD, sw=2.2))
    out.append(text(jx + 126, sy - 42, "сигнал → Vвх", size=12, color=INK, bold=True, anchor="start"))
    out.append(line(jx, sy, jx, sy + 46, color=FIELD, sw=2.2))
    out.append(line(jx, sy + 46, jx + 120, sy + 46, color=FIELD, sw=2.2))
    out.append(text(jx + 126, sy + 50, "опора → Vref", size=12, color=NEG, bold=True, anchor="start"))

    colY = 210
    bx, _, _ = textbox(190, colY, "СКОРОЧУЄТЬСЯ", size=13, color=FIELD,
                       stroke=FIELD, fill="#eafaf0", bold=True, min_w=180)
    out.append(bx)
    good = [
        "дрейф самої шини Vж",
        "— один і той самий вузол",
        "до розгалуження: один струм I,",
        "одне джерело — тотожні до біта",
    ]
    for i, ln in enumerate(good):
        out.append(text(190, colY + 34 + i * 22, ln, size=11.5,
                        color=(FIELD if i in (0, 2) else MUTED), anchor="middle"))

    bx2, _, _ = textbox(528, colY, "НЕ СКОРОЧУЄТЬСЯ", size=13, color=POS,
                        stroke=POS, fill="#fdecea", bold=True, min_w=220)
    out.append(bx2)
    bad = [
        "шум, доданий ПІСЛЯ розгалуження",
        "— різний на Vвх і Vref",
        "часове розузгодження вибірки",
        "— два різні значення Vж у мить t",
        "точність опорного резистора R_оп",
        "— це новий еталон системи",
    ]
    for i, ln in enumerate(bad):
        out.append(text(528, colY + 34 + i * 22, ln, size=11.5,
                        color=(POS if i % 2 == 0 else MUTED), anchor="middle"))

    render(os.path.join(IMG, 'budget.svg'), W, H, *out,
           title="Бюджет похибок: спільне до розгалуження зникає, решта лишається")


if __name__ == '__main__':
    fig_drift()
    fig_cancel()
    fig_ladder()
    fig_capweights()
    fig_budget()
    print("OK: drift.svg, cancel.svg, ladder.svg, capweights.svg, budget.svg")
