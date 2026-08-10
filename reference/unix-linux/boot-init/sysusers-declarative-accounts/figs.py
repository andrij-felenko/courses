import sys
import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect x="50" y="50" width="200" height="100" fill="#f0f0f0" stroke="#333"/>
    <text x="150" y="100" text-anchor="middle" font-family="sans-serif">sysusers.d/*.conf</text>
    
    <path d="M 250 100 L 350 100" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="350" y="50" width="200" height="100" fill="#e0e0ff" stroke="#333"/>
    <text x="450" y="100" text-anchor="middle" font-family="sans-serif">systemd-sysusers</text>
    
    <path d="M 550 80 L 650 50" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <path d="M 550 120 L 650 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="650" y="20" width="120" height="60" fill="#f0fff0" stroke="#333"/>
    <text x="710" y="55" text-anchor="middle" font-family="sans-serif">/etc/passwd</text>
    
    <rect x="650" y="120" width="120" height="60" fill="#f0fff0" stroke="#333"/>
    <text x="710" y="155" text-anchor="middle" font-family="sans-serif">/etc/group</text>
    
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
        </marker>
    </defs>
</svg>"""
    
    with open(os.path.join(os.path.dirname(__file__), "sysusers-flow.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
