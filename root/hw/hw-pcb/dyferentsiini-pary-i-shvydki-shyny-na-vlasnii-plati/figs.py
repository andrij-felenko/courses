# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Диференційні пари й швидкі шини на власній платі'."""

import os
import sys

# Підключення svgkit із кореневої теки scripts (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_diff_microstrip_geometry():
    """Фігура 1: Поперечний переріз диференційної мікросмужки та силові лінії полів (парний і непарний режими)."""
    w, h = 840, 480
    frags = []

    # Загальний фон та заголовок
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Електромагнітна структура диференційної мікросмужкової лінії", size=16, bold=True))

    # Ліва панель: Непарний режим (Odd Mode / Диференційний сигнал)
    frags.append(rect(30, 60, 375, 260, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(217, 84, "Непарний режим (Odd Mode): V+ та V−", size=13, color="#1e40af", bold=True))

    # Діелектрик зліва
    frags.append(rect(50, 170, 335, 90, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=0))
    frags.append(text(85, 215, "Діелектрик\nε_r, h", size=11, color="#475569", bold=True))

    # Опорна площина землі (GND)
    frags.append(rect(50, 260, 335, 16, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=0))
    frags.append(text(217, 272, "Опорна площина землі (GND Reference Plane)", size=10, color="#334155", bold=True))

    # Провідник D+ (позитивний)
    frags.append(rect(125, 150, 75, 20, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=2))
    frags.append(text(162, 164, "D+ (+V)", size=11, color="#9a3412", bold=True))

    # Провідник D- (негативний)
    frags.append(rect(235, 150, 75, 20, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=2))
    frags.append(text(272, 164, "D− (−V)", size=11, color="#9a3412", bold=True))

    # Силові лінії електричного поля в непарному режимі
    # Між провідниками (сильний зв'язок)
    frags.append(line(200, 156, 235, 156, color=POS, sw=1.8))
    frags.append(line(200, 164, 235, 164, color=POS, sw=1.8))
    # До площини землі
    frags.append(line(140, 170, 140, 260, color="#3b82f6", sw=1.4, dash="3,2"))
    frags.append(line(162, 170, 162, 260, color="#3b82f6", sw=1.4, dash="3,2"))
    frags.append(line(185, 170, 185, 260, color="#3b82f6", sw=1.4, dash="3,2"))
    frags.append(line(250, 170, 250, 260, color="#3b82f6", sw=1.4, dash="3,2"))
    frags.append(line(272, 170, 272, 260, color="#3b82f6", sw=1.4, dash="3,2"))
    frags.append(line(295, 170, 295, 260, color="#3b82f6", sw=1.4, dash="3,2"))

    # Віртуальна земля по центру
    frags.append(line(217, 130, 217, 260, color="#16a34a", sw=1.5, dash="4,3"))
    frags.append(text(217, 122, "Віртуальна земля (V = 0)", size=10, color="#15803d", bold=True))

    # Розмірні стрілки зліва
    frags.append(line(125, 140, 200, 140, color=INK, sw=1.2))
    frags.append(text(162, 135, "w", size=11, bold=True))
    frags.append(line(200, 140, 235, 140, color=INK, sw=1.2))
    frags.append(text(217, 135, "s", size=11, bold=True))
    frags.append(line(235, 140, 310, 140, color=INK, sw=1.2))
    frags.append(text(272, 135, "w", size=11, bold=True))

    frags.append(text(217, 305, "Z_diff = 2 · Z_odd = 2 · √( (L₀ − L_m) / (C₀ + C_m) )", size=11, color="#1e40af", bold=True))

    # Права панель: Парний режим (Even Mode / Синфазна завада)
    frags.append(rect(435, 60, 375, 260, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(622, 84, "Парний режим (Even Mode): V+ та V+", size=13, color="#b91c1c", bold=True))

    # Діелектрик справа
    frags.append(rect(455, 170, 335, 90, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=0))
    frags.append(text(490, 215, "Діелектрик\nε_r, h", size=11, color="#475569", bold=True))

    # Опорна площина землі (GND)
    frags.append(rect(455, 260, 335, 16, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=0))
    frags.append(text(622, 272, "Опорна площина землі (GND Reference Plane)", size=10, color="#334155", bold=True))

    # Провідник D+ (позитивний)
    frags.append(rect(530, 150, 75, 20, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=2))
    frags.append(text(567, 164, "D+ (+V)", size=11, color="#9a3412", bold=True))

    # Провідник D+ (теж позитивний синфазний)
    frags.append(rect(640, 150, 75, 20, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=2))
    frags.append(text(677, 164, "D+ (+V)", size=11, color="#9a3412", bold=True))

    # Силові лінії в парному режимі (відштовхуються між собою, всі йдуть на GND)
    frags.append(line(545, 170, 545, 260, color="#dc2626", sw=1.4, dash="3,2"))
    frags.append(line(567, 170, 567, 260, color="#dc2626", sw=1.4, dash="3,2"))
    frags.append(line(590, 170, 580, 260, color="#dc2626", sw=1.4, dash="3,2"))
    frags.append(line(655, 170, 665, 260, color="#dc2626", sw=1.4, dash="3,2"))
    frags.append(line(677, 170, 677, 260, color="#dc2626", sw=1.4, dash="3,2"))
    frags.append(line(700, 170, 700, 260, color="#dc2626", sw=1.4, dash="3,2"))

    # Відштовхування ліній поля по центру
    frags.append(text(622, 140, "E-поле відштовхується", size=10, color="#dc2626", bold=True))

    frags.append(text(622, 305, "Z_comm = Z_even / 2 = 0.5 · √( (L₀ + L_m) / (C₀ − C_m) )", size=11, color="#b91c1c", bold=True))

    # Нижній блок висновків і параметрів
    box_summary, _, _ = textbox(w / 2, 395,
                                "Ключові параметри топології диференційної пари:\n"
                                "• Геометрія: ширина провідника w, зазор у парі s, товщина фольги t, висота діелектрика h над опорною площиною GND.\n"
                                "• Взаємний зв'язок (Coupling): мікросмужки зчеплені через C_m та L_m. При зближенні (менший s) Z_odd падає, а Z_even зростає.\n"
                                "• Опорна земля обов'язкова: 70–85% силових ліній замикаються на GND-площину, а не між провідниками. Розрив землі руйнує імпеданс!",
                                size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=780)
    frags.append(box_summary)

    render(os.path.join(IMG_DIR, "diff-microstrip-geometry.svg"), w, h, *frags)


def fig_skew_phase_tuning():
    """Фігура 2: Компенсація фазового зсуву (Skew) та вирівнювання довжин меандрами біля джерела розбіжності."""
    w, h = 840, 460
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Фазове вирівнювання (Skew Compensation) диференційної пари меандрами", size=16, bold=True))

    # Верхня панель: НЕПРАВИЛЬНО - розбіжність фаз через поворот без локальної компенсації
    frags.append(rect(30, 60, 780, 140, fill="#fef2f2", stroke="#dc2626", sw=1.8, rx=6))
    frags.append(text(190, 82, "ПОМИЛКА: Нескомпенсований поворот (Розбіжність довжин ΔL)", size=13, color="#991b1b", bold=True))

    # Лінії пари (поворот 45 градусів)
    # Зовнішня лінія (довша)
    frags.append('<path d="M 60 110 L 220 110 L 320 160 L 520 160" fill="none" stroke="#ea580c" stroke-width="3"/>')
    frags.append(text(90, 102, "D+ (зовнішня, довша L+)", size=10, color="#9a3412", bold=True))

    # Внутрішня лінія (коротша)
    frags.append('<path d="M 60 125 L 210 125 L 305 175 L 520 175" fill="none" stroke="#2563eb" stroke-width="3"/>')
    frags.append(text(90, 137, "D− (внутрішня, коротша L−)", size=10, color="#1d4ed8", bold=True))

    # Фронт сигналу перекошений праворуч
    frags.append(line(520, 150, 520, 185, color="#dc2626", sw=2, dash="3,2"))
    frags.append(arrow(520, 160, 560, 160, color="#dc2626", sw=2))
    frags.append(arrow(490, 175, 530, 175, color="#dc2626", sw=2))

    frags.append(rect(560, 95, 230, 90, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    frags.append(text(675, 115, "Наслідки перекосу (Skew):", size=11, color="#991b1b", bold=True))
    frags.append(text(675, 133, "• Фазовий зсув Δt = ΔL / v_prop", size=10, color="#b91c1c"))
    frags.append(text(675, 150, "• Генерація синфазної завади V_cm", size=10, color="#b91c1c"))
    frags.append(text(675, 168, "• Закриття 'ока' та ЕМ-випромінювання", size=10, color="#b91c1c"))

    # Нижня панель: ПРАВИЛЬНО - локальний меандр безпосередньо біля вигину
    frags.append(rect(30, 215, 780, 140, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    frags.append(text(210, 237, "ПРАВИЛЬНО: Меандр на короткому провіднику одразу біля вигину", size=13, color="#166534", bold=True))

    # Зовнішня лінія (гладка)
    frags.append('<path d="M 60 265 L 220 265 L 320 315 L 520 315" fill="none" stroke="#ea580c" stroke-width="3"/>')
    frags.append(text(90, 257, "D+ (довша траса)", size=10, color="#9a3412", bold=True))

    # Внутрішня лінія з меандром на виході з повороту
    frags.append('<path d="M 60 280 L 210 280 L 305 330 L 340 330 L 340 345 L 355 345 L 355 330 L 370 330 L 370 345 L 385 345 L 385 330 L 520 330" fill="none" stroke="#2563eb" stroke-width="3"/>')
    frags.append(text(90, 292, "D− (вирівняно меандром)", size=10, color="#1d4ed8", bold=True))

    # Виділення меандра
    frags.append(rect(330, 320, 65, 32, fill="none", stroke="#16a34a", sw=1.5, rx=3))
    frags.append(text(362, 310, "Tuning Accordion", size=10, color="#15803d", bold=True))

    # Синхронний фронт сигналу
    frags.append(line(520, 305, 520, 340, color="#16a34a", sw=2.5))
    frags.append(text(520, 295, "Синфазний фронт", size=10, color="#15803d", bold=True))
    frags.append(arrow(520, 315, 550, 315, color="#16a34a", sw=2))
    frags.append(arrow(520, 330, 550, 330, color="#16a34a", sw=2))

    frags.append(rect(560, 250, 230, 90, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    frags.append(text(675, 270, "Правила геометрії меандра:", size=11, color="#166534", bold=True))
    frags.append(text(675, 288, "• Крок зубців Pitch P ≥ 3·w", size=10, color="#15803d"))
    frags.append(text(675, 306, "• Висота зубця A ≤ 2·s", size=10, color="#15803d"))
    frags.append(text(675, 324, "• Розміщення: біля джерела дисонансу!", size=10, color="#15803d", bold=True))

    # Нижній інформаційний блок
    box_rules, _, _ = textbox(w / 2, 400,
                              "Чому компенсація має бути локальною: Якщо додати меандр наприкінці довгої лінії (біля приймача),\n"
                              "весь проміжний відрізок плати буде нести нескомпенсований фазовий зсув і випромінювати синфазний шум у простір.\n"
                              "Локальне вирівнювання біля кута або роз'єму відновлює синфазність на найранішому етапі й зберігає симетрію поля.",
                              size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=780)
    frags.append(box_rules)

    render(os.path.join(IMG_DIR, "skew-phase-tuning.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_diff_microstrip_geometry()
    fig_skew_phase_tuning()
    print("Всі 2 фігури успішно згенеровано в img/")
