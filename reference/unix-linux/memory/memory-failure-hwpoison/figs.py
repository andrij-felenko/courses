# -*- coding: utf-8 -*-
"""Фігури до теми «Апаратна помилка пам'яті: hwpoison» (reference/unix-linux/memory)."""
import os

svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="250" viewBox="0 0 800 250" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333" />
    </marker>
  </defs>

  <!-- Rectangles -->
  <rect x="20" y="80" width="140" height="60" rx="8" fill="#ffcccc" stroke="#cc0000" stroke-width="2"/>
  <rect x="200" y="80" width="160" height="60" rx="8" fill="#e6f2ff" stroke="#0066cc" stroke-width="2"/>
  <rect x="400" y="80" width="160" height="60" rx="8" fill="#e6f2ff" stroke="#0066cc" stroke-width="2"/>
  <rect x="600" y="80" width="160" height="60" rx="8" fill="#ffffcc" stroke="#cccc00" stroke-width="2"/>

  <!-- Texts in rects -->
  <text x="90" y="105" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">Hardware</text>
  <text x="90" y="125" text-anchor="middle" font-size="12" fill="#333">MCE (Memory Error)</text>

  <text x="280" y="105" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">Linux Kernel</text>
  <text x="280" y="125" text-anchor="middle" font-size="12" fill="#333">Set PG_hwpoison</text>

  <text x="480" y="105" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">Linux Kernel</text>
  <text x="480" y="125" text-anchor="middle" font-size="12" fill="#333">Unmap (no signal yet)</text>

  <text x="680" y="105" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">User Process</text>
  <text x="680" y="125" text-anchor="middle" font-size="12" fill="#333">SIGBUS on access</text>

  <!-- Arrows -->
  <line x1="160" y1="110" x2="190" y2="110" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="360" y1="110" x2="390" y2="110" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="560" y1="110" x2="590" y2="110" stroke="#333" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Descriptions -->
  <text x="175" y="90" text-anchor="middle" font-size="10" fill="#666">#MC</text>
  <text x="375" y="90" text-anchor="middle" font-size="10" fill="#666">RMAP</text>
  <text x="575" y="90" text-anchor="middle" font-size="10" fill="#666">fault</text>
</svg>
"""

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "hwpoison-flow.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)

print("Created img/hwpoison-flow.svg")
