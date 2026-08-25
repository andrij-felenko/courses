# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми what-is-the-process-waiting-for."""

import os
import sys

# Шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_process_state_machine():
    """Карта станів процесу в ядрі Linux: TASK_RUNNING, TASK_INTERRUPTIBLE, TASK_UNINTERRUPTIBLE, TASK_KILLABLE, TASK_STOPPED/TRACED."""
    w, h = 880, 560
    frags = []

    # Заголовок / фонова зона
    frags.append(rect(15, 15, 850, 530, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 42, "КАРТА СТАНІВ ПРОЦЕСУ В ЯДРІ LINUX (task_struct.__state)", size=13, color=INK, anchor="middle", bold=True))

    # 1. TASK_RUNNING (R) - Центр угорі
    frags.append(fitbox(300, 65, 280, 85, "TASK_RUNNING (R)\n• Виконується на CPU або стоїть у runqueue\n• Активно обробляє інструкції користувача\n• Перемикання контексту: schedule()", size=10, fill="#f0fdf4", stroke="#86efac", bold=True))

    # 2. TASK_INTERRUPTIBLE (S) - Ліворуч посередині
    frags.append(fitbox(35, 195, 250, 95, "TASK_INTERRUPTIBLE (S)\n• Перервний сон на черзі wait_queue_head_t\n• Очікування сокета, пайпа, futex, таймера\n• Пробудження: подія АБО будь-який сигнал\n• Реакція на SIGINT / SIGTERM / SIGKILL", size=10, fill="#f8fafc", stroke="#94a3b8", bold=True))

    # 3. TASK_UNINTERRUPTIBLE (D) - Праворуч посередині
    frags.append(fitbox(595, 195, 255, 95, "TASK_UNINTERRUPTIBLE (D)\n• Неперервний сон під час операцій ядра\n• Очікування дискового I/O, блокування NFS\n• Сигнали ігноруються планувальником!\n• kill -9 безсилий до завершення I/O", size=10, fill="#fef2f2", stroke="#fca5a5", bold=True))

    # 4. TASK_KILLABLE - Праворуч унизу
    frags.append(fitbox(595, 335, 255, 85, "TASK_KILLABLE\n• Гібридний стан сну (D + WAKEKILL)\n• Спить на очікуванні критичного ресурсу\n• Пробуджується ЛИШЕ на фатальні сигнали\n• Дозволяє kill -9 для завислих NFS/I/O", size=10, fill="#fffbeb", stroke="#fcd34d", bold=True))

    # 5. TASK_STOPPED / TASK_TRACED (T / t) - Ліворуч унизу
    frags.append(fitbox(35, 335, 250, 85, "TASK_STOPPED / TRACED (T / t)\n• Зупинено сигналом SIGSTOP / SIGTSTP\n• АБО заморожено під ptrace (GDB, strace)\n• tracer інспектує регістри та пам'ять\n• Продовження: SIGCONT чи ptrace-detach", size=10, fill="#fdf4ff", stroke="#e879f9", bold=True))

    # 6. EXIT_ZOMBIE / EXIT_DEAD (Z / X) - Центр унизу
    frags.append(fitbox(315, 455, 250, 75, "EXIT_ZOMBIE / DEAD (Z / X)\n• Виконання завершено (exit_group)\n• Ресурси звільнено, дескриптор task_struct збережено\n• Очікує виклику waitpid() від батьківського процесу", size=10, fill="#f1f5f9", stroke="#64748b", bold=True))

    # Стрілки переходів
    # RUNNING -> S
    frags.append(arrow(360, 150, 200, 195, color=LINE, sw=1.8))
    frags.append(text(250, 165, "wait_event() / read()", size=9, color=MUTED, anchor="middle", bold=True))

    # S -> RUNNING
    frags.append(arrow(220, 195, 390, 150, color=FIELD, sw=1.8))
    frags.append(text(345, 185, "wake_up() / сигнал", size=9, color=FIELD, anchor="middle", bold=True))

    # RUNNING -> D
    frags.append(arrow(520, 150, 680, 195, color=POS, sw=1.8))
    frags.append(text(630, 165, "io_schedule() / NFS RPC", size=9, color=POS, anchor="middle", bold=True))

    # D -> RUNNING
    frags.append(arrow(660, 195, 490, 150, color=FIELD, sw=1.8))
    frags.append(text(540, 185, "DMA I/O завершено", size=9, color=FIELD, anchor="middle", bold=True))

    # RUNNING -> T/t
    frags.append(arrow(320, 150, 160, 335, color=MUTED, sw=1.5))
    frags.append(text(190, 310, "SIGSTOP / ptrace", size=9, color=MUTED, anchor="middle", bold=True))

    # T/t -> RUNNING
    frags.append(arrow(180, 335, 340, 150, color=FIELD, sw=1.5))
    frags.append(text(275, 330, "SIGCONT / continue", size=9, color=FIELD, anchor="middle", bold=True))

    # D -> TASK_KILLABLE
    frags.append(arrow(722, 290, 722, 335, color=MUTED, sw=1.5))

    # RUNNING -> ZOMBIE
    frags.append(arrow(440, 150, 440, 455, color=LINE, sw=1.8))
    frags.append(text(440, 290, "exit(0) / SIGKILL", size=9, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT_DIR, "process-state-machine.svg"), w, h, *frags)


def fig_wait_channel_procfs_stack():
    """Архітектура інспекції стану очікування через procfs: wchan, stack, syscall та fdinfo."""
    w, h = 880, 520
    frags = []

    # Три інформаційні блоки: /proc/[pid]/wchan, /proc/[pid]/stack, /proc/[pid]/syscall
    # Колонка 1: /proc/[pid]/wchan
    frags.append(rect(20, 20, 260, 480, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(150, 46, "/proc/[PID]/wchan", size=12, color=INK, anchor="middle", bold=True))

    frags.append(fitbox(35, 65, 230, 80, "Символічна назва очікування:\n• Функція ядра, де спить процес\n• Обчислюється get_wchan(task)\n• Розмотування до межі schedule()", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(35, 155, 230, 140, "Типові значення wchan:\n• futex_wait_queue_me\n  -> блокування на м'ютексі\n• sk_wait_data / inet_csk_accept\n  -> сокет чекає на байти\n• epoll_wait / do_sys_poll\n  -> цикл очікування подій\n• pipe_read / nfs_wait_bit_killable\n  -> ввід-вивід пайпа або NFS", size=9, fill="#f0fdf4", stroke="#86efac", bold=True))

    frags.append(fitbox(35, 305, 230, 85, "Обмеження wchan:\n• kptr_restrict = 2 може ховати\n  символи ядра і повертати '0'\n• Показує лише один кадр ядра,\n  без контексту викликів", size=9, fill="#fffbeb", stroke="#fcd34d", bold=True))

    frags.append(fitbox(35, 400, 230, 85, "Швидкий огляд:\ncat /proc/14920/wchan\nps -o pid,stat,wchan:20,comm\n-> Нульовий оверхед читання", size=9, fill="#ffffff", stroke="#94a3b8", bold=True))

    # Колонка 2: /proc/[pid]/stack
    frags.append(rect(310, 20, 260, 480, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(440, 46, "/proc/[PID]/stack", size=12, color=FIELD, anchor="middle", bold=True))

    frags.append(fitbox(325, 65, 230, 60, "Ядерний бектрейс (Kernel Call Stack):\n• Повний ланцюг викликів у ядрі\n• Від входу syscall до розкладу", size=10, fill="#ffffff", stroke="#86efac", bold=True))

    frags.append(fitbox(325, 135, 230, 220, "Приклад ядерного стека (#0..#7):\n[<0>] __schedule+0x3ee/0x890\n[<0>] schedule+0x4e/0xb0\n[<0>] futex_wait_queue_me+0xc2/0x120\n[<0>] futex_wait+0x139/0x240\n[<0>] do_futex+0x12c/0x190\n[<0>] __x64_sys_futex+0x125/0x180\n[<0>] do_syscall_64+0x5c/0x90\n[<0>] entry_SYSCALL_64_after_hwframe", size=9, fill="#f8fafc", stroke="#86efac", bold=True))

    frags.append(fitbox(325, 365, 230, 120, "Діагностична цінність:\n• Точна точка зупинки в ядрі\n• Видно, чи це драйвер диска,\n  мережевий стек або lock ядра\n• Потребує CAP_SYS_PTRACE / root", size=9, fill="#ffffff", stroke="#86efac", bold=True))

    # Колонка 3: /proc/[pid]/syscall + fd
    frags.append(rect(600, 20, 260, 480, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(730, 46, "/proc/[PID]/syscall & fd/", size=12, color=INK, anchor="middle", bold=True))

    frags.append(fitbox(615, 65, 230, 100, "Формат /proc/[pid]/syscall:\nNR arg0 arg1 arg2 arg3 arg4 arg5 sp pc\nПриклад блокування:\n202 0x7f0a40 0x80 0x2 0x0 0x0 0x0 ...\n-> NR 202 = SYS_futex (x86_64)", size=9, fill="#f8fafc", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(615, 175, 230, 140, "Зв'язок із дескриптором (fd):\nЯкщо NR = 0 (read) чи 45 (recvfrom):\n• arg0 = номер дескриптора (fd=3)\n• ls -l /proc/[pid]/fd/3\n  -> socket:[491029]\n• ss -tulpne | grep 491029\n  -> 10.0.1.5:8080 <-> 10.0.2.9:443", size=9, fill="#f0fdf4", stroke="#86efac", bold=True))

    frags.append(fitbox(615, 325, 230, 160, "Деталі у fdinfo/[fd]:\n• pos: поточне зміщення у файлі\n• flags: 02 (O_RDWR, блокуючий)\n• mnt_id: ідентифікатор точки монтування\n• eventfd-count / epoll-tfd:\n  внутрішні лічильники примітивів", size=9, fill="#f8fafc", stroke="#cbd5e1", bold=True))

    render(os.path.join(OUT_DIR, "wait-channel-procfs-stack.svg"), w, h, *frags)


def fig_futex_deadlock_detection():
    """Механіка взаємного блокування м'ютексів (ABBA Deadlock), черги futex та виявлення через GDB."""
    w, h = 880, 520
    frags = []

    # Зона 1: Потік 1 (TID 101)
    frags.append(rect(20, 20, 260, 480, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(150, 46, "ПОТІК 1 (TID 101)", size=12, color=POS, anchor="middle", bold=True))

    frags.append(fitbox(35, 65, 230, 85, "Крок 1: Захопив М'ютекс A\npthread_mutex_lock(&mutex_A)\n-> Успіх! mutex_A.__owner = 101\n-> Працює в просторі користувача", size=9, fill="#ffffff", stroke="#fca5a5", bold=True))

    frags.append(arrow(150, 150, 150, 180, color=POS, sw=1.8))

    frags.append(fitbox(35, 180, 230, 115, "Крок 2: Запитує М'ютекс B\npthread_mutex_lock(&mutex_B)\n-> mutex_B.__owner == 102 (зайнято!)\n-> Виклик syscall(SYS_futex, &mutex_B,\n   FUTEX_WAIT_BITSET, 2)\n-> Потік переходить у стан S (Sleep)", size=9, fill="#ffffff", stroke="#fca5a5", bold=True))

    frags.append(fitbox(35, 310, 230, 95, "Стан у системі:\n• wchan: futex_wait_queue_me\n• stack: futex_wait -> schedule\n• Очікує пробудження від TID 102", size=9, fill="#f8fafc", stroke="#fca5a5", bold=True))

    frags.append(fitbox(35, 415, 230, 70, "Висновки GDB:\nThread 1 тримає 0x7fff8010 (A)\nі заблокований на 0x7fff8030 (B)", size=9, fill="#fef2f2", stroke="#c0392b", bold=True))

    # Зона 2: Ядро Linux / Футекс-хеш-таблиця
    frags.append(rect(310, 20, 260, 480, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 46, "ЯДРО: FUTEX HASH BUCKET", size=12, color=INK, anchor="middle", bold=True))

    frags.append(fitbox(325, 65, 230, 95, "Хеш-кошик ядра (&mutex_A):\n• Ключ: {mm, uaddr=0x7fff8010}\n• Власник: TID 101\n• Черга очікування: [TID 102 спить]\n-> futex_q чекає wake_up від 101", size=9, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(325, 175, 230, 95, "Хеш-кошик ядра (&mutex_B):\n• Ключ: {mm, uaddr=0x7fff8030}\n• Власник: TID 102\n• Черга очікування: [TID 101 спить]\n-> futex_q чекає wake_up від 102", size=9, fill="#ffffff", stroke="#cbd5e1", bold=True))

    # Deadlock cycle illustration
    frags.append(rect(325, 285, 230, 115, fill="#fef2f2", stroke="#c0392b", sw=2, rx=6))
    frags.append(text(440, 310, "ЦИКЛ DEADLOCK (ABBA)", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(440, 335, "TID 101  --->  Чекає Mutex B", size=10, color=INK, anchor="middle"))
    frags.append(text(440, 355, "^                      |", size=10, color=POS, anchor="middle", bold=True))
    frags.append(text(440, 375, "Тримає Mutex A  <---  TID 102", size=10, color=INK, anchor="middle"))

    frags.append(fitbox(325, 415, 230, 70, "Результат: Навантаження CPU = 0%\nОбидва потоки сплять назавжди,\nжоден не викличе FUTEX_WAKE", size=9, fill="#ffffff", stroke="#94a3b8", bold=True))

    # Зона 3: Потік 2 (TID 102)
    frags.append(rect(600, 20, 260, 480, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(730, 46, "ПОТІК 2 (TID 102)", size=12, color=POS, anchor="middle", bold=True))

    frags.append(fitbox(615, 65, 230, 85, "Крок 1: Захопив М'ютекс B\npthread_mutex_lock(&mutex_B)\n-> Успіх! mutex_B.__owner = 102\n-> Працює в просторі користувача", size=9, fill="#ffffff", stroke="#fca5a5", bold=True))

    frags.append(arrow(730, 150, 730, 180, color=POS, sw=1.8))

    frags.append(fitbox(615, 180, 230, 115, "Крок 2: Запитує М'ютекс A\npthread_mutex_lock(&mutex_A)\n-> mutex_A.__owner == 101 (зайнято!)\n-> Виклик syscall(SYS_futex, &mutex_A,\n   FUTEX_WAIT_BITSET, 2)\n-> Потік переходить у стан S (Sleep)", size=9, fill="#ffffff", stroke="#fca5a5", bold=True))

    frags.append(fitbox(615, 310, 230, 95, "Стан у системі:\n• wchan: futex_wait_queue_me\n• stack: futex_wait -> schedule\n• Очікує пробудження від TID 101", size=9, fill="#f8fafc", stroke="#fca5a5", bold=True))

    frags.append(fitbox(615, 415, 230, 70, "Висновки GDB:\nThread 2 тримає 0x7fff8030 (B)\nі заблокований на 0x7fff8010 (A)", size=9, fill="#fef2f2", stroke="#c0392b", bold=True))

    # Міжзональні стрілки
    frags.append(arrow(265, 240, 325, 220, color=POS, sw=1.8))
    frags.append(arrow(615, 240, 555, 110, color=POS, sw=1.8))

    render(os.path.join(OUT_DIR, "futex-deadlock-detection.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_process_state_machine()
    fig_wait_channel_procfs_stack()
    fig_futex_deadlock_detection()
    print("All figures generated successfully.")
