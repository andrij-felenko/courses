import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../scripts")))
try:
    import svgkit
except ImportError:
    # Dummy mock for testing
    class SvgKitMock:
        def render(self):
            return "<svg width=\"800\" height=\"400\"><rect width=\"800\" height=\"400\" fill=\"white\"/><text x=\"400\" y=\"200\" font-size=\"24\" text-anchor=\"middle\">BPF Trampoline Architecture</text></svg>"
    svgkit = SvgKitMock()

def render():
    with open("trampoline-arch.svg", "w", encoding="utf-8") as f:
        f.write("<svg width=\"800\" height=\"400\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"800\" height=\"400\" fill=\"#f8f9fa\"/><text x=\"400\" y=\"50\" font-size=\"20\" text-anchor=\"middle\" fill=\"black\">BPF Trampoline Mechanism</text><rect x=\"100\" y=\"100\" width=\"200\" height=\"100\" fill=\"#e9ecef\" stroke=\"black\"/><text x=\"200\" y=\"150\" font-size=\"16\" text-anchor=\"middle\">Kernel Function</text><path d=\"M 300 150 L 500 150\" stroke=\"black\" stroke-width=\"2\" marker-end=\"url(#arrow)\"/><rect x=\"500\" y=\"100\" width=\"200\" height=\"100\" fill=\"#d4edda\" stroke=\"black\"/><text x=\"600\" y=\"150\" font-size=\"16\" text-anchor=\"middle\">BPF Program</text></svg>")

if __name__ == "__main__":
    render()
