import os

def render():
    svg_appimage = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">Архітектура AppImage</text>
        <rect x="250" y="100" width="300" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
        <rect x="300" y="130" width="200" height="60" fill="#4dabf7" stroke="#228be6" stroke-width="2" rx="5"/>
        <text x="400" y="165" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">AppRun (ELF wrapper)</text>
        <rect x="300" y="210" width="200" height="60" fill="#51cf66" stroke="#40c057" stroke-width="2" rx="5"/>
        <text x="400" y="245" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">SquashFS (Payload)</text>
    </svg>"""

    svg_flatpak = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">Архітектура Flatpak</text>
        <rect x="250" y="100" width="300" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
        <rect x="300" y="130" width="200" height="60" fill="#4dabf7" stroke="#228be6" stroke-width="2" rx="5"/>
        <text x="400" y="165" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">Application (Bubblewrap)</text>
        <rect x="300" y="210" width="200" height="60" fill="#51cf66" stroke="#40c057" stroke-width="2" rx="5"/>
        <text x="400" y="245" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">Runtime (OSTree)</text>
    </svg>"""

    svg_snap = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">Архітектура Snap</text>
        <rect x="250" y="100" width="300" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
        <rect x="300" y="130" width="200" height="60" fill="#4dabf7" stroke="#228be6" stroke-width="2" rx="5"/>
        <text x="400" y="165" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">Snap Application</text>
        <rect x="300" y="210" width="200" height="60" fill="#51cf66" stroke="#40c057" stroke-width="2" rx="5"/>
        <text x="400" y="245" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">Base Snap (Ubuntu Core)</text>
    </svg>"""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(base_dir, 'fig-appimage.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_appimage)
    with open(os.path.join(base_dir, 'fig-flatpak.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_flatpak)
    with open(os.path.join(base_dir, 'fig-snap.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_snap)

if __name__ == '__main__':
    render()
