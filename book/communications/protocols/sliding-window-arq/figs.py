# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. pipelining-vs-stop-wait: Порівняння Stop-and-Wait та Pipelined ковзного вікна ──
def fig_pipelining_vs_stop_wait():
    W, H = 840, 480
    p = []

    # Заголовки колонок
    p.append(textbox(215, 30, "Stop-and-Wait ARQ (W = 1): простій каналу", size=12.5, bold=True, fill="#fff3cd", stroke="#e0a800")[0])
    p.append(textbox(625, 30, "Pipelined ARQ (W = 4): безперервна передача", size=12.5, bold=True, fill="#eef6ef", stroke=FIELD)[0])

    # ── Ліва колонка: Stop-and-Wait ──
    tx_l, rx_l = 80, 350
    p.append(text(tx_l, 68, "TX", size=12, color=INK, bold=True))
    p.append(text(rx_l, 68, "RX", size=12, color=INK, bold=True))
    p.append(line(tx_l, 80, tx_l, 440, color=LINE, sw=1.5))
    p.append(line(rx_l, 80, rx_l, 440, color=LINE, sw=1.5))
    p.append(arrow(tx_l, 430, tx_l, 455, color=LINE, sw=1.5))
    p.append(arrow(rx_l, 430, rx_l, 455, color=LINE, sw=1.5))

    # Кадр 0
    p.append(rect(tx_l - 12, 90, 24, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(tx_l, 108, "П₀", size=10, color=NEG, bold=True))
    p.append(arrow(tx_l + 12, 90, rx_l - 12, 140, color=NEG, sw=1.5))
    p.append(arrow(tx_l + 12, 120, rx_l - 12, 170, color=NEG, sw=1.5))
    p.append(text(215, 120, "Пакет 0", size=10, color=NEG, bold=True))

    # ACK 0
    p.append(arrow(rx_l - 12, 170, tx_l + 12, 220, color=FIELD, sw=1.5))
    p.append(text(215, 202, "ACK 0", size=10, color=FIELD, bold=True))

    # Простій 1
    p.append(rect(tx_l + 14, 120, 10, 100, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=2))
    p.append(text(tx_l + 32, 170, "Простій (RTT)", size=9.5, color="#856404", anchor="start", italic=True))

    # Кадр 1
    p.append(rect(tx_l - 12, 225, 24, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(tx_l, 243, "П₁", size=10, color=NEG, bold=True))
    p.append(arrow(tx_l + 12, 225, rx_l - 12, 275, color=NEG, sw=1.5))
    p.append(arrow(tx_l + 12, 255, rx_l - 12, 305, color=NEG, sw=1.5))
    p.append(text(215, 255, "Пакет 1", size=10, color=NEG, bold=True))

    # ACK 1
    p.append(arrow(rx_l - 12, 305, tx_l + 12, 355, color=FIELD, sw=1.5))
    p.append(text(215, 337, "ACK 1", size=10, color=FIELD, bold=True))

    # Простій 2
    p.append(rect(tx_l + 14, 255, 10, 100, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=2))
    p.append(text(tx_l + 32, 305, "Простій (RTT)", size=9.5, color="#856404", anchor="start", italic=True))

    # Кадр 2
    p.append(rect(tx_l - 12, 360, 24, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(tx_l, 378, "П₂", size=10, color=NEG, bold=True))
    p.append(arrow(tx_l + 12, 360, rx_l - 12, 410, color=NEG, sw=1.5))
    p.append(arrow(tx_l + 12, 390, rx_l - 12, 440, color=NEG, sw=1.5))

    # Розділювач колонок
    p.append(line(420, 50, 420, 450, color=MUTED, sw=1, dash="4 4"))

    # ── Права колонка: Pipelined ковзне вікно ──
    tx_r, rx_r = 490, 760
    p.append(text(tx_r, 68, "TX", size=12, color=INK, bold=True))
    p.append(text(rx_r, 68, "RX", size=12, color=INK, bold=True))
    p.append(line(tx_r, 80, tx_r, 440, color=LINE, sw=1.5))
    p.append(line(rx_r, 80, rx_r, 440, color=LINE, sw=1.5))
    p.append(arrow(tx_r, 430, tx_r, 455, color=LINE, sw=1.5))
    p.append(arrow(rx_r, 430, rx_r, 455, color=LINE, sw=1.5))

    # Пакет 0, 1, 2, 3 безперервно
    colors = ["#eaf0fd", "#eef6ef", "#fdf6e2", "#f3e8fd"]
    strokes = [NEG, FIELD, "#b58900", "#6c71c4"]
    for i in range(4):
        y_top = 90 + i * 28
        p.append(rect(tx_r - 12, y_top, 24, 26, fill=colors[i], stroke=strokes[i], sw=1.4, rx=2))
        p.append(text(tx_r, y_top + 17, "П%d" % i, size=9.5, color=strokes[i], bold=True))
        p.append(arrow(tx_r + 12, y_top, rx_r - 12, y_top + 50, color=strokes[i], sw=1.4))
        p.append(arrow(tx_r + 12, y_top + 26, rx_r - 12, y_top + 76, color=strokes[i], sw=1.4))

    p.append(text(625, 115, "Конвеєр: П₀, П₁, П₂, П₃", size=10.5, color=NEG, bold=True))

    # Зворотні ACK
    for i in range(4):
        y_ack_rx = 166 + i * 28
        y_ack_tx = y_ack_rx + 50
        p.append(arrow(rx_r - 12, y_ack_rx, tx_r + 12, y_ack_tx, color=FIELD, sw=1.4))
        p.append(text(625, y_ack_rx + 30, "ACK %d" % i, size=9.5, color=FIELD, bold=True))

    # Наступні пакети 4, 5 після надходження ACK
    p.append(rect(tx_r - 12, 216, 24, 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=2))
    p.append(text(tx_r, 233, "П₄", size=9.5, color=NEG, bold=True))
    p.append(arrow(tx_r + 12, 216, rx_r - 12, 266, color=NEG, sw=1.4))
    p.append(arrow(tx_r + 12, 242, rx_r - 12, 292, color=NEG, sw=1.4))

    p.append(rect(tx_r - 12, 244, 24, 26, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=2))
    p.append(text(tx_r, 261, "П₅", size=9.5, color=FIELD, bold=True))
    p.append(arrow(tx_r + 12, 244, rx_r - 12, 294, color=FIELD, sw=1.4))
    p.append(arrow(tx_r + 12, 270, rx_r - 12, 320, color=FIELD, sw=1.4))

    p.append(text(625, 410, "Канал передавача утилізований на 100%", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "pipelining-vs-stop-wait.svg"), W, H, *p,
           title="Порівняння Stop-and-Wait та Pipelined ковзного вікна")


# ── 2. go-back-n-operation: Алгоритм Go-Back-N при втраті кадру ──
def fig_go_back_n_operation():
    W, H = 860, 520
    p = []

    tx_x, rx_x = 110, 660
    p.append(text(tx_x, 30, "Передавач TX (W_s = 4)", size=12.5, color=INK, bold=True))
    p.append(text(rx_x, 30, "Приймач RX (W_r = 1)", size=12.5, color=INK, bold=True))

    p.append(line(tx_x, 45, tx_x, 490, color=LINE, sw=1.6))
    p.append(line(rx_x, 45, rx_x, 490, color=LINE, sw=1.6))
    p.append(arrow(tx_x, 480, tx_x, 505, color=LINE, sw=1.6))
    p.append(arrow(rx_x, 480, rx_x, 505, color=LINE, sw=1.6))

    # Кадри 0, 1, 2, 3 надсилаються
    # Кадр 0 успішний
    p.append(arrow(tx_x, 60, rx_x, 110, color=NEG, sw=1.5))
    p.append(text(280, 75, "Кадр 0", size=10, color=NEG, bold=True))
    p.append(arrow(rx_x, 110, tx_x, 160, color=FIELD, sw=1.5))
    p.append(text(500, 142, "ACK 0", size=10, color=FIELD, bold=True))

    # Кадр 1 губиться
    p.append(line(tx_x, 90, 380, 125, color=POS, sw=1.6))
    p.append(circle(380, 125, 11, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(380, 129, "✗", size=13, color=POS, bold=True))
    p.append(text(405, 128, "Кадр 1 втрачено", size=10, color=POS, bold=True, anchor="start"))

    # Кадр 2 доходить, але відкидається (RX чекає 1)
    p.append(arrow(tx_x, 120, rx_x, 170, color=MUTED, sw=1.4))
    p.append(text(280, 135, "Кадр 2", size=10, color=MUTED))
    p.append(textbox(rx_x + 95, 165, "Відкинуто!\nОчікується 1", size=9.5, fill="#fdecea", stroke=POS)[0])
    p.append(arrow(rx_x, 170, tx_x, 220, color=FIELD, sw=1.4))
    p.append(text(500, 202, "ACK 0 (дублікат)", size=9.5, color=FIELD))

    # Кадр 3 доходить, але відкидається
    p.append(arrow(tx_x, 150, rx_x, 215, color=MUTED, sw=1.4))
    p.append(text(280, 170, "Кадр 3", size=10, color=MUTED))
    p.append(textbox(rx_x + 95, 220, "Відкинуто!\nОчікується 1", size=9.5, fill="#fdecea", stroke=POS)[0])
    p.append(arrow(rx_x, 215, tx_x, 265, color=FIELD, sw=1.4))
    p.append(text(500, 247, "ACK 0 (дублікат)", size=9.5, color=FIELD))

    # Таймаут на TX для Кадру 1
    p.append(line(tx_x - 35, 90, tx_x - 35, 285, color=POS, sw=1.5, dash="4 3"))
    p.append(line(tx_x - 45, 90, tx_x - 25, 90, color=POS, sw=1.5))
    p.append(line(tx_x - 45, 285, tx_x - 25, 285, color=POS, sw=1.5))
    p.append(text(tx_x - 50, 190, "Таймаут кадру 1", size=10, color=POS, bold=True, anchor="end"))

    # Повторна передача ВСЬОГО вікна починаючи з 1 (Go-Back-N)
    p.append(textbox(tx_x + 5, 310, "Go-Back-N:\nповтор 1, 2, 3, 4", size=10, fill="#fff3cd", stroke="#e0a800")[0])

    p.append(arrow(tx_x, 340, rx_x, 390, color=NEG, sw=1.5))
    p.append(text(280, 355, "Кадр 1 (повтор)", size=10, color=NEG, bold=True))
    p.append(arrow(rx_x, 390, tx_x, 440, color=FIELD, sw=1.5))
    p.append(text(500, 422, "ACK 1", size=10, color=FIELD, bold=True))

    p.append(arrow(tx_x, 370, rx_x, 420, color=NEG, sw=1.5))
    p.append(text(280, 385, "Кадр 2 (повтор)", size=10, color=NEG, bold=True))
    p.append(arrow(rx_x, 420, tx_x, 470, color=FIELD, sw=1.5))
    p.append(text(500, 452, "ACK 2", size=10, color=FIELD, bold=True))

    p.append(arrow(tx_x, 400, rx_x, 450, color=NEG, sw=1.5))
    p.append(text(280, 415, "Кадр 3 (повтор)", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "go-back-n-operation.svg"), W, H, *p,
           title="Робота протоколу Go-Back-N при втраті пакета")


# ── 3. selective-repeat-operation: Алгоритм Selective Repeat при втраті кадру ──
def fig_selective_repeat_operation():
    W, H = 860, 520
    p = []

    tx_x, rx_x = 110, 660
    p.append(text(tx_x, 30, "Передавач TX (W_s = 4)", size=12.5, color=INK, bold=True))
    p.append(text(rx_x, 30, "Приймач RX (W_r = 4)", size=12.5, color=INK, bold=True))

    p.append(line(tx_x, 45, tx_x, 490, color=LINE, sw=1.6))
    p.append(line(rx_x, 45, rx_x, 490, color=LINE, sw=1.6))
    p.append(arrow(tx_x, 480, tx_x, 505, color=LINE, sw=1.6))
    p.append(arrow(rx_x, 480, rx_x, 505, color=LINE, sw=1.6))

    # Кадр 0 успішний
    p.append(arrow(tx_x, 60, rx_x, 110, color=NEG, sw=1.5))
    p.append(text(280, 75, "Кадр 0", size=10, color=NEG, bold=True))
    p.append(arrow(rx_x, 110, tx_x, 160, color=FIELD, sw=1.5))
    p.append(text(500, 142, "ACK 0", size=10, color=FIELD, bold=True))

    # Кадр 1 губиться
    p.append(line(tx_x, 90, 380, 125, color=POS, sw=1.6))
    p.append(circle(380, 125, 11, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(380, 129, "✗", size=13, color=POS, bold=True))
    p.append(text(405, 128, "Кадр 1 втрачено", size=10, color=POS, bold=True, anchor="start"))

    # Кадр 2 доходить і буферизується на RX!
    p.append(arrow(tx_x, 120, rx_x, 170, color=NEG, sw=1.4))
    p.append(text(280, 135, "Кадр 2", size=10, color=NEG))
    p.append(textbox(rx_x + 95, 165, "Буферизовано!\n(чекає 1)", size=9.5, fill="#eef6ef", stroke=FIELD)[0])
    p.append(arrow(rx_x, 170, tx_x, 220, color=FIELD, sw=1.4))
    p.append(text(500, 202, "ACK 2 (вибірковий)", size=9.5, color=FIELD, bold=True))

    # Кадр 3 доходить і буферизується на RX!
    p.append(arrow(tx_x, 150, rx_x, 215, color=NEG, sw=1.4))
    p.append(text(280, 170, "Кадр 3", size=10, color=NEG))
    p.append(textbox(rx_x + 95, 220, "Буферизовано!\n(чекає 1)", size=9.5, fill="#eef6ef", stroke=FIELD)[0])
    p.append(arrow(rx_x, 215, tx_x, 265, color=FIELD, sw=1.4))
    p.append(text(500, 247, "ACK 3 (вибірковий)", size=9.5, color=FIELD, bold=True))

    # Таймаут на TX для Кадру 1
    p.append(line(tx_x - 35, 90, tx_x - 35, 285, color=POS, sw=1.5, dash="4 3"))
    p.append(line(tx_x - 45, 90, tx_x - 25, 90, color=POS, sw=1.5))
    p.append(line(tx_x - 45, 285, tx_x - 25, 285, color=POS, sw=1.5))
    p.append(text(tx_x - 50, 190, "Таймаут кадру 1", size=10, color=POS, bold=True, anchor="end"))

    # Повторна передача ТІЛЬКИ Кадру 1 (Selective Repeat)
    p.append(textbox(tx_x + 5, 310, "Selective Repeat:\nповтор ТІЛЬКИ 1", size=10, fill="#eef6ef", stroke=FIELD)[0])

    p.append(arrow(tx_x, 340, rx_x, 390, color=NEG, sw=1.6))
    p.append(text(280, 355, "Кадр 1 (вибірковий повтор)", size=10, color=NEG, bold=True))

    # Приймач отримує 1 і зшиває буфер 1, 2, 3 -> віддає додатку!
    p.append(textbox(rx_x + 95, 390, "Отримано 1!\nЗшито 1,2,3 -> стек", size=9.5, fill="#eaf0fd", stroke=NEG)[0])
    p.append(arrow(rx_x, 390, tx_x, 440, color=FIELD, sw=1.5))
    p.append(text(500, 422, "ACK 1", size=10, color=FIELD, bold=True))

    # Передавач зрушує вікно відразу на 4 позиції вперед!
    p.append(arrow(tx_x, 445, rx_x, 495, color=NEG, sw=1.4))
    p.append(text(280, 460, "Кадр 4 (нове вікно)", size=10, color=NEG))

    render(os.path.join(OUT, "selective-repeat-operation.svg"), W, H, *p,
           title="Робота протоколу Selective Repeat при втраті пакета")


# ── 4. sequence-space-wrap: Кільцевий простір номерів та колізія перекриття ──
def fig_sequence_space_wrap():
    import math
    W, H = 840, 430
    p = []

    # ── Ліва частина: Коректне вікно W_s + W_r <= 2^k (W = 4, M = 8) ──
    cx1, cy1, r = 210, 210, 110
    p.append(textbox(cx1, 35, "Коректно: W_s + W_r <= 2^k\n(W_s = 4, W_r = 4, M = 8)", size=11, bold=True, fill="#eef6ef", stroke=FIELD)[0])

    p.append(circle(cx1, cy1, r, fill="none", stroke=LINE, sw=2))

    for i in range(8):
        ang = -math.pi / 2 + i * (2 * math.pi / 8)
        x = cx1 + r * math.cos(ang)
        y = cy1 + r * math.sin(ang)

        # Кольори секторів
        if i in [0, 1, 2, 3]:
            # Вікно TX [0..3]
            p.append(circle(x, y, 14, fill="#eaf0fd", stroke=NEG, sw=1.8))
            p.append(text(x, y + 4.5, str(i), size=11, color=NEG, bold=True))
        else:
            # Наступне вікно RX [4..7]
            p.append(circle(x, y, 14, fill="#eef6ef", stroke=FIELD, sw=1.8))
            p.append(text(x, y + 4.5, str(i), size=11, color=FIELD, bold=True))

    p.append(text(cx1, cy1 - 15, "Немає", size=13, color=FIELD, bold=True))
    p.append(text(cx1, cy1 + 8, "перекриття", size=13, color=FIELD, bold=True))
    p.append(text(cx1, cy1 + 28, "вікон!", size=11, color=FIELD))

    # ── Права частина: Помилкове вікно W_s + W_r > 2^k (W = 5, M = 8) ──
    cx2, cy2 = 630, 210
    p.append(textbox(cx2, 35, "Помилка: W_s + W_r > 2^k\n(W_s = 5, W_r = 5, M = 8)", size=11, bold=True, fill="#fdecea", stroke=POS)[0])

    p.append(circle(cx2, cy2, r, fill="none", stroke=LINE, sw=2))

    for i in range(8):
        ang = -math.pi / 2 + i * (2 * math.pi / 8)
        x = cx2 + r * math.cos(ang)
        y = cy2 + r * math.sin(ang)

        if i in [0, 1]:  # Зона конфлікту!
            p.append(circle(x, y, 15, fill="#fdecea", stroke=POS, sw=2.2))
            p.append(text(x, y + 4.5, str(i), size=11, color=POS, bold=True))
        elif i in [2, 3, 4]:
            p.append(circle(x, y, 14, fill="#eaf0fd", stroke=NEG, sw=1.8))
            p.append(text(x, y + 4.5, str(i), size=11, color=NEG, bold=True))
        else:
            p.append(circle(x, y, 14, fill="#eef6ef", stroke=FIELD, sw=1.8))
            p.append(text(x, y + 4.5, str(i), size=11, color=FIELD, bold=True))

    p.append(text(cx2, cy2 - 18, "КОЛІЗІЯ 0 та 1!", size=12, color=POS, bold=True))
    p.append(text(cx2, cy2 + 4, "Старий дублікат 0", size=10, color=POS))
    p.append(text(cx2, cy2 + 22, "сприймається як новий!", size=10, color=POS, bold=True))

    p.append(textbox(420, 390, "Якщо всі ACK втрачено, повтор кадру 0 потрапляє у зміщене вікно RX [5..1] і спричиняє спотворення даних", size=10.5, fill="#fff3cd", stroke="#e0a800")[0])

    render(os.path.join(OUT, "sequence-space-wrap.svg"), W, H, *p,
           title="Кільцевий простір номерів та обмеження розміру вікна")


# ── 5. bdp-pipe-analogy: Фізична модель заповнення каналу (Bandwidth-Delay Product) ──
def fig_bdp_pipe_analogy():
    W, H = 840, 440
    p = []

    p.append(textbox(420, 30, "Модель каналу як труби: Bandwidth-Delay Product (BDP = R · RTT)", size=12.5, bold=True)[0])

    # ── Випадок 1: W < BDP (Канал недовантажений) ──
    y1 = 80
    p.append(text(40, y1 + 35, "1. Недовантаження (W << BDP):", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(rect(270, y1 + 10, 480, 50, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    # Пакети в трубі
    p.append(rect(290, y1 + 18, 50, 34, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
    p.append(text(315, y1 + 40, "П₀", size=10.5, color=NEG, bold=True))
    p.append(rect(350, y1 + 18, 50, 34, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
    p.append(text(375, y1 + 40, "П₁", size=10.5, color=NEG, bold=True))
    # Порожня зона труби
    p.append(text(580, y1 + 40, "Порожній простір (простій каналу)", size=10, color=MUTED, italic=True))
    p.append(text(760, y1 + 38, "U << 100%", size=11, color=POS, bold=True, anchor="start"))

    # ── Випадок 2: W = BDP (Оптимальне заповнення) ──
    y2 = 180
    p.append(text(40, y2 + 35, "2. Оптимальне вікно (W = BDP):", size=11.5, color=FIELD, bold=True, anchor="start"))
    p.append(rect(270, y2 + 10, 480, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    # Труба повністю заповнена пакетами
    for i in range(8):
        px = 278 + i * 58
        p.append(rect(px, y2 + 18, 52, 34, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
        p.append(text(px + 26, y2 + 40, "П%d" % i, size=10, color=NEG, bold=True))
    p.append(text(760, y2 + 38, "U = 100%", size=11, color=FIELD, bold=True, anchor="start"))

    # ── Випадок 3: W > BDP (Переповнення та bufferbloat) ──
    y3 = 280
    p.append(text(40, y3 + 35, "3. Перевантаження (W > BDP):", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(rect(270, y3 + 10, 360, 50, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    for i in range(6):
        px = 278 + i * 58
        p.append(rect(px, y3 + 18, 52, 34, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
        p.append(text(px + 26, y3 + 40, "П%d" % i, size=10, color=NEG, bold=True))
    # Буфер маршрутизатора переповнюється
    p.append(rect(640, y3 + 5, 110, 60, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(695, y3 + 28, "Черга в буфері", size=9.5, color=POS, bold=True))
    p.append(text(695, y3 + 46, "(Bufferbloat / втрати)", size=9.5, color=POS))
    p.append(text(760, y3 + 38, "Затримка ↑↑", size=11, color=POS, bold=True, anchor="start"))

    p.append(textbox(420, 395, "Оптимальний розмір вікна W* = (R · RTT) / L_frame забезпечує 100% завантаження лінії без утворення паразитної черги", size=10.5, fill="#f4f6f8", stroke=LINE)[0])

    render(os.path.join(OUT, "bdp-pipe-analogy.svg"), W, H, *p,
           title="Фізична модель заповнення каналу: Bandwidth-Delay Product")


# ── 6. throughput-vs-loss: Порівняння пропускної здатності SW, GBN та SR від імовірності втрати p ──
def fig_throughput_vs_loss():
    W, H = 840, 450
    p = []

    p.append(textbox(420, 28, "Коефіцієнт використання каналу U(p) при високій затримці (a = T_prop / T_tx = 10, W = 21)", size=11.5, bold=True)[0])

    # Осі графіка
    ox, oy = 90, 370
    gw, gh = 660, 290
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    p.append(arrow(ox + gw - 10, oy, ox + gw + 15, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - gh + 10, ox, oy - gh - 15, color=LINE, sw=1.8))

    p.append(text(ox + gw + 20, oy + 5, "p (імовірність втрати)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(ox - 10, oy - gh - 18, "U (утилізація)", size=10.5, color=INK, anchor="middle", bold=True))

    # Позначки осі Y (0% .. 100%)
    for i in range(5):
        val = i * 25
        y = oy - (val / 100.0) * gh
        p.append(line(ox - 5, y, ox, y, color=LINE, sw=1.4))
        p.append(line(ox, y, ox + gw, y, color="#e5e7eb", sw=1, dash="3 3"))
        p.append(text(ox - 10, y + 4, "%d%%" % val, size=10, color=MUTED, anchor="end"))

    # Позначки осі X (0.0 .. 0.3)
    p_ticks = [(0.0, "0.0"), (0.05, "0.05"), (0.10, "0.10"), (0.15, "0.15"), (0.20, "0.20"), (0.25, "0.25"), (0.30, "0.30")]
    for p_val, lbl in p_ticks:
        x = ox + (p_val / 0.30) * gw
        p.append(line(x, oy, x, oy + 5, color=LINE, sw=1.4))
        p.append(line(x, oy, x, oy - gh, color="#e5e7eb", sw=1, dash="3 3"))
        p.append(text(x, oy + 20, lbl, size=10, color=MUTED))

    # Побудова кривих
    # 1. Selective Repeat: U_SR = 1 - p (для W >= 2a+1)
    pts_sr = []
    # 2. Go-Back-N: U_GBN = (1 - p) / (1 + (W - 1)*p)
    pts_gbn = []
    # 3. Stop-and-Wait: U_SW = (1 - p) / (1 + 2a)  (1 / 21 ≈ 0.0476)
    pts_sw = []

    a = 10.0
    Ws = 21.0
    steps = 40
    for s in range(steps + 1):
        pval = (s / float(steps)) * 0.30
        x = ox + (pval / 0.30) * gw

        # SR
        u_sr = max(0.0, 1.0 - pval)
        y_sr = oy - u_sr * gh
        pts_sr.append((x, y_sr))

        # GBN
        u_gbn = (1.0 - pval) / (1.0 + (Ws - 1.0) * pval)
        y_gbn = oy - u_gbn * gh
        pts_gbn.append((x, y_gbn))

        # SW
        u_sw = (1.0 - pval) / (1.0 + 2.0 * a)
        y_sw = oy - u_sw * gh
        pts_sw.append((x, y_sw))

    # Малюємо лінії кривих
    def draw_curve(pts, color, sw):
        res = []
        for i in range(len(pts) - 1):
            res.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=color, sw=sw))
        return res

    for elem in draw_curve(pts_sr, FIELD, 2.5): p.append(elem)
    for elem in draw_curve(pts_gbn, NEG, 2.5): p.append(elem)
    for elem in draw_curve(pts_sw, POS, 2.2): p.append(elem)

    # Підписи ліній прямо на графіку
    p.append(textbox(450, 115, "Selective Repeat (SR):\nU_SR = 1 − p", size=10.5, color=FIELD, bold=True, fill="#eef6ef", stroke=FIELD)[0])
    p.append(textbox(280, 245, "Go-Back-N (GBN):\nU_GBN = (1 − p) / (1 + 20p)", size=10.5, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    p.append(textbox(560, 335, "Stop-and-Wait:\nU_SW = (1 − p) / 21 ≈ 4.7%", size=10, color=POS, bold=True, fill="#fdecea", stroke=POS)[0])

    render(os.path.join(OUT, "throughput-vs-loss.svg"), W, H, *p,
           title="Порівняння пропускної здатності SW, GBN та SR від імовірності помилки p")


if __name__ == "__main__":
    fig_pipelining_vs_stop_wait()
    fig_go_back_n_operation()
    fig_selective_repeat_operation()
    fig_sequence_space_wrap()
    fig_bdp_pipe_analogy()
    fig_throughput_vs_loss()
    print("All figures generated successfully.")
