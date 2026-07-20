# -*- coding: utf-8 -*-
"""Фігури до теми «Імпульс».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def poly(points, fill=FILL, stroke='none', sw=0.0):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


# ── Фігура 1: імпульс — вектор m·v; важке-повільне = легке-швидке ──────────────
def fig_momentum_vector():
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Імпульс p = m·v: різні маса й швидкість — той самий запас руху",
                  size=16, bold=True))

    xbox = 90                 # ліва межа тіла
    xstart = 250              # звідки ростуть стрілки v і p
    pL = 150                  # довжина стрілки p (ОДНАКОВА в обох рядах)

    def row(cy, is_ball, mlabel, vlen, vlabel, plabel):
        # тіло
        if is_ball:
            f.append(circle(xbox + 30, cy, 24, fill="#eef2fb", stroke=INK, sw=2))
            f.append(text(xbox + 30, cy + 6, "m", size=18, bold=True, color=INK))
        else:
            bw, bh = 96, 66
            f.append(rect(xbox, cy - bh / 2, bw, bh, fill="#eef2fb", stroke=INK, sw=2, rx=7))
            f.append(text(xbox + bw / 2, cy + 6, "m", size=20, bold=True, color=INK))
        f.append(text(xbox + 30, cy + 48, mlabel, size=13, color=MUTED))
        # швидкість v — над лінією стрілок, довжина ∝ швидкості
        vy = cy - 30
        f.append(arrow(xstart, vy, xstart + vlen, vy, color=FIELD, sw=3.2))
        f.append(text(xstart + vlen + 12, vy - 6, vlabel, size=14, bold=True, color=FIELD, anchor="start"))
        # імпульс p — нижче, довжина ОДНАКОВА
        py = cy + 22
        f.append(arrow(xstart, py, xstart + pL, py, color=NEG, sw=3.6))
        f.append(text(xstart + pL + 12, py + 6, plabel, size=14, bold=True, color=NEG, anchor="start"))

    row(150, False, "важке, повільне", 42, "v = 2 м/с", "p = 12 кг·м/с")
    row(300, True, "легке, швидке", 176, "v = 12 м/с", "p = 12 кг·м/с")

    b, w, h = textbox(W / 2, H - 34,
                      "6 кг · 2 м/с  =  1 кг · 12 м/с  =  12 кг·м/с   —   однаково важко спинити",
                      size=13, pad=11, fill="#eaf0fd", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "momentum-vector.svg"), W, H, *f)


# ── Фігура 2: збереження імпульсу в ударі (до / після) ────────────────────────
def fig_collision_conservation():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Пружний удар на гладкій рейці: сумарний імпульс не міняється",
                  size=16, bold=True))

    divx = 440
    f.append(line(divx, 70, divx, 360, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(225, 88, "до удару", size=14, bold=True, color=MUTED))
    f.append(text(655, 88, "після удару", size=14, bold=True, color=MUTED))

    def cart(cx, cy, label, vlen, vshow, sub, pcol):
        bw, bh = 74, 50
        f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eef2fb", stroke=INK, sw=2, rx=6))
        f.append(circle(cx - bw / 2 + 16, cy + bh / 2, 8, fill="#ffffff", stroke=INK, sw=1.6))
        f.append(circle(cx + bw / 2 - 16, cy + bh / 2, 8, fill="#ffffff", stroke=INK, sw=1.6))
        f.append(text(cx, cy + 4, label, size=14, bold=True, color=INK))
        if vlen > 0:
            f.append(arrow(cx + bw / 2 + 4, cy - bh / 2 - 14, cx + bw / 2 + 4 + vlen,
                           cy - bh / 2 - 14, color=FIELD, sw=3.0))
        f.append(text(cx, cy - bh / 2 - 26, vshow, size=12, bold=True, color=FIELD))
        f.append(text(cx, cy + bh / 2 + 30, sub, size=13, bold=True, color=pcol))

    gy = 210
    # до: A (2 кг, v=3, p=6) наздоганяє B (1 кг, спокій)
    cart(150, gy, "A · 2 кг", 60, "v = 3", "p = 6", NEG)
    cart(330, gy, "B · 1 кг", 0, "v = 0", "p = 0", MUTED)
    b0, _, _ = textbox(285, 330, "Σp = 6 кг·м/с", size=14, pad=9,
                       fill="#eaf0fd", stroke=NEG, sw=1.2, bold=True)
    f.append(b0)

    # після: A сповільнилась (v=1, p=2), B помчала (v=4, p=4)
    cart(555, gy, "A · 2 кг", 24, "v = 1", "p = 2", NEG)
    cart(725, gy, "B · 1 кг", 78, "v = 4", "p = 4", NEG)
    b1, _, _ = textbox(645, 330, "Σp = 2 + 4 = 6 кг·м/с", size=14, pad=9,
                       fill="#eaf0fd", stroke=NEG, sw=1.2, bold=True)
    f.append(b1)

    b, w, h = textbox(W / 2, H - 32,
                      "p_до = p_після = 6 кг·м/с     удар лише перекладає рух з тіла на тіло",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "collision-conservation.svg"), W, H, *f)


# ── Фігура 3: пружний проти непружного — імпульс завжди, енергія не завжди ─────
def fig_elastic_inelastic():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Імпульс зберігається завжди; кінетична енергія — лише в пружному",
                  size=16, bold=True))

    colw = 400
    lx, rx = 30, 450
    ptop, ph = 56, 320
    f.append(rect(lx, ptop, colw, ph, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(rect(rx, ptop, colw, ph, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(text(lx + colw / 2, ptop + 30, "Пружний удар", size=15, bold=True, color=FIELD))
    f.append(text(rx + colw / 2, ptop + 30, "Непружний удар", size=15, bold=True, color=POS))

    def scene(ox, elastic):
        cxL, cxR = ox + 120, ox + 280
        yb = ptop + 96     # ряд «до»
        ya = ptop + 190    # ряд «після»
        f.append(text(ox + colw / 2, yb - 30, "до", size=12, color=MUTED))
        # до: дві кулі назустріч
        f.append(circle(cxL, yb, 20, fill="#ffffff", stroke=INK, sw=2))
        f.append(circle(cxR, yb, 20, fill="#ffffff", stroke=INK, sw=2))
        f.append(arrow(cxL + 24, yb, cxL + 60, yb, color=NEG, sw=3.0))
        f.append(arrow(cxR - 24, yb, cxR - 60, yb, color=NEG, sw=3.0))
        # після
        f.append(text(ox + colw / 2, ya - 34, "після", size=12, color=MUTED))
        if elastic:
            f.append(circle(cxL, ya, 20, fill="#ffffff", stroke=INK, sw=2))
            f.append(circle(cxR, ya, 20, fill="#ffffff", stroke=INK, sw=2))
            f.append(arrow(cxL - 24, ya, cxL - 60, ya, color=NEG, sw=3.0))
            f.append(arrow(cxR + 24, ya, cxR + 60, ya, color=NEG, sw=3.0))
            f.append(text(ox + colw / 2, ya + 52, "тіла розлітаються", size=12, color=MUTED))
        else:
            f.append(rect(ox + colw / 2 - 30, ya - 20, 60, 40, fill="#f1d9d4", stroke=INK, sw=2, rx=8))
            f.append(arrow(ox + colw / 2 + 34, ya, ox + colw / 2 + 68, ya, color=NEG, sw=3.0))
            f.append(text(ox + colw / 2, ya + 52, "злиплися й їдуть разом", size=12, color=MUTED))

    scene(lx, True)
    scene(rx, False)

    # статус-рядки під колонками
    b1, _, _ = textbox(lx + colw / 2, ptop + ph + 44, ["імпульс зберігається ✓", "енергія зберігається ✓"],
                       size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b1)
    b2, _, _ = textbox(rx + colw / 2, ptop + ph + 44, ["імпульс зберігається ✓", "частина енергії → тепло ✗"],
                       size=13, pad=9, fill="#fdf0ee", stroke=POS, sw=1.3, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "elastic-inelastic.svg"), W, H, *f)


# ── Фігура 4: розліт зі спокою — вектори-імпульси складаються нулем ────────────
def fig_recoil_explosion():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Розліт зі спокою: сума імпульсів уламків = 0",
                  size=16, bold=True))

    divx = 470
    f.append(line(divx, 70, divx, 402, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(230, 90, "у просторі — розліт навсібіч", size=13, bold=True, color=MUTED))
    f.append(text(680, 90, "ті самі вектори кінець-у-кінець", size=13, bold=True, color=MUTED))

    labs = ["p₁", "p₂", "p₃"]

    def outlabel(px, py, cx, cy, lab, off=17):
        """Підпис назовні від центроїда (cx,cy): не лягає на чужі лінії."""
        dx, dy = px - cx, py - cy
        d = math.hypot(dx, dy) or 1.0
        lx, ly = px + dx / d * off, py + dy / d * off
        f.append(text(lx, ly + 4, lab, size=15, bold=True, color=NEG,
                      anchor="start" if dx >= 0 else "end"))

    # ── ліва сцена: спільна точка, три імпульси врізнобіч ──
    C = (230, 255)
    P = [(120, -78), (-150, 24), (30, 54)]     # сума = (0,0)
    f.append(text(C[0], C[1] - 62, "спокій: p = 0", size=12, bold=True, color=POS))
    for (dx, dy), lab in zip(P, labs):
        tx, ty = C[0] + dx, C[1] + dy
        f.append(arrow(C[0], C[1], tx, ty, color=NEG, sw=3.2))
        outlabel(tx, ty, C[0], C[1], lab)      # назовні від спільної точки
    f.append(circle(C[0], C[1], 9, fill="#fdecea", stroke=POS, sw=2))

    # ── права сцена: голова-до-хвоста, замкнений трикутник ──
    scale = 1.35
    Ps = [(dx * scale, dy * scale) for dx, dy in P]
    S = (620, 300)
    pt = [S]
    for dx, dy in Ps:
        pt.append((pt[-1][0] + dx, pt[-1][1] + dy))
    gx = sum(p[0] for p in pt[:3]) / 3.0       # центроїд трикутника
    gy = sum(p[1] for p in pt[:3]) / 3.0
    for i in range(3):
        a, b_ = pt[i], pt[i + 1]
        f.append(arrow(a[0], a[1], b_[0], b_[1], color=NEG, sw=3.0))
        mx, my = (a[0] + b_[0]) / 2, (a[1] + b_[1]) / 2
        outlabel(mx, my, gx, gy, labs[i], off=20)   # підпис назовні ребра
    f.append(circle(S[0], S[1], 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(S[0] - 4, S[1] + 24, "старт = фініш", size=12, bold=True, color=FIELD, anchor="middle"))

    b, w, h = textbox(W / 2, H - 30,
                      "p₁ + p₂ + p₃ = 0     трикутник замикається — збереження по кожній осі",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "recoil-explosion.svg"), W, H, *f)


# ── Фігура 5 (hist): народження поняття — часова смуга 1644–1743 ──────────────
def fig_hist_timeline():
    W, H = 1060, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Народження «кількості руху»: сто років уточнень",
                  size=17, bold=True))

    axy = 285
    f.append(arrow(60, axy, W - 46, axy, color=MUTED, sw=2.4))
    f.append(text(W - 46, axy - 14, "час", size=13, italic=True, color=MUTED, anchor="end"))

    xs = [130, 284, 438, 592, 746, 900]
    events = [
        (["1644 · Декарт", "«кількість руху»", "= розмір × швидкість", "скаляр, зберігається"], "above", POS),
        (["1656 · Гюйґенс", "правила удару:", "напрям вирішує"], "below", FIELD),
        (["1668–69 · Лондон", "Валліс · Рен · Гюйґенс", "закон удару доведено"], "above", FIELD),
        (["1686 · Ляйбніц", "«жива сила» mv²", "проти mv"], "below", INK),
        (["1687 · Ньютон", "«Начала»: сила —", "зміна кількості руху"], "above", NEG),
        (["1743 · Д'Аламбер", "суперечку знято —", "правдиві обидві"], "below", FIELD),
    ]
    bw, bh = 232, 100
    for x, (lines, side, col) in zip(xs, events):
        if side == "above":
            by = 150
            f.append(line(x, axy - 7, x, by + bh / 2, color=MUTED, sw=1.4, dash="4 4"))
        else:
            by = 420
            f.append(line(x, axy + 7, x, by - bh / 2, color=MUTED, sw=1.4, dash="4 4"))
        f.append(fitbox(x - bw / 2, by - bh / 2, bw, bh, lines, size=13, pad=10,
                        fill="#f7f9fc", stroke=col, sw=1.7, bold=True, color=INK))
        f.append(circle(x, axy, 7, fill=col, stroke=BG, sw=2))

    b, w, h = textbox(W / 2, H - 30,
                      "Від скалярної здогадки до векторного закону: кожен крок додавав те, чого бракувало попередньому",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── Фігура 6 (hist): те саме зіткнення — скаляр Декарта проти вектора ─────────
def fig_hist_scalar_vector():
    W, H = 900, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Та сама зустрічна пара — двома очима на «кількість руху»",
                  size=16, bold=True))

    colw = 400
    lx, rx = 30, 470
    ptop, ph = 56, 300
    f.append(rect(lx, ptop, colw, ph, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(rect(rx, ptop, colw, ph, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(lx + colw / 2, ptop + 28, "Декарт: рух — це число", size=15, bold=True, color=POS))
    f.append(text(rx + colw / 2, ptop + 28, "Гюйґенс і Ньютон: рух — вектор", size=15, bold=True, color=FIELD))

    def pair(ox, signed):
        cx = ox + colw / 2
        cy = ptop + 135
        cL, cR = cx - 80, cx + 80
        f.append(circle(cL, cy, 22, fill="#ffffff", stroke=INK, sw=2))
        f.append(circle(cR, cy, 22, fill="#ffffff", stroke=INK, sw=2))
        f.append(text(cL, cy + 5, "m", size=15, bold=True))
        f.append(text(cR, cy + 5, "m", size=15, bold=True))
        ay = cy - 46
        if signed:
            f.append(arrow(cL - 22, ay, cL + 22, ay, color=POS, sw=3.2))
            f.append(text(cL, ay - 11, "+m·v", size=13, bold=True, color=POS))
            f.append(arrow(cR + 22, ay, cR - 22, ay, color=NEG, sw=3.2))
            f.append(text(cR, ay - 11, "−m·v", size=13, bold=True, color=NEG))
            b, _, _ = textbox(cx, ptop + 242, ["(+m·v) + (−m·v) = 0", "напрям враховано — центр мас стоїть"],
                              size=13, pad=10, fill="#ffffff", stroke=FIELD, sw=1.4, bold=True, color=INK)
        else:
            f.append(arrow(cL - 22, ay, cL + 22, ay, color=MUTED, sw=3.2))
            f.append(text(cL, ay - 11, "m·v", size=13, bold=True, color=MUTED))
            f.append(arrow(cR + 22, ay, cR - 22, ay, color=MUTED, sw=3.2))
            f.append(text(cR, ay - 11, "m·v", size=13, bold=True, color=MUTED))
            b, _, _ = textbox(cx, ptop + 242, ["|m·v| + |m·v| = 2 m·v", "напрям відкинуто — правила хиблять"],
                              size=13, pad=10, fill="#ffffff", stroke=POS, sw=1.4, bold=True, color=INK)
        f.append(b)

    pair(lx, False)
    pair(rx, True)

    b, w, h = textbox(W / 2, H - 30,
                      "Як число «руху» — вдвічі більше за нуль; як вектор — рівно нуль. Цю різницю в напрямі й проґавив Декарт.",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "hist-scalar-vector.svg"), W, H, *f)


# ── Фігура 7 (math): імпульс сили J = ∫F dt = Δp — це площа під F(t) ──────────
def fig_impulse_area():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Імпульс сили J = ∫F dt = Δp — площа під кривою «сила–час»",
                  size=16, bold=True))

    baseY, topY = 352, 100

    def hump(cx, hw, peakH):
        return [(cx - hw, baseY),
                (cx - 0.60 * hw, baseY - 0.32 * peakH),
                (cx - 0.28 * hw, baseY - 0.86 * peakH),
                (cx, baseY - peakH),
                (cx + 0.28 * hw, baseY - 0.86 * peakH),
                (cx + 0.60 * hw, baseY - 0.32 * peakH),
                (cx + hw, baseY)]

    def panel(ox, axisW, cx, hw, peakH, favH, title, sub, favlab, dtlab):
        # осі
        f.append(arrow(ox, baseY, ox, topY, color=MUTED, sw=2.0))
        f.append(arrow(ox, baseY, ox + axisW, baseY, color=MUTED, sw=2.0))
        f.append(text(ox - 8, topY + 2, "F", size=14, italic=True, color=MUTED, anchor="end"))
        f.append(text(ox + axisW, baseY + 22, "t", size=14, italic=True, color=MUTED, anchor="end"))
        # горб = F(t) із заливкою
        f.append(poly(hump(cx, hw, peakH), fill="#eaf0fd", stroke=NEG, sw=2.0))
        f.append(text(cx, baseY - 0.44 * peakH, "площа", size=12, bold=True, color=NEG))
        f.append(text(cx, baseY - 0.44 * peakH + 16, "J = Δp", size=12, bold=True, color=NEG))
        # середня сила — пунктирна горизонталь
        fy = baseY - favH
        f.append(line(ox, fy, cx + hw + 8, fy, color=POS, sw=1.6, dash="6 5"))
        f.append(text(cx + hw + 12, fy + 4, favlab, size=12, bold=True, color=POS, anchor="start"))
        # проміжок Δt під горбом
        f.append(line(cx - hw, baseY + 12, cx + hw, baseY + 12, color=INK, sw=1.4))
        f.append(line(cx - hw, baseY + 8, cx - hw, baseY + 16, color=INK, sw=1.4))
        f.append(line(cx + hw, baseY + 8, cx + hw, baseY + 16, color=INK, sw=1.4))
        f.append(text(cx, baseY + 32, dtlab, size=12, bold=True, color=INK))
        # заголовок панелі
        f.append(text(cx, topY - 24, title, size=14, bold=True, color=INK))
        f.append(text(cx, topY - 8, sub, size=12, color=MUTED))

    panel(85, 340, 210, 58, 200, 118, "твердий удар",
          "велика сила, короткий час", "F_сер велика", "малий Δt")
    panel(500, 350, 660, 128, 92, 54, "м'який удар (зминання)",
          "мала сила, довгий час", "F_сер мала", "великий Δt")

    b, w, h = textbox(W / 2, H - 30,
                      "Однакова площа → однаковий Δp; сила (висота) й час (ширина) міняються в парі",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "impulse-area.svg"), W, H, *f)


# ── Фігура 8 (math): три граничні пружні удари з тих самих формул ─────────────
def fig_elastic_cases():
    W, H = 880, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Пружний удар: три граничні випадки з тієї самої пари формул",
                  size=16, bold=True))

    divx = 445
    f.append(line(divx, 66, divx, 475, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(235, 90, "до удару", size=14, bold=True, color=MUTED))
    f.append(text(660, 90, "після удару", size=14, bold=True, color=MUTED))

    def body(cx, cy, r, lab):
        f.append(circle(cx, cy, r, fill="#eef2fb", stroke=INK, sw=2))
        f.append(text(cx, cy + 5, lab, size=13, bold=True, color=INK))

    def vel(cx, cy, r, length, rightward):
        y = cy - r - 15
        if rightward:
            f.append(arrow(cx + r + 4, y, cx + r + 4 + length, y, color=FIELD, sw=3.0))
        else:
            f.append(arrow(cx - r - 4, y, cx - r - 4 - length, y, color=FIELD, sw=3.0))

    def rowlabel(cy, s):
        f.append(text(235, cy - 58, s, size=12, bold=True, color=MUTED))

    def outcome(cy, s):
        f.append(text(660, cy + 56, s, size=13, bold=True, color=INK))

    # Рядок 1: рівні маси — обмін швидкостями
    cy = 160
    rowlabel(cy, "рівні маси   m = m")
    body(175, cy, 20, "m"); vel(175, cy, 20, 44, True)
    body(300, cy, 20, "m")
    body(590, cy, 20, "m")
    body(720, cy, 20, "m"); vel(720, cy, 20, 44, True)
    outcome(cy, "тіла обмінялися швидкостями")

    # Рядок 2: важке б'є легке — легке ~вдвічі швидше
    cy = 290
    rowlabel(cy, "важке б'є легке   M ≫ m")
    body(175, cy, 26, "M"); vel(175, cy, 26, 44, True)
    body(308, cy, 13, "m")
    body(585, cy, 26, "M"); vel(585, cy, 26, 40, True)
    body(720, cy, 13, "m"); vel(720, cy, 13, 84, True)
    outcome(cy, "легке зривається ~вдвічі швидше")

    # Рядок 3: легке б'є важке — відскакує назад
    cy = 415
    rowlabel(cy, "легке б'є важке   m ≪ M")
    body(175, cy, 13, "m"); vel(175, cy, 13, 44, True)
    body(305, cy, 26, "M")
    body(600, cy, 13, "m"); vel(600, cy, 13, 42, False)
    body(725, cy, 26, "M")
    outcome(cy, "легке відскакує назад")

    b, w, h = textbox(W / 2, H - 30,
                      "усі три — та сама пара формул v₁′, v₂′; змінюються лише маси",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "elastic-cases.svg"), W, H, *f)


# ── Фігура 9 (math): той самий удар — лабораторія проти системи центра мас ────
def fig_cm_trick():
    W, H = 880, 510
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий пружний удар: лабораторія проти системи центра мас",
                  size=16, bold=True))

    def body(cx, cy, r, lab):
        f.append(circle(cx, cy, r, fill="#eef2fb", stroke=INK, sw=2))
        f.append(text(cx, cy + 5, lab, size=12, bold=True, color=INK))

    def vel(cx, cy, r, length, rightward, val):
        y = cy - r - 16
        if rightward:
            f.append(arrow(cx + r + 4, y, cx + r + 4 + length, y, color=FIELD, sw=3.0))
            f.append(text(cx + r + 4 + length / 2, y - 8, val, size=12, bold=True, color=FIELD))
        else:
            f.append(arrow(cx - r - 4, y, cx - r - 4 - length, y, color=FIELD, sw=3.0))
            f.append(text(cx - r - 4 - length / 2, y - 8, val, size=12, bold=True, color=FIELD))

    def panel(ptop, title):
        f.append(rect(30, ptop, W - 60, 190, fill=BG, stroke=MUTED, sw=1.3, rx=10))
        f.append(text(48, ptop + 24, title, size=14, bold=True, color=INK, anchor="start"))
        f.append(line(445, ptop + 42, 445, ptop + 176, color=MUTED, sw=1.1, dash="5 6"))
        f.append(text(235, ptop + 42, "до", size=12, bold=True, color=MUTED))
        f.append(text(660, ptop + 42, "після", size=12, bold=True, color=MUTED))

    # ── лабораторна система ──
    pt = 58
    panel(pt, "лабораторна система")
    cyl = pt + 122
    body(175, cyl, 24, "2"); vel(175, cyl, 24, 46, True, "v₁ = 3")
    body(300, cyl, 16, "1")
    f.append(text(300, cyl - 34, "v₂ = 0", size=12, bold=True, color=MUTED))
    body(585, cyl, 24, "2"); vel(585, cyl, 24, 20, True, "v₁′ = 1")
    body(715, cyl, 16, "1"); vel(715, cyl, 16, 76, True, "v₂′ = 4")

    # ── система центра мас ──
    pc = 268
    panel(pc, "система центра мас   (V = 2 м/с)")
    cyc = pc + 122
    body(175, cyc, 24, "2"); vel(175, cyc, 24, 22, True, "w₁ = 1")
    body(300, cyc, 16, "1"); vel(300, cyc, 16, 46, False, "w₂ = −2")
    body(585, cyc, 24, "2"); vel(585, cyc, 24, 22, False, "−1")
    body(715, cyc, 16, "1"); vel(715, cyc, 16, 46, True, "+2")
    f.append(text(660, cyc + 46, "обидві просто обертаються", size=12, bold=True, color=FIELD))

    b, w, h = textbox(W / 2, H - 28,
                      "у СЦМ пружний удар = зміна знаку швидкостей; назад у лабораторію — додати V",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "cm-frame-trick.svg"), W, H, *f)


# ── Фігура 10 (proj): чотири такти кадру, а Σp у центрі стоїть ─────────────────
def fig_sim_loop():
    W, H = 940, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Один кадр симулятора: чотири такти по колу, а Σp у центрі стоїть",
                  size=16, bold=True))

    bw, bh = 258, 84
    cx, cy = W / 2, 285
    TL = (cx - 215, cy - 96)
    TR = (cx + 215, cy - 96)
    BR = (cx + 215, cy + 96)
    BL = (cx - 215, cy + 96)

    def box(center, lines, col):
        x = center[0] - bw / 2
        y = center[1] - bh / 2
        f.append(fitbox(x, y, bw, bh, lines, size=13, pad=11,
                        fill="#f7f9fc", stroke=col, sw=1.8, bold=True, color=INK))

    box(TL, ["1 · Пролетіти крок Δt", "x += v·Δt — вільний рух"], NEG)
    box(TR, ["2 · Знайти дотик", "хто кого торкнувся"], FIELD)
    box(BR, ["3 · Розв'язати удар", "імпульс + e → нові v"], POS)
    box(BL, ["4 · Звірити Σp", "має бути той самий"], NEG)

    # стрілки по зовнішньому кільцю 1→2→3→4→1
    f.append(arrow(TL[0] + bw / 2 + 8, TL[1], TR[0] - bw / 2 - 8, TR[1], color=MUTED, sw=2.6))
    f.append(arrow(TR[0], TR[1] + bh / 2 + 8, BR[0], BR[1] - bh / 2 - 8, color=MUTED, sw=2.6))
    f.append(arrow(BR[0] - bw / 2 - 8, BR[1], BL[0] + bw / 2 + 8, BL[1], color=MUTED, sw=2.6))
    f.append(arrow(BL[0], BL[1] - bh / 2 - 8, TL[0], TL[1] + bh / 2 + 8, color=MUTED, sw=2.6))

    cb, _, _ = textbox(cx, cy, ["Σp = const", "внутрішні сили не міняють"],
                       size=14, pad=13, fill="#eef6ef", stroke=FIELD, sw=1.9, bold=True, color=INK)
    f.append(cb)

    b, w, h = textbox(W / 2, H - 30,
                      "Кадр лише перекладає рух між тілами — не додає й не забирає його з системи",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "sim-loop.svg"), W, H, *f)


# ── Фігура 11 (proj): тунелювання проти подієвого кроку ───────────────────────
def fig_tunneling():
    W, H = 960, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Тонка стіна й швидке тіло: фіксований крок промахується, подієвий — ні",
                  size=15, bold=True))

    wallx = 545
    x0, x1 = 155, 835

    # ── верхня панель: наївний фіксований крок ──
    f.append(text(W / 2, 78, "Наївний крок: за один Δt тіло перестрибує стіну — перекриття ніхто не бачить",
                  size=13, bold=True, color=POS))
    ty = 185
    f.append(line(80, ty, 880, ty, color=MUTED, sw=2.0))
    f.append(rect(wallx - 5, ty - 46, 10, 92, fill="#f1d9d4", stroke=INK, sw=2, rx=2))
    f.append(text(wallx, ty - 58, "стіна", size=12, bold=True, color=INK))
    f.append(text((x0 + x1) / 2, ty - 22, "стрибок  v·Δt  >  товщина стіни", size=12, bold=True, color=POS))
    f.append(arrow(x0 + 22, ty, x1 - 22, ty, color=POS, sw=2.6))
    f.append(circle(x0, ty, 17, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(x0, ty + 42, "t = n", size=12, bold=True, color=NEG))
    f.append(circle(x1, ty, 17, fill="#ffffff", stroke=MUTED, sw=2))
    f.append(text(x1, ty + 42, "t = n+1", size=12, bold=True, color=MUTED))

    # роздільник панелей
    f.append(line(60, 320, W - 60, 320, color=MUTED, sw=1.0, dash="4 6"))

    # ── нижня панель: подієвий крок ──
    f.append(text(W / 2, 368, "Подієвий крок: рахуємо мить дотику t* і спиняємо світ рівно на ній",
                  size=13, bold=True, color=FIELD))
    by = 470
    f.append(line(80, by, 880, by, color=MUTED, sw=2.0))
    f.append(rect(wallx - 5, by - 46, 10, 92, fill="#f1d9d4", stroke=INK, sw=2, rx=2))
    f.append(text(wallx, by - 58, "стіна", size=12, bold=True, color=INK))
    f.append(text((x0 + wallx) / 2 - 30, by - 22, "адванс до t*", size=12, bold=True, color=FIELD))
    f.append(arrow(x0 + 22, by, wallx - 26, by, color=FIELD, sw=2.8))
    f.append(circle(x0, by, 17, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(x0, by + 42, "t = n", size=12, bold=True, color=NEG))
    f.append(circle(wallx - 23, by, 17, fill="#eef6ef", stroke=FIELD, sw=2.4))
    f.append(text(wallx - 23, by - 30, "t*", size=13, bold=True, color=FIELD))
    f.append(arrow(wallx - 46, by + 28, wallx - 210, by + 28, color=NEG, sw=2.4))
    f.append(text(wallx - 128, by + 48, "розв'язали удар — відскок", size=12, bold=True, color=NEG))

    return render(os.path.join(IMG, "tunneling.svg"), W, H, *f)


# ── Фігура 12 (proj): Σp стоїть, кінетична енергія осідає сходинками ───────────
def fig_momentum_oracle():
    W, H = 960, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Свідок правди — Σp: імпульс не ворухнувся, енергія осідає щоудару",
                  size=16, bold=True))

    x0, x1 = 135, 855
    ybase = 400
    f.append(arrow(x0 - 22, ybase, x1 + 26, ybase, color=MUTED, sw=2.2))
    f.append(text(x1 + 22, ybase + 24, "кадри →", size=13, italic=True, color=MUTED, anchor="end"))

    events = [305, 485, 665]
    for ex in events:
        f.append(line(ex, 92, ex, ybase, color=MUTED, sw=1.2, dash="4 5"))
        f.append(text(ex, ybase + 24, "удар", size=11, color=MUTED))

    # Σp — рівна лінія вгорі
    py = 128
    f.append(line(x0, py, x1, py, color=FIELD, sw=3.4))
    f.append(text(x0, py - 14, "Σp — стоїть намертво (машинна точність)",
                  size=13, bold=True, color=FIELD, anchor="start"))

    # кінетична енергія — спадні сходинки (менше значення = більший y)
    levels = [182, 236, 280, 314]
    xs = [x0, events[0], events[1], events[2], x1]
    for i in range(4):
        f.append(line(xs[i], levels[i], xs[i + 1], levels[i], color=POS, sw=3.0))
        if i < 3:
            f.append(line(xs[i + 1], levels[i], xs[i + 1], levels[i + 1], color=POS, sw=2.4, dash="3 3"))
            my = (levels[i] + levels[i + 1]) / 2
            f.append(text(xs[i + 1] + 12, my + 4, "−ΔКЕ → тепло", size=10, color=POS, anchor="start"))
    f.append(text(x0, levels[0] - 14, "кінетична енергія", size=13, bold=True, color=POS, anchor="start"))

    b, w, h = textbox(W / 2, H - 34,
                      ["Непружний удар щоразу з'їдає трохи КЕ — тому баг енергією не зловиш.",
                       "Σp текти НЕ має права: ним і перевіряють рушій кадр за кадром."],
                      size=13, pad=12, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True, color=INK)
    f.append(b)
    return render(os.path.join(IMG, "momentum-oracle.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_momentum_vector(), fig_collision_conservation(),
          fig_elastic_inelastic(), fig_recoil_explosion(),
          fig_hist_timeline(), fig_hist_scalar_vector(),
          fig_impulse_area(), fig_elastic_cases(), fig_cm_trick(),
          fig_sim_loop(), fig_tunneling(), fig_momentum_oracle()]
    print("written:")
    for p in ps:
        print("  ", p)
