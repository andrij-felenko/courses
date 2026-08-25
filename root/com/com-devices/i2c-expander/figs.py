# -*- coding: utf-8 -*-
"""Генератор схем і діаграм для теми i2c-expander (I²C-розширювач)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_quasi_vs_pushpull():
    """Порівняння квазідвостороннього порту (PCF8574) і повноцінного Push-Pull з IODIR (TCA9555/MCP23017)."""
    w, h = 920, 480
    frags = []

    # Заголовок / розділювач між двома схемами
    frags.append(rect(15, 15, 435, 450, fill="#fcfdfd", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(rect(470, 15, 435, 450, fill="#fcfdfd", stroke="#d0d7de", sw=1.5, rx=8))

    frags.append(text(232, 42, "Квазідвосторонній вихід (PCF8574)", size=15, bold=True, color=INK))
    frags.append(text(687, 42, "Push-Pull з регістром напрямку (TCA/MCP)", size=15, bold=True, color=INK))

    # --- ЛІВА ПАНЕЛЬ: PCF8574 Quasi-bidirectional ---
    # Живлення VDD
    frags.append(line(80, 80, 260, 80, color=POS, sw=2))
    frags.append(text(275, 84, "VDD", size=13, color=POS, bold=True))

    # Слабке джерело струму / підтяжка (~100 мкА)
    frags.append(rect(60, 110, 110, 50, fill="#fff8e6", stroke="#d97706", sw=1.5, rx=4))
    frags.append(mtext(115, 128, ["Слабка підтяжка", "I_OH ≈ 100 мкА"], size=11, color="#92400e", bold=True))
    frags.append(line(115, 80, 115, 110, color=LINE, sw=1.5))
    frags.append(line(115, 160, 115, 230, color=LINE, sw=1.5))

    # Імпульсний підсилювач наростання (Strong Pull-up на 1 такт)
    frags.append(rect(190, 110, 115, 50, fill="#eef2ff", stroke="#4f46e5", sw=1.5, rx=4))
    frags.append(mtext(247, 128, ["Імпульсний розгін", "Strong pull-up 30нс"], size=11, color="#3730a3", bold=True))
    frags.append(line(247, 80, 247, 110, color=LINE, sw=1.5))
    frags.append(line(247, 160, 247, 230, color=LINE, sw=1.5))

    # Спільний вузол виходу
    frags.append(line(115, 230, 370, 230, color=LINE, sw=2))
    frags.append(circle(200, 230, 4, fill=INK, stroke=INK))
    frags.append(circle(370, 230, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(405, 235, "Пін P[n]", size=13, bold=True, color=INK))

    # NMOS відкритий стік униз
    frags.append(line(200, 230, 200, 270, color=LINE, sw=1.5))
    frags.append(rect(160, 270, 80, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(mtext(200, 287, ["NMOS ключовий", "I_sink ≤ 25 мА"], size=11, color=POS, bold=True))
    frags.append(line(200, 310, 200, 340, color=LINE, sw=1.5))
    frags.append(line(180, 340, 220, 340, color=LINE, sw=2))
    frags.append(line(188, 344, 212, 344, color=LINE, sw=1.5))
    frags.append(line(194, 348, 206, 348, color=LINE, sw=1))
    frags.append(text(235, 345, "GND", size=11, color=MUTED))

    # Вхідний буфер зчитування
    frags.append(line(320, 230, 320, 380, color=LINE, sw=1.5))
    frags.append(arrow(320, 380, 260, 380, color=FIELD, sw=1.5))
    frags.append(rect(140, 360, 115, 40, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(mtext(197, 377, ["Вхідний буфер", "Шмітта / засувка"], size=11, color="#166534", bold=True))
    frags.append(arrow(140, 380, 60, 380, color=FIELD, sw=1.5))
    frags.append(text(50, 384, "До I2C", size=11, color=FIELD, anchor="end", bold=True))

    # Коментар особливості
    frags.append(rect(30, 420, 405, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(232, 441, "Для входу в порт пишуть «1»: пін підтягується струмом 100 мкА", size=11, color=MUTED))

    # --- ПРАВА ПАНЕЛЬ: TCA9555/MCP23017 True Tri-state Push-Pull ---
    # Регістр напрямку IODIR
    frags.append(rect(490, 90, 120, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(mtext(550, 110, ["Регістр IODIR", "0=Output, 1=Input"], size=11, color="#92400e", bold=True))

    # Регістр виходу Output Latch (OLAT)
    frags.append(rect(490, 170, 120, 50, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=4))
    frags.append(mtext(550, 190, ["Вихідна засувка", "Output Port (OLAT)"], size=11, color="#3730a3", bold=True))

    # Драйвер Push-Pull (PMOS + NMOS)
    frags.append(rect(660, 120, 110, 120, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(715, 140, "Push-Pull Driver", size=11, bold=True, color="#334155"))
    frags.append(text(715, 165, "PMOS (Active High)", size=10, color=POS))
    frags.append(text(715, 185, "NMOS (Active Low)", size=10, color=NEG))
    frags.append(text(715, 215, "Tri-State (High-Z)", size=10, bold=True, color="#0f766e"))

    # З'єднання регістрів із драйвером
    frags.append(arrow(610, 115, 660, 145, color="#d97706", sw=1.5))
    frags.append(arrow(610, 195, 660, 195, color="#4338ca", sw=1.5))

    # Вихід до піна
    frags.append(line(770, 180, 835, 180, color=LINE, sw=2))
    frags.append(circle(835, 180, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(855, 185, "Пін GP[n]", size=13, bold=True, color=INK, anchor="start"))

    # Вхідна лінія зчитування через буфер
    frags.append(line(805, 180, 805, 330, color=LINE, sw=1.5))
    frags.append(arrow(805, 330, 755, 330, color=FIELD, sw=1.5))
    frags.append(rect(635, 310, 120, 45, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(mtext(695, 328, ["Вхідний регістр", "Input Port (GPIO)"], size=11, color="#166534", bold=True))
    frags.append(arrow(635, 330, 560, 330, color=FIELD, sw=1.5))
    frags.append(text(550, 334, "До I2C шини", size=11, color=FIELD, anchor="end", bold=True))

    # Програмована підтяжка (GPPU)
    frags.append(rect(635, 375, 120, 35, fill="#fffbeb", stroke="#b45309", sw=1.2, rx=4))
    frags.append(text(695, 397, "Підтяжка GPPU 100кОм", size=10, color="#b45309", bold=True))
    frags.append(line(755, 392, 805, 392, color="#b45309", sw=1.2, dash="3,3"))
    frags.append(line(805, 330, 805, 392, color="#b45309", sw=1.2, dash="3,3"))

    # Коментар особливості
    frags.append(rect(485, 420, 405, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(687, 441, "Повний 3-стабільний буфер: високий струм в обох станах (до 25 мА)", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "quasi-vs-pushpull.svg"), w, h, *frags)


def fig_interrupt_logic():
    """Конвеєр фіксації переривань: порівняння, маска GPINTEN, фіксація в INTCAP і лінія /INT."""
    w, h = 900, 380
    frags = []

    # 1. Фізичний пін
    frags.append(circle(45, 150, 7, fill=POS, stroke=LINE, sw=2))
    frags.append(mtext(45, 180, ["Пін GPIO", "Pin N"], size=12, bold=True, color=INK))
    frags.append(arrow(52, 150, 130, 150, color=LINE, sw=2))

    # 2. Логіка виявлення зміни (Comparator / Edge Detector)
    frags.append(rect(130, 95, 175, 110, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(217, 120, "Детектор події", size=13, bold=True, color="#1e293b"))
    frags.append(text(217, 142, "Порівняння зі станом:", size=11, color=MUTED))
    frags.append(text(217, 162, "• Попередній стан (INTCON=0)", size=10, color="#334155"))
    frags.append(text(217, 182, "• Регістр DEFVAL (INTCON=1)", size=10, color="#334155"))

    frags.append(arrow(305, 150, 370, 150, color=LINE, sw=2))
    frags.append(text(337, 142, "Зміна", size=11, color="#0f766e", bold=True))

    # 3. Маскування переривань (GPINTEN)
    frags.append(rect(370, 115, 120, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(mtext(430, 142, ["Маска GPINTEN", "Дозвіл по бітах"], size=12, color="#92400e", bold=True))

    frags.append(arrow(490, 150, 555, 150, color=LINE, sw=2))

    # 4. Регістри фіксації INTF та INTCAP
    frags.append(rect(555, 80, 160, 140, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=6))
    frags.append(text(635, 105, "Фіксація переривання", size=12, bold=True, color="#3730a3"))
    frags.append(rect(568, 120, 134, 38, fill="#ffffff", stroke="#818cf8", sw=1, rx=4))
    frags.append(mtext(635, 136, ["Прапорець INTF", "Хто викликав"], size=11, color="#312e81", bold=True))
    frags.append(rect(568, 168, 134, 42, fill="#ffffff", stroke="#818cf8", sw=1, rx=4))
    frags.append(mtext(635, 185, ["Знімок INTCAP", "Стан у момент збою"], size=11, color="#312e81", bold=True))

    # 5. Вихідний каскад лінії INT (Open-Drain Active-Low)
    frags.append(arrow(715, 150, 775, 150, color=LINE, sw=2))
    frags.append(rect(775, 115, 100, 70, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(mtext(825, 142, ["Open-Drain", "Вихід /INT"], size=12, color=POS, bold=True))

    # Підтяжка до VDD на лінії переривання
    frags.append(line(825, 115, 825, 60, color=POS, sw=1.5))
    frags.append(rect(810, 30, 30, 30, fill="#fff", stroke=POS, sw=1.5, rx=2))
    frags.append(text(825, 49, "R_pu", size=10, color=POS, bold=True))
    frags.append(line(825, 30, 825, 15, color=POS, sw=1.5))
    frags.append(text(825, 10, "VDD", size=11, color=POS, bold=True))

    # Скидання переривання через I2C
    frags.append(rect(220, 275, 460, 65, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(450, 298, "Скидання переривання (Clear Interrupt)", size=13, bold=True, color="#166534"))
    frags.append(text(450, 322, "Читання регістру INTCAP або GPIO через I2C деактивує лінію /INT", size=11, color="#15803d"))

    # Стрілка скидання
    frags.append(line(450, 275, 450, 230, color=FIELD, sw=1.8, dash="4,4"))
    frags.append(line(450, 230, 635, 230, color=FIELD, sw=1.8, dash="4,4"))
    frags.append(arrow(635, 230, 635, 220, color=FIELD, sw=1.8))

    return render(os.path.join(IMG_DIR, "interrupt-logic.svg"), w, h, *frags)


def fig_transaction_flow():
    """Порівняння послідовностей транзакцій I2C: простий PCF8574 проти регістрового MCP23017/TCA9555."""
    w, h = 920, 430
    frags = []

    # Секція 1: PCF8574 (Прямий доступ без показчика регістру)
    frags.append(rect(20, 20, 880, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 45, "1. Транзакції PCF8574 (Безрегістрова архітектура)", size=14, bold=True, color=INK))

    # Запис у PCF8574
    frags.append(text(40, 78, "Запис:", size=12, bold=True, color="#334155", anchor="start"))
    frags.append(rect(100, 60, 35, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(117, 80, "S", size=12, bold=True, color=POS))
    frags.append(rect(140, 60, 130, 30, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=3))
    frags.append(text(205, 80, "Адреса + W (0)", size=11, bold=True, color="#3730a3"))
    frags.append(rect(275, 60, 40, 30, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(295, 80, "ACK", size=10, bold=True, color="#166534"))
    frags.append(rect(320, 60, 140, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(390, 80, "Байт стану порту", size=11, bold=True, color="#92400e"))
    frags.append(rect(465, 60, 40, 30, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(485, 80, "ACK", size=10, bold=True, color="#166534"))
    frags.append(rect(510, 60, 35, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(527, 80, "P", size=12, bold=True, color=POS))

    # Читання з PCF8574
    frags.append(text(40, 133, "Читання:", size=12, bold=True, color="#334155", anchor="start"))
    frags.append(rect(100, 115, 35, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(117, 135, "S", size=12, bold=True, color=POS))
    frags.append(rect(140, 115, 130, 30, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=3))
    frags.append(text(205, 135, "Адреса + R (1)", size=11, bold=True, color="#3730a3"))
    frags.append(rect(275, 115, 40, 30, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(295, 135, "ACK", size=10, bold=True, color="#166534"))
    frags.append(rect(320, 115, 140, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(390, 135, "Байт з пінів порту", size=11, bold=True, color="#92400e"))
    frags.append(rect(465, 115, 45, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(487, 135, "NACK", size=10, bold=True, color=POS))
    frags.append(rect(515, 115, 35, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(532, 135, "P", size=12, bold=True, color=POS))

    # Секція 2: MCP23017 / TCA9555 (Покажчик регістру та повторний старт)
    frags.append(rect(20, 215, 880, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 240, "2. Транзакції регістрових розширювачів (TCA9555 / MCP23017)", size=14, bold=True, color=INK))

    # Запис у регістр
    frags.append(text(40, 278, "Запис:", size=12, bold=True, color="#334155", anchor="start"))
    frags.append(rect(100, 260, 30, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(115, 279, "S", size=11, bold=True, color=POS))
    frags.append(rect(135, 260, 115, 28, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=3))
    frags.append(text(192, 279, "Адреса + W", size=10, bold=True, color="#3730a3"))
    frags.append(rect(255, 260, 35, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(272, 279, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(295, 260, 130, 28, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=3))
    frags.append(text(360, 279, "Регістр (напр. IODIR)", size=10, bold=True, color="#6b21a8"))
    frags.append(rect(430, 260, 35, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(447, 279, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(470, 260, 115, 28, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(527, 279, "Дані байт 1", size=10, bold=True, color="#92400e"))
    frags.append(rect(590, 260, 35, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(607, 279, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(630, 260, 115, 28, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(687, 279, "Дані байт 2 (auto++ )", size=9, bold=True, color="#92400e"))
    frags.append(rect(750, 260, 35, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(767, 279, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(790, 260, 30, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(805, 279, "P", size=11, bold=True, color=POS))

    # Читання з регістру (Repeated START)
    frags.append(text(40, 343, "Читання:", size=12, bold=True, color="#334155", anchor="start"))
    frags.append(rect(100, 325, 25, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(112, 344, "S", size=10, bold=True, color=POS))
    frags.append(rect(130, 325, 95, 28, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=3))
    frags.append(text(177, 344, "Адреса + W", size=10, bold=True, color="#3730a3"))
    frags.append(rect(230, 325, 28, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(244, 344, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(263, 325, 115, 28, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=3))
    frags.append(text(320, 344, "Регістр (INTCAP)", size=10, bold=True, color="#6b21a8"))
    frags.append(rect(383, 325, 28, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(397, 344, "A", size=10, bold=True, color="#166534"))

    # Repeated Start
    frags.append(rect(416, 325, 30, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(431, 344, "Sr", size=10, bold=True, color=POS))
    frags.append(rect(451, 325, 95, 28, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=3))
    frags.append(text(498, 344, "Адреса + R", size=10, bold=True, color="#3730a3"))
    frags.append(rect(551, 325, 28, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(565, 344, "A", size=10, bold=True, color="#166534"))
    frags.append(rect(584, 325, 115, 28, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(641, 344, "Дані з регістру", size=10, bold=True, color="#92400e"))
    frags.append(rect(704, 325, 35, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(721, 344, "NA", size=10, bold=True, color=POS))
    frags.append(rect(744, 325, 25, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(756, 344, "P", size=10, bold=True, color=POS))

    # Пояснення легенди
    frags.append(text(460, 395, "S=START, Sr=Repeated START, P=STOP, A=ACK (0), NA=NACK (1)", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "transaction-flow.svg"), w, h, *frags)


def fig_addressing_and_bus():
    """Топологія підключення розширювачів до хоста: лінії SDA/SCL, адресні конфігурації A0-A2 та спільна лінія /INT."""
    w, h = 920, 460
    frags = []

    # Хост-контролер (MCU)
    frags.append(rect(30, 80, 160, 290, fill="#f1f5f9", stroke="#334155", sw=2, rx=8))
    frags.append(text(110, 115, "Мікроконтролер", size=14, bold=True, color=INK))
    frags.append(text(110, 135, "(Host MCU)", size=12, color=MUTED))

    frags.append(text(175, 185, "SDA", size=12, bold=True, color="#0284c7", anchor="end"))
    frags.append(text(175, 245, "SCL", size=12, bold=True, color="#0284c7", anchor="end"))
    frags.append(text(175, 315, "/INT_EXT", size=12, bold=True, color=POS, anchor="end"))

    # Шини I2C та INT
    frags.append(line(190, 180, 870, 180, color="#0284c7", sw=2.5))
    frags.append(text(880, 184, "SDA", size=12, bold=True, color="#0284c7", anchor="start"))

    frags.append(line(190, 240, 870, 240, color="#0284c7", sw=2.5))
    frags.append(text(880, 244, "SCL", size=12, bold=True, color="#0284c7", anchor="start"))

    frags.append(line(190, 310, 870, 310, color=POS, sw=2, dash="5,3"))
    frags.append(text(880, 314, "/INT (Wired-OR)", size=11, bold=True, color=POS, anchor="start"))

    # Підтяжки шини (Pull-up resistors)
    frags.append(line(240, 30, 360, 30, color=POS, sw=2))
    frags.append(text(300, 20, "VDD (+3.3V / +5V)", size=12, bold=True, color=POS))

    # Pull-up SDA
    frags.append(line(260, 30, 260, 70, color=LINE, sw=1.5))
    frags.append(rect(248, 70, 24, 45, fill="#fff", stroke="#0284c7", sw=1.5, rx=2))
    frags.append(text(260, 97, "4.7k", size=10, bold=True, color="#0284c7"))
    frags.append(line(260, 115, 260, 180, color=LINE, sw=1.5))
    frags.append(circle(260, 180, 4, fill="#0284c7", stroke="#0284c7"))

    # Pull-up SCL
    frags.append(line(300, 30, 300, 70, color=LINE, sw=1.5))
    frags.append(rect(288, 70, 24, 45, fill="#fff", stroke="#0284c7", sw=1.5, rx=2))
    frags.append(text(300, 97, "4.7k", size=10, bold=True, color="#0284c7"))
    frags.append(line(300, 115, 300, 240, color=LINE, sw=1.5))
    frags.append(circle(300, 240, 4, fill="#0284c7", stroke="#0284c7"))

    # Pull-up INT
    frags.append(line(340, 30, 340, 70, color=LINE, sw=1.5))
    frags.append(rect(328, 70, 24, 45, fill="#fff", stroke=POS, sw=1.5, rx=2))
    frags.append(text(340, 97, "10k", size=10, bold=True, color=POS))
    frags.append(line(340, 115, 340, 310, color=LINE, sw=1.5))
    frags.append(circle(340, 310, 4, fill=POS, stroke=POS))

    # Розширювач 1: Адреса 0x20 (A2=0, A1=0, A0=0)
    frags.append(rect(400, 120, 200, 250, fill="#f8fafc", stroke="#4f46e5", sw=2, rx=8))
    frags.append(text(500, 145, "Expander #1 (MCP23017)", size=12, bold=True, color="#3730a3"))
    frags.append(text(500, 165, "I2C Адреса: 0x20", size=11, bold=True, color=FIELD))

    frags.append(line(400, 180, 430, 180, color="#0284c7", sw=1.5))
    frags.append(circle(400, 180, 4, fill="#0284c7", stroke="#0284c7"))
    frags.append(text(435, 184, "SDA", size=10, color=MUTED, anchor="start"))

    frags.append(line(400, 240, 430, 240, color="#0284c7", sw=1.5))
    frags.append(circle(400, 240, 4, fill="#0284c7", stroke="#0284c7"))
    frags.append(text(435, 244, "SCL", size=10, color=MUTED, anchor="start"))

    frags.append(line(400, 310, 430, 310, color=POS, sw=1.5))
    frags.append(circle(400, 310, 4, fill=POS, stroke=POS))
    frags.append(text(435, 314, "/INT", size=10, color=POS, anchor="start"))

    # Адресні піни Expander 1 (GND/GND/GND)
    frags.append(rect(420, 200, 160, 28, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(text(500, 219, "A2=GND, A1=GND, A0=GND", size=9, bold=True, color="#1e40af"))

    # Виводи GPIO Expander 1
    frags.append(arrow(600, 240, 630, 240, color=LINE, sw=1.5))
    frags.append(text(605, 230, "16 GPIO", size=10, color=MUTED, anchor="start"))

    # Розширювач 2: Адреса 0x21 (A2=0, A1=0, A0=VDD)
    frags.append(rect(660, 120, 200, 250, fill="#f8fafc", stroke="#4f46e5", sw=2, rx=8))
    frags.append(text(760, 145, "Expander #2 (MCP23017)", size=12, bold=True, color="#3730a3"))
    frags.append(text(760, 165, "I2C Адреса: 0x21", size=11, bold=True, color=FIELD))

    frags.append(line(660, 180, 690, 180, color="#0284c7", sw=1.5))
    frags.append(circle(660, 180, 4, fill="#0284c7", stroke="#0284c7"))
    frags.append(text(695, 184, "SDA", size=10, color=MUTED, anchor="start"))

    frags.append(line(660, 240, 690, 240, color="#0284c7", sw=1.5))
    frags.append(circle(660, 240, 4, fill="#0284c7", stroke="#0284c7"))
    frags.append(text(695, 244, "SCL", size=10, color=MUTED, anchor="start"))

    frags.append(line(660, 310, 690, 310, color=POS, sw=1.5))
    frags.append(circle(660, 310, 4, fill=POS, stroke=POS))
    frags.append(text(695, 314, "/INT", size=10, color=POS, anchor="start"))

    # Адресні піни Expander 2 (GND/GND/VDD)
    frags.append(rect(680, 200, 160, 28, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(text(760, 219, "A2=GND, A1=GND, A0=VDD", size=9, bold=True, color="#1e40af"))

    # Виводи GPIO Expander 2
    frags.append(arrow(860, 240, 890, 240, color=LINE, sw=1.5))
    frags.append(text(865, 230, "16 GPIO", size=10, color=MUTED, anchor="start"))

    # Загальний підпис знизу
    frags.append(rect(180, 405, 560, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(460, 427, "Спільна лінія /INT об'єднує сповіщення від усіх чіпів за логікою монтажного АБО (Wired-OR)", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "addressing-and-bus.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_quasi_vs_pushpull()
    fig_interrupt_logic()
    fig_transaction_flow()
    fig_addressing_and_bus()
    print("Всі фігури успішно згенеровано.")
