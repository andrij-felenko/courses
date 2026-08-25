# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Поверхня атаки та методи її мінімізації'."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/programming/security/attack-surface)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_attack_surface_decomposition():
    """Фігура 1: Декомпозиція та виміри поверхні атаки."""
    w, h = 900, 490
    frags = []

    # Заголовок
    frags.append(text(450, 28, "Декомпозиція та складові поверхні атаки системи", size=18, bold=True))

    # Зона 1: Джерела загрози (ліворуч)
    frags.append(rect(15, 60, 200, 405, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(115, 85, "Джерела загрози", size=14, bold=True, color="#334155"))
    frags.append(text(115, 103, "(Недовірені суб'єкти)", size=12, color=MUTED))

    box1, _, _ = textbox(115, 150, "Відкрита мережа\n(HTTP / gRPC / DNS)", size=12, pad=8, fill="#fee2e2", stroke=POS, min_w=170)
    box2, _, _ = textbox(115, 240, "Локальні користувачі\n(CLI, файли, IPC)", size=12, pad=8, fill="#fef3c7", stroke="#d97706", min_w=170)
    box3, _, _ = textbox(115, 330, "Зовнішні носії й шини\n(USB, JTAG, порти)", size=12, pad=8, fill="#f3e8ff", stroke="#7e22ce", min_w=170)
    box4, _, _ = textbox(115, 415, "Сторонні залежності\n(Supply Chain)", size=12, pad=8, fill="#e2e8f0", stroke="#475569", min_w=170)
    frags.extend([box1, box2, box3, box4])

    # Зона 2: Поверхня атаки (Центр - червоний контур)
    frags.append(rect(230, 60, 440, 405, fill="#fff5f5", stroke=POS, sw=2, rx=8))
    frags.append(text(450, 85, "ПОВЕРХНЯ АТАКИ (Attack Surface)", size=15, bold=True, color=POS))
    frags.append(text(450, 103, "Сукупність усіх доступних точок входу, каналів та даних", size=11, color=MUTED))

    # 4 виміри поверхні атаки
    b_entry, _, _ = textbox(450, 145, "1. Точки входу й виходу (Entry/Exit Points)\nREST API, gRPC, CLI-аргументи, обробники сигналів", size=11, pad=8, fill=BG, stroke=LINE, min_w=390)
    b_chan, _, _ = textbox(450, 218, "2. Канали передачі даних (Channels)\nTCP/UDP порти, сокети Unix, черги повідомлень, IPC", size=11, pad=8, fill=BG, stroke=LINE, min_w=390)
    b_data, _, _ = textbox(450, 290, "3. Недовірені елементи даних (Untrusted Data Items)\nТіла запитів, JSON/XML, токени сесій, змінні оточення", size=11, pad=8, fill=BG, stroke=LINE, min_w=390)
    b_sys, _, _ = textbox(450, 362, "4. Системні виклики та драйвери (Syscalls & Drivers)\n450+ викликів ядра Linux, IOCTL, прямі дескриптори", size=11, pad=8, fill=BG, stroke=LINE, min_w=390)
    b_risk, _, _ = textbox(450, 424, "Рівень привілеїв: Unauth → Auth User → Admin → Root/Kernel", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True, min_w=390)
    frags.extend([b_entry, b_chan, b_data, b_sys, b_risk])

    # Зона 3: Захищені ресурси системи (Праворуч)
    frags.append(rect(685, 60, 200, 405, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(785, 85, "Захищені ресурси", size=14, bold=True, color=FIELD))
    frags.append(text(785, 103, "(Цільові активи)", size=12, color=MUTED))

    t1, _, _ = textbox(785, 150, "Пам'ять процесу\nі стан виконання", size=12, pad=8, fill=BG, stroke=LINE, min_w=170)
    t2, _, _ = textbox(785, 240, "Бази даних та\nфайлове сховище", size=12, pad=8, fill=BG, stroke=LINE, min_w=170)
    t3, _, _ = textbox(785, 330, "Криптографічні ключі\nй паролі доступу", size=12, pad=8, fill=BG, stroke=LINE, min_w=170)
    t4, _, _ = textbox(785, 415, "Привілеї ОС\n(Root / Ring 0)", size=12, pad=8, fill=BG, stroke=LINE, min_w=170)
    frags.extend([t1, t2, t3, t4])

    # Стрілки взаємодії
    frags.append(arrow(200, 150, 230, 145, color=POS, sw=2))
    frags.append(arrow(200, 240, 230, 218, color="#d97706", sw=2))
    frags.append(arrow(200, 330, 230, 290, color="#7e22ce", sw=2))
    frags.append(arrow(200, 415, 230, 362, color="#475569", sw=2))

    frags.append(arrow(670, 145, 685, 150, color=FIELD, sw=2))
    frags.append(arrow(670, 218, 685, 240, color=FIELD, sw=2))
    frags.append(arrow(670, 290, 685, 330, color=FIELD, sw=2))
    frags.append(arrow(670, 362, 685, 415, color=FIELD, sw=2))

    out_path = os.path.join(IMG_DIR, "attack-surface-decomposition.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_attack_surface_reduction_patterns():
    """Фігура 2: Чотири фундаментальні стовпи мінімізації поверхні атаки."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 28, "Чотири стратегії мінімізації поверхні атаки", size=18, bold=True))

    # Стовпець 1: Default Deny & Відключення
    c1, _, _ = textbox(125, 220, 
        "1. Заборона за дефолтом\n"
        "(Default Deny)\n\n"
        "• Закриті порти за дефолтом\n"
        "• Прив'язка до 127.0.0.1\n"
        "• Вимкнення legacy-протоколів\n"
        "• Зняття налагоджувальних ручок\n"
        "• Суворий білий список входів",
        size=12, pad=12, fill="#f8fafc", stroke=NEG, min_w=195)
    frags.append(rect(27, 70, 196, 32, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(125, 91, "ВИМКНЕННЯ ЕКСПОЗИЦІЇ", size=11, bold=True, color=NEG))
    frags.append(c1)

    # Стовпець 2: Розподіл привілеїв
    c2, _, _ = textbox(335, 220,
        "2. Розподіл привілеїв\n"
        "(Privilege Separation)\n\n"
        "• Відокремлення парсера від ядра\n"
        "• Непривілейовані воркери\n"
        "• Drop capabilities (setresuid)\n"
        "• Ізоляція просторів імен (unshare)\n"
        "• Вузький IPC замість моноліту",
        size=12, pad=12, fill="#f8fafc", stroke="#7e22ce", min_w=195)
    frags.append(rect(237, 70, 196, 32, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=6))
    frags.append(text(335, 91, "КОМПАРТМЕНТАЛІЗАЦІЯ", size=11, bold=True, color="#7e22ce"))
    frags.append(c2)

    # Стовпець 3: Звуження системних викликів
    c3, _, _ = textbox(545, 220,
        "3. Звуження API ядра\n"
        "(Syscall Constriction)\n\n"
        "• Seccomp-BPF фільтрація\n"
        "• Заборона execve, ptrace, socket\n"
        "• OpenBSD pledge() та unveil()\n"
        "• Landlock LSM обмеження ФС\n"
        "• Зниження з 450+ до 15 викликів",
        size=12, pad=12, fill="#f8fafc", stroke=FIELD, min_w=195)
    frags.append(rect(447, 70, 196, 32, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(545, 91, "САНДБОКСИНГ СИСТЕМНИХ ВИКЛИКІВ", size=10, bold=True, color=FIELD))
    frags.append(c3)

    # Стовпець 4: Очищення коду й залежностей
    c4, _, _ = textbox(755, 220,
        "4. Очищення залежностей\n"
        "(Code & Supply Shedding)\n\n"
        "• Dead code stripping (-Wl,--gc-sec)\n"
        "• Link-Time Optimization (LTO)\n"
        "• Відмова від небезпечних парсерів\n"
        "• Скорочення сторонніх пакетів\n"
        "• Типізовані схеми (Protobuf/TLV)",
        size=12, pad=12, fill="#f8fafc", stroke="#d97706", min_w=195)
    frags.append(rect(657, 70, 196, 32, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(755, 91, "УСУНЕННЯ ЗАЙВОГО КОДУ", size=11, bold=True, color="#d97706"))
    frags.append(c4)

    out_path = os.path.join(IMG_DIR, "attack-surface-reduction-patterns.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_privilege_separated_architecture():
    """Фігура 3: Архітектура сервісу з розподілом привілеїв та ізоляцією (Sandbox Model)."""
    w, h = 880, 440
    frags = []

    frags.append(text(440, 28, "Архітектура ізоляції та звуження поверхні атаки сервісу", size=18, bold=True))

    # Недовірена мережа
    b_net, _, _ = textbox(90, 200, "Недовірена мережа\n(Інтернет / Клієнти)\n\nСирий байтовий потік,\nневалідовані пакети", size=12, pad=10, fill="#fee2e2", stroke=POS, min_w=140)
    frags.append(b_net)

    # Непривілейований воркер-парсер (Sandbox)
    frags.append(rect(190, 70, 270, 340, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(325, 95, "Непривілейований пісочник", size=14, bold=True, color=POS))
    frags.append(text(325, 115, "(Network Receiver & Parser Worker)", size=11, color=MUTED))

    p1, _, _ = textbox(325, 160, "UID: nobody (65534) / No Capabilities", size=11, pad=6, fill=BG, stroke=LINE, min_w=240)
    p2, _, _ = textbox(325, 215, "Ізоляція: Unshare (Mount, Net, PID NS)", size=11, pad=6, fill=BG, stroke=LINE, min_w=240)
    p3, _, _ = textbox(325, 270, "Seccomp-BPF: дозволено лише\nread, write, exit_group, futex", size=11, pad=6, fill=BG, stroke=POS, bold=True, min_w=240)
    p4, _, _ = textbox(325, 345, "Парсер формату даних\n(Здійснює валідацію схеми й розмірів)", size=11, pad=6, fill=BG, stroke=LINE, min_w=240)
    frags.extend([p1, p2, p3, p4])

    # Вузький IPC канал
    frags.append(rect(480, 160, 110, 80, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(535, 185, "Вузький IPC", size=12, bold=True, color="#334155"))
    frags.append(text(535, 203, "Unix Pipe / Socket", size=10, color=MUTED))
    frags.append(text(535, 222, "Суворо типізований", size=10, color=FIELD))

    # Привілейоване захищене ядро / Менеджер
    frags.append(rect(610, 70, 250, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(735, 95, "Захищений координатор", size=14, bold=True, color=FIELD))
    frags.append(text(735, 115, "(Privileged Core / Manager)", size=11, color=MUTED))

    m1, _, _ = textbox(735, 160, "Виконує лише валідовані команди", size=11, pad=6, fill=BG, stroke=LINE, min_w=220)
    m2, _, _ = textbox(735, 220, "Прямий доступ до сховища\n(Keys, Database, Filesystem)", size=11, pad=6, fill=BG, stroke=LINE, min_w=220)
    m3, _, _ = textbox(735, 285, "Аудит та контроль сесій", size=11, pad=6, fill=BG, stroke=LINE, min_w=220)
    m4, _, _ = textbox(735, 350, "НЕ контактує з мережею напряму", size=11, pad=6, fill="#dcfce7", stroke=FIELD, bold=True, min_w=220)
    frags.extend([m1, m2, m3, m4])

    # Стрілки потоку
    frags.append(arrow(165, 200, 190, 200, color=POS, sw=2))
    frags.append(arrow(460, 200, 480, 200, color="#475569", sw=2))
    frags.append(arrow(590, 200, 610, 200, color=FIELD, sw=2))

    out_path = os.path.join(IMG_DIR, "privilege-separated-architecture.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == "__main__":
    fig_attack_surface_decomposition()
    fig_attack_surface_reduction_patterns()
    fig_privilege_separated_architecture()
