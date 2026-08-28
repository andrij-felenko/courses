# -*- coding: utf-8 -*-
"""Генератор архітектурних діаграм для теми asyncio-event-loop."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, text, mtext, line, arrow, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_event_loop_architecture():
    """Діаграма 1: Архітектура циклу подій asyncio та фази виконання _run_once()."""
    w, h = 860, 520
    frags = []

    frags.append(text(430, 26, "Архітектура циклу подій asyncio та цикл ітерації _run_once()", size=15, bold=True))

    # Контейнер 1: Черга таймерів (_scheduled)
    frags.append(rect(30, 55, 250, 185, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(155, 78, "Черга таймерів (_scheduled)", size=12, bold=True, color=NEG))
    frags.append(fitbox(45, 95, 220, 130, "Бінарна мін-купа (heapq)\n• Об'єкти TimerHandle\n• Впорядковані за міткою when\n• loop.call_later() / call_at()\n• Вершина: найближчий дедлайн", size=11, fill="#eef2ff", stroke=NEG))

    # Контейнер 2: Черга готових задач (_ready)
    frags.append(rect(580, 55, 250, 185, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(705, 78, "Черга готових дій (_ready)", size=12, bold=True, color=FIELD))
    frags.append(fitbox(595, 95, 220, 130, "Двобічна черга (collections.deque)\n• Об'єкти Handle\n• loop.call_soon() / Task._step\n• Колбеки I/O та готові таймери\n• FIFO виконання без затримок", size=11, fill="#f0fdf4", stroke=FIELD))

    # Центральний блок: Селектор ОС та опитування
    frags.append(rect(300, 55, 260, 185, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 78, "Селектор системних подій", size=12, bold=True, color=POS))
    frags.append(fitbox(315, 95, 230, 130, "selectors.DefaultSelector\n• epoll (Linux) / kqueue (macOS)\n• IOCP (Windows Proactor)\n• Розрахунок таймауту:\ntimeout = min(when - now, max)\n• selector.select(timeout)", size=11, fill="#fef2f2", stroke=POS))

    # Нижній блок: Диспетчеризація та виконання обробників
    frags.append(rect(30, 275, 800, 215, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 298, "Послідовність виконання однієї ітерації: BaseEventLoop._run_once()", size=13, bold=True, color=INK))

    frags.append(fitbox(45, 315, 175, 155, "Крок 1: Оцінка часу\n\n• Перевірка вершини купи\n  _scheduled[0].when\n• Якщо _ready не порожня,\n  timeout = 0\n• Інакше timeout = time_to_next", size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(240, 315, 175, 155, "Крок 2: Селектор\n\n• Виклик ОС select(timeout)\n• Отримання подій сокетів\n• Перетворення подій\n  (EVENT_READ/WRITE)\n  на виклики колбеків", size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(435, 315, 180, 155, "Крок 3: Перенесення\n\n• Зсув дозрілих таймерів\n  з _scheduled у _ready\n• Додавання сокетних\n  обробників у кінець _ready\n• Скасовані Handle фільтруються", size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(635, 315, 180, 155, "Крок 4: Виконання пачки\n\n• ntasks = len(_ready)\n• Вилучення ntasks елементів\n• Виконання handle._run()\n• Вивільнення контексту для\n  наступного циклу", size=10, fill="#ffffff", stroke=LINE))

    # Стрілки між кроками
    frags.append(arrow(220, 392, 240, 392, color=LINE, sw=1.5))
    frags.append(arrow(415, 392, 435, 392, color=LINE, sw=1.5))
    frags.append(arrow(615, 392, 635, 392, color=LINE, sw=1.5))

    # Стрілки з верхніх блоків до нижніх кроків
    frags.append(arrow(155, 240, 132, 315, color=NEG, sw=1.5))
    frags.append(arrow(430, 240, 327, 315, color=POS, sw=1.5))
    frags.append(arrow(705, 240, 725, 315, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "event-loop-architecture.svg"), w, h, *frags)


def fig_coroutine_task_future():
    """Діаграма 2: Життєвий цикл корутини, обгортки Task та примітива Future."""
    w, h = 860, 480
    frags = []

    frags.append(text(430, 26, "Взаємодія Coroutine, Task та Future у потоці керування", size=15, bold=True))

    # Колонка 1: Корутина (async def)
    frags.append(rect(30, 55, 245, 395, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(152, 80, "Coroutine (PyCoroObject)", size=12, bold=True, color=NEG))
    frags.append(fitbox(45, 100, 215, 80, "Генераторний фрейм CPython\n• Локальні змінні та стек\n• Поточний байткод-офсет\n• Інструкція await виклику", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(45, 195, 215, 105, "Стани корутини:\n• CORO_CREATED (створена)\n• CORO_RUNNING (виконується)\n• CORO_SUSPENDED (призупинена)\n• CORO_CLOSED (завершена)", size=10, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(45, 315, 215, 115, "Інструкція await:\n1. Отримує об'єкт-awaitable\n2. Викликає __await__()\n3. Зупиняється через YIELD_VALUE\n4. Повертає очікуваний Future", size=10, fill="#eef2ff", stroke=NEG))

    # Колонка 2: asyncio.Task
    frags.append(rect(305, 55, 250, 395, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 80, "asyncio.Task (Керівний рушій)", size=12, bold=True, color=FIELD))
    frags.append(fitbox(320, 100, 220, 80, "Обгортка корутини\n• Успадковує asyncio.Future\n• Зберігає посилання на _coro\n• Зареєстрована в Task.all_tasks()", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(320, 195, 220, 120, "Метод Task._step(val):\n1. coro.send(val) відновлює код\n2. Якщо корутина повернула значення:\n   set_result() завершує Task\n3. Якщо yield-нула Future:\n   fut.add_done_callback(_wakeup)", size=10, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(320, 330, 220, 100, "Метод Task._wakeup(fut):\n• Отримує результат fut.result()\n• loop.call_soon(self._step, res)\n• Планує наступне просування", size=10, fill="#f0fdf4", stroke=FIELD))

    # Колонка 3: asyncio.Future
    frags.append(rect(585, 55, 245, 395, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(707, 80, "asyncio.Future (Контейнер результату)", size=12, bold=True, color=POS))
    frags.append(fitbox(600, 100, 215, 80, "Низькорівневий примітив\n• _state: PENDING / CANCELLED / FINISHED\n• _result: збережене значення\n• _exception: збережений виняток", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(600, 195, 215, 110, "Зворотні виклики (_callbacks):\n• Список функцій для сповіщення\n• fut.add_done_callback(cb)\n• Під час завершення циклічно\n  викликає loop.call_soon(cb, fut)", size=10, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(600, 320, 215, 110, "Завершення події I/O:\n• Селектор фіксує готовність сокета\n• fut.set_result(data)\n• Стан переходить у FINISHED\n• Спрацьовує Task._wakeup()", size=10, fill="#fef2f2", stroke=POS))

    # Зв'язуючі стрілки
    frags.append(arrow(320, 245, 260, 245, color=LINE, sw=1.5))
    frags.append(arrow(260, 365, 320, 365, color=LINE, sw=1.5))
    frags.append(arrow(540, 255, 600, 255, color=LINE, sw=1.5))
    frags.append(arrow(600, 375, 540, 375, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "coroutine-task-future.svg"), w, h, *frags)


def fig_async_streams_backpressure():
    """Діаграма 3: Потоковий I/O, буферизація та зворотний тиск (Backpressure)."""
    w, h = 860, 460
    frags = []

    frags.append(text(430, 26, "Асинхронний мережевий I/O та механізм зворотного тиску (Backpressure)", size=15, bold=True))

    # Рівень 1: Корутина застосунку
    frags.append(rect(30, 55, 800, 75, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(160, 78, "Корутина застосунку (Writer)", size=12, bold=True, color=NEG))
    frags.append(fitbox(280, 68, 250, 50, "writer.write(chunk)\n(Неблокувальний запис у буфер)", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(560, 68, 250, 50, "await writer.drain()\n(Очікування звільнення буфера)", size=11, fill="#eef2ff", stroke=NEG))

    # Рівень 2: StreamWriter / Transport буфер
    frags.append(rect(30, 150, 800, 160, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 172, "Внутрішній буфер передачі (asyncio.Transport)", size=12, bold=True, color=FIELD))

    # Індикатор водяних міток
    frags.append(rect(60, 195, 740, 35, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=4))
    frags.append(rect(60, 195, 480, 35, fill="#fed7aa", stroke=POS, sw=1.5, rx=4))
    frags.append(text(150, 217, "Дані в черзі сокета", size=11, bold=True, color=INK))

    # Водяні мітки
    frags.append(line(240, 185, 240, 240, color=FIELD, sw=2, dash="4,3"))
    frags.append(text(240, 255, "low_water (16 КБ)", size=10, bold=True, color=FIELD))

    frags.append(line(520, 185, 520, 240, color=POS, sw=2, dash="4,3"))
    frags.append(text(520, 255, "high_water (64 КБ)", size=10, bold=True, color=POS))

    frags.append(fitbox(60, 270, 740, 30, "Поточний розмір > high_water: protocol.pause_writing() переводить drain() в очікування PENDING", size=10, fill="#ffffff", stroke=MUTED))

    # Рівень 3: Ядро ОС та мережевий сокет
    frags.append(rect(30, 330, 800, 105, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(150, 355, "Ядро ОС (Системні виклики)", size=12, bold=True, color=POS))

    frags.append(fitbox(280, 350, 250, 65, "Системний сокетний буфер SO_SNDBUF\nВідправка пакетів через TCP стек\nв мережевий інтерфейс (NIC)", size=10, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(560, 350, 250, 65, "Звільнення буфера нижче low_water:\nprotocol.resume_writing()\nВстановлює результат waiter.set_result(None)\nКорутина виходить з await drain()", size=10, fill="#f0fdf4", stroke=FIELD))

    # Стрілки керування потоком
    frags.append(arrow(405, 118, 405, 150, color=LINE, sw=1.5))
    frags.append(arrow(405, 310, 405, 330, color=LINE, sw=1.5))
    frags.append(arrow(685, 350, 685, 118, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "async-streams-backpressure.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_event_loop_architecture()
    fig_coroutine_task_future()
    fig_async_streams_backpressure()
    print("All asyncio figures generated successfully.")


if __name__ == "__main__":
    main()
