# -*- coding: utf-8 -*-
import sys
import os
import math

# '..' 4 рази до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def gen_fig1(out_dir):
    """Фігура 1: Фізична структура комірки CBRAM (ECM) у станах HRS та LRS."""
    w, h = 800, 450
    frags = []

    frags.append(text(w/2, 28, "Фізична структура комірки CBRAM (ECM) у станах HRS та LRS", size=18, bold=True))

    # Ліва рамка: Високоомний стан (HRS / OFF)
    frags.append(rect(20, 50, 370, 380, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    frags.append(text(205, 75, "Високоомний стан (HRS / OFF): R > 10 МОм", size=13, color=NEG, bold=True))

    # Шари HRS
    frags.append(fitbox(40, 95, 330, 45, "Активний анод (Ag / Cu)\nДжерело катіонів Me → Me⁺ + e⁻", size=11, fill="#fef3c7", stroke="#d97706"))
    # Матриця електроліту
    frags.append(rect(40, 145, 330, 140, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    # Текст у бічній частині матриці (щоб не перетинатися з містком по центру)
    frags.append(fitbox(45, 150, 140, 130, "Твердий електроліт\n(GeSₓ, SiO₂, HfO₂)\nσᵢₒₙ >> σₑₗ", size=10, fill="#ffffff", stroke="#38bdf8"))

    frags.append(fitbox(40, 290, 330, 45, "Інертний катод (Pt / W / TiN)\nЕлектронний колектор", size=11, fill="#e2e8f0", stroke="#475569"))

    # Розрив містка у HRS
    frags.append(line(230, 290, 230, 195, color="#d97706", sw=6))
    frags.append(circle(230, 180, 5, fill="#ef4444", stroke="#b91c1c", sw=1.5))
    frags.append(fitbox(245, 165, 120, 40, "Нанорозрив\n(~1-2 нм)", size=10, fill="#fff1f2", stroke=NEG))

    frags.append(fitbox(40, 345, 330, 75, "Місток розірвано біля анода.\nСтрум обмежений тунелюванням та дрейфом.\nЛогічний стан: «0»", size=11, fill="#ffffff", stroke=NEG))

    # Права рамка: Низькоомний стан (LRS / ON)
    frags.append(rect(410, 50, 370, 380, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    frags.append(text(595, 75, "Низькоомний стан (LRS / ON): R ≈ 1-10 кОм", size=13, color=FIELD, bold=True))

    # Шари LRS
    frags.append(fitbox(430, 95, 330, 45, "Активний анод (Ag / Cu)\nV_anode > V_SET", size=11, fill="#fef3c7", stroke="#d97706"))
    frags.append(rect(430, 145, 330, 140, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(fitbox(435, 150, 140, 130, "Твердий електроліт\n(GeSₓ, SiO₂, HfO₂)", size=10, fill="#ffffff", stroke="#38bdf8"))

    frags.append(fitbox(430, 290, 330, 45, "Інертний катод (Pt / W / TiN)\nV_cathode = 0 B", size=11, fill="#e2e8f0", stroke="#475569"))

    # Суцільний металевий місток у LRS
    frags.append(line(620, 290, 620, 140, color="#d97706", sw=7))
    frags.append(circle(620, 140, 6, fill="#b45309", stroke="#78350f", sw=1.5))
    frags.append(fitbox(635, 185, 120, 50, "Металевий\nнанопровід\n(Ag / Cu)", size=10, fill="#ecfdf5", stroke=FIELD))

    frags.append(fitbox(430, 345, 330, 75, "Неперервний металевий контакт.\nКвантова провідність G = n · G₀.\nЛогічний стан: «1»", size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(out_dir, "cbram-cell-structure.svg"), w, h, *frags)

def gen_fig2(out_dir):
    """Фігура 2: Чотиристадійний цикл електрохімічного переключення (SET / RESET)."""
    w, h = 800, 450
    frags = []

    frags.append(text(w/2, 28, "Цикл електрохімічного переключення (SET / RESET) у CBRAM", size=18, bold=True))

    # Стадія 1: Окиснення на аноді
    frags.append(rect(20, 50, 175, 380, fill="#fffbe6", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(107, 75, "1. Анодне окиснення", size=12, color="#b45309", bold=True))
    frags.append(fitbox(30, 95, 155, 130, "Вхідний стан: HRS\nV > V_SET > 0 B\n\nAg → Ag⁺ + e⁻\n(або Cu → Cu²⁺ + 2e⁻)\n\nРеакція за кінетикою Батлера-Фольмера.", size=10, fill="#ffffff", stroke="#f59e0b"))
    frags.append(circle(107, 260, 22, fill="#fef3c7", stroke="#d97706", sw=2))
    frags.append(text(107, 260, "Ag⁺", size=12, color="#b45309", bold=True))
    frags.append(arrow(107, 285, 107, 320, color="#d97706", sw=2))
    frags.append(fitbox(30, 340, 155, 75, "Інжекція катіонів у твердий електроліт під дією поля", size=10, fill="#ffffff", stroke="#d97706"))

    # Стадія 2: Дрейф і ростовий фронт
    frags.append(rect(210, 50, 175, 380, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(297, 75, "2. Міграція та ріст", size=12, color="#0369a1", bold=True))
    frags.append(fitbox(220, 95, 155, 130, "Поле E ≈ 10⁶ В/см\nДрейф Мотта-Герні\n\nКатодне відновлення:\nAg⁺ + e⁻ → Ag⁰\n\nРіст містка від катода до анода!", size=10, fill="#ffffff", stroke="#38bdf8"))
    frags.append(rect(272, 240, 50, 80, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    frags.append(line(297, 320, 297, 260, color="#d97706", sw=6))
    frags.append(arrow(297, 270, 297, 245, color="#0369a1", sw=2))
    frags.append(fitbox(220, 340, 155, 75, "Утворення та ріст металевого наноконуса", size=10, fill="#ffffff", stroke="#0284c7"))

    # Стадія 3: Замикання (SET / LRS)
    frags.append(rect(400, 50, 175, 380, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(487, 75, "3. Замикання (SET)", size=12, color="#047857", bold=True))
    frags.append(fitbox(410, 95, 155, 130, "Контакт з анодом!\nПерехід HRS → LRS\n\nСтрум обмежується комплайєнсом I_CC.\n\nФормування атомарного звуження.", size=10, fill="#ffffff", stroke="#34d399"))
    frags.append(line(487, 320, 487, 230, color="#d97706", sw=7))
    frags.append(circle(487, 230, 5, fill="#047857", stroke="#065f46", sw=1.5))
    frags.append(fitbox(410, 340, 155, 75, "Стан LRS (ON)\nПровідність G = n · G₀", size=10, fill="#ffffff", stroke=FIELD))

    # Стадія 4: Розчинення (RESET / HRS)
    frags.append(rect(590, 50, 190, 380, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(685, 75, "4. Розрив (RESET)", size=12, color="#b91c1c", bold=True))
    frags.append(fitbox(600, 95, 170, 130, "Зворотне поле V < 0 B\nV < V_RESET\n\nДжоулів нагрів I²R локалізований у звуженні.\n\nТермічне + електрохімічне розчинення.", size=10, fill="#ffffff", stroke="#f87171"))
    frags.append(line(685, 320, 685, 260, color="#d97706", sw=6))
    frags.append(circle(685, 250, 8, fill="#fee2e2", stroke="#ef4444", sw=1.5))
    frags.append(fitbox(600, 340, 170, 75, "Локальне теплове плавлення та розрив містка", size=10, fill="#ffffff", stroke=POS))

    render(os.path.join(out_dir, "cbram-set-reset-cycle.svg"), w, h, *frags)

def gen_fig3(out_dir):
    """Фігура 3: Вольт-амперна характеристика (ВАХ) CBRAM та квантування провідності."""
    w, h = 800, 460
    frags = []

    frags.append(text(w/2, 28, "Вольт-амперна характеристика (ВАХ) CBRAM та квантування", size=18, bold=True))

    # Ліва частина: ВАХ у напівлогарифмічному масштабі
    frags.append(rect(20, 50, 440, 390, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(240, 75, "Істерична ВАХ елемента CBRAM", size=13, bold=True))

    # Осі ВАХ
    frags.append(arrow(50, 240, 440, 240, color=LINE, sw=1.5)) # V-axis
    frags.append(arrow(240, 390, 240, 90, color=LINE, sw=1.5))  # I-axis
    frags.append(text(445, 245, "V", size=12, bold=True))
    frags.append(text(245, 85, "I (log)", size=12, bold=True))

    # Позначки напруг SET і RESET
    frags.append(line(370, 100, 370, 380, color=FIELD, dash="2 2", sw=1))
    frags.append(text(370, 255, "V_SET", size=11, color=FIELD, bold=True))

    frags.append(line(120, 100, 120, 380, color=POS, dash="2 2", sw=1))
    frags.append(text(120, 255, "V_RESET", size=11, color=POS, bold=True))

    # Комплайєнс струму I_CC
    frags.append(line(240, 120, 400, 120, color=MUTED, dash="3 3", sw=1.5))
    frags.append(text(330, 110, "I_CC (Compliance)", size=10, color=MUTED, bold=True))

    # Вітки ВАХ
    # HRS пряма гілка (низький струм)
    frags.append(line(240, 240, 370, 230, color=NEG, sw=2.5))
    # Перехід SET (стрибок вгору)
    frags.append(arrow(370, 230, 370, 120, color=FIELD, sw=2.5))
    frags.append(text(380, 175, "SET", size=11, color=FIELD, bold=True))
    # LRS зворотна гілка
    frags.append(line(370, 120, 240, 240, color=FIELD, sw=2.5))
    frags.append(line(240, 240, 120, 290, color=FIELD, sw=2.5))
    # Перехід RESET (скидання додолу)
    frags.append(arrow(120, 290, 120, 240, color=POS, sw=2.5))
    frags.append(text(75, 265, "RESET", size=11, color=POS, bold=True))
    # Повернення по HRS
    frags.append(line(120, 240, 240, 240, color=NEG, sw=2.5))

    frags.append(text(310, 220, "Гілка HRS (OFF)", size=10, color=NEG))
    frags.append(text(280, 160, "Гілка LRS (ON)", size=10, color=FIELD))

    # Права частина: Квантування провідності G = n * G_0
    frags.append(rect(480, 50, 300, 390, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(630, 75, "Квантування провідності", size=13, bold=True))

    frags.append(fitbox(495, 95, 270, 70, "Квант провідності Ландауера:\nG₀ = 2e² / h ≈ 77.48 мкСм\nR₀ = 1 / G₀ ≈ 12.91 кОм", size=10, fill="#ffffff", stroke="#94a3b8"))

    # Сходинки квантування G/G_0
    frags.append(arrow(510, 340, 510, 175, color=LINE, sw=1.5))
    frags.append(arrow(500, 330, 760, 330, color=LINE, sw=1.5))
    frags.append(text(740, 345, "Час t", size=10, bold=True))
    frags.append(text(490, 170, "G / G₀", size=10, bold=True))

    # Сходинки 1 G_0, 2 G_0, 3 G_0
    frags.append(line(510, 300, 570, 300, color=FIELD, sw=2))
    frags.append(line(570, 300, 570, 260, color=FIELD, sw=2))
    frags.append(line(570, 260, 650, 260, color=FIELD, sw=2))
    frags.append(line(650, 260, 650, 210, color=FIELD, sw=2))
    frags.append(line(650, 210, 740, 210, color=FIELD, sw=2))

    frags.append(text(540, 315, "1 G₀", size=9, color=FIELD, bold=True))
    frags.append(text(600, 275, "2 G₀", size=9, color=FIELD, bold=True))
    frags.append(text(680, 225, "3 G₀", size=9, color=FIELD, bold=True))

    frags.append(fitbox(495, 360, 270, 65, "Дискретні рівні дозволяють нейроморфну багаторівневу пам'ять (MLC).", size=9, fill="#ecfdf5", stroke=FIELD))

    render(os.path.join(out_dir, "cbram-iv-hysteresis.svg"), w, h, *frags)

def gen_fig4(out_dir):
    """Фігура 4: Енергетичний ландшафт міграції катіонів та деформація полем по Мотту-Герні."""
    w, h = 800, 430
    frags = []

    frags.append(text(w/2, 28, "Енергетичний бар'єр міграції катіонів та поле Мотта-Герні", size=18, bold=True))

    # Ліва частина: Симетричний потенціал (E = 0)
    frags.append(rect(20, 50, 370, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(205, 75, "Без електричного поля (E = 0)", size=13, bold=True))

    # Потенційна крива (2 ями)
    frags.append(arrow(40, 330, 370, 330, color=LINE, sw=1.5))
    frags.append(arrow(50, 340, 50, 100, color=LINE, sw=1.5))
    frags.append(text(375, 335, "x", size=11, bold=True))
    frags.append(text(40, 95, "Енергія U", size=11, bold=True))

    # Сонцеподібні потенційні ями
    pts1 = [(50 + i*3.0, 310 - 150 * (math.sin(math.pi * i / 50)**2)) for i in range(101)]
    for i in range(len(pts1)-1):
        frags.append(line(pts1[i][0], pts1[i][1], pts1[i+1][0], pts1[i+1][1], color="#0284c7", sw=2.5))

    # Позначки E_a та a
    frags.append(line(125, 310, 125, 160, color=MUTED, dash="2 2"))
    frags.append(line(200, 310, 200, 160, color=MUTED, dash="2 2"))
    frags.append(arrow(125, 160, 200, 160, color=FIELD, sw=1.5))
    frags.append(arrow(200, 160, 125, 160, color=FIELD, sw=1.5))
    frags.append(text(160, 150, "a (скачок)", size=10, color=FIELD, bold=True))

    frags.append(arrow(200, 310, 200, 160, color=POS, sw=1.5))
    frags.append(arrow(200, 160, 200, 310, color=POS, sw=1.5))
    frags.append(text(210, 235, "E_a", size=11, color=POS, bold=True))

    frags.append(fitbox(40, 350, 330, 45, "Симетричний бар'єр активації E_a.\nІмовірність стрибка вліво та вправо однакова.\nДрейфовий потік дорівнює нулю.", size=10, fill="#ffffff", stroke=MUTED))

    # Права частина: Асиметричний потенціал при сильному полі (E >> 0)
    frags.append(rect(410, 50, 370, 360, fill="#fffbe6", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(595, 75, "Сильне електричне поле (E >> 0)", size=13, color="#b45309", bold=True))

    frags.append(arrow(430, 330, 760, 330, color=LINE, sw=1.5))
    frags.append(arrow(440, 340, 440, 100, color=LINE, sw=1.5))
    frags.append(text(765, 335, "x", size=11, bold=True))
    frags.append(text(430, 95, "Енергія U", size=11, bold=True))

    # Похила деформована потенційна крива
    pts2 = [(440 + i*3.0, 250 - 150 * (math.sin(math.pi * i / 50)**2) + i*1.2) for i in range(101)]
    for i in range(len(pts2)-1):
        frags.append(line(pts2[i][0], pts2[i][1], pts2[i+1][0], pts2[i+1][1], color="#d97706", sw=2.5))

    # Знижений бар'єр в напрямку поля E
    frags.append(fitbox(430, 105, 330, 55, "Зниження бар'єра:\nE_eff = E_a - q · E · a / 2\n\nШвидкість стрибків зростає експоненційно:\nν ∝ exp(-(E_a - qEa/2) / k_BT)", size=10, fill="#ffffff", stroke="#f59e0b"))

    frags.append(fitbox(430, 350, 330, 45, "Електричне поле нахиляє потенційний ландшафт.\nСпрямована міграція катіонів у мільйони разів швидша!", size=10, fill="#ffffff", stroke=FIELD))

    render(os.path.join(out_dir, "cbram-energy-landscape.svg"), w, h, *frags)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)

    gen_fig1(out_dir)
    gen_fig2(out_dir)
    gen_fig3(out_dir)
    gen_fig4(out_dir)
    print("Успішно згенеровано 4 фігури CBRAM у", out_dir)

if __name__ == "__main__":
    main()
