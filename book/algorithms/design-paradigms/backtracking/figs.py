# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/algorithms/design-paradigms/backtracking/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_tree_diagram():
    path = os.path.join(os.path.dirname(__file__), 'img', 'fig1-backtracking-tree.svg')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    w, h = 760, 420
    
    # Title
    t_title = text(w / 2, 28, "Дерево простору станів та відтинання гілок (Pruning)", size=16, bold=True)
    
    # Nodes geometry
    # Level 0 (Root)
    r_box, _, _ = textbox(380, 70, "Корінь: порожній стан []", size=13, fill="#eef2ff", stroke="#3b82f6", bold=True, pad=8)
    
    # Level 1
    n11, _, _ = textbox(190, 150, "Крок 1: Варіант A", size=12, fill="#f4f6f8", stroke="#6b7280", pad=6)
    n12, _, _ = textbox(570, 150, "Крок 1: Варіант B", size=12, fill="#f4f6f8", stroke="#6b7280", pad=6)
    
    # Level 2
    n21, _, _ = textbox(100, 240, "Крок 2: A1 (Конфлікт!)", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, pad=6)
    n22, _, _ = textbox(280, 240, "Крок 2: A2 (ОК)", size=11, fill="#f4f6f8", stroke="#6b7280", pad=6)
    n23, _, _ = textbox(490, 240, "Крок 2: B1 (Конфлікт!)", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, pad=6)
    n24, _, _ = textbox(660, 240, "Крок 2: B2 (ОК)", size=11, fill="#f4f6f8", stroke="#6b7280", pad=6)
    
    # Level 3
    n31, _, _ = textbox(280, 330, "Крок 3: A2.1 (Розв'язок!)", size=11, fill="#e8f8f0", stroke=FIELD, color=FIELD, bold=True, pad=6)
    
    # Pruned subtrees visual indicator (Crosses / Pruned labels)
    pruned_box1, _, _ = textbox(100, 310, "Гілка відтята (Pruned)\nнемає сенсу іти далі", size=10, fill="#fff5f5", stroke="#feb2b2", color=POS, pad=5)
    pruned_box2, _, _ = textbox(490, 310, "Гілка відтята (Pruned)", size=10, fill="#fff5f5", stroke="#feb2b2", color=POS, pad=5)
    
    # Connectors
    # Root to Level 1
    a01 = arrow(340, 85, 220, 135, color="#6b7280", sw=1.5)
    a02 = arrow(420, 85, 540, 135, color="#6b7280", sw=1.5)
    
    # Level 1 to Level 2
    a11 = arrow(165, 165, 120, 225, color=POS, sw=1.5)
    a12 = arrow(215, 165, 260, 225, color="#6b7280", sw=1.5)
    a13 = arrow(545, 165, 510, 225, color=POS, sw=1.5)
    a14 = arrow(595, 165, 640, 225, color="#6b7280", sw=1.5)
    
    # Level 2 to Level 3
    a22 = arrow(280, 255, 280, 315, color=FIELD, sw=2.0)
    
    # Pruning lines (Level 2 to Pruned boxes)
    p_line1 = line(100, 255, 100, 290, color=POS, sw=1.5, dash="3,3")
    p_line2 = line(490, 255, 490, 290, color=POS, sw=1.5, dash="3,3")
    
    # Backtrack arrows (Curved/Dashed arrow indicating backtracking)
    bt_arrow1 = arrow(100, 225, 175, 165, color=POS, sw=1.8) # Backtrack from A1 to A
    lbl_bt1 = text(120, 185, "Backtrack", size=10, color=POS, bold=True)
    
    bt_arrow2 = arrow(490, 225, 555, 165, color=POS, sw=1.8) # Backtrack from B1 to B
    lbl_bt2 = text(505, 185, "Backtrack", size=10, color=POS, bold=True)

    # Legend / Explanations at bottom
    leg1, _, _ = textbox(160, 385, "🔴 Конфлікт / Відтинання", size=11, fill="#fdecea", stroke=POS, color=POS, pad=4)
    leg2, _, _ = textbox(380, 385, "🟢 Знайдений розв'язок", size=11, fill="#e8f8f0", stroke=FIELD, color=FIELD, pad=4)
    leg3, _, _ = textbox(600, 385, "↖ Повернення (Backtrack)", size=11, fill="#ffffff", stroke="#6b7280", color=INK, pad=4)

    render(path, w, h, t_title, r_box, n11, n12, n21, n22, n23, n24, n31, pruned_box1, pruned_box2,
           a01, a02, a11, a12, a13, a14, a22, p_line1, p_line2, bt_arrow1, bt_arrow2, lbl_bt1, lbl_bt2,
           leg1, leg2, leg3)

def generate_nqueens_diagram():
    path = os.path.join(os.path.dirname(__file__), 'img', 'fig2-nqueens-pruning.svg')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    w, h = 760, 360
    
    t_title = text(w / 2, 25, "Приклад відтинання в задачі 4-Ферзів на шахівниці", size=16, bold=True)
    
    # Draw 4x4 Chessboard sub-panels
    def draw_board(cx, cy, queens, attacked, title_str):
        size = 32
        x0 = cx - 2 * size
        y0 = cy - 2 * size
        frags = []
        # Title above board
        tb, _, _ = textbox(cx, cy - 75, title_str, size=12, fill="#ffffff", stroke="#333333", bold=True, pad=5)
        frags.append(tb)
        
        # Grid
        for r in range(4):
            for c in range(4):
                bx = x0 + c * size
                by = y0 + r * size
                is_dark = (r + c) % 2 == 1
                bg_col = "#e2e8f0" if is_dark else "#ffffff"
                
                # Check if cell is attacked
                if (r, c) in attacked:
                    bg_col = "#fdecea"
                
                frags.append(rect(bx, by, size, size, fill=bg_col, stroke="#cbd5e1", sw=1.0, rx=0))
                
                # If Queen is present
                if (r, c) in queens:
                    frags.append(text(bx + size / 2, by + size / 2 + 5, "♛", size=20, color="#1e293b", anchor="middle", bold=True))
                elif (r, c) in attacked:
                    frags.append(text(bx + size / 2, by + size / 2 + 4, "×", size=18, color=POS, anchor="middle", bold=True))
        return frags

    # Panel 1: Step 1 - Queen placed at (0,0)
    p1 = draw_board(130, 180, [(0, 0)], [(1, 0), (1, 1), (2, 0), (3, 0), (2, 2), (3, 3)], "Крок 1: Ферзь у (0,0)\nАтаковані клітинки")
    
    # Panel 2: Step 2 - Trying row 1 candidates. (1,0) and (1,1) attacked. Placement at (1,2)
    p2 = draw_board(380, 180, [(0, 0), (1, 2)], [(2, 0), (2, 1), (2, 2), (2, 3), (3, 2)], "Крок 2: Спроба (1,2)\nРядок 2 повністю під атакою!")
    
    # Panel 3: Step 3 - Pruning & Backtrack indicator
    p3 = draw_board(630, 180, [(0, 0)], [], "Крок 3: Глухий кут!\nBacktrack до рядка 0")
    
    # Arrows between boards
    arr1 = arrow(210, 180, 290, 180, color="#6b7280", sw=1.8)
    arr2 = arrow(460, 180, 540, 180, color=POS, sw=1.8)
    lbl_arr2 = text(500, 165, "Відтинання!", size=11, color=POS, bold=True)
    
    # Bottom summary box
    summary_box, _, _ = textbox(w / 2, 320, "Жодна клітинка у рядку 2 не є безпечною → дерево відтинається на глибині 2 без подальшої перевірки рядка 3.", size=12, fill="#f8fafc", stroke="#64748b", pad=6)

    all_frags = [t_title] + p1 + p2 + p3 + [arr1, arr2, lbl_arr2, summary_box]
    render(path, w, h, *all_frags)

if __name__ == "__main__":
    generate_tree_diagram()
    generate_nqueens_diagram()
    print("Figures generated successfully.")
