# -*- coding: utf-8 -*-
# Фігури для вставки math-sop-minimization.md (тема «Від PAL до FPGA»).
# Окремий генератор, щоб не чіпати figs.py / figs_d.py власника.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE  = NEG
GREEN = FIELD
RED   = POS
AMBER = "#b8860b"
GREY  = "#8a8a8a"


def cell(x, y, w, h, s, fill=BG, stroke="#c9ced6", sw=1.2, color=INK, size=13, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0)
    out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


# ── 1. truth-to-dnf: таблиця істинності → досконала ДНФ (мінтерми) ─────────────
def fig_truth_to_dnf():
    W, H = 720, 420
    p = []
    p.append(text(W / 2, 26, "Таблиця істинності → сума мінтермів", size=16, bold=True))
    # Таблиця зліва: a b c | F, функція «більшість»
    x0, y0 = 40, 60
    cw, ch = 44, 30
    hdr = ["a", "b", "c", "F"]
    for i, hh in enumerate(hdr):
        col = BLUE if i < 3 else GREEN
        p.append(cell(x0 + i * cw, y0, cw, ch, hh, fill="#f4f6f8", color=col, bold=True))
    rows = [
        (0, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 1, 1, 1),
        (1, 0, 0, 0), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 1),
    ]
    minterms = {
        (0, 1, 1): "ā·b·c",
        (1, 0, 1): "a·b̄·c",
        (1, 1, 0): "a·b·c̄",
        (1, 1, 1): "a·b·c",
    }
    for r, (a, b, c, f) in enumerate(rows):
        y = y0 + (r + 1) * ch
        one = (f == 1)
        rowfill = "#eef7ee" if one else BG
        for i, v in enumerate((a, b, c)):
            p.append(cell(x0 + i * cw, y, cw, ch, str(v), fill=rowfill))
        p.append(cell(x0 + 3 * cw, y, cw, ch, str(f), fill=rowfill,
                      color=GREEN if one else MUTED, bold=one))
        if one:
            # стрілка до мінтерма
            ax = x0 + 4 * cw + 6
            p.append(text(ax, y + ch / 2 + 4, "→", size=14, color=GREEN, anchor="start", bold=True))
            p.append(text(ax + 24, y + ch / 2 + 4, minterms[(a, b, c)], size=13,
                          color=INK, anchor="start", bold=True))
    # Пояснення читання рядка
    p.append(text(x0, y0 + 9 * ch + 26, "у рядку 1 → пряма змінна,   0 → інверсія;   беремо лише рядки з F = 1",
                  size=11, color=MUTED, anchor="start", italic=True))
    # Підсумкова формула праворуч знизу
    p.append(line(x0, y0 + 9 * ch + 40, W - 40, y0 + 9 * ch + 40, color="#e4e4e4", sw=1.2))
    p.append(text(x0, y0 + 9 * ch + 66, "F = ā·b·c + a·b̄·c + a·b·c̄ + a·b·c",
                  size=14, color=INK, anchor="start", bold=True))
    render(os.path.join(OUT, "truth-to-dnf.svg"), W, H, *p)


# ── 2. kmap-majority: карта Карно функції «більшість» ─────────────────────────
def fig_kmap_majority():
    W, H = 640, 400
    p = []
    p.append(text(W / 2, 26, "Карта Карно: сусідні одиниці склеюються", size=16, bold=True))
    # 2×4 сітка: рядки a∈{0,1}, стовпці bc у коді Ґрея 00 01 11 10
    gx, gy = 150, 90
    cw, ch = 90, 90
    cols = ["00", "01", "11", "10"]   # Gray code
    rlab = ["0", "1"]
    # значення F(a,b,c) для «більшості» у порядку стовпців-Ґрея bc = 00,01,11,10
    # рядок a=0: bc=00→0, 01→0, 11→1, 10→0
    # рядок a=1: bc=00→0, 01→1, 11→1, 10→1
    grid = [
        [0, 0, 1, 0],
        [0, 1, 1, 1],
    ]
    # підписи осей
    p.append(text(gx - 16, gy - 14, "a\\bc", size=12, color=MUTED, anchor="end", bold=True))
    for j, cl in enumerate(cols):
        p.append(text(gx + j * cw + cw / 2, gy - 12, cl, size=13, color=BLUE, bold=True))
    for i, rl in enumerate(rlab):
        p.append(text(gx - 16, gy + i * ch + ch / 2 + 5, rl, size=13, color=BLUE, anchor="end", bold=True))
    for i in range(2):
        for j in range(4):
            v = grid[i][j]
            fill = "#eef7ee" if v else BG
            p.append(cell(gx + j * cw, gy + i * ch, cw, ch, str(v), fill=fill,
                          color=GREEN if v else MUTED, size=20, bold=bool(v)))
    # Три овали-групи (кожен — пара сусідніх одиниць = один добуток)
    # a·b : стовпці 11,10 у рядку a=1  (клітинки [1][2],[1][3])
    def oval(cx, cy, rx, ry, col, label, lx, ly):
        o = ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
             'stroke="%s" stroke-width="2.4"/>' % (cx, cy, rx, ry, col))
        o += text(lx, ly, label, size=13, color=col, bold=True)
        return o
    # a·b — низ, два праві стовпці (11,10) рядка a=1
    p.append(oval(gx + 3 * cw, gy + 1.5 * ch, cw + 8, ch / 2 + 12, RED, "a·b",
                  gx + 3 * cw + cw / 2 + 44, gy + 2 * ch + 22))
    # a·c — стовпці 11,01 рядка a=1 (це b·? — обережно). У Ґреї сусідні по горизонталі:
    #   пара (01,11) рядка a=1 → a·c ; пара (11,10) рядка a=1 → a·b (уже взято)
    p.append(oval(gx + 1.5 * cw, gy + 1.5 * ch, cw + 8, ch / 2 + 4, BLUE, "a·c",
                  gx + 1.0 * cw, gy + 2 * ch + 22))
    # b·c — стовпець 11 (обидва рядки a=0,1) → b·c
    p.append(oval(gx + 2.5 * cw, gy + 1.0 * ch, cw / 2 + 6, ch + 10, AMBER, "b·c",
                  gx + 2.5 * cw + 8, gy - 26))
    # Підсумок
    p.append(text(W / 2, gy + 2 * ch + 66, "три пари → F = a·b + b·c + a·c   (3 добутки замість 4)",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, gy + 2 * ch + 90,
                  "сусідні по коду Ґрея клітинки різняться одним бітом — та змінна випадає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "kmap-majority.svg"), W, H, *p)


# ── 3. qmc-flow: Квайн—Мак-Класкі — групи, склейки, таблиця покриття ───────────
def fig_qmc_flow():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 26, "Квайн—Мак-Класкі: склейки → прості імпліканти → покриття", size=15, bold=True))

    # Стовпець 1: мінтерми, згруповані за кількістю одиниць
    x1, y1 = 30, 60
    p.append(text(x1, y1, "1. групи за числом одиниць", size=11, color=MUTED, anchor="start", bold=True))
    groups = [
        ("одна 1", ["011  (3)", "101  (5)", "110  (6)"]),
        ("дві 1",  ["111  (7)"]),
    ]
    y = y1 + 16
    for gname, items in groups:
        p.append(text(x1, y + 12, gname, size=10, color=BLUE, anchor="start", bold=True))
        y += 20
        for it in items:
            p.append(cell(x1, y, 120, 24, it, fill="#f4f6f8", size=12))
            y += 26
        y += 8

    # Стовпець 2: склейки (комбінування пар, що різняться 1 бітом)
    x2 = 210
    p.append(text(x2, y1, "2. склейка пар (−1 біт)", size=11, color=MUTED, anchor="start", bold=True))
    combos = [
        ("011+111", "-11  → b·c"),
        ("101+111", "1-1  → a·c"),
        ("110+111", "11-  → a·b"),
    ]
    y = y1 + 30
    for src, res in combos:
        p.append(cell(x2, y, 90, 26, src, fill=BG, size=11))
        p.append(text(x2 + 96, y + 17, "→", size=13, color=GREEN, anchor="start", bold=True))
        p.append(cell(x2 + 118, y, 120, 26, res, fill="#eef7ee", size=12, color=INK, bold=True))
        y += 34
    p.append(text(x2, y + 10, "далі не склеюється →", size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(x2, y + 26, "це прості імпліканти", size=10, color=RED, anchor="start", bold=True))

    # Стовпець 3: таблиця покриття
    x3, y3 = 500, 56
    p.append(text(x3, y3 - 4, "3. таблиця покриття", size=11, color=MUTED, anchor="start", bold=True))
    cols = ["3", "5", "6", "7"]      # мінтерми-стовпці
    pis = [("b·c", [1, 0, 0, 1]),
           ("a·c", [0, 1, 0, 1]),
           ("a·b", [0, 0, 1, 1])]
    ox, oy = x3, y3 + 12
    lw = 60
    cwn = 40
    rh = 34
    # шапка
    p.append(cell(ox, oy, lw, rh, "PI", fill="#f4f6f8", size=12, bold=True))
    for j, c in enumerate(cols):
        p.append(cell(ox + lw + j * cwn, oy, cwn, rh, c, fill="#f4f6f8", color=GREEN, size=13, bold=True))
    # рядки
    for i, (name, cov) in enumerate(pis):
        yy = oy + (i + 1) * rh
        p.append(cell(ox, yy, lw, rh, name, fill=BG, size=12, bold=True))
        for j, v in enumerate(cov):
            mark = "✓" if v else ""
            p.append(cell(ox + lw + j * cwn, yy, cwn, rh, mark, fill="#eef7ee" if v else BG,
                          color=GREEN, size=15, bold=True))
    # висновок
    yb = oy + 4 * rh + 26
    p.append(text(x3, yb, "кожен стовпець накрито → усі три PI потрібні",
                  size=11, color=INK, anchor="start", bold=True))
    p.append(text(x3, yb + 20, "F = a·b + b·c + a·c", size=14, color=INK, anchor="start", bold=True))
    p.append(text(x3, yb + 42, "той самий мінімум, що дала карта Карно",
                  size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "qmc-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_truth_to_dnf()
    fig_kmap_majority()
    fig_qmc_flow()
    print("OK: truth-to-dnf, kmap-majority, qmc-flow")
