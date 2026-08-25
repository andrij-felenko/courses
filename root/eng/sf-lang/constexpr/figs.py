# -*- coding: utf-8 -*-
"""Генератор діаграм для теми constexpr: обчислення на етапі компіляції.
Використовує svgkit з кореневої папки scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_ctfe_interpreter():
    """1. Внутрішній інтерпретатор компілятора (CTFE pipeline)."""
    w, h = 880, 480
    frags = []

    # Заголовок / шапка схеми
    frags.append(text(440, 32, "Архітектура обчислення константних виразів (CTFE) у компіляторі", size=16, bold=True))

    # Ліва частина: Вхідний вихідний код
    frags.append(fitbox(30, 70, 220, 110, "Вихідний код C++\nconstexpr / consteval\nфункції та змінні", size=13, fill="#edf2f7", stroke="#4a5568", bold=True))

    # Стрілка від коду до Парсера/AST
    frags.append(arrow(250, 125, 295, 125, color=LINE, sw=2))

    # Центральний верхній блок: Синтаксичний і семантичний аналіз
    frags.append(fitbox(295, 70, 250, 110, "Синтаксичний аналіз (AST)\nСемантична перевірка типів\nВизначення константного контексту", size=13, fill="#edf2f7", stroke="#4a5568"))

    # Розгалуження: константний контекст чи динамічний?
    frags.append(arrow(420, 180, 420, 225, color=LINE, sw=2))

    # Блок вибору контексту
    frags.append(fitbox(310, 225, 220, 60, "Контекст виклику?\n(static_assert, template arg,\nconstexpr var, consteval)", size=12, fill="#fff8e1", stroke="#f57c00", bold=True))

    # Гілка ТАК: Внутрішній інтерпретатор компілятора (CTFE)
    frags.append(arrow(310, 255, 170, 255, color=FIELD, sw=2))
    frags.append(text(240, 245, "Константний (CTFE)", size=11, color=FIELD, bold=True))

    # Великий блок інтерпретатора CTFE
    frags.append(fitbox(30, 290, 280, 160, "Інтерпретатор AST / Байткод-VM\n(Constant Evaluator)\n\n• Емуляція цільової архітектури\n• Відстеження життєвого циклу об'єктів\n• Сувора валідація меж пам'яті\n• Переривання з помилкою при UB", size=12, fill="#e8f5e9", stroke=FIELD))

    # Вихід із CTFE: Чисте значення
    frags.append(arrow(170, 450, 440, 450, color=FIELD, sw=2))
    frags.append(arrow(440, 450, 440, 430, color=FIELD, sw=2))

    # Гілка НІ: Звичайна кодогенерація (IR / LLVM)
    frags.append(arrow(530, 255, 670, 255, color=NEG, sw=2))
    frags.append(text(600, 245, "Динамічний (Runtime)", size=11, color=NEG, bold=True))

    # Блок звичайної кодогенерації
    frags.append(fitbox(570, 290, 280, 80, "Генерація проміжного коду (IR)\nОптимізації компілятора\nГенерація машинних інструкцій", size=12, fill="#e3f2fd", stroke=NEG))

    # Зведення в кінцевий бінарник
    frags.append(arrow(710, 370, 710, 400, color=NEG, sw=2))
    frags.append(arrow(710, 400, 580, 400, color=NEG, sw=2))

    # Фінальний блок артефакту
    frags.append(fitbox(340, 370, 240, 60, "Фінальний образ (ELF / PE)\n• Сталі одразу в секції .rodata\n• Жодних обчислень на старті", size=12, fill="#f3e5f5", stroke="#7b1fa2", bold=True))

    render(os.path.join(IMG_DIR, "ctfe-interpreter.svg"), w, h, *frags)


def fig_evolution_timeline():
    """2. Еволюція constexpr від C++11 до C++26."""
    w, h = 900, 450
    frags = []

    frags.append(text(450, 30, "Еволюція обчислень під час компіляції в стандартах C++", size=16, bold=True))

    # Часова шкала (горизонтальна лінія зі стрілкою)
    frags.append(line(50, 75, 850, 75, color=LINE, sw=3))
    frags.append(arrow(840, 75, 870, 75, color=LINE, sw=3))

    steps = [
        ("C++11", 110, "#e8eaf6", "#3f51b5", "Народження constexpr\n\n• Тільки один return\n• Рекурсія замість циклів\n• ?: замість if\n• Без локальних змінних\n• Literal Types"),
        ("C++14", 280, "#e0f2f1", "#00796b", "Імперативність\n\n• Звичайні цикли (for/while)\n• Локальні змінні та їх мутація\n• Розгалуження if / switch\n• Декілька return\n• void constexpr методи"),
        ("C++17", 450, "#fff3e0", "#e65100", "Статичне розгалуження\n\n• if constexpr\n• constexpr лямбда-функції\n• constexpr у std::array\n• Автоматичний інлайн\n• Послаблення для типів"),
        ("C++20", 620, "#fce4ec", "#c2185b", "Повноцінна мова\n\n• consteval (тільки compile-time)\n• constinit (статична ініціалізація)\n• std::vector / string у CTFE\n• constexpr virtual методи\n• is_constant_evaluated()"),
        ("C++23/26", 790, "#f3e5f5", "#7b1fa2", "Зрілість і зручність\n\n• if consteval\n• constexpr для cmath та charconv\n• Зменшення обмежень пам'яті\n• Підготовка до статичної рефлексії"),
    ]

    for name, x, bg_col, border_col, desc in steps:
        # Точка на часовій осі
        frags.append(circle(x, 75, 8, fill=border_col, stroke="#ffffff", sw=2))
        frags.append(text(x, 58, name, size=13, color=border_col, bold=True))
        frags.append(line(x, 83, x, 110, color=border_col, sw=1.5, dash="3,3"))

        # Картка опису
        frags.append(fitbox(x - 75, 115, 150, 310, desc, size=11.5, fill=bg_col, stroke=border_col, pad=6))

    render(os.path.join(IMG_DIR, "evolution-timeline.svg"), w, h, *frags)


def fig_lut_generation():
    """3. Порівняння: Runtime обчислення проти Compile-Time LUT у .rodata."""
    w, h = 860, 430
    frags = []

    frags.append(text(430, 30, "Розподіл пам'яті: динамічний розрахунок проти статичної таблиці LUT", size=16, bold=True))

    # Ліва панель: Обчислення в Runtime
    frags.append(rect(40, 60, 360, 350, fill="#fffde7", stroke="#fbc02d", sw=1.5, rx=8))
    frags.append(text(220, 88, "Динамічне обчислення (Runtime)", size=14, color="#f57f17", bold=True))

    frags.append(fitbox(60, 110, 320, 70, "Код ініціалізації в .text\nПри кожному старті програми / виклику:\nВиконується цикл розрахунку (напр. CRC32 / sin)", size=11.5, fill="#ffffff", stroke="#fbc02d"))

    frags.append(arrow(220, 185, 220, 215, color=POS, sw=2))

    frags.append(fitbox(60, 220, 320, 85, "Використання ресурсів процесора:\n• Витрата тактів CPU та енергії живлення\n• Виділення буфера в RAM (.bss / .data)\n• Ризик гонитви станів під час ініціалізації", size=11.5, fill="#ffebee", stroke=POS))

    frags.append(fitbox(60, 325, 320, 65, "Підсумок: Додатковий оверхед часу,\nвитрата пам'яті RAM, код старту", size=12, fill="#fdecea", stroke=POS, bold=True))

    # Права панель: Генерація в Compile-time через constexpr
    frags.append(rect(460, 60, 360, 350, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(640, 88, "Compile-Time LUT (constexpr / consteval)", size=14, color=FIELD, bold=True))

    frags.append(fitbox(480, 110, 320, 70, "Розрахунок у компіляторі (CTFE)\nПід час збірки проєкту:\nКомпілятор сам виконує алгоритм і генерує масив", size=11.5, fill="#ffffff", stroke=FIELD))

    frags.append(arrow(640, 185, 640, 215, color=FIELD, sw=2))

    frags.append(fitbox(480, 220, 320, 85, "Нульовий оверхед під час виконання:\n• Таблиця кладеться безпосередньо в .rodata (Flash/ROM)\n• Нуль тактів CPU на ініціалізацію\n• Миттєвий доступ O(1) за індексом", size=11.5, fill="#e8f5e9", stroke=FIELD))

    frags.append(fitbox(480, 325, 320, 65, "Підсумок: RAM = 0 байт, старт = 0 мкс,\nчистий безпомилковий доступ", size=12, fill="#d4edda", stroke=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "lut-generation-memory.svg"), w, h, *frags)


def fig_ub_compile_error():
    """4. Невизначена поведінка (UB) у Runtime vs у constexpr (Compile-Time)."""
    w, h = 860, 420
    frags = []

    frags.append(text(430, 30, "Поведінка при помилках: Невизначена поведінка (UB) vs constexpr", size=16, bold=True))

    # Верхній блок: Помилкова операція (спільний тригер)
    frags.append(fitbox(230, 60, 400, 55, "Помилкова операція з коду\n(Вихід за межі масиву arr[10], ділення на 0,\nрозіменування nullptr, знакове переповнення)", size=12, fill="#fff3e0", stroke="#e65100", bold=True))

    # Стрілка ліворуч (Runtime)
    frags.append(arrow(330, 115, 200, 160, color=POS, sw=2))
    frags.append(text(210, 135, "Виконання в Runtime", size=11, color=POS, bold=True))

    # Стрілка праворуч (Compile-Time)
    frags.append(arrow(530, 115, 660, 160, color=FIELD, sw=2))
    frags.append(text(650, 135, "Виконання в constexpr", size=11, color=FIELD, bold=True))

    # Лівий блок: Наслідки в Runtime
    frags.append(rect(40, 165, 360, 230, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(220, 192, "Класичний Runtime (UB)", size=14, color=POS, bold=True))
    frags.append(fitbox(60, 215, 320, 160, "• Непередбачувана поведінка програми\n• Пошкодження пам'яті (Memory corruption)\n• Приховані вразливості безпеки\n• Можливе аварійне падіння (SIGSEGV)\n• Компілятор оптимізує код, вважаючи UB неможливим", size=11.5, fill="#ffffff", stroke=POS))

    # Правий блок: Наслідки в constexpr
    frags.append(rect(460, 165, 360, 230, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(640, 192, "Compile-Time Evaluator (CTFE)", size=14, color=FIELD, bold=True))
    frags.append(fitbox(480, 215, 320, 160, "• Порушення умов константного виразу\n• Компіляція НЕГАЙНО ЗУПИНЯЄТЬСЯ\n• Точне повідомлення про помилку від компілятора\n• Повний стек викликів функцій на момент збою\n• Нульовий шанс потрапляння UB у релізний бінарник", size=11.5, fill="#ffffff", stroke=FIELD))

    render(os.path.join(IMG_DIR, "ub-compile-error.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_ctfe_interpreter()
    fig_evolution_timeline()
    fig_lut_generation()
    fig_ub_compile_error()
    print("Всі фігури для constexpr успішно згенеровано.")
