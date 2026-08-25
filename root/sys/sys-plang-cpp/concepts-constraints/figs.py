# -*- coding: utf-8 -*-
"""Фігури до теми «Концепти й обмеження шаблонів» (Concepts & Constraints)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_diagnostics_comparison():
    """Порівняння конвеєра діагностики помилок: SFINAE/невимушені шаблони проти концептів."""
    W, H = 1040, 430
    out = []

    # Title / Headers
    out.append(rect(25, 15, 480, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(265, 38, "Невимушений шаблон / SFINAE (до C++20)", size=13, bold=True, color="#2d3748"))

    out.append(rect(535, 15, 480, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(775, 38, "Шаблон із концептами C++20 (requires)", size=13, bold=True, color="#2d3748"))

    # Left: SFINAE / Unconstrained Flow
    out.append(rect(25, 65, 480, 345, fill="#fff5f5", stroke="#feb2b2", sw=1.2, rx=8))
    
    b_call_l, _, _ = textbox(265, 100, ["Виклик: std::sort(list.begin(), list.end())", "Аргумент: BidirectionalIterator (std::list)"], size=11, pad=8, fill="#ffffff", stroke="#cbd5e0")
    out.append(b_call_l)

    b_inst_l, _, _ = textbox(265, 170, ["Глибоке інстанціювання тіла шаблону", "std::__sort -> std::__introsort_loop -> std::__unguarded_partition"], size=10, pad=8, fill="#fed7d7", stroke="#e53e3e", color="#9b2c2c")
    out.append(b_inst_l)

    b_fail_l, _, _ = textbox(265, 255, ["Помилка глибоко в надрах STL:", "stl_algo.h:1842: error: no match for operator-", "iterators do not support random access subtraction"], size=10, pad=8, fill="#fff5f5", stroke="#c53030", color="#742a2a")
    out.append(b_fail_l)

    b_diag_l, _, _ = textbox(265, 350, ["Результат: каскад із 150+ рядків стек-трейсу інстанціювання", "Розробник змушений шукати першопричину в чужих внутрішніх заголовках"], size=10, pad=8, fill="#ffffff", stroke="#e53e3e", color="#c53030")
    out.append(b_diag_l)

    out.append(arrow(265, 125, 265, 145, color="#e53e3e", sw=1.5))
    out.append(arrow(265, 205, 265, 225, color="#e53e3e", sw=1.5))
    out.append(arrow(265, 295, 265, 320, color="#e53e3e", sw=1.5))

    # Right: Concepts Flow
    out.append(rect(535, 65, 480, 345, fill="#f0fff4", stroke="#9ae6b4", sw=1.2, rx=8))

    b_call_r, _, _ = textbox(775, 100, ["Виклик: std::ranges::sort(list)", "Вимога: template<std::ranges::random_access_range R>"], size=11, pad=8, fill="#ffffff", stroke="#cbd5e0")
    out.append(b_call_r)

    b_gate_r, _, _ = textbox(775, 175, ["Перевірка предикатів концепту на межі інтерфейсу", "std::random_access_iterator<I> == false (немає operator-)"], size=10, pad=8, fill="#c6f6d5", stroke="#38a169", color="#22543d")
    out.append(b_gate_r)

    b_stop_r, _, _ = textbox(775, 255, ["Миттєва зупинка ДО інстанціювання тіла", "Шаблон відсіюється з набору кандидатів без помилок у нутрощах"], size=10, pad=8, fill="#e6fffa", stroke="#319795", color="#234e52")
    out.append(b_stop_r)

    b_diag_r, _, _ = textbox(775, 350, ["Результат: чітка локалізована діагностика у 2 рядки:", "main.cpp:12: error: constraints not satisfied for sort(list)", "note: concept random_access_range<std::list<int>> evaluated to false"], size=10, pad=8, fill="#ffffff", stroke="#38a169", color="#22543d")
    out.append(b_diag_r)

    out.append(arrow(775, 125, 775, 145, color="#38a169", sw=1.5))
    out.append(arrow(775, 205, 775, 225, color="#38a169", sw=1.5))
    out.append(arrow(775, 295, 775, 320, color="#38a169", sw=1.5))

    render(os.path.join(IMG, 'sfinae-vs-concepts-diagnostics.svg'), W, H, *out,
           title="Порівняння діагностики помилок: SFINAE проти концептів C++20")


def fig_requires_taxonomy():
    """Класифікація чотирьох видів вимог у виразі requires."""
    W, H = 1040, 450
    out = []

    # Title
    out.append(rect(25, 15, 990, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(520, 38, "Анатомія виразу requires: чотири види вимог до типу", size=13, bold=True, color="#2d3748"))

    # Central requires block outline
    out.append(rect(25, 65, 990, 370, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))

    # Box 1: Simple requirement
    b1, _, _ = textbox(150, 115, ["1. Проста вимога", "(Simple Requirement)", "Синтаксична валідність виразу"], size=11, pad=8, fill="#ebf8ff", stroke="#3182ce", bold=True)
    out.append(b1)
    b1_code, _, _ = textbox(150, 240, ["x + y;", "*it;", "a.clear();", "", "Перевіряє, чи вираз успішно", "проходить синтаксичний", "і семантичний розбір."], size=10, pad=8, fill="#ffffff", stroke="#718096")
    out.append(b1_code)

    # Box 2: Type requirement
    b2, _, _ = textbox(395, 115, ["2. Типізована вимога", "(Type Requirement)", "Існування вкладеного типу"], size=11, pad=8, fill="#fefcbf", stroke="#d69e2e", bold=True)
    out.append(b2)
    b2_code, _, _ = textbox(395, 240, ["typename T::value_type;", "typename Container::iterator;", "", "Перевіряє наявність типу,", "псевдоніма using або", "валідності спеціалізації", "шаблону типу."], size=10, pad=8, fill="#ffffff", stroke="#718096")
    out.append(b2_code)

    # Box 3: Compound requirement
    b3, _, _ = textbox(645, 115, ["3. Складена вимога", "(Compound Requirement)", "Вираз + noexcept + тип результату"], size=11, pad=8, fill="#f0fff4", stroke="#38a169", bold=True)
    out.append(b3)
    b3_code, _, _ = textbox(645, 240, ["{ expr } noexcept -> concept;", "", "{ x.size() } -> std::same_as<std::size_t>;", "{ *it } noexcept -> std::convertible_to<T>;", "", "Валідує вираз, гарантію", "noexcept та накладає концепт", "на виведений тип результату."], size=10, pad=8, fill="#ffffff", stroke="#718096")
    out.append(b3_code)

    # Box 4: Nested requirement
    b4, _, _ = textbox(890, 115, ["4. Вкладена вимога", "(Nested Requirement)", "Обчислення логічного предикату"], size=11, pad=8, fill="#faf5ff", stroke="#805ad5", bold=True)
    out.append(b4)
    b4_code, _, _ = textbox(890, 240, ["requires predicate_v<T>;", "", "requires sizeof(T) <= 64;", "requires std::is_integral_v<T>;", "", "Обчислює константний логічний", "вираз під час компіляції.", "Якщо false — умова не виконана."], size=10, pad=8, fill="#ffffff", stroke="#718096")
    out.append(b4_code)

    # Bottom summary
    b_sum, _, _ = textbox(520, 395, ["requires (T a, T b) { /* 1. Прості */ a + b; /* 2. Типи */ typename T::value_type; /* 3. Складені */ { a.size() } -> std::integral; /* 4. Вкладені */ requires sizeof(T) >= 4; };"], size=10, pad=6, fill="#edf2f7", stroke="#4a5568")
    out.append(b_sum)

    render(os.path.join(IMG, 'requires-expression-taxonomy.svg'), W, H, *out,
           title="Класифікація чотирьох видів вимог у виразі requires")


def fig_constraint_syntax_forms():
    """Чотири синтаксичні форми застосування обмежень у C++20."""
    W, H = 1040, 420
    out = []

    # Title
    out.append(rect(25, 15, 990, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(520, 38, "Чотири форми синтаксису обмежень шаблонів у C++20", size=13, bold=True, color="#2d3748"))

    # 4 blocks in grid
    # Form 1: Ad-hoc requires clause after template
    out.append(rect(25, 65, 480, 155, fill="#ffffff", stroke="#cbd5e0", sw=1.2, rx=6))
    out.append(text(265, 88, "1. Речення requires після заголовка шаблону", size=11, bold=True, color="#2b6cb0"))
    b1_code, _, _ = textbox(265, 140, ["template<typename T>", "requires std::integral<T> && (sizeof(T) >= 4)", "void process(T val);"], size=10, pad=6, fill="#ebf8ff", stroke="#3182ce")
    out.append(b1_code)
    out.append(text(265, 195, "Найкраще для: складних кон'юнкцій, диз'юнкцій та ad-hoc предикатів", size=9, italic=True, color="#4a5568"))

    # Form 2: Type-constraint parameter
    out.append(rect(535, 65, 480, 155, fill="#ffffff", stroke="#cbd5e0", sw=1.2, rx=6))
    out.append(text(775, 88, "2. Типізоване обмеження параметра (Type-constraint)", size=11, bold=True, color="#2b6cb0"))
    b2_code, _, _ = textbox(775, 140, ["template<std::integral T, std::convertible_to<T> U>", "void process(T val, U other);"], size=10, pad=6, fill="#ebf8ff", stroke="#3182ce")
    out.append(b2_code)
    out.append(text(775, 195, "Найкраще для: лаконічного декларування одинарних концептів параметрів", size=9, italic=True, color="#4a5568"))

    # Form 3: Trailing requires clause
    out.append(rect(25, 240, 480, 160, fill="#ffffff", stroke="#cbd5e0", sw=1.2, rx=6))
    out.append(text(265, 263, "3. Хвостове речення requires (Trailing requires-clause)", size=11, bold=True, color="#2b6cb0"))
    b3_code, _, _ = textbox(265, 315, ["template<typename T>", "auto compute(T x) -> typename T::value_type", "    requires std::copyable<T> && std::default_initializable<T>;"], size=10, pad=6, fill="#ebf8ff", stroke="#3182ce")
    out.append(b3_code)
    out.append(text(265, 375, "Обов'язкове для: методів шаблонних класів та перевірки виведеного типу повернення", size=9, italic=True, color="#4a5568"))

    # Form 4: Abbreviated function template
    out.append(rect(535, 240, 480, 160, fill="#ffffff", stroke="#cbd5e0", sw=1.2, rx=6))
    out.append(text(775, 263, "4. Скорочені шаблони функцій (Abbreviated Function Template)", size=11, bold=True, color="#2b6cb0"))
    b4_code, _, _ = textbox(775, 315, ["void sort_buffer(std::ranges::random_access_range auto& buf);", "void print_value(std::integral auto x, std::floating_point auto y);"], size=10, pad=6, fill="#ebf8ff", stroke="#3182ce")
    out.append(b4_code)
    out.append(text(775, 375, "Найкраще для: повсякденних функцій без явного оголошення template<typename T>", size=9, italic=True, color="#4a5568"))

    render(os.path.join(IMG, 'constraint-syntax-forms.svg'), W, H, *out,
           title="Чотири синтаксичні форми застосування обмежень у C++20")


def fig_subsumption_ordering():
    """Часткове впорядкування та поглинання концептів (Subsumption)."""
    W, H = 1040, 420
    out = []

    # Title
    out.append(rect(25, 15, 990, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(520, 38, "Механізм Subsumption: нормалізація обмежень та вибір найбільш спеціалізованого шаблону", size=13, bold=True, color="#2d3748"))

    # Left: Overloads
    out.append(rect(25, 65, 310, 335, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(180, 90, "Перевантаження функцій", size=12, bold=True, color="#2d3748"))

    b_ov1, _, _ = textbox(180, 145, ["Кандидат 1 (Базовий)", "template<std::integral T>", "void advance(T x);"], size=10, pad=8, fill="#ebf8ff", stroke="#3182ce")
    b_ov2, _, _ = textbox(180, 260, ["Кандидат 2 (Спеціалізований)", "template<std::signed_integral T>", "void advance(T x);"], size=10, pad=8, fill="#f0fff4", stroke="#38a169")
    out.extend([b_ov1, b_ov2])

    # Center: Normalization & Atomic decomposition
    out.append(rect(360, 65, 370, 335, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(545, 90, "Нормалізація до атомарних обмежень", size=12, bold=True, color="#2d3748"))

    b_norm1, _, _ = textbox(545, 145, ["Нормалізоване обмеження 1:", "Атом A: std::is_integral_v<T>"], size=10, pad=8, fill="#ebf8ff", stroke="#3182ce")
    b_norm2, _, _ = textbox(545, 260, ["Нормалізоване обмеження 2:", "Атом A: std::is_integral_v<T>", "ТА (&&)", "Атом B: std::is_signed_v<T>"], size=10, pad=8, fill="#f0fff4", stroke="#38a169")
    out.extend([b_norm1, b_norm2])

    # Arrows from left to center
    out.append(arrow(280, 145, 355, 145, color="#3182ce", sw=1.5))
    out.append(arrow(280, 260, 355, 260, color="#38a169", sw=1.5))

    # Right: Subsumption verdict
    out.append(rect(755, 65, 260, 335, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(885, 90, "Правило поглинання", size=12, bold=True, color="#2d3748"))

    b_sub, _, _ = textbox(885, 180, ["(A && B) => A", "", "Кандидат 2 поглинає", "(subsumes) Кандидата 1,", "бо містить надмножину", "атомарних обмежень."], size=10, pad=8, fill="#fefcbf", stroke="#d69e2e", color="#744210")
    b_win, _, _ = textbox(885, 305, ["Виклик: advance(-5); (int)", "", "ПЕРЕМАГАЄ Кандидат 2", "без неоднозначності", "(Ambiguity)!"], size=10, pad=8, fill="#e6fffa", stroke="#319795", bold=True, color="#234e52")
    out.extend([b_sub, b_win])

    # Arrow from center to right
    out.append(arrow(675, 200, 750, 200, color="#d69e2e", sw=1.8))
    out.append(arrow(885, 235, 885, 265, color="#319795", sw=1.8))

    render(os.path.join(IMG, 'subsumption-ordering.svg'), W, H, *out,
           title="Механізм Subsumption: нормалізація обмежень та вибір шаблону")


if __name__ == '__main__':
    fig_diagnostics_comparison()
    fig_requires_taxonomy()
    fig_constraint_syntax_forms()
    fig_subsumption_ordering()
    print("All figures generated successfully.")
