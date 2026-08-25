import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_ss_vs_netstat_architecture(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 420, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 40, "Архітектурне порівняння: застарілий netstat проти сучасного ss", size=15, color="#263238", bold=True))

    # Left Column: netstat (/proc/net/tcp)
    frags.append(rect(35, 65, 345, 350, fill="#fff5f5", stroke="#e53935", sw=1.8, rx=6))
    frags.append(text(207, 92, "netstat (legacy /proc/net/tcp)", size=13, color="#c62828", bold=True))

    # Netstat flow boxes
    frags.append(rect(50, 115, 315, 55, fill="#ffffff", stroke="#ef9a9a", rx=4))
    frags.append(text(207, 137, "Ітератор seq_file у ядрі", size=11, color="#b71c1c", bold=True))
    frags.append(text(207, 155, "Захоплює спинлоки / RCU хеш-таблиць", size=10, color=INK))

    frags.append(arrow(207, 170, 207, 195, color="#e53935", sw=1.8))

    frags.append(rect(50, 195, 315, 60, fill="#ffffff", stroke="#ef9a9a", rx=4))
    frags.append(text(207, 217, "Текстове форматування sprintf()", size=11, color="#b71c1c", bold=True))
    frags.append(text(207, 237, "Генерація мільйонів ASCII-рядків у hex", size=10, color=INK))

    frags.append(arrow(207, 255, 207, 280, color="#e53935", sw=1.8))

    frags.append(rect(50, 280, 315, 65, fill="#ffffff", stroke="#ef9a9a", rx=4))
    frags.append(text(207, 302, "Читання userland буферами 4 КіБ", size=11, color="#b71c1c", bold=True))
    frags.append(text(207, 322, "Тисячі системних викликів read() + парсинг", size=10, color=INK))

    frags.append(rect(50, 355, 315, 45, fill="#ffebee", stroke="#e53935", rx=4))
    frags.append(text(207, 382, "Зависання на 10-30 с при 200k сокетах", size=11, color="#b71c1c", bold=True))

    # Right Column: ss (NETLINK_INET_DIAG)
    frags.append(rect(400, 65, 365, 350, fill="#f1f8e9", stroke="#43a047", sw=1.8, rx=6))
    frags.append(text(582, 92, "ss (iproute2 Netlink sock_diag)", size=13, color="#2e7d32", bold=True))

    # ss flow boxes
    frags.append(rect(415, 115, 335, 55, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(582, 137, "Бінарний запит inet_diag_req_v2", size=11, color="#1b5e20", bold=True))
    frags.append(text(582, 155, "Фільтрація станів сокетів у ядрі", size=10, color=INK))

    frags.append(arrow(582, 170, 582, 195, color="#43a047", sw=1.8))

    frags.append(rect(415, 195, 335, 60, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(582, 217, "Батчинг бінарних inet_diag_msg", size=11, color="#1b5e20", bold=True))
    frags.append(text(582, 237, "Компактні структури + TLV без тексту", size=10, color=INK))

    frags.append(arrow(582, 255, 582, 280, color="#43a047", sw=1.8))

    frags.append(rect(415, 280, 335, 65, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(582, 302, "Декілька викликів recvmsg()", size=11, color="#1b5e20", bold=True))
    frags.append(text(582, 322, "Вичитування повних сторінок пам'яті сокета", size=10, color=INK))

    frags.append(rect(415, 355, 335, 45, fill="#e8f5e9", stroke="#43a047", rx=4))
    frags.append(text(582, 382, "Миттєвий зріз за 2-5 мс без блокування ядра", size=11, color="#1b5e20", bold=True))

    render(path, 800, 445, *frags)

def build_tcp_socket_queues(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 420, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 40, "Анатомія черг TCP у виводі ss: слухаючі та встановлені з'єднання", size=15, color="#263238", bold=True))

    # Top Section: LISTEN Sockets
    frags.append(rect(35, 65, 730, 160, fill="#e3f2fd", stroke="#1976d2", sw=1.8, rx=6))
    frags.append(text(400, 90, "1. Слухаючі сокети (State: LISTEN, наприклад ss -ltn)", size=13, color="#0d47a1", bold=True))

    # Listen Recv-Q box
    frags.append(rect(55, 110, 330, 100, fill="#ffffff", stroke="#90caf9", rx=4))
    frags.append(text(220, 133, "Recv-Q = Поточна черга accept", size=12, color="#1565c0", bold=True))
    frags.append(text(220, 155, "Кількість завершених 3-way handshake", size=10, color=INK))
    frags.append(text(220, 175, "з'єднань, що чекають на accept() у застосунку", size=10, color=INK))
    frags.append(text(220, 195, "Зростання свідчить про зависання процесу", size=9, color="#c62828", bold=True))

    # Listen Send-Q box
    frags.append(rect(415, 110, 330, 100, fill="#ffffff", stroke="#90caf9", rx=4))
    frags.append(text(580, 133, "Send-Q = Максимальний ліміт backlog", size=12, color="#1565c0", bold=True))
    frags.append(text(580, 155, "Розмір черги повністю встановлених з'єднань:", size=10, color=INK))
    frags.append(text(580, 175, "min(backlog, /proc/sys/net/core/somaxconn)", size=10, color="#0d47a1", bold=True))
    frags.append(text(580, 195, "При Recv-Q > Send-Q нові клієнти відкидаються", size=9, color="#c62828", bold=True))

    # Bottom Section: ESTABLISHED Sockets
    frags.append(rect(35, 240, 730, 180, fill="#fff8e1", stroke="#ffa000", sw=1.8, rx=6))
    frags.append(text(400, 265, "2. Встановлені з'єднання (State: ESTAB, наприклад ss -tan)", size=13, color="#e65100", bold=True))

    # Estab Recv-Q box
    frags.append(rect(55, 285, 330, 120, fill="#ffffff", stroke="#ffe082", rx=4))
    frags.append(text(220, 308, "Recv-Q = Буфер прийому сокета (sk_receive_queue)", size=11, color="#e65100", bold=True))
    frags.append(text(220, 330, "Кількість байтів, які ядро прийняло з мережі,", size=10, color=INK))
    frags.append(text(220, 350, "але процес ще не вичитав через read()/recv()", size=10, color=INK))
    frags.append(text(220, 375, "Проблема: процес не встигає обробляти вхідні дані", size=9, color="#b71c1c", bold=True))

    # Estab Send-Q box
    frags.append(rect(415, 285, 330, 120, fill="#ffffff", stroke="#ffe082", rx=4))
    frags.append(text(580, 308, "Send-Q = Буфер відправки сокета (sk_write_queue)", size=11, color="#e65100", bold=True))
    frags.append(text(580, 330, "Кількість байтів, записаних процесом у сокет,", size=10, color=INK))
    frags.append(text(580, 350, "але ще не підтверджених (ACK) віддаленим вузлом", size=10, color=INK))
    frags.append(text(580, 375, "Проблема: затори в мережі, втрати або переповнення вузла", size=9, color="#b71c1c", bold=True))

    render(path, 800, 445, *frags)

def build_tcpdump_bpf_pipeline(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 410, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 40, "Конвеєр захоплення пакетів tcpdump: AF_PACKET, BPF та PACKET_MMAP", size=15, color="#263238", bold=True))

    # Kernel space container
    frags.append(rect(35, 65, 730, 210, fill="#e8eaf6", stroke="#3f51b5", sw=1.8, rx=6))
    frags.append(text(130, 90, "Простір ядра (Kernel Space)", size=12, color="#1a237e", bold=True))

    # Step 1: NIC & Driver
    frags.append(rect(50, 110, 150, 145, fill="#ffffff", stroke="#9fa8da", rx=4))
    frags.append(text(125, 135, "Мережевий адаптер", size=11, color="#283593", bold=True))
    frags.append(text(125, 155, "DMA в пам'ять", size=10, color=MUTED))
    frags.append(text(125, 180, "NAPI Softirq", size=10, color=INK))
    frags.append(text(125, 205, "netif_receive_skb()", size=10, color="#1a237e", bold=True))
    frags.append(text(125, 230, "dev_add_pack() хук", size=9, color=MUTED))

    frags.append(arrow(200, 180, 235, 180, color="#3f51b5", sw=2))

    # Step 2: In-kernel BPF Filter
    frags.append(rect(240, 110, 240, 145, fill="#fff3e0", stroke="#ff9800", sw=1.5, rx=4))
    frags.append(text(360, 135, "Ядерний фільтр BPF (JIT)", size=12, color="#e65100", bold=True))
    frags.append(text(360, 158, "Виконання фільтра на sk_buff", size=10, color=INK))
    frags.append(text(360, 180, "Байткод перевіряє заголовки", size=10, color=INK))
    frags.append(text(360, 202, "Миттєве відкидання (Drop len=0)", size=10, color="#c62828", bold=True))
    frags.append(text(360, 225, "Зрізання пакета до snaplen", size=9, color=MUTED))

    # Arrow to drop
    frags.append(arrow(360, 110, 360, 80, color="#c62828", sw=1.5))
    frags.append(text(360, 74, "Невідповідні пакети відкидаються", size=9, color="#c62828", bold=True))

    frags.append(arrow(480, 180, 515, 180, color="#3f51b5", sw=2))

    # Step 3: Ring Buffer PACKET_MMAP
    frags.append(rect(520, 110, 225, 145, fill="#ffffff", stroke="#9fa8da", rx=4))
    frags.append(text(632, 135, "PACKET_MMAP Ring Buffer", size=11, color="#283593", bold=True))
    frags.append(text(632, 160, "Кільцевий буфер rx_ring", size=10, color=INK))
    frags.append(text(632, 185, "Запис кадру без копіювання", size=10, color="#1b5e20", bold=True))
    frags.append(text(632, 210, "Зміна статусу TP_STATUS_USER", size=9, color=MUTED))
    frags.append(text(632, 230, "Оповіщення через poll()", size=9, color=MUTED))

    # Arrow Down to User Space
    frags.append(arrow(632, 255, 632, 305, color="#1b5e20", sw=2))

    # User space container
    frags.append(rect(35, 290, 730, 120, fill="#f1f8e9", stroke="#43a047", sw=1.8, rx=6))
    frags.append(text(130, 315, "Простір користувача (User Space)", size=12, color="#1b5e20", bold=True))

    # Step 4: libpcap & tcpdump
    frags.append(rect(240, 325, 505, 70, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(492, 348, "Бібліотека libpcap та процес tcpdump", size=12, color="#2e7d32", bold=True))
    frags.append(text(492, 368, "Пряме читання mmap-буфера → аналіз протоколів → запис у .pcap файл", size=10, color=INK))

    render(path, 800, 435, *frags)

def build_traceroute_ttl_mechanism(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 420, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 40, "Механізм зондування маршруту traceroute за допомогою поля IP TTL", size=15, color="#263238", bold=True))

    # Node boxes on top
    nodes = [
        (80, "Хост-відправник\n(traceroute)", "#e3f2fd", "#1976d2"),
        (280, "Маршрутизатор 1\n(Hop 1, R1)", "#f5f5f5", "#757575"),
        (480, "Маршрутизатор 2\n(Hop 2, R2)", "#f5f5f5", "#757575"),
        (680, "Цільовий вузол\n(Target Host)", "#e8f5e9", "#388e3c")
    ]
    for cx, label, fill_c, stroke_c in nodes:
        tb, _, _ = textbox(cx, 90, label, size=11, fill=fill_c, stroke=stroke_c, bold=True)
        frags.append(tb)

    # Hop 1: Probe TTL=1
    frags.append(line(50, 155, 750, 155, color="#e0e0e0", dash="4,4"))
    frags.append(arrow(80, 175, 260, 175, color="#1976d2", sw=1.8))
    frags.append(text(170, 168, "1. Зонд (TTL = 1)", size=10, color="#0d47a1", bold=True))

    frags.append(arrow(260, 195, 80, 195, color="#c62828", sw=1.8))
    frags.append(text(170, 210, "ICMP Time Exceeded (Type 11 Code 0) від R1", size=9, color="#b71c1c", bold=True))

    # Hop 2: Probe TTL=2
    frags.append(line(50, 230, 750, 230, color="#e0e0e0", dash="4,4"))
    frags.append(arrow(80, 250, 460, 250, color="#1976d2", sw=1.8))
    frags.append(text(270, 243, "2. Зонд (TTL = 2): R1 зменшує TTL до 1 і передає далі", size=10, color="#0d47a1", bold=True))

    frags.append(arrow(460, 270, 80, 270, color="#c62828", sw=1.8))
    frags.append(text(270, 285, "ICMP Time Exceeded (Type 11 Code 0) від R2", size=9, color="#b71c1c", bold=True))

    # Hop 3: Probe TTL=3 (Final Target)
    frags.append(line(50, 305, 750, 305, color="#e0e0e0", dash="4,4"))
    frags.append(arrow(80, 325, 660, 325, color="#1976d2", sw=1.8))
    frags.append(text(370, 318, "3. Зонд (TTL = 3): R1 та R2 зменшують TTL, пакет доходить до цілі", size=10, color="#0d47a1", bold=True))

    frags.append(arrow(660, 345, 80, 345, color="#2e7d32", sw=1.8))
    frags.append(text(370, 360, "Відповідь: ICMP Port Unreachable (UDP) / ICMP Echo Reply / TCP SYN-ACK", size=9, color="#1b5e20", bold=True))

    # Bottom summary box
    frags.append(rect(50, 380, 700, 32, fill="#f5f5f5", stroke="#bdbdbd", rx=4))
    frags.append(text(400, 401, "RTT для кожного хопа обчислюється як різниця часу між відправкою зонда та отриманням ICMP-відповіді", size=10, color=INK))

    render(path, 800, 445, *frags)

def render_all():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    build_ss_vs_netstat_architecture(os.path.join(img_dir, 'ss-vs-netstat-architecture.svg'))
    build_tcp_socket_queues(os.path.join(img_dir, 'tcp-socket-queues.svg'))
    build_tcpdump_bpf_pipeline(os.path.join(img_dir, 'tcpdump-bpf-pipeline.svg'))
    build_traceroute_ttl_mechanism(os.path.join(img_dir, 'traceroute-ttl-mechanism.svg'))

if __name__ == '__main__':
    render_all()
