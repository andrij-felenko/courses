import os
import sys

def render():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    # Figure 1: AF_XDP Architecture Overview
    svg1_path = os.path.join(img_dir, "af-xdp-arch.svg")
    svg1_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620">
    <style>
        .bg { fill: #f8fafc; }
        .panel-user { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 10px; }
        .panel-kernel { fill: #fff7ed; stroke: #ea580c; stroke-width: 2; rx: 10px; }
        .panel-nic { fill: #f1f5f9; stroke: #475569; stroke-width: 2; rx: 10px; }
        
        .box-umem { fill: #dbeafe; stroke: #1d4ed8; stroke-width: 1.5; rx: 6px; }
        .box-ring-fill { fill: #fef3c7; stroke: #d97706; stroke-width: 1.5; rx: 6px; }
        .box-ring-rx { fill: #dcfce7; stroke: #15803d; stroke-width: 1.5; rx: 6px; }
        .box-ring-tx { fill: #fee2e2; stroke: #dc2626; stroke-width: 1.5; rx: 6px; }
        .box-ring-comp { fill: #f3e8ff; stroke: #7e22ce; stroke-width: 1.5; rx: 6px; }
        
        .box-ebpf { fill: #ffedd5; stroke: #c2410c; stroke-width: 1.5; rx: 6px; }
        .box-xskmap { fill: #fed7aa; stroke: #ea580c; stroke-width: 1.5; rx: 6px; }
        .box-dma { fill: #e2e8f0; stroke: #334155; stroke-width: 1.5; rx: 6px; }
        
        .title-panel { font-family: monospace; font-size: 16px; font-weight: bold; }
        .title-panel-user { fill: #1e40af; }
        .title-panel-kernel { fill: #9a3412; }
        .title-panel-nic { fill: #1e293b; }
        
        .text-bold { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .text-sub { font-family: monospace; font-size: 12px; fill: #475569; }
        .text-code { font-family: monospace; font-size: 12px; fill: #1e293b; }
        
        .arrow-blue { stroke: #2563eb; stroke-width: 2; fill: none; marker-end: url(#arrowhead-blue); }
        .arrow-green { stroke: #16a34a; stroke-width: 2; fill: none; marker-end: url(#arrowhead-green); }
        .arrow-red { stroke: #dc2626; stroke-width: 2; fill: none; marker-end: url(#arrowhead-red); }
        .arrow-purple { stroke: #7e22ce; stroke-width: 2; fill: none; marker-end: url(#arrowhead-purple); }
        .arrow-orange { stroke: #ea580c; stroke-width: 2; stroke-dasharray: 4,4; fill: none; marker-end: url(#arrowhead-orange); }
    </style>

    <defs>
        <marker id="arrowhead-blue" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#2563eb"/>
        </marker>
        <marker id="arrowhead-green" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#16a34a"/>
        </marker>
        <marker id="arrowhead-red" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#dc2626"/>
        </marker>
        <marker id="arrowhead-purple" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#7e22ce"/>
        </marker>
        <marker id="arrowhead-orange" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#ea580c"/>
        </marker>
    </defs>

    <!-- Background -->
    <rect width="960" height="620" class="bg"/>

    <!-- User Space Panel -->
    <rect x="30" y="30" width="900" height="230" class="panel-user"/>
    <text x="50" y="58" class="title-panel title-panel-user">USER SPACE (AF_XDP Application &amp; Ring Interfaces)</text>

    <!-- UMEM Area -->
    <rect x="50" y="80" width="380" height="155" class="box-umem"/>
    <text x="65" y="105" class="text-bold">UMEM (Shared Memory Area)</text>
    <text x="65" y="125" class="text-sub">Pinned Memory Chunks (2048/4096B)</text>

    <!-- Chunk representations -->
    <rect x="65" y="140" width="80" height="80" fill="#bfdbfe" stroke="#2563eb" rx="4"/>
    <text x="105" y="175" class="text-code" text-anchor="middle">Frame 0</text>
    <text x="105" y="195" class="text-sub" text-anchor="middle">0x0000</text>

    <rect x="155" y="140" width="80" height="80" fill="#bfdbfe" stroke="#2563eb" rx="4"/>
    <text x="195" y="175" class="text-code" text-anchor="middle">Frame 1</text>
    <text x="195" y="195" class="text-sub" text-anchor="middle">0x0800</text>

    <rect x="245" y="140" width="80" height="80" fill="#bfdbfe" stroke="#2563eb" rx="4"/>
    <text x="285" y="175" class="text-code" text-anchor="middle">Frame 2</text>
    <text x="285" y="195" class="text-sub" text-anchor="middle">0x1000</text>

    <rect x="335" y="85" width="85" height="80" fill="#bfdbfe" stroke="#2563eb" rx="4"/>
    <text x="377" y="120" class="text-code" text-anchor="middle">Frame N</text>
    <text x="377" y="140" class="text-sub" text-anchor="middle">0x...</text>

    <!-- Four Lock-free SPSC Rings -->
    <!-- Fill Ring -->
    <rect x="460" y="80" width="220" height="70" class="box-ring-fill"/>
    <text x="475" y="102" class="text-bold">FILL Ring (Prod: App)</text>
    <text x="475" y="122" class="text-sub">Supplies empty UMEM addrs</text>
    <text x="475" y="138" class="text-code">[0x0000, 0x0800, ...]</text>

    <!-- Completion Ring -->
    <rect x="695" y="80" width="225" height="70" class="box-ring-comp"/>
    <text x="710" y="102" class="text-bold">COMPLETION Ring (Cons: App)</text>
    <text x="710" y="122" class="text-sub">Recycles sent TX addrs</text>
    <text x="710" y="138" class="text-code">[0x1000 freed]</text>

    <!-- Rx Ring -->
    <rect x="460" y="165" width="220" height="70" class="box-ring-rx"/>
    <text x="475" y="187" class="text-bold">RX Ring (Cons: App)</text>
    <text x="475" y="207" class="text-sub">Recv packet descriptors</text>
    <text x="475" y="223" class="text-code">[addr: 0x0000, len: 64]</text>

    <!-- Tx Ring -->
    <rect x="695" y="165" width="225" height="70" class="box-ring-tx"/>
    <text x="710" y="187" class="text-bold">TX Ring (Prod: App)</text>
    <text x="710" y="207" class="text-sub">Transmit packet descriptors</text>
    <text x="710" y="223" class="text-code">[addr: 0x1000, len: 128]</text>

    <!-- Kernel Space Panel -->
    <rect x="30" y="280" width="900" height="180" class="panel-kernel"/>
    <text x="50" y="308" class="title-panel title-panel-kernel">KERNEL SPACE (eBPF XDP Driver Subsystem)</text>

    <!-- eBPF XDP Engine -->
    <rect x="50" y="330" width="360" height="110" class="box-ebpf"/>
    <text x="65" y="355" class="text-bold">eBPF XDP Program (Driver Level Hook)</text>
    <text x="65" y="378" class="text-code">1. Parse Ethernet / IP / UDP headers</text>
    <text x="65" y="398" class="text-code">2. Target queue index match</text>
    <text x="65" y="418" class="text-code">3. return bpf_redirect_map(&amp;xsk_map, qid, 0);</text>

    <!-- XSKMAP -->
    <rect x="440" y="330" width="220" height="110" class="box-xskmap"/>
    <text x="455" y="355" class="text-bold">BPF_MAP_TYPE_XSKMAP</text>
    <text x="455" y="380" class="text-sub">Map Queue ID -&gt; AF_XDP Sock</text>
    <text x="455" y="405" class="text-code">Queue 0 -&gt; xsk_fd_0</text>
    <text x="455" y="425" class="text-code">Queue 1 -&gt; xsk_fd_1</text>

    <!-- AF_XDP Socket Kernel Core -->
    <rect x="680" y="330" width="235" height="110" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5" rx="6"/>
    <text x="695" y="355" class="text-bold">AF_XDP Socket (xsk.c)</text>
    <text x="695" y="380" class="text-sub">Zero-Copy Buffer Pool</text>
    <text x="695" y="400" class="text-code">ndo_xsk_wakeup()</text>
    <text x="695" y="420" class="text-code">xsk_buff_pool / DMA map</text>

    <!-- Hardware NIC Panel -->
    <rect x="30" y="480" width="900" height="110" class="panel-nic"/>
    <text x="50" y="508" class="title-panel title-panel-nic">HARDWARE NIC</text>

    <rect x="50" y="525" width="260" height="50" class="box-dma"/>
    <text x="65" y="547" class="text-bold">RX Queue &amp; DMA Engine</text>
    <text x="65" y="563" class="text-sub">Fetches UMEM addr via DMA</text>

    <rect x="340" y="525" width="260" height="50" class="box-dma"/>
    <text x="355" y="547" class="text-bold">Zero-Copy Driver Handler</text>
    <text x="355" y="563" class="text-sub">ixgbe / i40e / ice / mlx5</text>

    <rect x="630" y="525" width="285" height="50" class="box-dma"/>
    <text x="645" y="547" class="text-bold">TX Queue &amp; Wire Transmission</text>
    <text x="645" y="563" class="text-sub">Direct DMA from UMEM frame to wire</text>

    <!-- Clean Routed Arrows -->
    <!-- 1. Fill Ring -> AF_XDP Socket (via gap x=688) -->
    <path d="M 680 115 H 688 V 270 H 790 V 330" class="arrow-blue"/>
    
    <!-- 2. eBPF -> XSKMAP -->
    <path d="M 410 385 H 440" class="arrow-orange"/>
    
    <!-- 3. XSKMAP -> AF_XDP Socket -->
    <path d="M 660 385 H 680" class="arrow-orange"/>

    <!-- 4. AF_XDP Socket -> RX Ring (via gap x=688) -->
    <path d="M 740 330 V 270 H 688 V 200 H 680" class="arrow-green"/>

    <!-- 5. TX Ring -> AF_XDP Socket (direct vertically at x=800) -->
    <path d="M 800 235 V 330" class="arrow-red"/>

    <!-- 6. AF_XDP Socket -> Completion Ring (around TX ring via right gap x=925) -->
    <path d="M 860 330 V 270 H 925 V 115 H 920" class="arrow-purple"/>

    <!-- 7. DMA NIC <-> UMEM (via middle gap x=425) -->
    <path d="M 180 525 V 465 H 425 V 160 H 430" class="arrow-blue" stroke-dasharray="3,3"/>

</svg>"""

    with open(svg1_path, "w", encoding="utf-8") as f:
        f.write(svg1_content)
    print(f"Generated {svg1_path}")

    # Figure 2: AF_XDP Packet Life Cycle & Ring Operations
    svg2_path = os.path.join(img_dir, "af-xdp-ring-flow.svg")
    svg2_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
    <style>
        .bg { fill: #f8fafc; }
        .box-step { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.5; rx: 8px; }
        .box-num { fill: #2563eb; rx: 12px; }
        .text-num { font-family: monospace; font-size: 14px; font-weight: bold; fill: #ffffff; }
        
        .title-step { font-family: monospace; font-size: 14px; font-weight: bold; fill: #0f172a; }
        .text-body { font-family: monospace; font-size: 12px; fill: #334155; }
        .text-code { font-family: monospace; font-size: 12px; font-weight: bold; fill: #1e293b; }
        
        .box-fill { fill: #fef3c7; stroke: #d97706; stroke-width: 1; rx: 4px; }
        .box-rx { fill: #dcfce7; stroke: #15803d; stroke-width: 1; rx: 4px; }
        .box-tx { fill: #fee2e2; stroke: #dc2626; stroke-width: 1; rx: 4px; }
        .box-comp { fill: #f3e8ff; stroke: #7e22ce; stroke-width: 1; rx: 4px; }
        
        .arrow { stroke: #64748b; stroke-width: 2; fill: none; marker-end: url(#arrowhead-step); }
    </style>

    <defs>
        <marker id="arrowhead-step" markerWidth="9" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 9 3, 0 6" fill="#64748b"/>
        </marker>
    </defs>

    <!-- Background -->
    <rect width="960" height="540" class="bg"/>

    <!-- Step 1 -->
    <rect x="40" y="40" width="420" height="130" class="box-step"/>
    <rect x="55" y="55" width="24" height="24" class="box-num"/>
    <text x="67" y="72" class="text-num" text-anchor="middle">1</text>
    <text x="90" y="72" class="title-step">Поповнення Fill Ring (Userspace)</text>
    <text x="55" y="100" class="text-body">Додаток виділяє адреси вільних кадрів у UMEM</text>
    <text x="55" y="120" class="text-body">і додає їх у Fill Ring для майбутніх пакетів.</text>
    <rect x="55" y="132" width="390" height="26" class="box-fill"/>
    <text x="65" y="150" class="text-code">Fill Ring Addrs: [0x0000, 0x0800, 0x1000]</text>

    <!-- Step 2 -->
    <rect x="500" y="40" width="420" height="130" class="box-step"/>
    <rect x="515" y="55" width="24" height="24" class="box-num"/>
    <text x="527" y="72" class="text-num" text-anchor="middle">2</text>
    <text x="550" y="72" class="title-step">Zero-Copy DMA прийом (NIC &amp; XDP)</text>
    <text x="515" y="100" class="text-body">NIC бере 0x0000 з Fill Ring, виконує DMA,</text>
    <text x="515" y="120" class="text-body">eBPF XDP повертає bpf_redirect_map(XSKMAP).</text>
    <rect x="515" y="132" width="390" height="26" class="box-rx"/>
    <text x="525" y="150" class="text-code">RX Ring Desc: { addr: 0x0000, len: 128 }</text>

    <!-- Step 3 -->
    <rect x="40" y="210" width="420" height="130" class="box-step"/>
    <rect x="55" y="225" width="24" height="24" class="box-num"/>
    <text x="67" y="242" class="text-num" text-anchor="middle">3</text>
    <text x="90" y="242" class="title-step">Обробка в Userspace (Zero-Copy Read)</text>
    <text x="55" y="270" class="text-body">Додаток зчитує дескриптор з RX Ring</text>
    <text x="55" y="290" class="text-body">і читає/модифікує пакет прямо в UMEM[0x0000].</text>
    <rect x="55" y="302" width="390" height="26" fill="#eff6ff" stroke="#2563eb" rx="4"/>
    <text x="65" y="320" class="text-code">Payload in UMEM: 0x0000 + offset (No copy)</text>

    <!-- Step 4 -->
    <rect x="500" y="210" width="420" height="130" class="box-step"/>
    <rect x="515" y="225" width="24" height="24" class="box-num"/>
    <text x="527" y="242" class="text-num" text-anchor="middle">4</text>
    <text x="550" y="242" class="title-step">Відправка через TX Ring (Userspace)</text>
    <text x="515" y="270" class="text-body">Додаток вміщує дескриптор у TX Ring і</text>
    <text x="515" y="290" class="text-body">викликає sendto() (або use NEED_WAKEUP).</text>
    <rect x="515" y="302" width="390" height="26" class="box-tx"/>
    <text x="525" y="320" class="text-code">TX Ring Desc: { addr: 0x0000, len: 128 }</text>

    <!-- Step 5 -->
    <rect x="270" y="380" width="420" height="130" class="box-step"/>
    <rect x="285" y="395" width="24" height="24" class="box-num"/>
    <text x="297" y="412" class="text-num" text-anchor="middle">5</text>
    <text x="320" y="412" class="title-step">Завершення передачи &amp; Reclaim (Kernel)</text>
    <text x="285" y="440" class="text-body">NIC передає кадр у мережу, ядро повертає</text>
    <text x="285" y="460" class="text-body">адресу 0x0000 у Completion Ring для повторного вжитку.</text>
    <rect x="285" y="472" width="390" height="26" class="box-comp"/>
    <text x="295" y="490" class="text-code">Completion Ring Addr: 0x0000 (Freed)</text>

    <!-- Arrows between steps -->
    <path d="M 460 105 H 500" class="arrow"/>
    <path d="M 710 170 V 210" class="arrow"/>
    <path d="M 500 275 H 460" class="arrow"/>
    <path d="M 250 340 V 445 H 270" class="arrow"/>

</svg>"""

    with open(svg2_path, "w", encoding="utf-8") as f:
        f.write(svg2_content)
    print(f"Generated {svg2_path}")

if __name__ == "__main__":
    render()
