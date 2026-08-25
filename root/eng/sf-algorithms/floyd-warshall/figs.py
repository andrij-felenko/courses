# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"   # зелений — базовий вузол / оптимум
FRONT   = "#e08a1e"   # помаранчевий — транзитний / активний вузол k
ALERT   = "#c0392b"   # червоний — від'ємний цикл / застереження
FAR     = "#9aa3af"   # сірий — недосяжний / пасивний
EDGEC   = "#475569"   # колір контуру ребер

def node(cx, cy, name, subtitle=None, fill=FILL, stroke=LINE, r=22):
    """Вузол графа з назвою та підписом."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5 if not subtitle else cy - 2, name, size=15, color=INK, bold=True)
    if subtitle:
        out += text(cx, cy + 13, subtitle, size=10, color=MUTED, bold=False)
    return out

def directed_edge(x1, y1, x2, y2, w=None, r1=22, r2=22, col=EDGEC, sw=2.0, dash=None, label_side="top", curve=0.0):
    """Орієнтоване ребро зі стрілкою та вагою."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    
    if abs(curve) < 1e-3:
        ax, ay = x1 + ux * r1, y1 + uy * r1
        bx, by = x2 - ux * r2, y2 - uy * r2
        out = line(ax, ay, bx, by, color=col, sw=sw, dash=dash)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        
        ah_len, ah_w = 9.0, 4.0
        p1_x = bx - ux * ah_len + px * ah_w
        p1_y = by - uy * ah_len + py * ah_w
        p2_x = bx - ux * ah_len - px * ah_w
        p2_y = by - uy * ah_len - py * ah_w
        out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none"/>' %
                (bx, by, p1_x, p1_y, p2_x, p2_y, col))
    else:
        cx = (x1 + x2) / 2 + px * curve
        cy = (y1 + y2) / 2 + py * curve
        ax, ay = x1 + ux * r1, y1 + uy * r1
        bx, by = x2 - ux * r2, y2 - uy * r2
        d_str = ' stroke-dasharray="%s"' % dash if dash else ''
        out = ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
               (ax, ay, cx, cy, bx, by, col, sw, d_str))
        mx, my = (ax + 2 * cx + bx) / 4, (ay + 2 * cy + by) / 4
        
        tdx, tdy = bx - cx, by - cy
        tL = math.hypot(tdx, tdy) or 1.0
        tux, tuy = tdx / tL, tdy / tL
        tpx, tpy = -tuy, tux
        ah_len, ah_w = 9.0, 4.0
        p1_x = bx - tux * ah_len + tpx * ah_w
        p1_y = by - tuy * ah_len + tpy * ah_w
        p2_x = bx - tux * ah_len - tpx * ah_w
        p2_y = by - tuy * ah_len - tpy * ah_w
        out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none"/>' %
                (bx, by, p1_x, p1_y, p2_x, p2_y, col))
        
    if w is not None:
        offset = 14 if label_side == "top" else -14
        lx, ly = mx + px * offset, my + py * offset
        w_str = str(w)
        is_neg = isinstance(w, (int, float)) and w < 0
        w_col = ALERT if is_neg else INK
        out += circle(lx, ly, 10, fill=BG, stroke=col, sw=1.0)
        out += text(lx, ly + 3.5, w_str, size=11, color=w_col, bold=True)
        
    return out

# ── ФІГ. 1: Крок динамічного програмування та проміжна вершина k ──────────────
def fig_intermediate_vertex():
    W, H = 760, 310
    p = []
    
    ix, iy = 110.0, 180.0
    jx, jy = 650.0, 180.0
    kx, ky = 380.0, 70.0
    
    # Хмарка підмножини {1..k-1}
    p.append(rect(200, 140, 360, 75, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=12))
    p.append(text(380, 182, "проміжні вершини з підмножини {1, 2, ..., k−1}", size=12.5, color=MUTED))
    
    # Прямий або попередній шлях i -> j
    p.append(directed_edge(ix, iy, jx, jy, w="9", col="#64748b", sw=2.0, curve=0.0, label_side="bottom"))
    
    # Шлях i -> k
    p.append(directed_edge(ix, iy, kx, ky, w="3", col=FRONT, sw=2.2, label_side="top"))
    
    # Шлях k -> j
    p.append(directed_edge(kx, ky, jx, jy, w="4", col=FRONT, sw=2.2, label_side="top"))
    
    # Вузли
    p.append(node(ix, iy, "i", "старт", fill="#eaf7ee", stroke=SETTLED, r=24))
    p.append(node(jx, jy, "j", "фініш", fill="#eaf7ee", stroke=SETTLED, r=24))
    p.append(node(kx, ky, "k", "транзит", fill="#fff7ee", stroke=FRONT, r=25))
    
    # Пояснювальний блок
    tb, bw, bh = textbox(380, 260,
                         "dp[k][i][j] = min( dp[k−1][i][j],  dp[k−1][i][k] + dp[k−1][k][j] )\n"
                         "порівняння: зберегти шлях через {1..k−1} (вага 9) чи піти через k (вага 3 + 4 = 7) → d[i][j] := 7",
                         size=12.5, bold=True, fill="#fff7ee", stroke=FRONT, pad=7)
    p.append(tb)
    
    render(os.path.join(OUT, "intermediate-vertex.svg"), W, H, *p,
           title="Вибір найкоротшого шляху через проміжну вершину k")

# ── ФІГ. 2: Зріз матриці DP та інваріант незмінності k-го рядка і стовпця ───────
def fig_dp_cube_layers():
    W, H = 760, 350
    p = []
    
    ox1, oy1 = 60, 75
    ox2, oy2 = 440, 75
    cs = 44
    
    def draw_grid(ox, oy, tag):
        res = []
        res.append(text(ox + cs * 2.5, oy - 20, tag, size=14, bold=True, color=INK))
        for col_idx, col_name in enumerate(["1", "...", "k", "...", "V"]):
            res.append(text(ox + col_idx * cs + cs/2, oy - 5, col_name, size=12, color=MUTED, bold=(col_name=="k")))
        for row_idx, row_name in enumerate(["1", "...", "i", "...", "V"]):
            res.append(text(ox - 12, oy + row_idx * cs + cs/2 + 4, row_name, size=12, color=MUTED, bold=(row_name=="i")))
            
        for r_i in range(5):
            for c_j in range(5):
                x = ox + c_j * cs
                y = oy + r_i * cs
                fill_c = BG
                stroke_c = "#cbd5e1"
                sw_c = 1.0
                
                if r_i == 2 and c_j == 2:
                    fill_c = "#fff7ee"
                    stroke_c = FRONT
                    sw_c = 1.8
                elif r_i == 2 and c_j == 4:
                    fill_c = "#eaf7ee"
                    stroke_c = SETTLED
                    sw_c = 2.0
                elif r_i == 2 or c_j == 2:
                    fill_c = "#fdfbf7"
                
                lbl = ""
                if r_i == 2 and c_j == 2:
                    lbl = "d[i][k]"
                elif r_i == 2 and c_j == 4:
                    lbl = "d[i][j]"
                    
                res.append(rect(x, y, cs, cs, fill=fill_c, stroke=stroke_c, sw=sw_c, rx=2))
                if lbl:
                    res.append(text(x + cs/2, y + cs/2 + 4, lbl, size=10, bold=True, color=INK))
        return res

    p.extend(draw_grid(ox1, oy1, "Матриця на кроці k−1"))
    
    p.append(arrow(ox1 + cs*5 + 20, oy1 + cs*2.5, ox2 - 20, oy2 + cs*2.5, color=FRONT, sw=2.5))
    p.append(text((ox1 + cs*5 + ox2)/2, oy1 + cs*2.5 - 12, "крок k", size=12, bold=True, color=FRONT))
    
    p.extend(draw_grid(ox2, oy2, "Матриця на кроці k (In-place)"))
    
    tb, bw, bh = textbox(380, 315,
                         "Інваріант пам'яті: рядок d[k][*] та стовпець d[*][k] не змінюються на ітерації k.\n"
                         "Тому оновлення d[i][j] := min(d[i][j], d[i][k] + d[k][j]) безпечно робити в одній 2D матриці.",
                         size=12, bold=True, fill=FILL, stroke=LINE, pad=6)
    p.append(tb)
    
    render(os.path.join(OUT, "dp-cube-layers.svg"), W, H, *p,
           title="Оновлення клітинки (i, j) через перетин i-го рядка та k-го стовпця")

# ── ФІГ. 3: Виявлення від'ємного циклу на діагоналі та поширення -INF ─────────
def fig_negative_cycle_matrix():
    W, H = 760, 310
    p = []
    
    gx, gy = 140.0, 120.0
    p.append(node(gx - 60, gy - 45, "1", "старт", fill="#eaf7ee", stroke=SETTLED))
    p.append(node(gx + 40, gy - 45, "2", "цикл", fill="#fdecea", stroke=ALERT))
    p.append(node(gx + 40, gy + 45, "3", "цикл", fill="#fdecea", stroke=ALERT))
    p.append(node(gx + 130, gy, "4", "фініш", fill=FILL, stroke=LINE))
    
    p.append(directed_edge(gx - 60, gy - 45, gx + 40, gy - 45, w="2", col=EDGEC))
    p.append(directed_edge(gx + 40, gy - 45, gx + 40, gy + 45, w="−4", col=ALERT, sw=2.2))
    p.append(directed_edge(gx + 40, gy + 45, gx + 40, gy - 45, w="1", col=ALERT, sw=2.2, curve=35))
    p.append(directed_edge(gx + 40, gy + 45, gx + 130, gy, w="3", col=EDGEC))
    
    p.append(text(gx + 30, gy + 82, "сума циклу 2 ⇄ 3: (−4) + 1 = −3 < 0", size=11.5, color=ALERT, bold=True))
    
    mx, my = 430.0, 45.0
    cs = 44
    
    p.append(text(mx + cs * 2, my - 10, "Матриця відстаней D після V ітерацій", size=13, bold=True, color=INK))
    
    headers = ["1", "2", "3", "4"]
    for i, h_txt in enumerate(headers):
        p.append(text(mx + i * cs + cs/2, my + 6, h_txt, size=12, color=MUTED, bold=True))
        p.append(text(mx - 10, my + 24 + i * cs + cs/2, h_txt, size=12, color=MUTED, bold=True))
        
    vals = [
        ["0", "−∞", "−∞", "−∞"],
        ["∞", "−3", "−4", "−∞"],
        ["∞", "−2", "−3", "−∞"],
        ["∞", "∞", "∞", "0"]
    ]
    
    for r_i in range(4):
        for c_j in range(4):
            x = mx + c_j * cs
            y = my + 14 + r_i * cs
            val = vals[r_i][c_j]
            
            fill_c = BG
            stroke_c = "#cbd5e1"
            sw_c = 1.0
            val_col = INK
            bold_val = False
            
            if r_i == c_j and (val.startswith("−") or int(val if val not in ["−∞", "∞"] else 0) < 0):
                fill_c = "#fdecea"
                stroke_c = ALERT
                sw_c = 2.0
                val_col = ALERT
                bold_val = True
            elif val == "−∞":
                fill_c = "#fff5f5"
                val_col = ALERT
                bold_val = True
                
            p.append(rect(x, y, cs, cs, fill=fill_c, stroke=stroke_c, sw=sw_c, rx=3))
            p.append(text(x + cs/2, y + cs/2 + 4, val, size=12, color=val_col, bold=bold_val))
            
    tb, bw, bh = textbox(380, 270,
                         "Діагностика: якщо d[v][v] < 0, вершина v лежить на від'ємному циклі.\n"
                         "Для всіх пар (i, j), де шлях проходить крізь таку вершину v, істинна відстань дорівнює −∞.",
                         size=12, bold=True, fill="#fff5f5", stroke=ALERT, pad=6)
    p.append(tb)
    
    render(os.path.join(OUT, "negative-cycle-matrix.svg"), W, H, *p,
           title="Виявлення від'ємних циклів за від'ємними значеннями головної діагоналі")

# ── ФІГ. 4: Блокова схема кеш-оптимізації (Tiled Floyd-Warshall) ──────────────
def fig_cache_tiling():
    W, H = 760, 360
    p = []
    
    ox, oy = 70.0, 55.0
    bs = 42 # розмір блоку B x B
    
    p.append(text(ox + bs * 2.5, oy - 15, "Матриця V × V розбита на блоки B × B", size=13.5, bold=True, color=INK))
    
    for bi in range(5):
        for bj in range(5):
            x = ox + bj * bs
            y = oy + bi * bs
            
            fill_c = "#f8fafc"
            stroke_c = "#cbd5e1"
            sw_c = 1.0
            txt_c = MUTED
            b_name = ""
            
            if bi == 2 and bj == 2:
                fill_c = "#fdecea"
                stroke_c = ALERT
                sw_c = 2.2
                txt_c = ALERT
                b_name = "Фаза 1\nB(k,k)"
            elif bi == 2:
                fill_c = "#fff7ee"
                stroke_c = FRONT
                sw_c = 1.8
                txt_c = FRONT
                b_name = "Фаза 2\nB(k,j)"
            elif bj == 2:
                fill_c = "#fff7ee"
                stroke_c = FRONT
                sw_c = 1.8
                txt_c = FRONT
                b_name = "Фаза 2\nB(i,k)"
            elif (bi, bj) == (1, 4):
                fill_c = "#eaf7ee"
                stroke_c = SETTLED
                sw_c = 2.0
                txt_c = SETTLED
                b_name = "Фаза 3\nB(i,j)"
            else:
                b_name = "Фаза 3"
                
            p.append(rect(x, y, bs, bs, fill=fill_c, stroke=stroke_c, sw=sw_c, rx=3))
            
            lines = b_name.split("\n")
            if len(lines) == 1:
                p.append(text(x + bs/2, y + bs/2 + 4, lines[0], size=9.0, color=txt_c, bold=(txt_c!=MUTED)))
            else:
                p.append(text(x + bs/2, y + bs/2 - 3, lines[0], size=9.0, color=txt_c, bold=True))
                p.append(text(x + bs/2, y + bs/2 + 9, lines[1], size=9.0, color=txt_c, bold=True))
                
    # Панель фаз праворуч
    px, py = 370.0, 55.0
    p.append(rect(px, py, 340, 210, fill=BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(px + 170, py + 24, "Три фази обчислення кроку k:", size=13, bold=True, color=INK))
    
    p.append(circle(px + 24, py + 62, 10, fill="#fdecea", stroke=ALERT, sw=1.5))
    p.append(text(px + 24, py + 66, "1", size=11, bold=True, color=ALERT))
    p.append(text(px + 44, py + 66, "Оновлення блоку B(k, k) у кеші L1", size=11.5, color=INK, anchor="start", bold=True))
    
    p.append(circle(px + 24, py + 107, 10, fill="#fff7ee", stroke=FRONT, sw=1.5))
    p.append(text(px + 24, py + 111, "2", size=11, bold=True, color=FRONT))
    p.append(text(px + 44, py + 111, "Оновлення хрестовини B(i,k) та B(k,j)", size=11.5, color=INK, anchor="start", bold=True))
    
    p.append(circle(px + 24, py + 152, 10, fill="#eaf7ee", stroke=SETTLED, sw=1.5))
    p.append(text(px + 24, py + 156, "3", size=11, bold=True, color=SETTLED))
    p.append(text(px + 44, py + 156, "Паралельне оновлення всіх інших B(i, j)", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(px + 44, py + 174, "(повна незалежність, OpenMP/SIMD)", size=10.5, color=MUTED, anchor="start"))
    
    tb, bw, bh = textbox(380, 315,
                         "Тайлінг усуває кеш-промахи: блок B × B повністю вміщується у швидкій пам'яті L1 Data Cache,\n"
                         "забезпечуючи прискорення у 3–6 разів на великих матрицях (V > 1000).",
                         size=12, bold=True, fill=FILL, stroke=LINE, pad=6)
    p.append(tb)
    
    render(os.path.join(OUT, "cache-tiling.svg"), W, H, *p,
           title="Блокова кеш-оптимізація матричного алгоритму Флойда–Уоршелла")

if __name__ == "__main__":
    fig_intermediate_vertex()
    fig_dp_cube_layers()
    fig_negative_cycle_matrix()
    fig_cache_tiling()
    print("All figures generated successfully.")
