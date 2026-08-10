import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#1e1e1e" />
    <text x="400" y="50" fill="#fff" font-family="sans-serif" font-size="24" text-anchor="middle">User Events Architecture</text>
    
    <!-- Userspace -->
    <rect x="50" y="100" width="300" height="200" fill="#2d2d2d" stroke="#007acc" stroke-width="2"/>
    <text x="200" y="130" fill="#007acc" font-family="sans-serif" font-size="20" text-anchor="middle">Userspace</text>
    
    <rect x="80" y="150" width="240" height="50" fill="#3c3c3c" rx="5"/>
    <text x="200" y="180" fill="#fff" font-family="sans-serif" font-size="16" text-anchor="middle">Application</text>
    
    <rect x="80" y="220" width="240" height="50" fill="#3c3c3c" rx="5"/>
    <text x="200" y="250" fill="#fff" font-family="sans-serif" font-size="16" text-anchor="middle">libtracefs / libtraceevent</text>
    
    <!-- Kernel -->
    <rect x="450" y="100" width="300" height="200" fill="#2d2d2d" stroke="#4caf50" stroke-width="2"/>
    <text x="600" y="130" fill="#4caf50" font-family="sans-serif" font-size="20" text-anchor="middle">Kernel (Linux 5.18+)</text>
    
    <rect x="480" y="150" width="240" height="50" fill="#3c3c3c" rx="5"/>
    <text x="600" y="180" fill="#fff" font-family="sans-serif" font-size="16" text-anchor="middle">user_events_data (mmap/write)</text>
    
    <rect x="480" y="220" width="110" height="50" fill="#3c3c3c" rx="5"/>
    <text x="535" y="250" fill="#fff" font-family="sans-serif" font-size="16" text-anchor="middle">ftrace</text>
    
    <rect x="610" y="220" width="110" height="50" fill="#3c3c3c" rx="5"/>
    <text x="665" y="250" fill="#fff" font-family="sans-serif" font-size="16" text-anchor="middle">eBPF / perf</text>
    
    <!-- Arrows -->
    <path d="M 350 175 L 440 175" stroke="#fff" stroke-width="2" marker-end="url(#arrow)" />
    <path d="M 350 245 L 440 245" stroke="#fff" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#fff" />
        </marker>
    </defs>
</svg>"""
    out_path = os.path.join(os.path.dirname(__file__), "architecture.svg")
    with open(out_path, "w") as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    render()
