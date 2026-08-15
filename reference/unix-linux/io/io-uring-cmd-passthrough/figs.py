# -*- coding: utf-8 -*-
"""Фігури до теми «Низькорівневий пасстру команд NVMe через IORING_OP_URING_CMD»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_uring_passthrough():
    """Порівняння традиційного стеку blk-mq та прямого passthrough через IORING_OP_URING_CMD."""
    W, H = 940, 520
    g = []

    # Заголовок та шари
    g.append(fitbox(20, 20, 430, 40, "Класичний стек (blk-mq / VFS)", size=14, bold=True, fill="#fdecea"))
    g.append(fitbox(490, 20, 430, 40, "io_uring Passthrough (IORING_OP_URING_CMD)", size=14, bold=True, fill="#eaf7ee"))

    # Спрощена ліва колонка (класичний стек)
    g.append(fitbox(40, 80, 390, 44, "Програма Userspace: pread() / read()", size=12))
    g.append(fitbox(40, 150, 390, 44, "VFS & Файлова система (ext4 / xfs)", size=12, fill="#f0f4f8"))
    g.append(fitbox(40, 220, 390, 44, "Блоковий шар (blk-mq & struct bio)", size=12, fill="#f0f4f8"))
    g.append(fitbox(40, 290, 390, 44, "Драйвер блочного пристрою /dev/nvme0n1", size=12, fill="#f0f4f8"))
    g.append(fitbox(40, 360, 390, 44, "Апаратна черга NVMe SQ (PCIe DMA)", size=12, fill="#eef2f7"))
    g.append(fitbox(40, 430, 390, 44, "Накладні витрати: виділення bio/request, lock, IRQ", size=11, fill="#fdecea"))

    # Стрілки лівої колонки
    g.append(arrow(235, 124, 235, 148))
    g.append(arrow(235, 194, 235, 218))
    g.append(arrow(235, 264, 235, 288))
    g.append(arrow(235, 334, 235, 358))
    g.append(arrow(235, 404, 235, 428))

    # Права колонка (io_uring passthrough)
    g.append(fitbox(510, 80, 390, 44, "Userspace: SQE (IORING_OP_URING_CMD)", size=12, fill="#eaf7ee"))
    g.append(fitbox(510, 150, 390, 44, "Обхід VFS & blk-mq (Bypass)", size=12, bold=True, fill="#fff3cd"))
    g.append(fitbox(510, 220, 390, 44, "Символьний пристрій /dev/ng0n1 (uring_cmd)", size=12, fill="#eaf7ee"))
    g.append(fitbox(510, 290, 390, 44, "nvme_ns_chr_uring_cmd() → hardware SQ", size=12, fill="#eaf7ee"))
    g.append(fitbox(510, 360, 390, 44, "NVMe контролер + IOPOLL / CQE ring", size=12, fill="#eaf7ee"))
    g.append(fitbox(510, 430, 390, 44, "Переваги: Zero-copy, zero-alloc, прямі vendor NVMe cmd", size=11, fill="#eaf7ee"))

    # Стрілки правої колонки
    g.append(arrow(705, 124, 705, 148))
    g.append(arrow(705, 194, 705, 218))
    g.append(arrow(705, 264, 705, 288))
    g.append(arrow(705, 334, 705, 358))
    g.append(arrow(705, 404, 705, 428))

    render(os.path.join(IMG, 'fig-uring-passthrough.svg'), W, H, *g)


if __name__ == '__main__':
    fig_uring_passthrough()
    print("ok")
