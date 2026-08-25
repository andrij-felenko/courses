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


def fig_cgroupfs_v1_vs_v2_tree():
    """Порівняння ортогональних ієрархій cgroup v1 та єдиного дерева cgroup v2."""
    W, H = 1420, 680
    p = []

    # Загальний контейнер
    p.append(rect(20, 20, 1380, 640, fill="#fdfdfd", stroke="#cfd8dc", sw=1.5, rx=8))

    # Заголовок лівої панелі: cgroup v1
    p.append(rect(40, 40, 650, 600, fill="#f8f9fa", stroke="#b0bec5", sw=1.5, rx=6))
    p.append(text(365, 75, "cgroup v1: Ортогональні незалежні дерева", size=16, bold=True, color="#c62828"))

    # Дерево CPU у v1
    p.append(rect(60, 105, 290, 240, fill=RED, stroke="#e57373", sw=1.5, rx=6))
    p.append(text(205, 135, "Ієрархія /sys/fs/cgroup/cpu", size=14, bold=True, color="#b71c1c"))
    p.append(rect(110, 155, 180, 40, fill="#ffffff", stroke="#d32f2f", sw=1.5, rx=4))
    p.append(text(200, 180, "Root CPU cgroup", size=13, bold=True))
    p.append(line(200, 195, 200, 220, color="#d32f2f", sw=1.5))
    p.append(rect(110, 220, 180, 40, fill="#ffffff", stroke="#d32f2f", sw=1.5, rx=4))
    p.append(text(200, 245, "Group_A (CPU limits)", size=13))
    p.append(rect(80, 280, 240, 45, fill="#fff3e0", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(200, 308, "Process P1 (PID 4012)", size=13, bold=True, color="#e65100"))

    # Дерево Memory у v1
    p.append(rect(380, 105, 290, 240, fill=BLUE, stroke="#64b5f6", sw=1.5, rx=6))
    p.append(text(525, 135, "Ієрархія /sys/fs/cgroup/memory", size=14, bold=True, color="#0d47a1"))
    p.append(rect(435, 155, 180, 40, fill="#ffffff", stroke="#1976d2", sw=1.5, rx=4))
    p.append(text(525, 180, "Root Memory cgroup", size=13, bold=True))
    p.append(line(525, 195, 525, 220, color="#1976d2", sw=1.5))
    p.append(rect(435, 220, 180, 40, fill="#ffffff", stroke="#1976d2", sw=1.5, rx=4))
    p.append(text(525, 245, "Group_B (Mem limits)", size=13))
    p.append(rect(405, 280, 240, 45, fill="#fff3e0", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(525, 308, "Process P1 (PID 4012)", size=13, bold=True, color="#e65100"))

    # Проблема v1
    p.append(rect(60, 365, 610, 255, fill="#fff9c4", stroke="#fbc02d", sw=1.5, rx=6))
    p.append(text(365, 395, "Проблема cgroup v1: Конфлікт між контролерами", size=14, bold=True, color="#f57f17"))
    p.append(fitbox(80, 415, 570, 185, 
                    "• Процес P1 належить Group_A у CPU та Group_B у Memory.\n"
                    "• При скиданні брудних сторінок пам'яті (Buffered I/O Writeback)\n"
                    "  ядерний kworker не знає, до якої cgroup блокового I/O\n"
                    "  віднести операцію дискового запису.\n"
                    "• Розрив між контролерами унеможливлює точний облік I/O,\n"
                    "  створює гонки при міграції PID та блокування у ядрі.",
                    size=13, fill="#ffffff", stroke="#fbc02d", color="#37474f"))

    # Заголовок правої панелі: cgroup v2
    p.append(rect(730, 40, 650, 600, fill="#f8f9fa", stroke="#b0bec5", sw=1.5, rx=6))
    p.append(text(1055, 75, "cgroup v2: Єдина ієрархічна система (Unified Tree)", size=16, bold=True, color="#2e7d32"))

    # Єдине дерево cgroup v2
    p.append(rect(750, 105, 610, 515, fill=GREEN, stroke="#81c784", sw=1.5, rx=6))
    p.append(text(1055, 135, "Корінь /sys/fs/cgroup (Unified Hierarchy)", size=15, bold=True, color="#1b5e20"))
    p.append(text(1055, 160, "cgroup.subtree_control = \"+cpu +memory +io\"", size=13, italic=True, color="#2e7d32"))

    # Проміжний вузол (workload)
    p.append(rect(880, 190, 350, 65, fill="#ffffff", stroke="#388e3c", sw=2, rx=4))
    p.append(text(1055, 215, "Вузол /sys/fs/cgroup/workload", size=14, bold=True))
    p.append(text(1055, 240, "cgroup.subtree_control = \"+cpu +memory +io\"", size=12, color="#555555"))

    p.append(line(1055, 255, 1055, 290, color="#2e7d32", sw=2))

    # Дочірні листи cgroup v2
    p.append(rect(780, 290, 260, 100, fill="#ffffff", stroke="#388e3c", sw=1.5, rx=4))
    p.append(text(910, 315, "Вузол app1 (Листок)", size=14, bold=True))
    p.append(text(910, 340, "cpu.max = \"50000 100000\"", size=12, color="#455a64"))
    p.append(text(910, 365, "memory.max = \"1073741824\"", size=12, color="#455a64"))

    p.append(rect(1070, 290, 260, 100, fill="#ffffff", stroke="#388e3c", sw=1.5, rx=4))
    p.append(text(1200, 315, "Вузол app2 (Листок)", size=14, bold=True))
    p.append(text(1200, 340, "cpu.max = \"100000 100000\"", size=12, color="#455a64"))
    p.append(text(1200, 365, "memory.max = \"2147483648\"", size=12, color="#455a64"))

    # Зв'язки до процесів
    p.append(line(910, 390, 910, 425, color="#2e7d32", sw=1.5))
    p.append(rect(790, 425, 240, 50, fill="#fff3e0", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(910, 455, "Process P1 (PID 4012)", size=13, bold=True, color="#e65100"))

    p.append(line(1200, 390, 1200, 425, color="#2e7d32", sw=1.5))
    p.append(rect(1080, 425, 240, 50, fill="#fff3e0", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(1200, 455, "Process P2 (PID 5190)", size=13, bold=True, color="#e65100"))

    # Перевага v2
    p.append(fitbox(770, 495, 570, 110,
                    "✔ Перевага cgroup v2:\n"
                    "  Усі контролери (CPU, Memory, I/O) бачать однакову ієрархію.\n"
                    "  I/O Writeback tracking точно знає джерело сторінок пам'яті.\n"
                    "  Повна узгодженість OOM-killer та обліку ресурсів.",
                    size=13, fill="#ffffff", stroke="#388e3c", color="#1b5e20"))

    render(os.path.join(IMG, 'cgroupfs-v1-vs-v2-tree.svg'), W, H, *p)


def fig_cgroupfs_v2_no_internal_process_rule():
    """Ілюстрація правила відсутності внутрішніх процесів (No Internal Processes Rule)."""
    W, H = 1400, 580
    p = []

    p.append(rect(20, 20, 1360, 540, fill="#fdfdfd", stroke="#cfd8dc", sw=1.5, rx=8))

    # Ліва частина: Неприпустима конфігурація (Помилка)
    p.append(rect(40, 40, 640, 500, fill=RED, stroke="#e57373", sw=1.5, rx=6))
    p.append(text(360, 75, "НЕПРИПУСТИМА КОНФІГУРАЦІЯ (Помилка EBUSY)", size=16, bold=True, color="#c62828"))

    # Батьківський вузол з процесом та контролерами
    p.append(rect(110, 105, 500, 110, fill="#ffffff", stroke="#d32f2f", sw=2, rx=6))
    p.append(text(360, 135, "Вузол /sys/fs/cgroup/parent_node", size=15, bold=True))
    p.append(text(360, 165, "cgroup.subtree_control = \"+cpu +memory\"", size=13, color="#c62828", bold=True))
    p.append(text(360, 195, "cgroup.procs = [PID 1024]  <-- ВНУТРІШНІЙ ПРОЦЕС!", size=13, color="#d32f2f", bold=True))

    p.append(line(260, 215, 210, 265, color="#d32f2f", sw=2))
    p.append(line(460, 215, 510, 265, color="#d32f2f", sw=2))

    # Дочірній вузол A
    p.append(rect(80, 265, 260, 80, fill="#ffffff", stroke="#d32f2f", sw=1.5, rx=4))
    p.append(text(210, 295, "Дочірній child_A", size=14, bold=True))
    p.append(text(210, 325, "cgroup.procs = [PID 2048]", size=12, color="#555555"))

    # Дочірній вузол B
    p.append(rect(380, 265, 260, 80, fill="#ffffff", stroke="#d32f2f", sw=1.5, rx=4))
    p.append(text(510, 295, "Дочірній child_B", size=14, bold=True))
    p.append(text(510, 325, "cgroup.procs = [PID 3096]", size=12, color="#555555"))

    # Пояснення помилки
    p.append(fitbox(60, 365, 600, 155,
                    "❌ Чому це заборонено:\n"
                    "Якщо parent_node має власні процеси у cgroup.procs І одночасно\n"
                    "розподіляє ресурси між child_A та child_B через subtree_control,\n"
                    "виникає невизначеність: як планувальник CPU чи memory-reclaim має\n"
                    "ділити ресурс між безпосереднім PID 1024 та цілою групою child_A?\n"
                    "Ядро блокує такий запис і повертає помилку EBUSY.",
                    size=13, fill="#ffffff", stroke="#d32f2f", color="#b71c1c"))

    # Права частина: Правильна конфігурація (Вірно)
    p.append(rect(720, 40, 640, 500, fill=GREEN, stroke="#81c784", sw=1.5, rx=6))
    p.append(text(1040, 75, "ПРАВИЛЬНА КОНФІГУРАЦІЯ (Лише листки)", size=16, bold=True, color="#1b5e20"))

    # Батьківський вузол без процесів
    p.append(rect(790, 105, 500, 95, fill="#ffffff", stroke="#2e7d32", sw=2, rx=6))
    p.append(text(1040, 135, "Вузол /sys/fs/cgroup/parent_node", size=15, bold=True))
    p.append(text(1040, 162, "cgroup.subtree_control = \"+cpu +memory\"", size=13, color="#2e7d32", bold=True))
    p.append(text(1040, 185, "cgroup.procs = порожньо (0 процесів)", size=13, color="#388e3c", italic=True))

    p.append(line(910, 200, 840, 265, color="#2e7d32", sw=2))
    p.append(line(1040, 200, 1040, 265, color="#2e7d32", sw=2))
    p.append(line(1170, 200, 1240, 265, color="#2e7d32", sw=2))

    # Виділена cgroup для внутрішньої служби
    p.append(rect(740, 265, 200, 80, fill="#ffffff", stroke="#2e7d32", sw=1.5, rx=4))
    p.append(text(840, 295, "Листок leaf_main", size=14, bold=True))
    p.append(text(840, 325, "PID 1024", size=13, color="#e65100", bold=True))

    p.append(rect(960, 265, 180, 80, fill="#ffffff", stroke="#2e7d32", sw=1.5, rx=4))
    p.append(text(1050, 295, "Листок child_A", size=14, bold=True))
    p.append(text(1050, 325, "PID 2048", size=13, color="#e65100", bold=True))

    p.append(rect(1160, 265, 180, 80, fill="#ffffff", stroke="#2e7d32", sw=1.5, rx=4))
    p.append(text(1250, 295, "Листок child_B", size=14, bold=True))
    p.append(text(1250, 325, "PID 3096", size=13, color="#e65100", bold=True))

    # Пояснення рішення
    p.append(fitbox(740, 365, 600, 155,
                    "✔ Чому це працює коректно:\n"
                    "Всі процеси розташовані виключно у листкових вузлах (leaf nodes).\n"
                    "Процес PID 1024 винесено у власну cgroup leaf_main.\n"
                    "Батьківський вузол виступає виключно як контролер ієрархії.\n"
                    "Арбітраж ресурсів між leaf_main, child_A та child_B виконується\n"
                    "математично строго та без деградації продуктивності.",
                    size=13, fill="#ffffff", stroke="#388e3c", color="#1b5e20"))

    render(os.path.join(IMG, 'cgroupfs-v2-no-internal-process-rule.svg'), W, H, *p)


def fig_cgroupfs_kernel_vfs_kernfs():
    """Внутрішня архітектура ядра Linux: VFS, kernfs, task_struct, css_set та cgroup."""
    W, H = 1420, 680
    p = []

    p.append(rect(20, 20, 1380, 640, fill="#f8f9fa", stroke="#b0bec5", sw=1.5, rx=8))
    p.append(text(60, 55, "Простір користувача (User Space)", size=16, bold=True, color="#37474f"))

    # User space interaction
    p.append(rect(60, 75, 410, 85, fill="#ffffff", stroke="#1565c0", sw=2, rx=6))
    p.append(text(265, 105, "Системний виклик користувача", size=15, bold=True))
    p.append(text(265, 135, "mkdir /sys/fs/cgroup/app | echo PID > cgroup.procs", size=13, italic=True, color="#455a64"))

    # Boundary
    p.append(line(30, 180, 1390, 180, color="#d32f2f", dash="6 4", sw=2))
    p.append(text(60, 205, "Простір ядра (Kernel Space)", size=16, bold=True, color="#c62828"))

    # VFS & kernfs layer
    p.append(rect(60, 230, 410, 410, fill=BLUE, stroke="#1976d2", sw=2, rx=6))
    p.append(text(265, 265, "Віртуальна ФС (VFS) & kernfs", size=16, bold=True, color="#0d47a1"))

    p.append(rect(80, 295, 370, 70, fill="#ffffff", stroke="#1565c0", sw=1.5, rx=4))
    p.append(text(265, 325, "struct file_system_type (cgroup2_fs_type)", size=13, bold=True))
    p.append(text(265, 350, "mount -t cgroup2 none /sys/fs/cgroup", size=12, color="#555555"))

    p.append(rect(80, 385, 370, 70, fill="#ffffff", stroke="#1565c0", sw=1.5, rx=4))
    p.append(text(265, 415, "struct kernfs_node", size=14, bold=True))
    p.append(text(265, 440, "Абстракція ієрархії псевдофайлів у RAM", size=12, color="#555555"))

    p.append(rect(80, 475, 370, 140, fill="#ffffff", stroke="#1565c0", sw=1.5, rx=4))
    p.append(text(265, 505, "Мости cgroupfs у ядрі", size=14, bold=True))
    p.append(text(265, 535, "cgroup_mkdir() -> cgroup_create()", size=12, color="#37474f"))
    p.append(text(265, 565, "cgroup_procs_write() -> cgroup_attach_task()", size=12, color="#37474f"))
    p.append(text(265, 595, "kernfs_notify() -> POLLPRI на cgroup.events", size=12, color="#37474f"))

    # Core Kernel Task & Cgroup Data Structures
    p.append(rect(510, 230, 430, 410, fill=WARM, stroke="#f57c00", sw=2, rx=6))
    p.append(text(725, 265, "Ядро: Структури процесів та груп", size=16, bold=True, color="#e65100"))

    p.append(rect(530, 295, 390, 80, fill="#ffffff", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(725, 325, "struct task_struct (PID 4012)", size=14, bold=True))
    p.append(text(725, 355, "struct css_set *cgroups;  <-- Покажчик на CSS-сет", size=12, color="#d32f2f", bold=True))

    p.append(line(725, 375, 725, 405, color="#f57c00", sw=2))

    p.append(rect(530, 405, 390, 95, fill="#ffffff", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(725, 432, "struct css_set (Cgroup Subsystem State Set)", size=13, bold=True))
    p.append(text(725, 458, "refcount = 4 (Дедуплікований об'єкт)", size=12, color="#388e3c", bold=True))
    p.append(text(725, 482, "struct cgroup_subsys_state *subsys[CGROUP_SUBSYS_COUNT]", size=11, color="#555555"))

    p.append(line(725, 500, 725, 525, color="#f57c00", sw=2))

    p.append(rect(530, 525, 390, 95, fill="#ffffff", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(725, 552, "struct cgroup (Об'єкт вузла в ядрі)", size=14, bold=True))
    p.append(text(725, 578, "self (cgroup_subsys_state), subtree_control, nr_descendants", size=11, color="#555555"))
    p.append(text(725, 600, "flags (CGRP_FREEZE, CGRP_FROZEN, CGRP_KILL)", size=11, color="#555555"))

    # Subsystem Resource Controllers
    p.append(rect(970, 230, 410, 410, fill=GREEN, stroke="#2e7d32", sw=2, rx=6))
    p.append(text(1175, 265, "Підсистеми контролерів ресурсів", size=16, bold=True, color="#1b5e20"))

    p.append(rect(990, 295, 370, 95, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1175, 325, "cpu_cgrp_subsys (CPU Controller)", size=14, bold=True, color="#2e7d32"))
    p.append(text(1175, 355, "struct task_group (CFS bandwidth quota/period)", size=12, color="#555555"))
    p.append(text(1175, 377, "tg->shares, tg->cfs_bandwidth", size=11, color="#777777"))

    p.append(rect(990, 405, 370, 95, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1175, 435, "mem_cgrp_subsys (Memory Controller)", size=14, bold=True, color="#2e7d32"))
    p.append(text(1175, 465, "struct mem_cgroup (high, max, low, min)", size=12, color="#555555"))
    p.append(text(1175, 487, "page_counter (memory & swap accounting)", size=11, color="#777777"))

    p.append(rect(990, 515, 370, 105, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=4))
    p.append(text(1175, 542, "io_cgrp_subsys (Block I/O Controller)", size=14, bold=True, color="#2e7d32"))
    p.append(text(1175, 570, "struct io_cq / blkcg (Writeback tracking)", size=12, color="#555555"))
    p.append(text(1175, 595, "bfq / throtl (rbps, wbps, iops limits)", size=11, color="#777777"))

    render(os.path.join(IMG, 'cgroupfs-kernel-vfs-kernfs.svg'), W, H, *p)


if __name__ == '__main__':
    fig_cgroupfs_v1_vs_v2_tree()
    fig_cgroupfs_v2_no_internal_process_rule()
    fig_cgroupfs_kernel_vfs_kernfs()
    print("Figures generated successfully.")
