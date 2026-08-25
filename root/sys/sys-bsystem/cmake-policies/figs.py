# -*- coding: utf-8 -*-
"""Фігури до теми «Політики CMake: як мова змінюється, не ламаючи старі проєкти»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eafaf1"
INFO_FILL = "#eaf0fd"
MUTED_FILL = "#f8f9fa"


# ── 1. Життєвий цикл політики CMake ──────────────────────────────────────────
def fig_lifecycle():
    W, H = 1040, 560
    frags = []
    frags.append(text(W / 2, 40, "Життєвий цикл політики зворотньої сумісності (CMPxxxx)",
                      size=14, color=MUTED))

    # Чотири послідовні фази
    col_w = 215
    spacing = 30
    start_x = 40

    phases = [
        ("1. ВПРОВАДЖЕННЯ",
         "Реліз CMake X.Y\n\n"
         "• Політика з'являється у ядрі\n"
         "• Стан за замовчуванням: UNSET\n"
         "• Працює стара поведінка (OLD)\n"
         "• Виводиться авторське\n"
         "  попередження (dev warning)",
         INFO_FILL, NEG),
        
        ("2. АКТИВНИЙ СТАН",
         "Проєкт оновлює версію\n\n"
         "• cmake_minimum_required(X.Y)\n"
         "• Політика стає NEW\n"
         "• Активується нова поведінка\n"
         "• Попередження відсутні\n"
         "• Сучасний стандарт коду",
         OK_FILL, FIELD),

        ("3. ЗАСТАРІВАННЯ",
         "З плином версій (Deprecation)\n\n"
         "• Поведінка OLD визнається\n"
         "  застарілою й шкідливою\n"
         "• Явне встановлення OLD\n"
         "  генерує deprecation warning\n"
         "• Заклик оновити синтаксис",
         WARN_FILL, POS),

        ("4. ВИЛУЧЕННЯ",
         "Мажорний реліз (CMake 4.0+)\n\n"
         "• Підтримку OLD вилучено з коду\n"
         "• Запит OLD викликає\n"
         "  фатальну помилку конфігурації\n"
         "• Діє виключно стан NEW",
         MUTED_FILL, LINE)
    ]

    for i, (title_text, desc, fill_c, stroke_c) in enumerate(phases):
        x = start_x + i * (col_w + spacing)
        frags.append(fitbox(x, 75, col_w, 40, title_text, size=12.5, bold=True, fill=fill_c, stroke=stroke_c))
        frags.append(fitbox(x, 125, col_w, 240, desc, size=12, fill=FILL))
        if i < 3:
            frags.append(arrow(x + col_w + 4, 190, x + col_w + spacing - 4, 190, color=LINE, sw=1.8))

    # Нижній блок: Як керувати станами
    frags.append(fitbox(40, 390, 960, 120,
                        "КЕРУВАННЯ СТАНОМ ПОЛІТИК У КОДІ:\n\n"
                        "• cmake_minimum_required(VERSION 3.20) → встановлює всі політики до версії 3.20 у стан NEW\n"
                        "• cmake_policy(SET CMP0077 NEW) → точкове ввімкнення сучасної поведінки для конкретної політики\n"
                        "• cmake_policy(SET CMP0048 OLD) → тимчасове збереження старого режиму для сумісності з легасі-кодом",
                        size=12.5, bold=True, fill=INFO_FILL, stroke=NEG))

    render(os.path.join(IMG, "policy-lifecycle.svg"), W, H, *frags,
           title="Життєвий цикл політики CMake")


# ── 2. Стековий механізм та області видимості ─────────────────────────────────
def fig_stack():
    W, H = 1040, 600
    frags = []
    frags.append(text(W / 2, 40, "Ізоляція та успадкування стека політик у підпроєктах і модулях",
                      size=14, color=MUTED))

    # Ліва частина: Дерево каталогів add_subdirectory
    frags.append(fitbox(40, 75, 450, 42, "ІЄРАРХІЯ КАТАЛОГІВ (add_subdirectory)",
                        size=13, bold=True, fill=INFO_FILL, stroke=NEG))
    
    frags.append(fitbox(40, 130, 450, 150,
                        "Головний проєкт (кореневий CMakeLists.txt):\n\n"
                        "• cmake_minimum_required(VERSION 3.28)\n"
                        "• Стек політик: рівень 3.28 (усі сучасні NEW)\n"
                        "• add_subdirectory(subprojects/legacy_lib)",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(265, 280, 265, 330, color=FIELD))
    frags.append(text(275, 305, "створює копію стека", size=11.5, color=MUTED, anchor="start"))

    frags.append(fitbox(40, 330, 450, 160,
                        "Підпроєкт (legacy_lib/CMakeLists.txt):\n\n"
                        "• cmake_minimum_required(VERSION 3.0)\n"
                        "• Змінює рівень політик ЛОКАЛЬНО на 3.0\n"
                        "• По завершенні каталогу локальний стек видаляється\n"
                        "• Головний проєкт зберігає свій рівень 3.28",
                        size=12.5, fill=WARN_FILL, stroke=POS))

    # Права частина: Модулі include() та PUSH/POP
    frags.append(fitbox(530, 75, 470, 42, "МОДУЛІ ТА МАКРОСИ (include)",
                        size=13, bold=True, fill=INFO_FILL, stroke=NEG))

    frags.append(fitbox(530, 130, 470, 360,
                        "Безпечний модуль (cmake/FindCustomPackage.cmake):\n\n"
                        "cmake_policy(PUSH)                    # 1. Зберегти поточний стек\n"
                        "cmake_policy(SET CMP0054 NEW)         # 2. Локально виставити потрібні\n"
                        "cmake_policy(SET CMP0077 NEW)         #    налаштування політик\n\n"
                        "# ... тіло модуля, логіка пошуку, цілі ...\n\n"
                        "cmake_policy(POP)                     # 3. Відновити стек викликача\n\n"
                        "─────────────────────────────────────────\n"
                        "Сучасна альтернатива (CMake 3.25+):\n"
                        "block(SCOPE_FOR POLICIES)\n"
                        "  cmake_policy(SET CMP0144 NEW)\n"
                        "  find_package(OpenSSL REQUIRED)\n"
                        "endblock()  # Автоматичне відновлення політик",
                        size=12, fill=FILL, stroke=LINE))

    # Нижній висновок
    frags.append(fitbox(40, 515, 960, 60,
                        "Правило безпеки: include() виконується в поточному скоупі й може змінити політики викликача.\n"
                        "Кожен сторонній модуль або макрос зобов'язаний огортати зміну політик у пару PUSH/POP.",
                        size=12.5, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "policy-stack.svg"), W, H, *frags,
           title="Стековий механізм політик CMake")


# ── 3. Політика CMP0077: опції та нормальні змінні ───────────────────────────
def fig_cmp0077():
    W, H = 1040, 560
    frags = []
    frags.append(text(W / 2, 40, "Поведінка команди option() за політики CMP0077 (OLD проти NEW)",
                      size=14, color=MUTED))

    # Сценарій: Батьківський проєкт задає set(FOO_BUILD_TESTS OFF) і викликає add_subdirectory(foo)
    frags.append(fitbox(40, 70, 960, 60,
                        "Вхідна ситуація у головному CMakeLists.txt перед add_subdirectory(foo):\n"
                        "set(FOO_BUILD_TESTS OFF)   # Звичайна локальна змінна викликача",
                        size=13, bold=True, fill=INFO_FILL, stroke=NEG))

    col_w = 460
    lx = 40
    rx = 540

    # Ліва колонка: Стан OLD (CMake < 3.13)
    frags.append(fitbox(lx, 150, col_w, 40, "СТАН OLD: ігнорування звичайної змінної",
                        size=13, bold=True, fill=WARN_FILL, stroke=POS))

    frags.append(fitbox(lx, 200, col_w, 240,
                        "У підпроєкті foo/CMakeLists.txt:\n"
                        "option(FOO_BUILD_TESTS \"Build tests\" ON)\n\n"
                        "1. option() перевіряє тільки файл кешу CMakeCache.txt.\n"
                        "2. Звичайна змінна FOO_BUILD_TESTS = OFF ігнорується.\n"
                        "3. option() безумовно записує FOO_BUILD_TESTS = ON у кеш.\n\n"
                        "НАСЛІДОК: Тести підпроєкта збираються проти\n"
                        "бажання кореневого проєкту. Щоб вимкнути, доводилося\n"
                        "писати set(FOO_BUILD_TESTS OFF CACHE BOOL \"\" FORCE).",
                        size=12, fill=FILL))

    # Права колонка: Стан NEW (CMake 3.13+)
    frags.append(fitbox(rx, 150, col_w, 40, "СТАН NEW: повага до звичайної змінної",
                        size=13, bold=True, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(rx, 200, col_w, 240,
                        "У підпроєкті foo/CMakeLists.txt:\n"
                        "option(FOO_BUILD_TESTS \"Build tests\" ON)\n\n"
                        "1. option() спершу перевіряє, чи існує звичайна змінна.\n"
                        "2. Змінна FOO_BUILD_TESTS = OFF знайдена у скоупі.\n"
                        "3. option() нічого не записує в кеш і лишає OFF.\n\n"
                        "НАСЛІДОК: Чисте й передбачуване перевизначення\n"
                        "параметрів підпроєктів через FetchContent або\n"
                        "add_subdirectory без забруднення кешу!",
                        size=12, fill=FILL))

    # Висновок унизу
    frags.append(fitbox(40, 460, 960, 68,
                        "CMP0077 дозволяє кореневому проєкту прозоро конфігурувати сторонні залежності.\n"
                        "Це усуває потребу у небезпечному модифікаторі FORCE при взаємодії з опціями.",
                        size=13, bold=True, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "cmp0077-behavior.svg"), W, H, *frags,
           title="Поведінка option() за CMP0077")


# ── 4. Діапазон версій cmake_minimum_required ────────────────────────────────
def fig_version_range():
    W, H = 1040, 580
    frags = []
    frags.append(text(W / 2, 40, "Розгортання діапазону cmake_minimum_required(VERSION 3.15...3.30)",
                      size=14, color=MUTED))

    # Верхній опис
    frags.append(fitbox(40, 70, 960, 50,
                        "Декларація у проєкті: cmake_minimum_required(VERSION 3.15...3.30)",
                        size=13.5, bold=True, fill=INFO_FILL, stroke=NEG))

    cases = [
        ("Запуск на CMake 3.12",
         "3.12 < 3.15 (нижня межа)",
         "ФАТАЛЬНА ПОМИЛКА:\n"
         "CMake зупиняє роботу, оскільки інструмент\n"
         "старіший за мінімально підтримувану версію.",
         WARN_FILL, POS),

        ("Запуск на CMake 3.20",
         "3.15 <= 3.20 <= 3.30 (всередині)",
         "УСПІШНА КОНФІГУРАЦІЯ:\n"
         "Всі політики до CMake 3.20 включно стають NEW.\n"
         "Політики новіших версій (3.21+) відсутні у бінарнику.",
         OK_FILL, FIELD),

        ("Запуск на CMake 3.30",
         "3.30 = 3.30 (верхня межа)",
         "МАКСИМАЛЬНИЙ НАБІР ПОЛІТИК:\n"
         "Всі політики до CMake 3.30 включно стають NEW.\n"
         "Проєкт повністю протестований під цю версію.",
         OK_FILL, FIELD),

        ("Запуск на CMake 3.35",
         "3.35 > 3.30 (вище верхньої межі)",
         "ЗАХИСТ ВІД НЕОЧІКУВАНИХ ЗМІН:\n"
         "Політики до 3.30 стають NEW. Політики версій\n"
         "3.31...3.35 залишаються UNSET / OLD, захищаючи\n"
         "проєкт від неперевірених змін поведінки!",
         INFO_FILL, NEG)
    ]

    col_w = 215
    spacing = 30
    start_x = 40

    for i, (head, cond, desc, fill_c, stroke_c) in enumerate(cases):
        x = start_x + i * (col_w + spacing)
        frags.append(fitbox(x, 140, col_w, 42, head, size=12.5, bold=True, fill=fill_c, stroke=stroke_c))
        frags.append(fitbox(x, 192, col_w, 36, cond, size=11.5, bold=True, fill=FILL))
        frags.append(fitbox(x, 238, col_w, 190, desc, size=11.5, fill=FILL))

    # Нижній блок
    frags.append(fitbox(40, 450, 960, 90,
                        "ЧОМУ ДІАПАЗОН ВЕРСІЙ КРАЩИЙ ЗА ОДНУ ФІКСОВАНУ ВЕРСІЮ:\n\n"
                        "1. Дозволяє розробникам з новими версіями CMake користуватися найсучаснішими оптимізаціями та політиками.\n"
                        "2. Не вимагає від користувачів зі старішими дистрибутивами (наприклад, Ubuntu LTS) оновлювати CMake вище 3.15.\n"
                        "3. Обмежує набір активних політик верхньою межею (3.30), гарантуючи стабільність на майбутніх релізах CMake.",
                        size=12.5, bold=True, fill=MUTED_FILL, stroke=LINE))

    render(os.path.join(IMG, "version-range-matrix.svg"), W, H, *frags,
           title="Діапазон версій у cmake_minimum_required")


fig_lifecycle()
fig_stack()
fig_cmp0077()
fig_version_range()
print("All figures generated successfully.")
