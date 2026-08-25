# -*- coding: utf-8 -*-
"""Фігури до статті «Групи, підгрупи й теорема Лагранжа»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tri_vertices(cx, cy, rad):
    """Вершини рівностороннього трикутника: верх(1), лівий-низ(2), правий-низ(3)."""
    T = (cx, cy - rad)
    L = (cx - 0.8660 * rad, cy + 0.5 * rad)
    R = (cx + 0.8660 * rad, cy + 0.5 * rad)
    return T, L, R


def poly(points, fill=FILL, stroke=INK, sw=2):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts, fill, stroke, sw)


def extend(x1, y1, x2, y2, d):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    return (x1 - ux * d, y1 - uy * d, x2 + ux * d, y2 + uy * d)


def arc_arrow(cx, cy, r, a0, a1, color=INK, sw=2.4):
    """Дуга-стрілка від кута a0 до a1 (градуси, екранні коорд. y вниз)."""
    ra0, ra1 = math.radians(a0), math.radians(a1)
    sx, sy = cx + r * math.cos(ra0), cy + r * math.sin(ra0)
    ex, ey = cx + r * math.cos(ra1), cy + r * math.sin(ra1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (sx, sy, r, r, large, sweep, ex, ey, color, sw))


def seg_between(p1, p2, r1, r2, color=INK, sw=2.2, arrow=True):
    """Відрізок-стрілка між центрами двох вузлів, скорочений на радіуси+зазор."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * (r1 + 4), y1 + uy * (r1 + 4)
    bx, by = x2 - ux * (r2 + 6), y2 - uy * (r2 + 6)
    if arrow:
        return arrow_line(ax, ay, bx, by, color, sw)
    return line(ax, ay, bx, by, color=color, sw=sw)


def arrow_line(x1, y1, x2, y2, color=INK, sw=2.2):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: шість симетрій рівностороннього трикутника — група D₃
# ─────────────────────────────────────────────────────────────────────────────
def fig_d3():
    W, H = 760, 470
    rad = 52
    cols = [145, 380, 615]
    frby = []

    def cell(cx, cy, name, cyc, kind):
        """kind: 'id' | 'rot_ccw' | 'rot_cw' | 'refl1' | 'refl2' | 'refl3'."""
        s = []
        T, L, R = tri_vertices(cx, cy, rad)
        # назва зверху
        s.append(text(cx, cy - rad - 30, name, size=18, bold=True, color=INK))
        # осі відбиття (пунктир) — малюємо ПІД трикутником
        if kind == 'refl1':          # фіксує вершину 1 (верх): вертикаль
            mx, my = cx, cy + 0.5 * rad
            x1, y1, x2, y2 = extend(T[0], T[1], mx, my, 16)
            s.append(line(x1, y1, x2, y2, color=FIELD, sw=2, dash="6 5"))
        elif kind == 'refl2':        # фіксує вершину 2 (лівий-низ)
            mx, my = (T[0] + R[0]) / 2, (T[1] + R[1]) / 2
            x1, y1, x2, y2 = extend(L[0], L[1], mx, my, 16)
            s.append(line(x1, y1, x2, y2, color=FIELD, sw=2, dash="6 5"))
        elif kind == 'refl3':        # фіксує вершину 3 (правий-низ)
            mx, my = (T[0] + L[0]) / 2, (T[1] + L[1]) / 2
            x1, y1, x2, y2 = extend(R[0], R[1], mx, my, 16)
            s.append(line(x1, y1, x2, y2, color=FIELD, sw=2, dash="6 5"))
        # трикутник
        s.append(poly([T, L, R], fill="#f0f3f7", stroke=INK, sw=2))
        # дуга-стрілка для поворотів
        if kind == 'rot_ccw':
            s.append(arc_arrow(cx, cy, rad * 0.42, 200, -70, color=POS))
        elif kind == 'rot_cw':
            s.append(arc_arrow(cx, cy, rad * 0.42, -70, 200, color=POS))
        elif kind == 'id':
            s.append(text(cx, cy + 6, "id", size=15, color=MUTED, italic=True))
        # вершини з номерами (номери — ЗОВНІ трикутника)
        for (px, py), lab, dx, dy in [
            (T, "1", 0, -14), (L, "2", -14, 15), (R, "3", 14, 15)]:
            s.append(circle(px, py, 4.5, fill=INK, stroke=INK, sw=1))
            s.append(text(px + dx, py + dy, lab, size=13, bold=True, color=INK))
        # циклічний запис знизу
        s.append(text(cx, cy + rad + 34, cyc, size=14, color=NEG))
        return "".join(s)

    # заголовки рядів
    frby.append(text(W / 2, 52, "Повороти R = { e, r, r² } — це підгрупа", size=15, bold=True, color=POS))
    frby.append(text(W / 2, 254, "Відбиття — друга суміжна множина (той самий розмір 3)", size=15, bold=True, color=FIELD))
    # ряд 1 — повороти
    frby.append(cell(cols[0], 150, "e", "(тотожність)", "id"))
    frby.append(cell(cols[1], 150, "r", "(1 2 3)", "rot_ccw"))
    frby.append(cell(cols[2], 150, "r²", "(1 3 2)", "rot_cw"))
    # ряд 2 — відбиття
    frby.append(cell(cols[0], 352, "s₁", "(2 3)", "refl1"))
    frby.append(cell(cols[1], 352, "s₂", "(1 3)", "refl2"))
    frby.append(cell(cols[2], 352, "s₃", "(1 2)", "refl3"))

    render(os.path.join(OUT, "d3-symmetries.svg"), W, H, *frby,
           title="Шість симетрій рівностороннього трикутника — група D₃")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: суміжні класи розбивають групу на рівні блоки (Лагранж)
# ─────────────────────────────────────────────────────────────────────────────
def fig_cosets():
    W, H = 700, 470
    frby = []
    bx, by, bw = 150, 66, 250     # рамка групи G
    k = 4                          # кількість блоків (індекс)
    bh = 84                        # висота блоку
    total_h = k * bh
    labels = ["g₃H", "g₂H", "g₁H", "H  (містить e)"]
    fills = ["#f4f6f8", "#f4f6f8", "#f4f6f8", "#e7f7ee"]
    strokes = [LINE, LINE, LINE, FIELD]

    # підпис G над рамкою
    frby.append(text(bx + bw / 2, by - 16, "Група G", size=15, bold=True, color=INK))

    for j in range(k):
        y = by + j * bh
        col = fills[j]
        st = strokes[j]
        frby.append(rect(bx, y, bw, bh, fill=col, stroke=st, sw=2.2, rx=4))
        # назва блоку
        lab_color = FIELD if j == k - 1 else INK
        frby.append(text(bx + bw / 2, y + 30, labels[j], size=15, bold=True, color=lab_color))
        # чотири однакові кружки — «однакова кількість елементів у кожному блоці»
        for d in range(4):
            cxp = bx + 46 + d * 52
            frby.append(circle(cxp, y + 56, 6, fill="#ffffff", stroke=st, sw=1.6))
        frby.append(text(bx + bw / 2, y + 78, "|H| елементів", size=11, color=MUTED))

    # правий квадратний дужок: [G:H] блоків
    rxx = bx + bw + 22
    frby.append(line(rxx, by, rxx, by + total_h, color=INK, sw=2))
    frby.append(line(rxx, by, rxx - 8, by, color=INK, sw=2))
    frby.append(line(rxx, by + total_h, rxx - 8, by + total_h, color=INK, sw=2))
    frby.append(mtext(rxx + 14, by + total_h / 2 - 8,
                      ["[G : H] блоків", "(це індекс —", "число суміжних класів)"],
                      size=13, color=INK, anchor="start"))

    # лівий дужок на один блок = |H|
    lxx = bx - 20
    ytop, ybot = by + (k - 1) * bh, by + k * bh
    frby.append(line(lxx, ytop, lxx, ybot, color=FIELD, sw=2))
    frby.append(line(lxx, ytop, lxx + 8, ytop, color=FIELD, sw=2))
    frby.append(line(lxx, ybot, lxx + 8, ybot, color=FIELD, sw=2))
    frby.append(text(lxx - 10, (ytop + ybot) / 2 + 5, "|H|", size=14, bold=True,
                     color=FIELD, anchor="end"))

    # підсумкова формула
    frby.append(text(W / 2, by + total_h + 44, "|G|  =  [G : H] · |H|", size=20, bold=True, color=INK))

    render(os.path.join(OUT, "cosets-partition.svg"), W, H, *frby,
           title="Суміжні класи ділять групу на рівні блоки")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: порядок елемента — степені a повертаються до e (циклічна підгрупа)
# ─────────────────────────────────────────────────────────────────────────────
def fig_cyclic():
    W, H = 580, 470
    cx0, cy0, R = 290, 232, 150
    nr = 27
    labels = ["e", "a", "a²", "a³", "a⁴", "a⁵"]
    frby = []
    # позиції вузлів: e зверху, далі за годинниковою
    pts = []
    for k in range(6):
        ang = math.radians(-90 + 60 * k)
        pts.append((cx0 + R * math.cos(ang), cy0 + R * math.sin(ang)))

    # стрілки між сусідніми вузлами
    for k in range(6):
        p1, p2 = pts[k], pts[(k + 1) % 6]
        closing = (k == 5)
        col = POS if closing else INK
        frby.append(seg_between(p1, p2, nr, nr, color=col, sw=2.4))
    # підпис першої стрілки «·a»
    mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
    frby.append(text(mx + 24, my - 6, "· a", size=14, color=NEG))
    # підпис замикальної стрілки «a⁶ = e»
    mx5, my5 = (pts[5][0] + pts[0][0]) / 2, (pts[5][1] + pts[0][1]) / 2
    frby.append(text(mx5 - 40, my5 - 4, "a⁶ = e", size=15, bold=True, color=POS))

    # вузли
    for (px, py), lab in zip(pts, labels):
        frby.append(circle(px, py, nr, fill="#eef2f7", stroke=INK, sw=2))
        frby.append(text(px, py + 6, lab, size=16, bold=True, color=INK))

    # центр
    frby.append(text(cx0, cy0 - 4, "⟨a⟩", size=24, bold=True, color=FIELD))
    frby.append(text(cx0, cy0 + 22, "порядок a = 6", size=14, color=INK))

    # підпис під колом
    frby.append(text(W / 2, cy0 + R + 34,
                     "⟨a⟩ = { e, a, a², a³, a⁴, a⁵ } — циклічна підгрупа розміру 6",
                     size=14, color=INK))
    frby.append(text(W / 2, cy0 + R + 60,
                     "тому порядок елемента ділить порядок групи (наслідок Лагранжа)",
                     size=13, color=MUTED))

    render(os.path.join(OUT, "cyclic-order.svg"), W, H, *frby,
           title="Порядок елемента: степені a повертаються до e")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 (вставка hist): народження поняття групи — вертикальна хронологія
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 800, 700
    spine_x = 215
    top, bot = 62, 626
    y0, step = 96, 106
    frby = []

    # рядки: (рік, тег-рівень, колір, [рядок1, рядок2])
    rows = [
        ("1770–71", "ЗЕРНО", MUTED,
         ["Лагранж (Joseph-Louis Lagrange) · Турин → Париж",
          "перестановки коренів: число значень ділить n!"]),
        ("1831", "СЛОВО", NEG,
         ["Галуа (Évariste Galois) · Франція",
          "слово «groupe»; структура групи вирішує розвʼязність"]),
        ("1844", "ОКРЕМИЙ ВИПАДОК", NEG,
         ["Коші (Augustin-Louis Cauchy) · Франція",
          "теорія перестановок; доведення для симетричної Sₙ"]),
        ("1854", "ПЕРША АБСТРАКЦІЯ", FIELD,
         ["Кейлі (Arthur Cayley) · Англія",
          "група як абстрактні символи з асоціативним добутком"]),
        ("1861", "ЗАГАЛЬНЕ ДОВЕДЕННЯ", FIELD,
         ["Жордан (Camille Jordan) · Франція",
          "загальне доведення для будь-якої групи перестановок"]),
        ("1882", "ЧОТИРИ АКСІОМИ", POS,
         ["фон Дік і Вебер (von Dyck, Weber) · Німеччина",
          "чотири аксіоми набувають остаточної форми"]),
    ]

    # хребет часу
    frby.append(line(spine_x, top, spine_x, bot, color=LINE, sw=2.5))

    for i, (year, tag, col, lines) in enumerate(rows):
        cy = y0 + i * step
        # рік і тег-рівень у лівій колонці
        frby.append(text(192, cy - 5, year, size=20, bold=True, color=INK, anchor="end"))
        frby.append(text(192, cy + 15, tag, size=12, bold=True, color=col, anchor="end"))
        # вузол на хребті + короткий сполучник до рамки
        frby.append(circle(spine_x, cy, 8, fill=col, stroke=INK, sw=2))
        frby.append(line(spine_x + 8, cy, 241, cy, color=MUTED, sw=1.5))
        # рамка з описом (шрифт сам влазить у ширину)
        frby.append(fitbox(243, cy - 33, 537, 66, lines, size=15, pad=11,
                           stroke=col, sw=2, fill="#f7f8fa"))

    render(os.path.join(OUT, "birth-timeline.svg"), W, H, *frby,
           title="Народження поняття групи: понад століття від зерна до аксіом")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 (вставка proj): побудова групи з твірних — замикання (closure)
# ─────────────────────────────────────────────────────────────────────────────
def fig_closure():
    W, H = 860, 300
    frby = []

    # три панелі потоку: твірні → нові добутки → замкнена група
    frby.append(fitbox(40, 78, 214, 128,
                       ["Твірні", "S = { r, s₁ }", "2 елементи"],
                       size=15, fill="#eaf0fd", stroke=NEG, color=INK, bold=True))
    frby.append(fitbox(326, 78, 234, 128,
                       ["Множимо всі пари,", "нові — у чергу:", "r·r = r²,  s₁·r = s₂,",
                        "r·s₁ = s₃,  s₁·s₁ = e"],
                       size=14, fill="#eafaf1", stroke=FIELD, color=INK))
    frby.append(fitbox(632, 78, 190, 128,
                       ["Замкнено:", "D₃ = { e, r, r²,", "s₁, s₂, s₃ }", "|G| = 6"],
                       size=15, fill="#e7f7ee", stroke=INK, color=INK, bold=True))

    # стрілки потоку
    frby.append(arrow(256, 142, 322, 142, color=INK, sw=2.4))
    frby.append(arrow(562, 142, 628, 142, color=INK, sw=2.4))

    # підпис-алгоритм унизу
    frby.append(mtext(W / 2, 244,
                      ["closure(S): доки крок множення дає новий елемент — додаємо його;",
                       "коли жодна пара не виводить за межі — множина замкнена, це група."],
                      size=13, color=MUTED))

    render(os.path.join(OUT, "group-closure.svg"), W, H, *frby,
           title="Побудова групи з твірних: замикання за операцією")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 6 (вставка math): чому підгрупа порядку 6 неможлива — квадрати заповнюють H
# ─────────────────────────────────────────────────────────────────────────────
def fig_squares_flood():
    W, H = 820, 512
    e = []
    e.append(text(W / 2, 60, "Припустімо |H| = 6.  Тоді індекс [A₄ : H] = 12 / 6 = 2.",
                  size=16, bold=True))
    e.append(text(W / 2, 86, "Підгрупа індексу 2 містить квадрат кожного елемента A₄.",
                  size=14, color=INK))

    # пари 3-циклів під піднесенням у квадрат
    e.append(text(W / 2, 120,
                  "Квадрат 3-циклу — знову 3-цикл; піднесення до квадрата парує всі вісім:",
                  size=13, color=MUTED))
    pairs = [("(1 2 3)", "(1 3 2)"), ("(1 2 4)", "(1 4 2)"),
             ("(1 3 4)", "(1 4 3)"), ("(2 3 4)", "(2 4 3)")]
    bw2, bh2 = 78, 30
    ytop, ybot = 146, 208
    for i, (a, b) in enumerate(pairs):
        cxp = 70 + 170 * i + 85
        e.append(rect(cxp - bw2 / 2, ytop, bw2, bh2, fill="#eef2f7", stroke=INK, sw=1.6, rx=5))
        e.append(text(cxp, ytop + 20, a, size=13, bold=True))
        e.append(rect(cxp - bw2 / 2, ybot, bw2, bh2, fill="#eef2f7", stroke=INK, sw=1.6, rx=5))
        e.append(text(cxp, ybot + 20, b, size=13, bold=True))
        e.append(arrow(cxp + 16, ytop + bh2 + 2, cxp + 16, ybot - 2, color=POS, sw=1.7))
        e.append(arrow(cxp - 16, ybot - 2, cxp - 16, ytop + bh2 + 2, color=POS, sw=1.7))
        e.append(text(cxp + 33, ytop + bh2 + 20, "²", size=13, color=POS, bold=True))

    e.append(text(W / 2, 286, "⟹  H мусить містити всі вісім трициклів", size=15, bold=True))

    # рахунок: 6 місць проти 8 обов'язкових
    lx, ly, lw, lh = 178, 316, 204, 122
    e.append(rect(lx, ly, lw, lh, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    e.append(text(lx + lw / 2, ly - 8, "H — рівно 6 місць", size=13, bold=True, color=FIELD))
    for k in range(6):
        cxp = lx + 44 + (k % 3) * 58
        cyp = ly + 42 + (k // 3) * 46
        e.append(circle(cxp, cyp, 13, fill="#ffffff", stroke=FIELD, sw=1.8))

    rx0, ry, rw, rh = 440, 316, 214, 122
    e.append(rect(rx0, ry, rw, rh, fill="#fdecea", stroke=POS, sw=2, rx=8))
    e.append(text(rx0 + rw / 2, ry - 8, "мусить містити 8 трициклів", size=13, bold=True, color=POS))
    for k in range(8):
        cxp = rx0 + 32 + (k % 4) * 48
        cyp = ry + 42 + (k // 4) * 46
        e.append(circle(cxp, cyp, 12, fill=POS, stroke=POS, sw=1.2))

    e.append(text((lx + lw + rx0) / 2, ly + lh / 2 + 6, "<", size=30, bold=True, color=INK))
    e.append(text(W / 2, 476, "8 > 6 — суперечність: підгрупи порядку 6 в A₄ немає.",
                  size=16, bold=True, color=POS))

    render(os.path.join(OUT, "a4-squares-flood.svg"), W, H, *e,
           title="Чому підгрупа порядку 6 неможлива")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 7 (вставка math): дільники 12 — де підгрупа є, а де ні
# ─────────────────────────────────────────────────────────────────────────────
def fig_divisor_ladder():
    W, H = 820, 470
    e = []
    cards = [
        ("1", "✓", "{e}", ["тривіальна"], False),
        ("2", "✓", "⟨(1 2)(3 4)⟩", ["Коші · просте 2"], False),
        ("3", "✓", "⟨(1 2 3)⟩", ["Коші · просте 3"], False),
        ("4", "✓", "V₄ (клейнова)", ["Силов · 2²"], False),
        ("6", "✗", "— немає —", ["6 = 2·3,", "не степінь простого"], True),
        ("12", "✓", "уся A₄", ["сама група"], False),
    ]
    cw, ch = 250, 158
    xs = [20, 285, 550]
    ys = [66, 246]
    for i, (d, mark, ex, reason, bad) in enumerate(cards):
        x = xs[i % 3]
        y = ys[i // 3]
        fill = "#fdecea" if bad else "#f7f9fb"
        stroke = POS if bad else LINE
        e.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=2.0 if bad else 1.6, rx=8))
        e.append(text(x + 40, y + 48, d, size=30, bold=True, color=INK))
        e.append(text(x + cw - 34, y + 46, mark, size=24, bold=True,
                      color=POS if bad else FIELD))
        e.append(line(x + 16, y + 64, x + cw - 16, y + 64, color=LINE, sw=1))
        e.append(text(x + cw / 2, y + 96, ex, size=14, bold=True,
                      color=POS if bad else INK))
        e.append(mtext(x + cw / 2, y + 122, reason, size=12,
                       color=POS if bad else MUTED))

    e.append(mtext(W / 2, 438,
                   ["Кожен дільник 12 — степінь простого (1, 2, 3, 4) або сам порядок групи (12).",
                    "Виняток один — число 6, і саме там підгрупи немає."],
                   size=13, color=INK))

    render(os.path.join(OUT, "a4-divisor-ladder.svg"), W, H, *e,
           title="Дільники 12 та підгрупи A₄")


if __name__ == "__main__":
    fig_d3()
    fig_cosets()
    fig_cyclic()
    fig_timeline()
    fig_closure()
    fig_squares_flood()
    fig_divisor_ladder()
    print("OK: 7 фігур згенеровано в", OUT)
