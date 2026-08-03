# -*- coding: utf-8 -*-
"""Фігури до теми «Арифметико-логічний пристрій (АЛП)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_block():
    """АЛП як блок: два операнди + код операції на вхід, результат + прапорці на вихід;
    усередині — арифметичний і логічний вузли, що зливаються в MUX-вибір результату."""
    W, H = 720, 430
    f = []
    # Зовнішня рамка АЛП
    bx, by, bw, bh = 210, 70, 300, 290
    f.append(rect(bx, by, bw, bh, fill="#fbfcfe", stroke=INK, sw=2))
    f.append(text(bx + bw / 2, by + 26, "АЛП", size=18, bold=True))

    # Входи-операнди ліворуч
    f.append(textbox(95, 140, "Операнд A", size=14, fill="#eef4ff", stroke=NEG)[0])
    f.append(textbox(95, 210, "Операнд B", size=14, fill="#eef4ff", stroke=NEG)[0])
    f.append(arrow(150, 140, bx, 140, color=NEG))
    f.append(arrow(150, 210, bx, 210, color=NEG))

    # Код операції зверху
    f.append(textbox(bx + bw / 2, 30, "код операції", size=13, fill="#fff6e6", stroke="#b8860b")[0])
    f.append(arrow(bx + bw / 2, 48, bx + bw / 2, by, color="#b8860b"))

    # Усередині: два вузли
    f.append(fitbox(bx + 28, 120, 110, 52, "арифметичний\nвузол (+ −)", size=13,
                    fill="#fdecea", stroke=POS, bold=False))
    f.append(fitbox(bx + 28, 200, 110, 52, "логічний\nвузол (AND…)", size=13,
                    fill="#eafaf1", stroke=FIELD, bold=False))

    # MUX-вибір результату
    mux_x = bx + 188
    f.append(fitbox(mux_x, 150, 70, 72, "MUX\nвибір", size=13, fill=FILL, stroke=LINE, bold=True))
    f.append(arrow(bx + 138, 146, mux_x, 168, color=POS))
    f.append(arrow(bx + 138, 226, mux_x, 204, color=FIELD))
    # код операції керує MUX (пунктир згори)
    f.append(line(bx + bw / 2, by + 14, mux_x + 35, 150, color="#b8860b", sw=1.4, dash="4 3"))

    # Виходи праворуч
    f.append(arrow(mux_x + 70, 186, 620, 186, color=INK, sw=2))
    f.append(textbox(665, 186, "результат", size=14, fill=FILL, stroke=INK)[0])
    f.append(arrow(bx + bw - 14, 330, 620, 330, color=MUTED))
    f.append(textbox(665, 330, "прапорці", size=13, fill="#f3f4f6", stroke=MUTED)[0])
    f.append(text(bx + bw / 2, by + bh - 14, "Z  N  C  V", size=13, color=MUTED))

    render(os.path.join(OUT, 'alu-block.svg'), W, H, *f)


def fig_optable():
    """Один блок — багато дій: код операції обирає, яку саме функцію видати.
    Колонка арифметики й колонка логіки під спільним «селектором»."""
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 30, "Один код операції → одна з багатьох дій", size=16, bold=True))

    rows_a = [("000", "A + B", "додати"),
              ("001", "A − B", "відняти"),
              ("010", "A + 1", "інкремент")]
    rows_l = [("100", "A AND B", "побітове І"),
              ("101", "A OR B", "побітове АБО"),
              ("110", "A XOR B", "побітове XOR")]

    def column(x0, title, rows, accent, fill):
        col = [text(x0 + 150, 70, title, size=14, bold=True, color=accent)]
        # шапка
        for j, (cap, w) in enumerate([("код", 60), ("операція", 130), ("сенс", 110)]):
            pass
        y = 92
        col.append(text(x0 + 28, y, "код", size=12, color=MUTED))
        col.append(text(x0 + 130, y, "операція", size=12, color=MUTED))
        col.append(text(x0 + 250, y, "сенс", size=12, color=MUTED))
        y += 8
        for (code, op, mean) in rows:
            y += 44
            col.append(rect(x0, y - 26, 300, 36, fill=fill, stroke=accent, sw=1.3))
            col.append(text(x0 + 30, y - 3, code, size=14, bold=True))
            col.append(text(x0 + 130, y - 3, op, size=14, anchor="middle"))
            col.append(text(x0 + 250, y - 3, mean, size=12, color=MUTED))
        return col

    f += column(60, "арифметика", rows_a, POS, "#fdecea")
    f += column(380, "логіка", rows_l, FIELD, "#eafaf1")

    f.append(text(W / 2, H - 18,
                  "старший біт коду розрізняє арифметику (0…) і логіку (1…)",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'alu-optable.svg'), W, H, *f)


def fig_flags():
    """Звідки беруться прапорці: на прикладі віднімання 5 − 5 результат 0,
    а перенос/переповнення читають із самого додавання доповняльних кодів."""
    W, H = 750, 360
    f = []
    f.append(text(W / 2, 30, "Прапорці — це «довідка» про щойно отриманий результат", size=15, bold=True))

    # Стовпчик обчислення 5 − 5  (4 біти)
    lines = [
        " 5 − 5  =  5 + (−5)        (відняти = додати доповняльний код)",
        "",
        "   0101            5",
        " + 1011          −5  (доповняльний код)",
        " ──────",
        " 1 0000            перенос-вихід = 1, молодші 4 біти = 0000",
    ]
    x0 = 70
    y = 70
    f.append(rect(x0 - 14, y - 24, 470, 150, fill="#f7f9fc", stroke=LINE, sw=1.3))
    for ln in lines:
        f.append(text(x0, y, ln, size=14, color=INK, anchor="start"))
        y += 22
    # моноширинність імітуємо лівим вирівнюванням; вистачає для читабельності

    # Прапорці праворуч
    bx = 560
    flags = [
        ("Z", "= 1", "результат нульовий", FIELD),
        ("N", "= 0", "старший біт 0 → невід'ємний", NEG),
        ("C", "= 1", "був перенос із розряду", POS),
        ("V", "= 0", "знакового переповнення нема", MUTED),
    ]
    f.append(text(bx, 64, "прапорці", size=14, bold=True))
    y = 86
    for (name, val, mean, col) in flags:
        f.append(circle(bx, y + 10, 15, fill="#ffffff", stroke=col, sw=2))
        f.append(text(bx, y + 15, name, size=15, bold=True, color=col))
        f.append(text(bx + 26, y + 6, val, size=13, bold=True, anchor="start"))
        f.append(text(bx + 26, y + 22, mean, size=11, color=MUTED, anchor="start"))
        y += 58

    f.append(text(W / 2, H - 14,
                  "ті самі суматори рахують число; прапорці лише «зчитують» його ознаки",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'alu-flags.svg'), W, H, *f)


def fig_history():
    """Шлях поняття АЛП: від назви на папері (EDVAC, 1945) до цілого блока
    на одному кристалі (74181, 1970) — 25 років між ідеєю та кремнієм."""
    W, H = 760, 340
    f = []
    f.append(text(W / 2, 30, "Від назви на папері до блока на кремнії", size=16, bold=True))

    # Горизонтальна вісь часу
    axy = 150
    f.append(line(70, axy, 690, axy, color=MUTED, sw=2))
    for x, yr in [(120, "1945"), (400, "1958"), (690, "1970")]:
        f.append(line(x, axy - 5, x, axy + 5, color=MUTED, sw=2))
        f.append(text(x, axy + 22, yr, size=12, color=MUTED, bold=True))

    # Віха 1 — EDVAC: назва «центральна арифметична частина»
    f.append(circle(120, axy, 7, fill="#fdecea", stroke=POS, sw=2))
    b1 = textbox(150, 78, "EDVAC, чернетка фон Неймана\n«центральна арифметична\nчастина» CA — назва",
                 size=12, fill="#fdecea", stroke=POS)[0]
    f.append(b1)
    f.append(line(120, axy - 7, 120, 108, color=POS, sw=1.3, dash="4 3"))

    # Віха 2 — інтегральна схема робить блок на кристалі можливим
    f.append(circle(400, axy, 7, fill="#fff6e6", stroke="#b8860b", sw=2))
    b2 = textbox(400, 230, "інтегральна схема:\nсотні вентилів на\nодному кристалі",
                 size=12, fill="#fff6e6", stroke="#b8860b")[0]
    f.append(b2)
    f.append(line(400, axy + 7, 400, 200, color="#b8860b", sw=1.3, dash="4 3"))

    # Віха 3 — 74181: увесь АЛП в одному корпусі
    f.append(circle(690, axy, 7, fill="#eafaf1", stroke=FIELD, sw=2))
    b3 = textbox(600, 78, "74181, Texas Instruments\nувесь 4-бітний АЛП\nна одній мікросхемі",
                 size=12, fill="#eafaf1", stroke=FIELD)[0]
    f.append(b3)
    f.append(line(690, axy - 7, 690, 108, color=FIELD, sw=1.3, dash="4 3"))

    f.append(text(W / 2, H - 16,
                  "поняття народилося як слово в звіті, а тілом стало аж через чверть століття",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'alu-history-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_block()
    fig_optable()
    fig_flags()
    fig_history()
    print("OK: alu-block, alu-optable, alu-flags, alu-history-timeline")
