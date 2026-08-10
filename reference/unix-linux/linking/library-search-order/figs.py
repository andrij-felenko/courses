import sys
import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <rect width="100%" height="100%" fill="#f9f9f9"/>
    <text x="400" y="50" font-size="24" text-anchor="middle" font-family="sans-serif">Порядок пошуку бібліотек (ld.so)</text>
    
    <g transform="translate(100, 100)" font-family="sans-serif" font-size="16">
        <rect x="0" y="0" width="600" height="60" rx="10" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
        <text x="300" y="35" text-anchor="middle">1. DT_RPATH (якщо немає DT_RUNPATH)</text>

        <path d="M 300 60 L 300 90" stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>
        
        <rect x="0" y="90" width="600" height="60" rx="10" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
        <text x="300" y="125" text-anchor="middle">2. LD_LIBRARY_PATH (ігнорується для SUID/SGID)</text>
        
        <path d="M 300 150 L 300 180" stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>

        <rect x="0" y="180" width="600" height="60" rx="10" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
        <text x="300" y="215" text-anchor="middle">3. DT_RUNPATH (завжди після LD_LIBRARY_PATH)</text>
        
        <path d="M 300 240 L 300 270" stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>

        <rect x="0" y="270" width="600" height="60" rx="10" fill="#fce4ec" stroke="#e91e63" stroke-width="2"/>
        <text x="300" y="305" text-anchor="middle">4. Кеш /etc/ld.so.cache (згенерований ldconfig)</text>
        
        <path d="M 300 330 L 300 360" stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>

        <rect x="0" y="360" width="600" height="60" rx="10" fill="#f3e5f5" stroke="#9c27b0" stroke-width="2"/>
        <text x="300" y="395" text-anchor="middle">5. Стандартні шляхи: /lib, /usr/lib, /lib64, /usr/lib64</text>
    </g>

    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
</svg>"""
    
    with open('search_order.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    render()
