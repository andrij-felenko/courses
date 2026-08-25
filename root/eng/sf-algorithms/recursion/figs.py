# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CALL   = "#eef4ff"   # рамка виклику (холодна)
RETV   = "#f4f6f8"   # рамка повернення (нейтральна)
BASEHL = "#eafaf0"   # база / готове значення (зелене)
HOT    = "#fdecea"   # повторна робота (тепле)
SOFT   = "#fbfcfd"


# ── fig_stack: стек викликів fact(4) — занурення і виринання ──────────────────
# Ідея: лінійна рекурсія — це стос відкладених множень. Спершу виклики ростуть
# стосом до бази (нічого ще не помножено), тоді з бази значення повертаються
# догори, і кожне відкладене множення нарешті виконується.

def fig_stack():
    W, H = 940, 560
    p = []

    # ── ліва колонка: занурення ──
    lx, lw = 60, 330
    p.append(text(lx + lw / 2, 66, "Занурення: виклики стосом ростуть", size=13, color=NEG, bold=True))
    p.append(text(lx + lw / 2, 84, "кожен чекає на менший, ще нічого не помножено", size=10.5, color=MUTED))
    calls = [
        ("fact(4)", "= 4 · fact(3)", False),
        ("fact(3)", "= 3 · fact(2)", False),
        ("fact(2)", "= 2 · fact(1)", False),
        ("fact(1)", "= 1   (база — стоп)", True),
    ]
    ry, rh, gap = 108, 66, 26
    for i, (name, body, base) in enumerate(calls):
        y = ry + i * (rh + gap)
        p.append(rect(lx, y, lw, rh, fill=(BASEHL if base else CALL),
                      stroke=(FIELD if base else NEG), sw=(2.0 if base else 1.5), rx=6))
        p.append(text(lx + 18, y + rh / 2 + 5, name, size=15,
                      color=(FIELD if base else INK), bold=True, anchor="start"))
        p.append(text(lx + 128, y + rh / 2 + 5, body, size=13, color=INK, anchor="start"))
        if i < len(calls) - 1:
            ax = lx + lw / 2
            p.append(arrow(ax, y + rh + 2, ax, y + rh + gap - 2, color=NEG, sw=1.8))
    p.append(text(lx + lw / 2, ry + 4 * (rh + gap) + 2, "далі викликати нема кого — розвертаємось",
                  size=10.5, color=FIELD, bold=True))

    # ── роздільник ──
    p.append(line(W / 2, 96, W / 2, H - 40, color="#d8dde3", sw=1.2, dash="5 5"))

    # ── права колонка: виринання ──
    rxp, rwp = 548, 330
    p.append(text(rxp + rwp / 2, 66, "Виринання: значення повертаються догори", size=13, color=FIELD, bold=True))
    p.append(text(rxp + rwp / 2, 84, "кожне відкладене множення нарешті рахується", size=10.5, color=MUTED))
    rets = [
        ("fact(4)", "→ 4 · 6 = 24", True),
        ("fact(3)", "→ 3 · 2 = 6", False),
        ("fact(2)", "→ 2 · 1 = 2", False),
        ("fact(1)", "→ 1", False),
    ]
    for i, (name, body, top) in enumerate(rets):
        y = ry + i * (rh + gap)
        p.append(rect(rxp, y, rwp, rh, fill=(BASEHL if top else RETV),
                      stroke=(FIELD if top else LINE), sw=(2.0 if top else 1.4), rx=6))
        p.append(text(rxp + 18, y + rh / 2 + 5, name, size=15,
                      color=(FIELD if top else INK), bold=True, anchor="start"))
        p.append(text(rxp + 128, y + rh / 2 + 5, body, size=13, color=INK, anchor="start"))
        if i < len(rets) - 1:
            ax = rxp + rwp / 2
            p.append(arrow(ax, y + rh + gap - 2, ax, y + rh + 2, color=FIELD, sw=1.8))
    p.append(text(rxp + rwp / 2, ry + 4 * (rh + gap) + 2, "з бази вгору — відповідь готова: 24",
                  size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "stack.svg"), W, H, *p,
           title="Лінійна рекурсія — це стос відкладених множень")


# ── fig_fibtree: дерево викликів fib(5) — повторна робота ─────────────────────
# Ідея: розгалужена рекурсія без памʼяті рахує ті самі fib(k) знову і знову.
# Однакові k підсвічені однаково; легенда лічить, скільки разів кожне зайво
# пораховано — саме цю надлишковість прибирає мемоізація.

def fig_fibtree():
    W, H = 980, 600
    p = []

    # кольори за значенням k (однакове k — однаковий колір)
    kfill = {5: "#e9eefc", 4: "#eef4ff", 3: "#eaf0fd", 2: HOT, 1: BASEHL, 0: "#eef0f2"}
    kstroke = {5: NEG, 4: NEG, 3: NEG, 2: POS, 1: FIELD, 0: MUTED}

    nodes = []   # (x, y, k, is_leaf)
    edges = []   # (x1,y1,x2,y2)
    slot = [0]
    x_left, x_gap = 70, 116
    y_top, y_gap = 76, 96

    def build(k, depth):
        y = y_top + depth * y_gap
        if k < 2:                        # база — лист
            x = x_left + slot[0] * x_gap
            slot[0] += 1
            nodes.append((x, y, k, True))
            return x, y
        xl, yl = build(k - 1, depth + 1)
        xr, yr = build(k - 2, depth + 1)
        x = (xl + xr) / 2
        nodes.append((x, y, k, False))
        edges.append((x, y, xl, yl))
        edges.append((x, y, xr, yr))
        return x, y

    build(5, 0)

    # спершу ребра (під вузлами)
    for (x1, y1, x2, y2) in edges:
        p.append(line(x1, y1 + 16, x2, y2 - 16, color="#c2c8d0", sw=1.4))

    nw, nh = 52, 34
    for (x, y, k, leaf) in nodes:
        p.append(rect(x - nw / 2, y - nh / 2, nw, nh, fill=kfill[k], stroke=kstroke[k],
                      sw=1.6, rx=8))
        p.append(text(x, y + 5, "fib %d" % k, size=12, color=INK, bold=True))

    # легенда повторів
    lx, ly = 660, 452
    p.append(rect(lx, ly, 296, 128, fill=SOFT, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(lx + 148, ly + 24, "Скільки разів пораховано те саме:", size=11.5,
                  color=INK, bold=True))
    rows = [
        ("fib 2", "3 рази", POS),
        ("fib 1", "5 разів", FIELD),
        ("fib 0", "3 рази", MUTED),
    ]
    for i, (lab, cnt, col) in enumerate(rows):
        yy = ly + 46 + i * 22
        p.append(rect(lx + 18, yy - 12, 46, 18, fill=kfill[int(lab.split()[1])],
                      stroke=col, sw=1.3, rx=4))
        p.append(text(lx + 41, yy + 2, lab, size=10, color=INK, bold=True))
        p.append(text(lx + 80, yy + 2, "— " + cnt, size=11, color=col, bold=True, anchor="start"))
    p.append(text(lx + 148, ly + 118, "Мемоізація рахує кожне fib k один раз.",
                  size=10.5, color=NEG, bold=True))

    render(os.path.join(OUT, "fibtree.svg"), W, H, *p,
           title="Дерево викликів fib(5): гілки рекурсії рахують те саме багато разів")


# ── fig_anatomy: два складники рекурсії + що коли бази нема ───────────────────
# Ідея: рекурсія тримається на базі (де зупинитись) і кроці, що меншає до неї.
# Ліворуч — виклик щокроку ближчий до бази й доходить; праворуч — крок не меншає,
# база недосяжна, стос росте без упину до переповнення.

def fig_anatomy():
    W, H = 960, 540
    p = []

    # ── верх: два стовпи ──
    p.append(text(W / 2, 62, "Будь-яка рекурсія стоїть на двох речах", size=14, color=INK, bold=True))
    bw, bh, by = 396, 92, 84
    x1 = W / 2 - bw - 24
    x2 = W / 2 + 24
    p.append(rect(x1, by, bw, bh, fill=BASEHL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x1 + 20, by + 28, "БАЗА", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(mtext(x1 + bw / 2, by + 52, ["випадок, який розвʼязуємо прямо,",
                                          "без звертання до себе:  fact(1) = 1"],
                   size=11.5, color=INK, lh=1.35))
    p.append(rect(x2, by, bw, bh, fill=CALL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(x2 + 20, by + 28, "КРОК", size=13, color=NEG, bold=True, anchor="start"))
    p.append(mtext(x2 + bw / 2, by + 52, ["зводимо задачу до меншого себе,",
                                          "ближче до бази:  fact(n) = n · fact(n−1)"],
                   size=11.5, color=INK, lh=1.35))

    # ── низ: доходить / не доходить ──
    def stairs(px, pw, title, tcol, seq, ok):
        p.append(text(px + pw / 2, 236, title, size=12.5, color=tcol, bold=True))
        n = len(seq)
        sw_, sh_ = 96, 34
        step_dx = (pw - sw_ - 40) / (n - 1)
        step_dy = 40
        y0 = 268
        for i, val in enumerate(seq):
            x = px + 20 + i * step_dx
            y = y0 + i * step_dy
            last = (i == n - 1)
            if ok and last:
                fill, stroke, tc = BASEHL, FIELD, FIELD
            elif (not ok) and last:
                fill, stroke, tc = HOT, POS, POS
            else:
                fill, stroke, tc = CALL, NEG, INK
            p.append(rect(x, y, sw_, sh_, fill=fill, stroke=stroke, sw=1.6, rx=6))
            p.append(text(x + sw_ / 2, y + sh_ / 2 + 5, val, size=12, color=tc, bold=True))
            if i < n - 1:
                p.append(arrow(x + sw_ / 2, y + sh_ + 1, px + 20 + (i + 1) * step_dx + sw_ / 2,
                               y0 + (i + 1) * step_dy - 2, color=(NEG if ok else POS), sw=1.6))

    stairs(50, 410, "Добре: щокроку ближче до бази — доходить", FIELD,
           ["fact(4)", "fact(3)", "fact(2)", "fact(1) = 1"], True)
    p.append(text(255, 470, "стос порожніє, відповідь готова", size=10.5, color=FIELD, bold=True))

    stairs(510, 410, "Погано: крок не меншає — база недосяжна", POS,
           ["f(4)", "f(4)", "f(4)", "f(4) …"], False)
    p.append(text(715, 470, "стос росте без упину → переповнення стека",
                  size=10.5, color=POS, bold=True))

    p.append(line(W / 2, 224, W / 2, H - 28, color="#d8dde3", sw=1.2, dash="5 5"))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p,
           title="База зупиняє, крок меншає — без обох рекурсія не завершиться")


# ── fig_history: дві лінії історії рекурсії сходяться на стеку ────────────────
# Ідея: самопосилання йшло до програмування двома нитками. Математична (згори)
# зʼясовувала, ЩО таке рекурсія — від означення в логіці до загальних рекурсивних
# функцій. Програмна (знизу) — ЯК її виконати: від заборони у FORTRAN через
# Keller-стек до одного речення Наура. Обидві сходяться там, де стек із рантайм-
# трюку стає механізмом, що тримає виклики, — компілятор Дейкстри 1960 року.

def fig_history():
    MATH_F, MATH_S = "#eef4ff", NEG
    PROG_F, PROG_S = "#f4f6f8", MUTED
    STOP_F, STOP_S = "#fdecea", POS      # заборона / глухий кут
    GO_F,   GO_S   = "#eafaf0", FIELD    # дозвіл / розвʼязка

    MX, box_w, gap = 40, 196, 30
    xs = [MX + i * (box_w + gap) for i in range(4)]      # 4 стовпці-віхи
    x_last_right = xs[3] + box_w
    ox = x_last_right + 40
    ow = 240
    W, H = ox + ow + 40, 384

    math_y, prog_y, bh = 86, 252, 80

    p = []

    # осьові підписи ліній
    lane_cx = (xs[0] + x_last_right) / 2
    p.append(text(lane_cx, 66, "Математична лінія — ЩО таке рекурсія (самопосилання в логіці)",
                  size=13, color=NEG, bold=True))
    p.append(text(lane_cx, 234, "Програмна лінія — ЯК її виконати (самовиклик у машині)",
                  size=13, color=INK, bold=True))

    def milestone(x, y, l1, l2, fill, stroke, tcol):
        cx = x + box_w / 2
        p.append(rect(x, y, box_w, bh, fill=fill, stroke=stroke, sw=1.6, rx=8))
        p.append(text(cx, y + 30, l1, size=12, color=tcol, bold=True))
        p.append(text(cx, y + 54, l2, size=11, color=INK))

    # верхня нитка — математика
    math = [
        ("1888 · Дедекінд", "означення рекурсією"),
        ("1923 · Сколем", "примітивна рекурсія"),
        ("1928 · Аккерман", "функція поза нею"),
        ("1934 · Петер · Гьодель", "загальна рекурсія"),
    ]
    for i, (a, b) in enumerate(math):
        milestone(xs[i], math_y, a, b, MATH_F, MATH_S, NEG)
        if i < 3:
            p.append(arrow(xs[i] + box_w + 2, math_y + bh / 2,
                           xs[i + 1] - 2, math_y + bh / 2, color=MATH_S, sw=1.6))

    # нижня нитка — програмування (FORTRAN — глухий кут, Наур — дозвіл)
    prog = [
        ("1957 · FORTRAN", "рекурсію заборонено", STOP_F, STOP_S, POS),
        ("1957 · Бауер–Замельсон", "Keller-принцип: стек", PROG_F, PROG_S, INK),
        ("1959 · Маккарті (LISP)", "пропонує рекурсію", PROG_F, PROG_S, INK),
        ("1960 · Наур", "одне речення — дозвіл", GO_F, GO_S, FIELD),
    ]
    for i, (a, b, f, s, tc) in enumerate(prog):
        milestone(xs[i], prog_y, a, b, f, s, tc)
        if i < 3:
            p.append(arrow(xs[i] + box_w + 2, prog_y + bh / 2,
                           xs[i + 1] - 2, prog_y + bh / 2, color=PROG_S, sw=1.6))

    # спільна розвʼязка — стек виконує рекурсію
    oy, oh = math_y, prog_y + bh - math_y
    p.append(rect(ox, oy, ow, oh, fill=GO_F, stroke=GO_S, sw=2.4, rx=10))
    ocx = ox + ow / 2
    p.append(text(ocx, oy + 40, "1960 · Дейкстра", size=13, color=FIELD, bold=True))
    p.append(mtext(ocx, oy + 74, ["стек стає рантайм-", "механізмом, що",
                                   "тримає виклики"], size=11.5, color=INK, lh=1.4))
    p.append(mtext(ocx, oy + 150, ["компілятор для", "Electrologica X1", "(серпень 1960)"],
                   size=11, color=MUTED, lh=1.4))

    # обидві нитки сходяться у розвʼязку
    p.append(arrow(x_last_right + 2, math_y + bh / 2, ox - 3, oy + oh * 0.36,
                   color=GO_S, sw=2.0))
    p.append(arrow(x_last_right + 2, prog_y + bh / 2, ox - 3, oy + oh * 0.64,
                   color=GO_S, sw=2.0))

    render(os.path.join(OUT, "history.svg"), W, H, *p,
           title="Дві лінії — логіки й машини — сходяться на стеку викликів")


# ── fig_shapes: три форми рекурсії → три вартості ────────────────────────────
# Ідея: вартість рекурсії читається з ФОРМИ дерева викликів. Один менший виклик —
# прямий ланцюг завглибшки n → лінійно. Два менші, що не діляться роботою, —
# дерево розгалужується ≈ φ разів на рівень → експонента. Поділ навпіл —
# збалансоване дерево на log n рівнів, кожен коштує стільки ж → n·log n.

def fig_shapes():
    W, H = 1020, 600
    p = []
    cxA, cxB, cxC = 180, 510, 840

    heads = [
        (cxA, "Один менший виклик", "T(n) = T(n−1) + O(1)", NEG),
        (cxB, "Два менші, що не діляться", "T(n) = T(n−1) + T(n−2) + O(1)", POS),
        (cxC, "Поділ навпіл", "T(n) = 2·T(n/2) + O(n)", FIELD),
    ]
    for cx, h1, h2, col in heads:
        p.append(text(cx, 58, h1, size=12.5, color=col, bold=True))
        p.append(text(cx, 80, h2, size=12, color=INK))

    # тонкі роздільники між стовпцями
    for xd in (345, 675):
        p.append(line(xd, 96, xd, 404, color="#e3e7ec", sw=1.0, dash="4 5"))

    R = 7
    def dot(x, y, base=False):
        return circle(x, y, R, fill=(BASEHL if base else CALL),
                      stroke=(FIELD if base else NEG), sw=1.6)

    # ── A: ланцюг (лінійна рекурсія) ──
    chain_y = [116, 160, 204, 248]
    for i in range(len(chain_y) - 1):
        p.append(line(cxA, chain_y[i] + R, cxA, chain_y[i + 1] - R, color="#c2c8d0", sw=1.4))
    for y in chain_y:
        p.append(dot(cxA, y))
    p.append(text(cxA, 290, "⋮", size=18, color=MUTED, bold=True))
    p.append(line(cxA, 300, cxA, 328 - R, color="#c2c8d0", sw=1.4))
    p.append(dot(cxA, 328, base=True))
    p.append(text(cxA, 360, "n рівнів, по O(1)", size=11, color=MUTED))

    # ── B: розгалуження (справжня лопатна форма дерева fib) ──
    nodesB, edgesB, slotB = [], [], [0]
    xgapB, xleftB, ytopB, ygapB = 60, cxB - 120, 116, 46
    def buildB(k, depth):
        y = ytopB + depth * ygapB
        if k < 2:
            x = xleftB + slotB[0] * xgapB; slotB[0] += 1
            nodesB.append((x, y, True)); return x, y
        xl, yl = buildB(k - 1, depth + 1)
        xr, yr = buildB(k - 2, depth + 1)
        x = (xl + xr) / 2
        nodesB.append((x, y, False))
        edgesB.append((x, y, xl, yl)); edgesB.append((x, y, xr, yr))
        return x, y
    buildB(4, 0)
    for (x1, y1, x2, y2) in edgesB:
        p.append(line(x1, y1 + R, x2, y2 - R, color="#c2c8d0", sw=1.3))
    for (x, y, leaf) in nodesB:
        p.append(dot(x, y, base=leaf))
    p.append(text(cxB, 360, "≈ φ гілок на рівень", size=11, color=MUTED))

    # ── C: збалансований поділ навпіл ──
    nodesC, edgesC, leafC = [], [], [0]
    xgapC, xleftC, ytopC, ygapC = 40, cxC - 140, 116, 46
    def buildC(depth, maxd):
        y = ytopC + depth * ygapC
        if depth == maxd:
            x = xleftC + leafC[0] * xgapC; leafC[0] += 1
            nodesC.append((x, y, True)); return x, y
        xl, yl = buildC(depth + 1, maxd)
        xr, yr = buildC(depth + 1, maxd)
        x = (xl + xr) / 2
        nodesC.append((x, y, False))
        edgesC.append((x, y, xl, yl)); edgesC.append((x, y, xr, yr))
        return x, y
    buildC(0, 3)
    for (x1, y1, x2, y2) in edgesC:
        p.append(line(x1, y1 + R, x2, y2 - R, color="#c2c8d0", sw=1.3))
    for (x, y, leaf) in nodesC:
        p.append(dot(x, y, base=leaf))
    p.append(text(cxC, 360, "log n рівнів, по O(n)", size=11, color=MUTED))

    # ── присуд знизу: три вартості ──
    def verdict(cx, big, sub, col, fill):
        p.append(rect(cx - 122, 430, 244, 96, fill=fill, stroke=col, sw=2.0, rx=10))
        p.append(text(cx, 472, big, size=23, color=col, bold=True))
        p.append(text(cx, 502, sub, size=11.5, color=INK))
    verdict(cxA, "O(n)", "лінійно", NEG, "#eef4ff")
    verdict(cxB, "O(φⁿ)", "експонента — вибух", POS, HOT)
    verdict(cxC, "O(n · log n)", "майже лінійно", FIELD, BASEHL)

    render(os.path.join(OUT, "recurrence-shapes.svg"), W, H, *p,
           title="Форма дерева викликів вирішує вартість")


# ── fig_halving: облік роботи в дереві поділу навпіл ─────────────────────────
# Ідея: у T(n)=2·T(n/2)+O(n) кожен рівень коштує РІВНО n — удвічі більше шматків,
# але кожен удвічі менший, тож 2·(n/2)=n. Рівнів, поки n меншає до 1, — log₂n.
# Тому разом n·log₂n. Це «збалансований» випадок основної теореми.

def fig_halving():
    W, H = 980, 560
    p = []
    cx = 380

    def wbox(x, y, label, w=78, h=32, fill=CALL, stroke=NEG):
        p.append(rect(x - w / 2, y - h / 2, w, h, fill=fill, stroke=stroke, sw=1.5, rx=6))
        p.append(text(x, y + 5, label, size=13, color=INK, bold=True))

    # рівні дерева
    L0 = [(cx, 100, "n")]
    L1 = [(cx - 130, 182, "n/2"), (cx + 130, 182, "n/2")]
    L2 = [(cx - 210, 264, "n/4"), (cx - 70, 264, "n/4"),
          (cx + 70, 264, "n/4"), (cx + 210, 264, "n/4")]

    # ребра
    for (px, py, _) in L0:
        for (kx, ky, _) in L1:
            p.append(line(px, py + 16, kx, ky - 16, color="#c2c8d0", sw=1.4))
    p.append(line(L1[0][0], L1[0][1] + 16, L2[0][0], L2[0][1] - 16, color="#c2c8d0", sw=1.4))
    p.append(line(L1[0][0], L1[0][1] + 16, L2[1][0], L2[1][1] - 16, color="#c2c8d0", sw=1.4))
    p.append(line(L1[1][0], L1[1][1] + 16, L2[2][0], L2[2][1] - 16, color="#c2c8d0", sw=1.4))
    p.append(line(L1[1][0], L1[1][1] + 16, L2[3][0], L2[3][1] - 16, color="#c2c8d0", sw=1.4))

    for (x, y, s) in L0 + L1 + L2:
        wbox(x, y, s)

    # ⋮ і листковий рівень
    p.append(text(cx, 314, "⋮", size=20, color=MUTED, bold=True))
    leaf_y = 366
    for i in range(9):
        lx = cx - 224 + i * 56
        p.append(circle(lx, leaf_y, 6, fill=BASEHL, stroke=FIELD, sw=1.5))
    p.append(text(cx, 396, "n листків, по O(1)", size=11.5, color=MUTED))

    # права колонка — робота на кожному рівні
    sx = 812
    p.append(text(sx, 66, "робота на рівні", size=12, color=INK, bold=True))
    sums = [(100, "1 · n = n"), (182, "2 · (n/2) = n"), (264, "4 · (n/4) = n"),
            (314, "⋮"), (366, "n · O(1) = n")]
    for (y, s) in sums:
        if s != "⋮":
            p.append(line(648, y, sx - 78, y, color="#e3e7ec", sw=1.0, dash="4 5"))
        p.append(text(sx, y + 4, s, size=12.5, color=(MUTED if s == "⋮" else INK),
                      bold=(s != "⋮")))

    # присуд знизу
    p.append(text(cx, 428, "удвічі більше шматків × удвічі менший кожен  =  та сама сума n",
                  size=11.5, color=MUTED))
    bx, bw = 150, 680
    p.append(rect(bx, 452, bw, 78, fill=BASEHL, stroke=FIELD, sw=2.2, rx=10))
    p.append(text(bx + bw / 2, 482, "Кожен рівень коштує рівно n, а рівнів — log₂n",
                  size=13, color=INK))
    p.append(text(bx + bw / 2, 510, "разом:   n · log₂n   =   O(n · log n)",
                  size=15, color=FIELD, bold=True))

    render(os.path.join(OUT, "halving-tree.svg"), W, H, *p,
           title="Поділ навпіл: кожен рівень коштує n, рівнів — log₂n")


# ── fig_tailtoloop: три правила — хвостова рекурсія → цикл ─────────────────────
# Ідея: хвостовий виклик перекладається на цикл дослівно, за трьома правилами.
# Ліворуч — рекурсія (parametр, база, хвостовий виклик), праворуч — та сама
# роль у циклі (змінна стану, умова виходу, переприсвоєння + новий виток).
# Пронумеровані кружечки й стрілки показують, яка частина в яку переходить.

def fig_tailtoloop():
    W, H = 1000, 520
    p = []

    lx, lw = 60, 380
    rxp, rwp = 560, 380
    cx_mid = (lx + lw + rxp) / 2

    p.append(text(lx + lw / 2, 44, "Рекурсія (хвостовий виклик)", size=13.5, color=NEG, bold=True))
    p.append(text(rxp + rwp / 2, 44, "Цикл", size=13.5, color=FIELD, bold=True))

    bh, gap, y0 = 108, 34, 78
    rules = [
        ("1", "Параметри → змінні циклу", NEG,
         ["def list_sum(node, acc=0):", "параметр acc = стан обчислення"],
         ["def list_sum(node):", "acc = 0      ← та сама роль"]),
        ("2", "База → умова виходу", FIELD,
         ["if node is None:", "return acc            (база)"],
         ["while node is not None:", "...          return acc"]),
        ("3", "Хвостовий виклик → переприсвоєння", POS,
         ["return list_sum(", "  node.next, acc + node.value)"],
         ["acc = acc + node.value", "node = node.next   (новий виток)"]),
    ]

    for i, (num, label, col, lft, rgt) in enumerate(rules):
        y = y0 + i * (bh + gap)
        p.append(text(W / 2, y - 14, label, size=12, color=col, bold=True))

        p.append(fitbox(lx, y, lw, bh, lft, size=13.5, pad=14,
                         fill=CALL, stroke=NEG, sw=1.6, color=INK, bold=False, rx=8))
        p.append(fitbox(rxp, y, rwp, bh, rgt, size=13.5, pad=14,
                         fill=BASEHL, stroke=FIELD, sw=1.6, color=INK, bold=False, rx=8))

        cy = y + bh / 2
        p.append(arrow(lx + lw + 2, cy, cx_mid - 17, cy, color=col, sw=1.8))
        p.append(arrow(cx_mid + 17, cy, rxp - 2, cy, color=col, sw=1.8))
        p.append(circle(cx_mid, cy, 16, fill="#ffffff", stroke=col, sw=2.2))
        p.append(text(cx_mid, cy + 5, num, size=14, color=col, bold=True))

    foot_y = y0 + 3 * (bh + gap) - gap + 34
    p.append(text(W / 2, foot_y, "Стек не потрібен: на виринанні робити нема чого — кадр перевикористовується",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "tailtoloop.svg"), W, H, *p,
           title="Три правила: хвостова рекурсія переписується на цикл дослівно")


# ── fig_iterstack: той самий обхід — системний стек vs масив у купі ───────────
# Ідея: обидва стеки тримають однакову висоту дерева, але живуть у різних
# світах. Ліворуч — маленька фіксована ділянка потоку (1–8 МБ), важкі кадри
# (~100 байт) швидко впираються у стелю — переповнення. Праворуч — масив у
# купі (гігабайти), легкі вказівники (8 байт) на тій самій глибині займають
# крихту місця, і лишається простір рости ще на порядки.

def fig_iterstack():
    W, H = 980, 600
    p = []

    p.append(text(W / 2, 42, "Та сама глибина обходу — два різні стеки",
                  size=14, color=INK, bold=True))

    top, bot, boxh = 96, 500, 404

    # ── лівий бокс: системний стек ──
    lx, lw = 70, 380
    p.append(text(lx + lw / 2, 78, "Системний стек — 1–8 МБ, задано назавжди",
                  size=12.5, color=POS, bold=True))
    p.append(rect(lx, top, lw, boxh, fill=SOFT, stroke=MUTED, sw=1.6, rx=8))

    n_frames = 9
    fh, fgap = 34, 4
    fw = lw - 40
    fx = lx + 20
    for i in range(n_frames):
        fy = bot - (i + 1) * (fh + fgap) + fgap
        danger = i >= n_frames - 3
        fill = HOT if danger else CALL
        stroke = POS if danger else NEG
        p.append(rect(fx, fy, fw, fh, fill=fill, stroke=stroke, sw=1.5, rx=5))
        if i == 0:
            p.append(text(fx + fw / 2, fy + fh / 2 + 5, "кадр ≈ 50–150 байт",
                          size=11, color=INK, anchor="middle"))
    # стеля й переповнення над боксом
    ceil_y = bot - n_frames * (fh + fgap) + fgap - 6
    p.append(line(lx - 6, ceil_y, lx + lw + 6, ceil_y, color=POS, sw=2.0, dash="4 4"))
    p.append(text(lx + lw / 2, ceil_y - 14, "стеля ≈ 10–15 тис. кадрів → переповнення",
                  size=11.5, color=POS, bold=True))

    p.append(text(lx + lw / 2, top + boxh + 26,
                  "мегабайт ÷ сотня байтів = десятки тисяч рівнів, і край",
                  size=11, color=MUTED))

    # ── правий бокс: масив у купі ──
    rxp, rwp = 530, 380
    p.append(text(rxp + rwp / 2, 78, "Наш масив у купі — місткість гігабайти",
                  size=12.5, color=FIELD, bold=True))
    p.append(rect(rxp, top, rwp, boxh, fill=SOFT, stroke=MUTED, sw=1.6, rx=8))

    n_ticks = 22
    th, tgap = 13, 2
    tw = rwp - 40
    tx = rxp + 20
    filled_ticks = 9   # та сама глибина, що й ліворуч
    for i in range(n_ticks):
        ty = bot - (i + 1) * (th + tgap) + tgap
        filled = i < filled_ticks
        fill = BASEHL if filled else "#f4f6f8"
        stroke = FIELD if filled else "#d8dde3"
        p.append(rect(tx, ty, tw, th, fill=fill, stroke=stroke, sw=1.2, rx=3))
    same_depth_y = bot - filled_ticks * (th + tgap) + tgap - 6
    p.append(line(rxp - 6, same_depth_y, rxp + rwp + 6, same_depth_y,
                  color=FIELD, sw=1.8, dash="4 4"))
    p.append(text(rxp + rwp / 2, same_depth_y - 12, "та сама глибина — займає крихту місця",
                  size=11, color=FIELD, bold=True))
    p.append(text(rxp + rwp / 2, top + 40, "⋮  ще сотні мільйонів вміститься",
                  size=11.5, color=MUTED))

    p.append(text(rxp + rwp / 2, top + boxh + 26,
                  "елемент — 8-байтовий вказівник, масив росте подвоєнням",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "iterstack.svg"), W, H, *p,
           title="Один і той самий обхід: фіксований стек проти масиву в купі")


if __name__ == "__main__":
    fig_stack()
    fig_fibtree()
    fig_anatomy()
    fig_history()
    fig_shapes()
    fig_halving()
    fig_tailtoloop()
    fig_iterstack()
    print("figs: готово")
