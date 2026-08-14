# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: LNA vs PA — дві крайнощі радіотракту ───────────────────────────
def fig_lna_vs_pa():
    W, H = 760, 320
    p = []
    
    # Заголовок / розділення двох блоків
    p.append(rect(10, 10, 740, 300, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    
    # Ліва частина: LNA (Приймальний тракт)
    p.append(rect(25, 25, 345, 270, fill="#f0f4fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(197, 50, "Приймач: LNA (Малошумний)", size=15, color=NEG, bold=True))
    
    b1, w1, h1 = textbox(197, 100, "Вхід від антени\nP_in = -100 dBm (5 µV)", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b1)
    
    p.append(arrow(197, 125, 197, 150, color=NEG, sw=2))
    
    b2, w2, h2 = textbox(197, 185, "LNA (МШУ)\nПідсилення G = +20 dB\nШум NF = 0.8 dB", size=13, fill="#e0ebfd", stroke=NEG, sw=2, color=INK, bold=True)
    p.append(b2)
    
    p.append(arrow(197, 220, 197, 245, color=NEG, sw=2))
    
    b3, w3, h3 = textbox(197, 268, "До змішувача / ПЧ\nP_out = -80 dBm", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b3)

    # Права частина: PA (Передавальний тракт)
    p.append(rect(390, 25, 345, 270, fill="#fdf2f0", stroke=POS, sw=1.5, rx=6))
    p.append(text(562, 50, "Передавач: PA (Потужний)", size=15, color=POS, bold=True))
    
    b4, w4, h4 = textbox(562, 100, "Від модулятора / ВЧ\nP_in = 0 dBm (1 mW)", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b4)
    
    p.append(arrow(562, 125, 562, 150, color=POS, sw=2))
    
    b5, w5, h5 = textbox(562, 185, "PA (ПП)\nПідсилення G = +30 dB\nВихід P_out = +30 dBm (1 W)\nККД / PAE = 55%", size=13, fill="#fde4e1", stroke=POS, sw=2, color=INK, bold=True)
    p.append(b5)
    
    p.append(arrow(562, 220, 562, 245, color=POS, sw=2))
    
    b6, w6, h6 = textbox(562, 268, "Вихід у антену\n1 Ватт радіохвиль", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b6)
    
    return render(os.path.join(OUT, "lna-vs-pa.svg"), W, H, *p)


# ── Фігура 2: Формула Фрііса для каскадного коефіцієнта шуму ─────────────────
def fig_friis_noise():
    W, H = 760, 320
    p = []
    
    # Тракт із 3 каскадів
    p.append(rect(10, 10, 740, 300, fill="#f9fafb", stroke=LINE, sw=1, rx=8))
    p.append(text(380, 35, "Розподіл шумів у каскадному приймальному тракті", size=16, color=INK, bold=True))
    
    # Каскад 1: LNA
    b1, w1, h1 = textbox(130, 110, "Каскад 1: LNA\nNF1 = 1.0 dB (F1 = 1.26)\nG1 = 18 dB (G1 = 63.1)", size=12, fill="#e8f4ec", stroke=FIELD, sw=2, bold=True)
    p.append(b1)
    
    p.append(arrow(220, 110, 270, 110, color=LINE, sw=2))
    
    # Каскад 2: Фільтр
    b2, w2, h2 = textbox(380, 110, "Каскад 2: Фільтр\nNF2 = 2.0 dB (F2 = 1.58)\nG2 = -2.0 dB (G2 = 0.63)", size=12, fill="#ffffff", stroke=MUTED, sw=1.5)
    p.append(b2)
    
    p.append(arrow(490, 110, 540, 110, color=LINE, sw=2))
    
    # Каскад 3: Змішувач / ПЧ
    b3, w3, h3 = textbox(630, 110, "Каскад 3: Змішувач\nNF3 = 8.0 dB (F3 = 6.31)\nG3 = 10 dB", size=12, fill="#fdecea", stroke=POS, sw=1.5)
    p.append(b3)
    
    # Внески у формулу Фрііса
    p.append(line(50, 180, 710, 180, color=MUTED, sw=1, dash="4,4"))
    
    p.append(text(380, 205, "Формула Фрііса: F_total = F1 + (F2 - 1)/G1 + (F3 - 1)/(G1·G2)", size=14, color=INK, bold=True))
    
    b4, w4, h4 = textbox(130, 260, "Внесок LNA:\nF1 = 1.259\n(Визначний)", size=12, fill="#e8f4ec", stroke=FIELD)
    p.append(b4)
    
    p.append(text(245, 260, "+", size=20, color=INK, bold=True))
    
    b5, w5, h5 = textbox(380, 260, "Внесок фільтра:\n0.58 / 63.1 = 0.009\n(Мізерний)", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b5)
    
    p.append(text(515, 260, "+", size=20, color=INK, bold=True))
    
    b6, w6, h6 = textbox(630, 260, "Внесок змішувача:\n5.31 / 39.8 = 0.133\n(Придушений в G1)", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b6)
    
    return render(os.path.join(OUT, "friis-noise.svg"), W, H, *p)


# ── Фігура 3: Класи підсилення PA ───────────────────────────────────────────
def fig_pa_classes():
    W, H = 760, 340
    p = []
    
    p.append(rect(10, 10, 740, 320, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(380, 35, "Порівняння режимів підсилювачів потужності (PA)", size=16, color=INK, bold=True))
    
    # Таблична сітка класів
    classes = [
        ("Клас A", "360°", "Максимальна", "20 – 30%", "#eef2ff", NEG),
        ("Клас AB", "200° – 260°", "Висока (QAM, OFDM)", "50 – 65%", "#f0fdf4", FIELD),
        ("Клас B", "180°", "Середня (гармоніки)", "70 – 78%", "#fffbe1", INK),
        ("Клас C", "< 180°", "Низька (лише FM/CW)", "80 – 85%", "#fff1f2", POS),
        ("Клас E / F", "Ключовий", "Спеціальна (ZVS)", "85 – 95%", "#faf5ff", "#7e22ce")
    ]
    
    # Шапка таблиці
    y_start = 65
    p.append(rect(20, y_start, 720, 35, fill="#f3f4f6", stroke=LINE, sw=1, rx=4))
    p.append(text(90, y_start + 23, "Клас", size=13, color=INK, bold=True))
    p.append(text(210, y_start + 23, "Кут відсічки", size=13, color=INK, bold=True))
    p.append(text(390, y_start + 23, "Лінійність сигналу", size=13, color=INK, bold=True))
    p.append(text(610, y_start + 23, "Реальний ККД (PAE)", size=13, color=INK, bold=True))
    
    row_y = y_start + 42
    for name, angle, lin, eff, bg_col, txt_col in classes:
        p.append(rect(20, row_y, 720, 42, fill=bg_col, stroke=MUTED, sw=1, rx=4))
        p.append(text(90, row_y + 26, name, size=14, color=txt_col, bold=True))
        p.append(text(210, row_y + 26, angle, size=13, color=INK))
        p.append(text(390, row_y + 26, lin, size=13, color=INK))
        p.append(text(610, row_y + 26, eff, size=14, color=txt_col, bold=True))
        row_y += 48
        
    return render(os.path.join(OUT, "pa-classes.svg"), W, H, *p)


# ── Фігура 4: Лінійність, точка компресії P1dB та точка IP3 ──────────────────
def fig_linearity_p1db_ip3():
    W, H = 760, 400
    p = []
    
    ox, oy = 80, 330
    w_ax, h_ax = 620, 280
    
    p.append(rect(10, 10, 740, 380, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(380, 32, "Характеристика лінійності: P1dB та точка перетину IP3", size=16, color=INK, bold=True))
    
    # Осі координат
    p.append(line(ox, oy, ox + w_ax, oy, color=INK, sw=1.5))
    p.append(arrow(ox + w_ax - 10, oy, ox + w_ax + 10, oy, color=INK, sw=1.5))
    p.append(text(ox + w_ax + 15, oy + 5, "P_in (dBm)", size=13, color=INK, bold=True, anchor="start"))
    
    p.append(line(ox, oy, ox, oy - h_ax, color=INK, sw=1.5))
    p.append(arrow(ox, oy - h_ax + 10, ox, oy - h_ax - 5, color=INK, sw=1.5))
    p.append(text(ox - 10, oy - h_ax - 5, "P_out (dBm)", size=13, color=INK, bold=True, anchor="end"))
    
    # Основний сигнал (нахил 1:1) — ідеальна пряма
    p.append(line(ox + 40, oy - 40, ox + 450, oy - 245, color=NEG, sw=1.5, dash="4,4"))
    
    # Основний сигнал — реальна крива з компресією
    pts_fund = f"{ox+40},{oy-40} {ox+200},{oy-120} {ox+300},{oy-165} {ox+360},{oy-185} {ox+440},{oy-195} {ox+520},{oy-200}"
    p.append(f'<polyline points="{pts_fund}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    p.append(text(ox + 450, oy - 210, "Основний сигнал (P_out)", size=12, color=NEG, bold=True, anchor="start"))
    
    # Продукт IMD3 (нахил 3:1) — ідеальна пряма та екстраполяція
    pts_imd3 = f"{ox+150},{oy-20} {ox+300},{oy-90} {ox+450},{oy-160} {ox+530},{oy-281}"
    p.append(f'<polyline points="{pts_imd3}" fill="none" stroke="{POS}" stroke-width="2.0"/>')
    p.append(text(ox + 480, oy - 130, "Інтермодуляція IMD3", size=12, color=POS, bold=True, anchor="start"))
    
    # Точка P1dB
    px1, py1 = ox + 300, oy - 165
    p.append(circle(px1, py1, 5, fill=POS, stroke=INK, sw=1.5))
    b_p1, w_p1, h_p1 = textbox(px1 - 60, py1 - 25, "P1dB (компресія 1 dB)", size=11, fill="#fff1f2", stroke=POS)
    p.append(b_p1)
    
    # Точка перетину IP3 (перетин екстраполяцій)
    pip3_x, pip3_y = ox + 530, oy - 281
    p.append(circle(pip3_x, pip3_y, 6, fill=FIELD, stroke=INK, sw=2))
    b_ip3, w_ip3, h_ip3 = textbox(pip3_x - 70, pip3_y - 25, "Точка IP3 (IIP3 / OIP3)", size=12, fill="#e8f4ec", stroke=FIELD, bold=True)
    p.append(b_ip3)
    
    # Пунктири до осей для IP3
    p.append(line(pip3_x, pip3_y, pip3_x, oy, color=MUTED, sw=1, dash="2,2"))
    p.append(line(pip3_x, pip3_y, ox, pip3_y, color=MUTED, sw=1, dash="2,2"))
    p.append(text(pip3_x, oy + 18, "IIP3", size=12, color=FIELD, bold=True))
    p.append(text(ox - 25, pip3_y + 4, "OIP3", size=12, color=FIELD, bold=True))
    
    return render(os.path.join(OUT, "linearity-p1db-ip3.svg"), W, H, *p)


# ── Запуск генерації ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_lna_vs_pa()
    fig_friis_noise()
    fig_pa_classes()
    fig_linearity_p1db_ip3()
    print("Всі SVG-фігури успішно згенеровано у", OUT)
