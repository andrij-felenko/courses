import os
import sys

# Шлях до scripts у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import text, mtext, rect, fitbox, line, BG, INK, MUTED, POS, LINE

def generate_fanotify_arch():
    w, h = 800, 480
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    # Зони (User Space vs Kernel Space)
    out.append(rect(20, 15, 760, 175, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    out.append(text(400, 38, "User Space (Користувацький простір)", size=13, color=MUTED, anchor="middle", bold=True))

    out.append(rect(20, 205, 760, 260, fill="#f1f5f9", stroke="#94a3b8", rx=8))
    out.append(text(400, 228, "Kernel Space (Ядро Linux & VFS)", size=13, color=MUTED, anchor="middle", bold=True))

    # Компоненти User Space
    # 1. Процес-клієнт
    out.append(fitbox(40, 60, 180, 70, ["Прикладний процес", "open('/data/file.exe')"], fill="#e2e8f0", stroke="#64748b", size=13))

    # 2. Демон безпеки
    out.append(fitbox(580, 60, 190, 70, ["Демон безпеки", "(Security Daemon / AV)", "читає / відповідає"], fill="#dcfce7", stroke="#16a34a", size=13))

    # Компоненти Kernel Space
    # 3. VFS системний виклик
    out.append(fitbox(40, 260, 180, 80, ["VFS sys_open()", "do_dentry_open()", "Перехоплення fsnotify"], fill="#e0f2fe", stroke="#0284c7", size=13))

    # 4. fanotify черга та снага очікування
    out.append(fitbox(290, 260, 220, 80, ["Підсистема fanotify", "Черга подій & wait_event", "Блокування виклику"], fill="#fef3c7", stroke="#d97706", size=13))

    # 5. Сокет / fd підписки
    out.append(fitbox(580, 260, 190, 80, ["fanotify fd", "read(event) / write(resp)", "FAN_ALLOW / FAN_DENY"], fill="#dcfce7", stroke="#16a34a", size=13))

    # Стрілки та підписи
    # 1. Процес ініціює open (ліва стрілка)
    out.append(line(75, 130, 75, 260, color=LINE, sw=2))
    out.append(text(80, 160, "1. sys_open", size=11, color=LINE, anchor="start", bold=True))

    # 2. VFS переходить у fanotify і блокується
    out.append(line(220, 280, 290, 280, color="#0284c7", sw=2))
    out.append(text(255, 268, "2. fsnotify", size=11, color="#0284c7", anchor="middle"))

    # 3. Подія передається до fanotify fd
    out.append(line(510, 280, 580, 280, color="#d97706", sw=2))
    out.append(text(545, 268, "3. Event", size=11, color="#d97706", anchor="middle"))

    # 4. Демон читає подія з fd
    out.append(line(610, 260, 610, 130, color="#16a34a", sw=2))
    out.append(text(605, 185, "4. read()", size=11, color="#16a34a", anchor="end", bold=True))

    # 5. Демон надсилає відповідь FAN_ALLOW / FAN_DENY
    out.append(line(740, 130, 740, 260, color=POS, sw=2))
    out.append(text(745, 185, "5. write()", size=11, color=POS, anchor="start", bold=True))

    # 6. Врозблокування
    out.append(line(290, 320, 220, 320, color=LINE, sw=2))
    out.append(text(255, 335, "6. Wakeup", size=11, color=LINE, anchor="middle"))

    # 7. Повернення в процес (права стрілка клієнта)
    out.append(line(185, 260, 185, 130, color=LINE, sw=2))
    out.append(text(180, 210, "7. return", size=11, color=LINE, anchor="end", bold=True))

    out.append('</svg>')
    return '\n'.join(out)

def generate_pre_content_hsm():
    w, h = 800, 420
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(400, 30, "Ієрархія класів дозволів: HSM підведення та Перевірка безпеки", size=15, color=INK, anchor="middle", bold=True))

    # Крок 1: VFS
    out.append(fitbox(30, 80, 180, 80, ["1. Операція VFS", "open('/mnt/hsm/doc.pdf')", "Запит до файлу"], fill="#e2e8f0", stroke="#64748b", size=13))

    # Крок 2: PRE_CONTENT
    out.append(fitbox(270, 80, 220, 80, ["2. PRE_CONTENT", "HSM / Cloud Hydration", "Завантаження на диск"], fill="#fef3c7", stroke="#d97706", size=13))

    # Крок 3: CONTENT
    out.append(fitbox(550, 80, 220, 80, ["3. CONTENT", "Security / AV Inspection", "Сканування вмісту"], fill="#dcfce7", stroke="#16a34a", size=13))

    # Крок 4: Фінал Дозволено
    out.append(fitbox(270, 280, 220, 80, ["4. Доступ надано", "Процес читає вміст", "Повернення fd"], fill="#e0f2fe", stroke="#0284c7", size=13))

    # Крок 5: Заблоковано
    out.append(fitbox(550, 280, 220, 80, ["Заблоковано (DENY)", "Повернення -EPERM", "Операція скасована"], fill="#fee2e2", stroke="#dc2626", size=13))

    # Стрілки
    out.append(line(210, 120, 270, 120, color=LINE, sw=2))
    out.append(text(240, 105, "fsnotify", size=11, color=LINE, anchor="middle"))

    out.append(line(490, 120, 550, 120, color="#d97706", sw=2))
    out.append(text(520, 105, "ALLOW", size=11, color="#d97706", anchor="middle"))

    # Від PRE_CONTENT вниз або від CONTENT до дозволу/відмови
    # Обидва вердикти виносить клас CONTENT — доступ надається лише після сканування
    out.append(line(600, 160, 600, 230, color="#16a34a", sw=2))
    out.append(line(600, 230, 380, 230, color="#16a34a", sw=2))
    out.append(line(380, 230, 380, 280, color="#16a34a", sw=2))
    out.append(text(470, 214, "FAN_ALLOW", size=11, color="#16a34a", anchor="middle", bold=True))

    out.append(line(700, 160, 700, 280, color="#dc2626", sw=2))
    out.append(text(710, 214, "FAN_DENY", size=11, color="#dc2626", anchor="start", bold=True))

    out.append('</svg>')
    return '\n'.join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    arch_svg = generate_fanotify_arch()
    with open(os.path.join(img_dir, 'fanotify-arch.svg'), 'w', encoding='utf-8') as f:
        f.write(arch_svg)
    print("Generated img/fanotify-arch.svg")

    hsm_svg = generate_pre_content_hsm()
    with open(os.path.join(img_dir, 'pre-content-hsm.svg'), 'w', encoding='utf-8') as f:
        f.write(hsm_svg)
    print("Generated img/pre-content-hsm.svg")

if __name__ == '__main__':
    main()
