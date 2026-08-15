import os
import sys

# Шлях до scripts/ у корені репо (4 рівні вгору)
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

def generate_arch_svg():
    width = 750
    height = 450
    
    elements = []
    # Background
    elements.append(rect(0, 0, width, height, fill="#ffffff", stroke="none"))
    
    # Title
    elements.append(text(width / 2, 30, "Архітектура планування sched_ext (eBPF struct_ops)", size=16, bold=True, color="#1a1a1a"))
    
    # User space container
    elements.append(rect(30, 50, 690, 110, fill="#f4f6f8", stroke="#1976d2", sw=1.5, rx=6))
    elements.append(text(120, 75, "User Space (Демон розкладу)", size=14, bold=True, color="#1976d2", anchor="start"))
    
    # User space daemon box
    elements.append(rect(450, 70, 240, 70, fill="#e3f2fd", stroke="#1565c0", sw=1.5, rx=4))
    elements.append(text(570, 95, "Демон (Rust / C++ / Go)", size=13, bold=True, color="#0d47a1"))
    elements.append(text(570, 118, "scx_rustland / scx_lavd", size=11, color="#1565c0"))
    
    # User space description
    elements.append(text(60, 100, "• Обчислення складних моделей розкладу", size=11, color="#333333", anchor="start"))
    elements.append(text(60, 120, "• Отримання подій через BPF ringbuffer", size=11, color="#333333", anchor="start"))
    
    # Boundary line (System Call / BPF Interface)
    elements.append(line(30, 180, 720, 180, color="#9e9e9e", sw=1.5, dash="6,4"))
    elements.append(text(375, 175, "Межа ядра (Syscall / BPF Maps & Ringbuffer)", size=11, italic=True, color="#616161"))
    
    # Kernel space container
    elements.append(rect(30, 200, 690, 220, fill="#f9fbe7", stroke="#388e3c", sw=1.5, rx=6))
    elements.append(text(120, 225, "Kernel Space (ext_sched_class & BPF)", size=14, bold=True, color="#2e7d32", anchor="start"))
    
    # BPF struct_ops box
    elements.append(rect(50, 245, 290, 155, fill="#e8f5e9", stroke="#2e7d32", sw=1.5, rx=4))
    elements.append(text(195, 268, "BPF_PROG_TYPE_STRUCT_OPS", size=13, bold=True, color="#1b5e20"))
    elements.append(text(195, 290, "struct sched_ext_ops", size=12, bold=True, color="#2e7d32"))
    elements.append(text(70, 315, "• ops.select_cpu()  [вибір CPU]", size=11, color="#1b5e20", anchor="start"))
    elements.append(text(70, 335, "• ops.enqueue()     [черга DSQ]", size=11, color="#1b5e20", anchor="start"))
    elements.append(text(70, 355, "• ops.dispatch()    [видача task]", size=11, color="#1b5e20", anchor="start"))
    elements.append(text(70, 375, "• ops.running() / ops.stopping()", size=11, color="#1b5e20", anchor="start"))
    
    # Core Scheduler Box
    elements.append(rect(390, 245, 310, 155, fill="#fff8e1", stroke="#f57f17", sw=1.5, rx=4))
    elements.append(text(545, 268, "Ядро планувальника Linux", size=13, bold=True, color="#e65100"))
    elements.append(text(545, 290, "ext_sched_class (між RT і Fair)", size=12, color="#f57f17"))
    elements.append(text(410, 318, "• Черги DSQ (Global / Local / Custom)", size=11, color="#424242", anchor="start"))
    elements.append(text(410, 340, "• scx_watchdog (таймаут та захист)", size=11, color="#c62828", anchor="start"))
    elements.append(text(410, 362, "• Fallback на EEVDF/CFS при помилці", size=11, color="#c62828", anchor="start"))
    
    # Connections / Arrows
    # BPF <-> Core
    elements.append(arrow(340, 310, 390, 310, color="#2e7d32", sw=1.5))
    elements.append(arrow(390, 340, 340, 340, color="#e65100", sw=1.5))
    
    # User <-> Kernel BPF Maps
    elements.append(arrow(570, 140, 570, 245, color="#1976d2", sw=1.5))
    
    render(os.path.join(IMG_DIR, 'sched-ext-arch.svg'), width, height, *elements)

def generate_dsq_svg():
    width = 750
    height = 420
    
    elements = []
    
    # Title
    elements.append(text(width / 2, 28, "Ієрархія черг диспетчеризації (DSQ — Dispatch Queue)", size=16, bold=True, color="#1a1a1a"))
    
    # Runnable Tasks Box
    elements.append(rect(40, 60, 670, 65, fill="#e8eaf6", stroke="#3f51b5", sw=1.5, rx=4))
    elements.append(text(60, 85, "Потоки (Tasks):", size=12, bold=True, color="#1a237e", anchor="start"))
    
    # Task items
    elements.append(rect(170, 75, 90, 35, fill="#c5cae9", stroke="#303f9f", rx=3))
    elements.append(text(215, 97, "Task A (RT/GUI)", size=10, bold=True, color="#1a237e"))
    
    elements.append(rect(280, 75, 90, 35, fill="#c5cae9", stroke="#303f9f", rx=3))
    elements.append(text(325, 97, "Task B (Worker)", size=10, bold=True, color="#1a237e"))
    
    elements.append(rect(390, 75, 90, 35, fill="#c5cae9", stroke="#303f9f", rx=3))
    elements.append(text(435, 97, "Task C (Batch)", size=10, bold=True, color="#1a237e"))
    
    elements.append(rect(500, 75, 180, 35, fill="#ffffff", stroke="#9e9e9e", rx=3))
    elements.append(text(590, 97, "BPF ops.select_cpu / enqueue", size=10, italic=True, color="#616161"))
    
    # Arrow down to DSQs
    elements.append(arrow(375, 125, 375, 160, color="#3f51b5", sw=2))
    
    # DSQ Container
    elements.append(rect(40, 165, 670, 150, fill="#fafafa", stroke="#616161", sw=1.5, rx=4))
    elements.append(text(60, 188, "Типи черг DSQ (Dispatch Queues):", size=12, bold=True, color="#212121", anchor="start"))
    
    # SCX_DSQ_GLOBAL
    elements.append(rect(60, 205, 190, 95, fill="#ffe0b2", stroke="#f57c00", sw=1.5, rx=4))
    elements.append(text(155, 228, "SCX_DSQ_GLOBAL", size=12, bold=True, color="#e65100"))
    elements.append(text(155, 248, "Глобальна FIFO черга", size=10, color="#ef6c00"))
    elements.append(text(155, 268, "для всіх вільних CPU", size=10, color="#ef6c00"))
    elements.append(text(155, 288, "(Fallback за замовчуванням)", size=9, italic=True, color="#bf360c"))
    
    # Local Per-CPU DSQs
    elements.append(rect(280, 205, 190, 95, fill="#e1f5fe", stroke="#0288d1", sw=1.5, rx=4))
    elements.append(text(375, 228, "SCX_DSQ_LOCAL", size=12, bold=True, color="#01579b"))
    elements.append(text(375, 248, "Локальні черги CPU", size=10, color="#0277bd"))
    elements.append(text(375, 268, "SCX_DSQ_LOCAL_ON(cpu)", size=10, color="#0277bd"))
    elements.append(text(375, 288, "Прив'язка до L1/L2 кешу", size=9, italic=True, color="#01579b"))
    
    # Custom BPF DSQs
    elements.append(rect(500, 205, 190, 95, fill="#f3e5f5", stroke="#7b1fa2", sw=1.5, rx=4))
    elements.append(text(595, 228, "Custom DSQ (ID: 1..N)", size=12, bold=True, color="#4a148c"))
    elements.append(text(595, 248, "scx_bpf_create_dsq()", size=10, color="#6a1b9a"))
    elements.append(text(595, 268, "Пріоритетні / FIFO / RB-Tree", size=10, color="#6a1b9a"))
    elements.append(text(595, 288, "Спеціалізований QoS", size=9, italic=True, color="#4a148c"))
    
    # Arrows to CPUs
    elements.append(arrow(155, 300, 155, 340, color="#f57c00", sw=1.5))
    elements.append(arrow(375, 300, 375, 340, color="#0288d1", sw=1.5))
    elements.append(arrow(595, 300, 595, 340, color="#7b1fa2", sw=1.5))
    
    # CPU Execution Units
    elements.append(rect(40, 345, 670, 55, fill="#e8f5e9", stroke="#2e7d32", sw=1.5, rx=4))
    elements.append(text(60, 378, "Процесори (CPUs):", size=12, bold=True, color="#1b5e20", anchor="start"))
    
    elements.append(rect(210, 355, 100, 35, fill="#c8e6c9", stroke="#2e7d32", rx=3))
    elements.append(text(260, 377, "CPU 0 (Core 0)", size=10, bold=True, color="#1b5e20"))
    
    elements.append(rect(340, 355, 100, 35, fill="#c8e6c9", stroke="#2e7d32", rx=3))
    elements.append(text(390, 377, "CPU 1 (Core 1)", size=10, bold=True, color="#1b5e20"))
    
    elements.append(rect(470, 355, 100, 35, fill="#c8e6c9", stroke="#2e7d32", rx=3))
    elements.append(text(520, 377, "CPU N (Core N)", size=10, bold=True, color="#1b5e20"))
    
    render(os.path.join(IMG_DIR, 'sched-ext-dsq.svg'), width, height, *elements)

def main():
    generate_arch_svg()
    generate_dsq_svg()
    print("SVG diagrams generated successfully.")

if __name__ == '__main__':
    main()
