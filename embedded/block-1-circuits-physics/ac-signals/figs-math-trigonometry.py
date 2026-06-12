# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки до теми 1.7.1 —
«Синус і коло: тригонометрія обертання» (Модуль 1, Розділ 7).
Чистий Python, без залежностей. Вивід → ./img/ із УНІКАЛЬНИМИ іменами
(префікс fig-7-1m-…), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті — Рис. 1.7.1m.k.
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.0, dash=None):
    """Дуга кола (без стрілки) між кутами; кути в стандартній матем. орієнтації (CCW від +x)."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy - r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy - r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 0 if a1_deg > a0_deg else 1   # y-вісь донизу → CCW = sweep 0
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n')


def _arc_arrow(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.0):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy - r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy - r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 0 if a1_deg > a0_deg else 1
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.1m.1 — одиничне коло: cos θ і sin θ як КООРДИНАТИ точки
# ════════════════════════════════════════════════════════════════════════════
def fig_unit_circle():
    W, H = 920, 452
    s = header(W, H)
    s += text(W / 2, 28, "Одиничне коло: cos θ і sin θ — це просто координати точки",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "на колі радіуса 1 точка під кутом θ має координати (cos θ, sin θ); та сама точка біжить — а sin θ гойдається синусоїдою",
              11, GREY, "middle", style="italic")

    # ── ліворуч: одиничне коло ──
    cx, cy, R = 210, 235, 145
    s += circle(cx, cy, R, "none", FAINT, 1.8)
    s += arrow(cx - R - 28, cy, cx + R + 32, cy, GREY, 1.4)       # вісь x
    s += arrow(cx, cy + R + 28, cx, cy - R - 32, GREY, 1.4)       # вісь y
    s += text(cx + R + 30, cy + 18, "x", 12, GREY, "middle", "bold", "italic")
    s += text(cx + 18, cy - R - 24, "y", 12, GREY, "middle", "bold", "italic")
    # позначка радіуса 1 на осі
    s += line(cx + R, cy - 4, cx + R, cy + 4, GREY, 1.4)
    s += text(cx + R, cy + 18, "1", 10.5, GREY, "middle", "bold")

    ang = 52
    a = math.radians(ang)
    px, py = cx + R * math.cos(a), cy - R * math.sin(a)
    # радіус-вектор (гіпотенуза = 1)
    s += arrow(cx, cy, px, py, INK, 2.8)
    s += circle(px, py, 4.5, INK, INK, 1)
    s += text((cx + px) / 2 - 14, (cy + py) / 2 - 6, "1", 12.5, INK, "middle", "bold", "italic")
    # катети: cos θ (горизонталь, червоний-ish → INK), sin θ (вертикаль)
    s += line(cx, py, px, py, RED, 2.6)                            # cos: від осі y до точки (горизонт.)
    s += line(px, cy, px, py, BLUE, 2.6)                           # sin: вертикальний катет
    # проєкції на осі (пунктир)
    s += line(px, py, px, cy, BLUE, 1.3, "4,3")
    s += line(px, py, cx, py, RED, 1.3, "4,3")
    s += circle(px, cy, 4.0, RED, RED, 1)
    s += circle(cx, py, 4.0, BLUE, BLUE, 1)
    # підписи катетів/проєкцій
    s += text((cx + px) / 2, cy + 20, "cos θ", 12.5, RED, "middle", "bold", "italic")
    s += text(cx - 8, py - 4, "sin θ", 12.5, BLUE, "end", "bold", "italic")
    # кут θ
    s += _arc(cx, cy, 40, 0, ang, GREEN, 2.0)
    s += text(cx + 50, cy - 16, "θ", 13, GREEN, "start", "bold", "italic")
    # маленький прямокутний кут біля основи
    s += rect(px - 12, cy - 12, 12, 12, "none", GREY, 1.2)
    s += text(cx, cy + R + 56, "точка на колі = (cos θ, sin θ)", 11.5, INK, "middle", "bold")

    # ── праворуч: розгортка sin θ у синусоїду ──
    ax, ay, aw = 430, 235, 430
    s += arrow(ax, ay, ax + aw + 14, ay, GREY, 1.4)
    s += arrow(ax, ay + R + 14, ax, ay - R - 14, GREY, 1.4)
    s += text(ax + aw + 10, ay + 18, "θ", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - R - 8, "sin θ", 11, BLUE, "end", "bold", "italic")
    # синусоїда (один період на aw)
    pts = []
    n = 160
    for i in range(n + 1):
        t = i / n
        x = ax + t * aw
        y = ay - R * math.sin(2 * math.pi * t)
        pts.append((x, y))
    s += polyline(pts, BLUE, 2.8)
    # нитка від поточної проєкції sin θ до точки на хвилі
    cur_x = ax + (ang / 360.0) * aw
    cur_y = ay - R * math.sin(a)
    s += line(cx, py, ax, py, BLUE, 1.2, "4,3")
    s += line(ax, py, cur_x, cur_y, BLUE, 1.2, "4,3")
    s += circle(cur_x, cur_y, 4.5, BLUE, BLUE, 1)
    # рівні ±1
    s += line(ax, ay - R, ax + aw, ay - R, FAINT, 1.2, "3,3")
    s += line(ax, ay + R, ax + aw, ay + R, FAINT, 1.2, "3,3")
    s += text(ax + aw - 4, ay - R - 5, "+1", 10, INK, "end", "bold")
    s += text(ax + aw - 4, ay + R + 14, "−1", 10, INK, "end", "bold")
    # позначки на осі θ: π/2, π, 3π/2, 2π
    for frac, lab in ((0.25, "π/2"), (0.5, "π"), (0.75, "3π/2"), (1.0, "2π")):
        xx = ax + frac * aw
        s += line(xx, ay - 4, xx, ay + 4, GREY, 1.3)
        s += text(xx, ay + 20, lab, 10, GREY, "middle")
    s += text(ax + aw / 2, ay + R + 56, "повний оберт по колу = один період синусоїди",
              11, INK, "middle", "bold")
    save("fig-7-1m-1-unit-circle.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.1m.2 — радіани: кут = довжина дуги / радіус; sin і cos зсунуті на 90°
# ════════════════════════════════════════════════════════════════════════════
def fig_radian_and_shift():
    W, H = 920, 428
    s = header(W, H)
    s += text(W / 2, 28, "Радіан і зсув на чверть оберту: чому з'являється 2π і де ховається косинус",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "радіан — це коли довжина дуги дорівнює радіусу; повний оберт = 2π; косинус — той самий синус, зсунутий на 90°",
              11, GREY, "middle", style="italic")

    # ── ліворуч: радіан (дуга = радіус) ──
    cx, cy, R = 195, 230, 120
    s += circle(cx, cy, R, "none", FAINT, 1.8)
    s += line(cx - R - 22, cy, cx + R + 26, cy, GREY, 1.3)
    s += line(cx, cy + R + 22, cx, cy - R - 26, GREY, 1.3)
    # радіус 0
    s += line(cx, cy, cx + R, cy, INK, 2.4)
    # радіус під 1 радіан (≈57.3°)
    one = 1.0
    px, py = cx + R * math.cos(one), cy - R * math.sin(one)
    s += line(cx, cy, px, py, INK, 2.4)
    # дуга довжини R (= один радіан), виділена кольором
    s += _arc(cx, cy, R, 0, math.degrees(one), RED, 3.4)
    # позначки «R» на двох радіусах і на дузі
    s += text(cx + R / 2, cy + 18, "R", 12, INK, "middle", "bold", "italic")
    s += text(cx + R * 0.55 * math.cos(one) - 14, cy - R * 0.55 * math.sin(one), "R",
              12, INK, "middle", "bold", "italic")
    s += text(cx + (R + 22) * math.cos(one / 2), cy - (R + 22) * math.sin(one / 2),
              "дуга = R", 11, RED, "middle", "bold")
    s += _arc(cx, cy, 34, 0, math.degrees(one), GREEN, 2.0)
    s += text(cx + 44, cy - 14, "1 рад", 11, GREEN, "start", "bold", "italic")
    s += text(cx, cy + R + 48, "1 радіан ≈ 57.3°,   повний оберт = 2π рад",
              11, INK, "middle", "bold")
    s += text(cx, cy + R + 66, "θ (рад) = довжина дуги / R", 10.5, GREY, "middle", style="italic")

    # ── праворуч: sin і cos на одній осі (зсув на 90°) ──
    ax, ay, aw = 420, 220, 440
    amp = 70
    s += arrow(ax, ay, ax + aw + 14, ay, GREY, 1.3)
    s += arrow(ax, ay + amp + 26, ax, ay - amp - 26, GREY, 1.3)
    s += text(ax + aw + 10, ay + 18, "θ", 12, GREY, "middle", "bold", "italic")
    # sin
    psin, pcos = [], []
    n = 200
    for i in range(n + 1):
        t = i / n
        x = ax + t * aw
        psin.append((x, ay - amp * math.sin(2 * math.pi * t)))
        pcos.append((x, ay - amp * math.cos(2 * math.pi * t)))
    s += polyline(pcos, RED, 2.6)
    s += polyline(psin, BLUE, 2.8)
    s += text(ax + aw - 4, ay - amp - 30, "cos θ", 12, RED, "end", "bold", "italic")
    s += text(ax + aw - 4, ay + amp + 22, "sin θ", 12, BLUE, "end", "bold", "italic")
    # позначити зсув на π/2 між нулем cos (на 0) і відповідним нулем sin
    # cos має пік на θ=0; sin має пік на θ=π/2 → стрілка зсуву
    x0 = ax                          # пік cos
    x1 = ax + 0.25 * aw              # пік sin
    s += line(x0, ay - amp, x0, ay - amp - 20, GREY, 1.2, "3,3")
    s += line(x1, ay - amp, x1, ay - amp - 20, GREY, 1.2, "3,3")
    s += arrow(x0, ay - amp - 14, x1, ay - amp - 14, GREEN, 2.0)
    s += text((x0 + x1) / 2, ay - amp - 20, "зсув π/2 (90°)", 10, GREEN, "middle", "bold")
    # осьові позначки
    for frac, lab in ((0.25, "π/2"), (0.5, "π"), (0.75, "3π/2"), (1.0, "2π")):
        xx = ax + frac * aw
        s += line(xx, ay - 4, xx, ay + 4, GREY, 1.2)
        s += text(xx, ay + 20, lab, 9.5, GREY, "middle")
    s += rect(ax + 70, ay + amp + 40, 300, 26, "#eef7f0", GREEN, 1.5, 8)
    s += text(ax + 220, ay + amp + 57, "cos θ = sin(θ + 90°)", 12, GREEN, "middle", "bold", "italic")
    save("fig-7-1m-2-radian-shift.svg", s)


if __name__ == "__main__":
    fig_unit_circle()
    fig_radian_and_shift()
    print("OK")
