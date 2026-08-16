# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, scripts_dir)

from svgkit import (
    text, mtext, rect, line, circle, arrow, fitbox, _fit_viewbox,
    INK, MUTED, POS, NEG, FIELD, FILL, BG, LINE
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_site_vs_bond_svg():
    """SVG 1: Вузлова (Site) проти зв'язкової (Bond) перколації на 2D квадратно-ґратковій формі."""
    w, h = 800, 380
    elements = []

    # Background
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Title panels using fitbox
    elements.append(fitbox(30, 20, 350, 40, "Узлова перколація (Site Percolation)", size=15, bold=True, fill="#eef6ff", stroke="#2457d6"))
    elements.append(fitbox(420, 20, 350, 40, "Зв'язкова перколація (Bond Percolation)", size=15, bold=True, fill="#eef6ff", stroke="#2457d6"))

    # Panel 1: Site percolation (Left: 30 to 380, Y: 70 to 310)
    ox1, oy1 = 70, 90
    step = 60
    # States of nodes (1 = occupied, 0 = empty)
    site_states = [
        [1, 1, 0, 1],
        [0, 1, 1, 0],
        [1, 1, 0, 1],
        [0, 1, 1, 1]
    ]

    # Draw all potential grid edges in background
    for r in range(4):
        for c in range(4):
            x = ox1 + c * step
            y = oy1 + r * step
            if c < 3:
                elements.append(line(x, y, x + step, y, color="#d0d5dd", sw=1.5, dash="3,3"))
            if r < 3:
                elements.append(line(x, y, x, y + step, color="#d0d5dd", sw=1.5, dash="3,3"))

    # Draw actual connected bonds between occupied neighboring sites
    for r in range(4):
        for c in range(4):
            x = ox1 + c * step
            y = oy1 + r * step
            if site_states[r][c] == 1:
                if c < 3 and site_states[r][c+1] == 1:
                    elements.append(line(x, y, x + step, y, color=POS, sw=3.5))
                if r < 3 and site_states[r+1][c] == 1:
                    elements.append(line(x, y, x, y + step, color=POS, sw=3.5))

    # Draw node circles
    for r in range(4):
        for c in range(4):
            x = ox1 + c * step
            y = oy1 + r * step
            if site_states[r][c] == 1:
                elements.append(circle(x, y, 12, fill="#fdecea", stroke=POS, sw=2))
                elements.append(text(x, y + 4, "●", size=10, color=POS, anchor="middle"))
            else:
                elements.append(circle(x, y, 10, fill=BG, stroke=MUTED, sw=1.5))

    # Explanatory text under Site panel
    elements.append(fitbox(30, 320, 350, 45, "Вузли випадково відкриті (p) або заблоковані (1-p).\nЗв'язок існує лише між суміжними відкритими вузлами.", size=11, fill="#f8fafc", stroke="#cbd5e1"))

    # Panel 2: Bond percolation (Right: 420 to 770, Y: 70 to 310)
    ox2, oy2 = 460, 90
    horizontal_bonds = [
        [1, 0, 1],
        [1, 1, 0],
        [0, 1, 1],
        [1, 1, 0]
    ]
    vertical_bonds = [
        [1, 1, 0, 1],
        [0, 1, 1, 0],
        [1, 0, 1, 1]
    ]

    # Draw inactive bond positions
    for r in range(4):
        for c in range(4):
            x = ox2 + c * step
            y = oy2 + r * step
            if c < 3 and horizontal_bonds[r][c] == 0:
                elements.append(line(x, y, x + step, y, color="#e2e8f0", sw=1.5, dash="3,3"))
            if r < 3 and vertical_bonds[r][c] == 0:
                elements.append(line(x, y, x, y + step, color="#e2e8f0", sw=1.5, dash="3,3"))

    # Draw active bonds
    for r in range(4):
        for c in range(3):
            if horizontal_bonds[r][c] == 1:
                x = ox2 + c * step
                y = oy2 + r * step
                elements.append(line(x, y, x + step, y, color=FIELD, sw=3.5))

    for r in range(3):
        for c in range(4):
            if vertical_bonds[r][c] == 1:
                x = ox2 + c * step
                y = oy2 + r * step
                elements.append(line(x, y, x, y + step, color=FIELD, sw=3.5))

    # Draw nodes for bond percolation (all identical)
    for r in range(4):
        for c in range(4):
            x = ox2 + c * step
            y = oy2 + r * step
            elements.append(circle(x, y, 9, fill="#e8f5e9", stroke=FIELD, sw=1.5))

    # Explanatory text under Bond panel
    elements.append(fitbox(420, 320, 350, 45, "Усі вузли доступні. Випадково відкриваються ребра (зв'язки).\nПотік іде відкритими каналами ґратки.", size=11, fill="#f8fafc", stroke="#cbd5e1"))

    svg_content = "".join(elements)
    vx, vy, vw, vh = _fit_viewbox(svg_content, w, h)
    svg_final = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" width="{vw:.1f}" height="{vh:.1f}">\n'
    svg_final += '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>\n'
    svg_final += svg_content + '\n</svg>'

    with open(os.path.join(OUTPUT_DIR, 'site-vs-bond.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_final)


def create_percolation_transition_svg():
    """SVG 2: Залежність потужності нескінченного кластера P_inf(p) та середнього розміру chi(p) від ймовірності p."""
    w, h = 760, 400
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Title
    elements.append(fitbox(180, 20, 400, 35, "Фазовий перехід та критичні характеристики", size=14, bold=True, fill="#f1f5f9", stroke="#475569"))

    # Axes
    ox, oy = 80, 330
    gw, gh = 600, 260
    elements.append(arrow(ox - 10, oy, ox + gw + 30, oy, color=LINE, sw=2))  # p-axis
    elements.append(arrow(ox, oy + 10, ox, oy - gh - 20, color=LINE, sw=2))  # Y-axis

    # Axis labels
    elements.append(text(ox + gw + 40, oy + 5, "p", size=16, color=INK, bold=True))
    elements.append(text(ox - 35, oy - gh - 15, "P_∞, χ", size=15, color=INK, bold=True))

    # Critical point p_c line
    xc = ox + int(gw * 0.5)  # p_c at 0.5
    elements.append(line(xc, oy, xc, oy - gh, color=POS, sw=2, dash="4,4"))
    elements.append(fitbox(xc - 35, oy + 15, 70, 30, "p_c", size=14, bold=True, fill="#fdecea", stroke=POS))

    # Axis scale ticks
    elements.append(text(ox, oy + 20, "0", size=12, color=MUTED))
    elements.append(text(ox + gw, oy + 20, "1", size=12, color=MUTED))
    elements.append(line(ox + gw, oy - 4, ox + gw, oy + 4, color=LINE, sw=1.5))

    # P_infinity curve
    p_pts = []
    p_pts.append(f"M {ox},{oy} L {xc},{oy}")
    curve_cmd = [f"M {xc},{oy}"]
    for i in range(1, 51):
        frac = i / 50.0
        px = xc + frac * (gw * 0.5)
        val = frac ** 0.5
        py = oy - val * (gh * 0.8)
        curve_cmd.append(f"L {px:.1f},{py:.1f}")
    elements.append(f'<path d="{" ".join(curve_cmd)}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Chi(p) curve
    chi_left = []
    for i in range(0, 48):
        frac = i / 50.0
        px = ox + frac * (gw * 0.5)
        dist = 1.0 - frac
        val = min(1.0 / (dist ** 0.9), 15.0)
        py = oy - (val - 1.0) * 16
        if py < oy - gh:
            py = oy - gh
        if i == 0:
            chi_left.append(f"M {px:.1f},{py:.1f}")
        else:
            chi_left.append(f"L {px:.1f},{py:.1f}")
    elements.append(f'<path d="{" ".join(chi_left)}" fill="none" stroke="{NEG}" stroke-width="2.5" stroke-dasharray="6,3"/>')

    chi_right = []
    for i in range(2, 51):
        frac = i / 50.0
        px = xc + frac * (gw * 0.5)
        dist = frac
        val = min(1.0 / (dist ** 0.9), 15.0)
        py = oy - (val - 1.0) * 16
        if py < oy - gh:
            py = oy - gh
        if i == 2:
            chi_right.append(f"M {px:.1f},{py:.1f}")
        else:
            chi_right.append(f"L {px:.1f},{py:.1f}")
    elements.append(f'<path d="{" ".join(chi_right)}" fill="none" stroke="{NEG}" stroke-width="2.5" stroke-dasharray="6,3"/>')

    # Legend callouts
    elements.append(fitbox(460, oy - 180, 240, 40, "P_∞(p) — Потужність нескінченного кластера\n(Параметр порядку: P_∞ ~ (p - p_c)^β)", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))
    elements.append(fitbox(150, oy - 200, 230, 40, "χ(p) — Середній розмір скінченного кластера\n(Розбіжність: χ ~ |p - p_c|^-γ)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    # Regimes labels
    elements.append(fitbox(ox + 70, oy - 40, 160, 30, "Докритичний режим\n(p < p_c, ізольовані плями)", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    elements.append(fitbox(xc + 110, oy - 40, 180, 30, "Надкритичний режим\n(p > p_c, макроскопічний затік)", size=10, fill="#f8fafc", stroke="#cbd5e1"))

    svg_content = "".join(elements)
    vx, vy, vw, vh = _fit_viewbox(svg_content, w, h)
    svg_final = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" width="{vw:.1f}" height="{vh:.1f}">\n'
    svg_final += '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>\n'
    svg_final += svg_content + '\n</svg>'

    with open(os.path.join(OUTPUT_DIR, 'percolation-transition.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_final)


def create_bethe_lattice_svg():
    """SVG 3: Решітка Беті (дерево Келі) з координаційним числом z = 3."""
    w, h = 680, 450
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Move title away from tree geometry
    elements.append(fitbox(20, 20, 300, 35, "Решітка Беті (дерево Келі, z = 3)", size=14, bold=True, fill="#f1f5f9", stroke="#475569"))

    cx, cy = 340, 250

    import math
    r1 = 60
    l1_nodes = []
    for i in range(3):
        angle = math.radians(90 + i * 120)
        nx = cx + r1 * math.cos(angle)
        ny = cy - r1 * math.sin(angle)
        l1_nodes.append((nx, ny, angle))

    r2 = 55
    l2_nodes = []
    for nx, ny, base_angle in l1_nodes:
        for da in [-35, 35]:
            angle = base_angle + math.radians(da)
            n2x = nx + r2 * math.cos(angle)
            n2y = ny - r2 * math.sin(angle)
            l2_nodes.append((nx, ny, n2x, n2y, angle))

    r3 = 45
    l3_nodes = []
    for p1x, p1y, nx, ny, base_angle in l2_nodes:
        for da in [-20, 20]:
            angle = base_angle + math.radians(da)
            n3x = nx + r3 * math.cos(angle)
            n3y = ny - r3 * math.sin(angle)
            l3_nodes.append((nx, ny, n3x, n3y))

    # Draw Level 2 to Level 3 edges
    for px, py, nx, ny in l3_nodes:
        elements.append(line(px, py, nx, ny, color="#cbd5e1", sw=1.5))
        elements.append(circle(nx, ny, 4, fill="#cbd5e1", stroke=MUTED, sw=1))

    # Draw Level 1 to Level 2 edges
    for px, py, nx, ny, _ in l2_nodes:
        elements.append(line(px, py, nx, ny, color=NEG, sw=2))
        elements.append(circle(nx, ny, 7, fill="#eaf0fd", stroke=NEG, sw=1.5))

    # Draw Root to Level 1 edges
    for nx, ny, _ in l1_nodes:
        elements.append(line(cx, cy, nx, ny, color=POS, sw=2.5))
        elements.append(circle(nx, ny, 9, fill="#fdecea", stroke=POS, sw=2))

    # Draw Root node
    elements.append(circle(cx, cy, 12, fill="#fff3cd", stroke="#d97706", sw=2.5))
    elements.append(text(cx, cy + 4, "0", size=11, bold=True, color="#92400e", anchor="middle"))

    # Labels and explanation placed outside tree area
    elements.append(fitbox(460, 20, 200, 50, "Координаційне число z = 3\nГіллястість γ = z - 1 = 2", size=11, bold=True, fill="#fff8e1", stroke="#b45309"))
    elements.append(fitbox(460, 370, 200, 50, "Відсутність замкнених циклів\nТочний поріг: p_c = 1/(z-1) = 1/2", size=11, fill="#f8fafc", stroke="#cbd5e1"))

    svg_content = "".join(elements)
    vx, vy, vw, vh = _fit_viewbox(svg_content, w, h)
    svg_final = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" width="{vw:.1f}" height="{vh:.1f}">\n'
    svg_final += svg_content + '\n</svg>'

    with open(os.path.join(OUTPUT_DIR, 'bethe-lattice.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_final)


def create_hoshen_kopelman_steps_svg():
    """SVG 4: Етапи алгоритму Гошена — Копельмана для маркування кластерів на сітці."""
    w, h = 820, 360
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Three steps panels
    step_titles = [
        "1. Сканування та первинні мітки",
        "2. Таблиця еквівалентностей (DSU)",
        "3. Фінальне перемаркування"
    ]

    for i, title in enumerate(step_titles):
        px = 30 + i * 260
        elements.append(fitbox(px, 20, 240, 35, title, size=12, bold=True, fill="#eef6ff", stroke="#2457d6"))

    def draw_grid_matrix(ox, oy, matrix, is_final=False):
        step = 45
        for r in range(4):
            for c in range(4):
                x = ox + c * step
                y = oy + r * step
                val = matrix[r][c]
                if val == 0:
                    elements.append(rect(x, y, step-2, step-2, fill="#f8fafc", stroke="#cbd5e1", rx=3))
                    elements.append(text(x + step/2 - 1, y + step/2 + 4, "0", size=11, color=MUTED))
                else:
                    if is_final:
                        fill_col = "#dcfce7" if val == 1 else "#fef3c7"
                        strk_col = FIELD if val == 1 else "#b45309"
                        txt_col = FIELD if val == 1 else "#b45309"
                    else:
                        fill_col = "#e0f2fe" if val == 1 else ("#fef3c7" if val == 2 else "#ffe4e6")
                        strk_col = "#0284c7" if val == 1 else ("#d97706" if val == 2 else "#e11d48")
                        txt_col = strk_col
                    elements.append(rect(x, y, step-2, step-2, fill=fill_col, stroke=strk_col, sw=1.5, rx=3))
                    elements.append(text(x + step/2 - 1, y + step/2 + 5, str(val), size=13, bold=True, color=txt_col))

    # Draw Step 1 grid
    grid1 = [
        [1, 1, 0, 2],
        [0, 1, 1, 0],
        [3, 0, 1, 1],
        [3, 3, 0, 1]
    ]
    draw_grid_matrix(50, 75, grid1, is_final=False)

    # Step 2: DSU Equivalence Trees representation
    elements.append(rect(290, 75, 240, 180, fill="#fdfbf7", stroke="#f59e0b", rx=6))
    elements.append(fitbox(300, 85, 220, 28, "Масив батьків родини (parent)", size=11, bold=True, fill="#fff", stroke="#f59e0b"))

    # Table of parent array
    elements.append(fitbox(305, 125, 210, 30, "вузол:    [1]   [2]   [3]\nparent:   1     2     1", size=11, fill="#fff", stroke="#cbd5e1"))

    elements.append(fitbox(300, 170, 220, 70, "Об'єднання конфліктів:\nПід час зустрічі суміжних\nрізних міток (3 та 1)\nвиконується Union(3, 1).", size=10, fill="#f8fafc", stroke="#cbd5e1"))

    # Draw Step 3 grid (Final canonical labels)
    grid3 = [
        [1, 1, 0, 2],
        [0, 1, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 0, 1]
    ]
    draw_grid_matrix(570, 75, grid3, is_final=True)

    # Annotations under Step 1 and Step 3
    elements.append(fitbox(30, 275, 220, 50, "Рядковий обхід ґратки.\nПеревірка лівого та верхнього сусіда.\nПризначення нових або наявних міток.", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    elements.append(fitbox(550, 275, 220, 50, "Другий прохід: заміна тимчасових\nміток на канонічні корені ДСУ.\nКластер 3 об'єднано з кластером 1.", size=10, fill="#f8fafc", stroke="#cbd5e1"))

    svg_content = "".join(elements)
    vx, vy, vw, vh = _fit_viewbox(svg_content, w, h)
    svg_final = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" width="{vw:.1f}" height="{vh:.1f}">\n'
    svg_final += svg_content + '\n</svg>'

    with open(os.path.join(OUTPUT_DIR, 'hoshen-kopelman-steps.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_final)


if __name__ == '__main__':
    create_site_vs_bond_svg()
    create_percolation_transition_svg()
    create_bethe_lattice_svg()
    create_hoshen_kopelman_steps_svg()
    print("Successfully generated all SVG diagrams for percolation theory.")
