# -*- coding: utf-8 -*-
"""Фігури до теми «FetchContent і підпроєкти: чужий код усередині збірки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
BLUE_FILL = "#eaf0fd"


# ── 1. ExternalProject проти FetchContent ──────────────────────────────────
def fig_externalproject_vs_fetchcontent():
    W, H = 1100, 560
    frags = []

    frags.append(text(280, 56, "ExternalProject_Add: завантаження й збірка під час build time", size=14.5, bold=True))
    frags.append(text(820, 56, "FetchContent: завантаження й інтеграція під час configure time", size=14.5, bold=True))

    # Ліва колонка (ExternalProject)
    frags.append(fitbox(50, 84, 460, 160,
                        "1. Фаза конфігурації (cmake -B build):\n"
                        "• Інтерпретатор бачить лише add_custom_target\n"
                        "• Ціль dep_lib НЕ існує в моделі проєкту\n"
                        "• Не можна викликати target_link_libraries(app dep_lib)\n"
                        "• Потрібні фіктивні IMPORTED цілі та ручні шляхи",
                        size=13, fill=WARN_FILL, stroke=POS))

    frags.append(arrow(280, 252, 280, 286))

    frags.append(fitbox(50, 294, 460, 150,
                        "2. Фаза збірки (cmake --build build):\n"
                        "• Ninja/Make запускає дочірній процес CMake\n"
                        "• Дочірній процес качає, конфігурує і збирає .a/.so\n"
                        "• Головний проєкт чекає завершення чужої збірки\n"
                        "• Лінкування через ручний шлях до скомпільованого файлу",
                        size=13))

    # Права колонка (FetchContent)
    frags.append(fitbox(590, 84, 460, 160,
                        "1. Фаза конфігурації (cmake -B build):\n"
                        "• FetchContent скачує або розпаковує джерела\n"
                        "• Викликається add_subdirectory() для чужого коду\n"
                        "• Ціль dep_lib потрапляє в спільну модель проєкту\n"
                        "• Працює пряме target_link_libraries(app dep_lib)",
                        size=13, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(820, 252, 820, 286))

    frags.append(fitbox(590, 294, 460, 150,
                        "2. Фаза збірки (cmake --build build):\n"
                        "• Єдиний спільний граф залежностей Ninja/Make\n"
                        "• Компіляція чужих і власних файлів паралельно\n"
                        "• Інкрементальна збірка бачить точні залежності\n"
                        "• Повне узгодження прапорців компілятора й тулчейна",
                        size=13))

    frags.append(fitbox(50, 470, 1000, 62,
                        "ExternalProject ізолює збірку в окремий процес ціною розриву графу цілей;\n"
                        "FetchContent переносить отримання джерел на фазу конфігурації й об'єднує граф цілей.", size=13.5))

    render(os.path.join(IMG, "externalproject-vs-fetchcontent.svg"), W, H, *frags,
           title="Порівняння ExternalProject та FetchContent")


# ── 2. Життєвий цикл FetchContent ──────────────────────────────────────────
def fig_fetchcontent_lifecycle():
    W, H = 1120, 540
    frags = []

    frags.append(text(560, 54, "Послідовність обробки залежності у FetchContent", size=16, bold=True))

    steps = [
        ("1. Декларація", "FetchContent_Declare(fmt ...)",
         "Реєструє джерело (Git/URL/шлях)\nу внутрішньому реєстрі.\nНіяких завантажень чи мережі.", OK_FILL, FIELD),
        ("2. Активація", "FetchContent_MakeAvailable(fmt)",
         "Перевіряє, чи не створено вже fmt.\nЯкщо ні — запускає підготовку\nджерел у каталозі _deps/.", BLUE_FILL, NEG),
        ("3. Subbuild", "cmake --build _deps/fmt-subbuild",
         "Генерує тимчасовий мініпроєкт,\nякий скачує й розпаковує джерела\nу _deps/fmt-src.", FILL, LINE),
        ("4. Вбудовування", "add_subdirectory(_deps/fmt-src)",
         "Виконує чужий CMakeLists.txt,\nдодає цілі (fmt::fmt) у спільну\nмодель поточного проєкту.", OK_FILL, FIELD),
    ]

    x = 40
    for i, (st_num, code_call, desc, fl, st_col) in enumerate(steps):
        frags.append(fitbox(x, 92, 230, 340,
                            st_num + "\n\n" + code_call + "\n\n" + desc,
                            size=12.5, fill=fl, stroke=st_col))
        if i < len(steps) - 1:
            frags.append(arrow(x + 236, 260, x + 264, 260))
        x += 270

    frags.append(fitbox(40, 456, 1040, 60,
                        "Декларація відокремлена від виконання: кореневий проєкт визначає параметри джерел,\n"
                        "а MakeAvailable матеріалізує їх і передає керування в add_subdirectory().", size=13.5))

    render(os.path.join(IMG, "fetchcontent-lifecycle.svg"), W, H, *frags,
           title="Чотири кроки життєвого циклу FetchContent")


# ── 3. Ізоляція цілей та опцій підпроєкту ──────────────────────────────────
def fig_target_graph_isolation():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 45, "Спільний граф цілей і три захисні бар'єри підпроєкту", size=16, bold=True))

    # Головний проєкт
    frags.append(fitbox(50, 75, 360, 250,
                        "Головний проєкт: my_service\n\n"
                        "add_executable(my_service main.cpp)\n"
                        "target_link_libraries(my_service\n"
                        "    PRIVATE fmt::fmt\n"
                        ")\n\n"
                        "Прапорці: -Wall -Wextra -Werror\n"
                        "Стандарт: C++20",
                        size=13, fill=OK_FILL, stroke=FIELD))

    # Стрілка зв'язку
    frags.append(arrow(420, 200, 490, 200))
    frags.append(text(455, 185, "лінкує", size=12, color=MUTED))

    # Чужий підпроєкт
    frags.append(fitbox(500, 75, 550, 250,
                        "Підпроєкт у _deps/fmt-src (чужий CMakeLists.txt)\n\n"
                        "• Бібліотечна ціль: add_library(fmt ...) + ALIAS fmt::fmt\n"
                        "• Зайві цілі: fmt_test, fmt_benchmark, fmt_docs\n"
                        "• Опції: option(FMT_TEST \"Build tests\" ON)\n"
                        "• Заголовки з незвичним для проєкту стилем коду",
                        size=13, fill=FILL, stroke=LINE))

    # Три бар'єри
    barriers = [
        ("1. ALIAS fmt::fmt", "Захищає від колізій імен і перевіряє\nдрукарські помилки на етапі конфігурації", 50),
        ("2. EXCLUDE_FROM_ALL", "Виключає fmt_test і бенчмарки із цілі all\n(збирається лише потрібна бібліотека)", 400),
        ("3. SYSTEM include", "Позначає заголовки чужого коду як системні\nй придушує попередження компілятора", 750),
    ]

    for title_b, desc_b, bx in barriers:
        frags.append(fitbox(bx, 360, 300, 110, title_b + "\n\n" + desc_b, size=12, fill=BLUE_FILL, stroke=NEG))

    frags.append(fitbox(50, 490, 1000, 50,
                        "Підпроєкт ділить із додатком єдиний граф збірки, але захисні механізми ізолюють опції та прапорці.",
                        size=13))

    render(os.path.join(IMG, "target-graph-isolation.svg"), W, H, *frags,
           title="Ізоляція підпроєкту у спільному графі цілей")


# ── 4. Перенаправлення find_package та режим TRY_FIND_PACKAGE ──────────────
def fig_find_package_forwarding():
    W, H = 1060, 480
    frags = []

    frags.append(text(530, 50, "Уніфікація системних пакетів і FetchContent (CMake 3.24+)", size=15.5, bold=True))

    frags.append(fitbox(60, 86, 940, 70,
                        "FetchContent_Declare(fmt ... FIND_PACKAGE_ARGS 10.0 CONFIG)\n"
                        "FetchContent_MakeAvailable(fmt)", size=13.5, fill=FILL, stroke=LINE))

    frags.append(arrow(530, 162, 530, 204))
    frags.append(text(530, 186, "FETCHCONTENT_TRY_FIND_PACKAGE_MODE", size=12, color=MUTED))

    # Розгалуження
    frags.append(fitbox(60, 216, 440, 160,
                        "Гілка А: Пакет знайдено в системі\n(vcpkg, Conan або системний пакунок)\n\n"
                        "• Викликається find_package(fmt 10.0 CONFIG)\n"
                        "• Створюється імпортована ціль fmt::fmt\n"
                        "• Нуль завантажень з мережі, миттєва збірка",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(560, 216, 440, 160,
                        "Гілка Б: Пакет відсутній у системі\n(автономне завантаження з джерел)\n\n"
                        "• Скачується архів за URL_HASH або Git\n"
                        "• Викликається add_subdirectory()\n"
                        "• Створюється рідна ціль fmt::fmt",
                        size=12.5, fill=BLUE_FILL, stroke=NEG))

    frags.append(arrow(280, 382, 450, 420))
    frags.append(arrow(780, 382, 610, 420))

    frags.append(fitbox(280, 412, 500, 52,
                        "Код проєкту завжди лінкує fmt::fmt однаково:\n"
                        "target_link_libraries(my_app PRIVATE fmt::fmt)",
                        size=13, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "find-package-forwarding.svg"), W, H, *frags,
           title="Схема взаємодії FetchContent із find_package")


fig_externalproject_vs_fetchcontent()
fig_fetchcontent_lifecycle()
fig_target_graph_isolation()
fig_find_package_forwarding()
print("all figures generated successfully")
