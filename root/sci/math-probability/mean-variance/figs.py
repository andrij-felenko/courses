# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: середнє як точка опори ─────────────────────────────────────────
# Числа = однакові гирьки на невагомій планці; середнє — точка опори (важіль),
# на якій планка балансує: сума відхилень ліворуч = сума праворуч.
# Ідея, яку важко передати словами: середнє не "посередині списку", а ЦЕНТР
# РІВНОВАГИ моментів — тому далекий викид помітно тягне опору до себе.
def fig_balance():
    W, H = 620, 360
    ox = 60               # ліва межа осі
    axw = 500             # ширина осі значень
    beam_y = 150          # рівень планки
    data = [2, 4, 4, 6, 9]   # значення; середнє = 5.0
    mean = sum(data) / len(data)
    lo, hi = 0, 11        # діапазон осі
    def vx(v): return ox + (v - lo) / (hi - lo) * axw

    p = []

    # вісь значень із позначками
    p.append(line(ox - 6, beam_y + 60, ox + axw + 14, beam_y + 60, color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, beam_y + 60, ox + axw + 16, beam_y + 60, color=MUTED, sw=1.3))
    for v in range(lo, hi + 1):
        p.append(line(vx(v), beam_y + 56, vx(v), beam_y + 64, color=MUTED, sw=1))
        p.append(text(vx(v), beam_y + 80, str(v), 11, MUTED))
    p.append(text(ox + axw + 22, beam_y + 64, "значення", 12, MUTED, "start", italic=True))

    # планка (трохи ширша за крайні гирьки)
    bx0, bx1 = vx(data[0]) - 18, vx(data[-1]) + 18
    p.append(line(bx0, beam_y, bx1, beam_y, color=INK, sw=4))

    # гирьки-значення (однакові квадратики, що звисають з планки)
    gw = 26
    for v in data:
        gx = vx(v)
        p.append(line(gx, beam_y, gx, beam_y - 30, color=LINE, sw=1.3))   # підвіс
        p.append(rect(gx - gw / 2, beam_y - 30 - gw, gw, gw, fill=FILL, stroke=LINE, sw=1.5, rx=4))
        p.append(text(gx, beam_y - 30 - gw / 2 + 4, str(v), 12, INK, bold=True))

    # точка опори (трикутник) рівно під середнім
    mx = vx(mean)
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (mx, beam_y + 4, mx - 20, beam_y + 44, mx + 20, beam_y + 44)
    p.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (tri, "#eafaf1", FIELD))
    p.append(line(mx, beam_y, mx, beam_y + 4, color=FIELD, sw=2))
    p.append(text(mx, beam_y + 110, "середнє = 5.0", 13, FIELD, "middle", bold=True))
    p.append(line(mx, beam_y + 88, mx, beam_y + 96, color=FIELD, sw=1.2))

    # дужки: момент ліворуч = момент праворуч
    p.append(text((vx(data[0]) + mx) / 2, beam_y - 92, "відхилення вниз", 11, NEG, "middle"))
    p.append(text((mx + vx(data[-1])) / 2, beam_y - 92, "відхилення вгору", 11, POS, "middle"))
    p.append(text(W / 2, H - 8,
                  "Однакові гирьки; планка балансує на середньому — моменти ліворуч і праворуч рівні.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "balance.svg"), W, H, *p,
           title="Середнє — точка опори, на якій планка значень балансує")


# ── Фігура 2: однакове середнє, різний розкид ────────────────────────────────
# Дві серії точок з тим самим середнім 25, але різним розкидом: тісна купка
# проти широко розсіяних. Показує, що центру МАЛО — потрібне друге число.
def fig_two_spreads():
    W, H = 620, 360
    ox = 70
    axw = 470
    A = [25.0, 25.1, 24.9, 25.0, 25.0]      # тісно
    B = [21.0, 29.0, 25.0, 27.0, 23.0]      # широко
    lo, hi = 20, 30
    def vx(v): return ox + (v - lo) / (hi - lo) * axw
    yA, yB = 110, 250

    p = []

    def panel(data, y, label, col):
        out = []
        # вісь
        out.append(line(ox - 6, y, ox + axw + 12, y, color=MUTED, sw=1.2))
        for v in range(lo, hi + 1):
            out.append(line(vx(v), y - 4, vx(v), y + 4, color=MUTED, sw=1))
            if v % 2 == 0:
                out.append(text(vx(v), y + 20, str(v), 10.5, MUTED))
        # точки даних
        for v in data:
            out.append(circle(vx(v), y, 6, fill=col, stroke=col, sw=1))
        # лінія середнього (рівно 25 в обох)
        out.append(line(vx(25), y - 40, vx(25), y + 30, color=FIELD, sw=2, dash="6 4"))
        out.append(text(vx(25), y - 48, "середнє = 25", 11, FIELD, "middle", bold=True))
        # підпис серії
        out.append(text(ox - 14, y + 4, label, 13, col, "end", bold=True))
        return out

    p += panel(A, yA, "A", NEG)
    p += panel(B, yB, "B", POS)

    # ярлики розкиду
    p.append(text(ox + axw - 4, yA + 40, "тісно: σ ≈ 0.06 — надійно", 11, NEG, "end"))
    p.append(text(ox + axw - 4, yB + 40, "широко: σ ≈ 2.8 — обережно", 11, POS, "end"))

    p.append(text(W / 2, H - 8,
                  "Однакове середнє — різна довіра. Центр не каже про розкид; його міряє друге число.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "two-spreads.svg"), W, H, *p,
           title="Те саме середнє 25 — а розкид різний")


# ── Фігура 3: дзвін із поясами ±σ і ±2σ ──────────────────────────────────────
# Гаусів дзвін: центр μ задає положення, σ — ширину в тих самих одиницях.
# Пояс ±σ накриває основну масу, ±2σ — майже все. Менша σ → вужчий вищий дзвін.
def fig_sigma_band():
    W, H = 640, 360
    ox = 60
    axw = 520
    base = 280            # рівень осі (нуль густини)
    peak = 200            # висота піку над віссю
    mu_frac = 0.5         # μ посередині осі
    sigma_frac = 0.135    # σ як частка ширини осі

    def gx(frac): return ox + frac * axw            # frac ∈ [0,1]
    def gy(z): return base - peak * math.exp(-0.5 * z * z)   # z = (x−μ)/σ у "сигмах"

    mux = gx(mu_frac)
    sx = sigma_frac * axw           # σ у пікселях по осі

    p = []

    # вісь
    p.append(line(ox - 6, base, ox + axw + 14, base, color=MUTED, sw=1.3))
    p.append(arrow(ox + axw + 2, base, ox + axw + 16, base, color=MUTED, sw=1.3))
    p.append(text(ox + axw + 22, base + 4, "x", 13, MUTED, "start", italic=True))

    # межі ±σ і ±2σ у частках осі (обмежених полотном)
    def frac_at(zsig): return mu_frac + zsig * sigma_frac
    # заливка ±σ (поле — зелене)
    band = ["%.1f,%.1f" % (gx(frac_at(-1)), base)]
    z = -1.0
    while z <= 1.0001:
        band.append("%.1f,%.1f" % (gx(frac_at(z)), gy(z)))
        z += 0.05
    band.append("%.1f,%.1f" % (gx(frac_at(1)), base))
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="none"/>' % (" ".join(band), FIELD))

    # сам дзвін
    curve = []
    z = -3.0
    while z <= 3.0001:
        curve.append("%.1f,%.1f" % (gx(frac_at(z)), gy(z)))
        z += 0.04
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(curve), INK))

    # вертикаль μ
    p.append(line(mux, gy(0), mux, base, color=FIELD, sw=2, dash="6 4"))
    p.append(text(mux, base + 22, "μ (середнє)", 12, FIELD, "middle", bold=True))

    # позначки ±σ, ±2σ на осі
    for zsig, lab, col in [(-2, "−2σ", MUTED), (-1, "−σ", NEG), (1, "+σ", POS), (2, "+2σ", MUTED)]:
        x = gx(frac_at(zsig))
        p.append(line(x, base - 4, x, base + 6, color=col, sw=1.3))
        p.append(text(x, base + 22, lab, 11, col))

    # стрілка ширини ±σ під дзвоном
    ay = base - peak * 0.30
    p.append(line(gx(frac_at(-1)), ay, gx(frac_at(1)), ay, color=NEG, sw=1.4))
    p.append(arrow(gx(frac_at(-1)) + 1, ay, gx(frac_at(-1)) - 8, ay, color=NEG, sw=1.4))
    p.append(arrow(gx(frac_at(1)) - 1, ay, gx(frac_at(1)) + 8, ay, color=NEG, sw=1.4))
    p.append(text(mux, ay - 8, "ширина ±σ — основна маса", 11, NEG, "middle", bold=True))

    p.append(text(W / 2, H - 10,
                  "μ ставить центр, σ — ширину в тих самих одиницях. Менша σ → вужчий, вищий дзвін.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "sigma-band.svg"), W, H, *p,
           title="Середнє μ — центр, стандартне відхилення σ — ширина")


if __name__ == "__main__":
    fig_balance()
    fig_two_spreads()
    fig_sigma_band()
    print("Done.")
