import os
import sys

def generate_routing_architecture():
    os.makedirs("img", exist_ok=True)
    svg_path = os.path.join("img", "routing-architecture.svg")

    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
    <style>
        .bg { fill: #f8fafc; }
        .box-pipe { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-pbr { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .box-fib { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-dest { fill: #f3e8ff; stroke: #9333ea; stroke-width: 2; rx: 8px; }
        .title-main { font-family: monospace; font-size: 16px; font-weight: bold; fill: #1e40af; }
        .title-pbr { font-family: monospace; font-size: 15px; font-weight: bold; fill: #854d0e; }
        .title-fib { font-family: monospace; font-size: 15px; font-weight: bold; fill: #166534; }
        .title-dest { font-family: monospace; font-size: 15px; font-weight: bold; fill: #6b21a8; }
        .text-body { font-family: monospace; font-size: 12px; fill: #334155; }
        .text-bold { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrowhead-green); }
        .arrow-purple { stroke: #9333ea; stroke-width: 2; fill: none; marker-end: url(#arrowhead-purple); }
        .arrow-yellow { stroke: #ca8a04; stroke-width: 2; fill: none; marker-end: url(#arrowhead-yellow); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
        </marker>
        <marker id="arrowhead-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#9333ea"/>
        </marker>
        <marker id="arrowhead-yellow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ca8a04"/>
        </marker>
    </defs>

    <!-- Canvas Background -->
    <rect width="960" height="540" class="bg"/>

    <!-- Ingress Stage -->
    <rect x="30" y="40" width="200" height="460" class="box-pipe"/>
    <text x="130" y="70" class="title-main" text-anchor="middle">Вхідний пакет (sk_buff)</text>
    
    <rect x="45" y="95" width="170" height="75" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" rx="5"/>
    <text x="130" y="118" class="text-bold" text-anchor="middle">1. Driver Ingress</text>
    <text x="55" y="140" class="text-body">netif_receive_skb()</text>
    <text x="55" y="158" class="text-body">dev: eth0 / wlan0</text>

    <rect x="45" y="195" width="170" height="75" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" rx="5"/>
    <text x="130" y="218" class="text-bold" text-anchor="middle">2. PREROUTING</text>
    <text x="55" y="240" class="text-body">netfilter / iptables</text>
    <text x="55" y="258" class="text-body">conntrack / raw / mangle</text>

    <rect x="45" y="295" width="170" height="95" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" rx="5"/>
    <text x="130" y="318" class="text-bold" text-anchor="middle">3. Early Demux</text>
    <text x="55" y="340" class="text-body">sk-&gt;sk_dst_cache</text>
    <text x="55" y="358" class="text-body">Збіг сокета?</text>
    <text x="55" y="376" class="text-body">ТАК: обхід FIB!</text>

    <rect x="45" y="415" width="170" height="65" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5" rx="5"/>
    <text x="130" y="438" class="text-bold" text-anchor="middle" fill="#991b1b">НІ: fib_lookup()</text>
    <text x="55" y="460" class="text-body" fill="#991b1b">Перехід до RPDB</text>

    <!-- Arrow Ingress -> RPDB -->
    <path d="M 215 448 H 270" class="arrow"/>

    <!-- PBR Stage (RPDB) -->
    <rect x="270" y="40" width="220" height="460" class="box-pbr"/>
    <text x="380" y="70" class="title-pbr" text-anchor="middle">RPDB (ip rule)</text>

    <rect x="285" y="100" width="190" height="85" fill="#fef9c3" stroke="#eab308" stroke-width="1.5" rx="5"/>
    <text x="380" y="123" class="text-bold" text-anchor="middle">Пріоритет 0: local</text>
    <text x="295" y="145" class="text-body">from all lookup local</text>
    <text x="295" y="165" class="text-body">Локальні адреси / loopback</text>

    <rect x="285" y="210" width="190" height="110" fill="#fef9c3" stroke="#eab308" stroke-width="1.5" rx="5"/>
    <text x="380" y="233" class="text-bold" text-anchor="middle">Пріоритетні правила PBR</text>
    <text x="295" y="255" class="text-body">fwmark / tos / iif</text>
    <text x="295" y="275" class="text-body">from 10.0.0.0/24</text>
    <text x="295" y="295" class="text-body">lookup table 100</text>

    <rect x="285" y="345" width="190" height="70" fill="#fef9c3" stroke="#eab308" stroke-width="1.5" rx="5"/>
    <text x="380" y="368" class="text-bold" text-anchor="middle">Пріоритет 32766: main</text>
    <text x="295" y="390" class="text-body">from all lookup main</text>

    <rect x="285" y="430" width="190" height="55" fill="#fef9c3" stroke="#eab308" stroke-width="1.5" rx="5"/>
    <text x="380" y="453" class="text-bold" text-anchor="middle">Пріоритет 32767: default</text>

    <!-- Arrow RPDB -> FIB -->
    <path d="M 475 265 H 530" class="arrow-yellow"/>

    <!-- FIB Lookup Stage -->
    <rect x="530" y="40" width="210" height="460" class="box-fib"/>
    <text x="635" y="70" class="title-fib" text-anchor="middle">FIB (LC-Trie LPM)</text>

    <rect x="545" y="100" width="180" height="85" fill="#dcfce7" stroke="#22c55e" stroke-width="1.5" rx="5"/>
    <text x="635" y="123" class="text-bold" text-anchor="middle">Таблиця 255 (local)</text>
    <text x="555" y="145" class="text-body">RTN_LOCAL -&gt; local_in</text>
    <text x="555" y="165" class="text-body">RTN_BROADCAST</text>

    <rect x="545" y="210" width="180" height="110" fill="#dcfce7" stroke="#22c55e" stroke-width="1.5" rx="5"/>
    <text x="635" y="233" class="text-bold" text-anchor="middle">Таблиця 254 (main)</text>
    <text x="555" y="255" class="text-body">LC-Trie Stride Indexing</text>
    <text x="555" y="275" class="text-body">Longest Prefix Match</text>
    <text x="555" y="295" class="text-body">fib_alias -&gt; fib_info</text>

    <rect x="545" y="345" width="180" height="135" fill="#dcfce7" stroke="#22c55e" stroke-width="1.5" rx="5"/>
    <text x="635" y="368" class="text-bold" text-anchor="middle">Результат (fib_result)</text>
    <text x="555" y="390" class="text-body">nh_gw (Gateway IP)</text>
    <text x="555" y="410" class="text-body">dev (Output Interface)</text>
    <text x="555" y="430" class="text-body">scope (LINK/UNIVERSE)</text>
    <text x="555" y="450" class="text-body">type (UNICAST/LOCAL)</text>

    <!-- Arrow FIB -> Delivery -->
    <path d="M 725 412 H 770" class="arrow-green"/>

    <!-- Egress / Delivery Stage -->
    <rect x="770" y="40" width="160" height="460" class="box-dest"/>
    <text x="850" y="70" class="title-dest" text-anchor="middle">Результат</text>

    <rect x="782" y="110" width="136" height="110" fill="#faf5ff" stroke="#a855f7" stroke-width="1.5" rx="5"/>
    <text x="850" y="133" class="text-bold" text-anchor="middle">LOCAL_IN</text>
    <text x="792" y="158" class="text-body">ip_local_deliver()</text>
    <text x="792" y="180" class="text-body">L4 Demux (TCP/UDP)</text>
    <text x="792" y="202" class="text-body">Сокет застосунку</text>

    <rect x="782" y="290" width="136" height="160" fill="#faf5ff" stroke="#a855f7" stroke-width="1.5" rx="5"/>
    <text x="850" y="313" class="text-bold" text-anchor="middle">FORWARD / OUT</text>
    <text x="792" y="338" class="text-body">ip_forward()</text>
    <text x="792" y="360" class="text-body">Neighbor Table (ARP)</text>
    <text x="792" y="382" class="text-body">POSTROUTING</text>
    <text x="792" y="404" class="text-body">dev_queue_xmit()</text>
    <text x="792" y="426" class="text-body">Вихід у дріт</text>
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {svg_path}")

def generate_lc_trie_lookup():
    os.makedirs("img", exist_ok=True)
    svg_path = os.path.join("img", "lc-trie-lookup.svg")

    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="500" viewBox="0 0 960 500">
    <style>
        .bg { fill: #f8fafc; }
        .box-root { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 6px; }
        .box-branch { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 6px; }
        .box-leaf { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 6px; }
        .box-target { fill: #fee2e2; stroke: #dc2626; stroke-width: 2; rx: 6px; }
        .title-node { font-family: monospace; font-size: 14px; font-weight: bold; fill: #1e40af; }
        .title-branch { font-family: monospace; font-size: 14px; font-weight: bold; fill: #854d0e; }
        .title-leaf { font-family: monospace; font-size: 14px; font-weight: bold; fill: #166534; }
        .text-body { font-family: monospace; font-size: 12px; fill: #334155; }
        .text-bold { font-family: monospace; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        .arrow-red { stroke: #dc2626; stroke-width: 2.5; fill: none; marker-end: url(#arrowhead-red); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrowhead-green); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626"/>
        </marker>
        <marker id="arrowhead-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
        </marker>
    </defs>

    <!-- Canvas Background -->
    <rect width="960" height="500" class="bg"/>

    <!-- Destination IP Panel -->
    <rect x="40" y="30" width="880" height="60" class="box-target"/>
    <text x="60" y="55" class="title-node" fill="#991b1b">Шукана адреса (Destination IP): 10.1.2.45</text>
    <text x="60" y="75" class="text-body" fill="#991b1b">Бінарний вигляд: 00001010 . 00000001 . 00000010 . 00101101 (Префікс /24 збігається з 10.1.2.0/24)</text>

    <!-- Root Node -->
    <rect x="360" y="120" width="240" height="85" class="box-root"/>
    <text x="480" y="145" class="title-node" text-anchor="middle">Root Node (trie_node)</text>
    <text x="375" y="168" class="text-body">pos = 0, bits = 8 (256 slots)</text>
    <text x="375" y="188" class="text-body">index = key &gt;&gt; 24 = 10 (0x0A)</text>

    <!-- Branch Nodes (Level Compression) -->
    <!-- Branch 1: 10.0.0.0/8 -->
    <rect x="80" y="250" width="240" height="95" class="box-branch"/>
    <text x="200" y="275" class="title-branch" text-anchor="middle">Branch (10.0.0.0/16)</text>
    <text x="95" y="298" class="text-body">pos = 8, bits = 8</text>
    <text x="95" y="318" class="text-body">index = (key &gt;&gt; 16) &amp; 0xFF = 0</text>
    <text x="95" y="335" class="text-body">Префікс: 10.0.0.0/16</text>

    <!-- Branch 2: 10.1.0.0/16 (Target Branch) -->
    <rect x="360" y="250" width="240" height="95" class="box-branch" stroke="#dc2626" stroke-width="2.5"/>
    <text x="480" y="275" class="title-branch" text-anchor="middle" fill="#991b1b">Branch (10.1.0.0/16)</text>
    <text x="375" y="298" class="text-body" fill="#991b1b">pos = 8, bits = 8</text>
    <text x="375" y="318" class="text-body" fill="#991b1b">index = (key &gt;&gt; 16) &amp; 0xFF = 1</text>
    <text x="375" y="335" class="text-bold" fill="#dc2626">ЗБІГ: перехід до 10.1.2.0/24</text>

    <!-- Branch 3: 192.168.0.0/16 -->
    <rect x="640" y="250" width="240" height="95" class="box-branch"/>
    <text x="760" y="275" class="title-branch" text-anchor="middle">Branch (192.168.0.0/16)</text>
    <text x="655" y="298" class="text-body">pos = 8, bits = 8</text>
    <text x="655" y="318" class="text-body">index = (key &gt;&gt; 16) &amp; 0xFF = 168</text>
    <text x="655" y="335" class="text-body">Префікс: 192.168.0.0/16</text>

    <!-- Arrows from Root to Branches -->
    <path d="M 400 205 L 200 250" class="arrow"/>
    <path d="M 480 205 L 480 250" class="arrow-red"/>
    <path d="M 560 205 L 760 250" class="arrow"/>

    <!-- Leaves under Branch 2 -->
    <rect x="220" y="390" width="240" height="85" class="box-leaf"/>
    <text x="340" y="413" class="title-leaf" text-anchor="middle">Leaf: 10.1.1.0/24</text>
    <text x="235" y="435" class="text-body">fib_alias: tos=0, type=UNICAST</text>
    <text x="235" y="455" class="text-body">fib_info: via 192.168.1.1 dev eth0</text>

    <!-- Target Leaf: 10.1.2.0/24 -->
    <rect x="500" y="390" width="240" height="85" class="box-leaf" stroke="#dc2626" stroke-width="2.5"/>
    <text x="620" y="413" class="title-leaf" text-anchor="middle" fill="#991b1b">Leaf: 10.1.2.0/24 (LPM)</text>
    <text x="515" y="435" class="text-body" fill="#991b1b">fib_alias: mask=/24, prio=100</text>
    <text x="515" y="455" class="text-bold" fill="#dc2626">fib_info: via 10.1.2.1 dev eth1</text>

    <!-- Arrows from Branch 2 to Leaves -->
    <path d="M 440 345 L 340 390" class="arrow"/>
    <path d="M 520 345 L 620 390" class="arrow-red"/>
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {svg_path}")

def render():
    generate_routing_architecture()
    generate_lc_trie_lookup()

if __name__ == "__main__":
    render()
