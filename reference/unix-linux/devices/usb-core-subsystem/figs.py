import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
    <rect width="600" height="400" fill="#f8f9fa"/>
    <text x="300" y="30" font-family="Arial" font-size="20" text-anchor="middle" font-weight="bold">USB Subsystem Architecture</text>
    
    <rect x="50" y="60" width="500" height="50" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="300" y="90" font-family="Arial" font-size="16" text-anchor="middle">User Space Applications (lsusb, etc.)</text>
    
    <line x1="300" y1="110" x2="300" y2="150" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="50" y="150" width="220" height="50" rx="10" fill="#d1e7dd" stroke="#badbcc" stroke-width="2"/>
    <text x="160" y="180" font-family="Arial" font-size="16" text-anchor="middle">USB Device Drivers</text>
    
    <rect x="330" y="150" width="220" height="50" rx="10" fill="#cfe2ff" stroke="#b6d4fe" stroke-width="2"/>
    <text x="440" y="180" font-family="Arial" font-size="16" text-anchor="middle">Sysfs / Devfs</text>
    
    <line x1="160" y1="200" x2="160" y2="240" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="50" y="240" width="500" height="50" rx="10" fill="#fff3cd" stroke="#ffecb5" stroke-width="2"/>
    <text x="300" y="270" font-family="Arial" font-size="16" text-anchor="middle">USB Core</text>
    
    <line x1="300" y1="290" x2="300" y2="330" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="50" y="330" width="500" height="50" rx="10" fill="#f8d7da" stroke="#f5c2c7" stroke-width="2"/>
    <text x="300" y="360" font-family="Arial" font-size="16" text-anchor="middle">Host Controller Drivers (HCD - xHCI/EHCI)</text>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#495057" />
        </marker>
    </defs>
</svg>"""
    
    with open("usb-arch.svg", "w") as f:
        f.write(svg_content)
        
if __name__ == "__main__":
    render()
