def main():
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    <text x="400" y="50" font-family="Arial" font-size="24" text-anchor="middle">perf Architecture</text>
    <rect x="300" y="100" width="200" height="80" fill="#f0f0f0" stroke="black"/>
    <text x="400" y="145" font-family="Arial" font-size="16" text-anchor="middle">User Space (perf tool)</text>
    
    <line x1="400" y1="180" x2="400" y2="250" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="200" y="250" width="400" height="150" fill="#e0e0ff" stroke="black"/>
    <text x="400" y="280" font-family="Arial" font-size="16" text-anchor="middle">Kernel Space (perf_events subsystem)</text>
    
    <rect x="220" y="310" width="160" height="60" fill="#c0c0ff" stroke="black"/>
    <text x="300" y="345" font-family="Arial" font-size="14" text-anchor="middle">PMU Drivers</text>

    <rect x="420" y="310" width="160" height="60" fill="#c0c0ff" stroke="black"/>
    <text x="500" y="345" font-family="Arial" font-size="14" text-anchor="middle">Ring Buffer</text>
</svg>
'''
    with open('perf_architecture.svg', 'w') as f:
        f.write(svg_content)
    print("Successfully generated perf_architecture.svg")

if __name__ == '__main__':
    main()
