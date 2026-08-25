# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: чому квадрат ───────────────────────────────────────────────────
# Синусоїда v(t) (може бути від'ємна) та її квадрат v²(t) — завжди ≥ 0.
# Горизонтальна лінія = середнє квадрата = ½ (для одиничної амплітуди).
# Ідея, яку важко передати словами: миттєва потужність ∝ v², тож саме
# СЕРЕДНЄ КВАДРАТА, а не середнє самого сигналу (воно нуль), несе тепло.
def fig_why_square():
    W, H = 620, 400
    ox = 70          # ліва межа графіка (x=0)
    axw = 500        # ширина по осі t
    # верхня половина — сам сигнал; нижня — квадрат
    midtop = 120     # рівень нуля для v(t)
    ampv = 70        # амплітуда v у px (±1 → ±70)
    base2 = 372      # рівень нуля для v²(t)
    amp2 = 150       # висота для v²=1 у px

    def tx(frac): return ox + frac * axw          # frac ∈ [0,1] → x
    def vy(v): return midtop - v * ampv           # v ∈ [-1,1]
    def sqy(s): return base2 - s * amp2           # s ∈ [0,1]

    p = []

    # — верхня панель: v(t) = sin —
    p.append(line(ox - 8, vy(0), ox + axw + 14, vy(0), color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, vy(0), ox + axw + 16, vy(0), color=MUTED, sw=1.3))
    p.append(text(ox + axw + 22, vy(0) + 4, "t", 13, MUTED, "start", italic=True))
    p.append(line(ox, vy(1.25), ox, vy(-1.25), color=MUTED, sw=1.3))
    # позначки +1, -1
    p.append(line(ox - 4, vy(1), ox + 4, vy(1), color=MUTED, sw=1))
    p.append(text(ox - 9, vy(1) + 4, "+1", 11, MUTED, "end"))
    p.append(line(ox - 4, vy(-1), ox + 4, vy(-1), color=MUTED, sw=1))
    p.append(text(ox - 9, vy(-1) + 4, "−1", 11, MUTED, "end"))

    N = 200
    sine = []
    for i in range(N + 1):
        f = i / N
        sine.append("%.1f,%.1f" % (tx(f), vy(math.sin(2 * math.pi * f))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(sine), NEG))
    p.append(text(tx(0.5), vy(1) - 12, "v(t)", 13, NEG, "middle", bold=True))
    p.append(text(ox + axw - 4, vy(0) - 8,
                  "середнє(v) = 0  →  нічого не каже про тепло", 11, MUTED, "end"))

    # — нижня панель: v²(t) —
    p.append(line(ox - 8, sqy(0), ox + axw + 14, sqy(0), color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, sqy(0), ox + axw + 16, sqy(0), color=MUTED, sw=1.3))
    p.append(text(ox + axw + 22, sqy(0) + 4, "t", 13, MUTED, "start", italic=True))
    p.append(line(ox, sqy(0) + 4, ox, sqy(1.15), color=MUTED, sw=1.3))
    p.append(line(ox - 4, sqy(1), ox + 4, sqy(1), color=MUTED, sw=1))
    p.append(text(ox - 9, sqy(1) + 4, "1", 11, MUTED, "end"))

    # заливка під квадратом (підкреслює «площу = тепло»)
    fillpts = ["%.1f,%.1f" % (tx(0), sqy(0))]
    sq = []
    for i in range(N + 1):
        f = i / N
        s = math.sin(2 * math.pi * f) ** 2
        fillpts.append("%.1f,%.1f" % (tx(f), sqy(s)))
        sq.append("%.1f,%.1f" % (tx(f), sqy(s)))
    fillpts.append("%.1f,%.1f" % (tx(1), sqy(0)))
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.12" stroke="none"/>'
             % (" ".join(fillpts), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(sq), POS))
    p.append(text(tx(0.25), sqy(1) - 10, "v²(t) ≥ 0", 13, POS, "middle", bold=True))

    # лінія середнього квадрата = ½
    p.append(line(ox, sqy(0.5), ox + axw, sqy(0.5), color=FIELD, sw=2.2, dash="7 4"))
    p.append(text(ox + axw - 4, sqy(0.5) - 7,
                  "середнє(v²) = ½", 12, FIELD, "end", bold=True))

    # підпис-стрілка зв'язку
    p.append(text(W / 2, H - 8,
                  "Сам сигнал в середньому нульовий; його квадрат — ні. Тепло несе саме середнє квадрата.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "why-square.svg"), W, H, *p,
           title="Чому квадрат: середнє самого сигналу = 0, середнє квадрата — ні")


# ── Фігура 2: рецепт √(середнє(x²)) як конвеєр ───────────────────────────────
# Три кроки загальної формули: піднести в квадрат → усереднити → взяти корінь.
# Показує, звідки в назві «корінь із середнього квадрата» — і в якому порядку.
def fig_recipe():
    W, H = 660, 250
    p = []

    cy = 120
    bw, bh = 150, 78
    gap = 38
    x0 = 24

    boxes = [
        (POS,   "1. КВАДРАТ", ["x  →  x²", "знак зник,", "великі — важчі"]),
        (FIELD, "2. СЕРЕДНЄ", ["усереднити", "x² за період", "(або за вибіркою)"]),
        (NEG,   "3. КОРІНЬ",  ["√ середнього", "повертає", "одиниці x"]),
    ]
    cxs = []
    for i, (col, head, body) in enumerate(boxes):
        bx = x0 + i * (bw + gap)
        cxs.append(bx + bw / 2)
        # рамка
        p.append(rect(bx, cy - bh / 2, bw, bh, fill="#ffffff", stroke=col, sw=2.0, rx=8))
        # шапка
        p.append(rect(bx, cy - bh / 2, bw, 22, fill=col, stroke=col, sw=0, rx=8))
        p.append(text(bx + bw / 2, cy - bh / 2 + 16, head, 13, "#ffffff", "middle", bold=True))
        # тіло
        p.append(mtext(bx + bw / 2, cy - bh / 2 + 38, body, 11, INK, "middle", lh=1.25))

    # стрілки між боксами
    for i in range(len(boxes) - 1):
        x1 = x0 + i * (bw + gap) + bw + 4
        x2 = x0 + (i + 1) * (bw + gap) - 4
        p.append(arrow(x1, cy, x2, cy, color=INK, sw=2.0))

    # підсумкова формула під конвеєром
    p.append(text(W / 2, cy + bh / 2 + 42,
                  "RMS = √( середнє( x² ) )",
                  19, INK, "middle", bold=True))
    p.append(text(W / 2, cy + bh / 2 + 64,
                  "читається справа наліво: спершу квадрат, потім середнє, наприкінці корінь",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "recipe.svg"), W, H, *p,
           title="Рецепт RMS: квадрат → середнє → корінь")


# ── Фігура 3: однакове тепло — синус Vpk і постійна Vpk/√2 ───────────────────
# Два резистори: на одному змінна напруга амплітуди Vpk, на другому постійна
# 0.707·Vpk. Виділяють однакову потужність — це й означає «діюче значення».
def fig_equal_heating():
    W, H = 620, 360
    p = []

    # — лівий блок: змінна напруга —
    Lx = 150
    axw = 200
    top = 90
    amp = 56
    zero = top + amp + 10        # рівень 0 для синуса

    def lx(frac): return Lx - axw / 2 + frac * axw
    def ly(v): return zero - v * amp

    p.append(text(Lx, 56, "Змінна:  v(t) = Vpk·sin", 13, NEG, "middle", bold=True))
    p.append(line(lx(0) - 6, ly(0), lx(1) + 8, ly(0), color=MUTED, sw=1.2))
    p.append(line(lx(0), ly(1.2), lx(0), ly(-1.2), color=MUTED, sw=1.2))
    N = 160
    sine = []
    for i in range(N + 1):
        f = i / N
        sine.append("%.1f,%.1f" % (lx(f), ly(math.sin(2 * math.pi * f))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(sine), NEG))
    # пік
    p.append(line(lx(0) - 4, ly(1), lx(0) + 4, ly(1), color=MUTED, sw=1))
    p.append(text(lx(0) - 8, ly(1) + 4, "Vpk", 11, NEG, "end"))
    # рівень RMS пунктиром
    rms = 0.7071
    p.append(line(lx(0), ly(rms), lx(1), ly(rms), color=FIELD, sw=1.8, dash="6 4"))
    p.append(text(lx(1) + 6, ly(rms) + 4, "0.707·Vpk", 10.5, FIELD, "start", bold=True))

    # — правий блок: постійна напруга —
    Rx = 470
    p.append(text(Rx, 56, "Постійна:  V = 0.707·Vpk", 13, FIELD, "middle", bold=True))
    p.append(line(Rx - axw / 2 - 6, ly(0), Rx + axw / 2 + 8, ly(0), color=MUTED, sw=1.2))
    p.append(line(Rx - axw / 2, ly(1.2), Rx - axw / 2, ly(-1.2), color=MUTED, sw=1.2))
    p.append(line(Rx - axw / 2, ly(rms), Rx + axw / 2, ly(rms), color=FIELD, sw=2.6))
    p.append(line(Rx - axw / 2 - 4, ly(1), Rx - axw / 2 + 4, ly(1), color=MUTED, sw=1))
    p.append(text(Rx - axw / 2 - 8, ly(1) + 4, "Vpk", 11, MUTED, "end"))

    # — нижній рядок: однакова потужність у той самий резистор —
    by = 250
    lb = fitbox(Lx - 110, by, 220, 58,
                "Середня потужність\nP = Vpk² / (2R)",
                size=13, fill="#fdecea", stroke=POS, color=INK, bold=False)
    p.append(lb)
    rb = fitbox(Rx - 110, by, 220, 58,
                "Стала потужність\nP = (0.707·Vpk)² / R = Vpk²/(2R)",
                size=12, fill="#eafaf1", stroke=FIELD, color=INK, bold=False)
    p.append(rb)

    # знак рівності між блоками
    p.append(text(W / 2, by + 34, "=", 30, INK, "middle", bold=True))
    p.append(text(W / 2, by - 14, "однакове тепло", 12, INK, "middle", bold=True))

    p.append(text(W / 2, H - 10,
                  "Постійні 0.707·Vpk гріють резистор так само, як синус амплітуди Vpk — це і є «діюче» значення.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "equal-heating.svg"), W, H, *p,
           title="Діюче значення: однакове тепло від синуса й від постійної")


if __name__ == "__main__":
    fig_why_square()
    fig_recipe()
    fig_equal_heating()
    print("Done.")
