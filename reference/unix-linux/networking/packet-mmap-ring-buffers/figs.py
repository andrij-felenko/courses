import os

def render():
    out_dir = 'figs'
    os.makedirs(out_dir, exist_ok=True)

    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">
    <rect x="10" y="10" width="780" height="380" rx="10" ry="10" fill="#f9f9f9" stroke="#ccc"/>
    <rect x="30" y="50" width="340" height="320" rx="5" ry="5" fill="#e6f2ff" stroke="#99c2ff"/>
    <text x="150" y="40" font-size="16" font-family="Arial" font-weight="bold">Kernel Space</text>
    <rect x="70" y="100" width="260" height="60" rx="5" ry="5" fill="#cce0ff" stroke="#66a3ff"/>
    <text x="100" y="135" font-size="14" font-family="Arial">Network Interface Card (NIC)</text>
    <rect x="70" y="200" width="260" height="60" rx="5" ry="5" fill="#cce0ff" stroke="#66a3ff"/>
    <text x="110" y="235" font-size="14" font-family="Arial">AF_PACKET Socket Driver</text>
    <rect x="430" y="50" width="340" height="320" rx="5" ry="5" fill="#ffe6e6" stroke="#ff9999"/>
    <text x="560" y="40" font-size="16" font-family="Arial" font-weight="bold">User Space</text>
    <rect x="470" y="100" width="260" height="60" rx="5" ry="5" fill="#ffcccc" stroke="#ff6666"/>
    <text x="490" y="135" font-size="14" font-family="Arial">User Application (e.g., tcpdump)</text>
    <rect x="320" y="290" width="160" height="60" rx="5" ry="5" fill="#e6ffe6" stroke="#66cc66"/>
    <text x="340" y="315" font-size="14" font-family="Arial" font-weight="bold">Shared Memory</text>
    <text x="355" y="335" font-size="12" font-family="Arial">(Ring Buffer)</text>
    <line x1="200" y1="160" x2="200" y2="200" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="210" y="185" font-size="12" font-family="Arial">Interrupt / NAPI</text>
    <line x1="200" y1="260" x2="200" y2="320" stroke="black" stroke-width="2"/>
    <line x1="200" y1="320" x2="320" y2="320" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="220" y="310" font-size="12" font-family="Arial" font-style="italic">Direct Write</text>
    <line x1="480" y1="320" x2="600" y2="320" stroke="black" stroke-width="2"/>
    <line x1="600" y1="320" x2="600" y2="160" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="610" y="250" font-size="12" font-family="Arial" font-style="italic">Zero-copy Read</text>
    <line x1="600" y1="160" x2="600" y2="200" stroke="blue" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="610" y="190" font-size="12" font-family="Arial" fill="blue">mmap() mapping</text>
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="black"/>
        </marker>
    </defs>
</svg>"""

    with open(os.path.join(out_dir, 'packet_mmap_arch.svg'), 'w') as f:
        f.write(svg1)

    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300">
    <rect x="10" y="10" width="780" height="280" rx="5" ry="5" fill="#ffffff" stroke="#aaaaaa"/>
    <text x="20" y="30" font-size="18" font-family="Arial" font-weight="bold">TPACKET_V3 Block Structure</text>
    <rect x="40" y="60" width="120" height="160" rx="2" ry="2" fill="#fcfcff" stroke="#333333" stroke-width="1.5"/>
    <text x="55" y="80" font-size="14" font-family="monospace" font-weight="bold">block_desc</text>
    <line x1="40" y1="90" x2="160" y2="90" stroke="#333333" stroke-width="1"/>
    <text x="45" y="110" font-size="12" font-family="monospace">- block_status</text>
    <text x="45" y="130" font-size="12" font-family="monospace">- num_pkts</text>
    <text x="45" y="150" font-size="12" font-family="monospace">- offset_first</text>
    <rect x="180" y="60" width="180" height="160" rx="2" ry="2" fill="#fffaeb" stroke="#e6a800" stroke-width="1.5"/>
    <rect x="180" y="60" width="180" height="70" fill="#fffaeb" stroke="none"/>
    <text x="220" y="80" font-size="14" font-family="monospace" font-weight="bold">tpacket3_hdr</text>
    <text x="220" y="100" font-size="12" font-family="monospace">tp_next_offset</text>
    <text x="220" y="115" font-size="12" font-family="monospace">tp_snaplen</text>
    <rect x="180" y="130" width="180" height="90" fill="#ebf0e6" stroke="#5a803b" stroke-width="1.5"/>
    <text x="220" y="180" font-size="14" font-family="Arial" font-weight="bold">MAC Frame 1</text>
    <rect x="380" y="60" width="140" height="140" rx="2" ry="2" fill="#fffaeb" stroke="#e6a800" stroke-width="1.5"/>
    <text x="400" y="80" font-size="14" font-family="monospace" font-weight="bold">tpacket3_hdr</text>
    <rect x="380" y="120" width="140" height="80" fill="#ebf0e6" stroke="#5a803b" stroke-width="1.5"/>
    <text x="405" y="160" font-size="14" font-family="Arial" font-weight="bold">MAC Frame 2</text>
    <rect x="520" y="60" width="30" height="160" fill="#f0f0f0" stroke="#cccccc" stroke-dasharray="4,2"/>
    <text x="523" y="140" font-size="10" font-family="Arial" transform="rotate(-90 523 140)">Pad</text>
    <rect x="570" y="60" width="160" height="180" rx="2" ry="2" fill="#fffaeb" stroke="#e6a800" stroke-width="1.5"/>
    <text x="600" y="80" font-size="14" font-family="monospace" font-weight="bold">tpacket3_hdr</text>
    <text x="580" y="100" font-size="11" font-family="monospace">tp_next_offset=0</text>
    <rect x="570" y="130" width="160" height="110" fill="#ebf0e6" stroke="#5a803b" stroke-width="1.5"/>
    <text x="600" y="190" font-size="14" font-family="Arial" font-weight="bold">MAC Frame N</text>
    <path d="M 280 95 Q 330 40 380 95" fill="none" stroke="blue" stroke-width="1.5" marker-end="url(#arrow2)"/>
    <path d="M 470 95 Q 520 40 570 95" fill="none" stroke="blue" stroke-width="1.5" marker-end="url(#arrow2)"/>
    <defs>
        <marker id="arrow2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="blue"/>
        </marker>
    </defs>
</svg>"""

    with open(os.path.join(out_dir, 'tpacket_v3_block.svg'), 'w') as f:
        f.write(svg2)

if __name__ == '__main__':
    render()
