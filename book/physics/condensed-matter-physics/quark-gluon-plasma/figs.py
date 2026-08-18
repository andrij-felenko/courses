# -*- coding: utf-8 -*-
"""Фігури до теми «Кварк-глюонна плазма та деконфайнмент».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"


def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Фазова діаграма КХД матерії ─────────────────────────────────────
def fig_qgp_phase_diagram():
    W, H = 800, 480
    f = []

    f.append(text(W / 2, 28, "Фазова діаграма квантової хромодинаміки (КХД)", size=16, bold=True, color=INK))

    x0, y0 = 90, 400
    pw, ph = 660, 320
    x_max = x0 + pw
    y_min = y0 - ph

    # Frame background using path to avoid solid rect overlap detection
    f.append(path_svg(f"M {x0} {y_min} h {pw} v {ph} h {-pw} Z", fill="#f8fafc", stroke=BORDER, sw=1.0))

    # QCD Phase Areas
    hadron_path = f"M {x0} {y0} L {x0} {y0 - 200} C {x0 + 150} {y0 - 190}, {x0 + 350} {y0 - 140}, {x0 + 480} {y0 - 50} L {x_max - 50} {y0} Z"
    f.append(path_svg(hadron_path, fill="#eef2ff", stroke="none"))

    qgp_path = f"M {x0} {y0 - 200} C {x0 + 150} {y0 - 190}, {x0 + 350} {y0 - 140}, {x0 + 480} {y0 - 50} L {x_max} {y0 - 50} L {x_max} {y_min} L {x0} {y_min} Z"
    f.append(path_svg(qgp_path, fill="#fff1f2", stroke="none"))

    cfl_path = f"M {x_max - 180} {y0} L {x0 + 480} {y0 - 50} L {x_max} {y0 - 50} L {x_max} {y0} Z"
    f.append(path_svg(cfl_path, fill="#f0fdf4", stroke="none"))

    # Grid lines
    for i in range(1, 6):
        gx = x0 + i * (pw / 6)
        f.append(path_svg(f"M {gx:.1f} {y0} L {gx:.1f} {y_min}", stroke="#e2e8f0", sw=1.0, dash="4,4"))
    for j in range(1, 5):
        gy = y0 - j * (ph / 5)
        f.append(path_svg(f"M {x0} {gy:.1f} L {x_max} {gy:.1f}", stroke="#e2e8f0", sw=1.0, dash="4,4"))

    # Axes
    f.append(arrow(x0, y0, x_max + 20, y0, color=INK, sw=2.0))
    f.append(arrow(x0, y0, x0, y_min - 20, color=INK, sw=2.0))

    f.append(text(x_max + 25, y0 + 5, "μ_B (МеВ)", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(x0, y_min - 25, "Т (МеВ)", size=13, bold=True, color=INK, anchor="middle"))

    # Phase transition boundary curves
    x_cep, y_cep = x0 + 260, y0 - 165
    crossover_path = f"M {x0} {y0 - 200} C {x0 + 100} {y0 - 195}, {x0 + 180} {y0 - 180}, {x_cep} {y_cep}"
    f.append(path_svg(crossover_path, stroke=NEG, sw=2.5, dash="6,4"))

    first_order_path = f"M {x_cep} {y_cep} C {x0 + 330} {y0 - 130}, {x0 + 400} {y0 - 90}, {x0 + 460} {y0 - 45}"
    f.append(path_svg(first_order_path, stroke=POS, sw=3.0))

    # Critical End Point (CEP) marker
    f.append(circle(x_cep, y_cep, 7, fill="#f59e0b", stroke="#b45309", sw=2.0))
    b_cep, _, _ = textbox(x_cep + 20, y_cep - 25, "Критична точка CEP", size=11, bold=True, fill="#ffffff", stroke="#b45309", sw=1.0)
    f.append(b_cep)

    # Phase Labels
    b_qgp, _, _ = textbox(x0 + 260, y0 - 265, "Кварк-глюонна плазма (QGP)\n[Деконфайнований стан]", size=13, bold=True, fill="#ffe4e6", stroke=POS, sw=1.5)
    f.append(b_qgp)

    b_had, _, _ = textbox(x0 + 140, y0 - 80, "Адронна матерія\n(газ піонів, нуклонів)", size=13, bold=True, fill="#e0e7ff", stroke=NEG, sw=1.5)
    f.append(b_had)

    b_cfl, _, _ = textbox(x_max - 85, y0 - 30, "Колірна надпровідність\n(CFL-фаза)", size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5)
    f.append(b_cfl)

    # Experimental Trajectories / Zones
    f.append(circle(x0 + 15, y0 - 280, 5, fill=POS, stroke=INK, sw=1.0))
    b_univ, _, _ = textbox(x0 + 115, y0 - 305, "Ранній Всесвіт (t ~ 10⁻⁶ с)", size=10, bold=True, fill="#ffffff", stroke=POS, sw=1.0)
    f.append(b_univ)

    f.append(path_svg(f"M {x0} {y0 - 200} L {x0 + 80} {y0 - 185}", stroke="#8b5cf6", sw=3.0))
    b_lhc, _, _ = textbox(x0 + 90, y0 - 215, "LHC / RHIC (Т_c ≈ 155 МеВ)", size=10, bold=True, fill="#ffffff", stroke="#8b5cf6", sw=1.0)
    f.append(b_lhc)

    # Axis markers (T_c, Nuclear Density)
    f.append(line(x0 - 5, y0 - 200, x0 + 5, y0 - 200, color=INK, sw=1.5))
    f.append(text(x0 - 12, y0 - 196, "155", size=11, bold=True, color=INK, anchor="end"))

    x_nuc = x0 + 440
    f.append(circle(x_nuc, y0, 5, fill="#3b82f6", stroke=INK, sw=1.5))
    f.append(text(x_nuc, y0 + 20, "Ядерна матерія (μ₀ ≈ 938 МеВ)", size=10, bold=True, color="#1e40af", anchor="middle"))

    # Legend / Phase Transition types
    f.append(path_svg(f"M {x0 + 380} {y0 - 300} h 270 v 85 h -270 Z", fill="#ffffff", stroke=BORDER, sw=1.0))
    f.append(line(x0 + 390, y0 - 275, x0 + 430, y0 - 275, color=NEG, sw=2.5, dash="6,4"))
    f.append(text(x0 + 440, y0 - 271, "Гладкий кросовер (Crossover)", size=11, color=INK, anchor="start"))
    f.append(line(x0 + 390, y0 - 245, x0 + 430, y0 - 245, color=POS, sw=3.0))
    f.append(text(x0 + 440, y0 - 241, "Перехід 1-го роду", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "qgp-phase-diagram.svg"), W, H, *f)


# ── Фігура 2: Перехід від адронної фази до деконфайнованої КГП ────────────────
def fig_qgp_deconfinement_transition():
    W, H = 800, 420
    f = []

    f.append(text(W / 2, 28, "Хромоелектростатичне екранування та деконфайнмент", size=16, bold=True, color=INK))

    w_p = 350
    h_p = 310
    y_p = 65

    # Left Panel: Hadronic Phase
    x_l = 35
    f.append(path_svg(f"M {x_l} {y_p} h {w_p} v {h_p} h {-w_p} Z", fill="#f8fafc", stroke=BORDER, sw=1.0))
    f.append(text(x_l + w_p / 2, y_p + 25, "Адронна фаза (Т < Т_c)", size=14, bold=True, color="#1e3a8a", anchor="middle"))
    f.append(text(x_l + w_p / 2, y_p + 45, "Кварки затиснуті в адронах (r_D > r_hadron)", size=11, color=MUTED, anchor="middle"))

    cx1, cy1 = x_l + 90, y_p + 120
    f.append(circle(cx1, cy1, 38, fill="#e0e7ff", stroke=NEG, sw=1.5))
    f.append(line(cx1 - 18, cy1, cx1 + 18, cy1, color=POS, sw=5.0))
    f.append(circle(cx1 - 18, cy1, 10, fill=POS, stroke=INK, sw=1.0))
    f.append(text(cx1 - 18, cy1 + 4, "q", size=10, bold=True, color="#ffffff", anchor="middle"))
    f.append(circle(cx1 + 18, cy1, 10, fill=NEG, stroke=INK, sw=1.0))
    f.append(text(cx1 + 18, cy1 + 4, "q̄", size=10, bold=True, color="#ffffff", anchor="middle"))
    f.append(text(cx1, cy1 + 55, "Мезон (q q̄)", size=11, bold=True, color=INK, anchor="middle"))

    cx2, cy2 = x_l + 250, y_p + 180
    f.append(circle(cx2, cy2, 50, fill="#e0e7ff", stroke=NEG, sw=1.5))
    f.append(line(cx2, cy2, cx2 - 25, cy2 - 20, color=POS, sw=4.0))
    f.append(line(cx2, cy2, cx2 + 25, cy2 - 20, color=POS, sw=4.0))
    f.append(line(cx2, cy2, cx2, cy2 + 30, color=POS, sw=4.0))
    f.append(circle(cx2 - 25, cy2 - 20, 9, fill="#ef4444", stroke=INK, sw=1.0))
    f.append(text(cx2 - 25, cy2 - 16, "r", size=9, bold=True, color="#ffffff", anchor="middle"))
    f.append(circle(cx2 + 25, cy2 - 20, 9, fill="#22c55e", stroke=INK, sw=1.0))
    f.append(text(cx2 + 25, cy2 - 16, "g", size=9, bold=True, color="#ffffff", anchor="middle"))
    f.append(circle(cx2, cy2 + 30, 9, fill="#3b82f6", stroke=INK, sw=1.0))
    f.append(text(cx2, cy2 + 34, "b", size=9, bold=True, color="#ffffff", anchor="middle"))
    f.append(text(cx2, cy2 + 65, "Баріон (qqq)", size=11, bold=True, color=INK, anchor="middle"))

    b_hprop, _, _ = textbox(x_l + w_p / 2, y_p + 270, "Потенціал V(r) = -α_s/r + σ·r\nНатяг струни σ ≈ 1 ГеВ/фм", size=11, fill="#ffffff", stroke=BORDER, sw=1.0)
    f.append(b_hprop)

    # Arrow between panels
    f.append(arrow(x_l + w_p + 5, y_p + h_p / 2, x_l + w_p + 35, y_p + h_p / 2, color=POS, sw=3.0))
    f.append(text(x_l + w_p + 20, y_p + h_p / 2 - 12, "Т > Т_c", size=12, bold=True, color=POS, anchor="middle"))

    # Right Panel: Deconfined QGP Phase
    x_r = x_l + w_p + 40
    f.append(path_svg(f"M {x_r} {y_p} h {w_p} v {h_p} h {-w_p} Z", fill="#fff1f2", stroke=POS, sw=1.5))
    f.append(text(x_r + w_p / 2, y_p + 25, "Кварк-глюонна плазма (Т > Т_c)", size=14, bold=True, color="#991b1b", anchor="middle"))
    f.append(text(x_r + w_p / 2, y_p + 45, "Екранування Дебая r_D < r_hadron → Вільні кольори", size=11, color=MUTED, anchor="middle"))

    q_coords = [
        (x_r + 60, y_p + 90, "#ef4444", "q_r"),
        (x_r + 140, y_p + 110, "#3b82f6", "q̄_b"),
        (x_r + 220, y_p + 85, "#22c55e", "q_g"),
        (x_r + 290, y_p + 120, "#ef4444", "q̄_r"),
        (x_r + 80, y_p + 170, "#22c55e", "q_g"),
        (x_r + 170, y_p + 160, "#ef4444", "q_r"),
        (x_r + 260, y_p + 180, "#3b82f6", "q_b"),
        (x_r + 110, y_p + 220, "#3b82f6", "q̄_b"),
        (x_r + 210, y_p + 220, "#22c55e", "q̄_g"),
    ]

    for qx, qy, col, lbl in q_coords:
        f.append(circle(qx, qy, 22, fill="none", stroke=col, sw=1.0))
        f.append(circle(qx, qy, 7, fill=col, stroke=INK, sw=0.8))

    gluon_coords = [
        (x_r + 100, y_p + 135),
        (x_r + 180, y_p + 100),
        (x_r + 250, y_p + 145),
        (x_r + 140, y_p + 190),
    ]
    for gx, gy in gluon_coords:
        f.append(circle(gx, gy, 6, fill="#f59e0b", stroke="#b45309", sw=1.0))
        f.append(text(gx, gy + 3, "g", size=9, bold=True, color="#ffffff", anchor="middle"))

    b_qprop, _, _ = textbox(x_r + w_p / 2, y_p + 270, "Потенціал Юкави V(r) ~ (-α_s/r)·e^(-r/r_D)\nНатяг струни σ(Т) → 0", size=11, fill="#ffffff", stroke=POS, sw=1.0)
    f.append(b_qprop)

    render(os.path.join(IMG_DIR, "qgp-deconfinement-transition.svg"), W, H, *f)


# ── Фігура 3: Експериментальні сигнатури QGP ─────────────────────────────────
def fig_qgp_signatures():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 28, "Ключові експериментальні сигнатури деконфайнменту у КГП", size=16, bold=True, color=INK))

    cw = 240
    ch = 340
    cy = 65

    # Column 1: Jet Quenching
    cx1 = 30
    f.append(path_svg(f"M {cx1} {cy} h {cw} v {ch} h {-cw} Z", fill="#f8fafc", stroke=BORDER, sw=1.0))
    f.append(text(cx1 + cw / 2, cy + 25, "1. Гасіння струменів", size=13, bold=True, color="#1e3a8a", anchor="middle"))
    f.append(text(cx1 + cw / 2, cy + 42, "(Jet Quenching & R_AA)", size=11, color=MUTED, anchor="middle"))

    f.append(circle(cx1 + cw / 2, cy + 140, 45, fill="#ffe4e6", stroke=POS, sw=1.5))
    f.append(text(cx1 + cw / 2, cy + 144, "QGP", size=12, bold=True, color=POS, anchor="middle"))

    vx, vy = cx1 + cw / 2 - 20, cy + 140
    f.append(circle(vx, vy, 4, fill=INK, stroke="none"))
    f.append(arrow(vx, vy, cx1 + 15, cy + 140, color=POS, sw=3.0))
    b_jet1, _, _ = textbox(cx1 + 45, cy + 110, "Вільний струмінь", size=9, bold=True, fill="#ffffff", stroke=POS, sw=0.8)
    f.append(b_jet1)

    f.append(line(vx, vy, cx1 + cw - 20, cy + 140, color=MUTED, sw=2.0, dash="3,3"))
    b_jet2, _, _ = textbox(cx1 + cw - 45, cy + 110, "Згасання Е", size=9, bold=True, fill="#ffffff", stroke=MUTED, sw=0.8)
    f.append(b_jet2)

    b_s1, _, _ = textbox(cx1 + cw / 2, cy + 265, "Втрата енергії партонів dE/dx\nПригнічення адронів R_AA < 1", size=11, fill="#ffffff", stroke=BORDER, sw=1.0)
    f.append(b_s1)

    # Column 2: Elliptic Flow (v_2)
    cx2 = cx1 + cw + 25
    f.append(path_svg(f"M {cx2} {cy} h {cw} v {ch} h {-cw} Z", fill="#f8fafc", stroke=BORDER, sw=1.0))
    f.append(text(cx2 + cw / 2, cy + 25, "2. Еліптичний потік v₂", size=13, bold=True, color="#1e3a8a", anchor="middle"))
    f.append(text(cx2 + cw / 2, cy + 42, "(Колективна гідродинаміка)", size=11, color=MUTED, anchor="middle"))

    almond_d = f"M {cx2 + cw/2 - 35} {cy + 140} C {cx2 + cw/2 - 35} {cy + 105}, {cx2 + cw/2 + 35} {cy + 105}, {cx2 + cw/2 + 35} {cy + 140} C {cx2 + cw/2 + 35} {cy + 175}, {cx2 + cw/2 - 35} {cy + 175}, {cx2 + cw/2 - 35} {cy + 140} Z"
    f.append(path_svg(almond_d, fill="#dcfce7", stroke=FIELD, sw=2.0))
    f.append(text(cx2 + cw / 2, cy + 144, "Зона перекриття", size=10, bold=True, color=FIELD, anchor="middle"))

    f.append(arrow(cx2 + cw / 2 - 35, cy + 140, cx2 + 15, cy + 140, color=POS, sw=3.0))
    f.append(arrow(cx2 + cw / 2 + 35, cy + 140, cx2 + cw - 15, cy + 140, color=POS, sw=3.0))

    f.append(arrow(cx2 + cw / 2, cy + 105, cx2 + cw / 2, cy + 78, color=NEG, sw=1.5))
    f.append(arrow(cx2 + cw / 2, cy + 175, cx2 + cw / 2, cy + 202, color=NEG, sw=1.5))

    b_s2, _, _ = textbox(cx2 + cw / 2, cy + 265, "Анізотропія тиску ∇P\nГіпотеза KSS: η/s ≈ 1/(4π)", size=11, fill="#ffffff", stroke=BORDER, sw=1.0)
    f.append(b_s2)

    # Column 3: J/psi Suppression & Regeneration
    cx3 = cx2 + cw + 25
    f.append(path_svg(f"M {cx3} {cy} h {cw} v {ch} h {-cw} Z", fill="#f8fafc", stroke=BORDER, sw=1.0))
    f.append(text(cx3 + cw / 2, cy + 25, "3. Плавлення J/ψ", size=13, bold=True, color="#1e3a8a", anchor="middle"))
    f.append(text(cx3 + cw / 2, cy + 42, "(Екранування c-c̄ кварконіїв)", size=11, color=MUTED, anchor="middle"))

    cy_j = cy + 140
    f.append(circle(cx3 + cw / 2 - 30, cy_j, 12, fill="#ec4899", stroke=INK, sw=1.0))
    f.append(text(cx3 + cw / 2 - 30, cy_j + 4, "c", size=11, bold=True, color="#ffffff", anchor="middle"))

    f.append(circle(cx3 + cw / 2 + 30, cy_j, 12, fill="#a855f7", stroke=INK, sw=1.0))
    f.append(text(cx3 + cw / 2 + 30, cy_j + 4, "c̄", size=11, bold=True, color="#ffffff", anchor="middle"))

    f.append(line(cx3 + cw / 2 - 18, cy_j, cx3 + cw / 2 + 18, cy_j, color=POS, sw=2.0, dash="3,3"))
    b_jpsi, _, _ = textbox(cx3 + cw / 2, cy_j - 18, "r_D < r_(J/ψ)", size=9, bold=True, fill="#ffffff", stroke=POS, sw=0.8)
    f.append(b_jpsi)

    b_s3, _, _ = textbox(cx3 + cw / 2, cy + 265, "Тепловий термометр КГП\nДеінтеграція станів c-c̄ та b-b̄", size=11, fill="#ffffff", stroke=BORDER, sw=1.0)
    f.append(b_s3)

    render(os.path.join(IMG_DIR, "qgp-signatures.svg"), W, H, *f)


if __name__ == "__main__":
    fig_qgp_phase_diagram()
    fig_qgp_deconfinement_transition()
    fig_qgp_signatures()
    print("Всі 3 фігури QGP успішно згенеровано у ./img/")
