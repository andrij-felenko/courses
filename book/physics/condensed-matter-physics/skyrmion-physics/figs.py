# -*- coding: utf-8 -*-
"""Фігури до теми «Скироміони у магнітних матеріалах».
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

# ── Фігура 1: Топологічні типи магнітних скирміонів ────────────────────────────
def fig_skyrmion_structures():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 26, "Топологічні спинові текстури: Блохівський, Неєлівський скирміони та Антискирміон", size=15, bold=True, color=INK))

    panel_w = 245
    panel_h = 360
    y_top = 50

    panels = [
        ("Блохівський скирміон", "Тангенційне обертання спінів\n(киральний вихор у об'ємних кристалах)", "#eff6ff", "#1d4ed8", "bloch"),
        ("Неєлівський скирміон", "Радіальне обертання спінів\n(їжакоподібний у тонких плівках з DMI)", "#f0fdf4", "#15803d", "neel"),
        ("Антискирміон", "Анізотропна киральність\n(топологічний заряд Q = -1)", "#fff7ed", "#c2410c", "anti")
    ]

    for idx, (title_str, sub_str, bg_color, main_color, stype) in enumerate(panels):
        x0 = 20 + idx * 260
        f.append(rect(x0, y_top, panel_w, panel_h, fill=bg_color, stroke=BORDER, rx=8))
        f.append(text(x0 + panel_w / 2, y_top + 24, title_str, size=13, bold=True, color=main_color))

        # Center of spin grid
        cx_p = x0 + panel_w / 2
        cy_p = y_top + 165
        grid_r = 85

        # Draw spin grid (polar coordinates sampling)
        rings = 4
        spins_per_ring = [1, 6, 12, 18]

        for r_idx, num_s in enumerate(spins_per_ring):
            r_dist = (r_idx / (rings - 1)) * grid_r
            for s_idx in range(num_s):
                angle = (2 * math.pi * s_idx / num_s) if num_s > 1 else 0.0
                sx = cx_p + r_dist * math.cos(angle)
                sy = cy_p + r_dist * math.sin(angle)

                # Polar radius fraction
                rho = r_dist / grid_r
                # Magnetization theta profile: theta=pi at center (rho=0), theta=0 at edge (rho=1)
                theta = math.pi * (1.0 - rho)

                # Spin phi direction depending on skyrmion type
                if stype == "bloch":
                    # Tangential rotation: phi = angle + pi/2
                    phi = angle + math.pi / 2.0
                elif stype == "neel":
                    # Radial rotation: phi = angle
                    phi = angle
                elif stype == "anti":
                    # Antiskyrmion: phi = -angle
                    phi = -angle

                # Vector components of spin m = (sin theta cos phi, sin theta sin phi, cos theta)
                mx = math.sin(theta) * math.cos(phi)
                my = math.sin(theta) * math.sin(phi)
                mz = math.cos(theta)

                # Arrow draw coordinates
                arrow_len = 18
                ex = sx + arrow_len * mx
                ey = sy - arrow_len * my  # inverted Y for SVG screen coordinates

                # Color based on mz component (out-of-plane)
                if mz < -0.3:
                    spin_col = "#7c3aed" # down
                elif mz > 0.3:
                    spin_col = "#dc2626" # up
                else:
                    spin_col = "#059669" # in-plane

                # Draw atom base circle
                f.append(circle(sx, sy, 3.5, fill=spin_col, stroke="none"))
                # Draw spin vector
                if arrow_len * math.hypot(mx, my) > 2:
                    f.append(arrow(sx, sy, ex, ey, color=spin_col, sw=1.8))
                else:
                    # Pure z-spin representation
                    if mz < 0:
                        # Cross (into page / down)
                        f.append(line(sx - 3, sy - 3, sx + 3, sy + 3, color=spin_col, sw=1.5))
                        f.append(line(sx - 3, sy + 3, sx + 3, sy - 3, color=spin_col, sw=1.5))
                    else:
                        # Dot (out of page / up)
                        f.append(circle(sx, sy, 1.5, fill=spin_col, stroke="none"))

        # Legend / Explanation inside panel
        sub_lines = sub_str.split("\n")
        for l_idx, line_t in enumerate(sub_lines):
            f.append(text(x0 + panel_w / 2, y_top + panel_h - 45 + l_idx * 18, line_t, size=11, bold=False, color=INK))

        # Topological charge badge
        q_val = "Q = +1" if stype != "anti" else "Q = -1"
        tb_str, _, _ = textbox(x0 + panel_w / 2, y_top + panel_h - 90, q_val, size=11, pad=5, fill="#ffffff", stroke=main_color, bold=True)
        f.append(tb_str)

    f.append(text(W / 2, H - 12, "Стрілки показують проєкцію спінів у площині, колір — перпендикулярну компоненту mz", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'skyrmion-structures.svg'), W, H, "\n".join(f))

# ── Фігура 2: Мікроскопічний механізм DMI ─────────────────────────────────────
def fig_dmi_mechanism():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 26, "Мікроскопічний механізм взаємодії Дзялошинського — Моріа (DMI)", size=15, bold=True, color=INK))

    # Left box: Symmetric Heisenberg Exchange vs Right box: Antisymmetric DMI
    # Panel 1: Symmetric exchange (Heisenberg)
    f.append(rect(20, 50, 355, 300, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(197, 75, "Симетричний обмін (Гейзенберг)", size=13, bold=True, color="#1e293b"))
    f.append(text(197, 95, "E_ex = -J · (S_i · S_j)", size=12, bold=True, color="#2563eb"))

    # Atoms i and j
    f.append(circle(110, 180, 16, fill="#3b82f6", stroke="#1d4ed8", sw=2))
    f.append(text(110, 184, "S_i", size=12, bold=True, color="#ffffff"))
    f.append(circle(280, 180, 16, fill="#3b82f6", stroke="#1d4ed8", sw=2))
    f.append(text(280, 184, "S_j", size=12, bold=True, color="#ffffff"))

    # Parallel spin alignment arrows
    f.append(arrow(110, 160, 110, 115, color="#dc2626", sw=3))
    f.append(arrow(280, 160, 280, 115, color="#dc2626", sw=3))

    # Exchange bond
    f.append(line(126, 180, 264, 180, color="#64748b", sw=2, dash="4,4"))
    f.append(text(197, 172, "Обмін J > 0", size=11, bold=True, color="#475569"))

    tb_h1, _, _ = textbox(197, 260, "Інваріантність відносно інверсії:\nСпіни прагнуть встановитися паралельно\n(або антипаралельно при J < 0)", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    f.append(tb_h1)

    # Panel 2: Antisymmetric DMI (Interfacial DMI)
    f.append(rect(405, 50, 355, 300, fill="#f0fdf4", stroke=BORDER, rx=8))
    f.append(text(582, 75, "Асиметричний обмін (DMI)", size=13, bold=True, color="#15803d"))
    f.append(text(582, 95, "E_DMI = -D_ij · (S_i × S_j)", size=12, bold=True, color="#059669"))

    # Ferromagnet atoms i, j and Heavy Metal atom k
    f.append(circle(480, 200, 16, fill="#3b82f6", stroke="#1d4ed8", sw=2))
    f.append(text(480, 204, "S_i", size=12, bold=True, color="#ffffff"))
    f.append(circle(680, 200, 16, fill="#3b82f6", stroke="#1d4ed8", sw=2))
    f.append(text(680, 204, "S_j", size=12, bold=True, color="#ffffff"))

    # Heavy metal atom with strong Spin-Orbit Coupling
    f.append(circle(580, 130, 18, fill="#7c3aed", stroke="#6d28d9", sw=2))
    f.append(text(580, 134, "HM", size=11, bold=True, color="#ffffff"))
    f.append(text(580, 105, "Спін-орбітальний зв'язок (L·S)", size=10, bold=True, color="#6d28d9"))

    # Superexchange paths (triangular mechanism Fert-Levy)
    f.append(line(492, 190, 568, 140, color="#7c3aed", sw=2))
    f.append(line(668, 190, 592, 140, color="#7c3aed", sw=2))

    # Canted spin alignment (perpendicular preference)
    # Spin S_i up
    f.append(arrow(480, 180, 480, 135, color="#dc2626", sw=3))
    # Spin S_j canted right
    f.append(arrow(680, 180, 720, 180, color="#dc2626", sw=3))

    # DMI Vector D_ij
    f.append(arrow(580, 200, 580, 235, color="#059669", sw=2.5))
    f.append(text(615, 222, "Вектор D_ij", size=11, bold=True, color="#059669"))

    tb_h2, _, _ = textbox(582, 270, "Порушення симетрії інверсії на межі плівок:\nЗмушує сусідні спіни повертатися\nпід кутом 90°, задаючи киральність", size=11, pad=6, fill="#ffffff", stroke="#a7f3d0")
    f.append(tb_h2)

    f.append(text(W / 2, H - 12, "Конкуренція між Гейзенбергівським обміном J та DMI визначає характерний розмір і структуру скирміона", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'dmi-mechanism.svg'), W, H, "\n".join(f))

# ── Фігура 3: Концепція трекової пам'яті (Racetrack Memory) ───────────────────
def fig_racetrack_memory_concept():
    W, H = 820, 420
    f = []

    f.append(text(W / 2, 26, "Скироміонна трекова пам'ять (Skyrmion Racetrack Memory)", size=15, bold=True, color=INK))

    # Nanowire background (track)
    track_x = 40
    track_y = 150
    track_w = 740

    # Substrate heavy metal layer (Pt / Ta)
    f.append(rect(track_x, track_y + 45, track_w, 35, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=4))
    f.append(text(track_x + 90, track_y + 67, "Важкий метал (Pt / Ta / W)", size=11, bold=True, color="#475569"))

    # Ferromagnetic thin film track (CoFeB / Co)
    f.append(rect(track_x, track_y, track_w, 45, fill="#fee2e2", stroke="#f87171", sw=2, rx=4))
    f.append(text(track_x + 90, track_y + 26, "Магнітний трек (FM)", size=11, bold=True, color="#991b1b"))

    # Electric Current flow (Charge current I_e) in Heavy Metal
    f.append(arrow(track_x + 20, track_y + 105, track_x + 160, track_y + 105, color="#2563eb", sw=3))
    f.append(text(track_x + 90, track_y + 125, "Струм заряду I_e (SOT)", size=11, bold=True, color="#2563eb"))

    # Spin Hall Effect current (Spin current J_s upwards)
    f.append(arrow(track_x + 220, track_y + 75, track_x + 220, track_y + 48, color="#7c3aed", sw=2.5))
    f.append(text(track_x + 220, track_y + 90, "Спіновий струм J_s", size=10, bold=True, color="#7c3aed"))

    # Skyrmions along the track (representing bits)
    # Bit sequence: 1 - 0 - 1 - 1 - 0 - 1
    bits = [
        (130, "1", True),
        (230, "0", False),
        (330, "1", True),
        (430, "1", True),
        (530, "0", False),
        (630, "1", True)
    ]

    for bx, bit_val, has_skyrmion in bits:
        if has_skyrmion:
            # Outer ring representing Néel skyrmion domain wall
            f.append(circle(bx, track_y + 22, 16, fill="#c084fc", stroke="#7e22ce", sw=1.5))
            # Core spin down
            f.append(circle(bx, track_y + 22, 7, fill="#1e1b4b", stroke="none"))
            # Motion vector arrow (due to SOT driving)
            f.append(arrow(bx + 18, track_y + 22, bx + 36, track_y + 22, color="#059669", sw=2.5))

        # Bit label below track
        f.append(rect(bx - 12, track_y - 35, 24, 22, fill="#ffffff", stroke="#cbd5e1", rx=3))
        f.append(text(bx, track_y - 20, bit_val, size=12, bold=True, color="#0f172a" if has_skyrmion else "#94a3b8"))

    # Write Head (Injector) at left side
    f.append(rect(60, 45, 70, 55, fill="#dbeafe", stroke="#2563eb", sw=2, rx=6))
    f.append(text(95, 68, "Вузол", size=11, bold=True, color="#1e40af"))
    f.append(text(95, 84, "запису", size=11, bold=True, color="#1e40af"))
    f.append(line(95, 100, 95, 145, color="#2563eb", sw=2, dash="3,3"))

    # Read Head (Magnetic Tunnel Junction MTJ) at right side
    f.append(rect(670, 45, 80, 55, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    f.append(text(710, 68, "Зчитувач", size=11, bold=True, color="#92400e"))
    f.append(text(710, 84, "MTJ / TMR", size=11, bold=True, color="#92400e"))
    f.append(line(710, 100, 710, 145, color="#d97706", sw=2, dash="3,3"))

    # Skyrmion Hall Effect (SHE) forces explanation box
    tb_she, _, _ = textbox(W / 2, 330, "Магнусівська сила й холівський ефект скирміонів (Skyrmion Hall Effect):\nТопологічний заряд Q створює поперечне відхилення F_M = G × v, що штовхає скирміон до краю треку.\nДля компенсації використовують антиферомагнітно звязані двошарові треки (SAF).", size=11, pad=8, fill="#ffffff", stroke="#cbd5e1")
    f.append(tb_she)

    f.append(text(W / 2, H - 12, "Наносекундні імпульси струму рухають ланцюжок скирміонів зі швидкістю понад 100 м/с при низькому енергоспоживанні", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'racetrack-memory-concept.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_skyrmion_structures()
    fig_dmi_mechanism()
    fig_racetrack_memory_concept()
    print("Figures generated successfully in img/")
