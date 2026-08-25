# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def generate_memory_layout():
    w, h = 800, 240
    out = []
    
    # Заголовок
    out.append(text(w / 2, 25, "Розміщення масиву int A[5] у фізичній пам'яті та кеш-лінії (64 байти)", size=15, bold=True))
    
    # Кеш-лінія (рамка навколо)
    cl_x, cl_y, cl_w, cl_h = 40, 50, 720, 145
    out.append(rect(cl_x, cl_y, cl_w, cl_h, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    out.append(text(cl_x + 15, cl_y + 22, "Кеш-лінія процесора (64 байти)", size=12, color=NEG, bold=True, anchor="start"))
    
    # Блоки елементів масиву
    elem_w = 110
    elem_h = 60
    start_x = 65
    start_y = 90
    
    elements = [
        ("A[0]", "10", "0x1000"),
        ("A[1]", "25", "0x1004"),
        ("A[2]", "-7", "0x1008"),
        ("A[3]", "42", "0x100C"),
        ("A[4]", "0",  "0x1010")
    ]
    
    for i, (name, val, addr) in enumerate(elements):
        x = start_x + i * (elem_w + 12)
        y = start_y
        
        # Комірка пам'яті
        out.append(rect(x, y, elem_w, elem_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
        
        # Назва та значення
        out.append(text(x + elem_w / 2, y + 22, f"{name} = {val}", size=13, bold=True))
        # Розмір
        out.append(text(x + elem_w / 2, y + 42, "4 байти", size=11, color=MUTED))
        
        # Адреса під коміркою
        out.append(text(x + elem_w / 2, y + elem_h + 18, addr, size=11, color=POS, bold=True))
        
        # Стрілка звідси до наступної комірки
        if i < 4:
            arrow_x1 = x + elem_w
            arrow_x2 = x + elem_w + 12
            out.append(line(arrow_x1, y + elem_h / 2, arrow_x2, y + elem_h / 2, color=MUTED, sw=1))
            
    # Формула адресації під графіком
    formula_text = "Формула адресації: Адреса(A[i]) = BaseAddress + i × sizeof(int)  ⇒  0x1000 + i × 4"
    out.append(rect(160, 205, 480, 28, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    out.append(text(w / 2, 223, formula_text, size=12, color=INK, bold=True))
    
    body = "".join(out)
    vx, vy, vw, vh = svgkit._fit_viewbox(body, w, h)
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" '
        f'width="{vw:.1f}" height="{vh:.1f}">\n'
        f'<defs>\n'
        f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
        f'  </marker>\n'
        f'</defs>\n'
        f'<rect width="100%" height="100%" fill="{BG}"/>\n'
        f'{body}\n'
        f'</svg>'
    )
    with open(os.path.join(IMG_DIR, 'memory-layout.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_content)

def generate_multidimensional_indexing():
    w, h = 840, 310
    out = []
    
    out.append(text(w / 2, 22, "Розкладка двовимірної матриці 3×4 у лінійній оперативній пам'яті", size=15, bold=True))
    
    # 2D матриця зліва
    mat_x, mat_y = 40, 60
    cell_w, cell_h = 45, 35
    
    out.append(text(mat_x + 90, mat_y + 15, "Матриця M[3][4]", size=13, bold=True))
    
    for r in range(3):
        for c in range(4):
            x = mat_x + c * cell_w + 20
            y = mat_y + r * cell_h + 30
            out.append(rect(x, y, cell_w, cell_h, fill="#ffffff", stroke=LINE, sw=1, rx=2))
            out.append(text(x + cell_w / 2, y + cell_h / 2 + 4, f"[{r}][{c}]", size=10))
            
    # Порядок за рядками (Row-Major) - по центрі
    rm_x, rm_y = 260, 60
    out.append(text(rm_x + 130, rm_y + 15, "Row-Major Order (C, C++, Python)", size=12, color=POS, bold=True))
    out.append(text(rm_x + 130, rm_y + 32, "Рядки розміщуються послідовно", size=11, color=MUTED))
    
    rm_cells = [
        ("[0][0]", POS), ("[0][1]", POS), ("[0][2]", POS), ("[0][3]", POS),
        ("[1][0]", NEG), ("[1][1]", NEG), ("[1][2]", NEG), ("[1][3]", NEG)
    ]
    for i, (lbl, col) in enumerate(rm_cells):
        x = rm_x + (i % 4) * 58 + 10
        y = rm_y + (i // 4) * 45 + 50
        out.append(rect(x, y, 52, 35, fill="#ffffff", stroke=col, sw=1.5, rx=3))
        out.append(text(x + 26, y + 22, lbl, size=11, color=col, bold=True))
        
    out.append(rect(rm_x + 10, rm_y + 150, 240, 50, fill="#fdecea", stroke=POS, sw=1, rx=4))
    out.append(mtext(rm_x + 130, rm_y + 168, "Формула адресації:\nIndex = i × Cols + j = i × 4 + j", size=11, color=INK, bold=True))
    
    # Порядок за стовпчиками (Column-Major) - справа
    cm_x, cm_y = 550, 60
    out.append(text(cm_x + 130, cm_y + 15, "Column-Major Order (Fortran, Julia)", size=12, color=NEG, bold=True))
    out.append(text(cm_x + 130, cm_y + 32, "Стовпчики розміщуються послідовно", size=11, color=MUTED))
    
    cm_cells = [
        ("[0][0]", POS), ("[1][0]", POS), ("[2][0]", POS),
        ("[0][1]", FIELD), ("[1][1]", FIELD), ("[2][1]", FIELD)
    ]
    for i, (lbl, col) in enumerate(cm_cells):
        x = cm_x + (i % 3) * 76 + 15
        y = cm_y + (i // 3) * 45 + 50
        out.append(rect(x, y, 68, 35, fill="#ffffff", stroke=col, sw=1.5, rx=3))
        out.append(text(x + 34, y + 22, lbl, size=11, color=col, bold=True))
        
    out.append(rect(cm_x + 15, cm_y + 150, 240, 50, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    out.append(mtext(cm_x + 135, cm_y + 168, "Формула адресації:\nIndex = j × Rows + i = j × 3 + i", size=11, color=INK, bold=True))

    body = "".join(out)
    vx, vy, vw, vh = svgkit._fit_viewbox(body, w, h)
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" '
        f'width="{vw:.1f}" height="{vh:.1f}">\n'
        f'<defs>\n'
        f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
        f'  </marker>\n'
        f'</defs>\n'
        f'<rect width="100%" height="100%" fill="{BG}"/>\n'
        f'{body}\n'
        f'</svg>'
    )
    with open(os.path.join(IMG_DIR, 'multidimensional-indexing.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_content)

def generate_dynamic_array_growth():
    w, h = 840, 320
    out = []
    
    out.append(text(w / 2, 22, "Динамічний перерозподіл пам'яті при досягненні граничної місткості (Capacity)", size=15, bold=True))
    
    # Крок 1: Заповнений буфер (Size=4, Cap=4)
    step1_y = 60
    out.append(text(20, step1_y + 20, "Крок 1: Буфер заповнено (Size = 4, Capacity = 4)", size=12, bold=True, anchor="start"))
    for i in range(4):
        x = 380 + i * 55
        out.append(rect(x, step1_y, 50, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
        out.append(text(x + 25, step1_y + 22, f"E{i}", size=12, color=NEG, bold=True))
    out.append(text(615, step1_y + 22, "Адреса: 0x2000", size=11, color=MUTED, anchor="start"))
    
    # Стрілка вниз: push_back(E4)
    out.append(arrow(490, step1_y + 40, 490, step1_y + 65, color=POS, sw=2))
    out.append(text(505, step1_y + 55, "push_back(E4) → Переповнення!", size=11, color=POS, bold=True, anchor="start"))
    
    # Крок 2: Виділення нового буфера (Size=4, Cap=8) та копіювання
    step2_y = 135
    out.append(mtext(20, step2_y + 12, ["Крок 2: Виділення нового блоку x2 (Capacity = 8)", "та копіювання елементів E0..E3"], size=11, color=INK, anchor="start", bold=True))
    for i in range(8):
        x = 380 + i * 48
        if i < 4:
            fill_c, strk_c, txt_c = "#eaf0fd", NEG, NEG
            lbl = f"E{i}"
        elif i == 4:
            fill_c, strk_c, txt_c = "#fdecea", POS, POS
            lbl = "E4"
        else:
            fill_c, strk_c, txt_c = "#ffffff", MUTED, MUTED
            lbl = "вільно"
        out.append(rect(x, step2_y, 44, 35, fill=fill_c, stroke=strk_c, sw=1.5, rx=3))
        out.append(text(x + 22, step2_y + 22, lbl, size=10, color=txt_c, bold=(i<=4)))
    out.append(text(775, step2_y + 22, "0x5000", size=11, color=MUTED, anchor="start"))
    
    # Стрілка вниз: звільнення старої пам'яті
    out.append(arrow(490, step2_y + 40, 490, step2_y + 65, color=FIELD, sw=2))
    out.append(text(505, step2_y + 55, "free(0x2000) → Завершення", size=11, color=FIELD, bold=True, anchor="start"))
    
    # Крок 3: Фінальний стан
    step3_y = 210
    out.append(mtext(20, step3_y + 12, ["Крок 3: Старий блок звільнено.", "Новий стан: Size = 5, Capacity = 8"], size=11, color=INK, anchor="start", bold=True))
    for i in range(8):
        x = 380 + i * 48
        if i <= 4:
            fill_c, strk_c, txt_c = "#eaf0fd", FIELD, INK
            lbl = f"E{i}"
        else:
            fill_c, strk_c, txt_c = "#ffffff", MUTED, MUTED
            lbl = "вільно"
        out.append(rect(x, step3_y, 44, 35, fill=fill_c, stroke=strk_c, sw=1.5, rx=3))
        out.append(text(x + 22, step3_y + 22, lbl, size=10, color=txt_c, bold=(i<=4)))
    out.append(text(775, step3_y + 22, "0x5000", size=11, color=MUTED, anchor="start"))
    
    # Примітка про амортизаційну складність
    out.append(rect(140, 275, 540, 26, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    out.append(text(w / 2, 292, "Амортизована складність вставки: O(1) [копіювання O(n) відбувається рідко]", size=11, color=INK, bold=True))

    body = "".join(out)
    vx, vy, vw, vh = svgkit._fit_viewbox(body, w, h)
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" '
        f'width="{vw:.1f}" height="{vh:.1f}">\n'
        f'<defs>\n'
        f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
        f'  </marker>\n'
        f'</defs>\n'
        f'<rect width="100%" height="100%" fill="{BG}"/>\n'
        f'{body}\n'
        f'</svg>'
    )
    with open(os.path.join(IMG_DIR, 'dynamic-array-growth.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    generate_memory_layout()
    generate_multidimensional_indexing()
    generate_dynamic_array_growth()
    print("SVG figures generated successfully.")
