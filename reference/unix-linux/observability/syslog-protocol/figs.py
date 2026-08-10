import os
import sys

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
    <style>
        .box { fill: #f0f0f0; stroke: #333; stroke-width: 2px; }
        .text { font-family: sans-serif; font-size: 14px; fill: #333; text-anchor: middle; }
        .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #333; }
        .arrow { stroke: #333; stroke-width: 2px; marker-end: url(#arrowhead); }
    </style>
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>
    
    <text x="400" y="30" class="title" text-anchor="middle">RFC 5424 Syslog Message Format</text>
    
    <rect x="50" y="60" width="100" height="40" class="box" />
    <text x="100" y="85" class="text">&lt;PRIVAL&gt;</text>
    <text x="100" y="120" class="text" font-size="12">e.g. &lt;165&gt;</text>
    
    <rect x="150" y="60" width="60" height="40" class="box" />
    <text x="180" y="85" class="text">VER</text>
    <text x="180" y="120" class="text" font-size="12">1</text>
    
    <rect x="210" y="60" width="160" height="40" class="box" />
    <text x="290" y="85" class="text">TIMESTAMP</text>
    <text x="290" y="120" class="text" font-size="12">2023-10-11T22:14:15Z</text>
    
    <rect x="370" y="60" width="120" height="40" class="box" />
    <text x="430" y="85" class="text">HOSTNAME</text>
    <text x="430" y="120" class="text" font-size="12">server.local</text>
    
    <rect x="490" y="60" width="140" height="40" class="box" />
    <text x="560" y="85" class="text">APP-NAME / PID</text>
    <text x="560" y="120" class="text" font-size="12">sshd / 1234</text>
    
    <rect x="630" y="60" width="120" height="40" class="box" />
    <text x="690" y="85" class="text">MSG</text>
    <text x="690" y="120" class="text" font-size="12">Failed login</text>
</svg>"""

    os.makedirs('img', exist_ok=True)
    with open('img/syslog-format.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    render()
