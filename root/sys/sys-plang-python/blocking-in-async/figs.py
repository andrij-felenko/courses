# -*- coding: utf-8 -*-
"""Генератор архітектурних діаграм для теми blocking-in-async."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, text, mtext, line, arrow, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_blocking_timeline():
    """Діаграма 1: Порівняння нормальної диспетчеризації та блокування циклу подій."""
    w, h = 840, 460
    frags = []

    # Заголовок
    frags.append(text(420, 26, "Вплив блокувального виклику на диспетчеризацію задач у циклі подій", size=15, bold=True))

    # Секція 1: Нормальна кооперативна робота
    frags.append(rect(20, 50, 800, 180, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(220, 75, "Нормальна кооперативна диспетчеризація (Non-blocking I/O)", size=13, bold=True, color=FIELD))

    # Часова шкала 1
    frags.append(line(50, 150, 780, 150, color=LINE, sw=1.5))
    frags.append(arrow(770, 150, 790, 150, color=LINE, sw=1.5))
    frags.append(text(760, 170, "Час (t)", size=11, color=MUTED))

    # Блоки задач шкали 1
    frags.append(rect(60, 100, 130, 40, fill="#eef2ff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(125, 124, "Задача 1: I/O (await)", size=11, bold=True, color=NEG))

    frags.append(rect(220, 100, 140, 40, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(290, 124, "Задача 2: Таймер 50мс", size=11, bold=True, color=FIELD))

    frags.append(rect(390, 100, 150, 40, fill="#eef2ff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(465, 124, "Задача 3: TCP-запит", size=11, bold=True, color=NEG))

    frags.append(rect(570, 100, 130, 40, fill="#eef2ff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(635, 124, "Задача 1: Обробка", size=11, bold=True, color=NEG))

    # Позначки передачі керування
    frags.append(line(190, 100, 190, 150, color=FIELD, sw=1, dash="3,3"))
    frags.append(line(360, 100, 360, 150, color=FIELD, sw=1, dash="3,3"))
    frags.append(line(540, 100, 540, 150, color=FIELD, sw=1, dash="3,3"))
    frags.append(text(420, 205, "Кожна задача віддає керування через await -> нульова затримка інших задач", size=11, color=FIELD, bold=True))

    # Секція 2: Блокування
    frags.append(rect(20, 250, 800, 190, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(250, 275, "Блокування єдиного потоку циклу подій (Синхронний виклик)", size=13, bold=True, color=POS))

    # Часова шкала 2
    frags.append(line(50, 360, 780, 360, color=LINE, sw=1.5))
    frags.append(arrow(770, 360, 790, 360, color=LINE, sw=1.5))
    frags.append(text(760, 380, "Час (t)", size=11, color=MUTED))

    # Блокувальний виклик
    frags.append(rect(60, 305, 380, 45, fill="#fef2f2", stroke=POS, sw=2, rx=4))
    frags.append(text(250, 332, "Задача 1: time.sleep(200ms) або requests.get() [БЛОКУВАННЯ]", size=11, bold=True, color=POS))

    # Заблоковані задачі
    frags.append(rect(470, 305, 140, 45, fill="#fff1f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(540, 325, "Задача 2: Таймер", size=11, color=POS))
    frags.append(text(540, 342, "Затримка +150мс!", size=10, bold=True, color=POS))

    frags.append(rect(630, 305, 140, 45, fill="#fff1f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(700, 325, "Задача 3: TCP-пакет", size=11, color=POS))
    frags.append(text(700, 342, "Чекає в буфері ОС", size=10, bold=True, color=POS))

    # Позначка замороження
    frags.append(text(250, 385, "Потік ОС завис: селектор epoll не викликається, черга _ready заблокована", size=11, color=POS, italic=True))
    frags.append(text(420, 420, "Наслідок: колапс пропускної здатності та спайк затримок (latency spike) для всіх клієнтів", size=11, bold=True, color=POS))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, "event-loop-blocking-timeline.svg"), w, h, *frags)


def fig_executor_bridge():
    """Діаграма 2: Архітектура винесення коду у ThreadPoolExecutor та ProcessPoolExecutor."""
    w, h = 860, 470
    frags = []

    # Заголовок
    frags.append(text(430, 26, "Ізоляція блокувального коду: мости між asyncio та пулами виконання", size=15, bold=True))

    # Колонка 1: Event Loop
    frags.append(rect(20, 50, 260, 400, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(150, 75, "Головний потік (Event Loop)", size=13, bold=True, color=NEG))

    frags.append(fitbox(35, 95, 230, 65, "Цикл подій asyncio\n• epoll / kqueue / IOCP\n• Опитування дескрипторів", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(35, 175, 230, 80, "Асинхронна корутина\nres = await asyncio.to_thread(f)\nабо\nloop.run_in_executor(pool, f)", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(35, 270, 230, 60, "asyncio.Future\nОчікує результату\n(не блокуючи селектор)", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(35, 345, 230, 85, "Пробудження циклу\nloop.call_soon_threadsafe()\n→ запис 1 байта у self-pipe\n→ пробудження epoll.poll()", size=11, fill="#f0fdf4", stroke=FIELD))

    # Колонка 2: Пул потоків (ThreadPoolExecutor)
    frags.append(rect(310, 50, 250, 400, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(435, 75, "ThreadPoolExecutor", size=13, bold=True, color=FIELD))

    frags.append(fitbox(325, 95, 220, 75, "Призначення: I/O-bound\n• Дискові файли (open, write)\n• Синхронні БД (sqlite3)\n• C-бібліотеки без GIL", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(325, 185, 220, 70, "Пам'ять: Спільна купа\nСпільний адресний простір\nНульові витрати на копіювання", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(325, 270, 220, 75, "Обмеження CPython:\nБайткод Python виконується\nпід спільним GIL!\nНе для CPU-bound Python", size=11, fill="#fff1f2", stroke=POS))
    frags.append(fitbox(325, 360, 220, 70, "Повернення результату\nconcurrent.futures.Future\nВиклик зворотного колбека", size=11, fill="#f0fdf4", stroke=FIELD))

    # Колонка 3: Пул процесів (ProcessPoolExecutor)
    frags.append(rect(590, 50, 250, 400, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(715, 75, "ProcessPoolExecutor", size=13, bold=True, color=POS))

    frags.append(fitbox(605, 95, 220, 75, "Призначення: CPU-bound\n• Важка математика\n• Стиснення даних / криптографія\n• Парсинг великих JSON/XML", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(605, 185, 220, 70, "Пам'ять: Окремі процеси\nВласна купа та власний GIL\nПаралелізм на всіх ядрах CPU", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(605, 270, 220, 75, "Накладні витрати:\nСеріалізація через pickle\nIPC-канали (pipe/socket)\nВитрати на fork / spawn", size=11, fill="#fff1f2", stroke=POS))
    frags.append(fitbox(605, 360, 220, 70, "Передача результату\nДесеріалізація через IPC\nУстановка значення у Future", size=11, fill="#fef2f2", stroke=POS))

    # Зв'язки / стрілки
    frags.append(arrow(265, 215, 325, 130, color=LINE, sw=1.5))
    frags.append(arrow(265, 235, 605, 130, color=LINE, sw=1.5))
    frags.append(arrow(325, 395, 265, 390, color=FIELD, sw=1.5))
    frags.append(arrow(605, 395, 265, 410, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "thread-process-executor-bridge.svg"), w, h, *frags)


def fig_sync_async_queues():
    """Діаграма 3: Потокобезпечний міст між чергами asyncio.Queue та queue.Queue."""
    w, h = 840, 450
    frags = []

    # Заголовок
    frags.append(text(420, 26, "Потокобезпечний обмін даними між асинхронним та синхронним контекстами", size=15, bold=True))

    # Блок 1: Потік циклу подій
    frags.append(rect(20, 50, 380, 380, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(210, 75, "Асинхронний контекст (Event Loop)", size=13, bold=True, color=NEG))

    frags.append(fitbox(40, 95, 340, 60, "Асинхронні корутини\n(Мережеві сокети, WebSockets, HTTP-сервер)", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(40, 170, 340, 65, "asyncio.Queue (НЕ є thread-safe!)\n• await queue.get()\n• await queue.put(item)", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(40, 255, 340, 75, "Запис у синхронну чергу з корутини:\nawait asyncio.to_thread(sync_q.put, item)\n(виконується в пулі, не блокує цикл)", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(40, 345, 340, 65, "Прийом із потоку в асинхронну чергу:\nloop.call_soon_threadsafe(async_q.put_nowait, val)", size=11, fill="#f0fdf4", stroke=FIELD))

    # Блок 2: Синхронні робочі потоки
    frags.append(rect(440, 50, 380, 380, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(630, 75, "Синхронний контекст (Робочі потоки)", size=13, bold=True, color=FIELD))

    frags.append(fitbox(460, 95, 340, 60, "Синхронні Worker Threads\n(Дисковий запис, C-розрахунки, синхронні SDK)", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(460, 170, 340, 65, "queue.Queue (Потокобезпечна з блокуванням)\n• sync_q.get() [блокує потік до появи даних]\n• sync_q.put(item)", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(460, 255, 340, 75, "Заборонено в Event Loop:\nsync_q.get() без потоку -> зупинка циклу!\nasync_q.put() з потоку -> стан гонитви!", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(460, 345, 340, 65, "Передача завдання в корутину:\nasyncio.run_coroutine_threadsafe(coro, loop)", size=11, fill="#f0fdf4", stroke=FIELD))

    # Стрілки між блоками
    frags.append(arrow(380, 290, 460, 205, color=FIELD, sw=1.8))
    frags.append(arrow(460, 375, 380, 375, color=FIELD, sw=1.8))

    render(os.path.join(IMG_DIR, "sync-async-queues-bridge.svg"), w, h, *frags)


def main():
    fig_blocking_timeline()
    fig_executor_bridge()
    fig_sync_async_queues()
    print("Всі SVG успішно згенеровано.")


if __name__ == "__main__":
    main()
