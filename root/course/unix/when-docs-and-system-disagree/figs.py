# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми when-docs-and-system-disagree."""

import os
import sys

# Шлях до scripts/ у корені репо (4 рівні вгору від root/course/unix/when-docs-and-system-disagree)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_docs_vs_reality_layers():
    """Фігура 1: Шість рівнів трансформації команди: від мануалу до системного виклику."""
    w, h = 840, 480
    frags = []

    frags.append(text(420, 24, "Шість рівнів трансформації команди: від мануалу до системного виклику", size=15, bold=True))

    layers = [
        {
            "num": "1",
            "title": "Онлайн-довідка / StackOverflow / AI",
            "desc": "Узагальнені припущення, застарілі версії, специфіка чужого дистрибутива (macOS vs Ubuntu vs Alpine).",
            "mismatch": "Очікування: синтаксис та прапорці GNU coreutils або конкретної версії OpenSSH",
            "color": "#8e44ad",
            "bg": "#faf5ff"
        },
        {
            "num": "2",
            "title": "Інтерпретація в оболонці (Shell Parsing)",
            "desc": "Аліаси (alias rm='rm -i'), функції оболонки, пріоритет вбудованих команд (builtin echo/kill/test).",
            "mismatch": "Аліас перекриває бінарник або вбудований echo ігнорує прапорець -e",
            "color": "#c0392b",
            "bg": "#fff5f5"
        },
        {
            "num": "3",
            "title": "Пошук файлу за змінною $PATH",
            "desc": "Порядок каталогів у PATH (/usr/local/bin перед /usr/bin), закешований хеш команд (hash -r).",
            "mismatch": "Запускається не той двійковий файл або кастомний скрипт перехоплює виклик",
            "color": "#d35400",
            "bg": "#fffaf0"
        },
        {
            "num": "4",
            "title": "Реалізація бінарника та версійні дефолти",
            "desc": "Різні гілки (GNU vs BSD vs BusyBox), версії (coreutils 8 vs 9: лапкування ls, copy-on-write у cp).",
            "mismatch": "Прапорці відсутні (grep -P) або формат виводу несумісний зі скриптом",
            "color": "#2457d6",
            "bg": "#f0f4ff"
        },
        {
            "num": "5",
            "title": "Оточення процесу, libc та локаль",
            "desc": "Змінні LC_COLLATE / LANG (вплив на sort і діапазони regex [a-z]), конфіги (/etc vs ~/.config).",
            "mismatch": "Несподіваний порядок сортування або підміна бібліотеки через LD_PRELOAD",
            "color": "#16a085",
            "bg": "#f0fdf4"
        },
        {
            "num": "6",
            "title": "Ядро та системні виклики (Системна істина)",
            "desc": "Перехоплення ядра: openat, stat, execve. Фізична взаємодія процесу з файловою системою.",
            "mismatch": "strace виявляє реальні прочитані файли та причини помилок (ENOENT, EACCES)",
            "color": "#27ae60",
            "bg": "#f4fbf7"
        }
    ]

    y_start = 48
    box_h = 62
    gap = 8

    for i, lv in enumerate(layers):
        y = y_start + i * (box_h + gap)
        frags.append(rect(20, y, 800, box_h, fill=lv["bg"], stroke=lv["color"], sw=1.5, rx=6))

        # Номер рівня
        frags.append(circle(48, y + 31, 15, fill=lv["color"], stroke=lv["color"], sw=1))
        frags.append(text(48, y + 36, lv["num"], size=13, color="#ffffff", bold=True))

        # Заголовок та опис
        frags.append(text(76, y + 22, lv["title"], size=12, color=INK, anchor="start", bold=True))
        frags.append(text(76, y + 40, lv["desc"], size=10, color=MUTED, anchor="start"))
        frags.append(text(76, y + 54, "→ " + lv["mismatch"], size=10, color=lv["color"], anchor="start", bold=True))

        if i < len(layers) - 1:
            # Стрілочка вниз
            frags.append(line(420, y + box_h, 420, y + box_h + gap, color=LINE, sw=1.5))

    render(os.path.join(OUT, "docs-vs-reality-layers.svg"), w, h, *frags)


def fig_shell_resolution_hierarchy():
    """Фігура 2: Ієрархія розв'язання імені команди в оболонці."""
    w, h = 840, 420
    frags = []

    frags.append(text(420, 24, "Ієрархія розв'язання імені команди в Unix-оболонці (POSIX / Bash)", size=15, bold=True))

    steps = [
        {
            "priority": "1. Спеціальні Builtins",
            "examples": "exec, eval, exit, export, set, trap, shift",
            "behavior": "Мають найвищий пріоритет. Виконуються безпосередньо рушієм оболонки. Помилка може перервати неінтерактивний скрипт.",
            "color": "#c0392b",
            "bg": "#fdf2f2"
        },
        {
            "priority": "2. Аліаси (Aliases)",
            "examples": "alias rm='rm -i', alias ls='ls --color=auto'",
            "behavior": "Текстова заміна першого токена в інтерактивному режимі. Перекривають будь-які однойменні функції та бінарники.",
            "color": "#d35400",
            "bg": "#fef7ee"
        },
        {
            "priority": "3. Функції оболонки (Shell Functions)",
            "examples": "function cd() { ... }, my_deploy() { ... }",
            "behavior": "Користувацькі блоки коду, завантажені в пам'ять сесії (~/.bashrc). Працюють перед регулярними built-in і PATH.",
            "color": "#8e44ad",
            "bg": "#faf5ff"
        },
        {
            "priority": "4. Звичайні Builtins",
            "examples": "cd, echo, pwd, kill, test, [, type, umask",
            "behavior": "Вбудовані утиліти для швидкої роботи без системного виклику fork/execve. Поведінка може різнитися від /usr/bin/<cmd>.",
            "color": "#2457d6",
            "bg": "#f0f4ff"
        },
        {
            "priority": "5. Виконувані файли в $PATH",
            "examples": "/usr/local/bin/..., /usr/bin/..., /bin/...",
            "behavior": "Послідовне сканування каталогів зліва направо у змінній $PATH. Результат кешується в таблиці hash оболонки.",
            "color": "#27ae60",
            "bg": "#f0fbf4"
        }
    ]

    y_start = 50
    box_h = 64
    gap = 10

    for i, st in enumerate(steps):
        y = y_start + i * (box_h + gap)
        frags.append(rect(20, y, 800, box_h, fill=st["bg"], stroke=st["color"], sw=1.5, rx=6))

        # Бейдж пріоритету
        frags.append(rect(32, y + 10, 220, 24, fill=st["color"], stroke=st["color"], sw=1, rx=4))
        frags.append(text(142, y + 26, st["priority"], size=11, color="#ffffff", bold=True))

        # Приклади
        frags.append(rect(32, y + 38, 220, 20, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
        frags.append(text(142, y + 52, st["examples"], size=9, color="#334155", bold=True))

        # Поведінка
        lines = [st["behavior"][:78], st["behavior"][78:]] if len(st["behavior"]) > 78 else [st["behavior"]]
        frags.append(text(270, y + 26, lines[0], size=11, color=INK, anchor="start"))
        if len(lines) > 1 and lines[1].strip():
            frags.append(text(270, y + 46, lines[1].strip(), size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "shell-resolution-hierarchy.svg"), w, h, *frags)


def fig_strace_ground_truth_pipeline():
    """Фігура 3: Перехоплення системних викликів утилітою strace."""
    w, h = 840, 390
    frags = []

    frags.append(text(420, 24, "Перехоплення системних викликів через strace: викриття реального стану", size=15, bold=True))

    # Схема з 3 основними блоками: Досліджуваний процес, Ядро/ptrace, Вивід strace
    # Блок 1: Простір користувача (Процес)
    frags.append(rect(20, 55, 230, 290, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(rect(20, 55, 230, 32, fill="#64748b", stroke="#64748b", sw=1, rx=6))
    frags.append(text(135, 76, "Простір користувача", size=12, color="#ffffff", bold=True))

    frags.append(textbox(135, 125, "Виконуваний файл\n/usr/bin/my-app", size=11, bold=True, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(textbox(135, 205, "Запит відкриття файлу:\nopenat(AT_FDCWD, \"app.conf\")", size=10, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(textbox(135, 290, "Читання конфігурації\nабо вихід з помилкою", size=10, fill="#ffffff", stroke="#94a3b8")[0])

    # Блок 2: Межа ядра та ptrace
    frags.append(rect(275, 55, 240, 290, fill="#fff5f5", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(rect(275, 55, 240, 32, fill="#c0392b", stroke="#c0392b", sw=1, rx=6))
    frags.append(text(395, 76, "Ядро Linux (Механізм ptrace)", size=12, color="#ffffff", bold=True))

    frags.append(textbox(395, 125, "1. Перехоплення входу:\nPTRACE_SYSCALL_ENTRY\n(зчитування аргументів)", size=10, fill="#ffffff", stroke="#c0392b")[0])
    frags.append(textbox(395, 205, "2. Реальне виконання VFS:\nПошук /etc/app.conf → ENOENT\nПошук ~/.config/... → OK", size=10, fill="#ffffff", stroke="#c0392b")[0])
    frags.append(textbox(395, 290, "3. Перехоплення виходу:\nPTRACE_SYSCALL_EXIT\n(перевірка коду return/errno)", size=10, fill="#ffffff", stroke="#c0392b")[0])

    # Блок 3: Журнал strace
    frags.append(rect(540, 55, 280, 290, fill="#f0fbf4", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(rect(540, 55, 280, 32, fill="#27ae60", stroke="#27ae60", sw=1, rx=6))
    frags.append(text(680, 76, "Фактичний журнал strace", size=12, color="#ffffff", bold=True))

    log_lines = [
        "execve(\"/usr/bin/my-app\", ...)",
        "openat(AT_FDCWD, \"/etc/app.conf\",",
        "       O_RDONLY) = -1 ENOENT",
        "openat(AT_FDCWD, \"/usr/share/app/def.conf\",",
        "       O_RDONLY) = 3",
        "fstat(3, {st_size=1024, ...}) = 0",
        "read(3, \"mode=fallback\\n\", 1024) = 14",
        "close(3) = 0"
    ]
    y_log = 110
    frags.append(rect(550, 95, 260, 235, fill="#1e293b", stroke="#0f172a", sw=1, rx=4))
    for line_text in log_lines:
        col = "#f87171" if "ENOENT" in line_text else ("#4ade80" if "= 3" in line_text or "fallback" in line_text else "#94a3b8")
        frags.append(text(558, y_log, line_text, size=9, color=col, anchor="start", bold=True))
        y_log += 26

    # Стрілки взаємодії
    frags.append(arrow(220, 205, 275, 205, color=LINE, sw=1.5))
    frags.append(arrow(515, 205, 545, 205, color=LINE, sw=1.5))

    render(os.path.join(OUT, "strace-ground-truth-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_docs_vs_reality_layers()
    fig_shell_resolution_hierarchy()
    fig_strace_ground_truth_pipeline()
    print("Усі SVG-фігури згенеровано успішно.")
