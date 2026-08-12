# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#eceff1"

# ── 1. Архітектура devtmpfs: від реєстрації пристрою до udev ─────────────────
def fig_devtmpfs_architecture():
    W, H = 1200, 690
    p = []

    # Загальний контейнер
    p.append(rect(20, 20, 1160, 650, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    # Секції
    p.append(text(300, 50, "ПРОСТІР ЯДРА (Kernel Space)", size=16, bold=True, color=NEG))
    p.append(text(920, 50, "ПРОСТІР КОРИСТУВАЧА (User Space)", size=16, bold=True, color=POS))
    p.append(line(600, 30, 600, 650, color=MUTED, sw=1.5, dash="6,6"))

    # Блок 1: Драйвер пристрою та device_add()
    p.append(fitbox(40, 80, 520, 120,
                    "1. Ініціалізація та реєстрація пристрою\n"
                    "• Драйвер викликом device_add() виділяє dev_t (major, minor)\n"
                    "• device_add() потрапляє у devtmpfs_create_node(dev)\n"
                    "• Працює в атомарному контексті драйвера (без спання)",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    p.append(arrow(300, 200, 300, 240, color=LINE, sw=2))
    p.append(text(315, 220, "асинхронна черга req_list", size=11, color=MUTED, anchor="start"))

    # Блок 2: Демон kdevtmpfs та VFS операції
    p.append(fitbox(40, 240, 520, 150,
                    "2. Потік ядра kdevtmpfs (асинхронний обробник)\n"
                    "• Прокидається викликом wake_up_process(thread)\n"
                    "• Витягує struct req з замкненої черги req_list\n"
                    "• Виконує VFS-операції зі спанням: vfs_mkdir() та vfs_mknod()\n"
                    "• Створює файл вузла (S_IFCHR / S_IFBLK) у пам'яті devtmpfs",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.5))

    p.append(arrow(300, 390, 300, 430, color=LINE, sw=2))

    # Блок 3: Внутрішнє дерево devtmpfs у пам'яті
    p.append(fitbox(40, 430, 520, 140,
                    "3. Віртуальне дерево devtmpfs (/dev/)\n"
                    "• Одразу створюються стандартні вузли (/dev/sda1, /dev/null)\n"
                    "• Початкові права: 0600 або 0666, власник root:root (uid=0, gid=0)\n"
                    "• Доступне для ядрового init та initramfs ДО запуску udevd",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # Ліва -> Права сторона (Перехід у User Space)
    # Подія netlink uevent
    p.append(arrow(560, 140, 640, 140, color=NEG, sw=2))
    p.append(text(600, 125, "kobject_uevent()", size=11, color=NEG, anchor="middle"))

    # Блок 4: Демон systemd-udevd у просторі користувача
    p.append(fitbox(640, 80, 520, 140,
                    "4. Демон systemd-udevd (простір користувача)\n"
                    "• Слухає сокет NETLINK_KOBJECT_UEVENT\n"
                    "• Отримує сповіщення про створення вузла у devtmpfs\n"
                    "• Зчитує правила з /lib/udev/rules.d/ та /etc/udev/rules.d/",
                    size=13, fill=BLUE_FILL, stroke=POS, sw=1.5))

    p.append(arrow(900, 220, 900, 260, color=POS, sw=2))

    # Блок 5: Збагачення вузлів та символічні посилання
    p.append(fitbox(640, 260, 520, 160,
                    "5. Збагачення та модифікація /dev/\n"
                    "• Зміна власників та прав (chmod 0660 root:disk /dev/sda1)\n"
                    "• Створення символічних посилань:\n"
                    "   /dev/disk/by-uuid/5E2A-11F0 ──► ../../sda1\n"
                    "   /dev/snd/by-path/pci-0000:00:1f.3 ──► ../controlC0\n"
                    "• Застосування ACL-правил (systemd-logind / udev-acl)",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.5))

    p.append(arrow(900, 420, 900, 460, color=LINE, sw=2))

    # Блок 6: Готова система вузлів для додатків
    p.append(fitbox(640, 460, 520, 110,
                    "6. Фінальний стан файлової системи /dev\n"
                    "• Стабільні імена для монтажу системних дисків\n"
                    "• Безпечні права доступу для користувацьких груп (audio, video)\n"
                    "• Захист від race condition під час завантаження",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, 'devtmpfs-architecture.svg'), W, H, *p)

# ── 2. Еволюція керування вузлами пристроїв Linux ───────────────────────────
def fig_dev_evolution_timeline():
    W, H = 1200, 640
    p = []

    p.append(rect(20, 20, 1160, 600, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(text(600, 50, "Еволюція керування вузлами пристроїв у Linux (/dev)", size=18, bold=True, color=LINE))

    # 4 колонки
    col_w = 265
    gap = 18
    left_start = 35

    # Ера 1: Статичний /dev
    x1 = left_start
    p.append(fitbox(x1, 80, col_w, 510,
                    "1. Статичний /dev\n"
                    "(Linux 1.x ── 2.4)\n\n"
                    "• Файли створюються через MAKEDEV\n"
                    "• Тисячі статичних вузлів на дисках\n"
                    "• Відсутність підтримки hotplug\n\n"
                    "Проблема: розбухання rootfs.",
                    size=12, fill=RED_FILL, stroke=NEG, sw=1.5))

    # Ера 2: devfs
    x2 = x1 + col_w + gap
    p.append(fitbox(x2, 80, col_w, 510,
                    "2. devfs у ядрі\n"
                    "(Linux 2.3.46 ── 2.6.17)\n\n"
                    "• Динамічна система всередині ядра\n"
                    "• Імена зашиті у код ядра\n"
                    "• Автоматичне створення вузлів\n\n"
                    "Проблема: дедлоки VFS, вилучено.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.5))

    # Ера 3: udev на tmpfs
    x3 = x2 + col_w + gap
    p.append(fitbox(x3, 80, col_w, 510,
                    "3. udev на tmpfs\n"
                    "(Linux 2.6.0 ── 2.6.31)\n\n"
                    "• Чистий /dev як tmpfs у user-space\n"
                    "• udevd створює вузли за uevent\n"
                    "• Гнучкі правила та symlinks\n\n"
                    "Проблема: race condition завантаження.",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    # Ера 4: devtmpfs + udevd
    x4 = x3 + col_w + gap
    p.append(fitbox(x4, 80, col_w, 510,
                    "4. devtmpfs + udevd\n"
                    "(Linux 2.6.32 ── дотепер)\n\n"
                    "• devtmpfs створює вузли ядром\n"
                    "• Працює ще до запуску udevd\n"
                    "• udevd збагачує лінками й правами\n\n"
                    "Перевага: миттєве завантаження.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, 'dev-evolution-timeline.svg'), W, H, *p)

if __name__ == '__main__':
    fig_devtmpfs_architecture()
    fig_dev_evolution_timeline()
    print("Generated all figures successfully.")
