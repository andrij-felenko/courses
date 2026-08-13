# -*- coding: utf-8 -*-
"""Фігури до теми «UART: апаратний модуль і периферійний контролер»
та її вставок.
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. Блок-схема апаратного контролера UART
# ════════════════════════════════════════════════════════════════════════════
def fig_uart_block_diagram():
    W, H = 820, 480
    f = [text(W / 2, 28, "Структурна схема апаратного периферійного модуля UART", size=15, bold=True)]

    # Зовнішній контур чипа/контролера
    f.append(rect(20, 50, 780, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(35, 72, "Периферійний модуль UART (IP Core)", size=12, bold=True, color="#475569", anchor="start"))

    # Тактування та Baud Rate Generator (ліворуч вгорі)
    f.append(rect(50, 95, 210, 85, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    f.append(text(155, 120, "Генератор Baud Rate", size=12, bold=True, color="#0369a1"))
    f.append(text(155, 140, "Дільник prescaler / fractional", size=10, color="#0c4a6e"))
    f.append(text(155, 160, "Передискретизація 16× / 8×", size=10, color="#0c4a6e"))

    # Лінія такту
    f.append(arrow(260, 137, 310, 137, color="#0284c7", sw=1.8))

    # Блок керування та регістрів (вгорі посередині)
    f.append(rect(310, 95, 230, 85, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    f.append(text(425, 120, "Регістри CR1 / CR2 / SR", size=12, bold=True, color="#334155"))
    f.append(text(425, 140, "Прапорці: TXE, RXNE, TC", size=10, color="#475569"))
    f.append(text(425, 160, "Помилки: OE, FE, PE, BI", size=10, color="#b91c1c"))

    # Переривання / DMA (вгорі праворуч)
    f.append(rect(580, 95, 190, 85, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(675, 120, "Логіка IRQ / DMA", size=12, bold=True, color="#b45309"))
    f.append(text(675, 145, "Запити до шини системного", size=10, color="#78350f"))
    f.append(text(675, 160, "процесора / дма", size=10, color="#78350f"))

    # Системна шина MCU (горизонтальна)
    f.append(line(50, 205, 770, 205, color="#475569", sw=3.0, dash="6,3"))
    f.append(text(410, 222, "Внутрішня системна шина даними / адресою MCU (APB / AHB)", size=10.5, color="#475569"))

    # Передавальний тракт (TX) - посередині ліворуч -> праворуч
    f.append(rect(50, 250, 340, 90, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    f.append(text(220, 272, "Канал передавача (TX)", size=12, bold=True, color="#15803d"))
    # TX FIFO & TSR
    f.append(rect(70, 288, 130, 40, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    f.append(text(135, 312, "TX FIFO (Буфер)", size=10, color="#166534"))
    f.append(arrow(200, 308, 230, 308, color="#16a34a", sw=1.5))
    f.append(rect(230, 288, 140, 40, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    f.append(text(300, 312, "Зсувний регістр TSR", size=10, color="#166534"))

    # Приймальний тракт (RX) - знизу ліворуч -> праворуч
    f.append(rect(50, 360, 340, 90, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    f.append(text(220, 382, "Канал приймача (RX)", size=12, bold=True, color="#b91c1c"))
    # RSR & RX FIFO
    f.append(rect(70, 398, 140, 40, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=4))
    f.append(text(140, 422, "Зсувний регістр RSR", size=10, color="#991b1b"))
    f.append(arrow(210, 418, 240, 418, color="#dc2626", sw=1.5))
    f.append(rect(240, 398, 130, 40, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=4))
    f.append(text(305, 422, "RX FIFO (Буфер)", size=10, color="#991b1b"))

    # Керування потоком RTS / CTS (праворуч знизу)
    f.append(rect(430, 250, 340, 200, fill="#fae8ff", stroke="#c026d3", sw=1.5, rx=6))
    f.append(text(600, 275, "Блок керування потоком (Flow Control)", size=12, bold=True, color="#86198f"))
    f.append(rect(460, 300, 130, 50, fill="#ffffff", stroke="#c026d3", sw=1.2, rx=4))
    f.append(text(525, 323, "Логіка RTS", size=11, bold=True, color="#701a75"))
    f.append(text(525, 340, "(Запит відправки)", size=9.5, color="#701a75"))
    f.append(rect(615, 300, 130, 50, fill="#ffffff", stroke="#c026d3", sw=1.2, rx=4))
    f.append(text(680, 323, "Логіка CTS", size=11, bold=True, color="#701a75"))
    f.append(text(680, 340, "(Готовність партнера)", size=9.5, color="#701a75"))

    # Зовнішні виводи (Pins)
    f.append(arrow(370, 308, 790, 308, color="#15803d", sw=2.0))
    f.append(text(785, 298, "TX Pin", size=11, bold=True, color="#15803d", anchor="end"))

    f.append(arrow(790, 418, 70, 418, color="#dc2626", sw=2.0))
    f.append(text(785, 433, "RX Pin", size=11, bold=True, color="#dc2626", anchor="end"))

    f.append(arrow(525, 350, 790, 350, color="#c026d3", sw=1.8))
    f.append(text(785, 365, "RTS Pin", size=10.5, bold=True, color="#86198f", anchor="end"))

    f.append(arrow(790, 380, 680, 380, color="#c026d3", sw=1.8))
    f.append(text(785, 395, "CTS Pin", size=10.5, bold=True, color="#86198f", anchor="end"))

    render(os.path.join(IMG, 'uart-block-diagram.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. Передискретизація 16x та мажоритарна вибірка
# ════════════════════════════════════════════════════════════════════════════
def fig_oversampling_sampling():
    W, H = 800, 380
    f = [text(W / 2, 26, "Принцип передискретизації 16× та мажоритарного фільтрування RX", size=15, bold=True)]

    # Вхідний сигнал RX (лінія зі старт-бітом та шумом)
    f.append(text(40, 70, "Вхідний сигнал RX:", size=12, bold=True, color="#334155", anchor="start"))

    # Спадок високого рівню, спад старт-біта, 16 тактів передискретизації
    rx_x0 = 160
    rx_points = [
        (40, 90), (rx_x0, 90), (rx_x0, 150), (rx_x0 + 520, 150), (rx_x0 + 520, 90), (760, 90)
    ]
    path_d = f"M {rx_points[0][0]} {rx_points[0][1]} L {rx_points[1][0]} {rx_points[1][1]} L {rx_points[2][0]} {rx_points[2][1]} L {rx_points[3][0]} {rx_points[3][1]} L {rx_points[4][0]} {rx_points[4][1]} L {rx_points[5][0]} {rx_points[5][1]}"
    f.append(f'<path d="{path_d}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')

    # Позначення Start Bit
    f.append(text(rx_x0 + 260, 175, "Інтервал старт-біта T_bit (16 тактів f_oversample)", size=11, bold=True, color="#1d4ed8"))
    f.append(line(rx_x0, 162, rx_x0 + 520, 162, color="#1d4ed8", sw=1.2))

    # Спадаючий фронт -> виявлення старту
    f.append(line(rx_x0, 60, rx_x0, 290, color="#dc2626", sw=1.2, dash="4,4"))
    f.append(text(rx_x0, 52, "Спад 1→0 (Запуск відліку)", size=10, bold=True, color="#dc2626"))

    # Такти передискретизації 0..15
    dx = 520 / 16.0
    for i in range(16):
        cx = rx_x0 + i * dx + dx / 2.0
        # Вертикальні засічки тактів
        f.append(line(cx, 195, cx, 235, color="#94a3b8", sw=1.0))
        f.append(text(cx, 210, str(i), size=9, color="#64748b"))

        # Точки заміру 7, 8, 9 — виділяємо зеленим / мажоритарним
        if i in [7, 8, 9]:
            f.append(circle(cx, 150, 4.5, fill="#16a34a", stroke="#15803d", sw=1.5))
            f.append(line(cx, 220, cx, 238, color="#16a34a", sw=1.5))

    # Прямокутник мажоритарного фільтра
    f.append(rect(rx_x0 + 7 * dx - 5, 240, 3 * dx + 10, 45, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    f.append(text(rx_x0 + 8.5 * dx, 258, "Мажоритарна вибірка", size=10, bold=True, color="#15803d"))
    f.append(text(rx_x0 + 8.5 * dx, 273, "Відліки #7, #8, #9 (2 з 3)", size=9, color="#166534"))

    # Пояснювальний блок знизу
    f.append(rect(40, 305, 720, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(55, 326, "1. Спадаючий фронт (1→0) на RX скидає лічильник 16× передискретизації.", size=10.5, color="#334155", anchor="start"))
    f.append(text(55, 346, "2. Відліки беруться в середині біта (такти 7, 8, 9). За більшістю значений відсіюється шум.", size=10.5, color="#334155", anchor="start"))

    render(os.path.join(IMG, 'oversampling-sampling.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. Апаратне керування потоком RTS/CTS
# ════════════════════════════════════════════════════════════════════════════
def fig_rts_cts_flow_control():
    W, H = 780, 400
    f = [text(W / 2, 26, "Апаратне керування потоком (RTS / CTS Handshaking)", size=15, bold=True)]

    # Приймач A та Передавач B
    f.append(rect(40, 60, 240, 310, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    f.append(text(160, 85, "Приймач A (MCU A)", size=13, bold=True, color="#1d4ed8"))

    f.append(rect(500, 60, 240, 310, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    f.append(text(620, 85, "Передавач B (MCU B)", size=13, bold=True, color="#15803d"))

    # RX FIFO буфер приймача A
    f.append(rect(60, 110, 200, 120, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    f.append(text(160, 130, "Приймальний буфер RX FIFO", size=11, bold=True, color="#1e40af"))
    # Рівень заповнення
    f.append(rect(75, 175, 170, 45, fill="#fca5a5", stroke="#ef4444", sw=1.2, rx=4))
    f.append(text(160, 195, "Поріг High Watermark!", size=10, bold=True, color="#991b1b"))
    f.append(text(160, 210, "(Буфер майже повний)", size=9, color="#991b1b"))

    # Передавальний буфер B
    f.append(rect(520, 110, 200, 120, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(620, 130, "Передавальний буфер TX", size=11, bold=True, color="#166534"))
    f.append(rect(535, 150, 170, 65, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    f.append(text(620, 175, "Призупинення TX", size=10.5, bold=True, color="#14532d"))
    f.append(text(620, 195, "(Пауза до деасерції CTS)", size=9.5, color="#14532d"))

    # Сигнальні лінії між ними
    # 1. Дані TX_B -> RX_A
    f.append(arrow(500, 140, 280, 140, color="#16a34a", sw=2.0))
    f.append(text(390, 132, "Дані (TX B -> RX A)", size=10.5, bold=True, color="#15803d"))

    # 2. Линія RTS_A -> CTS_B
    f.append(arrow(280, 260, 500, 260, color="#c026d3", sw=2.2))
    f.append(text(390, 250, "Сигнал RTS (A) -> CTS (B)", size=11, bold=True, color="#86198f"))
    f.append(text(390, 275, "RTS = High (Накладено стоп)", size=10, color="#701a75"))

    # Пояснення логіки
    f.append(rect(60, 280, 200, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    f.append(text(160, 298, "Приймач A піднімає RTS", size=10, bold=True, color="#334155"))
    f.append(text(160, 316, "при досягненні порогу", size=9.5, color="#475569"))
    f.append(text(160, 334, "щоб відсікти переповнення", size=9.5, color="#475569"))

    f.append(rect(520, 280, 200, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    f.append(text(620, 298, "Передавач B бачить CTS", size=10, bold=True, color="#334155"))
    f.append(text(620, 316, "і негайно зупиняє TX", size=9.5, color="#475569"))
    f.append(text(620, 334, "після поточного байта", size=9.5, color="#475569"))

    render(os.path.join(IMG, 'rts-cts-flow-control.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. Перетворення логічних рівнів інтерфейсу UART
# ════════════════════════════════════════════════════════════════════════════
def fig_uart_system_levels():
    W, H = 820, 420
    f = [text(W / 2, 26, "Сопряження логічних рівнів: TTL/CMOS, RS-232 та USB-UART", size=15, bold=True)]

    # Секція 1: MCU TTL/CMOS
    f.append(rect(30, 60, 220, 320, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(140, 88, "Мікроконтролер (MCU)", size=13, bold=True, color="#1e293b"))
    f.append(rect(50, 110, 180, 110, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(140, 135, "Рівні CMOS / TTL", size=11, bold=True, color="#334155"))
    f.append(text(140, 160, "Логічна 1: +3.3V / +5V", size=10, color="#0f172a"))
    f.append(text(140, 180, "Логічний 0: 0V (GND)", size=10, color="#0f172a"))
    f.append(text(140, 200, "Пряма полярність", size=9.5, color="#475569"))

    # Секція 2: RS-232 Конвертер
    f.append(rect(290, 60, 240, 150, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    f.append(text(410, 85, "Трансивер RS-232 (MAX3232)", size=12, bold=True, color="#1d4ed8"))
    f.append(text(410, 110, "Насос заряду (Charge Pump)", size=10, color="#1e40af"))
    f.append(text(410, 135, "Логічна 1: -3V ... -15V", size=10, bold=True, color="#1d4ed8"))
    f.append(text(410, 155, "Логічний 0: +3V ... +15V", size=10, bold=True, color="#1d4ed8"))
    f.append(text(410, 175, "Інверсна полярність!", size=9.5, color="#b91c1c"))

    # Раз'єм DB9 / Кабель
    f.append(rect(560, 90, 220, 90, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=6))
    f.append(text(670, 120, "Кабель RS-232 / DB9", size=11, bold=True, color="#1d4ed8"))
    f.append(text(670, 145, "Дальність до 15 метрів", size=10, color="#1e40af"))

    # Зв'язок MCU -> MAX3232 -> DB9
    f.append(arrow(250, 130, 290, 130, color="#2563eb", sw=1.8))
    f.append(arrow(530, 135, 560, 135, color="#2563eb", sw=1.8))

    # Секція 3: USB-UART Мост
    f.append(rect(290, 230, 240, 150, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(410, 255, "Мост USB-UART (CP2102/CH340)", size=12, bold=True, color="#15803d"))
    f.append(text(410, 280, "Апаратний контролер USB", size=10, color="#166534"))
    f.append(text(410, 305, "Перетворення пакети <-> байти", size=10, color="#166534"))
    f.append(text(410, 330, "Віртуальний COM-порт на ПК", size=10, bold=True, color="#15803d"))

    # ПК Host
    f.append(rect(560, 260, 220, 90, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(670, 290, "Комп'ютер (Host ПК)", size=11, bold=True, color="#15803d"))
    f.append(text(670, 315, "Шина USB (D+ / D-)", size=10, color="#166534"))

    # Зв'язок MCU -> USB Bridge -> Host
    f.append(arrow(250, 305, 290, 305, color="#16a34a", sw=1.8))
    f.append(arrow(530, 305, 560, 305, color="#16a34a", sw=1.8))

    render(os.path.join(IMG, 'uart-system-levels.svg'), W, H, *f)


if __name__ == '__main__':
    fig_uart_block_diagram()
    fig_oversampling_sampling()
    fig_rts_cts_flow_control()
    fig_uart_system_levels()
    print("Готово: згенеровано всі 4 фігури в img/")
