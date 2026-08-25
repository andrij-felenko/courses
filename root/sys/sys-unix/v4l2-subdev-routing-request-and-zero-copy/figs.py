# -*- coding: utf-8 -*-
"""Фігури до теми «Відео-підсистема V4L2 та Media Controller API»."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_mc_graph():
    """Топологія графа Media Controller: entities, pads, links."""
    W, H = 860, 260
    f = []

    # Заголовок рамки підсистеми
    f.append(rect(20, 10, 820, 230, fill="#fdfdfd", stroke="#b0bec5", sw=1.5, rx=12))
    f.append(text(430, 32, "Media Controller Graph (/dev/media0)", size=15, bold=True, color="#37474f"))

    # Блок 1: Sensor
    f.append(fitbox(40, 75, 160, 110, "Sensor Entity\n\n/dev/v4l2-subdev0", size=13, fill="#e3f2fd", stroke="#1976d2", bold=True))
    f.append(circle(200, 130, 9, fill="#ff9800", stroke="#e65100"))
    f.append(text(200, 108, "Pad 0 (Src)", size=10, bold=True, color="#e65100"))

    # Блок 2: CSI-2 RX
    f.append(fitbox(260, 75, 150, 110, "CSI-2 Receiver\n\n/dev/v4l2-subdev1", size=13, fill="#e8eaf6", stroke="#3f51b5", bold=True))
    f.append(circle(260, 130, 9, fill="#4caf50", stroke="#1b5e20"))
    f.append(text(260, 108, "Pad 0 (Sink)", size=10, bold=True, color="#1b5e20"))
    f.append(circle(410, 130, 9, fill="#ff9800", stroke="#e65100"))
    f.append(text(410, 108, "Pad 1 (Src)", size=10, bold=True, color="#e65100"))

    # Блок 3: ISP
    f.append(fitbox(470, 75, 150, 110, "ISP Engine\n\n/dev/v4l2-subdev2", size=13, fill="#e8f5e9", stroke="#388e3c", bold=True))
    f.append(circle(470, 130, 9, fill="#4caf50", stroke="#1b5e20"))
    f.append(text(470, 108, "Pad 0 (Sink)", size=10, bold=True, color="#1b5e20"))
    f.append(circle(620, 130, 9, fill="#ff9800", stroke="#e65100"))
    f.append(text(620, 108, "Pad 1 (Src)", size=10, bold=True, color="#e65100"))

    # Блок 4: Video Node
    f.append(fitbox(680, 75, 140, 110, "Video Node\n\n/dev/video0", size=13, fill="#fff3e0", stroke="#f57c00", bold=True))
    f.append(circle(680, 130, 9, fill="#4caf50", stroke="#1b5e20"))
    f.append(text(680, 108, "Pad 0 (Sink)", size=10, bold=True, color="#1b5e20"))

    # Links
    f.append(arrow(209, 130, 251, 130, color="#263238", sw=2))
    f.append(arrow(419, 130, 461, 130, color="#263238", sw=2))
    f.append(arrow(629, 130, 671, 130, color="#263238", sw=2))

    f.append(text(230, 150, "Link 1", size=10, color=MUTED))
    f.append(text(440, 150, "Link 2", size=10, color=MUTED))
    f.append(text(650, 150, "Link 3", size=10, color=MUTED))

    # Підпис знизу
    f.append(text(430, 215, "Маршрутизація даних через pad formats та динамічні зв'язки (Media Links)", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'mc-graph.svg'), W, H, *f)


def fig_vb2_state_machine():
    """Життєвий цикл відеобуферів у фреймворку Videobuf2 (vb2)."""
    W, H = 840, 250
    f = []

    # Стан 1: DEQUEUED
    f.append(fitbox(30, 80, 130, 70, "DEQUEUED\n(у юзерспайсі)", size=12, fill="#eceff1", stroke="#546e7a", bold=True))
    # Стан 2: PREPARED
    f.append(fitbox(230, 80, 130, 70, "PREPARED\n(сторінки pinned)", size=12, fill="#e1f5fe", stroke="#0288d1", bold=True))
    # Стан 3: QUEUED
    f.append(fitbox(430, 80, 130, 70, "QUEUED\n(в queued_list)", size=12, fill="#fff8e1", stroke="#ffa000", bold=True))
    # Стан 4: ACTIVE / DONE
    f.append(fitbox(630, 80, 170, 70, "ACTIVE -> DONE\n(DMA -> done_list)", size=12, fill="#e8f5e9", stroke="#388e3c", bold=True))

    # Переходи
    f.append(arrow(160, 100, 230, 100, color="#37474f", sw=1.8))
    f.append(text(195, 90, "CREATE_BUFS", size=9, bold=True, color="#0288d1"))

    f.append(arrow(360, 105, 430, 105, color="#37474f", sw=1.8))
    f.append(text(395, 95, "QBUF", size=10, bold=True, color="#ffa000"))

    f.append(arrow(560, 115, 630, 115, color="#37474f", sw=1.8))
    f.append(text(595, 105, "Hardware DMA", size=10, bold=True, color="#388e3c"))

    # Повернення DQBUF
    f.append(arrow(715, 150, 95, 150, color="#c0392b", sw=1.8))
    f.append(text(405, 170, "VIDIOC_DQBUF (повернення в простір користувача)", size=11, bold=True, color="#c0392b"))

    # Прямий шлях QBUF з DEQUEUED в QUEUED
    f.append(arrow(95, 80, 495, 80, color="#546e7a", sw=1.5))
    f.append(text(295, 68, "VIDIOC_QBUF (прямий виклик)", size=10, italic=True, color="#546e7a"))

    render(os.path.join(IMG, 'vb2-state-machine.svg'), W, H, *f)


def fig_dma_buf_zero_copy():
    """Схема Zero-Copy передачі відеокадрів між V4L2 та DRM/KMS через DMA-BUF."""
    W, H = 840, 260
    f = []

    # V4L2 Device Box
    f.append(fitbox(40, 50, 220, 140, "V4L2 Capture Subsystem\n(/dev/video0)\n\n• vb2_queue\n• VIDIOC_EXPBUF\n• Створення dma_buf fd", size=12, fill="#e3f2fd", stroke="#1565c0", bold=True))

    # Central DMA-BUF Box
    f.append(fitbox(310, 70, 220, 100, "DMA-BUF Framework\n(Ядро Linux)\n\n• dma_buf_attachment\n• sg_table (физ. сторінки)\n• dma_fence (синхронізація)", size=12, fill="#fff3e0", stroke="#e65100", bold=True))

    # DRM/KMS / GPU Box
    f.append(fitbox(580, 50, 220, 140, "DRM/KMS / GPU Renderer\n(/dev/dri/card0)\n\n• DRM FB (addfb2)\n• Direct Scanout / EGL\n• Виведення на дисплей", size=12, fill="#e8f5e9", stroke="#2e7d32", bold=True))

    # Arrows
    f.append(arrow(260, 105, 310, 105, color="#1565c0", sw=2))
    f.append(text(285, 92, "EXPBUF", size=10, bold=True, color="#1565c0"))

    f.append(arrow(530, 105, 580, 105, color="#2e7d32", sw=2))
    f.append(text(555, 92, "Import FD", size=10, bold=True, color="#2e7d32"))

    # Direct DMA Transfer Line below
    f.append(arrow(150, 190, 690, 190, color="#c0392b", sw=2.5))
    f.append(text(420, 215, "Прямий апаратний DMA-перенос (RAM -> Display Controller) без копіювання CPU", size=12, bold=True, color="#c0392b"))

    render(os.path.join(IMG, 'dma-buf-zero-copy.svg'), W, H, *f)


def main():
    fig_mc_graph()
    fig_vb2_state_machine()
    fig_dma_buf_zero_copy()


if __name__ == "__main__":
    main()
