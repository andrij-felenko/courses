import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import render, textbox, fitbox, rect, line, arrow, text, mtext, circle, FILL, LINE, INK, MUTED, POS, NEG, FIELD

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def generate_tuntap_arch():
    w, h = 820, 500
    frags = []

    # Regions
    frags.append(rect(20, 20, 780, 190, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 45, "ПРОСТІР КОРИСТУВАЧА (USER SPACE)", size=13, color=MUTED, bold=True, anchor="start"))

    frags.append(rect(20, 230, 780, 250, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(40, 255, "ЯДРО LINUX (KERNEL SPACE)", size=13, color=MUTED, bold=True, anchor="start"))

    # User Space App Box
    b_app, _, _ = textbox(160, 120, "Процес / Програма\n(OpenVPN, QEMU, WireGuard)\nfd = open(\"/dev/net/tun\")", size=12, fill="#e0f2fe", stroke="#0284c7", sw=1.5)
    frags.append(b_app)

    # Tunnel socket box in App
    b_sock, _, _ = textbox(520, 120, "Сокет тунелю (UDP/TCP)\nпідключений до WAN", size=12, fill="#e0f2fe", stroke="#0284c7", sw=1.5)
    frags.append(b_sock)

    # /dev/net/tun Char Device Box in Kernel
    b_dev, _, _ = textbox(160, 320, "Символьний пристрій\n/dev/net/tun\n(struct file_operations)", size=12, fill="#fef3c7", stroke="#d97706", sw=1.5)
    frags.append(b_dev)

    # Net Device Box in Kernel (tun0 / tap0)
    b_netdev, _, _ = textbox(460, 320, "Віртуальний пристрій\ntun0 / tap0\n(struct net_device)", size=12, fill="#dcfce7", stroke="#16a34a", sw=1.5)
    frags.append(b_netdev)

    # Linux Network Stack / Routing
    b_stack, _, _ = textbox(460, 430, "Мережевий стек Linux\n(IP / Routing / Bridge / Netfilter)", size=12, fill="#ede9fe", stroke="#7c3aed", sw=1.5)
    frags.append(b_stack)

    # Physical NIC
    b_nic, _, _ = textbox(710, 430, "Фізичний NIC\neth0", size=12, fill="#fee2e2", stroke="#dc2626", sw=1.5)
    frags.append(b_nic)

    # Arrows
    # App <-> /dev/net/tun
    frags.append(arrow(130, 175, 130, 275, color="#0284c7", sw=2))
    frags.append(arrow(190, 275, 190, 175, color="#0284c7", sw=2))
    frags.append(text(105, 225, "write()", size=11, color="#0284c7", bold=True, anchor="end"))
    frags.append(text(215, 225, "read()", size=11, color="#0284c7", bold=True, anchor="start"))

    # /dev/net/tun <-> tun0/tap0
    frags.append(arrow(275, 310, 345, 310, color="#d97706", sw=2))
    frags.append(arrow(345, 330, 275, 330, color="#d97706", sw=2))
    frags.append(text(310, 295, "skb queue", size=10, color=MUTED, anchor="middle"))

    # tun0/tap0 -> Stack
    frags.append(arrow(460, 365, 460, 385, color="#16a34a", sw=2))

    # Stack -> Physical NIC
    frags.append(arrow(600, 430, 635, 430, color="#7c3aed", sw=2))

    # App <-> Tunnel socket
    frags.append(arrow(280, 120, 395, 120, color="#0284c7", sw=2))
    frags.append(text(337, 105, "пакети VPN", size=10, color=MUTED, anchor="middle"))

    # Tunnel socket -> Stack (routed via physical NIC)
    frags.append(arrow(520, 175, 520, 385, color="#7c3aed", sw=2))

    # Tunnel socket -> Outer WAN
    frags.append(arrow(645, 120, 740, 120, color="#0284c7", sw=2))
    frags.append(text(692, 105, "До Інтернету", size=11, color="#0284c7", anchor="middle"))

    render(os.path.join(IMG_DIR, "tuntap-arch.svg"), w, h, *frags)

def generate_l3_tun_vs_l2_tap():
    w, h = 760, 340
    frags = []

    # Left Column: TUN (L3)
    frags.append(rect(30, 30, 335, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(197, 60, "TUN (Layer 3 — Мережевий)", size=15, color="#0284c7", bold=True, anchor="middle"))
    frags.append(text(197, 82, "Оперує IP-пакетами", size=12, color=MUTED, anchor="middle"))

    # TUN Frame structure
    frags.append(rect(50, 120, 295, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(197, 147, "Заголовок IP (v4/v6)\n[Src IP | Dst IP | Proto]", size=12, color=INK, bold=True, anchor="middle"))

    frags.append(rect(50, 175, 295, 55, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(197, 207, "Корисне навантаження (Payload)\nTCP / UDP / ICMP даних", size=12, color=INK, anchor="middle"))

    frags.append(text(197, 260, "• Без Ethernet заголовка\n• Не має MAC-адреси\n• Не підтримує L2 ARP/Broadcast", size=11, color=MUTED, anchor="middle"))

    # Right Column: TAP (L2)
    frags.append(rect(395, 30, 335, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(562, 60, "TAP (Layer 2 — Канальний)", size=15, color="#16a34a", bold=True, anchor="middle"))
    frags.append(text(562, 82, "Оперує Ethernet-кадрами", size=12, color=MUTED, anchor="middle"))

    # TAP Frame structure
    frags.append(rect(415, 110, 295, 40, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    frags.append(text(562, 134, "Заголовок Ethernet\n[Dst MAC | Src MAC | EtherType]", size=11, color=INK, bold=True, anchor="middle"))

    frags.append(rect(415, 155, 295, 40, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(562, 179, "Заголовок IP (v4/v6) або ARP", size=11, color=INK, bold=True, anchor="middle"))

    frags.append(rect(415, 200, 295, 45, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(562, 227, "Payload (TCP / UDP / L2-дані)", size=11, color=INK, anchor="middle"))

    frags.append(text(562, 268, "• Повноцінний кадр Ethernet\n• Має власну MAC-адресу\n• Підтримує Bridge / ARP / Broadcast", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, "l3-tun-vs-l2-tap.svg"), w, h, *frags)

def generate_packet_lifecycle():
    w, h = 800, 420
    frags = []

    # Flow 1: Kernel Outgoing to TUN Process (RX for App)
    frags.append(rect(20, 20, 760, 180, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(40, 45, "1. Перехоплення трафіку з ядра в програму (kernel TX → app read)", size=13, color="#0284c7", bold=True, anchor="start"))

    b1, _, _ = textbox(110, 110, "Ядро / Сокет\nгенерує пакет", size=12, fill="#ffffff", stroke="#64748b")
    b2, _, _ = textbox(300, 110, "Таблиця маршрутів\nспрямовує в tun0", size=12, fill="#ffffff", stroke="#64748b")
    b3, _, _ = textbox(500, 110, "Черга skb у драйвері\n/dev/net/tun", size=12, fill="#fef3c7", stroke="#d97706")
    b4, _, _ = textbox(690, 110, "Процес викликає\nread(fd, buf)", size=12, fill="#e0f2fe", stroke="#0284c7")

    frags.extend([b1, b2, b3, b4])
    frags.append(arrow(180, 110, 225, 110, color="#0284c7", sw=2))
    frags.append(arrow(375, 110, 425, 110, color="#0284c7", sw=2))
    frags.append(arrow(575, 110, 625, 110, color="#0284c7", sw=2))

    # Flow 2: App Injecting Packet into Kernel (TX for App)
    frags.append(rect(20, 220, 760, 180, fill="#f8fafc", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(40, 245, "2. Впорскування пакетів з програми в ядро (app write → kernel rx)", size=13, color="#16a34a", bold=True, anchor="start"))

    c1, _, _ = textbox(110, 310, "Процес викликає\nwrite(fd, pkt)", size=12, fill="#e0f2fe", stroke="#0284c7")
    c2, _, _ = textbox(300, 310, "Драйвер створює skb\nі викликає netif_rx()", size=12, fill="#fef3c7", stroke="#d97706")
    c3, _, _ = textbox(500, 310, "Мережевий стек\nобробляє пакет", size=12, fill="#dcfce7", stroke="#16a34a")
    c4, _, _ = textbox(690, 310, "Маршрутизація / \nПризначений сокет", size=12, fill="#ffffff", stroke="#64748b")

    frags.extend([c1, c2, c3, c4])
    frags.append(arrow(180, 310, 225, 310, color="#16a34a", sw=2))
    frags.append(arrow(375, 310, 425, 310, color="#16a34a", sw=2))
    frags.append(arrow(575, 310, 625, 310, color="#16a34a", sw=2))

    render(os.path.join(IMG_DIR, "packet-lifecycle.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_tuntap_arch()
    generate_l3_tun_vs_l2_tap()
    generate_packet_lifecycle()
    print("Figures generated successfully!")
