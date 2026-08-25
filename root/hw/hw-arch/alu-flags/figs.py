# -*- coding: utf-8 -*-
"""Фігури до теми «Прапорці АЛП» (Z, N, C, V).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas','DejaVu Sans Mono',monospace"


def mono(x, y, s, size=15, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s xml:space="preserve">%s</text>'
            % (x, y, MONO, size, color, anchor, w, esc(s)))


def fig_four():
    """Чотири прапорці, зчитані з ОДНОГО додавання. Приклад беззнакового
    переповнення: 200 + 100 у 8 бітах. Видно, звідки береться кожен біт."""
    W, H = 720, 400
    f = [text(W / 2, 30, "Одне додавання — чотири прапорці", size=17, bold=True)]

    # Стовпчик обчислення (8 біт), моноширинний
    x0, y = 60, 78
    box_w = 380
    f.append(rect(x0 - 16, y - 26, box_w, 150, fill="#f7f9fc", stroke=LINE, sw=1.3))
    lines = [
        ("  1100 1000     200", INK),
        ("+ 0110 0100   + 100", INK),
        ("  ─────────", MUTED),
        ("1 0010 1100     300 ?", POS),
    ]
    for s, c in lines:
        f.append(mono(x0, y, s, size=16, color=c))
        y += 26
    f.append(mono(x0, y + 6, "перенос-вихід = 1     старший біт = 0", size=12, color=MUTED))

    # Чотири прапорці праворуч, кожен зі стрілкою-поясненням
    bx = 500
    f.append(text(bx + 60, 64, "прапорці", size=14, bold=True))
    flags = [
        ("Z", "0", "результат ≠ 0", NEG),
        ("N", "0", "старший біт = 0", NEG),
        ("C", "1", "перенос вийшов за 8 біт", POS),
        ("V", "0", "знаки однакові → нема", MUTED),
    ]
    yy = 92
    for name, val, why, col in flags:
        f.append(circle(bx, yy + 12, 16, fill="#ffffff", stroke=col, sw=2))
        f.append(text(bx, yy + 18, name, size=16, bold=True, color=col))
        f.append(text(bx + 28, yy + 8, "= " + val, size=15, bold=True, anchor="start"))
        f.append(text(bx + 28, yy + 25, why, size=11, color=MUTED, anchor="start"))
        yy += 62
    f.append(text(W / 2, H - 16,
                  "суматор порахував число; прапорці лише дивляться на нього й на перенос",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'alu-flags-four.svg'), W, H, *f)


def fig_cv():
    """C проти V: ті самі 8 бітів — два тлумачення. 200+100 переповнює
    беззнакове (C=1), але НЕ знакове; −100 + −50 навпаки — переповнює знакове (V=1)."""
    W, H = 720, 360
    f = [text(W / 2, 30, "Одні біти — два тлумачення: C стежить за беззнаковим, V за знаковим",
              size=15, bold=True)]

    # Ліва панель — беззнакове переповнення
    lx = 40
    f.append(rect(lx, 58, 310, 258, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(lx + 155, 82, "200 + 100", size=14, bold=True, color=POS))
    ml = [
        "  1100 1000   беззн. 200 / знак. −56",
        "+ 0110 0100   беззн. 100 / знак. +100",
        "  ─────────",
        "1 0010 1100   беззн. 300✗ / знак. +44✓",
    ]
    yy = 112
    for s in ml:
        f.append(mono(lx + 18, yy, s, size=12))
        yy += 24
    f.append(rect(lx + 18, yy - 4, 274, 74, fill="#ffffff", stroke=POS, sw=1.2))
    f.append(text(lx + 30, yy + 18, "C = 1  (беззнакове не влізло)", size=13, bold=True,
                  color=POS, anchor="start"))
    f.append(text(lx + 30, yy + 40, "V = 0  (знаки доданків різні —", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(lx + 44, yy + 56, "знакове переповнення неможливе)", size=12,
                  color=MUTED, anchor="start"))

    # Права панель — знакове переповнення
    rx = 380
    f.append(rect(rx, 58, 310, 258, fill="#eef4ff", stroke=NEG, sw=1.6))
    f.append(text(rx + 155, 82, "(−100) + (−50)", size=14, bold=True, color=NEG))
    mr = [
        "  1001 1100   беззн. 156 / знак. −100",
        "+ 1100 1110   беззн. 206 / знак.  −50",
        "  ─────────",
        "1 0110 1010   беззн. 362✗ / знак. +106✗",
    ]
    yy = 112
    for s in mr:
        f.append(mono(rx + 18, yy, s, size=12))
        yy += 24
    f.append(rect(rx + 18, yy - 4, 274, 74, fill="#ffffff", stroke=NEG, sw=1.2))
    f.append(text(rx + 30, yy + 18, "V = 1  (−150 не влазить у −128…127)", size=12,
                  bold=True, color=NEG, anchor="start"))
    f.append(text(rx + 30, yy + 40, "знак стрибнув з '−' на '+' —", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(rx + 44, yy + 56, "явна ознака знакового переповнення", size=12,
                  color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'alu-flags-cv.svg'), W, H, *f)


def fig_branch():
    """Як умовний перехід читає прапорці: після A − B кожне порівняння —
    це проста комбінація Z, N, V, C. Дві колонки: знакове й беззнакове."""
    W, H = 720, 380
    f = [text(W / 2, 30, "Порівняння = відняти й глянути на прапорці", size=17, bold=True)]
    f.append(text(W / 2, 54, "процесор рахує A − B, потім читає комбінацію бітів",
                  size=12, color=MUTED, italic=True))

    def column(x0, title, accent, fill, rows):
        col = [text(x0 + 150, 88, title, size=14, bold=True, color=accent)]
        y = 108
        for cond, expr in rows:
            col.append(rect(x0, y, 300, 40, fill=fill, stroke=accent, sw=1.3))
            col.append(text(x0 + 16, y + 25, cond, size=14, bold=True, anchor="start"))
            col.append(mono(x0 + 300 - 16, y + 25, expr, size=14, anchor="end"))
            y += 50
        return col

    rows_common = [
        ("A = B", "Z = 1"),
        ("A ≠ B", "Z = 0"),
    ]
    rows_signed = rows_common + [
        ("A < B  (знак.)", "N ≠ V"),
        ("A ≥ B  (знак.)", "N = V"),
    ]
    rows_unsigned = rows_common + [
        ("A < B  (беззн.)", "C = 0"),
        ("A ≥ B  (беззн.)", "C = 1"),
    ]
    f += column(40, "знакове тлумачення", NEG, "#eef4ff", rows_signed)
    f += column(380, "беззнакове тлумачення", POS, "#fdecea", rows_unsigned)

    f.append(text(W / 2, H - 14,
                  "ті самі біти результату — різні прапорці, бо '<' для знакових і беззнакових різне",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'alu-flags-branch.svg'), W, H, *f)


# ── Фігури для вставки math-flag-conditions ─────────────────────────────────

def fig_math_carry_xor():
    """Старший біт як шлюз між cₙ₋₁ (перенос, що заходить) і cₙ (що виходить):
    коли ваги збігаються — знак чесний; коли різні — знак ламається, V=1."""
    W, H = 760, 470
    f = [text(W / 2, 30, "Старший біт: перенос увійшов проти переносу вийшов", size=16, bold=True)]

    top = 78
    lx, ly, lw, lh = 60, top, 300, 88
    f.append(rect(lx, ly, lw, lh, fill="#eef2f7"))
    f.append(text(lx + lw / 2, ly + 34, "молодші n−1 розрядів", size=14, bold=True))
    f.append(mono(lx + lw / 2, ly + 62, "Aₗ+Bₗ+c₀ = Rₗ + cₙ₋₁·2ⁿ⁻¹", size=12, color=MUTED, anchor="middle"))

    sx, sw2 = 470, 180
    f.append(rect(sx, ly, sw2, lh, fill="#fdf3e6", stroke=POS, sw=2))
    f.append(text(sx + sw2 / 2, ly + 34, "старший біт", size=14, bold=True, color=POS))
    f.append(mono(sx + sw2 / 2, ly + 62, "aₛ+bₛ+cₙ₋₁", size=13, color=MUTED, anchor="middle"))

    f.append(arrow(lx + lw + 6, ly + lh / 2, sx - 6, ly + lh / 2, color=NEG, sw=2.4))
    f.append(text((lx + lw + sx) / 2, ly + lh / 2 - 12, "cₙ₋₁", size=15, bold=True, color=NEG))
    f.append(text((lx + lw + sx) / 2, ly + lh / 2 + 24, "тиск знизу", size=11, color=MUTED))

    f.append(arrow(sx + sw2 + 6, ly + lh / 2, sx + sw2 + 92, ly + lh / 2, color=POS, sw=2.4))
    f.append(text(sx + sw2 + 50, ly + lh / 2 - 12, "cₙ", size=15, bold=True, color=POS))
    f.append(text(sx + sw2 + 50, ly + lh / 2 + 24, "(= C)", size=11, color=MUTED))

    cases = [("0", "0"), ("1", "1"), ("1", "0"), ("0", "1")]
    by = 258
    cw, gap = 158, 24
    total = len(cases) * cw + (len(cases) - 1) * gap
    x0 = (W - total) / 2
    f.append(text(W / 2, by - 16, "усі чотири стани старшого розряду", size=14, bold=True))
    for cin, cout in cases:
        x = x0
        x0 += cw + gap
        same = (cin == cout)
        col = FIELD if same else POS
        f.append(rect(x, by, cw, 152, fill=FILL, stroke=col, sw=2))
        f.append(mono(x + cw / 2, by + 34, "cₙ₋₁ = " + cin, size=14, color=NEG, bold=True, anchor="middle"))
        f.append(mono(x + cw / 2, by + 60, "cₙ  = " + cout, size=14, color=POS, bold=True, anchor="middle"))
        f.append(line(x + 16, by + 76, x + cw - 16, by + 76, color=MUTED, sw=1))
        f.append(text(x + cw / 2, by + 102, "збіглись" if same else "різні", size=14, color=col, bold=True))
        f.append(text(x + cw / 2, by + 124, "знак чесний" if same else "знак зламано", size=12,
                      color=(INK if same else POS)))
        f.append(text(x + cw / 2, by + 146, "V = 0" if same else "V = 1", size=13, color=col, bold=True))
    render(os.path.join(OUT, 'math-carry-xor.svg'), W, H, *f)


def fig_math_signed_lt():
    """Чому самотній N не годиться: різниця d, що вискочила за межу, обгортається
    на протилежний бік осі й перевертає знак r; V=1 каже читати N навпаки."""
    W, H = 760, 430
    f = [text(W / 2, 30, "Знакове «менше»: коли різниця обгортається за межу", size=16, bold=True)]

    axy = 158
    ax0, ax1 = 150, 610
    f.append(rect(ax1 + 4, axy - 26, 96, 52, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(rect(ax0 - 100, axy - 26, 96, 52, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    f.append(line(ax0 - 44, axy, ax1 + 44, axy, color=INK, sw=2))
    f.append(line(ax0, axy - 12, ax0, axy + 12, color=INK, sw=2))
    f.append(line(ax1, axy - 12, ax1, axy + 12, color=INK, sw=2))
    f.append(line((ax0 + ax1) / 2, axy - 8, (ax0 + ax1) / 2, axy + 8, color=MUTED, sw=1.5))
    f.append(text(ax0, axy + 34, "−2ⁿ⁻¹", size=13, color=NEG, bold=True))
    f.append(text((ax0 + ax1) / 2, axy + 34, "0", size=13, color=MUTED))
    f.append(text(ax1, axy + 34, "2ⁿ⁻¹−1", size=13, color=POS, bold=True))
    f.append(text(W / 2, axy - 46, "знаковий діапазон різниці d = a − b", size=14, bold=True))

    mid = (ax0 + ax1) / 2
    # вискок угору → у від'ємну зону
    f.append(arrow(mid + 70, axy - 58, ax1 + 46, axy - 20, color=POS, sw=1.8))
    f.append(text(ax1 + 46, axy - 66, "d за +межу", size=12, color=POS, bold=True))
    f.append(arrow(ax1 + 40, axy + 24, ax0 + 60, axy - 20, color=POS, sw=1.4, ))
    f.append(text(mid, axy + 100, "d вгору → r ВІД'ЄМНЕ (N=1), але A>B → «не менше»", size=12, color=POS))
    # вискок униз → у додатну зону
    f.append(arrow(mid - 70, axy - 58, ax0 - 46, axy - 20, color=NEG, sw=1.8))
    f.append(text(ax0 - 46, axy - 66, "d за −межу", size=12, color=NEG, bold=True))
    f.append(text(mid, axy + 122, "d вниз → r ДОДАТНЕ (N=0), але A<B → «менше»", size=12, color=NEG))

    box, bw, bh = textbox(W / 2, 372,
                          "без переповнення (V=0):  A<B ⟺ N=1\n"
                          "з переповненням  (V=1):  A<B ⟺ N=0\n"
                          "разом:  A<B (знакове) ⟺ N ⊕ V",
                          size=14, pad=12, fill="#eef7f0", stroke=FIELD, sw=1.8)
    f.append(box)
    render(os.path.join(OUT, 'math-signed-lt.svg'), W, H, *f)


if __name__ == '__main__':
    fig_four()
    fig_cv()
    fig_branch()
    fig_math_carry_xor()
    fig_math_signed_lt()
    print("OK: alu-flags-four, alu-flags-cv, alu-flags-branch, math-carry-xor, math-signed-lt")
