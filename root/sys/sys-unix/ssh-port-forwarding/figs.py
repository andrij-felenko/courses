import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))

from svgkit import render, textbox, fitbox, rect, text, line, arrow, circle, POS, NEG, FIELD, INK, MUTED, LINE, FILL

def generate_forwarding_types(img_dir):
    path = os.path.join(img_dir, 'ssh-forwarding-types.svg')
    w, h = 880, 520
    
    frags = []
    frags.append(text(w / 2, 28, "Три моделі прокидання портів у протоколі SSH", size=16, bold=True))
    
    # 1. Локальне прокидання (-L)
    frags.append(rect(30, 55, 820, 135, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(50, 80, "1. Локальне прокидання (-L local_port:remote_host:remote_port)", size=13, color="#1e293b", bold=True, anchor="start"))
    
    b1, _, _ = textbox(130, 130, "Клієнтський застосунок\n(psql localhost:5432)", size=11, fill="#e0f2fe", stroke="#0284c7")
    b2, _, _ = textbox(360, 130, "SSH-клієнт\nСлухає 127.0.0.1:5432", size=11, fill="#e0f2fe", stroke="#0284c7")
    b3, _, _ = textbox(590, 130, "SSH-сервер (Бастіон)\nШлюз у приватну мережу", size=11, fill="#fef3c7", stroke="#d97706")
    b4, _, _ = textbox(770, 130, "База даних (Ціль)\n10.0.1.5:5432", size=11, fill="#dcfce7", stroke="#16a34a")
    frags.extend([b1, b2, b3, b4])
    
    frags.append(arrow(205, 130, 275, 130, color="#0284c7", sw=2))
    frags.append(arrow(445, 130, 500, 130, color="#d97706", sw=2))
    frags.append(text(472, 118, "SSH (22)", size=10, color="#d97706", bold=True))
    frags.append(arrow(680, 130, 705, 130, color="#16a34a", sw=2))
    frags.append(text(692, 118, "TCP", size=10, color="#16a34a"))
    
    # 2. Віддалене прокидання (-R)
    frags.append(rect(30, 205, 820, 135, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(50, 230, "2. Віддалене (реверсивне) прокидання (-R remote_port:local_host:local_port)", size=13, color="#1e293b", bold=True, anchor="start"))
    
    r1, _, _ = textbox(130, 280, "Зовнішній клієнт\n(HTTP-запит з інтернету)", size=11, fill="#f1f5f9", stroke="#64748b")
    r2, _, _ = textbox(360, 280, "SSH-сервер (VPS)\nСлухає 0.0.0.0:8080", size=11, fill="#fef3c7", stroke="#d97706")
    r3, _, _ = textbox(590, 280, "SSH-клієнт\nПриймає forwarded-tcpip", size=11, fill="#e0f2fe", stroke="#0284c7")
    r4, _, _ = textbox(770, 280, "Локальний сервер\n127.0.0.1:3000", size=11, fill="#dcfce7", stroke="#16a34a")
    frags.extend([r1, r2, r3, r4])
    
    frags.append(arrow(210, 280, 265, 280, color="#64748b", sw=2))
    frags.append(text(238, 268, "TCP", size=10, color="#64748b"))
    frags.append(arrow(455, 280, 505, 280, color="#d97706", sw=2))
    frags.append(text(480, 268, "SSH (22)", size=10, color="#d97706", bold=True))
    frags.append(arrow(675, 280, 705, 280, color="#16a34a", sw=2))
    
    # 3. Динамічне прокидання (-D)
    frags.append(rect(30, 355, 820, 145, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(50, 380, "3. Динамічне прокидання (-D local_port) — SOCKS5-проксі", size=13, color="#1e293b", bold=True, anchor="start"))
    
    d1, _, _ = textbox(130, 435, "Браузер / curl\nSOCKS5: 127.0.0.1:1080", size=11, fill="#e0f2fe", stroke="#0284c7")
    d2, _, _ = textbox(360, 435, "SSH-клієнт\nДинамічний SOCKS-сервер", size=11, fill="#e0f2fe", stroke="#0284c7")
    d3, _, _ = textbox(590, 435, "SSH-сервер (Exit Node)\nВиконує connect() до цілей", size=11, fill="#fef3c7", stroke="#d97706")
    d4, _, _ = textbox(770, 435, "Будь-який сайт / API\nexample.com:443", size=11, fill="#dcfce7", stroke="#16a34a")
    frags.extend([d1, d2, d3, d4])
    
    frags.append(arrow(210, 435, 265, 435, color="#0284c7", sw=2))
    frags.append(text(238, 422, "SOCKS5", size=10, color="#0284c7"))
    frags.append(arrow(455, 435, 500, 435, color="#d97706", sw=2))
    frags.append(text(478, 422, "SSH (22)", size=10, color="#d97706", bold=True))
    frags.append(arrow(680, 435, 705, 435, color="#16a34a", sw=2))
    frags.append(text(692, 422, "TLS", size=10, color="#16a34a"))
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def generate_channel_multiplexing(img_dir):
    path = os.path.join(img_dir, 'ssh-channel-multiplexing.svg')
    w, h = 880, 430
    
    frags = []
    frags.append(text(w / 2, 28, "Мультиплексування логічних каналів у протоколі SSH (RFC 4254)", size=16, bold=True))
    
    # Хости
    h1, _, _ = textbox(130, 75, "SSH-клієнт\n(ssh user@server)", size=12, fill="#e0f2fe", stroke="#0284c7", bold=True)
    h2, _, _ = textbox(750, 75, "SSH-сервер\n(sshd daemon)", size=12, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.extend([h1, h2])
    
    # Загальна труба SSH Transport Layer
    frags.append(rect(230, 115, 420, 275, fill="#f1f5f9", stroke="#64748b", sw=2, rx=10))
    frags.append(text(440, 138, "Єдине зашифроване TCP-з'єднання (Порт 22)", size=12, color="#334155", bold=True))
    frags.append(text(440, 154, "SSH Transport Layer (AES-GCM / ChaCha20-Poly1305)", size=10, color="#64748b"))
    
    # Канал 0: Інтерактивна оболонка
    frags.append(rect(250, 175, 380, 60, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(265, 195, "Канал 0: session (Псевдотермінал /bin/bash)", size=11, color="#0284c7", bold=True, anchor="start"))
    frags.append(text(265, 215, "SSH_MSG_CHANNEL_DATA (stdin / stdout / stderr)", size=10, color=MUTED, anchor="start"))
    
    # Канал 1: Локальний тунель (direct-tcpip)
    frags.append(rect(250, 245, 380, 60, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(265, 265, "Канал 1: direct-tcpip (Прокидання 127.0.0.1:5432)", size=11, color="#16a34a", bold=True, anchor="start"))
    frags.append(text(265, 285, "Інкапсуляція TCP-потоку PostgreSQL у пакети SSH", size=10, color=MUTED, anchor="start"))
    
    # Канал 2: Віддалений тунель (forwarded-tcpip)
    frags.append(rect(250, 315, 380, 60, fill="#ffffff", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(265, 335, "Канал 2: forwarded-tcpip (Зворотний тунель 8080)", size=11, color="#d97706", bold=True, anchor="start"))
    frags.append(text(265, 355, "SSH_MSG_CHANNEL_WINDOW_ADJUST (Flow Control)", size=10, color=MUTED, anchor="start"))
    
    # З'єднувальні лінії
    frags.append(line(130, 105, 130, 345, color="#0284c7", sw=1.5, dash="4,4"))
    frags.append(line(750, 105, 750, 345, color="#d97706", sw=1.5, dash="4,4"))
    
    frags.append(arrow(130, 205, 245, 205, color="#0284c7", sw=1.5))
    frags.append(arrow(635, 205, 745, 205, color="#0284c7", sw=1.5))
    
    frags.append(arrow(130, 275, 245, 275, color="#16a34a", sw=1.5))
    frags.append(arrow(635, 275, 745, 275, color="#16a34a", sw=1.5))
    
    frags.append(arrow(745, 345, 635, 345, color="#d97706", sw=1.5))
    frags.append(arrow(245, 345, 130, 345, color="#d97706", sw=1.5))
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def generate_supervisor_lifecycle(img_dir):
    path = os.path.join(img_dir, 'ssh-tunnel-supervisor-lifecycle.svg')
    w, h = 880, 380
    
    frags = []
    frags.append(text(w / 2, 28, "Життєвий цикл та відновлення фонового SSH-тунелю", size=16, bold=True))
    
    # Кроки автомата станів
    s1, _, _ = textbox(120, 110, "1. Ініціалізація\nssh -N -f -L ...\nАвтентифікація", size=11, fill="#e0f2fe", stroke="#0284c7", bold=True)
    s2, _, _ = textbox(360, 110, "2. Активний тунель\nПорт слухається\nТрафік передається", size=11, fill="#dcfce7", stroke="#16a34a", bold=True)
    s3, _, _ = textbox(620, 110, "3. Зондування живості\nServerAliveInterval 15\nServerAliveCountMax 3", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    s4, _, _ = textbox(770, 240, "4. Виявлення обриву\nТаймаут відповіді\nssh завершує процес", size=11, fill="#fee2e2", stroke="#dc2626", bold=True)
    s5, _, _ = textbox(360, 310, "5. Автоматичний перезапуск\nsystemd Restart=always або\nautossh / супервізор", size=11, fill="#f3e8ff", stroke="#9333ea", bold=True)
    
    frags.extend([s1, s2, s3, s4, s5])
    
    # Переходи
    frags.append(arrow(185, 110, 285, 110, color="#0284c7", sw=2))
    frags.append(text(235, 98, "Успіх bind()", size=10, color="#0284c7"))
    
    frags.append(arrow(435, 110, 525, 110, color="#16a34a", sw=2))
    frags.append(text(480, 98, "Кожні 15 с", size=10, color="#16a34a"))
    
    frags.append(arrow(715, 110, 770, 195, color="#d97706", sw=2))
    frags.append(text(765, 150, "Немає ACK (45 с)", size=10, color="#dc2626"))
    
    frags.append(arrow(700, 260, 480, 310, color="#dc2626", sw=2))
    frags.append(text(595, 298, "SIGCHLD / Exit code != 0", size=10, color="#dc2626"))
    
    frags.append(arrow(260, 310, 120, 160, color="#9333ea", sw=2))
    frags.append(text(150, 260, "RestartSec=5s", size=10, color="#9333ea", bold=True))
    
    # Додатковий блок умови ExitOnForwardFailure
    tb_fail, _, _ = textbox(120, 210, "ExitOnForwardFailure=yes\nЯкщо порт зайнятий —\nмиттєвий вихід (exit 255)", size=10, fill="#fff1f2", stroke="#e11d48")
    frags.append(tb_fail)
    frags.append(arrow(120, 150, 120, 175, color="#e11d48", sw=1.5))
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    generate_forwarding_types(img_dir)
    generate_channel_multiplexing(img_dir)
    generate_supervisor_lifecycle(img_dir)

if __name__ == '__main__':
    main()
