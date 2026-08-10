import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#f8f9fa"/>
    <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">Virtqueue Split Architecture</text>
    <rect x="50" y="100" width="200" height="250" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="150" y="130" font-family="sans-serif" font-size="18" text-anchor="middle">Descriptor Table</text>
    <rect x="70" y="150" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="150" y="170" font-family="sans-serif" font-size="14" text-anchor="middle">Desc 0: Addr, Len, Flags, Next</text>
    <rect x="70" y="190" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="150" y="210" font-family="sans-serif" font-size="14" text-anchor="middle">Desc 1: Addr, Len, Flags, Next</text>

    <rect x="300" y="100" width="200" height="250" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="400" y="130" font-family="sans-serif" font-size="18" text-anchor="middle">Available Ring</text>
    <rect x="320" y="150" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="400" y="170" font-family="sans-serif" font-size="14" text-anchor="middle">Flags, idx</text>
    <rect x="320" y="190" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="400" y="210" font-family="sans-serif" font-size="14" text-anchor="middle">Ring[0] = 0 (head)</text>

    <rect x="550" y="100" width="200" height="250" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="650" y="130" font-family="sans-serif" font-size="18" text-anchor="middle">Used Ring</text>
    <rect x="570" y="150" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="650" y="170" font-family="sans-serif" font-size="14" text-anchor="middle">Flags, idx</text>
    <rect x="570" y="190" width="160" height="30" fill="#fff" stroke="#adb5bd"/>
    <text x="650" y="210" font-family="sans-serif" font-size="14" text-anchor="middle">Ring[0] = {id: 0, len: 1024}</text>
    
    <path d="M250 205 L300 205" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    <path d="M500 205 L550 205" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
</svg>"""
    with open("virtqueue-split.svg", "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
