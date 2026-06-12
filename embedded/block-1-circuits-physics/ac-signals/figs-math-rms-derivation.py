# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.7.4m — «Звідки √2: середнє від sin² за період».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-7-4m-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.7.4m.k.
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


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.4m.1 — sin²(θ) гойдається між 0 і 1 коло рівня ½; площі над і під ½ рівні.
# ════════════════════════════════════════════════════════════════════════════
def fig_sin_squared_mean():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Чому ⟨sin²⟩ = ½: горби sin² ідеально лягають у западини",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "Квадрат синуса гойдається між 0 і 1; зайве над рівнем ½ рівно заповнює нестачу під ним",
              11.5, GREY, "middle", style="italic")

    # вісь
    ax, ay = 70, 330      # лівий низ (рівень 0)
    aw = 760              # ширина = 1 період (2π)
    top = 250             # висота, що відповідає значенню 1
    half_y = ay - top / 2  # рівень 0.5

    # горизонтальні рівні 0, ½, 1
    s += line(ax, ay, ax + aw, ay, GREY, 1.4)              # 0
    s += line(ax, ay - top, ax + aw, ay - top, FAINT, 1.4)  # 1
    s += text(ax - 10, ay + 5, "0", 12, GREY, "end", "bold")
    s += text(ax - 10, ay - top + 5, "1", 12, GREY, "end", "bold")

    # криві
    N = 240
    def yv(val):
        return ay - top * val

    sin2_pts = []
    sin_pts = []
    for i in range(N + 1):
        th = 2 * math.pi * i / N
        x = ax + aw * i / N
        sin2_pts.append((x, yv(math.sin(th) ** 2)))
        sin_pts.append((x, yv(0.5 + 0.5 * math.sin(th))))  # сам синус (масштабований у [0..1] для довідки)

    # заливка зон над/під ½ (показуємо взаємну компенсацію на першій чверті-горбі)
    # зона А: sin² над ½ (де sin²>½) — пофарбуємо зелено-світлим
    aboveA = [(ax, half_y)]
    belowB = [(ax, half_y)]
    for i in range(N + 1):
        th = 2 * math.pi * i / N
        x = ax + aw * i / N
        v = math.sin(th) ** 2
        if v >= 0.5:
            aboveA.append((x, yv(v)))
        else:
            aboveA.append((x, half_y))
        if v <= 0.5:
            belowB.append((x, yv(v)))
        else:
            belowB.append((x, half_y))
    aboveA.append((ax + aw, half_y))
    belowB.append((ax + aw, half_y))
    s += polygon(aboveA, "#d8efdf")     # надлишок над ½
    s += polygon(belowB, "#fde9e7")     # нестача під ½

    # лінія рівня ½ (поверх заливок)
    s += line(ax, half_y, ax + aw, half_y, GREEN, 2.2, "7,4")
    s += text(ax + aw + 6, half_y + 5, "½", 14, GREEN, "start", "bold")
    s += text(ax + aw + 6, half_y + 22, "середнє", 10.5, GREEN, "start", "bold")

    # криві поверх
    s += polyline(sin_pts, GREY, 1.6, "4,4")
    s += polyline(sin2_pts, RED, 3.0)

    # підписи кривих
    s += text(ax + 0.12 * aw, yv(0.62), "sin²θ", 15, RED, "start", "bold", "italic")
    s += text(ax + 0.30 * aw, yv(0.97) + 16, "sin θ", 12.5, GREY, "start", "bold", "italic")

    # позначки осі θ: 0, π/2, π, 3π/2, 2π
    for frac, lab in [(0.0, "0"), (0.25, "π/2"), (0.5, "π"), (0.75, "3π/2"), (1.0, "2π")]:
        x = ax + aw * frac
        s += line(x, ay, x, ay + 6, GREY, 1.4)
        s += text(x, ay + 22, lab, 11.5, GREY, "middle")
    s += text(ax + aw / 2, ay + 44, "один повний період", 12, INK, "middle", style="italic")

    # стрілки-підписи зон
    s += text(ax + 0.25 * aw, yv(0.80), "надлишок", 10.5, GREEN, "middle", "bold")
    s += text(ax + 0.50 * aw, yv(0.18), "нестача", 10.5, RED, "middle", "bold")

    save("fig-7-4m-1-sin-squared-mean.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.4m.2 — тотожність sin² = (1 − cos2θ)/2: косинус подвійного кута, опущений і вдвічі стиснутий.
# ════════════════════════════════════════════════════════════════════════════
def fig_double_angle():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 30, "sin²θ = ½ − ½·cos 2θ : той самий косинус, тільки вдвічі частіший і опущений до ½",
              16.5, INK, "middle", "bold")
    s += text(W / 2, 52, "cos 2θ за повний період має нульове середнє → лишається стала ½",
              11.5, GREY, "middle", style="italic")

    ax, ay = 70, 300
    aw = 760
    amp = 95           # піксель-амплітуда для ±1
    half_y = ay        # вісь нуля для cos-частини
    # для sin²: рівень 0 нижче, бо вона в [0..1]; покажемо обидві у спільних координатах значення
    # оберемо: значення v=0 → y=ay+ ... зробимо спільну шкалу: 1 угору = amp
    def yv(val):       # val у «фізичних» одиницях, 0 по осі ay
        return ay - amp * val

    # осі
    s += line(ax, yv(0), ax + aw, yv(0), GREY, 1.4)
    s += line(ax, yv(1.0), ax + aw, yv(1.0), FAINT, 1.2)
    s += line(ax, yv(-1.0), ax + aw, yv(-1.0), FAINT, 1.2)
    s += text(ax - 10, yv(1.0) + 5, "1", 12, GREY, "end", "bold")
    s += text(ax - 10, yv(0) + 5, "0", 12, GREY, "end", "bold")
    s += text(ax - 10, yv(-1.0) + 5, "−1", 12, BLUE, "end", "bold")
    s += text(ax - 10, yv(0.5) + 5, "½", 12, GREEN, "end", "bold")

    N = 240
    cos2_pts, sin2_pts, level_pts = [], [], []
    for i in range(N + 1):
        th = 2 * math.pi * i / N
        x = ax + aw * i / N
        cos2_pts.append((x, yv(math.cos(2 * th))))           # cos 2θ у [−1..1]
        sin2_pts.append((x, yv(math.sin(th) ** 2)))          # sin²θ у [0..1]
    # рівень ½
    s += line(ax, yv(0.5), ax + aw, yv(0.5), GREEN, 2.0, "7,4")

    # криві
    s += polyline(cos2_pts, BLUE, 2.2, "5,3")
    s += polyline(sin2_pts, RED, 3.0)

    # підписи
    s += text(ax + 0.10 * aw, yv(0.95), "cos 2θ", 14, BLUE, "start", "bold", "italic")
    s += text(ax + 0.34 * aw, yv(0.72), "sin²θ", 15, RED, "start", "bold", "italic")
    s += text(ax + aw + 6, yv(0.5) + 5, "½", 13, GREEN, "start", "bold")

    # позначки θ
    for frac, lab in [(0.0, "0"), (0.25, "π/2"), (0.5, "π"), (0.75, "3π/2"), (1.0, "2π")]:
        x = ax + aw * frac
        s += line(x, yv(0), x, yv(0) + 6, GREY, 1.4)
        s += text(x, yv(0) + 22, lab, 11.5, GREY, "middle")
    s += text(ax + aw + 6, yv(0) + 5, "θ", 13, GREY, "start", "bold", "italic")

    # пояснювальна підпис-рамка
    s += rect(ax + 0.55 * aw, yv(-0.30), 300, 70, "#f3f0f8", PURPLE, 1.5, 8)
    s += text(ax + 0.55 * aw + 150, yv(-0.30) + 24, "опусти cos 2θ на пів-амплітуди вниз", 11, PURPLE, "middle", "bold")
    s += text(ax + 0.55 * aw + 150, yv(-0.30) + 44, "і переверни — дістанеш sin²θ", 11, PURPLE, "middle")
    s += text(ax + 0.55 * aw + 150, yv(-0.30) + 62, "середнє cos 2θ = 0  ⇒  середнє sin²θ = ½", 10.5, GREEN, "middle", "bold")

    save("fig-7-4m-2-double-angle.svg", s)


if __name__ == "__main__":
    fig_sin_squared_mean()
    fig_double_angle()
    print("done")
