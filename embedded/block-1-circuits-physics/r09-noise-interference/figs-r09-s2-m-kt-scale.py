# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.9.2m — «kT як універсальний масштаб:
26 меВ і больцманівський фактор».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-r09-s2m-kt-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.9.2m.k.
НЕ чіпає головний figs.py розділу й сусідні скрипти.
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


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.2m.1 — енергетична лінійка: kT(300K) ≈ 26 меВ на тлі інших
#  характерних енергій (логарифмічна вісь). Показує, чому 26 меВ — «масштаб».
# ════════════════════════════════════════════════════════════════════════════
def fig_energy_ruler():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "kT при кімнатній температурі ≈ 26 меВ — це «лінійка» теплової енергії",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "Кожне зерно речовини теліпається з енергією порядку kT; з нею порівнюють усі бар'єри й рівні",
              11.5, GREY, "middle", style="italic")

    # горизонтальна логарифмічна вісь енергії (в еВ)
    ax = 90
    aw = 760
    ybar = 250
    emin_log = math.log10(1e-3)    # 1 меВ
    emax_log = math.log10(2.0)     # 2 еВ

    def X(eV):
        f = (math.log10(eV) - emin_log) / (emax_log - emin_log)
        return ax + aw * f

    # вісь
    s += arrow(ax - 10, ybar, ax + aw + 22, ybar, INK, 2.0)
    s += text(ax + aw + 26, ybar + 5, "енергія", 12.5, INK, "start", "bold", "italic")
    # поділки декад: 1, 10, 100 меВ, 1 еВ
    for eV, lab in [(1e-3, "1 меВ"), (1e-2, "10 меВ"), (1e-1, "100 меВ"), (1.0, "1 еВ")]:
        x = X(eV)
        s += line(x, ybar - 6, x, ybar + 6, GREY, 1.4)
        s += text(x, ybar + 24, lab, 11.5, GREY, "middle")
        # світла вертикаль-сітка
        s += line(x, ybar - 6, x, 90, FAINT, 1.0)

    # «прапорці» характерних енергій (зверху й знизу від осі — щоб не злипались)
    # (значення: підпис, енергія еВ, колір, рівень над/під, висота)
    marks = [
        ("теплова kT (300 K) ≈ 26 меВ", 0.02585, RED, +1, 150),
        ("ширина забороненої зони\nкремнію ≈ 1.12 еВ", 1.12, PURPLE, +1, 95),
        ("пряме падіння на діоді\n≈ 0.6–0.7 еВ (≈ 0.65 еВ)", 0.65, GREEN, -1, 92),
        ("видиме світло\n≈ 1.6–3.1 еВ (тут край ≈ 1.8 еВ)", 1.8, ORANGE, +1, 150),
        ("один тепловий «крок» kT", 0.02585, INK, -1, 0),  # лише підкреслити
    ]

    # окрема велика мітка kT
    xkt = X(0.02585)
    # стовпчик-«стрижень» kT (від осі вгору)
    s += line(xkt, ybar, xkt, ybar - 150, RED, 3.2)
    s += circle(xkt, ybar - 150, 4.5, RED)
    s += rect(xkt - 96, ybar - 188, 192, 30, "#fbe9e7", RED, 1.6, 6)
    s += text(xkt, ybar - 168, "kT ≈ 26 меВ", 14.5, RED, "middle", "bold")
    s += text(xkt, ybar - 16, "↑", 15, RED, "middle", "bold")

    # ширина забороненої зони кремнію
    xg = X(1.12)
    s += line(xg, ybar, xg, ybar - 95, PURPLE, 2.6)
    s += circle(xg, ybar - 95, 4.0, PURPLE)
    s += text(xg, ybar - 104, "Si: E_g ≈ 1.12 еВ", 12, PURPLE, "middle", "bold")

    # діод
    xd = X(0.65)
    s += line(xd, ybar, xd, ybar + 70, GREEN, 2.6)
    s += circle(xd, ybar + 70, 4.0, GREEN)
    s += text(xd, ybar + 86, "діод: U_F ≈ 0.65 еВ", 12, GREEN, "middle", "bold")

    # видиме світло (фотон)
    xl = X(1.8)
    s += line(xl, ybar, xl, ybar + 70, ORANGE, 2.6)
    s += circle(xl, ybar + 70, 4.0, ORANGE)
    s += text(xl, ybar + 86, "фотон світла ≳ 1.8 еВ", 12, ORANGE, "middle", "bold")

    # відстань у «kT» від теплової до бар'єрів — показати, чому переходи рідкі
    yan = 360
    s += line(xkt, ybar + 96, xkt, yan, GREY, 1.0, "3,3")
    s += line(xd, ybar + 96, xd, yan, GREY, 1.0, "3,3")
    s += arrow(xkt, yan, xd, yan, BLUE, 1.8)
    s += text((xkt + xd) / 2, yan - 8, "≈ 25 kT", 12.5, BLUE, "middle", "bold")
    s += text((xkt + xd) / 2, yan + 18,
              "бар'єр діода — десятки kT над тепловим шумом", 11.5, BLUE, "middle")

    # підсумкова рамка-висновок
    s += rect(120, 405, 700, 46, "#eef5ff", BLUE, 1.4, 8)
    s += text(470, 426,
              "Усе, що менше за kT, тепло легко «перестрибує»; усе, що в десятки kT, —",
              12.5, INK, "middle")
    s += text(470, 444,
              "стабільне, бо ймовірність стрибка падає як exp(−ΔE/kT).",
              12.5, INK, "middle", "bold")

    save("fig-r09-s2m-kt-1-energy-ruler.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.2m.2 — больцманівський фактор exp(−ΔE/kT): чому всюди експоненти.
#  Графік exp(−x), де x = ΔE/kT; позначки на 1,2,3,5 kT з числами.
# ════════════════════════════════════════════════════════════════════════════
def fig_boltzmann_factor():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Больцманівський фактор: кожні «kT» бар'єра ділять шанс ще на e ≈ 2.72",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "Імовірність того, що тепловий стрибок дасть енергію ΔE, спадає як exp(−ΔE / kT)",
              11.5, GREY, "middle", style="italic")

    # осі
    ox, oy = 110, 380          # початок (низ-ліво)
    pw, ph = 700, 290          # поле
    xmax = 6.0                 # до 6 kT
    def X(x):
        return ox + pw * x / xmax
    def Y(p):                  # p від 0 до 1
        return oy - ph * p

    # сітка по осі X (одиниці kT)
    for k in range(0, 7):
        x = X(k)
        s += line(x, oy, x, oy - ph, FAINT, 1.0)
        s += line(x, oy, x, oy + 6, GREY, 1.4)
        lab = "0" if k == 0 else f"{k}·kT"
        s += text(x, oy + 24, lab, 12, GREY, "middle")
    # сітка по осі Y (частки)
    for p, lab in [(0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1.0")]:
        y = Y(p)
        s += line(ox, y, ox + pw, y, FAINT, 1.0)
        s += line(ox - 6, y, ox, y, GREY, 1.4)
        s += text(ox - 12, y + 4, lab, 11.5, GREY, "end")

    # осі
    s += arrow(ox, oy, ox + pw + 22, oy, INK, 2.0)
    s += arrow(ox, oy, ox, oy - ph - 18, INK, 2.0)
    s += text(ox + pw + 26, oy + 5, "ΔE / kT", 12.5, INK, "start", "bold", "italic")
    s += text(ox - 70, oy - ph - 4, "exp(−ΔE/kT)", 12.5, INK, "start", "bold", "italic")
    s += text(ox - 70, oy - ph + 13, "(відносний шанс)", 10.5, GREY, "start", style="italic")

    # крива exp(-x)
    cpts = []
    for j in range(241):
        x = xmax * j / 240
        cpts.append((X(x), Y(math.exp(-x))))
    s += polyline(cpts, RED, 3.2)

    # ключові точки з числами
    pts = [
        (1, "при ΔE = 1·kT:  e⁻¹ ≈ 0.37", BLUE),
        (2, "2·kT:  e⁻² ≈ 0.14", GREEN),
        (3, "3·kT:  e⁻³ ≈ 0.05", PURPLE),
        (5, "5·kT:  e⁻⁵ ≈ 0.007", ORANGE),
    ]
    for x0, lab, col in pts:
        y0 = Y(math.exp(-x0))
        s += line(X(x0), oy, X(x0), y0, col, 1.4, "4,4")
        s += line(ox, y0, X(x0), y0, col, 1.4, "4,4")
        s += circle(X(x0), y0, 5.0, col)

    # підписи точок (розкладено, щоб не злипались)
    s += text(X(1) + 12, Y(math.exp(-1)) - 6, "e⁻¹ ≈ 0.37", 12.5, BLUE, "start", "bold")
    s += text(X(2) + 12, Y(math.exp(-2)) - 4, "e⁻² ≈ 0.14", 12.5, GREEN, "start", "bold")
    s += text(X(3) + 12, Y(math.exp(-3)) - 8, "e⁻³ ≈ 0.05", 12.5, PURPLE, "start", "bold")
    s += text(X(5) + 12, Y(math.exp(-5)) - 8, "e⁻⁵ ≈ 0.007", 12.5, ORANGE, "start", "bold")

    # «кожен крок ділить на e» — позначити рівні падіння
    s += rect(X(2.6), 96, 230, 70, "#fbe9e7", RED, 1.4, 8)
    s += text(X(2.6) + 115, 118, "кожен +kT до бар'єра —", 12, INK, "middle")
    s += text(X(2.6) + 115, 137, "× (1/e), тобто ÷ 2.72", 12.5, RED, "middle", "bold")
    s += text(X(2.6) + 115, 156, "три kT → лишилось ≈ 5 %", 11.5, INK, "middle")

    save("fig-r09-s2m-kt-2-boltzmann-factor.svg", s)


if __name__ == "__main__":
    fig_energy_ruler()
    fig_boltzmann_factor()
    print("done")
