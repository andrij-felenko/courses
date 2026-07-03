# -*- coding: utf-8 -*-
"""Фігури до курс-теми «Бітові операції» (embedded / prohramuvannia).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def bitcell(x, y, val, cell=30):
    """Клітинка одного біта: червона для 1, синя для 0."""
    c = POS if val else NEG
    bg = RED_BG if val else BLUE_BG
    return (rect(x, y, cell, cell, fill=bg, stroke=c, sw=1.8, rx=5) +
            text(x + cell / 2, y + cell * 0.68, str(val), size=15, color=c, bold=True))


def bitrow(x, y, bits, cell=30, gap=3):
    """Рядок бітів (список 0/1) зліва направо."""
    f = ""
    for i, v in enumerate(bits):
        f += bitcell(x + i * (cell + gap), y, v, cell)
    return f


# ════════════════ 1. Чотири логічні операції ═════════════════════════════════
def fig_logic_ops():
    W, H = 940, 720
    f = []
    # Дані: кожна операція — (назва, символ, колір, таблиця з 4 рядків, приклад A,B,R)
    A = [1, 0, 1, 1, 0, 0, 1, 0]
    B = [1, 1, 0, 1, 0, 1, 1, 0]

    def AND(a, b): return a & b
    def OR(a, b):  return a | b
    def XOR(a, b): return a ^ b

    ops = [
        ("І  (AND)", "&", "1 лише коли ОБИДВА 1",
         [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)],
         A, B, [AND(a, b) for a, b in zip(A, B)]),
        ("АБО  (OR)", "|", "1 коли ХОЧ ОДИН 1",
         [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)],
         A, B, [OR(a, b) for a, b in zip(A, B)]),
        ("XOR", "^", "1 коли біти РІЗНІ",
         [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)],
         A, B, [XOR(a, b) for a, b in zip(A, B)]),
    ]

    y0 = 62
    row_h = 150
    for oi, (name, sym, tip, tbl, aa, bb, rr) in enumerate(ops):
        yb = y0 + oi * row_h
        # заголовок операції
        f.append(rect(30, yb, 200, row_h - 20, fill="#fafafa", stroke=INK, sw=1.6, rx=10))
        f.append(mono(130, yb + 34, sym, size=30, color=POS, anchor="middle", bold=True))
        f.append(text(130, yb + 62, name, size=15, color=INK, bold=True))
        f.append(text(130, yb + 86, tip, size=11, color=MUTED))
        # таблиця істинності
        tx = 258
        f.append(text(tx + 90, yb + 6, "таблиця істинності", size=11, color=MUTED, bold=True))
        heads = ["a", "b", sym]
        for j, hh in enumerate(heads):
            f.append(mono(tx + 26 + j * 56, yb + 26, hh, size=13, color=MUTED, anchor="middle", bold=True))
        for ri, (a, b, r) in enumerate(tbl):
            ry = yb + 36 + ri * 24
            for j, v in enumerate([a, b, r]):
                col = POS if v else NEG
                bg = RED_BG if v else BLUE_BG
                f.append(rect(tx + 8 + j * 56, ry, 36, 20, fill=bg if j == 2 else BG,
                              stroke=col if j == 2 else "#dcdcdc", sw=1.4 if j == 2 else 1.0, rx=3))
                f.append(mono(tx + 26 + j * 56, ry + 15, str(v),
                              size=12, color=col, anchor="middle", bold=(j == 2)))
        # приклад на байтах
        ex = 470
        cell = 30
        f.append(text(ex + 4 * (cell + 3), yb + 6, "той самий на цілому байті", size=11, color=MUTED, bold=True))
        f.append(mono(ex - 12, yb + 41, "a", size=13, color=INK, anchor="end", bold=True))
        f.append(bitrow(ex, yb + 24, aa, cell))
        f.append(mono(ex - 12, yb + 74, "b", size=13, color=INK, anchor="end", bold=True))
        f.append(bitrow(ex, yb + 57, bb, cell))
        f.append(line(ex - 30, yb + 92, ex + 8 * (cell + 3) - 3, yb + 92, color=INK, sw=1.6))
        f.append(mono(ex - 30, yb + 88, sym, size=15, color=POS, anchor="start", bold=True))
        f.append(mono(ex - 12, yb + 114, "=", size=15, color=INK, anchor="end", bold=True))
        f.append(bitrow(ex, yb + 97, rr, cell))

    # НЕ окремо
    yn = y0 + 3 * row_h
    f.append(rect(30, yn, 200, 100, fill="#fafafa", stroke=INK, sw=1.6, rx=10))
    f.append(mono(130, yn + 40, "~", size=32, color=NEG, anchor="middle", bold=True))
    f.append(text(130, yn + 66, "НЕ  (NOT)", size=15, color=INK, bold=True))
    f.append(text(130, yn + 88, "перевертає кожен біт", size=11, color=MUTED))
    n_in = [0, 0, 0, 0, 1, 1, 1, 1]
    n_out = [1 - v for v in n_in]
    ex = 470
    cell = 30
    f.append(text(ex + 4 * (cell + 3), yn + 6, "одномісна: один вхід", size=11, color=MUTED, bold=True))
    f.append(mono(ex - 12, yn + 41, "x", size=13, color=INK, anchor="end", bold=True))
    f.append(bitrow(ex, yn + 24, n_in, cell))
    f.append(line(ex - 30, yn + 59, ex + 8 * (cell + 3) - 3, yn + 59, color=INK, sw=1.6))
    f.append(mono(ex - 30, yn + 55, "~", size=17, color=NEG, anchor="start", bold=True))
    f.append(mono(ex - 12, yn + 81, "=", size=15, color=INK, anchor="end", bold=True))
    f.append(bitrow(ex, yn + 64, n_out, cell))

    f.append(rect(30, H - 44, W - 60, 30, fill=GREEN_BG, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(W / 2, H - 24,
                  "Кожен розряд рахується САМ по собі, не оглядаючись на сусідів — тому операції й звуть побітовими.",
                  size=12, color=INK, bold=True))
    out("logic-ops.svg", W, H, *f,
        title="Чотири логічні операції: & (І), | (АБО), ^ (XOR), ~ (НЕ)")


# ════════════════ 2. Зсуви ліворуч і праворуч ════════════════════════════════
def fig_shifts():
    W, H = 900, 508
    f = []
    cell = 40
    x0 = 300

    # ── зсув ліворуч: x << 3 ──
    x = [0, 0, 0, 0, 0, 1, 0, 1]   # 0b00000101 = 5
    xl = [0, 0, 1, 0, 1, 0, 0, 0]  # 5 << 3 = 40 = 0b00101000
    yb = 74
    f.append(text(x0 + 4 * cell, yb - 26, "ЗСУВ ЛІВОРУЧ:  x << 3   (× 2³ = × 8)", size=14, color=INK, bold=True))
    f.append(mono(x0 - 14, yb + 28, "x", size=15, color=INK, anchor="end", bold=True))
    f.append(bitrow(x0, yb, x, cell, gap=2))
    f.append(mono(x0 + 8 * (cell + 2), yb + 28, "= 5", size=14, color=MUTED, anchor="start"))
    # стрілки вліво
    for i in range(8):
        cx = x0 + i * (cell + 2) + cell / 2
        f.append(arrow(cx, yb + cell + 24, cx - 3 * (cell + 2), yb + cell + 24, color=POS, sw=1.8))
    f.append(text(x0 + 4 * cell, yb + cell + 44, "усі біти їдуть на 3 позиції ліворуч", size=11, color=POS, bold=True))
    # результат
    yr = yb + cell + 64
    f.append(mono(x0 - 14, yr + 28, "=", size=15, color=INK, anchor="end", bold=True))
    for i, v in enumerate(xl):
        cx = x0 + i * (cell + 2)
        if i >= 5:  # набіглі нулі праворуч
            f.append(rect(cx, yr, cell, cell, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=5))
            f.append(text(cx + cell / 2, yr + cell * 0.68, "0", size=15, color=FIELD, bold=True))
        else:
            f.append(bitcell(cx, yr, v, cell))
    f.append(mono(x0 + 8 * (cell + 2), yr + 28, "= 40", size=14, color=MUTED, anchor="start"))
    f.append(text(x0 + 6.5 * cell, yr + cell + 18, "праворуч набігли нулі →", size=10.5, color=FIELD, anchor="start"))
    # межа зліва — випадають старші
    f.append(line(x0 - 4, yb - 6, x0 - 4, yr + cell + 6, color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(x0 - 8, yb - 12, "межа типу", size=9.5, color=MUTED, anchor="end"))

    # ── зсув праворуч: y >> 2 (беззнаковий) ──
    y2b = 330
    yv = [0, 0, 1, 0, 1, 1, 0, 0]   # 44
    yr2 = [0, 0, 0, 0, 1, 0, 1, 1]  # 44 >> 2 = 11
    f.append(text(x0 + 4 * cell, y2b - 26, "ЗСУВ ПРАВОРУЧ:  y >> 2   (÷ 2² = ÷ 4, без остачі)", size=14, color=INK, bold=True))
    f.append(mono(x0 - 14, y2b + 28, "y", size=15, color=INK, anchor="end", bold=True))
    f.append(bitrow(x0, y2b, yv, cell, gap=2))
    f.append(mono(x0 + 8 * (cell + 2), y2b + 28, "= 44", size=14, color=MUTED, anchor="start"))
    for i in range(8):
        cx = x0 + i * (cell + 2) + cell / 2
        f.append(arrow(cx, y2b + cell + 22, cx + 2 * (cell + 2), y2b + cell + 22, color=NEG, sw=1.8))
    f.append(text(x0 + 4 * cell, y2b + cell + 42, "усі біти їдуть на 2 позиції праворуч (для беззнакового зліва набігають нулі)",
                  size=11, color=NEG, bold=True))
    yr3 = y2b + cell + 62
    f.append(mono(x0 - 14, yr3 + 28, "=", size=15, color=INK, anchor="end", bold=True))
    for i, v in enumerate(yr3v := yr2):
        cx = x0 + i * (cell + 2)
        if i < 2:
            f.append(rect(cx, yr3, cell, cell, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=5))
            f.append(text(cx + cell / 2, yr3 + cell * 0.68, "0", size=15, color=FIELD, bold=True))
        else:
            f.append(bitcell(cx, yr3, v, cell))
    f.append(mono(x0 + 8 * (cell + 2), yr3 + 28, "= 11", size=14, color=MUTED, anchor="start"))
    f.append(text(x0, yr3 + cell + 18, "молодші два біти випали — остача відкинута", size=10.5, color=NEG, anchor="start"))

    out("shifts.svg", W, H, *f,
        title="Зсуви: пересунути біти вздовж числа (і водночас × чи ÷ на 2ⁿ)")


# ════════════════ 3. Чотири дії з бітом через маску ══════════════════════════
def fig_mask_ops():
    W, H = 940, 620
    f = []
    cell = 34
    gap = 3

    reg = [1, 0, 1, 1, 0, 0, 1, 0]  # приклад регістра
    # позиції бітів у масиві (0 — ліворуч=біт7 ... 7=біт0). Індекс масиву для біта n: 7-n
    def idx(bit): return 7 - bit

    panels = [
        # (заголовок, код, target_bit, дія над бітом, підпис-результат, колір)
        ("ВСТАНОВИТИ  (у 1)", "reg |= (1 << 3);", 3, "set", "біт 3 → 1, решта без змін", POS),
        ("СКИНУТИ  (у 0)", "reg &= ~(1 << 3);", 3, "clr", "біт 3 → 0, решта без змін", NEG),
        ("ПЕРЕВІРИТИ", "if (reg & (1 << 7))", 7, "test", "лишається тільки біт 7 → if бачить, 0 чи 1", AMBER),
        ("ПЕРЕМКНУТИ  (0↔1)", "reg ^= (1 << 2);", 2, "tgl", "біт 2 перевертається, решта без змін", FIELD),
    ]

    x0 = 250
    y0 = 56
    ph = 138
    for pi, (title_, code, tb, act, res, col) in enumerate(panels):
        yb = y0 + pi * ph
        # ліва картка
        f.append(rect(28, yb, 200, ph - 16, fill="#fafafa", stroke=col, sw=1.7, rx=10))
        f.append(text(128, yb + 26, title_, size=13.5, color=col, bold=True))
        f.append(mono(128, yb + 54, code, size=13, color=INK, anchor="middle", bold=True))
        f.append(text(128, yb + 82, res, size=10, color=MUTED))
        # маска зверху: показати, де «вікно»
        maskbits = [1 if (7 - i) == tb else 0 for i in range(8)]
        f.append(mono(x0 - 14, yb + 26, "маска", size=11, color=MUTED, anchor="end"))
        for i, v in enumerate(maskbits):
            cx = x0 + i * (cell + gap)
            if v:
                f.append(rect(cx, yb + 8, cell, 24, fill=AMBER_BG, stroke=AMBER, sw=2, rx=4))
                f.append(text(cx + cell / 2, yb + 25, "1", size=13, color=AMBER, bold=True))
                f.append(text(cx + cell / 2, yb + 4, "вікно", size=8.5, color=AMBER, bold=True))
            else:
                f.append(rect(cx, yb + 8, cell, 24, fill="#f0f0f0", stroke="#cfcfcf", sw=1.0, rx=4))
                f.append(text(cx + cell / 2, yb + 25, "0", size=12, color=MUTED))
        # регістр до / після
        f.append(mono(x0 - 14, yb + 66, "reg", size=12, color=INK, anchor="end", bold=True))
        f.append(bitrow(x0, yb + 48, reg, cell, gap))
        # результат-рядок
        after = list(reg)
        note = ""
        if act == "set":
            after[idx(tb)] = 1
        elif act == "clr":
            after[idx(tb)] = 0
        elif act == "tgl":
            after[idx(tb)] = 1 - reg[idx(tb)]
        elif act == "test":
            after = [reg[i] if (7 - i) == tb else 0 for i in range(8)]
        # стрілка вниз на цільовому біті
        cx = x0 + idx(tb) * (cell + gap) + cell / 2
        f.append(arrow(cx, yb + 48 + cell + 2, cx, yb + 48 + cell + 16, color=col, sw=2))
        lab = "=" if act != "test" else "&="
        f.append(mono(x0 - 14, yb + 66 + 38, lab, size=13, color=INK, anchor="end", bold=True))
        for i, v in enumerate(after):
            cx2 = x0 + i * (cell + gap)
            hot = ((7 - i) == tb)
            if act == "test" and not hot:
                f.append(rect(cx2, yb + 48 + 34, cell, cell, fill="#f0f0f0", stroke="#cfcfcf", sw=1.0, rx=5))
                f.append(text(cx2 + cell / 2, yb + 48 + 34 + cell * 0.68, "0", size=14, color=MUTED))
            else:
                bc = POS if v else NEG
                bg = RED_BG if v else BLUE_BG
                sw = 2.6 if hot else 1.8
                f.append(rect(cx2, yb + 48 + 34, cell, cell, fill=bg, stroke=(col if hot else bc), sw=sw, rx=5))
                f.append(text(cx2 + cell / 2, yb + 48 + 34 + cell * 0.68, str(v), size=14, color=(col if hot else bc), bold=hot))

    f.append(rect(28, H - 44, W - 56, 30, fill=GREEN_BG, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(W / 2, H - 24,
                  "Скрізь: біти ПОЗА вікном лишаються недоторканими. У цьому весь сенс маски.",
                  size=12.5, color=INK, bold=True))
    out("mask-ops.svg", W, H, *f,
        title="Чотири дії з бітом через маску: встановити · скинути · перевірити · перемкнути")


# ════════════════ 4. Логічний vs арифметичний зсув праворуч ══════════════════
def fig_shift_signed():
    W, H = 900, 470
    f = []
    cell = 38
    gap = 2

    # 248 = 1111 1000; як беззнакове >>1 → 124; як знакове (−8) >>1 → −4
    src = [1, 1, 1, 1, 1, 0, 0, 0]
    uns = [0, 1, 1, 1, 1, 1, 0, 0]   # 248 >> 1 = 124 (нулі зверху)
    sgn = [1, 1, 1, 1, 1, 1, 0, 0]   # −8 >> 1 = −4 (копія знаку зверху)

    colw = 8 * (cell + gap)
    xL = 60
    xR = 480

    def block(x0, head, headcol, res, filler_val, filler_is_zero, cap):
        g = []
        g.append(textbox(x0 + colw / 2, 66, head, size=13, pad=8,
                         fill="#fafafa", stroke=headcol, color=headcol, bold=True)[0])
        # вхід
        g.append(mono(x0 - 12, 118, "x", size=14, color=INK, anchor="end", bold=True))
        g.append(bitrow(x0, 100, src, cell, gap))
        # стрілки праворуч на 1
        for i in range(8):
            cx = x0 + i * (cell + gap) + cell / 2
            g.append(arrow(cx, 100 + cell + 16, cx + (cell + gap), 100 + cell + 16,
                          color=headcol, sw=1.7))
        g.append(text(x0 + colw / 2, 100 + cell + 40, ">> 1  (усі біти на 1 праворуч)",
                     size=11, color=headcol, bold=True))
        # результат
        yr = 100 + cell + 56
        g.append(mono(x0 - 12, yr + 26, "=", size=14, color=INK, anchor="end", bold=True))
        for i, v in enumerate(res):
            cx = x0 + i * (cell + gap)
            if i == 0:  # верхній розряд, що набіг
                fb = GREEN_BG if filler_is_zero else AMBER_BG
                fs = FIELD if filler_is_zero else AMBER
                g.append(rect(cx, yr, cell, cell, fill=fb, stroke=fs, sw=2.2, rx=5))
                g.append(text(cx + cell / 2, yr + cell * 0.68, str(filler_val),
                             size=15, color=fs, bold=True))
            else:
                g.append(bitcell(cx, yr, v, cell))
        g.append(text(x0 + colw / 2, yr + cell + 22, cap, size=12, color=INK, bold=True))
        return g

    f += block(xL, "БЕЗЗНАКОВЕ: 248", NEG,
               uns, 0, True, "зверху набіг НУЛЬ → 124  (÷2)")
    f += block(xR, "ЗНАКОВЕ: −8", POS,
               sgn, 1, False, "зверху набігла КОПІЯ ЗНАКУ → −4")
    # спільний вхід-підпис
    f.append(text(W / 2, 96, "той самий бітовий візерунок 1111 1000",
                  size=11, color=MUTED, bold=True))
    # висновок
    f.append(rect(40, H - 46, W - 80, 32, fill=RED_BG, stroke=POS, sw=1.4, rx=8))
    f.append(text(W / 2, H - 25,
                  "Якби для −8 набіг нуль, вийшло б +124 — знак загубився б. Механізм вибирає ТИП операнда.",
                  size=12, color=INK, bold=True))
    out("shift-signed.svg", W, H, *f,
        title="Один >> — два механізми: логічний (беззнакове) проти арифметичного (знакове)")


# ════════════════ 5. Запис багатобітового поля (read-modify-write) ════════════
def fig_field_write():
    W, H = 900, 470
    f = []
    cell = 40
    gap = 3
    x0 = 250

    # поле — біти 4..6 (індекси масиву 1,2,3). Приклад: старе=010, нове=101 (5)
    reg0 = [1, 0, 1, 0, 1, 1, 0, 1]   # чужі біти + старе поле (біти6..4 = 0,1,0)
    invm = [1, 0, 0, 0, 1, 1, 1, 1]   # ~DIV_MASK: 0 лише на бітах 4..6
    cleared = [1, 0, 0, 0, 0, 1, 0, 1]  # після &= ~MASK
    val_sh = [0, 1, 0, 1, 0, 0, 0, 0]  # 5<<4 = біти6..4 = 1,0,1
    final = [1, 1, 0, 1, 0, 1, 0, 1]   # після |= : поле=101

    def is_field(i): return i in (1, 2, 3)  # біти 6,5,4

    def row(y, bits, lab, labcol=INK, hi=True, faded_zero=False):
        g = [mono(x0 - 14, y + cell * 0.66, lab, size=12.5, color=labcol, anchor="end", bold=True)]
        for i, v in enumerate(bits):
            cx = x0 + i * (cell + gap)
            inf = is_field(i)
            if hi and inf:
                bc = POS if v else NEG
                bg = RED_BG if v else BLUE_BG
                g.append(rect(cx, y, cell, cell, fill=bg, stroke=AMBER, sw=2.6, rx=5))
                g.append(text(cx + cell / 2, y + cell * 0.68, str(v), size=15, color=bc, bold=True))
            else:
                if faded_zero and v == 0 and not inf:
                    g.append(rect(cx, y, cell, cell, fill="#f0f0f0", stroke="#cfcfcf", sw=1.0, rx=5))
                    g.append(text(cx + cell / 2, y + cell * 0.68, "0", size=14, color=MUTED))
                else:
                    g.append(bitcell(cx, y, v, cell))
        return g

    # шапка з номерами розрядів
    f.append(text(x0 + 4 * (cell + gap), 44, "розряди 7 … 0  (поле = біти 4–6)",
                  size=11, color=MUTED, bold=True))
    for i in range(8):
        cx = x0 + i * (cell + gap) + cell / 2
        f.append(mono(cx, 60, str(7 - i), size=10, color=MUTED, anchor="middle"))

    y0 = 70
    dy = 92
    # 1
    f += row(y0, reg0, "reg", INK, hi=True)
    f.append(text(x0 + 8 * (cell + gap) + 20, y0 + cell * 0.66,
                  "1. поточне (поле = 010)", size=11.5, color=INK, anchor="start"))
    # операція &= ~MASK
    f.append(mono(x0 + 8 * (cell + gap) + 20, y0 + dy - 16, "&= ~DIV_MASK", size=11,
                  color=NEG, anchor="start", bold=True))
    # 2 cleared
    f += row(y0 + dy, cleared, "→", NEG, hi=True, faded_zero=False)
    f.append(text(x0 + 8 * (cell + gap) + 20, y0 + dy + cell * 0.66,
                  "2. поле очищене в 000", size=11.5, color=NEG, anchor="start"))
    # операція |= val<<pos
    f.append(mono(x0 + 8 * (cell + gap) + 20, y0 + 2 * dy - 16, "|= 5 << 4", size=11,
                  color=POS, anchor="start", bold=True))
    # 3 final
    f += row(y0 + 2 * dy, final, "→", POS, hi=True)
    f.append(text(x0 + 8 * (cell + gap) + 20, y0 + 2 * dy + cell * 0.66,
                  "3. вкладено 101 (=5)", size=11.5, color=POS, anchor="start"))

    f.append(rect(40, H - 46, W - 80, 32, fill=GREEN_BG, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(W / 2, H - 25,
                  "Чужі біти (поза жовтою рамкою) недоторкані на всіх трьох кроках. Пропустиш крок 2 — нове змішається зі старим.",
                  size=11.5, color=INK, bold=True))
    out("field-write.svg", W, H, *f,
        title="Запис поля (read-modify-write): прочитати → очистити маскою → вкласти зсунуте")


# ════════════════ 6. x & (x−1) гасить наймолодший одиничний біт ══════════════
def fig_lowest_bit():
    W, H = 820, 420
    f = []
    cell = 44
    gap = 3
    x0 = 250

    x = [0, 1, 0, 1, 1, 0, 0, 0]     # наймолодша 1 у розряді 3
    xm1 = [0, 1, 0, 1, 0, 1, 1, 1]   # x−1
    res = [0, 1, 0, 1, 0, 0, 0, 0]   # x & (x−1)
    lowest = 4  # індекс масиву наймолодшої одиниці (розряд 3)

    def row(y, bits, lab, mark_from=None, col=INK):
        g = [mono(x0 - 14, y + cell * 0.66, lab, size=13, color=col, anchor="end", bold=True)]
        for i, v in enumerate(bits):
            cx = x0 + i * (cell + gap)
            # підсвітити «зону змін» (наймолодша 1 і нижче)
            zone = (mark_from is not None and i >= mark_from)
            bc = POS if v else NEG
            bg = RED_BG if v else BLUE_BG
            sw = 2.6 if zone else 1.8
            stk = AMBER if zone else bc
            g.append(rect(cx, y, cell, cell, fill=bg, stroke=stk, sw=sw, rx=5))
            g.append(text(cx + cell / 2, y + cell * 0.68, str(v), size=15,
                          color=bc, bold=zone))
        return g

    # шапка розрядів
    for i in range(8):
        cx = x0 + i * (cell + gap) + cell / 2
        f.append(mono(cx, 56, str(7 - i), size=10, color=MUTED, anchor="middle"))
    f.append(text(x0 + 4 * (cell + gap), 44, "розряди 7 … 0", size=11, color=MUTED, bold=True))

    y0 = 66
    dy = 84
    f += row(y0, x, "x", mark_from=lowest)
    f.append(text(x0 + 8 * (cell + gap) + 16, y0 + cell * 0.66,
                  "наймолодша 1 — розряд 3", size=11, color=INK, anchor="start"))

    f.append(mono(x0 - 14, y0 + dy - 12, "− 1", size=12, color=MUTED, anchor="end", bold=True))
    f += row(y0 + dy, xm1, "x−1", mark_from=lowest, col=NEG)
    f.append(text(x0 + 8 * (cell + gap) + 16, y0 + dy + cell * 0.66,
                  "позика: 1→0, нулі під нею → 1", size=11, color=NEG, anchor="start"))

    f.append(line(x0 - 30, y0 + 2 * dy - 14, x0 + 8 * (cell + gap) - gap, y0 + 2 * dy - 14,
                  color=INK, sw=1.6))
    f.append(mono(x0 - 30, y0 + 2 * dy - 18, "&", size=15, color=FIELD, anchor="start", bold=True))
    f += row(y0 + 2 * dy, res, "=", mark_from=lowest, col=FIELD)
    f.append(text(x0 + 8 * (cell + gap) + 16, y0 + 2 * dy + cell * 0.66,
                  "наймолодша 1 згасла ✓", size=11, color=FIELD, anchor="start"))

    f.append(rect(30, H - 44, W - 60, 30, fill=AMBER_BG, stroke=AMBER, sw=1.4, rx=8))
    f.append(text(W / 2, H - 24,
                  "Вище наймолодшої 1 біти збігаються (позика не дійшла) → лишаються; на ній і нижче протилежні → нулі.",
                  size=11.5, color=INK, bold=True))
    out("lowest-bit.svg", W, H, *f,
        title="x & (x−1): віднімання й позика гасять наймолодший одиничний біт")


# ════════════════ 7. SWAR-підрахунок: дерево часткових сум ════════════════════
def fig_swar_tree():
    """Паралельний popcount на 16-бітному прикладі: суми в 2-, 4-, 8-бітних полях."""
    W, H = 940, 560
    f = []
    cell = 34
    gap = 2
    x0 = 70
    N = 16

    # приклад: 1011 0100 1110 0010  → 8 одиниць
    bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0]

    def rowbits(y, vals, lab, labcol=INK):
        g = [mono(x0 - 12, y + cell * 0.66, lab, size=12, color=labcol, anchor="end", bold=True)]
        g += [bitcell(x0 + i * (cell + gap), y, v, cell) for i, v in enumerate(vals)]
        return g

    # рядок «полів»: у кожному полі шириною fw — число (сума), фон зелений
    def rowfields(y, counts, fw, lab, note):
        g = [mono(x0 - 12, y + cell * 0.66, lab, size=12, color=FIELD, anchor="end", bold=True)]
        step = fw * (cell + gap)
        for i, c in enumerate(counts):
            fx = x0 + i * step
            fwpx = fw * cell + (fw - 1) * gap
            g.append(rect(fx, y, fwpx, cell, fill=GREEN_BG, stroke=FIELD, sw=2, rx=5))
            g.append(text(fx + fwpx / 2, y + cell * 0.68, str(c), size=15, color=FIELD, bold=True))
        g.append(text(x0 + N * (cell + gap) + 12, y + cell * 0.66, note,
                      size=11, color=MUTED, anchor="start"))
        return g

    # шапка розрядів (15…0)
    for i in range(N):
        cx = x0 + i * (cell + gap) + cell / 2
        f.append(mono(cx, 52, str(N - 1 - i), size=9, color=MUTED, anchor="middle"))

    y = 60
    dy = 78
    f += rowbits(y, bits, "x")
    f.append(text(x0 + N * (cell + gap) + 12, y + cell * 0.66,
                  "16 сирих бітів — треба порахувати одиниці", size=11, color=MUTED, anchor="start"))

    # 2-бітні поля: суми пар (0,1,2)
    y += dy
    c2 = [sum(bits[2 * i:2 * i + 2]) for i in range(N // 2)]
    f += rowfields(y, c2, 2, "2-біт", "кожна ПАРА → своя кількість одиниць (0…2)")

    # 4-бітні поля
    y += dy
    c4 = [c2[2 * i] + c2[2 * i + 1] for i in range(N // 4)]
    f += rowfields(y, c4, 4, "4-біт", "сусідні пари складено → кількість у кожній четвірці")

    # 8-бітні поля (байти)
    y += dy
    c8 = [c4[2 * i] + c4[2 * i + 1] for i in range(N // 8)]
    f += rowfields(y, c8, 8, "8-біт", "четвірки складено → кількість у кожному байті")

    # разом
    y += dy
    total = c8[0] + c8[1]
    fwpx = N * cell + (N - 1) * gap
    f.append(rect(x0, y, fwpx, cell, fill="#d9f0e2", stroke=FIELD, sw=2.6, rx=6))
    f.append(text(x0 + fwpx / 2, y + cell * 0.68, "разом: %d" % total, size=16, color=FIELD, bold=True))
    f.append(mono(x0 - 12, y + cell * 0.66, "16-біт", size=12, color=FIELD, anchor="end", bold=True))

    # висновок
    f.append(rect(30, H - 46, W - 60, 32, fill=AMBER_BG, stroke=AMBER, sw=1.4, rx=8))
    f.append(text(W / 2, H - 25,
                  "log₂16 = 4 кроки замість 16: на кожному сусідні поля складаються ВОДНОРАЗ по всьому слову.",
                  size=12, color=INK, bold=True))
    out("swar-tree.svg", W, H, *f,
        title="SWAR-підрахунок: дерево часткових сум подвоює ширину поля щокроку")


# ════════════════ 8. Обертання бітів паралельними обмінами ════════════════════
def fig_bit_reverse():
    """Дзеркалення 8 бітів: обмін сусідів → пар → четвірок, log-кроки."""
    W, H = 880, 540
    f = []
    cell = 46
    gap = 4
    x0 = 210

    start = [1, 1, 0, 1, 0, 0, 1, 0]   # вихідне (біт 7 … 0)
    # крок 1: обмін сусідніх одиничних бітів
    s1 = [1, 1, 1, 0, 0, 0, 0, 1]
    # крок 2: обмін сусідніх пар
    s2 = [1, 0, 1, 1, 0, 1, 0, 0]
    # крок 3: обмін половин (по 4)
    s3 = [0, 1, 0, 0, 1, 0, 1, 1]      # = дзеркало start

    def row(y, vals, lab, labcol=INK, groups=None, gcol=FIELD):
        g = [mono(x0 - 14, y + cell * 0.66, lab, size=12, color=labcol, anchor="end", bold=True)]
        g += [bitcell(x0 + i * (cell + gap), y, v, cell) for i, v in enumerate(vals)]
        # дужки над групами, що обмінюються
        if groups:
            for a, b in groups:
                xa = x0 + a * (cell + gap)
                xb = x0 + (b + 1) * (cell + gap) - gap
                yb = y - 10
                g.append(line(xa + 2, yb, xb - 2, yb, color=gcol, sw=2))
                g.append(line(xa + 2, yb, xa + 2, yb + 6, color=gcol, sw=2))
                g.append(line(xb - 2, yb, xb - 2, yb + 6, color=gcol, sw=2))
        return g

    def swaparrows(y, pairs, col=NEG):
        """Криві-обміни між сусідніми групами (двоспрямовані)."""
        g = []
        for (ac, bc) in pairs:
            g.append(arrow(ac, y, bc, y, color=col, sw=1.6))
            g.append(arrow(bc, y + 8, ac, y + 8, color=col, sw=1.6))
        return g

    # шапка розрядів
    for i in range(8):
        cx = x0 + i * (cell + gap) + cell / 2
        f.append(mono(cx, 52, str(7 - i), size=10, color=MUTED, anchor="middle"))

    y = 62
    dy = 108
    # вихід — групуємо по одному біту (пари сусідів)
    grp1 = [(0, 1), (2, 3), (4, 5), (6, 7)]
    f += row(y, start, "x", groups=grp1, gcol=NEG)
    f.append(text(x0 + 8 * (cell + gap) + 14, y + cell * 0.66,
                  "обмін СУСІДНІХ бітів (◄─►)", size=11, color=NEG, anchor="start"))

    y += dy
    grp2 = [(0, 1), (2, 3), (4, 5), (6, 7)]  # пари над s1 → обмін пар
    f += row(y, s1, "1×", labcol=FIELD, groups=grp2, gcol=POS)
    f.append(text(x0 + 8 * (cell + gap) + 14, y + cell * 0.66,
                  "обмін СУСІДНІХ ПАР (по 2)", size=11, color=POS, anchor="start"))

    y += dy
    grp3 = [(0, 3), (4, 7)]  # дві половини по 4
    f += row(y, s2, "2×", labcol=FIELD, groups=grp3, gcol=NEG)
    f.append(text(x0 + 8 * (cell + gap) + 14, y + cell * 0.66,
                  "обмін ПОЛОВИН (по 4)", size=11, color=NEG, anchor="start"))

    y += dy
    f += row(y, s3, "4×", labcol=FIELD)
    f.append(text(x0 + 8 * (cell + gap) + 14, y + cell * 0.66,
                  "= повне дзеркало ✓", size=11.5, color=FIELD, anchor="start", bold=True))

    f.append(rect(30, H - 44, W - 60, 30, fill=AMBER_BG, stroke=AMBER, sw=1.4, rx=8))
    f.append(text(W / 2, H - 24,
                  "3 = log₂8 кроки: щоразу міняємо місцями вдвічі більші блоки. Для 32 бітів — 5 кроків.",
                  size=12, color=INK, bold=True))
    out("bit-reverse.svg", W, H, *f,
        title="Дзеркалення бітів: обмін блоків, що подвоюються (сусіди → пари → половини)")


if __name__ == "__main__":
    fig_logic_ops()
    fig_shifts()
    fig_mask_ops()
    fig_shift_signed()
    fig_field_write()
    fig_lowest_bit()
    fig_swar_tree()
    fig_bit_reverse()
    print("OK: 6 фігур у", IMG)
