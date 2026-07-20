# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: струминка звужується — A·v = const ─────────────────────────────
def fig_streamtube():
    W, H = 820, 440
    body = []
    cy = 214
    x0, x1 = 150, 660
    h1, h2 = 94, 36                      # півширина зліва / справа

    def half(x):
        t = (x - x0) / (x1 - x0)
        return h1 + (h2 - h1) * t

    # силует струминки (світла заливка) + штрихові «невидимі стінки»
    n = 44
    top, bot = [], []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        h = half(x)
        top.append((x, cy - h))
        bot.append((x, cy + h))
    d = "M%.1f %.1f " % top[0]
    d += " ".join("L%.1f %.1f" % p for p in top[1:])
    d += " " + " ".join("L%.1f %.1f" % p for p in reversed(bot))
    d += " Z"
    body.append('<path d="%s" fill="%s" stroke="none"/>' % (d, "#eaf0fd"))
    for i in range(n):
        body.append(line(top[i][0], top[i][1], top[i + 1][0], top[i + 1][1], color=NEG, sw=1.6, dash="6 4"))
        body.append(line(bot[i][0], bot[i][1], bot[i + 1][0], bot[i + 1][1], color=NEG, sw=1.6, dash="6 4"))

    # лінії течії, що згущуються
    for k in (-2, -1, 0, 1, 2):
        f = k / 2.5
        body.append(line(x0, cy + f * h1, x1, cy + f * h2, color=NEG, sw=1.3))

    # стрілки швидкості: коротка в широкому, довга у вузькому
    body.append(arrow(196, cy, 196 + 34, cy, color=POS, sw=3.2))
    body.append(arrow(556, cy, 556 + 84, cy, color=POS, sw=3.2))

    # підписи над трубою (у вільній зоні)
    body.append(text(x0 + 26, cy - h1 - 18, "широкий переріз A₁", size=13.5, color=INK, bold=True, anchor="start"))
    body.append(text(x0 + 26, cy - h1 - 2, "потік повільний — v₁", size=12, color=MUTED, anchor="start"))
    body.append(text(x1 - 20, cy - h2 - 34, "вузький A₂", size=13.5, color=INK, bold=True, anchor="end"))
    body.append(text(x1 - 20, cy - h2 - 18, "потік швидкий — v₂", size=12, color=MUTED, anchor="end"))

    # примітка про згущення ліній під трубою
    body.append(text(W / 2, cy + h1 + 24, "лінії течії згущуються — там потік швидший", size=12.5, color=MUTED))

    # підсумкова формула
    body.append(fitbox(W / 2 - 195, 380, 390, 46,
                       "A₁ · v₁ = A₂ · v₂   —   вужче означає швидше",
                       size=15, bold=True, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, "streamtube.svg"), W, H, *body,
           title="Нерозривність: крізь вужчий переріз — та сама витрата")


# ── Фігура 2: контрольний об'єм — облік маси ──────────────────────────────────
def fig_control_volume():
    W, H = 800, 400
    body = []
    cx, cy = 400, 196
    bw, bh = 250, 150
    bx, by = cx - bw / 2, cy - bh / 2

    # штриховий контрольний об'єм (уявна межа)
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
                'fill="#eef7f0" stroke="%s" stroke-width="2" stroke-dasharray="7 5"/>'
                % (bx, by, bw, bh, FIELD))
    body.append(text(cx, cy - 4, "контрольний об'єм", size=14.5, bold=True))
    body.append(text(cx, cy + 18, "маса всередині", size=12.5, color=MUTED))

    # приток (ліворуч)
    body.append(arrow(bx - 128, cy, bx - 6, cy, color=NEG, sw=3.2))
    body.append(text(bx - 128, cy - 18, "втікає", size=13.5, color=NEG, bold=True, anchor="start"))
    body.append(text(bx - 128, cy + 26, "ρ₁ · A₁ · v₁", size=13.5, color=NEG, anchor="start"))

    # витік (праворуч)
    body.append(arrow(bx + bw + 6, cy, bx + bw + 128, cy, color=POS, sw=3.2))
    body.append(text(bx + bw + 128, cy - 18, "витікає", size=13.5, color=POS, bold=True, anchor="end"))
    body.append(text(bx + bw + 128, cy + 26, "ρ₂ · A₂ · v₂", size=13.5, color=POS, anchor="end"))

    # підсумок унизу
    body.append(fitbox(W / 2 - 320, 320, 640, 52,
                       "накопичення = приток − витік      •      усталена течія → приток = витік",
                       size=14.5, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "control-volume.svg"), W, H, *body,
           title="Звідки береться закон: облік маси в контрольному об'ємі")


# ── Фігура 3: нестислива проти стисливої течії ────────────────────────────────
def _duct(body, cy, x0, x1, hL, hR, fill):
    n = 40
    top, bot = [], []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        h = hL + (hR - hL) * i / n
        top.append((x, cy - h))
        bot.append((x, cy + h))
    d = "M%.1f %.1f " % top[0]
    d += " ".join("L%.1f %.1f" % p for p in top[1:])
    d += " " + " ".join("L%.1f %.1f" % p for p in reversed(bot))
    d += " Z"
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (d, fill, LINE))

    def half(x):
        t = (x - x0) / (x1 - x0)
        return hL + (hR - hL) * t
    return half


def _dots(body, half, cy, x0, x1, dense_left):
    """Розкидати крапки-«молекули» в протоці; dense_left=True → рідшають праворуч."""
    xs = []
    x = x0 + 18
    mid = (x0 + x1) / 2
    while x < x1 - 10:
        xs.append(x)
        if dense_left:
            x += 20 if x < mid else 42
        else:
            x += 26
    for x in xs:
        h = half(x)
        y = cy - h + 14
        while y < cy + h - 6:
            body.append(circle(x, y, 2.2, fill=NEG, stroke=NEG, sw=0.6))
            y += 18


def fig_compressible():
    W, H = 820, 560
    body = []
    x0, x1 = 210, 650
    hL, hR = 66, 26

    # ── верхня панель: нестислива (вода) ──
    cyA = 150
    half = _duct(body, cyA, x0, x1, hL, hR, "#eaf0fd")
    _dots(body, half, cyA, x0, x1, dense_left=False)
    body.append(arrow(x0 + 34, cyA, x0 + 34 + 24, cyA, color=POS, sw=3.0))
    body.append(arrow(x1 - 96, cyA, x1 - 96 + 66, cyA, color=POS, sw=3.0))
    body.append(text(W / 2, 66, "Нестислива течія (вода): густина стала", size=15, bold=True))
    body.append(text(x0 - 12, cyA + 5, "ρ", size=15, color=NEG, bold=True, anchor="end"))
    body.append(text(x1 + 14, cyA + 5, "ρ", size=15, color=NEG, bold=True, anchor="start"))
    body.append(text(x0 + 46, cyA - hL - 8, "повільно", size=11.5, color=MUTED))
    body.append(text(x1 - 62, cyA - hR - 8, "швидко", size=11.5, color=MUTED))
    body.append(fitbox(x1 + 34, cyA - 22, 132, 44, "A · v = const",
                       size=14, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD))

    # ── нижня панель: стислива (газ) ──
    cyB = 400
    half = _duct(body, cyB, x0, x1, hL, hR, "#f0eefb")
    _dots(body, half, cyB, x0, x1, dense_left=True)
    body.append(arrow(x0 + 34, cyB, x0 + 34 + 24, cyB, color=POS, sw=3.0))
    body.append(arrow(x1 - 96, cyB, x1 - 96 + 66, cyB, color=POS, sw=3.0))
    body.append(text(W / 2, 300, "Стислива течія (газ біля швидкості звуку): густина падає", size=15, bold=True))
    body.append(text(x0 - 12, cyB + 5, "ρ₁ велика", size=12.5, color=INK, bold=True, anchor="end"))
    body.append(text(x1 + 14, cyB + 5, "ρ₂ мала", size=12.5, color=INK, bold=True, anchor="start"))
    body.append(text(x0 + 46, cyB - hL - 8, "повільно", size=11.5, color=MUTED))
    body.append(text(x1 - 62, cyB - hR - 8, "швидко", size=11.5, color=MUTED))
    body.append(fitbox(x0 - 4, 486, 404, 46,
                       "ρ · A · v = const,   але   A · v ≠ const",
                       size=14, bold=True, fill="#fdecea", stroke=POS))
    body.append(text(W / 2, 550, "крапки — молекули газу: праворуч рідше, отже густина менша",
                     size=12, color=MUTED))

    render(os.path.join(OUT, "compressible.svg"), W, H, *body,
           title="Спрощення A·v = const — лише для сталої густини")


# ── Фігура 4: як народжувався закон нерозривності (часова вісь) ────────────────
def fig_timeline():
    W, H = 900, 560
    body = []
    ax = 108                          # вертикальна вісь часу
    y_top, y_bot = 70, 520

    # вісь: суцільна там, де є поступ; штрихова на «провалі»
    gap_a, gap_b = 120, 214
    body.append(line(ax, y_top, ax, gap_a, color=INK, sw=2.6))
    body.append(line(ax, gap_a, ax, gap_b, color=MUTED, sw=2.2, dash="3 7"))
    body.append(line(ax, gap_b, ax, y_bot, color=INK, sw=2.6))
    body.append(arrow(ax, y_bot, ax, y_bot + 26, color=INK, sw=2.6))
    body.append(text(ax, y_bot + 42, "час", size=12, color=MUTED))

    def node(cy, title, desc, accent=INK):
        body.append(circle(ax, cy, 7.5, fill=accent, stroke=accent, sw=2))
        body.append(text(ax + 24, cy - 4, title, size=14, color=INK, bold=True, anchor="start"))
        body.append(text(ax + 24, cy + 16, desc, size=12.5, color=MUTED, anchor="start"))

    node(98, "Герон Александрійський · бл. 62 р. н.е.",
         "У «Діоптрі»: витрата — це площа, помножена на швидкість, а не сам отвір.", NEG)

    # смуга «провалу»
    body.append(text(ax + 24, 158, "≈ 15 століть — думку загублено;", size=12.5, color=MUTED,
                     italic=True, anchor="start"))
    body.append(text(ax + 24, 176, "річку далі міряють шириною отвору", size=12.5, color=MUTED,
                     italic=True, anchor="start"))

    node(240, "Леонардо да Вінчі · бл. 1508 (Кодекс Лестера)",
         "Скільки води входить, стільки й виходить; де вужче — там швидше. Словами.", FIELD)
    node(360, "Бенедетто Кастеллі · 1628, Рим",
         "Точний закон A · v = const: площа й швидкість обернено пропорційні.", POS)
    node(475, "Леонард Ойлер · 1757",
         "Диференціальне рівняння нерозривності: ∂ρ/∂t + ∇·(ρv) = 0.", INK)

    render(os.path.join(OUT, "history-timeline.svg"), W, H, *body,
           title="Як народжувався закон нерозривності")


# ── Фігура 5: мережа-дерево, розв'язана нерозривністю (proj) ───────────────────
def fig_flow_tree():
    import math as _m
    W, H = 900, 560
    body = []

    P  = (85, 275); J1 = (300, 275)
    C1 = (540, 150); J2 = (540, 400)
    C2 = (795, 300); C3 = (795, 470)

    def flow_edge(a, ra, b, rb, q, dmm):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = _m.hypot(dx, dy); ux, uy = dx / L, dy / L
        x1, y1 = a[0] + ux * ra, a[1] + uy * ra
        x2, y2 = b[0] - ux * rb, b[1] - uy * rb
        sw = 2.2 + 7.0 * (abs(q) / 20.0)          # товщина стрілки ∝ витраті
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        bw, bh = 54, 21                            # половина розмірів підпису-рамки
        # лінія обходить рамку підпису: розриваємо її на два відрізки ПОЗА рамкою,
        # а не ховаємо під непрозорим боксом — інакше геометрично лінія «протикає» напис
        d = min(bw / abs(ux) if ux else 1e9, bh / abs(uy) if uy else 1e9) + 5
        gx1, gy1 = mx - ux * d, my - uy * d
        gx2, gy2 = mx + ux * d, my + uy * d
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                    'stroke-width="%.1f"/>' % (x1, y1, gx1, gy1, NEG, sw))
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                    'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (gx2, gy2, x2, y2, NEG, sw))
        body.append(fitbox(mx - bw, my - bh, bw * 2, bh * 2,
                           "%g л/хв\n⌀ %.1f мм" % (q, dmm),
                           size=13, bold=True, fill="#eef4fd", stroke=NEG, color=INK))

    flow_edge(P, 27, J1, 20, 20, 16.8)
    flow_edge(J1, 20, C1, 23, 10, 11.9)
    flow_edge(J1, 20, J2, 20, 10, 11.9)
    flow_edge(J2, 20, C2, 23, 6, 9.2)
    flow_edge(J2, 20, C3, 23, 4, 7.5)

    def node(c, r, label, fill, stroke, sw=2.0):
        body.append(circle(c[0], c[1], r, fill=fill, stroke=stroke, sw=sw))
        body.append(text(c[0], c[1] + 5, label, size=14, bold=True))

    node(P, 27, "P", "#eaf6ec", FIELD, 2.6)
    body.append(text(P[0], P[1] - 40, "джерело +20", size=12.5, color=FIELD, bold=True))
    node(J1, 20, "J1", FILL, LINE)
    node(J2, 20, "J2", FILL, LINE)
    node(C1, 23, "C1", "#eaf0fd", NEG)
    node(C2, 23, "C2", "#eaf0fd", NEG)
    node(C3, 23, "C3", "#eaf0fd", NEG)
    body.append(text(C1[0] + 32, C1[1] + 5, "−10", size=13, color=NEG, bold=True, anchor="start"))
    body.append(text(C2[0] + 32, C2[1] + 5, "−6", size=13, color=NEG, bold=True, anchor="start"))
    body.append(text(C3[0] + 32, C3[1] + 5, "−4", size=13, color=NEG, bold=True, anchor="start"))

    body.append(fitbox(W / 2 - 305, 512, 610, 40,
        "у кожному вузлі приток = витік → витрату кожної гілки задає сама нерозривність",
        size=13.5, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "flow-tree.svg"), W, H, *body,
           title="Мережа-дерево: баланс вузлів задає всі витрати")


# ── Фігура 6: дерево визначене, петля — ні (межа з методом тисків) ─────────────
def fig_tree_vs_loop():
    import math as _m
    W, H = 900, 380
    body = []
    body.append(line(W / 2, 56, W / 2, 344, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: дерево — визначено ──
    body.append(text(232, 50, "Дерево — витрати визначені", size=15, bold=True, color=FIELD))
    S = (95, 195); A = (250, 195); C = (405, 120); Bn = (405, 270)

    def edge2(a, ra, b, rb, sw, label, lx, ly):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = _m.hypot(dx, dy); ux, uy = dx / L, dy / L
        x1, y1 = a[0] + ux * ra, a[1] + uy * ra
        x2, y2 = b[0] - ux * rb, b[1] - uy * rb
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                    'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, INK, sw))
        body.append(text(lx, ly, label, size=13.5, bold=True, color=INK))

    body.append(arrow(S[0] - 50, S[1], S[0] - 20, S[1], color=FIELD, sw=2.6))
    body.append(text(S[0] - 54, S[1] - 12, "10", size=12.5, color=FIELD, bold=True, anchor="end"))
    edge2(S, 18, A, 18, 5.5, "10", 172, 182)
    edge2(A, 18, C, 18, 4.0, "6", 322, 148)
    edge2(A, 18, Bn, 18, 3.4, "4", 322, 240)
    for c, l in ((S, "S"), (A, "A"), (C, "C"), (Bn, "B")):
        body.append(circle(c[0], c[1], 18, fill="#eaf6ec", stroke=FIELD, sw=2))
        body.append(text(c[0], c[1] + 5, l, size=13, bold=True))
    body.append(text(232, 336, "один шлях до кожного вузла — розподіл однозначний",
                     size=12, color=MUTED))

    # ── права панель: петля — недовизначено ──
    body.append(text(680, 50, "Петля — недовизначено", size=15, bold=True, color=POS))
    S2 = (575, 195); T2 = (815, 195); mx = (S2[0] + T2[0]) / 2
    body.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="3.4" marker-end="url(#arrow)"/>'
                % (S2[0] + 16, S2[1] - 7, mx, 80, T2[0] - 15, T2[1] - 11, INK))
    body.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="3.4" marker-end="url(#arrow)"/>'
                % (S2[0] + 16, S2[1] + 7, mx, 310, T2[0] - 15, T2[1] + 11, INK))
    body.append(text(mx, 96, "q = ?", size=13.5, bold=True, color=POS))
    body.append(text(mx, 296, "10 − q = ?", size=13.5, bold=True, color=POS))
    body.append(text(mx, 202, "?", size=30, bold=True, color=POS))
    body.append(arrow(S2[0] - 50, S2[1], S2[0] - 20, S2[1], color=FIELD, sw=2.6))
    body.append(text(S2[0] - 54, S2[1] - 12, "10", size=12.5, color=FIELD, bold=True, anchor="end"))
    body.append(arrow(T2[0] + 20, T2[1], T2[0] + 50, T2[1], color=POS, sw=2.6))
    body.append(text(T2[0] + 54, T2[1] - 12, "10", size=12.5, color=POS, bold=True, anchor="start"))
    for c, l in ((S2, "S"), (T2, "T")):
        body.append(circle(c[0], c[1], 18, fill="#fdecea", stroke=POS, sw=2))
        body.append(text(c[0], c[1] + 5, l, size=13, bold=True))
    body.append(text(680, 336, "нерозривність дає лиш q + (10−q) = 10 — розподіл вирішує тиск/опір",
                     size=12, color=MUTED))

    render(os.path.join(OUT, "tree-vs-loop.svg"), W, H, *body,
           title="Чому нерозривність визначає дерево, але не петлю")


# ── Фігура 7: коробочка з потоками крізь грані — виведення дивергенції (math) ──
def fig_flux_box():
    W, H = 880, 560
    body = []
    # передня грань паралелепіпеда
    FTL, FTR = (250, 235), (450, 235)
    FBL, FBR = (250, 380), (450, 380)
    dep = (92, -66)                       # вектор «углиб» (вісь z)
    BTL = (FTL[0] + dep[0], FTL[1] + dep[1]); BTR = (FTR[0] + dep[0], FTR[1] + dep[1])
    BBL = (FBL[0] + dep[0], FBL[1] + dep[1]); BBR = (FBR[0] + dep[0], FBR[1] + dep[1])

    def poly(pts, fill, stroke=LINE, sw=1.8):
        s = " ".join("%.1f,%.1f" % p for p in pts)
        return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (s, fill, stroke, sw)

    # приховані ребра — штрихом
    for a, b in ((BBL, BBR), (BBL, BTL), (BBL, FBL)):
        body.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.2, dash="4 5"))
    # видимі грані (права, верхня, передня — передня зверху)
    body.append(poly([FTR, BTR, BBR, FBR], "#dbe6fb"))
    body.append(poly([FTL, FTR, BTR, BTL], "#f3f7fe"))
    body.append(poly([FTL, FTR, FBR, FBL], "#eaf0fd"))

    # розміри ребер
    body.append(text(350, 399, "dx", size=12.5, color=INK))
    body.append(text(240, 352, "dy", size=12.5, color=INK, anchor="end"))
    body.append(text(311, 200, "dz", size=12.5, color=INK, anchor="start"))

    # потік маси вздовж x: втікає (ліворуч) — витікає (праворуч)
    body.append(arrow(150, 308, 248, 308, color=NEG, sw=3.2))
    body.append(text(199, 270, "втікає", size=12.5, color=NEG, bold=True))
    body.append(text(199, 289, "ρv_x(x)", size=12.5, color=NEG))
    body.append(arrow(544, 308, 662, 308, color=POS, sw=3.2))
    body.append(text(603, 270, "витікає", size=12.5, color=POS, bold=True))
    body.append(text(603, 289, "ρv_x(x+dx)", size=12.5, color=POS))

    # ключ осей (угорі ліворуч)
    ox, oy = 112, 150
    body.append(arrow(ox, oy, ox + 48, oy, color=INK, sw=1.8))
    body.append(text(ox + 58, oy + 4, "x", size=12.5, color=INK))
    body.append(arrow(ox, oy, ox, oy - 46, color=INK, sw=1.8))
    body.append(text(ox - 4, oy - 52, "y", size=12.5, color=INK))
    body.append(arrow(ox, oy, ox + 30, oy - 22, color=INK, sw=1.8))
    body.append(text(ox + 40, oy - 24, "z", size=12.5, color=INK))
    body.append(text(ox + 26, oy + 26, "осі координат", size=10.5, color=MUTED))

    # висновок
    body.append(text(W / 2, 432, "крізь грані y і z — так само, як крізь x",
                     size=12, color=MUTED, italic=True))
    body.append(fitbox(160, 450, 560, 66,
                       "чистий витік = ∇·(ρv) · dV\n"
                       "∇·(ρv) = ∂(ρv_x)/∂x + ∂(ρv_y)/∂y + ∂(ρv_z)/∂z",
                       size=14, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "flux-box.svg"), W, H, *body,
           title="Коробочка з шістьма гранями: витік маси = дивергенція")


if __name__ == "__main__":
    fig_streamtube()
    fig_control_volume()
    fig_compressible()
    fig_timeline()
    fig_flow_tree()
    fig_tree_vs_loop()
    fig_flux_box()
    print("figs done")
