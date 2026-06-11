# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для алгоритмічної вставки до Розділу 1.9 —
⚙️ «Шум у коді: від rand() до гаусового (Бокс—Мюллер)» (Модуль 1, до теми 1.9.1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка ⚙️ до теми 1.9.1 — секція «1a» → Рис. 1.9.1a.N.
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
PURPLE = "#7a3fae"
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
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", PURPLE: "aPurple"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


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
#  ⚙️ Вставка до теми 1.9.1 — шум у коді.  Рис. 1.9.1a.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.1a.1 — рівномірний rand() проти гаусового дзвона ─────────────────
def fig_uniform_vs_gauss():
    W, H = 1000, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дві форми випадковості: чому проста rand() — це ще не «шум»",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "rand() сипле рівно по всьому діапазону (плаский «брусок»); реальний шум юрмиться біля нуля (дзвін)",
              11.5, GREY, "middle", style="italic")

    # --- ліва панель: рівномірний розподіл ---
    ax, ay, aw, ah = 80, 350, 360, 220
    s += line(ax, ay, ax + aw, ay, INK, 2)          # вісь X
    s += line(ax, ay, ax, ay - ah, INK, 2)          # вісь Y
    s += polygon([(ax + aw, ay), (ax + aw - 12, ay - 5), (ax + aw - 12, ay + 5)], INK)
    s += polygon([(ax, ay - ah), (ax - 5, ay - ah + 12), (ax + 5, ay - ah + 12)], INK)
    # плаский «брусок» рівномірного розподілу
    top = ay - 130
    s += rect(ax + 30, top, aw - 80, ay - top, fill="#dfe7fb", stroke=BLUE, sw=2.4)
    s += text(ax + 30 + (aw - 80) / 2, top - 12, "однакова частота всюди", 12, BLUE, "middle", "bold")
    s += text(ax + aw / 2, ay + 28, "значення  →", 12.5, INK, "middle")
    s += text(ax - 10, ay - ah - 6, "частота", 12, INK, "end")
    s += text(ax + 30, ay + 18, "0", 11.5, GREY, "middle")
    s += text(ax + aw - 50, ay + 18, "1", 11.5, GREY, "middle")
    s += text(ax + aw / 2 + 10, ay - ah + 6, "rand()  →  U(0, 1)", 13.5, INK, "middle", "bold")

    # --- права панель: гаусів дзвін ---
    bx, by, bw, bh = 560, 350, 380, 220
    s += line(bx, by, bx + bw, by, INK, 2)
    s += line(bx + bw / 2, by, bx + bw / 2, by - bh, INK, 2)   # вісь по центру (нуль)
    s += polygon([(bx + bw, by), (bx + bw - 12, by - 5), (bx + bw - 12, by + 5)], INK)
    s += polygon([(bx + bw / 2, by - bh), (bx + bw / 2 - 5, by - bh + 12), (bx + bw / 2 + 5, by - bh + 12)], INK)
    # крива Гаусса
    cx0 = bx + bw / 2
    amp = 165.0
    sig_px = 52.0
    pts = []
    xx = bx + 22
    while xx <= bx + bw - 22:
        z = (xx - cx0) / sig_px
        y = by - amp * math.exp(-z * z / 2.0)
        pts.append((xx, y))
        xx += 3
    # заливка під кривою
    fillpts = [(pts[0][0], by)] + pts + [(pts[-1][0], by)]
    s += polygon(fillpts, fill="#dff0e3")
    s += polyline(pts, color=GREEN, w=3.0)
    # позначки σ
    for k, lab in ((-1, "−σ"), (1, "+σ")):
        xv = cx0 + k * sig_px
        yv = by - amp * math.exp(-0.5)
        s += line(xv, by, xv, yv, GREY, 1.6, dash="4 3")
        s += text(xv, by + 18, lab, 12, GREY, "middle", "bold")
    s += text(cx0, by + 18, "0", 11.5, GREY, "middle")
    s += text(cx0, by - amp - 12, "найчастіше — біля нуля", 12, GREEN, "middle", "bold")
    s += text(bx + bw / 2, by + 38, "відхилення від «істини»  →", 12.5, INK, "middle")
    s += text(cx0, by - bh + 6, "гаусів шум  →  N(0, σ)", 13.5, INK, "middle", "bold")

    # стрілка-перетворення між панелями
    s += arrow(ax + aw + 18, 230, bx - 18, 230, PURPLE, 3)
    s += text((ax + aw + bx) / 2, 214, "Бокс—Мюллер", 13.5, PURPLE, "middle", "bold")
    s += text((ax + aw + bx) / 2, 250, "2 рівномірні → 2 гаусові", 11, PURPLE, "middle")

    save("noisegen-uniform-vs-gauss.svg", s)


# ── Рис. 1.9.1a.2 — геометрія Бокса—Мюллера: квадрат → коло → дзвін ────────────
def fig_box_muller_geometry():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Як працює Бокс—Мюллер: два «плоских» числа задають точку, а її радіус — гаусів",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "u₁ обирає кут θ на колі, u₂ — радіус R за правилом R = √(−2·ln u₂); проєкції точки вже розподілені за Гауссом",
              11.5, GREY, "middle", style="italic")

    # --- ліва панель: одиничний квадрат двох рівномірних ---
    ax, ay, side = 70, 110, 240
    s += rect(ax, ay, side, side, fill="#eef3fd", stroke=BLUE, sw=2.2)
    s += text(ax + side / 2, ay - 14, "u₁, u₂  ~  U(0, 1)", 14, BLUE, "middle", "bold")
    s += line(ax, ay + side, ax + side + 18, ay + side, INK, 1.6)
    s += line(ax, ay, ax, ay + side + 18, INK, 1.6)
    s += text(ax + side + 22, ay + side + 4, "u₁", 12.5, INK, "start", "bold")
    s += text(ax - 8, ay - 4, "u₂", 12.5, INK, "end", "bold")
    # дві «кидані» точки
    dots = [(0.30, 0.62), (0.72, 0.28)]
    cols = [PURPLE, ORANGE]
    for (ux, uy), col in zip(dots, cols):
        px = ax + ux * side
        py = ay + (1 - uy) * side
        s += circle(px, py, 5.5, fill=col, stroke=col, w=1)
        s += line(px, ay + side, px, py, col, 1.3, dash="3 3")
        s += line(ax, py, px, py, col, 1.3, dash="3 3")

    # --- центральна панель: полярне коло ---
    cx, cy, R = 500, 235, 120
    s += circle(cx, cy, R, fill="none", stroke=FAINT, w=1.6)
    s += circle(cx, cy, R * 0.62, fill="none", stroke=FAINT, w=1.4)
    s += line(cx - R - 20, cy, cx + R + 20, cy, INK, 1.6)   # вісь z1
    s += line(cx, cy - R - 20, cx, cy + R + 20, INK, 1.6)   # вісь z2
    s += polygon([(cx + R + 20, cy), (cx + R + 8, cy - 5), (cx + R + 8, cy + 5)], INK)
    s += polygon([(cx, cy - R - 20), (cx - 5, cy - R - 8), (cx + 5, cy - R - 8)], INK)
    s += text(cx + R + 24, cy + 4, "z₁", 12.5, INK, "start", "bold")
    s += text(cx + 8, cy - R - 22, "z₂", 12.5, INK, "start", "bold")
    # точка на колі (фіолетова): кут θ, радіус r
    th = math.radians(62)
    rr = R * 0.86
    px = cx + rr * math.cos(th)
    py = cy - rr * math.sin(th)
    s += line(cx, cy, px, py, PURPLE, 2.4)
    s += circle(px, py, 6, fill=PURPLE, stroke=PURPLE, w=1)
    # дуга кута θ
    s += f'<path d="M {cx+34:.1f} {cy:.1f} A 34 34 0 0 0 {cx+34*math.cos(th):.1f} {cy-34*math.sin(th):.1f}" fill="none" stroke="{PURPLE}" stroke-width="1.8"/>\n'
    s += text(cx + 44, cy - 16, "θ = 2π·u₁", 12.5, PURPLE, "start", "bold")
    s += text((cx + px) / 2 - 10, (cy + py) / 2 - 8, "R = √(−2·ln u₂)", 12, PURPLE, "end", "bold")
    # проєкції на осі
    s += line(px, py, px, cy, GREEN, 1.6, dash="4 3")
    s += line(px, py, cx, py, GREEN, 1.6, dash="4 3")
    s += circle(px, cy, 4.5, fill=GREEN, stroke=GREEN, w=1)
    s += circle(cx, py, 4.5, fill=GREEN, stroke=GREEN, w=1)
    s += text(px, cy + 18, "z₁", 11.5, GREEN, "middle", "bold")
    s += text(cx - 12, py, "z₂", 11.5, GREEN, "end", "bold")

    # --- права панель: два гаусові виходи ---
    bx, by, bw, bh = 770, 360, 180, 230
    s += line(bx, by, bx + bw, by, INK, 1.8)
    s += line(bx + bw / 2, by, bx + bw / 2, by - bh, INK, 1.8)
    cx0 = bx + bw / 2
    amp = 150.0
    sig_px = 30.0
    pts = []
    xx = bx + 6
    while xx <= bx + bw - 6:
        z = (xx - cx0) / sig_px
        y = by - amp * math.exp(-z * z / 2.0)
        pts.append((xx, y))
        xx += 2.5
    fillpts = [(pts[0][0], by)] + pts + [(pts[-1][0], by)]
    s += polygon(fillpts, fill="#dff0e3")
    s += polyline(pts, color=GREEN, w=2.6)
    s += text(cx0, by - bh + 4, "z₁, z₂  ~  N(0, 1)", 13, GREEN, "middle", "bold")
    s += text(cx0, by + 20, "два незалежні гаусові", 11, INK, "middle")

    # стрілки між панелями
    s += arrow(ax + side + 14, cy, cx - R - 30, cy, INK, 2.4)
    s += arrow(cx + R + 30, cy, bx - 14, cy, INK, 2.4)
    s += text((ax + side + cx - R) / 2, cy - 12, "точка", 11, GREY, "middle")
    s += text((cx + R + bx) / 2 + 6, cy - 12, "проєкції", 11, GREY, "middle")

    save("noisegen-box-muller.svg", s)


if __name__ == "__main__":
    fig_uniform_vs_gauss()
    fig_box_muller_geometry()
    print("done")
