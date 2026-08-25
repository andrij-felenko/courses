# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#f8f9fa"
BORDER_GREY = "#b0bec5"
DARK_TEXT = "#263238"


def fig_debugfs_comparison():
    """Схема порівняння procfs, sysfs та debugfs."""
    W, H = 1200, 620
    p = []

    # Головний контейнер
    p.append(rect(20, 20, 1160, 580, fill=GREY, stroke=BORDER_GREY, sw=1.5, rx=8))
    p.append(text(600, 55, "Віртуальні файлові системи ядра Linux", size=20, bold=True, color=DARK_TEXT))

    # Стовпчик 1: procfs
    p.append(rect(50, 90, 340, 480, fill="#ffffff", stroke="#1976d2", sw=2, rx=6))
    p.append(rect(50, 90, 340, 50, fill="#bbdefb", stroke="#1976d2", sw=1.5, rx=6))
    p.append(text(220, 122, "procfs (/proc)", size=17, bold=True, color="#0d47a1"))
    
    p.append(text(70, 170, "• Призначення: метадані процесів", size=14, bold=True, anchor="start"))
    p.append(text(70, 195, "  та глобальні параметри ядра", size=13, color="#455a64", anchor="start"))
    p.append(text(70, 235, "• Правила ABI: СТАБІЛЬНІ", size=14, bold=True, color="#2e7d32", anchor="start"))
    p.append(text(70, 260, "  зміна формату ламає утиліти", size=13, color="#455a64", anchor="start"))
    p.append(text(70, 300, "• Формат файлів: текстовий,", size=14, anchor="start"))
    p.append(text(70, 325, "  іноді неструктурований", size=13, color="#455a64", anchor="start"))
    p.append(text(70, 365, "• Доступ: непривілейований", size=14, anchor="start"))
    p.append(text(70, 390, "  (частково обмежений правами)", size=13, color="#455a64", anchor="start"))
    p.append(text(70, 430, "• Основні об'єкти: /proc/[pid],", size=14, anchor="start"))
    p.append(text(70, 455, "  /proc/cpuinfo, /proc/meminfo", size=13, color="#455a64", anchor="start"))

    # Стовпчик 2: sysfs
    p.append(rect(430, 90, 340, 480, fill="#ffffff", stroke="#2e7d32", sw=2, rx=6))
    p.append(rect(430, 90, 340, 50, fill="#c8e6c9", stroke="#2e7d32", sw=1.5, rx=6))
    p.append(text(600, 122, "sysfs (/sys)", size=17, bold=True, color="#1b5e20"))

    p.append(text(450, 170, "• Призначення: модель пристроїв", size=14, bold=True, anchor="start"))
    p.append(text(450, 195, "  (Device Model & kobjects)", size=13, color="#455a64", anchor="start"))
    p.append(text(450, 235, "• Правила ABI: СУВОРІ Й СТАБІЛЬНІ", size=14, bold=True, color="#2e7d32", anchor="start"))
    p.append(text(450, 260, "  «Never break userspace»", size=13, color="#455a64", anchor="start"))
    p.append(text(450, 300, "• Формат: 1 файл = 1 значення", size=14, bold=True, anchor="start"))
    p.append(text(450, 325, "  строга структура атрибутів", size=13, color="#455a64", anchor="start"))
    p.append(text(450, 365, "• Доступ: керується udev/sysfs", size=14, anchor="start"))
    p.append(text(450, 390, "  (системні сервіси й користувачі)", size=13, color="#455a64", anchor="start"))
    p.append(text(450, 430, "• Основні об'єкти: /sys/bus,", size=14, anchor="start"))
    p.append(text(450, 455, "  /sys/class, /sys/devices", size=13, color="#455a64", anchor="start"))

    # Стовпчик 3: debugfs
    p.append(rect(810, 90, 340, 480, fill="#ffffff", stroke="#c62828", sw=2, rx=6))
    p.append(rect(810, 90, 340, 50, fill="#ffcdd2", stroke="#c62828", sw=1.5, rx=6))
    p.append(text(980, 122, "debugfs (/sys/kernel/debug)", size=17, bold=True, color="#b71c1c"))

    p.append(text(830, 170, "• Призначення: відлагодження", size=14, bold=True, anchor="start"))
    p.append(text(830, 195, "  драйверів та підсистем ядра", size=13, color="#455a64", anchor="start"))
    p.append(text(830, 235, "• Правила ABI: ВІДСУТНІ", size=14, bold=True, color="#c62828", anchor="start"))
    p.append(text(830, 260, "  формат може змінюватися щодня", size=13, color="#455a64", anchor="start"))
    p.append(text(830, 300, "• Формат: довільні дампи,", size=14, anchor="start"))
    p.append(text(830, 325, "  seq_file, регістри, блоби", size=13, color="#455a64", anchor="start"))
    p.append(text(830, 365, "• Доступ: лише root (0700)", size=14, bold=True, color="#c62828", anchor="start"))
    p.append(text(830, 390, "  блокується під Lockdown", size=13, color="#455a64", anchor="start"))
    p.append(text(830, 430, "• Основні об'єкти: DRM, USB,", size=14, anchor="start"))
    p.append(text(830, 455, "  mac80211, dynamic_debug", size=13, color="#455a64", anchor="start"))

    render(os.path.join(IMG, 'fig-debugfs-comparison.svg'), W, H, *p)


def fig_debugfs_internals():
    """Схема внутрішньої архітектури VFS, SRCU та життєвого циклу у debugfs."""
    W, H = 1240, 640
    p = []

    # Головний фоновий прямокутник
    p.append(rect(20, 20, 1200, 600, fill="#fcfcfc", stroke=BORDER_GREY, sw=1.5, rx=8))
    p.append(text(620, 55, "Внутрішній механізм викликів VFS та безпека вилучення у debugfs", size=19, bold=True, color=DARK_TEXT))

    # Зона User Space
    p.append(rect(50, 90, 1140, 90, fill="#f1f8e9", stroke="#7cb342", sw=1.5, rx=6))
    p.append(text(70, 115, "User Space (Користувацький простір)", size=15, bold=True, color="#33691e", anchor="start"))
    p.append(rect(90, 130, 440, 40, fill="#ffffff", stroke="#558b2f", sw=1, rx=4))
    p.append(text(310, 155, "Процес читання: cat /sys/kernel/debug/my_mod/status", size=13))

    p.append(rect(710, 130, 440, 40, fill="#ffffff", stroke="#c62828", sw=1, rx=4))
    p.append(text(930, 155, "Вивантаження модуля ядра: sudo rmmod my_mod", size=13, bold=True, color="#b71c1c"))

    # Зона VFS
    p.append(rect(50, 210, 1140, 160, fill=BLUE, stroke="#1e88e5", sw=1.5, rx=6))
    p.append(text(70, 235, "VFS Layer (Шар віртуальної файлової системи)", size=15, bold=True, color="#0d47a1", anchor="start"))

    p.append(rect(90, 255, 440, 95, fill="#ffffff", stroke="#1565c0", sw=1, rx=4))
    p.append(text(310, 280, "Системний виклик read(fd, buf, len)", size=14, bold=True))
    p.append(text(310, 305, "vfs_read() -> debugfs_file_read()", size=13, color="#1565c0"))
    p.append(text(310, 330, "Вхід у SRCU read lock: debugfs_file_get()", size=13, bold=True, color="#2e7d32"))

    p.append(rect(710, 255, 440, 95, fill="#ffffff", stroke="#d32f2f", sw=1, rx=4))
    p.append(text(930, 280, "Виклик debugfs_remove_recursive()", size=14, bold=True, color="#c62828"))
    p.append(text(930, 305, "Позначення dentry як DEAD", size=13, color="#b71c1c"))
    p.append(text(930, 330, "Синхронізація SRCU: synchronize_srcu()", size=13, bold=True, color="#d32f2f"))

    # Зона Kernel Module
    p.append(rect(50, 400, 1140, 190, fill=WARM, stroke="#fb8c00", sw=1.5, rx=6))
    p.append(text(70, 425, "Драйвер / Модуль ядра (Kernel Module State)", size=15, bold=True, color="#e65100", anchor="start"))

    p.append(rect(90, 450, 440, 120, fill="#ffffff", stroke="#f57c00", sw=1, rx=4))
    p.append(text(310, 475, "Реалізація file_operations / seq_file", size=14, bold=True))
    p.append(text(310, 505, "Виклик fops->read() або seq_printf()", size=13, color="#e65100"))
    p.append(text(310, 535, "Формування даних з оперативної пам'яті ядра", size=13, color="#424242"))

    p.append(rect(710, 450, 440, 120, fill="#ffffff", stroke="#757575", sw=1, rx=4))
    p.append(text(930, 475, "Звільнення ресурсів модуля", size=14, bold=True))
    p.append(text(930, 505, "Безнаслідкове вилучення структур даних", size=13, color="#616161"))
    p.append(text(930, 535, "Запобігання Use-After-Free та Kernel Panic", size=13, bold=True, color="#2e7d32"))

    # Зв'язуючі стрілки — x=580 (read path) та x=660 (rmmod path)
    p.append(arrow(580, 175, 580, 245, color="#1565c0", sw=2))
    p.append(text(570, 210, "read", size=12, color="#1565c0", anchor="end"))

    p.append(arrow(580, 355, 580, 445, color="#2e7d32", sw=2))
    p.append(text(570, 400, "fetch", size=12, color="#2e7d32", anchor="end"))

    p.append(arrow(660, 175, 660, 245, color="#c62828", sw=2))
    p.append(text(670, 210, "rmmod", size=12, color="#c62828", anchor="start"))

    p.append(arrow(660, 355, 660, 445, color="#d32f2f", sw=2))
    p.append(text(670, 400, "cleanup", size=12, color="#d32f2f", anchor="start"))

    render(os.path.join(IMG, 'fig-debugfs-internals.svg'), W, H, *p)


if __name__ == "__main__":
    fig_debugfs_comparison()
    fig_debugfs_internals()
    print("Successfully generated debugfs figures in ./img/")
