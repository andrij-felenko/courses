# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

def make_grounding_principle():
    w, h = 760, 420
    frags = []
    
    # Заголовок
    frags.append(text(w/2, 28, "Принцип дії захисного заземлення при пробої фази на корпус", size=16, bold=True))
    
    # Трафо / Джерело (ліворуч)
    frags.append(rect(40, 70, 140, 180, fill="#eef2f7", stroke=LINE, sw=1.5))
    frags.append(text(110, 95, "Трансформатор", size=13, bold=True))
    frags.append(text(110, 115, "230 В / 50 Гц", size=12, color=MUTED))
    
    # Виводи джерела
    frags.append(circle(160, 140, 5, fill=POS, stroke=LINE, sw=1))
    frags.append(text(145, 145, "L", size=12, bold=True, color=POS, anchor="end"))
    
    frags.append(circle(160, 200, 5, fill=NEG, stroke=LINE, sw=1))
    frags.append(text(145, 205, "N", size=12, bold=True, color=NEG, anchor="end"))
    
    # Робоче заземлення нейтралі джерела (R0)
    frags.append(line(160, 200, 160, 310, color=NEG, sw=2))
    frags.append(rect(145, 310, 30, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(160, 334, "R₀", size=12, bold=True))
    frags.append(line(160, 350, 160, 370, color=LINE, sw=2))
    # Знак заземлення
    frags.append(line(145, 370, 175, 370, color=LINE, sw=2.5))
    frags.append(line(150, 375, 170, 375, color=LINE, sw=2))
    frags.append(line(155, 380, 165, 380, color=LINE, sw=1.5))
    frags.append(text(110, 335, "R₀ = 2 Ом\n(нейтраль)", size=11, color=MUTED, anchor="end"))

    # Фазний та нейтральний провідники
    frags.append(line(160, 140, 480, 140, color=POS, sw=2.5))
    frags.append(text(310, 130, "Фазний провідник L", size=12, color=POS, bold=True))
    
    frags.append(line(160, 200, 480, 200, color=NEG, sw=2, dash="6,4"))
    frags.append(text(310, 190, "Робочий нуль N", size=12, color=NEG, bold=True))
    
    # Прилад споживача (металевий корпус)
    frags.append(rect(480, 100, 200, 180, fill="#f9fafd", stroke="#4a5568", sw=2, rx=8))
    frags.append(text(580, 125, "Електроприлад", size=14, bold=True))
    frags.append(text(580, 143, "(металевий корпус)", size=11, color=MUTED))
    
    # Пробій ізоляції усередині приладу
    frags.append(line(480, 140, 530, 140, color=POS, sw=2))
    frags.append(circle(530, 140, 4, fill=POS))
    # Коротке замикання на корпус
    frags.append(line(530, 140, 530, 170, color=POS, sw=2, dash="3,3"))
    frags.append(line(530, 170, 480, 170, color=POS, sw=2.5))
    frags.append(text(540, 160, "Пробій!", size=11, color=POS, bold=True, anchor="start"))
    
    # Захисне заземлення корпусу (Re)
    frags.append(line(580, 280, 580, 310, color=FIELD, sw=2.5))
    frags.append(rect(565, 310, 30, 40, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(580, 334, "Rₑ", size=12, bold=True, color=FIELD))
    frags.append(line(580, 350, 580, 370, color=FIELD, sw=2))
    # Знак заземлення корпусу
    frags.append(line(565, 370, 595, 370, color=FIELD, sw=2.5))
    frags.append(line(570, 375, 590, 375, color=FIELD, sw=2))
    frags.append(line(575, 380, 585, 380, color=FIELD, sw=1.5))
    frags.append(text(640, 335, "Rₑ = 4 Ом\n(захисне)", size=11, color=FIELD, anchor="start"))

    # Струм короткого замикання через заземлення
    frags.append(arrow(350, 150, 420, 150, color=POS, sw=2))
    frags.append(text(385, 170, "I_зз = U / (R₀ + Rₑ) ≈ 38.3 А", size=11, color=POS, bold=True))
    
    # Струм через людину
    frags.append(line(680, 190, 720, 190, color=LINE, sw=1.5))
    frags.append(circle(720, 210, 12, fill="#fff3cd", stroke=LINE, sw=1.5)) # голова
    frags.append(line(720, 222, 720, 270, color=LINE, sw=2)) # тулуб
    frags.append(line(720, 235, 680, 190, color=LINE, sw=1.5)) # рука до корпусу
    frags.append(line(720, 270, 710, 330, color=LINE, sw=2)) # нога 1
    frags.append(line(720, 270, 730, 330, color=LINE, sw=2)) # нога 2
    
    # Опір людини Rh
    frags.append(text(720, 348, "Людина\nR_люд ≈ 1000 Ом", size=10, color=INK))
    
    # Напруга дотику
    frags.append(rect(240, 360, 260, 50, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    frags.append(text(370, 380, "U_дотику = I_зз · Rₑ ≈ 153 В (TT)", size=11, bold=True, color=INK))
    frags.append(text(370, 398, "Вимикач / ПЗВ швидко знеструмлює мережу!", size=10, color=FIELD, bold=True))
    
    render(os.path.join(os.path.dirname(__file__), "img", "grounding-principle.svg"), w, h, *frags)

def make_potential_funnel():
    w, h = 780, 480
    frags = []
    
    frags.append(text(w/2, 28, "Потенціальна воронка розтікання струму, напруга дотику та кроку", size=16, bold=True))
    
    # Графік потенціалу V(r) у верхній частині
    gx0, gy0, gw, gh = 80, 70, 620, 170
    
    # Осі координат
    frags.append(line(gx0, gy0 + gh, gx0 + gw, gy0 + gh, color=LINE, sw=1.5)) # вісь X (відстань r)
    frags.append(line(gx0 + gw/2, gy0 + gh + 10, gx0 + gw/2, gy0, color=LINE, sw=1.5)) # вісь V
    frags.append(text(gx0 + gw/2 - 15, gy0 + 15, "V (В)", size=12, bold=True))
    frags.append(text(gx0 + gw - 20, gy0 + gh + 25, "r (м)", size=12, bold=True))
    
    # Крива розтікання V(r) = V0 / |r|
    cx = gx0 + gw/2
    curve_points = []
    for px in range(int(gx0 + 20), int(gx0 + gw - 20), 4):
        dx = abs(px - cx)
        if dx < 15:
            vy = gy0 + 20
        else:
            vy = gy0 + gh - (gh - 30) * (20.0 / (dx + 5))
        curve_points.append((px, vy))
        
    for i in range(len(curve_points) - 1):
        x1, y1 = curve_points[i]
        x2, y2 = curve_points[i+1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.5))
        
    frags.append(text(cx + 40, gy0 + 35, "V(r) = (I · ρ) / (2πr)", size=12, color=POS, bold=True))
    
    # Поверхня землі (лінія розділу)
    sy = 300
    frags.append(line(40, sy, 740, sy, color="#8b5a2b", sw=3))
    frags.append(text(60, sy + 30, "Ґрунт (питомий опір ρ)", size=12, color="#8b5a2b", italic=True))
    
    # Заземлювальний стрижень у центрі
    frags.append(rect(cx - 6, sy - 40, 12, 110, fill="#718096", stroke=LINE, sw=1.5))
    frags.append(text(cx, sy - 50, "Електрод заземлення", size=11, bold=True))
    
    # Півсфери розтікання в ґрунті
    for r_val in [35, 75, 125, 185]:
        frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' % (cx, sy, r_val, FIELD))
        
    frags.append(text(cx + 90, sy + 60, "Еквіпотенціальні лінії", size=10, color=FIELD, italic=True))
    
    # Точка А (на заземлювачі) та Точка Б (крок)
    # Напруга дотику (Touch voltage)
    frags.append(line(cx, gy0 + 20, cx, sy - 40, color=MUTED, sw=1, dash="2,2"))
    x_feet1 = cx + 110
    vy_feet1 = gy0 + gh - (gh - 30) * (20.0 / (110 + 5))
    frags.append(line(x_feet1, vy_feet1, x_feet1, sy, color=MUTED, sw=1, dash="2,2"))
    
    # Позначення U_дотику
    frags.append(arrow(cx + 10, gy0 + 30, x_feet1 - 10, gy0 + 30, color=POS, sw=1.5))
    frags.append(arrow(x_feet1 - 10, gy0 + 30, cx + 10, gy0 + 30, color=POS, sw=1.5))
    frags.append(text((cx + x_feet1)/2, gy0 + 20, "U_дотику", size=11, color=POS, bold=True))
    
    # Людина торкається заземлювача (рука на заземлювачі, ноги на х_feet1)
    frags.append(circle(x_feet1, sy - 70, 10, fill="#fff3cd", stroke=LINE, sw=1.2)) # голова
    frags.append(line(x_feet1, sy - 60, x_feet1, sy - 20, color=LINE, sw=1.5)) # тулуб
    frags.append(line(x_feet1, sy - 50, cx, sy - 30, color=LINE, sw=1.5)) # рука до електрода
    frags.append(line(x_feet1, sy - 20, x_feet1 - 10, sy, color=LINE, sw=1.5)) # нога
    frags.append(line(x_feet1, sy - 20, x_feet1 + 10, sy, color=LINE, sw=1.5)) # нога
    
    # Напруга кроку (Step voltage) праворуч
    x_step1 = cx + 200
    x_step2 = cx + 260
    vy_s1 = gy0 + gh - (gh - 30) * (20.0 / (200 + 5))
    vy_s2 = gy0 + gh - (gh - 30) * (20.0 / (260 + 5))
    
    frags.append(line(x_step1, vy_s1, x_step1, sy, color=NEG, sw=1, dash="2,2"))
    frags.append(line(x_step2, vy_s2, x_step2, sy, color=NEG, sw=1, dash="2,2"))
    
    frags.append(arrow(x_step1, vy_s1 - 15, x_step2, vy_s1 - 15, color=NEG, sw=1.5))
    frags.append(text((x_step1 + x_step2)/2, vy_s1 - 25, "U_кроку", size=11, color=NEG, bold=True))
    
    # Людина робить крок
    frags.append(circle((x_step1+x_step2)/2, sy - 70, 10, fill="#e8f4f8", stroke=LINE, sw=1.2))
    frags.append(line((x_step1+x_step2)/2, sy - 60, (x_step1+x_step2)/2, sy - 20, color=LINE, sw=1.5))
    frags.append(line((x_step1+x_step2)/2, sy - 20, x_step1, sy, color=LINE, sw=1.5)) # нога 1
    frags.append(line((x_step1+x_step2)/2, sy - 20, x_step2, sy, color=LINE, sw=1.5)) # нога 2
    frags.append(text((x_step1+x_step2)/2, sy + 20, "Крок a = 0.8 м", size=10, color=MUTED))

    render(os.path.join(os.path.dirname(__file__), "img", "potential-funnel.svg"), w, h, *frags)

def make_earthing_systems():
    w, h = 840, 520
    frags = []
    
    frags.append(text(w/2, 26, "Класифікація систем заземлення (IEC 60364)", size=16, bold=True))
    
    systems = [
        ("TN-S", "Роздільні N і PE від джерела", "#eef2f7", 50, 60),
        ("TN-C", "Суміщений PEN-провідник", "#fef3c7", 430, 60),
        ("TN-C-S", "Розділення PEN у ВРП будівлі", "#e0e7ff", 50, 280),
        ("TT", "Окремий заземлювач споживача", "#dcfce7", 430, 280),
    ]
    
    bw, bh = 360, 200
    for title, desc, bg_col, bx, by in systems:
        frags.append(rect(bx, by, bw, bh, fill=bg_col, stroke=LINE, sw=1.5, rx=8))
        frags.append(text(bx + 15, by + 25, title, size=15, bold=True, anchor="start"))
        frags.append(text(bx + 85, by + 25, "— " + desc, size=11, color=MUTED, anchor="start"))
        
        # Джерело
        frags.append(rect(bx + 20, by + 45, 60, 70, fill="#ffffff", stroke=LINE, sw=1))
        frags.append(text(bx + 50, by + 65, "Тр-р", size=11, bold=True))
        
        # Корпус приладу
        frags.append(rect(bx + 230, by + 45, 100, 70, fill="#ffffff", stroke=LINE, sw=1))
        frags.append(text(bx + 280, by + 65, "Корпус", size=11, bold=True))
        
        # Дріт L
        frags.append(line(bx + 80, by + 55, bx + 230, by + 55, color=POS, sw=2))
        frags.append(text(bx + 150, by + 50, "L", size=10, color=POS, bold=True))
        
        if title == "TN-S":
            frags.append(line(bx + 80, by + 75, bx + 230, by + 75, color=NEG, sw=1.5))
            frags.append(text(bx + 150, by + 71, "N (синій)", size=9, color=NEG))
            frags.append(line(bx + 80, by + 95, bx + 230, by + 95, color=FIELD, sw=1.5))
            frags.append(text(bx + 150, by + 91, "PE (жовто-зелений)", size=9, color=FIELD, bold=True))
            frags.append(line(bx + 50, by + 115, bx + 50, by + 150, color=LINE, sw=1.5))
            frags.append(line(bx + 35, by + 150, bx + 65, by + 150, color=LINE, sw=2))
            frags.append(text(bx + 50, by + 165, "R_знам", size=9, color=MUTED))
            frags.append(line(bx + 280, by + 95, bx + 280, by + 115, color=FIELD, sw=1.5))
            frags.append(text(bx + 180, by + 185, "Максимальна безпека, немає струму в PE", size=10, color=INK, italic=True))
            
        elif title == "TN-C":
            frags.append(line(bx + 80, by + 85, bx + 230, by + 85, color="#d97706", sw=2))
            frags.append(text(bx + 150, by + 80, "PEN (суміщений)", size=9, color="#d97706", bold=True))
            frags.append(line(bx + 280, by + 85, bx + 280, by + 115, color="#d97706", sw=1.5))
            frags.append(line(bx + 50, by + 115, bx + 50, by + 150, color=LINE, sw=1.5))
            frags.append(line(bx + 35, by + 150, bx + 65, by + 150, color=LINE, sw=2))
            frags.append(text(bx + 180, by + 185, "Небезпека при обриві PEN! Заборонено в сучасному житлі", size=10, color=POS, italic=True))

        elif title == "TN-C-S":
            frags.append(line(bx + 80, by + 85, bx + 160, by + 85, color="#d97706", sw=2))
            frags.append(text(bx + 120, by + 80, "PEN", size=9, color="#d97706", bold=True))
            frags.append(circle(bx + 160, by + 85, 4, fill="#d97706"))
            frags.append(line(bx + 160, by + 85, bx + 160, by + 140, color=FIELD, sw=1.5))
            frags.append(line(bx + 145, by + 140, bx + 175, by + 140, color=FIELD, sw=2))
            frags.append(text(bx + 160, by + 155, "Повторне R_повт", size=9, color=FIELD))
            frags.append(line(bx + 160, by + 75, bx + 230, by + 75, color=NEG, sw=1.5))
            frags.append(line(bx + 160, by + 95, bx + 230, by + 95, color=FIELD, sw=1.5))
            frags.append(line(bx + 280, by + 95, bx + 280, by + 115, color=FIELD, sw=1.5))
            frags.append(text(bx + 180, by + 185, "Основна система для нової забудови", size=10, color=INK, italic=True))

        elif title == "TT":
            frags.append(line(bx + 80, by + 85, bx + 230, by + 85, color=NEG, sw=1.5))
            frags.append(text(bx + 150, by + 80, "N", size=9, color=NEG))
            frags.append(line(bx + 50, by + 115, bx + 50, by + 140, color=LINE, sw=1.5))
            frags.append(line(bx + 35, by + 140, bx + 65, by + 140, color=LINE, sw=2))
            frags.append(line(bx + 280, by + 115, bx + 280, by + 140, color=FIELD, sw=1.5))
            frags.append(line(bx + 265, by + 140, bx + 295, by + 140, color=FIELD, sw=2))
            frags.append(text(bx + 280, by + 155, "R_спожив", size=9, color=FIELD))
            frags.append(text(bx + 180, by + 185, "Обов'язкове ПЗВ (RCD)! Струм ЗЗ малий", size=10, color=FIELD, italic=True))

    render(os.path.join(os.path.dirname(__file__), "img", "earthing-systems.svg"), w, h, *frags)

def make_equipotential_bonding():
    w, h = 760, 440
    frags = []
    
    frags.append(text(w/2, 26, "Система вирівнювання потенціалів у будівлі (MEB / SEB)", size=16, bold=True))
    
    # Стіни будівлі
    frags.append(rect(40, 60, 680, 340, fill="#fbfcfd", stroke="#94a3b8", sw=2, rx=10))
    frags.append(text(80, 85, "Будівля / Еквіпотенціальний контур", size=13, bold=True, color="#475569", anchor="start"))
    
    # Головна заземлювальна шина (ГЗШ / MET)
    frags.append(rect(100, 330, 260, 24, fill="#eab308", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(230, 346, "Головна заземлювальна шина (ГЗШ / MET)", size=11, bold=True, color=INK))
    
    # Фундаментний заземлювач
    frags.append(line(230, 354, 230, 390, color=FIELD, sw=2.5))
    frags.append(line(200, 390, 260, 390, color=FIELD, sw=3))
    frags.append(line(210, 395, 250, 395, color=FIELD, sw=2))
    frags.append(line(220, 400, 240, 400, color=FIELD, sw=1.5))
    frags.append(text(230, 418, "Фундаментний заземлювач", size=10, color=FIELD, bold=True))
    
    # Водопровід
    frags.append(rect(450, 110, 220, 25, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(560, 126, "Металевий водопровід", size=11, bold=True, color="#0369a1"))
    # Газопровід
    frags.append(rect(450, 160, 220, 25, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(560, 176, "Ввід газопроводу (ізолювальна вставка)", size=10, bold=True, color="#b45309"))
    # Металоконструкції
    frags.append(rect(450, 210, 220, 25, fill="#f1f5f9", stroke="#64748b", sw=1.5))
    frags.append(text(560, 226, "Сталевий каркас / арматура", size=11, bold=True, color="#334155"))
    
    # ВРП / Розподільчий щит
    frags.append(rect(100, 120, 140, 140, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(170, 145, "ВРП (Щит)", size=12, bold=True))
    frags.append(rect(115, 170, 110, 18, fill="#eab308", stroke=LINE, sw=1))
    frags.append(text(170, 183, "Шина PE", size=10, bold=True))
    frags.append(rect(115, 205, 110, 18, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(170, 218, "Шина N", size=10, bold=True, color="#ffffff"))
    
    # Зв'язки основної системи вирівнювання потенціалів (MEB)
    frags.append(line(170, 330, 170, 188, color=FIELD, sw=3))
    frags.append(line(320, 335, 450, 122, color=FIELD, sw=2.5))
    frags.append(line(340, 340, 450, 172, color=FIELD, sw=2.5))
    frags.append(line(360, 345, 450, 222, color=FIELD, sw=2.5))
    
    frags.append(text(380, 280, "Основна система (MEB)\nПровідники ≥ 6 мм² Cu", size=10, color=FIELD, bold=True))
    
    # Додаткова система (SEB)
    frags.append('<rect x="430.0" y="270.0" width="260.0" height="110.0" rx="6" fill="#f0fdf4" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % FIELD)
    frags.append(text(560, 290, "Ванна кімната (SEB / ДСВП)", size=11, bold=True, color=FIELD))
    frags.append(rect(450, 310, 70, 40, fill="#ffffff", stroke="#0284c7", sw=1.5))
    frags.append(text(485, 334, "Ванна", size=10, bold=True))
    frags.append(rect(580, 310, 90, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(625, 334, "Пральна маш.", size=10, bold=True))
    frags.append(line(485, 350, 625, 350, color=FIELD, sw=2))
    frags.append(text(555, 368, "Місцева шина ДСВП", size=9, color=FIELD))

    render(os.path.join(os.path.dirname(__file__), "img", "equipotential-bonding.svg"), w, h, *frags)

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    make_grounding_principle()
    make_potential_funnel()
    make_earthing_systems()
    make_equipotential_bonding()
    print("Figures generated successfully.")
