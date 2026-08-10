import sys
import os

sys.path.append(os.path.abspath("../../../../scripts"))

try:
    from svgkit import render, SVG
    has_svgkit = True
except ImportError:
    has_svgkit = False

def create_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#f0f0f0"/>
    <text x="400" y="50" font-family="Arial" font-size="24" text-anchor="middle" font-weight="bold">AMD SEV vs Intel TDX Architecture</text>
    
    <!-- AMD SEV -->
    <rect x="50" y="100" width="300" height="250" fill="#ccffcc" stroke="#009900" stroke-width="2"/>
    <text x="200" y="130" font-family="Arial" font-size="20" text-anchor="middle" font-weight="bold">AMD SEV-SNP</text>
    <rect x="70" y="150" width="260" height="60" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="200" y="185" font-family="Arial" font-size="16" text-anchor="middle">VM (Encrypted Memory &amp; State)</text>
    <rect x="70" y="220" width="260" height="50" fill="#ffcccc" stroke="#cc0000" stroke-width="1"/>
    <text x="200" y="250" font-family="Arial" font-size="16" text-anchor="middle">Untrusted Hypervisor</text>
    <rect x="70" y="280" width="260" height="50" fill="#cce5ff" stroke="#0066cc" stroke-width="1"/>
    <text x="200" y="310" font-family="Arial" font-size="16" text-anchor="middle">AMD Secure Processor (ASP)</text>

    <!-- Intel TDX -->
    <rect x="450" y="100" width="300" height="250" fill="#ccffcc" stroke="#009900" stroke-width="2"/>
    <text x="600" y="130" font-family="Arial" font-size="20" text-anchor="middle" font-weight="bold">Intel TDX</text>
    <rect x="470" y="150" width="260" height="60" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="600" y="185" font-family="Arial" font-size="16" text-anchor="middle">Trust Domain (TD)</text>
    <rect x="470" y="220" width="260" height="50" fill="#ffcccc" stroke="#cc0000" stroke-width="1"/>
    <text x="600" y="250" font-family="Arial" font-size="16" text-anchor="middle">Untrusted Hypervisor (KVM)</text>
    <rect x="470" y="280" width="260" height="50" fill="#cce5ff" stroke="#0066cc" stroke-width="1"/>
    <text x="600" y="310" font-family="Arial" font-size="16" text-anchor="middle">Intel TDX Module (SEAM)</text>
</svg>"""

    with open("sev-tdx.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    if has_svgkit:
        # Dummy call to render if it exists
        pass

if __name__ == "__main__":
    create_svg()
