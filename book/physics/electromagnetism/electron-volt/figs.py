# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Acceleration of an electron in a 1 V electric field
# ═══════════════════════════════════════════════════════════════════════════
def fig_acceleration():
    W, H = 660, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    f.append(text(W / 2, 32, 'Прискорення електрона у різниці потенціалів 1 В',
                  16, INK, 'middle', bold=True))

    # Capacitor plates
    # Left plate (Cathode, 0 V)
    f.append(rect(90, 75, 18, 200, fill='#eaf0fd', stroke=NEG, sw=2, rx=3))
    f.append(text(99, 62, 'Катод (0 В)', 13, NEG, 'middle', bold=True))

    # Right plate (Anode, +1 В)
    f.append(rect(470, 75, 18, 200, fill='#fdecea', stroke=POS, sw=2, rx=3))
    f.append(text(479, 62, 'Анод (+1 В)', 13, POS, 'middle', bold=True))

    # Electric field lines E (pointing right to left)
    for y in [105, 145, 185, 225, 255]:
        f.append(arrow(460, y, 115, y, color=MUTED, sw=1.5))
    f.append(text(290, 95, 'Електричне поле E', 12, MUTED, 'middle', italic=True))

    # Trajectory of electron
    f.append(line(125, 175, 450, 175, color=LINE, sw=1.8, dash='6,4'))

    # Initial state electron
    f.append(circle(145, 175, 12, fill='#eaf0fd', stroke=NEG, sw=2))
    f.append(text(145, 179, 'e⁻', 13, NEG, 'middle', bold=True))
    f.append(text(145, 205, 'v = 0', 12, MUTED, 'middle'))
    f.append(text(145, 222, 'Eₖ = 0', 12, MUTED, 'middle'))

    # Acceleration force arrow
    f.append(arrow(165, 175, 240, 175, color=POS, sw=2.5))
    f.append(text(202, 162, 'Сила F = e·E', 12, POS, 'middle', bold=True))

    # Accelerated state electron near anode
    f.append(circle(435, 175, 12, fill='#fdecea', stroke=POS, sw=2))
    f.append(text(435, 179, 'e⁻', 13, POS, 'middle', bold=True))
    f.append(arrow(450, 175, 495, 175, color=POS, sw=2))
    f.append(text(435, 205, 'v ≈ 5.93 × 10⁵ м/с', 12, INK, 'middle', bold=True))
    f.append(text(435, 224, 'Eₖ = 1 еВ', 13, POS, 'middle', bold=True))

    # Potential difference marker at top
    f.append(line(99, 285, 479, 285, color=INK, sw=1.4))
    f.append(line(99, 280, 99, 290, color=INK, sw=1.4))
    f.append(line(479, 280, 479, 290, color=INK, sw=1.4))
    f.append(text(289, 280, 'Різниця потенціалів ΔV = 1 В', 13, INK, 'middle', bold=True))

    # Summary box at bottom
    f.append(fitbox(50, 308, 560, 55,
                    'Набута кінетична енергія: Eₖ = q · ΔV = e · 1 В = 1.602 176 634 × 10⁻¹⁹ Дж ≡ 1 еВ\n'
                    'Робота поля не залежить від траєкторії чи відстані між електродами, а лише від різниці потенціалів.',
                    size=12, color=INK, fill='#f4f6f8', stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'acceleration.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Energy scale ladder across physics domains
# ═══════════════════════════════════════════════════════════════════════════
def fig_energy_scales():
    W, H = 720, 390
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    f.append(text(W / 2, 30, 'Драбина енергетичних масштабів в електронвольтах',
                  16, INK, 'middle', bold=True))

    # Axis y
    ay = 95
    f.append(line(40, ay, W - 30, ay, color=INK, sw=1.8))
    f.append(arrow(W - 40, ay, W - 20, ay, color=INK, sw=1.8))
    f.append(text(W - 15, ay + 5, 'E', 15, INK, 'start', italic=True))

    # Ticks for orders of magnitude
    domains = [
        (70,  '10⁻³ еВ', 'меВ',   'Теплі коливання\nгратки (25 меВ),\nТГц-імпліцит'),
        (180, '1 еВ',    'еВ',    'Валентні e⁻,\nоптичні фотони,\nзони (Si 1.1 еВ)'),
        (290, '10³ еВ',  'кеВ',   'K-атомні переходи,\nрентгенівські фотони,\nпромені ЕПТ'),
        (400, '10⁶ еВ',  'МеВ',   'Ядерні реакції,\nенергія зв’язку,\nмаса e⁻ (0.511 МеВ)'),
        (510, '10⁹ еВ',  'ГеВ',   'Маса p⁺ (0.938 ГеВ),\nсубатомний розпад,\nприскорювачі'),
        (620, '10¹² еВ', 'ТеВ',   'Адронний коллайдер\n(13.6 ТеВ), космічні\nпромені надвисоких E'),
    ]

    for x, val_str, unit_str, desc in domains:
        f.append(line(x, ay - 8, x, ay + 8, color=POS, sw=2))
        f.append(text(x, ay - 16, val_str, 12, POS, 'middle', bold=True))
        f.append(text(x, ay + 24, unit_str, 12, INK, 'middle', bold=True))

        # Box below with description
        f.append(fitbox(x - 50, ay + 38, 100, 210, desc, size=11, pad=6, color=INK, fill='#f4f6f8', stroke=MUTED, sw=1.2))

    # Summary text at the very bottom
    f.append(fitbox(40, 350, 640, 32,
                    'Один електронвольт покриває 15 порядків величини — від термодинаміки до фізики частинок.',
                    size=11, color=INK, fill='#eef7f0', stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'energy-scales.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Classical vs Relativistic Velocity of Electron
# ═══════════════════════════════════════════════════════════════════════════
def fig_relativistic_speed():
    W, H = 660, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    f.append(text(W / 2, 32, 'Залежність швидкості електрона v/c від кінетичної енергії Eₖ',
                  16, INK, 'middle', bold=True))

    # Axes setup
    ox, oy = 80, 300
    gw, gh = 520, 220

    # Axes lines
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.6)) # X axis
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.6)) # Y axis
    f.append(arrow(ox, oy - gh, ox, oy - gh - 15, color=INK, sw=1.6))
    f.append(arrow(ox + gw, oy, ox + gw + 15, oy, color=INK, sw=1.6))

    f.append(text(ox + gw + 20, oy + 5, 'Eₖ', 14, INK, 'start', bold=True, italic=True))
    f.append(text(ox - 10, oy - gh - 20, 'v / c', 14, INK, 'middle', bold=True, italic=True))

    # Speed of light asymptote v/c = 1
    y_c = oy - 190
    f.append(line(ox, y_c, ox + gw, y_c, color=POS, sw=1.4, dash='5,4'))
    f.append(text(ox + gw - 10, y_c - 8, 'Межа швидкості світла (v = c)', 12, POS, 'end', bold=True))

    # Grid & X Ticks
    f.append(text(ox - 12, oy + 5, '0', 12, MUTED, 'end'))
    f.append(line(ox - 5, oy - 95, ox + gw, oy - 95, color='#eef0f2', sw=1))
    f.append(text(ox - 12, oy - 91, '0.5', 12, MUTED, 'end'))
    f.append(line(ox - 5, oy - 164, ox + gw, oy - 164, color='#eef0f2', sw=1))
    f.append(text(ox - 12, oy - 160, '0.866', 12, MUTED, 'end'))
    f.append(text(ox - 12, y_c + 4, '1.0', 12, POS, 'end', bold=True))

    # X ticks
    x_ticks = [
        (100, '1 еВ'),
        (220, '10 кеВ'),
        (340, '100 кеВ'),
        (430, '511 кеВ'),
        (570, '10 МеВ')
    ]
    for x, label in x_ticks:
        f.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.4))
        f.append(text(x, oy + 22, label, 12, INK, 'middle'))

    # Classical curve: v/c = sqrt(2 E_k / m c^2)
    pts_class = [(80, oy), (100, oy - 1), (220, oy - 38), (340, oy - 119), (410, oy - 190)]
    path_class = 'M ' + ' L '.join(['%.1f,%.1f' % (px, py) for px, py in pts_class])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (path_class, NEG))

    # Place classical label in upper left clear area
    f.append(text(120, oy - 130, 'Ньютонівська механіка (v ∝ √Eₖ)', 11, NEG, 'start', italic=True))

    # Relativistic curve: v/c = sqrt(1 - 1/(1 + E/mc^2)^2)
    pts_rel = [(80, oy), (100, oy - 1), (220, oy - 37), (340, oy - 104), (430, oy - 164), (480, oy - 179), (570, oy - 189.8)]
    path_rel = 'M ' + ' L '.join(['%.1f,%.1f' % (px, py) for px, py in pts_rel])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path_rel, FIELD))

    # Place relativistic label clear of lines
    f.append(text(440, oy - 70, 'Релятивістська фізика (Ейнштейн)', 12, FIELD, 'start', bold=True))

    # Point at 511 keV (m_e c^2)
    f.append(circle(430, oy - 164, 6, fill='#ffffff', stroke=POS, sw=2.2))
    f.append(line(430, oy - 164, 430, oy, color=POS, sw=1, dash='3,3'))
    f.append(text(430, oy - 176, 'Eₖ = mₑ c² (γ = 2, v = 0.866 c)', 11, POS, 'middle', bold=True))

    # Legend at bottom
    f.append(fitbox(90, 328, 500, 42,
                    'При Eₖ << mₑ c² (до кількох кеВ) класична та релятивістська формули збігаються.\n'
                    'При Eₖ ≥ 511 кеВ класична механіка дає хибну швидкість v > c, а реальна швидкість асимптотично прямує до c.',
                    size=11, color=INK, fill='#f4f6f8', stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'relativistic-speed.svg'), W, H, *f)


fig_acceleration()
fig_energy_scales()
fig_relativistic_speed()
print('Figures generated successfully.')
