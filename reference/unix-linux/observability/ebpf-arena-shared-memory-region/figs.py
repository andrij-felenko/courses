import os
import sys

def render():
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
    <rect width="800" height="450" fill="#f8f9fa"/>
    <text x="400" y="40" font-family="Arial" font-size="22" text-anchor="middle" font-weight="bold">Архітектура BPF_MAP_TYPE_ARENA</text>
    
    <!-- Userspace Process -->
    <rect x="50" y="80" width="280" height="200" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="8"/>
    <text x="190" y="110" font-family="Arial" font-size="18" text-anchor="middle" font-weight="bold">Userspace App</text>
    <rect x="70" y="140" width="240" height="40" fill="#bbdefb" stroke="#64b5f6" stroke-width="1" rx="4"/>
    <text x="190" y="165" font-family="monospace" font-size="14" text-anchor="middle">mmap(..., fd, ...)</text>
    <rect x="70" y="200" width="240" height="40" fill="#bbdefb" stroke="#64b5f6" stroke-width="1" rx="4"/>
    <text x="190" y="225" font-family="monospace" font-size="14" text-anchor="middle">data->value = 42;</text>
    
    <!-- Kernel Process -->
    <rect x="470" y="80" width="280" height="200" fill="#e8f5e9" stroke="#388e3c" stroke-width="2" rx="8"/>
    <text x="610" y="110" font-family="Arial" font-size="18" text-anchor="middle" font-weight="bold">Kernel (eBPF)</text>
    <rect x="490" y="140" width="240" height="40" fill="#c8e6c9" stroke="#81c784" stroke-width="1" rx="4"/>
    <text x="610" y="165" font-family="monospace" font-size="14" text-anchor="middle">bpf_arena_alloc_pages()</text>
    <rect x="490" y="200" width="240" height="40" fill="#c8e6c9" stroke="#81c784" stroke-width="1" rx="4"/>
    <text x="610" y="225" font-family="monospace" font-size="14" text-anchor="middle">__arena ptr = ...</text>
    
    <!-- Shared Memory -->
    <rect x="150" y="340" width="500" height="80" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="10"/>
    <text x="400" y="370" font-family="Arial" font-size="18" text-anchor="middle" font-weight="bold">BPF Arena (Спільний регіон пам'яті)</text>
    <text x="400" y="395" font-family="Arial" font-size="14" text-anchor="middle">Direct Pointers (Єдиний адресний простір)</text>
    
    <!-- Pointers / Arrows -->
    <path d="M 190 240 L 190 340" stroke="#424242" stroke-width="3" fill="none" marker-end="url(#arrow)"/>
    <path d="M 610 240 L 610 340" stroke="#424242" stroke-width="3" fill="none" marker-end="url(#arrow)"/>
    <path d="M 330 180 L 470 180" stroke="#424242" stroke-width="3" stroke-dasharray="5,5" fill="none"/>
    <text x="400" y="170" font-family="Arial" font-size="12" text-anchor="middle" fill="#555">Zero-copy</text>
    
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#424242"/>
        </marker>
    </defs>
</svg>"""
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "arena_arch.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"SVG rendered to {out_path}")

if __name__ == "__main__":
    render()
