# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None):
    """Дуга кола від кута a0 до a1 (радіани, мат. напрям проти годинника).
    y екранний росте вниз → беремо -sin для екранних координат."""
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 0 if a1 > a0 else 1            # 0 = проти годинника на екрані (y вниз)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw, d))


# ── Фігура 1: чому нахил sin у нулі = 1 (мала дуга = хорда = підйом) ──────────
# Збільшений шматок одиничного кола біля θ=0. Видно, що для малого θ
# приріст висоти Δ(sinθ) майже дорівнює довжині дуги Δθ — тому відношення → 1.

def fig_small_angle():
    W, H = 620, 430
    cx, cy = 150, 360          # центр кола (далеко знизу-зліва — показуємо лише шматок)
    R = 360                    # великий радіус: біля θ=0 коло майже вертикальне
    a0 = math.radians(6)       # нижній кут (мала база)
    a1 = math.radians(20)      # верхній кут — між ними сектор Δθ

    def P(a):
        return cx + R * math.cos(a), cy - R * math.sin(a)
    x0, y0 = P(a0)
    x1, y1 = P(a1)

    p = []
    # вісь x (де sin=0) — горизонталь через центр
    p.append(line(cx, cy, cx + R + 40, cy, color=MUTED, sw=1.4))
    p.append(arrow(cx + R + 18, cy, cx + R + 42, cy, color=MUTED, sw=1.4))
    p.append(text(cx + R + 52, cy + 5, "x", size=15, color=MUTED, italic=True))

    # шматок кола (дуга від a0 до a1, трохи ширше для контексту)
    p.append(arc_path(cx, cy, R, math.radians(2), math.radians(26), INK, sw=2.0))

    # два радіуси
    p.append(line(cx, cy, x0, y0, color=MUTED, sw=1.6, dash="5 4"))
    p.append(line(cx, cy, x1, y1, color=MUTED, sw=1.6, dash="5 4"))

    # дуга Δθ біля центру (мітка кута)
    p.append(arc_path(cx, cy, 70, a0, a1, FIELD, sw=2.6))
    mid = (a0 + a1) / 2
    p.append(text(cx + 92 * math.cos(mid), cy - 92 * math.sin(mid) + 4,
                  "Δθ", size=15, color=FIELD, bold=True))

    # ── ключ: підйом по висоті Δ(sinθ) — вертикальний відрізок (синій)
    p.append(line(x1, y0, x1, y1, color=NEG, sw=3.2))
    b, bw, bh = textbox(x1 + 70, (y0 + y1) / 2, "Δ(sin θ)", size=14, color=NEG,
                        bold=True, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    # горизонтальна допоміжна (від нижньої точки до основи вертикалі)
    p.append(line(x0, y0, x1, y0, color=MUTED, sw=1.2, dash="3 3"))

    # ── довжина дуги ≈ Δθ (зелений) — підпис ліворуч від хорди, без перекриття
    b2, bw2, bh2 = textbox((x0 + x1) / 2 - 110, (y0 + y1) / 2 + 30,
                           "довжина дуги ≈ Δθ", size=13, color=FIELD,
                           bold=True, fill=BG, stroke=FIELD)
    p.append(b2)

    # точки
    p.append(circle(x0, y0, 5, fill=INK, stroke=INK))
    p.append(circle(x1, y1, 5, fill=INK, stroke=INK))

    # висновок-рамка
    concl = ("При малому Δθ дуга, хорда й підйом Δ(sin θ) майже рівні:\n"
             "Δ(sin θ) / Δθ → 1, тож (sin θ)′ при θ=0 дорівнює 1")
    p.append(fitbox(60, 30, 500, 56, concl, size=13, color=INK, bold=True,
                    fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "small-angle.svg"), W, H, *p)


# ── Фігура 2: нахил sin у кожній точці = висота cos ──────────────────────────
# Дві криві, sin і cos, одна під одною на спільній осі θ. Дотичні до sin
# у характерних точках; їхній нахил читається з висоти cos під ними.

def fig_slope_is_cos():
    W, H = 740, 420
    ox = 70
    oy_s = 130                 # нульова лінія верхнього графіка (sin)
    oy_c = 320                 # нульова лінія нижнього графіка (cos)
    Ax = 560                   # ширина по θ: 0..2π
    Ay = 80                    # амплітуда в px
    two_pi = 2 * math.pi
    sx = Ax / two_pi

    p = []

    def axis(oy, name):
        p.append(line(ox - 10, oy, ox + Ax + 40, oy, color=MUTED, sw=1.3))
        p.append(arrow(ox + Ax + 18, oy, ox + Ax + 42, oy, color=MUTED, sw=1.3))
        p.append(text(ox + Ax + 52, oy + 5, "θ", size=14, color=MUTED, italic=True))
        for frac, lbl in [(0.5, "π/2"), (1.0, "π"), (1.5, "3π/2"), (2.0, "2π")]:
            xx = ox + frac * math.pi * sx
            p.append(line(xx, oy - 4, xx, oy + 4, color=MUTED, sw=1.1))
            p.append(text(xx, oy + 18, lbl, size=11, color=MUTED))

    def curve(oy, fn, color, sw=2.6):
        pts = []
        n = 240
        for i in range(n + 1):
            th = two_pi * i / n
            pts.append("%.2f,%.2f" % (ox + th * sx, oy - fn(th) * Ay))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    axis(oy_s, "θ")
    axis(oy_c, "θ")
    p.append(curve(oy_s, math.sin, NEG))     # sin — синій
    p.append(curve(oy_c, math.cos, POS))     # cos — червоний

    p.append(text(ox + 16, oy_s - Ay - 8, "sin θ", size=15, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + 16, oy_c - Ay - 8, "(sin θ)′ = cos θ", size=15, color=POS, bold=True, anchor="start"))

    # дотичні до sin у θ=0 (нахил 1), π/2 (нахил 0), π (нахил −1)
    def tangent(th0, color):
        x0 = ox + th0 * sx
        y0 = oy_s - math.sin(th0) * Ay
        slope = math.cos(th0)              # нахил кривої sin
        # у пікселях: dy/dx = -(slope*Ay)/sx  (мінус — бо y екранна вниз)
        dpx = 46
        dpx_l = min(dpx, x0 - ox)           # не вилазити ліворуч за вісь
        # масштаб нахилу на екрані
        k = (slope * Ay) / sx
        x1, y1 = x0 - dpx_l, y0 + k * dpx_l
        x2, y2 = x0 + dpx, y0 - k * dpx
        out = line(x1, y1, x2, y2, color=color, sw=2.4)
        out += circle(x0, y0, 4.5, fill=color, stroke=color)
        return out, x0, y0

    for th0, note in [(0.0, "нахил 1"), (math.pi / 2, "нахил 0"), (math.pi, "нахил −1")]:
        seg, x0, y0 = tangent(th0, INK)
        p.append(seg)
        # вертикальна пунктирна вниз до cos — «висота cos = цей нахил»
        yc = oy_c - math.cos(th0) * Ay
        p.append(line(x0, y0, x0, yc, color=MUTED, sw=1.1, dash="4 4"))
        p.append(circle(x0, yc, 4.5, fill=POS, stroke=POS))

    # підпис-зв'язка
    b, bw, bh = textbox(ox + Ax * 0.5, 30,
                        "Нахил дотичної до sin у точці = висота cos під нею",
                        size=13, color=INK, bold=True, fill=FILL, stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "slope-is-cos.svg"), W, H, *p)


# ── Фігура 3: цикл диференціювання по чверті оберту ──────────────────────────
# d/dθ зсуває хвилю на +π/2 (вперед по фазі). Чотири кроки замикаються в коло:
# sin → cos → −sin → −cos → sin.

def fig_cycle():
    W, H = 560, 420
    cx, cy = 280, 235
    R = 135

    nodes = [
        ("sin θ",  90),     # верх
        ("cos θ",   0),     # право
        ("−sin θ", -90),    # низ
        ("−cos θ", 180),    # ліво
    ]

    p = []
    # вузли
    centers = []
    for label, deg in nodes:
        a = math.radians(deg)
        nx = cx + R * math.cos(a)
        ny = cy - R * math.sin(a)
        centers.append((nx, ny))
        b, bw, bh = textbox(nx, ny, label, size=16, color=INK, bold=True,
                            fill=FILL, stroke=LINE, min_w=92, pad=12)
        p.append(b)

    # стрілки по колу між сусідами (за годинниковою: sin→cos→−sin→−cos→sin)
    rr = R                      # радіус дуги-зв'язки
    for i in range(4):
        a_from = math.radians(nodes[i][1])
        a_to = math.radians(nodes[(i + 1) % 4][1])
        # трохи відступити від вузлів, щоб стрілка не входила в рамку
        pad = math.radians(26)
        af = a_from - pad
        at = a_to + pad
        # точки дуги
        fx = cx + rr * math.cos(af); fy = cy - rr * math.sin(af)
        tx = cx + rr * math.cos(at); ty = cy - rr * math.sin(at)
        large = 0
        sweep = 1               # за годинниковою на екрані (y вниз)
        p.append('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
                 'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (fx, fy, rr, rr, large, sweep, tx, ty, FIELD))

    # підпис у центрі
    b, bw, bh = textbox(cx, cy, "d/dθ\n+π/2", size=14, color=FIELD, bold=True,
                        fill=BG, stroke=FIELD, pad=10)
    p.append(b)

    # пояснення зверху
    p.append(text(cx, 26, "Кожне диференціювання = крок на +π/2; чотири кроки замикають коло",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "derivative-cycle.svg"), W, H, *p)


if __name__ == "__main__":
    fig_small_angle()
    fig_slope_is_cos()
    fig_cycle()
    print("done: small-angle.svg, slope-is-cos.svg, derivative-cycle.svg")
