# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_psi_stalls(img_dir):
    w, h = 850, 430
    frags = []

    # Title
    frags.append(text(w / 2, 30, "Модель затримок PSI: розмежування режимів 'some' та 'full'", size=16, bold=True))

    COLOR_RUN = "#c8e6c9"      # Running on CPU (green)
    COLOR_SOME = "#ffe0b2"     # Some stall (orange)
    COLOR_FULL = "#ef9a9a"     # Full stall (red)
    COLOR_IDLE = "#e0e0e0"     # Idle/Inactive (grey)

    # Time axis line
    frags.append(line(140, 330, 800, 330, color=LINE, sw=2))
    frags.append(arrow(800, 330, 820, 330, color=LINE, sw=2))
    frags.append(text(810, 350, "Час (t)", size=12, bold=True))

    # Grid vertical lines
    for t_val, x_pos in [(0, 160), (100, 260), (200, 360), (300, 460), (400, 560), (500, 660), (600, 760)]:
        frags.append(line(x_pos, 60, x_pos, 330, color="#e0e0e0", sw=1, dash="4,4"))
        frags.append(text(x_pos, 345, f"{t_val}мс", size=11, color=MUTED))

    # Task A timeline
    tb_a, _, _ = textbox(75, 85, "Завдання A", size=12, pad=6, fill=FILL, bold=True)
    frags.append(tb_a)
    frags.append(rect(160, 70, 150, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(235, 90, "CPU", size=11, bold=True))
    frags.append(rect(310, 70, 200, 30, fill=COLOR_SOME, stroke=LINE, rx=4))
    frags.append(text(410, 90, "Чекає пам'ять", size=11))
    frags.append(rect(510, 70, 250, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(635, 90, "CPU", size=11, bold=True))

    # Task B timeline
    tb_b, _, _ = textbox(75, 145, "Завдання B", size=12, pad=6, fill=FILL, bold=True)
    frags.append(tb_b)
    frags.append(rect(160, 130, 100, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(210, 150, "CPU", size=11, bold=True))
    frags.append(rect(260, 130, 350, 30, fill=COLOR_SOME, stroke=LINE, rx=4))
    frags.append(text(435, 150, "Чекає I/O", size=11))
    frags.append(rect(610, 130, 150, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(685, 150, "CPU", size=11, bold=True))

    # Task C timeline
    tb_c, _, _ = textbox(75, 205, "Завдання C", size=12, pad=6, fill=FILL, bold=True)
    frags.append(tb_c)
    frags.append(rect(160, 190, 200, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(260, 210, "CPU", size=11, bold=True))
    frags.append(rect(360, 190, 300, 30, fill=COLOR_SOME, stroke=LINE, rx=4))
    frags.append(text(510, 210, "Чекає пам'ять", size=11))
    frags.append(rect(660, 190, 100, 30, fill=COLOR_RUN, stroke=LINE, rx=4))
    frags.append(text(710, 210, "CPU", size=11, bold=True))

    # Divider line
    frags.append(line(20, 240, 830, 240, color=MUTED, sw=1, dash="2,2"))

    # PSI SOME Aggregated line (100ms - 500ms)
    tb_some, _, _ = textbox(75, 265, "PSI SOME", size=12, pad=6, fill=COLOR_SOME, bold=True)
    frags.append(tb_some)
    frags.append(rect(160, 250, 100, 30, fill=COLOR_IDLE, stroke=LINE, rx=4))
    frags.append(rect(260, 250, 400, 30, fill=COLOR_SOME, stroke=LINE, rx=4))
    frags.append(text(460, 270, "Принаймні 1 завдання заблоковане (100-500мс)", size=11, bold=True))
    frags.append(rect(660, 250, 100, 30, fill=COLOR_IDLE, stroke=LINE, rx=4))

    # PSI FULL Aggregated line (200ms - 350ms)
    tb_full, _, _ = textbox(75, 305, "PSI FULL", size=12, pad=6, fill=COLOR_FULL, bold=True)
    frags.append(tb_full)
    frags.append(rect(160, 290, 200, 30, fill=COLOR_IDLE, stroke=LINE, rx=4))
    frags.append(rect(360, 290, 150, 30, fill=COLOR_FULL, stroke=LINE, rx=4))
    frags.append(text(435, 310, "УСІ активні завдання чекають (200-350мс)", size=11, bold=True))
    frags.append(rect(510, 290, 250, 30, fill=COLOR_IDLE, stroke=LINE, rx=4))

    # Legend at bottom
    frags.append(rect(140, 380, 20, 20, fill=COLOR_RUN, stroke=LINE, rx=3))
    frags.append(text(170, 395, "Робота CPU", size=11, anchor="start"))

    frags.append(rect(310, 380, 20, 20, fill=COLOR_SOME, stroke=LINE, rx=3))
    frags.append(text(340, 395, "Голодування SOME (1+ задач)", size=11, anchor="start"))

    frags.append(rect(560, 380, 20, 20, fill=COLOR_FULL, stroke=LINE, rx=3))
    frags.append(text(590, 395, "Голодування FULL (УСІ задачі)", size=11, anchor="start"))

    out_path = os.path.join(img_dir, "psi-stalls.svg")
    render(out_path, w, h, *frags)

def generate_psi_architecture(img_dir):
    w, h = 900, 460
    frags = []

    # Title
    frags.append(text(w / 2, 30, "Архітектурний потік підсистеми PSI від ядра до простору користувача", size=16, bold=True))

    # Layer 1: Kernel Core Event Generators
    tb1, w1, _ = textbox(160, 90, "Події ядра Linux\nscheduler, memstall,\nio_schedule", size=12, pad=10, fill="#e8f5e9", stroke=LINE, bold=True)
    frags.append(tb1)

    # Layer 2: Per-CPU aggregators
    tb2, w2, _ = textbox(450, 90, "Per-CPU лічильники\npsi_group_cpu\ntimes[] у наносекундах", size=12, pad=10, fill="#e3f2fd", stroke=LINE, bold=True)
    frags.append(tb2)

    frags.append(arrow(160 + w1/2, 90, 450 - w2/2, 90, color=LINE, sw=2))

    # Layer 3: Moving Average Decay Engine
    tb3, w3, _ = textbox(740, 90, "Обчислення EWMA (2 с)\npsi_avgs_work()\navg10, avg60, avg300", size=12, pad=10, fill="#fff3e0", stroke=LINE, bold=True)
    frags.append(tb3)

    frags.append(arrow(450 + w2/2, 90, 740 - w3/2, 90, color=LINE, sw=2))

    # Middle Arrow down to VFS & Triggers
    frags.append(arrow(450, 135, 450, 195, color=LINE, sw=2))
    frags.append(text(465, 165, "Агрегація ресурсів", size=11, anchor="start", italic=True))

    # Layer 4: Interfacing Nodes
    tb4a, w4a, _ = textbox(250, 240, "Procfs інтерфейс\n/proc/pressure/cpu\n/proc/pressure/memory\n/proc/pressure/io", size=12, pad=10, fill=FILL, stroke=LINE, bold=True)
    frags.append(tb4a)

    tb4b, w4b, _ = textbox(650, 240, "Cgroups v2 контролери\n/sys/fs/cgroup/<group>/\nmemory.pressure\nio.pressure", size=12, pad=10, fill=FILL, stroke=LINE, bold=True)
    frags.append(tb4b)

    frags.append(arrow(450, 195, 250, 195, color=LINE, sw=1.5))
    frags.append(arrow(250, 195, 250, 200, color=LINE, sw=1.5))
    frags.append(arrow(450, 195, 650, 195, color=LINE, sw=1.5))
    frags.append(arrow(650, 195, 650, 200, color=LINE, sw=1.5))

    # Layer 5: Triggers and User-Space System Daemons
    frags.append(arrow(250, 290, 250, 340, color=LINE, sw=2))
    frags.append(arrow(650, 290, 650, 340, color=LINE, sw=2))

    tb5a, _, _ = textbox(250, 385, "Сповіщення Triggers\npoll() / epoll() [POLLPRI]\nsome 150000 1000000", size=12, pad=10, fill="#fce4ec", stroke=LINE, bold=True)
    frags.append(tb5a)

    tb5b, _, _ = textbox(650, 385, "Демони простору користувача\nsystemd-oomd, lmkd,\nfb-oomd / Custom Monitor", size=12, pad=10, fill="#f3e5f5", stroke=LINE, bold=True)
    frags.append(tb5b)

    frags.append(arrow(370, 385, 520, 385, color=LINE, sw=2))
    frags.append(text(445, 375, "Сигнали OOM / SIGKILL", size=11, bold=True, color=POS))

    out_path = os.path.join(img_dir, "psi-architecture.svg")
    render(out_path, w, h, *frags)

def main():
    topic_dir = os.path.dirname(__file__)
    img_dir = os.path.join(topic_dir, "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    generate_psi_stalls(img_dir)
    generate_psi_architecture(img_dir)

if __name__ == "__main__":
    main()
