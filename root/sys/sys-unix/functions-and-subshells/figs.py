import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_subshell_fork_cow(img_dir):
    w, h = 760, 470
    frags = []

    frags.append(text(w / 2, 25, "Ізоляція адресного простору та спільні дескриптори при створенні підоболонки", size=15, bold=True))

    # Parent shell block
    frags.append(rect(30, 55, 335, 385, fill="#f8fafc", stroke="#334155", sw=1.5))
    frags.append(text(197, 80, "Батьківська оболонка (PID 1042)", size=14, color="#1e293b", bold=True))
    frags.append(line(45, 92, 350, 92, color="#94a3b8", sw=1))

    # Parent memory
    frags.append(rect(45, 105, 305, 145, fill="#eff6ff", stroke="#3b82f6", sw=1.2))
    frags.append(text(197, 125, "Віртуальна пам'ять (Простір користувача)", size=12, color="#1d4ed8", bold=True))
    p_mem = [
        "Змінні: count=0, status=\"INIT\"",
        "Функції: log_msg(), worker()",
        "Каталог (CWD): /home/user/app",
        "Стек викликів: main"
    ]
    frags.append(mtext(60, 148, p_mem, size=11, color="#1e3a8a", anchor="start", lh=1.4))

    # Parent FD table
    frags.append(rect(45, 265, 305, 155, fill="#fef3c7", stroke="#d97706", sw=1.2))
    frags.append(text(197, 285, "Таблиця дескрипторів процесу", size=12, color="#b45309", bold=True))
    p_fds = [
        "FD 0 (stdin)  ──► Terminal PTY (offset 0)",
        "FD 1 (stdout) ──► Pipe Write End (ref=2)",
        "FD 2 (stderr) ──► Terminal PTY",
        "FD 3 (app.log)──► File Description #42"
    ]
    frags.append(mtext(60, 308, p_fds, size=11, color="#78350f", anchor="start", lh=1.4))

    # Fork arrow
    frags.append(line(365, 235, 395, 235, color=POS, sw=2))
    frags.append(arrow(365, 235, 393, 235, color=POS, sw=2))
    frags.append(text(380, 222, "fork()", size=11, color=POS, bold=True))

    # Subshell block
    frags.append(rect(395, 55, 335, 385, fill="#fffbeb", stroke="#b45309", sw=1.5))
    frags.append(text(562, 80, "Підоболонка Subshell (PID 1043)", size=14, color="#92400e", bold=True))
    frags.append(line(410, 92, 715, 92, color="#fcd34d", sw=1))

    # Subshell memory
    frags.append(rect(410, 105, 305, 145, fill="#fef2f2", stroke="#ef4444", sw=1.2))
    frags.append(text(562, 125, "Копія сторінок COW (Private Modify)", size=12, color="#b91c1c", bold=True))
    s_mem = [
        "Модифікація: count=42 (лише у PID 1043!)",
        "Зміна CWD: cd /tmp (лише у PID 1043)",
        "$$ = 1042 (незмінний PID предка)",
        "BASHPID = 1043 (реальний PID у ядрі)"
    ]
    frags.append(mtext(425, 148, s_mem, size=11, color="#7f1d1d", anchor="start", lh=1.4))

    # Subshell FD table
    frags.append(rect(410, 265, 305, 155, fill="#fef3c7", stroke="#d97706", sw=1.2))
    frags.append(text(562, 285, "Скопійована таблиця FD", size=12, color="#b45309", bold=True))
    s_fds = [
        "FD 0 (stdin)  ──► Terminal PTY (той самий)",
        "FD 1 (stdout) ──► Pipe Write End (той самий)",
        "FD 2 (stderr) ──► Terminal PTY (той самий)",
        "FD 3 (app.log)──► File Description #42 (спільний offset!)"
    ]
    frags.append(mtext(425, 308, s_fds, size=11, color="#78350f", anchor="start", lh=1.4))

    path = os.path.join(img_dir, "subshell-fork-cow.svg")
    svg_render(path, w, h, *frags)

def render_dynamic_scoping(img_dir):
    w, h = 760, 480
    frags = []

    frags.append(text(w / 2, 25, "Стек викликів та динамічна область видимості (Dynamic Scope) у Bash", size=15, bold=True))

    # Frame 1: main
    frags.append(rect(40, 55, 680, 85, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(60, 80, "Глобальне середовище (Global Frame / main)", size=13, color="#334155", anchor="start", bold=True))
    frags.append(text(500, 80, "FUNCNAME = [ ]", size=11, color="#64748b", anchor="start"))
    frags.append(text(60, 105, "var=\"global_val\", counter=0, config_path=\"/etc/app.conf\"", size=11, color="#1e293b", anchor="start"))
    frags.append(text(60, 125, "виклик: outer_func()", size=11, color="#0284c7", anchor="start", bold=True))

    # Arrow down
    frags.append(line(380, 140, 380, 160, color="#64748b", sw=2))
    frags.append(arrow(380, 140, 380, 158, color="#64748b", sw=2))

    # Frame 2: outer_func
    frags.append(rect(40, 165, 680, 95, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    frags.append(text(60, 190, "Фрейм outer_func()", size=13, color="#166534", anchor="start", bold=True))
    frags.append(text(460, 190, "FUNCNAME = [\"outer_func\"]", size=11, color="#166534", anchor="start"))
    frags.append(text(60, 215, "Оголошення: local var=\"outer_local_val\"  (затінює глобальну 'var')", size=11, color="#14532d", anchor="start", bold=True))
    frags.append(text(60, 235, "Модифікація: counter=1 (змінює глобальну, бо 'counter' не local!)", size=11, color="#b91c1c", anchor="start"))
    frags.append(text(60, 252, "виклик: inner_func()", size=11, color="#0284c7", anchor="start", bold=True))

    # Arrow down
    frags.append(line(380, 260, 380, 280, color="#16a34a", sw=2))
    frags.append(arrow(380, 260, 380, 278, color="#16a34a", sw=2))

    # Frame 3: inner_func
    frags.append(rect(40, 285, 680, 175, fill="#fef2f2", stroke="#ef4444", sw=1.5))
    frags.append(text(60, 310, "Фрейм inner_func() — Динамічний пошук змінних углиб стека", size=13, color="#991b1b", anchor="start", bold=True))
    frags.append(text(430, 310, "FUNCNAME = [\"inner_func\", \"outer_func\"]", size=11, color="#991b1b", anchor="start"))
    
    dyn_search = [
        "1. Читання $var: inner_func() не має local var ──► перевіряє caller (outer_func)",
        "   Знайдено var=\"outer_local_val\"! (У статичній мові тут була б \"global_val\")",
        "2. Запис var=\"new_val\": змінює локальну змінну outer_func, а НЕ глобальну!",
        "3. Локальна змінна: local inner_tmp=\"xyz\" (зникне одразу після return з inner_func)",
        "4. Стек інспекції: BASH_SOURCE[0], BASH_LINENO[0] вказують на точне місце виклику"
    ]
    frags.append(mtext(60, 335, dyn_search, size=11, color="#7f1d1d", anchor="start", lh=1.45))

    path = os.path.join(img_dir, "dynamic-scoping-stack.svg")
    svg_render(path, w, h, *frags)

def render_pipeline_lastpipe(img_dir):
    w, h = 760, 450
    frags = []

    frags.append(text(w / 2, 25, "Конвеєр: стандартні підоболонки проти оптимізації shopt -s lastpipe", size=15, bold=True))

    # Standard pipeline
    frags.append(rect(30, 55, 335, 370, fill="#f8fafc", stroke="#dc2626", sw=1.5))
    frags.append(text(197, 80, "Стандартний конвеєр (POSIX / Bash)", size=13, color="#991b1b", bold=True))
    frags.append(text(197, 100, "echo \"data\" | while read line; do count=1; done", size=10, color="#64748b"))
    frags.append(line(45, 110, 350, 110, color="#fca5a5", sw=1))

    # Left stages
    frags.append(rect(45, 125, 305, 60, fill="#fee2e2", stroke="#ef4444", sw=1))
    frags.append(text(197, 145, "fork() ──► Subshell #1 (PID 2001)", size=11, color="#b91c1c", bold=True))
    frags.append(text(197, 165, "Виконує: echo \"data\"", size=10, color="#7f1d1d"))

    frags.append(line(197, 185, 197, 210, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(text(197, 200, "pipe [0] ◄── [1]", size=9, color=MUTED))

    frags.append(rect(45, 215, 305, 75, fill="#fee2e2", stroke="#ef4444", sw=1))
    frags.append(text(197, 235, "fork() ──► Subshell #2 (PID 2002)", size=11, color="#b91c1c", bold=True))
    frags.append(text(197, 255, "Виконує: while read line; count=1", size=10, color="#7f1d1d"))
    frags.append(text(197, 273, "Змінна count=1 живе лише в PID 2002", size=10, color="#991b1b", bold=True))

    frags.append(rect(45, 310, 305, 95, fill="#f1f5f9", stroke="#64748b", sw=1))
    frags.append(text(197, 330, "Батьківська оболонка (PID 2000)", size=11, color="#334155", bold=True))
    frags.append(text(197, 350, "Очікує завершення: waitpid()", size=10, color="#475569"))
    frags.append(text(197, 372, "Результат: $count все ще 0 (Втрачено!)", size=11, color="#b91c1c", bold=True))
    frags.append(text(197, 390, "Пам'ять Subshell #2 знищена ядром", size=10, color="#64748b"))

    # Optimized lastpipe
    frags.append(rect(395, 55, 335, 370, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    frags.append(text(562, 80, "Оптимізація shopt -s lastpipe", size=13, color="#166534", bold=True))
    frags.append(text(562, 100, "(Ksh93, Zsh дефолт / Bash non-interactive)", size=10, color="#15803d"))
    frags.append(line(410, 110, 715, 110, color="#86efac", sw=1))

    # Right stages
    frags.append(rect(410, 125, 305, 60, fill="#fee2e2", stroke="#ef4444", sw=1))
    frags.append(text(562, 145, "fork() ──► Subshell #1 (PID 2001)", size=11, color="#b91c1c", bold=True))
    frags.append(text(562, 165, "Виконує: echo \"data\"", size=10, color="#7f1d1d"))

    frags.append(line(562, 185, 562, 210, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(text(562, 200, "pipe [0] ◄── [1]", size=9, color=MUTED))

    frags.append(rect(410, 215, 305, 190, fill="#dcfce7", stroke="#22c55e", sw=1.5))
    frags.append(text(562, 238, "Батьківська оболонка (PID 2000)", size=12, color="#14532d", bold=True))
    frags.append(text(562, 260, "Виконує ОСТАННІЙ елемент in-process!", size=11, color="#15803d", bold=True))
    r_pts = [
        "1. Читає зі stdin каналу без fork()",
        "2. Виконує тіло while у власному просторі",
        "3. Присвоєння count=1 змінює пам'ять батька",
        "4. Після завершення циклу $count збережено!",
        "5. Повна відсутність накладних витрат fork"
    ]
    frags.append(mtext(425, 285, r_pts, size=10, color="#166534", anchor="start", lh=1.4))

    path = os.path.join(img_dir, "pipeline-lastpipe-comparison.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_subshell_fork_cow(img_dir)
    render_dynamic_scoping(img_dir)
    render_pipeline_lastpipe(img_dir)

if __name__ == '__main__':
    render()
