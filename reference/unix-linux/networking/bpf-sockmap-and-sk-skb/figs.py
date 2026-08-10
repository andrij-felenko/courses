import sys
import os
import math

# We add the common scripts directory to the python path to import svgkit
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, "../../../../scripts")))

try:
    import svgkit
except ImportError:
    # If svgkit isn't available, we create a very simple mockup SVG writer to not fail
    class _MockSvg:
        def __init__(self, w, h):
            self.w = w
            self.h = h
            self.elements = []
            
        def add(self, el):
            self.elements.append(el)
            
        def save(self, p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(f'<svg width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg">\n')
                f.write("</svg>")
                
    svgkit = type('svgkit', (), {'Drawing': _MockSvg})

def generate_svg():
    try:
        doc = svgkit.Drawing(800, 500)
        
        # We need a proper representation since we don't have the actual svgkit class methods
        # let's just write raw XML if svgkit fails or is a mock, but assuming svgkit has a specific API
        pass
    except Exception:
        pass
        
    # Standard XML creation as a fallback and to ensure SVG is definitely generated properly.
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#d32f2f"/>
    </marker>
  </defs>
  <!-- Background -->
  <rect x="10" y="10" width="780" height="480" rx="10" fill="#f9f9f9" stroke="#ccc"/>
  
  <text x="400" y="50" font-size="24" text-anchor="middle" font-weight="bold" font-family="sans-serif">Socket Redirection with BPF SOCKMAP</text>
  
  <!-- Process A -->
  <rect x="50" y="100" width="200" height="150" rx="5" fill="#e1f5fe" stroke="#0288d1"/>
  <text x="150" y="130" text-anchor="middle" font-size="16" font-family="sans-serif">Process A (Proxy)</text>
  <rect x="70" y="160" width="160" height="40" rx="3" fill="#fff" stroke="#aaa"/>
  <text x="150" y="185" text-anchor="middle" font-family="sans-serif">Socket 1 (FD: 5)</text>
  
  <!-- Process B -->
  <rect x="550" y="100" width="200" height="150" rx="5" fill="#e1f5fe" stroke="#0288d1"/>
  <text x="650" y="130" text-anchor="middle" font-size="16" font-family="sans-serif">Process B (Backend)</text>
  <rect x="570" y="160" width="160" height="40" rx="3" fill="#fff" stroke="#aaa"/>
  <text x="650" y="185" text-anchor="middle" font-family="sans-serif">Socket 2 (FD: 8)</text>
  
  <!-- Kernel Space -->
  <rect x="50" y="300" width="700" height="160" rx="5" fill="#e8f5e9" stroke="#388e3c"/>
  <text x="150" y="330" text-anchor="middle" font-weight="bold" font-family="sans-serif">Kernel TCP/IP Stack</text>
  
  <!-- SOCKMAP -->
  <rect x="300" y="320" width="200" height="120" rx="5" fill="#fff3e0" stroke="#f57c00"/>
  <text x="400" y="345" text-anchor="middle" font-size="14" font-weight="bold" font-family="sans-serif">BPF_MAP_TYPE_SOCKMAP</text>
  <text x="400" y="375" text-anchor="middle" font-size="12" font-family="sans-serif">Key 0: Socket 1</text>
  <text x="400" y="395" text-anchor="middle" font-size="12" font-family="sans-serif">Key 1: Socket 2</text>
  
  <!-- Connections -->
  <line x1="150" y1="200" x2="150" y2="350" stroke="#666" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="650" y1="200" x2="650" y2="350" stroke="#666" stroke-width="2" stroke-dasharray="4,4"/>
  
  <!-- Redirection arrow -->
  <path d="M 150 350 C 150 430, 300 400, 390 400 C 480 400, 650 430, 650 350" fill="none" stroke="#d32f2f" stroke-width="3" marker-end="url(#arrow)"/>
  
  <text x="400" y="440" text-anchor="middle" font-size="14" font-weight="bold" fill="#d32f2f" font-family="sans-serif">Zero-Copy BPF Redirection</text>
  
</svg>
"""
    with open(os.path.join(script_dir, "fig-sockmap-redir.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("Generated fig-sockmap-redir.svg successfully.")

if __name__ == "__main__":
    generate_svg()
