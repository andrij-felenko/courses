# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми tmpfs-shmem-ram-filesystem."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_architecture_fig(path):
    """Фігура 1: Взаємодія VFS, підсистеми shmem, Page Cache та Swap."""
    w, h = 860, 530
    body = []

    # Верхній шар: VFS та Системні виклики
    body.append(rect(20, 15, 820, 60, fill="#f8fafc", stroke=MUTED, sw=1.5))
    body.append(text(430, 38, "Шар ВФС (Virtual File System) — Системні виклики", size=15, bold=True))
    body.append(text(430, 58, "sys_open()  ·  sys_read()  ·  sys_write()  ·  sys_mmap()  ·  sys_unlink()", size=12, color=MUTED))

    # Стрілки вниз від VFS до трьох файлових систем
    body.append(arrow(150, 75, 150, 130))
    body.append(arrow(430, 75, 430, 130))
    body.append(arrow(710, 75, 710, 130))

    # Блок 1: ramfs
    box1, w1, h1 = textbox(150, 190, "ramfs\nПряме обгортання Page Cache\nБез лімітів розміру (OOM!)\nСторінки НЕ у swap", size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.5)
    body.append(box1)

    # Блок 2: tmpfs / shmem (Головний акцент)
    box2, w2, h2 = textbox(430, 190, "tmpfs / shmem (mm/shmem.c)\nДинамічні сторінки (Page Cache)\nМежі: size=, nr_blocks=, nr_inodes=\nВитискання у Swap при тиску RAM", size=12, pad=10, fill="#eaf0fd", stroke=NEG, sw=2, bold=True)
    body.append(box2)

    # Блок 3: ext4 / XFS (дискова ФС)
    box3, w3, h3 = textbox(710, 190, "ext4 / XFS\nДисковий Page Cache\nСинхронізація (writeback)\nБлоковий пристрій (/dev/sda)", size=12, pad=10, fill="#f4f6f8", stroke=MUTED, sw=1.5)
    body.append(box3)

    # Стрілки від ФС до нижніх шарів
    body.append(arrow(150, 250, 150, 310))
    body.append(arrow(430, 250, 430, 310))
    body.append(arrow(710, 250, 710, 310))

    # Нижній шар: Фізичні ресурси
    # RAM
    box_ram, wr, hr = textbox(290, 360, "Фізична оперативна пам'ять (RAM)\nАнонімні сторінки (struct page / folio)\nВиділення при записі (shmem_get_folio)\nЗвільнення при unlink / truncate", size=12, pad=10, fill="#e8f8f5", stroke=FIELD, sw=2)
    body.append(box_ram)

    # Дисковий пристрій для ext4
    box_disk, wd, hd = textbox(710, 360, "Накопичувач (SSD/HDD)\nДискові сектори / ФС\nПостійне зберігання", size=12, pad=10, fill="#f4f6f8", stroke=MUTED, sw=1.5)
    body.append(box_disk)

    # Зв'язок від RAM до Swap для tmpfs
    body.append(arrow(430, 410, 430, 425))
    body.append(text(525, 418, "kswapd reclaim", size=11, color=MUTED, italic=True))

    # Swap підсистема для tmpfs
    box_swap, ws, hs = textbox(430, 470, "Підсистема Swap (swp_entry_t)\nshmem_writepage() виносить сторінки tmpfs у swap\nxarray (i_pages) тримає слоти swap замість покажчиків на сторінки", size=12, pad=10, fill="#fef9e7", stroke="#f39c12", sw=2)
    body.append(box_swap)

    render(path, w, h, "\n".join(body))


def make_dual_personality_fig(path):
    """Фігура 2: Двоїста природа підсистеми shmem у ядрі Linux."""
    w, h = 840, 500
    body = []

    # Заголовок зверху
    body.append(rect(20, 15, 800, 45, fill="#f8fafc", stroke=MUTED, sw=1.5))
    body.append(text(420, 43, "Ядерний двигун shmem (mm/shmem.c) та внутрішній shm_mnt", size=15, bold=True, color=NEG))

    # Ліва колонка: Публічний ВФС-інтерфейс (User mounts)
    body.append(rect(30, 80, 370, 225, fill="#f4f6f8", stroke=NEG, sw=1.5))
    body.append(text(215, 105, "Публічний ВФС-інтерфейс (mount -t tmpfs)", size=13, bold=True, color=NEG))

    b_tmp, _, _ = textbox(215, 145, "Тимчасові ФС системи\n/tmp  ·  /run  ·  /run/user/1000", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_tmp)

    b_shm, _, _ = textbox(215, 200, "POSIX Shared Memory\n/dev/shm  (shm_open / shm_unlink)", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_shm)

    b_custom, _, _ = textbox(215, 255, "Спеціальні монтування\nrootfs / initramfs  ·  overlayfs upperdir у RAM", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_custom)

    # Права колонка: Внутрішні механізми ядра та анонімні об'єкти
    body.append(rect(440, 80, 370, 225, fill="#f4f6f8", stroke=POS, sw=1.5))
    body.append(text(625, 105, "Внутрішні об'єкти ядра та IPC", size=13, bold=True, color=POS))

    b_sysv, _, _ = textbox(625, 145, "System V Shared Memory\nshmget()  ·  shmat()  ·  shmctl()", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_sysv)

    b_memfd, _, _ = textbox(625, 200, "Анонімні файлові дескриптори\nmemfd_create()  +  F_ADD_SEALS", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_memfd)

    b_gpu, _, _ = textbox(625, 255, "Анонімний mmap(MAP_SHARED) & DRM/GEM\nБуфери графіки i915 / amdgpu / dma-buf", size=11.5, fill="#ffffff", stroke=MUTED)
    body.append(b_gpu)

    # Стрілки від обох колонок до центрального ядра shmem
    body.append(arrow(215, 305, 360, 355))
    body.append(arrow(625, 305, 480, 355))

    # Центральний ядерний модуль shmem
    b_core, _, _ = textbox(420, 395, "Підсистема ядра shmem (mm/shmem.c)\nУправління сторінками Page Cache, індексними вузлами shmem_inode_info\nта відстеженням слотів Swap (swp_entry_t)", size=12, fill="#eaf0fd", stroke=NEG, sw=2, bold=True)
    body.append(b_core)

    # Нижня стрілка до RAM / Swap
    body.append(arrow(420, 435, 420, 460))
    body.append(text(420, 480, "Спільний фонд пам'яті: RAM (Page Cache) ↔ Swap", size=12, color=MUTED, bold=True))

    render(path, w, h, "\n".join(body))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    fig1_path = os.path.join(OUT_DIR, "tmpfs-vfs-shmem-architecture.svg")
    make_architecture_fig(fig1_path)
    print("Згенеровано:", fig1_path)

    fig2_path = os.path.join(OUT_DIR, "shmem-dual-personality.svg")
    make_dual_personality_fig(fig2_path)
    print("Згенеровано:", fig2_path)


if __name__ == "__main__":
    main()
