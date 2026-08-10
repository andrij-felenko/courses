import sys
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
scripts_dir = os.path.join(repo_root, 'scripts')
sys.path.insert(0, scripts_dir)

try:
    import svgkit
    has_svgkit = True
except ImportError:
    has_svgkit = False

def render():
    out_file = os.path.join(os.path.dirname(__file__), 'erofs-architecture.svg')
    
    if has_svgkit:
        # If real svgkit is present, use it. But since we don't know the exact API,
        # we will generate a raw SVG string and write it manually just to be safe
        # if the API is different. However, we'll write standard SVG.
        pass
        
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
    <rect width="100%" height="100%" fill="#f8f9fa"/>
    <text x="400" y="50" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">Архітектура EROFS (Enhanced Read-Only File System)</text>
    
    <g transform="translate(50, 100)">
        <!-- Superblock -->
        <rect x="0" y="0" width="150" height="60" rx="5" fill="#4dabf7" stroke="#228be6" stroke-width="2"/>
        <text x="75" y="35" font-family="monospace" font-size="16" text-anchor="middle" fill="#fff">Superblock</text>
        
        <!-- Metadata -->
        <rect x="170" y="0" width="200" height="60" rx="5" fill="#69db7c" stroke="#40c057" stroke-width="2"/>
        <text x="270" y="25" font-family="monospace" font-size="16" text-anchor="middle" fill="#fff">Meta/Inodes</text>
        <text x="270" y="45" font-family="Arial" font-size="12" text-anchor="middle" fill="#fff">(Compact 32B/Extended 64B)</text>
        
        <!-- Data Blocks -->
        <rect x="390" y="0" width="310" height="60" rx="5" fill="#ffa94d" stroke="#fd7e14" stroke-width="2"/>
        <text x="545" y="35" font-family="monospace" font-size="16" text-anchor="middle" fill="#fff">Compressed / Uncompressed Data</text>
        
        <!-- Fixed-sized output compression illustration -->
        <rect x="390" y="100" width="310" height="150" rx="5" fill="#fff" stroke="#adb5bd" stroke-width="2" stroke-dasharray="5,5"/>
        <text x="545" y="130" font-family="Arial" font-size="16" text-anchor="middle" fill="#495057">Fixed-sized Output Compression</text>
        
        <!-- Uncompressed logical blocks -->
        <rect x="410" y="150" width="80" height="30" fill="#e9ecef" stroke="#ced4da"/>
        <rect x="490" y="150" width="80" height="30" fill="#e9ecef" stroke="#ced4da"/>
        <rect x="570" y="150" width="80" height="30" fill="#e9ecef" stroke="#ced4da"/>
        
        <path d="M 450 180 L 490 220" stroke="#868e96" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 530 180 L 490 220" stroke="#868e96" stroke-width="2" marker-end="url(#arrow)"/>
        
        <!-- Compressed physical block -->
        <rect x="450" y="220" width="80" height="30" fill="#ffa94d" stroke="#fd7e14"/>
        <text x="490" y="240" font-family="Arial" font-size="12" text-anchor="middle" fill="#fff">4KB VBlock</text>
    </g>
</svg>
"""
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    render()
