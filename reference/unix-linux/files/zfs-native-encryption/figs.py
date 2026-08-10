import os
import textwrap

def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. ZFS Encryption Tree SVG
    enc_svg = textwrap.dedent("""\
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
      <defs>
        <style>
          .rect { fill: #2c3e50; stroke: #ecf0f1; stroke-width: 2; rx: 8; ry: 8; }
          .rect-enc { fill: #c0392b; stroke: #ecf0f1; stroke-width: 2; rx: 8; ry: 8; }
          .text { fill: #ecf0f1; font-family: 'Inter', sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; }
          .text-sub { fill: #bdc3c7; font-family: 'Inter', sans-serif; font-size: 11px; text-anchor: middle; }
          .line { stroke: #7f8c8d; stroke-width: 2; fill: none; }
          .label { fill: #7f8c8d; font-family: 'Inter', sans-serif; font-size: 12px; }
        </style>
      </defs>
      
      <!-- Nodes -->
      <rect class="rect" x="300" y="30" width="200" height="50"/>
      <text class="text" x="400" y="55">pool (unencrypted)</text>
      
      <rect class="rect-enc" x="150" y="130" width="200" height="60"/>
      <text class="text" x="250" y="155">pool/data</text>
      <text class="text-sub" x="250" y="175">Encryption Root (Key A)</text>
      
      <rect class="rect-enc" x="50" y="250" width="180" height="60"/>
      <text class="text" x="140" y="275">pool/data/home</text>
      <text class="text-sub" x="140" y="295">Inherits Key A</text>
      
      <rect class="rect-enc" x="270" y="250" width="180" height="60"/>
      <text class="text" x="360" y="275">pool/data/secret</text>
      <text class="text-sub" x="360" y="295">Encryption Root (Key B)</text>
      
      <rect class="rect" x="450" y="130" width="200" height="50"/>
      <text class="text" x="550" y="160">pool/public (unencrypted)</text>
      
      <!-- Edges -->
      <path class="line" d="M 400 80 L 250 130"/>
      <path class="line" d="M 400 80 L 550 130"/>
      <path class="line" d="M 250 190 L 140 250"/>
      <path class="line" d="M 250 190 L 360 250"/>
      
    </svg>
    """)
    
    # 2. DDT Structure SVG
    ddt_svg = textwrap.dedent("""\
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
      <defs>
        <style>
          .bg { fill: #1e1e1e; }
          .box { fill: #2980b9; stroke: #fff; stroke-width: 1.5; rx: 5; }
          .box-ddt { fill: #8e44ad; stroke: #fff; stroke-width: 1.5; rx: 5; }
          .box-disk { fill: #27ae60; stroke: #fff; stroke-width: 1.5; rx: 5; }
          .txt { fill: #fff; font-family: monospace; font-size: 13px; text-anchor: middle; }
          .txt-small { fill: #ddd; font-family: monospace; font-size: 10px; text-anchor: middle; }
          .line { stroke: #fff; stroke-width: 2; marker-end: url(#arrow); }
          .line-dashed { stroke: #95a5a6; stroke-width: 1.5; stroke-dasharray: 5,5; marker-end: url(#arrow); }
        </style>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#fff" />
        </marker>
      </defs>
      
      <rect class="bg" width="800" height="450"/>
      
      <!-- ARC / RAM -->
      <rect fill="none" stroke="#f39c12" stroke-dasharray="8,4" x="50" y="20" width="700" height="150" rx="10"/>
      <text fill="#f39c12" font-family="sans-serif" font-size="16" x="65" y="45">RAM (ARC)</text>
      
      <rect class="box-ddt" x="300" y="60" width="200" height="90"/>
      <text class="txt" x="400" y="80">Deduplication Table (DDT)</text>
      <text class="txt-small" x="400" y="100">Checksum (SHA256) | RefCount | DVA</text>
      <text class="txt-small" x="400" y="120">0xABCD...1234 : Ref=2 -> DVA1</text>
      <text class="txt-small" x="400" y="135">0x99FF...0011 : Ref=1 -> DVA2</text>
      
      <!-- Storage / Disk -->
      <rect fill="none" stroke="#27ae60" stroke-dasharray="8,4" x="50" y="220" width="700" height="200" rx="10"/>
      <text fill="#27ae60" font-family="sans-serif" font-size="16" x="65" y="245">Physical Storage (Zpool)</text>
      
      <rect class="box" x="100" y="280" width="120" height="50"/>
      <text class="txt" x="160" y="305">File A (Block 1)</text>
      <text class="txt-small" x="160" y="320">Refers to 0xABCD...</text>
      
      <rect class="box" x="580" y="280" width="120" height="50"/>
      <text class="txt" x="640" y="305">File B (Block 3)</text>
      <text class="txt-small" x="640" y="320">Refers to 0xABCD...</text>
      
      <rect class="box-disk" x="340" y="350" width="120" height="50"/>
      <text class="txt" x="400" y="375">Data Block on Disk</text>
      <text class="txt-small" x="400" y="390">DVA1</text>
      
      <!-- Arrows -->
      <path class="line-dashed" d="M 160 280 L 350 150"/>
      <path class="line-dashed" d="M 640 280 L 450 150"/>
      <path class="line" d="M 400 150 L 400 350"/>
      
    </svg>
    """)
    
    with open(os.path.join(out_dir, "zfs_encryption_tree.svg"), "w", encoding="utf-8") as f:
        f.write(enc_svg)
        
    with open(os.path.join(out_dir, "zfs_ddt_structure.svg"), "w", encoding="utf-8") as f:
        f.write(ddt_svg)

if __name__ == "__main__":
    render()
