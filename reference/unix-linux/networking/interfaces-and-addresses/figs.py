import os
import sys

def render():
    os.makedirs("img", exist_ok=True)
    svg_path = os.path.join("img", "interfaces-addresses.svg")

    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520">
    <style>
        .bg { fill: #f8fafc; }
        .box-kernel { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-l3 { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-addr { fill: #dcfce7; stroke: #15803d; stroke-width: 1.5; rx: 6px; }
        .box-user { fill: #fefce8; stroke: #ca8a04; stroke-width: 2; rx: 8px; }
        .title-kernel { font-family: monospace; font-size: 16px; font-weight: bold; fill: #1e40af; }
        .title-l3 { font-family: monospace; font-size: 16px; font-weight: bold; fill: #166534; }
        .title-user { font-family: monospace; font-size: 16px; font-weight: bold; fill: #854d0e; }
        .text-field { font-family: monospace; font-size: 13px; fill: #334155; }
        .text-bold { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .arrow { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrowhead-green); }
        .arrow-yellow { stroke: #ca8a04; stroke-width: 2; fill: none; marker-end: url(#arrowhead-yellow); }
    </style>

    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
        </marker>
        <marker id="arrowhead-yellow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ca8a04"/>
        </marker>
    </defs>

    <!-- Background -->
    <rect width="960" height="520" class="bg"/>

    <!-- Kernel L2 Layer: struct net_device -->
    <rect x="30" y="30" width="310" height="460" class="box-kernel"/>
    <text x="185" y="60" class="title-kernel" text-anchor="middle">struct net_device (L2)</text>

    <text x="50" y="95" class="text-bold">name: "eth0"</text>
    <text x="50" y="120" class="text-field">ifindex: 2</text>
    <text x="50" y="145" class="text-field">dev_addr: 52:54:00:12:34:56</text>
    <text x="50" y="170" class="text-field">type: ARPHRD_ETHER</text>
    <text x="50" y="195" class="text-field">mtu: 1500</text>
    <text x="50" y="220" class="text-field">flags: IFF_UP | IFF_RUNNING</text>
    <text x="50" y="245" class="text-field">state: __LINK_STATE_START</text>
    <text x="50" y="270" class="text-field">operstate: IF_OPER_UP</text>

    <line x1="50" y1="290" x2="320" y2="290" stroke="#cbd5e1" stroke-width="1"/>

    <text x="50" y="315" class="text-bold">netdev_ops:</text>
    <text x="70" y="340" class="text-field">.ndo_start_xmit</text>
    <text x="70" y="365" class="text-field">.ndo_open / .ndo_stop</text>
    <text x="70" y="390" class="text-field">.ndo_set_mac_address</text>

    <line x1="50" y1="410" x2="320" y2="410" stroke="#cbd5e1" stroke-width="1"/>

    <text x="50" y="435" class="text-bold">ip_ptr ────────────────►</text>
    <text x="50" y="465" class="text-bold">ip6_ptr ───────────────►</text>

    <!-- Pointer arrow from ip_ptr (x=240, y=431) routed cleanly to in_device (x=390, y=431) -->
    <path d="M 230 431 H 390" class="arrow"/>

    <!-- Kernel L3 Layer: struct in_device -->
    <rect x="390" y="30" width="280" height="460" class="box-l3"/>
    <text x="530" y="60" class="title-l3" text-anchor="middle">struct in_device (L3 IPv4)</text>

    <text x="410" y="95" class="text-field">dev: -&gt; net_device</text>
    <text x="410" y="120" class="text-field">ifa_list: -&gt; struct in_ifaddr</text>
    <text x="410" y="145" class="text-field">mc_list: -&gt; struct ip_mc_list</text>

    <!-- in_ifaddr 1 (Primary) -->
    <rect x="410" y="175" width="240" height="135" class="box-addr"/>
    <text x="530" y="198" class="title-l3" text-anchor="middle">struct in_ifaddr (Primary)</text>
    <text x="420" y="223" class="text-field">ifa_local: 192.168.1.10</text>
    <text x="420" y="248" class="text-field">ifa_mask: 255.255.255.0 (/24)</text>
    <text x="420" y="273" class="text-field">ifa_broadcast: 192.168.1.255</text>
    <text x="420" y="298" class="text-field">ifa_scope: RT_SCOPE_UNIVERSE</text>

    <!-- in_ifaddr 2 (Secondary/Alias) -->
    <rect x="410" y="335" width="240" height="135" class="box-addr"/>
    <text x="530" y="358" class="title-l3" text-anchor="middle">struct in_ifaddr (Secondary)</text>
    <text x="420" y="383" class="text-field">ifa_local: 10.0.0.5</text>
    <text x="420" y="408" class="text-field">ifa_mask: 255.255.255.255 (/32)</text>
    <text x="420" y="433" class="text-field">ifa_flags: IFA_F_SECONDARY</text>
    <text x="420" y="458" class="text-field">ifa_scope: RT_SCOPE_HOST</text>

    <!-- Userspace and Subsystems -->
    <rect x="700" y="30" width="230" height="460" class="box-user"/>
    <text x="815" y="60" class="title-user" text-anchor="middle">Userspace &amp; Subsystems</text>

    <!-- Sysfs box -->
    <rect x="715" y="90" width="200" height="100" fill="#fef08a" stroke="#ca8a04" stroke-width="1.5" rx="4"/>
    <text x="815" y="115" class="title-user" text-anchor="middle">/sys/class/net/eth0/</text>
    <text x="725" y="140" class="text-field">operstate: "up"</text>
    <text x="725" y="165" class="text-field">carrier: "1"</text>

    <!-- RTNETLINK Socket Box -->
    <rect x="715" y="220" width="200" height="140" fill="#fef08a" stroke="#ca8a04" stroke-width="1.5" rx="4"/>
    <text x="815" y="245" class="title-user" text-anchor="middle">AF_NETLINK Socket</text>
    <text x="725" y="270" class="text-field">RTM_GETLINK / RTM_NEWLINK</text>
    <text x="725" y="295" class="text-field">RTM_GETADDR / RTM_NEWADDR</text>
    <text x="725" y="320" class="text-field">iproute2 / NetworkManager</text>

    <!-- PHY Interrupt & Link State box -->
    <rect x="715" y="380" width="200" height="90" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5" rx="4"/>
    <text x="815" y="405" font-family="monospace" font-size="14" font-weight="bold" fill="#991b1b" text-anchor="middle">PHY Driver Interrupt</text>
    <text x="725" y="430" class="text-field">netif_carrier_on()</text>
    <text x="725" y="455" class="text-field">IFF_RUNNING state set</text>

    <!-- Routing arrows cleanly around middle box via top/bottom margins -->
    <!-- PHY Interrupt -> net_device (bottom route below in_device box) -->
    <path d="M 715 425 H 680 V 500 H 185 V 490" class="arrow" stroke="#dc2626" marker-end="url(#arrowhead)"/>

    <!-- Netlink -> net_device (top route above in_device box) -->
    <path d="M 715 290 H 680 V 15 H 185 V 30" class="arrow-yellow"/>
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {svg_path}")

if __name__ == "__main__":
    render()
