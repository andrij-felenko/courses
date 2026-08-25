# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми live-debug-session."""

import os
import sys

# Шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_ptrace_attach_sequence():
    """Схема системного виклику ptrace(PTRACE_ATTACH): безпека Yama LSM, зупинка SIGSTOP та перехід у TASK_TRACED."""
    w, h = 880, 560
    frags = []

    # Три вертикальні домени: GDB, Ядро Linux, Цільовий процес
    frags.append(rect(20, 20, 260, 520, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(150, 48, "GDB (Tracer / Ring 3)", size=13, color=MUTED, anchor="middle", bold=True))

    frags.append(rect(300, 20, 280, 520, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(440, 48, "ЯДРО LINUX (Ring 0)", size=13, color=FIELD, anchor="middle", bold=True))

    frags.append(rect(600, 20, 260, 520, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(730, 48, "ЦІЛЬОВИЙ ПРОЦЕС (Tracee / Ring 3)", size=13, color=POS, anchor="middle", bold=True))

    # Крок 1: Запуск gdb -p
    frags.append(fitbox(35, 75, 230, 60, "1. Команда оператора:\ngdb -p 18492\nВиклик ptrace(PTRACE_ATTACH)", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(265, 105, 315, 105, color=LINE, sw=2))

    # Крок 2: Перевірка Yama LSM
    frags.append(fitbox(315, 75, 250, 65, "2. Перевірка Yama LSM:\n/proc/sys/kernel/yama/ptrace_scope\nПеревірка UID та CAP_SYS_PTRACE", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(440, 140, 440, 165, color=LINE, sw=2))

    # Крок 3: Доставка SIGSTOP і перехід у TASK_TRACED
    frags.append(fitbox(315, 165, 250, 65, "3. Надсилання сигналу SIGSTOP\ntask_struct->__state = TASK_TRACED\nЗупинка на межі переривання", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(565, 195, 615, 195, color=POS, sw=2))

    # Крок 4: Стан цільового процесу
    frags.append(fitbox(615, 165, 230, 65, "4. Процес заморожено\nВиконання інструкцій зупинено\nРегістри збережено в pt_regs", size=11, fill="#ffffff", stroke="#fca5a5", bold=True))
    frags.append(arrow(730, 230, 730, 260, color=LINE, sw=2))

    # Крок 5: Сповіщення ядра
    frags.append(fitbox(615, 260, 230, 60, "5. Ядро сповіщає трейсера\nПотік переходить у стан 't'\nГотовність до інспекції", size=11, fill="#ffffff", stroke="#fca5a5", bold=True))
    frags.append(arrow(615, 290, 565, 290, color=LINE, sw=2))

    # Крок 6: waitpid у GDB
    frags.append(fitbox(315, 260, 250, 60, "6. Розблокування очікування\nwaitpid(pid, &status, WUNTRACED)\nОтримано статус WIFSTOPPED", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(315, 290, 265, 290, color=FIELD, sw=2))

    # Крок 7: Читання стану у GDB
    frags.append(fitbox(35, 260, 230, 60, "7. GDB отримує контроль\nІнспекція /proc/18492/task/\nАттач до всіх підпотоків TID", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(150, 320, 150, 350, color=LINE, sw=2))

    # Крок 8: Інтерактивна сесія
    frags.append(fitbox(35, 350, 230, 75, "8. Інтерактивна діагностика\nthread apply all bt full\nframe N, info locals, watch\nset variable = new_val", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(150, 425, 150, 455, color=LINE, sw=2))

    # Крок 9: Безпечний detach
    frags.append(fitbox(35, 455, 230, 65, "9. Безпечне завершення:\nКоманда 'detach'\nВідновлення коду та регістрів", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(265, 485, 315, 485, color=FIELD, sw=2))

    # Крок 10: Ядро відновлює процес
    frags.append(fitbox(315, 455, 250, 65, "10. ptrace(PTRACE_DETACH)\nОчищення прапорців трасування\ntask_struct->__state = TASK_RUNNING", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(565, 485, 615, 485, color=FIELD, sw=2))

    # Крок 11: Процес продовжує роботу
    frags.append(fitbox(615, 455, 230, 65, "11. Процес живий\nПродовження обробки запитів\nНульовий оверхед після виходу", size=11, fill="#ffffff", stroke="#86efac", bold=True))

    render(os.path.join(OUT_DIR, "ptrace-attach-sequence.svg"), w, h, *frags)


def fig_hardware_watchpoint_dr_registers():
    """Апаратні регістри зневадження x86-64 DR0-DR7 та апаратна пастка #DB без модифікації пам'яті."""
    w, h = 880, 520
    frags = []

    # Ліва частина: Регістри DR0-DR3, DR6, DR7
    frags.append(rect(20, 20, 430, 480, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(235, 46, "АПАРАТНІ РЕГІСТРИ ЗНЕВАДЖЕННЯ (x86-64 DR0–DR7)", size=12, color=INK, anchor="middle", bold=True))

    # Регістри адрес DR0..DR3
    frags.append(fitbox(35, 65, 400, 36, "DR0: 0x7fff48901000  (Лінійна 64-бітна адреса змінної A)", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))
    frags.append(fitbox(35, 107, 400, 36, "DR1: 0x7fff48901008  (Лінійна 64-бітна адреса змінної B)", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))
    frags.append(fitbox(35, 149, 400, 36, "DR2: 0x000000000000  (Не використовується / вільний)", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))
    frags.append(fitbox(35, 191, 400, 36, "DR3: 0x000000000000  (Не використовується / вільний)", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))

    # DR6 - Регістр стану
    frags.append(fitbox(35, 238, 400, 68, "DR6 — Debug Status Register (Стан спрацювання)\nБіти B0..B3: вказують, яка з адрес DR0-DR3 викликала пастку\nБіт BS: прапорець покрокового виконання (single-step)", size=10, fill="#fef2f2", stroke="#fca5a5", bold=True))

    # DR7 - Регістр керування
    frags.append(fitbox(35, 316, 400, 168, "DR7 — Debug Control Register (Керування умовами)\n• L0..L3 / G0..G3: локальний / глобальний дозвіл точок 0..3\n• R/W0..R/W3: тип умови доступу до пам'яті:\n    00 = виконання інструкції, 01 = запис даних,\n    11 = читання або запис (rwatch / awatch)\n• LEN0..LEN3: розмір комірки спостереження:\n    00 = 1 байт, 01 = 2 байти, 10 = 8 байтів, 11 = 4 байти", size=10, fill="#f0fdf4", stroke="#86efac", bold=True))

    # Права частина: Порівняння механізмів (Апаратний проти Програмного)
    frags.append(rect(470, 20, 390, 480, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(665, 46, "МЕХАНІЗМ СПОСТЕРЕЖЕННЯ ЗА ПАМ'ЯТТЮ", size=12, color=INK, anchor="middle", bold=True))

    # Блок Апаратного Watchpoint
    frags.append(fitbox(485, 65, 360, 190, "Апаратний Watchpoint (Hardware Watchpoint)\n1. GDB записує адресу в DR0 і маску в DR7\n2. Програма виконується на повній швидкості CPU\n3. При спробі запису шина CPU фіксує збіг адреси\n4. Процесор генерує вектор 1 (#DB Debug Exception)\n5. Пам'ять залишається чистою (без опкодів 0xCC)\n6. Максимум 4 активні адреси на ядро CPU", size=10, fill="#f0fdf4", stroke="#86efac", bold=True))

    # Розділювач
    frags.append(line(500, 275, 830, 275, color=MUTED, sw=1, dash="4,4"))

    # Блок Програмного Watchpoint
    frags.append(fitbox(485, 290, 360, 194, "Програмний Watchpoint (Software Watchpoint)\n1. Використовується, якщо змінних > 4 або розмір великий\n2. GDB вмикає покроковий режим (PTRACE_SINGLESTEP)\n3. CPU зупиняється ПІСЛЯ КОЖНОЇ асемблерної інструкції\n4. GDB перемикає контекст і читає пам'ять через ptrace\n5. Швидкість програми падає у 10 000+ разів\n6. Заборонено використовувати на живому продакшені", size=10, fill="#fef2f2", stroke="#fca5a5", bold=True))

    render(os.path.join(OUT_DIR, "hardware-watchpoint-dr-registers.svg"), w, h, *frags)


def fig_live_inspection_thread_frames():
    """Схема діагностики завислого багатопотокового процесу: потоки, стек викликів та інспекція локальних змінних."""
    w, h = 880, 520
    frags = []

    # Ліва колонка: Список потоків процесу (info threads)
    frags.append(rect(20, 20, 270, 480, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(155, 46, "ПОТОКИ ПРОЦЕСУ (info threads)", size=12, color=INK, anchor="middle", bold=True))

    frags.append(fitbox(35, 65, 240, 75, "Thread 1 (LWP 18492)\nГоловний цикл подій\n__epoll_wait (epoll_wait.c:30)\nСтан: Очікує нових підключень", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(35, 150, 240, 85, "Thread 2 (LWP 18493) [ПОТОЧНИЙ]\nОбробник замовлень #1\n__futex_abstimed_wait_common64\nОчікує м'ютекс: 0x7fff8040\nТримає м'ютекс: 0x7fff8020", size=10, fill="#fef2f2", stroke="#fca5a5", bold=True))

    frags.append(fitbox(35, 245, 240, 85, "Thread 3 (LWP 18494)\nОбробник замовлень #2\n__futex_abstimed_wait_common64\nОчікує м'ютекс: 0x7fff8020\nТримає м'ютекс: 0x7fff8040", size=10, fill="#fef2f2", stroke="#fca5a5", bold=True))

    frags.append(fitbox(35, 340, 240, 65, "Thread 4 (LWP 18495)\nФоновий таймер метрик\nclock_nanosleep (nanosleep.c)\nСтан: Спить до наступного інтервалу", size=10, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(35, 415, 240, 70, "Діагноз: Взаємне блокування!\nDeadlock між потоками 2 та 3:\nперехресне захоплення м'ютексів\n0x7fff8040 <-> 0x7fff8020", size=10, fill="#fef2f2", stroke="#c0392b", bold=True))

    # Середня колонка: Стек вибраного потоку 2 (backtrace / frame N)
    frags.append(rect(310, 20, 260, 480, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(440, 46, "СТЕК ПОТОКУ 2 (backtrace)", size=12, color=FIELD, anchor="middle", bold=True))

    frags.append(fitbox(325, 65, 230, 50, "#0 __futex_abstimed_wait_common\nфутекс у glibc (syscall 202)", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(440, 115, 440, 135, color=LINE, sw=1.5))

    frags.append(fitbox(325, 135, 230, 50, "#1 pthread_mutex_lock\nзахоплення std::mutex", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(440, 185, 440, 205, color=LINE, sw=1.5))

    frags.append(fitbox(325, 205, 230, 60, "#2 OrderProcessor::process_order\norder_processor.cpp:114\n[Вибрано: frame 2]", size=10, fill="#fef2f2", stroke="#c0392b", bold=True))
    frags.append(arrow(440, 265, 440, 285, color=LINE, sw=1.5))

    frags.append(fitbox(325, 285, 230, 55, "#3 WorkerPool::dispatch_task\nworker_pool.cpp:52", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(440, 340, 440, 360, color=LINE, sw=1.5))

    frags.append(fitbox(325, 360, 230, 55, "#4 WorkerPool::worker_entry\nstd::thread entrypoint", size=10, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(440, 415, 440, 435, color=LINE, sw=1.5))

    frags.append(fitbox(325, 435, 230, 50, "#5 clone (clone.S:100)\nсистемний виклик ядра", size=10, fill="#ffffff", stroke="#86efac", bold=True))

    # Права колонка: Інспекція даних у frame #2 (info locals, print)
    frags.append(rect(590, 20, 270, 480, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(725, 46, "ІНСПЕКЦІЯ ДАНИХ (frame 2)", size=12, color=INK, anchor="middle", bold=True))

    frags.append(fitbox(605, 65, 240, 100, "(gdb) info args\nthis = 0x55aa41908000\norder_id = 918429\naccount_from = 1044\naccount_to = 8821", size=10, fill="#f8fafc", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(605, 175, 240, 115, "(gdb) info locals\norder_ptr = 0x7fff8000a120\nlock_a = {m_mutex = 0x7fff8020}\nlock_b = {m_mutex = 0x7fff8040}\nretries_left = 3\nis_retryable = true", size=10, fill="#f8fafc", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(605, 300, 240, 105, "(gdb) p *order_ptr\n$1 = {\n  id = 918429,\n  amount = 45000.0,\n  status = ORDER_PROCESSING,\n  created_at = 1718049100\n}", size=10, fill="#f8fafc", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(605, 415, 240, 70, "(gdb) set var is_retryable = false\n(gdb) set var retries_left = 0\nЗміна значення локальної змінної\nбезпосередньо на стеку фрейму", size=10, fill="#f0fdf4", stroke="#86efac", bold=True))

    render(os.path.join(OUT_DIR, "live-inspection-thread-frames.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_ptrace_attach_sequence()
    fig_hardware_watchpoint_dr_registers()
    fig_live_inspection_thread_frames()
    print("Figures generated successfully.")
