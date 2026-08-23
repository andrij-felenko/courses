# -*- coding: utf-8 -*-
"""Figures for the DETAILED «Кінематика диференціального приводу».
Import svgkit from scripts/ (do not copy it). Output to ./img/.
Run:  python figs-d.py    then  python ../../../../scripts/svgcheck.py img --min-font 8
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None, n=120):
    """Polyline arc around (cx,cy), radius r, angles a0..a1 (radians, SVG y-down)."""
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append('%.1f,%.1f' % (cx + r * math.cos(a), cy + r * math.sin(a)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (' '.join(pts), color, sw, d))


def dot(cx, cy, r=4.0, fill=INK):
    return circle(cx, cy, r, fill=fill, stroke=BG, sw=1.2)


# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — three ways to integrate ONE arc step. The true motion over a step is
# an arc of the ICC; the "rectangular" scheme replaces it by the chord under the
# START heading (undershoots into the turn), the midpoint scheme uses the heading
# at mid-step (lands almost on the arc), the exact formula rides the arc itself.
# Point: the schemes differ by how they treat heading during the step, and the
# rectangular one systematically falls short.
# ════════════════════════════════════════════════════════════════════════════
def fig_arc_integration():
    W, H = 700, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # ICC low-centre; robot sweeps an arc up-and-across the upper canvas.
    icc = (360, 440)
    R = 250.0
    a0 = math.radians(212)          # start angle from ICC (SVG y-down): upper-left
    dth = math.radians(36)          # big-ish step so schemes visibly diverge, chords bounded
    a1 = a0 + dth                   # sweep toward 248° → upper-right, stays on canvas

    P0 = (icc[0] + R * math.cos(a0), icc[1] + R * math.sin(a0))   # start point
    P1 = (icc[0] + R * math.cos(a1), icc[1] + R * math.sin(a1))   # true end (on arc)

    # heading at start = tangent to arc at P0 (perp to radius), travel toward a1.
    # radius unit ICC->P = (cos a, sin a); tangent in direction of increasing a
    # is (-sin a, cos a).
    def tangent(a):
        return (-math.sin(a), math.cos(a))
    t0 = tangent(a0)
    tm = tangent((a0 + a1) / 2)      # heading at mid-step

    ds = R * dth                     # arc length of the step

    Prect = (P0[0] + ds * t0[0], P0[1] + ds * t0[1])   # straight ds under START heading
    Pmid = (P0[0] + ds * tm[0], P0[1] + ds * tm[1])    # straight ds under MID heading

    # radius spokes (faint) to show the ICC framing
    f.append(line(icc[0], icc[1], P0[0], P0[1], color=MUTED, sw=1.0, dash='4,4'))
    f.append(line(icc[0], icc[1], P1[0], P1[1], color=MUTED, sw=1.0, dash='4,4'))

    # true arc (thick green)
    f.append(arc_path(icc[0], icc[1], R, a0, a1, FIELD, sw=3.0))
    # rectangular chord (red) and midpoint chord (blue)
    f.append(line(P0[0], P0[1], Prect[0], Prect[1], color=POS, sw=2.4))
    f.append(line(P0[0], P0[1], Pmid[0], Pmid[1], color=NEG, sw=2.4))

    # gap markers from each scheme's endpoint to the true endpoint
    f.append(line(Prect[0], Prect[1], P1[0], P1[1], color=POS, sw=1.0, dash='3,3'))
    f.append(line(Pmid[0], Pmid[1], P1[0], P1[1], color=NEG, sw=1.0, dash='3,3'))

    # endpoints + ICC
    f.append(dot(P0[0], P0[1], 5, INK))
    f.append(dot(P1[0], P1[1], 5, FIELD))
    f.append(dot(Prect[0], Prect[1], 4.5, POS))
    f.append(dot(Pmid[0], Pmid[1], 4.5, NEG))
    f.append(dot(icc[0], icc[1], 5, INK))

    # start heading arrow (small) to make "початковий курс" concrete
    f.append(arrow(P0[0], P0[1], P0[0] + 46 * t0[0], P0[1] + 46 * t0[1], color=INK, sw=2.0))

    # ---- labels, placed with generous clearance ----
    f.append(text(P0[0] - 12, P0[1] + 6, 'старт', 12, INK, 'end'))
    f.append(text(icc[0], icc[1] - 12, 'ICC', 12, INK, 'middle', bold=True))

    # true end label (green) — right of P1
    f.append(text(P1[0] + 12, P1[1] + 4, 'точна дуга', 12, FIELD, 'start', bold=True))
    # rectangular end label (red) — above/left of Prect (Prect is up-left of P1)
    f.append(text(Prect[0] - 12, Prect[1] - 8, 'прямокутна', 12, POS, 'end', bold=True))
    f.append(text(Prect[0] - 12, Prect[1] + 9, '(курс початку)', 10.5, POS, 'end'))
    # midpoint end label (blue) — above Pmid
    f.append(text(Pmid[0] + 12, Pmid[1] - 8, 'середня точка', 12, NEG, 'start', bold=True))

    # heading arrow label
    hx = P0[0] + 52 * t0[0]
    hy = P0[1] + 52 * t0[1]
    f.append(text(hx - 8, hy + 4, 'θ', 13, INK, 'end', italic=True))

    f.append(text(W // 2, H - 12,
                  'Прямокутна недоводить робота всередину повороту; '
                  'середня точка лягає майже на дугу',
                  11, MUTED, 'middle'))
    render(os.path.join(IMG, 'arc-integration.svg'), W, H, *f,
           title='Три схеми інтегрування однієї дуги')


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — the wheel-speed space. Motor limits |v_L|,|v_R| ≤ v_max make a
# square; (v, ω) are the same plane rotated 45°, so the feasible (v, ω) region is
# that square standing on a corner. A command outside is pulled back either by
# proportional scaling (radially to centre → same arc) or by clipping to a side
# (keeps v, changes ω → wrong arc). Point: scale the pair, don't clip singly.
# ════════════════════════════════════════════════════════════════════════════
def fig_wheel_space():
    W, H = 620, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    cx, cy = 300, 290
    S = 148.0                        # half-side of the square = v_max in px

    # the square of motor limits (axes = v_L horizontal, v_R vertical)
    f.append(rect(cx - S, cy - S, 2 * S, 2 * S, fill='#f7f9fc', stroke=INK, sw=2.0, rx=0))

    # axes v_L, v_R (light) through centre
    f.append(line(cx - S - 34, cy, cx + S + 34, cy, color=MUTED, sw=1.0))
    f.append(line(cx, cy - S - 34, cx, cy + S + 44, color=MUTED, sw=1.0))
    f.append(text(cx + S + 40, cy + 4, 'v_L', 12, MUTED, 'start'))
    f.append(text(cx - 8, cy - S - 40, 'v_R', 12, MUTED, 'middle'))

    # rotated axes: v (forward) along v_L=v_R diagonal; ω along v_R=-v_L diagonal
    f.append(arrow(cx, cy, cx + (S + 24) * 0.707, cy - (S + 24) * 0.707, color=FIELD, sw=2.2))
    f.append(arrow(cx, cy, cx + (S + 24) * 0.707, cy + (S + 24) * 0.707, color=POS, sw=2.2))
    f.append(text(cx + (S + 40) * 0.707 + 4, cy - (S + 40) * 0.707, 'v (уперед)', 12, FIELD, 'start', bold=True))
    f.append(text(cx + (S + 40) * 0.707 + 4, cy + (S + 40) * 0.707 + 4, 'ω (поворот)', 12, POS, 'start', bold=True))

    # a command OUTSIDE the square (upper-right, beyond the corner)
    Cx, Cy = cx + 118, cy - 176
    # proportional scaling: radial to centre, land where the ray meets the square
    # ray from centre through (Cx,Cy); square boundary at max(|dx|,|dy|)=S
    dx, dy = Cx - cx, Cy - cy
    k = S / max(abs(dx), abs(dy))
    Px, Py = cx + dx * k, cy + dy * k          # scaled point on boundary
    # clip endpoint: keep v (project along +v diagonal), clamp the other → a side.
    # Simplest illustrative clip: clamp v_R to top edge, keep v_L.
    Qx, Qy = Cx, cy - S                         # clipped to top side (v_R = v_max)
    if Qx > cx + S: Qx = cx + S
    if Qx < cx - S: Qx = cx - S

    # draw command point and the two corrections
    f.append(line(cx, cy, Cx, Cy, color=MUTED, sw=1.0, dash='4,3'))      # the ray
    f.append(dot(Cx, Cy, 5, INK))
    # proportional: along ray to Px
    f.append(arrow(Cx, Cy, Px, Py, color=NEG, sw=2.4))
    f.append(dot(Px, Py, 4.5, NEG))
    # clip: straight down to the side
    f.append(arrow(Cx, Cy, Qx, Qy, color=POS, sw=2.0))
    f.append(dot(Qx, Qy, 4.5, POS))

    # labels for the command and the two landing points (kept clear of each other)
    f.append(text(Cx + 10, Cy - 8, 'команда', 12, INK, 'start', bold=True))
    f.append(text(Cx + 10, Cy + 9, 'поза межами', 10.5, INK, 'start'))

    # explanation boxes in a clean band BELOW the square (square bottom ≈ cy+S=438)
    band_y = cy + S + 74                      # ≈ 512, clear of the square and its corner labels
    # proportional (blue) — left box, leader up to the Px landing point
    b1, bw1, bh1 = textbox(160, band_y,
                           'пропорційно:\nпо променю до центра\n→ та сама дуга',
                           10.5, pad=7, fill='#eef4ff', stroke=NEG, sw=1.2, color=NEG)
    f.append(b1)
    f.append(line(160, band_y - bh1 / 2, Px - 4, Py + 6, color=NEG, sw=1.0, dash='2,3'))

    # clip (red) — right box, leader up to the Qx landing point
    b2, bw2, bh2 = textbox(460, band_y,
                           'зрізання по грані:\nзберігає v, псує ω\n→ інша дуга',
                           10.5, pad=7, fill='#fdecea', stroke=POS, sw=1.2, color=POS)
    f.append(b2)
    f.append(line(460, band_y - bh2 / 2, Qx + 4, Qy - 4, color=POS, sw=1.0, dash='2,3'))

    f.append(text(W // 2, H - 14,
                  'Рух по променю до центра зберігає відношення v до ω — тобто радіус дуги',
                  11, MUTED, 'middle'))
    render(os.path.join(IMG, 'wheel-space.svg'), W, H, *f,
           title='Досяжні (v, ω) — квадрат обмежень моторів на кут')


# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — heading error eats the coordinate. Two paths from one point: the true
# straight run and the odometric one, which after a heading slip δθ tilts away.
# The lateral gap grows as D·δθ, and because δθ itself slowly accumulates, the gap
# opens ever faster. Point: heading is the most valuable and most fragile number.
# ════════════════════════════════════════════════════════════════════════════
def fig_heading_drift():
    W, H = 700, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    x0, y0 = 90, 250
    Lpath = 520.0
    # true path: straight to the right
    Tx, Ty = x0 + Lpath, y0
    f.append(line(x0, y0, Tx, Ty, color=FIELD, sw=3.0))

    # odometric path: a slightly upward-curving line whose slope grows (accumulating δθ)
    # y = y0 - c*(t^1.5)*scale : curvature increases with distance
    pts = []
    N = 60
    for i in range(N + 1):
        t = i / N
        dxp = Lpath * t
        # growing tilt: lateral offset ~ (dx)^1.6, capped visually
        off = 150.0 * (t ** 1.7)
        pts.append('%.1f,%.1f' % (x0 + dxp, y0 - off))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>'
             % (' '.join(pts), NEG))

    # the small heading-error wedge near the start
    ax = x0 + 150
    # true point at ax
    true_y = y0
    # odo point at ax
    tt = 150.0 / Lpath
    odo_y = y0 - 150.0 * (tt ** 1.7)
    # short tangents to show δθ
    f.append(line(x0, y0, x0 + 120, y0, color=FIELD, sw=1.4, dash='4,3'))
    f.append(line(x0, y0, x0 + 118, y0 - 120.0 * ((118.0 / Lpath) ** 1.7) * (1.7),
                  color=NEG, sw=1.4, dash='4,3'))
    # δθ arc between the two tangents near start
    f.append(arc_path(x0, y0, 70, math.radians(-14), math.radians(0), INK, sw=1.4))
    f.append(text(x0 + 84, y0 - 12, 'δθ', 13, INK, 'start', italic=True))

    # two lateral gap arrows at growing distances D1 < D2
    for frac, lbl in ((0.5, 'D₁'), (0.86, 'D₂')):
        dxp = Lpath * frac
        tyv = y0
        oyv = y0 - 150.0 * (frac ** 1.7)
        gx = x0 + dxp
        f.append(line(gx, tyv, gx, oyv, color=MUTED, sw=1.4))
        f.append(dot(gx, tyv, 3.5, FIELD))
        f.append(dot(gx, oyv, 3.5, NEG))
        # bracket label for the gap, to the right of the vertical
        midy = (tyv + oyv) / 2
        f.append(text(gx + 8, midy + 4, '≈ %s·δθ' % lbl, 11, MUTED, 'start'))
        # distance tick along the true path
        f.append(text(gx, y0 + 20, lbl, 12, INK, 'middle', bold=True))

    # start dot + endpoint labels
    f.append(dot(x0, y0, 5, INK))
    f.append(text(x0 - 8, y0 + 20, 'старт', 12, INK, 'end'))
    f.append(text(Tx + 8, Ty + 4, 'істинний шлях', 12, FIELD, 'start', bold=True))
    # odo endpoint label (upper right, clear of true line)
    last_oy = y0 - 150.0
    f.append(text(Tx + 8, last_oy + 4, 'одометрія', 12, NEG, 'start', bold=True))

    f.append(text(W // 2, H - 12,
                  'Розрив між шляхами росте як відстань × кут, а сам кут накопичується — '
                  'тому розтуляється дедалі швидше',
                  10.5, MUTED, 'middle'))
    render(os.path.join(IMG, 'heading-drift.svg'), W, H, *f,
           title='Похибка курсу роз’їдає координату')


if __name__ == '__main__':
    fig_arc_integration()
    fig_wheel_space()
    fig_heading_drift()
    print('Done.')
