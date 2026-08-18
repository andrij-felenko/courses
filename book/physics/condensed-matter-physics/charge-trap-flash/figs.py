# -*- coding: utf-8 -*-
"""Фігури до теми «Charge trap Flash (SONOS/CTF)».
Запуск: python figs.py -> створює SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

BORDER = "#cbd5e1"

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Зонна діаграма структури SONOS (Program, Erase, Hold) ──────────────
def fig_sonos_band_diagram():
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 25, "Зонна діаграма структури SONOS у трьох станах", size=16, bold=True, color=INK))

    col_w = 260
    gap = 15
    y_top = 55
    panel_h = 425

    panels = [
        ("Програмування (V_g > 0)", "Тунелювання електронів у пастки Si₃N₄", "#eff6ff", "#1d4ed8"),
        ("Стирання (V_g < 0)", "Інжекція дірок та депасткування", "#fef2f2", "#b91c1c"),
        ("Збереження (V_g = 0)", "Глибокі пастки урівноважені бар'єрами", "#f0fdf4", "#15803d")
    ]

    for idx, (title, desc, bg_color, accent) in enumerate(panels):
        x0 = 15 + idx * (col_w + gap)
        f.append(rect(x0, y_top, col_w, panel_h, fill=bg_color, stroke=BORDER, rx=6))

        f.append(text(x0 + col_w / 2, y_top + 22, title, size=12, bold=True, color=accent))
        f.append(text(x0 + col_w / 2, y_top + 40, desc, size=10, color=MUTED, italic=True))

        # Межі шарів
        x_si = x0 + 40
        x_tox = x0 + 90
        x_nit = x0 + 170
        x_box = x0 + 220

        # Підписи шарів зверху
        f.append(text((x0+15 + x_si)/2, y_top + 58, "Si", size=10, bold=True, color=MUTED))
        f.append(text((x_si + x_tox)/2, y_top + 58, "SiO₂", size=10, bold=True, color=MUTED))
        f.append(text((x_tox + x_nit)/2, y_top + 58, "Si₃N₄", size=10, bold=True, color=MUTED))
        f.append(text((x_nit + x_box)/2, y_top + 58, "SiO₂", size=10, bold=True, color=MUTED))
        f.append(text((x_box + x0+col_w-10)/2, y_top + 58, "Gate", size=10, bold=True, color=MUTED))

        # Вертикальні пунктири меж
        for xv in [x_si, x_tox, x_nit, x_box]:
            f.append(line(xv, y_top + 65, xv, y_top + panel_h - 35, color="#cbd5e1", sw=1, dash="2,2"))

        y_base = y_top + 230

        if idx == 0:  # Program (V_g > 0)
            f.append(path_svg(f"M {x0+15} {y_base-40} L {x_si} {y_base-30}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x0+15} {y_base+40} L {x_si} {y_base+50}", stroke="#dc2626", sw=2.5))

            # Tunnel SiO2 barrier
            f.append(path_svg(f"M {x_si} {y_base-120} L {x_tox} {y_base-60}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x_si} {y_base+130} L {x_tox} {y_base+170}", stroke="#dc2626", sw=2.5))

            # Si3N4 trap layer
            f.append(path_svg(f"M {x_tox} {y_base-40} L {x_nit} {y_base+10}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x_tox} {y_base+100} L {x_nit} {y_base+130}", stroke="#dc2626", sw=2.5))

            # Blocking SiO2
            f.append(path_svg(f"M {x_nit} {y_base-50} L {x_box} {y_base+10}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x_nit} {y_base+150} L {x_box} {y_base+190}", stroke="#dc2626", sw=2.5))

            # Gate
            f.append(path_svg(f"M {x_box} {y_base+70} L {x0+col_w-10} {y_base+70}", stroke="#2563eb", sw=2.5))

            # FN Tunneling Arrow
            f.append(path_svg(f"M {x_si-5} {y_base-30} Q {x_si+25} {y_base-70} {x_tox+15} {y_base-20}", stroke="#1d4ed8", sw=2, dash="none"))
            f.append(path_svg(f"M {x_tox+15} {y_base-20} L {x_tox+8} {y_base-26} L {x_tox+10} {y_base-18} Z", fill="#1d4ed8", stroke="#1d4ed8", sw=1))
            f.append(text(x_si + 3, y_base - 130, "FN Тунелювання", size=9, color="#1d4ed8", anchor="start", bold=True))

            # Trapped electrons
            for xt, yt in [(x_tox+20, y_base+5), (x_tox+40, y_base+15), (x_tox+55, y_base+20)]:
                f.append(circle(xt, yt, 7, fill="#2563eb", stroke="#1d4ed8"))
                f.append(text(xt, yt+3, "e⁻", size=9, color="#ffffff", bold=True))

            f.append(text(x0+col_w/2, y_top + panel_h - 15, "Високе V_g > 0 створює трикутний бар'єр", size=9, color=INK))

        elif idx == 1:  # Erase (V_g < 0)
            f.append(path_svg(f"M {x0+15} {y_base+40} L {x_si} {y_base+30}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x0+15} {y_base+120} L {x_si} {y_base+110}", stroke="#dc2626", sw=2.5))

            # Tunnel SiO2 barrier
            f.append(path_svg(f"M {x_si} {y_base-50} L {x_tox} {y_base+20}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x_si} {y_base+110} L {x_tox} {y_base+170}", stroke="#dc2626", sw=2.5))

            # Si3N4 trap layer
            f.append(path_svg(f"M {x_tox} {y_base+30} L {x_nit} {y_base-20}", stroke="#2563eb", sw=2.5))
            f.append(path_svg(f"M {x_tox} {y_base+160} L {x_nit} {y_base+110}", stroke="#dc2626", sw=2.5))

            # Blocking SiO2
            f.append(path_svg(f"M {x_nit} {y_base+40} L {x_box} {y_base+100}", stroke="#2563eb", sw=2.5))

            # Gate
            f.append(path_svg(f"M {x_box} {y_base-90} L {x0+col_w-10} {y_base-90}", stroke="#2563eb", sw=2.5))

            # Hole injection arrow
            f.append(path_svg(f"M {x_si-5} {y_base+110} Q {x_si+25} {y_base+150} {x_tox+20} {y_base+135}", stroke="#dc2626", sw=2))
            f.append(path_svg(f"M {x_tox+20} {y_base+135} L {x_tox+12} {y_base+138} L {x_tox+15} {y_base+130} Z", fill="#dc2626", stroke="#dc2626", sw=1))
            f.append(text(x_si + 3, y_base + 175, "Інжекція дірок h⁺", size=9, color="#dc2626", anchor="start", bold=True))

            # Recombination
            f.append(circle(x_tox+35, y_base+125, 7, fill="#ef4444", stroke="#b91c1c"))
            f.append(text(x_tox+35, y_base+128, "h⁺", size=9, color="#ffffff", bold=True))

            f.append(text(x0+col_w/2, y_top + panel_h - 15, "V_g < 0 викликає інжекція дірок й депасткування", size=9, color=INK))

        else:  # Hold (V_g = 0)
            f.append(line(x0+15, y_base-10, x_si, y_base-10, color="#2563eb", sw=2.5))
            f.append(line(x0+15, y_base+70, x_si, y_base+70, color="#dc2626", sw=2.5))

            # SiO2 Tunnel
            f.append(line(x_si, y_base-10, x_si, y_base-110, color="#2563eb", sw=2))
            f.append(line(x_si, y_base-110, x_tox, y_base-110, color="#2563eb", sw=2.5))
            f.append(line(x_tox, y_base-110, x_tox, y_base-50, color="#2563eb", sw=2))

            f.append(line(x_si, y_base+70, x_si, y_base+170, color="#dc2626", sw=2))
            f.append(line(x_si, y_base+170, x_tox, y_base+170, color="#dc2626", sw=2.5))
            f.append(line(x_tox, y_base+170, x_tox, y_base+110, color="#dc2626", sw=2))

            # Si3N4 potential well
            f.append(line(x_tox, y_base-50, x_nit, y_base-50, color="#2563eb", sw=2.5))
            f.append(line(x_tox, y_base+110, x_nit, y_base+110, color="#dc2626", sw=2.5))

            # Blocking SiO2
            f.append(line(x_nit, y_base-50, x_nit, y_base-110, color="#2563eb", sw=2))
            f.append(line(x_nit, y_base-110, x_box, y_base-110, color="#2563eb", sw=2.5))
            f.append(line(x_box, y_base-110, x_box, y_base-10, color="#2563eb", sw=2))

            f.append(line(x_nit, y_base+110, x_nit, y_base+170, color="#dc2626", sw=2))
            f.append(line(x_nit, y_base+170, x_box, y_base+170, color="#dc2626", sw=2.5))
            f.append(line(x_box, y_base+170, x_box, y_base+70, color="#dc2626", sw=2))

            # Gate
            f.append(line(x_box, y_base-10, x0+col_w-10, y_base-10, color="#2563eb", sw=2.5))

            # Trapped electrons inside deep traps
            for xt, yt in [(x_tox+20, y_base-10), (x_tox+40, y_base-10), (x_tox+60, y_base-10)]:
                f.append(path_svg(f"M {xt-8} {y_base-50} L {xt-8} {y_base-10} L {xt+8} {y_base-10} L {xt+8} {y_base-50}", stroke="#1d4ed8", sw=1.2, fill="#dbeafe"))
                f.append(circle(xt, yt-8, 6, fill="#2563eb", stroke="#1d4ed8"))
                f.append(text(xt, yt-5, "e⁻", size=9, color="#ffffff", bold=True))

            f.append(text(x0+col_w/2, y_top + panel_h - 15, "Глибина пасток ~1.2 еВ забезпечує >10 років", size=9, color=INK))

    out_file = os.path.join(IMG_DIR, 'fig1-sonos-band-diagram.svg')
    with open(out_file, 'w', encoding='utf-8') as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n')
        fh.write(f'<rect width="{W}" height="{H}" fill="{BG}"/>\n')
        fh.write("\n".join(f))
        fh.write('\n</svg>\n')
    print(f"Generated: {out_file}")

# ── Фігура 2: Порівняння локалізованих пасток Si3N4 та плаваючого затвора ────────
def fig_trapping_mechanisms():
    W, H = 840, 380
    f = []

    f.append(text(W / 2, 25, "Механізм утримання заряду: Плаваючий затвор vs Диелектричні пастки CTF", size=16, bold=True, color=INK))

    col_w = 395
    gap = 20
    y_top = 55
    panel_h = 305

    # Ліва панель: Floating Gate
    x1 = 15
    f.append(rect(x1, y_top, col_w, panel_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x1 + col_w / 2, y_top + 22, "Плаваючий затвор (Floating Gate)", size=13, bold=True, color="#c2410c"))
    f.append(text(x1 + col_w / 2, y_top + 40, "Неперервний провідник (полікремній)", size=10, color=MUTED, italic=True))

    # Layers
    f.append(rect(x1 + 30, y_top + 60, col_w - 60, 30, fill="#e2e8f0", stroke="#64748b", rx=3))
    f.append(text(x1 + col_w / 2, y_top + 78, "Управляючий затвор (Control Gate)", size=10, bold=True, color=INK))

    f.append(rect(x1 + 30, y_top + 95, col_w - 60, 20, fill="#cbd5e1", stroke="#94a3b8", rx=2))
    f.append(text(x1 + col_w / 2, y_top + 109, "Міжзатворний диелектрик (ONO)", size=9, color=MUTED))

    # Floating gate
    f.append(rect(x1 + 30, y_top + 120, col_w - 60, 45, fill="#fed7aa", stroke="#f97316", rx=3))
    f.append(text(x1 + col_w / 2, y_top + 135, "Плаваючий затвор (n⁺ polysilicon)", size=10, bold=True, color="#c2410c"))
    for ex in range(x1 + 45, x1 + col_w - 40, 25):
        f.append(circle(ex, y_top + 150, 6, fill="#ea580c", stroke="#c2410c"))
        f.append(text(ex, y_top + 153, "e⁻", size=9, color="#ffffff", bold=True))

    # Tunnel oxide
    f.append(rect(x1 + 30, y_top + 170, col_w - 60, 25, fill="#e2e8f0", stroke="#94a3b8", rx=2))
    f.append(text(x1 + 75, y_top + 186, "Туннельний оксид SiO₂", size=9, color=MUTED))

    # Defect pinhole
    x_defect = x1 + col_w - 70
    f.append(rect(x_defect - 32, y_top + 170, 64, 25, fill="#fca5a5", stroke="#dc2626"))
    f.append(text(x_defect, y_top + 186, "Дефект", size=9, bold=True, color="#991b1b"))

    # Substrate rect
    f.append(rect(x1 + 30, y_top + 200, col_w - 60, 35, fill="#bbf7d0", stroke="#16a34a", rx=3))
    f.append(text(x1 + 45, y_top + 222, "Кремнієва підкладка (Si Substrate)", size=10, color="#15803d", anchor="start", bold=True))

    # Leakage arrow starting BELOW oxide rect (from y=252) into substrate
    f.append(path_svg(f"M {x_defect} {y_top+196} L {x_defect} {y_top+215}", stroke="#dc2626", sw=2.5, dash="3,3"))
    f.append(path_svg(f"M {x_defect} {y_top+215} L {x_defect-4} {y_top+207} L {x_defect+4} {y_top+207} Z", fill="#dc2626", stroke="#dc2626", sw=1))

    # Clean bottom note
    f.append(text(x1 + col_w / 2, y_top + 285, "Один дефект витікає УВЕСЬ заряд FG!", size=10, bold=True, color="#b91c1c"))

    # Права панель: Charge Trap Flash (SONOS)
    x2 = x1 + col_w + gap
    f.append(rect(x2, y_top, col_w, panel_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x2 + col_w / 2, y_top + 22, "Пастки заряду (Charge Trap Flash / CTF)", size=13, bold=True, color="#1d4ed8"))
    f.append(text(x2 + col_w / 2, y_top + 40, "Дискретні локалізовані пастки (K-центри Si₃N₄)", size=10, color=MUTED, italic=True))

    # Layers for CTF
    f.append(rect(x2 + 30, y_top + 60, col_w - 60, 30, fill="#e2e8f0", stroke="#64748b", rx=3))
    f.append(text(x2 + col_w / 2, y_top + 78, "Металевий затвор (Gate: TaN / TiN)", size=10, bold=True, color=INK))

    f.append(rect(x2 + 30, y_top + 95, col_w - 60, 20, fill="#dcfce7", stroke="#86efac", rx=2))
    f.append(text(x2 + col_w / 2, y_top + 109, "Блокуючий оксид (Al₂O₃ або SiO₂)", size=9, color="#15803d"))

    # Trap layer
    f.append(rect(x2 + 30, y_top + 120, col_w - 60, 45, fill="#bfdbfe", stroke="#3b82f6", rx=3))
    f.append(text(x2 + col_w / 2, y_top + 132, "Захоплюючий шар Si₃N₄ (Диелектрик)", size=9, bold=True, color="#1d4ed8"))

    # Isolated discrete traps
    trap_positions = [
        (x2 + 50, y_top + 148, True),
        (x2 + 95, y_top + 148, True),
        (x2 + 140, y_top + 148, False),
        (x2 + 185, y_top + 148, True),
        (x2 + 230, y_top + 148, True),
        (x2 + 275, y_top + 148, True),
        (x2 + 320, y_top + 148, True),
    ]
    for tx, ty, is_safe in trap_positions:
        if is_safe:
            f.append(circle(tx, ty, 7, fill="#1d4ed8", stroke="#1e40af"))
            f.append(text(tx, ty+3, "e⁻", size=9, color="#ffffff", bold=True))
        else:
            f.append(circle(tx, ty, 7, fill="#ef4444", stroke="#b91c1c"))
            f.append(text(tx, ty+3, "e⁻", size=9, color="#ffffff", bold=True))

    # Tunnel oxide
    f.append(rect(x2 + 30, y_top + 170, col_w - 60, 25, fill="#e2e8f0", stroke="#94a3b8", rx=2))
    f.append(text(x2 + 75, y_top + 186, "Ультратонукий оксид ~2 нм", size=9, color=MUTED))

    # Defect pinhole
    x_defect2 = x2 + 140
    f.append(rect(x_defect2 - 32, y_top + 170, 64, 25, fill="#fca5a5", stroke="#dc2626"))
    f.append(text(x_defect2, y_top + 186, "Дефект", size=9, bold=True, color="#991b1b"))

    # Substrate
    f.append(rect(x2 + 30, y_top + 200, col_w - 60, 35, fill="#bbf7d0", stroke="#16a34a", rx=3))
    f.append(text(x2 + col_w / 2, y_top + 222, "Кремнієва підкладка (Si Substrate)", size=10, bold=True, color="#15803d"))

    # Leakage arrow starting BELOW oxide rect (from y=196) into substrate
    f.append(path_svg(f"M {x_defect2} {y_top+196} L {x_defect2} {y_top+215}", stroke="#dc2626", sw=2, dash="3,3"))
    f.append(path_svg(f"M {x_defect2} {y_top+215} L {x_defect2-4} {y_top+207} L {x_defect2+4} {y_top+207} Z", fill="#dc2626", stroke="#dc2626", sw=1))

    # Clean bottom note
    f.append(text(x2 + col_w / 2, y_top + 285, "Витікає лише 1 заряд, інші захищені!", size=10, bold=True, color="#15803d"))

    out_file = os.path.join(IMG_DIR, 'fig2-trapping-mechanisms.svg')
    with open(out_file, 'w', encoding='utf-8') as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n')
        fh.write(f'<rect width="{W}" height="{H}" fill="{BG}"/>\n')
        fh.write("\n".join(f))
        fh.write('\n</svg>\n')
    print(f"Generated: {out_file}")

# ── Фігура 3: Циліндрична 3D V-NAND CTF структура (Gate-All-Around) ──────────────
def fig_3d_ctf_architecture():
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 25, "Архітектура 3D V-NAND: Циліндрична комірка з колоночним шаром CTF", size=16, bold=True, color=INK))

    panel1_w = 420
    panel2_w = 370
    y_top = 55
    panel_h = 345

    # Ліва частина: Вертикальний розріз 3D струни
    x1 = 15
    f.append(rect(x1, y_top, panel1_w, panel_h, fill="#fafafa", stroke=BORDER, rx=6))
    f.append(text(x1 + panel1_w / 2, y_top + 20, "Вертикальний розріз 3D струни (V-NAND)", size=12, bold=True, color=INK))

    y_gate_start = y_top + 45
    gate_h = 45
    iso_h = 25

    gate_names = ["Word Line 3 (Gate)", "Word Line 2 (Gate)", "Word Line 1 (Gate)"]

    for g_idx in range(3):
        yg = y_gate_start + g_idx * (gate_h + iso_h)
        f.append(rect(x1 + 25, yg, 110, gate_h, fill="#e2e8f0", stroke="#475569", rx=3))
        f.append(text(x1 + 80, yg + 27, gate_names[g_idx], size=9, bold=True, color=INK))

        f.append(rect(x1 + panel1_w - 135, yg, 110, gate_h, fill="#e2e8f0", stroke="#475569", rx=3))
        f.append(text(x1 + panel1_w - 80, yg + 27, gate_names[g_idx], size=9, bold=True, color=INK))

        if g_idx < 2:
            f.append(rect(x1 + 25, yg + gate_h, 110, iso_h, fill="#f1f5f9", stroke="#cbd5e1"))
            f.append(rect(x1 + panel1_w - 135, yg + gate_h, 110, iso_h, fill="#f1f5f9", stroke="#cbd5e1"))

    xc = x1 + panel1_w / 2

    x_bl_l, x_bl_r = xc - 55, xc + 55
    x_tr_l, x_tr_r = xc - 43, xc + 43
    x_tu_l, x_tu_r = xc - 33, xc + 33
    x_ch_l, x_ch_r = xc - 22, xc + 22
    x_co_l, x_co_r = xc - 10, xc + 10

    h_total = 3 * gate_h + 2 * iso_h

    # Blocking layer (Al2O3)
    f.append(rect(x_bl_l, y_gate_start, x_bl_r - x_bl_l, h_total, fill="#dcfce7", stroke="#22c55e"))
    # Trapping layer (Si3N4)
    f.append(rect(x_tr_l, y_gate_start, x_tr_r - x_tr_l, h_total, fill="#bfdbfe", stroke="#3b82f6"))
    # Tunnel oxide (SiO2)
    f.append(rect(x_tu_l, y_gate_start, x_tu_r - x_tu_l, h_total, fill="#f8fafc", stroke="#94a3b8"))
    # Poly-Si channel
    f.append(rect(x_ch_l, y_gate_start, x_ch_r - x_ch_l, h_total, fill="#fed7aa", stroke="#f97316"))
    # Oxide Core
    f.append(rect(x_co_l, y_gate_start, x_co_r - x_co_l, h_total, fill="#e2e8f0", stroke="#94a3b8"))
    f.append(text(xc, y_gate_start + h_total / 2, "Core SiO₂", size=9, color=MUTED, anchor="middle"))

    for g_idx in range(3):
        yg = y_gate_start + g_idx * (gate_h + iso_h) + gate_h / 2
        f.append(circle(x_tr_l + 6, yg, 4, fill="#1d4ed8", stroke="#1e40af"))
        f.append(circle(x_tr_r - 6, yg, 4, fill="#1d4ed8", stroke="#1e40af"))

    f.append(text(x1 + panel1_w / 2, y_top + panel_h - 15, "Суцільний вертикальний ONO-циліндр", size=10, bold=True, color="#1d4ed8"))


    # Права частина: Радіальний поперечний переріз комірки (GAA)
    x2 = x1 + panel1_w + 15
    f.append(rect(x2, y_top, panel2_w, panel_h, fill="#fafafa", stroke=BORDER, rx=6))
    f.append(text(x2 + panel2_w / 2, y_top + 20, "Радіальний розріз (Gate-All-Around)", size=12, bold=True, color=INK))

    cx = x2 + panel2_w / 2
    cy = y_top + 160

    radii = [
        (135, "#e2e8f0", "#475569", "Управляючий затвор (Gate Metal: W/TiN)", 11, INK),
        (105, "#dcfce7", "#22c55e", "Блокуючий оксид (Al₂O₃)", 9, "#15803d"),
        (82,  "#bfdbfe", "#3b82f6", "Шар пасток (Si₃N₄ CTF)", 9, "#1d4ed8"),
        (60,  "#ffffff", "#94a3b8", "Туннельний оксид (SiO₂)", 9, MUTED),
        (42,  "#fed7aa", "#f97316", "Канал (Poly-Si)", 9, "#c2410c"),
        (22,  "#e2e8f0", "#64748b", "Ядро (SiO₂)", 9, MUTED)
    ]

    for r, fill_c, stroke_c, label, txt_s, txt_c in radii:
        f.append(circle(cx, cy, r, fill=fill_c, stroke=stroke_c, sw=1.5))

    r_nit = 71
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        tx = cx + r_nit * math.cos(rad)
        ty = cy + r_nit * math.sin(rad)
        f.append(circle(tx, ty, 4, fill="#1d4ed8", stroke="#1e40af"))

    f.append(text(cx, y_top + panel_h - 45, "Симетрія GAA забезпечує рівномірне поле", size=10, bold=True, color=INK))
    f.append(text(cx, y_top + panel_h - 25, "та рівномірний рівень тунелювання за радіусом", size=9, color=MUTED))

    out_file = os.path.join(IMG_DIR, 'fig3-3d-ctf-architecture.svg')
    with open(out_file, 'w', encoding='utf-8') as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n')
        fh.write(f'<rect width="{W}" height="{H}" fill="{BG}"/>\n')
        fh.write("\n".join(f))
        fh.write('\n</svg>\n')
    print(f"Generated: {out_file}")

if __name__ == '__main__':
    fig_sonos_band_diagram()
    fig_trapping_mechanisms()
    fig_3d_ctf_architecture()
