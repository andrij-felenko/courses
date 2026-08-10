import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
    <!-- Background -->
    <rect width="100%" height="100%" fill="#ffffff" />
    
    <!-- Entities -->
    <!-- Sensor Entity -->
    <rect x="50" y="150" width="150" height="100" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="10" />
    <text x="125" y="205" text-anchor="middle" font-family="sans-serif" font-weight="bold" fill="#0d47a1">Sensor Entity</text>
    <text x="125" y="225" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0d47a1">/dev/v4l2-subdev0</text>
    
    <!-- ISP Entity -->
    <rect x="300" y="150" width="150" height="100" fill="#e8f5e9" stroke="#388e3c" stroke-width="2" rx="10" />
    <text x="375" y="205" text-anchor="middle" font-family="sans-serif" font-weight="bold" fill="#1b5e20">ISP Entity</text>
    <text x="375" y="225" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1b5e20">/dev/v4l2-subdev1</text>
    
    <!-- Video Node Entity -->
    <rect x="550" y="150" width="150" height="100" fill="#fff3e0" stroke="#f57c00" stroke-width="2" rx="10" />
    <text x="625" y="205" text-anchor="middle" font-family="sans-serif" font-weight="bold" fill="#e65100">Video Node</text>
    <text x="625" y="225" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#e65100">/dev/video0</text>
    
    <!-- Pads -->
    <!-- Sensor Src Pad -->
    <circle cx="200" cy="200" r="8" fill="#ff9800" stroke="#000" />
    <text x="190" y="185" font-size="12" font-family="sans-serif" text-anchor="middle">Pad 0 (Src)</text>
    
    <!-- ISP Sink Pad -->
    <circle cx="300" cy="200" r="8" fill="#4caf50" stroke="#000" />
    <text x="310" y="185" font-size="12" font-family="sans-serif" text-anchor="middle">Pad 0 (Sink)</text>
    
    <!-- ISP Src Pad -->
    <circle cx="450" cy="200" r="8" fill="#ff9800" stroke="#000" />
    <text x="440" y="185" font-size="12" font-family="sans-serif" text-anchor="middle">Pad 1 (Src)</text>
    
    <!-- Video Node Sink Pad -->
    <circle cx="550" cy="200" r="8" fill="#4caf50" stroke="#000" />
    <text x="560" y="185" font-size="12" font-family="sans-serif" text-anchor="middle">Pad 0 (Sink)</text>
    
    <!-- Links -->
    <line x1="208" y1="200" x2="292" y2="200" stroke="#000" stroke-width="3" marker-end="url(#arrow)" />
    <text x="250" y="190" font-size="12" font-family="sans-serif" text-anchor="middle" fill="#666">Link</text>

    <line x1="458" y1="200" x2="542" y2="200" stroke="#000" stroke-width="3" marker-end="url(#arrow)" />
    <text x="500" y="190" font-size="12" font-family="sans-serif" text-anchor="middle" fill="#666">Link</text>
    
    <!-- Arrow Definition -->
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
    
    <!-- Media Controller Border -->
    <rect x="25" y="100" width="700" height="200" fill="none" stroke="#9e9e9e" stroke-width="2" stroke-dasharray="10,5" rx="15" />
    <text x="375" y="125" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="bold" fill="#757575">Media Controller Graph (/dev/media0)</text>
</svg>"""
    out_path = os.path.join(os.path.dirname(__file__), 'mc-graph.svg')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    render()
