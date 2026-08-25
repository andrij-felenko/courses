# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Figure 1: why-zero-slope
# A smooth curve with one local max and one local min. Tangent lines drawn:
#   - on the rising stretch  → slope up   (f′>0)
#   - at the peak            → horizontal (f′=0)
#   - on the falling stretch → slope down (f′<0)
#   - at the trough          → horizontal (f′=0)
# Curve: f(x) = a cubic shaped to have max near x≈1.4, min near x≈3.6.
#   f(x) = 0.5*x³ - 3.75*x² + 8*x ... we instead use a hand-tuned smooth bump.
# We'll use  f(x) = 0.25*(x-2.5)³ - 1.6*(x-2.5) + 3.6  shifted, giving a clean
#   local max then local min over x∈[0.4, 4.6].
# ════════════════════════════════════════════════════════════════════════════

W, H = 600, 380

ox, oy = 60, 200        # SVG coords of math origin (0,0) — y=0 sits mid-canvas
sx = 112                # px per x-unit
sy = 52                 # px per y-unit


def gx(xv): return ox + xv * sx
def gy(yv): return oy - yv * sy


# curve: local max around x≈1.1, local min around x≈3.0
def f(x):
    return 0.30 * (x - 2.05) ** 3 - 1.05 * (x - 2.05) + 1.55


def fp(x):  # derivative
    return 0.90 * (x - 2.05) ** 2 - 1.05


# critical points: fp=0 → (x-2.05)² = 1.05/0.90 = 1.1667 → x-2.05 = ±1.080
xc_max = 2.05 - 1.080   # ≈ 0.970  (local max)
xc_min = 2.05 + 1.080   # ≈ 3.130  (local min)

frags = []
frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

# ── axes (x only; y-axis label omitted to keep it clean)
frags.append(arrow(gx(-0.1), gy(0), gx(4.55), gy(0), color=INK, sw=1.4))
frags.append(text(gx(4.62), gy(0) + 5, 'x', 13, INK, 'start'))

# ── the curve over x∈[0.30, 4.30]
N = 120
xa, xb = 0.30, 4.30
pts = []
for i in range(N + 1):
    xv = xa + (xb - xa) * i / N
    yv = f(xv)
    pts.append('%.1f,%.1f' % (gx(xv), gy(yv)))
frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(pts), FIELD))


# ── helper: draw a tangent segment of half-length L (in x) centred at x0
def tangent_seg(x0, L, color, sw=2.0, dash=None):
    y0 = f(x0)
    s = fp(x0)
    p1 = (gx(x0 - L), gy(y0 - s * L))
    p2 = (gx(x0 + L), gy(y0 + s * L))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p1[0], p1[1], p2[0], p2[1], color, sw, d))


# rising stretch: pick x=0.30 (left of max) → slope > 0
x_rise = 0.34
frags.append(tangent_seg(x_rise, 0.42, POS))
# falling stretch: pick x=2.05 (between, steepest descent) → slope < 0
x_fall = 2.05
frags.append(tangent_seg(x_fall, 0.46, NEG))
# horizontal at max and min
frags.append(tangent_seg(xc_max, 0.52, INK, sw=2.2))
frags.append(tangent_seg(xc_min, 0.52, INK, sw=2.2))

# ── dots on curve at the four tangent points
frags.append(circle(gx(x_rise), gy(f(x_rise)), 4, fill=POS, stroke=INK, sw=1))
frags.append(circle(gx(x_fall), gy(f(x_fall)), 4, fill=NEG, stroke=INK, sw=1))
frags.append(circle(gx(xc_max), gy(f(xc_max)), 5, fill='#ffffff', stroke=INK, sw=1.6))
frags.append(circle(gx(xc_min), gy(f(xc_min)), 5, fill='#ffffff', stroke=INK, sw=1.6))

# ── labels near tangents
frags.append(text(gx(x_rise) - 6, gy(f(x_rise)) - 14, "f′>0", 12, POS, 'middle'))
frags.append(text(gx(x_fall) + 38, gy(f(x_fall)) + 4, "f′<0", 12, NEG, 'middle'))
frags.append(text(gx(xc_max), gy(f(xc_max)) - 16, "f′=0  максимум", 12, INK, 'middle', bold=True))
frags.append(text(gx(xc_min), gy(f(xc_min)) + 26, "f′=0  мінімум", 12, INK, 'middle', bold=True))

# ── caption
frags.append(text(W // 2, H - 12,
    'Дотична горизонтальна лише на вершині й на дні — там, де нахил зникає',
    11, MUTED, 'middle'))

render(os.path.join(IMG, 'why-zero-slope.svg'), W, H, *frags,
       title='Чому в екстремумі похідна = 0')


# ════════════════════════════════════════════════════════════════════════════
# Figure 2: second-derivative-test
# Two panels side by side:
#   LEFT  — chasha (∪): minimum, f″>0, slope arrows −,0,+
#   RIGHT — kupol (∩): maximum, f″<0, slope arrows +,0,−
# ════════════════════════════════════════════════════════════════════════════

W2, H2 = 640, 360
frags2 = []
frags2.append(rect(0, 0, W2, H2, fill=BG, stroke='none', sw=0, rx=0))


def parabola(cx_px, cy_px, scale_x, scale_y, sign, color):
    """sign=+1 → ∪ (min), sign=-1 → ∩ (max). Returns polyline + vertex point.
       Local coords u∈[-1.3,1.3], y_local = sign*u²."""
    pts = []
    N = 60
    for i in range(N + 1):
        u = -1.3 + 2.6 * i / N
        yl = sign * (u * u)
        px = cx_px + u * scale_x
        py = cy_px - yl * scale_y
        pts.append('%.1f,%.1f' % (px, py))
    poly = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
            % (' '.join(pts), color))
    return poly


# ── panel geometry
# LEFT panel centre, RIGHT panel centre
pad = 26
panel_w = (W2 - 3 * pad) / 2
left_cx = pad + panel_w / 2
right_cx = 2 * pad + panel_w + panel_w / 2

# panel frames
ptop, pbot = 64, 300
frags2.append(rect(pad, ptop, panel_w, pbot - ptop, fill='#f8f9fa', stroke=MUTED, sw=1, rx=8))
frags2.append(rect(2 * pad + panel_w, ptop, panel_w, pbot - ptop, fill='#f8f9fa', stroke=MUTED, sw=1, rx=8))

scale_x = 78
scale_y = 70

# ── LEFT: minimum (∪), f″>0
min_cy = 230   # vertex near bottom of its arc (arc opens up, vertex is lowest)
frags2.append(parabola(left_cx, min_cy, scale_x, scale_y, +1, NEG))
# vertex dot (lowest point of ∪ at u=0)
frags2.append(circle(left_cx, min_cy, 5, fill='#ffffff', stroke=INK, sw=1.6))
# slope arrows along the curve: left side slope negative (down-right),
#   vertex flat, right side slope positive (up-right)
# left tangent arrow at u=-0.85
ulx = -0.85
lx_px = left_cx + ulx * scale_x
lx_py = min_cy - (ulx * ulx) * scale_y
frags2.append(arrow(lx_px - 22, lx_py - 20, lx_px + 16, lx_py + 14, color=POS, sw=2.0))
frags2.append(text(lx_px - 30, lx_py - 26, '−', 18, POS, 'middle', bold=True))
# right tangent arrow at u=+0.85
urx = 0.85
rx_px = left_cx + urx * scale_x
rx_py = min_cy - (urx * urx) * scale_y
frags2.append(arrow(rx_px - 16, rx_py + 14, rx_px + 22, rx_py - 20, color=POS, sw=2.0))
frags2.append(text(rx_px + 30, rx_py - 26, '+', 18, POS, 'middle', bold=True))
# flat marker at vertex
frags2.append(line(left_cx - 20, min_cy, left_cx + 20, min_cy, color=INK, sw=2.0))
frags2.append(text(left_cx, min_cy + 22, '0', 13, INK, 'middle', bold=True))
# labels
frags2.append(text(left_cx, ptop + 24, "f″ > 0   мінімум", 14, NEG, 'middle', bold=True))
frags2.append(text(left_cx, pbot + 26, "чаша ∪ : нахил зростає −→0→+", 12, MUTED, 'middle'))

# ── RIGHT: maximum (∩), f″<0
max_cy = 134   # vertex near top of its arc (arc opens down, vertex is highest)
frags2.append(parabola(right_cx, max_cy, scale_x, scale_y, -1, POS))
frags2.append(circle(right_cx, max_cy, 5, fill='#ffffff', stroke=INK, sw=1.6))
# left side slope positive (up-right), vertex flat, right side slope negative (down-right)
lx2_px = right_cx + ulx * scale_x
lx2_py = max_cy + (ulx * ulx) * scale_y
frags2.append(arrow(lx2_px - 22, lx2_py + 20, lx2_px + 16, lx2_py - 14, color=NEG, sw=2.0))
frags2.append(text(lx2_px - 30, lx2_py + 28, '+', 18, NEG, 'middle', bold=True))
rx2_px = right_cx + urx * scale_x
rx2_py = max_cy + (urx * urx) * scale_y
frags2.append(arrow(rx2_px - 16, rx2_py - 14, rx2_px + 22, rx2_py + 20, color=NEG, sw=2.0))
frags2.append(text(rx2_px + 30, rx2_py + 28, '−', 18, NEG, 'middle', bold=True))
frags2.append(line(right_cx - 20, max_cy, right_cx + 20, max_cy, color=INK, sw=2.0))
frags2.append(text(right_cx, max_cy - 12, '0', 13, INK, 'middle', bold=True))
frags2.append(text(right_cx, ptop + 24, "f″ < 0   максимум", 14, POS, 'middle', bold=True))
frags2.append(text(right_cx, pbot + 26, "купол ∩ : нахил спадає +→0→−", 12, MUTED, 'middle'))

# ── caption
frags2.append(text(W2 // 2, H2 - 10,
    'Знак другої похідної = знак кривини: чаша це мінімум, купол це максимум',
    11, MUTED, 'middle'))

render(os.path.join(IMG, 'second-derivative-test.svg'), W2, H2, *frags2,
       title='Тест другої похідної')

print('Done.')
