# -*- coding: utf-8 -*-
"""Фігури до теми «Цілі й властивості замість глобальних змінних»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"


# ── 1. Змінна копіюється деревом, ціль одна на все дерево ───────────────────
def fig_variable_vs_target():
    W, H = 1080, 590
    frags = []

    frags.append(text(260, 62, "змінна: у кожному каталозі своя копія", size=15, bold=True))
    frags.append(text(800, 62, "ціль: один об'єкт на все дерево", size=15, bold=True))

    dirs = [
        ("CMakeLists.txt (корінь)", "EXTRA_FLAGS = -DFAST"),
        ("src/CMakeLists.txt", "EXTRA_FLAGS = -DFAST -DSIMD"),
        ("app/CMakeLists.txt", "EXTRA_FLAGS = -DFAST"),
    ]
    y = 100
    for title_line, value_line in dirs:
        frags.append(fitbox(60, y, 400, 68, title_line + "\n" + value_line, size=13.5))
        y += 110
    frags.append(arrow(150, 170, 150, 208))
    frags.append(arrow(150, 280, 150, 318))
    frags.append(text(172, 194, "копія на момент add_subdirectory", size=12, color=MUTED, anchor="start"))
    frags.append(text(172, 304, "сусід про зміну не знає", size=12, color=MUTED, anchor="start"))

    body, _, _ = textbox(800, 130, ["src/CMakeLists.txt", "add_library(img img.cpp)"], size=13.5)
    frags.append(body)
    frags.append(arrow(800, 162, 800, 202))
    frags.append(text(822, 188, "створює й наповнює", size=12, color=MUTED, anchor="start"))

    body, _, _ = textbox(800, 278, [
        "ціль  img",
        "TYPE = STATIC_LIBRARY",
        "SOURCES = img.cpp",
        "INTERFACE_INCLUDE_DIRECTORIES = include",
        "INTERFACE_COMPILE_DEFINITIONS = IMG_SIMD",
    ], size=13.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)
    frags.append(arrow(800, 356, 800, 396))
    frags.append(text(822, 382, "читає за іменем", size=12, color=MUTED, anchor="start"))
    body, _, _ = textbox(800, 428, ["app/CMakeLists.txt", "target_link_libraries(app img)"], size=13.5)
    frags.append(body)

    frags.append(fitbox(60, 496, 960, 62,
                        "змінна описує МІСЦЕ в дереві файлів; ціль описує РІЧ, яку буде зібрано —\n"
                        "а лінкують саме річ, і разом з нею приходить увесь її опис", size=14))
    render(os.path.join(IMG, "variable-vs-target.svg"), W, H, *frags,
           title="Змінна копіюється деревом, ціль одна на все дерево")


# ── 2. Властивість — знімок змінної в момент створення цілі ─────────────────
def fig_snapshot():
    W, H = 1000, 550
    frags = []
    frags.append(text(60, 58, "CMakeLists.txt виконується згори вниз:", size=13, color=MUTED, anchor="start"))

    rows = [
        ("set(CMAKE_CXX_STANDARD 17)", "змінна каталогу = 17", MUTED, BG),
        ("add_library(core core.cpp)", "core.CXX_STANDARD = 17   (знімок)", FIELD, OK_FILL),
        ("set(CMAKE_CXX_STANDARD 20)", "змінна каталогу = 20", MUTED, BG),
        ("add_executable(app main.cpp)", "app.CXX_STANDARD = 20   (знімок)", FIELD, OK_FILL),
        ("set(CMAKE_CXX_STANDARD 23)", "на core і app НЕ впливає — вони вже створені", POS, WARN_FILL),
    ]
    y = 104
    for src, effect, st, fl in rows:
        frags.append(text(60, y + 5, src, size=14, anchor="start"))
        frags.append(fitbox(470, y - 24, 470, 48, effect, size=13.5, stroke=st, fill=fl))
        y += 76

    frags.append(fitbox(60, 468, 880, 62,
                        "змінна CMAKE_<ВЛАСТИВІСТЬ> лише задає усталене значення для наступних цілей;\n"
                        "після створення ціль живе власною властивістю й змінну більше не читає", size=14))
    render(os.path.join(IMG, "snapshot.svg"), W, H, *frags,
           title="Властивість — знімок змінної в момент створення цілі")


# ── 3. Дві половини торби властивостей ──────────────────────────────────────
def fig_two_halves():
    W, H = 1040, 540
    frags = []
    frags.append(text(520, 56, "ключове слово вирішує, у яку половину лягає запис",
                      size=13, color=MUTED))

    frags.append(rect(180, 84, 680, 258))
    frags.append(text(520, 116, "ціль  img", size=16, bold=True))
    frags.append(text(520, 140, "TYPE = STATIC_LIBRARY", size=12.5, color=MUTED))

    frags.append(fitbox(210, 162, 290, 160,
                        "щоб зібрати СЕБЕ\nSOURCES\nINCLUDE_DIRECTORIES\nCOMPILE_DEFINITIONS\nLINK_LIBRARIES",
                        size=13.5))
    frags.append(fitbox(540, 162, 290, 160,
                        "щоб мене ВЖИВАЛИ\nINTERFACE_INCLUDE_DIRECTORIES\nINTERFACE_COMPILE_DEFINITIONS\n"
                        "INTERFACE_LINK_LIBRARIES\nINTERFACE_COMPILE_FEATURES",
                        size=13.5))

    body, _, _ = textbox(290, 440, ["PRIVATE", "лише ліва половина"], size=13.5)
    frags.append(body)
    body, _, _ = textbox(520, 440, ["PUBLIC", "обидві половини"], size=13.5)
    frags.append(body)
    body, _, _ = textbox(770, 440, ["INTERFACE", "лише права половина"], size=13.5)
    frags.append(body)

    frags.append(arrow(290, 406, 320, 330))
    frags.append(arrow(478, 406, 400, 330))
    frags.append(arrow(562, 406, 640, 330))
    frags.append(arrow(770, 406, 720, 330))

    render(os.path.join(IMG, "two-halves.svg"), W, H, *frags,
           title="Дві половини торби властивостей цілі")



# ── 4. Часова шкала повороту до цілей (вставка hist-target-turn) ────────────
def fig_target_turn_timeline():
    W, H = 1080, 320
    frags = []

    frags.append(text(540, 34, "Від каталожних команд до цілей", size=16, bold=True))
    frags.append(line(30, 92, 1050, 92, sw=2))

    marks = [
        (20, "2000", ["перший CMake для ITK;", "include_directories,", "add_definitions —", "усе на каталозі"], FILL),
        (280, "17.05.2013", ["CMake 2.8.11:", "target_include_directories,", "target_compile_definitions,", "PUBLIC / PRIVATE / INTERFACE"], OK_FILL),
        (540, "10.06.2014", ["CMake 3.0.0:", "інтерфейсні бібліотеки,", "імена з ::  —", "помилка, якщо цілі немає"], OK_FILL),
        (800, "2017", ["доповіді про Modern CMake;", "нові команди стають", "нормою громади,", "старі не прибирають"], FILL),
    ]
    for x, year, lines, fill in marks:
        cx = x + 120
        frags.append(circle(cx, 92, 8, fill=fill, stroke=LINE, sw=2))
        frags.append(text(cx, 66, year, size=15, bold=True))
        frags.append(fitbox(x, 130, 240, 120, lines, size=13, fill=fill))

    render(os.path.join(IMG, "target-turn-timeline.svg"), W, H, *frags,
           title="Часова шкала повороту CMake до моделі цілей")


fig_variable_vs_target()
fig_snapshot()
fig_two_halves()
fig_target_turn_timeline()
print("ok")
