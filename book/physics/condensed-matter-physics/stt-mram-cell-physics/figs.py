# -*- coding: utf-8 -*-
import sys
import os
import math

# '..' 4 рази до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def gen_fig1(out_dir):
    """Фігура 1: Спіново-поляризоване тунелювання та TMR у паралельному й антипаралельному станах."""
    w, h = 800, 440
    frags = []

    # Заголовок
    frags.append(text(w/2, 28, "Спіново-поляризоване тунелювання та ефект TMR", size=18, bold=True))

    # Рамка ліворуч: Паралельний стан (P)
    frags.append(rect(20, 50, 370, 360, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    frags.append(text(205, 75, "Паралельний стан (P): R_P (Низький опір)", size=14, color=FIELD, bold=True))

    # Шари ліворуч (Pinned, Barrier, Free)
    frags.append(fitbox(40, 100, 100, 180, "Фіксований шар\nCoFeB (Pinned)\nMagnetization ↑\nDOS: N_up >> N_dn", size=12, fill="#e2e8f0"))
    frags.append(fitbox(150, 100, 40, 180, "Бар'єр\nMgO\n(~1 нм)", size=11, fill="#fef08a", stroke="#eab308"))
    frags.append(fitbox(200, 100, 100, 180, "Вільний шар\nCoFeB (Free)\nMagnetization ↑\nDOS: N_up >> N_dn", size=12, fill="#dbeafe", stroke=NEG))

    # Стрілки тунелювання у P стані
    frags.append(arrow(140, 140, 200, 140, color=POS, sw=3.5))
    frags.append(text(170, 130, "Спін ↑ (високий потік)", size=10, color=POS, bold=True))
    frags.append(arrow(140, 220, 200, 220, color=MUTED, sw=1.2))
    frags.append(text(170, 210, "Спін ↓ (низький)", size=10, color=MUTED))

    # Результат P стану
    frags.append(fitbox(40, 300, 330, 95, "Основний потік електронів (спін ↑) знаходить вільні стани такого ж спіну.\nПровідність висока → Опір R_P = R_min\nЛогічний стан: «0»", size=11, fill="#ecfdf5", stroke=FIELD))

    # Рамка праворуч: Антипаралельний стан (AP)
    frags.append(rect(410, 50, 370, 360, fill="#f8fafc", stroke=POS, sw=2, rx=8))
    frags.append(text(595, 75, "Антипаралельний стан (AP): R_AP (Високий опір)", size=14, color=POS, bold=True))

    # Шари праворуч
    frags.append(fitbox(430, 100, 100, 180, "Фіксований шар\nCoFeB (Pinned)\nMagnetization ↑\nDOS: N_up >> N_dn", size=12, fill="#e2e8f0"))
    frags.append(fitbox(540, 100, 40, 180, "Бар'єр\nMgO\n(~1 нм)", size=11, fill="#fef08a", stroke="#eab308"))
    frags.append(fitbox(590, 100, 100, 180, "Вільний шар\nCoFeB (Free)\nMagnetization ↓\nDOS: N_dn >> N_up", size=12, fill="#fee2e2", stroke=POS))

    # Стрілки тунелювання у AP стані
    frags.append(arrow(530, 140, 590, 140, color=MUTED, sw=1.2))
    frags.append(text(560, 130, "Мало станів ↑", size=10, color=MUTED))
    frags.append(arrow(530, 220, 590, 220, color=MUTED, sw=1.2))
    frags.append(text(560, 210, "Мало станів ↓", size=10, color=MUTED))

    # Результат AP стану
    frags.append(fitbox(430, 300, 330, 95, "Спіново-поляризований потік не знаходить станів відповідної орієнтації.\nПровідність низька → Опір R_AP = R_max\nФормула Julliere: TMR = (R_AP - R_P) / R_P > 200%\nЛогічний стан: «1»", size=11, fill="#fff1f2", stroke=POS))

    render(os.path.join(out_dir, "mtj-tunneling-tmr.svg"), w, h, *frags)

def gen_fig2(out_dir):
    """Фігура 2: Механізм спін-переносного моменту (STT) та векторна динаміка LLGS."""
    w, h = 800, 440
    frags = []

    frags.append(text(w/2, 28, "Переключення переносом спінового моменту (STT) у pMTJ", size=18, bold=True))

    # Ліва частина: Переключення AP -> P (струм від Free до Pinned)
    frags.append(rect(20, 50, 370, 360, fill="#faf5ff", stroke="#8b5cf6", sw=2, rx=8))
    frags.append(text(205, 75, "Режим AP → P (Струм I: Free → Pinned)", size=13, color="#6b21a8", bold=True))
    frags.append(text(205, 93, "Електрони рухаються: Pinned → Free", size=11, color=MUTED, italic=True))

    frags.append(fitbox(40, 115, 330, 75, "1. Електрони проходять Pinned шар і поляризуються (спін ↑).\n2. Поляризований потік входить у Free шар.\n3. Спіновий момент передається намагніченості M_free.", size=11, fill="#ffffff", stroke="#c084fc"))

    # Векторна діаграма для AP->P
    frags.append(circle(205, 260, 55, fill="#f3e8ff", stroke="#8b5cf6", sw=1.5))
    frags.append(arrow(205, 260, 205, 210, color=POS, sw=2.5))
    frags.append(text(220, 215, "M_free (↓)", size=11, color=POS, bold=True))
    frags.append(arrow(205, 260, 245, 245, color=FIELD, sw=2.5))
    frags.append(text(250, 240, "τ_STT", size=11, color=FIELD, bold=True))
    frags.append(arrow(205, 260, 175, 240, color=NEG, sw=1.8))
    frags.append(text(155, 235, "τ_damp", size=11, color=NEG))

    frags.append(fitbox(40, 330, 330, 65, "Момент τ_STT протидіє загатуванню Гільберта τ_damp.\nПри I > I_c0 намагніченість перевертається в стан ↑ (P).", size=11, fill="#ffffff", stroke="#8b5cf6"))

    # Права частина: Переключення P -> AP (струм від Pinned до Free)
    frags.append(rect(410, 50, 370, 360, fill="#fff7ed", stroke="#f97316", sw=2, rx=8))
    frags.append(text(595, 75, "Режим P → AP (Струм I: Pinned → Free)", size=13, color="#c2410c", bold=True))
    frags.append(text(595, 93, "Електрони рухаються: Free → Pinned", size=11, color=MUTED, italic=True))

    frags.append(fitbox(430, 115, 330, 75, "1. Електрони зі спіном ↑ легко проходять у Pinned шар.\n2. Електрони зі спіном ↓ відбиваються від Pinned інтерфейсу.\n3. Відбитий потік ↓ повертається і перевертає Free шар.", size=11, fill="#ffffff", stroke="#fdba74"))

    # Векторна діаграма для P->AP
    frags.append(circle(595, 260, 55, fill="#ffedd5", stroke="#f97316", sw=1.5))
    frags.append(arrow(595, 260, 595, 210, color=FIELD, sw=2.5))
    frags.append(text(610, 215, "M_free (↑)", size=11, color=FIELD, bold=True))
    frags.append(arrow(595, 260, 555, 275, color=POS, sw=2.5))
    frags.append(text(530, 275, "τ_STT", size=11, color=POS, bold=True))
    frags.append(arrow(595, 260, 625, 280, color=NEG, sw=1.8))
    frags.append(text(630, 285, "τ_damp", size=11, color=NEG))

    frags.append(fitbox(430, 330, 330, 65, "Відбиті спіни створюють τ_STT у напрямку ↓.\nПри I > I_c0 орієнтація змінюється на антипаралельну (AP).", size=11, fill="#ffffff", stroke="#f97316"))

    render(os.path.join(out_dir, "stt-switching-torque.svg"), w, h, *frags)

def gen_fig3(out_dir):
    """Фігура 3: Енергетичний бар'єр E_b та перевага перпендикулярної анізотропії pMTJ."""
    w, h = 800, 420
    frags = []

    frags.append(text(w/2, 28, "Енергетичний профіль та перевага pMTJ перед iMTJ", size=18, bold=True))

    # Ліворуч: Енергетичний потенціал E(theta) = E_b * sin^2(theta)
    frags.append(rect(20, 50, 420, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(230, 75, "Енергетичний ландшафт E(θ) = E_b · sin²(θ)", size=13, bold=True))

    # Осі графіку
    frags.append(arrow(50, 340, 410, 340, color=LINE, sw=1.5)) # X
    frags.append(arrow(60, 350, 60, 100, color=LINE, sw=1.5))   # Y
    frags.append(text(415, 345, "θ", size=12, bold=True))
    frags.append(text(45, 95, "Енергія E", size=12, bold=True))

    # Параболоподібні ями
    frags.append(line(60, 340, 140, 340, color=MUTED, dash="2 2"))
    frags.append(line(230, 160, 230, 340, color=MUTED, dash="2 2"))
    frags.append(line(400, 340, 400, 340, color=MUTED, dash="2 2"))

    # Намальована крива потенціалу
    pts = [(60 + i*3.4, 340 - 180 * (math.sin(math.pi * i / 100)**2)) for i in range(101)]
    for i in range(len(pts)-1):
        frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=FIELD, sw=3))

    frags.append(text(60, 360, "0° (P)", size=11, color=FIELD, bold=True))
    frags.append(text(230, 360, "90° (Top)", size=11, color=POS, bold=True))
    frags.append(text(400, 360, "180° (AP)", size=11, color=FIELD, bold=True))

    # Двостороння стрілка E_b
    frags.append(arrow(230, 340, 230, 160, color=POS, sw=2))
    frags.append(arrow(230, 160, 230, 340, color=POS, sw=2))
    frags.append(fitbox(240, 230, 180, 50, "Бар'єр збереження:\nE_b = K_eff · V\nΔ = E_b / (k_B · T) ≥ 60", size=11, fill="#fef2f2", stroke=POS))

    # Праворуч: Порівняння iMTJ проти pMTJ
    frags.append(rect(450, 50, 330, 350, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(615, 75, "Порівняння iMTJ та pMTJ", size=14, bold=True))

    frags.append(fitbox(465, 100, 300, 130, "Поздовжня анізотропія (iMTJ):\n• Намагніченість у площині плівки.\n• Форма створює демагнетизуюче поле 4πM_s.\n• Високий струм: I_c0 ∝ M_s² · V · (1 + 4πM_s / 2H_k)\n• Складність масштабування нижче 40 нм.", size=11, fill="#ffffff", stroke=MUTED))

    frags.append(fitbox(465, 245, 300, 140, "Перпендикулярна анізотропія (pMTJ):\n• Інтерфейсна анізотропія (iPMA) CoFeB/MgO.\n• Скасовано демагнетизуючий штраф 4πM_s.\n• Низький струм: I_c0 ∝ (2e/ℏ) · α · E_b / η\n• Масштабується до 10 нм із Δ ≥ 60!", size=11, fill="#ecfdf5", stroke=FIELD))

    render(os.path.join(out_dir, "pmtj-energy-barrier.svg"), w, h, *frags)

def gen_fig4(out_dir):
    """Фігура 4: Схема 1T-1MTJ комірки та вікно надійності (Endurance vs Read Disturb)."""
    w, h = 800, 440
    frags = []

    frags.append(text(w/2, 28, "Схема комірки 1T-1MTJ та діаграма надійності", size=18, bold=True))

    # Ліва частина: Схема 1T-1MTJ
    frags.append(rect(20, 50, 340, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(190, 75, "Електрична схема 1T-1MTJ", size=14, bold=True))

    # Лінії BL, SL, WL
    frags.append(line(60, 100, 300, 100, color=POS, sw=2))
    frags.append(text(50, 95, "BL (Bit Line)", size=11, color=POS, bold=True))

    # MTJ елемент
    frags.append(line(190, 100, 190, 140, color=LINE, sw=2))
    frags.append(rect(160, 140, 60, 40, fill="#dbeafe", stroke=NEG, sw=2, rx=4))
    frags.append(text(190, 164, "pMTJ", size=12, color=NEG, bold=True))
    frags.append(line(190, 180, 190, 220, color=LINE, sw=2))

    # Транзистор NMOS (селектор)
    frags.append(circle(190, 240, 20, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(line(120, 240, 170, 240, color=FIELD, sw=2))
    frags.append(text(100, 235, "WL (Gate)", size=11, color=FIELD, bold=True))
    frags.append(line(190, 260, 190, 300, color=LINE, sw=2))

    frags.append(line(60, 300, 300, 300, color=NEG, sw=2))
    frags.append(text(50, 315, "SL (Source Line)", size=11, color=NEG, bold=True))

    frags.append(fitbox(40, 330, 300, 65, "Транзистор регулює струм запису/читання.\nСпрямованість струму BL → SL (P→AP) або SL → BL (AP→P).", size=10, fill="#ffffff", stroke=MUTED))

    # Права частина: Графік J_c(t_pulse) та вікна надійності
    frags.append(rect(380, 50, 400, 360, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(580, 75, "Вікно імпульсного переключення J_c(t)", size=14, bold=True))

    # Осі
    frags.append(arrow(410, 340, 760, 340, color=LINE, sw=1.5))
    frags.append(arrow(420, 350, 420, 100, color=LINE, sw=1.5))
    frags.append(text(730, 360, "Тривалість t_pulse (с)", size=11, bold=True))
    frags.append(text(400, 95, "Густина струму J", size=11, bold=True))

    # Зони: Thermal activation (t > 10ns) та Precessional (t < 1ns)
    frags.append(line(420, 140, 750, 140, color=POS, dash="3 3", sw=1.5))
    frags.append(text(570, 130, "Пробій бар'єра MgO (TDDB limit)", size=10, color=POS, bold=True))

    frags.append(line(420, 300, 750, 300, color=FIELD, dash="3 3", sw=1.5))
    frags.append(text(570, 290, "Рівень зчитування I_read (без збурення)", size=10, color=FIELD, bold=True))

    # Намальована крива J_c(t)
    pts_j = [(430 + i*3.1, 150 + 130 * (1.0 / (1.0 + 0.05*i))) for i in range(101)]
    for i in range(len(pts_j)-1):
        frags.append(line(pts_j[i][0], pts_j[i][1], pts_j[i+1][0], pts_j[i+1][1], color="#2563eb", sw=2.5))

    frags.append(text(460, 200, "Прецесійне переключення J ∝ 1/t", size=10, color=NEG))
    frags.append(text(650, 265, "Термічна активація J ≈ J_c0", size=10, color=NEG))

    frags.append(fitbox(410, 370, 340, 30, "Вікно запису: I_read < I_switching < I_breakdown (MgO)", size=11, fill="#ecfdf5", stroke=FIELD))

    render(os.path.join(out_dir, "stt-mram-cell-circuit.svg"), w, h, *frags)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)

    gen_fig1(out_dir)
    gen_fig2(out_dir)
    gen_fig3(out_dir)
    gen_fig4(out_dir)
    print("Всі 4 фігури успішно згенеровано у", out_dir)

if __name__ == "__main__":
    main()
