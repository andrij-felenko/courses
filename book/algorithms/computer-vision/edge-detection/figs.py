# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── nms-sectors: 8 секторів напряму + білінійна інтерполяція двох сусідів ──────
# Ідея NMS: піксель лишається, лише якщо його градієнт більший за двох сусідів
# УЗДОВЖ напряму градієнта. Напрям квантують у 4 осі (8 секторів), а точніше —
# інтерполюють значення між двома цілими сусідами по обидва боки.

def fig_nms_sectors():
    W, H = 820, 510
    p = []

    # ── ЛІВО: коло з 8 секторів напряму (по 45°) ──
    cx, cy, R = 210, 250, 150
    p.append(text(cx, 70, "напрям градієнта → 4 осі (8 секторів)", size=12, bold=True))
    # сектори: межі через кожні 22.5°, осі через 0/45/90/135
    for k in range(8):
        a = math.radians(k * 45.0 - 22.5)
        p.append(line(cx, cy, cx + R * math.cos(a), cy - R * math.sin(a),
                      color=MUTED, sw=1, dash="4 4"))
    p.append(circle(cx, cy, R, fill="none", stroke=INK, sw=1.4))
    # 4 осі-напрями (0°, 45°, 90°, 135°) суцільні
    axes = [(0, "0°  ↔"), (45, "45° ⤢"), (90, "90° ↕"), (135, "135°⤡")]
    for deg, lab in axes:
        a = math.radians(deg)
        x2, y2 = cx + R * math.cos(a), cy - R * math.sin(a)
        x1, y1 = cx - R * math.cos(a), cy + R * math.sin(a)
        p.append(line(x1, y1, x2, y2, color=NEG, sw=2.2))
    # підписи осей по колу
    for deg, lab in axes:
        a = math.radians(deg)
        lx, ly = cx + (R + 22) * math.cos(a), cy - (R + 22) * math.sin(a)
        p.append(text(lx, ly + 4, lab, size=10.5, color=NEG, bold=True))
    # приклад вектора градієнта в секторі ~30° (потрапляє в вісь 45°)
    ga = math.radians(30)
    gx2, gy2 = cx + 0.7 * R * math.cos(ga), cy - 0.7 * R * math.sin(ga)
    p.append(arrow(cx, cy, gx2, gy2, color=POS, sw=2.6))
    p.append(text(gx2 + 6, gy2 - 8, "∇ ≈30°", size=10.5, color=POS, bold=True))
    p.append(text(cx, cy + R + 50, "сектор 30° → найближча вісь 45°",
                  size=10, color=MUTED, italic=True))

    # ── ПРАВО: сітка 3×3, інтерполяція двох сусідів уздовж напряму ──
    gx0, gy0 = 470, 150
    cell = 84
    p.append(text(gx0 + 1.5 * cell, gy0 - 24, "інтерполяція двох сусідів",
                  size=12, bold=True))
    vals = [[" ", "p", " "],
            ["q", "C", "r"],
            [" ", "s", " "]]
    for rr in range(3):
        for cc in range(3):
            x = gx0 + cc * cell
            y = gy0 + rr * cell
            mid = (rr == 1 and cc == 1)
            fill = "#fdecea" if mid else FILL
            stroke = POS if mid else LINE
            p.append(rect(x, y, cell, cell, fill=fill, stroke=stroke,
                          sw=2.2 if mid else 1.2, rx=4))
            p.append(text(x + cell / 2, y + cell / 2 + 6, vals[rr][cc],
                          size=18 if mid else 14,
                          color=POS if mid else MUTED, bold=mid))
    C = (gx0 + 1.5 * cell, gy0 + 1.5 * cell)
    # напрям градієнта ~45° через центр: дві точки інтерполяції між сусідами
    a = math.radians(45)
    dx, dy = math.cos(a), -math.sin(a)
    P1 = (C[0] + cell * dx, C[1] + cell * dy)
    P2 = (C[0] - cell * dx, C[1] - cell * dy)
    p.append(line(P2[0], P2[1], P1[0], P1[1], color=NEG, sw=2.4))
    # точки інтерполяції (між цілими сусідами)
    for (px, py), lab in [(P1, "g₁"), (P2, "g₂")]:
        p.append(circle(px, py, 7, fill=FIELD, stroke=BG, sw=1.6))
    p.append(text(P1[0] + 14, P1[1] - 6, "g₁ = lerp(p, r)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(P2[0] - 14, P2[1] + 16, "g₂ = lerp(q, s)", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(text(C[0] + 8, C[1] - cell * 0.62, "напрям ∇", size=10, color=NEG, bold=True, anchor="start"))

    # правило під сіткою
    p.append(fitbox(gx0 - 6, gy0 + 3 * cell + 18, 3 * cell + 12, 64,
                    "лишити C, лише якщо\n|∇C| ≥ g₁  і  |∇C| ≥ g₂\nінакше — занулити",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, bold=True))

    render(os.path.join(OUT, "nms-interp.svg"), W, H, *p,
           title="Придушення немаксимумів: сектори напряму й два сусіди")


# ── kernels-four: чотири ядра Gx поряд + їхній відгук на пряму під 45° ─────────
# Ідея: усі це ядра першої похідної, різниця — у вагах і розмірі. Scharr
# ізотропніший (3-10-3), Roberts найдешевший (2×2, по діагоналі).

def fig_kernels_four():
    W, H = 880, 430
    p = []

    def kbox(x, y, name, rows, sub, hl):
        cell = 30
        n = len(rows[0])
        bw = n * cell
        p.append(text(x + bw / 2, y - 26, name, size=12.5, bold=True, color=hl))
        for rr in range(len(rows)):
            for cc in range(n):
                v = rows[rr][cc]
                cxx = x + cc * cell
                cyy = y + rr * cell
                col = POS if (isinstance(v, (int, float)) and v > 0) else \
                      (NEG if (isinstance(v, (int, float)) and v < 0) else FILL)
                fill = "#fdecea" if col == POS else ("#eaf0fd" if col == NEG else FILL)
                p.append(rect(cxx, cyy, cell, cell, fill=fill, stroke=LINE, sw=1, rx=3))
                p.append(text(cxx + cell / 2, cyy + cell / 2 + 5, str(v),
                              size=12, color=INK))
        p.append(text(x + bw / 2, y + len(rows) * cell + 18, sub,
                      size=9.5, color=MUTED))
        return bw

    ys = 110
    x = 40
    x += kbox(x, ys, "Собель Gx", [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
              "3×3 · ваги 1-2-1", INK) + 56
    x += kbox(x, ys, "Prewitt Gx", [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
              "3×3 · рівна вага", "#7c3aed") + 56
    x += kbox(x, ys, "Scharr Gx", [[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]],
              "3×3 · ваги 3-10-3 (ізотроп.)", FIELD) + 56
    kbox(x, ys, "Roberts", [[1, 0], [0, -1]],
         "2×2 · по діагоналі (найдешевше)", "#b06b00")

    # нижня смуга: відгук на пряму під 45°
    by = ys + 150
    p.append(text(W / 2, by - 6, "відгук на пряму під 45°: чим ізотропніше ядро, "
                  "тим рівніша яскравість уздовж краю",
                  size=10.5, color=MUTED, italic=True))
    # малі панелі-кадри з краєм під 45° та «товщиною» відгуку
    labels = [("Собель", 0.80, INK), ("Prewitt", 0.72, "#7c3aed"),
              ("Scharr", 0.92, FIELD), ("Roberts", 0.55, "#b06b00")]
    pw, ph = 150, 96
    gap = (W - 80 - 4 * pw) / 3
    for i, (lab, strength, col) in enumerate(labels):
        px = 40 + i * (pw + gap)
        py = by + 14
        p.append(rect(px, py, pw, ph, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
        # діагональна смуга-відгук: товщина ~ (1-strength) (менш ізотроп. → нерівніша)
        thick = 5 + (1 - strength) * 10
        x1, y1 = px + 14, py + ph - 14
        x2, y2 = px + pw - 14, py + 14
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#f8fafc" '
                 'stroke-width="%.1f" stroke-linecap="round" opacity="0.92"/>'
                 % (x1, y1, x2, y2, thick))
        p.append(text(px + pw / 2, py + ph + 16, lab, size=10.5, color=col, bold=True))

    render(os.path.join(OUT, "kernels-four.svg"), W, H, *p,
           title="Сімейство ядер першої похідної: Gx поряд")


# ── log-zero: профіль → перша похідна (пік) → друга похідна (нуль-перетин) ─────
# Ідея LoG: межа — там, де ДРУГА похідна перетинає нуль (zero crossing). Це
# точніше за пік першої похідної й дає субпіксельне місце.

def fig_log_zero():
    W, H = 820, 470
    p = []
    L, Rr = 80, W - 60
    midx = (L + Rr) / 2

    def panel(y0, h, title_, color, fn, zero_line=False, mark_edge=False):
        p.append(line(L, y0 + h, Rr, y0 + h, color=MUTED, sw=1))   # вісь x
        base = y0 + h / 2
        p.append(line(L, base, Rr, base, color="#d0d4da", sw=1, dash="3 4"))
        p.append(text(L - 8, y0 + 14, title_, size=11, color=color, bold=True, anchor="end"))
        pts = []
        N = 220
        for i in range(N + 1):
            t = i / N
            x = L + t * (Rr - L)
            v = fn(t)                       # v у [-1, 1]
            yy = base - v * (h / 2 - 8)
            pts.append("%.1f,%.1f" % (x, yy))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), color))
        if mark_edge:
            p.append(line(midx, y0, midx, y0 + h, color=POS, sw=1.6, dash="5 4"))
        return base

    # сходинка з гладким переходом (сигмоїда) — край у центрі
    def smoothstep(t):
        # перехід навколо 0.5, ширина ~0.12
        z = (t - 0.5) / 0.09
        return 2.0 / (1.0 + math.exp(-z)) - 1.0     # від -1 до 1

    def deriv1(t):
        h = 1e-3
        return (smoothstep(t + h) - smoothstep(t - h)) / (2 * h) / 11.0  # унормовано

    def deriv2(t):
        h = 2e-3
        return (smoothstep(t + h) - 2 * smoothstep(t) + smoothstep(t - h)) / (h * h) / 120.0

    ph = 118
    y1 = 60
    panel(y1, ph, "профіль I(x)", NEG, smoothstep, mark_edge=True)
    panel(y1 + ph + 14, ph, "I′(x) — пік", POS, deriv1, mark_edge=True)
    base3 = panel(y1 + 2 * (ph + 14), ph, "I″(x) — нуль-перетин", FIELD, deriv2, mark_edge=True)

    # відмітити zero-crossing у центрі другої похідної
    p.append(circle(midx, base3, 8, fill="none", stroke=POS, sw=2.6))
    p.append(text(midx + 14, base3 - 12, "нуль-перетин = межа", size=10.5,
                  color=POS, bold=True, anchor="start"))
    p.append(text(midx, y1 - 8, "справжня межа", size=10, color=POS, anchor="middle"))

    render(os.path.join(OUT, "log-zero.svg"), W, H, *p,
           title="LoG / Марр–Гілдрет: межа на нуль-перетині другої похідної")


# ── subpixel-parabola: три цілі відліки гребеня → парабола → зсув δ ────────────
# Ідея: гребінь градієнта вузький, але навколо піка значення лягають на параболу.
# Вершина параболи лежить між пікселями — звідси субпіксельне δ = -f'/(2f'').

def fig_subpixel():
    W, H = 800, 430
    p = []
    # осі
    ox, oy = 120, H - 90
    axw, axh = W - 220, H - 170
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))           # x
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))           # y
    p.append(text(ox + axw, oy + 22, "позиція (піксель)", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - axh + 6, "|∇|", size=11, color=MUTED, anchor="end"))

    # три цілі відліки: x=-1,0,+1 (пікселі i-1, i, i+1), значення гребеня
    # підберемо так, щоб вершина була не в цілому: f(-1)=0.62, f(0)=0.95, f(1)=0.78
    fm, f0, fp = 0.62, 0.95, 0.78
    sx = axw / 4.0          # крок між пікселями по x
    def X(k): return ox + (k + 2) * sx
    def Y(v): return oy - v * (axh - 30)
    xs = [-1, 0, 1]
    fs = [fm, f0, fp]
    # парабола через три точки: a*x^2 + b*x + c
    c = f0
    a = (fm + fp) / 2 - f0
    b = (fp - fm) / 2
    # вершина
    delta = -b / (2 * a)                 # зсув від центру (в пікселях)
    vy = a * delta * delta + b * delta + c

    # крива параболи
    pts = []
    k = -1.6
    while k <= 1.6001:
        v = a * k * k + b * k + c
        pts.append("%.1f,%.1f" % (X(k), Y(v)))
        k += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # три цілі відліки
    for xk, fv, lab in zip(xs, fs, ["i−1", "i", "i+1"]):
        p.append(line(X(xk), oy, X(xk), Y(fv), color="#d0d4da", sw=1, dash="3 3"))
        p.append(circle(X(xk), Y(fv), 6, fill=POS, stroke=BG, sw=1.6))
        p.append(text(X(xk), oy + 18, lab, size=10.5, color=INK))
        p.append(text(X(xk), Y(fv) - 12, "%.2f" % fv, size=9.5, color=MUTED))

    # вершина параболи (субпіксельний максимум)
    p.append(line(X(delta), oy, X(delta), Y(vy), color=FIELD, sw=1.8, dash="5 3"))
    p.append(circle(X(delta), Y(vy), 7, fill=FIELD, stroke=BG, sw=1.8))
    p.append(text(X(delta) + 10, Y(vy) - 8,
                  "вершина: зсув δ = %.2f px" % delta,
                  size=11, color=FIELD, bold=True, anchor="start"))

    # формула (нижній правий кут, де крива вже спадає — не накриває вершину)
    p.append(fitbox(W - 350, oy - 70, 320, 56,
                    "δ = −f′ / (2·f″)\n= (f₋ − f₊) / (2·(f₋ − 2f₀ + f₊))",
                    size=12, fill=FILL, stroke=INK, sw=1.3, color=INK, bold=True))

    render(os.path.join(OUT, "subpixel-parabola.svg"), W, H, *p,
           title="Субпіксельна локалізація: парабола через три відліки")


if __name__ == "__main__":
    fig_nms_sectors()
    fig_kernels_four()
    fig_log_zero()
    fig_subpixel()
    print("OK: figures written to", OUT)
