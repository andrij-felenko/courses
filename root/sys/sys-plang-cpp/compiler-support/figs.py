# -*- coding: utf-8 -*-
"""Фігури до теми «Підтримка стандартів компіляторами й прапорці»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_compiler_matrix_pipeline():
    """Схема проходження стандарту ISO C++ через компілятори, макроси можливостей та код користувача."""
    W, H = 1000, 500
    out = []

    out.append(text(W / 2, 45, "Від тексту стандарту ISO до адаптивного сирцевого коду через макроси можливостей", size=13, color=MUTED))

    # 4 вертикальні рівні
    col_w = 215
    gap = 26
    start_x = 35
    y_top = 70
    h_col = 400

    stages = [
        {
            "num": "Рівень 1",
            "title": "Специфікація ISO",
            "subtitle": "WG21 International Standard",
            "fill": "#eff6ff",
            "stroke": "#2563eb",
            "items": [
                "Текст ISO/IEC 14882",
                "Нормативні папери (P-papers)",
                "Вимоги до синтаксису ядра",
                "Специфікація бібліотеки STL",
                "Звіт SD-6 (Feature Macros)"
            ],
            "desc": ["Єдине теоретичне", "джерело істини", "без коду трансляторів"]
        },
        {
            "num": "Рівень 2",
            "title": "Імплементація трійки",
            "subtitle": "Фронтенди та бібліотеки STL",
            "fill": "#f0fdf4",
            "stroke": "#16a34a",
            "items": [
                "GCC (G++ і libstdc++)",
                "LLVM / Clang (Clang і libc++)",
                "MSVC (c1xx/c2 і MSVC STL)",
                "Apple Clang / EDG / Intel",
                "Незалежні релізи версій"
            ],
            "desc": ["Роздільна реалізація", "синтаксису мови", "та класів бібліотеки"]
        },
        {
            "num": "Рівень 3",
            "title": "Зондування фіч",
            "subtitle": "Feature Test Macros & <version>",
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "items": [
                "Заголовок <version>",
                "Макроси ядра: __cpp_concepts",
                "Макроси STL: __cpp_lib_format",
                "Атрибути: __has_cpp_attribute",
                "Файли: __has_include"
            ],
            "desc": ["Стандартизовані дати", "виду YYYYMML для", "перевірки готовності"]
        },
        {
            "num": "Рівень 4",
            "title": "Адаптивний код",
            "subtitle": "Поліфіли та збірка",
            "fill": "#faf5ff",
            "stroke": "#9333ea",
            "items": [
                "#if __cpp_lib_expected",
                "using std::expected; #else poly",
                "CMake: target_compile_features",
                "Прапорці -std=c++20 /permissive-",
                "Кросплатформний білд"
            ],
            "desc": ["Автоматичний вибір", "сучасного коду або", "перевіреного поліфілу"]
        }
    ]

    for i, st in enumerate(stages):
        cx = start_x + i * (col_w + gap) + col_w / 2
        px = start_x + i * (col_w + gap)

        out.append(rect(px, y_top, col_w, h_col, fill=st["fill"], stroke=st["stroke"], sw=2, rx=8))

        out.append(text(cx, y_top + 24, st["num"], size=12, color=st["stroke"], bold=True))
        out.append(text(cx, y_top + 46, st["title"], size=13, bold=True))
        out.append(text(cx, y_top + 68, st["subtitle"], size=11, color=MUTED))

        out.append(line(px + 12, y_top + 82, px + col_w - 12, y_top + 82, color=st["stroke"], sw=1))

        item_y = y_top + 98
        for item in st["items"]:
            out.append(fitbox(px + 10, item_y, col_w - 20, 32, item, size=11, pad=4, fill="#ffffff", stroke="#cbd5e1", sw=1))
            item_y += 42

        out.append(line(px + 12, y_top + 326, px + col_w - 12, y_top + 326, color="#cbd5e1", sw=1))
        out.append(mtext(cx, y_top + 352, st["desc"], size=11, color=INK, lh=1.35, bold=False))

        if i < len(stages) - 1:
            arr_x1 = px + col_w + 3
            arr_x2 = arr_x1 + gap - 6
            arr_y = y_top + 180
            out.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))

    render(os.path.join(IMG, 'compiler-matrix-pipeline.svg'), W, H, *out,
           title="Конвеєр реалізації та виявлення можливостей стандарту C++")


def fig_conformance_modes():
    """Порівняння суворого стандарту та розширеного режиму (GNU / MSVC legacy)."""
    W, H = 1000, 520
    out = []

    out.append(text(W / 2, 45, "Порівняння діалектів: суворий ISO C++ проти розширень компіляторів", size=13, color=MUTED))

    panel_w = 445
    gap = 30
    start_x = 40
    y_top = 70
    h_panel = 425

    panels = [
        {
            "title": "Суворий режим відповідності ISO C++",
            "subtitle": "GCC/Clang: -std=c++20 -pedantic-errors  |  MSVC: /std:c++20 /permissive-",
            "fill": "#f0fdf4",
            "stroke": "#16a34a",
            "header_color": "#15803d",
            "blocks": [
                ("Двофазний пошук імен у шаблонах", "Помилки у залежних іменах виявляються на першій фазі"),
                ("Заборона нестандартних VLA", "Масиви змінної довжини відхиляються; std::vector/span"),
                ("Стандартний препроцесор ISO", "Коректний розбір __VA_OPT__ та макросів (/Zc:preprocessor)"),
                ("Точне значення макроса __cplusplus", "Повертає реальну дату стандарту 202002L (/Zc:__cplusplus)"),
                ("Гарантована кросплатформність", "Код надійно збирається всіма основними компіляторами")
            ]
        },
        {
            "title": "Розширений та поблажливий режим (Extensions)",
            "subtitle": "GCC/Clang: -std=gnu++20 (типовий)  |  MSVC: /permissive (застарілий)",
            "fill": "#fef2f2",
            "stroke": "#dc2626",
            "header_color": "#b91c1c",
            "blocks": [
                ("Однофазний пошук імен (MSVC legacy)", "Шаблони перевіряються лише при інстанціації, маскуючи баги"),
                ("Розширення GNU C у коді C++", "VLA, вирази-блоки ({ ... }), typeof без попереджень"),
                ("Традиційний препроцесор MSVC", "Помилкове склеювання токенів, що ламає макробібліотеки"),
                ("Застаріле значення __cplusplus", "MSVC за замовчуванням видає 199711L задля сумісності"),
                ("Прив'язка до одного компілятора", "Код не переноситься на інші платформи без правок")
            ]
        }
    ]

    for i, p in enumerate(panels):
        px = start_x + i * (panel_w + gap)
        cx = px + panel_w / 2

        out.append(rect(px, y_top, panel_w, h_panel, fill=p["fill"], stroke=p["stroke"], sw=2, rx=8))

        out.append(text(cx, y_top + 26, p["title"], size=13, color=p["header_color"], bold=True))
        out.append(text(cx, y_top + 48, p["subtitle"], size=10, color=MUTED))
        out.append(line(px + 15, y_top + 62, px + panel_w - 15, y_top + 62, color=p["stroke"], sw=1))

        item_y = y_top + 78
        for head, desc in p["blocks"]:
            text_lines = [head, desc]
            out.append(fitbox(px + 14, item_y, panel_w - 28, 56, text_lines, size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1))
            item_y += 66

    render(os.path.join(IMG, 'conformance-modes.svg'), W, H, *out,
           title="Порівняння суворого режиму відповідності ISO та розширень")


if __name__ == '__main__':
    fig_compiler_matrix_pipeline()
    fig_conformance_modes()
    print("OK: generated compiler-support figures")
