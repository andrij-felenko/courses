# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")
    ),
)
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig_architecture():
    w, h = 840, 460
    frags = []

    # Заголовок
    frags.append(
        text(
            420,
            28,
            "Розділення ВФС ядра Linux: procfs, sysfs, debugfs та tracefs",
            size=16,
            bold=True,
        )
    )

    # Шар 1: Простір користувача (Top)
    frags.append(
        rect(20, 50, 800, 75, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8)
    )
    frags.append(
        text(
            420,
            68,
            "ПРОСТІР КОРИСТУВАЧА (USERSPACE)",
            size=13,
            bold=True,
            color="#475569",
        )
    )

    b_tools, _, _ = textbox(
        160,
        98,
        "Профільувальники\n(perf, trace-cmd, eBPF)",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    b_shell, _, _ = textbox(
        420,
        98,
        "Консольні утиліти\n(cat, echo, sysctl)",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    b_apps, _, _ = textbox(
        680,
        98,
        "Користувацькі\nдодатки / Демони",
        size=11,
        pad=6,
        fill="#e0f2fe",
        stroke="#0284c7",
    )
    frags.extend([b_tools, b_shell, b_apps])

    # Системні виклики (Стрілки вниз)
    frags.append(arrow(160, 122, 680, 160, color="#0284c7"))
    frags.append(arrow(420, 122, 420, 160, color="#0284c7"))
    frags.append(arrow(680, 122, 420, 160, color="#0284c7"))

    # Шар 2: Межа VFS (Middle)
    frags.append(
        rect(20, 160, 800, 140, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8)
    )
    frags.append(
        text(
            420,
            178,
            "ШАР ВІРТУАЛЬНИХ ФАЙЛОВИХ СИСТЕМ (VFS LAYER)",
            size=13,
            bold=True,
            color="#334155",
        )
    )

    v_proc, _, _ = textbox(
        120,
        230,
        "procfs (/proc)\nСтан процесів\nта sysctl",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#3b82f6",
    )
    v_sys, _, _ = textbox(
        310,
        230,
        "sysfs (/sys)\nІєрархія kobject\nСуворий ABI",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#3b82f6",
    )
    v_debug, _, _ = textbox(
        510,
        230,
        "debugfs (/sys/kernel/debug)\nНалагодження драйверів\nБез гарантій ABI",
        size=11,
        pad=6,
        fill="#fef2f2",
        stroke="#ef4444",
    )
    v_trace, _, _ = textbox(
        710,
        230,
        "tracefs (/sys/kernel/tracing)\nІзольований ftrace\nПодії та кільцеві буфери",
        size=11,
        pad=6,
        fill="#f0fdf4",
        stroke="#16a34a",
    )
    frags.extend([v_proc, v_sys, v_debug, v_trace])

    # Стрілки з ВФС до ядра
    frags.append(arrow(120, 270, 240, 330, color="#64748b"))
    frags.append(arrow(310, 270, 320, 330, color="#64748b"))
    frags.append(arrow(510, 270, 560, 330, color="#ef4444"))
    frags.append(arrow(710, 270, 640, 330, color="#16a34a"))

    # Шар 3: Простір ядра (Bottom)
    frags.append(
        rect(20, 330, 800, 100, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8)
    )
    frags.append(
        text(
            420,
            348,
            "ВНУТРІШНІ ПІДСИСТЕМИ ЯДРА LINUX (KERNEL CORE)",
            size=13,
            bold=True,
            color="#475569",
        )
    )

    k_proc, _, _ = textbox(
        240,
        385,
        "Підсистема процесів & Менеджер пам'яті\n(task_struct, mm_struct, sysctl_table)",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    k_trace, _, _ = textbox(
        600,
        385,
        "Драйвери пристроїв & ftrace Engine\n(debugfs_nodes, tracepoints, ring_buffer)",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#64748b",
    )
    frags.extend([k_proc, k_trace])

    path = os.path.join(IMG_DIR, "debugfs-tracefs-architecture.svg")
    render(path, w, h, *frags)
    print(f"Generated {path}")


def build_fig_ring_buffer():
    w, h = 860, 420
    frags = []

    # Заголовок
    frags.append(
        text(
            430,
            26,
            "Механіка підсистеми tracefs та кільцевих буферів ftrace",
            size=16,
            bold=True,
        )
    )

    # Джерела трасування (Лівий блок)
    frags.append(
        rect(20, 60, 220, 330, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    )
    frags.append(
        text(
            130,
            82,
            "Джерела подій ядра",
            size=13,
            bold=True,
            color="#334155",
        )
    )

    s1, _, _ = textbox(
        130,
        125,
        "Tracepoints\n(Статичні точки)",
        size=11,
        pad=6,
        fill="#e0e7ff",
        stroke="#4338ca",
    )
    s2, _, _ = textbox(
        130,
        185,
        "kprobes / uprobes\n(Динамічні зонди)",
        size=11,
        pad=6,
        fill="#e0e7ff",
        stroke="#4338ca",
    )
    s3, _, _ = textbox(
        130,
        245,
        "Function Tracer\n(Виклики функцій)",
        size=11,
        pad=6,
        fill="#e0e7ff",
        stroke="#4338ca",
    )
    s4, _, _ = textbox(
        130,
        305,
        "Системні виклики\n(sys_enter / sys_exit)",
        size=11,
        pad=6,
        fill="#e0e7ff",
        stroke="#4338ca",
    )
    frags.extend([s1, s2, s3, s4])

    # Стрілки атомарного запису
    frags.append(arrow(240, 125, 270, 140, color="#4338ca"))
    frags.append(arrow(240, 185, 270, 190, color="#4338ca"))
    frags.append(arrow(240, 245, 270, 240, color="#4338ca"))
    frags.append(arrow(240, 305, 270, 290, color="#4338ca"))

    # Безблокувальний кільцевий буфер (Центральний блок)
    frags.append(
        rect(270, 60, 280, 330, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8)
    )
    frags.append(
        text(
            410,
            82,
            "Per-CPU Кільцеві буфери",
            size=13,
            bold=True,
            color="#14532d",
        )
    )

    rb0, _, _ = textbox(
        410,
        140,
        "CPU 0 Lockless Ring Buffer\n[ Сторінка 1 ] -> [ Сторінка 2 ]",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#15803d",
    )
    rb1, _, _ = textbox(
        410,
        215,
        "CPU 1 Lockless Ring Buffer\n[ Сторінка 1 ] -> [ Сторінка 2 ]",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#15803d",
    )
    rbn, _, _ = textbox(
        410,
        290,
        "CPU N Lockless Ring Buffer\n[ Сторінка 1 ] -> [ Сторінка 2 ]",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#15803d",
    )
    frags.extend([rb0, rb1, rbn])

    # Стрілки зчитування з буфера
    frags.append(arrow(550, 180, 580, 150, color="#16a34a"))
    frags.append(arrow(550, 240, 580, 270, color="#16a34a"))

    # Інтерфейси VFS в tracefs (Правий блок)
    frags.append(
        rect(580, 60, 260, 330, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8)
    )
    frags.append(
        text(
            710,
            82,
            "Інтерфейси tracefs",
            size=13,
            bold=True,
            color="#713f12",
        )
    )

    v_trace, _, _ = textbox(
        710,
        150,
        "/sys/kernel/tracing/trace\nСтатичний зріз\n(Без видалення даних)",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#a16207",
    )
    v_pipe, _, _ = textbox(
        710,
        270,
        "/sys/kernel/tracing/trace_pipe\nПотокове зчитування\n(Споживає буфер у реальному часі)",
        size=11,
        pad=6,
        fill="#ffffff",
        stroke="#a16207",
    )
    frags.extend([v_trace, v_pipe])

    path = os.path.join(IMG_DIR, "tracefs-ring-buffer.svg")
    render(path, w, h, *frags)
    print(f"Generated {path}")


if __name__ == "__main__":
    build_fig_architecture()
    build_fig_ring_buffer()
