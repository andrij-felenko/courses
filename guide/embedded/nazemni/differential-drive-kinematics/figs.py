# -*- coding: utf-8 -*-
"""Figures for «Кінематика диференціального приводу».
Import svgkit from scripts/ (do not copy it). Output to ./img/.
Run:  python figs.py    then  python ../../../../scripts/svgcheck.py img
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_path(cx, cy, r, a0, a1, color, sw=2.0, dash=None, n=90):
    """Polyline arc around (cx,cy), radius r, angles a0..a1 (radians, SVG y-down)."""
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append('%.1f,%.1f' % (cx + r * math.cos(a), cy + r * math.sin(a)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (' '.join(pts), color, sw, d))


# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — the ICC geometry. Two wheels on one rigid axle of width L both sweep
# arcs about a single instantaneous centre of curvature (ICC). The right (outer)
# wheel rides radius R+L/2, the left (inner) rides R-L/2, the body centre rides R,
# all sharing one angular velocity ω. The point: the turn is one geometric fact —
# a shared centre — not a steering mechanism.
# ════════════════════════════════════════════════════════════════════════════
def fig_icc_geometry():
    W, H = 660, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # ICC at lower-left; robot to the right, turning left (counter-clockwise-ish)
    icc = (120, 360)
    R = 300.0            # radius to body centre (px)
    L = 96.0             # track width (px)
    a = math.radians(-34)  # angle of the axle line from ICC (SVG y-down)

    # centre of axle
    cx = icc[0] + R * math.cos(a)
    cy = icc[1] + R * math.sin(a)
    # wheel contact points along the axle line (perpendicular to radius): the axle
    # points radially, wheels are offset ±L/2 ALONG the radius direction.
    ux, uy = math.cos(a), math.sin(a)          # unit vector ICC -> centre
    rgt = (icc[0] + (R + L / 2) * ux, icc[1] + (R + L / 2) * uy)  # outer wheel
    lft = (icc[0] + (R - L / 2) * ux, icc[1] + (R - L / 2) * uy)  # inner wheel

    # arcs each wheel + centre sweep about ICC
    span = math.radians(30)
    f.append(arc_path(icc[0], icc[1], R + L / 2, a - span, a + span * 0.5, POS, sw=2.2))
    f.append(arc_path(icc[0], icc[1], R - L / 2, a - span, a + span * 0.5, NEG, sw=2.2))
    f.append(arc_path(icc[0], icc[1], R, a - span, a + span * 0.5, MUTED, sw=1.4, dash='5,4'))

    # radius spokes ICC -> each wheel and -> centre
    f.append(line(icc[0], icc[1], rgt[0], rgt[1], color=POS, sw=1.3, dash='4,3'))
    f.append(line(icc[0], icc[1], lft[0], lft[1], color=NEG, sw=1.3, dash='4,3'))
    f.append(line(icc[0], icc[1], cx, cy, color=INK, sw=1.6))

    # the robot body: a rounded rectangle centred at (cx,cy), long axis = heading
    # heading is perpendicular to the axle (radius) direction
    hx, hy = -uy, ux                            # heading unit (perp to radius)
    bodyL, bodyW = 74, 54
    corners = []
    for sgnf, sgns in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        px = cx + sgnf * bodyL / 2 * hx + sgns * bodyW / 2 * ux
        py = cy + sgnf * bodyL / 2 * hy + sgns * bodyW / 2 * uy
        corners.append('%.1f,%.1f' % (px, py))
    f.append('<polygon points="%s" fill="#eef4ff" stroke="%s" stroke-width="1.8"/>'
             % (' '.join(corners), INK))

    # the axle line drawn across the body between wheels
    f.append(line(lft[0], lft[1], rgt[0], rgt[1], color=INK, sw=2.4))

    # wheels as short thick bars perpendicular to axle (i.e. along heading)
    for (wx, wy), col in ((rgt, POS), (lft, NEG)):
        f.append(line(wx - 15 * hx, wy - 15 * hy, wx + 15 * hx, wy + 15 * hy,
                      color=col, sw=6.0))

    # heading arrow from centre
    f.append(arrow(cx, cy, cx + 52 * hx, cy + 52 * hy, color=FIELD, sw=2.2))
    f.append(text(cx + 60 * hx, cy + 60 * hy, 'v', 13, FIELD, 'middle', italic=True))

    # ICC dot + label
    f.append(circle(icc[0], icc[1], 5, fill=INK, stroke=BG, sw=1.4))
    b, bw, bh = textbox(icc[0] + 66, icc[1] - 6, 'ICC\nмиттєвий центр', 11,
                        pad=6, fill='#fff', stroke=INK, sw=1.1, color=INK)
    f.append(b)

    # ω arc near ICC
    f.append(arc_path(icc[0], icc[1], 34, a - span * 0.7, a + span * 0.2, INK, sw=1.6))
    f.append(text(icc[0] + 40 * math.cos(a - span * 0.25),
                  icc[1] + 40 * math.sin(a - span * 0.25) - 6, 'ω', 13, INK, 'middle'))

    # radius labels along spokes
    mid = lambda p, q, t=0.5: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    mc = mid(icc, (cx, cy), 0.52)
    f.append(text(mc[0] - 6, mc[1] - 8, 'R', 13, INK, 'middle', bold=True))
    # нижче по спиці (t=0.64), щоб зелена стрілка курсу від центра не різала напис
    mr = mid(icc, rgt, 0.64)
    f.append(text(mr[0] + 10, mr[1] + 4, 'R + L/2', 10.5, POS, 'start'))
    ml = mid(icc, lft, 0.86)
    f.append(text(ml[0] - 8, ml[1] + 14, 'R − L/2', 10.5, NEG, 'end'))

    # L label across the axle
    lmx, lmy = mid(lft, rgt)
    f.append(text(lmx - 22 * hx, lmy - 22 * hy, 'L (колія)', 10.5, INK, 'middle'))

    # wheel labels
    f.append(text(rgt[0] + 20 * hx + 8, rgt[1] + 20 * hy, 'праве  v_R', 10, POS, 'start'))
    f.append(text(lft[0] - 20 * hx - 8, lft[1] - 20 * hy, 'ліве  v_L', 10, NEG, 'end'))

    f.append(text(W // 2, H - 10,
                  'Обидва колеса й корпус обертаються навколо одного центра ICC — '
                  'зовнішнє по більшому радіусу, внутрішнє по меншому',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'icc-geometry.svg'), W, H, *f,
           title='Геометрія повороту: спільний миттєвий центр')


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — three motion regimes side by side. Straight (equal speeds, ICC at
# infinity), arc (right faster, ICC to the side at finite R), spin-in-place
# (opposite speeds, ICC exactly at the axle midpoint). The point: all three come
# from one pair of formulas; the ICC location alone decides the character of motion.
# ════════════════════════════════════════════════════════════════════════════
def fig_three_modes():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    panel_w = W / 3.0
    cy = 180

    def draw_robot(cx, cy, heading_deg, vL, vR, col_body='#eef4ff'):
        """Small top-down robot: body box + two wheel bars; wheel bar length ∝ |v|,
        colour by sign. heading points 'up' the panel by default."""
        h = math.radians(heading_deg)
        hx, hy = math.cos(h), math.sin(h)      # heading
        ax, ay = -hy, hx                        # axle (perp)
        half = 26
        # body
        bL, bW = 46, 34
        corners = []
        for sgnf, sgns in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
            px = cx + sgnf * bL / 2 * hx + sgns * bW / 2 * ax
            py = cy + sgnf * bL / 2 * hy + sgns * bW / 2 * ay
            corners.append('%.1f,%.1f' % (px, py))
        out = ['<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6"/>'
               % (' '.join(corners), col_body, INK)]
        # axle
        lft = (cx - half * ax, cy - half * ay)
        rgt = (cx + half * ax, cy + half * ay)
        out.append(line(lft[0], lft[1], rgt[0], rgt[1], color=INK, sw=2.0))
        # wheels
        out.append(line(lft[0] - 11 * hx, lft[1] - 11 * hy, lft[0] + 11 * hx, lft[1] + 11 * hy,
                        color=INK, sw=5.0))
        out.append(line(rgt[0] - 11 * hx, rgt[1] - 11 * hy, rgt[0] + 11 * hx, rgt[1] + 11 * hy,
                        color=INK, sw=5.0))
        # velocity arrows on each wheel (length ∝ speed, colour by sign)
        def varr(base, v, side):
            if abs(v) < 0.01:
                return ''
            col = FIELD if v > 0 else POS
            ln = 20 * v
            return arrow(base[0], base[1], base[0] + ln * hx, base[1] + ln * hy, color=col, sw=2.2)
        out.append(varr(lft, vL, 'L'))
        out.append(varr(rgt, vR, 'R'))
        return out, lft, rgt, (hx, hy), (ax, ay)

    # ---- Panel 1: straight ----
    c1 = panel_w * 0.5
    f.append(text(c1, 44, 'Пряма', 13, INK, 'middle', bold=True))
    r1, lft1, rgt1, hd1, ax1 = draw_robot(c1, cy + 20, -90, 1.0, 1.0)
    f.extend(r1)
    f.append(text(c1, cy - 78, 'v_L = v_R', 11, INK, 'middle'))
    f.append(text(c1, cy - 62, 'ω = 0', 11, MUTED, 'middle'))
    # ICC at infinity: dashed axle extended both ways with arrowless ends
    f.append(line(lft1[0] - 60 * ax1[0], lft1[1] - 60 * ax1[1],
                  rgt1[0] + 60 * ax1[0], rgt1[1] + 60 * ax1[1],
                  color=MUTED, sw=1.0, dash='4,4'))
    f.append(text(c1, H - 60, 'ICC → ∞', 11, MUTED, 'middle'))
    f.append(text(c1, H - 44, '(центр на нескінченності)', 9.5, MUTED, 'middle'))

    # ---- Panel 2: arc ----
    c2 = panel_w * 1.5
    f.append(text(c2, 44, 'Дуга', 13, INK, 'middle', bold=True))
    # robot heading up, but turning: ICC to the LEFT at finite radius
    icc2 = (c2 - 92, cy + 24)
    r2, lft2, rgt2, hd2, ax2 = draw_robot(c2, cy + 24, -90, 0.62, 1.0)
    # arc through body centre about icc2
    Rc = math.hypot(c2 - icc2[0], (cy + 24) - icc2[1])
    a_c = math.atan2((cy + 24) - icc2[1], c2 - icc2[0])
    f.append(arc_path(icc2[0], icc2[1], Rc, a_c - 0.5, a_c + 0.5, MUTED, sw=1.4, dash='5,4'))
    f.append(line(icc2[0], icc2[1], c2, cy + 24, color=INK, sw=1.3))
    f.append(circle(icc2[0], icc2[1], 4, fill=INK, stroke=BG, sw=1.2))
    f.extend(r2)
    f.append(text(c2, cy - 74, 'v_R > v_L', 11, INK, 'middle'))
    f.append(text(c2 + 4, cy - 58, 'радіус R', 11, MUTED, 'middle'))
    f.append(text((icc2[0] + c2) / 2, cy + 24 - 8, 'R', 12, INK, 'middle', bold=True))
    f.append(text(c2, H - 52, 'ICC збоку, скінченний R', 10, MUTED, 'middle'))

    # ---- Panel 3: spin in place ----
    c3 = panel_w * 2.5
    f.append(text(c3, 44, 'Розворот на місці', 13, INK, 'middle', bold=True))
    r3, lft3, rgt3, hd3, ax3 = draw_robot(c3, cy + 20, -90, -1.0, 1.0)
    f.extend(r3)
    # ICC at axle midpoint = body centre
    f.append(circle(c3, cy + 20, 5, fill=INK, stroke=BG, sw=1.4))
    # rotation ring
    f.append(arc_path(c3, cy + 20, 40, math.radians(-150), math.radians(90), INK, sw=1.6))
    f.append(arrow(c3 + 40 * math.cos(math.radians(90)), cy + 20 + 40 * math.sin(math.radians(90)),
                   c3 + 40 * math.cos(math.radians(70)), cy + 20 + 40 * math.sin(math.radians(70)),
                   color=INK, sw=1.6))
    f.append(text(c3, cy - 78, 'v_R = −v_L', 11, INK, 'middle'))
    f.append(text(c3, cy - 62, 'v = 0', 11, MUTED, 'middle'))
    f.append(text(c3, H - 52, 'ICC точно між колесами', 10, MUTED, 'middle'))

    # panel dividers
    f.append(line(panel_w, 58, panel_w, H - 66, color='#e5e7eb', sw=1.0))
    f.append(line(2 * panel_w, 58, 2 * panel_w, H - 66, color='#e5e7eb', sw=1.0))

    f.append(text(W // 2, H - 14,
                  'Зелена стрілка — колесо вперед, червона — назад; довжина ∝ швидкості. '
                  'Положення ICC визначає режим',
                  9.5, MUTED, 'middle'))
    render(os.path.join(IMG, 'three-modes.svg'), W, H, *f,
           title='Три режими руху з однієї пари формул')


if __name__ == '__main__':
    fig_icc_geometry()
    fig_three_modes()
    print('Done.')
