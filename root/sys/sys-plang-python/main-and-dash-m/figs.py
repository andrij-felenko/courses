# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми '__main__, -m і точка входу'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_main_module_lifecycle():
    """Порівняння стану модуля під час прямого запуску скрипту, запуску через -m та звичайного імпорту."""
    w, h = 980, 540
    frags = []

    frags.append(text(w / 2, 28, "Ініціалізація та стан простору імен: порівняння трьох режимів запуску", size=16, bold=True))

    modes = [
        ("Режим А: Прямий запуск скрипту", "python app/server.py", [
            "sys.path[0]: абсолютний шлях до каталогу app/",
            "sys.modules['__main__']: app/server.py",
            "__name__: '__main__'",
            "__package__: '' (порожній рядок або None)",
            "__spec__: None",
            "if __name__ == '__main__':  ==> TRUE",
            "Відносні імпорти (from . import): ПАДАЮТЬ (ImportError)"
        ], "#fdecea", POS),

        ("Режим Б: Запуск як модуль (-m)", "python -m app.server", [
            "sys.path[0]: поточний робочий каталог (cwd)",
            "sys.modules['__main__']: runpy.run_module('app.server')",
            "__name__: '__main__'",
            "__package__: 'app'",
            "__spec__.name: 'app.server'",
            "if __name__ == '__main__':  ==> TRUE",
            "Відносні імпорти (from . import): ПРАЦЮЮТЬ БЕЗДОГАННО"
        ], "#e8f8f0", FIELD),

        ("Режим В: Бібліотечний імпорт", "import app.server", [
            "sys.path[0]: не модифікується викликом",
            "sys.modules['app.server']: кешований об'єкт модуля",
            "__name__: 'app.server'",
            "__package__: 'app'",
            "__spec__.name: 'app.server'",
            "if __name__ == '__main__':  ==> FALSE",
            "Відносні імпорти (from . import): ПРАЦЮЮТЬ БЕЗДОГАННО"
        ], "#eaf0fd", NEG)
    ]

    card_w = 286
    card_h = 320
    x_gap = 36
    start_x = 35
    card_y = 65

    for i, (title, cmd, bullets, fill_c, stroke_c) in enumerate(modes):
        cx = start_x + i * (card_w + x_gap)
        frags.append(rect(cx, card_y, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, card_y + 24, title, size=13, bold=True, color=stroke_c))
        frags.append(rect(cx + 12, card_y + 36, card_w - 24, 26, fill=BG, stroke=stroke_c, sw=1.0, rx=4))
        frags.append(text(cx + card_w / 2, card_y + 53, cmd, size=11, bold=True, color=INK))

        for b_idx, bullet in enumerate(bullets):
            by = card_y + 82 + b_idx * 33
            frags.append(line(cx + 12, by - 6, cx + card_w - 12, by - 6, color="#d0d5dd", sw=0.8, dash="2,2"))
            is_good = "ПРАЦЮЮТЬ" in bullet or "TRUE" in bullet
            is_bad = "ПАДАЮТЬ" in bullet
            b_color = FIELD if is_good else (POS if is_bad else INK)
            b_bold = is_good or is_bad
            frags.append(text(cx + 14, by + 12, "• " + bullet, size=10, anchor="start", color=b_color, bold=b_bold))

    # Нижній блок підсумку
    bot_y = 410
    frags.append(rect(start_x, bot_y, w - 2 * start_x, 105, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(w / 2, bot_y + 24, "Ключовий висновок архітектури імпорту CPython", size=13, bold=True, color=INK))
    frags.append(text(w / 2, bot_y + 50, "Прапорець -m гарантує збереження ієрархії пакета в __spec__ та __package__, зберігаючи поведінку точки входу (__name__ == '__main__')", size=11, color=INK))
    frags.append(text(w / 2, bot_y + 74, "Прямий запуск файлу за шляхом ізолює скрипт від батьківського пакета і руйнує відносні імпорти", size=11, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "main-module-lifecycle.svg"), w, h, *frags)


def fig_zipapp_shebang_structure():
    """Фізична структура виконуваного zipapp-архіву та подвійне читання (ядро OS vs zipimport)."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Анатомія виконуваного файлу zipapp: подвійне парсування заголовків", size=16, bold=True))

    # Ліва колонка: структура файлу
    file_x = 50
    file_y = 65
    file_w = 320
    file_h = 420

    frags.append(rect(file_x, file_y, file_w, file_h, fill=FILL, stroke=LINE, sw=2.0, rx=8))
    frags.append(text(file_x + file_w / 2, file_y + 24, "Фізичний бінарний файл (.pyz)", size=13, bold=True))

    # Сегменти всередині файлу
    # 1. Shebang
    sh_y = file_y + 40
    sh_h = 48
    frags.append(rect(file_x + 10, sh_y, file_w - 20, sh_h, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(file_x + file_w / 2, sh_y + 20, "1. Unix Shebang Префікс", size=11, bold=True, color=POS))
    frags.append(text(file_x + file_w / 2, sh_y + 36, "#!/usr/bin/env python3\\n", size=10, bold=True, color=INK))

    # 2. ZIP Data
    zip_y = sh_y + sh_h + 12
    zip_h = 210
    frags.append(rect(file_x + 10, zip_y, file_w - 20, zip_h, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(file_x + file_w / 2, zip_y + 22, "2. Тіло ZIP-архіву (Local File Records)", size=11, bold=True, color=NEG))
    
    entries = [
        "__main__.py (байткод або вихідний текст)",
        "app/__init__.py",
        "app/core.py",
        "app/utils.py",
        "Стиснені дані DEFLATE / STORE"
    ]
    for idx, e in enumerate(entries):
        ey = zip_y + 45 + idx * 30
        frags.append(rect(file_x + 20, ey, file_w - 40, 24, fill=BG, stroke="#90b0e0", sw=1.0, rx=3))
        frags.append(text(file_x + file_w / 2, ey + 16, e, size=9.5, color=INK))

    # 3. EOCD / Central Directory
    eocd_y = zip_y + zip_h + 12
    eocd_h = 80
    frags.append(rect(file_x + 10, eocd_y, file_w - 20, eocd_h, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(file_x + file_w / 2, eocd_y + 20, "3. Central Directory & EOCD", size=11, bold=True, color=FIELD))
    frags.append(text(file_x + file_w / 2, eocd_y + 40, "Таблиця зміщень файлів у архіві", size=10, color=INK))
    frags.append(text(file_x + file_w / 2, eocd_y + 60, "Сигнатура EOCD: 0x06054b50 (кінець файлу)", size=9.5, bold=True, color=FIELD))

    # Права сторона: Способи інтерпретації
    # Блок 1: Ядро ОС
    os_x = 450
    os_y = 75
    os_w = 480
    os_h = 165
    frags.append(rect(os_x, os_y, os_w, os_h, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    frags.append(text(os_x + os_w / 2, os_y + 24, "А. Системний запуск ОС (execve -> POSIX Kernel)", size=13, bold=True, color=POS))
    frags.append(text(os_x + 20, os_y + 55, "1. Ядро ОС зчитує перші байти файлу з нульового зміщення (offset 0).", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, os_y + 80, "2. Виявляє магічні символи '#!' (Shebang) і парсить команду інтерпретатора.", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, os_y + 105, "3. Викликає /usr/bin/env python3, передаючи шлях до цього ж .pyz файлу в argv[1].", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, os_y + 135, "Результат: ОС запускає CPython, який починає парсити переданий архів.", size=11, anchor="start", color=POS, bold=True))

    frags.append(arrow(file_x + file_w, sh_y + sh_h / 2, os_x - 4, os_y + 40, color=POS, sw=2.0))

    # Блок 2: CPython zipimport
    py_y = 270
    py_h = 215
    frags.append(rect(os_x, py_y, os_w, py_h, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(os_x + os_w / 2, py_y + 24, "Б. Внутрішній імпортер CPython (модуль zipimport)", size=13, bold=True, color=FIELD))
    frags.append(text(os_x + 20, py_y + 55, "1. CPython додає шлях archive.pyz у sys.path[0].", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, py_y + 80, "2. zipimport відкриває файл і шукає EOCD з кінця файлу (seek(-22, SEEK_END)).", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, py_y + 105, "3. Шебанг на початку не заважає: зміщення рахуються від EOCD.", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, py_y + 130, "4. zipimport зчитує __main__.py безпосередньо з пам'яті (без розархівації).", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, py_y + 160, "5. runpy виконує байткод у контексті модуля __main__.", size=11, anchor="start", color=INK))
    frags.append(text(os_x + 20, py_y + 190, "Результат: Повна автономність виконання в одному переносимому файлі.", size=11, anchor="start", color=FIELD, bold=True))

    frags.append(arrow(file_x + file_w, eocd_y + 35, os_x - 4, py_y + 40, color=FIELD, sw=2.0))

    render(os.path.join(OUT_DIR, "zipapp-shebang-structure.svg"), w, h, *frags)


def fig_console_scripts_pipeline():
    """Конвеєр розгортання та виконання Console Scripts точок входу."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр Console Scripts: від декларації в pyproject.toml до виклику CLI", size=16, bold=True))

    steps = [
        ("1. pyproject.toml", [
            "[project.scripts]",
            'myapp = "myapp.cli:main"',
            "",
            "Декларація імені утиліти",
            "та шляху 'модуль:функція'"
        ], "#eaf0fd", NEG),

        ("2. pip install & Wheel", [
            "Розбір метаданих пакунка",
            "Запис у dist-info/entry_points.txt:",
            "[console_scripts]",
            "myapp = myapp.cli:main"
        ], "#fef9e7", "#b78103"),

        ("3. Генерація обгортки", [
            "Linux/macOS: бінарний скрипт",
            "#!/path/to/venv/bin/python",
            "Windows: myapp.exe launcher",
            "(вбудований C-код запуску)"
        ], "#fdecea", POS),

        ("4. Виконання в середовищі", [
            "sys.exit(main())",
            "Ізольований sys.executable",
            "Автоматичне налаштування",
            "sys.path для venv"
        ], "#e8f8f0", FIELD)
    ]

    card_w = 200
    card_h = 240
    x_gap = 45
    start_x = 35
    card_y = 65

    for i, (title, bullets, fill_c, stroke_c) in enumerate(steps):
        cx = start_x + i * (card_w + x_gap)
        frags.append(rect(cx, card_y, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(cx + card_w / 2, card_y + 24, title, size=12, bold=True, color=stroke_c))
        frags.append(line(cx + 8, card_y + 36, cx + card_w - 8, card_y + 36, color=stroke_c, sw=1.0))

        for b_idx, bullet in enumerate(bullets):
            by = card_y + 58 + b_idx * 28
            is_code = "[" in bullet or "=" in bullet or "#!" in bullet or "sys." in bullet
            f_size = 9.5 if is_code else 10
            f_bold = is_code
            frags.append(text(cx + 10, by, bullet, size=f_size, anchor="start", color=INK, bold=f_bold))

        if i < 3:
            ax1 = cx + card_w + 4
            ay1 = card_y + card_h / 2
            ax2 = cx + card_w + x_gap - 4
            ay2 = ay1
            frags.append(arrow(ax1, ay1, ax2, ay2, color=LINE, sw=1.8))

    # Нижній блок: детальний код згенерованої pip-обгортки
    wrap_y = 330
    wrap_h = 160
    frags.append(rect(start_x, wrap_y, w - 2 * start_x, wrap_h, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(w / 2, wrap_y + 24, "Вміст реального згенерованого скрипта-обгортки (venv/bin/myapp)", size=13, bold=True, color=INK))

    code_lines = [
        "#!/abs/path/to/virtualenv/bin/python3",
        "# -*- coding: utf-8 -*-",
        "import re",
        "import sys",
        "from myapp.cli import main",
        "if __name__ == '__main__':",
        "    sys.argv[0] = re.sub(r'(-script\\.pyw|\\.exe)?$', '', sys.argv[0])",
        "    sys.exit(main())"
    ]
    for idx, c_line in enumerate(code_lines):
        lx = start_x + 30
        ly = wrap_y + 48 + idx * 13
        frags.append(text(lx, ly, c_line, size=9.5, anchor="start", color=INK))

    render(os.path.join(OUT_DIR, "console-scripts-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_main_module_lifecycle()
    fig_zipapp_shebang_structure()
    fig_console_scripts_pipeline()
    print("Всі SVG-ілюстрації згенеровано успішно.")
