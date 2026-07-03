# -*- coding: utf-8 -*-
"""Фігури для вставки math-velocity-obstacles.md — повне виведення швидкісної перешкоди.
Окремий файл, щоб не чіпати figs.py/figs-d.py теми. Вивід — у ./img/ з префіксом vo-.
Запуск: python figs-vo.py  (швидко, без зациклень)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG  = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def tangent_lines(ax, ay, cx, cy, R):
    """Дві дотичні від точки A(ax,ay) до кола (cx,cy,R): повертає точки дотику."""
    dx, dy = cx - ax, cy - ay
    d = math.hypot(dx, dy)
    if d <= R:
        return None
    # кут між лінією A→центр і дотичною
    a = math.asin(R / d)
    base = math.atan2(dy, dx)
    pts = []
    for s in (+1, -1):
        ang = base + s * a
        # довжина дотичної
        L = math.sqrt(d * d - R * R)
        tx = ax + L * math.cos(ang)
        ty = ay + L * math.sin(ang)
        pts.append((tx, ty, ang))
    return pts, base, a, d


# ── Фігура 1: конус зіткнення для НЕРУХОМОЇ перешкоди ────────────────────────
def fig_static_cone():
    W, H = 760, 470
    ax, ay = 130, 380           # апарат A (точка після роздування)
    cx, cy = 470, 190           # центр перешкоди B
    Rb = 46                     # істинний радіус B
    Ra = 26                     # радіус A
    R = Rb + Ra                 # роздутий радіус (сума Мінковського)
    fra = []

    # роздутий диск (сума Мінковського) — світлий ореол
    fra.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fbe9e7" stroke="%s" '
               'stroke-width="1.4" stroke-dasharray="5 4"/>' % (cx, cy, R, POS))
    # істинний диск B
    fra.append(circle(cx, cy, Rb, fill="#f2d7d3", stroke=POS, sw=1.8))
    fra.append(text(cx, cy + 4, "B", size=13, color=POS, bold=True))
    # позначка радіуса роздування
    fra.append(line(cx, cy, cx + R * math.cos(math.radians(35)),
                    cy + R * math.sin(math.radians(35)), color=POS, sw=1.0, dash="2 3"))
    fra.append(text(cx + 54, cy + 40, "r_A+r_B", size=10, color=POS, anchor="start", italic=True))

    res = tangent_lines(ax, ay, cx, cy, R)
    (t1x, t1y, a1), (t2x, t2y, a2) = res[0]
    base, half, d = res[1], res[2], res[3]

    def ray_to_box(x0, y0, ang, x_hi, y_hi, marg=10):
        """Довжина променя з (x0,y0) під кутом ang до межі рамки [marg..hi-marg]."""
        c, s = math.cos(ang), math.sin(ang)
        ts = []
        lo = marg
        if c > 1e-9:  ts.append((x_hi - marg - x0) / c)
        if c < -1e-9: ts.append((lo - x0) / c)
        if s > 1e-9:  ts.append((y_hi - marg - y0) / s)
        if s < -1e-9: ts.append((lo - y0) / s)
        return min(t for t in ts if t > 0)

    # заливка конуса (сектор між двома дотичними, продовжений за диск до межі рамки)
    f1 = ray_to_box(ax, ay, a1, W, H)
    f2 = ray_to_box(ax, ay, a2, W, H)
    p1x, p1y = ax + f1 * math.cos(a1), ay + f1 * math.sin(a1)
    p2x, p2y = ax + f2 * math.cos(a2), ay + f2 * math.sin(a2)
    fra.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" '
               'stroke="none" opacity="0.6"/>' % (ax, ay, p1x, p1y, p2x, p2y))

    # дотичні
    fra.append(line(ax, ay, p1x, p1y, color=POS, sw=1.8))
    fra.append(line(ax, ay, p2x, p2y, color=POS, sw=1.8))
    # осьова лінія A→центр
    fra.append(line(ax, ay, cx, cy, color=MUTED, sw=0.9, dash="3 3"))

    # апарат A
    fra.append(circle(ax, ay, 5, fill="#eaf0fd", stroke=NEG, sw=2))
    fra.append(text(ax - 6, ay + 18, "A", size=12, color=NEG, anchor="end", bold=True))
    fra.append(text(ax + 8, ay + 18, "(точка)", size=9, color=MUTED, anchor="start"))

    # дуга піввкута при апексі
    r_arc = 62
    arc_x1, arc_y1 = ax + r_arc * math.cos(base), ay + r_arc * math.sin(base)
    arc_x2, arc_y2 = ax + r_arc * math.cos(a1), ay + r_arc * math.sin(a1)
    fra.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="1.2"/>' % (arc_x1, arc_y1, r_arc, r_arc,
                                                     arc_x2, arc_y2, INK))
    mid = (base + a1) / 2
    fra.append(text(ax + (r_arc + 16) * math.cos(mid), ay + (r_arc + 16) * math.sin(mid) + 4,
                    "α", size=13, color=INK, italic=True))

    # напис-заголовок конуса — у вільному правому куті поза диском і поза лініями
    fra.append(mtext(645, 92,
                     ["Конус зіткнення:", "напрямки руху A,", "що ведуть у диск B"],
                     size=11, color=POS, anchor="middle"))

    # формула піввкута
    box = fitbox(430, 380, 300, 66,
                 "sin α = (r_A + r_B) / d\nα тим ширший, чим ближче B",
                 size=12, fill="#f7f9fc", stroke=MUTED, color=INK)
    fra.append(box)

    render(os.path.join(IMG, 'vo-static-cone.svg'), W, H, *fra,
           title="Нерухома перешкода: конус небезпечних напрямків руху A")


# ── Фігура 2: зсув конуса на швидкість перешкоди v_B ────────────────────────
def fig_shift():
    W, H = 780, 470
    fra = []
    # два простори швидкостей поруч
    # ЛІВО: відносний простір (A − v_B), апекс у нулі
    L = dict(ox=70, oy=100, w=300, h=330)
    R = dict(ox=440, oy=100, w=310, h=330)

    def axes(box, xlab, ylab):
        out = []
        o_x = box['ox'] + 46
        o_y = box['oy'] + box['h'] - 46
        top = box['oy'] + 20
        right = box['ox'] + box['w'] - 16
        out.append(rect(box['ox'], box['oy'], box['w'], box['h'],
                        fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="1.4" marker-end="url(#arrow)"/>' % (o_x, o_y, o_x, top, INK))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="1.4" marker-end="url(#arrow)"/>' % (o_x, o_y, right, o_y, INK))
        out.append(text(o_x - 12, top - 4, ylab, size=10, color=INK, anchor="middle", italic=True))
        out.append(text(right + 2, o_y + 16, xlab, size=10, color=INK, anchor="end", italic=True))
        return out, o_x, o_y

    # ── ЛІВО ──
    out, ox, oy = axes(L, "", "")
    fra += out
    fra.append(text(L['ox'] + L['w'] / 2, L['oy'] - 12,
                    "Відносний простір: w = v_A − v_B", size=11, color=INK, anchor="middle"))
    # конус з апексом у нулі (0 = початок), напрям на диск угору-праворуч
    half = math.radians(24)
    axis = math.radians(-58)          # напрям на перешкоду (вгору-праворуч в екранних коорд)
    far = 250
    a1, a2 = axis - half, axis + half
    p1 = (ox + far * math.cos(a1), oy + far * math.sin(a1))
    p2 = (ox + far * math.cos(a2), oy + far * math.sin(a2))
    fra.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" '
               'stroke="%s" stroke-width="1.6" opacity="0.8"/>' % (ox, oy, p1[0], p1[1], p2[0], p2[1], POS))
    fra.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    fra.append(text(ox - 8, oy + 16, "0", size=11, color=INK, anchor="end"))
    fra.append(text(ox + 150 * math.cos(axis) - 6, oy + 150 * math.sin(axis),
                    "CC", size=12, color=POS, anchor="middle", bold=True))
    fra.append(mtext(L['ox'] + L['w'] / 2, L['oy'] + L['h'] - 20,
                     ["Небезпека ⟺ w у конусі,", "напрямленому на перешкоду"],
                     size=10, color=MUTED, anchor="middle"))

    # ── ПРАВО ──
    out, ox2, oy2 = axes(R, "v_x", "v_y")
    fra += out
    fra.append(text(R['ox'] + R['w'] / 2, R['oy'] - 12,
                    "Простір швидкостей A: v_A", size=11, color=INK, anchor="middle"))
    # вектор v_B (апекс переїжджає сюди)
    vb = (95, -34)   # екранний зсув
    apx, apy = ox2 + vb[0], oy2 + vb[1]
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="2.2" marker-end="url(#arrow)"/>' % (ox2, oy2, apx, apy, POS))
    fra.append(text((ox2 + apx) / 2 + 4, (oy2 + apy) / 2 - 8, "v_B", size=11, color=POS,
                    anchor="start", italic=True))
    # той самий конус, але з апексом у v_B
    p1b = (apx + far * math.cos(a1), apy + far * math.sin(a1))
    p2b = (apx + far * math.cos(a2), apy + far * math.sin(a2))
    fra.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" '
               'stroke="%s" stroke-width="1.6" opacity="0.8"/>' % (apx, apy, p1b[0], p1b[1], p2b[0], p2b[1], POS))
    fra.append(circle(apx, apy, 4, fill=POS, stroke=POS, sw=1))
    fra.append(text(apx + 8, apy - 8, "апекс = v_B", size=9, color=POS, anchor="start"))
    fra.append(circle(ox2, oy2, 4, fill=INK, stroke=INK, sw=1))
    fra.append(text(ox2 - 8, oy2 + 16, "0", size=11, color=INK, anchor="end"))
    # обрана швидкість поза конусом
    ch = (150, -128)
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="2.4" marker-end="url(#arrow)"/>' % (ox2, oy2, ox2 + ch[0], oy2 + ch[1], FIELD))
    fra.append(text(ox2 + ch[0] + 4, oy2 + ch[1] + 2, "v_A поза\nконусом", size=9, color=FIELD, anchor="start"))
    fra.append(text(R['ox'] + R['w'] / 2, R['oy'] + R['h'] - 16,
                    "VO = конус, зсунутий на v_B", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'vo-shift.svg'), W, H, *fra,
           title="Зсув конуса на v_B: рухома небезпека — нерухомий конус у v-просторі")


# ── Фігура 3: взаємна перешкода RVO — кожен бере половину ────────────────────
def fig_rvo():
    W, H = 760, 430
    fra = []
    ox, oy = 300, 350
    top = 70
    right = 720
    # осі
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="1.4" marker-end="url(#arrow)"/>' % (ox, oy, ox, top, INK))
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="1.4" marker-end="url(#arrow)"/>' % (ox, oy, right, oy, INK))
    fra.append(text(ox - 12, top - 4, "v_y", size=10, color=INK, anchor="middle", italic=True))
    fra.append(text(right + 2, oy + 16, "v_x", size=10, color=INK, anchor="end", italic=True))
    fra.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    fra.append(text(ox - 8, oy + 16, "0", size=11, color=INK, anchor="end"))

    half = math.radians(22)
    axis = math.radians(-42)
    far = 420

    # VO: апекс у v_B (сірий, пунктир) — для порівняння
    vb = (150, -46)
    apxB, apyB = ox + vb[0], oy + vb[1]
    a1, a2 = axis - half, axis + half
    p1 = (apxB + far * math.cos(a1), apyB + far * math.sin(a1))
    p2 = (apxB + far * math.cos(a2), apyB + far * math.sin(a2))
    fra.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
               'stroke="%s" stroke-width="1.3" stroke-dasharray="5 4" opacity="0.7"/>'
               % (apxB, apyB, p1[0], p1[1], p2[0], p2[1], MUTED))
    fra.append(circle(apxB, apyB, 3.5, fill=MUTED, stroke=MUTED, sw=1))
    fra.append(text(apxB + 8, apyB + 16, "VO: апекс = v_B", size=9, color=MUTED, anchor="start"))

    # RVO: апекс у (v_A+v_B)/2 (червоний, суцільний)
    va = (60, -150)
    apxR = ox + (va[0] + vb[0]) / 2
    apyR = oy + (va[1] + vb[1]) / 2
    p1r = (apxR + far * math.cos(a1), apyR + far * math.sin(a1))
    p2r = (apxR + far * math.cos(a2), apyR + far * math.sin(a2))
    fra.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" '
               'stroke="%s" stroke-width="1.7" opacity="0.75"/>'
               % (apxR, apyR, p1r[0], p1r[1], p2r[0], p2r[1], POS))
    fra.append(circle(apxR, apyR, 4, fill=POS, stroke=POS, sw=1))
    fra.append(text(apxR - 8, apyR - 8, "RVO: апекс = (v_A+v_B)/2", size=10, color=POS,
                    anchor="end", bold=True))

    # поточні швидкості v_A, v_B від нуля
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="2.0" marker-end="url(#arrow)"/>' % (ox, oy, ox + va[0], oy + va[1], NEG))
    fra.append(text(ox + va[0] - 6, oy + va[1] - 4, "v_A", size=11, color=NEG, anchor="end", italic=True))
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="2.0" marker-end="url(#arrow)"/>' % (ox, oy, ox + vb[0], oy + vb[1], POS))
    fra.append(text(ox + vb[0] + 6, oy + vb[1] - 4, "v_B", size=11, color=POS, anchor="start", italic=True))

    # пояснення половини зсуву — стрілка апекс VO → апекс RVO
    fra.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="1.2" stroke-dasharray="2 3"/>' % (apxB, apyB, apxR, apyR, INK))

    fra.append(mtext(150, 120,
                     ["RVO: апекс на пів-", "дорозі між v_A і v_B", "→ кожен ухиляється", "лише на половину"],
                     size=11, color=INK, anchor="middle"))

    render(os.path.join(IMG, 'vo-rvo-half.svg'), W, H, *fra,
           title="Взаємна перешкода (RVO): апекс на півдорозі — кожен бере половину")


if __name__ == '__main__':
    fig_static_cone()
    fig_shift()
    fig_rvo()
    print("OK: vo-static-cone.svg, vo-shift.svg, vo-rvo-half.svg")
