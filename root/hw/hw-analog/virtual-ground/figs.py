# -*- coding: utf-8 -*-
"""Фігури до статті «Віртуальна земля» (book/electronics/analog/virtual-ground).
Три фігури:
  invert.svg  — інвертувальний підсилювач: вузол X тримається на 0 В, струм тече R1→R2
  loop.svg    — механізм: щойно X відхиляється від 0, підсилювач править вихід назад
  break.svg   — де ламається: вихід уперся у шину живлення → петля розірвана, X «зриває»
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def gnd(cx, y):
    """Символ землі: вертикальний штрих + три горизонтальні рисочки."""
    out = [line(cx, y, cx, y + 8, color=INK, sw=1.8)]
    out.append(line(cx - 9, y + 8, cx + 9, y + 8, color=INK, sw=1.8))
    out.append(line(cx - 5.5, y + 12, cx + 5.5, y + 12, color=INK, sw=1.6))
    out.append(line(cx - 2.5, y + 16, cx + 2.5, y + 16, color=INK, sw=1.4))
    return "".join(out)


def opamp(cx, cy, w=64, h=72, plus_top=False):
    """Трикутник операційного підсилювача вершиною праворуч.
    Повертає (svg, in_minus_xy, in_plus_xy, out_xy). plus_top — який вхід зверху."""
    x = cx - w / 2
    p = [(x, cy - h / 2), (x, cy + h / 2), (cx + w / 2, cy)]
    pts = " ".join("%.1f,%.1f" % q for q in p)
    body = ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.8"/>'
            % (pts, FILL, LINE))
    yt, yb = cy - h / 4, cy + h / 4
    out_xy = (cx + w / 2, cy)
    if plus_top:
        body += text(x + 11, yt + 5, "+", size=16, color=POS, bold=True)
        body += text(x + 11, yb + 5, "−", size=18, color=NEG, bold=True)
        return body, (x, yb), (x, yt), out_xy
    else:
        body += text(x + 11, yt + 5, "−", size=18, color=NEG, bold=True)
        body += text(x + 11, yb + 5, "+", size=16, color=POS, bold=True)
        return body, (x, yt), (x, yb), out_xy


def resistor_h(x1, y, x2, label=None, lab_color=INK):
    """Горизонтальний резистор-зигзаг між x1 і x2 на висоті y."""
    n = 6
    seg = (x2 - x1) / (n + 1)
    pts = [(x1, y), (x1 + seg, y)]
    up = True
    for i in range(n):
        xx = x1 + seg * (i + 1) + seg / 2
        pts.append((xx, y - 7 if up else y + 7))
        up = not up
    pts.append((x2 - seg, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % q for q in pts)
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        out += text((x1 + x2) / 2, y - 13, label, size=14, color=lab_color, bold=True)
    return out


def node_dot(cx, cy, r=4):
    return circle(cx, cy, r, fill=INK, stroke=INK, sw=1)


# ── Фігура 1: інвертувальний підсилювач — вузол X на 0 В ─────────────────────
def fig_invert():
    W, H = 720, 340
    amp, in_m, in_p, out = opamp(440, 165, plus_top=False)
    xnode = (300, in_m[1])          # вузол X (інвертувальний вхід)
    out_x, out_y = out

    parts = []
    # вхідне джерело зліва
    parts.append(text(70, 130, "Uвх", size=15, color=INK, bold=True))
    parts.append(line(70, 140, 70, 165, color=INK, sw=1.8))
    parts.append(line(70, 165, 110, 165, color=INK, sw=1.8))
    # R1 від входу до вузла X
    parts.append(resistor_h(110, 165, 250, "R1", NEG))
    parts.append(line(250, 165, xnode[0], xnode[1], color=INK, sw=1.8))
    # вузол X у вхід «−»
    parts.append(line(xnode[0], xnode[1], in_m[0], in_m[1], color=INK, sw=1.8))
    parts.append(node_dot(xnode[0], xnode[1]))
    # «+» вхід на землю
    parts.append(line(in_p[0], in_p[1], in_p[0] - 40, in_p[1], color=INK, sw=1.8))
    parts.append(gnd(in_p[0] - 40, in_p[1]))
    # вихід
    parts.append(line(out_x, out_y, 600, out_y, color=INK, sw=1.8))
    parts.append(text(632, out_y + 5, "Uвих", size=15, color=INK, bold=True))
    # зворотний зв'язок R2: вихід → вгору → ліворуч над підсилювачем → у вузол X
    fb_y = 86
    parts.append(line(560, out_y, 560, fb_y, color=INK, sw=1.8))
    parts.append(resistor_h(360, fb_y, 560, "R2", POS))
    parts.append(line(360, fb_y, xnode[0], fb_y, color=INK, sw=1.8))
    parts.append(line(xnode[0], fb_y, xnode[0], xnode[1], color=INK, sw=1.8))

    parts.append(amp)

    # мітка віртуальної землі коло X
    b, bw, bh = textbox(xnode[0] - 6, 250, ["вузол X", "тримається на 0 В", "(віртуальна земля)"],
                        size=13, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK)
    parts.append(b)
    parts.append(line(xnode[0], xnode[1] + 6, xnode[0] - 6, 250 - bh / 2,
                      color=FIELD, sw=1.4, dash="3,3"))

    # напрям струму
    parts.append(arrow(150, 188, 240, 188, color=NEG, sw=1.8))
    parts.append(text(195, 205, "I", size=14, color=NEG, bold=True, italic=True))
    parts.append(arrow(540, 70, 410, 70, color=POS, sw=1.8))
    parts.append(text(475, 62, "той самий I", size=13, color=POS, bold=True))

    render(os.path.join(IMG, 'invert.svg'), W, H, *parts,
           title="Інвертувальний підсилювач: струм входу йде повз вузол X прямо в R2")
    return 'invert.svg'


# ── Фігура 2: механізм — петля повертає X на 0 ───────────────────────────────
def fig_loop():
    W, H = 720, 300
    parts = []
    cy = 150
    # чотири блоки по колу: відхилення X → велике підсилення → вихід → R2 назад
    b1 = fitbox(40, cy - 40, 150, 80,
                "X піднявся\nна +δ", size=14, fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    b2 = fitbox(255, 40, 200, 70,
                "підсилювач × (−A)\nдуже велике A", size=14, fill=FILL, stroke=LINE, color=INK, bold=True)
    b3 = fitbox(530, cy - 40, 150, 80,
                "вихід різко\nпіде вниз", size=14, fill="#fdecea", stroke=POS, color=INK, bold=True)
    b4 = fitbox(255, cy + 80, 200, 70,
                "R2 стягує X\nназад до 0", size=14, fill="#eafaf1", stroke=FIELD, color=INK, bold=True)
    parts += [b1, b2, b3, b4]

    parts.append(arrow(115, cy - 42, 300, 112, color=INK, sw=2))
    parts.append(arrow(455, 80, 600, cy - 42, color=INK, sw=2))
    parts.append(arrow(600, cy + 42, 420, cy + 92, color=INK, sw=2))
    parts.append(arrow(290, cy + 100, 115, cy + 38, color=INK, sw=2))

    parts.append(text(W / 2, cy + 8, "рівновага:", size=14, color=MUTED, anchor="middle"))
    parts.append(text(W / 2, cy + 28, "X сам осідає на 0", size=14, color=MUTED, anchor="middle", bold=True))

    render(os.path.join(IMG, 'loop.svg'), W, H, *parts,
           title="Чому X тримається на нулі: зворотний зв'язок гасить будь-яке відхилення")
    return 'loop.svg'


# ── Фігура 3: де ламається — насичення / частота ────────────────────────────
def fig_break():
    W, H = 720, 320
    parts = []
    # ліва панель: норма
    parts.append(text(180, 60, "Поки петля «жива»", size=15, color=FIELD, bold=True))
    parts.append(line(60, 230, 320, 230, color=INK, sw=1.5))       # вісь часу
    parts.append(line(60, 110, 60, 250, color=INK, sw=1.5))         # вісь напруги
    parts.append(text(48, 175, "0", size=12, color=MUTED, anchor="end"))
    parts.append(line(56, 175, 320, 175, color=MUTED, sw=1, dash="4,4"))
    # вузол X — рівна лінія коло нуля
    parts.append(line(60, 172, 320, 172, color=NEG, sw=2.4))
    parts.append(text(335, 176, "X ≈ 0", size=13, color=NEG, bold=True, anchor="start"))

    # права панель: вихід уперся в шину
    parts.append(text(540, 60, "Вихід уперся в шину", size=15, color=POS, bold=True))
    parts.append(line(420, 230, 680, 230, color=INK, sw=1.5))
    parts.append(line(420, 90, 420, 250, color=INK, sw=1.5))
    parts.append(text(408, 175, "0", size=12, color=MUTED, anchor="end"))
    parts.append(line(416, 175, 680, 175, color=MUTED, sw=1, dash="4,4"))
    parts.append(text(690, 110, "+V", size=12, color=MUTED, anchor="start"))
    parts.append(line(420, 110, 680, 110, color=POS, sw=1.4, dash="5,3"))
    # вихід наїхав на стелю
    parts.append(line(420, 200, 500, 200, color=POS, sw=2.2))
    parts.append(line(500, 200, 560, 110, color=POS, sw=2.2))
    parts.append(line(560, 110, 680, 110, color=POS, sw=2.2))
    parts.append(text(610, 128, "вихід зафіксовано", size=12, color=POS, anchor="middle"))
    # X зривається разом з ним
    parts.append(line(420, 172, 520, 172, color=NEG, sw=2.4))
    parts.append(line(520, 172, 600, 145, color=NEG, sw=2.4))
    parts.append(line(600, 145, 680, 138, color=NEG, sw=2.4))
    parts.append(text(640, 165, "X «зриває»", size=13, color=NEG, bold=True, anchor="middle"))

    b, bw, bh = textbox(W / 2, 288, ["Віртуальна земля існує, лише поки підсилювач має",
                                     "запас вихідної напруги й швидкості тримати петлю замкнутою."],
                        size=13, fill=FILL, stroke=LINE, sw=1.5, color=INK)
    parts.append(b)

    render(os.path.join(IMG, 'break.svg'), W, H, *parts,
           title="Межа: коли вихід насичується або не встигає — нуль на X зникає")
    return 'break.svg'


# ── Фігура 4 (math): баланс струмів у вузлі-нулі ─────────────────────────────
def fig_math_kcl():
    """Серце прийому: у вузол X втікає Iвх по R1, витікає Iзз по Rзз,
    у вхід підсилювача — нуль. Прирівнюємо втік = витік."""
    W, H = 720, 320
    parts = []
    xn, yn = 360, 165
    # ліва гілка: джерело Uвх → R1 → вузол
    parts.append(text(70, 130, "Uвх", size=15, color=INK, bold=True))
    parts.append(line(70, 140, 70, yn, color=INK, sw=1.8))
    parts.append(line(70, yn, 110, yn, color=INK, sw=1.8))
    parts.append(resistor_h(110, yn, 250, "R1", NEG))
    parts.append(line(250, yn, xn, yn, color=INK, sw=1.8))
    # права гілка: вузол → Rзз → вихід
    parts.append(resistor_h(xn, yn, 560, "Rзз", POS))
    parts.append(line(560, yn, 620, yn, color=INK, sw=1.8))
    parts.append(text(652, yn + 5, "Uвих", size=15, color=INK, bold=True))
    # відведення у вхід підсилювача (вниз), позначене ≈0
    parts.append(line(xn, yn, xn, yn + 50, color=MUTED, sw=1.8))
    parts.append(arrow(xn, yn + 14, xn, yn + 46, color=MUTED, sw=1.6))
    parts.append(text(xn + 70, yn + 40, "Iвх ≈ 0", size=14, color=MUTED, bold=True))
    parts.append(text(xn + 78, yn + 58, "(у вхід)", size=12, color=MUTED))
    parts.append(node_dot(xn, yn))
    # стрілки струмів
    parts.append(arrow(150, yn - 22, 235, yn - 22, color=NEG, sw=1.8))
    parts.append(text(192, yn - 30, "Iвх", size=14, color=NEG, bold=True, italic=True))
    parts.append(arrow(xn + 30, yn - 22, 540, yn - 22, color=POS, sw=1.8))
    parts.append(text(455, yn - 30, "Iзз", size=14, color=POS, bold=True, italic=True))
    # мітка нуля на вузлі
    b, bw, bh = textbox(xn, 70, ["вузол X = 0 В"], size=14,
                        fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK)
    parts.append(b)
    parts.append(line(xn, 70 + bh / 2, xn, yn - 6, color=FIELD, sw=1.4, dash="3,3"))
    # підсумкове рівняння
    b2, _, _ = textbox(W / 2, 268, ["баланс вузла:  Iвх = Iзз + Iвх(у вхід)  ≈  Iзз",
                                    "Uвх/R1 = −Uвих/Rзз   →   Uвих = −Uвх·(Rзз/R1)"],
                       size=14, fill=FILL, stroke=LINE, sw=1.5, color=INK)
    parts.append(b2)
    render(os.path.join(IMG, 'math-kcl.svg'), W, H, *parts,
           title="Прийом: прирівняти втік і витік струму у вузлі-нулі")
    return 'math-kcl.svg'


# ── Фігура 5 (math): поправка на скінченне A ─────────────────────────────────
def fig_math_finite():
    """Похибка коефіцієнта = −(1+Rзз/R1)/A. Чим менше A або більший
    «шумовий коефіцієнт» (1+Rзз/R1), тим далі реальне підсилення від ідеалу."""
    W, H = 720, 360
    parts = []
    # осі
    x0, y0 = 90, 280
    xr, yt = 660, 70
    parts.append(line(x0, y0, xr, y0, color=INK, sw=1.6))   # вісь A (лог)
    parts.append(line(x0, y0, x0, yt, color=INK, sw=1.6))   # вісь похибки
    parts.append(text(xr, y0 + 22, "підсилення A (логарифм)", size=13, color=MUTED, anchor="end"))
    parts.append(text(x0 - 8, yt - 6, "похибка |G−Gід|/Gід", size=13, color=MUTED, anchor="start"))

    import math
    # модель похибки: err = (1+G0)/A, де G0 = Rзз/R1; беремо G0=99 (підсилення 100)
    G0 = 99.0
    Amin, Amax = 1e3, 1e7
    def X(A):
        t = (math.log10(A) - math.log10(Amin)) / (math.log10(Amax) - math.log10(Amin))
        return x0 + t * (xr - x0)
    def Y(err):
        # err у відсотках, шкала 0..12 %
        e = min(err, 12.0)
        return y0 - (e / 12.0) * (y0 - yt)
    # крива
    pts = []
    A = Amin
    while A <= Amax * 1.0001:
        err = (1 + G0) / A * 100.0
        pts.append((X(A), Y(err)))
        A *= 1.18
    d = "M " + " L ".join("%.1f %.1f" % q for q in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
    # рівень 1 %
    y1 = Y(1.0)
    parts.append(line(x0, y1, xr, y1, color=MUTED, sw=1, dash="5,4"))
    parts.append(text(x0 + 4, y1 - 5, "1 %", size=12, color=MUTED, anchor="start"))
    # позначки A
    for A, lab in [(1e3, "10³"), (1e4, "10⁴"), (1e5, "10⁵"), (1e6, "10⁶"), (1e7, "10⁷")]:
        parts.append(line(X(A), y0, X(A), y0 + 5, color=INK, sw=1.2))
        parts.append(text(X(A), y0 + 20, lab, size=12, color=MUTED))
    # формула-підпис
    b, _, _ = textbox(W / 2, 330, ["похибка ≈ (1 + Rзз/R1) / A   — для підсилення 100 (Rзз/R1 = 99)"],
                      size=13, fill=FILL, stroke=LINE, sw=1.5, color=INK)
    parts.append(b)
    render(os.path.join(IMG, 'math-finite.svg'), W, H, *parts,
           title="Скінченне A: похибка коефіцієнта спадає з ростом підсилення")
    return 'math-finite.svg'


if __name__ == '__main__':
    made = [fig_invert(), fig_loop(), fig_break(),
            fig_math_kcl(), fig_math_finite()]
    print("Згенеровано:", ", ".join(made))
