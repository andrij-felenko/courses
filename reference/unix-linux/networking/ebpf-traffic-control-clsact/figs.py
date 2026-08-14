import os
import sys

def ensure_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def generate_fig1_packet_flow(img_dir):
    # Diagram: Linux Packet Flow with TC clsact hooks
    width = 850
    height = 420
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append('  <text x="425" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Шлях пакета в ядрі Linux: хуки XDP та TC clsact</text>')
    
    # NIC Ingress box
    svg.append('  <rect x="30" y="70" width="110" height="280" rx="8" fill="#f1f5f9" stroke="#64748b" stroke-width="2"/>')
    svg.append('  <text x="85" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Мережева</text>')
    svg.append('  <text x="85" y="115" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">карта (NIC)</text>')
    svg.append('  <rect x="42" y="145" width="86" height="45" rx="4" fill="#cbd5e1" stroke="#475569"/>')
    svg.append('  <text x="85" y="172" font-size="12" text-anchor="middle" fill="#1e293b">RX Ring</text>')
    svg.append('  <rect x="42" y="275" width="86" height="45" rx="4" fill="#cbd5e1" stroke="#475569"/>')
    svg.append('  <text x="85" y="302" font-size="12" text-anchor="middle" fill="#1e293b">TX Ring</text>')
    
    # Driver / XDP Hook
    svg.append('  <rect x="175" y="70" width="120" height="130" rx="8" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/>')
    svg.append('  <text x="235" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#991b1b">Драйвер NIC</text>')
    svg.append('  <rect x="187" y="115" width="96" height="65" rx="6" fill="#fee2e2" stroke="#dc2626"/>')
    svg.append('  <text x="235" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#991b1b">XDP Hook</text>')
    svg.append('  <text x="235" y="162" font-size="11" text-anchor="middle" fill="#7f1d1d">(xdp_buff)</text>')
    
    # skb allocation boundary
    svg.append('  <line x1="315" y1="60" x2="315" y2="370" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg.append('  <text x="315" y="390" font-size="11" text-anchor="middle" fill="#64748b">Виділення sk_buff</text>')
    
    # TC Ingress Hook (clsact)
    svg.append('  <rect x="345" y="70" width="140" height="130" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="415" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#1e40af">TC Ingress</text>')
    svg.append('  <rect x="357" y="115" width="116" height="65" rx="6" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="415" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e40af">clsact ingress</text>')
    svg.append('  <text x="415" y="162" font-size="11" text-anchor="middle" fill="#1e3a8a">(struct __sk_buff)</text>')
    
    # L3 IP Stack / Netfilter / Routing
    svg.append('  <rect x="515" y="70" width="150" height="280" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>')
    svg.append('  <text x="590" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#166534">Стек L3/L4 Linux</text>')
    svg.append('  <rect x="527" y="115" width="126" height="40" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="590" y="140" font-size="12" text-anchor="middle" fill="#14532d">Netfilter PRE_ROUTING</text>')
    svg.append('  <rect x="527" y="170" width="126" height="40" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="590" y="195" font-size="12" text-anchor="middle" fill="#14532d">Маршрутизація (IP)</text>')
    svg.append('  <rect x="527" y="225" width="126" height="40" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="590" y="250" font-size="12" text-anchor="middle" fill="#14532d">Сокет / cgroup</text>')
    svg.append('  <rect x="527" y="280" width="126" height="45" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="590" y="307" font-size="12" text-anchor="middle" fill="#14532d">Netfilter POST_ROUTING</text>')
    
    # TC Egress Hook (clsact)
    svg.append('  <rect x="345" y="220" width="140" height="130" rx="8" fill="#faf5ff" stroke="#a855f7" stroke-width="2"/>')
    svg.append('  <text x="415" y="245" font-size="14" font-weight="bold" text-anchor="middle" fill="#6b21a8">TC Egress</text>')
    svg.append('  <rect x="357" y="265" width="116" height="65" rx="6" fill="#f3e8ff" stroke="#9333ea"/>')
    svg.append('  <text x="415" y="290" font-size="13" font-weight="bold" text-anchor="middle" fill="#6b21a8">clsact egress</text>')
    svg.append('  <text x="415" y="312" font-size="11" text-anchor="middle" fill="#581c87">(struct __sk_buff)</text>')
    
    # Driver Egress
    svg.append('  <rect x="175" y="220" width="120" height="130" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>')
    svg.append('  <text x="235" y="255" font-size="14" font-weight="bold" text-anchor="middle" fill="#334155">Драйвер TX</text>')
    svg.append('  <text x="235" y="285" font-size="12" text-anchor="middle" fill="#475569">dev_hard_start_xmit</text>')
    
    # Arrows and Markers
    svg.append('  <defs>')
    svg.append('    <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#334155"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-red" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#dc2626"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#2563eb"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-purple" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#9333ea"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # Flow path lines
    # NIC -> Driver XDP
    svg.append('  <line x1="140" y1="145" x2="187" y2="145" stroke="#dc2626" stroke-width="2" marker-end="url(#arr-red)"/>')
    # XDP -> TC Ingress
    svg.append('  <line x1="283" y1="145" x2="357" y2="145" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    # TC Ingress -> L3 Stack
    svg.append('  <line x1="473" y1="145" x2="527" y2="145" stroke="#334155" stroke-width="2" marker-end="url(#arr)"/>')
    # L3 Stack -> TC Egress
    svg.append('  <line x1="527" y1="302" x2="473" y2="302" stroke="#9333ea" stroke-width="2" marker-end="url(#arr-purple)"/>')
    # TC Egress -> Driver TX
    svg.append('  <line x1="357" y1="295" x2="295" y2="295" stroke="#334155" stroke-width="2" marker-end="url(#arr)"/>')
    # Driver TX -> NIC TX
    svg.append('  <line x1="175" y1="295" x2="128" y2="295" stroke="#334155" stroke-width="2" marker-end="url(#arr)"/>')
    
    svg.append('</svg>')
    
    filepath = os.path.join(img_dir, "tc-clsact-packet-flow.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {filepath}")

def generate_fig2_skb_structure(img_dir):
    # Diagram: Memory layout of struct __sk_buff and direct packet access
    width = 850
    height = 360
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append('  <text x="425" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Структура __sk_buff та прямий доступ до пам\'яті пакета</text>')
    
    # Context struct container
    svg.append('  <rect x="40" y="65" width="220" height="260" rx="8" fill="#f8fafc" stroke="#475569" stroke-width="2"/>')
    svg.append('  <text x="150" y="92" font-size="15" font-weight="bold" text-anchor="middle" fill="#0f172a">struct __sk_buff</text>')
    
    fields = [
        ("u32 len", "#e2e8f0"),
        ("u32 pkt_type", "#e2e8f0"),
        ("u32 mark / priority", "#e2e8f0"),
        ("u32 ifindex", "#e2e8f0"),
        ("u32 data_meta", "#fef08a"),
        ("u32 data", "#bbf7d0"),
        ("u32 data_end", "#fecaca")
    ]
    
    y_pos = 110
    for name, fill_color in fields:
        svg.append(f'  <rect x="55" y="{y_pos}" width="190" height="26" rx="4" fill="{fill_color}" stroke="#94a3b8"/>')
        svg.append(f'  <text x="150" y="{y_pos+18}" font-size="12" font-family="monospace" text-anchor="middle" fill="#1e293b">{name}</text>')
        y_pos += 30

    # Packet Buffer Memory Layout
    svg.append('  <rect x="330" y="65" width="480" height="260" rx="8" fill="#fafafa" stroke="#64748b" stroke-width="2"/>')
    svg.append('  <text x="570" y="92" font-size="15" font-weight="bold" text-anchor="middle" fill="#0f172a">Буфер пам\'яті пакета (skb linear data)</text>')
    
    # Buffer blocks
    # Headroom / Metadata
    svg.append('  <rect x="350" y="120" width="90" height="110" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>')
    svg.append('  <text x="395" y="165" font-size="12" font-weight="bold" text-anchor="middle" fill="#854d0e">Headroom</text>')
    svg.append('  <text x="395" y="185" font-size="11" text-anchor="middle" fill="#854d0e">(data_meta)</text>')
    
    # Ethernet Header
    svg.append('  <rect x="440" y="120" width="90" height="110" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>')
    svg.append('  <text x="485" y="165" font-size="12" font-weight="bold" text-anchor="middle" fill="#14532d">Ethernet</text>')
    svg.append('  <text x="485" y="185" font-size="11" text-anchor="middle" fill="#14532d">14 байтів</text>')
    
    # IP Header
    svg.append('  <rect x="530" y="120" width="100" height="110" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>')
    svg.append('  <text x="580" y="165" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">IPv4 / IPv6</text>')
    svg.append('  <text x="580" y="185" font-size="11" text-anchor="middle" fill="#1e40af">20-40 байтів</text>')
    
    # TCP/UDP Header + Payload
    svg.append('  <rect x="630" y="120" width="120" height="110" fill="#f3e8ff" stroke="#9333ea" stroke-width="1.5"/>')
    svg.append('  <text x="690" y="165" font-size="12" font-weight="bold" text-anchor="middle" fill="#6b21a8">L4 + Payload</text>')
    svg.append('  <text x="690" y="185" font-size="11" text-anchor="middle" fill="#6b21a8">Дані пакета</text>')
    
    # Tailroom
    svg.append('  <rect x="750" y="120" width="40" height="110" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>')
    svg.append('  <text x="770" y="175" font-size="10" text-anchor="middle" fill="#64748b" transform="rotate(-90 770 175)">Tailroom</text>')
    
    # Pointer lines from struct __sk_buff to Buffer
    svg.append('  <defs>')
    svg.append('    <marker id="arr-green" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#16a34a"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-red" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#dc2626"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-yellow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#ca8a04"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # data_meta pointer -> 350
    svg.append('  <path d="M 245 243 L 310 243 L 350 243 L 350 232" fill="none" stroke="#ca8a04" stroke-width="2" stroke-dasharray="3,3" marker-end="url(#arr-yellow)"/>')
    svg.append('  <text x="300" y="235" font-size="11" text-anchor="middle" fill="#854d0e">data_meta</text>')
    
    # data pointer -> 440
    svg.append('  <path d="M 245 273 L 320 273 L 440 273 L 440 232" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-green)"/>')
    svg.append('  <text x="360" y="265" font-size="11" text-anchor="middle" fill="#15803d">skb->data</text>')
    
    # data_end pointer -> 750
    svg.append('  <path d="M 245 303 L 330 303 L 750 303 L 750 232" fill="none" stroke="#dc2626" stroke-width="2" marker-end="url(#arr-red)"/>')
    svg.append('  <text x="540" y="295" font-size="11" text-anchor="middle" fill="#b91c1c">skb->data_end</text>')
    
    # Boundary check note below
    svg.append('  <rect x="350" y="260" width="440" height="50" rx="6" fill="#eff6ff" stroke="#3b82f6"/>')
    svg.append('  <text x="570" y="280" font-size="12" font-weight="bold" text-anchor="middle" fill="#1d4ed8">Вимога BPF Verifier: Перевірка меж (Bounds Check)</text>')
    svg.append('  <text x="570" y="298" font-size="11" font-family="monospace" text-anchor="middle" fill="#1e40af">if ((void *)(hdr + 1) &gt; data_end) return TC_ACT_OK;</text>')
    
    svg.append('</svg>')
    
    filepath = os.path.join(img_dir, "skb-buffer-structure.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {filepath}")

def generate_fig3_redirect_pathways(img_dir):
    # Diagram: Fast-path redirection using bpf_redirect() vs traditional L3 routing
    width = 850
    height = 380
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append('  <text x="425" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Перенаправлення пакетів: bpf_redirect() проти звичайної маршрутизації</text>')
    
    # Source Interface eth0
    svg.append('  <rect x="40" y="70" width="160" height="270" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="120" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#1e40af">Інтерфейс eth0 (veth0)</text>')
    svg.append('  <rect x="55" y="115" width="130" height="60" rx="6" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="120" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e40af">TC Ingress Hook</text>')
    svg.append('  <text x="120" y="160" font-size="11" text-anchor="middle" fill="#1d4ed8">bpf_redirect(ifindex, 0)</text>')
    
    # Destination Interface eth1
    svg.append('  <rect x="650" y="70" width="160" height="270" rx="8" fill="#faf5ff" stroke="#a855f7" stroke-width="2"/>')
    svg.append('  <text x="730" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#6b21a8">Інтерфейс eth1 (veth1)</text>')
    svg.append('  <rect x="665" y="250" width="130" height="60" rx="6" fill="#f3e8ff" stroke="#9333ea"/>')
    svg.append('  <text x="730" y="275" font-size="13" font-weight="bold" text-anchor="middle" fill="#6b21a8">TX Ring / Egress</text>')
    svg.append('  <text x="730" y="295" font-size="11" text-anchor="middle" fill="#7e22ce">Вихід у мережу</text>')
    
    # Traditional Heavy Route Box (Middle Top)
    svg.append('  <rect x="250" y="70" width="350" height="120" rx="8" fill="#fff7ed" stroke="#f97316" stroke-width="2"/>')
    svg.append('  <text x="425" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#c2410c">Стандартний повільний шлях (Slow Path)</text>')
    svg.append('  <rect x="265" y="115" width="100" height="55" rx="4" fill="#ffedd5" stroke="#ea580c"/>')
    svg.append('  <text x="315" y="140" font-size="11" font-weight="bold" text-anchor="middle" fill="#9a3412">Netfilter / IPTables</text>')
    svg.append('  <text x="315" y="156" font-size="10" text-anchor="middle" fill="#9a3412">Conntrack lookup</text>')
    svg.append('  <rect x="375" y="115" width="100" height="55" rx="4" fill="#ffedd5" stroke="#ea580c"/>')
    svg.append('  <text x="425" y="140" font-size="11" font-weight="bold" text-anchor="middle" fill="#9a3412">FIB Route Lookup</text>')
    svg.append('  <text x="425" y="156" font-size="10" text-anchor="middle" fill="#9a3412">ip_route_input()</text>')
    svg.append('  <rect x="485" y="115" width="100" height="55" rx="4" fill="#ffedd5" stroke="#ea580c"/>')
    svg.append('  <text x="535" y="140" font-size="11" font-weight="bold" text-anchor="middle" fill="#9a3412">Neighbor / ARP</text>')
    svg.append('  <text x="535" y="156" font-size="10" text-anchor="middle" fill="#9a3412">neigh_resolve()</text>')
    
    # Direct eBPF Fastpath Box (Middle Bottom)
    svg.append('  <rect x="250" y="220" width="350" height="120" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>')
    svg.append('  <text x="425" y="245" font-size="14" font-weight="bold" text-anchor="middle" fill="#15803d">Прямий eBPF Fast-Path (bpf_redirect)</text>')
    svg.append('  <rect x="270" y="260" width="310" height="60" rx="6" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="425" y="283" font-size="13" font-weight="bold" text-anchor="middle" fill="#14532d">Обхід L3 маршрутизації та Netfilter</text>')
    svg.append('  <text x="425" y="303" font-size="11" text-anchor="middle" fill="#166534">Пряма передача skb на dev_queue_xmit(eth1)</text>')
    
    # Arrow Markers
    svg.append('  <defs>')
    svg.append('    <marker id="arr-orange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#ea580c"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-green" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#16a34a"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # Slow path line (top)
    svg.append('  <path d="M 185 145 L 220 145 L 220 130 L 250 130" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-dasharray="5,5" marker-end="url(#arr-orange)"/>')
    svg.append('  <path d="M 600 130 L 630 130 L 630 280 L 665 280" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-dasharray="5,5" marker-end="url(#arr-orange)"/>')
    
    # Fast path line (bottom)
    svg.append('  <path d="M 185 175 L 220 175 L 220 280 L 250 280" fill="none" stroke="#16a34a" stroke-width="3" marker-end="url(#arr-green)"/>')
    svg.append('  <path d="M 600 280 L 665 280" fill="none" stroke="#16a34a" stroke-width="3" marker-end="url(#arr-green)"/>')
    
    svg.append('</svg>')
    
    filepath = os.path.join(img_dir, "bpf-redirect-fastpath.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {filepath}")

def render():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = ensure_img_dir(base_dir)
    generate_fig1_packet_flow(img_dir)
    generate_fig2_skb_structure(img_dir)
    generate_fig3_redirect_pathways(img_dir)

if __name__ == "__main__":
    render()
