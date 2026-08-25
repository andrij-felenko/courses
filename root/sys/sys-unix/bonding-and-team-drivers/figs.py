import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def generate_bonding_arch():
    svg_path = os.path.join(IMG_DIR, 'bonding-arch.svg')
    content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="920" height="500" viewBox="0 0 920 500">
    <style>
        .bg { fill: #f8fafc; }
        .box-kernel { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-user { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .box-sub { fill: #ffffff; stroke: #94a3b8; stroke-width: 1.5; rx: 6px; }
        .box-slave { fill: #f1f5f9; stroke: #475569; stroke-width: 1.5; rx: 4px; }
        .title-kernel { font-family: monospace; font-size: 15px; font-weight: bold; fill: #1e40af; }
        .title-user { font-family: monospace; font-size: 15px; font-weight: bold; fill: #92400e; }
        .text-bold { font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #1e293b; }
        .text-main { font-family: system-ui, sans-serif; font-size: 12px; fill: #334155; }
        .text-code { font-family: monospace; font-size: 12px; fill: #0f172a; }
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        .arrow-orange { stroke: #d97706; stroke-width: 2; fill: none; marker-end: url(#arrowhead-orange); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-orange" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#d97706"/>
        </marker>
    </defs>

    <rect width="920" height="500" class="bg"/>

    <!-- LEFT PANEL: MONOLITHIC BONDING -->
    <rect x="30" y="30" width="410" height="440" class="box-kernel"/>
    <text x="235" y="60" class="title-kernel" text-anchor="middle">Класичний Linux Bonding (Kernel Monolith)</text>

    <rect x="50" y="85" width="370" height="40" class="box-sub"/>
    <text x="235" y="110" class="text-bold" text-anchor="middle">Network Stack / Sockets (TCP/IP)</text>

    <rect x="50" y="155" width="370" height="120" class="box-sub" stroke="#2563eb" stroke-width="2"/>
    <text x="235" y="180" class="title-kernel" text-anchor="middle">Master net_device: bond0</text>
    <text x="70" y="205" class="text-main">• xmit_hash_policy / mode (0-6)</text>
    <text x="70" y="225" class="text-main">• MII Monitor / ARP State Machine</text>
    <text x="70" y="245" class="text-main">• LACPDU State Machine (Mode 4)</text>
    <text x="70" y="265" class="text-code">sysfs: /sys/class/net/bond0/bonding/</text>

    <rect x="70" y="310" width="150" height="50" class="box-slave"/>
    <text x="145" y="330" class="text-bold" text-anchor="middle">Slave: eth0</text>
    <text x="145" y="348" class="text-main" text-anchor="middle">IFF_SLAVE</text>

    <rect x="250" y="310" width="150" height="50" class="box-slave"/>
    <text x="325" y="330" class="text-bold" text-anchor="middle">Slave: eth1</text>
    <text x="325" y="348" class="text-main" text-anchor="middle">IFF_SLAVE</text>

    <rect x="50" y="395" width="370" height="50" fill="#e2e8f0" stroke="#475569" stroke-width="1.5" rx="6"/>
    <text x="235" y="425" class="text-bold" text-anchor="middle">Physical NIC Hardware Ports</text>

    <path d="M 235 125 V 155" class="arrow"/>
    <path d="M 145 275 V 310" class="arrow"/>
    <path d="M 325 275 V 310" class="arrow"/>
    <path d="M 145 360 V 395" class="arrow"/>
    <path d="M 325 360 V 395" class="arrow"/>

    <!-- RIGHT PANEL: TEAM DAEMON ARCHITECTURE -->
    <rect x="480" y="30" width="410" height="440" class="box-kernel" fill="#f8fafc"/>

    <rect x="500" y="50" width="370" height="110" class="box-user"/>
    <text x="685" y="75" class="title-user" text-anchor="middle">User-space: teamd Daemon (Control Path)</text>
    <text x="520" y="98" class="text-main">• LACP Runner / ActiveBackup Runner</text>
    <text x="520" y="118" class="text-main">• Link Watchers (ethtool, arp_ping, nsna)</text>
    <text x="520" y="138" class="text-code">JSON Config / DBus / teamdctl IPC</text>

    <rect x="500" y="210" width="370" height="100" class="box-sub" stroke="#059669" stroke-width="2"/>
    <text x="685" y="235" font-family="monospace" font-size="15" font-weight="bold" fill="#047857" text-anchor="middle">Kernel: team0 net_device (Data Path)</text>
    <text x="520" y="260" class="text-main">• Fast-path Packet Scheduler (Runners)</text>
    <text x="520" y="280" class="text-main">• eBPF Hash / Loadbalance Classifier</text>
    <text x="520" y="300" class="text-code">Netlink (genl) Control Channel</text>

    <rect x="520" y="340" width="150" height="45" class="box-slave"/>
    <text x="595" y="360" class="text-bold" text-anchor="middle">Port: eth0</text>
    <text x="595" y="375" class="text-main" text-anchor="middle">team port dev</text>

    <rect x="700" y="340" width="150" height="45" class="box-slave"/>
    <text x="775" y="360" class="text-bold" text-anchor="middle">Port: eth1</text>
    <text x="775" y="375" class="text-main" text-anchor="middle">team port dev</text>

    <rect x="500" y="410" width="370" height="45" fill="#e2e8f0" stroke="#475569" stroke-width="1.5" rx="6"/>
    <text x="685" y="437" class="text-bold" text-anchor="middle">Physical NIC Hardware Ports</text>

    <path d="M 685 160 V 210" class="arrow-orange"/>
    <path d="M 595 310 V 340" class="arrow"/>
    <path d="M 775 310 V 340" class="arrow"/>
    <path d="M 595 385 V 410" class="arrow"/>
    <path d="M 775 385 V 410" class="arrow"/>
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {svg_path}")

def generate_bonding_modes_hash():
    svg_path = os.path.join(IMG_DIR, 'bonding-modes-hash.svg')
    content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="920" height="460" viewBox="0 0 920 460">
    <style>
        .bg { fill: #f8fafc; }
        .box-card { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.5; rx: 8px; }
        .box-header { fill: #e0f2fe; stroke: #0284c7; stroke-width: 1.5; rx: 6px; }
        .box-hash { fill: #fef3c7; stroke: #d97706; stroke-width: 1.5; rx: 6px; }
        .box-port { fill: #f1f5f9; stroke: #475569; stroke-width: 1.5; rx: 4px; }
        .title-card { font-family: system-ui, sans-serif; font-size: 15px; font-weight: bold; fill: #0369a1; }
        .text-bold { font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .text-main { font-family: system-ui, sans-serif; font-size: 12px; fill: #334155; }
        .text-code { font-family: monospace; font-size: 12px; fill: #1e293b; }
        .arrow { stroke: #0284c7; stroke-width: 2; fill: none; marker-end: url(#arrowhead-blue); }
        .arrow-orange { stroke: #d97706; stroke-width: 2; fill: none; marker-end: url(#arrowhead-orange); }
    </style>

    <defs>
        <marker id="arrowhead-blue" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#0284c7"/>
        </marker>
        <marker id="arrowhead-orange" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#d97706"/>
        </marker>
    </defs>

    <rect width="920" height="460" class="bg"/>

    <!-- Ingress Frame Header -->
    <rect x="30" y="30" width="860" height="60" class="box-header"/>
    <text x="460" y="55" class="title-card" text-anchor="middle">Вхідний Ethernet Кадр / IP Пакет</text>
    <text x="460" y="75" class="text-code" text-anchor="middle">[ Src MAC | Dst MAC ]  [ Src IP | Dst IP ]  [ Src Port | Dst Port ]</text>

    <!-- Hash Policy Box 1: Layer 2 -->
    <rect x="30" y="130" width="270" height="200" class="box-card"/>
    <text x="165" y="155" class="text-bold" text-anchor="middle">layer2 (За замовчуванням)</text>
    <rect x="45" y="170" width="240" height="45" class="box-hash"/>
    <text x="165" y="190" class="text-code" text-anchor="middle">hash = (MAC_src XOR MAC_dst)</text>
    <text x="165" y="205" class="text-code" text-anchor="middle">port_idx = hash % N</text>
    <text x="45" y="235" class="text-main">• Стійке сесійне призначення</text>
    <text x="45" y="255" class="text-main">• Використовує лише L2 заголовок</text>
    <text x="45" y="275" class="text-main">• Вузьке місце за один маршрутизатор</text>
    <text x="165" y="310" class="text-code" text-anchor="middle">balance-xor / 802.3ad</text>

    <!-- Hash Policy Box 2: Layer 2+3 -->
    <rect x="325" y="130" width="270" height="200" class="box-card"/>
    <text x="460" y="155" class="text-bold" text-anchor="middle">layer2+3 (Комбінований)</text>
    <rect x="340" y="170" width="240" height="45" class="box-hash"/>
    <text x="460" y="190" class="text-code" text-anchor="middle">hash = MAC_xor XOR IP_xor</text>
    <text x="460" y="205" class="text-code" text-anchor="middle">port_idx = hash % N</text>
    <text x="340" y="235" class="text-main">• Балансування між різними IP</text>
    <text x="340" y="255" class="text-main">• Безпечно для більшості роутерів</text>
    <text x="340" y="275" class="text-main">• Підтримує IPv4 та IPv6</text>
    <text x="460" y="310" class="text-code" text-anchor="middle">xmit_hash_policy = layer2+3</text>

    <!-- Hash Policy Box 3: Layer 3+4 -->
    <rect x="620" y="130" width="270" height="200" class="box-card"/>
    <text x="755" y="155" class="text-bold" text-anchor="middle">layer3+4 (Високодетальний)</text>
    <rect x="635" y="170" width="240" height="45" class="box-hash"/>
    <text x="755" y="190" class="text-code" text-anchor="middle">hash = IP_xor XOR Port_xor</text>
    <text x="755" y="205" class="text-code" text-anchor="middle">port_idx = hash % N</text>
    <text x="635" y="235" class="text-main">• Розподіл окремих TCP/UDP сесій</text>
    <text x="635" y="255" class="text-main">• Максимальна рівномірність</text>
    <text x="635" y="275" class="text-main">• Ігнорує фрагментовані пакети</text>
    <text x="755" y="310" class="text-code" text-anchor="middle">xmit_hash_policy = layer3+4</text>

    <!-- Output Ports Array -->
    <rect x="30" y="360" width="860" height="70" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5" rx="6"/>
    <text x="460" y="385" class="text-bold" text-anchor="middle">Підпорядковані Фізичні Інтерфейси (Slave Ports 0..N-1)</text>

    <rect x="180" y="395" width="160" height="30" class="box-port"/>
    <text x="260" y="415" class="text-code" text-anchor="middle">eth0 (Port 0)</text>

    <rect x="380" y="395" width="160" height="30" class="box-port"/>
    <text x="460" y="415" class="text-code" text-anchor="middle">eth1 (Port 1)</text>

    <rect x="580" y="395" width="160" height="30" class="box-port"/>
    <text x="660" y="415" class="text-code" text-anchor="middle">eth2 (Port 2)</text>

    <!-- Arrows from Top to Hash Boxes -->
    <path d="M 165 90 V 130" class="arrow"/>
    <path d="M 460 90 V 130" class="arrow"/>
    <path d="M 755 90 V 130" class="arrow"/>

    <!-- Arrows from Hash Boxes to Ports -->
    <path d="M 165 330 V 360" class="arrow-orange"/>
    <path d="M 460 330 V 360" class="arrow-orange"/>
    <path d="M 755 330 V 360" class="arrow-orange"/>
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {svg_path}")

if __name__ == "__main__":
    generate_bonding_arch()
    generate_bonding_modes_hash()
