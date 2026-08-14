# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# 1. Packet structure diagram: Preamble + Header + Payload + CRC
def fig_packet_structure():
    W, H = 720, 280
    p = []
    
    y_box = 80
    h_box = 50
    x_start = 50
    
    # Sections: (Label, Width, Subtext, FillColor, TextColor)
    sections = [
        ("Преамбула\n(Preamble)", 140, "Синхронізація\n(8-12 символів)", "#dfe7fb", FIELD),
        ("Заголовок\n(Header)", 110, "Довжина + CR\n(8 біт + CRC)", "#f6efd6", NEG),
        ("Корисне навантаження\n(Payload)", 230, "Дані користувача\n(N байтів → N_payload символів)", "#dff0df", POS),
        ("CRC кадра\n(Frame CRC)", 130, "Контрольна сума\n(16 біт / 2 байти)", "#f3dede", NEG)
    ]
    
    cur_x = x_start
    for title, w, sub, fill, col in sections:
        p.append(rect(cur_x, y_box, w, h_box, fill=fill, stroke=col, sw=1.8, rx=4))
        # split title lines
        tlines = title.split("\n")
        if len(tlines) == 1:
            p.append(text(cur_x + w/2, y_box + h_box/2 + 4, tlines[0], size=11, color=col, bold=True))
        else:
            p.append(text(cur_x + w/2, y_box + 18, tlines[0], size=11, color=col, bold=True))
            p.append(text(cur_x + w/2, y_box + 34, tlines[1], size=9.5, color=MUTED, italic=True))
            
        slines = sub.split("\n")
        p.append(text(cur_x + w/2, y_box + h_box + 18, slines[0], size=9.5, color=INK))
        p.append(text(cur_x + w/2, y_box + h_box + 32, slines[1], size=9, color=MUTED, italic=True))
        
        cur_x += w
        
    total_w = cur_x - x_start
    
    # Bracket below showing Total Time-on-Air
    y_br = y_box + h_box + 52
    p.append(line(x_start, y_br, x_start + total_w, y_br, color=NEG, sw=2))
    p.append(line(x_start, y_br - 6, x_start, y_br + 6, color=NEG, sw=2))
    p.append(line(x_start + total_w, y_br - 6, x_start + total_w, y_br + 6, color=NEG, sw=2))
    
    p.append(text(x_start + total_w/2, y_br + 22, "Загальний час у ефірі: ToA = T_preamble + T_payload", size=13, color=NEG, bold=True))
    
    p.append(text(W / 2, H - 14,
                  "Фізична структура радіокадра: кожен елемент додає свій внесок у загальну тривалість",
                  size=11, color=MUTED, italic=True))
                  
    render(os.path.join(OUT, "packet-structure.svg"), W, H, *p,
           title="Анатомія радіокадра та формування часу в ефірі")

# 2. Spreading Factor (SF) comparison diagram
def fig_sf_comparison():
    W, H = 720, 310
    p = []
    
    # Show bar comparison of ToA for 20 bytes payload across SF7..SF12
    sf_data = [
        ("SF7",  "41 мс",   41,  "#dff0df", POS),
        ("SF8",  "72 мс",   72,  "#eef6ef", FIELD),
        ("SF9",  "144 мс",  144, "#dfe7fb", FIELD),
        ("SF10", "288 мс",  288, "#f6efd6", NEG),
        ("SF11", "576 мс",  576, "#fcd8d4", NEG),
        ("SF12", "1153 мс", 1153, "#f3dede", NEG)
    ]
    
    y_start = 55
    bar_h = 28
    gap = 14
    max_val = 1153
    max_bar_w = 420
    x_label = 90
    x_bar_start = 100
    
    p.append(text(W / 2, 28, "Порівняння Time-on-Air для кадра 20 байт (BW = 125 кГц, CR = 4/5)", size=13, color=INK, bold=True))
    
    for i, (sf, toa_str, val, fill, col) in enumerate(sf_data):
        cy = y_start + i * (bar_h + gap)
        w = int(max_bar_w * (val / max_val))
        w = max(w, 20)
        
        p.append(text(x_label - 10, cy + bar_h/2 + 4, sf, size=11, color=INK, anchor="end", bold=True))
        p.append(rect(x_bar_start, cy, w, bar_h, fill=fill, stroke=col, sw=1.5, rx=3))
        p.append(text(x_bar_start + w + 12, cy + bar_h/2 + 4, toa_str, size=11, color=col, anchor="start", bold=True))
        
    p.append(text(W / 2, H - 14,
                  "Кожен крок SF подвоює тривалість символа: перехід від SF7 до SF12 збільшує ToA у ~28 разів",
                  size=11, color=MUTED, italic=True))
                  
    render(os.path.join(OUT, "sf-comparison.svg"), W, H, *p,
           title="Вплив коефіцієнта розширення (SF) на тривалість передачі")

# 3. Duty cycle restriction diagram (1% ETSI limit)
def fig_duty_cycle():
    W, H = 720, 260
    p = []
    
    p.append(text(W / 2, 28, "Обмеження робочого циклу 1% (ETSI EN 300 220)", size=13, color=INK, bold=True))
    
    bx = 60
    by = 75
    bw = 600
    bh = 50
    
    # 1% transmit window, 99% silent window
    tx_w = bw * 0.08  # visually amplified so 1% is visible
    silent_w = bw - tx_w
    
    p.append(rect(bx, by, tx_w, bh, fill="#fcd8d4", stroke=NEG, sw=1.8))
    p.append(text(bx + tx_w/2, by + bh/2 + 4, "TX", size=11, color=NEG, bold=True))
    
    p.append(rect(bx + tx_w, by, silent_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(bx + tx_w + silent_w/2, by + bh/2 + 4, "Пауза мовчання (Off-Time: t_off ≥ 99 · ToA)", size=12, color=FIELD, bold=True))
    
    # Annotations below
    p.append(line(bx, by + bh + 16, bx + tx_w, by + bh + 16, color=NEG, sw=1.5))
    p.append(text(bx + tx_w/2, by + bh + 32, "ToA = 1 с", size=10.5, color=NEG, bold=True))
    
    p.append(line(bx + tx_w, by + bh + 16, bx + bw, by + bh + 16, color=FIELD, sw=1.5))
    p.append(text(bx + tx_w + silent_w/2, by + bh + 32, "Необхідний відпочинок каналу = 99 с", size=10.5, color=FIELD, bold=True))
    
    p.append(text(W / 2, H - 14,
                  "При 1% Duty Cycle після передачі пакета тривалістю 1 секунда пристрій зобов'язаний мовчати 99 секунд",
                  size=11, color=MUTED, italic=True))
                  
    render(os.path.join(OUT, "duty-cycle-budget.svg"), W, H, *p,
           title="Правило Duty Cycle: співвідношення часу передачі та мовчання")

# 4. Energy vs Range vs ToA trade-off triangle
def fig_energy_tradeoff():
    W, H = 720, 290
    p = []
    
    col_w = 210
    col_h = 170
    y_box = 60
    
    x1 = 40
    x2 = 255
    x3 = 470
    
    # Box 1: Low SF (SF7)
    p.append(rect(x1, y_box, col_w, col_h, fill="#dff0df", stroke=POS, sw=1.8, rx=4))
    p.append(text(x1 + col_w/2, y_box + 26, "Короткий ToA (SF7)", size=12, color=POS, bold=True))
    p.append(text(x1 + 15, y_box + 58, "• ToA ≈ 40 мс", size=10.5, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_box + 82, "• Мінімальна енергія", size=10.5, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_box + 106, "• Низький ризик колізій", size=10.5, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_box + 130, "• Дальність: мала / середня", size=10.5, color=MUTED, anchor="start", italic=True))

    # Box 2: Medium SF (SF9)
    p.append(rect(x2, y_box, col_w, col_h, fill="#dfe7fb", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(x2 + col_w/2, y_box + 26, "Баланс (SF9)", size=12, color=FIELD, bold=True))
    p.append(text(x2 + 15, y_box + 58, "• ToA ≈ 140 мс", size=10.5, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_box + 82, "• Збалансований заряд", size=10.5, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_box + 106, "• Помірне навантаження", size=10.5, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_box + 130, "• Дальність: впевнена", size=10.5, color=MUTED, anchor="start", italic=True))

    # Box 3: High SF (SF12)
    p.append(rect(x3, y_box, col_w, col_h, fill="#fcd8d4", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x3 + col_w/2, y_box + 26, "Довгий ToA (SF12)", size=12, color=NEG, bold=True))
    p.append(text(x3 + 15, y_box + 58, "• ToA > 1100 мс", size=10.5, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_box + 82, "• Витрата батареї ×28", size=10.5, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_box + 106, "• Високий ризик колізій", size=10.5, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_box + 130, "• Дальність: максимальна", size=10.5, color=MUTED, anchor="start", italic=True))

    p.append(text(W / 2, H - 14,
                  "Компроміс радіозв'язку: тривалість передачі визначає споживання енергії та ємність всієї мережі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "energy-tradeoff.svg"), W, H, *p,
           title="Компроміс між дальністю, споживанням енергії та часом у ефірі")

if __name__ == "__main__":
    fig_packet_structure()
    fig_sf_comparison()
    fig_duty_cycle()
    fig_energy_tradeoff()
    print("OK: figures written to", OUT)
