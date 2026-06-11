# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки §1.4.8m «Матриця як машина перетворень».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-4-8m-mm-*), щоб не зачепити головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано локально (за §9 — самодостатність).
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
PURPLE = "#7a3ea8"
ORANGE = "#e08030"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="mInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="mRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="mBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="mGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="mPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'  <marker id="mGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "mInk", RED: "mRed", BLUE: "mBlue", GREEN: "mGreen", PURPLE: "mPurple", GREY: "mGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "mInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>\n')


# ── фігура 1: матриця як машина «вектор → вектор» ──────────────────────────
# Ліворуч сітка-вхід з вектором v=(2,1); коробка-машина M; праворуч
# деформована сітка з вектором Mv. Показуємо, що відбувається з базисом.

def fig_machine():
    W, H = 760, 360
    s = []
    s.append(header(W, H))
    s.append(text(W / 2, 26, "Матриця M — це машина: бере вектор, повертає вектор",
                  size=17, anchor="middle", weight="bold"))

    # параметри панелей
    cellsL = 26.0          # піксель на одиницю (вхід)
    # ── ЛІВА панель: вхідна площина ──
    Lx, Ly = 70, 300       # початок координат (origin) лівої панелі
    def Lp(x, y):
        return (Lx + x * cellsL, Ly - y * cellsL)
    # сітка 0..4 x 0..4
    for k in range(0, 5):
        s.append(line(*Lp(k, 0), *Lp(k, 4), color=FAINT, w=1))
        s.append(line(*Lp(0, k), *Lp(4, k), color=FAINT, w=1))
    # осі
    s.append(arrow(*Lp(0, 0), *Lp(4.4, 0), color=GREY, w=1.6))
    s.append(arrow(*Lp(0, 0), *Lp(0, 4.4), color=GREY, w=1.6))
    # базисні вектори e1, e2
    s.append(arrow(*Lp(0, 0), *Lp(1, 0), color=RED, w=3))
    s.append(arrow(*Lp(0, 0), *Lp(0, 1), color=BLUE, w=3))
    s.append(text(*Lp(1.05, 0.30), "e₁", size=13, color=RED, weight="bold"))
    s.append(text(*Lp(0.12, 1.18), "e₂", size=13, color=BLUE, weight="bold"))
    # вектор v = (2,1)
    s.append(arrow(*Lp(0, 0), *Lp(2, 1), color=PURPLE, w=3.4))
    s.append(text(*Lp(2.05, 1.18), "v = (2, 1)", size=13, color=PURPLE, weight="bold"))
    s.append(text(Lx + 2 * cellsL, Ly + 26, "вхідна площина", size=12,
                  color=GREY, anchor="middle"))

    # ── машина-коробка ──
    bx, by, bw, bh = 320, 150, 120, 70
    s.append(rect(bx, by, bw, bh, fill="#f3eefb", stroke=PURPLE, sw=2.2, rx=10))
    s.append(text(bx + bw / 2, by + 24, "M =", size=14, anchor="middle", weight="bold"))
    s.append(text(bx + bw / 2, by + 48, "[1  1]", size=14, anchor="middle"))
    s.append(text(bx + bw / 2, by + 64, "[0  1]", size=14, anchor="middle"))
    s.append(arrow(255, 150, bx - 6, 175, color=INK, w=2.4))
    s.append(arrow(bx + bw + 6, 175, 525, 150, color=INK, w=2.4))
    s.append(text(bx + bw / 2, by - 12, "«зсув» (shear)", size=12, anchor="middle",
                  color=PURPLE, style="italic"))

    # ── ПРАВА панель: вихідна площина (та сама сітка, перекошена) ──
    Rx, Ry = 545, 300
    M = ((1, 1), (0, 1))
    def Rp(x, y):
        nx = M[0][0] * x + M[0][1] * y
        ny = M[1][0] * x + M[1][1] * y
        return (Rx + nx * cellsL, Ry - ny * cellsL)
    for k in range(0, 5):
        s.append(line(*Rp(k, 0), *Rp(k, 4), color=FAINT, w=1))
        s.append(line(*Rp(0, k), *Rp(4, k), color=FAINT, w=1))
    s.append(arrow(*Rp(0, 0), *Rp(4.4, 0), color=GREY, w=1.6))
    s.append(arrow(*Rp(0, 0), *Rp(0, 4.4), color=GREY, w=1.6))
    # куди поїхав базис: e1 лишився, e2 став стовпцем 2 = (1,1)
    s.append(arrow(*Rp(0, 0), *Rp(1, 0), color=RED, w=3))
    s.append(arrow(*Rp(0, 0), *Rp(0, 1), color=BLUE, w=3))
    s.append(text(*Rp(1.05, -0.30), "M·e₁ = стовпець 1", size=11, color=RED))
    s.append(text(*Rp(0.10, 1.30), "M·e₂ = стовпець 2", size=11, color=BLUE))
    # образ вектора
    s.append(arrow(*Rp(0, 0), *Rp(2, 1), color=PURPLE, w=3.4))
    s.append(text(*Rp(2.0, 1.35), "Mv = (3, 1)", size=13, color=PURPLE, weight="bold"))
    s.append(text(Rx + 2 * cellsL, Ry + 26, "вихідна площина", size=12,
                  color=GREY, anchor="middle"))

    s.append(footer())
    with open(os.path.join(OUT, "fig-4-8m-mm-1-machine.svg"), "w", encoding="utf-8") as f:
        f.write("".join(s))


# ── фігура 2: порядок важить — поворот×розтяг ≠ розтяг×поворот ──────────────

def fig_order():
    W, H = 760, 470
    s = []
    s.append(header(W, H))
    s.append(text(W / 2, 26, "Порядок важить: R·S ≠ S·R (та сама фігура, різний результат)",
                  size=16, anchor="middle", weight="bold"))

    u = 30.0  # масштаб

    def shape_unit():
        # «прапорець»: квадрат 0..1 з зубцем — несиметричний, щоб видно поворот
        return [(0, 0), (1, 0), (1, 1), (0.5, 1.4), (0, 1)]

    def apply(M, pts):
        out = []
        for (x, y) in pts:
            out.append((M[0][0] * x + M[0][1] * y, M[1][0] * x + M[1][1] * y))
        return out

    def matmul(A, B):
        return (
            (A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]),
            (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]),
        )

    th = math.radians(50)
    R = ((math.cos(th), -math.sin(th)), (math.sin(th), math.cos(th)))   # поворот 50°
    S = ((2.0, 0.0), (0.0, 0.7))                                        # розтяг x2, стиск y

    def draw_panel(cx, cy, pts, fill, title, sub):
        # локальні осі
        s.append(line(cx - 12, cy, cx + 130, cy, color=FAINT, w=1))
        s.append(line(cx, cy + 70, cx, cy - 90, color=FAINT, w=1))
        scr = [(cx + x * u, cy - y * u) for (x, y) in pts]
        s.append(polygon(scr, fill=fill, stroke=INK, sw=1.8, opacity=0.6))
        s.append(text(cx + 60, cy + 92, title, size=13, anchor="middle", weight="bold"))
        if sub:
            s.append(text(cx + 60, cy + 110, sub, size=11, anchor="middle", color=GREY))

    base = shape_unit()

    # вихідна фігура (зверху по центру)
    draw_panel(330, 110, base, GREEN, "вихідна фігура", "одиничний «прапорець»")

    # ── гілка А: спершу S, потім R  → застосовуємо (R·S) ──
    RS = matmul(R, S)
    draw_panel(120, 320, apply(RS, base), "#cfe3ff", "R·S  (спершу розтяг, тоді поворот)",
               "розтягнутий, далі повернутий")
    s.append(arrow(300, 150, 175, 250, color=BLUE, w=2.2))
    s.append(text(205, 195, "R·S", size=13, color=BLUE, weight="bold"))

    # ── гілка Б: спершу R, потім S → застосовуємо (S·R) ──
    SR = matmul(S, R)
    draw_panel(540, 320, apply(SR, base), "#ffd9d2", "S·R  (спершу поворот, тоді розтяг)",
               "повернутий, далі розтягнутий")
    s.append(arrow(360, 150, 545, 250, color=RED, w=2.2))
    s.append(text(470, 195, "S·R", size=13, color=RED, weight="bold"))

    # підпис-висновок
    s.append(text(W / 2, 458,
                  "Множення матриць читають праворуч-наліво; інша черга — інша геометрія.",
                  size=12, anchor="middle", color=PURPLE, style="italic"))

    s.append(footer())
    with open(os.path.join(OUT, "fig-4-8m-mm-2-order.svg"), "w", encoding="utf-8") as f:
        f.write("".join(s))


if __name__ == "__main__":
    fig_machine()
    fig_order()
    print("OK: fig-4-8m-mm-1-machine.svg, fig-4-8m-mm-2-order.svg")
