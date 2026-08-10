import sys
import os

# mock SVG generator
def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
        <rect width="800" height="400" fill="#f0f0f0"/>
        <text x="400" y="50" font-family="Arial" font-size="24" text-anchor="middle">TPM 2.0 PCR Extend Mechanism</text>
        
        <rect x="100" y="100" width="150" height="80" fill="#cce5ff" stroke="#004085"/>
        <text x="175" y="145" font-family="Arial" font-size="16" text-anchor="middle">Data / Firmware</text>

        <rect x="550" y="100" width="150" height="80" fill="#d4edda" stroke="#155724"/>
        <text x="625" y="145" font-family="Arial" font-size="16" text-anchor="middle">TPM PCR</text>
        
        <path d="M 250 140 L 550 140" stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="400" y="130" font-family="Arial" font-size="14" text-anchor="middle">HASH()</text>
        
        <rect x="300" y="250" width="200" height="60" fill="#fff3cd" stroke="#856404"/>
        <text x="400" y="285" font-family="Arial" font-size="16" text-anchor="middle">Event Log</text>
    </svg>"""
    with open("measured-boot-pcr-fig1.svg", "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
