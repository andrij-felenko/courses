# -*- coding: utf-8 -*-
"""Фігури до теми «Посилання і правила зв'язування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_alias_vs_pointer():
    W, H = 920, 430
    f = []
    # ── дві панелі ─────────────────────────────────────────────────────────
    f.append(rect(30, 50, 420, 345, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(rect(480, 50, 410, 345, fill="#ffffff", stroke=MUTED, sw=1.2))

    # ── ліва панель: посилання ─────────────────────────────────────────────
    f.append(text(240, 82, "int x = 7;   int& r = x;", size=15, bold=True))
    f.append(textbox(160, 140, "x", size=17, bold=True, min_w=60)[0])
    f.append(textbox(320, 140, "r", size=17, bold=True, min_w=60)[0])
    f.append(arrow(160, 164, 206, 220))
    f.append(arrow(320, 164, 274, 220))
    f.append(rect(190, 226, 100, 66, fill="#eef3f8"))
    f.append(text(240, 268, "7", size=24, bold=True))
    f.append(text(240, 320, "одна комірка", size=13, color=MUTED))
    f.append(mtext(240, 352, ["r не має власної адреси:",
                              "&r збігається з &x"], size=13, color=MUTED))

    # ── права панель: покажчик ─────────────────────────────────────────────
    f.append(text(685, 82, "int x = 7;   int* p = &x;", size=15, bold=True))
    f.append(textbox(570, 140, "x", size=17, bold=True, min_w=60)[0])
    f.append(textbox(810, 140, "p", size=17, bold=True, min_w=60)[0])
    f.append(arrow(570, 164, 570, 220))
    f.append(arrow(810, 164, 810, 220))
    f.append(rect(520, 226, 100, 66, fill="#eef3f8"))
    f.append(text(570, 268, "7", size=24, bold=True))
    f.append(rect(760, 226, 100, 66, fill="#eef3f8"))
    f.append(text(810, 268, "&x", size=19, bold=True))
    f.append(arrow(752, 259, 628, 259, color=NEG))
    f.append(text(685, 320, "дві комірки", size=13, color=MUTED))
    f.append(mtext(685, 352, ["p — самостійний об'єкт зі своєю адресою;",
                              "його можна перенацілити"], size=13, color=MUTED))

    render(os.path.join(OUT, 'alias-vs-pointer.svg'), W, H, *f,
           title="Посилання — друге ім'я комірки; покажчик — окрема комірка")


def fig_binding_matrix():
    W, H = 980, 410
    x0, y0 = 30, 62
    lw, cw = 300, 155
    hh, rh = 54, 56
    cols = ["T&", "const T&", "T&&", "const T&&"]
    rows = [
        ("змінний lvalue",       ["+", "+", "-", "-"]),
        ("const lvalue",         ["-", "+", "-", "-"]),
        ("rvalue (тимчасовий)",  ["-", "+", "+", "+"]),
        ("const rvalue",         ["-", "+", "-", "+"]),
    ]
    f = []
    f.append(fitbox(x0, y0, lw, hh, "ініціалізатор  \\  рід посилання",
                    size=13, color=MUTED, fill="#ffffff"))
    for j, c in enumerate(cols):
        f.append(fitbox(x0 + lw + j * cw, y0, cw, hh, c, size=17,
                        bold=True, fill="#eef3f8"))
    for i, (name, marks) in enumerate(rows):
        y = y0 + hh + i * rh
        f.append(fitbox(x0, y, lw, rh, name, size=14, fill="#eef3f8"))
        for j, m in enumerate(marks):
            x = x0 + lw + j * cw
            f.append(rect(x, y, cw, rh, fill="#ffffff"))
            if m == "+":
                f.append(text(x + cw / 2, y + rh / 2 + 9, "✓", size=26,
                              color=FIELD, bold=True))
            else:
                f.append(text(x + cw / 2, y + rh / 2 + 9, "✗", size=26,
                              color=POS, bold=True))
    render(os.path.join(OUT, 'binding-matrix.svg'), W, H, *f,
           title="Що до чого прив'язується")


def fig_lifetime_extension():
    W, H = 940, 415
    f = []
    # ── випадок, де життя продовжується ────────────────────────────────────
    f.append(text(40, 90, "const Matrix& m = compute();", size=15,
                  bold=True, anchor="start"))
    f.append(rect(170, 118, 700, 36, fill="#e8f6ed", stroke=FIELD, sw=1.6))
    f.append(text(520, 141, "тимчасовий живе, доки живе m", size=14))
    f.append(line(60, 178, 900, 178, color=MUTED))
    f.append(line(170, 158, 170, 186, color=MUTED))
    f.append(line(870, 158, 870, 186, color=MUTED))
    f.append(text(170, 204, "створення", size=12, color=MUTED))
    f.append(text(880, 204, "кінець блоку", size=12, color=MUTED, anchor="end"))

    # ── випадок, де не продовжується ───────────────────────────────────────
    f.append(text(40, 262, "const Matrix& m = pass(compute());", size=15,
                  bold=True, anchor="start"))
    f.append(text(40, 285, "pass приймає const& і повертає те саме посилання",
                  size=12, color=MUTED, anchor="start"))
    f.append(rect(170, 302, 210, 36, fill="#e8f6ed", stroke=FIELD, sw=1.6))
    f.append(text(275, 325, "живий", size=13))
    f.append(rect(380, 302, 490, 36, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(625, 325, "m висить — звертання дає UB", size=13))
    f.append(line(60, 362, 900, 362, color=MUTED))
    f.append(line(170, 342, 170, 370, color=MUTED))
    f.append(line(380, 342, 380, 370, color=MUTED))
    f.append(text(150, 388, "створення", size=12, color=MUTED))
    f.append(text(420, 388, "кінець повного виразу «;»", size=12, color=MUTED))

    render(os.path.join(OUT, 'lifetime-extension.svg'), W, H, *f,
           title="Продовження життя діє лише при прямому зв'язуванні")


def fig_references_timeline():
    W, H = 1060, 340
    ys = 168                      # висота часової прямої
    xs = [105, 270, 435, 600, 765, 930]
    items = [
        ("1979", ["«C with Classes»: класи є,",
                  "посилань і операторів немає"]),
        ("1983-84", ["посилання й перевантаження",
                     "операторів; назва «C++»"]),
        ("1985", ["Cfront 1.0 і перше видання",
                  "«The C++ Programming Language»"]),
        ("2002", ["N1377: rvalue-посилання",
                  "й семантика переміщення"]),
        ("2009", ["N2844: T&& більше",
                  "не зв'язується з lvalue"]),
        ("2011", ["C++11: move і forward —",
                  "це лише static_cast"]),
    ]
    f = [line(60, ys, 1000, ys, color=MUTED, sw=2)]
    for i, (year, lines) in enumerate(items):
        x = xs[i]
        up = (i % 2 == 0)
        f.append(circle(x, ys, 8, fill="#eef3f8", stroke=MUTED, sw=2))
        if up:
            f.append(line(x, ys - 12, x, ys - 34, color=MUTED))
            f.append(text(x, ys - 44, year, size=16, bold=True))
            f.append(mtext(x, 62, lines, size=12, color=MUTED))
        else:
            f.append(line(x, ys + 12, x, ys + 34, color=MUTED))
            f.append(text(x, ys + 54, year, size=16, bold=True))
            f.append(mtext(x, ys + 84, lines, size=12, color=MUTED))
    render(os.path.join(OUT, 'references-timeline.svg'), W, H, *f,
           title="Дві хвилі змін у правилах зв'язування")


def fig_loop_materialization():
    """До вставки proj-binding-lab: що бачить kv у двох формах циклу."""
    W, H = 1000, 450
    f = []

    # ── смуга 1: власноруч виписаний тип елемента ──────────────────────────
    f.append(text(40, 64, "for (const std::pair<std::string, Loud>& kv : registry)",
                  size=15, bold=True, anchor="start"))
    f.append(textbox(215, 160, ["вузол мапи (живе в контейнері)",
                                "std::pair<const std::string, Loud>",
                                "«альфа» → Loud #8"], size=13)[0])
    f.append(mtext(460, 120, ["типи різні —", "матеріалізується тимчасовий"],
                   size=12, color=MUTED))
    f.append(arrow(360, 160, 605, 160, color=POS))
    f.append(textbox(760, 160, ["тимчасовий (гине наприкінці ітерації)",
                                "std::pair<std::string, Loud>",
                                "«альфа» → Loud #11 — КОПІЯ"],
                     size=13, fill="#fdecea", stroke=POS)[0])
    f.append(arrow(760, 222, 760, 200, color=POS))
    f.append(text(760, 243, "kv зв'язане ОСЬ ІЗ ЦИМ", size=13, bold=True, color=POS))

    f.append(line(40, 272, 960, 272, color=MUTED, dash="6 5"))

    # ── смуга 2: const auto& ───────────────────────────────────────────────
    f.append(text(40, 306, "for (const auto& kv : registry)",
                  size=15, bold=True, anchor="start"))
    f.append(textbox(215, 375, ["вузол мапи (живе в контейнері)",
                                "std::pair<const std::string, Loud>",
                                "«альфа» → Loud #8"], size=13,
                     fill="#e8f6ed", stroke=FIELD)[0])
    f.append(arrow(515, 375, 358, 375, color=FIELD))
    f.append(text(548, 380, "kv", size=15, bold=True, anchor="start"))
    f.append(mtext(790, 362, ["нічого не створюється:",
                              "kv — друге ім'я самого вузла"], size=13, color=MUTED))

    render(os.path.join(OUT, 'loop-materialization.svg'), W, H, *f,
           title="Той самий цикл: із копією на ітерацію і без неї")


if __name__ == '__main__':
    fig_alias_vs_pointer()
    fig_binding_matrix()
    fig_lifetime_extension()
    fig_references_timeline()
    fig_loop_materialization()
    print("ok")
