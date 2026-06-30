# -*- coding: utf-8 -*-
"""Фігури до статті «Метод контурних струмів» (book/electronics/analog/mesh-analysis).
П'ять фігур:
  two-mesh.svg     — ідея: два «вікна» схеми, у кожному циркулює свій контурний струм
  shared-branch.svg — серце методу: у спільній гілці тече різниця контурних струмів
  system.svg       — структура системи рівнянь: діагональ +, позаосьові − (спільні опори)
  vs-node.svg      — коли обирати контури, а коли вузли (рахуємо вікна проти вузлів)
  hist-topology.svg — історія: одне число (b−n+1) трьома способами (кістяк/хорди ↔ грані Ейлера)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ────────────────────────────────────────────────────
def resistor_h(x0, x1, y, label=None, above=True, color=INK):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 7
    out.append(line(x0, y, x0 + seg, y, color=color, sw=1.7))
    xx = x0 + seg
    prev = y
    for i in range(n):
        ny = y - amp if i % 2 == 0 else y + amp
        out.append(line(xx, prev, xx + seg, ny, color=color, sw=1.7))
        xx += seg
        prev = ny
    out.append(line(xx, prev, x1, y, color=color, sw=1.7))
    if label:
        ly = y - 16 if above else y + 22
        out.append(text((x0 + x1) / 2, ly, label, size=13, color=color, bold=True))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="right", color=INK):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    amp = 7
    out.append(line(x, y0, x, y0 + seg, color=color, sw=1.7))
    yy = y0 + seg
    prev = x
    for i in range(n):
        nx = x + amp if i % 2 == 0 else x - amp
        out.append(line(prev, yy, nx, yy + seg, color=color, sw=1.7))
        yy += seg
        prev = nx
    out.append(line(prev, yy, x, y1, color=color, sw=1.7))
    if label:
        lx = x + 16 if side == "right" else x - 16
        an = "start" if side == "right" else "end"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=13, color=color, bold=True, anchor=an))
    return "".join(out)


def battery(x, y0, y1, label=None, plus_top=True, color=INK):
    """Джерело напруги (батарея): довга риска = +, коротка = −. Вертикально."""
    ym = (y0 + y1) / 2
    out = [line(x, y0, x, ym - 7, color=color, sw=1.7),
           line(x, ym + 7, x, y1, color=color, sw=1.7)]
    # дві пари рисок
    out.append(line(x - 13, ym - 7, x + 13, ym - 7, color=color, sw=2.6))   # довга
    out.append(line(x - 7, ym - 1, x + 7, ym - 1, color=color, sw=1.7))     # коротка
    out.append(line(x - 13, ym + 5, x + 13, ym + 5, color=color, sw=2.6))   # довга
    out.append(line(x - 7, ym + 11, x + 7, ym + 11, color=color, sw=1.7))   # коротка
    ptxt, mtxt_ = ("+", "−") if plus_top else ("−", "+")
    out.append(text(x + 22, y0 + 14, ptxt, size=15, color=POS if plus_top else NEG, bold=True))
    out.append(text(x + 22, y1 - 6, mtxt_, size=15, color=NEG if plus_top else POS, bold=True))
    if label:
        out.append(text(x - 20, ym + 4, label, size=13, color=color, bold=True, anchor="end"))
    return "".join(out)


def loop_arrow(cx, cy, r, color, label=None, cw=True, lab_dy=0):
    """Колова стрілка контурного струму (майже повне коло зі стрілкою на кінці)."""
    import math
    # дуга від 300° до -40° (за годинниковою), лишаємо розрив під стрілку
    a0, a1 = (-50, 250) if cw else (250, -50)
    pts = []
    steps = 36
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    out = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.4" '
           'marker-end="url(#arrow)" opacity="0.9"/>' % (d, color)]
    if label:
        out.append(text(cx, cy + lab_dy + 5, label, size=15, color=color, bold=True))
    return "".join(out)


def node_dot(x, y, color=INK):
    return circle(x, y, 3.0, fill=color, stroke=color)


# ════════════════════════════════════════════════════════════════════════════
# 1. two-mesh.svg — два вікна, у кожному свій контурний струм
# ════════════════════════════════════════════════════════════════════════════
def fig_two_mesh():
    W, H = 660, 360
    f = []
    # координати спільної сітки 2×1 (два вікна поряд)
    xL, xM, xR = 110, 360, 610
    yT, yB = 80, 290
    col = INK

    # верхня й нижня шини
    f.append(resistor_h(xL + 18, xM - 18, yT, label="R₁", above=True))
    f.append(resistor_h(xM + 18, xR - 18, yT, label="R₃", above=True))
    f.append(line(xL, yB, xR, yB, color=col, sw=1.7))            # низ — спільний провід
    # ліва вертикаль: джерело V₁
    f.append(battery(xL, yT, yB, label="V₁", plus_top=True))
    # права вертикаль: джерело V₂
    f.append(battery(xR, yT, yB, label="V₂", plus_top=True))
    # середня вертикаль — СПІЛЬНА гілка R₂
    f.append(resistor_v(xM, yT + 8, yB - 8, label="R₂", side="right", color=POS))
    # вузли
    for (x, y) in [(xL, yT), (xM, yT), (xR, yT), (xL, yB), (xM, yB), (xR, yB)]:
        f.append(node_dot(x, y))
    # горизонтальні стики від кутів до резисторів/джерел
    f.append(line(xL, yT, xL + 18, yT, color=col, sw=1.7))
    f.append(line(xM - 18, yT, xM, yT, color=col, sw=1.7))
    f.append(line(xM, yT, xM + 18, yT, color=col, sw=1.7))
    f.append(line(xR - 18, yT, xR, yT, color=col, sw=1.7))

    # контурні струми
    f.append(loop_arrow((xL + xM) / 2, (yT + yB) / 2 + 6, 48, NEG, label="I₁", lab_dy=-6))
    f.append(loop_arrow((xM + xR) / 2, (yT + yB) / 2 + 6, 48, FIELD, label="I₂", lab_dy=-6))
    f.append(text((xL + xM) / 2, yB + 26, "ліве «вікно»", size=11, color=NEG))
    f.append(text((xM + xR) / 2, yB + 26, "праве «вікно»", size=11, color=FIELD))

    f.append(text(W / 2, 30, "Кожному вікну схеми — свій струм, що тече по кільцю",
                  size=15, bold=True))
    f.append(text(W / 2, 332, "Спільну гілку R₂ ділять обидва контури — там струми накладаються",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "two-mesh.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. shared-branch.svg — у спільній гілці тече різниця контурних струмів
# ════════════════════════════════════════════════════════════════════════════
def fig_shared_branch():
    W, H = 620, 340
    f = []
    xM = W / 2
    yT, yB = 70, 280
    # сама спільна гілка — резистор вертикально
    f.append(resistor_v(xM, yT, yB, label="R₂", side="left", color=POS))
    f.append(node_dot(xM, yT)); f.append(node_dot(xM, yB))

    # I₁ зліва штовхає вниз крізь R₂
    f.append(loop_arrow(xM - 120, (yT + yB) / 2, 56, NEG, label="I₁"))
    f.append(arrow(xM - 14, yT + 26, xM - 14, yT + 70, color=NEG, sw=2.4))
    f.append(text(xM - 60, yT + 50, "I₁ вниз", size=12, color=NEG, anchor="middle"))

    # I₂ справа штовхає вгору крізь R₂
    f.append(loop_arrow(xM + 120, (yT + yB) / 2, 56, FIELD, label="I₂"))
    f.append(arrow(xM + 14, yB - 26, xM + 14, yB - 70, color=FIELD, sw=2.4))
    f.append(text(xM + 60, yB - 50, "I₂ вгору", size=12, color=FIELD, anchor="middle"))

    # підсумок — рамка
    body, w0, h0 = textbox(xM, 318,
                           "Справжній струм крізь R₂  =  I₁ − I₂   (вони течуть назустріч)",
                           size=13, color=INK, fill="#fdecea", stroke=POS, bold=True)
    f.append(body)
    f.append(text(W / 2, 34, "Спільна гілка: два контури течуть крізь неї назустріч",
                  size=15, bold=True))
    render(os.path.join(IMG, "shared-branch.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. system.svg — структура матриці опорів (діагональ +, позаосьові −)
# ════════════════════════════════════════════════════════════════════════════
def fig_system():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 34, "Система сама складається за простим правилом", size=15, bold=True))

    # два рівняння у вигляді «каркаса»
    eqx = 70
    y1, y2 = 130, 210
    f.append(text(eqx, y1, "(R₁+R₂)·I₁  −  R₂·I₂   =   V₁", size=16, color=INK, anchor="start"))
    f.append(text(eqx, y2, "−R₂·I₁   +  (R₂+R₃)·I₂  =   V₂", size=16, color=INK, anchor="start"))

    # підсвітити діагональні (свій контур) і позаосьові (спільні) доданки
    f.append(text(eqx, y1 + 30, "↑ власні опори контуру (+)", size=11, color=FIELD, anchor="start"))
    f.append(text(eqx + 250, y1 + 30, "↑ спільний опір зі знаком −", size=11, color=POS, anchor="start"))

    # права колонка — словесне правило
    rx = 430
    box = [
        "ДІАГОНАЛЬ:",
        "сума всіх опорів,",
        "що оточують цей контур  (+)",
        "",
        "ПОЗА ДІАГОНАЛЛЮ:",
        "опір, СПІЛЬНИЙ для двох",
        "контурів, зі знаком  −",
        "",
        "ПРАВА ЧАСТИНА:",
        "сума ЕРС у контурі",
        "(+ якщо штовхає за напрямком)",
    ]
    bx, by, bw = rx, 96, 230
    f.append(rect(bx, by, bw, 200, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=10))
    yy = by + 26
    cols = {0: FIELD, 4: POS, 8: NEG}
    for i, ln in enumerate(box):
        c = INK
        for k, cc in cols.items():
            if i == k:
                c = cc
        b = (i in cols)
        f.append(text(bx + 14, yy, ln, size=11, color=c, anchor="start", bold=b))
        yy += 17

    render(os.path.join(IMG, "system.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. vs-node.svg — коли контури, коли вузли (рахуй менше невідомих)
# ════════════════════════════════════════════════════════════════════════════
def fig_vs_node():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 32, "Що рахувати: контури чи вузли? Бери де менше невідомих",
                  size=15, bold=True))

    # ліва панель — схема «багато вузлів, мало вікон» → контури
    lx = 60
    f.append(rect(lx, 70, 250, 200, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + 125, 96, "багато вузлів, мало вікон", size=12, color=FIELD, bold=True))
    f.append(text(lx + 125, 116, "→ контурний метод", size=13, color=FIELD, bold=True))
    # маленька 2-вікон схемка
    gx0, gx1, gx2 = lx + 30, lx + 125, lx + 220
    gy0, gy1 = 150, 240
    for (a, b) in [((gx0, gy0), (gx2, gy0)), ((gx0, gy1), (gx2, gy1)),
                   ((gx0, gy0), (gx0, gy1)), ((gx1, gy0), (gx1, gy1)), ((gx2, gy0), (gx2, gy1))]:
        f.append(line(a[0], a[1], b[0], b[1], color=INK, sw=1.6))
    f.append(loop_arrow((gx0 + gx1) / 2, (gy0 + gy1) / 2, 24, FIELD))
    f.append(loop_arrow((gx1 + gx2) / 2, (gy0 + gy1) / 2, 24, FIELD))
    f.append(text(lx + 125, 262, "2 вікна = 2 рівняння", size=11, color=MUTED))

    # права панель — «мало вузлів, багато віток» → вузли
    rx = 370
    f.append(rect(rx, 70, 250, 200, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(rx + 125, 96, "мало вузлів, багато паралельних віток", size=11, color=NEG, bold=True))
    f.append(text(rx + 125, 116, "→ вузловий метод", size=13, color=NEG, bold=True))
    # схемка: дві шини, багато паралельних елементів
    bx0, bx1 = rx + 30, rx + 220
    byt, byb = 150, 240
    f.append(line(bx0, byt, bx1, byt, color=INK, sw=2.0))
    f.append(line(bx0, byb, bx1, byb, color=INK, sw=2.0))
    for xx in [rx + 60, rx + 95, rx + 130, rx + 165, rx + 200]:
        f.append(line(xx, byt, xx, byb, color=INK, sw=1.6))
    f.append(node_dot((bx0 + bx1) / 2, byt, NEG))
    f.append(text(rx + 125, 262, "1 вузол = 1 рівняння", size=11, color=MUTED))

    render(os.path.join(IMG, "vs-node.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. hist-topology.svg — одне число b−n+1 трьома способами (Кірхгоф ↔ Ейлер)
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_topology():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 30, "Одне число — три погляди: b − n + 1 незалежних контурів",
                  size=15, bold=True))

    # ── спільний граф: 4 вузли, 5 гілок (квадрат + одна діагональ-перетинка) ──
    # Розкладемо як два вікна поряд: вузли A B C (верх), D E F (низ) — як 2-mesh.
    # Беремо простий граф із 6 вузлами, 7 гілками → L = 7-6+1 = 2.
    def grid_nodes(ox, oy):
        # координати 6 вузлів сітки 3×2 у локальній системі
        x0, x1, x2 = ox + 20, ox + 110, ox + 200
        y0, y1 = oy + 30, oy + 130
        return {
            "A": (x0, y0), "B": (x1, y0), "C": (x2, y0),
            "D": (x0, y1), "E": (x1, y1), "F": (x2, y1),
        }
    EDGES = [("A", "B"), ("B", "C"), ("A", "D"), ("B", "E"), ("C", "F"),
             ("D", "E"), ("E", "F")]  # 7 гілок, 6 вузлів → 2 контури

    # ЛІВА панель — Кірхгоф: кістяк (жирні) + хорди (пунктир, кожна замикає контур)
    lx = 40
    f.append(rect(lx, 60, 300, 220, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(lx + 150, 84, "Кірхгоф, 1847: кістяк і хорди", size=12, color=FIELD, bold=True))
    N = grid_nodes(lx, 70)
    # кістяк (дерево без кілець): візьмемо A-B, B-C, A-D, B-E, C-F (5 гілок сполучають 6 вузлів)
    tree = {("A", "B"), ("B", "C"), ("A", "D"), ("B", "E"), ("C", "F")}
    for (a, b) in EDGES:
        x1_, y1_ = N[a]; x2_, y2_ = N[b]
        if (a, b) in tree:
            f.append(line(x1_, y1_, x2_, y2_, color=INK, sw=3.0))          # кістяк — жирний
        else:
            f.append(line(x1_, y1_, x2_, y2_, color=POS, sw=2.0, dash="5 4"))  # хорда
    for k, (x, y) in N.items():
        f.append(node_dot(x, y))
    # позначити хорди як «замикач контуру»
    for (a, b) in EDGES:
        if (a, b) not in tree:
            mx = (N[a][0] + N[b][0]) / 2; my = (N[a][1] + N[b][1]) / 2
            f.append(circle(mx, my, 9, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(lx + 150, 258, "кістяк (жирний) + 2 хорди = 2 контури", size=10.5, color=MUTED))

    # ПРАВА панель — Ейлер: ті самі вузли/гілки ділять площину на вікна
    rx = 360
    f.append(rect(rx, 60, 300, 220, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=10))
    f.append(text(rx + 150, 84, "Ейлер: грані плоскої карти", size=12, color=NEG, bold=True))
    M = grid_nodes(rx, 70)
    for (a, b) in EDGES:
        x1_, y1_ = M[a]; x2_, y2_ = M[b]
        f.append(line(x1_, y1_, x2_, y2_, color=INK, sw=1.8))
    for k, (x, y) in M.items():
        f.append(node_dot(x, y))
    # підписати два внутрішні вікна
    f.append(text((M["A"][0] + M["B"][0]) / 2, (M["A"][1] + M["D"][1]) / 2 + 4,
                  "вікно", size=11, color=NEG, bold=True))
    f.append(text((M["B"][0] + M["C"][0]) / 2, (M["B"][1] + M["E"][1]) / 2 + 4,
                  "вікно", size=11, color=NEG, bold=True))
    f.append(text(rx + 150, 258, "2 внутрішні грані = 2 вікна", size=10.5, color=MUTED))

    # нижня спільна формула
    body, w0, h0 = textbox(W / 2, 312,
                           "b − n + 1  =  7 − 6 + 1  =  2     (однаково обома шляхами)",
                           size=13, color=INK, fill=FILL, stroke=MUTED, bold=True)
    f.append(body)
    render(os.path.join(IMG, "hist-topology.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_mesh()
    fig_shared_branch()
    fig_system()
    fig_vs_node()
    fig_hist_topology()
    print("OK: 5 фігур у", IMG)
