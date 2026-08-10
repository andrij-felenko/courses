import os

def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect x="50" y="50" width="300" height="300" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    <rect x="450" y="50" width="300" height="300" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    
    <text x="200" y="80" text-anchor="middle" font-size="20" font-weight="bold" font-family="sans-serif">Системні пакунки</text>
    <text x="600" y="80" text-anchor="middle" font-size="20" font-weight="bold" font-family="sans-serif">OCI Контейнери</text>
    
    <rect x="70" y="300" width="260" height="40" fill="#a0c0ff" stroke="#333" stroke-width="1"/>
    <text x="200" y="325" text-anchor="middle" font-family="sans-serif">Ядро ОС (Linux Kernel)</text>
    
    <rect x="470" y="300" width="260" height="40" fill="#a0c0ff" stroke="#333" stroke-width="1"/>
    <text x="600" y="325" text-anchor="middle" font-family="sans-serif">Ядро ОС (Linux Kernel)</text>
    
    <rect x="70" y="250" width="260" height="40" fill="#ffd0a0" stroke="#333" stroke-width="1"/>
    <text x="200" y="275" text-anchor="middle" font-family="sans-serif">Спільні бібліотеки (.so)</text>
    
    <rect x="70" y="190" width="120" height="50" fill="#d0ffa0" stroke="#333" stroke-width="1"/>
    <text x="130" y="220" text-anchor="middle" font-family="sans-serif">Додаток А</text>
    
    <rect x="210" y="190" width="120" height="50" fill="#d0ffa0" stroke="#333" stroke-width="1"/>
    <text x="270" y="220" text-anchor="middle" font-family="sans-serif">Додаток Б</text>
    
    <rect x="470" y="250" width="260" height="40" fill="#ffb0d0" stroke="#333" stroke-width="1"/>
    <text x="600" y="275" text-anchor="middle" font-family="sans-serif">Контейнерний рушій</text>
    
    <rect x="470" y="140" width="120" height="100" fill="#f9f9f9" stroke="#333" stroke-dasharray="4"/>
    <rect x="480" y="190" width="100" height="40" fill="#ffd0a0" stroke="#333" stroke-width="1"/>
    <text x="530" y="215" text-anchor="middle" font-size="12" font-family="sans-serif">Бібліотеки (v1)</text>
    <rect x="480" y="150" width="100" height="35" fill="#d0ffa0" stroke="#333" stroke-width="1"/>
    <text x="530" y="172" text-anchor="middle" font-family="sans-serif">Додаток А</text>
    
    <rect x="610" y="140" width="120" height="100" fill="#f9f9f9" stroke="#333" stroke-dasharray="4"/>
    <rect x="620" y="190" width="100" height="40" fill="#ffd0a0" stroke="#333" stroke-width="1"/>
    <text x="670" y="215" text-anchor="middle" font-size="12" font-family="sans-serif">Бібліотеки (v2)</text>
    <rect x="620" y="150" width="100" height="35" fill="#d0ffa0" stroke="#333" stroke-width="1"/>
    <text x="670" y="172" text-anchor="middle" font-family="sans-serif">Додаток Б</text>
</svg>"""

    with open(os.path.join(out_dir, "arch.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
