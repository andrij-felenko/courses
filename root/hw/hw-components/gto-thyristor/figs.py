# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «GTO: тиристор із керованим вимиканням»."""

import sys
import os

# scripts/ у корені репо (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_structure():
    """Фігура 1: Сегментована структура GTO та анодні закоротки."""
    w, h = 820, 420
    frags = []

    # Заголовок блоків
    t1, _, _ = textbox(220, 35, "Класичний тиристор (SCR)\nСуцільний катод, один контакт затвора", size=13, bold=True)
    t2, _, _ = textbox(600, 35, "Замикальний тиристор (GTO)\nГребінчасті катодні пальці та анодні закоротки", size=13, bold=True)
    frags.extend([t1, t2])

    # Ліва частина: Звичайний SCR
    frags.append(rect(60, 75, 320, 300, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    
    # Шари SCR: Анод p+, База n-, База p, Катод n+
    frags.append(rect(90, 95, 260, 45, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(220, 122, "Анод p+ (емітерний шар)", size=13, color=POS, bold=True))

    frags.append(rect(90, 145, 260, 100, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(220, 198, "Широка слабколегована n-база (блокуюча)", size=12, color=INK))

    frags.append(rect(90, 250, 260, 55, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(220, 280, "p-база (керуюча)", size=12, color=POS))

    frags.append(rect(140, 310, 160, 35, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(220, 332, "Катод n+ (суцільний)", size=12, color=NEG, bold=True))

    # Виводи SCR
    frags.append(line(220, 95, 220, 70, color=LINE, sw=2))
    frags.append(text(220, 65, "Анод (A)", size=12, bold=True))

    frags.append(line(90, 275, 60, 275, color=LINE, sw=2))
    frags.append(text(45, 279, "Затвор (G)", size=12, bold=True, anchor="end"))

    frags.append(line(220, 345, 220, 370, color=LINE, sw=2))
    frags.append(text(220, 385, "Катод (K)", size=12, bold=True))


    # Права частина: GTO з пальцями
    frags.append(rect(440, 75, 320, 300, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))

    # Анодний шар з анодними закоротками
    frags.append(rect(470, 95, 75, 45, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    frags.append(text(507, 122, "p+ анод", size=11, color=POS, bold=True))

    frags.append(rect(550, 95, 40, 45, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    frags.append(text(570, 122, "n+ закоротка", size=9, color=NEG, bold=True))

    frags.append(rect(595, 95, 75, 45, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    frags.append(text(632, 122, "p+ анод", size=11, color=POS, bold=True))

    frags.append(rect(675, 95, 40, 45, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    frags.append(text(695, 122, "n+ закоротка", size=9, color=NEG, bold=True))

    # n-база
    frags.append(rect(470, 145, 260, 100, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(600, 198, "Високовольтна n-база", size=12, color=INK))

    # p-база
    frags.append(rect(470, 250, 260, 55, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(600, 275, "Тонка високопровідна p-база", size=12, color=POS))

    # Катодні пальці (n+)
    frags.append(rect(485, 310, 55, 35, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    frags.append(text(512, 332, "n+ палець", size=10, color=NEG, bold=True))

    frags.append(rect(572, 310, 55, 35, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    frags.append(text(600, 332, "n+ палець", size=10, color=NEG, bold=True))

    frags.append(rect(660, 310, 55, 35, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    frags.append(text(687, 332, "n+ палець", size=10, color=NEG, bold=True))

    # Контакти затвора між пальцями
    frags.append(rect(545, 305, 22, 15, fill="#d5dbdb", stroke=LINE, sw=1, rx=2))
    frags.append(rect(632, 305, 22, 15, fill="#d5dbdb", stroke=LINE, sw=1, rx=2))

    # Виводи GTO
    frags.append(line(600, 95, 600, 70, color=LINE, sw=2))
    frags.append(text(600, 65, "Анод (A)", size=12, bold=True))

    frags.append(line(470, 275, 445, 275, color=LINE, sw=2))
    frags.append(text(435, 279, "Затвор (G)", size=12, bold=True, anchor="end"))

    # Спільний катодний вивід
    frags.append(line(512, 345, 512, 365, color=LINE, sw=1.5))
    frags.append(line(600, 345, 600, 365, color=LINE, sw=1.5))
    frags.append(line(687, 345, 687, 365, color=LINE, sw=1.5))
    frags.append(line(512, 365, 687, 365, color=LINE, sw=2))
    frags.append(line(600, 365, 600, 385, color=LINE, sw=2))
    frags.append(text(600, 400, "Спільний катод (K)", size=12, bold=True))

    render(os.path.join(OUT_DIR, "structure-and-fingers.svg"), w, h, *frags)


def fig_crowding():
    """Фігура 2: Механізм стиснення струму (Current Crowding) у катодному пальці."""
    w, h = 760, 410
    frags = []

    t_main, _, _ = textbox(380, 30, "Динаміка екстракції дірок та стиснення струму в катодному пальці", size=14, bold=True)
    frags.append(t_main)

    # Велика область p-бази
    frags.append(rect(80, 65, 600, 245, fill="#fef5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(130, 95, "p-база GTO", size=13, color=POS, bold=True))

    # Контакти затвора з боків
    frags.append(rect(110, 160, 80, 110, fill="#d5dbdb", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(150, 205, "Метал G", size=12, bold=True))
    frags.append(text(150, 225, "Затвор", size=11, color=MUTED))

    frags.append(rect(570, 160, 80, 110, fill="#d5dbdb", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(610, 205, "Метал G", size=12, bold=True))
    frags.append(text(610, 225, "Затвор", size=11, color=MUTED))

    # Катодний емітерний острівець n+ посередині (розділений на 3 зони)
    # Зона 1: лівий закритий край
    frags.append(rect(230, 160, 80, 110, fill="#ffffff", stroke="#f39c12", sw=1.5, rx=4))
    frags.append(text(270, 205, "Збіднено", size=11, color="#d35400", bold=True))
    frags.append(text(270, 225, "Замкнено", size=10, color=MUTED))

    # Зона 2: центральний стиснутий канал струму
    frags.append(rect(320, 130, 120, 140, fill="#fadbd8", stroke=POS, sw=2, rx=4))
    frags.append(text(380, 155, "Канал струму", size=12, color=POS, bold=True))
    frags.append(arrow(380, 75, 380, 125, color=POS, sw=3))
    frags.append(arrow(380, 170, 380, 255, color=POS, sw=3))

    # Зона 3: правий закритий край
    frags.append(rect(450, 160, 80, 110, fill="#ffffff", stroke="#f39c12", sw=1.5, rx=4))
    frags.append(text(490, 205, "Збіднено", size=11, color="#d35400", bold=True))
    frags.append(text(490, 225, "Замкнено", size=10, color=MUTED))

    # Загальна рамка катодного пальця
    frags.append(text(380, 290, "Катодний палець n+ (завширшки 150..250 мкм)", size=12, color=NEG, bold=True))

    # Стрілки відсмоктування дірок до затвора
    frags.append(arrow(260, 130, 170, 155, color=POS, sw=2))
    frags.append(text(205, 120, "−I_GQ (дірки)", size=11, color=POS, bold=True))

    frags.append(arrow(500, 130, 590, 155, color=POS, sw=2))
    frags.append(text(555, 120, "−I_GQ (дірки)", size=11, color=POS, bold=True))

    t_hot, _, _ = textbox(380, 355, "Стиснення струму (Current Crowding) у центрі пальця\nНебезпека локального перегріву й вторинного теплового пробою", size=12, color=POS, bold=True, fill="#fdedec", stroke=POS)
    frags.append(t_hot)

    render(os.path.join(OUT_DIR, "turn-off-crowding.svg"), w, h, *frags)


def fig_waveforms():
    """Фігура 3: Осцилограми вимикання GTO та схема RCD-снабера."""
    w, h = 840, 420
    frags = []

    # Ліва частина: Схема RCD-демпфера
    frags.append(rect(40, 35, 320, 355, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    t_sch, _, _ = textbox(200, 65, "RCD-демпфер вимикання (Turn-Off Snubber)", size=12, bold=True)
    frags.append(t_sch)

    # GTO у схемі
    frags.append(rect(80, 180, 80, 90, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(120, 215, "GTO", size=14, bold=True))
    frags.append(text(120, 235, "Ключ", size=11, color=MUTED))

    # Шини живлення
    frags.append(line(120, 110, 120, 180, color=LINE, sw=2))
    frags.append(text(120, 100, "+V_DC (Анод)", size=11, bold=True))

    frags.append(line(120, 270, 120, 345, color=LINE, sw=2))
    frags.append(text(120, 360, "0 В (Катод)", size=11, bold=True))

    frags.append(line(55, 235, 80, 235, color=LINE, sw=2))
    frags.append(text(45, 239, "G", size=12, bold=True, anchor="end"))

    # RCD гілка паралельно GTO
    frags.append(line(120, 135, 260, 135, color=LINE, sw=1.8))
    frags.append(line(260, 135, 260, 165, color=LINE, sw=1.8))

    # Діод D_s паралельно з резистором R_s
    frags.append(rect(205, 170, 50, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(230, 195, "D_s", size=12, bold=True))

    frags.append(rect(265, 170, 50, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(290, 195, "R_s", size=12, bold=True))

    frags.append(line(260, 150, 230, 150, color=LINE, sw=1.5))
    frags.append(line(230, 150, 230, 170, color=LINE, sw=1.5))
    frags.append(line(260, 150, 290, 150, color=LINE, sw=1.5))
    frags.append(line(290, 150, 290, 170, color=LINE, sw=1.5))

    frags.append(line(230, 210, 230, 230, color=LINE, sw=1.5))
    frags.append(line(290, 210, 290, 230, color=LINE, sw=1.5))
    frags.append(line(230, 230, 290, 230, color=LINE, sw=1.5))
    frags.append(line(260, 230, 260, 255, color=LINE, sw=1.8))

    # Конденсатор C_s
    frags.append(rect(235, 255, 50, 35, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(260, 277, "C_s", size=12, bold=True))

    frags.append(line(260, 290, 260, 320, color=LINE, sw=1.8))
    frags.append(line(260, 320, 120, 320, color=LINE, sw=1.8))


    # Права частина: Осцилограми
    frags.append(rect(390, 35, 415, 355, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    t_osc, _, _ = textbox(595, 65, "Фази вимикання: затримка, спад і хвіст струму", size=12, bold=True)
    frags.append(t_osc)

    # 1. Струм затвора I_G
    frags.append(line(420, 130, 770, 130, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(420, 120, "Струм затвора i_G", size=11, bold=True))
    frags.append(line(430, 130, 480, 130, color=POS, sw=2))
    frags.append(line(480, 130, 520, 175, color=POS, sw=2)) # пік вимикання
    frags.append(line(520, 175, 570, 145, color=POS, sw=2))
    frags.append(line(570, 145, 760, 145, color=POS, sw=1.5))
    frags.append(text(540, 185, "−I_GQ (пік вимикання)", size=10, color=POS, bold=True))

    # 2. Анодний струм i_A
    frags.append(line(420, 220, 770, 220, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(420, 205, "Струм анода i_A", size=11, bold=True))
    frags.append(line(430, 215, 525, 215, color=NEG, sw=2))
    frags.append(line(525, 215, 560, 255, color=NEG, sw=2)) # крутий спад t_f
    frags.append(line(560, 255, 680, 260, color=NEG, sw=2)) # хвіст t_tail
    frags.append(line(680, 260, 760, 260, color=NEG, sw=1.5))
    frags.append(text(620, 275, "Хвіст струму (tail)", size=10, color=NEG, bold=True))

    # 3. Анодна напруга v_AK
    frags.append(line(420, 310, 770, 310, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(420, 300, "Напруга анода v_AK", size=11, bold=True))
    frags.append(line(430, 360, 525, 360, color=FIELD, sw=2))
    frags.append(line(525, 360, 580, 315, color=FIELD, sw=2)) # плавний ріст завдяки C_s
    frags.append(line(580, 315, 610, 305, color=FIELD, sw=2)) # пік перенапруги
    frags.append(line(610, 305, 660, 315, color=FIELD, sw=2))
    frags.append(line(660, 315, 760, 315, color=FIELD, sw=2))
    frags.append(text(640, 335, "Обмежене dv/dt (C_s)", size=10, color=FIELD, bold=True))

    # Вертикальні лінії меж фаз
    frags.append(line(480, 95, 480, 375, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(525, 95, 525, 375, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(560, 95, 560, 375, color=MUTED, sw=1, dash="2,2"))

    frags.append(text(502, 385, "t_storage", size=10, color=MUTED))
    frags.append(text(542, 385, "t_fall", size=10, color=MUTED))
    frags.append(text(610, 385, "t_tail (рекомбінація)", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "waveforms-and-snubber.svg"), w, h, *frags)


def fig_gto_vs_igct():
    """Фігура 4: Еволюція від GTO до IGCT (жорстка комутація без снабера)."""
    w, h = 800, 390
    frags = []

    t_top, _, _ = textbox(400, 30, "Порівняння контурів комутації: традиційний GTO проти IGCT", size=14, bold=True)
    frags.append(t_top)

    # Лівий блок: GTO з провідним керуванням
    frags.append(rect(50, 60, 335, 300, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    t_gto, _, _ = textbox(217, 85, "Традиційний GTO\nПовільний драйвер + RCD-снабер", size=12, bold=True)
    frags.append(t_gto)

    frags.append(rect(140, 130, 155, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(217, 160, "Дисковий GTO", size=13, bold=True))
    frags.append(text(217, 175, "Корпус Press-Pack", size=10, color=MUTED))

    # Драйвер GTO віддалений
    frags.append(rect(80, 230, 110, 70, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(135, 260, "Драйвер", size=12, color=POS, bold=True))
    frags.append(text(135, 278, "вимикання", size=10, color=POS))

    # Довгі дроти (індуктивність)
    frags.append(line(190, 255, 217, 255, color=LINE, sw=2))
    frags.append(line(217, 255, 217, 190, color=LINE, sw=2))
    frags.append(circle(217, 230, 12, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(217, 234, "L_G", size=10, color=POS, bold=True))
    frags.append(text(250, 235, "~200..500 нГн", size=10, color=MUTED))

    t_gto_desc, _, _ = textbox(217, 330, "di_G/dt обмежена (20..50 А/мкс)\nbeta_off ≈ 3..5, обов'язковий RCD-снабер", size=11, color=INK)
    frags.append(t_gto_desc)


    # Правий блок: IGCT з інтегрованим коаксіальним фланцем
    frags.append(rect(415, 60, 335, 300, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    t_igct, _, _ = textbox(582, 85, "Сучасний IGCT\nМонолітний драйвер + Snubberless", size=12, bold=True)
    frags.append(t_igct)

    frags.append(rect(505, 130, 155, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(582, 160, "Кристал GCT", size=13, bold=True))
    frags.append(text(582, 175, "Кільцевий затвор", size=10, color=MUTED))

    # Драйвер змонтований прямо на фланець
    frags.append(rect(445, 220, 275, 75, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(582, 245, "Інтегрований драйвер (ABB/HPCI)", size=12, color=FIELD, bold=True))
    frags.append(text(582, 265, "Коаксіальне багатошарове з'єднання: L_G < 3 нГн", size=10, color=INK))

    frags.append(line(582, 190, 582, 220, color=FIELD, sw=4))

    t_igct_desc, _, _ = textbox(582, 330, "di_G/dt надвисока (>3000 А/мкс)\nbeta_off = 1, робота БЕЗ снабера (Snubberless)", size=11, color=FIELD, bold=True)
    frags.append(t_igct_desc)

    render(os.path.join(OUT_DIR, "gto-vs-igct.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_structure()
    fig_crowding()
    fig_waveforms()
    fig_gto_vs_igct()
    print("All figures generated successfully.")
