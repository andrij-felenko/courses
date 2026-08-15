# -*- coding: utf-8 -*-
import sys
import os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def generate_architecture():
    path = os.path.join(IMG_DIR, 'smack-architecture.svg')
    w, h = 760, 440
    frags = []

    # Outer border
    frags.append(rect(10, 10, 740, 420, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=8))

    # User Space Box
    frags.append(rect(30, 35, 700, 110, fill="#f0f7ff", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(380, 58, "Простір користувача (User Space)", size=15, color="#0969da", bold=True))
    
    # User processes
    box1, _, _ = textbox(160, 95, "Процес WebBrowser\n(cred->security = \"Web\")", size=12, fill="#ffffff", stroke="#0969da")
    box2, _, _ = textbox(600, 95, "Процес AudioDaemon\n(cred->security = \"Audio\")", size=12, fill="#ffffff", stroke="#0969da")
    frags.extend([box1, box2])

    # Syscall arrows
    frags.append(arrow(160, 145, 160, 185, color="#57606a"))
    frags.append(arrow(600, 145, 600, 185, color="#57606a"))
    frags.append(text(215, 168, "sys_open() / sys_write()", size=11, color="#57606a"))
    frags.append(text(510, 168, "sys_sendmsg() / socket", size=11, color="#57606a"))

    # Kernel Space Box
    frags.append(rect(30, 190, 700, 225, fill="#fff8f0", stroke="#bf8700", sw=1.5, rx=6))
    frags.append(text(380, 212, "Простір ядра (Kernel Space - VFS & LSM)", size=15, color="#bf8700", bold=True))

    # VFS / Socket Layer
    box_vfs, _, _ = textbox(380, 250, "VFS / Socket Layer (Перехоплення LSM хуками)", size=13, fill="#ffffff", stroke="#bf8700", bold=True)
    frags.append(box_vfs)

    # Hooks arrows down
    frags.append(arrow(380, 275, 380, 310, color="#1a1a1a"))
    frags.append(text(470, 295, "smack_inode_permission()", size=11, color="#1a1a1a"))

    # SMACK Core Module Box
    frags.append(rect(50, 320, 660, 80, fill="#f6f8fa", stroke="#24292f", sw=1.5, rx=6))
    frags.append(text(380, 340, "Модуль SMACK LSM (Security Engine)", size=14, color="#24292f", bold=True))

    # Internal components of SMACK
    sub1 = fitbox(65, 355, 190, 36, "Кеш правил / sysfs\nsmack_known", size=11, fill="#ffffff", stroke="#57606a")
    sub2 = fitbox(285, 355, 190, 36, "Атрибути файлів\nsecurity.SMACK64", size=11, fill="#ffffff", stroke="#57606a")
    sub3 = fitbox(505, 355, 190, 36, "Мережеві мітки\nCIPSO / NetLabel", size=11, fill="#ffffff", stroke="#57606a")
    frags.extend([sub1, sub2, sub3])

    render(path, w, h, *frags)

def generate_rule_evaluation():
    path = os.path.join(IMG_DIR, 'smack-rule-evaluation.svg')
    w, h = 760, 480
    frags = []

    frags.append(rect(10, 10, 740, 460, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(380, 32, "Алгоритм перевірки доступу SMACK LSM", size=16, bold=True))

    # Step 1: Input
    b1 = fitbox(40, 55, 680, 45, "Запит доступу: Суб'єкт (Subject Label) -> Об'єкт (Object Label) [Права: r/w/x/a/t/l]", size=13, fill="#eaf0fd", stroke="#2457d6", bold=True)
    frags.append(b1)

    frags.append(arrow(380, 100, 380, 125))

    # Step 2: Star check
    b2 = fitbox(160, 125, 440, 45, "Суб'єкт має мітку '*' (Star)?", size=13, fill="#fff8f0", stroke="#bf8700", bold=True)
    frags.append(b2)
    frags.append(arrow(600, 147, 660, 147))
    frags.append(text(625, 138, "Так", size=11, color="#c0392b", bold=True))
    frags.append(fitbox(660, 130, 80, 34, "ВІДМОВА", size=11, fill="#ffebe9", stroke="#c0392b", color="#c0392b", bold=True))

    frags.append(arrow(380, 170, 380, 195))
    frags.append(text(400, 185, "Ні", size=11, color="#c0392b", bold=True))

    # Step 3: Equal check or Floor check
    b3 = fitbox(160, 195, 440, 45, "Об'єкт '*' чи '@', збіг міток,\nабо лише r/x/l при об'єкті '_' або суб'єкті '^'?", size=12, fill="#fff8f0", stroke="#bf8700", bold=True)
    frags.append(b3)
    frags.append(arrow(600, 217, 660, 217))
    frags.append(text(625, 208, "Так", size=11, color="#27ae60", bold=True))
    frags.append(fitbox(660, 200, 70, 34, "ДОЗВІЛ", size=12, fill="#e6ffed", stroke="#27ae60", color="#1a7f37", bold=True))

    frags.append(arrow(380, 240, 380, 265))
    frags.append(text(400, 255, "Ні", size=11, color="#c0392b", bold=True))

    # Step 4: Table lookup
    b4 = fitbox(160, 265, 440, 50, "Пошук у таблиці правил завантаженої політики\n(smack_known_list -> Subject / Object)", size=12, fill="#f6f8fa", stroke="#24292f", bold=True)
    frags.append(b4)

    frags.append(arrow(380, 315, 380, 340))

    # Step 5: Rule match check
    b5 = fitbox(160, 340, 440, 45, "Знайдено правило і запрашивані маски rwxatb збігаються?", size=12, fill="#fff8f0", stroke="#bf8700", bold=True)
    frags.append(b5)

    # Granted branch
    frags.append(arrow(600, 362, 660, 362))
    frags.append(text(625, 353, "Так", size=11, color="#27ae60", bold=True))
    frags.append(fitbox(660, 345, 70, 34, "ДОЗВІЛ", size=12, fill="#e6ffed", stroke="#27ae60", color="#1a7f37", bold=True))

    # Denied branch
    frags.append(arrow(380, 385, 380, 415))
    frags.append(text(400, 400, "Ні", size=11, color="#c0392b", bold=True))
    b6 = fitbox(280, 415, 200, 40, "ВІДМОВА (-EACCES)", size=13, fill="#ffebe9", stroke="#c0392b", color="#c0392b", bold=True)
    frags.append(b6)

    render(path, w, h, *frags)

def generate_transmutation():
    path = os.path.join(IMG_DIR, 'smack-transmutation.svg')
    w, h = 760, 420
    frags = []

    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(380, 32, "Механізм трансмутації директорій (Directory Transmutation)", size=16, bold=True))

    # Directory box
    frags.append(rect(40, 60, 320, 320, fill="#f6f8fa", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(200, 85, "Батьківська директорія /var/shared", size=14, color="#0969da", bold=True))
    frags.append(rect(55, 100, 290, 75, fill="#ffffff", stroke="#0969da", sw=1))
    frags.append(text(200, 120, "security.SMACK64 = \"SharedData\"", size=12, bold=True))
    frags.append(text(200, 142, "security.SMACK64TRANSMUTE = \"TRUE\"", size=12, color="#c0392b", bold=True))
    frags.append(text(200, 162, "Правило: WebApp SharedData rwat", size=11, color="#27ae60", bold=True))

    # Process box
    frags.append(rect(420, 60, 300, 120, fill="#f0f7ff", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(570, 85, "Процес WebApp", size=14, color="#0969da", bold=True))
    frags.append(text(570, 115, "Контекст безпеки: \"WebApp\"", size=12, bold=True))
    frags.append(text(570, 140, "Виконує: open(\"data.txt\", O_CREAT)", size=12, color="#57606a"))

    # Arrow process -> dir creation (arrow on left side, text on right side)
    frags.append(arrow(470, 180, 470, 240, color="#1a1a1a"))
    frags.append(text(570, 210, "Створення нового файлу", size=12, color="#1a1a1a", anchor="start"))

    # Comparison / Result Boxes
    # Without transmutation
    frags.append(rect(400, 245, 160, 120, fill="#ffebe9", stroke="#c0392b", sw=1, rx=6))
    frags.append(text(480, 265, "Без трансмутації", size=12, color="#c0392b", bold=True))
    frags.append(text(480, 295, "Новий файл data.txt", size=11))
    frags.append(text(480, 315, "отримує мітку:", size=11))
    frags.append(text(480, 335, "\"WebApp\"", size=12, color="#c0392b", bold=True))

    # With transmutation
    frags.append(rect(570, 245, 160, 120, fill="#e6ffed", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(text(650, 265, "З трансмутацією (t)", size=12, color="#1a7f37", bold=True))
    frags.append(text(650, 295, "Новий файл data.txt", size=11))
    frags.append(text(650, 315, "успадковує мітку:", size=11))
    frags.append(text(650, 335, "\"SharedData\"", size=12, color="#1a7f37", bold=True))

    render(path, w, h, *frags)

if __name__ == '__main__':
    generate_architecture()
    generate_rule_evaluation()
    generate_transmutation()
    print("All SMACK SVG figures generated successfully.")
