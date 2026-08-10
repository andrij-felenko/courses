import os

def render():
    os.makedirs('img', exist_ok=True)
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
    <rect width="100%" height="100%" fill="#ffffff" />
    <g font-family="sans-serif" font-size="14">
        <!-- Kernel space -->
        <rect x="50" y="50" width="700" height="300" fill="#f0f0f0" stroke="#333" stroke-width="2" rx="10"/>
        <text x="60" y="70" font-weight="bold">Linux Kernel Space</text>
        
        <!-- ACPI Subsystem -->
        <rect x="100" y="100" width="600" height="80" fill="#d0e0ff" stroke="#333" stroke-width="2"/>
        <text x="350" y="145" text-anchor="middle" font-weight="bold">ACPI Core Subsystem (acpi.ko)</text>
        
        <!-- WMI Core -->
        <rect x="100" y="220" width="250" height="80" fill="#e0ffd0" stroke="#333" stroke-width="2"/>
        <text x="225" y="265" text-anchor="middle" font-weight="bold">WMI Core (wmi.ko)</text>
        <text x="225" y="285" text-anchor="middle" font-size="12">wmi_driver, GUID mappings</text>
        
        <!-- Vendor Drivers -->
        <rect x="450" y="220" width="250" height="80" fill="#ffd0d0" stroke="#333" stroke-width="2"/>
        <text x="575" y="260" text-anchor="middle" font-weight="bold">Vendor WMI Drivers</text>
        <text x="575" y="280" text-anchor="middle" font-size="12">(dell-wmi, asus-wmi, hp-wmi)</text>
        
        <!-- Arrows -->
        <path d="M 225 180 L 225 220" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 350 260 L 450 260" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 575 220 L 575 180" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        
        <!-- User Space -->
        <rect x="50" y="380" width="700" height="100" fill="#fff0e0" stroke="#333" stroke-width="2" rx="10"/>
        <text x="60" y="400" font-weight="bold">User Space</text>
        <text x="350" y="430" text-anchor="middle">sysfs (/sys/bus/wmi/), udev, Desktop Environments</text>
        <path d="M 225 300 L 225 380" stroke="#333" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
        <path d="M 575 300 L 575 380" stroke="#333" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
    </g>
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#333" />
        </marker>
    </defs>
</svg>"""
    with open('img/wmi-architecture.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    render()
