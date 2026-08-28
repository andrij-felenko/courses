# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні кольори
RX_FILL = "#eef4ff"   # холодне (приймання / телеметрія)
RX_STK  = "#2457d6"
TX_FILL = "#fdecea"   # гаряче (команда / відправка)
TX_STK  = "#c0392b"
OK_FILL = "#eafaf1"   # успіх / ACCEPTED
OK_STK  = "#27ae60"
WARN_FILL = "#fef9e7" # попередження / очікування
WARN_STK  = "#f39c12"
ERR_FILL = "#fdedec"  # відхилено / помилка
ERR_STK  = "#e74c3c"
MUTED_BOX = "#f8f9fa"
MUTED_STK = "#95a5a6"


# ── 1. three-outcomes.svg ───────────────────────────────────────────────────
def fig_three_outcomes():
    W, H = 840, 480
    p = []
    p.append(text(W/2, 28, "Три результати відправки команди через ненадійний радіоефір", size=16, bold=True))

    # Стовпчики: Наземна станція (GCS) | Радіоефір | Польотний контролер (FC)
    p.append(text(120, 60, "Наземна станція (GCS)", size=13, bold=True, color=INK))
    p.append(text(420, 60, "Радіоканал (Uplink / Downlink)", size=13, bold=True, color=MUTED))
    p.append(text(720, 60, "Польотний контролер (FC)", size=13, bold=True, color=INK))

    p.append(line(240, 50, 240, 460, color="#e0e0e0", sw=1.0, dash="4,4"))
    p.append(line(600, 50, 600, 460, color="#e0e0e0", sw=1.0, dash="4,4"))

    # 1. ACCEPTED (ряд 1, y = 85..185)
    y1 = 85
    p.append(rect(15, y1, 810, 110, fill=OK_FILL, stroke=OK_STK, sw=1.2, rx=6))
    p.append(text(30, y1 + 22, "1. ПРИЙНЯТО (ACCEPTED)", size=13, bold=True, color=OK_STK, anchor="start"))
    
    # GCS box
    p.append(fitbox(30, y1 + 35, 180, 58, "Шле COMMAND_LONG\n(confirmation = 0)", size=12, fill=TX_FILL, stroke=TX_STK))
    # Uplink arrow
    p.append(arrow(215, y1 + 55, 625, y1 + 55, color=TX_STK, sw=2.0))
    p.append(text(420, y1 + 45, "COMMAND_LONG (ARM / SET_MODE)", size=11, color=TX_STK))
    # FC box
    p.append(fitbox(630, y1 + 35, 180, 58, "Перевірка стану: OK\nДію виконано! Шле ACK", size=12, fill=OK_FILL, stroke=OK_STK))
    # Downlink arrow
    p.append(arrow(625, y1 + 78, 215, y1 + 78, color=OK_STK, sw=2.0))
    p.append(text(420, y1 + 92, "COMMAND_ACK (MAV_RESULT_ACCEPTED)", size=11, color=OK_STK))

    # 2. REJECTED / DENIED (ряд 2, y = 210..310)
    y2 = 210
    p.append(rect(15, y2, 810, 110, fill=ERR_FILL, stroke=ERR_STK, sw=1.2, rx=6))
    p.append(text(30, y2 + 22, "2. ВІДХИЛЕНО (DENIED / TEMPORARILY_REJECTED / FAILED)", size=13, bold=True, color=ERR_STK, anchor="start"))
    
    # GCS box
    p.append(fitbox(30, y2 + 35, 180, 58, "Шле команду\n(наприклад, ARM)", size=12, fill=TX_FILL, stroke=TX_STK))
    # Uplink arrow
    p.append(arrow(215, y2 + 55, 625, y2 + 55, color=TX_STK, sw=2.0))
    p.append(text(420, y2 + 45, "COMMAND_LONG (ARM motors)", size=11, color=TX_STK))
    # FC box
    p.append(fitbox(630, y2 + 35, 180, 58, "Pre-arm: калібрування гіро!\nЗаборона армінгу", size=12, fill=ERR_FILL, stroke=ERR_STK))
    # Downlink arrow
    p.append(arrow(625, y2 + 78, 215, y2 + 78, color=ERR_STK, sw=2.0))
    p.append(text(420, y2 + 92, "COMMAND_ACK (MAV_RESULT_DENIED / TEMPORARILY_REJECTED)", size=11, color=ERR_STK))

    # 3. SILENCE / TIMEOUT (ряд 3, y = 335..450)
    y3 = 335
    p.append(rect(15, y3, 810, 120, fill=MUTED_BOX, stroke=MUTED_STK, sw=1.2, rx=6))
    p.append(text(30, y3 + 22, "3. ТИША (TIMEOUT / ВТРАТА В ЕФІРІ / ЗАВИСАННЯ)", size=13, bold=True, color=INK, anchor="start"))
    
    # GCS box
    p.append(fitbox(30, y3 + 35, 180, 68, "Чекає 1000 мс...\nВідповіді нема!\nСтан борту НЕВІДОМИЙ", size=11, fill=WARN_FILL, stroke=WARN_STK))
    
    # Uplink lost variant
    p.append(line(215, y3 + 52, 380, y3 + 52, color=TX_STK, sw=2.0))
    p.append(text(395, y3 + 56, "✖", size=16, bold=True, color=POS))
    p.append(text(475, y3 + 52, "Пакет втрачено в Uplink", size=10, color=MUTED))

    # Downlink lost variant
    p.append(line(625, y3 + 82, 460, y3 + 82, color=OK_STK, sw=2.0))
    p.append(text(445, y3 + 86, "✖", size=16, bold=True, color=POS))
    p.append(text(360, y3 + 82, "ACK втрачено в Downlink", size=10, color=MUTED))

    # FC box
    p.append(fitbox(630, y3 + 35, 180, 68, "Або не почув команду,\nабо виконав, але ACK упав,\nабо завис RTOS-потік", size=11, fill=MUTED_BOX, stroke=MUTED_STK))

    render(os.path.join(OUT, "three-outcomes.svg"), W, H, *p)


# ── 2. command-ack-fsm.svg ──────────────────────────────────────────────────
def fig_command_ack_fsm():
    W, H = 840, 520
    p = []
    p.append(text(W/2, 28, "Скінченний автомат повторних спроб і таймаутів (Retry/Timeout FSM)", size=16, bold=True))

    # IDLE
    p.append(fitbox(20, 85, 140, 70, "IDLE\n(Очікування команди)\nUI: доступний", size=12, fill=FILL, stroke=LINE))
    
    # Arrow IDLE -> WAITING_ACK
    p.append(arrow(160, 120, 275, 120, color=LINE, sw=1.8))
    p.append(text(218, 108, "Наказ UI", size=11, bold=True, color=INK))
    p.append(text(218, 136, "conf=0, T_timer", size=10, color=MUTED))

    # WAITING_ACK
    p.append(fitbox(280, 85, 170, 70, "WAITING_ACK\nТаймер 1000 мс активний\nUI: заблоковано", size=12, fill=WARN_FILL, stroke=WARN_STK))

    # Arrow WAITING_ACK -> IN_PROGRESS
    p.append(arrow(450, 105, 545, 105, color=WARN_STK, sw=1.8))
    p.append(text(498, 95, "ACK(IN_PROGRESS)", size=10, bold=True, color=WARN_STK))

    # IN_PROGRESS
    p.append(fitbox(550, 75, 180, 65, "IN_PROGRESS\n(Калібрування/формат)\nСкинути таймер, прогрес %", size=11, fill=WARN_FILL, stroke=WARN_STK))
    # Loop on IN_PROGRESS
    p.append(line(730, 105, 765, 105, color=WARN_STK, sw=1.5))
    p.append(line(765, 105, 765, 60, color=WARN_STK, sw=1.5))
    p.append(line(765, 60, 640, 60, color=WARN_STK, sw=1.5))
    p.append(arrow(640, 60, 640, 73, color=WARN_STK, sw=1.5))
    p.append(text(700, 52, "оновлення progress", size=10, color=MUTED))

    # Arrow WAITING_ACK -> SUCCESS
    p.append(arrow(450, 130, 545, 220, color=OK_STK, sw=2.0))
    p.append(text(515, 165, "ACK(ACCEPTED)", size=11, bold=True, color=OK_STK))

    # SUCCESS
    p.append(fitbox(550, 200, 180, 60, "SUCCESS (Термінальний)\nДію підтверджено!\nUI: розблокувати", size=12, fill=OK_FILL, stroke=OK_STK))

    # Arrow IN_PROGRESS -> SUCCESS
    p.append(arrow(640, 140, 640, 195, color=OK_STK, sw=1.8))
    p.append(text(685, 170, "ACK(ACCEPTED)", size=10, color=OK_STK))

    # Arrow WAITING_ACK -> REJECTED
    p.append(arrow(430, 155, 545, 340, color=ERR_STK, sw=1.8))
    p.append(text(460, 255, "ACK(DENIED /\nFAILED / UNSUPPORTED)", size=10, bold=True, color=ERR_STK))

    # REJECTED
    p.append(fitbox(550, 320, 195, 70, "REJECTED (Термінальний)\nБорт відхилив наказ!\nПовторів НЕ робити, UI: помилка", size=11, fill=ERR_FILL, stroke=ERR_STK))

    # Arrow WAITING_ACK -> RETRYING (timeout, retries < MAX)
    p.append(arrow(335, 155, 335, 275, color=POS, sw=1.8))
    p.append(text(285, 215, "Таймаут\nretries < 3", size=10, bold=True, color=POS))

    # RETRYING
    p.append(fitbox(270, 280, 190, 70, "RETRYING\nconfirmation++, retries++\nПовторна відправка кадру", size=12, fill=TX_FILL, stroke=TX_STK))

    # Arrow RETRYING -> WAITING_ACK
    p.append(arrow(395, 280, 395, 160, color=TX_STK, sw=1.8))
    p.append(text(445, 215, "Кадр надіслано\nСтарт таймера", size=10, color=TX_STK))

    # Arrow RETRYING -> TIMEOUT_FAIL (retries >= MAX)
    p.append(arrow(270, 315, 175, 315, color=ERR_STK, sw=1.8))
    p.append(text(220, 302, "retries ≥ 3", size=10, bold=True, color=ERR_STK))

    # TIMEOUT_FAIL
    p.append(fitbox(20, 280, 150, 70, "TIMEOUT_FAIL\n(Термінальний)\nКанал втрачено!\nUI: збій доставки", size=11, fill=ERR_FILL, stroke=ERR_STK))

    # Bottom explanatory note
    p.append(rect(20, 420, 800, 75, fill=FILL, stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 442, "Головне правило автомату: при відхиленні (DENIED) повтори ЗАБОРОНЕНІ — це свідома відмова борту.", size=12, bold=True, color=INK))
    p.append(text(420, 465, "Повтори робляться ТІЛЬКИ при тиші (таймаут), а поле confirmation сигналізує борту про повтор спроби.", size=11, color=MUTED))

    render(os.path.join(OUT, "command-ack-fsm.svg"), W, H, *p)


# ── 3. idempotency-lost-ack.svg ─────────────────────────────────────────────
def fig_idempotency_lost_ack():
    W, H = 840, 500
    p = []
    p.append(text(W/2, 28, "Загублений ACK: ідемпотентна дія проти пастки подвійного спрацьовування", size=16, bold=True))

    cx1 = 215
    cx2 = 625

    p.append(rect(15, 55, 395, 425, fill=OK_FILL, stroke=OK_STK, sw=1.2, rx=6))
    p.append(text(cx1, 80, "ІДЕМПОТЕНТНА КОМАНДА", size=14, bold=True, color=OK_STK))
    p.append(text(cx1, 100, "f(f(x)) = f(x) — безпечний повтор", size=11, color=MUTED))
    p.append(text(cx1, 118, "Приклад: SET_MODE(GUIDED) / ARM / SET_SERVO", size=10, color=INK))

    y = 135
    p.append(fitbox(30, y, 160, 45, "GCS: Set Mode Guided\n(confirmation = 0)", size=11, fill=TX_FILL, stroke=TX_STK))
    p.append(arrow(195, y + 22, 230, y + 22, color=TX_STK, sw=1.5))
    p.append(fitbox(235, y, 160, 45, "FC: Режим = GUIDED\nШле ACK(ACCEPTED)", size=11, fill=OK_FILL, stroke=OK_STK))

    y += 65
    p.append(arrow(315, y, 220, y, color=OK_STK, sw=1.5))
    p.append(text(205, y + 4, "✖", size=14, bold=True, color=POS))
    p.append(text(145, y + 4, "ACK упав у шумі!", size=10, color=POS))

    y += 45
    p.append(fitbox(30, y, 160, 45, "GCS: Таймаут 1000 мс\nПовтор: Set Mode Guided\n(confirmation = 1)", size=10, fill=TX_FILL, stroke=TX_STK))
    p.append(arrow(195, y + 22, 230, y + 22, color=TX_STK, sw=1.5))
    p.append(fitbox(235, y, 160, 45, "FC: Режим уже GUIDED!\nНіякої шкоди нема.\nШле ACK(ACCEPTED)", size=10, fill=OK_FILL, stroke=OK_STK))

    y += 65
    p.append(arrow(235, y + 10, 195, y + 10, color=OK_STK, sw=1.8))
    p.append(fitbox(30, y - 5, 160, 40, "GCS: ACK отримано!\nУспіх операції.", size=11, fill=OK_FILL, stroke=OK_STK))

    p.append(text(cx1, 445, "Повторне виконання НЕ змінює кінцевий стан.", size=11, bold=True, color=OK_STK))


    # Права колонка: Неідемпотентна команда
    p.append(rect(430, 55, 395, 425, fill=ERR_FILL, stroke=ERR_STK, sw=1.2, rx=6))
    p.append(text(cx2, 80, "НЕІДЕМПОТЕНТНА КОМАНДА", size=14, bold=True, color=ERR_STK))
    p.append(text(cx2, 100, "f(f(x)) ≠ f(x) — небезпека подвійного клацання!", size=11, color=MUTED))
    p.append(text(cx2, 118, "Приклад: TOGGLE_RELAY / DROP_CARGO / SHUTTER", size=10, color=INK))

    y = 135
    p.append(fitbox(445, y, 160, 45, "GCS: Toggle Gripper\n(confirmation = 0)", size=11, fill=TX_FILL, stroke=TX_STK))
    p.append(arrow(610, y + 22, 645, y + 22, color=TX_STK, sw=1.5))
    p.append(fitbox(650, y, 160, 45, "FC: Замок ВІДКРИТО!\nВантаж скинуто. Шле ACK", size=11, fill=OK_FILL, stroke=OK_STK))

    y += 65
    p.append(arrow(730, y, 635, y, color=OK_STK, sw=1.5))
    p.append(text(620, y + 4, "✖", size=14, bold=True, color=POS))
    p.append(text(555, y + 4, "ACK упав у шумі!", size=10, color=POS))

    y += 45
    p.append(fitbox(445, y, 160, 55, "GCS: Таймаут 1000 мс\nПовтор: Toggle Gripper\n(confirmation = 1)", size=10, fill=TX_FILL, stroke=TX_STK))
    p.append(arrow(610, y + 27, 645, y + 27, color=TX_STK, sw=1.5))
    
    p.append(fitbox(650, y, 165, 55, "БЕЗ ДЕДУПЛІКАЦІЇ:\nFC знову перемикає замок!\n(Аварійне закриття)", size=10, fill=ERR_FILL, stroke=ERR_STK))

    y += 75
    p.append(fitbox(445, y, 370, 60, "ЗАХИСТ ЧЕРЕЗ CONFIRMATION:\nFC бачить confirmation = 1 для щойно виконаної команди →\nНЕ чіпає замок удруге, а лише ПОВТОРЮЄ кешований ACK!", size=11, fill=WARN_FILL, stroke=WARN_STK))

    p.append(text(cx2, 445, "confirmation > 0 дозволяє борту відрізнити ретрай від нової дії.", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "idempotency-lost-ack.svg"), W, H, *p)


# ── 4. retry-storm-buffer.svg ───────────────────────────────────────────────
def fig_retry_storm_buffer():
    W, H = 840, 460
    p = []
    p.append(text(W/2, 28, "Чому короткий таймаут створює шторм повторів у буфері модема", size=16, bold=True))

    # Блок 1 (y = 55..235)
    y1 = 55
    p.append(rect(15, y1, 810, 180, fill=ERR_FILL, stroke=ERR_STK, sw=1.2, rx=6))
    p.append(text(30, y1 + 22, "АНТИПАТЕРН: Таймаут 100 мс на напівдуплексному лінку (RTT ефіру ≈ 120–250 мс)", size=13, bold=True, color=ERR_STK, anchor="start"))

    t_y = y1 + 65
    p.append(line(40, t_y, 780, t_y, color=LINE, sw=1.5))
    p.append(text(790, t_y + 4, "t", size=12, bold=True, color=LINE))

    times = [60, 180, 300, 420]
    for i, tx in enumerate(times):
        p.append(line(tx, t_y - 8, tx, t_y + 8, color=TX_STK, sw=2.0))
        p.append(text(tx, t_y - 14, "t = %dмс" % (i * 100), size=10, color=MUTED))
        p.append(fitbox(tx - 45, t_y + 15, 90, 36, "Спроба #%d\n(conf=%d)" % (i, i), size=10, fill=TX_FILL, stroke=TX_STK))

    p.append(rect(540, t_y + 15, 270, 75, fill=FILL, stroke=POS, sw=1.5, rx=4))
    p.append(text(675, t_y + 35, "Буфер UART модема (256B)", size=11, bold=True, color=POS))
    p.append(text(675, t_y + 55, "ПЕРЕПОВНЕННЯ: 4 копії команди\nвитісняють потік ACK і телеметрії!", size=10, color=POS))
    p.append(arrow(470, t_y + 33, 535, t_y + 33, color=POS, sw=2.0))

    # Блок 2 (y = 255..435)
    y2 = 255
    p.append(rect(15, y2, 810, 180, fill=OK_FILL, stroke=OK_STK, sw=1.2, rx=6))
    p.append(text(30, y2 + 22, "НОРМА: Зважений таймаут 800–1000 мс (запас на RTT + чергу борту)", size=13, bold=True, color=OK_STK, anchor="start"))

    t_y2 = y2 + 65
    p.append(line(40, t_y2, 780, t_y2, color=LINE, sw=1.5))
    p.append(text(790, t_y2 + 4, "t", size=12, bold=True, color=LINE))

    p.append(line(60, t_y2 - 8, 60, t_y2 + 8, color=TX_STK, sw=2.0))
    p.append(text(60, t_y2 - 14, "t = 0мс", size=10, color=MUTED))
    p.append(fitbox(15, t_y2 + 15, 100, 40, "Спроба #0\n(conf=0)", size=10, fill=TX_FILL, stroke=TX_STK))

    p.append(arrow(120, t_y2 + 35, 340, t_y2 + 35, color=MUTED, sw=1.5))
    p.append(text(230, t_y2 + 22, "TDD слот передачі (50мс) + виконання на борту (30мс)", size=10, color=MUTED))

    p.append(line(360, t_y2 - 8, 360, t_y2 + 8, color=OK_STK, sw=2.0))
    p.append(text(360, t_y2 - 14, "t ≈ 180мс", size=10, color=OK_STK))
    p.append(fitbox(310, t_y2 + 15, 110, 40, "ACK(ACCEPTED)\nприйшов у GCS!", size=10, fill=OK_FILL, stroke=OK_STK))

    p.append(rect(460, t_y2 + 15, 350, 65, fill=FILL, stroke=OK_STK, sw=1.2, rx=4))
    p.append(text(635, t_y2 + 35, "Буфер вільний, лінк стабільний", size=11, bold=True, color=OK_STK))
    p.append(text(635, t_y2 + 55, "Жодних фантомних пакетів, UI миттєво впевнений у результаті", size=10, color=INK))

    render(os.path.join(OUT, "retry-storm-buffer.svg"), W, H, *p)


if __name__ == "__main__":
    fig_three_outcomes()
    fig_command_ack_fsm()
    fig_idempotency_lost_ack()
    fig_retry_storm_buffer()
    print("All figures generated successfully.")
