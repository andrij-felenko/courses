import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Figure: secant-to-tangent ───────────────────────────────────────────────
# Shows parabola f(x)=x² and how the secant line through (x0, f(x0)) and
# a second point converges to the tangent as Δx→0.
# x-range shown: [0, 3.5], y-range: [0, 7]
# Coordinate system origin at pixel (ox=80, oy=340), scale sx=110, sy=42 px/unit
# => at y=7: SVG_y = 340 - 7*42 = 340-294 = 46  (well inside H=380)
# => at x=3.5: SVG_x = 80 + 3.5*110 = 465  (inside W=560)

W, H = 580, 370

ox, oy = 80, 340   # SVG coords of math origin (0,0)
sx = 108           # px per x-unit
sy = 42            # px per y-unit

def gx(xv): return ox + xv * sx
def gy(yv): return oy - yv * sy   # math y up → SVG y down

frags = []

# background (transparent via BG)
frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

# ── axes
frags.append(arrow(gx(-0.15), gy(0), gx(3.6), gy(0), color=INK, sw=1.5))
frags.append(text(gx(3.7), gy(0)+5, 'x', 14, INK, 'start'))
frags.append(arrow(gx(0), gy(-0.2), gx(0), gy(7.2), color=INK, sw=1.5))
frags.append(text(gx(0)+5, gy(7.3), 'y', 14, INK, 'start'))

# tick marks x: 1, 2, 3
for xi in [1, 2, 3]:
    frags.append(line(gx(xi), gy(0)-4, gx(xi), gy(0)+4, color=INK, sw=1))
    frags.append(text(gx(xi), gy(0)+17, str(xi), 12, INK, 'middle'))
# tick marks y: 1, 2, 4, 6 (skip odd crowded ones)
for yi, lab in [(2, '2'), (4, '4'), (6, '6')]:
    frags.append(line(gx(0)-4, gy(yi), gx(0)+4, gy(yi), color=INK, sw=1))
    frags.append(text(gx(0)-8, gy(yi)+4, lab, 12, INK, 'end'))

# ── parabola f(x)=x² for x in [0, 2.65] (so max y ≤ 7.0)
N = 80
pts_para = []
for i in range(N+1):
    xv = i * 2.65 / N
    yv = xv * xv
    if 0 <= gy(yv) <= H and 0 <= gx(xv) <= W:
        pts_para.append('%.1f,%.1f' % (gx(xv), gy(yv)))
frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (' '.join(pts_para), FIELD))

# ── key point x0=2
x0, y0 = 2.0, 4.0

# ── tangent at x0=2: slope=4, y=4+4*(x-2)
def tang(xv): return y0 + 4.0*(xv - x0)
# range x in [0.8, 2.6] to stay inside canvas
tx_pairs = [(gx(0.95), gy(tang(0.95))), (gx(2.6), gy(tang(2.6)))]
frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (' '.join('%.1f,%.1f' % p for p in tx_pairs), POS))

# ── secant Δx=1.0: x0=2, x1=3, slope=(9-4)/1=5
# Note: x1=3 gives y=9 → gy(9)=340-9*42=-38 (off canvas); we only show the LINE
# across the plot area, not the endpoint dot at x=3.
x1a, sl_a = 3.0, 5.0
def seca(xv): return y0 + sl_a*(xv - x0)
# clip x range so y stays inside [0, H]
# gy(yv) >= 0 => oy - yv*sy >= 0 => yv <= oy/sy = 340/42 ≈ 8.1
# gy(yv) <= H=370 => oy - yv*sy <= H => yv >= (oy-H)/sy = -30/42 < 0 (always)
# so clip y to ≤ 8.0 → x in [0, sqrt(8)=2.83]; use x∈[1.05, 2.58] for display
seca_x_max = 2.58   # seca(2.58): y=4+5*(2.58-2)=4+2.9=6.9 → gy≈49 ok
seca_pairs = [(gx(1.05), gy(seca(1.05))), (gx(seca_x_max), gy(seca(seca_x_max)))]
frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="8,4"/>'
             % (' '.join('%.1f,%.1f' % p for p in seca_pairs), MUTED))

# ── secant Δx=0.5: x0=2, x1=2.5, slope=(6.25-4)/0.5=4.5
x1b, sl_b = 2.5, 4.5
def secb(xv): return y0 + sl_b*(xv - x0)
secb_pairs = [(gx(1.1), gy(secb(1.1))), (gx(2.6), gy(secb(2.6)))]
frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>'
             % (' '.join('%.1f,%.1f' % p for p in secb_pairs), NEG))

# ── dots for key points
frags.append(circle(gx(x0), gy(y0), 5, fill=POS, stroke=INK, sw=1.2))   # x0 on parabola
# x1a=3 → y=9 is off canvas; show dot at the visible endpoint of the secant line instead
frags.append(circle(gx(seca_x_max), gy(seca(seca_x_max)), 4, fill=MUTED, stroke=INK, sw=1))
frags.append(circle(gx(x1b), gy(x1b**2), 4, fill=NEG, stroke=INK, sw=1))     # Δx=0.5 point

# ── small Δx labels near the x-axis (bracket x0 to x1a=3 → clip bracket to 2.58)
frags.append(line(gx(x0), gy(0)+6, gx(seca_x_max), gy(0)+6, color=MUTED, sw=1))
frags.append(text(gx((x0+seca_x_max)/2), gy(0)+20, 'Δx=1', 10, MUTED, 'middle'))
frags.append(line(gx(x0), gy(0)+22, gx(x1b), gy(0)+22, color=NEG, sw=1))
frags.append(text(gx((x0+x1b)/2), gy(0)+34, 'Δx=0.5', 10, NEG, 'middle'))

# ── slope annotations beside each line
frags.append(text(gx(seca_x_max)+4, gy(seca(seca_x_max))-6, 'нахил 5', 10, MUTED, 'start'))
frags.append(text(gx(x1b)+4, gy(x1b**2)-6, 'нахил 4.5', 10, NEG, 'start'))
frags.append(text(gx(2.62), gy(tang(2.62))+14, 'нахил 4', 10, POS, 'start'))

# ── legend
leg_x, leg_y = W - 208, 12
frags.append(rect(leg_x-4, leg_y, 202, 92, fill='#f8f9fa', stroke=MUTED, sw=1, rx=6))
items = [
    (FIELD, None,  'f(x) = x²'),
    (MUTED, '8,4', 'Сікна  Δx = 1'),
    (NEG,   '5,3', 'Сікна  Δx = 0.5'),
    (POS,   None,  'Дотична  (Δx → 0)'),
]
for i, (col, dash, label) in enumerate(items):
    yy = leg_y + 12 + i * 20
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    frags.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2"%s/>'
                 % (leg_x+4, yy+7, leg_x+26, yy+7, col, d))
    frags.append(text(leg_x+32, yy+11, label, 11, INK, 'start'))

# ── caption
frags.append(text(W//2, H-8,
    'Що менший Δx — то ближча сікна до дотичної; при Δx→0 вони збігаються',
    10, MUTED, 'middle'))

render(os.path.join(IMG, 'secant-to-tangent.svg'), W, H, *frags,
       title='Сікна → Дотична: границя відношення приростів')

print('Done.')
