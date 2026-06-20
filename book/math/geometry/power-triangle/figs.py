# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None):
    """Дуга кола від кута a0 до a1 (радіани, математичний напрям проти годинника).
    Екранний y росте вниз, тому беремо -sin."""
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 0 if a1 > a0 else 1
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.2f %.2f A %.2f %.2f 0 %d %d %.2f %.2f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw, d))


# ── Фігура 1: сам трикутник потужності — P, Q, S як катети й гіпотенуза ───────

def fig_triangle():
    W, H = 640, 420
    ax, ay = 130, 320          # вершина прямого кута (низ-ліво) — тут джерело
    Lp = 360                   # горизонтальний катет P (px)
    ang = math.radians(34)     # кут φ
    bx, by = ax + Lp, ay       # правий нижній кут
    # гіпотенуза S під кутом φ; вертикальний катет Q = P·tan φ
    Lq = Lp * math.tan(ang)
    tx, ty = bx, by - Lq       # верхній кут

    p = []
    # катет P — активна (горизонталь, червоний: «гаряча», корисна)
    p.append(line(ax, ay, bx, by, color=POS, sw=3.4))
    # катет Q — реактивна (вертикаль, синій)
    p.append(line(bx, by, tx, ty, color=NEG, sw=3.4))
    # гіпотенуза S — повна (чорна)
    p.append(line(ax, ay, tx, ty, color=INK, sw=3.0))

    # прямий кут у правому нижньому
    s = 17
    p.append(line(bx - s, by, bx - s, by - s, color=MUTED, sw=1.4))
    p.append(line(bx - s, by - s, bx, by - s, color=MUTED, sw=1.4))

    # кут φ біля джерела
    p.append(arc_path(ax, ay, 52, 0, ang, FIELD, sw=2.4))
    p.append(text(ax + 70, ay - 16, "φ", size=18, color=FIELD, bold=True))

    # підписи сторін
    p.append(text((ax + bx) / 2, ay + 30, "P — активна (Вт)", size=14, color=POS, bold=True))
    p.append(text(bx + 14, (by + ty) / 2 + 4, "Q — реактивна", size=14, color=NEG, bold=True, anchor="start"))
    p.append(text(bx + 14, (by + ty) / 2 + 24, "(вар)", size=12, color=NEG, anchor="start"))
    p.append(text((ax + tx) / 2 - 70, (ay + ty) / 2 - 10, "S — повна (В·А)", size=14, color=INK, bold=True, anchor="end"))

    # формули у рамках праворуч угорі
    f1 = fitbox(330, 56, 280, 40, "S² = P² + Q²", size=15, color=INK, fill=FILL, stroke=LINE)
    f2 = fitbox(330, 104, 280, 40, "P = S · cos φ", size=15, color=POS, fill="#fdecea", stroke=POS)
    f3 = fitbox(330, 152, 280, 40, "Q = S · sin φ", size=15, color=NEG, fill="#eaf0fd", stroke=NEG)
    p.append(f1); p.append(f2); p.append(f3)

    render(os.path.join(OUT, "power-triangle.svg"), W, H, *p,
           title="Три потужності — катети й гіпотенуза одного трикутника")


# ── Фігура 2: ЧОМУ так — миттєва потужність p = v·i при зсуві фаз ─────────────
# Показує, що при зсуві з'являються від'ємні ділянки: енергія тече назад.

def fig_instantaneous():
    W, H = 720, 440
    ox, oy = 70, 230           # початок осей (нуль по вертикалі)
    Ax = 560                   # ширина: два періоди
    Ay = 70                    # масштаб напруги/струму
    two = 2 * math.pi
    cycles = 2.0
    span = cycles * two
    sx = Ax / span
    phi = math.radians(60)     # помітний зсув струму (відстає)

    def Y(val, scale):
        return oy - val * scale

    p = []
    # осі
    p.append(line(ox - 10, oy, ox + Ax + 36, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 16, oy, ox + Ax + 38, oy, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 46, oy + 5, "t", size=15, color=MUTED, italic=True))
    p.append(line(ox, oy + 110, ox, oy - 130, color=MUTED, sw=1.4))

    # криву малюємо як polyline
    def curve(fn, color, sw=2.4, dash=None):
        pts = []
        n = 320
        for i in range(n + 1):
            t = span * i / n
            x = ox + t * sx
            y = fn(t)
            pts.append("%.2f,%.2f" % (x, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, d))

    # заливка від'ємних ділянок миттєвої потужності (енергія назад)
    pw_scale = 26.0
    def pw(t):
        return math.cos(t) * math.cos(t - phi)   # v·i (нормовані амплітуди)
    # будуємо смугу: для кожного кроку, де pw<0, малюємо тонкий стовпчик
    bars = []
    n = 320
    for i in range(n):
        t = span * (i + 0.5) / n
        val = pw(t)
        if val < 0:
            x = ox + (span * i / n) * sx
            wpx = span / n * sx + 0.6
            ytop = Y(val * pw_scale, 1.0)   # від'ємне → нижче нуля
            bars.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fde2e0" stroke="none"/>'
                        % (x, oy, wpx, ytop - oy))
    p.extend(bars)

    # напруга (червона), струм (синій, відстає)
    p.append(curve(lambda t: Y(math.cos(t), Ay), POS, sw=2.6))
    p.append(curve(lambda t: Y(math.cos(t - phi), Ay), NEG, sw=2.6, dash="6 4"))
    # миттєва потужність p=v·i (зелена, жирніша)
    p.append(curve(lambda t: Y(pw(t) * pw_scale, 1.0), FIELD, sw=2.8))

    # підписи кривих
    p.append(text(ox + 6, oy - Ay - 12, "напруга v", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(ox + 6, oy + Ay + 24, "струм i (відстає)", size=13, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + Ax * 0.52, oy - 118, "p = v·i", size=14, color=FIELD, bold=True, anchor="middle"))

    # рамка-пояснення внизу
    b, bw, bh = textbox(ox + Ax * 0.5, oy + 92,
                        "рожеві ділянки: p < 0 — енергія повертається до джерела",
                        size=12, color=NEG, fill="#fde2e0", stroke=NEG)
    p.append(b)

    render(os.path.join(OUT, "instantaneous-power.svg"), W, H, *p,
           title="Зсув фаз → миттєва потужність буває від'ємною")


# ── Фігура 3: розклад струму на дві складові (звідки катети) ──────────────────

def fig_current_split():
    W, H = 600, 430
    cx, cy = 150, 300          # початок векторів струму
    ang = math.radians(40)     # кут φ між струмом і напругою
    Ls = 330                   # довжина повного струму I (px)
    ix = cx + Ls * math.cos(ang)
    iy = cy - Ls * math.sin(ang)
    # проєкції: уздовж напруги (активна), упоперек (реактивна)
    ax_p = cx + Ls * math.cos(ang) * math.cos(ang)   # ні: простіше — катети прямокутника
    # in-phase складова — горизонталь до точки під струмом
    px2 = ix          # ні. Зробимо чисто: I cosφ уздовж осі напруги (горизонталь)
    # напруга — горизонтальна опорна вісь
    vx = cx + (Ls + 30)
    vy = cy

    p = []
    # опорна вісь напруги (горизонталь)
    p.append(line(cx - 20, cy, vx + 20, cy, color=MUTED, sw=1.4))
    p.append(arrow(vx, cy, vx + 22, cy, color=POS, sw=2.2))
    p.append(text(vx + 30, cy + 5, "U", size=15, color=POS, bold=True, anchor="start"))

    # повний струм I (чорний)
    p.append(arrow(cx, cy, ix, iy, color=INK, sw=2.8))
    p.append(text(ix + 8, iy - 6, "I — повний струм", size=13, color=INK, bold=True, anchor="start"))

    # активна складова I·cosφ (червона, уздовж напруги)
    icos = Ls * math.cos(ang)
    p.append(line(cx, cy, cx + icos, cy, color=POS, sw=3.4))
    # реактивна складова I·sinφ (синя, вертикаль угору від кінця активної)
    p.append(line(cx + icos, cy, ix, iy, color=NEG, sw=3.4, dash="6 4"))

    # прямий кут
    s = 15
    p.append(line(cx + icos - s, cy, cx + icos - s, cy - s, color=MUTED, sw=1.3))
    p.append(line(cx + icos - s, cy - s, cx + icos, cy - s, color=MUTED, sw=1.3))

    # дуга φ
    p.append(arc_path(cx, cy, 48, 0, ang, FIELD, sw=2.4))
    p.append(text(cx + 64, cy - 16, "φ", size=17, color=FIELD, bold=True))

    # підписи складових
    b1, w1, h1 = textbox(cx + icos / 2, cy + 30, "I·cos φ → активна (P)",
                         size=13, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b1)
    b2, w2, h2 = textbox(ix + 4, (cy + iy) / 2 + 20, "I·sin φ → реактивна (Q)",
                         size=13, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)
    p.append(b2)

    render(os.path.join(OUT, "current-split.svg"), W, H, *p,
           title="Струм ділиться на дві складові — звідси й катети")


if __name__ == "__main__":
    fig_triangle()
    fig_instantaneous()
    fig_current_split()
    print("OK: figures written to", OUT)
