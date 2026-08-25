# -*- coding: utf-8 -*-
"""Фігури до теми «GSL: not_null, owner і решта підпірок Core Guidelines»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Багаторівнева модель безпеки C++ Core Guidelines та GSL ─────────────
def fig_safety_layers():
    W, H = 960, 440
    f = []

    f.append(text(50, 35, "Багаторівнева модель безпеки: C++ Core Guidelines та бібліотека GSL", size=16, color=INK, anchor="start", bold=True))

    # Рівень 1: Статичний аналіз
    f.append(text(50, 75, "Рівень 1: Статичний аналіз вихідного коду (MSVC C++ Core Check, Clang-Tidy)", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 90, 860, 85,
                    "Правила Lifetime, Bounds та Type Profile:\n"
                    "• Відстеження життєвого циклу посилань і вказівників без оверхеду в бінарнику\n"
                    "• Виявлення використання вивільненої пам'яті (Use-After-Free) та dangling посилань\n"
                    "• Заборона сирої арифметики вказівників (Bounds.1) та неявних звужуючих приведень (ES.46)",
                    size=11, fill="#f0f4fc", stroke=NEG))

    # Рівень 2: Типобезпечні контракти в системі типів
    f.append(text(50, 200, "Рівень 2: Типобезпечні обгортки GSL (Type-Rich Zero-Overhead Abstractions)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 215, 275, 95,
                    "gsl::not_null<T*>\n\n"
                    "• Гарантія ненульового стану\n"
                    "• Заборона nullptr на етапі збірки\n"
                    "• Нульовий оверхед у регістрах",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(342, 215, 275, 95,
                    "gsl::owner<T*>\n\n"
                    "• Маркер володіння ресурсом\n"
                    "• Аліас типу для лінтерів\n"
                    "• Вимога явного delete/RAII",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(635, 215, 275, 95,
                    "gsl::span<T>\n\n"
                    "• Неперервний зріз пам'яті\n"
                    "• Автоматичний облік розміру\n"
                    "• Захист від Buffer Overflow",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Рівень 3: Динамічний контроль меж та контракти
    f.append(text(50, 335, "Рівень 3: Динамічний контроль, звуження та очищення ресурсів", size=13, color=POS, anchor="start", bold=True))
    f.append(fitbox(50, 350, 420, 70,
                    "Контроль переповнень: gsl::narrow / narrow_cast\n"
                    "• gsl::narrow<T>(val): перевірка втрати бітів/знаку -> narrowing_error\n"
                    "• gsl::narrow_cast<T>(val): явне документоване звуження без перевірки",
                    size=10, fill="#fff0f0", stroke=POS))

    f.append(fitbox(490, 350, 420, 70,
                    "Контракти та Scope Guard: Expects / Ensures / finally\n"
                    "• Expects(cond) / Ensures(cond): преумови та постумови функцій\n"
                    "• gsl::finally([&]{ ... }): гарантоване очищення під час виходу зі scope",
                    size=10, fill="#fff0f0", stroke=POS))

    render(os.path.join(OUT, 'gsl-safety-layers.svg'), W, H, *f,
           title="Багаторівнева модель безпеки GSL")


# ── 2. Архітектура та поведінка gsl::not_null<T*> ──────────────────────────
def fig_not_null():
    W, H = 960, 420
    f = []

    f.append(text(50, 35, "Анатомія gsl::not_null<T*>: конструювання, інваріанти та пам'ять", size=16, color=INK, anchor="start", bold=True))

    # Блок 1: Конструювання
    f.append(text(50, 70, "1. Фільтрація при конструюванні", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 90, 270, 130,
                    "Спроба nullptr:\n"
                    "gsl::not_null<int*> p = nullptr;\n"
                    "──► ПОМИЛКА КОМПІЛЯЦІЇ\n"
                    "(конструктор з nullptr_t видалено)\n\n"
                    "Динамічний вказівник:\n"
                    "gsl::not_null<int*> p(raw_ptr);\n"
                    "──► Runtime-перевірка Expects(p != nullptr)",
                    size=10, fill="#fff0f0", stroke=POS))

    # Блок 2: Розміщення в пам'яті та регістрах
    f.append(text(350, 70, "2. Фізичне розміщення (Zero-Overhead)", size=13, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(350, 90, 270, 130,
                    "Макет у пам'яті:\n"
                    "┌─────────────────────────────────┐\n"
                    "│   ptr_: T*  (8 байтів у x86-64) │\n"
                    "└─────────────────────────────────┘\n"
                    "sizeof(gsl::not_null<T*>) == sizeof(T*)\n\n"
                    "Асемблерний виклик:\n"
                    "Передається через регістр RDI/RCX\n"
                    "без додаткових обгорток чи vtable",
                    size=10, fill="#e8f6ee", stroke=FIELD))

    # Блок 3: Операції над вказівником
    f.append(text(650, 70, "3. Обмеження операцій (Rule Bounds.1)", size=13, color=NEG, anchor="start", bold=True))

    f.append(fitbox(650, 90, 260, 130,
                    "Дозволені операції:\n"
                    "• *p (розіменування без null-check)\n"
                    "• p->field (доступ до полів)\n"
                    "• p.get() (отримання сирого T*)\n\n"
                    "Заборонені операції:\n"
                    "• p++ / p-- (арифметика заборонена)\n"
                    "• p + 4 (для масивів є gsl::span)",
                    size=10, fill="#f0f4fc", stroke=NEG))

    # Нижня діаграма порівняння безпеки
    f.append(line(40, 245, 920, 245, color=MUTED, sw=1, dash="4 4"))
    f.append(text(50, 275, "Порівняння обробки розіменування у скомпільованому коді:", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 295, 420, 95,
                    "Традиційний підхід (defensive programming):\n"
                    "void render(Widget* w) {\n"
                    "    if (!w) return; // Зайва runtime-перевірка у кожній функції!\n"
                    "    w->draw();\n"
                    "}",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(490, 295, 420, 95,
                    "Підхід GSL (Type-Driven Contract):\n"
                    "void render(gsl::not_null<Widget*> w) {\n"
                    "    w->draw(); // Перевірка виконана один раз на межі введення!\n"
                    "               // Нуль зайвих інструкцій у тілі функції.\n"
                    "}",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'not-null-memory-and-checks.svg'), W, H, *f,
           title="Архітектура gsl::not_null")


# ── 3. Структура gsl::span<T> та безпечне вікно пам'яті ───────────────────
def fig_span():
    W, H = 960, 430
    f = []

    f.append(text(50, 35, "Структура gsl::span<T>: безпечний невласницький перегляд діапазону", size=16, color=INK, anchor="start", bold=True))

    # Дескриптор span
    f.append(text(50, 70, "Об'єкт gsl::span<int> на стеку (16 байтів у dynamic_extent):", size=12, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 85, 400, 75,
                    "┌───────────────────────┬───────────────────────┐\n"
                    "│ ptr_: int* (8 байтів) │ size_: ptrdiff_t (8B) │\n"
                    "│ вказує на початок     │ кількість елементів   │\n"
                    "└───────────────────────┴───────────────────────┘",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(455, 122, 535, 122, color=FIELD, sw=2))

    # Неперервний буфер у пам'яті
    f.append(text(540, 70, "Суцільний буфер даних у heap або stack:", size=12, color=INK, anchor="start", bold=True))
    f.append(fitbox(540, 85, 370, 75,
                    "┌─────────┬─────────┬─────────┬─────────┬─────────┐\n"
                    "│ elem[0] │ elem[1] │ elem[2] │ elem[3] │ elem[4] │\n"
                    "│  0x1000 │  0x1004 │  0x1008 │  0x100C │  0x1010 │\n"
                    "└─────────┴─────────┴─────────┴─────────┴─────────┘",
                    size=11, fill="#f0f4fc", stroke=NEG))

    # Нижня частина: перевірка меж та subspan
    f.append(line(40, 185, 920, 185, color=MUTED, sw=1, dash="4 4"))

    f.append(text(50, 215, "Контроль меж (Bounds Checking)", size=13, color=POS, anchor="start", bold=True))
    f.append(fitbox(50, 230, 420, 170,
                    "Індексація span[index]:\n\n"
                    "• Умова валідності: 0 <= index < span.size()\n"
                    "• При коректному index: прямий доступ O(1) *(ptr_ + index)\n"
                    "• При виході за межі (index >= 5 або index < 0):\n"
                    "  - Спрацьовує Expects(index < size_)\n"
                    "  - Виклик std::terminate() або викидання винятку\n"
                    "  - Повністю усувається вразливість Buffer Overflow",
                    size=10, fill="#fff0f0", stroke=POS))

    f.append(text(490, 215, "Операція піддіапазону (subspan)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(490, 230, 420, 170,
                    "Створення підвибірки: span.subspan(1, 3)\n\n"
                    "• Не копіює жодного байта з масиву!\n"
                    "• Створює новий дескриптор span:\n"
                    "  - new_ptr = ptr_ + 1 (0x1004)\n"
                    "  - new_size = 3 (елементи 1, 2, 3)\n"
                    "• Статична безпека: межі перевіряються під час створення subspan\n"
                    "• Підтримує перетворення у gsl::as_bytes(span)",
                    size=10, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'span-bounds-and-subspan.svg'), W, H, *f,
           title="Структура та операції gsl::span")


# ── 4. Дерево рішень звужуючих перетворень ─────────────────────────────────
def fig_narrowing_matrix():
    W, H = 960, 420
    f = []

    f.append(text(50, 35, "Звужуючі перетворення: безпечний gsl::narrow проти неявного касту", size=16, color=INK, anchor="start", bold=True))

    # Стовпчик 1: static_cast (небезпечний)
    f.append(text(50, 75, "Традиційний static_cast<Target>(v)", size=13, color=POS, anchor="start", bold=True))
    f.append(fitbox(50, 95, 270, 170,
                    "Поведінка:\n"
                    "• Мовчазне відкидання старших бітів\n"
                    "• Зміна знаку при знакових/незнакових типах\n\n"
                    "Приклад аварії:\n"
                    "int big = 300;\n"
                    "char c = static_cast<char>(big);\n"
                    "// c == 44 (втрата даних 300 != 44!)\n"
                    "Компілятор мовчить, баг іде в production.",
                    size=10, fill="#fff0f0", stroke=POS))

    # Стовпчик 2: gsl::narrow_cast (документований)
    f.append(text(345, 75, "Явний gsl::narrow_cast<Target>(v)", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(345, 95, 270, 170,
                    "Поведінка:\n"
                    "• Еквівалентний static_cast у рантаймі\n"
                    "• Повідомляє аналізатору: звуження свідоме\n\n"
                    "Призначення:\n"
                    "• Придушення попередження Core Check ES.46\n"
                    "• Використовується, коли інваріант доведено\n"
                    "математично (наприклад, v % 256).",
                    size=10, fill="#f0f4fc", stroke=NEG))

    # Стовпчик 3: gsl::narrow (безпечний з перевіркою)
    f.append(text(640, 75, "Перевірений gsl::narrow<Target>(v)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(640, 95, 270, 170,
                    "Поведінка:\n"
                    "• Виконує зворотне приведення у рантаймі\n"
                    "• static_cast<Source>(target) == source\n"
                    "• Перевіряє однаковість знаку (sign check)\n\n"
                    "Результат перевірки:\n"
                    "• Значення збережено -> повертає Target\n"
                    "• Значення спотворено -> кидає narrowing_error",
                    size=10, fill="#e8f6ee", stroke=FIELD))

    # Нижня смуга алгоритму верифікації gsl::narrow
    f.append(line(40, 285, 920, 285, color=MUTED, sw=1, dash="4 4"))
    f.append(text(50, 315, "Внутрішній алгоритм перевірки у gsl::narrow<Target>(Source val):", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 335, 860, 65,
                    "1. Target tgt = static_cast<Target>(val);\n"
                    "2. if (static_cast<Source>(tgt) != val || ((tgt < Target{}) != (val < Source{})))\n"
                    "       throw gsl::narrowing_error{};\n"
                    "3. return tgt;",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'narrowing-cast-matrix.svg'), W, H, *f,
           title="Звужуючі перетворення у GSL")


if __name__ == "__main__":
    fig_safety_layers()
    fig_not_null()
    fig_span()
    fig_narrowing_matrix()
    print("Усі 4 фігури згенеровано успішно.")
