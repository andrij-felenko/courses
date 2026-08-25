# -*- coding: utf-8 -*-
"""Фігури до теми «format і print: типобезпечне форматування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Архітектура std::format: компиляційна перевірка та стирання типів ───
def fig_formatting_architecture():
    W, H = 940, 480
    f = []

    f.append(text(470, 35, "Архітектура std::format: двофазна обробка та типобезпека", size=16, color=INK, anchor="middle", bold=True))

    # Фаза 1: Компіляція (Compile-time)
    f.append(fitbox(40, 65, 410, 180,
                    "1. Перевірка рядка формату (Compile-time Phase)\n\n"
                    "std::format(\"Температура: {:.2f} °C\", temp)\n"
                    "               ▲\n"
                    "               └─ std::basic_format_string<char, double>\n"
                    "                  consteval конструювання перевіряє\n"
                    "                  граматику та відповідність типів у під час компіляції!",
                    size=12, fill="#eef2f7", stroke=LINE))

    # Фаза 2: Пакування аргументів
    f.append(fitbox(490, 65, 410, 180,
                    "2. Стирання типів аргументів (Argument Packaging)\n\n"
                    "std::make_format_args(temp)\n"
                    "               ▲\n"
                    "               └─ Створює легковаговий масив std::format_args\n"
                    "                  Типи аргументів стіраються до таблиці\n"
                    "                  вказівників на функцій-форматирувачі (vtable)",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Лінії зв'язку між фазою 1, 2 і рушієм
    f.append(arrow(245, 245, 470, 280, color=LINE, sw=2))
    f.append(arrow(695, 245, 470, 280, color=FIELD, sw=2))

    # Фаза 3: Виконання (Runtime Engine)
    f.append(fitbox(200, 285, 540, 100,
                    "3. Диспетчеризація та форматування (Runtime Engine)\n\n"
                    "std::vformat_to(out_iter, format_str, format_args)\n"
                    "Викликає відповідні std::formatter<T>::format() для кожного елемента",
                    size=12, fill="#fff7e6", stroke=POS))

    # Запис у вихідний ітератор
    f.append(arrow(470, 385, 470, 415, color=POS, sw=2))
    f.append(fitbox(150, 420, 640, 45,
                    "Вихідний буфер: std::string / std::back_inserter / стековий масив / stdout",
                    size=12, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    render(os.path.join(OUT, 'formatting-architecture.svg'), W, H, *f,
           title="Архітектура форматування std::format")


# ── 2. Анатомія граматики специфікаторів формату ──────────────────────────
def fig_format_string_grammar():
    W, H = 940, 460
    f = []

    f.append(text(470, 35, "Анатомія рядка формату: структура специфікатора format-spec", size=16, color=INK, anchor="middle", bold=True))

    # Приклад синтаксису рядка
    f.append(fitbox(180, 65, 580, 45, "Синтаксис: {[arg_id] : [[fill]align] [sign] [#] [0] [width] [.precision] [type]}", size=13, fill="#f4f6f8", stroke=LINE, bold=True))

    # Приклад 1: {:*>+10.2f}
    f.append(text(50, 140, "Конкретний приклад: {:*>+10.2f}", size=15, color=FIELD, anchor="start", bold=True))

    elements = [
        (50, 165, 75, 75, "*", "Заповнювач\nfill='*'"),
        (135, 165, 75, 75, ">", "Вирівнювання\nalign=праворуч"),
        (220, 165, 75, 75, "+", "Знак\nsign=завжди +"),
        (305, 165, 75, 75, "#", "Альтернативний\n# (0x / .)"),
        (390, 165, 75, 75, "0", "Нулі\n0 (padding)"),
        (475, 165, 95, 75, "10", "Ширина\nwidth=10"),
        (580, 165, 95, 75, ".2", "Точність\nprecision=2"),
        (685, 165, 85, 75, "f", "Тип виводу\ntype=float"),
    ]

    for x, y, w, h, symbol, desc in elements:
        f.append(fitbox(x, y, w, h, f"'{symbol}'\n─────────\n{desc}", size=10, fill="#e8f6ee", stroke=FIELD))

    # Приклад виводу
    f.append(fitbox(50, 260, 840, 75,
                    "Результат для числа 3.14159:\n"
                    "std::format(\"{:*>+10.2f}\", 3.14159)  ==>  \"*****+3.14\"\n"
                    "(Ширина 10 символів, заповнення '*', знак '+', 2 знаки після коми)",
                    size=12, fill="#fff7e6", stroke=POS))

    # Додаткові прапорці типом
    f.append(fitbox(50, 355, 840, 80,
                    "Основні типи (type):\n"
                    "• d (decimal), x/X (hexadecimal), b/B (binary), o (octal)\n"
                    "• f/F (fixed float), e/E (scientific), g/G (general float)\n"
                    "• s (string), c (char), p (pointer), ? (escaped debug formatting у C++23)",
                    size=11, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, 'format-string-grammar.svg'), W, H, *f,
           title="Структура та граматика специфікаторів формату")


# ── 3. Шляхи виводу: std::cout vs printf vs std::print ────────────────────
def fig_print_vs_iostream_perf():
    W, H = 940, 440
    f = []

    f.append(text(470, 35, "Порівняння шляхів виводу: std::cout vs printf vs std::print", size=16, color=INK, anchor="middle", bold=True))

    # Шлях 1: std::cout
    f.append(fitbox(40, 65, 270, 310,
                    "std::cout << val1 << val2\n"
                    "───────────────\n"
                    "1. Декілька викликів operator<<\n"
                    "2. Динамічна обробка локалі\n"
                    "3. Внутрішній буфер std::streambuf\n"
                    "4. Синхронізація з stdio (lock)\n\n"
                    "Пастки:\n"
                    "❌ Повільний через iostream-буфер\n"
                    "❌ Зміна стану (hex, setw)\n"
                    "❌ Мішанина при багатопотоковості",
                    size=11, fill="#fdf2f2", stroke=POS))

    # Шлях 2: printf
    f.append(fitbox(335, 65, 270, 310,
                    "printf(\"%s: %d\\n\", str, val)\n"
                    "───────────────\n"
                    "1. Розбір рядка формату у runtime\n"
                    "2. Нетипобезпечні C-varargs (va_arg)\n"
                    "3. Буферизація через FILE*\n"
                    "4. Системний виклик write()\n\n"
                    "Пастки:\n"
                    "❌ Небезпечний: %s + int -> UB\n"
                    "❌ Немає підтримки власних типів\n"
                    "⚠️ Проблеми з UTF-8 на Windows",
                    size=11, fill="#fff7e6", stroke=POS))

    # Шлях 3: std::print
    f.append(fitbox(630, 65, 270, 310,
                    "std::print(\"{}: {}\\n\", str, val)\n"
                    "───────────────\n"
                    "1. Валідація формату під час компіляції\n"
                    "2. Форматування у стековий буфер\n"
                    "3. Атомарний прямоточний запис\n"
                    "4. Прямий виклик OS Unicode API\n\n"
                    "Переваги:\n"
                    "✅ Максимальна швидкість (fastest)\n"
                    "✅ Повна типобезпека (type safe)\n"
                    "✅ Нативна підтримка UTF-8 (OS API)",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 405, "std::print у C++23 об'єднує швидкість та типобезпеку std::format з прямоточним виводом у консоль", size=11, color=MUTED))

    render(os.path.join(OUT, 'print-vs-iostream-perf.svg'), W, H, *f,
           title="Порівняння шляхів виводу даних в ОС")


if __name__ == "__main__":
    fig_formatting_architecture()
    fig_format_string_grammar()
    fig_print_vs_iostream_perf()
    print("Всі 3 SVG фігури успішно згенеровано у img/")
