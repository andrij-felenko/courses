# -*- coding: utf-8 -*-
"""Фігури ДЕТАЛЬНОЇ статті «Планування шляху: сітка і A*».
Чистий Python + svgkit. Окремі імена файлів, щоб не чіпати фігури базової."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)

OCC   = "#c9ced6"   # зайнята клітина
OCCED = "#8a94a6"
OPEN  = "#dbe7f6"   # відкрита/оглянута клітина (світло-синя)
PLAT  = "#f6e8c8"   # «плато» рівного f (пісочна)
PATHC = "#c0392b"   # шлях/акцент


def grid_lines(ox, oy, cell, cols, rows, color="#c8ccd2", sw=1.0):
    frags = []
    for c in range(cols + 1):
        frags.append(line(ox + c * cell, oy, ox + c * cell, oy + rows * cell, color=color, sw=sw))
    for r in range(rows + 1):
        frags.append(line(ox, oy + r * cell, ox + cols * cell, oy + r * cell, color=color, sw=sw))
    return frags


def fill_cell(ox, oy, cell, cx, cy, color, stroke="#c8ccd2", sw=1.0):
    return rect(ox + cx * cell, oy + cy * cell, cell, cell, fill=color, stroke=stroke, sw=sw, rx=0)


def dot(ox, oy, cell, cx, cy, color, r=None):
    if r is None:
        r = cell * 0.16
    return circle(ox + (cx + 0.5) * cell, oy + (cy + 0.5) * cell, r, fill=color, stroke=color, sw=1)


def cell_label(ox, oy, cell, cx, cy, s, size=11, color=INK, bold=False):
    return text(ox + (cx + 0.5) * cell, oy + (cy + 0.5) * cell + size * 0.35, s,
                size=size, color=color, bold=bold)


# ── 1) discretization-gap.svg — сітка ≠ світ (роздільність і втрата проходу) ──
def fig_discretization_gap():
    W, H = 820, 430
    frags = [text(W / 2, 26, "Дискретизація втрачає те, що менше за клітину", size=17, bold=True)]
    cell = 34

    # ── ліворуч: тонкий прохід, який груба сітка «замуровує» ──
    ox, oy = 45, 70
    cols, rows = 8, 8
    frags.append(text(ox + cols * cell / 2, oy - 12, "груба сітка: прохід зник", size=13, color=MUTED, bold=True))
    frags += grid_lines(ox, oy, cell, cols, rows)
    # дві стіни з тонкою щілиною між ними (щілина вужча за клітину, тому обидві клітини «зайняті»)
    for r in range(rows):
        if r != 3:  # фізична щілина проходить рядком 3, але клітина однаково зачеплена стіною
            frags.append(fill_cell(ox, oy, cell, 4, r, OCC))
    # реальна тонка щілина (фізичний просвіт), намальована поверх — вужча за клітину
    gap_x = ox + 4 * cell + cell * 0.30
    frags.append(rect(gap_x, oy + 3 * cell + cell * 0.32, cell * 0.40, cell * 0.36,
                      fill="#ffffff", stroke=PATHC, sw=1.6, rx=2))
    frags.append(text(gap_x + cell * 0.20, oy + 3 * cell - 4, "щілина", size=9, color=PATHC, bold=True))
    # старт/ціль по різні боки
    frags.append(dot(ox, oy, cell, 1, 3, FIELD))
    frags.append(cell_label(ox, oy, cell, 1, 3, "S", size=11, color="#ffffff", bold=True))
    frags.append(dot(ox, oy, cell, 6, 3, POS))
    frags.append(cell_label(ox, oy, cell, 6, 3, "G", size=11, color="#ffffff", bold=True))
    # хрестик на замурованій клітині 4,3
    frags.append(text(ox + 4.5 * cell, oy + 3.5 * cell + 5, "×", size=22, color=PATHC, bold=True))
    frags.append(text(ox + cols * cell / 2, oy + rows * cell + 22,
                      "клітина ширша за щілину → прохід «зайнятий»", size=10, color=MUTED))

    # ── праворуч: та сама щілина під дрібнішою сіткою — прохід є ──
    ox2 = ox + cols * cell + 90
    cell2 = 18
    cols2, rows2 = 16, 16
    oy2 = oy
    frags.append(text(ox2 + cols2 * cell2 / 2, oy2 - 12, "дрібна сітка: прохід є", size=13, color=MUTED, bold=True))
    frags += grid_lines(ox2, oy2, cell2, cols2, rows2)
    for r in range(rows2):
        if not (6 <= r <= 7):  # щілина завширшки дві дрібні клітини
            frags.append(fill_cell(ox2, oy2, cell2, 8, r, OCC))
    frags.append(dot(ox2, oy2, cell2, 2, 6, FIELD))
    frags.append(dot(ox2, oy2, cell2, 13, 7, POS))
    # ламана крізь щілину
    pts = [(2, 6), (7, 6), (8, 6), (9, 7), (13, 7)]
    d = "M " + " L ".join("%.0f %.0f" % (ox2 + (a + 0.5) * cell2, oy2 + (b + 0.5) * cell2) for a, b in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, PATHC))
    frags.append(text(ox2 + cols2 * cell2 / 2, oy2 + rows2 * cell2 + 22,
                      "удвічі дрібніше → вчетверо більше пам'яті", size=10, color=MUTED))

    render(out("discretization-gap.svg"), W, H, *frags)


# ── 2) grid-vs-anyangle.svg — сітковий шлях довший за пряму (≈8 %) ───────────
def fig_grid_vs_anyangle():
    W, H = 760, 430
    frags = [text(W / 2, 26, "Сітка коштує довжини: сходинки проти прямої", size=17, bold=True)]
    cell = 40
    ox, oy = 60, 60
    cols, rows = 8, 7
    frags += grid_lines(ox, oy, cell, cols, rows)
    # старт (0,6) — ціль (7,0): чиста діагональ + зсув, щоб «драбинка» була видна
    S = (0, 6); G = (7, 0)
    frags.append(dot(ox, oy, cell, *S, FIELD, r=cell * 0.18))
    frags.append(cell_label(ox, oy, cell, S[0], S[1], "S", 12, "#ffffff", True))
    frags.append(dot(ox, oy, cell, *G, POS, r=cell * 0.18))
    frags.append(cell_label(ox, oy, cell, G[0], G[1], "G", 12, "#ffffff", True))

    # сітковий шлях «драбинкою» (8-зв'язність, але з ортогональними вставками — сходинки)
    step_pts = [(0, 6), (1, 5), (2, 5), (3, 4), (4, 3), (4, 2), (5, 1), (6, 1), (7, 0)]
    d1 = "M " + " L ".join("%.0f %.0f" % (ox + (a + 0.5) * cell, oy + (b + 0.5) * cell) for a, b in step_pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d1, PATHC))

    # пряма any-angle від центру S до центру G
    x1, y1 = ox + (S[0] + 0.5) * cell, oy + (S[1] + 0.5) * cell
    x2, y2 = ox + (G[0] + 0.5) * cell, oy + (G[1] + 0.5) * cell
    frags.append(line(x1, y1, x2, y2, color=FIELD, sw=2.6, dash="7 5"))

    # легенда праворуч
    lx = ox + cols * cell + 24
    frags.append(line(lx, oy + 30, lx + 28, oy + 30, color=PATHC, sw=2.6))
    frags.append(text(lx + 36, oy + 34, "сітковий шлях", size=12, color=INK, anchor="start"))
    frags.append(line(lx, oy + 58, lx + 28, oy + 58, color=FIELD, sw=2.6, dash="7 5"))
    frags.append(text(lx + 36, oy + 62, "пряма (any-angle)", size=12, color=INK, anchor="start"))

    box, bw, bh = textbox(lx + 70, oy + 150,
                          "8-зв'язна сітка\nу найгіршому разі\nдовша за пряму\nдо ≈ 8 %",
                          size=12, fill="#fbf3e0", stroke="#d9b25a", color="#7a5b12")
    frags.append(box)

    frags.append(text(W / 2, oy + rows * cell + 34,
                      "Кути зафіксовані на сітці, тож маршрут в'ється сходинками замість прямої лінії.",
                      size=11, color=MUTED))
    render(out("grid-vs-anyangle.svg"), W, H, *frags)


# ── 3) tie-break-plateau.svg — плато рівного f і як його розбиває нахил ──────
def fig_tie_break():
    W, H = 820, 440
    frags = [text(W / 2, 26, "Нічия за f: плато проти витягнутого пошуку", size=17, bold=True)]
    cell = 30
    cols, rows = 9, 9

    def draw_panel(ox, oy, plateau, caption):
        fr = grid_lines(ox, oy, cell, cols, rows)
        S = (0, 8); G = (8, 0)
        # оглянуті клітини
        for (a, b) in plateau:
            col = PLAT if plateau[(a, b)] == "plat" else OPEN
            fr.append(fill_cell(ox, oy, cell, a, b, col))
        fr += grid_lines(ox, oy, cell, cols, rows)  # лінії поверх заливки
        fr.append(dot(ox, oy, cell, *S, FIELD, r=cell * 0.20))
        fr.append(cell_label(ox, oy, cell, S[0], S[1], "S", 11, "#ffffff", True))
        fr.append(dot(ox, oy, cell, *G, POS, r=cell * 0.20))
        fr.append(cell_label(ox, oy, cell, G[0], G[1], "G", 11, "#ffffff", True))
        fr.append(text(ox + cols * cell / 2, oy + rows * cell + 20, caption, size=11, color=MUTED))
        return fr

    # ліва панель: величезне плато (усі клітини «нижнього трикутника» мають рівне f)
    ox, oy = 45, 62
    plat = {}
    for a in range(cols):
        for b in range(rows):
            # клітини, де сітковий діагональний шлях лишається оптимальним → рівне f
            if a + (rows - 1 - b) <= 9 and abs((rows - 1 - b) - a) <= 8:
                plat[(a, b)] = "plat"
    frags += draw_panel(ox, oy, plat, "без розбиття нічиїх: ціле плато оглянуто")
    frags.append(text(ox + cols * cell / 2, oy - 12, "плато рівного f", size=13, color="#7a5b12", bold=True))

    # права панель: вузька смуга вздовж діагоналі
    ox2 = ox + cols * cell + 110
    band = {}
    for a in range(cols):
        b = rows - 1 - a
        for db in (-1, 0, 1):
            bb = b + db
            if 0 <= bb < rows:
                band[(a, bb)] = "open"
    frags += draw_panel(ox2, oy, band, "з нахилом h: пошук тримається лінії")
    frags.append(text(ox2 + cols * cell / 2, oy - 12, "розбита нічия", size=13, color=NEG, bold=True))

    # формула-підпис унизу
    box, bw, bh = textbox(W / 2, oy + rows * cell + 52,
                          "нахил: h ← h · (1 + p),   p < ціна_кроку / макс_довжина",
                          size=13, fill="#eef4ff", stroke="#9db8e0", color=NEG)
    frags.append(box)
    render(out("tie-break-plateau.svg"), W, H, *frags)


# ── 4) branching-factor.svg — чому фронт росте (ефективний коефіцієнт) ───────
def fig_branching():
    W, H = 780, 400
    frags = [text(W / 2, 26, "Скільки клітин оглянуто: ширина «еліпса» пошуку", size=17, bold=True)]
    # три «еліпси» різної ширини для трьох евристик, від того самого S до G
    ox, oy = 60, 70
    cw, ch = 560, 250
    frags.append(rect(ox, oy, cw, ch, fill="#fbfcfd", stroke=LINE, sw=1.4))
    Sx, Sy = ox + 70, oy + ch / 2
    Gx, Gy = ox + cw - 70, oy + ch / 2
    # три вкладені еліпси (нуль/слабка/сильна евристика)
    specs = [
        (120, "#e9edf3", MUTED, "h = 0 (Дейкстра): коло"),
        (78,  "#dce9dc", FIELD, "евклід: ширший еліпс"),
        (40,  "#f6ddd8", PATHC, "діагональна: вузький еліпс"),
    ]
    midx, midy = (Sx + Gx) / 2, (Sy + Gy) / 2
    rx = (Gx - Sx) / 2 + 30
    for ry, fill, stroke, _ in specs:
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                     'stroke-width="1.8" opacity="0.85"/>' % (midx, midy, rx, ry, fill, stroke))
    # S, G поверх
    frags.append(circle(Sx, Sy, 9, fill=FIELD, stroke=FIELD))
    frags.append(text(Sx, Sy - 16, "S", size=13, bold=True))
    frags.append(circle(Gx, Gy, 9, fill=POS, stroke=POS))
    frags.append(text(Gx, Gy - 16, "G", size=13, bold=True))
    frags.append(line(Sx, Sy, Gx, Gy, color=INK, sw=1.4, dash="4 4"))

    # легенда праворуч від еліпсів (унизу)
    ly = oy + ch + 22
    lx = ox
    for i, (ry, fill, stroke, lab) in enumerate(specs):
        yy = ly + i * 20
        frags.append(rect(lx, yy - 9, 22, 13, fill=fill, stroke=stroke, sw=1.5, rx=3))
        frags.append(text(lx + 30, yy + 2, lab, size=11, color=INK, anchor="start"))
    frags.append(text(lx + 360, ly + 20,
                      "точніша (знизу) h → вужчий еліпс → менше клітин", size=11, color=MUTED, anchor="start"))
    render(out("branching-factor.svg"), W, H, *frags)


# ── 5) jps-jump.svg — Jump Point Search «перестрибує» проміжні клітини ───────
def fig_jps():
    W, H = 800, 420
    frags = [text(W / 2, 26, "Jump Point Search: пропустити симетричні шляхи", size=17, bold=True)]
    cell = 34
    cols, rows = 10, 9

    def panel(ox, oy, expanded, jumps, caption, title):
        fr = grid_lines(ox, oy, cell, cols, rows)
        for (a, b) in expanded:
            fr.append(fill_cell(ox, oy, cell, a, b, OPEN))
        fr += grid_lines(ox, oy, cell, cols, rows)
        S = (1, 7); G = (8, 1)
        fr.append(dot(ox, oy, cell, *S, FIELD, r=cell * 0.19))
        fr.append(cell_label(ox, oy, cell, S[0], S[1], "S", 11, "#ffffff", True))
        fr.append(dot(ox, oy, cell, *G, POS, r=cell * 0.19))
        fr.append(cell_label(ox, oy, cell, G[0], G[1], "G", 11, "#ffffff", True))
        for (a, b) in jumps:
            fr.append(circle(ox + (a + 0.5) * cell, oy + (b + 0.5) * cell, cell * 0.28,
                             fill="none", stroke=PATHC, sw=2.4))
        fr.append(text(ox + cols * cell / 2, oy - 12, title, size=13, color=MUTED, bold=True))
        fr.append(text(ox + cols * cell / 2, oy + rows * cell + 20, caption, size=11, color=MUTED))
        return fr

    # ліва: звичайний A* розкриває багато клітин
    ox, oy = 40, 66
    exp = set()
    for a in range(1, 9):
        for b in range(1, 8):
            if abs((a - 1) - (7 - b)) <= 2 and (a + b) >= 3:
                exp.add((a, b))
    frags += panel(ox, oy, exp, [], "A*: багато однакових діагональних гілок", "звичайний A*")

    # права: JPS — лише кілька «стрибкових точок»
    ox2 = ox + cols * cell + 60
    jumps = [(1, 7), (7, 1), (8, 1)]
    frags += panel(ox2, oy, set(), [], "JPS: лише точки повороту (jump points)", "Jump Point Search")
    # діагональний «стрибок» лінією
    d = "M %.0f %.0f L %.0f %.0f L %.0f %.0f" % (
        ox2 + 1.5 * cell, oy + 7.5 * cell, ox2 + 7.5 * cell, oy + 1.5 * cell,
        ox2 + 8.5 * cell, oy + 1.5 * cell)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, PATHC))
    for (a, b) in jumps:
        frags.append(circle(ox2 + (a + 0.5) * cell, oy + (b + 0.5) * cell, cell * 0.28,
                            fill="none", stroke=PATHC, sw=2.6))

    render(out("jps-jump.svg"), W, H, *frags)


# ── 6) replanning-dstar.svg — глобальний план застарів, локальний править ────
def fig_replanning():
    W, H = 800, 400
    frags = [text(W / 2, 26, "План застаріває: перепланувати чи об'їхати", size=17, bold=True)]
    cell = 32
    cols, rows = 10, 9
    ox, oy = 60, 66
    frags += grid_lines(ox, oy, cell, cols, rows)
    # відомі стіни
    walls = [(4, 2), (4, 3), (4, 4), (4, 5)]
    for (a, b) in walls:
        frags.append(fill_cell(ox, oy, cell, a, b, OCC))
    S = (1, 7); G = (8, 1)
    frags.append(dot(ox, oy, cell, *S, FIELD, r=cell * 0.19))
    frags.append(cell_label(ox, oy, cell, S[0], S[1], "S", 11, "#ffffff", True))
    frags.append(dot(ox, oy, cell, *G, POS, r=cell * 0.19))
    frags.append(cell_label(ox, oy, cell, G[0], G[1], "G", 11, "#ffffff", True))

    # старий глобальний план (обходить відому стіну зверху)
    old = [(1, 7), (3, 6), (4, 6), (5, 5), (6, 4), (7, 2), (8, 1)]
    d_old = "M " + " L ".join("%.0f %.0f" % (ox + (a + 0.5) * cell, oy + (b + 0.5) * cell) for a, b in old)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 4"/>' % (d_old, MUTED))

    # нова перешкода з'явилась у польоті (на шляху)
    newobs = (6, 4)
    frags.append(fill_cell(ox, oy, cell, *newobs, "#f2c9c2", stroke=PATHC, sw=2.0))
    frags.append(text(ox + (newobs[0] + 0.5) * cell, oy + (newobs[1] + 0.5) * cell + 4,
                      "!", size=16, color=PATHC, bold=True))

    # локальний об'їзд (реактивний контур) — відхилення й повернення
    local = [(5, 5), (6, 5), (7, 4), (7, 3), (7, 2)]
    d_loc = "M " + " L ".join("%.0f %.0f" % (ox + (a + 0.5) * cell, oy + (b + 0.5) * cell) for a, b in local)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_loc, PATHC))

    # легенда
    lx = ox + cols * cell + 22
    frags.append(line(lx, oy + 24, lx + 26, oy + 24, color=MUTED, sw=2.4, dash="6 4"))
    frags.append(text(lx + 34, oy + 28, "старий глобальний план (A*)", size=11, color=INK, anchor="start"))
    frags.append(line(lx, oy + 50, lx + 26, oy + 50, color=PATHC, sw=2.8))
    frags.append(text(lx + 34, oy + 54, "локальний об'їзд (реактивно)", size=11, color=INK, anchor="start"))
    frags.append(rect(lx, oy + 68, 18, 14, fill="#f2c9c2", stroke=PATHC, sw=1.6, rx=2))
    frags.append(text(lx + 26, oy + 79, "нова перешкода в польоті", size=11, color=INK, anchor="start"))
    box, bw, bh = textbox(lx + 90, oy + 150,
                          "D*/D* Lite:\nне рахувати план\nзаново — полагодити\nлише зачеплену\nчастину",
                          size=11, fill="#eef4ff", stroke="#9db8e0", color=NEG)
    frags.append(box)

    render(out("replanning-dstar.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_discretization_gap()
    fig_grid_vs_anyangle()
    fig_tie_break()
    fig_branching()
    fig_jps()
    fig_replanning()
    print("OK: 6 фігур детальної статті у", IMG)
