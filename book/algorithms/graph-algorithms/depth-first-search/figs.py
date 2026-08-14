# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ──────────────────────────────────────────────────────────
COLOR_NODE_WHITE = "#ffffff"  # Білий (не відвідано)
COLOR_NODE_GRAY  = "#fef3c7"  # Сірий / жовтий (у процесі / на стеку)
COLOR_NODE_BLACK = "#eaf7ee"  # Чорний / зелений (завершено)
COLOR_NODE_ERR   = "#fee2e2"  # Червоний (цикл)

BORDER_WHITE = "#64748b"
BORDER_GRAY  = "#d97706"
BORDER_BLACK = "#27ae60"
BORDER_ERR   = "#dc2626"

LINE_MUTED    = "#94a3b8"
LINE_TREE     = "#16a34a"  # Зелений — ребро дерева
LINE_BACK     = "#dc2626"  # Червоний — зворотне ребро (цикл)
LINE_FORWARD  = "#2563eb"  # Синій — пряме ребро
LINE_CROSS    = "#9333ea"  # Фіолетовий — перехресне ребро

def node(cx, cy, label, fill=COLOR_NODE_WHITE, stroke=BORDER_WHITE, r=22, timestamps=None):
    """Створює вузол графа з підписом усередині та часовими мітками d/f під ним."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, label, size=15, color=INK, bold=True)
    if timestamps:
        out += text(cx, cy + r + 15, timestamps, size=11, color=MUTED, bold=True)
    return out

def edge_arrow(x1, y1, x2, y2, r1=22, r2=22, col=BORDER_WHITE, sw=1.8, label=None, curve=0):
    """Малює орієнтоване ребро (зі стрілкою) з можливістю дуги (curve != 0)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    
    if curve == 0:
        ax, ay = x1 + ux * r1, y1 + uy * r1
        bx, by = x2 - ux * r2, y2 - uy * r2
        out = arrow(ax, ay, bx, by, color=col, sw=sw)
        if label:
            mx, my = (ax + bx) / 2, (ay + by) / 2
            nx, ny = -uy * 12, ux * 12
            out += circle(mx + nx, my + ny, 9, fill=BG, stroke="none", sw=0)
            out += text(mx + nx, my + ny + 4, str(label), size=11, color=col, bold=True)
    else:
        # Зігнуте ребро через контрольну точку
        nx, ny = -uy * curve, ux * curve
        mx, my = (x1 + x2) / 2 + nx, (y1 + y2) / 2 + ny
        
        # Точки на колах
        d1x, d1y = mx - x1, my - y1
        L1 = math.hypot(d1x, d1y) or 1.0
        ax, ay = x1 + (d1x / L1) * r1, y1 + (d1y / L1) * r1
        
        d2x, d2y = x2 - mx, y2 - my
        L2 = math.hypot(d2x, d2y) or 1.0
        bx, by = x2 - (d2x / L2) * r2, y2 - (d2y / L2) * r2
        
        out = f'<path d="M {ax:.1f} {ay:.1f} Q {mx:.1f} {my:.1f} {bx:.1f} {by:.1f}" fill="none" stroke="{col}" stroke-width="{sw:.1f}" />'
        
        # Стрілка на кінці
        angle = math.atan2(by - my, bx - mx)
        al1_x = bx - 8 * math.cos(angle - 0.4)
        al1_y = by - 8 * math.sin(angle - 0.4)
        al2_x = bx - 8 * math.cos(angle + 0.4)
        al2_y = by - 8 * math.sin(angle + 0.4)
        out += f'<polygon points="{bx:.1f},{by:.1f} {al1_x:.1f},{al1_y:.1f} {al2_x:.1f},{al2_y:.1f}" fill="{col}" />'
        
        if label:
            lx, ly = mx + nx * 0.3, my + ny * 0.3
            out += circle(lx, ly, 9, fill=BG, stroke="none", sw=0)
            out += text(lx, ly + 4, str(label), size=11, color=col, bold=True)
            
    return out

# ── ФІГ.1 Обхід DFS: три кольори вершин та часові мітки d/f ────────────────────
def fig_dfs_traversal():
    path = os.path.join(OUT, "dfs-traversal.svg")
    W, H = 760, 320
    p = []
    
    p.append(text(210, 25, "Стан вершин під час обходу DFS", size=14, color=INK, bold=True))
    
    # 5 вершин у розгалуженому графі
    coords = {
        "A": (70, 110, COLOR_NODE_BLACK, BORDER_BLACK, "1/10"),
        "B": (190, 70, COLOR_NODE_BLACK, BORDER_BLACK, "2/7"),
        "C": (190, 175, COLOR_NODE_GRAY, BORDER_GRAY, "8/•"),
        "D": (310, 70, COLOR_NODE_BLACK, BORDER_BLACK, "3/6"),
        "E": (310, 175, COLOR_NODE_WHITE, BORDER_WHITE, "•/•")
    }
    
    edges = [
        ("A", "B", LINE_TREE, 0),
        ("A", "C", LINE_TREE, 0),
        ("B", "D", LINE_TREE, 0),
        ("C", "E", LINE_MUTED, 0),
        ("D", "B", LINE_BACK, 30)  # зворотне ребро для прикладу
    ]
    
    for u, v, col, cur in edges:
        x1, y1, _, _, _ = coords[u]
        x2, y2, _, _, _ = coords[v]
        p.append(edge_arrow(x1, y1, x2, y2, col=col, sw=2.0, curve=cur))
        
    for name, (cx, cy, fill, stroke, ts) in coords.items():
        p.append(node(cx, cy, name, fill=fill, stroke=stroke, timestamps=ts))
        
    # Права частина: Стек викликів рекурсії
    p.append(text(580, 25, "Стек активних викликів (Call Stack)", size=14, color=INK, bold=True))
    
    # Контейнер для стеку
    p.append(rect(460, 50, 240, 170, fill=FILL, stroke=BORDER_WHITE, rx=6))
    
    # Елементи стеку (зверху донизу: C -> A)
    stack_items = [
        ("dfs(C)", "d=8, активна (GRAY)", COLOR_NODE_GRAY, BORDER_GRAY),
        ("dfs(A)", "d=1, очікує C (GRAY)", COLOR_NODE_GRAY, BORDER_GRAY)
    ]
    
    for i, (fn, desc, f_col, s_col) in enumerate(stack_items):
        sy = 70 + i * 55
        p.append(rect(475, sy, 210, 45, fill=f_col, stroke=s_col, rx=4))
        p.append(text(580, sy + 20, fn, size=13, color=INK, bold=True))
        p.append(text(580, sy + 36, desc, size=10, color=MUTED))
        
    p.append(text(580, 235, "Вершина D завершена (f=6) і знята зі стеку", size=11, color=BORDER_BLACK, bold=True))
    
    # Картка пояснення
    b, bw, bh = textbox(W / 2, 280,
                        "Мітка d[u]/f[u] показує час відкриття (входу на стек) та завершення (виходу зі стеку).\n"
                        "Вершина C у стані GRAY: d[C]=8, її піддерево обробляється прямо зараз.",
                        size=12, pad=10, fill=FILL, stroke=BORDER_WHITE)
    p.append(b)
    
    return render(path, W, H, *p)

# ── ФІГ.2 Класифікація ребер: Tree, Back, Forward, Cross ───────────────────────
def fig_dfs_tree_edges():
    path = os.path.join(OUT, "dfs-tree-edges.svg")
    W, H = 760, 320
    p = []
    
    p.append(text(W / 2, 25, "Класифікація ребер під час обходу DFS", size=14, color=INK, bold=True))
    
    # Координати 5 вершин
    coords = {
        "A": (150, 70, "1/10"),
        "B": (90, 160, "2/5"),
        "C": (210, 160, "6/9"),
        "D": (90, 250, "3/4"),
        "E": (210, 250, "7/8")
    }
    
    # Малювання ребер різних типів
    # Tree Edges (A->B, B->D, A->C, C->E)
    p.append(edge_arrow(150, 70, 90, 160, col=LINE_TREE, sw=2.2, label="Tree"))
    p.append(edge_arrow(90, 160, 90, 250, col=LINE_TREE, sw=2.2, label="Tree"))
    p.append(edge_arrow(150, 70, 210, 160, col=LINE_TREE, sw=2.2, label="Tree"))
    p.append(edge_arrow(210, 160, 210, 250, col=LINE_TREE, sw=2.2, label="Tree"))
    
    # Back Edge (D -> A) — дуга назад до предка
    p.append(edge_arrow(90, 250, 150, 70, col=LINE_BACK, sw=2.2, label="Back", curve=-45))
    
    # Forward Edge (A -> E) — дуга вперед до нащадка
    p.append(edge_arrow(150, 70, 210, 250, col=LINE_FORWARD, sw=2.2, label="Forward", curve=45))
    
    # Cross Edge (C -> B) — ребро між гілками
    p.append(edge_arrow(210, 160, 90, 160, col=LINE_CROSS, sw=2.2, label="Cross"))
    
    for name, (cx, cy, ts) in coords.items():
        p.append(node(cx, cy, name, fill=COLOR_NODE_BLACK, stroke=BORDER_BLACK, timestamps=ts))
        
    # Права частина: Легенда та правила
    legend_items = [
        ("Ребро дерева (Tree Edge)", "Веде до білої (WHITE) вершини", LINE_TREE),
        ("Зворотне ребро (Back Edge)", "Веде до сірої (GRAY) предка → ЦИКЛ!", LINE_BACK),
        ("Пряме ребро (Forward Edge)", "Веде до чорного нащадка (d[u] < d[v])", LINE_FORWARD),
        ("Перехресне ребро (Cross Edge)", "Веде до чорного чужого (d[u] > d[v])", LINE_CROSS)
    ]
    
    p.append(rect(360, 50, 370, 240, fill=FILL, stroke=BORDER_WHITE, rx=6))
    p.append(text(545, 72, "Правила визначення за кольором та мітками", size=13, color=INK, bold=True))
    
    for i, (title, rule, col) in enumerate(legend_items):
        ly = 100 + i * 46
        p.append(rect(380, ly - 8, 14, 14, fill=col, stroke="none", rx=2))
        p.append(text(402, ly, title, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(402, ly + 15, rule, size=11, color=MUTED, anchor="start"))
        
    return render(path, W, H, *p)

# ── ФІГ.3 Теорема про дужкову структуру часових інтервалів ─────────────────────
def fig_parenthesis_theorem():
    path = os.path.join(OUT, "parenthesis-theorem.svg")
    W, H = 760, 290
    p = []
    
    p.append(text(W / 2, 25, "Теорема про дужкову структуру інтервалів [d[u], f[u]]", size=14, color=INK, bold=True))
    
    # 1. Вкладені дужки (Предки та нащадки)
    p.append(text(200, 60, "Вкладені інтервали (Предок → Нащадок)", size=13, color=INK, bold=True))
    
    # Відрізок A: [1, 10]
    p.append(line(50, 90, 350, 90, color=LINE_TREE, sw=3))
    p.append(circle(50, 90, 4, fill=LINE_TREE, stroke="none"))
    p.append(circle(350, 90, 4, fill=LINE_TREE, stroke="none"))
    p.append(text(40, 94, "(A", size=13, color=LINE_TREE, bold=True))
    p.append(text(360, 94, ")A", size=13, color=LINE_TREE, bold=True))
    p.append(text(200, 80, "Інтервал A: [1, 10]", size=11, color=INK, bold=True))
    
    # Вкладений відрізок B: [2, 7]
    p.append(line(80, 125, 250, 125, color=BORDER_GRAY, sw=3))
    p.append(circle(80, 125, 4, fill=BORDER_GRAY, stroke="none"))
    p.append(circle(250, 125, 4, fill=BORDER_GRAY, stroke="none"))
    p.append(text(70, 129, "(B", size=13, color=BORDER_GRAY, bold=True))
    p.append(text(260, 129, ")B", size=13, color=BORDER_GRAY, bold=True))
    p.append(text(165, 115, "Інтервал B: [2, 7]", size=11, color=INK, bold=True))
    
    # Вкладений у B відрізок D: [3, 6]
    p.append(line(110, 160, 220, 160, color=BORDER_BLACK, sw=3))
    p.append(circle(110, 160, 4, fill=BORDER_BLACK, stroke="none"))
    p.append(circle(220, 160, 4, fill=BORDER_BLACK, stroke="none"))
    p.append(text(100, 164, "(D", size=13, color=BORDER_BLACK, bold=True))
    p.append(text(230, 164, ")D", size=13, color=BORDER_BLACK, bold=True))
    p.append(text(165, 150, "D: [3, 6]", size=10, color=INK, bold=True))
    
    # 2. Неперетинні дужки (Незалежні гілки)
    p.append(text(560, 60, "Неперетинні інтервали (Різні гілки)", size=13, color=INK, bold=True))
    
    # Відрізок B: [2, 7]
    p.append(line(420, 90, 560, 90, color=BORDER_GRAY, sw=3))
    p.append(circle(420, 90, 4, fill=BORDER_GRAY, stroke="none"))
    p.append(circle(560, 90, 4, fill=BORDER_GRAY, stroke="none"))
    p.append(text(410, 94, "(B", size=13, color=BORDER_GRAY, bold=True))
    p.append(text(570, 94, ")B", size=13, color=BORDER_GRAY, bold=True))
    p.append(text(490, 80, "B: [2, 7]", size=11, color=INK, bold=True))
    
    # Відрізок C: [8, 9]
    p.append(line(590, 90, 710, 90, color=LINE_CROSS, sw=3))
    p.append(circle(590, 90, 4, fill=LINE_CROSS, stroke="none"))
    p.append(circle(710, 90, 4, fill=LINE_CROSS, stroke="none"))
    p.append(text(580, 94, "(C", size=13, color=LINE_CROSS, bold=True))
    p.append(text(720, 94, ")C", size=13, color=LINE_CROSS, bold=True))
    p.append(text(650, 80, "C: [8, 9]", size=11, color=INK, bold=True))
    
    # Картка висновку
    b, bw, bh = textbox(W / 2, 230,
                        "Строге правило: для будь-якої пари вершин u та v їхні часові інтервали [d[u], f[u]] та [d[v], f[v]]\n"
                        "або повністю вкладені один в одного (u — предок v у дереві DFS), або зовсім не перетинаються.\n"
                        "Частковий перетин вигляду d[u] < d[v] < f[u] < f[v] МАТЕМАТИЧНО НЕМОЖЛИВИЙ.",
                        size=12, pad=12, fill=FILL, stroke=BORDER_WHITE)
    p.append(b)
    
    return render(path, W, H, *p)

if __name__ == "__main__":
    fig_dfs_traversal()
    fig_dfs_tree_edges()
    fig_parenthesis_theorem()
    print("SVG figures successfully generated in %s" % OUT)
