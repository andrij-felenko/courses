# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

TWO_PI = 2 * math.pi


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None):
    """Дуга кола від кута a0 до a1 (радіани, математичний напрям проти годинника).
    Екранний y росте вниз, тому беремо -sin для екранних координат."""
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 0 if a1 > a0 else 1            # 0 = проти годинника на екрані (y вниз)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw, d))


def wave(ox, oy, sx, Ay, fn, phi, color, sw=2.6, n=300, t0=0.0, t1=None):
    """Полілінія синусоїди fn(θ + phi) на проміжку θ∈[t0..t1] (радіани)."""
    if t1 is None:
        t1 = TWO_PI
    pts = []
    for i in range(n + 1):
        th = t0 + (t1 - t0) * i / n
        x = ox + (th - t0) * sx
        y = oy - fn(th + phi) * Ay
        pts.append("%.2f,%.2f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── Фігура 1: дві синусоїди зі зсувом фаз — випередження/відставання ──────────

def fig_two_waves():
    W, H = 760, 420
    ox, oy = 80, 210
    span = 2.5 * math.pi          # показуємо трохи більше за один період
    Ax = 580
    Ay = 110
    sx = Ax / span
    phi = math.radians(60)        # зсув φ = 60° = π/3

    p = []
    # вісь часу
    p.append(line(ox - 12, oy, ox + Ax + 40, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 20, oy, ox + Ax + 42, oy, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 50, oy + 5, "t", size=15, color=MUTED, italic=True))
    # вісь значень
    p.append(line(ox, oy + Ay + 34, ox, oy - Ay - 40, color=MUTED, sw=1.4))
    p.append(arrow(ox, oy - Ay - 20, ox, oy - Ay - 42, color=MUTED, sw=1.4))

    # позначки періоду по осі t
    for frac, lbl in [(0.5, "T/2"), (1.0, "T"), (1.5, "3T/2"), (2.0, "2T")]:
        xx = ox + frac * math.pi * sx
        p.append(line(xx, oy - 4, xx, oy + 4, color=MUTED, sw=1.1))
        p.append(text(xx, oy + 24, lbl, size=11, color=MUTED))

    # дві хвилі: опорна (cos, червона) і відстала на φ (синя)
    p.append(wave(ox, oy, sx, Ay, math.cos, 0.0, POS, sw=2.8, t1=span))
    p.append(wave(ox, oy, sx, Ay, math.cos, -phi, NEG, sw=2.8, t1=span))

    # вертикалі через перші вершини обох хвиль, щоб показати зсув Δt
    # вершина опорної cos — при θ=0 (t=ox); вершина відсталої — при θ=φ
    peak_a = ox                                   # t=0
    peak_b = ox + phi * sx                         # зсунута вершина
    p.append(line(peak_a, oy - Ay, peak_a, oy + Ay + 18, color=POS, sw=1.2, dash="4 4"))
    p.append(line(peak_b, oy - Ay, peak_b, oy + Ay + 18, color=NEG, sw=1.2, dash="4 4"))

    # дужка-розмір Δt між вершинами (під віссю)
    yb = oy + Ay + 18
    p.append(line(peak_a, yb, peak_b, yb, color=INK, sw=1.6))
    p.append(line(peak_a, yb - 5, peak_a, yb + 5, color=INK, sw=1.6))
    p.append(line(peak_b, yb - 5, peak_b, yb + 5, color=INK, sw=1.6))
    b, bw, bh = textbox((peak_a + peak_b) / 2, yb + 22, "Δt  (зсув φ)",
                        size=13, color=INK, bold=True, fill=BG, stroke=INK)
    p.append(b)

    # підписи хвиль
    p.append(text(ox + 18, oy - Ay - 8, "опорна", size=14, color=POS, bold=True, anchor="start"))
    p.append(text(peak_b + 14, oy - Ay + 16, "відстала на φ", size=14, color=NEG, bold=True, anchor="start"))

    render(os.path.join(OUT, "two-waves.svg"), W, H, *p,
           title="Зсув фаз: одна хвиля відстає від іншої на φ")


# ── Фігура 2: фаза як кутове положення на колі ───────────────────────────────

def fig_phase_on_circle():
    W, H = 760, 420
    cx, cy = 200, 210
    R = 140
    a = math.radians(48)          # фаза опорної точки
    phi = math.radians(60)        # зсув
    b = a - phi                   # відстала точка (менший кут)

    p = []
    # осі кола
    p.append(line(cx - R - 28, cy, cx + R + 28, cy, color=MUTED, sw=1.2))
    p.append(line(cx, cy + R + 28, cx, cy - R - 28, color=MUTED, sw=1.2))
    p.append(circle(cx, cy, R, fill="none", stroke=INK, sw=1.8))

    # дві радіус-точки
    ax = cx + R * math.cos(a); ay = cy - R * math.sin(a)
    bx = cx + R * math.cos(b); by = cy - R * math.sin(b)
    p.append(line(cx, cy, ax, ay, color=POS, sw=2.6))
    p.append(line(cx, cy, bx, by, color=NEG, sw=2.6))
    p.append(circle(ax, ay, 5.5, fill=POS, stroke=POS))
    p.append(circle(bx, by, 5.5, fill=NEG, stroke=NEG))

    # дуга зсуву φ між двома радіусами
    p.append(arc_path(cx, cy, 52, b, a, FIELD, sw=2.4))
    mid = (a + b) / 2
    p.append(text(cx + 70 * math.cos(mid), cy - 70 * math.sin(mid) + 5,
                  "φ", size=17, color=FIELD, bold=True))

    # стрілка обертання
    p.append(arc_path(cx, cy, R + 16, math.radians(95), math.radians(135), MUTED, sw=1.6))
    p.append(text(cx - 6, cy - R - 22, "ω", size=14, color=MUTED, italic=True, anchor="end"))

    # ── праворуч: проєкції двох точок як дві синусоїди в часі ──
    ox, oy = 380, 210
    Ax = 320
    Ay = 96
    span = 2.2 * math.pi
    sx = Ax / span
    p.append(line(ox - 8, oy, ox + Ax + 30, oy, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax + 14, oy, ox + Ax + 32, oy, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 40, oy + 5, "t", size=14, color=MUTED, italic=True))
    p.append(line(ox, oy + Ay + 14, ox, oy - Ay - 18, color=MUTED, sw=1.3))

    # хвилі стартують з поточних фаз a і b (y-проєкція = sin)
    p.append(wave(ox, oy, sx, Ay, math.sin, a, POS, sw=2.6, t1=span))
    p.append(wave(ox, oy, sx, Ay, math.sin, b, NEG, sw=2.6, t1=span))

    # пунктир: зв'язок висоти точки з початком хвилі
    p.append(line(ax, ay, ox, oy - math.sin(a) * Ay, color=POS, sw=1.0, dash="3 4"))
    p.append(line(bx, by, ox, oy - math.sin(b) * Ay, color=NEG, sw=1.0, dash="3 4"))

    b1, w1, h1 = textbox(ox + Ax * 0.5, oy - Ay - 24,
                         "та сама φ — тепер між хвилями",
                         size=12, color=MUTED, fill=BG, stroke=MUTED)
    p.append(b1)

    render(os.path.join(OUT, "phase-on-circle.svg"), W, H, *p,
           title="Фаза — це кут на колі; зсув φ — кут між двома точками")


# ── Фігура 3: чому фаза важлива — інтерференція (складання хвиль) ─────────────

def fig_interference():
    W, H = 760, 430
    ox = 90
    Ax = 560
    Ay = 60
    span = 2.2 * math.pi
    sx = Ax / span

    def panel(oy, phi, title_txt, sum_color):
        q = []
        q.append(line(ox - 10, oy, ox + Ax + 30, oy, color=MUTED, sw=1.2))
        q.append(text(ox - 18, oy - Ay - 8, title_txt, size=13, color=INK, bold=True, anchor="start"))
        # дві складові (тонкі) і їхня сума (товста)
        q.append(wave(ox, oy, sx, Ay, math.sin, 0.0, POS, sw=1.8, t1=span))
        q.append(wave(ox, oy, sx, Ay, math.sin, phi, NEG, sw=1.8, t1=span))
        q.append(wave(ox, oy, sx, Ay, lambda th: math.sin(th) + math.sin(th + phi),
                      0.0, sum_color, sw=3.0, t1=span))
        return q

    p = []
    # верхня панель: у фазі (φ=0) — підсилення (сума амплітуди 2)
    p += panel(120, 0.0, "у фазі (φ = 0)", POS)
    b1, w1, h1 = textbox(ox + Ax - 70, 120 - Ay - 28, "сума вдвічі більша — підсилення",
                         size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b1)

    # нижня панель: у протифазі (φ=π) — гасіння (сума нуль)
    p += panel(310, math.pi, "у протифазі (φ = π)", NEG)
    b2, w2, h2 = textbox(ox + Ax - 80, 310 + Ay + 30, "складові гасять одна одну — нуль",
                         size=12, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)
    p.append(b2)

    render(os.path.join(OUT, "interference.svg"), W, H, *p,
           title="Чому фаза вирішує: дві однакові хвилі підсилюються або гасяться")


if __name__ == "__main__":
    fig_two_waves()
    fig_phase_on_circle()
    fig_interference()
    print("OK: figures written to", OUT)
