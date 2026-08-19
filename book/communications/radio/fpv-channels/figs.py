# -*- coding: utf-8 -*-
import os
import sys
import math

# Add root scripts/ to sys.path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_bands_spectrum_map(path):
    w, h = 820, 440
    frags = []
    
    # Outer panel
    frags.append(rect(15, 40, 790, 385, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    
    # Frequency axis definition: 5640 MHz to 5960 MHz (320 MHz span)
    f_min, f_max = 5640, 5960
    x_left, x_right = 75, 765
    scale = (x_right - x_left) / (f_max - f_min)
    
    def f2x(f):
        return x_left + (f - f_min) * scale

    # ISM Band Highlight Banner (5725 to 5875 MHz)
    ism_x1 = f2x(5725)
    ism_x2 = f2x(5875)
    frags.append(rect(ism_x1, 50, ism_x2 - ism_x1, 24, fill="#edf7ed", stroke="#2e7d32", sw=1.2, rx=4))
    frags.append(text((ism_x1 + ism_x2) / 2, 66, "Дозволений діапазон ISM (5725–5875 МГц)", size=11, color="#2e7d32", bold=True))

    # Frequency axis line at bottom
    axis_y = 385
    frags.append(arrow(x_left - 20, axis_y, x_right + 25, axis_y, color=LINE, sw=1.8))
    frags.append(text(x_right + 30, axis_y + 4, "f, МГц", size=11, color=INK, bold=True))

    # Grid ticks and labels (lines only between y=78 and y=310 so they don't intersect boxes)
    for f in range(5650, 5951, 50):
        gx = f2x(f)
        frags.append(line(gx, 78, gx, 310, color="#e5e7eb", sw=1.0, dash="3 3"))
        frags.append(line(gx, axis_y - 4, gx, axis_y + 4, color=LINE, sw=1.5))
        frags.append(text(gx, axis_y + 16, str(f), size=11, color=MUTED))

    # Bands definition
    bands = [
        ("Band A", [5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725], "#7c3aed", 95),
        ("Band B", [5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866], "#1d4ed8", 140),
        ("Band E", [5705, 5685, 5665, 5645, 5885, 5905, 5925, 5945], "#c2410c", 185),
        ("Band F", [5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880], "#047857", 230),
        ("Raceband", [5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917], "#b91c1c", 285),
    ]

    for band_name, freqs, col, y_pos in bands:
        # Band label on left
        frags.append(text(44, y_pos + 12, band_name, size=11, color=col, bold=True))
        
        # Channel markers
        for idx, f in enumerate(freqs):
            cx = f2x(f)
            if band_name == "Raceband":
                frags.append(rect(cx - 8, y_pos - 2, 16, 26, fill="#fee2e2", stroke=col, sw=1.5, rx=3))
                frags.append(text(cx, y_pos + 14, "R%d" % (idx + 1), size=9, color=col, bold=True))
            else:
                frags.append(rect(cx - 7, y_pos, 14, 20, fill="#ffffff", stroke=col, sw=1.2, rx=3))
                frags.append(text(cx, y_pos + 14, str(idx + 1), size=9, color=col, bold=True))

    # Spacing annotations for Band F vs Raceband
    # Band F 20MHz step
    f1_x = f2x(5740)
    f2_x = f2x(5760)
    frags.append(line(f1_x, 255, f2_x, 255, color="#047857", sw=1.2))
    frags.append(text((f1_x + f2_x)/2, 266, "Δf = 20 МГц", size=9, color="#047857", bold=True))

    # Raceband 37MHz step
    r1_x = f2x(5658)
    r2_x = f2x(5695)
    frags.append(line(r1_x, 318, r2_x, 318, color="#b91c1c", sw=1.5))
    frags.append(text((r1_x + r2_x)/2, 330, "Δf = 37 МГц", size=10, color="#b91c1c", bold=True))

    # Annotation box on the right (below y=320)
    frags.append(fitbox(430, 325, 340, 44, "Ширина аналогового каналу: ~17–20 МГц.\nRaceband дає крок 37 МГц і охоплює 5658–5917 МГц,\nзабезпечуючи вдвічі більший захисний інтервал.", size=10, fill="#ffffff", stroke=MUTED))

    render(path, w, h, *frags, title="Розподіл сіток частот 5.8 ГГц (Bands A, B, E, F та TBS Raceband)")

def make_imd3_mechanism(path):
    w, h = 820, 360
    frags = []
    
    frags.append(rect(15, 45, 790, 300, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    
    # Conflict callout box (top)
    frags.append(fitbox(180, 58, 460, 46, "КОНФЛІКТ У СІТЦІ 20 МГц:\nПродукт IMD3 (2f₂ − f₁ = 5780 МГц) потрапляє точно в канал F3\nі за рівнем глушить слабкий корисний сигнал далекого пілота!", size=10, fill="#fef2f2", stroke="#dc2626", color="#991b1b"))

    # Frequency baseline
    base_y = 265
    frags.append(arrow(40, base_y, 770, base_y, color=LINE, sw=1.8))
    frags.append(text(775, base_y + 4, "f", size=13, color=INK, bold=True))
    
    # Peak positions
    f1_x, f1_h = 280, 145
    f2_x, f2_h = 440, 145
    delta_x = f2_x - f1_x # 160 px
    
    # IMD3 products
    imd1_x, imd1_h = f1_x - delta_x, 70
    imd2_x, imd2_h = f2_x + delta_x, 70

    # Grid lines starting below callout box (y=112) to base_y
    frags.append(line(imd1_x, 112, imd1_x, base_y, color="#e5e7eb", sw=1.0, dash="3 3"))
    frags.append(text(imd1_x, base_y + 18, "2f₁ − f₂", size=11, color=INK, bold=True))
    frags.append(text(imd1_x, base_y + 32, "(IMD3)", size=10, color=MUTED))

    frags.append(line(f1_x, 112, f1_x, base_y, color="#e5e7eb", sw=1.0, dash="3 3"))
    frags.append(text(f1_x, base_y + 18, "f₁ (Пілот 1)", size=11, color=INK, bold=True))
    frags.append(text(f1_x, base_y + 32, "5740 МГц", size=10, color=MUTED))

    frags.append(line(f2_x, 112, f2_x, base_y, color="#e5e7eb", sw=1.0, dash="3 3"))
    frags.append(text(f2_x, base_y + 18, "f₂ (Пілот 2)", size=11, color=INK, bold=True))
    frags.append(text(f2_x, base_y + 32, "5760 МГц", size=10, color=MUTED))

    frags.append(line(imd2_x, 112, imd2_x, base_y, color="#e5e7eb", sw=1.0, dash="3 3"))
    frags.append(text(imd2_x, base_y + 18, "2f₂ − f₁", size=11, color=POS, bold=True))
    frags.append(text(imd2_x, base_y + 32, "5780 МГц (F3!)", size=10, color=POS, bold=True))

    # Fundamental signals (f1, f2)
    frags.append(line(f1_x, base_y, f1_x, base_y - f1_h, color=POS, sw=3.5))
    frags.append(circle(f1_x, base_y - f1_h, 5, fill=POS, stroke=BG, sw=1.5))
    frags.append(text(f1_x, base_y - f1_h - 10, "f₁ (5740 МГц)", size=11, color=POS, bold=True))

    frags.append(line(f2_x, base_y, f2_x, base_y - f2_h, color=POS, sw=3.5))
    frags.append(circle(f2_x, base_y - f2_h, 5, fill=POS, stroke=BG, sw=1.5))
    frags.append(text(f2_x, base_y - f2_h - 10, "f₂ (5760 МГц)", size=11, color=POS, bold=True))

    # Delta f arrows
    frags.append(line(f1_x, 155, f2_x, 155, color=MUTED, sw=1.2))
    frags.append(arrow(f1_x + 30, 155, f1_x, 155, color=MUTED, sw=1.2))
    frags.append(arrow(f2_x - 30, 155, f2_x, 155, color=MUTED, sw=1.2))
    frags.append(text((f1_x + f2_x)/2, 147, "Δf = 20 МГц", size=11, color=MUTED, bold=True))

    # IMD3 products
    frags.append(line(imd1_x, base_y, imd1_x, base_y - imd1_h, color=NEG, sw=2.5))
    frags.append(circle(imd1_x, base_y - imd1_h, 4, fill=NEG, stroke=BG, sw=1.2))
    frags.append(text(imd1_x, base_y - imd1_h - 10, "5720 МГц", size=11, color=NEG, bold=True))

    frags.append(line(imd2_x, base_y, imd2_x, base_y - imd2_h, color="#dc2626", sw=2.5))
    frags.append(circle(imd2_x, base_y - imd2_h, 4, fill="#dc2626", stroke=BG, sw=1.2))
    frags.append(text(imd2_x, base_y - imd2_h - 10, "Паразитний IMD3", size=11, color="#dc2626", bold=True))

    # Victim weak signal at f3 (5780 MHz)
    f3_h = 35
    frags.append(line(imd2_x + 35, base_y, imd2_x + 35, base_y - f3_h, color="#16a34a", sw=2.0, dash="3 2"))
    frags.append(text(imd2_x + 40, base_y - f3_h - 8, "Корисний f₃ (далекий)", size=10, color="#16a34a", anchor="start", bold=True))

    render(path, w, h, *frags, title="Механізм утворення інтермодуляції 3-го порядку (IMD3)")

def make_pa_nonlinearity_swamping(path):
    w, h = 820, 330
    frags = []
    
    # Panel 1: PA Compression & Spectral Regrowth (Left side)
    frags.append(rect(20, 50, 375, 260, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(207, 72, "а) Нелінійність PA та розширення спектра", size=12, color=INK, bold=True))
    
    # Spectral curves: Clean vs Saturated PA
    p1_base_y = 240
    frags.append(arrow(40, p1_base_y, 370, p1_base_y, color=MUTED, sw=1.2))
    frags.append(text(375, p1_base_y + 4, "f", size=11, color=MUTED))
    
    # Carrier center
    fc_x = 180
    frags.append(line(fc_x, 95, fc_x, p1_base_y, color="#e5e7eb", sw=1.0, dash="3 3"))
    frags.append(text(fc_x, p1_base_y + 15, "f₀ (Несуча)", size=10, color=MUTED))
    
    # Clean Spectrum (Linear mode, 25 mW)
    clean_pts = [(70, 238), (120, 230), (150, 180), (170, 120), (180, 105), (190, 120), (210, 180), (240, 230), (290, 238)]
    clean_d = "M " + " L ".join(["%d,%d" % p for p in clean_pts])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (clean_d, "#16a34a"))
    frags.append(text(125, 175, "25 мВт (лінійний)", size=10, color="#16a34a", bold=True))
    
    # Overdriven Spectrum with Spectral Regrowth (Saturated PA, 1–2 W)
    dirty_pts = [(45, 215), (90, 205), (130, 180), (160, 120), (180, 95), (200, 120), (230, 180), (270, 205), (315, 215), (360, 225)]
    dirty_d = "M " + " L ".join(["%d,%d" % p for p in dirty_pts])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 2"/>' % (dirty_d, POS))
    frags.append(text(285, 160, "1–2 Вт (сплетери / ACPR)", size=10, color=POS, bold=True))
    
    frags.append(fitbox(35, 260, 345, 38, "Перевантаження вихідного каскаду розширює спектр\nна 20–40 МГц, забиваючи сусідні канали шумом.", size=10, fill="#ffffff", stroke=MUTED))

    # Panel 2: Receiver Swamping / Desensitization (Right side)
    frags.append(rect(415, 50, 385, 260, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(607, 72, "б) Ефект забиття (Swamping) приймача", size=12, color=INK, bold=True))
    
    # Distance / Power diagram
    frags.append(rect(435, 95, 105, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    frags.append(text(487, 115, "Близький дрон", size=11, color=POS, bold=True))
    frags.append(text(487, 132, "1–2 Вт (+33 дБм)", size=10, color=POS))
    frags.append(text(487, 146, "Відстань 5 м", size=9, color=MUTED))
    
    frags.append(rect(675, 95, 105, 60, fill="#ecfdf5", stroke="#16a34a", sw=1.5, rx=5))
    frags.append(text(727, 115, "Далекий дрон", size=11, color="#16a34a", bold=True))
    frags.append(text(727, 132, "25–200 мВт", size=10, color="#16a34a"))
    frags.append(text(727, 146, "Відстань 1500 м", size=9, color=MUTED))
    
    # Ground Station in the middle
    frags.append(rect(545, 185, 130, 60, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(610, 205, "Базова станція VRX", size=11, color=NEG, bold=True))
    frags.append(text(610, 222, "LNA перевантажено!", size=10, color=POS, bold=True))
    frags.append(text(610, 236, "Вхід: −10 дБм (забиття)", size=9, color=MUTED))
    
    # Signal propagation arrows
    frags.append(arrow(487, 160, 560, 185, color=POS, sw=2.5))
    frags.append(arrow(727, 160, 660, 185, color="#16a34a", sw=1.2))
    
    frags.append(fitbox(430, 260, 355, 38, "Різниця потужностей на вході сягає 70–80 дБ.\nLNA виходить у компресію, втрачаючи слабкий сигнал.", size=10, fill="#ffffff", stroke=MUTED))

    render(path, w, h, *frags, title="Спектральне розширення PA та десенсибілізація приймача")

def make_polarization_multipath_rejection(path):
    w, h = 820, 330
    frags = []
    
    # Ground reflection and multipath rejection
    frags.append(rect(15, 45, 790, 270, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    
    # Transmitter Drone (Left)
    frags.append(rect(35, 75, 130, 55, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(100, 97, "VTX Передавач", size=11, color=POS, bold=True))
    frags.append(text(100, 114, "Антена RHCP", size=10, color=POS))
    
    # Receiver Goggles / Base (Right)
    frags.append(rect(655, 75, 130, 55, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(720, 97, "VRX Приймач", size=11, color=NEG, bold=True))
    frags.append(text(720, 114, "Антена RHCP", size=10, color=NEG))
    
    # Direct Path (RHCP -> RHCP)
    frags.append(arrow(165, 102, 655, 102, color=POS, sw=2.5))
    frags.append(text(410, 90, "Прямий промінь (RHCP) → Прийом без втрат (0 дБ)", size=11, color=POS, bold=True))
    
    # Reflecting Surface (Ground / Obstacle)
    ref_y = 230
    frags.append(rect(100, ref_y, 620, 18, fill="#e5e7eb", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(410, ref_y + 13, "Відбивна поверхня (земля, бетонні стіни, металеві конструкції)", size=10, color=INK))
    
    # Reflected Path
    rx_mid = 410
    frags.append(arrow(165, 115, rx_mid, ref_y, color=POS, sw=1.8))
    frags.append(text(270, 160, "Падаюча: RHCP", size=10, color=POS, bold=True))
    
    # Bounce reversal
    frags.append(circle(rx_mid, ref_y - 8, 12, fill="#ffffff", stroke="#9333ea", sw=1.5))
    frags.append(text(rx_mid, ref_y - 4, "⇄", size=14, color="#9333ea", bold=True))
    frags.append(text(rx_mid, ref_y - 25, "Зміна знака фази (180°)", size=9, color="#9333ea", bold=True))
    
    frags.append(arrow(rx_mid, ref_y, 655, 115, color=NEG, sw=1.8))
    frags.append(text(555, 160, "Відбита: LHCP", size=10, color=NEG, bold=True))
    
    # Rejection label at receiver
    frags.append(fitbox(550, 260, 235, 42, "Придушення антеною RHCP:\nКрос-поляризаційне ослаблення\nLHCP-хвилі на 18–25 дБ!", size=10, fill="#fef2f2", stroke="#dc2626", color="#991b1b"))
    
    # Alternating Polarization for pilots note
    frags.append(fitbox(35, 260, 490, 42, "Чергування поляризацій між сусідніми пілотами:\nПілот 1: R1 (RHCP) | Пілот 2: R2 (LHCP) | Пілот 3: R4 (RHCP) | Пілот 4: R7 (LHCP)\nЗабезпечує додаткові 15–20 дБ просторової розв'язки між каналами.", size=10, fill="#ffffff", stroke=MUTED))

    render(path, w, h, *frags, title="Придушення багатопроменевих відбить круговою поляризацією")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    make_bands_spectrum_map(os.path.join(img_dir, 'bands-spectrum-map.svg'))
    make_imd3_mechanism(os.path.join(img_dir, 'imd3-mechanism.svg'))
    make_pa_nonlinearity_swamping(os.path.join(img_dir, 'pa-nonlinearity-swamping.svg'))
    make_polarization_multipath_rejection(os.path.join(img_dir, 'polarization-multipath-rejection.svg'))
    print("All 4 figures successfully generated!")

if __name__ == '__main__':
    main()
