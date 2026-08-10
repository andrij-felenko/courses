import sys
import os

def draw_ioctl_vs_netlink():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#ffffff" />
    <text x="400" y="40" font-family="sans-serif" font-size="22" text-anchor="middle" font-weight="bold">Еволюція API налаштування мережі: ioctl vs Netlink</text>
    
    <rect x="40" y="70" width="720" height="70" fill="#e3f2fd" stroke="#1e88e5" stroke-width="2" rx="5"/>
    <text x="400" y="110" font-family="sans-serif" font-size="20" text-anchor="middle" fill="#0d47a1">Простір Користувача (User Space) - ethtool, iproute2</text>
    
    <line x1="40" y1="160" x2="760" y2="160" stroke="#757575" stroke-dasharray="8,4" stroke-width="2"/>
    <text x="750" y="155" font-family="sans-serif" font-size="12" text-anchor="end" fill="#757575">Кордон ядра (Kernel Boundary)</text>
    
    <rect x="40" y="180" width="720" height="200" fill="#e8f5e9" stroke="#43a047" stroke-width="2" rx="5"/>
    <text x="400" y="365" font-family="sans-serif" font-size="20" text-anchor="middle" fill="#1b5e20">Простір Ядра (Kernel Space)</text>
    
    <!-- IOCTL Path -->
    <path d="M 200 140 L 200 210" fill="none" stroke="#d32f2f" stroke-width="3" marker-end="url(#arrow_red)"/>
    <rect x="100" y="210" width="200" height="50" fill="#ffcdd2" stroke="#c62828" stroke-width="2" rx="5"/>
    <text x="200" y="240" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#b71c1c">ioctl(SIOCETHTOOL)</text>
    <text x="200" y="275" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#c62828">(Застарілий, блокуючий)</text>
    
    <!-- Netlink Path -->
    <path d="M 600 140 L 600 210" fill="none" stroke="#388e3c" stroke-width="3" marker-end="url(#arrow_green)"/>
    <rect x="500" y="210" width="200" height="50" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2" rx="5"/>
    <text x="600" y="240" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#1b5e20">Generic Netlink (ethtool)</text>
    <text x="600" y="275" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#2e7d32">(Асинхронний, розширюваний)</text>
    
    <!-- Ethtool Core -->
    <rect x="300" y="300" width="200" height="40" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="5"/>
    <text x="400" y="325" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#f57f17">Ethtool Core &amp; Drivers</text>
    
    <path d="M 200 260 L 200 320 L 300 320" fill="none" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrow_red)"/>
    <path d="M 600 260 L 600 320 L 500 320" fill="none" stroke="#388e3c" stroke-width="2" marker-end="url(#arrow_green)"/>
    
    <defs>
        <marker id="arrow_red" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#d32f2f" />
        </marker>
        <marker id="arrow_green" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#388e3c" />
        </marker>
    </defs>
</svg>"""
    return svg

def render():
    figs = {
        "ethtool_arch.svg": draw_ioctl_vs_netlink()
    }
    for name, content in figs.items():
        with open(name, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    render()
