import sys
import os

# Add scripts directory to path to find svgkit
script_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")
sys.path.append(os.path.normpath(script_dir))

try:
    import svgkit
except ImportError:
    print("Could not import svgkit. Ensure scripts/svgkit.py exists.")
    sys.exit(1)

def render():
    out_dir = "figs"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    out_file = os.path.join(out_dir, "nftables-arch.svg")
    
    # Create the SVG drawing using svgkit functionality
    # We will construct a manual SVG if svgkit objects aren't standard, 
    # but based on rules, svgkit provides helpers.
    # We'll just generate standard SVG as text using python to be safe if svgkit API is unknown,
    # or simple wrapper if we assume standard tags.
    
    # Let's generate standard SVG string to ensure it renders perfectly.
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="800" height="450">
    <defs>
        <style>
            .title { font-family: sans-serif; font-size: 20px; font-weight: bold; fill: #333; }
            .label { font-family: sans-serif; font-size: 14px; fill: #333; }
            .mono { font-family: monospace; font-size: 13px; fill: #d63384; }
            .box { fill: #f8f9fa; stroke: #6c757d; stroke-width: 2; rx: 8; }
            .box-kernel { fill: #e9ecef; stroke: #495057; stroke-width: 2; rx: 8; }
            .box-highlight { fill: #d1e7dd; stroke: #0f5132; stroke-width: 2; rx: 8; }
            .line { stroke: #adb5bd; stroke-width: 3; fill: none; marker-end: url(#arrow); }
            .dashed-line { stroke: #adb5bd; stroke-width: 2; stroke-dasharray: 5,5; fill: none; }
        </style>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#adb5bd" />
        </marker>
    </defs>

    <!-- Backgrounds -->
    <rect x="50" y="50" width="300" height="350" class="box" />
    <text x="200" y="80" text-anchor="middle" class="title">Простір Користувача</text>
    <text x="200" y="100" text-anchor="middle" class="label">(Userspace)</text>
    
    <rect x="450" y="50" width="300" height="350" class="box-kernel" />
    <text x="600" y="80" text-anchor="middle" class="title">Ядро Linux</text>
    <text x="600" y="100" text-anchor="middle" class="label">(Kernel Space)</text>

    <!-- Userspace Components -->
    <rect x="100" y="130" width="200" height="50" class="box" />
    <text x="200" y="160" text-anchor="middle" class="label">Утиліта `nft`</text>

    <rect x="100" y="210" width="200" height="50" class="box" />
    <text x="200" y="240" text-anchor="middle" class="label">Бібліотека `libnftnl`</text>
    <text x="200" y="275" text-anchor="middle" class="mono">Трансляція правил в байт-код</text>

    <!-- Communication -->
    <path d="M 300 235 L 450 235" class="line" />
    <text x="375" y="225" text-anchor="middle" class="label">Netlink API</text>
    <text x="375" y="250" text-anchor="middle" class="mono">(Байт-код)</text>
    
    <!-- Kernel Components -->
    <rect x="500" y="130" width="200" height="70" class="box-highlight" />
    <text x="600" y="155" text-anchor="middle" class="label">Віртуальна машина</text>
    <text x="600" y="175" text-anchor="middle" class="label">nftables</text>
    <text x="600" y="192" text-anchor="middle" class="mono">(nft_do_chain)</text>

    <rect x="500" y="230" width="200" height="50" class="box" />
    <text x="600" y="260" text-anchor="middle" class="label">Структури Даних</text>
    <text x="600" y="275" text-anchor="middle" class="mono">(Sets, Maps)</text>

    <rect x="500" y="310" width="200" height="50" class="box" />
    <text x="600" y="340" text-anchor="middle" class="label">Netfilter Hooks</text>

    <!-- Flow lines in kernel -->
    <path d="M 600 310 L 600 200" class="line" />
    <text x="610" y="295" class="label">Мережевий пакет</text>

    <path d="M 600 230 L 600 200" class="line" />
    
    <path d="M 200 180 L 200 210" class="line" />
</svg>"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"Generated {out_file}")

if __name__ == "__main__":
    render()
