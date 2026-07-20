# -*- coding: utf-8 -*-
"""Фігури до статті «Задача здійсненності (SAT)».
Запуск:  python figs.py   → пише SVG у ./img/  (search-tree, cnf-anatomy, sat-hub)
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ROW = "#f4f6f8"
CUT = "#c7ccd4"      # відрубана (сіра) гілка
SATFILL = "#eaf6ee"  # легке зелене поле
CLA = "#eef2fb"      # заливка клаузи
BAND = "#eef2fb"     # смуга-підсвітка колонки 1971
WEST_F, WEST_S = "#eaf0fd", NEG   # Захід — холодні тони
SOV_F, SOV_S = "#fdecea", POS     # СРСР — теплі тони


# ── 1. Дерево наборів і експоненційний вибух ─────────────────────────────────
def fig_search_tree():
    W, H = 900, 500
    f = [text(W / 2, 32, "Простір усіх наборів значень — двійкове дерево", size=18, bold=True),
         text(W / 2, 54, "n змінних → n рівнів розвилок «0 чи 1» → 2ⁿ листків унизу; додати змінну = подвоїти дно",
              size=12, color=MUTED, italic=True)]

    # чотири рівні (A,B,C,D), корінь угорі
    levels = [
        (450, 96),                                  # корінь
    ]
    # координати вузлів по рівнях
    ox, top = 450, 96
    rh = 78
    # рівень 1: 2 вузли, рівень 2: 4, рівень 3: 8 (останній рівень листків не малюємо кружками — забагато)
    xs1 = [300, 600]
    xs2 = [180, 420, 480, 720]
    xs3 = [120, 240, 360, 480, 540, 660, 720, 840]

    y0, y1, y2, y3 = top, top + rh, top + 2 * rh, top + 3 * rh

    # які піддерева «відрубані» (сірі): позначимо, що частина гілок гине рано
    # відрубаємо праву гілку кореня цілком (демонстрація pruning)
    def edge(x1, y1, x2, y2, cut=False):
        return line(x1, y1, x2, y2, color=(CUT if cut else INK), sw=(1.4 if cut else 1.8),
                    dash=("5 5" if cut else None))

    def node(x, y, cut=False):
        return circle(x, y, 9, fill=(ROW if cut else BG), stroke=(CUT if cut else INK), sw=1.8)

    # корінь → рівень1
    f.append(edge(ox, y0, xs1[0], y1))
    f.append(edge(ox, y0, xs1[1], y1, cut=True))
    # мітки ребер кореня
    f.append(text((ox + xs1[0]) / 2 - 14, (y0 + y1) / 2, "A=0", size=12, color=NEG, anchor="middle"))
    f.append(text((ox + xs1[1]) / 2 + 16, (y0 + y1) / 2, "A=1", size=12, color=POS, anchor="middle"))

    # рівень1 → рівень2  (ліва гілка жива, права — сіра)
    f.append(edge(xs1[0], y1, xs2[0], y2))
    f.append(edge(xs1[0], y1, xs2[1], y2))
    f.append(edge(xs1[1], y1, xs2[2], y2, cut=True))
    f.append(edge(xs1[1], y1, xs2[3], y2, cut=True))

    # рівень2 → рівень3
    live2 = [(xs2[0], [xs3[0], xs3[1]], False),
             (xs2[1], [xs3[2], xs3[3]], False),
             (xs2[2], [xs3[4], xs3[5]], True),
             (xs2[3], [xs3[6], xs3[7]], True)]
    for px, kids, cut in live2:
        for kx in kids:
            f.append(edge(px, y2, kx, y3, cut=cut))

    # вузли
    f.append(node(ox, y0))
    for x in xs1:
        f.append(node(x, y1, cut=(x == xs1[1])))
    for i, x in enumerate(xs2):
        f.append(node(x, y2, cut=(i >= 2)))
    for i, x in enumerate(xs3):
        f.append(node(x, y3, cut=(i >= 4)))

    # мітки рівнів ліворуч
    for yy, lab in [(y1, "A"), (y2, "B"), (y3, "C")]:
        f.append(text(70, yy + 5, lab, size=14, bold=True, color=MUTED, anchor="middle"))
    f.append(text(70, y0 + 5, "старт", size=11, color=MUTED, anchor="middle"))
    f.append(text(70, y3 + 34, "…", size=16, color=MUTED, anchor="middle"))

    # позначки: живий листок-свідок (зелений) і відрубане піддерево
    f.append(circle(xs3[0], y3, 9, fill=SATFILL, stroke=FIELD, sw=2.4))
    tb, tw, th = textbox(xs3[1] + 150, y3 + 4,
                         "листок = повний набір\n(тут — знайдений свідок)",
                         size=11.5, pad=8, fill=SATFILL, stroke=FIELD, color=INK)
    f.append(line(xs3[0] + 9, y3, xs3[1] + 150 - tw / 2, y3 + 4, color=FIELD, sw=1.4))
    f.append(tb)

    # плашка про відрубування
    by = 452
    f.append(rect(60, by, 780, 40, fill=ROW, stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, by + 25,
                  "Сірим — гілки, що відпадають рано: щойно частковий набір провалює умову, усе піддерево під ним "
                  "не переглядають. Саме на цьому тримається швидкодія.",
                  size=12, color=INK))
    render(os.path.join(IMG, "search-tree.svg"), W, H, *f)


# ── 2. Будова CNF: клаузи, літерали, правило ─────────────────────────────────
def fig_cnf_anatomy():
    W, H = 900, 470
    f = [text(W / 2, 32, "Будова формули в CNF та правило її істинності", size=18, bold=True),
         text(W / 2, 54, "велике І над клаузами; кожна клауза — АБО літералів",
              size=12, color=MUTED, italic=True)]

    # три клаузи як окремі рамки, з'єднані ∧
    clauses = ["A ∨ ¬B", "B ∨ C", "¬A ∨ ¬C"]
    cx0 = 150
    cw, ch = 170, 66
    gap = 60
    y = 110
    centers = []
    for i, cl in enumerate(clauses):
        x = cx0 + i * (cw + gap)
        centers.append((x + cw / 2, y + ch / 2))
        f.append(rect(x, y, cw, ch, fill=CLA, stroke=NEG, sw=1.8, rx=10))
        f.append(text(x + cw / 2, y + ch / 2 + 8, cl, size=21, bold=True))
        f.append(text(x + cw / 2, y - 12, "клауза %d" % (i + 1), size=12, color=MUTED))
        if i < len(clauses) - 1:
            xa = x + cw
            f.append(text(xa + gap / 2, y + ch / 2 + 9, "∧", size=26, bold=True, color=INK))

    # виноски: літерал і що таке заперечення (ведемо ПОВЗ рамки, вниз)
    f.append(text(cx0 + cw / 2, y + ch + 40, "↑ два літерали, з'єднані ∨", size=12, color=MUTED))
    f.append(text(cx0 + cw / 2, y + ch + 60, "¬B — заперечення змінної B", size=12, color=MUTED))

    # рамка-правило
    ry = 250
    f.append(rect(60, ry, 780, 66, fill=ROW, stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, ry + 27,
                  "формула істинна  ⟺  істинна КОЖНА клауза   (усі вимоги вдоволено водночас)",
                  size=13.5, bold=True))
    f.append(text(W / 2, ry + 50,
                  "клауза істинна  ⟺  істинний БОДАЙ ОДИН її літерал   (хоч один варіант справдився)",
                  size=13.5, bold=True))

    # набір-свідок і як він запалює клаузи
    sy = 350
    f.append(text(150, sy, "набір A=1, B=1, C=0:", size=13.5, bold=True, anchor="start"))
    checks = ["клауза 1: 1 ∨ 0 = 1 ✓", "клауза 2: 1 ∨ 0 = 1 ✓", "клауза 3: 0 ∨ 1 = 1 ✓"]
    for i, ch_txt in enumerate(checks):
        cxp = cx0 + i * (cw + gap) + cw / 2
        f.append(text(cxp, sy + 26, ch_txt, size=12.5, color=FIELD, bold=True))

    by = 402
    tb, tw, th = textbox(W / 2, by + 24,
                         "усі три клаузи істинні  →  формула здійсненна, (1,1,0) — свідок",
                         size=13, pad=12, fill=SATFILL, stroke=FIELD, color=INK, bold=True, min_w=680)
    f.append(tb)
    render(os.path.join(IMG, "cnf-anatomy.svg"), W, H, *f)


# ── 3. SAT у центрі: зведення й P проти NP ───────────────────────────────────
def fig_sat_hub():
    W, H = 900, 500
    f = [text(W / 2, 32, "SAT — універсальний ключ: до нього зводиться будь-що з NP", size=18, bold=True),
         text(W / 2, 54, "перша NP-повна задача (Кук і Левін, 1971)", size=12, color=MUTED, italic=True)]

    # центр
    cx, cy = W / 2, 250
    f.append(circle(cx, cy, 62, fill=SATFILL, stroke=FIELD, sw=3))
    f.append(text(cx, cy - 4, "SAT", size=26, bold=True, color=INK))
    f.append(text(cx, cy + 20, "чи здійсненна?", size=11.5, color=MUTED))

    # задачі-супутники навколо — заводимо ПОВЗ коло, стрілки всередину
    around = [
        ("розфарбування\nграфів", 175, 150),
        ("складання\nрозкладів", 725, 150),
        ("планування\nдій", 130, 300),
        ("покриття\nмножини", 770, 300),
        ("головоломки\n(судоку)", 230, 410),
        ("розведення\nплат", 670, 410),
    ]
    import math
    for lab, x, y in around:
        tb, tw, th = textbox(x, y, lab, size=12, pad=9, fill=ROW, stroke=MUTED, color=INK)
        f.append(tb)
        # стрілка від краю плашки до краю кола
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx = x + ux * (tw / 2 + 6)
        sy = y + uy * (th / 2 + 6)
        ex = cx - ux * 68
        ey = cy - uy * 68
        f.append(arrow(sx, sy, ex, ey, color=MUTED, sw=1.8))

    # підпис стрілок
    f.append(text(cx, cy + 108, "кожну задачу NP за поліномний час перекладають у формулу SAT",
                  size=12, color=MUTED, italic=True))

    # плашка про P проти NP
    by = 452
    f.append(rect(60, by, 780, 40, fill="#fdf3ec", stroke=POS, sw=1.6, rx=10))
    f.append(text(W / 2, by + 25,
                  "Тому один швидкий розв'язувач SAT розв'язав би їх усі одразу. Чи можливий він — це «P проти NP», "
                  "задача тисячоліття (премія $1 000 000).",
                  size=12, color=INK))
    render(os.path.join(IMG, "sat-hub.svg"), W, H, *f)


# ── 4. Хроніка Кука–Левіна: дві незалежні стежки (для вставки hist) ──────────
def fig_timeline():
    W, H = 1040, 580
    axis_y = 300
    f = [text(W / 2, 30, "Народження NP-повноти: дві незалежні стежки, 1956–2000", size=18, bold=True),
         text(W / 2, 52, "над віссю — Захід · під віссю — СРСР · у колонці 1971 стежки сходяться",
              size=12, color=MUTED, italic=True)]

    cols = [(1956, 150), (1971, 380), (1972, 575), (1973, 785), (2000, 930)]
    colx = dict(cols)

    # смуга-підсвітка колонки 1971 (малюємо ПЕРШОЮ, під усім)
    f.append(rect(300, 96, 160, 396, fill=BAND, stroke="#d8e0f0", sw=1, rx=10))

    aboveY, belowY = 150, 440
    node_r = 19

    def place(x, cy, s, above, fill, stroke):
        body, w, h = textbox(x, cy, s, size=12, pad=9, fill=fill, stroke=stroke, sw=1.7, color=INK)
        if above:
            f.append(line(x, cy + h / 2, x, axis_y - node_r, color=MUTED, sw=1.5))
        else:
            f.append(line(x, cy - h / 2, x, axis_y + node_r, color=MUTED, sw=1.5))
        f.append(body)

    # Захід (над віссю)
    place(colx[1956], aboveY, "Ґедель → фон Нейман\nлист: «швидко чи перебором?»", True, WEST_F, WEST_S)
    place(colx[1971], aboveY, "Кук (Торонто), STOC\nSAT — NP-повна", True, WEST_F, WEST_S)
    place(colx[1972], aboveY, "Карп\n21 NP-повна задача", True, WEST_F, WEST_S)
    place(colx[2000], aboveY, "Інститут Клея\nP=NP: премія $1 000 000", True, "#fdf3ec", POS)

    # СРСР (під віссю)
    place(colx[1956], belowY, "школа «перебору»\n(Колмогоров, 1950-і)", False, SOV_F, SOV_S)
    place(colx[1971], belowY, "Левін (Москва)\nідея на семінарах", False, SOV_F, SOV_S)
    place(colx[1972], belowY, "Левін подає до друку\n(червень)", False, SOV_F, SOV_S)
    place(colx[1973], belowY, "Левін друкує «Універсальні\nзадачі перебора»", False, SOV_F, SOV_S)

    # вісь сегментами між вузлами (лінія НЕ проходить крізь числа-роки),
    # з розривом на великому проміжку 1973 → 2000
    xs = [x for _, x in cols]
    ends = [60] + [c for x in xs for c in (x - node_r, x + node_r)] + [990]
    segs = [(ends[i], ends[i + 1]) for i in range(0, len(ends), 2)]
    for x1, x2 in segs:
        if x1 < 820 or x2 > 900:          # пропускаємо ділянку розриву 1973→2000
            f.append(line(x1, axis_y, min(x2, 838) if x1 < 820 else x2, axis_y, color=INK, sw=2))
    f.append(line(878, axis_y, 911, axis_y, color=INK, sw=2))
    f.append(text(858, axis_y - 10, "≈27 років", size=10.5, color=MUTED, italic=True))
    f.append(text(858, axis_y + 5, "//", size=15, color=MUTED, bold=True))

    # вузли-роки на осі (кружок білий, поверх осі; число всередині)
    for yr, x in cols:
        f.append(circle(x, axis_y, node_r, fill=BG, stroke=INK, sw=2))
        f.append(text(x, axis_y + 5, str(yr), size=12.5, bold=True))

    # підсумкова плашка
    by = 512
    f.append(rect(60, by, 920, 44, fill=ROW, stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, by + 27,
                  "Кук (1971) опублікував першим і з повним доведенням; Левін (1973) дійшов незалежно "
                  "й дав оптимальнісну форму — тому теорема Кука–Левіна.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "cook-levin-timeline.svg"), W, H, *f)


FORCE = "#1f8a4c"    # вимушений крок (одинична клауза / чистий літерал)


# ── 5. Трасування DPLL: вибір · поширення · суперечність · повернення · свідок ─
def fig_dpll_trace():
    W, H = 900, 560
    f = [text(W / 2, 30, "DPLL: вибір, поширення, суперечність, повернення, свідок", size=17, bold=True),
         text(W / 2, 52, "F = (¬x₁ ∨ x₂) ∧ (¬x₂ ∨ x₃) ∧ (¬x₃ ∨ ¬x₁)", size=14, color=MUTED, italic=True)]

    rx, ry = 450, 104
    f.append(circle(rx, ry, 19, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(rx, ry + 5, "x₁?", size=14, bold=True))
    f.append(text(rx, ry - 28, "вибір змінної", size=11.5, color=MUTED))

    # ── ліва гілка: x₁=1 → вимушений ланцюг → суперечність
    lx = 300
    l1y, l2y, l3y = 205, 292, 380
    f.append(line(rx - 8, ry + 15, lx + 8, l1y - 17, color=POS, sw=2))
    f.append(text((rx + lx) / 2 - 24, (ry + l1y) / 2 - 2, "x₁=1", size=12.5, color=POS, bold=True))

    f.append(circle(lx, l1y, 17, fill=BG, stroke=FORCE, sw=2))
    f.append(text(lx, l1y + 5, "x₂=1", size=12, bold=True, color=FORCE))
    f.append(circle(lx, l2y, 17, fill=BG, stroke=FORCE, sw=2))
    f.append(text(lx, l2y + 5, "x₃=1", size=12, bold=True, color=FORCE))
    f.append(line(lx, l1y + 17, lx, l2y - 17, color=FORCE, sw=2.4))
    f.append(line(lx, l2y + 17, lx, l3y - 19, color=FORCE, sw=2.4))
    f.append(text(lx + 34, l1y + 4, "← вимушено (одинична клауза)", size=11, color=MUTED, anchor="start"))
    f.append(text(lx + 34, l2y + 4, "← вимушено (одинична клауза)", size=11, color=MUTED, anchor="start"))

    f.append(circle(lx, l3y, 19, fill="#fdecea", stroke=POS, sw=2.6))
    f.append(text(lx, l3y + 6, "⊥", size=19, bold=True, color=POS))
    f.append(text(lx, l3y + 38, "порожня клауза — суперечність", size=11.5, color=POS))

    # ── права гілка: x₁=0 → чистий літерал → свідок
    ux = 640
    u1y, wy = 205, 322
    f.append(line(rx + 8, ry + 15, ux - 8, u1y - 17, color=NEG, sw=2))
    f.append(text((rx + ux) / 2 + 24, (ry + u1y) / 2 - 2, "x₁=0", size=12.5, color=NEG, bold=True))

    f.append(circle(ux, u1y, 17, fill=BG, stroke=FORCE, sw=2))
    f.append(text(ux, u1y + 5, "x₂=0", size=12, bold=True, color=FORCE))
    f.append(text(ux + 34, u1y + 4, "← чистий літерал ¬x₂", size=11, color=MUTED, anchor="start"))
    f.append(line(ux, u1y + 17, ux, wy - 19, color=FORCE, sw=2.4))
    f.append(circle(ux, wy, 19, fill="#eaf6ee", stroke=FIELD, sw=2.8))
    f.append(text(ux, wy + 6, "✓", size=17, bold=True, color=FIELD))
    tb, tw, th = textbox(ux, wy + 54, "свідок:  x₁=0, x₂=0, x₃ — вільна", size=12,
                         pad=10, fill="#eaf6ee", stroke=FIELD, color=INK, bold=True)
    f.append(tb)

    # ── повернення (backtrack): від суперечності повз усе — до вибору x₁
    bx = 150
    f.append(line(lx - 19, l3y, bx, l3y, color=MUTED, sw=1.6, dash="5 5"))
    f.append(line(bx, l3y, bx, 122, color=MUTED, sw=1.6, dash="5 5"))
    f.append(arrow(bx, 122, rx - 19, ry - 4, color=MUTED, sw=1.6))
    f.append(text(bx + 10, (l3y + 122) / 2 - 6, "повернення", size=11.5, color=MUTED, anchor="start"))
    f.append(text(bx + 10, (l3y + 122) / 2 + 10, "(backtrack)", size=11.5, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "dpll-trace.svg"), W, H, *f)


# ── 6. CDCL: аналіз суперечності, вивчена клауза, нехронологічний стрибок ──────
def fig_cdcl_conflict():
    W, H = 980, 540
    f = [text(W / 2, 30, "CDCL: аналіз суперечності, вивчена клауза, стрибок назад", size=17, bold=True),
         text(W / 2, 52, "конфлікт залежить від рішень x₁ (рівень 1) і x₃ (рівень 3) — рівень 2 ні до чого",
              size=12.5, color=MUTED, italic=True)]

    def dec(x, y, lab, lvl, dim=False):
        col = MUTED if dim else NEG
        s = circle(x, y, 19, fill=("#f0f1f3" if dim else "#eaf0fd"), stroke=col, sw=2.2)
        s += text(x, y + 5, lab, size=13, bold=True, color=(MUTED if dim else INK))
        s += text(x, y - 27, "рішення · рівень %d" % lvl, size=11, color=MUTED)
        return s

    x1x, x1y = 150, 150
    x2x, x2y = 150, 300
    x3x, x3y = 150, 452
    f.append(dec(x1x, x1y, "x₁=1", 1))
    f.append(dec(x2x, x2y, "x₂=1", 2, dim=True))
    f.append(dec(x3x, x3y, "x₃=1", 3))
    f.append(text(x2x + 30, x2y + 4, "← гілка ні до чого", size=11, color=MUTED, anchor="start"))

    ix, iy = 430, 452
    f.append(circle(ix, iy, 17, fill=BG, stroke=INK, sw=1.8))
    f.append(text(ix, iy + 5, "x₅=1", size=12, bold=True))
    kx, ky = 740, 358
    f.append(circle(kx, ky, 23, fill="#fdecea", stroke=POS, sw=2.6))
    f.append(text(kx, ky + 6, "⊥", size=20, bold=True, color=POS))
    f.append(text(kx, ky + 42, "суперечність (κ)", size=11.5, color=POS))

    f.append(arrow(x3x + 19, x3y, ix - 17, iy, color=INK, sw=1.7))
    f.append(arrow(ix + 17, iy, kx - 21, ky + 15, color=INK, sw=1.7))
    f.append(arrow(x1x + 19, x1y + 6, kx - 21, ky - 15, color=INK, sw=1.7))
    f.append(text((x3x + ix) / 2, x3y + 24, "ланцюг: ¬x₃∨x₄, ¬x₄∨x₅", size=10.5, color=MUTED))
    f.append(text((ix + kx) / 2 + 14, (iy + ky) / 2 + 26, "¬x₅∨…", size=10.5, color=MUTED))
    f.append(text(410, 236, "¬x₁∨¬x₅∨…", size=10.5, color=MUTED))

    f.append(line(612, 116, 612, 476, color=FIELD, sw=1.8, dash="6 5"))
    f.append(text(612, 104, "розріз", size=12, color=FIELD, bold=True))

    tb, tw, th = textbox(770, 168, "вивчена клауза:\n(¬x₁ ∨ ¬x₃)", size=13, pad=12,
                         fill="#eaf6ee", stroke=FIELD, color=INK, bold=True, min_w=200)
    f.append(tb)

    f.append(line(kx + 23, ky, 890, ky, color=NEG, sw=1.8, dash="4 4"))
    f.append(line(890, ky, 890, 84, color=NEG, sw=1.8, dash="4 4"))
    f.append(line(890, 84, x1x - 80, 84, color=NEG, sw=1.8, dash="4 4"))
    # обхід повз напис «рішення · рівень 1» (заходимо в x1 збоку, а не крізь підпис)
    f.append(line(x1x - 80, 84, x1x - 80, x1y, color=NEG, sw=1.8, dash="4 4"))
    f.append(arrow(x1x - 80, x1y, x1x - 19, x1y, color=NEG, sw=1.8))
    f.append(text(500, 74, "нехронологічний стрибок: назад аж на рівень 1, рівень 2 — повз",
                  size=12, color=NEG, italic=True))
    render(os.path.join(IMG, "cdcl-conflict.svg"), W, H, *f)


# ── 7. Чому навчання дає стрибок швидкості (той самий глухий кут vs вивчено) ───
def fig_why_learning():
    W, H = 980, 460
    f = [text(W / 2, 30, "Чому навчання на суперечностях дає стрибок швидкості", size=17, bold=True)]

    def small_tree(cx, top, dead_color, dead_fill, cut=False):
        out = ""
        root = (cx, top)
        c1 = (cx - 95, top + 78)
        c2 = (cx + 95, top + 78)
        leaves = [(cx - 140, top + 168), (cx - 50, top + 168),
                  (cx + 50, top + 168), (cx + 140, top + 168)]
        out += line(root[0], root[1] + 12, c1[0], c1[1] - 12, color=INK, sw=1.6)
        out += line(root[0], root[1] + 12, c2[0], c2[1] - 12, color=INK, sw=1.6)
        out += line(c1[0], c1[1] + 12, leaves[0][0], leaves[0][1] - 11, color=INK, sw=1.6)
        out += line(c1[0], c1[1] + 12, leaves[1][0], leaves[1][1] - 11, color=INK, sw=1.6)
        out += line(c2[0], c2[1] + 12, leaves[2][0], leaves[2][1] - 11, color=INK, sw=1.6)
        out += line(c2[0], c2[1] + 12, leaves[3][0], leaves[3][1] - 11, color=INK, sw=1.6)
        for (x, y) in (root, c1, c2):
            out += circle(x, y, 12, fill=BG, stroke=INK, sw=1.6)
        dead = {0, 2, 3}
        for i, (x, y) in enumerate(leaves):
            if i in dead:
                out += circle(x, y, 13, fill=dead_fill, stroke=dead_color, sw=2.2)
                out += text(x, y + 5, "⊥", size=14, bold=True, color=dead_color)
                if cut:
                    # штрих-«закреслення» з розривом навколо символу ⊥, щоб лінія не лягала на напис
                    g = 8
                    out += line(x - 15, y - 15, x - g, y - g, color=dead_color, sw=2)
                    out += line(x + g, y + g, x + 15, y + 15, color=dead_color, sw=2)
            else:
                out += circle(x, y, 12, fill=BG, stroke=INK, sw=1.6)
        return out

    f.append(text(245, 66, "DPLL: той самий глухий кут — щоразу наново", size=13, bold=True))
    f.append(small_tree(245, 100, POS, "#fdecea", cut=False))
    tb, tw, th = textbox(245, 344, "три різні гілки натикаються на ОДИН взір;\n"
                         "перебір не памʼятає — відкриває його щоразу", size=11.5,
                         pad=10, fill="#fdecea", stroke=POS, color=INK, min_w=380)
    f.append(tb)

    f.append(line(490, 60, 490, 402, color=MUTED, sw=1.4, dash="4 5"))

    f.append(text(735, 66, "CDCL: вивчив один раз — відрубав усюди", size=13, bold=True))
    f.append(small_tree(735, 100, MUTED, "#f0f1f3", cut=True))
    tbc, twc, thc = textbox(735, 300, "вивчена клауза (¬a ∨ ¬b)", size=12.5, pad=10,
                            fill="#eaf6ee", stroke=FIELD, color=INK, bold=True, min_w=210)
    f.append(tbc)
    tb2, tw2, th2 = textbox(735, 362, "забороняє той самий взір раз і назавжди —\n"
                            "решта таких гілок гине без перебору", size=11.5,
                            pad=10, fill="#eaf6ee", stroke=FIELD, color=INK, min_w=380)
    f.append(tb2)
    render(os.path.join(IMG, "why-learning.svg"), W, H, *f)


# ── 8. Зведення: легкість назад, складність уперед (вставка math-reductions) ──
def fig_reduction_flow():
    W, H = 900, 380
    f = [text(W / 2, 30, "Зведення: легкість тече назад, складність — уперед", size=18, bold=True),
         text(W / 2, 54, "A ≤ₚ B  —  «A не важча за B»", size=12.5, color=MUTED, italic=True)]
    lb, lw, lh = textbox(200, 150, "Задача A\n(розклад, розфарбування,\nмаршрут, головоломка…)",
                         size=13, pad=14, fill=ROW, stroke=INK, sw=1.8, min_w=250)
    rb, rw, rh = textbox(700, 150, "SAT\nздійсненність\nCNF-формули φ",
                         size=13, pad=14, fill=SATFILL, stroke=FIELD, sw=2, min_w=250)
    f += [lb, rb]
    f.append(arrow(200 + lw / 2, 150, 700 - rw / 2, 150, color=INK, sw=2))
    f.append(text(450, 132, "зведення  f   (поліномний час)", size=12.5, bold=True))
    f.append(text(450, 178, "A розв'язна  ⟺  φ здійсненна", size=12.5, color=MUTED, italic=True))
    p1y = 250
    f.append(rect(70, p1y, 760, 42, fill=SATFILL, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, p1y + 26,
                  "умієш швидко SAT  →  умієш швидко й A       (легкість тече проти стрілки)",
                  size=13, bold=True))
    p2y = 306
    f.append(rect(70, p2y, 760, 42, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    f.append(text(W / 2, p2y + 26,
                  "A справді важка  →  SAT не легша за неї       (складність тече за стрілкою)",
                  size=13, bold=True))
    render(os.path.join(IMG, "reduction-flow.svg"), W, H, *f)


# ── 9. Розфарбування графа → CNF (наскрізний приклад) ────────────────────────
def fig_coloring_encode():
    W, H = 900, 560
    f = [text(W / 2, 30, "Розфарбування графа, закодоване як CNF", size=18, bold=True),
         text(W / 2, 54, "змінна на кожну пару (вершина, колір); умови розфарбування — клаузи",
              size=12, color=MUTED, italic=True)]
    # трикутник із розфарбуванням-свідком
    v1 = (170, 150); v2 = (105, 280); v3 = (235, 280)
    f.append(line(v1[0], v1[1], v2[0], v2[1], color=INK, sw=2))
    f.append(line(v1[0], v1[1], v3[0], v3[1], color=INK, sw=2))
    f.append(line(v2[0], v2[1], v3[0], v3[1], color=INK, sw=2))
    f.append(circle(v1[0], v1[1], 27, fill="#fdecea", stroke=POS, sw=2.6))
    f.append(circle(v2[0], v2[1], 27, fill="#eaf6ee", stroke=FIELD, sw=2.6))
    f.append(circle(v3[0], v3[1], 27, fill="#eaf0fd", stroke=NEG, sw=2.6))
    f.append(text(v1[0], v1[1] + 6, "1", size=18, bold=True))
    f.append(text(v2[0], v2[1] + 6, "2", size=18, bold=True))
    f.append(text(v3[0], v3[1] + 6, "3", size=18, bold=True))
    f.append(text(v1[0], v1[1] - 40, "R", size=15, bold=True, color=POS))
    f.append(text(v2[0] - 46, v2[1] + 6, "G", size=15, bold=True, color=FIELD))
    f.append(text(v3[0] + 46, v3[1] + 6, "B", size=15, bold=True, color=NEG))
    f.append(text(170, 345, "трикутник: 3 вершини, 3 ребра", size=12, color=MUTED))
    f.append(text(170, 368, "свідок  1→R  2→G  3→B", size=12.5, color=FIELD, bold=True))
    # три сім'ї клауз праворуч
    bx, bw = 320, 550
    f.append(fitbox(bx, 86, bw, 92,
                    "①  кожна вершина — бодай один колір\n"
                    "(R₁ ∨ G₁ ∨ B₁) ∧ (R₂ ∨ G₂ ∨ B₂) ∧ (R₃ ∨ G₃ ∨ B₃)",
                    size=14, pad=12, fill=CLA, stroke=NEG))
    f.append(fitbox(bx, 194, bw, 106,
                    "②  не два кольори на одній вершині\n"
                    "верш. 1:  (¬R₁ ∨ ¬G₁) ∧ (¬R₁ ∨ ¬B₁) ∧ (¬G₁ ∨ ¬B₁)\n"
                    "(технічно зайва для питання «чи розфарбовний?»)",
                    size=13.5, pad=12, fill=ROW, stroke=MUTED))
    f.append(fitbox(bx, 316, bw, 106,
                    "③  суміжні вершини — різного кольору\n"
                    "ребро 1–2:  (¬R₁ ∨ ¬R₂) ∧ (¬G₁ ∨ ¬G₂) ∧ (¬B₁ ∨ ¬B₂)\n"
                    "… по три клаузи на кожне ребро",
                    size=13.5, pad=12, fill=CLA, stroke=NEG))
    f.append(rect(60, 470, 780, 62, fill=SATFILL, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, 494, "9 змінних, 21 клауза — і росте лише поліномно:", size=13, bold=True))
    f.append(text(W / 2, 516, "n вершин · k кольорів → n·k змінних;  клауз ~ n + n·(k над 2) + m·k",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "coloring-encode.svg"), W, H, *f)


# ── 10. 3-SAT: розбиття клаузи й межа «2 проти 3» ────────────────────────────
def fig_clause_split():
    W, H = 900, 470
    f = [text(W / 2, 30, "3-SAT: розбиття довгої клаузи й межа «два проти трьох»", size=18, bold=True),
         text(W / 2, 54, "рівно три літерали в клаузі — і вся складність SAT лишається",
              size=12, color=MUTED, italic=True)]
    lb, lw, lh = textbox(450, 96, "(ℓ₁ ∨ ℓ₂ ∨ ℓ₃ ∨ ℓ₄ ∨ ℓ₅)", size=19, bold=True,
                         pad=12, fill=CLA, stroke=NEG, sw=2)
    f.append(lb)
    f.append(arrow(450, 96 + lh / 2, 450, 158, color=INK, sw=2))
    f.append(text(620, 138, "доточуємо свіжі y₁, y₂", size=12.5, color=MUTED, italic=True))
    cy = 190
    c1, _, _ = textbox(190, cy, "(ℓ₁ ∨ ℓ₂ ∨ y₁)", size=15, bold=True, pad=10, fill=ROW, stroke=INK)
    c2, _, _ = textbox(450, cy, "(¬y₁ ∨ ℓ₃ ∨ y₂)", size=15, bold=True, pad=10, fill=ROW, stroke=INK)
    c3, _, _ = textbox(710, cy, "(¬y₂ ∨ ℓ₄ ∨ ℓ₅)", size=15, bold=True, pad=10, fill=ROW, stroke=INK)
    f += [c1, c2, c3]
    f.append(text(320, cy + 6, "∧", size=22, bold=True))
    f.append(text(580, cy + 6, "∧", size=22, bold=True))
    f.append(text(W / 2, 240,
                  "y — «естафета»: без жодного істинного ℓ ланцюг падає в суперечність; "
                  "один істинний ℓ — і його досить",
                  size=12, color=MUTED, italic=True))
    f.append(text(W / 2, 296, "чому три, а не два", size=15, bold=True))
    f.append(fitbox(70, 322, 360, 96,
                    "2-клауза  (a ∨ b)\n= вимушена імплікація  ¬a ⇒ b\n"
                    "розкручується детерміновано\n→ 2-SAT за лінійний час (у P)",
                    size=13, pad=10, fill="#eaf6ee", stroke=FIELD))
    f.append(fitbox(470, 322, 360, 96,
                    "3-клауза  (a ∨ b ∨ c)\n= ¬a ⇒ (b ∨ c)\n"
                    "наслідок — диз'юнкція → гілкування\n→ повертається 2ⁿ-вибух (NP-повна)",
                    size=13, pad=10, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, "clause-split.svg"), W, H, *f)


if __name__ == "__main__":
    fig_search_tree()
    fig_cnf_anatomy()
    fig_sat_hub()
    fig_timeline()
    fig_dpll_trace()
    fig_cdcl_conflict()
    fig_why_learning()
    fig_reduction_flow()
    fig_coloring_encode()
    fig_clause_split()
    print("OK: 10 figures ->", IMG)
