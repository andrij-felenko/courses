# -*- coding: utf-8 -*-
import sys
import os

# Four directory levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def draw_mst_cut_property():
    """
    Figure 1: mst-definition-cut.svg
    Illustrates graph cut (S, V \\ S), cut-crossing edges, and the lightest cut edge selected by Cut Property.
    """
    w, h = 760, 380
    parts = []

    # Title
    parts.append(text(380, 25, "Властивість розрізу (Cut Property) у зваженому графі", size=15, bold=True))

    # Cut partitions backgrounds: Subset S (left) and Subset V \\ S (right)
    # S partition
    parts.append(rect(40, 55, 300, 295, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=12))
    parts.append(text(190, 80, "Підмножина вершин S", size=13, color="#1e40af", bold=True))

    # V \\ S partition
    parts.append(rect(420, 55, 300, 295, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=12))
    parts.append(text(570, 80, "Підмножина вершин V \\ S", size=13, color="#166534", bold=True))

    # Cut boundary dividing dashed line
    parts.append(line(380, 48, 380, 360, color="#94a3b8", sw=2, dash="6,6"))
    parts.append(text(380, 368, "Лінія розрізу (S, V \\ S)", size=11, color="#64748b", bold=True))

    # Internal edges within S (Tree edges in S)
    parts.append(line(110, 135, 260, 150, color="#2563eb", sw=2.5))
    parts.append(line(110, 135, 130, 265, color="#2563eb", sw=2.5))
    parts.append(line(130, 265, 250, 280, color="#2563eb", sw=2.5))

    # Internal edges within V \\ S (Tree edges in V \\ S)
    parts.append(line(500, 135, 640, 150, color="#16a34a", sw=2.5))
    parts.append(line(500, 265, 630, 280, color="#16a34a", sw=2.5))
    parts.append(line(640, 150, 630, 280, color="#16a34a", sw=2.5))

    # Cut crossing edges (between S and V \\ S)
    # Edge 1: u2 (260, 150) -> v1 (500, 135), weight = 7 (Heavier)
    parts.append(line(260, 150, 500, 135, color="#94a3b8", sw=1.8, dash="4,4"))
    # Edge 2: u2 (260, 150) -> v3 (500, 265), weight = 3 (LIGHTEST - Cut Property SAFE EDGE!)
    parts.append(line(260, 150, 500, 265, color="#dc2626", sw=3.5))
    # Edge 3: u4 (250, 280) -> v3 (500, 265), weight = 6 (Heavier)
    parts.append(line(250, 280, 500, 265, color="#94a3b8", sw=1.8, dash="4,4"))

    # Labels for crossing edge weights
    # Lightest edge weight badge
    parts.append(rect(355, 195, 50, 24, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(380, 211, "w = 3", size=11, color="#991b1b", bold=True))

    # Other crossing edges badges
    parts.append(rect(360, 125, 40, 20, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(380, 139, "w = 7", size=10, color="#475569"))

    parts.append(rect(360, 270, 40, 20, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(380, 284, "w = 6", size=10, color="#475569"))

    # Vertices in S
    nodes_s = [
        (110, 135, "A"),
        (260, 150, "B"),
        (130, 265, "C"),
        (250, 280, "D")
    ]
    for nx, ny, name in nodes_s:
        parts.append(circle(nx, ny, 19, fill="#dbeafe", stroke="#1d4ed8", sw=2))
        parts.append(text(nx, ny + 4.5, name, size=12, color="#1e3a8a", bold=True))

    # Vertices in V \\ S
    nodes_v = [
        (500, 135, "E"),
        (640, 150, "F"),
        (500, 265, "G"),
        (630, 280, "H")
    ]
    for nx, ny, name in nodes_v:
        parts.append(circle(nx, ny, 19, fill="#dcfce7", stroke="#15803d", sw=2))
        parts.append(text(nx, ny + 4.5, name, size=12, color="#14532d", bold=True))

    # Callout badge at bottom
    parts.append(fitbox(55, 305, 270, 36, "Внутрішній кістяк компоненти S", size=10, fill="#ffffff", stroke="#93c5fd", color="#1e40af", bold=True))
    parts.append(fitbox(435, 305, 270, 36, "Внутрішній кістяк компоненти V \\ S", size=10, fill="#ffffff", stroke="#86efac", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "mst-definition-cut.svg"), w, h, *parts)


def draw_prim_vs_boruvka():
    """
    Figure 2: prim-vs-boruvka-evolution.svg
    Compares the evolutionary expansion of MST in Prim (single tree expanding) vs Boruvka/Kruskal (forest fragments merging).
    """
    w, h = 760, 340
    parts = []

    parts.append(text(380, 24, "Еволюція побудови МКД: Алгоритм Прима проти Алгоритму Борувки", size=15, bold=True))

    # Left panel: Prim's Algorithm (Single component growth)
    parts.append(rect(30, 48, 335, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(197, 72, "Алгоритм Прима: Росте ОДНЕ дерево", size=12, color="#1e293b", bold=True))

    # Single growing blob (x=45 to x=195)
    parts.append(rect(45, 95, 150, 175, fill="#e0f2fe", stroke="#38bdf8", sw=1.5, rx=16))
    parts.append(text(120, 115, "Зростаюче дерево T", size=10, color="#0369a1", bold=True))

    # Edges in Prim's tree
    parts.append(line(80, 160, 145, 145, color="#0284c7", sw=2.5))
    parts.append(line(80, 160, 105, 220, color="#0284c7", sw=2.5))
    parts.append(line(145, 145, 165, 210, color="#0284c7", sw=2.5))

    # Prim vertices inside T
    parts.append(circle(80, 160, 15, fill="#0284c7", stroke="#0369a1", sw=1.5))
    parts.append(text(80, 164, "s", size=11, color="#ffffff", bold=True))

    parts.append(circle(145, 145, 15, fill="#0284c7", stroke="#0369a1", sw=1.5))
    parts.append(text(145, 149, "u₁", size=10, color="#ffffff", bold=True))

    parts.append(circle(105, 220, 15, fill="#0284c7", stroke="#0369a1", sw=1.5))
    parts.append(text(105, 224, "u₂", size=10, color="#ffffff", bold=True))

    parts.append(circle(165, 210, 15, fill="#0284c7", stroke="#0369a1", sw=1.5))
    parts.append(text(165, 214, "u₃", size=10, color="#ffffff", bold=True))

    # Candidate vertex outside T (x=300)
    parts.append(circle(300, 160, 16, fill="#f1f5f9", stroke="#64748b", sw=1.5))
    parts.append(text(300, 164, "v", size=11, color="#1e293b", bold=True))

    # Lightest crossing candidate edge from u1 (145, 145) to v (300, 160)
    parts.append(line(145, 145, 300, 160, color="#dc2626", sw=2.5))
    # Badge situated at x=215..260, outside blob (which ends at 195) and outside node v (at 300)
    parts.append(rect(215, 140, 48, 20, fill="#fee2e2", stroke="#ef4444", sw=1, rx=3))
    parts.append(text(239, 154, "min w", size=9, color="#991b1b", bold=True))

    # Caption for Prim
    parts.append(fitbox(45, 280, 305, 34, "Почергово приєднує найближчу вершину v ∉ T", size=10, fill="#ffffff", stroke="#cbd5e1", color="#475569"))


    # Right panel: Boruvka / Kruskal Algorithm (Multi-fragment parallel growth)
    parts.append(rect(395, 48, 335, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(562, 72, "Алгоритм Борувки: Зливаються ФРАГМЕНТИ", size=12, color="#1e293b", bold=True))

    # Fragment 1 (Top Left: x=410..525)
    parts.append(rect(410, 95, 115, 75, fill="#dcfce7", stroke="#4ade80", sw=1.5, rx=10))
    parts.append(text(467, 110, "Фрагмент 1", size=9, color="#15803d", bold=True))
    parts.append(line(435, 140, 490, 145, color="#16a34a", sw=2.2))
    parts.append(circle(435, 140, 13, fill="#16a34a", stroke="#15803d", sw=1.5))
    parts.append(circle(490, 145, 13, fill="#16a34a", stroke="#15803d", sw=1.5))

    # Fragment 2 (Top Right: x=600..715)
    parts.append(rect(600, 95, 115, 75, fill="#fef3c7", stroke="#fcd34d", sw=1.5, rx=10))
    parts.append(text(657, 110, "Фрагмент 2", size=9, color="#b45309", bold=True))
    parts.append(line(625, 145, 685, 140, color="#d97706", sw=2.2))
    parts.append(circle(625, 145, 13, fill="#d97706", stroke="#b45309", sw=1.5))
    parts.append(circle(685, 140, 13, fill="#d97706", stroke="#b45309", sw=1.5))

    # Fragment 3 (Bottom Center: x=500..625)
    parts.append(rect(500, 195, 125, 75, fill="#ede9fe", stroke="#c084fc", sw=1.5, rx=10))
    parts.append(text(562, 210, "Фрагмент 3", size=9, color="#6b21a8", bold=True))
    parts.append(line(530, 245, 595, 245, color="#9333ea", sw=2.2))
    parts.append(circle(530, 245, 13, fill="#9333ea", stroke="#6b21a8", sw=1.5))
    parts.append(circle(595, 245, 13, fill="#9333ea", stroke="#6b21a8", sw=1.5))

    # Parallel connecting edges between fragments
    parts.append(line(490, 145, 625, 145, color="#dc2626", sw=2.5, dash="4,3"))
    parts.append(line(490, 145, 530, 245, color="#dc2626", sw=2.5, dash="4,3"))

    # Edge labels badge situated between 525 and 600 at x=540..580
    parts.append(rect(540, 135, 40, 20, fill="#fee2e2", stroke="#ef4444", sw=1, rx=3))
    parts.append(text(560, 149, "e₁₂", size=9, color="#991b1b", bold=True))

    # Caption for Boruvka
    parts.append(fitbox(410, 280, 305, 34, "Паралельне злиття всіх компонент за найдешевшими ребрами", size=10, fill="#ffffff", stroke="#cbd5e1", color="#475569"))

    render(os.path.join(OUT_DIR, "prim-vs-boruvka-evolution.svg"), w, h, *parts)


def draw_cycle_property():
    """
    Figure 3: cycle-property-exchange.svg
    Shows Cycle Property: Adding an edge e creates a cycle C, heaviest edge e_max is removed.
    """
    w, h = 760, 360
    parts = []

    parts.append(text(380, 25, "Властивість циклу (Cycle Property) та техніка заміни ребер", size=15, bold=True))

    # Background cycle area
    parts.append(rect(40, 55, 680, 280, fill="#fafafa", stroke="#e2e8f0", sw=1.5, rx=12))

    # Spanning Tree edges (in T) - solid green/blue
    # 1 -> 2: w = 4
    parts.append(line(180, 120, 380, 85, color="#2563eb", sw=3))
    parts.append(rect(265, 90, 42, 20, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    parts.append(text(286, 104, "w = 4", size=10, color="#1e40af", bold=True))

    # 2 -> 3: w = 5
    parts.append(line(380, 85, 580, 120, color="#2563eb", sw=3))
    parts.append(rect(465, 90, 42, 20, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    parts.append(text(486, 104, "w = 5", size=10, color="#1e40af", bold=True))

    # 3 -> 4: w = 9 (HEAVIEST EDGE IN CYCLE e_max - CANDIDATE FOR REMOVAL!)
    parts.append(line(580, 120, 500, 250, color="#dc2626", sw=3.5, dash="6,4"))
    parts.append(rect(545, 175, 75, 24, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(582, 191, "e_max (w = 9)", size=10, color="#991b1b", bold=True))

    # 4 -> 5: w = 3
    parts.append(line(500, 250, 260, 250, color="#2563eb", sw=3))
    parts.append(rect(360, 240, 42, 20, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    parts.append(text(381, 254, "w = 3", size=10, color="#1e40af", bold=True))

    # Non-tree Edge 5 -> 1: w = 2 (NEW ADDED EDGE e - CHEAP ALTERNATIVE!)
    parts.append(line(260, 250, 180, 120, color="#16a34a", sw=3.5))
    parts.append(rect(170, 175, 75, 24, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(207, 191, "e_new (w = 2)", size=10, color="#15803d", bold=True))

    # Vertices
    nodes = [
        (180, 120, "u₁"),
        (380, 85, "u₂"),
        (580, 120, "u₃"),
        (500, 250, "u₄"),
        (260, 250, "u₅")
    ]
    for nx, ny, name in nodes:
        parts.append(circle(nx, ny, 20, fill="#ffffff", stroke="#0f172a", sw=2))
        parts.append(text(nx, ny + 4.5, name, size=12, color="#0f172a", bold=True))

    # Central explanation callout
    parts.append(rect(290, 140, 180, 70, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(380, 160, "Утворено цикл C", size=11, color="#0f172a", bold=True))
    parts.append(text(380, 178, "w(T') = w(T) + 2 − 9", size=11, color="#16a34a", bold=True))
    parts.append(text(380, 196, "Зменшення ваги на 7!", size=10, color="#dc2626", bold=True))

    # Bottom summary explanation
    parts.append(fitbox(60, 290, 640, 36, "Додавання ребра e_new замикає цикл C; вилучення найважчого ребра e_max відновлює дерево меншої ваги", size=10, fill="#ffffff", stroke="#94a3b8", color="#334155", bold=True))

    render(os.path.join(OUT_DIR, "cycle-property-exchange.svg"), w, h, *parts)


def draw_clustering_and_bottleneck():
    """
    Figure 4: clustering-and-bottleneck.svg
    Illustrates k-clustering via MST edge deletion and the Minimax (Bottleneck) property.
    """
    w, h = 760, 340
    parts = []

    parts.append(text(380, 24, "Застосування МКД: Кластеризація (k-Clustering) та Вузькі місця", size=15, bold=True))

    # Cluster 1 Box (Left)
    parts.append(rect(40, 55, 200, 225, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=12))
    parts.append(text(140, 80, "Кластер 1 (C₁)", size=12, color="#1e40af", bold=True))

    # Cluster 1 edges & nodes
    parts.append(line(90, 130, 180, 120, color="#2563eb", sw=2.2))
    parts.append(line(90, 130, 120, 210, color="#2563eb", sw=2.2))
    parts.append(line(180, 120, 190, 200, color="#2563eb", sw=2.2))

    parts.append(circle(90, 130, 15, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    parts.append(text(90, 134, "A", size=11, color="#1e3a8a", bold=True))

    parts.append(circle(180, 120, 15, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    parts.append(text(180, 124, "B", size=11, color="#1e3a8a", bold=True))

    parts.append(circle(120, 210, 15, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    parts.append(text(120, 214, "C", size=11, color="#1e3a8a", bold=True))

    parts.append(circle(190, 200, 15, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    parts.append(text(190, 204, "D", size=11, color="#1e3a8a", bold=True))


    # Cluster 2 Box (Middle-Right)
    parts.append(rect(290, 55, 200, 225, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=12))
    parts.append(text(390, 80, "Кластер 2 (C₂)", size=12, color="#166534", bold=True))

    # Cluster 2 edges & nodes
    parts.append(line(340, 130, 430, 140, color="#16a34a", sw=2.2))
    parts.append(line(340, 130, 360, 220, color="#16a34a", sw=2.2))
    parts.append(line(430, 140, 440, 210, color="#16a34a", sw=2.2))

    parts.append(circle(340, 130, 15, fill="#dcfce7", stroke="#15803d", sw=1.5))
    parts.append(text(340, 134, "E", size=11, color="#14532d", bold=True))

    parts.append(circle(430, 140, 15, fill="#dcfce7", stroke="#15803d", sw=1.5))
    parts.append(text(430, 144, "F", size=11, color="#14532d", bold=True))

    parts.append(circle(360, 220, 15, fill="#dcfce7", stroke="#15803d", sw=1.5))
    parts.append(text(360, 224, "G", size=11, color="#14532d", bold=True))

    parts.append(circle(440, 210, 15, fill="#dcfce7", stroke="#15803d", sw=1.5))
    parts.append(text(440, 214, "H", size=11, color="#14532d", bold=True))


    # Cluster 3 Box (Far Right)
    parts.append(rect(540, 55, 180, 225, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=12))
    parts.append(text(630, 80, "Кластер 3 (C₃)", size=12, color="#9a3412", bold=True))

    # Cluster 3 edges & nodes
    parts.append(line(590, 135, 670, 160, color="#ea580c", sw=2.2))
    parts.append(line(590, 135, 620, 220, color="#ea580c", sw=2.2))

    parts.append(circle(590, 135, 15, fill="#ffedd5", stroke="#c2410c", sw=1.5))
    parts.append(text(590, 139, "I", size=11, color="#7c2d12", bold=True))

    parts.append(circle(670, 160, 15, fill="#ffedd5", stroke="#c2410c", sw=1.5))
    parts.append(text(670, 164, "J", size=11, color="#7c2d12", bold=True))

    parts.append(circle(620, 220, 15, fill="#ffedd5", stroke="#c2410c", sw=1.5))
    parts.append(text(620, 224, "K", size=11, color="#7c2d12", bold=True))


    # Cut Edges (Deleted heaviest edges of MST):
    # Cut 1: B (180, 120) -> E (340, 130), w = 18 (Deleted)
    parts.append(line(180, 120, 340, 130, color="#dc2626", sw=2.5, dash="6,4"))
    parts.append(rect(235, 115, 60, 22, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(265, 130, "w = 18 ✖", size=10, color="#991b1b", bold=True))

    # Cut 2: F (430, 140) -> I (590, 135), w = 24 (Deleted)
    parts.append(line(430, 140, 590, 135, color="#dc2626", sw=2.5, dash="6,4"))
    parts.append(rect(485, 125, 60, 22, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    parts.append(text(515, 140, "w = 24 ✖", size=10, color="#991b1b", bold=True))

    # Bottom summary box
    parts.append(fitbox(50, 290, 660, 36, "Вилучення k − 1 найважчих ребер МКД максимізує мінімальну міжкиликову відстань (Margin)", size=10, fill="#ffffff", stroke="#cbd5e1", color="#334155", bold=True))

    render(os.path.join(OUT_DIR, "clustering-and-bottleneck.svg"), w, h, *parts)


if __name__ == '__main__':
    draw_mst_cut_property()
    draw_prim_vs_boruvka()
    draw_cycle_property()
    draw_clustering_and_bottleneck()
    print("All figures successfully generated.")
