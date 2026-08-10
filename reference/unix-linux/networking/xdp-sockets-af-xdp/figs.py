import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <rect width="100%" height="100%" fill="#f4f4f4"/>
    <rect x="50" y="50" width="700" height="500" fill="#ffffff" stroke="#ccc" stroke-width="2"/>
    <text x="400" y="100" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">AF_XDP Architecture</text>
    
    <!-- User Space -->
    <rect x="100" y="150" width="250" height="350" fill="#e0f7fa" stroke="#00bcd4" stroke-width="2"/>
    <text x="225" y="180" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold">User Space (AF_XDP)</text>
    
    <!-- UMEM -->
    <rect x="120" y="220" width="210" height="80" fill="#b2ebf2" stroke="#0097a7" stroke-width="2"/>
    <text x="225" y="255" font-family="sans-serif" font-size="16" text-anchor="middle">UMEM</text>
    <text x="225" y="275" font-family="sans-serif" font-size="12" text-anchor="middle">(Packet Buffers)</text>
    
    <!-- Rings -->
    <rect x="120" y="320" width="100" height="60" fill="#ffecb3" stroke="#ffc107" stroke-width="2"/>
    <text x="170" y="355" font-family="sans-serif" font-size="14" text-anchor="middle">Fill Ring</text>
    
    <rect x="230" y="320" width="100" height="60" fill="#ffecb3" stroke="#ffc107" stroke-width="2"/>
    <text x="280" y="355" font-family="sans-serif" font-size="14" text-anchor="middle">Comp Ring</text>
    
    <rect x="120" y="400" width="100" height="60" fill="#c8e6c9" stroke="#4caf50" stroke-width="2"/>
    <text x="170" y="435" font-family="sans-serif" font-size="14" text-anchor="middle">Rx Ring</text>
    
    <rect x="230" y="400" width="100" height="60" fill="#c8e6c9" stroke="#4caf50" stroke-width="2"/>
    <text x="280" y="435" font-family="sans-serif" font-size="14" text-anchor="middle">Tx Ring</text>
    
    <!-- Kernel Space -->
    <rect x="450" y="150" width="250" height="350" fill="#ffe0b2" stroke="#ff9800" stroke-width="2"/>
    <text x="575" y="180" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold">Kernel Space</text>
    
    <!-- XDP Program -->
    <rect x="470" y="220" width="210" height="80" fill="#ffcc80" stroke="#f57c00" stroke-width="2"/>
    <text x="575" y="260" font-family="sans-serif" font-size="16" text-anchor="middle">eBPF XDP Program</text>
    <text x="575" y="280" font-family="sans-serif" font-size="14" text-anchor="middle">bpf_redirect_map()</text>
    
    <!-- NIC -->
    <rect x="470" y="350" width="210" height="110" fill="#cfd8dc" stroke="#607d8b" stroke-width="2"/>
    <text x="575" y="380" font-family="sans-serif" font-size="16" text-anchor="middle" font-weight="bold">NIC (Network Card)</text>
    <text x="575" y="410" font-family="sans-serif" font-size="14" text-anchor="middle">XDP_ZEROCOPY</text>
    
</svg>"""
    with open("af_xdp_arch.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Generated af_xdp_arch.svg")

if __name__ == "__main__":
    render()
