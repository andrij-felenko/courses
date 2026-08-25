# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори за змістом
COLOR_SIG1 = NEG       # Головний сигнал A1 (синій)
COLOR_SIG2 = POS       # Завада A2 (червоний)
COLOR_RES  = FIELD     # Сумарний вектор R(t) (зелений)
COLOR_TEXT = INK       # Основний текст
COLOR_MUTED = MUTED    # Осі, допоміжні лінії

def path(pts, color, sw=2.0, fill="none", dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{da}/>'

def arrow_path(x1, y1, x2, y2, color, sw=2.0, head_len=8.0):
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-4:
        return ""
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    hx1 = x2 - head_len * ux + head_len * 0.4 * px
    hy1 = y2 - head_len * uy + head_len * 0.4 * py
    hx2 = x2 - head_len * ux - head_len * 0.4 * px
    hy2 = y2 - head_len * uy - head_len * 0.4 * py
    
    line_svg = line(x1, y1, x2, y2, color=color, sw=sw)
    head_svg = f'<polygon points="{x2:.1f},{y2:.1f} {hx1:.1f},{hy1:.1f} {hx2:.1f},{hy2:.1f}" fill="{color}"/>'
    return line_svg + head_svg

# ── Фігура 1: Векторне додавання двох ЧМ-несучих ──────────────────────────────

def fig_phasor_addition():
    W, H = 760, 440
    p = []
    
    ox, oy = 160, 300
    
    len1 = 280
    ax1, ay1 = ox + len1, oy
    
    len2 = 140
    angle2_deg = 65
    angle2_rad = math.radians(angle2_deg)
    ax2 = ax1 + len2 * math.cos(angle2_rad)
    ay2 = ay1 - len2 * math.sin(angle2_rad)
    
    p.append(line(ox - 30, oy, ox + len1 + 180, oy, color=COLOR_MUTED, sw=1.2, dash="4 4"))
    
    # Вектор A1
    p.append(arrow_path(ox, oy, ax1, ay1, COLOR_SIG1, sw=3.2))
    p.append(text(ox + len1 / 2, oy + 25, "Сильний сигнал A₁ (несуча ω₁)", size=13, color=COLOR_SIG1, bold=True, anchor="middle"))
    
    # Пунктирне коло опису A2 навколо кінця A1 через path
    circle_pts = []
    for i in range(73):
        a = 2.0 * math.pi * i / 72.0
        circle_pts.append((ax1 + len2 * math.cos(a), ay1 - len2 * math.sin(a)))
    p.append(path(circle_pts, "#cbd5e1", sw=1.5, dash="4 4"))
    
    p.append(line(ax1, ay1, ax1 + len2 + 30, ay1, color=COLOR_MUTED, sw=1.0, dash="3 3"))
    
    # Вектор A2
    p.append(arrow_path(ax1, ay1, ax2, ay2, COLOR_SIG2, sw=2.8))
    p.append(text(ax1 + len2 * 0.5 * math.cos(angle2_rad) + 20, ay1 - len2 * 0.5 * math.sin(angle2_rad) - 10,
                  "Слабкий сигнал A₂", size=12.5, color=COLOR_SIG2, bold=True, anchor="start"))
    
    # Сумарний вектор R(t)
    p.append(arrow_path(ox, oy, ax2, ay2, COLOR_RES, sw=3.5))
    p.append(text((ox + ax2) / 2 - 25, (oy + ay2) / 2 - 12, "Сумарний вектор R(t)", size=13.5, color=COLOR_RES, bold=True, anchor="end"))
    
    # Кут фазової завади psi(t)
    r_arc = 100
    psi_rad = math.atan2(oy - ay2, ax2 - ox)
    arc_pts = []
    for i in range(30):
        a = psi_rad * i / 29.0
        arc_pts.append((ox + r_arc * math.cos(a), oy - r_arc * math.sin(a)))
    p.append(path(arc_pts, COLOR_RES, sw=2.0))
    p.append(text(ox + r_arc + 14, oy - r_arc * 0.4, "ψ(t)", size=15, color=COLOR_RES, bold=True, anchor="start"))
    
    # Дуга кута theta(t) між A1 та A2
    r_arc2 = 50
    arc2_pts = []
    for i in range(30):
        a = angle2_rad * i / 29.0
        arc2_pts.append((ax1 + r_arc2 * math.cos(a), ay1 - r_arc2 * math.sin(a)))
    p.append(path(arc2_pts, COLOR_SIG2, sw=1.8))
    p.append(text(ax1 + r_arc2 + 10, ay1 - r_arc2 * 0.4, "θ(t) = Δω·t", size=12, color=COLOR_SIG2, bold=True, anchor="start"))
    
    expl = (
        "Оскільки A₁ > A₂, вектор A₂ лише «коливає» фазу сумарного вектора R(t) на кут ψ(t) < 90°.\n"
        "Обмежувач приймача відсікає пульсації амплітуди R(t), а середня частота за період дорівнює точно ω₁!"
    )
    box_svg, _, _ = textbox(W / 2, 385, expl, size=12, color=COLOR_TEXT, fill="#f8fafc", stroke=COLOR_SIG1, min_w=W - 80)
    p.append(box_svg)
    
    render(os.path.join(OUT, "phasor-addition.svg"), W, H, *p, title="Векторне додавання двох ЧМ-несучих")

# ── Фігура 2: Порогова характеристика придушення завади (AM vs FM) ────────────

def fig_capture_threshold():
    W, H = 760, 420
    p = []
    
    x0, x1 = 90, 700
    y0, y1 = 70, 320
    
    p.append(line(x0, y1, x1 + 15, y1, color=COLOR_TEXT, sw=1.8))
    p.append(line(x0, y1, x0, y0 - 15, color=COLOR_TEXT, sw=1.8))
    
    p.append(text(x1 + 10, y1 + 30, "Співвідношення несучих A₁/A₂ (дБ)", size=12.5, color=COLOR_TEXT, bold=True, anchor="end"))
    p.append(text(x0 - 50, y0 - 10, "Рівень звукового сигналу / придушення (дБ)", size=12, color=COLOR_TEXT, bold=True, anchor="start"))
    
    db_vals = [-10, -5, 0, 3, 5, 10, 15, 20]
    for db in db_vals:
        cx = x0 + (db + 10) / 30.0 * (x1 - x0)
        p.append(line(cx, y1, cx, y1 + 6, color=COLOR_TEXT, sw=1.2))
        p.append(line(cx, y0, cx, y1, color="#f1f5f9", sw=1.0))
        p.append(text(cx, y1 + 22, f"{db}", size=11, color=COLOR_MUTED, anchor="middle"))
    
    for y_db in [0, 10, 20, 30, 40]:
        cy = y1 - (y_db / 40.0) * (y1 - y0)
        p.append(line(x0 - 6, cy, x0, cy, color=COLOR_TEXT, sw=1.2))
        p.append(line(x0, cy, x1, cy, color="#f1f5f9", sw=1.0))
        p.append(text(x0 - 12, cy + 4, f"{y_db}", size=11, color=COLOR_MUTED, anchor="end"))
    
    pts_fm_a1 = []
    pts_fm_a2 = []
    pts_am_a1 = []
    
    N = 200
    for i in range(N):
        db = -10 + 30.0 * i / (N - 1)
        cx = x0 + (db + 10) / 30.0 * (x1 - x0)
        
        val_fm = 1.0 / (1.0 + math.exp(-2.2 * (db - 1.5)))
        y_fm_a1 = y1 - (val_fm * 38.0) / 40.0 * (y1 - y0)
        y_fm_a2 = y1 - ((1.0 - val_fm) * 38.0) / 40.0 * (y1 - y0)
        
        pts_fm_a1.append((cx, y_fm_a1))
        pts_fm_a2.append((cx, y_fm_a2))
        
        val_am = max(0.0, min(1.0, (db + 10) / 30.0))
        y_am_a1 = y1 - (val_am * 38.0) / 40.0 * (y1 - y0)
        pts_am_a1.append((cx, y_am_a1))
    
    p.append(path(pts_am_a1, POS, sw=2.2, dash="5 4"))
    p.append(path(pts_fm_a2, COLOR_SIG2, sw=2.0))
    p.append(path(pts_fm_a1, COLOR_SIG1, sw=3.2))
    
    cx_0 = x0 + (0 + 10) / 30.0 * (x1 - x0)
    cx_3 = x0 + (3 + 10) / 30.0 * (x1 - x0)
    p.append(rect(cx_0, y0, cx_3 - cx_0, y1 - y0, fill="#fef08a", stroke="none", rx=0))
    p.append(line(cx_0, y0, cx_0, y1, color="#ca8a04", sw=1.2, dash="3 3"))
    p.append(line(cx_3, y0, cx_3, y1, color="#ca8a04", sw=1.2, dash="3 3"))
    p.append(text((cx_0 + cx_3) / 2, y0 + 20, "Вікно захоплення", size=11, color="#854d0e", bold=True, anchor="middle"))
    p.append(text((cx_0 + cx_3) / 2, y0 + 36, "(1–3 дБ)", size=10.5, color="#854d0e", anchor="middle"))
    
    p.append(line(x0 + 40, y0 + 30, x0 + 70, y0 + 30, color=COLOR_SIG1, sw=3.2))
    p.append(text(x0 + 78, y0 + 34, "FM: Корисний сигнал A₁", size=11.5, color=COLOR_SIG1, bold=True, anchor="start"))
    
    p.append(line(x0 + 40, y0 + 50, x0 + 70, y0 + 50, color=COLOR_SIG2, sw=2.0))
    p.append(text(x0 + 78, y0 + 54, "FM: Заглушена завада A₂", size=11.5, color=COLOR_SIG2, bold=True, anchor="start"))
    
    p.append(line(x0 + 40, y0 + 70, x0 + 70, y0 + 70, color=POS, sw=2.2, dash="5 4"))
    p.append(text(x0 + 78, y0 + 74, "AM: Повільне лінійне придушення (потрібно >20 дБ)", size=11.5, color=POS, bold=True, anchor="start"))
    
    render(os.path.join(OUT, "capture-threshold.svg"), W, H, *p, title="Порогова характеристика ефекту захоплення ЧМ")

# ── Фігура 3: Сплески миттєвої частоти dpsi/dt ───────────────────────────────

def fig_phase_spikes():
    W, H = 760, 440
    p = []
    
    x0, x1 = 80, 710
    cy = 220
    
    p.append(line(x0, cy, x1 + 10, cy, color=COLOR_TEXT, sw=1.5))
    p.append(line(x0 + (x1 - x0) / 2, 40, x0 + (x1 - x0) / 2, 380, color=COLOR_MUTED, sw=1.0, dash="3 3"))
    
    p.append(text(x1, cy + 22, "Кут фазової розбудови θ = Δω·t", size=12, color=COLOR_TEXT, bold=True, anchor="end"))
    p.append(text(x0 - 50, 45, "Відхилення миттєвої частоти dψ/dθ", size=12, color=COLOR_TEXT, bold=True, anchor="start"))
    
    x_mid = x0 + (x1 - x0) / 2
    x_pi = x1 - 30
    x_npi = x0 + 30
    
    p.append(text(x_npi, cy + 20, "−π", size=13, color=COLOR_TEXT, anchor="middle"))
    p.append(text(x0 + (x_mid - x0) / 2, cy + 20, "−π/2", size=12, color=COLOR_MUTED, anchor="middle"))
    p.append(text(x_mid, cy + 20, "0", size=13, color=COLOR_TEXT, anchor="middle"))
    p.append(text(x_mid + (x1 - x_mid) / 2, cy + 20, "π/2", size=12, color=COLOR_MUTED, anchor="middle"))
    p.append(text(x_pi, cy + 20, "+π", size=13, color=COLOR_TEXT, anchor="middle"))
    
    ratios = [
        (0.5, "#d97706", "a = 0.5 (−6 дБ) — гладка пульсація"),
        (0.8, FIELD,   "a = 0.8 (−2 дБ) — виражені піки"),
        (0.95, COLOR_SIG1, "a = 0.95 (−0.4 дБ) — гострі сплески на ±π")
    ]
    
    N = 400
    scale_y = 45.0
    
    for a_val, col_val, label_text in ratios:
        pts = []
        for i in range(N):
            th = -math.pi + 2.0 * math.pi * i / (N - 1)
            cx = x_npi + (th + math.pi) / (2.0 * math.pi) * (x_pi - x_npi)
            
            denom = 1.0 + a_val**2 + 2.0 * a_val * math.cos(th)
            dpsi = (a_val**2 + a_val * math.cos(th)) / denom
            
            dpsi_clamped = max(-3.5, min(1.5, dpsi))
            cy_pt = cy - dpsi_clamped * scale_y
            pts.append((cx, cy_pt))
        
        p.append(path(pts, col_val, sw=2.2 if a_val < 0.9 else 2.8))
    
    expl = (
        "При протилежності фаз (θ = ±π) вектори A₁ та A₂ віднімаються. При a → 1 фаза змінюється майже миттєво,\n"
        "породжуючи вузькі гострі імпульси від'ємної частоти. Оскільки площа імпульсу за період дорівнює 0,\n"
        "низькочастотний аудіофільтр приймача повністю подавляє їх за умови a < 1!"
    )
    box_svg, _, _ = textbox(W / 2, 385, expl, size=11.5, color=COLOR_TEXT, fill="#f8fafc", stroke=COLOR_SIG1, min_w=W - 80)
    p.append(box_svg)
    
    ly = 65
    for a_val, col_val, label_text in ratios:
        p.append(line(x0 + 20, ly, x0 + 50, ly, color=col_val, sw=2.5))
        p.append(text(x0 + 58, ly + 4, label_text, size=11.5, color=col_val, bold=True, anchor="start"))
        ly += 22
        
    render(os.path.join(OUT, "phase-spikes.svg"), W, H, *p, title="Форма сплесків миттєвої частоти за різних співвідношень амплітуд")

if __name__ == "__main__":
    fig_phasor_addition()
    fig_capture_threshold()
    fig_phase_spikes()
    print("Figures generated successfully.")
