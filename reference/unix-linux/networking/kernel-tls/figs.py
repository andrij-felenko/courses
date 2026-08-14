import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

from svgkit import render, fitbox, rect, line, arrow, text, mtext, FILL, LINE, INK

def generate_figs():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # Figure 1: Architecture Comparison (User-space vs SW kTLS vs HW Offload)
    frags1 = []
    
    # Title
    frags1.append(text(500, 25, "Порівняння моделей обробки HTTPS трафіку у ядрі Linux", size=18, bold=True))

    # Column 1: Traditional User-space TLS
    frags1.append(rect(20, 50, 300, 440, fill="#fff5f5", stroke="#e53e3e", sw=2, rx=8))
    frags1.append(text(170, 75, "1. Традиційний User-Space TLS", size=14, bold=True, color="#9b2c2c"))
    
    frags1.append(fitbox(35, 100, 270, 50, "Файловий кеш (Page Cache)\n[Kernel Memory]", size=12, fill="#edf2f7", stroke="#cbd5e0"))
    frags1.append(fitbox(35, 175, 270, 55, "User-space Web-server\n'sys_read' -> Memory Copy #1\n(Буфер відкритого тексту)", size=11, fill="#feebc8", stroke="#dd6b20"))
    frags1.append(fitbox(35, 255, 270, 55, "TLS Бібліотека (OpenSSL)\n[Шифрування CPU User-space]\nФормування TLS записів", size=11, fill="#fed7d7", stroke="#e53e3e"))
    frags1.append(fitbox(35, 335, 270, 55, "Socket Buffer (sk_buff)\n'sys_write' -> Memory Copy #2\n(Буфер зашифрованого TCP)", size=11, fill="#feebc8", stroke="#dd6b20"))
    frags1.append(fitbox(35, 415, 270, 55, "Мережевий адаптер (NIC)\nПередача зашифрованих пакетів", size=11, fill="#e2e8f0", stroke="#4a5568"))

    frags1.append(arrow(170, 150, 170, 175, color="#e53e3e", sw=2))
    frags1.append(arrow(170, 230, 170, 255, color="#e53e3e", sw=2))
    frags1.append(arrow(170, 310, 170, 335, color="#e53e3e", sw=2))
    frags1.append(arrow(170, 390, 170, 415, color="#e53e3e", sw=2))

    # Column 2: SW kTLS
    frags1.append(rect(350, 50, 300, 440, fill="#ebf8ff", stroke="#3182ce", sw=2, rx=8))
    frags1.append(text(500, 75, "2. Software kTLS (Kernel TLS)", size=14, bold=True, color="#2b6cb0"))
    
    frags1.append(fitbox(365, 100, 270, 50, "Файловий кеш (Page Cache)\n[Kernel Memory]", size=12, fill="#edf2f7", stroke="#cbd5e0"))
    frags1.append(fitbox(365, 175, 270, 55, "User-space Web-server\n'sendfile(2)' Zero-Copy\n(Жодного копіювання в user)", size=11, fill="#ebf8ff", stroke="#3182ce"))
    frags1.append(fitbox(365, 255, 270, 55, "kTLS Engine (tls_sw_sendmsg)\n[Kernel Crypto API: AES-NI]\nШифрування в ядрі", size=11, fill="#bee3f8", stroke="#2b6cb0"))
    frags1.append(fitbox(365, 335, 270, 55, "Socket Buffer (sk_buff)\nЗашифровані TLS сторінки", size=11, fill="#e2e8f0", stroke="#4a5568"))
    frags1.append(fitbox(365, 415, 270, 55, "Мережевий адаптер (NIC)\nПередача TCP пакетів", size=11, fill="#e2e8f0", stroke="#4a5568"))

    frags1.append(arrow(500, 150, 500, 175, color="#3182ce", sw=2))
    frags1.append(arrow(500, 230, 500, 255, color="#3182ce", sw=2))
    frags1.append(arrow(500, 310, 500, 335, color="#3182ce", sw=2))
    frags1.append(arrow(500, 390, 500, 415, color="#3182ce", sw=2))

    # Column 3: HW kTLS Offload
    frags1.append(rect(680, 50, 300, 440, fill="#f0fff4", stroke="#38a169", sw=2, rx=8))
    frags1.append(text(830, 75, "3. Hardware kTLS Offload", size=14, bold=True, color="#276749"))
    
    frags1.append(fitbox(695, 100, 270, 50, "Файловий кеш (Page Cache)\n[Kernel Memory]", size=12, fill="#edf2f7", stroke="#cbd5e0"))
    frags1.append(fitbox(695, 175, 270, 55, "User-space Web-server\n'sendfile(2)' Zero-Copy", size=11, fill="#f0fff4", stroke="#38a169"))
    frags1.append(fitbox(695, 255, 270, 55, "kTLS Offload Manager\nФормування TLS записів\n0% CPU на шифрування!", size=11, fill="#c6f6d5", stroke="#276749"))
    frags1.append(fitbox(695, 335, 270, 55, "Socket Buffer (sk_buff)\nВідкритий текст + TLS заголовки", size=11, fill="#e2e8f0", stroke="#4a5568"))
    frags1.append(fitbox(695, 415, 270, 55, "SmartNIC (ConnectX-6/7)\n[Inline AES-GCM Crypto Engine]\nШифрування в кабелі 100+ Gbps", size=11, fill="#9ae6b4", stroke="#22543d"))

    frags1.append(arrow(830, 150, 830, 175, color="#38a169", sw=2))
    frags1.append(arrow(830, 230, 830, 255, color="#38a169", sw=2))
    frags1.append(arrow(830, 310, 830, 335, color="#38a169", sw=2))
    frags1.append(arrow(830, 390, 830, 415, color="#38a169", sw=2))

    render(os.path.join(img_dir, "ktls-architecture-comparison.svg"), 1000, 510, *frags1)

    # Figure 2: Socket Transformation & ULP Hooks
    frags2 = []
    frags2.append(text(425, 25, "Трансформація сокета при включенні ULP kTLS та підміна sk_prot", size=17, bold=True))

    # User Space Box
    frags2.append(rect(30, 50, 790, 70, fill="#edf2f7", stroke="#cbd5e0", sw=1.5, rx=6))
    frags2.append(text(425, 70, "ПРОСТІР КОРИСТУВАЧА (USER SPACE)", size=12, bold=True, color="#4a5568"))
    frags2.append(fitbox(45, 80, 760, 30, "setsockopt(fd, IPPROTO_TCP, TCP_ULP, \"tls\", 3)  -->  setsockopt(fd, SOL_TLS, TLS_TX, &keys, len)", size=11, fill="#edf2f7", stroke="#edf2f7"))

    frags2.append(arrow(425, 120, 425, 150, color="#4a5568", sw=2))

    # Kernel Space Box
    frags2.append(rect(30, 155, 790, 260, fill="#f7fafc", stroke="#a0aec0", sw=1.5, rx=6))
    frags2.append(text(425, 175, "ПРОСТІР ЯДРА (KERNEL SPACE / SOCKET LAYER)", size=12, bold=True, color="#2b6cb0"))

    # Struct sock
    frags2.append(rect(50, 195, 240, 205, fill="#ffffff", stroke="#3182ce", sw=2, rx=4))
    frags2.append(text(170, 215, "struct sock (inet_sk)", size=13, bold=True, color="#2b6cb0"))
    frags2.append(line(50, 225, 290, 225, color="#cbd5e0"))
    frags2.append(fitbox(55, 235, 230, 35, "sk_prot  -------->", size=12, color="#e53e3e", bold=True, fill="#fff5f5", stroke="#e53e3e"))
    frags2.append(fitbox(55, 280, 230, 35, "sk_user_data ---->", size=12, color="#3182ce", bold=True, fill="#ebf8ff", stroke="#3182ce"))
    frags2.append(fitbox(55, 325, 230, 65, "sk_write_space\nsk_data_ready\n(TCP Event Handlers)", size=11, color="#718096", fill="#f7fafc", stroke="#cbd5e0"))

    # Struct tls_prot / ops
    frags2.append(rect(320, 195, 230, 205, fill="#ebf8ff", stroke="#2b6cb0", sw=2, rx=4))
    frags2.append(text(435, 215, "struct proto tls_sw_prot", size=13, bold=True, color="#2b6cb0"))
    frags2.append(line(320, 225, 550, 225, color="#cbd5e0"))
    frags2.append(fitbox(325, 235, 220, 35, "sendmsg = tls_sw_sendmsg", size=11, bold=True, fill="#ffffff", stroke="#2b6cb0"))
    frags2.append(fitbox(325, 275, 220, 35, "recvmsg = tls_sw_recvmsg", size=11, bold=True, fill="#ffffff", stroke="#2b6cb0"))
    frags2.append(fitbox(325, 315, 220, 35, "splice_read = tls_sw_splice_read", size=11, fill="#ffffff", stroke="#cbd5e0"))
    frags2.append(fitbox(325, 355, 220, 35, "close = tls_sk_proto_close", size=11, fill="#ffffff", stroke="#cbd5e0"))

    # Struct tls_context
    frags2.append(rect(580, 195, 220, 205, fill="#f0fff4", stroke="#276749", sw=2, rx=4))
    frags2.append(text(690, 215, "struct tls_context", size=13, bold=True, color="#276749"))
    frags2.append(line(580, 225, 800, 225, color="#cbd5e0"))
    frags2.append(fitbox(585, 235, 210, 30, "tx_conf: SW / HW / INLINE", size=11, color="#276749", fill="#ffffff", stroke="#276749"))
    frags2.append(fitbox(585, 270, 210, 30, "rx_conf: SW / HW / INLINE", size=11, color="#276749", fill="#ffffff", stroke="#276749"))
    frags2.append(fitbox(585, 305, 210, 45, "struct crypto_aead *aead\n(AES-GCM Key & IV)", size=11, bold=True, fill="#ffffff", stroke="#276749"))
    frags2.append(fitbox(585, 355, 210, 35, "seq_number (TX/RX)\nTLS Record State", size=10, fill="#ffffff", stroke="#cbd5e0"))

    frags2.append(arrow(285, 252, 325, 252, color="#e53e3e", sw=2))
    frags2.append(arrow(285, 297, 585, 297, color="#3182ce", sw=2))

    render(os.path.join(img_dir, "ktls-sk-prot-hook.svg"), 850, 430, *frags2)

    # Figure 3: Inline SmartNIC Offload Flow
    frags3 = []
    frags3.append(text(450, 25, "Конвеєр апаратного розвантаження kTLS TX (NIC Inline Encryption Flow)", size=17, bold=True))

    # Step 1
    frags3.append(rect(30, 60, 250, 140, fill="#ffffff", stroke="#4a5568", sw=1.5, rx=6))
    frags3.append(text(155, 80, "1. Ядро (kTLS TX Driver)", size=13, bold=True, color="#2b6cb0"))
    frags3.append(line(30, 95, 280, 95, color="#cbd5e0"))
    frags3.append(fitbox(35, 105, 240, 85, "Формування SKB:\n- Заголовок TLS (5B)\n- Відкритий текст (Payload)\n- Позначка skb: 'tls_offload=1'", size=11, fill="#ffffff", stroke="#ffffff"))

    frags3.append(arrow(280, 130, 320, 130, color="#2b6cb0", sw=2))

    # Step 2
    frags3.append(rect(320, 60, 260, 140, fill="#ebf8ff", stroke="#3182ce", sw=1.5, rx=6))
    frags3.append(text(450, 80, "2. Передача в PCIe Ring", size=13, bold=True, color="#2b6cb0"))
    frags3.append(line(320, 95, 580, 95, color="#cbd5e0"))
    frags3.append(fitbox(325, 105, 250, 85, "Передача дескриптора пакета\nв чергу TX Ring адаптера.\nДані у буфері RAM\nЛИШАЮТЬСЯ ВІДКРИТИМИ!", size=11, fill="#ebf8ff", stroke="#ebf8ff"))

    frags3.append(arrow(580, 130, 620, 130, color="#3182ce", sw=2))

    # Step 3
    frags3.append(rect(620, 60, 250, 140, fill="#f0fff4", stroke="#276749", sw=2, rx=6))
    frags3.append(text(745, 80, "3. SmartNIC Crypto Engine", size=13, bold=True, color="#276749"))
    frags3.append(line(620, 95, 870, 95, color="#cbd5e0"))
    frags3.append(fitbox(625, 105, 240, 85, "Апаратне шифрування:\n- Ключ із контексту NIC\n- Обчислення AES-GCM tag\n- Відправка зашифрованого TCP", size=11, fill="#f0fff4", stroke="#f0fff4"))

    # Bottom explanation box
    frags3.append(rect(30, 220, 840, 110, fill="#feebc8", stroke="#dd6b20", sw=1.5, rx=6))
    frags3.append(text(450, 245, "🔑 Ключовий виграш продуктивності:", size=13, bold=True, color="#9c4221"))
    frags3.append(fitbox(40, 260, 820, 60, "Шифрування виконується безпосередньо у кремнії мережевої карти під час проходження байтів крізь апаратний FIFO буфер. Процесор (CPU) серверу взагалі не виконує криптографічних обчислень, що вивільняє 100% CPU для бізнес-логіки.", size=11, fill="#feebc8", stroke="#feebc8"))

    render(os.path.join(img_dir, "ktls-nic-offload-pipeline.svg"), 900, 350, *frags3)

if __name__ == "__main__":
    generate_figs()
