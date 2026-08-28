# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Клас захисту IP'."""

import os
import sys

# Підключення svgkit із кореневої теки scripts (4 рівні вгору від root/hw/hw-pcb/klas-zakhystu)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_ip_code_structure():
    """Фігура 1: Анатомія та розряди коду IEC 60529 / ISO 20653."""
    w, h = 880, 480
    frags = []

    # Загальна рамка
    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 45, "Структура коду ступеня захисту оболонки (IEC 60529 / ISO 20653)", size=16, bold=True))

    # Центральний блок IP коду
    frags.append(rect(60, 75, 110, 70, fill="#e2e8f0", stroke="#475569", sw=2, rx=6))
    frags.append(text(115, 118, "IP", size=32, bold=True, color="#1e293b"))

    frags.append(rect(185, 75, 180, 70, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    frags.append(text(275, 118, "6 (0–6)", size=28, bold=True, color="#b45309"))

    frags.append(rect(380, 75, 200, 70, fill="#dbeafe", stroke=NEG, sw=2, rx=6))
    frags.append(text(480, 118, "7 / 9K (0–9K)", size=26, bold=True, color=NEG))

    frags.append(rect(595, 75, 220, 70, fill="#f3e8ff", stroke="#7e22ce", sw=2, rx=6))
    frags.append(text(705, 118, "A/B/C/D / M/S", size=22, bold=True, color="#6b21a8"))

    # Пояснення 1-ї цифри (Тверді тіла та пил)
    frags.append(rect(60, 175, 365, 270, fill="#ffffff", stroke="#d97706", sw=1.5, rx=6))
    frags.append(rect(60, 175, 365, 32, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(242, 196, "Перша цифра: тверді предмети й пил", size=13, bold=True, color="#b45309"))

    dust_items = [
        ("0", "Немає захисту від контакту та частинок"),
        ("1", "Предмети > 50 мм (долоня, зусилля 50 Н)"),
        ("2", "Предмети > 12.5 мм (тестовий палець 80 мм)"),
        ("3", "Інструменти й дріт > 2.5 мм (зусилля 3 Н)"),
        ("4", "Дріт і тонкі частки > 1.0 мм (зусилля 1 Н)"),
        ("5", "Пилозахист (Dust-protected, тальк, розрідження 2 кПа)"),
        ("6", "Пилонепроникність (Dust-tight, повний вакуум 8 год)")
    ]
    for i, (num, desc) in enumerate(dust_items):
        y = 230 + i * 30
        frags.append(circle(85, y - 4, 11, fill="#fde68a", stroke="#b45309", sw=1.2))
        frags.append(text(85, y, num, size=11, bold=True, color="#78350f"))
        frags.append(text(105, y, desc, size=11, anchor="start", color=INK))

    # Пояснення 2-ї цифри (Рідини та струмені)
    frags.append(rect(445, 175, 390, 270, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(rect(445, 175, 390, 32, fill="#dbeafe", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(640, 196, "Друга цифра: вода, тиск і занурення", size=13, bold=True, color=NEG))

    water_items = [
        ("0–4", "Краплі вертикальні/під 15°, дощ 60°, бризки 360°"),
        ("5", "Струмені води: сопло 6.3 мм, 12.5 л/хв, тиск 30 кПа"),
        ("6", "Потужні струмені: сопло 12.5 мм, 100 л/хв, напір 100 кПа"),
        ("6K", "Струмені під підвищеним тиском (1000 кПа, ISO 20653)"),
        ("7", "Занурення на 1 м на 30 хв (статичний тиск 9.8 кПа)"),
        ("8", "Тривале занурення на задану глибину (> 1 м під тиском)"),
        ("9K", "Гарячий струмінь: 80 °C, 100 бар (10 МПа), 15 л/хв")
    ]
    for i, (num, desc) in enumerate(water_items):
        y = 230 + i * 30
        frags.append(rect(458, y - 13, 34, 18, fill="#bfdbfe", stroke=NEG, sw=1, rx=3))
        frags.append(text(475, y, num, size=10, bold=True, color="#1e3a8a"))
        frags.append(text(500, y, desc, size=11, anchor="start", color=INK))

    # З'єднувальні стрілки від коду до списків
    frags.append(arrow(275, 145, 275, 172, color="#d97706", sw=2))
    frags.append(arrow(480, 145, 550, 172, color=NEG, sw=2))

    render(os.path.join(IMG_DIR, "ip-code-structure.svg"), w, h, *frags)


def fig_jet_vs_submersion():
    """Фігура 2: Порівняння механіки IP65/IP66 (струмінь) та IP67/IP68 (занурення)."""
    w, h = 880, 430
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "Динамічний напір струменя (IP66) проти гідростатичного тиску (IP67)", size=15, bold=True))

    # Ліва колонка: IP67 занурення
    frags.append(rect(40, 65, 380, 345, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(rect(40, 65, 380, 32, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(230, 86, "IP67: Статичне занурення (глибина 1 м)", size=13, bold=True, color="#0369a1"))

    # Корпус під водою
    frags.append(rect(90, 140, 280, 140, fill="#f8fafc", stroke="#334155", sw=2, rx=4))
    frags.append(rect(110, 160, 240, 100, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    frags.append(text(230, 210, "Герметична порожнина РЕА", size=12, bold=True, color="#334155"))
    frags.append(text(230, 228, "Внутрішній тиск P_0 = 101.3 кПа", size=10, color=MUTED))

    # Симетричні стрілки гідростатичного тиску навколо корпусу
    for x in (140, 200, 260, 320):
        frags.append(arrow(x, 115, x, 138, color=NEG, sw=2))
        frags.append(arrow(x, 305, x, 282, color=NEG, sw=2))
    for y in (170, 210, 250):
        frags.append(arrow(65, y, 88, y, color=NEG, sw=2))
        frags.append(arrow(395, y, 372, y, color=NEG, sw=2))

    frags.append(text(230, 335, "Рівномірний гідростатичний стиск", size=11, bold=True, color=NEG))
    frags.append(text(230, 355, "P = ρ·g·h ≈ 9.81 кПа (обтискає шов ущільнення)", size=10, color=INK))
    frags.append(text(230, 375, "Прокладка стискається щільніше в паз", size=10, color=FIELD, bold=True))

    # Права колонка: IP66 струмінь
    frags.append(rect(450, 65, 390, 345, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(rect(450, 65, 390, 32, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(645, 86, "IP66 / IP69K: Динамічний швидкісний струмінь", size=13, bold=True, color=POS))

    # Сопло зі струменем
    frags.append(rect(470, 180, 50, 30, fill="#64748b", stroke="#334155", sw=1.5, rx=2))
    frags.append(text(495, 198, "Сопло", size=10, bold=True, color="#ffffff"))
    frags.append('<polygon points="520,185 610,150 610,240 520,205" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5" fill-opacity="0.7"/>')
    frags.append(text(565, 200, "100 кПа / 100 л/хв", size=10, bold=True, color="#0369a1"))

    # Стінка корпусу з прогином
    frags.append('<path d="M 620 120 Q 645 195 620 270 L 645 270 Q 670 195 645 120 Z" fill="#cbd5e1" stroke="#475569" stroke-width="2"/>')
    frags.append(text(690, 160, "Локальний", size=11, bold=True, color=POS))
    frags.append(text(690, 175, "прогин стінки", size=11, bold=True, color=POS))

    # Зсув/вибивання прокладки
    frags.append(circle(636, 135, 6, fill="#f97316", stroke="#c2410c", sw=1.5))
    frags.append(circle(643, 255, 6, fill="#f97316", stroke="#c2410c", sw=1.5))
    frags.append(arrow(600, 195, 626, 195, color=POS, sw=3))

    frags.append(text(645, 335, "Динамічний удар: P_dyn = ½·ρ·v² (до 100 кПа/10 МПа)", size=11, bold=True, color=POS))
    frags.append(text(645, 355, "Відгинає тонкі фланці між кріпильними гвинтами", size=10, color=INK))
    frags.append(text(645, 375, "Ризик: вибивання еластомеру та гідророзклинювання", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "jet-vs-submersion-physics.svg"), w, h, *frags)


def fig_gasket_gland_mechanics():
    """Фігура 3: Геометрія паза (Gland Design), радіуси скруглення, стиснення та fill factor."""
    w, h = 880, 440
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "Конструкція паза (Gland Design) та деформація еластомерного O-кільця", size=15, bold=True))

    # Ліва частина: Нестиснутий стан (вільне кільце в пазу)
    frags.append(rect(45, 70, 370, 335, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(230, 95, "1. До складання (вільне O-кільце)", size=13, bold=True, color="#334155"))

    # Верхня кришка
    frags.append(rect(75, 120, 310, 30, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(230, 138, "Верхня кришка корпусу (Flange)", size=11, color="#334155"))

    # Нижній корпус із прямокутним пазом
    frags.append('<path d="M 75 190 L 160 190 L 160 270 L 300 270 L 300 190 L 385 190 L 385 330 L 75 330 Z" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>')

    # Кругле нестиснуте кільце
    frags.append(circle(230, 215, 45, fill="#fed7aa", stroke="#ea580c", sw=2))
    frags.append(text(230, 218, "d_s", size=14, bold=True, color="#9a3412"))

    # Розміри паза
    frags.append(line(160, 285, 300, 285, color="#0284c7", sw=1.5))
    frags.append(text(230, 302, "Ширина паза W (1.3–1.4 · d_s)", size=10, bold=True, color="#0284c7"))
    frags.append(line(315, 190, 315, 270, color="#0284c7", sw=1.5))
    frags.append(text(348, 235, "Глибина H", size=10, bold=True, color="#0284c7"))

    frags.append(text(230, 355, "Вільний переріз: d_s > H на 20–30%", size=11, color=INK))
    frags.append(text(230, 375, "Заповнення паза площею ≈ 65–70%", size=10, color=MUTED))

    # Права частина: Стиснутий стан при затягуванні
    frags.append(rect(455, 70, 380, 335, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(645, 95, "2. Після затягування (стиснення 25%)", size=13, bold=True, color=FIELD))

    # Верхня кришка опущена в контакт з корпусом
    frags.append(rect(490, 140, 310, 30, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=2))
    frags.append('<path d="M 490 170 L 575 170 L 575 250 L 715 250 L 715 170 L 800 170 L 800 330 L 490 330 Z" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>')

    # Деформоване еліптичне кільце, що розширилось у боки
    frags.append('<ellipse cx="645" cy="210" rx="58" ry="38" fill="#fed7aa" stroke="#ea580c" stroke-width="2"/>')

    # Контактні площини зверху і знизу
    frags.append(line(600, 171, 690, 171, color=POS, sw=3))
    frags.append(line(600, 249, 690, 249, color=POS, sw=3))
    frags.append(text(645, 213, "Контактна напруга σ_c", size=11, bold=True, color="#9a3412"))

    # Вільні бічні зазори (Expansion gap)
    frags.append(arrow(580, 210, 587, 210, color="#0284c7", sw=1.5))
    frags.append(arrow(710, 210, 703, 210, color="#0284c7", sw=1.5))
    frags.append(text(645, 275, "Заповнення паза (Gland Fill): 75–85%", size=11, bold=True, color=FIELD))
    frags.append(text(645, 295, "Бічний зазор для розширення (ν ≈ 0.499)", size=10, color=MUTED))

    # Скруглення кромок
    frags.append(circle(575, 170, 3, fill=POS, stroke=POS, sw=1))
    frags.append(circle(715, 170, 3, fill=POS, stroke=POS, sw=1))
    frags.append(text(645, 345, "Фаски/радіуси R = 0.2–0.4 мм запобігають затисканню", size=10, color="#b91c1c", bold=True))
    frags.append(text(645, 365, "100% заповнення → гідроудар і руйнування фланця!", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "gasket-gland-mechanics.svg"), w, h, *frags)


def fig_thermal_breathing_vent():
    """Фігура 4: Фізика термічного вакуумування та мембрана ePTFE (Gore Vent)."""
    w, h = 880, 440
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "Термічне вакуумування та мембранне вирівнювання тиску (ePTFE Vent)", size=15, bold=True))

    # Лівий блок: Глухий корпус без мембрани (всмоктування води при охолодженні)
    frags.append(rect(45, 70, 370, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(rect(45, 70, 370, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(230, 90, "Глухий корпус: термічна помпа (Vacuum Ingress)", size=12, bold=True, color=POS))

    frags.append(rect(75, 120, 310, 160, fill="#f8fafc", stroke="#334155", sw=2, rx=4))
    frags.append(text(230, 150, "Охолодження: 65 °C → 10 °C (дощ)", size=11, bold=True, color="#1e293b"))
    frags.append(text(230, 175, "Розрідження ΔP = -16.5 кПа (-165 мбар)", size=11, bold=True, color=POS))

    # Всмоктування крізь мікродефект
    frags.append(rect(75, 230, 10, 30, fill="#fca5a5", stroke=POS, sw=1.5))
    frags.append(arrow(40, 245, 90, 245, color=NEG, sw=2.5))
    frags.append(text(145, 245, "Вода засмоктується", size=10, bold=True, color=NEG))
    frags.append(circle(200, 260, 5, fill="#38bdf8", stroke=NEG, sw=1))
    frags.append(circle(230, 265, 7, fill="#38bdf8", stroke=NEG, sw=1))
    frags.append(circle(260, 260, 4, fill="#38bdf8", stroke=NEG, sw=1))

    frags.append(text(230, 310, "Наслідки без клапана вирівнювання:", size=11, bold=True, color=POS))
    frags.append(text(230, 330, "• Всмоктування вологи через мікропори", size=10, color=INK))
    frags.append(text(230, 350, "• Конденсація на холодній платі (точка роси)", size=10, color=INK))
    frags.append(text(230, 370, "• Електрохімічна корозія та дендрити", size=10, color=POS, bold=True))

    # Правий блок: Корпус із захисною мембраною ePTFE
    frags.append(rect(455, 70, 380, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(rect(455, 70, 380, 30, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(645, 90, "Корпус із мембраною ePTFE (Gore Vent)", size=12, bold=True, color=FIELD))

    # Корпус з отвором під клапан
    frags.append('<path d="M 485 140 L 575 140 L 575 120 L 715 120 L 715 140 L 805 140 L 805 285 L 485 285 Z" fill="#f8fafc" stroke="#334155" stroke-width="2"/>')

    # Вбудована мембрана у верхньому монтажному гнізді
    frags.append(rect(580, 122, 130, 12, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(645, 131, "Мембрана ePTFE", size=10, bold=True, color="#854d0e"))

    # Пори мембрани (структура): стрілки повітря і краплі води
    frags.append(arrow(620, 106, 620, 148, color=FIELD, sw=2))
    frags.append(arrow(670, 148, 670, 106, color=FIELD, sw=2))
    frags.append(text(645, 162, "Вільний газообмін: N₂, O₂, пара (ΔP ≈ 0)", size=10, bold=True, color=FIELD))

    # Краплі води блокуються на поверхні
    frags.append(circle(595, 108, 6, fill="#38bdf8", stroke=NEG, sw=1.5))
    frags.append(circle(695, 108, 7, fill="#38bdf8", stroke=NEG, sw=1.5))
    frags.append(text(595, 96, "H₂O", size=9, bold=True, color=NEG))
    frags.append(text(695, 94, "Крапля", size=9, bold=True, color=NEG))

    frags.append(text(645, 205, "Внутрішній тиск = зовнішньому", size=11, bold=True, color="#1e293b"))
    frags.append(text(645, 225, "Пори 0.1–1.0 мкм: газ проходить, вода ні", size=10, color=MUTED))
    frags.append(text(645, 245, "Гідрофобність (кут > 110°), WEP > 100 кПа", size=10, color=MUTED))

    frags.append(text(645, 310, "Переваги захисної вентиляції:", size=11, bold=True, color=FIELD))
    frags.append(text(645, 330, "• Немає вакууму → ущільнення не навантажені", size=10, color=INK))
    frags.append(text(645, 350, "• Волога не накопичується, пара виходить", size=10, color=INK))
    frags.append(text(645, 370, "• Збереження IP67 / IP68 / IP69K", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "thermal-vacuum-breathing-vent.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_ip_code_structure()
    fig_jet_vs_submersion()
    fig_gasket_gland_mechanics()
    fig_thermal_breathing_vent()
    print("All figures generated successfully.")
