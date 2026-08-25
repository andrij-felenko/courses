# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми close-on-exec."""

import os
import sys

# Підключаємо svgkit з кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_fork_exec_lifecycle():
    """Ілюстрація життєвого циклу дескрипторів при fork та execve з FD_CLOEXEC."""
    w, h = 860, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Успадкування файлових дескрипторів: fork() та execve()", size=16, bold=True))

    # Стовпчик 1: Батьківський процес
    bx, by, bw, bh = 40, 60, 240, 390
    frags.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(bx + bw / 2, by + 28, "Батьківський процес", size=14, bold=True))
    frags.append(text(bx + bw / 2, by + 46, "PID 1000 (таблиця fd)", size=12, color=MUTED))

    # Таблиця fd батька
    rows_parent = [
        ("fd 0, 1, 2", "stdio (термінал)", "CLOEXEC = 0", "#e2e8f0", INK),
        ("fd 3", "key.pem (секрет)", "CLOEXEC = 1", "#fef3c7", POS),
        ("fd 4", "socket (порт 443)", "CLOEXEC = 0", "#fee2e2", POS),
        ("fd 5", "access.log", "CLOEXEC = 1", "#fef3c7", POS),
    ]
    for i, (fd_name, desc, flag, bg_color, flag_color) in enumerate(rows_parent):
        ry = by + 70 + i * 72
        frags.append(rect(bx + 12, ry, bw - 24, 62, fill=bg_color, stroke="#cbd5e1", sw=1.2, rx=4))
        frags.append(text(bx + 22, ry + 22, fd_name, size=13, bold=True, anchor="start"))
        frags.append(text(bx + 22, ry + 42, desc, size=11, color=MUTED, anchor="start"))
        frags.append(text(bx + bw - 22, ry + 32, flag, size=11, bold=True, color=flag_color, anchor="end"))

    # Стрілка fork()
    frags.append(arrow(285, 230, 335, 230, color=LINE, sw=2))
    frags.append(text(310, 215, "fork()", size=13, bold=True))
    frags.append(text(310, 250, "копіює", size=11, color=MUTED))

    # Стовпчик 2: Дочірній процес після fork()
    cx, cy, cw, ch = 340, 60, 240, 390
    frags.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(cx + cw / 2, by + 28, "Дитина після fork()", size=14, bold=True))
    frags.append(text(cx + cw / 2, by + 46, "PID 1001 (точна копія)", size=12, color=MUTED))

    rows_child_fork = [
        ("fd 0, 1, 2", "stdio (термінал)", "CLOEXEC = 0", "#e2e8f0", INK),
        ("fd 3", "key.pem (секрет)", "CLOEXEC = 1", "#fef3c7", POS),
        ("fd 4", "socket (порт 443)", "CLOEXEC = 0", "#fee2e2", POS),
        ("fd 5", "access.log", "CLOEXEC = 1", "#fef3c7", POS),
    ]
    for i, (fd_name, desc, flag, bg_color, flag_color) in enumerate(rows_child_fork):
        ry = cy + 70 + i * 72
        frags.append(rect(cx + 12, ry, cw - 24, 62, fill=bg_color, stroke="#cbd5e1", sw=1.2, rx=4))
        frags.append(text(cx + 22, ry + 22, fd_name, size=13, bold=True, anchor="start"))
        frags.append(text(cx + 22, ry + 42, desc, size=11, color=MUTED, anchor="start"))
        frags.append(text(cx + cw - 22, ry + 32, flag, size=11, bold=True, color=flag_color, anchor="end"))

    # Стрілка execve()
    frags.append(arrow(585, 230, 635, 230, color=LINE, sw=2))
    frags.append(text(610, 215, "execve()", size=13, bold=True))
    frags.append(text(610, 250, "образ", size=11, color=MUTED))

    # Стовпчик 3: Дочірній процес після execve()
    ex, ey, ew, eh = 640, 60, 180, 390
    frags.append(rect(ex, ey, ew, eh, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(ex + ew / 2, by + 28, "Нова програма", size=14, bold=True))
    frags.append(text(ex + ew / 2, by + 46, "PID 1001 (/bin/helper)", size=12, color=MUTED))

    rows_child_exec = [
        ("fd 0, 1, 2", "stdio успадковано", "#dcfce7", FIELD),
        ("fd 3 [зачинено]", "flush_old_files()", "#f1f5f9", MUTED),
        ("fd 4 [ВИТІК!]", "сокет лишився відкритим", "#fee2e2", POS),
        ("fd 5 [зачинено]", "flush_old_files()", "#f1f5f9", MUTED),
    ]
    for i, (fd_name, state_desc, bg_color, state_color) in enumerate(rows_child_exec):
        ry = ey + 70 + i * 72
        frags.append(rect(ex + 10, ry, ew - 20, 62, fill=bg_color, stroke="#cbd5e1", sw=1.2, rx=4))
        frags.append(text(ex + 16, ry + 24, fd_name, size=12, bold=True, color=state_color, anchor="start"))
        frags.append(text(ex + 16, ry + 44, state_desc, size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG_DIR, "fork-exec-fd-lifecycle.svg"), w, h, *frags)


def fig_kernel_fdtable():
    """Структури ядра Linux: task_struct, files_struct, fdtable та бітова маска close_on_exec."""
    w, h = 880, 460
    frags = []

    frags.append(text(w / 2, 26, "Внутрішні структури ядра: таблиця дескрипторів та маска close_on_exec", size=16, bold=True))

    # Блок 1: struct task_struct
    t_box, tw, th = textbox(130, 150, "struct task_struct\n(дескриптор процесу)\n\npid = 1420\nfiles = 0xffff8801...\nmm = 0xffff8802...", size=13, pad=12, fill="#f1f5f9", stroke="#475569")
    frags.append(t_box)

    # Стрілка від task_struct до files_struct
    frags.append(arrow(215, 150, 275, 150, color=LINE, sw=1.8))
    frags.append(text(245, 135, "files", size=12, color=MUTED))

    # Блок 2: struct files_struct
    f_box, fw, fh = textbox(370, 150, "struct files_struct\n(файловий контекст)\n\ncount (refcount) = 1\nfdt = 0xffff8803...\nfdtab (embedded)", size=13, pad=12, fill="#f1f5f9", stroke="#475569")
    frags.append(f_box)

    # Стрілка від files_struct до struct fdtable
    frags.append(arrow(465, 150, 525, 150, color=LINE, sw=1.8))
    frags.append(text(495, 135, "fdt", size=12, color=MUTED))

    # Блок 3: struct fdtable
    fdt_box, fdtw, fdth = textbox(680, 175, "struct fdtable\n(динамічна таблиця дескрипторів)\n\nmax_fds = 64\nfd = struct file** (масив вказівників)\nclose_on_exec = unsigned long*\nopen_fds = unsigned long*\nrcu = rcu_head", size=12.5, pad=12, fill="#e2e8f0", stroke="#334155")
    frags.append(fdt_box)

    # Деталізація масиву fd та бітової маски
    # Масив fd[]
    frags.append(rect(40, 290, 380, 145, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    frags.append(text(230, 314, "Масив вказівників: fd[n] -> struct file*", size=13, bold=True))

    rows_fd = [
        ("fd[0] -> struct file (stdin)", "#f1f5f9"),
        ("fd[1] -> struct file (stdout)", "#f1f5f9"),
        ("fd[3] -> struct file (key.pem)", "#fef3c7"),
        ("fd[4] -> struct file (socket:443)", "#fee2e2"),
    ]
    for i, (title_fd, bg_col) in enumerate(rows_fd):
        fy = 330 + i * 24
        frags.append(rect(52, fy, 356, 20, fill=bg_col, stroke="#cbd5e1", sw=1, rx=3))
        frags.append(text(60, fy + 14, title_fd, size=11, anchor="start"))

    # Бітова маска close_on_exec
    frags.append(rect(460, 290, 380, 145, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    frags.append(text(650, 314, "Бітова маска: close_on_exec (біт на дескриптор)", size=13, bold=True))

    bits = [
        ("біт 0 (fd 0)", "0  (успадкувати)", INK),
        ("біт 1 (fd 1)", "0  (успадкувати)", INK),
        ("біт 3 (fd 3)", "1  (ЗАКРИТИ ПРИ EXEC)", POS),
        ("біт 4 (fd 4)", "0  (успадкувати)", INK),
    ]
    for i, (bit_title, bit_val, bit_col) in enumerate(bits):
        by = 330 + i * 24
        frags.append(rect(472, by, 356, 20, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=3))
        frags.append(text(482, by + 14, bit_title, size=11, anchor="start"))
        frags.append(text(816, by + 14, bit_val, size=11, bold=True, color=bit_col, anchor="end"))

    render(os.path.join(IMG_DIR, "kernel-fdtable-layout.svg"), w, h, *frags)


def fig_multithread_race():
    """Часова діаграма стану гонитви між open()+fcntl() та fork()+execve()."""
    w, h = 860, 430
    frags = []

    frags.append(text(w / 2, 26, "Стан гонитви: неатомарний open() + fcntl() у багатопотоковій програмі", size=16, bold=True))

    # Вісь часу зліва
    frags.append(arrow(60, 70, 60, 380, color=LINE, sw=1.8))
    frags.append(text(60, 398, "Час (t)", size=12, bold=True))

    # Стовпець 1: Потік 1 (Серверний воркер)
    p1_x = 130
    frags.append(rect(p1_x, 70, 300, 300, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(p1_x + 150, 95, "Потік 1 (Відкриває файл)", size=14, bold=True))

    # Дії потоку 1
    # 1. open()
    frags.append(rect(p1_x + 15, 120, 270, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(p1_x + 25, 145, "1. fd = open(\"secret.key\", O_RDONLY)", size=12, bold=True, anchor="start"))

    # 2. Небезпечне вікно (Race Window)
    frags.append(rect(p1_x + 15, 175, 270, 95, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(p1_x + 150, 202, "НЕБЕЗПЕЧНЕ ВІКНО ГОНИТВИ", size=12, bold=True, color=POS))
    frags.append(text(p1_x + 150, 222, "(fd існує, але close_on_exec == 0)", size=11, color=POS))
    frags.append(text(p1_x + 150, 245, "дитина успадкує відкритий файл!", size=10, color=POS))

    # 3. fcntl()
    frags.append(rect(p1_x + 15, 285, 270, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(p1_x + 25, 310, "4. fcntl(fd, F_SETFD, FD_CLOEXEC)", size=12, bold=True, anchor="start"))
    frags.append(text(p1_x + 25, 350, "(пізно! дочірній процес уже створено)", size=11, color=MUTED, anchor="start"))

    # Стовпець 2: Потік 2 (Запуск зовнішньої утиліти)
    p2_x = 480
    frags.append(rect(p2_x, 70, 340, 300, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(p2_x + 170, 95, "Потік 2 (Створює підпроцес)", size=14, bold=True))

    # Дії потоку 2
    # 2. fork() потрапляє рівно у вікно
    frags.append(rect(p2_x + 15, 185, 310, 46, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(p2_x + 25, 206, "2. pid = fork()", size=12, bold=True, anchor="start"))
    frags.append(text(p2_x + 25, 222, "дитина копіює fdtable (у якій fd ще без прапорця)", size=10, color=MUTED, anchor="start"))

    # 3. execve() у дочірньому процесі
    frags.append(rect(p2_x + 15, 245, 310, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(p2_x + 25, 268, "3. [у дитині] execve(\"/bin/helper\")", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(p2_x + 25, 285, "ядро НЕ закриває fd -> секрет витік у helper!", size=10, bold=True, color=POS, anchor="start"))

    # Стрілка взаємодії (гонка)
    frags.append(arrow(p1_x + 285, 200, p2_x + 15, 200, color=POS, sw=1.8))
    frags.append(text(458, 190, "гонка", size=11, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "multithread-cloexec-race.svg"), w, h, *frags)


def fig_atomic_solutions():
    """Атомарне встановлення прапорця при відкритті та масове закриття через close_range()."""
    w, h = 860, 440
    frags = []

    frags.append(text(w / 2, 26, "Захист від витоку: атомарні системні виклики та close_range()", size=16, bold=True))

    # Ліва половина: Атомарне відкриття
    lx, ly, lw, lh = 40, 60, 370, 350
    frags.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(lx + lw / 2, ly + 28, "Атомарне створення: *_CLOEXEC", size=14, bold=True))
    frags.append(text(lx + lw / 2, ly + 46, "Вікно гонитви = 0 наносекунд", size=12, color=FIELD, bold=True))

    calls = [
        ("open(path, flags | O_CLOEXEC)", "файл створюється одразу з бітом у fdtable"),
        ("socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0)", "сокет захищено ще до повернення fd"),
        ("pipe2(pipefd, O_CLOEXEC)", "обидва кінці каналу з прапорцем"),
        ("accept4(listen_fd, ..., SOCK_CLOEXEC)", "клієнтський сокет не витече в дочірні процеси"),
        ("epoll_create1(EPOLL_CLOEXEC)", "дескриптор epoll закрито при exec"),
    ]
    for i, (fn_sig, fn_desc) in enumerate(calls):
        cy = ly + 65 + i * 54
        frags.append(rect(lx + 12, cy, lw - 24, 46, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
        frags.append(text(lx + 20, cy + 20, fn_sig, size=11, bold=True, anchor="start"))
        frags.append(text(lx + 20, cy + 36, fn_desc, size=10, color=MUTED, anchor="start"))

    # Права половина: Масове закриття та close_range
    rx, ry, rw, rh = 450, 60, 370, 350
    frags.append(rect(rx, ry, rw, rh, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(rx + rw / 2, ry + 28, "Масове очищення: close_range()", size=14, bold=True))
    frags.append(text(rx + rw / 2, ry + 46, "Один виклик на всі зайві дескриптори", size=12, color=FIELD, bold=True))

    ops = [
        ("close_range(3, ~0U, 0)", "Закриває всі fd від 3 до нескінченності", "миттєве звільнення ресурсів перед exec"),
        ("close_range(3, ~0U, CLOSE_RANGE_CLOEXEC)", "Ставить FD_CLOEXEC на діапазон [3..max]", "дескриптори працюють до самого execve"),
        ("posix_spawn_file_actions_addclose()", "Декларативне закриття у posix_spawn", "атомарний запуск без fork/exec гонитви"),
    ]
    for i, (op_sig, op_desc1, op_desc2) in enumerate(ops):
        oy = ry + 65 + i * 88
        frags.append(rect(rx + 12, oy, rw - 24, 76, fill="#e0f2fe", stroke="#7dd3fc", sw=1, rx=4))
        frags.append(text(rx + 20, oy + 22, op_sig, size=10.5, bold=True, anchor="start"))
        frags.append(text(rx + 20, oy + 42, op_desc1, size=10, color=INK, anchor="start"))
        frags.append(text(rx + 20, oy + 60, op_desc2, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG_DIR, "close-range-atomic-fix.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_fork_exec_lifecycle()
    fig_kernel_fdtable()
    fig_multithread_race()
    fig_atomic_solutions()
    print("Усі 4 фігури успішно згенеровано.")
