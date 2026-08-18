# -*- coding: utf-8 -*-
"""Фігури для теми «Чому саме два виклики, а не один» (guide/unix/protses/fork-exec-why-two)."""
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

def fig_monolithic_vs_composable():
    """monolithic-vs-composable.svg: Монолітний виклик запуску проти ортогональної композиції fork + exec."""
    W, H = 960, 490
    frags = []

    # Заголовок
    frags.append(text(480, 32, "Дві філософії створення процесу: монолітний API проти ортогонального вікна", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Монолітний підхід
    frags.append(rect(30, 60, 430, 405, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_lh, _, _ = textbox(245, 90, "Монолітний підхід: один універсальний виклик", size=12, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_lh)

    b_call, _, _ = textbox(245, 145, "CreateProcess() / spawn(файл, аргументи, оточення, ...)", size=10.5, bold=True, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_call)

    # Величезна структура параметрів
    frags.append(rect(50, 180, 390, 165, fill="#ffffff", stroke=RED_S, sw=1.2, rx=6))
    frags.append(text(245, 202, "Величезна структура конфігурації (STARTUPINFOEX / алокації)", size=11, bold=True, color=RED_S))
    
    params = [
        "• Масив перепризначення дескрипторів (std_in, std_out, err)",
        "• Прапорці успадкування дескрипторів та сокетів",
        "• Ідентифікатори прав (UID/GID, маркери безпеки)",
        "• Маска блокування сигналів і пріоритети планування",
        "• Робочий каталог, ліміти ресурсів, групи процесів",
        "• Нова властивість ядра? → Потрібно оновлювати весь API!"
    ]
    for i, p in enumerate(params):
        frags.append(text(65, 226 + i * 20, p, size=10, color="#334155", anchor="start"))

    frags.append(line(245, 345, 245, 370, color=RED_S, sw=1.5))
    b_kernel, _, _ = textbox(245, 410, "Ядро: монструозний парсер сотень прапорців\n(комбінаторний вибух та залежності в одному виклику)", size=10.5, fill=RED_F, stroke=RED_S)
    frags.append(b_kernel)

    # Права колонка: Ортогональна композиція
    frags.append(rect(500, 60, 430, 405, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_rh, _, _ = textbox(715, 90, "Ортогональна модель Unix: fork + вікно + exec", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_rh)

    b_fork, _, _ = textbox(715, 140, "1. fork(): народжується точна копія процесу", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_fork)

    frags.append(line(715, 162, 715, 185, color=GREEN_S, sw=1.5))

    # Вікно налаштувань
    frags.append(rect(520, 185, 390, 160, fill="#ffffff", stroke=GREEN_S, sw=1.2, rx=6))
    frags.append(text(715, 205, "2. Вікно налаштування: виконання звичайних системних викликів", size=11, bold=True, color=GREEN_S))
    
    actions = [
        "• dup2() / close() → перенаправлення потоків та каналів",
        "• chdir() → перехід у потрібний каталог",
        "• setuid() / capset() → скидання зайвих привілеїв",
        "• sigprocmask() → налаштування маски сигналів",
        "• unshare() / setns() → перехід у простори імен (namespaces)",
        "• Нова властивість ядра? → Вже доступна, API запуску не міняється!"
    ]
    for i, a in enumerate(actions):
        frags.append(text(535, 228 + i * 19, a, size=10, color="#334155", anchor="start"))

    frags.append(line(715, 345, 715, 370, color=GREEN_S, sw=1.5))
    b_exec, _, _ = textbox(715, 410, "3. execve(): заміна образу пам'яті новою програмою\n(всі налаштовані властивості ядра безшовно успадковано)", size=10.5, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_exec)

    render(os.path.join(IMG, "monolithic-vs-composable.svg"), W, H, *frags)

def fig_the_setup_window():
    """the-setup-window.svg: Анатомія вікна між fork та execve."""
    W, H = 960, 450
    frags = []

    frags.append(text(480, 32, "Хронологія життя дитини у вікні між fork() та execve()", size=16, bold=True, color="#1e293b"))

    # Батьківський процес
    b_parent, _, _ = textbox(130, 80, "Батьківський процес (Shell / Supervisor)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_parent)

    # Лінія fork
    frags.append(line(130, 105, 130, 150, color=BLUE_S, sw=2))
    frags.append(text(138, 130, "fork() повертає child_pid", size=10, color=BLUE_S, anchor="start"))

    # Стрілка очікування батька
    frags.append(line(130, 150, 130, 385, color="#94a3b8", sw=1.5, dash="4,4"))
    b_wait, _, _ = textbox(130, 400, "waitpid(child_pid) очікує завершення", size=10.5, fill="#f8fafc", stroke="#94a3b8")
    frags.append(b_wait)

    # Початок дитини
    frags.append(line(130, 150, 280, 150, color=GREEN_S, sw=2))
    b_child_start, _, _ = textbox(360, 150, "fork() == 0 (дитина)\nТочна копія пам'яті й дескрипторів", size=10.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_child_start)

    # Велика рамка «ВІКНО НАЛАШТУВАННЯ»
    frags.append(rect(235, 195, 520, 175, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(495, 218, "ВІКНО ВИКОНАННЯ ДИТИНИ (налаштування ядра під себе)", size=11.5, bold=True, color=AMBER_S))

    steps = [
        ("1. Дескриптори", "dup2(pipe_fd, STDOUT_FILENO); close(unused_fds);"),
        ("2. Оточення й робочий стан", "chdir(\"/var/run/app\"); umask(0027); setrlimit(RLIMIT_NOFILE, &lim);"),
        ("3. Сигнали та групи", "setpgid(0, 0); sigprocmask(SIG_SETMASK, &mask, NULL);"),
        ("4. Безпека та ізоляція", "unshare(CLONE_NEWPID); setgid(1000); setuid(1000); seccomp(...);")
    ]

    for i, (title, code_str) in enumerate(steps):
        y = 242 + i * 30
        frags.append(text(250, y, title, size=10.5, bold=True, color="#1e293b", anchor="start"))
        frags.append(text(410, y, code_str, size=10, color="#0f766e", anchor="start"))

    # З'єднання до вікна
    frags.append(line(360, 175, 360, 195, color=GREEN_S, sw=1.5))

    # Стрілка з вікна до execve
    frags.append(line(755, 282, 785, 282, color=PURPLE_S, sw=2))
    
    # execve
    b_exec, _, _ = textbox(860, 282, "execve(path, argv, envp)\nТОЧКА НЕПОВЕРНЕННЯ\nОбраз пам'яті замінено", size=10.5, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_exec)

    frags.append(line(860, 325, 860, 375, color=PURPLE_S, sw=2))
    b_new_prog, _, _ = textbox(860, 395, "Виконання нової програми: _start() -> main()", size=10.5, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_new_prog)

    render(os.path.join(IMG, "the-setup-window.svg"), W, H, *frags)

def fig_spawn_fast_path_cloneline():
    """spawn-fast-path-cloneline.svg: Порівняння механізмів виділення пам'яті fork+exec проти оптимізованого posix_spawn."""
    W, H = 960, 460
    frags = []

    frags.append(text(480, 32, "Ціна створення процесу: fork() (COW) проти оптимізованого posix_spawn()", size=16, bold=True, color="#1e293b"))

    # Ліва половина: fork + exec
    frags.append(rect(30, 60, 435, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_f_head, _, _ = textbox(247, 90, "Стандартний fork() + execve() (COW)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_f_head)

    f_blocks = [
        (247, 140, "1. Батьківський процес (наприклад, 32 ГБ RSS)\nТаблиці сторінок займають ~64 МБ пам'яті.", GRAY_F, "#64748b"),
        (247, 210, "2. fork(): Дублювання таблиць сторінок\nЯдро копіює всі PTE, маркує Read-Only (COW).\nВитрачається CPU-час та пам'ять ядра.", RED_F, RED_S),
        (247, 285, "3. Вікно дитини: мінімальний запис\nКожен запис викликає Page Fault і копіювання 4 КіБ.", AMBER_F, AMBER_S),
        (247, 355, "4. execve(): Знищення таблиць сторінок\nУсі скопійовані таблиці сторінок викидаються!\nЯдро будує чистий адресний простір з нуля.", PURPLE_F, PURPLE_S)
    ]

    for cx, cy, text_str, bg, st in f_blocks:
        b, _, _ = textbox(cx, cy, text_str, size=10, fill=bg, stroke=st, pad=6)
        frags.append(b)

    # Права половина: posix_spawn
    frags.append(rect(495, 60, 435, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_s_head, _, _ = textbox(712, 90, "Оптимізований posix_spawn() (Linux / glibc)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_s_head)

    s_blocks = [
        (712, 140, "1. Батьківський процес (32 ГБ RSS)\nТаблиці сторінок залишаються недоторканими.", GRAY_F, "#64748b"),
        (712, 210, "2. clone(CLONE_VM | CLONE_VFORK)\nБатько чекає, дитина ділить пам'ять батька.\nТаблиці сторінок НЕ дублюються взагалі!", GREEN_F, GREEN_S),
        (712, 285, "3. Виконання дій з окремого стека\nglibc виділяє маленький тимчасовий стек (64 КіБ).\nВиконуються file_actions без псування пам'яті батька.", TEAL_F, TEAL_S),
        (712, 355, "4. execve(): Новий процес оживає\nЯдро завантажує образ нової програми.\nБатько розблоковується. Нуль копіювань PTE!", BLUE_F, BLUE_S)
    ]

    for cx, cy, text_str, bg, st in s_blocks:
        b, _, _ = textbox(cx, cy, text_str, size=10, fill=bg, stroke=st, pad=6)
        frags.append(b)

    render(os.path.join(IMG, "spawn-fast-path-cloneline.svg"), W, H, *frags)

def main():
    fig_monolithic_vs_composable()
    fig_the_setup_window()
    fig_spawn_fast_path_cloneline()
    print("Всі фігури згенеровано успішно.")

if __name__ == "__main__":
    main()
