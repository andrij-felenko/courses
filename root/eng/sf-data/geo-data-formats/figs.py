# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F = "#eef4ff"
RED_F = "#fdecea"
GREEN_F = "#eaf7ef"
GREY_F = "#f4f6f8"


# ── three-questions: три формати народилися з трьох різних питань ────────────
def fig_three_questions():
    W, H = 960, 470
    p = []
    cols = [
        (30, "GPX", "TopoGrafix, 2002", NEG, BLUE_F,
         "«де я був\nі коли?»",
         "trk → trkseg → trkpt\nlat, lon як атрибути\nele · time · hdop · sat",
         "немає полігонів,\nнемає стилю показу,\nвластивості — лише\nчерез extensions"),
        (346, "KML", "Keyhole → Google, 2004\nстандарт OGC, 2008", FIELD, GREEN_F,
         "«що показати\nй як?»",
         "Placemark + Style\n<coordinates> одним рядком\naltitudeMode · Folder",
         "немає компактності,\nвластивості нетипізовані,\nформат прив'язаний\nдо земного браузера"),
        (662, "GeoJSON", "чернетка 2008\nRFC 7946, 2016", POS, RED_F,
         "«які об'єкти\nі з якими\nвластивостями?»",
         "FeatureCollection →\nFeature { geometry,\nproperties, id }",
         "немає стилю,\nнемає часу на точку,\nінша система координат\nзаборонена"),
    ]
    cw = 268
    for x, name, origin, col, fill, question, core, gap in cols:
        p.append(fitbox(x, 54, cw, 66, name + "\n" + origin, size=14,
                        fill=fill, stroke=col, sw=2.2, bold=True))
        p.append(fitbox(x, 140, cw, 76, question, size=15,
                        fill=BG, stroke=col, sw=1.6, color=col, bold=True))
        p.append(fitbox(x, 236, cw, 96, core, size=12,
                        fill=GREY_F, stroke=LINE, sw=1.4))
        p.append(fitbox(x, 352, cw, 96, gap, size=12,
                        fill=BG, stroke=MUTED, sw=1.2, color=MUTED))
    render(os.path.join(OUT, "three-questions.svg"), W, H, *p,
           title="Три формати — три різні питання про те саме місце")


# ── height-datums: над чим саме рахують третє число ──────────────────────────
def fig_height_datums():
    W, H = 940, 520
    p = []
    x_left, x_right = 60, 700
    y_ell = 268          # еліпсоїд
    # еліпсоїд — рівна лінія
    p.append(line(x_left, y_ell, x_right, y_ell, color=NEG, sw=2.4))
    # геоїд — м'яка хвиля над еліпсоїдом
    geoid = []
    import math
    for i in range(0, 33):
        gx = x_left + (x_right - x_left) * i / 32.0
        gy = y_ell - 34 + 11 * math.sin(i / 32.0 * 3.6 * math.pi)
        geoid.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(geoid), FIELD))
    # рельєф — ламана вище
    ter = [(60, 190), (140, 168), (220, 196), (300, 156), (380, 178),
           (460, 142), (540, 166), (620, 150), (700, 182)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%d,%d" % t for t in ter), "#8a5a2b"))

    # підписи ліній — праворуч від малюнка, з великим запасом
    p.append(text(724, 150, "рельєф", size=13, color="#8a5a2b", anchor="start"))
    p.append(text(724, 234, "геоїд — рівень моря", size=13, color=FIELD, anchor="start"))
    p.append(text(724, 272, "еліпсоїд WGS-84", size=13, color=NEG, anchor="start"))

    # точка на рельєфі
    px, py = 460, 142
    p.append(circle(px, py, 6, fill=POS, stroke=POS, sw=1.5))
    p.append(text(px, py - 16, "точка вимірювання", size=12, color=POS))
    p.append(line(300, py, 620, py, color=MUTED, sw=1.2, dash="5,5"))

    # три мірні лінії з підписами під різними x
    def measure(x, y1, y2, label, color):
        out = line(x, y1, x, y2, color=color, sw=2.0)
        out += line(x - 5, y1, x + 5, y1, color=color, sw=1.6)
        out += line(x - 5, y2, x + 5, y2, color=color, sw=1.6)
        out += text(x + 10, (y1 + y2) / 2 + 5, label, size=14,
                    color=color, anchor="start", bold=True)
        return out

    y_geoid_at = y_ell - 34 + 11 * math.sin(((460 - 60) / 640.0) * 3.6 * math.pi)
    p.append(measure(330, py, y_ell, "h", NEG))
    p.append(measure(420, py, y_geoid_at, "H", FIELD))
    p.append(measure(560, y_geoid_at, y_ell, "N", MUTED))

    p.append(text(x_left, 320, "h — над еліпсоїдом · H — над геоїдом (рівнем моря) · N — хвиля геоїда, h = H + N",
                  size=13, color=INK, anchor="start"))

    # три легенди-картки
    cw = 288
    p.append(fitbox(30, 348, cw, 122,
                    "GeoJSON\n\nтретій елемент координати —\nвисота над еліпсоїдом WGS-84,\nтобто h. Так велить RFC 7946.",
                    size=12, fill=RED_F, stroke=POS, sw=1.8))
    p.append(fitbox(336, 348, cw, 122,
                    "KML, altitudeMode=absolute\n\nвисота над рівнем моря,\nу Google Earth — над геоїдом\nEGM96, тобто H.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))
    p.append(fitbox(642, 348, cw, 122,
                    "GPX <ele>\n\n«висота в метрах» — над чим,\nсхема не каже. Окремий\n<geoidheight> дає N.",
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.8))
    render(os.path.join(OUT, "height-datums.svg"), W, H, *p,
           title="Третє число координати: над чим його рахують")


# ── geojson-nesting: обгортки й глибина квадратних дужок ─────────────────────
def fig_geojson_nesting():
    W, H = 960, 500
    p = []
    # ліва колонка — ланцюг обгорток
    cx = 230
    chain = [
        (70, "FeatureCollection\nfeatures: [ … ]", RED_F, POS),
        (154, "Feature\ngeometry · properties · id", GREY_F, LINE),
        (238, "Geometry\ntype + coordinates", GREY_F, LINE),
        (322, "Position\n[ довгота, широта, (висота) ]", BLUE_F, NEG),
    ]
    for y, label, fill, col in chain:
        p.append(fitbox(cx - 190, y, 380, 60, label, size=13, fill=fill, stroke=col, sw=1.8))
    for y in (130, 214, 298):
        p.append(arrow(cx, y, cx, y + 22, color=MUTED, sw=1.8))
    p.append(text(cx, 410, "кожен рівень — окремий об'єкт JSON", size=12, color=MUTED))

    # права колонка — глибина вкладення coordinates
    lx, rw = 500, 430
    p.append(text(lx + rw / 2, 62, "глибина дужок у coordinates", size=13, bold=True))
    rows = [
        ("Point", "[ x, y ]"),
        ("LineString, MultiPoint", "[ [ x, y ], … ]"),
        ("Polygon, MultiLineString", "[ [ [ x, y ], … ], … ]"),
        ("MultiPolygon", "[ [ [ [ x, y ], … ] ] ]"),
    ]
    for i, (name, br) in enumerate(rows):
        y = 78 + i * 52
        p.append(rect(lx, y, rw, 44, fill=GREY_F, stroke=LINE, sw=1.2, rx=5))
        p.append(text(lx + 14, y + 28, name, size=12, anchor="start"))
        p.append(text(lx + rw - 14, y + 28, br, size=12, color=NEG, anchor="end"))
    p.append(mtext(lx + rw / 2, 306, ["GeometryCollection тримає не coordinates,",
                                      "а масив geometries"], size=12, color=MUTED))

    # нижня рамка — правило кілець
    p.append(fitbox(30, 424, 900, 62,
                    "Кільця полігона: перше — зовнішнє, проти годинникової; наступні — дірки, за годинниковою. "
                    "Перша й остання позиція кільця збігаються.",
                    size=13, fill=GREEN_F, stroke=FIELD, sw=1.8))
    render(os.path.join(OUT, "geojson-nesting.svg"), W, H, *p,
           title="Будова GeoJSON: обгортки й глибина масивів")


# ── conversion-loss: що переживає перетворення, а що ні ──────────────────────
def fig_conversion_loss():
    W, H = 940, 500
    p = []
    lab_w = 400
    x0 = 24
    col_w = 164
    cols_x = [x0 + lab_w + 6, x0 + lab_w + 6 + col_w + 8, x0 + lab_w + 6 + 2 * (col_w + 8)]
    names = ["GPX", "KML", "GeoJSON"]
    colors = [NEG, FIELD, POS]

    y_head = 56
    p.append(rect(x0, y_head, lab_w, 44, fill=BG, stroke=BG, sw=0))
    p.append(text(x0 + 8, y_head + 28, "шар відомостей", size=13, bold=True, anchor="start"))
    for i, nm in enumerate(names):
        p.append(fitbox(cols_x[i], y_head, col_w, 44, nm, size=14, bold=True,
                        fill=GREY_F, stroke=colors[i], sw=2.0, color=colors[i]))

    rows = [
        ("полігон з дірками", "ні", "так", "так"),
        ("довільні властивості об'єкта", "частково", "частково", "так"),
        ("час на кожній точці", "так", "частково", "ні"),
        ("якість фіксу: HDOP, супутники", "так", "ні", "ні"),
        ("стиль показу: колір, іконка", "ні", "так", "ні"),
        ("явна база висоти", "ні", "так", "так"),
        ("розрив запису на сегменти", "так", "частково", "ні"),
    ]
    fills = {"так": (GREEN_F, FIELD), "ні": (RED_F, POS), "частково": (GREY_F, MUTED)}
    y = y_head + 52
    for label, a, b, c in rows:
        p.append(rect(x0, y, lab_w, 44, fill=BG, stroke="#e2e6ea", sw=1.0, rx=4))
        p.append(text(x0 + 8, y + 28, label, size=12, anchor="start"))
        for i, v in enumerate((a, b, c)):
            fill, col = fills[v]
            p.append(fitbox(cols_x[i], y, col_w, 44, v, size=12,
                            fill=fill, stroke=col, sw=1.3, color=col))
        y += 52

    p.append(text(W / 2, y + 26,
                  "Перетворення форматів губить рівно ті шари, яких немає в цілі.",
                  size=13, color=INK))
    render(os.path.join(OUT, "conversion-loss.svg"), W, H, *p,
           title="Що переживає перетворення між форматами")


# ── births-timeline: хронологія трьох народжень (вставка hist) ───────────────
def fig_births_timeline():
    W, H = 960, 780
    p = []
    col_x = [150, 420, 690]
    col_w = 252
    heads = [("GPX", NEG, BLUE_F), ("KML", FIELD, GREEN_F), ("GeoJSON", POS, RED_F)]

    for i, (nm, col, fill) in enumerate(heads):
        p.append(fitbox(col_x[i], 34, col_w, 46, nm, size=15, bold=True,
                        fill=fill, stroke=col, sw=2.2, color=col))

    rows = [
        ("кінець 2001", 0, "список розсилки розробників\nGPS-програм (дата — за\nвторинними джерелами)"),
        ("2002", 0, "GPX 1.0 — спільний XML\nзамість форматів приладів"),
        ("9 серп. 2004", 0, "GPX 1.1 — сувора схема\nй окремий <extensions>"),
        ("2004", 1, "Google купує Keyhole Inc.\nразом з EarthViewer"),
        ("бер. 2007", 2, "заведено список розсилки\nGeoJSON"),
        ("лист. 2007", 1, "робоча група KML 2.2\nв OGC"),
        ("14 квіт. 2008", 1, "KML 2.2 — стандарт OGC\n(07-147r2)"),
        ("16 черв. 2008", 2, "чернетка GeoJSON 1.0\n(шість авторів)"),
        ("4 серп. 2015", 1, "KML 2.3 — стандарт OGC\n(12-007r2)"),
        ("жовт. 2015", 2, "робота переходить\nу робочу групу IETF"),
        ("серп. 2016", 2, "RFC 7946 — вибір системи\nкоординат прибрано"),
    ]

    y = 100
    step = 60
    box_h = 50
    for label, ci, textv in rows:
        p.append(text(122, y + box_h / 2 + 5, label, size=12,
                      color=MUTED, anchor="end"))
        col = heads[ci][1]
        p.append(fitbox(col_x[ci], y, col_w, box_h, textv, size=11,
                        fill=BG, stroke=col, sw=1.6))
        y += step

    p.append(text(W / 2, y + 24,
                  "Кожен формат виріс із власної незручності — і зберіг її сліди в структурі.",
                  size=13, color=INK))
    render(os.path.join(OUT, "births-timeline.svg"), W, H, *p,
           title="Хронологія: як з'явилися GPX, KML і GeoJSON")


# ── precision-ladder: усі кроки сітки й шуми на одній логарифмічній осі ──────
def fig_precision_ladder():
    import math as _m
    W, H = 1240, 620
    p = []
    x0, x1 = 96, 1156          # межі осі
    y_ax = 322                 # сама вісь
    lo, hi = -10.0, 3.0        # декади: від 10⁻¹⁰ м до 10³ м

    def X(v):
        return x0 + (_m.log10(v) - lo) / (hi - lo) * (x1 - x0)

    # вісь із декадними мітками (підписи — НАД віссю, у смузі без виносок;
    # мітку пропускаємо, якщо поруч виносить підпис верхній маркер)
    p.append(line(x0 - 26, y_ax, x1 + 26, y_ax, color=INK, sw=2.4))
    up_marks = [0.02, 3.0, 100.0]
    dec_lab = {-10: "0.1 нм", -9: "1 нм", -6: "1 мкм", -3: "1 мм",
               -2: "1 см", -1: "10 см", 0: "1 м", 1: "10 м", 2: "100 м", 3: "1 км"}
    for d in range(-10, 4):
        xd = X(10.0 ** d)
        p.append(line(xd, y_ax - 7, xd, y_ax + 7, color=MUTED, sw=1.2))
        if d in dec_lab and all(abs(xd - X(v)) > 20 for v in up_marks):
            p.append(text(xd, y_ax - 18, dec_lab[d], size=11, color=MUTED))

    # ярусне розкладання підписів, щоб сусідні не наїжджали один на одного
    def place(items, up):
        rows, out = [], []
        for v, lab, col, fill in sorted(items, key=lambda t: t[0]):
            xv = X(v)
            lines = lab.split("\n")
            bw = max(text_width(s, 12) for s in lines) + 22
            bh = len(lines) * 16 + 16
            k = 0
            while k < len(rows) and rows[k] > xv - bw / 2 - 14:
                k += 1
            if k == len(rows):
                rows.append(0.0)
            rows[k] = xv + bw / 2
            # тримаємо підпис у полі малюнка
            bx = min(max(xv - bw / 2, 10), W - bw - 10)
            gap = 52 + k * (bh + 16)
            by = y_ax - gap - bh if up else y_ax + gap
            p.append(line(xv, y_ax + (-10 if up else 10),
                          xv, (by + bh) if up else by, color=col, sw=1.4, dash="4 3"))
            p.append(circle(xv, y_ax, 5.0, fill=fill, stroke=col, sw=2.0))
            out.append(fitbox(bx, by, bw, bh, lab, size=12,
                              fill=fill, stroke=col, sw=1.6, color=col))
        return out

    # ↑ над віссю — фізичний шум вимірювання, який ми НЕ контролюємо
    p += place([
        (0.02,  "шум RTK\n≈ 2 см",            FIELD, GREEN_F),
        (3.0,   "побутовий приймач\n≈ 3 м",   FIELD, GREEN_F),
        (100.0, "чужий датум\n≈ 100 м",       FIELD, GREEN_F),
    ], up=True)

    # ↓ під віссю — кроки сітки запису, які ми обираємо самі
    p += place([
        (7.9e-10, "ulp float64\n0.8 нм",          NEG,  BLUE_F),
        (1.11e-3, "8 знаків\n1.1 мм",             MUTED, GREY_F),
        (1.11e-2, "7 знаків\n1.1 см",             MUTED, GREY_F),
        (1.11e-1, "6 знаків\n11 см",              MUTED, GREY_F),
        (0.424,   "ulp float32\n42 см",           POS,  RED_F),
        (1.11,    "5 знаків\n1.1 м",              MUTED, GREY_F),
        (11.1,    "4 знаки\n11 м",                MUTED, GREY_F),
        (111.0,   "3 знаки\n111 м",               MUTED, GREY_F),
        (400.0,   "TopoJSON, світ,\nn = 10⁵ → 400 м", POS, RED_F),
    ], up=False)

    p.append(text(W / 2, H - 26,
                  "Крок запису має бути помітно дрібнішим за шум вимірювання — "
                  "але дрібніти без межі немає сенсу.", size=13, color=INK))
    render(os.path.join(OUT, "precision-ladder.svg"), W, H, *p,
           title="Кроки сітки та шуми вимірювання на широті 50° (логарифмічна вісь, метри)")


# ── quantization-deltas: округлення на сітку і чому різниці не накопичують ────
def fig_quantization_deltas():
    W, H = 1180, 620
    p = []
    gx0, gy0, step = 92, 118, 62
    ncol, nrow = 7, 6

    # сітка кроку q
    for i in range(ncol):
        p.append(line(gx0 + i * step, gy0, gx0 + i * step, gy0 + (nrow - 1) * step,
                      color="#dfe4ea", sw=1.0))
    for j in range(nrow):
        p.append(line(gx0, gy0 + j * step, gx0 + (ncol - 1) * step, gy0 + j * step,
                      color="#dfe4ea", sw=1.0))

    p.append(text(gx0 + (ncol - 1) * step / 2, gy0 - 44,
                  "справжні координати  →  найближчий вузол сітки", size=13, bold=True))
    # позначка кроку q
    p.append(line(gx0, gy0 + (nrow - 1) * step + 30, gx0 + step,
                  gy0 + (nrow - 1) * step + 30, color=INK, sw=1.6))
    p.append(line(gx0, gy0 + (nrow - 1) * step + 24, gx0, gy0 + (nrow - 1) * step + 36,
                  color=INK, sw=1.6))
    p.append(line(gx0 + step, gy0 + (nrow - 1) * step + 24, gx0 + step,
                  gy0 + (nrow - 1) * step + 36, color=INK, sw=1.6))
    p.append(text(gx0 + step / 2, gy0 + (nrow - 1) * step + 52, "q", size=14, bold=True))

    true_pts = [(0.62, 4.38), (2.28, 3.15), (3.78, 3.62), (5.34, 1.78), (6.42, 0.55)]
    snap_pts = [(round(a), round(b)) for a, b in true_pts]

    def P(u, v):
        return gx0 + u * step, gy0 + v * step

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-dasharray="6 4"/>'
             % (" ".join("%.1f,%.1f" % P(u, v) for u, v in true_pts), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % P(u, v) for u, v in snap_pts), NEG))

    # клітинка притягання навколо одного вузла
    su, sv = snap_pts[2]
    cx, cy = P(su, sv)
    p.append(rect(cx - step / 2, cy - step / 2, step, step,
                  fill="none", stroke=FIELD, sw=2.0, rx=3))

    for (tu, tv), (su2, sv2) in zip(true_pts, snap_pts):
        tx, ty = P(tu, tv)
        sx, sy = P(su2, sv2)
        p.append(line(tx, ty, sx, sy, color=MUTED, sw=1.4))
        p.append(circle(sx, sy, 6.0, fill=BLUE_F, stroke=NEG, sw=2.2))
        p.append(circle(tx, ty, 4.0, fill=RED_F, stroke=POS, sw=1.8))

    p.append(fitbox(gx0 - 12, gy0 + (nrow - 1) * step + 72, 486, 68,
                    "Зелена клітинка сторони q: усі її точки дають той самий вузол.\n"
                    "Звідси |похибка| ≤ q/2 по кожній осі — хоч скільки точок у лінії.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.6))

    # права колонка: цілі індекси, різниці, часткові суми
    tx0, tw = 620, 500
    hdr = ["точка", "індекс (i, j)", "різниця Δ", "сума ⇒ індекс"]
    cw = [86, 132, 132, 150]
    y = gy0 - 30
    xx = tx0
    for k, hname in enumerate(hdr):
        p.append(fitbox(xx, y, cw[k], 40, hname, size=12, bold=True,
                        fill=GREY_F, stroke=LINE, sw=1.4))
        xx += cw[k] + 6
    y += 48
    acc = None
    for idx, (su2, sv2) in enumerate(snap_pts):
        if acc is None:
            d = "(%d, %d) — абсолютні" % (su2, sv2)
            acc = (su2, sv2)
        else:
            d = "(%+d, %+d)" % (su2 - acc[0], sv2 - acc[1])
            acc = (su2, sv2)
        cells = ["P%d" % idx, "(%d, %d)" % (su2, sv2), d, "(%d, %d)" % acc]
        xx = tx0
        for k, cval in enumerate(cells):
            p.append(fitbox(xx, y, cw[k], 40, cval, size=12,
                            fill=BG if k else BLUE_F,
                            stroke=LINE if k else NEG, sw=1.2))
            xx += cw[k] + 6
        y += 46

    p.append(fitbox(tx0, y + 16, tw, 96,
                    "Різниці — цілі числа. Часткові суми цілих у float64 точні,\n"
                    "поки |сума| < 2⁵³, а індекси не більші за n − 1.\n"
                    "Тому відновлені індекси збігаються з початковими біт у біт:\n"
                    "похибка точки P_k — лише її власне округлення, не сума попередніх.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "quantization-deltas.svg"), W, H, *p,
           title="Квантування на цілочислову сітку й різницеве кодування")


# ── stream-and-memory: куди дівається пам'ять у потоковому перетворювачі ─────
def fig_stream_and_memory():
    W, H = 1000, 580
    p = []

    # верхній ряд: конвеєр
    y1, h1 = 58, 84
    stages = [
        (24, 200, "GPX на диску\n200 МБ\n1.5 млн точок", BLUE_F, NEG),
        (262, 186, "буфер читання\n64 КіБ\nсталий", GREY_F, LINE),
        (496, 214, "expat\nподії start · text · end\nдерева НЕ будує", GREEN_F, FIELD),
        (758, 218, "stdout\nGeoJSON тече вперед\nі не переписується", RED_F, POS),
    ]
    for x, w, label, fill, col in stages:
        p.append(fitbox(x, y1, w, h1, label, size=13, fill=fill, stroke=col, sw=1.9))
    for x1, x2 in ((224, 258), (448, 492), (710, 754)):
        p.append(arrow(x1, y1 + h1 / 2, x2, y1 + h1 / 2, color=MUTED, sw=1.8))

    # середній ряд: що лежить у пам'яті
    y2, h2 = 182, 206
    p.append(rect(24, y2, 460, h2, fill=BG, stroke=LINE, sw=1.6, rx=6))
    p.append(text(254, y2 + 28, "стала пам'ять розбору", size=14, bold=True, color=INK))
    const_rows = [
        "поточна точка trkpt — близько 180 Б",
        "одна відкладена точка — стільки ж",
        "назва треку — до 512 Б",
        "текст поточного вузла — 128 Б",
        "глибини trk · trkseg · trkpt — три числа",
    ]
    for i, r in enumerate(const_rows):
        p.append(text(46, y2 + 60 + i * 25, "· " + r, size=12, color=INK, anchor="start"))
    p.append(text(46, y2 + 192, "разом близько кілобайта — від розміру файлу не залежить",
                  size=12, color=FIELD, anchor="start", bold=True))

    p.append(rect(516, y2, 460, h2, fill=BG, stroke=POS, sw=1.6, rx=6))
    p.append(text(746, y2 + 28, "єдине, що росте", size=14, bold=True, color=POS))
    grow_rows = [
        "буфер часів для properties",
        "«2026-04-18T07:12:03Z», — 23 Б на точку",
        "1.5 млн точок — приблизно 35 МБ",
        "скидається на кінці кожного <trk>",
        "прапорець --no-times прибирає й це",
    ]
    for i, r in enumerate(grow_rows):
        p.append(text(538, y2 + 60 + i * 25, "· " + r, size=12, color=INK, anchor="start"))
    p.append(text(538, y2 + 192, "час живе в properties — сусіді geometry, а не в ній",
                  size=12, color=MUTED, anchor="start"))

    # нижній ряд: чим це відрізняється від дерева
    y3, h3 = 424, 116
    p.append(fitbox(24, y3, 460, h3,
                    "ДЕРЕВО В ПАМ'ЯТІ\n\nкожен вузол — окрема структура з покажчиками;\n"
                    "пікова пам'ять у кілька разів більша за файл",
                    size=12, fill=RED_F, stroke=POS, sw=1.8))
    p.append(fitbox(516, y3, 460, h3,
                    "ПОТІК ПОДІЙ\n\nстала пам'ять плюс 23 Б на точку;\n"
                    "вхід читається рівно раз, вихід пишеться рівно раз",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))

    p.append(text(W / 2, 562,
                  "Файл, більший за пам'ять, не проблема, поки нічого не треба тримати цілим.",
                  size=13, color=INK))
    render(os.path.join(OUT, "stream-and-memory.svg"), W, H, *p,
           title="Потоковий перетворювач: де саме витрачається пам'ять")


# ── conversion-decisions: що GPX не каже, а GeoJSON вимагає ──────────────────
def fig_conversion_decisions():
    W, H = 1000, 604
    p = []
    x0, c1, c2, c3 = 24, 250, 250, 420
    gap = 8
    xa, xb, xc = x0, x0 + c1 + gap, x0 + c1 + c2 + 2 * gap

    p.append(fitbox(xa, 52, c1, 42, "що дає GPX", size=13, bold=True,
                    fill=BLUE_F, stroke=NEG, sw=1.9, color=NEG))
    p.append(fitbox(xb, 52, c2, 42, "чого вимагає GeoJSON", size=13, bold=True,
                    fill=RED_F, stroke=POS, sw=1.9, color=POS))
    p.append(fitbox(xc, 52, c3, 42, "рішення перетворювача", size=13, bold=True,
                    fill=GREEN_F, stroke=FIELD, sw=1.9, color=FIELD))

    rows = [
        ("<ele> без бази відліку",
         "третє число — над\nеліпсоїдом WGS-84",
         "є <geoidheight> → пишемо h = ele + N;\nнемає → координата лишається двовимірною"),
        ("точка без <time>",
         "масив часів має збігатися\nдовжиною з масивом точок",
         "у масив іде null, а не пропуск —\nінакше зсунуться всі наступні"),
        ("<trkseg> з нуля\nабо однієї точки",
         "LineString — щонайменше\nдві позиції",
         "сегмент викидаємо, а лічильник\nвикинутих кладемо в properties"),
        ("GPX 1.0 і GPX 1.1 —\nрізні простори імен",
         "формату байдуже,\nяк улаштований XML",
         "звіряємо локальне ім'я тега,\nпростір імен свідомо ігноруємо"),
        ("<extensions> — чужі теги\nз довільними іменами",
         "нічого; вони просто\nне мають куди подітися",
         "усередині extensions не бачимо нічого,\nщоб чужий <time> не став нашим"),
        ("трек без <name>",
         "properties — довільний\nоб'єкт, назва не обов'язкова",
         "пишемо \"name\": null,\nа не вигадуємо назву з імені файлу"),
    ]
    y, rh, step = 106, 70, 78
    for a, b, c in rows:
        p.append(fitbox(xa, y, c1, rh, a, size=12, fill=BG, stroke=NEG, sw=1.3))
        p.append(fitbox(xb, y, c2, rh, b, size=12, fill=BG, stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(xc, y, c3, rh, c, size=12, fill=GREEN_F, stroke=FIELD, sw=1.4))
        y += step

    p.append(text(W / 2, y + 26,
                  "Кожне рішення в правій колонці — домисел. Тому кожне лишає слід у properties.",
                  size=13, color=INK))
    render(os.path.join(OUT, "conversion-decisions.svg"), W, H, *p,
           title="Шість місць, де перетворювач мусить вирішувати сам")


fig_three_questions()
fig_births_timeline()
fig_height_datums()
fig_geojson_nesting()
fig_conversion_loss()
fig_precision_ladder()
fig_quantization_deltas()
fig_stream_and_memory()
fig_conversion_decisions()
print("ok")
