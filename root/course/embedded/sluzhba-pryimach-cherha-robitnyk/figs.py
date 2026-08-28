# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pipeline_architecture():
    """Схема тришарового конвеєра прийому: Приймач -> Демпферна черга -> Пул робітників."""
    W, H = 860, 470
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Архітектура конвеєра прийому телеметрії (Ingestion Pipeline)", size=16, bold=True))

    # Стовпець 1: Джерела (Вузли / Шлюзи)
    p.append(rect(20, 60, 165, 365, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(102, 85, "Джерела трафіку", size=14, bold=True, color=INK))
    p.append(text(102, 105, "50 000+ вузлів / шлюзів", size=11, color=MUTED))

    # Блоки клієнтів
    p.append(fitbox(35, 130, 135, 50, "Вузол ESP32\nMQTT QoS 0 / 1", size=12, fill="#ffffff", stroke=LINE))
    p.append(fitbox(35, 195, 135, 50, "IoT-шлюз\nTCP / Binary Frames", size=12, fill="#ffffff", stroke=LINE))
    p.append(fitbox(35, 260, 135, 50, "HTTP REST / CoAP\nПакети телеметрії", size=12, fill="#ffffff", stroke=LINE))
    p.append(fitbox(35, 335, 135, 65, "Піковий залп\n(Thundering Herd)\n100 000 кадр/с", size=11, fill="#fdecea", stroke=POS, bold=True))

    # Стрілка від джерел до Приймача
    p.append(arrow(185, 225, 220, 225, color=LINE, sw=2))

    # Стовпець 2: Швидкий приймач (Fast Ingest / Receiver)
    p.append(rect(225, 60, 175, 365, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(312, 85, "1. Швидкий приймач", size=14, bold=True, color=NEG))
    p.append(text(312, 105, "Non-blocking epoll Loop", size=11, color=MUTED))

    p.append(fitbox(240, 130, 145, 55, "Мережевий сокет\nO_NONBLOCK · I/O loop", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(240, 200, 145, 65, "Маркування кадру\nМітка t_recv · peer_id\nНуль алокацій пам'яті", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(240, 280, 145, 60, "Захист входу\nToken Bucket лімітер\nКонтроль затримки < 5 мкс", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(240, 355, 145, 50, "push(raw_packet)\nНеблокувальний запис", size=11, fill="#ffffff", stroke=NEG, bold=True))

    # Стрілка від Приймача до Черги
    p.append(arrow(400, 225, 435, 225, color=LINE, sw=2))

    # Стовпець 3: Демпферна черга (Shock-Absorbing Queue)
    p.append(rect(440, 60, 185, 365, fill="#fef9e7", stroke="#d4ac0d", sw=2, rx=8))
    p.append(text(532, 85, "2. Демпферна черга", size=14, bold=True, color="#7d6608"))
    p.append(text(532, 105, "RingBuffer / Redis / IPC", size=11, color=MUTED))

    p.append(fitbox(455, 130, 155, 60, "Кільцевий буфер FIFO\nФіксована місткість K\nБезпечна черга SPSC/MPMC", size=11, fill="#ffffff", stroke="#d4ac0d"))
    p.append(fitbox(455, 205, 155, 65, "Контроль ватерпостів\nHigh Watermark (85%)\nLow Watermark (60%)", size=11, fill="#ffffff", stroke="#d4ac0d"))
    p.append(fitbox(455, 285, 155, 55, "Політика скидання\nDrop Oldest / Drop Tail\nЗахист від вичерпання RAM", size=11, fill="#ffffff", stroke="#d4ac0d"))
    p.append(fitbox(455, 355, 155, 50, "Зворотний тиск\n(Backpressure Signal)", size=11, fill="#fdecea", stroke=POS, bold=True))

    # Зворотний тиск (пунктирна стрілка назад від Черги до Приймача)
    p.append(line(532, 405, 532, 440, color=POS, sw=1.8, dash="4 3"))
    p.append(line(532, 440, 312, 440, color=POS, sw=1.8, dash="4 3"))
    p.append(arrow(312, 440, 312, 425, color=POS, sw=1.8))
    p.append(text(422, 455, "Пауза читання сокетів при W_high", size=11, color=POS, bold=True))

    # Стрілка від Черги до Воркерів
    p.append(arrow(625, 225, 660, 225, color=LINE, sw=2))

    # Стовпець 4: Пул робітників (Worker Pool)
    p.append(rect(665, 60, 175, 365, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(752, 85, "3. Пул робітників", size=14, bold=True, color=FIELD))
    p.append(text(752, 105, "N паралельних воркерів", size=11, color=MUTED))

    p.append(fitbox(680, 130, 145, 55, "Розбір кадру\nCRC16 · Ендіанність\nДвійкове розпакування", size=11, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(680, 195, 145, 55, "Час і валідація\nЗведення t_dev і t_recv\nФізичні межі датчиків", size=11, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(680, 260, 145, 55, "Нормалізація DTO\nКанонічний формат подій\nЗбагачення метаданими", size=11, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(680, 325, 145, 80, "Пакетний запис\nМікробатчі (500 шт)\nДо Сховища / TSDB", size=11, fill="#ffffff", stroke=FIELD, bold=True))

    render(os.path.join(IMG, "pipeline-architecture.svg"), W, H, *p)


def fig_backpressure_watermarks():
    """Схема станів черги: порожня, норма, ватерпости, зворотний тиск і скидання."""
    W, H = 860, 420
    p = []

    p.append(text(W / 2, 28, "Динаміка заповнення черги та механізм зворотного тиску", size=16, bold=True))

    # Велика вертикальна труба-резервуар черги
    qx, qy, qw, qh = 60, 75, 160, 300
    p.append(rect(qx, qy, qw, qh, fill="#ffffff", stroke=LINE, sw=2, rx=6))

    # Зони заповнення
    # 1. Зона скидання (85% .. 100%) -> висота 45px
    p.append(rect(qx + 2, qy + 2, qw - 4, qh * 0.15, fill="#fdecea", stroke="none"))
    # 2. Зона зворотного тиску (60% .. 85%) -> висота 75px
    p.append(rect(qx + 2, qy + qh * 0.15 + 2, qw - 4, qh * 0.25, fill="#fef9e7", stroke="none"))
    # 3. Зелена зона (0% .. 60%) -> висота 180px
    p.append(rect(qx + 2, qy + qh * 0.40 + 2, qw - 4, qh * 0.60 - 4, fill="#eafaf0", stroke="none"))

    # Позначки рівнів (горизонтальні лінії)
    # 100% Місткість
    p.append(line(qx, qy, qx + qw, qy, color=POS, sw=2))
    p.append(text(qx + qw + 15, qy + 5, "100%  Місткість K", size=12, color=POS, anchor="start", bold=True))

    # High Watermark (85%)
    y_high = qy + qh * 0.15
    p.append(line(qx, y_high, qx + qw, y_high, color="#d4ac0d", sw=2, dash="5 4"))
    p.append(text(qx + qw + 15, y_high + 5, "85%  W_high", size=12, color="#7d6608", anchor="start", bold=True))

    # Low Watermark (60%)
    y_low = qy + qh * 0.40
    p.append(line(qx, y_low, qx + qw, y_low, color=FIELD, sw=2, dash="5 4"))
    p.append(text(qx + qw + 15, y_low + 5, "60%  W_low", size=12, color=FIELD, anchor="start", bold=True))

    # 0% Порожня
    p.append(text(qx + qw + 15, qy + qh - 5, "0%  Порожня", size=12, color=MUTED, anchor="start"))

    # Вхідний і вихідний потік
    p.append(arrow(qx + qw / 2, 45, qx + qw / 2, qy - 2, color=NEG, sw=2.5))
    p.append(text(qx + qw / 2, 40, "Вхід λ(t)", size=12, color=NEG, bold=True))

    p.append(arrow(qx + qw / 2, qy + qh + 2, qx + qw / 2, qy + qh + 35, color=FIELD, sw=2.5))
    p.append(text(qx + qw / 2, qy + qh + 30, "Вихід μ", size=12, color=FIELD, bold=True))

    # Пояснювальні картки дій праворуч
    card_x, card_w = 380, 440

    # Картка 1: Зона червона (Критичне переповнення)
    p.append(rect(card_x, 75, card_w, 80, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(card_x + 15, 98, "Рівень > W_high: Скидання (Drop Policies)", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(card_x + 15, 120, "• Drop Oldest: витіснення застарілої телеметрії", size=11, color=INK, anchor="start"))
    p.append(text(card_x + 15, 138, "• Лічильник drops_total++ для моніторингу черги", size=11, color=MUTED, anchor="start"))

    # Картка 2: Зона жовта (Зворотний тиск)
    p.append(rect(card_x, 175, card_w, 95, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    p.append(text(card_x + 15, 198, "Рівень між W_low та W_high: Зворотний тиск (Backpressure)", size=13, bold=True, color="#7d6608", anchor="start"))
    p.append(text(card_x + 15, 220, "• Приймач знімає EPOLLIN з дескрипторів сокетів", size=11, color=INK, anchor="start"))
    p.append(text(card_x + 15, 238, "• TCP Window звужується до 0 -> затримка на шлюзі", size=11, color=INK, anchor="start"))
    p.append(text(card_x + 15, 256, "• Локальне буферизування на периферійному шлюзі", size=11, color=MUTED, anchor="start"))

    # Картка 3: Зона зелена (Штатний режим)
    p.append(rect(card_x, 290, card_w, 85, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(card_x + 15, 313, "Рівень < W_low: Штатна безперебійна робота", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(card_x + 15, 335, "• Повне відновлення обробки мережевих подій", size=11, color=INK, anchor="start"))
    p.append(text(card_x + 15, 353, "• Нульова затримка доставки телеметрії (P99 < 15 мс)", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "backpressure-watermarks.svg"), W, H, *p)


def fig_frame_normalization_flow():
    """Схема процесу нормалізації: Двійковий сирий кадр -> Валідація -> Канонічна DTO подія."""
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 28, "Етапи розбору та нормалізації двійкового кадру телеметрії", size=16, bold=True))

    # Блок 1: Сирий двійковий кадр (Raw Binary Frame)
    x1, y1, w1, h1 = 30, 70, 205, 280
    p.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(x1 + w1 / 2, y1 + 25, "1. Сирий кадр (24 байти)", size=13, bold=True, color=INK))

    p.append(fitbox(x1 + 15, y1 + 45, 175, 32, "Magic: 0xAA 0x55 (2 B)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(x1 + 15, y1 + 84, 175, 32, "Device ID: 0x000104A2 (4 B)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(x1 + 15, y1 + 123, 175, 32, "Uptime ms: 1 482 910 (4 B)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(x1 + 15, y1 + 162, 175, 32, "Raw Temp: 2345 (int16)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(x1 + 15, y1 + 201, 175, 32, "Raw Humid: 5820 (uint16)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(x1 + 15, y1 + 240, 175, 32, "Flags & CRC16 (4 B)", size=11, fill="#ffffff", stroke=LINE))

    p.append(arrow(x1 + w1, y1 + h1 / 2, x1 + w1 + 35, y1 + h1 / 2, color=LINE, sw=2))

    # Блок 2: Конвеєр перевірки та перетворення воркером
    x2, y2, w2, h2 = 270, 70, 260, 280
    p.append(rect(x2, y2, w2, h2, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(x2 + w2 / 2, y2 + 25, "2. Обробка у воркері", size=13, bold=True, color=NEG))

    p.append(fitbox(x2 + 15, y2 + 45, 230, 38, "Перевірка CRC16 (Табличний алгоритм)\nЗахист від спотворень каналу", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(x2 + 15, y2 + 91, 230, 38, "Зведення годинника (Clock Alignment)\nt_event = t_recv − (t_now_up − t_up)", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(x2 + 15, y2 + 137, 230, 38, "Масштабування фіксованої коми\nTemp = 2345 · 0.01 = 23.45 °C", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(x2 + 15, y2 + 183, 230, 38, "Перевірка фізичних діапазонів\n-40 ≤ T ≤ 85 °C · 0 ≤ H ≤ 100%", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(x2 + 15, y2 + 229, 230, 35, "Збагачення з кешу (Site, Room, Calib)", size=11, fill="#ffffff", stroke=NEG))

    p.append(arrow(x2 + w2, y2 + h2 / 2, x2 + w2 + 35, y2 + h2 / 2, color=LINE, sw=2))

    # Блок 3: Канонічна подія (Structured Event / DTO)
    x3, y3, w3, h3 = 565, 70, 245, 280
    p.append(rect(x3, y3, w3, h3, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(x3 + w3 / 2, y3 + 25, "3. Нормалізована подія (DTO)", size=13, bold=True, color=FIELD))

    dto_code = (
        '{\n'
        '  "device_id": "esp32-000104a2",\n'
        '  "timestamp": "2026-08-27T06:15:00Z",\n'
        '  "telemetry": {\n'
        '    "temperature_c": 23.45,\n'
        '    "humidity_pct": 58.2,\n'
        '    "battery_v": 3.82\n'
        '  },\n'
        '  "quality": "VALID",\n'
        '  "ingest_lag_ms": 12\n'
        '}'
    )
    p.append(fitbox(x3 + 15, y3 + 45, 215, 220, dto_code, size=11, fill="#ffffff", stroke=FIELD, color="#1e3a8a"))

    render(os.path.join(IMG, "frame-normalization-flow.svg"), W, H, *p)


if __name__ == '__main__':
    fig_pipeline_architecture()
    fig_backpressure_watermarks()
    fig_frame_normalization_flow()
    print("Figures generated successfully.")
