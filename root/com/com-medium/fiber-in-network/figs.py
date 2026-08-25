# -*- coding: utf-8 -*-
"""Фігури до теми «Мережеве оптичне волокно: архітектури, мультиплексування та оптичний бюджет».
Запуск: python figs.py  → створює SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Додаткові кольори для оптики
FIBER_CORE = "#3498db"  # Блакитний — волокно / сигнал
DOWNSTREAM = "#27ae60"  # Зелений — Downstream (1490/1577 нм)
UPSTREAM   = "#e67e22"  # Помаранчевий — Upstream (1310/1270 нм)
LASER_RED  = "#c0392b"  # Червоний — лазер DWDM / C-діапазон
AMPLIFIER  = "#8e44ad"  # Фіолетовий — підсилювач EDFA
SPLITTER   = "#d35400"  # Темно-помаранчевий — пасивний сплітер
CLADDING   = "#bdc3c7"  # Сірий — оболонка волокна
COAX_SH    = "#718096"  # Оболонка роз'єму


# ── 1. Архітектура пасивної оптичної мережі (PON) ───────────────────────────
def fig_pon_architecture():
    W, H = 820, 410
    f = [text(W / 2, 26, "Архітектура пасивної оптичної мережі (PON): OLT, сплітер та ONU", size=15, bold=True)]

    # Центральний вузол (OLT)
    f.append(rect(20, 50, 190, 290, fill="#f4f6f8", stroke=FIBER_CORE, sw=1.5, rx=8))
    f.append(text(115, 75, "Центральна станція (CO)", size=13, bold=True, color=FIBER_CORE))
    f.append(rect(35, 95, 160, 110, fill="#ebf5fb", stroke=FIBER_CORE, sw=1.2, rx=6))
    f.append(text(115, 120, "OLT", size=15, bold=True, color=FIBER_CORE))
    f.append(text(115, 140, "Optical Line Terminal", size=10, color=MUTED))
    f.append(text(115, 165, "TX: 1490 / 1577 нм", size=10, bold=True, color=DOWNSTREAM))
    f.append(text(115, 182, "RX: 1310 / 1270 нм", size=10, bold=True, color=UPSTREAM))

    f.append(text(115, 230, "WDM-фільтр OLT", size=11, bold=True, color=INK))
    f.append(text(115, 250, "Розділення TX/RX", size=10, color=MUTED))
    f.append(text(115, 270, "на одній нитці", size=10, color=MUTED))
    f.append(text(115, 315, "Шина Ethernet 10G/100G", size=10, bold=True, color=MUTED))

    # Магістральне волокно (Feeder Fiber)
    f.append(line(195, 150, 360, 150, color=FIBER_CORE, sw=3))
    f.append(arrow(210, 140, 270, 140, color=DOWNSTREAM, sw=1.8))
    f.append(text(240, 130, "Downstream (1490 нм)", size=10, bold=True, color=DOWNSTREAM))
    f.append(arrow(270, 160, 210, 160, color=UPSTREAM, sw=1.8))
    f.append(text(240, 175, "Upstream TDMA (1310 нм)", size=10, bold=True, color=UPSTREAM))
    f.append(text(275, 195, "Магістральний кабель (до 20 км)", size=10, italic=True, color=MUTED))

    # Пасивний оптичний розгалужувач (Splitter 1:N)
    f.append(rect(360, 100, 100, 180, fill="#fdebd0", stroke=SPLITTER, sw=1.8, rx=8))
    f.append(text(410, 130, "Пасивний", size=12, bold=True, color=SPLITTER))
    f.append(text(410, 148, "сплітер 1:32", size=13, bold=True, color=SPLITTER))
    f.append(text(410, 180, "Втрати:", size=10, bold=True, color=INK))
    f.append(text(410, 198, "10·log2(32) ≈ 15 дБ", size=10, color=INK))
    f.append(text(410, 240, "Без живлення!", size=11, bold=True, color=POS))
    f.append(text(410, 260, "(шафа в дворі)", size=9, italic=True, color=MUTED))

    # Розподільчі нитки до абонентів (Distribution Fibers)
    # Абонент 1
    f.append(line(460, 120, 620, 90, color=FIBER_CORE, sw=2))
    f.append(rect(620, 65, 180, 50, fill="#e8f8f5", stroke=DOWNSTREAM, sw=1.2, rx=6))
    f.append(text(710, 85, "ONU 1 (Будинок A)", size=11, bold=True, color=DOWNSTREAM))
    f.append(text(710, 102, "Пакетний фільтр MAC", size=9, color=MUTED))

    # Абонент 2
    f.append(line(460, 150, 620, 150, color=FIBER_CORE, sw=2))
    f.append(rect(620, 125, 180, 50, fill="#e8f8f5", stroke=DOWNSTREAM, sw=1.2, rx=6))
    f.append(text(710, 145, "ONU 2 (Квартира 12)", size=11, bold=True, color=DOWNSTREAM))
    f.append(text(710, 162, "Часовий слот T2 (Upstream)", size=9, color=UPSTREAM))

    # Пунктир замість решти абонентів
    f.append(line(460, 190, 540, 210, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(550, 215, "• • •  до 64 абонентів", size=10, bold=True, color=MUTED))

    # Абонент N
    f.append(line(460, 230, 620, 270, color=FIBER_CORE, sw=2))
    f.append(rect(620, 245, 180, 50, fill="#e8f8f5", stroke=DOWNSTREAM, sw=1.2, rx=6))
    f.append(text(710, 265, "ONU N (Квартира 64)", size=11, bold=True, color=DOWNSTREAM))
    f.append(text(710, 282, "Часовий слот TN (Upstream)", size=9, color=UPSTREAM))

    # Нижнє пояснення
    f.append(fitbox(20, 350, 780, 50,
                    "Вхідне світло від OLT розщеплюється пасивним призматичним/планарним сплітером без електрики.\n"
                    "Downstream мовить на всі ONU безперервно, Upstream передається пакетами спалахів (Burst Mode) у виділених слотах.",
                    size=10.5, fill="#fcfcfd", stroke=INK))

    render(os.path.join(IMG, "pon-architecture.svg"), W, H, *f)


# ── 2. DWDM Мультиплексування у магістральних мережах ────────────────────────
def fig_dwdm_spectrum_mux():
    W, H = 820, 420
    f = [text(W / 2, 26, "Спектральне мультиплексування DWDM: MUX, оптичний підсилювач EDFA та DEMUX", size=15, bold=True)]

    # Передавачі хвиль (Transmitters Lambda 1..4)
    lambdas = [
        ("λ1 = 1550.12 нм", LASER_RED, 70),
        ("λ2 = 1550.92 нм", DOWNSTREAM, 125),
        ("λ3 = 1551.72 нм", FIBER_CORE, 180),
        ("λ4 = 1552.52 нм", AMPLIFIER, 235),
    ]

    for label, col, y_pos in lambdas:
        f.append(rect(20, y_pos, 140, 38, fill="#fcfcfd", stroke=col, sw=1.5, rx=5))
        f.append(text(90, y_pos + 23, label, size=10.5, bold=True, color=col))
        f.append(arrow(160, y_pos + 19, 230, y_pos + 19, color=col, sw=2))

    # MUX (AWG / Thin Film Filter)
    f.append(rect(230, 60, 90, 225, fill="#ebf5fb", stroke=FIBER_CORE, sw=1.8, rx=8))
    f.append(mtext(275, 145, "DWDM\nMUX\n(AWG)", size=13, bold=True, color=FIBER_CORE))
    f.append(text(275, 235, "Сітка ITU\n100 ГГц", size=10, color=MUTED))

    # Мультиплексований промінь у магістраль
    f.append(line(320, 172, 420, 172, color=LASER_RED, sw=4))
    f.append(text(370, 158, "Мультиплексна хвиля (40..96 хвиль)", size=9.5, bold=True, color=LASER_RED))

    # Оптичний підсилювач EDFA
    f.append(rect(420, 137, 90, 70, fill="#f3e5f5", stroke=AMPLIFIER, sw=1.8, rx=6))
    f.append(mtext(465, 165, "EDFA\nПідсилювач", size=11, bold=True, color=AMPLIFIER))
    f.append(text(465, 195, "+20 dBm", size=9.5, bold=True, color=POS))

    # Лінія зв'язку після підсилювача
    f.append(line(510, 172, 600, 172, color=LASER_RED, sw=4))
    f.append(text(555, 158, "Одномод > 80 км", size=9.5, italic=True, color=MUTED))

    # DEMUX на приймальній стороні
    f.append(rect(600, 60, 90, 225, fill="#ebf5fb", stroke=FIBER_CORE, sw=1.8, rx=8))
    f.append(mtext(645, 145, "DWDM\nDEMUX", size=13, bold=True, color=FIBER_CORE))

    # Розділені промені на приймачі
    for label, col, y_pos in lambdas:
        f.append(arrow(690, y_pos + 19, 740, y_pos + 19, color=col, sw=2))
        f.append(circle(755, y_pos + 19, 10, fill=FILL, stroke=col, sw=1.5))
        f.append(text(755, y_pos + 23, "RX", size=9, bold=True, color=col))

    # Спектральна діаграма внизу
    f.append(rect(20, 300, 780, 55, fill="#fafafa", stroke=MUTED, sw=1, rx=6))
    f.append(text(410, 318, "Спектральний C-діапазон (1530 – 1565 нм) з відстанню 0.8 нм між каналами", size=11, bold=True, color=INK))
    
    # Спектральні піки
    x_start = 220
    for i, (_, col, _) in enumerate(lambdas):
        xp = x_start + i * 110
        f.append(line(xp, 345, xp, 325, color=col, sw=2.5))
        f.append(circle(xp, 325, 3, fill=col, stroke=col))
        f.append(text(xp, 352, "ch %d" % (i + 1), size=9, color=col))

    # Пояснення на самій картці
    f.append(fitbox(20, 365, 780, 45,
                    "Завдяки спектральному мультиплексуванню десяткам лазерів із різною довжиною хвилі не потрібні окремі кабелі:\n"
                    "вони об'єднуються в єдину скляну нитку, підсилюються одним EDFA і розділяються на протилежному боці.",
                    size=10, fill="#fcfcfd", stroke=INK))

    render(os.path.join(IMG, "dwdm-spectrum-mux.svg"), W, H, *f)


# ── 3. Порівняння роз'ємів UPC та APC: Зворотне відбиття ORL ───────────────
def fig_connector_types_orl():
    W, H = 820, 400
    f = [text(W / 2, 26, "Оптичні роз'єми UPC (0°) проти APC (8°): механизм пригнічення відбиття ORL", size=15, bold=True)]

    # Ліва секція: UPC (Ultra Physical Contact, 0°)
    f.append(rect(20, 50, 370, 280, fill="#fcfcfd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(205, 75, "Роз'єм UPC (Синій, плоский зріз 0°)", size=13, bold=True, color=NEG))

    # Волокно UPC
    f.append(rect(50, 130, 140, 40, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=2))
    f.append(line(50, 150, 190, 150, color=FIBER_CORE, sw=5)) # Ядро
    f.append(line(190, 130, 190, 170, color=NEG, sw=3)) # Плоский торцевий зріз 0°

    # Друге волокно в роз'ємі
    f.append(rect(200, 130, 140, 40, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=2))
    f.append(line(200, 150, 340, 150, color=FIBER_CORE, sw=5))
    f.append(line(200, 130, 200, 170, color=NEG, sw=3))

    # Прямий промінь та відбитий назад
    f.append(arrow(80, 150, 185, 150, color=POS, sw=2))
    f.append(text(130, 140, "Падаюче світло", size=9.5, bold=True, color=POS))
    f.append(arrow(185, 150, 90, 150, color=NEG, sw=2))
    f.append(text(130, 168, "Відбиття назад (-45 дБ)", size=9.5, bold=True, color=NEG))

    f.append(text(205, 210, "Відбитий сигнал повертається", size=11, bold=True, color=NEG))
    f.append(text(205, 228, "прямо в лазерний передавач!", size=11, bold=True, color=NEG))
    f.append(text(205, 260, "Загасання відбиття (ORL): ~45..50 дБ", size=10, color=INK))
    f.append(text(205, 280, "Сфера: Ethernet, LAN, дата-центри", size=10, italic=True, color=MUTED))

    # Права секція: APC (Angled Physical Contact, 8°)
    f.append(rect(410, 50, 370, 280, fill="#fcfcfd", stroke=DOWNSTREAM, sw=1.5, rx=8))
    f.append(text(595, 75, "Роз'єм APC (Зелений, косий зріз 8°)", size=13, bold=True, color=DOWNSTREAM))

    # Волокно APC
    f.append(rect(440, 130, 140, 40, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=2))
    f.append(line(440, 150, 580, 150, color=FIBER_CORE, sw=5)) # Ядро
    # Скошений зріз 8° (лінія під кутом)
    f.append(line(575, 128, 585, 172, color=DOWNSTREAM, sw=3))

    # Друге волокно APC
    f.append(rect(590, 130, 140, 40, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=2))
    f.append(line(590, 150, 730, 150, color=FIBER_CORE, sw=5))
    f.append(line(585, 128, 595, 172, color=DOWNSTREAM, sw=3))

    # Промінь падаючий та відбитий в ОБОЛОНКУ
    f.append(arrow(470, 150, 575, 150, color=POS, sw=2))
    f.append(arrow(578, 150, 510, 122, color=DOWNSTREAM, sw=2)) # Відбиття вгору в оболонку
    f.append(text(515, 115, "Відбиття згасає в оболонці!", size=9.5, bold=True, color=DOWNSTREAM))

    f.append(text(595, 210, "Світло відбивається під кутом 16°", size=11, bold=True, color=DOWNSTREAM))
    f.append(text(595, 228, "і розсіюється в оболонці волокна", size=11, bold=True, color=DOWNSTREAM))
    f.append(text(595, 260, "Загасання відбиття (ORL): ≥ 60..70 дБ", size=10, bold=True, color=DOWNSTREAM))
    f.append(text(595, 280, "Сфера: PON, CATV, DWDM магістралі", size=10, italic=True, color=MUTED))

    # Нижня підсумкова картка
    f.append(fitbox(20, 345, 760, 45,
                    "У мережах PON та DWDM косий зріз APC є обов'язковим: він не дає потужному паразитному відбиттю\n"
                    "повертатися в лазер OLT і спотворювати вимірювання рефлектометра OTDR.",
                    size=10.5, fill="#fcfcfd", stroke=INK))

    render(os.path.join(IMG, "connector-types-orl.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pon_architecture()
    fig_dwdm_spectrum_mux()
    fig_connector_types_orl()
    print("Фігури успішно згенеровано у ./img/")
