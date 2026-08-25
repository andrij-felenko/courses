# -*- coding: utf-8 -*-
"""Generator for SVG figures in ragone-chart topic."""

import sys
import os

# Four levels up to reach scripts/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_ragone_overview(path):
    w, h = 760, 520
    frags = []
    
    # Title
    frags.append(text(w / 2, 28, "Порівняльна діаграма Рагоне для джерел енергії", size=16, bold=True))
    
    # Chart area background and grid
    ox, oy = 90, 440
    cw, ch = 630, 380
    
    frags.append(rect(ox, oy - ch, cw, ch, fill="#fafbfc", stroke="#cccccc", sw=1.5))
    
    # Axes labels
    frags.append(text(ox + cw / 2, oy + 42, "Питома енергія E_sp (Вт·год / кг)", size=13, bold=True, color="#333333"))
    frags.append(text(ox - 55, oy - ch / 2, "Питома потужність P_sp (Вт / кг)", size=13, bold=True, color="#333333", anchor="middle"))
    
    # Log Grid lines (Horizontal: P_sp from 10^0 to 10^6)
    y_labels = [
        (oy, "10⁰ = 1"),
        (oy - ch * 1/6, "10¹ = 10"),
        (oy - ch * 2/6, "10² = 100"),
        (oy - ch * 3/6, "10³ = 1 кВт"),
        (oy - ch * 4/6, "10⁴ = 10 кВт"),
        (oy - ch * 5/6, "10⁵ = 100 кВт"),
        (oy - ch, "10⁶ = 1 МВт")
    ]
    for y_pos, lbl in y_labels:
        if y_pos != oy and y_pos != (oy - ch):
            frags.append(line(ox, y_pos, ox + cw, y_pos, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(ox - 8, y_pos + 4, lbl, size=10, color=MUTED, anchor="end"))
        
    # Log Grid lines (Vertical: E_sp from 10^-2 to 10^4)
    x_labels = [
        (ox, "0.01"),
        (ox + cw * 1/6, "0.1"),
        (ox + cw * 2/6, "1"),
        (ox + cw * 3/6, "10"),
        (ox + cw * 4/6, "100"),
        (ox + cw * 5/6, "1 000"),
        (ox + cw, "10 000")
    ]
    for x_pos, lbl in x_labels:
        if x_pos != ox and x_pos != (ox + cw):
            frags.append(line(x_pos, oy - ch, x_pos, oy, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(x_pos, oy + 18, lbl, size=10, color=MUTED, anchor="middle"))

    # Time lines
    time_lines = [
        (ox + cw * 0.1, oy - ch * 0.8, ox + cw * 0.85, oy - ch * 0.05, "t = 1 с"),
        (ox + cw * 0.25, oy - ch * 0.85, ox + cw * 0.95, oy - ch * 0.15, "t = 1 хв"),
        (ox + cw * 0.4, oy - ch * 0.9, ox + cw * 0.98, oy - ch * 0.32, "t = 1 год"),
        (ox + cw * 0.55, oy - ch * 0.95, ox + cw * 0.99, oy - ch * 0.5, "t = 10 год")
    ]
    for x1, y1, x2, y2, lbl in time_lines:
        frags.append(line(x1, y1, x2, y2, color="#9ca3af", sw=1.2, dash="6,3"))
        frags.append(text(x2 - 15, y2 - 6, lbl, size=10, color="#6b7280", italic=True))

    # Tech Regions
    # 1. Electrostatic Capacitors
    c_box = rect(ox + 10, oy - ch + 15, 80, 90, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=8)
    frags.append(c_box)
    frags.append(mtext(ox + 50, oy - ch + 45, "Електростатичні\nконденсатори", size=10, color="#991b1b", bold=True))

    # 2. Supercapacitors
    sc_box = rect(ox + 120, oy - ch + 60, 110, 110, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=8)
    frags.append(sc_box)
    frags.append(mtext(ox + 175, oy - ch + 100, "Суперконденсатори\n(EDLC / Іоністори)", size=10, color="#92400e", bold=True))

    # 3. Li-ion Batteries
    li_box = rect(ox + 350, oy - ch + 170, 130, 100, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=8)
    frags.append(li_box)
    frags.append(mtext(ox + 415, oy - ch + 205, "Літій-іонні\nакумулятори", size=11, color="#166534", bold=True))

    # 4. Lead-Acid & NiMH
    pb_box = rect(ox + 270, oy - ch + 230, 100, 80, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=8)
    frags.append(pb_box)
    frags.append(mtext(ox + 320, oy - ch + 260, "Свинцеві та NiMH\nакумулятори", size=10, color="#075985", bold=True))

    # 5. Fuel Cells
    fc_box = rect(ox + 470, oy - ch + 260, 120, 90, fill="#f3e8ff", stroke="#a855f7", sw=1.5, rx=8)
    frags.append(fc_box)
    frags.append(mtext(ox + 530, oy - ch + 295, "Паливні\nелементи", size=11, color="#6b21a8", bold=True))

    render(path, w, h, *frags)

def generate_equivalent_circuit(path):
    w, h = 720, 320
    frags = []
    
    frags.append(text(w / 2, 26, "Еквівалентна електрична схема імпедансу елемента", size=16, bold=True))
    
    # Left terminal (Positive)
    frags.append(plus(50, 160, r=14))
    frags.append(line(64, 160, 110, 160, sw=2))
    
    # EMF source (E_0)
    frags.append(circle(130, 160, 20, fill="#ffffff", stroke="#1a1a1a", sw=2))
    frags.append(text(130, 165, "E₀", size=14, bold=True))
    frags.append(line(150, 160, 190, 160, sw=2))
    
    # Ohmic Resistance
    frags.append(rect(190, 140, 70, 40, fill="#ffffff", stroke="#c0392b", sw=2, rx=4))
    frags.append(text(225, 165, "R_Ω", size=13, color="#c0392b", bold=True))
    frags.append(text(225, 125, "Омічний опір", size=10, color=MUTED))
    
    frags.append(line(260, 160, 300, 160, sw=2))
    
    # Parallel branch for Electrochemical Interface (R_ct || C_dl) + Warburg element W
    frags.append(line(300, 160, 300, 100, sw=2))
    frags.append(line(300, 160, 300, 220, sw=2))
    
    # Upper branch: R_ct
    frags.append(line(300, 100, 340, 100, sw=2))
    frags.append(rect(340, 80, 80, 40, fill="#ffffff", stroke="#2457d6", sw=2, rx=4))
    frags.append(text(380, 105, "R_ct", size=13, color="#2457d6", bold=True))
    frags.append(text(380, 68, "Перенос заряду", size=10, color=MUTED))
    frags.append(line(420, 100, 460, 100, sw=2))
    
    # Lower branch: C_dl
    frags.append(line(300, 220, 350, 220, sw=2))
    frags.append(line(350, 200, 350, 240, color="#27ae60", sw=3))
    frags.append(line(360, 200, 360, 240, color="#27ae60", sw=3))
    frags.append(text(355, 258, "C_dl", size=13, color="#27ae60", bold=True))
    frags.append(text(355, 275, "Подвійний шар", size=10, color=MUTED))
    frags.append(line(360, 220, 460, 220, sw=2))
    
    # Rejoin branches
    frags.append(line(460, 100, 460, 160, sw=2))
    frags.append(line(460, 220, 460, 160, sw=2))
    frags.append(line(460, 160, 500, 160, sw=2))
    
    # Warburg Impedance W
    frags.append(rect(500, 140, 80, 40, fill="#ffffff", stroke="#8e44ad", sw=2, rx=4))
    frags.append(text(540, 165, "Z_W", size=13, color="#8e44ad", bold=True))
    frags.append(text(540, 125, "Дифузія Варбурга", size=10, color=MUTED))
    
    frags.append(line(580, 160, 645, 160, sw=2))
    # Right terminal (Negative)
    frags.append(minus(660, 160, r=14))
    
    render(path, w, h, *frags)

def generate_discharge_degradation(path):
    w, h = 680, 400
    frags = []
    
    frags.append(text(w / 2, 26, "Падіння напруги та ємності при підвищенні струму розряду", size=16, bold=True))
    
    ox, oy = 80, 340
    cw, ch = 550, 270
    
    # Chart box
    frags.append(rect(ox, oy - ch, cw, ch, fill="#fafbfc", stroke="#cccccc", sw=1.5))
    
    # Axis labels
    frags.append(text(ox + cw / 2, oy + 40, "Віддана ємність / Енергія (відн. од.)", size=13, bold=True))
    frags.append(text(ox - 45, oy - ch / 2, "Напруга на клемах V (В)", size=13, bold=True, anchor="middle"))
    
    # Grid lines & ticks
    y_ticks = [
        (oy - ch * 0.95, "4.2 В (НРЦ)"),
        (oy - ch * 0.7, "3.8 В"),
        (oy - ch * 0.45, "3.4 В"),
        (oy - ch * 0.25, "3.0 В (Відсічка)"),
        (oy, "2.5 В")
    ]
    for y_pos, lbl in y_ticks:
        frags.append(line(ox, y_pos, ox + cw, y_pos, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(ox - 8, y_pos + 4, lbl, size=10, color=MUTED, anchor="end"))
        
    # Cutoff voltage red line
    frags.append(line(ox, oy - ch * 0.25, ox + cw, oy - ch * 0.25, color="#ef4444", sw=1.5, dash="6,3"))
    
    # Curves for different C-rates
    # 0.2C
    frags.append(line(ox, oy - ch * 0.95, ox + cw * 0.1, oy - ch * 0.8, color="#22c55e", sw=2.5))
    frags.append(line(ox + cw * 0.1, oy - ch * 0.8, ox + cw * 0.8, oy - ch * 0.72, color="#22c55e", sw=2.5))
    frags.append(line(ox + cw * 0.8, oy - ch * 0.72, ox + cw * 0.95, oy - ch * 0.25, color="#22c55e", sw=2.5))
    frags.append(text(ox + cw * 0.96, oy - ch * 0.35, "0.2C (Повільний)", size=11, color="#15803d", bold=True, anchor="start"))

    # 1C
    frags.append(line(ox, oy - ch * 0.85, ox + cw * 0.1, oy - ch * 0.72, color="#0284c7", sw=2.5))
    frags.append(line(ox + cw * 0.1, oy - ch * 0.72, ox + cw * 0.75, oy - ch * 0.62, color="#0284c7", sw=2.5))
    frags.append(line(ox + cw * 0.75, oy - ch * 0.62, ox + cw * 0.88, oy - ch * 0.25, color="#0284c7", sw=2.5))
    frags.append(text(ox + cw * 0.89, oy - ch * 0.45, "1C (Номінальний)", size=11, color="#0369a1", bold=True, anchor="start"))

    # 5C
    frags.append(line(ox, oy - ch * 0.65, ox + cw * 0.1, oy - ch * 0.55, color="#f59e0b", sw=2.5))
    frags.append(line(ox + cw * 0.1, oy - ch * 0.55, ox + cw * 0.55, oy - ch * 0.45, color="#f59e0b", sw=2.5))
    frags.append(line(ox + cw * 0.55, oy - ch * 0.45, ox + cw * 0.70, oy - ch * 0.25, color="#f59e0b", sw=2.5))
    frags.append(text(ox + cw * 0.71, oy - ch * 0.2, "5C (Високий струм)", size=11, color="#b45309", bold=True, anchor="start"))

    # 20C
    frags.append(line(ox, oy - ch * 0.45, ox + cw * 0.1, oy - ch * 0.35, color="#ef4444", sw=2.5))
    frags.append(line(ox + cw * 0.1, oy - ch * 0.35, ox + cw * 0.38, oy - ch * 0.25, color="#ef4444", sw=2.5))
    frags.append(text(ox + cw * 0.40, oy - ch * 0.15, "20C (Екстремальний)", size=11, color="#b91c1c", bold=True, anchor="start"))

    render(path, w, h, *frags)

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    generate_ragone_overview(os.path.join(img_dir, "ragone-chart-overview.svg"))
    generate_equivalent_circuit(os.path.join(img_dir, "equivalent-circuit-losses.svg"))
    generate_discharge_degradation(os.path.join(img_dir, "discharge-rate-degradation.svg"))
    print("Figures successfully generated in", img_dir)
