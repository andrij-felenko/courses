# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ──────────────────────────────────────────────────────────
COLOR_NODE_BG   = "#f4f6f8"
COLOR_NODE_DONE = "#eaf7ee"   # Зелений (оброблено / BLACK)
COLOR_NODE_ACTIVE = "#fef3c7" # Жовтий / помаранчевий (у процесі / GRAY / в черзі)
COLOR_NODE_ERR  = "#fee2e2"   # Червоний (конфлікт / цикл)

BORDER_NORMAL = "#333333"
BORDER_DONE   = "#27ae60"
BORDER_ACTIVE = "#d97706"
BORDER_ERR    = "#dc2626"

LINE_MUTED    = "#94a3b8"

def node(cx, cy, label, fill=COLOR_NODE_BG, stroke=BORDER_NORMAL, r=22, extra_sub=None):
    """Створює вузол графа круглої форми з підписом усередині та опціональним підписом знизу."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, label, size=15, color=INK, bold=True)
    if extra_sub:
        out += text(cx, cy + r + 15, extra_sub, size=11, color=MUTED, bold=True)
    return out

def edge_arrow(x1, y1, x2, y2, r1=22, r2=22, col=BORDER_NORMAL, sw=1.8, label=None):
    """Малює орієнтоване ребро (дугу зі стрілкою) між двома вузлами із урахуванням їхніх радіусів."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    
    out = arrow(ax, ay, bx, by, color=col, sw=sw)
    if label:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        nx, ny = -uy * 12, ux * 12
        out += circle(mx + nx, my + ny, 9, fill=BG, stroke="none", sw=0)
        out += text(mx + nx, my + ny + 4, str(label), size=11, color=INK, bold=True)
    return out

# ── ФІГ.1 DAG Концепція та лінійне топологічне впорядкування ──────────────────
def fig_dag_concept():
    path = os.path.join(OUT, "dag-concept.svg")
    W, H = 760, 320
    p = []
    
    # Заголовок лівого блоку
    p.append(text(200, 30, "Орієнтований безциклічний граф (DAG)", size=15, color=INK, bold=True))
    
    # Координати 6 вершин у DAG
    coords = {
        "A": (70, 100),
        "B": (190, 70),
        "C": (190, 160),
        "D": (310, 70),
        "E": (310, 160),
        "F": (420, 115)
    }
    
    edges = [
        ("A", "B"), ("A", "C"),
        ("B", "D"), ("C", "D"), ("C", "E"),
        ("D", "F"), ("E", "F")
    ]
    
    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        p.append(edge_arrow(x1, y1, x2, y2, col=BORDER_NORMAL, sw=2.0))
        
    for name, (cx, cy) in coords.items():
        p.append(node(cx, cy, name, fill=COLOR_NODE_BG, stroke=BORDER_NORMAL))
        
    # Права частина: Лінійний топологічний порядок
    p.append(text(600, 30, "Валідний топологічний порядок", size=15, color=INK, bold=True))
    
    order = ["A", "B", "C", "D", "E", "F"]
    ox_start = 490
    oy = 115
    dx = 42
    
    for i, elem in enumerate(order):
        cx = ox_start + i * dx
        p.append(rect(cx - 16, oy - 16, 32, 32, fill=COLOR_NODE_DONE, stroke=BORDER_DONE, rx=4))
        p.append(text(cx, oy + 5, elem, size=14, color=INK, bold=True))
        if i < len(order) - 1:
            p.append(line(cx + 16, oy, cx + dx - 16, oy, color=BORDER_DONE, sw=1.5))
            
    # Нижня пояснювальна картка
    b, bw, bh = textbox(W / 2, 255,
                        "Усі ребра графа спрямовані ЗЛІВА НАПРАВО в топологічному порядку.\n"
                        "Кожна залежність u → v задовольняється: u стоїть у списку раніше за v.",
                        size=13, pad=12, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    return render(path, W, H, *p)

# ── ФІГ.2 Конфлікт циклу: чому топологічне сортування неможливе ───────────────
def fig_cycle_conflict():
    path = os.path.join(OUT, "cycle-conflict.svg")
    W, H = 740, 290
    p = []
    
    # Координати 4 вершин з циклом A -> B -> C -> A та ребро C -> D
    coords = {
        "A": (120, 80),
        "B": (280, 80),
        "C": (200, 190),
        "D": (400, 190)
    }
    
    # Ребра циклу (підкреслені червоним)
    p.append(edge_arrow(coords["A"][0], coords["A"][1], coords["B"][0], coords["B"][1], col=BORDER_ERR, sw=2.4))
    p.append(edge_arrow(coords["B"][0], coords["B"][1], coords["C"][0], coords["C"][1], col=BORDER_ERR, sw=2.4))
    p.append(edge_arrow(coords["C"][0], coords["C"][1], coords["A"][0], coords["A"][1], col=BORDER_ERR, sw=2.4))
    
    # Звичайне ребро C -> D
    p.append(edge_arrow(coords["C"][0], coords["C"][1], coords["D"][0], coords["D"][1], col=BORDER_NORMAL, sw=1.8))
    
    for name, (cx, cy) in coords.items():
        if name in ["A", "B", "C"]:
            p.append(node(cx, cy, name, fill=COLOR_NODE_ERR, stroke=BORDER_ERR))
        else:
            p.append(node(cx, cy, name, fill=COLOR_NODE_BG, stroke=BORDER_NORMAL))
            
    # Права картка з математичною суперечністю
    b_err, bw_err, bh_err = textbox(570, 135,
                                    "Залежність: A → B → C → A\n\n"
                                    "Вимога порядку:\n"
                                    "pos(A) < pos(B) < pos(C) < pos(A)\n\n"
                                    "Суперечність: pos(A) < pos(A) !\n"
                                    "Жоден лінійний порядок неможливий.",
                                    size=12, pad=12, fill="#fff5f5", stroke=BORDER_ERR)
    p.append(b_err)
    
    # Підпис циклу
    p.append(text(200, 45, "Орієнтований цикл (Cyclic Dependency)", size=14, color=BORDER_ERR, bold=True))
    
    return render(path, W, H, *p)

# ── ФІГ.3 Алгоритм Кана: покрокова робота черги джерел ───────────────────────
def fig_kahn_step():
    path = os.path.join(OUT, "kahn-step.svg")
    W, H = 760, 310
    p = []
    
    # Лівий блок: Стан графа з лічильниками in_degree
    p.append(text(200, 25, "Стан вхідних степеней (in_degree)", size=14, color=INK, bold=True))
    
    nodes_kahn = {
        "A": (70, 90, 0, COLOR_NODE_DONE, BORDER_DONE),    # Оброблено
        "B": (200, 70, 0, COLOR_NODE_ACTIVE, BORDER_ACTIVE),# У черзі Q (degree стало 0)
        "C": (200, 160, 1, COLOR_NODE_BG, BORDER_NORMAL),  # in_degree = 1
        "D": (330, 115, 2, COLOR_NODE_BG, BORDER_NORMAL)   # in_degree = 2
    }
    
    # Ребра
    p.append(edge_arrow(70, 90, 200, 70, col=BORDER_DONE, sw=2.0))
    p.append(edge_arrow(70, 90, 200, 160, col=BORDER_DONE, sw=2.0))
    p.append(edge_arrow(200, 70, 330, 115, col=BORDER_NORMAL, sw=1.8))
    p.append(edge_arrow(200, 160, 330, 115, col=BORDER_NORMAL, sw=1.8))
    
    for name, (cx, cy, deg, fill, stroke) in nodes_kahn.items():
        sub_txt = "in = %d" % deg
        p.append(node(cx, cy, name, fill=fill, stroke=stroke, extra_sub=sub_txt))
        
    # Правий блок: Черга Q та Результат
    p.append(text(580, 25, "Черга джерел Q (in_degree == 0)", size=14, color=INK, bold=True))
    
    # Візуалізація черги Q
    p.append(rect(460, 50, 240, 50, fill=FILL, stroke=BORDER_NORMAL, rx=6))
    p.append(text(480, 80, "Q:", size=14, color=INK, bold=True))
    p.append(rect(510, 60, 36, 30, fill=COLOR_NODE_ACTIVE, stroke=BORDER_ACTIVE, rx=4))
    p.append(text(528, 80, "B", size=14, color=INK, bold=True))
    p.append(text(570, 80, "← наступний для вилучення", size=11, color=MUTED))
    
    # Результат L
    p.append(text(580, 140, "Результат L (Накопичений порядок)", size=14, color=INK, bold=True))
    p.append(rect(460, 165, 240, 50, fill=FILL, stroke=BORDER_NORMAL, rx=6))
    p.append(text(480, 195, "L:", size=14, color=INK, bold=True))
    p.append(rect(510, 175, 36, 30, fill=COLOR_NODE_DONE, stroke=BORDER_DONE, rx=4))
    p.append(text(528, 195, "A", size=14, color=INK, bold=True))
    
    # Підпис знизу
    b_k, bw_k, bh_k = textbox(W / 2, 265,
                              "Крок: вершину A вилучено, її вихідні ребра видалено.\n"
                              "Степінь B впав до 0 → B додано у чергу Q. Наступною з Q буде оброблено B.",
                              size=12, pad=10, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b_k)
    
    return render(path, W, H, *p)

# ── ФІГ.4 Алгоритм DFS: 3 кольори вершин та зворотні ребра ───────────────────
def fig_dfs_colors():
    path = os.path.join(OUT, "dfs-colors.svg")
    W, H = 760, 310
    p = []
    
    # Ліва частина: Стани вершин при DFS
    p.append(text(200, 25, "Кольори вершин під час DFS", size=14, color=INK, bold=True))
    
    # 3 типи вершин з підписами
    p.append(node(80, 80, "U", fill=COLOR_NODE_BG, stroke=BORDER_NORMAL, extra_sub="WHITE (0)"))
    p.append(text(80, 135, "Не відвідано", size=11, color=MUTED))
    
    p.append(node(200, 80, "V", fill=COLOR_NODE_ACTIVE, stroke=BORDER_ACTIVE, extra_sub="GRAY (1)"))
    p.append(text(200, 135, "На стеку викликів", size=11, color=MUTED))
    
    p.append(node(320, 80, "W", fill=COLOR_NODE_DONE, stroke=BORDER_DONE, extra_sub="BLACK (2)"))
    p.append(text(320, 135, "Завершено (Post-order)", size=11, color=MUTED))
    
    # Пояснення зворотного ребра
    b_back, bw_b, bh_b = textbox(200, 225,
                                  "Якщо під час обходу з вершини V веде ребро у GRAY-вершину —\n"
                                  "знайдено ЗВОРОТНЕ РЕБРО (Back Edge). Це сигналізує про ЦИКЛ!",
                                  size=12, pad=10, fill="#fff5f5", stroke=BORDER_ERR)
    p.append(b_back)
    
    # Права частина: Стек виходу та підсумковий розворот
    p.append(text(580, 25, "Формування порядку (Post-Order Reversal)", size=14, color=INK, bold=True))
    
    p.append(text(580, 60, "1. Порядок виходу з рекурсії (стек виходу):", size=12, color=INK))
    p.append(rect(440, 80, 280, 40, fill=FILL, stroke=BORDER_NORMAL, rx=4))
    p.append(text(580, 105, "[ F , E , D , C , B , A ]", size=13, color=MUTED, bold=True))
    
    p.append(text(580, 150, "2. Обернений порядок (Topological Sort):", size=12, color=INK))
    p.append(rect(440, 170, 280, 40, fill=COLOR_NODE_DONE, stroke=BORDER_DONE, rx=4))
    p.append(text(580, 195, "[ A , B , C , D , E , F ]", size=14, color=INK, bold=True))
    
    # Загальний підпис під правою частиною
    p.append(text(580, 250, "Вершина додається у результат ПІСЛЯ завершення всіх своїх дітей.", size=11, color=MUTED))
    
    return render(path, W, H, *p)

if __name__ == "__main__":
    fig_dag_concept()
    fig_cycle_conflict()
    fig_kahn_step()
    fig_dfs_colors()
    print("SVG figures successfully generated in %s" % OUT)
