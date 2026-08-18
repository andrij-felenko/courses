# -*- coding: utf-8 -*-
"""Фігури до теми «Спіновий ефект Зеєбека (SSE)».
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

def polygon(pts, fill=LINE, stroke="none", sw=1.0):
    pts_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts])
    s_attr = f' stroke="{stroke}" stroke-width="{sw:.1f}"' if stroke != "none" else ''
    return f'<polygon points="{pts_str}" fill="{fill}"{s_attr}/>'

# ── Фігура 1: Геометрія LSSE та TSSE ──────────────────────────────────────────
def fig_lsse_vs_tsse_geometry():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Геометрія експериментального спостереження SSE", size=16, bold=True, color=INK))

    # --- Ліва панель: LSSE ---
    x_l = 25
    y_p = 50
    pw, ph = 350, 340
    f.append(rect(x_l, y_p, pw, ph, fill="#fafafa", stroke=BORDER, rx=6))
    f.append(text(x_l + pw / 2, y_p + 25, "Поздовжня конфігурація (LSSE)", size=14, bold=True, color=INK))
    
    # YIG block
    f.append(rect(x_l + 50, y_p + 170, 250, 90, fill="#e2e8f0", stroke="#475569", rx=3))
    f.append(text(x_l + 175, y_p + 215, "Магнітний діелектрик YIG", size=13, bold=True, color="#334155"))
    
    # Pt layer on top
    f.append(rect(x_l + 50, y_p + 140, 250, 30, fill="#fef08a", stroke="#ca8a04", rx=2))
    f.append(text(x_l + 175, y_p + 160, "Важкий метал (Pt)", size=12, bold=True, color="#854d0e"))

    # Temperature gradient (vertical arrow)
    f.append(path_svg(f"M {x_l + 30} {y_p + 270} L {x_l + 30} {y_p + 110}", stroke=POS, sw=2.5))
    f.append(polygon([(x_l + 30, y_p + 100), (x_l + 25, y_p + 112), (x_l + 35, y_p + 112)], fill=POS))
    f.append(text(x_l + 30, y_p + 290, "∇T (гаряче → холодне)", size=11, bold=True, color=POS))

    # Magnetization arrow (in-plane x)
    f.append(path_svg(f"M {x_l + 70} {y_p + 245} L {x_l + 140} {y_p + 245}", stroke=NEG, sw=2))
    f.append(polygon([(x_l + 148, y_p + 245), (x_l + 138, y_p + 241), (x_l + 138, y_p + 249)], fill=NEG))
    f.append(text(x_l + 110, y_p + 238, "M (намагніченість)", size=11, bold=True, color=NEG))

    # Spin current arrow (vertical z into Pt)
    f.append(path_svg(f"M {x_l + 200} {y_p + 185} L {x_l + 200} {y_p + 145}", stroke=FIELD, sw=2.5))
    f.append(polygon([(x_l + 200, y_p + 137), (x_l + 195, y_p + 147), (x_l + 205, y_p + 147)], fill=FIELD))
    f.append(text(x_l + 215, y_p + 195, "J_s (спіновий струм)", size=11, bold=True, color=FIELD))

    # ISHE voltage contacts
    f.append(circle(x_l + 50, y_p + 155, 4, fill=POS, stroke=INK))
    f.append(circle(x_l + 300, y_p + 155, 4, fill=NEG, stroke=INK))
    f.append(path_svg(f"M {x_l + 50} {y_p + 155} Q {x_l + 175} {y_p + 95} {x_l + 300} {y_p + 155}", stroke="#7c3aed", sw=1.5, dash="3,3"))
    f.append(rect(x_l + 140, y_p + 70, 70, 24, fill="#f3e8ff", stroke="#7c3aed", rx=3))
    f.append(text(x_l + 175, y_p + 86, "V_ISHE", size=12, bold=True, color="#6b21a8"))

    # Notes
    f.append(text(x_l + pw / 2, y_p + 315, "∇T ⊥ межі, M ⊥ J_s → чистий магнонний сигнал", size=11, color=MUTED))

    # --- Права панель: TSSE ---
    x_r = 405
    f.append(rect(x_r, y_p, pw, ph, fill="#fafafa", stroke=BORDER, rx=6))
    f.append(text(x_r + pw / 2, y_p + 25, "Поперечна конфігурація (TSSE)", size=14, bold=True, color=INK))

    # YIG slab
    f.append(rect(x_r + 50, y_p + 170, 250, 90, fill="#e2e8f0", stroke="#475569", rx=3))
    f.append(text(x_r + 175, y_p + 215, "Магнітний підкладковий шар", size=13, bold=True, color="#334155"))

    # Pt strip in middle
    f.append(rect(x_r + 140, y_p + 140, 70, 30, fill="#fef08a", stroke="#ca8a04", rx=2))
    f.append(text(x_r + 175, y_p + 160, "Pt смужка", size=11, bold=True, color="#854d0e"))

    # Temperature gradient (horizontal arrow)
    f.append(path_svg(f"M {x_r + 40} {y_p + 280} L {x_r + 300} {y_p + 280}", stroke=POS, sw=2.5))
    f.append(polygon([(x_r + 310, y_p + 280), (x_r + 298, y_p + 275), (x_r + 298, y_p + 285)], fill=POS))
    f.append(text(x_r + 175, y_p + 298, "∇T вздовж площини зразка", size=11, bold=True, color=POS))

    # Magnetization arrow (transverse y)
    f.append(path_svg(f"M {x_r + 65} {y_p + 200} L {x_r + 65} {y_p + 240}", stroke=NEG, sw=2))
    f.append(polygon([(x_r + 65, y_p + 248), (x_r + 61, y_p + 238), (x_r + 69, y_p + 238)], fill=NEG))
    f.append(text(x_r + 95, y_p + 225, "M", size=12, bold=True, color=NEG))

    # ISHE contacts on Pt strip
    f.append(circle(x_r + 145, y_p + 155, 4, fill=POS, stroke=INK))
    f.append(circle(x_r + 205, y_p + 155, 4, fill=NEG, stroke=INK))
    f.append(path_svg(f"M {x_r + 145} {y_p + 155} Q {x_r + 175} {y_p + 105} {x_r + 205} {y_p + 155}", stroke="#7c3aed", sw=1.5, dash="3,3"))
    f.append(rect(x_r + 140, y_p + 80, 70, 24, fill="#f3e8ff", stroke="#7c3aed", rx=3))
    f.append(text(x_r + 175, y_p + 96, "V_ISHE", size=12, bold=True, color="#6b21a8"))

    # Notes
    f.append(text(x_r + pw / 2, y_p + 315, "∇T ∥ площині; чутливий до артефактів PNE", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "lsse-vs-tsse-geometry.svg"), W, H, *f)

# ── Фігура 2: Двотемпературна модель ──────────────────────────────────────────
def fig_magnon_phonon_two_temp():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 25, "Двотемпературна модель фононів і магнонів у SSE", size=16, bold=True, color=INK))

    # Graph area
    gx0, gy0 = 80, 60
    gw, gh = 620, 250

    # Axes
    f.append(path_svg(f"M {gx0} {gy0 + gh} L {gx0 + gw + 20} {gy0 + gh}", stroke=INK, sw=2))
    f.append(polygon([(gx0 + gw + 28, gy0 + gh), (gx0 + gw + 18, gy0 + gh - 4), (gx0 + gw + 18, gy0 + gh + 4)], fill=INK))
    f.append(text(gx0 + gw + 15, gy0 + gh + 22, "Координата z (товщина YIG)", size=12, bold=True, color=INK))

    f.append(path_svg(f"M {gx0} {gy0 + gh} L {gx0} {gy0 - 20}", stroke=INK, sw=2))
    f.append(polygon([(gx0, gy0 - 28), (gx0 - 4, gy0 - 18), (gx0 + 4, gy0 - 18)], fill=INK))
    f.append(text(gx0 - 10, gy0 - 15, "Температура T", size=12, bold=True, color=INK, anchor="end"))

    # YIG / Pt interface at z = d
    int_x = gx0 + 480
    f.append(path_svg(f"M {int_x} {gy0} L {int_x} {gy0 + gh}", stroke="#ca8a04", sw=2, dash="4,4"))
    f.append(rect(int_x, gy0, 140, gh, fill="#fef9c3", stroke="none"))
    f.append(text(int_x + 70, gy0 + 30, "Межа YIG / Pt", size=12, bold=True, color="#854d0e"))

    # Phonon linear gradient line T_p(z)
    tp_start_y = gy0 + 50
    tp_end_y = gy0 + gh - 40
    f.append(path_svg(f"M {gx0} {tp_start_y} L {int_x} {tp_end_y}", stroke=POS, sw=2.5))
    f.append(text(gx0 + 120, tp_start_y + 15, "T_p(z) — температура фононів", size=12, bold=True, color=POS))

    # Magnon non-equilibrium profile T_m(z)
    path_tm = []
    steps = 50
    for i in range(steps + 1):
        z_frac = i / steps
        zx = gx0 + z_frac * (int_x - gx0)
        tp_val = tp_start_y + z_frac * (tp_end_y - tp_start_y)
        dev = 25 * math.exp(-z_frac * 4) - 30 * math.exp(-(1 - z_frac) * 5)
        tm_y = tp_val + dev
        path_tm.append(f"{'M' if i == 0 else 'L'} {zx:.1f} {tm_y:.1f}")
    
    f.append(path_svg(" ".join(path_tm), stroke=NEG, sw=2.5))
    f.append(text(gx0 + 120, tp_start_y + 55, "T_m(z) — температура магнонів", size=12, bold=True, color=NEG))

    # Highlight thermal non-equilibrium gap at interface
    gap_y1 = tp_end_y
    gap_y2 = tp_end_y - 30
    f.append(path_svg(f"M {int_x - 5} {gap_y1} L {int_x - 5} {gap_y2}", stroke="#7c3aed", sw=2))
    f.append(circle(int_x - 5, gap_y1, 3, fill="#7c3aed"))
    f.append(circle(int_x - 5, gap_y2, 3, fill="#7c3aed"))
    f.append(text(int_x - 20, gap_y2 - 10, "ΔT_mp = T_m - T_p", size=11, bold=True, color="#6b21a8", anchor="end"))

    # Magnon-phonon relaxation length indicator
    f.append(path_svg(f"M {int_x - 120} {gy0 + gh - 15} L {int_x} {gy0 + gh - 15}", stroke=FIELD, sw=2))
    f.append(polygon([(int_x - 120, gy0 + gh - 15), (int_x - 114, gy0 + gh - 19), (int_x - 114, gy0 + gh - 11)], fill=FIELD))
    f.append(polygon([(int_x, gy0 + gh - 15), (int_x - 6, gy0 + gh - 19), (int_x - 6, gy0 + gh - 11)], fill=FIELD))
    f.append(text(int_x - 60, gy0 + gh - 25, "λ_mp (релаксація)", size=11, bold=True, color=FIELD))

    # Bottom caption
    f.append(text(W / 2, gy0 + gh + 40, "Різниця між T_m та T_p на межі з металом визначає силу теплової спінової інжекції", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "magnon-phonon-two-temp.svg"), W, H, *f)

# ── Фігура 3: Механізм ISHE ──────────────────────────────────────────────────
def fig_ishe_conversion_mechanism():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 25, "Обернений спіновий ефект Холла (ISHE) у важкому металі", size=16, bold=True, color=INK))

    # Heavy metal box
    bx0, by0 = 60, 60
    bw, bh = 640, 240
    f.append(rect(bx0, by0, bw, bh, fill="#f8fafc", stroke="#94a3b8", rx=8))
    f.append(text(bx0 + 20, by0 + 25, "Плівка важкого металу (Pt / Ta / W)", size=13, bold=True, color="#334155"))

    # Injected Spin Current arrow (vertical J_s)
    f.append(path_svg(f"M {bx0 + 90} {by0 + bh - 20} L {bx0 + 90} {by0 + 80}", stroke=FIELD, sw=3))
    f.append(polygon([(bx0 + 90, by0 + 68), (bx0 + 84, by0 + 82), (bx0 + 96, by0 + 82)], fill=FIELD))
    f.append(text(bx0 + 90, by0 + bh - 5, "Вхідний спіновий струм J_s", size=11, bold=True, color=FIELD))

    # Spin orientation sigma (along x)
    f.append(path_svg(f"M {bx0 + 150} {by0 + 130} L {bx0 + 220} {by0 + 130}", stroke=NEG, sw=2))
    f.append(polygon([(bx0 + 228, by0 + 130), (bx0 + 218, by0 + 126), (bx0 + 218, by0 + 134)], fill=NEG))
    f.append(text(bx0 + 185, by0 + 115, "Спінова поляризація σ", size=11, bold=True, color=NEG))

    # Center: Scattering diagram (Spin-orbit interaction)
    cx, cy = bx0 + 340, by0 + 130
    f.append(circle(cx, cy, 26, fill="#e2e8f0", stroke="#475569"))
    f.append(text(cx, cy + 5, "Pt атом", size=11, bold=True, color="#1e293b"))
    f.append(text(cx, cy + 42, "Спін-орбітальний центр", size=10, color=MUTED))

    # Trajectory of spin-up electron (deflects right/top)
    f.append(path_svg(f"M {cx - 90} {cy + 40} Q {cx - 30} {cy + 30} {cx + 40} {cy - 50}", stroke=POS, sw=2))
    f.append(polygon([(cx + 46, cy - 56), (cx + 34, cy - 50), (cx + 42, cy - 40)], fill=POS))
    f.append(circle(cx - 70, cy + 37, 6, fill=POS))
    f.append(text(cx - 70, cy + 37, "↑", size=10, bold=True, color=BG))
    f.append(text(cx + 65, cy - 55, "Спін-вгору носії (+e)", size=11, color=POS, anchor="start"))

    # Trajectory of spin-down electron (deflects left/bottom)
    f.append(path_svg(f"M {cx - 90} {cy - 40} Q {cx - 30} {cy - 30} {cx + 40} {cy + 50}", stroke=NEG, sw=2))
    f.append(polygon([(cx + 46, cy + 56), (cx + 42, cy + 40), (cx + 34, cy + 50)], fill=NEG))
    f.append(circle(cx - 70, cy - 37, 6, fill=NEG))
    f.append(text(cx - 70, cy - 37, "↓", size=10, bold=True, color=BG))
    f.append(text(cx + 65, cy + 55, "Спін-вниз носії (-e)", size=11, color=NEG, anchor="start"))

    # Resulting transverse charge current / electric field (E_ISHE along y)
    f.append(path_svg(f"M {bx0 + 540} {by0 + 190} L {bx0 + 540} {by0 + 70}", stroke="#7c3aed", sw=3))
    f.append(polygon([(bx0 + 540, by0 + 58), (bx0 + 534, by0 + 72), (bx0 + 546, by0 + 72)], fill="#7c3aed"))
    f.append(text(bx0 + 540, by0 + 42, "Поперечний струм J_c", size=12, bold=True, color="#6b21a8"))

    # Vector cross product equation box
    f.append(rect(bx0 + 160, by0 + bh - 40, 360, 26, fill="#f1f5f9", stroke=BORDER, rx=4))
    f.append(text(bx0 + 340, by0 + bh - 23, "E_ISHE = (θ_SH / σ) · (2e / ℏ) · (J_s × σ)", size=12, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "ishe-conversion-mechanism.svg"), W, H, *f)

# ── Фігура 4: Спіновий транспорт через межу YIG/Pt ────────────────────────────
def fig_yig_pt_interface_transfer():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 25, "Мікроскопічна передача спіну на фазовій межі YIG/Pt", size=16, bold=True, color=INK))

    # YIG lower region
    f.append(rect(50, 200, 680, 150, fill="#f1f5f9", stroke="#64748b", rx=4))
    f.append(text(390, 335, "Магнітний діелектрик YIG (локалізовані спіни Fe³⁺)", size=12, bold=True, color="#334155"))

    # Pt upper region
    f.append(rect(50, 50, 680, 150, fill="#fefce8", stroke="#eab308", rx=4))
    f.append(text(390, 75, "Метал Pt (вільні електрони провідності)", size=12, bold=True, color="#854d0e"))

    # Interface line
    f.append(path_svg("M 50 200 L 730 200", stroke="#dc2626", sw=2.5, dash="6,4"))
    f.append(text(390, 192, "Межа розділу (спінова провідність g_↑↓)", size=12, bold=True, color="#991b1b"))

    # YIG spins (precessing arrows)
    spins_x = [120, 200, 280, 520, 600, 680]
    for sx in spins_x:
        f.append(circle(sx, 260, 14, fill="#cbd5e1", stroke="#475569"))
        f.append(text(sx, 264, "Fe", size=10, bold=True, color="#1e293b"))
        # Precession spin arrow
        f.append(path_svg(f"M {sx} 260 L {sx + 10} 225", stroke=NEG, sw=2))
        f.append(polygon([(sx + 13, 218), (sx + 3, 225), (sx + 12, 230)], fill=NEG))
        # Wave curve representing magnon
        f.append(path_svg(f"M {sx - 18} 285 Q {sx} 275 {sx + 18} 285", stroke=NEG, sw=1.5))

    f.append(text(200, 305, "Магнонний потік (спінові хвилі)", size=11, bold=True, color=NEG))

    # Interfacial Exchange coupling J_ex arrows across interface
    for ex in [160, 240, 560, 640]:
        f.append(path_svg(f"M {ex} 230 L {ex} 170", stroke="#7c3aed", sw=1.5, dash="3,3"))
        f.append(polygon([(ex, 162), (ex - 4, 172), (ex + 4, 172)], fill="#7c3aed"))
        f.append(polygon([(ex, 238), (ex - 4, 228), (ex + 4, 228)], fill="#7c3aed"))

    f.append(text(390, 160, "s-d обмінна взаємодія J_ex (спіновий обмін)", size=11, bold=True, color="#6b21a8"))

    # Pt conduction electrons (spin accumulation)
    elec_x = [160, 240, 560, 640]
    for ex in elec_x:
        f.append(circle(ex, 130, 12, fill="#fef08a", stroke="#ca8a04"))
        f.append(text(ex, 134, "e⁻", size=10, bold=True, color="#854d0e"))
        # Injected spin orientation arrow
        f.append(path_svg(f"M {ex} 130 L {ex + 12} 105", stroke=FIELD, sw=2))
        f.append(polygon([(ex + 15, 99), (ex + 5, 105), (ex + 14, 111)], fill=FIELD))

    # Spin accumulation decay profile in Pt
    f.append(path_svg("M 460 200 C 460 140 480 110 500 100", stroke=FIELD, sw=2))
    f.append(text(340, 105, "Накопичення спіну μ_s(z) ∝ exp(-z / λ_sd)", size=11, bold=True, color=FIELD))

    # Bottom caption
    f.append(text(W / 2, 380, "Тепловий магнонний потік у YIG передає кутовий момент електронам у Pt через обмінну взаємодію", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "yig-pt-interface-transfer.svg"), W, H, *f)

if __name__ == "__main__":
    fig_lsse_vs_tsse_geometry()
    fig_magnon_phonon_two_temp()
    fig_ishe_conversion_mechanism()
    fig_yig_pt_interface_transfer()
    print("Всі 4 фігури успішно згенеровано у ./img/")
