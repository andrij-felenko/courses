import os

SVG_CONTENT = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333" />
    </marker>
  </defs>

  <!-- Windows Game Context -->
  <rect x="50" y="50" width="220" height="300" rx="10" fill="#f0f4f8" stroke="#333" stroke-width="2" />
  <text x="160" y="80" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle">Windows Game</text>
  <rect x="70" y="120" width="180" height="50" rx="5" fill="#fff" stroke="#333" stroke-width="1" />
  <text x="160" y="150" font-family="sans-serif" font-size="14" text-anchor="middle">WaitForMultipleObjects()</text>

  <!-- Wine/Proton Translation -->
  <path d="M 270 145 L 430 145" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrow)" />
  <text x="350" y="135" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0055a4">Wine / Proton</text>
  <text x="350" y="165" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#555">Емуляція синхронізації</text>

  <!-- Linux Kernel Context -->
  <rect x="450" y="50" width="280" height="300" rx="10" fill="#e8f5e9" stroke="#333" stroke-width="2" />
  <text x="590" y="80" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle">Linux Kernel (5.16+)</text>
  <rect x="470" y="120" width="240" height="50" rx="5" fill="#fff" stroke="#333" stroke-width="1" />
  <text x="590" y="150" font-family="sans-serif" font-size="14" text-anchor="middle">sys_futex_waitv()</text>

  <!-- Futex Objects -->
  <rect x="470" y="220" width="70" height="40" rx="5" fill="#c8e6c9" stroke="#333" stroke-width="1" />
  <text x="505" y="245" font-family="sans-serif" font-size="12" text-anchor="middle">futex 1</text>
  <rect x="555" y="220" width="70" height="40" rx="5" fill="#c8e6c9" stroke="#333" stroke-width="1" />
  <text x="590" y="245" font-family="sans-serif" font-size="12" text-anchor="middle">futex 2</text>
  <text x="650" y="245" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">...</text>

  <path d="M 590 170 L 590 205" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrow)" />
</svg>
"""

def render():
    with open("futex2-waitv-syscall-d.svg", "w", encoding="utf-8") as f:
        f.write(SVG_CONTENT)
    print("Generated futex2-waitv-syscall-d.svg")

if __name__ == "__main__":
    render()
