# -*- coding: utf-8 -*-
"""Фігури для статті «Спільна шкала часу: борт, станція, відео» (spilna-shkala-chasu).
Генерує 4 SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_time_divergence():
    """1. time-divergence-asymmetry.svg — Дрейф трьох годинників та розрив кореляції."""
    W, H = 840, 470
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 35, "Проблема трьох годинників: дрейф генераторів і затримка каналу", size=15, color=INK, bold=True))

    # Секція 1: Три незалежні генератори
    top_y = 60
    parts.append(rect(25, top_y, 790, 185, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(40, top_y + 22, "1. Фізична розбіжність автономних генераторів (без корекції)", size=12, color=INK, bold=True, anchor="start"))

    # Бортовий комп'ютер (STM32/PX4)
    y1 = top_y + 42
    parts.append(rect(40, y1, 160, 36, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    parts.append(text(120, y1 + 16, "Бортовий МК (PX4)", size=11, color=POS, bold=True))
    parts.append(text(120, y1 + 30, "Кварц 16 МГц (+30 ppm)", size=9, color=MUTED))
    parts.append(line(210, y1 + 18, 770, y1 + 18, color=POS, sw=2))
    parts.append(text(780, y1 + 22, "t_board", size=11, color=POS, bold=True, anchor="start"))
    parts.append(circle(260, y1 + 18, 4, fill=POS, stroke=POS))
    parts.append(text(260, y1 + 10, "100.000 с", size=9, color=POS))
    parts.append(circle(680, y1 + 18, 4, fill=POS, stroke=POS))
    parts.append(text(680, y1 + 10, "100.054 с (+54 мс)", size=9, color=POS, bold=True))

    # Наземна станція (GCS Laptop)
    y2 = top_y + 88
    parts.append(rect(40, y2, 160, 36, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    parts.append(text(120, y2 + 16, "Станція (QGC)", size=11, color=NEG, bold=True))
    parts.append(text(120, y2 + 30, "x86 RTC (-15 ppm)", size=9, color=MUTED))
    parts.append(line(210, y2 + 18, 770, y2 + 18, color=NEG, sw=2))
    parts.append(text(780, y2 + 22, "t_gcs", size=11, color=NEG, bold=True, anchor="start"))
    parts.append(circle(260, y2 + 18, 4, fill=NEG, stroke=NEG))
    parts.append(text(260, y2 + 10, "100.000 с", size=9, color=NEG))
    parts.append(circle(640, y2 + 18, 4, fill=NEG, stroke=NEG))
    parts.append(text(640, y2 + 10, "99.973 с (-27 мс)", size=9, color=NEG, bold=True))

    # Відеоенкодер камери
    y3 = top_y + 134
    parts.append(rect(40, y3, 160, 36, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(120, y3 + 16, "Відеокамера (H.264)", size=11, color=FIELD, bold=True))
    parts.append(text(120, y3 + 30, "SoC кварц (+50 ppm)", size=9, color=MUTED))
    parts.append(line(210, y3 + 18, 770, y3 + 18, color=FIELD, sw=2))
    parts.append(text(780, y3 + 22, "t_cam", size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(circle(260, y3 + 18, 4, fill=FIELD, stroke=FIELD))
    parts.append(text(260, y3 + 10, "100.000 с", size=9, color=FIELD))
    parts.append(circle(720, y3 + 18, 4, fill=FIELD, stroke=FIELD))
    parts.append(text(720, y3 + 10, "100.090 с (+90 мс)", size=9, color=FIELD, bold=True))

    # Секція 2: Спотворення під час інциденту через затримки передачі
    bot_y = 260
    parts.append(rect(25, bot_y, 790, 190, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(40, bot_y + 22, "2. Ілюзія послідовності подій у разі запису «за часом отримання»", size=12, color=INK, bold=True, anchor="start"))

    # Подія 1: Удар об перешкоду
    parts.append(rect(40, bot_y + 38, 225, 138, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    parts.append(text(152, bot_y + 56, "Фізична подія: Удар", size=11, color=POS, bold=True))
    parts.append(text(152, bot_y + 74, "t_real = 100.000 с", size=10, color=INK, bold=True))
    parts.append(text(50, bot_y + 96, "• Акселерометр: сплеск 18g", size=9.5, color=INK, anchor="start"))
    parts.append(text(50, bot_y + 114, "• Запис у ULog: 100.054 с", size=9.5, color=POS, anchor="start"))
    parts.append(text(50, bot_y + 132, "• Збережено локально на SD", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(50, bot_y + 150, "  із міткою бортового таймера", size=9.5, color=MUTED, anchor="start"))

    # Подія 2: Телеметрія на станції
    parts.append(rect(285, bot_y + 38, 245, 138, fill="#eff6ff", stroke=NEG, sw=1.2, rx=5))
    parts.append(text(407, bot_y + 56, "Лог телеметрії станції", size=11, color=NEG, bold=True))
    parts.append(text(407, bot_y + 74, "t_gcs_recv = 100.220 с", size=10, color=NEG, bold=True))
    parts.append(text(295, bot_y + 96, "• Затримка радіоканалу: 120 мс", size=9.5, color=INK, anchor="start"))
    parts.append(text(295, bot_y + 114, "• Джитер буфера: 50 мс", size=9.5, color=INK, anchor="start"))
    parts.append(text(295, bot_y + 132, "• Похибка дрейфу GCS: -27 мс", size=9.5, color=NEG, anchor="start"))
    parts.append(text(295, bot_y + 150, "→ Зсув у лозі: +220 мс!", size=9.5, color=POS, bold=True, anchor="start"))

    # Подія 3: Відеозапис
    parts.append(rect(550, bot_y + 38, 250, 138, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    parts.append(text(675, bot_y + 56, "Відеопотік на екрані", size=11, color=FIELD, bold=True))
    parts.append(text(675, bot_y + 74, "t_disp = 100.350 с", size=10, color=FIELD, bold=True))
    parts.append(text(560, bot_y + 96, "• Експозиція + ISP: 33 мс", size=9.5, color=INK, anchor="start"))
    parts.append(text(560, bot_y + 114, "• H.264 кодування: 45 мс", size=9.5, color=INK, anchor="start"))
    parts.append(text(560, bot_y + 132, "• RTSP/RTP буфер: 200 мс", size=9.5, color=INK, anchor="start"))
    parts.append(text(560, bot_y + 150, "→ Кадр відстає на 350 мс!", size=9.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "time-divergence-asymmetry.svg"), W, H, *parts)


def fig_ptp_mavlink():
    """2. ptp-mavlink-four-timestamps.svg — Двосторонній обмін 4 мітками часу."""
    W, H = 860, 500
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 35, "Двосторонній обмін мітками часу: розрахунок RTT і зміщення годинника", size=15, color=INK, bold=True))

    # Дві часові осі: Клієнт (Земля) та Сервер (Борт)
    cx, sx = 160, 500
    top_y, bot_y = 65, 335

    parts.append(rect(cx - 90, top_y - 8, 180, 30, fill="#dbeafe", stroke=NEG, sw=1.5, rx=5))
    parts.append(text(cx, top_y + 12, "Клієнт (Станція GCS)", size=12, color=NEG, bold=True))

    parts.append(rect(sx - 90, top_y - 8, 180, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    parts.append(text(sx, top_y + 12, "Сервер (Бортовий МК)", size=12, color=POS, bold=True))

    # Вертикальні лінії життя
    parts.append(line(cx, top_y + 26, cx, bot_y + 10, color=NEG, sw=2))
    parts.append(line(sx, top_y + 26, sx, bot_y + 10, color=POS, sw=2))

    # Мітка t1: відправка запиту
    t1_y = 120
    parts.append(circle(cx, t1_y, 5, fill=NEG, stroke=INK, sw=1.2))
    parts.append(text(cx - 15, t1_y + 4, "t₁ (відправка запиту)", size=10, color=NEG, bold=True, anchor="end"))

    # Мітка t2: отримання запиту сервером
    t2_y = 175
    parts.append(circle(sx, t2_y, 5, fill=POS, stroke=INK, sw=1.2))
    parts.append(text(sx + 15, t2_y + 4, "t₂ (прийом сервером)", size=10, color=POS, bold=True, anchor="start"))

    # Стрілка запиту (t1 -> t2)
    parts.append(arrow(cx, t1_y, sx, t2_y, color=NEG, sw=2))
    parts.append(text(330, 138, "TIMESYNC #111 [tc1=0, ts1=t₁]", size=10, color=NEG, bold=True))
    parts.append(text(330, 154, "Затримка прямого каналу d_fwd", size=9.5, color=MUTED))

    # Мітка t3: відповідь сервера
    t3_y = 205
    parts.append(circle(sx, t3_y, 5, fill=POS, stroke=INK, sw=1.2))
    parts.append(text(sx + 15, t3_y + 4, "t₃ (відправка відповіді)", size=10, color=POS, bold=True, anchor="start"))

    # Обробка на сервері (t3 - t2)
    parts.append(line(sx + 6, t2_y, sx + 6, t3_y, color=MUTED, sw=1.5, dash="3 3"))
    parts.append(text(sx + 145, (t2_y + t3_y) / 2 + 4, "t_proc = t₃ - t₂", size=9.5, color=MUTED, anchor="start"))

    # Мітка t4: отримання відповіді клієнтом
    t4_y = 285
    parts.append(circle(cx, t4_y, 5, fill=NEG, stroke=INK, sw=1.2))
    parts.append(text(cx - 15, t4_y + 4, "t₄ (прийом відповіді)", size=10, color=NEG, bold=True, anchor="end"))

    # Стрілка відповіді (t3 -> t4)
    parts.append(arrow(sx, t3_y, cx, t4_y, color=POS, sw=2))
    parts.append(text(330, 238, "TIMESYNC #111 [tc1=t₁, ts1=t₂]", size=10, color=POS, bold=True))
    parts.append(text(330, 254, "Затримка зворотного каналу d_rev", size=9.5, color=MUTED))

    # Панель формул та розрахунків праворуч
    fx, fy, fw, fh = 635, 75, 200, 265
    parts.append(rect(fx, fy, fw, fh, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(rect(fx, fy, fw, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=6))
    parts.append(text(fx + fw / 2, fy + 17, "Формули обчислення", size=11, color=INK, bold=True))

    parts.append(text(fx + 10, fy + 48, "Час кругового обігу (RTT):", size=10, color=INK, bold=True, anchor="start"))
    parts.append(text(fx + 10, fy + 68, "δ = (t₄ - t₁) - (t₃ - t₂)", size=10, color=NEG, bold=True, anchor="start"))

    parts.append(text(fx + 10, fy + 102, "Зміщення годинника (Offset):", size=10, color=INK, bold=True, anchor="start"))
    parts.append(text(fx + 10, fy + 122, "θ = ((t₂ - t₁) + (t₃ - t₄)) / 2", size=10, color=POS, bold=True, anchor="start"))

    parts.append(text(fx + 10, fy + 156, "У разі швидкої відповіді (t₂ ≈ t₃):", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(fx + 10, fy + 174, "δ = t₄ - t₁", size=10, color=INK, anchor="start"))
    parts.append(text(fx + 10, fy + 192, "θ = t₂ - (t₁ + t₄) / 2", size=10, color=INK, anchor="start"))

    parts.append(text(fx + 10, fy + 224, "Похибка асиметрії каналу:", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(fx + 10, fy + 244, "ε = (d_rev - d_fwd) / 2", size=10, color=POS, bold=True, anchor="start"))

    # Блок знизу: Чому важливий відбір за мінімальним RTT
    parts.append(rect(25, 360, 810, 115, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(rect(25, 360, 810, 26, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=6))
    parts.append(text(40, 377, "Ключовий інваріант: мінімізація асиметрії через фільтрацію Min-RTT", size=11, color="#0369a1", bold=True, anchor="start"))

    parts.append(text(40, 404, "• Затримка поширення сигналу в ефірі суворо симетрична: d_fwd ≈ d_rev.", size=10, color=INK, anchor="start"))
    parts.append(text(40, 424, "• Асиметрія виникає через черги буферизації в ОС, стеках Wi-Fi/LTE та радіомодемах (Bufferbloat).", size=10, color=INK, anchor="start"))
    parts.append(text(40, 444, "• Вибірка з мінімальним RTT у ковзному вікні гарантує проходження без затримок у чергах: ε → 0.", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "ptp-mavlink-four-timestamps.svg"), W, H, *parts)


def fig_video_sei():
    """3. video-sei-pipeline.svg — Конвеєр відеокадрів і вшивання SEI-таймкодів."""
    W, H = 860, 480
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 35, "Конвеєр відеопотоку та вшивання метаданих SEI у кадри H.264", size=15, color=INK, bold=True))

    # Схема конвеєра: 4 послідовні блоки
    bx, by, bw, bh = 25, 65, 175, 120
    # Блок 1: Сенсор
    parts.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(rect(bx, by, bw, 26, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=6))
    parts.append(text(bx + bw / 2, by + 17, "1. Сенсор камери", size=11, color="#0369a1", bold=True))
    parts.append(text(bx + 10, by + 46, "• Фотодіоди + Shutter", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx + 10, by + 64, "• Апаратний Strobe", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(bx + 10, by + 82, "• Початок експозиції", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx + 10, by + 100, "  на Input Capture МК", size=9.5, color=MUTED, anchor="start"))

    # Стрілка 1 -> 2
    parts.append(arrow(bx + bw, by + bh / 2, bx + bw + 35, by + bh / 2, color=INK, sw=1.5))

    # Блок 2: Таймер захоплення
    bx2 = bx + bw + 35
    parts.append(rect(bx2, by, bw, bh, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    parts.append(rect(bx2, by, bw, 26, fill="#fee2e2", stroke=POS, sw=1, rx=6))
    parts.append(text(bx2 + bw / 2, by + 17, "2. Фіксація мітки МК", size=11, color=POS, bold=True))
    parts.append(text(bx2 + 10, by + 46, "• Апаратний таймер (TIM)", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx2 + 10, by + 64, "• Похибка < 1 мкс", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(bx2 + 10, by + 82, "• Зчитування UTC з GPS", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx2 + 10, by + 100, "• Прив'язка кватерніона", size=9.5, color=MUTED, anchor="start"))

    # Стрілка 2 -> 3
    parts.append(arrow(bx2 + bw, by + bh / 2, bx2 + bw + 35, by + bh / 2, color=INK, sw=1.5))

    # Блок 3: Енкодер H.264
    bx3 = bx2 + bw + 35
    parts.append(rect(bx3, by, bw, bh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    parts.append(rect(bx3, by, bw, 26, fill="#dcfce7", stroke=FIELD, sw=1, rx=6))
    parts.append(text(bx3 + bw / 2, by + 17, "3. Енкодер (V4L2/ISP)", size=11, color=FIELD, bold=True))
    parts.append(text(bx3 + 10, by + 46, "• Стиснення (YUV420)", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx3 + 10, by + 64, "• NAL Type 6 (SEI)", size=9.5, color=FIELD, bold=True, anchor="start"))
    parts.append(text(bx3 + 10, by + 82, "• user_data_unregistered", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx3 + 10, by + 100, "• Вшивання перед IDR", size=9.5, color=MUTED, anchor="start"))

    # Стрілка 3 -> 4
    parts.append(arrow(bx3 + bw, by + bh / 2, bx3 + bw + 35, by + bh / 2, color=INK, sw=1.5))

    # Блок 4: Зберігання / Стрім
    bx4 = bx3 + bw + 35
    parts.append(rect(bx4, by, bw, bh, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    parts.append(rect(bx4, by, bw, 26, fill="#dbeafe", stroke=NEG, sw=1, rx=6))
    parts.append(text(bx4 + bw / 2, by + 17, "4. RTSP / MP4 Запис", size=11, color=NEG, bold=True))
    parts.append(text(bx4 + 10, by + 46, "• Контейнер MP4 / RTP", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx4 + 10, by + 64, "• Метадані не псують кадр", size=9.5, color=NEG, bold=True, anchor="start"))
    parts.append(text(bx4 + 10, by + 82, "• Стандартні плеєри грають", size=9.5, color=INK, anchor="start"))
    parts.append(text(bx4 + 10, by + 100, "• Парсер витягує лог", size=9.5, color=MUTED, anchor="start"))

    # Нижня частина: Внутрішня анатомія NAL-пакета H.264 з SEI
    nal_y = 205
    parts.append(rect(25, nal_y, 810, 255, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(rect(25, nal_y, 810, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=6))
    parts.append(text(40, nal_y + 17, "Анатомія NAL-юнітів кадру: вбудовування SEI User Data Unregistered (PayloadType = 5)", size=11, color=INK, bold=True, anchor="start"))

    # Рядок NAL юнітів
    ny = nal_y + 38
    parts.append(rect(40, ny, 110, 42, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    parts.append(text(95, ny + 18, "NAL 7: SPS", size=10, color=INK, bold=True))
    parts.append(text(95, ny + 32, "Параметри", size=9, color=MUTED))

    parts.append(rect(160, ny, 110, 42, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    parts.append(text(215, ny + 18, "NAL 8: PPS", size=10, color=INK, bold=True))
    parts.append(text(215, ny + 32, "Картинка", size=9, color=MUTED))

    # Виділений NAL 6 (SEI)
    parts.append(rect(280, ny, 320, 42, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    parts.append(text(440, ny + 18, "NAL 6: SEI (Supplemental Enhancement Info)", size=11, color=POS, bold=True))
    parts.append(text(440, ny + 32, "payloadType = 5 (user_data_unregistered) | Довжина L байтів", size=9.5, color=POS))

    parts.append(rect(610, ny, 205, 42, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    parts.append(text(712, ny + 18, "NAL 5: IDR Slice (I-Frame)", size=10, color=NEG, bold=True))
    parts.append(text(712, ny + 32, "Стиснені пікселі кадру", size=9, color=MUTED))

    # Розгортання структури SEI Payload
    py_top = ny + 54
    parts.append(rect(40, py_top, 775, 148, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    parts.append(text(55, py_top + 20, "Структура корисного навантаження SEI (Бінарний заголовок телеметрії кадру):", size=10, color=POS, bold=True, anchor="start"))

    # Поля SEI
    col1_x = 55
    parts.append(rect(col1_x, py_top + 32, 170, 100, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(col1_x + 85, py_top + 50, "UUID ідентифікатор", size=10, color=POS, bold=True))
    parts.append(text(col1_x + 10, py_top + 70, "16 байтів (GUID)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col1_x + 10, py_top + 90, "Унікальний ключ схеми", size=9, color=MUTED, anchor="start"))
    parts.append(text(col1_x + 10, py_top + 108, "для перевірки типу", size=9, color=MUTED, anchor="start"))

    col2_x = col1_x + 185
    parts.append(rect(col2_x, py_top + 32, 195, 100, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(col2_x + 97, py_top + 50, "Часові мітки (uint64)", size=10, color=POS, bold=True))
    parts.append(text(col2_x + 10, py_top + 70, "• timestamp_utc_us (64 біти)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col2_x + 10, py_top + 90, "• timestamp_boot_us (64 біти)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col2_x + 10, py_top + 110, "• exposure_us (32 біти)", size=9, color=MUTED, anchor="start"))

    col3_x = col2_x + 210
    parts.append(rect(col3_x, py_top + 32, 185, 100, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(col3_x + 92, py_top + 50, "Бортовий стан дрона", size=10, color=POS, bold=True))
    parts.append(text(col3_x + 10, py_top + 70, "• Кватерніон q[4] (float32)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col3_x + 10, py_top + 90, "• Координати Lat/Lon/Alt", size=9.5, color=INK, anchor="start"))
    parts.append(text(col3_x + 10, py_top + 110, "• Кутові швидкості gyro[3]", size=9, color=MUTED, anchor="start"))

    col4_x = col3_x + 200
    parts.append(rect(col4_x, py_top + 32, 165, 100, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(col4_x + 82, py_top + 50, "Службові поля", size=10, color=POS, bold=True))
    parts.append(text(col4_x + 10, py_top + 70, "• frame_sequence (32 біти)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col4_x + 10, py_top + 90, "• sensor_id (8 бітів)", size=9.5, color=INK, anchor="start"))
    parts.append(text(col4_x + 10, py_top + 110, "• CRC32 контрольна сума", size=9, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "video-sei-pipeline.svg"), W, H, *parts)


def fig_timesync_filter():
    """4. timesync-filter-architecture.svg — Архітектура робастного фільтра зміщення."""
    W, H = 860, 480
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 35, "Архітектура робастного фільтра зміщення часу (Timesync Filter)", size=15, color=INK, bold=True))

    # Схема конвеєра фільтрації: 5 кроків
    y_box = 65
    bw, bh = 150, 140

    # 1. Вхідні сирі дані
    x1 = 25
    parts.append(rect(x1, y_box, bw, bh, fill="#ffffff", stroke="#64748b", sw=1.5, rx=6))
    parts.append(rect(x1, y_box, bw, 26, fill="#f1f5f9", stroke="#64748b", sw=1, rx=6))
    parts.append(text(x1 + bw / 2, y_box + 17, "1. Сирі мітки", size=11, color=INK, bold=True))
    parts.append(text(x1 + 10, y_box + 48, "TIMESYNC / PTP", size=10, color=INK, bold=True, anchor="start"))
    parts.append(text(x1 + 10, y_box + 70, "• t₁, t₂, t₃, t₄", size=9.5, color=INK, anchor="start"))
    parts.append(text(x1 + 10, y_box + 90, "• Обчислення сирих:", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(x1 + 10, y_box + 108, "  raw_rtt = t₄ - t₁", size=9.5, color=NEG, anchor="start"))
    parts.append(text(x1 + 10, y_box + 126, "  raw_offset = θ_raw", size=9.5, color=POS, anchor="start"))

    parts.append(arrow(x1 + bw, y_box + bh / 2, x1 + bw + 18, y_box + bh / 2, color=INK, sw=1.5))

    # 2. Кільцевий буфер
    x2 = x1 + bw + 18
    parts.append(rect(x2, y_box, bw, bh, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(rect(x2, y_box, bw, 26, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=6))
    parts.append(text(x2 + bw / 2, y_box + 17, "2. Кільцевий буфер", size=11, color="#0369a1", bold=True))
    parts.append(text(x2 + 10, y_box + 48, "Ковзне вікно (K=16)", size=10, color="#0369a1", bold=True, anchor="start"))
    parts.append(text(x2 + 10, y_box + 70, "• Збереження K пар", size=9.5, color=INK, anchor="start"))
    parts.append(text(x2 + 10, y_box + 90, "  (offset_i, rtt_i)", size=9.5, color=INK, anchor="start"))
    parts.append(text(x2 + 10, y_box + 110, "• Витіснення старих", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(x2 + 10, y_box + 128, "• Захист від втрат", size=9.5, color=MUTED, anchor="start"))

    parts.append(arrow(x2 + bw, y_box + bh / 2, x2 + bw + 18, y_box + bh / 2, color=INK, sw=1.5))

    # 3. Фільтр Min-RTT
    x3 = x2 + bw + 18
    parts.append(rect(x3, y_box, bw, bh, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    parts.append(rect(x3, y_box, bw, 26, fill="#fee2e2", stroke=POS, sw=1, rx=6))
    parts.append(text(x3 + bw / 2, y_box + 17, "3. Min-RTT Фільтр", size=11, color=POS, bold=True))
    parts.append(text(x3 + 10, y_box + 48, "Відбір вибірок", size=10, color=POS, bold=True, anchor="start"))
    parts.append(text(x3 + 10, y_box + 70, "• Знаходження min(RTT)", size=9.5, color=INK, anchor="start"))
    parts.append(text(x3 + 10, y_box + 90, "• Відкидання піків", size=9.5, color=POS, anchor="start"))
    parts.append(text(x3 + 10, y_box + 110, "• Фільтрація викидів", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(x3 + 10, y_box + 128, "  (Outlier Rejection)", size=9.5, color=MUTED, anchor="start"))

    parts.append(arrow(x3 + bw, y_box + bh / 2, x3 + bw + 18, y_box + bh / 2, color=INK, sw=1.5))

    # 4. EWMA / Skew
    x4 = x3 + bw + 18
    parts.append(rect(x4, y_box, bw, bh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    parts.append(rect(x4, y_box, bw, 26, fill="#dcfce7", stroke=FIELD, sw=1, rx=6))
    parts.append(text(x4 + bw / 2, y_box + 17, "4. Оцінка фази й дрейфу", size=11, color=FIELD, bold=True))
    parts.append(text(x4 + 10, y_box + 48, "EWMA + Skew Rate", size=10, color=FIELD, bold=True, anchor="start"))
    parts.append(text(x4 + 10, y_box + 70, "• Згладжування фази:", size=9.5, color=INK, anchor="start"))
    parts.append(text(x4 + 10, y_box + 88, "  θ_filt = (1-α)θ + α·θ_new", size=9, color=FIELD, bold=True, anchor="start"))
    parts.append(text(x4 + 10, y_box + 108, "• Лінійна регресія дрейфу", size=9.5, color=INK, anchor="start"))
    parts.append(text(x4 + 10, y_box + 126, "  частоти (ppm / skew)", size=9, color=MUTED, anchor="start"))

    parts.append(arrow(x4 + bw, y_box + bh / 2, x4 + bw + 18, y_box + bh / 2, color=INK, sw=1.5))

    # 5. Контролер Slewing
    x5 = x4 + bw + 18
    parts.append(rect(x5, y_box, bw, bh, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    parts.append(rect(x5, y_box, bw, 26, fill="#dbeafe", stroke=NEG, sw=1, rx=6))
    parts.append(text(x5 + bw / 2, y_box + 17, "5. Синхронізатор", size=11, color=NEG, bold=True))
    parts.append(text(x5 + 10, y_box + 48, "Плавне підтягування", size=10, color=NEG, bold=True, anchor="start"))
    parts.append(text(x5 + 10, y_box + 70, "• Slewing (±500 ppm)", size=9.5, color=NEG, bold=True, anchor="start"))
    parts.append(text(x5 + 10, y_box + 90, "• Заборона стрибків назад", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(x5 + 10, y_box + 110, "• Гарантія dt > 0 для PID", size=9.5, color=INK, anchor="start"))
    parts.append(text(x5 + 10, y_box + 128, "• Монотонна шкала часу", size=9.5, color=MUTED, anchor="start"))

    # Нижній порівняльний блок: Stepping проти Slewing
    comp_y = 225
    parts.append(rect(25, comp_y, 810, 235, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(rect(25, comp_y, 810, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=6))
    parts.append(text(40, comp_y + 17, "Порівняння стратегій корекції: Миттєвий стрибок (Stepping) проти Плавного підтягування (Slewing)", size=11, color=INK, bold=True, anchor="start"))

    # Ліва колонка: Stepping (Небезпечно)
    cx1 = 40
    parts.append(rect(cx1, comp_y + 36, 375, 185, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    parts.append(text(cx1 + 187, comp_y + 56, "Миттєвий стрибок (Clock Stepping) — НЕБЕЗПЕЧНО", size=11, color=POS, bold=True))
    parts.append(text(cx1 + 15, comp_y + 80, "Механізм: Прямий запис нового часу у годинник: t_now = t_new", size=9.5, color=INK, bold=True, anchor="start"))
    parts.append(text(cx1 + 15, comp_y + 102, "• Якщо годинник випереджав: час стрибає НАЗАД на Δt.", size=9.5, color=POS, anchor="start"))
    parts.append(text(cx1 + 15, comp_y + 122, "• Обчислення інтервалу в контурі керування ламається:", size=9.5, color=INK, anchor="start"))
    parts.append(text(cx1 + 25, comp_y + 140, "dt = t_now - t_prev  →  dt < 0  або  4 294 967 мс (uint32)!", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(cx1 + 15, comp_y + 162, "• Наслідок: інтегратор PID видає нескінченний ривок, таймери", size=9.5, color=INK, anchor="start"))
    parts.append(text(cx1 + 25, comp_y + 180, "FreeRTOS блокуються, EKF розходиться.", size=9.5, color=INK, anchor="start"))
    parts.append(text(cx1 + 15, comp_y + 202, "✓ Дозволено ЛИШЕ один раз під час холодного старту системи (|θ| > 1 с).", size=9, color=MUTED, anchor="start"))

    # Права колонка: Slewing (Стандарт безпеки)
    cx2 = 445
    parts.append(rect(cx2, comp_y + 36, 375, 185, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    parts.append(text(cx2 + 187, comp_y + 56, "Плавне підтягування (Clock Slewing) — НАДІЙНО", size=11, color=FIELD, bold=True))
    parts.append(text(cx2 + 15, comp_y + 80, "Механізм: Тимчасова зміна темпу ходу годинника на ±r ppm", size=9.5, color=INK, bold=True, anchor="start"))
    parts.append(text(cx2 + 15, comp_y + 102, "• Годинник ніколи не стрибає і ніколи не йде назад.", size=9.5, color=FIELD, bold=True, anchor="start"))
    parts.append(text(cx2 + 15, comp_y + 122, "• Якщо годинник поспішає на 10 мс, прискорюємо або", size=9.5, color=INK, anchor="start"))
    parts.append(text(cx2 + 25, comp_y + 140, "сповільнюємо віртуальний час на 500 ppm (0.5 мс/с).", size=9.5, color=INK, anchor="start"))
    parts.append(text(cx2 + 15, comp_y + 162, "• За 20 секунд помилка 10 мс повністю усувається без ривків.", size=9.5, color=FIELD, anchor="start"))
    parts.append(text(cx2 + 15, comp_y + 182, "• Інваріант строгого монотонного зростання: dt > 0 ЗАВЖДИ.", size=9.5, color=POS, bold=True, anchor="start"))
    parts.append(text(cx2 + 15, comp_y + 202, "✓ Стандарт для PX4/ArduPilot, Linux adjtimex() та промислового PTP.", size=9, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "timesync-filter-architecture.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_time_divergence()
    fig_ptp_mavlink()
    fig_video_sei()
    fig_timesync_filter()
    print("Всі 4 фігури згенеровано у ./img/")
