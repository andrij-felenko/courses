# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# ── 1. Порівняння архітектур: Системний пакунок проти OCI Контейнера ─────────
def fig_pkg_vs_container():
    W, H = 1000, 520
    frags = []

    # Тло та рамка
    frags.append(rect(15, 15, 970, 490, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(500, 45, "Архітектура розгортання: Системний пакунок проти OCI-контейнера", size=18, bold=True))

    # Ліва частина: Системний пакунок (Спільний FHS)
    frags.append(rect(35, 70, 445, 415, fill=FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(257, 98, "Системні пакунки (.deb / .rpm)", size=16, color=NEG, bold=True))
    frags.append(line(50, 112, 465, 112, color=NEG, sw=1.0))

    # Компоненти лівої частини
    # Застосунки
    frags.append(rect(55, 130, 190, 50, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(150, 153, "Застосунок А", size=13, bold=True, color=NEG))
    frags.append(text(150, 169, "/usr/bin/app-a", size=11, color=MUTED))

    frags.append(rect(270, 130, 190, 50, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(365, 153, "Застосунок Б", size=13, bold=True, color=NEG))
    frags.append(text(365, 169, "/usr/bin/app-b", size=11, color=MUTED))

    # Спільні бібліотеки
    frags.append(rect(55, 205, 405, 60, fill="#fff6e5", stroke="#b45309", sw=1.5, rx=6))
    frags.append(text(257, 230, "Спільне середовище бібліотек (/usr/lib)", size=14, bold=True, color="#b45309"))
    frags.append(text(257, 252, "glibc.so.6, libssl.so.3, libcrypto.so (Спільний Page Cache)", size=11, color=INK))

    # Спільна FHS
    frags.append(rect(55, 285, 405, 60, fill="#eaf6ef", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(257, 310, "Спільне дерево FHS (/etc, /var, /usr)", size=14, bold=True, color=FIELD))
    frags.append(text(257, 332, "Єдине глобальне середовище та конфігурації", size=11, color=INK))

    # Ядро
    frags.append(rect(55, 365, 405, 100, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(257, 395, "Хостове ядро Linux (Single Kernel)", size=15, bold=True, color=POS))
    frags.append(text(257, 420, "Системні виклики (VFS, POSIX, Memory Management)", size=12, color=INK))
    frags.append(text(257, 445, "Неізольований простір імен хоста", size=11, color=MUTED))

    # Права частина: OCI Контейнери (Ізольований rootfs)
    frags.append(rect(520, 70, 445, 415, fill=FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(742, 98, "OCI Контейнери (Docker / Podman)", size=16, color=FIELD, bold=True))
    frags.append(line(535, 112, 950, 112, color=FIELD, sw=1.0))

    # Контейнер 1
    frags.append(rect(535, 130, 200, 135, fill="#eaf6ef", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(635, 152, "Контейнер 1", size=13, bold=True, color=FIELD))
    frags.append(rect(545, 165, 180, 30, fill=BG, stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(635, 184, "Застосунок А", size=11, bold=True))
    frags.append(rect(545, 200, 180, 55, fill="#fff6e5", stroke="#b45309", sw=1.0, rx=4))
    frags.append(text(635, 220, "Власний rootfs (v1.1)", size=11, bold=True, color="#b45309"))
    frags.append(text(635, 240, "glibc 2.31 + libssl 1.1", size=10, color=MUTED))

    # Контейнер 2
    frags.append(rect(750, 130, 200, 135, fill="#eaf6ef", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(850, 152, "Контейнер 2", size=13, bold=True, color=FIELD))
    frags.append(rect(760, 165, 180, 30, fill=BG, stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(850, 184, "Застосунок Б", size=11, bold=True))
    frags.append(rect(760, 200, 180, 55, fill="#fff6e5", stroke="#b45309", sw=1.0, rx=4))
    frags.append(text(850, 220, "Власний rootfs (v2.0)", size=11, bold=True, color="#b45309"))
    frags.append(text(850, 240, "glibc 2.35 + libssl 3.0", size=10, color=MUTED))

    # Шар ізоляції (Namespaces & cgroups)
    frags.append(rect(535, 285, 415, 60, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(742, 310, "Шар ізоляції ядра (Namespaces & cgroups v2)", size=14, bold=True, color=NEG))
    frags.append(text(742, 332, "mnt, pid, net, ipc, uts, user + OverlayFS", size=11, color=INK))

    # Ядро
    frags.append(rect(535, 365, 415, 100, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(742, 395, "Хостове ядро Linux (Single Kernel)", size=15, bold=True, color=POS))
    frags.append(text(742, 420, "Системні виклики (VFS, POSIX, Memory Management)", size=12, color=INK))
    frags.append(text(742, 445, "Пряме виконання процесів без гіпервізора", size=11, color=MUTED))

    render(os.path.join(IMG, 'pkg-vs-container-layers.svg'), W, H, *frags)

# ── 2. Структура OverlayFS у контейнері ────────────────────────────────────
def fig_overlayfs_structure():
    W, H = 960, 480
    frags = []

    frags.append(rect(15, 15, 930, 450, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(480, 45, "Архітектура шаруватої файлової системи OverlayFS у контейнері", size=18, bold=True))

    # 1. Merged View (Верхній об'єднаний шар)
    frags.append(rect(50, 75, 860, 75, fill="#eaf6ef", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(480, 103, "Віртуальне об'єднане дерево (merged)", size=16, color=FIELD, bold=True))
    frags.append(text(480, 130, "Єдина файлова система, яку бачить процес усередині Mount Namespace (/app, /etc, /lib)", size=12, color=INK))

    # Стрілка від Upper & Lower до Merged
    frags.append(arrow(260, 180, 260, 155, color=LINE, sw=1.5))
    frags.append(arrow(700, 180, 700, 155, color=LINE, sw=1.5))

    # 2. Upperdir (Мутабельний шар контейнера)
    frags.append(rect(50, 185, 410, 110, fill="#fff6e5", stroke="#b45309", sw=1.5, rx=8))
    frags.append(text(255, 213, "Шар запису (upperdir - Read/Write)", size=15, color="#b45309", bold=True))
    frags.append(text(255, 240, "Нові файли, зміни конфігів, тимчасові логи", size=12, color=INK))
    frags.append(text(255, 268, "Механізм Copy-on-Write (CoW) при модифікації", size=11, color=MUTED))

    # 3. Lowerdir (Незмінні базові шари образу)
    frags.append(rect(500, 185, 410, 245, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(705, 213, "Базові шари образу (lowerdir - Read-Only)", size=15, color=NEG, bold=True))
    frags.append(line(515, 225, 895, 225, color=NEG, sw=1.0))

    # Шари усередині lowerdir
    frags.append(rect(520, 238, 370, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    frags.append(text(705, 258, "Шар 3: Застосунок (Python / Node.js / Go code)", size=12, bold=True, color=INK))
    frags.append(text(705, 276, "SHA-256 layer digest (tarball)", size=10, color=MUTED))

    frags.append(rect(520, 298, 370, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    frags.append(text(705, 318, "Шар 2: Залежності та динамічні бібліотеки (OpenSSL, CPython)", size=12, bold=True, color=INK))
    frags.append(text(705, 336, "SHA-256 layer digest (tarball)", size=10, color=MUTED))

    frags.append(rect(520, 358, 370, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    frags.append(text(705, 378, "Шар 1: Базовий дистрибутив (Debian / Alpine rootfs)", size=12, bold=True, color=INK))
    frags.append(text(705, 396, "SHA-256 layer digest (tarball)", size=10, color=MUTED))

    # Workdir
    frags.append(rect(50, 310, 410, 120, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(255, 338, "Службовий каталог (workdir)", size=14, color=POS, bold=True))
    frags.append(text(255, 368, "Внутрішній каталог ядра для атомарної підготовки CoW", size=12, color=INK))
    frags.append(text(255, 398, "Використовується драйвером VFS при створенні whiteout-файлів", size=11, color=MUTED))

    render(os.path.join(IMG, 'overlayfs-structure.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_pkg_vs_container()
    fig_overlayfs_structure()
    print("SVG diagrams generated successfully!")
