# -*- coding: utf-8 -*-
"""Фігури до теми «Спеціалізація й перевантаження шаблонів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_specialization_pipeline():
    """Двоетапний конвеєр: перевантаження функцій та вибір спеціалізації."""
    W, H = 1000, 420
    out = []

    # Title / Phase headers
    out.append(rect(30, 20, 440, 40, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(250, 45, "Фаза 1: Overload Resolution (Вирішення перевантаження)", size=13, bold=True, color="#2d3748"))

    out.append(rect(530, 20, 440, 40, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(750, 45, "Фаза 2: Інстанціювання та вибір спеціалізації", size=13, bold=True, color="#2d3748"))

    # Step 1: Call site
    b_call, _, _ = textbox(110, 160, ["Виклик функції", "f(ptr) / f(val)"], size=13, pad=12, bold=True, fill="#e2e8f0", stroke="#4a5568")
    out.append(b_call)

    # Overload candidate set
    out.append(rect(230, 80, 230, 290, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(345, 105, "Набір кандидатів перевантаження", size=12, bold=True, color="#4a5568"))

    b_cand1, _, _ = textbox(345, 145, ["Звичайні функції", "void f(int)"], size=12, pad=8, fill="#ffffff", stroke="#718096")
    b_cand2, _, _ = textbox(345, 215, ["Первинний шаблон A", "template<class T>", "void f(T)"], size=12, pad=8, fill="#ebf8ff", stroke="#3182ce")
    b_cand3, _, _ = textbox(345, 305, ["Первинний шаблон B", "template<class T>", "void f(T*)"], size=12, pad=8, fill="#ebf8ff", stroke="#3182ce")
    out.extend([b_cand1, b_cand2, b_cand3])

    # Warning box: specializations not in overload set
    b_warn, _, _ = textbox(345, 395, ["Спеціалізації НЕ беруть участі у фазі 1!", "Вони відсутні в наборі кандидатів"], size=11, pad=6, fill="#fff5f5", stroke="#e53e3e", color="#c53030")
    out.append(b_warn)

    # Arrows from call to candidates
    out.append(arrow(180, 160, 225, 160, color="#4a5568", sw=1.8))

    # Arrow from Phase 1 to Phase 2
    out.append(arrow(465, 260, 525, 260, color="#2b6cb0", sw=2.0))
    out.append(text(495, 245, "Переміг", size=11, bold=True, color="#2b6cb0"))

    # Phase 2 details
    out.append(rect(535, 80, 430, 290, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(750, 105, "Перевірка спеціалізацій обраного первинного шаблону", size=12, bold=True, color="#4a5568"))

    b_p2_win, _, _ = textbox(750, 155, ["Обраний первинний шаблон", "(наприклад, template<class T> void f(T*))"], size=12, pad=8, fill="#ebf8ff", stroke="#3182ce", bold=True)
    out.append(b_p2_win)

    # Branching in Phase 2
    b_spec_yes, _, _ = textbox(660, 265, ["Знайдено точну повну", "спеціалізацію template<>", "Викликається Foo<int*>()"], size=11, pad=8, fill="#f0fff4", stroke="#38a169", color="#22543d")
    b_spec_no, _, _ = textbox(850, 265, ["Спеціалізації немає:", "Компілятор генерує код", "з первинного шаблону"], size=11, pad=8, fill="#f7fafc", stroke="#718096", color="#2d3748")
    out.extend([b_spec_yes, b_spec_no])

    out.append(arrow(710, 195, 665, 225, color="#38a169", sw=1.5))
    out.append(arrow(790, 195, 845, 225, color="#718096", sw=1.5))

    render(os.path.join(IMG, 'specialization-vs-overload-pipeline.svg'), W, H, *out,
           title="Двоетапний конвеєр: перевантаження функцій та вибір спеціалізації")


def fig_partial_ordering():
    """Алгоритм часткового впорядкування шаблонів функцій (Partial Ordering)."""
    W, H = 1020, 380
    out = []

    # Title
    out.append(rect(30, 15, 960, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(510, 38, "Алгоритм часткового впорядкування шаблонів (Partial Ordering of Function Templates)", size=13, bold=True, color="#2d3748"))

    # Initial Templates
    b_t1, _, _ = textbox(160, 105, ["Шаблон 1 (Загальний)", "template<typename T>", "void process(T)"], size=12, pad=10, fill="#ebf8ff", stroke="#3182ce")
    b_t2, _, _ = textbox(160, 235, ["Шаблон 2 (Вказівники)", "template<typename T>", "void process(T*)"], size=12, pad=10, fill="#ebf8ff", stroke="#3182ce")
    out.extend([b_t1, b_t2])

    # Step 1: Synthesize dummy types
    b_synth, _, _ = textbox(470, 105, ["Крок 1: Синтез фіктивних типів", "Параметр T замінюється на унікальний", "штучний тип-маркер U1 (UniqueType)"], size=11, pad=10, fill="#fefcbf", stroke="#d69e2e", color="#744210")
    out.append(b_synth)

    out.append(arrow(280, 105, 335, 105, color="#4a5568", sw=1.5))
    out.append(arrow(280, 235, 335, 140, color="#4a5568", sw=1.5))

    # Step 2: Cross deduction
    b_ded1, _, _ = textbox(470, 215, ["Крок 2А: Підстановка процесу 2 у 1", "Аргумент process(U1*) -> process(T)", "Виведення T = U1* -> УСПІХ"], size=11, pad=8, fill="#f0fff4", stroke="#38a169", color="#22543d")
    b_ded2, _, _ = textbox(470, 310, ["Крок 2Б: Підстановка процесу 1 у 2", "Аргумент process(U1) -> process(T*)", "Виведення T* неможливе -> НЕВДАЧА"], size=11, pad=8, fill="#fff5f5", stroke="#e53e3e", color="#742a2a")
    out.extend([b_ded1, b_ded2])

    out.append(arrow(470, 155, 470, 175, color="#4a5568", sw=1.5))

    # Arrows to Conclusion
    out.append(arrow(605, 215, 685, 255, color="#2b6cb0", sw=1.8))
    out.append(arrow(605, 310, 685, 275, color="#2b6cb0", sw=1.8))

    # Step 3: Conclusion
    b_res, _, _ = textbox(830, 265, ["Крок 3: Висновок (Strict Ordering)", "Шаблон 2 приймає вужчу підмножину", "типів, ніж Шаблон 1.", "process(T*) є БІЛЬШ СПЕЦІАЛІЗОВАНИМ", "і перемагає під час перевантаження"], size=11, pad=10, fill="#ebf8ff", stroke="#2b6cb0", bold=True, color="#2c5282")
    out.append(b_res)

    render(os.path.join(IMG, 'partial-ordering-algorithm.svg'), W, H, *out,
           title="Алгоритм часткового впорядкування шаблонів функцій")


def fig_specialization_taxonomy():
    """Класифікація можливостей спеціалізації та перевантаження за сутностями мови C++."""
    W = 1040
    M = 20
    head = ["Сутність мови C++", "Повна спеціалізація", "Часткова спеціалізація", "Перевантаження (Overload)"]
    cols = [220, 240, 260, 280]
    rows = [
        ["Шаблони класів та структур\n(Class / Struct Templates)",
         "Дозволено\ntemplate<> struct Foo<int>",
         "Дозволено\ntemplate<class T> struct Foo<T*>",
         "Заборонено\n(не є функцією)"],
        ["Шаблони змінних\n(Variable Templates, C++14)",
         "Дозволено\ntemplate<> constexpr int v<int>",
         "Дозволено\ntemplate<class T> constexpr int v<T*>",
         "Заборонено\n(не є функцією)"],
        ["Шаблони функцій\n(Function Templates)",
         "Дозволено (Антипаттерн!)\ntemplate<> void f<int>(int)",
         "ЗАБОРОНЕНО СТАНДАРТОМ\n(помилка компіляції)",
         "ДОЗВОЛЕНО ТА РЕКОМЕНДОВАНО\n(вирішується через Partial Ordering)"],
        ["Шаблони псевдонімів\n(Alias Templates, using)",
         "Заборонено стандартом\n(не можна спеціалізувати)",
         "Заборонено стандартом\n(делегують у структури)",
         "Заборонено\n(не є функцією)"],
        ["Концепти\n(Concepts, C++20)",
         "Заборонено\n(не спеціалізуються)",
         "Заборонено\n(використовують subsumption)",
         "Заборонено\n(обмежують перевантаження)"]
    ]
    HH, RH, GAP = 50, 78, 6
    H = 40 + HH + len(rows) * RH + 20
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 40, c - GAP, HH - GAP, head[i], size=13, bold=True, fill="#edf2f7"))
        x += c

    y = 40 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            if i == 0:
                fill = "#f7fafc"
            elif "ЗАБОРОНЕНО" in cell or "Антипаттерн" in cell:
                fill = "#fff5f5"
            elif "ДОЗВОЛЕНО" in cell or "Дозволено" in cell:
                fill = "#f0fff4"
            else:
                fill = "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=11, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'specialization-taxonomy.svg'), W, H, *out,
           title="Класифікація можливостей спеціалізації та перевантаження за сутностями")


def fig_helper_delegation():
    """Ідіома делегування спеціалізації функцій у допоміжні структури."""
    W, H = 1000, 360
    out = []

    # Title
    out.append(rect(30, 15, 940, 36, fill="#edf2f7", stroke="#4a5568", sw=1.5))
    out.append(text(500, 38, "Ідіома делегування: обхід заборони часткової спеціалізації функцій", size=13, bold=True, color="#2d3748"))

    # Public API function
    b_api, _, _ = textbox(170, 160, ["Публічний шаблон функції", "template<typename T>", "void serialize(const T& val) {", "    detail::Serializer<T>::run(val);", "}"], size=12, pad=12, fill="#ebf8ff", stroke="#3182ce", bold=True)
    out.append(b_api)

    # Arrow to dispatcher
    out.append(arrow(320, 160, 385, 160, color="#2b6cb0", sw=2.0))
    out.append(text(352, 145, "Виклик", size=11, bold=True, color="#2b6cb0"))

    # Helper struct specializations
    out.append(rect(390, 75, 570, 260, fill="#f7fafc", stroke="#a0aec0", sw=1.2, rx=8))
    out.append(text(675, 100, "Допоміжний шаблон структури detail::Serializer<T>", size=13, bold=True, color="#4a5568"))

    b_h1, _, _ = textbox(515, 160, ["Первинна структура", "template<typename T>", "struct Serializer {", "  static void run(const T&);", "};"], size=11, pad=8, fill="#ffffff", stroke="#718096")
    b_h2, _, _ = textbox(515, 270, ["Часткова спец. для вказівників", "template<typename T>", "struct Serializer<T*> {", "  static void run(const T*);", "};"], size=11, pad=8, fill="#f0fff4", stroke="#38a169")
    b_h3, _, _ = textbox(790, 160, ["Часткова спец. для векторів", "template<typename T>", "struct Serializer<std::vector<T>> {", "  static void run(const auto&);", "};"], size=11, pad=8, fill="#f0fff4", stroke="#38a169")
    b_h4, _, _ = textbox(790, 270, ["Повна спец. для рядків", "template<>", "struct Serializer<std::string> {", "  static void run(const auto&);", "};"], size=11, pad=8, fill="#f0fff4", stroke="#38a169")

    out.extend([b_h1, b_h2, b_h3, b_h4])

    render(os.path.join(IMG, 'helper-delegation-flow.svg'), W, H, *out,
           title="Ідіома делегування спеціалізації функцій у допоміжні структури")


if __name__ == '__main__':
    fig_specialization_pipeline()
    fig_partial_ordering()
    fig_specialization_taxonomy()
    fig_helper_delegation()
    print("All figures generated successfully.")
