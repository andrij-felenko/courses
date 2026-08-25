import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_in_process_vs_subshell(img_dir):
    w, h = 820, 430
    frags = []
    
    frags.append(text(w / 2, 28, "Порівняння: підстановка параметра в пам'яті проти запуску підпроцесу", size=15, bold=True))
    
    # Left Box: In-process Parameter Expansion
    frags.append(rect(30, 55, 365, 350, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(212, 82, "Внутрішній механізм оболонки", size=13, color="#166534", bold=True))
    frags.append(text(212, 102, "${path##*/}  або  ${var//foo/bar}", size=11, color="#15803d"))
    
    frags.append(rect(50, 120, 325, 60, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(212, 142, "Єдиний процес оболонки (PID: 1042)", size=11, bold=True, color="#14532d"))
    frags.append(text(212, 162, "Хеш-таблиця змінних у купі процесу", size=10, color="#166534"))
    
    frags.append(arrow(212, 180, 212, 205, color="#16a34a", sw=1.8))
    
    frags.append(rect(50, 205, 325, 75, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(212, 227, "Пряма модифікація буфера (RAM)", size=11, bold=True, color="#14532d"))
    frags.append(text(212, 247, "Зіставлення патерну в пам'яті + копіювання", size=10, color="#166534"))
    frags.append(text(212, 265, "Системні виклики до ядра: 0", size=10, bold=True, color="#15803d"))
    
    frags.append(rect(50, 300, 325, 85, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=6))
    frags.append(text(212, 322, "Характеристики виконання:", size=11, bold=True, color="#14532d"))
    frags.append(text(212, 342, "Час: ~0.05 мкс на операцію", size=10, color="#166534"))
    frags.append(text(212, 360, "Накладні витрати пам'яті: 0 байтів", size=10, color="#166534"))
    frags.append(text(212, 376, "100 000 ітерацій: ~0.04 с", size=10, bold=True, color="#15803d"))
    
    # Right Box: External Process Substitution
    frags.append(rect(425, 55, 365, 350, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(text(607, 82, "Зовнішній конвеєр / утиліта", size=13, color="#991b1b", bold=True))
    frags.append(text(607, 102, "$(basename \"$path\")  або  $(echo \"$var\" | sed ...)", size=11, color="#b91c1c"))
    
    frags.append(rect(445, 120, 325, 60, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    frags.append(text(607, 138, "Батьківський процес (PID: 1042)", size=10, bold=True, color="#7f1d1d"))
    frags.append(text(607, 154, "1. fork() -> 2. pipe() -> 3. wait4()", size=10, color="#991b1b"))
    frags.append(text(607, 169, "Блокування очікуванням завершення I/O", size=9, color="#b91c1c"))
    
    frags.append(arrow(607, 180, 607, 205, color="#dc2626", sw=1.8))
    
    frags.append(rect(445, 205, 325, 75, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    frags.append(text(607, 224, "Дочірній процес (PID: 1043)", size=10, bold=True, color="#7f1d1d"))
    frags.append(text(607, 240, "execve(/usr/bin/basename) + ld.so + libc", size=9, color="#991b1b"))
    frags.append(text(607, 255, "Копіювання таблиць сторінок, скидання TLB", size=9, color="#b91c1c"))
    frags.append(text(607, 270, "Міжпроцесна передача IPC через пайп", size=9, color="#991b1b"))
    
    frags.append(rect(445, 300, 325, 85, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=6))
    frags.append(text(607, 322, "Характеристики виконання:", size=11, bold=True, color="#7f1d1d"))
    frags.append(text(607, 342, "Час: ~1.5 - 3.0 мс на операцію", size=10, color="#991b1b"))
    frags.append(text(607, 360, "Накладні витрати: створення процесу та VMA", size=10, color="#991b1b"))
    frags.append(text(607, 376, "100 000 ітерацій: ~180.0 с (у 4500 разів повільніше)", size=10, bold=True, color="#b91c1c"))
    
    os.makedirs(img_dir, exist_ok=True)
    svg_render(os.path.join(img_dir, "in-process-vs-subshell.svg"), w, h, *frags)

def render_parameter_decision_tree(img_dir):
    w, h = 820, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Логіка перевірки стану змінних у виразах дефолтів", size=15, bold=True))
    
    # Root Question
    frags.append(rect(280, 50, 260, 45, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(410, 77, "Чи існує змінна у таблиці символів?", size=11, bold=True, color="#1e293b"))
    
    # Branch Unset
    frags.append(line(340, 95, 170, 140, color="#64748b", sw=1.5))
    frags.append(text(210, 112, "НІ (unset)", size=10, bold=True, color="#dc2626"))
    
    frags.append(rect(30, 140, 280, 135, fill="#fef2f2", stroke="#ef4444", sw=1.3, rx=6))
    frags.append(text(170, 162, "Стан: Unset (не встановлено)", size=11, bold=True, color="#991b1b"))
    frags.append(text(170, 185, "${var-def} та ${var:-def} ──► def", size=10, color="#7f1d1d"))
    frags.append(text(170, 207, "${var=def} та ${var:=def} ──► var=def; def", size=10, color="#7f1d1d"))
    frags.append(text(170, 229, "${var?err} та ${var:?err} ──► помилка, вихід", size=10, color="#7f1d1d"))
    frags.append(text(170, 251, "${var+alt} та ${var:+alt} ──► порожньо (\"\")", size=10, color="#7f1d1d"))
    frags.append(text(170, 267, "(Двокрапка \":\" не змінює результат)", size=9, italic=True, color="#b91c1c"))
    
    # Branch Set
    frags.append(line(480, 95, 620, 140, color="#64748b", sw=1.5))
    frags.append(text(580, 112, "ТАК (встановлено)", size=10, bold=True, color="#16a34a"))
    
    frags.append(rect(490, 140, 260, 45, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(620, 167, "Яке значення має змінна?", size=11, bold=True, color="#1e293b"))
    
    # Sub-branch: Empty / Null
    frags.append(line(550, 185, 450, 225, color="#64748b", sw=1.5))
    frags.append(text(460, 205, "Порожнє (\"\")", size=10, bold=True, color="#d97706"))
    
    frags.append(rect(340, 225, 230, 230, fill="#fffbeb", stroke="#f59e0b", sw=1.3, rx=6))
    frags.append(text(455, 247, "Стан: Null (var=\"\")", size=11, bold=True, color="#92400e"))
    frags.append(text(455, 270, "Без двокрапки (дійсна змінна):", size=10, bold=True, color="#b45309"))
    frags.append(text(455, 290, "${var-def}  ──► \"\"", size=10, color="#78350f"))
    frags.append(text(455, 308, "${var=def}  ──► \"\" (без змін)", size=10, color="#78350f"))
    frags.append(text(455, 326, "${var?err}  ──► \"\" (немає помилки)", size=10, color="#78350f"))
    frags.append(text(455, 344, "${var+alt}  ──► alt", size=10, color="#78350f"))
    frags.append(text(455, 367, "З двокрапкою (якщо порожнє):", size=10, bold=True, color="#b45309"))
    frags.append(text(455, 387, "${var:-def} ──► def", size=10, color="#78350f"))
    frags.append(text(455, 405, "${var:=def} ──► var=def; def", size=10, color="#78350f"))
    frags.append(text(455, 423, "${var:?err} ──► помилка, вихід", size=10, color="#78350f"))
    frags.append(text(455, 441, "${var:+alt} ──► \"\"", size=10, color="#78350f"))
    
    # Sub-branch: Non-empty
    frags.append(line(690, 185, 700, 225, color="#64748b", sw=1.5))
    frags.append(text(725, 205, "Непорожнє (\"abc\")", size=10, bold=True, color="#16a34a"))
    
    frags.append(rect(590, 225, 210, 230, fill="#f0fdf4", stroke="#16a34a", sw=1.3, rx=6))
    frags.append(text(695, 247, "Стан: Set & Non-null", size=11, bold=True, color="#166534"))
    frags.append(text(695, 275, "Значення визначене:", size=10, bold=True, color="#15803d"))
    frags.append(text(695, 305, "${var-def} та ${var:-def}", size=10, color="#14532d"))
    frags.append(text(695, 323, " ──► \"abc\"", size=10, bold=True, color="#15803d"))
    frags.append(text(695, 350, "${var=def} та ${var:=def}", size=10, color="#14532d"))
    frags.append(text(695, 368, " ──► \"abc\" (var не змінюється)", size=10, color="#14532d"))
    frags.append(text(695, 395, "${var?err} та ${var:?err}", size=10, color="#14532d"))
    frags.append(text(695, 413, " ──► \"abc\"", size=10, color="#14532d"))
    frags.append(text(695, 435, "${var+alt} та ${var:+alt} ──► alt", size=10, bold=True, color="#15803d"))
    
    os.makedirs(img_dir, exist_ok=True)
    svg_render(os.path.join(img_dir, "parameter-decision-tree.svg"), w, h, *frags)

def render_trimming_patterns(img_dir):
    w, h = 820, 440
    frags = []
    
    frags.append(text(w / 2, 28, "Оператори обрізання префіксів та суфіксів за glob-шаблонами", size=15, bold=True))
    
    # Path buffer visualization
    frags.append(rect(50, 55, 720, 50, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(410, 75, "Вихідний рядок:  path=\"/var/log/nginx/access.log.tar.gz\"", size=12, bold=True, color="#0f172a"))
    frags.append(text(410, 94, "Складові: [/var/log/nginx/] [access] [.log] [.tar] [.gz]", size=10, color="#475569"))
    
    # Row 1: Shortest Prefix #
    frags.append(rect(50, 120, 345, 65, fill="#f0f9ff", stroke="#0284c7", sw=1.2, rx=6))
    frags.append(text(222, 140, "${path#*/}", size=12, bold=True, color="#0369a1"))
    frags.append(text(222, 158, "Видаляє найкоротший префікс, що збігається з */", size=10, color="#075985"))
    frags.append(text(222, 174, "Результат: \"var/log/nginx/access.log.tar.gz\"", size=10, bold=True, color="#0c4a6e"))
    
    # Row 1: Longest Prefix ## (basename)
    frags.append(rect(425, 120, 345, 65, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=6))
    frags.append(text(597, 140, "${path##*/}", size=12, bold=True, color="#0369a1"))
    frags.append(text(597, 158, "Видаляє найдовший префікс до останнього / (basename)", size=10, color="#075985"))
    frags.append(text(597, 174, "Результат: \"access.log.tar.gz\"", size=10, bold=True, color="#0c4a6e"))
    
    # Row 2: Shortest Suffix % (strip last extension)
    frags.append(rect(50, 200, 345, 65, fill="#fdf4ff", stroke="#c026d3", sw=1.2, rx=6))
    frags.append(text(222, 220, "${path%.*}", size=12, bold=True, color="#a21caf"))
    frags.append(text(222, 238, "Видаляє найкоротший суфікс від останньої крапки", size=10, color="#86198f"))
    frags.append(text(222, 254, "Результат: \"/var/log/nginx/access.log.tar\"", size=10, bold=True, color="#701a75"))
    
    # Row 2: Longest Suffix %% (strip all extensions / stem)
    frags.append(rect(425, 200, 345, 65, fill="#fae8ff", stroke="#c026d3", sw=1.2, rx=6))
    frags.append(text(597, 220, "${path%%.*}", size=12, bold=True, color="#a21caf"))
    frags.append(text(597, 238, "Видаляє найдовший суфікс від першої крапки (stem)", size=10, color="#86198f"))
    frags.append(text(597, 254, "Результат: \"/var/log/nginx/access\"", size=10, bold=True, color="#701a75"))
    
    # Row 3: dirname idiom with %/*
    frags.append(rect(50, 280, 345, 65, fill="#fefce8", stroke="#ca8a04", sw=1.2, rx=6))
    frags.append(text(222, 300, "${path%/*}", size=12, bold=True, color="#a16207"))
    frags.append(text(222, 318, "Видаляє найкоротший суфікс від останнього / (dirname)", size=10, color="#854d0e"))
    frags.append(text(222, 334, "Результат: \"/var/log/nginx\"", size=10, bold=True, color="#713f12"))
    
    # Row 3: Pattern replacement / and //
    frags.append(rect(425, 280, 345, 65, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=6))
    frags.append(text(597, 300, "${path//\\//_}  та  ${path/#\\/var/\\/opt}", size=12, bold=True, color="#15803d"))
    frags.append(text(597, 318, "Заміна всіх збігів (//) або якоріння на початку (/#)", size=10, color="#166534"))
    frags.append(text(597, 334, "Результат: \"_var_log...\" та \"/opt/log/...\"", size=10, bold=True, color="#14532d"))
    
    # Summary note box
    frags.append(rect(50, 360, 720, 55, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(410, 380, "Пам'ятка запам'ятовування: # на клавіатурі стоїть лівіше за % (Shift+3 лівіше Shift+5).", size=10, bold=True, color="#334155"))
    frags.append(text(410, 398, "Тому # та ## обрізають зліва (префікс), а % та %% обрізають справа (суфікс). Одинарний — короткий, подвійний — довгий.", size=9, color="#475569"))
    
    os.makedirs(img_dir, exist_ok=True)
    svg_render(os.path.join(img_dir, "trimming-patterns.svg"), w, h, *frags)

if __name__ == '__main__':
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    render_in_process_vs_subshell(img_dir)
    render_parameter_decision_tree(img_dir)
    render_trimming_patterns(img_dir)
