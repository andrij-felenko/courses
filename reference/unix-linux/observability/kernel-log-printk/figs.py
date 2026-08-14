# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"
ACCENT = "#3182ce"
MUTED_BG = "#edf2f7"

def fig_printk_buffer():
    W, H = 820, 360
    p = []
    
    # Title / Background Card
    p.append(rect(10, 10, 800, 340, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    p.append(text(30, 40, "Структура кільцевого буфера printk (lockless ringbuffer)", size=15, color=INK, bold=True))

    # Kernel space sources
    p.append(fitbox(30, 70, 220, 50, "HardIRQ / SoftIRQ", fill=WARM, stroke=NEG, sw=1.5, rx=6))
    p.append(fitbox(30, 135, 220, 50, "Контекст процесів ядра", fill=COLD, stroke=ACCENT, sw=1.5, rx=6))
    p.append(fitbox(30, 200, 220, 50, "Emergency / Kernel Panic", fill="#fff5f5", stroke="#e53e3e", sw=2, rx=6))

    # Arrow to printk()
    p.append(arrow(250, 95, 300, 145, color=NEG, sw=1.5))
    p.append(arrow(250, 160, 300, 160, color=ACCENT, sw=1.5))
    p.append(arrow(250, 225, 300, 175, color="#e53e3e", sw=2))

    # printk core lockless engine
    p.append(rect(300, 120, 160, 80, fill=GREENFILL, stroke=POS, sw=2, rx=8))
    p.append(text(380, 150, "printk()", size=14, color=POS, bold=True, anchor="middle"))
    p.append(text(380, 175, "lockless prb_reserve()", size=11, color=INK, anchor="middle"))

    # Ring Buffer Box
    p.append(rect(490, 60, 300, 160, fill=SOFT, stroke=ACCENT, sw=2, rx=8))
    p.append(text(640, 85, "__log_buf (lockless ring)", size=13, color=ACCENT, bold=True, anchor="middle"))
    
    # Ring slots
    for i in range(4):
        x = 510 + i * 68
        p.append(rect(x, 105, 62, 70, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
        p.append(text(x + 31, 130, f"Rec {i+1}", size=11, color=INK, bold=True, anchor="middle"))
        p.append(text(x + 31, 155, f"seq={100+i}", size=10, color=MUTED, anchor="middle"))

    # Pointers
    p.append(arrow(460, 160, 490, 160, color=POS, sw=2))
    p.append(text(475, 145, "Write", size=10, color=POS, bold=True, anchor="middle"))

    # Consumers below
    p.append(fitbox(490, 260, 140, 55, "Консольний потік\n(console kthread)", fill=COLD, stroke=ACCENT, sw=1.5, rx=6))
    p.append(fitbox(650, 260, 140, 55, "Простір користувача\n(/dev/kmsg)", fill=GREENFILL, stroke=POS, sw=1.5, rx=6))

    p.append(arrow(560, 220, 560, 260, color=ACCENT, sw=1.5))
    p.append(arrow(720, 220, 720, 260, color=POS, sw=1.5))

    render(os.path.join(OUT, "printk-buffer.svg"), W, H, *p, title="Буфер printk")


def fig_kmsg_flow():
    W, H = 820, 360
    p = []

    # Outer container
    p.append(rect(10, 10, 800, 340, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    p.append(text(30, 40, "Маршрутизація повідомлень ядра та засобів спостереження", size=15, color=INK, bold=True))

    # Kernel space box
    p.append(rect(30, 65, 360, 265, fill="#f7fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(50, 90, "Простір ядра (Kernel Space)", size=12, color=MUTED, bold=True))

    p.append(fitbox(50, 110, 150, 45, "Драйвери та ядро\npr_info() / pr_err()", fill=WARM, stroke=NEG, sw=1.5, rx=6))
    p.append(arrow(200, 132, 230, 132, color=INK, sw=1.5))

    p.append(rect(230, 105, 140, 175, fill=GREENFILL, stroke=POS, sw=2, rx=6))
    p.append(text(300, 130, "Кільцевий буфер", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text(300, 150, "printk_ringbuffer", size=11, color=INK, anchor="middle"))

    p.append(fitbox(240, 175, 120, 35, "Loglevel filter\n(console_loglevel)", fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(arrow(300, 210, 300, 230, color=INK, sw=1.5))
    p.append(fitbox(240, 230, 120, 40, "Консолі\nttyS0 / tty0", fill=COLD, stroke=ACCENT, sw=1, rx=4))

    # Userspace box
    p.append(rect(430, 65, 360, 265, fill="#f7fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(450, 90, "Простір користувача (User Space)", size=12, color=MUTED, bold=True))

    p.append(fitbox(450, 110, 140, 45, "Інтерфейс\n/dev/kmsg", fill=COLD, stroke=ACCENT, sw=1.5, rx=6))
    p.append(fitbox(450, 180, 140, 45, "Системний виклик\nsyslog(2) / klogctl", fill=MUTED_BG, stroke=MUTED, sw=1.5, rx=6))
    p.append(fitbox(450, 250, 140, 45, "Процедура cat\n/proc/kmsg", fill=MUTED_BG, stroke=MUTED, sw=1.5, rx=6))

    # Arrows from kernel ring buffer to userspace interfaces
    p.append(arrow(370, 132, 450, 132, color=ACCENT, sw=2))
    p.append(arrow(370, 160, 450, 202, color=MUTED, sw=1.5))
    p.append(arrow(370, 180, 450, 272, color=MUTED, sw=1.5))

    # Userspace daemons & tools (Grid alignment)
    p.append(fitbox(630, 110, 145, 45, "systemd-journald\n/ rsyslog", fill=GREENFILL, stroke=POS, sw=1.5, rx=6))
    p.append(fitbox(630, 180, 145, 45, "Сховище логів\n/var/log/kern.log", fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    p.append(fitbox(630, 250, 145, 45, "Утиліта dmesg\n/ stdout", fill=COLD, stroke=ACCENT, sw=1.5, rx=6))

    p.append(arrow(590, 132, 630, 132, color=POS, sw=1.5))
    p.append(arrow(702, 155, 702, 180, color=POS, sw=1.5))
    p.append(arrow(590, 272, 630, 272, color=ACCENT, sw=1.5))

    render(os.path.join(OUT, "kmsg-flow.svg"), W, H, *p, title="Маршрутизація kmsg")

fig_printk_buffer()
fig_kmsg_flow()
print("SVG figures generated successfully.")
