# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Palette
CORE_BG  = "#eaf2fb"
CLAD_BG  = "#f4f6f8"
SUB_BG   = "#e2e8f0"
SILICON  = "#3b82f6"
OXIDE    = "#94a3b8"
GOLD     = "#f59e0b"
TE0_COLOR = "#2563eb"
TE1_COLOR = "#dc2626"
TE2_COLOR = "#16a34a"

# ═══════════════════════════════════════════════════════════════════════════
# Fig 1: waveguide-structures.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_waveguide_structures():
    W, H = 820, 480
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 28, "Класифікація геометрій інтегральних оптичних хвилеводів", 16, INK, "middle", bold=True))

    def draw_cell(x, y, w, h, title, sub):
        frags.append(rect(x, y, w, h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(x + w / 2, y + 22, title, 13, INK, "middle", bold=True))
        frags.append(text(x + w / 2, y + 38, sub, 11, MUTED, "middle", italic=True))

    # 1. Slab (Planar) Waveguide
    x1, y1, w1, h1 = 20, 60, 245, 185
    draw_cell(x1, y1, w1, h1, "Плоский (Slab) хвилевід", "1D утримання світла")
    frags.append(rect(x1 + 20, y1 + 130, 205, 40, fill=OXIDE, stroke=LINE, sw=1, rx=0))
    frags.append(text(x1 + 122, y1 + 154, "Підкладка n₃", 11, INK, "middle"))
    frags.append(rect(x1 + 20, y1 + 90, 205, 40, fill=SILICON, stroke=LINE, sw=1.2, rx=0))
    frags.append(text(x1 + 122, y1 + 114, "Серцевина n₁ (n₁ > n₂, n₃)", 11, BG, "middle", bold=True))
    frags.append(rect(x1 + 20, y1 + 50, 205, 40, fill=CLAD_BG, stroke=LINE, sw=1, rx=0))
    frags.append(text(x1 + 122, y1 + 74, "Покриття n₂", 11, MUTED, "middle"))

    # 2. Strip / Channel Waveguide
    x2, y2, w2, h2 = 285, 60, 245, 185
    draw_cell(x2, y2, w2, h2, "Смужковий (Strip) хвилевід", "2D високий контраст (SOI)")
    frags.append(rect(x2 + 20, y2 + 130, 205, 40, fill=OXIDE, stroke=LINE, sw=1, rx=0))
    frags.append(text(x2 + 122, y2 + 154, "Підкладка SiO₂ (n₃=1.45)", 11, INK, "middle"))
    frags.append(rect(x2 + 20, y2 + 50, 205, 80, fill=CLAD_BG, stroke=LINE, sw=1, rx=0))
    frags.append(rect(x2 + 97, y2 + 90, 50, 40, fill=SILICON, stroke=LINE, sw=1.5, rx=0))
    frags.append(text(x2 + 122, y2 + 114, "Si (3.45)", 10, BG, "middle", bold=True))
    frags.append(text(x2 + 122, y2 + 72, "Оболонка SiO₂", 10, MUTED, "middle"))

    # 3. Rib / Ridge Waveguide
    x3, y3, w3, h3 = 550, 60, 250, 185
    draw_cell(x3, y3, w3, h3, "Реберний (Rib) хвилевід", "Низькі втрати на шорсткість")
    frags.append(rect(x3 + 20, y3 + 130, 210, 40, fill=OXIDE, stroke=LINE, sw=1, rx=0))
    frags.append(text(x3 + 125, y3 + 154, "Підкладка SiO₂", 11, INK, "middle"))
    frags.append(rect(x3 + 20, y3 + 50, 210, 80, fill=CLAD_BG, stroke=LINE, sw=1, rx=0))
    points = [
        (x3 + 40, y3 + 130),
        (x3 + 40, y3 + 115),
        (x3 + 95, y3 + 115),
        (x3 + 95, y3 + 80),
        (x3 + 155, y3 + 80),
        (x3 + 155, y3 + 115),
        (x3 + 210, y3 + 115),
        (x3 + 210, y3 + 130)
    ]
    pts_str = " ".join(["%.1f,%.1f" % p for p in points])
    frags.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5" />' % (pts_str, SILICON, LINE))
    frags.append(text(x3 + 125, y3 + 102, "Ребро Si", 11, BG, "middle", bold=True))

    # 4. Slot Waveguide
    x4, y4, w4, h4 = 20, 265, 380, 195
    draw_cell(x4, y4, w4, h4, "Щілинний (Slot) хвилевід", "Локалізація світла у вузькій щілині (<100 нм)")
    frags.append(rect(x4 + 20, y4 + 135, 340, 40, fill=OXIDE, stroke=LINE, sw=1, rx=0))
    frags.append(text(x4 + 190, y4 + 159, "Оксидна підкладка SiO₂", 11, INK, "middle"))
    frags.append(rect(x4 + 20, y4 + 50, 340, 85, fill=CLAD_BG, stroke=LINE, sw=1, rx=0))
    frags.append(rect(x4 + 110, y4 + 75, 60, 60, fill=SILICON, stroke=LINE, sw=1.2, rx=0))
    frags.append(rect(x4 + 210, y4 + 75, 60, 60, fill=SILICON, stroke=LINE, sw=1.2, rx=0))
    frags.append(rect(x4 + 170, y4 + 75, 40, 60, fill="#fef08a", stroke="#eab308", sw=1.5, rx=0))
    frags.append(text(x4 + 140, y4 + 110, "Si рейка", 10, BG, "middle", bold=True))
    frags.append(text(x4 + 240, y4 + 110, "Si рейка", 10, BG, "middle", bold=True))
    frags.append(text(x4 + 190, y4 + 65, "Щілина (n_low)", 10, POS, "middle", bold=True))

    # 5. Photonic Crystal Waveguide
    x5, y5, w5, h5 = 420, 265, 380, 195
    draw_cell(x5, y5, w5, h5, "Фотоно-кристалічний хвилевід (PhCW)", "Дефект у періодичній матриці отворів")
    frags.append(rect(x5 + 20, y5 + 50, 340, 125, fill=SILICON, stroke=LINE, sw=1.2, rx=4))
    for ry in [y5 + 65, y5 + 85, y5 + 145, y5 + 165]:
        for rx in range(x5 + 40, x5 + 340, 30):
            frags.append('<circle cx="%d" cy="%d" r="7" fill="%s" stroke="%s" stroke-width="1" />' % (rx, ry, BG, LINE))
    frags.append(line(x5 + 30, y5 + 115, x5 + 100, y5 + 115, color=FIELD, sw=3, dash="4,2"))
    frags.append(line(x5 + 280, y5 + 115, x5 + 350, y5 + 115, color=FIELD, sw=3, dash="4,2"))
    frags.append(text(x5 + 190, y5 + 119, "Оптичний канал-дефект W1", 11, BG, "middle", bold=True))
    frags.append(text(x5 + 190, y5 + 183, "Заборонена фотонна зона блокує вихід світла", 10, MUTED, "middle"))

    with open(os.path.join(IMG, 'waveguide-structures.svg'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        f.write("\n".join(frags))
        f.write('\n</svg>\n')

# ═══════════════════════════════════════════════════════════════════════════
# Fig 2: slab-mode-profiles.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_mode_profiles():
    W, H = 780, 440
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 28, "Профілі поперечного електричного поля E_y(x) для TE мод", 16, INK, "middle", bold=True))

    cx = 100
    w_plot = 620
    d_core = 180
    x_left = cx + (w_plot - d_core) / 2
    x_right = x_left + d_core

    frags.append(rect(cx, 60, (w_plot - d_core) / 2, 330, fill=CLAD_BG, stroke='none', rx=0))
    frags.append(rect(x_left, 60, d_core, 330, fill=CORE_BG, stroke='none', rx=0))
    frags.append(rect(x_right, 60, (w_plot - d_core) / 2, 330, fill=CLAD_BG, stroke='none', rx=0))

    frags.append(line(x_left, 55, x_left, 395, color=LINE, sw=1.5, dash="4,4"))
    frags.append(line(x_right, 55, x_right, 395, color=LINE, sw=1.5, dash="4,4"))

    frags.append(text(x_left, 398, "x = -d/2", 11, INK, "middle"))
    frags.append(text(x_right, 398, "x = +d/2", 11, INK, "middle"))
    frags.append(text(cx + (w_plot - d_core) / 4, 75, "Оболонка (n₂)", 12, MUTED, "middle", bold=True))
    frags.append(text(x_left + d_core / 2, 75, "Серцевина хвилеводу (n₁)", 13, INK, "middle", bold=True))
    frags.append(text(x_right + (w_plot - d_core) / 4, 75, "Оболонка (n₂)", 12, MUTED, "middle", bold=True))

    y0 = 130
    y1 = 230
    y2 = 330

    frags.append(line(cx - 20, y0, cx + w_plot + 20, y0, color="#cbd5e1", sw=1))
    frags.append(line(cx - 20, y1, cx + w_plot + 20, y1, color="#cbd5e1", sw=1))
    frags.append(line(cx - 20, y2, cx + w_plot + 20, y2, color="#cbd5e1", sw=1))

    frags.append(text(cx - 30, y0 + 4, "TE₀", 14, TE0_COLOR, "end", bold=True))
    frags.append(text(cx - 30, y1 + 4, "TE₁", 14, TE1_COLOR, "end", bold=True))
    frags.append(text(cx - 30, y2 + 4, "TE₂", 14, TE2_COLOR, "end", bold=True))

    def curve_to_path(pts):
        d = ["M %.1f,%.1f" % pts[0]]
        for p in pts[1:]:
            d.append("L %.1f,%.1f" % p)
        return " ".join(d)

    pts_te0 = []
    amp0 = 45
    h0 = math.pi / d_core
    q0 = 0.025
    for px in range(int(cx), int(cx + w_plot) + 1):
        x_val = px - (x_left + d_core / 2)
        if abs(x_val) <= d_core / 2:
            val = amp0 * math.cos(h0 * x_val)
        elif x_val > d_core / 2:
            val = amp0 * math.cos(h0 * d_core / 2) * math.exp(-q0 * (x_val - d_core / 2))
        else:
            val = amp0 * math.cos(h0 * d_core / 2) * math.exp(-q0 * (-x_val - d_core / 2))
        pts_te0.append((px, y0 - val))

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" />' % (curve_to_path(pts_te0), TE0_COLOR))

    pts_te1 = []
    amp1 = 40
    h1 = 2.0 * math.pi / d_core
    q1 = 0.02
    for px in range(int(cx), int(cx + w_plot) + 1):
        x_val = px - (x_left + d_core / 2)
        if abs(x_val) <= d_core / 2:
            val = amp1 * math.sin(h1 * x_val)
        elif x_val > d_core / 2:
            val = amp1 * math.sin(h1 * d_core / 2) * math.exp(-q1 * (x_val - d_core / 2))
        else:
            val = -amp1 * math.sin(h1 * d_core / 2) * math.exp(-q1 * (-x_val - d_core / 2))
        pts_te1.append((px, y1 - val))

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" />' % (curve_to_path(pts_te1), TE1_COLOR))

    pts_te2 = []
    amp2 = 38
    h2 = 2.8 * math.pi / d_core
    q2 = 0.015
    for px in range(int(cx), int(cx + w_plot) + 1):
        x_val = px - (x_left + d_core / 2)
        if abs(x_val) <= d_core / 2:
            val = amp2 * math.cos(h2 * x_val)
        elif x_val > d_core / 2:
            val = amp2 * math.cos(h2 * d_core / 2) * math.exp(-q2 * (x_val - d_core / 2))
        else:
            val = amp2 * math.cos(h2 * d_core / 2) * math.exp(-q2 * (-x_val - d_core / 2))
        pts_te2.append((px, y2 - val))

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" />' % (curve_to_path(pts_te2), TE2_COLOR))

    frags.append(text(cx + 35, y0 - 15, "Зникаючі хвости", 10, MUTED, "start", italic=True))
    frags.append(line(cx + 40, y0 - 10, cx + 80, y0 - 5, color=MUTED, sw=1, dash="2,2"))

    frags.append(text(W / 2, 422, "Моди вищого порядку мають ширші зникаючі поля та нижчий ефективний показник n_eff", 12, INK, "middle", italic=True))

    with open(os.path.join(IMG, 'slab-mode-profiles.svg'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        f.write("\n".join(frags))
        f.write('\n</svg>\n')

# ═══════════════════════════════════════════════════════════════════════════
# Fig 3: mzi-modulator-photonic.svg
# ═══════════════════════════════════════════════════════════════════════════
def fig_mzi_modulator():
    W, H = 840, 420
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    frags.append(text(W / 2, 28, "Інтегральний фотонний модулятор Маха-Цендера (MZI) на SOI", 16, INK, "middle", bold=True))

    # Silicon chip background
    frags.append(rect(30, 55, 780, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(45, 75, "Кремнієвий чип (SOI)", 12, MUTED, "start", bold=True))

    # Input waveguide
    y_center = 200
    frags.append(rect(50, y_center - 8, 110, 16, fill=SILICON, stroke=LINE, sw=1, rx=0))
    frags.append(text(55, y_center - 15, "Оптичний вхід P_in", 11, INK, "start", bold=True))

    # 50:50 Directional Coupler / Y-splitter
    p_split_top = "M 160,200 C 210,200 230,120 280,120 L 540,120 C 590,120 610,200 660,200"
    p_split_bot = "M 160,200 C 210,200 230,280 280,280 L 540,280 C 590,280 610,200 660,200"

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="14" stroke-linecap="round" />' % (p_split_top, SILICON))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="14" stroke-linecap="round" />' % (p_split_bot, SILICON))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1" />' % (p_split_top, LINE))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1" />' % (p_split_bot, LINE))

    # Labels placed in middle between the arms (y=200)
    frags.append(text(210, 204, "50:50 Розділювач", 11, INK, "middle", bold=True))
    frags.append(text(630, 204, "50:50 Змішувач", 11, INK, "middle", bold=True))

    # Arm 1: Active Phase Shifter
    frags.append(rect(340, 95, 140, 50, fill="#fef3c7", stroke=GOLD, sw=1.8, rx=4))
    frags.append(text(410, 116, "Фазообертач Δφ", 12, INK, "middle", bold=True))
    frags.append(text(410, 134, "PN-перехід / Нагрівач", 10, POS, "middle"))

    # Arm 2: Reference
    frags.append(text(410, 305, "Опорне плече L", 11, MUTED, "middle", italic=True))

    # Electrical Control Signal
    frags.append(line(410, 60, 410, 95, color=POS, sw=2))
    frags.append('<circle cx="410" cy="60" r="4" fill="%s" />' % POS)
    frags.append(text(410, 55, "Електричний сигнал V(t)", 11, POS, "middle", bold=True))

    # Output waveguide
    frags.append(rect(660, y_center - 8, 120, 16, fill=SILICON, stroke=LINE, sw=1, rx=0))
    frags.append(text(775, y_center - 15, "Оптичний вихід P_out", 11, INK, "end", bold=True))

    # Interference equation text
    frags.append(text(420, 360, "P_out = P_in · cos²(Δφ / 2),   де Δφ = π · V / V_π", 12, INK, "middle", bold=True))

    with open(os.path.join(IMG, 'mzi-modulator-photonic.svg'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        f.write("\n".join(frags))
        f.write('\n</svg>\n')

if __name__ == "__main__":
    fig_waveguide_structures()
    fig_mode_profiles()
    fig_mzi_modulator()
    print("Figures generated successfully in img/")
