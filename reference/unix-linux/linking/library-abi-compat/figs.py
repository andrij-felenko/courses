import os

svg_content = """<svg width="600" height="250" xmlns="http://www.w3.org/2000/svg">
  <style>
    .box { fill: #f8f9fa; stroke: #343a40; stroke-width: 2px; }
    .text { font-family: monospace; font-size: 14px; fill: #212529; }
    .padding { fill: #e9ecef; stroke: #343a40; stroke-width: 2px; stroke-dasharray: 4; }
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #212529; }
  </style>

  <text x="50" y="30" class="title">V1: struct { char a; int b; }</text>
  <rect x="50" y="50" width="50" height="40" class="box" />
  <text x="70" y="75" class="text">a (1)</text>
  
  <rect x="100" y="50" width="150" height="40" class="padding" />
  <text x="130" y="75" class="text">padding (3)</text>
  
  <rect x="250" y="50" width="200" height="40" class="box" />
  <text x="330" y="75" class="text">b (4)</text>

  <text x="50" y="140" class="title">V2 (Порушення ABI): struct { char a; short c; int b; }</text>
  <rect x="50" y="160" width="50" height="40" class="box" />
  <text x="70" y="185" class="text">a (1)</text>

  <rect x="100" y="160" width="50" height="40" class="padding" />
  <text x="110" y="185" class="text">pad</text>

  <rect x="150" y="160" width="100" height="40" class="box" />
  <text x="180" y="185" class="text">c (2)</text>

  <rect x="250" y="160" width="200" height="40" class="box" />
  <text x="330" y="185" class="text">b (4)</text>
</svg>
"""

def render():
    with open("struct-layout.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("SVG generated successfully.")

if __name__ == "__main__":
    render()
