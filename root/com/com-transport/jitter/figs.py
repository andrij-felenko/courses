# -*- coding: utf-8 -*-
"""Фігури до теми «Джитер: варіація затримки».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і примітиви — зі спільного scripts/svgkit.py.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e67e22"
PURPLE = "#8e44ad"
CYAN = "#16a085"

# ── 1. Концепція джитеру: часова шкала надсилання та прибуття ────────────────
def fig_jitter_concept():
    W, H = 760, 400
    f = [text(W / 2, 25, "Ідеальна періодична передача проти реального прибуття з джитером", size=15, bold=True)]

    # Заголовок передавача (ліворуч зверху)
    f.append(rect(30, 50, 160, 26, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(110, 67, "Передавач (T = 20 мс)", size=11, bold=True, color=FIELD))

    # Вісь передавача
    f.append(arrow(195, 63, 720, 63, color=LINE, sw=1.8))
    f.append(text(725, 67, "Час t", size=11, bold=True, color=MUTED, anchor="start"))

    send_times = [230, 310, 390, 470, 550, 630]
    for idx, sx in enumerate(send_times, 1):
        f.append(line(sx, 55, sx, 71, color=FIELD, sw=2.0))
        f.append(circle(sx, 63, 4, fill=FIELD, stroke="#ffffff", sw=1.2))
        f.append(rect(sx - 16, 76, 32, 20, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=3))
        f.append(text(sx, 90, f"P{idx}", size=10, bold=True, color=FIELD))
        f.append(text(sx, 48, f"{(idx-1)*20}", size=9, color=MUTED))

    # Інтервали надсилання
    for i in range(len(send_times) - 1):
        x1, x2 = send_times[i], send_times[i+1]
        f.append(line(x1 + 6, 63, x2 - 6, 63, color=FIELD, sw=1.0, dash="2,2"))

    # Пояснення мережевого транзиту посередині
    f.append(text(100, 150, "Мережевий тракт", size=11, bold=True, color=MUTED))
    f.append(text(100, 168, "Змінний час у дорозі", size=9, color=MUTED))

    # Фактичні часи прибуття (з різною затримкою):
    # send_times = [230, 310, 390, 470, 550, 630]
    recv_data = [
        (1, 230, 290, "60мс", FIELD),
        (2, 310, 360, "50мс", CYAN),
        (3, 390, 505, "115мс", POS),
        (4, 470, 545, "75мс", ORANGE),
        (5, 550, 620, "70мс", FIELD),
        (6, 630, 690, "60мс", FIELD)
    ]

    for pidx, sx, rx, dlab, pcol in recv_data:
        # Лінія польоту через мережу
        f.append(line(sx, 98, rx, 210, color=pcol, sw=1.4, dash="3,3"))
        f.append(text((sx + rx)/2 - 12, (98 + 210)/2, dlab, size=9, color=pcol, bold=True))

    # Заголовок приймача (ліворуч знизу)
    f.append(rect(30, 215, 160, 26, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
    f.append(text(110, 232, "Приймач (з джитером)", size=11, bold=True, color=INK))

    # Вісь приймача
    f.append(arrow(195, 228, 720, 228, color=LINE, sw=1.8))
    f.append(text(725, 232, "Час t", size=11, bold=True, color=MUTED, anchor="start"))

    for pidx, sx, rx, dlab, pcol in recv_data:
        f.append(line(rx, 220, rx, 236, color=pcol, sw=2.0))
        f.append(circle(rx, 228, 4, fill=pcol, stroke="#ffffff", sw=1.2))
        f.append(rect(rx - 16, 242, 32, 20, fill="#ffffff", stroke=pcol, sw=1.5, rx=3))
        f.append(text(rx, 256, f"P{pidx}", size=10, bold=True, color=pcol))

    # Позначки інтервалів прибуття
    f.append(line(290, 280, 360, 280, color=CYAN, sw=1.4))
    f.append(text(325, 295, "Δt = 14мс (ранній)", size=9, color=CYAN, bold=True))

    f.append(line(360, 280, 505, 280, color=POS, sw=1.4))
    f.append(text(432, 295, "Δt = 73мс (запізнення!)", size=9, color=POS, bold=True))

    f.append(line(505, 312, 545, 312, color=ORANGE, sw=1.4))
    f.append(text(525, 327, "Δt = 8мс", size=9, color=ORANGE, bold=True))

    # Пояснювальний висновок
    f.append(rect(30, 350, 700, 38, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=5))
    f.append(text(W / 2, 373, "Джитер = відхилення інтервалів прибуття від інтервалів відправлення: D(i, j) = (R_j - R_i) - (S_j - S_i)", size=11, bold=True, color=INK))

    render(os.path.join(IMG, "jitter-concept-interarrival.svg"), W, H, *f)


# ── 2. Джерела виникнення джитеру в мережевому тракті ─────────────────────────
def fig_jitter_sources():
    W, H = 760, 420
    f = [text(W / 2, 25, "Джерела виникнення джитеру в мережевому тракті", size=15, bold=True)]

    # 1. Вхідний потік реального часу (VoIP / Відео)
    f.append(rect(30, 80, 140, 80, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(100, 105, "Джерело потоку", size=12, bold=True, color=FIELD))
    f.append(text(100, 125, "Рівномірні пакети", size=10, color=MUTED))
    f.append(text(100, 142, "T = 20 мс (ідеал)", size=10, bold=True, color=FIELD))

    # Стрілка до маршрутизатора
    f.append(arrow(170, 120, 240, 120, color=INK, sw=1.8))

    # 2. Вузол комутації з чергою та крос-трафіком (Router Buffer)
    f.append(rect(240, 65, 270, 205, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(375, 88, "Маршрутизатор 1 (Черги)", size=12, bold=True, color=INK))

    # Крос-трафік зверху
    f.append(arrow(375, 30, 375, 105, color=POS, sw=1.8))
    f.append(text(375, 20, "Сплеск крос-трафіку (TCP/HTTP)", size=11, bold=True, color=POS))

    # Буфер черги
    f.append(line(260, 115, 450, 115, color=INK, sw=1.8))
    f.append(line(260, 165, 450, 165, color=INK, sw=1.8))
    f.append(line(260, 115, 260, 165, color=INK, sw=1.8, dash="3,3"))

    # Пакети в черзі: великі TCP кадри блокують малі голосові
    f.append(rect(270, 122, 50, 36, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    f.append(text(295, 144, "1500 B", size=10, bold=True, color=POS))

    f.append(rect(325, 122, 50, 36, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    f.append(text(350, 144, "1500 B", size=10, bold=True, color=POS))

    f.append(rect(380, 126, 25, 28, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(392, 144, "VoIP", size=9, bold=True, color=FIELD))

    f.append(rect(410, 122, 35, 36, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    f.append(text(427, 144, "TCP", size=10, bold=True, color=POS))

    f.append(text(355, 185, "Змінний час очікування T_queue", size=10, bold=True, color=NEG))
    f.append(text(355, 200, "Затримка залежить від довжини черги", size=10, color=MUTED))
    f.append(text(355, 215, "Head-of-Line Blocking (блокування черги)", size=9, color=POS, italic=True))

    # Вихід на мульти-маршрутизацію
    f.append(arrow(510, 120, 570, 120, color=INK, sw=1.8))

    # 3. Багатошляховість та динамічна маршрутизація
    f.append(rect(570, 65, 160, 205, fill="#fef9e7", stroke=ORANGE, sw=1.5, rx=8))
    f.append(text(650, 88, "Мережевий тракт", size=12, bold=True, color=INK))

    # Маршрут A (швидкий)
    f.append(line(590, 115, 710, 115, color=CYAN, sw=1.5))
    f.append(text(650, 130, "Шлях A (RTT = 30 мс)", size=10, bold=True, color=CYAN))

    # Маршрут B (повільний / обхідний)
    f.append(line(590, 155, 710, 155, color=ORANGE, sw=1.5, dash="4,3"))
    f.append(text(650, 170, "Шлях B (RTT = 85 мс)", size=10, bold=True, color=ORANGE))

    f.append(text(650, 195, "ECMP / Зміна трас", size=10, bold=True, color=INK))
    f.append(text(650, 212, "Перевпорядкування", size=10, color=POS))
    f.append(text(650, 227, "(Packet Reordering)", size=9, color=MUTED, italic=True))

    # Нижня частина: Бездротові середовища (WiFi / LTE)
    f.append(rect(30, 290, 700, 115, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(380, 312, "Бездротовий сегмент (Wi-Fi 802.11 / LTE / 5G Radio Access):", size=11, bold=True, color=INK))

    # 3 колонки бездротових причин
    f.append(rect(45, 325, 210, 65, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(150, 345, "CSMA/CA та колізії", size=11, bold=True, color=FIELD))
    f.append(text(150, 362, "Випадковий бекофф (Backoff)", size=10, color=MUTED))
    f.append(text(150, 377, "Конкуренція за радіоефір", size=9, color=INK))

    f.append(rect(275, 325, 210, 65, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(380, 345, "MAC Retransmissions", size=11, bold=True, color=POS))
    f.append(text(380, 362, "Повторні спроби на L2", size=10, color=MUTED))
    f.append(text(380, 377, "+10..60 мс на кожну спробу", size=9, color=POS, bold=True))

    f.append(rect(505, 325, 210, 65, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(610, 345, "Агрегація кадрів (A-MPDU)", size=11, bold=True, color=PURPLE))
    f.append(text(610, 362, "Очікування наповнення блоку", size=10, color=MUTED))
    f.append(text(610, 377, "Сплескоподібна видача", size=9, color=PURPLE))

    render(os.path.join(IMG, "jitter-sources.svg"), W, H, *f)


# ── 3. Робота буфера відтворення (Jitter Buffer Mechanics) ──────────────────
def fig_jitter_buffer_mechanics():
    W, H = 760, 420
    f = [text(W / 2, 25, "Принцип роботи буфера відтворення (Jitter Buffer)", size=15, bold=True)]

    # Вхідний нерівномірний потік пакетів
    f.append(text(100, 65, "Вхідні пакети (змінний інтервал)", size=11, bold=True, color=INK))
    f.append(arrow(40, 95, 230, 95, color=INK, sw=2.0))

    pkts_arrive = [
        (60, "P₁", FIELD),
        (105, "P₂", CYAN),
        (170, "P₃", POS),
        (195, "P₄", ORANGE)
    ]
    for px, plab, pcol in pkts_arrive:
        f.append(rect(px, 78, 32, 34, fill="#ffffff", stroke=pcol, sw=1.5, rx=3))
        f.append(text(px + 16, 99, plab, size=11, bold=True, color=pcol))

    # Центральний буфер FIFO (Черга впорядкування)
    f.append(rect(240, 60, 280, 160, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    f.append(text(380, 82, "Буфер відтворення (Jitter Buffer)", size=12, bold=True, color=INK))
    f.append(text(380, 98, "Фіксована/адаптивна глибина D_buf (напр. 60 мс)", size=10, color=MUTED))

    # Комірки буфера
    slots = [
        (260, 115, "P₁", "#e8f8f5", FIELD, "Готовий"),
        (310, 115, "P₂", "#e8f8f5", FIELD, "Готовий"),
        (360, 115, "P₃", "#fef9e7", ORANGE, "У черзі"),
        (410, 115, "P₄", "#fef9e7", ORANGE, "У черзі"),
        (460, 115, "—", "#f1f5f9", MUTED, "Вільний")
    ]
    for sx, sy, slab, sfill, scol, sdesc in slots:
        f.append(rect(sx, sy, 42, 48, fill=sfill, stroke=scol, sw=1.2, rx=4))
        f.append(text(sx + 21, sy + 25, slab, size=12, bold=True, color=scol))
        f.append(text(sx + 21, sy + 40, sdesc, size=9, color=MUTED))

    # Шкала дедлайну відтворення
    f.append(line(260, 185, 480, 185, color=LINE, sw=1.5))
    f.append(text(370, 205, "Часовий дедлайн вичитування", size=10, bold=True, color=FIELD))

    # Вихідний тактовий генератор ЦАП / Декодера
    f.append(arrow(520, 135, 600, 135, color=FIELD, sw=2.0))
    f.append(rect(600, 75, 130, 120, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(665, 100, "ЦАП / Декодер", size=12, bold=True, color=FIELD))
    f.append(text(665, 122, "Строгий період", size=10, color=INK))
    f.append(text(665, 139, "T_play = 20.00 мс", size=10, bold=True, color=FIELD))
    f.append(text(665, 165, "Безперервний звук", size=10, color=MUTED))

    # Нижня частина: Крайові випадки (Underrun та Overrun)
    f.append(rect(40, 245, 325, 155, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(202, 270, "1. Буферне голодування (Underrun)", size=12, bold=True, color=POS))
    f.append(text(202, 292, "Пакет прибув ПІСЛЯ дедлайну відтворення:", size=10, color=INK))
    f.append(text(202, 310, "t_arrive > t_play_deadline", size=11, bold=True, color=POS))
    f.append(text(202, 332, "• Декодер отримує порожнечу (клік/тиша)", size=10, color=MUTED))
    f.append(text(202, 350, "• Вмикається маскування втрат (PLC)", size=10, color=MUTED))
    f.append(text(202, 368, "• Запізнілий пакет відкидається як непотрібний", size=10, color=POS, bold=True))

    f.append(rect(395, 245, 325, 155, fill="#fef5e7", stroke=ORANGE, sw=1.4, rx=6))
    f.append(text(557, 270, "2. Переповнення буфера (Overrun)", size=12, bold=True, color=ORANGE))
    f.append(text(557, 292, "Сплеск затримки роздуває чергу:", size=10, color=INK))
    f.append(text(557, 310, "Queue_Depth > Max_Buffer_Capacity", size=11, bold=True, color=ORANGE))
    f.append(text(557, 332, "• Нові або найстаріші пакети скидаються", size=10, color=MUTED))
    f.append(text(557, 350, "• Загальна інтерактивна затримка зростає", size=10, color=MUTED))
    f.append(text(557, 368, "• Потрібне прискорення відтворення (WSOLA)", size=10, color=ORANGE, bold=True))

    render(os.path.join(IMG, "jitter-buffer-mechanics.svg"), W, H, *f)


# ── 4. Статичний проти адаптивного буфера ────────────────────────────────────
def fig_adaptive_vs_static():
    W, H = 760, 440
    f = [text(W / 2, 25, "Порівняння статичного та адаптивного буфера джитеру", size=15, bold=True)]

    # Вісь координат X: Час, Y: Затримка пакетів
    ox, oy = 75, 340
    gw, gh = 635, 240

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))

    f.append(text(ox + gw + 25, oy + 5, "Час t", size=12, bold=True, color=INK))
    f.append(text(ox - 10, oy - gh - 20, "Затримка (мс)", size=11, bold=True, color=INK, anchor="end"))

    # Позначки осі Y
    for y_ms, y_pos in [(50, 60), (100, 120), (150, 180), (200, 240)]:
        f.append(line(ox - 5, oy - y_pos, ox, oy - y_pos, color=LINE, sw=1.2))
        f.append(text(ox - 10, oy - y_pos + 4, f"{y_ms}мс", size=10, color=MUTED, anchor="end"))
        f.append(line(ox, oy - y_pos, ox + gw, oy - y_pos, color="#f1f5f9", sw=1.0, dash="3,3"))

    # Реальна мережева затримка (шум із двома сплесками)
    delay_curve = [
        (ox + 20, oy - 70),
        (ox + 60, oy - 65),
        (ox + 100, oy - 80),
        (ox + 140, oy - 75),
        (ox + 180, oy - 190),  # Сплеск 1 (160 мс)
        (ox + 210, oy - 160),
        (ox + 250, oy - 85),
        (ox + 300, oy - 70),
        (ox + 350, oy - 75),
        (ox + 400, oy - 90),
        (ox + 450, oy - 210),  # Сплеск 2 (175 мс)
        (ox + 480, oy - 180),
        (ox + 520, oy - 110),
        (ox + 560, oy - 80),
        (ox + 610, oy - 70)
    ]

    for i in range(len(delay_curve) - 1):
        f.append(line(delay_curve[i][0], delay_curve[i][1], delay_curve[i+1][0], delay_curve[i+1][1], color=MUTED, sw=2.0))
        f.append(circle(delay_curve[i][0], delay_curve[i][1], 3, fill=MUTED, stroke="#ffffff", sw=1.0))
    f.append(circle(delay_curve[-1][0], delay_curve[-1][1], 3, fill=MUTED, stroke="#ffffff", sw=1.0))

    # 1. Статичний буфер (фіксована полиця = 100 мс)
    static_y = oy - 120
    f.append(line(ox, static_y, ox + gw, static_y, color=POS, sw=2.2, dash="6,4"))

    # Зони втрат статичного буфера (Underrun)
    f.append(rect(ox + 160, static_y - 75, 55, 70, fill="#fdecea", stroke=POS, sw=1.0, rx=3))
    f.append(text(ox + 187, static_y - 40, "ВТРАТА!", size=9, bold=True, color=POS))

    f.append(rect(ox + 425, static_y - 95, 60, 90, fill="#fdecea", stroke=POS, sw=1.0, rx=3))
    f.append(text(ox + 455, static_y - 50, "ВТРАТА!", size=9, bold=True, color=POS))

    # 2. Адаптивний буфер (слідує за статистикою E[D] + 3*sigma)
    adaptive_curve = [
        (ox + 20, oy - 100),
        (ox + 60, oy - 95),
        (ox + 100, oy - 105),
        (ox + 140, oy - 110),
        (ox + 180, oy - 215),  # Розширення при сплеску
        (ox + 220, oy - 200),
        (ox + 260, oy - 170),
        (ox + 310, oy - 130),
        (ox + 360, oy - 110),  # Плавне повернення під час пауз
        (ox + 400, oy - 115),
        (ox + 450, oy - 235),  # Друге розширення
        (ox + 490, oy - 210),
        (ox + 530, oy - 160),
        (ox + 570, oy - 120),
        (ox + 610, oy - 105)
    ]

    for i in range(len(adaptive_curve) - 1):
        f.append(line(adaptive_curve[i][0], adaptive_curve[i][1], adaptive_curve[i+1][0], adaptive_curve[i+1][1], color=FIELD, sw=2.5))

    # Легенда розміщена внизу під графіком
    f.append(rect(30, 360, 700, 65, fill="#f8fafc", stroke="#d1d5db", sw=1.0, rx=6))

    # 3 елементи легенди в один рядок
    f.append(line(45, 385, 80, 385, color=MUTED, sw=2.0))
    f.append(circle(62, 385, 3, fill=MUTED, stroke="#ffffff", sw=1.0))
    f.append(text(90, 389, "Мережева затримка пакета T_transit", size=10, color=MUTED, anchor="start"))

    f.append(line(45, 408, 80, 408, color=POS, sw=2.0, dash="4,3"))
    f.append(text(90, 412, "Статичний буфер 100 мс (сплески спричиняють Underrun)", size=10, color=POS, bold=True, anchor="start"))

    f.append(line(460, 385, 495, 385, color=FIELD, sw=2.5))
    f.append(text(505, 389, "Адаптивний буфер D_target(t)", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(505, 412, "Динамічне масштабування (WSOLA)", size=9, color=INK, anchor="start"))

    render(os.path.join(IMG, "adaptive-vs-static-buffer.svg"), W, H, *f)


# ── 5. Фільтр джитеру RFC 3550 (EWMA Filter) ─────────────────────────────────
def fig_rtp_jitter_filter():
    W, H = 760, 390
    f = [text(W / 2, 25, "Фільтрація джитеру в протоколі RTP (RFC 3550)", size=15, bold=True)]

    # Блок обчислення різниці транзитного часу
    f.append(rect(40, 70, 240, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(160, 92, "1. Різниця часу транзиту", size=12, bold=True, color=INK))
    f.append(text(160, 115, "D(i-1, i) = (R_i - S_i) - (R_{i-1} - S_{i-1})", size=10, bold=True, color=NEG))
    f.append(text(160, 138, "S_i — мітка надсилання (RTP timestamp)", size=9, color=MUTED))
    f.append(text(160, 155, "R_i — локальний час прибуття (кванти RTP)", size=9, color=MUTED))

    # Стрілка переходу
    f.append(arrow(280, 125, 340, 125, color=INK, sw=1.8))
    f.append(text(310, 115, "|D|", size=11, bold=True, color=POS))

    # Блок рекурсивного фільтра 1-го порядку (EWMA)
    f.append(rect(340, 70, 380, 110, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(530, 92, "2. Рекурсивний згладжувальний фільтр (EWMA)", size=12, bold=True, color=FIELD))
    f.append(text(530, 118, "J_i = J_{i-1} + (|D(i-1, i)| - J_{i-1}) / 16", size=12, bold=True, color=FIELD))
    f.append(text(530, 142, "Ваговий коефіцієнт α = 1/16 (постійна часу ≈ 16 пакетів)", size=10, color=INK))
    f.append(text(530, 160, "Реалізується цілочисельним бітовим зсувом: >> 4", size=9, bold=True, color=ORANGE))

    # Пояснення RTCP поля
    f.append(arrow(530, 180, 530, 230, color=FIELD, sw=1.8))
    f.append(rect(140, 230, 480, 125, fill="#fef9e7", stroke=ORANGE, sw=1.5, rx=8))
    f.append(text(380, 255, "3. Передача в звітах RTCP Receiver Report (RR)", size=12, bold=True, color=INK))
    f.append(text(380, 280, "Поле «Interarrival Jitter» (32 біти):", size=11, bold=True, color=ORANGE))
    f.append(text(380, 302, "• Передається в одиницях частоти дискретизації кодека", size=10, color=INK))
    f.append(text(380, 320, "• 8 кГц (G.711): 1 квант = 125 мкс  |  48 кГц (Opus): 1 квант = 20.83 мкс", size=9, bold=True, color=MUTED))
    f.append(text(380, 338, "• Дозволяє відправнику оцінити якість мережі без синхронізації годинників!", size=9, color=FIELD, bold=True))

    render(os.path.join(IMG, "rtp-jitter-filter.svg"), W, H, *f)


def main():
    fig_jitter_concept()
    fig_jitter_sources()
    fig_jitter_buffer_mechanics()
    fig_adaptive_vs_static()
    fig_rtp_jitter_filter()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
