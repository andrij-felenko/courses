# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_equivalent_circuit():
    W, H = 840, 400
    p = []
    p.append(rect(30, 25, 780, 350, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 52, "Повна зосереджена схема заміщення реальної котушки індуктивності", size=15, color=INK, bold=True))
    
    p.append(line(50, 180, 120, 180, color=LINE, sw=2))
    p.append(circle(50, 180, 4, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(50, 160, "Вхід A", size=11, color=NEG, bold=True))
    
    p.append(line(720, 180, 790, 180, color=LINE, sw=2))
    p.append(circle(790, 180, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(790, 160, "Вихід B", size=11, color=POS, bold=True))
    
    p.append(circle(120, 180, 3.5, fill=INK, stroke=INK))
    p.append(line(120, 110, 120, 250, color=LINE, sw=1.8))
    
    p.append(circle(720, 180, 3.5, fill=INK, stroke=INK))
    p.append(line(720, 110, 720, 250, color=LINE, sw=1.8))
    
    p.append(line(120, 110, 390, 110, color=LINE, sw=1.8))
    p.append(line(430, 110, 720, 110, color=LINE, sw=1.8))
    
    p.append(line(390, 85, 390, 135, color=NEG, sw=2.5))
    p.append(line(410, 85, 410, 135, color=NEG, sw=2.5))
    p.append(rect(320, 64, 160, 20, fill="#ffffff", stroke="#2457d6", sw=1, rx=3))
    p.append(text(400, 78, "EPC (C_par)", size=11, color=NEG, bold=True))
    p.append(text(400, 150, "Міжвиткова, міжшарова та ємність на екран", size=10, color=MUTED))
    
    p.append(line(120, 250, 170, 250, color=LINE, sw=1.8))
    
    p.append(rect(170, 235, 75, 30, fill="#ffffff", stroke=POS, sw=1.8, rx=4))
    p.append(text(207.5, 254, "DCR", size=11, color=POS, bold=True))
    p.append(text(207.5, 282, "Омічний опір", size=10, color=MUTED))
    p.append(text(207.5, 296, "проводу (R_dc)", size=9.5, color=MUTED))
    
    p.append(line(245, 250, 285, 250, color=LINE, sw=1.8))
    
    p.append(rect(285, 235, 85, 30, fill="#ffffff", stroke=POS, sw=1.8, rx=4))
    p.append(text(327.5, 254, "R_ac(f)", size=11, color=POS, bold=True))
    p.append(text(327.5, 282, "Скін-ефект і", size=10, color=MUTED))
    p.append(text(327.5, 296, "ефект близькості", size=9.5, color=MUTED))
    
    p.append(line(370, 250, 410, 250, color=LINE, sw=1.8))
    
    p.append(circle(410, 250, 3, fill=INK, stroke=INK))
    p.append(line(410, 205, 410, 295, color=LINE, sw=1.5))
    p.append(line(600, 205, 600, 295, color=LINE, sw=1.5))
    p.append(circle(600, 250, 3, fill=INK, stroke=INK))
    
    p.append(line(410, 205, 440, 205, color=LINE, sw=1.5))
    p.append(line(570, 205, 600, 205, color=LINE, sw=1.5))
    
    for i in range(4):
        cx = 455 + i * 26
        p.append('<path d="M %d 205 A 13 13 0 0 1 %d 205" fill="none" stroke="%s" stroke-width="2.5"/>' % (cx-13, cx+13, FIELD))
    p.append(text(494, 185, "L_ном (Основна індуктивність)", size=11, color=FIELD, bold=True))
    
    p.append(line(410, 295, 465, 295, color=LINE, sw=1.5))
    p.append(line(545, 295, 600, 295, color=LINE, sw=1.5))
    p.append(rect(465, 280, 80, 30, fill="#ffffff", stroke="#e0a32e", sw=1.8, rx=4))
    p.append(text(505, 299, "R_core(f)", size=11, color="#b27b10", bold=True))
    p.append(text(505, 327, "Втрати на гістерезис", size=10, color=MUTED))
    p.append(text(505, 341, "та вихрові струми осердя", size=9.5, color=MUTED))
    
    p.append(line(600, 250, 720, 250, color=LINE, sw=1.8))
    
    render(os.path.join(OUT, "equivalent-circuit-model.svg"), W, H, *p,
           title="Повна еквівалентна схема неідеальної котушки індуктивності")

def fig_impedance_frequency():
    W, H = 840, 480
    p = []
    
    p.append(rect(30, 20, 780, 440, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 45, "Частотна характеристика імпедансу |Z(f)| та зсуву фази θ(f)", size=15, color=INK, bold=True))
    
    p.append(line(100, 370, 740, 370, color=LINE, sw=1.8))
    p.append(arrow(730, 370, 755, 370, color=LINE, sw=1.8))
    p.append(text(750, 395, "Частота f (log)", size=11, color=INK, bold=True, anchor="end"))
    
    p.append(line(100, 370, 100, 70, color=POS, sw=1.8))
    p.append(arrow(100, 80, 100, 60, color=POS, sw=1.8))
    p.append(text(95, 75, "|Z| (Ом)", size=11, color=POS, bold=True, anchor="end"))
    
    p.append(line(740, 370, 740, 70, color=NEG, sw=1.8))
    p.append(arrow(740, 80, 740, 60, color=NEG, sw=1.8))
    p.append(text(745, 75, "Фаза θ (°)", size=11, color=NEG, bold=True, anchor="start"))
    
    p.append(line(100, 130, 740, 130, color="#d0d7de", sw=1, dash="4,4"))
    p.append(text(748, 134, "+90°", size=10, color=NEG, anchor="start"))
    
    p.append(line(100, 230, 740, 230, color="#d0d7de", sw=1, dash="4,4"))
    p.append(text(748, 234, "0°", size=10, color=NEG, anchor="start"))
    
    p.append(line(100, 330, 740, 330, color="#d0d7de", sw=1, dash="4,4"))
    p.append(text(748, 334, "−90°", size=10, color=NEG, anchor="start"))
    
    f_res_x = 420
    p.append(line(f_res_x, 70, f_res_x, 370, color="#e0a32e", sw=1.5, dash="6,4"))
    p.append(text(f_res_x, 390, "f_SRF (Резонанс)", size=11, color="#b27b10", bold=True))
    
    z_path = "M 100 350 C 160 350, 190 340, 220 310 L 380 150 C 400 130, 410 95, 420 95 C 430 95, 440 130, 460 150 L 640 310 C 670 335, 700 350, 730 360"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (z_path, POS))
    
    phase_path = "M 100 230 C 150 230, 180 135, 240 130 L 370 130 C 400 130, 410 180, 420 230 C 430 280, 440 330, 470 330 L 670 330 C 700 330, 720 330, 730 330"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,3"/>' % (phase_path, NEG))
    
    p.append(circle(100, 350, 4, fill=POS, stroke=LINE))
    p.append(text(125, 345, "|Z| = DCR", size=10, color=POS, bold=True, anchor="start"))
    
    p.append(rect(160, 190, 150, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(235, 206, "Індуктивна область", size=10.5, color=FIELD, bold=True))
    p.append(text(235, 222, "+20 дБ/дек (|Z| ≈ 2πfL)", size=9.5, color=INK))
    
    p.append(circle(f_res_x, 95, 4.5, fill="#e0a32e", stroke=LINE))
    p.append(rect(330, 58, 180, 30, fill="#ffffff", stroke="#e0a32e", sw=1.5, rx=4))
    p.append(text(420, 72, "Z_peak = Q · ω_0 · L", size=10.5, color="#b27b10", bold=True))
    p.append(text(420, 84, "Антирезонанс (θ = 0°)", size=9.5, color=MUTED))
    
    p.append(rect(530, 190, 160, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(610, 206, "Ємнісна область", size=10.5, color=NEG, bold=True))
    p.append(text(610, 222, "−20 дБ/дек (|Z| ≈ 1/2πfC_par)", size=9.5, color=INK))
    
    p.append(line(130, 435, 170, 435, color=POS, sw=3))
    p.append(text(180, 439, "Модуль імпедансу |Z|", size=10, color=INK, anchor="start", bold=True))
    
    p.append(line(370, 435, 410, 435, color=NEG, sw=2, dash="6,3"))
    p.append(text(420, 439, "Фазовий кут θ (струм/напруга)", size=10, color=INK, anchor="start", bold=True))
    
    p.append(line(610, 435, 640, 435, color="#e0a32e", sw=1.5, dash="6,4"))
    p.append(text(650, 439, "Частота SRF", size=10, color=INK, anchor="start", bold=True))
    
    render(os.path.join(OUT, "impedance-frequency-curve.svg"), W, H, *p,
           title="Частотна характеристика імпедансу неідеальної котушки")

def fig_skin_and_proximity():
    W, H = 840, 440
    p = []
    
    p.append(rect(25, 20, 790, 400, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 48, "Розподіл густини змінного струму в провідниках обмотки", size=15, color=INK, bold=True))
    
    p.append(rect(45, 75, 225, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(157.5, 100, "1. Постійний струм (DC)", size=12, color=INK, bold=True))
    
    p.append(circle(157.5, 200, 65, fill="#ffebee", stroke=POS, sw=2))
    p.append(text(157.5, 195, "Рівномірна", size=11, color=POS, bold=True))
    p.append(text(157.5, 212, "густина J_0", size=11, color=POS, bold=True))
    p.append(text(157.5, 290, "Струм протікає крізь", size=10, color=MUTED))
    p.append(text(157.5, 305, "весь переріз міді", size=10, color=MUTED))
    p.append(text(157.5, 345, "R_ac = R_dc", size=11.5, color=FIELD, bold=True))
    p.append(text(157.5, 365, "Втрати мінімальні", size=10, color=MUTED))
    
    p.append(rect(295, 75, 240, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(415, 100, "2. Скін-ефект (Skin Effect)", size=12, color=INK, bold=True))
    
    p.append(circle(415, 200, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(circle(415, 200, 65, fill="none", stroke=POS, sw=14))
    p.append(circle(415, 200, 51, fill="#f8f9fa", stroke="#d0d7de", sw=1))
    
    p.append(text(415, 195, "Знеструмлений", size=10, color=MUTED))
    p.append(text(415, 210, "центр (J ≈ 0)", size=10, color=MUTED))
    
    p.append(line(480, 200, 466, 200, color=POS, sw=1.8))
    p.append(text(485, 185, "δ (скін-шар)", size=10, color=POS, bold=True, anchor="start"))
    
    p.append(text(415, 290, "Власне поле витісняє", size=10, color=MUTED))
    p.append(text(415, 305, "струм до поверхні", size=10, color=MUTED))
    p.append(text(415, 345, "R_ac > R_dc", size=11.5, color="#e0a32e", bold=True))
    p.append(text(415, 365, "δ = √(ρ / π f μ)", size=10, color=INK))
    
    p.append(rect(560, 75, 240, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(680, 100, "3. Ефект близькості", size=12, color=INK, bold=True))
    
    p.append(circle(630, 200, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(circle(730, 200, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    
    p.append('<path d="M 630 160 A 40 40 0 0 0 630 240 A 25 40 0 0 1 630 160" fill="%s" stroke="none"/>' % POS)
    p.append('<path d="M 730 160 A 40 40 0 0 1 730 240 A 25 40 0 0 0 730 160" fill="%s" stroke="none"/>' % POS)
    
    p.append('<path d="M 680 145 Q 680 200 680 255" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % FIELD)
    p.append(text(680, 140, "Поле H_ext", size=10, color=FIELD, bold=True))
    
    p.append(text(680, 290, "Поле сусідніх витків", size=10, color=MUTED))
    p.append(text(680, 305, "спричиняє вихрові струми", size=10, color=MUTED))
    p.append(text(680, 345, "R_ac >> R_dc (до 10–50×)", size=11.5, color=POS, bold=True))
    p.append(text(680, 365, "Втрати ростуть як m²", size=10, color=POS))
    
    render(os.path.join(OUT, "skin-and-proximity-effect.svg"), W, H, *p,
           title="Скін-ефект та ефект близькості в провідниках котушки")

def fig_winding_capacitance():
    W, H = 840, 420
    p = []
    
    p.append(rect(25, 20, 790, 380, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 48, "Конструкція обмоток: розподіл градієнта напруги та паразитної ємності", size=15, color=INK, bold=True))
    
    p.append(rect(45, 75, 235, 305, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(162.5, 98, "А. Звичайне пошарове", size=11.5, color=POS, bold=True))
    
    p.append(rect(65, 120, 195, 16, fill="#e0e0e0", stroke=LINE, sw=1.2))
    p.append(text(162.5, 132, "Магнітне осердя / каркас", size=9.5, color=MUTED))
    
    for i in range(5):
        cx = 85 + i * 38
        p.append(circle(cx, 160, 15, fill="#fff3e0", stroke=POS, sw=1.5))
        p.append(text(cx, 164, "В%d" % (i+1), size=9.5, color=INK, bold=True))
    
    for i in range(5):
        cx = 85 + i * 38
        p.append(circle(cx, 200, 15, fill="#ffebee", stroke=POS, sw=1.5))
        p.append(text(cx, 204, "В%d" % (10-i), size=9.5, color=INK, bold=True))
    
    p.append(line(85, 175, 85, 185, color=POS, sw=2))
    p.append(text(85, 235, "ΔV_max = 9 · V_turn", size=10, color=POS, bold=True))
    p.append(text(162.5, 260, "Величезна накопичена", size=10, color=MUTED))
    p.append(text(162.5, 275, "енергія W = ½ C (ΔV)²", size=10, color=MUTED))
    p.append(rect(65, 305, 195, 30, fill="#fbecec", stroke=POS, sw=1, rx=4))
    p.append(text(162.5, 324, "EPC максимальна (найгірше)", size=10, color=POS, bold=True))
    
    p.append(rect(300, 75, 235, 305, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(417.5, 98, "Б. Прогресивне (Bank)", size=11.5, color="#e0a32e", bold=True))
    
    p.append(rect(320, 120, 195, 16, fill="#e0e0e0", stroke=LINE, sw=1.2))
    p.append(text(417.5, 132, "Магнітне осердя / каркас", size=9.5, color=MUTED))
    
    turns_bank = [(340, 160, 1), (355, 195, 2), (380, 160, 3), (395, 195, 4),
                  (420, 160, 5), (435, 195, 6), (460, 160, 7), (475, 195, 8)]
    for cx, cy, num in turns_bank:
        p.append(circle(cx, cy, 14, fill="#fff8e1", stroke="#e0a32e", sw=1.5))
        p.append(text(cx, cy+3, "В%d" % num, size=9.5, color=INK, bold=True))
        
    p.append(text(417.5, 235, "ΔV_сусідні ≤ 2 · V_turn", size=10, color="#b27b10", bold=True))
    p.append(text(417.5, 260, "Намотування ведеться", size=10, color=MUTED))
    p.append(text(417.5, 275, "похилими стопками", size=10, color=MUTED))
    p.append(rect(320, 305, 195, 30, fill="#fff8e1", stroke="#e0a32e", sw=1, rx=4))
    p.append(text(417.5, 324, "EPC знижено в 3–5 разів", size=10, color="#b27b10", bold=True))
    
    p.append(rect(555, 75, 240, 305, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(675, 98, "В. Секціонований каркас", size=11.5, color=FIELD, bold=True))
    
    p.append(rect(575, 120, 200, 16, fill="#e0e0e0", stroke=LINE, sw=1.2))
    p.append(rect(638, 136, 8, 85, fill="#b0bec5", stroke=LINE, sw=1))
    p.append(rect(705, 136, 8, 85, fill="#b0bec5", stroke=LINE, sw=1))
    
    sec_turns = [
        (595, 160, 1), (618, 160, 2), (606, 195, 3),
        (662, 160, 4), (685, 160, 5), (673, 195, 6),
        (728, 160, 7), (751, 160, 8), (740, 195, 9)
    ]
    for cx, cy, num in sec_turns:
        p.append(circle(cx, cy, 11, fill="#e8f5e9", stroke=FIELD, sw=1.5))
        p.append(text(cx, cy+3, "%d" % num, size=9.5, color=INK, bold=True))
        
    p.append(text(675, 235, "C_секцій = C_0 / N_секцій", size=10, color=FIELD, bold=True))
    p.append(text(675, 260, "Фізичний поділ обмотки", size=10, color=MUTED))
    p.append(text(675, 275, "на ізольовані камери", size=10, color=MUTED))
    p.append(rect(575, 305, 200, 30, fill="#eef6ef", stroke=FIELD, sw=1, rx=4))
    p.append(text(675, 324, "EPC мінімальна (SRF макс.)", size=10, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "winding-capacitance-topologies.svg"), W, H, *p,
           title="Вплив геометрії обмотки на паразитну ємність EPC")

def fig_shielding_and_stray_flux():
    W, H = 840, 440
    p = []
    
    p.append(rect(25, 20, 790, 400, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 48, "Поля розсіювання: неекрановані, напівекрановані та монолітні дроселі", size=15, color=INK, bold=True))
    
    p.append(rect(45, 75, 235, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(162.5, 98, "1. Неекранований (Drum)", size=11.5, color=POS, bold=True))
    
    p.append(rect(142.5, 140, 40, 70, fill="#90a4ae", stroke=LINE, sw=1.5))
    p.append(rect(122.5, 125, 80, 15, fill="#90a4ae", stroke=LINE, sw=1.5))
    p.append(rect(122.5, 210, 80, 15, fill="#90a4ae", stroke=LINE, sw=1.5))
    
    p.append(rect(127.5, 145, 15, 60, fill="#ffccbc", stroke=POS, sw=1.2))
    p.append(rect(182.5, 145, 15, 60, fill="#ffccbc", stroke=POS, sw=1.2))
    
    p.append('<path d="M 125 130 C 60 130, 60 220, 125 220" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % POS)
    p.append('<path d="M 200 130 C 265 130, 265 220, 200 220" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % POS)
    p.append(text(162.5, 250, "Магнітне поле замикається", size=10, color=POS, bold=True))
    p.append(text(162.5, 265, "через відкрите повітря", size=10, color=MUTED))
    
    p.append(line(55, 330, 270, 330, color=LINE, sw=2))
    p.append(text(162.5, 345, "Шар GND / сигнальні доріжки", size=9.5, color=MUTED))
    p.append(text(162.5, 360, "Високі наведення та вихрові втрати", size=9.5, color=POS, bold=True))
    p.append(text(162.5, 385, "EMI високий · Дешевий", size=10, color=INK))
    
    p.append(rect(300, 75, 235, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(417.5, 98, "2. Напівекранований", size=11.5, color="#e0a32e", bold=True))
    
    p.append(rect(397.5, 140, 40, 70, fill="#90a4ae", stroke=LINE, sw=1.5))
    p.append(rect(377.5, 125, 80, 15, fill="#90a4ae", stroke=LINE, sw=1.5))
    p.append(rect(377.5, 210, 80, 15, fill="#90a4ae", stroke=LINE, sw=1.5))
    
    p.append(rect(382.5, 145, 15, 60, fill="#ffccbc", stroke=POS, sw=1.2))
    p.append(rect(437.5, 145, 15, 60, fill="#ffccbc", stroke=POS, sw=1.2))
    
    p.append(rect(367.5, 140, 15, 70, fill="#bcaaa4", stroke="#8d6e63", sw=1.2))
    p.append(rect(452.5, 140, 15, 70, fill="#bcaaa4", stroke="#8d6e63", sw=1.2))
    
    p.append('<path d="M 375 130 C 350 130, 350 220, 375 220" fill="none" stroke="#e0a32e" stroke-width="1.8" stroke-dasharray="4,3"/>')
    p.append('<path d="M 460 130 C 485 130, 485 220, 460 220" fill="none" stroke="#e0a32e" stroke-width="1.8" stroke-dasharray="4,3"/>')
    p.append(text(417.5, 250, "Смола з феритовим порошком", size=10, color="#b27b10", bold=True))
    p.append(text(417.5, 265, "частково замикає потік", size=10, color=MUTED))
    
    p.append(line(310, 330, 525, 330, color=LINE, sw=2))
    p.append(text(417.5, 345, "Шар GND / сигнальні доріжки", size=9.5, color=MUTED))
    p.append(text(417.5, 360, "Помірні наведення", size=9.5, color="#b27b10", bold=True))
    p.append(text(417.5, 385, "EMI середній · Баланс ціни", size=10, color=INK))
    
    p.append(rect(555, 75, 240, 325, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(675, 98, "3. Монолітний (Molded)", size=11.5, color=FIELD, bold=True))
    
    p.append(rect(615, 125, 120, 100, fill="#78909c", stroke=LINE, sw=1.5, rx=4))
    
    p.append(circle(645, 160, 10, fill="#ffccbc", stroke=POS, sw=1.2))
    p.append(circle(645, 190, 10, fill="#ffccbc", stroke=POS, sw=1.2))
    p.append(circle(705, 160, 10, fill="#ffccbc", stroke=POS, sw=1.2))
    p.append(circle(705, 190, 10, fill="#ffccbc", stroke=POS, sw=1.2))
    
    p.append('<circle cx="675" cy="175" r="42" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % FIELD)
    p.append(text(675, 250, "100% потоку замкнено", size=10, color=FIELD, bold=True))
    p.append(text(675, 265, "всередині моноліту", size=10, color=MUTED))
    
    p.append(line(565, 330, 785, 330, color=LINE, sw=2))
    p.append(text(675, 345, "Суцільний екран GND під дроселем", size=9.5, color=MUTED))
    p.append(text(675, 360, "Наведення відсутні · Безпечно", size=9.5, color=FIELD, bold=True))
    p.append(text(675, 385, "EMI мінімальний · Топ надійність", size=10, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "shielding-and-stray-flux.svg"), W, H, *p,
           title="Порівняння полів розсіювання неекранованих та екранованих дроселів")

if __name__ == "__main__":
    fig_equivalent_circuit()
    fig_impedance_frequency()
    fig_skin_and_proximity()
    fig_winding_capacitance()
    fig_shielding_and_stray_flux()
    print("All 5 figures generated successfully.")
