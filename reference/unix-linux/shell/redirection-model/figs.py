# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_fd_table_kernel_structure():
    W, H = 860, 420
    p = []
    
    # Заголовок фігури
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 25, "Структура дескрипторів процесу та системні об'єкти відкритих файлів", size=16, color=INK, bold=True))
    
    # Стовпець 1: Таблиця дескрипторів процесу (Process FD Table)
    px1, py1, pw1, ph1 = 30, 60, 240, 330
    p.append(rect(px1, py1, pw1, ph1, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(px1 + pw1 / 2, py1 + 25, "Таблиця FD (task_struct)", size=13, color=INK, bold=True))
    
    fd_labels = [
        ("FD 0 (stdin)", "#e2e8f0", INK),
        ("FD 1 (stdout)", "#dbeafe", NEG),
        ("FD 2 (stderr)", "#dbeafe", NEG),
        ("FD 3 (file fd)", "#fef3c7", POS),
        ("FD 4 (pipe rd)", "#dcfce7", FIELD)
    ]
    
    fd_y_positions = []
    for i, (label, fill_col, text_col) in enumerate(fd_labels):
        ey = py1 + 50 + i * 52
        p.append(rect(px1 + 15, ey, pw1 - 30, 42, fill=fill_col, stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(px1 + pw1 / 2, ey + 25, label, size=12, color=text_col, bold=True))
        fd_y_positions.append(ey + 21)

    # Стовпець 2: Системна таблиця відкритих файлів (Open File Description Table)
    px2, py2, pw2, ph2 = 330, 60, 260, 330
    p.append(rect(px2, py2, pw2, ph2, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(px2 + pw2 / 2, py2 + 25, "Відкриті файли (struct file)", size=13, color=INK, bold=True))

    ofd_entries = [
        ("struct file: /dev/pts/1\n[f_pos=1024, f_flags=O_RDWR]", "#f1f5f9", py1 + 50),
        ("struct file: output.txt\n[f_pos=0, f_flags=O_WRONLY]", "#fef3c7", py1 + 154),
        ("struct file: pipe:[3421]\n[f_pos=0, f_flags=O_RDONLY]", "#dcfce7", py1 + 258)
    ]
    
    ofd_y_positions = []
    for label, fill_col, ey in ofd_entries:
        p.append(rect(px2 + 15, ey, pw2 - 30, 58, fill=fill_col, stroke="#cbd5e1", sw=1.2, rx=5))
        lines = label.split('\n')
        p.append(text(px2 + pw2 / 2, ey + 22, lines[0], size=11.5, color=INK, bold=True))
        p.append(text(px2 + pw2 / 2, ey + 42, lines[1], size=10, color=MUTED, bold=False))
        ofd_y_positions.append(ey + 29)

    # Стовпець 3: Іноди VFS (Inodes / VFS)
    px3, py3, pw3, ph3 = 650, 60, 180, 330
    p.append(rect(px3, py3, pw3, ph3, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(px3 + pw3 / 2, py3 + 25, "Іноди (struct inode)", size=13, color=INK, bold=True))

    inode_entries = [
        ("chrdev: /dev/pts/1", py1 + 50),
        ("ext4: inode #4092", py1 + 154),
        ("fifo/pipe: inode #3421", py1 + 258)
    ]
    
    inode_y_positions = []
    for label, ey in inode_entries:
        p.append(rect(px3 + 12, ey, pw3 - 24, 58, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(px3 + pw3 / 2, ey + 33, label, size=11, color=INK, bold=True))
        inode_y_positions.append(ey + 29)

    # Вказівники між FD та struct file
    # FD 0 -> /dev/pts/1
    p.append(arrow(px1 + pw1 - 15, fd_y_positions[0], px2 + 15, ofd_y_positions[0], color=INK, sw=1.5))
    # FD 1 -> output.txt (після dup2(3, 1))
    p.append(arrow(px1 + pw1 - 15, fd_y_positions[1], px2 + 15, ofd_y_positions[1], color=POS, sw=2.0))
    # FD 2 -> /dev/pts/1
    p.append(arrow(px1 + pw1 - 15, fd_y_positions[2], px2 + 15, ofd_y_positions[0], color=INK, sw=1.5))
    # FD 3 -> output.txt
    p.append(arrow(px1 + pw1 - 15, fd_y_positions[3], px2 + 15, ofd_y_positions[1], color=POS, sw=1.5))
    # FD 4 -> pipe:[3421]
    p.append(arrow(px1 + pw1 - 15, fd_y_positions[4], px2 + 15, ofd_y_positions[2], color=FIELD, sw=1.5))

    # Вказівники між struct file та inode
    p.append(arrow(px2 + pw2 - 15, ofd_y_positions[0], px3 + 12, inode_y_positions[0], color=INK, sw=1.5))
    p.append(arrow(px2 + pw2 - 15, ofd_y_positions[1], px3 + 12, inode_y_positions[1], color=POS, sw=1.5))
    p.append(arrow(px2 + pw2 - 15, ofd_y_positions[2], px3 + 12, inode_y_positions[2], color=FIELD, sw=1.5))

    render(os.path.join(OUT, "fd-table-kernel-structure.svg"), W, H, *p,
           title="Морфологія файлових дескрипторів та ядерних таблиць")

def fig_redirection_fork_exec_flow():
    W, H = 880, 440
    p = []
    
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 25, "Конвеєр системних викликів під час перенаправлення оболонкою", size=16, color=INK, bold=True))
    
    steps = [
        ("1. fork()", "Оболонка створює новий процес.\nДочірній процес успадковує\nтаблицю дескрипторів 0, 1, 2.", 30, "#e2e8f0", INK),
        ("2. open(\"out.txt\")", "Відкриття цільового файлу.\nОС повертає найменший\nвільний дескриптор (FD 3).", 240, "#fef3c7", POS),
        ("3. dup2(3, 1)", "Перенаправлення stdout.\nДескриптор 1 перевизначається\nна об'єкт файлу FD 3.", 450, "#dbeafe", NEG),
        ("4. close(3) + execve()", "Закриття зайвого FD 3.\nЗаміна образу процесу.\nПрограма пише у FD 1.", 660, "#dcfce7", FIELD)
    ]
    
    box_w = 190
    box_h = 320
    py = 65
    
    for i, (title, desc, px, bg_col, border_col) in enumerate(steps):
        p.append(rect(px, py, box_w, box_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(px + box_w / 2, py + 28, title, size=13, color=INK, bold=True))
        
        # Опис кроку
        lines = desc.split('\n')
        for j, line_txt in enumerate(lines):
            p.append(text(px + box_w / 2, py + 60 + j * 20, line_txt, size=10.5, color=INK, bold=False))

        # Схема стан дескрипторів на цьому кроці
        fds_box_y = py + 140
        p.append(rect(px + 15, fds_box_y, box_w - 30, 160, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(px + box_w / 2, fds_box_y + 20, "Стан дескрипторів:", size=11, color=MUTED, bold=True))
        
        if i == 0:
            fd_state = [("0: tty", INK), ("1: tty", INK), ("2: tty", INK)]
        elif i == 1:
            fd_state = [("0: tty", INK), ("1: tty", INK), ("2: tty", INK), ("3: out.txt", POS)]
        elif i == 2:
            fd_state = [("0: tty", INK), ("1: out.txt", POS), ("2: tty", INK), ("3: out.txt", MUTED)]
        else:
            fd_state = [("0: tty", INK), ("1: out.txt", POS), ("2: tty", INK)]

        for k, (fd_t, col) in enumerate(fd_state):
            p.append(text(px + box_w / 2, fds_box_y + 45 + k * 28, fd_t, size=11.5, color=col, bold=True))

        if i < len(steps) - 1:
            # Стрілка переходу
            p.append(arrow(px + box_w + 3, py + box_h / 2, px + box_w + 17, py + box_h / 2, color=INK, sw=2.0))

    render(os.path.join(OUT, "redirection-fork-exec-flow.svg"), W, H, *p,
           title="Послідовність системних викликів при виконанні перенаправлення")

if __name__ == '__main__':
    fig_fd_table_kernel_structure()
    fig_redirection_fork_exec_flow()
