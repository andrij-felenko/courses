# -*- coding: utf-8 -*-
"""Фігури до статті «Сортувальні мережі». Запуск: python figs.py
Виводить SVG у ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 64, 34
COLOR_WIRE = "#4b5563"
COLOR_COMP = "#2563eb"
COLOR_DOT  = "#1e40af"
COLOR_BOX  = "#f3f4f6"
COLOR_ACTIVE = "#dbeafe"

def cell(x, y, label, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.5, tcolor=INK, tsize=14, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=5)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out

# ── Фігура 1: Принцип дії сортувальної мережі ───────────────────────────────
def fig_comparator_wire():
    W, H = 820, 440
    parts = []
    parts.append(text(W / 2, 34, "Сортувальна мережа для N = 4 дротів (глибина D = 3, розмір S = 5)", size=16, bold=True))
    
    # 4 горизонтальні проводи
    wires_y = [110, 180, 250, 320]
    x_start = 140
    x_end = 700
    
    # Підписи дротів та вхідні значення
    inputs = [7, 3, 9, 1]
    stage1_vals = [3, 7, 1, 9]
    stage2_vals = [1, 7, 3, 9]
    outputs = [1, 3, 7, 9]
    
    for i, y in enumerate(wires_y):
        parts.append(line(x_start, y, x_end, y, color=COLOR_WIRE, sw=2.2))
        parts.append(text(x_start - 75, y + 5, "дріт %d" % i, size=13, color=MUTED, anchor="end"))
        parts.append(cell(x_start - 60, y - CH / 2, str(inputs[i]), w=42, h=CH, fill=COLOR_ACTIVE, tcolor=NEG, bold=True))
        parts.append(cell(x_end + 18, y - CH / 2, str(outputs[i]), w=42, h=CH, fill="#dcfce7", tcolor=FIELD, bold=True))

    # Сонця/етапи (вертикальні пунктири та підписи)
    stages_x = [250, 400, 550]
    for s_idx, sx in enumerate(stages_x):
        parts.append(line(sx, 75, sx, 355, color="#d1d5db", sw=1.2, dash="4,4"))
        parts.append(text(sx, 65, "Такт %d" % (s_idx + 1), size=13, color=MUTED, bold=True))

    # Такт 1: компаратор (0,1) та (2,3)
    # (0,1)
    x1 = stages_x[0]
    parts.append(line(x1, wires_y[0], x1, wires_y[1], color=COLOR_COMP, sw=2.6))
    parts.append(circle(x1, wires_y[0], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(circle(x1, wires_y[1], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(text(x1 - 18, (wires_y[0] + wires_y[1]) / 2 + 4, "min/max", size=11, color=COLOR_COMP, anchor="end"))
    
    # (2,3)
    parts.append(line(x1, wires_y[2], x1, wires_y[3], color=COLOR_COMP, sw=2.6))
    parts.append(circle(x1, wires_y[2], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(circle(x1, wires_y[3], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(text(x1 - 18, (wires_y[2] + wires_y[3]) / 2 + 4, "min/max", size=11, color=COLOR_COMP, anchor="end"))

    # Значення після такту 1
    for i, y in enumerate(wires_y):
        parts.append(text(x1 + 65, y - 10, str(stage1_vals[i]), size=12.5, color=INK, bold=True))

    # Такт 2: компаратор (0,2) та (1,3)
    x2 = stages_x[1]
    # (0,2)
    parts.append(line(x2, wires_y[0], x2, wires_y[2], color=COLOR_COMP, sw=2.6))
    parts.append(circle(x2, wires_y[0], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(circle(x2, wires_y[2], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    
    # (1,3)
    parts.append(line(x2 + 15, wires_y[1], x2 + 15, wires_y[3], color=COLOR_COMP, sw=2.6))
    parts.append(circle(x2 + 15, wires_y[1], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(circle(x2 + 15, wires_y[3], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Значення після такту 2
    for i, y in enumerate(wires_y):
        parts.append(text(x2 + 65, y - 10, str(stage2_vals[i]), size=12.5, color=INK, bold=True))

    # Такт 3: компаратор (1,2)
    x3 = stages_x[2]
    parts.append(line(x3, wires_y[1], x3, wires_y[2], color=COLOR_COMP, sw=2.6))
    parts.append(circle(x3, wires_y[1], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(circle(x3, wires_y[2], 5.5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Легенда знизу
    parts.append(rect(140, 375, 540, 48, fill="#f9fafb", stroke="#e5e7eb", rx=6))
    parts.append(circle(165, 399, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
    parts.append(line(165, 387, 165, 411, color=COLOR_COMP, sw=2))
    parts.append(text(180, 403, "Компаратор: менший елемент іде на верхній дріт, більший — на нижній", size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "comparator-wire.svg"), W, H, *parts)

# ── Фігура 2: Теорема 0-1 ───────────────────────────────────────────────────
def fig_zero_one():
    W, H = 840, 460
    parts = []
    parts.append(text(W / 2, 34, "Теорема 0-1: збереження порядку при монотонному відображенні f(x)", size=16, bold=True))
    
    # Верхня частина: Дійсні числа
    parts.append(text(120, 80, "Дійсні значення X:", size=14, bold=True, anchor="start"))
    vals_real = [7.2, 3.1, 9.5, 1.4]
    rx_start = 320
    for i, v in enumerate(vals_real):
        parts.append(cell(rx_start + i * 110, 62, "%.1f" % v, w=70, h=36, fill=COLOR_ACTIVE, tcolor=NEG, bold=True))

    # Стрілка відображення f(x)
    parts.append(line(W / 2, 112, W / 2, 148, color=POS, sw=2))
    parts.append(arrow(W / 2, 112, W / 2, 148, color=POS, sw=2))
    parts.append(text(W / 2 + 15, 134, "f(x) = 1 при x ≥ 5.0,  0 при x < 5.0", size=13, color=POS, anchor="start", bold=True))

    # Нижня частина: Бінарні значення 0-1
    parts.append(text(120, 185, "Бінарні значення B = f(X):", size=14, bold=True, anchor="start"))
    vals_bin = [1, 0, 1, 0]
    for i, v in enumerate(vals_bin):
        fill_col = "#fdecea" if v == 1 else "#eaf0fd"
        txt_col = POS if v == 1 else NEG
        parts.append(cell(rx_start + i * 110, 167, str(v), w=70, h=36, fill=fill_col, tcolor=txt_col, bold=True))

    # Блок доведення рівності для компаратора
    bx, by, bw, bh = 100, 235, 640, 140
    parts.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    parts.append(text(W / 2, by + 28, "Основна властивість монотонної неспадної функції f:", size=14, bold=True, color=INK))
    
    eq1 = "f( min(a, b) )  =  min( f(a), f(b) )"
    eq2 = "f( max(a, b) )  =  max( f(a), f(b) )"
    parts.append(text(W / 2, by + 65, eq1, size=14, bold=True, color=NEG))
    parts.append(text(W / 2, by + 98, eq2, size=14, bold=True, color=NEG))

    # Підсумок
    parts.append(text(W / 2, 420, "Якщо мережа сортує всі 2ⁿ бінарних векторів → вона сортує будь-які дійсні числа!", size=13.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "zero-one-principle.svg"), W, H, *parts)

# ── Фігура 3: Бітонічна сортувальна мережа N=8 ─────────────────────────────
def fig_bitonic_network():
    W, H = 920, 520
    parts = []
    parts.append(text(W / 2, 32, "Бітонічна сортувальна мережа Батчера (Bitonic Sort) для N = 8", size=16, bold=True))
    
    wires_y = [80 + i * 48 for i in range(8)]
    x_start = 110
    x_end = 830
    
    for i, y in enumerate(wires_y):
        parts.append(line(x_start, y, x_end, y, color=COLOR_WIRE, sw=2.0))
        parts.append(text(x_start - 25, y + 4, "%d" % i, size=13, color=MUTED, anchor="end"))

    # Фаза 1: Блоки по 2 (Такт 1)
    # Зростання (0,1), Спадання (2,3), Зростання (4,5), Спадання (6,7)
    x_t1 = 200
    parts.append(line(x_t1, 60, x_t1, 430, color="#e5e7eb", sw=1, dash="4,4"))
    parts.append(text(x_t1, 50, "Такт 1", size=12, color=MUTED, bold=True))
    
    comp_t1 = [(0,1), (2,3), (4,5), (6,7)]
    for w1, w2 in comp_t1:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t1, y1, x_t1, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t1, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t1, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Фаза 2: Блоки по 4 (Такт 2, Такт 3)
    x_t2 = 330
    x_t3 = 430
    parts.append(line(x_t2, 60, x_t2, 430, color="#e5e7eb", sw=1, dash="4,4"))
    parts.append(text(x_t2, 50, "Такт 2", size=12, color=MUTED, bold=True))
    parts.append(line(x_t3, 60, x_t3, 430, color="#e5e7eb", sw=1, dash="4,4"))
    parts.append(text(x_t3, 50, "Такт 3", size=12, color=MUTED, bold=True))
    
    # Такт 2: (0,3), (1,2), (4,7), (5,6)
    comp_t2 = [(0,3), (1,2), (4,7), (5,6)]
    for w1, w2 in comp_t2:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t2, y1, x_t2, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t2, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t2, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        
    # Такт 3: (0,1), (2,3), (4,5), (6,7)
    for w1, w2 in comp_t1:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t3, y1, x_t3, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t3, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t3, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Фаза 3: Блок 8 (Такт 4, Такт 5, Такт 6)
    x_t4 = 560
    x_t5 = 660
    x_t6 = 760
    for xt, num in [(x_t4, 4), (x_t5, 5), (x_t6, 6)]:
        parts.append(line(xt, 60, xt, 430, color="#e5e7eb", sw=1, dash="4,4"))
        parts.append(text(xt, 50, "Такт %d" % num, size=12, color=MUTED, bold=True))

    # Такт 4: (0,4), (1,5), (2,6), (3,7)
    comp_t4 = [(0,4), (1,5), (2,6), (3,7)]
    for w1, w2 in comp_t4:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t4, y1, x_t4, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t4, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t4, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Такт 5: (0,2), (1,3), (4,6), (5,7)
    comp_t5 = [(0,2), (1,3), (4,6), (5,7)]
    for w1, w2 in comp_t5:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t5, y1, x_t5, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t5, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t5, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Такт 6: (0,1), (2,3), (4,5), (6,7)
    for w1, w2 in comp_t1:
        y1, y2 = wires_y[w1], wires_y[w2]
        parts.append(line(x_t6, y1, x_t6, y2, color=COLOR_COMP, sw=2.4))
        parts.append(circle(x_t6, y1, 5, fill=COLOR_DOT, stroke=COLOR_DOT))
        parts.append(circle(x_t6, y2, 5, fill=COLOR_DOT, stroke=COLOR_DOT))

    # Підписи під етапами
    parts.append(text((x_t1), 448, "Крок 1 (довжина 2)", size=12, color=NEG, bold=True))
    parts.append(text((x_t2 + x_t3)/2, 448, "Крок 2 (довжина 4)", size=12, color=NEG, bold=True))
    parts.append(text((x_t4 + x_t6)/2, 448, "Крок 3 (довжина 8 — підсумкове злиття)", size=12, color=FIELD, bold=True))
    
    parts.append(text(W / 2, 485, "Всього компараторів S = 19, Паралельна глибина D = 6 тактів", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "bitonic-network.svg"), W, H, *parts)

if __name__ == "__main__":
    fig_comparator_wire()
    fig_zero_one()
    fig_bitonic_network()
    print("OK: 3 SVG згенеровано у", IMG)
