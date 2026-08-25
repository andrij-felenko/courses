# -*- coding: utf-8 -*-
"""Фігури до теми «Core Guidelines: узгоджені правила стилю й безпеки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Еволюція підходів до безпеки C++ ──────────────────────────────────
def fig_evolution_comparison():
    W, H = 960, 430
    f = []

    f.append(text(480, 32, "Еволюція парадигм безпеки та культури коду в C++", size=16, color=INK, anchor="middle", bold=True))

    # Колонка 1: 1990-ті
    f.append(text(170, 75, "1990-ті: Ручна дисципліна (C із класами)", size=13, color=POS, anchor="middle", bold=True))
    f.append(fitbox(30, 95, 280, 240,
                    "Практика:\n"
                    "• Ручне виділення malloc/free, new/delete\n"
                    "• Нетипізовані буфери void* та C-масиви\n"
                    "• Сирі вказівники володіють пам'яттю\n"
                    "• Сигналізація помилок через int коди\n\n"
                    "Наслідки:\n"
                    "• Регулярні витоки пам'яті (Leaks)\n"
                    "• Use-After-Free та подвійне звільнення\n"
                    "• ~70% вразливостей безпеки (CVE)\n"
                    "• Помилки знаходять користувачі",
                    size=11, fill="#fdf2f2", stroke=POS))

    # Колонка 2: 2000-ні
    f.append(text(480, 75, "2000-ні: Книжкові правила та гайди компаній", size=13, color=NEG, anchor="middle", bold=True))
    f.append(fitbox(340, 95, 280, 240,
                    "Практика:\n"
                    "• Книги Скотта Меєрса (Effective C++)\n"
                    "• Google C++ Style Guide, запрети фіч\n"
                    "• Ручний код-рев'ю колегами по команді\n"
                    "• Поява std::auto_ptr та boost::shared_ptr\n\n"
                    "Наслідки:\n"
                    "• Суб'єктивність трактування правил\n"
                    "• Людський фактор пропускає витоки\n"
                    "• Відсутність єдиного стандарту індустрії\n"
                    "• Заборона корисних фіч замість правил",
                    size=11, fill="#f0f4fd", stroke=NEG))

    # Колонка 3: 2015+
    f.append(text(790, 75, "2015+: C++ Core Guidelines & Статаналіз", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(fitbox(650, 95, 280, 240,
                    "Практика:\n"
                    "• Формальний звід правил Страуструпа/Саттера\n"
                    "• Залізне правило володіння (RAII, smart ptrs)\n"
                    "• Бібліотека підтримки GSL (span, not_null)\n"
                    "• Автоматичний аналіз (Clang-Tidy, MSVC)\n\n"
                    "Наслідки:\n"
                    "• Помилки блокуються на етапі компіляції\n"
                    "• Механічний аудит через CI/CD конвеєр\n"
                    "• Профілі безпеки (Type, Bounds, Lifetime)\n"
                    "• Швидкість C++ без жертв безпекою",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Підсумок знизу
    f.append(rect(30, 355, 900, 50, fill="#f8fafc", stroke=LINE, sw=1.2))
    f.append(text(480, 385, "Перехід: від «пам'ятай сотні заборон у голові» до «компілятор механічно гарантує відсутність дефектів»", size=12, color=INK, anchor="middle", bold=True))

    render(os.path.join(OUT, 'evolution-comparison.svg'), W, H, *f,
           title="Еволюція підходів до безпеки C++")


# ── 2. Модель володіння ресурсами ─────────────────────────────────────────
def fig_ownership_model():
    W, H = 960, 440
    f = []

    f.append(text(480, 32, "Модель володіння та семантика доступу в C++ Core Guidelines", size=16, color=INK, anchor="middle", bold=True))

    # Верхній ряд: Власники ресурсів (Owners)
    f.append(text(240, 75, "Власники ресурсів (Керують життєвим циклом через RAII)", size=13, color=FIELD, anchor="middle", bold=True))

    f.append(fitbox(30, 95, 420, 120,
                    "Одноосібне володіння: std::unique_ptr<T>\n"
                    "• Повний контроль над ресурсом у купі\n"
                    "• Заборонено копіювання, передача через std::move\n"
                    "• Деструктор гарантовано звільняє пам'ять",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(480, 95, 450, 120,
                    "Спільне володіння: std::shared_ptr<T> / weak_ptr<T>\n"
                    "• Атомарний лічильник посилань (Control Block)\n"
                    "• Використовується ЛИШЕ коли власників справді кілька\n"
                    "• weak_ptr запобігає циклічним залежностям",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Нижня частина: Неволодіючі спостерігачі (Borrowers)
    f.append(text(480, 245, "Неволодіючі позичальники (Передаються у функції як параметри)", size=13, color=NEG, anchor="middle", bold=True))

    f.append(fitbox(30, 265, 280, 140,
                    "Посилання: T& / const T&\n"
                    "• Обов'язковий аргумент\n"
                    "• Гарантовано не null\n"
                    "• const T& — читання без копії\n"
                    "• T& — модифікація in-place",
                    size=11, fill="#f0f4fd", stroke=NEG))

    f.append(fitbox(340, 265, 280, 140,
                    "Вказівники: T* / not_null<T*>\n"
                    "• T* — опціональний об'єкт (може бути nullptr)\n"
                    "• not_null<T*> — гарантовано дійсний вказівник\n"
                    "• СУВОРО ЗАБОРОНЕНО викликати delete над T*!\n"
                    "• Вказівник ніколи не володіє ресурсом",
                    size=11, fill="#f0f4fd", stroke=NEG))

    f.append(fitbox(650, 265, 280, 140,
                    "Буфери: std::span<T> / string_view\n"
                    "• Перегляд неперервного масиву\n"
                    "• Зберігає пару [pointer, size]\n"
                    "• Захист від виходу за межі масиву\n"
                    "• Заміна небезпечної пари (T* data, int n)",
                    size=11, fill="#f0f4fd", stroke=NEG))

    render(os.path.join(OUT, 'ownership-model.svg'), W, H, *f,
           title="Модель володіння ресурсами в Core Guidelines")


# ── 3. Архітектура розділів та профілів ───────────────────────────────────
def fig_rule_architecture():
    W, H = 960, 440
    f = []

    f.append(text(480, 30, "Структура розділів C++ Core Guidelines та Профілі Безпеки", size=16, color=INK, anchor="middle", bold=True))

    # Ліва колонка: Основні розділи керівних принципів
    f.append(text(250, 68, "Тематичні розділи правил (Sections)", size=13, color=INK, anchor="middle", bold=True))

    sections = [
        ("P: Philosophy", "Фундаментальні цілі: виражати наміри в типах, стандартний C++, RAII", "#eef2ff"),
        ("I: Interfaces", "Явні інтерфейси, заборона глобальних змінних, сильна типізація", "#f0fdf4"),
        ("F: Functions & C: Classes", "Короткі функції, Rule of Zero/Five, незмінні інваріанти класів", "#fefce8"),
        ("ES: Expr & Statements", "Заборона небезпечних кастів, явна ініціалізація, auto, без goto", "#fff7ed"),
        ("Per, CP, E: Perf, Concurrency, Errors", "Zero-overhead абстракції, безпечні потоки, RAII-блокування, винятки", "#faf5ff"),
    ]

    y_pos = 90
    for name, desc, bg_col in sections:
        f.append(fitbox(30, y_pos, 440, 52,
                        name + "\n" + desc,
                        size=11, fill=bg_col, stroke=LINE))
        y_pos += 62

    # Права колонка: Профілі безпеки (Safety Profiles)
    f.append(text(710, 68, "Профілі автоматизованої безпеки (Enforcement Profiles)", size=13, color=FIELD, anchor="middle", bold=True))

    f.append(fitbox(510, 90, 420, 90,
                    "Type Safety Profile (Типобезпека)\n"
                    "• Заборона reinterpret_cast та C-style casts\n"
                    "• Заборона небезпечних varargs (...)\n"
                    "• Заборона нетипізованих union (використовувати std::variant)",
                    size=11, fill="#fdf2f2", stroke=POS))

    f.append(fitbox(510, 195, 420, 90,
                    "Bounds Safety Profile (Безпека меж пам'яті)\n"
                    "• Заборона адресної арифметики над сирими вказівниками\n"
                    "• Заборона C-масивів у публічних інтерфейсах\n"
                    "• Вимога використовувати std::span<T> та std::array",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(fitbox(510, 300, 420, 90,
                    "Lifetime Safety Profile (Безпека життєвого циклу)\n"
                    "• Статичне виявлення висячих посилань (Dangling References)\n"
                    "• Відстеження повернення посилань на локальні змінні стека\n"
                    "• Контроль валідності ітераторів та анулювання вказівників",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Стрілка між розділами та профілями
    f.append(arrow(475, 230, 505, 230, color=FIELD, sw=2.5))

    render(os.path.join(OUT, 'rule-architecture.svg'), W, H, *f,
           title="Архітектура розділів Core Guidelines")


# ── 4. Конвеєр перевірки та придушення винятків ──────────────────────────
def fig_linter_enforcement():
    W, H = 960, 430
    f = []

    f.append(text(480, 30, "Конвеєр автоматичного аудиту через Clang-Tidy та MSVC Core Check", size=16, color=INK, anchor="middle", bold=True))

    # Блок 1: Вихідний код
    f.append(fitbox(30, 80, 180, 80,
                    "Вихідний код C++\n"
                    "source.cpp, headers.h\n"
                    "CMake / Ninja компіляція",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(215, 120, 265, 120, color=LINE, sw=2))

    # Блок 2: Інструменти статичного аналізу
    f.append(fitbox(270, 70, 260, 100,
                    "Статичний аналізатор\n"
                    "• clang-tidy: cppcoreguidelines-*\n"
                    "• MSVC: /analyze (C++ Core Check)\n"
                    "• Перевірка контракту правил",
                    size=11, fill="#eef2ff", stroke=NEG))

    f.append(arrow(535, 120, 585, 120, color=LINE, sw=2))

    # Блок 3: Розгалуження рішення
    f.append(fitbox(590, 80, 160, 80,
                    "Результат перевірки:\n"
                    "Чи знайдено\n"
                    "порушення правил?",
                    size=11, fill="#fff7e6", stroke=POS))

    # Гілка 1: Немає порушень -> Успіх
    f.append(arrow(755, 120, 805, 120, color=FIELD, sw=2))
    f.append(fitbox(810, 80, 120, 80,
                    "Успіх (OK)\n"
                    "CI/CD збірка\n"
                    "дозволена",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Гілка 2: Є порушення -> Вниз
    f.append(arrow(670, 165, 670, 235, color=POS, sw=2))

    f.append(fitbox(540, 240, 260, 80,
                    "Виявлено порушення правила!\n"
                    "Наприклад: cppcoreguidelines-owning-memory\n"
                    "Чи є це легітимним винятком?",
                    size=11, fill="#fdf2f2", stroke=POS))

    # Розгалуження внизу: Легітимний виняток чи дефект
    f.append(arrow(535, 280, 425, 280, color=NEG, sw=2))
    f.append(fitbox(150, 240, 270, 80,
                    "Легітимний виняток (System Driver / Allocator)\n"
                    "• Документування: [[gsl::suppress(...)]]\n"
                    "• Коментар з доказом інваріанту\n"
                    "• Локальна ізоляція коду",
                    size=11, fill="#f0f4fd", stroke=NEG))

    f.append(arrow(285, 325, 285, 360, color=FIELD, sw=1.5))
    f.append(line(285, 360, 870, 360, color=FIELD, sw=1.5))
    f.append(arrow(870, 360, 870, 165, color=FIELD, sw=1.5))

    f.append(arrow(670, 325, 670, 365, color=POS, sw=2))
    f.append(fitbox(540, 370, 260, 50,
                    "Звичайний дефект / антипатерн\n"
                    "CI блокує злиття гілки -> Рефакторинг",
                    size=11, fill="#fdf2f2", stroke=POS))

    render(os.path.join(OUT, 'linter-enforcement.svg'), W, H, *f,
           title="Конвеєр статичного аналізу Core Guidelines")


if __name__ == '__main__':
    fig_evolution_comparison()
    fig_ownership_model()
    fig_rule_architecture()
    fig_linter_enforcement()
    print("Всі 4 фігури успішно згенеровано.")
