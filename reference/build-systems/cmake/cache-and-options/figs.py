# -*- coding: utf-8 -*-
"""Фігури до теми «Кеш CMake, опції та їхнє життя між прогонами»."""
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


# ── 1. Життєвий цикл кешу ───────────────────────────────────────────────────
def fig_lifecycle():
    W, H = 1040, 600
    frags = []
    frags.append(text(W / 2, 42, "Два шляхи виконання CMake: перший запуск проти повторного",
                      size=14, color=MUTED))

    # Ліва колонка: Перший прогін
    lx, col_w = 270, 440
    frags.append(fitbox(lx - col_w / 2, 70, col_w, 42, "ПЕРШИЙ ПРОГІН (порожній каталог збірки)",
                        size=13, bold=True, fill=INFO_FILL, stroke=NEG))
    
    p1 = [
        (130, 46, "1. Парсинг CLI: прапорці -D записуються в пам'ять"),
        (196, 52, "2. project() / toolchain: перевірки компілятора,\nважкі проби try_compile записуються в кеш"),
        (268, 52, "3. set(VAR default CACHE): створює новий запис,\nякщо прапорця -D не було в CLI"),
        (340, 46, "4. Генерація: створення build.ninja / Makefile"),
        (406, 52, "5. Серіалізація: збереження всіх змінних кешу\nу файл build/CMakeCache.txt на диску"),
    ]
    for y, h, s in p1:
        frags.append(fitbox(lx - col_w / 2, y, col_w, h, s, size=12.5))
    
    for y in [176, 248, 320, 386]:
        frags.append(arrow(lx, y, lx, y + 20))

    # Права колонка: Повторний прогін
    rx = 770
    frags.append(fitbox(rx - col_w / 2, 70, col_w, 42, "ПОВТОРНИЙ ПРОГІН (build/CMakeCache.txt існує)",
                        size=13, bold=True, fill=OK_FILL, stroke=FIELD))
    
    p2 = [
        (130, 46, "1. Зчитування build/CMakeCache.txt у пам'ять"),
        (196, 52, "2. project(): тести компілятора пропускаються,\nзначення беруться готовими з кешу"),
        (268, 52, "3. set(VAR default CACHE): ІГНОРУЄТЬСЯ,\nбо змінна вже присутня в кеші пам'яті"),
        (340, 46, "4. Генерація: створення оновлених правил збірки"),
        (406, 52, "5. Оновлення build/CMakeCache.txt (збереження\nнових та модифікованих значень)"),
    ]
    for y, h, s in p2:
        frags.append(fitbox(rx - col_w / 2, y, col_w, h, s, size=12.5))
    
    for y in [176, 248, 320, 386]:
        frags.append(arrow(rx, y, rx, y + 20))

    # Нижня плашка-висновок
    frags.append(fitbox(50, 480, 940, 68,
                        "Головний наслідок: зміна дефолтного значення у файлі CMakeLists.txt\n"
                        "не змінює значення у вже наявному кеші — потрібен явний -D або очищення (--fresh)",
                        size=13.5, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "lifecycle.svg"), W, H, *frags,
           title="Життєвий цикл кешу CMake")


# ── 2. Пошук змінної та затінення ───────────────────────────────────────────
def fig_lookup():
    W, H = 1000, 560
    cx, bw = 320, 360
    frags = []
    frags.append(text(140, 60, "Обчислення ${VAR} шукає значення згори вниз:",
                      size=13.5, color=MUTED, anchor="start"))

    steps = [
        (86, 60, "1. Область функції або блоку block()\n(стек викликів зсередини назовні)"),
        (192, 54, "2. Область поточного каталогу\n(локальні змінні CMakeLists.txt)"),
        (292, 54, "3. Кеш проєкту\n(глобальний CMakeCache.txt)"),
    ]
    for y, h, label in steps:
        frags.append(fitbox(cx - bw / 2, y, bw, h, label, size=13))
    
    frags.append(arrow(cx, 146, cx, 192))
    frags.append(arrow(cx, 246, cx, 292))
    frags.append(text(cx + bw / 2 + 16, 169, "якщо не знайдено", size=12, color=MUTED, anchor="start"))
    frags.append(text(cx + bw / 2 + 16, 269, "якщо не знайдено", size=12, color=MUTED, anchor="start"))

    rx, rw = 740, 360
    frags.append(fitbox(rx - rw / 2, 86, rw, 50, "$CACHE{VAR}", size=15, bold=True, fill=OK_FILL, stroke=FIELD))
    frags.append(arrow(rx - rw / 2, 111, cx + bw / 2 + 4, 319, color=FIELD))
    frags.append(text(rx, 162, "Прямий доступ до кешу в обхід локальних змінних", size=12, color=MUTED))

    frags.append(fitbox(rx - rw / 2, 192, rw, 50, "$ENV{VAR}", size=15, bold=True, fill=INFO_FILL, stroke=NEG))
    frags.append(fitbox(rx - rw / 2, 292, rw, 54, "Змінні середовища процесу (OS Environment)\nОкремий простір імен, не пов'язаний із ${VAR}", size=12))
    frags.append(arrow(rx, 242, rx, 292, color=NEG))

    frags.append(fitbox(50, 420, 900, 80,
                        "ЕФЕКТ ЗАТІНЕННЯ (SHADOWING):\n"
                        "Якщо у поточному CMakeLists.txt виконано set(VAR \"local\"), то звичайна змінна\n"
                        "перекриває кешовану VAR, і виклик ${VAR} повертає \"local\", ігноруючи значення з кешу.",
                        size=13, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "variable-lookup.svg"), W, H, *frags,
           title="Пошук змінної та затінення кешу")


# ── 3. CMakeDependentOption ─────────────────────────────────────────────────
def fig_dependent():
    W, H = 1000, 520
    frags = []
    frags.append(text(W / 2, 42, "Логіка роботи cmake_dependent_option(OPT doc default \"COND1;COND2\" force)",
                      size=13.5, color=MUTED))

    # Блок перевірки умови
    frags.append(fitbox(320, 80, 360, 56, "Обчислення умови COND:\nif(COND1 AND COND2)",
                        size=14, bold=True))
    
    frags.append(arrow(400, 136, 260, 200))
    frags.append(arrow(600, 136, 740, 200))
    frags.append(text(290, 160, "Умова ІСТИННА", size=13, color=FIELD, bold=True))
    frags.append(text(710, 160, "Умова ХИБНА", size=13, color=POS, bold=True))

    # Ліва гілка — Умова істинна
    frags.append(fitbox(60, 200, 400, 160,
                        "АКТИВНА ОПЦІЯ КЕШУ:\n\n"
                        "• Змінна реєструється як кешована BOOL\n"
                        "• Доступна для зміни в ccmake / cmake-gui\n"
                        "• Зчитує значення за замовчуванням default\n"
                        "• Користувач може передати -DOPT=ON/OFF",
                        size=13, fill=OK_FILL, stroke=FIELD))

    # Права гілка — Умова хибна
    frags.append(fitbox(540, 200, 400, 160,
                        "ПРИМУСОВЕ ЗНАЧЕННЯ:\n\n"
                        "• Змінній призначається force (зазвичай OFF)\n"
                        "• Опція ховається з інтерактивних GUI\n"
                        "• Попередньо збережене значення в кеші\n"
                        "  не впливає на поточну збірку",
                        size=13, fill=WARN_FILL, stroke=POS))

    frags.append(fitbox(60, 400, 880, 68,
                        "Призначення: захист графа конфігурації від взаємовиключних або нечинних комбінацій.\n"
                        "Користувач не може ввімкнути фічу, якщо в системі відсутні її обов'язкові залежності.",
                        size=13.5, bold=True))

    render(os.path.join(IMG, "dependent-option.svg"), W, H, *frags,
           title="Логіка роботи cmake_dependent_option")


# ── 4. Анатомія запису та GUI ───────────────────────────────────────────────
def fig_anatomy():
    W, H = 1040, 560
    frags = []
    frags.append(text(W / 2, 40, "Формат рядка CMakeCache.txt та його відображення в інструментах",
                      size=13.5, color=MUTED))

    # Схема рядка
    frags.append(fitbox(60, 70, 920, 64,
                        "// Описовий рядок документації (Help String)\n"
                        "CMAKE_BUILD_TYPE:STRING=Release",
                        size=14, bold=True, fill=INFO_FILL, stroke=NEG))

    parts = [
        (60, 170, 200, 90, "ІМ'Я ЗМІННОЇ\n\nCMAKE_BUILD_TYPE\nУнікальний ключ у кеші"),
        (280, 170, 200, 90, "ТИП ЗНАЧЕННЯ\n\nSTRING / BOOL /\nPATH / FILEPATH / INTERNAL"),
        (500, 170, 220, 90, "ЗНАЧЕННЯ\n\nRelease\nПоточний збережений стан"),
        (740, 170, 240, 90, "ВЛАСТИВОСТІ (PROPERTIES)\n\nADVANCED (прихована)\nSTRINGS (список вибору)"),
    ]
    for x, y, w, h, s in parts:
        frags.append(fitbox(x, y, w, h, s, size=12.5))

    # Відображення в GUI
    frags.append(fitbox(60, 290, 440, 120,
                        "ccmake / cmake-gui:\n\n"
                        "• BOOL → Прапорець (Checkbox / ON-OFF)\n"
                        "• PATH / FILEPATH → Діалог вибору каталогу чи файлу\n"
                        "• STRING + STRINGS → Випадаючий список (Combobox)",
                        size=13))

    frags.append(fitbox(540, 290, 440, 120,
                        "Фільтрація через ADVANCED:\n\n"
                        "• Звичайний режим: видно лише 5–10 опцій проєкту\n"
                        "• Режим «t» (ccmake) / Advanced (GUI): відкриває\n"
                        "  всі системні шляхи компілятора та прапорці",
                        size=13))

    frags.append(fitbox(60, 440, 920, 64,
                        "Змінні типу INTERNAL ніколи не показуються в GUI й слугують для збереження\n"
                        "результатів тестів try_compile, версій інструментів та внутрішнього стану CMake.",
                        size=13.5, bold=True))

    render(os.path.join(IMG, "cache-anatomy.svg"), W, H, *frags,
           title="Анатомія запису в CMakeCache.txt")


fig_lifecycle()
fig_lookup()
fig_dependent()
fig_anatomy()
print("ok")
