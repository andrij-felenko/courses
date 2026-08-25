import os
import sys

def render():
    os.makedirs("img", exist_ok=True)
    
    # 1. Flow diagram: name-resolution-flow.svg
    svg_flow_path = os.path.join("img", "name-resolution-flow.svg")
    svg_flow_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="580" viewBox="0 0 960 580">
    <style>
        .bg { fill: #f8fafc; }
        .box-app { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .box-nss { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-module { fill: #ffffff; stroke: #3b82f6; stroke-width: 1.5; rx: 6px; }
        .box-resolved { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-net { fill: #faf5ff; stroke: #9333ea; stroke-width: 2; rx: 8px; }
        
        .title-app { font-family: monospace; font-size: 15px; font-weight: bold; fill: #854d0e; }
        .title-nss { font-family: monospace; font-size: 15px; font-weight: bold; fill: #1e40af; }
        .title-resolved { font-family: monospace; font-size: 15px; font-weight: bold; fill: #166534; }
        .title-net { font-family: monospace; font-size: 15px; font-weight: bold; fill: #6b21a8; }
        
        .text-main { font-family: monospace; font-size: 13px; fill: #1e293b; }
        .text-sub { font-family: monospace; font-size: 12px; fill: #475569; }
        .text-code { font-family: monospace; font-size: 12px; fill: #0f172a; font-weight: bold; }
        
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrow-blue); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrow-green-head); }
        .arrow-purple { stroke: #9333ea; stroke-width: 2; fill: none; marker-end: url(#arrow-purple-head); }
        .arrow-dash { stroke: #64748b; stroke-width: 1.5; stroke-dasharray: 4,4; fill: none; marker-end: url(#arrow-slate); }
    </style>

    <defs>
        <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrow-green-head" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
        </marker>
        <marker id="arrow-purple-head" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#9333ea"/>
        </marker>
        <marker id="arrow-slate" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
        </marker>
    </defs>

    <!-- Background -->
    <rect width="960" height="580" class="bg"/>

    <!-- 1. Application Layer -->
    <rect x="30" y="25" width="900" height="80" class="box-app"/>
    <text x="50" y="52" class="title-app">1. Додаток (User Application)</text>
    <text x="50" y="80" class="text-main">Виклик POSIX C API: getaddrinfo("example.com", "80", &amp;hints, &amp;res)</text>

    <!-- Arrow App -> NSS -->
    <path d="M 480 105 V 135" class="arrow"/>

    <!-- 2. NSS Dispatcher in glibc -->
    <rect x="30" y="140" width="900" height="230" class="box-nss"/>
    <text x="50" y="167" class="title-nss">2. Glibc Name Service Switch (NSS) — /etc/nsswitch.conf</text>
    <text x="50" y="192" class="text-sub">Рядок конфігурації: hosts: files resolve [!UNAVAIL=return] dns myhostname</text>

    <!-- NSS Modules -->
    <!-- Module 1: files -->
    <rect x="50" y="215" width="250" height="135" class="box-module"/>
    <text x="65" y="240" class="text-code">1. libnss_files.so.2</text>
    <text x="65" y="265" class="text-sub">Локальний файл:</text>
    <text x="65" y="290" class="text-code">/etc/hosts</text>
    <text x="65" y="315" class="text-sub">Перевірка статичних записів</text>

    <!-- Module 2: resolve -->
    <rect x="355" y="215" width="250" height="135" class="box-module"/>
    <text x="370" y="240" class="text-code">2. libnss_resolve.so.2</text>
    <text x="370" y="265" class="text-sub">D-Bus IPC запит до:</text>
    <text x="370" y="290" class="text-code">systemd-resolved</text>
    <text x="370" y="315" class="text-sub">Обхід сокета UDP 53</text>

    <!-- Module 3: dns -->
    <rect x="660" y="215" width="250" height="135" class="box-module"/>
    <text x="675" y="240" class="text-code">3. libnss_dns.so.2</text>
    <text x="675" y="265" class="text-sub">Читає /etc/resolv.conf</text>
    <text x="675" y="290" class="text-code">glibc res_init()</text>
    <text x="675" y="315" class="text-sub">Прямий UDP/TCP DNS</text>

    <!-- Arrows from NSS modules down -->
    <path d="M 480 350 V 390" class="arrow-green"/>
    <path d="M 785 350 V 390" class="arrow-purple"/>

    <!-- 3. systemd-resolved daemon -->
    <rect x="30" y="395" width="575" height="160" class="box-resolved"/>
    <text x="50" y="422" class="title-resolved">3. Daemon systemd-resolved (System Resolver)</text>
    <text x="50" y="447" class="text-main">• Stub-резолвер 127.0.0.53:53 (для сокет-додатків)</text>
    <text x="50" y="472" class="text-main">• Спліт-DNS: маршрутизація доменів по інтерфейсах</text>
    <text x="50" y="497" class="text-main">• Клієнтський кеш, mDNS (5353), LLMNR (5355)</text>
    <text x="50" y="522" class="text-main">• Перевірка DNSSEC та підтримка DNS-over-TLS</text>

    <!-- Arrow resolved -> Net -->
    <path d="M 605 475 H 645" class="arrow-purple"/>

    <!-- 4. Network DNS Servers -->
    <rect x="650" y="395" width="280" height="160" class="box-net"/>
    <text x="670" y="422" class="title-net">4. DNS у мережі</text>
    <text x="670" y="450" class="text-main">Upstream DNS Server</text>
    <text x="670" y="475" class="text-sub">• UDP 53 (до 512B / EDNS0)</text>
    <text x="670" y="500" class="text-sub">• TCP 53 (при TC=1)</text>
    <text x="670" y="525" class="text-sub">• DoT 853 (TLS шифрування)</text>

</svg>
"""
    with open(svg_flow_path, "w", encoding="utf-8") as f:
        f.write(svg_flow_content)

    # 2. Architecture diagram: systemd-resolved-arch.svg
    svg_arch_path = os.path.join("img", "systemd-resolved-arch.svg")
    svg_arch_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520">
    <style>
        .bg { fill: #f8fafc; }
        .box-outer { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 10px; }
        .box-in { fill: #ffffff; stroke: #22c55e; stroke-width: 1.5; rx: 6px; }
        .box-client { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .box-net { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        
        .title-daemon { font-family: monospace; font-size: 16px; font-weight: bold; fill: #15803d; }
        .title-client { font-family: monospace; font-size: 15px; font-weight: bold; fill: #854d0e; }
        .title-net { font-family: monospace; font-size: 15px; font-weight: bold; fill: #1e40af; }
        
        .text-bold { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .text-sub { font-family: monospace; font-size: 12px; fill: #334155; }
        
        .arrow { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrow-green-head); }
        .arrow-blue { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrow-blue-head); }
    </style>

    <defs>
        <marker id="arrow-green-head" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
        </marker>
        <marker id="arrow-blue-head" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
    </defs>

    <rect width="960" height="520" class="bg"/>

    <!-- Clients Left -->
    <rect x="25" y="40" width="220" height="440" class="box-client"/>
    <text x="40" y="70" class="title-client">Клієнти систем</text>
    
    <rect x="40" y="100" width="190" height="90" class="box-in"/>
    <text x="50" y="125" class="text-bold">NSS-додатки</text>
    <text x="50" y="150" class="text-sub">libnss_resolve.so</text>
    <text x="50" y="172" class="text-sub">D-Bus / Varlink IPC</text>

    <rect x="40" y="220" width="190" height="90" class="box-in"/>
    <text x="50" y="245" class="text-bold">Традиційні C-lib</text>
    <text x="50" y="270" class="text-sub">/etc/resolv.conf</text>
    <text x="50" y="292" class="text-sub">-> 127.0.0.53:53</text>

    <rect x="40" y="340" width="190" height="110" class="box-in"/>
    <text x="50" y="365" class="text-bold">CLI інструменти</text>
    <text x="50" y="390" class="text-sub">resolvectl query</text>
    <text x="50" y="415" class="text-sub">resolvectl status</text>

    <!-- Arrow Clients -> Daemon -->
    <path d="M 245 265 H 285" class="arrow"/>

    <!-- systemd-resolved central daemon -->
    <rect x="290" y="40" width="380" height="440" class="box-outer"/>
    <text x="310" y="70" class="title-daemon">systemd-resolved.service</text>

    <!-- Component 1: Entry Points -->
    <rect x="310" y="95" width="340" height="75" class="box-in"/>
    <text x="325" y="120" class="text-bold">Вхідні інтерфейси</text>
    <text x="325" y="145" class="text-sub">127.0.0.53:53 (Stub) | D-Bus / Varlink IPC</text>

    <!-- Component 2: Logic & Routing -->
    <rect x="310" y="190" width="340" height="140" class="box-in"/>
    <text x="325" y="215" class="text-bold">Ядро маршрутизації та кешування</text>
    <text x="325" y="240" class="text-sub">• TTL-базований DNS-кеш</text>
    <text x="325" y="265" class="text-sub">• Split-DNS (маршрутизація доменів)</text>
    <text x="325" y="290" class="text-sub">• DNSSEC валідатор трасту</text>
    <text x="325" y="315" class="text-sub">• Синхронізація з NetworkManager/networkd</text>

    <!-- Component 3: Egress Protocols -->
    <rect x="310" y="350" width="340" height="110" class="box-in"/>
    <text x="325" y="375" class="text-bold">Протокольні модулі виходу</text>
    <text x="325" y="400" class="text-sub">• DNS / DNS-over-TLS (DoT)</text>
    <text x="325" y="425" class="text-sub">• mDNS (.local) &amp; LLMNR</text>

    <!-- Arrow Daemon -> Network -->
    <path d="M 670 265 H 710" class="arrow-blue"/>

    <!-- Network / Upstream Right -->
    <rect x="715" y="40" width="220" height="440" class="box-net"/>
    <text x="730" y="70" class="title-net">Зовнішня мережа</text>

    <rect x="730" y="100" width="190" height="90" class="box-in"/>
    <text x="740" y="125" class="text-bold">Upstream DNS</text>
    <text x="740" y="150" class="text-sub">1.1.1.1 / 8.8.8.8</text>
    <text x="740" y="172" class="text-sub">Порт 53 (UDP/TCP)</text>

    <rect x="730" y="220" width="190" height="90" class="box-in"/>
    <text x="740" y="245" class="text-bold">DoT Сервери</text>
    <text x="740" y="270" class="text-sub">TLS encrypted</text>
    <text x="740" y="292" class="text-sub">Порт 853 (TCP)</text>

    <rect x="730" y="340" width="190" height="110" class="box-in"/>
    <text x="740" y="365" class="text-bold">Локальні вузли</text>
    <text x="740" y="390" class="text-sub">Multicast DNS (5353)</text>
    <text x="740" y="415" class="text-sub">LLMNR (5355)</text>

</svg>
"""
    with open(svg_arch_path, "w", encoding="utf-8") as f:
        f.write(svg_arch_content)

if __name__ == "__main__":
    render()
