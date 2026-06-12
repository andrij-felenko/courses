# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.9.1m — «Випадкова величина: середнє, σ і гаусів розподіл».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-9-1m-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.9.1m.k.
НЕ чіпає головний figs.py розділу.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
PURPLE = "#7a3ea8"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def circle(cx, cy, r, fill=INK, stroke="none", sw=0):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# Детермінований «шум» без random: сума кількох синусоїд із несумірними частотами.
# Виглядає випадково, але повторюється — щоб фігура була стабільною між запусками.
def _noise(t):
    return (0.62 * math.sin(2.0 * t + 0.7)
            + 0.48 * math.sin(3.7 * t + 2.1)
            + 0.37 * math.sin(6.3 * t + 0.3)
            + 0.30 * math.sin(9.1 * t + 4.0)
            + 0.22 * math.sin(13.7 * t + 1.2)
            + 0.18 * math.sin(19.3 * t + 5.1))


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.1m.1 — від «тремтливого» сигналу до гістограми й дзвону:
#  зліва шумова доріжка в часі, праворуч — як часто трапляється кожне значення.
# ════════════════════════════════════════════════════════════════════════════
def fig_samples_to_histogram():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 28, "Шум — це випадкова величина: один сигнал, але щораз інше значення",
              18, INK, "middle", "bold")
    s += text(W / 2, 49, "Зліва — як напруга тремтить у часі; справа — як часто трапляється кожен рівень (та сама величина, погляд збоку)",
              11.5, GREY, "middle", style="italic")

    # ---- ліва панель: сигнал у часі ----
    lx, ly = 60, 360          # лівий низ осі
    lw, lh = 470, 250         # ширина (час) і повна висота поля
    midy = ly - lh / 2        # рівень середнього (0)
    scale = lh / 2 / 2.4      # 2.4 ≈ розмах шуму

    # збираємо відліки
    N = 520
    T = 26.0
    pts = []
    vals = []
    for i in range(N + 1):
        t = T * i / N
        v = _noise(t)
        x = lx + lw * i / N
        y = midy - v * scale
        pts.append((x, y))
        vals.append(v)

    # рамка-фон поля
    s += rect(lx, ly - lh, lw, lh, "#fcfcfc", FAINT, 1.4, 4)
    # рівень середнього
    s += line(lx, midy, lx + lw, midy, GREEN, 2.0, "7,4")
    s += text(lx + 6, midy - 7, "середнє μ", 12, GREEN, "start", "bold")
    # доріжка шуму
    s += polyline(pts, RED, 1.7)
    # вісь часу
    s += arrow(lx, ly + 4, lx + lw + 6, ly + 4, GREY, 1.6)
    s += text(lx + lw + 10, ly + 9, "час", 12, GREY, "start", style="italic")
    s += text(lx - 8, midy + 4, "U", 13, INK, "end", "bold", "italic")

    # кілька «миттєвих відліків» — крапки, що підкреслюють: кожен замір — одне число
    for k in range(0, N + 1, 47):
        s += circle(pts[k][0], pts[k][1], 2.4, BLUE)

    # ---- права панель: гістограма + дзвін ----
    hx0 = 600                 # лівий край поля гістограми (вісь значень — вертикальна, спільна з лівою)
    hw = 280                  # глибина «скільки разів»
    # вертикальна вісь значень тут — та сама шкала, що ліворуч (midy ± scale*v)
    # будуємо гістограму по горизонталі: bin за значенням, довжина стовпця = частота
    nb = 17
    vmin, vmax = -2.4, 2.4
    counts = [0] * nb
    for v in vals:
        b = int((v - vmin) / (vmax - vmin) * nb)
        if 0 <= b < nb:
            counts[b] += 1
    cmax = max(counts)
    binh = lh / nb

    s += text(hx0, ly - lh - 12, "скільки разів трапилось", 12, INK, "start", "bold")
    s += arrow(hx0, ly + 4, hx0 + hw + 6, ly + 4, GREY, 1.6)
    s += text(hx0 + hw + 10, ly + 9, "частота", 12, GREY, "start", style="italic")

    for b in range(nb):
        # центр біна у «значенні»
        vc = vmin + (b + 0.5) / nb * (vmax - vmin)
        yc = midy - vc * scale
        bl = hw * counts[b] / cmax
        s += rect(hx0, yc - binh / 2 + 1, bl, binh - 2, "#dbe6fa", BLUE, 1.0, 1.5)

    # накладена гаусова крива (густина), відмасштабована під cmax
    sigma_v = math.sqrt(sum(v * v for v in vals) / len(vals))
    gpts = []
    for j in range(121):
        v = vmin + (vmax - vmin) * j / 120
        g = math.exp(-0.5 * (v / sigma_v) ** 2)
        # масштаб піка під cmax (бін біля 0)
        peak = hw * (max(counts) / cmax)
        x = hx0 + g * peak
        y = midy - v * scale
        gpts.append((x, y))
    s += polyline(gpts, RED, 3.0)
    s += text(hx0 + hw - 4, midy - 1.7 * scale, "гаусів", 13, RED, "end", "bold", "italic")
    s += text(hx0 + hw - 4, midy - 1.7 * scale + 16, "дзвін", 13, RED, "end", "bold", "italic")

    # лінія середнього через обидві панелі (підкреслити спільну вісь значень)
    s += line(hx0, midy, hx0 + hw, midy, GREEN, 1.6, "7,4")

    save("fig-9-1m-1-samples-to-histogram.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.1m.2 — гаусів дзвін із поясами ±σ, ±2σ, ±3σ:
#  правило 68/95/99.7 і чому розмах ≈ 6σ.
# ════════════════════════════════════════════════════════════════════════════
def fig_sigma_bands():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 28, "σ — це ширина дзвону: де лежать майже всі значення",
              18, INK, "middle", "bold")
    s += text(W / 2, 49, "Правило 68 / 95 / 99.7 % і чому на екрані розмах шуму «на око» ≈ 6σ",
              11.5, GREY, "middle", style="italic")

    cx, baseY = W / 2, 330
    span = 360.0              # піксель на один σ (горизонтально від центру: ±3.6σ у поле)
    px_per_sigma = span / 3.6
    amp = 230.0              # висота піка в пікселях

    def X(z):
        return cx + z * px_per_sigma

    def Y(z):
        return baseY - amp * math.exp(-0.5 * z * z)

    # вісь
    s += arrow(cx - span - 30, baseY, cx + span + 30, baseY, GREY, 1.8)
    s += text(cx + span + 34, baseY + 5, "U", 13, GREY, "start", "bold", "italic")

    # заливки поясів (від країв до центру, шарами)
    def band(z0, z1, color):
        pts = [(X(z0), baseY)]
        steps = 60
        for k in range(steps + 1):
            z = z0 + (z1 - z0) * k / steps
            pts.append((X(z), Y(z)))
        pts.append((X(z1), baseY))
        s_local = polygon(pts, color)
        return s_local

    s += band(-3, 3, "#eef3df")     # ±3σ (найсвітліший, увесь)
    s += band(-2, 2, "#d8efdf")     # ±2σ
    s += band(-1, 1, "#bfe3c9")     # ±1σ (найтемніший)

    # сама крива
    cpts = []
    for k in range(241):
        z = -3.6 + 7.2 * k / 240
        cpts.append((X(z), Y(z)))
    s += polyline(cpts, RED, 3.2)

    # вертикалі на ±1,2,3σ і μ
    for z in (-3, -2, -1, 0, 1, 2, 3):
        col = GREEN if z == 0 else INK
        wdt = 2.2 if z == 0 else 1.3
        dash = None if z == 0 else "4,4"
        s += line(X(z), baseY, X(z), Y(z), col, wdt, dash)
    # підписи осі в одиницях σ
    for z, lab in [(-3, "−3σ"), (-2, "−2σ"), (-1, "−1σ"), (0, "μ"), (1, "+1σ"), (2, "+2σ"), (3, "+3σ")]:
        col = GREEN if z == 0 else INK
        s += line(X(z), baseY, X(z), baseY + 6, GREY, 1.4)
        s += text(X(z), baseY + 23, lab, 12.5, col, "middle", "bold")

    # частки під дугами
    s += text(cx, baseY - amp * 0.42, "68%", 15, "#0d5a26", "middle", "bold")
    s += text(X(-1.5), baseY - amp * 0.16, "95%", 13, "#1f8a3b", "middle", "bold")
    s += text(X(1.5), baseY - amp * 0.16, "усередині ±2σ", 10.5, "#1f8a3b", "middle")
    s += text(X(2.55), baseY - amp * 0.055, "99.7% усередині ±3σ", 10.5, GREY, "middle")

    # підпис піка
    s += text(cx, Y(0) - 10, "σ", 16, RED, "middle", "bold", "italic")
    s += arrow(cx + 6, Y(0) + 18, X(1), Y(1) + 2, INK, 1.4)
    s += text(cx + 0.5 * px_per_sigma, Y(0) + 16, "ширина = σ", 11, INK, "middle")

    # розмах ≈ 6σ (стрілка від −3σ до +3σ під віссю)
    yb = baseY + 52
    s += arrow(X(-3), yb, X(3), yb, BLUE, 1.8)
    s += arrow(X(3), yb, X(-3), yb, BLUE, 1.8)
    s += line(X(-3), baseY, X(-3), yb + 6, BLUE, 1.0, "3,3")
    s += line(X(3), baseY, X(3), yb + 6, BLUE, 1.0, "3,3")
    s += text(cx, yb - 8, "видимий розмах (peak-to-peak) ≈ 6σ", 12.5, BLUE, "middle", "bold")

    save("fig-9-1m-2-sigma-bands.svg", s)


if __name__ == "__main__":
    fig_samples_to_histogram()
    fig_sigma_bands()
    print("done")
