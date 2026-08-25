# -*- coding: utf-8 -*-
"""Фігури до теми «Макроси тестування можливостей (__cpp_*)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_feature_detection_mechanisms():
    """Схема трьох рівнів тестування можливостей: препроцесор, ядро та бібліотека."""
    W, H = 960, 480
    out = []

    out.append(text(W / 2, 35, "Архітектура зондування можливостей у C++: від синтаксису до бібліотеки", size=15, bold=True))
    out.append(text(W / 2, 58, "Три незалежні рівні перевірки підтримки стандарту компілятором і стандартною бібліотекою", size=12, color=MUTED))

    col_w = 275
    gap = 35
    start_x = 30
    y_top = 85
    h_col = 250

    levels = [
        {
            "num": "Рівень 1",
            "title": "Оператори препроцесора",
            "subtitle": "Перевірка файлів і атрибутів",
            "fill": "#eff6ff",
            "stroke": "#2563eb",
            "items": [
                "__has_include(<header>)",
                "__has_include(\"custom.h\")",
                "__has_cpp_attribute(nodiscard)",
                "__has_cpp_attribute(likely)",
                "Безпечна перевірка без помилок"
            ]
        },
        {
            "num": "Рівень 2",
            "title": "Макроси ядра мови",
            "subtitle": "Синтаксис та семантика транслятора",
            "fill": "#f0fdf4",
            "stroke": "#16a34a",
            "items": [
                "__cpp_concepts >= 201907L",
                "__cpp_constexpr >= 201907L",
                "__cpp_structured_bindings",
                "__cpp_consteval >= 201811L",
                "Вбудовані у компілятор (без #include)"
            ]
        },
        {
            "num": "Рівень 3",
            "title": "Макроси бібліотеки STL",
            "subtitle": "Компоненти заголовка <version>",
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "items": [
                "__cpp_lib_span >= 202002L",
                "__cpp_lib_format >= 201907L",
                "__cpp_lib_expected >= 202202L",
                "__cpp_lib_ranges >= 201911L",
                "Доступні через <version> і заголовки"
            ]
        }
    ]

    for i, lv in enumerate(levels):
        px = start_x + i * (col_w + gap)
        cx = px + col_w / 2

        out.append(rect(px, y_top, col_w, h_col, fill=lv["fill"], stroke=lv["stroke"], sw=2, rx=8))
        out.append(text(cx, y_top + 26, lv["num"], size=12, color=lv["stroke"], bold=True))
        out.append(text(cx, y_top + 48, lv["title"], size=14, bold=True))
        out.append(text(cx, y_top + 68, lv["subtitle"], size=11, color=MUTED))
        out.append(line(px + 15, y_top + 80, px + col_w - 15, y_top + 80, color=lv["stroke"], sw=1))

        item_y = y_top + 104
        for item in lv["items"]:
            out.append(text(px + 18, item_y, "• " + item, size=11, color=INK, anchor="start"))
            item_y += 24

        # Стрілка вниз до споживача
        out.append(arrow(cx, y_top + h_col, cx, y_top + h_col + 38, color=LINE, sw=1.6))

    # Нижній спільний блок: Адаптивний код / Поліфіли
    bot_y = y_top + h_col + 40
    bot_w = W - 2 * start_x
    out.append(rect(start_x, bot_y, bot_w, 85, fill="#faf5ff", stroke="#9333ea", sw=2, rx=8))
    out.append(text(W / 2, bot_y + 24, "Споживач: Адаптивний вихідний код і шар кроскомпіляторних поліфілів", size=13, bold=True, color="#9333ea"))
    out.append(text(W / 2, bot_y + 46, "#if __cpp_lib_span >= 202002L  →  using std::span;  #else  →  using compat::span;", size=12, color=INK))
    out.append(text(W / 2, bot_y + 68, "Автоматичне перемикання між рідними можливостями стандарту та сумісними реалізаціями", size=11, color=MUTED))

    render(os.path.join(IMG, "feature-detection-mechanisms.svg"), W, H, *out)


def fig_macro_date_versioning():
    """Схема еволюції числових значень-дат на прикладі макросу __cpp_constexpr."""
    W, H = 960, 420
    out = []

    out.append(text(W / 2, 32, "Еволюція числових значень макросу: приклад __cpp_constexpr", size=15, bold=True))
    out.append(text(W / 2, 54, "Числові значення формату YYYYMML відображають конкретні розширення можливості у версіях стандарту", size=12, color=MUTED))

    # Хронологічна шкала
    y_line = 135
    out.append(line(50, y_line, 910, y_line, color=LINE, sw=3))

    milestones = [
        {
            "x": 100,
            "std": "C++11",
            "val": "200704L",
            "date": "Квітень 2007",
            "title": "Базовий constexpr",
            "details": ["Один return", "Константні вирази", "Літеральні типи"]
        },
        {
            "x": 280,
            "std": "C++14",
            "val": "201304L",
            "date": "Квітень 2013",
            "title": "Послаблення правил",
            "details": ["Цикли for/while", "Локальні змінні", "Кілька return"]
        },
        {
            "x": 480,
            "std": "C++17",
            "val": "201603L",
            "date": "Березень 2016",
            "title": "Лямбди та розгалуження",
            "details": ["if constexpr", "constexpr-лямбди", "Компактні шаблони"]
        },
        {
            "x": 680,
            "std": "C++20",
            "val": "201907L",
            "date": "Липень 2019",
            "title": "Динамічність і ООП",
            "details": ["Віртуальні виклики", "try/catch у константах", "Динамічна пам'ять"]
        },
        {
            "x": 860,
            "std": "C++23",
            "val": "202211L",
            "date": "Листопад 2022",
            "title": "Зняття обмежень",
            "details": ["Статичні змінні", "goto у compile-time", "Нелітеральні типи"]
        }
    ]

    for m in milestones:
        # Вузол на шкалі
        out.append(circle(m["x"], y_line, 8, fill="#2563eb", stroke="#ffffff", sw=2))

        # Верхній ярлик (стандарт і значення)
        out.append(rect(m["x"] - 55, y_line - 55, 110, 38, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=5))
        out.append(text(m["x"], y_line - 39, m["std"], size=12, bold=True, color="#2563eb"))
        out.append(text(m["x"], y_line - 22, m["val"], size=11, bold=True, color=INK))

        # Стрілка вниз до опису
        out.append(line(m["x"], y_line + 8, m["x"], y_line + 30, color=LINE, sw=1.2))

        # Картка з описом
        card_w = 150
        card_h = 175
        cx = m["x"]
        px = cx - card_w / 2
        card_y = y_line + 32

        out.append(rect(px, card_y, card_w, card_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        out.append(text(cx, card_y + 20, m["title"], size=11, bold=True))
        out.append(text(cx, card_y + 36, m["date"], size=10, color=MUTED))
        out.append(line(px + 10, card_y + 46, px + card_w - 10, card_y + 46, color=LINE, sw=0.8))

        detail_y = card_y + 66
        for d in m["details"]:
            out.append(text(px + 12, detail_y, "• " + d, size=10, color=INK, anchor="start"))
            detail_y += 20

    render(os.path.join(IMG, "macro-date-versioning.svg"), W, H, *out)


def fig_polyfill_cascade_flow():
    """Блок-схема каскадного зондування заголовків і вибору реалізації поліфілу."""
    W, H = 960, 470
    out = []

    out.append(text(W / 2, 32, "Алгоритм каскадного зондування можливостей і підключення поліфілів", size=15, bold=True))
    out.append(text(W / 2, 54, "Покрокове визначення наявності компонента стандартної бібліотеки або перемикання на резерв", size=12, color=MUTED))

    # Крок 1: Перевірка наявності <version>
    b1_x, b1_y, b1_w, b1_h = 40, 110, 240, 95
    out.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=6))
    out.append(text(b1_x + b1_w / 2, b1_y + 24, "Крок 1: Зондування <version>", size=12, bold=True, color="#2563eb"))
    out.append(text(b1_x + b1_w / 2, b1_y + 46, "#if __has_include(<version>)", size=11, bold=True))
    out.append(text(b1_x + b1_w / 2, b1_y + 66, "   #include <version>", size=11))
    out.append(text(b1_x + b1_w / 2, b1_y + 84, "#endif", size=11))

    # Стрілка 1 -> 2
    out.append(arrow(b1_x + b1_w, b1_y + b1_h / 2, b1_x + b1_w + 35, b1_y + b1_h / 2, color=LINE, sw=1.6))

    # Крок 2: Зондування макросу конкретної фічі
    b2_x, b2_y, b2_w, b2_h = b1_x + b1_w + 35, 105, 275, 105
    out.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    out.append(text(b2_x + b2_w / 2, b2_y + 24, "Крок 2: Перевірка макросу фічі", size=12, bold=True, color="#d97706"))
    out.append(text(b2_x + b2_w / 2, b2_y + 48, "#if defined(__cpp_lib_expected)", size=11, bold=True))
    out.append(text(b2_x + b2_w / 2, b2_y + 68, "    && __cpp_lib_expected >= 202202L", size=11, bold=True))
    out.append(text(b2_x + b2_w / 2, b2_y + 90, "Числове порівняння версії WG21", size=10, color=MUTED))

    # Розгалуження ТАК (вправо-вгору) та НІ (вправо-вниз)
    branch_x = b2_x + b2_w
    branch_y = b2_y + b2_h / 2

    # Гілка ТАК -> STL
    out.append(line(branch_x, branch_y, branch_x + 35, branch_y - 45, color="#16a34a", sw=1.8))
    out.append(arrow(branch_x + 35, branch_y - 45, branch_x + 75, branch_y - 45, color="#16a34a", sw=1.8))
    out.append(text(branch_x + 30, branch_y - 55, "ТАК (Підтримується)", size=11, bold=True, color="#16a34a"))

    b3_yes_x, b3_yes_y, b3_yes_w, b3_yes_h = branch_x + 75, 75, 265, 95
    out.append(rect(b3_yes_x, b3_yes_y, b3_yes_w, b3_yes_h, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=6))
    out.append(text(b3_yes_x + b3_yes_w / 2, b3_yes_y + 24, "Рідна стандартна реалізація", size=12, bold=True, color="#16a34a"))
    out.append(text(b3_yes_x + b3_yes_w / 2, b3_yes_y + 46, "#include <expected>", size=11, bold=True))
    out.append(text(b3_yes_x + b3_yes_w / 2, b3_yes_y + 66, "namespace compat {", size=11))
    out.append(text(b3_yes_x + b3_yes_w / 2, b3_yes_y + 84, "    using std::expected; }", size=11, bold=True))

    # Гілка НІ -> Поліфіл
    out.append(line(branch_x, branch_y, branch_x + 35, branch_y + 65, color="#dc2626", sw=1.8))
    out.append(arrow(branch_x + 35, branch_y + 65, branch_x + 75, branch_y + 65, color="#dc2626", sw=1.8))
    out.append(text(branch_x + 30, branch_y + 55, "НІ (Відсутня/застаріла)", size=11, bold=True, color="#dc2626"))

    b3_no_x, b3_no_y, b3_no_w, b3_no_h = branch_x + 75, 205, 265, 105
    out.append(rect(b3_no_x, b3_no_y, b3_no_w, b3_no_h, fill="#fef2f2", stroke="#dc2626", sw=2, rx=6))
    out.append(text(b3_no_x + b3_no_w / 2, b3_no_y + 24, "Резервний сумісний поліфіл", size=12, bold=True, color="#dc2626"))
    out.append(text(b3_no_x + b3_no_w / 2, b3_no_y + 46, "#include \"compat/fallback_expected.hpp\"", size=10, bold=True))
    out.append(text(b3_no_x + b3_no_w / 2, b3_no_y + 66, "namespace compat {", size=11))
    out.append(text(b3_no_x + b3_no_w / 2, b3_no_y + 86, "    using fallback::expected; }", size=11, bold=True))

    # Фінальний злив у користувацький інтерфейс
    fin_y = 350
    out.append(line(b3_yes_x + b3_yes_w / 2, b3_yes_y + b3_yes_h, b3_yes_x + b3_yes_w / 2, fin_y - 15, color=LINE, sw=1.4))
    out.append(line(b3_no_x + b3_no_w / 2, b3_no_y + b3_no_h, b3_no_x + b3_no_w / 2, fin_y - 15, color=LINE, sw=1.4))
    out.append(line(b3_yes_x + b3_yes_w / 2, fin_y - 15, b3_no_x + b3_no_w / 2, fin_y - 15, color=LINE, sw=1.4))
    out.append(arrow(W / 2, fin_y - 15, W / 2, fin_y, color=LINE, sw=1.6))

    out.append(rect(40, fin_y, W - 80, 80, fill="#faf5ff", stroke="#9333ea", sw=2, rx=8))
    out.append(text(W / 2, fin_y + 24, "Уніфікований клієнтський код (User Code)", size=13, bold=True, color="#9333ea"))
    out.append(text(W / 2, fin_y + 46, "compat::expected<int, std::string_view> result = parse_packet(buffer);", size=12, bold=True))
    out.append(text(W / 2, fin_y + 66, "Код залишається на 100% ідентичним незалежно від версії компілятора та наявності C++23", size=11, color=MUTED))

    render(os.path.join(IMG, "polyfill-cascade-flow.svg"), W, H, *out)


if __name__ == "__main__":
    fig_feature_detection_mechanisms()
    fig_macro_date_versioning()
    fig_polyfill_cascade_flow()
    print("Фігури успішно згенеровано.")
