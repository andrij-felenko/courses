# -*- coding: utf-8 -*-
"""Фігури до теми «Barrel shifter».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_crossbar_vs_layers():
    """Головний контраст будови: повний crossbar (окремий великий мультиплексор
    на кожен вихід, ~n×n) проти barrel shifter (log₂n тонких шарів, кожен на свій
    степінь двійки)."""
    W, H = 780, 470
    f = []

    # --- Верх: повний crossbar ---
    f.append(text(W / 2, 30, "Повний crossbar: великий мультиплексор на кожен вихід",
                  size=15, bold=True, color=POS))
    n = 8
    cx0, cw, cgap, cy, ch = 90, 66, 12, 62, 46
    # входи (спільна шина зверху) → до кожного великого mux
    bus_y = 56
    f.append(line(cx0, bus_y, cx0 + n * (cw + cgap) - cgap, bus_y, color=MUTED, sw=2))
    f.append(text(cx0 - 8, bus_y + 4, "усі n входів", size=11, color=MUTED, anchor="end"))
    for i in range(n):
        x = cx0 + i * (cw + cgap)
        mcx = x + cw / 2
        f.append(line(mcx, bus_y, mcx, cy, color=MUTED, sw=1))
        f.append(fitbox(x, cy, cw, ch, "MUX\nn→1", size=11, fill="#fdecea",
                        stroke=POS, bold=True))
        f.append(text(mcx, cy + ch + 14, "y%d" % i, size=11, color=MUTED))
    f.append(text(W / 2, cy + ch + 40,
                  "n великих мультиплексорів по n входів  →  порядка  n × n  вентилів",
                  size=12.5, color=MUTED))

    # --- Низ: barrel shifter (шари) ---
    yb = 250
    f.append(text(W / 2, yb - 8, "Barrel shifter: log₂n тонких шарів",
                  size=15, bold=True, color=FIELD))
    lay_x, lay_w, lay_h, lay_gap = 150, 480, 40, 18
    layers = [
        ("шар «4»:  зсунути на 4  або  пропустити", "1"),
        ("шар «2»:  зсунути на 2  або  пропустити", "0"),
        ("шар «1»:  зсунути на 1  або  пропустити", "1"),
    ]
    ly = yb + 16
    for label, bit in layers:
        on = (bit == "1")
        col = FIELD if on else MUTED
        fill = "#eafaf1" if on else FILL
        f.append(fitbox(lay_x, ly, lay_w, lay_h, label, size=12.5,
                        fill=fill, stroke=col, bold=True))
        # керівний біт зліва
        f.append(fitbox(lay_x - 84, ly, 70, lay_h, "біт = %s" % bit, size=12,
                        fill=("#eafaf1" if on else "#f4f6f8"),
                        stroke=col, bold=True))
        ly += lay_h + lay_gap
    f.append(text(W / 2, ly + 8,
                  "величина зсуву в двійці вмикає шари:  5 = 101  →  шари «4» і «1»",
                  size=12.5, color=INK))
    f.append(text(W / 2, ly + 30,
                  "разом лише  n × log₂n  простих мультиплексорів 2-в-1",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, 'crossbar-vs-layers.svg'), W, H, *f)


def fig_shift_by_5():
    """Прохід зсуву вліво на 5 (=101) крізь три шари восьмибітного зсувача:
    шар-1 і шар-4 увімкнені, шар-2 пропускає; знизу заходять нулі."""
    W, H = 780, 420
    f = []
    f.append(text(W / 2, 30, "Зсув вліво на 5 (101₂) крізь три шари", size=16, bold=True))

    n = 8
    bx0, bw, gap = 150, 66, 6
    row_h = 34

    def draw_bits(y, bits, hi=None, label="", lab_col=INK):
        """Рядок із 8 бітів; hi — множина позицій (0..7) підсвітити зеленим (нові нулі)."""
        f.append(text(bx0 - 12, y + row_h / 2 + 5, label, size=12.5,
                      color=lab_col, anchor="end", bold=(lab_col != MUTED)))
        for j in range(n):
            pos = n - 1 - j                      # зліва старший біт (7), справа 0
            x = bx0 + j * (bw + gap)
            b = bits[j]
            isnew = hi is not None and pos in hi
            fill = "#eafaf1" if isnew else FILL
            stroke = FIELD if isnew else LINE
            col = FIELD if isnew else INK
            f.append(rect(x, y, bw, row_h, fill=fill, stroke=stroke, sw=1.4))
            f.append(text(x + bw / 2, y + row_h / 2 + 5, b, size=15, bold=True, color=col))

    # позиційні підписи зверху
    for j in range(n):
        pos = n - 1 - j
        x = bx0 + j * (bw + gap)
        f.append(text(x + bw / 2, 56, str(pos), size=11, color=MUTED))

    y = 66
    # вхід
    draw_bits(y, ["1", "0", "1", "0", "1", "1", "0", "1"], label="вхід A")
    # шар 1: зсув на 1, знизу 1 нуль → нова позиція 0
    y += row_h + 26
    f.append(text(W / 2, y - 10, "шар «1» увімкнено (біт 1 величини) → зсув на 1",
                  size=12, color=FIELD))
    draw_bits(y, ["0", "1", "0", "1", "1", "0", "1", "0"], hi={0}, label="після «1»")
    # шар 2: пропускає
    y += row_h + 26
    f.append(text(W / 2, y - 10, "шар «2» вимкнено (біт 0) → пропускає без змін",
                  size=12, color=MUTED))
    draw_bits(y, ["0", "1", "0", "1", "1", "0", "1", "0"], label="після «2»", lab_col=MUTED)
    # шар 4: зсув на 4, знизу 4 нулі
    y += row_h + 26
    f.append(text(W / 2, y - 10, "шар «4» увімкнено (біт 4 величини) → зсув на 4",
                  size=12, color=FIELD))
    draw_bits(y, ["1", "0", "1", "0", "0", "0", "0", "0"], hi={0, 1, 2, 3},
              label="результат", lab_col=POS)

    f.append(text(W / 2, y + row_h + 24,
                  "1 + 4 = 5 :  A зсунуто вліво на 5, молодші позиції — нулі (зелені)",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, 'shift-by-5.svg'), W, H, *f)


def fig_fill_modes():
    """Три режими на одному блоці: логічний зсув (нулі), арифметичний зсув вправо
    (знаковий біт), оберт (біти з протилежного краю). Різниця лише у «вході
    заповнення» з краю."""
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 30, "Одне залізо — три режими: різниться лише вхід заповнення",
                  size=15.5, bold=True))

    n = 6
    bw, gap = 58, 6
    row_w = n * (bw + gap) - gap
    bx0 = (W - row_w) / 2
    row_h = 36

    def word_row(y, bits, cols):
        for j in range(n):
            x = bx0 + j * (bw + gap)
            f.append(rect(x, y, bw, row_h, fill=cols[j][1], stroke=cols[j][2], sw=1.4))
            f.append(text(x + bw / 2, y + row_h / 2 + 5, bits[j], size=15, bold=True,
                          color=cols[j][0]))

    plain = (INK, FILL, LINE)
    fillc = (FIELD, "#eafaf1", FIELD)

    # 1) логічний зсув вправо: згори заходить 0
    y = 76
    f.append(text(bx0, y - 12, "Логічний зсув вправо: згори заходить 0", size=13,
                  bold=True, color=INK, anchor="start"))
    word_row(y, ["0", "1", "0", "1", "1", "0"],
             [fillc, plain, plain, plain, plain, plain])
    f.append(text(bx0 - 10, y + row_h / 2 + 5, "→", size=18, color=MUTED, anchor="end"))
    f.append(text(bx0 + row_w + 12, y + row_h / 2 + 5, "нуль", size=12, color=FIELD,
                  anchor="start"))

    # 2) арифметичний зсув вправо: згори заходить копія знакового біта (тут 1)
    y = 176
    f.append(text(bx0, y - 12, "Арифметичний зсув вправо: згори — копія знакового біта",
                  size=13, bold=True, color=INK, anchor="start"))
    word_row(y, ["1", "1", "0", "1", "1", "0"],
             [fillc, plain, plain, plain, plain, plain])
    f.append(text(bx0 + row_w + 12, y + row_h / 2 + 5, "знак = 1", size=12, color=FIELD,
                  anchor="start"))

    # 3) оберт вправо: біт, що випав знизу, заходить згори
    y = 276
    f.append(text(bx0, y - 12, "Оберт (циклічний зсув): біт, що випав знизу, заходить згори",
                  size=13, bold=True, color=INK, anchor="start"))
    word_row(y, ["0", "1", "0", "1", "1", "0"],
             [fillc, plain, plain, plain, plain, plain])
    # дуга «випало знизу → зайшло згори»
    x_last = bx0 + (n - 1) * (bw + gap) + bw / 2
    x_first = bx0 + bw / 2
    f.append(('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
              'fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
              % (x_last, y + row_h + 4, x_last, y + row_h + 46,
                 x_first, y + row_h + 46, x_first, y + row_h + 4, NEG)))
    f.append(text(W / 2, y + row_h + 42, "той самий біт", size=11.5, color=NEG))

    render(os.path.join(OUT, 'fill-modes.svg'), W, H, *f)


def fig_name_timeline():
    """Три віхи назви й реалізації: CDC 6600 (1964) — залізо є, зветься «parallel
    shifting network»; патент Burroughs (поданий 1965) — уперше термін «barrel
    switch»; Intel 386 (1985) — barrel shifter на кристалі мікропроцесора. Ліворуч —
    три різні речі: ідея розкладу, назва, реалізація."""
    W, H = 800, 430
    f = []
    f.append(text(W / 2, 30, "Ідея, назва й залізо йшли нарізно",
                  size=16, bold=True))

    # горизонтальна вісь часу
    ax_x0, ax_x1, ax_y = 120, 700, 92
    f.append(line(ax_x0, ax_y, ax_x1 + 8, ax_y, color=MUTED, sw=2))
    f.append(text(ax_x1 + 14, ax_y + 4, "рік", size=11, color=MUTED, anchor="start"))

    # три віхи: (рік, x, заголовок, що саме, колір-акцент)
    marks = [
        (1964, 190, "CDC 6600",
         "залізо є: 6 ярусів, зсув\nдо 63 позицій за такт;\nзветься «parallel\nshifting network»", FIELD),
        (1965, 400, "патент Burroughs",
         "уперше в тексті —\nтермін «barrel switch»\n(подано 26.11.1965,\nвидано 1968)", POS),
        (1985, 615, "Intel 386",
         "barrel shifter на кристалі\nмікропроцесора: зсув за\n3 такти незалежно від\nвеличини", NEG),
    ]
    for yr, x, head, body, col in marks:
        f.append(circle(x, ax_y, 6, fill=col, stroke=col, sw=2))
        f.append(text(x, ax_y - 14, str(yr), size=13, bold=True, color=col))
        f.append(line(x, ax_y + 6, x, ax_y + 34, color=MUTED, sw=1))
        f.append(fitbox(x - 92, ax_y + 34, 184, 44, head, size=13.5,
                        fill="#f4f6f8", stroke=col, bold=True))
        f.append(mtext(x, ax_y + 96, body, size=11, color=INK, lh=1.28))

    # ліворуч знизу — розрізнення трьох речей
    yb = 300
    f.append(text(W / 2, yb, "Три речі, які легко сплутати:", size=13.5, bold=True))
    rows = [
        ("ідея розкладу на степені двійки", "стара, спільна — жоден автор", MUTED),
        ("назва «barrel switch / shifter»", "від патенту Burroughs, 1965", POS),
        ("реалізація на кристалі CPU", "масово — Intel 386, 1985", NEG),
    ]
    ly = yb + 22
    for what, who, col in rows:
        f.append(fitbox(150, ly, 300, 30, what, size=12, fill="#f4f6f8",
                        stroke=col, bold=True))
        f.append(text(468, ly + 20, "→  " + who, size=12, color=INK, anchor="start"))
        ly += 38

    render(os.path.join(OUT, 'name-timeline.svg'), W, H, *f)


if __name__ == "__main__":
    fig_crossbar_vs_layers()
    fig_shift_by_5()
    fig_fill_modes()
    fig_name_timeline()
    print("OK: figures written to", OUT)
