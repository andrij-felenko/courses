import sys
import os

sys.path.append(os.path.abspath("../../scripts"))
try:
    from svgkit import SVG, Rect, Text, Line, Circle, Path, Group
except ImportError:
    pass # In case scripts/svgkit.py doesn't exist yet, we mock it or fail gracefully

def render_audit_architecture():
    # Architecture of Linux Audit
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
    <rect width="100%" height="100%" fill="#ffffff" />
    <text x="400" y="30" font-family="sans-serif" font-size="24" text-anchor="middle" font-weight="bold">Архітектура Linux Audit Framework</text>
    
    <!-- User Space -->
    <rect x="50" y="80" width="700" height="150" fill="#f0f8ff" stroke="#333" stroke-width="2" rx="10" />
    <text x="400" y="105" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold" fill="#333">User Space (Простір користувача)</text>
    
    <!-- Kernel Space -->
    <rect x="50" y="270" width="700" height="200" fill="#e6ffe6" stroke="#333" stroke-width="2" rx="10" />
    <text x="400" y="295" font-family="sans-serif" font-size="18" text-anchor="middle" font-weight="bold" fill="#333">Kernel Space (Простір ядра)</text>
    
    <!-- Components -->
    <rect x="100" y="120" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="175" y="155" font-family="sans-serif" font-size="16" text-anchor="middle">auditctl</text>
    
    <rect x="325" y="120" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="400" y="155" font-family="sans-serif" font-size="16" text-anchor="middle">auditd</text>
    
    <rect x="550" y="120" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="625" y="145" font-family="sans-serif" font-size="16" text-anchor="middle">aureport /</text>
    <text x="625" y="165" font-family="sans-serif" font-size="16" text-anchor="middle">ausearch</text>
    
    <rect x="325" y="320" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="400" y="355" font-family="sans-serif" font-size="16" text-anchor="middle">kauditd</text>
    
    <rect x="100" y="380" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="175" y="415" font-family="sans-serif" font-size="16" text-anchor="middle">Syscall Filter</text>
    
    <rect x="550" y="380" width="150" height="60" fill="#fff" stroke="#333" rx="5" />
    <text x="625" y="415" font-family="sans-serif" font-size="16" text-anchor="middle">VFS (Файли)</text>
    
    <!-- Logs -->
    <rect x="325" y="20" width="150" height="40" fill="#ffeeee" stroke="#333" rx="5" />
    <text x="400" y="45" font-family="monospace" font-size="14" text-anchor="middle">audit.log</text>
    
    <!-- Arrows -->
    <!-- auditctl to kauditd -->
    <line x1="175" y1="180" x2="175" y2="350" stroke="#333" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>
    <line x1="175" y1="350" x2="325" y2="350" stroke="#333" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>
    <text x="210" y="340" font-family="sans-serif" font-size="12">Конфігурація (Netlink)</text>

    <!-- kauditd to auditd -->
    <line x1="400" y1="320" x2="400" y2="180" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="410" y="250" font-family="sans-serif" font-size="12">Події (Netlink)</text>
    
    <!-- auditd to log -->
    <line x1="400" y1="120" x2="400" y2="60" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- kauditd to filters -->
    <line x1="325" y1="350" x2="250" y2="350" stroke="#333" stroke-width="2"/>
    <line x1="250" y1="350" x2="250" y2="380" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <line x1="475" y1="350" x2="550" y2="350" stroke="#333" stroke-width="2"/>
    <line x1="550" y1="350" x2="550" y2="380" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#333" />
        </marker>
    </defs>
</svg>"""

def render():
    with open("audit-architecture.svg", "w", encoding="utf-8") as f:
        f.write(render_audit_architecture())

if __name__ == "__main__":
    render()
