# -*- coding: utf-8 -*-
"""Фігури до теми «Володіння в сигнатурі: що означає тип параметра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Два питання розділяють словник форм ─────────────────────────────────
def fig_two_questions():
    W, H = 980, 440
    f = []

    f.append(fitbox(340, 22, 300, 48,
                    "Чи потрібен об'єкт функції\nпісля повернення?", size=13, bold=True))
    f.append(arrow(430, 72, 258, 112))
    f.append(arrow(550, 72, 722, 112))

    f.append(rect(40, 112, 430, 272, fill=BG))
    f.append(rect(510, 112, 430, 272, fill=BG))

    f.append(text(255, 138, "НІ — позичання: власник лишається один",
                  size=13, color=NEG, bold=True))
    f.append(text(725, 138, "ТАК — володіння: функції потрібна гарантія",
                  size=13, color=FIELD, bold=True))

    left = [
        "const T&   —  читати, не змінюючи",
        "T&   —  змінити об'єкт викликача",
        "T*   —  те саме, «нічого» дозволене",
        "дешеве значення, string_view, span",
    ]
    right = [
        "T за значенням  —  власний об'єкт",
        "T&&   —  забрати нутрощі приреченого",
        "unique_ptr<T>  —  володіння переходить",
        "shared_ptr<T>  —  функція співвласник",
    ]
    for i, s in enumerate(left):
        f.append(fitbox(56, 154 + i * 56, 398, 44, s, size=13))
    for i, s in enumerate(right):
        f.append(fitbox(526, 154 + i * 56, 398, 44, s, size=13))

    f.append(text(490, 414,
                  "Питання «чи змінюємо чуже» розрізняє лише ліву колонку: володіючи, функція змінює вже своє.",
                  size=11, color=MUTED))

    return render(os.path.join(OUT, 'two-questions.svg'), W, H, *f)


# ── 2. Три режими на осі часу ──────────────────────────────────────────────
def fig_lifetime_lanes():
    W, H = 980, 430
    f = []

    # межі виклику
    f.append(line(380, 66, 380, 348, color=MUTED, sw=1.2, dash="6 5"))
    f.append(line(664, 66, 664, 348, color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(380, 54, "виклик", size=12, color=MUTED))
    f.append(text(664, 54, "повернення", size=12, color=MUTED))

    lanes = [
        (96,  "позичання\nconst T&"),
        (196, "передача\nunique_ptr<T>"),
        (296, "спільне\nshared_ptr<T>"),
    ]
    for y, name in lanes:
        f.append(fitbox(16, y, 118, 44, name, size=11, fill=BG, stroke=MUTED))

    # 1: власник не міняється
    f.append(fitbox(150, 96, 730, 44, "власник — викликач увесь час", size=13))

    # 2: власник міняється рівно на виклику
    f.append(fitbox(150, 196, 222, 44, "власник — викликач", size=12))
    f.append(fitbox(388, 196, 492, 44, "власник — функція та її наступники", size=12))

    # 3: перекриття власників
    f.append(fitbox(150, 296, 222, 44, "1 власник", size=12))
    f.append(fitbox(388, 296, 268, 44, "2 власники, лічильник = 2", size=12,
                    fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(672, 296, 208, 44, "1 власник", size=12))

    f.append(text(490, 400,
                  "Об'єкт живий, поки живий останній власник; тип параметра каже, чи їх стає більше.",
                  size=11, color=MUTED))

    return render(os.path.join(OUT, 'lifetime-lanes.svg'), W, H, *f)


# ── 3. Пастка const shared_ptr& ────────────────────────────────────────────
def fig_refcount_trap():
    W, H = 940, 396
    f = []

    f.append(rect(30, 56, 425, 250, fill=BG))
    f.append(rect(485, 56, 425, 250, fill=BG))

    f.append(text(242, 40, "const shared_ptr<Widget>&", size=13, bold=True, color=POS))
    f.append(text(697, 40, "shared_ptr<Widget> за значенням", size=13, bold=True, color=FIELD))

    f.append(fitbox(52, 74, 381, 40, "вхід у функцію: лічильник = 1", size=12))
    f.append(fitbox(507, 74, 381, 40, "вхід у функцію: лічильник = 2", size=12))

    f.append(arrow(242, 118, 242, 146))
    f.append(arrow(697, 118, 697, 146))

    f.append(fitbox(52, 150, 381, 44,
                    "усередині виклику викликач\nскидає свій вказівник", size=12))
    f.append(fitbox(507, 150, 381, 44,
                    "усередині виклику викликач\nскидає свій вказівник", size=12))

    f.append(arrow(242, 198, 242, 226))
    f.append(arrow(697, 198, 697, 226))

    f.append(fitbox(52, 230, 381, 54,
                    "лічильник → 0, об'єкт знищено;\nпараметр указує в нікуди", size=12,
                    fill="#fdecea", stroke=POS))
    f.append(fitbox(507, 230, 381, 54,
                    "лічильник → 1, об'єкт живий;\nфункція дограє до кінця", size=12,
                    fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 344,
                  "Один атомарний інкремент — це не накладні витрати, а куплена гарантія життя.",
                  size=11, color=MUTED))

    return render(os.path.join(OUT, 'refcount-trap.svg'), W, H, *f)


# ── 4. Порядок кроків переписування і хвиля помилок ────────────────────────
def fig_refactor_order():
    W, H = 1000, 438
    f = []

    cols = [(24, 176), (212, 416), (648, 328)]
    heads = ["крок переписування", "що перестає збиратися", "що саме це виявляє"]
    for (x, w), h in zip(cols, heads):
        f.append(text(x + w / 2, 34, h, size=12, color=MUTED, bold=True))

    rows = [
        ("1. повернення\nфабрики",
         "Codec* c = make_codec(\"h264\");\nfree_codec(c);",
         "усі місця, що вважали\nсебе власниками кодека"),
        ("2. явні\nприймачі",
         "set_sink(c, new FileSink(path));\nset_sink(c, &sink_on_stack);",
         "справжня помилка: звільнення\nоб'єкта зі стека"),
        ("3. співволодіння\nтам, де воно є",
         "submit(c.get(), &frame);",
         "місця, де об'єкт мусить\nпережити виклик"),
        ("4. позичання",
         "probe(c.get(), &frame);   // сотні рядків",
         "нічого нового — заміна\nмеханічна, тому остання"),
    ]

    y = 54
    for step, breaks, reveals in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], 72, step, size=12, bold=True))
        f.append(fitbox(cols[1][0], y, cols[1][1], 72, breaks, size=12,
                        fill="#fdecea", stroke=POS))
        f.append(fitbox(cols[2][0], y, cols[2][1], 72, reveals, size=12,
                        fill="#e8f6ee", stroke=FIELD))
        y += 84

    f.append(text(500, 412,
                  "Кожна помилка збирання — рядок, у якому досі жило неперевірене припущення про час життя.",
                  size=11, color=MUTED))

    return render(os.path.join(OUT, 'refactor-order.svg'), W, H, *f)


if __name__ == '__main__':
    for fn in (fig_two_questions, fig_lifetime_lanes, fig_refcount_trap,
               fig_refactor_order):
        print(fn())
