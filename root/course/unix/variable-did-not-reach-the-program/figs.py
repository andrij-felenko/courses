# -*- coding: utf-8 -*-
"""Фігури для теми «Чому змінна не доїхала до програми» (course/unix/obolonka-y-terminal/variable-did-not-reach-the-program)."""
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

def fig_environ_memory_layout():
    """environ-memory-layout.svg: Анатомія стека процесу та розміщення змінних середовища."""
    W, H = 960, 520
    frags = []

    # Заголовок
    frags.append(text(480, 28, "Розташування аргументів та змінних середовища у пам'яті стека Linux (x86-64)", size=15, bold=True, color="#1e293b"))

    # Контейнер адресного простору стека
    frags.append(rect(40, 50, 880, 445, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))

    # Стрілка напрямку пам'яті
    frags.append(text(70, 75, "0x7FFF_FFFF_FFFF (Верхній край віртуальної пам'яті / Старші адреси)", size=11, color="#64748b", anchor="start", italic=True))
    frags.append(arrow(60, 90, 60, 465, color="#64748b", sw=1.5))
    frags.append(text(55, 280, "Стек зростає донизу (до молодших адрес)", size=10, color="#64748b", anchor="middle", italic=True))
    frags.append(text(70, 480, "Молодші адреси пам'яті (Поточний покажчик стека RSP)", size=11, color="#64748b", anchor="start", italic=True))

    # Блок 1: Рядки середовища (Environment Strings)
    frags.append(rect(140, 90, 760, 65, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(520, 112, "Блок рядків середовища: нуль-терміновані байти в пам'яті (POSIX name=value\\0)", size=12, bold=True, color=GREEN_S))
    frags.append(text(520, 138, "\"PATH=/usr/bin:/bin\\0\"  |  \"USER=alex\\0\"  |  \"HOME=/home/alex\\0\"  |  \"DB_HOST=127.0.0.1\\0\"", size=11, color="#1e293b"))

    # Блок 2: Рядки аргументів (Argument Strings)
    frags.append(rect(140, 165, 760, 55, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(520, 185, "Блок рядків аргументів командного рядка (argv strings)", size=12, bold=True, color=BLUE_S))
    frags.append(text(520, 207, "\"./migrate_app\\0\"  |  \"--config=prod.yaml\\0\"  |  \"--verbose\\0\"", size=11, color="#1e293b"))

    # Блок 3: Допоміжний вектор Auxiliary Vector (auxv)
    frags.append(rect(140, 230, 760, 50, fill=GRAY_F, stroke=GRAY_S, sw=1.2, rx=6))
    frags.append(text(520, 250, "Допоміжний вектор ядра: Elf64_auxv_t auxv[] (AT_SYSINFO_EHDR, AT_RANDOM, AT_NULL)", size=11, bold=True, color="#475569"))
    frags.append(text(520, 269, "Передає параметри vDSO, ентропію канарок стека та точки входу динамічного лінкера", size=10, color="#64748b"))

    # Блок 4: Таблиця покажчиків envp (Покажчики на рядки середовища)
    frags.append(rect(140, 290, 760, 70, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(520, 310, "Таблиця покажчиків середовища: char *envp[] (закінчується покажчиком NULL)", size=12, bold=True, color=GREEN_S))
    frags.append(text(520, 340, "[ envp[0] ] ──> \"PATH=...\"  |  [ envp[1] ] ──> \"USER=...\"  |  [ envp[2] ] ──> \"HOME=...\"  |  [ NULL ]", size=10.5, color="#1e293b"))

    # Блок 5: Таблиця покажчиків argv (Покажчики на аргументи)
    frags.append(rect(140, 370, 760, 60, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(520, 390, "Таблиця покажчиків аргументів: char *argv[] (закінчується покажчиком NULL)", size=12, bold=True, color=BLUE_S))
    frags.append(text(520, 416, "[ argv[0] ] ──> \"./migrate_app\"  |  [ argv[1] ] ──> \"--config=...\"  |  [ argv[2] ] ──> \"--verbose\"  |  [ NULL ]", size=10.5, color="#1e293b"))

    # Блок 6: Лічильник argc
    frags.append(rect(140, 440, 760, 40, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=6))
    frags.append(text(520, 465, "Кількість аргументів: int argc (на вершині стека під час передачі керування в _start)", size=11, bold=True, color=AMBER_S))

    # Стрілка глобального покажчика environ
    frags.append(rect(730, 320, 160, 26, fill="#ffffff", stroke="#0f766e", sw=1.2, rx=4))
    frags.append(text(810, 337, "extern char **environ", size=10, bold=True, color="#0f766e"))

    render(os.path.join(IMG, "environ-memory-layout.svg"), W, H, *frags)

def fig_shell_symbol_table_export_fork_exec():
    """shell-symbol-table-export-fork-exec.svg: Життєвий цикл змінної від Bash var_table через fork до execve."""
    W, H = 960, 480
    frags = []

    frags.append(text(480, 26, "Фільтрація змінних: чому локальні змінні оболонки не потрапляють до execve()", size=15, bold=True, color="#1e293b"))

    # Фаза 1: Внутрішня таблиця символів Bash
    frags.append(rect(30, 50, 270, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b_p1, _, _ = textbox(165, 75, "1. Таблиця символів Bash (var_table)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_p1)

    # Запис 1: Експортована
    frags.append(rect(45, 110, 240, 70, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=6))
    frags.append(text(165, 130, "export PATH=\"/usr/bin\"", size=10.5, bold=True, color=GREEN_S))
    frags.append(text(165, 150, "flags: att_exported (0x01)", size=9.5, color="#15803d"))
    frags.append(text(165, 168, "Статус: ЕКСПОРТОВАНА", size=9.5, bold=True, color="#15803d"))

    # Запис 2: Локальна змінна
    frags.append(rect(45, 195, 240, 70, fill=RED_F, stroke=RED_S, sw=1.2, rx=6))
    frags.append(text(165, 215, "DB_PASS=\"secret123\"", size=10.5, bold=True, color=RED_S))
    frags.append(text(165, 235, "flags: 0x00 (лише пам'ять Bash)", size=9.5, color="#b91c1c"))
    frags.append(text(165, 253, "Статус: ЛОКАЛЬНА ОБОЛОНКИ", size=9.5, bold=True, color="#b91c1c"))

    # Запис 3: Ще одна експортована
    frags.append(rect(45, 280, 240, 70, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=6))
    frags.append(text(165, 300, "export USER=\"alex\"", size=10.5, bold=True, color=GREEN_S))
    frags.append(text(165, 320, "flags: att_exported (0x01)", size=9.5, color="#15803d"))
    frags.append(text(165, 338, "Статус: ЕКСПОРТОВАНА", size=9.5, bold=True, color="#15803d"))

    frags.append(text(165, 395, "Оболонка тримає змінні у власній", size=10, color="#64748b"))
    frags.append(text(165, 412, "структурі даних процесу (хеш-таблиці)", size=10, color="#64748b"))

    # Стрілка fork
    frags.append(arrow(300, 255, 350, 255, color=BLUE_S, sw=2))
    frags.append(text(325, 245, "fork()", size=11, bold=True, color=BLUE_S))

    # Фаза 2: Підготовка дочірнього процесу
    frags.append(rect(360, 50, 270, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b_p2, _, _ = textbox(495, 75, "2. Підготовка дочірнього процесу", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_p2)

    frags.append(rect(375, 110, 240, 155, fill="#ffffff", stroke=AMBER_S, sw=1.2, rx=6))
    frags.append(text(495, 130, "Серіалізація перед execve():", size=10.5, bold=True, color=AMBER_S))
    frags.append(text(495, 155, "Цикл по всіх змінних Bash:", size=10, color="#334155"))
    frags.append(text(495, 178, "if (var->flags & att_exported)", size=9.5, bold=True, color="#0f766e"))
    frags.append(text(495, 200, "  додати в масив envp[]", size=9.5, color="#15803d"))
    frags.append(text(495, 222, "else", size=9.5, bold=True, color="#b91c1c"))
    frags.append(text(495, 244, "  ПРОПУСТИТИ (DB_PASS відкинуто!)", size=9.5, bold=True, color="#b91c1c"))

    # Сформований масив envp
    frags.append(rect(375, 280, 240, 100, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=6))
    frags.append(text(495, 302, "Сформований масив char **envp:", size=10, bold=True, color=GREEN_S))
    frags.append(text(495, 324, "envp[0] = \"PATH=/usr/bin\"", size=9.5, color="#1e293b"))
    frags.append(text(495, 344, "envp[1] = \"USER=alex\"", size=9.5, color="#1e293b"))
    frags.append(text(495, 364, "envp[2] = NULL", size=9.5, color="#1e293b"))

    frags.append(text(495, 415, "Виклик execve(шлях, argv, envp)", size=10.5, bold=True, color=PURPLE_S))
    frags.append(text(495, 435, "Точка неповернення ядра", size=9.5, color="#64748b"))

    # Стрілка execve
    frags.append(arrow(630, 255, 680, 255, color=PURPLE_S, sw=2))
    frags.append(text(655, 245, "execve()", size=11, bold=True, color=PURPLE_S))

    # Фаза 3: Нова програма
    frags.append(rect(690, 50, 240, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b_p3, _, _ = textbox(810, 75, "3. Запущена програма (./app)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_p3)

    frags.append(rect(705, 110, 210, 160, fill="#ffffff", stroke=PURPLE_S, sw=1.2, rx=6))
    frags.append(text(810, 130, "Адресний простір програми:", size=10.5, bold=True, color=PURPLE_S))
    frags.append(text(810, 155, "Пам'ять Bash повністю стерта", size=9.5, color="#475569"))
    frags.append(text(810, 180, "getenv(\"PATH\") ──> \"/usr/bin\"", size=9.5, color="#15803d"))
    frags.append(text(810, 205, "getenv(\"USER\") ──> \"alex\"", size=9.5, color="#15803d"))
    frags.append(text(810, 235, "getenv(\"DB_PASS\") ──> NULL!", size=10, bold=True, color="#dc2626"))

    frags.append(rect(705, 290, 210, 150, fill=RED_F, stroke=RED_S, sw=1.2, rx=6))
    frags.append(text(810, 312, "Результат:", size=11, bold=True, color=RED_S))
    frags.append(text(810, 340, "Змінна DB_PASS не була", size=10, color="#b91c1c"))
    frags.append(text(810, 360, "передана у масиві envp.", size=10, color="#b91c1c"))
    frags.append(text(810, 390, "Програма не має до неї", size=10, color="#b91c1c"))
    frags.append(text(810, 410, "жодного доступу!", size=10, bold=True, color="#b91c1c"))

    render(os.path.join(IMG, "shell-symbol-table-export-fork-exec.svg"), W, H, *frags)

def fig_pipeline_subshell_isolation():
    """pipeline-subshell-isolation.svg: Чому змінні у конвеєрі cmd | while read line не повертаються до батька."""
    W, H = 960, 500
    frags = []

    frags.append(text(480, 26, "Ізоляція пам'яті конвеєра: чому cat file | while read ... не змінює батьківську змінну", size=15, bold=True, color="#1e293b"))

    # Батьківський процес (Shell PID 1000)
    frags.append(rect(30, 55, 900, 105, fill="#f8fafc", stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(180, 80, "Батьківська оболонка (PID 1000)", size=12, bold=True, color=BLUE_S))
    frags.append(text(180, 102, "Адресний простір батька: count = 0", size=11, bold=True, color="#1e293b"))
    frags.append(text(180, 125, "Команда: count=0; cat data.txt | while read l; do count=$((count+1)); done", size=10, color="#64748b"))

    frags.append(rect(580, 72, 330, 70, fill=AMBER_F, stroke=AMBER_S, sw=1.2, rx=6))
    frags.append(text(745, 92, "Батько створює канал pipe() та викликає", size=10, color="#92400e"))
    frags.append(text(745, 110, "fork() ДВІЧІ для лівої та правої частин,", size=10, bold=True, color="#92400e"))
    frags.append(text(745, 128, "після чого чекає через waitpid()", size=10, color="#92400e"))

    # Стрілки fork()
    frags.append(arrow(260, 160, 260, 205, color=BLUE_S, sw=1.8))
    frags.append(text(205, 185, "fork() #1", size=10.5, bold=True, color=BLUE_S))

    frags.append(arrow(680, 160, 680, 205, color=BLUE_S, sw=1.8))
    frags.append(text(735, 185, "fork() #2 (Subshell)", size=10.5, bold=True, color=BLUE_S))

    # Лівий дочірній процес: cat data.txt
    frags.append(rect(30, 210, 420, 160, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    frags.append(text(240, 235, "Лівий процес: cat data.txt (PID 1001)", size=11.5, bold=True, color="#334155"))
    frags.append(text(240, 260, "stdout перенаправлено у дескриптор запису каналу", size=10, color="#64748b"))
    frags.append(text(240, 285, "Зчитує рядки файлу та записує їх у pipe", size=10, color="#334155"))
    frags.append(text(240, 315, "Завершує роботу: exit(0) -> закриває канал", size=10, color="#15803d"))
    frags.append(text(240, 345, "Стан змінної count: не використовує", size=9.5, italic=True, color="#64748b"))

    # Неіменований канал зв'язку
    frags.append(rect(460, 260, 40, 45, fill=AMBER_F, stroke=AMBER_S, sw=1.2, rx=4))
    frags.append(text(480, 287, "PIPE", size=9.5, bold=True, color=AMBER_S))
    frags.append(arrow(430, 282, 460, 282, color=AMBER_S, sw=1.5))
    frags.append(arrow(500, 282, 530, 282, color=AMBER_S, sw=1.5))

    # Правий дочірній процес: Subshell з циклом while
    frags.append(rect(510, 210, 420, 160, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(720, 235, "Правий підпроцес: Subshell (PID 1002)", size=11.5, bold=True, color=RED_S))
    frags.append(text(720, 260, "stdin підключено до дескриптора читання каналу", size=10, color="#64748b"))
    frags.append(text(720, 285, "Отримує копію пам'яті батька (COW): count = 0", size=10, color="#334155"))
    frags.append(text(720, 310, "Цикл while інкрементує count у СВОЇЙ пам'яті: count = 100", size=10, bold=True, color="#b91c1c"))
    frags.append(text(720, 335, "EOF на каналі ──> вихід із циклу ──> exit(0)", size=10, bold=True, color="#b91c1c"))
    frags.append(text(720, 355, "Уся віртуальна пам'ять PID 1002 знищується ядром!", size=9.5, bold=True, color="#b91c1c"))

    # Підсумок у батьківському процесі
    frags.append(rect(30, 395, 900, 85, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    frags.append(text(480, 420, "Фінал у батьківській оболонці (PID 1000) після завершення конвеєра:", size=11.5, bold=True, color="#1e293b"))
    frags.append(text(480, 445, "echo \"$count\" ──> друкує 0! (Батьківська пам'ять не зазнала жодних змін)", size=12, bold=True, color=RED_S))
    frags.append(text(480, 468, "Альтернатива: shopt -s lastpipe (виконання в поточному процесі) або while ... done < <(cat data.txt)", size=10.5, color="#15803d"))

    render(os.path.join(IMG, "pipeline-subshell-isolation.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_environ_memory_layout()
    fig_shell_symbol_table_export_fork_exec()
    fig_pipeline_subshell_isolation()
    print("All figures generated successfully.")
