# -*- coding: utf-8 -*-
"""Фігури для статті keruvannia-potokom-i-nadiinyi-obmin («Керування потоком і надійний обмін»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. rts-cts-timing: часова діаграма апаратного керування RTS/CTS ───────────
def fig_rts_cts_timing():
    W, H = 760, 380
    p = []

    # Заголовок / фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.0, rx=8))

    # Лінії сигналів
    y_tx = 70
    y_rts = 150
    y_fifo = 250

    # Підписи зліва
    p.append(text(120, y_tx, "TX Data (Передавач)", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(120, y_rts, "/RTS (Приймач)", size=12, color=POS, bold=True, anchor="end"))
    p.append(text(120, y_fifo, "Заповнення RX FIFO", size=12, color=NEG, bold=True, anchor="end"))

    # Часова вісь знизу
    t_start = 140
    t_end = 720
    p.append(arrow(t_start - 10, 340, t_end + 10, 340, color=MUTED, sw=1.2))
    p.append(text(t_end + 10, 355, "t (час)", size=11, color=MUTED, italic=True, anchor="end"))

    # Вертикальні допоміжні лінії часу
    t_hwm = 320    # момент досягнення High Watermark
    t_tx_stop = 460  # момент завершення передачі поточного байта
    t_lwm = 600    # момент вичитки до Low Watermark

    p.append(line(t_hwm, 40, t_hwm, 330, color="#d0d7de", sw=1.0, dash="3 3"))
    p.append(line(t_tx_stop, 40, t_tx_stop, 330, color="#d0d7de", sw=1.0, dash="3 3"))
    p.append(line(t_lwm, 40, t_lwm, 330, color="#d0d7de", sw=1.0, dash="3 3"))

    p.append(text(t_hwm, 355, "High Watermark", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(t_tx_stop, 355, "TX зупинено", size=10, color=INK, anchor="middle"))
    p.append(text(t_lwm, 355, "Low Watermark", size=10, color=FIELD, anchor="middle", bold=True))

    # TX Data: пачки байтів
    # Байт 1..4 (до t_hwm), Байт 5 (у процесі передачі під час t_hwm..t_tx_stop), Пауза (t_tx_stop..t_lwm), Відновлення
    bytes_x = [(140, 190, "Байт 1"), (200, 250, "Байт 2"), (260, 310, "Байт 3"),
               (320, 380, "Байт 4"), (390, 450, "Байт 5 (в польоті)"), (610, 660, "Байт 6"), (670, 715, "Байт 7")]
    for bx1, bx2, bname in bytes_x:
        col = "#e2e8f0" if "польоті" not in bname else "#fef3c7"
        border = LINE if "польоті" not in bname else POS
        p.append(rect(bx1, y_tx - 18, bx2 - bx1, 36, fill=col, stroke=border, sw=1.2, rx=3))
        p.append(text((bx1 + bx2) / 2, y_tx + 4, bname, size=9, color=INK, bold=False))

    # TX Пауза
    p.append(line(450, y_tx, 610, y_tx, color=MUTED, sw=1.5, dash="4 4"))
    p.append(text(530, y_tx - 8, "Лінія IDLE (CTS=High)", size=10, color=MUTED, italic=True))

    # /RTS сигнал: Активний НИЗЬКИЙ (0 В). Коли High Watermark -> стає ВИСОКИЙ (3.3 В)
    # 0V рівень: y_rts + 15, 3.3V рівень: y_rts - 15
    rts_pts = [
        (t_start, y_rts + 15),
        (t_hwm, y_rts + 15),
        (t_hwm, y_rts - 15),
        (t_lwm, y_rts - 15),
        (t_lwm, y_rts + 15),
        (t_end, y_rts + 15)
    ]
    rts_poly = " ".join("%.1f,%.1f" % pt for pt in rts_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' % (rts_poly, POS))
    p.append(text(200, y_rts + 28, "0 В: Ready (Готовий)", size=10, color=FIELD, bold=True))
    p.append(text(460, y_rts - 22, "3.3 В: Busy (Стоп, буфер заповнюється)", size=10, color=POS, bold=True))

    # RX FIFO рівень: ступінчасте заповнення і спад
    # Рівні: 0 (y_fifo+35), Low Watermark (y_fifo+10), High Watermark (y_fifo-20), 100% Full (y_fifo-40)
    p.append(line(t_start, y_fifo - 40, t_end, y_fifo - 40, color=POS, sw=1.0, dash="2 2"))
    p.append(text(t_start + 10, y_fifo - 44, "100% Переповнення (Overflow/ORE)", size=9, color=POS, anchor="start"))

    p.append(line(t_start, y_fifo - 20, t_end, y_fifo - 20, color=POS, sw=1.0, dash="4 3"))
    p.append(text(t_start + 10, y_fifo - 24, "Положення High Watermark (зняття RTS)", size=9, color=POS, anchor="start"))

    p.append(line(t_start, y_fifo + 10, t_end, y_fifo + 10, color=FIELD, sw=1.0, dash="4 3"))
    p.append(text(t_start + 10, y_fifo + 6, "Положення Low Watermark (повернення RTS)", size=9, color=FIELD, anchor="start"))

    # Крива рівня FIFO
    fifo_pts = [
        (t_start, y_fifo + 35),
        (190, y_fifo + 25),
        (250, y_fifo + 12),
        (310, y_fifo - 5),
        (t_hwm, y_fifo - 20),      # Спрацював поріг
        (380, y_fifo - 28),      # Байт 4 прийнято
        (450, y_fifo - 35),      # Байт 5 прийнято (досяг піку безпечно НИЖЧЕ 100%)
        (490, y_fifo - 35),      # Пауза передавача, процесор читає
        (550, y_fifo - 10),      # Процесор вичитує
        (t_lwm, y_fifo + 10),    # Досягнуто LWM
        (610, y_fifo + 20),
        (660, y_fifo + 12),
        (715, y_fifo + 2)
    ]
    fifo_poly = " ".join("%.1f,%.1f" % pt for pt in fifo_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round"/>' % (fifo_poly, NEG))

    # Виділення запасу безпеки
    p.append(rect(460, y_fifo - 39, 130, 18, fill="#fee2e2", stroke=POS, sw=0.8, rx=2))
    p.append(text(525, y_fifo - 27, "Запас на байти в польоті", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "rts-cts-timing.svg"), W, H, *p)


# ── 2. sliding-window-credits: кредитний та віконний обмін ───────────────────
def fig_sliding_window_credits():
    W, H = 760, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.0, rx=8))

    # Дві часові шкали
    x_tx = 160
    x_rx = 600

    p.append(line(x_tx, 60, x_tx, 390, color=LINE, sw=2.0))
    p.append(line(x_rx, 60, x_rx, 390, color=LINE, sw=2.0))

    # Шапки вузлів
    p.append(rect(x_tx - 80, 20, 160, 36, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x_tx, 42, "Передавач (TX)", size=13, color=INK, bold=True))

    p.append(rect(x_rx - 80, 20, 160, 36, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x_rx, 42, "Приймач (RX)", size=13, color=INK, bold=True))

    # Початковий стан
    p.append(text(x_tx - 15, 80, "Кредити = 3", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(x_rx + 15, 80, "Вільно 3 слоти буфера", size=11, color=FIELD, bold=True, anchor="start"))

    # Кадр 1 (seq=0)
    p.append(arrow(x_tx, 95, x_rx, 135, color=NEG, sw=1.6))
    p.append(text((x_tx + x_rx) / 2, 108, "Кадр #0 (1/3)", size=11, color=NEG, bold=True))
    p.append(text(x_tx - 15, 120, "Кредити = 2", size=10, color=INK, anchor="end"))

    # Кадр 2 (seq=1)
    p.append(arrow(x_tx, 130, x_rx, 170, color=NEG, sw=1.6))
    p.append(text((x_tx + x_rx) / 2, 143, "Кадр #1 (2/3)", size=11, color=NEG, bold=True))
    p.append(text(x_tx - 15, 155, "Кредити = 1", size=10, color=INK, anchor="end"))

    # Кадр 3 (seq=2)
    p.append(arrow(x_tx, 165, x_rx, 205, color=NEG, sw=1.6))
    p.append(text((x_tx + x_rx) / 2, 178, "Кадр #2 (3/3)", size=11, color=NEG, bold=True))
    p.append(text(x_tx - 15, 190, "Кредити = 0", size=10, color=POS, bold=True, anchor="end"))

    # Блокування передавача
    p.append(rect(x_tx - 130, 205, 120, 32, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_tx - 70, 225, "TX БЛОКОВАНО", size=10, color=POS, bold=True))

    # Обробка на приймачі
    p.append(rect(x_rx + 15, 150, 120, 60, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(mtext(x_rx + 75, 172, ["Буфер заповнено", "Обробка завданням"], size=10, color="#b45309", bold=True))

    # Повернення кредитів (ACK / CREDIT_GRANT)
    p.append(arrow(x_rx, 240, x_tx, 280, color=FIELD, sw=1.8))
    p.append(text((x_tx + x_rx) / 2, 253, "ACK + Кредити (+2 слоти)", size=11, color=FIELD, bold=True))
    p.append(text(x_rx + 15, 245, "Звільнено 2 слоти", size=10, color=FIELD, anchor="start"))

    # Відновлення передачі
    p.append(text(x_tx - 15, 295, "Кредити = 2", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(rect(x_tx - 130, 310, 120, 32, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_tx - 70, 330, "TX РОЗБЛОКОВАНО", size=10, color=FIELD, bold=True))

    # Кадр 4 (seq=3)
    p.append(arrow(x_tx, 340, x_rx, 380, color=NEG, sw=1.6))
    p.append(text((x_tx + x_rx) / 2, 353, "Кадр #3 (1/2)", size=11, color=NEG, bold=True))
    p.append(text(x_tx - 15, 365, "Кредити = 1", size=10, color=INK, anchor="end"))

    render(os.path.join(OUT, "sliding-window-credits.svg"), W, H, *p)


# ── 3. backpressure-chain: ланцюжок зворотного тиску в системі ────────────────
def fig_backpressure_chain():
    W, H = 760, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.0, rx=8))

    # 4 ланки конвеєра
    # 1. Зовнішнє джерело / TX
    # 2. UART DMA Buffer
    # 3. RTOS Message Queue
    # 4. Worker Task / Flash Storage
    boxes = [
        (40, 90, 140, 70, "Зовнішній вузол\n(Передавач)", "#f1f5f9"),
        (220, 90, 150, 70, "Апаратний FIFO /\nDMA буфер", "#f1f5f9"),
        (410, 90, 140, 70, "Черга повідомлень\n(RTOS Queue)", "#f1f5f9"),
        (590, 90, 130, 70, "Завдання запису\nу Flash (25 мс)", "#fee2e2")
    ]

    for bx, by, bw, bh, title, bg in boxes:
        p.append(rect(bx, by, bw, bh, fill=bg, stroke=LINE, sw=1.4, rx=6))
        p.append(mtext(bx + bw / 2, by + 26, title.split("\n"), size=11, color=INK, bold=True))

    # Прямий потік даних (сині стрілки зліва направо)
    p.append(arrow(180, 115, 220, 115, color=NEG, sw=2.0))
    p.append(arrow(370, 115, 410, 115, color=NEG, sw=2.0))
    p.append(arrow(550, 115, 590, 115, color=NEG, sw=2.0))

    p.append(text(380, 60, "Прямий потік даних (Data Flow: RX → ISR → Queue → Task)", size=12, color=NEG, bold=True))

    # Зворотний тиск (червоні пунктирні стрілки справа наліво)
    p.append(text(380, 205, "Поширення зворотного тиску (Backpressure Ripple)", size=12, color=POS, bold=True))

    # 1. Flash блокує Worker Task
    p.append(rect(590, 170, 130, 24, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
    p.append(text(655, 186, "Затримка Flash", size=9, color=POS, bold=True))

    # Стрілка назад від Task до Queue
    p.append(arrow(590, 240, 550, 240, color=POS, sw=2.0))
    p.append(rect(410, 230, 140, 50, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(mtext(480, 248, ["Черга переповнюється", "(Queue Full)"], size=10, color="#b45309", bold=True))

    # Стрілка назад від Queue до DMA / Драйвера
    p.append(arrow(410, 255, 370, 255, color=POS, sw=2.0))
    p.append(rect(220, 230, 150, 50, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    p.append(mtext(295, 248, ["Драйвер зупиняє DMA", "RTS знімається (/RTS=1)"], size=10, color=POS, bold=True))

    # Стрілка назад від Драйвера до Передавача
    p.append(arrow(220, 255, 180, 255, color=POS, sw=2.0))
    p.append(rect(40, 230, 140, 50, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(110, 248, ["Передавач бачить CTS=1", "і зупиняє потік"], size=10, color=POS, bold=True))

    p.append(text(380, 325, "Результат: жоден байт не губиться в усьому конвеєрі", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "backpressure-chain.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rts_cts_timing()
    fig_sliding_window_credits()
    fig_backpressure_chain()
    print("All figures generated successfully.")
