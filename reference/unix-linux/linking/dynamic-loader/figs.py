import sys
import os

def render():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="sans-serif">
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
    
    <!-- ELF Program -->
    <rect x="50" y="50" width="200" height="100" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    <text x="150" y="95" text-anchor="middle" font-weight="bold" font-size="16">ELF Executable</text>
    <text x="150" y="120" text-anchor="middle" font-size="14" fill="#555">_start / main</text>
    
    <!-- Linker -->
    <rect x="350" y="50" width="200" height="100" fill="#e0f0ff" stroke="#333" stroke-width="2"/>
    <text x="450" y="95" text-anchor="middle" font-weight="bold" font-size="16">ld-linux.so (rtld)</text>
    <text x="450" y="120" text-anchor="middle" font-size="14" fill="#555">Dynamic Linker</text>
    
    <path d="M 250 100 L 340 100" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="300" y="90" text-anchor="middle" font-size="12">PT_INTERP</text>
    
    <!-- Library -->
    <rect x="350" y="250" width="200" height="100" fill="#ffe0e0" stroke="#333" stroke-width="2"/>
    <text x="450" y="295" text-anchor="middle" font-weight="bold" font-size="16">libc.so.6</text>
    <text x="450" y="320" text-anchor="middle" font-size="14" fill="#555">C Standard Library</text>
    
    <path d="M 450 150 L 450 240" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="460" y="200" font-size="12">DT_NEEDED (mmap)</text>
    
    <!-- execution flow -->
    <path d="M 450 350 L 450 420 L 150 420 L 150 150" fill="none" stroke="#2ca02c" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
    <text x="300" y="410" text-anchor="middle" fill="#2ca02c" font-size="12">__libc_start_main calls main()</text>
</svg>"""

if __name__ == '__main__':
    print(render())
