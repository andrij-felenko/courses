# -*- coding: utf-8 -*-
"""Фігури до теми «V4L2: модель відеопристрою в ядрі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_buffer_ownership():
    """Кільце власності: буфер завжди належить комусь одному."""
    W, H = 1060, 350
    f = []

    boxes = [
        (40,  "простір користувача", "Програма\nтримає буфер 3"),
        (300, "драйвер",             "Вхідна черга\nбуфер 0 чекає"),
        (560, "апаратура",           "Запис кадру\nбуфер 1 наповнюється"),
        (820, "драйвер",             "Вихідна черга\nбуфер 2 готовий"),
    ]
    bw, by, bh = 200, 140, 84
    fills = [FILL, "#eaf0fd", "#eaf7ee", "#eaf0fd"]
    strokes = [LINE, NEG, FIELD, NEG]

    for i, (bx, head, body) in enumerate(boxes):
        f.append(text(bx + bw / 2, 118, head, size=12, color=MUTED))
        f.append(fitbox(bx, by, bw, bh, body, size=13,
                        fill=fills[i], stroke=strokes[i]))

    # стрілки між станціями
    gaps = [(240, 300, "QBUF"), (500, 560, "кадр"), (760, 820, "IRQ")]
    for x1, x2, lab in gaps:
        f.append(arrow(x1 + 8, by + bh / 2, x2 - 6, by + bh / 2))
        f.append(text((x1 + x2) / 2, by + bh / 2 - 16, lab, size=12, color=MUTED))

    # зворотний шлях: DQBUF
    ry = 296
    f.append(line(920, by + bh, 920, ry))
    f.append(line(920, ry, 140, ry))
    f.append(arrow(140, ry, 140, by + bh + 6))
    f.append(text(530, ry - 14,
                  "VIDIOC_DQBUF — програма забирає готовий буфер, poll каже коли",
                  size=13, color=INK))

    render(os.path.join(IMG, 'buffer-ownership.svg'), W, H, *f)


def fig_memory_models():
    """Три відповіді на питання «чия пам'ять»."""
    W, H = 1060, 430
    f = []

    lab_x = 24
    col_x = 320
    col_w = 700

    rows = [
        (60,  "V4L2_MEMORY_MMAP", "виділяє драйвер",
         "пам'ять драйвера, відображена в процес",
         "драйвер сам знає вирівнювання й зону, доступну його пристроєві",
         FILL, LINE),
        (185, "V4L2_MEMORY_USERPTR", "виділяє програма",
         "пам'ять процесу, віддана драйверові вказівником",
         "сторінки треба закріпити й узгодити кеші — багато драйверів не підтримують",
         "#fdecea", POS),
        (310, "V4L2_MEMORY_DMABUF", "виділяє хтось третій",
         "буфер відеокарти чи кодека, переданий дескриптором",
         "камера пише прямо в чужий буфер — кадр не заходить у пам'ять процесу",
         "#eaf7ee", FIELD),
    ]

    for y, title_, sub, box, note, fill, stroke in rows:
        f.append(text(lab_x, y + 16, title_, size=13, bold=True, anchor="start"))
        f.append(text(lab_x, y + 38, sub, size=12, color=MUTED, anchor="start"))
        f.append(fitbox(col_x, y, col_w, 50, box, size=13, fill=fill, stroke=stroke))
        f.append(text(col_x, y + 74, note, size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'memory-models.svg'), W, H, *f)


def fig_node_vs_graph():
    """Один вузол проти графа вузлів."""
    W, H = 1100, 410
    f = []

    # ── ліва половина: USB-камера ─────────────────────────────────────────
    lx, lw = 100, 280
    f.append(text(lx + lw / 2, 52, "Проста USB-камера", size=14, bold=True))
    left = [
        (86,  "мікросхема камери\nуся обробка всередині", FILL, LINE),
        (186, "/dev/video0", "#eaf0fd", NEG),
        (286, "програма", FILL, LINE),
    ]
    for y, s, fill, stroke in left:
        f.append(fitbox(lx, y, lw, 62, s, size=13, fill=fill, stroke=stroke))
    f.append(arrow(lx + lw / 2, 150, lx + lw / 2, 182))
    f.append(arrow(lx + lw / 2, 250, lx + lw / 2, 282))

    # роздільник
    f.append(line(470, 40, 470, 380, color=MUTED, sw=1.2, dash="6 6"))

    # ── права половина: тракт на системі на кристалі ───────────────────────
    rx_, rw = 560, 280
    f.append(text(rx_ + rw / 2, 52, "Тракт на системі на кристалі", size=14, bold=True))
    right = [
        (76,  "сенсор", FILL, LINE),
        (156, "приймач CSI-2", FILL, LINE),
        (236, "блок обробки зображення", FILL, LINE),
        (316, "/dev/video0", "#eaf0fd", NEG),
    ]
    for y, s, fill, stroke in right:
        f.append(fitbox(rx_, y, rw, 48, s, size=13, fill=fill, stroke=stroke))
    for y in (124, 204, 284):
        f.append(arrow(rx_ + rw / 2, y, rx_ + rw / 2, y + 28))

    # бічні підписи
    f.append(line(846, 180, 872, 180, color=MUTED, sw=1.2, dash="4 4"))
    f.append(mtext(880, 174, ["/dev/v4l-subdevN —", "формат кожної ланки"],
                   size=11, color=MUTED, anchor="start"))
    f.append(line(846, 260, 872, 260, color=MUTED, sw=1.2, dash="4 4"))
    f.append(mtext(880, 254, ["/dev/media0 —", "граф і зв'язки"],
                   size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'node-vs-graph.svg'), W, H, *f)


def fig_readback_fields():
    """Три виклики, після яких структуру треба ПЕРЕЧИТАТИ."""
    W, H = 1060, 380
    f = []

    lx, lw = 40, 300
    rx_, rw = 660, 360
    bh = 84

    f.append(text(lx + lw / 2, 36, "що просимо", size=13, color=MUTED))
    f.append(text(rx_ + rw / 2, 36, "що лежить у структурі після виклику",
                  size=13, color=MUTED))

    rows = [
        (100, "VIDIOC_S_FMT",
         "width  = 1366\nheight = 768\nYUYV",
         "1366 × 768, YUYV\nbytesperline = 2752 Б\nsizeimage = 2 113 536 Б"),
        (215, "VIDIOC_REQBUFS",
         "count = 4",
         "count = 2\nстільки пам'яті під DMA дали"),
        (330, "VIDIOC_QUERYBUF",
         "index = 1",
         "m.offset — де шукати у вузлі\nlength = 2 113 536 Б"),
    ]

    for cy, call, ask, got in rows:
        f.append(fitbox(lx, cy - bh / 2, lw, bh, ask, size=13,
                        fill=FILL, stroke=LINE))
        f.append(fitbox(rx_, cy - bh / 2, rw, bh, got, size=13,
                        fill="#eaf7ee", stroke=FIELD))
        f.append(arrow(lx + lw + 10, cy, rx_ - 10, cy))
        f.append(text((lx + lw + rx_) / 2, cy - 14, call, size=13, bold=True))

    render(os.path.join(IMG, 'readback-fields.svg'), W, H, *f)


def fig_buf_flags():
    """Стан буфера й прапорці, які показує QUERYBUF."""
    W, H = 1080, 430
    f = []

    lab_x = 24
    col_x, col_w = 300, 420
    flg_x = 760
    bh = 52

    f.append(text(lab_x, 34, "команда або подія", size=12, color=MUTED,
                  anchor="start"))
    f.append(text(col_x + col_w / 2, 34, "стан буфера", size=12, color=MUTED))
    f.append(text(flg_x, 34, "що покаже QUERYBUF", size=12, color=MUTED,
                  anchor="start"))

    rows = [
        (60,  "VIDIOC_REQBUFS", "буфер виділено, ще не відображено",
         "прапорців нема", FILL, LINE),
        (130, "mmap()", "пам'ять видно програмі",
         "MAPPED", FILL, LINE),
        (200, "VIDIOC_QBUF", "у вхідній черзі або наповнюється",
         "MAPPED | QUEUED", "#eaf0fd", NEG),
        (270, "кадр завершено", "у вихідній черзі, poll дає POLLIN",
         "MAPPED | DONE", "#eaf7ee", FIELD),
        (340, "VIDIOC_DQBUF", "знову в руках програми",
         "MAPPED, іноді ERROR", FILL, LINE),
    ]

    for y, cmd, state, flags, fill, stroke in rows:
        f.append(text(lab_x, y + 30, cmd, size=13, bold=True, anchor="start"))
        f.append(fitbox(col_x, y, col_w, bh, state, size=13,
                        fill=fill, stroke=stroke))
        f.append(text(flg_x, y + 30, flags, size=12, color=INK, anchor="start"))

    for y in (60, 130, 200, 270):
        f.append(arrow(col_x + col_w / 2, y + bh + 2, col_x + col_w / 2, y + 66))

    f.append(text(lab_x, 412,
                  "VIDIOC_STREAMOFF повертає буфери з обох черг у другий рядок: "
                  "QUEUED і DONE знято, дані втрачено",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'buf-flags.svg'), W, H, *f)


if __name__ == '__main__':
    fig_buffer_ownership()
    fig_memory_models()
    fig_node_vs_graph()
    fig_readback_fields()
    fig_buf_flags()
    print("готово:", IMG)
