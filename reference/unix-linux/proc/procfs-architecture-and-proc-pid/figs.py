# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"
DARK_BLUE = "#1a237e"


def fig_procfs_vfs_architecture():
    """Схема взаємодії VFS, procfs та внутрішніх структур ядра."""
    W, H = 1420, 680
    p = []

    # Заголовок та зони
    p.append(rect(30, 40, 1360, 600, fill="#f8f9fa", stroke="#b0bec5", sw=1.5, rx=8))
    p.append(text(60, 75, "Простір користувача (User Space)", size=16, bold=True, color="#37474f"))

    # Блок системного виклику у User Space
    p.append(rect(60, 100, 390, 110, fill="#ffffff", stroke="#1565c0", sw=2, rx=6))
    p.append(text(255, 135, "Утиліта користувача (ps / top / cat)", size=15, bold=True))
    p.append(text(255, 170, "read(fd, buf, count) -> /proc/1234/status", size=14, italic=True, color="#455a64"))

    # Лінія розділу між User Space та Kernel Space
    p.append(line(40, 240, 1380, 240, color="#d32f2f", dash="6 4", sw=2))
    p.append(text(60, 265, "Простір ядра (Kernel Space)", size=16, bold=True, color="#c62828"))

    # Блок VFS Layer
    p.append(rect(60, 290, 390, 130, fill=BLUE, stroke="#1976d2", sw=2, rx=6))
    p.append(text(255, 325, "Шар VFS (Virtual File System)", size=15, bold=True, color="#0d47a1"))
    p.append(text(255, 360, "vfs_read() / proc_pid_lookup()", size=14))
    p.append(text(255, 390, "Перевірка dentry & dentry_operations", size=13, color="#37474f"))

    # Блок procfs Core & seq_file
    p.append(rect(510, 290, 410, 130, fill=WARM, stroke="#f57c00", sw=2, rx=6))
    p.append(text(715, 325, "Рушій procfs & seq_file", size=15, bold=True, color="#e65100"))
    p.append(text(715, 360, "proc_single_show() -> seq_printf()", size=14))
    p.append(text(715, 390, "Динамічна генерація тексту без диска", size=13, color="#37474f"))

    # Блок Kernel Data Structures (task_struct, mm_struct)
    p.append(rect(970, 290, 390, 310, fill=GREEN, stroke="#2e7d32", sw=2, rx=6))
    p.append(text(1165, 325, "Структури даних ядра", size=16, bold=True, color="#1b5e20"))

    p.append(rect(990, 355, 350, 65, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1165, 380, "struct task_struct (PID 1234)", size=14, bold=True))
    p.append(text(1165, 403, "pid, state, uid, gid, comm", size=13, color="#555555"))

    p.append(rect(990, 435, 350, 65, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1165, 460, "struct mm_struct", size=14, bold=True))
    p.append(text(1165, 483, "total_vm, rss, mmap (VMA list)", size=13, color="#555555"))

    p.append(rect(990, 515, 350, 65, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1165, 540, "struct files_struct", size=14, bold=True))
    p.append(text(1165, 563, "fdt -> fd array (open files)", size=13, color="#555555"))

    # Стрілки з'єднання
    # 1. User -> VFS
    p.append(arrow(255, 210, 255, 282, color="#1565c0", sw=2))
    p.append(text(270, 235, "syscall: read()", size=13, color="#1565c0", anchor="start"))

    # 2. VFS -> procfs
    p.append(arrow(450, 355, 502, 355, color="#1976d2", sw=2))
    p.append(text(476, 343, "proc_ops", size=13, color="#1976d2"))

    # 3. procfs -> Kernel Data Structures
    p.append(arrow(920, 355, 962, 385, color="#e65100", sw=2))
    p.append(arrow(920, 355, 962, 465, color="#e65100", sw=2))
    p.append(arrow(920, 355, 962, 545, color="#e65100", sw=2))

    # Нижній пояснювальний блок для procfs
    p.append(rect(60, 460, 860, 140, fill="#ffffff", stroke="#78909c", sw=1.5, rx=6))
    p.append(text(490, 490, "Життєвий цикл inode/dentry у procfs", size=15, bold=True, color="#263238"))
    p.append(text(490, 520, "1. lookup() створює тимчасовий inode на вимогу виклику open()/stat()", size=13, color="#37474f"))
    p.append(text(490, 545, "2. dentry_operations.d_revalidate() перевіряє, чи процес task_struct ще живий", size=13, color="#37474f"))
    p.append(text(490, 570, "3. Якщо процес помер -> dentry зникає зі списків VFS без зчитування з диска", size=13, color="#37474f"))

    render(os.path.join(IMG, 'procfs-vfs-architecture.svg'), W, H, *p)


def fig_proc_pid_structure():
    """Структура каталогу /proc/[pid] та її ключові вузли."""
    W, H = 1380, 650
    p = []

    # Головний корінь /proc/[pid]
    p.append(rect(30, 40, 1320, 570, fill="#fafafa", stroke="#cfd8dc", sw=1.5, rx=8))

    # Кореневий вузол
    p.append(rect(540, 60, 300, 65, fill=DARK_BLUE, stroke="#0d47a1", sw=2, rx=6))
    p.append(text(690, 97, "/proc/[pid] (напр. /proc/1234/)", size=17, bold=True, color="#ffffff"))

    # Категорії гілок
    # Гілка 1: Метадані стану
    p.append(rect(60, 170, 380, 410, fill=BLUE, stroke="#1e88e5", sw=1.5, rx=6))
    p.append(text(250, 200, "Метадані та стан процесу", size=16, bold=True, color="#0d47a1"))

    meta_items = [
        ("cmdline", "Аргументи виклику (\\x00-separated)"),
        ("environ", "Змінні оточення (\\x00-separated)"),
        ("status", "Людиночитаний стан (UID, RSS, Threads)"),
        ("stat", "Машинні лічильники та кванти CPU"),
        ("statm", "Розмір пам’яті у сторінках (pages)"),
        ("cgroup", "Приналежність до контрольних груп"),
        ("oom_score", "Оцінка OOM-killer для ліквідації")
    ]
    y_m = 230
    for name, desc in meta_items:
        p.append(rect(80, y_m, 340, 42, fill="#ffffff", stroke="#90caf9", sw=1, rx=4))
        p.append(text(95, y_m + 25, name, size=14, bold=True, anchor="start", color="#1565c0"))
        p.append(text(410, y_m + 25, desc, size=12, color="#455a64", anchor="end"))
        y_m += 48

    # Гілка 2: Пам'ять та ресурси
    p.append(rect(500, 170, 380, 410, fill=WARM, stroke="#fb8c00", sw=1.5, rx=6))
    p.append(text(690, 200, "Віртуальна пам’ять та ресурси", size=16, bold=True, color="#e65100"))

    mem_items = [
        ("maps", "Карта областей VMA (адреси, права)"),
        ("smaps", "Детальні метрики пам'яті (PSS, RSS, Swap)"),
        ("mem", "Прямий доступ до адрес процесу (для gdb)"),
        ("fd/", "Каталог файлових дескрипторів (symlinks)"),
        ("fdinfo/", "Детальні позиції та прапори для fd"),
        ("limits", "Обмеження ресурсів процесу (rlimit)"),
        ("io", "Статистика дискового вводу/виводу")
    ]
    y_mem = 230
    for name, desc in mem_items:
        p.append(rect(520, y_mem, 340, 42, fill="#ffffff", stroke="#ffe082", sw=1, rx=4))
        p.append(text(535, y_mem + 25, name, size=14, bold=True, anchor="start", color="#ef6c00"))
        p.append(text(850, y_mem + 25, desc, size=12, color="#455a64", anchor="end"))
        y_mem += 48

    # Гілка 3: Символічні посилання та ієрархія
    p.append(rect(940, 170, 380, 410, fill=GREEN, stroke="#43a047", sw=1.5, rx=6))
    p.append(text(1130, 200, "Символічні посилання та потоки", size=16, bold=True, color="#1b5e20"))

    sym_items = [
        ("cwd ->", "Поточний робочий каталог (magic link)"),
        ("exe ->", "Шлях до виконуваного файла на диску"),
        ("root ->", "Кореневий каталог процесу (chroot)"),
        ("task/", "Підкаталоги потоків [tid] (POSIX threads)"),
        ("ns/", "Простори імен Linux (net, pid, mnt...)"),
        ("net/", "Мережевий стек у даному netns"),
        ("mounts", "Точки монтування даного mntns")
    ]
    y_sym = 230
    for name, desc in sym_items:
        p.append(rect(960, y_sym, 340, 42, fill="#ffffff", stroke="#a5d6a7", sw=1, rx=4))
        p.append(text(975, y_sym + 25, name, size=14, bold=True, anchor="start", color="#2e7d32"))
        p.append(text(1290, y_sym + 25, desc, size=12, color="#455a64", anchor="end"))
        y_sym += 48

    # Стрілки від кореня до трьох колонок
    p.append(arrow(600, 125, 250, 162, color="#0d47a1", sw=2))
    p.append(arrow(690, 125, 690, 162, color="#e65100", sw=2))
    p.append(arrow(780, 125, 1130, 162, color="#1b5e20", sw=2))

    render(os.path.join(IMG, 'proc-pid-structure.svg'), W, H, *p)


if __name__ == '__main__':
    fig_procfs_vfs_architecture()
    fig_proc_pid_structure()
    print("ok")
