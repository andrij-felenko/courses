import sys
import os

def render_load_avg_svg(filename):
    svg = """<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
    <rect width="600" height="300" fill="#ffffff" />
    <text x="300" y="30" font-family="sans-serif" font-size="20" text-anchor="middle">Load Average States</text>
    <rect x="50" y="80" width="150" height="100" fill="#a0e0a0" stroke="#000" />
    <text x="125" y="130" font-family="sans-serif" font-size="16" text-anchor="middle">Running</text>
    <text x="125" y="150" font-family="sans-serif" font-size="12" text-anchor="middle">(TASK_RUNNING)</text>
    
    <rect x="225" y="80" width="150" height="100" fill="#ffb0b0" stroke="#000" />
    <text x="300" y="130" font-family="sans-serif" font-size="16" text-anchor="middle">Runnable</text>
    <text x="300" y="150" font-family="sans-serif" font-size="12" text-anchor="middle">(Waiting for CPU)</text>

    <rect x="400" y="80" width="150" height="100" fill="#d0d0ff" stroke="#000" />
    <text x="475" y="130" font-family="sans-serif" font-size="16" text-anchor="middle">Uninterruptible</text>
    <text x="475" y="150" font-family="sans-serif" font-size="12" text-anchor="middle">(Disk/IO wait)</text>
    
    <path d="M 50 220 L 550 220" stroke="black" stroke-width="2" stroke-dasharray="5,5" />
    <text x="300" y="240" font-family="sans-serif" font-size="14" text-anchor="middle">Included in Linux Load Average Calculation</text>
</svg>"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def render_psi_svg(filename):
    svg = """<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
    <rect width="600" height="300" fill="#ffffff" />
    <text x="300" y="30" font-family="sans-serif" font-size="20" text-anchor="middle">PSI (Pressure Stall Information)</text>
    
    <rect x="100" y="80" width="400" height="60" fill="#fff0b3" stroke="#000" />
    <text x="300" y="115" font-family="sans-serif" font-size="16" text-anchor="middle">SOME: Принаймні один процес чекає на ресурс</text>
    
    <rect x="100" y="160" width="400" height="60" fill="#ff9999" stroke="#000" />
    <text x="300" y="195" font-family="sans-serif" font-size="16" text-anchor="middle">FULL: Усі процеси чекають (повний простій)</text>
</svg>"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def render():
    render_load_avg_svg("load-avg.svg")
    render_psi_svg("psi-stall.svg")

if __name__ == '__main__':
    render()
