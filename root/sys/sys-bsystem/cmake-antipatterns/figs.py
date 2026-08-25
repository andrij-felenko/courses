# -*- coding: utf-8 -*-
"""Фігури до теми «Антипатерни CMake і чому вони живучі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL   = "#eaf5ec"
INFO_FILL = "#eef4fb"


# ── 1. Чому file(GLOB) сліпить генератор збірки ──────────────────────────────
def fig_glob_rebuild_blindness():
    W, H = 1080, 580
    frags = []

    frags.append(text(260, 50, "Фаза 1: Конфігурація (cmake -B build)", size=15, bold=True))
    frags.append(text(820, 50, "Фаза 2: Додано файл і збірка (ninja)", size=15, bold=True))

    # Left Column: Configuration phase
    b1, _, _ = textbox(260, 110, [
        "Файлова система src/",
        "├── a.cpp",
        "└── b.cpp",
    ], size=13.5, pad=10)
    frags.append(b1)

    frags.append(arrow(260, 150, 260, 195))
    frags.append(text(285, 175, "file(GLOB SRC src/*.cpp)", size=12, color=MUTED, anchor="start"))

    b2, _, _ = textbox(260, 245, [
        "CMakeLists.txt",
        "set(SRC a.cpp b.cpp)",
        "add_executable(app ${SRC})",
    ], size=13.5, fill=INFO_FILL, stroke=NEG)
    frags.append(b2)

    frags.append(arrow(260, 298, 260, 345))
    frags.append(text(285, 324, "Генерація графу", size=12, color=MUTED, anchor="start"))

    b3, _, _ = textbox(260, 395, [
        "build.ninja (або Makefile)",
        "Правило для a.cpp.o",
        "Правило для b.cpp.o",
        "Лінкування app <- a.o b.o",
    ], size=13.5, pad=10)
    frags.append(b3)

    # Right Column: Rebuild phase when new file is added
    b4, _, _ = textbox(820, 110, [
        "Файлова система src/",
        "├── a.cpp",
        "├── b.cpp",
        "└── c.cpp   (новий файл!)",
    ], size=13.5, fill=OK_FILL, stroke=FIELD)
    frags.append(b4)

    frags.append(arrow(820, 160, 820, 210))
    frags.append(text(845, 185, "Запуск команди ninja", size=12, color=MUTED, anchor="start"))

    b5, _, _ = textbox(820, 275, [
        "build.ninja перевіряє часові мітки:",
        "• CMakeLists.txt НЕ змінено",
        "• Залежності від вмісту каталогу НЕМАЄ",
        "-> Повторна конфігурація НЕ викликається!",
    ], size=13.5, fill=WARN_FILL, stroke=POS)
    frags.append(b5)

    frags.append(arrow(820, 340, 820, 385))

    b6, _, _ = textbox(820, 420, [
        "Збірка виконує старий граф:",
        "c.cpp НЕ компілюється взагалі",
        "Помилка лінкера: undefined reference",
    ], size=13.5, fill=WARN_FILL, stroke=POS)
    frags.append(b6)

    # Bottom summary box
    frags.append(fitbox(60, 480, 960, 68,
                        "file(GLOB) обчислюється один раз під час конфігурації.\n"
                        "Генератор збірки (Ninja/Make) не відстежує появу нових файлів на диску,\n"
                        "якщо сам CMakeLists.txt не змінював мітку часу.", size=13.5))

    render(os.path.join(IMG, "glob-rebuild-blindness.svg"), W, H, *frags,
           title="Сліпота генератора збірки до нових файлів при використанні GLOB")


# ── 2. Забруднення простору каталогу проти інкапсуляції цілей ─────────────────
def fig_directory_pollution_vs_targets():
    W, H = 1080, 570
    frags = []

    frags.append(text(270, 48, "CMake 2.8: Глобальний стан каталогу", size=15, bold=True))
    frags.append(text(810, 48, "Modern CMake: Інкапсуляція цілей", size=15, bold=True))

    # Left: Directory pollution
    frags.append(rect(50, 75, 440, 370, fill=WARN_FILL, stroke=POS, sw=1.5))
    frags.append(text(270, 102, "Кореневий CMakeLists.txt", size=14, bold=True))
    frags.append(text(270, 126, "include_directories(/opt/crypto/include)", size=13, color=POS))
    frags.append(text(270, 146, "add_definitions(-DENABLE_OPENSSL)", size=13, color=POS))

    frags.append(arrow(270, 160, 270, 195))
    frags.append(text(270, 180, "add_subdirectory(lib) & (app) & (tests)", size=12, color=MUTED))

    # Subdirectories inheriting pollution
    b_sub1, _, _ = textbox(160, 245, [
        "src/lib",
        "Бачить /opt/crypto",
        "Бачить -DENABLE_OPENSSL",
    ], size=12.5)
    frags.append(b_sub1)

    b_sub2, _, _ = textbox(380, 245, [
        "tests/unit",
        "Випадково бачить чужі",
        "внутрішні заголовки!",
    ], size=12.5, fill="#fff3cd", stroke="#e67e22")
    frags.append(b_sub2)

    frags.append(fitbox(70, 320, 400, 105,
                        "Властивості каталогу протікають у всі підкаталоги:\n"
                        "• Неможливо розмежувати внутрішні та публічні заголовки\n"
                        "• Колізії імен файлів (наприклад, config.h або utils.h)\n"
                        "• Непотрібні прапорці дістаються юніт-тестам", size=12))

    # Right: Target encapsulation
    frags.append(rect(590, 75, 440, 370, fill=OK_FILL, stroke=FIELD, sw=1.5))
    frags.append(text(810, 102, "Ціль crypto_lib (add_library)", size=14, bold=True))

    b_target, _, _ = textbox(810, 175, [
        "Властивості цілі crypto_lib",
        "• PRIVATE: src/internal_aes.h",
        "• PUBLIC: include/crypto.h",
        "• INTERFACE: -DUSE_CRYPTO_API",
    ], size=12.5, fill=BG, stroke=FIELD)
    frags.append(b_target)

    frags.append(arrow(810, 240, 810, 280))
    frags.append(text(810, 260, "target_link_libraries(app PRIVATE crypto_lib)", size=12, color=FIELD, bold=True))

    b_consumer, _, _ = textbox(810, 345, [
        "Ціль app (add_executable)",
        "• Отримує ЛИШЕ PUBLIC та INTERFACE вимоги",
        "• Внутрішні шляхи src/lib ізольовані від app",
        "• Тести мають чистий контекст без витоків",
    ], size=12.5, fill=BG, stroke=LINE)
    frags.append(b_consumer)

    # Bottom summary box
    frags.append(fitbox(50, 465, 980, 68,
                        "Директиви каталогу діють за місцем у файловому дереві й забруднюють дочірні папки.\n"
                        "Цільові команди (target_*) прив'язують вимоги до конкретного артефакту й поширюють\n"
                        "виключно публічний інтерфейс через граф лінкування.", size=13.5))

    render(os.path.join(IMG, "directory-pollution-vs-targets.svg"), W, H, *frags,
           title="Забруднення простору каталогу проти інкапсуляції цілей")


# ── 3. Область видимості macro() проти function() ─────────────────────────────
def fig_macro_vs_function_scope():
    W, H = 1080, 560
    frags = []

    frags.append(text(270, 48, "macro(): Текстова підстановка без скоупу", size=15, bold=True))
    frags.append(text(810, 48, "function(): Ізольований фрейм стеку", size=15, bold=True))

    # Left: macro()
    frags.append(rect(50, 75, 440, 360, fill=WARN_FILL, stroke=POS, sw=1.5))

    frags.append(text(270, 105, "Виклик macro(add_plugin name)", size=13.5, bold=True))

    b_m1, _, _ = textbox(270, 175, [
        "Тіло макросу:",
        "set(TEMP_VAR \"plugin_${name}\")",
        "if(${name} STREQUAL \"auth\") ...",
    ], size=13, fill=BG, stroke=POS)
    frags.append(b_m1)

    frags.append(arrow(270, 230, 270, 275))
    frags.append(text(270, 255, "Прямий запис у пам'ять викликача", size=12, color=POS, bold=True))

    b_m2, _, _ = textbox(270, 345, [
        "Контекст викликача (батьківський скоуп):",
        "• TEMP_VAR викликача БЕЗПОВОРОТНО ПЕРЕЗАПИСАНО!",
        "• ${name} підставляється рядком до виконання if()",
        "• Складно налагоджувати неявні побічні ефекти",
    ], size=12, fill="#fff0ef", stroke=POS)
    frags.append(b_m2)

    # Right: function()
    frags.append(rect(590, 75, 440, 360, fill=OK_FILL, stroke=FIELD, sw=1.5))

    frags.append(text(810, 105, "Виклик function(add_plugin name)", size=13.5, bold=True))

    b_f1, _, _ = textbox(810, 175, [
        "Тіло функції (локальний скоуп):",
        "set(TEMP_VAR \"plugin_${name}\")",
        "set(OUT_RESULT \"ready\" PARENT_SCOPE)",
    ], size=13, fill=BG, stroke=FIELD)
    frags.append(b_f1)

    frags.append(arrow(810, 230, 810, 275))
    frags.append(text(810, 255, "Повернення лише через PARENT_SCOPE", size=12, color=FIELD, bold=True))

    b_f2, _, _ = textbox(810, 345, [
        "Контекст викликача (батьківський скоуп):",
        "• Локальні змінні функції (TEMP_VAR) ЗНИЩЕНО",
        "• Змінні викликача надійно захищені від колізій",
        "• OUT_RESULT передано явно й контрольовано",
    ], size=12, fill="#f0faf2", stroke=FIELD)
    frags.append(b_f2)

    # Bottom summary box
    frags.append(fitbox(50, 460, 980, 68,
                        "macro() розгортається безпосередньо у місці виклику й мутує змінні викликача.\n"
                        "function() створює ізольовану область видимості: змінні всередині залишаються локальними,\n"
                        "а повернення результатів вимагає явної директиви PARENT_SCOPE.", size=13.5))

    render(os.path.join(IMG, "macro-vs-function-scope.svg"), W, H, *frags,
           title="Порівняння областей видимості macro() та function()")


# ── 4. In-source збірка проти Out-of-source розділення ────────────────────────
def fig_in_source_vs_out_of_source():
    W, H = 1080, 560
    frags = []

    frags.append(text(270, 48, "Антипатерн: In-source збірка (cmake .)", size=15, bold=True))
    frags.append(text(810, 48, "Modern CMake: Out-of-source (cmake -B build)", size=15, bold=True))

    # Left: in-source build
    frags.append(rect(50, 75, 440, 360, fill=WARN_FILL, stroke=POS, sw=1.5))
    frags.append(text(270, 102, "Каталог сирців проєкту (src_dir/)", size=14, bold=True))

    b_in, _, _ = textbox(270, 205, [
        "├── CMakeLists.txt",
        "├── main.cpp, util.cpp, include/...",
        "├── CMakeCache.txt           [ЗГЕНЕРОВАНО]",
        "├── CMakeFiles/               [СМІТТЯ]",
        "├── Makefile / build.ninja    [АРТЕФАКТ]",
        "├── main.o, util.o           [ОБ'ЄКТНІ ФАЙЛИ]",
        "└── libengine.so             [БІНАРНИК]",
    ], size=12.5, fill=BG, stroke=POS)
    frags.append(b_in)

    frags.append(fitbox(65, 305, 410, 115,
                        "Наслідки in-source збірки:\n"
                        "• git status виводить десятки тимчасових файлів\n"
                        "• Неможливо паралельно тримати Debug та Release\n"
                        "• Повне очищення вимагає видалення невідстежуваних файлів\n"
                        "• Кеш CMakeCache.txt заважає повторній конфігурації", size=12))

    # Right: out-of-source build
    frags.append(rect(590, 75, 440, 360, fill=OK_FILL, stroke=FIELD, sw=1.5))
    frags.append(text(810, 102, "Повне розділення дерева сирців і бінарників", size=14, bold=True))

    b_out_src, _, _ = textbox(810, 175, [
        "Каталог сирців (лише вихідний код):",
        "├── CMakeLists.txt",
        "├── src/ (main.cpp, util.cpp)",
        "└── include/ (чистий репозиторій Git)",
    ], size=12.5, fill=BG, stroke=FIELD)
    frags.append(b_out_src)

    frags.append(arrow(810, 235, 810, 275))
    frags.append(text(810, 255, "cmake -B build/debug -DCMAKE_BUILD_TYPE=Debug", size=12, color=MUTED))

    b_out_bin, _, _ = textbox(810, 345, [
        "Каталоги збірки (build/debug/, build/release/):",
        "• Усі артефакти та CMakeCache ізольовані в build/",
        "• Очищення: rm -rf build/",
        "• Дерево сирців лишається недоторканим",
    ], size=12.5, fill=BG, stroke=FIELD)
    frags.append(b_out_bin)

    # Bottom summary box
    frags.append(fitbox(50, 460, 980, 68,
                        "Збирання всередині сирців засмічує дерево джерел генерованими файлами та руйнує робочу копію Git.\n"
                        "Modern CMake вимагає суворого out-of-source розділення через прапорець -B,\n"
                        "дозволяючи мати кілька незалежних конфігурацій збірки поруч.", size=13.5))

    render(os.path.join(IMG, "in-source-vs-out-of-source.svg"), W, H, *frags,
           title="In-source збірка проти Out-of-source розділення")


def main():
    fig_glob_rebuild_blindness()
    fig_directory_pollution_vs_targets()
    fig_macro_vs_function_scope()
    fig_in_source_vs_out_of_source()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
