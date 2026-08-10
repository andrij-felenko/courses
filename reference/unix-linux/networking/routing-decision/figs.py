import sys
import os

def render():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <rect width="100%" height="100%" fill="#f8f9fa"/>
    <text x="300" y="40" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#343a40">Linux Routing Decision Process</text>
    
    <rect x="50" y="80" width="140" height="50" rx="5" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="120" y="110" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#212529">Incoming Packet</text>
    
    <line x1="190" y1="105" x2="240" y2="105" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="250" y="80" width="140" height="50" rx="5" fill="#fff3cd" stroke="#ffe69c" stroke-width="2"/>
    <text x="320" y="110" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#856404">ip rule (PBR)</text>
    
    <line x1="390" y1="105" x2="440" y2="105" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="450" y="80" width="120" height="50" rx="5" fill="#d1e7dd" stroke="#a3cfbb" stroke-width="2"/>
    <text x="510" y="110" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#0f5132">FIB Lookup</text>
    
    <line x1="510" y1="130" x2="510" y2="180" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="430" y="190" width="160" height="60" rx="5" fill="#cff4fc" stroke="#9eeaf9" stroke-width="2"/>
    <text x="510" y="215" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#055160">LC-Trie Traversal</text>
    <text x="510" y="235" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#055160">(Longest Prefix Match)</text>
    
    <line x1="510" y1="250" x2="510" y2="300" stroke="#495057" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="430" y="310" width="160" height="50" rx="5" fill="#e2e3e5" stroke="#d3d6d8" stroke-width="2"/>
    <text x="510" y="340" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#383d41">Next Hop Selected</text>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#495057" />
        </marker>
    </defs>
</svg>"""
    out_dir = os.path.dirname(__file__)
    out_path = os.path.join(out_dir, "routing_flow.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    render()
