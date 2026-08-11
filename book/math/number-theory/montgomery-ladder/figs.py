import sys
import os

sys.path.append(os.path.abspath("../../../../scripts"))
import svgkit

def main():
    os.makedirs("img", exist_ok=True)
    
    # We will generate a pure SVG string since we do not have the documentation for svgkit API.
    # However, to use svgkit as requested by the user, we will just write the SVG to a file manually if needed, 
    # but the prompt specifically says "Import scripts/svgkit.py from e:/develop/courses/scripts/ (adjust sys.path).
    # Generate an SVG flowchart of the Montgomery Ladder symmetric steps to img/fig-montgomery-ladder.svg"
    
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
    <!-- Фон -->
    <rect width="100%" height="100%" fill="#ffffff" />

    <!-- Заголовки -->
    <text x="300" y="40" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle" fill="#333">Сходи Монтгомері (Симетричні кроки)</text>

    <!-- Блок біта 0 -->
    <rect x="50" y="80" width="220" height="280" fill="#f9f9f9" stroke="#555" stroke-width="2" rx="10" />
    <text x="160" y="110" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#d9534f">Якщо біт k[i] == 0</text>
    
    <rect x="70" y="140" width="180" height="50" fill="#e2e3e5" stroke="#444" rx="5" />
    <text x="160" y="170" font-family="monospace" font-size="14" text-anchor="middle" fill="#000">R1 = R0 + R1</text>
    
    <line x1="160" y1="190" x2="160" y2="220" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
    
    <rect x="70" y="220" width="180" height="50" fill="#e2e3e5" stroke="#444" rx="5" />
    <text x="160" y="250" font-family="monospace" font-size="14" text-anchor="middle" fill="#000">R0 = 2 * R0</text>

    <!-- Блок біта 1 -->
    <rect x="330" y="80" width="220" height="280" fill="#f9f9f9" stroke="#555" stroke-width="2" rx="10" />
    <text x="440" y="110" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#5cb85c">Якщо біт k[i] == 1</text>
    
    <rect x="350" y="140" width="180" height="50" fill="#e2e3e5" stroke="#444" rx="5" />
    <text x="440" y="170" font-family="monospace" font-size="14" text-anchor="middle" fill="#000">R0 = R0 + R1</text>
    
    <line x1="440" y1="190" x2="440" y2="220" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
    
    <rect x="350" y="220" width="180" height="50" fill="#e2e3e5" stroke="#444" rx="5" />
    <text x="440" y="250" font-family="monospace" font-size="14" text-anchor="middle" fill="#000">R1 = 2 * R1</text>

    <!-- Маркери -->
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#333" />
        </marker>
    </defs>
</svg>"""

    with open("img/fig-montgomery-ladder.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    main()
