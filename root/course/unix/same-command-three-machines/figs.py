# -*- coding: utf-8 -*-
import sys, os

# Path to scripts for svgkit (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Три екосистеми простору користувача ──────────────────────────────
def fig_unix_command_three_ecosystems():
    W, H = 940, 540
    p = []

    # Заголовок
    p.append(fitbox(20, 16, W - 40, 36, "Три екосистеми Unix-утиліт: коріння, механіка та поведінка",
                    size=16, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    cols = [
        (40.0, 70.0, 270.0, 400.0, "GNU Coreutils\n(GNU/Linux / Ubuntu / RHEL)",
         ["• Бібліотека: glibc",
          "• Парсер: getopt_long з пермутацією",
          "• Довгі опції (--long-options)",
          "• Розширені можливості (PCRE, gensub)",
          "• sed -i: опціональний суфікс (-i.bak)",
          "• date -d: природний парсер дат",
          "• ps: підтримує і -ef, і aux",
          "• grep -P: підтримка регулярних виразів PCRE",
          "• Орієнтація: комфорт користувача"],
         "#eaf0fd", NEG),

        (335.0, 70.0, 270.0, 400.0, "BSD Userland\n(FreeBSD / macOS Darwin)",
         ["• Бібліотека: BSD libc",
          "• Парсер: класичний POSIX getopt",
          "• Переважно короткі однолітерні опції",
          "• Суворий зв'язок із монолітним деревом ОС",
          "• sed -i: обов'язковий суфікс ('' для пустки)",
          "• date -v / date -r: відносні зсуви часу",
          "• ps: синтаксис aux без дефіса",
          "• grep: лише BRE / ERE (без -P у базі)",
          "• Орієнтація: стабільність інтерфейсу"],
         "#eef7f0", FIELD),

        (630.0, 70.0, 270.0, 400.0, "BusyBox\n(Alpine / OpenWrt / Embedded)",
         ["• Бібліотека: musl / uClibc / dietlibc",
          "• Парсер: внутрішній комбайн getopt32",
          "• Багатоцільовий бінарник (multi-call 1-2 МБ)",
          "• Урізані прапорці заради розміру коду",
          "• sed -i: спрощена поведінка",
          "• date: лише поточний час або -d @epoch",
          "• ps: мінімалістичний вивід (без aux)",
          "• grep: базова фільтрація (без PCRE)",
          "• Орієнтація: мінімальний розмір у Flash"],
         "#fdf0dc", "#e08a1e"),
    ]

    for x, y, w, h, title, items, fill_col, border_col in cols:
        p.append(rect(x, y, w, h, fill="#ffffff", stroke=border_col, sw=1.8, rx=8))
        p.append(fitbox(x + 8, y + 8, w - 16, 46, title, size=12.5, bold=True,
                        fill=fill_col, stroke=border_col, color=INK))
        iy = y + 68
        for it in items:
            p.append(text(x + 14, iy, it, size=11, color=INK, anchor="start"))
            iy += 35

    # Підсумок унизу
    p.append(fitbox(20, 484, W - 40, 36,
                    "POSIX є мінімальним спільним знаменником, але кожна екосистема додає власні розширення",
                    size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "unix-command-three-ecosystems.svg"), W, H, *p,
           title="Три екосистеми Unix-утиліт")


# ── Фіг. 2: Механіка парсингу аргументів: POSIX vs GNU ───────────────────────
def fig_getopt_permutation_vs_posix():
    W, H = 940, 500
    p = []

    p.append(fitbox(20, 16, W - 40, 36, "Парсинг аргументів: зупинка за POSIX проти пермутації у GNU",
                    size=15, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    # Вихідний командний рядок
    p.append(rect(40, 66, W - 80, 50, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=8))
    p.append(text(W / 2, 88, "Команда із перемішаними прапорцями та аргументами:", size=11, color=MUTED))
    p.append(text(W / 2, 106, "grep   \"error\"   -i   -n   /var/log/syslog", size=13, bold=True, color=INK))

    # Лівий блок: Стандартний POSIX getopt()
    p.append(rect(40, 130, 410, 275, fill="#ffffff", stroke=FIELD, sw=1.6, rx=8))
    p.append(fitbox(55, 142, 380, 30, "Стандартний POSIX getopt() (BSD / macOS / POSIXLY_CORRECT)",
                    size=11.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    posix_steps = [
        ("1. Токен 'grep':", "назва програми (argv[0])"),
        ("2. Токен 'error':", "перший позиційний аргумент (шаблон)"),
        ("3. Зупинка сканування:", "getopt() зупиняється на першому не-прапорці!"),
        ("4. Токени '-i', '-n':", "інтерпретуються як імена файлів, а не прапорці!"),
        ("5. Результат:", "пошук 'error' у файлах '-i', '-n' та '/var/log/syslog'"),
    ]
    py = 185
    for st, sd in posix_steps:
        p.append(text(65, py, st, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(210, py, sd, size=10.5, color=POS if "не прапорці" in sd or "файлах '-i'" in sd else INK, anchor="start"))
        py += 40

    # Правий блок: GNU getopt_long() з пермутацією
    p.append(rect(490, 130, 410, 275, fill="#ffffff", stroke=NEG, sw=1.6, rx=8))
    p.append(fitbox(505, 142, 380, 30, "GNU getopt_long() за замовчуванням (GNU/Linux / glibc)",
                    size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, color=INK))

    gnu_steps = [
        ("1. Токен 'grep':", "назва програми (argv[0])"),
        ("2. Токен 'error':", "відкладено у внутрішній список аргументів"),
        ("3. Пермутація argv:", "сканує рядок до кінця, витягуючи всі прапорці"),
        ("4. Прапорці '-i', '-n':", "успішно активують ігнорування регістру й нумерацію"),
        ("5. Результат:", "виконується: grep -i -n \"error\" /var/log/syslog"),
    ]
    gy = 185
    for st, sd in gnu_steps:
        p.append(text(515, gy, st, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(660, gy, sd, size=10.5, color=FIELD if "успішно" in sd or "виконується" in sd else INK, anchor="start"))
        gy += 40

    # Стрілка різниці
    p.append(arrow(450, 260, 490, 260, color="#e08a1e", sw=2))

    # Нижня плашка
    p.append(fitbox(40, 420, W - 80, 60,
                    "Практичний висновок: за стандартом POSIX усі прапорці обов'язково мають передувати позиційним аргументам.\nЯкщо поставити аргумент перед прапорцем на macOS чи BSD, скрипт зламається.",
                    size=11.5, bold=False, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "getopt-permutation-vs-posix.svg"), W, H, *p,
           title="Парсинг аргументів POSIX vs GNU")


# ── Фіг. 3: Анатомія розбіжності sed -i ───────────────────────────────────────
def fig_sed_inplace_divergence():
    W, H = 940, 490
    p = []

    p.append(fitbox(20, 16, W - 40, 36, "Анатомія розбіжності sed -i: чому той самий рядок падає на macOS",
                    size=15, bold=True, fill="#eef2f8", stroke=NEG, color=INK))

    # Вихідна команда
    p.append(rect(40, 66, W - 80, 44, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=6))
    p.append(text(W / 2, 84, "Виклик у скрипті:", size=11, color=MUTED))
    p.append(text(W / 2, 100, "sed  -i  's/old/new/g'  config.txt", size=13, bold=True, color=INK))

    # Ліва колонка: GNU sed
    p.append(rect(40, 124, 410, 260, fill="#ffffff", stroke=FIELD, sw=1.6, rx=8))
    p.append(fitbox(55, 136, 380, 28, "GNU sed (Linux / Ubuntu / glibc)",
                    size=12, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))

    gnu_items = [
        ("Специфікація опції:", "\"i::\" (суфікс є ОПЦІОНАЛЬНИМ)"),
        ("Обробка '-i':", "аргумент не приклеєний -> бекап НЕ потрібен"),
        ("Наступний токен:", "'s/old/new/g' розпізнано як скрипт sed"),
        ("Файл для обробки:", "config.txt модифікується на місці"),
        ("Статус виконання:", "УСПІХ (файл відредаговано)"),
    ]
    gy = 180
    for k, v in gnu_items:
        p.append(text(55, gy, k, size=11, bold=True, color=INK, anchor="start"))
        col = FIELD if "УСПІХ" in v else INK
        p.append(text(210, gy, v, size=10.5, color=col, bold=("УСПІХ" in v), anchor="start"))
        gy += 38

    # Права колонка: BSD sed
    p.append(rect(490, 124, 410, 260, fill="#ffffff", stroke=POS, sw=1.6, rx=8))
    p.append(fitbox(505, 136, 380, 28, "BSD sed (macOS / FreeBSD / Darwin)",
                    size=12, bold=True, fill="#fdecea", stroke=POS, color=POS))

    bsd_items = [
        ("Специфікація опції:", "\"i:\" (суфікс є ОБОВ'ЯЗКОВИМ)"),
        ("Обробка '-i':", "захоплює наступний токен як розширення!"),
        ("Суфікс бекапу:", "створює копію config.txts/old/new/g"),
        ("Команда sed:", "'config.txt' парситься як вираз sed"),
        ("Статус виконання:", "ПОМИЛКА: undefined label 'onfig.txt'"),
    ]
    by = 180
    for k, v in bsd_items:
        p.append(text(505, by, k, size=11, bold=True, color=INK, anchor="start"))
        col = POS if "ПОМИЛКА" in v else INK
        p.append(text(660, by, v, size=10.5, color=col, bold=("ПОМИЛКА" in v), anchor="start"))
        by += 38

    # Нижня панель із переносним рішенням
    p.append(rect(40, 396, W - 80, 76, fill="#fbfdff", stroke="#aab4c0", sw=1.5, rx=8))
    p.append(fitbox(55, 404, W - 110, 22, "Портативні рішення без ризику падіння на іншій ОС",
                    size=11.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))
    p.append(text(W / 2, 442, "1) Тимчасовий файл:  sed 's/old/new/g' config.txt > config.tmp && mv config.tmp config.txt",
                  size=11, color=INK))
    p.append(text(W / 2, 460, "2) Явний суфікс для sed:  sed -i.bak 's/old/new/g' config.txt && rm config.txt.bak",
                  size=11, color=INK))

    render(os.path.join(OUT, "sed-inplace-divergence.svg"), W, H, *p,
           title="Анатомія розбіжності sed -i")


if __name__ == "__main__":
    fig_unix_command_three_ecosystems()
    fig_getopt_permutation_vs_posix()
    fig_sed_inplace_divergence()
    print("OK figs")
