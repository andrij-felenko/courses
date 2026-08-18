# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. fsm-states: Скінченний автомат станів TCP (11 станів) ───────────────────
def fig_fsm_states():
    W, H = 820, 560
    p = []

    # Заголовок блоків
    p.append(rect(30, 20, 760, 520, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=8))

    # Стан CLOSED зверху
    b_closed, _, _ = textbox(410, 55, "CLOSED", size=13, bold=True, fill="#eef2f7", stroke=INK, sw=1.8, pad=8)
    p.append(b_closed)

    # Ліва колонка: Встановлення з'єднання (Активне / Пасивне)
    b_listen, _, _ = textbox(210, 130, "LISTEN\n(пасивне відкриття)", size=11, bold=True, fill="#fdfefe", stroke=MUTED, sw=1.4, pad=7)
    b_syn_sent, _, _ = textbox(610, 130, "SYN_SENT\n(активне відкриття: вислано SYN)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)
    b_syn_rcvd, _, _ = textbox(210, 215, "SYN_RCVD\n(отримано SYN, вислано SYN-ACK)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)

    p.append(b_listen)
    p.append(b_syn_sent)
    p.append(b_syn_rcvd)

    # Центр: ESTABLISHED
    b_est, _, _ = textbox(410, 275, "ESTABLISHED\n(активна передача даних: потік байтів)", size=13, bold=True, fill="#eef6ef", stroke=FIELD, sw=2.2, pad=10)
    p.append(b_est)

    # Нижня частина: Розрив з'єднання
    # Активне закриття (ліворуч/центр)
    b_fin_w1, _, _ = textbox(210, 365, "FIN_WAIT_1\n(вислано FIN)", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    b_fin_w2, _, _ = textbox(210, 440, "FIN_WAIT_2\n(напівзакритий: отримано ACK на FIN)", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    b_closing, _, _ = textbox(410, 395, "CLOSING\n(одночасне закриття)", size=11, bold=True, fill="#fff7e0", stroke=INK, sw=1.4, pad=7)
    b_tw, _, _ = textbox(310, 505, "TIME_WAIT\n(очікування 2·MSL)", size=12, bold=True, fill="#fdecea", stroke=POS, sw=2.0, pad=8)

    # Пасивне закриття (праворуч)
    b_close_wait, _, _ = textbox(610, 365, "CLOSE_WAIT\n(отримано FIN, очікування закриття)", size=11, bold=True, fill="#fff7e0", stroke=INK, sw=1.5, pad=7)
    b_last_ack, _, _ = textbox(610, 460, "LAST_ACK\n(вислано FIN, чекаємо фінальний ACK)", size=11, bold=True, fill="#fff7e0", stroke=INK, sw=1.5, pad=7)

    p.append(b_fin_w1)
    p.append(b_fin_w2)
    p.append(b_closing)
    p.append(b_tw)
    p.append(b_close_wait)
    p.append(b_last_ack)

    # Стрілки переходів встановлення
    p.append(arrow(370, 68, 260, 110, color=MUTED, sw=1.4))
    p.append(text(290, 80, "listen()", size=10, color=MUTED, italic=True))

    p.append(arrow(450, 68, 560, 110, color=NEG, sw=1.4))
    p.append(text(530, 80, "connect() / вислати SYN", size=10, color=NEG, italic=True))

    p.append(arrow(210, 155, 210, 195, color=NEG, sw=1.4))
    p.append(text(145, 175, "отримано SYN\nвислати SYN+ACK", size=9, color=NEG, anchor="middle"))

    p.append(arrow(560, 150, 460, 255, color=FIELD, sw=1.4))
    p.append(text(555, 210, "отримано SYN+ACK\nвислати ACK", size=9, color=FIELD, anchor="middle"))

    p.append(arrow(260, 235, 360, 265, color=FIELD, sw=1.4))
    p.append(text(285, 265, "отримано ACK", size=9, color=FIELD, anchor="middle"))

    # Стрілки розриву
    p.append(arrow(360, 295, 240, 345, color=POS, sw=1.4))
    p.append(text(270, 315, "close() / вислати FIN", size=9, color=POS, italic=True))

    p.append(arrow(460, 295, 580, 345, color=INK, sw=1.4))
    p.append(text(555, 315, "отримано FIN / вислати ACK", size=9, color=INK, italic=True))

    p.append(arrow(210, 388, 210, 420, color=POS, sw=1.4))
    p.append(text(145, 405, "отримано ACK", size=9, color=POS, italic=True))

    p.append(arrow(210, 462, 280, 490, color=POS, sw=1.4))
    p.append(text(215, 485, "отримано FIN\nвислати ACK", size=9, color=POS, anchor="middle"))

    p.append(arrow(610, 392, 610, 440, color=INK, sw=1.4))
    p.append(text(675, 415, "close() / вислати FIN", size=9, color=INK, italic=True))

    # Стрілка з LAST_ACK в CLOSED
    p.append(line(675, 460, 740, 460, color=MUTED, sw=1.3, dash="4 3"))
    p.append(line(740, 460, 740, 55, color=MUTED, sw=1.3, dash="4 3"))
    p.append(arrow(740, 55, 460, 55, color=MUTED, sw=1.3))
    p.append(text(745, 270, "отримано фінальний ACK", size=9, color=MUTED, anchor="start"))

    # Стрілка з TIME_WAIT в CLOSED
    p.append(line(310, 528, 100, 528, color=MUTED, sw=1.3, dash="4 3"))
    p.append(line(100, 528, 100, 55, color=MUTED, sw=1.3, dash="4 3"))
    p.append(arrow(100, 55, 360, 55, color=MUTED, sw=1.3))
    p.append(text(95, 270, "таймаут 2·MSL вичерпано", size=9, color=MUTED, anchor="end"))

    # Одночасне закриття: FIN_WAIT_1 -> CLOSING -> TIME_WAIT
    p.append(arrow(275, 370, 350, 385, color=INK, sw=1.2))
    p.append(arrow(410, 420, 350, 485, color=INK, sw=1.2))

    render(os.path.join(OUT, "fsm-states.svg"), W, H, *p,
           title="Скінченний автомат станів TCP (RFC 793 / RFC 1122)")


# ── 2. three-way-handshake: Трикрокове рукостискання та опції ───────────────────
def fig_three_way_handshake():
    W, H = 760, 420
    p = []
    cx, sx = 160, 600
    top, bot = 70, 390

    # Вертикалі клієнта та сервера
    for x, lab, sub in ((cx, "КЛІЄНТ (Active)", "SYN_SENT → ESTABLISHED"),
                        (sx, "СЕРВЕР (Passive)", "LISTEN → SYN_RCVD → ESTABLISHED")):
        p.append(line(x, top, x, bot, color=MUTED, sw=1.3, dash="4 4"))
        b, _, _ = textbox(x, top - 25, f"{lab}\n{sub}", size=11, bold=True, fill=FILL, stroke=INK, sw=1.5, pad=8)
        p.append(b)

    # 1. Пакет SYN
    y1 = 120
    p.append(arrow(cx, y1, sx, y1 + 35, color=NEG, sw=2.0))
    b1, _, _ = textbox((cx + sx) / 2, y1 + 10,
                       "1. SYN [SEQ = ISN_c = 1000]\nОпції: MSS=1460, WS=7, SACK=1, TSval=100",
                       size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.4, pad=6)
    p.append(b1)
    p.append(text(cx - 15, y1, "SYN_SENT", size=10, color=NEG, bold=True, anchor="end"))
    p.append(text(sx + 15, y1 + 35, "SYN_RCVD\n(виділено TCB)", size=9, color=NEG, bold=True, anchor="start"))

    # 2. Пакет SYN-ACK
    y2 = 205
    p.append(arrow(sx, y2, cx, y2 + 35, color=FIELD, sw=2.0))
    b2, _, _ = textbox((cx + sx) / 2, y2 + 10,
                       "2. SYN + ACK [SEQ = ISN_s = 5000, ACK = 1001]\nОпції: MSS=1460, WS=7, SACK=1, TSval=200, TSecr=100",
                       size=10.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, pad=6)
    p.append(b2)

    # 3. Пакет ACK
    y3 = 290
    p.append(arrow(cx, y3, sx, y3 + 35, color=INK, sw=2.0))
    b3, _, _ = textbox((cx + sx) / 2, y3 + 10,
                       "3. ACK [SEQ = 1001, ACK = 5001]\n(може нести перші корисні дані застосунку)",
                       size=10.5, bold=True, fill="#fdfefe", stroke=INK, sw=1.4, pad=6)
    p.append(b3)
    p.append(text(cx - 15, y3, "ESTABLISHED", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(text(sx + 15, y3 + 35, "ESTABLISHED\n(перенесено в accept_queue)", size=9, color=FIELD, bold=True, anchor="start"))

    # Лінія передачі даних
    y4 = 370
    p.append(line(cx, y4, sx, y4, color=FIELD, sw=2.5))
    p.append(text((cx + sx) / 2, y4 - 10, "Двосторонній потік даних: full-duplex потік байтів", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "three-way-handshake.svg"), W, H, *p,
           title="Трикрокове рукостискання TCP з узгодженням опцій")


# ── 3. four-way-teardown: Чотирикрокове закриття та напівзакритий стан ─────────
def fig_four_way_teardown():
    W, H = 760, 450
    p = []
    cx, sx = 160, 600
    top, bot = 65, 420

    for x, lab in ((cx, "АКТИВНА СТОРОНА (Client)"), (sx, "ПАСИВНА СТОРОНА (Server)")):
        p.append(line(x, top, x, bot, color=MUTED, sw=1.3, dash="4 4"))
        b, _, _ = textbox(x, top - 20, lab, size=11, bold=True, fill=FILL, stroke=INK, sw=1.5, pad=8)
        p.append(b)

    # 1. FIN від клієнта
    y1 = 105
    p.append(text(cx - 15, y1 - 10, "shutdown(SHUT_WR)\nабо close()", size=9, color=POS, anchor="end"))
    p.append(arrow(cx, y1, sx, y1 + 30, color=POS, sw=2.0))
    b1, _, _ = textbox((cx + sx) / 2, y1 + 10, "1. FIN [SEQ = u, ACK = v]", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.4, pad=6)
    p.append(b1)
    p.append(text(cx - 15, y1 + 30, "FIN_WAIT_1", size=10, color=POS, bold=True, anchor="end"))
    p.append(text(sx + 15, y1 + 30, "CLOSE_WAIT\n(ядро шле ACK, read()=0)", size=9, color=INK, bold=True, anchor="start"))

    # 2. ACK від сервера
    y2 = 175
    p.append(arrow(sx, y2, cx, y2 + 30, color=INK, sw=2.0))
    b2, _, _ = textbox((cx + sx) / 2, y2 + 10, "2. ACK [ACK = u + 1]", size=11, bold=True, fill="#f4f6f8", stroke=INK, sw=1.4, pad=6)
    p.append(b2)
    p.append(text(cx - 15, y2 + 30, "FIN_WAIT_2\n(напівзакритий канал)", size=9, color=POS, bold=True, anchor="end"))

    # Фаза напівзакриття: сервер ще досилає дані
    y_half = 240
    p.append(rect(cx + 40, y_half - 12, (sx - cx) - 80, 24, fill="#fffde7", stroke="#d4b106", sw=1.0, rx=4))
    p.append(text((cx + sx) / 2, y_half + 4, "Напівзакритий стан: сервер ще може передавати залишок даних", size=10, color="#7d6608", bold=True))

    # 3. FIN від сервера
    y3 = 295
    p.append(text(sx + 15, y3 - 10, "close() після вичитки", size=9, color=POS, anchor="start"))
    p.append(arrow(sx, y3, cx, y3 + 30, color=POS, sw=2.0))
    b3, _, _ = textbox((cx + sx) / 2, y3 + 10, "3. FIN [SEQ = w, ACK = u + 1]", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.4, pad=6)
    p.append(b3)
    p.append(text(sx + 15, y3 + 30, "LAST_ACK", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(cx - 15, y3 + 30, "TIME_WAIT\n(старт 2·MSL = 60 с)", size=9, color=POS, bold=True, anchor="end"))

    # 4. Фінальний ACK від клієнта
    y4 = 365
    p.append(arrow(cx, y4, sx, y4 + 30, color=FIELD, sw=2.0))
    b4, _, _ = textbox((cx + sx) / 2, y4 + 10, "4. ACK [ACK = w + 1]", size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, pad=6)
    p.append(b4)
    p.append(text(sx + 15, y4 + 30, "CLOSED", size=10, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "four-way-teardown.svg"), W, H, *p,
           title="Чотирикрокове закриття з'єднання та напівзакритий стан")


# ── 4. time-wait-protection: Чому необхідний стан TIME_WAIT ───────────────────
def fig_time_wait_protection():
    W, H = 820, 420
    p = []

    # Дві панелі небезпек
    col_w = 370
    p.append(rect(25, 20, col_w, 380, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(rect(425, 20, col_w, 380, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))

    # Панель 1: Втрата фінального ACK
    p.append(text(210, 45, "Захист 1: Втрата фінального ACK", size=12, color=POS, bold=True))
    p.append(text(210, 65, "Без TIME_WAIT сервер застрягне в LAST_ACK", size=10, color=MUTED, italic=True))

    p.append(line(80, 85, 80, 360, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(340, 85, 340, 360, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(80, 80, "Клієнт", size=10, bold=True))
    p.append(text(340, 80, "Сервер", size=10, bold=True))

    p.append(arrow(340, 110, 80, 135, color=POS, sw=1.5))
    p.append(text(210, 115, "FIN", size=10, color=POS, bold=True))

    # Загублений ACK
    p.append(line(80, 160, 210, 185, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(225, 190, "ACK ✗ (загубився)", size=10, color=POS, bold=True))

    # Сервер перевисилає FIN
    p.append(arrow(340, 230, 80, 255, color=POS, sw=1.5))
    p.append(text(210, 235, "Ретрансмісія FIN", size=10, color=POS, bold=True))

    # Клієнт у TIME_WAIT відповідає повторним ACK
    p.append(arrow(80, 280, 340, 305, color=FIELD, sw=1.8))
    p.append(text(210, 285, "Повторний ACK з TIME_WAIT", size=10, color=FIELD, bold=True))
    p.append(text(340, 325, "Сервер переходить у CLOSED ✓", size=9.5, color=FIELD, bold=True, anchor="end"))

    # Панель 2: Запізнілий дублікат даних
    p.append(text(610, 45, "Захист 2: Запізнілі дублікати (Ghost Packets)", size=12, color=NEG, bold=True))
    p.append(text(610, 65, "Захист від пошкодження нового втілення (5-кортеж)", size=10, color=MUTED, italic=True))

    p.append(line(480, 85, 480, 360, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(740, 85, 740, 360, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(480, 80, "Клієнт", size=10, bold=True))
    p.append(text(740, 80, "Сервер", size=10, bold=True))

    # Старий пакет блукає в мережі
    p.append(arrow(480, 110, 600, 140, color="#d4b106", sw=1.5))
    p.append(text(590, 120, "Дані з'єднання #1\n(застрягли в маршрутизаторі)", size=9, color="#7d6608", anchor="middle"))

    p.append(rect(460, 160, 290, 40, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    p.append(text(605, 177, "З'єднання #1 закрите. TIME_WAIT триває 2·MSL.", size=9.5, color=POS, bold=True))
    p.append(text(605, 192, "Усі запізнілі пакети зникають (TTL вичерпується)", size=9, color=MUTED))

    # Нове з'єднання після TIME_WAIT
    p.append(arrow(480, 235, 740, 260, color=FIELD, sw=1.6))
    p.append(text(610, 240, "SYN нового з'єднання #2 (той самий 5-кортеж)", size=9.5, color=FIELD, bold=True))

    p.append(text(610, 300, "Якщо старий пакет прийде у TIME_WAIT —\nядро його відкине, не ламаючи нове з'єднання",
                  size=9.5, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "time-wait-protection.svg"), W, H, *p,
           title="Два критичні механізми захисту стану TIME_WAIT")


# ── 5. simultaneous-open-close: Одночасне відкриття та закриття ────────────────
def fig_simultaneous_open_close():
    W, H = 820, 390
    p = []

    col_w = 370
    p.append(rect(25, 20, col_w, 350, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(rect(425, 20, col_w, 350, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))

    # 1. Одночасне відкриття
    p.append(text(210, 45, "Одночасне відкриття (Simultaneous Open)", size=12, color=NEG, bold=True))
    p.append(text(210, 65, "Обидва вузли надсилають SYN майже одночасно", size=10, color=MUTED, italic=True))

    p.append(line(80, 85, 80, 335, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(340, 85, 340, 335, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(80, 80, "Вузол A", size=10, bold=True))
    p.append(text(340, 80, "Вузол B", size=10, bold=True))

    p.append(arrow(80, 110, 340, 145, color=NEG, sw=1.6))
    p.append(text(190, 115, "SYN (seq=x)", size=10, color=NEG, bold=True))

    p.append(arrow(340, 110, 80, 145, color=NEG, sw=1.6))
    p.append(text(230, 145, "SYN (seq=y)", size=10, color=NEG, bold=True))

    p.append(text(80, 165, "SYN_SENT → SYN_RCVD", size=9, color=INK, bold=True))
    p.append(text(340, 165, "SYN_SENT → SYN_RCVD", size=9, color=INK, bold=True))

    p.append(arrow(80, 195, 340, 230, color=FIELD, sw=1.6))
    p.append(text(190, 200, "SYN+ACK (seq=x, ack=y+1)", size=9, color=FIELD, bold=True))

    p.append(arrow(340, 195, 80, 230, color=FIELD, sw=1.6))
    p.append(text(230, 230, "SYN+ACK (seq=y, ack=x+1)", size=9, color=FIELD, bold=True))

    p.append(text(80, 260, "ESTABLISHED", size=10, color=FIELD, bold=True))
    p.append(text(340, 260, "ESTABLISHED", size=10, color=FIELD, bold=True))

    # 2. Одночасне закриття
    p.append(text(610, 45, "Одночасне закриття (Simultaneous Close)", size=12, color=POS, bold=True))
    p.append(text(610, 65, "Обидва вузли викликають close() одночасно", size=10, color=MUTED, italic=True))

    p.append(line(480, 85, 480, 335, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(740, 85, 740, 335, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(480, 80, "Вузол A", size=10, bold=True))
    p.append(text(740, 80, "Вузол B", size=10, bold=True))

    p.append(arrow(480, 110, 740, 145, color=POS, sw=1.6))
    p.append(text(590, 115, "FIN (seq=u)", size=10, color=POS, bold=True))

    p.append(arrow(740, 110, 480, 145, color=POS, sw=1.6))
    p.append(text(630, 145, "FIN (seq=v)", size=10, color=POS, bold=True))

    p.append(text(480, 165, "FIN_WAIT_1 → CLOSING", size=9, color=INK, bold=True))
    p.append(text(740, 165, "FIN_WAIT_1 → CLOSING", size=9, color=INK, bold=True))

    p.append(arrow(480, 195, 740, 230, color=FIELD, sw=1.6))
    p.append(text(590, 200, "ACK (ack=v+1)", size=9, color=FIELD, bold=True))

    p.append(arrow(740, 195, 480, 230, color=FIELD, sw=1.6))
    p.append(text(630, 230, "ACK (ack=u+1)", size=9, color=FIELD, bold=True))

    p.append(text(480, 260, "TIME_WAIT (2·MSL)", size=10, color=POS, bold=True))
    p.append(text(740, 260, "TIME_WAIT (2·MSL)", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "simultaneous-open-close.svg"), W, H, *p,
           title="Симетричні сценарії: одночасне відкриття та одночасне закриття TCP")


if __name__ == "__main__":
    fig_fsm_states()
    fig_three_way_handshake()
    fig_four_way_teardown()
    fig_time_wait_protection()
    fig_simultaneous_open_close()
    print("OK: figures generated in", OUT)
