import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: метод голова-до-хвоста (3 на схід + 4 на північ = 5) ───────────

def fig_head_to_tail():
    W, H = 520, 380
    # Origin (start point)
    ox, oy = 80, 290

    # Vector a: 3 km east (→)  scale: 1 km = 70 px
    scale = 70
    ax = ox + 3 * scale   # 290
    ay = oy               # 290

    # Vector b: 4 km north (↑) from tip of a
    bx = ax               # 290
    by = ay - 4 * scale   # 290 - 280 = 10 ... let's recalc: 4*70=280 → by = 290-280=10
    # that's too tight; use scale=55
    scale = 55
    ax = ox + 3 * scale   # 80+165=245
    ay = oy
    bx = ax
    by = ay - 4 * scale   # 290-220=70

    # Resultant: from ox,oy to bx,by
    parts = []

    # Grid / axes (light)
    parts.append(line(ox, oy + 20, ox, 20, color=MUTED, sw=1, dash="4 4"))
    parts.append(line(ox - 20, oy, W - 30, oy, color=MUTED, sw=1, dash="4 4"))

    # Compass labels
    parts.append(text(W - 28, oy + 5, "Схід", size=12, color=MUTED, anchor="middle"))
    parts.append(text(ox, 14, "Північ", size=12, color=MUTED, anchor="middle"))

    # Vector a (east) — blue
    parts.append(arrow(ox, oy, ax - 2, ay, color=NEG, sw=2.5))
    tb, tw, th = textbox(ox + (ax - ox) / 2, oy + 28, "a = 3 км →", size=13, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1)
    parts.append(tb)

    # Vector b (north) — green
    parts.append(arrow(ax, ay, bx, by + 2, color=FIELD, sw=2.5))
    tb2, _, _ = textbox(ax + 52, (ay + by) / 2, "b = 4 км ↑", size=13, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1)
    parts.append(tb2)

    # Resultant — red
    parts.append(arrow(ox, oy, bx - 1, by + 1, color=POS, sw=2.5))

    # Angle arc at origin
    ang = math.degrees(math.atan2(oy - by, bx - ox))
    # Draw small arc indication
    r_arc = 30
    # arc from 0° to angle (measuring from east, going north = negative y)
    # atan2 gives angle in standard math coords; in SVG y is flipped
    ang_svg = -math.atan2(oy - by, bx - ox)  # angle from +x axis in standard coords
    arc_x = ox + r_arc * math.cos(ang_svg / 2)
    arc_y = oy - r_arc * math.sin(ang_svg / 2)

    # Label for resultant
    mid_rx = (ox + bx) / 2 - 48
    mid_ry = (oy + by) / 2
    tb3, _, _ = textbox(mid_rx, mid_ry, "|c| = 5 км", size=13, color=POS, fill="#fdecea", stroke=POS, sw=1)
    parts.append(tb3)

    # Start/end dots
    parts.append(circle(ox, oy, 5, fill=INK, stroke=INK, sw=1))
    parts.append(circle(bx, by, 5, fill=POS, stroke=POS, sw=1))
    parts.append(circle(ax, ay, 4, fill=MUTED, stroke=MUTED, sw=1))

    # Labels start / corner / end
    parts.append(text(ox - 12, oy + 16, "Старт", size=12, color=INK, anchor="end"))
    parts.append(text(ax + 10, ay + 16, "Поворот", size=12, color=MUTED, anchor="start"))
    parts.append(text(bx + 10, by - 4, "Фініш", size=12, color=POS, anchor="start"))

    # Right angle mark at corner
    sq = 10
    parts.append(f'<polyline points="{ax},{ay-sq} {ax+sq},{ay-sq} {ax+sq},{ay}" '
                 f'fill="none" stroke="{MUTED}" stroke-width="1.2"/>')

    render(os.path.join(OUT, "head-to-tail.svg"), W, H, *parts)


# ── Фігура 2: правило паралелограма ──────────────────────────────────────────

def fig_parallelogram():
    W, H = 500, 360
    ox, oy = 90, 270

    # Vector a: right-down (simulating two forces from common point)
    # a = (200, -60) in SVG coords (→ and slightly ↑ = negative y)
    # b = (80, -180) in SVG coords (slightly → and strongly ↑)
    adx, ady = 190, -55
    bdx, bdy = 75, -175

    ax = ox + adx
    ay = oy + ady
    bx = ox + bdx
    by = oy + bdy

    # Parallelogram corners: O, A, C (tip), B
    cx = ox + adx + bdx
    cy = oy + ady + bdy

    parts = []

    # Dashed sides (copies for parallelogram)
    parts.append(line(bx, by, cx, cy, color=MUTED, sw=1.2, dash="5 4"))
    parts.append(line(ax, ay, cx, cy, color=MUTED, sw=1.2, dash="5 4"))

    # Small arrowheads on dashed lines (indicate copy/shift)
    parts.append(arrow(bx + 1, by + 1, cx - 1, cy - 1, color=MUTED, sw=1.2))
    parts.append(arrow(ax + 1, ay + 1, cx - 1, cy - 1, color=MUTED, sw=1.2))

    # Vector a — blue
    parts.append(arrow(ox, oy, ax - 1, ay - 1 if ady < 0 else ay + 1, color=NEG, sw=2.5))
    tb_a, _, _ = textbox(ox + adx / 2 + 10, oy + ady / 2 + 22, "a", size=15, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1)
    parts.append(tb_a)

    # Vector b — green
    parts.append(arrow(ox, oy, bx - 1 if bdx > 0 else bx + 1, by + 1, color=FIELD, sw=2.5))
    tb_b, _, _ = textbox(ox + bdx / 2 - 30, oy + bdy / 2, "b", size=15, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1)
    parts.append(tb_b)

    # Resultant diagonal — red
    parts.append(arrow(ox, oy, cx - 1, cy + 1, color=POS, sw=2.8))
    tb_c, _, _ = textbox(ox + (adx + bdx) / 2 + 18, oy + (ady + bdy) / 2 - 10, "a + b", size=14, color=POS, fill="#fdecea", stroke=POS, sw=1)
    parts.append(tb_c)

    # Dots
    parts.append(circle(ox, oy, 5, fill=INK, stroke=INK, sw=1))
    parts.append(circle(ax, ay, 4, fill=NEG, stroke=NEG, sw=1))
    parts.append(circle(bx, by, 4, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(circle(cx, cy, 5, fill=POS, stroke=POS, sw=1))

    # Label origin
    parts.append(text(ox - 8, oy + 16, "O", size=13, color=INK, anchor="end"))
    parts.append(text(cx + 8, cy, "C = a+b", size=12, color=POS, anchor="start"))

    render(os.path.join(OUT, "parallelogram.svg"), W, H, *parts)


# ── Фігура 3: покомпонентне складання ────────────────────────────────────────

def fig_components():
    W, H = 560, 400
    ox, oy = 70, 330

    # Vector a = (3, 2) in math coords → scale to px
    scale = 60
    # a = (3, 2): SVG x right, y down → ady = -2*scale
    adx, ady = 3 * scale, -2 * scale   # (180, -120)
    # b = (1, 3)
    bdx, bdy = 1 * scale, -3 * scale   # (60, -180)
    # c = a+b = (4, 5)
    cdx, cdy = adx + bdx, ady + bdy   # (240, -300)

    ax, ay = ox + adx, oy + ady
    bx, by = ox + bdx, oy + bdy
    cx, cy = ox + cdx, oy + cdy

    parts = []

    # Axes
    parts.append(arrow(ox - 15, oy, ox + cdx + 50, oy, color=MUTED, sw=1.2))
    parts.append(arrow(ox, oy + 15, ox, oy + cdy - 20, color=MUTED, sw=1.2))
    parts.append(text(ox + cdx + 55, oy + 5, "x", size=13, color=MUTED, anchor="start"))
    parts.append(text(ox - 5, oy + cdy - 24, "y", size=13, color=MUTED, anchor="end"))

    # aₓ projection (horizontal dashed from O to ax)
    parts.append(line(ox, oy, ax, oy, color=NEG, sw=1.2, dash="5 3"))
    parts.append(line(ax, oy, ax, ay, color=NEG, sw=1.2, dash="5 3"))

    # bₓ projection
    parts.append(line(ox, oy, bx, oy, color=FIELD, sw=1.2, dash="5 3"))
    parts.append(line(bx, oy, bx, by, color=FIELD, sw=1.2, dash="5 3"))

    # cₓ label on axis
    parts.append(line(cx, oy - 5, cx, oy + 5, color=POS, sw=1.5))
    parts.append(text(cx, oy + 17, "cₓ=4", size=12, color=POS, anchor="middle"))

    # cy label on axis
    parts.append(line(ox - 5, cy, ox + 5, cy, color=POS, sw=1.5))
    parts.append(text(ox - 10, cy + 4, "c_y=5", size=12, color=POS, anchor="end"))

    # aₓ on axis label
    parts.append(line(ax, oy - 4, ax, oy + 4, color=NEG, sw=1.2))
    parts.append(text(ax, oy + 17, "aₓ=3", size=11, color=NEG, anchor="middle"))

    # a_y on axis label
    parts.append(line(ox - 4, ay, ox + 4, ay, color=NEG, sw=1.2))
    parts.append(text(ox - 8, ay + 4, "a_y=2", size=11, color=NEG, anchor="end"))

    # bₓ on axis label
    parts.append(line(bx, oy - 4, bx, oy + 4, color=FIELD, sw=1.2))
    parts.append(text(bx, oy + 30, "bₓ=1", size=11, color=FIELD, anchor="middle"))

    # b_y on axis label
    parts.append(line(ox - 4, by, ox + 4, by, color=FIELD, sw=1.2))
    parts.append(text(ox - 8, by + 4, "b_y=3", size=11, color=FIELD, anchor="end"))

    # Dashed lines for c
    parts.append(line(cx, oy, cx, cy, color=POS, sw=1.0, dash="5 3"))
    parts.append(line(ox, cy, cx, cy, color=POS, sw=1.0, dash="5 3"))

    # Vector a — blue
    parts.append(arrow(ox, oy, ax - 1, ay + 1, color=NEG, sw=2.3))
    tb_a, _, _ = textbox(ox + adx / 2 + 20, oy + ady / 2 - 4, "a=(3,2)", size=12, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1)
    parts.append(tb_a)

    # Vector b — green
    parts.append(arrow(ox, oy, bx, by + 1, color=FIELD, sw=2.3))
    tb_b, _, _ = textbox(ox + bdx / 2 - 42, oy + bdy / 2, "b=(1,3)", size=12, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1)
    parts.append(tb_b)

    # Resultant c — red
    parts.append(arrow(ox, oy, cx - 1, cy + 1, color=POS, sw=2.8))
    tb_c, _, _ = textbox(ox + cdx / 2 + 30, oy + cdy / 2, "c=(4,5)", size=13, color=POS, fill="#fdecea", stroke=POS, sw=1)
    parts.append(tb_c)

    # Dots
    parts.append(circle(ox, oy, 5, fill=INK, stroke=INK, sw=1))
    parts.append(circle(ax, ay, 4, fill=NEG, stroke=NEG, sw=1))
    parts.append(circle(bx, by, 4, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(circle(cx, cy, 5, fill=POS, stroke=POS, sw=1))

    # Formula box
    fb = fitbox(W - 160, H - 90, 155, 56,
                "cₓ = aₓ+bₓ = 3+1 = 4\nc_y = a_y+b_y = 2+3 = 5",
                size=12, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK)
    parts.append(fb)

    render(os.path.join(OUT, "components.svg"), W, H, *parts)


# ── Запуск ────────────────────────────────────────────────────────────────────

fig_head_to_tail()
fig_parallelogram()
fig_components()
print("SVG figures generated in", OUT)
