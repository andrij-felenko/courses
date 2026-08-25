# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"

def fig_virtio_fs():
    W, H = 1000, 580
    frags = []

    frags.append(rect(40, 50, 340, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(210, 80, "Гостьова ОС (Guest VM)", size=16, color=INK, bold=True))

    frags.append(rect(620, 50, 340, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(790, 80, "Хостова система (Host)", size=16, color=INK, bold=True))

    b1, _, _ = textbox(210, 140, ["Гостьовий процес", "(open, read, mmap)"], size=13, pad=16, fill=BLUE, stroke=LINE)
    frags.append(b1)

    b2, _, _ = textbox(210, 260, ["Ядро гостя: VFS & virtiofs.ko", "(Формування FUSE-запитів)"], size=13, pad=16, fill=BLUE, stroke=LINE)
    frags.append(b2)
    frags.append(arrow(210, 180, 210, 220))

    b3, _, _ = textbox(210, 440, ["Віртуальна пам'ять ВМ", "(Shared Memory Region / DAX Window)"], size=13, pad=16, fill=WARM, stroke=LINE)
    frags.append(b3)

    frags.append(rect(410, 235, 180, 50, fill=GREY, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(500, 265, "Virtqueue (FUSE Req/Resp)", size=12, color=INK, bold=True))

    frags.append(arrow(320, 260, 405, 260))
    frags.append(arrow(595, 260, 645, 260))

    b4, _, _ = textbox(790, 260, ["Демон virtiofsd (Host Userspace)", "(vhost-user / openat2, pread)"], size=13, pad=16, fill=GREEN, stroke=LINE)
    frags.append(b4)

    b5, _, _ = textbox(790, 440, ["Сторінковий кеш хоста", "(Host Page Cache & FS)"], size=13, pad=16, fill=GREEN, stroke=LINE)
    frags.append(b5)
    frags.append(arrow(790, 310, 790, 390))

    frags.append(line(325, 440, 675, 440, color=POS, sw=2, dash="5,5"))
    frags.append(text(500, 420, "Прямий mmap (Zero-copy DAX)", size=12, color=POS, bold=True))

    render(os.path.join(IMG, "virtio-fs-arch.svg"), W, H, *frags)

def fig_virtio_gpu():
    W, H = 1000, 600
    frags = []

    frags.append(rect(40, 50, 340, 510, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(210, 80, "Гостьова ОС (Guest VM)", size=16, color=INK, bold=True))

    frags.append(rect(620, 50, 340, 510, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(790, 80, "Хостова система (Host)", size=16, color=INK, bold=True))

    b1, _, _ = textbox(210, 140, ["Графічний додаток", "(OpenGL / Vulkan)"], size=13, pad=16, fill=BLUE, stroke=LINE)
    frags.append(b1)

    b2, _, _ = textbox(210, 240, ["Mesa (virgl / vulkan-virtio)", "Серіалізація в TGSI/Venus"], size=13, pad=16, fill=BLUE, stroke=LINE)
    frags.append(b2)
    frags.append(arrow(210, 180, 210, 205))

    b3, _, _ = textbox(210, 340, ["Ядро гостя: virtio_gpu.ko", "(Управління Virtqueue controlq)"], size=13, pad=16, fill=BLUE, stroke=LINE)
    frags.append(b3)
    frags.append(arrow(210, 275, 210, 305))

    frags.append(rect(410, 315, 180, 50, fill=GREY, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(500, 345, "Virtqueue (Command Stream)", size=12, color=INK, bold=True))

    frags.append(arrow(320, 340, 405, 340))
    frags.append(arrow(595, 340, 645, 340))

    b4, _, _ = textbox(790, 340, ["virglrenderer / QEMU", "Трансляція в OpenGL/Vulkan хоста"], size=13, pad=16, fill=GREEN, stroke=LINE)
    frags.append(b4)

    b5, _, _ = textbox(790, 160, ["Драйвер GPU хоста", "& Фізичний GPU (NVIDIA/AMD/Intel)"], size=13, pad=16, fill=GREEN, stroke=LINE)
    frags.append(b5)

    # Arrow from virglrenderer up to GPU driver
    frags.append(arrow(790, 290, 790, 210))

    b6, _, _ = textbox(790, 490, ["Композитор хоста (Wayland/X11)", "(Zero-copy вивід через dma-buf)"], size=13, pad=16, fill=WARM, stroke=LINE)
    frags.append(b6)

    # Arrow from virglrenderer down to Host Compositor (dma-buf)
    frags.append(arrow(790, 390, 790, 440))

    render(os.path.join(IMG, "virtio-gpu-arch.svg"), W, H, *frags)

def render_all():
    fig_virtio_fs()
    fig_virtio_gpu()

if __name__ == '__main__':
    render_all()
