# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def resistor(x, y, w=46, h=14, label=None, lblsize=13):
    """Горизонтальний резистор-зигзаг від (x,y) завдовжки w, центрований по y."""
    n = 6
    seg = w / n
    pts = [(x, y)]
    for i in range(n):
        px = x + seg * (i + 0.5)
        py = y - h / 2 if i % 2 == 0 else y + h / 2
        pts.append((px, py))
    pts.append((x + w, y))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        out += text(x + w / 2, y - h / 2 - 6, label, size=lblsize, bold=True)
    return out


def cap_to_gnd(x, y, label=None, lblsize=13):
    """Конденсатор від вузла (x,y) вниз на землю."""
    out = line(x, y, x, y + 16, INK, 1.8)
    out += line(x - 12, y + 16, x + 12, y + 16, INK, 2.2)   # верхня пластина
    out += line(x - 12, y + 22, x + 12, y + 22, INK, 2.2)   # нижня пластина
    out += line(x, y + 22, x, y + 34, INK, 1.8)
    # земля
    out += line(x - 13, y + 34, x + 13, y + 34, INK, 2)
    out += line(x - 8, y + 39, x + 8, y + 39, INK, 2)
    out += line(x - 3, y + 44, x + 3, y + 44, INK, 2)
    if label:
        out += text(x + 18, y + 22, label, size=lblsize, bold=True, anchor="start")
    return out


def node_dot(x, y, r=3.2):
    return circle(x, y, r, fill=INK, stroke=INK, sw=1)


# ── Фігура 1: наївна помилка — друга ланка п'є струм із вузла першої ──────────
def fig_naive():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Чому дві ланки поспіль — не два незалежні дільники", size=17, bold=True))

    yw = 150           # рівень верхнього дроту
    x0 = 70            # вхід
    # вхід Uвх
    f.append(text(x0 - 8, yw - 14, "Uвх", size=13, bold=True, color=POS, anchor="end"))
    f.append(line(x0 - 4, yw, x0 + 6, yw, INK, 1.8))
    f.append(plus(x0 - 4, yw, 8))

    # R1
    xr1 = x0 + 30
    f.append(resistor(xr1, yw, 54, label="R1"))
    nx1 = xr1 + 54 + 18   # вузол 1
    f.append(line(xr1 + 54, yw, nx1, yw, INK, 1.8))
    f.append(node_dot(nx1, yw))
    f.append(text(nx1, yw - 30, "вузол A", size=12, bold=True, color=FIELD))
    # C1 з вузла 1
    f.append(cap_to_gnd(nx1, yw, "C1"))

    # R2 далі по дроту
    xr2 = nx1 + 18
    f.append(line(nx1, yw, xr2, yw, INK, 1.8))
    f.append(resistor(xr2, yw, 54, label="R2"))
    nx2 = xr2 + 54 + 18   # вузол 2 / вихід
    f.append(line(xr2 + 54, yw, nx2, yw, INK, 1.8))
    f.append(node_dot(nx2, yw))
    f.append(cap_to_gnd(nx2, yw, "C2"))
    f.append(text(nx2 + 18, yw - 14, "Uвих", size=13, bold=True, anchor="start"))

    # стрілка струму, що відгалужується у R2 з вузла A
    f.append(text(nx1 + 28, yw + 14, "i₂", size=14, bold=True, color=POS, italic=True))
    f.append('<path d="M %.1f %.1f q 16 12 30 0" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % (nx1 + 4, yw + 6, POS))

    # пояснення в рамці
    f.append(fitbox(60, 235, 600, 95,
        "Друга ланка під'єднана ПРЯМО до вузла A — і тягне з нього струм i₂.\n"
        "Тому напруга на C1 уже НЕ та, що в одинокого дільника R1C1:\n"
        "R2 і C2 «висять» паралельно до C1 і змінюють його ділення.\n"
        "Висновок: відгук двох ланок поспіль ≠ добуток двох окремих відгуків.",
        size=14, fill="#fdecea", stroke=POS))
    render(os.path.join(OUT, "naive-cascade.svg"), W, H, *f)


# ── Фігура 2: АЧХ — одна ланка, ідеальний добуток, реальна некерована ────────
def fig_response():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 26, "АЧХ: чого справді чекати від двох ланок", size=17, bold=True))

    # осі (log-log ескіз)
    ox, oy = 95, 320      # початок осей (низ-ліво)
    pw, ph = 560, 240     # робоче поле
    f.append(line(ox, oy, ox + pw, oy, INK, 1.8))           # вісь частоти
    f.append(line(ox, oy, ox, oy - ph, INK, 1.8))           # вісь підсилення
    f.append(text(ox + pw, oy + 22, "частота (лог)", size=12, anchor="end"))
    f.append(text(ox - 8, oy - ph + 4, "K, дБ", size=12, anchor="end"))

    # рівень 0 дБ
    y0 = oy - ph + 30
    f.append(line(ox, y0, ox + pw, y0, MUTED, 1, dash="4 4"))
    f.append(text(ox - 8, y0 + 4, "0", size=11, anchor="end", color=MUTED))
    # рівень -3 дБ
    y3 = y0 + 22
    f.append(text(ox - 8, y3 + 4, "−3", size=11, anchor="end", color=MUTED))
    # рівень -6 дБ
    y6 = y0 + 44
    f.append(text(ox - 8, y6 + 4, "−6", size=11, anchor="end", color=MUTED))

    # позиція зрізу fc (одинокої ланки)
    xc = ox + 250
    f.append(line(xc, oy, xc, y0, MUTED, 1, dash="3 3"))
    f.append(text(xc, oy + 18, "fc", size=12, bold=True, color=MUTED, italic=True))

    # 1) одна ланка: плато 0 дБ до fc, далі -20 дБ/дек (полога пряма)
    p1 = "M %.1f %.1f L %.1f %.1f L %.1f %.1f" % (ox, y0, xc, y0, ox + pw, y0 + 120)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (p1, NEG))
    f.append(text(ox + pw - 4, y0 + 108, "одна ланка  −20 дБ/дек", size=12, bold=True, color=NEG, anchor="end"))

    # 2) ідеальний добуток (буфер): той самий зріз, але -40 дБ/дек (крутіша)
    p2 = "M %.1f %.1f L %.1f %.1f L %.1f %.1f" % (ox, y0, xc, y0, ox + pw, y0 + 185)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (p2, FIELD))
    f.append(text(ox + pw - 4, y0 + 183, "з буфером  −40 дБ/дек", size=12, bold=True, color=FIELD, anchor="end"))

    # 3) реальна некерована: зріз раніше (зсунутий ліворуч), плече просіло
    xc2 = ox + 175    # зсунутий зріз
    # плавна крива: рано починає падати, до fc вже помітно нижче, далі ~-40
    p3 = ("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f"
          % (ox, y0 - 1, xc2 - 30, y0, xc2 + 30, y3 + 6, xc, y6 + 8, ox + pw, y0 + 175))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p3, POS))
    f.append(text(ox + 150, y6 + 30, "реальна, без буфера", size=12, bold=True, color=POS))
    f.append(text(ox + 150, y6 + 46, "зріз нижчий, плече просіло", size=11, color=POS))
    f.append(line(xc2, oy, xc2, y3 + 6, POS, 1, dash="3 3"))
    f.append(text(xc2, oy + 18, "fc′ < fc", size=11, bold=True, color=POS, italic=True))

    render(os.path.join(OUT, "cascade-response.svg"), W, H, *f)


# ── Фігура 3: лікування — буфер між ланками ──────────────────────────────────
def fig_buffer():
    W, H = 740, 330
    f = []
    f.append(text(W / 2, 26, "Буфер між ланками робить відгук добутком", size=17, bold=True))

    yw = 145
    x0 = 60
    f.append(text(x0 - 6, yw - 14, "Uвх", size=12, bold=True, color=POS, anchor="end"))
    f.append(plus(x0 - 2, yw, 7))

    # ланка 1
    xr1 = x0 + 22
    f.append(resistor(xr1, yw, 48, label="R1"))
    n1 = xr1 + 48 + 14
    f.append(line(xr1 + 48, yw, n1, yw, INK, 1.8))
    f.append(node_dot(n1, yw))
    f.append(cap_to_gnd(n1, yw, "C1"))

    # буфер — трикутник (повторювач ×1)
    bx = n1 + 22
    bw, bh = 64, 54
    tri = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (bx, yw - bh / 2, bx, yw + bh / 2, bx + bw, yw)
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (tri, FILL, INK))
    f.append(line(n1, yw, bx, yw, INK, 1.8))
    f.append(text(bx + 20, yw + 4, "×1", size=14, bold=True))
    f.append(text(bx + bw / 2, yw - bh / 2 - 8, "буфер", size=12, bold=True, color=FIELD))

    # ланка 2
    xr2 = bx + bw + 16
    f.append(line(bx + bw, yw, xr2, yw, INK, 1.8))
    f.append(resistor(xr2, yw, 48, label="R2"))
    n2 = xr2 + 48 + 14
    f.append(line(xr2 + 48, yw, n2, yw, INK, 1.8))
    f.append(node_dot(n2, yw))
    f.append(cap_to_gnd(n2, yw, "C2"))
    f.append(text(n2 + 16, yw - 14, "Uвих", size=12, bold=True, anchor="start"))

    # підписи зон
    f.append(text(n1 - 24, yw - 40, "ланка 1", size=12, bold=True, color=NEG))
    f.append(text(xr2 + 24, yw - 40, "ланка 2", size=12, bold=True, color=NEG))

    f.append(fitbox(70, 225, 600, 78,
        "Повторювач має ВЕЛИЧЕЗНИЙ вхідний опір — майже не бере струму з C1,\n"
        "і МАЛИЙ вихідний — живить R2 «від себе». Ланки більше не бачать одна одну.\n"
        "Тепер чесно: K(f) = K₁(f) · K₂(f), кожен зріз там, де поставили.",
        size=14, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, "buffer-fix.svg"), W, H, *f)


# ── Фігура 4: правило імпедансів 10× ─────────────────────────────────────────
def fig_impedance():
    W, H = 700, 320
    f = []
    f.append(text(W / 2, 26, "Дешеве правило без буфера: розв'язати імпедансами", size=17, bold=True))

    # ліва коробка — вихід ланки 1
    f.append(fitbox(60, 70, 250, 120,
        "Ланка 1\nвихідний опір\n≈ R1\n(на низьких частотах)",
        size=15, fill="#eaf0fd", stroke=NEG, bold=False))
    # права коробка — вхід ланки 2
    f.append(fitbox(390, 70, 250, 120,
        "Ланка 2\nвхідний опір\n≈ R2 + (Xc2)\n— на зрізі ~ R2",
        size=15, fill="#fdf3ea", stroke="#b9770e", bold=False))

    # стрілка між ними з умовою
    f.append('<line x1="315" y1="130" x2="385" y2="130" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % INK)
    f.append(text(350, 118, "живить", size=12, color=MUTED))

    # умова знизу
    f.append(fitbox(120, 215, 460, 70,
        "Щоб ланка 2 майже не навантажувала ланку 1:\n"
        "R2  ≥  10 · R1     — тоді відгук ≈ добуток, без буфера.",
        size=16, fill="#eafaf0", stroke=FIELD, bold=True))
    render(os.path.join(OUT, "impedance-rule.svg"), W, H, *f)


if __name__ == "__main__":
    fig_naive()
    fig_response()
    fig_buffer()
    fig_impedance()
    print("figs done")
