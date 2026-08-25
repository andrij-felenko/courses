# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ──────────────────────────────────────────────────────────
COLOR_NODE_BG   = "#f8fafc"
COLOR_SCC1_BG   = "#eff6ff"  # Синій відтінок
COLOR_SCC1_BRD  = "#2563eb"
COLOR_SCC2_BG   = "#f0fdf4"  # Зелений відтінок
COLOR_SCC2_BRD  = "#16a34a"
COLOR_SCC3_BG   = "#fff7ed"  # Помаранчевий відтінок
COLOR_SCC3_BRD  = "#ea580c"

BORDER_NORMAL = "#334155"
MUTED_EDGE    = "#94a3b8"
BACK_EDGE     = "#dc2626"  # Зворотні ребра (червоний)

def node(cx, cy, label, fill=COLOR_NODE_BG, stroke=BORDER_NORMAL, r=20):
    """Створює кругу вершину з ім'ям всередині."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, label, size=14, color=INK, bold=True)
    return out

def edge_arrow(x1, y1, x2, y2, r1=20, r2=20, col=BORDER_NORMAL, sw=1.8):
    """Орієнтоване ребро (зі стрілкою) між двома вузлами."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    return arrow(ax, ay, bx, by, color=col, sw=sw)

# ── ФІГ.1 Концепція компонент сильної зв'язаності (SCC) ──────────────────────
def fig_scc_concept():
    path_file = os.path.join(OUT, "scc-concept.svg")
    W, H = 760, 360
    p = []
    
    # 3 контури (бульбашки) для 3 компонент сильної зв'язаності
    # SCC 1: A, B, C (трикутник ліворуч)
    p.append(f'<ellipse cx="140" cy="170" rx="95" ry="105" fill="{COLOR_SCC1_BG}" stroke="{COLOR_SCC1_BRD}" stroke-width="2" stroke-dasharray="6 4"/>')
    p.append(text(140, 52, "SCC 1: {A, B, C}", size=13, color=COLOR_SCC1_BRD, bold=True))
    
    # SCC 2: D, E (центр)
    p.append(f'<ellipse cx="380" cy="170" rx="75" ry="95" fill="{COLOR_SCC2_BG}" stroke="{COLOR_SCC2_BRD}" stroke-width="2" stroke-dasharray="6 4"/>')
    p.append(text(380, 62, "SCC 2: {D, E}", size=13, color=COLOR_SCC2_BRD, bold=True))
    
    # SCC 3: F, G, H (праворуч)
    p.append(f'<ellipse cx="620" cy="170" rx="95" ry="105" fill="{COLOR_SCC3_BG}" stroke="{COLOR_SCC3_BRD}" stroke-width="2" stroke-dasharray="6 4"/>')
    p.append(text(620, 52, "SCC 3: {F, G, H}", size=13, color=COLOR_SCC3_BRD, bold=True))
    
    # Координати вершин
    coords = {
        "A": (95, 120),  "B": (185, 120), "C": (140, 220),
        "D": (380, 110), "E": (380, 230),
        "F": (575, 120), "G": (665, 120), "H": (620, 220)
    }
    
    # Ребра всередині компонент (внутрішні цикли)
    p.append(edge_arrow(coords["A"][0], coords["A"][1], coords["B"][0], coords["B"][1], col=COLOR_SCC1_BRD, sw=2.0))
    p.append(edge_arrow(coords["B"][0], coords["B"][1], coords["C"][0], coords["C"][1], col=COLOR_SCC1_BRD, sw=2.0))
    p.append(edge_arrow(coords["C"][0], coords["C"][1], coords["A"][0], coords["A"][1], col=COLOR_SCC1_BRD, sw=2.0))
    
    # D <-> E (двонапрямлені ребра в SCC 2)
    p.append(edge_arrow(coords["D"][0] - 8, coords["D"][1], coords["E"][0] - 8, coords["E"][1], col=COLOR_SCC2_BRD, sw=2.0))
    p.append(edge_arrow(coords["E"][0] + 8, coords["E"][1], coords["D"][0] + 8, coords["D"][1], col=COLOR_SCC2_BRD, sw=2.0))
    
    # F -> G -> H -> F в SCC 3
    p.append(edge_arrow(coords["F"][0], coords["F"][1], coords["G"][0], coords["G"][1], col=COLOR_SCC3_BRD, sw=2.0))
    p.append(edge_arrow(coords["G"][0], coords["G"][1], coords["H"][0], coords["H"][1], col=COLOR_SCC3_BRD, sw=2.0))
    p.append(edge_arrow(coords["H"][0], coords["H"][1], coords["F"][0], coords["F"][1], col=COLOR_SCC3_BRD, sw=2.0))
    
    # Міжкомпонентні ребра (місткі між SCC)
    p.append(edge_arrow(coords["B"][0], coords["B"][1], coords["D"][0], coords["D"][1], col=BORDER_NORMAL, sw=2.2))
    p.append(edge_arrow(coords["E"][0], coords["E"][1], coords["H"][0], coords["H"][1], col=BORDER_NORMAL, sw=2.2))
    
    # Відображення вершин
    for name, (cx, cy) in coords.items():
        if name in ["A", "B", "C"]:
            st = COLOR_SCC1_BRD
        elif name in ["D", "E"]:
            st = COLOR_SCC2_BRD
        else:
            st = COLOR_SCC3_BRD
        p.append(node(cx, cy, name, stroke=st))
        
    # Нижній пояснювальний блок
    b, bw, bh = textbox(W / 2, 310,
                        "Усередині кожної компоненти (SCC) існує орієнтований шлях від будь-якої вершини u до v і навпаки.\n"
                        "Міжкомпонентні ребра (B → D, E → H) однонапрямлені: зворотного шляху між різними SCC немає.",
                        size=12.5, pad=10, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path_file, W, H, *p, title="Концепція компонент сильної зв'язаності (SCC)")


# ── ФІГ.2 Двопрохідний алгоритм Косарайю–Шаріра ──────────────────────────────
def fig_kosaraju_two_pass():
    path_file = os.path.join(OUT, "kosaraju-two-pass.svg")
    W, H = 760, 360
    p = []
    
    # Ліва панель: Прохід 1 (DFS на первинному графі G)
    p.append(rect(20, 20, 350, 250, fill="#f8fafc", stroke=MUTED_EDGE, rx=6))
    p.append(text(195, 42, "1. DFS на графі G: час виходу (tout)", size=14, color=INK, bold=True))
    
    # Малий граф ліворуч (A -> B -> C -> A, C -> D)
    coords_left = {"A": (70, 90), "B": (160, 90), "C": (115, 170), "D": (250, 130)}
    p.append(edge_arrow(coords_left["A"][0], coords_left["A"][1], coords_left["B"][0], coords_left["B"][1]))
    p.append(edge_arrow(coords_left["B"][0], coords_left["B"][1], coords_left["C"][0], coords_left["C"][1]))
    p.append(edge_arrow(coords_left["C"][0], coords_left["C"][1], coords_left["A"][0], coords_left["A"][1]))
    p.append(edge_arrow(coords_left["C"][0], coords_left["C"][1], coords_left["D"][0], coords_left["D"][1]))
    
    for n, (cx, cy) in coords_left.items():
        p.append(node(cx, cy, n, r=18))
        
    # Стек виходу під лівим графом
    p.append(text(195, 205, "Стек впорядкування за tout:", size=12, color=MUTED, bold=True))
    stack_elems = ["D", "C", "B", "A"]
    for i, elem in enumerate(stack_elems):
        sx = 110 + i * 45
        p.append(rect(sx, 220, 38, 26, fill=COLOR_SCC1_BG, stroke=COLOR_SCC1_BRD, rx=4))
        p.append(text(sx + 19, 237, elem, size=13, color=INK, bold=True))
        
    # Права панель: Прохід 2 (DFS на транспонованому графі G^T)
    p.append(rect(390, 20, 350, 250, fill="#f8fafc", stroke=MUTED_EDGE, rx=6))
    p.append(text(565, 42, "2. DFS на G^T у порядку знімання зі стека", size=14, color=INK, bold=True))
    
    # Малий граф праворуч (ребра розвернуті: A <- B <- C <- A, C <- D)
    coords_right = {"A": (440, 90), "B": (530, 90), "C": (485, 170), "D": (620, 130)}
    p.append(edge_arrow(coords_right["B"][0], coords_right["B"][1], coords_right["A"][0], coords_right["A"][1], col=COLOR_SCC1_BRD, sw=2.0))
    p.append(edge_arrow(coords_right["C"][0], coords_right["C"][1], coords_right["B"][0], coords_right["B"][1], col=COLOR_SCC1_BRD, sw=2.0))
    p.append(edge_arrow(coords_right["A"][0], coords_right["A"][1], coords_right["C"][0], coords_right["C"][1], col=COLOR_SCC1_BRD, sw=2.0))
    p.append(edge_arrow(coords_right["D"][0], coords_right["D"][1], coords_right["C"][0], coords_right["C"][1], col=COLOR_SCC2_BRD, sw=2.0))
    
    p.append(node(coords_right["A"][0], coords_right["A"][1], "A", fill=COLOR_SCC1_BG, stroke=COLOR_SCC1_BRD, r=18))
    p.append(node(coords_right["B"][0], coords_right["B"][1], "B", fill=COLOR_SCC1_BG, stroke=COLOR_SCC1_BRD, r=18))
    p.append(node(coords_right["C"][0], coords_right["C"][1], "C", fill=COLOR_SCC1_BG, stroke=COLOR_SCC1_BRD, r=18))
    p.append(node(coords_right["D"][0], coords_right["D"][1], "D", fill=COLOR_SCC2_BG, stroke=COLOR_SCC2_BRD, r=18))
    
    p.append(text(565, 205, "Виділені SCC на G^T:", size=12, color=MUTED, bold=True))
    p.append(text(565, 235, "1) {A, B, C}   2) {D}", size=13, color=BORDER_NORMAL, bold=True))
    
    # Нижній пояснювальний блок
    b, bw, bh = textbox(W / 2, 310,
                        "Перший прохід DFS наповнює стек у порядку завершення обходу (tout).\n"
                        "Другий прохід витягає вершини зі стека і запускає DFS на транспонованому графі G^T, виділяючи SCC по одній.",
                        size=12.5, pad=10, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path_file, W, H, *p, title="Двопрохідний алгоритм Косарайю–Шаріра")


# ── ФІГ.3 Однопрохідний алгоритм Таржана зі стеком та lowlink ───────────────
def fig_tarjan_stack_lowlink():
    path_file = os.path.join(OUT, "tarjan-stack-lowlink.svg")
    W, H = 760, 380
    p = []
    
    p.append(text(280, 30, "Дерево DFS та обчислення tin / low", size=15, color=INK, bold=True))
    p.append(text(640, 30, "Стек активних вершин", size=15, color=INK, bold=True))
    
    # Вершини дерева DFS
    # 0 -> 1 -> 2 -> 0 (цикл), 1 -> 3
    nodes_data = {
        "0": (120, 80,  "tin=1, low=1"),
        "1": (220, 160, "tin=2, low=1"),
        "2": (120, 240, "tin=3, low=1"),
        "3": (340, 240, "tin=4, low=4")
    }
    
    # Деревні ребра (суцільні)
    p.append(edge_arrow(120, 80, 220, 160, sw=2.2))
    p.append(edge_arrow(220, 160, 120, 240, sw=2.2))
    p.append(edge_arrow(220, 160, 340, 240, sw=2.2))
    
    # Зворотне ребро 2 -> 0 (червона пунктирна лінія)
    p.append(line(105, 230, 105, 90, color=BACK_EDGE, sw=2.0, dash="5 4"))
    # Стрілка зворотного ребра вгору
    p.append(f'<polygon points="105,80 100,92 110,92" fill="{BACK_EDGE}"/>')
    p.append(text(60, 160, "зворотне ребро", size=11, color=BACK_EDGE, bold=True))
    
    # Малювання вершин
    for label, (cx, cy, sub) in nodes_data.items():
        st = COLOR_SCC1_BRD if label in ["0", "1", "2"] else COLOR_SCC2_BRD
        fl = COLOR_SCC1_BG if label in ["0", "1", "2"] else COLOR_SCC2_BG
        p.append(node(cx, cy, label, fill=fl, stroke=st, r=20))
        p.append(text(cx + 45, cy + 4, sub, size=11, color=MUTED, bold=True))
        
    # Стек праворуч
    p.append(rect(600, 70, 80, 200, fill="#f8fafc", stroke=BORDER_NORMAL, rx=4))
    stack_v = [("3", COLOR_SCC2_BG, COLOR_SCC2_BRD, "low[3]==tin[3] -> SCC 2"),
               ("2", COLOR_SCC1_BG, COLOR_SCC1_BRD, ""),
               ("1", COLOR_SCC1_BG, COLOR_SCC1_BRD, ""),
               ("0", COLOR_SCC1_BG, COLOR_SCC1_BRD, "low[0]==tin[0] -> SCC 1")]
    
    for i, (v_name, fl, st, desc) in enumerate(stack_v):
        sy = 220 - i * 45
        p.append(rect(610, sy, 60, 35, fill=fl, stroke=st, rx=4))
        p.append(text(640, sy + 22, v_name, size=14, color=INK, bold=True))
        if desc:
            p.append(text(500 if "SCC 1" in desc else 480, sy + 20, desc, size=10, color=st, bold=True))
            
    # Нижній пояснювальний блок
    b, bw, bh = textbox(W / 2, 330,
                        "Зворотне ребро (2 → 0) оновлює low[2] := min(low[2], tin[0]) = 1. Значення low транслюється вгору деревом.\n"
                        "Коли DFS повертається у вершину u з low[u] == tin[u], вона є коренем SCC: усі вершини вище неї у стеку скидаються в одну SCC.",
                        size=12, pad=10, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path_file, W, H, *p, title="Однопрохідний алгоритм Таржана зі стеком та lowlink")


# ── ФІГ.4 Конденсація графа в орієнтований ациклічний граф (DAG) ─────────────
def fig_condensation_dag():
    path_file = os.path.join(OUT, "condensation-dag.svg")
    W, H = 760, 320
    p = []
    
    # Заголовок
    p.append(text(W / 2, 30, "Граф конденсації G^SCC є орієнтованим безконтурним графом (DAG)", size=15, color=INK, bold=True))
    
    # 3 мета-вершини
    # C1 (ліворуч)
    p.append(rect(80, 80, 160, 110, fill=COLOR_SCC1_BG, stroke=COLOR_SCC1_BRD, rx=12, sw=2.0))
    p.append(text(160, 110, "Мета-вершина C₁", size=15, color=COLOR_SCC1_BRD, bold=True))
    p.append(text(160, 135, "SCC = {A, B, C}", size=13, color=MUTED, bold=True))
    p.append(text(160, 165, "вхідний ступінь = 0", size=11, color=INK))
    
    # C2 (центр)
    p.append(rect(300, 80, 160, 110, fill=COLOR_SCC2_BG, stroke=COLOR_SCC2_BRD, rx=12, sw=2.0))
    p.append(text(380, 110, "Мета-вершина C₂", size=15, color=COLOR_SCC2_BRD, bold=True))
    p.append(text(380, 135, "SCC = {D, E}", size=13, color=MUTED, bold=True))
    p.append(text(380, 165, "вхідний = 1, вихідний = 1", size=11, color=INK))
    
    # C3 (праворуч)
    p.append(rect(520, 80, 160, 110, fill=COLOR_SCC3_BG, stroke=COLOR_SCC3_BRD, rx=12, sw=2.0))
    p.append(text(600, 110, "Мета-вершина C₃", size=15, color=COLOR_SCC3_BRD, bold=True))
    p.append(text(600, 135, "SCC = {F, G, H}", size=13, color=MUTED, bold=True))
    p.append(text(600, 165, "вихідний ступінь = 0", size=11, color=INK))
    
    # Мета-ребра між C1 -> C2 -> C3
    p.append(edge_arrow(240, 135, 300, 135, r1=0, r2=0, col=BORDER_NORMAL, sw=2.5))
    p.append(text(270, 120, "e₁", size=12, color=MUTED, bold=True))
    
    p.append(edge_arrow(460, 135, 520, 135, r1=0, r2=0, col=BORDER_NORMAL, sw=2.5))
    p.append(text(490, 120, "e₂", size=12, color=MUTED, bold=True))
    
    # Пояснювальна картка
    b, bw, bh = textbox(W / 2, 255,
                        "Заміна кожної компоненти сильної зв'язаності на одну мета-вершину утворює конденсований граф G^SCC.\n"
                        "Він НЕ містить орієнтованих циклів (є DAG): це дозволяє топологічно сортувати компоненти й обробляти граф пошарово.",
                        size=13, pad=12, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path_file, W, H, *p, title="Конденсація графа в орієнтований ациклічний граф (DAG)")


if __name__ == "__main__":
    fig_scc_concept()
    fig_kosaraju_two_pass()
    fig_tarjan_stack_lowlink()
    fig_condensation_dag()
    print("Figures generated successfully in img/")
