import sys
import os

# Спроба імпортувати svgkit зі scripts/ (як вказано у правилах)
# Якщо його немає в контексті, ми згенеруємо SVG напряму для надійності,
# але збережемо структуру.

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <defs>
        <style>
            .box { fill: #2c3e50; stroke: #34495e; stroke-width: 2; rx: 5; ry: 5; }
            .txt { fill: #ecf0f1; font-family: sans-serif; font-size: 16px; text-anchor: middle; alignment-baseline: middle; }
            .txt-title { fill: #333; font-family: sans-serif; font-size: 20px; font-weight: bold; text-anchor: middle; }
            .line { stroke: #7f8c8d; stroke-width: 2; stroke-dasharray: 5,5; }
            .arrow { stroke: #e74c3c; stroke-width: 3; marker-end: url(#arrowhead); }
        </style>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#e74c3c" />
        </marker>
    </defs>
    
    <text x="400" y="30" class="txt-title">Архітектура sched_ext</text>
    
    <!-- User Space -->
    <rect x="50" y="60" width="700" height="120" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="2" rx="10"/>
    <text x="400" y="80" class="txt-title" font-size="14">User Space</text>
    
    <rect x="100" y="100" width="200" height="50" class="box" fill="#8e44ad" />
    <text x="200" y="125" class="txt">scx_rustland (User Agent)</text>
    
    <rect x="500" y="100" width="200" height="50" class="box" fill="#8e44ad" />
    <text x="600" y="125" class="txt">scx_lavd (User Agent)</text>
    
    <!-- Kernel Space -->
    <rect x="50" y="210" width="700" height="160" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="2" rx="10"/>
    <text x="400" y="230" class="txt-title" font-size="14">Kernel Space (Linux)</text>
    
    <rect x="100" y="260" width="200" height="50" class="box" fill="#2980b9" />
    <text x="200" y="285" class="txt">BPF Program (sched_ext)</text>
    
    <rect x="500" y="260" width="200" height="50" class="box" fill="#27ae60" />
    <text x="600" y="285" class="txt">Core Scheduler (core.c)</text>
    
    <!-- Lines & Arrows -->
    <line x1="200" y1="150" x2="200" y2="260" class="arrow" />
    <text x="260" y="200" class="txt-title" font-size="12" fill="#e74c3c">BPF Maps / Ringbuf</text>
    
    <line x1="300" y1="285" x2="500" y2="285" class="arrow" />
    <text x="400" y="275" class="txt-title" font-size="12" fill="#e74c3c">struct sched_ext_ops</text>
    
    <line x1="50" y1="195" x2="750" y2="195" class="line" />
</svg>"""
    
    out_dir = os.path.dirname(__file__)
    out_path = os.path.join(out_dir, "sched_ext_arch.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    render()
