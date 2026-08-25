import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_figs():
    # Remove obsolete SVGs if present
    old_svg = os.path.join(IMG, 'perf-architecture.svg')
    if os.path.exists(old_svg):
        try:
            os.remove(old_svg)
        except OSError:
            pass

    # ── Figure 1: PMU Architecture & perf Event Flow ─────────────────────────
    frags1 = []
    
    # Layer 1: Hardware CPU & PMU
    frags1.append(rect(40, 60, 720, 100, fill="#f8f9fa", stroke="#6c757d", sw=1.5, rx=8))
    frags1.append(text(400, 82, "Апаратний рівень (CPU Silicon & PMU Registers)", size=14, bold=True, color="#343a40"))
    
    b_msr, _, _ = textbox(160, 120, "MSR / PMC Лічильники\nIA32_PERFEVTSELx\nIA32_PMC0..N", size=11, fill="#e3f2fd", stroke="#1976d2")
    frags1.append(b_msr)
    
    b_pebs, _, _ = textbox(400, 120, "Апаратний самплінг\nPEBS (Intel) / IBS (AMD)\nТочний RIP без скіду", size=11, fill="#e3f2fd", stroke="#1976d2")
    frags1.append(b_pebs)
    
    b_nmi, _, _ = textbox(630, 120, "Сигнал переповнення\nNMI (Non-Maskable Interrupt)\nМиттєве переривання", size=11, fill="#ffebee", stroke="#c62828")
    frags1.append(b_nmi)

    # Arrow HW -> Kernel
    frags1.append(arrow(630, 145, 630, 190, color="#c62828", sw=2))

    # Layer 2: Linux Kernel Core
    frags1.append(rect(40, 190, 720, 130, fill="#f1f8e9", stroke="#558b2f", sw=1.5, rx=8))
    frags1.append(text(400, 212, "Ядро Linux (perf_event Core & Event Handlers)", size=14, bold=True, color="#2e7d32"))
    
    b_handler, _, _ = textbox(180, 260, "Обробник NMI / Переривань\nФіксація RIP, PID/TID,\nCallchain, CPU ID", size=11, fill="#ffffff", stroke="#558b2f")
    frags1.append(b_handler)
    
    b_open, _, _ = textbox(410, 260, "perf_event_open()\nСтворення fd, group_fd,\nМультиплексування PMU", size=11, fill="#ffffff", stroke="#558b2f")
    frags1.append(b_open)
    
    b_rb_k, _, _ = textbox(630, 260, "Запис у кільцевий буфер\nВхідні події PERF_RECORD_\nЗахист бар'єром пам'яті", size=11, fill="#ffffff", stroke="#558b2f")
    frags1.append(b_rb_k)

    frags1.append(arrow(280, 260, 315, 260, color="#558b2f", sw=1.5))
    frags1.append(arrow(505, 260, 535, 260, color="#558b2f", sw=1.5))
    frags1.append(arrow(630, 320, 630, 360, color="#1565c0", sw=2))

    # Layer 3: Userspace Profiling Applications
    frags1.append(rect(40, 360, 720, 110, fill="#e8eaf6", stroke="#283593", sw=1.5, rx=8))
    frags1.append(text(400, 382, "Користувацький простір (Userspace Analysis)", size=14, bold=True, color="#1a237e"))

    b_mmap, _, _ = textbox(180, 425, "Спільна пам'ять mmap()\nБезкопіювальний доступ\nдо data_head / data_tail", size=11, fill="#ffffff", stroke="#283593")
    frags1.append(b_mmap)

    b_tools, _, _ = textbox(440, 425, "Утиліти perf stat / record / report\nВласні аналізатори на C / C++\nПобудова Flamegraph", size=11, fill="#ffffff", stroke="#283593")
    frags1.append(b_tools)

    frags1.append(arrow(630, 425, 560, 425, color="#283593", sw=1.5))
    frags1.append(arrow(300, 425, 335, 425, color="#283593", sw=1.5))

    render(os.path.join(IMG, 'perf-pmu-kernel-flow.svg'), 800, 490, *frags1, title="Архітектурний потік подій perf: PMU -> Ядро -> mmap буфер")

    # ── Figure 2: mmap Ring Buffer Layout ────────────────────────────────────
    frags2 = []
    
    # Header / Control Page
    frags2.append(rect(40, 60, 720, 90, fill="#fff3e0", stroke="#e65100", sw=1.5, rx=6))
    frags2.append(text(160, 82, "Сторінка управління (Page 0)", size=13, bold=True, color="#e65100"))
    frags2.append(text(160, 102, "struct perf_event_mmap_page", size=11, color="#bf360c"))

    b_dh, _, _ = textbox(400, 105, "data_head (зміщення ядра)\nОновлює ядро після NMI", size=11, fill="#ffffff", stroke="#e65100")
    frags2.append(b_dh)

    b_dt, _, _ = textbox(630, 105, "data_tail (зміщення користувача)\nОновлює користувач після читання", size=11, fill="#ffffff", stroke="#e65100")
    frags2.append(b_dt)

    # Ring Buffer Slots
    frags2.append(rect(40, 180, 720, 120, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=6))
    frags2.append(text(400, 202, "Кільцевий буфер даних (Ring Buffer Payload / Data Pages)", size=13, bold=True))

    # Sample slots
    slots = [
        (60, "Record #1\nSAMPLE\n(RIP, PID)", "#c8e6c9", "#2e7d32"),
        (200, "Record #2\nMMAP\n(addr, len)", "#bbdefb", "#1565c0"),
        (340, "Record #3\nSAMPLE\n(Callchain)", "#c8e6c9", "#2e7d32"),
        (480, "Вільна зона\n(Очікує на NMI)", "#ffffff", "#9e9e9e"),
        (620, "Непрочитане\n(Запис #0)", "#fff9c4", "#fbc02d"),
    ]

    for x_pos, label, f_col, s_col in slots:
        b_slot, _, _ = textbox(x_pos + 50, 255, label, size=10, fill=f_col, stroke=s_col)
        frags2.append(b_slot)

    # Cursor arrows
    frags2.append(arrow(400, 135, 430, 220, color="#e65100", sw=2))
    frags2.append(arrow(630, 135, 660, 220, color="#d84315", sw=2))

    render(os.path.join(IMG, 'perf-ring-buffer-layout.svg'), 800, 320, *frags2, title="Структура пам'яті mmap кільцевого буфера perf")

    # ── Figure 3: Stack Unwinding Methods Comparison ─────────────────────────
    frags3 = []

    methods = [
        (40, "Frame Pointers (FP)", "Ланцюжок RBP у стеку", "Плюси: Миттєво, нульові витрати", "Мінуси: Потребує -fno-omit-frame-pointer", "#e8f5e9", "#2e7d32"),
        (290, "DWARF Debug Info", "Сирий стек + таблиці .eh_frame", "Плюси: Працює для будь-якого коду", "Мінуси: Великий perf.data, важкий розбір", "#e3f2fd", "#1565c0"),
        (540, "Hardware LBR / BTS", "Регістри LBR у процесорі", "Плюси: Апаратна швидкість, гілки", "Мінуси: Обмежена глибина (16-32 кадри)", "#fff3e0", "#e65100"),
    ]

    for x, m_title, m_mech, m_pro, m_con, bg_c, str_c in methods:
        frags3.append(rect(x, 60, 220, 230, fill=bg_c, stroke=str_c, sw=1.5, rx=8))
        frags3.append(text(x + 110, 88, m_title, size=13, bold=True, color=str_c))
        frags3.append(text(x + 110, 118, m_mech, size=11, italic=True, color="#333333"))
        
        frags3.append(mtext(x + 110, 160, m_pro, size=11, color="#2e7d32"))
        frags3.append(mtext(x + 110, 220, m_con, size=11, color="#c62828"))

    render(os.path.join(IMG, 'perf-stack-unwinding-methods.svg'), 800, 310, *frags3, title="Методи відновлення стеку викликів (Stack Unwinding)")

if __name__ == "__main__":
    render_figs()
