# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GRN = FIELD     # вціліле / краще
RED = POS       # петля-межа / гірше
BLU = NEG       # холодне / жорстке
GREY = "#c2c8d0"


def redmarker():
    return ('<defs><marker id="arrowRED" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
            '<marker id="arrowGRN" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % (RED, GRN))


def dbl_arrow(x1, y, x2, color=INK, sw=2.0):
    """Двобічна розмірна стрілка по горизонталі."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
            % (x1, y, x2, y, color, sw))


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── 1. Анатомія декодера: BMU → ACSU → SMU + петля ACS ────────────────────────

def fig_pipeline():
    W, H = 1180, 470
    p = [redmarker()]

    cy = 262
    bw, bh = 210, 128
    cx = {"BMU": 258, "ACSU": 590, "SMU": 922}

    # вхід
    p.append(text(96, cy - 24, "м'які відліки", size=13, color=MUTED))
    p.append(text(96, cy - 6, "r₀ r₁ … з демодулятора", size=12.5, color=MUTED))
    p.append(arrow(70, cy + 22, cx["BMU"] - bw / 2 - 4, cy + 22, sw=2.4))

    # три блоки
    p.append(fitbox(cx["BMU"] - bw / 2, cy - bh / 2, bw, bh,
                    "Блок метрик гілок\n(BMU)\n\nдля кожного ребра ґратки —\nвідстань прийнятого\nдо мітки ребра",
                    size=14, bold=False, fill="#eef2f7", stroke=INK, sw=2.0, pad=12))
    p.append(fitbox(cx["ACSU"] - bw / 2, cy - bh / 2, bw, bh,
                    "Додати-порівняти-\nвибрати (ACSU)\n\nоновити метрику стану,\nлишити один\nвцілілий шлях",
                    size=14, bold=False, fill="#eafaf0", stroke=GRN, sw=2.4, pad=12))
    p.append(fitbox(cx["SMU"] - bw / 2, cy - bh / 2, bw, bh,
                    "Пам'ять вцілілих\n(SMU)\n\nвікно глибини D,\nпростеження назад\nдо злиття шляхів",
                    size=14, bold=False, fill="#eef2f7", stroke=INK, sw=2.0, pad=12))

    # стрілки між блоками з підписами що тече (підписи вище стрілки)
    p.append(arrow(cx["BMU"] + bw / 2 + 2, cy, cx["ACSU"] - bw / 2 - 2, cy, sw=2.4))
    p.append(text((cx["BMU"] + cx["ACSU"]) / 2, cy - 30, "метрики", size=12.5, color=INK, bold=True))
    p.append(text((cx["BMU"] + cx["ACSU"]) / 2, cy - 14, "гілок λ", size=12.5, color=INK, bold=True))

    p.append(arrow(cx["ACSU"] + bw / 2 + 2, cy, cx["SMU"] - bw / 2 - 2, cy, sw=2.4))
    p.append(text((cx["ACSU"] + cx["SMU"]) / 2, cy - 30, "біти рішень", size=12.5, color=INK, bold=True))
    p.append(text((cx["ACSU"] + cx["SMU"]) / 2, cy - 14, "(вказівники)", size=12.5, color=MUTED))

    # вихід
    p.append(arrow(cx["SMU"] + bw / 2 + 2, cy + 22, W - 40, cy + 22, sw=2.4))
    p.append(text(W - 44, cy - 24, "відновлені", size=13, color=GRN, bold=True, anchor="end"))
    p.append(text(W - 44, cy - 6, "біти", size=13, color=GRN, bold=True, anchor="end"))

    # петля зворотного зв'язку над ACSU (широка дуга; підписи ВИЩЕ апексу)
    lx1, lx2 = cx["ACSU"] + 132, cx["ACSU"] - 132
    top = cy - bh / 2
    loop = ('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="2.6" marker-end="url(#arrowRED)"/>'
            % (lx1, top - 2, lx1, top - 122, lx2, top - 122, lx2, top - 2, RED))
    p.append(loop)
    p.append(text(cx["ACSU"], top - 138, "метрики станів ← такт t−1", size=13, color=RED, bold=True))
    p.append(text(cx["ACSU"], top - 122, "замкнена петля — межа швидкості", size=11.5, color=RED, italic=True))

    b, bw2, bh2 = textbox(W / 2, H - 30,
                          "BMU і SMU конвеєризуються вільно; уся межа швидкості — в одній замкненій ланці ACS",
                          size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Анатомія декодера: три блоки й петля, що впирається в межу швидкості")


# ── 2. Жорстке проти м'якого рішення ─────────────────────────────────────────

def fig_metric():
    W, H = 1000, 500
    p = []

    xL, xR = 130, 870          # −1 … +1
    xC = (xL + xR) / 2         # поріг 0
    span = (xR - xL) / 2

    def vx(v):                 # значення −1..+1 → x
        return xC + v * span

    yH = 180                   # рядок «жорстке»
    yS = 360                   # рядок «м'яке»

    # спільні підписи кінців осі
    p.append(text(xL, 96, "символ −1  (передана 1)", size=13, color=INK, bold=True))
    p.append(text(xR, 96, "символ +1  (переданий 0)", size=13, color=INK, bold=True, anchor="middle"))
    p.append(text(xC, 96, "поріг 0", size=12, color=MUTED, italic=True))

    # ── жорстке: одна межа, дві скриньки ──
    p.append(text(xL - 8, yH - 34, "жорстке рішення", size=14, color=BLU, bold=True, anchor="start"))
    p.append(rect(xL, yH - 16, xC - xL, 32, fill="#eef2fd", stroke=GREY, sw=1.2, rx=4))
    p.append(rect(xC, yH - 16, xR - xC, 32, fill="#fdecea", stroke=GREY, sw=1.2, rx=4))
    p.append(line(xC, yH - 30, xC, yH + 30, color=INK, sw=2.4))
    p.append(text((xL + xC) / 2, yH + 6, "→ рішення 1", size=13, color=INK, bold=True))
    p.append(text((xC + xR) / 2, yH + 6, "→ рішення 0", size=13, color=INK, bold=True))

    # ── м'яке: 8 рівнів ──
    p.append(text(xL - 8, yS - 34, "м'яке рішення — 8 рівнів (3 біти)", size=14, color=GRN, bold=True, anchor="start"))
    step = (xR - xL) / 8
    for k in range(9):
        xx = xL + k * step
        p.append(line(xx, yS - 16, xx, yS + 16, color=(INK if k == 4 else GREY), sw=(2.2 if k == 4 else 1.3)))
    p.append(rect(xL, yS - 16, xR - xL, 32, fill="none", stroke=GREY, sw=1.3, rx=4))
    p.append(text(xL + step * 0.5, yS + 6, "певна", size=10.5, color=MUTED))
    p.append(text(xL + step * 0.5, yS + 30, "1", size=11, color=MUTED, bold=True))
    p.append(text(xR - step * 0.5, yS + 6, "певний", size=10.5, color=MUTED))
    p.append(text(xR - step * 0.5, yS + 30, "0", size=11, color=MUTED, bold=True))

    # спільна вибірка +0.3
    xs = vx(0.3)
    p.append(line(xs, yH + 34, xs, yS - 34, color=RED, sw=1.6, dash="4 4"))
    p.append(circle(xs, yH, 6, fill=RED, stroke=RED, sw=1.5))
    p.append(circle(xs, yS, 6, fill=RED, stroke=RED, sw=1.5))
    p.append(text(xs + 10, yH - 40, "та сама вибірка +0.3", size=12.5, color=RED, bold=True, anchor="start"))
    p.append(text(xs + 12, yH - 6, "жорстке: → 0", size=11.5, color=INK, anchor="start"))
    p.append(text(xs + 12, yH + 10, "(певність утрачено)", size=10.5, color=MUTED, anchor="start"))
    # мітка рівня м'якого
    p.append(text(xs, yS + 52, "«слабкий 0» — певність збережено", size=12, color=GRN, bold=True))

    b, bw, bh = textbox(W / 2, H - 34,
                        "метрика гілки = квадрат відстані вибірки до символу ±1 мітки ребра   ·   м'яке рішення ≈ 2 дБ виграшу",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "metric.svg"), W, H, *p,
           title="Жорстке рішення викидає певність, м'яке її зберігає")


# ── 3. Метелик ACS ───────────────────────────────────────────────────────────

def fig_acs():
    W, H = 1020, 540
    p = []

    xS, xD = 250, 770
    yT, yB = 180, 360
    R = 30

    p.append(text(W / 2, 74, "прийнято: 11", size=15, color=INK, bold=True))

    # ребра (спершу лінії, тоді вузли зверху)
    # переможні — зелені, програшні — сірі
    def edge(a, b, color, sw):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        p.append(line(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R, color=color, sw=sw))

    src00, src01 = (xS, yT), (xS, yB)
    dst00, dst10 = (xD, yT), (xD, yB)
    edge(src00, dst00, GREY, 2.0)          # 00→00 (програш)
    edge(src01, dst00, GRN, 3.4)           # 01→00 (виграш)
    edge(src00, dst10, GRN, 3.4)           # 00→10 (виграш)
    edge(src01, dst10, GREY, 2.0)          # 01→10 (програш)

    # мітки виходів біля ребер (з боку призначення, поза лініями)
    p.append(text(xD - 150, yT - 16, "вих 00", size=12, color=MUTED))
    p.append(text(xD - 150, yT + 30, "вих 11", size=12, color=GRN, bold=True))
    p.append(text(xD - 150, yB - 28, "вих 11", size=12, color=GRN, bold=True))
    p.append(text(xD - 150, yB + 18, "вих 00", size=12, color=MUTED))

    # вузли-джерела з метриками
    for (cx, cy, nm, pmv) in [(xS, yT, "00", "PM=2"), (xS, yB, "01", "PM=1")]:
        p.append(circle(cx, cy, R, fill="#f4f6f8", stroke=INK, sw=2.0))
        p.append(text(cx, cy + 6, nm, size=16, color=INK, bold=True))
        p.append(text(cx - R - 10, cy + 5, pmv, size=13, color=INK, bold=True, anchor="end"))
    p.append(text(xS, yT - R - 16, "стани-джерела", size=12, color=MUTED, italic=True))

    # вузли-призначення з новою метрикою + вказівник
    for (cx, cy, nm, res, ptr) in [(xD, yT, "00", "1", "з 01"), (xD, yB, "10", "2", "з 00")]:
        p.append(circle(cx, cy, R, fill="#eafaf0", stroke=GRN, sw=2.8))
        p.append(text(cx, cy + 6, nm, size=16, color=INK, bold=True))
        p.append(text(cx + R + 10, cy - 4, "PM=" + res, size=13, color=GRN, bold=True, anchor="start"))
        p.append(text(cx + R + 10, cy + 14, "↖ " + ptr, size=11.5, color=GRN, anchor="start"))
    p.append(text(xD, yT - R - 16, "стани-призначення", size=12, color=MUTED, italic=True))

    # арифметика ACS унизу
    b, bw, bh = textbox(W / 2, 452,
                        "у стан 00:  з 00 (вих 00) 2+2=4   |   з 01 (вих 11) 1+0=1  →  вцілів 1\n"
                        "у стан 10:  з 00 (вих 11) 2+0=2  →  вцілів 2   |   з 01 (вих 00) 1+2=3",
                        size=13, bold=True, fill="#eef2f7", stroke=INK, sw=1.8, pad=12)
    p.append(b)
    b, bw, bh = textbox(W / 2, H - 26,
                        "метелик: 2 джерела → 2 призначення; ребра несуть доповняльні виходи 00/11",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=10)
    p.append(b)

    render(os.path.join(OUT, "acs-butterfly.svg"), W, H, *p,
           title="Метелик ACS: додати, порівняти, вибрати — один вцілілий на стан")


# ── 4. Злиття вцілілих шляхів і глибина рішення ──────────────────────────────

def fig_merge():
    W, H = 1120, 480
    p = []

    yr = [150, 224, 298, 372]                   # чотири стани
    ncol = 13
    x = [96 + i * 78 for i in range(ncol)]
    mcol = 6                                     # колонка злиття

    # напрямні станів (ледь помітні)
    for y in yr:
        p.append(line(x[0], y, x[-1], y, color="#eef1f4", sw=1.2, dash="2 6"))

    # стовбур (усі шляхи спільні) — товста зелена лінія
    trunk_rows = [2, 1, 1, 2, 2, 3, 2]          # cols 0..6
    trunk = [(x[i], yr[trunk_rows[i]]) for i in range(mcol + 1)]
    p.append(polyline(trunk, color=GRN, sw=4.2))

    # чотири вцілілі, що розходяться від злиття до чотирьох станів праворуч
    branches = [
        [2, 2, 1, 0, 0, 0, 0],   # → стан 0
        [2, 3, 3, 2, 1, 1, 1],   # → стан 1
        [2, 2, 3, 3, 2, 2, 2],   # → стан 2
        [2, 1, 2, 2, 3, 3, 3],   # → стан 3
    ]
    bc = [BLU, "#8e44ad", "#d68910", RED]
    for bi, br in enumerate(branches):
        pts = [(x[mcol], yr[2])] + [(x[mcol + 1 + j], yr[br[j]]) for j in range(len(br) - 1)]
        # вирівняти довжину до правого краю
        pts = [(x[mcol + k], yr[br[k - 0]]) if False else pp for k, pp in enumerate(pts)]
        p.append(polyline(pts, color=bc[bi], sw=2.0))

    # вузол злиття
    p.append(circle(x[mcol], yr[2], 8, fill="#eafaf0", stroke=GRN, sw=2.8))

    # лінія глибини рішення
    p.append(line(x[mcol], 108, x[mcol], 410, color=INK, sw=2.0, dash="6 5"))
    p.append(text(x[mcol], 100, "глибина рішення  D ≈ 5(K−1)", size=13, color=INK, bold=True))

    # підписи областей
    p.append(text((x[0] + x[mcol]) / 2, 434, "усі вцілілі злилися → біт вирішено", size=12.5, color=GRN, bold=True))
    p.append(text((x[mcol] + x[-1]) / 2, 434, "ще різні — змагаються", size=12.5, color=MUTED, bold=True))
    p.append(text(x[0] - 6, 130, "минуле", size=11.5, color=MUTED, italic=True, anchor="start"))
    p.append(text(x[-1] + 4, 130, "тепер", size=11.5, color=MUTED, italic=True, anchor="end"))

    # видати найдавніший біт
    p.append(arrow(x[0] + 30, yr[trunk_rows[0]] - 26, x[0] + 2, yr[trunk_rows[0]] - 6, sw=2.0))
    p.append(text(x[0] + 36, yr[trunk_rows[0]] - 30, "видати найдавніший біт", size=11.5, color=GRN, bold=True, anchor="start"))
    # вікно ковзає
    p.append(arrow(x[-4], 128, x[-1], 128, sw=2.0))
    p.append(text(x[-4] - 4, 124, "вікно ковзає", size=11.5, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "merge.svg"), W, H, *p,
           title="Вцілілі шляхи зливаються в минулому — тому декодер видає біти на льоту")


# ── 5. Виграш кодування: BER від Eb/N0 ───────────────────────────────────────

def fig_gain():
    W, H = 940, 590
    p = []

    xL, xR = 150, 860          # 0 … 11 дБ
    yT, yB = 96, 516           # 10⁰ … 10⁻⁶
    dbmax = 11
    decades = 6

    def px(db):
        return xL + db / dbmax * (xR - xL)

    def py(logber):            # logber ∈ [0,-6]
        return yT + (-logber) / decades * (yB - yT)

    # осі
    p.append(line(xL, yT, xL, yB, color=MUTED, sw=1.8))
    p.append(line(xL, yB, xR, yB, color=MUTED, sw=1.8))
    for d in range(0, decades + 1):
        yy = py(-d)
        p.append(line(xL - 5, yy, xL, yy, color=MUTED, sw=1.4))
        p.append(text(xL - 12, yy + 4, "10⁻%d" % d if d else "10⁰", size=11.5, color=MUTED, anchor="end"))
    for db in range(0, dbmax + 1, 2):
        xx = px(db)
        p.append(line(xx, yB, xx, yB + 5, color=MUTED, sw=1.4))
        p.append(text(xx, yB + 22, "%d" % db, size=11.5, color=MUTED))
    p.append(text((xL + xR) / 2, yB + 44, "Eb/N0, дБ", size=12.5, color=MUTED, italic=True))
    p.append(text(xL - 8, yT - 16, "ймовірність помилки на біт", size=12, color=MUTED, italic=True, anchor="start"))

    # три криві (схематичні waterfall-и), кожна досягає 10⁻⁵ у своїй точці
    soft = [(2.5, -1), (3.2, -2), (3.8, -3), (4.2, -4), (4.6, -5), (4.9, -6)]
    hard = [(4.0, -1), (4.9, -2), (5.6, -3), (6.1, -4), (6.6, -5), (7.0, -6)]
    unc = [(5.5, -1), (6.7, -2), (7.7, -3), (8.6, -4), (9.6, -5), (10.4, -6)]
    for pts, col, sw in [(unc, MUTED, 2.4), (hard, BLU, 2.8), (soft, GRN, 3.2)]:
        p.append(polyline([(px(a), py(b)) for a, b in pts], color=col, sw=sw))

    # підписи кривих біля верху
    p.append(text(px(5.5) + 8, py(-1) - 6, "некодована", size=12.5, color=MUTED, bold=True, anchor="start"))
    p.append(text(px(4.0) - 8, py(-1.15) - 6, "жорсткий", size=12.5, color=BLU, bold=True, anchor="end"))
    p.append(text(px(4.0) - 8, py(-1.15) + 10, "Вітербі", size=12.5, color=BLU, bold=True, anchor="end"))
    p.append(text(px(2.5) - 6, py(-1) + 4, "м'який", size=12.5, color=GRN, bold=True, anchor="end"))
    p.append(text(px(2.5) - 6, py(-1) + 20, "Вітербі", size=12.5, color=GRN, bold=True, anchor="end"))

    # рівень 10⁻⁵ і проміжки
    y5 = py(-5)
    p.append(line(xL, y5, xR, y5, color="#d8b23a", sw=1.4, dash="6 5"))
    xs, xh, xu = px(4.6), px(6.6), px(9.6)
    for xx, col in [(xs, GRN), (xh, BLU), (xu, MUTED)]:
        p.append(circle(xx, y5, 5, fill=col, stroke=col, sw=1.2))
    p.append(dbl_arrow(xs, y5 - 40, xh, color=INK, sw=2.0))
    p.append(text((xs + xh) / 2, y5 - 48, "≈ 2 дБ", size=12.5, color=INK, bold=True))
    p.append(dbl_arrow(xs, y5 - 78, xu, color=INK, sw=2.0))
    p.append(text((xs + xu) / 2, y5 - 86, "≈ 5 дБ  (повний виграш на 10⁻⁵)", size=12.5, color=INK, bold=True))

    b, bw, bh = textbox(W / 2, H - 26,
                        "схема, не точні дані  ·  кодування зсуває криву ліворуч: та сама надійність за меншої потужності",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=11)
    p.append(b)

    render(os.path.join(OUT, "coding-gain.svg"), W, H, *p,
           title="Виграш кодування: м'яке рішення додає ≈ 2 дБ до жорсткого")


# ── 6. Геометрія м'якого рішення: сузір'я на колі рівної норми ────────────────

def fig_ml_geometry():
    W, H = 960, 660
    p = []

    cx0, cy0, s = 480, 340, 150            # початок і масштаб (px на одиницю)

    def sx(a):
        return cx0 + a * s

    def sy(b):
        return cy0 - b * s

    # осі
    p.append(line(cx0 - 236, cy0, cx0 + 246, cy0, color=GREY, sw=1.6))
    p.append(line(cx0, cy0 - 236, cx0, cy0 + 236, color=GREY, sw=1.6))
    p.append(text(cx0 + 252, cy0 + 4, "r₀", size=13, color=MUTED, italic=True, anchor="start"))
    p.append(text(cx0 + 10, cy0 - 244, "r₁", size=13, color=MUTED, italic=True, anchor="start"))

    # коло рівної норми |s| = √2
    rc = (2 ** 0.5) * s
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="5 6"/>' % (cx0, cy0, rc, MUTED))
    p.append(text(sx(1.41) + 12, cy0 - 6, "|s| = √N = √2", size=12.5, color=MUTED, italic=True, anchor="start"))

    # прийнята точка r
    rr = (0.3, -0.9)
    rp = (sx(rr[0]), sy(rr[1]))

    # ребра-відстані від r до кожної мітки (переможна — зелена й товста)
    corners = {
        "00": (1, 1), "10": (-1, 1), "01": (1, -1), "11": (-1, -1),
    }
    for nm, (a, b) in corners.items():
        cp = (sx(a), sy(b))
        win = (nm == "01")
        p.append(line(rp[0], rp[1], cp[0], cp[1],
                      color=(GRN if win else GREY), sw=(3.4 if win else 1.8),
                      dash=(None if win else "4 5")))

    # вузли-мітки
    for nm, (a, b) in corners.items():
        cp = (sx(a), sy(b))
        win = (nm == "01")
        p.append(circle(cp[0], cp[1], 8,
                        fill=("#eafaf0" if win else "#eef2f7"),
                        stroke=(GRN if win else INK), sw=(2.8 if win else 2.0)))

    # підписи міток (назва + координати; числа — у таблиці статті)
    p.append(text(sx(1) + 6, sy(1) - 18, "мітка 00 = (+1, +1)", size=12.5, color=INK, bold=True, anchor="start"))
    p.append(text(sx(-1) - 6, sy(1) - 18, "мітка 10 = (−1, +1)", size=12.5, color=INK, bold=True, anchor="end"))
    p.append(text(sx(-1) - 6, sy(-1) + 26, "мітка 11 = (−1, −1)", size=12.5, color=INK, bold=True, anchor="end"))
    p.append(text(sx(1) + 6, sy(-1) + 26, "мітка 01 = (+1, −1)", size=12.5, color=GRN, bold=True, anchor="start"))
    p.append(text(sx(1) + 6, sy(-1) + 44, "← найближча до r", size=12, color=GRN, bold=True, anchor="start"))

    # точка r
    p.append(circle(rp[0], rp[1], 6, fill=RED, stroke=RED, sw=1.5))
    p.append(text(rp[0] - 12, rp[1] + 30, "прийнято  r = (+0.3, −0.9)", size=13, color=RED, bold=True, anchor="middle"))

    b, bw, bh = textbox(W / 2, H - 30,
                        "усі 4 мітки лежать на колі однакової норми √N — тому найближча\n"
                        "за евклідовою відстанню воднораз і найбільша за кореляцією",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "ml-geometry.svg"), W, H, *p,
           title="Геометрія м'якого рішення: найближча мітка = найбільша кореляція")


# ── 7. Дві метрики — одна спадна пряма: d² = C − 2·кореляція ──────────────────

def fig_metric_equiv():
    W, H = 940, 580
    p = []

    xL, xR = 150, 830          # кореляція −1.5 … +1.5
    yT, yB = 96, 470           # d²  6 … 0
    cmin, cmax = -1.5, 1.5
    dmax = 6.0

    def px(c):
        return xL + (c - cmin) / (cmax - cmin) * (xR - xL)

    def py(d):
        return yB - d / dmax * (yB - yT)

    # осі
    p.append(line(xL, yT, xL, yB, color=MUTED, sw=1.8))
    p.append(line(xL, yB, xR, yB, color=MUTED, sw=1.8))
    for c in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        xx = px(c)
        p.append(line(xx, yB, xx, yB + 5, color=MUTED, sw=1.3))
        p.append(text(xx, yB + 22, ("%+.1f" % c).replace("+0.0", "0.0"), size=11.5, color=MUTED))
    for d in range(0, 7):
        yy = py(d)
        p.append(line(xL - 5, yy, xL, yy, color=MUTED, sw=1.3))
        p.append(text(xL - 12, yy + 4, "%d" % d, size=11.5, color=MUTED, anchor="end"))
    p.append(text((xL + xR) / 2, yB + 46, "кореляція  Σ rᵢsᵢ  →", size=13, color=MUTED, italic=True))
    p.append(text(xL - 14, yT - 14, "квадрат відстані  Σ(rᵢ−sᵢ)²", size=12.5, color=MUTED, italic=True, anchor="start"))

    # пряма d² = 2.9 − 2·c
    C = 2.9
    p.append(line(px(cmin), py(C - 2 * cmin), px(1.45), py(C - 2 * 1.45), color=BLU, sw=2.6))
    p.append(text(px(0.05) + 8, py(C) - 10, "d² = 2.90 − 2·(кор)", size=13, color=BLU, bold=True, anchor="start"))

    # чотири мітки на прямій
    pts = {"10": -1.2, "00": -0.6, "11": 0.6, "01": 1.2}
    for nm, c in pts.items():
        d = C - 2 * c
        win = (nm == "01")
        if win:
            # напрямні до осей
            p.append(line(px(c), py(d), px(c), yB, color=GRN, sw=1.4, dash="4 4"))
            p.append(line(xL, py(d), px(c), py(d), color=GRN, sw=1.4, dash="4 4"))
            p.append(text(px(c), yB + 22, "+1.20", size=11.5, color=GRN, bold=True))
            p.append(text(xL - 12, py(d) + 4, "0.50", size=11.5, color=GRN, bold=True, anchor="end"))
        p.append(circle(px(c), py(d), (8 if win else 6),
                        fill=("#eafaf0" if win else "#eef2f7"),
                        stroke=(GRN if win else INK), sw=(2.8 if win else 2.0)))
        p.append(text(px(c) + (12 if c < 1 else 0), py(d) - (14 if not win else 16),
                      nm, size=13, color=(GRN if win else INK), bold=True,
                      anchor=("middle" if win else "start")))
    p.append(text(px(1.2), py(0.5) - 34, "макс. кореляція = мін. відстань", size=11.5, color=GRN, bold=True, anchor="middle"))

    b, bw, bh = textbox(W / 2, H - 30,
                        "дві м'які метрики лежать на одній спадній прямій: більша кореляція\n"
                        "= менша відстань, тож argmax і argmin — та сама мітка (тут 01)",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=10)
    p.append(b)

    render(os.path.join(OUT, "metric-equiv.svg"), W, H, *p,
           title="Кореляція й відстань — одна спадна пряма, тож вибір той самий")


# ── 8. Дві архітектури SMU: простеження проти обміну регістрами ───────────────

def fig_smu_two_ways():
    W, H = 1300, 650
    p = [redmarker()]

    PUR = "#8e44ad"
    states = ["00", "01", "10", "11"]
    cw, ch = 60, 46
    gy = 176
    rows = 4

    def cell(x, y, s, fill, stroke, tcol=INK, sw=1.6, bold=True):
        out = rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=sw, rx=5)
        out += text(x + cw / 2, y + ch / 2 + 6, s, size=16, color=tcol, bold=bold)
        return out

    # роздільник панелей
    p.append(line(W / 2, 60, W / 2, H - 70, color=GREY, sw=1.4, dash="3 7"))

    # ── ЛІВА панель: простеження (traceback) ──
    Lx = 150
    p.append(text(Lx + 3 * cw, 96, "простеження (traceback)", size=17, color=INK, bold=True))
    p.append(text(Lx + 3 * cw, 118, "1 біт рішення на стан на такт — крокуємо назад крізь вікно",
                  size=12.5, color=MUTED))
    # заголовок часу
    p.append(text(Lx - 34, gy - 16, "стан", size=11.5, color=MUTED, anchor="end", italic=True))
    p.append(text(Lx + cw / 2, gy - 16, "старий", size=11, color=MUTED))
    p.append(text(Lx + 5 * cw + cw / 2, gy - 16, "новий", size=11, color=MUTED))
    p.append(arrow(Lx + cw + 6, gy - 20, Lx + 5 * cw - 6, gy - 20, sw=1.6))
    bitsL = [[1, 0, 1, 1, 0, 1], [0, 1, 0, 0, 1, 0],
             [1, 1, 0, 1, 0, 0], [0, 0, 1, 0, 1, 1]]
    # зворотний шлях (крокуємо назад): (стовпець, рядок)
    path = [(5, 1), (4, 2), (3, 0), (2, 2), (1, 1), (0, 3)]
    pathset = set(path)
    land = (0, 3)                         # клітина видачі (найдавніший біт)
    for r in range(rows):
        p.append(text(Lx - 18, gy + r * ch + ch / 2 + 5, states[r],
                      size=13, color=INK, bold=True, anchor="end"))
        for c in range(6):
            on = (c, r) in pathset
            # цифру лишаємо лише в контекстних клітинах і в клітині видачі,
            # щоб зелена ламана простеження не перетинала гліфів
            show = (str(bitsL[r][c]) if (not on or (c, r) == land) else "")
            p.append(cell(Lx + c * cw, gy + r * ch, show,
                          fill=("#eafaf0" if on else "#f7f9fb"),
                          stroke=(GRN if on else GREY),
                          tcol=(GRN if (c, r) == land else (INK if on else MUTED)),
                          sw=(2.4 if on else 1.3), bold=on))
    # ламана зворотного простеження крізь порожні клітини шляху
    pts = [(Lx + c * cw + cw / 2, gy + r * ch + ch / 2) for (c, r) in path]
    p.append(polyline(pts, color=GRN, sw=2.6))
    for (c, r) in path:
        rr = 4.5 if (c, r) != land else 0
        if rr:
            p.append(circle(Lx + c * cw + cw / 2, gy + r * ch + ch / 2, rr, fill=GRN, stroke=GRN))
    # видати найдавніший біт — найлівіший стовпець (path-стрілка знизу: не ріже підписів)
    exL = Lx + cw / 2
    p.append('<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrowGRN)"/>'
             % (exL, 396, exL, gy + 4 * ch + 3, GRN))
    p.append(text(exL, 414, "видача", size=12, color=GRN, bold=True))
    p.append(text(exL, 430, "біт 0", size=12, color=GRN, bold=True))
    b, _, _ = textbox(Lx + 3 * cw, 508,
                      "пам'ять D·S біт  ·  запис S біт/такт\nвидача: прохід назад на D кроків",
                      size=12.5, bold=True, fill="#eef2f7", stroke=INK, sw=1.6, pad=11)
    p.append(b)

    # ── ПРАВА панель: обмін регістрами (register-exchange) ──
    Rx = W / 2 + 130
    p.append(text(Rx + 3 * cw, 96, "обмін регістрами (register-exchange)", size=17, color=INK, bold=True))
    p.append(text(Rx + 3 * cw, 118, "весь декодований префікс у кожному стані — копіюємо переможця",
                  size=12.5, color=MUTED))
    p.append(text(Rx + cw / 2, gy - 16, "старий", size=11, color=MUTED))
    p.append(text(Rx + 5 * cw + cw / 2, gy - 16, "новий", size=11, color=MUTED))
    regs = [[1, 0, 1, 1, 0, 1], [1, 0, 1, 0, 1, 1],
            [0, 1, 1, 0, 1, 0], [1, 1, 0, 0, 1, 0]]
    win, dst = 1, 3                       # переможець(01) → призначення(11)
    for r in range(rows):
        p.append(text(Rx - 18, gy + r * ch + ch / 2 + 5, states[r],
                      size=13, color=INK, bold=True, anchor="end"))
        for c in range(6):
            hot = (r in (win, dst))
            p.append(cell(Rx + c * cw, gy + r * ch, str(regs[r][c]),
                          fill=("#f6eefb" if r == win else ("#eafaf0" if r == dst else "#f7f9fb")),
                          stroke=(PUR if r == win else (GRN if r == dst else GREY)),
                          tcol=(INK if hot else MUTED), sw=(2.2 if hot else 1.3), bold=hot))
    # стрілка копіювання переможець → призначення (зі зсувом), компактно праворуч
    ax = Rx + 6 * cw + 12
    ay1 = gy + win * ch + ch / 2
    ay2 = gy + dst * ch + ch / 2
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="2.6" marker-end="url(#arrowGRN)"/>'
             % (ax, ay1, ax + 44, ay1, ax + 44, ay2, ax, ay2, PUR))
    p.append(text(ax + 52, (ay1 + ay2) / 2 + 4, "копія<<1", size=11, color=PUR, bold=True, anchor="start"))
    # видача — найлівіший (найстарший) біт: та сама найлівіша колонка (path-стрілка знизу)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (Rx - 1, gy + 3 * ch - 1, cw + 2, ch + 2, GRN))
    exR = Rx + cw / 2
    p.append('<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrowGRN)"/>'
             % (exR, 396, exR, gy + 4 * ch + 3, GRN))
    p.append(text(exR, 414, "видача", size=12, color=GRN, bold=True))
    p.append(text(exR, 430, "миттєва", size=12, color=GRN, bold=True))
    b, _, _ = textbox(Rx + 3 * cw, 508,
                      "пам'ять D·S біт  ·  переписуємо всі S·D біт/такт\nвидача: одразу, без простеження",
                      size=12.5, bold=True, fill="#f6eefb", stroke=INK, sw=1.6, pad=11)
    p.append(b)

    b, _, _ = textbox(W / 2, H - 34,
                      "та сама пам'ять D·S біт — але простеження пише мало й читає назад, "
                      "а обмін регістрами щотакту рухає всю пам'ять: швидкість проти латентності",
                      size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "smu-two-ways.svg"), W, H, *p,
           title="Два блоки пам'яті вцілілих: зберігати біти й крокувати назад — чи носити префікси")


# ── 9. Пастка малої глибини: передчасний хибний біт ──────────────────────────

def fig_depth_trap():
    W, H = 1240, 560
    p = []

    # ґратка-хвіст такти 6..12 (минуле → тепер), 4 стани — ліва зона
    x = [140 + i * 104 for i in range(7)]            # t6 … t12  → 140..764
    yr = [156, 250, 344, 438]                        # стани 00,01,10,11
    states = ["00", "01", "10", "11"]

    # напрямні станів
    for r, y in enumerate(yr):
        p.append(line(x[0] - 8, y, x[-1] + 8, y, color="#eef1f4", sw=1.2, dash="2 6"))
        p.append(text(x[0] - 24, y + 5, states[r], size=12.5, color=MUTED, bold=True, anchor="end"))

    # чотири вцілілі (реальні послідовності станів t6..t12 із симуляції)
    seqs = {
        "s00": [2, 1, 2, 3, 1, 0, 0],
        "s01": [2, 1, 2, 1, 2, 3, 1],   # найкращий стан наприкінці (метрика 2)
        "s10": [2, 1, 2, 3, 1, 0, 2],
        "s11": [2, 1, 0, 0, 0, 2, 3],
    }
    faint = {"s00": BLU, "s10": "#d68910", "s11": "#16a085"}
    for name in ("s00", "s10", "s11"):
        pts = [(x[i], yr[seqs[name][i]]) for i in range(7)]
        p.append(polyline(pts, color=faint[name], sw=1.8, dash="5 4"))
    # найкращий — зелений товстий
    p.append(polyline([(x[i], yr[seqs["s01"][i]]) for i in range(7)], color=GRN, sw=3.6))

    # вузол злиття на t7 (усі стани = 01)
    p.append(circle(x[1], yr[1], 9, fill="#eafaf0", stroke=GRN, sw=3))

    # мітки часу
    p.append(text(x[0] - 24, 120, "минуле", size=12, color=MUTED, italic=True, anchor="end"))
    p.append(text(x[-1] + 8, 120, "тепер (t)", size=12, color=INK, bold=True, anchor="end"))
    p.append(circle(x[-1], yr[1], 8, fill=GRN, stroke=GRN))
    p.append(text(x[-1] + 14, yr[1] + 5, "найкращий", size=11.5, color=GRN, bold=True, anchor="start"))
    p.append(text(x[-1] + 14, yr[1] + 21, "стан 01", size=11.5, color=GRN, bold=True, anchor="start"))

    # вертикаль глибини 6 (t7) — злилися (підпис вгорі ліворуч від лінії)
    p.append(line(x[1], 96, x[1], 474, color=GRN, sw=2.0, dash="6 5"))
    p.append(text(x[1] - 8, 88, "глибина 6", size=12.5, color=GRN, bold=True, anchor="end"))
    p.append(text(x[1] - 8, 498, "злилися → 0", size=12, color=GRN, bold=True, anchor="end"))
    # вертикаль глибини 5 (t8) — ще різні (підпис угорі праворуч від лінії)
    p.append(line(x[2], 96, x[2], 474, color=RED, sw=2.0, dash="6 5"))
    p.append(text(x[2] + 8, 88, "глибина 5", size=12.5, color=RED, bold=True, anchor="start"))
    p.append(text(x[2] + 8, 498, "ще різні: 1,1,1,0", size=12, color=RED, bold=True, anchor="start"))

    # ── права зона: дві картки видачі ──
    cardx = 1010
    b, _, _ = textbox(cardx, 214,
                      "видача при D = 5\n\n1   ✗ хибний\nбіт іще не злився",
                      size=13, bold=True, fill="#fdecea", stroke=RED, sw=2.0, pad=13)
    p.append(b)
    b, _, _ = textbox(cardx, 356,
                      "видача при D = 6\n\n0   ✓ правильний\nістинний біт msg = 0",
                      size=13, bold=True, fill="#eafaf0", stroke=GRN, sw=2.0, pad=13)
    p.append(b)

    b, _, _ = textbox(W / 2, H - 26,
                      "той самий потік і той самий найкращий стан 01 — простеження на 5 тактів видає 1, "
                      "а на 6 (аж до злиття) — правильний 0",
                      size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=11)
    p.append(b)

    render(os.path.join(OUT, "depth-trap.svg"), W, H, *p,
           title="Замала глибина видає передчасний хибний біт (K = 3, сплеск на парі 8)")


if __name__ == "__main__":
    fig_pipeline()
    fig_metric()
    fig_acs()
    fig_merge()
    fig_gain()
    fig_ml_geometry()
    fig_metric_equiv()
    fig_smu_two_ways()
    fig_depth_trap()
    print("OK: figures written to", OUT)
