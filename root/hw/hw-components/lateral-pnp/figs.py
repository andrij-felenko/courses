# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Латеральний p-n-p транзистор» (lateral-pnp)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_cross_section():
    """Поперечний розріз інтегрального латерального PNP-транзистора з прихованим n+ шаром."""
    w, h = 860, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Поперечний розріз латерального PNP-транзистора на кремнієвому кристалі", size=16, bold=True))

    # Підкладка p-Si
    frags.append(rect(40, 310, 780, 120, fill="#fcedea", stroke="#c0392b", sw=1.5, rx=0))
    frags.append(text(430, 405, "p-підкладка (p-Substrate, підключена до найнижчого потенціалу V_EE / GND)", size=13, color=POS, bold=True))

    # Прихований шар n+ (NBL)
    frags.append(rect(160, 275, 540, 45, fill="#d6e4ff", stroke="#2457d6", sw=1.5, rx=4))
    frags.append(text(430, 303, "n⁺ прихований шар (NBL) — рекомбінаційний та потенціальний бар'єр проти витоку в підкладку", size=12, color=NEG, bold=True))

    # Епітаксійний шар n-типу (База)
    frags.append(rect(140, 110, 580, 170, fill="#eef4ff", stroke="#2457d6", sw=1.5, rx=0))
    frags.append(text(215, 145, "n-епітаксія (База BJT)", size=12, color=NEG, bold=True))

    # p+ ізоляційні стінки ліворуч і праворуч
    frags.append(rect(40, 110, 100, 200, fill="#fbe8e6", stroke="#c0392b", sw=1.5, rx=0))
    frags.append(text(90, 205, "p⁺ ізоляція", size=12, color=POS, bold=True))

    frags.append(rect(720, 110, 100, 200, fill="#fbe8e6", stroke="#c0392b", sw=1.5, rx=0))
    frags.append(text(770, 205, "p⁺ ізоляція", size=12, color=POS, bold=True))

    # p-дифузійні області: Емітер (центр) та Колектор (кільце з двох боків на розрізі)
    # Колектор (ліва частина кільця)
    frags.append(rect(270, 110, 90, 65, fill="#fadbd8", stroke="#922b21", sw=1.5, rx=3))
    frags.append(text(315, 145, "p (Колектор)", size=12, color="#922b21", bold=True))

    # Емітер (центр)
    frags.append(rect(430, 110, 80, 65, fill="#fadbd8", stroke="#922b21", sw=1.8, rx=3))
    frags.append(text(470, 145, "p (Емітер)", size=12, color="#922b21", bold=True))

    # Колектор (права частина кільця)
    frags.append(rect(580, 110, 90, 65, fill="#fadbd8", stroke="#922b21", sw=1.5, rx=3))
    frags.append(text(625, 145, "p (Колектор)", size=12, color="#922b21", bold=True))

    # Контакт бази n+
    frags.append(rect(170, 110, 65, 45, fill="#cce0ff", stroke="#1f4e99", sw=1.5, rx=2))
    frags.append(text(202, 137, "n⁺ база", size=11, color="#1f4e99", bold=True))

    # Оксид SiO2
    frags.append(rect(40, 92, 780, 18, fill="#fdfefe", stroke="#7f8c8d", sw=1.2, rx=0))
    frags.append(text(100, 105, "SiO₂ оксид", size=10, color=MUTED))

    # Металеві контакти (алюміній)
    # Контакт B
    frags.append(rect(185, 60, 35, 36, fill="#bdc3c7", stroke="#34495e", sw=1.5, rx=2))
    frags.append(line(202, 60, 202, 45, color=LINE, sw=2))
    frags.append(textbox(202, 35, "B (База)", size=12, pad=6, bold=True)[0])

    # Контакт C (лівий)
    frags.append(rect(295, 60, 40, 36, fill="#bdc3c7", stroke="#34495e", sw=1.5, rx=2))
    frags.append(line(315, 60, 315, 45, color=LINE, sw=2))
    frags.append(line(315, 45, 570, 45, color=LINE, sw=2))

    # Контакт E (центр)
    frags.append(rect(450, 60, 40, 36, fill="#bdc3c7", stroke="#34495e", sw=1.5, rx=2))
    frags.append(line(470, 60, 470, 40, color=LINE, sw=2))
    frags.append(textbox(470, 30, "E (Емітер)", size=12, pad=6, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # Контакт C (правий)
    frags.append(rect(605, 60, 40, 36, fill="#bdc3c7", stroke="#34495e", sw=1.5, rx=2))
    frags.append(line(625, 60, 625, 45, color=LINE, sw=2))
    frags.append(textbox(645, 35, "C (Колектор)", size=12, pad=6, bold=True)[0])

    # Ширина бази W_B (визначена літографією)
    frags.append(line(360, 185, 430, 185, color="#d35400", sw=1.8))
    frags.append(line(360, 178, 360, 192, color="#d35400", sw=1.8))
    frags.append(line(430, 178, 430, 192, color="#d35400", sw=1.8))
    frags.append(text(395, 203, "W_B ≈ 1–3 мкм", size=11, color="#d35400", bold=True))

    # Стрілки руху дірок (латеральний корисний струм)
    frags.append(arrow(430, 140, 365, 140, color=FIELD, sw=2.5))
    frags.append(arrow(510, 140, 575, 140, color=FIELD, sw=2.5))
    frags.append(textbox(340, 225, "Латеральний потік дірок\n(корисний струм I_C)", size=11, pad=6, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True)[0])

    # Паразитний вертикальний потік до підкладки (пригнічений)
    frags.append(line(470, 175, 470, 268, color=POS, sw=1.8, dash="4,3"))
    frags.append(arrow(470, 268, 470, 278, color=POS, sw=1.8))
    frags.append(textbox(600, 225, "Паразитний вертикальний PNP:\nблокується шаром n⁺ NBL", size=11, pad=6, fill="#fdfefe", stroke=MUTED, color=INK)[0])

    render(os.path.join(OUT_DIR, "lateral-pnp-cross-section.svg"), w, h, *frags)


def fig_top_view():
    """Топологічний вигляд зверху (Mask Layout): кільцевий та розділений колектори."""
    w, h = 860, 420
    frags = []

    frags.append(text(w / 2, 28, "Топологія латерального PNP: кільцевий та багатоколекторний дизайн", size=16, bold=True))

    # Ліва панель: концентричний кільцевий колектор
    frags.append(rect(40, 55, 370, 345, fill="#ffffff", stroke="#95a5a6", sw=1.2, rx=6))
    frags.append(text(225, 80, "Кільцевий охоплюючий колектор", size=14, bold=True))

    # n-кишеня (фон)
    frags.append(rect(65, 100, 320, 280, fill="#eef4ff", stroke="#2457d6", sw=1.2, rx=4))
    frags.append(text(125, 122, "n-епітаксія", size=11, color=NEG))

    # Контакт бази n+ (смужка зверху)
    frags.append(rect(80, 135, 290, 25, fill="#cce0ff", stroke="#1f4e99", sw=1.2, rx=3))
    frags.append(text(225, 152, "n⁺ контакт бази (B)", size=11, color="#1f4e99", bold=True))

    # Колекторне p-кільце (зовнішнє)
    frags.append(circle(225, 265, 80, fill="#fadbd8", stroke="#922b21", sw=1.8))

    # n-епі проміжок (база всередині)
    frags.append(circle(225, 265, 45, fill="#eef4ff", stroke="#2457d6", sw=1.5))

    # p-емітер (центр)
    frags.append(circle(225, 265, 25, fill="#f5b7b1", stroke=POS, sw=1.8))
    frags.append(text(225, 270, "E", size=14, color=POS, bold=True))

    frags.append(text(225, 210, "p-колекторне кільце (C)", size=11, color="#922b21", bold=True))
    frags.append(text(225, 370, "Охоплення 360° вловлює > 90% інжектованих дірок", size=11, color=MUTED, italic=True))

    # Права панель: розділений колектор (Split-Collector)
    frags.append(rect(450, 55, 370, 345, fill="#ffffff", stroke="#95a5a6", sw=1.2, rx=6))
    frags.append(text(635, 80, "Розділений колектор (Split-Collector)", size=14, bold=True))

    frags.append(rect(475, 100, 320, 280, fill="#eef4ff", stroke="#2457d6", sw=1.2, rx=4))
    frags.append(text(535, 122, "n-епітаксія", size=11, color=NEG))

    # Контакт бази n+
    frags.append(rect(490, 135, 290, 25, fill="#cce0ff", stroke="#1f4e99", sw=1.2, rx=3))
    frags.append(text(635, 152, "n⁺ контакт бази (B)", size=11, color="#1f4e99", bold=True))

    # Ліве півкільце колектора C1
    frags.append(rect(540, 180, 75, 160, fill="#fadbd8", stroke="#922b21", sw=1.5, rx=6))
    frags.append(text(575, 265, "C₁ (50%)", size=12, color="#922b21", bold=True))

    # Праве півкільце колектора C2
    frags.append(rect(655, 180, 75, 160, fill="#fadbd8", stroke="#922b21", sw=1.5, rx=6))
    frags.append(text(695, 265, "C₂ (50%)", size=12, color="#922b21", bold=True))

    # Центральний емітер E
    frags.append(circle(635, 260, 22, fill="#f5b7b1", stroke=POS, sw=1.8))
    frags.append(text(635, 265, "E", size=13, color=POS, bold=True))

    frags.append(text(635, 370, "Прецизійний поділ струму I_C1 = I_C2 = 0.5 · I_C", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "lateral-pnp-top-view.svg"), w, h, *frags)


def fig_lateral_vs_vertical():
    """Фізичне порівняння вертикального NPN та латерального PNP."""
    w, h = 860, 460
    frags = []

    frags.append(text(w / 2, 28, "Порівняння фізики вертикального NPN та латерального PNP", size=16, bold=True))

    # Ліва картка: Вертикальний NPN
    frags.append(rect(40, 55, 370, 385, fill="#ffffff", stroke="#2457d6", sw=1.5, rx=6))
    frags.append(text(225, 82, "Вертикальний NPN (оптимізований)", size=15, color=NEG, bold=True))

    frags.append(rect(65, 105, 320, 140, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=4))
    # Схематичний розріз шарів NPN
    frags.append(rect(85, 115, 240, 28, fill="#d6e4ff", stroke="#2457d6", sw=1.2, rx=2))
    frags.append(text(205, 134, "n⁺ Емітер (сильно легований)", size=11, color=NEG, bold=True))

    frags.append(rect(85, 148, 240, 26, fill="#fadbd8", stroke="#922b21", sw=1.2, rx=2))
    frags.append(text(205, 165, "p База (W_B ≈ 0.2–0.5 мкм, дифузійна)", size=10, color="#922b21", bold=True))

    frags.append(rect(85, 179, 240, 55, fill="#eef4ff", stroke="#2457d6", sw=1.2, rx=2))
    frags.append(text(205, 210, "n Колектор (епітаксія + NBL)", size=11, color=NEG, bold=True))

    # Стрілка вертикального руху електронів збоку
    frags.append(arrow(345, 125, 345, 220, color=NEG, sw=2.5))
    frags.append(text(345, 235, "e⁻", size=11, color=NEG, bold=True))

    # Параметри NPN
    p_npn = [
        "• Носії: електрони (висока рухливість μ_n ≈ 1350 см²/В·с)",
        "• База: надтонка (W_B ~ 0.3 мкм), задана дифузією",
        "• Час прольоту бази: τ_B ≈ 0.1–0.2 нс",
        "• Коефіцієнт підсилення: β ≈ 100–300",
        "• Гранична частота: f_T ≈ 300–800 МГц",
        "• Поверхнева рекомбінація: мінімальна (струм у глибині)"
    ]
    for i, p in enumerate(p_npn):
        frags.append(text(70, 275 + i * 24, p, size=11, color=INK, anchor="start"))

    # Права картка: Латеральний PNP
    frags.append(rect(450, 55, 370, 385, fill="#ffffff", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(text(635, 82, "Латеральний PNP (без додаткових масок)", size=15, color=POS, bold=True))

    frags.append(rect(475, 105, 320, 140, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=4))
    # Схематичний розріз PNP
    frags.append(rect(495, 120, 80, 55, fill="#fadbd8", stroke="#922b21", sw=1.2, rx=2))
    frags.append(text(535, 150, "p Емітер", size=11, color="#922b21", bold=True))

    frags.append(rect(580, 120, 110, 55, fill="#eef4ff", stroke="#2457d6", sw=1.2, rx=2))
    frags.append(text(635, 145, "n-база", size=11, color=NEG, bold=True))
    frags.append(text(635, 162, "W_B ≈ 1–3 мкм", size=10, color="#d35400"))

    frags.append(rect(695, 120, 80, 55, fill="#fadbd8", stroke="#922b21", sw=1.2, rx=2))
    frags.append(text(735, 150, "p Колектор", size=11, color="#922b21", bold=True))

    # Стрілка горизонтального руху дірок
    frags.append(arrow(570, 147, 700, 147, color=POS, sw=2.5))

    # Параметри PNP
    p_pnp = [
        "• Носії: дірки (низька рухливість μ_p ≈ 450 см²/В·с)",
        "• База: широка (W_B ~ 1–3 мкм), задана літографією",
        "• Час прольоту бази: τ_B ≈ 20–30 нс (у 150 разів повільніше!)",
        "• Коефіцієнт підсилення: β ≈ 10–50",
        "• Гранична частота: f_T ≈ 2–8 МГц (< 10 МГц)",
        "• Поверхнева рекомбінація: сильна біля межі Si-SiO₂"
    ]
    for i, p in enumerate(p_pnp):
        frags.append(text(480, 275 + i * 24, p, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "lateral-vs-vertical-bjt.svg"), w, h, *frags)


def fig_circuits():
    """Схемотехнічне застосування латерального PNP: активне навантаження, зсув рівня, вхідний каскад LM324."""
    w, h = 860, 440
    frags = []

    frags.append(text(w / 2, 28, "Типове застосування латерального PNP в аналогових мікросхемах", size=16, bold=True))

    # Блок (а): Активне навантаження (струмове дзеркало)
    frags.append(rect(40, 55, 245, 365, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(162, 80, "а) Активне навантаження", size=13, bold=True))

    # Шина V+
    frags.append(line(60, 110, 265, 110, color=POS, sw=2))
    frags.append(text(162, 102, "V⁺ (живлення)", size=11, color=POS, bold=True))

    # PNP дзеркало Q1 / Q2
    # Q1
    frags.append(circle(105, 160, 18, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(105, 165, "Q₁", size=12, color=POS, bold=True))
    frags.append(line(105, 110, 105, 142, color=LINE, sw=1.5))
    frags.append(line(105, 178, 105, 230, color=LINE, sw=1.5))

    # Q2
    frags.append(circle(220, 160, 18, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(220, 165, "Q₂", size=12, color=POS, bold=True))
    frags.append(line(220, 110, 220, 142, color=LINE, sw=1.5))
    frags.append(line(220, 178, 220, 230, color=LINE, sw=1.5))

    # З'єднання баз
    frags.append(line(123, 160, 202, 160, color=LINE, sw=1.5))
    # Діодне включення Q1
    frags.append(line(150, 160, 150, 200, color=LINE, sw=1.5))
    frags.append(line(150, 200, 105, 200, color=LINE, sw=1.5))

    # Диференціальна пара NPN (Q3, Q4)
    frags.append(circle(105, 260, 18, fill="#d6e4ff", stroke=NEG, sw=1.5))
    frags.append(text(105, 265, "Q₃", size=12, color=NEG, bold=True))
    frags.append(circle(220, 260, 18, fill="#d6e4ff", stroke=NEG, sw=1.5))
    frags.append(text(220, 265, "Q₄", size=12, color=NEG, bold=True))

    frags.append(line(105, 278, 162, 320, color=LINE, sw=1.5))
    frags.append(line(220, 278, 162, 320, color=LINE, sw=1.5))
    frags.append(line(162, 320, 162, 350, color=LINE, sw=1.5))
    frags.append(text(162, 365, "I_tail", size=11, color=MUTED))

    # Вихід
    frags.append(line(220, 205, 265, 205, color=FIELD, sw=2))
    frags.append(text(265, 195, "V_out", size=11, color=FIELD, bold=True))

    frags.append(text(162, 395, "Підсилення A_v ~ 1000–5000", size=10, color=MUTED, italic=True))

    # Блок (б): Зсув рівня (Level Shifter)
    frags.append(rect(305, 55, 245, 365, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(427, 80, "б) Зсув рівня напруги", size=13, bold=True))

    frags.append(line(325, 110, 530, 110, color=POS, sw=2))
    frags.append(text(427, 102, "V⁺", size=11, color=POS, bold=True))

    # PNP каскад зі спільним емітером / базою
    frags.append(circle(427, 160, 20, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(427, 165, "Q_PNP", size=11, color=POS, bold=True))
    frags.append(line(427, 110, 427, 140, color=LINE, sw=1.5))

    # Вхідний сигнал біля шини V+
    frags.append(line(335, 160, 407, 160, color=LINE, sw=1.5))
    frags.append(text(360, 150, "V_in(V⁺)", size=10, bold=True))

    # Колектор стікає вниз до навантаження біля GND
    frags.append(line(427, 180, 427, 260, color=LINE, sw=1.5))
    frags.append(rect(412, 260, 30, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(427, 290, "R_L", size=11, bold=True))
    frags.append(line(427, 310, 427, 350, color=LINE, sw=1.5))

    # Шина GND
    frags.append(line(380, 350, 475, 350, color=LINE, sw=2))
    frags.append(text(427, 368, "GND / V⁻", size=11, bold=True))

    # Вихід біля GND
    frags.append(line(427, 230, 510, 230, color=FIELD, sw=2))
    frags.append(text(510, 220, "V_out(GND)", size=10, color=FIELD, bold=True))

    frags.append(text(427, 395, "Перенесення сигналу зверху вниз", size=10, color=MUTED, italic=True))

    # Блок (в): Вхідний каскад LM324 (діапазон від 0 В / GND)
    frags.append(rect(570, 55, 250, 365, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(695, 80, "в) Вхід LM324 (0 В / GND)", size=13, bold=True))

    frags.append(line(590, 110, 800, 110, color=POS, sw=2))
    frags.append(text(695, 102, "V⁺", size=11, color=POS, bold=True))

    # Джерело струму I_tail
    frags.append(circle(695, 140, 14, fill="#f4f6f8", stroke=LINE, sw=1.2))
    frags.append(line(695, 110, 695, 126, color=LINE, sw=1.5))
    frags.append(line(695, 154, 695, 175, color=LINE, sw=1.5))
    frags.append(line(640, 175, 750, 175, color=LINE, sw=1.5))

    # PNP вхідна пара Q1, Q2 (емітерні повторювачі)
    frags.append(circle(640, 205, 16, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(640, 210, "Q₁", size=11, color=POS, bold=True))
    frags.append(line(640, 175, 640, 189, color=LINE, sw=1.5))

    frags.append(circle(750, 205, 16, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(750, 210, "Q₂", size=11, color=POS, bold=True))
    frags.append(line(750, 175, 750, 189, color=LINE, sw=1.5))

    # Входи V_IN- та V_IN+
    frags.append(line(590, 205, 624, 205, color=LINE, sw=1.5))
    frags.append(text(585, 195, "IN⁻ (≥ 0 В)", size=9, bold=True))

    frags.append(line(766, 205, 800, 205, color=LINE, sw=1.5))
    frags.append(text(800, 195, "IN⁺ (≥ 0 В)", size=9, bold=True))

    # Q1/Q2 колектори на GND
    frags.append(line(640, 221, 640, 270, color=LINE, sw=1.5))
    frags.append(line(750, 221, 750, 270, color=LINE, sw=1.5))

    frags.append(circle(640, 285, 16, fill="#d6e4ff", stroke=NEG, sw=1.5))
    frags.append(text(640, 290, "Q₃", size=11, color=NEG, bold=True))

    frags.append(circle(750, 285, 16, fill="#d6e4ff", stroke=NEG, sw=1.5))
    frags.append(text(750, 290, "Q₄", size=11, color=NEG, bold=True))

    frags.append(line(640, 301, 640, 350, color=LINE, sw=1.5))
    frags.append(line(750, 301, 750, 350, color=LINE, sw=1.5))

    frags.append(line(610, 350, 780, 350, color=LINE, sw=2))
    frags.append(text(695, 368, "GND (0 В)", size=11, bold=True))

    frags.append(text(695, 395, "Синфазний сигнал включає 0 В", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "lateral-pnp-circuits.svg"), w, h, *frags)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    fig_cross_section()
    fig_top_view()
    fig_lateral_vs_vertical()
    fig_circuits()
    print("All figures generated successfully.")
