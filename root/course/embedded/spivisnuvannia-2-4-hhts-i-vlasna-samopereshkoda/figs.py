# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Співіснування 2,4 ГГц і власна самоперешкода'."""

import sys
import os

# Імпорт спільних утиліт svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_freq_overlap():
    """Діаграма частотної сітки 2.4 ГГц: Wi-Fi, BLE та Zigbee з виділенням безпечних зон."""
    w, h = 860, 430
    frags = []

    # Заголовок блоку
    frags.append(text(w / 2, 28, "Частотний розподіл діапазону 2,4 ГГц ISM (2400–2483,5 МГц)", size=16, bold=True))

    # Вісь частот
    x_start = 80
    x_end = 800
    f_min = 2400.0
    f_max = 2485.0

    def f2x(f):
        return x_start + (f - f_min) / (f_max - f_min) * (x_end - x_start)

    # Лінія осі
    axis_y = 390
    frags.append(line(x_start - 10, axis_y, x_end + 20, axis_y, color=INK, sw=1.5))
    frags.append(arrow(x_end + 10, axis_y, x_end + 30, axis_y, color=INK, sw=1.5))
    frags.append(text(x_end + 40, axis_y + 4, "МГц", size=12, bold=True, anchor="start"))

    # Позначки частот на осі
    freq_ticks = [2400, 2412, 2425, 2437, 2450, 2462, 2475, 2483.5]
    for ft in freq_ticks:
        tx = f2x(ft)
        frags.append(line(tx, axis_y - 4, tx, axis_y + 4, color=MUTED, sw=1.0))
        frags.append(text(tx, axis_y + 18, f"{ft:g}", size=11, color=MUTED))

    # 1. Рівень Wi-Fi (Канали 1, 6, 11) - смуга 20 МГц (маска 22 МГц)
    y_wifi = 80
    frags.append(text(35, y_wifi + 22, "Wi-Fi", size=13, bold=True, anchor="middle", color="#b03a2e"))
    frags.append(text(35, y_wifi + 36, "802.11b/g/n", size=10, color=MUTED, anchor="middle"))

    wifi_ch = [
        (1, 2412, "Канал 1 (2412 МГц)"),
        (6, 2437, "Канал 6 (2437 МГц)"),
        (11, 2462, "Канал 11 (2462 МГц)")
    ]

    for ch_num, fc, lbl in wifi_ch:
        x_left = f2x(fc - 11.0)
        x_right = f2x(fc + 11.0)
        ch_w = x_right - x_left
        frags.append(rect(x_left, y_wifi, ch_w, 48, fill="#fdecea", stroke="#e74c3c", sw=1.5, rx=8))
        frags.append(text(f2x(fc), y_wifi + 22, f"Wi-Fi Канал {ch_num}", size=13, bold=True, color="#922b21"))
        frags.append(text(f2x(fc), y_wifi + 38, "смуга 22 МГц", size=10, color="#b03a2e"))

    # 2. Рівень Zigbee / Thread (IEEE 802.15.4) - 16 каналів (11..26)
    y_zig = 175
    frags.append(text(35, y_zig + 20, "Zigbee", size=13, bold=True, anchor="middle", color="#27ae60"))
    frags.append(text(35, y_zig + 34, "Thread", size=10, color=MUTED, anchor="middle"))

    # Безпечні канали 15, 20, 25, 26 (зелені) проти зашумлених (сіро-червоні)
    safe_zig = {15, 20, 25, 26}
    for zc in range(11, 27):
        fc = 2405 + (zc - 11) * 5
        x_c = f2x(fc)
        is_safe = zc in safe_zig
        fill_c = "#eafaf1" if is_safe else "#f4f6f7"
        stroke_c = "#27ae60" if is_safe else "#bdc3c7"
        txt_c = "#1e8449" if is_safe else "#7f8c8d"

        frags.append(rect(x_c - 9, y_zig, 18, 44, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(x_c, y_zig + 18, str(zc), size=11, bold=is_safe, color=txt_c))
        frags.append(text(x_c, y_zig + 34, f"{fc}", size=9, color=txt_c))

    # Позначення тихих гаваней Zigbee
    frags.append(rect(f2x(2425) - 30, y_zig + 50, 60, 18, fill="#d4efdf", stroke="#27ae60", sw=1.0, rx=4))
    frags.append(text(f2x(2425), y_zig + 63, "Тиха гавань 15", size=9, bold=True, color="#196f3d"))

    frags.append(rect(f2x(2450) - 30, y_zig + 50, 60, 18, fill="#d4efdf", stroke="#27ae60", sw=1.0, rx=4))
    frags.append(text(f2x(2450), y_zig + 63, "Тиха гавань 20", size=9, bold=True, color="#196f3d"))

    frags.append(rect(f2x(2477.5) - 36, y_zig + 50, 72, 18, fill="#d4efdf", stroke="#27ae60", sw=1.0, rx=4))
    frags.append(text(f2x(2477.5), y_zig + 63, "Гавані 25 та 26", size=9, bold=True, color="#196f3d"))

    # 3. Рівень Bluetooth Low Energy (BLE) - 40 каналів
    y_ble = 280
    frags.append(text(35, y_ble + 20, "BLE", size=13, bold=True, anchor="middle", color="#2980b9"))
    frags.append(text(35, y_ble + 34, "40 каналів", size=10, color=MUTED, anchor="middle"))

    # Фонова плашка BLE (охоплює всі 40 каналів від 2400 до 2483.5 МГц з запасом)
    ble_x0 = f2x(2400)
    ble_x1 = f2x(2483.5)
    frags.append(rect(ble_x0, y_ble, ble_x1 - ble_x0, 52, fill="#ebf5fb", stroke="#aed6f1", sw=1.0, rx=6))
    frags.append(text((ble_x0 + ble_x1) / 2, y_ble + 17, "37 каналів даних BLE (f = 2404..2478 МГц, крок 2 МГц) — Адаптивні стрибки AFH", size=11, color="#2471a3"))

    # Канали реклами (Adv Ch 37, 38, 39)
    adv_ch = [
        (37, 2402, "Канал 37 (Adv)"),
        (38, 2426, "Канал 38 (Adv)"),
        (39, 2480, "Канал 39 (Adv)")
    ]

    for adv_num, fc, lbl in adv_ch:
        x_adv = f2x(fc)
        frags.append(rect(x_adv - 13, y_ble + 26, 26, 20, fill="#2980b9", stroke="#1b4f72", sw=1.2, rx=3))
        frags.append(text(x_adv, y_ble + 40, str(adv_num), size=10, bold=True, color="#ffffff"))

    # Виноски для каналів реклами BLE
    frags.append(text(f2x(2402), y_ble + 64, "Adv 37 (2402)", size=9, color="#1b4f72", bold=True))
    frags.append(text(f2x(2426), y_ble + 64, "Adv 38 (2426)", size=9, color="#1b4f72", bold=True))
    frags.append(text(f2x(2480), y_ble + 64, "Adv 39 (2480)", size=9, color="#1b4f72", bold=True))

    render(os.path.join(IMG_DIR, "freq-overlap-24ghz.svg"), w, h, *frags)


def fig_lna_blocking():
    """Схемотехнічний механізм блокування вхідного LNA та десенситизації."""
    w, h = 820, 390
    frags = []

    frags.append(text(w / 2, 26, "Механізм власної самоперешкоди та блокування вхідного підсилювача (LNA)", size=16, bold=True))

    # Ліва частина: Передавач Wi-Fi
    tx_x = 40
    tx_y = 65
    frags.append(rect(tx_x, tx_y, 220, 260, fill="#fdfefe", stroke="#c0392b", sw=1.8, rx=8))
    frags.append(text(tx_x + 110, tx_y + 24, "Wi-Fi Передавач (PA)", size=14, bold=True, color="#922b21"))

    # Блок синтезатора й PA
    frags.append(rect(tx_x + 20, tx_y + 45, 180, 45, fill="#fdecea", stroke="#e74c3c", sw=1.2, rx=4))
    frags.append(text(tx_x + 110, tx_y + 66, "Потужний PA: +20 dBm", size=12, bold=True, color="#c0392b"))
    frags.append(text(tx_x + 110, tx_y + 80, "(100 мВт у каналі Wi-Fi)", size=10, color=MUTED))

    # Фазовий шум та бічні пелюстки
    frags.append(rect(tx_x + 20, tx_y + 105, 180, 50, fill="#fbfcfc", stroke="#bdc3c7", sw=1.0, rx=4))
    frags.append(text(tx_x + 110, tx_y + 124, "Фазовий шум гетеродина", size=11, bold=True, color=INK))
    frags.append(text(tx_x + 110, tx_y + 142, "Спектральне відростання (ACLR)", size=10, color=MUTED))

    # Антена Wi-Fi (RF вихід іде вправо від PA)
    ant_tx_x = tx_x + 180
    ant_tx_y = tx_y + 240
    frags.append(line(tx_x + 110, tx_y + 165, ant_tx_x, tx_y + 165, color="#c0392b", sw=2.0))
    frags.append(line(ant_tx_x, tx_y + 165, ant_tx_x, ant_tx_y - 25, color="#c0392b", sw=2.0))
    frags.append(line(ant_tx_x - 10, ant_tx_y - 25, ant_tx_x + 10, ant_tx_y - 25, color="#c0392b", sw=2.0))
    frags.append(text(ant_tx_x, ant_tx_y + 14, "Антена Wi-Fi", size=10, bold=True, color="#922b21"))

    # Центральна частина: Паразитний зв'язок на платі
    mid_x = 280
    mid_y = 110
    frags.append(rect(mid_x, mid_y, 220, 160, fill="#f8f9f9", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(mid_x + 110, mid_y + 22, "Паразитний зв'язок на платі", size=12, bold=True, color="#2c3e50"))

    frags.append(arrow(tx_x + 220, mid_y + 50, mid_x + 220, mid_y + 50, color="#e74c3c", sw=2.2))
    frags.append(text(mid_x + 110, mid_y + 44, "Потужна завада Wi-Fi", size=11, bold=True, color="#c0392b"))

    frags.append(text(mid_x + 110, mid_y + 75, "Розв'язка антен: S₂₁ ≈ -20 dB", size=11, bold=True, color="#2980b9"))
    frags.append(text(mid_x + 110, mid_y + 95, "Рівень на вході LNA: 0 dBm", size=12, bold=True, color="#c0392b"))
    frags.append(text(mid_x + 110, mid_y + 115, "(на 10 дБ вище точки P1dB!)", size=10, color="#922b21"))

    frags.append(text(mid_x + 110, mid_y + 142, "Пряме наведення по спільній землі", size=10, color=MUTED))

    # Права частина: Чутливий приймач BLE / Zigbee
    rx_x = 520
    rx_y = 65
    frags.append(rect(rx_x, rx_y, 260, 260, fill="#fdfefe", stroke="#2980b9", sw=1.8, rx=8))
    frags.append(text(rx_x + 130, rx_y + 24, "BLE / Zigbee Приймач (LNA)", size=14, bold=True, color="#1b4f72"))

    # Антена RX
    ant_rx_x = rx_x + 40
    ant_rx_y = rx_y + 80
    frags.append(line(ant_rx_x, ant_rx_y, ant_rx_x, ant_rx_y - 25, color="#2980b9", sw=2.0))
    frags.append(line(ant_rx_x - 10, ant_rx_y - 25, ant_rx_x + 10, ant_rx_y - 25, color="#2980b9", sw=2.0))
    frags.append(text(ant_rx_x, ant_rx_y + 16, "Антена RX", size=10, bold=True, color="#1b4f72"))

    # Корисний сигнал з ефіру
    frags.append(arrow(rx_x - 30, ant_rx_y - 12, ant_rx_x - 12, ant_rx_y - 12, color="#27ae60", sw=1.5))
    frags.append(text(rx_x - 35, ant_rx_y - 22, "Корисний сигнал -95 dBm", size=9, bold=True, color="#1e8449", anchor="end"))

    # Блок LNA
    frags.append(rect(rx_x + 80, rx_y + 55, 160, 65, fill="#ebf5fb", stroke="#3498db", sw=1.4, rx=6))
    frags.append(text(rx_x + 160, rx_y + 75, "Вхідний LNA", size=13, bold=True, color="#1b4f72"))
    frags.append(text(rx_x + 160, rx_y + 92, "P₁dB ≈ -10 dBm", size=11, bold=True, color="#c0392b"))
    frags.append(text(rx_x + 160, rx_y + 107, "IIP3 ≈ 0 dBm", size=10, color=MUTED))

    # Наслідки насичення
    frags.append(rect(rx_x + 20, rx_y + 135, 220, 105, fill="#fdecea", stroke="#e74c3c", sw=1.2, rx=6))
    frags.append(text(rx_x + 130, rx_y + 155, "Наслідки самоперешкоди:", size=11, bold=True, color="#922b21"))
    frags.append(text(rx_x + 130, rx_y + 173, "1. Насичення LNA: Gain падає на >15 dB", size=10, color="#c0392b"))
    frags.append(text(rx_x + 130, rx_y + 191, "2. Зворотне змішування шуму (Reciprocal Mix)", size=10, color="#c0392b"))
    frags.append(text(rx_x + 130, rx_y + 209, "3. Інтермодуляція IMD3 прямо в смугу RX", size=10, color="#c0392b"))
    frags.append(text(rx_x + 130, rx_y + 227, "Підсумок: 100% втрата пакетів (PER = 1.0)", size=10, bold=True, color="#78281f"))

    # Підпис знизу
    frags.append(text(w / 2, 355, "Без часового арбітражу (PTA) або фільтрації передавач Wi-Fi засліплює сусідній LNA на тій самій платі", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "lna-blocking-mechanism.svg"), w, h, *frags)


def fig_pta_timing():
    """Часова діаграма 3-провідного апаратного арбітражу пакетів (PTA)."""
    w, h = 840, 390
    frags = []

    frags.append(text(w / 2, 26, "Часова діаграма 3-провідного апаратного арбітражу пакетів (3-Wire PTA)", size=16, bold=True))

    sig_x0 = 150
    sig_x1 = 780

    # Рівні сигналів
    signals = [
        ("COEX_REQ", "Запит каналу (BLE/Zigbee)", 70, "#2980b9"),
        ("COEX_PRI", "Пріоритет (High/Low)", 140, "#8e44ad"),
        ("COEX_GNT", "Дозвіл (Grant від Wi-Fi)", 210, "#27ae60"),
        ("RF Стан", "Активність у ефірі", 280, "#d35400"),
    ]

    for name, desc, y, col in signals:
        frags.append(text(sig_x0 - 15, y + 16, name, size=13, bold=True, color=col, anchor="end"))
        frags.append(text(sig_x0 - 15, y + 30, desc, size=9, color=MUTED, anchor="end"))
        frags.append(line(sig_x0, y + 38, sig_x1, y + 38, color="#eaeded", sw=1.0))

    # Часові інтервали:
    # 1. COEX_REQ
    req_y_low = 100
    req_y_high = 75
    p_req = f"M {sig_x0} {req_y_low} L 240 {req_y_low} L 240 {req_y_high} L 520 {req_y_high} L 520 {req_y_low} L {sig_x1} {req_y_low}"
    frags.append(f'<path d="{p_req}" fill="none" stroke="#2980b9" stroke-width="2.2"/>')

    # 2. COEX_PRI
    pri_y_low = 170
    pri_y_high = 145
    p_pri = f"M {sig_x0} {pri_y_low} L 240 {pri_y_low} L 240 {pri_y_high} L 520 {pri_y_high} L 520 {pri_y_low} L {sig_x1} {pri_y_low}"
    frags.append(f'<path d="{p_pri}" fill="none" stroke="#8e44ad" stroke-width="2.2"/>')

    # 3. COEX_GNT
    gnt_y_low = 240
    gnt_y_high = 215
    p_gnt = f"M {sig_x0} {gnt_y_low} L 290 {gnt_y_low} L 290 {gnt_y_high} L 530 {gnt_y_high} L 530 {gnt_y_low} L {sig_x1} {gnt_y_low}"
    frags.append(f'<path d="{p_gnt}" fill="none" stroke="#27ae60" stroke-width="2.2"/>')

    # 4. RF Стан
    frags.append(rect(170, 280, 70, 32, fill="#f2f4f4", stroke="#bdc3c7", sw=1.0, rx=4))
    frags.append(text(205, 300, "Wi-Fi RX", size=10, color=MUTED))

    # Захисний інтервал
    frags.append(rect(240, 280, 90, 32, fill="#fef9e7", stroke="#f39c12", sw=1.0, rx=4))
    frags.append(text(285, 296, "T_guard", size=10, bold=True, color="#b7950b"))
    frags.append(text(285, 308, "30..50 мкс", size=9, color="#7d6608"))

    # BLE активність
    frags.append(rect(330, 280, 180, 32, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(420, 296, "BLE Connection Event (RX/TX)", size=11, bold=True, color="#196f3d"))
    frags.append(text(420, 308, "Wi-Fi передавач заблоковано арбітром", size=9, color="#1e8449"))

    # Wi-Fi TX burst
    frags.append(rect(550, 280, 200, 32, fill="#fdecea", stroke="#c0392b", sw=1.5, rx=4))
    frags.append(text(650, 296, "Wi-Fi TX Burst (+20 dBm)", size=11, bold=True, color="#922b21"))
    frags.append(text(650, 308, "Передача TCP/UDP пакета", size=9, color="#b03a2e"))

    # Вертикальні лінії прив'язки
    frags.append(line(240, 60, 240, 320, color="#bdc3c7", sw=1.0, dash="3,3"))
    frags.append(line(290, 60, 290, 320, color="#bdc3c7", sw=1.0, dash="3,3"))
    frags.append(line(520, 60, 520, 320, color="#bdc3c7", sw=1.0, dash="3,3"))

    # Позначення часового бюджету арбітражу
    frags.append(arrow(240, 52, 290, 52, color="#2980b9", sw=1.2))
    frags.append(arrow(290, 52, 240, 52, color="#2980b9", sw=1.2))
    frags.append(text(265, 45, "t_req ≈ 30 мкс", size=10, bold=True, color="#2471a3"))

    frags.append(text(w / 2, 360, "PTA арбітр оцінює пріоритет (COEX_PRI) та зупиняє передавач Wi-Fi на час критичного BLE кадру", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "pta-three-wire-timing.svg"), w, h, *frags)


def fig_pcb_isolation():
    """Топологія друкованої плати колокованого пристрою: рознесення, екрани, via stitching."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 26, "Топологія друкованої плати для ізоляції колокрованих радіотрактів 2,4 ГГц", size=16, bold=True))

    # Контур плати PCB
    pcb_x = 40
    pcb_y = 55
    pcb_w = 740
    pcb_h = 320
    frags.append(rect(pcb_x, pcb_y, pcb_w, pcb_h, fill="#196f3d", stroke="#145a32", sw=3.0, rx=10))
    frags.append(text(pcb_x + 70, pcb_y + 24, "PCB FR-4 (4 шари)", size=12, bold=True, color="#a9dfbf"))

    # 1. Ліва частина: Модуль Wi-Fi + антена
    wifi_box_x = pcb_x + 30
    wifi_box_y = pcb_y + 45
    frags.append(rect(wifi_box_x, wifi_box_y, 220, 240, fill="#27ae60", stroke="#a9dfbf", sw=1.2, rx=6))

    # Металевий екран (Shield Can) над Wi-Fi SoC
    frags.append(rect(wifi_box_x + 20, wifi_box_y + 80, 180, 130, fill="#d5dbdb", stroke="#7f8c8d", sw=2.0, rx=4))
    frags.append(text(wifi_box_x + 110, wifi_box_y + 110, "Wi-Fi SoC + FEM", size=13, bold=True, color="#1b2631"))
    frags.append(text(wifi_box_x + 110, wifi_box_y + 130, "Металевий екран", size=11, color="#2c3e50"))
    frags.append(text(wifi_box_x + 110, wifi_box_y + 150, "(Shielding Can)", size=10, italic=True, color=MUTED))
    frags.append(text(wifi_box_x + 110, wifi_box_y + 180, "+20 dBm PA всередині", size=10, bold=True, color="#922b21"))

    # Антена Wi-Fi (горизонтальна орієнтація)
    ant1_x = wifi_box_x + 30
    ant1_y = wifi_box_y + 25
    frags.append(rect(ant1_x, ant1_y, 160, 30, fill="#f39c12", stroke="#b9770e", sw=1.5, rx=3))
    frags.append(text(ant1_x + 80, ant1_y + 20, "PCB Антена Wi-Fi (Поляризація H)", size=10, bold=True, color="#ffffff"))

    # 2. Центральна зона: Бар'єр перехідних отворів (Via Fence) та PTA лінії
    mid_fence_x = pcb_x + 320
    frags.append(rect(mid_fence_x - 35, pcb_y + 40, 70, 250, fill="#1e8449", stroke="#27ae60", sw=1.0, rx=4))
    frags.append(text(mid_fence_x, pcb_y + 60, "Via Fence", size=11, bold=True, color="#f9e79f"))
    frags.append(text(mid_fence_x, pcb_y + 75, "s ≤ λ/10 ≈ 5 мм", size=9, color="#fcf3cf"))

    # Подвійний ряд земляних via
    for vy in range(pcb_y + 95, pcb_y + 275, 18):
        frags.append(circle(mid_fence_x - 12, vy, 4, fill="#f1c40f", stroke="#b7950b", sw=1.0))
        frags.append(circle(mid_fence_x + 12, vy, 4, fill="#f1c40f", stroke="#b7950b", sw=1.0))

    # Лінії PTA шини через бар'єр
    frags.append(line(wifi_box_x + 200, pcb_y + 200, pcb_x + 470, pcb_y + 200, color="#f39c12", sw=1.8))
    frags.append(line(wifi_box_x + 200, pcb_y + 215, pcb_x + 470, pcb_y + 215, color="#9b59b6", sw=1.8))
    frags.append(line(wifi_box_x + 200, pcb_y + 230, pcb_x + 470, pcb_y + 230, color="#3498db", sw=1.8))
    frags.append(text(mid_fence_x, pcb_y + 190, "3-провідний PTA", size=10, bold=True, color="#ffffff"))

    # 3. Права частина: BLE / Zigbee SoC + вертикальна антена
    ble_box_x = pcb_x + 450
    ble_box_y = pcb_y + 45
    frags.append(rect(ble_box_x, ble_box_y, 250, 240, fill="#27ae60", stroke="#a9dfbf", sw=1.2, rx=6))

    # Металевий екран над BLE / Zigbee
    frags.append(rect(ble_box_x + 20, ble_box_y + 80, 140, 130, fill="#d5dbdb", stroke="#7f8c8d", sw=2.0, rx=4))
    frags.append(text(ble_box_x + 90, ble_box_y + 110, "BLE / 802.15.4", size=13, bold=True, color="#1b2631"))
    frags.append(text(ble_box_x + 90, ble_box_y + 130, "SoC (LNA RX)", size=11, color="#2c3e50"))
    frags.append(text(ble_box_x + 90, ble_box_y + 150, "Shielding Can", size=10, italic=True, color=MUTED))
    frags.append(text(ble_box_x + 90, ble_box_y + 180, "-95 dBm чутливість", size=10, bold=True, color="#1e8449"))

    # Антена BLE (вертикальна орієнтація - ортогональна поляризація 90°)
    ant2_x = ble_box_x + 185
    ant2_y = ble_box_y + 45
    frags.append(rect(ant2_x, ant2_y, 35, 170, fill="#e67e22", stroke="#a04000", sw=1.5, rx=3))
    frags.append(mtext(ant2_x + 18, ant2_y + 35, "Антена\nBLE\n(Поляризація\nвертикальна\n90°)", size=9, bold=True, color="#ffffff"))

    # Рознесення антен d >= 40 мм
    frags.append(arrow(ant1_x + 160, ant1_y + 15, ant2_x, ant1_y + 15, color="#f1c40f", sw=1.5))
    frags.append(arrow(ant2_x, ant1_y + 15, ant1_x + 160, ant1_y + 15, color="#f1c40f", sw=1.5))
    frags.append(text((ant1_x + 160 + ant2_x) / 2, ant1_y + 8, "Рознос d ≥ 40 мм (Ізоляція > 25 dB)", size=10, bold=True, color="#f9e79f"))

    # Підпис внизу
    frags.append(text(w / 2, 395, "Ортогональна орієнтація антен (90°), захисний паркан із via та окремі екрани забезпечують >30 дБ розв'язки", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "pcb-coex-isolation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_freq_overlap()
    fig_lna_blocking()
    fig_pta_timing()
    fig_pcb_isolation()
    print("All figures generated successfully.")
