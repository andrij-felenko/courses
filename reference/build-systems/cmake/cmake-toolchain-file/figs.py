# -*- coding: utf-8 -*-
"""Фігури до теми «Файл тулчейна: як CMake дізнається про чужу платформу»."""
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


# ── 1. Життєвий цикл і порядок виконання Toolchain File ─────────────────────
def fig_toolchain_execution_flow():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 32, "Порядок завантаження файлу тулчейна під час конфігурації CMake", size=16, bold=True))

    # Крок 1: Запуск
    body, _, _ = textbox(160, 80, [
        "1. Запуск конфігурації",
        "cmake -B build -S .",
        "-DCMAKE_TOOLCHAIN_FILE=...",
        "або через CMakePresets.json",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Стрілка 1 -> 2
    frags.append(arrow(270, 80, 360, 80))

    # Крок 2: project()
    body, _, _ = textbox(470, 80, [
        "2. Виклик project(App C CXX)",
        "CMake ініціалізує мови",
        "та починає опитування",
        "цільової платформи",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Стрілка 2 -> 3
    frags.append(arrow(580, 80, 670, 80))

    # Крок 3: Завантаження Toolchain
    body, _, _ = textbox(810, 80, [
        "3. Виконання Toolchain File",
        "Завантажується ДО тестів",
        "Встановлює CMAKE_SYSTEM_NAME,",
        "CMAKE_C_COMPILER, sysroot",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Стрілка вниз до перевірки
    frags.append(arrow(810, 135, 810, 185))

    # Перевірка CMAKE_SYSTEM_NAME
    body, _, _ = textbox(810, 230, [
        "4. Визначення режиму збірки",
        "Чи встановлено CMAKE_SYSTEM_NAME",
        "відмінним від хост-системи?",
    ], size=12.5, fill=FILL, stroke=LINE)
    frags.append(body)

    # Розгалуження: вліво (Host), вниз (Cross)
    frags.append(arrow(680, 230, 520, 230))
    frags.append(text(600, 218, "Ні (не задано)", size=11.5, color=MUTED, bold=True))

    frags.append(arrow(810, 275, 810, 325))
    frags.append(text(885, 298, "Так (Generic / Linux)", size=11.5, color=FIELD, bold=True))

    # Нативна збірка
    body, _, _ = textbox(380, 230, [
        "Нативна збірка (Host)",
        "CMAKE_CROSSCOMPILING = FALSE",
        "Компілятор тестується для хоста",
        "Пошук у стандартних /usr/lib",
    ], size=12, fill=FILL, stroke=MUTED)
    frags.append(body)

    # Крос-компіляція
    body, _, _ = textbox(810, 375, [
        "Крос-компіляція (Target)",
        "CMAKE_CROSSCOMPILING = TRUE",
        "try_compile() запускається для цілі",
        "Пошукові команди блокують хост",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Стрілка до виконання CMakeLists.txt
    frags.append(arrow(810, 425, 810, 460))
    frags.append(arrow(380, 280, 380, 480))
    frags.append(arrow(380, 480, 670, 480))

    # Фінал: виконання решти CMakeLists.txt
    body, _, _ = textbox(810, 480, [
        "5. Виконання основного тіла CMakeLists.txt",
        "Цілі компілюються цільовим тулчейном за правилами ізоляції sysroot",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    render(os.path.join(IMG, "toolchain-execution-flow.svg"), W, H, *frags,
           title="Порядок завантаження файлу тулчейна під час конфігурації CMake")


# ── 2. Маршрутизація пошукових шляхів CMAKE_FIND_ROOT_PATH ──────────────────
def fig_find_root_path_routing():
    W, H = 1040, 540
    frags = []

    frags.append(text(520, 32, "Маршрутизація пошуку між хостом та sysroot за CMAKE_FIND_ROOT_PATH_MODE_*", size=16, bold=True))

    # Джерело: Команди пошуку у CMake
    body, _, _ = textbox(180, 150, [
        "Команда CMake:",
        "find_program(PROTOC protoc)",
        "Потрібен генератор коду",
    ], size=12.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    body, _, _ = textbox(180, 390, [
        "Команди CMake:",
        "find_path(PNG_H png.h)",
        "find_library(PNG_LIB png)",
        "find_package(OpenSSL)",
        "Потрібні цільові файли",
    ], size=12.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Центральний диспетчер (режими)
    body, _, _ = textbox(520, 150, [
        "CMAKE_FIND_ROOT_PATH_MODE_PROGRAM = NEVER",
        "Правило: виконувані інструменти збірки",
        "мають запускатися на ЦЬОМУ комп'ютері (Host CPU)",
    ], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    body, _, _ = textbox(520, 390, [
        "CMAKE_FIND_ROOT_PATH_MODE_INCLUDE = ONLY",
        "CMAKE_FIND_ROOT_PATH_MODE_LIBRARY = ONLY",
        "CMAKE_FIND_ROOT_PATH_MODE_PACKAGE = ONLY",
        "Правило: заголовки й бібліотеки беруться ЛИШЕ з sysroot",
    ], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    frags.append(arrow(300, 150, 370, 150))
    frags.append(arrow(300, 390, 350, 390))

    # Праві блоки: Файлова система Host проти Target Sysroot
    body, _, _ = textbox(860, 150, [
        "Хостова система (Host OS)",
        "Каталоги: /usr/bin, /usr/local/bin",
        "Бінарники x86_64: виконуються на хості",
        "Результат: /usr/bin/protoc [УСПІХ]",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    body, _, _ = textbox(860, 390, [
        "Цільовий Sysroot (Target Root)",
        "Шлях: CMAKE_SYSROOT = /opt/sysroot-arm64",
        "Каталоги: /opt/sysroot-arm64/usr/include",
        "та /opt/sysroot-arm64/usr/lib",
        "Результат: libpng.so для ARM64 [УСПІХ]",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(670, 150, 720, 150))
    frags.append(arrow(690, 390, 720, 390))

    # Попередження про ізоляцію посередині
    body, _, _ = textbox(520, 270, [
        "ІЗОЛЯЦІЯ: Хостові /usr/lib та /usr/include",
        "заблоковані для пошуку (режим ONLY)",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Червоні стрілки блокування, що не перетинають текст
    frags.append(arrow(680, 270, 770, 200, color=POS))
    frags.append(text(750, 245, "заборонено", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "find-root-path-routing.svg"), W, H, *frags,
           title="Маршрутизація пошуку між хостом та sysroot за CMAKE_FIND_ROOT_PATH_MODE_*")


# ── 3. Проблема try_compile для Bare-Metal ─────────────────────────────────
def fig_baremetal_trycompile_dilemma():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 32, "Перевірка компілятора під час project() для платформ без ОС (Bare-Metal)", size=16, bold=True))

    # Ліва частина: Стандартна поведінка (EXECUTABLE)
    body, _, _ = textbox(270, 80, [
        "Стандартна перевірка CMake",
        "try_compile() збирає тестовий виконуваний файл",
        "arm-none-eabi-gcc test.c -o test.elf",
    ], size=12.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    frags.append(arrow(270, 130, 270, 180))

    body, _, _ = textbox(270, 245, [
        "Збій на стадії лінкування (Linker Error)",
        "• Немає системної бібліотеки (libc/libgloss)",
        "• Відсутні системні виклики: _exit, _sbrk, _write",
        "• Не задано карту пам'яті (-T linker_script.ld)",
        "Помилка: 'The C compiler is not able to",
        "compile a simple test program'",
    ], size=12, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    frags.append(arrow(270, 315, 270, 370))

    body, _, _ = textbox(270, 420, [
        "Результат: АВАРІЙНА ЗУПИНКА",
        "CMake зупиняє генерацію до того,",
        "як прочитає решту CMakeLists.txt",
    ], size=12.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Розділювач
    frags.append(line(520, 60, 520, 480, color=LINE, dash="4,4"))

    # Права частина: Виправлення через STATIC_LIBRARY
    body, _, _ = textbox(770, 80, [
        "Рішення у Toolchain File",
        "set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)",
        "Вказівка CMake тестувати компілятор без лінкера",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(770, 130, 770, 180))

    body, _, _ = textbox(770, 245, [
        "Перевірка через архіватор (Archiver)",
        "1. Компіляція: arm-none-eabi-gcc -c test.c -o test.o",
        "2. Архівація: arm-none-eabi-ar cr libtest.a test.o",
        "Лінкер НЕ викликається!",
        "Тест підтверджує працездатність компілятора",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(770, 315, 770, 370))

    body, _, _ = textbox(770, 420, [
        "Результат: УСПІШНА КОНФІГУРАЦІЯ",
        "CMake фіксує тулчейн, а скрипт лінкера",
        "та стартап-код підключаються вже в цілях проєкту",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    render(os.path.join(IMG, "baremetal-trycompile-dilemma.svg"), W, H, *frags,
           title="Перевірка компілятора під час project() для платформ без ОС (Bare-Metal)")


if __name__ == "__main__":
    fig_toolchain_execution_flow()
    fig_find_root_path_routing()
    fig_baremetal_trycompile_dilemma()
    print("Фігури згенеровано успішно.")
