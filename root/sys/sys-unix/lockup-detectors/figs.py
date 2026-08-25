# -*- coding: utf-8 -*-
import sys
import os

# Add scripts directory to path (4 levels up from topic dir: reference/unix-linux/observability/lockup-detectors)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import (
    render, text, mtext, rect, line, arrow, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "img")
os.makedirs(IMG_DIR, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"

def make_box(x, y, w, h, title, subtitle="", fill_color=FILL, border_color=LINE, title_color=INK):
    res = []
    res.append(rect(x, y, w, h, fill=fill_color, stroke=border_color, sw=1.5, rx=6))
    if subtitle:
        res.append(text(x + w / 2, y + 20, title, size=13, color=title_color, bold=True))
        lines = subtitle.split("\n")
        res.append(mtext(x + w / 2, y + 38, lines, size=11, color=MUTED))
    else:
        res.append(text(x + w / 2, y + h / 2 + 4, title, size=13, color=title_color, bold=True))
    return "".join(res)

def fig_lockup_types_matrix():
    w, h = 880, 480
    frags = []
    
    # Title
    frags.append(text(440, 30, "Класифікація та матриця виявлення ядерних зависань", size=16, color=INK, bold=True))
    
    # Column 1: Hard Lockup
    frags.append(rect(40, 60, 250, 400, fill=RED_FILL, stroke=POS, sw=1.8, rx=8))
    frags.append(text(165, 90, "Hard Lockup", size=15, color=POS, bold=True))
    frags.append(text(165, 110, "Апаратний параліч ядра CPU", size=11, color=MUTED))
    frags.append(line(55, 125, 275, 125, color=POS, sw=1))
    
    col1_items = [
        ("Стан переривань", "local_irq_disable() (IRQ вимкнено)\nНеможливість обробки звичайних переривань"),
        ("Рівень проблеми", "Нескінченний цикл у коді ядра/ISR\nАпаратний dead-lock у спинлоку"),
        ("Механізм виявлення", "NMI Watchdog (perf_event)\nНемасковані переривання NMI"),
        ("Типовий поріг", "watchdog_thresh (замовчування: 10 с)"),
        ("Наслідок / Реакція", "Watchdog detected hard LOCKUP\nМожлива паніка (hardlockup_panic)")
    ]
    
    cy = 145
    for heading, detail in col1_items:
        frags.append(text(60, cy, heading, size=12, color=POS, bold=True, anchor="start"))
        lines = detail.split("\n")
        frags.append(mtext(60, cy + 16, lines, size=10.5, color=INK, anchor="start"))
        cy += 52
        
    # Column 2: Soft Lockup
    frags.append(rect(315, 60, 250, 400, fill=WARM_FILL, stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(440, 90, "Soft Lockup", size=15, color="#d97706", bold=True))
    frags.append(text(440, 110, "Програмне монополізування CPU", size=11, color=MUTED))
    frags.append(line(330, 125, 550, 125, color="#d97706", sw=1))
    
    col2_items = [
        ("Стан переривань", "IRQ увімкнено (таймери цокають)\nПреемпцію вимкнено / немає yield"),
        ("Рівень проблеми", "Нескінченний цикл у Ring 0 без schedule()\nГолодування потоків користувача"),
        ("Механізм виявлення", "hrtimer + потік [watchdog/K]\n(перевірка watchdog_touch_ts)"),
        ("Типовий поріг", "2 * watchdog_thresh (типово: 20 с)"),
        ("Наслідок / Реакція", "BUG: soft lockup - CPU#K stuck\nМожлива паніка (softlockup_panic)")
    ]
    
    cy = 145
    for heading, detail in col2_items:
        frags.append(text(335, cy, heading, size=12, color="#d97706", bold=True, anchor="start"))
        lines = detail.split("\n")
        frags.append(mtext(335, cy + 16, lines, size=10.5, color=INK, anchor="start"))
        cy += 52

    # Column 3: Hung Task
    frags.append(rect(590, 60, 250, 400, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(715, 90, "Hung Task (D-state)", size=15, color=NEG, bold=True))
    frags.append(text(715, 110, "Зависання окремого процесу", size=11, color=MUTED))
    frags.append(line(605, 125, 825, 125, color=NEG, sw=1))
    
    col3_items = [
        ("Стан переривань", "CPU активний, планувальник працює\nЗависла конкретна задача"),
        ("Рівень проблеми", "TASK_UNINTERRUPTIBLE (D-state)\nБлокування на I/O, NFS чи м'ютексі"),
        ("Механізм виявлення", "Демон ядра [khungtaskd]\n(перевірка nvcsw + nivcsw)"),
        ("Типовий поріг", "hung_task_timeout_secs (типово: 120 с)"),
        ("Наслідок / Реакція", "INFO: task blocked for >120s\nМожлива паніка (hung_task_panic)")
    ]
    
    cy = 145
    for heading, detail in col3_items:
        frags.append(text(610, cy, heading, size=12, color=NEG, bold=True, anchor="start"))
        lines = detail.split("\n")
        frags.append(mtext(610, cy + 16, lines, size=10.5, color=INK, anchor="start"))
        cy += 52

    render(os.path.join(IMG_DIR, "lockup-types-matrix.svg"), w, h, *frags, title="Класифікація та матриця виявлення ядерних зависань")

def fig_soft_vs_hard_detector_arch():
    w, h = 880, 520
    frags = []
    
    # Header
    frags.append(text(440, 25, "Внутрішня архітектура Soft Lockup та Hard Lockup детекторів", size=15, color=INK, bold=True))
    
    # Left container: Soft Lockup
    frags.append(rect(30, 45, 395, 455, fill=WARM_FILL, stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(227, 70, "Soft Lockup Detector (hrtimer + kthread)", size=13, color="#d97706", bold=True))
    
    # Step 1: kthread watchdog/K
    frags.append(rect(50, 95, 355, 75, fill=BG, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(227, 118, "Ядерний потік [watchdog/K]", size=12, color=INK, bold=True))
    frags.append(mtext(227, 138, ["Пріоритет: SCHED_FIFO 99 (найвищий)", "Дія: touch_softlockup_watchdog()", "Оновлює: watchdog_touch_ts = now()"], size=10.5, color=MUTED))
    
    # Down arrow
    frags.append(arrow(227, 170, 227, 205, color=LINE, sw=1.5))
    frags.append(text(240, 190, "кожні sample_period (4 с)", size=10, color=MUTED, anchor="start"))
    
    # Step 2: hrtimer
    frags.append(rect(50, 205, 355, 80, fill=BG, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(227, 228, "Високоточний таймер watchdog_hrtimer", size=12, color=INK, bold=True))
    frags.append(mtext(227, 248, ["Спрацьовує в контексті апаратного таймера", "Обчислює: delta = now() - watchdog_touch_ts", "Збільшує лічильник: hrtimer_interrupts++"], size=10.5, color=MUTED))
    
    # Decision branch
    frags.append(arrow(227, 285, 227, 320, color=LINE, sw=1.5))
    
    frags.append(rect(50, 320, 355, 60, fill=WARM_FILL, stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(227, 342, "Перевірка: delta > 2 * watchdog_thresh (20 с)?", size=11.5, color="#d97706", bold=True))
    frags.append(text(227, 362, "Потік watchdog/K не отримував CPU через цикл у ядрі", size=10, color=MUTED))
    
    frags.append(arrow(227, 380, 227, 415, color=POS, sw=1.5))
    frags.append(text(235, 400, "Так (Зависання)", size=10.5, color=POS, bold=True, anchor="start"))
    
    # Soft lockup trigger
    frags.append(rect(50, 415, 355, 65, fill=RED_FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(227, 435, "BUG: soft lockup - CPU#K stuck for Ns!", size=11.5, color=POS, bold=True))
    frags.append(mtext(227, 455, ["Дамп стека поточного коду через printk", "Якщо softlockup_panic=1 -> panic()"], size=10, color=INK))

    # Right container: Hard Lockup
    frags.append(rect(455, 45, 395, 455, fill=RED_FILL, stroke=POS, sw=1.5, rx=8))
    frags.append(text(652, 70, "Hard Lockup Detector (NMI + perf_event)", size=13, color=POS, bold=True))
    
    # Step 1: CPU stalls with local_irq_disable()
    frags.append(rect(475, 95, 355, 75, fill=BG, stroke=POS, sw=1.2, rx=6))
    frags.append(text(652, 118, "Ядро виконує local_irq_disable()", size=12, color=POS, bold=True))
    frags.append(mtext(652, 138, ["Звичайні IRQ заблоковано на рівні CPU", "hrtimer НЕ МОЖЕ спрацювати", "hrtimer_interrupts НЕ збільшується"], size=10.5, color=MUTED))
    
    # Down arrow
    frags.append(arrow(652, 170, 652, 205, color=LINE, sw=1.5))
    frags.append(text(665, 190, "Апаратний таймер заблоковано", size=10, color=POS, anchor="start"))
    
    # Step 2: NMI Perf Counter
    frags.append(rect(475, 205, 355, 80, fill=BG, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(652, 228, "Апаратне переривання NMI (perf_event)", size=12, color=INK, bold=True))
    frags.append(mtext(652, 248, ["Генерується лічильником CPU (Local APIC)", "NMI ігнорує прапорець IF (пробиває cli)", "Викликає обробник watchdog_overflow_callback()"], size=10.5, color=MUTED))
    
    # Decision branch
    frags.append(arrow(652, 285, 652, 320, color=LINE, sw=1.5))
    
    frags.append(rect(475, 320, 355, 60, fill=WARM_FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(652, 342, "Перевірка: hrtimer_interrupts змінився?", size=11.5, color=POS, bold=True))
    frags.append(text(652, 362, "Чи збільшувався лічильник за останні 10 с?", size=10, color=MUTED))
    
    frags.append(arrow(652, 380, 652, 415, color=POS, sw=1.5))
    frags.append(text(660, 400, "Ні (IRQ вимкнено задовго)", size=10.5, color=POS, bold=True, anchor="start"))
    
    # Hard lockup trigger
    frags.append(rect(475, 415, 355, 65, fill=RED_FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(652, 435, "Watchdog detected hard LOCKUP on cpu K", size=11.5, color=POS, bold=True))
    frags.append(mtext(652, 455, ["Дамп регістрів процесора через NMI context", "Якщо hardlockup_panic=1 -> panic()"], size=10, color=INK))

    render(os.path.join(IMG_DIR, "soft-vs-hard-detector-arch.svg"), w, h, *frags, title="Внутрішня архітектура Soft Lockup та Hard Lockup детекторів")

def fig_hung_task_khungtaskd_flow():
    w, h = 880, 460
    frags = []
    
    frags.append(text(440, 25, "Алгоритм періодичного сканування демона khungtaskd", size=15, color=INK, bold=True))
    
    # Block 1: Sleep
    frags.append(rect(300, 50, 280, 55, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(440, 72, "Сон khungtaskd", size=13, color=NEG, bold=True))
    frags.append(text(440, 90, "Інтервал: timeout_secs / 2 (типово 60 с)", size=10.5, color=MUTED))
    
    frags.append(arrow(440, 105, 440, 135, color=LINE, sw=1.5))
    
    # Block 2: Loop processes
    frags.append(rect(280, 135, 320, 55, fill=BG, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 157, "Обхід for_each_process_thread(g, t)", size=13, color=INK, bold=True))
    frags.append(text(440, 175, "Сканування списку задач ядра під rcu_read_lock()", size=10.5, color=MUTED))
    
    frags.append(arrow(440, 190, 440, 220, color=LINE, sw=1.5))
    
    # Block 3: Decision - Task State
    frags.append(rect(270, 220, 340, 60, fill=WARM_FILL, stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(440, 242, "Перевірка стану: t->state == TASK_UNINTERRUPTIBLE?", size=12, color="#d97706", bold=True))
    frags.append(text(440, 262, "Чи перебуває потік у непереривному сні (D-state)?", size=10.5, color=MUTED))
    
    # Branch NO (left)
    frags.append(line(270, 250, 120, 250, color=LINE, sw=1.5))
    frags.append(arrow(120, 250, 120, 162, color=LINE, sw=1.5))
    frags.append(line(120, 162, 280, 162, color=LINE, sw=1.5))
    frags.append(text(190, 242, "Ні (R / S / Z)", size=10.5, color=MUTED, bold=True))
    
    # Branch YES (down)
    frags.append(arrow(440, 280, 440, 310, color=LINE, sw=1.5))
    frags.append(text(450, 298, "Так (D-state)", size=10.5, color=POS, bold=True, anchor="start"))
    
    # Block 4: Context switch counter check
    frags.append(rect(260, 310, 360, 65, fill=BG, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 332, "Перевірка лічильника перемикань контексту", size=12, color=INK, bold=True))
    frags.append(mtext(440, 352, ["switch_count = t->nvcsw + t->nivcsw", "Якщо switch_count == t->last_switch_count -> завис!"], size=10.5, color=MUTED))
    
    # Branch: Did switch_count change?
    frags.append(arrow(440, 375, 440, 400, color=POS, sw=1.5))
    
    # Block 5: Warning / Panic
    frags.append(rect(230, 400, 420, 50, fill=RED_FILL, stroke=POS, sw=1.5, rx=6))
    frags.append(text(440, 420, "INFO: task [PID] blocked for more than 120 seconds", size=12, color=POS, bold=True))
    frags.append(text(440, 438, "Вивід sched_show_task(t) -> Call Trace; якщо hung_task_panic=1 -> panic()", size=10, color=INK))
    
    render(os.path.join(IMG_DIR, "hung-task-khungtaskd-flow.svg"), w, h, *frags, title="Алгоритм періодичного сканування демона khungtaskd")

def fig_lockup_stacktrace_anatomy():
    w, h = 880, 500
    frags = []
    
    frags.append(text(440, 25, "Анатомія повідомлення та дампу стека при виявленні Soft Lockup", size=15, color=INK, bold=True))
    
    # Header box (Red)
    frags.append(rect(40, 50, 800, 65, fill=RED_FILL, stroke=POS, sw=1.8, rx=6))
    frags.append(text(60, 75, "BUG: soft lockup - CPU#2 stuck for 23s! [kworker/u8:2:1842]", size=14, color=POS, bold=True, anchor="start"))
    frags.append(mtext(60, 96, [
        "Пояснення: Ядро CPU#2 безперервно виконувало задачу kworker/u8:2 (PID 1842) протягом 23 секунд",
        "без передачі керування планувальнику (перевищено поріг 2 * watchdog_thresh = 20 с)"
    ], size=10.5, color=INK, anchor="start"))
    
    # Modules & Taint state (Grey)
    frags.append(rect(40, 125, 800, 55, fill=GREY_FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(60, 147, "Modules linked in: nf_conntrack iptable_nat ip_tables x_tables bonding [last unloaded: dummy]", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(60, 166, "CPU: 2 PID: 1842 Comm: kworker/u8:2 Tainted: G        W  O      5.15.0-89-generic #99-Ubuntu", size=11, color=MUTED, anchor="start"))
    
    # Hardware Registers (Blue)
    frags.append(rect(40, 190, 800, 85, fill=BLUE_FILL, stroke=NEG, sw=1.2, rx=6))
    frags.append(text(60, 212, "Апаратний стан процесора на момент виклику hrtimer interrupt:", size=11.5, color=NEG, bold=True, anchor="start"))
    frags.append(text(60, 232, "RIP: 0010:queued_spin_lock_slowpath+0x4b/0x2a0", size=11.5, color=POS, bold=True, anchor="start"))
    frags.append(text(60, 252, "RSP: 0018:ffffa4c241973cb0 EFLAGS: 00000202 ORIG_RAX: ffffffffffffff13", size=10.5, color=INK, anchor="start"))
    frags.append(text(60, 267, "RAX: 0000000000000101 RBX: ffff92840c5e8000 RCX: 0000000000000000 RDX: 0000000000000001", size=10.5, color=MUTED, anchor="start"))

    # Call Trace (Warm)
    frags.append(rect(40, 285, 800, 195, fill=WARM_FILL, stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(60, 307, "Call Trace (Ланцюжок викликів ядра / ORC Unwinder):", size=12, color="#d97706", bold=True, anchor="start"))
    
    trace_lines = [
        ("<IRQ>", "Переривання hrtimer спрацювало під час очікування spinlock"),
        ("queued_spin_lock_slowpath+0x4b/0x2a0", "Зависання в активному очікуванні qspinlock"),
        ("_raw_spin_lock_irqsave+0x32/0x40", "Спроба захоплення блокування з маскуванням локальних IRQ"),
        ("nf_conntrack_find_get+0x8a/0x140 [nf_conntrack]", "Пошук запису в таблиці conntrack (висока конкуренція за замок)"),
        ("nf_conntrack_in+0x215/0x560 [nf_conntrack]", "Обробка вхідного мережевого пакета підсистемою Netfilter"),
        ("process_one_work+0x1ee/0x3f0", "Виконання елемента черги воркерів workqueue"),
        ("worker_thread+0x53/0x3e0", "Головний цикл потоку kworker"),
        ("kthread+0x124/0x150", "Базова функція ядерного потоку")
    ]
    
    ty = 328
    for func, desc in trace_lines:
        frags.append(text(75, ty, func, size=10.5, color=INK, bold=True, anchor="start"))
        frags.append(text(460, ty, "/* " + desc + " */", size=10, color=MUTED, italic=True, anchor="start"))
        ty += 18

    render(os.path.join(IMG_DIR, "lockup-stacktrace-anatomy.svg"), w, h, *frags, title="Анатомія повідомлення та дампу стека при виявленні Soft Lockup")

if __name__ == "__main__":
    fig_lockup_types_matrix()
    fig_soft_vs_hard_detector_arch()
    fig_hung_task_khungtaskd_flow()
    fig_lockup_stacktrace_anatomy()
    print("Figures generated successfully in img/")
