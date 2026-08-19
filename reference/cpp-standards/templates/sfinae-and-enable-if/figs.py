# -*- coding: utf-8 -*-
"""Фігури до теми «SFINAE й enable_if: відбір перевантажень»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_sfinae_pipeline():
    """Конвеєр SFINAE у процесі розв'язання перевантажень."""
    W, H = 1040, 430
    out = []

    # Title / description area
    out.append(text(W / 2, 28, "Шлях виклику функції через конвеєр SFINAE та розв'язання перевантажень", size=15, bold=True))

    # Column 1: Виклик функції
    b1, w1, h1 = textbox(130, 110, ["Точка виклику", "serialize(42)"], size=14, pad=14, bold=True, fill="#e8edf3")
    out.append(b1)

    # Column 2: Кандидати
    b_cand1, _, _ = textbox(380, 85, ["Кандидат A (шаблон):", "template<typename T>", "enable_if_t<is_integral_v<T>, void>", "serialize(T val)"], size=12, pad=10, fill="#eef4ff", stroke=NEG)
    b_cand2, _, _ = textbox(380, 205, ["Кандидат B (шаблон):", "template<typename T>", "decltype(declval<T>().write(), void())", "serialize(T val)"], size=12, pad=10, fill="#fff5f5", stroke=POS)
    out.append(b_cand1)
    out.append(b_cand2)

    # Arrows from Call to Candidates
    out.append(arrow(130 + w1 / 2 + 6, 110, 380 - 150, 85))
    out.append(arrow(130 + w1 / 2 + 6, 110, 380 - 150, 205))

    # Column 3: Результат підстановки типів (T = int)
    b_res1, _, _ = textbox(680, 85, ["Підстановка T = int:", "is_integral_v<int> == true", "enable_if_t<true, void> ⇒ void", "Сигнатура валідна: void(int)"], size=12, pad=10, fill="#eaf7ee", stroke=FIELD)
    b_res2, _, _ = textbox(680, 205, ["Підстановка T = int:", "declval<int>().write() ⇒ ПОМИЛКА", "Тип int не має методу write()", "Невдача в сигнатурі (SFINAE)"], size=12, pad=10, fill="#fdecea", stroke=POS)
    out.append(b_res1)
    out.append(b_res2)

    out.append(arrow(380 + 150, 85, 680 - 145, 85))
    out.append(arrow(380 + 150, 205, 680 - 145, 205))

    # Column 4: Множина придатних функцій (Viable Set)
    b_viable, _, _ = textbox(930, 85, ["Множина кандидатів:", "Кандидат A включено", "Обирається для виклику"], size=12, pad=10, fill="#eaf7ee", stroke=FIELD)
    b_drop, _, _ = textbox(930, 205, ["Тихе вилучення:", "Кандидат B відкинутий", "Жодної помилки збірки!"], size=12, pad=10, fill="#fdf0ed", stroke=POS)
    out.append(b_viable)
    out.append(b_drop)

    out.append(arrow(680 + 145, 85, 930 - 95, 85))
    out.append(arrow(680 + 145, 205, 930 - 95, 205))

    # Lower comparison banner
    b_bot, _, _ = textbox(W / 2, 350, [
        "Ключова вимога стандарту C++ (§13.10.2):",
        "Помилка підстановки дає тихе вилучення лише у безпосередньому контексті (сигнатурі) оголошення шаблону.",
        "Помилка всередині тіла функції або всередині інстанційованого класу є жорсткою помилкою (Hard Error)."
    ], size=13, pad=14, fill="#fff8e1", stroke="#b8860b")
    out.append(b_bot)

    render(os.path.join(IMG, 'sfinae-overload-pipeline.svg'), W, H, *out,
           title="Конвеєр SFINAE у процесі розв'язання перевантажень")


def fig_enable_if_anatomy():
    """Анатомія метафункції std::enable_if та генерація помилки підстановки."""
    W, H = 980, 390
    out = []

    out.append(text(W / 2, 28, "Внутрішній механізм std::enable_if: наявність або відсутність вкладеного ::type", size=15, bold=True))

    # Left Branch: Condition == true
    b_l1, _, _ = textbox(260, 95, ["Умова B == true", "std::enable_if<true, T>"], size=13, pad=12, bold=True, fill="#e8edf3")
    b_l2, _, _ = textbox(260, 205, ["Спеціалізація шаблону:", "template<typename T>", "struct enable_if<true, T> {", "    using type = T;", "};"], size=13, pad=14, fill="#eaf7ee", stroke=FIELD)
    b_l3, _, _ = textbox(260, 315, ["Результат розіменування ::type:", "Успіх: тип T підставлено у сигнатуру", "Функція потрапляє до списку кандидатів"], size=12, pad=12, fill="#eaf7ee", stroke=FIELD)
    out.append(b_l1)
    out.append(b_l2)
    out.append(b_l3)
    out.append(arrow(260, 95 + 28, 260, 205 - 48))
    out.append(arrow(260, 205 + 48, 260, 315 - 32))

    # Right Branch: Condition == false
    b_r1, _, _ = textbox(720, 95, ["Умова B == false", "std::enable_if<false, T>"], size=13, pad=12, bold=True, fill="#fdecea")
    b_r2, _, _ = textbox(720, 205, ["Первинний шаблон:", "template<bool B, typename T = void>", "struct enable_if {};", "/* Вкладений псевдонім type ВІДСУТНІЙ */"], size=13, pad=14, fill="#fff5f5", stroke=POS)
    b_r3, _, _ = textbox(720, 315, ["Спроба доступу до enable_if<false, T>::type:", "Невдача: член type не існує у структурі!", "SFINAE відкидає перевантаження"], size=12, pad=12, fill="#fdecea", stroke=POS)
    out.append(b_r1)
    out.append(b_r2)
    out.append(b_r3)
    out.append(arrow(720, 95 + 28, 720, 205 - 48))
    out.append(arrow(720, 205 + 48, 720, 315 - 32))

    render(os.path.join(IMG, 'enable-if-anatomy.svg'), W, H, *out,
           title="Анатомія метафункції std::enable_if та генерація помилки підстановки")


def fig_evolution_table():
    """Еволюція методів відбору перевантажень та інтроспекції типів."""
    W = 1040
    M = 20
    cols = [140, 260, 380, 220]
    head = ["Епоха", "Інструмент і синтаксис", "Механізм роботи", "Діагностика компілятора"]
    rows = [
        ["C++03\nSFINAE 1.0",
         "sizeof-ідіома та перевантаження\nchar test(int); char test_yes[2];",
         "Обчислення розміру фіктивних викликів\nбез запуску коду в runtime",
         "Незрозумілі помилки,\nобмеженість лише типами"],
        ["C++11\nSFINAE 2.0",
         "std::enable_if, decltype, declval\nExpression SFINAE у сигнатурах",
         "Підстановка довільних виразів у\nповернене значення та дефолтні типи",
         "Багатосторінкові простирадла\nглибоких стеків інстанціації"],
        ["C++14 / 17\nDetection",
         "std::void_t, type_traits_v\nstd::experimental::is_detected",
         "Уніфікований маппінг виразів у void\nчерез часткову спеціалізацію класів",
         "Краща структуризація коду,\nале помилки все ще важкі"],
        ["C++20\nConcepts",
         "concept, requires-clause\nauto func(std::integral auto x)",
         "Пряме декларативне обмеження інтерфейсу\nта предикатне ранжування subsumption",
         "Точні повідомлення:\nяку саме вимогу порушено"]
    ]
    HH, RH, GAP = 54, 82, 6
    H = 50 + HH + len(rows) * RH + 24
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 50, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 50 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else ("#eaf7ee" if ri == 3 else "#f7f9fb")
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=13, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'sfinae-evolution.svg'), W, H, *out,
           title="Еволюція методів відбору перевантажень та інтроспекції типів")


if __name__ == '__main__':
    fig_sfinae_pipeline()
    fig_enable_if_anatomy()
    fig_evolution_table()
    print("All figures generated successfully.")
