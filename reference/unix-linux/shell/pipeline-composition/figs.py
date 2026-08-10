import os
import sys

def render():
    svg1 = """<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
  <g font-family="sans-serif" font-size="14">
    <!-- Kernel Space -->
    <rect x="200" y="50" width="200" height="200" fill="#e0e0e0" stroke="#999" rx="10"/>
    <text x="300" y="70" text-anchor="middle" font-weight="bold">Kernel Space</text>
    
    <!-- Pipe Buffer -->
    <rect x="250" y="100" width="100" height="100" fill="#cce5ff" stroke="#66b2ff" rx="5"/>
    <text x="300" y="150" text-anchor="middle">64KB Ring Buffer</text>
    
    <!-- Process 1 -->
    <rect x="20" y="100" width="120" height="100" fill="#ffebcc" stroke="#ffb366" rx="5"/>
    <text x="80" y="140" text-anchor="middle">Process 1</text>
    <text x="80" y="160" text-anchor="middle">(Writer)</text>
    
    <!-- Process 2 -->
    <rect x="460" y="100" width="120" height="100" fill="#d9f2d9" stroke="#8cbf8c" rx="5"/>
    <text x="520" y="140" text-anchor="middle">Process 2</text>
    <text x="520" y="160" text-anchor="middle">(Reader)</text>
    
    <!-- Arrows -->
    <path d="M140 150 L240 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <path d="M350 150 L450 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- Marker definition -->
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#333" />
      </marker>
    </defs>
  </g>
</svg>"""
    
    svg2 = """<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <g font-family="monospace" font-size="12">
    <!-- FDs -->
    <text x="50" y="50" font-weight="bold">Parent (Shell)</text>
    <text x="50" y="80">0: stdin</text>
    <text x="50" y="100">1: stdout</text>
    
    <path d="M100 120 L100 180" stroke="#333" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="110" y="150">fork()</text>
    
    <text x="50" y="220" font-weight="bold">Child (Writer: ls)</text>
    <text x="50" y="250">0: stdin</text>
    <text x="50" y="270" fill="red">1: stdout -> dup2(pipe[1])</text>
    <text x="50" y="290">3: pipefd[0] (closed)</text>
    <text x="50" y="310">4: pipefd[1] (closed)</text>
    
    <text x="350" y="220" font-weight="bold">Child (Reader: wc)</text>
    <text x="350" y="250" fill="green">0: stdin -> dup2(pipe[0])</text>
    <text x="350" y="270">1: stdout</text>
    <text x="350" y="290">3: pipefd[0] (closed)</text>
    <text x="350" y="310">4: pipefd[1] (closed)</text>
  </g>
</svg>"""

    base_path = os.path.dirname(__file__)
    
    with open(os.path.join(base_path, 'pipe-buffer.svg'), 'w', encoding='utf-8') as f:
        f.write(svg1)
        
    with open(os.path.join(base_path, 'fork-dup2.svg'), 'w', encoding='utf-8') as f:
        f.write(svg2)

if __name__ == '__main__':
    render()
