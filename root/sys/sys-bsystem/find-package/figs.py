# -*- coding: utf-8 -*-
"""Фігури до теми «find_package: Config проти Module й імпортовані цілі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
ACCENT_FILL = "#eef4fd"


# ── 1. Дерево рішень find_package: Module vs Config ─────────────────────────
def fig_mode_decision_flow():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 36, "Як find_package обирає режим пошуку", size=16, bold=True))

    # Корінь: виклик команди
    body, _, _ = textbox(520, 80, ["find_package(Foo 2.0 REQUIRED)", "Чи вказано явний прапорець режиму?"], size=13.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Три гілки від виклику
    frags.append(arrow(340, 106, 200, 150))
    frags.append(text(240, 126, "MODULE", size=12, color=MUTED, bold=True))

    frags.append(arrow(520, 106, 520, 150))
    frags.append(text(535, 130, "за замовчуванням", size=12, color=MUTED))

    frags.append(arrow(700, 106, 840, 150))
    frags.append(text(800, 126, "CONFIG / NO_MODULE", size=12, color=MUTED, bold=True))

    # Ліва гілка: лише Module mode
    body, _, _ = textbox(200, 190, ["Режим модуля (Module Mode)", "Шукає FindFoo.cmake у:", "1. CMAKE_MODULE_PATH", "2. Каталозі модулів самого CMake"], size=12.5)
    frags.append(body)

    # Центральна гілка: спроба модуля з переходом у конфіг
    body, _, _ = textbox(520, 190, ["Спроба Module Mode", "Шукає FindFoo.cmake", "у тих самих шляхах"], size=12.5)
    frags.append(body)

    # Права гілка: лише Config mode
    body, _, _ = textbox(840, 190, ["Режим конфігурації (Config Mode)", "Шукає FooConfig.cmake або", "foo-config.cmake у префіксах"], size=12.5)
    frags.append(body)

    # Розгалуження від центральної гілки
    frags.append(arrow(430, 226, 280, 280))
    frags.append(text(330, 250, "знайдено", size=12, color=FIELD, bold=True))

    frags.append(arrow(610, 226, 760, 280))
    frags.append(text(715, 250, "не знайдено", size=12, color=POS, bold=True))

    # Результати виконання
    body, _, _ = textbox(200, 330, [
        "Виконання FindFoo.cmake",
        "• Сторонній сценарій-детектив",
        "• Шукає find_path() / find_library()",
        "• Створює Foo::Foo або змінні",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    body, _, _ = textbox(840, 330, [
        "Виконання FooConfig.cmake",
        "• Файл від автора бібліотеки",
        "• Перевіряє версію (ConfigVersion)",
        "• Імпортує цілі (FooTargets.cmake)",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Підсумок у разі невдачі
    frags.append(arrow(200, 390, 360, 450))
    frags.append(arrow(840, 390, 680, 450))
    frags.append(text(250, 424, "не знайдено", size=12, color=POS))
    frags.append(text(790, 424, "не знайдено", size=12, color=POS))

    body, _, _ = textbox(520, 470, [
        "Результат пошуку залежності",
        "REQUIRED: фатальна помилка конфігурації | без REQUIRED: Foo_FOUND = FALSE",
    ], size=13, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    render(os.path.join(IMG, "mode-decision-flow.svg"), W, H, *frags,
           title="Дерево рішень find_package: вибір між Module Mode та Config Mode")


# ── 2. Драбина пріоритетів пошуку шляхів ────────────────────────────────────
def fig_search_paths_order():
    W, H = 1040, 620
    frags = []

    frags.append(text(520, 34, "Пріоритет пошуку шляхів у Config Mode та командах find_*", size=16, bold=True))
    frags.append(text(520, 56, "CMake перевіряє каталоги згори вниз до першого збігу:", size=13, color=MUTED))

    steps = [
        ("1. Точковий корінь пакета", "<PackageName>_ROOT (змінна CMake або оточення), <PackageName>_DIR", FIELD, OK_FILL),
        ("2. Шляхи проєкту та розробника", "CMAKE_PREFIX_PATH, CMAKE_FRAMEWORK_PATH, CMAKE_APPBUNDLE_PATH", NEG, ACCENT_FILL),
        ("3. Тулчейн та менеджер пакетів", "CMAKE_PREFIX_PATH від vcpkg / Conan, CMAKE_FIND_ROOT_PATH (крос-компіляція)", INK, FILL),
        ("4. Підказки з виклику команди", "HINTS із find_package(...) / find_path(...) / find_library(...)", INK, FILL),
        ("5. Системні каталоги оточення", "PATH (змінна оточення), стандартні префікси /usr/local, /usr, /opt", MUTED, BG),
        ("6. Системні реєстри та жорсткі шляхи", "Реєстр Windows (HKLM/HKCU), PATHS із виклику команди", MUTED, BG),
    ]

    y = 86
    for rank_title, details, st, fl in steps:
        frags.append(fitbox(80, y, 880, 54, rank_title + "\n" + details, size=12.5, stroke=st, fill=fl))
        if y < 430:
            frags.append(arrow(520, y + 54, 520, y + 70))
        y += 70

    frags.append(fitbox(80, 526, 880, 64,
                        "Ключ NO_DEFAULT_PATH вимикає кроки 2, 5 і 6, залишаючи лише явні HINTS та PATHS;\n"
                        "прапорець --debug-find у командному рядку виводить кожен перевірений каталог.", size=13))

    render(os.path.join(IMG, "search-paths-order.svg"), W, H, *frags,
           title="Ієрархія та порядок перевірки шляхів пошуку CMake")


# ── 3. Анатомія сучасного пакета в Config Mode ──────────────────────────────
def fig_config_package_layout():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 34, "Будова встановленого пакета та розгортання графа цілей", size=16, bold=True))

    # Ліва колонка: файли на диску
    frags.append(text(270, 72, "Файли у lib/cmake/Foo/ на диску", size=14.5, bold=True))

    files = [
        ("FooConfigVersion.cmake", "перевіряє сумісність запитаної версії з наявною"),
        ("FooConfig.cmake", "головна точка входу: шукає залежності через find_dependency"),
        ("FooTargets.cmake", "створює цілі: add_library(Foo::Core IMPORTED)"),
        ("FooTargets-release.cmake", "прописує IMPORTED_LOCATION_RELEASE = lib/libfoo.so"),
    ]
    y = 96
    for fname, desc in files:
        frags.append(fitbox(60, y, 420, 58, fname + "\n" + desc, size=12.5, stroke=NEG, fill=ACCENT_FILL))
        y += 68

    # Стрілка між диском і пам'яттю
    frags.append(arrow(490, 230, 550, 230, sw=2.5))
    frags.append(text(520, 218, "завантаження", size=12, color=MUTED))

    # Права колонка: відновлений граф імпортованих цілей у пам'яті CMake
    frags.append(text(780, 72, "Модель імпортованих цілей у пам'яті", size=14.5, bold=True))

    body, _, _ = textbox(780, 160, [
        "Ціль  Foo::Core  (IMPORTED)",
        "INTERFACE_INCLUDE_DIRECTORIES = <prefix>/include",
        "IMPORTED_LOCATION = <prefix>/lib/libfoo_core.so",
        "INTERFACE_COMPILE_DEFINITIONS = FOO_FAST_IO=1",
        "INTERFACE_LINK_LIBRARIES = OpenSSL::Crypto",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(780, 236, 780, 280))
    frags.append(text(805, 258, "тягне транзитивно", size=12, color=MUTED, anchor="start"))

    body, _, _ = textbox(780, 330, [
        "Ціль  OpenSSL::Crypto  (IMPORTED)",
        "INTERFACE_INCLUDE_DIRECTORIES = /usr/include",
        "IMPORTED_LOCATION = /usr/lib/libcrypto.so",
    ], size=12.5, fill=FILL, stroke=LINE)
    frags.append(body)

    frags.append(fitbox(60, 420, 920, 56,
                        "Споживач пише лише target_link_libraries(app PRIVATE Foo::Core) — усі шляхи заголовків,\n"
                        "прапорці компіляції та транзитивні бібліотеки (OpenSSL) підтягуються автоматично.", size=13))

    render(os.path.join(IMG, "config-package-layout.svg"), W, H, *frags,
           title="Анатомія пакета Config Mode та імпортовані цілі")


fig_mode_decision_flow()
fig_search_paths_order()
fig_config_package_layout()
print("ok")
