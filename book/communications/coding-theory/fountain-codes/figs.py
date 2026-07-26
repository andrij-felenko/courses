# -*- coding: utf-8 -*-
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SRCFILL = "#eafaf0"   # блок-джерело (variable)
SRCSTRK = "#27ae60"
DRPFILL = "#eef4ff"   # крапля (encoded)
DRPSTRK = "#2457d6"
HOTFILL = "#fdecea"   # виділене — степінь 1 / щойно відкрите
HOTSTRK = "#c0392b"
DONEFILL = "#eef0f2"  # спожите / уже зняте
DONESTRK = "#aeb6c0"


# ── fountain: нескінченний потік крапель, будь-які ~k відновлюють ──────────────

def fig_fountain():
    W, H = 940, 500
    p = []

    # --- файл: k блоків ---
    fx, fy0 = 62, 92
    labels = ["a", "b", "c", "d"]
    p.append(text(fx + 34, fy0 - 16, "файл: k блоків", size=13, color=SRCSTRK, bold=True))
    for i, lab in enumerate(labels):
        y = fy0 + i * 34
        p.append(rect(fx, y, 68, 28, fill=SRCFILL, stroke=SRCSTRK, sw=1.8, rx=5))
        p.append(text(fx + 34, y + 19, lab, size=14, color=SRCSTRK, bold=True))

    # --- кодер ---
    ex = 196
    box, bw, bh = textbox(ex + 30, fy0 + 2 * 34, "кодер", size=14, bold=True,
                          fill="#f6f4ec", stroke=INK, sw=1.8, pad=14)
    p.append(box)
    p.append(arrow(fx + 74, fy0 + 2 * 34, ex + 30 - bw / 2 - 6, fy0 + 2 * 34, sw=2.0))

    # --- нескінченний потік крапель ---
    sy = fy0 + 2 * 34
    sx0, sx1 = ex + 30 + bw / 2 + 26, W - 96
    p.append(arrow(sx0 - 8, sy, sx1 + 30, sy, color=DRPSTRK, sw=2.2))
    n = 9
    dxs = [sx0 + i * (sx1 - sx0) / (n - 1) for i in range(n)]
    for i, dx in enumerate(dxs):
        p.append(circle(dx, sy, 15, fill=DRPFILL, stroke=DRPSTRK, sw=2.0))
        p.append(text(dx, sy + 5, str(i + 1), size=12, color=DRPSTRK, bold=True))
    p.append(text(sx1 + 44, sy + 6, "…", size=26, color=DRPSTRK, bold=True))
    p.append(text((sx0 + sx1) / 2, sy - 30, "нескінченний потік крапель", size=12.5,
                  color=DRPSTRK, italic=True))

    # --- два приймачі, кожен зі СВОЄЮ підбіркою ---
    def receiver(cy, name, caught):
        out = [text(120, cy + 5, name, size=13, color=INK, bold=True, anchor="middle")]
        x0 = 210
        for k, idx in enumerate(caught):
            cx = x0 + k * 58
            out.append(circle(cx, cy, 15, fill=DRPFILL, stroke=DRPSTRK, sw=2.0))
            out.append(text(cx, cy + 5, str(idx), size=12, color=DRPSTRK, bold=True))
        ax = x0 + len(caught) * 58 + 6
        out.append(arrow(ax, cy, ax + 52, cy, sw=2.0))
        b, w, h = textbox(ax + 52 + 92, cy, "усі k блоків ✓", size=12.5, bold=True,
                          fill=SRCFILL, stroke=SRCSTRK, sw=2.0, pad=11)
        out.append(b)
        return out

    p.append(text(W / 2, 300, "різні приймачі ловлять РІЗНІ краплі — і кожен збирає той самий файл",
                  size=12.5, color=MUTED, italic=True))
    p.extend(receiver(356, "приймач A", [1, 3, 4, 6, 8]))
    p.extend(receiver(424, "приймач B", [2, 3, 5, 7, 9]))

    box, bw, bh = textbox(W / 2, H - 34,
                          "Відправник не знає, хто що загубив. Кожен ловить будь-які ~k крапель — і збирає файл; котрі саме, байдуже.",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "fountain.svg"), W, H, *p,
           title="Безшвидкісний код: один нескінченний потік, будь-які ~k крапель відновлюють файл")


# ── encode: двочастковий граф — крапля = XOR жменьки блоків ───────────────────

SRC = ["a", "b", "c"]                              # k = 3
# кожна крапля: список індексів джерел, що в неї злиті
DROPS = [
    ("p1", [1]),          # b
    ("p2", [0, 1]),       # a⊕b
    ("p3", [2]),          # c
    ("p4", [0, 1, 2]),    # a⊕b⊕c
    ("p5", [0, 2]),       # a⊕c
]


def _content(idxs):
    return " ⊕ ".join(SRC[j] for j in idxs)


def fig_encode():
    W, H = 900, 470
    p = []

    sx0, sx1 = 220, 680
    vy, dy = 108, 300
    NS, ND = len(SRC), len(DROPS)
    vx = [sx0 + i * (sx1 - sx0) / (NS - 1) for i in range(NS)]
    dgx0, dgx1 = 120, W - 120
    dx = [dgx0 + j * (dgx1 - dgx0) / (ND - 1) for j in range(ND)]

    # ребра спершу
    for j, (_, idxs) in enumerate(DROPS):
        for i in idxs:
            p.append(line(vx[i], vy + 20, dx[j], dy - 24, color="#c2c8d0", sw=1.6))

    # джерела (кружки)
    p.append(text(sx0 - 80, vy + 5, "блоки", size=12, color=SRCSTRK, italic=True, anchor="start"))
    for i, lab in enumerate(SRC):
        p.append(circle(vx[i], vy, 20, fill=SRCFILL, stroke=SRCSTRK, sw=2.2))
        p.append(text(vx[i], vy + 6, lab, size=15, color=SRCSTRK, bold=True))

    # краплі (квадрати) з підписами
    p.append(text(dgx0 - 92, dy + 5, "краплі", size=12, color=DRPSTRK, italic=True, anchor="start"))
    for j, (name, idxs) in enumerate(DROPS):
        deg = len(idxs)
        hot = (deg == 1)
        p.append(rect(dx[j] - 22, dy - 22, 44, 44, fill=HOTFILL if hot else DRPFILL,
                      stroke=HOTSTRK if hot else DRPSTRK, sw=2.4, rx=6))
        p.append(text(dx[j], dy + 6, name, size=13, color=HOTSTRK if hot else DRPSTRK, bold=True))
        p.append(text(dx[j], dy + 44, _content(idxs), size=12, color=INK))
        p.append(text(dx[j], dy + 63, "степінь %d" % deg, size=11,
                      color=HOTSTRK if hot else MUTED, italic=True, bold=hot))

    box, bw, bh = textbox(W / 2, H - 34,
                          "Степінь краплі — скільки блоків у ній злито. Список цих блоків (або зерно генератора) їде разом із краплею.",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "encode.svg"), W, H, *p,
           title="Кодування: кожна крапля — XOR випадкової жменьки блоків")


# ── peel: три панелі обчищення того самого прикладу ──────────────────────────

def fig_peel():
    W, H = 940, 470
    p = []

    # три стани того самого набору d1=b, d2=a⊕b, d3=a⊕b⊕c
    # для кожної панелі: recovered set, поточний вміст крапель, індекс виділеної (щойно степінь 1), спожиті краплі
    DNAMES = ["d1", "d2", "d3"]
    STAGES = [
        # (заголовок, recovered, {крапля: idxs}, hot_drop, used_drops, підпис)
        ("початок", set(),
         {0: [1], 1: [0, 1], 2: [0, 1, 2]}, 0, set(),
         "d1 = b має степінь 1 → відомо b"),
        ("виріж b", {1},
         {1: [0], 2: [0, 2]}, 1, {0},
         "d2 стало a (степінь 1) → відомо a"),
        ("виріж a", {0, 1},
         {2: [2]}, 2, {0, 1},
         "d3 стало c → відомо c. Готово"),
    ]

    pw = W / 3.0
    for s, (htitle, rec, drops, hot, used, cap) in enumerate(STAGES):
        cx = pw * s + pw / 2
        # роздільник панелей
        if s > 0:
            p.append(line(pw * s, 66, pw * s, H - 96, color="#e2e5ea", sw=1.3, dash="5 5"))
        p.append(text(cx, 66, "%d.  %s" % (s + 1, htitle), size=13.5, color=INK, bold=True))

        # джерела a,b,c
        svx = [cx - 82, cx, cx + 82]
        vy = 128
        # краплі d1,d2,d3
        dvx = [cx - 82, cx, cx + 82]
        dyp = 268

        # ребра з поточного стану
        for jj, idxs in drops.items():
            for i in idxs:
                hotedge = (jj == hot)
                p.append(line(svx[i], vy + 18, dvx[jj], dyp - 20,
                              color=HOTSTRK if hotedge else "#c2c8d0", sw=2.4 if hotedge else 1.5))

        # джерела
        for i, lab in enumerate(SRC):
            done = (i in rec)
            p.append(circle(svx[i], vy, 18, fill=SRCFILL if not done else DONEFILL,
                            stroke=SRCSTRK if not done else DONESTRK, sw=2.2))
            p.append(text(svx[i], vy + 5, lab, size=14, color=SRCSTRK if not done else DONESTRK, bold=True))
            if done:
                p.append(text(svx[i], vy - 26, "✓", size=14, color=SRCSTRK, bold=True))

        # краплі
        for jj in range(3):
            name = DNAMES[jj]
            if jj in used:
                p.append(rect(dvx[jj] - 20, dyp - 20, 40, 40, fill=DONEFILL, stroke=DONESTRK, sw=1.6, rx=6))
                p.append(text(dvx[jj], dyp + 6, name, size=12, color=DONESTRK, bold=True))
                p.append(text(dvx[jj], dyp + 40, "знято", size=10.5, color=DONESTRK, italic=True))
                continue
            idxs = drops[jj]
            deg = len(idxs)
            hotd = (jj == hot)
            p.append(rect(dvx[jj] - 20, dyp - 20, 40, 40, fill=HOTFILL if hotd else DRPFILL,
                          stroke=HOTSTRK if hotd else DRPSTRK, sw=2.4 if hotd else 1.8, rx=6))
            p.append(text(dvx[jj], dyp + 6, name, size=12, color=HOTSTRK if hotd else DRPSTRK, bold=True))
            p.append(text(dvx[jj], dyp + 40, _content(idxs), size=11.5, color=INK))
            p.append(text(dvx[jj], dyp + 58, "ст. %d" % deg, size=10.5,
                          color=HOTSTRK if hotd else MUTED, italic=True, bold=hotd))

        p.append(text(cx, dyp + 108, cap, size=11.5, color=HOTSTRK, bold=True))

    box, bw, bh = textbox(W / 2, H - 40,
                          "Кожен відомий блок вирізають XOR-ом з крапель — степінь падає,\n"
                          "з'являються нові краплі степеня 1: брижа котиться, поки файл не збереться.",
                          size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "peel.svg"), W, H, *p,
           title="Обчищення: крапля степеня 1 запускає ланцюг")


# ── timeline: родовід фонтанних кодів (три акти) ─────────────────────────────

# кольори трьох «актів»
A_STRK, A_FILL = MUTED,   "#eef0f2"   # попередник: швидкий, але фіксована швидкість
B_STRK, B_FILL = DRPSTRK, "#eef4ff"   # ідея + перший безшвидкісний
C_STRK, C_FILL = SRCSTRK, "#eafaf0"   # лінійний і стандартизований


def fig_timeline():
    W, H = 900, 650
    p = []

    spine_x = 232
    y0, y1 = 96, H - 118
    MS = [
        ("1997", "Tornado-коди (STOC)",
         "швидке лінійне кодування на графах — але швидкість n фіксована", "A"),
        ("1998", "«Цифровий фонтан» (SIGCOMM)",
         "метафора потоку; Лубі засновує стартап Digital Fountain", "B"),
        ("2002", "LT-коди (FOCS) — Майкл Лубі",
         "перший практичний безшвидкісний код; ціна декодування ~k·ln k", "B"),
        ("2006", "Raptor-коди — Амін Шокроллагі",
         "передкод + LT → лінійний час, надлишок кілька відсотків", "C"),
        ("2007", "RFC 5053 — Raptor",
         "стандарт IETF; ляже в 3GPP-мовлення (MBMS) і FLUTE", "C"),
        ("2009", "Qualcomm купує Digital Fountain",
         "коди йдуть у мобільне й супутникове мовлення", "C"),
        ("2011", "RFC 6330 — RaptorQ",
         "надлишок майже до нуля; згодом і в телемовленні ATSC 3.0", "C"),
    ]
    COL = {"A": (A_STRK, A_FILL), "B": (B_STRK, B_FILL), "C": (C_STRK, C_FILL)}

    # спинка часу
    p.append(line(spine_x, y0, spine_x, y1, color="#c2c8d0", sw=2.6))

    n = len(MS)
    ys = [y0 + 30 + i * (y1 - y0 - 40) / (n - 1) for i in range(n)]
    cx0, cx1 = spine_x + 34, W - 40
    for (year, title, desc, tier), cy in zip(MS, ys):
        strk, fill = COL[tier]
        # картка
        ch = 54
        p.append(rect(cx0, cy - ch / 2, cx1 - cx0, ch, fill=fill, stroke=strk, sw=2.0, rx=8))
        p.append(line(cx0 + 5, cy - ch / 2 + 6, cx0 + 5, cy + ch / 2 - 6, color=strk, sw=4))
        p.append(text(cx0 + 18, cy - 6, title, size=13.5, color=INK, bold=True, anchor="start"))
        p.append(text(cx0 + 18, cy + 15, desc, size=11.5, color=MUTED, anchor="start"))
        # рік ліворуч від спинки
        p.append(text(spine_x - 30, cy + 5, year, size=15, color=strk, bold=True, anchor="end"))
        # вузол на спинці + конектор
        p.append(line(spine_x, cy, cx0, cy, color=strk, sw=1.6, dash="3 4"))
        p.append(circle(spine_x, cy, 8.5, fill=fill, stroke=strk, sw=2.6))

    # легенда трьох актів
    ly = H - 46
    acts = [
        (A_STRK, A_FILL, "попередник: швидкий, але швидкість фіксована"),
        (B_STRK, B_FILL, "ідея потоку + перший безшвидкісний код"),
        (C_STRK, C_FILL, "лінійний час і стандарти"),
    ]
    lx = 60
    for strk, fill, lab in acts:
        p.append(circle(lx, ly, 8, fill=fill, stroke=strk, sw=2.4))
        p.append(text(lx + 16, ly + 5, lab, size=11.5, color=INK, anchor="start"))
        lx += 30 + text_width(lab, 11.5) + 28

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Родовід: від швидкого коду — до безшвидкісного ідеалу й стандарту")


# ── soliton-pmf: ідеальний ρ(d) проти робастного μ(d), той самий k=64 ─────────

IDEAL_STRK, IDEAL_FILL = DRPSTRK, "#e7eefc"   # ідеальний розподіл
ROB_STRK,   ROB_FILL   = SRCSTRK, "#e9f7ef"   # робастний розподіл


def _rho(d, k):
    return 1.0 / k if d == 1 else 1.0 / (d * (d - 1))


def _tau(i, k, R, delta):
    kR = int(round(k / R))
    if i < kR:
        return R / (i * k)
    if i == kR:
        return R * math.log(R / delta) / k
    return 0.0


def fig_soliton_pmf():
    k, R, delta = 64, 8.0, 0.1
    kR = int(round(k / R))
    beta = sum(_rho(d, k) + _tau(d, k, R, delta) for d in range(1, k + 1))

    def mu(d):
        return (_rho(d, k) + _tau(d, k, R, delta)) / beta

    W, H = 940, 486
    p = []
    XL, XR = 100, 884
    ybase, ytop = 392, 104
    plotH = ybase - ytop
    ymax = 0.5
    ndeg = 12
    bw = 21

    def xg(d):
        return XL + (d - 0.5) * (XR - XL) / ndeg

    def yv(v):
        return ybase - v / ymax * plotH

    # сітка + мітки осі y
    for gv in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        yy = yv(gv)
        p.append(line(XL, yy, XR, yy, color="#e6e9ee", sw=1.1))
        p.append(text(XL - 12, yy + 4, "%.1f" % gv, size=11, color=MUTED, anchor="end"))
    p.append(line(XL, ybase, XR, ybase, color=INK, sw=1.7))
    p.append(text(XL - 6, ytop - 16, "частка крапель зі степенем d", size=12,
                  color=MUTED, anchor="start"))

    # стовпчики
    for d in range(1, ndeg + 1):
        cx = xg(d)
        rv, mv = _rho(d, k), mu(d)
        p.append(rect(cx - bw - 2, yv(rv), bw, ybase - yv(rv),
                      fill=IDEAL_FILL, stroke=IDEAL_STRK, sw=1.6, rx=2))
        spike = (d == kR)
        p.append(rect(cx + 2, yv(mv), bw, ybase - yv(mv),
                      fill="#fdecea" if spike else ROB_FILL,
                      stroke=POS if spike else ROB_STRK, sw=2.6 if spike else 1.6, rx=2))
        p.append(text(cx, ybase + 17, str(d), size=11, color=INK))
    p.append(text(xg(ndeg) + 42, ybase + 17, "…   до d = 64", size=11, color=MUTED, anchor="start"))
    p.append(text((XL + XR) / 2, ybase + 40, "степінь краплі  d", size=12, color=MUTED))

    # позначка сплеску
    sx = xg(kR) + 2 + bw / 2
    p.append(arrow(sx + 78, yv(mu(kR)) - 40, sx + 6, yv(mu(kR)) - 6, color=POS, sw=1.8))
    box, bwd, bh = textbox(sx + 150, yv(mu(kR)) - 48,
                           "сплеск при d = k/R = 8:\nдобирає покриття всіх блоків",
                           size=11.5, bold=True, color=POS, fill="#fff5f4", stroke=POS, sw=1.6, pad=9)
    p.append(box)

    # легенда
    lx, ly = XR - 232, ytop + 4
    p.append(rect(lx, ly, 15, 15, fill=IDEAL_FILL, stroke=IDEAL_STRK, sw=1.6, rx=2))
    p.append(text(lx + 21, ly + 12, "ідеальний  ρ(d)", size=12, color=INK, anchor="start"))
    p.append(rect(lx, ly + 23, 15, 15, fill=ROB_FILL, stroke=ROB_STRK, sw=1.6, rx=2))
    p.append(text(lx + 21, ly + 35, "робастний  μ(d)", size=12, color=INK, anchor="start"))

    box, bwd, bh = textbox(W / 2, H - 22,
                           "Обидва — розподіли степенів. Ідеальний спадає як 1/d² з єдиним піком при d=2;\n"
                           "робастний додає другий пік при d=k/R, щоб брижа не пересихала й усі блоки покрились.",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.7, pad=11)
    p.append(box)

    render(os.path.join(OUT, "soliton-pmf.svg"), W, H, *p,
           title="Два розподіли степенів: ідеальний (один пік) і робастний (пік + сплеск при k/R)")


# ── ripple: брижа як випадкове блукання — тонка гине, товста доживає ──────────

def fig_ripple():
    k, R = 64, 8.0
    W, H = 940, 470
    p = []
    XL, XR = 100, 884
    ybase, ytop = 388, 92
    plotH = ybase - ytop
    ymax = 16.0

    def xL(L):
        return XL + L / k * (XR - XL)

    def yS(s):
        return ybase - s / ymax * plotH

    def poly(pts, color, sw=2.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (s, color, sw, d))

    # сітка y + мітки
    for gv in [0, 4, 8, 12, 16]:
        yy = yS(gv)
        p.append(line(XL, yy, XR, yy, color="#eceef1", sw=1.1))
        p.append(text(XL - 12, yy + 4, str(gv), size=11, color=MUTED, anchor="end"))
    # мітки x
    for L in [0, 16, 32, 48, 64]:
        xx = xL(L)
        p.append(line(xx, ybase, xx, ybase + 5, color=INK, sw=1.2))
        p.append(text(xx, ybase + 21, str(L), size=11, color=MUTED))
    p.append(text((XL + XR) / 2, ybase + 42, "відновлено блоків  L  →", size=12, color=MUTED))
    p.append(text(XL - 6, ytop - 14, "розмір брижі  (крапель степеня 1)", size=12,
                  color=MUTED, anchor="start"))

    Ls = list(range(0, k + 1))

    # нуль — смертельна межа
    p.append(line(XL, ybase, XR, ybase, color=INK, sw=2.0))
    box, bwd, bh = textbox(XR - 96, ybase - 15, "нуль → зупинка",
                           size=11, bold=True, color=POS, fill="#fff5f4", stroke=POS, sw=1.5, pad=6)
    p.append(box)

    # ── робастний: полиця R=8, огортка 8±√L (нижня сягає 0 лише при L=k) ──
    p.append(poly([(xL(L), yS(R + math.sqrt(L))) for L in Ls], ROB_STRK, sw=1.3, dash="4 4"))
    p.append(poly([(xL(L), yS(max(0, R - math.sqrt(L)))) for L in Ls], ROB_STRK, sw=1.3, dash="4 4"))
    p.append(poly([(xL(L), yS(R)) for L in Ls], ROB_STRK, sw=2.6))
    p.append(circle(xL(k), yS(0), 4.5, fill=ROB_STRK, stroke=ROB_STRK, sw=1.5))
    p.append(text(xL(30), yS(R) - 9, "робастний: брижа ≈ R = c·√k·ln(k/δ) ≈ √k",
                  size=12, color=ROB_STRK, bold=True))
    p.append(text(xL(40), yS(1.4), "нижня межа R−√L", size=10.5, color=ROB_STRK, italic=True))
    p.append(text(xL(40), yS(1.4) + 15, "торкається 0 аж при L=k", size=10.5, color=ROB_STRK, italic=True))

    # ── ідеальний: полиця 1, нижня огортка 1−√L падає до 0 майже одразу ──
    p.append(poly([(xL(L), yS(1 + math.sqrt(L))) for L in Ls], IDEAL_STRK, sw=1.3, dash="4 4"))
    p.append(poly([(xL(L), yS(1)) for L in Ls], IDEAL_STRK, sw=2.6))
    p.append(poly([(xL(L), yS(max(0, 1 - math.sqrt(L)))) for L in range(0, 3)],
                  IDEAL_STRK, sw=1.3, dash="4 4"))
    p.append(circle(xL(1), yS(0), 5, fill=POS, stroke=POS, sw=1.5))
    p.append(text(xL(11), yS(1) - 8, "ідеальний: брижа ≈ 1", size=12, color=IDEAL_STRK,
                  bold=True, anchor="start"))
    p.append(arrow(xL(9), yS(2.4), xL(1.4), yS(0.3), color=POS, sw=1.7))
    p.append(text(xL(9.5), yS(2.7), "1−√L падає до 0 одразу", size=11, color=POS,
                  bold=True, anchor="start"))

    # верхня огортка — підпис
    p.append(text(xL(58), yS(1 + math.sqrt(58)) + 2, "1+√L", size=10.5, color=IDEAL_STRK, italic=True))

    box, bwd, bh = textbox(W / 2, H - 20,
                           "Брижа — випадкове блукання; відхилення по L кроках ≈ √L. Тонку полицю =1 воно з'їдає одразу;\n"
                           "піднявши полицю до R≈√k, робастний розподіл доводить блукання до нуля лише в кінці.",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.7, pad=11)
    p.append(box)

    render(os.path.join(OUT, "ripple.svg"), W, H, *p,
           title="Брижа як випадкове блукання: чому потрібна полиця висотою ≈ √k")


if __name__ == "__main__":
    fig_fountain()
    fig_encode()
    fig_peel()
    fig_timeline()
    fig_soliton_pmf()
    fig_ripple()
    print("OK: figures written to", OUT)
