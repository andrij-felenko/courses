# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Один інтерфейс на файл, сокет і пристрій'."""

import sys, os

# 4 рівні вгору до кореня, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_vfs_dispatch():
    """Схема поліморфної диспетчеризації викликів read/write через VFS."""
    w, h = 960, 560
    frags = []

    # Рівень 1: Простір користувача (syscalls)
    frags.append(rect(30, 20, 900, 75, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(480, 42, "ПРОСТІР КОРИСТУВАЧА: ЄДИНИЙ СИСТЕМНИЙ ВИКЛИК", size=13, color="#475569", bold=True))
    frags.append(textbox(170, 68, "read(3, buf, 4096)", size=13, pad=6, fill="#ffffff", stroke="#0284c7", bold=True)[0])
    frags.append(textbox(380, 68, "read(4, buf, 4096)", size=13, pad=6, fill="#ffffff", stroke="#0284c7", bold=True)[0])
    frags.append(textbox(590, 68, "read(5, buf, 4096)", size=13, pad=6, fill="#ffffff", stroke="#0284c7", bold=True)[0])
    frags.append(textbox(800, 68, "read(6, buf, 4096)", size=13, pad=6, fill="#ffffff", stroke="#0284c7", bold=True)[0])

    # Стрілки вхід у ядро
    for x in [170, 380, 590, 800]:
        frags.append(arrow(x, 95, x, 135, color="#0284c7", sw=1.8))
    frags.append(text(480, 120, "sys_read(fd, buf, count) → перехід у простір ядра", size=12, color="#0369a1", bold=True))

    # Рівень 2: Таблиця дескрипторів процесу
    frags.append(rect(30, 140, 900, 95, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(480, 160, "ТАБЛИЦЯ ДЕСКРИПТОРІВ ПРОЦЕСУ (files_struct → fdtable)", size=13, color="#334155", bold=True))
    frags.append(textbox(170, 195, "fd 3 → struct file*", size=12, pad=6, fill="#ffffff", stroke="#475569", bold=True)[0])
    frags.append(textbox(380, 195, "fd 4 → struct file*", size=12, pad=6, fill="#ffffff", stroke="#475569", bold=True)[0])
    frags.append(textbox(590, 195, "fd 5 → struct file*", size=12, pad=6, fill="#ffffff", stroke="#475569", bold=True)[0])
    frags.append(textbox(800, 195, "fd 6 → struct file*", size=12, pad=6, fill="#ffffff", stroke="#475569", bold=True)[0])

    # Стрілки до struct file
    for x in [170, 380, 590, 800]:
        frags.append(arrow(x, 235, x, 275, color="#475569", sw=1.8))

    # Рівень 3: Описи відкритих файлів і покажчик f_op
    frags.append(rect(30, 280, 900, 110, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(480, 302, "ОПИСИ ВІДКРИТИХ ФАЙЛІВ (struct file) ТА ДИСПЕТЧЕРИЗАЦІЯ ЧЕРЕЗ f_op", size=13, color="#166534", bold=True))
    
    frags.append(fitbox(70, 318, 200, 62, "struct file (диск)\nf_pos = 122880\nf_op = &ext4_file_ops", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(fitbox(280, 318, 200, 62, "struct file (мережевий)\nf_pos = 0 (ігнор)\nf_op = &socket_file_ops", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(fitbox(490, 318, 200, 62, "struct file (канал)\nf_pos = 0 (ігнор)\nf_op = &pipefifo_fops", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(fitbox(700, 318, 200, 62, "struct file (драйвер)\nf_pos = 0\nf_op = &tty_fops", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))

    # Стрілки динамічного виклику (поліморфізм f_op->read_iter)
    for x in [170, 380, 590, 800]:
        frags.append(arrow(x, 390, x, 435, color="#16a34a", sw=1.8))
    frags.append(text(480, 418, "прямий виклик: file->f_op->read_iter(iocb, to)  [жодного if/switch за типом!]", size=12, color="#15803d", bold=True))

    # Рівень 4: Спеціалізовані підсистеми ядра
    frags.append(rect(30, 440, 900, 100, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(480, 460, "КОНКРЕТНІ РЕАЛІЗАЦІЇ ОБРОБНИКІВ У ПІДСИСТЕМАХ ЯДРА", size=13, color="#991b1b", bold=True))

    frags.append(fitbox(60, 474, 210, 56, "ext4_file_read_iter()\nКеш сторінок → NVMe/SATA\nЧитання блоків з диска", size=11, pad=5, fill="#ffffff", stroke="#dc2626"))
    frags.append(fitbox(278, 474, 210, 56, "sock_read_iter()\nstruct socket → TCP/UDP\nЧерга вхідних мережевих пакетів", size=11, pad=5, fill="#ffffff", stroke="#dc2626"))
    frags.append(fitbox(496, 474, 210, 56, "pipe_read()\nstruct pipe_inode_info\nКільцевий буфер сторінок у RAM", size=11, pad=5, fill="#ffffff", stroke="#dc2626"))
    frags.append(fitbox(714, 474, 210, 56, "tty_read() / uart_read()\nБуфер TTY line discipline\nРегістри апаратного UART/USB", size=11, pad=5, fill="#ffffff", stroke="#dc2626"))

    render(os.path.join(OUT_DIR, "vfs-polymorphism-dispatch.svg"), w, h, *frags)


def fig_struct_specialization():
    """Схема зв'язку struct file та struct inode зі спеціалізованими структурами ядра."""
    w, h = 960, 480
    frags = []

    # Верхній спільний поверх VFS
    frags.append(rect(40, 20, 880, 100, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(480, 42, "СПІЛЬНЕ ЯДРО VFS: ОПИС ВІДКРИТТЯ ТА ВУЗОЛ МЕТАДАНИХ", size=14, color="#1e40af", bold=True))
    
    frags.append(fitbox(140, 54, 300, 54, "struct file (опис відкриття)\nf_pos | f_flags | f_count | f_op", size=12, pad=6, fill="#ffffff", stroke="#3b82f6", bold=True))
    frags.append(fitbox(520, 54, 300, 54, "struct inode (об'єкт ядра)\ni_mode (тип/права) | i_rdev | i_op", size=12, pad=6, fill="#ffffff", stroke="#3b82f6", bold=True))
    frags.append(arrow(440, 81, 520, 81, color="#2563eb", sw=1.8))
    frags.append(text(480, 74, "f_inode", size=11, color="#1d4ed8", bold=True))

    # Вертикальні стрілки спеціалізації
    frags.append(arrow(180, 120, 130, 175, color="#475569", sw=1.8))
    frags.append(arrow(380, 120, 360, 175, color="#475569", sw=1.8))
    frags.append(arrow(580, 120, 600, 175, color="#475569", sw=1.8))
    frags.append(arrow(780, 120, 830, 175, color="#475569", sw=1.8))

    # Чотири спеціалізовані підсистеми
    # 1. Регулярний файл
    frags.append(rect(30, 180, 210, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(135, 205, "РЕГУЛЯРНИЙ ФАЙЛ", size=12, color="#0f172a", bold=True))
    frags.append(fitbox(45, 220, 180, 48, "inode->i_mapping\nstruct address_space", size=11, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(arrow(135, 268, 135, 290, color="#64748b", sw=1.5))
    frags.append(fitbox(45, 290, 180, 48, "Кеш сторінок (page cache)\nradix tree / xarray", size=11, pad=4, fill="#ffffff", stroke="#64748b"))
    frags.append(arrow(135, 338, 135, 360, color="#64748b", sw=1.5))
    frags.append(fitbox(45, 360, 180, 75, "Драйвер ФС (Ext4/XFS)\nБлоковий шар\nФізичний SSD / HDD", size=11, pad=4, fill="#f1f5f9", stroke="#475569"))

    # 2. Мережевий сокет
    frags.append(rect(255, 180, 210, 270, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))
    frags.append(text(360, 205, "МЕРЕЖЕВИЙ СОКЕТ", size=12, color="#14532d", bold=True))
    frags.append(fitbox(270, 220, 180, 48, "SOCKET_I(inode)\nstruct socket (VFS-міст)", size=11, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(arrow(360, 268, 360, 290, color="#22c55e", sw=1.5))
    frags.append(fitbox(270, 290, 180, 48, "struct sock (мережеве ядро)\nsk_receive_queue (sk_buff)", size=11, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(arrow(360, 338, 360, 360, color="#22c55e", sw=1.5))
    frags.append(fitbox(270, 360, 180, 75, "Протокольні операції\nTCP / UDP / IP стек\nМережева карта (NIC)", size=11, pad=4, fill="#f0fdf4", stroke="#15803d"))

    # 3. Анонімний канал (pipe)
    frags.append(rect(480, 180, 210, 270, fill="#fefce8", stroke="#fef08a", sw=1.5, rx=8))
    frags.append(text(585, 205, "АНОНІМНИЙ КАНАЛ", size=12, color="#713f12", bold=True))
    frags.append(fitbox(495, 220, 180, 48, "inode->i_pipe\nstruct pipe_inode_info", size=11, pad=4, fill="#ffffff", stroke="#eab308"))
    frags.append(arrow(585, 268, 585, 290, color="#eab308", sw=1.5))
    frags.append(fitbox(495, 290, 180, 48, "pipe_buffer[16]\nКільце сторінок у RAM", size=11, pad=4, fill="#ffffff", stroke="#eab308"))
    frags.append(arrow(585, 338, 585, 360, color="#eab308", sw=1.5))
    frags.append(fitbox(495, 360, 180, 75, "Черги очікування:\npipe->rd_wait\npipe->wr_wait", size=11, pad=4, fill="#fefce8", stroke="#a16207"))

    # 4. Символьний пристрій
    frags.append(rect(705, 180, 225, 270, fill="#faf5ff", stroke="#e9d5ff", sw=1.5, rx=8))
    frags.append(text(817, 205, "СИМВОЛЬНИЙ ПРИСТРІЙ", size=12, color="#581c87", bold=True))
    frags.append(fitbox(720, 220, 195, 48, "inode->i_cdev / i_rdev\nstruct cdev (major:minor)", size=11, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(arrow(817, 268, 817, 290, color="#a855f7", sw=1.5))
    frags.append(fitbox(720, 290, 195, 48, "cdev->ops (file_operations)\nДрайвер заліза", size=11, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(arrow(817, 338, 817, 360, color="#a855f7", sw=1.5))
    frags.append(fitbox(720, 360, 195, 75, "Буфери пристрою / MMIO\nПереривання (IRQ) / DMA\nАпаратний контролер", size=11, pad=4, fill="#faf5ff", stroke="#7e22ce"))

    render(os.path.join(OUT_DIR, "file-struct-specialization.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_vfs_dispatch()
    fig_struct_specialization()
    print("OK: generated figures for one-interface-many-things")
