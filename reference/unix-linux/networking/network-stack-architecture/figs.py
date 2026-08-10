import sys

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">
    <rect x="0" y="0" width="800" height="600" fill="#f8f9fa"/>
    <text x="400" y="50" font-family="Arial" font-size="24" font-weight="bold" text-anchor="middle" fill="#333">Мережевий стек ядра Linux: TX / RX шлях</text>
    
    <!-- User Space -->
    <rect x="100" y="100" width="600" height="80" rx="10" fill="#e3f2fd" stroke="#1e88e5" stroke-width="2"/>
    <text x="400" y="130" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle" fill="#1565c0">User Space</text>
    <text x="400" y="160" font-family="Arial" font-size="14" text-anchor="middle" fill="#000">Application (Sockets, sendmsg/recvmsg)</text>
    
    <!-- Boundary -->
    <line x1="50" y1="200" x2="750" y2="200" stroke="#d32f2f" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="80" y="195" font-family="Arial" font-size="12" fill="#d32f2f">System Call Boundary</text>
    <text x="730" y="195" font-family="Arial" font-size="12" fill="#d32f2f" text-anchor="end">Kernel Space</text>

    <!-- Kernel Space - Socket Layer -->
    <rect x="100" y="220" width="600" height="60" rx="10" fill="#fff3e0" stroke="#fb8c00" stroke-width="2"/>
    <text x="400" y="255" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">Socket Layer (VFS, sock structure)</text>

    <!-- L4: TCP/UDP -->
    <rect x="100" y="300" width="600" height="60" rx="10" fill="#e8f5e9" stroke="#43a047" stroke-width="2"/>
    <text x="400" y="335" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">L4: Transport Layer (TCP, UDP, State Machine)</text>

    <!-- L3: IP Routing -->
    <rect x="100" y="380" width="600" height="60" rx="10" fill="#f3e5f5" stroke="#8e24aa" stroke-width="2"/>
    <text x="400" y="415" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">L3: Network Layer (IPv4/v6, Routing, Netfilter)</text>

    <!-- L2: Data Link & Qdisc -->
    <rect x="100" y="460" width="600" height="60" rx="10" fill="#eceff1" stroke="#546e7a" stroke-width="2"/>
    <text x="400" y="495" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">L2: Data Link Layer (Qdisc, TC, net_device)</text>

    <!-- Boundary Hardware -->
    <line x1="50" y1="540" x2="750" y2="540" stroke="#d32f2f" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="80" y="535" font-family="Arial" font-size="12" fill="#d32f2f">Hardware Boundary</text>
    
    <!-- Hardware -->
    <rect x="100" y="550" width="600" height="40" rx="10" fill="#d7ccc8" stroke="#6d4c41" stroke-width="2"/>
    <text x="400" y="575" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">NIC Hardware (TX/RX Ring, DMA, IRQ, NAPI)</text>
    
    <!-- Arrows TX -->
    <path d="M 200 180 L 200 220" stroke="#1e88e5" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 200 280 L 200 300" stroke="#fb8c00" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 200 360 L 200 380" stroke="#43a047" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 200 440 L 200 460" stroke="#8e24aa" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 200 520 L 200 550" stroke="#546e7a" stroke-width="3" marker-end="url(#arrow)"/>
    <text x="170" y="375" font-family="Arial" font-size="14" fill="#666" transform="rotate(-90 170,375)">TX (Transmission)</text>

    <!-- Arrows RX -->
    <path d="M 600 550 L 600 520" stroke="#546e7a" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 600 460 L 600 440" stroke="#8e24aa" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 600 380 L 600 360" stroke="#43a047" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 600 300 L 600 280" stroke="#fb8c00" stroke-width="3" marker-end="url(#arrow)"/>
    <path d="M 600 220 L 600 180" stroke="#1e88e5" stroke-width="3" marker-end="url(#arrow)"/>
    <text x="620" y="375" font-family="Arial" font-size="14" fill="#666" transform="rotate(-90 620,375)">RX (Reception)</text>

    <!-- Marker Definition -->
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
        </marker>
    </defs>
</svg>"""
    return svg_content

if __name__ == '__main__':
    print(render())
