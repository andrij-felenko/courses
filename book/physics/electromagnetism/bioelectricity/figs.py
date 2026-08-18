# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def path(d, color=INK, sw=3.0, fill='none', dash=None):
    dd = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round"%s/>' % (d, fill, color, sw, dd))


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Lipid bilayer membrane as an electric capacitor separating ions
# ═══════════════════════════════════════════════════════════════════════════
def fig_membrane_capacitor():
    W, H = 760, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Клітинна мембрана як електричний конденсатор', 17, INK, 'middle', bold=True))

    # Extracellular vs Intracellular space backgrounds
    f.append(rect(60, 50, 640, 115, fill='#eef4fb', stroke='#b0c4de', sw=1, rx=6))
    f.append(text(80, 75, 'Позаклітинне середовище (ECF)', 13, NEG, 'start', bold=True))
    f.append(text(80, 95, '[Na⁺] = 145 мМ | [Cl⁻] = 110 мМ | [K⁺] = 5 мМ', 11, MUTED, 'start'))

    f.append(rect(60, 265, 640, 115, fill='#fdf2f0', stroke='#f5c6cb', sw=1, rx=6))
    f.append(text(80, 290, 'Внутрішньоклітинне середовище (ICF / Цитоплазма)', 13, POS, 'start', bold=True))
    f.append(text(80, 310, '[K⁺] = 140 мМ | [Na⁺] = 15 мМ | [A⁻] (білки) = 140 мМ', 11, MUTED, 'start'))

    # Lipid bilayer (membrane dielectric core)
    my0, my1 = 165, 265
    f.append(rect(60, my0, 640, my1 - my0, fill='#fdf8e2', stroke='#e6c200', sw=1.8, rx=4))

    # Phospholipid heads and tails representation
    for x in range(80, 640, 26):
        # Outer hydrophilic heads
        f.append(circle(x, my0 + 6, 5, fill='#e67e22', stroke='#d35400', sw=1.0))
        f.append(line(x, my0 + 11, x, my0 + 42, color='#d35400', sw=1.2))
        # Inner hydrophilic heads
        f.append(circle(x, my1 - 6, 5, fill='#e67e22', stroke='#d35400', sw=1.0))
        f.append(line(x, my1 - 11, x, my1 - 42, color='#d35400', sw=1.2))

    # Charges aligned on outer (+) and inner (-) faces
    for x in range(95, 630, 45):
        f.append(plus(x, my0 - 14, r=8))
        f.append(minus(x, my1 + 14, r=8))

    # Electric field arrows (placed away from center text)
    for x in [130, 220, 540, 630]:
        f.append(arrow(x, my0 + 12, x, my1 - 12, color=FIELD, sw=2.0))

    # Center text box for field strength
    f.append(fitbox(290, my0 + 32, 180, 36, 'Електричне поле\nE ≈ 10⁷ В/м', size=12,
                    fill='#ffffff', stroke=FIELD, bold=True, color=FIELD))

    # Right side membrane thickness
    f.append(text(670, (my0 + my1) / 2 + 4, 'd ≈ 7 нм', 12, INK, 'end', bold=True))

    # Bottom summary box
    f.append(fitbox(60, 388, 640, 36,
                    'Ліпідний бішар — діелектрик (εᵣ ≈ 2). Ємність мембрани Cₘ ≈ 1 мкФ/см².\n'
                    'Потенціал спокою Vₘ = Φᵢₙ - Φₒᵤₜ ≈ -70 мВ забезпечує гігантську напруженість поля.',
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'membrane-capacitor.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Action potential waveform V_m(t) and channel gating states
# ═══════════════════════════════════════════════════════════════════════════
def fig_action_potential_cycle():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Фази потенціалу дії та стани іонних каналів', 17, INK, 'middle', bold=True))

    # Axes for Action Potential V_m(t)
    ox, oy = 80, 350
    f.append(arrow(ox, oy, ox, 60, color=INK, sw=1.8))
    f.append(arrow(ox, oy, 680, oy, color=INK, sw=1.8))

    f.append(text(ox - 10, 65, 'Vₘ (мВ)', 12, INK, 'end', bold=True))
    f.append(text(685, oy + 20, 'час (мс)', 12, INK, 'middle', bold=True))

    # Y-axis ticks and grid lines
    y_peaks = [
        (+40, 110, POS, '+40 мВ (овершут E_Na)'),
        (0, 160, MUTED, '0 мВ'),
        (-55, 235, '#e67e22', '-55 мВ (поріг)'),
        (-65, 258, NEG, '-65 мВ (спокій)'),
        (-75, 282, '#8e44ad', '-75 мВ (гіперполяризація E_K)')
    ]

    for val, ypos, col, label in y_peaks:
        f.append(line(ox - 4, ypos, 660, ypos, color=col, sw=1.0, dash='3,3'))
        f.append(text(ox - 8, ypos + 4, str(val), 11, col, 'end'))

    # Action potential curve path
    ap_path = ('M 80,258 L 160,258 L 200,235 L 260,110 '
               'L 330,282 L 440,282 L 520,258 L 660,258')
    f.append(path(ap_path, color=POS, sw=3.2))

    # Phase boxes and labels
    f.append(fitbox(90, 290, 100, 48, '1. Спокій\n(Na⁺ закрито,\nK⁺ закрито)', size=11, fill='#eef4fb', stroke=NEG))
    f.append(fitbox(205, 75, 110, 48, '2. Деполяризація\n(Na⁺ відкриті,\ninflux Na⁺)', size=11, fill='#fdf2f0', stroke=POS))
    f.append(fitbox(325, 150, 110, 48, '3. Реполяризація\n(Na⁺ інактивовано,\nK⁺ відкриті)', size=11, fill='#f4eefd', stroke='#8e44ad'))
    f.append(fitbox(450, 300, 130, 48, '4. Гіперполяризація\n(слідовий потенціал,\nрефрактерність)', size=11, fill='#eefbf4', stroke=FIELD))

    # Bottom summary
    f.append(fitbox(80, 385, 600, 42,
                    'Пороговий стимул (-55 мВ) вмикає лавиноподібну активацію натрію (m³).\n'
                    'Автоматична інактивація натрію (h) та запізніла активація калію (n⁴) повертають напругу.',
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'action-potential-cycle.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Cable theory model & Saltatory conduction in myelinated axon
# ═══════════════════════════════════════════════════════════════════════════
def fig_cable_propagation():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Кабельна модель аксона та сальтаторне проведення', 17, INK, 'middle', bold=True))

    # Upper Panel: Unmyelinated Axon Cable Model
    f.append(text(60, 55, 'А. Немієлінізоване волокно: згасання λ = √(rₘ / rᵢ)', 13, INK, 'start', bold=True))
    f.append(rect(60, 65, 640, 140, fill='#fcfcfc', stroke='#cccccc', sw=1.2, rx=6))

    # Cable circuit elements
    for x in range(120, 600, 110):
        # Axial resistor (r_i)
        f.append(line(x, 90, x + 40, 90, color=POS, sw=2.0))
        f.append(rect(x + 40, 83, 30, 14, fill='#fdecea', stroke=POS, sw=1.2, rx=2))
        f.append(text(x + 55, 94, 'rᵢ', 10, POS, 'middle', bold=True))
        f.append(line(x + 70, 90, x + 110, 90, color=POS, sw=2.0))

        # Transmembrane resistor (r_m) and capacitor (c_m)
        cx = x + 55
        f.append(line(cx, 97, cx, 120, color=INK, sw=1.5))
        f.append(rect(cx - 10, 120, 20, 28, fill='#eef4fb', stroke=NEG, sw=1.2, rx=2))
        f.append(text(cx, 137, 'rₘ', 10, NEG, 'middle', bold=True))
        f.append(line(cx, 148, cx, 175, color=INK, sw=1.5))

        # Parallel capacitor c_m
        cap_x = cx + 25
        f.append(line(cx, 110, cap_x, 110, color=MUTED, sw=1.2))
        f.append(line(cap_x, 110, cap_x, 130, color=MUTED, sw=1.2))
        f.append(line(cap_x - 8, 130, cap_x + 8, 130, color=FIELD, sw=2.0))
        f.append(line(cap_x - 8, 136, cap_x + 8, 136, color=FIELD, sw=2.0))
        f.append(line(cap_x, 136, cap_x, 155, color=MUTED, sw=1.2))
        f.append(line(cap_x, 155, cx, 155, color=MUTED, sw=1.2))
        f.append(text(cap_x + 12, 136, 'cₘ', 10, FIELD, 'start'))

    # Extracellular return line
    f.append(line(120, 175, 600, 175, color=NEG, sw=2.0))

    # Lower Panel: Myelinated Axon (Saltatory Conduction)
    f.append(text(60, 230, 'Б. Мієлінізоване волокно: сальтаторний стрибок (до 120 м/с)', 13, INK, 'start', bold=True))
    f.append(rect(60, 240, 640, 140, fill='#fafafa', stroke='#cccccc', sw=1.2, rx=6))

    # Axon core
    f.append(rect(80, 290, 600, 35, fill='#fdf2f0', stroke=POS, sw=1.5, rx=4))
    f.append(text(95, 312, 'Аксоплазма', 12, POS, 'start', bold=True))

    # Myelin sheaths and Nodes of Ranvier
    sheath_blocks = [(170, 130), (340, 130), (510, 130)]
    for sx, sw_len in sheath_blocks:
        # Top myelin block
        f.append(rect(sx, 268, sw_len, 22, fill='#fcf0d8', stroke='#e67e22', sw=1.4, rx=4))
        f.append(text(sx + sw_len / 2, 283, 'Мієлінова оболонка (Шваннівська клітина)', 10, '#d35400', 'middle'))
        # Bottom myelin block
        f.append(rect(sx, 325, sw_len, 22, fill='#fcf0d8', stroke='#e67e22', sw=1.4, rx=4))

    # Nodes of Ranvier labels and jump arcs
    nodes = [160, 310, 480, 650]
    for nx in nodes:
        f.append(line(nx, 260, nx, 350, color=FIELD, sw=1.5, dash='2,2'))
        f.append(text(nx, 365, 'Вузол Ранв\'є', 10, FIELD, 'middle', bold=True))

    # Saltatory jump arcs
    for i in range(len(nodes) - 1):
        x1, x2 = nodes[i], nodes[i + 1]
        mx = (x1 + x2) / 2
        f.append(path('M %d,260 Q %d,235 %d,260' % (x1, mx, x2), color=POS, sw=2.5))
        f.append(arrow(mx, 247, mx + 15, 248, color=POS, sw=1.5))

    # Bottom summary box
    f.append(fitbox(60, 392, 640, 38,
                    'Мієлін збільшує товщину оболонки → ємність cₘ падає в 100 разів, опір rₘ зростає.\n'
                    'Потенціал дії не повзе безперервно, а стрибає між вузлами Ранв\'є (сальтаторно).',
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'cable-propagation.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Cardiac equivalent dipole vector in volume conductor (ECG)
# ═══════════════════════════════════════════════════════════════════════════
def fig_volume_conductor_dipole():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Біоелектричний диполь серця в об\'ємному провіднику', 17, INK, 'middle', bold=True))

    # Left torso region panel
    f.append(rect(60, 60, 320, 300, fill='#f4f8fd', stroke='#b0c4de', sw=1.4, rx=12))
    f.append(text(220, 82, 'Об\'ємний провідник (тканини тіла)', 12, MUTED, 'middle'))

    # Heart position and cardiac dipole vector
    hx, hy = 220, 195
    f.append(circle(hx, hy, 32, fill='#fdecea', stroke=POS, sw=1.8))
    f.append(text(hx, hy - 6, 'Серце', 12, POS, 'middle', bold=True))

    # Dipole vector P(t)
    f.append(arrow(hx - 15, hy - 15, hx + 25, hy + 25, color=POS, sw=2.8))
    f.append(text(hx + 30, hy + 35, 'Диполь P(t)', 11, POS, 'start', bold=True))

    # Dipole field lines spreading through volume conductor
    f.append(path('M 205,180 C 140,115 140,275 205,210', color=FIELD, sw=1.4, dash='4,4'))
    f.append(path('M 235,210 C 300,275 300,115 235,180', color=FIELD, sw=1.4, dash='4,4'))
    f.append(text(125, 195, 'струми J', 11, FIELD, 'middle'))

    # Einthoven electrodes (RA, LA, LL) - rendered as circles with text labels beside them to avoid box overlap
    rax, ray = 90, 110
    lax, lay = 340, 110
    llx, lly = 220, 335

    f.append(circle(rax, ray, 10, fill='#f3d9d6', stroke=POS, sw=1.5))
    f.append(text(rax, ray + 3, 'RA', 10, POS, 'middle', bold=True))

    f.append(circle(lax, lay, 10, fill='#d9e2f6', stroke=NEG, sw=1.5))
    f.append(text(lax, lay + 3, 'LA', 10, NEG, 'middle', bold=True))

    f.append(circle(llx, lly, 10, fill='#d9e2f6', stroke=NEG, sw=1.5))
    f.append(text(llx, lly + 3, 'LL', 10, NEG, 'middle', bold=True))

    # Einthoven Triangle dashed lines
    f.append(line(rax, ray, lax, lay, color=INK, sw=1.4, dash='3,3'))
    f.append(line(rax, ray, llx, lly, color=INK, sw=1.4, dash='3,3'))
    f.append(line(lax, lay, llx, lly, color=INK, sw=1.4, dash='3,3'))
    f.append(text(215, 103, 'Відведення I', 11, INK, 'middle', bold=True))

    # Right Panel: Output ECG Signal Waveform
    f.append(rect(410, 60, 310, 300, fill='#ffffff', stroke=LINE, sw=1.4, rx=6))
    f.append(text(565, 85, 'Запис відведення I (ЕКГ)', 13, INK, 'middle', bold=True))

    # ECG grid lines
    for yg in range(120, 340, 40):
        f.append(line(420, yg, 710, yg, color='#eeeeee', sw=1.0))
    for xg in range(440, 700, 45):
        f.append(line(xg, 100, xg, 340, color='#eeeeee', sw=1.0))

    # ECG waveform path
    ecg_p = ('M 420,220 L 460,220 Q 470,205 480,220 L 500,220 '
             'L 508,235 L 518,130 L 528,255 L 536,220 '
             'L 570,220 Q 595,185 620,220 L 710,220')
    f.append(path(ecg_p, color=POS, sw=2.5))

    # ECG Wave Annotations
    f.append(text(475, 195, 'P', 12, INK, 'middle', bold=True))
    f.append(text(518, 118, 'R', 13, POS, 'middle', bold=True))
    f.append(text(505, 250, 'Q', 11, INK, 'middle', bold=True))
    f.append(text(533, 268, 'S', 11, INK, 'middle', bold=True))
    f.append(text(595, 175, 'T', 12, INK, 'middle', bold=True))

    # Bottom summary box
    f.append(fitbox(60, 375, 660, 36,
                    'Сумарна деполяризація міокарда утворює обертовий дипольний вектор P(t).\n'
                    'Поверхневі електроди на шкірі вимірюють проекцію диполя на вектор відведення V_I(t).',
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'volume-conductor-dipole.svg'), W, H, *f)


def main():
    fig_membrane_capacitor()
    fig_action_potential_cycle()
    fig_cable_propagation()
    fig_volume_conductor_dipole()


if __name__ == '__main__':
    main()
