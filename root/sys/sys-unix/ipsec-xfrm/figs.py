import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_arch():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(out_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "xfrm-architecture.svg")

    frags = [
        # User space block
        svgkit.rect(30, 45, 740, 60, fill="#eef6fc", stroke="#2457d6", sw=1.5, rx=8),
        svgkit.text(400, 65, "Простір користувача (User Space)", size=13, bold=True, color="#2457d6"),
        svgkit.fitbox(50, 72, 210, 26, "IKE-демон (strongSwan / LibreSwan)", size=11, fill="#ffffff", stroke="#2457d6"),
        svgkit.fitbox(280, 72, 200, 26, "Утиліта iproute2 (ip xfrm)", size=11, fill="#ffffff", stroke="#2457d6"),
        svgkit.fitbox(500, 72, 250, 26, "Прикладні сокети (TCP / UDP)", size=11, fill="#ffffff", stroke="#2457d6"),

        # Netlink arrow
        svgkit.arrow(275, 105, 275, 140, color="#1a1a1a", sw=1.8),
        svgkit.fitbox(285, 112, 170, 20, "Netlink (NETLINK_XFRM)", size=10, fill="#ffffff", stroke="#6b7280"),

        # Kernel space block
        svgkit.rect(30, 145, 740, 275, fill="#f4f6f8", stroke="#333333", sw=1.5, rx=8),
        svgkit.text(400, 165, "Ядро Linux: підсистема XFRM та мережевий стек", size=13, bold=True, color="#1a1a1a"),

        # SPD Box
        svgkit.rect(50, 180, 310, 110, fill="#ffffff", stroke="#27ae60", sw=1.5, rx=6),
        svgkit.text(205, 198, "База політик безпеки (SPD)", size=12, bold=True, color="#27ae60"),
        svgkit.text(205, 216, "Таблиця xfrm_policy", size=11, color="#6b7280"),
        svgkit.fitbox(60, 226, 290, 54, "Селектори: IP джерела/призначення, порти, протокол\nДія: XFRM_POLICY_ALLOW / BLOCK / PASS\nНапрямок: IN / OUT / FORWARD", size=10, fill="#eafaf1", stroke="#27ae60"),

        # SAD Box
        svgkit.rect(420, 180, 330, 110, fill="#ffffff", stroke="#c0392b", sw=1.5, rx=6),
        svgkit.text(585, 198, "База станів безпеки (SAD)", size=12, bold=True, color="#c0392b"),
        svgkit.text(585, 216, "Хеш-таблиця xfrm_state", size=11, color="#6b7280"),
        svgkit.fitbox(430, 226, 310, 54, "Ідентифікатор: SPI + Dst IP + Протокол (ESP/AH)\nАлгоритми: шифрування (AES), цілісність (HMAC)\nРежим: Tunnel / Transport, Seq counter", size=10, fill="#fdecea", stroke="#c0392b"),

        # Pointer Arrow between SPD and SAD
        svgkit.arrow(360, 235, 420, 235, color="#1a1a1a", sw=1.5),
        svgkit.text(390, 228, "tmpl", size=10, color="#6b7280"),

        # Network path / Core XFRM lookup
        svgkit.rect(50, 310, 700, 95, fill="#ffffff", stroke="#333333", sw=1.5, rx=6),
        svgkit.text(400, 328, "Маршрутизація та обробка пакетів (sk_buff)", size=12, bold=True),
        svgkit.fitbox(70, 342, 190, 48, "Пошук маршруту (FIB)\nКеш dst_entry", size=11, fill="#f4f6f8", stroke="#333333"),
        svgkit.fitbox(300, 342, 200, 48, "xfrm_lookup()\nПрив'язка xfrm_dst", size=11, fill="#f4f6f8", stroke="#333333"),
        svgkit.fitbox(540, 342, 190, 48, "Crypto API\n(AES-GCM / HMAC-SHA2)", size=11, fill="#f4f6f8", stroke="#333333"),

        svgkit.arrow(260, 366, 300, 366, color="#1a1a1a", sw=1.5),
        svgkit.arrow(500, 366, 540, 366, color="#1a1a1a", sw=1.5),

        # Connection lines between SPD/SAD and lookup
        svgkit.arrow(205, 290, 205, 342, color="#27ae60", sw=1.5),
        svgkit.arrow(585, 290, 585, 342, color="#c0392b", sw=1.5),
    ]

    svgkit.render(path, 800, 440, *frags, title="Архітектура підсистеми XFRM у ядрі Linux")

def render_flow():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "img", "xfrm-packet-flow.svg")

    frags = [
        # Outbound flow header
        svgkit.rect(30, 45, 740, 160, fill="#f4f6f8", stroke="#2457d6", sw=1.5, rx=8),
        svgkit.text(400, 65, "Вихідний трафік (Outbound TX Path)", size=13, bold=True, color="#2457d6"),

        svgkit.fitbox(50, 85, 140, 45, "1. Socket sendmsg\nip_output()", size=10, fill="#ffffff", stroke="#2457d6"),
        svgkit.arrow(190, 107, 220, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(220, 85, 150, 45, "2. xfrm_lookup()\nПеревірка SPD", size=10, fill="#ffffff", stroke="#27ae60"),
        svgkit.arrow(370, 107, 400, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(400, 85, 150, 45, "3. Пошук SA в SAD\nФормування xfrm_dst", size=10, fill="#ffffff", stroke="#c0392b"),
        svgkit.arrow(550, 107, 580, 107, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(580, 85, 170, 45, "4. xfrm_output()\nШифрування / ESP wrap", size=10, fill="#ffffff", stroke="#333333"),

        svgkit.arrow(665, 130, 665, 150, color="#1a1a1a", sw=1.5),
        svgkit.fitbox(550, 150, 200, 35, "5. Передача в мережеву карту\ndev_queue_xmit()", size=10, fill="#eafaf1", stroke="#27ae60"),

        # Inbound flow header
        svgkit.rect(30, 225, 740, 160, fill="#f4f6f8", stroke="#c0392b", sw=1.5, rx=8),
        svgkit.text(400, 245, "Вхідний трафік (Inbound RX Path)", size=13, bold=True, color="#c0392b"),

        svgkit.fitbox(50, 265, 160, 45, "1. Отримання кадру\nnetif_receive_skb()", size=10, fill="#ffffff", stroke="#333333"),
        svgkit.arrow(210, 287, 240, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(240, 265, 150, 45, "2. ip_local_deliver()\nПротокол ESP (50)/AH (51)", size=10, fill="#ffffff", stroke="#2457d6"),
        svgkit.arrow(390, 287, 420, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(420, 265, 150, 45, "3. xfrm4_rcv()\nПошук SA за (SPI, Dst)", size=10, fill="#ffffff", stroke="#c0392b"),
        svgkit.arrow(570, 287, 600, 287, color="#1a1a1a", sw=1.5),

        svgkit.fitbox(600, 265, 150, 45, "4. xfrm_input()\nДешифрація та Anti-Replay", size=10, fill="#ffffff", stroke="#333333"),

        svgkit.arrow(675, 310, 675, 330, color="#1a1a1a", sw=1.5),
        svgkit.fitbox(530, 330, 220, 35, "5. Перевірка SPD + передача сокету\nnetif_rx() / socket receive", size=10, fill="#eafaf1", stroke="#27ae60"),
    ]

    svgkit.render(path, 800, 400, *frags, title="Життєвий цикл IPsec-пакета в мережевому стеку Linux")

def render_modes():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "img", "xfrm-mode-comparison.svg")

    frags = [
        # Original Packet
        svgkit.text(120, 55, "Ззвичайний IP-пакет:", size=11, bold=True, anchor="start"),
        svgkit.rect(120, 65, 110, 35, fill="#eef6fc", stroke="#2457d6"),
        svgkit.text(175, 87, "IP Header", size=10),
        svgkit.rect(230, 65, 110, 35, fill="#f4f6f8", stroke="#333333"),
        svgkit.text(285, 87, "TCP / UDP", size=10),
        svgkit.rect(340, 65, 220, 35, fill="#eafaf1", stroke="#27ae60"),
        svgkit.text(450, 87, "Payload (Дані)", size=10),

        # Transport Mode ESP
        svgkit.text(120, 130, "Транспортний режим (Transport Mode ESP):", size=11, bold=True, anchor="start"),
        svgkit.rect(120, 140, 110, 35, fill="#eef6fc", stroke="#2457d6"),
        svgkit.text(175, 162, "IP Header", size=10),
        svgkit.rect(230, 140, 90, 35, fill="#fdecea", stroke="#c0392b"),
        svgkit.text(275, 162, "ESP Header", size=10),
        svgkit.rect(320, 140, 100, 35, fill="#f4f6f8", stroke="#333333"),
        svgkit.text(370, 162, "TCP / UDP", size=10),
        svgkit.rect(420, 140, 160, 35, fill="#eafaf1", stroke="#27ae60"),
        svgkit.text(500, 162, "Payload", size=10),
        svgkit.rect(580, 140, 90, 35, fill="#fdecea", stroke="#c0392b"),
        svgkit.text(625, 162, "ESP Auth", size=10),

        # Bracket for Transport Mode Encryption
        svgkit.line(320, 180, 580, 180, color="#c0392b", sw=1.5, dash="4,4"),
        svgkit.text(450, 193, "Шифрується та захищається ESP", size=10, color="#c0392b"),

        # Tunnel Mode ESP
        svgkit.text(120, 225, "Тунельний режим (Tunnel Mode ESP):", size=11, bold=True, anchor="start"),
        svgkit.rect(120, 235, 110, 35, fill="#2457d6", stroke="#2457d6"),
        svgkit.text(175, 257, "Outer IP Hdr", size=10, color="#ffffff", bold=True),
        svgkit.rect(230, 235, 90, 35, fill="#fdecea", stroke="#c0392b"),
        svgkit.text(275, 257, "ESP Header", size=10),
        svgkit.rect(320, 235, 100, 35, fill="#eef6fc", stroke="#2457d6"),
        svgkit.text(370, 257, "Inner IP Hdr", size=10),
        svgkit.rect(420, 235, 90, 35, fill="#f4f6f8", stroke="#333333"),
        svgkit.text(465, 257, "TCP / UDP", size=10),
        svgkit.rect(510, 235, 120, 35, fill="#eafaf1", stroke="#27ae60"),
        svgkit.text(570, 257, "Payload", size=10),
        svgkit.rect(630, 235, 80, 35, fill="#fdecea", stroke="#c0392b"),
        svgkit.text(670, 257, "ESP Auth", size=10),

        # Bracket for Tunnel Mode Encryption
        svgkit.line(320, 275, 630, 275, color="#c0392b", sw=1.5, dash="4,4"),
        svgkit.text(475, 288, "Повністю інкапсульований та зашифрований внутрішній пакет", size=10, color="#c0392b"),
    ]

    svgkit.render(path, 800, 310, *frags, title="Структура пакетів IPsec: транспортний та тунельний режими")

def main():
    render_arch()
    render_flow()
    render_modes()

if __name__ == "__main__":
    main()
