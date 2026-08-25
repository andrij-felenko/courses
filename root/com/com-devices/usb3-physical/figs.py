# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми usb3-physical."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_dual_bus_topology():
    """Фігура 1: Архітектура подвійної шини USB 3.x (Dual-Bus Architecture)."""
    w, h = 860, 430
    body = []

    # Заголовок / фонові блоки хоста і пристрою
    body.append(fitbox(20, 20, 240, 390, "Хост (Host / DFP)\nUSB 3.x Controller", size=15, bold=True, fill="#f8fafc", stroke=LINE))
    body.append(fitbox(600, 20, 240, 390, "Пристрій (Device / UFP)\nSuperSpeed Peripheral", size=15, bold=True, fill="#f8fafc", stroke=LINE))

    # Внутрішні контролери Хоста
    body.append(fitbox(35, 75, 210, 80, "USB 2.0 PHY\n(Half-Duplex Engine)\n480 Мбіт/с", size=12, fill="#fff7ed", stroke="#ea580c"))
    body.append(fitbox(35, 185, 210, 210, "SuperSpeed PHY (SerDes)\n5 / 10 / 20 Гбіт/с\n(Full-Duplex Dual-Simplex)", size=12, fill="#eff6ff", stroke=NEG))

    # Внутрішні контролери Пристрою
    body.append(fitbox(615, 75, 210, 80, "USB 2.0 PHY\n(Half-Duplex Engine)\n480 Мбіт/с", size=12, fill="#fff7ed", stroke="#ea580c"))
    body.append(fitbox(615, 185, 210, 210, "SuperSpeed PHY (SerDes)\n5 / 10 / 20 Гбіт/с\n(Full-Duplex Dual-Simplex)", size=12, fill="#eff6ff", stroke=NEG))

    # Кабельний простір посередині
    body.append(rect(285, 45, 290, 350, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    body.append(text(430, 65, "Кабель USB 3.x (Dual-Bus)", size=13, bold=True, color="#475569"))

    # Лінія USB 2.0 (D+ / D-)
    body.append(line(245, 105, 615, 105, color="#ea580c", sw=2))
    body.append(line(245, 125, 615, 125, color="#c2410c", sw=2))
    body.append(fitbox(330, 95, 200, 45, "USB 2.0: D+ / D− (90 Ом)\nНапівдуплекс (спільна пара)", size=11, fill="#ffedd5", stroke="#ea580c"))

    # SuperSpeed TX лінія (Хост -> Пристрій)
    # AC-конденсатори на боці передавача
    body.append(line(245, 230, 320, 230, color=NEG, sw=2))
    body.append(line(245, 255, 320, 255, color=NEG, sw=2))

    # Конденсатори C_TX
    body.append(rect(320, 222, 28, 16, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
    body.append(text(334, 234, "C_ac", size=9, bold=True, color=NEG))
    body.append(rect(320, 247, 28, 16, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
    body.append(text(334, 259, "C_ac", size=9, bold=True, color=NEG))

    body.append(arrow(348, 230, 615, 230, color=NEG, sw=2))
    body.append(arrow(348, 255, 615, 255, color=NEG, sw=2))
    body.append(fitbox(380, 218, 195, 45, "SSTX+ / SSTX− (TX пара)\nAC-розв'язка 100 нФ, 90 Ом", size=11, fill="#e0f2fe", stroke=NEG))

    # SuperSpeed RX лінія (Пристрій -> Хост)
    # AC-конденсатори на боці пристрою (TX пристрою)
    body.append(arrow(512, 330, 245, 330, color=POS, sw=2))
    body.append(arrow(512, 355, 245, 355, color=POS, sw=2))

    body.append(rect(512, 322, 28, 16, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    body.append(text(526, 334, "C_ac", size=9, bold=True, color=POS))
    body.append(rect(512, 347, 28, 16, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    body.append(text(526, 359, "C_ac", size=9, bold=True, color=POS))

    body.append(line(615, 330, 540, 330, color=POS, sw=2))
    body.append(line(615, 355, 540, 355, color=POS, sw=2))
    body.append(fitbox(300, 318, 195, 45, "SSRX+ / SSRX− (RX пара)\nAC-розв'язка 100 нФ, 90 Ом", size=11, fill="#ffe4e6", stroke=POS))

    # Земляний екран (GND_DRAIN)
    body.append(line(245, 385, 615, 385, color="#64748b", sw=1.5, dash="4,4"))
    body.append(text(430, 380, "GND_DRAIN (індивідуальний екран)", size=10, color="#64748b"))

    render(os.path.join(IMG_DIR, "dual-bus-topology.svg"), w, h, "".join(body))


def fig_receiver_detection_rc():
    """Фігура 2: Схема та графіки виявлення приймача (Receiver Detection)."""
    w, h = 860, 390
    body = []

    # Ліва частина: Електрична схема виявлення
    body.append(rect(15, 15, 410, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    body.append(text(220, 42, "Еквівалентна схема Rx Detect", size=14, bold=True, color=INK))

    # Передавач (Host TX)
    body.append(rect(30, 65, 140, 290, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    body.append(text(100, 90, "Передавач (TX)", size=12, bold=True, color=NEG))
    body.append(fitbox(40, 110, 120, 45, "Генератор кроку\nV_step = 0.5 В", size=11, fill="#ffffff", stroke=NEG))
    body.append(fitbox(40, 180, 120, 40, "R_tx = 45 Ом\n(Джерело)", size=11, fill="#ffffff", stroke=NEG))
    body.append(fitbox(40, 245, 120, 50, "Компаратор\nСтроб t_strobe\nПоріг V_th", size=11, fill="#ffffff", stroke="#7c3aed"))

    # AC Конденсатор
    body.append(line(170, 130, 215, 130, color=LINE, sw=2))
    body.append(rect(215, 115, 35, 30, fill="#dbeafe", stroke=NEG, sw=1.5, rx=3))
    body.append(text(232, 134, "C_ac", size=11, bold=True, color=NEG))
    body.append(text(232, 160, "100 нФ", size=10, color=MUTED))

    # Вузол вимірювання до компаратора
    body.append(line(190, 130, 190, 270, color="#7c3aed", sw=1.8, dash="3,3"))
    body.append(arrow(190, 270, 160, 270, color="#7c3aed", sw=1.8))
    body.append(circle(190, 130, 4, fill="#7c3aed", stroke=LINE))
    body.append(text(190, 120, "V(t)", size=11, bold=True, color="#7c3aed"))

    # Роз'єм / лінія
    body.append(line(250, 130, 295, 130, color=LINE, sw=2))
    body.append(line(295, 110, 295, 150, color="#94a3b8", sw=1.5, dash="2,2"))
    body.append(text(295, 100, "Роз'єм", size=10, color=MUTED))

    # Приймач (Device RX)
    body.append(rect(310, 65, 100, 290, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    body.append(text(360, 90, "Приймач (RX)", size=12, bold=True, color=FIELD))
    body.append(fitbox(320, 115, 80, 55, "R_rx_term\n45 Ом\nдо GND", size=11, fill="#ffffff", stroke=FIELD))
    body.append(line(360, 170, 360, 220, color=LINE, sw=2))
    # GND символ
    body.append(line(345, 220, 375, 220, color=LINE, sw=2))
    body.append(line(350, 225, 370, 225, color=LINE, sw=1.5))
    body.append(line(355, 230, 365, 230, color=LINE, sw=1))

    # Права частина: Графік напруги V(t)
    body.append(rect(440, 15, 405, 360, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    body.append(text(642, 42, "Криві заряду на вузлі V(t)", size=14, bold=True, color=INK))

    # Осі графіка
    body.append(arrow(480, 320, 810, 320, color=LINE, sw=1.8))
    body.append(arrow(480, 320, 480, 75, color=LINE, sw=1.8))
    body.append(text(810, 338, "t", size=13, bold=True, color=INK))
    body.append(text(465, 80, "V", size=13, bold=True, color=INK))

    # Рівні V_step та V_th
    body.append(line(475, 110, 790, 110, color=MUTED, sw=1, dash="4,4"))
    body.append(text(455, 114, "V_step", size=10, color=MUTED))

    body.append(line(475, 200, 790, 200, color="#7c3aed", sw=1.2, dash="4,4"))
    body.append(text(450, 204, "V_porig", size=10, bold=True, color="#7c3aed"))

    # Крива 1: Приймач ВІДСУТНІЙ (миттєвий стрибок через паразитарну ємність 2 пФ)
    body.append(line(480, 320, 490, 115, color=POS, sw=2.5))
    body.append(line(490, 115, 790, 110, color=POS, sw=2.5))
    body.append(fitbox(510, 125, 210, 35, "Відсутній: tau ≈ 90 пс\n(Миттєвий стрибок до V_step)", size=10, fill="#fee2e2", stroke=POS))

    # Крива 2: Приймач ПІДКЛЮЧЕНИЙ (повільний експоненційний заряд RC)
    pts = []
    for x in range(0, 300, 10):
        vx = 480 + x
        vy = 320 - 210 * (1.0 - math.exp(-x / 140.0))
        pts.append(f"{vx:.1f},{vy:.1f}")
    body.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    body.append(fitbox(550, 240, 230, 40, "Підключений: tau = R·C ≈ 9 мкс\n(Повільний плавний заряд)", size=10, fill="#dcfce7", stroke=FIELD))

    # Час стробування t_strobe
    body.append(line(580, 85, 580, 320, color="#7c3aed", sw=1.5, dash="3,3"))
    body.append(circle(580, 212, 4, fill="#7c3aed", stroke=LINE))
    body.append(text(580, 338, "t_strobe", size=11, bold=True, color="#7c3aed"))

    render(os.path.join(IMG_DIR, "receiver-detection-rc.svg"), w, h, "".join(body))


def fig_equalization_eye():
    """Фігура 3: Ланцюг еквалайзингу та відновлення очного патерну."""
    w, h = 860, 410
    body = []

    # 4 етапи обробки сигналу
    # Блок 1: Передавач + De-emphasis
    body.append(fitbox(20, 20, 185, 160, "1. Передавач (TX)\nDe-emphasis (−3.5 дБ)\nОслаблення низьких\nчастот перед лінією", size=11, fill="#eff6ff", stroke=NEG))

    # Блок 2: Втрати в каналі (Channel Loss)
    body.append(fitbox(235, 20, 185, 160, "2. Кабель і доріжки\nSkin-effect + Dielectric\nЗавал ВЧ (−15...−20 дБ)\nМіжсимвольна\nінтерференція (ISI)", size=11, fill="#fee2e2", stroke=POS))

    # Блок 3: Приймач CTLE
    body.append(fitbox(450, 20, 185, 160, "3. Приймач: CTLE\nЛінійний еквалайзер\nАналоговий підйом ВЧ\nна частоті Найквіста\n(2.5 / 5.0 ГГц)", size=11, fill="#fef9c3", stroke="#ca8a04"))

    # Блок 4: Приймач DFE
    body.append(fitbox(660, 20, 185, 160, "4. Приймач: DFE\nЗворотний зв'язок\nНелінійне віднімання\nхвостів ISI без\nпідсилення шумів", size=11, fill="#dcfce7", stroke=FIELD))

    # Стрілки між блоками
    body.append(arrow(205, 100, 235, 100, color=LINE, sw=2))
    body.append(arrow(420, 100, 450, 100, color=LINE, sw=2))
    body.append(arrow(635, 100, 660, 100, color=LINE, sw=2))

    # Нижня частина: Очні діаграми (Eye Diagrams)
    # Зліва: Закрите око після кабелю без корекції
    body.append(rect(60, 200, 320, 190, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    body.append(text(220, 225, "Сигнал після каналу без еквалайзингу", size=12, bold=True, color=POS))

    # Малюємо закрите змазане око
    # Осі
    body.append(line(90, 300, 350, 300, color="#e2e8f0", sw=1))
    # Спотворені траєкторії
    body.append(line(90, 255, 350, 335, color="#fca5a5", sw=1.5))
    body.append(line(90, 335, 350, 255, color="#fca5a5", sw=1.5))
    body.append(line(90, 280, 350, 310, color="#f87171", sw=1.5))
    body.append(line(90, 310, 350, 280, color="#f87171", sw=1.5))
    body.append(line(90, 260, 350, 290, color="#ef4444", sw=1.8))
    body.append(line(90, 330, 350, 305, color="#ef4444", sw=1.8))

    body.append(circle(220, 295, 12, fill="#fee2e2", stroke=POS, sw=1.5))
    body.append(text(220, 299, "X", size=12, bold=True, color=POS))
    body.append(fitbox(90, 345, 260, 35, "Око закрите: 100% помилок\nНеможливо розрізнити 0 і 1", size=10, fill="#fef2f2", stroke=POS))

    # Стрілка відновлення
    body.append(arrow(390, 295, 470, 295, color=FIELD, sw=3))
    body.append(text(430, 280, "CTLE + DFE", size=11, bold=True, color=FIELD))

    # Справа: Відкрите розчищене око після CTLE + DFE
    body.append(rect(480, 200, 320, 190, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    body.append(text(640, 225, "Сигнал після повної корекції (CTLE + DFE)", size=12, bold=True, color=FIELD))

    # Осі
    body.append(line(510, 300, 770, 300, color="#e2e8f0", sw=1))
    # Чіткі траєкторії з широким розкриттям
    body.append(f'<path d="M 510 250 Q 570 250 640 295 Q 710 340 770 340" fill="none" stroke="{FIELD}" stroke-width="2"/>')
    body.append(f'<path d="M 510 340 Q 570 340 640 295 Q 710 250 770 250" fill="none" stroke="{FIELD}" stroke-width="2"/>')
    body.append(f'<path d="M 510 250 L 770 250" fill="none" stroke="{FIELD}" stroke-width="1.8"/>')
    body.append(f'<path d="M 510 340 L 770 340" fill="none" stroke="{FIELD}" stroke-width="1.8"/>')

    # Око відкрите
    body.append(fitbox(590, 275, 100, 40, "Око відкрито\n(Чистий біт)", size=10, bold=True, fill="#dcfce7", stroke=FIELD))
    body.append(fitbox(510, 345, 260, 35, "Запас за часом і напругою\nBER &lt; 10⁻¹²", size=10, fill="#f0fdf4", stroke=FIELD))

    render(os.path.join(IMG_DIR, "equalization-eye.svg"), w, h, "".join(body))


def fig_ssc_spectrum():
    """Фігура 4: Розподіл спектра завад (Spread Spectrum Clocking) та захист Wi-Fi."""
    w, h = 860, 400
    body = []

    # Лівий блок: Модуляція тактової частоти (трикутна SSC)
    body.append(rect(15, 15, 400, 370, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    body.append(text(215, 42, "Частотна модуляція SSC (Down-Spread)", size=13, bold=True, color=INK))

    # Осі
    body.append(arrow(50, 240, 380, 240, color=LINE, sw=1.8))
    body.append(arrow(50, 240, 50, 70, color=LINE, sw=1.8))
    body.append(text(380, 258, "t", size=12, bold=True, color=INK))
    body.append(text(35, 75, "f", size=12, bold=True, color=INK))

    # Рівні частоти: f_nom (5.000 ГГц) та f_min (4.975 ГГц, -0.5%)
    body.append(line(45, 100, 370, 100, color=POS, sw=1.2, dash="4,4"))
    body.append(text(130, 93, "f_nom = 5.000 ГГц (0 ppm)", size=10, color=POS))

    body.append(line(45, 190, 370, 190, color=NEG, sw=1.2, dash="4,4"))
    body.append(text(145, 205, "f_min = 4.975 ГГц (−5000 ppm, −0.5%)", size=10, color=NEG))

    # Трикутна хвиля модуляції
    # Період T_mod = 1 / 31.5 кГц ≈ 31.7 мкс
    body.append(f'<polyline points="50,100 110,190 170,100 230,190 290,100 350,190" fill="none" stroke="#7c3aed" stroke-width="2.5"/>')

    body.append(line(50, 215, 170, 215, color="#7c3aed", sw=1.2))
    body.append(text(110, 230, "T_mod (30–33 кГц)", size=10, bold=True, color="#7c3aed"))

    body.append(fitbox(35, 270, 360, 95, "Параметри модуляції:\n• Форма: симетричний трикутник (Hershey-profile)\n• Швидкість модуляції: 30–33 кГц (поза звуковим діапазоном)\n• Девіація: −5000 ppm (лише вниз, щоб не перевищити ліміт f_max)", size=11, fill="#f8fafc", stroke="#94a3b8"))

    # Правий блок: Спектральна щільність потужності завад (PSD)
    body.append(rect(435, 15, 410, 370, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    body.append(text(640, 42, "Спектр випромінювання та конфлікт 2.4 ГГц", size=13, bold=True, color=INK))

    # Осі спектра
    body.append(arrow(470, 240, 810, 240, color=LINE, sw=1.8))
    body.append(arrow(470, 240, 470, 70, color=LINE, sw=1.8))
    body.append(text(810, 258, "f", size=12, bold=True, color=INK))
    body.append(text(450, 75, "дБм", size=11, bold=True, color=INK))

    # Ліміт FCC/CISPR
    body.append(line(465, 130, 800, 130, color="#dc2626", sw=1.5, dash="4,4"))
    body.append(text(725, 122, "Ліміт завад FCC", size=10, bold=True, color="#dc2626"))

    # Пік 1: БЕЗ SSC (вузький потужний гострий пік завади)
    body.append(line(535, 240, 535, 85, color=POS, sw=3))
    body.append(fitbox(485, 80, 100, 38, "Без SSC:\nгострий пік", size=10, fill="#fee2e2", stroke=POS))

    # Пік 2: З SSC (розмитий плоский спектр нижче ліміту)
    # Трапеція розмиття на осі f
    body.append(f'<polygon points="630,240 645,160 705,160 720,240" fill="#dbeafe" stroke="{NEG}" stroke-width="2"/>')
    body.append(fitbox(625, 175, 100, 48, "З SSC: смуга\n25 МГц\n(−15 дБ)", size=10, fill="#eff6ff", stroke=NEG))

    # Небезпека для Wi-Fi / Bluetooth
    body.append(fitbox(455, 270, 370, 95, "Чому ламається Wi-Fi / Bluetooth (2.4 ГГц):\n• 1-ша гармоніка SuperSpeed (2.5 ГГц) лежить поруч із Wi-Fi 2.4 ГГц\n• Неекранований роз'єм або кабель випромінює завади прямо в антену\n• SSC розмиває пік, але для стабільного радіо потрібен і якісний екран", size=11, fill="#fef2f2", stroke=POS))

    render(os.path.join(IMG_DIR, "ssc-spectrum.svg"), w, h, "".join(body))


if __name__ == "__main__":
    fig_dual_bus_topology()
    fig_receiver_detection_rc()
    fig_equalization_eye()
    fig_ssc_spectrum()
    print("Всі 4 фігури успішно згенеровано.")
