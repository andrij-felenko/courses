# -*- coding: utf-8 -*-
import sys
import os

# Four levels up from reference/unix-linux/observability/ptrace-model/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_arch_fig():
    w, h = 800, 360
    frags = []
    
    # Tracer Box
    b1 = fitbox(40, 70, 210, 230, "Tracer (Трасувальник)\n[gdb / strace / ltrace]\n\n• Цикл waitpid()\n• Читання/запис регістрів\n• Модифікація пам'яті", size=13, fill="#e8f4f8", stroke="#1b6ec2", bold=True)
    frags.append(b1)
    
    # Kernel Box (Middle)
    b2 = fitbox(295, 70, 210, 230, "Ядро Linux (Kernel)\n[ptrace subsystem]\n\n• task_struct (PT_PTRACED)\n• Сигнальна черга\n• syscall entry/exit trap\n• seccomp filter", size=13, fill="#fdf2e9", stroke="#e67e22", bold=True)
    frags.append(b2)

    # Tracee Box
    b3 = fitbox(550, 70, 210, 230, "Tracee (Трасований)\n[Цільовий процес]\n\n• Виконання коду\n• Зупинка в SIGTRAP\n• Очікування команд\n• Інструкція INT 3", size=13, fill="#eafaf1", stroke="#27ae60", bold=True)
    frags.append(b3)

    # Arrows
    frags.append(arrow(250, 110, 295, 110, color="#1b6ec2", sw=2))
    frags.append(text(272, 100, "ptrace(req)", size=11, color="#1b6ec2", bold=True))
    
    frags.append(arrow(295, 170, 250, 170, color="#c0392b", sw=2))
    frags.append(text(272, 160, "SIGTRAP", size=11, color="#c0392b", bold=True))
    
    frags.append(arrow(505, 110, 550, 110, color="#e67e22", sw=2))
    frags.append(text(527, 100, "Freeze / Resume", size=11, color="#e67e22", bold=True))

    frags.append(arrow(550, 170, 505, 170, color="#27ae60", sw=2))
    frags.append(text(527, 160, "Trap / Exec", size=11, color="#27ae60", bold=True))

    # Bottom note
    tb, _, _ = textbox(400, 330, "Взаємодія Tracer та Tracee відбувається виключно через ядро з зупинкою процесу-цілі", size=12, fill="#f4f6f8", stroke="#6b7280")
    frags.append(tb)

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, "fig-ptrace-arch.svg"), w, h, *frags, title="Архітектура ptrace: Tracer, Ядро та Tracee")

def generate_breakpoint_fig():
    w, h = 820, 360
    frags = []
    
    tb1, _, _ = textbox(200, 50, "1. Оригінальний стан пам'яті", size=14, bold=True, fill="#ffffff", stroke="#ffffff")
    frags.append(tb1)
    frags.append(fitbox(40, 80, 320, 160, "Адреса      Опкоди       Інструкція\n---------------------------------------\n0x401120:   48 89 pt     mov %rdi, %rbp\n0x401124:   e8 32 01     call exit_func\n0x401127:   b8 00 00     mov $0x0, %eax", size=12, fill="#f8f9fa", stroke="#6b7280"))

    tb2, _, _ = textbox(620, 50, "2. Встановлено Breakpoint (0xCC)", size=14, bold=True, fill="#ffffff", stroke="#ffffff")
    frags.append(tb2)
    frags.append(fitbox(460, 80, 320, 160, "Адреса      Опкоди       Інструкція\n---------------------------------------\n0x401120:   CC 89 pt     INT 3 (TRAP!)\n0x401124:   e8 32 01     call exit_func\n0x401127:   b8 00 00     mov $0x0, %eax", size=12, fill="#fff3cd", stroke="#e67e22"))

    frags.append(arrow(365, 160, 455, 160, color="#1b6ec2", sw=2.5))
    frags.append(text(410, 145, "PTRACE_POKEDATA", size=11, color="#1b6ec2", bold=True))
    frags.append(text(410, 180, "Заміна 0x48 на 0xCC", size=10, color="#6b7280"))

    frags.append(fitbox(140, 270, 540, 70, "Покроковий відновлювальний алгоритм GDB:\n1. Отримання SIGTRAP -> 2. Відновлення 0x48 -> 3. RIP = RIP - 1 -> 4. PTRACE_SINGLESTEP -> 5. Повтор 0xCC", size=12, fill="#e8f4f8", stroke="#1b6ec2"))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, "fig-breakpoint.svg"), w, h, *frags, title="Механізм програмної точки зупину (Software Breakpoint)")

def generate_syscall_fig():
    w, h = 820, 380
    frags = []

    tb1, _, _ = textbox(140, 50, "Tracee (Процес)", size=14, bold=True, fill="#eafaf1", stroke="#27ae60")
    tb2, _, _ = textbox(410, 50, "Ядро Linux", size=14, bold=True, fill="#fdf2e9", stroke="#e67e22")
    tb3, _, _ = textbox(680, 50, "Tracer (strace)", size=14, bold=True, fill="#e8f4f8", stroke="#1b6ec2")
    frags.extend([tb1, tb2, tb3])

    frags.append(line(140, 75, 140, 320, color="#27ae60", sw=1.5, dash="4,4"))
    frags.append(line(410, 75, 410, 320, color="#e67e22", sw=1.5, dash="4,4"))
    frags.append(line(680, 75, 680, 320, color="#1b6ec2", sw=1.5, dash="4,4"))

    frags.append(arrow(140, 100, 410, 100, color="#27ae60", sw=2))
    frags.append(text(275, 90, "1. syscall write()", size=11, color="#27ae60", bold=True))

    frags.append(arrow(410, 130, 680, 130, color="#c0392b", sw=2))
    frags.append(text(545, 120, "2. Syscall-enter-stop (SIGTRAP)", size=11, color="#c0392b", bold=True))

    frags.append(arrow(680, 170, 410, 170, color="#1b6ec2", sw=2))
    frags.append(text(545, 160, "3. PEEKREGS + PTRACE_SYSCALL", size=11, color="#1b6ec2", bold=True))

    frags.append(line(410, 170, 410, 210, color="#e67e22", sw=3))
    frags.append(text(420, 195, "Виконання write()", size=11, color="#e67e22", anchor="start"))

    frags.append(arrow(410, 230, 680, 230, color="#c0392b", sw=2))
    frags.append(text(545, 220, "4. Syscall-exit-stop (SIGTRAP)", size=11, color="#c0392b", bold=True))

    frags.append(arrow(680, 270, 410, 270, color="#1b6ec2", sw=2))
    frags.append(text(545, 260, "5. Read RAX + PTRACE_SYSCALL", size=11, color="#1b6ec2", bold=True))

    frags.append(arrow(410, 300, 140, 300, color="#27ae60", sw=2))
    frags.append(text(275, 290, "6. Повернення в юзерспейс", size=11, color="#27ae60", bold=True))

    tb_bot, _, _ = textbox(410, 350, "Сумарні накладні витрати: 4 перемикання контексту на 1 системний виклик", size=12, fill="#f4f6f8", stroke="#6b7280")
    frags.append(tb_bot)

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, "fig-syscall-tracing.svg"), w, h, *frags, title="Перехоплення системних викликів у strace (Double Trap)")

if __name__ == "__main__":
    generate_arch_fig()
    generate_breakpoint_fig()
    generate_syscall_fig()
