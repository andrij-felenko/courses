# -*- coding: utf-8 -*-
"""Фігури до теми «std::generator: синхронний корутинний генератор C++23»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Взаємодія викликача, ітератора та кадру корутини std::generator ─────────
def fig_generator_execution_flow():
    W, H = 940, 450
    f = []

    f.append(text(50, 35, "Архітектура та цикли призупинення / відновлення std::generator", size=16, color=INK, anchor="start", bold=True))

    # Викликач (Loop)
    f.append(text(50, 70, "Код викликача (Caller Loop)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 90, 250, 310,
                    "for (int v : generate_nums()) {\n"
                    "  // 1. auto it = gen.begin()\n"
                    "  //    --> handle.resume()\n"
                    "  //\n"
                    "  // 2. int v = *it\n"
                    "  //    --> promise.value()\n"
                    "  //\n"
                    "  // 3. ++it\n"
                    "  //    --> handle.resume()\n"
                    "  use(v);\n"
                    "}",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Інтерфейс std::generator & iterator
    f.append(text(340, 70, "Об'єкт std::generator<T>", size=13, color=INK, anchor="start", bold=True))
    f.append(fitbox(340, 90, 240, 310,
                    "std::generator<T>\n"
                    "┌───────────────────────────────┐\n"
                    "│ std::coroutine_handle<P> h_  │\n"
                    "└──────────────┬────────────────┘\n"
                    "               │\n"
                    "               ▼\n"
                    "iterator:\n"
                    "• begin() -> resume() h_\n"
                    "• operator*() -> promise.val_\n"
                    "• operator++() -> resume() h_\n"
                    "• sentinel: default_sentinel_t",
                    size=11, fill="#eef2f7", stroke=LINE))

    # Кадр корутини у купі (Coroutine Frame)
    f.append(text(630, 70, "Кадр корутини у купі (Heap Frame)", size=13, color=POS, anchor="start", bold=True))
    f.append(fitbox(630, 90, 260, 310,
                    "Coroutine Frame:\n"
                    "┌───────────────────────────────┐\n"
                    "│ promise_type (std::generator) │\n"
                    "│   • val_ptr / ref_holder     │\n"
                    "│   • initial_suspend: always   │\n"
                    "│   • yield_value(x): suspend   │\n"
                    "├───────────────────────────────┤\n"
                    "│ Тіло корутини:                │\n"
                    "│   co_yield 1; // suspend      │\n"
                    "│   co_yield 2; // suspend      │\n"
                    "│   co_return;  // done         │\n"
                    "└───────────────────────────────┘",
                    size=11, fill="#fff7e6", stroke=POS))

    # Стрілки взаємодії між блоками
    f.append(arrow(300, 150, 340, 150, color=FIELD, sw=2))
    f.append(arrow(580, 180, 630, 180, color=POS, sw=2))
    f.append(arrow(630, 240, 580, 240, color=MUTED, sw=2))

    f.append(text(470, 420, "Призупинення на co_yield повертає керування у викликач без розгортання системного стеку", size=11, color=MUTED))

    render(os.path.join(OUT, 'generator-execution-flow.svg'), W, H, *f,
           title="Архітектура std::generator")


# ── 2. Делегування вкладених генераторів через elements_of ───────────────────────
def fig_recursive_yield_delegation():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Рекурсивна передача керування через std::ranges::elements_of (Symmetric Transfer)", size=16, color=INK, anchor="start", bold=True))

    # Безкоштовний прямий перехід між генераторами
    f.append(text(50, 75, "Традиційний циклічний yield (O(N^2) оверхед):", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 95, 410, 140,
                    "for (auto x : sub_generator()) {\n"
                    "    co_yield x;\n"
                    "}\n"
                    "// Проблема: Кожен виклик проходить призупинення\n"
                    "// та відновлення через усі проміжні рівні стеку!",
                    size=11, fill="#fff0f0", stroke=NEG))

    f.append(text(490, 75, "C++23 elements_of (O(1) Symmetric Transfer):", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(490, 95, 400, 140,
                    "co_yield std::ranges::elements_of(\n"
                    "    sub_generator()\n"
                    ");\n"
                    "// Перевага: Посилання parent_link зв'язує\n"
                    "// вкладені обіцянки напряму у зв'язаний список!",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Схема зв'язаного списку обіцянок (Promise Chain)
    f.append(text(50, 260, "Прямий ланцюжок вкладених обіцянок (Promise Chain Pointer):", size=13, color=INK, anchor="start", bold=True))
    f.append(fitbox(50, 285, 260, 95,
                    "Батьківська корутина:\n"
                    "promise_type (Root)\n"
                    "top_promise ────────┐",
                    size=11, fill="#eef2f7", stroke=LINE))

    f.append(arrow(310, 330, 370, 330, color=POS, sw=2))

    f.append(fitbox(375, 285, 260, 95,
                    "Вкладена корутина L1:\n"
                    "promise_type (Node)\n"
                    "parent_link ──────┐",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(arrow(635, 330, 695, 330, color=FIELD, sw=2))

    f.append(fitbox(700, 285, 190, 95,
                    "Листова корутина L2:\n"
                    "co_yield value;\n"
                    "Відновлення напряму!",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'recursive-yield-delegation.svg'), W, H, *f,
           title="Делегування через elements_of")


if __name__ == '__main__':
    fig_generator_execution_flow()
    fig_recursive_yield_delegation()
    print("Figures generated successfully.")
