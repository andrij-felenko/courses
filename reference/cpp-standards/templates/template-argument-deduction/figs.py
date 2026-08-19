# -*- coding: utf-8 -*-
"""Фігури до теми «Виведення аргументів шаблону (Template Argument Deduction)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_deduction_contexts():
    """Порівняння трьох контекстів виведення аргументів шаблону."""
    W = 1040
    M = 20
    head = ["Контекст передачі", "Шаблон параметра", "Поведінка трансформації типу", "Приклад виведення типу"]
    cols = [220, 240, 300, 240]
    rows = [
        ["За значенням\n(Pass-by-value)",
         "template<typename T>\nvoid f(T x);",
         "Відкидання top-level const/volatile.\nМасиви та функції розпадаються\nу сирі вказівники (type decay).",
         "const int a = 5;  ⇒ T = int\nint arr[10];      ⇒ T = int*\nvoid fn();        ⇒ T = void(*)()"],
        ["За lvalue-посиланням\n(Pass-by-reference)",
         "template<typename T>\nvoid f(T& x);\nvoid g(const T& x);",
         "Посилання в аргументі ігнорується.\nКонстантність зберігається.\nМасиви зберігають точний розмір.",
         "const int a = 5;  ⇒ T = const int\nint arr[10];      ⇒ T = int[10]\n                   (x: int(&)[10])"],
        ["Передавальне посилання\n(Forwarding Reference)",
         "template<typename T>\nvoid f(T&& x);",
         "lvalue виводить T як посилання T&.\nrvalue виводить T як не-посилання T.\nСпрацьовує згортання посилань.",
         "int a = 5;\nf(a);   ⇒ T = int&  ⇒ x: int&\nf(10);  ⇒ T = int   ⇒ x: int&&"]
    ]
    HH, RH, GAP = 52, 96, 6
    H = 40 + HH + len(rows) * RH + 24
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 40, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 40 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=12, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'deduction-contexts.svg'), W, H, *out,
           title="Три контексти виведення аргументів шаблону")


def fig_reference_collapsing():
    """Матриця правил згортання посилань (Reference Collapsing)."""
    W = 980
    M = 20
    head = ["Тип параметра T", "Оголошений тип у шаблоні", "Синтезований проміжний тип", "Фінальний згорнутий тип"]
    cols = [210, 240, 260, 230]
    rows = [
        ["T є U& (lvalue-посилання)", "T&  (lvalue-посилання)", "U& &", "U&  (lvalue-посилання)"],
        ["T є U& (lvalue-посилання)", "T&& (rvalue-посилання)", "U& &&", "U&  (lvalue-посилання)"],
        ["T є U&& (rvalue-посилання)", "T&  (lvalue-посилання)", "U&& &", "U&  (lvalue-посилання)"],
        ["T є U&& (rvalue-посилання)", "T&& (rvalue-посилання)", "U&& &&", "U&& (rvalue-посилання)"]
    ]
    HH, RH, GAP = 50, 68, 6
    H = 40 + HH + len(rows) * RH + 60
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 40, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 40 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            fill = "#eaf7ee" if ri == 3 and i == 3 else ("#eef4ff" if i == 0 else "#f7f9fb")
            stroke = POS if (ri == 3 and i == 3) else MUTED
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=13, bold=(i == 0 or i == 3), fill=fill, stroke=stroke))
            x += cols[i]
        y += RH

    out.append(text(W / 2, y + 26, "Головний інваріант: rvalue-посилання виникає лише тоді, коли обидва компоненти є rvalue (&& + &&)", size=13, color=MUTED))

    render(os.path.join(IMG, 'reference-collapsing.svg'), W, H, *out,
           title="Матриця правил згортання посилань")


def fig_non_deduced_contexts():
    """Дедуковані та недедуковані контексти у шаблонах C++."""
    W, H = 980, 360
    out = []

    b1, w1, h1 = textbox(240, 110,
                         ["Дедукований контекст (Deduced)",
                          "template<typename T>",
                          "void compare(T a, T b);",
                          "Виклик: compare(10, 20.0);",
                          "ПОМИЛКА: конфлікт int vs double"],
                         size=13, pad=16, fill="#fdf0ed", stroke=NEG)
    out.append(b1)
    out.append(text(240, 110 - h1 / 2 - 16, "Пряме зіставлення типів (Deduction Conflict)", size=13, color=MUTED))

    b2, w2, h2 = textbox(740, 110,
                         ["Недедукований контекст (Non-deduced)",
                          "template<typename T>",
                          "void compare(T a, std::type_identity_t<T> b);",
                          "Виклик: compare(10, 20.0);",
                          "УСПІХ: T = int, аргумент b приводиться до int"],
                         size=13, pad=16, fill="#eaf7ee", stroke=POS)
    out.append(b2)
    out.append(text(740, 110 - h2 / 2 - 16, "Кероване вимкнення виведення (type_identity)", size=13, color=MUTED))

    out.append(arrow(240 + w1 / 2 + 10, 110, 740 - w2 / 2 - 10, 110))

    b_info, _, _ = textbox(W / 2, 260,
                           ["std::type_identity_t<T> (або typename Class<T>::type) блокує шаблонне виведення для аргументу b.",
                            "Компілятор виводить T виключно з аргументу a, а для другого аргументу застосовує стандартне неявне приведення типів."],
                           size=13, pad=14, fill="#fff8e1", stroke="#b8860b")
    out.append(b_info)

    out.append(text(W / 2, 330, "Недедуковані контексти дозволяють розділити джерело типу від споживача перетвореного типу", size=13, color=MUTED))

    render(os.path.join(IMG, 'non-deduced-contexts.svg'), W, H, *out,
           title="Недедуковані контексти у шаблонах C++")


def fig_ctad_synthesis():
    """Синтез кандидатів виведення у механізмі CTAD (C++17)."""
    W, H = 1040, 420
    out = []

    b1, w1, h1 = textbox(180, 120,
                         ["Шаблон класу та конструктори",
                          "template<typename T>",
                          "struct Vector {",
                          "  Vector(T val);",
                          "  Vector(const T* b, const T* e);",
                          "};"],
                         size=12, pad=14, fill="#eef4ff", stroke=MUTED)
    out.append(b1)
    out.append(text(180, 120 - h1 / 2 - 16, "Первинний шаблон класу", size=13, color=MUTED))

    b2, w2, h2 = textbox(520, 75,
                         ["Неявні кандидати CTAD (Implicit)",
                          "template<typename T>",
                          "auto __f(T val) -> Vector<T>;",
                          "template<typename T>",
                          "auto __f(const T* b, const T* e) -> Vector<T>;"],
                         size=12, pad=12, fill="#f7f9fb", stroke=MUTED)
    out.append(b2)

    b3, w3, h3 = textbox(520, 195,
                         ["Явні правила виведення (Deduction Guides)",
                          "template<typename Iter>",
                          "Vector(Iter b, Iter e)",
                          "  -> Vector<typename iterator_traits<Iter>::value_type>;"],
                         size=12, pad=12, fill="#fff8e1", stroke="#b8860b")
    out.append(b3)

    b4, w4, h4 = textbox(870, 135,
                         ["Спільний набір перевантажень",
                          "Overload Resolution",
                          "Знаходження найкращого кандидата",
                          "⇒ Створення спеціалізації Vector<int>"],
                         size=13, pad=16, fill="#eaf7ee", stroke=POS)
    out.append(b4)
    out.append(text(870, 135 - h4 / 2 - 16, "Результат вирішення виклику", size=13, color=MUTED))

    out.append(arrow(180 + w1 / 2 + 10, 100, 520 - w2 / 2 - 10, 75))
    out.append(arrow(180 + w1 / 2 + 10, 140, 520 - w3 / 2 - 10, 195))
    out.append(arrow(520 + w2 / 2 + 10, 75, 870 - w4 / 2 - 10, 115))
    out.append(arrow(520 + w3 / 2 + 10, 195, 870 - w4 / 2 - 10, 155))

    b_bot, _, _ = textbox(W / 2, 330,
                          ["Ініціалізація: Vector v(arr, arr + 10);",
                           "Компілятор формує уявний набір перевантажень функцій, запускає звичайне виведення типів функцій,",
                           "обирає найбільш спеціалізований кандидат (Deduction Guide) і підставляє виведений тип у клас."],
                          size=13, pad=14, fill="#f0f4f8", stroke=MUTED)
    out.append(b_bot)

    render(os.path.join(IMG, 'ctad-synthesis-guide.svg'), W, H, *out,
           title="Синтез кандидатів виведення у механізмі CTAD")


if __name__ == '__main__':
    fig_deduction_contexts()
    fig_reference_collapsing()
    fig_non_deduced_contexts()
    fig_ctad_synthesis()
    print("All figures generated successfully.")
