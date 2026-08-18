# -*- coding: utf-8 -*-
"""Генератор фігур для теми ntp-sync."""

import sys
import os

# Імпортуємо спільний svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def make_fig_stratum_hierarchy():
    """Ієрархія джерел часу Stratum (0..3, 16)."""
    w, h = 820, 480
    frags = []

    # Заголовок / шапка
    frags.append(textbox(410, 24, "Ієрархія джерел точного часу NTP (Stratum 0..16)", size=15, bold=True, fill="#ffffff", stroke="#ffffff")[0])

    # Stratum 0 (Фізичні еталони)
    box0, _, _ = textbox(410, 75, "Stratum 0: Первинні фізичні еталони часу\nАтомні годинники (Цезій-133, Рубідій), Водневі мазери, GNSS/GPS супутники (UTC)", size=12, pad=8, fill="#fdecea", stroke=POS, bold=True)
    frags.append(box0)

    # Стрілки від Stratum 0 до Stratum 1 (PPS / Serial / Hardware)
    frags.append(line(310, 105, 230, 155, color=POS, sw=2))
    frags.append(line(510, 105, 590, 155, color=POS, sw=2))
    frags.append(fitbox(270, 115, 280, 26, "Апаратний інтерфейс: 1 PPS + RS-232 / NMEA", size=10, fill="#ffffff", stroke=MUTED, pad=4))

    # Stratum 1 (Первинні сервери)
    box1a, _, _ = textbox(210, 185, "Stratum 1 (Первинний сервер A)\nNTPd + GPS/PPS ресивер\nRefID: GPS / PPS / ATOM", size=11, pad=7, fill="#eaf0fd", stroke=NEG, min_w=250)
    box1b, _, _ = textbox(610, 185, "Stratum 1 (Первинний сервер B)\nNTPd + Рубідієвий еталон\nRefID: RUBD / CDMA", size=11, pad=7, fill="#eaf0fd", stroke=NEG, min_w=250)
    frags.append(box1a)
    frags.append(box1b)

    # Піринг між Stratum 1
    frags.append(line(340, 185, 480, 185, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(fitbox(360, 172, 100, 22, "NTP Peer (UDP 123)", size=9, fill="#ffffff", stroke=MUTED, pad=2))

    # Стрілки до Stratum 2 (Internet / WAN)
    frags.append(line(210, 225, 210, 275, color=NEG, sw=1.8))
    frags.append(line(210, 225, 410, 275, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(610, 225, 410, 275, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(610, 225, 610, 275, color=NEG, sw=1.8))
    frags.append(fitbox(290, 238, 240, 24, "Мережа: Інтернет / WAN (UDP порт 123)", size=10, fill="#ffffff", stroke=MUTED, pad=3))

    # Stratum 2 (Вторинні публічні сервери / Регіональні пули)
    box2a, _, _ = textbox(190, 310, "Stratum 2 (Сервер пулу)\n0.pool.ntp.org", size=11, pad=6, fill=FILL, stroke=LINE, min_w=190)
    box2b, _, _ = textbox(410, 310, "Stratum 2 (Регіональний вузол)\n1.ua.pool.ntp.org", size=11, pad=6, fill=FILL, stroke=LINE, min_w=190)
    box2c, _, _ = textbox(630, 310, "Stratum 2 (Корпоративний NTP)\ntime.cloudflare.com", size=11, pad=6, fill=FILL, stroke=LINE, min_w=190)
    frags.append(box2a)
    frags.append(box2b)
    frags.append(box2c)

    # Стрілки до Stratum 3 (LAN)
    frags.append(line(190, 335, 260, 400, color=LINE, sw=1.5))
    frags.append(line(630, 335, 560, 400, color=LINE, sw=1.5))
    frags.append(textbox(410, 368, "Локальна мережа (Корпоративний LAN / UDP 123)", size=10, fill="#ffffff", stroke=MUTED, pad=4)[0])

    # Stratum 3 (Кінцеві клієнти та локальні сервери)
    box3a, _, _ = textbox(260, 430, "Stratum 3: Локальні сервери БД,\nкластери Kubernetes, шлюзи", size=11, pad=6, fill="#f4fbf7", stroke=FIELD, min_w=240)
    box3b, _, _ = textbox(560, 430, "Stratum 3..15: Кінцеві робочі станції,\nIoT-пристрої, смартфони", size=11, pad=6, fill="#f4fbf7", stroke=FIELD, min_w=240)
    frags.append(box3a)
    frags.append(box3b)

    # Примітка про Stratum 16
    frags.append(fitbox(670, 75, 135, 40, "Stratum 16:\nНесинхронізований", size=10, fill="#fff0f0", stroke=POS, bold=True, pad=4))

    render(os.path.join(IMG_DIR, "fig-stratum-hierarchy.svg"), w, h, *frags)


def make_fig_four_timestamps():
    """Чотириточковий обмін мітками часу T1..T4."""
    w, h = 820, 460
    frags = []

    # Заголовок
    frags.append(textbox(410, 24, "Чотириточковий обмін мітками часу між клієнтом і сервером NTP", size=15, bold=True, fill="#ffffff", stroke="#ffffff")[0])

    # Вертикальні осі часу
    client_x = 180
    server_x = 640
    y_start = 65
    y_end = 365

    # Стовпчики-осі
    frags.append(line(client_x, y_start, client_x, y_end, color=LINE, sw=2.5))
    frags.append(line(server_x, y_start, server_x, y_end, color=LINE, sw=2.5))
    frags.append(arrow(client_x, y_end - 5, client_x, y_end + 20, color=LINE, sw=2.5))
    frags.append(arrow(server_x, y_end - 5, server_x, y_end + 20, color=LINE, sw=2.5))

    # Підписи осей
    frags.append(textbox(client_x, y_start - 12, "Клієнт (локальний годинник t_c)", size=13, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    frags.append(textbox(server_x, y_start - 12, "Сервер (еталонний годинник t_s)", size=13, bold=True, fill="#fdecea", stroke=POS)[0])

    # Точки та мітки часу
    t1_y = 110
    t2_y = 175
    t3_y = 240
    t4_y = 305

    # T1: клієнт відправляє
    frags.append(circle(client_x, t1_y, 5, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(textbox(client_x - 90, t1_y, "T1 (Origin)\nВідправка клієнтом", size=11, bold=True, fill="#ffffff", stroke=NEG, pad=4)[0])

    # T2: сервер приймає
    frags.append(circle(server_x, t2_y, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(textbox(server_x + 95, t2_y, "T2 (Receive)\nПрийом сервером", size=11, bold=True, fill="#ffffff", stroke=POS, pad=4)[0])

    # Пакет від клієнта до сервера
    frags.append(arrow(client_x, t1_y, server_x, t2_y, color=NEG, sw=2))
    frags.append(fitbox(350, 120, 160, 26, "NTP Request (Запит)\n[Мітка T1]", size=10, fill="#ffffff", stroke=NEG, pad=3))

    # Обробка на сервері (T2 -> T3)
    frags.append(line(server_x + 12, t2_y, server_x + 12, t3_y, color=POS, sw=2, dash="3,3"))
    frags.append(fitbox(server_x + 85, (t2_y + t3_y) / 2, 130, 24, "Обробка на сервері:\n(T3 − T2)", size=9, fill="#fff8e7", stroke=POS, pad=3))

    # T3: сервер відправляє
    frags.append(circle(server_x, t3_y, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(textbox(server_x + 95, t3_y, "T3 (Transmit)\nВідправка сервером", size=11, bold=True, fill="#ffffff", stroke=POS, pad=4)[0])

    # T4: клієнт приймає
    frags.append(circle(client_x, t4_y, 5, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(textbox(client_x - 90, t4_y, "T4 (Destination)\nПрийом клієнтом", size=11, bold=True, fill="#ffffff", stroke=NEG, pad=4)[0])

    # Пакет-відповідь від сервера до клієнта
    frags.append(arrow(server_x, t3_y, client_x, t4_y, color=POS, sw=2))
    frags.append(fitbox(320, 250, 220, 28, "NTP Response (Відповідь)\n[Мітки: T1 (Origin), T2 (Rx), T3 (Tx)]", size=10, fill="#ffffff", stroke=POS, pad=3))

    # Загальний інтервал на клієнті
    frags.append(line(client_x - 12, t1_y, client_x - 12, t4_y, color=NEG, sw=2, dash="3,3"))
    frags.append(fitbox(client_x - 145, (t1_y + t4_y) / 2, 120, 24, "Час обміну:\n(T4 − T1)", size=9, fill="#eaf0fd", stroke=NEG, pad=3))

    # Блок формул унизу
    box_calc, _, _ = textbox(410, 415, "Кругова затримка (Round-Trip Delay): δ = (T4 − T1) − (T3 − T2)\nЗміщення годинника (Clock Offset): θ = ((T2 − T1) + (T3 − T4)) / 2", size=12, bold=True, pad=8, fill="#f4fbf7", stroke=FIELD, min_w=680)
    frags.append(box_calc)

    render(os.path.join(IMG_DIR, "fig-four-timestamps.svg"), w, h, *frags)


def make_fig_marzullo_intersection():
    """Алгоритм перетину інтервалів Марзулло для відсікання помилкових джерел (falsetickers)."""
    w, h = 820, 430
    frags = []

    # Заголовок
    frags.append(textbox(410, 24, "Алгоритм Марзулло: знаходження інтервалу істинного часу", size=15, bold=True, fill="#ffffff", stroke="#ffffff")[0])

    x_left = 80
    x_right = 740
    axis_y = 355

    # Джерела та їхні довірчі інтервали
    # S1: [-30, +10], центр -10
    # S2: [-15, +25], центр +5
    # S3: [-5, +35], центр +15
    # S4 (Falseticker): [+48, +88], центр +68
    # Шкала: від -60 до +100 мс. Нуль на x=320. 1 мс = 3.5 px.
    def to_x(val):
        return 320 + val * 3.5

    # Рядки джерел
    sources = [
        ("Сервер 1 (Truechimer)", -30, 10, -10, 75, "#27ae60", True),
        ("Сервер 2 (Truechimer)", -15, 25, 5, 125, "#27ae60", True),
        ("Сервер 3 (Truechimer)", -5, 35, 15, 175, "#27ae60", True),
        ("Сервер 4 (Falseticker — збійний!)", 48, 88, 68, 225, "#c0392b", False),
    ]

    for name, left_val, right_val, center_val, y_pos, col, is_ok in sources:
        x1 = to_x(left_val)
        x2 = to_x(right_val)
        xc = to_x(center_val)

        # Назва зліва
        frags.append(text(x_left + 10, y_pos - 10, name, size=11, bold=True, color=col, anchor="start"))

        # Відрізок довірчого інтервалу [θ_i - Λ_i, θ_i + Λ_i]
        frags.append(line(x1, y_pos, x2, y_pos, color=col, sw=4))
        # Кінці інтервалу
        frags.append(line(x1, y_pos - 6, x1, y_pos + 6, color=col, sw=2))
        frags.append(line(x2, y_pos - 6, x2, y_pos + 6, color=col, sw=2))
        # Центр (оцінка θ_i)
        frags.append(circle(xc, y_pos, 4, fill=col, stroke=LINE, sw=1.2))

        # Підписи значень
        frags.append(text(x1, y_pos + 15, "%d мс" % left_val, size=9, color=MUTED))
        frags.append(text(x2, y_pos + 15, "%d мс" % right_val, size=9, color=MUTED))
        frags.append(text(xc, y_pos - 8, "θ=%d" % center_val, size=10, bold=True, color=col))

    # Виділення області перетину істинних серверів (S1 ∩ S2 ∩ S3)
    # Перетин: [-5, +10]
    inter_x1 = to_x(-5)
    inter_x2 = to_x(10)
    frags.append(rect(inter_x1, 55, inter_x2 - inter_x1, 230, fill="#27ae60", stroke="#27ae60", sw=1.5, rx=0))
    # Напівпрозоре накриття
    frags.append('<rect x="%.1f" y="55" width="%.1f" height="230" fill="#27ae60" opacity="0.12"/>' % (inter_x1, inter_x2 - inter_x1))

    # Стрілки проекції на результат
    frags.append(line(inter_x1, 285, inter_x1, 335, color=FIELD, sw=1.5, dash="3,3"))
    frags.append(line(inter_x2, 285, inter_x2, 335, color=FIELD, sw=1.5, dash="3,3"))

    # Підсумковий інтервал
    frags.append(rect(inter_x1, 295, inter_x2 - inter_x1, 24, fill="#27ae60", stroke=FIELD, sw=2, rx=4))
    frags.append(fitbox(inter_x1 - 160, 292, 150, 30, "Інтервал перетину:\n[−5 мс .. +10 мс]", size=10, bold=True, fill="#ffffff", stroke=FIELD, pad=3))

    # Вісь часу унизу
    frags.append(line(x_left, axis_y, x_right, axis_y, color=LINE, sw=2))
    frags.append(arrow(x_right - 5, axis_y, x_right + 15, axis_y, color=LINE, sw=2))
    frags.append(text(x_right + 20, axis_y + 4, "Δt (мс)", size=11, bold=True, anchor="start"))

    # Поділки осі
    for tick_val in [-50, -25, 0, 25, 50, 75, 100]:
        tx = to_x(tick_val)
        frags.append(line(tx, axis_y - 4, tx, axis_y + 4, color=LINE, sw=1.5))
        frags.append(text(tx, axis_y + 16, "%d" % tick_val, size=10, color=INK if tick_val == 0 else MUTED, bold=(tick_val == 0)))

    # Висновок алгоритму
    box_res, _, _ = textbox(410, 395, "Результат Марзулло: Сервери 1, 2, 3 узгоджені (Truechimers), їхній перетин гарантовано містить точний час.\nСервер 4 відкинуто як некоректний (Falseticker), бо його інтервал не перетинає спільну більшість (m = n − f = 3).", size=11, pad=6, fill="#f4f6f8", stroke=LINE, min_w=740)
    frags.append(box_res)

    render(os.path.join(IMG_DIR, "fig-marzullo-intersection.svg"), w, h, *frags)


def make_fig_slew_vs_step():
    """Порівняння підведення годинника: Clock Step проти Clock Slew (adjtime)."""
    w, h = 820, 420
    frags = []

    # Заголовок
    frags.append(textbox(410, 24, "Дисципліна локального годинника: Стрибок часу (Step) проти Плавного підведення (Slew)", size=15, bold=True, fill="#ffffff", stroke="#ffffff")[0])

    # Ліва половина: Clock Step
    box_l_title, _, _ = textbox(210, 65, "Стрибок часу (Clock Step: settimeofday)", size=13, bold=True, fill="#fdecea", stroke=POS, min_w=340)
    frags.append(box_l_title)

    # Графік Step
    # Осі
    lx0, ly0 = 60, 240
    lx_max, ly_max = 350, 110
    frags.append(line(lx0, ly0, lx_max, ly0, color=LINE, sw=1.5))
    frags.append(arrow(lx_max - 5, ly0, lx_max + 10, ly0, color=LINE, sw=1.5))
    frags.append(line(lx0, ly0, lx0, ly_max, color=LINE, sw=1.5))
    frags.append(arrow(lx0, ly_max + 5, lx0, ly_max - 10, color=LINE, sw=1.5))
    frags.append(text(lx_max + 5, ly0 + 16, "Справжній час t", size=10, color=MUTED, anchor="end"))
    frags.append(text(lx0 - 5, ly_max - 5, "Системний час T(t)", size=10, color=MUTED, anchor="start"))

    # Еталонна лінія (пунктир 45 градусів)
    frags.append(line(lx0, ly0, lx0 + 260, ly0 - 130, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(text(lx0 + 200, ly0 - 110, "Еталонний час", size=9, color=MUTED, italic=True))

    # Лінія системного часу зі стрибком назад
    frags.append(line(lx0, ly0 - 25, lx0 + 110, ly0 - 80, color=POS, sw=2.5))
    frags.append(circle(lx0 + 110, ly0 - 80, 4, fill=POS, stroke=LINE))
    # Стрибок униз (дисконтинуїтет)
    frags.append(line(lx0 + 110, ly0 - 80, lx0 + 110, ly0 - 55, color=POS, sw=2, dash="3,3"))
    frags.append(arrow(lx0 + 110, ly0 - 75, lx0 + 110, ly0 - 57, color=POS, sw=2))
    frags.append(circle(lx0 + 110, ly0 - 55, 4, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(line(lx0 + 110, ly0 - 55, lx0 + 240, ly0 - 120, color=POS, sw=2.5))

    # Підпис небезпеки
    box_warn, _, _ = textbox(210, 285, "Небезпека: порушення монотонності!\n• Час рухається назад або стрибає вперед\n• Таймери та тайм-аути спрацьовують некоректно\n• Ламається порядок записів у базах даних та логах", size=10, pad=6, fill="#fff5f5", stroke=POS, min_w=340)
    frags.append(box_warn)

    # Права половина: Clock Slew
    box_r_title, _, _ = textbox(610, 65, "Плавне підведення (Clock Slew: adjtime / PLL)", size=13, bold=True, fill="#f4fbf7", stroke=FIELD, min_w=340)
    frags.append(box_r_title)

    # Графік Slew
    rx0, ry0 = 460, 240
    rx_max, ry_max = 750, 110
    frags.append(line(rx0, ry0, rx_max, ry0, color=LINE, sw=1.5))
    frags.append(arrow(rx_max - 5, ry0, rx_max + 10, ry0, color=LINE, sw=1.5))
    frags.append(line(rx0, ry0, rx0, ry_max, color=LINE, sw=1.5))
    frags.append(arrow(rx0, ry_max + 5, rx0, ry_max - 10, color=LINE, sw=1.5))
    frags.append(text(rx_max + 5, ry0 + 16, "Справжній час t", size=10, color=MUTED, anchor="end"))
    frags.append(text(rx0 - 5, ry_max - 5, "Системний час T(t)", size=10, color=MUTED, anchor="start"))

    # Еталонна лінія
    frags.append(line(rx0, ry0, rx0 + 260, ry0 - 130, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(text(rx0 + 200, ry0 - 110, "Еталонний час", size=9, color=MUTED, italic=True))

    # Лінія системного часу з плавним вигином
    # Початковий дрейф (випередження)
    frags.append(line(rx0, ry0 - 25, rx0 + 80, ry0 - 65, color=FIELD, sw=2.5))
    # Плавне уповільнення частоти генератора (менший нахил)
    frags.append(line(rx0 + 80, ry0 - 65, rx0 + 180, ry0 - 90, color=FIELD, sw=2.5))
    # Вихід на еталон
    frags.append(line(rx0 + 180, ry0 - 90, rx0 + 250, ry0 - 125, color=FIELD, sw=2.5))
    frags.append(fitbox(rx0 + 85, ry0 - 105, 140, 22, "Сповільнення ходу (−500 ppm)", size=9, fill="#ffffff", stroke=FIELD, pad=2))

    # Підпис переваг
    box_good, _, _ = textbox(610, 285, "Перевага: сувора монотонність часу!\n• Частота тактового таймера коригується на ±500 ppm\n• Час безперервний, жодних стрибків і збоїв таймерів\n• Застосовується для зміщень < 128 мс (NTP стандарт)", size=10, pad=6, fill="#f4fbf7", stroke=FIELD, min_w=340)
    frags.append(box_good)

    # Порівняльний висновок
    box_bot, _, _ = textbox(410, 385, "Правило NTP: Якщо |θ| < 128 мс — виконується плавне підведення Slew (adjtime).\nЯкщо 128 мс ≤ |θ| < 1000 с — виконується Step (разовий стрибок). Якщо |θ| ≥ 1000 с — паніка (NTPd зупиняється).", size=11, bold=True, pad=6, fill=FILL, stroke=LINE, min_w=740)
    frags.append(box_bot)

    render(os.path.join(IMG_DIR, "fig-slew-vs-step.svg"), w, h, *frags)


def make_fig_packet_layout():
    """Структура 48-байтного бінарного заголовка NTP v4."""
    w, h = 820, 480
    frags = []

    # Заголовок
    frags.append(textbox(410, 22, "Двійкова структура 48-байтного пакета NTPv4 (RFC 5905)", size=15, bold=True, fill="#ffffff", stroke="#ffffff")[0])

    # Шкала бітів: 0..31
    x_start = 50
    total_w = 720
    col_w = total_w / 32.0
    y_start = 50

    # Шапка бітів
    frags.append(rect(x_start, y_start, total_w, 20, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=0))
    for bit in [0, 2, 5, 8, 16, 24, 31]:
        bx = x_start + bit * col_w
        frags.append(text(bx + col_w / 2, y_start + 14, str(bit), size=10, bold=True, color=MUTED))

    # Стовпчик 1: LI (2 біти), VN (3 біти), Mode (3 біти), Stratum (8 бітів), Poll (8 бітів), Precision (8 бітів)
    y1 = y_start + 20
    h_row = 38
    w_li = 2 * col_w
    w_vn = 3 * col_w
    w_mode = 3 * col_w
    w_stratum = 8 * col_w
    w_poll = 8 * col_w
    w_prec = 8 * col_w

    frags.append(fitbox(x_start, y1, w_li, h_row, "LI\n(2b)", size=10, bold=True, fill="#fdecea", stroke=POS, pad=2))
    frags.append(fitbox(x_start + w_li, y1, w_vn, h_row, "VN\n(3b)", size=10, bold=True, fill="#eaf0fd", stroke=NEG, pad=2))
    frags.append(fitbox(x_start + w_li + w_vn, y1, w_mode, h_row, "Mode\n(3b)", size=10, bold=True, fill="#f4fbf7", stroke=FIELD, pad=2))
    frags.append(fitbox(x_start + w_li + w_vn + w_mode, y1, w_stratum, h_row, "Stratum (8b)\n0..16", size=10, bold=True, fill=FILL, stroke=LINE, pad=2))
    frags.append(fitbox(x_start + w_li + w_vn + w_mode + w_stratum, y1, w_poll, h_row, "Poll (8b)\nlog2 інтервалу", size=10, bold=True, fill=FILL, stroke=LINE, pad=2))
    frags.append(fitbox(x_start + w_li + w_vn + w_mode + w_stratum + w_poll, y1, w_prec, h_row, "Precision (8b)\nlog2 точності", size=10, bold=True, fill=FILL, stroke=LINE, pad=2))

    # Рядок 2: Root Delay (32 біти)
    y2 = y1 + h_row
    frags.append(fitbox(x_start, y2, total_w / 2, h_row, "Root Delay: Ціла частина секунд (16 бітів)", size=11, fill="#f9f9f9", stroke=LINE, pad=4))
    frags.append(fitbox(x_start + total_w / 2, y2, total_w / 2, h_row, "Root Delay: Дробова частина (16 бітів)", size=11, fill="#f9f9f9", stroke=LINE, pad=4))

    # Рядок 3: Root Dispersion (32 біти)
    y3 = y2 + h_row
    frags.append(fitbox(x_start, y3, total_w / 2, h_row, "Root Dispersion: Ціла частина (16 бітів)", size=11, fill="#f9f9f9", stroke=LINE, pad=4))
    frags.append(fitbox(x_start + total_w / 2, y3, total_w / 2, h_row, "Root Dispersion: Дробова частина (16 бітів)", size=11, fill="#f9f9f9", stroke=LINE, pad=4))

    # Рядок 4: Reference ID (32 біти)
    y4 = y3 + h_row
    frags.append(fitbox(x_start, y4, total_w, h_row, "Reference ID: 4 ASCII символи (GPS, PPS, ATOM) або IPv4 адреса джерела (32 біти)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, pad=4))

    # Рядок 5: Reference Timestamp (64 біти)
    y5 = y4 + h_row
    frags.append(fitbox(x_start, y5, total_w / 2, h_row, "Reference Timestamp: Секунди від 1900-01-01 (32 біти)", size=10.5, fill="#ffffff", stroke=LINE, pad=3))
    frags.append(fitbox(x_start + total_w / 2, y5, total_w / 2, h_row, "Reference Timestamp: Дріб (~232 пс роздільність, 32 біти)", size=10.5, fill="#ffffff", stroke=LINE, pad=3))

    # Рядок 6: Origin Timestamp T1 (64 біти)
    y6 = y5 + h_row
    frags.append(fitbox(x_start, y6, total_w / 2, h_row, "Origin Timestamp T1: Секунди відправки клієнтом (32 біти)", size=10.5, fill="#fdecea", stroke=POS, pad=3))
    frags.append(fitbox(x_start + total_w / 2, y6, total_w / 2, h_row, "Origin Timestamp T1: Дробова частина (32 біти)", size=10.5, fill="#fdecea", stroke=POS, pad=3))

    # Рядок 7: Receive Timestamp T2 (64 біти)
    y7 = y6 + h_row
    frags.append(fitbox(x_start, y7, total_w / 2, h_row, "Receive Timestamp T2: Секунди прийому сервером (32 біти)", size=10.5, fill="#f4fbf7", stroke=FIELD, pad=3))
    frags.append(fitbox(x_start + total_w / 2, y7, total_w / 2, h_row, "Receive Timestamp T2: Дробова частина (32 біти)", size=10.5, fill="#f4fbf7", stroke=FIELD, pad=3))

    # Рядок 8: Transmit Timestamp T3 (64 біти)
    y8 = y7 + h_row
    frags.append(fitbox(x_start, y8, total_w / 2, h_row, "Transmit Timestamp T3: Секунди відправки сервером (32 біти)", size=10.5, fill="#eaf0fd", stroke=NEG, pad=3))
    frags.append(fitbox(x_start + total_w / 2, y8, total_w / 2, h_row, "Transmit Timestamp T3: Дробова частина (32 біти)", size=10.5, fill="#eaf0fd", stroke=NEG, pad=3))

    # Довідковий підпис унізу
    y_info = y8 + h_row + 15
    frags.append(fitbox(x_start, y_info, total_w, 32, "Разом: 48 байтів основного заголовка (12 32-бітних слів). Порядок байтів — суворо Big-Endian (Network Byte Order).\nЗаголовок може розширюватися полями Extension Fields та криптографічними мітками NTS / MAC.", size=10, fill=FILL, stroke=MUTED, pad=4))

    render(os.path.join(IMG_DIR, "fig-packet-layout.svg"), w, h, *frags)


def main():
    print("Генерація SVG-фігур для ntp-sync...")
    make_fig_stratum_hierarchy()
    make_fig_four_timestamps()
    make_fig_marzullo_intersection()
    make_fig_slew_vs_step()
    make_fig_packet_layout()
    print("Усі 5 фігур успішно згенеровано у %s" % IMG_DIR)


if __name__ == "__main__":
    main()
