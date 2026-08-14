# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"
DARK = "#1a202c"
PURPLE = "#f3e8ff"

def tb(cx, cy, lines, **kw):
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2

# ── 1. Load Average States (Process states in Linux Load Average) ────────────
def fig_load_avg():
    W, H = 860, 480
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", rx=0))
    p.append(text(W / 2, 32, "Формування Load Average у ядрі Linux", size=18, bold=True, color=DARK))
    
    # State boxes
    # TASK_RUNNING (CPU Executing)
    f, x0a, x1a, y0a, y1a = tb(160, 130, "TASK_RUNNING\n(Виконується на CPU)", size=14, fill=GREEN, pad=12)
    p.append(f)

    # TASK_RUNNING (Runnable in scheduler queue)
    f, x0b, x1b, y0b, y1b = tb(430, 130, "TASK_RUNNING\n(Чекає в черзі runqueue)", size=14, fill=BLUE, pad=12)
    p.append(f)

    # TASK_UNINTERRUPTIBLE (D state)
    f, x0c, x1c, y0c, y1c = tb(700, 130, "TASK_UNINTERRUPTIBLE (D)\n(Чекає на I/O, NFS, swap)", size=14, fill=WARM, pad=12)
    p.append(f)

    # TASK_INTERRUPTIBLE (S state) - excluded
    f, x0d, x1d, y0d, y1d = tb(430, 410, "TASK_INTERRUPTIBLE (S)\n(Спить / чекає на сигнал)", size=13, fill=GREY, pad=10)
    p.append(f)

    # Inclusion container box
    p.append(rect(40, 70, 780, 140, fill="none", stroke="#2e7d32", sw=2))
    p.append(text(430, 85, "Враховуються в рахунку Load Average (calc_load)", size=13, bold=True, color="#2e7d32"))

    # Sampling tick box
    f, sx0, sx1, sy0, sy1 = tb(430, 270, "Таймер ядра calc_load() (кожні 5 сек / LOAD_FREQ)\nОбчислення згладженого середнього (EMA): active_tasks · exp + load · (1 - exp)", size=13, fill=PURPLE, pad=12)
    p.append(f)

    # Arrows from included states to sampling box
    p.append(arrow(160, y1a, 160, sy0, color="#1565c0", sw=1.5))
    p.append(arrow(430, y1b, 430, sy0, color="#1565c0", sw=1.5))
    p.append(arrow(700, y1c, 700, sy0, color="#1565c0", sw=1.5))

    # Exclusion arrow to S state
    p.append(arrow(430, sy1, 430, y0d, color="#d32f2f", sw=1.5))
    p.append(text(570, 345, "НЕ враховується в Load Avg", size=12, color="#d32f2f", italic=True))

    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(p) + '\n</svg>'
    with open(os.path.join(IMG, 'load-avg.svg'), 'w', encoding='utf-8') as f_out:
        f_out.write(svg)

# ── 2. PSI SOME vs FULL Timeline ─────────────────────────────────────────────
def fig_psi_stall():
    W, H = 860, 440
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", rx=0))
    p.append(text(W / 2, 32, "Різниця між станами голодування PSI: SOME проти FULL", size=18, bold=True, color=DARK))

    # SOME section
    p.append(rect(30, 65, 800, 150, fill="#f9fbe7", stroke="#afb42b", sw=1.5))
    p.append(text(430, 85, "PSI SOME (Частковий тиск): Принаймні один потік заблоковано на ресурсі", size=14, bold=True, color="#827717"))

    # Timelines for SOME
    # Thread 1: CPU running
    p.append(text(100, 125, "Потік A:", size=13))
    p.append(rect(160, 110, 630, 25, fill=GREEN, stroke="#2e7d32"))
    p.append(text(475, 127, "Виконується на CPU", size=12, color="#1b5e20"))

    # Thread 2: Stalled on I/O part of time
    p.append(text(100, 170, "Потік B:", size=13))
    p.append(rect(160, 155, 250, 25, fill=GREEN, stroke="#2e7d32"))
    p.append(text(285, 172, "CPU", size=12, color="#1b5e20"))
    p.append(rect(410, 155, 230, 25, fill=RED, stroke="#c62828"))
    p.append(text(525, 172, "Заблоковано на I/O (Stall)", size=12, color="#b71c1c"))
    p.append(rect(640, 155, 150, 25, fill=GREEN, stroke="#2e7d32"))
    p.append(text(715, 172, "CPU", size=12, color="#1b5e20"))

    # Highlight SOME interval
    p.append(rect(410, 105, 230, 80, fill="none", stroke="#d81b60", sw=2))
    p.append(text(525, 203, "Інтервал SOME: CPU працює (Потік A), але Потік B чекає I/O", size=12, color="#d81b60", italic=True))

    # FULL section
    p.append(rect(30, 240, 800, 170, fill="#fbe9e7", stroke="#d84315", sw=1.5))
    p.append(text(430, 260, "PSI FULL (Повний тиск): УСІ активні потоки заблоковано (CPU повністю простоює)", size=14, bold=True, color="#bf360c"))

    # Timelines for FULL
    p.append(text(100, 300, "Потік A:", size=13))
    p.append(rect(160, 285, 220, 25, fill=GREEN, stroke="#2e7d32"))
    p.append(text(270, 302, "CPU", size=12, color="#1b5e20"))
    p.append(rect(380, 285, 280, 25, fill=RED, stroke="#c62828"))
    p.append(text(520, 302, "Заблоковано на I/O / RAM (Stall)", size=12, color="#b71c1c"))
    p.append(rect(660, 285, 130, 25, fill=GREEN, stroke="#2e7d32"))

    p.append(text(100, 345, "Потік B:", size=13))
    p.append(rect(160, 330, 220, 25, fill=GREEN, stroke="#2e7d32"))
    p.append(rect(380, 330, 280, 25, fill=RED, stroke="#c62828"))
    p.append(text(520, 347, "Заблоковано на I/O / RAM (Stall)", size=12, color="#b71c1c"))
    p.append(rect(660, 330, 130, 25, fill=GREEN, stroke="#2e7d32"))

    # Highlight FULL interval
    p.append(rect(380, 280, 280, 80, fill="none", stroke="#b71c1c", sw=2.5))
    p.append(text(520, 395, "Інтервал FULL: Жоден потік не виконується, CPU втрачає 100% потужності", size=12, color="#b71c1c", bold=True))

    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(p) + '\n</svg>'
    with open(os.path.join(IMG, 'psi-stall.svg'), 'w', encoding='utf-8') as f_out:
        f_out.write(svg)

# ── 3. Kernel PSI Architecture & Userspace Triggers ─────────────────────────
def fig_psi_architecture():
    W, H = 880, 520
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", rx=0))
    p.append(text(W / 2, 32, "Архітектура підсистеми PSI та порігові тригери", size=18, bold=True, color=DARK))

    # Kernel space box
    p.append(rect(30, 65, 820, 220, fill="#f4f6f9", stroke="#455a64", sw=1.5))
    p.append(text(220, 90, "Простір ядра (Kernel Space)", size=14, bold=True, color="#37474f"))

    # Scheduler task state change
    f, x01, x11, y01, y11 = tb(160, 145, "Подія розкладу / I/O / Fault\npsi_task_change()\npsi_task_switch()", size=13, fill=BLUE, pad=10)
    p.append(f)

    # Per-CPU tracking & struct psi_group
    f, x02, x12, y02, y12 = tb(440, 145, "Облік станів процесів\nstruct psi_group_cpu\n(Маска PSI_MEM/IO_SOME/FULL)", size=13, fill=PURPLE, pad=10)
    p.append(f)

    # Aggregator worker
    f, x03, x13, y03, y13 = tb(720, 145, "Фоновий воркер\npsi_group_change()\n(Оновлення avg10/60/300)", size=13, fill=GREEN, pad=10)
    p.append(f)

    # Trigger checker
    f, x04, x14, y04, y14 = tb(440, 235, "Детектор тригерів (psi_trigger)\nПеревірка вікон 50ms..1s\n(Встановлення події wake_up)", size=13, fill=WARM, pad=10)
    p.append(f)

    # Internal arrows
    p.append(arrow(x11, 145, x02, 145, color="#1565c0", sw=1.5))
    p.append(arrow(x12, 145, x03, 145, color="#2e7d32", sw=1.5))
    p.append(arrow(440, y12, 440, y04, color="#e65100", sw=1.5))

    # Boundary indicator (VFS Interface)
    f_vfs, vfs_x0, vfs_x1, vfs_y0, vfs_y1 = tb(440, 315, "Інтерфейс VFS: /proc/pressure/* та cgroup.pressure", size=13, bold=True, fill="#ffffff", stroke="#78909c", pad=8)

    # Userspace box
    p.append(rect(30, 350, 820, 150, fill="#fafafa", stroke="#616161", sw=1.5))
    p.append(text(220, 375, "Простір користувача (Userspace)", size=14, bold=True, color="#424242"))

    # File open & write trigger spec
    f, ux01, ux11, uy01, uy11 = tb(130, 425, "Відкриття fd & write()\n\"some 150000 1000000\"\n(150ms тиску за 1s)", size=13, fill=BLUE, pad=10)
    p.append(f)

    # epoll / poll loop
    f, ux02, ux12, uy02, uy12 = tb(430, 425, "Реєстрація у epoll_wait()\nОчікування на події POLLPRI", size=13, fill=WARM, pad=10)
    p.append(f)

    # Reaction daemons (systemd-oomd, lmkd)
    f, ux03, ux13, uy03, uy13 = tb(730, 425, "Демони реагування\nsystemd-oomd / lmkd\n(Завершення cgroup / SIGKILL)", size=13, fill=RED, pad=10)
    p.append(f)

    # Arrows between kernel & userspace (routed cleanly around VFS box)
    p.append(arrow(ux11, 425, ux02, 425, color="#1565c0", sw=1.5))
    p.append(arrow(ux12, 425, ux03, 425, color="#c62828", sw=1.5))
    p.append(line(130, uy01, 130, 235, color="#0288d1", sw=1.5))
    p.append(arrow(130, 235, x04, 235, color="#0288d1", sw=1.5))
    p.append(line(430, y14, 430, vfs_y0 - 2, color="#e65100", sw=2))
    p.append(arrow(430, vfs_y1 + 2, 430, uy02, color="#e65100", sw=2))
    
    # Append VFS box on top
    p.append(f_vfs)

    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(p) + '\n</svg>'
    with open(os.path.join(IMG, 'psi-kernel-architecture.svg'), 'w', encoding='utf-8') as f_out:
        f_out.write(svg)

def render():
    fig_load_avg()
    fig_psi_stall()
    fig_psi_architecture()

if __name__ == '__main__':
    render()
