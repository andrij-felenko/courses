import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def create_sparsemem_struct():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
  <defs>
    <style>
      .box { fill: #eef2f5; stroke: #8ca2b0; stroke-width: 2; rx: 5; }
      .text { font-family: sans-serif; font-size: 14px; fill: #333; }
      .title { font-weight: bold; font-size: 16px; }
      .arrow { stroke: #8ca2b0; stroke-width: 2; marker-end: url(#arrowhead); }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#8ca2b0" />
    </marker>
  </defs>

  <rect x="20" y="20" width="560" height="260" fill="#fafafa" stroke="#ccc" rx="10"/>
  <text x="300" y="45" class="text title" text-anchor="middle">SPARSEMEM Memory Structure</text>

  <rect x="50" y="80" width="140" height="60" class="box" />
  <text x="120" y="105" class="text title" text-anchor="middle">mem_section</text>
  <text x="120" y="125" class="text" text-anchor="middle">(Physical memory)</text>

  <rect x="250" y="80" width="180" height="60" class="box" />
  <text x="340" y="105" class="text title" text-anchor="middle">sysfs Memory Block</text>
  <text x="340" y="125" class="text" text-anchor="middle">(/sys/.../memoryX)</text>

  <rect x="250" y="180" width="180" height="60" class="box" />
  <text x="340" y="205" class="text title" text-anchor="middle">State: online/offline</text>
  <text x="340" y="225" class="text" text-anchor="middle">(Kernel control)</text>

  <line x1="190" y1="110" x2="240" y2="110" class="arrow" />
  <line x1="340" y1="140" x2="340" y2="170" class="arrow" />
</svg>"""
    with open(os.path.join(OUT, "sparsemem-struct.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def create_hotplug_transition():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="250" viewBox="0 0 600 250">
  <defs>
    <style>
      .box { fill: #eef2f5; stroke: #8ca2b0; stroke-width: 2; rx: 5; }
      .text { font-family: sans-serif; font-size: 14px; fill: #333; }
      .title { font-weight: bold; font-size: 16px; }
      .arrow { stroke: #8ca2b0; stroke-width: 2; marker-end: url(#arrowhead); }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#8ca2b0" />
    </marker>
  </defs>

  <rect x="50" y="50" width="120" height="60" class="box" />
  <text x="110" y="85" class="text title" text-anchor="middle">OFFLINE</text>

  <rect x="430" y="50" width="120" height="60" class="box" />
  <text x="490" y="85" class="text title" text-anchor="middle">ONLINE</text>

  <line x1="170" y1="65" x2="420" y2="65" class="arrow" />
  <text x="295" y="55" class="text" text-anchor="middle">echo online > state</text>

  <line x1="420" y1="95" x2="170" y2="95" class="arrow" />
  <text x="295" y="115" class="text" text-anchor="middle">echo offline > state</text>
  
  <rect x="200" y="140" width="200" height="60" class="box" stroke="#d9534f" fill="#fdf0ef" />
  <text x="300" y="165" class="text" text-anchor="middle" fill="#d9534f">Page Migration</text>
  <text x="300" y="185" class="text" text-anchor="middle" fill="#d9534f">(Moving data before offline)</text>
  
  <line x1="430" y1="95" x2="350" y2="140" stroke="#8ca2b0" stroke-width="2" stroke-dasharray="4" />
</svg>"""
    with open(os.path.join(OUT, "hotplug-transition.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    create_sparsemem_struct()
    create_hotplug_transition()
