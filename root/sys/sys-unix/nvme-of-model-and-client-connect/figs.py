import sys
import os

def generate_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="700" height="400" viewBox="0 0 700 400">
    <rect width="100%" height="100%" fill="white"/>

    <text x="350" y="30" font-family="sans-serif" font-size="16" text-anchor="middle" font-weight="bold">NVMe-oF Queue Architecture</text>

    <!-- Initiator Side -->
    <g transform="translate(40, 50)">
        <rect width="200" height="250" fill="#f0f0f0" stroke="black" stroke-width="2"/>
        <text x="100" y="20" font-family="sans-serif" font-size="14" text-anchor="middle" font-weight="bold">Initiator (Host)</text>
        
        <rect x="20" y="40" width="160" height="60" fill="#cce5ff" stroke="#004085"/>
        <text x="100" y="75" font-family="sans-serif" font-size="12" text-anchor="middle">CPU Core 0 (SQ/CQ)</text>

        <rect x="20" y="120" width="160" height="60" fill="#cce5ff" stroke="#004085"/>
        <text x="100" y="155" font-family="sans-serif" font-size="12" text-anchor="middle">CPU Core 1 (SQ/CQ)</text>
        
        <rect x="20" y="200" width="160" height="30" fill="#d4edda" stroke="#155724"/>
        <text x="100" y="220" font-family="sans-serif" font-size="12" text-anchor="middle">Network Adapter</text>

        <path d="M 100 183 L 100 199" stroke="#004085" stroke-width="2" marker-end="url(#arrow)"/>
    </g>
    
    <!-- Network -->
    <path d="M 240 265 L 460 265" stroke="black" stroke-width="4" stroke-dasharray="5,5"/>
    <text x="350" y="252" font-family="sans-serif" font-size="12" text-anchor="middle">Fabric (TCP/RDMA/FC)</text>

    <!-- Target Side -->
    <g transform="translate(460, 50)">
        <rect width="200" height="250" fill="#f0f0f0" stroke="black" stroke-width="2"/>
        <text x="100" y="20" font-family="sans-serif" font-size="14" text-anchor="middle" font-weight="bold">Target (Subsystem)</text>
        
        <rect x="20" y="200" width="160" height="30" fill="#d4edda" stroke="#155724"/>
        <text x="100" y="220" font-family="sans-serif" font-size="12" text-anchor="middle">Network Adapter</text>

        <rect x="20" y="120" width="160" height="60" fill="#fff3cd" stroke="#856404"/>
        <text x="100" y="155" font-family="sans-serif" font-size="12" text-anchor="middle">nvmet (NVMe Target)</text>
        
        <rect x="20" y="40" width="160" height="60" fill="#f8d7da" stroke="#721c24"/>
        <text x="100" y="75" font-family="sans-serif" font-size="12" text-anchor="middle">NVMe SSD Controller</text>

        <path d="M 100 199 L 100 183" stroke="#004085" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 100 119 L 100 103" stroke="#004085" stroke-width="2" marker-end="url(#arrow)"/>
    </g>
    
    <!-- Arrows -->
    <text x="350" y="95" font-family="sans-serif" font-size="12" text-anchor="middle">NVMe command</text>
    <path d="M 240 110 L 460 110" stroke="#004085" stroke-width="2" marker-end="url(#arrow)"/>
    <path d="M 460 150 L 240 150" stroke="#004085" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="350" y="170" font-family="sans-serif" font-size="12" text-anchor="middle">Completion</text>

    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#004085" />
        </marker>
    </defs>
</svg>"""
    
    # Save the file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "nvme-of-queues.svg"), "w") as f:
        f.write(svg)

if __name__ == "__main__":
    generate_svg()
    print("Generated nvme-of-queues.svg")
