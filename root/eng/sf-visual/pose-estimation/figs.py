# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RAY     = "#94a3b8"   # промінь погляду
KNOWN   = FIELD       # відоме — зелене
UNKNOWN = POS         # шукане — червоне
ANGLE   = NEG         # кути зі знімка — синє
OBJ     = "#0f766e"   # 3D-точки об'єкта


def arc(cx, cy, r, a1, a2, color=INK, sw=1.6):
    """Дуга кола від кута a1 до a2 (радіани, екранні координати)."""
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    sweep = 1 if a2 > a1 else 0
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x1, y1, r, r, sweep, x2, y2, color, sw))


def cross(cx, cy, r, col, sw=2):
    return (line(cx - r, cy, cx + r, cy, color=col, sw=sw) +
            line(cx, cy - r, cx, cy + r, color=col, sw=sw))


# ── 1. Геометрія PnP: центр, площина знімка, промені, невідома поза ────────────
def fig_pnp_setup():
    W, H = 860, 478
    p = []
    C = (152, 226)                       # центр камери
    plane_x = 312
    # три 3D-точки об'єкта
    P = [(654, 92), (784, 226), (662, 362)]

    # промені з C через площину знімка до точок + пікселі на площині
    px = []
    for (qx, qy) in P:
        t = (plane_x - C[0]) / (qx - C[0])
        py = C[1] + t * (qy - C[1])
        px.append((plane_x, py))

    # фрустум (поле зору) — легкі лінії від центра до країв площини
    p.append(line(C[0], C[1], plane_x, 150, color=RAY, sw=1.1, dash="2,4"))
    p.append(line(C[0], C[1], plane_x, 302, color=RAY, sw=1.1, dash="2,4"))

    # промені-погляди й точки
    for (qx, qy), (ux, uy) in zip(P, px):
        p.append(line(C[0], C[1], qx, qy, color=RAY, sw=1.4, dash="6,5"))

    # об'єкт: три точки, з'єднані тонким трикутником
    tri = " ".join("%.0f,%.0f" % q for q in P)
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="3,3"/>' % (tri, OBJ))
    for i, (qx, qy) in enumerate(P):
        p.append(circle(qx, qy, 6, fill=KNOWN, stroke=INK, sw=1.3))
        p.append(text(qx + 16, qy + 5, "X%d" % (i + 1), size=13, color=OBJ, bold=True, anchor="start"))

    # площина знімка + пікселі
    p.append(rect(plane_x - 8, 150, 16, 152, fill="#eef2f7", stroke=INK, sw=1.4, rx=3))
    p.append(text(plane_x, 140, "площина знімка", size=11, color=INK))
    for i, (ux, uy) in enumerate(px):
        p.append(cross(ux, uy, 6, ANGLE, sw=2))
    p.append(text(plane_x + 14, px[0][1] - 6, "(u, v)", size=11, color=ANGLE, anchor="start"))

    # центр камери
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=INK, sw=1))
    p.append(text(C[0] - 12, C[1] + 5, "C", size=14, color=INK, bold=True, anchor="end"))
    p.append(text(C[0], C[1] + 26, "центр камери", size=10.5, color=MUTED))

    # позначки двох систем координат + стрілка пози (R, t) знизу
    ay = 408
    p.append(arrow(636, ay, 214, ay, color=UNKNOWN, sw=2.2))
    p.append(text(424, ay - 12, "(R, t) — шукана поза", size=13, color=UNKNOWN, bold=True))
    p.append(text(214, ay + 20, "система камери", size=10.5, color=MUTED, anchor="start"))
    p.append(text(636, ay + 20, "система об'єкта (світу)", size=10.5, color=MUTED, anchor="end"))

    # легенда: відоме / шукане
    p.append(circle(60, 448, 6, fill=KNOWN, stroke=INK, sw=1.2))
    p.append(text(74, 452, "відомо: 3D-точки Xᵢ, пікселі (u,v), матриця K", size=11, color=INK, anchor="start"))
    p.append(cross(470, 448, 6, UNKNOWN, sw=2))
    p.append(text(484, 452, "шукано: поворот R і зсув t (шість чисел)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "pnp-setup.svg"), W, H, *p,
           title="PnP: за 3D-точками та їхніми пікселями знайти позу камери")


# ── 2. P3P: піраміда з трьох променів — кути й сторони відомі, відстані шукані ──
def fig_p3p_cosines():
    W, H = 820, 470
    p = []
    C = (150, 300)
    P = [(566, 96), (726, 250), (524, 386)]     # три точки-вершини

    # промені (шукані відстані d)
    for (qx, qy) in P:
        p.append(line(C[0], C[1], qx, qy, color=UNKNOWN, sw=2))
    # трикутник об'єкта (відомі сторони)
    tri = " ".join("%.0f,%.0f" % q for q in P)
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (tri, KNOWN))

    # кути між сусідніми променями (з атан2 в екранних координатах)
    ang = [math.atan2(q[1] - C[1], q[0] - C[0]) for q in P]
    order = sorted(range(3), key=lambda i: ang[i])       # за кутом згори донизу
    a = [ang[i] for i in order]
    p.append(arc(C[0], C[1], 74, a[0], a[1], color=ANGLE, sw=2))
    p.append(arc(C[0], C[1], 100, a[1], a[2], color=ANGLE, sw=2))
    am1 = (a[0] + a[1]) / 2
    am2 = (a[1] + a[2]) / 2
    p.append(text(C[0] + 92 * math.cos(am1), C[1] + 92 * math.sin(am1) + 4, "θ₁", size=13, color=ANGLE, bold=True))
    p.append(text(C[0] + 120 * math.cos(am2), C[1] + 120 * math.sin(am2) + 4, "θ₂", size=13, color=ANGLE, bold=True))

    # підписи відстаней d на серединах променів
    dnames = ["d₁", "d₂", "d₃"]
    for (qx, qy), nm in zip(P, dnames):
        mx, my = (C[0] + qx) / 2, (C[1] + qy) / 2
        p.append(text(mx - 14, my - 6, nm, size=14, color=UNKNOWN, bold=True))

    # підписи сторін трикутника
    sides = [((P[0], P[1]), "|P₁P₂|"), ((P[1], P[2]), "|P₂P₃|"), ((P[0], P[2]), "|P₁P₃|")]
    for ((A, B), nm) in sides:
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        p.append(text(mx + 12, my, nm, size=11.5, color=OBJ, bold=True, anchor="start"))

    # вершини
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=INK, sw=1))
    p.append(text(C[0] - 12, C[1] + 5, "C", size=14, color=INK, bold=True, anchor="end"))
    for i, (qx, qy) in enumerate(P):
        p.append(circle(qx, qy, 6, fill=KNOWN, stroke=INK, sw=1.3))
        p.append(text(qx + 14, qy + 4, "P%d" % (i + 1), size=12, color=OBJ, bold=True, anchor="start"))

    # легенда
    lx, ly = 40, 424
    p.append(line(lx, ly, lx + 30, ly, color=ANGLE, sw=2.4))
    p.append(text(lx + 38, ly + 4, "θ — кути між променями (зі знімка)", size=10.5, color=INK, anchor="start"))
    p.append(line(lx + 330, ly, lx + 360, ly, color=KNOWN, sw=2.4))
    p.append(text(lx + 368, ly + 4, "|PᵢPⱼ| — сторони (з моделі)", size=10.5, color=INK, anchor="start"))
    p.append(line(lx, ly + 24, lx + 30, ly + 24, color=UNKNOWN, sw=2.4))
    p.append(text(lx + 38, ly + 28, "dᵢ — відстані до вершин (шукані): теорема косинусів дає три квадратні рівняння",
                  size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "p3p-cosines.svg"), W, H, *p,
           title="P3P: кути й сторони відомі — знайти три відстані")


# ── 3. Похибка перепроєкції та відсів викидів (RANSAC) ─────────────────────────
def fig_reprojection_ransac():
    W, H = 820, 462
    p = []
    fx0, fy0, fw, fh = 60, 66, 700, 300
    p.append(rect(fx0, fy0, fw, fh, fill="#0f172a", stroke=INK, sw=1.3, rx=8))
    p.append(text(fx0 + fw / 2, fy0 - 12, "кадр: спостережене (×) проти спроєктованого (●)", size=11, color=INK))

    # inliers: спостережене-хрестик і спроєктована-точка близько
    inl = [((190, 150), (198, 158)), ((320, 128), (313, 136)),
           ((452, 176), (460, 169)), ((556, 138), (549, 146)),
           ((262, 250), (269, 256)), ((628, 236), (620, 243)),
           ((404, 300), (411, 293))]
    # outliers: далеко
    outl = [((360, 214), (250, 250)), ((600, 300), (690, 226)), ((150, 300), (214, 344))]

    for (ox, oy), (rx, ry) in inl:
        p.append(line(ox, oy, rx, ry, color="#22c55e", sw=2.4))
        p.append(cross(ox, oy, 6, "#93c5fd", sw=2))
        p.append(circle(rx, ry, 4, fill="#f59e0b", stroke="none", sw=0))
    for (ox, oy), (rx, ry) in outl:
        p.append(line(ox, oy, rx, ry, color="#ef4444", sw=2, dash="5,4"))
        p.append(cross(ox, oy, 6, "#93c5fd", sw=2))
        p.append(circle(rx, ry, 4, fill="#f59e0b", stroke="none", sw=0))

    # поріг навколо однієї пари
    p.append(circle(320, 128, 20, fill="none", stroke="#e2e8f0", sw=1.3))
    p.append(text(320, 100, "поріг", size=9.5, color="#e2e8f0"))

    # легенда
    ly = fy0 + fh + 26
    p.append(line(80, ly, 112, ly, color="#22c55e", sw=2.6))
    p.append(text(120, ly + 4, "inlier — похибка менша за поріг", size=11, color=INK, anchor="start"))
    p.append(line(430, ly, 462, ly, color="#ef4444", sw=2.2, dash="5,4"))
    p.append(text(470, ly + 4, "outlier — велика похибка, відкинути", size=11, color=INK, anchor="start"))

    p.append(fitbox(60, ly + 20, 700, 42,
                    "Похибка перепроєкції — довжина відрізка від спостереженого пікселя до спроєктованого.\n"
                    "RANSAC лишає короткі (inliers) й відкидає довгі (outliers), тоді усереднює лише inliers.",
                    size=11, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "reprojection-ransac.svg"), W, H, *p,
           title="Похибка перепроєкції: короткі лишити, довгі відсіяти")


# ── 4. Конвеєр PnP: пари → RANSAC(P3P) → inliers → уточнення → поза ─────────────
def fig_pnp_pipeline():
    W, H = 860, 264
    p = []
    boxes = [
        (24, 128, "пари\n2D ↔ 3D", KNOWN),
        (196, 176, "RANSAC\nP3P на трійці\n→ лічити inliers", ANGLE),
        (400, 96, "inliers", MUTED),
        (524, 176, "Ґаусс–Ньютон\nмін. похибки\nперепроєкції", UNKNOWN),
        (728, 108, "поза\n(R, t)", INK),
    ]
    by, bh = 84, 104
    ends = []
    for (x, w, s, col) in boxes:
        p.append(fitbox(x, by, w, bh, s, size=12, fill="#fbfbfd", stroke=col, sw=1.8, color=INK))
        ends.append((x, x + w))
    for i in range(len(boxes) - 1):
        p.append(arrow(ends[i][1] + 4, by + bh / 2, ends[i + 1][0] - 4, by + bh / 2, color=INK, sw=1.8))

    # цикл RANSAC
    bx, bw = boxes[1][0], boxes[1][1]
    p.append(text(bx + bw / 2, by + bh + 22, "↺ багато випадкових трійок", size=10.5, color=ANGLE))

    p.append(fitbox(24, by + bh + 44, W - 48, 24,
                    "Мінімальна розв'язка в циклі RANSAC відсіює викиди й дає грубу позу; "
                    "нелінійне уточнення на всіх inliers доводить її до найменшої піксельної похибки.",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "pnp-pipeline.svg"), W, H, *p,
           title="Конвеєр PnP: груба розв'язка → відсів викидів → уточнення")


# ── 5. Родовід PnP: часова стрічка (для історичної вставки hist-pnp-lineage) ────
def fig_pnp_timeline():
    W, H = 1040, 486
    ERA_GEO, ERA_PHOTO, ERA_CV = FIELD, OBJ, NEG
    axis_y = 156
    p = []

    # вісь часу
    p.append(line(48, axis_y, W - 48, axis_y, color=MUTED, sw=2))
    p.append(arrow(W - 66, axis_y, W - 44, axis_y, color=MUTED, sw=2))
    p.append(text(W - 50, axis_y - 10, "час", size=11, color=MUTED, anchor="end"))

    nodes = [
        ("1615 · 1692", ["Снелліус,", "Потено"],        "засічка 2D",     ERA_GEO),
        ("1841",        ["Ґрунерт"],                      "теорія P3P",     ERA_GEO),
        ("1903 · 1949", ["Фінстервальдер,", "Меррітт"],   "фотограмметрія", ERA_PHOTO),
        ("1981",        ["Фішлер, Боллз"],                "ім'я + RANSAC",  ERA_CV),
        ("1991",        ["Гаралік та ін."],               "ревізія",        ERA_CV),
        ("2003",        ["Гао та ін."],                   "класифікація",   ERA_CV),
        ("2007 · 2009", ["EPnP"],                         "за O(n)",        ERA_CV),
        ("2018",        ["Lambda-Twist"],                 "стійкий P3P",    ERA_CV),
    ]
    n = len(nodes)
    left, right = 82, W - 82
    step = (right - left) / (n - 1)

    for i, (year, names, role, col) in enumerate(nodes):
        x = left + step * i
        p.append(text(x, axis_y - 30, role, size=10.5, color=col, bold=True))
        base = axis_y + 26 if i % 2 == 0 else axis_y + 74
        if base - 16 > axis_y + 12:                     # поводок лише для нижнього ряду
            p.append(line(x, axis_y + 8, x, base - 16, color="#d0d5dd", sw=1))
        p.append(circle(x, axis_y, 7, fill=col, stroke=INK, sw=1.3))
        p.append(text(x, base, year, size=12, color=INK, bold=True))
        for j, nm in enumerate(names):
            p.append(text(x, base + 18 + j * 15, nm, size=11, color=MUTED))

    # легенда трьох епох
    ly = H - 58
    lx = 82
    for lab, col in [("геодезична засічка", ERA_GEO), ("фотограмметрія", ERA_PHOTO),
                     ("комп'ютерний зір", ERA_CV)]:
        p.append(circle(lx, ly, 6, fill=col, stroke=INK, sw=1.2))
        p.append(text(lx + 14, ly + 4, lab, size=11, color=INK, anchor="start"))
        lx += text_width(lab, 11) + 66

    p.append(fitbox(70, H - 40, 900, 30,
                    "Одна задача — засічка за трьома променями — виникала наново в кожній галузі.\n"
                    "У комп'ютерному зорі вона дістала ім'я, а потім і швидкі, чисельно стійкі розв'язувачі.",
                    size=11, fill=FILL, stroke=INK, sw=1.1, color=INK))

    render(os.path.join(OUT, "pnp-lineage-timeline.svg"), W, H, *p,
           title="Родовід PnP: від землемірної засічки до розв'язувачів реального часу")


# ── math-вставка P3P: квартика й кількість коренів ────────────────────────────
def _peval(c, x):
    r = 0.0
    for a in c:
        r = r * x + a
    return r


def _quartic_panel(px, py, pw, ph, coef, vlo, vhi, roots, sub):
    """Один графік p(v) у рамці; y нормалізується під саму криву (форма важлива,
    не абсолютні значення). roots — дійсні додатні корені (позначаємо крапками)."""
    f = [rect(px, py, pw, ph, fill="#fbfcfd", stroke="#e5e7eb", sw=1.2, rx=10)]
    N = 180
    xs = [vlo + (vhi - vlo) * i / (N - 1) for i in range(N)]
    ys = [_peval(coef, x) for x in xs]
    ymin = min(min(ys), 0.0); ymax = max(max(ys), 0.0)
    span = (ymax - ymin) or 1.0
    ymin -= 0.10 * span; ymax += 0.12 * span
    padL, padR, padT, padB = 40, 16, 40, 46
    ax0, ax1 = px + padL, px + pw - padR
    ay0, ay1 = py + padT, py + ph - padB
    X = lambda v: ax0 + (v - vlo) / (vhi - vlo) * (ax1 - ax0)
    Y = lambda p: ay1 - (p - ymin) / (ymax - ymin) * (ay1 - ay0)
    # осі
    f.append(line(ax0, ay0 - 6, ax0, ay1, color=INK, sw=1.4))          # p(v)
    f.append(line(ax0, ay1, ax1, ay1, color=INK, sw=1.4))              # v
    f.append(text(ax0 - 6, ay0 - 2, "p(v)", size=11, color=INK, anchor="end"))
    f.append(text(ax1, ay1 + 26, "v = d₃/d₁", size=11.5, color=INK, anchor="end"))
    for tv in [t for t in (0.5, 1.0, 1.5, 2.0, 2.5) if vlo <= t <= vhi]:
        f.append(line(X(tv), ay1, X(tv), ay1 + 4, color=INK, sw=1.1))
        f.append(text(X(tv), ay1 + 17, "%.1f" % tv, size=10, color=MUTED))
    # нульова лінія
    yz = Y(0.0)
    f.append(line(ax0, yz, ax1, yz, color=MUTED, sw=1.1, dash="5 4"))
    f.append(text(ax1 - 2, yz - 5, "0", size=10, color=MUTED, anchor="end"))
    # крива
    pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in zip(xs, ys))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, NEG))
    # дійсні додатні корені — пози
    for rv in roots:
        f.append(circle(X(rv), yz, 5.6, fill=UNKNOWN, stroke=INK, sw=1.4))
    f.append(text(px + pw / 2, py + 22, sub, size=13, color=INK, bold=True))
    return "".join(f)


def fig_p3p_quartic():
    W, H = 940, 430
    left = _quartic_panel(40, 60, 420, H - 92,
                          [1.0, -3.91428, 5.57306, -3.63634, 0.82412],
                          0.30, 1.95, [0.451, 1.797],
                          "2 дійсні корені  →  2 пози")
    right = _quartic_panel(480, 60, 420, H - 92,
                           [1.0, -4.77967, 7.53055, -4.37757, 0.70936],
                           0.05, 2.45, [0.2606, 0.8199, 1.5317, 2.1674],
                           "4 дійсні корені  →  4 пози")
    leg = text(W / 2, H - 16,
               "червона крапка = дійсний додатний корінь (одна поза);  "
               "комплексні та від'ємні корені позами не є",
               size=11.5, color=MUTED)
    render(os.path.join(OUT, "p3p-quartic.svg"), W, H, left, right, leg,
           title="Квартика P3P: скільки разів вона перетинає вісь — стільки поз")


# ── math-вставка P3P: одна картинка — кілька конгруентних посадок ──────────────
def fig_p3p_ambiguity():
    W, H = 680, 500
    Cx, Cy, sc = 336, 452, 100.0
    S = lambda x, y: (Cx + x * sc, Cy - y * sc)
    rays = [(0.3746, 0.9272), (0.0, 1.0), (-0.4067, 0.9135)]
    trueP = [(1.1987, 2.967), (0.0, 3.6), (-1.1389, 2.5579)]
    otherP = [(1.1064, 2.7383), (0.0, 1.955), (-1.2646, 2.8403)]
    p = []

    # промені з камери
    for i, (dx, dy) in enumerate(rays):
        ex, ey = S(dx * 4.05, dy * 4.05)
        p.append(line(Cx, Cy, ex, ey, color=RAY, sw=1.6))
        p.append(text(ex + (10 if dx > 0.05 else (-10 if dx < -0.05 else 0)),
                      ey - 6, "промінь %d" % (i + 1), size=11, color=MUTED,
                      anchor="start" if dx > 0.05 else ("end" if dx < -0.05 else "middle")))

    # дуга «кути θ фіксовані знімком» біля камери
    import math as _m
    a1 = _m.atan2(-(rays[0][1]), rays[0][0]); a2 = _m.atan2(-(rays[2][1]), rays[2][0])
    rr = 66
    x1, y1 = Cx + rr * _m.cos(a1), Cy + rr * _m.sin(a1)
    x2, y2 = Cx + rr * _m.cos(a2), Cy + rr * _m.sin(a2)
    p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.4"/>' % (x1, y1, rr, rr, x2, y2, ANGLE))
    p.append(text(Cx - rr - 12, Cy - 26, "кути θ — зі знімка", size=11, color=ANGLE,
                  anchor="end"))

    # інша посадка (штрихова, синя) — малюємо першою, щоб справжня була згори
    op = [S(*q) for q in otherP]
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="7 5"/>' % (" ".join("%.1f,%.1f" % q for q in op), ANGLE))
    for (sx, sy) in op:
        p.append(circle(sx, sy, 5.0, fill=BG, stroke=ANGLE, sw=2.0))

    # справжня посадка (суцільна, червона, легка заливка)
    tp = [S(*q) for q in trueP]
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.12" stroke="%s" '
             'stroke-width="2.6"/>' % (" ".join("%.1f,%.1f" % q for q in tp), UNKNOWN, UNKNOWN))
    labs = ["P₁", "P₂", "P₃"]
    for i, (sx, sy) in enumerate(tp):
        p.append(circle(sx, sy, 6.0, fill=UNKNOWN, stroke=INK, sw=1.4))
        off = (14 if trueP[i][0] > 0.05 else (-14 if trueP[i][0] < -0.05 else 0))
        p.append(text(sx + off, sy - 10, labs[i], size=13, color=UNKNOWN, bold=True,
                      anchor="middle"))

    # камера
    p.append(circle(Cx, Cy, 8, fill=INK, stroke=INK, sw=1))
    p.append(text(Cx, Cy + 24, "камера C", size=12.5, color=INK, bold=True))

    # легенда
    lx, ly = 60, 96
    p.append(line(lx, ly, lx + 30, ly, color=UNKNOWN, sw=2.6))
    p.append(text(lx + 38, ly + 4, "поза A (справжня)", size=12, color=INK, anchor="start"))
    p.append(line(lx, ly + 24, lx + 30, ly + 24, color=ANGLE, sw=2.2, dash="7 5"))
    p.append(text(lx + 38, ly + 28, "поза B — та сама картинка", size=12, color=INK, anchor="start"))

    p.append(fitbox(W - 322, 78, 288, 52,
                    "Обидва трикутники конгруентні — ті самі сторони.\n"
                    "Кожна вершина сидить на своєму промені.",
                    size=11, fill=FILL, stroke="#e5e7eb", sw=1.1, color=INK))

    render(os.path.join(OUT, "p3p-ambiguity.svg"), W, H, *p,
           title="Та сама трійка променів — конгруентний трикутник сідає по-різному")


# ── math-вставка якобіана: геометрія збурення пози + ланцюг множників 2×3·3×6 ───
def fig_reprojection_jacobian():
    W, H = 1000, 442
    p = []

    # ---- Ліворуч: геометричний зміст ∂X_c/∂φ = −[X_c]× та ∂X_c/∂δt = I ----------
    C = (150, 250)                       # центр камери
    Xc = (340, 110)                      # точка в системі камери
    p.append(line(C[0], C[1], Xc[0], Xc[1], color=RAY, sw=1.8))          # промінь-радіус
    # вісь повороту φ через центр камери
    p.append(arrow(C[0], C[1], 141, 162, color=ANGLE, sw=2))
    p.append(line(C[0], C[1], 158, 332, color=ANGLE, sw=1.2, dash="3,4"))
    p.append(text(120, 158, "вісь φ", size=11.5, color=ANGLE, bold=True, anchor="end"))
    # червона дотична — швидкість повороту φ × X_c (⟂ радіуса)
    p.append(arrow(Xc[0], Xc[1], 388, 174, color=UNKNOWN, sw=2.4))
    p.append(text(396, 182, "φ × X_c", size=12.5, color=UNKNOWN, bold=True, anchor="start"))
    p.append(text(396, 199, "= −[X_c]ₓ·φ", size=10.5, color=UNKNOWN, anchor="start"))
    # зелений — зсув δt (рух 1:1)
    p.append(arrow(Xc[0], Xc[1], 420, 110, color=KNOWN, sw=2.4))
    p.append(text(428, 106, "δt", size=12.5, color=KNOWN, bold=True, anchor="start"))
    p.append(text(428, 122, "(I)", size=10.5, color=KNOWN, anchor="start"))
    # мітка прямого кута між радіусом і дотичною
    p.append(line(330.3, 117.1, 337.4, 126.7, color=MUTED, sw=1.2))
    p.append(line(347.1, 119.7, 337.4, 126.7, color=MUTED, sw=1.2))
    # вузли
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=INK, sw=1))
    p.append(text(C[0] - 12, C[1] + 5, "C", size=13, color=INK, bold=True, anchor="end"))
    p.append(circle(Xc[0], Xc[1], 6, fill=OBJ, stroke=INK, sw=1.3))
    p.append(text(Xc[0] + 12, Xc[1] - 6, "X_c", size=13, color=OBJ, bold=True, anchor="start"))

    p.append(fitbox(44, 300, 430, 74,
                    "Поворот φ несе X_c по колу навколо осі — миттєва швидкість φ×X_c\n"
                    "перпендикулярна радіусу C→X_c, тобто дорівнює −[X_c]ₓ·φ.\n"
                    "Зсув δt рухає точку 1:1, тому ∂X_c/∂δt = I.",
                    size=11, fill=FILL, stroke=INK, sw=1.2, color=INK))

    # ---- Праворуч: ланцюг множників (розміри матриць) ---------------------------
    by, bh = 150, 64
    boxes = [(515, 118, "Δ = (δt, φ)\nℝ⁶ · поза"),
             (705, 96,  "δX_c\nℝ³ · камера"),
             (873, 100, "δ(u, v)\nℝ² · піксель")]
    span = []
    for (x, w, s) in boxes:
        p.append(fitbox(x, by, w, bh, s, size=12, fill="#fbfbfd", stroke=INK, sw=1.7, color=INK))
        span.append((x, x + w))
    midy = by + bh / 2
    p.append(arrow(span[0][1] + 5, midy, span[1][0] - 5, midy, color=INK, sw=1.9))
    p.append(text((span[0][1] + span[1][0]) / 2, 138, "( I₃ | −[X_c]ₓ )", size=11, color=INK, bold=True))
    p.append(text((span[0][1] + span[1][0]) / 2, 236, "3×6", size=11, color=MUTED))
    p.append(arrow(span[1][1] + 5, midy, span[2][0] - 5, midy, color=INK, sw=1.9))
    p.append(text((span[1][1] + span[2][0]) / 2, 138, "∂π ∕ ∂X_c", size=11, color=INK, bold=True))
    p.append(text((span[1][1] + span[2][0]) / 2, 236, "2×3", size=11, color=MUTED))

    p.append(fitbox(505, 300, 470, 74,
                    "Ланцюг: поза → точка в камері → піксель.\n"
                    "Перемножені блоки дають J = ∂π/∂X_c · ( I₃ | −[X_c]ₓ )\n"
                    "— 2×6 на кожну точку, цеглину нормальних рівнянь JᵀJ·Δ = −Jᵀr.",
                    size=11, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "reprojection-jacobian.svg"), W, H, *p,
           title="Якобіан перепроєкції: геометрія збурення пози та ланцюг множників 2×3 · 3×6")


if __name__ == "__main__":
    fig_pnp_setup()
    fig_p3p_cosines()
    fig_reprojection_ransac()
    fig_pnp_pipeline()
    fig_pnp_timeline()
    fig_p3p_quartic()
    fig_p3p_ambiguity()
    fig_reprojection_jacobian()
    print("OK: figures written to", OUT)


# ── proj-vstavka pnp-solver: budget RANSAC ──
def fig_ransac_budget():
    W, H = 820, 496
    p = []
    x0, y0, gw, gh = 100, 78, 640, 280
    xr = y0 + gh
    conf = 0.99
    lo, hi = 0.2, 0.9
    Lmax = 5.0

    def X(w):  return x0 + (w - lo) / (hi - lo) * gw
    def Y(L):  return xr - min(L, Lmax) / Lmax * gh
    def Nreq(w, s):
        return math.log(1 - conf) / math.log(1 - w ** s)

    p.append(rect(x0, y0, gw, gh, fill="#fbfdff", stroke=MUTED, sw=1.2, rx=4))
    for L in range(1, 6):
        gy = Y(L)
        p.append(line(x0, gy, x0 + gw, gy, color="#e6eaf1", sw=1))
        lab = "10" if L == 1 else "10" + "²³⁴⁵"[L - 2]
        p.append(text(x0 - 12, gy + 4, lab, size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 4, y0 - 12, "потрібно ітерацій N", size=11.5, color=INK, anchor="start"))

    w = 0.2
    while w <= 0.9001:
        gx = X(w)
        p.append(line(gx, xr, gx, xr + 5, color=MUTED, sw=1))
        p.append(text(gx, xr + 19, "%.1f" % w, size=10.5, color=MUTED))
        w += 0.1
    p.append(text(x0 + gw / 2, xr + 40, "частка правильних пар  w", size=12, color=INK, bold=True))

    for s, col in [(3, NEG), (6, POS)]:
        prev = None
        w = lo
        while w <= hi + 1e-9:
            cx, cy = X(w), Y(math.log10(Nreq(w, s)))
            if prev:
                p.append(line(prev[0], prev[1], cx, cy, color=col, sw=2.8))
            prev = (cx, cy)
            w += 0.01

    p.append(line(X(0.5), y0, X(0.5), xr, color="#cbd5e1", sw=1, dash="4,4"))
    p.append(text(X(0.5), y0 - 12, "w = 0.5", size=10.5, color=MUTED))
    for s, col in [(3, NEG), (6, POS)]:
        N = Nreq(0.5, s)
        cx, cy = X(0.5), Y(math.log10(N))
        p.append(circle(cx, cy, 5, fill=col, stroke=BG, sw=1.6))
        p.append(text(cx + 11, cy + 4, "≈ %d" % math.ceil(N), size=12, color=col, bold=True, anchor="start"))

    ly = xr + 60
    p.append(line(x0, ly, x0 + 32, ly, color=NEG, sw=3))
    p.append(text(x0 + 40, ly + 4, "s = 3 — трійка для P3P", size=11, color=INK, anchor="start"))
    p.append(line(x0 + 300, ly, x0 + 332, ly, color=POS, sw=3))
    p.append(text(x0 + 340, ly + 4, "s = 6 — шістка для DLT", size=11, color=INK, anchor="start"))

    p.append(fitbox(x0, ly + 18, gw, 42,
                    "Менша мінімальна вибірка — експоненційно менше випадкових спроб на ту саму певність.\n"
                    "За 50% правильних пар P3P коштує ≈35 трійок, DLT — ≈293 шістки: тому продакшн бере P3P.",
                    size=11, fill=FILL, stroke=INK, sw=1.1, color=INK))

    render(os.path.join(OUT, "ransac-budget.svg"), W, H, *p,
           title="Бюджет RANSAC: менша вибірка — менше ітерацій")


if __name__ == "__main__":
    fig_ransac_budget()
