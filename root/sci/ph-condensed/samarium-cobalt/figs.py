# -*- coding: utf-8 -*-
"""Фігури до теми «Самарій-кобальтові магніти (SmCo5, Sm2Co17)».
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

# ── Фігура 1: Кристалічні структури SmCo5 та Sm2Co17 ─────────────────────────
def fig_smco_crystal_structures():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 26, "Кристалографічна структура магнітів SmCo₅ (1:5) та Sm₂Co₁₇ (2:17)", size=16, bold=True, color=INK))

    # Panel 1: SmCo5
    p1_x, p1_y, p1_w, p1_h = 20, 50, 360, 320
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(p1_x + p1_w / 2, p1_y + 24, "SmCo₅ (Тип CaCu₅, гексагональна)", size=13, bold=True, color="#1e3a8a"))
    f.append(text(p1_x + p1_w / 2, p1_y + 42, "Просторова група P6/mmm, c-вісь — легке намагнічування", size=11, color=MUTED))

    # Diagram of SmCo5 hexagon
    hex_cx, hex_cy, R = p1_x + 130, p1_y + 160, 70
    pts = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        hx = hex_cx + R * math.cos(angle)
        hy = hex_cy + R * math.sin(angle)
        pts.append((hx, hy))
    
    # Hexagon outline
    d_hex = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + " Z"
    f.append(path_svg(d_hex, stroke="#94a3b8", sw=1.5))

    # Center Sm atom
    f.append(circle(hex_cx, hex_cy, 14, fill="#dc2626", stroke="#991b1b", sw=2))
    f.append(text(hex_cx, hex_cy + 4, "Sm", size=10, bold=True, color="#ffffff"))

    # Co atoms at vertices and midpoints
    for px, py in pts:
        f.append(circle(px, py, 9, fill="#2563eb", stroke="#1e40af", sw=1.5))
        f.append(text(px, py + 3, "Co", size=9, bold=True, color="#ffffff"))

    # Easy axis vector (c-axis)
    f.append(arrow(hex_cx + 110, hex_cy + 70, hex_cx + 110, hex_cy - 70, color="#d97706", sw=3))
    f.append(text(hex_cx + 110, hex_cy - 80, "Вісь c [0001]", size=11, bold=True, color="#b45309"))
    f.append(text(hex_cx + 110, hex_cy + 88, "(Легка вісь)", size=10, italic=True, color="#b45309"))

    # Key parameters panel 1
    f.append(rect(p1_x + 15, p1_y + 245, p1_w - 30, 60, fill="#eff6ff", stroke="#bfdbfe", rx=4))
    f.append(text(p1_x + p1_w / 2, p1_y + 262, "K₁ = 1.7·10⁷ Дж/м³ | H_A = 250-300 кЕ", size=11, bold=True, color="#1e40af"))
    f.append(text(p1_x + p1_w / 2, p1_y + 280, "T_C = 727 °C | B_r ≈ 0.95-1.05 Тл", size=11, color="#1e3a8a"))

    # Panel 2: Sm2Co17
    p2_x, p2_y, p2_w, p2_h = 400, 50, 360, 320
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(p2_x + p2_w / 2, p2_y + 24, "Sm₂Co₁₇ (Тип Th₂Zn₁₇ / Th₂Ni₁₇)", size=13, bold=True, color="#065f46"))
    f.append(text(p2_x + p2_w / 2, p2_y + 42, "Ромбоедрична/гексагональна з гантелями Co-Co", size=11, color=MUTED))

    # Diagram of Sm2Co17 structure (cell replacement)
    r_cx, r_cy = p2_x + 130, p2_y + 160
    f.append(circle(r_cx - 45, r_cy - 40, 14, fill="#dc2626", stroke="#991b1b", sw=2))
    f.append(text(r_cx - 45, r_cy - 36, "Sm", size=10, bold=True, color="#ffffff"))

    f.append(circle(r_cx + 45, r_cy + 40, 14, fill="#dc2626", stroke="#991b1b", sw=2))
    f.append(text(r_cx + 45, r_cy + 44, "Sm", size=10, bold=True, color="#ffffff"))

    # Co-Co dumbbell replacement
    f.append(line(r_cx - 15, r_cy + 15, r_cx + 15, r_cy - 15, color="#059669", sw=3))
    f.append(circle(r_cx - 15, r_cy + 15, 9, fill="#2563eb", stroke="#1e40af", sw=1.5))
    f.append(circle(r_cx + 15, r_cy - 15, 9, fill="#2563eb", stroke="#1e40af", sw=1.5))
    f.append(text(r_cx, r_cy + 30, "Гантель Co-Co", size=10, bold=True, color="#047857"))

    # Surround Co atoms
    f.append(circle(r_cx - 60, r_cy + 35, 9, fill="#2563eb", stroke="#1e40af", sw=1.5))
    f.append(circle(r_cx + 60, r_cy - 35, 9, fill="#2563eb", stroke="#1e40af", sw=1.5))

    # Easy axis vector (c-axis)
    f.append(arrow(p2_x + 280, r_cy + 70, p2_x + 280, r_cy - 70, color="#d97706", sw=3))
    f.append(text(p2_x + 280, r_cy - 80, "Вісь c [0001]", size=11, bold=True, color="#b45309"))
    f.append(text(p2_x + 280, r_cy + 88, "(Легка вісь)", size=10, italic=True, color="#b45309"))

    # Key parameters panel 2
    f.append(rect(p2_x + 15, p2_y + 245, p2_w - 30, 60, fill="#ecfdf5", stroke="#a7f3d0", rx=4))
    f.append(text(p2_x + p2_w / 2, p2_y + 262, "K₁ = 3.3·10⁶ Дж/м³ | H_A = 130-150 кЕ", size=11, bold=True, color="#047857"))
    f.append(text(p2_x + p2_w / 2, p2_y + 280, "T_C = 820 °C | B_r ≈ 1.05-1.15 Тл", size=11, color="#065f46"))

    # Bottom legend
    f.append(circle(180, H - 20, 7, fill="#dc2626", stroke="#991b1b", sw=1.5))
    f.append(text(240, H - 16, "Атом самарію (Sm³⁺)", size=11, color=INK))

    f.append(circle(390, H - 20, 6, fill="#2563eb", stroke="#1e40af", sw=1.5))
    f.append(text(450, H - 16, "Атом кобальту (Co)", size=11, color=INK))

    f.append(line(540, H - 20, 565, H - 20, color="#d97706", sw=2.5))
    f.append(text(620, H - 16, "Вісь легкого намагнічування", size=11, color=INK))

    render(os.path.join(IMG_DIR, 'smco-crystal-structures.svg'), W, H, "\n".join(f))

# ── Фігура 2: Криві розмагнічування B-H та J-H ──────────────────────────────
def fig_smco_demag_curves():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 26, "Криві розмагнічування SmCo₅ та Sm₂Co₁₇ за різних температур", size=16, bold=True, color=INK))

    ox, oy = 420, 360
    gw, gh = 360, 290

    # Axes
    f.append(line(ox - gw, oy, ox + 30, oy, color="#475569", sw=2)) # H axis
    f.append(line(ox, oy + 20, ox, oy - gh, color="#475569", sw=2)) # B, J axis

    f.append(text(ox - gw + 40, oy + 25, "-H (Магнітне поле, кЕ / кА/м)", size=11, bold=True, color="#334155"))
    f.append(text(ox + 15, oy - gh + 10, "B, J (Індукція / Намагніченість, Тл)", size=11, bold=True, color="#334155"))

    # Grid lines
    for b_val in [0.5, 1.0, 1.5]:
        by = oy - (b_val / 1.5) * (gh - 30)
        f.append(line(ox - gw, by, ox, by, color="#e2e8f0", sw=1, dash="4,4"))
        f.append(text(ox + 15, by + 4, f"{b_val:.1f}", size=10, color=MUTED))

    # Curve 1: Sm2Co17 at 20°C (B-H and J-H)
    pts_j_20 = [(0, 1.15), (-15, 1.14), (-25, 1.12), (-32, 1.05), (-35, 0.0)]
    pts_b_20 = [(0, 1.15), (-15, 0.70), (-25, 0.40), (-32, 0.15), (-35, -0.1)]

    def to_svg_pts(pts):
        res = []
        for h_val, b_val in pts:
            sx = ox + (h_val / 40.0) * gw
            sy = oy - (b_val / 1.5) * (gh - 30)
            res.append(f"{sx:.1f},{sy:.1f}")
        return "M " + " L ".join(res)

    f.append(path_svg(to_svg_pts(pts_j_20), stroke="#059669", sw=2.5))
    f.append(path_svg(to_svg_pts(pts_b_20), stroke="#059669", sw=2.5, dash="6,3"))

    # Curve 2: Sm2Co17 at 300°C
    pts_j_300 = [(0, 1.0), (-12, 0.98), (-18, 0.90), (-22, 0.0)]
    pts_b_300 = [(0, 1.0), (-12, 0.62), (-18, 0.42), (-22, 0.0)]
    f.append(path_svg(to_svg_pts(pts_j_300), stroke="#d97706", sw=2.0))
    f.append(path_svg(to_svg_pts(pts_b_300), stroke="#d97706", sw=2.0, dash="6,3"))

    # Curve 3: NdFeB at 200°C (shows knee / irreversible loss)
    pts_b_nd = [(0, 1.10), (-8, 0.65), (-12, 0.10), (-14, -0.4)]
    f.append(path_svg(to_svg_pts(pts_b_nd), stroke="#dc2626", sw=2.0, dash="3,3"))

    # Annotations
    # B_r point
    f.append(circle(ox, oy - (1.15 / 1.5) * (gh - 30), 4, fill="#059669", stroke="none"))
    f.append(text(ox - 35, oy - (1.15 / 1.5) * (gh - 30) - 8, "B_r (20 °C) = 1.15 Тл", size=10, bold=True, color="#047857"))

    # H_cj point
    hc_x = ox + (-35.0 / 40.0) * gw
    f.append(circle(hc_x, oy, 4, fill="#059669", stroke="none"))
    f.append(text(hc_x - 10, oy + 18, "H_ci > 30 кЕ", size=10, bold=True, color="#047857"))

    # Recoil line annotation
    rec_x1 = ox + (-10.0 / 40.0) * gw
    rec_y1 = oy - (0.85 / 1.5) * (gh - 30)
    rec_x2 = ox + (-20.0 / 40.0) * gw
    rec_y2 = oy - (0.55 / 1.5) * (gh - 30)
    f.append(line(rec_x1, rec_y1, rec_x2, rec_y2, color="#2563eb", sw=2.0))
    f.append(text(rec_x1 - 50, rec_y1 - 12, "Лінія повернення (μ_rec ≈ 1.05)", size=10, bold=True, color="#1d4ed8"))

    # Legend box
    leg_x, leg_y = 30, 60
    f.append(rect(leg_x, leg_y, 250, 140, fill="#ffffff", stroke=BORDER, rx=4))
    f.append(text(leg_x + 125, leg_y + 18, "Позначення кривих:", size=11, bold=True, color=INK))

    f.append(line(leg_x + 15, leg_y + 40, leg_x + 55, leg_y + 40, color="#059669", sw=2.5))
    f.append(text(leg_x + 65, leg_y + 44, "Sm₂Co₁₇ J(H) при 20 °C", size=10, color=INK, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 65, leg_x + 55, leg_y + 65, color="#059669", sw=2.5, dash="6,3"))
    f.append(text(leg_x + 65, leg_y + 69, "Sm₂Co₁₇ B(H) при 20 °C", size=10, color=INK, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 90, leg_x + 55, leg_y + 90, color="#d97706", sw=2.0, dash="6,3"))
    f.append(text(leg_x + 65, leg_y + 94, "Sm₂Co₁₇ B(H) при 300 °C", size=10, color=INK, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 115, leg_x + 55, leg_y + 115, color="#dc2626", sw=2.0, dash="3,3"))
    f.append(text(leg_x + 65, leg_y + 119, "NdFeB B(H) при 200 °C (злам)", size=10, color=INK, anchor="start"))

    # Bottom note
    f.append(text(W / 2, H - 12, "Завдяки лінійній кривій B(H) SmCo витримує сильні розмагнічувальні поля без незворотних втрат", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'smco-demag-curves.svg'), W, H, "\n".join(f))

# ── Фігура 3: Температурна стабільність SmCo проти NdFeB ────────────────────
def fig_smco_temp_stability_comparison():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 26, "Температурна залежність залишкові індукції (B_r) різних магнітотвердих матеріалів", size=16, bold=True, color=INK))

    ox, oy = 80, 330
    gw, gh = 640, 250

    # Axes
    f.append(line(ox, oy, ox + gw, oy, color="#475569", sw=2)) # T axis
    f.append(line(ox, oy, ox, oy - gh, color="#475569", sw=2)) # B_r axis

    f.append(text(ox + gw - 30, oy + 25, "Температура T (°C)", size=11, bold=True, color="#334155"))
    f.append(text(ox - 35, oy - gh + 15, "B_r (Тл)", size=11, bold=True, color="#334155"))

    # Temp Ticks (0, 100, 200, 300, 400, 500, 600, 700, 800)
    for t_val in range(0, 801, 100):
        tx = ox + (t_val / 800.0) * gw
        f.append(line(tx, oy, tx, oy + 5, color="#475569", sw=1.5))
        f.append(text(tx, oy + 18, str(t_val), size=10, color=MUTED))
        if t_val > 0 and t_val < 800:
            f.append(line(tx, oy, tx, oy - gh, color="#f1f5f9", sw=1))

    # B_r Ticks (0.0 to 1.4)
    for b_val in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
        by = oy - (b_val / 1.4) * gh
        f.append(line(ox - 5, by, ox, by, color="#475569", sw=1.5))
        f.append(text(ox - 18, by + 4, f"{b_val:.1f}", size=10, color=MUTED))

    # Helper coordinate transformer
    def get_xy(t_val, b_val):
        return ox + (t_val / 800.0) * gw, oy - (b_val / 1.4) * gh

    # 1. NdFeB (N35 / 35UH): Br starts high 1.25, drops fast, Tc = 315°C
    pts_nd = [(0, 1.25), (100, 1.10), (150, 0.95), (200, 0.75), (280, 0.30), (315, 0.0)]
    d_nd = "M " + " L ".join(f"{get_xy(t,b)[0]:.1f},{get_xy(t,b)[1]:.1f}" for t, b in pts_nd)
    f.append(path_svg(d_nd, stroke="#dc2626", sw=2.5))
    f.append(text(get_xy(160, 0.98)[0] + 45, get_xy(160, 0.98)[1] - 5, "NdFeB (T_C = 315 °C)", size=10, bold=True, color="#dc2626"))

    # 2. SmCo5: Br starts 1.0, α = -0.04%/°C, Tc = 727°C
    pts_sm15 = [(0, 1.0), (200, 0.92), (400, 0.82), (600, 0.60), (700, 0.25), (727, 0.0)]
    d_sm15 = "M " + " L ".join(f"{get_xy(t,b)[0]:.1f},{get_xy(t,b)[1]:.1f}" for t, b in pts_sm15)
    f.append(path_svg(d_sm15, stroke="#2563eb", sw=2.5))
    f.append(text(get_xy(420, 0.82)[0] + 55, get_xy(420, 0.82)[1] - 8, "SmCo₅ (T_C = 727 °C)", size=10, bold=True, color="#2563eb"))

    # 3. Sm2Co17 (2:17 HT): Br starts 1.12, α = -0.03%/°C, Tc = 820°C
    pts_sm217 = [(0, 1.12), (200, 1.05), (400, 0.97), (550, 0.88), (700, 0.60), (800, 0.15)]
    d_sm217 = "M " + " L ".join(f"{get_xy(t,b)[0]:.1f},{get_xy(t,b)[1]:.1f}" for t, b in pts_sm217)
    f.append(path_svg(d_sm217, stroke="#059669", sw=3.0))
    f.append(text(get_xy(500, 0.95)[0] + 15, get_xy(500, 0.95)[1] - 12, "Sm₂Co₁₇ (T_C = 820 °C)", size=11, bold=True, color="#047857"))

    # Highlight region > 200°C where SmCo dominates
    rx1, ry1 = get_xy(180, 1.38)
    rx2, ry2 = get_xy(550, 0.15)
    f.append(rect(rx1, ry1, rx2 - rx1, ry2 - ry1, fill="#fef3c7", stroke="#f59e0b", rx=4, sw=1.5))
    f.append(text(rx1 + (rx2 - rx1) / 2, ry1 + 20, "Область беззаперечного домінування SmCo (T > 180-200 °C)", size=11, bold=True, color="#b45309"))

    render(os.path.join(IMG_DIR, 'smco-temp-stability-comparison.svg'), W, H, "\n".join(f))

# ── Фігура 4: Мікроструктура та закріплення доменних стінок у Sm2Co17 ────────
def fig_smco_microstructure_pinning():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 26, "Коерцитивні механізми та осередкова мікроструктура сплаву Sm₂Co₁₇", size=16, bold=True, color=INK))

    # Panel 1: Single domain grains in SmCo5 (Nucleation)
    p1_x, p1_y, p1_w, p1_h = 20, 50, 360, 320
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(p1_x + p1_w / 2, p1_y + 22, "SmCo₅: Механізм зародкоутворення (Nucleation)", size=12, bold=True, color="#1e3a8a"))

    # Single domain grains diagram
    f.append(rect(p1_x + 30, p1_y + 50, 140, 110, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(p1_x + 100, p1_y + 68, "Однодоменне зерно", size=10, bold=True, color="#1e40af"))
    f.append(arrow(p1_x + 100, p1_y + 140, p1_x + 100, p1_y + 85, color="#1d4ed8", sw=3))

    f.append(rect(p1_x + 190, p1_y + 50, 140, 110, fill="#fef2f2", stroke="#fca5a5", rx=4))
    f.append(text(p1_x + 260, p1_y + 68, "Дефект на межі зерна", size=10, bold=True, color="#991b1b"))
    # Reverse domain nucleation
    f.append(circle(p1_x + 260, p1_y + 145, 18, fill="#fecaca", stroke="#dc2626", sw=1.5))
    f.append(arrow(p1_x + 260, p1_y + 135, p1_x + 260, p1_y + 155, color="#dc2626", sw=2.5))
    f.append(text(p1_x + 260, p1_y + 110, "Зародок розмагн.", size=9, color="#991b1b"))

    f.append(fitbox(p1_x + 20, p1_y + 180, p1_w - 40, 120, 
                    "Поведінка: Зерна дрібні (1-5 мкм).\nВручну зміщені стінки легко рухаються,\nпроте для зародження зворотного домену\nпотрібне величезне зовнішнє поле H_ci ≈ H_A.",
                    fill="#ffffff", stroke="#cbd5e1", size=10, color=INK))

    # Panel 2: Cellular microstructure in Sm2Co17 (Pinning)
    p2_x, p2_y, p2_w, p2_h = 400, 50, 360, 320
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(p2_x + p2_w / 2, p2_y + 22, "Sm₂Co₁₇: Механізм пінінгу (Cellular Pinning)", size=12, bold=True, color="#065f46"))

    # Rhombohedral cell representation
    cx, cy = p2_x + 180, p2_y + 115
    f.append(rect(cx - 90, cy - 50, 180, 100, fill="#ecfdf5", stroke="#10b981", rx=4, sw=2))
    f.append(text(cx, cy - 30, "Основна осередкова фаза 2:17", size=10, bold=True, color="#047857"))
    f.append(text(cx, cy - 14, "(Sm₂Co₁₇ rhombohedral, ~100 нм)", size=9, color=MUTED))

    # Boundary phase lines (Cu-rich 1:5 phase)
    f.append(rect(cx - 96, cy - 56, 192, 112, fill="none", stroke="#d97706", rx=6, sw=3))
    f.append(text(cx, cy + 24, "Межова фаза 1:5 (збагачена Cu)", size=10, bold=True, color="#b45309"))

    # Z-phase platelets
    f.append(line(cx - 110, cy, cx + 110, cy, color="#7e22ce", sw=2.5, dash="4,2"))
    f.append(text(cx, cy + 42, "Пластинчаста Z-фаза (Zr₂Co₁₁)", size=9, bold=True, color="#6b21a8"))

    # Pinned Domain Wall
    f.append(line(cx - 96, cy - 40, cx - 96, cy + 40, color="#dc2626", sw=3.5))
    f.append(text(cx - 120, cy - 45, "Закріплена стінка (Pinning)", size=9, bold=True, color="#dc2626"))

    f.append(fitbox(p2_x + 20, p2_y + 180, p2_w - 40, 120,
                    "Поведінка: Градієнт енергії доменної стінки\nΔγ_w між фазою 2:17 та межовою фазою 1:5 (Cu)\nстворює потужні пастки (пінінг).\nДоменна стінка надійно застрягає на межах.",
                    fill="#ffffff", stroke="#cbd5e1", size=10, color=INK))

    render(os.path.join(IMG_DIR, 'smco-microstructure-pinning.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_smco_crystal_structures()
    fig_smco_demag_curves()
    fig_smco_temp_stability_comparison()
    fig_smco_microstructure_pinning()
    print("Всі 4 фігури успішно згенеровані у ./img/")
