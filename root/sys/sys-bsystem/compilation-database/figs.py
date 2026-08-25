# -*- coding: utf-8 -*-
"""Фігури до теми «База даних компіляції (compile_commands.json)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"
CLEAN = "#eaf7ef"
PANEL = "#f8fafc"


# ── 1. Роль бази компіляції як єдиного джерела правди ───────────────────────
def fig_compile_database_role():
    W, H = 1060, 580
    p = []

    # Ліва панель: Традиційний хаос (подвійне ведення)
    p.append(rect(40, 50, 460, 500, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(270, 80, "Традиційний підхід · паралельні конфігурації", size=15, bold=True, color=POS))

    p.append(fitbox(70, 110, 180, 60, "Система збірки\n(Makefile / Autotools)", size=13.5, fill=BG, stroke=LINE))
    p.append(fitbox(290, 110, 180, 60, "IDE / Аналізатор\n(Власні налаштування)", size=13.5, fill=BG, stroke=POS))

    p.append(arrow(160, 175, 160, 240, color=LINE, sw=1.8))
    p.append(arrow(380, 175, 380, 240, color=POS, sw=1.8))

    p.append(fitbox(70, 245, 180, 80, "Реальна компіляція:\n-I /opt/lib/include\n-DENABLE_FEATURE=1\n-std=c++20", size=12, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(290, 245, 180, 80, "Парсер IDE:\n(забули прапорець)\n-DENABLE_FEATURE=0\nдефолтний -std=c++14", size=12, fill=DIRTY, stroke=POS))

    p.append(fitbox(70, 360, 400, 75, "Наслідок розсинхронізації:\nКод успішно збирається компілятором,\nале в редакторі підкреслений червоним (хибні помилки)", size=13, fill=DIRTY, stroke=POS))
    p.append(fitbox(70, 455, 400, 70, "Подвійна робота:\nКожен новий прапорець чи шлях треба вручну\nдублювати у файли проєкту кожного інструмента", size=12.5, fill=BG, stroke=MUTED))

    # Права панель: Єдине джерело правди через compile_commands.json
    p.append(rect(540, 50, 480, 500, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(780, 80, "Єдине джерело правди · compile_commands.json", size=15, bold=True, color=FIELD))

    p.append(fitbox(570, 110, 420, 60, "Системи збірки (CMake, Meson, Ninja, Bear)\nЗнають повний граф і точні прапорці тулчейну", size=13.5, fill=BG, stroke=LINE))

    p.append(arrow(780, 170, 780, 230, color=FIELD, sw=2.2))
    p.append(text(795, 200, "експорт або перехоплення", size=12, color=FIELD, italic=True, anchor="start"))

    p.append(fitbox(610, 230, 340, 70, "compile_commands.json\nСтандартизований знімок викликів\n(directory, file, arguments)", size=13.5, fill=CLEAN, stroke=FIELD, bold=True))

    p.append(arrow(680, 300, 620, 360, color=FIELD, sw=1.8))
    p.append(arrow(780, 300, 780, 360, color=FIELD, sw=1.8))
    p.append(arrow(880, 300, 940, 360, color=FIELD, sw=1.8))

    p.append(fitbox(560, 365, 120, 60, "clangd / LSP\n(автодоповнення,\nнавігація)", size=12, fill=BG, stroke=LINE))
    p.append(fitbox(710, 365, 140, 60, "clang-tidy / Cppcheck\n(статичний\nаналіз)", size=12, fill=BG, stroke=LINE))
    p.append(fitbox(880, 365, 120, 60, "IWYU / CodeQL\n(рефакторинг,\nбезпека)", size=12, fill=BG, stroke=LINE))

    p.append(fitbox(570, 455, 420, 70, "Результат: Нульова розсинхронізація.\nІнструменти бачать одиницю трансляції з точністю 100%\nдо того, як її бачить справжній компілятор.", size=13, fill=CLEAN, stroke=FIELD))

    render(os.path.join(IMG, "compile-database-role.svg"), W, H, *p,
           title="Роль бази даних компіляції як єдиного джерела правди")


# ── 2. Анатомія запису compile_commands.json ────────────────────────────────
def fig_entry_anatomy():
    W, H = 1060, 520
    p = []

    # Загальний контейнер
    p.append(rect(40, 40, 980, 440, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(530, 70, "Структура запису CompileCommand у JSON-масиві", size=16, bold=True))

    # directory
    p.append(rect(70, 100, 920, 80, fill=BG, stroke=LINE, sw=1.5))
    p.append(textbox(170, 140, "directory", size=14, bold=True, fill=CLEAN, stroke=FIELD)[0])
    p.append(fitbox(260, 115, 710, 50,
                    "Робочий каталог запуску: абсолютний шлях (/home/user/proj/build).\nЯкір резолюції: відносні шляхи в -Iinclude та до джерел обчислюються саме звідси!",
                    size=13, fill=BG, stroke=MUTED))

    # file
    p.append(rect(70, 195, 920, 80, fill=BG, stroke=LINE, sw=1.5))
    p.append(textbox(170, 235, "file", size=14, bold=True, fill=CLEAN, stroke=FIELD)[0])
    p.append(fitbox(260, 210, 710, 50,
                    "Головна одиниця трансляції: шлях до сирцевого файлу (src/engine.cpp).\nЗаголовки (.h) сюди не входять — вони втягуються через #include під час парсингу.",
                    size=13, fill=BG, stroke=MUTED))

    # arguments проти command
    p.append(rect(70, 290, 920, 110, fill=BG, stroke=LINE, sw=1.5))
    p.append(textbox(170, 345, "arguments\n(або command)", size=13.5, bold=True, fill=CLEAN, stroke=FIELD)[0])

    p.append(fitbox(260, 305, 340, 80,
                    "arguments (масив токенів):\n[\"clang++\", \"-c\", \"-Iinclude\",\n \"-DFOO=\\\"bar baz\\\"\", \"src/engine.cpp\"]\n✓ Безпечно, без помилок shell-екранування",
                    size=12, fill=CLEAN, stroke=FIELD))

    p.append(fitbox(620, 305, 350, 80,
                    "command (єдиний сирий рядок):\n\"clang++ -c -Iinclude -DFOO=\\\"bar baz\\\"...\"\n✗ Небезпека: правила лапок і слешів\nвідрізняються між POSIX sh та Windows cmd",
                    size=12, fill=DIRTY, stroke=POS))

    # output
    p.append(rect(70, 415, 920, 50, fill=BG, stroke=MUTED, sw=1))
    p.append(text(170, 445, "output (опційно)", size=13, bold=True, color=MUTED))
    p.append(text(550, 445, "Цільовий об'єктний файл (наприклад, CMakeFiles/app.dir/src/engine.cpp.o)", size=12.5, color=MUTED))

    render(os.path.join(IMG, "entry-anatomy.svg"), W, H, *p,
           title="Анатомія полів запису compile_commands.json")


# ── 3. Два шляхи генерації: Декларативний та Перехоплювальний ──────────────
def fig_generator_vs_interceptor():
    W, H = 1060, 560
    p = []

    # Ліва колонка: Декларативний шлях (CMake / Ninja / Meson)
    p.append(rect(40, 50, 465, 470, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(272, 82, "1. Декларативний експорт (CMake / Meson / Ninja)", size=14.5, bold=True, color=FIELD))

    p.append(fitbox(70, 115, 405, 65, "Вхід: Опис структури проєкту\n(CMakeLists.txt / meson.build / build.ninja)", size=13, fill=BG, stroke=LINE))

    p.append(arrow(150, 180, 150, 235, color=FIELD, sw=2))
    p.append(text(165, 208, "CMAKE_EXPORT_COMPILE_COMMANDS=ON", size=11.5, color=FIELD, italic=True, anchor="start"))

    p.append(fitbox(70, 235, 405, 80, "Генератор збірки\nЗнає кожен target, його PRIVATE/PUBLIC\nвключення, прапорці мови та дефайни", size=13, fill=CLEAN, stroke=FIELD))

    p.append(arrow(150, 315, 150, 370, color=FIELD, sw=2))
    p.append(text(165, 343, "прямий запис на етапі генерації", size=11.5, color=FIELD, italic=True, anchor="start"))

    p.append(fitbox(70, 370, 405, 125, "Переваги:\n• Миттєво (не треба запускати збірку проєкту)\n• Точно відповідає налаштованій конфігурації\nОбмеження:\n• Потребує сумісної метасистеми (CMake + Ninja/Make)", size=12.5, fill=BG, stroke=MUTED))

    # Права колонка: Перехоплювальний шлях (Bear / scan-build)
    p.append(rect(555, 50, 465, 470, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(787, 82, "2. Перехоплення процесів (Bear / intercept-build)", size=14.5, bold=True, color=NEG))

    p.append(fitbox(585, 115, 405, 65, "Вхід: Довільна чорна скринька збірки\n(Спадковий Makefile, Autotools, bash-скрипт)", size=13, fill=BG, stroke=LINE))

    p.append(arrow(665, 180, 665, 235, color=NEG, sw=2))
    p.append(text(680, 208, "bear -- make -j8", size=12, color=NEG, italic=True, anchor="start"))

    p.append(fitbox(585, 235, 405, 80, "Механізм перехоплення (LD_PRELOAD / ptrace)\nОбгортає системні виклики execve() / posix_spawn().\nФільтрує виклики компіляторів (gcc, g++, clang)", size=12.5, fill=DIRTY, stroke=POS))

    p.append(arrow(665, 315, 665, 370, color=NEG, sw=2))
    p.append(text(680, 343, "дамп перехоплених argv + getcwd()", size=11.5, color=NEG, italic=True, anchor="start"))

    p.append(fitbox(585, 370, 405, 125, "Переваги:\n• Працює з будь-якою системою збірки без її модифікації\nОбмеження:\n• Потрібна повна чиста збірка (інкрементальна пропустить файли)\n• Залежить від прав доступу, SIP на macOS і ptrace", size=12.5, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "generator-vs-interceptor.svg"), W, H, *p,
           title="Два шляхи отримання бази: генерація проти перехоплення")


# ── 4. Ланцюжок обробки в clangd / LSP ─────────────────────────────────────
def fig_clangd_indexer_flow():
    W, H = 1060, 560
    p = []

    # Контейнер процесу
    p.append(rect(40, 40, 980, 480, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(530, 70, "Як мовний сервер (clangd) перетворює запис у семантичний індекс", size=15.5, bold=True))

    # Крок 1
    p.append(fitbox(70, 100, 260, 95, "1. Подія редактора\nКористувач відкриває\nsrc/math_utils.cpp\n(або include/math_utils.h)", size=13, fill=BG, stroke=LINE))

    p.append(arrow(335, 147, 385, 147, color=LINE, sw=2))

    # Крок 2
    p.append(fitbox(390, 100, 280, 95, "2. Пошук бази\nclangd сканує каталог файлу,\nпотім батьківські теки, теки build/,\nзнаходить compile_commands.json", size=12.5, fill=BG, stroke=LINE))

    p.append(arrow(675, 147, 725, 147, color=LINE, sw=2))

    # Крок 3
    p.append(fitbox(730, 100, 260, 95, "3. Резолюція прапорців\nВитягує точний запис.\nДля заголовків (.h) застосовує\nевристику файлу-близнюка", size=12.5, fill=CLEAN, stroke=FIELD))

    p.append(arrow(860, 200, 860, 250, color=FIELD, sw=2))

    # Крок 4
    p.append(fitbox(580, 255, 410, 105, "4. Ініціалізація Clang FrontendAction\nФормує екземпляр CompilerInstance із реальними:\n-I шляхами, -D макросами, -std стандартом,\nта системними include через --query-driver", size=12.5, fill=CLEAN, stroke=FIELD))

    p.append(arrow(575, 307, 485, 307, color=FIELD, sw=2))

    # Крок 5
    p.append(fitbox(70, 255, 410, 105, "5. Побудова AST та Індексу\nПовне розгортання макросів і шаблонів.\nВідстеження AST-вузлів, перехресних посилань,\nтипів та сигнатур функцій", size=12.5, fill=CLEAN, stroke=FIELD))

    p.append(arrow(275, 365, 275, 405, color=FIELD, sw=2))

    # Фінал: можливості
    p.append(rect(70, 410, 920, 85, fill=BG, stroke=FIELD, sw=1.8))
    p.append(text(530, 435, "Можливості LSP та інструментів розробки:", size=14, bold=True, color=FIELD))
    p.append(text(530, 465, "• Бездоганне автодоповнення   • Перехід до визначення (F12)   • clang-tidy перевірки   • Безпечний рефакторинг", size=13, color=INK))

    render(os.path.join(IMG, "clangd-indexer-flow.svg"), W, H, *p,
           title="Ланцюжок побудови AST та індексації в clangd")


if __name__ == "__main__":
    fig_compile_database_role()
    fig_entry_anatomy()
    fig_generator_vs_interceptor()
    fig_clangd_indexer_flow()
    print("Всі 4 фігури згенеровано успішно.")
