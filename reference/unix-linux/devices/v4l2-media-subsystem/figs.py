# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
WARM   = "#fff6e5"
RED    = "#fdecea"
GREY   = "#eceff1"
PURPLE = "#f3e8ff"
LINE   = "#2c3e50"
FILL   = "#ffffff"

def fig_v4l2_mc_architecture():
    W, H = 1000, 680
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 40, ["Архітектура підсистеми V4L2 та Media Controller у Linux"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Userspace box
    f_usr, _, _ = textbox(W / 2, 110, ["Простір користувача (Userspace)", "Додатки (GStreamer, PipeWire, FFmpeg) / Бібліотека libcamera"], size=14, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_usr)

    # VFS / Device Nodes Layer
    y_dev = 230
    f_dev_sub, _, _ = textbox(250, y_dev, ["Вузли субпристроїв", "/dev/v4l-subdev0 .. N", "Конфігурація форматів і крапів"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_dev_sub)

    f_dev_mc, _, _ = textbox(500, y_dev, ["Вузол медіа-контролера", "/dev/media0", "Топологія графа та зв'язки"], size=13, fill=GREEN, stroke=LINE)
    p.append(f_dev_mc)

    f_dev_vid, _, _ = textbox(750, y_dev, ["Вузол відеопотоку", "/dev/video0 .. N", "Потік кадрів та Videobuf2"], size=13, fill=BLUE, stroke=LINE)
    p.append(f_dev_vid)

    # Kernel Core Frameworks
    y_core = 380
    f_v4l2_core, _, _ = textbox(300, y_core, ["V4L2 Subsystem Core", "struct v4l2_device & struct v4l2_subdev", "Управління контролями v4l2_ctrl_handler"], size=13, fill=FILL, stroke=LINE)
    p.append(f_v4l2_core)

    f_mc_core, _, _ = textbox(700, y_core, ["Media Controller Framework", "struct media_device & struct media_entity", "Валідація конвеєрів media_pipeline"], size=13, fill=FILL, stroke=LINE)
    p.append(f_mc_core)

    # Hardware & Drivers Layer
    y_hw = 540
    f_hw_sensor, _, _ = textbox(200, y_hw, ["Сенсор камери", "OV5640 / IMX219 (I2C)"], size=13, fill=RED, stroke=LINE)
    p.append(f_hw_sensor)

    f_hw_csi, _, _ = textbox(500, y_hw, ["Приймач MIPI CSI-2", "CSI-2 Receiver Subdevice"], size=13, fill=RED, stroke=LINE)
    p.append(f_hw_csi)

    f_hw_isp, _, _ = textbox(800, y_hw, ["Апаратний ISP / DMA Engine", "Обробка RAW -> NV12 -> RAM"], size=13, fill=RED, stroke=LINE)
    p.append(f_hw_isp)

    # Lines connecting layers
    p.append(line(500, 145, 500, 195, color=LINE, sw=2))
    p.append(line(250, 145, 250, 195, color=LINE, sw=2))
    p.append(line(750, 145, 750, 195, color=LINE, sw=2))

    p.append(line(250, 265, 300, 345, color=LINE, sw=2))
    p.append(line(500, 265, 700, 345, color=LINE, sw=2))
    p.append(line(750, 265, 700, 345, color=LINE, sw=2))

    p.append(line(300, 415, 200, 505, color=LINE, sw=2))
    p.append(line(300, 415, 500, 505, color=LINE, sw=2))
    p.append(line(700, 415, 800, 505, color=LINE, sw=2))

    render(os.path.join(IMG, 'v4l2-mc-architecture.svg'), W, H, *p)

def fig_mc_graph_topology():
    W, H = 1050, 480
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 40, ["Топологія графа Media Controller (Entities, Pads, Links)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Entity 1: Camera Sensor
    f_e1, _, _ = textbox(180, 140, ["Entity 1: Sensor", "(Subdevice)"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_e1)
    f_p1, _, _ = textbox(180, 220, ["Pad 0 [SOURCE]", "RAW10 1920x1080"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_p1)

    # Entity 2: CSI-2 Receiver
    f_e2, _, _ = textbox(525, 140, ["Entity 2: MIPI CSI-2 Receiver", "(Subdevice)"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_e2)
    f_p2_sink, _, _ = textbox(440, 220, ["Pad 0 [SINK]"], size=12, fill=PURPLE, stroke=LINE)
    p.append(f_p2_sink)
    f_p2_src, _, _ = textbox(610, 220, ["Pad 1 [SOURCE]"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_p2_src)

    # Entity 3: Video Capture Node
    f_e3, _, _ = textbox(870, 140, ["Entity 3: Video Node", "(/dev/video0)"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_e3)
    f_p3, _, _ = textbox(870, 220, ["Pad 0 [SINK]", "V4L2 Capture"], size=12, fill=PURPLE, stroke=LINE)
    p.append(f_p3)

    # Links between pads
    p.append(line(245, 220, 380, 220, color=LINE, sw=3))
    f_l1, _, _ = textbox(312, 190, ["Link 1: ENABLED"], size=11, fill=WARM, stroke=LINE)
    p.append(f_l1)

    p.append(line(675, 220, 805, 220, color=LINE, sw=3))
    f_l2, _, _ = textbox(740, 190, ["Link 2: ENABLED"], size=11, fill=WARM, stroke=LINE)
    p.append(f_l2)

    # Pipeline validation box below
    f_pipe, _, _ = textbox(W / 2, 380, ["Валідація медіа-конвеєра: media_pipeline_start()", "Перевірка збігу форматів (Subdev Format Negotiation) та активності посилань"], size=13, fill=BLUE, stroke=LINE)
    p.append(f_pipe)

    p.append(line(312, 235, 312, 350, color=LINE, sw=2))
    p.append(line(740, 235, 740, 350, color=LINE, sw=2))

    render(os.path.join(IMG, 'mc-graph-topology.svg'), W, H, *p)

def fig_vb2_buffer_lifecycle():
    W, H = 1100, 520
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 40, ["Життєвий цикл буфера у фреймворку Videobuf2 (vb2)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # States
    f_s1, _, _ = textbox(150, 160, ["DEQUEUED", "Буфер у користувача"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_s1)

    f_s2, _, _ = textbox(450, 160, ["PREPARED", "Перевірено & DMA mapped"], size=13, bold=True, fill=PURPLE, stroke=LINE)
    p.append(f_s2)

    f_s3, _, _ = textbox(750, 160, ["QUEUED", "В черзі драйвера"], size=13, bold=True, fill=WARM, stroke=LINE)
    p.append(f_s3)

    f_s4, _, _ = textbox(950, 340, ["ACTIVE (DMA)", "Заповнення кадру HW"], size=13, bold=True, fill=RED, stroke=LINE)
    p.append(f_s4)

    f_s5, _, _ = textbox(450, 340, ["DONE", "Кадр готовий"], size=13, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_s5)

    # Transitions
    p.append(line(230, 160, 360, 160, color=LINE, sw=2))
    f_t1, _, _ = textbox(295, 130, ["VIDIOC_PREPARE_BUF"], size=11, fill=FILL, stroke=LINE)
    p.append(f_t1)

    p.append(line(540, 160, 670, 160, color=LINE, sw=2))
    f_t2, _, _ = textbox(605, 130, ["VIDIOC_QBUF"], size=11, fill=FILL, stroke=LINE)
    p.append(f_t2)

    p.append(line(830, 160, 950, 295, color=LINE, sw=2))
    f_t3, _, _ = textbox(920, 210, ["STREAMON"], size=11, fill=FILL, stroke=LINE)
    p.append(f_t3)

    p.append(line(870, 340, 540, 340, color=LINE, sw=2))
    f_t4, _, _ = textbox(705, 370, ["IRQ: vb2_buffer_done()"], size=11, fill=FILL, stroke=LINE)
    p.append(f_t4)

    p.append(line(360, 340, 150, 210, color=LINE, sw=2))
    f_t5, _, _ = textbox(220, 300, ["VIDIOC_DQBUF"], size=11, fill=FILL, stroke=LINE)
    p.append(f_t5)

    # Bottom summary box
    f_summary, _, _ = textbox(W / 2, 460, ["Типи пам'яті: V4L2_MEMORY_MMAP (аллокація у драйвері) / V4L2_MEMORY_DMABUF (Zero-Copy з GPU) / V4L2_MEMORY_USERPTR"], size=12, fill=GREY, stroke=LINE)
    p.append(f_summary)

    render(os.path.join(IMG, 'vb2-buffer-lifecycle.svg'), W, H, *p)

if __name__ == '__main__':
    fig_v4l2_mc_architecture()
    fig_mc_graph_topology()
    fig_vb2_buffer_lifecycle()
    print("Figures generated successfully.")
