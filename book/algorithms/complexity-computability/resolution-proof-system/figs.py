# -*- coding: utf-8 -*-
import os
import sys

# Підключаємо scripts/ з кореня репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def draw_path(d, color=LINE, sw=1.5, fill="none"):
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"/>'

def generate_resolution_rule_elimination():
    path = os.path.join(IMG_DIR, 'resolution-rule-elimination.svg')
    w, h = 680, 360
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Правило резолюції: Елімінація комплементарної змінної", size=16, bold=True))
    frags.append(text(w / 2, 55, "Вивід резольвенти з двох початкових диз'юнктів за змінною x", size=12, color=MUTED))
    
    # Left clause box C1
    b_c1, _, _ = textbox(190, 120, "Диз'юнкт C₁ = A ∨ x\n(містить позитивний літерал x)", size=13, fill="#eef6ff", stroke="#2563eb", sw=1.5)
    frags.append(b_c1)
    
    # Right clause box C2
    b_c2, _, _ = textbox(490, 120, "Диз'юнкт C₂ = B ∨ ¬x\n(містить негативний літерал ¬x)", size=13, fill="#fff1f2", stroke="#e11d48", sw=1.5)
    frags.append(b_c2)
    
    # Convergence lines down to Resolvent
    frags.append(arrow(210, 165, 300, 230, color="#2563eb", sw=2))
    frags.append(arrow(470, 165, 380, 230, color="#e11d48", sw=2))
    
    # Operation label box in the middle
    b_op, _, _ = textbox(340, 190, "Елімінація {x, ¬x}", size=11, fill="#f3f4f6", stroke="#9ca3af", sw=1)
    frags.append(b_op)
    
    # Resolvent C3 box
    b_res, _, _ = textbox(340, 275, "Резольвента C = A ∨ B\n(диз'юнкт без змінної x)", size=14, bold=True, fill="#f0fdf4", stroke="#16a34a", sw=2)
    frags.append(b_res)
    
    # Explanatory text at bottom
    frags.append(text(w / 2, 335, "Якщо C₁ і C₂ істинні, то при x=0 істинне A, а при x=1 істинне B. Отже, A ∨ B істинне завжди.", size=11, color="#4b5563"))
    
    render(path, w, h, *frags)

def generate_tree_vs_dag_resolution():
    path = os.path.join(IMG_DIR, 'tree-vs-dag-resolution.svg')
    w, h = 720, 380
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Структури резолюційного виводу: Деревна (Tree) проти Графної (DAG)", size=16, bold=True))
    
    # Vertical separator
    frags.append(line(360, 55, 360, 350, color="#e5e7eb", sw=1.5, dash="4,4"))
    
    # Left side: Tree Resolution
    frags.append(text(180, 60, "Деревний вивід (Tree Resolution)", size=14, bold=True, color="#1e3a8a"))
    frags.append(text(180, 78, "Дублювання виводу проміжних диз'юнктів", size=11, color=MUTED))
    
    # Tree nodes
    b_t1, _, _ = textbox(90, 115, "A ∨ x", size=11, fill="#f8fafc", stroke=LINE)
    b_t2, _, _ = textbox(170, 115, "¬x ∨ y", size=11, fill="#f8fafc", stroke=LINE)
    b_t3, _, _ = textbox(270, 115, "A ∨ x", size=11, fill="#f8fafc", stroke=LINE)
    b_t4, _, _ = textbox(330, 115, "¬x ∨ ¬y", size=11, fill="#f8fafc", stroke=LINE)
    
    frags.extend([b_t1, b_t2, b_t3, b_t4])
    
    b_tr1, _, _ = textbox(130, 195, "A ∨ y\n(підвивід 1)", size=11, fill="#eff6ff", stroke="#3b82f6")
    b_tr2, _, _ = textbox(300, 195, "A ∨ ¬y\n(дубльований підвивід 2)", size=11, fill="#eff6ff", stroke="#3b82f6")
    
    frags.extend([b_tr1, b_tr2])
    
    frags.append(arrow(100, 138, 120, 172, color="#64748b"))
    frags.append(arrow(160, 138, 140, 172, color="#64748b"))
    frags.append(arrow(260, 138, 285, 172, color="#64748b"))
    frags.append(arrow(320, 138, 305, 172, color="#64748b"))
    
    b_troot, _, _ = textbox(215, 285, "Головна резольвента A\n(експоненційний розмір)", size=12, bold=True, fill="#ffe4e6", stroke="#e11d48", sw=1.5)
    frags.append(b_troot)
    
    frags.append(arrow(140, 222, 190, 260, color="#64748b"))
    frags.append(arrow(290, 222, 240, 260, color="#64748b"))
    
    # Right side: DAG Resolution
    frags.append(text(540, 60, "Загальний графний вивід (DAG Resolution)", size=14, bold=True, color="#065f46"))
    frags.append(text(540, 78, "Перевикористання обчислених резольвент", size=11, color=MUTED))
    
    # DAG nodes
    b_d1, _, _ = textbox(420, 115, "A ∨ x", size=11, fill="#f8fafc", stroke=LINE)
    b_d2, _, _ = textbox(530, 115, "¬x ∨ y", size=11, fill="#f8fafc", stroke=LINE)
    b_d3, _, _ = textbox(640, 115, "¬y", size=11, fill="#f8fafc", stroke=LINE)
    
    frags.extend([b_d1, b_d2, b_d3])
    
    # Shared intermediate resolvent A ∨ y
    b_dres1, _, _ = textbox(475, 195, "A ∨ y\n(спільний вузол)", size=11, fill="#ecfdf5", stroke="#10b981", sw=1.5)
    frags.append(b_dres1)
    
    frags.append(arrow(435, 138, 460, 172, color="#64748b"))
    frags.append(arrow(515, 138, 490, 172, color="#64748b"))
    
    # Final resolvent A
    b_droot, _, _ = textbox(560, 285, "Головна резольвента A\n(поліноміальний розмір)", size=12, bold=True, fill="#ecfdf5", stroke="#059669", sw=1.5)
    frags.append(b_droot)
    
    frags.append(arrow(490, 222, 535, 260, color="#64748b"))
    frags.append(arrow(630, 138, 580, 260, color="#64748b"))
    
    # Footer notes
    frags.append(text(w / 2, 350, "Розмір деревного доведення може бути O(2ⁿ), тоді як графне доведення має розмір O(n).", size=11, color="#374151"))
    
    render(path, w, h, *frags)

def generate_cdcl_1uip_resolution_graph():
    path = os.path.join(IMG_DIR, 'cdcl-1uip-resolution-graph.svg')
    w, h = 700, 390
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Вивід конфліктного диз'юнкта 1UIP в імпликаційному графі CDCL", size=16, bold=True))
    frags.append(text(w / 2, 55, "Ланцюжок резолюцій від ноди конфлікту ⊥ до першої точки унікальної імпликації", size=12, color=MUTED))
    
    # Decision level 1 & 2 blocks
    b_dec1, _, _ = textbox(90, 100, "Призначення x₁=1\n@Рівень 1", size=11, fill="#eff6ff", stroke="#3b82f6")
    b_dec2, _, _ = textbox(90, 200, "Призначення x₂=1\n@Рівень 2 (поточний)", size=11, fill="#fef3c7", stroke="#d97706")
    frags.extend([b_dec1, b_dec2])
    
    # Propagated nodes
    b_p1, _, _ = textbox(270, 130, "x₃=1\n(з диз'юнкта ¬x₁ ∨ x₃)", size=11, fill="#f8fafc", stroke=LINE)
    b_uip, _, _ = textbox(270, 230, "x₄=1 [1UIP]\n(Перша точка імпликації)", size=11, bold=True, fill="#ecfdf5", stroke="#059669", sw=2)
    frags.extend([b_p1, b_uip])
    
    # Propagated nodes inside conflict clause
    b_cnode1, _, _ = textbox(470, 150, "x₅=1\n(з ¬x₄ ∨ x₅)", size=11, fill="#f8fafc", stroke=LINE)
    b_cnode2, _, _ = textbox(470, 250, "x₆=0\n(з ¬x₄ ∨ ¬x₆)", size=11, fill="#f8fafc", stroke=LINE)
    frags.extend([b_cnode1, b_cnode2])
    
    # Conflict node
    b_conf, _, _ = textbox(620, 200, "Конфлікт ⊥\n(¬x₅ ∨ x₆)", size=12, bold=True, fill="#ffe4e6", stroke="#e11d48", sw=2)
    frags.append(b_conf)
    
    # Implication arrows
    frags.append(arrow(150, 100, 215, 125, color="#64748b"))
    frags.append(arrow(150, 200, 215, 225, color="#64748b"))
    frags.append(arrow(150, 100, 215, 220, color="#64748b"))
    
    frags.append(arrow(325, 230, 415, 160, color="#64748b"))
    frags.append(arrow(325, 230, 415, 245, color="#64748b"))
    frags.append(arrow(325, 130, 415, 150, color="#64748b"))
    
    frags.append(arrow(525, 160, 565, 190, color="#e11d48", sw=1.5))
    frags.append(arrow(525, 245, 565, 210, color="#e11d48", sw=1.5))
    
    # Cut line representing 1UIP Resolution Clause
    frags.append(line(375, 80, 375, 300, color="#dc2626", sw=2, dash="5,5"))
    frags.append(text(375, 315, "Переріз 1UIP (1UIP Cut)", size=11, bold=True, color="#dc2626"))
    
    # Learned clause text box
    b_learned, _, _ = textbox(350, 350, "Згенерований конфліктний диз'юнкт резолюції: C_learned = ¬x₃ ∨ ¬x₄", size=12, bold=True, fill="#f0fdf4", stroke="#16a34a")
    frags.append(b_learned)
    
    render(path, w, h, *frags)

def generate_haken_pigeonhole_bound():
    path = os.path.join(IMG_DIR, 'haken-pigeonhole-bound.svg')
    w, h = 680, 360
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Нижня межа Хакена (1985) для принципу дірочок Діріхле PHPₙⁿ⁺¹", size=16, bold=True))
    frags.append(text(w / 2, 55, "Експоненційне зростання довжини резолюційного спростування 2^Ω(n)", size=12, color=MUTED))
    
    # Graph axes
    ox, oy = 90, 300
    gw, gh = 520, 220
    
    # Axes lines
    frags.append(arrow(ox, oy, ox + gw, oy, color="#374151", sw=2)) # X axis
    frags.append(arrow(ox, oy, ox, oy - gh, color="#374151", sw=2)) # Y axis
    
    # Axis labels
    frags.append(text(ox + gw - 40, oy + 25, "Кількість елементів (n)", size=12, bold=True))
    frags.append(text(ox - 45, oy - gh + 15, "Кількість диз'юнктів у доведенні", size=11, bold=True))
    
    # Polynomial curve (e.g. Extended Resolution)
    poly_pts = []
    for x in range(0, 420, 20):
        px = ox + x
        py = oy - (x * 0.25 + (x/50)**2 * 3)
        poly_pts.append((px, py))
    
    poly_path = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in poly_pts)
    frags.append(draw_path(poly_path, color="#2563eb", sw=2.5, fill="none"))
    frags.append(text(ox + 320, oy - 65, "Розширена резолюція (Extended Res): O(n³)", size=11, color="#2563eb", bold=True))
    
    # Exponential curve (Standard Resolution)
    exp_pts = []
    for x in range(0, 360, 15):
        px = ox + x
        val = 2 ** (x / 50.0) - 1
        py = oy - val * 3.2
        if py < oy - gh + 10:
            py = oy - gh + 10
            exp_pts.append((px, py))
            break
        exp_pts.append((px, py))
    
    exp_path = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in exp_pts)
    frags.append(draw_path(exp_path, color="#e11d48", sw=3, fill="none"))
    frags.append(text(ox + 210, oy - 180, "Стандартна резолюція: 2^Ω(n) [Теорема Хакена]", size=11, color="#e11d48", bold=True))
    
    # Grid lines and ticks
    for i in range(1, 6):
        tx = ox + i * 80
        frags.append(line(tx, oy - 4, tx, oy + 4, color="#64748b"))
        frags.append(text(tx, oy + 18, f"n={i*5}", size=10, color="#64748b"))
    
    # Explanatory note box at top right
    b_note, _, _ = textbox(520, 100, "PHPₙⁿ⁺¹: n+1 голубив у n гнізд.\nРезолюція не може зберегти\nієрархію підформул без нових змінних.", size=11, fill="#fef2f2", stroke="#fca5a5")
    frags.append(b_note)
    
    render(path, w, h, *frags)

def main():
    generate_resolution_rule_elimination()
    generate_tree_vs_dag_resolution()
    generate_cdcl_1uip_resolution_graph()
    generate_haken_pigeonhole_bound()
    print("Всі 4 фігури успішно згенеровано у ./img/")

if __name__ == '__main__':
    main()
