# -*- coding: utf-8 -*-
"""Фігури до теми «Таймаути і бюджет часу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / зависання / вичерпання
COOL = "#eaf0fd"   # нейтральне / запити
GOOD = "#e8f6ee"   # успіх / швидке відсікання


# ── 1. Каскадне вичерпання ресурсів без таймаутів ─────────────────────────────
def cascading_hang():
    W, H = 1180, 620
    f = []

    # Заголовок зверху
    f.append(fitbox(40, 24, 1100, 48,
                    "КАСКАДНЕ БЛОКУВАННЯ: як одне зависання глибинного вузла паралізує всю систему",
                    size=14, bold=True, fill=COOL))

    # Стовпчик 1: Клієнти
    xC = 120.0
    f.append(rect(40, 100, 160, 400, fill=FILL, stroke=MUTED, sw=1.5))
    f.append(text(xC, 130, "Клієнти / Браузери", size=13, bold=True))
    for i in range(5):
        y = 175 + i * 65
        f.append(rect(55, y - 18, 130, 36, fill=COOL, stroke=NEG, sw=1.2))
        f.append(text(xC, y + 4, f"Запит #{i+1}", size=11))

    # Стрілки від клієнтів до Шлюзу
    for i in range(5):
        y = 175 + i * 65
        f.append(arrow(185, y, 255, y, color=NEG, sw=1.4))

    # Стовпчик 2: Сервіс A (Шлюз API)
    xA = 340.0
    f.append(rect(260, 100, 160, 400, fill=FILL, stroke=MUTED, sw=1.5))
    f.append(text(xA, 130, "Сервіс A (Шлюз)", size=13, bold=True))
    f.append(text(xA, 150, "Пул: 100% заблоковано", size=11, color=POS, bold=True))
    for i in range(5):
        y = 175 + i * 65
        f.append(rect(275, y - 18, 130, 36, fill=WARM, stroke=POS, sw=1.4))
        f.append(text(xA, y + 4, f"Потік #{i+1} чекає B", size=11, color=POS))

    # Стрілки від A до B
    for i in range(5):
        y = 175 + i * 65
        f.append(arrow(405, y, 475, y, color=POS, sw=1.4))

    # Стовпчик 3: Сервіс B (Бізнес-логіка)
    xB = 560.0
    f.append(rect(480, 100, 160, 400, fill=FILL, stroke=MUTED, sw=1.5))
    f.append(text(xB, 130, "Сервіс B", size=13, bold=True))
    f.append(text(xB, 150, "Пул потоків вичерпано", size=11, color=POS, bold=True))
    for i in range(5):
        y = 175 + i * 65
        f.append(rect(495, y - 18, 130, 36, fill=WARM, stroke=POS, sw=1.4))
        f.append(text(xB, y + 4, f"Потік #{i+1} чекає C", size=11, color=POS))

    # Стрілки від B до C
    for i in range(5):
        y = 175 + i * 65
        f.append(arrow(625, y, 695, y, color=POS, sw=1.4))

    # Стовпчик 4: Сервіс C (Глибинна служба / База)
    xC3 = 780.0
    f.append(rect(700, 100, 160, 400, fill=WARM, stroke=POS, sw=2.0))
    f.append(text(xC3, 130, "Сервіс C / База", size=13, bold=True, color=POS))
    f.append(text(xC3, 150, "ЗАВИС / Lock stall", size=11, color=POS, bold=True))
    f.append(fitbox(715, 175, 130, 290,
                    "Блокування на диску\nабо дедлок у транзакції\n\nНе відповідає,\nале з'єднання тримає\n\nМовчання без обриву",
                    size=12, fill="#ffffff", stroke=POS, sw=1.4))

    # Стовпчик 5: Сервіс D (Здоровий сусідній сервіс)
    xD = 1010.0
    f.append(rect(930, 100, 160, 400, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(xD, 130, "Сервіс D (Здоровий)", size=13, bold=True, color=FIELD))
    f.append(text(xD, 150, "Готовий приймати", size=11, color=FIELD))
    f.append(fitbox(945, 175, 130, 290,
                    "Працює ідеально,\nале запити до нього\nНЕ доходять:\n\nСервіс A вичерпав усі\nпотоки на очікуванні C\nй більше не приймає нічого",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.4))

    # Пояснення знизу
    f.append(fitbox(40, 524, 1100, 72,
                    "Без жорстких таймаутів повільність одного компонента затягує в зависання всі вищі шари.\n"
                    "Потоки пулів блокуються на викликах, що мовчать, і сервіс втрачає здатність обслуговувати навіть ті гілки,\n"
                    "які не мають жодного стосунку до збійного вузла.",
                    size=12.5, fill=FILL))

    render(os.path.join(OUT, 'cascading-hang.svg'), W, H, *f)


# ── 2. Таймаут на кожен виклик проти наскрізного дедлайну ─────────────────────
def timeout_vs_deadline():
    W, H = 1180, 680
    f = []

    # Верхня панель: Статичні таймаути на кожен крок (Per-hop Timeouts)
    yTop = 40.0
    f.append(rect(40, yTop, 1100, 270, fill="#ffffff", stroke=POS, sw=1.6))
    f.append(fitbox(55, yTop + 12, 1070, 36,
                    "СТАТИЧНІ ТАЙМАУТИ НА ВИКЛИК: роздуття сумарного часу та «зомбі-робота»",
                    size=13, bold=True, fill=WARM, stroke=POS, sw=1.4))

    # Схема зверху
    # Клієнт (таймаут 3с)
    f.append(rect(70, yTop + 65, 180, 50, fill=COOL, stroke=NEG, sw=1.4))
    f.append(text(160, yTop + 85, "Клієнт (таймаут 3 с)", size=12, bold=True))
    f.append(text(160, yTop + 103, "здається о T = 3.0 c", size=11, color=POS))

    # Стрілка
    f.append(arrow(250, yTop + 90, 320, yTop + 90, color=LINE, sw=1.4))

    # Сервіс A (таймаут 2с)
    f.append(rect(320, yTop + 65, 200, 50, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(420, yTop + 85, "Сервіс A (таймаут 2 с)", size=12, bold=True))
    f.append(text(420, yTop + 103, "чекає B до 2 секунд", size=11))

    # Стрілка
    f.append(arrow(520, yTop + 90, 590, yTop + 90, color=LINE, sw=1.4))

    # Сервіс B (таймаут 2с)
    f.append(rect(590, yTop + 65, 200, 50, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(690, yTop + 85, "Сервіс B (таймаут 2 с)", size=12, bold=True))
    f.append(text(690, yTop + 103, "чекає C до 2 секунд", size=11))

    # Стрілка
    f.append(arrow(790, yTop + 90, 860, yTop + 90, color=LINE, sw=1.4))

    # Сервіс C (таймаут 2с)
    f.append(rect(860, yTop + 65, 220, 50, fill=WARM, stroke=POS, sw=1.4))
    f.append(text(970, yTop + 85, "Сервіс C (зависання)", size=12, bold=True, color=POS))
    f.append(text(970, yTop + 103, "палить CPU і транзакцію", size=11, color=POS))

    # Часова шкала зверху
    yBar1 = yTop + 140
    f.append(line(70, yBar1, 1080, yBar1, color=MUTED, sw=1.2))
    # Відмітки 0s, 1s, 2s, 3s, 4s, 5s, 6s
    for s in range(7):
        x = 70 + s * 160
        f.append(line(x, yBar1 - 6, x, yBar1 + 6, color=MUTED, sw=1.2))
        f.append(text(x, yBar1 + 20, f"{s} c", size=11, color=MUTED))

    # Смуга життя
    f.append(rect(70, yBar1 + 32, 480, 24, fill=COOL, stroke=NEG, sw=1.4))
    f.append(text(310, yBar1 + 48, "Клієнт чекає (0 .. 3 с) → ОБРИВАЄ ЗАПИТ", size=11, color=NEG, bold=True))

    f.append(rect(550, yBar1 + 32, 480, 24, fill=WARM, stroke=POS, sw=1.4, rx=4))
    f.append(text(790, yBar1 + 48, "«ЗОМБІ-ОБЧИСЛЕННЯ»: Сервіси B і C рахують ще 3 с, але відповідь ніхто не чекає!",
                  size=11, color=POS, bold=True))

    f.append(fitbox(70, yBar1 + 66, 1010, 32,
                    "Сумарний гірший час: 2с + 2с + 2с = 6с. Клієнт пішов на 3-й секунді, а сервери спалили ресурси даремно.",
                    size=11.5, fill=FILL))

    # Нижня панель: Наскрізний дедлайн (End-to-End Deadline Propagation)
    yBot = 330.0
    f.append(rect(40, yBot, 1100, 320, fill="#ffffff", stroke=FIELD, sw=1.6))
    f.append(fitbox(55, yBot + 12, 1070, 36,
                    "НАСКРІЗНЕ ПРОКИДАННЯ ДЕДЛАЙНУ (DEADLINE PROPAGATION): спільний бюджет часу",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=1.4))

    # Клієнт передає deadline=500ms
    f.append(rect(70, yBot + 65, 200, 50, fill=COOL, stroke=NEG, sw=1.4))
    f.append(text(170, yBot + 85, "Клієнт (бюджет 500 мс)", size=12, bold=True))
    f.append(text(170, yBot + 103, "заголовок grpc-timeout: 500m", size=11, color=NEG))

    f.append(arrow(270, yBot + 90, 340, yBot + 90, color=FIELD, sw=1.6))

    # Сервіс A (залишок 420ms)
    f.append(rect(340, yBot + 65, 210, 50, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(445, yBot + 85, "Сервіс A (витратив 80 мс)", size=12, bold=True))
    f.append(text(445, yBot + 103, "прокидає залишок: 420 мс", size=11, color=FIELD))

    f.append(arrow(550, yBot + 90, 620, yBot + 90, color=FIELD, sw=1.6))

    # Сервіс B (залишок 200ms)
    f.append(rect(620, yBot + 65, 210, 50, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(725, yBot + 85, "Сервіс B (витратив 220 мс)", size=12, bold=True))
    f.append(text(725, yBot + 103, "прокидає залишок: 200 мс", size=11, color=FIELD))

    f.append(arrow(830, yBot + 90, 900, yBot + 90, color=FIELD, sw=1.6))

    # Сервіс C (дедлайн вичерпано → миттєве скасування)
    f.append(rect(900, yBot + 65, 210, 50, fill=WARM, stroke=POS, sw=1.4))
    f.append(text(1005, yBot + 85, "Сервіс C (залишок 0 мс)", size=12, bold=True, color=POS))
    f.append(text(1005, yBot + 103, "СКАСУВАННЯ / ABORT", size=11, color=POS, bold=True))

    # Часова шкала знизу
    yBar2 = yBot + 140
    f.append(line(70, yBar2, 1080, yBar2, color=MUTED, sw=1.2))
    for ms in range(0, 601, 100):
        x = 70 + (ms / 600.0) * 960
        f.append(line(x, yBar2 - 6, x, yBar2 + 6, color=MUTED, sw=1.2))
        f.append(text(x, yBar2 + 20, f"{ms} мс", size=11, color=MUTED))

    # Бюджет
    f.append(rect(70, yBar2 + 32, 800, 24, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(470, yBar2 + 48, "Корисна робота в межах бюджету (0 .. 500 мс)", size=11, color=FIELD, bold=True))

    f.append(rect(870, yBar2 + 32, 160, 24, fill=WARM, stroke=POS, sw=1.4, rx=4))
    f.append(text(950, yBar2 + 48, "Відсічено: 0 витрат", size=11, color=POS, bold=True))

    f.append(fitbox(70, yBar2 + 66, 1010, 40,
                    "Щойно бюджет вичерпано на рівні T = 500 мс, усі нижчі виклики скасовуються негайно (context cancellation),\n"
                    "звільняючи потоки, з'єднання і блокування для інших корисних запитів.",
                    size=12, fill=FILL))

    render(os.path.join(OUT, 'timeout-vs-deadline.svg'), W, H, *f)


# ── 3. Анатомія таймаутів на життєвому циклі запиту ───────────────────────────
def timeout_layers():
    W, H = 1180, 640
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "ШАРИ ТАЙМАУТІВ: де саме таймери контролюють ресурси на шляху запиту",
                    size=14, bold=True, fill=COOL))

    layers = [
        ("1. Connect Timeout", "TCP SYN / SYN-ACK", "Обмежує час встановлення TCP-з'єднання з віддаленим хостом.\n"
         "Захищає від зависання, коли вузол вимкнений з мережі або переповнено SYN backlog.\n"
         "Типове значення: 200–1000 мс.", COOL, NEG),
        ("2. Queue / Admission Timeout", "Черга пулу обробників", "Час перебування запиту в черзі до того, як вільний потік візьме його в роботу.\n"
         "Якщо час у черзі з'їв весь дедлайн — запит відкидають без виконання (load shedding).\n"
         "Типове значення: 50–200 мс.", WARM, POS),
        ("3. Socket / Idle Timeout", "SO_RCVTIMEO / TCP keepalive", "Максимальна пауза МІЖ сусідніми байтами в сокеті (не весь запит!).\n"
         "Пастка: якщо надсилати по 1 байту кожні 4.9 с при таймауті 5 с — з'єднання висить годинами.\n"
         "Типове значення: 2–5 с.", COOL, NEG),
        ("4. DB / Lock Timeout", "statement_timeout / lock_timeout", "Обмеження тривалості SQL-запиту та очікування блокування рядків у базі даних.\n"
         "Запобігає утриманню 'мертвих' блокувань після того, як HTTP-клієнт уже відвалився.\n"
         "Типове значення: 500–3000 мс.", WARM, POS),
        ("5. End-to-End RPC Deadline", "Контекст запиту / grpc-timeout", "Абсолютний бюджет часу на всю бізнес-операцію від ініціатора до кінця.\n"
         "Прокидається крізь усі мікросервіси та підсумовує витрати на всіх етапах.\n"
         "Типове значення: 300–2000 мс.", GOOD, FIELD),
    ]

    for i, (title, subtitle, desc, bg, col) in enumerate(layers):
        y = 80 + i * 102
        f.append(rect(50, y, 280, 88, fill=bg, stroke=col, sw=1.5))
        f.append(text(190, y + 32, title, size=13, bold=True, color=col))
        f.append(text(190, y + 58, subtitle, size=11, color=MUTED))

        f.append(arrow(340, y + 44, 380, y + 44, color=col, sw=1.6))

        f.append(fitbox(390, y, 740, 88, desc, size=12, fill="#ffffff", stroke=MUTED, sw=1.2))

    f.append(fitbox(50, 592, 1080, 36,
                    "Помилка в будь-якому з цих шарів перетворює систему на вразливу: брак одного таймауту зводить нанівець решту.",
                    size=12, fill=FILL))

    render(os.path.join(OUT, 'timeout-layers.svg'), W, H, *f)


# ── 4. Арифметика розбиття бюджету на підзапити ───────────────────────────────
def deadline_budget_split():
    W, H = 1180, 580
    f = []

    f.append(fitbox(40, 20, 1100, 46,
                    "РОЗРАХУНОК БЮДЖЕТУ ЧАСУ: як залишок дедлайну ділиться між послідовними кроками",
                    size=14, bold=True, fill=COOL))

    x0 = 80.0
    total_w = 1000.0   # 600 мс = 1000 px (1.666 px / мс)
    scale = total_w / 600.0

    yAxis = 110.0
    f.append(line(x0, yAxis, x0 + total_w, yAxis, color=MUTED, sw=1.4))
    for ms in [0, 100, 200, 300, 400, 500, 600]:
        x = x0 + ms * scale
        f.append(line(x, yAxis - 8, x, yAxis + 8, color=MUTED, sw=1.4))
        f.append(text(x, yAxis - 16, f"{ms} мс", size=11.5, color=MUTED))

    # Крок 1: Вхідна черга (40 мс)
    x1 = x0 + 40 * scale
    f.append(rect(x0, yAxis + 30, 40 * scale, 56, fill=WARM, stroke=POS, sw=1.4))
    f.append(fitbox(x0 + 2, yAxis + 34, 40 * scale - 4, 48, "Черга\n40 мс", size=11, color=POS, fill=WARM))

    # Крок 2: Локальні обчислення (60 мс)
    x2 = x1 + 60 * scale
    f.append(rect(x1, yAxis + 30, 60 * scale, 56, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(fitbox(x1 + 2, yAxis + 34, 60 * scale - 4, 48, "Локально\n60 мс", size=11, fill=FILL))

    # Крок 3: Підвиклик 1 (Сервіс авторизації, 150 мс)
    x3 = x2 + 150 * scale
    f.append(rect(x2, yAxis + 30, 150 * scale, 56, fill=COOL, stroke=NEG, sw=1.4))
    f.append(fitbox(x2 + 2, yAxis + 34, 150 * scale - 4, 48, "Виклик 1 (Auth)\n150 мс", size=11, color=NEG, fill=COOL))

    # Крок 4: Підвиклик 2 (Сервіс платежів, факт 180 мс)
    x4 = x3 + 180 * scale
    f.append(rect(x3, yAxis + 30, 180 * scale, 56, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(fitbox(x3 + 2, yAxis + 34, 180 * scale - 4, 48, "Виклик 2 (Платіж)\n180 мс", size=11, color=FIELD, fill=GOOD))

    # Залишок запасу (170 мс)
    f.append(rect(x4, yAxis + 30, 170 * scale, 56, fill="#ffffff", stroke=MUTED, sw=1.4, rx=4))
    f.append(fitbox(x4 + 2, yAxis + 34, 170 * scale - 4, 48, "Невикористаний\nзапас (170 мс)", size=11, color=MUTED, fill="#ffffff"))

    # Блок з формулами та поясненням знизу
    yBox = 240.0
    f.append(rect(x0, yBox, total_w, 200, fill="#ffffff", stroke=MUTED, sw=1.5))

    f.append(text(x0 + 20, yBox + 30, "ПРАВИЛО ОБЧИСЛЕННЯ ТАЙМАУТУ ДЛЯ ПІДВИКЛИКУ (Subcall Budgeting):", size=13, bold=True, anchor="start"))
    f.append(text(x0 + 20, yBox + 60, "T_remain = T_deadline − T_now", size=12.5, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 + 20, yBox + 88, "T_subcall = min( T_configured_limit, T_remain − T_safety_margin )", size=12.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(x0 + 20, yBox + 116, "Якщо T_subcall < T_min_network_rtt → ВІДМОВА ВІДРАЗУ (Fail Fast / Shed Load)", size=12.5, color=POS, bold=True, anchor="start"))

    f.append(fitbox(x0 + 20, yBox + 134, total_w - 40, 54,
                    "Замість передачі статичного ліміту (напр., 400 мс) на кожен підвиклик, клієнт обмежує виклик ЗАЛИШКОМ бюджету.\n"
                    "Якщо після виклику 1 лишилося 350 мс, виклик 2 отримає таймаут min(400, 350 − 20) = 330 мс.",
                    size=12, fill=FILL))

    f.append(fitbox(x0, 460, total_w, 90,
                    "Головний висновок: дедлайн не додається до кожного виклику заново, а ТАНЕ в міру проходження конвеєра.\n"
                    "Кожен наступний сервіс у ланцюжку знає точний залишок часу, завдяки чому не починає безнадійну роботу,\n"
                    "якщо попередня ланка вже з'їла більшу частину доступного бюджету.",
                    size=12.5, fill=COOL))

    render(os.path.join(OUT, 'deadline-budget-split.svg'), W, H, *f)


if __name__ == '__main__':
    cascading_hang()
    timeout_vs_deadline()
    timeout_layers()
    deadline_budget_split()
    print("Всі фігури згенеровано успішно.")
