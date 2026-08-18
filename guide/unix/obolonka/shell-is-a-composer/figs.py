# -*- coding: utf-8 -*-
"""Фігури для теми «Оболонка як композитор: один конвеєр наскрізь» (guide/unix/obolonka/shell-is-a-composer)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_pipeline_fd_topology():
    """pipeline-fd-topology.svg: Топологія дескрипторів та успадкування каналів між ядром і процесами."""
    W, H = 1000, 520
    frags = []

    # Заголовок
    frags.append(text(500, 32, "Топологія дескрипторів конвеєра: виділення в ядрі та успадкування", size=16, bold=True, color="#1e293b"))

    # Панель Оболонки (Батьківський процес)
    frags.append(rect(40, 65, 420, 200, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_shell, _, _ = textbox(250, 92, "Батьківський процес: Оболонка (Shell, PID 1000)", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_shell)

    frags.append(text(65, 125, "1. pipe(p1)  → дескриптори [3: read, 4: write]", size=11, color="#334155", anchor="start", bold=True))
    frags.append(text(65, 148, "2. pipe(p2)  → дескриптори [5: read, 6: write]", size=11, color="#334155", anchor="start", bold=True))
    frags.append(text(65, 172, "Таблиця файлових дескрипторів оболонки містить FD 0..6.", size=10.5, color="#64748b", anchor="start"))
    frags.append(text(65, 195, "Оболонка робить fork() для кожного елемента конвеєра.", size=10.5, color="#64748b", anchor="start"))
    frags.append(text(65, 218, "УСІ діти спочатку успадковують ПОВНИЙ набір FD 0..6!", size=10.5, color=RED_S, anchor="start", bold=True))
    frags.append(text(65, 242, "3. Оболонка закриває FD 3, 4, 5, 6 одразу після запуску дітей.", size=10, color=GREEN_S, anchor="start", bold=True))

    # Панель Ядра (Кільцеві буфери каналів)
    frags.append(rect(500, 65, 460, 200, fill="#fdfbf7", stroke=AMBER_S, sw=1.2, rx=8))
    b_kern, _, _ = textbox(730, 92, "Простір ядра: Відкриті файли (Open File Descriptions)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_kern)

    # Буфер каналу 1
    frags.append(rect(520, 120, 420, 60, fill="#ffffff", stroke="#d97706", sw=1.1, rx=6))
    frags.append(text(730, 140, "Кільцевий буфер Каналу 1 (pipe 1, 64 КіБ у RAM)", size=11, bold=True, color="#92400e"))
    frags.append(text(540, 162, "struct pipe_inode_info: wr_wait / rd_wait, refcount", size=10, color="#78350f", anchor="start"))

    # Буфер каналу 2
    frags.append(rect(520, 190, 420, 60, fill="#ffffff", stroke="#d97706", sw=1.1, rx=6))
    frags.append(text(730, 210, "Кільцевий буфер Каналу 2 (pipe 2, 64 КіБ у RAM)", size=11, bold=True, color="#92400e"))
    frags.append(text(540, 232, "struct pipe_inode_info: wr_wait / rd_wait, refcount", size=10, color="#78350f", anchor="start"))

    # Нижня частина: 3 дочірні процеси
    # Процес 1: grep (PID 1001)
    frags.append(rect(40, 295, 280, 200, fill="#ffffff", stroke=BLUE_S, sw=1.2, rx=8))
    b_p1, _, _ = textbox(180, 320, "Дитина 1: cmd1 (grep)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_p1)
    frags.append(text(60, 350, "FD 0 (stdin): термінал / файл", size=10, color="#334155", anchor="start"))
    frags.append(text(60, 375, "dup2(4, 1) → FD 1 = Pipe 1 Write", size=10.5, color=GREEN_S, anchor="start", bold=True))
    frags.append(text(60, 400, "close(3) — закрити read кінця", size=10, color=RED_S, anchor="start"))
    frags.append(text(60, 425, "close(4) — закрити старий FD", size=10, color=RED_S, anchor="start"))
    frags.append(text(60, 450, "close(5, 6) — закрити Pipe 2", size=10, color=RED_S, anchor="start"))
    frags.append(text(60, 475, "execve(\"grep\", ...)", size=10, color=PURPLE_S, anchor="start", bold=True))

    # Процес 2: cut (PID 1002)
    frags.append(rect(360, 295, 280, 200, fill="#ffffff", stroke=TEAL_S, sw=1.2, rx=8))
    b_p2, _, _ = textbox(500, 320, "Дитина 2: cmd2 (cut)", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_p2)
    frags.append(text(380, 350, "dup2(3, 0) → FD 0 = Pipe 1 Read", size=10.5, color=GREEN_S, anchor="start", bold=True))
    frags.append(text(380, 375, "dup2(6, 1) → FD 1 = Pipe 2 Write", size=10.5, color=GREEN_S, anchor="start", bold=True))
    frags.append(text(380, 400, "close(3, 4) — очистити Pipe 1", size=10, color=RED_S, anchor="start"))
    frags.append(text(380, 425, "close(5, 6) — очистити Pipe 2", size=10, color=RED_S, anchor="start"))
    frags.append(text(380, 450, "Потоки: [P1 Read] → [P2 Write]", size=10, color="#0f766e", anchor="start"))
    frags.append(text(380, 475, "execve(\"cut\", ...)", size=10, color=PURPLE_S, anchor="start", bold=True))

    # Процес 3: wc (PID 1003)
    frags.append(rect(680, 295, 280, 200, fill="#ffffff", stroke=PURPLE_S, sw=1.2, rx=8))
    b_p3, _, _ = textbox(820, 320, "Дитина 3: cmd3 (wc)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_p3)
    frags.append(text(700, 350, "dup2(5, 0) → FD 0 = Pipe 2 Read", size=10.5, color=GREEN_S, anchor="start", bold=True))
    frags.append(text(700, 375, "FD 1 (stdout): термінал / файл", size=10, color="#334155", anchor="start"))
    frags.append(text(700, 400, "close(3, 4) — закрити Pipe 1", size=10, color=RED_S, anchor="start"))
    frags.append(text(700, 425, "close(5) — закрити старий FD", size=10, color=RED_S, anchor="start"))
    frags.append(text(700, 450, "close(6) — закрити write кінця", size=10, color=RED_S, anchor="start"))
    frags.append(text(700, 475, "execve(\"wc\", ...)", size=10, color=PURPLE_S, anchor="start", bold=True))

    render(os.path.join(IMG, "pipeline-fd-topology.svg"), W, H, *frags)

def fig_fd_plumbing_and_closure():
    """fd-plumbing-and-closure.svg: Перенаправлення через dup2 та небезпека незакритих дескрипторів."""
    W, H = 1000, 480
    frags = []

    # Заголовок
    frags.append(text(500, 30, "Матриця закріплення та закриття файлових дескрипторів у конвеєрі", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Правильне перенаправлення
    frags.append(rect(30, 55, 450, 400, fill="#f8fafc", stroke=GREEN_S, sw=1.3, rx=8))
    b_ok, _, _ = textbox(255, 82, "Коректна схема: лічильники посилань падають до 1", size=11.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_ok)

    items_ok = [
        "1. Дитина A: dup2(p1[1], STDOUT) → close(p1[0]) + close(p1[1])",
        "   Єдиний записувач у Pipe 1 — FD 1 процесу A (refcount=1).",
        "2. Дитина B: dup2(p1[0], STDIN)  → close(p1[0]) + close(p1[1])",
        "   Єдиний читач із Pipe 1 — FD 0 процесу B (refcount=1).",
        "3. Батьківська оболонка: close(p1[0]) + close(p1[1])",
        "   Оболонка не тримає дескрипторів каналу у своїй таблиці.",
        "▶ РЕЗУЛЬТАТ ПРИ ЗАВЕРШЕННІ A:",
        "   • A завершує роботу → ядро автоматично закриває FD 1.",
        "   • Лічильник записувачів у Pipe 1 стає 0!",
        "   • Наступний read() у процесі B миттєво отримує EOF (0 байтів).",
        "   • Процес B коректно завершує свій цикл обробки."
    ]
    for i, line_text in enumerate(items_ok):
        col = GREEN_S if "РЕЗУЛЬТАТ" in line_text else "#1e293b" if line_text.startswith(" ") else "#334155"
        bld = True if ("РЕЗУЛЬТАТ" in line_text or "Коректна" in line_text) else False
        frags.append(text(45, 118 + i * 28, line_text, size=9.5, color=col, anchor="start", bold=bld))

    # Права частина: Фатальна помилка незакритих FD
    frags.append(rect(520, 55, 450, 400, fill="#fffafb", stroke=RED_S, sw=1.3, rx=8))
    b_err, _, _ = textbox(745, 82, "Помилка: оболонка забула закрити p1[1] (FD leak)", size=11.5, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_err)

    items_err = [
        "1. Оболонка зробила fork(), але НЕ викликала close(p1[1]).",
        "   У системі ДВА відкриті дескриптори запису: у дитини A і в Shell.",
        "2. Дитина A завершила обробку даних і вийшла через exit(0).",
        "   Ядро закрило FD 1 дитини A. Лічильник записувачів: 2 → 1.",
        "3. Процес B зчитує залишок буфера і викликає read(0, ...).",
        "   Буфер порожній. Чи закритий канал?",
        "   НІ! Оболонка все ще тримає відкритий FD p1[1]!",
        "▶ КАТАСТРОФА: ДЕДЛОК (Вічне зависання конвеєра)",
        "   • Ядро НЕ повертає EOF, бо теоретично Shell може щось записати.",
        "   • Процес B засинає в ядрі назавжди (TASK_INTERRUPTIBLE).",
        "   • Конвеєр зависає, ресурси заблоковані, скрипт не завершується."
    ]
    for i, line_text in enumerate(items_err):
        col = RED_S if ("КАТАСТРОФА" in line_text or "НІ!" in line_text) else "#1e293b" if line_text.startswith(" ") else "#334155"
        bld = True if ("КАТАСТРОФА" in line_text or "НІ!" in line_text) else False
        frags.append(text(535, 118 + i * 28, line_text, size=9.5, color=col, anchor="start", bold=bld))

    render(os.path.join(IMG, "fd-plumbing-and-closure.svg"), W, H, *frags)

def fig_pipeline_lifecycle_sequence():
    """pipeline-lifecycle-sequence.svg: Наскрізна хронологія життя конвеєра cmd1 | cmd2 | cmd3."""
    W, H = 1020, 540
    frags = []

    frags.append(text(510, 30, "Повна хронологія конвеєра: налаштування, потокова передача та завершення", size=15.5, bold=True, color="#1e293b"))

    # Стовпці сутностей
    cols = [
        (130, "Оболонка (Shell)", BLUE_F, BLUE_S),
        (370, "Дитина 1 (grep)", TEAL_F, TEAL_S),
        (610, "Дитина 2 (head -n 2)", PURPLE_F, PURPLE_S),
        (850, "Ядро: Канал (Pipe)", AMBER_F, AMBER_S)
    ]
    for cx, label, fcol, scol in cols:
        b, _, _ = textbox(cx, 68, label, size=11, bold=True, fill=fcol, stroke=scol)
        frags.append(b)
        frags.append(line(cx, 92, cx, 515, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Етапи взаємодії
    events = [
        # (y, from_x, to_x, label, color, bold)
        (115, 130, 850, "pipe2(&pfd, O_CLOEXEC) → виділення кільцевого буфера 64 КіБ", BLUE_S, True),
        (145, 130, 370, "fork() → Дитина 1 (PID 2001)", BLUE_S, False),
        (175, 130, 610, "fork() → Дитина 2 (PID 2002)", BLUE_S, False),
        (205, 130, 610, "setpgid(2001, 2001) + setpgid(2002, 2001) [єдина група]", PURPLE_S, True),
        (235, 130, 130, "tcsetpgrp(tty, 2001) → передача переднього плану термінала", "#334155", False),
        (265, 370, 850, "dup2(pfd[1], 1) → write(1, data) [потоковий запис]", TEAL_S, False),
        (295, 610, 850, "dup2(pfd[0], 0) → read(0, buf) [потокове зчитування]", PURPLE_S, False),
        (330, 850, 850, "⚡ Backpressure: якщо буфер 64 КіБ заповнено, write() блокується", AMBER_S, True),
        (370, 610, 610, "head прочитав 2 рядки і робить exit(0) [закриття FD 0]", RED_S, True),
        (405, 850, 370, "⚡ Дитина 1 робить черговий write() → ядро шле SIGPIPE (-EPIPE)", RED_S, True),
        (440, 370, 370, "Дитина 1 гине від SIGPIPE (статус 128 + 13 = 141)", RED_S, False),
        (475, 130, 610, "waitpid(-2001, &st, 0) → збір кодів виходу, pipefail аналіз", BLUE_S, True),
        (505, 130, 130, "tcsetpgrp(tty, shell_pgid) → повернення термінала оболонці", GREEN_S, True),
    ]

    for y, x1, x2, msg, col, bld in events:
        if x1 == x2:
            # Локальна дія
            b, _, _ = textbox(x1, y, msg, size=9.5, pad=5, fill="#ffffff", stroke=col, color=col, bold=bld)
            frags.append(b)
        else:
            # Передача повідомлення
            frags.append(line(x1, y, x2, y, color=col, sw=1.4))
            mid_x = (x1 + x2) / 2
            b, _, _ = textbox(mid_x, y - 10, msg, size=9.2, pad=4, fill="#ffffff", stroke=col, color=col, bold=bld)
            frags.append(b)

    render(os.path.join(IMG, "pipeline-lifecycle-sequence.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_pipeline_fd_topology()
    fig_fd_plumbing_and_closure()
    fig_pipeline_lifecycle_sequence()
    print("Всі фігури успішно згенеровано.")
