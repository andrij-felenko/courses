# -*- coding: utf-8 -*-
"""Фігури до історичної вставки «Історія прапорців стану» (hist-condition-codes).
Запуск:  python figs-hist.py   → пише SVG у ./img/
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


def fig_three_eras():
    """Три способи спитати 'який вийшов результат', у хронології:
    (1) IBM 704 — тест-і-стрибок однією командою, стану ніде не лишається;
    (2) System/360 — 2 біти коду умови у PSW, живуть до наступної операції;
    (3) явний регістр стану — окремі N Z V C, кожна операція оновлює однаково."""
    W, H = 760, 470
    f = [text(W / 2, 30, "Три способи спитати «який вийшов результат»", size=17, bold=True)]

    col_w = 226
    xs = [24, 24 + col_w + 14, 24 + 2 * (col_w + 14)]
    top = 58
    body_h = 372

    # ── (1) IBM 704: тест-і-стрибок ──
    x = xs[0]
    f.append(rect(x, top, col_w, body_h, fill="#f7f9fc", stroke=LINE, sw=1.4))
    f.append(text(x + col_w / 2, top + 24, "IBM 704 · 1954", size=14, bold=True))
    f.append(text(x + col_w / 2, top + 42, "тест-і-стрибок", size=12, color=MUTED, italic=True))
    code1 = [
        "  CLA  X      ; A := X",
        "  SUB  Y      ; A := A−Y",
        "  TMI  NEG    ; A<0 → стриб",
        "  ...         ; інакше сюди",
        "NEG ...",
    ]
    yy = top + 74
    for s in code1:
        f.append(mono(x + 14, yy, s, size=11))
        yy += 21
    f.append(fitbox(x + 12, top + 196, col_w - 24, 156,
                    "Команда сама дивиться\nна суматор і стрибає.\n"
                    "Стану після неї\nне лишається —\nпитати «а який був\nзнак?» вже нема де.\n"
                    "Умову вшито\nв сам стрибок.",
                    size=11, fill="#ffffff", stroke=MUTED, sw=1.1, color=INK))

    # ── (2) System/360: 2-бітний код умови ──
    x = xs[1]
    f.append(rect(x, top, col_w, body_h, fill="#eef4ff", stroke=NEG, sw=1.6))
    f.append(text(x + col_w / 2, top + 24, "System/360 · 1964", size=14, bold=True, color=NEG))
    f.append(text(x + col_w / 2, top + 42, "2 біти коду умови", size=12, color=MUTED, italic=True))
    # два біти
    bx = x + 42
    by = top + 66
    for i, bit in enumerate(("c", "c")):
        f.append(rect(bx + i * 34, by, 30, 30, fill="#ffffff", stroke=NEG, sw=1.6))
        f.append(text(bx + i * 34 + 15, by + 21, "?", size=16, bold=True, color=NEG))
    f.append(mono(bx + 84, by + 21, "CC ∈ {0,1,2,3}", size=12, color=INK))
    f.append(fitbox(x + 12, top + 116, col_w - 24, 236,
                    "Операція лишає у слові\nстану (PSW) двобітний\nкод: 0, 1, 2 або 3.\n \n"
                    "Але що ці числа значать —\nзалежить від КОМАНДИ:\n"
                    "після ADD «2» — це\n«додатний», після\nпорівняння — «перший\nбільший».\n \n"
                    "Стан нарешті переживає\nкоманду; тлумачити\nйого важко.",
                    size=11, fill="#ffffff", stroke=NEG, sw=1.1, color=INK))

    # ── (3) явний регістр стану N Z V C ──
    x = xs[2]
    f.append(rect(x, top, col_w, body_h, fill="#eafbf0", stroke=FIELD, sw=1.6))
    f.append(text(x + col_w / 2, top + 24, "явний регістр стану", size=14, bold=True, color=FIELD))
    f.append(text(x + col_w / 2, top + 42, "N Z V C, однаково завжди", size=11, color=MUTED, italic=True))
    bx = x + 30
    by = top + 66
    for i, nm in enumerate(("N", "Z", "V", "C")):
        f.append(rect(bx + i * 40, by, 34, 30, fill="#ffffff", stroke=FIELD, sw=1.6))
        f.append(text(bx + i * 40 + 17, by + 21, nm, size=14, bold=True, color=FIELD))
    f.append(fitbox(x + 12, top + 116, col_w - 24, 236,
                    "Окремі іменовані біти:\nзнак, нуль, знакове\nпереповнення, перенос.\n \n"
                    "МАЙЖЕ КОЖНА операція\nчерез АЛП оновлює їх\nОДНАКОВО.\n \n"
                    "Читати легко: «менше\nзнакове» = N≠V, і це\nне залежить від того,\nхто порахував.\n \n"
                    "Так і живе в процесорах\nдонині.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.1, color=INK))

    # стрілки хронології між колонками
    ay = top + body_h + 26
    for i in range(2):
        x1 = xs[i] + col_w
        x2 = xs[i + 1]
        f.append(arrow(x1 + 2, top + body_h / 2, x2 - 2, top + body_h / 2, color=MUTED, sw=2))
    f.append(text(W / 2, H - 10,
                  "стан результату поступово «відклеївся» від самої команди й став окремим, іменованим",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, 'hist-three-eras.svg'), W, H, *f)


def fig_two_borrows():
    """Дві живі домовленості про перенос при відніманні A−B.
    Ліворуч: борг (x86/Z80/68000) — C=1 коли позичали. Праворуч: не-борг
    (6502/ARM/360) — C=1 коли позики НЕ було, бо C — чесний перенос із A+(~B)+1."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Одна операція A − B, два протилежні значення переносу", size=16, bold=True)]

    # спільний приклад згори
    f.append(text(W / 2, 56, "приклад:  5 − 3  (позики немає)     і     3 − 5  (позика є)",
                  size=12, color=MUTED, italic=True))

    lx = 30
    rx = 392
    bw = 338
    top = 78
    bh = 250

    # ── ліва: БОРГ ──
    f.append(rect(lx, top, bw, bh, fill="#fdecea", stroke=POS, sw=1.7))
    f.append(text(lx + bw / 2, top + 24, "домовленість «борг»", size=14, bold=True, color=POS))
    f.append(text(lx + bw / 2, top + 42, "C = 1  ⟺  довелося позичати", size=12, color=INK))
    rows = [
        ("5 − 3 = 2   позики нема", "C = 0"),
        ("3 − 5 = −2  позичали", "C = 1"),
    ]
    yy = top + 66
    for cond, res in rows:
        f.append(rect(lx + 16, yy, bw - 32, 34, fill="#ffffff", stroke=POS, sw=1.1))
        f.append(mono(lx + 28, yy + 22, cond, size=12))
        f.append(text(lx + bw - 28, yy + 22, res, size=13, bold=True, color=POS, anchor="end"))
        yy += 44
    f.append(fitbox(lx + 16, yy + 2, bw - 32, top + bh - yy - 14,
                    "так вважає людина з олівцем: позичив — запиши борг.\n"
                    "x86 · Z80 · 8080 · 68000 · 8051 · VAX",
                    size=11, fill="#fff5f4", stroke=POS, sw=1.0, color=INK))

    # ── права: НЕ-БОРГ ──
    f.append(rect(rx, top, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.7))
    f.append(text(rx + bw / 2, top + 24, "домовленість «не-борг»", size=14, bold=True, color=NEG))
    f.append(text(rx + bw / 2, top + 42, "C = 1  ⟺  позики НЕ було", size=12, color=INK))
    rows2 = [
        ("5 − 3 → 5+(~3)+1  перенос є", "C = 1"),
        ("3 − 5 → 3+(~5)+1  переносу нема", "C = 0"),
    ]
    yy = top + 66
    for cond, res in rows2:
        f.append(rect(rx + 16, yy, bw - 32, 34, fill="#ffffff", stroke=NEG, sw=1.1))
        f.append(mono(rx + 28, yy + 22, cond, size=11))
        f.append(text(rx + bw - 28, yy + 22, res, size=13, bold=True, color=NEG, anchor="end"))
        yy += 44
    f.append(fitbox(rx + 16, yy + 2, bw - 32, top + bh - yy - 14,
                    "падає з A+(~B)+1: C — чесний перенос суматора.\n"
                    "6502 · ARM · PowerPC · System/360 · MSP430 · SPARC",
                    size=11, fill="#f4f8ff", stroke=NEG, sw=1.0, color=INK))

    f.append(text(W / 2, H - 12,
                  "той самий біт, протилежний зміст:  борг = НЕ C.  Обидві — усталений факт, жодна не «правильніша»",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, 'hist-two-borrows.svg'), W, H, *f)


if __name__ == '__main__':
    fig_three_eras()
    fig_two_borrows()
    print("OK: hist-three-eras, hist-two-borrows")
