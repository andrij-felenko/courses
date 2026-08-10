import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect width="100%" height="100%" fill="#f9f9f9" />
    <style>
        .box { fill: #e0f2fe; stroke: #0284c7; stroke-width: 2; rx: 8; ry: 8; }
        .text { font-family: monospace; font-size: 14px; fill: #0f172a; text-anchor: middle; }
        .line { stroke: #94a3b8; stroke-width: 2; marker-end: url(#arrow); }
        .label { font-family: sans-serif; font-size: 12px; fill: #475569; }
    </style>
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
        </marker>
    </defs>
    
    <!-- Title -->
    <text x="400" y="30" font-family="sans-serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">TOMOYO Domain Tree (Дерево доменів)</text>

    <!-- Nodes -->
    <rect x="300" y="60" width="200" height="40" class="box" />
    <text x="400" y="85" class="text">&lt;kernel&gt;</text>

    <rect x="300" y="150" width="200" height="40" class="box" />
    <text x="400" y="175" class="text">&lt;kernel&gt; /sbin/init</text>

    <rect x="100" y="250" width="250" height="40" class="box" />
    <text x="225" y="275" class="text">&lt;kernel&gt; /sbin/init /usr/sbin/sshd</text>

    <rect x="450" y="250" width="250" height="40" class="box" />
    <text x="575" y="275" class="text">&lt;kernel&gt; /sbin/init /usr/sbin/nginx</text>

    <rect x="100" y="340" width="280" height="40" class="box" />
    <text x="240" y="365" class="text">... /usr/sbin/sshd /bin/bash</text>

    <!-- Lines -->
    <line x1="400" y1="100" x2="400" y2="140" class="line" />
    <text x="410" y="125" class="label">execve()</text>

    <line x1="400" y1="190" x2="225" y2="240" class="line" />
    <text x="310" y="210" class="label">execve()</text>

    <line x1="400" y1="190" x2="575" y2="240" class="line" />
    <text x="490" y="210" class="label">execve()</text>

    <line x1="225" y1="290" x2="240" y2="330" class="line" />
    <text x="240" y="315" class="label">execve()</text>

</svg>
"""
    with open("tomoyo-domain-tree.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("SVG generated successfully.")

if __name__ == "__main__":
    render()
