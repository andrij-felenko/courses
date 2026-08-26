# -*- coding: utf-8 -*-
"""Фігури до статті «Виклик проти повідомлення: RPC»
(root/course/embedded/vyklyk-proty-povidomlennia).
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Порівняння парадигм: Синхронний RPC проти Асинхронної черги подій ─────
def fig_rpc_vs_event_queue():
    W, H = 940, 520
    f = []

    f.append(text(W / 2, 28, "Порівняння парадигм: Синхронний RPC проти Черги повідомлень",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "використання потоків RTOS, блокування стека та розподіл часу під час віддаленої взаємодії",
                  12, MUTED, "middle", italic=True))

    # Ліва колонка: Синхронний RPC
    lx, ly = 40, 80
    lw, lh = 410, 380
    f.append(rect(lx, ly, lw, lh, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 28, "Синхронний RPC (Request-Response)", 14, POS, "middle", bold=True))
    f.append(text(lx + lw / 2, ly + 46, "Ілюзія локальної функції: int res = read_sensor();", 11, MUTED, "middle", italic=True))

    # Ліва часова діаграма
    # Потік клієнта
    f.append(rect(lx + 25, ly + 70, 100, 32, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    f.append(text(lx + 75, ly + 90, "Потік клієнта", 11, INK, "middle", bold=True))

    # Лінія життя клієнта
    f.append(line(lx + 75, ly + 102, lx + 75, ly + 330, color=POS, sw=1.5))
    # Блокування
    f.append(rect(lx + 67, ly + 130, 16, 140, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    f.append(text(lx + 60, ly + 195, "Блокування RTOS", 10.5, POS, "end", bold=True))
    f.append(text(lx + 60, ly + 210, "(xSemaphoreTake)", 9.5, MUTED, "end"))

    # Потік сервера
    f.append(rect(lx + lw - 125, ly + 70, 100, 32, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    f.append(text(lx + lw - 75, ly + 90, "Серверний вузол", 11, INK, "middle", bold=True))
    f.append(line(lx + lw - 75, ly + 102, lx + lw - 75, ly + 330, color=POS, sw=1.5))

    # Стрілка запиту
    f.append(arrow(lx + 75, ly + 130, lx + lw - 75, ly + 170, color=POS, sw=1.6))
    f.append(text(lx + lw / 2, ly + 142, "Маршалінг + TX запиту", 10, POS, "middle", bold=True))

    # Обробка на сервері
    f.append(rect(lx + lw - 83, ly + 170, 16, 60, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    f.append(text(lx + lw - 55, ly + 205, "Обробка", 10, INK, "start"))

    # Стрілка відповіді
    f.append(arrow(lx + lw - 75, ly + 230, lx + 75, ly + 270, color=POS, sw=1.6))
    f.append(text(lx + lw / 2, ly + 242, "RX відповіді + розпакування", 10, POS, "middle", bold=True))

    # Підсумок ліворуч
    f.append(text(lx + lw / 2, ly + 348, "Стек задачі утримується весь RTT (10–200 мс)", 11, POS, "middle", bold=True))
    f.append(text(lx + lw / 2, ly + 365, "Втрата пакету блокує потік до таймауту", 10.5, MUTED, "middle"))

    # Права колонка: Черга повідомлень
    rx, ry = 490, 80
    rw, rh = 410, 380
    f.append(rect(rx, ry, rw, rh, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 28, "Черга повідомлень (Event-Driven / Actor)", 14, FIELD, "middle", bold=True))
    f.append(text(rx + rw / 2, ry + 46, "Асинхронний поділ: post_msg(EVT_REQ, id);", 11, MUTED, "middle", italic=True))

    # Права часова діаграма
    f.append(rect(rx + 25, ry + 70, 100, 32, fill="#eefaf2", stroke=FIELD, sw=1.2, rx=5))
    f.append(text(rx + 75, ry + 90, "Задача-сенсор", 11, INK, "middle", bold=True))
    f.append(line(rx + 75, ry + 102, rx + 75, ry + 330, color=FIELD, sw=1.5))

    f.append(rect(rx + rw - 125, ry + 70, 100, 32, fill="#eefaf2", stroke=FIELD, sw=1.2, rx=5))
    f.append(text(rx + rw - 75, ry + 90, "Шина / Диспетчер", 11, INK, "middle", bold=True))
    f.append(line(rx + rw - 75, ry + 102, rx + rw - 75, ry + 330, color=FIELD, sw=1.5))

    # Стрілка публікації
    f.append(arrow(rx + 75, ry + 125, rx + rw - 75, ry + 140, color=FIELD, sw=1.6))
    f.append(text(rx + rw / 2, ry + 122, "Push у чергу (2 мкс)", 10, FIELD, "middle", bold=True))

    # Робота продовжується
    f.append(rect(rx + 67, ry + 145, 16, 120, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(rx + 60, ry + 195, "Потік працює далі!", 10.5, FIELD, "end", bold=True))
    f.append(text(rx + 60, ry + 210, "Керує мотором/LED", 9.5, MUTED, "end"))

    # Асинхронна зворотна подія
    f.append(arrow(rx + rw - 75, ry + 270, rx + 75, ry + 295, color=FIELD, sw=1.6))
    f.append(text(rx + rw / 2, ry + 275, "Вхідна подія EVT_DATA", 10, FIELD, "middle", bold=True))

    # Підсумок праворуч
    f.append(text(rx + rw / 2, ry + 348, "Нульове блокування: 1 потік на всю систему", 11, FIELD, "middle", bold=True))
    f.append(text(rx + rw / 2, ry + 365, "Стійкість до будь-яких затримок середовища", 10.5, MUTED, "middle"))

    # Нижній загальний висновок
    f.append(line(50, H - 35, W - 50, H - 35, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 14,
                  "RPC прив'язує час життя локального потоку до надійності віддаленої мережі; черга подій розриває цей зв'язок.",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "rpc-vs-event-queue.svg"), W, H, *f)


# ── 2. Пастки RPC: взаємне блокування (Deadlock) та вичерпання пулу потоків ─
def fig_rpc_failure_modes():
    W, H = 920, 480
    f = []

    f.append(text(W / 2, 28, "Пастки RPC у вбудованих системах: Deadlock та деградація пулу потоків",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "чому синхронний виклик у повільних та нестабільних каналах призводить до системного колапсу",
                  12, MUTED, "middle", italic=True))

    # Ліва частина: Взаємне блокування (Deadlock)
    lx, ly = 40, 80
    lw, lh = 400, 345
    f.append(rect(lx, ly, lw, lh, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 26, "1. Циклічний Deadlock між вузлами", 13.5, POS, "middle", bold=True))

    # Вузол А і Вузол Б
    f.append(rect(lx + 30, ly + 65, 130, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(lx + 95, ly + 90, "Вузол А (MCU 1)", 12, INK, "middle", bold=True))
    f.append(text(lx + 95, ly + 110, "Потік 1: RPC call B", 10.5, POS, "middle"))
    f.append(text(lx + 95, ly + 128, "[Очікує Вузол Б...]", 10, MUTED, "middle"))

    f.append(rect(lx + lw - 160, ly + 65, 130, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(lx + lw - 95, ly + 90, "Вузол Б (MCU 2)", 12, INK, "middle", bold=True))
    f.append(text(lx + lw - 95, ly + 110, "Потік 2: RPC call A", 10.5, POS, "middle"))
    f.append(text(lx + lw - 95, ly + 128, "[Очікує Вузол А...]", 10, MUTED, "middle"))

    # Стрілки взаємного очікування
    f.append(arrow(lx + 160, ly + 90, lx + lw - 160, ly + 90, color=POS, sw=1.8))
    f.append(text(lx + lw / 2, ly + 80, "RPC Req (A → B)", 10, POS, "middle", bold=True))

    f.append(arrow(lx + lw - 160, ly + 125, lx + 160, ly + 125, color=POS, sw=1.8))
    f.append(text(lx + lw / 2, ly + 143, "RPC Req (B → A)", 10, POS, "middle", bold=True))

    # Пояснення глухого кута
    f.append(rect(lx + 20, ly + 175, lw - 40, 145, fill="#fee2e2", stroke=POS, sw=1.0, rx=6))
    f.append(text(lx + lw / 2, ly + 200, "Механізм глухого кута:", 11.5, POS, "middle", bold=True))
    f.append(text(lx + lw / 2, ly + 225, "• Вузол А заблокував свій єдиний робочий потік", 10.5, INK, "middle"))
    f.append(text(lx + lw / 2, ly + 245, "• Вузол Б не може відповісти, бо викликає А", 10.5, INK, "middle"))
    f.append(text(lx + lw / 2, ly + 265, "• Серверні обробники не мають вільних потоків", 10.5, INK, "middle"))
    f.append(text(lx + lw / 2, ly + 295, "Обидва мікроконтролери зависають назавжди!", 11, POS, "middle", bold=True))

    # Права частина: Вичерпання пулу потоків RTOS
    rx, ry = 480, 80
    rw, rh = 400, 345
    f.append(rect(rx, ry, rw, rh, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 26, "2. Вичерпання пулу задач RTOS", 13.5, POS, "middle", bold=True))

    # Пул задач
    ty_start = ry + 60
    tasks = [
        ("Task 1 (Sensor RPC)", "BLOCKED (чекає радіопакет)", POS),
        ("Task 2 (Config RPC)", "BLOCKED (чекає радіопакет)", POS),
        ("Task 3 (Cloud RPC)", "BLOCKED (чекає радіопакет)", POS),
        ("Task 4 (Motor Loop)", "STARVED (черга переповнена)", "#991b1b"),
    ]
    for i, (t_name, t_stat, col) in enumerate(tasks):
        y_pos = ty_start + i * 44
        f.append(rect(rx + 25, y_pos, rw - 50, 36, fill="#ffffff", stroke=col, sw=1.2, rx=5))
        f.append(text(rx + 38, y_pos + 22, t_name, 11, INK, "start", bold=True))
        f.append(text(rx + rw - 38, y_pos + 22, t_stat, 10, col, "end", bold=True))

    # Пояснення каскаду
    f.append(rect(rx + 20, ry + 250, rw - 40, 70, fill="#fee2e2", stroke=POS, sw=1.0, rx=6))
    f.append(text(rx + rw / 2, ry + 272, "Каскадна відмова:", 11.5, POS, "middle", bold=True))
    f.append(text(rx + rw / 2, ry + 295, "Затримка радіоканалу заморожує критичні задачі керування", 10.5, INK, "middle"))

    # Нижній висновок
    f.append(line(50, H - 35, W - 50, H - 35, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 14,
                  "У ненадійних радіоканалах синхронний RPC перетворює випадкові втрати зв'язку на системний Deadlock.",
                  11.5, POS, "middle", bold=True))

    render(os.path.join(IMG, "rpc-failure-modes.svg"), W, H, *f)


# ── 3. Гібридний патерн: Асинхронний корелятор запит-відповідь ───────────────
def fig_hybrid_async_correlator():
    W, H = 940, 500
    f = []

    f.append(text(W / 2, 28, "Гібридна архітектура: Асинхронний корелятор запитів і відповідей",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "зв'язування віддалених операцій через унікальні Correlation ID без блокування потоків RTOS",
                  12, MUTED, "middle", italic=True))

    # 1. Прикладний шар (зліва)
    ax, ay = 40, 90
    aw, ah = 230, 340
    f.append(rect(ax, ay, aw, ah, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(ax + aw / 2, ay + 26, "Прикладна логіка", 13, INK, "middle", bold=True))
    f.append(text(ax + aw / 2, ay + 44, "Non-blocking API", 11, MUTED, "middle", italic=True))

    f.append(rect(ax + 15, ay + 65, aw - 30, 65, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    f.append(text(ax + aw / 2, ay + 88, "async_request()", 11, INK, "middle", bold=True))
    f.append(text(ax + aw / 2, ay + 108, "Виділяє Trans ID = 42", 10, FIELD, "middle"))

    f.append(rect(ax + 15, ay + 150, aw - 30, 80, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    f.append(text(ax + aw / 2, ay + 172, "Future / Callback", 11, INK, "middle", bold=True))
    f.append(text(ax + aw / 2, ay + 194, "Опитування: is_ready()", 10, MUTED, "middle"))
    f.append(text(ax + aw / 2, ay + 212, "або callback(result)", 10, MUTED, "middle"))

    f.append(rect(ax + 15, ay + 250, aw - 30, 60, fill="#eefaf2", stroke=FIELD, sw=1.2, rx=5))
    f.append(text(ax + aw / 2, ay + 275, "Потік ВІЛЬНИЙ", 11.5, FIELD, "middle", bold=True))
    f.append(text(ax + aw / 2, ay + 295, "виконує іншу роботу", 10, MUTED, "middle"))

    # 2. Таблиця кореляції (посередині)
    cx, cy = 310, 90
    cw, ch = 320, 340
    f.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(cx + cw / 2, cy + 26, "Таблиця очікування транзакцій", 13, FIELD, "middle", bold=True))
    f.append(text(cx + cw / 2, cy + 44, "Статичний масив слотів (Zero-Alloc)", 11, MUTED, "middle", italic=True))

    # Слоти
    slots = [
        ("Slot [0]: ID=42 | State=PENDING | Timeout=150ms", FIELD, "#eefaf2"),
        ("Slot [1]: ID=43 | State=PENDING | Timeout=420ms", FIELD, "#eefaf2"),
        ("Slot [2]: ID=-- | State=FREE", MUTED, "#ffffff"),
        ("Slot [3]: ID=-- | State=FREE", MUTED, "#ffffff"),
    ]
    for i, (sl_text, s_col, s_bg) in enumerate(slots):
        sy = cy + 65 + i * 44
        f.append(rect(cx + 15, sy, cw - 30, 34, fill=s_bg, stroke=s_col, sw=1.1, rx=4))
        f.append(text(cx + 25, sy + 21, sl_text, 10, s_col, "start", bold=(i < 2)))

    # Таймер таймаутів
    f.append(rect(cx + 15, cy + 255, cw - 30, 65, fill="#fffaf9", stroke=POS, sw=1.1, rx=5))
    f.append(text(cx + cw / 2, cy + 278, "Сторож таймаутів (10 Гц)", 11, POS, "middle", bold=True))
    f.append(text(cx + cw / 2, cy + 300, "Сплив час → onError(TIMEOUT)", 10, MUTED, "middle"))

    # 3. Транспорт і віддалений вузол (справа)
    tx, ty = 670, 90
    tw, th = 230, 340
    f.append(rect(tx, ty, tw, th, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(tx + tw / 2, ty + 26, "Асинхронний транспорт", 13, INK, "middle", bold=True))
    f.append(text(tx + tw / 2, ty + 44, "UART / CAN / Радіо", 11, MUTED, "middle", italic=True))

    f.append(rect(tx + 15, ty + 65, tw - 30, 60, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    f.append(text(tx + tw / 2, ty + 88, "TX Frame", 11, INK, "middle", bold=True))
    f.append(text(tx + tw / 2, ty + 108, "[ID=42, CMD, DATA]", 10, POS, "middle"))

    f.append(rect(tx + 15, ty + 150, tw - 30, 60, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    f.append(text(tx + tw / 2, ty + 173, "Віддалений вузол", 11, INK, "middle", bold=True))
    f.append(text(tx + tw / 2, ty + 193, "Обробляє у фоні", 10, MUTED, "middle"))

    f.append(rect(tx + 15, ty + 235, tw - 30, 60, fill="#ffffff", stroke=LINE, sw=1.1, rx=5))
    f.append(text(tx + tw / 2, ty + 258, "RX Frame", 11, INK, "middle", bold=True))
    f.append(text(tx + tw / 2, ty + 278, "[ID=42, RSP, RESULT]", 10, FIELD, "middle"))

    # Зв'язки між шарами
    # Реєстрація в кореляторі
    f.append(arrow(ax + aw, ay + 95, cx, ay + 95, color=FIELD, sw=1.6))
    # Відправка в транспорт
    f.append(arrow(cx + cw, cy + 95, tx, ty + 95, color=POS, sw=1.6))
    # Прийом відповіді
    f.append(arrow(tx, ty + 265, cx + cw, cy + 265, color=FIELD, sw=1.6))
    # Сповіщення застосунку
    f.append(arrow(cx, cy + 265, ax + aw, ay + 190, color=FIELD, sw=1.6))

    # Нижній висновок
    f.append(line(50, H - 35, W - 50, H - 35, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 14,
                  "Гібридна модель: семантика запит-відповідь для програміста, але повністю асинхронна шина без зависань потоків.",
                  11.5, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "hybrid-async-correlator.svg"), W, H, *f)


if __name__ == "__main__":
    fig_rpc_vs_event_queue()
    fig_rpc_failure_modes()
    fig_hybrid_async_correlator()
    print("All figures generated successfully.")
