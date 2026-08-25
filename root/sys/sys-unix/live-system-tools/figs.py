# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")
    ),
)
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig_inspection_architecture():
    w, h = 880, 520
    frags = []

    # Заголовок
    frags.append(
        text(
            440,
            28,
            "Архітектура діагностики: ядро Linux, простір procfs та утиліти спостереження",
            size=16,
            bold=True,
        )
    )

    # Рівень 1: Простір користувача (Інструменти)
    frags.append(
        rect(20, 50, 840, 85, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8)
    )
    frags.append(
        text(
            440,
            70,
            "ПРОСТІР КОРИСТУВАЧА — УТИЛІТИ ІНСПЕКЦІЇ ТА ДІАГНОСТИКИ",
            size=12,
            bold=True,
            color="#475569",
        )
    )

    b_ps, _, _ = textbox(
        130,
        102,
        "ps (POSIX / BSD)\nЗріз процесів (STAT, PID, CPU)",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    b_top, _, _ = textbox(
        390,
        102,
        "top / htop\nРеальний час (CPU ticks, RES/VIRT, LA)",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    b_lsof, _, _ = textbox(
        690,
        102,
        "lsof\nВідкриті дескриптори, сокети, файли",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    frags.extend([b_ps, b_top, b_lsof])

    # Системні виклики до /proc (стрілки)
    frags.append(arrow(130, 125, 200, 175, color="#0284c7"))
    frags.append(arrow(390, 125, 440, 175, color="#0284c7"))
    frags.append(arrow(690, 125, 680, 175, color="#0284c7"))

    # Рівень 2: Віртуальна файлова система procfs
    frags.append(
        rect(20, 175, 840, 150, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8)
    )
    frags.append(
        text(
            440,
            195,
            "ШАР VFS — ВІРТУАЛЬНА ФАЙЛОВА СИСТЕМА PROCFS (/proc)",
            size=12,
            bold=True,
            color="#334155",
        )
    )

    p_stat, _, _ = textbox(
        150,
        250,
        "/proc/[pid]/stat, status\nЛічильники тактів, пам'ять,\nстан (R, S, D, Z, T), PPID, TGID",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#3b82f6",
    )
    p_sys, _, _ = textbox(
        440,
        250,
        "/proc/stat, /proc/loadavg\nСумарні jiffies (us, sy, id, wa...),\nсереднє навантаження за 1/5/15 хв",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#3b82f6",
    )
    p_fd, _, _ = textbox(
        720,
        250,
        "/proc/[pid]/fd/, /proc/net/*\nСимволічні посилання на inode,\nсокети та анонімні пайпи",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#3b82f6",
    )
    frags.extend([p_stat, p_sys, p_fd])

    # Стрілки з /proc до структур ядра
    frags.append(arrow(150, 290, 180, 365, color="#64748b"))
    frags.append(arrow(440, 290, 440, 365, color="#64748b"))
    frags.append(arrow(720, 290, 700, 365, color="#64748b"))

    # Рівень 3: Структури ядра Linux
    frags.append(
        rect(20, 365, 840, 130, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8)
    )
    frags.append(
        text(
            440,
            385,
            "ПРОСТІР ЯДРА — СТРУКТУРИ ТА ПІДСИСТЕМИ LINUX",
            size=12,
            bold=True,
            color="#475569",
        )
    )

    k_proc, _, _ = textbox(
        180,
        440,
        "Керування процесами\nstruct task_struct (state, utime, stime)\nstruct mm_struct (rss, virt space)",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    k_sched, _, _ = textbox(
        440,
        440,
        "Планувальник & Таймери\nkernel_cpustat (сума тактів CPU),\ncalc_load() (експоненційне середнє)",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    k_vfs, _, _ = textbox(
        700,
        440,
        "Підсистема VFS та Мережа\nstruct files_struct -> fdtable -> struct file\nstruct inode (i_nlink, i_size), struct sock",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    frags.extend([k_proc, k_sched, k_vfs])

    path = os.path.join(IMG_DIR, "procfs-inspection-architecture.svg")
    render(path, w, h, *frags)
    print(f"Generated {path}")


def build_fig_stat_transitions():
    w, h = 880, 480
    frags = []

    # Заголовок
    frags.append(
        text(
            440,
            28,
            "Граф станів процесів у Linux (STAT) та їх відображення в утилітах ps/top",
            size=16,
            bold=True,
        )
    )

    # Стани (Блоки)
    s_run, _, _ = textbox(
        150,
        140,
        "R: TASK_RUNNING\nВиконується на CPU\nабо стоїть у черзі Runqueue",
        size=11,
        pad=8,
        fill="#dcfce7",
        stroke="#16a34a",
        bold=True,
    )

    s_int, _, _ = textbox(
        480,
        90,
        "S: TASK_INTERRUPTIBLE\nПереривний сон (очікування події, сокета, таймера)\nПрокидається сигналом або подією",
        size=11,
        pad=8,
        fill="#e0f2fe",
        stroke="#0284c7",
        bold=True,
    )

    s_unint, _, _ = textbox(
        480,
        200,
        "D: TASK_UNINTERRUPTIBLE\nБезперервний сон на дисковому I/O або lock ядра\nІмунний до сигналів (навіть kill -9), рахується в Load Avg",
        size=11,
        pad=8,
        fill="#fee2e2",
        stroke="#dc2626",
        bold=True,
    )

    s_stop, _, _ = textbox(
        150,
        350,
        "T / t: TASK_STOPPED / TRACED\nЗупинено сигналом SIGSTOP / SIGTSTP\nабо зупинено під налагоджувачем ptrace",
        size=11,
        pad=8,
        fill="#fef3c7",
        stroke="#d97706",
        bold=True,
    )

    s_zomb, _, _ = textbox(
        540,
        350,
        "Z: EXIT_ZOMBIE\nЗавершено (do_exit), код виходу в task_struct\nЧекає на виклик wait4() батьківського процесу",
        size=11,
        pad=8,
        fill="#f3e8ff",
        stroke="#9333ea",
        bold=True,
    )

    s_dead, _, _ = textbox(
        780,
        350,
        "X: DEAD\nОстаточне вивільнення\nпам'яті task_struct",
        size=10,
        pad=6,
        fill="#f1f5f9",
        stroke="#64748b",
        bold=True,
    )

    frags.extend([s_run, s_int, s_unint, s_stop, s_zomb, s_dead])

    # Переходи (Стрілки)
    # R -> S (сон на очікуванні)
    frags.append(arrow(190, 115, 330, 95, color="#0284c7"))
    frags.append(text(250, 90, "read(), epoll_wait()", size=9, color="#0284c7"))

    # S -> R (подія надійшла)
    frags.append(arrow(330, 110, 210, 130, color="#16a34a"))
    frags.append(text(270, 132, "Подія / Сигнал", size=9, color="#16a34a"))

    # R -> D (початок блокувального I/O)
    frags.append(arrow(180, 165, 300, 195, color="#dc2626"))
    frags.append(text(230, 172, "Синхронний I/O, семафор", size=9, color="#dc2626"))

    # D -> R (завершення I/O драйвером)
    frags.append(arrow(300, 210, 190, 180, color="#16a34a"))
    frags.append(text(250, 218, "Переривання I/O", size=9, color="#16a34a"))

    # R -> T (SIGSTOP / SIGTSTP)
    frags.append(arrow(130, 185, 130, 305, color="#d97706"))
    frags.append(text(80, 250, "SIGSTOP / Ctrl+Z", size=9, color="#d97706"))

    # T -> R (SIGCONT)
    frags.append(arrow(170, 305, 170, 185, color="#16a34a"))
    frags.append(text(205, 250, "SIGCONT", size=9, color="#16a34a"))

    # R -> Z (do_exit)
    frags.append(arrow(210, 170, 430, 325, color="#9333ea"))
    frags.append(text(350, 270, "exit_group() / вихід", size=9, color="#9333ea"))

    # Z -> X (wait4)
    frags.append(arrow(650, 350, 715, 350, color="#64748b"))
    frags.append(text(685, 335, "wait4()", size=9, color="#64748b"))

    # Нижня панель: суфікси STAT в утиліті ps
    frags.append(
        rect(20, 410, 840, 55, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6)
    )
    frags.append(
        text(
            440,
            428,
            "Модифікатори STAT у ps: < (високий пріоритет)  ·  N (низький пріоритет)  ·  L (сторінки заблоковано в RAM)",
            size=10,
            color="#334155",
        )
    )
    frags.append(
        text(
            440,
            448,
            "s (лідер сесії)  ·  l (багатопотоковий процес / multi-threaded)  ·  + (процес у foreground групі термінала)",
            size=10,
            color="#334155",
        )
    )

    path = os.path.join(IMG_DIR, "process-stat-transitions.svg")
    render(path, w, h, *frags)
    print(f"Generated {path}")


def build_fig_deleted_leak():
    w, h = 880, 480
    frags = []

    # Заголовок
    frags.append(
        text(
            440,
            28,
            "Механіка витоку дискового простору при unlink: чому показники df та du розходяться",
            size=16,
            bold=True,
        )
    )

    # Ліва колонка: Файлова система (Шляхи й dentry)
    frags.append(
        rect(20, 60, 260, 390, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    )
    frags.append(
        text(
            150,
            85,
            "ДЕРЕВО КАТАЛОГІВ (DENTRY)",
            size=12,
            bold=True,
            color="#334155",
        )
    )

    d_root, _, _ = textbox(
        150,
        135,
        "Каталог /var/log/\n(dentry: log_dir)",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    d_file, _, _ = textbox(
        150,
        225,
        "app.log (dentry)\n(ВИДАЛЕНО через unlink)\n[ dentry вилучено з каталогу ]",
        size=10,
        pad=6,
        fill="#fee2e2",
        stroke="#dc2626",
    )
    d_du, _, _ = textbox(
        150,
        360,
        "Утиліта du:\nОбходить дерево каталогів\nНе бачить app.log -> показує 0 Б\nДиск виглядає «порожнім»",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#dc2626",
    )
    frags.extend([d_root, d_file, d_du])
    frags.append(arrow(150, 160, 150, 195, color="#64748b"))
    frags.append(arrow(150, 260, 150, 310, color="#dc2626"))

    # Центральна колонка: Відкриті дескриптори процесу (VFS)
    frags.append(
        rect(300, 60, 280, 390, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8)
    )
    frags.append(
        text(
            440,
            85,
            "ТАБЛИЦЯ ДЕСКРИПТОРІВ (VFS)",
            size=12,
            bold=True,
            color="#14532d",
        )
    )

    p_proc, _, _ = textbox(
        440,
        135,
        "Процес (PID 4821)\nfiles_struct -> fdtable",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#16a34a",
    )
    p_fd, _, _ = textbox(
        440,
        225,
        "Дескриптор fd=3\nstruct file (f_count = 1)\n/proc/4821/fd/3 -> app.log (deleted)",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#16a34a",
    )
    p_lsof, _, _ = textbox(
        440,
        360,
        "Утиліта lsof /proc:\nЗнаходить відкритий дескриптор\nіз міткою (deleted)\nВиявляє джерело витоку",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#16a34a",
    )
    frags.extend([p_proc, p_fd, p_lsof])
    frags.append(arrow(440, 160, 440, 195, color="#16a34a"))
    frags.append(arrow(440, 260, 440, 310, color="#16a34a"))

    # Права колонка: Іноди та Суперблок (Дисковий простір)
    frags.append(
        rect(600, 60, 260, 390, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8)
    )
    frags.append(
        text(
            730,
            85,
            "ІНОДА ТА СУПЕРБЛОК ФС",
            size=12,
            bold=True,
            color="#713f12",
        )
    )

    i_inode, _, _ = textbox(
        730,
        155,
        "struct inode (ext4/xfs)\ni_nlink = 0 (посилань у ФС немає)\nАЛЕ f_count > 0 (файл відкритий)",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#ca8a04",
    )
    i_blocks, _, _ = textbox(
        730,
        245,
        "Блоки даних на диску\n(50 ГБ логів ЗАБЛОКОВАНО)\nБлоки НЕ повертаються у пул",
        size=10,
        pad=6,
        fill="#fee2e2",
        stroke="#dc2626",
    )
    i_df, _, _ = textbox(
        730,
        360,
        "Утиліта df (statvfs):\nОпитує суперблок ФС\nБачить зайняті блоки -> 100% full\nДиск переповнений!",
        size=10,
        pad=6,
        fill="#ffffff",
        stroke="#dc2626",
    )
    frags.extend([i_inode, i_blocks, i_df])
    frags.append(arrow(730, 190, 730, 215, color="#dc2626"))
    frags.append(arrow(730, 280, 730, 315, color="#dc2626"))

    # Зв'язки між колонками
    # fd=3 тримає посилання на inode
    frags.append(arrow(530, 225, 630, 175, color="#ca8a04", sw=2))
    frags.append(text(580, 190, "struct file*", size=9, color="#ca8a04"))

    path = os.path.join(IMG_DIR, "deleted-file-vfs-leak.svg")
    render(path, w, h, *frags)
    print(f"Generated {path}")


if __name__ == "__main__":
    build_fig_inspection_architecture()
    build_fig_stat_transitions()
    build_fig_deleted_leak()
