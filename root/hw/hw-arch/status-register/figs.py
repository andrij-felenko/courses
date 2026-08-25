# -*- coding: utf-8 -*-
"""Фігури до теми «Регістр стану процесора».
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


def fig_layout():
    """Байт SREG в AVR: вісім названих бітів I T H S V N Z C, розбитих на
    дві популяції — біти керування (ліворуч, старші) і прапорці результату
    (праворуч, молодші). Видно, що арифметика чіпає лише праву частину."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Байт SREG: одне слово, дві популяції бітів", size=17, bold=True)]

    # Вісім комірок байта, біт 7 (ліворуч) … біт 0 (праворуч)
    bits = [
        ("I", 7, "дозвіл переривань", NEG),
        ("T", 6, "біт-буфер", NEG),
        ("H", 5, "напівперенос", POS),
        ("S", 4, "знак N⊕V", POS),
        ("V", 3, "переповнення", POS),
        ("N", 2, "від'ємний", POS),
        ("Z", 1, "нуль", POS),
        ("C", 0, "перенос", POS),
    ]
    cw, ch = 82, 66
    x0 = (W - len(bits) * cw) / 2
    y0 = 84
    for i, (name, num, why, col) in enumerate(bits):
        x = x0 + i * cw
        fill = "#eef2fb" if col is NEG else "#fdf0ee"
        f.append(rect(x, y0, cw - 6, ch, fill=fill, stroke=col, sw=2))
        f.append(text(x + (cw - 6) / 2, y0 + 30, name, size=22, bold=True, color=col))
        f.append(text(x + (cw - 6) / 2, y0 + 52, "біт %d" % num, size=11, color=MUTED))
        f.append(text(x + (cw - 6) / 2, y0 + ch + 18, why, size=10.5, color=MUTED))

    # Дужки-групи під іменами
    ctrl_x0 = x0
    ctrl_x1 = x0 + 2 * cw - 6
    res_x0 = x0 + 2 * cw
    res_x1 = x0 + 8 * cw - 6
    gy = y0 + ch + 44
    f.append(line(ctrl_x0, gy, ctrl_x1, gy, color=NEG, sw=2))
    f.append(line(res_x0, gy, res_x1, gy, color=POS, sw=2))
    f.append(text((ctrl_x0 + ctrl_x1) / 2, gy + 22, "БІТИ КЕРУВАННЯ", size=13, bold=True, color=NEG))
    f.append(text((ctrl_x0 + ctrl_x1) / 2, gy + 40, "налаштовують процесор;", size=11, color=MUTED))
    f.append(text((ctrl_x0 + ctrl_x1) / 2, gy + 56, "арифметика їх НЕ чіпає", size=11, color=MUTED))
    f.append(text((res_x0 + res_x1) / 2, gy + 22, "ПРАПОРЦІ РЕЗУЛЬТАТУ", size=13, bold=True, color=POS))
    f.append(text((res_x0 + res_x1) / 2, gy + 40, "знімок останньої дії АЛП;", size=11, color=MUTED))
    f.append(text((res_x0 + res_x1) / 2, gy + 56, "оновлюються майже щоразу", size=11, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "старший біт ← → молодший;  одне слово можна цілком зберегти й відновити",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'sreg-layout.svg'), W, H, *f)


def fig_save_restore():
    """Регістр стану переживає переривання: головна програма з живими прапорцями
    після CMP; переривання зберігає SREG у стек, рахує (затирає), відновлює SREG;
    керування вертається — прапорці ті самі, перехід правильний."""
    W, H = 760, 470
    f = [text(W / 2, 30, "Регістр стану переживає переривання", size=17, bold=True)]

    # Ліва колонка — головна програма (часова вісь згори вниз)
    lx = 60
    lw = 250
    f.append(text(lx + lw / 2, 66, "головна програма", size=14, bold=True))
    steps_main = [
        (86, "CMP a, b", "прапорці в SREG — ЖИВІ", INK, "#f4f6f8"),
        (150, "…", "готова стрибнути за умовою", MUTED, "#f4f6f8"),
    ]
    for y, code, note, col, fill in steps_main:
        f.append(rect(lx, y, lw, 44, fill=fill, stroke=LINE, sw=1.4))
        f.append(mono(lx + 14, y + 22, code, size=15, bold=True, color=col))
        f.append(text(lx + 14, y + 38, note, size=10.5, color=MUTED, anchor="start"))

    # Точка переривання
    f.append(circle(lx + lw, 172, 7, fill=POS, stroke=POS, sw=1))
    f.append(text(lx + lw / 2, 220, "◄ тут влучає переривання", size=12, bold=True, color=POS))

    # Продовження головної (після повернення)
    y_ret = 372
    f.append(rect(lx, y_ret, lw, 44, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(mono(lx + 14, y_ret + 22, "BRLO skip", size=15, bold=True, color=FIELD))
    f.append(text(lx + 14, y_ret + 38, "читає ТІ САМІ прапорці", size=10.5, color=MUTED, anchor="start"))

    f.append(arrow(lx + lw / 2, 194, lx + lw / 2, 220, color=MUTED, sw=1.6))
    f.append(arrow(lx + lw / 2, 236, lx + lw / 2, y_ret - 6, color=FIELD, sw=1.6))
    f.append(text(lx + lw / 2 - 4, (236 + y_ret) / 2, "керування", size=10, color=MUTED, anchor="end"))
    f.append(text(lx + lw / 2 - 4, (236 + y_ret) / 2 + 14, "повертається", size=10, color=MUTED, anchor="end"))

    # Права колонка — обробник переривання
    rx = 420
    rw = 280
    f.append(rect(rx - 14, 236, rw + 28, 126, fill="#fbfbfd", stroke=NEG, sw=1.6))
    f.append(text(rx + rw / 2, 258, "обробник переривання", size=14, bold=True, color=NEG))
    steps_isr = [
        (270, "PUSH SREG", "зберегти знімок у стек", FIELD),
        (306, "INC ticks", "рахує — ЗАТИРАЄ прапорці", POS),
        (342, "POP  SREG", "відновити знімок зі стеку", FIELD),
    ]
    for y, code, note, col in steps_isr:
        f.append(mono(rx, y, code, size=14, bold=True, color=col))
        f.append(text(rx + 150, y, note, size=10.5, color=MUTED, anchor="start"))

    # Стрілки заходу/виходу переривання
    f.append(arrow(lx + lw + 4, 172, rx + 30, 246, color=POS, sw=1.8))
    f.append(arrow(rx + 30, 356, lx + lw + 4, y_ret + 8, color=FIELD, sw=1.8))

    f.append(text(W / 2, H - 12,
                  "весь стан — в одному слові, тож зняти й відновити знімок можна однією парою команд",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'save-restore.svg'), W, H, *f)


def fig_rmw():
    """Читання-зміна-запис SREG розірвано перериванням: головна читає копію;
    переривання міняє біт у справжньому SREG; головна дописує стару копію —
    зміна обробника затерта. Небезпечний проміжок між читанням і записом."""
    W, H = 760, 440
    f = [text(W / 2, 30, "Читання-зміна-запис розірвано перериванням", size=17, bold=True)]

    # Справжній SREG (посередині, «жива» комірка)
    sx = W / 2 - 90
    sy = 88
    f.append(text(sx + 90, sy - 8, "справжній SREG (спільна комірка)", size=12, bold=True))
    def sreg_cell(y, bits, hilite=None, note="", ncol=MUTED):
        cw = 22
        x0 = sx
        for i, b in enumerate(bits):
            col = POS if (hilite is not None and i == hilite) else LINE
            fill = "#fdecea" if (hilite is not None and i == hilite) else "#ffffff"
            f.append(rect(x0 + i * cw, y, cw - 2, 26, fill=fill, stroke=col, sw=1.6, rx=3))
            f.append(mono(x0 + i * cw + (cw - 2) / 2, y + 18, b, size=13, anchor="middle",
                          color=(POS if (hilite is not None and i == hilite) else INK)))
        if note:
            f.append(text(x0 + len(bits) * cw + 12, y + 18, note, size=11, color=ncol, anchor="start"))

    sreg_cell(sy, list("00011010"), note="стан на початку")

    # Крок 1 — головна читає копію
    lx = 40
    f.append(rect(lx, 168, 300, 50, fill="#eef2fb", stroke=NEG, sw=1.6))
    f.append(text(lx + 12, 188, "① головна: IN copy, SREG", size=13, bold=True, color=NEG, anchor="start"))
    f.append(mono(lx + 12, 208, "copy = 0001 1010   (знімок)", size=12, color=MUTED))
    f.append(arrow(sx, sy + 26, lx + 200, 168, color=NEG, sw=1.4))

    # Крок 2 — переривання міняє реальний SREG
    rx = 420
    f.append(rect(rx, 168, 300, 50, fill="#fdf0ee", stroke=POS, sw=1.8))
    f.append(text(rx + 12, 188, "② переривання: міняє біт у SREG", size=13, bold=True, color=POS, anchor="start"))
    f.append(mono(rx + 12, 208, "SREG → 1001 1010   (біт 7 ↑)", size=12, color=MUTED))
    sreg_cell(258, list("10011010"), hilite=0, note="обробник підняв біт 7", ncol=POS)
    f.append(arrow(rx + 150, 218, sx + 90, 258, color=POS, sw=1.6))

    # Крок 3 — головна дописує стару копію
    f.append(rect(lx, 330, 300, 62, fill="#eef2fb", stroke=NEG, sw=1.6))
    f.append(text(lx + 12, 350, "③ головна: OUT SREG, copy", size=13, bold=True, color=NEG, anchor="start"))
    f.append(mono(lx + 12, 370, "SREG = 0001 1010   (стара!)", size=12, color=MUTED))
    f.append(mono(lx + 12, 386, "→ біт 7 обробника ЗАТЕРТО", size=12, color=POS, bold=True))
    f.append(arrow(lx + 200, 330, sx + 40, 286, color=NEG, sw=1.6))

    box, bw, bh = textbox(rx + 150, 360,
                          "небезпечний саме проміжок\n"
                          "між читанням ① і записом ③:\n"
                          "копія весь цей час застаріває",
                          size=12, pad=10, fill="#fdf6ec", stroke=POS, sw=1.6)
    f.append(box)

    f.append(text(W / 2, H - 12,
                  "тому дозвіл переривань чіпають однокомандним SEI/CLI — його не розірвати",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'rmw-hazard.svg'), W, H, *f)


if __name__ == '__main__':
    fig_layout()
    fig_save_restore()
    fig_rmw()
    print("OK: sreg-layout, save-restore, rmw-hazard")
