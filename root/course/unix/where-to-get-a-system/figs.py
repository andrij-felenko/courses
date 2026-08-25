#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми where-to-get-a-system."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_execution_environments():
    """Порівняння шарів виконання: Bare Metal, Hypervisor, WSL2, Containers, Translation."""
    w, h = 880, 480
    frags = []

    frags.append(text(w / 2, 26, "Спектр середовищ виконання: де насправді живе ядро операційної системи", size=15, bold=True))

    cols = [
        ("1. Bare Metal", "Пряме залізо", [
            ("Застосунки користувача", "#f8fafc", "#64748b"),
            ("Ядро Linux (Ring 0 / EL1)", "#eff6ff", NEG),
            ("Апаратне забезпечення", "#f1f5f9", "#334155")
        ], "100% чесне ядро,\nпрямий доступ до кілець,\nнайнижча латентність"),

        ("2. Віртуалізація (VM)", "Type-1 / Type-2", [
            ("Застосунки віртуальної машини", "#f8fafc", "#64748b"),
            ("Гостьове ядро Linux", "#eff6ff", NEG),
            ("Гіпервізор (KVM / QEMU)", "#fef3c7", "#d97706"),
            ("Апаратне забезпечення", "#f1f5f9", "#334155")
        ], "Ізольоване гостьове ядро,\nприскорення VT-x/AMD-V,\nоверхед на пам'ять"),

        ("3. WSL2 (Micro-VM)", "Hyper-V легка ВМ", [
            ("Linux CLI / Служби", "#f8fafc", "#64748b"),
            ("Оптимізоване ядро Linux", "#eff6ff", NEG),
            ("Гіпервізор Hyper-V + NT", "#fef3c7", "#d97706"),
            ("Апаратне забезпечення", "#f1f5f9", "#334155")
        ], "Справжнє модифіковане ядро,\nшвидкий запуск, міст 9P\nдо дисків Windows"),

        ("4. Контейнери", "Namespaces & Cgroups", [
            ("Ізольований процес контейнера", "#f0fdf4", FIELD),
            ("Спільне хостове ядро Linux", "#eff6ff", NEG),
            ("Апаратне забезпечення", "#f1f5f9", "#334155")
        ], "Немає другого ядра,\nізоляція просторів імен,\nнульовий оверхед"),

        ("5. Емуляція (Cygwin/WSL1)", "Трансляція API", [
            ("POSIX-застосунок (Win32)", "#fef2f2", POS),
            ("Шар трансляції (DLL/Driver)", "#fee2e2", POS),
            ("Ядро Windows NT", "#f8fafc", "#475569"),
            ("Апаратне забезпечення", "#f1f5f9", "#334155")
        ], "НЕМАЄ ядра Linux!\nЕмуляція через Win32 API,\nпастки блокувань і epoll")
    ]

    col_w = 156
    gap = 14
    left_margin = (w - (5 * col_w + 4 * gap)) / 2

    for c_idx, (title, subtitle, layers, footer) in enumerate(cols):
        x = left_margin + c_idx * (col_w + gap)

        # Картка колонки
        border_col = POS if c_idx == 4 else (FIELD if c_idx == 3 else (NEG if c_idx == 0 else "#94a3b8"))
        bg_col = "#fffbfb" if c_idx == 4 else "#ffffff"
        frags.append(rect(x, 48, col_w, 412, fill=bg_col, stroke=border_col, sw=1.5, rx=6))

        # Заголовок стовпчика
        frags.append(text(x + col_w / 2, 70, title, size=11, bold=True, color=INK))
        frags.append(text(x + col_w / 2, 85, subtitle, size=9.5, color=MUTED, italic=True))

        # Шари
        y_layer = 104
        layer_h = 56 if len(layers) == 3 else 42
        for l_title, l_fill, l_stroke in layers:
            frags.append(rect(x + 6, y_layer, col_w - 12, layer_h, fill=l_fill, stroke=l_stroke, sw=1.2, rx=4))
            frags.append(mtext(x + col_w / 2, y_layer + layer_h / 2 - 5, l_title, size=9.5, bold=True, color=INK))
            y_layer += layer_h + 5

        # Підсумок у нижній частині стовпчика
        frags.append(rect(x + 6, 310, col_w - 12, 138, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
        frags.append(mtext(x + col_w / 2, 332, footer, size=9.5, color=INK, lh=1.35))

    out_path = os.path.join(OUT_DIR, "execution-environments-layers.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_authenticity_probes():
    """Схема діагностики: як перевірити справжність Unix/Linux середовища."""
    w, h = 860, 460
    frags = []

    frags.append(text(w / 2, 28, "Діагностичне дерево: критерії автентичності ядра та середовища", size=15, bold=True))

    # Лівий блок: Точки зондування ядра
    frags.append(rect(30, 56, 380, 380, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(220, 80, "Анатомічні ознаки живого ядра Linux", size=12.5, color=NEG, bold=True))
    frags.append(text(220, 98, "Тести на рівні процесора, пам'яті та структур VFS", size=10, color=MUTED, italic=True))

    probes = [
        ("1. Інструкція SYSCALL (Ring 0)", "Прямий апаратний виклик переводить процесор у режим ядра,\nзмінюючи регістри RSP -> TSS.RSP0 без посередництва Win32."),
        ("2. Псевдофайлова система /proc", "Генерація вузлів у пам'яті на льоту: /proc/self/maps,\n/proc/version, /proc/cpuinfo, таблиці файлових дескрипторів."),
        ("3. Файлова підсистема /sys (sysfs)", "Дерево пристроїв, шин та драйверів kobject/kset:\n/sys/class, /sys/devices, інтерфейси cgroup v2."),
        ("4. Семантика POSIX unlink()", "Видалення відкритого файлу негайно прибирає dentry,\nале inode живе до закриття останнього дескриптора."),
        ("5. Дескриптори в сокетах AF_UNIX", "Передача дескрипторів через SCM_RIGHTS та нативна\nпідсистема epoll з дескрипторними чергами очікування.")
    ]

    y_p = 118
    for title, desc in probes:
        frags.append(rect(45, y_p, 350, 56, fill="#eff6ff", stroke="#93c5fd", sw=1.1, rx=5))
        frags.append(text(55, y_p + 16, title, size=10.5, bold=True, color=NEG, anchor="start"))
        frags.append(mtext(55, y_p + 31, desc, size=9, color=INK, anchor="start", lh=1.25))
        y_p += 63

    # Правий блок: Визначення середовища за маркерами
    frags.append(rect(450, 56, 380, 380, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(640, 80, "Ідентифікація типу виконання", size=12.5, color=FIELD, bold=True))
    frags.append(text(640, 98, "Маркери середовища у віртуальних таблицях і DMI", size=10, color=MUTED, italic=True))

    markers = [
        ("Bare Metal (Фізична машина)", "CPUID Hypervisor bit = 0; DMI містить виробника плати;\nвсі апаратні ядра доступні без VMCS-виходів.", "#f0fdf4", FIELD),
        ("KVM / QEMU / Cloud VPS", "CPUID Hypervisor bit = 1; підпис 'KVMKVMKVM';\nпристрої virtio-blk/virtio-net у /sys/bus/virtio.", "#f0fdf4", FIELD),
        ("WSL2 (Windows Hyper-V)", "Рядок 'microsoft-standard-WSL2' у /proc/version;\nнаявність драйвера /dev/dxg (DirectX GPU) та 9P-FS.", "#fefce8", "#ca8a04"),
        ("Docker / Podman Контейнер", "Файл /.dockerenv або маркер 'container=' у /proc/1/environ;\nізольований простір імен PID 1 та обмежені cgroups.", "#f0fdf4", FIELD),
        ("Cygwin / MSYS2 (Емуляція)", "Відсутнє ядро Linux; uname повідомляє MINGW/CYGWIN;\n/proc є статичною структурою DLL-бібліотеки.", "#fef2f2", POS)
    ]

    y_m = 118
    for title, desc, fill_c, strk_c in markers:
        frags.append(rect(465, y_m, 350, 56, fill=fill_c, stroke=strk_c, sw=1.1, rx=5))
        frags.append(text(475, y_m + 16, title, size=10.5, bold=True, color=strk_c, anchor="start"))
        frags.append(mtext(475, y_m + 31, desc, size=9, color=INK, anchor="start", lh=1.25))
        y_m += 63

    out_path = os.path.join(OUT_DIR, "authenticity-probe-pipeline.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_emulation_traps():
    """Три фундаментальні пастки емуляції: відкриті файли, fork і epoll."""
    w, h = 860, 450
    frags = []

    frags.append(text(w / 2, 26, "Пастки емуляції: чому трансляція API ламається на низькому рівні", size=15, bold=True))

    traps = [
        ("1. Семантика видалення файлів (unlink)", [
            ("Справжнє ядро POSIX / Linux:", FIELD),
            ("• Процес тримає дескриптор через open().", INK),
            ("• Інший виклик робить unlink('file.txt').", INK),
            ("• Запис у каталозі зникає негайно.", INK),
            ("• Inode і дані на диску лишаються,", INK),
            ("  доки останній процес не викличе close().", INK),
            ("Емуляція на Windows NT (WSL1/Cygwin):", POS),
            ("• Windows NT блокує видалення відкритого файлу.", INK),
            ("• Виклик повертає ERROR_SHARING_VIOLATION.", INK),
            ("• Робота баз даних (SQLite/Git) аварійно ламається.", INK)
        ]),

        ("2. Клонування процесу (fork vs NT)", [
            ("Справжнє ядро POSIX / Linux:", FIELD),
            ("• fork() дублює адресний простір миттєво", INK),
            ("  через апаратний Copy-on-Write (MMU).", INK),
            ("• Усі дескриптори та сокети зберігаються.", INK),
            ("• Дочірній процес готовий за мікросекунди.", INK),
            ("Емуляція на Windows NT (WSL1/Cygwin):", POS),
            ("• Ядро NT не має примітива fork() для процесів.", INK),
            ("• Cygwin змушений створювати CreateProcess,", INK),
            ("  зупиняти його та вручну копіювати пам'ять.", INK),
            ("• Швидкість запуску падає в десятки разів.", INK)
        ]),

        ("3. Події та передача дескрипторів", [
            ("Справжнє ядро POSIX / Linux:", FIELD),
            ("• epoll очікує на сотні тисяч дескрипторів у ядрі.", INK),
            ("• AF_UNIX передає відкриті дескриптори файлів", INK),
            ("  між процесами через керування SCM_RIGHTS.", INK),
            ("• Ядро оновлює лічильник посилань struct file.", INK),
            ("Емуляція на Windows NT (WSL1/Cygwin):", POS),
            ("• У Winsock відсутня семантика передачі файлів.", INK),
            ("• epoll емулюється через повільний select().", INK),
            ("• Служби systemd, dbus, wayland не працюють.", INK)
        ])
    ]

    col_w = 260
    gap = 16
    left_margin = (w - (3 * col_w + 2 * gap)) / 2

    for i, (title, lines) in enumerate(traps):
        x = left_margin + i * (col_w + gap)
        frags.append(rect(x, 52, col_w, 380, fill="#ffffff", stroke="#94a3b8", sw=1.4, rx=6))
        frags.append(rect(x, 52, col_w, 36, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
        frags.append(text(x + col_w / 2, 74, title, size=11, bold=True, color=INK))

        y_l = 104
        for l_txt, l_col in lines:
            bold = l_col in [FIELD, POS]
            frags.append(text(x + 12, y_l, l_txt, size=9.5, color=l_col, anchor="start", bold=bold))
            y_l += 24 if bold else 19

    out_path = os.path.join(OUT_DIR, "posix-translation-traps.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_execution_environments()
    fig_authenticity_probes()
    fig_emulation_traps()
