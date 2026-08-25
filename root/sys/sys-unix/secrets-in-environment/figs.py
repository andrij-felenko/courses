import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_leak_vectors(img_dir):
    w, h = 820, 540
    frags = []
    
    # Title
    frags.append(text(w / 2, 28, "Вектори витоків секретів зі змінних середовища (environ)", size=16, bold=True))
    
    # Center: Process virtual memory box
    frags.append(rect(240, 65, 340, 210, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(410, 92, "Пам'ять процесу (UID = 1000)", size=14, color="#991b1b", bold=True))
    frags.append(line(255, 105, 565, 105, color=POS, sw=1))
    
    mem_items = [
        "Стек: char **environ",
        "• DB_PASSWORD=SecretPass123!",
        "• AWS_SECRET_KEY=AKIA...XYZ",
        "• JWT_SIGNING_KEY=d8f1e0...c4",
        "Купа / .bss / .data: відкритий текст у RAM"
    ]
    frags.append(mtext(410, 125, mem_items, size=11, color="#7f1d1d", anchor="middle", lh=1.45))
    
    # Vector 1: /proc/$PID/environ (Top Left)
    frags.append(rect(25, 65, 185, 120, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(117, 88, "1. Читання через procfs", size=12, color="#0369a1", bold=True))
    frags.append(mtext(117, 108, ["/proc/$PID/environ", "Доступно будь-якому", "процесу того самого UID", "або root без ptrace"], size=10, color="#0c4a6e", anchor="middle", lh=1.35))
    frags.append(arrow(240, 125, 213, 125, color="#0284c7", sw=1.8))
    
    # Vector 2: Uncontrolled Inheritance (Top Right)
    frags.append(rect(610, 65, 185, 120, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    frags.append(text(702, 88, "2. Успадкування дочірніми", size=12, color="#a21caf", bold=True))
    frags.append(mtext(702, 108, ["fork() + execve()", "Усі змінні копіюються", "у ps, tar, curl, convert", "та сторонні скрипти"], size=10, color="#701a75", anchor="middle", lh=1.35))
    frags.append(arrow(580, 125, 607, 125, color="#c026d3", sw=1.8))
    
    # Vector 3: Coredumps & Memory Dumps (Bottom Left)
    frags.append(rect(25, 330, 230, 150, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6))
    frags.append(text(140, 355, "3. Coredump та файли крешів", size=12, color="#c2410c", bold=True))
    frags.append(mtext(140, 377, ["SIGSEGV / SIGABRT скидає", "початковий стек на диск", "(/var/lib/systemd/coredump)", "Паролі потрапляють у нешифровані", "дампи та системи аналізу"], size=10, color="#7c2d12", anchor="middle", lh=1.35))
    frags.append(arrow(330, 275, 200, 327, color="#ea580c", sw=1.8))
    
    # Vector 4: Logging & APM (Bottom Right)
    frags.append(rect(565, 330, 230, 150, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(text(680, 355, "4. APM, логи та винятки", size=12, color="#854d0e", bold=True))
    frags.append(mtext(680, 377, ["Sentry, Datadog, Bugsnag", "дамплять os.environ при помилках;", "Діагностика CI/CD, set -x,", "друк env у stdout/stderr", "витікає в центральні логи"], size=10, color="#713f12", anchor="middle", lh=1.35))
    frags.append(arrow(490, 275, 620, 327, color="#ca8a04", sw=1.8))
    
    # Bottom Summary banner
    frags.append(rect(270, 360, 280, 100, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(410, 385, "Чому середовище не захищене?", size=12, color="#334155", bold=True))
    frags.append(mtext(410, 408, ["• Немає розмежування прав за змінними", "• Відкритий текст у віртуальній пам'яті", "• Автоматичне успадкування всім деревом"], size=10, color="#475569", anchor="middle", lh=1.35))
    
    path = os.path.join(img_dir, "environ-leak-vectors.svg")
    svg_render(path, w, h, *frags)

def render_secure_alternatives(img_dir):
    w, h = 820, 520
    frags = []
    
    # Title
    frags.append(text(w / 2, 28, "Архітектура безпечної передачі секретів у Linux", size=16, bold=True))
    
    # 4 Model Panels in a 2x2 grid
    # Model 1: Anonymous Pipes & FDs (Top Left)
    frags.append(rect(25, 55, 370, 210, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(210, 80, "1. Анонімні пайпи та файлові дескриптори", size=13, color="#15803d", bold=True))
    frags.append(line(40, 92, 380, 92, color="#16a34a", sw=1))
    p1_lines = [
        "• pipe2(fd, O_CLOEXEC) створює односпрямований канал",
        "• Батько записує секрет і передає fd=3 дочірньому процесу",
        "• Секрет зчитується один раз і буфер занулюється",
        "• Відсутній у /proc/$PID/environ та argv",
        "• Інші дочірні процеси не отримують дескриптор"
    ]
    frags.append(mtext(40, 115, p1_lines, size=10.5, color="#14532d", anchor="start", lh=1.5))
    
    # Model 2: tmpfs / RAM Mounts (Top Right)
    frags.append(rect(425, 55, 370, 210, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=8))
    frags.append(text(610, 80, "2. Захищений tmpfs та Secret Mounts", size=13, color="#1d4ed8", bold=True))
    frags.append(line(440, 92, 780, 92, color="#2563eb", sw=1))
    p2_lines = [
        "• Монтування RAM-диска (tmpfs) з правами 0700/0600",
        "• Дані ніколи не скидаються на диск (no swap via mlock)",
        "• systemd LoadCredential= та K8s Secret Volumes",
        "• Додаток відкриває файл, читає й занулює пам'ять",
        "• Ізоляція через Mount Namespaces та права доступу"
    ]
    frags.append(mtext(440, 115, p2_lines, size=10.5, color="#1e3a8a", anchor="start", lh=1.5))
    
    # Model 3: memfd_create with Seals (Bottom Left)
    frags.append(rect(25, 285, 370, 210, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=8))
    frags.append(text(210, 310, "3. Анонімні memfd_create з пломбуванням", size=13, color="#7e22ce", bold=True))
    frags.append(line(40, 322, 380, 322, color="#9333ea", sw=1))
    p3_lines = [
        "• memfd_create(\"sec\", MFD_CLOEXEC | MFD_ALLOW_SEALING)",
        "• Пломби F_SEAL_WRITE | F_SEAL_GROW захищають буфер",
        "• Передача через Unix Domain Socket (SCM_RIGHTS)",
        "• Не має шляху у файловій системі (анонімний алокатор)",
        "• Читач гарантовано отримує незмінний зріз даних"
    ]
    frags.append(mtext(40, 345, p3_lines, size=10.5, color="#581c87", anchor="start", lh=1.5))
    
    # Model 4: Linux Kernel Keyrings (Bottom Right)
    frags.append(rect(425, 285, 370, 210, fill="#fff1f2", stroke="#e11d48", sw=1.5, rx=8))
    frags.append(text(610, 310, "4. Зв'язки ключів ядра (Kernel Keyrings)", size=13, color="#be123c", bold=True))
    frags.append(line(440, 322, 780, 322, color="#e11d48", sw=1))
    p4_lines = [
        "• Секрети зберігаються всередині ядра (add_key / request_key)",
        "• Ієрархія: Thread -> Process -> Session -> User Keyring",
        "• Захист від coredump (немає у віртуальній пам'яті процесу)",
        "• Гранулярні POSIX-права (read, write, search, link)",
        "• Автоматичне згасання секретів за таймаутом (TTL)"
    ]
    frags.append(mtext(440, 345, p4_lines, size=10.5, color="#881337", anchor="start", lh=1.5))
    
    path = os.path.join(img_dir, "secure-secret-delivery-models.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_leak_vectors(img_dir)
    render_secure_alternatives(img_dir)

if __name__ == '__main__':
    render()
