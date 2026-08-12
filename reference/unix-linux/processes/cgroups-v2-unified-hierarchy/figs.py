import os

def render():
    v1_vs_v2_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" font-family="sans-serif">
    <!-- Cgroups v1 -->
    <text x="200" y="30" text-anchor="middle" font-size="20" font-weight="bold">Cgroups v1 (Multiple Hierarchies)</text>
    
    <rect x="50" y="60" width="100" height="40" rx="5" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    <text x="100" y="85" text-anchor="middle">CPU</text>
    <line x1="100" y1="100" x2="70" y2="130" stroke="#333" stroke-width="2"/>
    <line x1="100" y1="100" x2="130" y2="130" stroke="#333" stroke-width="2"/>
    <rect x="30" y="130" width="80" height="30" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="70" y="150" text-anchor="middle">Group A</text>
    <rect x="120" y="130" width="80" height="30" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="160" y="150" text-anchor="middle">Group B</text>

    <rect x="250" y="60" width="100" height="40" rx="5" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    <text x="300" y="85" text-anchor="middle">Memory</text>
    <line x1="300" y1="100" x2="270" y2="130" stroke="#333" stroke-width="2"/>
    <line x1="300" y1="100" x2="330" y2="130" stroke="#333" stroke-width="2"/>
    <rect x="230" y="130" width="80" height="30" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="270" y="150" text-anchor="middle">Group X</text>
    <rect x="320" y="130" width="80" height="30" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="360" y="150" text-anchor="middle">Group Y</text>

    <line x1="400" y1="0" x2="400" y2="400" stroke="#ccc" stroke-dasharray="5,5"/>

    <!-- Cgroups v2 -->
    <text x="600" y="30" text-anchor="middle" font-size="20" font-weight="bold">Cgroups v2 (Unified Hierarchy)</text>
    
    <rect x="520" y="60" width="160" height="40" rx="5" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
    <text x="600" y="85" text-anchor="middle">Root (Unified)</text>
    <line x1="600" y1="100" x2="520" y2="150" stroke="#333" stroke-width="2"/>
    <line x1="600" y1="100" x2="680" y2="150" stroke="#333" stroke-width="2"/>
    
    <rect x="440" y="150" width="160" height="40" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="520" y="170" text-anchor="middle" font-weight="bold">Service A</text>
    <text x="520" y="185" text-anchor="middle" font-size="12">cpu, memory</text>
    
    <rect x="600" y="150" width="160" height="40" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="680" y="170" text-anchor="middle" font-weight="bold">Service B</text>
    <text x="680" y="185" text-anchor="middle" font-size="12">io, pids</text>

    <!-- Notes -->
    <text x="200" y="240" text-anchor="middle" font-size="14">Process P1 can be in CPU Group A and</text>
    <text x="200" y="260" text-anchor="middle" font-size="14">Memory Group Y simultaneously.</text>
    <text x="200" y="280" text-anchor="middle" font-size="14" fill="red">Complex to manage and trace.</text>

    <text x="600" y="240" text-anchor="middle" font-size="14">Process P1 belongs to exactly one cgroup</text>
    <text x="600" y="260" text-anchor="middle" font-size="14">(e.g., Service A). Controllers are enabled</text>
    <text x="600" y="280" text-anchor="middle" font-size="14">per sub-tree.</text>
    <text x="600" y="300" text-anchor="middle" font-size="14" fill="green">Simpler, predictable resource tracking.</text>

</svg>"""

    top_down_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" font-family="sans-serif">
    <text x="300" y="30" text-anchor="middle" font-size="20" font-weight="bold">No Internal Processes Rule</text>
    
    <rect x="250" y="60" width="100" height="40" rx="5" fill="#f0f0f0" stroke="#333"/>
    <text x="300" y="85" text-anchor="middle">Parent Group</text>
    
    <line x1="300" y1="100" x2="200" y2="150" stroke="#333" stroke-width="2"/>
    <line x1="300" y1="100" x2="400" y2="150" stroke="#333" stroke-width="2"/>
    
    <rect x="150" y="150" width="100" height="40" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="200" y="175" text-anchor="middle">Leaf 1</text>
    <circle cx="180" cy="220" r="10" fill="#ff9999" stroke="#333"/>
    <text x="200" y="225">PID 100</text>
    
    <rect x="350" y="150" width="100" height="40" rx="5" fill="#d9edf7" stroke="#333"/>
    <text x="400" y="175" text-anchor="middle">Leaf 2</text>
    <circle cx="380" cy="220" r="10" fill="#ff9999" stroke="#333"/>
    <text x="400" y="225">PID 101</text>
    
    <circle cx="370" cy="80" r="12" fill="#ff0000" stroke="#333"/>
    <line x1="362" y1="72" x2="378" y2="88" stroke="#fff" stroke-width="3"/>
    <line x1="378" y1="72" x2="362" y2="88" stroke="#fff" stroke-width="3"/>
    <text x="390" y="85" fill="red" font-weight="bold">No PIDs here!</text>

    <text x="300" y="270" text-anchor="middle" font-size="14">A cgroup can either distribute controllers to its children</text>
    <text x="300" y="290" text-anchor="middle" font-size="14">OR contain processes, but never both simultaneously.</text>
</svg>"""

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    with open(os.path.join(img_dir, "v1-vs-v2.svg"), "w", encoding="utf-8") as f:
        f.write(v1_vs_v2_svg)
    with open(os.path.join(img_dir, "no-internal-processes.svg"), "w", encoding="utf-8") as f:
        f.write(top_down_svg)

if __name__ == '__main__':
    render()

