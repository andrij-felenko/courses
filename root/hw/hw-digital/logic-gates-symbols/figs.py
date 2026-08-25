# -*- coding: utf-8 -*-
"""Фігури до теми «Символи логічних вентилів».
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
    """AND: пряма спинка зліва, округлий ніс справа. (svg, x_out)."""
    x, y = cx - w / 2, cy - h / 2
    r = h / 2
    d = ("M %.1f,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L %.1f,%.1f Z"
         % (x, y, x + w / 2, y, r, r, x + w / 2, y + h, x, y + h))
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    return p, x + w / 2 + r, x


def gate_or(cx, cy, w=54, h=46, xor=False):
    """OR: увігнута спинка, гострий ніс. xor=True додає другу дугу. (svg, x_out, x_back)."""
    x, y = cx - w / 2, cy - h / 2
    nose = x + w
    d = ("M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f Q %.1f,%.1f %.1f,%.1f "
         "Q %.1f,%.1f %.1f,%.1f Z"
         % (x, y, x + w * 0.55, y, nose, cy,
            x + w * 0.55, y + h, x, y + h,
            x + w * 0.28, cy, x, y))
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    xb = x
    if xor:
        xb = x - 7
        arc = ("M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f"
               % (xb, y, xb + w * 0.28, cy, xb, y + h))
        p += '<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (arc, INK)
    return p, nose, xb


def gate_not(cx, cy, w=40, h=42, bubble=True, bubble_color=INK):
    """NOT: трикутник + кружок-інверсія (буфер — bubble=False). (svg, x_out, x_back)."""
    x, y = cx - w / 2, cy - h / 2
    tip = x + w
    d = "M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" % (x, y, x, y + h, tip, cy)
    p = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, BG, INK)
    if bubble:
        p += circle(tip + 6, cy, 6, fill="#fff", stroke=bubble_color, sw=2.4)
        return p, tip + 12, x
    return p, tip, x


def bub(cx, cy, color=INK):
    """Кружок-інверсія діаметром 12 із центром (cx,cy)."""
    return circle(cx, cy, 6, fill="#fff", stroke=color, sw=2.4)


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


def truth_cell(x, y, val, w=30, h=21):
    fill = "#fdf4f4" if val == 1 else "#f3f5fd"
    col = ONE if val == 1 else ZERO
    s = rect(x, y, w, h, fill=fill, stroke="#9aa3ad", sw=1.0, rx=0)
    s += text(x + w / 2, y + h / 2 + 4.2, str(val), size=11.5, color=col, bold=True)
    return s


def mini_tt(x0c, top, name, vals, unary=False, cw=28):
    """Мала таблиця істинності під символом (2-вхідна або 1-вхідна)."""
    ab = [(0, 0), (0, 1), (1, 0), (1, 1)]
    f = []
    ncol = 2 if unary else 3
    x0 = x0c - (ncol * cw) / 2
    heads = ["A", "Y"] if unary else ["A", "B", "Y"]
    for j, h_ in enumerate(heads):
        f += [rect(x0 + j * cw, top, cw, 21, fill="#eceef0", stroke="#9aa3ad", sw=1.0, rx=0),
              text(x0 + j * cw + cw / 2, top + 14.5, h_, size=11, bold=True)]
    if unary:
        for r, (a, y) in enumerate([(0, 1), (1, 0)]):
            yy = top + 21 * (r + 1)
            f += [truth_cell(x0, yy, a, w=cw), truth_cell(x0 + cw, yy, y, w=cw)]
    else:
        for r, (a, b) in enumerate(ab):
            yy = top + 21 * (r + 1)
            f += [truth_cell(x0, yy, a, w=cw), truth_cell(x0 + cw, yy, b, w=cw),
                  truth_cell(x0 + 2 * cw, yy, vals[r], w=cw)]
    return f


# ── 1. Шість основних символів + таблиці істинності ─────────────────────────
def fig_symbols():
    W, H = 880, 380
    f = []
    gy = 90
    cols = [110, 270, 430, 590, 750]   # AND OR NOT NAND NOR (рядок 1)
    # рядок 1: AND, OR, NOT, NAND, NOR
    # AND
    cx = cols[0]
    g, xo, _ = gate_and(cx, gy, w=42, h=40)
    f += [in_lead(cx - 50, cx - 21, gy - 9, "A"), in_lead(cx - 50, cx - 21, gy + 9, "B"),
          g, out_lead(xo, gy, xo + 26, "Y"), text(cx, gy - 32, "AND", size=12, bold=True),
          text(cx, gy + 40, "A·B", size=12, bold=True, color=ONE)]
    # OR
    cx = cols[1]
    g, xo, _ = gate_or(cx, gy, w=48, h=40)
    f += [in_lead(cx - 50, cx - 24, gy - 9, "A"), in_lead(cx - 50, cx - 24, gy + 9, "B"),
          g, out_lead(xo, gy, xo + 26, "Y"), text(cx, gy - 32, "OR", size=12, bold=True),
          text(cx, gy + 40, "A+B", size=12, bold=True, color=ONE)]
    # NOT
    cx = cols[2]
    g, xo, _ = gate_not(cx, gy, w=34, h=36, bubble_color=ONE)
    f += [in_lead(cx - 50, cx - 17, gy, "A"), g, out_lead(xo, gy, xo + 24, "Y"),
          text(cx, gy - 32, "NOT", size=12, bold=True),
          text(cx, gy + 40, "Ā", size=13, bold=True, color=ONE)]
    # NAND
    cx = cols[3]
    g, xo, _ = gate_and(cx, gy, w=42, h=40)
    f += [in_lead(cx - 50, cx - 21, gy - 9, "A"), in_lead(cx - 50, cx - 21, gy + 9, "B"),
          g, bub(xo + 6, gy, ONE), out_lead(xo + 12, gy, xo + 30, "Y"),
          text(cx, gy - 32, "NAND", size=12, bold=True),
          text(cx, gy + 40, "‾(A·B)", size=12, bold=True, color=ONE)]
    # NOR
    cx = cols[4]
    g, xo, _ = gate_or(cx, gy, w=48, h=40)
    f += [in_lead(cx - 50, cx - 24, gy - 9, "A"), in_lead(cx - 50, cx - 24, gy + 9, "B"),
          g, bub(xo + 6, gy, ONE), out_lead(xo + 12, gy, xo + 30, "Y"),
          text(cx, gy - 32, "NOR", size=12, bold=True),
          text(cx, gy + 40, "‾(A+B)", size=12, bold=True, color=ONE)]

    # рядок 2 (XOR) окремо зліва + таблиці істинності праворуч
    xy = 230
    cx = 110
    g, xo, _ = gate_or(cx, xy, w=48, h=40, xor=True)
    f += [in_lead(cx - 52, cx - 31, xy - 9, "A"), in_lead(cx - 52, cx - 31, xy + 9, "B"),
          g, out_lead(xo, xy, xo + 26, "Y"), text(cx, xy - 32, "XOR", size=12, bold=True),
          text(cx, xy + 40, "A⊕B", size=12, bold=True, color=ONE)]

    # таблиці істинності трьох ключових (AND, OR, XOR) під рядком 2
    tt_top = 200
    f += mini_tt(300, tt_top, "AND", [0, 0, 0, 1])
    f += mini_tt(470, tt_top, "OR", [0, 1, 1, 1])
    f += mini_tt(640, tt_top, "XOR", [0, 1, 1, 0])
    f += [text(300, tt_top - 8, "AND", size=11, bold=True),
          text(470, tt_top - 8, "OR", size=11, bold=True),
          text(640, tt_top - 8, "XOR", size=11, bold=True),
          text(790, tt_top + 40, "решта —", size=11, color=MUTED, italic=True, anchor="start"),
          text(790, tt_top + 56, "ці ж із", size=11, color=MUTED, italic=True, anchor="start"),
          text(790, tt_top + 72, "кружком", size=11, color=MUTED, italic=True, anchor="start")]

    b, _, _ = textbox(W / 2, 350,
                      "Форма проказує функцію; кружок на виході перетворює AND/OR/XOR на NAND/NOR/XNOR.",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "symbols.svg"), W, H, *f)


# ── 2. Кружок як модифікатор: на виході й на вході ──────────────────────────
def fig_bubble():
    W, H = 820, 340
    f = []
    gy = 130
    # буфер
    cx = 130
    g, xo, _ = gate_not(cx, gy, w=34, h=36, bubble=False)
    f += [in_lead(cx - 46, cx - 17, gy, "A"), g, out_lead(xo, gy, xo + 30, "Y"),
          text(cx, gy - 34, "буфер", size=12, bold=True),
          text(cx, gy + 44, "Y = A", size=12, bold=True)]
    # інвертор
    cx = 300
    g, xo, _ = gate_not(cx, gy, w=34, h=36, bubble=True, bubble_color=ONE)
    f += [in_lead(cx - 46, cx - 17, gy, "A"), g, out_lead(xo, gy, xo + 30, "Y"),
          text(cx, gy - 34, "інвертор", size=12, bold=True),
          text(cx, gy + 44, "Y = Ā", size=12, bold=True, color=ONE)]
    # AND
    cx = 490
    g, xo, xb = gate_and(cx, gy, w=44, h=42)
    f += [in_lead(cx - 50, xb, gy - 9, "A"), in_lead(cx - 50, xb, gy + 9, "B"),
          g, out_lead(xo, gy, xo + 30, "Y"), text(cx, gy - 34, "AND", size=12, bold=True),
          text(cx, gy + 44, "Y = A·B", size=12, bold=True)]
    # AND із вхідними кружками
    cx = 680
    g, xo, xb = gate_and(cx, gy, w=44, h=42)
    f += [line(cx - 50, gy - 9, xb - 12, gy - 9, color=INK, sw=1.8),
          line(cx - 50, gy + 9, xb - 12, gy + 9, color=INK, sw=1.8),
          bub(xb - 6, gy - 9, ONE), bub(xb - 6, gy + 9, ONE),
          text(cx - 56, gy - 5, "A", size=12, anchor="end", bold=True),
          text(cx - 56, gy + 13, "B", size=12, anchor="end", bold=True),
          g, out_lead(xo, gy, xo + 30, "Y"),
          text(cx, gy - 34, "вх. кружки", size=12, bold=True),
          text(cx, gy + 44, "Y = Ā·B̄", size=12, bold=True, color=ONE)]

    f += [text(215, gy + 78, "кружок на ВИХОДІ → інверсія результату", size=11.5, color=MUTED, italic=True),
          text(585, gy + 78, "кружок на ВХОДІ → вхід активний на нулі", size=11.5, color=MUTED, italic=True)]
    b, _, _ = textbox(W / 2, 312,
                      "Кружок означає «перевернути тут» незалежно від місця: на виході — інверсія, на вході — активний нуль.",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "bubble.svg"), W, H, *f)


# ── 3. Три стандарти: ANSI відмітні / IEC прямокутники / старі DIN ──────────
def fig_standards():
    W, H = 820, 320
    f = [text(215, 38, "Відмітні форми (ANSI/IEEE)", size=12.5, bold=True),
         text(470, 38, "Прямокутні (IEC 60617)", size=12.5, bold=True),
         text(700, 38, "Старі DIN (скасовані)", size=12.5, bold=True)]
    rows = [("AND", "&", 92), ("OR", "≥1", 162), ("XOR", "=1", 232)]
    for name, iec_lbl, gy in rows:
        f.append(text(58, gy + 4, name, size=12.5, bold=True, anchor="start"))
        # ANSI відмітна форма
        if name == "AND":
            g, xo, xb = gate_and(225, gy, w=38, h=36)
        elif name == "OR":
            g, xo, xb = gate_or(225, gy, w=46, h=36)
        else:
            g, xo, xb = gate_or(228, gy, w=46, h=36, xor=True)
        f += [line(135, gy, xb, gy, color=INK, sw=1.8),
              g, line(xo, gy, xo + 30, gy, color=INK, sw=1.8)]
        # IEC бокс
        bx, bw = 445, 54
        f += [line(bx - 30, gy, bx, gy, color=INK, sw=1.8),
              rect(bx, gy - 23, bw, 46, fill=BG, stroke=INK, sw=2, rx=0),
              text(bx + bw / 2, gy + 5, iec_lbl, size=13, bold=True),
              line(bx + bw, gy, bx + bw + 30, gy, color=INK, sw=1.8)]
        # старий DIN — півколо/рамка з іншим написом
        dx, dw = 672, 54
        din = {"AND": "&", "OR": "1", "XOR": "=1"}[name]
        f += [line(dx - 30, gy, dx, gy, color=INK, sw=1.8),
              rect(dx, gy - 23, dw, 46, fill="#f7f3ec", stroke=MUTED, sw=1.8, rx=0),
              text(dx + dw / 2, gy + 5, din, size=13, bold=True, color=MUTED),
              line(dx + dw, gy, dx + dw + 30, gy, color=INK, sw=1.8)]
    b, _, _ = textbox(W / 2, 296,
                      "Та сама функція — три накреслення. У IEC напис: & = AND, ≥1 = OR, =1 = XOR.",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "standards.svg"), W, H, *f)


# ── 4. Штовхання бульбашки: NAND = OR із вхідними кружками ───────────────────
def fig_bubble_push():
    W, H = 800, 300
    f = []
    gy = 130
    # NAND (ліворуч)
    cx = 180
    g, xo, _ = gate_and(cx, gy, w=48, h=46)
    f += [in_lead(cx - 56, cx - 24, gy - 11, "A"), in_lead(cx - 56, cx - 24, gy + 11, "B"),
          g, bub(xo + 6, gy, ONE), out_lead(xo + 12, gy, xo + 34, "Y"),
          text(cx, gy - 38, "NAND", size=13, bold=True),
          text(cx, gy + 52, "Y = ‾(A·B)", size=13, bold=True, color=ONE)]
    # знак рівності
    f.append(text(W / 2, gy + 6, "=", size=30, bold=True, color=FIELD))
    # OR із вхідними кружками (праворуч)
    cx = 560
    g, xo, xb = gate_or(cx, gy, w=54, h=46)
    f += [line(cx - 62, gy - 11, xb - 12, gy - 11, color=INK, sw=1.8),
          line(cx - 62, gy + 11, xb - 12, gy + 11, color=INK, sw=1.8),
          bub(xb - 6, gy - 11, ONE), bub(xb - 6, gy + 11, ONE),
          text(cx - 68, gy - 7, "A", size=12, anchor="end", bold=True),
          text(cx - 68, gy + 15, "B", size=12, anchor="end", bold=True),
          g, out_lead(xo, gy, xo + 34, "Y"),
          text(cx, gy - 38, "OR з вх. кружками", size=13, bold=True),
          text(cx, gy + 52, "Y = Ā+B̄", size=13, bold=True, color=ONE)]
    b, _, _ = textbox(W / 2, 272,
                      "Закон Де Моргана: ‾(A·B) = Ā+B̄ — одна функція, два символи (бульбашки «перекинуто» з виходу на входи).",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "bubble-push.svg"), W, H, *f)


# ── 5. Зчитування ланцюжка: Y = ‾(A·B) + C ──────────────────────────────────
def fig_chain():
    W, H = 720, 300
    f = []
    # NAND згори
    ax, ay = 290, 120
    g_and, xo_and, _ = gate_and(ax, ay, w=46, h=44)
    f += [in_lead(150, ax - 23, ay - 11, None),
          text(140, ay - 7, "A", size=12, color=INK, anchor="end", bold=True),
          in_lead(150, ax - 23, ay + 11, None),
          text(140, ay + 15, "B", size=12, color=INK, anchor="end", bold=True),
          g_and, bub(xo_and + 6, ay, ONE), text(ax, ay - 32, "NAND", size=12, bold=True)]
    # дріт P від NAND до OR
    px = xo_and + 12
    f += [line(px, ay, 420, ay, color=INK, sw=1.8),
          line(420, ay, 420, 190, color=INK, sw=1.8),
          line(420, 190, 462, 190, color=INK, sw=1.8),
          text(372, ay - 9, "P = ‾(A·B)", size=12, color=FIELD, bold=True)]
    # OR знизу
    ox, oy = 500, 200
    g_or, xo_or, _ = gate_or(ox, oy, w=54, h=46)
    f += [line(150, 222, 465, 222, color=INK, sw=1.8),
          text(140, 226, "C", size=12, color=INK, anchor="end", bold=True),
          g_or, out_lead(xo_or, oy, xo_or + 40, None),
          text(xo_or + 46, oy + 4, "Y", size=13, color=FIELD, bold=True, anchor="start"),
          text(ox + 2, oy - 32, "OR", size=12, bold=True)]
    # стрілка напряму читання
    f.append(arrow(165, 262, 235, 262, color=MUTED))
    f.append(text(245, 266, "читаємо зліва направо, від входів до виходу", size=11, color=MUTED, italic=True, anchor="start"))
    render(os.path.join(IMG, "chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_symbols()
    fig_bubble()
    fig_standards()
    fig_bubble_push()
    fig_chain()
    print("OK: 5 figures ->", IMG)
