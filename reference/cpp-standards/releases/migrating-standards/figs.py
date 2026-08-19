# -*- coding: utf-8 -*-
"""Фігури до теми «Перехід проєкту на новіший стандарт»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_migration_pipeline():
    """Фазовий конвеєр міграції великої кодової бази."""
    W, H = 1040, 500
    out = []

    out.append(text(W / 2, 48, "Послідовний інженерний маршрут: від аналізу залежностей до закріплення стандарту", size=13, color=MUTED))

    # 5 послідовних фаз
    col_w = 180
    gap = 20
    start_x = 30
    y_top = 75
    h_col = 390

    phases = [
        {
            "num": "Фаза 1",
            "title": "Аудит і залежності",
            "subtitle": "Оцінка кодової бази",
            "items": ["Аудит third-party ліб", "Сумісність ABI і toolchain", "Перевірка ODR-ризиків", "Фіксація бейзлайну тестів"],
            "fill": "#eff6ff",
            "stroke": NEG,
            "desc": ["Картування залежностей,", "виявлення вендорних", "блокерів та оновлення STL"]
        },
        {
            "num": "Фаза 2",
            "title": "Оновлення компілятора",
            "subtitle": "Сучасний тулчейн",
            "items": ["Новий GCC/Clang/MSVC", "Старий прапорець -std", "Усунення -Wdeprecated", "Ввімкнення -Werror в CI"],
            "fill": "#f0fdf4",
            "stroke": FIELD,
            "desc": ["Збірка на сучасному", "компіляторі зі старим", "діалектом без варнінгів"]
        },
        {
            "num": "Фаза 3",
            "title": "Авторефакторинг",
            "subtitle": "Clang-Tidy Modernize",
            "items": ["modernize-use-nullptr", "modernize-use-override", "Заміна std::auto_ptr", "modernize-use-using"],
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "desc": ["Автоматизована правка", "AST-шаблонів частинами", "через окремі PR"]
        },
        {
            "num": "Фаза 4",
            "title": "Підняття прапорця",
            "subtitle": "Перемикання стандарту",
            "items": ["Зміна -std у CMake", "Правка розривних змін", "Виправлення RVO/Copy", "Адаптація агрегатів"],
            "fill": "#fdf2f8",
            "stroke": POS,
            "desc": ["Фіксація нового стандарту", "знизу вгору по DAG-графу", "бібліотек проєкту"]
        },
        {
            "num": "Фаза 5",
            "title": "CI/CD верифікація",
            "subtitle": "Захист від регресій",
            "items": ["Матриця компіляторів", "ASan / UBSan / TSan", "Заборона legacy-коду", "Розгортання нових фіч"],
            "fill": "#faf5ff",
            "stroke": "#7e22ce",
            "desc": ["Санітайзери, регресійні", "тести та фіксація", "нових правил у лінтерах"]
        }
    ]

    for i, st in enumerate(phases):
        cx = start_x + i * (col_w + gap) + col_w / 2

        # Фонова картка
        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=st["fill"], stroke=st["stroke"], sw=2, rx=8))

        # Заголовки
        out.append(text(cx, y_top + 24, st["num"], size=12, color=st["stroke"], bold=True))
        out.append(text(cx, y_top + 46, st["title"], size=13, bold=True))
        out.append(text(cx, y_top + 68, st["subtitle"], size=11, color=MUTED, bold=True))

        # Лінія-роздільник
        out.append(line(cx - col_w / 2 + 10, y_top + 80, cx + col_w / 2 - 10, y_top + 80, color=st["stroke"], sw=1))

        # Список кроків
        item_y = y_top + 104
        for item in st["items"]:
            bb, _, _ = textbox(cx, item_y, item, size=10, pad=5, fill="#ffffff", stroke="#d1d5db", sw=1, min_w=col_w - 20)
            out.append(bb)
            item_y += 34

        # Опис внизу
        out.append(line(cx - col_w / 2 + 10, y_top + 316, cx + col_w / 2 - 10, y_top + 316, color="#d1d5db", sw=1))
        out.append(mtext(cx, y_top + 338, st["desc"], size=11, color=INK, lh=1.35))

        # Стрілка переходу
        if i < len(phases) - 1:
            arr_x1 = cx + col_w / 2 + 3
            arr_x2 = arr_x1 + gap - 6
            arr_y = y_top + 190
            out.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))

    render(os.path.join(IMG, 'migration-pipeline.svg'), W, H, *out,
           title="Фазовий конвеєр міграції проєкту на новіший стандарт C++")


def fig_breaking_changes():
    """Карта критичних розривних змін (Breaking Changes) за стандартами."""
    W, H = 1000, 480
    out = []

    out.append(text(W / 2, 48, "Ключові зміни семантики ядра мови та STL, що ламають наявний робочий код", size=13, color=MUTED))

    cols = [
        {
            "std": "C++98/03 → C++11",
            "color": NEG,
            "bg": "#eff6ff",
            "changes": [
                ("Заборона CoW у std::string", "Dual ABI у GCC, O(1) для size/const ref"),
                ("Деструктори типово noexcept", "throw під час руйнування викликає terminate"),
                ("Звужувальні перетворення {}", "Заборонено double->int або int->char у {}"),
                ("Rule of 0/3/5 & Move Semantics", "Користувацький деструктор блокує move"),
                ("Вилучено export template", "Поява ключового слова nullptr замість NULL")
            ]
        },
        {
            "std": "C++11/14 → C++17",
            "color": "#d97706",
            "bg": "#fffbeb",
            "changes": [
                ("Вилучено std::auto_ptr", "Обов'язкова заміна на std::unique_ptr"),
                ("Вилучено старі функтори STL", "ptr_fun, bind1st, unary_function зникли"),
                ("Вилучено register і триграфи", "register і послідовності ??= викликають error"),
                ("noexcept став частиною типу", "void(*)() noexcept не приводиться до void(*)()"),
                ("Обов'язковий RVO для prvalue", "prvalue не матеріалізується, новий життєвий цикл")
            ]
        },
        {
            "std": "C++17 → C++20",
            "color": POS,
            "bg": "#fdf2f8",
            "changes": [
                ("Агрегати без конструкторів", "Будь-який T() = default блокує T{...}"),
                ("Реверсивне порівняння <=>", "Неоднозначність перевантажених == та !="),
                ("Новий тип char8_t", "u8\"str\" тепер const char8_t*, а не char*"),
                ("Вилучено std::is_pod", "Заміна на std::is_standard_layout/trivial"),
                ("Зарезервовано нові слова", "concept, requires, consteval ламають імена")
            ]
        }
    ]

    col_w = 295
    gap = 25
    start_x = 45
    y_top = 75
    h_col = 375

    for i, col in enumerate(cols):
        cx = start_x + i * (col_w + gap) + col_w / 2

        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=col["bg"], stroke=col["color"], sw=2, rx=8))
        out.append(text(cx, y_top + 28, col["std"], size=14, color=col["color"], bold=True))
        out.append(line(cx - col_w / 2 + 12, y_top + 42, cx + col_w / 2 - 12, y_top + 42, color=col["color"], sw=1.5))

        cur_y = y_top + 68
        for title, desc in col["changes"]:
            card_h = 48
            out.append(rect(cx - col_w / 2 + 10, cur_y - 14, col_w - 20, card_h, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
            out.append(text(cx, cur_y + 4, title, size=11, bold=True, color=INK))
            out.append(text(cx, cur_y + 22, desc, size=9.5, color=MUTED))
            cur_y += 58

    render(os.path.join(IMG, 'breaking-changes-matrix.svg'), W, H, *out,
           title="Карта розривних змін семантики за поколіннями стандартів C++")


def fig_ci_matrix():
    """Матриця компіляторів та рівнів санітайзерів у CI/CD."""
    W, H = 980, 420
    out = []

    out.append(text(W / 2, 48, "Багаторівнева верифікація для виявлення дефектів оптимізатора й розривів сумісності", size=13, color=MUTED))

    # Ліва частина: Матриця компіляторів
    box_w = 420
    box_h = 320
    x_left = 50
    y_top = 75

    out.append(rect(x_left, y_top, box_w, box_h, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    out.append(text(x_left + box_w / 2, y_top + 26, "Матриця збірки (Compiler Matrix)", size=13, color=NEG, bold=True))
    out.append(line(x_left + 15, y_top + 40, x_left + box_w - 15, y_top + 40, color=NEG, sw=1))

    compilers = [
        ("GCC 9 / 11 / 13", "Linux x86_64 / AArch64", "-std=c++11, -std=c++17, -std=c++20"),
        ("Clang 12 / 15 / 17", "Linux / macOS Apple Silicon", "-Wall -Wextra -Werror -Wdeprecated"),
        ("MSVC 2019 / 2022", "Windows x64 / ARM64", "/permissive- /Zc:__cplusplus /std:c++latest"),
        ("Cross Toolchains", "ARM Embedded (GCC 10.3)", "Bare-metal без винятків / -fno-exceptions")
    ]

    item_y = y_top + 68
    for comp, platform, flags in compilers:
        out.append(rect(x_left + 15, item_y - 12, box_w - 30, 48, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        out.append(text(x_left + 25, item_y + 4, comp, size=11, bold=True, color=INK, anchor="start"))
        out.append(text(x_left + box_w - 25, item_y + 4, platform, size=10, color=MUTED, anchor="end"))
        out.append(text(x_left + 25, item_y + 22, flags, size=9.5, color=LINE, anchor="start"))
        item_y += 58

    # Центральна стрілка перевірки
    arr_y = y_top + box_h / 2
    out.append(arrow(x_left + box_w + 8, arr_y, x_left + box_w + 52, arr_y, color=LINE, sw=2.5))
    out.append(text(x_left + box_w + 30, arr_y - 12, "Тести", size=11, color=LINE, bold=True))

    # Права частина: Інструменти діагностики та санітайзери
    x_right = x_left + box_w + 60
    out.append(rect(x_right, y_top, box_w, box_h, fill="#fdf2f8", stroke=POS, sw=2, rx=8))
    out.append(text(x_right + box_w / 2, y_top + 26, "Динамічний і статичний аналіз", size=13, color=POS, bold=True))
    out.append(line(x_right + 15, y_top + 40, x_right + box_w - 15, y_top + 40, color=POS, sw=1))

    sanitizers = [
        ("AddressSanitizer (ASan)", "Пам'ять та витоки", "Ловить Use-after-move, memory corruption, OOB"),
        ("UndefinedBehavior (UBSan)", "Невизначена поведінка", "Зсуви бітів, переповнення знакових, null deref"),
        ("ThreadSanitizer (TSan)", "Стан перегонів (Races)", "Гонки даних, порушення інваріантів CoW/lock-free"),
        ("Clang-Tidy CI Gate", "Статичний контроль", "Блокування виклику застарілих API у нових PR")
    ]

    item_y = y_top + 68
    for san, tag, desc in sanitizers:
        out.append(rect(x_right + 15, item_y - 12, box_w - 30, 48, fill="#ffffff", stroke="#fbcfe8", sw=1, rx=4))
        out.append(text(x_right + 25, item_y + 4, san, size=11, bold=True, color=POS, anchor="start"))
        out.append(text(x_right + box_w - 25, item_y + 4, tag, size=10, color=MUTED, anchor="end"))
        out.append(text(x_right + 25, item_y + 22, desc, size=9.5, color=INK, anchor="start"))
        item_y += 58

    render(os.path.join(IMG, 'ci-matrix-migration.svg'), W, H, *out,
           title="Матриця збірки та динамічний аналіз у конвеєрі CI/CD")


def main():
    fig_migration_pipeline()
    fig_breaking_changes()
    fig_ci_matrix()
    print("Усі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
