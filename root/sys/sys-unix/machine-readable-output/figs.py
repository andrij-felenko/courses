# -*- coding: utf-8 -*-
import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_cli_duality(img_dir):
    w, h = 760, 470
    frags = []
    
    frags.append(text(w / 2, 25, "Дуальність інтерфейсу CLI: термінал користувача проти конвеєра", size=15, bold=True))
    
    # Left column: Interactive Terminal (Human)
    frags.append(rect(30, 50, 335, 395, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    frags.append(text(197, 75, "Людський вивід (Інтерактивний TTY)", size=14, color="#15803d", bold=True))
    frags.append(line(45, 88, 350, 88, color="#16a34a", sw=1))
    
    human_traits = [
        "• Ціль: швидке сприйняття людиною",
        "• isatty(STDOUT_FILENO) == 1 (true)",
        "• Форматування: вирівняні стовпці, шапка",
        "• Кольори: ANSI escape-коди (\\033[32m)",
        "• Одиниці: суфікси K/M/G (4.2G замість байтів)",
        "• Інтерактивність: прогрес-бари (\\r), пейджер",
        "• Буферизація: рядкова (_IOLBF)"
    ]
    frags.append(mtext(45, 112, human_traits, size=11, color="#14532d", anchor="start", lh=1.6))
    
    # Box snippet human
    frags.append(rect(45, 275, 305, 155, fill="#ffffff", stroke="#86efac", sw=1))
    frags.append(text(197, 295, "Приклад виводу для оператора:", size=11, color="#15803d", bold=True))
    human_sample = [
        "NAME    SIZE  TYPE MOUNTPOINT",
        "sda     1.8T  disk",
        "├─sda1  512M  part /boot/efi",
        "└─sda2  1.8T  part /",
        "Зручно для очей, але ламає парсери"
    ]
    frags.append(mtext(55, 318, human_sample, size=10, color="#1e293b", anchor="start", lh=1.4))
    
    # Right column: Pipeline / Machine
    frags.append(rect(395, 50, 335, 395, fill="#f0f9ff", stroke="#0284c7", sw=1.5))
    frags.append(text(562, 75, "Машинний вивід (Конвеєр / Скрипт)", size=14, color="#0369a1", bold=True))
    frags.append(line(410, 88, 715, 88, color="#0284c7", sw=1))
    
    machine_traits = [
        "• Ціль: стабільний автоматичний парсинг",
        "• isatty(STDOUT_FILENO) == 0 (pipe/file)",
        "• Форматування: JSON, TSV або NUL-розділювачі",
        "• Чистота: без ANSI-кодів та пейджерів",
        "• Точність: сирі цілі числа (1932735283200)",
        "• Заголовки: відсутні (--no-heading)",
        "• Буферизація: повна блокова (_IOFBF, 4KB)"
    ]
    frags.append(mtext(410, 112, machine_traits, size=11, color="#0c4a6e", anchor="start", lh=1.6))
    
    # Box snippet machine
    frags.append(rect(410, 275, 305, 155, fill="#ffffff", stroke="#7dd3fc", sw=1))
    frags.append(text(562, 295, "Приклад виводу для скриптів (JSON / TSV):", size=11, color="#0369a1", bold=True))
    machine_sample = [
        "{\"blockdevices\": [",
        "  {\"name\": \"sda\", \"size\": 1932735283200},",
        "  {\"name\": \"sda1\", \"size\": 536870912},",
        "  {\"name\": \"sda2\", \"size\": 1932198412288}",
        "]}",
        "Детерміновано, типобезпечно, стабільно"
    ]
    frags.append(mtext(420, 315, machine_sample, size=9.5, color="#1e293b", anchor="start", lh=1.35))
    
    path = os.path.join(img_dir, "cli-duality-pipeline.svg")
    svg_render(path, w, h, *frags)

def render_isatty_kernel_flow(img_dir):
    w, h = 760, 480
    frags = []
    
    frags.append(text(w / 2, 25, "Механізм визначення типу пристрою: isatty() у просторі ядра та користувача", size=14, bold=True))
    
    # User space layer
    frags.append(rect(30, 50, 700, 95, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(380, 72, "Простір користувача (libc / Програма)", size=13, color="#334155", bold=True))
    frags.append(rect(50, 85, 310, 45, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(205, 112, "isatty(STDOUT_FILENO)", size=12, color="#0f172a", bold=True))
    
    frags.append(arrow(360, 107, 420, 107, color="#64748b", sw=1.5))
    
    frags.append(rect(420, 85, 290, 45, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(565, 112, "ioctl(1, TCGETS, &termios)", size=12, color="#0f172a", bold=True))
    
    # Kernel transition line
    frags.append(line(30, 160, 730, 160, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(380, 175, "Межа системного виклику (Trap / Syscall)", size=11, color="#64748b", italic=True))
    
    # Kernel layer
    frags.append(rect(30, 190, 700, 120, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(380, 212, "Ядро Linux: VFS та драйвери пристроїв", size=13, color="#9a3412", bold=True))
    
    frags.append(rect(50, 230, 310, 65, fill="#ffffff", stroke="#fdba74", sw=1))
    frags.append(text(205, 252, "Файловий дескриптор fd=1", size=11, color="#9a3412", bold=True))
    frags.append(text(205, 275, "struct file -> f_op->unlocked_ioctl()", size=10.5, color="#7c2d12"))
    
    frags.append(rect(420, 230, 290, 65, fill="#ffffff", stroke="#fdba74", sw=1))
    frags.append(text(565, 252, "Перевірка обробника TCGETS", size=11, color="#9a3412", bold=True))
    frags.append(text(565, 275, "Чи підтримує файл операції термінала?", size=10.5, color="#7c2d12"))
    
    # Branches down
    frags.append(arrow(205, 295, 205, 345, color="#16a34a", sw=2))
    frags.append(arrow(565, 295, 565, 345, color="#dc2626", sw=2))
    
    # Success branch (TTY)
    frags.append(rect(40, 345, 330, 115, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(205, 370, "Пристрій: /dev/pts/* або /dev/tty*", size=12, color="#166534", bold=True))
    frags.append(mtext(205, 395, ["Результат ioctl: 0 (Успіх)", "libc повертає isatty() == 1", "Дія: вмикаємо ANSI кольори, таблиці, пейджер"], size=10.5, color="#14532d", lh=1.4))
    
    # Failure branch (Pipe / File)
    frags.append(rect(390, 345, 330, 115, fill="#fee2e2", stroke="#dc2626", sw=1.5))
    frags.append(text(555, 370, "Пристрій: pipe, socket, регулярний файл", size=12, color="#991b1b", bold=True))
    frags.append(mtext(555, 395, ["Результат ioctl: -1 (errno = ENOTTY)", "libc повертає isatty() == 0", "Дія: чистий потік даних, JSON/TSV, без ANSI"], size=10.5, color="#7f1d1d", lh=1.4))
    
    path = os.path.join(img_dir, "isatty-kernel-flow.svg")
    svg_render(path, w, h, *frags)

def render_delimiter_traps(img_dir):
    w, h = 760, 450
    frags = []
    
    frags.append(text(w / 2, 25, "Пастки розділювачів у конвеєрі Unix: пробіли, нові рядки та NUL-байт", size=14, bold=True))
    
    # Scenario A: Whitespace splitting failure
    frags.append(rect(30, 50, 700, 175, fill="#fef2f2", stroke="#ef4444", sw=1.5))
    frags.append(text(380, 72, "1. Небезпечний конвеєр: поділ за пробілами та переносом рядка (IFS)", size=13, color="#991b1b", bold=True))
    
    frags.append(rect(50, 88, 300, 50, fill="#ffffff", stroke="#fca5a5", sw=1))
    frags.append(text(200, 107, "Вхідні файли на диску:", size=11, color="#7f1d1d", bold=True))
    frags.append(text(200, 126, "\"report 2026.pdf\"  та  \"backup\\nrm.sh\"", size=10, color="#991b1b"))
    
    frags.append(arrow(350, 113, 400, 113, color="#ef4444", sw=1.5))
    
    frags.append(rect(400, 88, 310, 50, fill="#ffffff", stroke="#fca5a5", sw=1))
    frags.append(text(555, 107, "Команда: for f in $(ls); do ...", size=11, color="#7f1d1d", bold=True))
    frags.append(text(555, 126, "Оболонка розбиває рядок за $IFS (пробіл, табуляція, \\n)", size=9.5, color="#991b1b"))
    
    frags.append(rect(50, 150, 660, 60, fill="#fee2e2", stroke="#ef4444", sw=1))
    frags.append(text(380, 170, "Результат: файл розрізано на 4 фальшивих аргументи: 'report', '2026.pdf', 'backup', 'rm.sh'", size=11, color="#991b1b", bold=True))
    frags.append(text(380, 192, "Скрипт видаляє або перезаписує випадкові файли, виникає критична помилка автоматизації", size=10.5, color="#7f1d1d"))
    
    # Scenario B: Safe NUL-delimiter pipeline
    frags.append(rect(30, 245, 700, 185, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    frags.append(text(380, 268, "2. Надійний машинний конвеєр: нульовий байт (NUL / \\0) як атомарна межа", size=13, color="#15803d", bold=True))
    
    frags.append(rect(50, 285, 300, 55, fill="#ffffff", stroke="#86efac", sw=1))
    frags.append(text(200, 305, "Потік виводу find / git -z:", size=11, color="#14532d", bold=True))
    frags.append(text(200, 326, "report 2026.pdf\\0backup\\nrm.sh\\0", size=10, color="#166534"))
    
    frags.append(arrow(350, 312, 400, 312, color="#16a34a", sw=1.5))
    
    frags.append(rect(400, 285, 310, 55, fill="#ffffff", stroke="#86efac", sw=1))
    frags.append(text(555, 305, "Обробка: xargs -0 / read -d ''", size=11, color="#14532d", bold=True))
    frags.append(text(555, 326, "Байт \\0 заборонений у шляхах POSIX (стабільна межа)", size=9.5, color="#14532d"))
    
    frags.append(rect(50, 355, 660, 60, fill="#dcfce7", stroke="#16a34a", sw=1))
    frags.append(text(380, 375, "Результат: рівно 2 непорушні елементи з оригінальними пробілами та переносами", size=11, color="#15803d", bold=True))
    frags.append(text(380, 397, "Гарантія безпеки: жоден спецсимвол у назві об'єкта не ламає логіку обробки", size=10.5, color="#14532d"))
    
    path = os.path.join(img_dir, "whitespace-delimiter-traps.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_cli_duality(img_dir)
    render_isatty_kernel_flow(img_dir)
    render_delimiter_traps(img_dir)

if __name__ == '__main__':
    render()
