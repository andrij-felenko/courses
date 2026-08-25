# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_sched_ext_arch():
    W, H = 1000, 600
    p = []

    # Title / Top boundary
    p.append(fitbox(40, 20, 920, 44,
                    "Гібридна та вбудована архітектура BPF-планувальників у sched_ext",
                    size=16, fill="#f4f6f8", stroke=INK, sw=1.5))

    # User Space Container
    p.append(fitbox(40, 80, 920, 150,
                    "",
                    fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=8))
    p.append(fitbox(50, 90, 200, 30, "User Space (Простір користувача)", size=13, fill="#eaeded", stroke=None))

    # scx_rustland User Daemon
    p.append(fitbox(80, 130, 380, 80,
                    ["scx_rustland (Rust User Daemon)",
                     "• Алгоритми прийняття рішень (RB-tree, пріоритети)",
                     "• Безпечна обробка помилок (без kernel panic)"],
                    size=12, fill="#f5eeef", stroke=POS, sw=1.5))

    # User Space Admin / Control Tool (for LAVD)
    p.append(fitbox(540, 130, 380, 80,
                    ["scx_lavd (User Control & Stats)",
                     "• Динамічне налаштування профілів (Gaming / Eco)",
                     "• Моніторинг затримок та топології CCX"],
                    size=12, fill="#eef3fb", stroke=NEG, sw=1.5))

    # Boundary line / IPC
    p.append(fitbox(40, 240, 920, 36,
                    "Інтерфейс ядра / BPF Maps / BPF Ring Buffer / struct_ops",
                    size=13, fill="#fef9e7", stroke="#f1c40f", sw=1.5))

    # Arrows crossing boundary
    p.append(arrow(270, 210, 270, 240))
    p.append(arrow(730, 210, 730, 240))
    p.append(arrow(270, 276, 270, 300))
    p.append(arrow(730, 276, 730, 300))

    # Kernel Space Container
    p.append(fitbox(40, 300, 920, 270,
                    "",
                    fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=8))
    p.append(fitbox(50, 310, 200, 30, "Kernel Space (Ядро Linux)", size=13, fill="#eaeded", stroke=None))

    # BPF Program for Rustland (Kernel side)
    p.append(fitbox(80, 350, 380, 75,
                    ["BPF Program (scx_rustland.bpf.c)",
                     "• enqueue: перенаправляє події в RingBuf",
                     "• dispatch: вичитує рішення з BPF Map"],
                    size=12, fill="#fcf3cf", stroke="#f39c12", sw=1.5))

    # BPF Program for LAVD (Kernel side)
    p.append(fitbox(540, 350, 380, 75,
                    ["BPF Program (scx_lavd.bpf.c)",
                     "• 100% логіки планування в ядрі (vruntime + deadline)",
                     "• Прямий dispatch в NUMA/CCX DSQ"],
                    size=12, fill="#d4efdf", stroke=FIELD, sw=1.5))

    # Core Scheduler & DSQs
    p.append(fitbox(80, 445, 840, 55,
                    ["Core Scheduler (kernel/sched/ext.c)",
                     "• Dispatch Queues (DSQ): Local DSQ (per-CPU), Global DSQ, Custom DSQs",
                     "• Перемикання контексту задач на виконуючих ядрах CPU"],
                    size=12.5, fill="#ebf5fb", stroke="#3498db", sw=1.5))

    # Hardware Cores
    p.append(fitbox(80, 515, 840, 40,
                    "Фізичні ядра CPU0 .. CPU N (E-cores / P-cores / AMD CCX)",
                    size=13, fill="#e5e7e9", stroke=INK, sw=1.5))

    # Output SVG
    out_path = os.path.join(OUT, "sched-ext-arch.svg")
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")


def fig_scx_lavd_topology():
    W, H = 1000, 520
    p = []

    # Title
    p.append(fitbox(40, 20, 920, 44,
                    "Топологічне ущільнення та керування затримками в scx_lavd",
                    size=16, fill="#f4f6f8", stroke=INK, sw=1.5))

    # Task Streams
    p.append(fitbox(60, 80, 420, 70,
                    ["Критичні до затримки потоки (Gaming / Render)",
                     "• Жорсткий vruntime deadline",
                     "• Закріплення за спільним L3/CCX domain"],
                    size=12, fill="#fef9e7", stroke="#f39c12", sw=1.5))

    p.append(fitbox(520, 80, 420, 70,
                    ["Фонові & некритичні потоки (Downloads / Shaders)",
                     "• Ущільнення (Core Compaction)",
                     "• Виконання на обмеженій групі ядер (Енергозбереження)"],
                    size=12, fill="#eef3fb", stroke=NEG, sw=1.5))

    # Arrows to CCX Domains
    p.append(arrow(270, 150, 270, 190))
    p.append(arrow(730, 150, 730, 190))

    # CCX Domain 0 (Active & Warm L3 Cache)
    p.append(fitbox(60, 190, 420, 200,
                    "",
                    fill="#fcfcfc", stroke=FIELD, sw=1.5, rx=8))
    p.append(fitbox(70, 200, 300, 30, "AMD CCX 0 / L3 Cache Domain (Активні ядра)", size=13, fill="#eafaf1", stroke=None))

    p.append(fitbox(80, 240, 180, 60, ["CPU 0", "Custom DSQ 0"], size=12, fill="#d4efdf", stroke=FIELD, sw=1.5))
    p.append(fitbox(280, 240, 180, 60, ["CPU 1", "Custom DSQ 0"], size=12, fill="#d4efdf", stroke=FIELD, sw=1.5))
    p.append(fitbox(80, 315, 180, 60, ["CPU 2", "Custom DSQ 0"], size=12, fill="#d4efdf", stroke=FIELD, sw=1.5))
    p.append(fitbox(280, 315, 180, 60, ["CPU 3", "Custom DSQ 0"], size=12, fill="#d4efdf", stroke=FIELD, sw=1.5))

    # CCX Domain 1 (Compacted / Deep Sleep C-states)
    p.append(fitbox(520, 190, 420, 200,
                    "",
                    fill="#fcfcfc", stroke=POS, sw=1.5, rx=8))
    p.append(fitbox(530, 200, 340, 30, "AMD CCX 1 / L3 Domain (Ущільнені / Сплячі ядра)", size=13, fill="#f5eeef", stroke=None))

    p.append(fitbox(540, 240, 180, 60, ["CPU 4", "Фонова DSQ 1"], size=12, fill="#ebf5fb", stroke="#3498db", sw=1.5))
    p.append(fitbox(740, 240, 180, 60, ["CPU 5 (Deep Sleep)", "C6 C-state"], size=12, fill="#eaeded", stroke="#95a5a6", sw=1.5))
    p.append(fitbox(540, 315, 180, 60, ["CPU 6 (Deep Sleep)", "C6 C-state"], size=12, fill="#eaeded", stroke="#95a5a6", sw=1.5))
    p.append(fitbox(740, 315, 180, 60, ["CPU 7 (Deep Sleep)", "C6 C-state"], size=12, fill="#eaeded", stroke="#95a5a6", sw=1.5))

    # Result Summary
    p.append(fitbox(60, 415, 880, 60,
                    ["Результат оптимізації LAVD: мікросекундна затримка для ігрових потоків без промахів L3-кешу,",
                     "та суттєва економія батареї завдяки утримуванню вільних ядер процесора у стані глибокого сну."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.5))

    # Output SVG
    out_path = os.path.join(OUT, "scx-lavd-topology.svg")
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_sched_ext_arch()
    fig_scx_lavd_topology()
