# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Скінченний автомат станів Запобіжника ─────────────────────────
def fig_circuit_breaker_state_machine():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Скінченний автомат станів запобіжника (Circuit Breaker State Machine)", size=16, bold=True))

    # Стан 1: CLOSED (Замкнений) - Зліва
    frags.append(rect(50, 70, 260, 170, fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    frags.append(text(180, 100, "CLOSED (Замкнений)", size=14, bold=True, color=FIELD))
    frags.append(text(180, 126, "Запити проходять нормально", size=11, color=INK))
    frags.append(text(180, 148, "Ковзне вікно збирає метрики", size=11, color=MUTED))
    frags.append(text(180, 172, "Помилки / Затримки < Поріг", size=11, bold=True, color=FIELD))
    frags.append(text(180, 196, "Потік: 100% до бекенда", size=10, color=MUTED))

    # Стан 2: OPEN (Розімкнений) - Справа
    frags.append(rect(690, 70, 260, 170, fill="#fef2f2", stroke=POS, sw=2, rx=10))
    frags.append(text(820, 100, "OPEN (Розімкнений)", size=14, bold=True, color=POS))
    frags.append(text(820, 126, "Миттєве відхилення (Fail-Fast)", size=11, bold=True, color=POS))
    frags.append(text(820, 148, "Запити блокуються без I/O", size=11, color=INK))
    frags.append(text(820, 172, "Виклик Fallback-стратегій", size=11, color=MUTED))
    frags.append(text(820, 196, "Таймер: очікування відновлення", size=10, color=MUTED))

    # Стан 3: HALF-OPEN (Напіврозімкнений) - Посередині знизу
    frags.append(rect(370, 310, 260, 170, fill="#fffbeb", stroke="#d97706", sw=2, rx=10))
    frags.append(text(500, 340, "HALF-OPEN (Пробний)", size=14, bold=True, color="#d97706"))
    frags.append(text(500, 366, "Пробний пакет запитів", size=11, bold=True, color="#d97706"))
    frags.append(text(500, 388, "Обмежена квота (напр. 10 викликів)", size=11, color=INK))
    frags.append(text(500, 410, "Решта запитів: Fail-Fast", size=11, color=MUTED))
    frags.append(text(500, 434, "Оцінка здоров'я сервісу", size=10, color=MUTED))

    # Перехід 1: CLOSED -> OPEN (Помилки > порогу)
    frags.append(arrow(310, 130, 680, 130, color=POS, sw=2))
    frags.append(rect(410, 105, 180, 24, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(500, 121, "Помилки > 50% у вікні", size=10, bold=True, color=POS))

    # Перехід 2: OPEN -> HALF-OPEN (Таймер сплив)
    frags.append(arrow(780, 240, 635, 330, color="#d97706", sw=2))
    frags.append(rect(695, 275, 170, 24, fill="#ffffff", stroke="#d97706", sw=1, rx=4))
    frags.append(text(780, 291, "Таймаут сплив (waitDuration)", size=10, bold=True, color="#d97706"))

    # Перехід 3: HALF-OPEN -> CLOSED (Пробні успішні)
    frags.append(arrow(370, 340, 230, 245, color=FIELD, sw=2))
    frags.append(rect(145, 275, 170, 24, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(230, 291, "Пробні виклики успішні", size=10, bold=True, color=FIELD))

    # Перехід 4: HALF-OPEN -> OPEN (Збій у пробних)
    frags.append(arrow(580, 310, 720, 245, color=POS, sw=1.8))
    frags.append(rect(560, 240, 150, 24, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(635, 256, "Збій пробного виклику", size=10, bold=True, color=POS))

    return render(os.path.join(IMG, 'circuit-breaker-state-machine.svg'), W, H, *frags)


# ── Фігура 2: Структура кільцевого буфера ковзного вікна ──────────────────────
def fig_sliding_window_ring_buffer():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 28, "Внутрішня організація кільцевого буфера ковзного вікна (Ring Buffer)", size=16, bold=True))

    # Панель 1: Кількісне вікно (Count-based Window)
    frags.append(rect(40, 60, 440, 395, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(260, 88, "Кількісне вікно (Count-based, N=10)", size=13, bold=True, color=INK))

    # Комірки кільцевого буфера
    cell_w, cell_h = 34, 40
    start_x, start_y = 60, 120
    labels = ["OK", "OK", "ERR", "OK", "OK", "ERR", "ERR", "OK", "OK", "OK"]
    colors = [FIELD, FIELD, POS, FIELD, FIELD, POS, POS, FIELD, FIELD, FIELD]
    bg_colors = ["#f0fdf4", "#f0fdf4", "#fef2f2", "#f0fdf4", "#f0fdf4", "#fef2f2", "#fef2f2", "#f0fdf4", "#f0fdf4", "#f0fdf4"]

    for i in range(10):
        cx = start_x + i * 38
        frags.append(rect(cx, start_y, cell_w, cell_h, fill=bg_colors[i], stroke=colors[i], sw=1.5, rx=4))
        frags.append(text(cx + cell_w/2, start_y + 24, labels[i], size=10, bold=True, color=colors[i]))
        frags.append(text(cx + cell_w/2, start_y + 55, "[%d]" % i, size=9, color=MUTED))

    # Вказівник голови запису
    frags.append(arrow(260, 205, 260, 175, color=POS, sw=2))
    frags.append(text(260, 222, "Поточний індекс запису (head % 10)", size=10, bold=True, color=POS))

    # Агреговані лічильники
    frags.append(rect(60, 245, 395, 190, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    frags.append(text(260, 270, "Атомарні агрегати у вікні:", size=11, bold=True, color=INK))
    frags.append(text(80, 298, "• Загальна кількість запитів (total): 10", size=11, color=INK, anchor="start"))
    frags.append(text(80, 323, "• Успішні виклики (success): 7", size=11, color=FIELD, anchor="start"))
    frags.append(text(80, 348, "• Збійні виклики (failed): 3", size=11, color=POS, anchor="start"))
    frags.append(text(80, 378, "• Відсоток помилок: 3 / 10 = 30.0%", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(80, 400, "  (Поріг 50% не перевищено -> CLOSED)", size=10, color=FIELD, anchor="start"))


    # Панель 2: Часове вікно (Time-based Window з бакетами)
    frags.append(rect(520, 60, 440, 395, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(740, 88, "Часове вікно (Time-based: 10 бакетів по 1 с)", size=13, bold=True, color=INK))

    # 10 часових бакетів
    for i in range(10):
        cx = 540 + i * 38
        frags.append(rect(cx, start_y, cell_w, cell_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(cx + cell_w/2, start_y + 18, "B%d" % i, size=10, bold=True, color=INK))
        frags.append(text(cx + cell_w/2, start_y + 32, "1с", size=9, color=MUTED))
        frags.append(text(cx + cell_w/2, start_y + 55, "t-%d" % (9-i), size=9, color=MUTED))

    # Активний кошик
    frags.append(rect(540 + 9 * 38, start_y, cell_w, cell_h, fill="#eff6ff", stroke="#2563eb", sw=2, rx=4))
    frags.append(text(540 + 9 * 38 + cell_w/2, start_y + 18, "B9", size=10, bold=True, color="#2563eb"))
    frags.append(text(540 + 9 * 38 + cell_w/2, start_y + 32, "1с", size=9, color="#2563eb"))

    # Вказівник поточного часу
    frags.append(arrow(880, 205, 880, 175, color="#2563eb", sw=2))
    frags.append(text(800, 222, "Поточний секундний кошик", size=10, bold=True, color="#2563eb"))

    # Структура бакета
    frags.append(rect(540, 245, 395, 190, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    frags.append(text(740, 270, "Вміст кожного часового бакета:", size=11, bold=True, color=INK))
    frags.append(text(560, 298, "• `total_calls`: сума запитів за секунду", size=11, color=INK, anchor="start"))
    frags.append(text(560, 323, "• `failed_calls`: кількість помилок 5xx / таймаутів", size=11, color=POS, anchor="start"))
    frags.append(text(560, 348, "• `slow_calls`: виклики довші за поріг затримки", size=11, color="#d97706", anchor="start"))
    frags.append(text(560, 378, "Зсув часу: застарілий бакет скидається в 0", size=10, color=MUTED, anchor="start"))
    frags.append(text(560, 400, "Сума по 10 бакетах = ковзний зріз за 10 с", size=10, bold=True, color=INK, anchor="start"))

    return render(os.path.join(IMG, 'sliding-window-ring-buffer.svg'), W, H, *frags)


# ── Фігура 3: Захист від каскадного колапсу ─────────────────────────────────
def fig_cascading_failure_protection():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 28, "Захист від каскадного колапсу: прямий виклик проти захисту запобіжником", size=16, bold=True))

    # Ліва половина: БЕЗ запобіжника (Каскадна смерть потоків)
    frags.append(rect(40, 60, 440, 430, fill="#fffafb", stroke=POS, sw=1.5, rx=8))
    frags.append(text(260, 90, "Без запобіжника (Прямі виклики)", size=13, bold=True, color=POS))

    # Вузол 1: API Gateway
    frags.append(rect(70, 120, 160, 70, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(150, 145, "API Gateway", size=11, bold=True, color=INK))
    frags.append(text(150, 165, "Черга: 200/200", size=10, color=POS))
    frags.append(text(150, 180, "Потоки: 100% зайняті", size=9, bold=True, color=POS))

    # Вузол 2: Сервіс замовлень (Order Service)
    frags.append(rect(290, 120, 160, 70, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(370, 145, "Order Service", size=11, bold=True, color=INK))
    frags.append(text(370, 165, "Всі воркери чекають", size=10, color=POS))
    frags.append(text(370, 180, "Socket read timeout", size=9, color=MUTED))

    # Вузол 3: Збійний сервіс платежів (Payment Service)
    frags.append(rect(180, 250, 170, 70, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(text(265, 275, "Payment Service", size=11, bold=True, color=POS))
    frags.append(text(265, 295, "GC Pause / Deadlock", size=10, bold=True, color=POS))
    frags.append(text(265, 310, "Затримка: 15 мс -> 10 с", size=9, color=POS))

    # Стрілки застрягання
    frags.append(arrow(150, 190, 220, 250, color=POS, sw=2))
    frags.append(arrow(370, 190, 310, 250, color=POS, sw=2))

    frags.append(rect(60, 360, 400, 110, fill="#ffffff", stroke=POS, sw=1, rx=6))
    frags.append(text(260, 385, "Каскадний крах інфраструктури:", size=11, bold=True, color=POS))
    frags.append(text(80, 410, "1. Збійний сервіс утримує TCP-з'єднання", size=10, color=INK, anchor="start"))
    frags.append(text(80, 430, "2. Пули потоків вищих сервісів вичерпуються", size=10, color=INK, anchor="start"))
    frags.append(text(80, 450, "3. Падає весь користувацький інтерфейс і API", size=10, bold=True, color=POS, anchor="start"))


    # Права половина: ІЗ запобіжником (Fail-Fast + Fallback)
    frags.append(rect(520, 60, 440, 430, fill="#fbfdfb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(740, 90, "Із запобіжником (Fail-Fast Ізоляція)", size=13, bold=True, color=FIELD))

    # Вузол 1: API Gateway
    frags.append(rect(550, 120, 160, 70, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(630, 145, "API Gateway", size=11, bold=True, color=INK))
    frags.append(text(630, 165, "Черга: 5/200 (вільна)", size=10, color=FIELD))
    frags.append(text(630, 180, "CPU / Threads у нормі", size=9, bold=True, color=FIELD))

    # Вузол 2: Order Service + Circuit Breaker
    frags.append(rect(760, 120, 170, 70, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(845, 140, "Order Service", size=11, bold=True, color=INK))
    frags.append(rect(775, 155, 140, 24, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    frags.append(text(845, 171, "[ Breaker: OPEN ]", size=10, bold=True, color=POS))

    # Вузол 3: Збійний сервіс платежів (Payment Service)
    frags.append(rect(650, 250, 170, 70, fill="#fef2f2", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(735, 275, "Payment Service", size=11, bold=True, color=MUTED))
    frags.append(text(735, 295, "Ізольований від потоку", size=10, color=MUTED))
    frags.append(text(735, 310, "0 RPS навантаження", size=9, color=MUTED))

    # Стрілка Fail-Fast та Fallback
    frags.append(line(845, 190, 845, 240, color=POS, sw=2))
    frags.append(arrow(845, 240, 890, 240, color=POS, sw=2))
    frags.append(text(875, 230, "Fail-Fast", size=9, bold=True, color=POS))

    frags.append(rect(855, 250, 85, 45, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(897, 270, "Fallback", size=10, bold=True, color=FIELD))
    frags.append(text(897, 285, "Кеш / Стаб", size=9, color=MUTED))

    frags.append(rect(540, 360, 400, 110, fill="#ffffff", stroke=FIELD, sw=1, rx=6))
    frags.append(text(740, 385, "Стійкість та локалізація збою:", size=11, bold=True, color=FIELD))
    frags.append(text(560, 410, "1. Запобіжник розмикає ланцюг за 1 мкс без I/O", size=10, color=INK, anchor="start"))
    frags.append(text(560, 430, "2. Потоки звільняються негайно для інших клієнтів", size=10, color=INK, anchor="start"))
    frags.append(text(560, 450, "3. Збійний сервіс отримує час на спокійне відновлення", size=10, bold=True, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'cascading-failure-protection.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_circuit_breaker_state_machine()
    fig_sliding_window_ring_buffer()
    fig_cascading_failure_protection()
    print("Figures generated successfully.")
