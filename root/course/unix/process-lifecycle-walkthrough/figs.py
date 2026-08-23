# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY_S  = "#c8ced6"
BLUE_F  = "#eef3fb"
RED_F   = "#fdeeec"
GREEN_F = "#eef7f0"
AMBER_F = "#fef9e7"
AMBER_S = "#d4ac0d"
PURP_F  = "#f5eef8"
PURP_S  = "#8e44ad"

# ── Фіг. 1: Повний життєвий цикл процесу (автомат станів ядра) ───────────────
def fig_lifecycle_state_machine():
    W, H = 1180, 800
    p = []

    p.append(text(W / 2, 36, "Повний автомат станів процесу в ядрі Linux", size=16, color=INK, bold=True))

    # Ряд 1: Народження, Running, Stopped/Traced
    p.append(fitbox(40, 70, 260, 110,
                    ["1. НАРОДЖЕННЯ",
                     "fork() / clone3()",
                     "alloc_task_struct(), alloc_pid()",
                     "дублювання mm (COW) та дескрипторів"],
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.6))

    p.append(fitbox(360, 65, 420, 120,
                    ["2. СТАН TASK_RUNNING (R)",
                     "Черга планувальника CFS / EEVDF",
                     "• Стоїть у черзі готових (чекає на ядро ЦП)",
                     "• Виконує інструкції на процесорі (user/kernel)"],
                    size=12.5, fill=GREEN_F, stroke=FIELD, sw=1.8))

    p.append(fitbox(840, 70, 300, 110,
                    ["TASK_STOPPED / TRACED (T / t)",
                     "Зупинено сигналами керування (SIGSTOP)",
                     "або ptrace (налагодження/strace)",
                     "Відновлення: сигнал SIGCONT"],
                    size=12, fill=PURP_F, stroke=PURP_S, sw=1.5))

    # Ряд 2: Стани сну та вихід do_exit
    p.append(fitbox(40, 260, 330, 125,
                    ["TASK_INTERRUPTIBLE (S)",
                     "Сон у wait queue (сокет, канал, таймер)",
                     "Прокидається від надходження даних",
                     "або доставки сигналу (wake_up)"],
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.5))

    p.append(fitbox(410, 260, 330, 125,
                    ["TASK_UNINTERRUPTIBLE (D)",
                     "Сон на апаратному I/O (диск, сторінковий збій)",
                     "Ігнорує звичайні сигнали заради цілісності",
                     "TASK_KILLABLE: реагує лише на SIGKILL"],
                    size=12, fill=AMBER_F, stroke=AMBER_S, sw=1.5))

    p.append(fitbox(780, 260, 360, 125,
                    ["3. ЗАВЕРШЕННЯ: do_exit() (PF_EXITING)",
                     "exit_group() або смертельний сигнал",
                     "• exit_mm(): звільнення адресного простору",
                     "• exit_files(): закриття дескрипторів та сокетів"],
                    size=12, fill=RED_F, stroke=POS, sw=1.6))

    # Ряд 3: Зомбі та Прибирання
    p.append(fitbox(180, 460, 400, 120,
                    ["4. СТАН ЗОМБІ: EXIT_ZOMBIE (Z)",
                     "Усі ресурси пам'яті й дескрипторів звільнено.",
                     "Лишилися: task_struct, PID, exit_code, rusage.",
                     "Батькові надіслано сигнал SIGCHLD."],
                    size=12, fill=RED_F, stroke=POS, sw=1.6))

    p.append(fitbox(640, 460, 400, 120,
                    ["5. ПРИБИРАННЯ: release_task()",
                     "Батько викликає waitpid() / waitid().",
                     "• Статус і лічильники rusage скопійовано батькові.",
                     "• PID повернуто в пул, task_struct звільнено RCU."],
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.6))

    # Стрілки
    # 1 -> 2
    p.append(arrow(300, 125, 360, 125, color=INK))
    p.append(text(330, 115, "wake_up", size=10.5, color=MUTED))

    # 2 <-> T
    p.append(arrow(780, 110, 840, 110, color=PURP_S))
    p.append(arrow(840, 135, 780, 135, color=PURP_S))
    p.append(text(810, 100, "SIGSTOP", size=10, color=PURP_S))
    p.append(text(810, 150, "SIGCONT", size=10, color=PURP_S))

    # 2 <-> S
    p.append(arrow(420, 185, 230, 260, color=INK))
    p.append(arrow(260, 260, 450, 185, color=INK))
    p.append(text(300, 215, "wait / wake", size=10.5, color=MUTED))

    # 2 <-> D
    p.append(arrow(550, 185, 550, 260, color=AMBER_S))
    p.append(arrow(590, 260, 590, 185, color=AMBER_S))
    p.append(text(625, 225, "I/O запит/готово", size=10, color=AMBER_S))

    # 2 -> do_exit
    p.append(arrow(720, 185, 880, 260, color=POS, sw=1.8))
    p.append(text(840, 220, "exit_group()", size=11, color=POS, bold=True))

    # do_exit -> ZOMBIE
    p.append(arrow(880, 385, 460, 460, color=POS, sw=1.8))
    p.append(text(690, 420, "exit_notify()", size=11, color=POS))

    # ZOMBIE -> release_task
    p.append(arrow(580, 520, 640, 520, color=FIELD, sw=2.0))
    p.append(text(610, 505, "waitpid()", size=11.5, color=FIELD, bold=True))

    # Нижній пояснювальний блок
    p.append(fitbox(40, 640, 1100, 120,
                    ["КЛЮЧОВИЙ ПРИНЦИП РОЗДІЛЕННЯ ВІДПОВІДАЛЬНОСТІ:",
                     "• Кроки 1–3 виконує САМ ПРОЦЕС у контексті ядра (звільняє пам'ять, закриває файли, надсилає SIGCHLD).",
                     "• Крок 4 (EXIT_ZOMBIE) — стан очікування батька, коли процесу вже немає, але його дескриптор ще не знищено.",
                     "• Крок 5 виконує БАТЬКІВСЬКИЙ ПРОЦЕС через waitpid(): забирає результат і дає ядру команду остаточно стерти task_struct."],
                    size=12.5, fill="#f4f6f8", stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "lifecycle-state-machine.svg"), W, H, *p,
           title="Автомат станів життєвого циклу процесу в Linux")


# ── Фіг. 2: Конвеєр завершення процесу do_exit() ─────────────────────────────
def fig_kernel_exit_pipeline():
    W, H = 1180, 800
    p = []

    p.append(text(W / 2, 38, "Конвеєр демонтажу ресурсів у функції ядра do_exit()", size=16, color=INK, bold=True))

    STEPS = [
        ("1. PF_EXITING", "Встановлення прапорця",
         ["current->flags |= PF_EXITING",
          "Заборона створення нових потоків,",
          "блокування доставки нових сигналів"],
         POS, RED_F),
        ("2. exit_mm()", "Демонтаж пам'яті",
         ["Звільнення таблиць сторінок MMU,",
          "анулювання анонімних VMA та стеків,",
          "кадри пам'яті повертаються ядру"],
         NEG, BLUE_F),
        ("3. exit_files()", "Закриття дескрипторів",
         ["Зменшення refcount у files_struct,",
          "закриття сокетів (TCP FIN/RST),",
          "надсилання EOF у канали (pipes)"],
         NEG, BLUE_F),
        ("4. exit_fs() / sem", "Файлова система й замки",
         ["Відв'язування кореня та cwd (fs_struct),",
          "відкат операцій SysV IPC (semundo),",
          "скидання блокувань flock/fcntl"],
         AMBER_S, AMBER_F),
        ("5. forget_original_parent()", "Перепідпорядкування",
         ["Обхід усіх дочірніх процесів,",
          "перевірка субреперів у дереві предків,",
          "перепризначення сиріт на новий reaper"],
         PURP_S, PURP_F),
        ("6. exit_notify()", "Сповіщення та зомбі",
         ["Встановлення стану EXIT_ZOMBIE,",
          "відправка сигналу SIGCHLD батькові,",
          "виклик schedule() — задача вибуває з ЦП"],
         FIELD, GREEN_F),
    ]

    BOX_W = 340
    BOX_H = 150
    X_COLS = [210, 590, 970]
    Y_ROWS = [170, 410]

    for i, (title, sub, lines, stroke, fill) in enumerate(STEPS):
        col = i % 3
        row = i // 3
        cx = X_COLS[col]
        cy = Y_ROWS[row]
        x = cx - BOX_W / 2
        y = cy - BOX_H / 2

        content = [title + " — " + sub] + lines
        p.append(fitbox(x, y, BOX_W, BOX_H, content, size=12, fill=fill, stroke=stroke, sw=1.6))

    # Стрілки між кроками
    # 1 -> 2
    p.append(arrow(380, 170, 420, 170, color=INK, sw=1.8))
    # 2 -> 3
    p.append(arrow(760, 170, 800, 170, color=INK, sw=1.8))
    # 3 -> 4 (згин униз-вліво)
    p.append(arrow(970, 245, 970, 310, color=INK, sw=1.8))
    p.append(arrow(970, 310, 210, 310, color=INK, sw=1.8))
    p.append(arrow(210, 310, 210, 335, color=INK, sw=1.8))
    # 4 -> 5
    p.append(arrow(380, 410, 420, 410, color=INK, sw=1.8))
    # 5 -> 6
    p.append(arrow(760, 410, 800, 410, color=INK, sw=1.8))

    # Нижній блок: Що лишається після do_exit()
    p.append(fitbox(60, 540, 1060, 220,
                    ["ПІДСУМОК: СТАН ЗОМБІ (EXIT_ZOMBIE) ТА ЧАС ЖИТТЯ РЕСУРСІВ",
                     "",
                     "• ЗВІЛЬНЕНО ПОВНІСТЮ: фізичну пам'ять, таблиці сторінок, файлові дескриптори, мережеві сокети, каталоги.",
                     "• ЗБЕРЕЖЕНО В task_struct: номер PID, статус виходу (exit_code), лічильники витраченого часу (rusage), зв'язок із батьком.",
                     "• НАСТУПНИЙ КРОК: виклик waitpid() батьківським процесом переносить exit_code і викликає release_task().",
                     "  Лише після release_task() дескриптор task_struct звільняється через RCU, а PID повертається в пул системи."],
                    size=13, fill="#f4f6f8", stroke=LINE, sw=1.5))

    render(os.path.join(OUT, "kernel-exit-pipeline.svg"), W, H, *p,
           title="Послідовність звільнення ресурсів у do_exit()")


# ── Фіг. 3: Ланцюг субреперів та перепідпорядкування сиріт ────────────────────
def fig_reaper_hierarchy_subreaper():
    W, H = 1180, 780
    p = []

    p.append(text(W / 2, 38, "Ієрархія перепідпорядкування сиріт та механізм subreaper", size=16, color=INK, bold=True))

    # Ліва колонка: Класична модель без субрепера (усе йде в PID 1)
    p.append(text(280, 80, "Класична схема: перепідпорядкування на PID 1", size=14, color=INK, bold=True))
    p.append(fitbox(80, 110, 400, 80,
                    ["PID 1 (init / systemd)",
                     "Головний процес системи, глобальний прибирач"],
                    size=12.5, fill=GREEN_F, stroke=FIELD, sw=1.6))

    p.append(fitbox(80, 250, 400, 80,
                    ["Процес-Батько (PID 1050)",
                     "Створює дочірній процес і раптово завершується"],
                    size=12.5, fill=RED_F, stroke=POS, sw=1.6))

    p.append(fitbox(80, 400, 400, 80,
                    ["Процес-Сирота (PID 1051)",
                     "Працює у фоні; батька 1050 вже не існує"],
                    size=12.5, fill=BLUE_F, stroke=NEG, sw=1.6))

    # Стрілки лівої колонки
    p.append(arrow(280, 190, 280, 250, color=LINE, sw=1.5))
    p.append(arrow(280, 330, 280, 400, color=LINE, sw=1.5))
    p.append(line(80, 290, 40, 290, color=POS, sw=1.8))
    p.append(line(40, 290, 40, 150, color=POS, sw=1.8))
    p.append(arrow(40, 150, 80, 150, color=POS, sw=1.8))
    p.append(text(60, 220, "reparent", size=11, color=POS, anchor="middle"))

    # Права колонка: Модель із PR_SET_CHILD_SUBREAPER (systemd --user / контейнер)
    p.append(text(880, 80, "Сучасна схема: перехоплення субрепером", size=14, color=INK, bold=True))

    p.append(fitbox(680, 110, 400, 70,
                    ["PID 1 (system systemd)",
                     "Глобальний прибирач (не навантажується сиротами сесій)"],
                    size=12, fill="#f4f6f8", stroke=GREY_S, sw=1.3))

    p.append(fitbox(680, 220, 400, 90,
                    ["Субрепер (systemd --user / container runtime / tmux)",
                     "Оголосив себе через prctl(PR_SET_CHILD_SUBREAPER, 1)",
                     "Збирає всіх сиріт у межах власного дерева"],
                    size=12, fill=AMBER_F, stroke=AMBER_S, sw=1.6, bold=False))

    p.append(fitbox(680, 350, 400, 70,
                    ["Проміжний процес / воркер (PID 2400)",
                     "Створює дитину й завершується"],
                    size=12, fill=RED_F, stroke=POS, sw=1.5))

    p.append(fitbox(680, 460, 400, 70,
                    ["Дочірня сирота (PID 2401)",
                     "Перепідпорядковується найближчому субреперу"],
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.5))

    # Стрілки правої колонки
    p.append(arrow(880, 180, 880, 220, color=LINE, sw=1.4))
    p.append(arrow(880, 310, 880, 350, color=LINE, sw=1.4))
    p.append(arrow(880, 420, 880, 460, color=LINE, sw=1.4))
    p.append(line(680, 495, 630, 495, color=AMBER_S, sw=1.8))
    p.append(line(630, 495, 630, 265, color=AMBER_S, sw=1.8))
    p.append(arrow(630, 265, 680, 265, color=AMBER_S, sw=1.8))
    p.append(text(650, 380, "reparent", size=11, color=AMBER_S, anchor="middle"))

    # Блок коду та висновку внизу
    p.append(fitbox(80, 570, 1000, 170,
                    ["ЯК СУБРЕПЕР ПРИБИРАЄ СИРІТ:",
                     "",
                     "1. Сирота перепідпорядковується найближчому живому предку з прапорцем is_child_subreaper.",
                     "2. Коли сирота помирає, субрепер отримує сигнал SIGCHLD.",
                     "3. Головний цикл подій субрепера (наприклад, epoll у systemd) викликає waitpid(-1, &st, WNOHANG) у циклі.",
                     "4. Зомбі миттєво знищується, ізоляція сесії/контейнера не порушується, PID 1 не перевантажується."],
                    size=12.5, fill="#f4f6f8", stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "reaper-hierarchy-subreaper.svg"), W, H, *p,
           title="Ієрархія субреперів та перепідпорядкування сиріт")


if __name__ == "__main__":
    fig_lifecycle_state_machine()
    fig_kernel_exit_pipeline()
    fig_reaper_hierarchy_subreaper()
    print("OK: generated 3 figures in img/")
