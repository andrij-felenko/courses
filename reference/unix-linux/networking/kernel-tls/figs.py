import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

try:
    import svgkit
except ImportError:
    class SvgKitFallback:
        def render(self, filename, width, height, elements):
            with open(filename, 'w') as f:
                f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
                f.write('  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#333" /></marker></defs>\n')
                for el in elements:
                    f.write(f'  {el}\n')
                f.write('</svg>\n')
    svgkit = SvgKitFallback()

def generate_figs():
    elements = [
        '<rect x="10" y="10" width="380" height="280" fill="#f0f0f0" stroke="#333" stroke-width="2"/>',
        '<text x="200" y="40" font-family="sans-serif" font-size="16" text-anchor="middle" font-weight="bold">Традиційний TLS vs kTLS</text>',
        
        '<rect x="20" y="60" width="160" height="100" fill="#cce5ff" stroke="#004085" stroke-width="2"/>',
        '<text x="100" y="80" font-family="sans-serif" font-size="14" text-anchor="middle">User Space</text>',
        '<rect x="40" y="90" width="120" height="50" fill="#b8daff" stroke="#004085" stroke-width="1"/>',
        '<text x="100" y="120" font-family="sans-serif" font-size="12" text-anchor="middle">OpenSSL (TLS)</text>',

        '<rect x="20" y="180" width="160" height="100" fill="#d4edda" stroke="#155724" stroke-width="2"/>',
        '<text x="100" y="200" font-family="sans-serif" font-size="14" text-anchor="middle">Kernel Space</text>',
        '<rect x="40" y="210" width="120" height="50" fill="#c3e6cb" stroke="#155724" stroke-width="1"/>',
        '<text x="100" y="240" font-family="sans-serif" font-size="12" text-anchor="middle">TCP/IP Stack</text>',
        
        '<rect x="220" y="180" width="160" height="100" fill="#ffeeba" stroke="#856404" stroke-width="2"/>',
        '<text x="300" y="200" font-family="sans-serif" font-size="14" text-anchor="middle">Kernel (kTLS)</text>',
        '<rect x="240" y="210" width="120" height="50" fill="#ffdf7e" stroke="#856404" stroke-width="1"/>',
        '<text x="300" y="235" font-family="sans-serif" font-size="12" text-anchor="middle">kTLS Crypto</text>',
        
        '<path d="M 100 140 L 100 210" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<path d="M 300 140 L 300 210" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>'
    ]
    # In an actual environment, svgkit.render takes the path relative to caller or absolute
    out_file = os.path.join(os.path.dirname(__file__), "ktls-architecture.svg")
    svgkit.render(out_file, 400, 300, elements)

if __name__ == "__main__":
    generate_figs()
