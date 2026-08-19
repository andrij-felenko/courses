# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
AMBER   = "#d97706"
AMBERBG = "#fef3c7"
REDBG   = "#fee2e2"
GRNBG   = "#dcfce7"
BLUEBG  = "#dbeafe"
PURPLE  = "#7c3aed"
PURPLEBG= "#f3e8ff"
GRAYBG  = "#f3f4f6"
DARKGRAY= "#4b5563"

# ── 1. cathode-conductivity-comparison: Порівняння електропровідності катодів ─
def fig_conductivity():
    W, H = 760, 360
    p = []
    
    # Header & canvas title
    p.append(rect(10, 10, 740, 340, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Scale line
    p.append(line(80, 260, 700, 260, color=LINE, sw=2))
    p.append(arrow(690, 260, 705, 260, color=LINE, sw=2))
    p.append(text(710, 264, "σ (См/см)", size=11, color=INK, anchor="start", bold=True))
    
    # Decade ticks from 10^-3 to 10^4
    # Map log10(sigma): -2 -> 110, -1 -> 190, 0 -> 270, 1 -> 350, 2 -> 430, 3 -> 510, 4 -> 590, 5 -> 670
    decades = [
        (-2, "0.01", 120),
        (-1, "0.1", 200),
        (0, "1", 280),
        (1, "10", 360),
        (2, "100", 440),
        (3, "1000", 520),
        (4, "10⁴", 600),
        (5, "10⁵", 670),
    ]
    for exp, label, x in decades:
        p.append(line(x, 255, x, 265, color=MUTED, sw=1.2))
        p.append(text(x, 280, label, size=10, color=MUTED))
    
    # Category 1: Liquid Electrolyte
    # Range 0.01 - 0.1 S/cm (x: 120 - 200)
    p.append(rect(100, 70, 120, 160, fill=BLUEBG, stroke=NEG, sw=1.5, rx=6))
    p.append(text(160, 92, "Рідкий електроліт", size=11, color=NEG, bold=True))
    p.append(text(160, 110, "Іонна провідність", size=9.5, color=DARKGRAY, italic=True))
    p.append(text(160, 135, "0.01–0.1 См/см", size=11, color=NEG, bold=True))
    p.append(text(160, 160, "ESR: 50–500 мОм", size=10, color=INK, bold=True))
    p.append(text(160, 182, "В'язкий дрейф іонів", size=9, color=DARKGRAY))
    p.append(text(160, 200, "Замерзає на холоді", size=9, color=POS))
    p.append(line(160, 230, 160, 255, color=NEG, sw=1.5, dash="3 3"))
    
    # Category 2: MnO2
    # Range 0.1 - 1 S/cm (x: 200 - 280)
    p.append(rect(235, 70, 120, 160, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=6))
    p.append(text(295, 92, "Діоксид марганцю", size=11, color=AMBER, bold=True))
    p.append(text(295, 110, "Напівпровідник MnO₂", size=9.5, color=DARKGRAY, italic=True))
    p.append(text(295, 135, "0.1–1.0 См/см", size=11, color=AMBER, bold=True))
    p.append(text(295, 160, "ESR: 30–150 мОм", size=10, color=INK, bold=True))
    p.append(text(295, 182, "Твердий катод", size=9.5, color=DARKGRAY))
    p.append(text(295, 200, "Джерело кисню при к.з.", size=9.5, color=POS))
    p.append(line(295, 230, 295, 255, color=AMBER, sw=1.5, dash="3 3"))
    
    # Category 3: Conductive Polymers
    # Range 100 - 1000 S/cm (x: 440 - 520)
    p.append(rect(380, 50, 180, 180, fill=GRNBG, stroke=FIELD, sw=2, rx=6))
    p.append(text(470, 72, "Кондуктивні полімери", size=12, color=FIELD, bold=True))
    p.append(text(470, 90, "PEDOT:PSS, PPy", size=10, color=DARKGRAY, italic=True))
    p.append(text(470, 115, "100–1000 См/см", size=12, color=FIELD, bold=True))
    p.append(text(470, 138, "ESR: 2–10 мОм", size=11, color=POS, bold=True))
    p.append(text(470, 160, "Електронна провідність (π-система)", size=9.5, color=DARKGRAY))
    p.append(text(470, 178, "Стрибок провідності у 10 000 разів", size=9.5, color=FIELD, bold=True))
    p.append(text(470, 198, "Безпечне дедопування без пожежі", size=9.5, color=DARKGRAY))
    p.append(line(470, 230, 470, 255, color=FIELD, sw=1.8, dash="3 3"))
    
    # Category 4: Metals (Copper)
    # Range 10^5 S/cm (x: 670)
    p.append(rect(585, 70, 145, 160, fill=GRAYBG, stroke=MUTED, sw=1.5, rx=6))
    p.append(text(657, 92, "Метали (мідь, срібло)", size=11, color=INK, bold=True))
    p.append(text(657, 110, "Металічні електроди", size=9.5, color=DARKGRAY, italic=True))
    p.append(text(657, 135, "≈ 10⁵–10⁶ См/см", size=11, color=INK, bold=True))
    p.append(text(657, 160, "Виводи та фольга", size=10, color=DARKGRAY))
    p.append(text(657, 185, "Омічний опір контактів", size=9, color=DARKGRAY))
    p.append(text(657, 205, "Фізична опора схеми", size=9, color=DARKGRAY))
    p.append(line(657, 230, 657, 255, color=MUTED, sw=1.5, dash="3 3"))
    
    # Summary note below
    p.append(text(380, 320, "Заміна іонного рідкого електроліту або оксиду MnO₂ на полімер з π-спряженням знижує ESR на 1-2 порядки", size=10, color=INK, bold=True))
    
    render(os.path.join(OUT, "cathode-conductivity-comparison.svg"), W, H, *p,
           title="Порівняння електропровідності катодних матеріалів")


# ── 2. polymer-structures-anatomy: 4 конструктивні родини полімерних конденсаторів ─
def fig_structures():
    W, H = 760, 440
    p = []
    
    p.append(rect(10, 10, 740, 420, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # 4 quadrants / boxes
    # Top-Left: Polymer Tantalum (KO-CAP, POSCAP)
    bx, by, bw, bh = 25, 30, 345, 185
    p.append(rect(bx, by, bw, bh, fill=GRAYBG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx + bw/2, by + 22, "A. Полімерний тантал (KO-CAP, POSCAP)", size=11.5, color=INK, bold=True))
    # Diagram inside
    # Tantalum anode sintered pellet
    p.append(rect(bx + 25, by + 45, 110, 75, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    p.append(text(bx + 80, by + 75, "Танталова губка", size=9.5, color="#9a3412", bold=True))
    p.append(text(bx + 80, by + 92, "Ta + Ta₂O₅", size=9, color="#9a3412"))
    # Polymer coat
    p.append(rect(bx + 140, by + 45, 60, 75, fill=GRNBG, stroke=FIELD, sw=1.5, rx=4))
    p.append(text(bx + 170, by + 75, "PEDOT", size=10, color=FIELD, bold=True))
    p.append(text(bx + 170, by + 92, "катод", size=9, color=FIELD))
    # Carbon / Ag layer
    p.append(rect(bx + 205, by + 45, 40, 75, fill=BLUEBG, stroke=NEG, sw=1.2, rx=2))
    p.append(text(bx + 225, by + 85, "C / Ag", size=9, color=NEG, bold=True))
    # Leads
    p.append(line(bx + 15, by + 82, bx + 25, by + 82, color=POS, sw=3))
    p.append(text(bx + 15, by + 72, "+", size=12, color=POS, bold=True))
    p.append(line(bx + 245, by + 82, bx + 325, by + 82, color=NEG, sw=3))
    p.append(text(bx + 315, by + 72, "−", size=12, color=NEG, bold=True))
    p.append(text(bx + bw/2, by + 145, "Висока питома ємність, напруги 2–50 В", size=9.5, color=DARKGRAY))
    p.append(text(bx + bw/2, by + 165, "ESR: 5–25 мОм, безпечна відмова без горіння", size=9.5, color=FIELD, bold=True))
    
    # Top-Right: Stacked Aluminum (SP-Cap)
    bx, by, bw, bh = 390, 30, 345, 185
    p.append(rect(bx, by, bw, bh, fill=GRAYBG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx + bw/2, by + 22, "B. Багатошаровий алюмінієвий (SP-Cap)", size=11.5, color=INK, bold=True))
    # Stacked layers
    for i in range(4):
        ly = by + 45 + i * 18
        p.append(rect(bx + 40, ly, 100, 14, fill="#e2e8f0", stroke="#64748b", sw=1, rx=2))
        p.append(rect(bx + 145, ly, 110, 14, fill=GRNBG, stroke=FIELD, sw=1, rx=2))
    p.append(text(bx + 90, by + 130, "Al фольга + Al₂O₃", size=9, color="#334155", bold=True))
    p.append(text(bx + 200, by + 130, "Полімерні шари", size=9, color=FIELD, bold=True))
    # Busbars
    p.append(line(bx + 30, by + 45, bx + 30, by + 105, color=POS, sw=3))
    p.append(line(bx + 265, by + 45, bx + 265, by + 105, color=NEG, sw=3))
    p.append(text(bx + 25, by + 40, "+", size=12, color=POS, bold=True))
    p.append(text(bx + 270, by + 40, "−", size=12, color=NEG, bold=True))
    p.append(text(bx + bw/2, by + 150, "Паралельна планарна структура, наднизький ESL (<1 нГн)", size=9.5, color=DARKGRAY))
    p.append(text(bx + bw/2, by + 168, "ESR: 3–9 мОм, ідеально для VRM процесорів", size=9.5, color=FIELD, bold=True))
    
    # Bottom-Left: Wound Aluminum (OS-CON)
    bx, by, bw, bh = 25, 230, 345, 185
    p.append(rect(bx, by, bw, bh, fill=GRAYBG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx + bw/2, by + 22, "C. Рулонний полімерний (OS-CON)", size=11.5, color=INK, bold=True))
    # Can & wound jelly roll
    p.append(rect(bx + 40, by + 45, 130, 80, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=10))
    p.append(circle(bx + 105, by + 85, 30, fill=GRNBG, stroke=FIELD, sw=1.5))
    p.append(circle(bx + 105, by + 85, 18, fill="#e2e8f0", stroke="#64748b", sw=1.2))
    p.append(circle(bx + 105, by + 85, 6, fill=GRNBG, stroke=FIELD, sw=1.2))
    p.append(text(bx + 235, by + 68, "Циліндричний рулон:", size=9.5, color=DARKGRAY, bold=True))
    p.append(text(bx + 235, by + 85, "Анодна + катодна фольга", size=9, color=DARKGRAY))
    p.append(text(bx + 235, by + 102, "Твердий полімерний гель", size=9, color=FIELD, bold=True))
    p.append(line(bx + 75, by + 125, bx + 75, by + 140, color=POS, sw=2))
    p.append(line(bx + 135, by + 125, bx + 135, by + 140, color=NEG, sw=2))
    p.append(text(bx + bw/2, by + 155, "Високий Ripple Current (до 5–7 А), радіальний/SMD", size=9.5, color=DARKGRAY))
    p.append(text(bx + bw/2, by + 172, "Напруги до 35–100 В, ESR: 5–30 мОм", size=9.5, color=FIELD, bold=True))
    
    # Bottom-Right: Hybrid Aluminum (Polymer + Liquid)
    bx, by, bw, bh = 390, 230, 345, 185
    p.append(rect(bx, by, bw, bh, fill=GRAYBG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx + bw/2, by + 22, "D. Гібридний алюмінієвий (Hybrid)", size=11.5, color=INK, bold=True))
    # Hybrid structure
    p.append(rect(bx + 35, by + 45, 120, 80, fill=GRNBG, stroke=FIELD, sw=1.5, rx=8))
    p.append(rect(bx + 45, by + 55, 100, 60, fill=BLUEBG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx + 95, by + 78, "Полімер (ESR)", size=9.5, color=FIELD, bold=True))
    p.append(text(bx + 95, by + 98, "+ Рідкий електроліт", size=9, color=NEG, bold=True))
    p.append(text(bx + 235, by + 68, "Подвійний електроліт:", size=9.5, color=DARKGRAY, bold=True))
    p.append(text(bx + 235, by + 85, "Полімер дає низький ESR", size=9, color=FIELD))
    p.append(text(bx + 235, by + 102, "Рідина лікує оксид (self-heal)", size=9, color=NEG))
    p.append(text(bx + bw/2, by + 155, "Напруги до 63–100 В, ультранизький струм витоку DCL", size=9.5, color=DARKGRAY))
    p.append(text(bx + bw/2, by + 172, "Автомобільна електроніка (AEC-Q200), ESR: 15–40 мОм", size=9.5, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "polymer-structures-anatomy.svg"), W, H, *p,
           title="Анатомія чотирьох конструктивних родин полімерних конденсаторів")


def svg_path(pts, stroke=LINE, sw=1.5, fill="none", dash=None):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{da}/>'


# ── 3. impedance-frequency-curves: Частотна характеристика |Z(f)| ────────────
def fig_impedance():
    W, H = 760, 380
    p = []
    
    p.append(rect(10, 10, 740, 360, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Axes
    ox, oy = 90, 300
    ax_w, ax_h = 610, 240
    p.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=1.8))
    p.append(arrow(ox + ax_w - 5, oy, ox + ax_w + 10, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - ax_h + 5, ox, oy - ax_h - 10, color=LINE, sw=1.8))
    
    p.append(text(ox + ax_w + 15, oy + 4, "f", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ox - 10, oy - ax_h - 5, "|Z| (Ом)", size=12, color=INK, anchor="end", bold=True))
    
    # Frequency ticks (100 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz, 10 MHz)
    f_ticks = [(0, "100 Гц"), (120, "1 кГц"), (240, "10 кГц"), (360, "100 кГц"), (480, "1 МГц"), (600, "10 МГц")]
    for fx, flabel in f_ticks:
        p.append(line(ox + fx, oy, ox + fx, oy + 5, color=MUTED, sw=1))
        p.append(text(ox + fx, oy + 20, flabel, size=9.5, color=MUTED))
    
    # |Z| ticks (10 Ohm, 1 Ohm, 100 mOhm, 10 mOhm, 1 mOhm)
    # y positions: 10 Ohm -> 80, 1 Ohm -> 130, 100 mOhm -> 185, 10 mOhm -> 240, 1 mOhm -> 290
    z_ticks = [(80, "10 Ом"), (130, "1 Ом"), (185, "100 мОм"), (240, "10 мОм"), (290, "1 мОм")]
    for zy, zlabel in z_ticks:
        p.append(line(ox - 5, zy, ox, zy, color=MUTED, sw=1))
        p.append(text(ox - 10, zy + 4, zlabel, size=9.5, color=MUTED, anchor="end"))
        p.append(line(ox, zy, ox + ax_w, zy, color="#f3f4f6", sw=1, dash="4 4"))
    
    # Curve 1: Liquid Electrolytic (100 uF / 25 V)
    # Starts at 10 Ohm, bottoms at 100 mOhm around 50 kHz, rises due to ESL
    p.append(svg_path([
        (ox, 80), (ox + 120, 130), (ox + 240, 175), (ox + 320, 185),
        (ox + 400, 190), (ox + 480, 210), (ox + 600, 240)
    ], stroke=NEG, sw=2, fill="none"))
    p.append(text(ox + 410, 175, "Рідкий електроліт (ESR ≈ 100 мОм)", size=9.5, color=NEG, bold=True))
    
    # Curve 2: Tantalum MnO2 (100 uF / 16 V)
    # Bottoms at 50 mOhm around 100 kHz
    p.append(svg_path([
        (ox, 80), (ox + 120, 130), (ox + 240, 175), (ox + 350, 205),
        (ox + 420, 210), (ox + 480, 225), (ox + 600, 255)
    ], stroke=AMBER, sw=2, fill="none"))
    p.append(text(ox + 460, 205, "Тантал MnO₂ (ESR ≈ 50 мОм)", size=9.5, color=AMBER, bold=True))
    
    # Curve 3: Polymer Capacitor (100 uF / 6.3 V, e.g. KO-CAP / SP-Cap)
    # Deep flat bottom at 5 mOhm from 100 kHz to 1 MHz
    p.append(svg_path([
        (ox, 80), (ox + 120, 130), (ox + 240, 175), (ox + 330, 225),
        (ox + 400, 255), (ox + 480, 255), (ox + 540, 260), (ox + 600, 280)
    ], stroke=FIELD, sw=3, fill="none"))
    p.append(text(ox + 310, 275, "Полімерний (ESR ≈ 4.5 мОм, широке дно)", size=10, color=FIELD, bold=True))
    
    # Curve 4: MLCC Class II Ceramic (100 uF nominal, but 1206)
    # High Q notch down to 2 mOhm, but sharp V-shape
    p.append(svg_path([
        (ox, 80), (ox + 120, 130), (ox + 240, 175), (ox + 360, 235),
        (ox + 470, 285), (ox + 530, 240), (ox + 600, 190)
    ], stroke=PURPLE, sw=2, dash="5 3", fill="none"))
    p.append(text(ox + 520, 160, "MLCC X5R (гострий V-резонанс)", size=9, color=PURPLE, bold=True))
    
    # Regions annotations: Capacitive, ESR minimum, Inductive
    p.append(text(ox + 100, 110, "1 / (2π f C)", size=9.5, color=DARKGRAY, italic=True))
    p.append(text(ox + 440, 325, "Зона мінімуму імпедансу: |Z_min| = ESR", size=10, color=FIELD, bold=True))
    p.append(text(ox + 570, 215, "2π f ESL", size=9.5, color=DARKGRAY, italic=True))

    
    render(os.path.join(OUT, "impedance-frequency-curves.svg"), W, H, *p,
           title="Частотна характеристика імпедансу різних типів конденсаторів")


# ── 4. failure-mode-flame-vs-dedoping: Механізм відмови ──────────────────────
def fig_failure_mode():
    W, H = 760, 340
    p = []
    
    p.append(rect(10, 10, 740, 320, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))
    
    # Left Box: Standard Tantalum MnO2 (Catastrophic Thermal Runaway)
    bx, by, bw, bh = 30, 30, 335, 275
    p.append(rect(bx, by, bw, bh, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(bx + bw/2, by + 25, "Традиційний тантал з MnO₂", size=12, color=POS, bold=True))
    p.append(text(bx + bw/2, by + 45, "Катастрофічний тепловий розгін", size=10, color=DARKGRAY, italic=True))
    
    steps_l = [
        ("1. Дефект оксиду Ta₂O₅", "Локальний струм витоку в мікротріщині"),
        ("2. Локальний перегрів (>400 °C)", "Струм шини концентрується в точці пробою"),
        ("3. Термічний розклад MnO₂", "2 MnO₂ → Mn₂O₃ + O (виділення кисню)"),
        ("4. Екзотермічне горіння Ta + O", "Тантал спалахує без зовнішнього повітря"),
        ("5. Результат: ПОЖЕЖА", "Коротке замикання шини та відкрите полум'я"),
    ]
    sy = by + 75
    for title, desc in steps_l:
        p.append(text(bx + 15, sy, title, size=10, color=POS, anchor="start", bold=True))
        p.append(text(bx + 15, sy + 15, desc, size=9, color=DARKGRAY, anchor="start"))
        sy += 38
        
    # Right Box: Polymer Tantalum / Aluminum (Benign Self-Healing / Dedoping)
    bx, by, bw, bh = 395, 30, 335, 275
    p.append(rect(bx, by, bw, bh, fill=GRNBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx + bw/2, by + 25, "Полімерний конденсатор (PEDOT)", size=12, color=FIELD, bold=True))
    p.append(text(bx + bw/2, by + 45, "Безпечне теплове дедопування", size=10, color=DARKGRAY, italic=True))
    
    steps_r = [
        ("1. Дефект оксиду Ta₂O₅ / Al₂O₃", "Локальний струм витоку в мікропорі"),
        ("2. Локальний нагрів (250–300 °C)", "Тепло виділяється в мікрошарі полімеру"),
        ("3. Дедопування PEDOT:PSS", "Полімер втрачає провідність → ІЗОЛЯТОР"),
        ("4. Автоматичне відсікання", "Струм через дефектну точку припиняється"),
        ("5. Результат: БЕЗПЕЧНА ВІДМОВА", "Незначний ріст DCL, відсутність полум'я"),
    ]
    sy = by + 75
    for title, desc in steps_r:
        p.append(text(bx + 15, sy, title, size=10, color=FIELD, anchor="start", bold=True))
        p.append(text(bx + 15, sy + 15, desc, size=9, color=DARKGRAY, anchor="start"))
        sy += 38
        
    render(os.path.join(OUT, "failure-mode-flame-vs-dedoping.svg"), W, H, *p,
           title="Порівняння механізмів відмови: горіння MnO2 проти дедопування полімеру")

if __name__ == "__main__":
    fig_conductivity()
    fig_structures()
    fig_impedance()
    fig_failure_mode()
    print("All figures generated successfully.")
