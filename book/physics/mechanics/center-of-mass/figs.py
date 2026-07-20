# -*- coding: utf-8 -*-
"""Фігури до теми «Центр мас».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.6, op=1.0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="%.1f" stroke-linejoin="round"/>' % (p, fill, op, stroke, sw))


# ── Фігура 1: тіло перекидається, а центр мас летить параболою ────────────────
def fig_tumbling():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тіло перекидається безладно — центр мас летить рівною параболою",
                  size=17, bold=True))

    def cm(t):
        return (130 + 560 * t, 150 + 800 * (t - 0.5) ** 2)

    def theta(t):
        return 0.5 + 6.3 * t

    La, Lb = 54.0, 22.0        # хвіст ручки / бік голівки від центра мас

    def tail(t):
        x, y = cm(t); a = theta(t)
        return (x - La * math.cos(a), y - La * math.sin(a))

    def head(t):
        x, y = cm(t); a = theta(t)
        return (x + Lb * math.cos(a), y + Lb * math.sin(a))

    N = 90
    cm_path = [cm(i / N) for i in range(N + 1)]
    tip_path = [tail(i / N) for i in range(N + 1)]

    # шлях кінця ручки — сіра пунктирна хвиляста крива
    f.append(polyline(tip_path, color=MUTED, sw=1.7, dash="2 7"))
    # шлях центра мас — чиста парабола, зелена й товста
    f.append(polyline(cm_path, color=FIELD, sw=3.2))

    # ключ у кількох положеннях
    for t in (0.05, 0.28, 0.5, 0.72, 0.95):
        c = cm(t); tl = tail(t); hd = head(t)
        a = theta(t)
        f.append(line(tl[0], tl[1], hd[0], hd[1], color=INK, sw=4.5))
        # голівка (важкий кінець) — коло + маленька «вилка»
        f.append(circle(hd[0], hd[1], 12, fill="#dfe4ea", stroke=INK, sw=1.6))
        nx, ny = -math.sin(a), math.cos(a)
        jx, jy = math.cos(a), math.sin(a)
        f.append(line(hd[0] + nx * 8 + jx * 6, hd[1] + ny * 8 + jy * 6,
                      hd[0] - nx * 8 + jx * 6, hd[1] - ny * 8 + jy * 6, color=INK, sw=3))
        # центр мас — червона крапка
        f.append(circle(c[0], c[1], 5, fill=POS, stroke=POS, sw=1))

    # легенда (угорі ліворуч, далеко від траєкторії)
    f.append(line(52, 58, 84, 58, color=FIELD, sw=3.2))
    f.append(text(92, 62, "центр мас — рівна парабола", size=13, anchor="start"))
    f.append(line(52, 82, 84, 82, color=MUTED, sw=1.7, dash="2 7"))
    f.append(text(92, 86, "кінець ручки — петляє", size=13, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "tumbling-wrench.svg"), W, H, *f)


# ── Фігура 2: центр мас як зважене середнє двох мас ───────────────────────────
def fig_weighted():
    W, H = 780, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Центр мас — зважене середнє: ближче до більшої маси",
                  size=17, bold=True))

    xL, xR = 200.0, 610.0      # 0 м та 1 м
    yb = 185.0
    span = xR - xL
    xcm = xL + 0.75 * span     # 0.75 м від легкої

    # стрижень
    f.append(line(xL, yb, xR, yb, color=INK, sw=5))
    # маси (площа кружка ~ маса: r ∝ √m)
    f.append(circle(xL, yb, 20, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(xL, yb + 5, "2 кг", size=13, bold=True, color=NEG))
    f.append(circle(xR, yb, 38, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(xR, yb + 6, "6 кг", size=16, bold=True, color=NEG))

    # опора-трикутник під центром мас + червона крапка
    f.append(polygon([(xcm, yb + 6), (xcm - 22, yb + 58), (xcm + 22, yb + 58)],
                     fill="#fdecea", stroke=POS, sw=2))
    f.append(circle(xcm, yb, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(xcm, yb - 20, "центр мас", size=13, bold=True, color=POS))

    # розмірні лінії
    dl = yb + 92
    for a, b, lab in ((xL, xcm, "0.75 м"), (xcm, xR, "0.25 м")):
        f.append(line(a, dl, b, dl, color=MUTED, sw=1.3))
        f.append(line(a, dl - 6, a, dl + 6, color=MUTED, sw=1.3))
        f.append(line(b, dl - 6, b, dl + 6, color=MUTED, sw=1.3))
        f.append(text((a + b) / 2, dl - 9, lab, size=12, color=MUTED))
    # тонкі поводки від мас/цм до розмірної лінії
    for xx in (xL, xcm, xR):
        f.append(line(xx, yb + 60 if xx == xcm else yb + 22, xx, dl - 6,
                      color=MUTED, sw=0.8, dash="3 4"))

    b0, w0, h0 = textbox(W / 2, H - 30,
                         "x_цм = (2·0 + 6·1) / (2 + 6) = 0.75 м    (відстані обернені до мас — 1 : 3)",
                         size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b0)
    return render(os.path.join(IMG, "weighted-average.svg"), W, H, *f)


# ── Фігура 3: центр мас може лежати поза тілом ────────────────────────────────
def fig_cm_outside():
    W, H = 780, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Центр мас може лежати там, де тіла немає",
                  size=17, bold=True))

    # ── ліва панель: кільце ──
    cxL, cyL = 210, 210
    f.append(text(cxL, 64, "кільце", size=14, bold=True, color=MUTED))
    f.append(circle(cxL, cyL, 86, fill="#eef2fb", stroke=INK, sw=2))
    f.append(circle(cxL, cyL, 46, fill=BG, stroke=INK, sw=2))   # дірка
    f.append(circle(cxL, cyL, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(cxL, cyL - 14, "центр мас", size=12, bold=True, color=POS))
    f.append(text(cxL, cyL + 24, "тут порожньо", size=11, color=MUTED))

    # ── права панель: бумеранг ──
    cxR = 560
    f.append(text(cxR, 64, "бумеранг", size=14, bold=True, color=MUTED))
    V = (cxR, 292)             # вершина вигину (унизу)
    L, wdt = 150.0, 26.0
    dL = (-0.46, -0.888); dR = (0.46, -0.888)
    pL = (0.888, -0.46); pR = (0.888, 0.46)

    def arm(V, d, p):
        a = (V[0] + p[0] * wdt / 2, V[1] + p[1] * wdt / 2)
        b = (V[0] - p[0] * wdt / 2, V[1] - p[1] * wdt / 2)
        c = (b[0] + d[0] * L, b[1] + d[1] * L)
        e = (a[0] + d[0] * L, a[1] + d[1] * L)
        return [a, e, c, b]

    f.append(polygon(arm(V, dL, pL), fill="#eef2fb", stroke=INK, sw=2))
    f.append(polygon(arm(V, dR, pR), fill="#eef2fb", stroke=INK, sw=2))
    # центр мас — у роззявленому роті, поза деревом
    cm = (cxR, 208)
    f.append(line(cm[0], cm[1], cm[0], 150, color=MUTED, sw=0.9, dash="3 4"))
    f.append(circle(cm[0], cm[1], 6, fill=POS, stroke=POS, sw=1))
    f.append(text(cxR, 128, "центр мас", size=12, bold=True, color=POS))
    f.append(text(cxR, 145, "поза тілом", size=11, color=MUTED))

    b0, w0, h0 = textbox(W / 2, H - 26,
                         "Центр мас — геометрична точка балансу, а не частинка речовини",
                         size=13, pad=10, fill=FILL, stroke=LINE, sw=1.2, bold=False)
    f.append(b0)
    return render(os.path.join(IMG, "cm-outside-body.svg"), W, H, *f)


# ── Фігура 4 (hist): закон важеля Архімеда ────────────────────────────────────
def fig_lever_law():
    W, H = 820, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Закон важеля: рівновага при відстанях, обернених до ваг",
                  size=17, bold=True))
    fx = 470.0          # опора
    yb = 190.0          # балка
    u = 80.0            # px на «частку» відстані
    xL = fx - 3 * u     # легкий тягар (2) на відстані 3
    xR = fx + 2 * u     # важкий тягар (3) на відстані 2

    # балка
    f.append(line(xL - 34, yb, xR + 34, yb, color=INK, sw=6))
    # опора-трикутник
    f.append(polygon([(fx, yb + 4), (fx - 30, yb + 60), (fx + 30, yb + 60)],
                     fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(fx, yb + 82, "опора", size=13, color=MUTED))

    # тягарі (важчий — більший кружок)
    f.append(circle(xL, yb - 24, 22, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(xL, yb - 19, "2", size=17, bold=True, color=NEG))
    f.append(circle(xR, yb - 32, 30, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(xR, yb - 25, "3", size=21, bold=True, color=NEG))

    # розмірні лінії відстаней (нижче опори, щоб нічого не перетинати)
    dl = yb + 106
    for xx in (xL, xR):
        f.append(line(xx, yb, xx, dl - 6, color=MUTED, sw=0.8, dash="3 4"))
    for a, b, lab in ((xL, fx, "3 частки"), (fx, xR, "2 частки")):
        f.append(line(a, dl, b, dl, color=MUTED, sw=1.3))
        f.append(line(a, dl - 6, a, dl + 6, color=MUTED, sw=1.3))
        f.append(line(b, dl - 6, b, dl + 6, color=MUTED, sw=1.3))
        f.append(text((a + b) / 2, dl - 9, lab, size=12, color=MUTED))

    b0, w0, h0 = textbox(W / 2, H - 30,
                         "тягар · відстань = тягар · відстань   →   2 · 3 = 3 · 2",
                         size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b0)
    return render(os.path.join(IMG, "lever-law.svg"), W, H, *f)


# ── Фігура 5 (hist): центри ваги, що знайшов Архімед ──────────────────────────
def fig_centroids():
    W, H = 880, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Центри ваги, які знайшов Архімед", size=17, bold=True))

    # ── ліва панель: трикутник (медіани → центр 2:1) ──
    f.append(text(235, 78, "трикутник", size=14, bold=True, color=MUTED))
    A = (235, 118); B = (140, 330); C = (345, 330)
    f.append(polygon([A, B, C], fill="#eef2fb", stroke=INK, sw=2))
    mBC = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    mAC = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    mAB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    for v, m in ((A, mBC), (B, mAC), (C, mAB)):
        f.append(line(v[0], v[1], m[0], m[1], color=MUTED, sw=1.3, dash="4 4"))
    G = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)
    f.append(circle(G[0], G[1], 6, fill=POS, stroke=POS, sw=1))
    f.append(text(G[0] + 11, G[1] + 5, "G", size=14, bold=True, color=POS, anchor="start"))

    # ── права панель: сегмент параболи (діаметр у 3:2) ──
    f.append(text(645, 78, "сегмент параболи", size=14, bold=True, color=MUTED))
    cx = 645.0; ay = 350.0; oy = 200.0; hw = 92.0
    Hh = ay - oy
    N = 44
    pts = []
    for i in range(N + 1):
        xx = -hw + 2 * hw * i / N
        yy = (xx * xx) / (hw * hw) * Hh          # 0 у вершині, Hh на краях
        pts.append((cx + xx, ay - yy))
    f.append(polyline(pts, color=INK, sw=2.4))
    # хорда (основа) + діаметр
    f.append(line(cx - hw, oy, cx + hw, oy, color=INK, sw=2.4))
    f.append(text(cx, oy - 14, "хорда (основа)", size=12, color=MUTED))
    f.append(line(cx, ay, cx, oy, color=MUTED, sw=1.3, dash="4 4"))
    # вершина A та основа O
    f.append(circle(cx, ay, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx + 9, ay + 4, "A", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(circle(cx, oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx - 9, oy + 16, "O", size=13, bold=True, color=MUTED, anchor="end"))
    # центр ваги G на 3/5 від вершини (AG:GO = 3:2)
    gy = ay - 0.6 * Hh
    f.append(circle(cx, gy, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(cx - 10, gy + 5, "G", size=14, bold=True, color=POS, anchor="end"))
    # поділки 3 і 2 на діаметрі (праворуч від осі)
    for yy0 in (ay, gy, oy):
        f.append(line(cx - 5, yy0, cx + 5, yy0, color=INK, sw=1.4))
    f.append(text(cx + 16, (ay + gy) / 2 + 4, "3", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(cx + 16, (gy + oy) / 2 + 4, "2", size=13, bold=True, color=INK, anchor="start"))

    # підписи-висновки під панелями
    b1, _, _ = textbox(235, H - 34, "центр ваги ділить кожну медіану 2 : 1",
                       size=13, pad=9, fill=FILL, stroke=LINE, sw=1.2)
    b2, _, _ = textbox(645, H - 34, "AG = 3⁄2 · GO   →   діаметр у 3 : 2",
                       size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b1)
    f.append(b2)
    return render(os.path.join(IMG, "archimedes-centroids.svg"), W, H, *f)


# ── Фігура 6 (math): внутрішні сили гасяться попарно (виведення теореми) ──────
def fig_internal_cancel():
    W, H = 860, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Внутрішні сили гасяться попарно — лишаються зовнішні",
                  size=17, bold=True))

    # легенда (угорі ліворуч)
    f.append(line(52, 60, 92, 60, color=NEG, sw=2.6))
    f.append(text(100, 64, "внутрішні fᵢⱼ — рівні й протилежні (у сумі 0)",
                  size=13, color=NEG, anchor="start"))
    f.append(line(52, 84, 92, 84, color=POS, sw=2.6))
    f.append(text(100, 88, "зовнішні (тяжіння) — лишаються", size=13, color=POS, anchor="start"))

    P = {1: (230.0, 240.0), 2: (620.0, 205.0), 3: (430.0, 370.0)}
    r = 24.0

    def uvec(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        return dx / L, dy / L

    # внутрішні пари вздовж кожного ребра (обидві стрілки — всередину, рівні)
    edges = [(1, 2, True), (2, 3, False), (1, 3, False)]
    alen = 58.0
    for i, j, lab in edges:
        a, b = P[i], P[j]
        ux, uy = uvec(a, b)
        nx, ny = -uy, ux
        sa = (a[0] + ux * (r + 8), a[1] + uy * (r + 8))
        ea = (sa[0] + ux * alen, sa[1] + uy * alen)
        sb = (b[0] - ux * (r + 8), b[1] - uy * (r + 8))
        eb = (sb[0] - ux * alen, sb[1] - uy * alen)
        f.append(arrow(sa[0], sa[1], ea[0], ea[1], color=NEG, sw=2.4))
        f.append(arrow(sb[0], sb[1], eb[0], eb[1], color=NEG, sw=2.4))
        if lab:
            ma = ((sa[0] + ea[0]) / 2, (sa[1] + ea[1]) / 2)
            mb = ((sb[0] + eb[0]) / 2, (sb[1] + eb[1]) / 2)
            f.append(text(ma[0] + nx * 20, ma[1] + ny * 20 - 2, "f₁₂",
                          size=14, color=NEG, bold=True))
            f.append(text(mb[0] + nx * 20, mb[1] + ny * 20 - 2, "f₂₁",
                          size=14, color=NEG, bold=True))

    # зовнішні сили (тяжіння) — червоні стрілки вниз від кожної частинки
    for k in (1, 2, 3):
        c = P[k]
        f.append(arrow(c[0], c[1] + r + 4, c[0], c[1] + r + 50, color=POS, sw=2.6))

    # частинки поверх стрілок
    for k in (1, 2, 3):
        c = P[k]
        f.append(circle(c[0], c[1], r, fill="#eef2fb", stroke=INK, sw=2))
        f.append(text(c[0], c[1] + 5, "m%d" % k, size=15, bold=True))

    b0, w0, h0 = textbox(W / 2, H - 40,
                         "кожна пара  fᵢⱼ + fⱼᵢ = 0    →    Σ внутрішніх = 0    →    F_зовн = M·a_цм",
                         size=15, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b0)
    return render(os.path.join(IMG, "internal-cancel.svg"), W, H, *f)


# ── Фігура 7 (math): у системі центра мас повний імпульс — нуль ───────────────
def fig_cm_frame():
    W, H = 900, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ті самі імпульси у двох системах відліку",
                  size=17, bold=True))

    def tiptail(O, vecs, names, closing=False, cname=None):
        out = []
        pts = [O]
        for v in vecs:
            pts.append((pts[-1][0] + v[0], pts[-1][1] + v[1]))
        # центроїд унікальних вершин — щоб класти підписи НАЗОВНІ полігона
        closed = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1
        uniq = pts[:-1] if closed else pts
        cxc = sum(p[0] for p in uniq) / len(uniq)
        cyc = sum(p[1] for p in uniq) / len(uniq)

        def put(a, b, name, off, color=INK):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            px, py = -dy / L, dx / L                     # нормаль до відрізка
            if (mx - cxc) * px + (my - cyc) * py < 0:    # бік, протилежний до центра
                px, py = -px, -py
            return text(mx + px * off, my + py * off + 4, name, size=14, bold=True, color=color)

        for k, v in enumerate(vecs):
            a, b = pts[k], pts[k + 1]
            out.append(arrow(a[0], a[1], b[0], b[1], color=INK, sw=2.4))
            out.append(put(a, b, names[k], 22))
        if closing:
            a, b = O, pts[-1]
            out.append(arrow(a[0], a[1], b[0], b[1], color=FIELD, sw=3.4))
            out.append(put(a, b, cname, 34, color=FIELD))
        out.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
        return out

    # ── ліва панель: лабораторна система (полігон НЕ замикається) ──
    f.append(text(240, 92, "Лабораторна система", size=15, bold=True))
    lab = [(70.0, -80.0), (130.0, 0.0), (70.0, 80.0)]        # Σ = (270, 0) = M·v_цм
    f += tiptail((105.0, 290.0), lab, ["p₁", "p₂", "p₃"],
                 closing=True, cname="P = M·v_цм")
    f.append(text(240, 452, "Σ pᵢ = M·v_цм ≠ 0", size=14, bold=True, color=FIELD))

    # роздільник між панелями
    f.append(line(475, 110, 475, 414, color=MUTED, sw=1.0, dash="4 6"))

    # ── права панель: система центра мас (полігон замикається → сума нуль) ──
    f.append(text(680, 92, "Система центра мас", size=15, bold=True))
    cm = [(120.0, 0.0), (-60.0, 104.0), (-60.0, -104.0)]     # Σ = (0, 0)
    f += tiptail((620.0, 215.0), cm, ["p₁′", "p₂′", "p₃′"])
    f.append(text(680, 452, "Σ pᵢ′ = 0", size=14, bold=True, color=FIELD))

    return render(os.path.join(IMG, "cm-frame-momentum.svg"), W, H, *f)


# ── Фігура 8 (proj): пастка — центроїд многокутника ≠ середнє вершин ──────────
def fig_centroid_trap():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Та сама фігура: середнє вершин ≠ справжній центроїд",
                  size=17, bold=True))

    sc = 92.0
    ox, oy = 150.0, 330.0

    def M(x, y):
        return (ox + x * sc, oy - y * sc)

    # прямокутник 4×2 із ЗАЙВОЮ вершиною (2,0) на нижньому боці (форми не змінює)
    verts = [(0, 0), (2, 0), (4, 0), (4, 2), (0, 2)]
    f.append(polygon([M(*v) for v in verts], fill="#eef2fb", stroke=INK, sw=2))
    for v in verts:
        p = M(*v)
        f.append(circle(p[0], p[1], 4.5, fill=INK, stroke=INK, sw=1))

    # зайва вершина (2,0) — синім кільцем
    ex = M(2, 0)
    f.append(circle(ex[0], ex[1], 7.5, fill=BG, stroke=NEG, sw=2.4))
    f.append(text(ex[0], ex[1] + 26, "зайва вершина (2,0)", size=12, color=NEG))
    f.append(text(ex[0], ex[1] + 42, "форми не міняє", size=11, color=MUTED))

    # справжній центроїд (2,1) — червоний, підпис ЛІВОРУЧ
    ce = M(2, 1)
    va = M(2, 0.8)
    f.append(line(ce[0], ce[1], va[0], va[1], color=MUTED, sw=1.2, dash="3 3"))
    f.append(circle(ce[0], ce[1], 7, fill="#fdecea", stroke=POS, sw=2.6))
    f.append(text(ce[0] - 14, ce[1] - 4, "центроїд площі (2, 1)",
                  size=13, bold=True, color=POS, anchor="end"))
    # середнє вершин (2, 0.8) — синій, підпис ПРАВОРУЧ
    f.append(circle(va[0], va[1], 7, fill="#eaf0fd", stroke=NEG, sw=2.6))
    f.append(text(va[0] + 14, va[1] + 6, "середнє вершин (2, 0.8)",
                  size=13, bold=True, color=NEG, anchor="start"))

    b0, w0, h0 = textbox(W / 2, H - 26,
                         "Додали вершину на боці — форма та сама, а середнє вершин з'їхало вниз на 0.2",
                         size=13, pad=10, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b0)
    return render(os.path.join(IMG, "centroid-trap.svg"), W, H, *f)


# ── Фігура 9 (proj): віяло трикутників зі знаковою площею ─────────────────────
def fig_triangle_fan():
    W, H = 780, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Віяло трикутників від нуля O: знак площі узгоджує все сам",
                  size=16, bold=True))

    sc = 52.0
    ox, oy = 90.0, 405.0

    def M(x, y):
        return (ox + x * sc, oy - y * sc)

    P = [(3.0, 1.2), (6.2, 2.0), (6.4, 5.2), (3.6, 6.4), (1.6, 3.6)]
    O = (0.6, 0.6)                      # нуль ПОЗА многокутником
    n = len(P)

    # трикутники віяла: колір за знаком площі (світові координати)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        cross = (a[0] - O[0]) * (b[1] - O[1]) - (b[0] - O[0]) * (a[1] - O[1])
        col = FIELD if cross > 1e-9 else POS
        f.append(polygon([M(*O), M(*a), M(*b)], fill=col, stroke=col, sw=1.0, op=0.15))

    # промені від нуля до вершин
    po = M(*O)
    for a in P:
        pa = M(*a)
        f.append(line(po[0], po[1], pa[0], pa[1], color=MUTED, sw=0.8, dash="2 4"))

    # сам многокутник — жирний контур поверх
    f.append(polygon([M(*p) for p in P], fill="none", stroke=INK, sw=2.6))

    # нуль O
    f.append(circle(po[0], po[1], 6, fill=BG, stroke=INK, sw=2))
    f.append(text(po[0] + 12, po[1] + 5, "нуль O — хоч де", size=12, bold=True, anchor="start"))

    # справжній центроїд (реальна формула) — червона крапка всередині
    a2 = cx = cy = 0.0
    for i in range(n):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % n]
        cr = x0 * y1 - x1 * y0
        a2 += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    C = (cx / (3 * a2), cy / (3 * a2))
    pc = M(*C)
    f.append(circle(pc[0], pc[1], 6.5, fill="#fdecea", stroke=POS, sw=2.6))
    f.append(text(pc[0] + 12, pc[1] - 4, "центроїд", size=13, bold=True, color=POS, anchor="start"))

    # легенда (праворуч угорі)
    lx = 560
    f.append(rect(lx, 66, 200, 76, fill="#fbfbfc", stroke=LINE, sw=1.1, rx=8))
    f.append(rect(lx + 14, 82, 22, 15, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    f.append(text(lx + 46, 95, "+ площа (додається)", size=12, anchor="start"))
    f.append(rect(lx + 14, 110, 22, 15, fill=POS, stroke=POS, sw=1, rx=3))
    f.append(text(lx + 46, 123, "− площа (віднімається)", size=12, anchor="start"))

    return render(os.path.join(IMG, "triangle-fan.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_tumbling(), fig_weighted(), fig_cm_outside(),
          fig_lever_law(), fig_centroids(),
          fig_internal_cancel(), fig_cm_frame(),
          fig_centroid_trap(), fig_triangle_fan()]
    print("written:")
    for p in ps:
        print("  ", p)
