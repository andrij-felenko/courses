def render():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="100%" height="100%" fill="#ffffff" />
    <!-- CPU and RAM -->
    <rect x="300" y="20" width="200" height="80" rx="10" fill="#e0e0e0" stroke="#333" stroke-width="2" />
    <text x="400" y="55" font-family="Arial" font-size="18" text-anchor="middle" font-weight="bold">CPU &amp; Root Complex</text>
    
    <rect x="550" y="30" width="120" height="60" rx="5" fill="#cce5ff" stroke="#333" stroke-width="2" />
    <text x="610" y="65" font-family="Arial" font-size="16" text-anchor="middle">System RAM</text>
    <line x1="500" y1="60" x2="550" y2="60" stroke="#333" stroke-width="3" />
    
    <!-- PCIe Switch -->
    <rect x="330" y="150" width="140" height="60" rx="10" fill="#ffe5cc" stroke="#333" stroke-width="2" />
    <text x="400" y="185" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold">PCIe Switch</text>
    <line x1="400" y1="100" x2="400" y2="150" stroke="#333" stroke-width="4" />
    
    <!-- GPU -->
    <rect x="150" y="250" width="140" height="80" rx="10" fill="#d5f5e3" stroke="#333" stroke-width="2" />
    <text x="220" y="285" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold">GPU</text>
    <text x="220" y="310" font-family="Arial" font-size="14" text-anchor="middle">VRAM</text>
    
    <!-- NVMe SSD -->
    <rect x="510" y="250" width="140" height="80" rx="10" fill="#fcf3cf" stroke="#333" stroke-width="2" />
    <text x="580" y="285" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold">NVMe SSD</text>
    <text x="580" y="310" font-family="Arial" font-size="14" text-anchor="middle">CMB</text>
    
    <!-- PCIe Links -->
    <line x1="350" y1="210" x2="220" y2="250" stroke="#333" stroke-width="4" />
    <line x1="450" y1="210" x2="580" y2="250" stroke="#333" stroke-width="4" />
    
    <!-- P2PDMA Path -->
    <path d="M 230 240 Q 400 170 570 240" fill="none" stroke="#e74c3c" stroke-width="4" stroke-dasharray="10,10" />
    <polygon points="560,230 575,243 555,248" fill="#e74c3c" />
    <text x="400" y="220" font-family="Arial" font-size="14" text-anchor="middle" fill="#e74c3c" font-weight="bold">P2PDMA (TLP Routing)</text>
</svg>"""

if __name__ == "__main__":
    with open("p2pdma-arch.svg", "w") as f:
        f.write(render())
