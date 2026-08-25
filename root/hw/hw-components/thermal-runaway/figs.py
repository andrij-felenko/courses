# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Петля додатного зворотного зв'язку ───────────────────────────────────
def fig_loop():
    W, H = 720, 360
    frags = []
    cx, cy = W / 2, H / 2 + 8
    # чотири вузли по колу
    nodes = [
        (cx,        cy - 120, "Більше тепла\nна кристалі",  POS),
        (cx + 230,  cy,       "Падає VBE,\nросте струм Ic", INK),
        (cx,        cy + 120, "Більша потужність\nP = Ic·Vce", POS),
        (cx - 230,  cy,       "Температура\nпереходу ще вища", POS),
    ]
    boxes = []
    for (x, y, s, col) in nodes:
        b, w, h = textbox(x, y, s, size=14, pad=11,
                          fill="#fdecea" if col is POS else FILL,
                          stroke=col, sw=2.0, color=INK)
        boxes.append((x, y, w, h))
        frags.append(b)

    # стрілки за годинниковою — від краю однієї рамки до краю наступної
    def edge(i, j):
        xi, yi, wi, hi = boxes[i]
        xj, yj, wj, hj = boxes[j]
        import math
        dx, dy = xj - xi, yj - yi
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # вийти за межі рамки-джерела і не дійти до рамки-цілі
        ri = max(wi, hi) / 2 + 6
        rj = max(wj, hj) / 2 + 10
        return (xi + ux * ri, yi + uy * ri, xj - ux * rj, yj - uy * rj)

    for (i, j) in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        x1, y1, x2, y2 = edge(i, j)
        frags.append(arrow(x1, y1, x2, y2, color=POS, sw=2.4))

    frags.append(text(cx, cy + 4, "⟳", size=46, color=POS, bold=True))
    frags.append(text(cx, cy + 40, "сам себе підсилює", size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "feedback-loop.svg"), W, H, *frags,
           title="Петля, що живить сама себе: тепло → струм → ще тепло")


# ── 2. Чому фіксоване зміщення «пливе»: дві кри耗 Ic(Vbe) за різних T ──────
def fig_vbe_shift():
    W, H = 720, 380
    ox, oy = 90, H - 70      # початок осей
    aw, ah = 560, 250        # розміри поля
    frags = []
    # осі
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 26, "VBE  (напруга база–емітер)", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 12, oy - ah, "Ic", size=15, color=INK, anchor="end", bold=True))

    import math
    def expo(shift, x):
        # експонента, зсунута вліво на shift (гарячіша крива «лівіша»)
        return ah * (1 - math.exp(-(x - shift) / 0.16)) if x > shift else 0

    # дві криві: холодна (праворуч) і гаряча (ліворуч)
    def curve(shift, col, dash=None):
        pts = []
        for k in range(0, 101):
            xv = 0.30 + (k / 100.0) * 0.95          # VBE 0.30..1.25 (умовні)
            yv = expo(shift, xv)
            yv = min(yv, ah - 6)
            px = ox + (k / 100.0) * aw
            py = oy - yv
            pts.append("%.1f,%.1f" % (px, py))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>'
                % (" ".join(pts), col, ' stroke-dasharray="7,5"' if dash else ''))

    frags.append(curve(0.55, NEG))            # холодна
    frags.append(curve(0.40, POS))            # гаряча (зсув вліво)

    # фіксована робоча напруга VBE (вертикаль) і дві робочі точки
    xfix = ox + 0.60 * aw
    frags.append(line(xfix, oy, xfix, oy - ah + 4, color=MUTED, sw=1.6, dash="4,4"))
    frags.append(text(xfix, oy + 18, "фіксована VBE", size=12, color=MUTED))

    # точки перетину (приблизно)
    yc = oy - min(expo(0.55, 0.30 + 0.60 * 0.95), ah - 6)
    yh = oy - min(expo(0.40, 0.30 + 0.60 * 0.95), ah - 6)
    frags.append(circle(xfix, yc, 6, fill=NEG, stroke=NEG))
    frags.append(circle(xfix, yh, 6, fill=POS, stroke=POS))
    frags.append(arrow(xfix + 14, yc - 4, xfix + 14, yh + 8, color=POS, sw=2.0))
    frags.append(text(xfix + 22, (yc + yh) / 2, "стрибок Ic", size=12, color=POS, anchor="start"))

    # легенда
    lb, lw, lh = textbox(ox + aw - 120, oy - ah + 34,
                         "холодна  T₁", size=12, pad=7, stroke=NEG, sw=2, color=NEG)
    frags.append(lb)
    lb2, _, _ = textbox(ox + aw - 120, oy - ah + 74,
                        "гаряча  T₂ > T₁", size=12, pad=7, stroke=POS, sw=2, color=POS)
    frags.append(lb2)
    render(os.path.join(IMG, "vbe-shift.svg"), W, H, *frags,
           title="За тієї самої VBE гарячий перехід пропускає більший струм")


# ── 3. Резистор в емітері як гальмо (від'ємний ЗЗ) ──────────────────────────
def fig_emitter_brake():
    W, H = 745, 320
    frags = []
    # ліворуч — без RE (розгін), праворуч — з RE (стабільно)
    midx = W / 2
    frags.append(line(midx, 60, midx, H - 30, color="#d0d0d0", sw=1.5, dash="3,5"))

    # ── ліва панель: голий ланцюг ──
    lx = 40
    frags.append(text(180, 52, "Без RE: ніщо не спиняє петлю", size=14, color=POS, bold=True))
    b, w, h = textbox(180, 110, "Ic росте", size=13, pad=10, stroke=POS, sw=2)
    frags.append(b)
    b2, w2, h2 = textbox(180, 180, "VBE не міняється\n→ Ic росте далі", size=13, pad=10, stroke=POS, sw=2)
    frags.append(b2)
    frags.append(arrow(180, 110 + h / 2 + 4, 180, 180 - h2 / 2 - 4, color=POS, sw=2.4))
    frags.append(arrow(180 + w2 / 2 + 6, 180, 230, 130, color=POS, sw=2.0))
    frags.append(text(180, H - 36, "розгін", size=13, color=POS, italic=True))

    # ── права панель: з RE ──
    rx0 = midx + 40
    frags.append(text(midx + 180, 52, "З RE: струм сам себе тримає", size=14, color=FIELD, bold=True))
    a, aw, ah = textbox(midx + 180, 104, "Ic спробував\nпідрости", size=13, pad=10, stroke=INK, sw=1.8)
    frags.append(a)
    bb, bw, bh = textbox(midx + 180, 176, "падіння на RE\nросте → VBE падає", size=13, pad=10, stroke=FIELD, sw=2)
    frags.append(bb)
    cc, cw, ch = textbox(midx + 180, 250, "Ic вертається\nназад", size=13, pad=10, stroke=FIELD, sw=2)
    frags.append(cc)
    frags.append(arrow(midx + 180, 104 + ah / 2 + 4, midx + 180, 176 - bh / 2 - 4, color=INK, sw=2.0))
    frags.append(arrow(midx + 180, 176 + bh / 2 + 4, midx + 180, 250 - ch / 2 - 4, color=FIELD, sw=2.4))
    # зворотна стрілка-петля (від'ємний ЗЗ)
    frags.append(arrow(midx + 180 + cw / 2 + 6, 250, midx + 180 + aw / 2 + 30, 116, color=FIELD, sw=2.0))
    frags.append(text(midx + 180 + cw / 2 + 70, 185, "тягне\nназад", size=11, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "emitter-brake.svg"), W, H, *frags,
           title="Резистор в емітері перетворює петлю розгону на гальмо")


# ── 4. Сума обертів петлі: M<1 згасає, M≥1 розходиться ──────────────────────
def fig_loop_sum():
    """Кожен оберт петлі додає до температури δTj·Mⁿ. Ліворуч M<1 — стовпчики
    тануть, сума скінченна. Праворуч M≥1 — стовпчики ростуть, сума втікає."""
    W, H = 720, 380
    frags = []
    midx = W / 2
    frags.append(line(midx, 64, midx, H - 24, color="#d0d0d0", sw=1.5, dash="3,5"))

    base = H - 64          # рівень підлоги стовпчиків
    unit = 150.0           # висота першого стовпчика (δTj·M у px) — спільний масштаб
    bw = 26                # ширина стовпчика
    n = 7

    def panel(x0, M, col, fillc, caption, sub, runaway):
        # підпис панелі
        frags.append(text(x0 + 3.5 * (bw + 12), 54, caption, size=14, color=col, bold=True))
        # підлога
        frags.append(line(x0 - 6, base, x0 + n * (bw + 12), base, color=INK, sw=2))
        h = unit
        for k in range(n):
            bx = x0 + k * (bw + 12)
            hk = h
            clipped = False
            if hk > base - 70:           # стовпчик «вибиває» за верх поля
                hk = base - 70
                clipped = True
            frags.append(rect(bx, base - hk, bw, hk, fill=fillc, stroke=col, sw=1.8, rx=3))
            # показник Mⁿ під віссю
            lab = "M" if k == 0 else "M%d" % (k + 1)
            frags.append(text(bx + bw / 2, base + 18, lab, size=11, color=MUTED))
            if clipped:
                frags.append(arrow(bx + bw / 2, base - hk + 6, bx + bw / 2, base - hk - 22, color=col, sw=2.2))
            h = h * M
        # підпис-висновок
        frags.append(text(x0 + 3.5 * (bw + 12), base + 44, sub, size=12.5,
                          color=col, italic=True))
        # сумарна дужка / стрілка
        if runaway:
            frags.append(text(x0 + 3.5 * (bw + 12), 88, "сума → ∞", size=15, color=col, bold=True))
        else:
            frags.append(text(x0 + 3.5 * (bw + 12), 88, "сума скінченна", size=14, color=col, bold=True))

    # ліва панель: M = 0.6 (згасання)
    panel(54, 0.6, NEG, "#eaf0fd",
          "M < 1 : кожен оберт слабший",
          "збурення тане — транзистор живий", runaway=False)
    # права панель: M = 1.25 (розгін)
    panel(midx + 44, 1.25, POS, "#fdecea",
          "M ≥ 1 : кожен оберт сильніший",
          "збурення росте — розгін", runaway=True)

    render(os.path.join(IMG, "loop-sum.svg"), W, H, *frags,
           title="Підсилення петлі M вирішує: затухання чи втеча")


if __name__ == "__main__":
    fig_loop()
    fig_vbe_shift()
    fig_emitter_brake()
    fig_loop_sum()
    print("ok: figures written to", IMG)
