# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_call_strategies():
    W, H = 840, 440
    p = []

    col_w = 244
    gap = 24
    start_x = 30
    y_top = 64
    card_h = 326

    strategies = [
        ("Call-by-Value (Строге)",
         "Аплікативний порядок",
         [
             "Аргументи рахуються ДО виклику",
             "Простий стек і передбачуваний час",
             "Зайва робота, якщо аргумент не треба",
             "Падає на ⊥, навіть якщо аргумент оминули"
         ],
         "f(2+3, loop())  →  ЗАВИСАЄ",
         NEG, "#eaf0fd"),

        ("Call-by-Name (За ім'ям)",
         "Нормальний порядок (дерево)",
         [
             "Вираз підставляється нерозкритим",
             "Не використано → 0 обчислень",
             "Безпечно оминає ⊥ у невикористаному",
             "Повторює обчислення за кожним зверненням"
         ],
         "sq(2+3)  →  (2+3)*(2+3)  (2 рази)",
         POS, "#fdecea"),

        ("Call-by-Need (Ліниве)",
         "Редукція графа (спільне)",
         [
             "Вираз підставляється як санк (Thunk)",
             "Рахується під час першого читання",
             "Результат мутує граф (мемоізація)",
             "Наступні звернення читають готове (1 раз)"
         ],
         "sq(thunk)  →  5 * 5 = 25  (1 раз)",
         FIELD, "#eef6ef"),
    ]

    for i, (title_text, subtitle, points, formula, col, fill_col) in enumerate(strategies):
        x = start_x + i * (col_w + gap)
        p.append(rect(x, y_top, col_w, card_h, fill=fill_col, stroke=col, sw=1.8, rx=12))
        p.append(text(x + col_w / 2, y_top + 24, title_text, size=12.5, color=col, bold=True))
        p.append(text(x + col_w / 2, y_top + 44, subtitle, size=10, color=MUTED, italic=True))
        p.append(line(x + 16, y_top + 56, x + col_w - 16, y_top + 56, color=col, sw=1, dash="4 3"))

        py = y_top + 80
        for pt in points:
            p.append(fitbox(x + 12, py, col_w - 24, 42, pt, size=10, fill=BG, stroke=col, sw=1, color=INK))
            py += 48

        p.append(rect(x + 12, y_top + card_h - 48, col_w - 24, 34, fill=BG, stroke=col, sw=1.4, rx=6))
        p.append(text(x + col_w / 2, y_top + card_h - 26, formula, size=10, color=col, bold=True))

    p.append(text(W / 2, H - 16,
                  "Call-by-need поєднує безпеку нормального порядку з ефективністю однократного обчислення",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "call-strategies.svg"), W, H, *p,
           title="Порівняння стратегій: Call-by-Value, Call-by-Name та Call-by-Need")


def fig_thunk_lifecycle():
    W, H = 840, 420
    p = []

    box_w = 220
    box_h = 240
    y_box = 80
    xs = [35, 310, 585]

    # Стан 1: Thunk
    p.append(rect(xs[0], y_box, box_w, box_h, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=12))
    p.append(text(xs[0] + box_w / 2, y_box + 24, "1. Необчислений (Thunk)", size=11.5, color=NEG, bold=True))
    p.append(rect(xs[0] + 16, y_box + 44, box_w - 32, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(xs[0] + box_w / 2, y_box + 64, "info_ptr → eval_fn()", size=10.5, color=INK, bold=True))
    p.append(text(xs[0] + box_w / 2, y_box + 82, "вказівник на код", size=9, color=MUTED))

    p.append(rect(xs[0] + 16, y_box + 104, box_w - 32, 70, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(xs[0] + box_w / 2, y_box + 124, "Захоплене оточення:", size=9.5, color=INK, bold=True))
    p.append(text(xs[0] + box_w / 2, y_box + 142, "arg1 = 2, arg2 = 3", size=9.5, color=MUTED))
    p.append(text(xs[0] + box_w / 2, y_box + 160, "вільні змінні замикання", size=9.5, color=MUTED, italic=True))

    p.append(text(xs[0] + box_w / 2, y_box + 200, "Очікує першої вимоги", size=10, color=NEG, bold=True))
    p.append(text(xs[0] + box_w / 2, y_box + 220, "займає пам'ять у купі", size=9.5, color=MUTED))

    # Стрілка 1 -> 2
    p.append(arrow(xs[0] + box_w + 4, y_box + box_h / 2, xs[1] - 6, y_box + box_h / 2, color=INK, sw=2))
    p.append(text((xs[0] + box_w + xs[1]) / 2, y_box + box_h / 2 - 12, "force()", size=10, color=INK, bold=True))

    # Стан 2: Blackhole
    p.append(rect(xs[1], y_box, box_w, box_h, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    p.append(text(xs[1] + box_w / 2, y_box + 24, "2. В процесі (Blackhole)", size=11.5, color=POS, bold=True))
    p.append(rect(xs[1] + 16, y_box + 44, box_w - 32, 50, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(xs[1] + box_w / 2, y_box + 64, "info_ptr → BLACKHOLE", size=10, color=POS, bold=True))
    p.append(text(xs[1] + box_w / 2, y_box + 82, "пастка самовиклику", size=9.5, color=MUTED))

    p.append(rect(xs[1] + 16, y_box + 104, box_w - 32, 70, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(xs[1] + box_w / 2, y_box + 124, "Поточний потік рахує:", size=9.5, color=INK, bold=True))
    p.append(text(xs[1] + box_w / 2, y_box + 142, "2 + 3 = 5", size=10.5, color=POS, bold=True))
    p.append(text(xs[1] + box_w / 2, y_box + 160, "виявляє ⊥ (цикли) і блокує", size=9.5, color=MUTED, italic=True))

    p.append(text(xs[1] + box_w / 2, y_box + 200, "Захист від гонок і циклів", size=10, color=POS, bold=True))
    p.append(text(xs[1] + box_w / 2, y_box + 220, "оточення можна звільнити", size=9.5, color=MUTED))

    # Стрілка 2 -> 3
    p.append(arrow(xs[1] + box_w + 4, y_box + box_h / 2, xs[2] - 6, y_box + box_h / 2, color=INK, sw=2))
    p.append(text((xs[1] + box_w + xs[2]) / 2, y_box + box_h / 2 - 12, "update", size=10, color=FIELD, bold=True))

    # Стан 3: Evaluated Value
    p.append(rect(xs[2], y_box, box_w, box_h, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(xs[2] + box_w / 2, y_box + 24, "3. Обчислений (Значення)", size=11.5, color=FIELD, bold=True))
    p.append(rect(xs[2] + 16, y_box + 44, box_w - 32, 50, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(xs[2] + box_w / 2, y_box + 64, "info_ptr → INT_VAL", size=10.5, color=FIELD, bold=True))
    p.append(text(xs[2] + box_w / 2, y_box + 82, "прямий доступ без коду", size=9.5, color=MUTED))

    p.append(rect(xs[2] + 16, y_box + 104, box_w - 32, 70, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(xs[2] + box_w / 2, y_box + 124, "Збережене значення:", size=9.5, color=INK, bold=True))
    p.append(text(xs[2] + box_w / 2, y_box + 144, "value = 5", size=12, color=FIELD, bold=True))
    p.append(text(xs[2] + box_w / 2, y_box + 162, "оточення повністю очищене", size=9.5, color=MUTED, italic=True))

    p.append(text(xs[2] + box_w / 2, y_box + 200, "Вузол графа мутовано", size=10, color=FIELD, bold=True))
    p.append(text(xs[2] + box_w / 2, y_box + 220, "наступні виклики миттєві", size=9, color=MUTED))

    p.append(text(W / 2, H - 24,
                  "Редукція графа мутує вузол санка на місці: код замінюється готовим значенням",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "thunk-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл санка (Thunk) та мутація вузла графа")


def fig_whnf_vs_nf():
    W, H = 840, 400
    p = []

    half_w = 370
    lx = 35
    rx = 435
    y_top = 66
    h_block = 276

    # Ліворуч: WHNF
    p.append(rect(lx, y_top, half_w, h_block, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=12))
    p.append(text(lx + half_w / 2, y_top + 26, "WHNF (Weak Head Normal Form)", size=12, color=NEG, bold=True))
    p.append(text(lx + half_w / 2, y_top + 46, "Розкрито ЛИШЕ верхній конструктор", size=10, color=MUTED, italic=True))

    p.append(rect(lx + 24, y_top + 66, half_w - 48, 54, fill=BG, stroke=NEG, sw=1.4, rx=8))
    p.append(text(lx + half_w / 2, y_top + 88, "Конструктор списку (:)", size=11, color=NEG, bold=True))
    p.append(text(lx + half_w / 2, y_top + 106, "голова і хвіст лишаються санками", size=9, color=MUTED))

    p.append(arrow(lx + 100, y_top + 120, lx + 70, y_top + 154, color=NEG, sw=1.6))
    p.append(arrow(lx + 270, y_top + 120, lx + 300, y_top + 154, color=NEG, sw=1.6))

    p.append(rect(lx + 20, y_top + 154, 130, 48, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(lx + 85, y_top + 174, "head: Thunk", size=10, color=POS, bold=True))
    p.append(text(lx + 85, y_top + 190, "(1 + 2)", size=9.5, color=MUTED))

    p.append(rect(lx + 220, y_top + 154, 130, 48, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(lx + 285, y_top + 174, "tail: Thunk", size=10, color=POS, bold=True))
    p.append(text(lx + 285, y_top + 190, "map f [4, 5]", size=9.5, color=MUTED))

    p.append(fitbox(lx + 20, y_top + 218, half_w - 40, 44,
                    "Форсується зіставленням зі зразком (pattern match) або функцією seq",
                    size=9.5, fill=BG, stroke=NEG, sw=1, color=INK))

    # Праворуч: NF
    p.append(rect(rx, y_top, half_w, h_block, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(rx + half_w / 2, y_top + 26, "NF (Normal Form — Повна форма)", size=12, color=FIELD, bold=True))
    p.append(text(rx + half_w / 2, y_top + 46, "Усі рівні обчислено до чистих значень", size=10, color=MUTED, italic=True))

    p.append(rect(rx + 24, y_top + 66, half_w - 48, 54, fill=BG, stroke=FIELD, sw=1.4, rx=8))
    p.append(text(rx + half_w / 2, y_top + 88, "Конструктор списку (:)", size=11, color=FIELD, bold=True))
    p.append(text(rx + half_w / 2, y_top + 106, "усі елементи повністю розгорнуті", size=9, color=MUTED))

    p.append(arrow(rx + 100, y_top + 120, rx + 70, y_top + 154, color=FIELD, sw=1.6))
    p.append(arrow(rx + 270, y_top + 120, rx + 300, y_top + 154, color=FIELD, sw=1.6))

    p.append(rect(rx + 20, y_top + 154, 130, 48, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(rx + 85, y_top + 174, "head = 3", size=11, color=FIELD, bold=True))
    p.append(text(rx + 85, y_top + 190, "числове значення", size=9, color=MUTED))

    p.append(rect(rx + 220, y_top + 154, 130, 48, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(rx + 285, y_top + 174, "tail = [8, 10]", size=11, color=FIELD, bold=True))
    p.append(text(rx + 285, y_top + 190, "повністю обчислений", size=9, color=MUTED))

    p.append(fitbox(rx + 20, y_top + 218, half_w - 40, 44,
                    "Потребує глибокого форсування: deepseq / NFData або виводу всього результату",
                    size=9.5, fill=BG, stroke=FIELD, sw=1, color=INK))

    p.append(text(W / 2, H - 18,
                  "Лінива мова за замовчуванням обчислює лише до WHNF — рівно стільки, щоб розпізнати конструктор",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "whnf-vs-nf.svg"), W, H, *p,
           title="Рівні редукції: слабка головна нормальна форма проти повної")


def fig_space_leak_chain():
    W, H = 840, 430
    p = []

    half_w = 370
    lx = 35
    rx = 435
    y_top = 66
    h_block = 308

    # Ліворуч: Небезпечний лінивий акумулятор (foldl)
    p.append(rect(lx, y_top, half_w, h_block, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    p.append(text(lx + half_w / 2, y_top + 24, "Лінивий foldl (+) 0 [1..N]", size=11.5, color=POS, bold=True))
    p.append(text(lx + half_w / 2, y_top + 42, "Ланцюг невиконаних санків росте в купі", size=9.5, color=POS))

    chain_items = [
        ("Thunk 4: (((0 + 1) + 2) + 3) + 4", 62),
        ("Thunk 3: ((0 + 1) + 2) + 3", 108),
        ("Thunk 2: (0 + 1) + 2", 154),
        ("Thunk 1: 0 + 1", 200),
    ]
    for label, cy in chain_items:
        p.append(rect(lx + 20, y_top + cy, half_w - 40, 36, fill=BG, stroke=POS, sw=1.2, rx=6))
        p.append(text(lx + half_w / 2, y_top + cy + 22, label, size=10, color=INK, bold=True))

    p.append(rect(lx + 20, y_top + 246, half_w - 40, 48, fill="#f9d7d3", stroke=POS, sw=1.4, rx=6))
    p.append(text(lx + half_w / 2, y_top + 266, "Пам'ять: O(N) у купі", size=10.5, color=POS, bold=True))
    p.append(text(lx + half_w / 2, y_top + 284, "При читанні: переповнення стека!", size=9.5, color=POS, bold=True))

    # Праворуч: Строгий акумулятор (foldl')
    p.append(rect(rx, y_top, half_w, h_block, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(rx + half_w / 2, y_top + 24, "Строгий foldl' (+) 0 [1..N]", size=11.5, color=FIELD, bold=True))
    p.append(text(rx + half_w / 2, y_top + 42, "Акумулятор обчислюється на кожному кроці", size=9.5, color=FIELD))

    steps = [
        ("Крок 1: acc = 0 + 1  →  1", 62),
        ("Крок 2: acc = 1 + 2  →  3", 108),
        ("Крок 3: acc = 3 + 3  →  6", 154),
        ("Крок 4: acc = 6 + 4  →  10", 200),
    ]
    for label, cy in steps:
        p.append(rect(rx + 20, y_top + cy, half_w - 40, 36, fill=BG, stroke=FIELD, sw=1.2, rx=6))
        p.append(text(rx + half_w / 2, y_top + cy + 22, label, size=10, color=INK, bold=True))

    p.append(rect(rx + 20, y_top + 246, half_w - 40, 48, fill="#d5f0df", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(rx + half_w / 2, y_top + 266, "Пам'ять: O(1) у регістрі/стеку", size=10.5, color=FIELD, bold=True))
    p.append(text(rx + half_w / 2, y_top + 284, "Жодних санків у купі та переповнення", size=9.5, color=FIELD, bold=True))

    p.append(text(W / 2, H - 18,
                  "Витік пам'яті через санки: накопичення відкладеної роботи замість швидкого обчислення",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "space-leak-chain.svg"), W, H, *p,
           title="Витік пам'яті (Space Leak): накопичення ланцюгів санків")


def fig_knot_tying():
    W, H = 840, 380
    p = []

    p.append(rect(40, 64, W - 80, 52, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=8))
    p.append(text(W / 2, 86, 'let ones = 1 : ones', size=13, color=INK, bold=True))
    p.append(text(W / 2, 105, 'нескінченний список одиниць без мутацій на рівні мови', size=10, color=MUTED, italic=True))

    cx, cy = W / 2, 220
    cell_w, cell_h = 240, 80

    p.append(rect(cx - cell_w / 2, cy - cell_h / 2, cell_w, cell_h, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    p.append(line(cx, cy - cell_h / 2, cx, cy + cell_h / 2, color=FIELD, sw=1.8))

    p.append(text(cx - cell_w / 4, cy - 12, "head", size=11, color=MUTED))
    p.append(text(cx - cell_w / 4, cy + 16, "1", size=18, color=FIELD, bold=True))

    p.append(text(cx + cell_w / 4, cy - 12, "tail (next)", size=11, color=MUTED))
    p.append(circle(cx + cell_w / 4, cy + 14, 6, fill=FIELD, stroke=FIELD, sw=1))

    loop_path = ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (cx + cell_w / 4, cy + 8,
                    cx + cell_w / 2 + 70, cy - 90,
                    cx - cell_w / 2 - 70, cy - 90,
                    cx - cell_w / 2 - 4, cy, FIELD))
    p.append(loop_path)

    p.append(rect(cx - 150, cy - 100, 300, 30, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(cx, cy - 80, "вказівник tail посилається на саму Cons-комірку", size=10, color=FIELD, bold=True))

    p.append(fitbox(50, cy + 62, W - 100, 44,
                    "Зав'язування вузла (Knot Tying): нескінченна структура займає O(1) пам'яті (1 комірку) завдяки замкненому графу",
                    size=10.5, fill=BG, stroke=FIELD, sw=1.2, color=INK, bold=True))

    render(os.path.join(OUT, "knot-tying.svg"), W, H, *p,
           title="Зав'язування вузла: нескінченний список у фіксованій пам'яті")


if __name__ == "__main__":
    fig_call_strategies()
    fig_thunk_lifecycle()
    fig_whnf_vs_nf()
    fig_space_leak_chain()
    fig_knot_tying()
    print("OK: all figures generated")
