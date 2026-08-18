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

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'

# 1. 2D Material Lattices: Graphene, TMD (MoS2), and h-BN
def gen_lattices_2d():
    w, h = 840, 360
    frags = []

    # Title
    frags.append(text(w / 2, 25, "Геометрія атомних ґраток 2D матеріалів: Графен, TMD (MoS₂) та h-BN", size=16, bold=True))

    # Panel 1: Graphene (Honeycomb lattice)
    p1_x, p1_y, p1_w, p1_h = 20, 55, 250, 280
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Графен (Monolayer C)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w/2, p1_y + 45, "Однорідний sp² вуглець", size=12, color=MUTED, italic=True))

    # Draw hexagonal lattice inside Panel 1
    cx1, cy1 = p1_x + 125, p1_y + 150
    r_hex = 32.0
    for row in range(-2, 3):
        for col in range(-2, 3):
            hx = cx1 + col * r_hex * 1.732 + (row % 2) * r_hex * 0.866
            hy = cy1 + row * r_hex * 1.5
            if p1_x + 25 < hx < p1_x + p1_w - 25 and p1_y + 60 < hy < p1_y + p1_h - 45:
                pts = []
                for angle_deg in range(30, 390, 60):
                    rad = math.radians(angle_deg)
                    pts.append((hx + r_hex * math.cos(rad), hy + r_hex * math.sin(rad)))
                for k in range(6):
                    frags.append(line(pts[k][0], pts[k][1], pts[(k+1)%6][0], pts[(k+1)%6][1], color="#94a3b8", sw=1.8))
                for k in range(6):
                    node_color = POS if k % 2 == 0 else NEG
                    frags.append(circle(pts[k][0], pts[k][1], 5.5, fill=node_color, stroke="#1e293b", sw=1.0))

    frags.append(text(p1_x + p1_w/2, p1_y + p1_h - 15, "Підґратки A (червона) та B (синя)", size=11, color=INK))

    # Panel 2: TMD MoS2 (Sandwich layer X-M-X)
    p2_x, p2_y, p2_w, p2_h = 295, 55, 250, 280
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "TMD (MoS₂ / WSe₂)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w/2, p2_y + 45, "Тришаровий сендвіч X-M-X", size=12, color=MUTED, italic=True))

    sy_top = p2_y + 95
    sy_mid = p2_y + 155
    sy_bot = p2_y + 215

    frags.append(line(p2_x + 30, sy_top, p2_x + p2_w - 30, sy_top, color="#cbd5e1", sw=1.0, dash="3,3"))
    frags.append(line(p2_x + 30, sy_mid, p2_x + p2_w - 30, sy_mid, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(p2_x + 30, sy_bot, p2_x + p2_w - 30, sy_bot, color="#cbd5e1", sw=1.0, dash="3,3"))

    for i in range(4):
        ax = p2_x + 45 + i * 52
        frags.append(circle(ax, sy_top, 9.0, fill="#f59e0b", stroke="#b45309", sw=1.2))
        frags.append(circle(ax, sy_bot, 9.0, fill="#f59e0b", stroke="#b45309", sw=1.2))
        mx = ax + 26
        if mx < p2_x + p2_w - 35:
            frags.append(circle(mx, sy_mid, 11.0, fill="#0284c7", stroke="#0369a1", sw=1.2))
            frags.append(line(ax, sy_top, mx, sy_mid, color="#64748b", sw=1.5))
            frags.append(line(ax, sy_bot, mx, sy_mid, color="#64748b", sw=1.5))
            if i + 1 < 4:
                frags.append(line(ax + 52, sy_top, mx, sy_mid, color="#64748b", sw=1.5))
                frags.append(line(ax + 52, sy_bot, mx, sy_mid, color="#64748b", sw=1.5))

    frags.append(text(p2_x + 20, sy_top + 4, "S", size=12, bold=True, color="#b45309"))
    frags.append(text(p2_x + 20, sy_mid + 4, "Mo", size=12, bold=True, color="#0369a1"))
    frags.append(text(p2_x + 20, sy_bot + 4, "S", size=12, bold=True, color="#b45309"))
    frags.append(text(p2_x + p2_w/2, p2_y + p2_h - 15, "Ковалентні зв'язки Mo-S", size=11, color=INK))

    # Panel 3: Hexagonal Boron Nitride (h-BN)
    p3_x, p3_y, p3_w, p3_h = 570, 55, 250, 280
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p3_x + p3_w/2, p3_y + 25, "h-BN (Boron Nitride)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p3_x + p3_w/2, p3_y + 45, "Полярна ґратка, Eg ≈ 6 еВ", size=12, color=MUTED, italic=True))

    cx3, cy3 = p3_x + 125, p3_y + 150
    for row in range(-2, 3):
        for col in range(-2, 3):
            hx = cx3 + col * r_hex * 1.732 + (row % 2) * r_hex * 0.866
            hy = cy3 + row * r_hex * 1.5
            if p3_x + 25 < hx < p3_x + p3_w - 25 and p3_y + 60 < hy < p3_y + p3_h - 45:
                pts = []
                for angle_deg in range(30, 390, 60):
                    rad = math.radians(angle_deg)
                    pts.append((hx + r_hex * math.cos(rad), hy + r_hex * math.sin(rad)))
                for k in range(6):
                    frags.append(line(pts[k][0], pts[k][1], pts[(k+1)%6][0], pts[(k+1)%6][1], color="#94a3b8", sw=1.8))
                for k in range(6):
                    node_color = "#ec4899" if k % 2 == 0 else "#10b981"
                    frags.append(circle(pts[k][0], pts[k][1], 5.5, fill=node_color, stroke="#1e293b", sw=1.0))

    frags.append(text(p3_x + p3_w/2, p3_y + p3_h - 15, "Атоми Бору B (рожеві) та Азоту N (зелені)", size=11, color=INK))

    render(os.path.join(OUT_DIR, "lattices-2d.svg"), w, h, *frags)

# 2. Dirac Cone Dispersion in Graphene
def gen_dirac_cone():
    w, h = 680, 420
    frags = []

    frags.append(text(w / 2, 25, "Електронна зонна структура графена поблизу точки K: конус Дірака", size=16, bold=True))

    cx, cy = 340, 220

    # Upper Cone
    top_poly = [
        (cx, cy),
        (cx - 160, cy - 140),
        (cx + 160, cy - 140)
    ]
    frags.append(polygon(top_poly, fill="#eff6ff", stroke="#3b82f6", sw=1.8))
    frags.append(ellipse(cx, cy - 140, 160, 35, fill="#dbeafe", stroke="#2563eb", sw=1.5))

    # Lower Cone
    bot_poly = [
        (cx, cy),
        (cx - 160, cy + 140),
        (cx + 160, cy + 140)
    ]
    frags.append(polygon(bot_poly, fill="#fef2f2", stroke="#ef4444", sw=1.8))
    frags.append(ellipse(cx, cy + 140, 160, 35, fill="#fee2e2", stroke="#dc2626", sw=1.5))

    # Axis E
    frags.append(arrow(cx - 210, cy + 165, cx - 210, cy - 165, color="#1e293b", sw=2.0))
    frags.append(text(cx - 210, cy - 178, "Енергія E", size=13, bold=True))

    # Fermi level EF line
    frags.append(line(cx - 220, cy, cx + 220, cy, color="#475569", sw=1.5, dash="4,4"))
    frags.append(text(cx + 225, cy + 4, "E_F (Рівень Фермі)", size=12, bold=True, color="#0f172a", anchor="start"))

    # Dirac Point (K)
    frags.append(circle(cx, cy, 5.0, fill="#1e293b", stroke="#ffffff", sw=1.5))
    frags.append(text(cx + 12, cy - 8, "Точка Дірака (K / K')", size=13, bold=True, color="#0f172a", anchor="start"))

    # Band labels
    frags.append(text(cx - 90, cy - 70, "Зона провідності π*", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(cx - 90, cy + 70, "Валентна зона π", size=13, bold=True, color="#b91c1c"))

    # Linear dispersion slope annotation
    frags.append(arrow(cx + 40, cy - 35, cx + 110, cy - 96, color="#0284c7", sw=1.5))
    frags.append(text(cx + 140, cy - 65, "E(q) = ± ℏ·v_F·|q|", size=13, bold=True, color="#0369a1", anchor="start"))
    frags.append(text(cx + 140, cy - 45, "v_F ≈ 10⁶ м/с", size=12, color=MUTED, anchor="start"))

    # Momentum axis q
    frags.append(arrow(cx - 180, cy + 185, cx + 180, cy + 185, color="#1e293b", sw=1.5))
    frags.append(text(cx + 195, cy + 189, "Хвильовий вектор q = k - K", size=12, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "dirac-cone.svg"), w, h, *frags)

# 3. TMD Bandgap Transition: Bulk (Indirect) vs Monolayer (Direct)
def gen_tmd_bandgap():
    w, h = 760, 380
    frags = []

    frags.append(text(w / 2, 25, "Трансформація зонної структури MoS₂: Об'єм (непряма) vs Моношар (пряма)", size=16, bold=True))

    # Left Panel: Bulk MoS2
    p1_x, p1_y, p1_w, p1_h = 40, 55, 320, 300
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Об'ємний MoS₂ (Bulk)", size=14, bold=True))
    frags.append(text(p1_x + p1_w/2, p1_y + 45, "Непряма заборонена зона Eg ≈ 1.2 еВ", size=12, color="#b91c1c", bold=True))

    frags.append(arrow(p1_x + 35, p1_y + p1_h - 35, p1_x + 35, p1_y + 65, color="#475569", sw=1.5))
    frags.append(text(p1_x + 20, p1_y + 65, "E", size=12, bold=True))
    frags.append(line(p1_x + 35, p1_y + p1_h - 35, p1_x + p1_w - 20, p1_y + p1_h - 35, color="#475569", sw=1.5))

    g_x = p1_x + 60
    k_x = p1_x + 200
    m_x = p1_x + 290
    frags.append(text(g_x, p1_y + p1_h - 18, "Γ", size=12, bold=True))
    frags.append(text(k_x, p1_y + p1_h - 18, "K", size=12, bold=True))
    frags.append(text(m_x, p1_y + p1_h - 18, "M", size=12, bold=True))

    path_cb1 = f"M {g_x} {p1_y+130} Q {p1_x+130} {p1_y+150} {k_x} {p1_y+120} Q {p1_x+250} {p1_y+110} {m_x} {p1_y+130}"
    frags.append(path(path_cb1, fill="none", stroke="#2563eb", sw=2.2))

    path_vb1 = f"M {g_x} {p1_y+180} Q {p1_x+130} {p1_y+210} {k_x} {p1_y+220} Q {p1_x+250} {p1_y+230} {m_x} {p1_y+210}"
    frags.append(path(path_vb1, fill="none", stroke="#dc2626", sw=2.2))

    frags.append(arrow(g_x, p1_y+180, k_x, p1_y+120, color="#7c3aed", sw=1.8))
    frags.append(text(p1_x + 125, p1_y + 165, "Непрямий перехід", size=11, color="#7c3aed", bold=True))

    # Right Panel: Monolayer MoS2
    p2_x, p2_y, p2_w, p2_h = 400, 55, 320, 300
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Моношар MoS₂ (Monolayer)", size=14, bold=True))
    frags.append(text(p2_x + p2_w/2, p2_y + 45, "Пряма заборонена зона Eg ≈ 1.9 еВ", size=12, color="#059669", bold=True))

    frags.append(arrow(p2_x + 35, p2_y + p2_h - 35, p2_x + 35, p2_y + 65, color="#475569", sw=1.5))
    frags.append(text(p2_x + 20, p2_y + 65, "E", size=12, bold=True))
    frags.append(line(p2_x + 35, p2_y + p2_h - 35, p2_x + p2_w - 20, p2_y + p2_h - 35, color="#475569", sw=1.5))

    g2_x = p2_x + 60
    k2_x = p2_x + 200
    m2_x = p2_x + 290
    frags.append(text(g2_x, p2_y + p2_h - 18, "Γ", size=12, bold=True))
    frags.append(text(k2_x, p2_y + p2_h - 18, "K", size=12, bold=True))
    frags.append(text(m2_x, p2_y + p2_h - 18, "M", size=12, bold=True))

    path_cb2 = f"M {g2_x} {p2_y+130} Q {p2_x+130} {p2_y+160} {k2_x} {p2_y+110} Q {p2_x+250} {p2_y+140} {m2_x} {p2_y+130}"
    frags.append(path(path_cb2, fill="none", stroke="#2563eb", sw=2.2))

    path_vb2_up = f"M {g2_x} {p2_y+220} Q {p2_x+130} {p2_y+200} {k2_x} {p2_y+190} Q {p2_x+250} {p2_y+220} {m2_x} {p2_y+230}"
    path_vb2_dn = f"M {g2_x} {p2_y+220} Q {p2_x+130} {p2_y+215} {k2_x} {p2_y+210} Q {p2_x+250} {p2_y+225} {m2_x} {p2_y+230}"
    frags.append(path(path_vb2_up, fill="none", stroke="#dc2626", sw=2.2))
    frags.append(path(path_vb2_dn, fill="none", stroke="#ea580c", sw=1.8, dash="3,3"))

    frags.append(arrow(k2_x, p2_y+190, k2_x, p2_y+110, color="#059669", sw=2.2))
    frags.append(text(k2_x + 10, p2_y + 150, "Прямий оптичний перехід", size=11, color="#059669", bold=True, anchor="start"))
    frags.append(text(k2_x - 70, p2_y + 205, "ΔE_SOC ≈ 150 меВ", size=10, color="#ea580c", bold=True))

    render(os.path.join(OUT_DIR, "tmd-bandgap.svg"), w, h, *frags)

# 4. van der Waals Heterostructure and Moiré Superlattice
def gen_vdw_heterostructure():
    w, h = 760, 390
    frags = []

    frags.append(text(w / 2, 25, "Архітектура вандерваальсової гетероструктури та муарова надґратка", size=16, bold=True))

    # Left: Vertical heterostructure stack
    p1_x, p1_y, p1_w, p1_h = 40, 55, 340, 310
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w/2, p1_y + 25, "Вандерваальсів стек (vdW Stack)", size=14, bold=True))

    frags.append(rect(p1_x + 30, p1_y + 250, p1_w - 60, 35, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=3))
    frags.append(text(p1_x + p1_w/2, p1_y + 272, "Підкладка SiO₂ / Si", size=12, color=INK))

    frags.append(rect(p1_x + 30, p1_y + 200, p1_w - 60, 25, fill="#fbcfe8", stroke="#db2777", sw=1.2, rx=3))
    frags.append(text(p1_x + p1_w/2, p1_y + 217, "Нижній диелектрик h-BN (10-30 нм)", size=12, color="#9d174d", bold=True))

    frags.append(rect(p1_x + 30, p1_y + 160, p1_w - 60, 20, fill="#bae6fd", stroke="#0284c7", sw=1.2, rx=3))
    frags.append(text(p1_x + p1_w/2, p1_y + 175, "Канал MoS₂ (Моношар ~0.7 нм)", size=12, color="#0369a1", bold=True))

    frags.append(rect(p1_x + 30, p1_y + 120, p1_w - 60, 25, fill="#fbcfe8", stroke="#db2777", sw=1.2, rx=3))
    frags.append(text(p1_x + p1_w/2, p1_y + 137, "Верхній h-BN (Затворна ізоляція)", size=12, color="#9d174d", bold=True))

    frags.append(rect(p1_x + 50, p1_y + 80, p1_w - 100, 18, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=3))
    frags.append(text(p1_x + p1_w/2, p1_y + 93, "Затвор з графена", size=12, color="#1e293b", bold=True))

    frags.append(arrow(p1_x + 285, p1_y + 160, p1_x + 285, p1_y + 145, color="#7c3aed", sw=1.5))
    frags.append(text(p1_x + 285, p1_y + 152, "d_vdW", size=10, color="#7c3aed", bold=True, anchor="start"))

    # Right: Moiré Superlattice
    p2_x, p2_y, p2_w, p2_h = 410, 55, 310, 310
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w/2, p2_y + 25, "Муарова надґратка (Moiré)", size=14, bold=True))
    frags.append(text(p2_x + p2_w/2, p2_y + 45, "Кут повороту θ (Магічний кут 1.08°)", size=12, color=MUTED, italic=True))

    mc_x, mc_y = p2_x + p2_w/2, p2_y + 175
    for row in range(-2, 3):
        for col in range(-2, 3):
            mx = mc_x + col * 55 + (row % 2) * 27
            my = mc_y + row * 48
            if p2_x + 25 < mx < p2_x + p2_w - 25 and p2_y + 60 < my < p2_y + p2_h - 40:
                frags.append(circle(mx, my, 22.0, fill="#fef08a", stroke="#eab308", sw=1.5))
                frags.append(circle(mx, my, 8.0, fill="#ca8a04", stroke="#854d0e", sw=1.0))

    frags.append(text(p2_x + p2_w/2, p2_y + p2_h - 20, "Період муару L_m = a / (2·sin(θ/2))", size=12, color="#854d0e", bold=True))

    render(os.path.join(OUT_DIR, "vdw-heterostructure.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_lattices_2d()
    gen_dirac_cone()
    gen_tmd_bandgap()
    gen_vdw_heterostructure()
    print("SVG generation complete.")
