import os
import sys

# Ensure output directory exists
img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)

def create_fig1():
    """Figure 1: Augmenting path in bipartite graph vs failure in odd cycle (blossom)."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .title { font-family: sans-serif; font-size: 15px; font-weight: bold; fill: #1e293b; }
    .label { font-family: sans-serif; font-size: 13px; fill: #334155; }
    .node-txt { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }
    .edge { stroke: #94a3b8; stroke-width: 2; }
    .match-edge { stroke: #2563eb; stroke-width: 4; }
    .aug-edge { stroke: #dc2626; stroke-width: 3; stroke-dasharray: 6,4; }
    .node-unmatched { fill: #ef4444; stroke: #b91c1c; stroke-width: 2; }
    .node-matched { fill: #2563eb; stroke: #1d4ed8; stroke-width: 2; }
    .node-even { fill: #10b981; stroke: #047857; stroke-width: 2; }
    .node-odd { fill: #f59e0b; stroke: #b45309; stroke-width: 2; }
    .panel { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1; rx: 8; }
  </style>
  <rect width="100%" height="100%" class="bg"/>

  <!-- Left Panel: Bipartite Graph -->
  <rect x="20" y="20" width="360" height="280" class="panel"/>
  <text x="200" y="45" text-anchor="middle" class="title">a) Двочастковий граф (простий чергувальний шлях)</text>

  <!-- Left Nodes -->
  <circle cx="70" cy="110" r="18" class="node-unmatched"/>
  <text x="70" y="110" class="node-txt">r</text>

  <circle cx="70" cy="210" r="18" class="node-matched"/>
  <text x="70" y="210" class="node-txt">u2</text>

  <circle cx="200" cy="110" r="18" class="node-matched"/>
  <text x="200" y="110" class="node-txt">v1</text>

  <circle cx="200" cy="210" r="18" class="node-matched"/>
  <text x="200" y="210" class="node-txt">v2</text>

  <circle cx="330" cy="160" r="18" class="node-unmatched"/>
  <text x="330" y="160" class="node-txt">t</text>

  <!-- Edges Left -->
  <line x1="88" y1="110" x2="182" y2="110" class="aug-edge"/>
  <line x1="200" y1="128" x2="70" y2="192" class="match-edge"/>
  <line x1="88" y1="210" x2="182" y2="210" class="aug-edge"/>
  <line x1="218" y1="203" x2="313" y2="167" class="match-edge"/>

  <text x="200" y="270" text-anchor="middle" class="label">Шлях: r → v1 = u2 → v2 = t (чітке двочасткове розбиття)</text>

  <!-- Right Panel: General Graph with Odd Cycle -->
  <rect x="420" y="20" width="360" height="280" class="panel"/>
  <text x="600" y="45" text-anchor="middle" class="title">б) Недвочастковий граф (непарний цикл / квітка)</text>

  <!-- Right Nodes -->
  <circle cx="460" cy="160" r="18" class="node-unmatched"/>
  <text x="460" y="160" class="node-txt">r</text>

  <circle cx="540" cy="100" r="18" class="node-even"/>
  <text x="540" y="100" class="node-txt">b</text>

  <circle cx="630" cy="80" r="18" class="node-odd"/>
  <text x="630" y="80" class="node-txt">w1</text>

  <circle cx="710" cy="130" r="18" class="node-even"/>
  <text x="710" y="130" class="node-txt">w2</text>

  <circle cx="680" cy="220" r="18" class="node-odd"/>
  <text x="680" y="220" class="node-txt">w3</text>

  <circle cx="580" cy="210" r="18" class="node-even"/>
  <text x="580" y="210" class="node-txt">w4</text>

  <!-- Edges Right -->
  <line x1="478" y1="147" x2="523" y2="113" class="edge"/>
  <line x1="558" y1="96" x2="612" y2="84" class="match-edge"/>
  <line x1="648" y1="91" x2="693" y2="119" class="edge"/>
  <line x1="702" y1="146" x2="688" y2="202" class="match-edge"/>
  <line x1="663" y1="218" x2="598" y2="212" class="edge"/>
  <line x1="571" y1="194" x2="549" y2="116" class="match-edge"/>

  <text x="600" y="270" text-anchor="middle" class="label">Цикл (b, w1, w2, w3, w4): вершина w2 і парна, і непарна!</text>
</svg>'''
    with open(os.path.join(img_dir, "fig1-bipartite-vs-general.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

def create_fig2():
    """Figure 2: Structure of Blossom, Stem, and Base."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
    .label { font-family: sans-serif; font-size: 13px; fill: #334155; }
    .node-txt { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }
    .edge { stroke: #64748b; stroke-width: 2; }
    .match-edge { stroke: #2563eb; stroke-width: 4; }
    .blossom-bg { fill: #fef3c7; stroke: #f59e0b; stroke-width: 2; stroke-dasharray: 6,4; rx: 20; }
    .stem-bg { fill: #e0f2fe; stroke: #0284c7; stroke-width: 2; stroke-dasharray: 6,4; rx: 15; }
    .node-root { fill: #dc2626; stroke: #991b1b; stroke-width: 2; }
    .node-base { fill: #10b981; stroke: #047857; stroke-width: 2; }
    .node-blossom { fill: #d97706; stroke: #b45309; stroke-width: 2; }
    .node-stem { fill: #0284c7; stroke: #0369a1; stroke-width: 2; }
  </style>
  <rect width="100%" height="100%" class="bg"/>

  <text x="400" y="30" text-anchor="middle" class="title">Будова квітки (Blossom) та стебла (Stem)</text>

  <!-- Background highlights -->
  <!-- Stem Region -->
  <rect x="50" y="70" width="280" height="180" class="stem-bg"/>
  <text x="190" y="95" text-anchor="middle" class="label" font-weight="bold" fill="#0369a1">Стебло P (Stem)</text>

  <!-- Blossom Region -->
  <rect x="360" y="60" width="390" height="220" class="blossom-bg"/>
  <text x="555" y="85" text-anchor="middle" class="label" font-weight="bold" fill="#b45309">Квітка B (Blossom: 2k + 1 = 5 вершин)</text>

  <!-- Stem Edges & Nodes -->
  <circle cx="90" cy="160" r="18" class="node-root"/>
  <text x="90" y="160" class="node-txt">r</text>

  <circle cx="180" cy="160" r="18" class="node-stem"/>
  <text x="180" y="160" class="node-txt">s1</text>

  <circle cx="270" cy="160" r="18" class="node-stem"/>
  <text x="270" y="160" class="node-txt">s2</text>

  <line x1="108" y1="160" x2="162" y2="160" class="edge"/>
  <line x1="198" y1="160" x2="252" y2="160" class="match-edge"/>

  <!-- Connection Stem to Base -->
  <line x1="288" y1="160" x2="392" y2="160" class="edge"/>

  <!-- Blossom Base Node -->
  <circle cx="410" cy="160" r="20" class="node-base"/>
  <text x="410" y="160" class="node-txt">b</text>

  <!-- Other Blossom Nodes -->
  <circle cx="490" cy="100" r="18" class="node-blossom"/>
  <text x="490" y="100" class="node-txt">v1</text>

  <circle cx="590" cy="100" r="18" class="node-blossom"/>
  <text x="590" y="100" class="node-txt">v2</text>

  <circle cx="630" cy="190" r="18" class="node-blossom"/>
  <text x="630" y="190" class="node-txt">v3</text>

  <circle cx="520" cy="220" r="18" class="node-blossom"/>
  <text x="520" y="220" class="node-txt">v4</text>

  <!-- Blossom Edges (Alternating) -->
  <line x1="426" y1="148" x2="474" y2="112" class="match-edge"/>
  <line x1="508" y1="100" x2="572" y2="100" class="edge"/>
  <line x1="603" y1="113" x2="617" y2="177" class="match-edge"/>
  <line x1="616" y1="199" x2="538" y2="216" class="edge"/>
  <line x1="503" y1="214" x2="422" y2="173" class="match-edge"/>

  <!-- Labels -->
  <text x="90" y="200" text-anchor="middle" class="label">Корінь r</text>
  <text x="410" y="200" text-anchor="middle" class="label">Основа b</text>
  <text x="400" y="295" text-anchor="middle" class="label">Основа b — єдина вершина квітки, незанята її внутрішніми ребрами паросполучення</text>
</svg>'''
    with open(os.path.join(img_dir, "fig2-blossom-structure.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

def create_fig3():
    """Figure 3: Blossom Contraction and Unshrinking."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .title { font-family: sans-serif; font-size: 15px; font-weight: bold; fill: #1e293b; }
    .label { font-family: sans-serif; font-size: 12px; fill: #334155; }
    .node-txt { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }
    .edge { stroke: #64748b; stroke-width: 2; }
    .match-edge { stroke: #2563eb; stroke-width: 4; }
    .aug-path { stroke: #dc2626; stroke-width: 3; stroke-dasharray: 5,4; }
    .node-norm { fill: #0284c7; stroke: #0369a1; stroke-width: 2; }
    .node-pseudo { fill: #d97706; stroke: #b45309; stroke-width: 3; }
    .panel { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1; rx: 8; }
    .arrow { fill: #0f172a; }
  </style>
  <rect width="100%" height="100%" class="bg"/>

  <!-- Left: Original Graph G with Blossom -->
  <rect x="20" y="20" width="340" height="280" class="panel"/>
  <text x="190" y="45" text-anchor="middle" class="title">1. Початковий граф G з квіткою B</text>

  <circle cx="60" cy="160" r="16" class="node-norm"/>
  <text x="60" y="160" class="node-txt">r</text>

  <circle cx="130" cy="160" r="16" class="node-norm"/>
  <text x="130" y="160" class="node-txt">b</text>

  <!-- Blossom B nodes -->
  <circle cx="190" cy="110" r="16" class="node-norm"/>
  <text x="190" y="110" class="node-txt">v1</text>
  <circle cx="260" cy="120" r="16" class="node-norm"/>
  <text x="260" y="120" class="node-txt">v2</text>
  <circle cx="240" cy="200" r="16" class="node-norm"/>
  <text x="240" y="200" class="node-txt">v3</text>

  <circle cx="320" cy="120" r="16" class="node-norm"/>
  <text x="320" y="120" class="node-txt">t</text>

  <line x1="76" y1="160" x2="114" y2="160" class="edge"/>
  <line x1="144" y1="148" x2="176" y2="122" class="match-edge"/>
  <line x1="206" y1="113" x2="244" y2="117" class="edge"/>
  <line x1="256" y1="135" x2="244" y2="184" class="match-edge"/>
  <line x1="225" y1="195" x2="144" y2="168" class="edge"/>
  <line x1="276" y1="120" x2="304" y2="120" class="edge"/>

  <!-- Arrow Contraction -->
  <path d="M 370 160 L 410 160" stroke="#0f172a" stroke-width="3" marker-end="url(#arr)"/>
  <text x="390" y="145" text-anchor="middle" class="label" font-weight="bold">Стиснення</text>

  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" class="arrow" />
    </marker>
  </defs>

  <!-- Right: Contracted Graph G/B -->
  <rect x="430" y="20" width="350" height="280" class="panel"/>
  <text x="605" y="45" text-anchor="middle" class="title">2. Стиснутий граф G/B (знайдено шлях)</text>

  <circle cx="480" cy="160" r="16" class="node-norm"/>
  <text x="480" y="160" class="node-txt">r</text>

  <!-- Pseudo-node B -->
  <circle cx="600" cy="160" r="26" class="node-pseudo"/>
  <text x="600" y="160" class="node-txt">B</text>

  <circle cx="720" cy="160" r="16" class="node-norm"/>
  <text x="720" y="160" class="node-txt">t</text>

  <line x1="496" y1="160" x2="574" y2="160" class="aug-path"/>
  <line x1="626" y1="160" x2="704" y2="160" class="aug-path"/>

  <text x="605" y="230" text-anchor="middle" class="label">Шлях у G/B: r → B → t</text>
  <text x="605" y="250" text-anchor="middle" class="label">Розгортання: r → b → v3 → v2 → t</text>
</svg>'''
    with open(os.path.join(img_dir, "fig3-blossom-contraction.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

def create_fig4():
    """Figure 4: Alternating Forest BFS traversal."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%" height="100%">
  <style>
    .bg { fill: #ffffff; }
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
    .label { font-family: sans-serif; font-size: 12px; fill: #334155; }
    .node-txt { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }
    .edge { stroke: #64748b; stroke-width: 2; }
    .match-edge { stroke: #2563eb; stroke-width: 4; }
    .cross-edge { stroke: #dc2626; stroke-width: 3; stroke-dasharray: 4,4; }
    .node-even { fill: #10b981; stroke: #047857; stroke-width: 2; }
    .node-odd { fill: #f59e0b; stroke: #b45309; stroke-width: 2; }
    .panel { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1; rx: 8; }
  </style>
  <rect width="100%" height="100%" class="bg"/>

  <text x="400" y="30" text-anchor="middle" class="title">Пошук в ширину в чергувальному лісі (Alternating Forest BFS)</text>

  <!-- Tree 1 -->
  <rect x="30" y="55" width="340" height="235" class="panel"/>
  <text x="200" y="80" text-anchor="middle" class="title">Дерево T1 (корінь r1)</text>

  <circle cx="80" cy="160" r="18" class="node-even"/>
  <text x="80" y="160" class="node-txt">r1</text>
  <text x="80" y="192" text-anchor="middle" class="label">Парна (0)</text>

  <circle cx="180" cy="120" r="18" class="node-odd"/>
  <text x="180" y="120" class="node-txt">u1</text>

  <circle cx="270" cy="120" r="18" class="node-even"/>
  <text x="270" y="120" class="node-txt">u2</text>

  <circle cx="180" cy="210" r="18" class="node-odd"/>
  <text x="180" y="210" class="node-txt">u3</text>

  <circle cx="270" cy="210" r="18" class="node-even"/>
  <text x="270" y="210" class="node-txt">u4</text>

  <line x1="97" y1="153" x2="163" y2="127" class="edge"/>
  <line x1="198" y1="120" x2="252" y2="120" class="match-edge"/>

  <line x1="97" y1="167" x2="163" y2="203" class="edge"/>
  <line x1="198" y1="210" x2="252" y2="210" class="match-edge"/>

  <!-- Cross-edge in same tree => Blossom -->
  <line x1="270" y1="138" x2="270" y2="192" class="cross-edge"/>
  <text x="315" y="165" text-anchor="middle" class="label" fill="#dc2626" font-weight="bold">Квітка!</text>

  <!-- Tree 2 -->
  <rect x="430" y="55" width="340" height="235" class="panel"/>
  <text x="600" y="80" text-anchor="middle" class="title">Дерево T2 (корінь r2)</text>

  <circle cx="480" cy="160" r="18" class="node-even"/>
  <text x="480" y="160" class="node-txt">r2</text>
  <text x="480" y="192" text-anchor="middle" class="label">Парна (0)</text>

  <circle cx="580" cy="160" r="18" class="node-odd"/>
  <text x="580" y="160" class="node-txt">w1</text>

  <circle cx="680" cy="160" r="18" class="node-even"/>
  <text x="680" y="160" class="node-txt">w2</text>

  <line x1="498" y1="160" x2="562" y2="160" class="edge"/>
  <line x1="598" y1="160" x2="662" y2="160" class="match-edge"/>

  <!-- Cross-edge between trees => Augmenting Path -->
  <path d="M 288 120 C 350 80, 600 80, 680 142" fill="none" class="cross-edge"/>
  <text x="400" y="70" text-anchor="middle" class="label" fill="#dc2626" font-weight="bold">Доповняльний шлях між T1 і T2</text>

</svg>'''
    with open(os.path.join(img_dir, "fig4-alternating-forest.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    create_fig1()
    create_fig2()
    create_fig3()
    create_fig4()
    print("Generated 4 SVG figures successfully.")
