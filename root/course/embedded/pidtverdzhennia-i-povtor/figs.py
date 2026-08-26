# -*- coding: utf-8 -*-
"""Фігури до теми «Підтвердження й повтор: ARQ» (root/course/embedded/pidtverdzhennia-i-povtor).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Порівняння трьох режимів ARQ на часовій шкалі ─────────────────────────
def fig_three_modes():
    W = 1060
    H = 640
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Тріада ARQ: реакція на втрату кадру в часі", 16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "порівняння Stop-and-Wait, Go-Back-N та Selective Repeat за однакової втрати кадру №1",
                  11.5, MUTED, "middle", italic=True))

    col_w = 320
    gap = 20
    left_m = (W - (3 * col_w + 2 * gap)) / 2  # 30 px

    modes = [
        ("Stop-and-Wait", "Простоює повний RTO при втраті", [
            ("tx", 100, 140, "Кадр 0", POS),
            ("rx_ack", 140, 180, "ACK 0", FIELD),
            ("tx", 200, 240, "Кадр 1 (втрата)", POS),
            ("lost", 220, 240, "✕ Загублено", POS),
            ("timer", 200, 370, "Таймаут RTO сплив", MUTED),
            ("tx", 380, 420, "Кадр 1 (повтор)", POS),
            ("rx_ack", 420, 460, "ACK 1", FIELD),
            ("tx", 480, 520, "Кадр 2", POS),
            ("rx_ack", 520, 560, "ACK 2", FIELD),
        ]),
        ("Go-Back-N (N=4)", "Скидає 2 і 3, повторює все вікно", [
            ("tx", 100, 140, "Кадр 0", POS),
            ("tx", 130, 170, "Кадр 1 (втрата)", POS),
            ("tx", 160, 200, "Кадр 2", POS),
            ("tx", 190, 230, "Кадр 3", POS),
            ("rx_ack", 140, 180, "ACK 0", FIELD),
            ("lost", 150, 170, "✕ Загублено", POS),
            ("rx_drop", 200, 220, "Відкинуто 2 (не по черзі)", MUTED),
            ("rx_drop", 230, 250, "Відкинуто 3 (не по черзі)", MUTED),
            ("timer", 130, 330, "Таймаут кадру 1", MUTED),
            ("tx", 340, 380, "Кадр 1 (повтор)", POS),
            ("tx", 370, 410, "Кадр 2 (повтор)", POS),
            ("tx", 400, 440, "Кадр 3 (повтор)", POS),
            ("rx_ack", 380, 420, "ACK 1", FIELD),
        ]),
        ("Selective Repeat (W=4)", "Буферизує 2 і 3, шле лише №1", [
            ("tx", 100, 140, "Кадр 0", POS),
            ("tx", 130, 170, "Кадр 1 (втрата)", POS),
            ("tx", 160, 200, "Кадр 2", POS),
            ("tx", 190, 230, "Кадр 3", POS),
            ("rx_ack", 140, 180, "ACK 0", FIELD),
            ("lost", 150, 170, "✕ Загублено", POS),
            ("rx_buf", 200, 240, "ACK 2 (буфер RX: 2)", FIELD),
            ("rx_buf", 230, 270, "ACK 3 (буфер RX: 2,3)", FIELD),
            ("timer", 130, 330, "Таймаут кадру 1", MUTED),
            ("tx", 340, 380, "Кадр 1 (повтор)", POS),
            ("rx_ack", 380, 420, "ACK 3 (віддано 1,2,3)", FIELD),
            ("tx", 440, 480, "Кадр 4", POS),
        ])
    ]

    for idx, (title, subtitle, events) in enumerate(modes):
        cx = left_m + idx * (col_w + gap)
        # Рамка стовпця
        f.append(rect(cx, 70, col_w, H - 90, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
        f.append(text(cx + col_w / 2, 94, title, 14, INK, "middle", bold=True))
        f.append(text(cx + col_w / 2, 110, subtitle, 10.5, MUTED, "middle", italic=True))

        # Лінії часової шкали: Передавач (TX) ліворуч, Приймач (RX) праворуч
        tx_x = cx + 55
        rx_x = cx + col_w - 55
        top_y = 125
        bot_y = H - 35

        f.append(line(tx_x, top_y, tx_x, bot_y, color=MUTED, sw=1.5, dash="4,4"))
        f.append(line(rx_x, top_y, rx_x, bot_y, color=MUTED, sw=1.5, dash="4,4"))

        f.append(text(tx_x, top_y - 4, "TX", 11, INK, "middle", bold=True))
        f.append(text(rx_x, top_y - 4, "RX", 11, INK, "middle", bold=True))

        for ev in events:
            ev_type = ev[0]
            if ev_type == "tx":
                _, y1, y2, label, col = ev
                f.append(arrow(tx_x, y1, rx_x, y2, color=col, sw=1.5))
                mid_y = (y1 + y2) / 2 - 3
                f.append(text((tx_x + rx_x) / 2, mid_y, label, 9.5, col, "middle", bold=True))
            elif ev_type == "rx_ack":
                _, y1, y2, label, col = ev
                f.append(arrow(rx_x, y1, tx_x, y2, color=col, sw=1.5))
                mid_y = (y1 + y2) / 2 - 3
                f.append(text((tx_x + rx_x) / 2, mid_y, label, 9.5, col, "middle", bold=True))
            elif ev_type == "lost":
                _, y1, y2, label, col = ev
                f.append(line(tx_x, y1, (tx_x + rx_x) * 0.65, (y1 + y2) * 0.65, color=col, sw=1.5, dash="3,3"))
                f.append(text((tx_x + rx_x) * 0.72, (y1 + y2) * 0.65 + 3, label, 9.5, col, "start", bold=True))
            elif ev_type == "timer":
                _, y1, y2, label, col = ev
                f.append(line(tx_x - 12, y1, tx_x - 12, y2, color=col, sw=1.2))
                f.append(line(tx_x - 16, y1, tx_x - 8, y1, color=col, sw=1.2))
                f.append(line(tx_x - 16, y2, tx_x - 8, y2, color=col, sw=1.2))
                f.append(text(tx_x - 18, (y1 + y2) / 2 + 3, label, 9, col, "end"))
            elif ev_type == "rx_drop":
                _, y1, y2, label, col = ev
                f.append(line(tx_x, y1, rx_x, y2, color=MUTED, sw=1.2, dash="2,2"))
                f.append(text(rx_x + 8, y2 + 3, label, 9, POS, "start"))
            elif ev_type == "rx_buf":
                _, y1, y2, label, col = ev
                f.append(arrow(rx_x, y1, tx_x, y2, color=col, sw=1.5))
                mid_y = (y1 + y2) / 2 - 3
                f.append(text((tx_x + rx_x) / 2, mid_y, label, 9.5, col, "middle", bold=True))

    render(os.path.join(IMG, "arq-three-modes.svg"), W, H, *f)


# ── 2. Колізія номерів при некоректному розмірі вікна ────────────────────────
def fig_modulo_collision():
    W = 960
    H = 480
    f = []

    f.append(text(W / 2, 28, "Колізія номерів: чому розмір вікна обмежений модулем лічильника", 16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "приклад для 2-бітного лічильника (модуль M=4, номери 0..3) за втрати всіх квитанцій",
                  11.5, MUTED, "middle", italic=True))

    # Верхній блок: Go-Back-N помилка (W=4) проти норми (W=3)
    f.append(rect(40, 70, 880, 180, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(60, 96, "Go-Back-N: помилка вибору W = M = 4 замість дозволеного W ≤ M − 1 = 3", 13.5, POS, "start", bold=True))

    # Ліва половина верхнього блоку: що стається
    f.append(text(60, 122, "1. TX надсилає вікно кадрів: [0, 1, 2, 3]", 11.5, INK, "start"))
    f.append(text(60, 142, "2. RX успішно приймає 0, 1, 2, 3 і зсуває очікуване вікно на нове коло: очікує наступний кадр [0]", 11.5, INK, "start"))
    f.append(text(60, 162, "3. УСІ квитанції ACK 0..3 губляться на зворотному шляху через заваду", 11.5, POS, "start", bold=True))
    f.append(text(60, 182, "4. TX не отримує жодного ACK, таймер спливає, TX повторює СТАРИЙ кадр 0", 11.5, INK, "start"))
    f.append(text(60, 204, "❌ КАТАСТРОФА: RX очікує новий кадр 0, отримує старий дублікат 0 і приймає його за нові дані!", 12, POS, "start", bold=True))
    f.append(text(60, 226, "✔ Правило GBN: W ≤ 2^k − 1. Для 2 бітів W_max = 3. Тоді повтор 0 лежить за межами очікуваного вікна.", 11.5, FIELD, "start", bold=True))

    # Нижній блок: Selective Repeat (W > M/2)
    f.append(rect(40, 270, 880, 180, fill="#f9fbfd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(60, 296, "Selective Repeat: вимога симетрії W_send = W_recv ≤ M / 2 = 2^(k−1)", 13.5, NEG, "start", bold=True))

    f.append(text(60, 322, "1. При M=4 оберемо помилкове вікно W = 3 > M/2. TX надсилає кадри 0, 1, 2.", 11.5, INK, "start"))
    f.append(text(60, 342, "2. RX успішно приймає 0, 1, 2, віддає програмі й зсуває своє вікно прийому на [3, 0, 1].", 11.5, INK, "start"))
    f.append(text(60, 362, "3. ACK 0 загубився в каналі. TX за таймаутом надсилає ПОВТОР старого кадру 0.", 11.5, POS, "start", bold=True))
    f.append(text(60, 384, "4. Нове вікно RX [3, 0, 1] містить номер 0! RX сприймає старий кадр 0 як майбутній кадр 0 другого кола.", 11.5, POS, "start", bold=True))
    f.append(text(60, 408, "❌ КАТАСТРОФА: змішування попереднього і наступного циклів через перекриття вікон.", 12, POS, "start", bold=True))
    f.append(text(60, 430, "✔ Правило SR: W_send + W_recv ≤ 2^k. При однакових вікнах W_max = 2^(k−1) = 2 (для k=2).", 11.5, FIELD, "start", bold=True))

    render(os.path.join(IMG, "window-modulo-collision.svg"), W, H, *f)


# ── 3. Динамічний таймаут RTO (Якобсон і Карн) ────────────────────────────────
def fig_rto_estimation():
    W = 980
    H = 460
    f = []

    f.append(text(W / 2, 28, "Динамічний розрахунок RTO: адаптація до затримок і фільтр Карна", 16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "згладжування середнього RTT, облік джитеру та запобігання хибним замірам при повторах",
                  11.5, MUTED, "middle", italic=True))

    # Схема формул ліворуч
    f.append(rect(40, 75, 430, 355, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(255, 105, "Алгоритм Якобсона (Цілочисельний)", 14, INK, "middle", bold=True))

    formulas = [
        ("1. Похибка виміру (Error):", "Err = SampleRTT − SRTT", MUTED, INK),
        ("2. Згладжений RTT (α = 1/8):", "SRTT += Err >> 3", MUTED, FIELD),
        ("3. Варіація затримки (β = 1/4):", "|Err| = abs(Err)", MUTED, INK),
        ("", "RTTVAR += (|Err| − RTTVAR) >> 2", MUTED, FIELD),
        ("4. Підсумковий таймаут безпеки:", "RTO = SRTT + 4 · RTTVAR", MUTED, POS),
        ("5. Обмеження діапазону:", "RTO = clamp(RTO, MIN_RTO, MAX_RTO)", MUTED, INK),
    ]

    cur_y = 135
    for title, form, c1, c2 in formulas:
        if title:
            f.append(text(60, cur_y, title, 11, c1, "start", bold=True))
            cur_y += 18
        f.append(text(75, cur_y, form, 12, c2, "start", bold=True))
        cur_y += 26

    f.append(text(255, cur_y + 10, "Зсуви >>3 і >>2 виключають ділення на МК без FPU", 10.5, MUTED, "middle", italic=True))

    # Правило Карна праворуч
    f.append(rect(490, 75, 450, 355, fill="#fffefb", stroke=POS, sw=1.5, rx=8))
    f.append(text(715, 105, "Алгоритм Карна: неоднозначність повтору", 14, POS, "middle", bold=True))

    karn_steps = [
        ("Проблема неоднозначності ACK:", "Коли кадр передано двічі (через таймаут), а потім приходить ACK, невідомо: це ACK на першу чи на другу спробу?"),
        ("Хибний замір RTT:", "• Якщо на 1-шу → RTT вийде штучно завищеним.\n• Якщо на 2-гу → RTT вийде штучно заниженим."),
        ("Правило Карна №1 (Фільтрація):", "НЕ оновлювати SRTT та RTTVAR для кадрів, які зазнали хоча б однієї ретрансмісії."),
        ("Правило Карна №2 (Backoff):", "При кожному повторі подвоювати таймаут: RTO = min(2 · RTO, MAX_RTO) до першого успішного пакету без повторів.")
    ]

    ky = 135
    for title, desc in karn_steps:
        f.append(text(510, ky, title, 11.5, INK, "start", bold=True))
        ky += 18
        lines = desc.split("\n")
        for ln in lines:
            f.append(text(520, ky, ln, 10.5, MUTED if "•" in ln else INK, "start"))
            ky += 16
        ky += 8

    render(os.path.join(IMG, "rto-jacobson-karn.svg"), W, H, *f)


# ── 4. Скінченні автомати (FSM) передавача та приймача ───────────────────────
def fig_fsm_states():
    W = 1020
    H = 500
    f = []

    f.append(text(W / 2, 28, "Скінченні автомати (FSM) передавача і приймача ARQ", 16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "обробка відправки, квитанцій, таймаутів, дублікатів та переходу станів",
                  11.5, MUTED, "middle", italic=True))

    # Ліва половина: Передавач (Sender FSM)
    f.append(rect(30, 70, 465, 400, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(262, 98, "FSM Передавача (TX)", 14.5, INK, "middle", bold=True))

    # Стани передавача
    # IDLE
    f.append(rect(70, 130, 150, 48, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    f.append(text(145, 158, "TX_IDLE", 13, FIELD, "middle", bold=True))

    # WAIT_ACK
    f.append(rect(280, 130, 180, 48, fill="#ffffff", stroke=NEG, sw=2, rx=6))
    f.append(text(370, 158, "TX_WAIT_ACK", 13, NEG, "middle", bold=True))

    # RETRANSMIT
    f.append(rect(280, 270, 180, 48, fill="#ffffff", stroke=POS, sw=2, rx=6))
    f.append(text(370, 298, "TX_RETRANSMIT", 13, POS, "middle", bold=True))

    # FAILED
    f.append(rect(70, 270, 150, 48, fill="#ffffff", stroke=MUTED, sw=2, rx=6))
    f.append(text(145, 298, "TX_FAILED", 13, MUTED, "middle", bold=True))

    # Переходи TX
    # IDLE -> WAIT_ACK (send())
    f.append(arrow(220, 146, 280, 146, color=INK, sw=1.5))
    f.append(text(250, 138, "send()", 9.5, INK, "middle", bold=True))

    # WAIT_ACK -> IDLE (valid ACK)
    f.append(arrow(280, 162, 220, 162, color=FIELD, sw=1.5))
    f.append(text(250, 175, "ACK ok", 9.5, FIELD, "middle", bold=True))

    # WAIT_ACK -> RETRANSMIT (Timeout / NACK)
    f.append(arrow(370, 178, 370, 270, color=POS, sw=1.5))
    f.append(text(378, 225, "RTO / NACK", 9.5, POS, "start", bold=True))

    # RETRANSMIT -> WAIT_ACK (retries < MAX)
    f.append(arrow(350, 270, 350, 178, color=NEG, sw=1.5))
    f.append(text(342, 225, "повтор кадру", 9.5, NEG, "end"))

    # RETRANSMIT -> FAILED (retries >= MAX)
    f.append(arrow(280, 294, 220, 294, color=POS, sw=1.5))
    f.append(text(250, 286, "ліміт спроб", 9.5, POS, "middle", bold=True))

    # FAILED -> IDLE (reset)
    f.append(arrow(145, 270, 145, 178, color=MUTED, sw=1.5))
    f.append(text(138, 225, "скидання помилки", 9, MUTED, "end"))

    f.append(text(262, 380, "Керування таймером:", 11, INK, "middle", bold=True))
    f.append(text(262, 400, "• При відправці: запуск таймера RTO, лічильник спроб = 0", 10, MUTED, "middle"))
    f.append(text(262, 418, "• При валідному ACK: зупинка таймера, зсув вікна", 10, MUTED, "middle"))
    f.append(text(262, 436, "• При таймауті: лічильник++, RTO *= 2 (backoff), перепосилання", 10, MUTED, "middle"))

    # Права половина: Приймач (Receiver FSM)
    f.append(rect(525, 70, 465, 400, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(757, 98, "FSM Приймача (RX)", 14.5, INK, "middle", bold=True))

    # Стани приймача
    # WAIT_FRAME
    f.append(rect(660, 130, 195, 48, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    f.append(text(757, 158, "RX_WAIT_FRAME", 13, FIELD, "middle", bold=True))

    # PROCESS_FRAME
    f.append(rect(550, 250, 180, 48, fill="#ffffff", stroke=NEG, sw=2, rx=6))
    f.append(text(640, 278, "RX_PROCESS", 13, NEG, "middle", bold=True))

    # HANDLE_DUPLICATE
    f.append(rect(780, 250, 185, 48, fill="#ffffff", stroke=POS, sw=2, rx=6))
    f.append(text(872, 278, "RX_DUPLICATE", 13, POS, "middle", bold=True))

    # Переходи RX
    # WAIT_FRAME -> PROCESS (Seq == Expected)
    f.append(arrow(710, 178, 640, 250, color=FIELD, sw=1.5))
    f.append(text(695, 215, "Seq == Exp (CRC ok)", 9.5, FIELD, "start", bold=True))

    # PROCESS -> WAIT_FRAME (Deliver + Send ACK)
    f.append(arrow(610, 250, 670, 178, color=FIELD, sw=1.5))
    f.append(text(600, 215, "віддати в App, ACK", 9, FIELD, "end"))

    # WAIT_FRAME -> DUPLICATE (Seq < Expected)
    f.append(arrow(790, 178, 860, 250, color=POS, sw=1.5))
    f.append(text(805, 215, "Seq < Exp (Дублікат)", 9.5, POS, "end", bold=True))

    # DUPLICATE -> WAIT_FRAME (Drop data + Resend ACK)
    f.append(arrow(890, 250, 830, 178, color=POS, sw=1.5))
    f.append(text(900, 215, "скинути дані, ACK ще раз", 9, POS, "start"))

    f.append(text(757, 380, "Логіка надійності при втраті ACK:", 11, INK, "middle", bold=True))
    f.append(text(757, 400, "1. Кадр прийшов, але ACK загубився → TX шле повтор.", 10, MUTED, "middle"))
    f.append(text(757, 418, "2. RX бачить старий Seq → НЕ віддає в App вдруге (захист).", 10, MUTED, "middle"))
    f.append(text(757, 436, "3. RX ПОВТОРНО надсилає ACK → TX нарешті виходить із зависання.", 10, MUTED, "middle"))

    render(os.path.join(IMG, "arq-fsm-states.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_modes()
    fig_modulo_collision()
    fig_rto_estimation()
    fig_fsm_states()
    print("All figures generated successfully.")
