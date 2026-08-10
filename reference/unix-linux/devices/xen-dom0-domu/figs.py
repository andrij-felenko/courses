import os
import sys

def render():
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
    <rect width="600" height="400" fill="#ffffff" />
    <text x="300" y="50" font-size="24" text-anchor="middle" font-family="sans-serif">Xen Architecture Overview</text>
    <rect x="50" y="80" width="200" height="150" fill="#cce5ff" stroke="#004085" stroke-width="2"/>
    <text x="150" y="110" font-size="18" text-anchor="middle" font-family="sans-serif">Dom0 (Control)</text>
    <rect x="70" y="130" width="160" height="40" fill="#b8daff" stroke="#004085" />
    <text x="150" y="155" font-size="14" text-anchor="middle" font-family="sans-serif">Backend Drivers</text>
    <rect x="70" y="180" width="160" height="40" fill="#b8daff" stroke="#004085" />
    <text x="150" y="205" font-size="14" text-anchor="middle" font-family="sans-serif">Xenstore</text>
    
    <rect x="350" y="80" width="200" height="150" fill="#d4edda" stroke="#155724" stroke-width="2"/>
    <text x="450" y="110" font-size="18" text-anchor="middle" font-family="sans-serif">DomU (Guest)</text>
    <rect x="370" y="130" width="160" height="40" fill="#c3e6cb" stroke="#155724" />
    <text x="450" y="155" font-size="14" text-anchor="middle" font-family="sans-serif">Frontend Drivers</text>
    
    <rect x="50" y="260" width="500" height="60" fill="#fff3cd" stroke="#856404" stroke-width="2"/>
    <text x="300" y="295" font-size="20" text-anchor="middle" font-family="sans-serif">Xen Hypervisor (Ring -1)</text>
    
    <rect x="50" y="340" width="500" height="40" fill="#e2e3e5" stroke="#383d41" stroke-width="2"/>
    <text x="300" y="365" font-size="18" text-anchor="middle" font-family="sans-serif">Hardware (CPU, RAM, I/O)</text>
</svg>"""
    
    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" width="700" height="350">
    <rect width="700" height="350" fill="#ffffff" />
    <text x="350" y="40" font-size="22" text-anchor="middle" font-family="sans-serif">Grant Tables and Event Channels</text>
    
    <rect x="100" y="80" width="200" height="200" fill="#d4edda" stroke="#155724" stroke-width="2" rx="10"/>
    <text x="200" y="110" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">DomU (Frontend)</text>
    <rect x="120" y="140" width="160" height="40" fill="#c3e6cb" stroke="#155724" rx="5"/>
    <text x="200" y="165" font-size="14" text-anchor="middle" font-family="sans-serif">Grant Reference</text>
    <rect x="120" y="210" width="160" height="40" fill="#c3e6cb" stroke="#155724" rx="5"/>
    <text x="200" y="235" font-size="14" text-anchor="middle" font-family="sans-serif">Event Channel</text>
    
    <rect x="400" y="80" width="200" height="200" fill="#cce5ff" stroke="#004085" stroke-width="2" rx="10"/>
    <text x="500" y="110" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">Dom0 (Backend)</text>
    <rect x="420" y="140" width="160" height="40" fill="#b8daff" stroke="#004085" rx="5"/>
    <text x="500" y="165" font-size="14" text-anchor="middle" font-family="sans-serif">Map memory</text>
    <rect x="420" y="210" width="160" height="40" fill="#b8daff" stroke="#004085" rx="5"/>
    <text x="500" y="235" font-size="14" text-anchor="middle" font-family="sans-serif">Wait for Notify</text>
    
    <path d="M 280 160 L 420 160" stroke="#000" stroke-width="2" stroke-dasharray="5,5" fill="none" marker-end="url(#arrow)"/>
    <text x="350" y="150" font-size="12" text-anchor="middle" font-family="sans-serif">Shared Memory (I/O Ring)</text>
    
    <path d="M 280 230 L 420 230" stroke="#ff0000" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
    <text x="350" y="220" font-size="12" text-anchor="middle" font-family="sans-serif">Virtual Interrupt</text>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
</svg>"""

    with open("xen-arch.svg", "w", encoding="utf-8") as f:
        f.write(svg1)
    
    with open("xen-gnttab.svg", "w", encoding="utf-8") as f:
        f.write(svg2)

if __name__ == "__main__":
    render()
