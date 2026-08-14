#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_arch():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(out_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "wireguard-architecture.svg")

    frags = [
        # Userspace block
        svgkit.rect(30, 45, 740, 65, fill="#eef6fc", stroke="#2457d6", sw=1.5, rx=8),
        svgkit.text(400, 65, "Простір користувача (User Space)", size=13, bold=True, color="#2457d6"),
        svgkit.fitbox(50, 75, 200, 26, "Утиліта wg / iproute2", size=11, fill="#ffffff", stroke="#2457d6"),
        svgkit.fitbox(270, 75, 220, 26, "systemd-networkd / NetworkManager", size=11, fill="#ffffff", stroke="#2457d6"),
        svgkit.fitbox(510, 75, 240, 26, "Прикладне ПЗ (браузер, SSH, VPN app)", size=11, fill="#ffffff", stroke="#2457d6"),

        # Netlink & Socket Arrows
        svgkit.arrow(150, 110, 150, 145, color="#1a1a1a", sw=1.5),
        svgkit.fitbox(160, 118, 140, 20, "Generic Netlink (wg)", size=10, fill="#ffffff", stroke="#6b7280"),

        svgkit.arrow(630, 110, 630, 145, color="#1a1a1a", sw=1.5),
        svgkit.fitbox(500, 118, 120, 20, "Системний виклик (skb)", size=10, fill="#ffffff", stroke="#6b7280"),

        # Kernel space container
        svgkit.rect(30, 145, 740, 275, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=8),
        svgkit.text(400, 165, "Ядро Linux: віртуальний пристрій та модуль WireGuard", size=13, bold=True, color="#1a1a1a"),

        # wg0 interface block
        svgkit.rect(50, 180, 250, 115, fill="#ffffff", stroke="#27ae60", sw=1.5, rx=6),
        svgkit.text(175, 198, "Мережевий пристрій wg0", size=12, bold=True, color="#27ae60"),
        svgkit.text(175, 214, "struct net_device + netdev_ops", size=10, color="#6b7280"),
        svgkit.fitbox(60, 224, 230, 62, "wg_xmit(): обробка вихідних пакетів\nwg_receive(): обробка вхідних UDP\nUDP Tunnel Listener (порт 51820)", size=10, fill="#eafaf1", stroke="#27ae60"),

        # Cryptokey Routing block
        svgkit.rect(320, 180, 210, 115, fill="#ffffff", stroke="#c0392b", sw=1.5, rx=6),
        svgkit.text(425, 198, "Cryptokey Routing", size=12, bold=True, color="#c0392b"),
        svgkit.text(425, 214, "struct allowedips (Radix Tree)", size=10, color="#6b7280"),
        svgkit.fitbox(330, 224, 190, 62, "LPM пошук за Dest IP -> Peer\nПеревірка Src IP на вході\nДинамічна авто-роумінг оновлення", size=10, fill="#fdecea", stroke="#c0392b"),

        # Parallel Crypto Queue block
        svgkit.rect(550, 180, 200, 115, fill="#ffffff", stroke="#8e44ad", sw=1.5, rx=6),
        svgkit.text(650, 198, "Крипто-конвеєр padata", size=12, bold=True, color="#8e44ad"),
        svgkit.text(650, 214, "Per-CPU Workqueues", size=10, color="#6b7280"),
        svgkit.fitbox(560, 224, 180, 62, "ChaCha20-Poly1305 AEAD\nBLAKE2s / Curve25519\nЗбереження порядку пакетів", size=10, fill="#f3e8f9", stroke="#8e44ad"),

        # Connections inside kernel
        svgkit.arrow(300, 237, 320, 237, color="#1a1a1a", sw=1.5),
        svgkit.arrow(530, 237, 550, 237, color="#1a1a1a", sw=1.5),

        # Stack output block
        svgkit.rect(50, 315, 700, 85, fill="#ffffff", stroke="#333333", sw=1.5, rx=6),
        svgkit.text(400, 333, "Нижній мережевий стек та сокети UDP", size=12, bold=True),
        svgkit.fitbox(70, 345, 210, 45, "udp_tunnel_xmit_skb()\nІнкапсуляція в UDP", size=11, fill="#f4f6f8", stroke="#333333"),
        svgkit.fitbox(300, 345, 200, 45, "Таблиця маршрутів (FIB)\nПошук фізичного пристрою", size=11, fill="#f4f6f8", stroke="#333333"),
        svgkit.fitbox(520, 345, 210, 45, "Фізичний NIC (eth0 / wlan0)\ndev_queue_xmit()", size=11, fill="#f4f6f8", stroke="#333333"),

        svgkit.arrow(280, 367, 300, 367, color="#1a1a1a", sw=1.5),
        svgkit.arrow(500, 367, 520, 367, color="#1a1a1a", sw=1.5),
        svgkit.arrow(650, 295, 650, 315, color="#1a1a1a", sw=1.5),
    ]

    svgkit.render(path, 800, 440, *frags, title="Архітектура підсистеми WireGuard у ядрі Linux")

def render_flow():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(out_dir, "img")
    path = os.path.join(img_dir, "wireguard-packet-flow.svg")

    frags = [
        # Outbound flow header
        svgkit.rect(30, 45, 740, 160, fill="#f4f6f8", stroke="#2457d6", sw=1.5, rx=8),
        svgkit.text(400, 65, "Вихідний шлях (Outbound TX Path: skb -> wg0 -> eth0)", size=13, bold=True, color="#2457d6"),

        svgkit.fitbox(45, 85, 135, 45, "1. wg_xmit()\nОтримання skb", size=10, fill="#ffffff", stroke="#2457d6"),
        svgkit.arrow(180, 107, 200, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(200, 85, 145, 45, "2. allowedips_lookup()\nLPM пошук піра", size=10, fill="#ffffff", stroke="#c0392b"),
        svgkit.arrow(345, 107, 365, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(365, 85, 145, 45, "3. padata_do_parallel()\nШифрування ChaCha20", size=10, fill="#ffffff", stroke="#8e44ad"),
        svgkit.arrow(510, 107, 530, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(530, 85, 135, 45, "4. UDP encapsulation\nЗаголовок 8 байт", size=10, fill="#ffffff", stroke="#333333"),

        svgkit.arrow(665, 107, 690, 107, color="#1a1a1a", sw=1.5),
        svgkit.arrow(690, 107, 690, 145, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(510, 145, 230, 40, "5. iptunnel_xmit() -> eth0\nВідправка у мережу", size=10, fill="#eafaf1", stroke="#27ae60"),

        # Inbound flow header
        svgkit.rect(30, 225, 740, 160, fill="#f4f6f8", stroke="#c0392b", sw=1.5, rx=8),
        svgkit.text(400, 245, "Вхідний шлях (Inbound RX Path: eth0 -> UDP -> wg0)", size=13, bold=True, color="#c0392b"),

        svgkit.fitbox(45, 265, 145, 45, "1. wg_receive()\nОтримання UDP 51820", size=10, fill="#ffffff", stroke="#333333"),
        svgkit.arrow(190, 287, 210, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(210, 265, 145, 45, "2. padata_do_parallel()\nДешифрація Poly1305", size=10, fill="#ffffff", stroke="#8e44ad"),
        svgkit.arrow(355, 287, 375, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(375, 265, 145, 45, "3. allowedips_lookup()\nПеревірка Src IP (Anti-Spoof)", size=10, fill="#ffffff", stroke="#c0392b"),
        svgkit.arrow(520, 287, 540, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(540, 265, 135, 45, "4. wg_netif_rx()\nПередача в ядро", size=10, fill="#ffffff", stroke="#2457d6"),

        svgkit.arrow(675, 287, 695, 287, color="#1a1a1a", sw=1.5),
        svgkit.arrow(695, 287, 695, 325, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(490, 325, 250, 40, "5. Оновлення Endpoint (Auto-roaming)\nДоставка сокету застосунку", size=10, fill="#eafaf1", stroke="#27ae60"),
    ]

    svgkit.render(path, 800, 400, *frags, title="Конвеєр обробки пакетів WireGuard у мережевому стеку")

def render_handshake():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(out_dir, "img")
    path = os.path.join(img_dir, "wireguard-noise-handshake.svg")

    frags = [
        # Peer A column
        svgkit.rect(50, 45, 220, 330, fill="#eef6fc", stroke="#2457d6", sw=1.5, rx=8),
        svgkit.text(160, 65, "Ініціатор (Peer A)", size=12, bold=True, color="#2457d6"),
        svgkit.fitbox(60, 80, 200, 50, "Генерація ефемерного ключа (e_a)\nDH(e_a, s_b), DH(s_a, s_b)\nСтворення MAC1 та MAC2", size=9, fill="#ffffff", stroke="#2457d6"),

        # Peer B column
        svgkit.rect(530, 45, 220, 330, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=8),
        svgkit.text(640, 65, "Відповідач (Peer B)", size=12, bold=True, color="#27ae60"),
        svgkit.fitbox(540, 80, 200, 50, "Перевірка MAC1 / MAC2\nДешифрація статичного ключа A\nПеревірка таймштампу", size=9, fill="#ffffff", stroke="#27ae60"),

        # Message 1 Arrow: Initiation
        svgkit.arrow(270, 150, 530, 150, color="#2457d6", sw=2.0),
        svgkit.text(400, 142, "1. Handshake Initiation (148 байт)", size=11, bold=True, color="#2457d6"),
        svgkit.fitbox(310, 155, 180, 22, "msg_type=1, unencrypted_ephemeral, MAC1, MAC2", size=9, fill="#ffffff", stroke="#2457d6"),

        # Intermediate calc B
        svgkit.fitbox(540, 195, 200, 45, "Генерація ефемерного ключа (e_b)\nDH(e_a, e_b), DH(s_a, e_b)\nОбчислення симетричних ключів", size=9, fill="#ffffff", stroke="#27ae60"),

        # Message 2 Arrow: Response
        svgkit.arrow(530, 260, 270, 260, color="#27ae60", sw=2.0),
        svgkit.text(400, 252, "2. Handshake Response (92 байта)", size=11, bold=True, color="#27ae60"),
        svgkit.fitbox(310, 265, 180, 22, "msg_type=2, unencrypted_ephemeral, MAC1, MAC2", size=9, fill="#ffffff", stroke="#27ae60"),

        # Final key activation
        svgkit.fitbox(60, 290, 200, 45, "Фіналізація сесійних ключів\nКлюч запису (sending_key)\nКлюч читання (receiving_key)", size=9, fill="#ffffff", stroke="#2457d6"),
        svgkit.fitbox(540, 290, 200, 45, "Фіналізація сесійних ключів\nКлюч читання (receiving_key)\nКлюч запису (sending_key)", size=9, fill="#ffffff", stroke="#27ae60"),

        # DoS Cookie block at bottom
        svgkit.rect(50, 390, 700, 45, fill="#fdecea", stroke="#c0392b", sw=1.5, rx=6),
        svgkit.text(400, 408, "Механізм захисту від DoS-атак (Cookie Reply / MAC2)", size=11, bold=True, color="#c0392b"),
        svgkit.text(400, 424, "При високому навантаженні процесора Відповідач надсилає Cookie (64B), вимагаючи MAC2 підтвердження IP", size=9, color="#6b7280"),
    ]

    svgkit.render(path, 800, 450, *frags, title="Протокол рукостискання Noise_IK та обмін ключами")

def main():
    render_arch()
    render_flow()
    render_handshake()

if __name__ == "__main__":
    main()
