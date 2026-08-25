# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для статті про акустичний шум керамічних конденсаторів."""

import os
import sys

# Підключаємо svgkit із кореневої папки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    text, mtext, rect, line, arrow, circle, textbox,
    render, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_piezo_electrostriction_distortion():
    """Фігура 1: Кристалографічна деформація BaTiO3 та електромеханічний відгук MLCC."""
    W, H = 820, 480
    s = []

    # Фон
    s.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок секції 1: Кристалічна комірка
    s.append(text(210, 28, "Кристалічна комірка BaTiO₃ (перовскіт)", size=15, bold=True, color=INK))
    
    # Ліва панель: Комірка BaTiO3 вище та нижче точки Кюрі (fill="none", щоб не конфліктувати з вкладеними блоками)
    s.append(rect(20, 42, 380, 420, fill="none", stroke="#d1d5db", sw=1.2, rx=8))

    # Вище точки Кюрі (кубічна, параелектрична)
    s.append(text(120, 68, "T > 125 °C (Кубічна, C0G/NP0)", size=12, bold=True, color=MUTED))
    # Куб
    s.append(rect(75, 85, 90, 90, fill="#ffffff", stroke="#4b5563", sw=1.5, rx=2))
    # Іони Ba2+ по кутах
    for bx, by in [(75, 85), (165, 85), (75, 175), (165, 175)]:
        s.append(circle(bx, by, 5, fill="#9ca3af", stroke=INK, sw=1))
    # Іон Ti4+ у центрі (ідеальна симетрія)
    s.append(circle(120, 130, 7, fill=POS, stroke=INK, sw=1))
    s.append(text(120, 134, "+", size=10, bold=True, color="#ffffff", anchor="middle"))
    s.append(text(120, 196, "Центр симетрії збігається", size=11, color=MUTED))
    s.append(text(120, 210, "Дипольний момент = 0", size=11, bold=True, color=FIELD))

    # Нижче точки Кюрі (тетрагональна, X7R/X5R)
    s.append(text(300, 68, "T < 125 °C (Тетрагональна, X7R)", size=12, bold=True, color=POS))
    # Тетрагональна витягнута комірка
    s.append(rect(255, 80, 90, 100, fill="#fff5f5", stroke=POS, sw=1.8, rx=2))
    for bx, by in [(255, 80), (345, 80), (255, 180), (345, 180)]:
        s.append(circle(bx, by, 5, fill="#9ca3af", stroke=INK, sw=1))
    # Іон Ti4+ зміщений вгору
    s.append(circle(300, 120, 7, fill=POS, stroke=INK, sw=1))
    s.append(text(300, 124, "+", size=10, bold=True, color="#ffffff", anchor="middle"))
    # Стрілка диполя Ps
    s.append(arrow(300, 155, 300, 133, color=POS, sw=2))
    s.append(text(318, 148, "P_s", size=12, bold=True, color=POS))
    s.append(text(300, 196, "Зміщення іона Ti⁴⁺ на ~0.01 нм", size=11, color=INK))
    s.append(text(300, 210, "Спонтанна поляризація P_s ≠ 0", size=11, bold=True, color=POS))

    # Розділювальна лінія в лівій панелі
    s.append(line(35, 228, 385, 228, color="#e5e7eb", sw=1.2))

    # Пояснення зворотного п'єзоефекту та електрострикції
    tb1, _, _ = textbox(210, 260, "Зворотний п'єзоефект: S = d₃₃ · E  (лінійний)", size=12, bold=True,
                        pad=8, fill="#eff6ff", stroke=NEG, min_w=340)
    s.append(tb1)
    s.append(text(210, 290, "Знак поля змінює напрямок деформації (розтяг / стиск)", size=11, color=INK))

    tb2, _, _ = textbox(210, 330, "Електрострикція: S = M₃₃ · E²  (квадратична)", size=12, bold=True,
                        pad=8, fill="#fef3c7", stroke="#d97706", min_w=340)
    s.append(tb2)
    s.append(text(210, 360, "Деформація завжди одного знака; подвоює частоту (2f)", size=11, color=INK))

    tb3, _, _ = textbox(210, 410, "Сумарний відгук під DC-зміщенням + AC-пульсаціями:\nS(t) ≈ d_eff · E_ac · sin(ωt) + M₃₃ · E_ac² · sin²(ωt)",
                        size=11, bold=True, pad=8, fill="#ecfdf5", stroke=FIELD, min_w=340)
    s.append(tb3)

    # Права панель: Макроскопічна деформація пакета MLCC (fill="none")
    s.append(text(615, 28, "Динамічна деформація тіла MLCC", size=15, bold=True, color=INK))
    s.append(rect(420, 42, 380, 420, fill="none", stroke="#d1d5db", sw=1.2, rx=8))

    # Реальний деформований прямокутник (витягнутий по висоті, звужений по ширині)
    s.append(rect(490, 70, 240, 160, fill="#e0e7ff", stroke=NEG, sw=2, rx=4))

    # Внутрішні електроди гребінчастої структури
    for i, ey in enumerate([95, 115, 135, 155, 175, 195]):
        if i % 2 == 0:
            # Лівий електрод
            s.append(line(490, ey, 690, ey, color=POS, sw=2.5))
        else:
            # Правий електрод
            s.append(line(530, ey, 730, ey, color=NEG, sw=2.5))

    # Торцеві металізації
    s.append(rect(475, 68, 20, 164, fill="#9ca3af", stroke=INK, sw=1.5, rx=3))
    s.append(rect(725, 68, 20, 164, fill="#9ca3af", stroke=INK, sw=1.5, rx=3))

    s.append(text(485, 60, "Вивід (−)", size=11, bold=True, color=NEG))
    s.append(text(735, 60, "Вивід (+)", size=11, bold=True, color=POS))

    # Стрілки деформації по осі Z (висота: розширення +ΔZ)
    s.append(arrow(610, 52, 610, 68, color=POS, sw=2))
    s.append(arrow(610, 248, 610, 232, color=POS, sw=2))
    s.append(text(610, 44, "Поздовжнє розширення (+ΔZ)", size=12, bold=True, color=POS))

    # Стрілки деформації по осі X (довжина: поперечне стискання −ΔX через коефіцієнт Пуассона)
    s.append(arrow(445, 150, 472, 150, color=NEG, sw=2))
    s.append(arrow(775, 150, 748, 150, color=NEG, sw=2))
    s.append(text(435, 165, "−ΔX", size=11, bold=True, color=NEG))
    s.append(text(785, 165, "−ΔX", size=11, bold=True, color=NEG))

    # Текстовий блок із висновком
    s.append(rect(435, 270, 350, 175, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=6))
    s.append(text(610, 292, "Ключові фізичні чинники амплітуди:", size=12, bold=True, color=INK))
    
    reasons = [
        "1. Електричне поле E = V_ripple / d_layer (до 5 МВ/м)",
        "2. Сегнетоелектрична поляризація кераміки BaTiO₃",
        "3. DC bias зміщує точку й лінеаризує електрострикцію",
        "4. Коефіцієнт Пуассона ν ≈ 0.3 стискає торці по X",
        "5. Циклічне зусилля передається на пайку з частотою f"
    ]
    for idx, rline in enumerate(reasons):
        s.append(text(448, 318 + idx * 24, rline, size=11, color="#374151", anchor="start"))

    render(os.path.join(OUT, 'piezo-electrostriction-distortion.svg'), W, H, *s)


def fig_pcb_speaker_transmission():
    """Фігура 2: Механізм передачі вібрацій на плату та випромінювання звуку (PCB як динамік)."""
    W, H = 820, 460
    s = []

    # Фон
    s.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    s.append(text(410, 26, "Механізм акустичного випромінювання: перетворення мікровібрацій на звук", size=15, bold=True, color=INK))

    # Рамка всієї схеми
    s.append(rect(30, 45, 760, 395, fill="none", stroke="#d1d5db", sw=1.2, rx=8))

    # Друкована плата (FR4)
    s.append(rect(60, 240, 700, 28, fill="#047857", stroke="#065f46", sw=1.5, rx=4))
    s.append(text(410, 258, "Текстолітна основа друкованої плати (FR4, товщина 1.6 мм, велика площа)", size=12, bold=True, color="#ffffff"))

    # Мідні контактні майданчики (Pads)
    s.append(rect(320, 234, 50, 6, fill="#d97706", stroke="#b45309", sw=1, rx=1))
    s.append(rect(450, 234, 50, 6, fill="#d97706", stroke="#b45309", sw=1, rx=1))

    # Тіло конденсатора MLCC над платою
    s.append(rect(335, 140, 150, 80, fill="#e0e7ff", stroke=NEG, sw=2, rx=4))
    s.append(text(410, 175, "Тіло MLCC", size=13, bold=True, color=INK))
    s.append(text(410, 192, "(X7R 1206 / 0805)", size=11, color=MUTED))

    # Металізовані торці MLCC
    s.append(rect(335, 140, 22, 80, fill="#9ca3af", stroke=INK, sw=1.2, rx=2))
    s.append(rect(463, 140, 22, 80, fill="#9ca3af", stroke=INK, sw=1.2, rx=2))

    # Паяні з'єднання (галтелі припою — жорсткі клиноподібні трикутники)
    s.append('<polygon points="320,234 357,234 357,175" fill="#6b7280" stroke="#374151" stroke-width="1.5"/>')
    s.append('<polygon points="463,175 463,234 500,234" fill="#6b7280" stroke="#374151" stroke-width="1.5"/>')

    # Стрілки деформації конденсатора
    s.append(arrow(380, 160, 360, 160, color=POS, sw=2))
    s.append(arrow(440, 160, 460, 160, color=POS, sw=2))
    s.append(text(410, 153, "±ΔL (стиск/розтяг)", size=10, bold=True, color=POS))

    # Сили й моменти на паяних з'єднаннях
    s.append(arrow(345, 230, 330, 245, color=POS, sw=2.5))
    s.append(arrow(475, 230, 490, 245, color=POS, sw=2.5))
    s.append(text(290, 218, "Згинальний момент M_b", size=11, bold=True, color=POS, anchor="end"))
    s.append(text(530, 218, "Згинальний момент M_b", size=11, bold=True, color=POS, anchor="start"))

    # Згинальні хвилі на платі
    s.append(line(70, 280, 750, 280, color="#9ca3af", sw=1, dash="4,4"))
    s.append('<path d="M 70 280 Q 240 325 410 280 T 750 280" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    s.append(text(410, 320, "Динамічний вигин друкованої плати (амплітуда прогину w(x,y))", size=12, bold=True, color="#dc2626"))

    # Акустичні звукові хвилі в повітрі
    for rad, opac in [(40, "0.9"), (80, "0.6"), (120, "0.3")]:
        s.append('<path d="M %d %d Q 410 %d %d %d" fill="none" stroke="%s" stroke-width="2" stroke-opacity="%s"/>'
                 % (410 - rad * 2, 235 - rad, 235 - rad - 20, 410 + rad * 2, 235 - rad, NEG, opac))
        s.append('<path d="M %d %d Q 410 %d %d %d" fill="none" stroke="%s" stroke-width="2" stroke-opacity="%s"/>'
                 % (410 - rad * 2, 275 + rad, 275 + rad + 20, 410 + rad * 2, 275 + rad, NEG, opac))

    s.append(text(410, 80, "Акустичні звукові хвилі в повітрі (20 Гц – 20 кГц, 40–70 дБА)", size=13, bold=True, color=NEG))

    # Інформаційні блоки зліва та справа
    tb_left, _, _ = textbox(175, 120, "1. Сам MLCC (A ≈ 3 мм²):\nВипромінювання мізерне\nчерез акустичний розрив\nімпедансів (σ_rad << 10⁻⁴)",
                            size=11, bold=False, pad=8, fill="#ffffff", stroke="#9ca3af", min_w=210)
    s.append(tb_left)

    tb_right, _, _ = textbox(645, 120, "2. Друкована плата (A ≈ 100 см²):\nПрацює як дифузор динаміка,\nпідсилюючи звуковий тиск\nна 30–50 дБ (до чутного писку)",
                             size=11, bold=False, pad=8, fill="#ffffff", stroke=POS, min_w=220)
    s.append(tb_right)

    # Вузли та пучності резонансу
    s.append(rect(80, 360, 660, 65, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=6))
    s.append(text(410, 380, "Умова сильного посилення шуму (явище «Singing Capacitor»):", size=12, bold=True, color=INK))
    s.append(text(410, 402, "Збіг частоти комутації/пульсацій f_ripple із власною резонансною частотою плати f_(m,n)", size=11, bold=True, color=POS))
    s.append(text(410, 418, "Добротність механічного резонансу FR4 Q ≈ 20...50 породжує різкий сплеск шуму на 15–30 дБ", size=11, color=MUTED))

    render(os.path.join(OUT, 'pcb-speaker-transmission.svg'), W, H, *s)


def fig_acoustic_mitigation_layout():
    """Фігура 3: Топологічні та конструктивні методи придушення шуму."""
    W, H = 820, 500
    s = []

    # Фон
    s.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    s.append(text(410, 26, "Топологічні та механічні методи гасіння акустичного шуму на PCB", size=15, bold=True, color=INK))

    # Квадрант 1 (Верхній лівий): Симетричне розміщення Top / Bottom (fill="none")
    s.append(rect(20, 45, 380, 210, fill="none", stroke="#d1d5db", sw=1.2, rx=6))
    s.append(text(210, 68, "1. Симетричний монтаж (Top + Bottom)", size=13, bold=True, color=FIELD))

    # Плата посередині
    s.append(rect(40, 142, 340, 16, fill="#047857", stroke="#065f46", sw=1, rx=2))
    s.append(text(80, 154, "FR4", size=10, bold=True, color="#ffffff"))

    # Верхній конденсатор
    s.append(rect(160, 95, 100, 40, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    s.append(text(210, 120, "C_top (X7R)", size=11, bold=True, color=INK))
    # Стрілки моменту верхнього
    s.append(arrow(150, 138, 140, 148, color=POS, sw=2))
    s.append(arrow(270, 138, 280, 148, color=POS, sw=2))
    s.append(text(125, 125, "+M_b", size=11, bold=True, color=POS))

    # Нижній конденсатор (дзеркальний)
    s.append(rect(160, 165, 100, 40, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    s.append(text(210, 190, "C_bottom (X7R)", size=11, bold=True, color=INK))
    # Стрілки моменту нижнього
    s.append(arrow(150, 162, 140, 152, color=NEG, sw=2))
    s.append(arrow(270, 162, 280, 152, color=NEG, sw=2))
    s.append(text(125, 175, "−M_b", size=11, bold=True, color=NEG))

    s.append(text(210, 225, "Згинальні моменти компенсуються: ΣM_b ≈ 0", size=11, bold=True, color=FIELD))
    s.append(text(210, 242, "Зниження шуму: на 15–20 дБА", size=11, color=MUTED))

    # Квадрант 2 (Верхній правий): Фрезерування акустичних пазів (fill="none")
    s.append(rect(420, 45, 380, 210, fill="none", stroke="#d1d5db", sw=1.2, rx=6))
    s.append(text(610, 68, "2. Фрезерування пазів (Isolation Slots)", size=13, bold=True, color=FIELD))

    # Плата вид зверху
    s.append(rect(440, 90, 340, 120, fill="#047857", stroke="#065f46", sw=1, rx=4))
    
    # Фрезеровані пази (прорізи в текстоліті)
    s.append(rect(510, 105, 12, 90, fill="#ffffff", stroke="#d1d5db", sw=1, rx=2))
    s.append(rect(698, 105, 12, 90, fill="#ffffff", stroke="#d1d5db", sw=1, rx=2))
    s.append(rect(510, 95, 200, 10, fill="#ffffff", stroke="#d1d5db", sw=1, rx=2))

    # MLCC
    s.append(rect(560, 130, 100, 40, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    s.append(text(610, 155, "MLCC 1206", size=11, bold=True, color=INK))

    s.append(text(475, 150, "Паз", size=10, bold=True, color="#ffffff"))
    s.append(text(745, 150, "Паз", size=10, bold=True, color="#ffffff"))

    s.append(text(610, 225, "Переривання механічного містка хвилі", size=11, bold=True, color=FIELD))
    s.append(text(610, 242, "Зниження шуму: на 10–18 дБА", size=11, color=MUTED))

    # Квадрант 3 (Нижній лівий): Розміщення у вузлах та кут 45° (fill="none")
    s.append(rect(20, 270, 380, 210, fill="none", stroke="#d1d5db", sw=1.2, rx=6))
    s.append(text(210, 292, "3. Розміщення у вузлах та кут 45°", size=13, bold=True, color=FIELD))

    # Малюнок форми коливань плати
    s.append(rect(40, 310, 340, 110, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    # Лінії вузлів
    s.append(line(130, 310, 130, 420, color=FIELD, sw=2, dash="4,2"))
    s.append(line(290, 310, 290, 420, color=FIELD, sw=2, dash="4,2"))
    s.append(text(130, 325, "Вузол", size=10, bold=True, color=FIELD))
    s.append(text(290, 325, "Вузол", size=10, bold=True, color=FIELD))

    # Конденсатор у вузлі (зелений)
    s.append(rect(115, 345, 30, 50, fill="#d1fae5", stroke=FIELD, sw=1.5, rx=2))
    s.append(text(130, 373, "C1", size=10, bold=True, color=FIELD))

    # Конденсатор у пучності (червоний)
    s.append(rect(195, 345, 30, 50, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    s.append(text(210, 373, "C2", size=10, bold=True, color=POS))
    s.append(text(210, 335, "Пучність (макс. звук!)", size=10, color=POS))

    s.append(text(210, 445, "Монтаж біля гвинтів та вузлових ліній", size=11, bold=True, color=FIELD))
    s.append(text(210, 462, "Зниження шуму: на 8–15 дБА", size=11, color=MUTED))

    # Квадрант 4 (Нижній правий): Спеціальні конструкції компонентів (fill="none")
    s.append(rect(420, 270, 380, 210, fill="none", stroke="#d1d5db", sw=1.2, rx=6))
    s.append(text(610, 292, "4. Спеціальні конструкції компонентів", size=13, bold=True, color=FIELD))

    # Конденсатор на металевій ніжці
    s.append(rect(460, 315, 140, 110, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    s.append(rect(480, 330, 100, 45, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=3))
    s.append(text(530, 357, "MLCC", size=11, bold=True, color=INK))
    # Металеві гнучкі ніжки
    s.append('<path d="M 480 340 L 465 340 L 465 395 L 485 395" fill="none" stroke="#f59e0b" stroke-width="2.5"/>')
    s.append('<path d="M 580 340 L 595 340 L 595 395 L 575 395" fill="none" stroke="#f59e0b" stroke-width="2.5"/>')
    s.append(line(450, 400, 610, 400, color="#047857", sw=3))
    s.append(text(530, 415, "Metal Cap (зазор 1 мм)", size=10, bold=True, color="#b45309"))

    # Альтернатива: Полімерний / C0G
    s.append(rect(620, 315, 160, 110, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    s.append(rect(640, 340, 120, 45, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    s.append(text(700, 360, "C0G або Полімер", size=11, bold=True, color=INK))
    s.append(text(700, 375, "(нульовий п'єзоефект)", size=10, color=FIELD))
    s.append(line(630, 400, 770, 400, color="#047857", sw=3))

    s.append(text(610, 445, "Metal Cap / C0G / Полімер", size=11, bold=True, color=FIELD))
    s.append(text(610, 462, "Зниження шуму: на 20–35 дБА (повна тиша)", size=11, color=MUTED))

    render(os.path.join(OUT, 'acoustic-mitigation-layout.svg'), W, H, *s)


def fig_capacitor_technology_noise_comparison():
    """Фігура 4: Спектральне порівняння рівня звукового тиску (SPL) для різних технологій конденсаторів."""
    W, H = 820, 450
    s = []

    # Фон
    s.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    s.append(text(410, 26, "Порівняння рівня звукового тиску (SPL) різних типів конденсаторів", size=15, bold=True, color=INK))

    # Область графіка
    gx, gy, gw, gh = 80, 55, 680, 305
    s.append(rect(gx, gy, gw, gh, fill="#f9fafb", stroke="#9ca3af", sw=1.2, rx=4))

    # Горизонтальні лінії сітки (дБ)
    levels = [
        (60, "60 дБА (Дуже гучний писк)"),
        (50, "50 дБА (Чітко чутно в кімнаті)"),
        (40, "40 дБА (Тихий офіс / поріг комфорту)"),
        (30, "30 дБА (Шепіт / дуже тихо)"),
        (20, "20 дБА (Фоновий шум студії / поріг чутності)")
    ]

    for val, label in levels:
        y = gy + (60 - val) * (gh - 60) / 40 + 20
        s.append(line(gx, y, gx + gw, y, color="#e5e7eb", sw=1, dash="4,4"))
        s.append(text(gx - 8, y + 4, str(val), size=11, bold=True, color=MUTED, anchor="end"))
        s.append(text(gx + gw - 10, y - 5, label, size=10, color="#9ca3af", anchor="end"))

    # Вертикальні лінії сітки (частота 100 Гц, 1 кГц, 3 кГц, 10 кГц, 20 кГц)
    freqs = [
        (100, "100 Гц", 100),
        (500, "500 Гц", 220),
        (1000, "1 кГц", 310),
        (3500, "3.5 кГц (Резонанс PCB)", 450),
        (10000, "10 кГц", 580),
        (20000, "20 кГц", 700)
    ]

    for f_val, f_label, fx in freqs:
        s.append(line(fx, gy, fx, gy + gh, color="#e5e7eb", sw=1, dash="4,4"))
        s.append(text(fx, gy + gh + 18, f_label, size=10, color=MUTED, anchor="middle"))

    # Позначення осей
    s.append(text(gx - 40, gy + gh / 2, "Рівень звуку L_p (дБА)", size=12, bold=True, color=INK, anchor="middle"))
    s.append(text(gx + gw / 2, gy + gh + 35, "Акустична частота пульсацій напруги f (Гц)", size=12, bold=True, color=INK, anchor="middle"))

    # Крива 1: Стандартний MLCC X7R 1206 (Червона, з високим піком на 3.5 кГц)
    s.append('<path d="M 100 290 Q 220 280 310 240 Q 450 75 580 230 T 700 295" fill="none" stroke="#dc2626" stroke-width="3"/>')
    s.append(circle(450, 80, 5, fill="#dc2626", stroke=INK, sw=1))
    s.append(text(450, 68, "58 дБА (X7R стандартний)", size=11, bold=True, color="#dc2626"))

    # Крива 2: Soft-Termination MLCC (Помаранчева, на 8 дБ нижче)
    s.append('<path d="M 100 300 Q 220 295 310 265 Q 450 135 580 255 T 700 305" fill="none" stroke="#d97706" stroke-width="2.5"/>')
    s.append(text(310, 160, "Soft-Termination (−8 дБ)", size=10, bold=True, color="#d97706", anchor="middle"))

    # Крива 3: Двосторонній симетричний монтаж Top/Bottom (Синя, на 18 дБ нижче)
    s.append('<path d="M 100 310 Q 220 305 310 285 Q 450 205 580 280 T 700 315" fill="none" stroke="#2457d6" stroke-width="2.5"/>')
    s.append(text(310, 215, "Top + Bottom (−18 дБ)", size=10, bold=True, color="#2457d6", anchor="middle"))

    # Крива 4: Metal Cap / Interposer (Зелена, на 28 дБ нижче)
    s.append('<path d="M 100 318 Q 220 315 310 305 Q 450 260 580 300 T 700 320" fill="none" stroke="#059669" stroke-width="2.5"/>')
    s.append(text(310, 270, "Metal Cap (−28 дБ)", size=10, bold=True, color="#059669", anchor="middle"))

    # Лінія 5: C0G / Тантал / Полімер (Повна тиша, на рівні шуму 18–20 дБА)
    s.append(line(100, 325, 700, 325, color="#6b7280", sw=2, dash="6,3"))
    s.append(text(450, 342, "C0G / Танталовий полімер / Алюмінієвий полімер (< 20 дБА, нечутно)", size=10, bold=True, color="#4b5563"))

    # Легенда під графіком
    s.append(rect(80, 400, 680, 42, fill="#f3f4f6", stroke="#e5e7eb", sw=1, rx=4))
    s.append(line(95, 421, 125, 421, color="#dc2626", sw=3))
    s.append(text(130, 425, "Стандартний X7R", size=10, color=INK, anchor="start"))

    s.append(line(245, 421, 275, 421, color="#d97706", sw=2.5))
    s.append(text(280, 425, "Soft-Term", size=10, color=INK, anchor="start"))

    s.append(line(365, 421, 395, 421, color="#2457d6", sw=2.5))
    s.append(text(400, 425, "Top/Bottom", size=10, color=INK, anchor="start"))

    s.append(line(490, 421, 520, 421, color="#059669", sw=2.5))
    s.append(text(525, 425, "Metal Cap", size=10, color=INK, anchor="start"))

    s.append(line(610, 421, 640, 421, color="#6b7280", sw=2, dash="4,2"))
    s.append(text(645, 425, "C0G / Полімер", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, 'capacitor-technology-noise-comparison.svg'), W, H, *s)


if __name__ == '__main__':
    fig_piezo_electrostriction_distortion()
    fig_pcb_speaker_transmission()
    fig_acoustic_mitigation_layout()
    fig_capacitor_technology_noise_comparison()
    print("Усі 4 SVG-фігури згенеровано успішно.")
