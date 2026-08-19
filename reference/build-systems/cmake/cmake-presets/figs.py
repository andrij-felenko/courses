# -*- coding: utf-8 -*-
"""Фігури до теми «CMakePresets: конфігурації як декларація»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL   = "#eaf5ec"
USER_FILL = "#eaf0fd"


# ── 1. Роздробленість і розходження проти єдиного пресета ───────────────────
def fig_matrix_drift():
    W, H = 1060, 520
    frags = []

    frags.append(text(270, 42, "роздробленість: у кожного споживача своя копія прапорців", size=14.5, bold=True))
    frags.append(text(800, 42, "декларація: єдине джерело істини", size=14.5, bold=True))

    # Ліва колонка — розрізнені інструменти
    tools_bad = [
        ("Термінал (розробник Linux)", "cmake -B build -DCMAKE_BUILD_TYPE=Debug -DENABLE_TESTS=ON"),
        ("CI Runner (GitHub Actions)", "cmake -B out -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=1"),
        ("VS Code (settings.json)", "\"cmake.configureSettings\": {\"TESTS\": \"ON\"}"),
        ("Visual Studio (CMakeSettings)", "{\"name\": \"x64-Debug\", \"variables\": [...]}"),
    ]
    y = 76
    for title_line, cmd in tools_bad:
        frags.append(fitbox(50, y, 440, 64, title_line + "\n" + cmd, size=12.5, fill=WARN_FILL, stroke=POS))
        y += 82

    frags.append(fitbox(50, 416, 440, 74,
                        "прапорці розходяться між машинами й середовищами;\n"
                        "локальна збірка не повторює збірку на сервері CI,\n"
                        "а зміна опції вимагає правок у чотирьох різних місцях",
                        size=12.5, fill=FILL, stroke=MUTED))

    # Права колонка — єдиний файл пресетів і стрілки до споживачів
    frags.append(fitbox(640, 76, 320, 100,
                        "CMakePresets.json\n"
                        "configurePresets: [\"dev-debug\", \"ci-release\"]\n"
                        "buildPresets: [\"dev-debug\", \"ci-release\"]\n"
                        "testPresets: [\"dev-debug\", \"ci-release\"]",
                        size=13, fill=OK_FILL, stroke=FIELD, bold=True))

    # Споживачі праворуч
    consumers = [
        ("CLI", "cmake --preset dev-debug\ncmake --build --preset dev-debug"),
        ("CI Runner", "cmake --workflow --preset ci-release"),
        ("IDE (VS Code, VS, CLion)", "Вибір пресета зі списку без локальних скриптів"),
    ]
    cy = 230
    for title_line, desc in consumers:
        frags.append(fitbox(630, cy, 340, 58, title_line + "\n" + desc, size=12.5, fill=FILL, stroke=LINE))
        cy += 74

    # Стрілки від CMakePresets.json до споживачів
    frags.append(arrow(750, 180, 700, 226))
    frags.append(arrow(800, 180, 800, 226))
    frags.append(arrow(850, 180, 900, 226))

    frags.append(fitbox(560, 456, 470, 48,
                        "команда фіксує конфігурації у версійному JSON;\n"
                        "усі інструменти читають один і той самий набір параметрів",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "matrix-drift.svg"), W, H, *frags,
           title="Роздробленість конфігурацій проти єдиної декларації у CMakePresets.json")


# ── 2. Шари: версійний CMakePresets і локальний CMakeUserPresets ────────────
def fig_presets_hierarchy():
    W, H = 1060, 540
    frags = []

    frags.append(text(280, 42, "CMakePresets.json (у репозиторії Git)", size=14.5, bold=True))
    frags.append(text(800, 42, "CMakeUserPresets.json (у .gitignore)", size=14.5, bold=True))

    # Ліва частина — CMakePresets.json
    frags.append(rect(40, 68, 480, 390, fill=FILL, stroke=LINE, rx=8))
    frags.append(text(280, 92, "Командні спільні пресети", size=13, color=MUTED))

    frags.append(fitbox(70, 114, 420, 84,
                        "\"base-ninja\" (hidden: true)\n"
                        "generator: \"Ninja\"\n"
                        "binaryDir: \"${sourceDir}/build/${presetName}\"\n"
                        "cacheVariables: { CMAKE_EXPORT_COMPILE_COMMANDS: true }",
                        size=12.5, fill=BG, stroke=LINE))

    frags.append(arrow(280, 202, 200, 246))
    frags.append(arrow(280, 202, 360, 246))

    frags.append(fitbox(60, 250, 200, 90,
                        "\"dev-debug\"\n"
                        "inherits: \"base-ninja\"\n"
                        "cacheVariables:\n"
                        "  CMAKE_BUILD_TYPE: \"Debug\"\n"
                        "  ENABLE_TESTS: true",
                        size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(280, 250, 220, 90,
                        "\"ci-release\"\n"
                        "inherits: \"base-ninja\"\n"
                        "cacheVariables:\n"
                        "  CMAKE_BUILD_TYPE: \"Release\"\n"
                        "  ENABLE_TESTS: true",
                        size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(70, 360, 420, 80,
                        "\"linux-clang-asan\"\n"
                        "inherits: \"dev-debug\"\n"
                        "environment: { CC: \"clang\", CXX: \"clang++\" }\n"
                        "cacheVariables: { ENABLE_ASAN: true }",
                        size=12, fill=BG, stroke=LINE))
    frags.append(arrow(160, 344, 210, 356))

    # Права частина — CMakeUserPresets.json
    frags.append(rect(560, 68, 460, 390, fill=FILL, stroke=LINE, rx=8))
    frags.append(text(790, 92, "Приватні налаштування розробника", size=13, color=MUTED))

    frags.append(fitbox(580, 114, 420, 110,
                        "\"my-local-debug\"\n"
                        "inherits: \"dev-debug\"\n"
                        "cacheVariables:\n"
                        "  CMAKE_TOOLCHAIN_FILE: \"C:/vcpkg/scripts/vcpkg.cmake\"\n"
                        "  Qt6_DIR: \"/opt/Qt/6.6.0/gcc_64/lib/cmake/Qt6\"\n"
                        "  LOCAL_DEBUG_LOGS: true",
                        size=12.5, fill=USER_FILL, stroke=NEG))

    frags.append(fitbox(580, 250, 420, 90,
                        "\"my-custom-clang\"\n"
                        "inherits: \"linux-clang-asan\"\n"
                        "environment:\n"
                        "  PATH: \"/opt/llvm-18/bin:$penv{PATH}\"",
                        size=12.5, fill=USER_FILL, stroke=NEG))

    frags.append(arrow(264, 290, 576, 170, color=NEG))
    frags.append(arrow(494, 390, 576, 290, color=NEG))

    frags.append(fitbox(40, 474, 980, 52,
                        "UserPresets вільно успадковує пресети з CMakePresets.json і перевизначає локальні шляхи;\n"
                        "CMakePresets.json нічого не знає про UserPresets і зберігає чисту конфігурацію команди",
                        size=13, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "presets-hierarchy.svg"), W, H, *frags,
           title="Структура успадкування між CMakePresets і CMakeUserPresets")


# ── 3. П'ять фаз життєвого циклу ───────────────────────────────────────────
def fig_phases_lifecycle():
    W, H = 1060, 520
    frags = []

    frags.append(text(530, 38, "П'ять типів пресетів у життєвому циклі проєкту", size=15, bold=True))

    phases = [
        ("1. configurePresets", "генератор, binaryDir, змінні кешу, тулчейн", "cmake --preset <cfg>", OK_FILL, FIELD),
        ("2. buildPresets", "таргети, конфігурація, паралелізм jobs", "cmake --build --preset <bld>", BG, LINE),
        ("3. testPresets", "фільтри тестів, тайм-аути, повтори ctest", "ctest --preset <tst>", BG, LINE),
        ("4. packagePresets", "генератори CPack (TGZ, DEB, RPM, ZIP)", "cpack --preset <pkg>", BG, LINE),
    ]

    x = 40
    for name, desc, cmd, fl, st in phases:
        frags.append(fitbox(x, 70, 220, 160,
                            name + "\n\n" + desc + "\n\n" + cmd,
                            size=12, fill=fl, stroke=st, bold=True))
        if x < 750:
            frags.append(arrow(x + 224, 150, x + 248, 150))
        x += 255

    # Нижня частина — Workflow Presets
    frags.append(rect(40, 270, 980, 160, fill=USER_FILL, stroke=NEG, rx=8))
    frags.append(text(530, 300, "5. workflowPresets (оркестрація всього ланцюжка)", size=14, bold=True))
    frags.append(text(530, 324, "cmake --workflow --preset <flow>", size=13, color=MUTED))

    wf_steps = [
        ("Крок 1: configure", "type: \"configure\"\nname: \"ci-release\""),
        ("Крок 2: build", "type: \"build\"\nname: \"ci-release\""),
        ("Крок 3: test", "type: \"test\"\nname: \"ci-release\""),
        ("Крок 4: package", "type: \"package\"\nname: \"ci-release\""),
    ]
    wx = 70
    for st_title, st_body in wf_steps:
        frags.append(fitbox(wx, 344, 200, 68, st_title + "\n" + st_body, size=11.5, fill=BG, stroke=LINE))
        if wx < 650:
            frags.append(arrow(wx + 204, 378, wx + 226, 378))
        wx += 235

    frags.append(fitbox(40, 450, 980, 52,
                        "кожний наступний тип спирається на результат попереднього;\n"
                        "workflowPresets з'єднує чотири кроки в один детермінований автоматизований прогін",
                        size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "phases-lifecycle.svg"), W, H, *frags,
           title="Фази життєвого циклу CMakePresets")


# ── 4. Підстановка макросів у полях ─────────────────────────────────────────
def fig_macro_resolution():
    W, H = 1060, 480
    frags = []

    frags.append(text(530, 38, "Механізм розкриття динамічних макросів у JSON", size=15, bold=True))

    macros = [
        ("${sourceDir}", "Каталог із головним CMakeLists.txt", "/home/dev/repo"),
        ("${presetName}", "Ім'я поточного пресета", "linux-clang-debug"),
        ("${generator}", "Назва генератора у поточному пресеті", "Ninja"),
        ("$env{VCPKG_ROOT}", "Значення змінної оточення хоста", "/opt/vcpkg"),
        ("$penv{PATH}", "Батьківський PATH до змін у пресеті", "/usr/bin:/bin"),
    ]

    y = 72
    for name, meaning, example in macros:
        frags.append(fitbox(50, y, 220, 54, name, size=13.5, fill=BG, stroke=LINE, bold=True))
        frags.append(fitbox(290, y, 420, 54, meaning, size=12.5, fill=FILL, stroke=LINE))
        frags.append(fitbox(730, y, 280, 54, "-> " + example, size=12.5, fill=OK_FILL, stroke=FIELD))
        y += 64

    # Приклад результату
    sample = (
        "Поле у JSON:   \"binaryDir\": \"${sourceDir}/build/${presetName}\"\n"
        "Результат:     /home/dev/repo/build/linux-clang-debug"
    )
    frags.append(fitbox(50, 400, 960, 62, sample, size=13, fill=USER_FILL, stroke=NEG))

    render(os.path.join(IMG, "macro-resolution.svg"), W, H, *frags,
           title="Розкриття макросів у полях пресетів")


fig_matrix_drift()
fig_presets_hierarchy()
fig_phases_lifecycle()
fig_macro_resolution()
print("ok")
