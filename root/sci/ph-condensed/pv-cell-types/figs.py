# -*- coding: utf-8 -*-
"""Фігури теми «Типи фотоелементів: матеріали й фізика»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


# ── Фігура 1: стеля ККД проти забороненої зони (крива Шоклі–Квайссера) ───────
def fig_bandgap_efficiency():
    w, h = 760, 480
    x0, xR = 95, 660          # eg: 0.5 … 2.6 еВ
    y0, yT = 395, 78          # eff: 0 … 36 %
    sx = (xR - x0) / (2.6 - 0.5)
    sy = (y0 - yT) / 36.0
    def X(eg): return x0 + (eg - 0.5) * sx
    def Y(e):  return y0 - e * sy

    # крива стелі одного переходу (наближено до Шоклі–Квайссера)
    curve = [(0.5, 4), (0.6, 10), (0.7, 17), (0.8, 23), (0.9, 27.5),
             (1.0, 30.5), (1.1, 32.3), (1.2, 33.1), (1.34, 33.7), (1.5, 33.0),
             (1.6, 32.2), (1.7, 31.0), (1.8, 29.5), (1.9, 28.0), (2.0, 26.0),
             (2.1, 24.0), (2.2, 22.0), (2.3, 19.5), (2.4, 17.0), (2.5, 14.5), (2.6, 12.0)]
    curve_px = [(X(eg), Y(e)) for eg, e in curve]

    parts = []
    # смуга робочих матеріалів 1.0…1.7 еВ (позаду всього)
    parts.append(rect(X(1.0), yT, X(1.7) - X(1.0), y0 - yT,
                      fill="#e8f6ee", stroke="none", sw=0, rx=0))
    parts.append(text((X(1.0) + X(1.7)) / 2, 360, "робочі матеріали", 13, FIELD, bold=True))
    parts.append(text((X(1.0) + X(1.7)) / 2, 378, "1.0 – 1.7 еВ", 12, FIELD))

    # осі
    parts.append(line(x0, y0, xR + 12, y0, INK, 2.0))
    parts.append(line(x0, y0, x0, yT - 6, INK, 2.0))
    for eg in (0.5, 1.0, 1.5, 2.0, 2.5):
        parts.append(line(X(eg), y0, X(eg), y0 + 5, INK, 1.5))
        parts.append(text(X(eg), y0 + 22, "%.1f" % eg, 12, MUTED))
    parts.append(text((x0 + xR) / 2, y0 + 42, "заборонена зона, еВ", 13, MUTED))
    for e in (0, 10, 20, 30):
        parts.append(line(x0 - 5, Y(e), x0, Y(e), INK, 1.5))
        parts.append(text(x0 - 10, Y(e) + 4, "%d" % e, 12, MUTED, anchor="end"))
    parts.append(text(x0 - 12, yT - 14, "стеля ККД одного переходу, %", 12, MUTED, anchor="start"))

    # крива
    parts.append(polyline(curve_px, INK, sw=3))

    # оптимум 1.34 еВ
    parts.append(line(X(1.34), y0, X(1.34), Y(33.7), MUTED, 1.4, dash="5,4"))
    parts.append(text(X(1.34), yT - 26, "оптимум ~1.34 еВ", 13, INK, bold=True))
    parts.append(text(X(1.34), yT - 10, "стеля ~33 %", 12, INK))

    # матеріали-точки на кривій
    mats = [(1.12, 32.4, INK),   (1.42, 33.5, FIELD), (1.50, 33.0, NEG),
            (1.60, 32.2, POS),   (1.70, 31.0, MUTED)]
    for eg, e, col in mats:
        parts.append(circle(X(eg), Y(e), 6, BG, col, 2.4))

    # легенда під віссю (кольори = матеріали)
    leg = [("Si · 1.12 еВ", INK, 78), ("GaAs · 1.42 еВ", FIELD, 210),
           ("CdTe · 1.5 еВ", NEG, 360), ("перовскіт · 1.6 еВ", POS, 500),
           ("a-Si · 1.7 еВ", MUTED, 660)]
    for lab, col, lx in leg:
        parts.append(circle(lx, 458, 6, BG, col, 2.4))
        parts.append(text(lx + 13, 462, lab, 12, INK, anchor="start"))

    render(os.path.join(IMG, "bandgap-efficiency.svg"), w, h, *parts,
           title="Стеля ефективності залежить від забороненої зони")


# ── Фігура 2: пряма чи непряма зона — товщина матеріалу ─────────────────────
def fig_direct_indirect():
    w, h = 780, 440
    parts = []

    # ── ЛІВА панель: непрямозонний кремній (товста пластина) ──
    lx, ly, lw, lh = 150, 120, 210, 200
    parts.append(rect(lx, ly, lw, lh, fill="#dfe3e8", stroke=LINE, sw=2))
    parts.append(text(lx + lw / 2, ly - 16, "непрямозонний: кремній", 14, INK, bold=True))
    # фотони входять зліва й гаснуть глибоко
    depths = [(150, 0.72), (200, 0.95), (250, 0.55)]
    for yin, frac in depths:
        parts.append(arrow(lx - 52, yin, lx + 2, yin, POS, 2.2))
        xabs = lx + frac * lw
        parts.append(line(lx + 2, yin, xabs, yin, POS, 1.6, dash="4,3"))
        parts.append(circle(xabs, yin, 5, POS, POS, 1))
    parts.append(text(lx - 54, 108, "світло", 12, POS, anchor="start"))
    parts.append(text(lx + lw / 2, 344, "гасне повільно — потрібна", 12, INK))
    parts.append(text(lx + lw / 2, 361, "товста пластина", 13, INK, bold=True))
    parts.append(text(lx + lw / 2, 380, "~150 – 200 мкм", 12, MUTED))

    # ── ПРАВА панель: прямозонні (тонка плівка) ──
    rx, ry, rw, rh = 560, 120, 30, 200
    parts.append(rect(rx, ry, rw, rh, fill="#dfe3e8", stroke=LINE, sw=2))
    parts.append(text(rx + rw / 2, ry - 16, "прямозонні: GaAs · CdTe · перовскіт", 14, INK, bold=True))
    for yin in (150, 200, 250):
        parts.append(arrow(rx - 52, yin, rx + 2, yin, POS, 2.2))
        parts.append(circle(rx + rw * 0.5, yin, 5, POS, POS, 1))
    parts.append(text(rx + rw / 2, 344, "гасне одразу — досить", 12, INK))
    parts.append(text(rx + rw / 2, 361, "тонкої плівки", 13, INK, bold=True))
    parts.append(text(rx + rw / 2, 380, "~1 – 2 мкм", 12, MUTED))

    # порівняння товщини між панелями
    parts.append(text(w / 2, 200, "у ~100", 14, FIELD, bold=True))
    parts.append(text(w / 2, 220, "разів", 14, FIELD, bold=True))
    parts.append(text(w / 2, 240, "тонше", 14, FIELD, bold=True))
    parts.append(text(w / 2, 416, "(товщина схематична, не в масштабі)", 12, MUTED))

    render(os.path.join(IMG, "direct-indirect.svg"), w, h, *parts,
           title="Чому кремній — товста пластина, а решта — тонка плівка")


# ── Фігура 3: карта родин фотоелементів (ККД проти вартості) ────────────────
def fig_family_map():
    w, h = 780, 470
    parts = []

    # осі-стрілки
    parts.append(arrow(105, 410, 700, 410, INK, 2.0))     # вартість →
    parts.append(arrow(105, 410, 105, 80, INK, 2.0))      # ККД ↑
    parts.append(text(400, 438, "вартість і складність  →", 13, MUTED))
    parts.append(text(112, 76, "↑  вищий ККД", 13, MUTED, anchor="start"))

    # кутові підказки
    parts.append(text(150, 392, "дешево, кволо", 12, MUTED))
    parts.append(text(628, 108, "дорого, рекордно", 12, MUTED))

    # чипи-родини (textbox сам підганяє ширину під напис)
    chips = [
        (185, 345, "аморфний Si\n~10 %", MUTED, "#f0f1f3", False),
        (235, 255, "тонка плівка\nCdTe · CIGS\n~18–22 %", NEG, "#eaf0fd", False),
        (360, 205, "кристалічний Si\nмоно / полі · ~22 %", FIELD, "#e8f6ee", False),
        (485, 110, "перовскіт-\nтандем  >30 %", INK, "#f6f0fa", True),
        (630, 175, "III–V й\nбагатоперехідні\n29–47 %", POS, "#fdecea", False),
    ]
    for cx, cy, s, col, fillc, dashed in chips:
        stroke = col
        body, bw, bh = textbox(cx, cy, s, size=13, pad=11, fill=fillc,
                               stroke=stroke, sw=2.2, color=INK, rx=10)
        if dashed:
            # перемалювати рамку пунктиром (сигнал «ще дозріває»)
            body = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
                    'fill="%s" stroke="%s" stroke-width="2.2" stroke-dasharray="7,4"/>'
                    % (cx - bw / 2, cy - bh / 2, bw, bh, fillc, stroke)) + \
                   mtext(cx, cy - (len(s.split("\n")) - 1) * 13 * 1.3 / 2 + 13 * 0.35,
                         s.split("\n"), size=13, color=INK)
        parts.append(body)

    # позначка «робочий кінь» біля кристалічного кремнію
    parts.append(text(360, 240, "★ дев'ять із десяти панелей", 12, FIELD, bold=True))

    render(os.path.join(IMG, "family-map.svg"), w, h, *parts,
           title="Карта родин: що дорожче для вас — площа чи гроші")


def polygon(pts, fill, stroke="none", sw=0, opacity=1.0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    op = ' fill-opacity="%.2f"' % opacity if opacity < 1 else ''
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, fill, stroke, sw, op))


# ── Вставка «math-material-tradeoff»: дві протилежні тенденції та добуток ─────
def fig_tradeoff_curves():
    w, h = 840, 530
    x0, xR = 100, 750           # Eg: 0.6 … 2.0 еВ
    y0, yT = 430, 95            # нормована величина 0 … 1
    sx = (xR - x0) / (2.0 - 0.6)
    sy = (y0 - yT) / 1.0
    def X(eg): return x0 + (eg - 0.6) * sx
    def Y(v):  return y0 - v * sy

    egs = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    jsc = [66, 61, 57, 52, 49, 45, 41, 37, 33, 28, 24, 21, 18, 15.5, 13]
    voc = [max(eg - 0.4, 0.0) for eg in egs]
    prod = [voc[i] * jsc[i] for i in range(len(egs))]
    jmax, vmax, pmax = max(jsc), max(voc), max(prod)

    voc_px = [(X(egs[i]), Y(voc[i] / vmax)) for i in range(len(egs))]
    jsc_px = [(X(egs[i]), Y(jsc[i] / jmax)) for i in range(len(egs))]
    prod_px = [(X(egs[i]), Y(prod[i] / pmax)) for i in range(len(egs))]

    parts = []

    # заливка добутку (позаду всього)
    poly = list(prod_px) + [(X(2.0), y0), (X(0.6), y0)]
    parts.append(polygon(poly, "#e2f2e8"))

    # осі
    parts.append(line(x0, y0, xR + 10, y0, INK, 2.0))
    parts.append(line(x0, y0, x0, yT - 8, INK, 2.0))
    for eg in (0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        parts.append(line(X(eg), y0, X(eg), y0 + 5, INK, 1.5))
        parts.append(text(X(eg), y0 + 22, "%.1f" % eg, 12, MUTED))
    parts.append(text((x0 + xR) / 2, y0 + 44, "заборонена зона Eg, еВ", 14, MUTED))
    for v, lab in ((0.0, "0"), (0.5, "½"), (1.0, "макс")):
        parts.append(line(x0 - 5, Y(v), x0, Y(v), INK, 1.5))
        parts.append(text(x0 - 9, Y(v) + 4, lab, 11, MUTED, anchor="end"))
    parts.append(text(x0 - 4, yT - 9, "частка від макс.", 12, MUTED, anchor="start"))

    # криві
    parts.append(polyline(voc_px, NEG, sw=3))
    parts.append(polyline(jsc_px, POS, sw=3))
    parts.append(polyline(prod_px, FIELD, sw=3.6))

    # пік добутку
    parts.append(line(X(1.34), y0, X(1.34), Y(1.0), MUTED, 1.4, dash="5,4"))
    parts.append(text(X(1.34) + 10, 128, "пік Voc·Jsc", 13, INK, bold=True, anchor="start"))
    parts.append(text(X(1.34) + 10, 145, "~1.34 еВ", 12, INK, anchor="start"))

    # легенда (над полем)
    leg = [("Voc — напруга", NEG, 150), ("Jsc — струм", POS, 380),
           ("Voc·Jsc — потужність", FIELD, 560)]
    for lab, col, lx in leg:
        parts.append(line(lx, 54, lx + 30, 54, col, 4))
        parts.append(text(lx + 38, 58, lab, 13, INK, anchor="start"))

    # позначки матеріалів на осі + нижній ряд
    mats = [(1.12, "Si", INK), (1.42, "GaAs", FIELD), (1.50, "CdTe", NEG), (1.70, "a-Si", MUTED)]
    for eg, _, col in mats:
        tx = X(eg)
        parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                     % (tx, y0 - 7, tx - 6, y0 + 5, tx + 6, y0 + 5, col))
    row = [("Si 1.12", INK, 190), ("GaAs 1.42", FIELD, 330),
           ("CdTe 1.50", NEG, 490), ("a-Si 1.70", MUTED, 650)]
    for lab, col, lx in row:
        parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                     % (lx, 500, lx - 6, 511, lx + 6, 511, col))
        parts.append(text(lx + 12, 510, lab, 12, INK, anchor="start"))

    render(os.path.join(IMG, "tradeoff-curves.svg"), w, h, *parts,
           title="Напруга росте, струм падає — добуток має максимум")


# ── Вставка «math-material-tradeoff»: напруга проти стелі (нестача) ──────────
def fig_voltage_deficit():
    w, h = 860, 430
    xL = 175                   # ліва межа смуг (після підписів)
    xMax = 760                 # права межа шкали
    vspan = 1.8                # шкала напруги 0 … 1.8 В
    sx = (xMax - xL) / vspan
    def VX(v): return xL + v * sx

    rows = [  # (матеріал, Eg/q, Voc, нестача)
        ("Si",   1.12, 0.74, 0.38),
        ("GaAs", 1.42, 1.13, 0.29),
        ("CdTe", 1.50, 0.89, 0.61),
        ("a-Si", 1.70, 0.90, 0.80),
    ]
    yTop, bh, gap = 90, 42, 30
    parts = []

    # шкала напруги зверху
    for v in (0.0, 0.5, 1.0, 1.5):
        parts.append(line(VX(v), yTop - 14, VX(v), yTop + len(rows) * (bh + gap) - gap + 6,
                          "#e3e6ea", 1.2))
        parts.append(text(VX(v), yTop - 20, "%.1f" % v, 11, MUTED))
    parts.append(text((xL + xMax) / 2, 58, "напруга, В", 13, MUTED))

    for i, (name, eg, vc, wdef) in enumerate(rows):
        y = yTop + i * (bh + gap)
        # стеля Eg/q — вся смуга (світлий контур)
        parts.append(rect(xL, y, VX(eg) - xL, bh, fill="#f4f6f8", stroke=INK, sw=1.8, rx=4))
        # реальна Voc — зафарбована частина
        parts.append(rect(xL, y, VX(vc) - xL, bh, fill="#d6ecdf", stroke=FIELD, sw=2.2, rx=4))
        # підпис матеріалу зліва
        parts.append(text(xL - 16, y + bh / 2 + 5, name, 15, INK, bold=True, anchor="end"))
        # Voc у зафарбованій частині
        parts.append(text((xL + VX(vc)) / 2, y + bh / 2 + 5,
                          "Voc %.2f В" % vc, 12, INK))
        # нестача у світлому залишку
        wmid = (VX(vc) + VX(eg)) / 2
        parts.append(text(wmid, y + bh / 2 + 5, "−%.2f" % wdef, 12, MUTED))
        # стеля Eg/q праворуч
        parts.append(text(VX(eg) + 10, y + bh / 2 + 5,
                          "Eg/q = %.2f В" % eg, 12, MUTED, anchor="start"))

    # легенда внизу
    ly = yTop + len(rows) * (bh + gap) + 6
    parts.append(rect(xL, ly, 22, 14, fill="#d6ecdf", stroke=FIELD, sw=2, rx=3))
    parts.append(text(xL + 30, ly + 12, "реальна Voc", 12, INK, anchor="start"))
    parts.append(rect(xL + 165, ly, 22, 14, fill="#f4f6f8", stroke=INK, sw=1.6, rx=3))
    parts.append(text(xL + 195, ly + 12, "нестача (до стелі Eg/q)", 12, INK, anchor="start"))

    render(os.path.join(IMG, "voltage-deficit.svg"), w, h, *parts,
           title="Напруга проти стелі: нестача кожного матеріалу")


# ── Вставка «hist-material-lineage»: родовід матеріалів після кремнію ────────
def fig_material_lineage():
    w, h = 940, 560
    parts = []
    yA, yB, yC = 118, 300, 478
    xL, xR = 250, 918
    lanes = [
        (yA, POS,   "▲ ефективність за будь-яку ціну — космос"),
        (yB, NEG,   "◆ дешевизна за ват — тонка плівка"),
        (yC, FIELD, "▼ дешево і ефективно — перовскіт"),
    ]
    for y, col, cap in lanes:
        parts.append(text((xL + xR) / 2, y - 58, cap, 14, col, bold=True))

    # корінь: кремнієвий стовбур
    root, rw, rh = textbox(120, yB, "кремній\n1954\n(Bell Labs)", size=14, pad=12,
                           fill="#eef2f6", stroke=INK, sw=2.4, color=INK, bold=True, rx=10)
    # гілки від кореня до трьох доріжок (позаду чипа-кореня)
    parts.append(arrow(120 + rw / 2 - 4, yB - rh * 0.28, xL - 6, yA + 4, POS, 2.2))
    parts.append(arrow(120 + rw / 2 - 4, yB,             xL - 6, yB,     NEG, 2.2))
    parts.append(arrow(120 + rw / 2 - 4, yB + rh * 0.28, xL - 6, yC - 4, FIELD, 2.2))
    parts.append(root)

    def lane_line(y, items_extent):
        """Пунктир доріжки лише в ПРОМІЖКАХ між чипами — не крізь написи."""
        gaps = sorted(items_extent)
        cur = xL
        for gx0, gx1 in gaps:
            if gx0 - cur > 4:
                parts.append(line(cur, y, gx0, y, MUTED, 1.4, dash="3,5"))
            cur = max(cur, gx1)
        if xR - cur > 4:
            parts.append(line(cur, y, xR, y, MUTED, 1.4, dash="3,5"))

    def chiprow(y, col, fillc, items):
        extents = []
        boxes = []
        for cx, s in items:
            body, bw, bh = textbox(cx, y, s, size=13, pad=10, fill=fillc,
                                   stroke=col, sw=2.2, color=INK, rx=9)
            boxes.append(body)
            extents.append((cx - bw / 2 - 6, cx + bw / 2 + 6))
        lane_line(y, extents)
        parts.extend(boxes)

    chiprow(yA, POS, "#fdecea", [
        (330, "GaAs-гетероструктура\nАлфьоров ~1970"),
        (520, "«Луноход»\n1970 · 1973"),
        (700, "станція «Мир»\n1986"),
        (866, "III–V\nна супутниках"),
    ])
    chiprow(yB, NEG, "#eaf0fd", [
        (325, "CdTe · Боннет\n~1970"),
        (510, "CuInSe₂ · Bell\n1974"),
        (695, "аморфний Si\nRCA · 1976"),
        (866, "CdTe у мережі\nFirst Solar 1999"),
    ])
    chiprow(yC, FIELD, "#eef7f0", [
        (340, "перший перовскіт\nМіясака 2009"),
        (560, "твердотільний\nСнейт 2012"),
        (800, "перовскіт+Si тандем\n~35 % · 2025-26"),
    ])

    parts.append(text(w / 2, h - 16, "час  →", 13, MUTED, bold=True))
    render(os.path.join(IMG, "material-lineage.svg"), w, h, *parts,
           title="Родовід матеріалів після кремнію: три сили — три гілки")


# ── Вставка «hist-material-lineage»: два кінці одного десятиліття ────────────
def fig_two_extremes():
    w, h = 840, 400
    parts = []

    lx, ly, lw, lh = 55, 74, 330, 252
    parts.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2.4, rx=12))
    parts.append(text(lx + lw / 2, ly + 34, "Місяць: GaAs", 16, POS, bold=True))
    left_lines = ["• кіловати на орбіту", "• виживає в радіації",
                  "• «Луноход» 1970-73", "• станція «Мир» 1986", "• ціна — байдужа"]
    parts.append(mtext(lx + 26, ly + 74, left_lines, size=14, color=INK,
                       anchor="start", lh=1.5))

    rx, ry, rw2, rh2 = 455, 74, 330, 252
    parts.append(rect(rx, ry, rw2, rh2, fill="#eaf0fd", stroke=NEG, sw=2.4, rx=12))
    parts.append(text(rx + rw2 / 2, ry + 34, "Кишеня: аморфний Si", 16, NEG, bold=True))
    right_lines = ["• мілівати в руці", "• живе на слабкому світлі",
                   "• Sanyo «Amorton» ~1980", "• калькулятори, годинники",
                   "• важить лише дешевизна"]
    parts.append(mtext(rx + 26, ry + 74, right_lines, size=14, color=INK,
                       anchor="start", lh=1.5))

    parts.append(text(w / 2, 204, "проти", 15, MUTED, bold=True))
    parts.append(text(w / 2, 372, "різна нестача  →  діаметрально різний матеріал",
                      14, FIELD, bold=True))
    render(os.path.join(IMG, "two-extremes.svg"), w, h, *parts,
           title="Два кінці одного десятиліття: Місяць і кишеня")


if __name__ == "__main__":
    fig_bandgap_efficiency()
    fig_direct_indirect()
    fig_family_map()
    fig_tradeoff_curves()
    fig_voltage_deficit()
    fig_material_lineage()
    fig_two_extremes()
    print("ok: bandgap-efficiency, direct-indirect, family-map, "
          "tradeoff-curves, voltage-deficit, material-lineage, two-extremes")
