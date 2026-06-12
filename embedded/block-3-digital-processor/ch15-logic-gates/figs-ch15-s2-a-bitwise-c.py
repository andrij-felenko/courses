# -*- coding: utf-8 -*-
"""
Фігури до ⚙️-вставки §3.2.2a — «Бітові операції в C: маски, set/clear/toggle».
Окремий скрипт (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; «1»/істина червоний, «0»/хибність синій;
зелене — результат/висновок; шрифт sans-serif. Нумерація підписів — за темою-вставкою:
«Рис. 3.2.2a.k». Імена SVG-файлів містять суфікс s2a, щоб не змішуватися з рисунками тем.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (єдина з figs.py розділу) ───────────────────────────────────────
RED   = "#c0271e"   # «1» / істина / high
BLUE  = "#1f47b5"   # «0» / хибність / low
GREEN = "#1f8a3b"   # результат / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
MONO  = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="bInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="bGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = "bGreen" if color == GREEN else "bInk"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: рядок із 8 бітів (клітинки), старший біт ліворуч ──────────────
def bit_row(x, y, bits, cell=30, gap=4, label=None, label_col=INK,
            hi=RED, lo=BLUE, faint_lo=False, mark=None):
    """bits — список 0/1 (8 шт., MSB перший). mark — множина індексів (0..7,
    зліва направо), які підсвітити рамкою (наприклад біти маски)."""
    out = ""
    if label is not None:
        out += text(x - 12, y + cell * 0.66, label, 13.5, label_col, "end", "bold", mono=True)
    for i, b in enumerate(bits):
        cx = x + i * (cell + gap)
        if b == 1:
            fill, col = "#fbeceb", hi
        else:
            fill, col = ("#f4f7fb" if not faint_lo else "#fafafa"), (lo if not faint_lo else GREY)
        out += rect(cx, y, cell, cell, fill, FAINT, 1.4, 4)
        out += text(cx + cell / 2, y + cell * 0.7, str(b), 16, col, "middle", "bold", mono=True)
        if mark and i in mark:
            out += rect(cx - 1.5, y - 1.5, cell + 3, cell + 3, "none", AMBER, 2.4, 5)
    return out


def op_glyph(x, y, sym, color=INK):
    """Велика моноширинна позначка операції (&, |, ^, ~) ліворуч від рядка."""
    return text(x, y, sym, 26, color, "middle", "bold", mono=True)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2a.1 — чотири бітові оператори C = масив вентилів §3.2.1–3.2.4,
# що працює над усіма 8 бітами слова РАЗОМ (порозрядно, паралельно).
# ════════════════════════════════════════════════════════════════════════════
def fig_operators():
    W, H = 920, 620
    s = header(W, H)
    s += text(W / 2, 34, "Бітові оператори C — це вентилі §3.2, прикладені до КОЖНОГО біта слова",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "один оператор = той самий вентиль над усіма 8 розрядами ВОДНОЧАС (порозрядно, паралельно)",
              12, GREY, "middle", style="italic")

    A = [1, 0, 1, 1, 0, 0, 1, 0]   # 0xB2
    B = [0, 1, 1, 0, 1, 0, 1, 1]   # 0x6B
    x0 = 250
    cell = 30
    roww = 8 * (cell + 4) - 4

    def panel(oy, sym, op_col, gate, fn, note, binary=True):
        nonlocal s
        # позначка операції — зліва, на рівні рядка B (між операндами)
        glyph_y = oy + (40 if binary else 16)
        s += op_glyph(x0 - 56, glyph_y + 9, sym, op_col)
        s += text(x0 - 56, glyph_y - 16, gate, 11, op_col, "middle", "bold")
        s += bit_row(x0, oy, A, cell, 4, "A")
        if binary:
            s += bit_row(x0, oy + 40, B, cell, 4, "B")
            r = [fn(a, b) for a, b in zip(A, B)]
            ry = oy + 80
        else:
            r = [1 - a for a in A]
            s += text(x0 + roww + 16, oy + cell * 0.7, "(другий операнд не потрібен)",
                      11, GREY, "start", style="italic")
            ry = oy + 40
        s += line(x0 - 18, ry - 8, x0 + roww, ry - 8, INK, 1.4)
        s += bit_row(x0, ry, r, cell, 4, "=", hi=GREEN, lo=GREY)
        s += text(x0 + roww + 16, ry + cell * 0.7, note, 11.5, INK, "start", "bold")

    panel(92,  "&", BLUE,  "AND", lambda a, b: a & b, "лишає 1, де B=1 і A=1  → «стирає/маскує»")
    panel(232, "|", RED,   "OR",  lambda a, b: a | b, "ставить 1, де B=1       → «вмикає»")
    panel(372, "^", GREEN, "XOR", lambda a, b: a ^ b, "перевертає, де B=1      → «перемикає»")
    panel(512, "~", AMBER, "NOT", None, "перевертає ВСІ біти     → доповнення", binary=False)

    s += rect(60, 588, W - 120, 26, "#f4f7f4", GREEN, 1.4, 8)
    s += text(W / 2, 606, "Кожен стовпчик рахується незалежно — це і є «вентиль над усім словом одним махом».",
              12, INK, "middle", "bold")
    save("fig-15-s2a-1-operators.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2a.2 — три ідіоми над одним байтом: SET (|=), CLEAR (&= ~), TOGGLE (^=).
# Маска чіпає лише позначені (бурштинові) біти; решта НЕ змінюється.
# ════════════════════════════════════════════════════════════════════════════
def fig_idioms():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Три ідіоми над одним байтом: SET · CLEAR · TOGGLE",
              20, INK, "middle", "bold")
    s += text(W / 2, 54, "маска має 1 у потрібних розрядах (бурштин); біти поза маскою у ВСІХ трьох ідіом не змінюються",
              11.5, GREY, "middle", style="italic")

    reg  = [1, 0, 0, 1, 0, 1, 0, 0]
    mask = [0, 0, 1, 0, 0, 0, 1, 0]      # біти 2 і 6 (зліва направо)
    marks = {i for i, m in enumerate(mask) if m == 1}
    cell = 22
    gap = 3
    roww = 8 * (cell + gap) - gap

    def col(cx, title, code, op, result, tcol):
        nonlocal s
        s += rect(cx - 14, 86, roww + 28, 330, "none", FAINT, 1.4, 10)
        s += text(cx + roww / 2, 108, title, 13.5, tcol, "middle", "bold")
        s += text(cx + roww / 2, 128, code, 12.5, tcol, "middle", "bold", mono=True)
        s += bit_row(cx, 150, reg, cell, gap, "reg")
        s += op_glyph(cx - 30, 150 + 78, op, tcol)
        marker_hi = {"|": RED, "&": BLUE, "^": GREEN}[op]
        # для CLEAR показуємо ~mask
        if op == "&":
            shown = [1 - m for m in mask]
            mlabel = "~mask"
            s += bit_row(cx, 192, shown, cell, gap, mlabel, mark=marks, hi=GREY, lo=AMBER, faint_lo=False)
        else:
            s += bit_row(cx, 192, mask, cell, gap, "mask", mark=marks, hi=AMBER, lo=GREY, faint_lo=True)
        s += line(cx - 16, 192 + cell + 7, cx + roww, 192 + cell + 7, INK, 1.4)
        s += bit_row(cx, 192 + cell + 14, result, cell, gap, "→", mark=marks, hi=GREEN, lo=BLUE)
        s += text(cx + roww / 2, 192 + cell + 14 + cell + 22, _effect(op), 11, INK, "middle", "bold")

    def _effect(op):
        return {"|": "1 у позначених, решта як була",
                "&": "0 у позначених, решта як була",
                "^": "перевернуті позначені, решта як була"}[op]

    setr = [r | m for r, m in zip(reg, mask)]
    clrr = [r & (1 - m) for r, m in zip(reg, mask)]
    togr = [r ^ m for r, m in zip(reg, mask)]
    col(70,  "SET (увімкнути)",  "reg |= mask",  "|", setr, RED)
    col(390, "CLEAR (вимкнути)", "reg &= ~mask", "&", clrr, BLUE)
    col(710, "TOGGLE (перемкнути)", "reg ^= mask", "^", togr, GREEN)

    s += text(W / 2, 448, "Скрізь працює пара §3.2: вентиль обирає ДІЮ, маска обирає, НАД ЯКИМИ бітами її виконати.",
              12, INK, "middle", "bold")
    save("fig-15-s2a-2-idioms.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2a.3 — побудова маски зсувом (1u << n) і читання біта (& mask).
# ════════════════════════════════════════════════════════════════════════════
def fig_mask_shift():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Звідки береться маска: зсув 1u << n — і як ПРОЧИТАТИ біт",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "одиниця, зсунута на n позицій, дає маску «лише біт n»; AND із нею перевіряє цей біт",
              11.5, GREY, "middle", style="italic")

    cell = 30
    x0 = 250
    roww = 8 * (cell + 4) - 4
    # верх: будуємо 1u<<3
    one = [0, 0, 0, 0, 0, 0, 0, 1]
    m3  = [0, 0, 0, 0, 1, 0, 0, 0]   # біт 3 → індекс 4 зліва (бо MSB ліворуч)
    s += text(x0 - 18, 92, "крок 1 — побудувати маску одного біта", 13, INK, "start", "bold")
    s += bit_row(x0, 104, one, cell, 4, "1u")
    s += arrow(x0 + roww / 2, 138, x0 + roww / 2, 158, INK, 2)
    s += text(x0 + roww / 2 + 12, 152, "<< 3  (зсув уліво на 3)", 12, AMBER, "start", "bold", mono=True)
    s += bit_row(x0, 160, m3, cell, 4, "1u<<3", mark={4}, hi=AMBER, lo=GREY, faint_lo=True)
    s += text(x0 + roww + 16, 160 + cell * 0.7, "= маска «біт 3»", 12, INK, "start", "bold")

    # низ: читання біта  (reg & (1u<<3)) != 0
    reg = [1, 0, 1, 1, 1, 0, 0, 1]
    s += text(x0 - 18, 250, "крок 2 — прочитати біт 3 регістра", 13, INK, "start", "bold")
    s += bit_row(x0, 262, reg, cell, 4, "reg")
    s += op_glyph(x0 - 30, 262 + 78, "&", BLUE)
    s += bit_row(x0, 300, m3, cell, 4, "mask", mark={4}, hi=AMBER, lo=GREY, faint_lo=True)
    s += line(x0 - 16, 300 + cell + 7, x0 + roww, 300 + cell + 7, INK, 1.4)
    res = [r & m for r, m in zip(reg, m3)]
    s += bit_row(x0, 300 + cell + 14, res, cell, 4, "=", mark={4}, hi=GREEN, lo=BLUE)
    s += text(x0 + roww + 16, 300 + cell + 14 + cell * 0.7,
              "≠ 0  →  біт 3 = 1", 12.5, GREEN, "start", "bold")

    s += text(W / 2, 416, "Перевірка «чи стоїть біт»: (reg & (1u<<n)) — ненульове, якщо біт n увімкнено.",
              12, INK, "middle", "bold")
    save("fig-15-s2a-3-mask-shift.svg", s)


if __name__ == "__main__":
    fig_operators()
    fig_idioms()
    fig_mask_shift()
    print("ch15-s2a (bitwise-c) figures done.")
