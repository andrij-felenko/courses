# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None):
    """Дуга кола від кута a0 до a1 (радіани, математичний напрям проти годинника).
    y екранний росте вниз, тому беремо -sin для екранних координат."""
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 0 if a1 > a0 else 1            # 0 = проти годинника на екрані (y вниз)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw, d))


# ── Фігура 1: одиничне коло — означення sin/cos як координат точки ────────────

def fig_unit_circle():
    W, H = 560, 480
    cx, cy = 280, 250          # центр кола
    R = 170                    # радіус = 1 (у px)
    ang = math.radians(52)     # обраний кут θ
    px = cx + R * math.cos(ang)
    py = cy - R * math.sin(ang)

    p = []
    # осі
    p.append(line(cx - R - 40, cy, cx + R + 40, cy, color=MUTED, sw=1.4))
    p.append(arrow(cx + R + 20, cy, cx + R + 42, cy, color=MUTED, sw=1.4))
    p.append(line(cx, cy + R + 40, cx, cy - R - 50, color=MUTED, sw=1.4))
    p.append(arrow(cx, cy - R - 30, cx, cy - R - 52, color=MUTED, sw=1.4))
    p.append(text(cx + R + 52, cy + 5, "x", size=15, color=MUTED, italic=True))
    p.append(text(cx + 14, cy - R - 40, "y", size=15, color=MUTED, italic=True))

    # коло радіуса 1
    p.append(circle(cx, cy, R, fill="none", stroke=INK, sw=1.8))
    # позначки 1 і -1 на осях
    p.append(text(cx + R + 4, cy + 20, "1", size=12, color=MUTED, anchor="middle"))
    p.append(text(cx - 14, cy - R + 2, "1", size=12, color=MUTED, anchor="middle"))

    # радіус-стрілка до точки (гіпотенуза = 1)
    p.append(line(cx, cy, px, py, color=INK, sw=2.4))
    p.append(circle(px, py, 5.5, fill=INK, stroke=INK))

    # катет cos θ — горизонтальна проєкція (червоний)
    p.append(line(cx, py, px, py, color=POS, sw=2.6))          # на висоті точки? ні: cos уздовж x
    # переробимо: cos уздовж осі x на рівні центру; sin вертикально вгору від осі
    p[-1] = line(cx, cy, px, cy, color=POS, sw=3.0)            # cos θ: уздовж x
    # sin θ — вертикальний катет (синій)
    p.append(line(px, cy, px, py, color=NEG, sw=3.0, dash="5 4"))

    # прямий кут біля основи
    s = 13
    p.append(line(px - s, cy, px - s, cy - s, color=MUTED, sw=1.2))
    p.append(line(px - s, cy - s, px, cy - s, color=MUTED, sw=1.2))

    # дуга кута θ
    p.append(arc_path(cx, cy, 40, 0, ang, FIELD, sw=2.2))
    p.append(text(cx + 56, cy - 18, "θ", size=16, color=FIELD, bold=True))

    # підписи проєкцій
    b1, w1, h1 = textbox((cx + px) / 2, cy + 24, "cos θ", size=14, color=POS, bold=True,
                         fill="#fdecea", stroke=POS)
    p.append(b1)
    b2, w2, h2 = textbox(px + 52, (cy + py) / 2, "sin θ", size=14, color=NEG, bold=True,
                         fill="#eaf0fd", stroke=NEG)
    p.append(b2)

    # підпис точки
    b3, w3, h3 = textbox(px + 4, py - 26, "(cos θ, sin θ)", size=13, color=INK, bold=True,
                         min_w=140)
    # зсунути, щоб не вилазило за верх
    p.append(b3)

    # підпис гіпотенузи = 1
    p.append(text((cx + px) / 2 - 30, (cy + py) / 2 - 6, "1", size=14, color=INK, bold=True))

    render(os.path.join(OUT, "unit-circle.svg"), W, H, *p,
           title="Синус і косинус = координати точки на колі радіуса 1")


# ── Фігура 2: графіки sin і cos як сліди обертання ───────────────────────────

def fig_graphs():
    W, H = 720, 380
    ox, oy = 70, 190          # початок осей графіка
    Ax = 540                  # ширина по θ: 0..2π
    Ay = 110                  # амплітуда в px (=1)
    two_pi = 2 * math.pi
    sx = Ax / two_pi          # px на радіан

    p = []
    # вісь θ
    p.append(line(ox - 10, oy, ox + Ax + 40, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 20, oy, ox + Ax + 42, oy, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 52, oy + 5, "θ", size=15, color=MUTED, italic=True))
    # вісь значень
    p.append(line(ox, oy + Ay + 26, ox, oy - Ay - 26, color=MUTED, sw=1.4))
    p.append(arrow(ox, oy - Ay - 8, ox, oy - Ay - 28, color=MUTED, sw=1.4))
    p.append(text(ox - 18, oy - Ay - 14, "1", size=12, color=MUTED))
    p.append(text(ox - 22, oy + Ay + 6, "−1", size=12, color=MUTED))
    p.append(line(ox - 4, oy - Ay, ox + 4, oy - Ay, color=MUTED, sw=1.2))
    p.append(line(ox - 4, oy + Ay, ox + 4, oy + Ay, color=MUTED, sw=1.2))

    # позначки π/2, π, 3π/2, 2π
    for frac, lbl in [(0.5, "π/2"), (1.0, "π"), (1.5, "3π/2"), (2.0, "2π")]:
        xx = ox + frac * math.pi * sx
        p.append(line(xx, oy - 4, xx, oy + 4, color=MUTED, sw=1.2))
        p.append(text(xx, oy + 22, lbl, size=12, color=MUTED))

    # криві
    def curve(fn, color, sw=2.6):
        pts = []
        n = 240
        for i in range(n + 1):
            th = two_pi * i / n
            x = ox + th * sx
            y = oy - fn(th) * Ay
            pts.append("%.2f,%.2f" % (x, y))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    p.append(curve(math.cos, POS))      # cos — червоний (стартує з 1)
    p.append(curve(math.sin, NEG))      # sin — синій (стартує з 0)

    # підписи кривих біля старту
    p.append(text(ox + 30, oy - Ay - 6, "cos θ", size=14, color=POS, bold=True, anchor="start"))
    p.append(text(ox + 18, oy + 26, "sin θ", size=14, color=NEG, bold=True, anchor="start"))

    # зсув на π/2 — підказка
    b, bw, bh = textbox(ox + Ax * 0.5, oy - Ay - 30, "cos випереджає sin на π/2",
                        size=12, color=MUTED, fill=BG, stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "sin-cos-graphs.svg"), W, H, *p,
           title="Один оберт по колу = одна хвиля кожної функції")


# ── Фігура 3: від кола до прямокутного трикутника ────────────────────────────

def fig_triangle():
    W, H = 600, 360
    ax, ay = 110, 280         # вершина прямого кута (низ-ліво)
    L = 360                   # довжина горизонтального катета (px)
    ang = math.radians(34)
    bx = ax + L
    by = ay
    # гіпотенуза під кутом ang, довжина так, щоб піднятися: hyp = L / cos
    hyp = L / math.cos(ang)
    tx = ax + hyp * math.cos(ang)
    ty = ay - hyp * math.sin(ang)

    p = []
    # трикутник
    p.append(line(ax, ay, bx, by, color=POS, sw=3.0))         # прилеглий
    p.append(line(bx, by, tx, ty, color=NEG, sw=3.0))         # протилежний
    p.append(line(ax, ay, tx, ty, color=INK, sw=2.6))         # гіпотенуза

    # прямий кут
    s = 16
    p.append(line(bx - s, by, bx - s, by - s, color=MUTED, sw=1.4))
    p.append(line(bx - s, by - s, bx, by - s, color=MUTED, sw=1.4))

    # кут θ біля лівої вершини
    p.append(arc_path(ax, ay, 48, 0, ang, FIELD, sw=2.2))
    p.append(text(ax + 64, ay - 14, "θ", size=17, color=FIELD, bold=True))

    # підписи сторін
    p.append(text((ax + bx) / 2, ay + 26, "прилеглий", size=13, color=POS, bold=True))
    p.append(text(bx - 56, (by + ty) / 2, "протилежний", size=13, color=NEG, bold=True, anchor="end"))
    p.append(text((ax + tx) / 2 - 36, (ay + ty) / 2 - 8, "гіпотенуза", size=13, color=INK, bold=True))

    # формули праворуч у рамці
    f1 = fitbox(ax + 30, 70, 250, 46, "cos θ = прилеглий / гіпотенуза",
                size=14, color=POS, fill="#fdecea", stroke=POS)
    f2 = fitbox(ax + 30, 122, 250, 46, "sin θ = протилежний / гіпотенуза",
                size=14, color=NEG, fill="#eaf0fd", stroke=NEG)
    p.append(f1); p.append(f2)

    render(os.path.join(OUT, "right-triangle.svg"), W, H, *p,
           title="Те саме означення мовою прямокутного трикутника")


if __name__ == "__main__":
    fig_unit_circle()
    fig_graphs()
    fig_triangle()
    print("OK: figures written to", OUT)
