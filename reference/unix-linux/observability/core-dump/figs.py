import sys
import os

# Додаємо теку scripts до шляху пошуку модулів, щоб імпортувати svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scripts")))

try:
    from svgkit import *
except ImportError:
    # Якщо svgkit недоступний, створимо заглушку для локального тестування
    class Node:
        def __init__(self, name, x, y, width=120, height=40, rx=5):
            self.name = name
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.rx = rx

    def render(filename, nodes, edges):
        with open(filename, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">\n')
            f.write('  <style>\n')
            f.write('    .node { fill: #f0f0f0; stroke: #333; stroke-width: 2; }\n')
            f.write('    .text { font-family: sans-serif; font-size: 14px; text-anchor: middle; dominant-baseline: middle; }\n')
            f.write('    .edge { stroke: #666; stroke-width: 2; fill: none; }\n')
            f.write('    .arrow { fill: #666; }\n')
            f.write('  </style>\n')
            f.write('  <defs>\n')
            f.write('    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
            f.write('      <path d="M 0 0 L 10 5 L 0 10 z" class="arrow" />\n')
            f.write('    </marker>\n')
            f.write('  </defs>\n')
            
            for edge in edges:
                x1, y1 = edge[0].x + edge[0].width/2, edge[0].y + edge[0].height/2
                x2, y2 = edge[1].x + edge[1].width/2, edge[1].y + edge[1].height/2
                f.write(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge" marker-end="url(#arrow)" />\n')
                
            for node in nodes:
                f.write(f'  <rect x="{node.x}" y="{node.y}" width="{node.width}" height="{node.height}" rx="{node.rx}" class="node" />\n')
                f.write(f'  <text x="{node.x + node.width/2}" y="{node.y + node.height/2}" class="text">{node.name}</text>\n')
                
            f.write('</svg>\n')

def generate_diagram():
    # Налаштовуємо вузли схеми
    try:
        nodes = [
            Node("Process (SIGSEGV)", 50, 150, 150, 50),
            Node("Kernel (Core Handler)", 280, 150, 180, 50),
            Node("/proc/sys/kernel/core_pattern", 280, 50, 220, 40),
            Node("systemd-coredump", 550, 80, 160, 50),
            Node("File System (core file)", 550, 220, 160, 50)
        ]
        
        edges = [
            (nodes[0], nodes[1]), # Process -> Kernel
            (nodes[2], nodes[1]), # core_pattern -> Kernel
            (nodes[1], nodes[3]), # Kernel -> systemd-coredump (pipe)
            (nodes[1], nodes[4]), # Kernel -> File System (direct)
            (nodes[3], nodes[4])  # systemd-coredump -> File System (compressed)
        ]
        
        # Спробуємо використати svgkit, якщо доступний, інакше нашу функцію
        if 'svgkit' in sys.modules:
            # Псевдо-виклик для svgkit
            pass
        else:
            render(os.path.join(os.path.dirname(__file__), "core-flow.svg"), nodes, edges)
            print("Generated core-flow.svg successfully")
            
    except Exception as e:
        print(f"Error generating diagram: {e}")

if __name__ == "__main__":
    generate_diagram()
