# -*- coding: utf-8 -*-
"""Фігури до теми «configure_file: значення конфігурації у згенерованих файлах»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
INFO_FILL = "#eaf2fb"


# ── 1. Потік трансформації: вихідне дерево, configure_file та білд ───────────
def fig_configure_file_flow():
    W, H = 1040, 560
    frags = []

    frags.append(text(240, 48, "Дерево джерел (лише читання)", size=15, bold=True))
    frags.append(text(800, 48, "Каталог збірки (згенеровані файли)", size=15, bold=True))

    # Джерело: config.h.in + CMakeLists.txt
    body_src, _, _ = textbox(240, 130, [
        "CMAKE_CURRENT_SOURCE_DIR",
        "  config.h.in (шаблон з @VAR@)",
        "  CMakeLists.txt (змінні збірки)",
    ], size=13.5, fill=FILL, stroke=LINE, min_w=380)
    frags.append(body_src)

    # Процес: configure_file()
    body_proc, _, _ = textbox(520, 250, [
        "configure_file(config.h.in include/app/config.h @ONLY)",
        "Виконується на фазі конфігурації (Configure Time)",
        "Підстановка значень: @APP_VERSION@ -> \"2.4.1\"",
    ], size=13.5, fill=INFO_FILL, stroke=NEG, min_w=460)
    frags.append(body_proc)

    # Стрілки від джерела до процесу
    frags.append(arrow(240, 180, 420, 220))
    frags.append(text(290, 215, "вхідний шаблон", size=12, color=MUTED, anchor="start"))

    # Результат: CMAKE_CURRENT_BINARY_DIR/include/app/config.h
    body_bin, _, _ = textbox(800, 130, [
        "CMAKE_CURRENT_BINARY_DIR",
        "  include/app/config.h",
        "  (готовий заголовок C/C++)",
    ], size=13.5, fill=OK_FILL, stroke=FIELD, min_w=360)
    frags.append(body_bin)

    frags.append(arrow(620, 220, 780, 180))
    frags.append(text(710, 215, "запис результату", size=12, color=MUTED, anchor="start"))

    # Компілятор і ціль
    body_target, _, _ = textbox(520, 390, [
        "target_include_directories(app PUBLIC",
        "    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>",
        ")",
        "Компілятор бачить #include <app/config.h>",
    ], size=13.5, fill=FILL, stroke=LINE, min_w=460)
    frags.append(body_target)

    frags.append(arrow(800, 180, 680, 350))
    frags.append(arrow(520, 305, 520, 345))

    frags.append(fitbox(60, 470, 920, 62,
                        "Дерево джерел лишається недоторканним (чистий репозиторій);\n"
                        "згенеровані заголовки потрапляють у каталог збірки та ізолюються за префіксом простору імен", size=13.5))

    render(os.path.join(IMG, "configure-file-flow.svg"), W, H, *frags,
           title="Потік трансформації шаблону configure_file у заголовок збірки")


# ── 2. Стани #cmakedefine та #cmakedefine01 ──────────────────────────────────
def fig_cmakedefine_states():
    W, H = 1060, 560
    frags = []

    frags.append(text(530, 46, "Перетворення директив у вихідний код C/C++", size=15, bold=True))

    # Стовпчик 1: Змінна CMake
    frags.append(text(150, 90, "Значення у CMake", size=13.5, bold=True, color=MUTED))
    # Стовпчик 2: Шаблон (.h.in)
    frags.append(text(460, 90, "Рядок у шаблоні (.in)", size=13.5, bold=True, color=MUTED))
    # Стовпчик 3: Згенерований код (.h)
    frags.append(text(830, 90, "Згенерований результат (.h)", size=13.5, bold=True, color=MUTED))

    rows = [
        ("ENABLE_FEATURE = ON", "#cmakedefine ENABLE_FEATURE", "#define ENABLE_FEATURE", OK_FILL, FIELD),
        ("ENABLE_FEATURE = OFF", "#cmakedefine ENABLE_FEATURE", "/* #undef ENABLE_FEATURE */", WARN_FILL, POS),
        ("ENABLE_FEATURE = ON", "#cmakedefine01 ENABLE_FEATURE", "#define ENABLE_FEATURE 1", OK_FILL, FIELD),
        ("ENABLE_FEATURE = OFF", "#cmakedefine01 ENABLE_FEATURE", "#define ENABLE_FEATURE 0", INFO_FILL, NEG),
        ("BUFFER_SIZE = 4096", "#cmakedefine BUFFER_SIZE @BUFFER_SIZE@", "#define BUFFER_SIZE 4096", OK_FILL, FIELD),
    ]

    y = 125
    for var_val, in_line, out_line, bg_col, stroke_col in rows:
        frags.append(fitbox(50, y, 200, 48, var_val, size=13, fill=FILL, stroke=LINE))
        frags.append(fitbox(280, y, 360, 48, in_line, size=13, fill=FILL, stroke=LINE))
        frags.append(arrow(650, y + 24, 690, y + 24))
        frags.append(fitbox(700, y, 310, 48, out_line, size=13, fill=bg_col, stroke=stroke_col))
        y += 66

    frags.append(fitbox(50, 470, 960, 62,
                        "#cmakedefine при вимкненні створює /* #undef */ для перевірок через #ifdef;\n"
                        "#cmakedefine01 завжди створює 0 або 1 для безпечних числових перевірок #if та C++ if constexpr", size=13.5))

    render(os.path.join(IMG, "cmakedefine-states.svg"), W, H, *frags,
           title="Правила генерації #cmakedefine та #cmakedefine01")


# ── 3. Збереження mtime та відсікання зайвої перекомпіляції ───────────────────
def fig_mtime_cutoff():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 46, "Захист інкрементальної збірки: збереження мітки часу (Early Cutoff)", size=15, bold=True))

    body_reconf, _, _ = textbox(520, 115, [
        "Повторна конфігурація CMake (зміна CMakeLists.txt або cmake --build .)",
        "configure_file() генерує новий вміст у внутрішньому буфері",
    ], size=13.5, fill=FILL, stroke=LINE, min_w=700)
    frags.append(body_reconf)

    # Розгалуження
    frags.append(arrow(360, 160, 260, 215))
    frags.append(arrow(680, 160, 780, 215))

    # Гілка 1: Вміст не змінився
    body_same, _, _ = textbox(260, 275, [
        "Вміст буфера == config.h на диску",
        "Файл НЕ перезаписується",
        "Мітка часу (mtime) НЕ змінюється",
    ], size=13, fill=OK_FILL, stroke=FIELD, min_w=380)
    frags.append(body_same)

    # Гілка 2: Вміст змінився
    body_diff, _, _ = textbox(780, 275, [
        "Вміст буфера != config.h на диску",
        "Файл перезаписується на диску",
        "Мітка часу (mtime) оновлюється",
    ], size=13, fill=WARN_FILL, stroke=POS, min_w=380)
    frags.append(body_diff)

    # Наслідки для білд-системи
    frags.append(arrow(260, 335, 260, 385))
    frags.append(arrow(780, 335, 780, 385))

    body_res_skip, _, _ = textbox(260, 420, [
        "Ninja/Make: mtime(config.h) < mtime(main.o)",
        "Компіляція ПРОПУСКАЄТЬСЯ (0.01с)",
    ], size=13, fill=OK_FILL, stroke=FIELD, min_w=380)
    frags.append(body_res_skip)

    body_res_rebuild, _, _ = textbox(780, 420, [
        "Ninja/Make: mtime(config.h) > mtime(main.o)",
        "Перекомпілюються лише залежні .cpp",
    ], size=13, fill=WARN_FILL, stroke=POS, min_w=380)
    frags.append(body_res_rebuild)

    frags.append(fitbox(60, 480, 920, 56,
                        "Побайтове порівняння перед записом запобігає лавинній перекомпіляції всього проєкту\n"
                        "при кожній модифікації CMakeLists.txt або повторному прогоні генератора", size=13.5))

    render(os.path.join(IMG, "mtime-cutoff.svg"), W, H, *frags,
           title="Збереження mtime при незмінному вмісті у configure_file")


if __name__ == "__main__":
    fig_configure_file_flow()
    fig_cmakedefine_states()
    fig_mtime_cutoff()
    print("All figures generated successfully.")
