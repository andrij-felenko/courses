# -*- coding: utf-8 -*-
"""Фігури до теми «Базові вентилі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Підпис фігури несе .md, тож великого заголовка всередині малюнка немає (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ZERO = NEG   # «0» — холодний синій
ONE  = POS   # «1» — гарячий червоний


# ── примітиви форм вентилів (входи зліва, вихід справа) ──────────────────────
def gate_and(cx, cy, w=46, h=46):
    """AND: пряма спинка зліва, округлий ніс справа. Повертає (svg, x_out)."""
    x, y = cx - w / 2, cy - h / 2
    r = h / 2
    d = ("M %.1f,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L %.1f,%.1f Z"
         % (x, y, x + w / 2, y, r, r, x + w / 2, y + h, x, y + h))
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    return p, x + w / 2 + r


def gate_or(cx, cy, w=54, h=46):
    """OR: увігнута спинка, гострий ніс. Повертає (svg, x_out)."""
    x, y = cx - w / 2, cy - h / 2
    nose = x + w
    d = ("M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f Q %.1f,%.1f %.1f,%.1f "
         "Q %.1f,%.1f %.1f,%.1f Z"
         % (x, y, x + w * 0.55, y, nose, cy,
            x + w * 0.55, y + h, x, y + h,
            x + w * 0.28, cy, x, y))
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    return p, nose


def gate_not(cx, cy, w=40, h=42, bubble=True, bubble_color=INK):
    """NOT: трикутник + кружок-інверсія (буфер — bubble=False). (svg, x_out)."""
    x, y = cx - w / 2, cy - h / 2
    tip = x + w
    d = "M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" % (x, y, x, y + h, tip, cy)
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    if bubble:
        p += circle(tip + 6, cy, 6, fill="#fff", stroke=bubble_color, sw=2.4)
        return p, tip + 12
    return p, tip


def in_lead(x0, cx, cy, label=None, color=INK):
    s = line(x0, cy, cx, cy, color=INK, sw=1.8)
    if label is not None:
        s += text(x0 - 6, cy + 4, label, size=12, color=color, anchor="end", bold=True)
    return s


def out_lead(x_out, cy, x1, label=None, color=FIELD):
    s = line(x_out, cy, x1, cy, color=INK, sw=1.8)
    if label is not None:
        s += text(x1 + 6, cy + 4, label, size=12, color=color, anchor="start", bold=True)
    return s


def truth_cell(x, y, val, w=34, h=22):
    """Клітинка таблиці істинності з кольором за значенням."""
    fill = "#fdf4f4" if val == 1 else "#f3f5fd"
    col = ONE if val == 1 else ZERO
    s = rect(x, y, w, h, fill=fill, stroke="#9aa3ad", sw=1.0, rx=0)
    s += text(x + w / 2, y + h / 2 + 4.3, str(val), size=12, color=col, bold=True)
    return s


# ── 1. Три базові символи + їхні таблиці істинності ──────────────────────────
def fig_symbols():
    W, H = 840, 360
    f = []
    cols = [180, 430, 680]          # центри AND / OR / NOT
    gy = 96                          # рівень символів
    names = [("AND", "кон'юнктор", "Y = A · B"),
             ("OR", "диз'юнктор", "Y = A + B"),
             ("NOT", "інвертор", "Y = Ā")]

    # AND
    cx = cols[0]
    g, xo = gate_and(cx, gy)
    f += [in_lead(cx - 60, cx - 23, gy - 11, "A"), in_lead(cx - 60, cx - 23, gy + 11, "B"),
          g, out_lead(xo, gy, xo + 34, "Y")]
    # OR
    cx = cols[1]
    g, xo = gate_or(cx, gy)
    f += [in_lead(cx - 60, cx - 27, gy - 11, "A"), in_lead(cx - 60, cx - 27, gy + 11, "B"),
          g, out_lead(xo, gy, xo + 34, "Y")]
    # NOT
    cx = cols[2]
    g, xo = gate_not(cx, gy, bubble_color=ONE)
    f += [in_lead(cx - 60, cx - 20, gy, "A"), g, out_lead(xo, gy, xo + 34, "Y")]

    # підписи назв + формула
    for cx, (en, ua, eq) in zip(cols, names):
        f += [text(cx, gy - 36, "%s (%s)" % (en, ua), size=13, bold=True),
              text(cx, gy + 50, eq, size=14, bold=True, color=ONE)]

    # таблиці істинності під кожним символом
    ty = 178
    cw = 34
    # AND / OR — двовхідні
    rows2 = {"AND": [0, 0, 0, 1], "OR": [0, 1, 1, 1]}
    ab = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for idx, key in (("0", "AND"), ("1", "OR")):
        cx = cols[int(idx)]
        x0 = cx - 1.5 * cw
        # шапка
        for j, h_ in enumerate(["A", "B", "Y"]):
            f += [rect(x0 + j * cw, ty, cw, 22, fill="#eceef0", stroke="#9aa3ad", sw=1.1, rx=0),
                  text(x0 + j * cw + cw / 2, ty + 15, h_, size=12, bold=True)]
        for r, (a, b) in enumerate(ab):
            yy = ty + 22 * (r + 1)
            f += [truth_cell(x0, yy, a), truth_cell(x0 + cw, yy, b),
                  truth_cell(x0 + 2 * cw, yy, rows2[key][r])]
    # NOT — одновхідна
    cx = cols[2]
    x0 = cx - cw
    for j, h_ in enumerate(["A", "Y"]):
        f += [rect(x0 + j * cw, ty, cw, 22, fill="#eceef0", stroke="#9aa3ad", sw=1.1, rx=0),
              text(x0 + j * cw + cw / 2, ty + 15, h_, size=12, bold=True)]
    for r, (a, y) in enumerate([(0, 1), (1, 0)]):
        yy = ty + 22 * (r + 1)
        f += [truth_cell(x0, yy, a), truth_cell(x0 + cw, yy, y)]

    b, _, _ = textbox(W / 2, 330,
                      "Форма підказує функцію: пряма спинка — AND, кругла — OR, трикутник із кружком — NOT.",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "symbols.svg"), W, H, *f)


# ── 2. Кружок-інверсія: буфер проти інвертора ───────────────────────────────
def fig_bubble():
    W, H = 760, 320
    f = []
    gy = 150
    # буфер
    cx = 170
    g, xo = gate_not(cx, gy, bubble=False)
    f += [in_lead(cx - 56, cx - 20, gy, "A"), g, out_lead(xo, gy, xo + 40, "Y"),
          text(cx, gy - 44, "буфер", size=14, bold=True),
          text(cx, gy + 56, "Y = A", size=14, bold=True, color=INK),
          text(cx, gy + 80, "лише підсилює / відновлює", size=11, color=MUTED, italic=True)]
    # інвертор
    cx = 430
    g, xo = gate_not(cx, gy, bubble=True, bubble_color=ONE)
    f += [in_lead(cx - 56, cx - 20, gy, "A"), g, out_lead(xo, gy, xo + 40, "Y"),
          text(cx, gy - 44, "інвертор", size=14, bold=True),
          text(cx, gy + 56, "Y = Ā", size=14, bold=True, color=ONE),
          text(cx, gy + 80, "той самий трикутник + кружок", size=11, color=MUTED, italic=True)]
    # рамка-правило
    b = fitbox(600, 96, 144, 112,
               "Кружок на ніжці\n= інверсія\nв цій точці.\nЗвідси NAND, NOR.",
               size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "bubble.svg"), W, H, *f)


# ── 3. Два стандарти символів: відмітні форми проти IEC-прямокутників ────────
def fig_iec():
    W, H = 820, 330
    f = [text(235, 40, "Відмітні форми (ANSI/IEEE)", size=13, bold=True),
         text(600, 40, "Прямокутні (IEC / ДСТУ)", size=13, bold=True)]
    rows = [("AND", 96), ("OR", 176), ("NOT", 256)]
    iec_label = {"AND": "&", "OR": "≥1", "NOT": "1"}
    for name, gy in rows:
        f.append(text(70, gy + 4, name, size=13, bold=True, anchor="start"))
        # ліворуч — відмітна форма
        if name == "AND":
            g, xo = gate_and(245, gy, w=40, h=38)
        elif name == "OR":
            g, xo = gate_or(245, gy, w=48, h=38)
        else:
            g, xo = gate_not(243, gy, w=36, h=36, bubble_color=INK)
        f += [line(150, gy, 245 - (20 if name != "OR" else 24), gy, color=INK, sw=1.8),
              g, line(xo, gy, xo + 36, gy, color=INK, sw=1.8)]
        # праворуч — IEC-бокс
        bx, bw = 575, 60
        f += [line(bx - 35, gy, bx, gy, color=INK, sw=1.8),
              rect(bx, gy - 25, bw, 50, fill=BG, stroke=INK, sw=2, rx=0),
              text(bx + bw / 2, gy + 5, iec_label[name], size=14, bold=True)]
        if name == "NOT":
            f += [circle(bx + bw + 6, gy, 6, fill="#fff", stroke=INK, sw=2),
                  line(bx + bw + 12, gy, bx + bw + 45, gy, color=INK, sw=1.8)]
        else:
            f.append(line(bx + bw, gy, bx + bw + 45, gy, color=INK, sw=1.8))
    b, _, _ = textbox(W / 2, 305,
                      "У IEC-боксі функцію пише напис: & = AND, ≥1 = OR, 1 з кружком = NOT.",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "iec.svg"), W, H, *f)


# ── 4. Багатовхідні вентилі: 3-вхідні AND і OR ──────────────────────────────
def fig_multi():
    W, H = 760, 300
    f = []
    gy = 130
    # 3-вхідний AND
    cx = 200
    g, xo = gate_and(cx, gy, w=56, h=64)
    f += [in_lead(cx - 64, cx - 28, gy - 18, "A"), in_lead(cx - 64, cx - 28, gy, "B"),
          in_lead(cx - 64, cx - 28, gy + 18, "C"), g, out_lead(xo, gy, xo + 36, "Y"),
          text(cx, gy - 50, "3-вхідний AND", size=13, bold=True),
          text(cx, gy + 56, "Y = A · B · C", size=13, bold=True, color=ONE),
          text(cx, gy + 78, "1 лише за A=B=C=1", size=11, color=MUTED, italic=True)]
    # 3-вхідний OR
    cx = 560
    g, xo = gate_or(cx, gy, w=64, h=64)
    f += [in_lead(cx - 70, cx - 32, gy - 18, "A"), in_lead(cx - 70, cx - 32, gy, "B"),
          in_lead(cx - 70, cx - 32, gy + 18, "C"), g, out_lead(xo, gy, xo + 36, "Y"),
          text(cx, gy - 50, "3-вхідний OR", size=13, bold=True),
          text(cx, gy + 56, "Y = A + B + C", size=13, bold=True, color=ONE),
          text(cx, gy + 78, "0 лише за A=B=C=0", size=11, color=MUTED, italic=True)]
    b, _, _ = textbox(W / 2, 272,
                      "Більше входів — та сама ідея «всі / хоч один»: одним вентилем перевіряють умову над багатьма сигналами.",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "multi.svg"), W, H, *f)


# ── 5. Зʼєднання вентилів у вираз Y = A·B + C ────────────────────────────────
def fig_wiring():
    W, H = 720, 320
    f = []
    # AND згори
    ax, ay = 300, 130
    g_and, xo_and = gate_and(ax, ay, w=46, h=44)
    f += [in_lead(150, ax - 23, ay - 11, None), text(140, ay - 7, "A = 1", size=12, color=ONE, anchor="end", bold=True),
          in_lead(150, ax - 23, ay + 11, None), text(140, ay + 15, "B = 1", size=12, color=ONE, anchor="end", bold=True),
          g_and]
    # дріт P від AND до OR
    px = xo_and
    f += [line(px, ay, 430, ay, color=INK, sw=1.8),
          line(430, ay, 430, 200, color=INK, sw=1.8),
          line(430, 200, 470, 200, color=INK, sw=1.8),
          text(385, ay - 9, "P = A·B = 1", size=12, color=FIELD, bold=True)]
    # OR знизу
    ox, oy = 500, 210
    g_or, xo_or = gate_or(ox, oy, w=54, h=46)
    f += [line(150, 232, 473, 232, color=INK, sw=1.8),
          text(140, 236, "C = 0", size=12, color=ZERO, anchor="end", bold=True),
          g_or, out_lead(xo_or, oy, xo_or + 40, None),
          text(xo_or + 46, oy + 4, "Y = 1", size=13, color=FIELD, bold=True, anchor="start"),
          text(ax, ay - 32, "AND", size=12, bold=True),
          text(ox + 2, oy - 32, "OR", size=12, bold=True)]
    b = fitbox(60, 268, 600, 40,
               "Вихід AND (P) заводять на вхід OR; другий вхід OR — це C. Так вираз Y = A·B + C «оживає» в залізі.",
               size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 6. Worked-приклад: таблиці істинності AND/OR/NOT/NAND/XOR ────────────────
def fig_truthtables():
    W, H = 820, 330
    f = []
    cw = 30
    ab = [(0, 0), (0, 1), (1, 0), (1, 1)]
    # п'ять колонок; NOT — одновхідна
    specs = [
        ("AND", "A·B", [0, 0, 0, 1], False),
        ("OR", "A+B", [0, 1, 1, 1], False),
        ("NAND", "A·B з кружком", [1, 1, 1, 0], False),
        ("XOR", "A⊕B", [0, 1, 1, 0], False),
        ("NOT", "Ā", [1, 0], True),
    ]
    xs = [70, 225, 380, 545, 710]
    top = 70
    for (name, eq, vals, unary), x0c in zip(specs, xs):
        ncol = 2 if unary else 3
        x0 = x0c - (ncol * cw) / 2
        f += [text(x0c, top - 26, name, size=13, bold=True),
              text(x0c, top - 8, eq, size=11, color=MUTED, italic=True)]
        heads = ["A", "Y"] if unary else ["A", "B", "Y"]
        for j, h_ in enumerate(heads):
            f += [rect(x0 + j * cw, top, cw, 22, fill="#eceef0", stroke="#9aa3ad", sw=1.0, rx=0),
                  text(x0 + j * cw + cw / 2, top + 15, h_, size=11.5, bold=True)]
        if unary:
            for r, (a, y) in enumerate([(0, 1), (1, 0)]):
                yy = top + 22 * (r + 1)
                f += [truth_cell(x0, yy, a, w=cw), truth_cell(x0 + cw, yy, y, w=cw)]
        else:
            for r, (a, b) in enumerate(ab):
                yy = top + 22 * (r + 1)
                f += [truth_cell(x0, yy, a, w=cw), truth_cell(x0 + cw, yy, b, w=cw),
                      truth_cell(x0 + 2 * cw, yy, vals[r], w=cw)]
    b = fitbox(60, 254, W - 120, 48,
               "NAND = стовпчик AND, перевернутий кружком. XOR = 1, коли входи РІЗНІ.",
               size=13, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "truthtables.svg"), W, H, *f)


if __name__ == "__main__":
    fig_symbols()
    fig_bubble()
    fig_iec()
    fig_multi()
    fig_wiring()
    fig_truthtables()
    print("OK: 6 figures ->", IMG)
