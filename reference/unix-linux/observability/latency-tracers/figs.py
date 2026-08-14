import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def build_osnoise_svg():
    W, H = 840, 450
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    
    out.append(text(W/2, 30, "Анатомія OS Noise: викрадення процесорного часу на ізольованому ядрі", size=18, bold=True))
    
    ly = 60
    box_leg1, _, _ = textbox(150, ly, "Корисна робота потоку (osnoise loop)", size=11, fill="#d5f5e3", stroke=FIELD)
    box_leg2, _, _ = textbox(420, ly, "Апаратне переривання (Hardware IRQ)", size=11, fill="#fadbd8", stroke=POS)
    box_leg3, _, _ = textbox(680, ly, "SoftIRQ / Kthread / SMI / NMI", size=11, fill="#fdebd0", stroke="#e67e22")
    out.extend([box_leg1, box_leg2, box_leg3])

    cpus = [
        ("CPU 0 (High Load)", [
            (160, 110, "#27ae60", "Work"),
            (275, 40, POS, "HW IRQ"),
            (320, 55, "#e67e22", "SoftIRQ"),
            (380, 230, "#27ae60", "Work"),
            (615, 30, POS, "IRQ"),
            (650, 120, "#27ae60", "Work")
        ]),
        ("CPU 1 (Isolated)", [
            (160, 240, "#27ae60", "Work"),
            (405, 30, POS, "NIC IRQ"),
            (440, 170, "#27ae60", "Work"),
            (615, 45, "#e67e22", "rcu_sched"),
            (665, 105, "#27ae60", "Work")
        ]),
        ("CPU 2 (RT Task)", [
            (160, 290, "#27ae60", "Work"),
            (455, 60, "#8e44ad", "SMI (BIOS)"),
            (520, 250, "#27ae60", "Work")
        ]),
        ("CPU 3 (Strict RT)", [
            (160, 400, "#27ae60", "Work (0 Noise)"),
            (565, 25, "#d35400", "NMI Watchdog"),
            (595, 175, "#27ae60", "Work")
        ])
    ]

    y_start = 120
    row_h = 75

    for idx, (label, segments) in enumerate(cpus):
        y = y_start + idx * row_h
        out.append(text(150, y + 22, label, size=12, bold=True, anchor="end", color=INK))
        
        for sx, swidth, color, stext in segments:
            out.append(rect(sx, y, swidth, 38, fill=color, stroke=LINE, sw=1.5, rx=4))
            if swidth >= 35:
                tcolor = "#ffffff" if color in [POS, "#e67e22", "#8e44ad", "#d35400", "#27ae60"] else INK
                out.append(text(sx + swidth/2, y + 23, stext, size=10, bold=True, color=tcolor))

    out.append(line(160, 405, 770, 405, color=LINE, sw=2))
    out.append(arrow(760, 405, 775, 405, color=LINE, sw=2))
    out.append(text(465, 430, "Час виконання (мікросекунди / TSC cycles)", size=12, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def build_timerlat_svg():
    W, H = 840, 450
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    out.append(text(W/2, 30, "Складові затримки періодичного таймера у timerlat", size=18, bold=True))

    x_target = 180
    x_irq = 380
    x_thread = 660

    y_top = 70
    y_bot = 350

    out.append(line(x_target, y_top + 50, x_target, y_bot, color=MUTED, sw=1.5, dash="5,5"))
    out.append(line(x_irq, y_top + 50, x_irq, y_bot, color=POS, sw=1.5, dash="5,5"))
    out.append(line(x_thread, y_top + 50, x_thread, y_bot, color=NEG, sw=1.5, dash="5,5"))

    b1, _, _ = textbox(x_target, y_top + 20, "T_target\nОчікуваний час\nспрацювання hrtimer", size=11, fill="#eef2f7")
    b2, _, _ = textbox(x_irq, y_top + 20, "T_irq\nВхід в обробник\nапаратного IRQ", size=11, fill="#fdedec", stroke=POS, color=POS, bold=True)
    b3, _, _ = textbox(x_thread, y_top + 20, "T_thread\nСтарт виконання\nRT-потоку на CPU", size=11, fill="#eaf2f8", stroke=NEG, color=NEG, bold=True)
    out.extend([b1, b2, b3])

    y_irq_lat = 190
    cx_irq = (x_target + x_irq) / 2
    out.append(line(x_target, y_irq_lat, cx_irq - 75, y_irq_lat, color=POS, sw=2))
    out.append(line(cx_irq + 75, y_irq_lat, x_irq, y_irq_lat, color=POS, sw=2))
    b_irq, _, _ = textbox(cx_irq, y_irq_lat, "IRQ Latency\n(Заборона IRQ / NMI / SMI)", size=11, fill="#fadbd8", stroke=POS, color=POS, bold=True)
    out.append(b_irq)

    y_th_lat = 260
    cx_th = (x_irq + x_thread) / 2
    out.append(line(x_irq, y_th_lat, cx_th - 90, y_th_lat, color=NEG, sw=2))
    out.append(line(cx_th + 90, y_th_lat, x_thread, y_th_lat, color=NEG, sw=2))
    b_th, _, _ = textbox(cx_th, y_th_lat, "Thread Latency\n(Планувальник / Конкуренція за CPU)", size=11, fill="#d6eaf8", stroke=NEG, color=NEG, bold=True)
    out.append(b_th)

    y_tot = 370
    cx_tot = (x_target + x_thread) / 2
    out.append(line(x_target, y_tot, cx_tot - 150, y_tot, color=FIELD, sw=2.5))
    out.append(line(cx_tot + 150, y_tot, x_thread, y_tot, color=FIELD, sw=2.5))
    b_tot, _, _ = textbox(cx_tot, y_tot, "Total Latency = IRQ Latency + Thread Latency", size=12, fill="#d4efdf", stroke=FIELD, color="#1e8449", bold=True)
    out.append(b_tot)

    out.append("</svg>")
    return "\n".join(out)

def build_rtla_arch_svg():
    W, H = 840, 460
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    out.append(text(W/2, 30, "Архітектура підсистеми RTLA та трасувальників ядра", size=18, bold=True))

    # Шар Простору Користувача (Userspace)
    out.append(rect(30, 55, 780, 115, fill="#f4f6f9", stroke="#a6acaf", sw=1.5, rx=8))
    # Ставимо мітку ліворуч у x=45..140 (до першої стрілки на x=160)
    out.append(text(45, 76, "Userspace", size=11, bold=True, anchor="start", color="#566573"))

    b1, _, _ = textbox(160, 120, "rtla osnoise\n(top / hist / cpus)", size=11, fill="#e8f8f5", stroke=FIELD, bold=True)
    out.append(b1)
    b2, _, _ = textbox(420, 120, "rtla timerlat\n(top / hist / -u)", size=11, fill="#eaf2f8", stroke=NEG, bold=True)
    out.append(b2)
    b3, _, _ = textbox(670, 120, "rtla hnoise\n(HW / SMI tracer)", size=11, fill="#fdedec", stroke=POS, bold=True)
    out.append(b3)

    # Лінія розділу VFS / tracefs
    b_vfs, _, _ = textbox(420, 190, "Інтерфейс tracefs (/sys/kernel/tracing/)", size=11, fill="#fcf3cf", stroke="#f1c40f", bold=True)

    out.append(line(30, 190, 280, 190, color=MUTED, sw=1.5, dash="4,4"))
    out.append(line(560, 190, 810, 190, color=MUTED, sw=1.5, dash="4,4"))
    out.append(b_vfs)

    # Шар Ядра (Kernel Space)
    out.append(rect(30, 220, 780, 225, fill="#ebedef", stroke="#7f8c8d", sw=1.5, rx=8))
    # Ставимо мітку ліворуч у x=45..140 (до першого блоку ядра)
    out.append(text(45, 242, "Kernel Space", size=11, bold=True, anchor="start", color="#2c3e50"))

    # Модулі osnoise & timerlat
    k1, _, _ = textbox(200, 295, "osnoise tracer\n(kthread loop + TSC read\npreempt_disable)", size=11, fill="#d5f5e3", stroke=FIELD)
    out.append(k1)
    k2, _, _ = textbox(640, 295, "timerlat tracer\n(hrtimer callback +\nIRQ/Thread timestamps)", size=11, fill="#d6eaf8", stroke=NEG)
    out.append(k2)

    # Інфраструктура ftrace & tracepoints
    k3, _, _ = textbox(420, 390, "Інфраструктура ftrace & Tracepoints\n(irq_handler_entry, softirq_entry, sched_switch, stop_tracing_us)", size=11, fill="#f5eeed", stroke=POS)
    out.append(k3)

    # Стрілки зв'язку (поза текстами)
    out.append(arrow(160, 150, 190, 260, color=FIELD, sw=1.8))
    out.append(arrow(420, 145, 420, 172, color=NEG, sw=1.8))
    out.append(arrow(420, 208, 420, 360, color=NEG, sw=1.8))
    out.append(arrow(670, 150, 650, 260, color=POS, sw=1.8))

    out.append(arrow(200, 330, 320, 365, color=FIELD, sw=1.5))
    out.append(arrow(640, 330, 520, 365, color=NEG, sw=1.5))

    out.append("</svg>")
    return "\n".join(out)

def main():
    with open(os.path.join(IMG_DIR, "osnoise.svg"), "w", encoding="utf-8") as f:
        f.write(build_osnoise_svg())
    with open(os.path.join(IMG_DIR, "timerlat.svg"), "w", encoding="utf-8") as f:
        f.write(build_timerlat_svg())
    with open(os.path.join(IMG_DIR, "rtla-architecture.svg"), "w", encoding="utf-8") as f:
        f.write(build_rtla_arch_svg())
    print("SVGs generated successfully.")

if __name__ == "__main__":
    main()
