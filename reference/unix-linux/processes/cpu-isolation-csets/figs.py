import os

def render(filename, svg_content):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def main():
    arch_svg = """<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect width="800" height="400" fill="#f8f9fa"/>
    <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" fill="#333">Архітектура ізоляції CPU в Linux</text>
    
    <g transform="translate(100, 100)">
        <rect width="250" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2" rx="10"/>
        <text x="125" y="40" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold">Housekeeping CPUs</text>
        <text x="125" y="80" font-family="sans-serif" font-size="14" text-anchor="middle">CPU 0, 1</text>
        <rect x="25" y="100" width="200" height="30" fill="#fff" stroke="#adb5bd" rx="5"/>
        <text x="125" y="120" font-family="sans-serif" font-size="14" text-anchor="middle">ОС, IRQ, RCU, Таймери</text>
    </g>
    
    <g transform="translate(450, 100)">
        <rect width="250" height="200" fill="#d4edda" stroke="#c3e6cb" stroke-width="2" rx="10"/>
        <text x="125" y="40" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold">Isolated CPUs</text>
        <text x="125" y="80" font-family="sans-serif" font-size="14" text-anchor="middle">CPU 2, 3</text>
        <rect x="25" y="100" width="200" height="30" fill="#fff" stroke="#adb5bd" rx="5"/>
        <text x="125" y="120" font-family="sans-serif" font-size="14" text-anchor="middle">Real-time додатки (100% CPU)</text>
    </g>
</svg>
"""
    render('figs/isolation_arch.svg', arch_svg)

if __name__ == '__main__':
    main()
