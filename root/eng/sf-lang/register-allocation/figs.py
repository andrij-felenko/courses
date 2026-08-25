# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ──────────────────────────────────────────────────────────
COLOR_R0_BG   = "#fee2e2"   # Червоний/Рожевий для регістру R0
BORDER_R0     = "#dc2626"
COLOR_R1_BG   = "#eaf7ee"   # Зелений для регістру R1
BORDER_R1     = "#27ae60"
COLOR_R2_BG   = "#dbeafe"   # Синій для регістру R2
BORDER_R2     = "#2563eb"
COLOR_SPILL_BG = "#fef3c7"  # Жовтий для скинутих у пам'ять змінних (Spill)
BORDER_SPILL   = "#d97706"

COLOR_NODE_BG = "#f4f6f8"
BORDER_NORMAL = "#333333"

def node(cx, cy, label, fill=COLOR_NODE_BG, stroke=BORDER_NORMAL, r=22, extra_sub=None):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, label, size=15, color=INK, bold=True)
    if extra_sub:
        out += text(cx, cy + r + 15, extra_sub, size=11, color=MUTED, bold=True)
    return out

def edge_line(x1, y1, x2, y2, r1=22, r2=22, col=BORDER_NORMAL, sw=1.8):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    return line(ax, ay, bx, by, color=col, sw=sw)

def path_arc(d_attr, stroke=BORDER_NORMAL, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_attr}" fill="none" stroke="{stroke}" stroke-width="{sw}"{d}/>'

# ── ФІГ.1 Граф інтерференції та розфарбування ───────────────────────────────
def fig_interference_graph():
    path = os.path.join(OUT, "interference-graph.svg")
    W, H = 760, 320
    p = []
    
    # Заголовок
    p.append(text(210, 25, "Діапазони життя змінних (Live Ranges)", size=14, color=INK, bold=True))
    p.append(text(570, 25, "Граф інтерференції (K = 3)", size=14, color=INK, bold=True))
    
    # Ліва частина: Інтервали життєвості
    # Шкала часу
    p.append(line(50, 260, 370, 260, color=MUTED, sw=1.5))
    for t in range(1, 6):
        tx = 50 + t * 55
        p.append(line(tx, 255, tx, 265, color=MUTED, sw=1.5))
        p.append(text(tx, 280, f"i{t}", size=11, color=MUTED))
    p.append(text(385, 264, "t", size=12, color=MUTED, bold=True))
    
    intervals = [
        ("v1", 1, 3, COLOR_R0_BG, BORDER_R0, "R0"),
        ("v2", 2, 4, COLOR_R1_BG, BORDER_R1, "R1"),
        ("v3", 1, 5, COLOR_R2_BG, BORDER_R2, "R2"),
        ("v4", 4, 5, COLOR_R0_BG, BORDER_R0, "R0"),
        ("v5", 3, 5, COLOR_R1_BG, BORDER_R1, "R1")
    ]
    
    for idx, (vname, start, end, bg, brd, rname) in enumerate(intervals):
        y = 55 + idx * 38
        x1 = 50 + start * 55
        x2 = 50 + end * 55
        p.append(rect(x1, y - 12, x2 - x1, 24, fill=bg, stroke=brd, sw=1.5, rx=4))
        p.append(text(x1 + 15, y + 4, f"{vname} ({rname})", size=11, color=INK, bold=True, anchor="start"))
    
    # Розділювач
    p.append(line(410, 30, 410, 290, color="#e2e8f0", sw=1.5, dash="4,4"))
    
    # Права частина: Граф інтерференції
    coords = {
        "v1": (490, 80),
        "v2": (650, 80),
        "v3": (570, 160),
        "v4": (490, 240),
        "v5": (650, 240)
    }
    
    colors_map = {
        "v1": (COLOR_R0_BG, BORDER_R0, "R0"),
        "v2": (COLOR_R1_BG, BORDER_R1, "R1"),
        "v3": (COLOR_R2_BG, BORDER_R2, "R2"),
        "v4": (COLOR_R0_BG, BORDER_R0, "R0"),
        "v5": (COLOR_R1_BG, BORDER_R1, "R1")
    }
    
    edges = [
        ("v1", "v2"), ("v1", "v3"),
        ("v2", "v3"), ("v2", "v5"),
        ("v3", "v4"), ("v3", "v5"),
        ("v4", "v5")
    ]
    
    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        p.append(edge_line(x1, y1, x2, y2, r1=22, r2=22, col=BORDER_NORMAL, sw=1.8))
        
    for name, (cx, cy) in coords.items():
        bg, brd, rname = colors_map[name]
        p.append(node(cx, cy, name, fill=bg, stroke=brd, r=22))
        p.append(text(cx, cy + 33, rname, size=11, color=brd, bold=True))
        
    # Нижня пояснювальна картка
    b, bw, bh = textbox(W / 2, 305,
                        "Перетин діапазонів життєвості створює ребро інтерференції. Сусідні вершини отримують різні регістри R0, R1, R2.",
                        size=11, pad=6, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path, W, H, *p)

# ── ФІГ.2 Конвеєр Chaitin-Briggs ──────────────────────────────────────────────
def fig_chaitin_briggs():
    path = os.path.join(OUT, "chaitin-briggs-simplify.svg")
    W, H = 760, 300
    p = []
    
    p.append(text(W / 2, 22, "Конвеєр алгоритму розфарбування графів Чейтіна–Бріґґса", size=14, color=INK, bold=True))
    
    steps = [
        ("1. Побудова", "Граф інтерференції\nLive Ranges + IR"),
        ("2. Спрощення", "Вилучення deg < K\nPush у стек S"),
        ("3. Спихання", "Якщо deg ≥ K\nПотенційний Spill"),
        ("4. Вибір кольору", "Pop зі стеку S\nОптимістичний Color"),
        ("5. Переписання", "Якщо фактичний Spill\nСтек пам'яті + Reload")
    ]
    
    x_start = 75
    dx = 145
    y = 120
    
    for i, (title, desc) in enumerate(steps):
        cx = x_start + i * dx
        bg = COLOR_SPILL_BG if i == 2 else (COLOR_R1_BG if i == 3 else FILL)
        brd = BORDER_SPILL if i == 2 else (BORDER_R1 if i == 3 else BORDER_NORMAL)
        
        b, bw, bh = textbox(cx, y, f"{title}\n{desc}", size=11, pad=8, fill=bg, stroke=brd, min_w=125)
        p.append(b)
        
        if i < len(steps) - 1:
            p.append(arrow(cx + bw / 2 + 2, y, cx + dx - bw / 2 - 2, y, color=BORDER_NORMAL, sw=1.8))
            
    # Зворотна петля оптимістичного розфарбування / повторного циклу
    p.append(path_arc(f"M 510,165 C 510,230 220,230 220,165", stroke=BORDER_SPILL, sw=1.5, dash="4,4"))
    p.append(text(365, 238, "Якщо виявлено факт Spill → вставити Store/Load і повторити (Re-iterative Spill)", size=10, color=BORDER_SPILL, bold=True))
    
    b2, _, _ = textbox(W / 2, 280,
                       "Спрощення спирається на правило Кемпе: вершина з ступенем deg(v) < K не може заблокувати розфарбування решти графа.",
                       size=11, pad=6, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b2)
    
    render(path, W, H, *p)

# ── ФІГ.3 Linear Scan ────────────────────────────────────────────────────────
def fig_linear_scan():
    path = os.path.join(OUT, "linear-scan-intervals.svg")
    W, H = 760, 300
    p = []
    
    p.append(text(W / 2, 22, "Алгоритм Linear Scan (K = 2 physical registers)", size=14, color=INK, bold=True))
    
    # Інтервали
    intervals = [
        ("x", 20, 180, "R0", COLOR_R0_BG, BORDER_R0),
        ("y", 60, 280, "R1", COLOR_R1_BG, BORDER_R1),
        ("z", 140, 380, "Spill [rsp+8]", COLOR_SPILL_BG, BORDER_SPILL),
        ("w", 220, 440, "R0", COLOR_R0_BG, BORDER_R0),
        ("t", 320, 520, "R1", COLOR_R1_BG, BORDER_R1)
    ]
    
    y_start = 60
    for idx, (name, x1, x2, reg, bg, brd) in enumerate(intervals):
        y = y_start + idx * 35
        p.append(rect(100 + x1, y - 10, x2 - x1, 22, fill=bg, stroke=brd, rx=4))
        p.append(text(100 + x1 + 10, y + 4, f"{name}: [{x1},{x2}] → {reg}", size=11, color=INK, bold=True, anchor="start"))
        
    # Лінія сканування (Scan position)
    p.append(line(250, 45, 250, 235, color=POS, sw=2.0, dash="3,3"))
    p.append(text(250, 40, "Позиція сканування t=150", size=11, color=POS, bold=True))
    
    # Картка пояснення
    b, _, _ = textbox(W / 2, 265,
                      "В точці t=150 активні x, y та z. Оскільки K=2, інтервал z з найдовшим залишком [140,380] скидається в стек (Spill).\n"
                      "Складність O(N log N) замість O(N²) — ідеально для JIT-компіляторів (V8, JVM HotSpot C1).",
                      size=11, pad=8, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b)
    
    render(path, W, H, *p)

# ── ФІГ.4 SSA & Хордальні графи ──────────────────────────────────────────────
def fig_ssa_chordal():
    path = os.path.join(OUT, "ssa-chordal-coloring.svg")
    W, H = 760, 310
    p = []
    
    p.append(text(W / 2, 22, "Розподіл регістрів у SSA-формі: Хордальні графи", size=14, color=INK, bold=True))
    
    # Лівий блок: Звичайний IR (NP-повна задача)
    p.append(text(200, 50, "Загальний IR (Довільний граф)", size=13, color=INK, bold=True))
    b1, _, _ = textbox(200, 130,
                       "Цикли C_n без хорд (n ≥ 4)\n"
                       "Граф інтерференції може бути будь-яким\n"
                       "Розфарбування NP-повне (Chaitin 1981)",
                       size=11, pad=10, fill=COLOR_SPILL_BG, stroke=BORDER_SPILL)
    p.append(b1)
    
    # Стрілка
    p.append(arrow(340, 130, 410, 130, color=BORDER_NORMAL, sw=2.0))
    p.append(text(375, 115, "SSA Transformation", size=10, color=MUTED, bold=True))
    
    # Правий блок: SSA IR (Поліноміальний час)
    p.append(text(560, 50, "SSA-форма (Хордальний граф)", size=13, color=INK, bold=True))
    b2, _, _ = textbox(560, 130,
                       "Кожен цикл довжиною ≥ 4 має хорду\n"
                       "Інтервальний / Хордальний граф\n"
                       "Розфарбування за O(|V| + |E|) через PEO\n"
                       "(Hack 2006, Pereyron et al.)",
                       size=11, pad=10, fill=COLOR_R1_BG, stroke=BORDER_R1)
    p.append(b2)
    
    b3, _, _ = textbox(W / 2, 260,
                       "В SSA-формі кожна змінна призначається строго один раз. Діапазони життєвості утворюють дерево вкладеності,\n"
                       "що робить граф інтерференції хордальним і дозволяє точне розфарбування за поліноміальний час.",
                       size=11, pad=8, fill=FILL, stroke=BORDER_NORMAL)
    p.append(b3)
    
    render(path, W, H, *p)

if __name__ == "__main__":
    fig_interference_graph()
    fig_chaitin_briggs()
    fig_linear_scan()
    fig_ssa_chordal()
    print("Figures generated successfully.")
