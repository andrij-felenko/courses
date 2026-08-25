import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, rect, text, line, arrow, textbox, fitbox, INK, FIELD, POS, NEG, MUTED

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def draw_trampoline_arch():
    frags = []

    # Title / Container left: INT3 Traditional Kprobe
    frags.append(rect(30, 40, 340, 320, fill="#fef2f2", stroke=POS))
    frags.append(text(200, 30, "1. Традиційний Kprobe (INT3 Trap)", bold=True, color=POS, size=15))

    frags.append(fitbox(50, 60, 300, 40, "Вхід у функцію ядра\n[заміна 1-го байта на INT3 0xCC]", fill="#ffffff", stroke=POS))
    frags.append(arrow(200, 100, 200, 120, color=POS))

    frags.append(fitbox(50, 120, 300, 50, "Програмне переривання (#BP Trap)\nСкидання конвеєра CPU, перемикання NMI", fill="#fee2e2", stroke=POS, bold=True))
    frags.append(arrow(200, 170, 200, 190, color=POS))

    frags.append(fitbox(50, 190, 300, 50, "Обробник traps: збереження pt_regs\n(21+ регістр: RAX, RBX, RDI, RSI...)", fill="#ffffff", stroke="#9ca3af"))
    frags.append(arrow(200, 240, 200, 260, color=POS))

    frags.append(fitbox(50, 260, 300, 40, "Виклик BPF-програми + Single-step OOL\nВідновлення всіх регістрів -> RET", fill="#ffffff", stroke="#9ca3af"))

    frags.append(text(200, 345, "Оверхед: ~300-1000 тактів / нс", bold=True, color=POS, size=13))

    # Right Container: BPF Trampoline (fentry/fexit)
    frags.append(rect(410, 40, 340, 320, fill="#f0fdf4", stroke=FIELD))
    frags.append(text(580, 30, "2. BPF Trampoline (fentry / fexit)", bold=True, color=FIELD, size=15))

    frags.append(fitbox(430, 60, 300, 40, "Вхід у функцію ядра\n[ftrace CALL __fentry__]", fill="#ffffff", stroke=FIELD))
    frags.append(arrow(580, 100, 580, 120, color=FIELD))

    frags.append(fitbox(430, 120, 300, 50, "Динамічний JIT Trampoline Stub\nЗбереження лише аргументів (до 6 рег)", fill="#dcfce7", stroke=FIELD, bold=True))
    frags.append(arrow(580, 170, 580, 190, color=FIELD))

    frags.append(fitbox(430, 190, 300, 50, "Прямий виклик JIT BPF-програми\nO(1) без pt_regs, без traps, type-safe", fill="#ffffff", stroke=FIELD))
    frags.append(arrow(580, 240, 580, 260, color=FIELD))

    frags.append(fitbox(430, 260, 300, 40, "Прямий виклик оригіналу -> fexit -> RET\nМінімальний пролог/епілог", fill="#ffffff", stroke=FIELD))

    frags.append(text(580, 345, "Оверхед: ~5-15 тактів / нс (Zero-trap)", bold=True, color=FIELD, size=13))

    render(os.path.join(IMG, 'bpf-trampoline-architecture.svg'), 780, 380, *frags, title="Порівняння архітектури Kprobe INT3 та BPF Trampoline fentry")

def draw_fprobe_multi():
    frags = []

    # Container
    frags.append(rect(30, 40, 720, 310, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(text(390, 28, "Архітектура fprobe та kprobe.multi (Масове трасування)", bold=True, color=INK, size=15))

    # Kernel Functions Box
    frags.append(fitbox(50, 60, 210, 80, "Тисячі функцій ядра\nvfs_read(), vfs_write(),\nsys_clone(), ip_rcv()...", fill="#eff6ff", stroke=NEG))

    # Ftrace Subsystem Box
    frags.append(fitbox(300, 60, 180, 80, "Підсистема ftrace\nftrace_ops\n[Live patching NOP->CALL]", fill="#ffffff", stroke="#64748b"))

    # fprobe Layer Box
    frags.append(fitbox(520, 60, 210, 80, "Фреймворк fprobe\n+ rethook (для exit probes)\n[Єдиний колбек для всіх цілей]", fill="#fef3c7", stroke="#d97706", bold=True))

    # Connectors Top
    frags.append(arrow(260, 100, 300, 100, color=NEG))
    frags.append(arrow(480, 100, 520, 100, color=FIELD))

    # Down to bpf_kprobe_multi
    frags.append(arrow(625, 140, 625, 180, color=FIELD))

    # BPF Program Box
    frags.append(fitbox(420, 180, 310, 70, "BPF_TRACE_KPROBE_MULTI\nОдна BPF-програма на 10 000+ функцій\nОтримує IP / Cookie без тисяч trampolines", fill="#dcfce7", stroke=FIELD, bold=True))

    # User Space Controller
    frags.append(fitbox(50, 180, 300, 70, "Користувацький простір (bpftrace / libbpf)\nСтворення link bpf_program__attach_kprobe_multi()\nПередача масиву символів або паттерна", fill="#ffffff", stroke="#94a3b8"))

    frags.append(arrow(350, 215, 420, 215, color=INK))

    render(os.path.join(IMG, 'fprobe-multi-kprobe.svg'), 780, 370, *frags, title="Схема роботи fprobe та bpf_kprobe_multi у ядрі Linux")

if __name__ == '__main__':
    draw_trampoline_arch()
    draw_fprobe_multi()
