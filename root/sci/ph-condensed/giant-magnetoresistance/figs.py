# -*- coding: utf-8 -*-
"""Фігури до теми «Гігантський магнітоопір (GMR)».
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

# ── Фігура 1: Двоканальна модель Мотта ─────────────────────────────────────────
def fig_mott_two_channel():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 28, "Двоканальна модель Мотта для паралельного та антипаралельного станів", size=16, bold=True, color=INK))

    p_w = 370
    p_h = 340
    y0 = 55

    # Left panel: Parallel alignment (Low Resistance)
    x1 = 25
    f.append(rect(x1, y0, p_w, p_h, fill="#f0fdf4", stroke="#bbf7d0", rx=8))
    f.append(text(x1 + p_w / 2, y0 + 24, "Паралельний стан (FM1 ↑ / FM2 ↑)", size=14, bold=True, color="#15803d"))
    f.append(text(x1 + p_w / 2, y0 + 44, "Низький опір: R_P (Коротке замикання каналу спін-вгору)", size=11, bold=True, color="#166534"))

    # Ferromagnetic layers (Left)
    f.append(rect(x1 + 30, y0 + 70, 90, 160, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(x1 + 75, y0 + 90, "FM 1", size=12, bold=True, color="#1d4ed8"))
    f.append(arrow(x1 + 75, y0 + 190, x1 + 75, y0 + 115, color="#1d4ed8", sw=3))
    f.append(text(x1 + 75, y0 + 210, "M₁ ↑", size=12, bold=True, color="#1d4ed8"))

    # Non-magnetic spacer
    f.append(rect(x1 + 140, y0 + 70, 70, 160, fill="#f1f5f9", stroke="#94a3b8", rx=4))
    f.append(text(x1 + 175, y0 + 150, "NM (Cu)", size=11, bold=True, color="#475569"))

    # Ferromagnetic layer 2 (Left)
    f.append(rect(x1 + 230, y0 + 70, 90, 160, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(x1 + 275, y0 + 90, "FM 2", size=12, bold=True, color="#1d4ed8"))
    f.append(arrow(x1 + 275, y0 + 190, x1 + 275, y0 + 115, color="#1d4ed8", sw=3))
    f.append(text(x1 + 275, y0 + 210, "M₂ ↑", size=12, bold=True, color="#1d4ed8"))

    # Channel Spin-up trajectory (weak scattering -> low resistance)
    f.append(path_svg(f"M {x1 + 15} {y0 + 110} L {x1 + 335} {y0 + 110}", stroke="#15803d", sw=3.5))
    f.append(circle(x1 + 50, y0 + 110, 5, fill="#15803d", stroke="none"))
    f.append(circle(x1 + 290, y0 + 110, 5, fill="#15803d", stroke="none"))
    f.append(text(x1 + 175, y0 + 102, "Канал спін-↑ (мале розсіювання r_↑)", size=10, bold=True, color="#15803d"))

    # Channel Spin-down trajectory (strong scattering -> high resistance)
    pts_dn1 = f"M {x1 + 15} {y0 + 170} L {x1 + 65} {y0 + 170} L {x1 + 80} {y0 + 155} L {x1 + 100} {y0 + 185} L {x1 + 120} {y0 + 170} L {x1 + 240} {y0 + 170} L {x1 + 265} {y0 + 150} L {x1 + 285} {y0 + 180} L {x1 + 335} {y0 + 170}"
    f.append(path_svg(pts_dn1, stroke="#dc2626", sw=2, dash="3,2"))
    f.append(text(x1 + 175, y0 + 182, "Канал спін-↓ (сильне розсіювання r_↓)", size=10, bold=True, color="#b91c1c"))

    # Equivalent circuit diagram parallel
    f.append(rect(x1 + 35, y0 + 250, 300, 75, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(x1 + p_w / 2, y0 + 270, "Схема: r_↑ || r_↓", size=11, bold=True, color=INK))
    f.append(text(x1 + p_w / 2, y0 + 295, "R_P = (r_↑ · r_↓) / (r_↑ + r_↓) ≈ r_↑", size=12, bold=True, color="#15803d"))

    # Right panel: Antiparallel alignment (High Resistance)
    x2 = 425
    f.append(rect(x2, y0, p_w, p_h, fill="#fff1f2", stroke="#fecdd3", rx=8))
    f.append(text(x2 + p_w / 2, y0 + 24, "Антипаралельний стан (FM1 ↑ / FM2 ↓)", size=14, bold=True, color="#be123c"))
    f.append(text(x2 + p_w / 2, y0 + 44, "Високий опір: R_AP (Обидва канали розсіюються)", size=11, bold=True, color="#9f1239"))

    # Ferromagnetic layer 1 (Right)
    f.append(rect(x2 + 30, y0 + 70, 90, 160, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(x2 + 75, y0 + 90, "FM 1", size=12, bold=True, color="#1d4ed8"))
    f.append(arrow(x2 + 75, y0 + 190, x2 + 75, y0 + 115, color="#1d4ed8", sw=3))
    f.append(text(x2 + 75, y0 + 210, "M₁ ↑", size=12, bold=True, color="#1d4ed8"))

    # Non-magnetic spacer
    f.append(rect(x2 + 140, y0 + 70, 70, 160, fill="#f1f5f9", stroke="#94a3b8", rx=4))
    f.append(text(x2 + 175, y0 + 150, "NM (Cu)", size=11, bold=True, color="#475569"))

    # Ferromagnetic layer 2 (Right - Down)
    f.append(rect(x2 + 230, y0 + 70, 90, 160, fill="#fed7aa", stroke="#f97316", rx=4))
    f.append(text(x2 + 275, y0 + 90, "FM 2", size=12, bold=True, color="#c2410c"))
    f.append(arrow(x2 + 275, y0 + 115, x2 + 275, y0 + 190, color="#c2410c", sw=3))
    f.append(text(x2 + 275, y0 + 210, "M₂ ↓", size=12, bold=True, color="#c2410c"))

    # Spin-up trajectory (weak scattering in FM1, strong in FM2)
    pts_up2 = f"M {x2 + 15} {y0 + 110} L {x2 + 230} {y0 + 110} L {x2 + 255} {y0 + 90} L {x2 + 275} {y0 + 125} L {x2 + 335} {y0 + 110}"
    f.append(path_svg(pts_up2, stroke="#d97706", sw=2.5, dash="4,2"))
    f.append(text(x2 + 175, y0 + 102, "Спін-↑: r_↑ у FM1, але r_↓ у FM2", size=10, bold=True, color="#b45309"))

    # Spin-down trajectory (strong scattering in FM1, weak in FM2)
    pts_dn2 = f"M {x2 + 15} {y0 + 170} L {x2 + 65} {y0 + 170} L {x2 + 80} {y0 + 155} L {x2 + 100} {y0 + 185} L {x2 + 120} {y0 + 170} L {x2 + 335} {y0 + 170}"
    f.append(path_svg(pts_dn2, stroke="#d97706", sw=2.5, dash="4,2"))
    f.append(text(x2 + 175, y0 + 182, "Спін-↓: r_↓ у FM1, але r_↑ у FM2", size=10, bold=True, color="#b45309"))

    # Equivalent circuit diagram antiparallel
    f.append(rect(x2 + 35, y0 + 250, 300, 75, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(x2 + p_w / 2, y0 + 270, "Схема: (r_↑ + r_↓) || (r_↓ + r_↑)", size=11, bold=True, color=INK))
    f.append(text(x2 + p_w / 2, y0 + 295, "R_AP = (r_↑ + r_↓) / 2 > R_P", size=12, bold=True, color="#be123c"))

    f.append(text(W / 2, H - 15, "Різниця між R_AP та R_P визначає величину ефекту гігантського магнітоопору (GMR)", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig1-mott-two-channel.svg'), W, H, "\n".join(f))

# ── Фігура 2: Структура суперґратки Fe/Cr vs Спиновий клапан ──────────────────
def fig_gmr_multilayer_vs_spin_valve():
    W, H = 800, 420
    f = []

    f.append(text(W / 2, 28, "Порівняння геометричних структур: Багатошарова суперґратка vs Спиновий клапан", size=16, bold=True, color=INK))

    w_p = 360
    h_p = 330
    y0 = 55

    # Left: Multilayer Fe/Cr
    x1 = 25
    f.append(rect(x1, y0, w_p, h_p, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x1 + w_p / 2, y0 + 22, "Багатошарова суперґратка (Fe/Cr)_N", size=13, bold=True, color=INK))
    f.append(text(x1 + w_p / 2, y0 + 40, "Осциляційний RKKY-зв'язок (H_sat ~ 1-2 Тл)", size=10, bold=True, color=MUTED))

    # Stack layers
    y_stack = y0 + 60
    layer_h = 24
    colors_multi = [
        ("#3b82f6", "Fe (3 нм) ↑"),
        ("#94a3b8", "Cr (0.9 нм) - RKKY АФМ"),
        ("#3b82f6", "Fe (3 нм) ↓"),
        ("#94a3b8", "Cr (0.9 нм) - RKKY АФМ"),
        ("#3b82f6", "Fe (3 нм) ↑"),
        ("#94a3b8", "Cr (0.9 нм) - RKKY АФМ"),
        ("#3b82f6", "Fe (3 нм) ↓"),
        ("#64748b", "Підкладка (Substrate)")
    ]

    for idx, (col, lbl) in enumerate(colors_multi):
        ly = y_stack + idx * (layer_h + 3)
        f.append(rect(x1 + 40, ly, 280, layer_h, fill=col, stroke="none", rx=3))
        f.append(text(x1 + 180, ly + layer_h / 2 + 4, lbl, size=11, bold=True, color="#ffffff" if col != "#f1f5f9" else INK))

    # Right: Spin Valve
    x2 = 415
    f.append(rect(x2, y0, w_p, h_p, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x2 + w_p / 2, y0 + 22, "Спиновий клапан (Spin Valve)", size=13, bold=True, color=INK))
    f.append(text(x2 + w_p / 2, y0 + 40, "Екранне закріплення (H_sens ~ 0.5-5 мТл)", size=10, bold=True, color=MUTED))

    layers_sv = [
        ("#475569", "Захисний шар (Cap: Ta / Ru)"),
        ("#3b82f6", "Вільний шар (Free Layer: NiFe / CoFe) ↑↓"),
        ("#f59e0b", "Немагнітна проміжка (Spacer: Cu 2-3 нм)"),
        ("#1d4ed8", "Закріплений шар (Pinned Layer: CoFe) ↑"),
        ("#dc2626", "Антиферомагнетик (AFM Pinning: IrMn / PtMn)"),
        ("#94a3b8", "Буферний шар (Seed Layer: Ta / NiFeCr)"),
        ("#64748b", "Підкладка (Substrate: Si/SiO₂)")
    ]

    y_sv = y0 + 60
    layer_h_sv = 28
    for idx, (col, lbl) in enumerate(layers_sv):
        ly = y_sv + idx * (layer_h_sv + 3)
        f.append(rect(x2 + 30, ly, 300, layer_h_sv, fill=col, stroke="none", rx=3))
        f.append(text(x2 + 180, ly + layer_h_sv / 2 + 4, lbl, size=11, bold=True, color="#ffffff"))

    f.append(text(W / 2, H - 15, "Спинові клапани потребують у 1000 разів менших магнітних полів для перемикання ніж суперґратки", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig2-gmr-multilayer-vs-spin-valve.svg'), W, H, "\n".join(f))

# ── Фігура 3: Криві M(H) та R(H) спинового клапана ────────────────────────────
def fig_gmr_hysteresis_curve():
    W, H = 800, 430
    f = []

    f.append(text(W / 2, 28, "Гістерезис намагніченості M(H) та магнітоопору R(H) спинового клапана", size=16, bold=True, color=INK))

    w_p = 360
    h_p = 330
    y0 = 55

    # Left plot: M(H)
    x1 = 25
    f.append(rect(x1, y0, w_p, h_p, fill="#ffffff", stroke=BORDER, rx=6))
    f.append(text(x1 + w_p / 2, y0 + 22, "Петля намагніченості M(H)", size=13, bold=True, color=INK))

    cx1 = x1 + w_p / 2
    cy1 = y0 + h_p / 2 + 10

    # Axes M(H)
    f.append(arrow(x1 + 30, cy1, x1 + w_p - 20, cy1, color=INK, sw=1.5))
    f.append(text(x1 + w_p - 15, cy1 + 15, "H", size=12, bold=True, italic=True, color=INK))
    f.append(arrow(cx1, y0 + h_p - 20, cx1, y0 + 45, color=INK, sw=1.5))
    f.append(text(cx1 - 20, y0 + 45, "M", size=12, bold=True, italic=True, color=INK))

    pts_free = [
        (cx1 - 120, cy1 + 35), (cx1 - 40, cy1 + 35), (cx1 + 10, cy1 - 35), (cx1 + 120, cy1 - 35),
        (cx1 + 120, cy1 - 35), (cx1 + 40, cy1 - 35), (cx1 - 10, cy1 + 35), (cx1 - 120, cy1 + 35)
    ]
    d_free = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_free)
    f.append(path_svg(d_free, stroke="#2563eb", sw=2))
    f.append(text(cx1 + 15, cy1 - 45, "Перемикання вільного шару (H_c)", size=10, bold=True, color="#2563eb"))

    pts_pinned = [
        (cx1 + 60, cy1 - 35), (cx1 + 110, cy1 - 35), (cx1 + 140, cy1 - 90), (cx1 + 160, cy1 - 90),
        (cx1 + 160, cy1 - 90), (cx1 + 130, cy1 - 90), (cx1 + 90, cy1 - 35), (cx1 + 60, cy1 - 35)
    ]
    d_pin = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_pinned)
    f.append(path_svg(d_pin, stroke="#dc2626", sw=2, dash="4,2"))
    f.append(text(cx1 + 110, cy1 - 100, "Закріплений шар (H_ex)", size=10, bold=True, color="#dc2626"))

    # Right plot: R(H)
    x2 = 415
    f.append(rect(x2, y0, w_p, h_p, fill="#ffffff", stroke=BORDER, rx=6))
    f.append(text(x2 + w_p / 2, y0 + 22, "Залежність опору R(H)", size=13, bold=True, color=INK))

    cx2 = x2 + w_p / 2
    cy2 = y0 + h_p - 50

    # Axes R(H)
    f.append(arrow(x2 + 30, cy2, x2 + w_p - 20, cy2, color=INK, sw=1.5))
    f.append(text(x2 + w_p - 15, cy2 + 15, "H", size=12, bold=True, italic=True, color=INK))
    f.append(arrow(x2 + 50, cy2, x2 + 50, y0 + 45, color=INK, sw=1.5))
    f.append(text(x2 + 25, y0 + 45, "R", size=12, bold=True, italic=True, color=INK))

    y_rp = cy2 - 30
    y_rap = cy2 - 210

    pts_r = [
        (x2 + 50, y_rp), (cx2 - 50, y_rp), (cx2 - 10, y_rap), (cx2 + 90, y_rap), (cx2 + 130, y_rp), (x2 + w_p - 30, y_rp)
    ]
    d_r = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_r)
    f.append(path_svg(d_r, stroke="#059669", sw=3))

    f.append(path_svg(f"M {x2 + 40} {y_rp} L {x2 + w_p - 30} {y_rp}", stroke="#94a3b8", sw=1, dash="2,2"))
    f.append(text(x2 + 65, y_rp + 15, "R_P (паралельний)", size=10, bold=True, color="#15803d"))

    f.append(path_svg(f"M {x2 + 40} {y_rap} L {x2 + w_p - 30} {y_rap}", stroke="#94a3b8", sw=1, dash="2,2"))
    f.append(text(cx2 + 20, y_rap - 10, "R_AP (антипаралельний)", size=10, bold=True, color="#be123c"))

    f.append(arrow(cx2 + 40, y_rp, cx2 + 40, y_rap, color="#9333ea", sw=2))
    f.append(arrow(cx2 + 40, y_rap, cx2 + 40, y_rp, color="#9333ea", sw=2))
    f.append(text(cx2 + 48, (y_rp + y_rap) / 2 + 4, "ΔR = R_AP - R_P", size=11, bold=True, color="#9333ea"))

    f.append(text(W / 2, H - 15, "Максимум опору R_AP спостерігається у вікні полів між перемиканням вільного та закріпленого шарів", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig3-gmr-hysteresis-curve.svg'), W, H, "\n".join(f))

# ── Фігура 4: Густина станів N(E) спін-вгору та спін-вниз ──────────────────────
def fig_spin_dependent_density_of_states():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Густина електронних станів N(E) у феромагнітному 3d-металі", size=16, bold=True, color=INK))

    cx = 380
    cy = 230

    # Vertical energy axis E
    f.append(arrow(cx, H - 50, cx, 55, color=INK, sw=1.5))
    f.append(text(cx + 15, 60, "Енергія (E)", size=13, bold=True, italic=True, color=INK))

    # Horizontal axis N(E)
    f.append(arrow(70, cy, W - 70, cy, color=INK, sw=1.5))
    f.append(text(W - 60, cy + 18, "N(E)", size=13, bold=True, italic=True, color=INK))
    f.append(text(100, cy - 15, "← Спін-↓ (Minority)", size=12, bold=True, color="#dc2626"))
    f.append(text(W - 220, cy - 15, "Спін-↑ (Majority) →", size=12, bold=True, color="#15803d"))

    # Fermi level E_F
    y_ef = cy - 70
    f.append(path_svg(f"M 90 {y_ef} L {W - 90} {y_ef}", stroke="#9333ea", sw=2, dash="4,4"))
    f.append(text(cx + 15, y_ef - 8, "Рівень Фермі E_F", size=12, bold=True, color="#9333ea"))

    # Parabolic 4s band
    pts_4s_right = []
    pts_4s_left = []
    for i in range(80):
        e = i * 2.5
        y = cy + 100 - e
        x_val = math.sqrt(max(0, e)) * 12
        pts_4s_right.append((cx + x_val, y))
        pts_4s_left.append((cx - x_val, y))

    d_4s_r = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_4s_right)
    d_4s_l = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_4s_left)
    f.append(path_svg(d_4s_r, stroke="#64748b", sw=1.5, dash="3,2"))
    f.append(path_svg(d_4s_l, stroke="#64748b", sw=1.5, dash="3,2"))
    f.append(text(cx + 170, cy + 80, "4s-зона (провідність)", size=11, bold=True, color="#64748b"))

    # Exchange split 3d bands
    pts_3d_up = []
    y_3d_up_bot = cy + 80
    for i in range(100):
        e = i * 1.4
        y = y_3d_up_bot - e
        x_val = math.exp(-((e - 60)**2) / 800.0) * 180.0
        pts_3d_up.append((cx + x_val, y))

    d_3d_up = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_3d_up)
    f.append(path_svg(d_3d_up, stroke="#15803d", sw=2.5))
    f.append(text(cx + 120, y_ef + 45, "3d-зона ↑ (заповнена)", size=11, bold=True, color="#15803d"))

    pts_3d_dn = []
    y_3d_dn_bot = cy + 40
    for i in range(100):
        e = i * 1.4
        y = y_3d_dn_bot - e
        x_val = math.exp(-((e - 60)**2) / 800.0) * 180.0
        pts_3d_dn.append((cx - x_val, y))

    d_3d_dn = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_3d_dn)
    f.append(path_svg(d_3d_dn, stroke="#dc2626", sw=2.5))
    f.append(text(cx - 240, y_ef - 10, "3d-зона ↓ (перетинає E_F!)", size=11, bold=True, color="#dc2626"))

    f.append(circle(cx + 35, y_ef, 6, fill="#15803d", stroke="none"))
    f.append(text(cx + 45, y_ef + 15, "N_↑(E_F) мала", size=11, bold=True, color="#15803d"))

    f.append(circle(cx - 165, y_ef, 6, fill="#dc2626", stroke="none"))
    f.append(text(cx - 250, y_ef + 15, "N_↓(E_F) висока", size=11, bold=True, color="#dc2626"))

    f.append(text(W / 2, H - 15, "Обмінне розщеплення зон призводить до високої густини станів N_↓(E_F) та сильного розсіювання спінів-вниз", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fig4-spin-dependent-density-of-states.svg'), W, H, "\n".join(f))

def main():
    fig_mott_two_channel()
    fig_gmr_multilayer_vs_spin_valve()
    fig_gmr_hysteresis_curve()
    fig_spin_dependent_density_of_states()
    print("All GMR figures successfully generated in ./img/")

if __name__ == '__main__':
    main()
