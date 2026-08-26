# -*- coding: utf-8 -*-
"""Фігури для статті mitka-chasu.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_server_vs_edge_timestamp():
    """Порівняння спотворення фізичної картини при Server Ingest Time проти Edge Event Time."""
    W, H = 840, 560
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    p.append(text(W / 2, 26, "Спотворення фізичної картини: час сервера проти часу пристрою", size=15, color=INK, bold=True))

    # Секція 1: Фізичний процес та накопичення в офлайні
    p.append(rect(30, 45, 780, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(420, 68, "Реальний фізичний процес на об'єкті (6 годин обриву зв'язку)", size=13, color="#334155", bold=True))

    # Шкала реального часу
    p.append(line(70, 115, 750, 115, color=LINE, sw=2))
    p.append(arrow(750, 115, 765, 115, color=LINE, sw=2))
    p.append(text(765, 135, "t (фізичний)", size=11, color=LINE, italic=True))

    event_times = [
        ("10:00", 110, "P = 4.2 бар"),
        ("11:00", 220, "P = 3.8 бар"),
        ("12:00", 330, "P = 3.1 бар"),
        ("13:00", 440, "P = 2.5 бар"),
        ("14:00", 550, "P = 2.1 бар"),
        ("15:00", 660, "P = 1.9 бар"),
    ]

    for label, x, val in event_times:
        p.append(circle(x, 115, 5, fill=FIELD, stroke=LINE, sw=1.5))
        p.append(text(x, 100, label, size=11, color="#1e293b", bold=True))
        p.append(text(x, 135, val, size=10, color="#475569"))

    p.append(rect(80, 150, 660, 24, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(410, 166, "Зв'язок відсутній: пристрій вимірює тиск і накопичує 6 точок у локальній Flash-пам'яті", size=10, color="#92400e"))

    # Секція 2: Помилковий варіант — Ingest Timestamp
    p.append(rect(30, 200, 780, 160, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(420, 222, "Варіант А: Сервер ставить мітку надходження (Server Ingestion Timestamp)", size=13, color=POS, bold=True))

    p.append(line(70, 270, 750, 270, color=LINE, sw=2))
    p.append(arrow(750, 270, 765, 270, color=LINE, sw=2))
    p.append(text(765, 290, "t (сервер)", size=11, color=LINE, italic=True))

    # Скупчення точок о 16:00
    p.append(rect(520, 240, 220, 60, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(630, 256, "16:00:00 (Пакетний скид)", size=11, color=POS, bold=True))

    for idx, (lbl, orig_x, val) in enumerate(event_times):
        dot_x = 550 + idx * 28
        p.append(circle(dot_x, 270, 4, fill=POS, stroke=LINE, sw=1.2))
        p.append(text(dot_x, 288, f"+{idx*8}мс", size=9, color=POS))

    p.append(text(280, 260, "6 годин тиші в базі даних (удавані нулі)", size=11, color="#7f1d1d"))
    p.append(text(280, 280, "Потім 6 точок за 40 мілісекунд", size=11, color=POS, bold=True))

    p.append(rect(50, 315, 740, 32, fill="#ffffff", stroke=POS, sw=1.0, rx=4))
    p.append(text(420, 335, "НАСЛІДОК: похідна dP/dt штучно зростає в тисячі разів -> помилкова тривога «гідроудар», втрата хронології", size=10.5, color=POS, bold=True))

    # Секція 3: Правильний варіант — Dual / Edge Timestamp
    p.append(rect(30, 375, 780, 165, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(420, 397, "Варіант Б: Бортова мітка події (Edge Event Timestamp) + Серверний аудит", size=13, color=FIELD, bold=True))

    p.append(line(70, 445, 750, 445, color=LINE, sw=2))
    p.append(arrow(750, 445, 765, 445, color=LINE, sw=2))
    p.append(text(765, 465, "t (подій)", size=11, color=LINE, italic=True))

    for label, x, val in event_times:
        p.append(circle(x, 445, 5, fill=FIELD, stroke=LINE, sw=1.5))
        p.append(text(x, 430, label, size=11, color=FIELD, bold=True))
        p.append(text(x, 465, val, size=10, color="#1e293b"))

    p.append(rect(50, 490, 740, 38, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(420, 506, "РЕЗУЛЬТАТ: Точки лягають на реальні моменти 10:00..15:00. Графік плавний і достовірний.", size=10.5, color=FIELD, bold=True))
    p.append(text(420, 520, "Сервер додатково фіксує ingest_time=16:00:00 лише для аудиту доставки мережею.", size=10, color="#475569"))

    render(os.path.join(OUT, "server-vs-edge-timestamp.svg"), W, H, *p)


def fig_dual_timestamp_pipeline():
    """Архітектурний тракт подвійних часових міток від сенсора до аналітики."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Тракт подвійних часових міток: розведення семантики Event Time та Ingestion Time", size=14, color=INK, bold=True))

    blocks = [
        ("1. Бортовий сенсор", "ADC / I2C заміри\nАпаратний таймер / RTC\nФіксація event_time\nПрапорці якості часу", 40, 70, 160, 110, "#e0f2fe", "#0284c7"),
        ("2. Офлайн-буфер", "Кільцевий Flash / RAM\nЗбереження кортежів\n(event_time, value)\nБез зміни мітки", 240, 70, 160, 110, "#f1f5f9", "#475569"),
        ("3. Шлюз / Gateway", "Ретрансляція пакетів\nДодавання gateway_time\nОцінка локальної черги\nБуферизація лінка", 440, 70, 160, 110, "#fef3c7", "#d97706"),
        ("4. Ingestion Service", "Прийом MQTT / HTTP\nФіксація ingest_time\n(NTP / PTP точний час)\nРозрахунок latency", 640, 70, 160, 110, "#f3e8fd", "#7e22ce"),
    ]

    for title, desc, bx, by, bw, bh, fcol, scol in blocks:
        p.append(rect(bx, by, bw, bh, fill=fcol, stroke=scol, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, by + 20, title, size=11.5, color=scol, bold=True))
        p.append(mtext(bx + bw / 2, by + 42, desc, size=9.5, color="#1e293b", lh=1.3))

    # Стрілки між блоками 1-4
    p.append(arrow(200, 125, 235, 125, color="#0284c7", sw=1.8))
    p.append(arrow(400, 125, 435, 125, color="#475569", sw=1.8))
    p.append(arrow(600, 125, 635, 125, color="#d97706", sw=1.8))

    # Стрілка вниз до СУБД
    p.append(arrow(720, 185, 720, 230, color="#7e22ce", sw=2.0))
    p.append(text(720, 215, "Запис у Time-Series DB", size=10, color="#7e22ce", bold=True, anchor="middle"))

    # Блок 5: СУБД та Сховище (TimescaleDB / ClickHouse / InfluxDB)
    p.append(rect(40, 240, 760, 115, fill="#ecfdf5", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(420, 264, "5. База даних часових рядів (Time-Series Database)", size=13, color=FIELD, bold=True))

    col_w = 345
    # Ліва частина СУБД: Індексація
    p.append(rect(55, 280, col_w, 62, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(55 + col_w / 2, 298, "Індекс первинного ключа: event_time", size=11, color=FIELD, bold=True))
    p.append(text(55 + col_w / 2, 318, "Забезпечує правильний хронологічний порядок", size=9.5, color="#334155"))
    p.append(text(55 + col_w / 2, 332, "Фізично точні графіки, тренди, похідні, FFT", size=9.5, color="#334155"))

    # Права частина СУБД: Партиціювання
    p.append(rect(435, 280, col_w, 62, fill="#ffffff", stroke="#7e22ce", sw=1.0, rx=4))
    p.append(text(435 + col_w / 2, 298, "Партиціювання та TTL: ingest_time", size=11, color="#7e22ce", bold=True))
    p.append(text(435 + col_w / 2, 318, "Швидкий запис пачками (Append-only LSM)", size=9.5, color="#334155"))
    p.append(text(435 + col_w / 2, 332, "Аудит доставки, метрики затримок мережі (SLA)", size=9.5, color="#334155"))

    # Нижня частина: Споживачі даних
    p.append(arrow(227, 360, 227, 395, color=FIELD, sw=1.8))
    p.append(arrow(607, 360, 607, 395, color="#7e22ce", sw=1.8))

    p.append(rect(55, 400, 345, 60, fill="#f8fafc", stroke="#0284c7", sw=1.3, rx=6))
    p.append(text(227, 422, "Аналітика та моніторинг процесів", size=11.5, color="#0284c7", bold=True))
    p.append(text(227, 444, "Кореляція сигналів, виявлення аварій, звітність", size=10, color="#475569"))

    p.append(rect(435, 400, 345, 60, fill="#f8fafc", stroke="#6b7280", sw=1.3, rx=6))
    p.append(text(607, 422, "Мережева діагностика та безпека", size=11.5, color="#374151", bold=True))
    p.append(text(607, 444, "Виявлення втрат зв'язку, джитер, атаки повтору", size=10, color="#475569"))

    render(os.path.join(OUT, "dual-timestamp-pipeline.svg"), W, H, *p)


def fig_reverse_delta_reconstruction():
    """Принцип якірної реконструкції часу за зворотними дельтами (Anchor Timestamping)."""
    W, H = 840, 500
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Реконструкція абсолютного часу за методом зворотних дельт (Anchor Timestamping)", size=14, color=INK, bold=True))

    # Верхній блок: Локальний час пристрою
    p.append(rect(30, 45, 780, 160, fill="#f8fafc", stroke="#0284c7", sw=1.4, rx=6))
    p.append(text(420, 68, "Крок 1. Пристрій (без RTC): відлік монотонних дельт від моменту передачі T_tx", size=12.5, color="#0284c7", bold=True))

    p.append(line(70, 125, 750, 125, color=LINE, sw=2))
    p.append(arrow(750, 125, 765, 125, color=LINE, sw=2))
    p.append(text(765, 145, "uptime_ms", size=11, color=LINE, italic=True))

    samples = [
        ("Замір 1", 110, "t1 = 1000", "Δt1 = 4000 мс"),
        ("Замір 2", 230, "t2 = 2500", "Δt2 = 2500 мс"),
        ("Замір 3", 350, "t3 = 4000", "Δt3 = 1000 мс"),
        ("Замір 4", 470, "t4 = 5000", "Δt4 = 0 мс"),
    ]

    for name, x, raw_t, delta in samples:
        p.append(circle(x, 125, 5, fill="#0284c7", stroke=LINE, sw=1.5))
        p.append(text(x, 105, name, size=11, color="#0284c7", bold=True))
        p.append(text(x, 145, raw_t, size=9.5, color="#64748b"))
        p.append(text(x, 162, delta, size=10, color=POS, bold=True))

    # Момент відправки кадру T_tx (праворуч від заміру 4)
    p.append(rect(540, 85, 250, 75, fill="#fee2e2", stroke=POS, sw=1.3, rx=5))
    p.append(text(665, 106, "T_tx (відправка кадру)", size=11, color=POS, bold=True))
    p.append(text(665, 126, "Пакет містить лише дельти:", size=9.5, color="#334155"))
    p.append(text(665, 144, "[4000, 2500, 1000, 0] мс", size=10, color=POS, bold=True))

    # Перехід: радіоефір
    p.append(arrow(420, 210, 420, 245, color="#94a3b8", sw=2.0))
    p.append(text(420, 230, "Радіоканал (затримка поширення t_prop ≈ 15 мс)", size=10, color="#64748b", anchor="middle"))

    # Нижній блок: Сервер відновлює абсолютний час
    p.append(rect(30, 255, 780, 225, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(420, 278, "Крок 2. Сервер (синхронізований за NTP): обчислення абсолютних міток кожного заміру", size=12.5, color=FIELD, bold=True))

    p.append(line(70, 370, 750, 370, color=LINE, sw=2))
    p.append(arrow(750, 370, 765, 370, color=LINE, sw=2))
    p.append(text(765, 390, "UTC (NTP)", size=11, color=LINE, italic=True))

    # Серверні розрахунки
    p.append(rect(50, 295, 740, 42, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(420, 312, "T_anchor = T_server - t_prop = 12:00:05.015 - 0.015 = 12:00:05.000 UTC", size=11, color=FIELD, bold=True))
    p.append(text(420, 327, "Формула відновлення: T_real[i] = T_anchor - Δt[i]", size=10.5, color="#1e293b"))

    reconstructed = [
        ("Замір 1", 110, "12:00:01.000", "(T_anchor − 4.0с)"),
        ("Замір 2", 230, "12:00:02.500", "(T_anchor − 2.5с)"),
        ("Замір 3", 350, "12:00:04.000", "(T_anchor − 1.0с)"),
        ("Замір 4", 470, "12:00:05.000", "(T_anchor − 0.0с)"),
    ]

    for name, x, utc_time, formula in reconstructed:
        p.append(circle(x, 370, 5, fill=FIELD, stroke=LINE, sw=1.5))
        p.append(text(x, 395, name, size=11, color=FIELD, bold=True))
        p.append(text(x, 415, utc_time, size=11, color="#0f172a", bold=True))
        p.append(text(x, 432, formula, size=9.5, color="#475569"))

    # Підсумок відновлення
    p.append(rect(540, 360, 250, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(665, 382, "T_anchor = 12:00:05.000", size=10.5, color=FIELD, bold=True))
    p.append(text(665, 402, "Абсолютний час відновлено!", size=9.5, color="#334155"))

    p.append(rect(50, 448, 740, 24, fill="#ffffff", stroke="#059669", sw=1.0, rx=3))
    p.append(text(420, 464, "ВИГОДА: Пристрою НЕ потрібен дорогий RTC і батарейка; економія до 75% радіотрафіку.", size=10, color="#065f46", bold=True))

    render(os.path.join(OUT, "reverse-delta-reconstruction.svg"), W, H, *p)


if __name__ == "__main__":
    fig_server_vs_edge_timestamp()
    fig_dual_timestamp_pipeline()
    fig_reverse_delta_reconstruction()
    print("Всі 3 фігури згенеровано успішно.")
