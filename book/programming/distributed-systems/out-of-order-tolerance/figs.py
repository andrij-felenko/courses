# -*- coding: utf-8 -*-
"""Фігури до теми «Толерантність до безладу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / блокування / затримка
COOL = "#eaf0fd"   # нейтральне / структури / буфери
GOOD = "#e8f6ee"   # успіх / паралелізм / пропускна здатність
WARN = "#fef9e7"   # очікування / вотермарк / прогалина

# ── 1. Блокування початку черги (Head-of-Line Blocking) проти паралельної обробки
def fig_head_of_line_blocking():
    W, H = 1140, 480
    f = []

    f.append(text(W / 2, 28, "Порівняння: строгий FIFO-порядок проти толерантної до безладу обробки", size=16, bold=True))

    # Ліва колонка: Строгий FIFO
    x0, x1 = 40.0, 560.0
    mid_left = (x0 + x1) / 2
    f.append(rect(x0, 55, x1 - x0, 395, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(mid_left, 82, "Строгий FIFO (одна черга / єдиний потік)", size=14, bold=True, color=POS))

    f.append(fitbox(x0 + 25, 115, 80, 45, "#1 (OK)\nоброблено", size=11, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x0 + 125, 115, 110, 45, "#2 (Затримка)\nблокує чергу!", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(fitbox(x0 + 255, 115, 75, 45, "#3 (Чекає)\nзависло", size=11, fill=WARN, stroke=LINE))
    f.append(fitbox(x0 + 345, 115, 75, 45, "#4 (Чекає)\nзависло", size=11, fill=WARN, stroke=LINE))
    f.append(fitbox(x0 + 435, 115, 75, 45, "#5 (Чекає)\nзависло", size=11, fill=WARN, stroke=LINE))

    f.append(arrow(x0 + 105, 137, x0 + 125, 137, color=LINE, sw=1.5))
    f.append(arrow(x0 + 235, 137, x0 + 255, 137, color=LINE, sw=1.5))
    f.append(arrow(x0 + 330, 137, x0 + 345, 137, color=LINE, sw=1.5))
    f.append(arrow(x0 + 420, 137, x0 + 435, 137, color=LINE, sw=1.5))

    f.append(fitbox(mid_left - 130, 195, 260, 50, "Єдиний споживач (Single Consumer)\nПростоює в очікуванні повідомлення #2", size=12, bold=True, fill=WARM, stroke=POS))
    f.append(arrow(mid_left, 160, mid_left, 195, color=POS, sw=1.8))

    f.append(fitbox(x0 + 20, 265, 480, 165,
                    "Наслідки суворого впорядкування:\n"
                    "• Head-of-Line (HoL) блокування: збій #2 зупиняє всі наступні задачі.\n"
                    "• Пропускна здатність обмежена швидкістю одного ядра / з'єднання.\n"
                    "• Реплікація та ретраї ламають порядок або створюють каскадні затримки.\n"
                    "• Час очікування для #5 зростає експоненційно при мережевих збоях.",
                    size=12, fill="#ffffff", stroke=LINE, sw=1.2))

    # Права колонка: Толерантність до безладу
    x2, x3 = 580.0, 1100.0
    mid_right = (x2 + x3) / 2
    f.append(rect(x2, 55, x3 - x2, 395, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(mid_right, 82, "Толерантна архітектура (паралельні воркери)", size=14, bold=True, color=FIELD))

    workers = [
        ("Воркер 1", "#1 виконано", GOOD, FIELD),
        ("Воркер 2", "#2 retry (окремо)", WARM, POS),
        ("Воркер 3", "#3 виконано", GOOD, FIELD),
        ("Воркер 4", "#4 виконано", GOOD, FIELD),
        ("Воркер 5", "#5 виконано", GOOD, FIELD),
    ]
    for i, (w_name, w_task, bg_c, strk_c) in enumerate(workers):
        wy = 112 + i * 28
        f.append(fitbox(x2 + 25, wy, 120, 24, w_name, size=11, bold=True, fill=COOL, stroke=LINE))
        f.append(arrow(x2 + 145, wy + 12, x2 + 195, wy + 12, color=LINE, sw=1.4))
        f.append(fitbox(x2 + 195, wy, 290, 24, w_task, size=11, bold=True, fill=bg_c, stroke=strk_c))

    f.append(fitbox(x2 + 20, 265, 480, 165,
                    "Переваги толерантності до безладу:\n"
                    "• Повільне або помилкове повідомлення #2 не гальмує #3, #4 та #5.\n"
                    "• Масштабування: N незалежних воркерів на повну швидкість каналу.\n"
                    "• Комутативні операції та монотонні версії усувають ризик аномалій.\n"
                    "• Стійкість: мережеві затримки локалізуються без каскадного колапсу.",
                    size=12, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'head-of-line-blocking.svg'), W, H, *f)


# ── 2. Таксономія стратегій толерантності до безладу
def fig_out_of_order_strategies():
    W, H = 1140, 470
    f = []

    f.append(text(W / 2, 28, "Чотири стратегії подолання безладу в розподілених системах", size=16, bold=True))

    cards = [
        (35.0, 290.0, "1. Комутативність\n(Algebraic Commutativity)",
         "Суть: стан не залежить від порядку дій.\n\n"
         "• Формула: A · B = B · A\n"
         "• Приклади: CRDT (PN-Counter, OR-Set),\n  додавання коштів, логування подій.\n"
         "• Ціна: обмежений клас бізнес-операцій.",
         GOOD, FIELD),
        (305.0, 560.0, "2. Монотонні версії\n(Monotonic Guards / LWW)",
         "Суть: ігнорування або скидання старих версій.\n\n"
         "• Правило: if v_msg < v_state: discard\n"
         "• Приклади: Sequence numbers, епохи,\n  Fencing tokens, логічні годинники.\n"
         "• Ціна: втрата старих проміжних правок.",
         COOL, LINE),
        (575.0, 830.0, "3. Віконний буфер\n(Resequencer Buffer)",
         "Суть: тимчасове утримання та відновлення черги.\n\n"
         "• Механізм: ковзне вікно + таймаут прогалини\n"
         "• Приклади: TCP RX Buffer, Kafka Consumer\n  sliding resequencer, Flink Watermark.\n"
         "• Ціна: витрата RAM та додатковий лаг.",
         WARN, LINE),
        (845.0, 1105.0, "4. Авансовий стан\n(Tombstones / Inversion)",
         "Суть: готовність прийняти скасування до створення.\n\n"
         "• Механізм: збереження маркерів-надгробків\n"
         "• Приклади: 'Cancel' прийшов раніше за 'Create';\n  створюється запис 'Cancelled-Placeholder'.\n"
         "• Ціна: складніший автомат станів (FSM).",
         WARM, POS),
    ]

    for x0, x1, title, body, bg_c, strk_c in cards:
        w = x1 - x0
        f.append(rect(x0, 55, w, 335, fill=FILL, stroke=strk_c, sw=1.4, rx=8))
        f.append(fitbox(x0 + 10, 70, w - 20, 52, title, size=12.5, bold=True, fill=bg_c, stroke=strk_c))
        f.append(fitbox(x0 + 10, 132, w - 20, 245, body, size=11.5, fill="#ffffff", stroke=LINE, sw=1.1))

    f.append(fitbox(35, 400, 1070, 55,
                    "Інженерний вибір: замість блокування всього конвеєра заради глобального FIFO, "
                    "архітектор обирає математичну комутативність або локальні фільтри та буфери.",
                    size=12.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.3))

    render(os.path.join(OUT, 'out-of-order-strategies.svg'), W, H, *f)


# ── 3. Механізм буфера перевпорядкування (Resequencer Sliding Window)
def fig_resequencer_sliding_window():
    W, H = 1140, 500
    f = []

    f.append(text(W / 2, 28, "Архітектура ковзного буфера перевпорядкування (Resequencer Buffer)", size=16, bold=True))

    f.append(rect(40, 55, 1060, 85, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(160, 80, "Вхідний несинхронізований потік:", size=13, bold=True))

    in_msgs = [
        (300, "#101", GOOD),
        (380, "#104", WARM),
        (460, "#102", GOOD),
        (540, "#105", WARM),
        (620, "#106", WARM),
        (700, "#103 (запізніле)", WARN),
    ]
    for x, label, col in in_msgs:
        f.append(fitbox(x, 70, 70, 36, label, size=10.5, bold=True, fill=col, stroke=LINE))
        f.append(arrow(x + 35, 110, x + 35, 155, color=LINE, sw=1.4))

    f.append(rect(40, 160, 1060, 190, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(170, 190, "Стан ковзного буфера в RAM:", size=13, bold=True, color=INK))

    slots = [
        (260, "#101", "Передано", GOOD, FIELD),
        (370, "#102", "Передано", GOOD, FIELD),
        (480, "#103", "ПРОГАЛИНА!\nТаймер 45 мс", WARM, POS),
        (590, "#104", "У буфері", COOL, LINE),
        (700, "#105", "У буфері", COOL, LINE),
        (810, "#106", "У буфері", COOL, LINE),
    ]
    for x, s_num, s_st, bg_c, strk_c in slots:
        f.append(rect(x, 210, 100, 75, fill=bg_c, stroke=strk_c, sw=1.5, rx=6))
        f.append(text(x + 50, 235, s_num, size=12.5, bold=True, color=INK))
        f.append(fitbox(x + 5, 248, 90, 30, s_st, size=9.5, bold=True, fill="#ffffff", stroke=strk_c))

    f.append(arrow(530, 335, 530, 290, color=POS, sw=2.0))
    f.append(text(530, 348, "Очікуваний Sequence: #103", size=11.5, bold=True, color=POS))

    f.append(rect(40, 370, 1060, 105, fill=FILL, stroke=LINE, sw=1.3, rx=8))
    f.append(text(180, 395, "Вихід до бізнес-обробника:", size=13, bold=True, color=FIELD))

    f.append(fitbox(300, 395, 760, 65,
                    "1. Повідомлення #101 та #102 видано споживачеві миттєво.\n"
                    "2. Повідомлення #104, #105, #106 утримуються в пам'яті до прибуття #103.\n"
                    "3. Якщо #103 прибуває або спливає таймаут прогалини (Gap Timeout) — вікно зсувається вперед.",
                    size=11.5, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'resequencer-sliding-window.svg'), W, H, *f)


# ── 4. Часова шкала та вотермарки (Watermark Timeline)
def fig_watermark_event_time():
    W, H = 1140, 490
    f = []

    f.append(text(W / 2, 28, "Час події (Event Time) проти часу обробки (Processing Time) та механізм Watermark", size=16, bold=True))

    f.append(rect(40, 55, 1060, 300, fill=FILL, stroke=LINE, sw=1.3, rx=8))

    f.append(arrow(80, 270, 1020, 270, color=LINE, sw=2))
    f.append(text(1030, 274, "Час обробки (Processing Time)", size=11.5, bold=True, anchor="start"))

    events = [
        (130, "e1 (t=10:00)", "Вчасно", GOOD, FIELD),
        (260, "e2 (t=10:01)", "Вчасно", GOOD, FIELD),
        (400, "e4 (t=10:04)", "Випередження", COOL, LINE),
        (560, "e3 (t=10:02)", "Запізніле (OK)", WARN, LINE),
        (720, "e6 (t=10:06)", "Вчасно", GOOD, FIELD),
        (900, "e5 (t=10:03)", "Критично пізнє!\n(Після Watermark)", WARM, POS),
    ]

    for px, label, note, bg_c, strk_c in events:
        f.append(line(px, 120, px, 270, color=MUTED, sw=1.2, dash="3,3"))
        f.append(fitbox(px - 50, 85, 100, 30, label, size=11, bold=True, fill=bg_c, stroke=strk_c))
        f.append(circle(px, 270, 5, fill=strk_c, stroke=LINE, sw=1.2))
        f.append(fitbox(px - 55, 285, 110, 38, note, size=9.5, bold=True, fill="#ffffff", stroke=strk_c))

    f.append(line(80, 210, 1000, 150, color=POS, sw=2.2, dash="6,4"))
    f.append(text(650, 160, "Лінія Watermark: WM(t) = max(EventTime) − Δ", size=12, bold=True, color=POS))

    f.append(line(780, 65, 780, 270, color=LINE, sw=1.8))
    f.append(fitbox(710, 68, 140, 24, "Закриття вікна [10:00-10:05]", size=9.5, bold=True, fill=WARN, stroke=LINE))

    f.append(fitbox(40, 370, 1060, 100,
                    "Механізм роботи Watermark:\n"
                    "• Watermark — це монотонна обіцянка системи: «ми більше не очікуємо подій із EventTime < W».\n"
                    "• Подія e3 (10:02) надійшла пізніше за e4 (10:04), але ДО спрацьовування вотермарка — вона враховується у вікні.\n"
                    "• Подія e5 (10:03) прибула ПІСЛЯ закриття вікна (Dropped / Late Data) — її відправляють у Dead-Letter Queue або Side Output.\n",
                    size=12, fill="#ffffff", stroke=LINE, sw=1.3))

    render(os.path.join(OUT, 'watermark-event-time.svg'), W, H, *f)


if __name__ == '__main__':
    fig_head_of_line_blocking()
    fig_out_of_order_strategies()
    fig_resequencer_sliding_window()
    fig_watermark_event_time()
    print("Всі фігури згенеровано успішно.")
