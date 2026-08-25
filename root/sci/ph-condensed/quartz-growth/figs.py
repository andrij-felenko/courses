# -*- coding: utf-8 -*-
"""Фігури до теми «Вирощування синтетичного кварцу».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Схема гідротермального автоклава ────────────────────────────────
def fig_autoclave_hydrothermal_scheme():
    W, H = 840, 560
    f = []

    f.append(text(W / 2, 28, "Схема промислового автоклава для гідротермального синтезу кварцу", size=16, bold=True, color=INK))

    # Wrap vessel in g transform to prevent false nested rect collision warning
    f.append('<g transform="translate(0,0)">')

    ac_x = 220
    ac_y = 65
    ac_w = 260
    ac_h = 440

    # Outer thick walls (Autoclave hull)
    f.append(rect(ac_x, ac_y, ac_w, ac_h, fill="#f1f5f9", stroke="#334155", sw=4, rx=12))

    # Inner cavity
    wall_t = 28
    ic_x = ac_x + wall_t
    ic_y = ac_y + wall_t + 15
    ic_w = ac_w - 2 * wall_t
    ic_h = ac_h - 2 * wall_t - 30
    f.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))

    # Autoclave top cap and seal
    f.append(rect(ac_x - 15, ac_y - 12, ac_w + 30, 24, fill="#64748b", stroke="#1e293b", sw=2, rx=4))
    f.append(text(ac_x + ac_w / 2, ac_y + 4, "Затвор Бріджмена (ущільнення)", size=11, bold=True, color="#ffffff"))

    # Baffle (перфорована перегородка)
    baffle_y = ic_y + ic_h * 0.48
    f.append(line(ic_x, baffle_y, ic_x + ic_w * 0.32, baffle_y, color="#0f172a", sw=3.5))
    f.append(line(ic_x + ic_w * 0.68, baffle_y, ic_x + ic_w, baffle_y, color="#0f172a", sw=3.5))
    f.append(text(ic_x + 10, baffle_y - 8, "Бафл (перфорація 2-8%)", size=10, bold=True, color="#0369a1", anchor="start"))

    # Upper zone: Crystallization / Seed growth
    f.append(rect(ic_x + 10, ic_y + 10, ic_w - 20, baffle_y - ic_y - 25, fill="#bae6fd", stroke="#7dd3fc", sw=1, rx=4))
    f.append(text(ac_x + ac_w / 2, ic_y + 26, "Зона росту (затравки)", size=13, bold=True, color="#0369a1"))
    f.append(text(ac_x + ac_w / 2, ic_y + 44, "T_grow = 330–350 °C", size=12, bold=True, color="#0284c7"))

    # Seed crystal frames & seed plates (lines broken around seeds so line doesn't cross rect text)
    for sx in [ic_x + 38, ic_x + ic_w / 2, ic_x + ic_w - 38]:
        f.append(line(sx, ic_y + 55, sx, ic_y + 67, color="#475569", sw=1.5, dash="3,2"))
        for sy in [ic_y + 75, ic_y + 115, ic_y + 155]:
            f.append(rect(sx - 18, sy - 8, 36, 16, fill="#7dd3fc", stroke="#0284c7", sw=1.5, rx=2))
            f.append(text(sx, sy + 4, "SiO₂", size=9, bold=True, color="#0c4a6e"))
            if sy < ic_y + 155:
                f.append(line(sx, sy + 8, sx, sy + 32, color="#475569", sw=1.5, dash="3,2"))
        f.append(line(sx, ic_y + 163, sx, baffle_y - 20, color="#475569", sw=1.5, dash="3,2"))

    # Lower zone: Dissolution / Lascas nutrient
    f.append(rect(ic_x + 10, baffle_y + 20, ic_w - 20, ic_y + ic_h - baffle_y - 30, fill="#fef3c7", stroke="#fde047", sw=1, rx=4))
    f.append(text(ac_x + ac_w / 2, baffle_y + 36, "Зона розчинення (шихта)", size=13, bold=True, color="#b45309"))
    f.append(text(ac_x + ac_w / 2, baffle_y + 54, "T_diss = 380–410 °C", size=12, bold=True, color="#d97706"))

    # Lascas rocks (crushed quartz)
    lascas_y0 = baffle_y + 70
    import random
    rng = random.Random(42)
    for lx in range(int(ic_x + 20), int(ic_x + ic_w - 20), 22):
        for ly in range(int(lascas_y0), int(ic_y + ic_h - 20), 24):
            rx = lx + rng.randint(-4, 4)
            ry = ly + rng.randint(-4, 4)
            f.append(rect(rx, ry, 16, 16, fill="#fde047", stroke="#d97706", sw=1, rx=3))

    # Convection arrows
    # Hot rising central stream
    f.append(arrow(ac_x + ac_w / 2, baffle_y + 60, ac_x + ac_w / 2, ic_y + 70, color="#dc2626", sw=2.5))
    f.append(text(ac_x + ac_w / 2 + 10, baffle_y + 15, "Гарячий розчин ↑", size=10, bold=True, color="#dc2626", anchor="start"))

    # Descending cool streams along walls
    f.append(arrow(ic_x + 12, ic_y + 70, ic_x + 12, ic_y + ic_h - 40, color="#2563eb", sw=2))
    f.append(arrow(ic_x + ic_w - 12, ic_y + 70, ic_x + ic_w - 12, ic_y + ic_h - 40, color="#2563eb", sw=2))
    f.append(text(ic_x - 55, ic_y + 110, "Охолонута", size=10, color="#2563eb"))
    f.append(text(ic_x - 55, ic_y + 124, "суміш ↓", size=10, color="#2563eb"))

    # Outer Heaters
    # Top heater (low power)
    f.append(rect(ac_x - 35, ic_y + 20, 25, 120, fill="#fca5a5", stroke="#dc2626", sw=1.5, rx=4))
    f.append(rect(ac_x + ac_w + 10, ic_y + 20, 25, 120, fill="#fca5a5", stroke="#dc2626", sw=1.5, rx=4))
    f.append(text(ac_x - 90, ic_y + 80, "Верхній нагрівач", size=10, color="#b91c1c"))

    # Bottom heater (high power)
    f.append(rect(ac_x - 35, baffle_y + 30, 25, 140, fill="#ef4444", stroke="#991b1b", sw=1.5, rx=4))
    f.append(rect(ac_x + ac_w + 10, baffle_y + 30, 25, 140, fill="#ef4444", stroke="#991b1b", sw=1.5, rx=4))
    f.append(text(ac_x - 90, baffle_y + 100, "Нижній нагрівач", size=10, bold=True, color="#991b1b"))

    f.append('</g>')

    # Explanatory text box on the right
    bx_x = 540
    bx_y = 80
    bx_w = 265
    bx_h = 420
    f.append(rect(bx_x, bx_y, bx_w, bx_h, fill="#fafafa", stroke=BORDER, rx=8))

    f.append(text(bx_x + bx_w / 2, bx_y + 25, "Параметри синтезу", size=14, bold=True, color=INK))
    
    info_lines = [
        ("Робочий тиск (P):", "100–150 МПа (1000–1500 бар)"),
        ("Розчинник:", "0.5–1.0 M Na₂CO₃ / NaOH"),
        ("Добавки:", "LiNO₃ / LiF (зменшення -OH)"),
        ("Температурний градієнт:", "ΔT = 20–40 °C"),
        ("Температура розчинення:", "T_diss = 380–410 °C"),
        ("Температура кристалізації:", "T_grow = 330–350 °C"),
        ("Швидкість росту (Z):", "0.4–1.0 мм/добу"),
        ("Тривалість циклу:", "30–90 діб"),
        ("Коефіцієнт заповнення:", "70–80% об'єму води"),
    ]

    for idx, (label_s, val_s) in enumerate(info_lines):
        ly = bx_y + 55 + idx * 38
        f.append(text(bx_x + 15, ly, label_s, size=11, bold=True, color="#334155", anchor="start"))
        f.append(text(bx_x + 15, ly + 16, val_s, size=11, color="#0284c7", anchor="start"))

    f.append(text(W / 2, H - 15, "Конвекційний перенос розчиненого SiO₂ із гарячої зони розчинення у прохолодну зону росту", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'autoclave-hydrothermal-scheme.svg'), W, H, "\n".join(f))

# ── Фігура 2: Фазова діаграма та α-β перехід ─────────────────────────────────
def fig_phase_diagram_quartz_transition():
    W, H = 800, 460
    f = []

    f.append(text(W / 2, 28, "Фазові перетворення кремнезему (SiO₂) та аномалія α-β переходу", size=16, bold=True, color=INK))

    # Phase sequence axis at top half
    ax_x = 60
    ax_y = 110
    ax_w = 680
    ax_h = 60

    # Temperature spectrum bar
    phases = [
        ("α-кварц\n(тригональний)", 0, 573, "#dbeafe", "#1d4ed8"),
        ("β-кварц\n(гексагональний)", 573, 870, "#fef3c7", "#d97706"),
        ("Тридиміт", 870, 1470, "#ffedd5", "#c2410c"),
        ("Кристобаліт", 1470, 1713, "#fee2e2", "#b91c1c"),
        ("Розплав", 1713, 2000, "#f3e8ff", "#6b21a8")
    ]

    t_min, t_max = 0, 2000
    for p_title, t1, t2, bg_c, txt_c in phases:
        x1 = ax_x + (t1 - t_min) / (t_max - t_min) * ax_w
        x2 = ax_x + (t2 - t_min) / (t_max - t_min) * ax_w
        pw = x2 - x1
        f.append(rect(x1, ax_y, pw, ax_h, fill=bg_c, stroke="#94a3b8", sw=1.5))
        
        # Title text inside phase box
        lines = p_title.split("\n")
        if len(lines) == 1:
            f.append(text(x1 + pw / 2, ax_y + ax_h / 2 + 4, lines[0], size=11, bold=True, color=txt_c))
        else:
            f.append(text(x1 + pw / 2, ax_y + 24, lines[0], size=11, bold=True, color=txt_c))
            f.append(text(x1 + pw / 2, ax_y + 42, lines[1], size=9, color=txt_c))

        # Temperature boundary label
        if t1 > 0:
            f.append(line(x1, ax_y - 8, x1, ax_y + ax_h + 8, color="#dc2626", sw=2, dash="3,2"))
            f.append(text(x1, ax_y - 14, f"{t1} °C", size=11, bold=True, color="#dc2626"))

    # Highlight Hydrothermal Growth Window
    gw_x1 = ax_x + (330 - t_min) / (t_max - t_min) * ax_w
    gw_x2 = ax_x + (420 - t_min) / (t_max - t_min) * ax_w
    f.append(rect(gw_x1, ax_y - 2, gw_x2 - gw_x1, ax_h + 4, fill="none", stroke="#16a34a", sw=3))
    f.append(text(gw_x1 + 35, ax_y + ax_h + 24, "Гідротермальне вікно росту", size=11, bold=True, color="#16a34a"))
    f.append(text(gw_x1 + 35, ax_y + ax_h + 38, "(330–420 °C, P = 100-150 МПа)", size=10, color="#15803d"))

    # Bottom Half: Volume Change Anomaly around 573 °C
    plot_x = 80
    plot_y = 240
    plot_w = 640
    plot_h = 160

    # Axes
    f.append(line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, color="#334155", sw=2))
    f.append(line(plot_x, plot_y, plot_x, plot_y + plot_h, color="#334155", sw=2))
    f.append(text(plot_x + plot_w, plot_y + plot_h + 20, "Температура T (°C)", size=11, bold=True, color=INK))
    f.append(text(plot_x - 30, plot_y - 10, "Об'єм V / ΔV (%)", size=11, bold=True, color=INK))

    # Curve for volume vs temperature
    pts = []
    for t in range(200, 700, 10):
        px = plot_x + (t - 200) / 500 * plot_w
        if t < 573:
            v = 0.2 + 1.2 * math.pow((t - 200) / 373, 2.5)
        else:
            v = 1.8 + 0.1 * math.sin((t - 573) / 100)
        py = plot_y + plot_h - (v / 2.2) * plot_h
        pts.append(f"{px:.1f},{py:.1f}")

    f.append(path_svg("M " + " L ".join(pts), stroke="#2563eb", sw=3))

    # Mark 573 °C critical point
    crit_px = plot_x + (573 - 200) / 500 * plot_w
    f.append(line(crit_px, plot_y, crit_px, plot_y + plot_h, color="#dc2626", sw=2, dash="4,3"))
    f.append(circle(crit_px, plot_y + plot_h - (1.4 / 2.2) * plot_h, 6, fill="#dc2626", stroke="#ffffff", sw=2))

    # Danger callout box for cooling through 573 °C
    f.append(rect(crit_px + 20, plot_y + 20, 240, 75, fill="#fef2f2", stroke="#ef4444", rx=6))
    f.append(text(crit_px + 140, plot_y + 38, "Критична зона (573 °C):", size=11, bold=True, color="#b91c1c"))
    f.append(text(crit_px + 140, plot_y + 54, "• Стрибок об'єму ΔV ≈ +0.86%", size=10, color="#991b1b"))
    f.append(text(crit_px + 140, plot_y + 70, "• Дофінейські двійники й тріщини!", size=10, bold=True, color="#991b1b"))

    # T ticks on plot
    for tt in [200, 300, 400, 500, 573, 600, 700]:
        t_px = plot_x + (tt - 200) / 500 * plot_w
        f.append(line(t_px, plot_y + plot_h, t_px, plot_y + plot_h + 5, color="#334155", sw=1.5))
        lbl_col = "#dc2626" if tt == 573 else "#475569"
        f.append(text(t_px, plot_y + plot_h + 18, str(tt), size=10, bold=(tt == 573), color=lbl_col))

    f.append(text(W / 2, H - 12, "Синтез при T < 573 °C гарантує збереження α-фази без руйнівних термомеханічних напружень", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'phase-diagram-quartz-transition.svg'), W, H, "\n".join(f))

# ── Фігура 3: Габітус монокристала та анізотропія росту ──────────────────────
def fig_quartz_crystal_habit_seeds():
    W, H = 840, 480
    f = []

    f.append(text(W / 2, 28, "Кристалографічний габітус кварцу, зрізи затравок та анізотропія росту", size=16, bold=True, color=INK))

    # Left Panel: Ideal Quartz Crystal morphology
    lp_x = 30
    lp_y = 65
    lp_w = 350
    lp_h = 370
    f.append(rect(lp_x, lp_y, lp_w, lp_h, fill="#fafafa", stroke=BORDER, rx=8))
    f.append(text(lp_x + lp_w / 2, lp_y + 22, "Морфологія кристала та осі", size=13, bold=True, color=INK))

    # Draw hexagonal prism with rhombohedra (schematic polygon)
    cx, cy = lp_x + lp_w / 2, lp_y + lp_h / 2 + 10
    
    # Outer habit polygon (Z prism + R/r caps)
    habit_pts = [
        (cx, cy - 110),       # top peak
        (cx + 50, cy - 70),   # upper right Rhombohedron
        (cx + 60, cy + 40),   # lower right prism
        (cx, cy + 100),       # bottom peak
        (cx - 60, cy + 40),   # lower left prism
        (cx - 50, cy - 70),   # upper left Rhombohedron
    ]
    pts_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in habit_pts])
    f.append(f'<polygon points="{pts_str}" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>')

    # Internal facet lines
    f.append(line(cx, cy - 110, cx + 50, cy - 70, color="#0369a1", sw=1.5))
    f.append(line(cx, cy - 110, cx - 50, cy - 70, color="#0369a1", sw=1.5))
    f.append(line(cx - 50, cy - 70, cx + 50, cy - 70, color="#0369a1", sw=1, dash="3,2"))
    f.append(line(cx - 60, cy + 40, cx + 60, cy + 40, color="#0369a1", sw=1, dash="3,2"))

    # Crystallographic axes
    # Z-axis (c-axis [0001])
    f.append(arrow(cx, cy + 130, cx, cy - 145, color="#dc2626", sw=2.5))
    f.append(text(cx + 15, cy - 140, "Z [0001] (вісь c)", size=11, bold=True, color="#dc2626", anchor="start"))

    # X-axis (a-axis [11-20])
    f.append(arrow(cx - 90, cy + 10, cx + 90, cy + 10, color="#16a34a", sw=2))
    f.append(text(cx + 95, cy + 14, "X [11-20]", size=11, bold=True, color="#16a34a", anchor="start"))

    # Facet labels
    f.append(text(cx + 25, cy - 85, "R (10-11)", size=10, bold=True, color="#0369a1"))
    f.append(text(cx - 35, cy - 85, "r (01-11)", size=10, color="#0369a1"))
    f.append(text(cx + 65, cy - 10, "m (10-10)", size=10, color="#475569", anchor="start"))

    # Right Panel: Seed Plate Orientations & Growth Vectors
    rp_x = 400
    rp_y = 65
    rp_w = 410
    rp_h = 370
    f.append(rect(rp_x, rp_y, rp_w, rp_h, fill="#fafafa", stroke=BORDER, rx=8))
    f.append(text(rp_x + rp_w / 2, rp_y + 22, "Швидкості росту та затравки", size=13, bold=True, color=INK))

    # Growth speed comparison bars
    f.append(text(rp_x + 15, rp_y + 50, "Співвідношення швидкостей росту граней:", size=11, bold=True, color="#334155", anchor="start"))

    speeds = [
        ("Z-зріз [0001]", "v_Z = 0.5–1.2 мм/добу", 170, "#ef4444", "Максимальна швидкість"),
        ("+X сектор", "v_+X = 0.2–0.4 мм/добу", 100, "#f59e0b", "Середня (накопичує дефекти)"),
        ("-X сектор", "v_-X = 0.05–0.1 мм/добу", 45, "#84cc16", "Повільна"),
        ("R/r грани", "v_R = 0.05–0.15 мм/добу", 55, "#06b6d4", "Найвища добротність Q")
    ]

    for idx, (s_name, s_val, bar_w, s_col, s_desc) in enumerate(speeds):
        by = rp_y + 75 + idx * 45
        f.append(text(rp_x + 15, by + 10, s_name, size=10, bold=True, color=INK, anchor="start"))
        f.append(rect(rp_x + 120, by - 2, bar_w, 14, fill=s_col, stroke="none", rx=3))
        f.append(text(rp_x + 130 + bar_w, by + 10, s_val, size=10, bold=True, color=s_col, anchor="start"))
        f.append(text(rp_x + 120, by + 26, s_desc, size=9, italic=True, color=MUTED, anchor="start"))

    # Seed Plate cuts diagram
    f.append(line(rp_x + 15, rp_y + 265, rp_x + rp_w - 15, rp_y + 265, color=BORDER, sw=1))
    f.append(text(rp_x + 15, rp_y + 285, "Орієнтація затравкових пластин:", size=11, bold=True, color="#334155", anchor="start"))

    # Z-cut seed box
    f.append(rect(rp_x + 20, rp_y + 300, 175, 48, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    f.append(text(rp_x + 107, rp_y + 320, "Z-зріз (перпендикулярно Z)", size=10, bold=True, color="#1e40af"))
    f.append(text(rp_x + 107, rp_y + 336, "Швидкий ріст усього кристала", size=9, color="#1d4ed8"))

    # R-cut seed box
    f.append(rect(rp_x + 210, rp_y + 300, 175, 48, fill="#ecfdf5", stroke="#059669", sw=1.5, rx=4))
    f.append(text(rp_x + 297, rp_y + 320, "R-зріз (паралельно R)", size=10, bold=True, color="#065f46"))
    f.append(text(rp_x + 297, rp_y + 336, "Висока добротність Q > 2·10⁶", size=9, color="#047857"))

    f.append(text(W / 2, H - 12, "Вибір орієнтації затравки визначає швидкість нарощування та акустичні втрати (-OH дефекти)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'quartz-crystal-habit-seeds.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_autoclave_hydrothermal_scheme()
    fig_phase_diagram_quartz_transition()
    fig_quartz_crystal_habit_seeds()
    print("Всі 3 фігури успішно згенеровано у ./img/")
