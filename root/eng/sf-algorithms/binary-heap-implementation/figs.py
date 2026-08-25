# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

HEAP_BG  = "#f4f6f8"
MIN_NODE = "#eaf0fd"
MAX_NODE = "#fdecea"
HL_NODE  = "#e6f7ee"
ACCENT   = "#2457d6"
HOT      = "#c0392b"
OK_GRN   = "#27ae60"

def draw_node(cx, cy, val, idx_text=None, r=18, fill=FILL, stroke=LINE, sw=1.8, tc=INK):
    out = [circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw),
           text(cx, cy + 5, str(val), size=14, color=tc, bold=True)]
    if idx_text is not None:
        out.append(text(cx, cy - r - 4, idx_text, size=11, color=MUTED, bold=True))
    return "".join(out)

def draw_cell(x, y, w, h, val, idx=None, fill=FILL, stroke=LINE, sw=1.5, tc=INK):
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4),
           text(x + w / 2, y + h / 2 + 5, str(val), size=14, color=tc, bold=True)]
    if idx is not None:
        out.append(text(x + w / 2, y - 5, str(idx), size=11, color=MUTED, bold=True))
    return "".join(out)

def fig_tree_to_array():
    W, H = 760, 370
    f = []
    f.append(text(220, 24, "Двійкове майже повне дерево", size=15, bold=True, color=INK))
    coords = [(220, 60), (130, 125), (310, 125), (85, 190), (175, 190), (265, 190), (355, 190)]
    vals = [4, 12, 8, 25, 19, 15, 30]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        f.append(line(x1, y1 + 14, x2, y2 - 14, color=LINE, sw=1.8))
    for i, (cx, cy) in enumerate(coords):
        f.append(draw_node(cx, cy, vals[i], idx_text="i=" + str(i), r=16, fill=MIN_NODE if i==0 else FILL))
    f.append(rect(430, 42, 310, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(585, 66, "Арифметика переходів (0-індексація)", size=13, bold=True, color=INK))
    f.append(text(450, 95, "• Ліва дитина:", size=12, anchor="start", bold=True, color=INK))
    f.append(text(575, 95, "left(i) = 2i + 1", size=12, anchor="start", bold=True, color=ACCENT))
    f.append(text(450, 122, "• Права дитина:", size=12, anchor="start", bold=True, color=INK))
    f.append(text(575, 122, "right(i) = 2i + 2", size=12, anchor="start", bold=True, color=ACCENT))
    f.append(text(450, 149, "• Батьківський вузол:", size=12, anchor="start", bold=True, color=INK))
    f.append(text(575, 149, "parent(i) = ⌊(i − 1) / 2⌋", size=12, anchor="start", bold=True, color=HOT))
    f.append(text(450, 180, "1-індексація: 2i,  2i + 1,  ⌊i / 2⌋ (бітовий зсув i>>1)", size=11, anchor="start", color=MUTED))
    f.append(arrow(220, 222, 220, 260, color=ACCENT, sw=2.2))
    f.append(text(275, 245, "порівневий запис", size=11, color=ACCENT, bold=True))
    f.append(text(90, 310, "Одновимірний масив:", size=13, bold=True, anchor="end", color=INK))
    cw, ch = 52, 42
    start_x = 110
    ay = 285
    for i, v in enumerate(vals):
        f.append(draw_cell(start_x + i * cw, ay, cw, ch, v, idx="[" + str(i) + "]", fill=MIN_NODE if i==0 else FILL))
    f.append(text(500, 310, "Без вказівників (0 байтів оверхеду), 100% кеш-локальність", size=12, color=OK_GRN, anchor="start", bold=True))
    render(os.path.join(IMG, "binary-tree-to-array.svg"), W, H, *f)

def fig_heap_invariants():
    W, H = 760, 260
    f = []
    f.append(text(120, 24, "Min-Купа (батько ≤ дітей)", size=14, bold=True, color=INK))
    f.append(line(120, 55, 75, 100, color=LINE, sw=1.5))
    f.append(line(120, 55, 165, 100, color=LINE, sw=1.5))
    f.append(line(75, 100, 50, 145, color=LINE, sw=1.5))
    f.append(line(75, 100, 100, 145, color=LINE, sw=1.5))
    f.append(line(165, 100, 140, 145, color=LINE, sw=1.5))
    f.append(line(165, 100, 190, 145, color=LINE, sw=1.5))
    f.append(draw_node(120, 55, 3, r=15, fill=MIN_NODE, stroke=ACCENT, sw=2))
    f.append(draw_node(75, 100, 7, r=15))
    f.append(draw_node(165, 100, 5, r=15))
    f.append(draw_node(50, 145, 12, r=14))
    f.append(draw_node(100, 145, 9, r=14))
    f.append(draw_node(140, 145, 15, r=14))
    f.append(draw_node(190, 145, 8, r=14))
    f.append(text(120, 195, "Корінь = Глобальний МІНІМУМ", size=11, bold=True, color=ACCENT))
    f.append(text(120, 215, "Діти не впорядковані між собою (7 > 5)", size=11, color=MUTED))
    f.append(line(245, 20, 245, 235, color="#e2e8f0", sw=1.5, dash="4,4"))
    f.append(text(375, 24, "Max-Купа (батько ≥ дітей)", size=14, bold=True, color=INK))
    f.append(line(375, 55, 330, 100, color=LINE, sw=1.5))
    f.append(line(375, 55, 420, 100, color=LINE, sw=1.5))
    f.append(line(330, 100, 305, 145, color=LINE, sw=1.5))
    f.append(line(330, 100, 355, 145, color=LINE, sw=1.5))
    f.append(line(420, 100, 395, 145, color=LINE, sw=1.5))
    f.append(line(420, 100, 445, 145, color=LINE, sw=1.5))
    f.append(draw_node(375, 55, 95, r=15, fill=MAX_NODE, stroke=HOT, sw=2))
    f.append(draw_node(330, 100, 70, r=15))
    f.append(draw_node(420, 100, 85, r=15))
    f.append(draw_node(305, 145, 20, r=14))
    f.append(draw_node(355, 145, 65, r=14))
    f.append(draw_node(395, 145, 40, r=14))
    f.append(draw_node(445, 145, 80, r=14))
    f.append(text(375, 195, "Корінь = Глобальний МАКСИМУМ", size=11, bold=True, color=HOT))
    f.append(text(375, 215, "Діти не впорядковані між собою (70 < 85)", size=11, color=MUTED))
    f.append(line(500, 20, 500, 235, color="#e2e8f0", sw=1.5, dash="4,4"))
    f.append(text(630, 24, "Дерево пошуку (BST)", size=14, bold=True, color=INK))
    f.append(line(630, 55, 580, 100, color=LINE, sw=1.5))
    f.append(line(630, 55, 680, 100, color=LINE, sw=1.5))
    f.append(line(580, 100, 555, 145, color=LINE, sw=1.5))
    f.append(line(580, 100, 605, 145, color=LINE, sw=1.5))
    f.append(line(680, 100, 655, 145, color=LINE, sw=1.5))
    f.append(line(680, 100, 705, 145, color=LINE, sw=1.5))
    f.append(draw_node(630, 55, 50, r=15, fill=FILL))
    f.append(draw_node(580, 100, 30, r=15))
    f.append(draw_node(680, 100, 70, r=15))
    f.append(draw_node(555, 145, 20, r=14))
    f.append(draw_node(605, 145, 40, r=14))
    f.append(draw_node(655, 145, 60, r=14))
    f.append(draw_node(705, 145, 80, r=14))
    f.append(text(630, 195, "Горизонтальний порядок (L < Root < R)", size=11, bold=True, color=INK))
    f.append(text(630, 215, "Повний порядок дорогий для динамічного min", size=11, color=MUTED))
    render(os.path.join(IMG, "heap-invariants.svg"), W, H, *f)

def fig_sift_up_down():
    W, H = 760, 290
    f = []
    f.append(text(180, 24, "Просіювання вгору (Sift-Up / Push)", size=14, bold=True, color=INK))
    f.append(text(180, 44, "Додаємо новий елемент «2» у хвіст масиву", size=11, color=MUTED))
    f.append(line(180, 75, 120, 120, color=LINE, sw=1.5))
    f.append(line(180, 75, 240, 120, color=LINE, sw=1.5))
    f.append(line(120, 120, 90, 165, color=LINE, sw=1.5))
    f.append(line(120, 120, 150, 165, color=LINE, sw=1.5))
    f.append(line(240, 120, 210, 165, color=LINE, sw=1.5))
    f.append(line(240, 120, 270, 165, color=LINE, sw=1.5))
    f.append(draw_node(180, 75, 5, r=14))
    f.append(draw_node(120, 120, 10, r=14))
    f.append(draw_node(240, 120, 8, r=14, fill=MAX_NODE))
    f.append(draw_node(90, 165, 15, r=13))
    f.append(draw_node(150, 165, 20, r=13))
    f.append(draw_node(210, 165, 18, r=13))
    f.append(draw_node(270, 165, 2, r=13, fill=HL_NODE, stroke=OK_GRN, sw=2))
    f.append(arrow(260, 152, 248, 134, color=OK_GRN, sw=2.2))
    f.append(arrow(230, 108, 192, 85, color=OK_GRN, sw=2.2))
    f.append(text(180, 210, "Крок 1: 2 < 8  → обмін з батьком", size=11, bold=True, color=OK_GRN))
    f.append(text(180, 230, "Крок 2: 2 < 5  → обмін з коренем", size=11, bold=True, color=OK_GRN))
    f.append(text(180, 255, "Вартість: O(висота) = O(log N) порівнянь", size=11, color=ACCENT, bold=True))
    f.append(line(370, 20, 370, 270, color="#cbd5e1", sw=1.5))
    f.append(text(560, 24, "Просіювання вниз (Sift-Down / Pop)", size=14, bold=True, color=INK))
    f.append(text(560, 44, "Вилучили корінь, поставили останній елемент «30»", size=11, color=MUTED))
    f.append(line(560, 75, 500, 120, color=LINE, sw=1.5))
    f.append(line(560, 75, 620, 120, color=LINE, sw=1.5))
    f.append(line(500, 120, 470, 165, color=LINE, sw=1.5))
    f.append(line(500, 120, 530, 165, color=LINE, sw=1.5))
    f.append(line(620, 120, 590, 165, color=LINE, sw=1.5))
    f.append(line(620, 120, 650, 165, color=LINE, sw=1.5))
    f.append(draw_node(560, 75, 30, r=14, fill=MAX_NODE, stroke=HOT, sw=2))
    f.append(draw_node(500, 120, 4, r=14, fill=HL_NODE, stroke=OK_GRN, sw=2))
    f.append(draw_node(620, 120, 9, r=14))
    f.append(draw_node(470, 165, 12, r=13))
    f.append(draw_node(530, 165, 7, r=13, fill=HL_NODE, stroke=OK_GRN, sw=2))
    f.append(draw_node(590, 165, 15, r=13))
    f.append(draw_node(650, 165, 25, r=13))
    f.append(arrow(550, 88, 512, 110, color=HOT, sw=2.2))
    f.append(arrow(508, 134, 522, 152, color=HOT, sw=2.2))
    f.append(text(560, 210, "Крок 1: min(4, 9) = 4;  30 > 4 → обмін з 4", size=11, bold=True, color=HOT))
    f.append(text(560, 230, "Крок 2: min(12, 7) = 7; 30 > 7 → обмін з 7", size=11, bold=True, color=HOT))
    f.append(text(560, 255, "Обов'язковий вибір МЕНШОЇ дитини! Разом: O(log N)", size=11, color=ACCENT, bold=True))
    render(os.path.join(IMG, "sift-up-down.svg"), W, H, *f)

def fig_floyd_heapify():
    W, H = 760, 310
    f = []
    f.append(text(380, 24, "Лінійна побудова купи за алгоритмом Флойда (Bottom-Up Heapify)", size=15, bold=True, color=INK))
    coords = [(260, 60), (160, 120), (360, 120), (110, 180), (210, 180), (310, 180), (410, 180)]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        f.append(line(x1, y1 + 13, x2, y2 - 13, color=LINE, sw=1.5))
    for i, (cx, cy) in enumerate(coords):
        fill_c = "#f1f5f9" if i>=3 else (HL_NODE if i>=1 else MIN_NODE)
        f.append(draw_node(cx, cy, "v" + str(i), idx_text="i=" + str(i), r=15, fill=fill_c))
    f.append(line(50, 60, 470, 60, color="#cbd5e1", sw=1, dash="3,3"))
    f.append(line(50, 120, 470, 120, color="#cbd5e1", sw=1, dash="3,3"))
    f.append(line(50, 180, 470, 180, color="#cbd5e1", sw=1, dash="3,3"))
    f.append(text(45, 64, "h=2", size=11, bold=True, anchor="end", color=MUTED))
    f.append(text(45, 124, "h=1", size=11, bold=True, anchor="end", color=MUTED))
    f.append(text(45, 184, "h=0", size=11, bold=True, anchor="end", color=MUTED))
    f.append(rect(490, 45, 255, 185, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(617, 68, "Розподіл праці за висотою h", size=13, bold=True, color=INK))
    f.append(text(505, 96, "• h=0 (Листки, 50% вузлів):", size=11, anchor="start", bold=True, color=MUTED))
    f.append(text(725, 96, "0 кроків", size=11, anchor="end", bold=True, color=OK_GRN))
    f.append(text(505, 124, "• h=1 (Батьки листків, 25%):", size=11, anchor="start", bold=True, color=MUTED))
    f.append(text(725, 124, "≤ 1 спуск", size=11, anchor="end", bold=True, color=ACCENT))
    f.append(text(505, 152, "• h=2 (Корінь, 1 вузол):", size=11, anchor="start", bold=True, color=MUTED))
    f.append(text(725, 152, "≤ 2 спуски", size=11, anchor="end", bold=True, color=HOT))
    f.append(line(505, 172, 730, 172, color="#cbd5e1", sw=1))
    f.append(text(617, 195, "Сумарно: S = N ∑ (h / 2ʰ) ≤ 2N", size=12, bold=True, color=OK_GRN))
    f.append(text(617, 215, "Складність побудови: O(N)", size=12, bold=True, color=ACCENT))
    f.append(text(380, 260, "Алгоритм Флойда починає з індексу i = ⌊N/2⌋ − 1 і рухається до 0 (Bottom-Up).", size=12, bold=True, color=INK))
    f.append(text(380, 282, "Маса вузлів зосереджена внизу, тому переважна більшість виконує 0 або 1 спуск!", size=11, color=MUTED))
    render(os.path.join(IMG, "floyd-heapify.svg"), W, H, *f)

def fig_indexed_heap_map():
    W, H = 760, 260
    f = []
    f.append(text(380, 24, "Індексована купа (Indexed Heap): Decrease-Key та Delete за O(log N)", size=15, bold=True, color=INK))
    f.append(text(140, 60, "Масив позицій: pos[id]", size=13, bold=True, color=ACCENT))
    f.append(text(140, 78, "(індекс вузла в купі за його дескриптором id)", size=10, color=MUTED))
    cw, ch = 44, 36
    ids = [0, 1, 2, 3, 4]
    pos_vals = [2, 0, 4, 1, 3]
    for i in range(5):
        f.append(draw_cell(30 + i * cw, 92, cw, ch, pos_vals[i], idx="id=" + str(ids[i]), fill="#eff6ff", stroke=ACCENT))
    f.append(text(540, 60, "Масив купи: h[i] = {id, key}", size=13, bold=True, color=OK_GRN))
    f.append(text(540, 78, "(фізичний масив двійкової купи)", size=10, color=MUTED))
    heap_nodes = [("id:1", "k:10"), ("id:3", "k:15"), ("id:0", "k:25"), ("id:4", "k:40"), ("id:2", "k:50")]
    hw = 64
    for i in range(5):
        nid, nkey = heap_nodes[i]
        x = 380 + i * hw
        y = 92
        f.append(rect(x, y, hw, ch, fill=HL_NODE if i==0 else FILL, stroke=LINE, sw=1.5, rx=4))
        f.append(text(x + hw/2, y - 5, "[" + str(i) + "]", size=11, color=MUTED, bold=True))
        f.append(text(x + hw/2, y + 14, nid, size=11, bold=True, color=INK))
        f.append(text(x + hw/2, y + 28, nkey, size=11, bold=True, color=ACCENT if i==0 else INK))
    f.append(arrow(184, 136, 476, 136, color=HOT, sw=2.2))
    f.append(text(330, 155, "Прямий доступ O(1): pos[id=3] → комірка h[1]", size=11, bold=True, color=HOT))
    f.append(rect(40, 180, 680, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(380, 202, "Двосторонній інваріант: pos[h[i].id] == i та h[pos[id]].id == id", size=12, bold=True, color=INK))
    f.append(text(380, 224, "Кожен swap(h[i], h[j]) обов'язково оновлює pos[h[i].id] = i та pos[h[j].id] = j", size=11, color=MUTED))
    render(os.path.join(IMG, "indexed-heap-map.svg"), W, H, *f)

if __name__ == "__main__":
    fig_tree_to_array()
    fig_heap_invariants()
    fig_sift_up_down()
    fig_floyd_heapify()
    fig_indexed_heap_map()
    print("All 5 figures generated successfully.")
