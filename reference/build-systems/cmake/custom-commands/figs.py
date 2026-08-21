# -*- coding: utf-8 -*-
"""Фігури до теми «Власні команди й цілі: кодогенерація у збірці»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL   = "#eafaf1"
INFO_FILL = "#eaf0fd"


# ── 1. Граф залежностей: add_custom_command проти add_custom_target ──────────
def fig_dag_custom_command_vs_target():
    W, H = 1040, 600
    frags = []
    frags.append(text(W / 2, 38, "Два способи виконання власних дій у графі збірки CMake",
                      size=15, color=MUTED))

    # Ліва колонка: add_custom_command(OUTPUT ...)
    lx, col_w = 265, 470
    frags.append(fitbox(lx - col_w / 2, 65, col_w, 42,
                        "add_custom_command(OUTPUT ...)\nПравило генерації файлу (ліниве, за мітками часу)",
                        size=12, bold=True, fill=OK_FILL, stroke=FIELD))

    cmd_steps = [
        (125, 48, "1. Вхідний файл (schema.dsl)\nДжерело опису даних або протоколу", FILL, LINE),
        (195, 54, "2. Перевірка актуальності в графі\nmtime(schema.dsl) > mtime(msg.cpp) ?", INFO_FILL, NEG),
        (271, 50, "3. Виконання генератора (якщо застаріло)\ngenerator_tool schema.dsl -> msg.cpp, msg.h", OK_FILL, FIELD),
        (343, 50, "4. Властивість GENERATED = 1 на файлі msg.cpp\nКомпілятор викликається для msg.cpp -> msg.o", FILL, LINE),
        (415, 48, "5. Фінальний артефакт (app)\nЛінкування об'єктних файлів у бінарник", INFO_FILL, LINE),
    ]
    for y, h, s, f, st in cmd_steps:
        frags.append(fitbox(lx - col_w / 2, y, col_w, h, s, size=11.5, fill=f, stroke=st))

    for y in [173, 249, 321, 393]:
        frags.append(arrow(lx, y, lx, y + 22))

    # Права колонка: add_custom_target(Name ...)
    rx = 775
    frags.append(fitbox(rx - col_w / 2, 65, col_w, 42,
                        "add_custom_target(Name ...)\nФіктивна ціль-дія (завжди вважається застарілою)",
                        size=12, bold=True, fill=WARN_FILL, stroke=POS))

    tgt_steps = [
        (125, 48, "1. Іменована ціль (run_linter / run_codegen)\nНе має прив'язаного дискового артефакту", FILL, LINE),
        (195, 54, "2. Запуск на вимогу або через ALL\nЗавжди 'out-of-date' (немає перевірки mtime)", WARN_FILL, POS),
        (271, 50, "3. Виконання командного рядка\nclippy/clang-tidy або безумовний скрипт", WARN_FILL, POS),
        (343, 50, "4. Не створює гарантованих вихідних вузлів\nНе може автоматично передати .cpp цілям", FILL, LINE),
        (415, 48, "5. Якщо примусово згенерує файл msg.cpp\nКожен запуск оновлює mtime -> повна перезбірка!", WARN_FILL, POS),
    ]
    for y, h, s, f, st in tgt_steps:
        frags.append(fitbox(rx - col_w / 2, y, col_w, h, s, size=11.5, fill=f, stroke=st))

    for y in [173, 249, 321, 393]:
        frags.append(arrow(rx, y, rx, y + 22))

    # Нижня плашка
    frags.append(fitbox(40, 485, 960, 68,
                        "Головне розмежування: add_custom_command додає правило генерації файлу у граф і спрацьовує\n"
                        "лише коли файл потрібен іншій цілі; add_custom_target створює точку входу для запуску дій.",
                        size=12.5, bold=True, fill=INFO_FILL, stroke=NEG))

    render(os.path.join(IMG, "dag-custom-command-vs-target.svg"), W, H, *frags,
           title="add_custom_command проти add_custom_target у графі CMake")


# ── 2. Динамічні залежності та DEPFILE ───────────────────────────────────────
def fig_depfile_lifecycle():
    W, H = 1020, 580
    frags = []
    frags.append(text(W / 2, 38, "Відстеження неявних залежностей кодогенератора через DEPFILE",
                      size=15, color=MUTED))

    # Крок 1: Входи та імпорти
    frags.append(fitbox(50, 70, 280, 76,
                        "Вхідні файли схеми:\n• schema.dsl (відомий CMake)\n• types.dsl (імпортується)\n• consts.dsl (імпортується)",
                        size=11.5, fill=INFO_FILL, stroke=NEG))

    # Крок 2: Робота генератора
    frags.append(fitbox(370, 70, 280, 76,
                        "Кастомний кодогенератор:\n1. Парсить schema.dsl\n2. Знаходить include/import\n3. Генерує код та .d файл",
                        size=11.5, fill=OK_FILL, stroke=FIELD))

    # Крок 3: Вихідні файли
    frags.append(fitbox(690, 70, 280, 76,
                        "Артефакти генерації:\n• msg.cpp + msg.h (код)\n• msg.cpp.d (depfile формату Makefile)",
                        size=11.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(330, 108, 370, 108))
    frags.append(arrow(650, 108, 690, 108))

    # Центральний блок: вміст depfile
    frags.append(fitbox(150, 175, 720, 68,
                        "Вміст файлу msg.cpp.d:\nmsg.cpp: schema.dsl types.dsl consts.dsl\n(Синтаксис Makefile: вихідний файл залежить від повного списку відкритих джерел)",
                        size=12, bold=True, fill=FILL, stroke=LINE))

    frags.append(arrow(830, 146, 830, 175))

    # Нижня частина: як рушій Ninja підхоплює граф
    frags.append(fitbox(50, 275, 920, 150,
                        "ЖИТТЄВИЙ ЦИКЛ ОНОВЛЕННЯ БЕЗ ПЕРЕКОНФІГУРАЦІЇ CMAKE:\n\n"
                        "1. Рушій збірки (Ninja) читає msg.cpp.d після першого запуску генератора\n"
                        "2. Залежності між msg.cpp та types.dsl/consts.dsl записуються у внутрішню базу .ninja_deps\n"
                        "3. Розробник змінює consts.dsl (який не згаданий у CMakeLists.txt!)\n"
                        "4. На наступному кроці 'ninja' виявляє mtime(consts.dsl) > mtime(msg.cpp) і перезапускає генератор\n"
                        "5. Конфігурація CMake не потрібна — граф актуалізується миттєво під час збірки",
                        size=12, fill=INFO_FILL, stroke=NEG))

    frags.append(arrow(510, 243, 510, 275))

    # Нижня рамка з резюме
    frags.append(fitbox(50, 455, 920, 65,
                        "Без DEPFILE довелося б вручну перелічувати всі імпортовані файли в DEPENDS\n"
                        "або запускати переконфігурацію CMake при будь-якій зміні внутрішньої структури схеми.",
                        size=12.5, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "depfile-lifecycle.svg"), W, H, *frags,
           title="Відстеження залежностей через DEPFILE у Ninja")


# ── 3. Крос-компіляція: Хост-генератор проти Цільової платформи ──────────────
def fig_cross_compilation_tool_flow():
    W, H = 1040, 590
    frags = []
    frags.append(text(W / 2, 38, "Архітектура кодогенерації при крос-компіляції (Host vs Target)",
                      size=15, color=MUTED))

    # Верхня зона: Хост (машина розробника)
    frags.append(fitbox(40, 65, 460, 210,
                        "ХОСТ (Host Machine: x86_64 Linux/macOS/Windows)\n\n"
                        "• Хостовий компілятор (Host GCC/Clang/MSVC)\n"
                        "• Збирає генератор: add_executable(codegen_tool ...)\n"
                        "• Бінарник codegen_tool має архітектуру x86_64\n"
                        "• Виконується на хості під час кроку збірки:\n"
                        "  COMMAND codegen_tool protocol.def\n"
                        "• Результат: згенеровані protocol.c та protocol.h",
                        size=12, fill=OK_FILL, stroke=FIELD))

    # Стрілка посередині: передача коду
    frags.append(fitbox(540, 65, 460, 210,
                        "ЦІЛЬОВА ПЛАТФОРМА (Target: ARM Cortex-M / AArch64)\n\n"
                        "• Крос-компілятор (arm-none-eabi-gcc / aarch64-gcc)\n"
                        "• Читає згенеровані protocol.c + protocol.h\n"
                        "• Компілює у двійковий код цільової архітектури\n"
                        "• Лінкує з рештою компонентів у firmware.elf / app\n"
                        "• Запускається на мікроконтролері або цільовій платі",
                        size=12, fill=INFO_FILL, stroke=NEG))

    frags.append(arrow(500, 170, 540, 170, color=FIELD))
    frags.append(text(520, 155, "C/H", size=12, color=FIELD, bold=True))

    # Нижня частина: Пастка та правильні підходи
    frags.append(fitbox(40, 305, 960, 130,
                        "ГОЛОВНА ПАСТКА КРОС-КОМПІЛЯЦІЇ:\n"
                        "Якщо при CMAKE_CROSSCOMPILING=TRUE зібрати генератор звичайним add_executable(codegen_tool ...),\n"
                        "CMake скомпілює його крос-компілятором під ARM. При спробі виконати COMMAND codegen_tool\n"
                        "хостова система поверне помилку 'Exec format error' — бінарник ARM не може виконуватися на x86_64!",
                        size=12, fill=WARN_FILL, stroke=POS))

    # Стратегії вирішення
    frags.append(fitbox(40, 460, 960, 75,
                        "Три робочі стратегії вирішення:\n"
                        "1. Попередньо зібраний хост-інструмент + find_program() або IMPORTED-ціль\n"
                        "2. Двоетапна збірка (Superbuild) через ExternalProject_Add для хостових цілей\n"
                        "3. Окрема нативна конфігурація хоста з експортом цілей (export/import)",
                        size=12, bold=True, fill=INFO_FILL, stroke=NEG))

    render(os.path.join(IMG, "cross-compilation-tool-flow.svg"), W, H, *frags,
           title="Кодогенерація при крос-компіляції у CMake")


# ── 4. Хуки життєвого циклу цілі (TARGET hooks) ──────────────────────────────
def fig_target_hook_lifecycle():
    W, H = 1040, 570
    frags = []
    frags.append(text(W / 2, 38, "Стадії збірки цілі та хуки add_custom_command(TARGET ...)",
                      size=15, color=MUTED))

    # Горизонтальний конвеєр стадій збірки
    stages = [
        (40, 80, 160, 65, "1. Початок збірки\nПідготовка дерева", FILL),
        (240, 80, 160, 65, "2. Компіляція\nsrc.cpp -> src.o", INFO_FILL),
        (440, 80, 160, 65, "3. Перед лінкуванням\nУсі .o готові", FILL),
        (640, 80, 160, 65, "4. Лінкування\nld -> binary.elf", INFO_FILL),
        (840, 80, 160, 65, "5. Фінал\nБінарник готовий", OK_FILL),
    ]
    for x, y, w, h, s, f in stages:
        frags.append(fitbox(x, y, w, h, s, size=12, fill=f, stroke=LINE))

    for x in [200, 400, 600, 800]:
        frags.append(arrow(x, 112, x + 40, 112))

    # Хуки
    # PRE_BUILD
    frags.append(fitbox(40, 185, 230, 110,
                        "PRE_BUILD\n\n"
                        "• Працює у Visual Studio (MSVC)\n"
                        "• Виконується до компіляції файлів\n"
                        "• У Ninja/Makefile працює як PRE_LINK\n"
                        "  (не підходить для генерації .h!)",
                        size=11.5, fill=WARN_FILL, stroke=POS))
    frags.append(arrow(120, 145, 120, 185, color=POS))

    # PRE_LINK
    frags.append(fitbox(390, 185, 260, 110,
                        "PRE_LINK\n\n"
                        "• Виконується після компіляції всіх .o,\n"
                        "  але перед викликом лінкера\n"
                        "• Вбудовування маніфестів, перевірка\n"
                        "  експортованих символів, генерація табл.",
                        size=11.5, fill=INFO_FILL, stroke=NEG))
    frags.append(arrow(520, 145, 520, 185, color=NEG))

    # POST_BUILD
    frags.append(fitbox(770, 185, 230, 110,
                        "POST_BUILD\n\n"
                        "• Виконується після успішного лінкування\n"
                        "• Конвертація objcopy (.elf -> .bin/.hex)\n"
                        "• Підпис бінарника кодом (codesign)\n"
                        "• Копіювання .dll поруч із .exe",
                        size=11.5, fill=OK_FILL, stroke=FIELD))
    frags.append(arrow(920, 145, 920, 185, color=FIELD))

    # Нижня частина: Головне застереження
    frags.append(fitbox(40, 335, 960, 175,
                        "ПРАВИЛА ВИКОРИСТАННЯ ХУКІВ ЦІЛІ:\n\n"
                        "1. Хуки add_custom_command(TARGET ...) ПРИВ'ЯЗАНІ ДО ЦІЛІ, а не до файлів на диску.\n"
                        "2. Вони не можуть замінити add_custom_command(OUTPUT ...): генератор коду .cpp/.h, запущений\n"
                        "   у PRE_BUILD на генераторах Ninja або Make, виконається ЗАПІЗНО — компілятор уже спробує\n"
                        "   прочитати відсутні файли джерел і завершиться з помилкою!\n"
                        "3. POST_BUILD — найнадійніший і найпоширеніший хук для вторинної обробки вже готового бінарника.",
                        size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "target-hook-lifecycle.svg"), W, H, *frags,
           title="Хуки життєвого циклу цілі у CMake")


if __name__ == "__main__":
    fig_dag_custom_command_vs_target()
    fig_depfile_lifecycle()
    fig_cross_compilation_tool_flow()
    fig_target_hook_lifecycle()
    print("Всі фігури згенеровано успішно.")
