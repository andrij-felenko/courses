import sys
import os

# Append the scripts directory to sys.path to import svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

try:
    import svgkit
except ImportError:
    # Minimal fallback if svgkit is not found
    class svgkit:
        @staticmethod
        def render(filename, width, height, content):
            with open(filename, 'w') as f:
                f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n')
                f.write(content)
                f.write('</svg>\n')

def main():
    content = """
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#333" />
        </marker>
    </defs>
    
    <!-- Traditional read/write -->
    <g transform="translate(50, 50)">
        <text x="150" y="-20" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">Традиційне копіювання (read / write)</text>
        
        <rect x="0" y="0" width="100" height="60" rx="5" fill="#e0f7fa" stroke="#006064" stroke-width="2"/>
        <text x="50" y="35" font-family="sans-serif" font-size="14" text-anchor="middle">Файл (Джерело)</text>
        
        <rect x="200" y="0" width="100" height="60" rx="5" fill="#f3e5f5" stroke="#4a148c" stroke-width="2"/>
        <text x="250" y="35" font-family="sans-serif" font-size="14" text-anchor="middle">User Space</text>
        
        <rect x="0" y="120" width="100" height="60" rx="5" fill="#e0f7fa" stroke="#006064" stroke-width="2"/>
        <text x="50" y="155" font-family="sans-serif" font-size="14" text-anchor="middle">Файл (Ціль)</text>
        
        <!-- Arrows -->
        <path d="M 100,30 C 150,30 150,30 190,30" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="150" y="25" font-family="monospace" font-size="12" text-anchor="middle">read()</text>
        
        <path d="M 250,60 C 250,90 100,150 100,150" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="180" y="110" font-family="monospace" font-size="12" text-anchor="middle">write()</text>
    </g>

    <!-- copy_file_range -->
    <g transform="translate(450, 50)">
        <text x="150" y="-20" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">copy_file_range (In-kernel / Offload)</text>
        
        <rect x="0" y="0" width="100" height="60" rx="5" fill="#e0f7fa" stroke="#006064" stroke-width="2"/>
        <text x="50" y="35" font-family="sans-serif" font-size="14" text-anchor="middle">Файл (Джерело)</text>
        
        <rect x="200" y="60" width="100" height="60" rx="5" fill="#e8f5e9" stroke="#1b5e20" stroke-width="2"/>
        <text x="250" y="95" font-family="sans-serif" font-size="14" text-anchor="middle">Kernel VFS / FS</text>
        
        <rect x="0" y="120" width="100" height="60" rx="5" fill="#e0f7fa" stroke="#006064" stroke-width="2"/>
        <text x="50" y="155" font-family="sans-serif" font-size="14" text-anchor="middle">Файл (Ціль)</text>
        
        <!-- Arrows -->
        <path d="M 100,30 C 150,30 200,60 200,70" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 200,110 C 150,150 100,150 100,150" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        
        <path d="M 50,60 C 50,90 50,120 50,120" fill="none" stroke="#e53935" stroke-width="3" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
        <text x="120" y="95" font-family="monospace" font-size="12" fill="#e53935" text-anchor="middle">Server-Side Copy / Reflink</text>
    </g>
    """
    
    filepath = os.path.join(os.path.dirname(__file__), "architecture.svg")
    try:
        svgkit.render(filepath, 800, 250, content)
    except Exception as e:
        # Fallback to local render
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="250">\n')
            f.write(content)
            f.write('</svg>\n')

if __name__ == "__main__":
    main()
