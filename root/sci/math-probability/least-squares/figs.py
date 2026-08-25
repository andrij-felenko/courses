# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Figure 1: scatter + best-fit line + residuals
# A cloud of (x,y) data points around a rising trend. The least-squares line is
# drawn through them; from each point a thin VERTICAL segment to the line shows
# its residual (the quantity whose squares we minimise). This is the central
# picture of the whole article: line + the vertical gaps it tries to shrink.
# Data hand-chosen so the fit slope ≈ 0.8 and the residuals are clearly visible.
# ════════════════════════════════════════════════════════════════════════════
W, H = 600, 400

ox, oy = 70, 340          # SVG coords of math origin (0,0)
sx = 46                   # px per x-unit
sy = 30                   # px per y-unit


def gx(xv): return ox + xv * sx
def gy(yv): return oy - yv * sy


# data: x = 1..10, y = 0.8x + 1 + scatter (hand-tuned, both signs of residual)
data = [(1, 2.4), (2, 2.0), (3, 4.1), (4, 3.6), (5, 5.6),
        (6, 5.2), (7, 7.4), (8, 6.6), (9, 8.6), (10, 8.2)]

# least-squares fit computed once so the picture is honest
n = len(data)
sxsum = sum(p[0] for p in data)
sysum = sum(p[1] for p in data)
sxx = sum(p[0] * p[0] for p in data)
sxy = sum(p[0] * p[1] for p in data)
k = (n * sxy - sxsum * sysum) / (n * sxx - sxsum * sxsum)
b = (sysum - k * sxsum) / n


def fit(xv): return k * xv + b


frags = []
frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

# ── axes
frags.append(arrow(gx(-0.2), gy(0), gx(11.0), gy(0), color=INK, sw=1.4))
frags.append(arrow(gx(0), gy(-0.2), gx(0), gy(10.2), color=INK, sw=1.4))
frags.append(text(gx(11.1), gy(0) + 5, 'x', 14, INK, 'start'))
frags.append(text(gx(0) - 8, gy(10.4), 'y', 14, INK, 'end'))

# light gridline ticks on x
for xt in range(1, 11):
    frags.append(line(gx(xt), gy(0) - 3, gx(xt), gy(0) + 3, color=MUTED, sw=1.0))

# ── the fitted line over x∈[0.3, 10.7]
frags.append(line(gx(0.3), gy(fit(0.3)), gx(10.7), gy(fit(10.7)), color=NEG, sw=2.4))
frags.append(text(gx(10.7), gy(fit(10.7)) - 10, 'y = k·x + b', 13, NEG, 'end', bold=True))

# ── residuals: vertical segment from each point to the line (the gaps we shrink)
for (xv, yv) in data:
    yl = fit(xv)
    frags.append(line(gx(xv), gy(yv), gx(xv), gy(yl), color=FIELD, sw=1.6, dash="3,2"))

# ── data points on top
for (xv, yv) in data:
    frags.append(circle(gx(xv), gy(yv), 4.2, fill=POS, stroke="#7d211a", sw=1.2))

# ── one labelled residual to name the idea (point on the left, big gap)
# point (3, 4.1): residual = y - fit ; the upper-left region is empty (points rise)
xv, yv = 3, 4.1
yl = fit(xv)
midy = (gy(yv) + gy(yl)) / 2
box, bw, bh = textbox(gx(2.0) + 4, gy(9.0), "залишок rᵢ = yᵢ − (k·xᵢ + b)",
                      size=12, fill="#eafbf0", stroke=FIELD, color=INK)
frags.append(box)
# leader from the box down to the labelled residual segment
frags.append(line(gx(2.0) + 4, gy(9.0) + bh / 2, gx(xv), midy, color=FIELD, sw=1.0, dash="2,2"))

render(os.path.join(IMG, 'scatter-fit-residuals.svg'), W, H, *frags)


# ════════════════════════════════════════════════════════════════════════════
# Figure 2: why squares — parabola penalty bowl vs absolute-value V
# Left: the squared-error penalty r² is a smooth bowl with a single rounded
#   bottom and a unique minimum; its slope passes smoothly through zero.
# Right: the absolute-error penalty |r| is a sharp V — a kink at the bottom,
#   slope jumps from −1 to +1, no derivative at the minimum.
# This carries the three reasons squares win: smooth (differentiable), single
#   clean minimum from slope=0, and the bowl GROWS FAST so big errors are
#   punished much harder than small ones (steepness).
# ════════════════════════════════════════════════════════════════════════════
W2, H2 = 640, 384

# two panels side by side
def panel(cx0, title, square):
    """Return svg frags for one penalty panel centred at column cx0."""
    f = []
    base = 250          # y of the r=0 baseline
    halfw = 118         # px each side of centre for r∈[-3,3]
    pscale = 23         # vertical px per penalty unit
    cx = cx0

    # axes for this panel
    f.append(arrow(cx - halfw - 14, base, cx + halfw + 14, base, color=INK, sw=1.3))
    f.append(arrow(cx, base + 12, cx, base - 196, color=INK, sw=1.3))
    f.append(text(cx + halfw + 16, base + 5, 'r', 13, INK, 'start'))
    f.append(text(cx - 8, base - 192, 'штраф', 12, INK, 'end'))

    # the penalty curve over r∈[-3,3]
    N = 80
    pts = []
    for i in range(N + 1):
        rv = -3 + 6 * i / N
        pen = rv * rv if square else abs(rv)
        px = cx + (rv / 3) * halfw
        py = base - pen * pscale * (1.0 if square else 2.6)  # scale |r| so heights compare
        pts.append("%.1f,%.1f" % (px, py))
    col = FIELD if square else POS
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), col))

    # mark the minimum (r=0)
    f.append(circle(cx, base, 4.0, fill=col, stroke=INK, sw=1.2))

    # title under panel (clear of the annotation box below)
    f.append(text(cx, base + 38, title, 14, INK, 'middle', bold=True))
    return f


frags2 = []
frags2.append(rect(0, 0, W2, H2, fill=BG, stroke='none', sw=0, rx=0))
frags2.append(text(W2 / 2, 30, 'Чим штрафувати відхилення r', 16, INK, 'middle', bold=True))

frags2 += panel(160, 'квадрат  r²  — гладка чаша', True)
frags2 += panel(480, 'модуль  |r|  — гострий злам', False)

# short annotations under each panel (kept narrow so the two boxes never touch)
b1, w1, h1 = textbox(160, 360, "дно гладке →\nодин чіткий мінімум",
                     size=12, fill="#eafbf0", stroke=FIELD, color=INK)
frags2.append(b1)
b2, w2, h2 = textbox(480, 360, "у дні злам →\nпохідної немає",
                     size=12, fill="#fdeeec", stroke=POS, color=INK)
frags2.append(b2)

render(os.path.join(IMG, 'why-squares.svg'), W2, H2, *frags2)


# ════════════════════════════════════════════════════════════════════════════
# Figure 3: the sum of squares as literal areas, shrunk at the optimum
# The same scatter, two candidate lines:
#   - a tilted/wrong line: each residual drawn as a SQUARE (area = r²), big total
#   - the best-fit line:    squares are visibly smaller, total area minimal
# Makes "sum of SQUARES" literal: we shrink total coloured area. Side by side.
# ════════════════════════════════════════════════════════════════════════════
W3, H3 = 740, 360

# compact data for clean squares
data3 = [(1, 1.8), (2, 3.0), (3, 3.2), (4, 4.6), (5, 4.8), (6, 6.2)]
n3 = len(data3)


def lsq(dd):
    xs = sum(p[0] for p in dd); ys = sum(p[1] for p in dd)
    xx = sum(p[0] ** 2 for p in dd); xy = sum(p[0] * p[1] for p in dd)
    kk = (len(dd) * xy - xs * ys) / (len(dd) * xx - xs * xs)
    bb = (ys - kk * xs) / len(dd)
    return kk, bb


kb, bb = lsq(data3)           # best line
# a deliberately worse line: shallower slope, shifted
kw_, bw_ = 0.55, 2.4


def mini_panel(x0, title, kk, bb):
    f = []
    oxl, oyl = x0 + 36, 300
    sxl, syl = 42, 24

    def lx(xv): return oxl + xv * sxl
    def ly(yv): return oyl - yv * syl

    f.append(arrow(lx(-0.1), ly(0), lx(7.0), ly(0), color=INK, sw=1.2))
    f.append(arrow(lx(0), ly(-0.1), lx(0), ly(7.4), color=INK, sw=1.2))
    f.append(text(lx(7.0), ly(0) + 5, 'x', 12, INK, 'start'))

    # the line
    f.append(line(lx(0.2), ly(kk * 0.2 + bb), lx(6.6), ly(kk * 6.6 + bb), color=NEG, sw=2.2))

    total = 0.0
    # residual squares: side length = |r| in DATA units, drawn to the right of x
    for (xv, yv) in data3:
        yl = kk * xv + bb
        r = yv - yl
        total += r * r
        side_px = abs(r) * syl                 # square side in px (use y-scale)
        # anchor square between point and line, extended horizontally
        topy = min(ly(yv), ly(yl))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s" fill-opacity="0.30" stroke="%s" stroke-width="1.0"/>'
                 % (lx(xv), topy, side_px, side_px, FIELD, FIELD))
        # vertical residual line itself
        f.append(line(lx(xv), ly(yv), lx(xv), ly(yl), color=FIELD, sw=1.4))
        f.append(circle(lx(xv), ly(yv), 3.6, fill=POS, stroke="#7d211a", sw=1.1))

    f.append(text(x0 + 165, 36, title, 13, INK, 'middle', bold=True))
    # show the total S as a number
    bsum, wsum, hsum = textbox(x0 + 165, 332,
                               "сума квадратів S = %.1f" % total,
                               size=12, fill=FILL, stroke=LINE, color=INK)
    f.append(bsum)
    return f


frags3 = []
frags3.append(rect(0, 0, W3, H3, fill=BG, stroke='none', sw=0, rx=0))
frags3 += mini_panel(10, 'довільна пряма — площа велика', kw_, bw_)
frags3 += mini_panel(380, 'найкраща пряма — площа найменша', kb, bb)

render(os.path.join(IMG, 'sum-of-squares-areas.svg'), W3, H3, *frags3)

print("ok: 3 figures ->", IMG)
print("fit line 1: k=%.3f b=%.3f" % (k, b))
print("fit line 3: k=%.3f b=%.3f ; worse k=%.2f b=%.2f" % (kb, bb, kw_, bw_))
