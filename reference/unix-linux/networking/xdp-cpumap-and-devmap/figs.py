import os
import sys

def ensure_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def generate_fig1_xdp_redirect_arch(img_dir):
    width = 900
    height = 460
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append('  <text x="450" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#0f172a">Загальна архітектура XDP Redirect: CPUMAP та DEVMAP</text>')
    
    # Ingress Section
    svg.append('  <rect x="30" y="70" width="160" height="350" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>')
    svg.append('  <text x="110" y="95" font-size="15" font-weight="bold" text-anchor="middle" fill="#1e293b">Вхідний вузол (RX)</text>')
    
    svg.append('  <rect x="45" y="115" width="130" height="50" rx="6" fill="#e2e8f0" stroke="#475569"/>')
    svg.append('  <text x="110" y="138" font-size="13" font-weight="bold" text-anchor="middle" fill="#0f172a">RX Ring (NIC)</text>')
    svg.append('  <text x="110" y="155" font-size="11" text-anchor="middle" fill="#475569">DMA кадр / Page</text>')
    
    svg.append('  <rect x="45" y="185" width="130" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/>')
    svg.append('  <text x="110" y="210" font-size="13" font-weight="bold" text-anchor="middle" fill="#991b1b">XDP Програма</text>')
    svg.append('  <text x="110" y="230" font-size="11" text-anchor="middle" fill="#7f1d1d">bpf_redirect_map()</text>')
    svg.append('  <text x="110" y="245" font-size="10" text-anchor="middle" fill="#991b1b">XDP_REDIRECT</text>')

    svg.append('  <rect x="45" y="275" width="130" height="60" rx="6" fill="#f1f5f9" stroke="#64748b"/>')
    svg.append('  <text x="110" y="300" font-size="12" font-weight="bold" text-anchor="middle" fill="#334155">xdp_do_redirect()</text>')
    svg.append('  <text x="110" y="318" font-size="11" text-anchor="middle" fill="#64748b">per-CPU scratchpad</text>')

    # Decision Split Node
    svg.append('  <polygon points="250,215 280,185 310,215 280,245" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    svg.append('  <text x="280" y="219" font-size="11" font-weight="bold" text-anchor="middle" fill="#92400e">Тип карти</text>')

    # Branch 1: CPUMAP
    svg.append('  <rect x="360" y="70" width="510" height="170" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="615" y="95" font-size="15" font-weight="bold" text-anchor="middle" fill="#1e40af">BPF_MAP_TYPE_CPUMAP (Розпаралелювання обробки)</text>')
    
    svg.append('  <rect x="380" y="115" width="140" height="100" rx="6" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="450" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e40af">lockless ptr_ring</text>')
    svg.append('  <text x="450" y="160" font-size="11" text-anchor="middle" fill="#1e3a8a">Черга на цільовий CPU</text>')
    svg.append('  <text x="450" y="180" font-size="10" text-anchor="middle" fill="#2563eb">xdp_frame (без skb)</text>')

    svg.append('  <rect x="545" y="115" width="140" height="100" rx="6" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="615" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e40af">Target CPU kthread</text>')
    svg.append('  <text x="615" y="160" font-size="11" text-anchor="middle" fill="#1e3a8a">xdp_cpu_kthread</text>')
    svg.append('  <text x="615" y="180" font-size="10" text-anchor="middle" fill="#2563eb">napi_alloc_skb()</text>')

    svg.append('  <rect x="710" y="115" width="145" height="100" rx="6" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="782" y="140" font-size="13" font-weight="bold" text-anchor="middle" fill="#14532d">Стек TCP/IP</text>')
    svg.append('  <text x="782" y="160" font-size="11" text-anchor="middle" fill="#166534">netif_receive_skb()</text>')
    svg.append('  <text x="782" y="180" font-size="10" text-anchor="middle" fill="#15803d">Сокети / Маршрут</text>')

    # Branch 2: DEVMAP
    svg.append('  <rect x="360" y="255" width="510" height="165" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>')
    svg.append('  <text x="615" y="280" font-size="15" font-weight="bold" text-anchor="middle" fill="#15803d">BPF_MAP_TYPE_DEVMAP (Пряма переадресація кадру)</text>')

    svg.append('  <rect x="380" y="300" width="140" height="100" rx="6" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="450" y="325" font-size="13" font-weight="bold" text-anchor="middle" fill="#14532d">Bulk Queue</text>')
    svg.append('  <text x="450" y="345" font-size="11" text-anchor="middle" fill="#166534">xdp_bulk_queue</text>')
    svg.append('  <text x="450" y="365" font-size="10" text-anchor="middle" fill="#15803d">Пакетне групування</text>')

    svg.append('  <rect x="545" y="300" width="140" height="100" rx="6" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="615" y="325" font-size="13" font-weight="bold" text-anchor="middle" fill="#14532d">Egress Driver</text>')
    svg.append('  <text x="615" y="345" font-size="11" text-anchor="middle" fill="#166534">ndo_xdp_xmit()</text>')
    svg.append('  <text x="615" y="365" font-size="10" text-anchor="middle" fill="#15803d">Пряма передача</text>')

    svg.append('  <rect x="710" y="300" width="145" height="100" rx="6" fill="#f1f5f9" stroke="#475569"/>')
    svg.append('  <text x="782" y="325" font-size="13" font-weight="bold" text-anchor="middle" fill="#0f172a">TX Ring (NIC)</text>')
    svg.append('  <text x="782" y="345" font-size="11" text-anchor="middle" fill="#475569">Вихідний порт</text>')
    svg.append('  <text x="782" y="365" font-size="10" text-anchor="middle" fill="#334155">Wire Speed</text>')

    # Connections
    svg.append('  <defs>')
    svg.append('    <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#475569"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#2563eb"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-green" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#16a34a"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')

    svg.append('  <line x1="175" y1="215" x2="250" y2="215" stroke="#475569" stroke-width="2" marker-end="url(#arr)"/>')
    
    # Choice to CPUMAP
    svg.append('  <path d="M 280 185 L 280 155 L 380 155" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    svg.append('  <line x1="520" y1="155" x2="545" y2="155" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    svg.append('  <line x1="685" y1="155" x2="710" y2="155" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')

    # Choice to DEVMAP
    svg.append('  <path d="M 280 245 L 280 350 L 380 350" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-green)"/>')
    svg.append('  <line x1="520" y1="350" x2="545" y2="350" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-green)"/>')
    svg.append('  <line x1="685" y1="350" x2="710" y2="350" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-green)"/>')

    svg.append('</svg>')
    
    with open(os.path.join(img_dir, "cpumap-devmap-arch.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

def generate_fig2_cpumap_pipeline(img_dir):
    width = 850
    height = 360
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    svg.append('  <text x="425" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#0f172a">Паралелізація обробки пакетів через BPF_MAP_TYPE_CPUMAP</text>')
    
    # RX CPU Box
    svg.append('  <rect x="30" y="70" width="220" height="250" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="140" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#1e40af">RX CPU (Первинне ядро)</text>')
    
    svg.append('  <rect x="45" y="115" width="190" height="40" rx="4" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="140" y="140" font-size="12" text-anchor="middle" fill="#1e3a8a">Обробка NAPI / IRQ</text>')
    
    svg.append('  <rect x="45" y="170" width="190" height="45" rx="4" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="140" y="190" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">XDP Program</text>')
    svg.append('  <text x="140" y="206" font-size="10" text-anchor="middle" fill="#1e3a8a">bpf_redirect_map(cpu_map, N)</text>')
    
    svg.append('  <rect x="45" y="230" width="190" height="70" rx="4" fill="#bfdbfe" stroke="#1d4ed8"/>')
    svg.append('  <text x="140" y="252" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">xdp_do_flush()</text>')
    svg.append('  <text x="140" y="270" font-size="11" text-anchor="middle" fill="#1e3a8a">Запис у ptr_ring без skb</text>')
    svg.append('  <text x="140" y="286" font-size="10" fill="#1d4ed8" text-anchor="middle">IPI / Wakeup trigger</text>')

    # Lockless Queue (ptr_ring)
    svg.append('  <rect x="290" y="130" width="230" height="130" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    svg.append('  <text x="405" y="155" font-size="14" font-weight="bold" text-anchor="middle" fill="#92400e">Кільцевий буфер ptr_ring</text>')
    svg.append('  <rect x="305" y="175" width="200" height="35" rx="4" fill="#fde68a" stroke="#b45309"/>')
    svg.append('  <text x="405" y="197" font-size="12" font-family="monospace" text-anchor="middle" fill="#78350f">[xdp_frame*] [xdp_frame*] ...</text>')
    svg.append('  <text x="405" y="232" font-size="11" text-anchor="middle" fill="#92400e">Конфігурований qsize (напр. 2048)</text>')
    svg.append('  <text x="405" y="247" font-size="10" text-anchor="middle" fill="#b45309">Lockless Producer/Consumer</text>')

    # Target CPU Box
    svg.append('  <rect x="560" y="70" width="260" height="250" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>')
    svg.append('  <text x="690" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#15803d">Target CPU N (Цільове ядро)</text>')

    svg.append('  <rect x="575" y="115" width="230" height="50" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="690" y="138" font-size="12" font-weight="bold" text-anchor="middle" fill="#14532d">kthread: xdp_cpu_kthread</text>')
    svg.append('  <text x="690" y="154" font-size="11" text-anchor="middle" fill="#166534">Вичитка пакетів із ptr_ring</text>')

    svg.append('  <rect x="575" y="178" width="230" height="50" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="690" y="200" font-size="12" font-weight="bold" text-anchor="middle" fill="#14532d">napi_alloc_skb() / SKB Alloc</text>')
    svg.append('  <text x="690" y="217" font-size="11" text-anchor="middle" fill="#166534">Паралельна аллокація SKB</text>')

    svg.append('  <rect x="575" y="240" width="230" height="65" rx="4" fill="#bbf7d0" stroke="#15803d"/>')
    svg.append('  <text x="690" y="263" font-size="12" font-weight="bold" text-anchor="middle" fill="#14532d">netif_receive_skb_core()</text>')
    svg.append('  <text x="690" y="280" font-size="11" text-anchor="middle" fill="#166534">Передача у стек TCP/IP / Netfilter</text>')
    svg.append('  <text x="690" y="296" font-size="10" text-anchor="middle" fill="#15803d">Локальний кеш L1/L2 цільового ядра</text>')

    # Arrows
    svg.append('  <defs>')
    svg.append('    <marker id="arr-b" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#2563eb"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-g" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#16a34a"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')

    svg.append('  <line x1="235" y1="195" x2="290" y2="195" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-b)"/>')
    svg.append('  <line x1="520" y1="195" x2="560" y2="195" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-g)"/>')

    svg.append('</svg>')

    with open(os.path.join(img_dir, "cpumap-pipeline.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

def generate_fig3_devmap_bulk_xmit(img_dir):
    width = 850
    height = 360
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">')
    svg.append('  <rect width="100%" height="100%" fill="#ffffff" />')
    
    svg.append('  <text x="425" y="32" font-size="18" font-weight="bold" text-anchor="middle" fill="#0f172a">Пакетна передача (Bulk Transmit) та переробка сторінок у DEVMAP</text>')

    # RX Interface
    svg.append('  <rect x="30" y="70" width="220" height="250" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="140" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#1e40af">RX Інтерфейс (eth0)</text>')

    svg.append('  <rect x="45" y="115" width="190" height="40" rx="4" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="140" y="140" font-size="12" text-anchor="middle" fill="#1e3a8a">Отримання кадра (page_pool)</text>')

    svg.append('  <rect x="45" y="170" width="190" height="55" rx="4" fill="#dbeafe" stroke="#2563eb"/>')
    svg.append('  <text x="140" y="192" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">XDP Rewrite &amp; Redirect</text>')
    svg.append('  <text x="140" y="210" font-size="10" text-anchor="middle" fill="#1e3a8a">L2 MAC Mod + bpf_redirect_map</text>')

    svg.append('  <rect x="45" y="240" width="190" height="60" rx="4" fill="#bfdbfe" stroke="#1d4ed8"/>')
    svg.append('  <text x="140" y="263" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">Конвертація в xdp_frame</text>')
    svg.append('  <text x="140" y="282" font-size="10" text-anchor="middle" fill="#1d4ed8">Перевірка HEADROOM &gt;= 256B</text>')

    # Bulk Queue
    svg.append('  <rect x="290" y="120" width="230" height="150" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>')
    svg.append('  <text x="405" y="145" font-size="14" font-weight="bold" text-anchor="middle" fill="#15803d">xdp_bulk_queue</text>')
    svg.append('  <rect x="305" y="165" width="200" height="40" rx="4" fill="#dcfce7" stroke="#16a34a"/>')
    svg.append('  <text x="405" y="189" font-size="12" font-family="monospace" text-anchor="middle" fill="#14532d">Пакетний буфер (до 16/64)</text>')
    svg.append('  <text x="405" y="225" font-size="11" text-anchor="middle" fill="#15803d">Виклик xdp_do_flush() наприкінці NAPI</text>')
    svg.append('  <text x="405" y="242" font-size="10" text-anchor="middle" fill="#166534">Мінімізація доступу до PCI-регістрів</text>')

    # TX Interface
    svg.append('  <rect x="560" y="70" width="260" height="250" rx="8" fill="#f8fafc" stroke="#475569" stroke-width="2"/>')
    svg.append('  <text x="690" y="95" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">TX Інтерфейс (eth1)</text>')

    svg.append('  <rect x="575" y="115" width="230" height="50" rx="4" fill="#e2e8f0" stroke="#475569"/>')
    svg.append('  <text x="690" y="138" font-size="12" font-weight="bold" text-anchor="middle" fill="#0f172a">ndo_xdp_xmit()</text>')
    svg.append('  <text x="690" y="154" font-size="11" text-anchor="middle" fill="#334155">Передача пачки xdp_frame</text>')

    svg.append('  <rect x="575" y="178" width="230" height="45" rx="4" fill="#cbd5e1" stroke="#334155"/>')
    svg.append('  <text x="690" y="205" font-size="12" font-weight="bold" text-anchor="middle" fill="#0f172a">TX Ring DMA</text>')

    svg.append('  <rect x="575" y="235" width="230" height="70" rx="4" fill="#fef2f2" stroke="#ef4444"/>')
    svg.append('  <text x="690" y="258" font-size="12" font-weight="bold" text-anchor="middle" fill="#991b1b">Рециклінг пам\'яті page_pool</text>')
    svg.append('  <text x="690" y="276" font-size="11" text-anchor="middle" fill="#7f1d1d">Повернення сторінок RX NIC</text>')
    svg.append('  <text x="690" y="292" font-size="10" text-anchor="middle" fill="#991b1b">Без повторної аллокації!</text>')

    # Arrows
    svg.append('  <defs>')
    svg.append('    <marker id="arr-b2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#2563eb"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-g2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#16a34a"/>')
    svg.append('    </marker>')
    svg.append('    <marker id="arr-r" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">')
    svg.append('      <path d="M0,0 L8,4 L0,8 Z" fill="#ef4444"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')

    svg.append('  <line x1="235" y1="195" x2="290" y2="195" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-b2)"/>')
    svg.append('  <line x1="520" y1="195" x2="560" y2="195" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-g2)"/>')

    # Page pool recycle loop back line
    svg.append('  <path d="M 575 270 L 270 270 L 270 135 L 235 135" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arr-r)"/>')
    svg.append('  <text x="400" y="285" font-size="10" fill="#dc2626" text-anchor="middle">Зворотний потік сторінок (Zero Copy Recycle)</text>')

    svg.append('</svg>')

    with open(os.path.join(img_dir, "devmap-bulk-xmit.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = ensure_img_dir(base_dir)
    generate_fig1_xdp_redirect_arch(img_dir)
    generate_fig2_cpumap_pipeline(img_dir)
    generate_fig3_devmap_bulk_xmit(img_dir)
    print("Successfully generated all SVG figures for xdp-cpumap-and-devmap.")

if __name__ == "__main__":
    main()
