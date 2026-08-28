# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Системи й діапазони: GPS, Galileo, GLONASS, BeiDou, L1/L5»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def dashed_circle(cx, cy, r, stroke=LINE, sw=1.5, dash="4,4"):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw:.1f}" stroke-dasharray="{dash}"/>')


def fig_constellations_orbits():
    """Фігура 1: Супутникові сузір'я — типи орбіт MEO, GEO, IGSO та їхні характеристики."""
    w, h = 940, 480
    frags = []

    # Заголовок та підкладка
    frags.append(rect(15, 15, 910, 450, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(470, 42, "Супутникові сузір'я GNSS: геометрія орбіт та глобальне покриття", size=16, bold=True, color=INK))

    # Секція 1: Схематична модель орбітальних поясів (Зліва)
    frags.append(rect(30, 65, 410, 385, fill="#f8fafc", stroke=LINE, sw=1.0, rx=6))
    frags.append(text(235, 90, "Орбітальні пояси GNSS (масштабовано за висотою)", size=13, bold=True, color=INK))

    # Земля в центрі
    frags.append(circle(235, 260, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.8))
    frags.append(text(235, 256, "Земля", size=12, bold=True, color="#0369a1"))
    frags.append(text(235, 272, "R ≈ 6371 км", size=10, color=MUTED))

    # Орбіта LEO (довідково, низька)
    frags.append(dashed_circle(235, 260, 52, stroke="#94a3b8", sw=1.0, dash="3,3"))

    # Пояс MEO (GPS, GLONASS, Galileo, BeiDou MEO)
    frags.append(dashed_circle(235, 260, 110, stroke="#2563eb", sw=1.5, dash="5,4"))
    frags.append(text(235, 138, "Пояс MEO: 19 100 – 23 222 км", size=11, bold=True, color="#2563eb"))
    frags.append(text(235, 152, "Період обертання: 11.2 – 14.1 год", size=10, color=MUTED))

    # Супутники MEO
    frags.append(circle(145, 205, 6, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(115, 202, "GPS (55°)", size=10, bold=True, color="#1e40af"))

    frags.append(circle(325, 205, 6, fill="#16a34a", stroke=LINE, sw=1))
    frags.append(text(365, 202, "Galileo (56°)", size=10, bold=True, color="#15803d"))

    frags.append(circle(235, 150, 6, fill="#d97706", stroke=LINE, sw=1))
    frags.append(text(285, 168, "GLONASS (64.8°)", size=10, bold=True, color="#b45309"))

    frags.append(circle(180, 335, 6, fill="#dc2626", stroke=LINE, sw=1))
    frags.append(text(180, 355, "BeiDou MEO (55°)", size=10, bold=True, color="#b91c1c"))

    # Пояс GEO / IGSO (35 786 км)
    frags.append(dashed_circle(235, 260, 165, stroke="#7c3aed", sw=1.5, dash="6,4"))
    frags.append(text(235, 78, "Пояс GEO / IGSO: 35 786 км (24 год)", size=11, bold=True, color="#7c3aed"))

    # Супутники GEO та IGSO
    frags.append(circle(75, 260, 6, fill="#7c3aed", stroke=LINE, sw=1))
    frags.append(text(75, 245, "BeiDou GEO", size=10, bold=True, color="#6d28d9"))

    frags.append(circle(395, 290, 6, fill="#0891b2", stroke=LINE, sw=1))
    frags.append(text(395, 310, "QZSS / BDS IGSO", size=10, bold=True, color="#0e7490"))

    # Довідка внизу зліва
    frags.append(rect(45, 385, 380, 52, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(235, 403, "Нахил 64.8° (GLONASS) дає краще покриття приполярних зон,", size=10, color=INK))
    frags.append(text(235, 420, "тоді як 55° (GPS/Galileo/BDS) оптимізовано для помірних широт.", size=10, color=INK))

    # Секція 2: Порівняльна таблиця характеристик сузір'їв (Справа)
    frags.append(rect(455, 65, 455, 385, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    frags.append(text(682, 90, "Параметри чотирьох глобальних констеляцій", size=13, bold=True, color=INK))

    # Рядок GPS
    frags.append(rect(470, 110, 425, 72, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=5))
    frags.append(text(485, 130, "GPS NAVSTAR (США)", size=12, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(485, 148, "• Супутники: 31+ активних на MEO (20 180 км, 6 площин, нахил 55°)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 166, "• Сигнали / Доступ: CDMA (PRN Gold); L1 C/A (1575.42), L2C, L5 (1176.45)", size=11, color=INK, anchor="start"))

    # Рядок Galileo
    frags.append(rect(470, 190, 425, 72, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=5))
    frags.append(text(485, 210, "Galileo (Європейський Союз)", size=12, bold=True, color="#15803d", anchor="start"))
    frags.append(text(485, 228, "• Супутники: 24+ активних на MEO (23 222 км, 3 площини, нахил 56°)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 246, "• Сигнали / Доступ: CDMA (Memory codes); E1 CBOC, E5a (L5), E5b, E6", size=11, color=INK, anchor="start"))

    # Рядок BeiDou
    frags.append(rect(470, 270, 425, 80, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=5))
    frags.append(text(485, 290, "BeiDou-3 (Китай)", size=12, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(485, 308, "• Гібридна структура: 24 MEO (21 528 км, 55°) + 3 GEO + 3 IGSO (35 786 км)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 326, "• Сигнали / Доступ: CDMA (Weil codes); B1I (1561), B1C (1575.42), B2a (L5)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 342, "• Перевага: високі кути місця над Азією завдяки GEO та IGSO", size=10, color=MUTED, anchor="start"))

    # Рядок GLONASS
    frags.append(rect(470, 358, 425, 78, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=5))
    frags.append(text(485, 378, "GLONASS (РФ)", size=12, bold=True, color="#b45309", anchor="start"))
    frags.append(text(485, 396, "• Супутники: 24 на MEO (19 100 км, 3 площини, високий нахил 64.8°)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 414, "• Сигнали / Доступ: FDMA (G1/G2) + CDMA на GLONASS-K/K2; міжканальні зсуви", size=11, color=INK, anchor="start"))
    frags.append(text(485, 429, "• Обмеження: FDMA вимагає калібрування фазових затримок у приймачі", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT_DIR, "gnss-constellations-and-orbits.svg"), w, h, *frags)


def fig_frequency_spectrum():
    """Фігура 2: Частотний спектр L-діапазону: L1, L2 та високоточний L5/E5a/B2a."""
    w, h = 940, 460
    frags = []

    # Фонова рамка
    frags.append(rect(15, 15, 910, 430, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(470, 42, "Радіочастотний спектр GNSS у діапазоні 1150 – 1610 МГц", size=16, bold=True, color=INK))

    # Вісь частот внизу
    frags.append(line(50, 400, 890, 400, color=LINE, sw=2.0))
    frags.append(arrow(870, 400, 895, 400, color=LINE, sw=2.0))
    frags.append(text(890, 422, "Частота f (МГц)", size=11, bold=True, color=INK, anchor="end"))

    # Позначки частотної осі
    ticks = [(1176.45, 180, "1176.45 (L5)"), (1227.60, 430, "1227.60 (L2)"), (1575.42, 740, "1575.42 (L1)")]
    for f_val, x_pos, f_lbl in ticks:
        frags.append(line(x_pos, 395, x_pos, 405, color=LINE, sw=1.5))
        frags.append(text(x_pos, 420, f_lbl, size=11, bold=True, color="#1e3a8a"))

    # Блок 1: Діапазон L5 / E5a / B2a (Зліва)
    frags.append(rect(60, 75, 240, 305, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=6))
    frags.append(text(180, 100, "Діапазон L5 / E5a / B2a", size=13, bold=True, color="#1e40af"))
    frags.append(text(180, 120, "Несуча: 1176.45 МГц", size=12, bold=True, color="#2563eb"))

    # Властивості L5
    frags.append(rect(72, 135, 216, 75, fill="#dbeafe", stroke="#93c5fd", sw=1.0, rx=4))
    frags.append(text(180, 155, "Захищена смуга ARNS", size=11, bold=True, color="#1e40af"))
    frags.append(text(180, 172, "Aeronautical Radionavigation", size=10, color=MUTED))
    frags.append(text(180, 189, "Заборона комерційних завад", size=10, color="#166534"))
    frags.append(text(180, 202, "Висока стійкість до RFI", size=10, color="#166534"))

    frags.append(rect(72, 220, 216, 148, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(80, 240, "• Швидкість чипів: 10.23 Мчип/с", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(80, 258, "• Ширина смуги: 20.46 МГц", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(80, 276, "• Довжина чипа: 29.3 м (10× точніше)", size=10, color="#15803d", anchor="start"))
    frags.append(text(80, 294, "• Пілотний канал (без даних):", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(80, 310, "  когерентне накопичення до", size=10, color=MUTED, anchor="start"))
    frags.append(text(80, 326, "  слабких сигналів (−163 дБм)", size=10, color=MUTED, anchor="start"))
    frags.append(text(80, 346, "• Потужність: +3 дБ вище за L1", size=10, bold=True, color="#1e40af", anchor="start"))

    # Блок 2: Діапазон L2 / E5b / B2b (Центр)
    frags.append(rect(320, 75, 220, 305, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(430, 100, "Діапазон L2 / E5b", size=13, bold=True, color="#334155"))
    frags.append(text(430, 120, "Несуча: 1227.60 МГц", size=12, bold=True, color="#475569"))

    frags.append(rect(332, 135, 196, 75, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(430, 155, "Спільний спектр", size=11, bold=True, color="#475569"))
    frags.append(text(430, 172, "Історично військовий P(Y)", size=10, color=MUTED))
    frags.append(text(430, 190, "Цивільний код L2C", size=10, color=INK))
    frags.append(text(430, 203, "GLONASS G2 (1246 МГц)", size=10, color=MUTED))

    frags.append(rect(332, 220, 196, 148, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(340, 240, "• Швидкість чипів: 1.023 / 0.511", size=10, color=INK, anchor="start"))
    frags.append(text(340, 260, "• Смуга: 2.046 МГц (L2C)", size=10, color=INK, anchor="start"))
    frags.append(text(340, 280, "• Використання: геодезичний", size=10, color=INK, anchor="start"))
    frags.append(text(340, 296, "  RTK на двох частотах L1/L2", size=10, color=INK, anchor="start"))
    frags.append(text(340, 320, "• Недолік: нижча потужність", size=10, color="#b91c1c", anchor="start"))
    frags.append(text(340, 338, "  та вразливість до радарів", size=10, color="#b91c1c", anchor="start"))

    # Блок 3: Діапазон L1 / E1 / B1 / G1 (Справа)
    frags.append(rect(560, 75, 340, 305, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    frags.append(text(730, 100, "Діапазон L1 / E1 / B1 / G1", size=13, bold=True, color="#15803d"))
    frags.append(text(730, 120, "Центральна частота: 1575.42 МГц", size=12, bold=True, color="#16a34a"))

    frags.append(rect(575, 135, 310, 75, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=4))
    frags.append(text(730, 155, "Основний базовий діапазон навігації", size=11, bold=True, color="#15803d"))
    frags.append(text(730, 172, "GPS L1 C/A, Galileo E1 (CBOC), BDS B1C (1575.42)", size=10, color=INK))
    frags.append(text(730, 190, "BDS B1I (1561.098 МГц), GLONASS G1 (1602 МГц FDMA)", size=10, color=MUTED))
    frags.append(text(730, 203, "Присутній у 100% споживчих та бортових приймачів", size=10, color="#15803d"))

    frags.append(rect(575, 220, 310, 148, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(585, 240, "• Швидкість чипів: 1.023 Мчип/с (GPS L1 C/A)", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(585, 258, "• Довжина чипа: 293.05 м (вузька смуга 2.046 МГц)", size=10, color=MUTED, anchor="start"))
    frags.append(text(585, 278, "• Galileo E1: CBOC(6,1,1/11) розносить енергію від центру,", size=10, color="#15803d", anchor="start"))
    frags.append(text(585, 294, "  забезпечуючи гостріший пік автокореляції", size=10, color="#15803d", anchor="start"))
    frags.append(text(585, 316, "• Головна вразливість: перевантажений спектр,", size=10, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(585, 332, "  велика іоносферна затримка та багатопроменевість", size=10, color="#b91c1c", anchor="start"))

    render(os.path.join(OUT_DIR, "gnss-frequency-spectrum-l1-l2-l5.svg"), w, h, *frags)


def fig_multipath_correlation():
    """Фігура 3: Порівняння кореляційних піків та придушення багатопроменевості L1 проти L5."""
    w, h = 940, 440
    frags = []

    # Фонова рамка
    frags.append(rect(15, 15, 910, 410, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(470, 42, "Автокореляція та придушення відбитих сигналів: L1 C/A проти L5", size=16, bold=True, color=INK))

    # Ліва колонка: L1 C/A (Широкий чип, висока вразливість)
    frags.append(rect(30, 65, 425, 345, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(242, 90, "GPS L1 C/A: Чип 1.023 МГц (T_c = 293 м)", size=13, bold=True, color="#b91c1c"))

    # Графік автокореляції L1
    frags.append(line(60, 230, 420, 230, color=LINE, sw=1.5))
    frags.append(line(242, 115, 242, 235, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(242, 246, "0 (Прямий)", size=10, bold=True, color=INK))

    # Трикутник автокореляції прямого сигналу L1 (широкий: ±1 чип = ±293 м)
    # Вершина (242, 125), база (95, 230) до (389, 230)
    frags.append(line(95, 230, 242, 125, color="#2563eb", sw=2.0))
    frags.append(line(242, 125, 389, 230, color="#2563eb", sw=2.0))
    frags.append(text(140, 155, "Прямий R(τ)", size=10, color="#2563eb"))

    # Відбитий сигнал (зсув +30 м = +0.1 чипа, амплітуда 0.5)
    # Зсув x = 242 + 15 = 257, вершина (257, 178), база (110, 230) до (404, 230)
    frags.append(line(110, 230, 257, 178, color="#dc2626", sw=1.5, dash="4,3"))
    frags.append(line(257, 178, 404, 230, color="#dc2626", sw=1.5, dash="4,3"))
    frags.append(text(340, 175, "Відбитий (Multipath)", size=10, color="#dc2626"))

    # Сумарний спотворений пік
    frags.append(circle(252, 120, 5, fill="#dc2626", stroke=LINE, sw=1))
    frags.append(line(252, 120, 252, 230, color="#dc2626", sw=1.2, dash="2,2"))
    frags.append(text(252, 108, "Зсув піка: +12 м!", size=10, bold=True, color="#b91c1c"))

    # Пояснення L1
    frags.append(rect(45, 265, 395, 130, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
    frags.append(text(55, 285, "• Тривалість чипа: T_c = 977.5 нс (293.05 м у просторі)", size=10, color=INK, anchor="start"))
    frags.append(text(55, 305, "• Зона спотворення корелятора: до 1.5 чипа = 440 метрів!", size=10, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(55, 325, "• Будь-яке відбиття від будівель, землі чи крила дрона", size=10, color=INK, anchor="start"))
    frags.append(text(55, 342, "  у радіусі 400 м зсуває нуль дискримінатора стеження,", size=10, color=INK, anchor="start"))
    frags.append(text(55, 360, "  створюючи псевдодалекомірну похибку від 5 до 30 метрів.", size=10, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(55, 380, "• Фільтри EKF інтерпретують це як реальний стрибок координат.", size=9, color=MUTED, anchor="start"))

    # Права колонка: L5 / E5a (Вузький чип, захист від відбиттів)
    frags.append(rect(485, 65, 425, 345, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(697, 90, "GPS L5 / E5a: Чип 10.23 МГц (T_c = 29.3 м)", size=13, bold=True, color="#15803d"))

    # Графік автокореляції L5
    frags.append(line(515, 230, 875, 230, color=LINE, sw=1.5))
    frags.append(line(697, 115, 697, 235, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(697, 246, "0 (Прямий)", size=10, bold=True, color=INK))

    # Трикутник автокореляції L5 (у 10 разів вужчий: база ±14.6 px навколо 697)
    # Вершина (697, 125), база (682, 230) до (712, 230)
    frags.append(line(682, 230, 697, 125, color="#16a34a", sw=2.0))
    frags.append(line(697, 125, 712, 230, color="#16a34a", sw=2.0))
    frags.append(text(697, 112, "Гострий пік L5", size=10, bold=True, color="#15803d"))

    # Відбитий сигнал на відстані 50 м (> 1.5 чипа = 44 м)
    # Зсув x = 697 + 50 px = 747, вершина (747, 178), база (732, 230) до (762, 230)
    frags.append(line(732, 230, 747, 178, color="#dc2626", sw=1.5, dash="4,3"))
    frags.append(line(747, 178, 762, 230, color="#dc2626", sw=1.5, dash="4,3"))
    frags.append(text(790, 175, "Відбиття > 44 м", size=10, color="#dc2626"))

    # Позначення повної розв'язки
    frags.append(rect(725, 195, 125, 28, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=3))
    frags.append(text(787, 213, "Поза вікном раннього/пізнього!", size=9, bold=True, color="#15803d"))

    # Пояснення L5
    frags.append(rect(500, 265, 395, 130, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    frags.append(text(510, 285, "• Тривалість чипа: T_c = 97.75 нс (29.30 м у просторі)", size=10, color=INK, anchor="start"))
    frags.append(text(510, 305, "• Зона чутливості до відбиттів: лише до 1.5 чипа = 44 метри!", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(510, 325, "• Будь-яке відбиття з затримкою понад 44 м падає поза робочу", size=10, color=INK, anchor="start"))
    frags.append(text(510, 342, "  зону раннього/пізнього стробів (Early-Late Tracking) і дає", size=10, color=INK, anchor="start"))
    frags.append(text(510, 360, "  РІВНО 0 метрів систематичного зсуву кодової дальності.", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(510, 380, "• Максимальна похибка від близьких перевідбиттів обмежена < 1.5–3 м.", size=9, color="#166534", anchor="start"))

    render(os.path.join(OUT_DIR, "l1-vs-l5-multipath-and-correlation.svg"), w, h, *frags)


def fig_iono_free_combination():
    """Фігура 4: Усунення іоносферної затримки комбінацією двох частот L1 та L5."""
    w, h = 940, 380
    frags = []

    # Фонова рамка
    frags.append(rect(15, 15, 910, 350, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(470, 42, "Пряме виключення іоносферної дисперсії комбінацією L1 + L5", size=16, bold=True, color=INK))

    # Ліва частина: Фізика іоносферної дисперсії
    frags.append(rect(30, 65, 410, 280, fill="#f8fafc", stroke=LINE, sw=1.0, rx=6))
    frags.append(text(235, 90, "Дисперсія радіохвиль в іонізованій плазмі", size=13, bold=True, color=INK))

    # Іоносферний шар
    frags.append(rect(45, 110, 380, 55, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=4))
    frags.append(text(235, 130, "Іоносфера: вільні електрони (TEC = ∫ N_e ds)", size=11, bold=True, color="#92400e"))
    frags.append(text(235, 150, "Групова затримка коду: I_iono = +40.3 · TEC / f²", size=11, bold=True, color="#b45309"))

    # Два промені L1 та L5 крізь іоносферу
    frags.append(rect(45, 180, 180, 75, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    frags.append(text(135, 202, "Сигнал L1 (1575.42 МГц)", size=11, bold=True, color="#15803d"))
    frags.append(text(135, 222, "Затримка: I₁ = K / f₁²", size=11, color=INK))
    frags.append(text(135, 240, "Наприклад: +10.0 метрів", size=10, color=MUTED))

    frags.append(rect(245, 180, 180, 75, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(335, 202, "Сигнал L5 (1176.45 МГц)", size=11, bold=True, color="#1e40af"))
    frags.append(text(335, 222, "Затримка: I₅ = K / f₅²", size=11, color=INK))
    frags.append(text(335, 240, "I₅ = I₁ · (f₁/f₅)² = +17.93 м", size=10, bold=True, color="#1e40af"))

    frags.append(text(235, 280, "Нижча частота f5 відчуває значно сильнішу затримку плазми.", size=10, color=MUTED))
    frags.append(text(235, 300, "Різниця псевдодальностей (ρ5 − ρ1) прямо вимірює TEC!", size=10, bold=True, color="#b45309"))
    frags.append(text(235, 325, "Не потрібні неточні табличні моделі (Klobuchar / NeQuick).", size=10, color="#166534"))

    # Права частина: Алгебра безіоносферної комбінації
    frags.append(rect(460, 65, 450, 280, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    frags.append(text(685, 90, "Безрозмірна лінійна комбінація (Ionosphere-Free, IF)", size=13, bold=True, color=INK))

    frags.append(rect(475, 110, 420, 75, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=5))
    frags.append(text(685, 132, "Рівняння комбінації псевдодальностей ρ_IF:", size=11, bold=True, color="#1e40af"))
    frags.append(text(685, 155, "ρ_IF = (f₁² · ρ₁ − f₅² · ρ₅) / (f₁² − f₅²)", size=13, bold=True, color=INK))
    frags.append(text(685, 174, "= 2.261 · ρ₁ − 1.261 · ρ₅", size=12, bold=True, color="#1e40af"))

    # Розв'язок і скорочення іоносфери
    frags.append(rect(475, 195, 420, 135, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=5))
    frags.append(text(485, 218, "Підставляємо ρ₁ = r + c·δt + I₁  та  ρ₅ = r + c·δt + I₁·(f₁²/f₅²):", size=10, color=MUTED, anchor="start"))
    frags.append(text(485, 242, "ρ_IF = 2.261·(r + c·δt + I₁) − 1.261·(r + c·δt + 1.7934·I₁)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 266, "= (2.261 − 1.261)·(r + c·δt) + (2.261·I₁ − 2.261·I₁)", size=11, color=INK, anchor="start"))
    frags.append(text(485, 292, "= r + c·δt + 0 · I_iono   [Іоносферну похибку скорочено на 100%!]", size=12, bold=True, color="#15803d", anchor="start"))
    frags.append(text(485, 316, "Плата за комбінацію: зростання некорельованого шуму в √(α²+β²) ≈ 2.59 раза.", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT_DIR, "ionosphere-free-linear-combination.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_constellations_orbits()
    fig_frequency_spectrum()
    fig_multipath_correlation()
    fig_iono_free_combination()
    print("All figures generated successfully.")
