# -*- coding: utf-8 -*-
"""Фігури до теми «Категорії значень: lvalue, prvalue, xvalue»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Дві незалежні властивості → три категорії ────────────────────────────
def fig_two_properties():
    W, H = 940, 410
    x0, y0 = 40, 62
    hw = 260          # ширина стовпця з підписами рядків
    cw = 310          # ширина клітинки
    hh = 66           # висота шапки
    rh = 124          # висота рядка

    f = []
    # шапка стовпців
    f.append(fitbox(x0 + hw, y0, cw, hh, "нутрощі ЗАБРАТИ можна",
                    size=15, bold=True, fill="#eef3fb"))
    f.append(fitbox(x0 + hw + cw, y0, cw, hh, "нутрощі забирати НЕ можна",
                    size=15, bold=True, fill="#eef3fb"))
    # підписи рядків
    f.append(fitbox(x0, y0 + hh, hw, rh,
                    "тотожність Є:\nце конкретне місце,\nдо якого можна повернутися",
                    size=13, bold=True, fill="#eef3fb"))
    f.append(fitbox(x0, y0 + hh + rh, hw, rh,
                    "тотожності НЕМАЄ:\nповертатися нема куди",
                    size=13, bold=True, fill="#eef3fb"))

    cells = [
        (0, 0, "xvalue", "std::move(s)", FIELD, "#eaf7ef"),
        (0, 1, "lvalue", "s", NEG, "#eaf0fd"),
        (1, 0, "prvalue", "s + \"!\"", POS, "#fdecea"),
        (1, 1, None, "такої потреби немає", MUTED, "#f4f6f8"),
    ]
    for r, c, name, sample, col, bg in cells:
        cx = x0 + hw + c * cw + cw / 2.0
        cy = y0 + hh + r * rh + rh / 2.0
        f.append(rect(x0 + hw + c * cw, y0 + hh + r * rh, cw, rh, fill=bg))
        if name:
            f.append(text(cx, cy - 6, name, size=23, color=col, bold=True))
            f.append(text(cx, cy + 26, sample, size=15, color=MUTED))
        else:
            f.append(text(cx, cy + 6, sample, size=15, color=MUTED))

    return render(os.path.join(IMG, 'two-properties.svg'), W, H, *f,
                  title="Дві незалежні властивості виразу дають три категорії")


# ── 2. Дерево категорій ─────────────────────────────────────────────────────
def fig_taxonomy():
    W, H = 940, 372
    f = []

    def node(cx, cy, lines, col=INK, bg=FILL):
        frag, w, h = textbox(cx, cy, lines, size=14, fill=bg, stroke=col,
                             sw=2, pad=12)
        return frag, w, h

    root, rw, rh = node(470, 66, ["будь-який вираз"])
    gl, gw, gh = node(270, 172, ["glvalue", "тотожність є"], NEG, "#eaf0fd")
    rv, vw, vh = node(680, 172, ["rvalue", "нутрощі можна забрати"], POS, "#fdecea")
    lv, lw, lh = node(140, 296, ["lvalue", "тотожність є,", "грабунку немає"], NEG, "#eaf0fd")
    xv, xw, xh = node(470, 296, ["xvalue", "тотожність є,", "грабунок дозволено"], FIELD, "#eaf7ef")
    pv, pw, ph = node(790, 296, ["prvalue", "тотожності немає,", "грабунок дозволено"], POS, "#fdecea")

    f += [line(470, 66 + rh / 2, 270, 172 - gh / 2, color=MUTED),
          line(470, 66 + rh / 2, 680, 172 - vh / 2, color=MUTED),
          line(270, 172 + gh / 2, 140, 296 - lh / 2, color=NEG),
          line(270, 172 + gh / 2, 434, 296 - xh / 2, color=NEG),
          line(680, 172 + vh / 2, 506, 296 - xh / 2, color=POS),
          line(680, 172 + vh / 2, 790, 296 - ph / 2, color=POS)]
    f += [root, gl, rv, lv, xv, pv]

    return render(os.path.join(IMG, 'taxonomy-tree.svg'), W, H, *f,
                  title="xvalue належить одразу двом збірним категоріям")


# ── 3. Шлях prvalue у C++17 ─────────────────────────────────────────────────
def fig_materialization():
    W, H = 940, 402
    f = []

    f.append(fitbox(30, 152, 240, 116,
                    "make()\n\nprvalue —\nрецепт ініціалізації,\nа не об'єкт",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=2))

    f.append(fitbox(330, 66, 250, 88,
                    "контекст:\nT x = make();",
                    size=15, fill="#f4f6f8"))
    f.append(fitbox(640, 66, 270, 88,
                    "x ініціалізовано напряму;\nтимчасовий об'єкт\nне виникає взагалі",
                    size=14, fill="#eaf0fd", stroke=NEG, sw=2))

    f.append(fitbox(330, 262, 250, 88,
                    "контекст:\nconst T& r = make();",
                    size=15, fill="#f4f6f8"))
    f.append(fitbox(640, 262, 270, 88,
                    "матеріалізація:\nоб'єкт таки виникає —\nі це вже xvalue",
                    size=14, fill="#eaf7ef", stroke=FIELD, sw=2))

    f += [arrow(276, 190, 326, 120, color=MUTED),
          arrow(276, 230, 326, 296, color=MUTED),
          arrow(586, 110, 636, 110, color=MUTED),
          arrow(586, 306, 636, 306, color=MUTED)]

    return render(os.path.join(IMG, 'prvalue-materialization.svg'), W, H, *f,
                  title="Об'єкт виникає лише там, де його справді треба")


# ── 4. Хронологія термінів (вставка hist) ───────────────────────────────────
def fig_terms_timeline():
    W, H = 960, 330
    axis_y = 112
    f = []

    stations = [
        ("1963", "CPL · Крістофер Стрейчі\n\nL-режим дає місце,\nR-режим дає вміст —\nдва способи обчислити\nодин вираз", "#eaf0fd", NEG),
        ("1978", "C · Денніс Річі\n\nлишилося одне слово:\nlvalue проти\n«не lvalue»", "#f4f6f8", MUTED),
        ("2002", "N1377 · Гіннант,\nДімов, Абрагамс\n\nтреба відрізнити\nприречений об'єкт\nвід живого", "#fdecea", POS),
        ("2010", "N3055 · Міллер\nзаписка Струструпа\n\nвластивості i та m\nдають lvalue, xvalue,\nprvalue", "#eaf7ef", FIELD),
        ("2016", "P0135 · Річард Сміт\n\nprvalue — рецепт\nініціалізації,\nа не об'єкт", "#eaf0fd", NEG),
    ]

    bw, bh, by = 176, 152, 152
    xs = [30 + i * 184 for i in range(5)]

    f.append(line(30, axis_y, 924, axis_y, color=MUTED, sw=2))
    f.append(arrow(900, axis_y, 936, axis_y, color=MUTED))

    for (year, body, bg, col), x in zip(stations, xs):
        cx = x + bw / 2.0
        f.append(text(cx, 74, year, size=21, color=col, bold=True))
        f.append(line(cx, axis_y - 8, cx, axis_y + 8, color=col, sw=3))
        f.append(fitbox(x, by, bw, bh, body, size=12, fill=bg, stroke=col, sw=2))

    return render(os.path.join(IMG, 'terms-timeline.svg'), W, H, *f,
                  title="П'ять кроків, якими виріс словник категорій значень")


# ── 5. Чому функція не годиться (вставка proj) ──────────────────────────────
def fig_function_collapse():
    W, H = 960, 452
    f = []

    calls = [
        (55, "probe(s)\n\nаргумент — lvalue", "#eaf0fd", NEG),
        (150, "probe(std::move(s))\n\nаргумент — xvalue", "#eaf7ef", FIELD),
        (245, "probe(make())\n\nаргумент — prvalue", "#fdecea", POS),
    ]
    for y, body, bg, col in calls:
        f.append(fitbox(30, y, 250, 76, body, size=13, fill=bg, stroke=col, sw=2))

    f.append(fitbox(352, 108, 226, 160,
                    "template <class T>\nvoid probe(T&& p);\n\nвиведення T\nна місці виклику",
                    size=13, fill="#f4f6f8", stroke=MUTED, sw=2))

    f.append(fitbox(660, 62, 270, 92,
                    "T = std::string&\n\nlvalue ще видно",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(fitbox(660, 216, 270, 118,
                    "T = std::string\n\nсюди злилися xvalue і prvalue —\nрозрізнити вже нічим",
                    size=13, fill="#f4f6f8", stroke=POS, sw=2))

    f += [arrow(286, 93, 346, 150, color=MUTED),
          arrow(286, 188, 346, 188, color=MUTED),
          arrow(286, 283, 346, 228, color=MUTED),
          arrow(584, 150, 654, 112, color=MUTED),
          arrow(584, 228, 654, 268, color=MUTED)]

    f.append(fitbox(30, 358, 900, 66,
                    "а сам параметр p усередині функції — завжди lvalue: у нього є ім'я.\n"
                    "Тому функція не може ані виміряти категорію, ані зберегти її.",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=2))

    return render(os.path.join(IMG, 'function-collapse.svg'), W, H, *f,
                  title="Виклик функції стирає різницю між xvalue і prvalue")


# ── 6. Дві оптики: компіляційна і рантаймова (вставка proj) ─────────────────
def fig_two_instruments():
    W, H = 960, 456
    f = []

    cols = [
        (30, "VALUE_CATEGORY(expr)\nмірять на етапі компіляції", NEG, "#eaf0fd",
         "категорію виразу:\nlvalue · xvalue · prvalue\n"
         "константність, що вимикає переміщення\n"
         "нічого не виконує — навіть\nділення на нуль безпечне",
         "який конструктор справді спрацював\nчи була копія, чи не була"),
        (490, "тип, що кричить у конструкторах\nмірять на етапі виконання", FIELD, "#eaf7ef",
         "який конструктор викликано\nскільки разів скопійовано\nчи спрацювало усунення копій",
         "категорію виразу, з якого\nнічого не будують\nвідповідь коштує запуску програми"),
    ]
    for x, head, col, bg, sees, blind in cols:
        f.append(fitbox(x, 34, 440, 66, head, size=14, bold=True, fill=bg, stroke=col, sw=2))
        f.append(fitbox(x, 118, 440, 140, "БАЧИТЬ\n\n" + sees, size=13, fill="#ffffff",
                        stroke=col, sw=2))
        f.append(fitbox(x, 274, 440, 104, "НЕ БАЧИТЬ\n\n" + blind, size=13, fill="#f4f6f8",
                        stroke=MUTED, sw=2))

    f.append(fitbox(30, 396, 900, 48,
                    "категорія — намір виразу, конструктор — наслідок: питання різні, отже й приладів два",
                    size=14, bold=True, fill="#f4f6f8", stroke=INK, sw=2))

    return render(os.path.join(IMG, 'two-instruments.svg'), W, H, *f,
                  title="Два прилади відповідають на два різні питання")


if __name__ == '__main__':
    for fn in (fig_two_properties, fig_taxonomy, fig_materialization,
               fig_terms_timeline, fig_function_collapse, fig_two_instruments):
        print(fn())
