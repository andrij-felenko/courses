# -*- coding: utf-8 -*-
"""Фігури до теми «std::function та Type Erasure у C++»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння концепцій поліморфізму у C++ ────────────────────────────────
def fig_type_erasure_concept():
    W, H = 940, 480
    f = []

    f.append(text(470, 30, "Порівняння підходів до поліморфізму у C++", size=16, color=INK, anchor="middle", bold=True))

    # Колонка 1: Статичний поліморфізм (Шаблони)
    f.append(fitbox(40, 60, 270, 40, "1. Статичний поліморфізм\n(Templates / Monomorphization)", size=12, fill="#eef2f7", stroke=LINE, bold=True))
    f.append(fitbox(40, 110, 270, 270,
                    "template <typename F>\nvoid execute(F func) {\n    func();\n}\n\n"
                    "✔ Повне вбудовування\n"
                    "✔ Нульові витрати runtime\n\n"
                    "✖ Новий код для кожного F\n"
                    "✖ Немає контейнерів (std::vector)",
                    size=11, fill="#f4f6f8", stroke=LINE, anchor="start"))

    # Колонка 2: Динамічний поліморфізм (ООП Спадкування)
    f.append(fitbox(335, 60, 270, 40, "2. Динамічний поліморфізм\n(Virtual Inheritance / OOP)", size=12, fill="#fff7e6", stroke=POS, bold=True))
    f.append(fitbox(335, 110, 270, 270,
                    "class IAction {\npublic:\n    virtual void run() = 0;\n};\n\n"
                    "✔ Єдиний тип покажчика\n"
                    "✔ Збереження у контейнери\n\n"
                    "✖ Спадкування від IAction\n"
                    "✖ Не працює з лямбдами напряму",
                    size=11, fill="#fffbf2", stroke=POS, anchor="start"))

    # Колонка 3: Стирання типів (Type Erasure / std::function)
    f.append(fitbox(630, 60, 270, 40, "3. Стирання типів\n(Type Erasure / std::function)", size=12, fill="#e8f6ee", stroke=FIELD, bold=True))
    f.append(fitbox(630, 110, 270, 270,
                    "std::function<void()> fn = f;\n\n"
                    "✔ Однорідний зовнішній тип\n"
                    "✔ Приймає БУДЬ-ЯКИЙ Callable\n"
                    "✔ Поєднує шаблони та vtable\n\n"
                    "✖ Непрямий виклик (vtable)\n"
                    "✖ Можлива купа (Heap)",
                    size=11, fill="#f2f9f4", stroke=FIELD, anchor="start"))

    f.append(text(470, 440, "Type Erasure ізолює шаблонне конструювання від нешаблонного інтерфейсу виклику", size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, 'type-erasure-concept.svg'), W, H, *f,
           title="Порівняння концепцій поліморфізму у C++")


# ── 2. Анатомія макету пам'яті std::function (SBO vs Heap) ─────────────────────
def fig_std_function_memory_layout():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Анатомія макету пам'яті std::function (SBO проти Heap)", size=16, color=INK, anchor="middle", bold=True))

    # Сценарій А: Малий об'єкт (SBO — Small Buffer Optimization)
    f.append(text(40, 65, "Сценарій А: Малий об'єкт (Captures ≤ 16..32 байти)", size=13, color=FIELD, anchor="start", bold=True))
    
    # Прямокутник об'єкта std::function на стеку (48 байтів)
    f.append(fitbox(40, 90, 860, 110,
                    "Об'єкт std::function<R(Args...)> на стеку (наприклад, sizeof = 32..48 байтів):\n"
                    "┌──────────────────────────────────────┬────────────────────────────────────────────────────────┐\n"
                    "│  vtable / invoker ptr (8 B)         │  Внутрішній буфер char storage[24..32 B]              │\n"
                    "│  0x004012a0 ─────────► [invoke_fn]   │  [ Вміст лямбди: int x=10, double y=3.14 ] (на стеку) │\n"
                    "└──────────────────────────────────────┴────────────────────────────────────────────────────────┘\n"
                    "Пам'ять у купі НЕ ВИДІЛЯЄТЬСЯ. Викликається placement new всередині storage.",
                    size=11, fill="#e8f6ee", stroke=FIELD, anchor="start"))

    # Розділювальна лінія
    f.append(line(40, 220, 900, 220, color=MUTED, sw=1, dash="6 5"))

    # Сценарій Б: Великий об'єкт (Heap Allocation)
    f.append(text(40, 245, "Сценарій Б: Великий об'єкт (Captures > SBO limit або non-trivially relocatable)", size=13, color=POS, anchor="start", bold=True))
    
    # Об'єкт на стеку
    f.append(fitbox(40, 270, 420, 120,
                    "Об'єкт std::function на стеку:\n"
                    "┌───────────────────────────────────────┐\n"
                    "│ vtable / invoker ptr (8 B)            │\n"
                    "├───────────────────────────────────────┤\n"
                    "│ storage.heap_ptr (8 B) ─────────────┐ │\n"
                    "│ (вказівник на купу)                 │ │\n"
                    "└───────────────────────────────────────┴─┘",
                    size=11, fill="#fff7e6", stroke=POS, anchor="start"))

    f.append(arrow(470, 330, 535, 330, color=POS, sw=2))

    # Виділення у купі
    f.append(fitbox(540, 270, 360, 120,
                    "Динамічний буфер у купі (Heap Allocation):\n"
                    "┌────────────────────────────────────────┐\n"
                    "│ Динамічний об'єкт лямбди/функтора      │\n"
                    "│ [ std::vector, std::string, 100 байтів]│\n"
                    "│ Виділяється через operator new()       │\n"
                    "└────────────────────────────────────────┘",
                    size=11, fill="#fdf2f2", stroke=POS, anchor="start"))

    f.append(text(470, 430, "SBO гарантує відсутність алокацій у купі для малих функторів та покажчиків на функції", size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, 'std-function-memory-layout.svg'), W, H, *f,
           title="Макет пам'яті std::function для SBO та алокації у купі")


# ── 3. Механіка диспатчеризації виклику (Vtable / Invoker Pointer) ────────────
def fig_vtable_dispatch_mechanics():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Механіка виклику std::function::operator() через ручний інвокер", size=16, color=INK, anchor="middle", bold=True))

    # Крок 1: Виклик f(arg)
    f.append(fitbox(40, 70, 200, 100,
                    "Крок 1: Викликач\n"
                    "fn(42);\n"
                    "Виклик std::function::\noperator()(int x)",
                    size=11, fill="#eef2f7", stroke=LINE))

    f.append(arrow(245, 120, 295, 120, color=LINE, sw=2))

    # Крок 2: Внутрішній розіменування вказівника на інвокер
    f.append(fitbox(300, 70, 260, 100,
                    "Крок 2: Непрямий виклик\n"
                    "this->invoker_(&this->storage, 42);\n"
                    "Зчитування вказівника\nна статичний шаблонний інвокер",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(arrow(565, 120, 615, 120, color=POS, sw=2))

    # Крок 3: Статична функція інвокер
    f.append(fitbox(620, 70, 280, 100,
                    "Крок 3: Статичний інвокер\n"
                    "template<typename Lambda>\n"
                    "static R invoke(void* storage, int x) {\n"
                    "  return (*cast<Lambda*>(storage))(x);\n"
                    "}",
                    size=10, fill="#e8f6ee", stroke=FIELD))

    # Нижня частина: Схема таблиці управління часом життя (Control Vtable)
    f.append(line(40, 200, 900, 200, color=MUTED, sw=1, dash="6 5"))

    f.append(text(470, 225, "Таблиця віртуальних функцій управління (Custom Vtable / Control Block)", size=13, color=INK, anchor="middle", bold=True))

    f.append(fitbox(40, 250, 860, 150,
                    "┌─────────────────────────────────────────────────────────────────────────────────────────┐\n"
                    "│ std::function Vtable / Function Pointers:                                               │\n"
                    "├─────────────────────────────┬─────────────────────────────┬─────────────────────────────┤\n"
                    "│ invoker_ptr                 │ manager_ptr (Destructor)    │ manager_ptr (Copy/Move)     │\n"
                    "│ R(*)(void* storage, Args...)│ void(*)(void* storage)      │ void(*)(void* dst, src)     │\n"
                    "│ Розіменовує storage і       │ Викликає явний деструктор   │ Випливає при копіюванні чи  │\n"
                    "│ здійснює виклик operator()  │ ~Lambda() або delete ptr    │ переміщенні std::function   │\n"
                    "└─────────────────────────────┴─────────────────────────────┴─────────────────────────────┘",
                    size=11, fill="#f8f9fa", stroke=LINE, anchor="start"))

    f.append(text(470, 430, "Диспатчеризація здійснюється через статичні функціональні покажчики без віртуального спадкування", size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, 'vtable-dispatch-mechanics.svg'), W, H, *f,
           title="Механіка диспатчеризації виклику через ручний інвокер у std::function")


# ── 4. Матриця порівняння продуктивності та накладних витрат ───────────────────
def fig_performance_cost_matrix():
    W, H = 940, 440
    f = []

    f.append(text(470, 30, "Матриця накладних витрат різних способів виклику функцій у C++", size=16, color=INK, anchor="middle", bold=True))

    cols = [(210, "Механізм"), (370, "Алокація пам'яті"), (530, "Накладні витрати виклику"), (690, "Підтримка Inlining"), (850, "Гнучість / Гетерогенність")]
    
    # Заголовок таблиці
    f.append(fitbox(40, 60, 860, 35, "Спосіб передачі виклику \\ Характеристики", size=11, fill="#eceff3", color=INK, bold=True))

    rows = [
        ("Шаблон (auto / F)", "0 байтів (Стек)", "0 тактів (Direct call)", "✔ Повне (Inlining)", "✖ Лише під час компіляції"),
        ("C-вказівник (R(*)(Args...))", "0 байтів (Стек)", "1..3 такти (Indirect call)", "✖ Ні (крім LTO)", "✖ Не підтримує стан / лямбди"),
        ("std::function (SBO)", "0 байтів у купі", "2..5 тактів (Indirect call)", "✖ Ні (через fn ptr)", "✔ Повна гетерогенність"),
        ("std::function (Heap)", "24..128+ B у купі", "5..15+ тактів (Indirect + Cache miss)", "✖ Ні", "✔ Повна гетерогенність"),
        ("std::function_ref (C++26)", "0 байтів у купі", "1..3 такти (Non-owning ptr)", "✖ Ні", "✔ Тимчасова гетерогенність"),
    ]

    styles = [
        dict(fill="#e8f6ee", stroke=FIELD),
        dict(fill="#f4f6f8", stroke=LINE),
        dict(fill="#fff7e6", stroke=POS),
        dict(fill="#fdf2f2", stroke=POS),
        dict(fill="#eef2f7", stroke=LINE),
    ]

    y = 100
    for idx, (mech, alloc, call_cost, inlining, flex) in enumerate(rows):
        f.append(fitbox(40, y, 170, 50, mech, size=10, bold=True, **styles[idx]))
        f.append(fitbox(215, y, 155, 50, alloc, size=10, **styles[idx]))
        f.append(fitbox(375, y, 175, 50, call_cost, size=10, **styles[idx]))
        f.append(fitbox(555, y, 155, 50, inlining, size=10, **styles[idx]))
        f.append(fitbox(715, y, 185, 50, flex, size=10, **styles[idx]))
        y += 55

    f.append(text(470, 410, "Шаблони дають максимльну швидкість, std::function_ref — нульові алокації, std::function — універсальність", size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, 'performance-cost-matrix.svg'), W, H, *f,
           title="Матриця порівняння продуктивності та накладних витрат функціональних абстракцій")


if __name__ == "__main__":
    fig_type_erasure_concept()
    fig_std_function_memory_layout()
    fig_vtable_dispatch_mechanics()
    fig_performance_cost_matrix()
    print("Всі 4 SVG фігури успішно згенеровано у img/")
