import os
import sys

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від reference/unix-linux/observability/syslog-protocol)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_architecture():
    w, h = 860, 360
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 25, "Архітектура системи логування Syslog", size=16, bold=True))
    
    # Колонка 1: Джерела (Generators)
    frags.append(fitbox(30, 60, 220, 40, "Програми користувача\nsyslog(3) / libc", fill="#e8f0fe", stroke="#2457d6"))
    frags.append(fitbox(30, 120, 220, 40, "Ядро Linux\nprintk() / /proc/kmsg", fill="#e8f0fe", stroke="#2457d6"))
    frags.append(fitbox(30, 180, 220, 40, "Мережеві пристрої\nCisco, RouterOS, IoT", fill="#e8f0fe", stroke="#2457d6"))
    frags.append(fitbox(30, 240, 220, 40, "CLI інструмент\nlogger(1)", fill="#e8f0fe", stroke="#2457d6"))
    
    # Стрілки від джерел до транспорту
    frags.append(arrow(250, 80, 310, 110, color=LINE))
    frags.append(arrow(250, 140, 310, 130, color=LINE))
    frags.append(arrow(250, 200, 310, 230, color=LINE))
    frags.append(arrow(250, 260, 310, 240, color=LINE))
    
    # Колонка 2: Транспорт (Sockets / Network)
    frags.append(fitbox(310, 80, 200, 70, "Unix Datagram Socket\n/dev/log\n(AF_UNIX, local)", fill="#fff8e1", stroke="#f57f17"))
    frags.append(fitbox(310, 200, 200, 70, "Мережеві канали\nUDP 514 / TCP 6514\n(RFC 5426 / RFC 5425)", fill="#fff8e1", stroke="#f57f17"))
    
    # Стрілки від транспорту до демона
    frags.append(arrow(510, 115, 570, 150, color=LINE))
    frags.append(arrow(510, 235, 570, 180, color=LINE))
    
    # Колонка 3: Демон (Collector & Router)
    frags.append(fitbox(570, 100, 120, 140, "Маршрутизатор\n\nrsyslogd /\nsyslog-ng /\njournald\n\n(Правила та\nфільтрація)", fill="#e8f5e9", stroke="#27ae60"))
    
    # Стрілки від демона до призначення
    frags.append(arrow(690, 120, 730, 80, color=LINE))
    frags.append(arrow(690, 170, 730, 170, color=LINE))
    frags.append(arrow(690, 220, 730, 260, color=LINE))
    
    # Колонка 4: Призначення (Sinks)
    frags.append(fitbox(730, 60, 110, 40, "Локальні файли\n/var/log/*", fill="#f3e5f5", stroke="#8e24aa"))
    frags.append(fitbox(730, 150, 110, 40, "Центральний\nSyslog Server", fill="#f3e5f5", stroke="#8e24aa"))
    frags.append(fitbox(730, 240, 110, 40, "Консоль / Wall\n/dev/console", fill="#f3e5f5", stroke="#8e24aa"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'syslog-architecture.svg'), w, h, *frags)

def generate_priority_bitmath():
    w, h = 820, 280
    frags = []
    
    frags.append(text(w / 2, 25, "Анатомія значення PRIVAL (Упаковка Facility та Severity)", size=16, bold=True))
    
    # Байт з 8 бітів
    frags.append(text(120, 65, "Біти 7 .. 3: Facility (0 .. 23)", size=13, color="#2457d6", bold=True))
    frags.append(text(620, 65, "Біти 2 .. 0: Severity (0 .. 7)", size=13, color="#c0392b", bold=True))
    
    # 5 бітів Facility
    for i in range(5):
        bit_num = 7 - i
        x = 50 + i * 70
        frags.append(fitbox(x, 80, 65, 45, f"Bit {bit_num}\n[F]", fill="#e8f0fe", stroke="#2457d6"))
        
    # 3 біти Severity
    for i in range(3):
        bit_num = 2 - i
        x = 450 + i * 70
        frags.append(fitbox(x, 80, 65, 45, f"Bit {bit_num}\n[S]", fill="#fdecea", stroke="#c0392b"))
        
    # Формула під бітами
    frags.append(fitbox(50, 150, 720, 45, "Формула: PRIVAL = Facility * 8 + Severity   (або: (Facility << 3) | Severity)", fill="#f4f6f8", stroke="#333333", bold=True))
    
    # Приклад обчислення
    frags.append(fitbox(50, 210, 720, 50, "Приклад: Facility = authpriv (10), Severity = err (3)\nPRIVAL = 10 * 8 + 3 = 83  =>  Мережевий формат: <83>", fill="#e8f5e9", stroke="#27ae60"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'syslog-priority-bitmath.svg'), w, h, *frags)

def generate_rfc_comparison():
    w, h = 840, 310
    frags = []
    
    frags.append(text(w / 2, 25, "Порівняння форматів RFC 3164 (BSD) та RFC 5424 (IETF)", size=16, bold=True))
    
    # Блок RFC 3164
    frags.append(text(40, 65, "RFC 3164 (Застарілий BSD Syslog):", size=14, bold=True))
    frags.append(fitbox(40, 80, 80, 40, "<PRI>", fill="#e8f0fe", stroke="#2457d6"))
    frags.append(fitbox(125, 80, 160, 40, "TIMESTAMP\nOct 11 22:14:15", fill="#fff3e0", stroke="#e65100"))
    frags.append(fitbox(290, 80, 140, 40, "HOSTNAME\nmyhost", fill="#f3e5f5", stroke="#8e24aa"))
    frags.append(fitbox(435, 80, 150, 40, "TAG\nsshd[1234]:", fill="#e8f5e9", stroke="#27ae60"))
    frags.append(fitbox(590, 80, 210, 40, "MSG\nFailed password for root", fill="#f4f6f8", stroke="#333333"))
    
    # Блок RFC 5424
    frags.append(text(40, 165, "RFC 5424 (Сучасний Структурований Syslog):", size=14, bold=True))
    frags.append(fitbox(40, 180, 65, 40, "<PRI>", fill="#e8f0fe", stroke="#2457d6"))
    frags.append(fitbox(110, 180, 45, 40, "VER\n1", fill="#eceff1", stroke="#455a64"))
    frags.append(fitbox(160, 180, 195, 40, "TIMESTAMP (ISO 8601)\n2026-08-14T13:36:16.003Z", fill="#fff3e0", stroke="#e65100"))
    frags.append(fitbox(360, 180, 110, 40, "HOSTNAME\nhost.example", fill="#f3e5f5", stroke="#8e24aa"))
    frags.append(fitbox(475, 180, 85, 40, "APP-NAME\nsshd", fill="#e8f5e9", stroke="#27ae60"))
    frags.append(fitbox(565, 180, 65, 40, "PROCID\n1234", fill="#e8f5e9", stroke="#27ae60"))
    frags.append(fitbox(635, 180, 65, 40, "MSGID\nID47", fill="#e8f5e9", stroke="#27ae60"))
    
    # Другий рядок для STRUCTURED-DATA та MSG у RFC 5424
    frags.append(fitbox(40, 230, 395, 40, "STRUCTURED-DATA\n[exampleSDID@32473 iut=\"3\" eventSource=\"App\"]", fill="#ede7f6", stroke="#512da8"))
    frags.append(fitbox(440, 230, 360, 40, "MSG\nFailed password for root from 192.168.1.100", fill="#f4f6f8", stroke="#333333"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'syslog-rfc-comparison.svg'), w, h, *frags)

if __name__ == '__main__':
    generate_architecture()
    generate_priority_bitmath()
    generate_rfc_comparison()
