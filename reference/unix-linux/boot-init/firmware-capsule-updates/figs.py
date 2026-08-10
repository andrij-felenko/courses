import sys
import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
    <rect x="50" y="20" width="700" height="260" fill="#fcfcfc" stroke="#333" rx="10" />
    <text x="400" y="50" text-anchor="middle" font-size="22" font-family="sans-serif" font-weight="bold">Процес оновлення UEFI Capsule</text>
    
    <rect x="100" y="100" width="160" height="80" fill="#e3f2fd" stroke="#1565c0" stroke-width="2" rx="5" />
    <text x="180" y="135" text-anchor="middle" font-size="16" font-family="sans-serif">LVFS / fwupd</text>
    <text x="180" y="155" text-anchor="middle" font-size="12" font-family="sans-serif">Завантаження .cab</text>
    
    <path d="M 260 140 L 330 140" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
    
    <rect x="340" y="100" width="160" height="80" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2" rx="5" />
    <text x="420" y="135" text-anchor="middle" font-size="16" font-family="sans-serif">Linux Kernel</text>
    <text x="420" y="155" text-anchor="middle" font-size="12" font-family="sans-serif">efi_capsule_loader</text>
    
    <path d="M 500 140 L 570 140" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />

    <rect x="580" y="100" width="160" height="80" fill="#fff3e0" stroke="#e65100" stroke-width="2" rx="5" />
    <text x="660" y="135" text-anchor="middle" font-size="16" font-family="sans-serif">UEFI Firmware</text>
    <text x="660" y="155" text-anchor="middle" font-size="12" font-family="sans-serif">UpdateCapsule()</text>
    
    <text x="420" y="210" text-anchor="middle" font-size="14" font-family="sans-serif" font-style="italic">Ребут системи для застосування (ESRT)</text>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,10 L10,5 z" fill="#333" />
        </marker>
    </defs>
</svg>"""
    with open(os.path.join(os.path.dirname(__file__), "capsule_flow.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("SVG generated: capsule_flow.svg")

if __name__ == "__main__":
    render()
