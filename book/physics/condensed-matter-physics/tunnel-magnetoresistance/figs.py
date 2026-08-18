# -*- coding: utf-8 -*-
"""Фігури до теми «Тунельний магнітоопір (TMR)».
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


# ── Фігура 1: Зонна діаграма та тунелювання спінів у моделі Джульєра ─────────
def fig_spin_tunneling_band_diagram():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 26, "Спіново-поляризоване тунелювання у моделі Джульєра", size=16, bold=True, color=INK))

    # Panel 1: Parallel Alignment (P)
    p1_x, p1_y, p1_w, p1_h = 20, 50, 380, 370
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(p1_x + p1_w / 2, p1_y + 24, "Паралельний стан (P) — Низький опір (R_P)", size=13, bold=True, color="#1e293b"))

    # Ferromagnet 1 (Left), Barrier (Center), Ferromagnet 2 (Right)
    f.append(rect(p1_x + 20, p1_y + 50, 110, 270, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(p1_x + 75, p1_y + 70, "FM1 (↑)", size=12, bold=True, color="#1d4ed8"))

    f.append(rect(p1_x + 140, p1_y + 50, 80, 270, fill="#fef3c7", stroke="#fde047", rx=4))
    f.append(text(p1_x + 180, p1_y + 70, "Бар'єр", size=12, bold=True, color="#b45309"))

    f.append(rect(p1_x + 230, p1_y + 50, 130, 270, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(p1_x + 295, p1_y + 70, "FM2 (↑)", size=12, bold=True, color="#1d4ed8"))

    # Fermi energy line across
    f.append(line(p1_x + 15, p1_y + 190, p1_x + 365, p1_y + 190, color="#ef4444", sw=1.5, dash="4 3"))
    f.append(text(p1_x + 30, p1_y + 183, "E_F", size=11, bold=True, color="#dc2626"))

    # Left DOS profiles
    f.append(path_svg(f"M {p1_x+75} {p1_y+290} C {p1_x+120} {p1_y+230}, {p1_x+125} {p1_y+170}, {p1_x+75} {p1_y+110}", fill="none", stroke="#2563eb", sw=2))
    f.append(text(p1_x + 95, p1_y + 140, "D_↑", size=10, bold=True, color="#1d4ed8"))
    
    f.append(path_svg(f"M {p1_x+75} {p1_y+290} C {p1_x+40} {p1_y+230}, {p1_x+45} {p1_y+170}, {p1_x+75} {p1_y+110}", fill="none", stroke="#7c3aed", sw=2))
    f.append(text(p1_x + 55, p1_y + 140, "D_↓", size=10, bold=True, color="#6d28d9"))

    # Right DOS profiles
    f.append(path_svg(f"M {p1_x+295} {p1_y+290} C {p1_x+340} {p1_y+230}, {p1_x+345} {p1_y+170}, {p1_x+295} {p1_y+110}", fill="none", stroke="#2563eb", sw=2))
    f.append(text(p1_x + 315, p1_y + 140, "D_↑", size=10, bold=True, color="#1d4ed8"))
    
    f.append(path_svg(f"M {p1_x+295} {p1_y+290} C {p1_x+260} {p1_y+230}, {p1_x+265} {p1_y+170}, {p1_x+295} {p1_y+110}", fill="none", stroke="#7c3aed", sw=2))
    f.append(text(p1_x + 275, p1_y + 140, "D_↓", size=10, bold=True, color="#6d28d9"))

    # Tunneling paths
    f.append(arrow(p1_x + 120, p1_y + 165, p1_x + 275, p1_y + 165, color="#2563eb", sw=3.5))
    f.append(text(p1_x + 180, p1_y + 155, "↑ → ↑", size=10, bold=True, color="#1e40af"))

    f.append(arrow(p1_x + 50, p1_y + 215, p1_x + 265, p1_y + 215, color="#7c3aed", sw=1.2))
    f.append(text(p1_x + 180, p1_y + 230, "↓ → ↓", size=10, bold=True, color="#5b21b6"))

    f.append(text(p1_x + p1_w / 2, p1_y + 345, "G_P = G_↑↑ + G_↓↓ (Висока провідність)", size=11, bold=True, color="#166534"))


    # Panel 2: Antiparallel Alignment (AP)
    p2_x, p2_y, p2_w, p2_h = 420, 50, 380, 370
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(p2_x + p2_w / 2, p2_y + 24, "Антипаралельний стан (AP) — Високий опір (R_AP)", size=13, bold=True, color="#1e293b"))

    # Left FM
    f.append(rect(p2_x + 20, p2_y + 50, 110, 270, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(p2_x + 75, p2_y + 70, "FM1 (↑)", size=12, bold=True, color="#1d4ed8"))

    # Barrier
    f.append(rect(p2_x + 140, p2_y + 50, 80, 270, fill="#fef3c7", stroke="#fde047", rx=4))
    f.append(text(p2_x + 180, p2_y + 70, "Бар'єр", size=12, bold=True, color="#b45309"))

    # Right FM
    f.append(rect(p2_x + 230, p2_y + 50, 130, 270, fill="#fff1f2", stroke="#fca5a5", rx=4))
    f.append(text(p2_x + 295, p2_y + 70, "FM2 (↓)", size=12, bold=True, color="#b91c1c"))

    # Fermi energy line across
    f.append(line(p2_x + 15, p2_y + 190, p2_x + 365, p2_y + 190, color="#ef4444", sw=1.5, dash="4 3"))
    f.append(text(p2_x + 30, p2_y + 183, "E_F", size=11, bold=True, color="#dc2626"))

    # Left DOS profiles
    f.append(path_svg(f"M {p2_x+75} {p2_y+290} C {p2_x+120} {p2_y+230}, {p2_x+125} {p2_y+170}, {p2_x+75} {p2_y+110}", fill="none", stroke="#2563eb", sw=2))
    f.append(text(p2_x + 95, p2_y + 140, "D_↑", size=10, bold=True, color="#1d4ed8"))
    
    f.append(path_svg(f"M {p2_x+75} {p2_y+290} C {p2_x+40} {p2_y+230}, {p2_x+45} {p2_y+170}, {p2_x+75} {p2_y+110}", fill="none", stroke="#7c3aed", sw=2))
    f.append(text(p2_x + 55, p2_y + 140, "D_↓", size=10, bold=True, color="#6d28d9"))

    # Right DOS profiles (Inverted)
    f.append(path_svg(f"M {p2_x+295} {p2_y+290} C {p2_x+340} {p2_y+230}, {p2_x+345} {p2_y+170}, {p2_x+295} {p2_y+110}", fill="none", stroke="#7c3aed", sw=2))
    f.append(text(p2_x + 315, p2_y + 140, "D_↓", size=10, bold=True, color="#6d28d9"))
    
    f.append(path_svg(f"M {p2_x+295} {p2_y+290} C {p2_x+260} {p2_y+230}, {p2_x+265} {p2_y+170}, {p2_x+295} {p2_y+110}", fill="none", stroke="#2563eb", sw=2))
    f.append(text(p2_x + 275, p2_y + 140, "D_↑", size=10, bold=True, color="#1d4ed8"))

    # Tunneling paths
    f.append(arrow(p2_x + 120, p2_y + 165, p2_x + 265, p2_y + 165, color="#dc2626", sw=1.2))
    f.append(text(p2_x + 180, p2_y + 155, "↑ → ↑ (Пригнічено)", size=10, bold=True, color="#991b1b"))

    f.append(arrow(p2_x + 50, p2_y + 215, p2_x + 335, p2_y + 215, color="#dc2626", sw=1.2))
    f.append(text(p2_x + 180, p2_y + 230, "↓ → ↓ (Пригнічено)", size=10, bold=True, color="#991b1b"))

    f.append(text(p2_x + p2_w / 2, p2_y + 345, "G_AP = G_↑↓ + G_↓↑ (Низька провідність)", size=11, bold=True, color="#991b1b"))

    f.append(text(W / 2, H - 12, "Збереження напрямку спіну під час тунелювання змушує опір залежати від взаємної орієнтації намагніченостей", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-tunneling-band-diagram.svg'), W, H, "\n".join(f))


# ── Фігура 2: Когерентне тунелювання та фільтрація симетрій у MgO ────────────
def fig_mgo_symmetry_filtering():
    W, H = 800, 440
    f = []

    f.append(text(W / 2, 26, "Фільтрація блохівських симетрій у кристалічному бар'єрі MgO(001)", size=16, bold=True, color=INK))

    bx, by, bw, bh = 30, 50, 740, 350
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=BORDER, rx=8))

    f.append(rect(bx + 20, by + 40, 180, 250, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(bx + 110, by + 65, "Fe(001) Електрод 1", size=13, bold=True, color="#1d4ed8"))
    f.append(text(bx + 110, by + 85, "Блохівські стани при E_F", size=11, color="#3b82f6"))

    f.append(rect(bx + 250, by + 40, 240, 250, fill="#fef3c7", stroke="#fde047", rx=4))
    f.append(text(bx + 370, by + 65, "Кристалічний бар'єр MgO(001)", size=13, bold=True, color="#b45309"))
    f.append(text(bx + 370, by + 85, "Згасаючі еванесцентні хвилі", size=11, color="#d97706"))

    f.append(rect(bx + 540, by + 40, 180, 250, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(bx + 630, by + 65, "Fe(001) Електрод 2", size=13, bold=True, color="#1d4ed8"))
    f.append(text(bx + 630, by + 85, "Приймальні стани", size=11, color="#3b82f6"))

    # Wave symmetries
    y1 = by + 120
    f.append(text(bx + 110, y1 + 5, "Стан Δ₁ (s-p-d_z²)", size=11, bold=True, color="#166534"))
    f.append(path_svg(f"M {bx+200} {y1} L {bx+250} {y1} C {bx+320} {y1}, {bx+420} {y1+10}, {bx+490} {y1+15} L {bx+540} {y1+15}", fill="none", stroke="#16a34a", sw=3.5))
    f.append(arrow(bx + 490, y1 + 15, bx + 540, y1 + 15, color="#16a34a", sw=3.5))
    f.append(text(bx + 370, y1 - 8, "κ(Δ₁) = 0.85 Å⁻¹ (Мале згасання)", size=10, bold=True, color="#15803d"))
    f.append(text(bx + 630, y1 + 20, "Високе T(Δ₁)", size=10, bold=True, color="#166534"))

    y2 = by + 180
    f.append(text(bx + 110, y2 + 5, "Стан Δ₅ (d_xz, d_yz)", size=11, bold=True, color="#1e40af"))
    f.append(path_svg(f"M {bx+200} {y2} L {bx+250} {y2} C {bx+300} {y2+10}, {bx+380} {y2+35}, {bx+490} {y2+45} L {bx+540} {y2+45}", fill="none", stroke="#2563eb", sw=2))
    f.append(arrow(bx + 490, y2 + 45, bx + 540, y2 + 45, color="#2563eb", sw=2))
    f.append(text(bx + 370, y2 + 10, "κ(Δ₅) = 1.05 Å⁻¹ (Середнє згасання)", size=10, bold=True, color="#1d4ed8"))
    f.append(text(bx + 630, y2 + 45, "Пригнічене T(Δ₅)", size=10, bold=True, color="#1e40af"))

    y3 = by + 240
    f.append(text(bx + 110, y3 + 5, "Стан Δ₂' (d_xy)", size=11, bold=True, color="#6d28d9"))
    f.append(path_svg(f"M {bx+200} {y3} L {bx+250} {y3} C {bx+280} {y3+15}, {bx+320} {y3+40}, {bx+490} {y3+45} L {bx+540} {y3+45}", fill="none", stroke="#7c3aed", sw=1.5, dash="4 2"))
    f.append(text(bx + 370, y3 + 24, "κ(Δ₂') = 1.25 Å⁻¹ (Швидке згасання)", size=10, bold=True, color="#6d28d9"))
    f.append(text(bx + 630, y3 + 45, "Незриме T(Δ₂') ≈ 0", size=10, bold=True, color="#5b21b6"))

    f.append(text(bx + bw / 2, by + 325, "При E_F стан Δ₁ у Fe є 100% спіново-поляризованим (тільки спін ↑), що піднімає TMR > 600%", size=11, bold=True, color="#166534"))

    f.append(text(W / 2, H - 12, "Когерентний добір симетрій у кристалічному MgO перетворює бар'єр на ефективний спіновий фільтр", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'mgo-symmetry-filtering.svg'), W, H, "\n".join(f))


# ── Фігура 3: Багатошарова структура MTJ та вольт-амперна/гістерезисна крива ─
def fig_mtj_structure_and_tmr_curve():
    W, H = 840, 460
    f = []

    f.append(text(W / 2, 26, "Конструкція MTJ-структури та петля магнітоопору R(H)", size=16, bold=True, color=INK))

    p1_x, p1_y, p1_w, p1_h = 20, 50, 390, 370
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(p1_x + p1_w / 2, p1_y + 24, "Вертикальний стек шарів MTJ", size=13, bold=True, color="#1e293b"))

    layers = [
        ("Верхній електрод (Cap / Hard Mask)", 30, "#e2e8f0", "#475569", ""),
        ("Вільний шар (Free Layer: CoFeB)", 40, "#dbeafe", "#1d4ed8", "↑ / ↓ (Перемикається)"),
        ("Тунельний бар'єр (MgO ~1.1 нм)", 25, "#fef3c7", "#b45309", "Квантове тунелювання"),
        ("Опорний шар (Pinned Layer: CoFeB)", 35, "#fee2e2", "#b91c1c", "↑ (Фіксований)"),
        ("Немагнітна прокладка (Ru ~0.8 нм)", 18, "#f3e8ff", "#6b21a8", "Антиферомагнітний зв'язок"),
        ("Заколовлений шар (Pinned 2: CoFe)", 35, "#fee2e2", "#991b1b", "↓ (Протилежний)"),
        ("Антиферомагнетик (AFM: PtMn / IrMn)", 45, "#dcfce7", "#15803d", "Обмінне зміщення (Exchange Bias)"),
        ("Буфер / Нижній електрод (Seed Layer)", 30, "#cbd5e1", "#334155", "")
    ]

    curr_y = p1_y + 45
    for l_title, l_h, l_fill, l_color, l_sub in layers:
        f.append(rect(p1_x + 30, curr_y, 330, l_h, fill=l_fill, stroke=l_color, rx=3))
        f.append(text(p1_x + 45, curr_y + l_h / 2 + 4, l_title, size=11, bold=True, color=l_color, anchor="start"))
        if l_sub:
            f.append(text(p1_x + 350, curr_y + l_h / 2 + 4, l_sub, size=9, bold=True, color="#64748b", anchor="end"))
        curr_y += l_h + 3


    # Panel 2: TMR Hysteresis Loop R(H)
    p2_x, p2_y, p2_w, p2_h = 430, 50, 390, 370
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(p2_x + p2_w / 2, p2_y + 24, "Залежність опору R від зовнішнього поля H", size=13, bold=True, color="#1e293b"))

    ax_x0 = p2_x + 70
    ax_y0 = p2_y + 310
    ax_w = 290
    ax_h = 240

    # Horizontal axis
    f.append(line(ax_x0 - 15, ax_y0, ax_x0 + ax_w + 15, ax_y0, color="#64748b", sw=1.5))
    f.append(arrow(ax_x0 + ax_w, ax_y0, ax_x0 + ax_w + 15, ax_y0, color="#64748b", sw=1.5))
    f.append(text(ax_x0 + ax_w + 10, ax_y0 + 20, "Поле H", size=11, bold=True, color="#475569"))

    # Vertical axis
    f.append(line(ax_x0, ax_y0 + 15, ax_x0, ax_y0 - ax_h - 15, color="#64748b", sw=1.5))
    f.append(arrow(ax_x0, ax_y0 - ax_h, ax_x0, ax_y0 - ax_h - 15, color="#64748b", sw=1.5))
    f.append(text(ax_x0, ax_y0 - ax_h - 20, "Опір R", size=11, bold=True, color="#475569", anchor="middle"))

    # Resistance levels
    r_p_y = ax_y0 - 50
    f.append(line(ax_x0 + 5, r_p_y, ax_x0 + ax_w, r_p_y, color="#2563eb", sw=1, dash="3 3"))
    f.append(text(ax_x0 - 12, r_p_y + 4, "R_P", size=10, bold=True, color="#1d4ed8", anchor="end"))
    f.append(text(ax_x0 + 210, r_p_y + 18, "Паралельний стан (↑ ↑)", size=10, bold=True, color="#1e40af"))

    r_ap_y = ax_y0 - 200
    f.append(line(ax_x0 + 5, r_ap_y, ax_x0 + ax_w, r_ap_y, color="#dc2626", sw=1, dash="3 3"))
    f.append(text(ax_x0 - 12, r_ap_y + 4, "R_AP", size=10, bold=True, color="#b91c1c", anchor="end"))
    f.append(text(ax_x0 + 75, r_ap_y - 10, "Антипаралельний стан (↑ ↓)", size=10, bold=True, color="#991b1b"))

    h1_x = ax_x0 + 80
    h2_x = ax_x0 + 200

    f.append(path_svg(f"M {ax_x0+15} {r_ap_y} L {h2_x} {r_ap_y} L {h2_x} {r_p_y} L {ax_x0+ax_w} {r_p_y}", stroke="#dc2626", sw=2.5))
    f.append(path_svg(f"M {ax_x0+ax_w} {r_p_y} L {h1_x} {r_p_y} L {h1_x} {r_ap_y} L {ax_x0+15} {r_ap_y}", stroke="#2563eb", sw=2.5))

    f.append(arrow(ax_x0 + ax_w - 30, r_p_y, ax_x0 + ax_w - 30, r_ap_y, color="#166534", sw=2))
    f.append(arrow(ax_x0 + ax_w - 30, r_ap_y, ax_x0 + ax_w - 30, r_p_y, color="#166534", sw=2))
    f.append(text(ax_x0 + ax_w - 35, (r_p_y + r_ap_y) / 2 + 4, "ΔR = R_AP - R_P", size=10, bold=True, color="#166534", anchor="end"))

    f.append(text(W / 2, H - 12, "Синтетичний антиферомагнетик (SAF) заклинює опорний шар, забезпечуючи чітке перемикання опору", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'mtj-structure-and-tmr-curve.svg'), W, H, "\n".join(f))


# ── Фігура 4: Залежність TMR від напруги зсуву (Bias Voltage) ───────────────
def fig_tmr_bias_dependence():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 26, "Залежність тунельного магнітоопору від напруги зсуву V_bias", size=16, bold=True, color=INK))

    bx, by, bw, bh = 40, 50, 680, 340
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=BORDER, rx=8))

    ax_x0 = bx + 80
    ax_y0 = by + 280
    ax_w = 550
    ax_h = 210

    # Axes
    f.append(line(ax_x0 - 15, ax_y0, ax_x0 + ax_w + 15, ax_y0, color="#64748b", sw=1.5))
    f.append(arrow(ax_x0 + ax_w, ax_y0, ax_x0 + ax_w + 15, ax_y0, color="#64748b", sw=1.5))
    f.append(text(ax_x0 + ax_w - 20, ax_y0 + 25, "Напруга зсуву V (В)", size=11, bold=True, color="#475569"))

    f.append(line(ax_x0, ax_y0 + 15, ax_x0, ax_y0 - ax_h - 15, color="#64748b", sw=1.5))
    f.append(arrow(ax_x0, ax_y0 - ax_h, ax_x0, ax_y0 - ax_h - 15, color="#64748b", sw=1.5))
    f.append(text(ax_x0, ax_y0 - ax_h - 20, "TMR (%)", size=11, bold=True, color="#475569", anchor="middle"))

    tmr_max_y = ax_y0 - 180
    v12_y = ax_y0 - 90

    f.append(line(ax_x0 + 5, v12_y, ax_x0 + ax_w - 40, v12_y, color="#cbd5e1", sw=1, dash="4 3"))
    f.append(text(ax_x0 - 10, v12_y + 4, "TMR₀ / 2", size=10, bold=True, color="#475569", anchor="end"))

    v0_x = ax_x0 + 150
    points = []
    for i in range(340):
        vx = i * 1.2
        v_volts = (vx - 150) / 100.0
        v_half = 0.5
        tmr_val = 200.0 / (1.0 + (v_volts / v_half)**2)
        px = ax_x0 + i * 1.5
        py = ax_y0 - (tmr_val / 200.0) * 180.0
        points.append(f"{px:.1f},{py:.1f}")

    f.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#2563eb" stroke-width="3"/>')

    f.append(circle(v0_x, tmr_max_y, 5, fill="#1d4ed8", stroke="none"))
    f.append(text(v0_x, tmr_max_y - 12, "TMR₀ ≈ 200-600% (V = 0)", size=11, bold=True, color="#1d4ed8"))

    v12_x = v0_x + 50
    f.append(circle(v12_x, v12_y, 5, fill="#dc2626", stroke="none"))
    f.append(line(v12_x, ax_y0, v12_x, v12_y, color="#dc2626", sw=1, dash="3 3"))
    f.append(text(v12_x, ax_y0 + 18, "V₁/₂ ≈ 0.5 В", size=10, bold=True, color="#b91c1c"))

    # Mechanisms box
    f.append(rect(ax_x0 + 250, by + 40, 260, 75, fill="#eff6ff", stroke="#bfdbfe", rx=4))
    f.append(text(ax_x0 + 260, by + 60, "Причини деградації TMR при V > 0:", size=11, bold=True, color="#1e40af", anchor="start"))
    f.append(text(ax_x0 + 260, by + 78, "1. Випромінювання магнонів (спінових хвиль)", size=10, color="#1e3a8a", anchor="start"))
    f.append(text(ax_x0 + 260, by + 94, "2. Зсув стану за рівень Фермі E_F", size=10, color="#1e3a8a", anchor="start"))

    f.append(text(W / 2, H - 12, "При підвищенні напруги зсуву до V₁/₂ ефективний тунельний магнітоопір зменшується вдвічі", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'tmr-bias-dependence.svg'), W, H, "\n".join(f))


if __name__ == "__main__":
    fig_spin_tunneling_band_diagram()
    fig_mgo_symmetry_filtering()
    fig_mtj_structure_and_tmr_curve()
    fig_tmr_bias_dependence()
    print("Всі фігури TMR успішно згенеровано.")
