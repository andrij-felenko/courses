import os
import sys

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300">
    <rect x="10" y="10" width="580" height="280" fill="none" stroke="black"/>
    <text x="300" y="30" text-anchor="middle" font-size="20">File Descriptor Table</text>
    
    <!-- Process -->
    <rect x="50" y="50" width="150" height="200" fill="#f0f0f0" stroke="black"/>
    <text x="125" y="70" text-anchor="middle" font-size="16">Process</text>
    
    <text x="125" y="120" text-anchor="middle">0 (stdin)</text>
    <text x="125" y="160" text-anchor="middle">1 (stdout)</text>
    <text x="125" y="200" text-anchor="middle">2 (stderr)</text>
    
    <!-- Kernel -->
    <rect x="300" y="50" width="250" height="200" fill="#e0e0ff" stroke="black"/>
    <text x="425" y="70" text-anchor="middle" font-size="16">Kernel Open File Table</text>
    
    <text x="425" y="120" text-anchor="middle">Terminal Keyboard</text>
    <text x="425" y="160" text-anchor="middle">Terminal Display</text>
    <text x="425" y="200" text-anchor="middle">Terminal Display</text>
    
    <line x1="175" y1="115" x2="310" y2="115" stroke="black" marker-end="url(#arrow)"/>
    <line x1="175" y1="155" x2="310" y2="155" stroke="black" marker-end="url(#arrow)"/>
    <line x1="175" y1="195" x2="310" y2="195" stroke="black" marker-end="url(#arrow)"/>
</svg>"""
    with open("fig-descriptors.svg", "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
