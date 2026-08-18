# -*- coding: utf-8 -*-
"""Фігури для теми «Як обрати спосіб взаємодії під задачу» (guide/unix/syhnaly/choosing-ipc)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_decision_tree():
    """decision-tree.svg: Дерево прийняття рішень для вибору примітиву взаємодії між процесами."""
    W, H = 1020, 640
    frags = []

    # Заголовок
    frags.append(text(510, 28, "Дерево інженерного вибору IPC: від архітектурних вимог до системного примітиву", size=15, bold=True, color="#1e293b"))

    # Початковий вузол (Корінь)
    b_root, _, _ = textbox(510, 70, "Головна вимога: обсяг даних, характер передачі та межі безпеки", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_root)

    # 3 основні гілки від кореня
    frags.append(arrow(340, 90, 180, 135, color=LINE, sw=1.5))
    frags.append(arrow(510, 90, 510, 135, color=LINE, sw=1.5))
    frags.append(arrow(680, 90, 840, 135, color=LINE, sw=1.5))

    frags.append(text(240, 110, "Масивні дані / нуль копій", size=10, bold=True, color="#2563eb"))
    frags.append(text(510, 110, "Керування / FDs / безпека", size=10, bold=True, color="#7e22ce"))
    frags.append(text(780, 110, "Потоки байтів / черги", size=10, bold=True, color="#16a34a"))

    # ── Ліва колонка: Спільна пам'ять (Швидкість) ──
    frags.append(rect(30, 140, 300, 475, fill="#f8fafc", stroke=BLUE_S, sw=1.2, rx=8))
    frags.append(text(180, 165, "1. Швидкість та Обсяг даних", size=12, bold=True, color=BLUE_S))

    b_q1, _, _ = textbox(180, 210, "Потрібна ізоляція у пісочниці\nчи відкрите системне ім'я?", size=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_q1)

    frags.append(arrow(180, 240, 180, 270, color=LINE, sw=1.2))

    b_memfd, _, _ = textbox(180, 310, "memfd_create() + mmap + seals\n• Анонімний дескриптор у RAM\n• fcntl(F_ADD_SEALS, F_SEAL_WRITE)\n• Ідеально для передачі у sandbox", size=9.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_memfd)

    b_posix_shm, _, _ = textbox(180, 400, "POSIX shm (shm_open + mmap)\n• Файл у віртуальній пам'яті /dev/shm\n• Доступ за правами користувача/групи", size=9.5, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_posix_shm)

    frags.append(arrow(180, 435, 180, 465, color=LINE, sw=1.2))

    b_sync, _, _ = textbox(180, 520, "Обов'язкова сигналізація:\n• eventfd (готовність для epoll)\n• Robust Futex / Pthread Mutex\n• Lockless Ring Buffer (SPSC)", size=9.5, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_sync)

    b_shm_res, _, _ = textbox(180, 585, "Вибір: Спільна пам'ять + eventfd", size=10, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_shm_res)

    # ── Середня колонка: Unix Domain Sockets ──
    frags.append(rect(360, 140, 300, 475, fill="#f8fafc", stroke=PURPLE_S, sw=1.2, rx=8))
    frags.append(text(510, 165, "2. Керування, FDs та Безпека", size=12, bold=True, color=PURPLE_S))

    b_q2, _, _ = textbox(510, 210, "Топологія зв'язку:\nбатько-дитина чи клієнт-сервер?", size=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_q2)

    frags.append(arrow(510, 240, 510, 270, color=LINE, sw=1.2))

    b_uds, _, _ = textbox(510, 310, "Unix Domain Socket (SEQPACKET)\n• Межі повідомлень без розриву потоку\n• SO_PEERCRED: перевірка UID/GID ядра\n• SCM_RIGHTS: передача дескрипторів", size=9.5, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_uds)

    b_sockp, _, _ = textbox(510, 400, "socketpair(AF_UNIX, STREAM)\n• Без створення файлу на диску\n• Двоспрямований надійний зв'язок", size=9.5, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_sockp)

    frags.append(arrow(510, 435, 510, 465, color=LINE, sw=1.2))

    b_cap, _, _ = textbox(510, 520, "Системні переваги:\n• Автоматичний EOF / POLLHUP при краху\n• Рідне мультиплексування в epoll\n• Безпечне розділення привілеїв", size=9.5, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_cap)

    b_uds_res, _, _ = textbox(510, 585, "Вибір: UDS (головний IPC у Linux)", size=10, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_uds_res)

    # ── Права колонка: Pipes та Message Queues ──
    frags.append(rect(690, 140, 300, 475, fill="#f8fafc", stroke=GREEN_S, sw=1.2, rx=8))
    frags.append(text(840, 165, "3. Потоки або Пріоритети", size=12, bold=True, color=GREEN_S))

    b_q3, _, _ = textbox(840, 210, "Односпрямований потік байтів\nчи дискретні пріоритетні черги?", size=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_q3)

    frags.append(arrow(840, 240, 840, 270, color=LINE, sw=1.2))

    b_pipe, _, _ = textbox(840, 310, "Pipes / FIFO (pipe2, mkfifo)\n• Простий односпрямований потік\n• Атомарність запису до 4 КБ\n• SIGPIPE та EOF при закритті", size=9.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_pipe)

    b_mq, _, _ = textbox(840, 400, "POSIX Message Queues (mq_open)\n• Пріоритетизація повідомлень (0..32767)\n• Збереження меж кожного пакета", size=9.5, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_mq)

    frags.append(arrow(840, 435, 840, 465, color=LINE, sw=1.2))

    b_limit, _, _ = textbox(840, 520, "Особливості експлуатації:\n• Pipe: без збереження меж повідомлень\n• MQ: незручний mq_notify для epoll;\n  повідомлення зависають у ядрі", size=9.5, fill=RED_F, stroke=RED_S)
    frags.append(b_limit)

    b_pm_res, _, _ = textbox(840, 585, "Вибір: Pipes для CLI; MQ для RT", size=10, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_pm_res)

    return render(os.path.join(IMG, "decision-tree.svg"), W, H, *frags)

def fig_ipc_tradeoffs():
    """ipc-tradeoffs.svg: Багатовимірне порівняння характеристик IPC."""
    W, H = 960, 480
    frags = []

    frags.append(text(480, 28, "Порівняння властивостей IPC: швидкість, складність, надійність та ізоляція", size=15, bold=True, color="#1e293b"))

    rows = [
        ("Пропускна здатність", "Середня (копіювання)", "Висока (буфер ядра)", "Максимальна (0 копій)", "Середня (копіювання)"),
        ("Латентність (дрібні)", "Низька (~1-2 мкс)", "Низька (~1.5-2.5 мкс)", "Ультранизька (<0.3 мкс)", "Середня (~3-5 мкс)"),
        ("Складність коду", "Мінімальна (read/write)", "Середня (стандартний API)", "Висока (м'ютекси, futex)", "Середня (mq_open/send)"),
        ("Інтеграція в epoll", "Рідна (файловий FD)", "Рідна (файловий FD)", "Через допоміжний eventfd", "Складна (через mq_notify)"),
        ("Передача прав / FDs", "Неможливо", "Так (SCM_RIGHTS)", "Через дескриптор memfd", "Неможливо"),
        ("Автентифікація", "Тільки біти прав FS", "Ядерна (SO_PEERCRED)", "Тільки біти прав FS", "Тільки біти прав FS"),
        ("Збереження меж", "Ні (потік байтів)", "Так (SEQPACKET / DGRAM)", "Ні (структура у RAM)", "Так (за повідомленнями)"),
        ("Поведінка при збої", "Автоматична (EOF/SIGPIPE)", "Автоматична (POLLHUP/EOF)", "Ризик зависання м'ютекса", "Повідомлення висять у черзі")
    ]

    # Шапка таблиці
    y = 65
    frags.append(rect(20, y, 920, 36, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    frags.append(text(105, y + 23, "Критерій вибору", size=11, bold=True, color="#0f172a"))
    frags.append(text(270, y + 23, "Pipes / FIFO", size=11, bold=True, color=GREEN_S))
    frags.append(text(455, y + 23, "Unix Domain Sockets", size=11, bold=True, color=PURPLE_S))
    frags.append(text(650, y + 23, "POSIX Shared Memory", size=11, bold=True, color=BLUE_S))
    frags.append(text(835, y + 23, "POSIX Message Queues", size=11, bold=True, color=AMBER_S))

    y += 36
    for i, row in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        frags.append(rect(20, y, 920, 38, fill=bg, stroke="#cbd5e1", sw=0.8, rx=0))
        frags.append(text(105, y + 24, row[0], size=10, bold=True, color="#334155"))
        frags.append(text(270, y + 24, row[1], size=9.5, color="#1e293b"))
        frags.append(text(455, y + 24, row[2], size=9.5, color="#1e293b"))
        frags.append(text(650, y + 24, row[3], size=9.5, color="#1e293b"))
        frags.append(text(835, y + 24, row[4], size=9.5, color="#1e293b"))
        y += 38

    # Пояснювальний висновок
    b_note, _, _ = textbox(480, 440, "Ключове правило: починайте з Unix Domain Sockets (SEQPACKET); якщо виміри показують вузьке місце\nу копіюванні великих даних — переходьте на спільну пам'ять (memfd + eventfd) для тіла даних.", size=10, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_note)

    return render(os.path.join(IMG, "ipc-tradeoffs.svg"), W, H, *frags)

def fig_failure_modes():
    """failure-modes.svg: Поведінка примітивів взаємодії при раптовому збої або аварійному завершенні процесу."""
    W, H = 960, 420
    frags = []

    frags.append(text(480, 26, "Аварія процесу (SIGKILL / Segfault): автоматичне очищення ядра проти завислого стану", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: Дескрипторні IPC (Pipes, Unix Sockets)
    frags.append(rect(30, 55, 430, 335, fill="#f8fafc", stroke=GREEN_S, sw=1.2, rx=8))
    b_fd_title, _, _ = textbox(245, 85, "Дескрипторні IPC (Pipes, Unix Sockets)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_fd_title)

    frags.append(rect(50, 120, 390, 85, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(245, 142, "1. Процес падає → Ядро закриває всі відкриті дескриптори", size=10, bold=True, color="#0f172a"))
    frags.append(text(245, 165, "• Лічильник посилань struct file падає до нуля", size=9.5, color="#334155"))
    frags.append(text(245, 185, "• Стан каналу/сокету переходить у статус закритого кінця", size=9.5, color="#334155"))

    frags.append(arrow(245, 205, 245, 235, color=GREEN_S, sw=1.5))

    frags.append(rect(50, 235, 390, 135, fill=GREEN_F, stroke=GREEN_S, rx=6))
    frags.append(text(245, 258, "Детерміноване сповіщення іншої сторони", size=10.5, bold=True, color=GREEN_S))
    frags.append(text(65, 282, "• Читач: epoll видає EPOLLHUP / EPOLLRDHUP, read() повертає 0 (EOF)", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(65, 305, "• Записувач: спроба write() викликає сигнал SIGPIPE та помилку EPIPE", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(65, 328, "• Ресурси ядра звільняються автоматично без витоків у системі", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(65, 351, "• Відновлення: супервізор просто перезапускає дочірній процес", size=9.5, color="#0f172a", anchor="start"))

    # Права колонка: Спільна пам'ять без дескрипторного нагляду
    frags.append(rect(500, 55, 430, 335, fill="#f8fafc", stroke=RED_S, sw=1.2, rx=8))
    b_shm_title, _, _ = textbox(715, 85, "Спільна пам'ять (Shared Memory)", size=12, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_shm_title)

    frags.append(rect(520, 120, 390, 85, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(715, 142, "1. Процес падає посеред критичної секції запису", size=10, bold=True, color="#0f172a"))
    frags.append(text(715, 165, "• М'ютекс залишається захопленим у пам'яті RAM", size=9.5, color="#334155"))
    frags.append(text(715, 185, "• Структури даних (голови/хвости буферів) частково оновлені", size=9.5, color="#334155"))

    frags.append(arrow(715, 205, 715, 235, color=RED_S, sw=1.5))

    frags.append(rect(520, 235, 390, 135, fill=RED_F, stroke=RED_S, rx=6))
    frags.append(text(715, 258, "Небезпека мертвого блокування (Deadlock) та сміття", size=10.5, bold=True, color=RED_S))
    frags.append(text(535, 282, "• Стандартний mutex: сусідні процеси засинають назавжди", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(535, 305, "• Порятунок: PTHREAD_MUTEX_ROBUST повертає EOWNERDEAD", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(535, 328, "• shm_open: файли в /dev/shm виживають і засмічують пам'ять RAM", size=9.5, color="#0f172a", anchor="start"))
    frags.append(text(535, 351, "• memfd_create: анонімна пам'ять зникає автоматично з останнім FD", size=9.5, color="#0f172a", anchor="start"))

    return render(os.path.join(IMG, "failure-modes.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_decision_tree()
    fig_ipc_tradeoffs()
    fig_failure_modes()
    print("All figures generated successfully.")
