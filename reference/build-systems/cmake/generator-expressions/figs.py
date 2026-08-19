# -*- coding: utf-8 -*-
"""Фігури до теми «Генераторні вирази: рішення, відкладене до генерації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
INFO_FILL = "#eaf0fd"


# ── 1. Дві фази CMake: де живуть і обчислюються генераторні вирази ───────────
def fig_two_phases():
    W, H = 1060, 560
    frags = []

    # Фаза 1
    frags.append(rect(40, 50, 460, 420, fill=FILL, stroke=LINE, rx=8))
    frags.append(text(270, 82, "1. Фаза конфігурації (Configure)", size=16, bold=True))
    frags.append(text(270, 106, "Читання CMakeLists.txt згори вниз", size=13, color=MUTED))

    p1_items = [
        "Виконуються звичайні команди й змінні: set(), if(), message()",
        "Створюються цілі: add_library(), add_executable()",
        "Властивості цілей записують сирі рядки з виразами",
        "Multi-config генератори НЕ знають поточної конфігурації (Debug/Release)",
        "Точні файлові шляхи майбутніх бінарників ще не обчислені",
    ]
    y = 135
    for item in p1_items:
        frags.append(fitbox(60, y, 420, 52, item, size=12.5, stroke=MUTED, fill=BG))
        y += 62

    # Стрілка між фазами
    frags.append(arrow(510, 260, 550, 260, color=LINE, sw=2.5))
    frags.append(text(530, 245, "модель", size=12, color=MUTED))

    # Фаза 2
    frags.append(rect(560, 50, 460, 420, fill=INFO_FILL, stroke=NEG, rx=8))
    frags.append(text(790, 82, "2. Фаза генерації (Generate)", size=16, bold=True, color=NEG))
    frags.append(text(790, 106, "Побудова файлів збірки для Ninja, MSVC, Make", size=13, color=MUTED))

    p2_items = [
        "Рушій обчислює генераторні вирази $<...> для кожної цілі",
        "Відома активна конфігурація: $<CONFIG:Debug> стає 1 або 0",
        "Відомий цільовий компілятор: $<CXX_COMPILER_ID:...> розгортається",
        "Обчислені абсолютні шляхи до файлів: $<TARGET_FILE:tgt>",
        "Запис build.ninja / .vcxproj з фінальними прапорцями",
    ]
    y = 135
    for item in p2_items:
        frags.append(fitbox(580, y, 420, 52, item, size=12.5, stroke=NEG, fill=BG))
        y += 62

    # Нижній підсумок
    frags.append(fitbox(40, 485, 980, 58,
                        "Звичайний if() бачить лише стан під час конфігурації;\n"
                        "генераторний вираз $<...> чекає другої фази й обчислюється для кожного споживача окремо",
                        size=13.5, stroke=FIELD, fill=OK_FILL))

    render(os.path.join(IMG, "two-phases-and-genex.svg"), W, H, *frags,
           title="Дві фази CMake: де обчислюються генераторні вирази")


# ── 2. Дерево рекурсивного обчислення генераторного виразу ────────────────────
def fig_evaluation_tree():
    W, H = 1060, 580
    frags = []

    frags.append(text(530, 55, "Вихідний вираз: $<IF:$<CONFIG:Debug>,-DDEBUG_LOGS,$<IF:$<CONFIG:Release>,-DRELEASE_OPT,-DDEFAULT>>",
                      size=13.5, bold=True, color=INK))

    # Рівень 1: Корінь $<IF:...>
    frags.append(fitbox(380, 80, 300, 56, "Корінь: $<IF: cond1 , val_true , val_false >\n(чекає обчислення гілок)",
                        size=13, stroke=LINE, fill=FILL, bold=True))

    # Стрілки від кореня
    frags.append(arrow(430, 136, 230, 195))
    frags.append(arrow(530, 136, 530, 195))
    frags.append(arrow(630, 136, 830, 195))

    frags.append(text(310, 160, "умова 1", size=12, color=MUTED))
    frags.append(text(500, 165, "якщо 1", size=12, color=MUTED))
    frags.append(text(750, 160, "якщо 0", size=12, color=MUTED))

    # Рівень 2: Вузли
    # Вузол 1: Умова $<CONFIG:Debug>
    frags.append(fitbox(90, 195, 280, 75, "Вузол 1: $<CONFIG:Debug>\nДля збірки Release обчислюється в: 0",
                        size=12.5, stroke=NEG, fill=INFO_FILL))

    # Вузол 2: Значення для True
    frags.append(fitbox(410, 195, 240, 75, "Гілка True:\n-DDEBUG_LOGS\n(пропускається, бо умова 0)",
                        size=12.5, stroke=MUTED, fill=BG))

    # Вузол 3: Вкладений $<IF:...>
    frags.append(fitbox(690, 195, 300, 75, "Вузол 2: $<IF: cond2 , opt , def >\n(обчислюється, бо умова 1 була 0)",
                        size=12.5, stroke=LINE, fill=FILL, bold=True))

    # Стрілки від вкладеного виразу
    frags.append(arrow(740, 270, 640, 335))
    frags.append(arrow(840, 270, 790, 335))
    frags.append(arrow(940, 270, 940, 335))

    frags.append(text(670, 300, "умова 2", size=12, color=MUTED))
    frags.append(text(800, 305, "якщо 1", size=12, color=MUTED))
    frags.append(text(920, 305, "якщо 0", size=12, color=MUTED))

    # Рівень 3: Листки
    frags.append(fitbox(530, 335, 210, 65, "$<CONFIG:Release>\nОбчислюється в: 1",
                        size=12.5, stroke=FIELD, fill=OK_FILL))
    frags.append(fitbox(755, 335, 140, 65, "-DRELEASE_OPT\n(обрано)",
                        size=12.5, stroke=FIELD, fill=OK_FILL, bold=True))
    frags.append(fitbox(910, 335, 120, 65, "-DDEFAULT\n(пропущено)",
                        size=12.5, stroke=MUTED, fill=BG))

    # Згортання в результат
    frags.append(arrow(790, 400, 530, 460, color=FIELD, sw=2.2))
    frags.append(fitbox(280, 450, 500, 50, "Результат обчислення для Release:   -DRELEASE_OPT",
                        size=14, stroke=FIELD, fill=OK_FILL, bold=True))

    frags.append(fitbox(40, 515, 980, 50,
                        "Рушій генерації обчислює листки дерева знизу вгору, згортаючи вирази у фінальний рядок",
                        size=13, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, "genex-evaluation-tree.svg"), W, H, *frags,
           title="Рекурсивне обчислення вкладених генераторних виразів")


# ── 3. Розділення простору джерел та інсталяції ──────────────────────────────
def fig_build_vs_install():
    W, H = 1060, 540
    frags = []

    frags.append(fitbox(60, 45, 940, 52,
                        "target_include_directories(core PUBLIC\n"
                        "    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>\n"
                        "    $<INSTALL_INTERFACE:include>)",
                        size=13, stroke=LINE, fill=FILL, bold=True))

    # Ліва колонка: Локальна збірка
    frags.append(rect(60, 115, 450, 345, fill=OK_FILL, stroke=FIELD, rx=8))
    frags.append(text(285, 145, "Локальна збірка проєкту", size=15, bold=True, color=FIELD))
    frags.append(text(285, 168, "Ціль core збирається або лінкується сусідом", size=12.5, color=MUTED))

    frags.append(fitbox(80, 190, 410, 68,
                        "$<BUILD_INTERFACE:...>  →  розгортається в:\n"
                        "/home/user/project/src/core/include",
                        size=12.5, stroke=FIELD, fill=BG, bold=True))

    frags.append(fitbox(80, 275, 410, 60,
                        "$<INSTALL_INTERFACE:...>  →  розгортається в:\n"
                        "\"\" (порожній рядок, ігнорується)",
                        size=12.5, stroke=MUTED, fill=BG))

    frags.append(fitbox(80, 350, 410, 92,
                        "Результат компілятора:\n"
                        "-I/home/user/project/src/core/include\n"
                        "Локальні сирці бачать власні заголовки",
                        size=12.5, stroke=FIELD, fill=BG))

    # Права колонка: Інсталяція / Експорт
    frags.append(rect(550, 115, 450, 345, fill=INFO_FILL, stroke=NEG, rx=8))
    frags.append(text(775, 145, "Встановлений пакет (install / export)", size=15, bold=True, color=NEG))
    frags.append(text(775, 168, "Сторонній проєкт робить find_package(core)", size=12.5, color=MUTED))

    frags.append(fitbox(570, 190, 410, 68,
                        "$<BUILD_INTERFACE:...>  →  розгортається в:\n"
                        "\"\" (порожній рядок, видаляється)",
                        size=12.5, stroke=MUTED, fill=BG))

    frags.append(fitbox(570, 275, 410, 60,
                        "$<INSTALL_INTERFACE:...>  →  розгортається в:\n"
                        "${_IMPORT_PREFIX}/include",
                        size=12.5, stroke=NEG, fill=BG, bold=True))

    frags.append(fitbox(570, 350, 410, 92,
                        "Результат в coreTargets.cmake:\n"
                        "-I/usr/local/include (або C:/Program Files/include)\n"
                        "Немає витоку шляхів розробницької машини",
                        size=12.5, stroke=NEG, fill=BG))

    frags.append(fitbox(60, 475, 940, 50,
                        "Дуальність інтерфейсів ізолює файлову систему розробника від файлової системи кінцевого користувача",
                        size=13.5, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, "build-vs-install-interface.svg"), W, H, *frags,
           title="Розділення шляхів заголовків: BUILD_INTERFACE проти INSTALL_INTERFACE")


# ── 4. Кодогенерація: цільовий бінарник у кастомній команді ─────────────────
def fig_custom_command_target():
    W, H = 1060, 520
    frags = []

    # Крок 1: Ціль-генератор
    frags.append(rect(50, 60, 270, 250, fill=INFO_FILL, stroke=NEG, rx=8))
    frags.append(text(185, 90, "1. Ціль-інструмент", size=15, bold=True, color=NEG))
    frags.append(fitbox(70, 110, 230, 60, "add_executable(schema_gen\n  generator.cpp)", size=13, stroke=NEG, fill=BG))
    frags.append(fitbox(70, 185, 230, 110,
                        "Артефакт збірки:\n"
                        "• Linux: build/schema_gen\n"
                        "• Windows: build/Debug/\n"
                        "  schema_gen.exe", size=12, stroke=MUTED, fill=BG))

    # Стрілка 1 -> 2
    frags.append(arrow(320, 185, 380, 185, color=LINE, sw=2))
    frags.append(text(350, 170, "$<TARGET_FILE>", size=12, bold=True, color=FIELD))

    # Крок 2: add_custom_command
    frags.append(rect(390, 60, 360, 250, fill=OK_FILL, stroke=FIELD, rx=8))
    frags.append(text(570, 90, "2. Кастомна команда", size=15, bold=True, color=FIELD))
    frags.append(fitbox(410, 110, 320, 80,
                        "add_custom_command(\n"
                        "  OUTPUT schema.cpp schema.h\n"
                        "  COMMAND $<TARGET_FILE:schema_gen>\n"
                        "    --in ${IN} --out ${OUT})", size=12, stroke=FIELD, fill=BG, bold=True))
    frags.append(fitbox(410, 200, 320, 95,
                        "Подвійна дія CMake:\n"
                        "1) Підставляє точний шлях до .exe\n"
                        "2) Автоматично додає schema_gen\n"
                        "   як залежність у графі робіт", size=12, stroke=FIELD, fill=BG))

    # Стрілка 2 -> 3
    frags.append(arrow(750, 185, 810, 185, color=LINE, sw=2))
    frags.append(text(780, 170, "OUTPUT", size=12, color=MUTED))

    # Крок 3: Ціль-споживач
    frags.append(rect(820, 60, 190, 250, fill=FILL, stroke=LINE, rx=8))
    frags.append(text(915, 90, "3. Програма", size=15, bold=True))
    frags.append(fitbox(835, 110, 160, 80, "add_executable(app\n  main.cpp\n  schema.cpp)", size=12.5, stroke=LINE, fill=BG))
    frags.append(fitbox(835, 205, 160, 90, "Чекає завершення\nгенерації\nschema.cpp", size=12, stroke=MUTED, fill=BG))

    # Нижній блок
    frags.append(fitbox(50, 335, 960, 70,
                        "Чому не можна писати COMMAND ./schema_gen:\n"
                        "• На Windows потрібне розширення .exe, а в багатоконфігураційних генераторах шлях веде в Debug/ чи Release/;\n"
                        "• $<TARGET_FILE:schema_gen> розв'язує обидві проблеми й гарантує правильний порядок збірки в DAG.",
                        size=13, stroke=POS, fill=WARN_FILL))

    frags.append(fitbox(50, 420, 960, 85,
                        "Граф залежностей: schema_gen (компіляція/лінкування)  →  виконання генератора  →  app (збірка зі згенерованим файлом)",
                        size=13.5, stroke=LINE, fill=FILL, bold=True))

    render(os.path.join(IMG, "custom-command-target-file.svg"), W, H, *frags,
           title="Використання цільового артефакту в кастомній команді")


if __name__ == "__main__":
    fig_two_phases()
    fig_evaluation_tree()
    fig_build_vs_install()
    fig_custom_command_target()
    print("All figures generated successfully.")
