# -*- coding: utf-8 -*-
"""Фігури до теми «Протокол Jobserver: координація паралелізму між процесами збірки»."""
import sys, os

# 4 рівні вгору від root/sys/sys-bsystem/jobserver-protocol до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий / перепідписка / деградація
CLEAN = "#eaf7ef"     # зеленуватий / узгоджений розподіл
PANEL = "#f8fafc"
ACCENT = "#eaf0fd"    # блакитний
WARN = "#fef9e7"      # жовтуватий / черга / семафор


# ── 1. Неконтрольована рекурсія проти Jobserver ─────────────────────────────
def fig_oversubscription_tree():
    W, H = 1040, 470
    p = []

    # Заголовок
    p.append(text(520, 35, "Розподіл навантаження CPU: рекурсивний вибух проти пулу Jobserver", size=16, bold=True))

    # Ліва колонка: Неконтрольована рекурсія
    p.append(rect(30, 60, 470, 385, fill=PANEL, stroke=POS, sw=1.6))
    p.append(text(265, 90, "Без Jobserver: рекурсивна перепідписка", size=14, bold=True, color=POS))

    # Вузли лівої колонки
    tb1, _, _ = textbox(265, 135, "Головний процес: make -j8\n(Запускає 8 підпроєктів)", size=12.5, bold=True, fill=BG, stroke=LINE)
    p.append(tb1)

    p.append(arrow(170, 165, 130, 205, color=POS, sw=1.6))
    p.append(arrow(265, 165, 265, 205, color=POS, sw=1.6))
    p.append(arrow(360, 165, 400, 205, color=POS, sw=1.6))

    tb_sub1, _, _ = textbox(120, 235, "Sub-Make 1\n(-j8)", size=11.5, bold=True, fill=DIRTY, stroke=POS)
    tb_sub2, _, _ = textbox(265, 235, "Sub-Make 2…7\n(-j8 кожному)", size=11.5, bold=True, fill=DIRTY, stroke=POS)
    tb_sub3, _, _ = textbox(410, 235, "Sub-Make 8\n(-j8)", size=11.5, bold=True, fill=DIRTY, stroke=POS)
    p.append(tb_sub1)
    p.append(tb_sub2)
    p.append(tb_sub3)

    p.append(arrow(120, 265, 120, 305, color=POS, sw=1.6))
    p.append(arrow(265, 265, 265, 305, color=POS, sw=1.6))
    p.append(arrow(410, 265, 410, 305, color=POS, sw=1.6))

    fb_bad = fitbox(55, 310, 420, 115,
                    "Одночасно стартує: 8 × 8 = 64 компілятори!\n"
                    "• 8 фізичних ядер CPU перевантажені\n"
                    "• Вимивання кешів L1/L2/L3 через перемикання контекстів\n"
                    "• Вибух пам'яті (до 2 ГБ на процес) → OOM Killer / Swap",
                    size=12, fill=DIRTY, stroke=POS)
    p.append(fb_bad)

    # Права колонка: Координація через Jobserver
    p.append(rect(540, 60, 470, 385, fill=PANEL, stroke=FIELD, sw=1.6))
    p.append(text(775, 90, "З Jobserver: спільний пул токенів", size=14, bold=True, color=FIELD))

    tb2, _, _ = textbox(775, 135, "Головний процес: make -j8\n(Створює пул із 8 токенів)", size=12.5, bold=True, fill=BG, stroke=LINE)
    p.append(tb2)

    # Центральний пул токенів
    p.append(arrow(775, 165, 775, 195, color=FIELD, sw=1.6))
    tb_pool, _, _ = textbox(775, 220, "Пул токенів (Pipe / Semaphore)\n[●] [●] [●] [●] [●] [●] [●] [●]\n(1 неявний + 7 явних у черзі)", size=12, bold=True, fill=WARN, stroke=FIELD)
    p.append(tb_pool)

    p.append(arrow(700, 250, 640, 290, color=FIELD, sw=1.6))
    p.append(arrow(775, 250, 775, 290, color=FIELD, sw=1.6))
    p.append(arrow(850, 250, 910, 290, color=FIELD, sw=1.6))

    fb_good = fitbox(565, 295, 420, 130,
                     "Динамічний запит токенів за потребою:\n"
                     "• Сумарно працює строго не більше 8 компіляторів\n"
                     "• Вільні ядра миттєво переходять до завантажених гілок\n"
                     "• Немає простоїв, пам'ять під повним контролем\n"
                     "• 100% утилізація CPU без надлишкових перемикань",
                     size=12, fill=CLEAN, stroke=FIELD)
    p.append(fb_good)

    render(os.path.join(IMG, "oversubscription-tree.svg"), W, H, *p,
           title="Розподіл навантаження CPU: рекурсивний вибух проти пулу Jobserver")


# ── 2. Класичний обмін токенами через POSIX Pipe ───────────────────────────
def fig_pipe_token_exchange():
    W, H = 1000, 480
    p = []

    p.append(text(500, 35, "Життєвий цикл токена в POSIX Jobserver (GNU Make Pipe)", size=16, bold=True))

    # Батьківський процес
    p.append(rect(40, 70, 420, 380, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(250, 100, "Кореневий процес (Make -j4)", size=14, bold=True, color=LINE))

    p.append(fitbox(60, 120, 380, 95,
                    "1. Створює pipe(fds) → rfd=3, wfd=4\n"
                    "2. Записує 3 байти токенів у wfd: '+++'\n"
                    "3. 1 токен залишає собі як неявний слот\n"
                    "4. Експортує MAKEFLAGS=\"--jobserver-auth=3,4\"",
                    size=12, fill=BG, stroke=MUTED))

    # Стан пайпа (буфер ядра)
    p.append(rect(510, 70, 450, 380, fill=PANEL, stroke=FIELD, sw=1.5))
    p.append(text(735, 100, "Буфер Pipe у ядрі (FIFO токенів)", size=14, bold=True, color=FIELD))

    # Відображення байтів у пайпі
    p.append(rect(540, 130, 390, 60, fill=WARN, stroke=FIELD, sw=1.8))
    p.append(text(735, 155, "Пайп: [ Байт '+' ] [ Байт '+' ] [ Байт '+' ]", size=13, bold=True, color=INK))
    p.append(text(735, 175, "Доступно токенів у ядрі: 3 (загалом паралелізм = 4)", size=11, color=MUTED))

    # Кроки отримання та повернення
    p.append(arrow(440, 250, 540, 250, color=NEG, sw=2))
    p.append(fitbox(60, 230, 360, 80,
                    "Крок 1: Запит токена (Acquire)\n"
                    "read(rfd, &token, 1);\n"
                    "→ Якщо пайп порожній, процес блокується",
                    size=12, fill=ACCENT, stroke=NEG))

    p.append(fitbox(540, 220, 390, 90,
                    "Компілятор запущено (PID 4092)\n"
                    "• Працює g++ -c main.cpp\n"
                    "• Токен перебуває у розпорядженні процесу\n"
                    "• У пайпі лишилося 2 токени",
                    size=12, fill=BG, stroke=MUTED))

    p.append(arrow(540, 360, 440, 360, color=FIELD, sw=2))
    p.append(fitbox(60, 340, 360, 85,
                    "Крок 2: Повернення токена (Release)\n"
                    "waitpid(pid, &status, 0);\n"
                    "write(wfd, &token, 1);\n"
                    "→ Токен знову доступний іншим процесам",
                    size=12, fill=CLEAN, stroke=FIELD))

    p.append(fitbox(540, 340, 390, 85,
                    "Компілятор завершив роботу\n"
                    "• Байт '+' повернуто у буфер пайпа\n"
                    "• Ядро розблоковує інший процес у черзі read()",
                    size=12, fill=CLEAN, stroke=FIELD))

    render(os.path.join(IMG, "pipe-token-exchange.svg"), W, H, *p,
           title="Життєвий цикл токена в POSIX Jobserver (GNU Make Pipe)")


# ── 3. Windows Named Semaphore ─────────────────────────────────────────────
def fig_windows_named_semaphore():
    W, H = 1020, 460
    p = []

    p.append(text(510, 35, "Архітектура Windows Jobserver на основі Named Semaphore", size=16, bold=True))

    # Об'єкт ядра Windows
    p.append(rect(340, 70, 340, 150, fill=WARN, stroke=POS, sw=1.8))
    p.append(text(510, 100, "Об'єкт ядра: Named Semaphore", size=14, bold=True, color=POS))
    p.append(text(510, 125, "Шлях: \\BaseNamedObjects\\jobserver_sem_4102", size=11.5, color=MUTED))
    p.append(fitbox(355, 140, 310, 65,
                    "Поточний лічильник: N - 1 токенів\n"
                    "CreateSemaphoreA(NULL, N-1, N-1, name);",
                    size=12, fill=BG, stroke=MUTED))

    # Клієнти зліва і справа
    p.append(rect(40, 260, 420, 175, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(250, 285, "Клієнт 1: GNU Make / CMake", size=13.5, bold=True))
    p.append(fitbox(55, 305, 390, 115,
                    "Отримує ім'я через --jobserver-auth=jobserver_sem_4102\n"
                    "1. OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE...)\n"
                    "2. WaitForSingleObject(hSem, INFINITE) → токен захоплено\n"
                    "3. ReleaseSemaphore(hSem, 1, NULL) → токен звільнено",
                    size=11.5, fill=BG, stroke=MUTED))

    p.append(rect(560, 260, 420, 175, fill=PANEL, stroke=FIELD, sw=1.5))
    p.append(text(770, 285, "Клієнт 2: Cargo / Rustc / Ninja", size=13.5, bold=True, color=FIELD))
    p.append(fitbox(575, 305, 390, 115,
                    "Атомарне очікування токена та завершення задач:\n"
                    "WaitForMultipleObjects(\n"
                    "    handles = [hSem, hChildProc1, hChildProc2...],\n"
                    "    bWaitAll = FALSE, dwMilliseconds = INFINITE\n"
                    ");  // Розблоковується і по токену, і по виходу процесу",
                    size=11.5, fill=CLEAN, stroke=FIELD))

    # Стрілки взаємодії
    p.append(arrow(350, 260, 430, 225, color=LINE, sw=1.6))
    p.append(arrow(670, 260, 590, 225, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "windows-named-semaphore.svg"), W, H, *p,
           title="Архітектура Windows Jobserver на основі Named Semaphore")


# ── 4. Алгоритм уникнення дедлоків (Deadlock Avoidance) ──────────────────────
def fig_deadlock_avoidance_flow():
    W, H = 1000, 480
    p = []

    p.append(text(500, 35, "Диспетчеризація токенів: цикл подій клієнта без дедлоків", size=16, bold=True))

    # Блоки алгоритму
    tb_start, _, _ = textbox(500, 80, "Початок кроку планувальника\n(Черга готових задач графа > 0)", size=12.5, bold=True, fill=BG, stroke=LINE)
    p.append(tb_start)

    p.append(arrow(500, 105, 500, 135, color=LINE, sw=1.6))

    # Умова 1: Неявний токен
    tb_cond1, _, _ = textbox(500, 160, "Чи використано неявний токен поточного процесу?", size=12.5, bold=True, fill=ACCENT, stroke=NEG)
    p.append(tb_cond1)

    # Гілка ТАК -> Запуск одразу
    p.append(arrow(340, 160, 230, 160, color=FIELD, sw=1.6))
    tb_imp, _, _ = textbox(135, 160, "Використати неявний слот\n(Без читання з пайпа)", size=11.5, bold=True, fill=CLEAN, stroke=FIELD)
    p.append(tb_imp)

    p.append(arrow(135, 185, 135, 275, color=FIELD, sw=1.6))

    # Гілка НІ -> Запит токена
    p.append(arrow(500, 185, 500, 220, color=LINE, sw=1.6))
    tb_acquire, _, _ = textbox(500, 245, "Неблокувальний запит токена (O_NONBLOCK / poll)\nread(rfd, &token, 1)", size=12, bold=True, fill=WARN, stroke=LINE)
    p.append(tb_acquire)

    # Успіх захоплення
    p.append(arrow(500, 270, 310, 310, color=FIELD, sw=1.6))
    tb_exec, _, _ = textbox(220, 320, "Запуск дочірнього процесу\n(fork + execve / CreateProcess)", size=12, bold=True, fill=CLEAN, stroke=FIELD)
    p.append(tb_exec)

    # Немає токенів у пайпі (EAGAIN / EWOULDBLOCK)
    p.append(arrow(650, 245, 780, 245, color=POS, sw=1.6))
    tb_wait, _, _ = textbox(810, 300, "Пайп порожній (EAGAIN)\nОчікування завершення робітників:\n• poll([rfd, pidfds...])\n• waitpid(-1, &st, 0)\n• Повернути токени перед сном!", size=11.5, bold=True, fill=DIRTY, stroke=POS)
    p.append(tb_wait)

    p.append(arrow(220, 350, 220, 400, color=LINE, sw=1.6))
    tb_finish, _, _ = textbox(500, 420, "Завершення дочірньої задачі → Повернення токена у Pipe/Семафор\nwrite(wfd, &token, 1) / ReleaseSemaphore()", size=12, bold=True, fill=BG, stroke=FIELD)
    p.append(tb_finish)

    p.append(arrow(220, 420, 310, 420, color=FIELD, sw=1.6))
    p.append(arrow(810, 355, 690, 420, color=LINE, sw=1.6))

    render(os.path.join(IMG, "deadlock-avoidance-flow.svg"), W, H, *p,
           title="Диспетчеризація токенів: цикл подій клієнта без дедлоків")


if __name__ == "__main__":
    fig_oversubscription_tree()
    fig_pipe_token_exchange()
    fig_windows_named_semaphore()
    fig_deadlock_avoidance_flow()
    print("Всі 4 фігури згенеровано успішно.")
