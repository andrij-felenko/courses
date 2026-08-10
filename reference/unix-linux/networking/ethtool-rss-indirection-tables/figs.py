import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
try:
    import svgkit
except ImportError:
    print("WARNING: Could not import svgkit. Stubbing.")
    class SvgStub:
        def start(self, w, h): return f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
        def end(self): return "</svg>"
        def rect(self, x, y, w, h, fill="white", stroke="black"): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
        def text(self, x, y, txt, fontsize=12): return f'<text x="{x}" y="{y}" font-size="{fontsize}">{txt}</text>'
        def line(self, x1, y1, x2, y2, stroke="black"): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}"/>'

    svgkit = type('obj', (object,), {'SvgKit': SvgStub})

def render():
    figs_dir = os.path.join(os.path.dirname(__file__), 'figs')
    os.makedirs(figs_dir, exist_ok=True)
    
    # 1. Single Queue
    out_file1 = os.path.join(figs_dir, 'single_queue_interrupt.svg')
    with open(out_file1, 'w') as f:
        f.write('<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">\n')
        f.write('<rect x="50" y="50" width="100" height="200" fill="#ccddff" stroke="#003366"/>\n')
        f.write('<text x="100" y="40" text-anchor="middle" font-family="sans-serif" font-size="14">NIC</text>\n')
        f.write('<rect x="60" y="140" width="80" height="40" fill="#ffffff" stroke="#000000"/>\n')
        f.write('<text x="100" y="165" text-anchor="middle" font-family="sans-serif" font-size="12">1 Rx Queue</text>\n')
        
        f.write('<rect x="350" y="50" width="200" height="200" fill="#ffddcc" stroke="#663300"/>\n')
        f.write('<text x="450" y="40" text-anchor="middle" font-family="sans-serif" font-size="14">CPU Cores</text>\n')
        f.write('<rect x="370" y="70" width="160" height="30" fill="#ff9999" stroke="#cc0000"/>\n')
        f.write('<text x="450" y="90" text-anchor="middle" font-family="sans-serif" font-size="12">Core 0 (100% IRQ Storm)</text>\n')
        
        f.write('<rect x="370" y="110" width="160" height="30" fill="#ffffff" stroke="#000000"/>\n')
        f.write('<text x="450" y="130" text-anchor="middle" font-family="sans-serif" font-size="12">Core 1 (Idle)</text>\n')
        f.write('<rect x="370" y="150" width="160" height="30" fill="#ffffff" stroke="#000000"/>\n')
        f.write('<text x="450" y="170" text-anchor="middle" font-family="sans-serif" font-size="12">Core 2 (Idle)</text>\n')
        f.write('<rect x="370" y="190" width="160" height="30" fill="#ffffff" stroke="#000000"/>\n')
        f.write('<text x="450" y="210" text-anchor="middle" font-family="sans-serif" font-size="12">Core 3 (Idle)</text>\n')
        
        f.write('<line x1="140" y1="160" x2="370" y2="85" stroke="#cc0000" stroke-width="3" marker-end="url(#arrow)"/>\n')
        f.write('<text x="250" y="110" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#cc0000">All Interrupts</text>\n')
        
        f.write('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#cc0000" /></marker></defs>\n')
        
        f.write('</svg>\n')

    # 2. RSS Architecture
    out_file2 = os.path.join(figs_dir, 'rss_architecture.svg')
    with open(out_file2, 'w') as f:
        f.write('<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">\n')
        f.write('<rect x="10" y="10" width="780" height="380" fill="#f8f9fa" stroke="#dee2e6"/>\n')
        
        # Incoming Packet
        f.write('<rect x="30" y="160" width="120" height="60" fill="#d1e7dd" stroke="#0f5132" rx="5"/>\n')
        f.write('<text x="90" y="185" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">Incoming Packet</text>\n')
        f.write('<text x="90" y="205" text-anchor="middle" font-family="sans-serif" font-size="12">4-Tuple (IPs, Ports)</text>\n')
        
        # Parser & Hasher
        f.write('<rect x="200" y="140" width="140" height="100" fill="#cfe2ff" stroke="#084298" rx="5"/>\n')
        f.write('<text x="270" y="170" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">Toeplitz Hash</text>\n')
        f.write('<text x="270" y="195" text-anchor="middle" font-family="sans-serif" font-size="12">+ Secret Key</text>\n')
        f.write('<text x="270" y="225" text-anchor="middle" font-family="sans-serif" font-size="12">Result: 32-bit Hash</text>\n')
        
        f.write('<line x1="150" y1="190" x2="200" y2="190" stroke="#000" stroke-width="2" marker-end="url(#arrowBlack)"/>\n')
        
        # RETA
        f.write('<rect x="400" y="80" width="140" height="220" fill="#fff3cd" stroke="#664d03" rx="5"/>\n')
        f.write('<text x="470" y="105" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">RETA</text>\n')
        f.write('<text x="470" y="125" text-anchor="middle" font-family="sans-serif" font-size="12">(128 entries)</text>\n')
        
        f.write('<rect x="420" y="140" width="100" height="20" fill="#fff" stroke="#000"/>\n')
        f.write('<text x="440" y="154" font-family="monospace" font-size="12">0  ->  Q0</text>\n')
        f.write('<rect x="420" y="160" width="100" height="20" fill="#fff" stroke="#000"/>\n')
        f.write('<text x="440" y="174" font-family="monospace" font-size="12">1  ->  Q1</text>\n')
        f.write('<rect x="420" y="180" width="100" height="20" fill="#fff" stroke="#000"/>\n')
        f.write('<text x="440" y="194" font-family="monospace" font-size="12">2  ->  Q2</text>\n')
        f.write('<text x="470" y="215" text-anchor="middle" font-family="sans-serif" font-size="14">...</text>\n')
        f.write('<rect x="420" y="230" width="100" height="20" fill="#fff" stroke="#000"/>\n')
        f.write('<text x="440" y="244" font-family="monospace" font-size="12">127 -> Q3</text>\n')
        
        f.write('<line x1="340" y1="190" x2="400" y2="190" stroke="#000" stroke-width="2" marker-end="url(#arrowBlack)"/>\n')
        f.write('<text x="370" y="180" text-anchor="middle" font-family="sans-serif" font-size="12">LSB 7 bits</text>\n')
        f.write('<text x="370" y="205" text-anchor="middle" font-family="sans-serif" font-size="12">Index</text>\n')
        
        # Queues & Cores
        f.write('<rect x="600" y="60" width="80" height="40" fill="#e2e3e5" stroke="#41464b"/>\n')
        f.write('<text x="640" y="85" text-anchor="middle" font-family="sans-serif" font-size="12">Rx Q0</text>\n')
        f.write('<rect x="690" y="60" width="80" height="40" fill="#ffddcc" stroke="#663300"/>\n')
        f.write('<text x="730" y="85" text-anchor="middle" font-family="sans-serif" font-size="12">Core 0</text>\n')
        
        f.write('<rect x="600" y="130" width="80" height="40" fill="#e2e3e5" stroke="#41464b"/>\n')
        f.write('<text x="640" y="155" text-anchor="middle" font-family="sans-serif" font-size="12">Rx Q1</text>\n')
        f.write('<rect x="690" y="130" width="80" height="40" fill="#ffddcc" stroke="#663300"/>\n')
        f.write('<text x="730" y="155" text-anchor="middle" font-family="sans-serif" font-size="12">Core 1</text>\n')
        
        f.write('<rect x="600" y="200" width="80" height="40" fill="#e2e3e5" stroke="#41464b"/>\n')
        f.write('<text x="640" y="225" text-anchor="middle" font-family="sans-serif" font-size="12">Rx Q2</text>\n')
        f.write('<rect x="690" y="200" width="80" height="40" fill="#ffddcc" stroke="#663300"/>\n')
        f.write('<text x="730" y="225" text-anchor="middle" font-family="sans-serif" font-size="12">Core 2</text>\n')
        
        f.write('<rect x="600" y="270" width="80" height="40" fill="#e2e3e5" stroke="#41464b"/>\n')
        f.write('<text x="640" y="295" text-anchor="middle" font-family="sans-serif" font-size="12">Rx Q3</text>\n')
        f.write('<rect x="690" y="270" width="80" height="40" fill="#ffddcc" stroke="#663300"/>\n')
        f.write('<text x="730" y="295" text-anchor="middle" font-family="sans-serif" font-size="12">Core 3</text>\n')
        
        f.write('<line x1="520" y1="150" x2="600" y2="80" stroke="#000" stroke-width="1" stroke-dasharray="4" marker-end="url(#arrowBlack)"/>\n')
        f.write('<line x1="520" y1="170" x2="600" y2="150" stroke="#000" stroke-width="1" stroke-dasharray="4" marker-end="url(#arrowBlack)"/>\n')
        f.write('<line x1="520" y1="190" x2="600" y2="220" stroke="#000" stroke-width="1" stroke-dasharray="4" marker-end="url(#arrowBlack)"/>\n')
        f.write('<line x1="520" y1="240" x2="600" y2="290" stroke="#000" stroke-width="1" stroke-dasharray="4" marker-end="url(#arrowBlack)"/>\n')
        
        f.write('<defs><marker id="arrowBlack" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#000" /></marker></defs>\n')
        f.write('</svg>\n')
        
if __name__ == '__main__':
    render()
