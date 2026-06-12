# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.9.9m — «Чому усереднення працює: σ/√N».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена avg-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.9.9m.k.
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


# Детермінований «шум» без random: лінійний конгруентний генератор із фіксованим
# seed, перетворений у ~гаусів через суму трьох рівномірних (наближення CLT).
# Так фігура стабільна між запусками, але «на око» виглядає випадковою.
class _RNG:
    def __init__(self, seed=12345):
        self.s = seed & 0x7fffffff

    def u(self):
        self.s = (1103515245 * self.s + 12345) & 0x7fffffff
        return self.s / 0x7fffffff

    def gauss(self):
        # сума трьох рівномірних [−0.5,0.5] → майже гаусів, σ ≈ 0.5
        return (self.u() + self.u() + self.u() - 1.5)


def _clean(t):
    """Чистий «справжній» сигнал, який ховається під шумом: один згладжений імпульс."""
    return 1.0 * math.exp(-((t - 0.52) ** 2) / (2 * 0.055)) - 0.18


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.9m.1 — режим Average на осцилографі: що більше усереднених проходів,
#  то чистіший слід. Чотири доріжки N=1, 4, 16, 64 над тим самим прихованим сигналом.
# ════════════════════════════════════════════════════════════════════════════
def fig_average_traces():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 28, "Режим Average: складаємо N проходів — шум гасне, сигнал лишається",
              18, INK, "middle", "bold")
    s += text(W / 2, 49, "Той самий слабкий імпульс під однаковим шумом; різниця лише в кількості усереднених розгорток N",
              11.5, GREY, "middle", style="italic")

    panels = [(1, "#fbe9e7"), (4, "#fdeede"), (16, "#eaf3ec"), (64, "#e6efe6")]
    px = 80
    pw = 360
    gap = 34
    py0 = 84
    ph = 78
    rng = _RNG(2024)

    Npts = 230
    sigma1 = 0.34   # σ одного проходу

    for idx, (Navg, bg) in enumerate(panels):
        py = py0 + idx * (ph + gap)
        midy = py + ph / 2
        amp = ph / 2 / 1.35

        # фон панелі
        s += rect(px, py, pw, ph, bg, FAINT, 1.2, 5)
        # нульова лінія
        s += line(px, midy, px + pw, midy, GREY, 1.0, "3,4")

        # доріжка: середнє з Navg незалежних зашумлених проходів
        pts = []
        for i in range(Npts + 1):
            t = i / Npts
            acc = 0.0
            for _ in range(Navg):
                acc += _clean(t) + 2.0 * sigma1 * rng.gauss()
            v = acc / Navg
            x = px + pw * i / Npts
            y = midy - v * amp
            pts.append((x, y))
        col = RED if Navg == 1 else (ORANGE if Navg == 4 else GREEN)
        s += polyline(pts, col, 1.7 if Navg <= 4 else 2.0)

        # підпис N зліва
        s += text(px - 14, midy + 5, f"N={Navg}", 14, col, "end", "bold")
        # позначка очікуваного σ після усереднення
        eff = sigma1 / math.sqrt(Navg)
        s += text(px + pw + 12, midy - 4, f"σ = {eff*100:.0f} (умовно)", 11, GREY, "start")
        s += text(px + pw + 12, midy + 12, f"÷√{Navg} = ÷{math.sqrt(Navg):.0f}", 11, BLUE, "start", "bold")

    # пунктир «де насправді пік» через усі панелі
    xpk = px + pw * 0.52
    s += line(xpk, py0 - 6, xpk, py0 + 3 * (ph + gap) + ph + 6, PURPLE, 1.2, "2,5")
    s += text(xpk + 5, py0 - 10, "справжній пік сигналу", 11, PURPLE, "start", "bold")

    save("avg-traces-vs-N.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.9m.2 — крива σ/√N: спадні віддачі усереднення.
#  Щоб ужужити шум удвічі, треба вчетверо більше проходів.
# ════════════════════════════════════════════════════════════════════════════
def fig_sqrt_n_curve():
    W, H = 940, 460
    s = header(W, H)
    s += text(W / 2, 28, "σ ∕ √N — закон спадних віддач усереднення",
              18, INK, "middle", "bold")
    s += text(W / 2, 49, "Шум падає як корінь із N: щоб зменшити його вдвічі, проходів треба вчетверо більше",
              11.5, GREY, "middle", style="italic")

    # осі
    ox, oy = 95, 372            # початок координат (лівий низ)
    axw, axh = 720, 290
    s += arrow(ox, oy, ox + axw + 10, oy, INK, 1.8)
    s += arrow(ox, oy, ox, oy - axh - 10, INK, 1.8)
    s += text(ox + axw + 4, oy + 22, "N (скільки усереднено)", 12.5, INK, "end", "bold")
    s += text(ox - 60, oy - axh - 2, "шум σₙ", 12.5, INK, "start", "bold")
    s += text(ox - 60, oy - axh + 16, "(відносно", 10.5, GREY, "start")
    s += text(ox - 60, oy - axh + 30, " одного)", 10.5, GREY, "start")

    Nmax = 64.0
    # вісь N — лінійна; вісь σ — від 0 до 1
    def X(n):
        return ox + axw * n / Nmax

    def Y(frac):
        return oy - axh * frac

    # сітка по N у «приємних» точках
    for n in [1, 4, 9, 16, 25, 36, 49, 64]:
        s += line(X(n), oy, X(n), oy + 5, GREY, 1.2)
        s += text(X(n), oy + 20, str(n), 11, INK, "middle")
    # сітка по σ
    for frac, lab in [(1.0, "1.0"), (0.5, "0.5"), (0.25, "0.25"), (0.125, "0.125")]:
        s += line(ox - 5, Y(frac), ox, Y(frac), GREY, 1.2)
        s += line(ox, Y(frac), ox + axw, Y(frac), FAINT, 1.0, "2,5")
        s += text(ox - 10, Y(frac) + 4, lab, 11, INK, "end")

    # сама крива 1/√N
    cpts = []
    n = 1.0
    while n <= Nmax + 0.001:
        cpts.append((X(n), Y(1.0 / math.sqrt(n))))
        n += 0.5
    s += polyline(cpts, RED, 3.2)
    s += text(X(40), Y(1.0 / math.sqrt(40)) - 12, "σₙ = σ ∕ √N", 16, RED, "middle", "bold", "italic")

    # ключові точки з підписами «у скільки разів»
    for n in [1, 4, 16, 64]:
        fr = 1.0 / math.sqrt(n)
        s += circle(X(n), Y(fr), 4.5, RED)
        s += line(X(n), oy, X(n), Y(fr), BLUE, 1.0, "3,3")
        s += line(ox, Y(fr), X(n), Y(fr), BLUE, 1.0, "3,3")
        s += text(X(n) + 8, Y(fr) - 8, f"÷{int(round(math.sqrt(n)))}", 12.5, BLUE, "start", "bold")

    # ілюстрація «вдвічі тихіше — вчетверо довше»: дужки 1→4 і 4→16
    yb = oy + 44
    s += arrow(X(1), yb, X(4), yb, GREEN, 1.8)
    s += text((X(1) + X(4)) / 2, yb - 7, "×4 проходів → ÷2 шуму", 11.5, GREEN, "middle", "bold")
    s += arrow(X(4), yb + 26, X(16), yb + 26, GREEN, 1.8)
    s += text((X(4) + X(16)) / 2, yb + 19, "ще ×4 → ще ÷2", 11.5, GREEN, "middle", "bold")

    # підпис-висновок про межу
    s += text(X(48), Y(0.16) + 30, "далі — майже дарма:", 11.5, GREY, "middle", "bold")
    s += text(X(48), Y(0.16) + 46, "крива майже лягла", 11, GREY, "middle")

    save("avg-sqrt-n-curve.svg", s)


if __name__ == "__main__":
    fig_average_traces()
    fig_sqrt_n_curve()
    print("done")
