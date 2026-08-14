# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для теми book/communications/radio-engineering/return-loss
"""

import sys
import os

# Вказуємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_fig1_concept(path):
    """Фігура 1: Концепція зворотних втрат (P_inc, P_ref, Gamma, RL)."""
    w, h = 760, 360
    elements = []
    
    # Заголовок
    elements.append(text(w / 2, 25, "Концепція зворотних втрат (Return Loss) у лінії передачі", size=16, bold=True))
    
    # Генератор / Передавач
    b_gen = fitbox(30, 80, 130, 80, "Джерело ВЧ\n(Z₀ = 50 Ом)", size=13, fill="#e8f0fe", stroke=NEG)
    elements.append(b_gen)
    
    # Лінія передачі (фідер)
    elements.append(rect(200, 105, 340, 30, fill="#f8f9fa", stroke=LINE, sw=1.5))
    elements.append(text(370, 125, "Лінія передачі (хвильовий опір Z₀ = 50 Ом)", size=12, color=MUTED))
    
    # Навантаження (Антена)
    b_load = fitbox(580, 80, 140, 80, "Навантаження Z_L\n(Антена / DUT)\nZ_L ≠ Z₀", size=13, fill="#fdecea", stroke=POS)
    elements.append(b_load)
    
    # З'єднання
    elements.append(line(160, 120, 200, 120, color=LINE, sw=2))
    elements.append(line(540, 120, 580, 120, color=LINE, sw=2))
    
    # Падаюча хвиля (P_inc)
    elements.append(arrow(220, 80, 480, 80, color=FIELD, sw=2.5))
    elements.append(text(350, 70, "Падаюча потужність P_inc (ВЧ-сигнал)", size=12, color=FIELD, bold=True))
    
    # Відбита хвиля (P_ref)
    elements.append(arrow(480, 160, 220, 160, color=POS, sw=2.5))
    elements.append(text(350, 178, "Відбита потужність P_ref (через неузгодження)", size=12, color=POS, bold=True))
    
    # Формули в нижніх блоках
    box_gamma = fitbox(30, 215, 340, 125, 
                       "Коефіцієнт відбиття за напругою (Γ):\n"
                       "Γ = (Z_L − Z₀) / (Z_L + Z₀)\n"
                       "|Γ| = √(P_ref / P_inc)", 
                       size=12, fill="#ffffff", stroke=LINE)
    elements.append(box_gamma)
    
    box_rl = fitbox(390, 215, 340, 125, 
                     "Зворотні втрати (Return Loss, RL):\n"
                     "RL = 10 · log₁₀(P_inc / P_ref) [дБ]\n"
                     "RL = −20 · log₁₀|Γ| [дБ]\n"
                     "Чим вище RL в дБ, тим менше відбиття!", 
                     size=12, fill="#e6f4ea", stroke=FIELD, bold=False)
    elements.append(box_rl)
    
    body = "".join(elements)
    render(path, w, h, body)

def make_fig2_s11_curve(path):
    """Фігура 2: Частотна характеристика S11 (Return Loss) на графіку VNA."""
    w, h = 760, 400
    elements = []
    
    elements.append(text(w / 2, 25, "Частотна характеристика S₁₁ та смуга узгодження антени", size=16, bold=True))
    
    # Осі координат
    ox, oy = 80, 320
    gw, gh = 620, 250
    
    # Рамка графіка
    elements.append(rect(ox, oy - gh, gw, gh, fill="#fafafa", stroke=LINE, sw=1.5))
    
    # Сітка та позначки по Y (S11 в дБ від 0 до -35)
    y_levels = [
        (0, "0 дБ (100% відб.)", POS),
        (-5, "−5 дБ", INK),
        (-10, "−10 дБ (порог 90% поглинання)", FIELD),
        (-15, "−15 дБ", INK),
        (-20, "−20 дБ (1% відб., відмінно)", FIELD),
        (-25, "−25 дБ", INK),
        (-30, "−30 дБ (0.1% відб.)", INK)
    ]
    
    for val, label, col in y_levels:
        y_pos = oy - gh + int((-val / 35.0) * gh)
        dash_style = "4,4" if val != 0 else None
        elements.append(line(ox, y_pos, ox + gw, y_pos, color=MUTED if val != -10 else FIELD, sw=1.2 if val == -10 else 0.8, dash=dash_style))
        elements.append(text(ox - 10, y_pos + 4, label, size=10, color=col, anchor="end"))
        
    # Позначки по X (Частота f)
    elements.append(text(ox + gw / 2, oy + 45, "Частота f [ГГц]", size=13, bold=True))
    elements.append(text(ox, oy + 20, "2.30", size=11, color=MUTED))
    elements.append(text(ox + gw * 0.35, oy + 20, "2.40 (f_low)", size=11, color=MUTED))
    elements.append(text(ox + gw * 0.5, oy + 20, "2.45 (f₀)", size=11, color=FIELD, bold=True))
    elements.append(text(ox + gw * 0.65, oy + 20, "2.50 (f_high)", size=11, color=MUTED))
    elements.append(text(ox + gw, oy + 20, "2.60", size=11, color=MUTED))
    
    # Крива S11 (лоренцівська/параболічна резонансна крива)
    points = []
    num_pts = 100
    for i in range(num_pts + 1):
        rel_x = i / float(num_pts)
        fx = 2.30 + rel_x * 0.30
        dev = (fx - 2.45) / 0.04
        s11_db = -2.0 - 26.0 / (1.0 + dev * dev)
        
        px = ox + rel_x * gw
        py = oy - gh + (-s11_db / 35.0) * gh
        points.append((px, py))
        
    path_d = "M " + " L ".join("%.1f,%.1f" % pt for pt in points)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, NEG))
    
    # Вертикальні лінії смуги пропускання на рівні -10 дБ
    x_flow = ox + (1.0 / 3.0) * gw
    x_fhigh = ox + (2.0 / 3.0) * gw
    y_10db = oy - gh + (10.0 / 35.0) * gh
    
    elements.append(line(x_flow, oy - gh, x_flow, oy, color=FIELD, sw=1, dash="3,3"))
    elements.append(line(x_fhigh, oy - gh, x_fhigh, oy, color=FIELD, sw=1, dash="3,3"))
    
    # Стрілка смуги пропускання BW
    elements.append(line(x_flow, y_10db, x_fhigh, y_10db, color=FIELD, sw=1.8))
    elements.append(circle(x_flow, y_10db, 4, fill=FIELD, stroke=FIELD))
    elements.append(circle(x_fhigh, y_10db, 4, fill=FIELD, stroke=FIELD))
    elements.append(text(ox + gw * 0.5, y_10db - 10, "Робоча смуга BW (RL ≥ 10 дБ)", size=12, color=FIELD, bold=True))
    
    # Точка мінімуму (резонанс)
    x_f0 = ox + 0.5 * gw
    y_min = oy - gh + (28.0 / 35.0) * gh
    elements.append(circle(x_f0, y_min, 5, fill=POS, stroke=POS))
    elements.append(text(x_f0 + 15, y_min + 5, "Точка резонансу: RL = 28 дБ (S₁₁ = −28 дБ)", size=11, color=POS, bold=True))
    
    body = "".join(elements)
    render(path, w, h, body)

def make_fig3_vna_diagram(path):
    """Фігура 3: Схема вимірювання зворотних втрат за допомогою VNA та спрямованого відгалужувача."""
    w, h = 760, 320
    elements = []
    
    elements.append(text(w / 2, 25, "Структурна схема вимірювання S₁₁ у Векторному Аналізаторі Кіл (VNA)", size=16, bold=True))
    
    # Генератор сигналів
    elements.append(fitbox(30, 85, 140, 70, "ВЧ-Синтезатор\n(Джерело f)", size=12, fill="#e8f0fe", stroke=NEG))
    elements.append(arrow(170, 120, 230, 120, color=LINE, sw=2))
    
    # Спрямований відгалужувач (Directional Coupler)
    elements.append(rect(230, 65, 200, 135, fill="#fff8e1", stroke="#f39c12", sw=2))
    elements.append(text(330, 85, "Спрямований відгалужувач", size=12, bold=True, color="#b7950b"))
    elements.append(text(330, 100, "(Directional Coupler)", size=10, color=MUTED))
    
    # Лінії всередині відгалужувача
    elements.append(line(230, 120, 430, 120, color=LINE, sw=2))
    elements.append(line(260, 165, 400, 165, color=MUTED, sw=1.5, dash="4,2"))
    
    # Зв'язок між лініями
    elements.append(arrow(310, 120, 310, 165, color=FIELD, sw=1.5))
    elements.append(arrow(360, 120, 360, 165, color=POS, sw=1.5))
    
    # Відгалуження до приймачів
    elements.append(arrow(430, 120, 540, 120, color=LINE, sw=2))
    elements.append(fitbox(540, 85, 180, 70, "Вимірюваний пристрій\n(DUT / Антена)", size=12, fill="#fdecea", stroke=POS))
    
    # Приймачі R1 та R2
    elements.append(arrow(260, 165, 260, 235, color=FIELD, sw=2))
    elements.append(fitbox(180, 235, 140, 55, "Приймач A\n(Падаюча P_inc)", size=11, fill="#e6f4ea", stroke=FIELD))
    
    elements.append(arrow(400, 165, 400, 235, color=POS, sw=2))
    elements.append(fitbox(340, 235, 140, 55, "Приймач B\n(Відбита P_ref)", size=11, fill="#fdecea", stroke=POS))
    
    # Блок обчислення DSP
    elements.append(arrow(320, 262, 500, 262, color=LINE, sw=2))
    elements.append(fitbox(500, 230, 220, 65, "Процесор DSP / Екран\nS₁₁ [дБ] = 20 log₁₀(|B| / |A|)\nRL = −S₁₁ [дБ]", size=11, fill="#f4f6f8", stroke=NEG, bold=True))
    
    body = "".join(elements)
    render(path, w, h, body)

def make_fig4_attenuator(path):
    """Фігура 4: Покращення зворотних втрат за допомогою резистивного атенюатора."""
    w, h = 760, 320
    elements = []
    
    elements.append(text(w / 2, 25, "Покращення зворотних втрат за допомогою атенюатора (Буферизація)", size=16, bold=True))
    
    # Передавач
    elements.append(fitbox(30, 80, 130, 75, "Передавач\n(Z₀ = 50 Ом)", size=12, fill="#e8f0fe", stroke=NEG))
    
    # Атенюатор 3 дБ
    elements.append(arrow(160, 117, 240, 117, color=LINE, sw=2))
    elements.append(fitbox(240, 80, 150, 75, "Атенюатор\n3 дБ (50 Ом)", size=13, fill="#fff8e1", stroke="#f39c12", bold=True))
    
    # Погане навантаження
    elements.append(arrow(390, 117, 470, 117, color=LINE, sw=2))
    elements.append(fitbox(470, 80, 160, 75, "Неузгоджене\nнавантаження\nRL_load = 6 дБ", size=12, fill="#fdecea", stroke=POS))
    
    # Пряма хвиля
    elements.append(arrow(170, 70, 230, 70, color=FIELD, sw=2))
    elements.append(text(200, 60, "0 дБ", size=11, color=FIELD, bold=True))
    
    elements.append(arrow(400, 70, 460, 70, color=FIELD, sw=2))
    elements.append(text(430, 60, "−3 дБ", size=11, color=FIELD, bold=True))
    
    # Відбита хвиля
    elements.append(arrow(460, 165, 400, 165, color=POS, sw=2))
    elements.append(text(430, 180, "−9 дБ (відб. 6 дБ)", size=11, color=POS, bold=True))
    
    elements.append(arrow(230, 165, 170, 165, color=POS, sw=2))
    elements.append(text(200, 180, "−12 дБ (ще −3 дБ)", size=11, color=POS, bold=True))
    
    # Пояснювальний блок
    box_exp = fitbox(180, 215, 480, 90,
                     "Формула подвійного проходу загасання:\n"
                     "RL_вхід = RL_навантаження + 2 · A_ат\n"
                     "RL_вхід = 6 дБ + 2 · 3 дБ = 12 дБ (покращення на +6 дБ!)\n"
                     "Ціна: прямому сигналу завдається втрата 3 дБ, але зворотне відбиття послаблюється двічі.",
                     size=11, fill="#e6f4ea", stroke=FIELD)
    elements.append(box_exp)
    
    body = "".join(elements)
    render(path, w, h, body)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    figs = [
        ("return-loss-concept.svg", make_fig1_concept),
        ("s11-vna-curve.svg", make_fig2_s11_curve),
        ("vna-reflectometer.svg", make_fig3_vna_diagram),
        ("attenuator-buffer.svg", make_fig4_attenuator),
    ]
    
    for filename, func in figs:
        path = os.path.join(img_dir, filename)
        func(path)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    main()

