# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── split: рекурсивний поділ згори вниз на дві ~рівні за вагою групи ───────────
# Ідея: відсортований ряд A15 B7 C6 D6 E5 ріжемо так, щоб сума ліворуч ≈ сумі
# праворуч; ліва половина дістає 0, права 1; далі кожну половину ріжемо так само.
# Три яруси показують, як накопичуються біти коду.

def _chip(cx, cy, lab, w, hot, p, small=False):
    s = "%s\n%d" % (lab, w)
    size = 11 if small else 12
    fill = "#f3c6bf" if hot else "#eaf2fb"
    stroke = POS if hot else INK
    box, bw, bh = textbox(cx, cy, s, size=size, bold=True, fill=fill, stroke=stroke,
                          sw=1.6, color=INK, min_w=42)
    p.append(box)
    return bw


def fig_split():
    W, H = 700, 430
    p = []

    # ярус 0: усі п'ять символів у ряд
    syms = [("A", 15), ("B", 7), ("C", 6), ("D", 6), ("E", 5)]
    y0 = 70
    xs = [120, 230, 340, 450, 560]
    for (lab, w), x in zip(syms, xs):
        _chip(x, y0, lab, w, False, p)
    p.append(text(60, y0 + 5, "сума 39", size=11, color=MUTED, anchor="start"))

    # перший розріз: AB(22) | CDE(17)  — між B і C
    cut1 = (xs[1] + xs[2]) / 2
    p.append(line(cut1, y0 - 26, cut1, y0 + 60, color=POS, sw=2.4, dash="5,4"))
    p.append(text(cut1, y0 + 76, "розріз 1: 22 | 17", size=11, color=POS, bold=True))
    p.append(text(xs[0] + 30, y0 - 30, "ліво → 0", size=10, color=NEG, bold=True))
    p.append(text(xs[3] + 30, y0 - 30, "право → 1", size=10, color=POS, bold=True))

    # ярус 1: дві групи, кожну ріжемо далі
    y1 = 200
    # ліва AB → A(15)|B(7)
    _chip(xs[0], y1, "A", 15, True, p)
    _chip(xs[1], y1, "B", 7, True, p)
    cutL = (xs[0] + xs[1]) / 2
    p.append(line(cutL, y1 - 24, cutL, y1 + 24, color=NEG, sw=2.0, dash="4,4"))
    p.append(text(cutL, y1 + 44, "15 | 7", size=10, color=NEG))
    # права CDE → C(6)|DE(12)
    _chip(xs[2], y1, "C", 6, True, p)
    _chip(xs[3], y1, "D", 6, True, p)
    _chip(xs[4], y1, "E", 5, True, p)
    cutR = (xs[2] + xs[3]) / 2
    p.append(line(cutR, y1 - 24, cutR, y1 + 24, color=NEG, sw=2.0, dash="4,4"))
    p.append(text(cutR + 6, y1 + 44, "6 | 12", size=10, color=NEG, anchor="start"))
    # стрілки з ярусу 0 у ярус 1
    p.append(arrow(cut1 - 60, y0 + 90, xs[0] + 40, y1 - 30, color=MUTED, sw=1.4))
    p.append(arrow(cut1 + 60, y0 + 90, xs[3], y1 - 30, color=MUTED, sw=1.4))

    # ярус 2: останній розріз DE → D|E
    y2 = 330
    _chip(xs[3], y2, "D", 6, True, p)
    _chip(xs[4], y2, "E", 5, True, p)
    cutDE = (xs[3] + xs[4]) / 2
    p.append(line(cutDE, y2 - 24, cutDE, y2 + 24, color=NEG, sw=1.8, dash="4,4"))
    p.append(text(cutDE, y2 + 42, "6 | 5", size=10, color=NEG))
    p.append(arrow(xs[4] - 10, y1 + 40, xs[4] - 5, y2 - 30, color=MUTED, sw=1.4))

    # підсумкові коди збоку
    rows = ["A = 00", "B = 01", "C = 10", "D = 110", "E = 111"]
    bx = 40
    p.append(text(bx, 300, "коди:", size=12, color=INK, bold=True, anchor="start"))
    for i, r in enumerate(rows):
        p.append(text(bx, 322 + i * 20, r, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "split.svg"), W, H, *p,
           title="Поділ згори вниз: ріжемо на дві ~рівні за вагою групи")


# ── tree: те саме рішення у вигляді дерева з кодами на листках ─────────────────
# Ідея: кожен розріз = розвилка (0 ліворуч, 1 праворуч); символ — листок,
# код — шлях від кореня. Видно, що частий A сидить на глибині 2, а не 1.

def _edge(x1, y1, x2, y2, bit, p):
    p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.5))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    col = NEG if bit == "0" else POS
    p.append(text(mx + (-10 if bit == "0" else 10), my - 2, bit, size=13, color=col, bold=True))


def fig_tree():
    W, H = 680, 380
    p = []
    r = 18

    root = (330, 60)
    nAB = (190, 150)            # внутрішній: ліва група AB (0)
    nCDE = (470, 150)           # внутрішній: права група CDE (1)
    nA = (120, 250)            # лист A (00)
    nB = (260, 250)            # лист B (01)
    nC = (390, 250)            # лист C (10)
    nDE = (560, 250)           # внутрішній DE (11)
    nD = (510, 330)           # лист D (110)
    nE = (610, 330)           # лист E (111)

    def _wnode(c, p):
        p.append(circle(c[0], c[1], r, fill="#eaf2fb", stroke=INK, sw=1.8))
    def _leaf(c, lab, p):
        p.append(circle(c[0], c[1], r, fill="#f3c6bf", stroke=POS, sw=1.8))
        p.append(text(c[0], c[1] + 5, lab, size=13, color=INK, bold=True))

    _edge(root[0], root[1] + r, nAB[0], nAB[1] - r, "0", p)
    _edge(root[0], root[1] + r, nCDE[0], nCDE[1] - r, "1", p)
    _edge(nAB[0], nAB[1] + r, nA[0], nA[1] - r, "0", p)
    _edge(nAB[0], nAB[1] + r, nB[0], nB[1] - r, "1", p)
    _edge(nCDE[0], nCDE[1] + r, nC[0], nC[1] - r, "0", p)
    _edge(nCDE[0], nCDE[1] + r, nDE[0], nDE[1] - r, "1", p)
    _edge(nDE[0], nDE[1] + r, nD[0], nD[1] - r, "0", p)
    _edge(nDE[0], nDE[1] + r, nE[0], nE[1] - r, "1", p)

    _wnode(root, p)
    _wnode(nAB, p)
    _wnode(nCDE, p)
    _wnode(nDE, p)
    _leaf(nA, "A", p)
    _leaf(nB, "B", p)
    _leaf(nC, "C", p)
    _leaf(nD, "D", p)
    _leaf(nE, "E", p)

    # підписи-коди біля листків
    p.append(text(nA[0], nA[1] + 36, "00", size=12, color=INK))
    p.append(text(nB[0], nB[1] + 36, "01", size=12, color=INK))
    p.append(text(nC[0], nC[1] + 36, "10", size=12, color=INK))
    p.append(text(nD[0], nD[1] + 36, "110", size=12, color=INK))
    p.append(text(nE[0], nE[1] + 36, "111", size=12, color=INK))

    # винесена ремарка про A (у вільному лівому нижньому куті)
    p.append(text(40, 340, "A: p=0.385, та однаково 2 біти", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "tree.svg"), W, H, *p,
           title="Дерево Шеннона–Фано: код — шлях від кореня")


# ── vs-huffman: дві таблиці кодів поряд + середні довжини проти дна H ──────────
# Ідея: на тому самому джерелі Фано дає A 2 біти, Гаффман — 1; через це
# середня довжина Фано 2.28 вища за Гаффманову 2.23, а дно H=2.19.

def fig_vs_huffman():
    W, H = 700, 380
    p = []

    # дві таблиці кодів
    fano = [("A", "00"), ("B", "01"), ("C", "10"), ("D", "110"), ("E", "111")]
    huff = [("A", "0"), ("B", "100"), ("C", "101"), ("D", "110"), ("E", "111")]

    def table(x0, title, rows, hotsym, p):
        p.append(text(x0 + 60, 64, title, size=13, color=INK, bold=True))
        for i, (sym, code) in enumerate(rows):
            ry = 92 + i * 30
            hot = sym == hotsym
            p.append(text(x0, ry, sym, size=13, color=POS if hot else INK, bold=True, anchor="start"))
            p.append(text(x0 + 28, ry, "=", size=12, color=MUTED, anchor="start"))
            p.append(text(x0 + 46, ry, code, size=13,
                          color=POS if hot else INK, bold=hot, anchor="start"))

    table(70, "Шеннон–Фано", fano, "A", p)
    table(230, "Гаффман", huff, "A", p)

    # стрілка-акцент на рядок A
    p.append(text(70, 250, "A частий (0.385), але Фано дав 2 біти,", size=10, color=POS, anchor="start"))
    p.append(text(70, 266, "а Гаффман — лише 1. Звідси програш.", size=10, color=POS, anchor="start"))

    # стовпчики середніх довжин праворуч
    ox, oy = 430, 300
    aw, ah = 230, 210
    p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5))
    p.append(text(ox - 12, oy - ah - 2, "біт/симв.", size=10, color=INK, bold=True, anchor="end"))

    scale = ah / 3.0
    bars = [("Фано\n2.28", 2.28, "#f3c6bf", POS),
            ("Гаффман\n2.23", 2.23, "#cfe0f5", NEG),
            ("H\n2.19", 2.186, "#d7f0de", FIELD)]
    slot = aw / (len(bars) + 0.4)
    bw = slot * 0.46
    # обрізаємо вісь знизу до 1.8, щоб різниця була видна
    base = 1.8
    scale = ah / (3.0 - base)
    for i, (lab, val, fill, stroke) in enumerate(bars):
        bx = ox + 28 + i * slot
        bh = (val - base) * scale
        p.append(rect(bx, oy - bh, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=3))
        p.append(text(bx + bw / 2, oy - bh - 7, "%.2f" % val, size=10, color=stroke, bold=True))
        p.append(mtext(bx + bw / 2, oy + 15, lab, size=9, color=INK))
    # лінія дна H
    yH = oy - (2.186 - base) * scale
    p.append(line(ox, yH, ox + aw, yH, color=FIELD, sw=1.2, dash="5,4"))
    p.append(text(ox + aw, yH - 5, "дно H", size=9, color=FIELD, anchor="end"))
    p.append(text(ox + aw / 2, oy + 44, "(вісь від 1.8)", size=9, color=MUTED))

    render(os.path.join(OUT, "vs-huffman.svg"), W, H, *p,
           title="Те саме джерело: Фано не дотягує до Гаффмана")


# ── greedy-fail: чому жадібний поділ за вагою груп не оптимальний ──────────────
# Ідея: розріз вирівнює СУМИ двох груп, та оптимальність вимагає глибин,
# обернених до −log p кожного символу. Балансування груп цього не гарантує:
# найчастіший може потрапити у «важку» половину й дістати на біт довший код.

def fig_greedy_fail():
    W, H = 680, 330
    p = []

    # ліворуч: що робить Фано — рівняє суми
    bx = 60
    p.append(text(bx + 130, 62, "Фано рівняє СУМИ груп", size=12, color=INK, bold=True))
    b1, b1w, _ = textbox(bx + 70, 110, "A+B\n22", size=12, bold=True,
                         fill="#eaf2fb", stroke=NEG, sw=1.8, color=INK, min_w=80)
    p.append(b1)
    b2, _, _ = textbox(bx + 200, 110, "C+D+E\n17", size=12, bold=True,
                       fill="#eaf2fb", stroke=POS, sw=1.8, color=INK, min_w=80)
    p.append(b2)
    p.append(text(bx + 135, 150, "≈ рівні", size=11, color=MUTED))
    p.append(text(bx + 30, 200, "A потрапив у пару з B →", size=10, color=POS, anchor="start"))
    p.append(text(bx + 30, 216, "дістав 2 біти, хоч p(A)=0.385", size=10, color=POS, anchor="start"))
    p.append(text(bx + 30, 232, "просить ~1.4 біта", size=10, color=POS, anchor="start"))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 260, color="#dde3ea", sw=1.2))

    # праворуч: чого вимагає оптимальність — глибина ~ −log p
    rx = 380
    p.append(text(rx + 130, 62, "оптимум хоче глибину ~ −log₂p", size=12, color=INK, bold=True))
    rows = [("A", "0.385", "1.4", "1"),
            ("B", "0.179", "2.5", "3"),
            ("E", "0.128", "3.0", "3")]
    p.append(text(rx, 98, "симв", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 70, 98, "p", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 140, 98, "−log₂p", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 220, 98, "Гаффман", size=10, color=MUTED, anchor="start"))
    for i, (s, pr, sp, hl) in enumerate(rows):
        ry = 124 + i * 30
        p.append(text(rx, ry, s, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(rx + 70, ry, pr, size=11, color=INK, anchor="start"))
        p.append(text(rx + 140, ry, sp, size=11, color=NEG, anchor="start"))
        p.append(text(rx + 230, ry, hl, size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx, 230, "A заслуговує 1 біт — Гаффман дає,", size=10, color=FIELD, anchor="start"))
    p.append(text(rx, 246, "Фано ні: баланс сум це не бачить", size=10, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "рівні суми груп ≠ правильні глибини: ось чому жадібний поділ субоптимальний",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "greedy-fail.svg"), W, H, *p,
           title="Чому поділ за вагою груп не дає оптимуму")


if __name__ == "__main__":
    fig_split()
    fig_tree()
    fig_vs_huffman()
    fig_greedy_fail()
    print("OK: figures written to", OUT)
