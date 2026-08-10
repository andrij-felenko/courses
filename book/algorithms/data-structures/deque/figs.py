# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_deque_ring():
    """Фігура 1: Кільцевий буфер фіксованого розміру (загортання індексів)"""
    W, H = 820, 240
    p = []

    p.append(text(W/2, 30, "Кільцевий масив (загортання індексів head та tail)", size=16, color=INK, bold=True, anchor="middle"))

    x0, y0 = 90, 75
    cw, ch = 80, 50
    items = ["30", "40", "", "", "", "", "10", "20"]
    
    for i in range(8):
        bx = x0 + i * cw
        val = items[i]
        active = bool(val)
        fill_col = "#eafaf0" if active else "#f8f9fa"
        stroke_col = FIELD if active else "#d0d7de"
        
        p.append(rect(bx, y0, cw - 4, ch, fill=fill_col, stroke=stroke_col, sw=1.5, rx=4))
        p.append(text(bx + (cw - 4)/2, y0 - 10, f"[{i}]", size=12, color=MUTED, anchor="middle"))
        
        if active:
            p.append(text(bx + (cw - 4)/2, y0 + ch/2 + 5, val, size=16, color=INK, bold=True, anchor="middle"))

    # Marker tail at index 1
    t_x = x0 + 1 * cw + (cw - 4)/2
    p.append(arrow(t_x, y0 + ch + 35, t_x, y0 + ch + 4, color=POS, sw=2.0))
    p.append(text(t_x, y0 + ch + 52, "tail (хвіст = 1)", size=13, color=POS, bold=True, anchor="middle"))

    # Marker head at index 6
    h_x = x0 + 6 * cw + (cw - 4)/2
    p.append(arrow(h_x, y0 + ch + 35, h_x, y0 + ch + 4, color=NEG, sw=2.0))
    p.append(text(h_x, y0 + ch + 52, "head (голова = 6)", size=13, color=NEG, bold=True, anchor="middle"))

    # Wrap-around arrow from 7 back to 0
    p.append(f'<path d="M {x0 + 7*cw + cw/2} {y0-22} Q {W - 30} {y0 - 55} {W/2} {y0 - 55} Q {30} {y0 - 55} {x0 + cw/2} {y0 - 22}" stroke="{FIELD}" fill="none" stroke-width="1.8" stroke-dasharray="4 4"/>')
    p.append(text(W/2, y0 - 40, "модульна арифметика: (index + 1) % N", size=12, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "deque-ring.svg"), W, H, *p)
    print("Generated deque-ring.svg")

def fig_deque_layout():
    """Фігура 2: Дворангова блочна двобічна черга (Карта + Блоки)"""
    W, H = 820, 340
    p = []

    p.append(text(W/2, 30, "Архітектура двобічної черги (карта блоків)", size=16, color=INK, bold=True, anchor="middle"))
    p.append(text(80, 65, "Карта вказівників (Map of Block Pointers):", size=13, color=MUTED, bold=True, anchor="start"))
    
    map_x0, map_y = 80, 85
    map_cw, map_ch = 100, 40
    
    map_blocks = [
        ("NULL", False),
        ("Блок 0", True),
        ("Блок 1", True),
        ("Блок 2", True),
        ("NULL", False)
    ]
    
    for i, (label, active) in enumerate(map_blocks):
        bx = map_x0 + i * map_cw
        fill_col = "#eef4ff" if active else "#f5f7fa"
        stroke_col = FIELD if active else "#d0d7de"
        p.append(rect(bx, map_y, map_cw - 6, map_ch, fill=fill_col, stroke=stroke_col, sw=1.5, rx=4))
        p.append(text(bx + (map_cw - 6)/2, map_y + map_ch/2 + 5, label, size=13, color=INK if active else MUTED, bold=active, anchor="middle"))

    data_y = 200
    chunk_w = 160
    chunk_h = 55
    
    data_chunks = [
        (1, 120, ["", "2", "5"], "голова -> 2"),
        (2, 330, ["10", "20", "30"], "повний блок"),
        (3, 540, ["40", "", ""], "хвіст -> 40")
    ]

    for map_idx, cx, items, note in data_chunks:
        m_x = map_x0 + map_idx * map_cw + (map_cw - 6)/2
        p.append(arrow(m_x, map_y + map_ch, cx + chunk_w/2, data_y - 2, color=FIELD, sw=1.8))
        
        p.append(rect(cx, data_y, chunk_w, chunk_h, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
        
        sub_w = (chunk_w - 12) / 3
        for k, item in enumerate(items):
            sx = cx + 6 + k * sub_w
            sy = data_y + 6
            sh = chunk_h - 12
            cell_fill = "#eafaf0" if item != "" else "#f8f9fa"
            p.append(rect(sx, sy, sub_w - 2, sh, fill=cell_fill, stroke=FIELD if item != "" else "#e1e4e8", sw=1.2, rx=3))
            txt_label = item if item != "" else " "
            p.append(text(sx + (sub_w - 2)/2, sy + sh/2 + 5, txt_label, size=14, color=INK if item != "" else MUTED, bold=(item != ""), anchor="middle"))
        
        p.append(text(cx + chunk_w/2, data_y + chunk_h + 20, note, size=11, color=MUTED, anchor="middle"))

    p.append(text(120 + 20, data_y - 12, "push_front / pop_front", size=11.5, color=POS, bold=True, anchor="middle"))
    p.append(text(540 + 140, data_y - 12, "push_back / pop_back", size=11.5, color=POS, bold=True, anchor="middle"))

    render(os.path.join(OUT, "deque-layout.svg"), W, H, *p)
    print("Generated deque-layout.svg")

def fig_deque_indexing():
    """Фігура 3: Дворанговий розрахунок індексу operator[i]"""
    W, H = 820, 260
    p = []

    p.append(text(W/2, 30, "Дворанговий пошук елемента за індексом i (O(1))", size=16, color=INK, bold=True, anchor="middle"))

    # Step 1: Map lookup
    p.append(rect(60, 70, 320, 70, fill="#f0f4ff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(80, 95, "Крок 1: Номер блоку в Карті", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(80, 120, "map_index = head_map + (offset / BLOCK_SIZE)", size=12, color=FIELD, anchor="start"))

    # Step 2: Block offset lookup
    p.append(rect(440, 70, 320, 70, fill="#eafaf0", stroke=POS, sw=1.5, rx=6))
    p.append(text(460, 95, "Крок 2: Зміщення всередині Блоку", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(460, 120, "elem_index = offset % BLOCK_SIZE", size=12, color=POS, anchor="start"))

    p.append(arrow(382, 105, 438, 105, color=INK, sw=2.0))

    # Target element lookup visualization
    p.append(rect(200, 175, 420, 55, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(text(220, 208, "Результат: 2 зчитування пам'яті (Map -> Block -> Elem)", size=13, color=INK, bold=True, anchor="start"))

    render(os.path.join(OUT, "deque-indexing.svg"), W, H, *p)
    print("Generated deque-indexing.svg")

if __name__ == "__main__":
    fig_deque_ring()
    fig_deque_layout()
    fig_deque_indexing()
