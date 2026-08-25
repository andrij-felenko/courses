# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY_S  = "#c8ced6"
BLUE_F  = "#eef3fb"
BLUE_S  = "#2457d6"
RED_F   = "#fdeeec"
RED_S   = "#c0392b"
GREEN_F = "#eef7f0"
GREEN_S = "#27ae60"
AMBER_F = "#fef9e7"
AMBER_S = "#d4ac0d"
PURP_F  = "#f5eef8"
PURP_S  = "#8e44ad"

# ── 1. Порівняння контексту виконання: Термінал vs Служба systemd ─────────────
def fig_terminal_vs_service_execution_context():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Контекст виконання процесу: Інтерактивний термінал проти фонової служби systemd", size=15, color=INK, bold=True))

    # Ліва колонка: Термінальний сеанс
    p.append(rect(30, 50, 470, 440, fill="#fcfdfe", stroke=BLUE_S, sw=1.8, rx=8))
    p.append(text(265, 78, "Інтерактивний сеанс (Bash / Zsh у TTY)", size=14, color=BLUE_S, bold=True))

    t_boxes = [
        ("1. Змінні оточення (envp)",
         ["• Повний набір (80+ змінних з ~/.bashrc)",
          "• $PATH: містить ~/.cargo/bin, venv, nvm",
          "• $HOME, $USER, $DISPLAY, $XDG_RUNTIME_DIR"],
         BLUE_F, BLUE_S, 50, 98, 430, 80),

        ("2. Робочий каталог (CWD)",
         ["• task_struct->fs->pwd = поточна тека проєкту",
          "• Відносні шляхи (./config.yaml) знаходять файл",
          "• Права запису у поточний каталог користувача"],
         GREEN_F, GREEN_S, 50, 192, 430, 80),

        ("3. Стандартні потоки вводу / виводу",
         ["• FDs 0, 1, 2 прив'язані до TTY (/dev/pts/X)",
          "• isatty(0) == 1 (доступний ввід пароля)",
          "• stdout: рядкова буферизація (_IOLBF, скидання по \\n)"],
         AMBER_F, AMBER_S, 50, 286, 430, 80),

        ("4. Привілеї та обмеження",
         ["• Користувач UID 1000 (повний доступ до свого $HOME)",
          "• Загальний простір імен /tmp разом із десктопом",
          "• Дефолтні ліміти сеансу (дескриптори, пам'ять)"],
         PURP_F, PURP_S, 50, 380, 430, 80),
    ]

    for title, lines, fill_c, stroke_c, bx, by, bw, bh in t_boxes:
        p.append(fitbox(bx, by, bw, bh, [title] + lines, size=11, fill=fill_c, stroke=stroke_c, sw=1.2))

    # Права колонка: Фонова служба systemd
    p.append(rect(540, 50, 470, 440, fill="#fffbfb", stroke=RED_S, sw=1.8, rx=8))
    p.append(text(775, 78, "Фонова служба (systemd PID 1)", size=14, color=RED_S, bold=True))

    s_boxes = [
        ("1. Змінні оточення (envp)",
         ["• Стерильне середовище (немає .bashrc)",
          "• Мінімальний $PATH (/usr/bin:/bin)",
          "• $HOME, $USER, $DISPLAY ВІДСУТНІ"],
         RED_F, RED_S, 560, 98, 430, 80),

        ("2. Робочий каталог (CWD)",
         ["• task_struct->fs->pwd = / (корінь)",
          "• Відносні шляхи шукають /config.yaml -> ENOENT",
          "• Потрібна директива WorkingDirectory="],
         RED_F, RED_S, 560, 192, 430, 80),

        ("3. Стандартні потоки вводу / виводу",
         ["• FD 0 -> /dev/null, FDs 1, 2 -> journald socket",
          "• isatty(0) == 0 (інтерактивні запити зависають)",
          "• stdout: блокова буферизація (_IOFBF, 4096 байтів)"],
         RED_F, RED_S, 560, 286, 430, 80),

        ("4. Привілеї та пісочниця",
         ["• DynamicUser= / User=app (немає доступу до /home)",
          "• PrivateTmp=yes (ізольований простір імен /tmp)",
          "• ProtectSystem=strict, жорсткі cgroup-ліміти"],
         RED_F, RED_S, 560, 380, 430, 80),
    ]

    for title, lines, fill_c, stroke_c, bx, by, bw, bh in s_boxes:
        p.append(fitbox(bx, by, bw, bh, [title] + lines, size=11, fill=fill_c, stroke=stroke_c, sw=1.2))

    render(os.path.join(OUT, "terminal-vs-service-execution-context.svg"), W, H, *p)


# ── 2. Фізика буферизації stdio: TTY проти Пайпа/Сокета ──────────────────────
def fig_stdio_buffering_tty_vs_pipe():
    W, H = 1000, 430
    p = []

    p.append(text(W / 2, 28, "Режими буферизації стандартної бібліотеки C (glibc stdio)", size=15, color=INK, bold=True))

    # Ліва половина: Термінал (isatty == 1)
    p.append(rect(30, 55, 455, 345, fill=GREEN_F, stroke=GREEN_S, sw=1.6, rx=8))
    p.append(text(257, 85, "Термінал (isatty(1) == 1): _IOLBF", size=13.5, color=GREEN_S, bold=True))
    p.append(text(257, 107, "Рядкова буферизація (Line Buffered)", size=11, color=MUTED, italic=True))

    p.append(fitbox(50, 125, 415, 60,
                    ["printf(\"Starting server...\\n\");",
                     "Зустрінуто символ перенесення рядка '\\n'"],
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    p.append(arrow(257, 190, 257, 215, color=GREEN_S, sw=2.0))

    p.append(fitbox(50, 220, 415, 65,
                    ["glibc stdio негайно виконує системний виклик:",
                     "write(1, \"Starting server...\\n\", 19)",
                     "Буфер очищається після кожного рядка"],
                    size=11, fill="#ffffff", stroke=GREEN_S, sw=1.2))

    p.append(arrow(257, 290, 257, 315, color=GREEN_S, sw=2.0))

    p.append(fitbox(50, 320, 415, 60,
                    ["Результат: Рядок миттєво з'являється",
                     "на екрані користувача в емуляторі термінала"],
                    size=11, fill=GREEN_F, stroke=GREEN_S, sw=1.4))

    # Права половина: Служба (isatty == 0)
    p.append(rect(515, 55, 455, 345, fill=RED_F, stroke=RED_S, sw=1.6, rx=8))
    p.append(text(742, 85, "Служба systemd (isatty(1) == 0): _IOFBF", size=13.5, color=RED_S, bold=True))
    p.append(text(742, 107, "Повна блокова буферизація (Block Buffered, 4096 байтів)", size=11, color=MUTED, italic=True))

    p.append(fitbox(535, 125, 415, 60,
                    ["printf(\"Starting server...\\n\");",
                     "Символ '\\n' ігнорується, байти осідають у буфері"],
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    p.append(arrow(742, 190, 742, 215, color=RED_S, sw=2.0))

    p.append(fitbox(535, 220, 415, 65,
                    ["glibc НЕ робить системний виклик write(1, ...)",
                     "Повідомлення затримуються в пам'яті процесу,",
                     "доки обсяг даних не досягне 4096 байтів"],
                    size=11, fill="#ffffff", stroke=RED_S, sw=1.2))

    p.append(arrow(742, 290, 742, 315, color=RED_S, sw=2.0))

    p.append(fitbox(535, 320, 415, 60,
                    ["Пастка: якщо процес падає (SIGSEGV/OOM/abort),",
                     "нескинуті логи втрачаються назавжди без запису в journald"],
                    size=11, fill=RED_F, stroke=RED_S, sw=1.4))

    render(os.path.join(OUT, "stdio-buffering-tty-vs-pipe.svg"), W, H, *p)


# ── 3. Чотири шари ізоляції та пісочниці systemd ──────────────────────────────
def fig_systemd_isolation_layers():
    W, H = 1060, 460
    p = []

    p.append(text(W / 2, 28, "Чотири концентричні шари ізоляції та обмежень служби systemd", size=15, color=INK, bold=True))

    layers = [
        ("1. Ідентичність та облікові записи",
         ["User=, Group=",
          "DynamicUser=yes",
          "SupplementaryGroups=",
          "UID/GID з пулу 61184..65519",
          "Повна втрата доступу до /home/user"],
         BLUE_F, BLUE_S, 35, 65, 230, 310),

        ("2. Простори назв файлової системи",
         ["PrivateTmp=yes (ізольований /tmp)",
          "ProtectSystem=strict (/usr, /etc - RO)",
          "ProtectHome=yes (/home недоступний)",
          "ReadOnlyPaths=, ReadWritePaths=",
          "Захист від несанкціонованого запису"],
         GREEN_F, GREEN_S, 285, 65, 235, 310),

        ("3. Ресурсні обмеження та cgroups",
         ["LimitNOFILE=65535 (дескриптори)",
          "LimitNPROC= (кількість потоків)",
          "MemoryMax= (жорсткий OOM-поріг)",
          "CPUQuota= (ліміт процесорного часу)",
          "TasksMax= (захист від fork-бомб)"],
         AMBER_F, AMBER_S, 540, 65, 235, 310),

        ("4. Фільтрація викликів та привілеїв",
         ["NoNewPrivileges=yes (блокування SUID)",
          "CapabilityBoundingSet= (зняття CAP_*)",
          "SystemCallFilter=@system-service",
          "ProtectKernelTunables=yes (/proc, /sys)",
          "RestrictAddressFamilies=AF_UNIX AF_INET"],
         PURP_F, PURP_S, 795, 65, 230, 310),
    ]

    for title, lines, fill_c, stroke_c, bx, by, bw, bh in layers:
        p.append(fitbox(bx, by, bw, bh, [title] + lines, size=11, fill=fill_c, stroke=stroke_c, sw=1.4))

    # Стрілки потоку ізоляції
    p.append(arrow(265, 220, 285, 220, color=INK, sw=2.0))
    p.append(arrow(520, 220, 540, 220, color=INK, sw=2.0))
    p.append(arrow(775, 220, 795, 220, color=INK, sw=2.0))

    # Нижня інформаційна плашка
    p.append(rect(35, 390, 990, 50, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(530, 412, "Ядро Linux застосовує всі конфігурації пісочниці під час fork() перед виконанням execve().", size=11.5, color=INK, bold=True))
    p.append(text(530, 428, "Будь-яка невідповідність коду вимогам пісочниці спричиняє негайну помилку EPERM, EACCES або EROFS.", size=10.5, color=MUTED))

    render(os.path.join(OUT, "systemd-isolation-layers.svg"), W, H, *p)


if __name__ == "__main__":
    fig_terminal_vs_service_execution_context()
    fig_stdio_buffering_tty_vs_pipe()
    fig_systemd_isolation_layers()
    print("All figures generated successfully.")
