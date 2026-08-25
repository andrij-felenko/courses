# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
SETTLED = "#27ae60"   # зелений — оптимум / паросполучення
FRONT   = "#e08a1e"   # помаранчевий — поточний кандидат / змінний шлях
ACCENT  = "#2457d6"   # синій — потенціали / редукція
ALERT   = "#c0392b"   # червоний — конфлікт / дельта
FAR     = "#94a3b8"   # сірий — невикористані зв'язки
FILL_U  = "#eaf2fd"   # блакитна заливка для рядків / виконавців
FILL_V  = "#fef3e6"   # бежева заливка для стовпців / завдань
GRID_BG = "#f8fafc"   # фонова сітка матриці

def vnode(cx, cy, name, fill=FILL, stroke=LINE, r=18):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, name, size=13, color=INK, bold=True)
    return out

def edge(x1, y1, x2, y2, color=FAR, sw=1.8, dash=None, r1=18, r2=18):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    return line(ax, ay, bx, by, color=color, sw=sw, dash=dash)

# ── ФІГ.1 Редукція матриці та нульові комірки ──────────────────────────────
def fig_matrix_reduction():
    W, H = 820, 420
    p = []

    # Ліва матриця: Початкова вагова матриця C
    p.append(textbox(200, 35, "1. Початкова вартість C[i][j] та min по рядках", size=13, bold=True, fill=FILL, stroke=LINE)[0])
    
    m1_x, m1_y = 50.0, 70.0
    cell_w, cell_h = 55.0, 45.0
    
    # Дані початкової матриці 4x4
    orig = [
        [10, 19, 8, 15],
        [10, 18, 7, 17],
        [13, 16, 9, 14],
        [12, 19, 8, 18]
    ]
    u_mins = [8, 7, 9, 8]
    
    # Малюємо заголовки стовпців
    for j in range(4):
        p.append(text(m1_x + (j + 1) * cell_w + cell_w / 2, m1_y + 20, f"v{j+1}", size=12, bold=True, color=ACCENT))
    
    for i in range(4):
        p.append(text(m1_x + cell_w / 2, m1_y + (i + 1) * cell_h + 28, f"u{i+1}", size=12, bold=True, color=ALERT))
        for j in range(4):
            val = orig[i][j]
            cx = m1_x + (j + 1) * cell_w
            cy = m1_y + (i + 1) * cell_h
            p.append(rect(cx, cy, cell_w, cell_h, fill=BG, stroke="#cbd5e1", sw=1.0))
            p.append(text(cx + cell_w / 2, cy + 28, str(val), size=13, color=INK))
        
        # Мінімум рядка
        rx = m1_x + 5 * cell_w
        ry = m1_y + (i + 1) * cell_h
        p.append(rect(rx, ry, cell_w + 10, cell_h, fill=FILL_U, stroke=ALERT, sw=1.5))
        p.append(text(rx + (cell_w + 10) / 2, ry + 28, f"u={u_mins[i]}", size=11, bold=True, color=ALERT))

    # Стрілка між матрицями
    p.append(arrow(395, 185, 435, 185, color=INK, sw=2.5))
    p.append(text(415, 170, "u, v", size=12, bold=True, color=ACCENT))

    # Права матриця: Редукована матриця з нулями
    p.append(textbox(620, 35, "2. Редукована матриця C'[i][j] ≥ 0 та нулі", size=13, bold=True, fill=FILL, stroke=LINE)[0])
    
    m2_x, m2_y = 450.0, 70.0
    reduced = [
        [2, 8, 0, 0],
        [3, 8, 0, 3],
        [4, 4, 0, 0],
        [4, 8, 0, 3]
    ]
    
    for j in range(4):
        p.append(text(m2_x + (j + 1) * cell_w + cell_w / 2, m2_y + 20, f"v{j+1}", size=12, bold=True, color=ACCENT))
        
    for i in range(4):
        p.append(text(m2_x + cell_w / 2, m2_y + (i + 1) * cell_h + 28, f"u{i+1}", size=12, bold=True, color=ALERT))
        for j in range(4):
            val = reduced[i][j]
            cx = m2_x + (j + 1) * cell_w
            cy = m2_y + (i + 1) * cell_h
            is_zero = (val == 0)
            fill_c = "#dcfce7" if is_zero else BG
            stroke_c = SETTLED if is_zero else "#cbd5e1"
            sw = 2.0 if is_zero else 1.0
            p.append(rect(cx, cy, cell_w, cell_h, fill=fill_c, stroke=stroke_c, sw=sw))
            p.append(text(cx + cell_w / 2, cy + 28, str(val), size=13, bold=is_zero, color=SETTLED if is_zero else INK))

    # Нижній пояснювальний блок
    p.append(textbox(W / 2, 360,
                     "Редукція C'[i][j] = C[i][j] − u[i] − v[j] зберігає взаємний порядок вартостей усіх призначень.\n"
                     "Будь-яке досконале паросполучення, побудоване виключно з нульових клітинок (C'=0), є глобально оптимальним.",
                     size=12, fill="#f0fdf4", stroke=SETTLED)[0])

    render(os.path.join(OUT, "fig1-matrix-reduction.svg"), W, H, *p,
           title="Редукція матриці та поява нульових комірок")


# ── ФІГ.2 Граф рівності та двоїсті потенціали ──────────────────────────────
def fig_equality_subgraph():
    W, H = 820, 430
    p = []

    ux, vx = 240.0, 580.0
    ys = [85.0, 165.0, 245.0, 325.0]
    
    # Заголовки часток
    p.append(textbox(ux, 30, "Рядки U (виконавці) з потенціалами u[i]", size=12, bold=True, fill=FILL_U, stroke=ALERT)[0])
    p.append(textbox(vx, 30, "Стовпці V (задачі) з потенціалами v[j]", size=12, bold=True, fill=FILL_V, stroke=ACCENT)[0])

    # Ребра графа рівності: C[i][j] - u[i] - v[j] == 0
    all_eq = [(0, 2), (0, 3), (1, 2), (2, 2), (2, 3), (3, 2)]
    matching = {(0, 3), (1, 2)}

    for ui, vi in all_eq:
        is_m = (ui, vi) in matching
        col = SETTLED if is_m else FRONT
        sw = 3.0 if is_m else 1.8
        dash = None if is_m else "5 4"
        p.append(edge(ux, ys[ui], vx, ys[vi], color=col, sw=sw, dash=dash))

    u_labels = ["u₁ (u=8)", "u₂ (u=7)", "u₃ (u=9)", "u₄ (u=8)"]
    v_labels = ["v₁ (v=0)", "v₂ (v=1)", "v₃ (v=0)", "v₄ (v=7)"]

    for i, (y, lbl) in enumerate(zip(ys, u_labels)):
        p.append(vnode(ux, y, f"u{i+1}", fill=FILL_U, stroke=ALERT, r=20))
        p.append(text(ux - 70, y + 4, lbl.split(" ")[1], size=11, bold=True, color=ALERT))

    for j, (y, lbl) in enumerate(zip(ys, v_labels)):
        p.append(vnode(vx, y, f"v{j+1}", fill=FILL_V, stroke=ACCENT, r=20))
        p.append(text(vx + 70, y + 4, lbl.split(" ")[1], size=11, bold=True, color=ACCENT))

    # Легенда
    p.append(textbox(W / 2, 385,
                     "Суцільні зелені ребра — поточне насичене паросполучення M у графі рівності C'[i][j] = 0.\n"
                     "Помаранчеві пунктирні ребра — інші дозволені нульові зв'язки. Вершини u₃ та u₄ не мають вільних партнерів у V.",
                     size=12, fill=FILL, stroke=LINE)[0])

    render(os.path.join(OUT, "fig2-equality-subgraph.svg"), W, H, *p,
           title="Граф рівності та двоїсті потенціали")


# ── ФІГ.3 Змінне дерево та перерахунок потенціалів (Slack і Delta) ──────────
def fig_alternating_tree():
    W, H = 880, 450
    p = []

    # Ліва частина: Множина відвіданих S ⊆ U та T ⊆ V
    p.append(rect(30, 45, 370, 295, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(textbox(215, 70, "Змінне дерево пошуку (S ⊂ U, T ⊂ V)", size=12, bold=True, fill="#e2e8f0", stroke=LINE)[0])

    # Вузли в дереві
    p.append(vnode(120, 130, "u₃", fill="#fee2e2", stroke=ALERT, r=20))
    p.append(text(120, 168, "Корінь (вільний)", size=10, color=ALERT, bold=True))

    p.append(vnode(290, 130, "v₃", fill="#fef3c7", stroke=FRONT, r=20))
    p.append(text(290, 168, "T: нульове ребро", size=10, color=FRONT))

    p.append(vnode(290, 240, "u₂", fill="#fee2e2", stroke=ALERT, r=20))
    p.append(text(290, 278, "S: покритий в M", size=10, color=ALERT))

    # Ребра в дереві
    p.append(edge(120, 130, 290, 130, color=FRONT, sw=2.5, dash="4 4"))
    p.append(edge(290, 130, 290, 240, color=SETTLED, sw=3.0))

    # Права зона: Зовнішні стовпці
    p.append(rect(480, 45, 370, 295, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(textbox(665, 70, "Неперевірені стовпці j ∉ T та оцінки Slack", size=12, bold=True, fill="#e2e8f0", stroke=LINE)[0])

    p.append(vnode(580, 140, "v₁", fill=FILL_V, stroke=ACCENT, r=20))
    p.append(text(580, 178, "slack[v₁] = 3", size=11, bold=True, color=ACCENT))

    p.append(vnode(740, 140, "v₂", fill=FILL_V, stroke=ACCENT, r=20))
    p.append(text(740, 178, "slack[v₂] = 1 (min)", size=11, bold=True, color=ALERT))

    p.append(vnode(660, 240, "v₄", fill=FILL_V, stroke=ACCENT, r=20))
    p.append(text(660, 278, "slack[v₄] = 2", size=11, bold=True, color=ACCENT))

    # Зв'язки між S і стовпцями ззовні
    p.append(edge(290, 240, 740, 140, color=ALERT, sw=2.0, dash="3 3"))
    p.append(textbox(445, 210, "Δ = 1", size=11, bold=True, fill="#fef2f2", stroke=ALERT)[0])

    # Нижній опис модифікації потенціалів
    p.append(textbox(W / 2, 390,
                     "Коригування потенціалів на величину Δ: u[i] += Δ для i ∈ S, v[j] -= Δ для j ∈ T.\n"
                     "Для j ∉ T залишок slack зменшується: slack[j] -= Δ. При slack[j]=0 з'являється нове нульове ребро без рестарту пошуку.",
                     size=12, fill="#fffbeb", stroke=FRONT)[0])

    render(os.path.join(OUT, "fig3-alternating-tree-potentials.svg"), W, H, *p,
           title="Змінне дерево пошуку та оновлення Slack")


# ── ФІГ.4 Доповнюючий шлях та інверсія паросполучення ───────────────────────
def fig_augmenting_path_trace():
    W, H = 820, 390
    p = []

    # Ланцюжок вершин вздовж доповнюючого шляху
    xs = [110.0, 290.0, 470.0, 650.0]
    y_top = 110.0
    y_bot = 220.0

    p.append(textbox(W / 2, 35, "Інверсія ребер вздовж знайденого доповнюючого шляху", size=13, bold=True, fill=FILL, stroke=LINE)[0])

    # До інверсії
    p.append(text(50, y_top + 5, "ДО:", size=13, bold=True, color=INK))
    p.append(vnode(xs[0], y_top, "u₃", fill="#fee2e2", stroke=ALERT, r=18))
    p.append(vnode(xs[1], y_top, "v₃", fill="#fef3c7", stroke=FRONT, r=18))
    p.append(vnode(xs[2], y_top, "u₂", fill="#fee2e2", stroke=ALERT, r=18))
    p.append(vnode(xs[3], y_top, "v₂", fill=FILL_V, stroke=ACCENT, r=18))

    p.append(edge(xs[0], y_top, xs[1], y_top, color=FRONT, sw=2.5, dash="4 4"))
    p.append(edge(xs[1], y_top, xs[2], y_top, color=SETTLED, sw=3.2))
    p.append(edge(xs[2], y_top, xs[3], y_top, color=FRONT, sw=2.5, dash="4 4"))

    p.append(text(xs[0], y_top - 28, "вільний", size=10, color=ALERT))
    p.append(text((xs[0] + xs[1]) / 2, y_top - 12, "C'=0 (не в M)", size=10, color=FRONT))
    p.append(text((xs[1] + xs[2]) / 2, y_top - 12, "в M", size=10, color=SETTLED, bold=True))
    p.append(text((xs[2] + xs[3]) / 2, y_top - 12, "C'=0 (не в M)", size=10, color=FRONT))
    p.append(text(xs[3], y_top - 28, "вільний", size=10, color=ACCENT))

    # Стрілка інверсії
    p.append(arrow(W / 2 - 30, 165, W / 2 + 30, 165, color=INK, sw=2.5))
    p.append(text(W / 2, 160, "M' = M ⊕ P", size=11, bold=True, color=SETTLED))

    # Після інверсії
    p.append(text(50, y_bot + 5, "ПІСЛЯ:", size=13, bold=True, color=SETTLED))
    p.append(vnode(xs[0], y_bot, "u₃", fill=FILL_U, stroke=SETTLED, r=18))
    p.append(vnode(xs[1], y_bot, "v₃", fill=FILL_V, stroke=SETTLED, r=18))
    p.append(vnode(xs[2], y_bot, "u₂", fill=FILL_U, stroke=SETTLED, r=18))
    p.append(vnode(xs[3], y_bot, "v₂", fill=FILL_V, stroke=SETTLED, r=18))

    p.append(edge(xs[0], y_bot, xs[1], y_bot, color=SETTLED, sw=3.2))
    p.append(edge(xs[1], y_bot, xs[2], y_bot, color=FAR, sw=1.5, dash="4 4"))
    p.append(edge(xs[2], y_bot, xs[3], y_bot, color=SETTLED, sw=3.2))

    p.append(text(xs[0], y_bot + 30, "покритий", size=10, color=SETTLED))
    p.append(text((xs[0] + xs[1]) / 2, y_bot + 16, "новий зв'язок M", size=10, color=SETTLED, bold=True))
    p.append(text((xs[1] + xs[2]) / 2, y_bot + 16, "вилучено", size=10, color=FAR))
    p.append(text((xs[2] + xs[3]) / 2, y_bot + 16, "новий зв'язок M", size=10, color=SETTLED, bold=True))
    p.append(text(xs[3], y_bot + 30, "покритий", size=10, color=SETTLED))

    p.append(textbox(W / 2, 340,
                     "Інверсія ребер збільшує кількість насичених пар у паросполученні M рівно на 1.\n"
                     "Масив зворотних посилань way[j] дозволяє виконати ланцюгове перепризначення за O(N) кроків.",
                     size=12, fill="#f0fdf4", stroke=SETTLED)[0])

    render(os.path.join(OUT, "fig4-augmenting-path-trace.svg"), W, H, *p,
           title="Доповнюючий шлях та інверсія паросполучення")


if __name__ == "__main__":
    fig_matrix_reduction()
    fig_equality_subgraph()
    fig_alternating_tree()
    fig_augmenting_path_trace()
    print("Усі 4 фігури згенеровано успішно.")
