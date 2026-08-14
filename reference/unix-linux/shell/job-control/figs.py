import sys, os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def draw_arch(img_dir):
    path = os.path.join(img_dir, 'job-control-arch.svg')
    frags = []
    
    # Outer Session Box
    frags.append(rect(10, 10, 700, 390, fill="#f8f9fa", stroke="#4b5563", sw=2, rx=8))
    frags.append(text(360, 32, "Сесія (Session, SID = 1000) — Лідер: bash (PID 1000)", size=15, bold=True, color="#1f2937"))
    
    # Controlling Terminal Box
    frags.append(rect(30, 60, 200, 100, fill="#eff6ff", stroke="#2563eb", sw=2, rx=6))
    frags.append(text(130, 85, "Управляючий термінал", size=13, bold=True, color="#1e40af"))
    frags.append(text(130, 105, "/dev/pts/2", size=12, bold=True, color="#1d4ed8"))
    frags.append(text(130, 125, "TPGID = 2000 (fg group)", size=11, color="#3b82f6"))
    frags.append(text(130, 145, "Прапор: ISIG | TOSTOP", size=10, color="#6b7280"))
    
    # Foreground Process Group Box
    frags.append(rect(260, 60, 430, 140, fill="#fef2f2", stroke="#dc2626", sw=2, rx=6))
    frags.append(text(475, 82, "Foreground Група (PGID = 2000)", size=14, bold=True, color="#991b1b"))
    
    # Processes in Foreground PGID
    frags.append(rect(280, 100, 180, 80, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(370, 122, "cat /var/log/syslog", size=12, bold=True, color="#111827"))
    frags.append(text(370, 142, "PID = 2000 (Лідер)", size=11, color="#4b5563"))
    frags.append(text(370, 162, "Отримує ввід з TTY", size=10, color="#059669"))
    
    frags.append(rect(490, 100, 180, 80, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(580, 122, "grep CRITICAL", size=12, bold=True, color="#111827"))
    frags.append(text(580, 142, "PID = 2001", size=11, color="#4b5563"))
    frags.append(text(580, 162, "Приймає SIGINT/SIGTSTP", size=10, color="#dc2626"))
    
    frags.append(arrow(460, 140, 490, 140, color="#4b5563", sw=1.5))
    
    # Arrow from Terminal to FG group
    frags.append(arrow(230, 80, 260, 80, color="#dc2626", sw=2))
    frags.append(text(245, 72, "tcsetpgrp()", size=10, color="#2563eb", bold=True))
    
    # Background Process Group 1 (Shell itself)
    frags.append(rect(30, 220, 310, 160, fill="#f3f4f6", stroke="#6b7280", sw=1.5, rx=6))
    frags.append(text(185, 242, "Background Група Оболонки (PGID = 1000)", size=13, bold=True, color="#374151"))
    frags.append(rect(50, 260, 270, 100, fill="#ffffff", stroke="#6b7280", rx=4))
    frags.append(text(185, 282, "bash (Оболонка)", size=13, bold=True, color="#111827"))
    frags.append(text(185, 302, "PID = 1000, SID = 1000", size=11, color="#4b5563"))
    frags.append(text(185, 322, "Чекає у waitpid(WUNTRACED)", size=11, color="#6b7280"))
    frags.append(text(185, 342, "Керує таблицею завдань", size=10, color="#2563eb"))
    
    # Background Process Group 2 (Job #1 suspended or running)
    frags.append(rect(370, 220, 320, 160, fill="#fffbe6", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(530, 242, "Background Завдання #1 (PGID = 1500)", size=13, bold=True, color="#b45309"))
    frags.append(rect(390, 260, 280, 100, fill="#ffffff", stroke="#d97706", rx=4))
    frags.append(text(530, 282, "make -j4 (Зупинено / Фоне)", size=12, bold=True, color="#111827"))
    frags.append(text(530, 302, "PID = 1500, Стан: TASK_STOPPED", size=11, color="#4b5563"))
    frags.append(text(530, 322, "Спроба read() → SIGTTIN", size=11, bold=True, color="#dc2626"))
    frags.append(text(530, 342, "Спроба write() (TOSTOP=1) → SIGTTOU", size=10, color="#d97706"))
    
    render(path, 720, 410, *frags)

def draw_ttin_ttou(img_dir):
    path = os.path.join(img_dir, 'job-control-ttin-ttou.svg')
    frags = []
    
    frags.append(rect(10, 10, 680, 320, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    frags.append(text(350, 30, "Арбітраж термінала: Сигнали SIGTTIN та SIGTTOU", size=15, bold=True, color="#111827"))
    
    # Terminal Driver Box
    frags.append(rect(30, 60, 180, 240, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6))
    frags.append(text(120, 85, "Драйвер TTY", size=14, bold=True, color="#1d4ed8"))
    frags.append(text(120, 105, "n_tty.c", size=11, color="#6b7280"))
    frags.append(rect(45, 120, 150, 60, fill="#ffffff", stroke="#93c5fd", rx=4))
    frags.append(text(120, 140, "Foreground PGID:", size=11, color="#1e40af"))
    frags.append(text(120, 160, "2000", size=14, bold=True, color="#dc2626"))
    frags.append(rect(45, 200, 150, 80, fill="#ffffff", stroke="#93c5fd", rx=4))
    frags.append(text(120, 220, "Прапорці termios:", size=11, color="#1e40af"))
    frags.append(text(120, 240, "ISIG = 1", size=11, color="#374151"))
    frags.append(text(120, 260, "TOSTOP = 1", size=11, bold=True, color="#b45309"))
    
    # Foreground Process Box
    frags.append(rect(260, 60, 390, 90, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(455, 82, "Foreground Процес (PGID = 2000)", size=13, bold=True, color="#991b1b"))
    frags.append(text(455, 105, "read(0, buf, n) → Дозволено (отримує байти)", size=11, color="#059669", bold=True))
    frags.append(text(455, 128, "write(1, buf, n) → Дозволено (виводить на екран)", size=11, color="#059669", bold=True))
    
    frags.append(arrow(210, 95, 260, 95, color="#059669", sw=2))
    
    # Background Process Box
    frags.append(rect(260, 170, 390, 130, fill="#fffbe6", stroke="#f59e0b", sw=1.5, rx=6))
    frags.append(text(455, 192, "Background Процес (PGID = 1500)", size=13, bold=True, color="#b45309"))
    frags.append(text(455, 218, "Спроба read(0, buf, n)  →  Драйвер надсилає SIGTTIN", size=11, bold=True, color="#dc2626"))
    frags.append(text(455, 242, "Спроба write(1, buf, n) (TOSTOP=1) → SIGTTOU", size=11, bold=True, color="#b45309"))
    frags.append(text(455, 275, "Результат: Стан TASK_STOPPED (Stopped (tty input/output))", size=11, color="#4b5563"))
    
    frags.append(arrow(210, 220, 260, 220, color="#dc2626", sw=2))
    frags.append(arrow(210, 250, 260, 250, color="#b45309", sw=2))
    
    render(path, 700, 340, *frags)

def draw_lifecycle(img_dir):
    path = os.path.join(img_dir, 'job-control-lifecycle.svg')
    frags = []
    
    frags.append(rect(10, 10, 720, 300, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    frags.append(text(370, 30, "Життєвий цикл завдання та переходи між станами", size=15, bold=True, color="#111827"))
    
    # State 1: Foreground Running
    frags.append(rect(30, 70, 190, 100, fill="#fef2f2", stroke="#ef4444", sw=2, rx=6))
    frags.append(text(125, 95, "Foreground Running", size=13, bold=True, color="#991b1b"))
    frags.append(text(125, 115, "Володіє TTY", size=11, color="#dc2626"))
    frags.append(text(125, 135, "Отримує ввід", size=11, color="#dc2626"))
    frags.append(text(125, 150, "Оболонка чекає", size=10, color="#6b7280"))
    
    # State 2: Stopped
    frags.append(rect(280, 70, 190, 100, fill="#f3f4f6", stroke="#4b5563", sw=2, rx=6))
    frags.append(text(375, 95, "Stopped (TASK_STOPPED)", size=13, bold=True, color="#1f2937"))
    frags.append(text(375, 115, "Не отримує CPU", size=11, color="#4b5563"))
    frags.append(text(375, 135, "Записано в jobs", size=11, color="#4b5563"))
    frags.append(text(375, 150, "Оболонка володіє TTY", size=10, color="#2563eb"))
    
    # State 3: Background Running
    frags.append(rect(510, 70, 190, 100, fill="#ecfdf5", stroke="#10b981", sw=2, rx=6))
    frags.append(text(605, 95, "Background Running", size=13, bold=True, color="#065f46"))
    frags.append(text(605, 115, "Виконується у фоні", size=11, color="#047857"))
    frags.append(text(605, 135, "read() → SIGTTIN", size=11, color="#dc2626"))
    frags.append(text(605, 150, "Оболонка вільна", size=10, color="#047857"))
    
    # Transitions
    # 1 -> 2: Ctrl+Z (SIGTSTP)
    frags.append(arrow(220, 100, 280, 100, color="#dc2626", sw=2))
    frags.append(text(250, 90, "Ctrl+Z (SIGTSTP)", size=10, bold=True, color="#dc2626"))
    
    # 2 -> 3: bg %N (SIGCONT)
    frags.append(arrow(470, 100, 510, 100, color="#047857", sw=2))
    frags.append(text(490, 90, "bg (SIGCONT)", size=10, bold=True, color="#047857"))
    
    # 3 -> 2: SIGTTIN / SIGTTOU
    frags.append(arrow(550, 170, 420, 170, color="#d97706", sw=1.5))
    frags.append(text(485, 185, "read() / write() → SIGTTIN / SIGTTOU", size=10, bold=True, color="#d97706"))
    
    # 2 -> 1: fg %N (tcsetpgrp + SIGCONT)
    frags.append(arrow(340, 170, 140, 170, color="#2563eb", sw=2))
    frags.append(text(240, 190, "fg (tcsetpgrp + SIGCONT)", size=11, bold=True, color="#2563eb"))
    
    # Additional Spawn to BG arrow
    frags.append(arrow(370, 230, 605, 170, color="#047857", sw=1.5))
    frags.append(text(460, 240, "Запуск з '&' (command &)", size=10, color="#047857"))
    
    render(path, 740, 310, *frags)

def draw():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    draw_arch(img_dir)
    draw_ttin_ttou(img_dir)
    draw_lifecycle(img_dir)

if __name__ == '__main__':
    draw()
