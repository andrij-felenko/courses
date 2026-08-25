# -*- coding: utf-8 -*-
"""Генератор фігур для теми ble-link-layer (BLE Link Layer: канальний стрибок і connection events)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ll-fsm: кінцевий автомат станів Link Layer ────────────────────────────
def fig_ll_fsm():
    W, H = 840, 480
    p = []

    # Standby в центрі зверху
    p.append(rect(340, 30, 160, 50, fill="#f8fafc", stroke=INK, sw=2.0, rx=8))
    p.append(text(420, 60, "STANDBY", size=13, color=INK, bold=True))

    # Advertising зліва
    p.append(rect(40, 150, 200, 65, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(140, 178, "ADVERTISING", size=12, color=FIELD, bold=True))
    p.append(text(140, 198, "Випромінює пакети реклами", size=10, color=MUTED))

    # Scanning по центру
    p.append(rect(320, 150, 200, 65, fill="#eef4ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(420, 178, "SCANNING", size=12, color=NEG, bold=True))
    p.append(text(420, 198, "Слухає рекламні канали", size=10, color=MUTED))

    # Initiating справа
    p.append(rect(600, 150, 200, 65, fill="#fdf2e9", stroke=POS, sw=1.8, rx=8))
    p.append(text(700, 178, "INITIATING", size=12, color=POS, bold=True))
    p.append(text(700, 198, "Слухає та надсилає CONNECT", size=10, color=MUTED))

    # З'єднання (Connection State) знизу
    p.append(rect(160, 310, 520, 140, fill="#fdfcf8", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(420, 335, "CONNECTION STATE (Стан з'єднання)", size=13, color=INK, bold=True))

    # Slave role
    p.append(rect(190, 360, 210, 70, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(295, 388, "Slave (Ведений)", size=12, color=FIELD, bold=True))
    p.append(text(295, 410, "Синхронізується з розкладом Master", size=9.5, color=MUTED))

    # Master role
    p.append(rect(440, 360, 210, 70, fill="#fdf2e9", stroke=POS, sw=1.6, rx=6))
    p.append(text(545, 388, "Master (Ведучий)", size=12, color=POS, bold=True))
    p.append(text(545, 410, "Задає сітку Anchor Points і стрибки", size=9.5, color=MUTED))

    # Стрілки переходів
    # Standby -> Adv
    p.append(arrow(360, 80, 200, 150, color=FIELD, sw=1.6))
    p.append(text(260, 105, "Host: Start Adv", size=10, color=FIELD, bold=True))

    # Standby -> Scan
    p.append(arrow(420, 80, 420, 150, color=NEG, sw=1.6))
    p.append(text(435, 115, "Host: Scan", size=10, color=NEG, bold=True, anchor="start"))

    # Standby -> Init
    p.append(arrow(480, 80, 640, 150, color=POS, sw=1.6))
    p.append(text(580, 105, "Host: Connect", size=10, color=POS, bold=True))

    # Adv -> Slave Connection
    p.append(arrow(140, 215, 250, 360, color=FIELD, sw=1.8))
    p.append(text(145, 275, "Прийнято CONNECT_IND", size=10, color=FIELD, bold=True, anchor="start"))

    # Init -> Master Connection
    p.append(arrow(700, 215, 590, 360, color=POS, sw=1.8))
    p.append(text(695, 275, "Надіслано CONNECT_IND", size=10, color=POS, bold=True, anchor="end"))

    # Connection -> Standby (Розірвання)
    p.append(arrow(420, 310, 420, 80, color=MUTED, sw=1.5))
    p.append(text(340, 250, "LL_TERMINATE / Timeout", size=10, color=MUTED, italic=True))

    # Adv/Scan/Init -> Standby
    p.append(arrow(100, 150, 340, 60, color=MUTED, sw=1.2))
    p.append(arrow(740, 150, 500, 60, color=MUTED, sw=1.2))

    render(os.path.join(OUT, "ll-fsm.svg"), W, H, *p,
           title="Кінцевий автомат станів Link Layer у BLE")


# ── 2. ble-spectrum-channels: частотний спектр і 40 каналів ──────────────────
def fig_ble_spectrum():
    W, H = 840, 390
    p = []

    # Заголовок
    p.append(text(420, 25, "Розподіл 40 фізичних каналів BLE у діапазоні 2.4 ГГц ISM", size=13, color=INK, bold=True))

    # Wi-Fi фонові смуги (20 МГц шириною) - зверху (y=45..135)
    # Wi-Fi Ch 1: 2412 MHz (2401..2423) -> x: 60..230
    p.append(rect(60, 45, 170, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(145, 70, "Wi-Fi Канал 1", size=11, color=POS, bold=True))
    p.append(text(145, 90, "2412 МГц (смуга 20 МГц)", size=9.5, color=POS))

    # Wi-Fi Ch 6: 2437 MHz (2426..2448) -> x: 310..480
    p.append(rect(310, 45, 170, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(395, 70, "Wi-Fi Канал 6", size=11, color=POS, bold=True))
    p.append(text(395, 90, "2437 МГц (смуга 20 МГц)", size=9.5, color=POS))

    # Wi-Fi Ch 11: 2462 MHz (2451..2473) -> x: 560..730
    p.append(rect(560, 45, 170, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(645, 70, "Wi-Fi Канал 11", size=11, color=POS, bold=True))
    p.append(text(645, 90, "2462 МГц (смуга 20 МГц)", size=9.5, color=POS))

    # Шкала частот і лінія
    p.append(line(50, 235, 790, 235, color=INK, sw=2.0))

    # Рекламні канали BLE: 37, 38, 39 (y=155..220)
    # Ch 37: 2402 MHz -> x = 55
    p.append(rect(52, 155, 38, 65, fill="#dcfce7", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(71, 180, "Ch 37", size=10, color=FIELD, bold=True))
    p.append(text(71, 202, "2402", size=9.5, color=FIELD))

    # Ch 38: 2426 MHz -> x = 255 (між Wi-Fi 1 та 6)
    p.append(rect(255, 155, 38, 65, fill="#dcfce7", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(274, 180, "Ch 38", size=10, color=FIELD, bold=True))
    p.append(text(274, 202, "2426", size=9.5, color=FIELD))

    # Ch 39: 2480 MHz -> x = 745 (вище Wi-Fi 11)
    p.append(rect(745, 155, 38, 65, fill="#dcfce7", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(764, 180, "Ch 39", size=10, color=FIELD, bold=True))
    p.append(text(764, 202, "2480", size=9.5, color=FIELD))

    # Позначення каналів даних (0..36)
    p.append(text(420, 268, "Канали передачі даних BLE: Канали 0–36 (крок 2 МГц)", size=12, color=NEG, bold=True))
    p.append(text(420, 290, "Канали даних рівномірно заповнюють діапазон 2404 .. 2478 МГц для стрибків (FHSS)", size=10.5, color=MUTED))

    # Позначки шкали МГц
    p.append(line(55, 230, 55, 240, color=INK, sw=1.5))
    p.append(text(55, 252, "2400 МГц", size=9.5, color=MUTED))

    p.append(line(780, 230, 780, 240, color=INK, sw=1.5))
    p.append(text(780, 252, "2483.5 МГц", size=9.5, color=MUTED))

    # Легенда знизу
    p.append(rect(180, 335, 18, 14, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(205, 347, "Рекламні канали (37, 38, 39)", size=10.5, color=INK, anchor="start"))

    p.append(rect(450, 335, 18, 14, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
    p.append(text(475, 347, "Смуги завад Wi-Fi 802.11 (1, 6, 11)", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "ble-spectrum-channels.svg"), W, H, *p,
           title="Розподіл частотних каналів BLE та електромагнітна сумісність з Wi-Fi")


# ── 3. connection-event-timing: таймінги події з'єднання ─────────────────────
def fig_conn_timing():
    W, H = 840, 420
    p = []

    p.append(text(420, 25, "Анатомія події з'єднання (Connection Event) та міжкадрові інтервали", size=13, color=INK, bold=True))

    # Часова вісь
    p.append(line(40, 160, 800, 160, color=LINE, sw=1.5))
    p.append(text(805, 164, "t", size=12, color=INK, bold=True, anchor="start"))

    # Anchor Point 0
    p.append(line(60, 60, 60, 220, color=POS, sw=2.0, dash="4,3"))
    p.append(text(60, 50, "Anchor Point (n)", size=11, color=POS, bold=True))

    # Master Packet 1 (Tx)
    p.append(rect(60, 110, 110, 45, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(115, 130, "Master Tx", size=11, color=POS, bold=True))
    p.append(text(115, 145, "Data PDU (SN=0)", size=9, color=POS))

    # T_IFS = 150 µs
    p.append(line(170, 135, 230, 135, color=MUTED, sw=1.5))
    p.append(line(170, 128, 170, 142, color=MUTED, sw=1.5))
    p.append(line(230, 128, 230, 142, color=MUTED, sw=1.5))
    p.append(text(200, 122, "T_IFS", size=10, color=MUTED, bold=True))
    p.append(text(200, 150, "150 мкс", size=9, color=MUTED))

    # Slave Packet 1 (Tx)
    p.append(rect(230, 170, 110, 45, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(285, 190, "Slave Tx", size=11, color=FIELD, bold=True))
    p.append(text(285, 205, "ACK (NESN=1)", size=9, color=FIELD))

    # T_IFS знову
    p.append(line(340, 135, 400, 135, color=MUTED, sw=1.5))
    p.append(line(340, 128, 340, 142, color=MUTED, sw=1.5))
    p.append(line(400, 128, 400, 142, color=MUTED, sw=1.5))
    p.append(text(370, 122, "T_IFS", size=10, color=MUTED, bold=True))

    # Master Packet 2 (Tx - MD=1)
    p.append(rect(400, 110, 100, 45, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(450, 130, "Master Tx", size=11, color=POS, bold=True))
    p.append(text(450, 145, "Data (MD=0)", size=9, color=POS))

    # Slave Packet 2 (Tx)
    p.append(rect(530, 170, 100, 45, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(580, 190, "Slave Tx", size=11, color=FIELD, bold=True))
    p.append(text(580, 205, "ACK (MD=0)", size=9, color=FIELD))

    # Сон до наступного Anchor Point
    p.append(rect(635, 145, 115, 30, fill="#f3f4f6", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(692, 164, "Режим сну (Sleep)", size=10, color=MUTED, italic=True))

    # Anchor Point n+1
    p.append(line(755, 60, 755, 220, color=POS, sw=2.0, dash="4,3"))
    p.append(text(755, 50, "Anchor Point (n+1)", size=11, color=POS, bold=True))

    # Стрілка Connection Interval
    p.append(line(60, 80, 755, 80, color=NEG, sw=2.0))
    p.append(line(60, 73, 60, 87, color=NEG, sw=2.0))
    p.append(line(755, 73, 755, 87, color=NEG, sw=2.0))
    p.append(text(410, 74, "Connection Interval (connInterval: 7.5 мс .. 4.0 с)", size=11, color=NEG, bold=True))

    # Блок пояснень параметрів
    p.append(rect(40, 250, 760, 150, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(60, 275, "Ключові часові параметри Link Layer:", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(60, 302, "• connInterval — період між точками прив'язки (Anchor Points), крок 1.25 мс.", size=11, color=INK, anchor="start"))
    p.append(text(60, 327, "• connSlaveLatency — кількість подій зв'язку (0..499), які ведений може проспати за відсутності даних.", size=11, color=INK, anchor="start"))
    p.append(text(60, 352, "• connSupervisionTimeout — граничний час (100 мс..32 с) очікування успішного пакету до розриву зв'язку.", size=11, color=INK, anchor="start"))
    p.append(text(60, 377, "• T_IFS (Inter-Frame Space) — фіксована пауза 150 ± 1 мкс між передачею та прийомом для перемикання радіотракту.", size=11, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "connection-event-timing.svg"), W, H, *p,
           title="Таймінги події з'єднання BLE Link Layer та міжкадровий інтервал T_IFS")


# ── 4. ll-packet-format: структура пакету Link Layer ─────────────────────────
def fig_packet_format():
    W, H = 840, 390
    p = []

    p.append(text(420, 28, "Структура кадру канального рівня (Link Layer Packet Format)", size=13, color=INK, bold=True))

    # Загальна структура пакету
    x0 = 60
    # Preamble
    p.append(rect(x0, 60, 90, 55, fill="#eef4ff", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x0 + 45, 83, "Preamble", size=11, color=NEG, bold=True))
    p.append(text(x0 + 45, 102, "1 / 2 байти", size=9.5, color=MUTED))

    # Access Address
    p.append(rect(x0 + 95, 60, 160, 55, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(x0 + 175, 83, "Access Address", size=11, color=POS, bold=True))
    p.append(text(x0 + 175, 102, "4 байти (32 біти)", size=9.5, color=MUTED))

    # PDU
    p.append(rect(x0 + 260, 60, 330, 55, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(x0 + 425, 83, "Link Layer PDU", size=12, color=FIELD, bold=True))
    p.append(text(x0 + 425, 102, "2 .. 257 байтів", size=9.5, color=MUTED))

    # CRC
    p.append(rect(x0 + 595, 60, 125, 55, fill="#f3e8ff", stroke="#8e44ad", sw=1.8, rx=4))
    p.append(text(x0 + 657, 83, "CRC", size=11, color="#8e44ad", bold=True))
    p.append(text(x0 + 657, 102, "3 байти (24 біти)", size=9.5, color=MUTED))

    # Розгортання PDU (Data Channel PDU Header)
    p.append(line(x0 + 260, 115, 60, 175, color=FIELD, sw=1.2, dash="3,3"))
    p.append(line(x0 + 590, 115, 780, 175, color=FIELD, sw=1.2, dash="3,3"))

    p.append(rect(60, 175, 720, 185, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(420, 198, "Деталізація Data Channel PDU (Пакет каналу даних)", size=12, color=FIELD, bold=True))

    # Блок заголовка PDU Header (16 бітів)
    p.append(rect(80, 215, 340, 75, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(250, 233, "16-бітний заголовок (Header)", size=11, color=INK, bold=True))

    # Поля заголовка: LLID (2), NESN (1), SN (1), MD (1), CP/RFU (3), Length (8)
    p.append(rect(90, 245, 45, 35, fill="#eef4ff", stroke=NEG, sw=1.0, rx=2))
    p.append(text(112, 259, "LLID", size=9.5, color=NEG, bold=True))
    p.append(text(112, 272, "2 біти", size=9.5, color=MUTED))

    p.append(rect(140, 245, 45, 35, fill="#fdf2e9", stroke=POS, sw=1.0, rx=2))
    p.append(text(162, 259, "NESN", size=9.5, color=POS, bold=True))
    p.append(text(162, 272, "1 біт", size=9.5, color=MUTED))

    p.append(rect(190, 245, 40, 35, fill="#fdf2e9", stroke=POS, sw=1.0, rx=2))
    p.append(text(210, 259, "SN", size=9.5, color=POS, bold=True))
    p.append(text(210, 272, "1 біт", size=9.5, color=MUTED))

    p.append(rect(235, 245, 40, 35, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=2))
    p.append(text(255, 259, "MD", size=9.5, color=FIELD, bold=True))
    p.append(text(255, 272, "1 біт", size=9.5, color=MUTED))

    p.append(rect(280, 245, 55, 35, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=2))
    p.append(text(307, 259, "CP/RFU", size=9.5, color=MUTED, bold=True))
    p.append(text(307, 272, "3 біти", size=9.5, color=MUTED))

    p.append(rect(340, 245, 70, 35, fill="#eef4ff", stroke=NEG, sw=1.0, rx=2))
    p.append(text(375, 259, "Length", size=9.5, color=NEG, bold=True))
    p.append(text(375, 272, "8 бітів", size=9.5, color=MUTED))

    # Блок корисного навантаження (Payload)
    p.append(rect(435, 215, 330, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(600, 242, "Payload (Корисне навантаження)", size=11, color=FIELD, bold=True))
    p.append(text(600, 267, "0 .. 251 байт (L2CAP фрагменти або LL Control)", size=10, color=MUTED))

    p.append(text(420, 320, "LLID: 01b = Continuation/Empty, 10b = Start L2CAP, 11b = LL Control", size=10.5, color=INK))
    p.append(text(420, 342, "Контроль потоку ARQ: біти SN (Sequence Number) та NESN (Next Expected Sequence Number)", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "ll-packet-format.svg"), W, H, *p,
           title="Формат пакету канального рівня BLE та бітові поля заголовка PDU")


# ── 5. arq-flow: механізм підтверджень Stop-and-Wait ARQ ─────────────────────
def fig_arq_flow():
    W, H = 840, 440
    p = []

    p.append(text(420, 25, "Апаратний протокол Stop-and-Wait ARQ у BLE Link Layer", size=13, color=INK, bold=True))

    # Стовпчики Master та Slave
    p.append(rect(120, 45, 140, 35, fill="#fdf2e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(190, 68, "Master (Tx / Rx)", size=11, color=POS, bold=True))
    p.append(line(190, 80, 190, 410, color=POS, sw=1.5, dash="4,4"))

    p.append(rect(580, 45, 140, 35, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(650, 68, "Slave (Rx / Tx)", size=11, color=FIELD, bold=True))
    p.append(line(650, 80, 650, 410, color=FIELD, sw=1.5, dash="4,4"))

    # Фаза 1: Успішна передача
    p.append(arrow(190, 105, 650, 140, color=POS, sw=1.6))
    p.append(text(420, 112, "Data PDU [SN=0, NESN=0]", size=10, color=POS, bold=True))

    p.append(arrow(650, 155, 190, 190, color=FIELD, sw=1.6))
    p.append(text(420, 162, "ACK PDU [SN=0, NESN=1] (підтверджено)", size=10, color=FIELD, bold=True))

    # Фаза 2: Помилка CRC / Втрата пакету
    p.append(arrow(190, 215, 650, 250, color=POS, sw=1.6))
    p.append(text(420, 222, "Data PDU [SN=1, NESN=0] (пошкоджено в ефірі)", size=10, color=POS, bold=True))
    p.append(circle(530, 241, 10, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(530, 245, "✕", size=10, color=POS, bold=True))

    # Slave відхиляє пакет і повторює старий NESN
    p.append(arrow(650, 265, 190, 300, color=FIELD, sw=1.6))
    p.append(text(420, 272, "NACK PDU [SN=0, NESN=1] (NESN не змінився!)", size=10, color="#c0392b", bold=True))

    # Фаза 3: Повторна передача (Retransmit)
    p.append(arrow(190, 325, 650, 360, color=POS, sw=1.8))
    p.append(text(420, 332, "Retransmit: Data PDU [SN=1, NESN=0]", size=10, color=POS, bold=True))

    p.append(arrow(650, 375, 190, 410, color=FIELD, sw=1.6))
    p.append(text(420, 382, "ACK PDU [SN=1, NESN=0] (успішно прийнято)", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "arq-flow.svg"), W, H, *p,
           title="Послідовність підтверджень та повторної передачі пакетів у протоколі ARQ BLE Link Layer")


if __name__ == "__main__":
    fig_ll_fsm()
    fig_ble_spectrum()
    fig_conn_timing()
    fig_packet_format()
    fig_arq_flow()
    print("Всі 5 фігур успішно згенеровано.")
