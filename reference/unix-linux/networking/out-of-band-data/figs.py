import sys
import os

# Спрощений figs.py для генерації SVG
def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
  <defs>
    <style>
      .bg { fill: #f8f9fa; }
      .box { fill: #ffffff; stroke: #343a40; stroke-width: 2; }
      .text { font-family: monospace; font-size: 16px; fill: #212529; }
      .title { font-family: sans-serif; font-size: 20px; font-weight: bold; }
      .urg { fill: #dc3545; }
      .arrow { stroke: #dc3545; stroke-width: 2; marker-end: url(#arrowhead); }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#dc3545" />
    </marker>
  </defs>
  <rect width="800" height="300" class="bg" />
  
  <text x="30" y="40" class="title">Заголовок TCP та покажчик терміновости</text>
  
  <rect x="50" y="80" width="700" height="120" class="box" />
  
  <line x1="50" y1="120" x2="750" y2="120" stroke="#343a40" stroke-width="2"/>
  <line x1="50" y1="160" x2="750" y2="160" stroke="#343a40" stroke-width="2"/>
  
  <line x1="400" y1="80" x2="400" y2="160" stroke="#343a40" stroke-width="2"/>
  
  <text x="180" y="105" class="text">Source Port</text>
  <text x="530" y="105" class="text">Destination Port</text>
  
  <text x="350" y="145" class="text">Sequence Number</text>
  
  <text x="350" y="185" class="text">Acknowledgment Number</text>
  
  <!-- Flags and Urgent Pointer -->
  <line x1="50" y1="200" x2="750" y2="200" stroke="#343a40" stroke-width="2"/>
  <line x1="150" y1="160" x2="150" y2="200" stroke="#343a40" stroke-width="2"/>
  <line x1="250" y1="160" x2="250" y2="200" stroke="#343a40" stroke-width="2"/>
  <line x1="400" y1="160" x2="400" y2="200" stroke="#343a40" stroke-width="2"/>
  <line x1="500" y1="160" x2="500" y2="200" stroke="#343a40" stroke-width="2"/>
  
  <text x="75" y="185" class="text">HLEN</text>
  <text x="175" y="185" class="text">Resvd</text>
  
  <!-- Flags -->
  <text x="270" y="185" class="text" style="font-size: 14px;">C E <tspan class="urg">U</tspan> A P R S F</text>
  <circle cx="304" cy="180" r="12" fill="none" stroke="#dc3545" stroke-width="2" />
  
  <text x="415" y="185" class="text">Window Size</text>
  
  <text x="540" y="185" class="text urg" font-weight="bold">Urgent Pointer</text>
  
  <path d="M 310 192 L 350 250 L 530 250 L 600 200" fill="none" class="arrow"/>
  <text x="400" y="270" class="text" fill="#dc3545">URG=1 активує Urgent Pointer</text>

</svg>"""
    
    with open('tcp-urgent-pointer.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    render()
