import os

def render():
    # vDSO vs syscall illustration
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect width="100%" height="100%" fill="#fafafa"/>
    
    <!-- User Space -->
    <rect x="50" y="50" width="300" height="300" fill="#e3f2fd" stroke="#1565c0" stroke-width="2" rx="10"/>
    <text x="200" y="80" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#0d47a1" text-anchor="middle">User Space</text>
    
    <!-- Kernel Space -->
    <rect x="450" y="50" width="300" height="300" fill="#fff3e0" stroke="#e65100" stroke-width="2" rx="10"/>
    <text x="600" y="80" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#e65100" text-anchor="middle">Kernel Space</text>
    
    <!-- Syscall path -->
    <path d="M 200 120 C 350 120, 450 200, 600 200" fill="none" stroke="#d32f2f" stroke-width="3" stroke-dasharray="5,5" marker-end="url(#arrow-red)"/>
    <text x="400" y="140" font-family="Arial" font-size="14" fill="#d32f2f" text-anchor="middle">Standard Syscall (Context Switch)</text>
    
    <!-- vDSO path -->
    <rect x="100" y="220" width="200" height="100" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2" rx="5"/>
    <text x="200" y="250" font-family="Arial" font-size="16" font-weight="bold" fill="#1b5e20" text-anchor="middle">vDSO mapped library</text>
    <text x="200" y="275" font-family="Arial" font-size="14" fill="#1b5e20" text-anchor="middle">gettimeofday()</text>
    
    <path d="M 200 160 L 200 220" fill="none" stroke="#2e7d32" stroke-width="3" marker-end="url(#arrow-green)"/>
    <text x="140" y="190" font-family="Arial" font-size="14" fill="#2e7d32">Fast call</text>
    
    <defs>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d32f2f"/>
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#2e7d32"/>
        </marker>
    </defs>
</svg>"""

    # Memory Layout vDSO / vvar
    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect width="100%" height="100%" fill="#fafafa"/>
    
    <!-- Process Memory -->
    <rect x="200" y="50" width="400" height="300" fill="#eceff1" stroke="#455a64" stroke-width="2" rx="10"/>
    <text x="400" y="80" font-family="Arial" font-size="20" font-weight="bold" fill="#263238" text-anchor="middle">Process Virtual Address Space</text>
    
    <!-- vvar page -->
    <rect x="250" y="120" width="300" height="60" fill="#ffe0b2" stroke="#f57c00" stroke-width="2" rx="5"/>
    <text x="400" y="145" font-family="Arial" font-size="16" font-weight="bold" fill="#e65100" text-anchor="middle">[vvar] page</text>
    <text x="400" y="165" font-family="Arial" font-size="14" fill="#e65100" text-anchor="middle">Kernel Time Variables (Read-Only: r--)</text>
    
    <!-- vdso page -->
    <rect x="250" y="210" width="300" height="60" fill="#c8e6c9" stroke="#388e3c" stroke-width="2" rx="5"/>
    <text x="400" y="235" font-family="Arial" font-size="16" font-weight="bold" fill="#1b5e20" text-anchor="middle">[vdso] page</text>
    <text x="400" y="255" font-family="Arial" font-size="14" fill="#1b5e20" text-anchor="middle">vDSO Executable Code (Execute: r-x)</text>
    
</svg>"""

    with open(os.path.join(os.path.dirname(__file__), "vdso-vs-syscall.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)
    
    with open(os.path.join(os.path.dirname(__file__), "vdso-memory-layout.svg"), "w", encoding="utf-8") as f:
        f.write(svg2)

if __name__ == "__main__":
    render()
