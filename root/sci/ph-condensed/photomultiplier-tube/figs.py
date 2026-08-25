# -*- coding: utf-8 -*-
"""
figs.py — Генерація SVG-ілюстрацій для теми «Фотоелектронний помножувач (ФЕУ)»
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_pmt_structure():
    """Фігура 1: Загальна схема та будова фотоелектронного помножувача (ФЕУ)."""
    w, h = 820, 420
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Будова та принцип дії фотоелектронного помножувача (ФЕУ)", size=16, bold=True))

    # Скляна вакуумна колба (оболонка)
    frags.append(rect(60, 50, 700, 310, fill="#f8fafc", stroke=MUTED, sw=2, rx=15))

    # Вхідне оптичне вікно та фотокатод (лівий торець)
    frags.append(rect(60, 50, 24, 310, fill="#e2e8f0", stroke=LINE, sw=2, rx=4))
    frags.append(rect(84, 55, 12, 300, fill="#3182ce", stroke="#2b6cb0", sw=1.5, rx=2))

    # Підписи вікна та фотокатода
    frags.append(arrow(110, 390, 72, 360, color=MUTED, sw=1.2))
    frags.append(text(120, 395, "Оптичне вікно", size=12, color=MUTED, anchor="start"))

    frags.append(arrow(140, 25, 90, 55, color="#2b6cb0", sw=1.2))
    frags.append(text(145, 20, "Фотокатод (напилений шар)", size=12, color="#2b6cb0", anchor="start", bold=True))

    # Фокусувальні електроди
    frags.append(rect(140, 75, 18, 50, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    frags.append(rect(140, 285, 18, 50, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(149, 140, "Фокусувальний електрод", size=11, color=MUTED, anchor="middle"))

    # Падаюче світло (фотони)
    for y_off in [120, 165, 210, 255, 290]:
        frags.append(arrow(10, y_off, 80, y_off, color="#d69e2e", sw=2))
    frags.append(text(45, 100, "Падаючі фотони (h·ν)", size=13, color="#b7791f", bold=True))

    # Первинні фотоелектрони
    frags.append(arrow(96, 170, 210, 135, color=NEG, sw=1.5))
    frags.append(arrow(96, 210, 210, 145, color=NEG, sw=1.5))
    frags.append(arrow(96, 250, 210, 155, color=NEG, sw=1.5))
    frags.append(text(145, 110, "Фотоелектрони e⁻", size=12, color=NEG, bold=True))

    # Каскад дінодів D1..D5 та Анод (A)
    dynode_coords = [
        (220, 140, "D1"),
        (310, 260, "D2"),
        (400, 140, "D3"),
        (490, 260, "D4"),
        (580, 140, "D5"),
    ]

    for dx, dy, label in dynode_coords:
        # Вигнута пластина дінода
        frags.append(rect(dx - 15, dy - 25, 30, 50, fill="#e2e8f0", stroke="#475569", sw=2, rx=8))
        frags.append(text(dx, dy + 4, label, size=12, bold=True, color=INK))

    # Анод (A)
    frags.append(rect(670, 170, 16, 80, fill="#fc8181", stroke=POS, sw=2, rx=4))
    frags.append(text(678, 214, "A", size=13, bold=True, color="#9b2c2c"))
    frags.append(text(678, 270, "Анод (колектор)", size=12, color=POS, anchor="middle", bold=True))

    # Пучки вторинних електронів між дінодами
    frags.append(arrow(235, 140, 295, 250, color=NEG, sw=2))
    frags.append(arrow(235, 145, 300, 260, color=NEG, sw=1.5))
    frags.append(text(275, 185, "×δ", size=12, color=NEG, bold=True))

    frags.append(arrow(325, 260, 385, 150, color=NEG, sw=2.2))
    frags.append(arrow(325, 250, 390, 140, color=NEG, sw=1.8))
    frags.append(text(365, 220, "×δ²", size=12, color=NEG, bold=True))

    frags.append(arrow(415, 140, 475, 250, color=NEG, sw=2.5))
    frags.append(arrow(415, 145, 480, 260, color=NEG, sw=2.0))
    frags.append(text(455, 185, "×δ³", size=12, color=NEG, bold=True))

    frags.append(arrow(505, 260, 565, 150, color=NEG, sw=2.8))
    frags.append(arrow(505, 250, 570, 140, color=NEG, sw=2.2))
    frags.append(text(545, 220, "×δ⁴", size=12, color=NEG, bold=True))

    frags.append(arrow(595, 140, 665, 200, color=NEG, sw=3.5))
    frags.append(arrow(595, 150, 665, 210, color=NEG, sw=3.0))
    frags.append(text(640, 160, "Лавина (M = δᴺ)", size=12, color=NEG, bold=True))

    # Лінія напруги знизу
    frags.append(line(84, 345, 686, 345, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(text(385, 365, "Прискорювальне електричне поле (зростання потенціалу U: 0 В → +1500 В)", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "pmt-structure.svg"), w, h, *frags)


def build_dynode_multiplication():
    """Фігура 2: Механізм вторинної електронної емісії на поверхні дінода."""
    w, h = 680, 360
    frags = []

    frags.append(text(w / 2, 26, "Механізм вторинної електронної емісії", size=16, bold=True))

    # Металева/напівпровідникова основа дінода
    frags.append(rect(140, 200, 400, 110, fill="#e2e8f0", stroke=LINE, sw=2, rx=6))
    frags.append(text(340, 255, "Активний шар дінода (BeO, Cs₃Sb, GaP:Cs)", size=13, color=INK, bold=True))
    frags.append(text(340, 280, "Низька робота виходу для вторинних електронів", size=12, color=MUTED))

    # Вакуумний простір зверху
    frags.append(rect(140, 50, 400, 150, fill="#fafafa", stroke=MUTED, sw=1, rx=4))
    frags.append(text(180, 75, "Вакуум", size=12, color=MUTED, italic=True))

    # Первинний електрон
    frags.append(arrow(60, 80, 260, 195, color=NEG, sw=2.5))
    frags.append(circle(60, 80, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(60, 84, "e⁻", size=12, color=NEG, bold=True))
    frags.append(text(130, 70, "Первинний електрон\n(Eₖ = 150–300 еВ)", size=12, color=NEG, bold=True))

    # Точка удару
    frags.append(circle(260, 200, 6, fill=POS, stroke=POS, sw=1))

    # Вторинні електрони, що вилітають у вакуум
    sec_targets = [(330, 90), (370, 110), (410, 135), (440, 160)]
    for tx, ty in sec_targets:
        frags.append(arrow(260, 200, tx, ty, color=NEG, sw=1.8))
        frags.append(circle(tx, ty, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(tx, ty + 3, "e⁻", size=10, color=NEG, bold=True))

    frags.append(textbox(470, 95, "Вторинні електрони\n(к-сть δ = 3..6)", size=12, pad=8, fill="#eaf0fd", stroke=NEG)[0])

    render(os.path.join(IMG_DIR, "dynode-multiplication.svg"), w, h, *frags)


def build_dynode_geometries():
    """Фігура 3: Порівняння основних конфігурацій дінодних систем."""
    w, h = 780, 380
    frags = []

    frags.append(text(w / 2, 26, "Типи конфігурацій дінодних систем ФЕУ", size=16, bold=True))

    # 4 блоки конфігурацій
    # (a) Лінійно-фокусована
    frags.append(fitbox(30, 60, 340, 130, "а) Лінійно-фокусована (Linear focused)\nВисока часова роздільна здатність, малий TTS (0.3-1 нс).\nОптимальна для швидкого таймінгу та рахунку фотонів.", size=13, fill="#f8fafc"))
    # (b) Коробчаста (Box-and-grid)
    frags.append(fitbox(410, 60, 340, 130, "б) Коробчаста з сіткою (Box-and-grid)\nВелика ефективність збору фотоелектронів.\nІдеальна для спектрометрії та слабких світлових потоків.", size=13, fill="#f8fafc"))
    # (c) Жалюзійна (Venetian blind)
    frags.append(fitbox(30, 210, 340, 130, "в) Жалюзійна (Venetian blind)\nВисока стабільність коефіцієнта підсилення, велика площа.\nСтійкість до перевантажень струмом.", size=13, fill="#f8fafc"))
    # (d) Мікроканальна пластина (MCP)
    frags.append(fitbox(410, 210, 340, 130, "г) Мікроканальна пластина (MCP-PMT)\nУльтрашвидкий відгук (TTS < 100 пс), компактність.\nСтійкість до зовнішніх магнітних полів.", size=13, fill="#f8fafc"))

    render(os.path.join(IMG_DIR, "dynode-geometries.svg"), w, h, *frags)


def build_voltage_divider_schematic():
    """Фігура 4: Схемотехніка високовольтного дільника напруги ФЕУ."""
    w, h = 760, 360
    frags = []

    frags.append(text(w / 2, 26, "Електрична схема дільника напруги ФЕУ", size=16, bold=True))

    # Джерело високої напруги (-HV) та Земля (GND)
    frags.append(textbox(80, 80, "-HV\n(-1500 В)", size=13, pad=8, fill="#fee2e2", stroke=POS)[0])
    frags.append(textbox(680, 80, "GND\n(0 В)", size=13, pad=8, fill="#e2e8f0", stroke=LINE)[0])

    # Головний резистивний ланцюг
    frags.append(line(130, 80, 630, 80, color=LINE, sw=2))

    # Резистори дільника R1..RN
    res_x = [180, 280, 380, 480, 580]
    for i, rx in enumerate(res_x):
        frags.append(rect(rx - 20, 65, 40, 30, fill="#ffffff", stroke=LINE, sw=1.8, rx=3))
        frags.append(text(rx, 80, "R", size=12, bold=True))
        frags.append(text(rx, 115, "R%d" % (i + 1), size=11, color=MUTED))

    # Підключення електродів
    frags.append(arrow(130, 80, 130, 180, color=POS, sw=2))
    frags.append(text(130, 205, "Катод (K)", size=12, bold=True, color=POS))

    frags.append(arrow(230, 80, 230, 180, color=LINE, sw=1.8))
    frags.append(text(230, 205, "D1", size=12, bold=True))

    frags.append(arrow(330, 80, 330, 180, color=LINE, sw=1.8))
    frags.append(text(330, 205, "D2", size=12, bold=True))

    frags.append(arrow(430, 80, 430, 180, color=LINE, sw=1.8))
    frags.append(text(430, 205, "D(N-1)", size=12, bold=True))

    frags.append(arrow(530, 80, 530, 180, color=LINE, sw=1.8))
    frags.append(text(530, 205, "DN", size=12, bold=True))

    frags.append(arrow(630, 80, 630, 180, color=NEG, sw=2))
    frags.append(text(630, 205, "Анод (A)", size=12, bold=True, color=NEG))

    # Розв'язувальні конденсатори C1, C2 на останніх дінодах
    frags.append(rect(465, 120, 30, 20, fill="#e2e8f0", stroke="#2b6cb0", sw=1.5, rx=2))
    frags.append(text(480, 134, "C", size=10, color="#2b6cb0", bold=True))
    frags.append(text(480, 155, "Буферний C", size=10, color="#2b6cb0"))

    frags.append(rect(565, 120, 30, 20, fill="#e2e8f0", stroke="#2b6cb0", sw=1.5, rx=2))
    frags.append(text(580, 134, "C", size=10, color="#2b6cb0", bold=True))

    # Вихідний сигнал через розділювальний конденсатор Cout
    frags.append(line(630, 180, 630, 260, color=NEG, sw=2))
    frags.append(rect(615, 260, 30, 20, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=2))
    frags.append(text(630, 274, "Cₒᵤₜ", size=11, color=NEG, bold=True))
    frags.append(arrow(630, 280, 630, 320, color=NEG, sw=2))
    frags.append(text(630, 340, "Вихідний імпульс сигналу (50 Ом)", size=12, color=NEG, bold=True, anchor="middle"))

    render(os.path.join(IMG_DIR, "voltage-divider-schematic.svg"), w, h, *frags)


def build_timing_and_tts():
    """Фігура 5: Часові характеристики анодного імпульсу та розкид часу прольоту (TTS)."""
    w, h = 760, 360
    frags = []

    frags.append(text(w / 2, 26, "Часові характеристики та розкид часу прольоту (TTS)", size=16, bold=True))

    # Осі координат для імпульсу
    frags.append(arrow(60, 280, 420, 280, color=LINE, sw=2))
    frags.append(text(425, 284, "Час t (нс)", size=12, color=LINE, anchor="start"))

    frags.append(arrow(60, 280, 60, 60, color=LINE, sw=2))
    frags.append(text(55, 50, "Струм анода I", size=12, color=LINE, anchor="end"))

    # Світловий спалах t=0
    frags.append(line(90, 80, 90, 280, color="#d69e2e", sw=1.5, dash="3,3"))
    frags.append(text(90, 298, "t = 0 (фотон)", size=11, color="#b7791f", bold=True))

    # Сформований анодний імпульс
    frags.append(arrow(260, 280, 260, 110, color=NEG, sw=2.5))
    frags.append(text(260, 95, "Пік імпульсу Iₚₑₐₖ", size=12, color=NEG, bold=True))

    # Час прольоту t_TT (Transit Time)
    frags.append(arrow(90, 240, 260, 240, color=FIELD, sw=1.8))
    frags.append(text(175, 230, "Час прольоту tₜₜ (15–40 нс)", size=12, color=FIELD, bold=True))

    # Тривалість імпульсу FWHM
    frags.append(line(220, 185, 310, 185, color=POS, sw=1.5))
    frags.append(text(265, 175, "FWHM (1–3 нс)", size=11, color=POS, bold=True))

    # Права частина: розподіл TTS (Jitter)
    frags.append(rect(480, 60, 240, 240, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(600, 85, "Розподіл TTS (Часовий джитер)", size=13, bold=True))

    # Гаусове колокола TTS
    frags.append(circle(600, 170, 45, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(600, 174, "σₜₜₛ = 0.2–1 нс", size=12, color=NEG, bold=True))
    frags.append(text(600, 240, "Флуктуація часу прольоту\nміж окремими фотонами", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "timing-and-tts.svg"), w, h, *frags)


if __name__ == "__main__":
    build_pmt_structure()
    build_dynode_multiplication()
    build_dynode_geometries()
    build_voltage_divider_schematic()
    build_timing_and_tts()
    print("Всі 5 фігур успішно згенеровано у ./img/")
