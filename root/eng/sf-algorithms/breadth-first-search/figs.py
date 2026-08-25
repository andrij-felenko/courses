# -*- coding: utf-8 -*-
import sys
import os

# Four directory levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def draw_bfs_frontier():
    """
    Figure 1: bfs-frontier.svg
    Illustrates BFS wave expansion (levels L0, L1, L2) and the FIFO queue status.
    """
    w, h = 760, 360
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    # Defs for markers
    out.append('''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>
      </marker>
    </defs>''')

    # Title / Level headers
    out.append(text(380, 25, "Шар під шаром: поширення хвилі BFS та стан черги FIFO", size=15, bold=True))

    # Level background bands
    # L0
    out.append(rect(40, 50, 140, 180, fill="#eef6ff", stroke="#93c5fd", sw=1, rx=8))
    out.append(text(110, 70, "L0 (Старт)", size=12, color="#1e40af", bold=True))

    # L1
    out.append(rect(210, 50, 200, 180, fill="#f0fdf4", stroke="#86efac", sw=1, rx=8))
    out.append(text(310, 70, "L1 (Відстань = 1)", size=12, color="#166534", bold=True))

    # L2
    out.append(rect(440, 50, 270, 180, fill="#fff7ed", stroke="#fdba74", sw=1, rx=8))
    out.append(text(575, 70, "L2 (Відстань = 2)", size=12, color="#9a3412", bold=True))

    # Edges
    # S -> A, S -> B
    out.append(line(110, 130, 290, 100, color=LINE, sw=2))
    out.append(line(110, 130, 290, 165, color=LINE, sw=2))

    # A -> C, A -> D
    out.append(line(290, 100, 500, 90, color=LINE, sw=2))
    out.append(line(290, 100, 500, 140, color=LINE, sw=2))

    # B -> D, B -> E
    out.append(line(290, 165, 500, 140, color=LINE, sw=2))
    out.append(line(290, 165, 630, 180, color=LINE, sw=2))

    # Nodes
    # S (Processed / Black/Dark Blue)
    out.append(circle(110, 130, 22, fill="#1e293b", stroke="#0f172a", sw=2))
    out.append(text(110, 135, "S", size=13, color="#ffffff", bold=True))

    # A (Processed / Dark Blue)
    out.append(circle(290, 100, 22, fill="#1e293b", stroke="#0f172a", sw=2))
    out.append(text(290, 105, "A", size=13, color="#ffffff", bold=True))

    # B (Processed / Dark Blue)
    out.append(circle(290, 165, 22, fill="#1e293b", stroke="#0f172a", sw=2))
    out.append(text(290, 170, "B", size=13, color="#ffffff", bold=True))

    # C (Active in Queue / Orange)
    out.append(circle(500, 90, 22, fill="#ea580c", stroke="#c2410c", sw=2))
    out.append(text(500, 95, "C", size=13, color="#ffffff", bold=True))

    # D (Active in Queue / Orange)
    out.append(circle(500, 140, 22, fill="#ea580c", stroke="#c2410c", sw=2))
    out.append(text(500, 145, "D", size=13, color="#ffffff", bold=True))

    # E (Active in Queue / Orange)
    out.append(circle(630, 180, 22, fill="#ea580c", stroke="#c2410c", sw=2))
    out.append(text(630, 185, "E", size=13, color="#ffffff", bold=True))

    # Queue visualization box at bottom
    out.append(rect(80, 255, 600, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(380, 275, "Стан черги FIFO в момент обробки L1:", size=12, color=MUTED, bold=True))

    # Queue slots
    # Head / Front arrow
    out.append(text(125, 310, "ГОЛОВА ➔", size=11, color=POS, bold=True))

    # Queue cells: C, D, E
    out.append(rect(200, 290, 80, 32, fill="#ea580c", stroke="#c2410c", sw=1.5, rx=4))
    out.append(text(240, 311, "C (L2)", size=12, color="#ffffff", bold=True))

    out.append(rect(290, 290, 80, 32, fill="#ea580c", stroke="#c2410c", sw=1.5, rx=4))
    out.append(text(330, 311, "D (L2)", size=12, color="#ffffff", bold=True))

    out.append(rect(380, 290, 80, 32, fill="#ea580c", stroke="#c2410c", sw=1.5, rx=4))
    out.append(text(420, 311, "E (L2)", size=12, color="#ffffff", bold=True))

    # Empty tail slots
    out.append(rect(470, 290, 70, 32, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    out.append(text(505, 311, "вільно", size=11, color=MUTED))

    out.append(text(595, 310, "🠔 ХВІСТ (push)", size=11, color=NEG, bold=True))

    out.append('</svg>')
    path = os.path.join(OUT_DIR, "bfs-frontier.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def draw_bfs_shortest_path():
    """
    Figure 2: bfs-shortest-path.svg
    Demonstrates unweighted shortest path level distances.
    """
    w, h = 760, 350
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(380, 22, "Дерево найкоротших шляхів у незваженому графі", size=15, bold=True))

    # Nodes coordinates:
    # S (90, 180)
    # A (250, 100), B (250, 260)
    # C (430, 70), D (430, 180), E (430, 270)
    # F (610, 180)

    # Edges - Shortest Path Tree Edges (Green/Bold)
    out.append(line(90, 180, 250, 100, color=FIELD, sw=3))
    out.append(line(90, 180, 250, 260, color=FIELD, sw=3))

    out.append(line(250, 100, 430, 70, color=FIELD, sw=3))
    out.append(line(250, 100, 430, 180, color=FIELD, sw=3))

    out.append(line(250, 260, 430, 270, color=FIELD, sw=3))

    out.append(line(430, 180, 610, 180, color=FIELD, sw=3))

    # Cross / Non-tree Edges (Dashed Gray)
    out.append(line(250, 260, 430, 180, color=MUTED, sw=1.5, dash="4,4"))
    out.append(line(430, 70, 430, 180, color=MUTED, sw=1.5, dash="4,4"))
    out.append(line(430, 270, 610, 180, color=MUTED, sw=1.5, dash="4,4"))

    # Nodes with d[v] labels
    # S
    out.append(circle(90, 180, 24, fill="#2563eb", stroke="#1d4ed8", sw=2))
    out.append(text(90, 184, "S", size=13, color="#ffffff", bold=True))
    out.append(text(90, 218, "d = 0", size=11, color="#1d4ed8", bold=True))

    # A
    out.append(circle(250, 100, 22, fill="#059669", stroke="#047857", sw=2))
    out.append(text(250, 104, "A", size=13, color="#ffffff", bold=True))
    out.append(text(250, 66, "d = 1", size=11, color="#047857", bold=True))

    # B
    out.append(circle(250, 260, 22, fill="#059669", stroke="#047857", sw=2))
    out.append(text(250, 264, "B", size=13, color="#ffffff", bold=True))
    out.append(text(250, 296, "d = 1", size=11, color="#047857", bold=True))

    # C
    out.append(circle(430, 70, 22, fill="#d97706", stroke="#b45309", sw=2))
    out.append(text(430, 74, "C", size=13, color="#ffffff", bold=True))
    out.append(text(380, 74, "d = 2", size=11, color="#b45309", bold=True, anchor="end"))

    # D
    out.append(circle(430, 180, 22, fill="#d97706", stroke="#b45309", sw=2))
    out.append(text(430, 184, "D", size=13, color="#ffffff", bold=True))
    out.append(text(430, 214, "d = 2", size=11, color="#b45309", bold=True))

    # E
    out.append(circle(430, 270, 22, fill="#d97706", stroke="#b45309", sw=2))
    out.append(text(430, 274, "E", size=13, color="#ffffff", bold=True))
    out.append(text(430, 304, "d = 2", size=11, color="#b45309", bold=True))

    # F
    out.append(circle(610, 180, 22, fill="#7c3aed", stroke="#6d28d9", sw=2))
    out.append(text(610, 184, "F", size=13, color="#ffffff", bold=True))
    out.append(text(610, 214, "d = 3", size=11, color="#6d28d9", bold=True))

    # Legend
    out.append(rect(510, 45, 230, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    out.append(line(525, 60, 555, 60, color=FIELD, sw=3))
    out.append(text(640, 64, "Деревне ребро", size=10, anchor="middle"))
    out.append(line(525, 85, 555, 85, color=MUTED, sw=1.5, dash="4,4"))
    out.append(text(640, 89, "Поперечне ребро", size=10, anchor="middle"))

    out.append('</svg>')
    path = os.path.join(OUT_DIR, "bfs-shortest-path.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def draw_bfs_tree():
    """
    Figure 3: bfs-tree.svg
    Shows structural properties of BFS tree edges vs cross edges between levels.
    """
    w, h = 760, 320
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(380, 25, "Класифікація ребер та обмеження різниці рівнів |L(u) - L(v)| ≤ 1", size=15, bold=True))

    # Level separators (Horizontal dashed lines)
    out.append(line(60, 90, 700, 90, color="#cbd5e1", sw=1, dash="5,5"))
    out.append(text(100, 82, "Рівень i (L_i)", size=11, color=MUTED, bold=True))

    out.append(line(60, 220, 700, 220, color="#cbd5e1", sw=1, dash="5,5"))
    out.append(text(100, 212, "Рівень i + 1 (L_{i+1})", size=11, color=MUTED, bold=True))

    # Nodes on Level i
    out.append(circle(220, 60, 20, fill="#2563eb", stroke="#1d4ed8", sw=2))
    out.append(text(220, 64, "u1", size=12, color="#ffffff", bold=True))

    out.append(circle(450, 60, 20, fill="#2563eb", stroke="#1d4ed8", sw=2))
    out.append(text(450, 64, "u2", size=12, color="#ffffff", bold=True))

    # Intra-level edge (Cross edge within same level)
    out.append(line(240, 60, 430, 60, color=POS, sw=2, dash="4,4"))
    out.append(text(335, 50, "Поперечне ребро (ΔL = 0)", size=11, color=POS, bold=True))

    # Nodes on Level i+1
    out.append(circle(160, 250, 20, fill="#059669", stroke="#047857", sw=2))
    out.append(text(160, 254, "v1", size=12, color="#ffffff", bold=True))

    out.append(circle(330, 250, 20, fill="#059669", stroke="#047857", sw=2))
    out.append(text(330, 254, "v2", size=12, color="#ffffff", bold=True))

    out.append(circle(540, 250, 20, fill="#059669", stroke="#047857", sw=2))
    out.append(text(540, 254, "v3", size=12, color="#ffffff", bold=True))

    # Tree edges
    out.append(line(220, 60, 160, 250, color=FIELD, sw=3))
    out.append(line(220, 60, 330, 250, color=FIELD, sw=3))
    out.append(line(450, 60, 540, 250, color=FIELD, sw=3))

    # Cross edge between adjacent levels
    out.append(line(450, 60, 330, 250, color=POS, sw=2, dash="4,4"))

    # Labels for edge types
    out.append(text(170, 150, "Деревне ребро (ΔL = 1)", size=11, color=FIELD, bold=True))

    # Impossible edge note
    out.append(rect(580, 130, 150, 70, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=6))
    out.append(text(655, 153, "Неможливо:", size=11, color=POS, bold=True))
    out.append(text(655, 175, "Ребро L_i ➔ L_{i+2}", size=11, color=POS, bold=True))

    out.append('</svg>')
    path = os.path.join(OUT_DIR, "bfs-tree.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    draw_bfs_frontier()
    draw_bfs_shortest_path()
    draw_bfs_tree()
    print("Generated 3 SVG figures for BFS.")
