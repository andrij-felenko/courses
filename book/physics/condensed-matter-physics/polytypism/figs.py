# -*- coding: utf-8 -*-
import sys
import os
import math

# Add path to scripts/ in repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

# 1. Stacking Sequences (3C, 2H, 4H, 6H)
def gen_stacking_sequences(out_path):
    w, h = 840, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Послідовності укладання атомних шарів у політипах карбіду кремнію (SiC)", size=16, bold=True))
    
    polytypes = [
        {"title": "3C-SiC (Кубічний)", "code": "ABCABC", "sym": "k k k k k k", "seq": ["A","B","C","A","B","C"], "hex": "0% h"},
        {"title": "2H-SiC (Гексагональний)", "code": "ABABAB", "sym": "h h h h h h", "seq": ["A","B","A","B","A","B"], "hex": "100% h"},
        {"title": "4H-SiC (4-шаровий)", "code": "ABCBAB", "sym": "h k h k h k", "seq": ["A","B","C","B","A","B"], "hex": "50% h"},
        {"title": "6H-SiC (6-шаровий)", "code": "ABCACBAB", "sym": "h k k h k k", "seq": ["A","B","C","A","C","B"], "hex": "33.3% h"}
    ]
    
    col_w = 190
    gap = 15
    top_y = 55
    panel_h = 340
    
    pos_x = {"A": 0, "B": 24, "C": 48}
    pos_colors = {"A": POS, "B": NEG, "C": FIELD}
    
    for idx, pt in enumerate(polytypes):
        px = 20 + idx * (col_w + gap)
        py = top_y
        
        frags.append(rect(px, py, col_w, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))        
        frags.append(text(px + col_w/2, py + 22, pt["title"], size=12, bold=True, color="#0f172a"))        
        frags.append(text(px + col_w/2, py + 40, f"Гексагональність: {pt['hex']}", size=10, color=MUTED, italic=True))
        
        axis_x = px + 35
        frags.append(line(axis_x, py + 295, axis_x, py + 55, color="#94a3b8", sw=1.5, dash="4,4"))
        frags.append(text(axis_x, py + 50, "c-вісь [0001]", size=9, color=MUTED))
        
        base_y = py + 280
        layer_h = 36
        
        for l_idx, pos in enumerate(pt["seq"]):
            ly = base_y - l_idx * layer_h
            cx = axis_x + 35 + pos_x[pos]
            
            frags.append(line(axis_x + 10, ly, px + col_w - 15, ly, color="#e2e8f0", sw=1.0))
            frags.append(circle(cx, ly, 10, fill=pos_colors[pos], stroke="#1e293b", sw=1.2))
            frags.append(text(cx, ly + 3.5, pos, size=10, color="#ffffff", bold=True))
            
            sym_char = pt["sym"].split()[l_idx]
            sym_color = "#b91c1c" if sym_char == "h" else "#1d4ed8"
            frags.append(text(px + col_w - 25, ly + 3.5, f"({sym_char})", size=10, color=sym_color, bold=True))
        
        frags.append(text(px + col_w/2, py + 315, f"Послідовність: {pt['code']}", size=10, color=INK, bold=True))
        frags.append(text(px + col_w/2, py + 330, f"Ягодзінський: ({pt['sym']})", size=9, color=MUTED))

    return render(out_path, w, h, *frags)

# 2. Ramsdell-Jagodzinski Mapping & Bandgap Correlation
def gen_ramsdell_jagodzinski_mapping(out_path):
    w, h = 840, 380
    frags = []
    
    frags.append(text(w / 2, 25, "Залежність ширини забороненої зони E_g від ступеня гексагональності α_h", size=16, bold=True))
    
    ax_x, ax_y = 70, 60
    ax_w, ax_h = 440, 270
    
    frags.append(rect(ax_x - 10, ax_y - 10, ax_w + 20, ax_h + 30, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    
    frags.append(line(ax_x, ax_y + ax_h, ax_x + ax_w, ax_y + ax_h, color=INK, sw=2.0))
    frags.append(line(ax_x, ax_y, ax_x, ax_y + ax_h, color=INK, sw=2.0))
    
    frags.append(text(ax_x + ax_w/2, ax_y + ax_h + 38, "Гексагональність α_h (%)", size=12, bold=True))
    frags.append(text(ax_x - 45, ax_y + ax_h/2, "E_g (еВ)", size=12, bold=True))
    
    pts_data = [
        {"poly": "3C", "alpha": 0.0, "eg": 2.36, "x_off": 0, "y_off": -14},
        {"poly": "8H", "alpha": 25.0, "eg": 2.80, "x_off": 0, "y_off": -14},
        {"poly": "6H", "alpha": 33.3, "eg": 3.02, "x_off": -15, "y_off": 14},
        {"poly": "15R", "alpha": 40.0, "eg": 2.98, "x_off": 15, "y_off": 14},
        {"poly": "4H", "alpha": 50.0, "eg": 3.26, "x_off": 0, "y_off": -14},
        {"poly": "2H", "alpha": 100.0, "eg": 3.33, "x_off": 0, "y_off": -14}
    ]
    
    def map_x(alpha):
        return ax_x + (alpha / 100.0) * ax_w
    
    def map_y(eg):
        eg_min, eg_max = 2.2, 3.5
        return ax_y + ax_h - ((eg - eg_min) / (eg_max - eg_min)) * ax_h

    for tick_a in [0, 25, 33.3, 50, 75, 100]:
        tx = map_x(tick_a)
        frags.append(line(tx, ax_y + ax_h, tx, ax_y + ax_h + 5, color=INK, sw=1.5))
        frags.append(text(tx, ax_y + ax_h + 18, f"{tick_a:.0f}%" if tick_a != 33.3 else "33%", size=10))
        frags.append(line(tx, ax_y, tx, ax_y + ax_h, color="#f1f5f9", sw=1.0))
        
    for tick_e in [2.4, 2.6, 2.8, 3.0, 3.2, 3.4]:
        ty = map_y(tick_e)
        frags.append(line(ax_x - 5, ty, ax_x, ty, color=INK, sw=1.5))
        frags.append(text(ax_x - 18, ty + 4, f"{tick_e:.1f}", size=10))
        frags.append(line(ax_x, ty, ax_x + ax_w, ty, color="#f1f5f9", sw=1.0))

    trend_p1 = (map_x(0), map_y(2.36))
    trend_p2 = (map_x(100), map_y(3.33))
    frags.append(line(trend_p1[0], trend_p1[1], trend_p2[0], trend_p2[1], color="#94a3b8", sw=2.0, dash="6,4"))
    
    for pt in pts_data:
        cx = map_x(pt["alpha"])
        cy = map_y(pt["eg"])
        frags.append(circle(cx, cy, 6, fill=POS, stroke="#1e293b", sw=1.5))
        frags.append(text(cx + pt["x_off"], cy + pt["y_off"], f"{pt['poly']} ({pt['eg']} еВ)", size=10, bold=True, color="#0f172a"))

    info_x, info_y, info_w, info_h = 540, 60, 280, 270
    frags.append(rect(info_x, info_y, info_w, info_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(info_x + info_w/2, info_y + 22, "Правила номенклатури", size=13, bold=True))
    
    lines_info = [
        "• Рамсделл (N L):",
        "  N — шар у періоді,",
        "  L — C (куб), H (гекс), R (ромб).",
        "",
        "• Ягодзінський (h / k):",
        "  h — гексагональне отчення",
        "      (сусіди однакові: ABA),",
        "  k — кубічне оточення",
        "      (сусіди різні: ABC).",
        "",
        "• Жданов (n, m):",
        "  к-сть шарів вперед/назад."
    ]
    
    for i, ln in enumerate(lines_info):
        is_b = ln.startswith("•")
        c = "#0f172a" if is_b else MUTED
        sz = 10 if is_b else 9.5
        frags.append(text(info_x + 15, info_y + 48 + i * 18, ln, size=sz, anchor="start", bold=is_b, color=c))

    return render(out_path, w, h, *frags)

# 3. Step-Flow Epitaxy Mechanism
def gen_step_flow_epitaxy(out_path):
    w, h = 840, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Механізм пошарової епітаксії step-flow на відхиленій підкладці SiC", size=16, bold=True))
    
    p1_x, p1_y, p1_w, p1_h = 30, 55, 375, 275
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 22, "Точно торець [0001] (On-axis)", size=13, bold=True, color="#991b1b"))
    frags.append(text(p1_x + p1_w/2, p1_y + 40, "Утворення потрійних зародків 3C-SiC", size=10, color=MUTED, italic=True))
    
    frags.append(rect(p1_x + 30, p1_y + 150, 315, 90, fill="#cbd5e1", stroke="#475569", sw=1.5))
    frags.append(text(p1_x + 187, p1_y + 195, "4H-SiC Підкладка (Гладка поверхня)", size=11, bold=True, color="#1e293b"))
    
    frags.append(rect(p1_x + 100, p1_y + 120, 60, 30, fill="#fca5a5", stroke="#b91c1c", sw=1.5, rx=3))
    frags.append(text(p1_x + 130, p1_y + 138, "3C Зародок", size=9, bold=True, color="#7f1d1d"))
    
    frags.append(rect(p1_x + 220, p1_y + 120, 60, 30, fill="#fca5a5", stroke="#b91c1c", sw=1.5, rx=3))
    frags.append(text(p1_x + 250, p1_y + 138, "3C Зародок", size=9, bold=True, color="#7f1d1d"))
    
    frags.append(arrow(p1_x + 130, p1_y + 80, p1_x + 130, p1_y + 115, color=POS, sw=1.5))
    frags.append(text(p1_x + 130, p1_y + 70, "Атоми Si + C", size=10, color=POS, bold=True))

    p2_x, p2_y, p2_w, p2_h = 435, 55, 375, 275
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 22, "Відхилена поверхня (4° Off-axis)", size=13, bold=True, color="#166534"))
    frags.append(text(p2_x + p2_w/2, p2_y + 40, "Точне відтворення політипу 4H-SiC", size=10, color=MUTED, italic=True))
    
    steps_path = f"M {p2_x + 30} {p2_y + 220} L {p2_x + 100} {p2_y + 220} L {p2_x + 100} {p2_y + 180} L {p2_x + 180} {p2_y + 180} L {p2_x + 180} {p2_y + 140} L {p2_x + 260} {p2_y + 140} L {p2_x + 260} {p2_y + 100} L {p2_x + 345} {p2_y + 100} L {p2_x + 345} {p2_y + 250} L {p2_x + 30} {p2_y + 250} Z"
    frags.append(path(steps_path, fill="#cbd5e1", stroke="#475569", sw=1.5))
    
    frags.append(circle(p2_x + 120, p2_y + 172, 6, fill=FIELD, stroke="#14532d", sw=1.2))
    frags.append(arrow(p2_x + 135, p2_y + 172, p2_x + 107, p2_y + 172, color=FIELD, sw=1.5))
    
    frags.append(text(p2_x + 145, p2_y + 160, "Міграція до сходинки", size=9, bold=True, color="#14532d"))
    
    frags.append(line(p2_x + 40, p2_y + 215, p2_x + 330, p2_y + 95, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(p2_x + 200, p2_y + 265, "Кут відхилення α = 4° до [11-20]", size=10, bold=True, color="#0f172a"))

    return render(out_path, w, h, *frags)

# 4. XRD Reciprocal Rod 10L Profiles
def gen_xrd_reciprocal_rod(out_path):
    w, h = 840, 380
    frags = []
    
    frags.append(text(w / 2, 25, "Дифракційні профілі інтенсивності уздовж стержня (10L) оберненого простору", size=16, bold=True))
    
    ax_x, ax_y = 60, 60
    ax_w, ax_h = 740, 270
    
    frags.append(rect(ax_x - 10, ax_y - 10, ax_w + 20, ax_h + 30, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    
    frags.append(line(ax_x, ax_y + ax_h, ax_x + ax_w, ax_y + ax_h, color=INK, sw=2.0))
    frags.append(text(ax_x + ax_w/2, ax_y + ax_h + 20, "Індекс L уздовж стержня (10L)", size=12, bold=True))
    
    poly_plots = [
        {"name": "3C-SiC", "y0": ax_y + 40, "peaks": [1/3, 4/3, 7/3], "color": NEG},
        {"name": "4H-SiC", "y0": ax_y + 105, "peaks": [1/4, 2/4, 3/4, 5/4, 6/4, 7/4], "color": POS},
        {"name": "6H-SiC", "y0": ax_y + 170, "peaks": [1/6, 2/6, 3/6, 4/6, 5/6, 7/6], "color": FIELD},
        {"name": "15R-SiC", "y0": ax_y + 235, "peaks": [1/15, 4/15, 7/15, 11/15, 14/15], "color": "#7c3aed"}
    ]
    
    for pp in poly_plots:
        frags.append(text(ax_x + 10, pp["y0"] - 10, pp["name"], size=11, bold=True, color=pp["color"], anchor="start"))
        frags.append(line(ax_x + 70, pp["y0"], ax_x + ax_w - 20, pp["y0"], color="#cbd5e1", sw=1.0))
        
        l_min, l_max = 0.0, 2.5
        def map_l(l_val):
            return ax_x + 70 + ((l_val - l_min) / (l_max - l_min)) * (ax_w - 90)
        
        for p_val in pp["peaks"]:
            px = map_l(p_val)
            frags.append(line(px, pp["y0"], px, pp["y0"] - 22, color=pp["color"], sw=2.2))
            frags.append(circle(px, pp["y0"] - 22, 3, fill=pp["color"], stroke=pp["color"], sw=1.0))

    return render(out_path, w, h, *frags)

def main():
    print("Generating polytypism figures...")
    gen_stacking_sequences(os.path.join(OUT_DIR, "stacking-sequences.svg"))
    gen_ramsdell_jagodzinski_mapping(os.path.join(OUT_DIR, "ramsdell-jagodzinski-mapping.svg"))
    gen_step_flow_epitaxy(os.path.join(OUT_DIR, "step-flow-epitaxy.svg"))
    gen_xrd_reciprocal_rod(os.path.join(OUT_DIR, "xrd-reciprocal-rod.svg"))
    print("Done generating SVGs.")

if __name__ == "__main__":
    main()
