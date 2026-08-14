import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "img")

def create_kernel_structs_svg():
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
    <style>
        .bg { fill: #f8fafc; }
        .box-net { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-sub { fill: #ffffff; stroke: #93c5fd; stroke-width: 1.5; rx: 6px; }
        .box-vfs { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .box-proc { fill: #f0fdf4; stroke: #16a34a; stroke-width: 1.5; rx: 6px; }
        .title-main { font-family: monospace; font-size: 16px; font-weight: bold; fill: #1e40af; }
        .title-vfs { font-family: monospace; font-size: 16px; font-weight: bold; fill: #854d0e; }
        .title-sub { font-family: monospace; font-size: 13px; font-weight: bold; fill: #1e3a8a; }
        .text-field { font-family: monospace; font-size: 12px; fill: #334155; }
        .text-bold { font-family: monospace; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        .arrow-gold { stroke: #ca8a04; stroke-width: 2; fill: none; marker-end: url(#arrowhead-gold); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-gold" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ca8a04"/>
        </marker>
    </defs>

    <rect width="960" height="540" class="bg"/>

    <!-- Main struct net container -->
    <rect x="30" y="30" width="580" height="480" class="box-net"/>
    <text x="320" y="60" class="title-main" text-anchor="middle">struct net (include/net/net_namespace.h)</text>
    
    <text x="50" y="85" class="text-bold">refcnt: refcount_t (net->count)</text>
    <text x="50" y="105" class="text-field">passive: refcount_t (net->passive)</text>

    <!-- Sub-component 1: Devices -->
    <rect x="50" y="125" width="250" height="160" class="box-sub"/>
    <text x="175" y="148" class="title-sub" text-anchor="middle">dev_base_head (L2 Devices)</text>
    <text x="65" y="173" class="text-field">• struct net_device *lo</text>
    <text x="65" y="195" class="text-field">• struct net_device *veth0</text>
    <text x="65" y="217" class="text-field">• struct net_device *eth0</text>
    <text x="65" y="239" class="text-field">ifindex_generator: int</text>
    <text x="65" y="261" class="text-field">dev_name_head: hlist_head</text>

    <!-- Sub-component 2: FIB / Routing -->
    <rect x="330" y="125" width="260" height="160" class="box-sub"/>
    <text x="460" y="148" class="title-sub" text-anchor="middle">ipv4.fib_main / fib_local (L3)</text>
    <text x="345" y="173" class="text-field">• fib_table (RT_TABLE_LOCAL)</text>
    <text x="345" y="195" class="text-field">• fib_table (RT_TABLE_MAIN)</text>
    <text x="345" y="217" class="text-field">• fib_rules_ops</text>
    <text x="345" y="239" class="text-field">• ip_fib_trie (FIB Trie)</text>
    <text x="345" y="261" class="text-field">• struct fib_nh_notifier</text>

    <!-- Sub-component 3: Netfilter & Sockets -->
    <rect x="50" y="300" width="250" height="190" class="box-sub"/>
    <text x="175" y="323" class="title-sub" text-anchor="middle">netfilter &amp; Sockets (L4)</text>
    <text x="65" y="348" class="text-field">• nf.hooks (PREROUTING...)</text>
    <text x="65" y="370" class="text-field">• ct.hash (Conntrack table)</text>
    <text x="65" y="392" class="text-field">• ipv4.tcp_death_row</text>
    <text x="65" y="414" class="text-field">• inet_hashinfo (Sockets)</text>
    <text x="65" y="436" class="text-field">• raw_v4_hash / udp_table</text>
    <text x="65" y="458" class="text-field">• nftables tables/chains</text>

    <!-- Sub-component 4: Sysctl & Loopback -->
    <rect x="330" y="300" width="260" height="190" class="box-sub"/>
    <text x="460" y="323" class="title-sub" text-anchor="middle">sysctl &amp; ProcFS (/proc/sys/net)</text>
    <text x="345" y="348" class="text-field">• sysctl_ip_forward: int</text>
    <text x="345" y="370" class="text-field">• sysctl_tcp_rmem / wmem</text>
    <text x="345" y="392" class="text-field">• sysctl_somaxconn: int</text>
    <text x="345" y="414" class="text-field">• proc_net: proc_dir_entry</text>
    <text x="345" y="436" class="text-field">• proc_net_stat: entry</text>
    <text x="345" y="458" class="text-field">• ns.inum (Inode number)</text>

    <!-- VFS and Process representation -->
    <rect x="640" y="30" width="290" height="480" class="box-vfs"/>
    <text x="785" y="60" class="title-vfs" text-anchor="middle">VFS &amp; User-Space Bind Mounts</text>

    <rect x="660" y="90" width="250" height="110" class="box-proc"/>
    <text x="785" y="113" class="title-vfs" text-anchor="middle">Process task_struct</text>
    <text x="675" y="138" class="text-bold">PID 4512 (Container Process)</text>
    <text x="675" y="160" class="text-field">->nsproxy->net_ns ────────►</text>
    <text x="675" y="182" class="text-field">fd[3] -> /proc/4512/ns/net</text>

    <path d="M 670 160 C 620 160 620 90 610 90" class="arrow-gold"/>

    <rect x="660" y="220" width="250" height="120" class="box-proc"/>
    <text x="785" y="243" class="title-vfs" text-anchor="middle">/var/run/netns/red</text>
    <text x="675" y="268" class="text-bold">VFS nsfs Inode (4026532581)</text>
    <text x="675" y="290" class="text-field">Bind mounted file node</text>
    <text x="675" y="312" class="text-field">Holds reference net->count</text>

    <rect x="660" y="360" width="250" height="130" class="box-proc"/>
    <text x="785" y="383" class="title-vfs" text-anchor="middle">Syscall Interfaces</text>
    <text x="675" y="408" class="text-field">• clone(CLONE_NEWNET)</text>
    <text x="675" y="430" class="text-field">• unshare(CLONE_NEWNET)</text>
    <text x="675" y="452" class="text-field">• setns(fd, CLONE_NEWNET)</text>
    <text x="675" y="474" class="text-field">• ioctl(fd, NS_GET_USERNS)</text>
</svg>"""
    with open(os.path.join(IMG_DIR, "netns-kernel-structs.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

def create_topology_svg():
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
    <style>
        .bg { fill: #f8fafc; }
        .box-root { fill: #f1f5f9; stroke: #475569; stroke-width: 2; rx: 8px; }
        .box-netns { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-bridge { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 6px; }
        .box-veth { fill: #fef3c7; stroke: #d97706; stroke-width: 1.5; rx: 4px; }
        .title-root { font-family: monospace; font-size: 15px; font-weight: bold; fill: #1e293b; }
        .title-netns { font-family: monospace; font-size: 14px; font-weight: bold; fill: #1e40af; }
        .title-bridge { font-family: monospace; font-size: 13px; font-weight: bold; fill: #15803d; }
        .text-bold { font-family: monospace; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .text-field { font-family: monospace; font-size: 11px; fill: #334155; }
        .veth-cable { stroke: #d97706; stroke-width: 3; stroke-dasharray: 6,4; fill: none; }
        .arrow-net { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
    </defs>

    <rect width="960" height="540" class="bg"/>

    <!-- Root Namespace Box -->
    <rect x="20" y="20" width="920" height="500" class="box-root"/>
    <text x="40" y="45" class="title-root">Root Network Namespace (Host / init_net)</text>

    <!-- Physical NIC -->
    <rect x="740" y="60" width="180" height="80" fill="#e2e8f0" stroke="#64748b" stroke-width="1.5" rx="6"/>
    <text x="830" y="85" class="title-root" text-anchor="middle">Physical eth0</text>
    <text x="830" y="105" class="text-field" text-anchor="middle">IP: 192.168.1.100/24</text>
    <text x="830" y="123" class="text-field" text-anchor="middle">Default Gateway -> WAN</text>

    <!-- Linux Bridge br0 -->
    <rect x="280" y="170" width="400" height="100" class="box-bridge"/>
    <text x="480" y="195" class="title-bridge" text-anchor="middle">Linux Bridge br0 (L2 Switch + L3 Gateway)</text>
    <text x="480" y="215" class="text-field" text-anchor="middle">IP: 10.0.0.254/24 (Gateway for containers)</text>
    <text x="480" y="235" class="text-field" text-anchor="middle">FDB Table / STP / Forwarding Engine</text>

    <!-- IPTables NAT / Forwarding box -->
    <rect x="740" y="170" width="180" height="100" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5" rx="6"/>
    <text x="830" y="195" class="title-bridge" text-anchor="middle" fill="#991b1b">Netfilter NAT</text>
    <text x="830" y="215" class="text-field" text-anchor="middle">sysctl: ip_forward=1</text>
    <text x="830" y="235" class="text-field" text-anchor="middle">POSTROUTING MASQUERADE</text>

    <!-- Connect Bridge to NAT -->
    <path d="M 680 220 H 740" class="arrow-net"/>
    <path d="M 830 170 V 140" class="arrow-net"/>

    <!-- Netns RED Container -->
    <rect x="50" y="320" width="380" height="180" class="box-netns"/>
    <text x="240" y="345" class="title-netns" text-anchor="middle">Network Namespace "red"</text>
    <text x="70" y="370" class="text-field">Processes: App-1 (PID 1021)</text>
    <text x="70" y="390" class="text-field">Default Route: via 10.0.0.254</text>
    <text x="70" y="410" class="text-field">lo: UP (127.0.0.1)</text>

    <rect x="70" y="430" width="340" height="55" class="box-veth"/>
    <text x="240" y="452" class="text-bold" text-anchor="middle">veth-red (inside ns red)</text>
    <text x="240" y="470" class="text-field" text-anchor="middle">IP: 10.0.0.1/24 | MAC: 52:54:00:aa:bb:01</text>

    <!-- Netns BLUE Container -->
    <rect x="530" y="320" width="380" height="180" class="box-netns"/>
    <text x="720" y="345" class="title-netns" text-anchor="middle">Network Namespace "blue"</text>
    <text x="550" y="370" class="text-field">Processes: App-2 (PID 1088)</text>
    <text x="550" y="390" class="text-field">Default Route: via 10.0.0.254</text>
    <text x="550" y="410" class="text-field">lo: UP (127.0.0.1)</text>

    <rect x="550" y="430" width="340" height="55" class="box-veth"/>
    <text x="720" y="452" class="text-bold" text-anchor="middle">veth-blue (inside ns blue)</text>
    <text x="720" y="470" class="text-field" text-anchor="middle">IP: 10.0.0.2/24 | MAC: 52:54:00:aa:bb:02</text>

    <!-- Host-side veth ends attached to bridge -->
    <rect x="300" y="280" width="140" height="40" class="box-veth"/>
    <text x="370" y="305" class="text-bold" text-anchor="middle">veth-red-br (br0)</text>

    <rect x="520" y="280" width="140" height="40" class="box-veth"/>
    <text x="590" y="305" class="text-bold" text-anchor="middle">veth-blue-br (br0)</text>

    <!-- Veth Virtual Cables - Routed around text box to avoid label collision -->
    <path d="M 240 430 V 370 H 370 V 320" class="veth-cable"/>
    <path d="M 720 430 V 370 H 590 V 320" class="veth-cable"/>

    <!-- Bridge connections -->
    <path d="M 370 280 V 270" class="arrow-net"/>
    <path d="M 590 280 V 270" class="arrow-net"/>
</svg>"""
    with open(os.path.join(IMG_DIR, "veth-bridge-topology.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

def create_packet_flow_svg():
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520">
    <style>
        .bg { fill: #f8fafc; }
        .box-ns { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-kernel { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-step { fill: #ffffff; stroke: #94a3b8; stroke-width: 1.5; rx: 6px; }
        .title-step { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .title-sec { font-family: monospace; font-size: 15px; font-weight: bold; fill: #1e40af; }
        .text-field { font-family: monospace; font-size: 12px; fill: #334155; }
        .arrow-flow { stroke: #2563eb; stroke-width: 2.5; fill: none; marker-end: url(#arrowhead); }
        .arrow-irq { stroke: #dc2626; stroke-width: 2; stroke-dasharray: 4,4; fill: none; marker-end: url(#arrowhead-red); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626"/>
        </marker>
    </defs>

    <rect width="960" height="520" class="bg"/>

    <!-- Section 1: Sending Namespace -->
    <rect x="30" y="30" width="270" height="460" class="box-ns"/>
    <text x="165" y="60" class="title-sec" text-anchor="middle">Namespace "red" (Tx)</text>

    <rect x="50" y="90" width="230" height="75" class="box-step"/>
    <text x="65" y="115" class="title-step">1. Socket sendmsg()</text>
    <text x="65" y="135" class="text-field">Process creates sk_buff</text>
    <text x="65" y="150" class="text-field">skb->dev = veth-red</text>

    <rect x="50" y="210" width="230" height="85" class="box-step"/>
    <text x="65" y="235" class="title-step">2. dev_queue_xmit()</text>
    <text x="65" y="255" class="text-field">Passes skb to qdisc</text>
    <text x="65" y="275" class="text-field">veth_xmit() invoked</text>

    <rect x="50" y="345" width="230" height="120" class="box-step"/>
    <text x="65" y="370" class="title-step">3. Peer Transfer</text>
    <text x="65" y="390" class="text-field">veth_xmit() swaps dev:</text>
    <text x="65" y="410" class="text-field">skb->dev = veth-peer</text>
    <text x="65" y="430" class="text-field">skb_scrub_packet()</text>
    <text x="65" y="450" class="text-field">Resets netns context</text>

    <path d="M 165 165 V 210" class="arrow-flow"/>
    <path d="M 165 295 V 345" class="arrow-flow"/>

    <!-- Section 2: Kernel SoftIRQ & Inter-Namespace Cross -->
    <rect x="345" y="30" width="270" height="460" class="box-kernel"/>
    <text x="480" y="60" class="title-sec" text-anchor="middle" fill="#166534">Kernel SoftIRQ Bridge</text>

    <rect x="365" y="140" width="230" height="90" class="box-step"/>
    <text x="380" y="165" class="title-step">4. netif_rx() / napi</text>
    <text x="380" y="185" class="text-field">Enqueues skb to CPU</text>
    <text x="380" y="205" class="text-field">input_pkt_queue</text>

    <rect x="365" y="280" width="230" height="100" class="box-step"/>
    <text x="380" y="305" class="title-step">5. NET_RX_SOFTIRQ</text>
    <text x="380" y="325" class="text-field">Softirq daemon triggers</text>
    <text x="380" y="345" class="text-field">netif_receive_skb()</text>
    <text x="380" y="365" class="text-field">Crosses netns boundary</text>

    <path d="M 280 405 H 345 V 185 H 365" class="arrow-flow"/>
    <path d="M 480 230 V 280" class="arrow-flow"/>

    <!-- Section 3: Receiving Namespace / Host -->
    <rect x="660" y="30" width="270" height="460" class="box-ns"/>
    <text x="795" y="60" class="title-sec" text-anchor="middle">Root / Target Netns (Rx)</text>

    <rect x="680" y="140" width="230" height="90" class="box-step"/>
    <text x="695" y="165" class="title-step">6. L2/L3 Processing</text>
    <text x="695" y="185" class="text-field">Bridge br0 or ip_rcv()</text>
    <text x="695" y="205" class="text-field">FIB route lookup</text>

    <rect x="680" y="280" width="230" height="90" class="box-step"/>
    <text x="695" y="305" class="title-step">7. Netfilter Hooks</text>
    <text x="695" y="325" class="text-field">PREROUTING / FORWARD</text>
    <text x="695" y="345" class="text-field">NAT Masquerade check</text>

    <rect x="680" y="410" width="230" height="65" class="box-step"/>
    <text x="695" y="435" class="title-step">8. Socket Delivery</text>
    <text x="695" y="455" class="text-field">skb_queue_tail() -> app</text>

    <path d="M 595 330 H 680 V 230" class="arrow-flow"/>
    <path d="M 795 230 V 280" class="arrow-flow"/>
    <path d="M 795 370 V 410" class="arrow-flow"/>
</svg>"""
    with open(os.path.join(IMG_DIR, "netns-packet-flow.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

def render():
    os.makedirs(IMG_DIR, exist_ok=True)
    create_kernel_structs_svg()
    create_topology_svg()
    create_packet_flow_svg()
    print("Generated 3 figures in img/")

if __name__ == "__main__":
    render()
