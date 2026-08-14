import os

def render():
    os.makedirs("img", exist_ok=True)

    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#6c757d"/>
        </marker>
    </defs>
    <rect width="600" height="400" fill="#f8f9fa"/>
    <!-- SR-IOV Architecture -->
    <rect x="50" y="50" width="500" height="300" fill="#e9ecef" stroke="#adb5bd" stroke-width="2" rx="10"/>
    <text x="300" y="80" font-family="Arial" font-size="20" text-anchor="middle" font-weight="bold">Архітектура SR-IOV (PF та VF)</text>
    
    <!-- Physical Function -->
    <rect x="80" y="120" width="440" height="80" fill="#cfe2ff" stroke="#9ec5fe" stroke-width="2" rx="5"/>
    <text x="300" y="165" font-family="Arial" font-size="18" text-anchor="middle">Physical Function (PF) - Повний контроль</text>
    
    <!-- Virtual Functions -->
    <rect x="80" y="230" width="130" height="80" fill="#d1e7dd" stroke="#a3cfbb" stroke-width="2" rx="5"/>
    <text x="145" y="275" font-family="Arial" font-size="16" text-anchor="middle">VF 0</text>

    <rect x="235" y="230" width="130" height="80" fill="#d1e7dd" stroke="#a3cfbb" stroke-width="2" rx="5"/>
    <text x="300" y="275" font-family="Arial" font-size="16" text-anchor="middle">VF 1</text>

    <text x="400" y="275" font-family="Arial" font-size="24" text-anchor="middle">...</text>

    <rect x="430" y="230" width="90" height="80" fill="#d1e7dd" stroke="#a3cfbb" stroke-width="2" rx="5"/>
    <text x="475" y="275" font-family="Arial" font-size="16" text-anchor="middle">VF N</text>
    
    <!-- Arrows -->
    <line x1="145" y1="200" x2="145" y2="225" stroke="#6c757d" stroke-width="2" marker-end="url(#arrow)"/>
    <line x1="300" y1="200" x2="300" y2="225" stroke="#6c757d" stroke-width="2" marker-end="url(#arrow)"/>
    <line x1="475" y1="200" x2="475" y2="225" stroke="#6c757d" stroke-width="2" marker-end="url(#arrow)"/>
</svg>"""

    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" width="780" height="420" viewBox="0 0 780 420">
<rect width="780" height="420" fill="#ffffff"/>
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/>
</marker>
</defs>
<text x="390.0" y="28.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="16" fill="#1a1a1a" text-anchor="middle" font-weight="700">Структура PCIe SR-IOV Extended Capability та адресація BDF</text>
<rect x="30.0" y="50.0" width="340.0" height="340.0" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="1.5"/>
<text x="40.0" y="75.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="13" fill="#1a1a1a" text-anchor="start" font-weight="700">SR-IOV Extended Capability (ID 0x0010)</text>
<rect x="107.7" y="91.5" width="184.7" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="104.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x00: Header</tspan><tspan x="200.0" dy="13.0">Capability ID (0x0010), Version</tspan></text>
<rect x="124.8" y="127.5" width="150.5" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="140.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x04: SR-IOV Caps</tspan><tspan x="200.0" dy="13.0">VF Migration, ARI Capable</tspan></text>
<rect x="110.5" y="163.5" width="179.0" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="176.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x08: SR-IOV Control</tspan><tspan x="200.0" dy="13.0">VF Enable, VF Migration Enable</tspan></text>
<rect x="119.1" y="199.5" width="161.9" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="212.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x0C: InitialVFs / TotalVFs</tspan><tspan x="200.0" dy="13.0">Max VFs supported by HW</tspan></text>
<rect x="104.8" y="235.5" width="190.4" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="248.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x10: NumVFs</tspan><tspan x="200.0" dy="13.0">Active VFs count (written by OS)</tspan></text>
<rect x="110.5" y="271.5" width="179.0" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="284.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x14: VF Offset &amp; Stride</tspan><tspan x="200.0" dy="13.0">First VF BDF offset &amp; distance</tspan></text>
<rect x="124.8" y="307.5" width="150.5" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="320.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x1A: VF Device ID</tspan><tspan x="200.0" dy="13.0">Device ID assigned to VFs</tspan></text>
<rect x="110.5" y="343.5" width="179.0" height="31.0" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.0"/><text x="200.0" y="356.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="200.0" dy="0.0">0x24..0x38: VF BAR0..BAR5</tspan><tspan x="200.0" dy="13.0">Base Address Registers for VFs</tspan></text>
<rect x="400.0" y="50.0" width="350.0" height="340.0" rx="8" fill="#fafaf9" stroke="#78716c" stroke-width="1.5"/>
<text x="410.0" y="75.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="13" fill="#1a1a1a" text-anchor="start" font-weight="700">Адресація шини PCIe (Bus:Device.Function)</text>
<rect x="472.9" y="92.2" width="204.1" height="55.6" rx="6" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/><text x="575.0" y="109.5" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="11" fill="#1a1a1a" text-anchor="middle"><tspan x="575.0" dy="0.0">Physical Function (PF)</tspan><tspan x="575.0" dy="14.3">BDF = 03:00.0</tspan><tspan x="575.0" dy="14.3">Vendor: 0x8086, Device: 0x1572</tspan></text>
<rect x="420.0" y="175.0" width="310.0" height="45.0" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="1.0"/>
<text x="575.0" y="195.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#92400e" text-anchor="middle" font-weight="700">BDF(VF n) = BDF(PF) + VF_Offset + (n × VF_Stride)</text>
<text x="575.0" y="210.0" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="9" fill="#92400e" text-anchor="middle" font-style="italic">Приклад: Offset = 128 (0x80), Stride = 1</text>
<rect x="426.5" y="239.0" width="297.0" height="22.0" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.0"/><text x="575.0" y="253.5" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="575.0" dy="0.0">VF 0 → BDF = 03:02.0 (Vendor: 0x8086, Dev: 0x154c)</tspan></text>
<rect x="426.5" y="284.0" width="297.0" height="22.0" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.0"/><text x="575.0" y="298.5" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="575.0" dy="0.0">VF 1 → BDF = 03:02.1 (Vendor: 0x8086, Dev: 0x154c)</tspan></text>
<rect x="426.5" y="329.0" width="297.0" height="22.0" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.0"/><text x="575.0" y="343.5" font-family="'Segoe UI', 'DejaVu Sans', Arial, sans-serif" font-size="10" fill="#1a1a1a" text-anchor="middle"><tspan x="575.0" dy="0.0">VF 2 → BDF = 03:02.2 (Vendor: 0x8086, Dev: 0x154c)</tspan></text>
<line x1="370.0" y1="210.0" x2="400.0" y2="210.0" stroke="#d97706" stroke-width="2.0" marker-end="url(#arrow)"/>
<line x1="575.0" y1="145.0" x2="575.0" y2="175.0" stroke="#0284c7" stroke-width="1.5" marker-end="url(#arrow)"/>
<line x1="575.0" y1="220.0" x2="575.0" y2="235.0" stroke="#16a34a" stroke-width="1.5" marker-end="url(#arrow)"/>
</svg>"""

    with open(os.path.join("img", "sr-iov-arch.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)
    
    with open(os.path.join("img", "sr-iov-pcie-bdf.svg"), "w", encoding="utf-8") as f:
        f.write(svg2)

    if os.path.exists("sr-iov-arch.svg"):
        os.remove("sr-iov-arch.svg")
    
if __name__ == "__main__":
    render()

