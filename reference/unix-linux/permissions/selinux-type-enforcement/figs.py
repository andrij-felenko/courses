import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect width="800" height="400" fill="#f8f9fa"/>
    <text x="400" y="30" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle">SELinux Type Enforcement (TE)</text>
    
    <!-- Subject (Process) -->
    <rect x="50" y="100" width="200" height="100" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="150" y="140" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle">Process (Subject)</text>
    <text x="150" y="170" font-family="Arial" font-size="14" fill="#495057" text-anchor="middle">Domain: httpd_t</text>
    
    <!-- Object (File) -->
    <rect x="550" y="100" width="200" height="100" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="650" y="140" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle">File (Object)</text>
    <text x="650" y="170" font-family="Arial" font-size="14" fill="#495057" text-anchor="middle">Type: httpd_sys_content_t</text>
    
    <!-- Kernel / Policy Server -->
    <rect x="300" y="250" width="200" height="100" rx="10" fill="#d4edda" stroke="#28a745" stroke-width="2"/>
    <text x="400" y="285" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle">SELinux Policy</text>
    <text x="400" y="315" font-family="Courier New" font-size="12" fill="#155724" text-anchor="middle">allow httpd_t httpd_sys_content_t</text>
    <text x="400" y="335" font-family="Courier New" font-size="12" fill="#155724" text-anchor="middle">: file { read getattr };</text>

    <!-- Arrows -->
    <path d="M 250 150 L 530 150" fill="none" stroke="#007bff" stroke-width="3" marker-end="url(#arrow)"/>
    <text x="400" y="140" font-family="Arial" font-size="14" font-weight="bold" fill="#007bff" text-anchor="middle">Access Request (read)</text>
    
    <path d="M 400 160 L 400 240" fill="none" stroke="#28a745" stroke-width="3" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
    <text x="470" y="200" font-family="Arial" font-size="14" font-style="italic" fill="#28a745" text-anchor="middle">Policy Check</text>
    
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="context-stroke" />
        </marker>
    </defs>
</svg>"""
    
    filepath = os.path.join(os.path.dirname(__file__), "selinux-te.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {filepath}")

if __name__ == "__main__":
    render()
