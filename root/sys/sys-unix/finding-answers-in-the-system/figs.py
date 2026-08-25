# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM_BORDER = "#d48806"
PURPLE_FILL = "#f3e8ff"
PURPLE_BORDER = "#7e22ce"


# ── 1. Ієрархія та площини системного стану ──────────────────────────────────
def fig_truth_planes():
    W, H = 1000, 620
    p = []

    p.append(fitbox(40, 20, 920, 50,
                    "Ієрархія та площини системного стану в Unix / Linux:\n"
                    "від статичного задуму постачальника до живого стану пам'яті та подій",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    layers = [
        ("1. Статичний канон дистрибутива",
         "/usr/share/man, /usr/share/doc, /usr/lib/systemd, /usr/lib/sysctl.d\n"
         "Тільки читання (immutable). Задум авторів та системні значення за замовчуванням.",
         BLUE_FILL, NEG, 85),

        ("2. Декларативна конфігурація машини",
         "/etc (хостова конфігурація: fstab, sysctl.d, systemd/system, nginx.conf)\n"
         "Персистентний намір адміністратора на диску. Переживає перезавантаження ОС.",
         WARM_FILL, WARM_BORDER, 185),

        ("3. Летючий рантайм-стан сервісів",
         "/run (/var/run): tmpfs в оперативній пам'яті (PID-файли, IPC-сокети, динамічні юніти)\n"
         "Поточний стан активних процесів. Очищається при вимкненні живлення.",
         GREEN_FILL, FIELD, 285),

        ("4. Живий стан ядра та пристроїв",
         "/proc (процеси, пам'ять, планувальник) · /sys (kobjects, шини, драйвери) · debugfs\n"
         "Синтетичні VFS: дані генеруються ядром на льоту безпосередньо з RAM.",
         PURPLE_FILL, PURPLE_BORDER, 385),

        ("5. Часовий потік подій та журналювання",
         "journald (/var/log/journal) · rsyslog (/var/log/messages) · dmesg (/dev/kmsg)\n"
         "Структуровані та текстові сліди дій, перепадів стану та апаратних збоїв.",
         RED_FILL, POS, 485)
    ]

    for title, desc, f_col, s_col, y_pos in layers:
        p.append(fitbox(40, y_pos, 920, 85,
                        title + "\n" + desc,
                        size=13, fill=f_col, stroke=s_col))

    p.append(fitbox(40, 580, 920, 30,
                    "Правило розслідування: конфігурація у /etc — це лише намір; факт — у /proc, /sys та /run",
                    size=12, fill=FILL, stroke=LINE, bold=True))

    render(os.path.join(IMG, "truth-planes-hierarchy.svg"), W, H, *p)


# ── 2. Архітектурне порівняння /proc та /sys ────────────────────────────────
def fig_proc_vs_sys():
    W, H = 1000, 560
    p = []

    p.append(fitbox(40, 20, 920, 48,
                    "Віртуальні проекції стану ядра: /proc проти /sys",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Ліва колонка: /proc
    p.append(fitbox(40, 80, 445, 45,
                    "/proc (procfs) — процесний вимір",
                    size=14, fill=BLUE_FILL, stroke=NEG, bold=True))

    proc_items = [
        "Фокус: структури task_struct процесів та глобальний стан підсистем ядра",
        "Організація: /proc/<PID>/ (maps, status, fd, ns) та глобальні файли (meminfo, cpuinfo)",
        "sysctl: вузли /proc/sys/ проектуються на глобальні змінні ядра через sysctl_table",
        "Формат виводу: довільний неструктурований текст, багаторядкові таблиці (seq_file)",
        "Історія: виник у Plan 9 / UNIX 8th Ed для зневадження (gdb), розрісся в Linux без єдиної схеми"
    ]
    p.append(fitbox(40, 135, 445, 335,
                    "\n\n".join(proc_items),
                    size=12, fill=FILL, stroke=LINE))

    # Права колонка: /sys
    p.append(fitbox(515, 80, 445, 45,
                    "/sys (sysfs) — об'єктний та пристроєвий вимір",
                    size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))

    sys_items = [
        "Фокус: єдина модель пристроїв ядра (kobject, kset, драйвери та шини)",
        "Організація:\n• /sys/devices/ — фізична топологія шин\n• /sys/bus/ — шини (pci, usb, i2c)\n• /sys/class/ — функціональні класи (net, block, tty)",
        "Суворе правило: один атрибут — один файл (одне число чи слово в ASCII)",
        "Зв'язки: масивне використання символьних посилань для перехресних проєкцій",
        "Історія: спроектований у Linux 2.6 як структурована заміна хаосу /proc"
    ]
    p.append(fitbox(515, 135, 445, 335,
                    "\n\n".join(sys_items),
                    size=12, fill=FILL, stroke=LINE))

    p.append(fitbox(40, 485, 920, 55,
                    "debugfs (/sys/kernel/debug): окрема VFS для розробників без стабільного ABI,\n"
                    "використовується для глибокого налагодження (ftrace, підсистеми DRM, Wi-Fi).",
                    size=12, fill=WARM_FILL, stroke=WARM_BORDER))

    render(os.path.join(IMG, "proc-vs-sys-architecture.svg"), W, H, *p)


# ── 3. Пайплайн системного журналювання ──────────────────────────────────────
def fig_log_pipeline():
    W, H = 1000, 580
    p = []

    p.append(fitbox(40, 20, 920, 48,
                    "Пайплайн телеметрії та реєстрації подій у Linux",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    # Джерела подій (зліва)
    p.append(fitbox(40, 85, 260, 110,
                    "Ядро Linux (printk)\n\n"
                    "Драйвери, пам'ять, OOM, паніки,\n"
                    "повідомлення апаратури",
                    size=12, fill=PURPLE_FILL, stroke=PURPLE_BORDER))

    p.append(fitbox(40, 210, 260, 110,
                    "Користувацькі сервіси\n\n"
                    "stdout / stderr юнітів systemd,\n"
                    "помилки застосунків",
                    size=12, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(40, 335, 260, 110,
                    "Класичний syslog API\n\n"
                    "Виклики syslog() через\n"
                    "сокети /dev/log",
                    size=12, fill=WARM_FILL, stroke=WARM_BORDER))

    # Стрілки від джерел до центру
    p.append(arrow(300, 140, 360, 180, color=LINE, sw=1.8))
    p.append(arrow(300, 265, 360, 265, color=LINE, sw=1.8))
    p.append(arrow(300, 390, 360, 350, color=LINE, sw=1.8))

    # Центр: Кільцевий буфер та systemd-journald
    p.append(fitbox(370, 85, 260, 80,
                    "Кільцевий буфер ядра\n"
                    "struct printk_ringbuffer\n"
                    "доступ: /dev/kmsg, dmesg",
                    size=12, fill=FILL, stroke=LINE))

    p.append(arrow(500, 165, 500, 205, color=LINE, sw=1.8))

    p.append(fitbox(370, 210, 260, 235,
                    "systemd-journald\n\n"
                    "Приймає сокети:\n"
                    "• /run/systemd/journal/socket\n"
                    "• /run/systemd/journal/stdout\n"
                    "• читає /dev/kmsg\n\n"
                    "Збагачує непідробними\n"
                    "метаданими ядра:\n"
                    "_PID, _UID, _SYSTEMD_UNIT,\n"
                    "_COMM, _EXE, _SELINUX_CONTEXT",
                    size=12, fill=GREEN_FILL, stroke=FIELD, bold=False))

    # Стрілки від центру праворуч
    p.append(arrow(630, 260, 690, 190, color=LINE, sw=1.8))
    p.append(arrow(630, 360, 690, 360, color=LINE, sw=1.8))

    # Сховища правди (праворуч)
    p.append(fitbox(700, 110, 260, 150,
                    "Структурований журнал\n"
                    "/var/log/journal/<machine-id>/\n\n"
                    "• Бінарний формат з індексами\n"
                    "• B-дерева для швидкого пошуку\n"
                    "• Захист цілісності FSP\n"
                    "• Читання: journalctl",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(700, 290, 260, 155,
                    "Текстові логи (rsyslog)\n"
                    "/var/log/syslog, auth.log\n\n"
                    "• Пересилання через /dev/log\n"
                    "• Текстові рядки без метаданих\n"
                    "• Ротація через logrotate\n"
                    "• Читання: grep, tail, less",
                    size=12, fill=WARM_FILL, stroke=WARM_BORDER))

    p.append(fitbox(40, 480, 920, 65,
                    "Ключова перевага journald: поля з префіксом «_» заповнюються самим ядром через SO_PEERCRED,\n"
                    "тому скомпрометований процес не може підробити власний PID, юніт чи шлях до бінарника.",
                    size=12, fill=FILL, stroke=LINE, bold=True))

    render(os.path.join(IMG, "log-and-trace-pipeline.svg"), W, H, *p)


if __name__ == '__main__':
    fig_truth_planes()
    fig_proc_vs_sys()
    fig_log_pipeline()
    print("OK: generated 3 figures for finding-answers-in-the-system")
