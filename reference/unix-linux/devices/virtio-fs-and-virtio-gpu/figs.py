import os
import sys

def render_virtio_fs(out_dir):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="#f0f0f0"/>
    <text x="400" y="300" font-family="sans-serif" font-size="24" text-anchor="middle">Virtio-FS Architecture</text>
    <rect x="100" y="100" width="250" height="400" fill="#cce5ff" stroke="#004085"/>
    <text x="225" y="140" font-family="sans-serif" font-size="18" text-anchor="middle">Guest OS</text>
    <rect x="450" y="100" width="250" height="400" fill="#d4edda" stroke="#155724"/>
    <text x="575" y="140" font-family="sans-serif" font-size="18" text-anchor="middle">Host OS</text>
    <path d="M 350 300 L 450 300" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="400" y="290" font-family="sans-serif" font-size="14" text-anchor="middle">DAX / Virtqueue</text>
</svg>"""
    with open(os.path.join(out_dir, "virtio_fs_arch.svg"), "w") as f:
        f.write(svg_content)

def render_virtio_gpu(out_dir):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="#f0f0f0"/>
    <text x="400" y="300" font-family="sans-serif" font-size="24" text-anchor="middle">Virtio-GPU Architecture</text>
    <rect x="100" y="100" width="250" height="400" fill="#fff3cd" stroke="#856404"/>
    <text x="225" y="140" font-family="sans-serif" font-size="18" text-anchor="middle">Guest (Mesa/VirGL)</text>
    <rect x="450" y="100" width="250" height="400" fill="#f8d7da" stroke="#721c24"/>
    <text x="575" y="140" font-family="sans-serif" font-size="18" text-anchor="middle">Host (virglrenderer)</text>
    <path d="M 350 300 L 450 300" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="400" y="290" font-family="sans-serif" font-size="14" text-anchor="middle">Virtqueue (Commands)</text>
</svg>"""
    with open(os.path.join(out_dir, "virtio_gpu_arch.svg"), "w") as f:
        f.write(svg_content)

def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    render_virtio_fs(out_dir)
    render_virtio_gpu(out_dir)

if __name__ == '__main__':
    render()
