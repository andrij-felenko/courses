# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Двійковий пошук»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — Звуження діапазону пошуку (Bisection)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bisection():
    W, H = 860, 420
    p = []
    
    arr = [2, 5, 8, 12, 16, 23, 38, 45, 56, 67, 78, 89, 90, 92, 95, 99]
    cell_w, cell_h = 44, 36
    x0, y0 = 70, 90
    row_step = 75
    
    # Кроки пошуку елемента 56
    steps = [
        {"low": 0, "high": 15, "mid": 7, "note": "Крок 1: mid=7 (значення 45 < 56) → шукаємо праворуч [8..15]"},
        {"low": 8, "high": 15, "mid": 11, "note": "Крок 2: mid=11 (значення 89 > 56) → шукаємо ліворуч [8..10]"},
        {"low": 8, "high": 10, "mid": 9, "note": "Крок 3: mid=9 (значення 67 > 56) → шукаємо ліворуч [8..8]"},
        {"low": 8, "high": 8, "mid": 8, "note": "Крок 4: mid=8 (значення 56 = 56) → знайдено!"}
    ]
    
    for r_idx, step in enumerate(steps):
        ry = y0 + r_idx * row_step
        low, high, mid = step["low"], step["high"], step["mid"]
        
        # Напис з описом кроку
        p.append(text(x0, ry - 10, step["note"], size=13, color=INK, anchor="start", bold=(r_idx==3)))
        
        for i, val in enumerate(arr):
            cx = x0 + i * cell_w
            
            if i < low or i > high:
                # Поза активним діапазоном (відкинуто)
                f_color = "#e5e7eb"
                s_color = "#d1d5db"
                t_color = MUTED
            elif i == mid:
                # Поточний mid
                if r_idx == 3:
                    f_color = "#eafaf0"
                    s_color = FIELD
                    t_color = FIELD
                else:
                    f_color = "#fdecea"
                    s_color = POS
                    t_color = POS
            else:
                # В активній зоні [low..high]
                f_color = "#eef6ff"
                s_color = NEG
                t_color = INK
                
            p.append(rect(cx, ry, cell_w, cell_h, fill=f_color, stroke=s_color, sw=1.5, rx=3))
            p.append(text(cx + cell_w/2, ry + cell_h/2 + 4, str(val), size=13, color=t_color, bold=(i==mid)))
            
            # Підписи low, high, mid
            if r_idx < 3:
                pointers = []
                if i == low: pointers.append("L")
                if i == high: pointers.append("H")
                if i == mid: pointers.append("M")
                if pointers:
                    lbl = ",".join(pointers)
                    p.append(text(cx + cell_w/2, ry + cell_h + 15, lbl, size=11, color=LINE, bold=True))

    render(os.path.join(OUT, "fig1-bisection.svg"), W, H, *p,
           title="Звуження діапазону пошуку в масиві з 16 елементів (шукаємо 56)")

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — Дерево рішень двійкового пошуку для N = 7
# ─────────────────────────────────────────────────────────────────────────────
def fig_decision_tree():
    W, H = 840, 380
    p = []
    
    nodes = [
        {"id": "3", "x": 420, "y": 80, "val": "A[3]", "lvl": "Порівняння 1"},
        {"id": "1", "x": 220, "y": 160, "val": "A[1]", "lvl": "Порівняння 2"},
        {"id": "5", "x": 620, "y": 160, "val": "A[5]", "lvl": "Порівняння 2"},
        {"id": "0", "x": 120, "y": 250, "val": "A[0]", "lvl": "Порівняння 3"},
        {"id": "2", "x": 320, "y": 250, "val": "A[2]", "lvl": "Порівняння 3"},
        {"id": "4", "x": 520, "y": 250, "val": "A[4]", "lvl": "Порівняння 3"},
        {"id": "6", "x": 720, "y": 250, "val": "A[6]", "lvl": "Порівняння 3"},
    ]
    
    edges = [
        ("3", "1", "< target"),
        ("3", "5", "> target"),
        ("1", "0", "< target"),
        ("1", "2", "> target"),
        ("5", "4", "< target"),
        ("5", "6", "> target"),
    ]
    
    node_map = {n["id"]: n for n in nodes}
    
    # Ребра
    for src, dst, lbl in edges:
        n1 = node_map[src]
        n2 = node_map[dst]
        p.append(line(n1["x"], n1["y"], n2["x"], n2["y"], color="#9ca3af", sw=1.8))
        mx, my = (n1["x"] + n2["x"])/2, (n1["y"] + n2["y"])/2
        p.append(text(mx, my - 6, lbl, size=11, color=MUTED))
        
    # Вузли
    for n in nodes:
        bx = fitbox(n["x"] - 40, n["y"] - 18, 80, 36, n["val"], size=14, pad=6, fill="#eef6ff", stroke=NEG, bold=True)
        p.append(bx)
        
    # Пояснення висоти
    p.append(line(50, 60, 50, 270, color=FIELD, sw=2, dash="4,4"))
    p.append(text(40, 165, "Висота H = 3 = ⌈log₂ (7 + 1)⌉", size=13, color=FIELD, bold=True, anchor="end"))
    
    p.append(text(420, 330, "Для масиву з N = 7 елементів достатньо максимум 3 порівнянь у найгіршому випадку", size=13, color=INK))

    render(os.path.join(OUT, "fig2-decision-tree.svg"), W, H, *p,
           title="Дерево рішень двійкового пошуку для 7 елементів")

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — Переповнення (low + high) / 2
# ─────────────────────────────────────────────────────────────────────────────
def fig_overflow():
    W, H = 840, 360
    p = []
    
    # Лівий блок — з переповненням
    bx1, w1, h1 = textbox(230, 140,
        "Некоректний розрахунок:\n\n"
        "low = 1,500,000,000\n"
        "high = 1,000,000,000\n\n"
        "low + high = 2,500,000,000\n"
        "(> INT_MAX = 2,147,483,647!)\n\n"
        "Переповнення 32-біт signed int:\n"
        "low + high = -1,794,967,296\n"
        "mid = -897,483,648  ❌\n"
        "Призводить до ArrayIndexOutOfBoundsException!",
        size=13, pad=14, fill="#fdecea", stroke=POS, sw=1.8, color=INK)
    p.append(bx1)
    
    # Правий блок — безпечний розрахунок
    bx2, w2, h2 = textbox(610, 140,
        "Безпечний розрахунок:\n\n"
        "low = 1,500,000,000\n"
        "high = 1,000,000,000\n\n"
        "high - low = 500,000,000\n"
        "(high - low) / 2 = 250,000,000\n\n"
        "low + (high - low) / 2:\n"
        "= 1,500,000,000 + 250,000,000\n"
        "mid = 1,750,000,000  ✓\n"
        "Ніколи не переповнює діапазон int!",
        size=13, pad=14, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK)
    p.append(bx2)
    
    p.append(text(420, 315, "Баг Джонса (2006): чому (low + high) / 2 небезпечний у мовах зі скінченними цілими типами", size=13, color=INK, bold=True))

    render(os.path.join(OUT, "fig3-overflow-bug.svg"), W, H, *p,
           title="Переповнення при обчисленні середини діапазону")

if __name__ == "__main__":
    fig_bisection()
    fig_decision_tree()
    fig_overflow()
    print("Figures for binary-search generated successfully in", OUT)
