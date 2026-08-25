# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Принцип комплексно-спряженого узгодження ───────────────────────
def fig_matching_concept():
    W, H = 760, 310
    p = []
    
    p.append(rect(10, 10, 740, 290, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    
    # Лівий блок: Пряме з'єднання з неузгодженням
    p.append(rect(20, 25, 350, 260, fill="#fdf2f0", stroke=NEG, sw=1.5, rx=6))
    p.append(text(195, 48, "Пряме з'єднання (неузгоджено)", size=15, color=NEG, bold=True))
    
    b1, w1, h1 = textbox(195, 95, "Джерело сигналу\nZ_S = 50 + j20 Ом", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b1)
    
    p.append(arrow(195, 120, 195, 155, color=NEG, sw=2))
    p.append(text(205, 140, "Γ ≠ 0", size=11, color=NEG, bold=True))
    
    b2, w2, h2 = textbox(195, 195, "Навантаження (антена)\nZ_L = 10 - j40 Ом", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b2)
    
    b3, w3, h3 = textbox(195, 255, "Наслідок: відбиття хвилі, перевипромінення,\nвтрата потужності, нагрів передавача", size=11, fill="#fde4e1", stroke=NEG, color=INK)
    p.append(b3)
    
    # Правий блок: З'єднання через узгоджувальну ланку
    p.append(rect(390, 25, 350, 260, fill="#f0f4fd", stroke=POS, sw=1.5, rx=6))
    p.append(text(565, 48, "З вузлом узгодження (комплексне)", size=15, color=POS, bold=True))
    
    b4, w4, h4 = textbox(565, 90, "Джерело: Z_S = 50 + j20 Ом", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b4)
    
    p.append(arrow(565, 110, 565, 130, color=POS, sw=2))
    
    b5, w5, h5 = textbox(565, 160, "Коло узгодження (LC-ланка)\nПеретворює Z_L у Z_S* = 50 - j20 Ом", size=12, fill="#e0ebfd", stroke=POS, sw=2, color=INK, bold=True)
    p.append(b5)
    
    p.append(arrow(565, 190, 565, 210, color=POS, sw=2))
    
    b6, w6, h6 = textbox(565, 230, "Навантаження: Z_L = 10 - j40 Ом", size=12, fill="#ffffff", stroke=MUTED)
    p.append(b6)
    
    b7, w7, h7 = textbox(565, 268, "Результат: Γ = 0, максимальна передача", size=11, fill="#e8f4ec", stroke=POS, color=POS, bold=True)
    p.append(b7)
    
    return render(os.path.join(OUT, "matching-concept.svg"), W, H, *p)

# ── Фігура 2: Чотири базові конфігурації L-ланки ─────────────────────────────
def fig_l_network_topologies():
    W, H = 780, 360
    p = []
    
    p.append(rect(10, 10, 760, 340, fill="#f9fafb", stroke=LINE, sw=1, rx=8))
    p.append(text(390, 32, "Базові конфігурації L-ланок (Low-Pass та High-Pass)", size=16, color=INK, bold=True))
    
    # 1. ФНЧ зі зниженням опору (R_S > R_L)
    p.append(text(195, 65, "1. ФНЧ понижувальний (R_S > R_L)", size=13, color=INK, bold=True))
    b1, w1, h1 = textbox(70, 110, "Z_S (50 Ом)", size=11, fill="#f0f4fd", stroke=MUTED)
    p.append(b1)
    p.append(line(110, 110, 135, 110, color=LINE, sw=2))
    b2, w2, h2 = textbox(185, 110, "Індуктивність L\n(Послідовно)", size=11, fill="#e8f4ec", stroke=POS, bold=True)
    p.append(b2)
    p.append(line(235, 110, 270, 110, color=LINE, sw=2))
    p.append(line(270, 110, 270, 135, color=LINE, sw=2))
    b3, w3, h3 = textbox(270, 155, "Ємність C (Паралельно)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b3)
    p.append(line(270, 110, 290, 110, color=LINE, sw=2))
    b4, w4, h4 = textbox(320, 110, "Z_L (10 Ом)", size=11, fill="#fdf2f0", stroke=MUTED)
    p.append(b4)
    
    # 2. ФНЧ з підвищенням опору (R_S < R_L)
    p.append(text(585, 65, "2. ФНЧ підвищувальний (R_S < R_L)", size=13, color=INK, bold=True))
    b5, w5, h5 = textbox(455, 110, "Z_S (10 Ом)", size=11, fill="#fdf2f0", stroke=MUTED)
    p.append(b5)
    p.append(line(495, 110, 515, 110, color=LINE, sw=2))
    p.append(line(515, 110, 515, 135, color=LINE, sw=2))
    b6, w6, h6 = textbox(515, 155, "Ємність C (Паралельно)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b6)
    p.append(line(515, 110, 535, 110, color=LINE, sw=2))
    b7, w7, h7 = textbox(585, 110, "Індуктивність L\n(Послідовно)", size=11, fill="#e8f4ec", stroke=POS, bold=True)
    p.append(b7)
    p.append(line(635, 110, 660, 110, color=LINE, sw=2))
    b8, w8, h8 = textbox(700, 110, "Z_L (50 Ом)", size=11, fill="#f0f4fd", stroke=MUTED)
    p.append(b8)
    
    # 3. ФВЧ зі зниженням опору (R_S > R_L)
    p.append(text(195, 215, "3. ФВЧ понижувальний (R_S > R_L)", size=13, color=INK, bold=True))
    b9, w9, h9 = textbox(70, 260, "Z_S (50 Ом)", size=11, fill="#f0f4fd", stroke=MUTED)
    p.append(b9)
    p.append(line(110, 260, 135, 260, color=LINE, sw=2))
    b10, w10, h10 = textbox(185, 260, "Ємність C\n(Послідовно)", size=11, fill="#e0ebfd", stroke=NEG, bold=True)
    p.append(b10)
    p.append(line(235, 260, 270, 260, color=LINE, sw=2))
    p.append(line(270, 260, 270, 285, color=LINE, sw=2))
    b11, w11, h11 = textbox(270, 310, "Індуктивність L (Паралельно)", size=10, fill="#e8f4ec", stroke=POS)
    p.append(b11)
    p.append(line(270, 260, 290, 260, color=LINE, sw=2))
    b12, w12, h12 = textbox(320, 260, "Z_L (10 Ом)", size=11, fill="#fdf2f0", stroke=MUTED)
    p.append(b12)

    # 4. ФВЧ з підвищенням опору (R_S < R_L)
    p.append(text(585, 215, "4. ФВЧ підвищувальний (R_S < R_L)", size=13, color=INK, bold=True))
    b13, w13, h13 = textbox(455, 260, "Z_S (10 Ом)", size=11, fill="#fdf2f0", stroke=MUTED)
    p.append(b13)
    p.append(line(495, 260, 515, 260, color=LINE, sw=2))
    p.append(line(515, 260, 515, 285, color=LINE, sw=2))
    b14, w14, h14 = textbox(515, 310, "Індуктивність L (Паралельно)", size=10, fill="#e8f4ec", stroke=POS)
    p.append(b14)
    p.append(line(515, 260, 535, 260, color=LINE, sw=2))
    b15, w15, h15 = textbox(585, 260, "Ємність C\n(Послідовно)", size=11, fill="#e0ebfd", stroke=NEG, bold=True)
    p.append(b15)
    p.append(line(635, 260, 660, 260, color=LINE, sw=2))
    b16, w16, h16 = textbox(700, 260, "Z_L (50 Ом)", size=11, fill="#f0f4fd", stroke=MUTED)
    p.append(b16)

    return render(os.path.join(OUT, "l-network-topologies.svg"), W, H, *p)

# ── Фігура 3: Порівняння Pi та T ланок ────────────────────────────────────────
def fig_pi_and_t_networks():
    W, H = 760, 310
    p = []
    
    p.append(rect(10, 10, 740, 290, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    
    # Pi-ланка
    p.append(rect(20, 25, 350, 260, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(195, 48, "П-подібна ланка (Pi-Network)", size=15, color=POS, bold=True))
    
    b1, w1, h1 = textbox(60, 110, "Z_S", size=12, fill="#f0f4fd", stroke=MUTED)
    p.append(b1)
    p.append(line(85, 110, 120, 110, color=LINE, sw=2))
    p.append(line(120, 110, 120, 150, color=LINE, sw=2))
    b2, w2, h2 = textbox(120, 175, "C1 (Шунт)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b2)
    
    b3, w3, h3 = textbox(195, 110, "L (Послідовно)", size=11, fill="#e8f4ec", stroke=POS, bold=True)
    p.append(b3)
    p.append(line(245, 110, 270, 110, color=LINE, sw=2))
    p.append(line(270, 110, 270, 150, color=LINE, sw=2))
    b4, w4, h4 = textbox(270, 175, "C2 (Шунт)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b4)
    
    p.append(line(270, 110, 305, 110, color=LINE, sw=2))
    b5, w5, h5 = textbox(330, 110, "Z_L", size=12, fill="#fdf2f0", stroke=MUTED)
    p.append(b5)
    
    b6, w6, h6 = textbox(195, 240, "Переваги: ФНЧ придушує гармоніки PA;\nдозволяє вибирати Q незалежно від Z_S/Z_L", size=11, fill="#e8f4ec", stroke=POS, color=INK)
    p.append(b6)
    
    # T-ланка
    p.append(rect(390, 25, 350, 260, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(565, 48, "Т-подібна ланка (T-Network)", size=15, color=NEG, bold=True))
    
    b7, w7, h7 = textbox(430, 110, "Z_S", size=12, fill="#f0f4fd", stroke=MUTED)
    p.append(b7)
    p.append(line(450, 110, 470, 110, color=LINE, sw=2))
    
    b8, w8, h8 = textbox(505, 110, "C1 (Серія)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b8)
    
    p.append(line(540, 110, 565, 110, color=LINE, sw=2))
    p.append(line(565, 110, 565, 150, color=LINE, sw=2))
    b9, w9, h9 = textbox(565, 175, "L (Шунт)", size=11, fill="#e8f4ec", stroke=POS, bold=True)
    p.append(b9)
    
    p.append(line(565, 110, 588, 110, color=LINE, sw=2))
    b10, w10, h10 = textbox(625, 110, "C2 (Серія)", size=10, fill="#e0ebfd", stroke=NEG)
    p.append(b10)
    
    p.append(line(660, 110, 680, 110, color=LINE, sw=2))
    b11, w11, h11 = textbox(700, 110, "Z_L", size=12, fill="#fdf2f0", stroke=MUTED)
    p.append(b11)
    
    b12, w12, h12 = textbox(565, 240, "Переваги: ФВЧ відсікає постійний струм (DC);\nзручна для узгодження з вищими опорами", size=11, fill="#fde4e1", stroke=NEG, color=INK)
    p.append(b12)
    
    return render(os.path.join(OUT, "pi-and-t-networks.svg"), W, H, *p)

# ── Фігура 4: Розподілені узгоджувальні кола ─────────────────────────
def fig_quarter_wave_stub():
    W, H = 760, 310
    p = []
    
    p.append(rect(10, 10, 740, 290, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    
    # Чвертьхвильовий трансформатор
    p.append(rect(20, 25, 350, 260, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(195, 48, "Чвертьхвильовий трансформатор λ/4", size=14, color=INK, bold=True))
    
    b1, w1, h1 = textbox(55, 110, "Z0", size=10, fill="#f0f4fd", stroke=MUTED)
    p.append(b1)
    p.append(line(75, 110, 95, 110, color=LINE, sw=2))
    
    b2, w2, h2 = textbox(180, 110, "Трансформатор Z_m\nl = λ/4", size=10, fill="#fef0d9", stroke=POS, sw=1.5, color=INK, bold=True)
    p.append(b2)
    p.append(line(260, 110, 290, 110, color=LINE, sw=2))
    
    b3, w3, h3 = textbox(325, 110, "RL", size=10, fill="#fdf2f0", stroke=MUTED)
    p.append(b3)
    
    b4, w4, h4 = textbox(195, 220, "Формула хвильового опору:\nZ_m = √(Z0 · RL)\nПрацює у вузькій смузі частот біля f0", size=11, fill="#f9f9f9", stroke=MUTED)
    p.append(b4)

    # Шлейфове узгодження (Stub matching)
    p.append(rect(390, 25, 350, 260, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(565, 48, "Шлейфове узгодження (Single Stub)", size=14, color=INK, bold=True))
    
    b5, w5, h5 = textbox(425, 110, "Джерело", size=10, fill="#f0f4fd", stroke=MUTED)
    p.append(b5)
    p.append(line(460, 110, 520, 110, color=LINE, sw=2))
    
    # Вузол підключення шлейфу
    p.append(circle(520, 110, 4, fill=INK))
    p.append(line(520, 110, 520, 145, color=LINE, sw=2))
    b6, w6, h6 = textbox(520, 180, "Паралельний шлейф\n(короткозамкнений / замкнутий)", size=10, fill="#e8f4ec", stroke=POS)
    p.append(b6)
    
    p.append(line(520, 110, 575, 110, color=LINE, sw=2))
    b7, w7, h7 = textbox(625, 110, "Навантаж.", size=10, fill="#fdf2f0", stroke=MUTED)
    p.append(b7)
    
    b8, w8, h8 = textbox(565, 235, "Відстань d компенсує активний опір;\nдовжина шлейфу l компенсує реактивність", size=11, fill="#f9f9f9", stroke=MUTED)
    p.append(b8)
    
    return render(os.path.join(OUT, "quarter-wave-stub.svg"), W, H, *p)

if __name__ == "__main__":
    fig_matching_concept()
    fig_l_network_topologies()
    fig_pi_and_t_networks()
    fig_quarter_wave_stub()
    print("Всі фігури згенеровано успішно.")
