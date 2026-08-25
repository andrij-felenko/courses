# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми manual-pages-and-help."""

import os
import sys

# Шлях до scripts/ у корені репо (4 рівні вгору від root/sys/sys-unix/manual-pages-and-help)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_terminal_help_levels():
    """Фігура 1: Чотири рівні довідки в терміналі."""
    w, h = 820, 360
    frags = []

    # Заголовок
    frags.append(text(410, 24, "Рівні довідкової системи в терміналі Unix / Linux", size=16, bold=True))

    # 4 колонки для рівнів
    levels = [
        {
            "x": 15, "w": 185,
            "title": "1. Shell Builtin",
            "cmd": "help <cmd> / type",
            "src": "Пам'ять процесу оболонки",
            "speed": "< 1 мс (миттєво)",
            "scope": "Вбудовані команди (cd, read, eval)",
            "color": "#2457d6",
            "bg": "#f0f4ff"
        },
        {
            "x": 215, "w": 185,
            "title": "2. Прапорець утиліти",
            "cmd": "<cmd> --help / -h",
            "src": "Сам бінарник (compiled-in)",
            "speed": "2–10 мс (запуск процесу)",
            "scope": "Шпаргалка опцій та синтаксису",
            "color": "#27ae60",
            "bg": "#f0fbf4"
        },
        {
            "x": 415, "w": 185,
            "title": "3. Сторінка man",
            "cmd": "man [1-8] <topic>",
            "src": "/usr/share/man (groff/gz)",
            "speed": "20–50 мс (pager, mandb)",
            "scope": "Повна специфікація, API, errno",
            "color": "#c0392b",
            "bg": "#fdf2f0"
        },
        {
            "x": 615, "w": 190,
            "title": "4. Дерево info",
            "cmd": "info <program>",
            "src": "/usr/share/info (Texinfo)",
            "speed": "30–70 мс (TUI-навігатор)",
            "scope": "Гіпертекстові книги та підручники",
            "color": "#8e44ad",
            "bg": "#fbf4ff"
        }
    ]

    for lv in levels:
        x, box_w = lv["x"], lv["w"]
        # Зовнішній контейнер
        frags.append(rect(x, 50, box_w, 280, fill=lv["bg"], stroke=lv["color"], sw=1.5, rx=8))
        # Шапка картки
        frags.append(rect(x, 50, box_w, 36, fill=lv["color"], stroke=lv["color"], sw=1, rx=6))
        frags.append(text(x + box_w / 2, 73, lv["title"], size=13, color="#ffffff", bold=True))

        # Виклик / команда
        frags.append(rect(x + 10, 96, box_w - 20, 26, fill="#ffffff", stroke="#cccccc", sw=1, rx=4))
        frags.append(text(x + box_w / 2, 113, lv["cmd"], size=11, color="#111111", bold=True))

        # Деталі
        y_cursor = 145
        frags.append(text(x + 12, y_cursor, "Джерело даних:", size=11, color=MUTED, anchor="start", bold=True))
        frags.append(text(x + 12, y_cursor + 16, lv["src"], size=10, color=INK, anchor="start"))

        y_cursor += 45
        frags.append(text(x + 12, y_cursor, "Час відповіді:", size=11, color=MUTED, anchor="start", bold=True))
        frags.append(text(x + 12, y_cursor + 16, lv["speed"], size=10, color=INK, anchor="start"))

        y_cursor += 45
        frags.append(text(x + 12, y_cursor, "Призначення:", size=11, color=MUTED, anchor="start", bold=True))
        # розбиваємо scope на два рядки якщо треба
        scope_words = lv["scope"].split(" ")
        mid = len(scope_words) // 2
        line1 = " ".join(scope_words[:mid])
        line2 = " ".join(scope_words[mid:])
        frags.append(text(x + 12, y_cursor + 16, line1, size=10, color=INK, anchor="start"))
        frags.append(text(x + 12, y_cursor + 30, line2, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "terminal-help-levels.svg"), w, h, *frags)


def fig_cli_syntax_styles():
    """Фігура 2: Порівняння стилів розбору аргументів командного рядка."""
    w, h = 820, 390
    frags = []

    frags.append(text(410, 24, "Стилі прапорців CLI та правила розбору аргументів", size=16, bold=True))

    styles = [
        {
            "y": 50,
            "name": "POSIX / UNIX (getopt)",
            "example": "tar -x -v -f arch.tar  або  tar -xvf arch.tar",
            "rule": "Однолітерні опції з одним дефісом. Прапорці групуються (-xvf). Опція з аргументом забирає наступний токен або злитий суфікс (-f file або -ffile).",
            "badge": "Стандарт POSIX",
            "bcolor": "#2457d6"
        },
        {
            "y": 130,
            "name": "GNU Long Options (getopt_long)",
            "example": "grep --ignore-case --color=always --max-count 5",
            "rule": "Подвійний дефіс (--), повні описові слова. Аргументи через = або окремим токеном (--file=X або --file X). Підтримка однозначних префіксів.",
            "badge": "Де-факто стандарт Linux",
            "bcolor": "#27ae60"
        },
        {
            "y": 210,
            "name": "BSD Style & Legacy UNIX",
            "example": "ps aux    та    tar xzf archive.tgz",
            "rule": "Опції без початкового дефіса (історичний спадок V7 / BSD). Не плутати з 'ps -a -u -x' (у POSIX це інший набір процесів).",
            "badge": "Історичний виняток",
            "bcolor": "#d35400"
        },
        {
            "y": 290,
            "name": "Розділювач позиційних операндів «--»",
            "example": "rm -- -rf    та    grep --pattern -- -file.txt",
            "rule": "Маркер '--' наказує парсеру негайно зупинити обробку прапорців: усі наступні аргументи вважаються суто шляхами або іменами файлів.",
            "badge": "Захист від ін'єкцій",
            "bcolor": "#c0392b"
        }
    ]

    for st in styles:
        y = st["y"]
        # Головна рамка
        frags.append(rect(15, y, 790, 72, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))

        # Заголовок стилю та бейдж
        frags.append(text(28, y + 20, st["name"], size=13, color=INK, anchor="start", bold=True))
        badge_w = text_width(st["badge"], size=10, bold=True) + 14
        frags.append(rect(790 - badge_w - 5, y + 8, badge_w, 20, fill=st["bcolor"], stroke=st["bcolor"], sw=1, rx=4))
        frags.append(text(790 - badge_w / 2 - 5, y + 22, st["badge"], size=10, color="#ffffff", bold=True))

        # Приклад у моноширинному блоці
        frags.append(rect(28, y + 28, 300, 22, fill="#ffffff", stroke="#94a3b8", sw=1, rx=3))
        frags.append(text(35, y + 43, st["example"], size=10, color="#0f172a", anchor="start", bold=True))

        # Правило
        frags.append(text(340, y + 43, st["rule"][:70], size=10, color="#334155", anchor="start"))
        frags.append(text(340, y + 58, st["rule"][70:], size=10, color="#334155", anchor="start"))

    render(os.path.join(OUT, "cli-syntax-styles.svg"), w, h, *frags)


def fig_man_sections_map():
    """Фігура 3: Карта числових розділів man (1..8) та їхнє призначення."""
    w, h = 820, 370
    frags = []

    frags.append(text(410, 24, "Структура 8 числових розділів керівництва (man pages)", size=16, bold=True))

    sections = [
        ("1", "Команди користувача", "ls, grep, tar, bash, gcc", "#2457d6"),
        ("2", "Системні виклики ядра", "open(), fork(), epoll_create()", "#c0392b"),
        ("3", "Бібліотечні функції C", "printf(), malloc(), pthread_create()", "#27ae60"),
        ("4", "Спеціальні файли пристроїв", "/dev/null, /dev/tty, /dev/sda", "#8e44ad"),
        ("5", "Формати файлів і конфіги", "/etc/passwd, /etc/fstab, crontab", "#d35400"),
        ("6", "Ігри та заставки", "bsd-games, fortune, tetris", "#7f8c8d"),
        ("7", "Оглядові статті та протоколи", "man 7 ip, man 7 socket, man 7 signal", "#16a085"),
        ("8", "Адміністрування системи", "mount, iptables, systemd, fsck", "#2c3e50"),
    ]

    for i, (sec_num, title, examples, col) in enumerate(sections):
        col_idx = i % 2
        row_idx = i // 2
        x = 15 + col_idx * 400
        y = 50 + row_idx * 75

        # Рамка секції
        frags.append(rect(x, y, 390, 65, fill="#fdfdfd", stroke="#d1d5db", sw=1.5, rx=6))

        # Кружечок із номером розділу
        frags.append(circle(x + 30, y + 32, 18, fill=col, stroke=col, sw=1))
        frags.append(text(x + 30, y + 38, sec_num, size=15, color="#ffffff", bold=True))

        # Текст
        frags.append(text(x + 60, y + 26, title, size=12, color=INK, anchor="start", bold=True))
        frags.append(text(x + 60, y + 46, "Приклади: " + examples, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "man-sections-map.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_terminal_help_levels()
    fig_cli_syntax_styles()
    fig_man_sections_map()
    print("Всі SVG-фігури згенеровано успішно.")
