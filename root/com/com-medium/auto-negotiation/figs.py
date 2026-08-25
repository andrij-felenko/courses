# -*- coding: utf-8 -*-
"""Генератор фігур SVG для теми «Автопогодження Ethernet: протокол, сторінки та арбітраж»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_flp_burst_timing():
    """Фігура 1: Порівняння імпульсів NLP (10BASE-T) та пачки FLP (Auto-Negotiation)."""
    w, h = 820, 380
    frags = []

    # Заголовок / шапка
    frags.append(fitbox(20, 15, 780, 42, "Часова структура імпульсів NLP (10BASE-T) та пачки FLP (Clause 28)", size=15, bold=True, fill="#eef2f7"))

    # Секція 1: NLP 10BASE-T
    frags.append(fitbox(20, 68, 780, 115, "", fill="#ffffff", stroke="#cbd5e1"))
    frags.append(text(35, 92, "10BASE-T: Одиночний імпульс цілісності лінка (NLP)", size=13, bold=True, color=INK, anchor="start"))
    
    # Часова вісь NLP
    frags.append(line(50, 135, 750, 135, color=LINE, sw=1.5))
    frags.append(arrow(750, 135, 770, 135, color=LINE, sw=1.5))
    frags.append(text(765, 155, "t", size=13, italic=True, bold=True))

    # Імпульс 1 на t=100
    frags.append(line(100, 135, 100, 105, color=POS, sw=2.5))
    frags.append(line(100, 105, 108, 105, color=POS, sw=2.5))
    frags.append(line(108, 105, 108, 135, color=POS, sw=2.5))
    frags.append(text(104, 98, "100 нс", size=10, color=POS, anchor="middle"))

    # Імпульс 2 на t=580
    frags.append(line(580, 135, 580, 105, color=POS, sw=2.5))
    frags.append(line(580, 105, 588, 105, color=POS, sw=2.5))
    frags.append(line(588, 105, 588, 135, color=POS, sw=2.5))

    # Стрілка інтервалу 16 мс
    frags.append(line(108, 150, 580, 150, color=MUTED, sw=1.2, dash="4,3"))
    frags.append(text(344, 168, "Інтервал тиші: 16 ± 8 мс між імпульсами NLP", size=11, color=MUTED, anchor="middle"))

    # Секція 2: FLP пачка
    frags.append(fitbox(20, 195, 780, 165, "", fill="#ffffff", stroke="#cbd5e1"))
    frags.append(text(35, 218, "Auto-Negotiation: Пачка швидких імпульсів лінка (FLP Burst = 16 бітів даних)", size=13, bold=True, color=INK, anchor="start"))

    # Збільшена пачка FLP (від t=65 до t=425)
    frags.append(rect(65, 235, 360, 55, fill="#f8fafc", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(245, 252, "Пачка FLP (тривалість ≈ 2.125 мкс, 17 тактових + до 16 інформаційних)", size=11, bold=True, color=NEG, anchor="middle"))

    # Часова вісь FLP
    frags.append(line(50, 310, 750, 310, color=LINE, sw=1.5))
    frags.append(arrow(750, 310, 770, 310, color=LINE, sw=1.5))
    frags.append(text(765, 330, "t", size=13, italic=True, bold=True))

    # Позначення окремих імпульсів всередині пачки
    xs = [80, 110, 140, 170, 200, 230, 260, 290, 320, 350, 380, 410]
    for idx, x in enumerate(xs):
        # Тактовий імпульс
        frags.append(line(x, 308, x, 280, color=POS, sw=2))
        # Імпульс даних (через один)
        if idx % 2 == 1 and idx < 10:
            frags.append(line(x + 15, 308, x + 15, 288, color=FIELD, sw=1.8, dash="2,1"))

    frags.append(text(125, 335, "T_clk = 125 мкс", size=10, color=POS, anchor="middle"))
    frags.append(text(215, 335, "T_data = 62.5 мкс", size=10, color=FIELD, anchor="middle"))

    # Наступна пачка через 16 мс
    frags.append(rect(600, 235, 120, 55, fill="#f8fafc", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(660, 268, "Наступна FLP", size=11, color=NEG, anchor="middle"))

    frags.append(line(425, 262, 600, 262, color=MUTED, sw=1.2, dash="4,3"))
    frags.append(text(512, 255, "Пауза 16 ± 8 мс", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, "flp-burst-timing.svg"), w, h, *frags)


def fig_base_page_format():
    """Фігура 2: Структура 16-розрядної базової сторінки Base Page (IEEE 802.3 Clause 28)."""
    w, h = 820, 370
    frags = []

    frags.append(fitbox(20, 15, 780, 42, "Структура 16-бітного слова базової сторінки (Base Page, Clause 28)", size=15, bold=True, fill="#eef2f7"))

    # Сітка з 16 бітів (D0..D15)
    bit_w = 48.0
    start_x = 26.0

    fields = [
        ("D0..D4", "Selector Field\nS[4:0] = 00001 (802.3)", 5 * bit_w, "#e0f2fe", NEG),
        ("D5..D12", "Technology Ability Field A[7:0]\n10/100M, Duplex, PAUSE, ENP", 8 * bit_w, "#fef3c7", "#b45309"),
        ("D13", "RF\nRemote Fault", bit_w, "#fee2e2", POS),
        ("D14", "ACK\nAcknowledge", bit_w, "#dcfce7", FIELD),
        ("D15", "NP\nNext Page", bit_w, "#f3e8ff", "#7e22ce"),
    ]

    cur_x = start_x
    for name, desc, width, fill_c, text_c in fields:
        frags.append(rect(cur_x, 70, width, 45, fill=fill_c, stroke=text_c, sw=1.5, rx=4))
        frags.append(text(cur_x + width / 2, 98, name, size=13, bold=True, color=text_c, anchor="middle"))
        cur_x += width

    # Поодинокі біти D0..D15
    for i in range(16):
        bx = start_x + i * bit_w
        frags.append(rect(bx, 120, bit_w, 32, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=2))
        frags.append(text(bx + bit_w / 2, 141, "D%d" % i, size=11, bold=True, color=INK, anchor="middle"))

    # Деталізація полів нижче
    # Блок 1: Selector
    frags.append(fitbox(26, 165, 235, 185, 
        "S[4:0] — Поле селектора:\n"
        "• 00001 = IEEE 802.3 Ethernet\n"
        "• 00010 = IEEE 802.9 ISLAN-16T\n"
        "• 00100 = IEEE 802.5 Token Ring\n"
        "• 00101 = IEEE 802.3 Annex 28F\n"
        "Усі сучасні Ethernet-чипи\n"
        "передають строго 00001b.",
        size=11, fill="#f0f9ff", stroke=NEG))

    # Блок 2: Technology Ability
    frags.append(fitbox(271, 165, 375, 185,
        "A[7:0] — Технологічні можливості:\n"
        "• D5 (A0): 10BASE-T Half-Duplex\n"
        "• D6 (A1): 10BASE-T Full-Duplex\n"
        "• D7 (A2): 100BASE-TX Half-Duplex\n"
        "• D8 (A3): 100BASE-TX Full-Duplex\n"
        "• D9 (A4): 100BASE-T4 (4 пари Cat3)\n"
        "• D10 (A5): Симетричний PAUSE (802.3x)\n"
        "• D11 (A6): Асиметричний PAUSE\n"
        "• D12 (A7): Extended Next Page (10GBASE-T)",
        size=11, fill="#fffbeb", stroke="#b45309"))

    # Блок 3: Керуючі біти
    frags.append(fitbox(656, 165, 138, 185,
        "Керуючі біти:\n\n"
        "• RF (D13):\n"
        "  Помилка на\n"
        "  віддаленому кінці\n\n"
        "• ACK (D14):\n"
        "  Успішний прийом\n"
        "  3 однакових слів\n\n"
        "• NP (D15):\n"
        "  Запит обміну\n"
        "  Next Page",
        size=11, fill="#faf5ff", stroke="#7e22ce"))

    render(os.path.join(IMG_DIR, "base-page-format.svg"), w, h, *frags)


def fig_master_slave_resolution():
    """Фігура 3: Дерево прийняття рішень Master/Slave для 1000BASE-T (Clause 40)."""
    w, h = 820, 390
    frags = []

    frags.append(fitbox(20, 12, 780, 40, "Алгоритм арбітражу тактування Master/Slave у 1000BASE-T (Clause 40)", size=15, bold=True, fill="#eef2f7"))

    # Рівень 1: Ручне налаштування
    frags.append(fitbox(240, 60, 340, 48, "Чи встановлено ручний вибір\n(Manual Master / Manual Slave у Reg 9)?", size=11, bold=True, fill="#ffffff", stroke=LINE))
    
    # Гілка ТАК -> вліво
    frags.append(arrow(240, 84, 140, 84, color=LINE))
    frags.append(text(185, 76, "ТАК", size=10, bold=True, color=POS))
    
    frags.append(fitbox(20, 60, 120, 72, "Обидва примусово\nоднакові?\n(Master-Master чи\nSlave-Slave)", size=10, fill="#fee2e2", stroke=POS))
    
    frags.append(arrow(80, 132, 80, 160, color=POS))
    frags.append(text(95, 146, "ТАК", size=10, bold=True, color=POS))
    frags.append(fitbox(20, 160, 120, 46, "CONFIG FAULT!\nЛінк не підніметься\n(Reg 10.15 = 1)", size=10, bold=True, fill="#fee2e2", stroke=POS))

    frags.append(arrow(140, 110, 170, 110, color=FIELD))
    frags.append(text(155, 102, "НІ", size=10, bold=True, color=FIELD))
    frags.append(fitbox(170, 95, 125, 45, "Ручне призначення:\nодин Master,\nдругий Slave", size=10, fill="#dcfce7", stroke=FIELD))

    # Гілка НІ -> вниз до Рівня 2 (Тип пристрою)
    frags.append(arrow(410, 108, 410, 138, color=LINE))
    frags.append(text(425, 124, "НІ", size=10, bold=True, color=FIELD))

    # Рівень 2: Тип пристрою (Multiport vs Single-port)
    frags.append(fitbox(260, 138, 300, 48, "Порівняння типів портів:\nMultiport (комутатор) проти Single-port (NIC)?", size=11, bold=True, fill="#ffffff", stroke=LINE))

    # Гілка ТАК (різні типи) -> вправо
    frags.append(arrow(560, 162, 640, 162, color=LINE))
    frags.append(text(595, 154, "Різні", size=10, bold=True, color=FIELD))
    frags.append(fitbox(640, 138, 160, 52, "Multiport стає MASTER\nSingle-port стає SLAVE\n(стабільність тактування)", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    # Гілка НІ (однакові типи) -> вниз до Рівня 3 (Seed)
    frags.append(arrow(410, 186, 410, 218, color=LINE))
    frags.append(text(435, 202, "Однакові", size=10, bold=True, color=MUTED))

    # Рівень 3: Випадкове число Seed (11 бітів)
    frags.append(fitbox(250, 218, 320, 52, "Генерація 11-бітного псевдовипадкового Seed\n(Next Page Unformatted D0..D10):\nПорівняння Seed_local проти Seed_remote", size=11, bold=True, fill="#ffffff", stroke=LINE))

    # Гілка Seed1 > Seed2
    frags.append(arrow(250, 244, 150, 244, color=LINE))
    frags.append(arrow(150, 244, 150, 295, color=LINE))
    frags.append(text(195, 236, "Seed_A > Seed_B", size=10, bold=True, color=FIELD))
    frags.append(fitbox(60, 295, 180, 55, "Вузол А стає MASTER\nВузол B стає SLAVE\n(розв'язання успішне)", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    # Гілка Seed1 == Seed2 (колізія seed)
    frags.append(arrow(570, 244, 680, 244, color=LINE))
    frags.append(arrow(680, 244, 680, 295, color=LINE))
    frags.append(text(620, 236, "Seed_A == Seed_B", size=10, bold=True, color=POS))
    frags.append(fitbox(590, 295, 180, 55, "Колізія випадкових чисел!\n(ймовірність 1/2048)\nПерегенерація Seed і рестарт", size=10, fill="#fee2e2", stroke=POS))

    frags.append(fitbox(260, 310, 300, 48, "Результат записується в регістр MII 10:\n• Біт 10.14: Master/Slave Resolution Result\n• Біт 10.15: Master/Slave Configuration Fault", size=10, fill="#f1f5f9", stroke="#64748b"))

    render(os.path.join(IMG_DIR, "master-slave-resolution.svg"), w, h, *frags)


def fig_duplex_mismatch_late_collision():
    """Фігура 4: Механізм виникнення Late Collision при Duplex Mismatch."""
    w, h = 820, 380
    frags = []

    frags.append(fitbox(20, 12, 780, 40, "Анатомія Duplex Mismatch: виникнення пізніх колізій (Late Collisions)", size=15, bold=True, fill="#eef2f7"))

    # Колонка 1: Комутатор (Full-Duplex)
    frags.append(fitbox(40, 62, 210, 52, "Комутатор (Switch)\nФіксований: 100M Full-Duplex\n(CSMA/CD вимкнено)", size=11, bold=True, fill="#e0f2fe", stroke=NEG))

    # Колонка 2: Кабель
    frags.append(fitbox(300, 62, 220, 52, "Кабель Cat5e (100 м)\nParallel Detection обрав:\n100M Half-Duplex для ПК", size=11, fill="#f8fafc", stroke=LINE))

    # Колонка 3: Клієнт (Half-Duplex)
    frags.append(fitbox(570, 62, 210, 52, "Клієнтський ПК (Host)\nAuto-Neg -> Half-Duplex\n(CSMA/CD активний!)", size=11, bold=True, fill="#fef3c7", stroke="#b45309"))

    # Часова шкала передачі кадру (розриваємо лінії навколо блоків повідомлень)
    frags.append(line(145, 125, 145, 330, color=NEG, sw=1.5, dash="4,4"))
    
    # Права вертикальна лінія для ПК (йде від 125 до 240, не перетинаючи прямокутник результату знизу)
    frags.append(line(675, 125, 675, 235, color="#b45309", sw=1.5, dash="4,4"))

    # Подія 1: ПК починає передачу довгого кадру (t=0)
    frags.append(text(665, 145, "1. ПК слухає лінію (вільно) і починає передачу", size=10, color=INK, anchor="end"))
    frags.append(arrow(665, 155, 300, 190, color="#b45309", sw=2))
    frags.append(text(485, 165, "Кадр даних (1500 байтів)", size=10, bold=True, color="#b45309", anchor="middle"))

    # Подія 2: Передано понад 64 байти (512 бітів — Slot Time вичерпано)
    frags.append(line(240, 200, 650, 200, color=MUTED, sw=1.2, dash="2,2"))
    frags.append(text(655, 204, "512 бітів (Slot Time)", size=10, color=MUTED, anchor="start"))

    # Подія 3: Комутатор відправляє свій кадр (t=пізніше)
    frags.append(text(145, 218, "2. Комутатор має Full-Duplex:", size=10, color=NEG, anchor="start"))
    frags.append(text(145, 232, "передає без очікування!", size=10, color=NEG, anchor="start"))
    frags.append(arrow(145, 240, 440, 268, color=NEG, sw=2))

    # Подія 4: Точка зіткнення / колізії на приймачі ПК
    frags.append(circle(455, 270, 12, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(455, 274, "💥", size=12, anchor="middle"))
    
    # Блок результату колізії розташовуємо так, щоб жодна лінія не проходила крізь нього
    frags.append(fitbox(480, 245, 300, 75,
        "3. КОЛІЗІЯ ПІСЛЯ 64 БАЙТІВ!\n"
        "• ПК фіксує Late Collision\n"
        "• Апаратний повтор CSMA/CD скасовано\n"
        "• Кадр відкидається назавжди\n"
        "• TCP падає в Retransmit Timeout",
        size=10, bold=True, fill="#fee2e2", stroke=POS))

    # Підсумок знизу
    frags.append(fitbox(40, 332, 740, 38,
        "Наслідок: пінг (< 64 байти) проходить ідеально, а передача файлів (MTU 1500) втрачає до 90% пакетів.",
        size=11, fill="#fff1f2", stroke=POS))

    render(os.path.join(IMG_DIR, "duplex-mismatch-late-collision.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_flp_burst_timing()
    fig_base_page_format()
    fig_master_slave_resolution()
    fig_duplex_mismatch_late_collision()
    print("Всі фігури успішно згенеровано.")
