# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def ang(a):
    return math.radians(a)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Механізм релеєвського розсіяння (осцилювальний диполь)
# ═══════════════════════════════════════════════════════════════════════════
def fig_rayleigh_dipole_scattering():
    W, H = 740, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Фізичний механізм релеєвського розсіяння світла', 16, INK, 'middle', bold=True))

    cx, cy = 340, 210

    # Світлова хвиля падає зліва вздовж осі X
    wave_pts = []
    for x in range(60, 240, 4):
        y = cy - 25 * math.sin((x - 60) * 0.08)
        wave_pts.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(wave_pts)}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    f.append(arrow(220, cy, 270, cy, color=NEG, sw=2.5))
    f.append(text(140, cy - 35, 'падаюче світло (λ)', 12, NEG, 'middle', bold=True))

    # Частинка в центрі (розмір a << λ)
    f.append(circle(cx, cy, 18, fill='#e0f2fe', stroke=NEG, sw=2))
    f.append(text(cx, cy + 4, 'a ≪ λ', 10, INK, 'middle', bold=True))

    # Осцилювальний диполь (двостороння вертикальна стрілка p = α E)
    f.append(line(cx, cy - 45, cx, cy + 45, color=POS, sw=2.5, dash='4,3'))
    f.append(arrow(cx, cy - 20, cx, cy - 48, color=POS, sw=2.5))
    f.append(arrow(cx, cy + 20, cx, cy + 48, color=POS, sw=2.5))
    f.append(text(cx + 25, cy - 35, 'p(t) = α · E(t)', 11, POS, 'start', bold=True))

    # Діаграма випромінювання диполя
    lobes_pts = []
    num_pts = 120
    R_scale = 110.0
    for i in range(num_pts + 1):
        a_deg = i * 360.0 / num_pts
        rad = math.radians(a_deg)
        r_val = R_scale * 0.45 * (1.0 + math.cos(rad)**2)
        px = cx + r_val * math.cos(rad)
        py = cy - r_val * math.sin(rad)
        lobes_pts.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polygon points="{" ".join(lobes_pts)}" fill="#f0fdf4" stroke="{FIELD}" stroke-width="1.8" stroke-dasharray="6,4"/>')

    # Напрямки розсіяння:
    f.append(arrow(cx + 30, cy, cx + 180, cy, color=FIELD, sw=2))
    f.append(text(cx + 185, cy + 4, 'θ = 0° (вперед)', 11, FIELD, 'start', bold=True))

    f.append(arrow(cx - 30, cy, cx - 180, cy, color=FIELD, sw=2))
    f.append(text(cx - 185, cy + 4, 'θ = 180° (назад)', 11, FIELD, 'end', bold=True))

    f.append(arrow(cx, cy - 30, cx, cy - 130, color=POS, sw=2))
    f.append(text(cx + 10, cy - 110, 'θ = 90° (100% поляризація)', 11, POS, 'start', bold=True))
    f.append(circle(cx, cy - 80, 6, fill=BG, stroke=POS, sw=1.5))
    f.append(circle(cx, cy - 80, 2, fill=POS, stroke=POS, sw=1))

    # Кут θ позначка
    arc_pts = []
    for deg in range(0, 91, 5):
        rad = math.radians(deg)
        ax = cx + 45 * math.cos(rad)
        ay = cy - 45 * math.sin(rad)
        arc_pts.append(f"{ax:.1f},{ay:.1f}")
    f.append(f'<polyline points="{" ".join(arc_pts)}" fill="none" stroke="{MUTED}" stroke-width="1.2"/>')
    f.append(text(cx + 52, cy - 20, 'θ', 12, MUTED, 'middle', bold=True, italic=True))

    # Інформаційний блок
    f.append(fitbox(520, 310, 200, 95,
                    'Інтенсивність розсіяння:\n'
                    'I(θ) ∝ (1 + cos²θ) / λ⁴\n'
                    '• Короткі хвилі (сині) розсіюються сильніше\n'
                    '• Під θ = 90° світло повністю поляризоване',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'rayleigh-dipole-scattering.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Порівняння режимів розсіяння
# ═══════════════════════════════════════════════════════════════════════════
def fig_rayleigh_vs_mie():
    W, H = 750, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Режими розсіяння світла залежно від параметра розміру x = 2πa / λ', 15, INK, 'middle', bold=True))

    pw = 220
    ph = 300
    py = 55

    # Панель 1: Релеєвське
    px1 = 20
    f.append(rect(px1, py, pw, ph, fill='#fafafa', stroke=LINE, sw=1.2, rx=6))
    f.append(text(px1 + pw / 2, py + 22, 'Релеєвське розсіяння', 13, INK, 'middle', bold=True))
    f.append(text(px1 + pw / 2, py + 40, 'x = 2πa / λ ≪ 1  (a ≪ λ)', 11, POS, 'middle', bold=True))

    c1x, c1y = px1 + pw / 2, py + 150
    f.append(circle(c1x, c1y, 8, fill='#dbeafe', stroke=NEG, sw=1.5))
    f.append(text(c1x, c1y + 3, 'молекула', 9, INK, 'middle'))

    f.append(arrow(px1 + 15, c1y, c1x - 15, c1y, color=NEG, sw=2))

    r1_pts = []
    for i in range(121):
        deg = i * 3.0
        rad = math.radians(deg)
        r_val = 55.0 * 0.5 * (1.0 + math.cos(rad)**2)
        rx = c1x + r_val * math.cos(rad)
        ry = c1y - r_val * math.sin(rad)
        r1_pts.append(f"{rx:.1f},{ry:.1f}")
    f.append(f'<polygon points="{" ".join(r1_pts)}" fill="#f0fdf4" stroke="{FIELD}" stroke-width="1.5"/>')

    f.append(fitbox(px1 + 10, py + 215, pw - 20, 75,
                    'Симетричне випромінювання\n'
                    'вперед і назад.\n'
                    'I ∝ λ⁻⁴ (сильний колірний ефект).\n'
                    'Приклад: молекули N₂, O₂.',
                    size=9.5, color=INK, fill=BG, stroke=MUTED, sw=1))

    # Панель 2: Мі
    px2 = 265
    f.append(rect(px2, py, pw, ph, fill='#fafafa', stroke=LINE, sw=1.2, rx=6))
    f.append(text(px2 + pw / 2, py + 22, 'Розсіяння Мі', 13, INK, 'middle', bold=True))
    f.append(text(px2 + pw / 2, py + 40, 'x = 2πa / λ ≈ 0.1…10  (a ≈ λ)', 11, FIELD, 'middle', bold=True))

    c2x, c2y = px2 + pw / 2, py + 150
    f.append(circle(c2x, c2y, 22, fill='#fef3c7', stroke='#d97706', sw=1.5))
    f.append(text(c2x, c2y + 3, 'аерозоль', 9, INK, 'middle'))

    f.append(arrow(px2 + 15, c2y, c2x - 30, c2y, color=NEG, sw=2))

    r2_pts = []
    for i in range(121):
        deg = i * 3.0
        rad = math.radians(deg)
        r_val = 15.0 * math.exp(1.2 * math.cos(rad))
        rx = c2x + r_val * math.cos(rad)
        ry = c2y - r_val * math.sin(rad)
        r2_pts.append(f"{rx:.1f},{ry:.1f}")
    f.append(f'<polygon points="{" ".join(r2_pts)}" fill="#fefce8" stroke="#d97706" stroke-width="1.5"/>')

    f.append(fitbox(px2 + 10, py + 215, pw - 20, 75,
                    'Переважає розсіяння вперед.\n'
                    'Слабке залеження від λ\n'
                    '(білястий/білий колір).\n'
                    'Приклад: туман, хмари, пил.',
                    size=9.5, color=INK, fill=BG, stroke=MUTED, sw=1))

    # Панель 3: Геометрична оптика
    px3 = 510
    f.append(rect(px3, py, pw, ph, fill='#fafafa', stroke=LINE, sw=1.2, rx=6))
    f.append(text(px3 + pw / 2, py + 22, 'Геометрична оптика', 13, INK, 'middle', bold=True))
    f.append(text(px3 + pw / 2, py + 40, 'x = 2πa / λ ≫ 10  (a ≫ λ)', 11, NEG, 'middle', bold=True))

    c3x, c3y = px3 + pw / 2 - 20, py + 150
    f.append(circle(c3x, c3y, 35, fill='#e0e7ff', stroke=NEG, sw=1.8))
    f.append(text(c3x, c3y + 3, 'крапля', 9, INK, 'middle'))

    f.append(arrow(px3 + 15, c3y - 15, c3x - 32, c3y - 15, color=NEG, sw=2))
    f.append(arrow(c3x - 32, c3y - 15, px3 + 15, c3y - 45, color=POS, sw=1.8))
    f.append(line(c3x - 32, c3y - 15, c3x + 20, c3y + 10, color=FIELD, sw=1.8))
    f.append(arrow(c3x + 20, c3y + 10, px3 + pw - 15, c3y + 30, color=FIELD, sw=1.8))

    f.append(fitbox(px3 + 10, py + 215, pw - 20, 75,
                    'Чіткі заломлені й відбиті\n'
                    'промені, дифракційні смуги.\n'
                    'Незалежно від λ.\n'
                    'Приклад: дощові краплі (веселка).',
                    size=9.5, color=INK, fill=BG, stroke=MUTED, sw=1))

    render(os.path.join(IMG, 'rayleigh-vs-mie.svg'), W, H, *f)

if __name__ == '__main__':
    fig_rayleigh_dipole_scattering()
    fig_rayleigh_vs_mie()
    print("Figures generated successfully!")
