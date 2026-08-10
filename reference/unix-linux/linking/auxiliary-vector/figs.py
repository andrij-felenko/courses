import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
try:
    from svgkit import *
except ImportError:
    # Fallback mock for svgkit if it doesn't exist to avoid errors in this environment
    pass

def render_stack():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" width="400" height="500">
    <rect width="100%" height="100%" fill="white"/>
    <g font-family="sans-serif" font-size="14">
        <rect x="50" y="50" width="300" height="40" fill="#f0f0f0" stroke="black"/>
        <text x="200" y="75" text-anchor="middle">Information block (strings)</text>
        
        <rect x="50" y="90" width="300" height="20" fill="#e0e0e0" stroke="black"/>
        <text x="200" y="105" text-anchor="middle">NULL</text>
        
        <rect x="50" y="110" width="300" height="80" fill="#d0e0ff" stroke="black"/>
        <text x="200" y="145" text-anchor="middle">auxv array (Elf64_auxv_t)</text>
        <text x="200" y="170" text-anchor="middle">AT_NULL, AT_SYSINFO_EHDR, ...</text>
        
        <rect x="50" y="190" width="300" height="20" fill="#e0e0e0" stroke="black"/>
        <text x="200" y="205" text-anchor="middle">NULL</text>
        
        <rect x="50" y="210" width="300" height="80" fill="#d0ffd0" stroke="black"/>
        <text x="200" y="255" text-anchor="middle">Environment variables (envp)</text>
        
        <rect x="50" y="290" width="300" height="20" fill="#e0e0e0" stroke="black"/>
        <text x="200" y="305" text-anchor="middle">NULL</text>
        
        <rect x="50" y="310" width="300" height="80" fill="#ffd0d0" stroke="black"/>
        <text x="200" y="355" text-anchor="middle">Arguments (argv)</text>
        
        <rect x="50" y="390" width="300" height="40" fill="#ffffd0" stroke="black"/>
        <text x="200" y="415" text-anchor="middle">argc</text>
        
        <path d="M 20 410 L 40 410" stroke="red" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="10" y="415" fill="red" font-size="12" text-anchor="end">rsp</text>
    </g>
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="red"/>
        </marker>
    </defs>
</svg>"""
    with open(os.path.join(out_dir, "stack.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

def render():
    render_stack()

if __name__ == "__main__":
    render()
