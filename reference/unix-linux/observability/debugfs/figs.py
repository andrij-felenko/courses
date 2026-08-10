import sys
import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#282a36"/>
    <text x="400" y="50" fill="#f8f8f2" font-family="sans-serif" font-size="24" text-anchor="middle">debugfs: /sys/kernel/debug</text>
    <rect x="50" y="100" width="200" height="250" rx="10" fill="#44475a"/>
    <text x="150" y="140" fill="#50fa7b" font-family="sans-serif" font-size="20" text-anchor="middle">procfs</text>
    <text x="150" y="180" fill="#f8f8f2" font-family="sans-serif" font-size="14" text-anchor="middle">Process info</text>
    <text x="150" y="210" fill="#f8f8f2" font-family="sans-serif" font-size="14" text-anchor="middle">Stable ABI</text>

    <rect x="300" y="100" width="200" height="250" rx="10" fill="#44475a"/>
    <text x="400" y="140" fill="#8be9fd" font-family="sans-serif" font-size="20" text-anchor="middle">sysfs</text>
    <text x="400" y="180" fill="#f8f8f2" font-family="sans-serif" font-size="14" text-anchor="middle">Device models</text>
    <text x="400" y="210" fill="#f8f8f2" font-family="sans-serif" font-size="14" text-anchor="middle">Strict rules</text>

    <rect x="550" y="100" width="200" height="250" rx="10" fill="#ff79c6"/>
    <text x="650" y="140" fill="#282a36" font-family="sans-serif" font-size="20" text-anchor="middle">debugfs</text>
    <text x="650" y="180" fill="#282a36" font-family="sans-serif" font-size="14" text-anchor="middle">Kernel debugging</text>
    <text x="650" y="210" fill="#282a36" font-family="sans-serif" font-size="14" text-anchor="middle">No ABI stability</text>
    <text x="650" y="240" fill="#282a36" font-family="sans-serif" font-size="14" text-anchor="middle">"Do whatever"</text>
</svg>"""
    with open("fig-debugfs-comparison.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
if __name__ == "__main__":
    render()
