# -*- coding: utf-8 -*-
import os
import sys
import math

# Add scripts/ directory from workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def generate_landscape_trapping():
    path = os.path.join(IMG_DIR, 'landscape-trapping-and-tunneling.svg')
    w, h = 800, 490
    
    frags = []
    # Background panel
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Title & Subtitle
    frags.append(text(w / 2, 32, "Енергетичний рельєф: жадібна пастка проти подолання бар'єрів у відпалі", size=15, bold=True))
    frags.append(text(w / 2, 52, "Жадібний спуск застрягає в локальному мінімумі, тоді як SA долає потенційні бар'єри", size=12, color=MUTED))
    
    # Axes
    ax_x0, ax_y0 = 60, 410
    ax_w, ax_h = 680, 270
    frags.append(arrow(ax_x0, ax_y0, ax_x0 + ax_w + 30, ax_y0, color=LINE, sw=1.5)) # X axis
    frags.append(arrow(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h - 25, color=LINE, sw=1.5)) # Y axis
    
    frags.append(text(ax_x0 + ax_w + 25, ax_y0 + 26, "Простір станів (S)", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(ax_x0 + 10, ax_y0 - ax_h - 15, "Енергія E(s)", size=12, color=INK, anchor="start", bold=True))
    
    # Energy landscape curve points
    curve_pts = [
        (70, 300), (120, 290), (160, 220), (210, 200), (260, 270),
        (310, 320), (350, 340), (390, 300), (430, 230), (470, 210),
        (510, 260), (550, 330), (600, 380), (640, 390), (680, 330), (730, 270)
    ]
    path_d = ["M %d %d" % (curve_pts[0][0], curve_pts[0][1])]
    for i in range(1, len(curve_pts)):
        p0 = curve_pts[i-1]
        p1 = curve_pts[i]
        cx1 = (p0[0] + p1[0]) / 2
        path_d.append("Q %d %d %d %d" % (cx1, p0[1], p1[0], p1[1]))
    
    frags.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % " ".join(path_d))
    
    # Shade under curve
    shade_d = list(path_d)
    shade_d.append("L %d %d L %d %d Z" % (curve_pts[-1][0], ax_y0, curve_pts[0][0], ax_y0))
    frags.append('<path d="%s" fill="#eff6ff" opacity="0.5"/>' % " ".join(shade_d))
    
    # Local Minimum marker at (350, 340)
    frags.append(circle(350, 340, 5, fill=POS, stroke="#991b1b", sw=2))
    b_local, _, _ = textbox(350, 375, "Локальний мінімум\n(Пастка жадібного спуску)", size=11, fill="#fef2f2", stroke=POS, sw=1.2)
    frags.append(b_local)
    
    # Global Minimum marker at (640, 390)
    frags.append(circle(640, 390, 6, fill=FIELD, stroke="#166534", sw=2))
    b_global, _, _ = textbox(570, 440, "Глобальний мінімум (Оптимальний стан s*)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    frags.append(b_global)
    
    # Energy barrier ΔE at x=470 (peak at y=210, local min at y=340)
    frags.append(line(350, 340, 470, 340, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(470, 340, 470, 210, color=NEG, sw=1.5))
    frags.append(arrow(470, 275, 470, 210, color=NEG, sw=1.5))
    frags.append(arrow(470, 275, 470, 340, color=NEG, sw=1.5))
    frags.append(text(510, 275, "Бар'єр ΔE", size=11, color=NEG, bold=True))
    
    # Greedy trajectory
    frags.append(circle(270, 280, 4, fill=POS, stroke=LINE, sw=1.5))
    frags.append(arrow(270, 280, 340, 335, color=POS, sw=2))
    frags.append(text(285, 310, "Жадібний спуск (ΔE < 0)", size=10, color=POS, bold=True))
    
    # SA trajectory over the barrier
    frags.append(circle(350, 340, 4, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append('<path d="M 355 335 Q 470 145 585 365" fill="none" stroke="#059669" stroke-width="2.2" stroke-dasharray="4,4" marker-end="url(#arrow)"/>')
    b_sa_step, _, _ = textbox(470, 115, "Стрибок SA через бар'єр при високій T\nЙмовірність P = exp(−ΔE / T)", size=11, fill="#ecfdf5", stroke=FIELD, sw=1.2)
    frags.append(b_sa_step)
    
    render(path, w, h, *frags)
    return path

def generate_metropolis_probability():
    path = os.path.join(IMG_DIR, 'metropolis-acceptance-probability.svg')
    w, h = 780, 430
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Title & Subtitle
    frags.append(text(w / 2, 34, "Критерій Метрополіса: ймовірність прийняття погіршення P(ΔE, T)", size=15, bold=True))
    frags.append(text(w / 2, 54, "При ΔE ≤ 0 перехід приймається безумовно (P = 1); при ΔE > 0 — з експоненційною ймовірністю", size=12, color=MUTED))
    
    # Graph area
    gx0, gy0 = 270, 350
    gw, gh = 460, 240
    
    # Y-axis (P: 0.0 to 1.0)
    frags.append(arrow(gx0, gy0, gx0, gy0 - gh - 20, color=LINE, sw=1.5))
    frags.append(text(gx0 - 15, gy0 - gh - 15, "Ймовірність P", size=12, bold=True, anchor="start"))
    
    # X-axis (ΔE: 0 to 50)
    frags.append(arrow(gx0 - 90, gy0, gx0 + gw + 20, gy0, color=LINE, sw=1.5))
    frags.append(text(gx0 + gw + 15, gy0 + 20, "Зміна енергії ΔE", size=12, bold=True, anchor="end"))
    
    # Zero vertical line
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color="#9ca3af", sw=1, dash="3,3"))
    
    # Y-ticks
    for p_val, y_off in [(0.0, 0), (0.25, 55), (0.5, 110), (0.75, 165), (1.0, 220)]:
        y_pos = gy0 - y_off
        frags.append(line(gx0 - 5, y_pos, gx0, y_pos, color=LINE, sw=1.2))
        frags.append(text(gx0 - 10, y_pos + 4, "%.2f" % p_val, size=11, color=MUTED, anchor="end"))
        if p_val > 0:
            frags.append(line(gx0, y_pos, gx0 + gw, y_pos, color="#f3f4f6", sw=1))
    
    # Left region: ΔE <= 0 (P = 1.0)
    frags.append(line(gx0 - 90, gy0 - 220, gx0, gy0 - 220, color=FIELD, sw=3))
    frags.append(circle(gx0, gy0 - 220, 4, fill=FIELD, stroke=LINE, sw=1.5))
    
    b_imp, _, _ = textbox(gx0 - 65, gy0 - 260, "Покращення (ΔE ≤ 0)\nP = 1.0 (завжди)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.2, bold=True)
    frags.append(b_imp)
    
    # Right region: ΔE > 0 curves for different Temperatures
    # 1. High Temperature (T = 50): P = exp(-dE / 50)
    pts_high = []
    for de in range(0, 51):
        x = gx0 + (de / 50.0) * gw
        p = math.exp(-de / 50.0)
        y = gy0 - p * 220
        pts_high.append((x, y))
    d_high = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_high)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_high, POS))
    
    # 2. Medium Temperature (T = 15): P = exp(-dE / 15)
    pts_med = []
    for de in range(0, 51):
        x = gx0 + (de / 50.0) * gw
        p = math.exp(-de / 15.0)
        y = gy0 - p * 220
        pts_med.append((x, y))
    d_med = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_med)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_med, "#d97706"))
    
    # 3. Low Temperature (T = 4): P = exp(-dE / 4)
    pts_low = []
    for de in range(0, 51):
        x = gx0 + (de / 50.0) * gw
        p = math.exp(-de / 4.0)
        y = gy0 - p * 220
        pts_low.append((x, y))
    d_low = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_low)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_low, NEG))
    
    # Legend panel on the left side
    leg_x, leg_y = 135, 200
    b_leg, _, _ = textbox(leg_x, leg_y, 
                          "Температурний режим:\n\n"
                          "● Висока T (T = 50)\n  Майже всі погіршення приймаються\n\n"
                          "● Середня T (T = 15)\n  Приймаються лише малі ΔE\n\n"
                          "● Низька T (T = 4)\n  Практично чистий жадібний спуск",
                          size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, pad=12)
    frags.append(b_leg)
    
    # Annotations on curves
    frags.append(text(gx0 + 340, gy0 - 150, "Висока T (дослідження)", size=11, color=POS, bold=True))
    frags.append(text(gx0 + 230, gy0 - 65, "Середня T", size=11, color="#d97706", bold=True))
    frags.append(text(gx0 + 80, gy0 - 30, "Низька T (експлуатація)", size=11, color=NEG, bold=True))
    
    render(path, w, h, *frags)
    return path

def generate_cooling_schedules():
    path = os.path.join(IMG_DIR, 'cooling-schedules-comparison.svg')
    w, h = 760, 400
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Title & Subtitle
    frags.append(text(w / 2, 36, "Порівняння температурних розкладів охолодження (Cooling Schedules)", size=15, bold=True))
    frags.append(text(w / 2, 56, "Залежність температури T від номера ітерації / епохи k для різних стратегій", size=12, color=MUTED))
    
    # Axes
    ax_x0, ax_y0 = 70, 320
    ax_w, ax_h = 440, 230
    
    frags.append(arrow(ax_x0, ax_y0, ax_x0 + ax_w + 30, ax_y0, color=LINE, sw=1.5)) # X axis (Iterations)
    frags.append(arrow(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h - 15, color=LINE, sw=1.5)) # Y axis (Temperature)
    
    frags.append(text(ax_x0 + ax_w + 25, ax_y0 + 20, "Ітерації (k)", size=12, bold=True, anchor="end"))
    frags.append(text(ax_x0 - 15, ax_y0 - ax_h - 10, "Температура T", size=12, bold=True, anchor="start"))
    
    # T0 mark
    frags.append(line(ax_x0 - 5, ax_y0 - 200, ax_x0, ax_y0 - 200, color=LINE, sw=1.5))
    frags.append(text(ax_x0 - 10, ax_y0 - 195, "T₀", size=12, bold=True, anchor="end"))
    
    # 1. Logarithmic: T_k = T0 / ln(1 + k) (Blue)
    pts_log = []
    for k in range(0, 101):
        x = ax_x0 + (k / 100.0) * ax_w
        t = 200.0 / (1.0 + 0.3 * math.log(1.0 + k * 0.5))
        y = ax_y0 - t
        pts_log.append((x, y))
    d_log = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_log)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_log, NEG))
    
    # 2. Geometric / Exponential: T_k = T0 * alpha^k (Green)
    pts_geom = []
    for k in range(0, 101):
        x = ax_x0 + (k / 100.0) * ax_w
        t = 200.0 * (0.96 ** k)
        y = ax_y0 - t
        pts_geom.append((x, y))
    d_geom = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_geom)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_geom, FIELD))
    
    # 3. Linear: T_k = T0 - beta * k (Purple)
    pts_lin = []
    for k in range(0, 81):
        x = ax_x0 + (k / 100.0) * ax_w
        t = max(0.0, 200.0 * (1.0 - k / 80.0))
        y = ax_y0 - t
        pts_lin.append((x, y))
    d_lin = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_lin)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>' % (d_lin, "#7c3aed"))
    
    # 4. Adaptive with Reheating (Orange)
    pts_adap = []
    t_curr = 200.0
    for k in range(0, 101):
        x = ax_x0 + (k / 100.0) * ax_w
        if 35 <= k <= 45: # plateau at phase transition
            t_curr *= 0.995
        elif k == 70: # reheating jump
            t_curr = min(200.0, t_curr * 2.2)
        else:
            t_curr *= 0.95
        y = ax_y0 - t_curr
        pts_adap.append((x, y))
    d_adap = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_adap)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_adap, "#ea580c"))
    
    # Legend & Description Cards on Right Side
    rx = 625
    b_desc, _, _ = textbox(rx, 205,
                           "Стратегії охолодження:\n\n"
                           "● Логарифмічний (Джеман):\n  T = T₀ / ln(1 + k)\n  Теоретична збіжність,\n  надто повільний на практиці\n\n"
                           "● Геометричний (експоненційний):\n  T_{k+1} = α · T_k (α ≈ 0.85–0.99)\n  Золотий стандарт практики\n\n"
                           "● Лінійний розклад:\n  T_{k+1} = T_k − β\n\n"
                           "● Адаптивний з повторним нагрівом:\n  Уповільнення при флуктуаціях",
                           size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, pad=12)
    frags.append(b_desc)
    
    render(path, w, h, *frags)
    return path

def generate_tsp_two_opt():
    path = os.path.join(IMG_DIR, 'tsp-two-opt-move.svg')
    w, h = 760, 390
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Title & Subtitle
    frags.append(text(w / 2, 36, "Окільний оператор 2-opt для задачі комівояжера (TSP)", size=15, bold=True))
    frags.append(text(w / 2, 56, "Усунення перехрещення ребер розворотом підмаршруту та інкрементний розрахунок ΔE за O(1)", size=12, color=MUTED))
    
    # Left Panel: Before 2-opt (Crossed edges)
    p1_cx, p1_cy = 200, 200
    frags.append(rect(30, 80, 330, 280, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=6))
    frags.append(text(195, 105, "До 2-opt (стан s): Перехресні ребра", size=13, bold=True, color=POS))
    
    # Vertices A, B, C, D
    va = (90, 150)
    vb = (300, 270)
    vc = (90, 270)
    vd = (300, 150)
    
    # Edges before (A-B and C-D crossed!)
    frags.append(line(va[0], va[1], vb[0], vb[1], color=POS, sw=2.5))
    frags.append(line(vc[0], vc[1], vd[0], vd[1], color=POS, sw=2.5))
    
    # Remaining tour edges (subpaths)
    frags.append(line(va[0], va[1], vc[0], vc[1], color="#94a3b8", sw=1.8, dash="4,4")) # subpath 1
    frags.append(line(vb[0], vb[1], vd[0], vd[1], color="#94a3b8", sw=1.8, dash="4,4")) # subpath 2
    
    # Draw vertex circles & labels
    for (vx, vy), lbl in [(va, "A (u)"), (vb, "B (v)"), (vc, "C (w)"), (vd, "D (z)")]:
        frags.append(circle(vx, vy, 14, fill="#ffffff", stroke=LINE, sw=1.8))
        frags.append(text(vx, vy + 4, lbl.split()[0], size=12, bold=True))
    
    frags.append(text(195, 200, "Перехрещення!", size=11, color=POS, bold=True))
    frags.append(text(195, 335, "Видаляються ребра (A, B) та (C, D)", size=11, color=MUTED))
    
    # Arrow between panels
    frags.append(arrow(375, 220, 415, 220, color=LINE, sw=2.5))
    frags.append(text(395, 205, "2-opt", size=12, bold=True, color=FIELD))
    
    # Right Panel: After 2-opt (Reconnected & Untangled)
    p2_cx, p2_cy = 570, 200
    frags.append(rect(430, 80, 300, 280, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=6))
    frags.append(text(580, 105, "Після 2-opt (стан s'): Розплутаний тур", size=13, bold=True, color=FIELD))
    
    # Vertices coords in right panel
    r_va = (480, 150)
    r_vb = (680, 270)
    r_vc = (480, 270)
    r_vd = (680, 150)
    
    # Reconnected edges: (A, D) and (C, B)
    frags.append(line(r_va[0], r_va[1], r_vd[0], r_vd[1], color=FIELD, sw=2.8))
    frags.append(line(r_vc[0], r_vc[1], r_vb[0], r_vb[1], color=FIELD, sw=2.8))
    
    # Same remaining tour subpaths
    frags.append(line(r_va[0], r_va[1], r_vc[0], r_vc[1], color="#94a3b8", sw=1.8, dash="4,4"))
    frags.append(line(r_vb[0], r_vb[1], r_vd[0], r_vd[1], color="#94a3b8", sw=1.8, dash="4,4"))
    
    # Draw vertex circles & labels
    for (vx, vy), lbl in [(r_va, "A"), (r_vb, "B"), (r_vc, "C"), (r_vd, "D")]:
        frags.append(circle(vx, vy, 14, fill="#ffffff", stroke=FIELD, sw=2))
        frags.append(text(vx, vy + 4, lbl, size=12, bold=True, color=FIELD))
    
    # Delta E Box
    b_de, _, _ = textbox(580, 215, "Інкрементна зміна вартості:\nΔE = (d_AD + d_CB) − (d_AB + d_CD)\nСкладність розрахунку: O(1)", size=11, fill="#ffffff", stroke=FIELD, sw=1.2, pad=8)
    frags.append(b_de)
    
    frags.append(text(580, 335, "Додаються ребра (A, D) та (C, B)", size=11, color=FIELD, bold=True))
    
    render(path, w, h, *frags)
    return path

if __name__ == '__main__':
    generate_landscape_trapping()
    generate_metropolis_probability()
    generate_cooling_schedules()
    generate_tsp_two_opt()
    print("All figures generated successfully.")
