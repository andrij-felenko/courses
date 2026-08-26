# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_tools_hierarchy():
    """Ієрархія інструментів інспекції каналу: від фізичних ліній до прикладного рівня Wireshark."""
    W, H = 960, 460
    p = []

    layers = [
        ("Прикладний та мережевий (App / Net)", "Wireshark / extcap / TCP / UDP / TLS / MQTT",
         "Розбір семантики протоколів, дерева полів, часові ряди пакетів", "#eaf4fd", NEG),
        ("Вбудоване системне логування (MCU Tracing)", "DMA Ring Buffer / RTT / SWO / Hex Dump",
         "Внутрішній стан автоматів, таймстеми подій, сирі RX/TX буфери", "#eef8f0", FIELD),
        ("Радіочастотний рівень (RF Over-The-Air)", "nRF Sniffer (BLE / 802.15.4) / SDR (LoRa / FSK)",
         "Ефірні пакети, channel hopping, рівень RSSI, помилки CRC в ефірі", "#fdf4e8", "#d97706"),
        ("Фізичний та канальний дріт (PHY / Bus)", "Логічний аналізатор (Saleae/Sigrok) / Осцилограф",
         "Форма фронтів, бітові таймінги, апаратний UART/SPI/I2C/CAN детекшн", "#fbebee", POS),
    ]

    lw = 620
    lh = 80
    x0 = 40
    y0 = 60

    for i, (title, tools, desc, fill, stroke) in enumerate(layers):
        yy = y0 + i * 95
        p.append(rect(x0, yy, lw, lh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x0 + 20, yy + 25, title, size=13, color=stroke, anchor="start", bold=True))
        p.append(text(x0 + 20, yy + 47, "Інструменти: " + tools, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x0 + 20, yy + 67, desc, size=10.5, color=MUTED, anchor="start"))

    # Права панель: порівняння параметрів вторгнення та видимості
    rx = 690
    rw = 230
    p.append(rect(rx, y0, rw, 365, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, y0 + 26, "Характеристики інспекції", size=13, color=INK, bold=True))

    p.append(line(rx + 15, y0 + 40, rx + rw - 15, y0 + 40, color="#d1d5db", sw=1))

    traits = [
        ("Видимість даних:", "Від бітів і напруги до семантики полів"),
        ("Вторгнення (Invasiveness):", "0% (осцилограф/снифер)"),
        ("", "до 1–3% CPU (DMA логер)"),
        ("Точність міток часу:", "Наносекунди (PHY логіка)"),
        ("", "до мікросекунд (Wireshark PCAP)"),
        ("Складність аналізу:", "Від ручного бітового пошуку"),
        ("", "до автоматичних Lua-фільтрів"),
    ]

    ty = y0 + 65
    for lab, val in traits:
        if lab:
            p.append(text(rx + 15, ty, lab, size=11, color=INK, anchor="start", bold=True))
            ty += 18
            p.append(text(rx + 15, ty, val, size=10, color=MUTED, anchor="start"))
            ty += 24
        else:
            p.append(text(rx + 15, ty - 6, val, size=10, color=MUTED, anchor="start"))
            ty += 18

    render(os.path.join(OUT, "tools-layer-hierarchy.svg"), W, H, *p,
           title="Рівні інспекції каналу: вибір точки спостереження та інструменту")


def fig_wireshark_lua():
    """Конвеєр обробки пакетів кастомним Wireshark Lua Dissector."""
    W, H = 960, 430
    p = []

    steps = [
        ("1. Захоплення потоку", "extcap / UART pipe / UDP\nСирий буфер байтів (TVB)", "#eef2ff", NEG),
        ("2. Розбір заголовка", "Magic 0xAA 0x55, Seq, Len, Cmd\nПеревірка мінімальної довжини", "#f0fdf4", FIELD),
        ("3. Дерево та поля", "ProtoField: uint16, enum, bits\nДодавання гілок у Protocol Tree", "#fef3c7", "#d97706"),
        ("4. Валідація і статус", "Перевірка CRC16, ExpertInfo\nКолонки Protocol та Info", "#fee2e2", POS),
    ]

    bw = 200
    bh = 100
    gap = 35
    x_start = 35
    cy = 80

    for i, (stitle, sdesc, fill, stroke) in enumerate(steps):
        x = x_start + i * (bw + gap)
        p.append(rect(x, cy, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + bw / 2, cy + 24, stitle, size=12, color=stroke, bold=True))
        p.append(mtext(x + bw / 2, cy + 52, sdesc, size=10, color=INK, lh=1.35))
        if i < 3:
            p.append(arrow(x + bw + 4, cy + bh / 2, x + bw + gap - 4, cy + bh / 2, color=LINE, sw=2))

    # Нижня частина: структура кадру в буфері TVB
    frame_y = 230
    p.append(rect(35, frame_y, 890, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(480, frame_y + 24, "Структура буфера TVB (Testy Virtual Buffer) та проекція полів Lua", size=13, color=INK, bold=True))

    fields = [
        ("PREAMBLE", "2 байти\n0xAA 0x55", 100, "#e0e7ff"),
        ("SEQ_NUM", "2 байти\nuint16 (LE)", 100, "#dbeafe"),
        ("CMD_ID", "1 байт\nenum opcode", 95, "#ccfbf1"),
        ("PAYLOAD_LEN", "2 байти\nдовжина N", 105, "#fef08a"),
        ("PAYLOAD DATA (N байтів)", "Телеметрія, координати, статус, прапорці стану", 320, "#dcfce7"),
        ("CRC16", "2 байти\nCCITT", 95, "#fed7aa"),
    ]

    fx = 55
    fy = frame_y + 48
    fh = 75

    for fname, fdesc, fw, ffill in fields:
        p.append(rect(fx, fy, fw, fh, fill=ffill, stroke=LINE, sw=1.2, rx=5))
        p.append(text(fx + fw / 2, fy + 22, fname, size=10.5, color=INK, bold=True))
        p.append(mtext(fx + fw / 2, fy + 44, fdesc, size=9.5, color=MUTED, lh=1.25))
        fx += fw + 8

    render(os.path.join(OUT, "wireshark-lua-pipeline.svg"), W, H, *p,
           title="Конвеєр розбору бінарного кадру в Wireshark Lua Dissector")


def fig_mcu_dma_buffer():
    """Архітектура неблокуючого логування трафіку на мікроконтролері з кільцевим DMA буфером."""
    W, H = 960, 440
    p = []

    # Ліва колонка: апаратні інтерфейси зв'язку
    p.append(rect(40, 70, 220, 320, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(150, 95, "Апаратні шини МК", size=13, color=INK, bold=True))

    buses = [
        ("UART RX / TX", "Основний лінк даних", "#e0e7ff"),
        ("SPI / I2C", "Датчики та радіочипи", "#fef3c7"),
        ("CAN / RS-485", "Промислова польова шина", "#fee2e2"),
    ]
    for i, (bname, bsub, bcol) in enumerate(buses):
        by = 120 + i * 85
        p.append(rect(55, by, 190, 65, fill=bcol, stroke=LINE, sw=1.2, rx=6))
        p.append(text(150, by + 24, bname, size=12, color=INK, bold=True))
        p.append(text(150, by + 46, bsub, size=10, color=MUTED))

    # Стрілки в DMA модуль
    p.append(arrow(265, 150, 335, 150, color=FIELD, sw=2))
    p.append(arrow(265, 235, 335, 200, color=FIELD, sw=2))
    p.append(arrow(265, 320, 335, 250, color=FIELD, sw=2))

    # Центральна частина: Кільцевий буфер DMA в RAM
    p.append(rect(340, 70, 280, 320, fill="#eef8f0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(480, 95, "Zero-Copy RAM Ring Buffer", size=13, color=FIELD, bold=True))
    p.append(text(480, 118, "Захоплення без блокування CPU", size=10.5, color=MUTED))

    # Комірки буфера
    slots = [
        ("Кадр #1 [TX]", "124.050 ms · 18 байт · OK", "#dcfce7"),
        ("Кадр #2 [RX]", "124.082 ms · 64 байти · OK", "#dcfce7"),
        ("Кадр #3 [TX]", "124.110 ms · 12 байт · OK", "#dcfce7"),
        ("Вільний слот (HEAD)", "Запис нових байтів по DMA", "#ffffff"),
    ]
    for i, (shead, ssub, scol) in enumerate(slots):
        sy = 140 + i * 58
        p.append(rect(355, sy, 250, 48, fill=scol, stroke=FIELD, sw=1.2, rx=5))
        p.append(text(480, sy + 20, shead, size=11, color=INK, bold=True))
        p.append(text(480, sy + 38, ssub, size=9.5, color=MUTED))

    # Стрілка назовні
    p.append(arrow(625, 230, 695, 230, color=NEG, sw=2))

    # Права частина: Канали відвантаження траси
    p.append(rect(700, 70, 220, 320, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(810, 95, "Вивід на хост (ПК)", size=13, color=NEG, bold=True))

    out_channels = [
        ("Debug UART DMA", "Окремий порт налагодження", "#e0f2fe"),
        ("SEGGER RTT", "SWD прямий доступ до RAM", "#e0e7ff"),
        ("SWO / ITM", "Апаратна траса Cortex-M", "#f1f5f9"),
    ]
    for i, (oname, osub, ocol) in enumerate(out_channels):
        oy = 120 + i * 85
        p.append(rect(715, oy, 190, 65, fill=ocol, stroke=NEG, sw=1.2, rx=6))
        p.append(text(810, oy + 24, oname, size=12, color=INK, bold=True))
        p.append(text(810, oy + 46, osub, size=10, color=MUTED))

    render(os.path.join(OUT, "mcu-dma-log-buffer.svg"), W, H, *p,
           title="Архітектура неблокуючого логування трафіку на базі кільцевого DMA-буфера")


def fig_tls_debug():
    """Послідовність налагодження проблем TLS на вбудованому пристрої."""
    W, H = 960, 460
    p = []

    # Кроки рукостискання та точки відмови
    flow = [
        ("1. ClientHello", "Пристрій -> Сервер\nШифронабори, версія TLS, SNI",
         "Alert: Handshake Failure\n(Немає спільного шифронабору)", "#fee2e2"),
        ("2. ServerHello & Cert", "Сервер -> Пристрій\nСертифікат X.509, ланцюг CA",
         "Alert: Bad Certificate / Expired\n(Зсув годинника або відсутній CA)", "#fee2e2"),
        ("3. Key Exchange", "Обмін ключами ECDHE / RSA\nГенерація Pre-Master Secret",
         "Out of Memory / Timeout\n(Брак RAM під криптоконтекст)", "#fef3c7"),
        ("4. Encrypted Channel", "Завершення рукостискання\nЗашифрований потік додатку",
         "Розшифрування через SSLKEYLOGFILE\n(Аналіз незахищених даних у Wireshark)", "#dcfce7"),
    ]

    bw = 410
    bh = 78
    x_left = 50
    x_right = 500
    y_start = 65

    for i, (step_title, step_desc, diag_desc, diag_col) in enumerate(flow):
        yy = y_start + i * 95
        # Ліва колонка: фаза протоколу
        p.append(rect(x_left, yy, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
        p.append(text(x_left + 15, yy + 24, step_title, size=12, color=INK, anchor="start", bold=True))
        p.append(mtext(x_left + 15, yy + 46, step_desc, size=10, color=MUTED, anchor="start", lh=1.3))

        # Стрілка між фазою та точкою діагностики
        p.append(arrow(x_left + bw + 4, yy + bh / 2, x_right - 4, yy + bh / 2, color=LINE, sw=1.8))

        # Права колонка: типовий збій або метод інспекції
        p.append(rect(x_right, yy, bw, bh, fill=diag_col, stroke=LINE, sw=1.4, rx=6))
        p.append(text(x_right + 15, yy + 24, "Діагностика Wireshark:", size=11, color=INK, anchor="start", bold=True))
        p.append(mtext(x_right + 15, yy + 46, diag_desc, size=10, color=INK, anchor="start", lh=1.3))

    render(os.path.join(OUT, "tls-debug-flow.svg"), W, H, *p,
           title="Фази рукостискання TLS та локалізація помилок сертифікатів і пам'яті")


if __name__ == "__main__":
    fig_tools_hierarchy()
    fig_wireshark_lua()
    fig_mcu_dma_buffer()
    fig_tls_debug()
    print("OK: 4 figures generated in ->", OUT)
