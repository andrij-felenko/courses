# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Цикл подій (Event Loop)».
Використовує бібліотеку svgkit для створення чистих SVG без зовнішніх залежностей.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_thread_per_conn_vs_event_loop():
    """Діаграма 1: Порівняння моделі 'потік на з'єднання' та циклу подій."""
    W, H = 820, 360
    f = []

    # ── Ліва колонка: Модель «Один потік на клієнта» ──
    f.append(rect(15, 45, 385, 300, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(207, 72, "Модель «Один потік на з’єднання»", size=15, color=POS, bold=True))
    f.append(text(207, 92, "10 000 клієнтів → 10 000 потоків у ядрі ОС", size=12, color=MUTED))

    # Клієнти зліва
    f.append(rect(30, 115, 95, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(77, 138, "Клієнт 1", size=12, bold=True))

    f.append(rect(30, 165, 95, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(77, 188, "Клієнт 2", size=12, bold=True))

    f.append(text(77, 222, "⋮", size=18, color=MUTED, bold=True))

    f.append(rect(30, 240, 95, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(77, 263, "Клієнт N", size=12, bold=True))

    # Потоки ядра
    f.append(arrow(125, 133, 165, 133, color=LINE))
    f.append(rect(165, 115, 215, 36, fill="#ffffff", stroke=POS, sw=1))
    f.append(text(272, 131, "Потік 1: Стек 4 МБ (Спить у read)", size=11, color=POS))
    f.append(text(272, 144, "очікує пакет байтів", size=9, color=MUTED))

    f.append(arrow(125, 183, 165, 183, color=LINE))
    f.append(rect(165, 165, 215, 36, fill="#ffffff", stroke=POS, sw=1))
    f.append(text(272, 181, "Потік 2: Стек 4 МБ (Спить у read)", size=11, color=POS))
    f.append(text(272, 194, "очікує пакет байтів", size=9, color=MUTED))

    f.append(text(272, 222, "⋮", size=18, color=MUTED, bold=True))

    f.append(arrow(125, 258, 165, 258, color=LINE))
    f.append(rect(165, 240, 215, 36, fill="#ffffff", stroke=POS, sw=1))
    f.append(text(272, 256, "Потік N: Стек 4 МБ (Спить у read)", size=11, color=POS))
    f.append(text(272, 269, "очікує пакет байтів", size=9, color=MUTED))

    f.append(rect(30, 290, 350, 42, fill="#fdecea", stroke=POS, sw=1, rx=4))
    f.append(text(205, 307, "Пам’ять під стеки: ~40 ГБ RAM", size=11, color=POS, bold=True))
    f.append(text(205, 323, "Перемикання контексту спалює процесорні такти", size=10, color=POS))

    # ── Права колонка: Модель «Цикл подій» ──
    f.append(rect(420, 45, 385, 300, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(612, 72, "Модель «Цикл подій (Event Loop)»", size=15, color=FIELD, bold=True))
    f.append(text(612, 92, "10 000 неблокуючих сокетів → 1 потік виконання", size=12, color=MUTED))

    # Клієнти справа
    f.append(rect(435, 115, 85, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(477, 138, "Сокет 1", size=11, bold=True))

    f.append(rect(435, 165, 85, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(477, 188, "Сокет 2", size=11, bold=True))

    f.append(text(477, 222, "⋮", size=18, color=MUTED, bold=True))

    f.append(rect(435, 240, 85, 36, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(477, 263, "Сокет N", size=11, bold=True))

    # Демультиплексор ядра
    f.append(arrow(520, 133, 550, 160, color=LINE))
    f.append(arrow(520, 183, 550, 180, color=LINE))
    f.append(arrow(520, 258, 550, 200, color=LINE))

    f.append(rect(550, 135, 105, 95, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(602, 162, "epoll / kqueue", size=12, color=NEG, bold=True))
    f.append(text(602, 180, "Події ядра", size=11, color=NEG))
    f.append(text(602, 202, "готово: [1, N]", size=10, color=INK, bold=True))

    # Єдиний потік виконання (Event Loop)
    f.append(arrow(655, 182, 680, 182, color=LINE))
    f.append(rect(680, 115, 110, 135, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    f.append(text(735, 140, "Event Loop", size=13, color=FIELD, bold=True))
    f.append(text(735, 158, "1 потік", size=11, color=FIELD))
    f.append(line(690, 168, 780, 168, color="#e0e0e0"))
    f.append(text(735, 188, "Черга подій", size=10, color=INK))
    f.append(text(735, 204, "Обробник 1", size=10, color=INK))
    f.append(text(735, 220, "Обробник N", size=10, color=INK))
    f.append(text(735, 238, "Run-to-end", size=9, color=MUTED))

    f.append(rect(435, 290, 355, 42, fill="#e8f8f0", stroke=FIELD, sw=1, rx=4))
    f.append(text(612, 307, "Пам’ять під стек: 1 стек (~2-4 МБ разом)", size=11, color=FIELD, bold=True))
    f.append(text(612, 323, "Нуль перемикань контексту, чудове кешування", size=10, color=FIELD))

    render(os.path.join(IMG, "thread-per-conn-vs-event-loop.svg"), W, H, *f)


def fig_event_loop_phases():
    """Діаграма 2: Фази одного оберту (tick) циклу подій."""
    W, H = 820, 380
    f = []

    # Заголовок
    f.append(text(410, 30, "Анатомія одного оберту циклу подій", size=16, color=INK, bold=True))

    # Фаза 1: Таймери
    f.append(rect(290, 55, 240, 52, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(410, 78, "1. Таймери (Timers Heap)", size=13, color=NEG, bold=True))
    f.append(text(410, 96, "Виконати setTimeout / setInterval, що збігли", size=10, color=MUTED))

    # Стрілка 1 -> 2
    f.append(arrow(530, 81, 620, 130, color=LINE, sw=1.8))

    # Фаза 2: Очікування I/O
    f.append(rect(540, 135, 250, 70, fill="#f4faf6", stroke=FIELD, sw=2, rx=6))
    f.append(text(665, 160, "2. Опитування I/O (Poll / epoll_wait)", size=13, color=FIELD, bold=True))
    f.append(text(665, 178, "Сон до появи готових сокетів або", size=10, color=INK))
    f.append(text(665, 194, "до дедлайну найближчого таймера", size=10, color=INK, bold=True))

    # Стрілка 2 -> 3
    f.append(arrow(665, 205, 665, 250, color=LINE, sw=1.8))

    # Фаза 3: Обробники I/O
    f.append(rect(540, 250, 250, 52, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(665, 273, "3. Обробники I/O (Callbacks)", size=13, color=INK, bold=True))
    f.append(text(665, 291, "Виклик колбеків для прочитаних сокетів", size=10, color=MUTED))

    # Стрілка 3 -> 4
    f.append(arrow(540, 290, 480, 325, color=LINE, sw=1.8))

    # Фаза 4: Мікрозадачі
    f.append(rect(270, 315, 280, 52, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    f.append(text(410, 338, "4. Мікрозадачі (Microtasks / nextTick)", size=13, color=POS, bold=True))
    f.append(text(410, 356, "Спустошити чергу промісів до дна", size=10, color=POS))

    # Стрілка 4 -> 5
    f.append(arrow(270, 335, 190, 290, color=LINE, sw=1.8))

    # Фаза 5: Check / Immediate
    f.append(rect(30, 250, 240, 52, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(150, 273, "5. Check / setImmediate", size=13, color=INK, bold=True))
    f.append(text(150, 291, "Обслуговування сокетів після Poll", size=10, color=MUTED))

    # Стрілка 5 -> 6
    f.append(arrow(150, 250, 150, 205, color=LINE, sw=1.8))

    # Фаза 6: UI Render / Housekeeping
    f.append(rect(30, 135, 240, 70, fill="#fdf8e6", stroke="#d35400", sw=1.5, rx=6))
    f.append(text(150, 158, "6. UI Render / Housekeeping", size=13, color="#d35400", bold=True))
    f.append(text(150, 176, "Перемалювання кадрів (requestAnimationFrame),", size=10, color=INK))
    f.append(text(150, 192, "очищення закритих дескрипторів", size=10, color=MUTED))

    # Стрілка 6 -> 1
    f.append(arrow(190, 135, 290, 81, color=LINE, sw=1.8))

    # Центр: ядро циклу
    f.append(circle(410, 195, 55, fill="#f8f9fa", stroke=LINE, sw=1.5))
    f.append(text(410, 190, "Run-to-end", size=12, color=INK, bold=True))
    f.append(text(410, 208, "1 потік", size=11, color=MUTED))

    render(os.path.join(IMG, "event-loop-phases.svg"), W, H, *f)


def fig_timer_demux_coordination():
    """Діаграма 3: Узгодження таймерної мін-купи з таймаутом epoll_wait."""
    W, H = 820, 280
    f = []

    f.append(text(410, 26, "Як черга таймерів керує сном у epoll_wait", size=15, color=INK, bold=True))

    # Мін-купа таймерів зліва
    f.append(rect(20, 50, 250, 210, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(145, 75, "Мін-купа таймерів (Min-Heap)", size=13, color=NEG, bold=True))
    f.append(line(35, 85, 255, 85, color="#c5d8fb"))

    f.append(rect(35, 98, 220, 36, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(145, 116, "Найближчий: t = 1000.045 s", size=11, color=POS, bold=True))
    f.append(text(145, 127, "через 45 мс (вершина купи)", size=9, color=MUTED))

    f.append(rect(35, 142, 220, 30, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(145, 162, "t = 1000.120 s (+120 ms)", size=10, color=INK))

    f.append(rect(35, 180, 220, 30, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(145, 200, "t = 1001.500 s (+1500 ms)", size=10, color=INK))

    f.append(text(145, 240, "Поточний час: now = 1000.000 s", size=11, color=INK, bold=True))

    # Розрахунок таймауту посередині
    f.append(arrow(270, 116, 320, 116, color=LINE, sw=1.5))
    f.append(rect(320, 75, 190, 85, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(415, 98, "Обчислення таймауту:", size=11, color=MUTED))
    f.append(text(415, 118, "timeout = 1000.045 - now", size=11, color=INK, bold=True))
    f.append(text(415, 138, "timeout = 45 мс", size=13, color=POS, bold=True))

    # epoll_wait праворуч
    f.append(arrow(510, 116, 560, 116, color=LINE, sw=1.8))
    f.append(rect(560, 50, 240, 210, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(680, 75, "Системний виклик ядра", size=13, color=FIELD, bold=True))
    f.append(text(680, 95, "epoll_wait(epfd, evs, max, 45)", size=12, color=INK, bold=True))
    f.append(line(575, 108, 785, 108, color="#c8ebd8"))

    f.append(rect(575, 120, 210, 55, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    f.append(text(680, 138, "Сценарій А: Прийшов пакет сокета", size=10, color=FIELD, bold=True))
    f.append(text(680, 152, "Пробудження за 12 мс", size=10, color=INK))
    f.append(text(680, 166, "Обробляємо сокет, таймер чекає", size=9, color=MUTED))

    f.append(rect(575, 185, 210, 55, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    f.append(text(680, 203, "Сценарій Б: Немає подій I/O", size=10, color=NEG, bold=True))
    f.append(text(680, 217, "Пробудження рівно через 45 мс", size=10, color=INK))
    f.append(text(680, 231, "Виконуємо колбек таймера", size=9, color=MUTED))

    render(os.path.join(IMG, "timer-demux-coordination.svg"), W, H, *f)


def fig_worker_pool_offloading():
    """Діаграма 4: Винесення важкої блокуючої роботи у пул потоків через eventfd."""
    W, H = 820, 300
    f = []

    f.append(text(410, 26, "Винесення важких робіт у пул робітників", size=15, color=INK, bold=True))

    # Головний потік (Event Loop)
    f.append(rect(20, 50, 250, 230, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(145, 75, "Event Loop (головний потік)", size=13, color=FIELD, bold=True))
    f.append(text(145, 93, "Крутить неблокуючий цикл", size=10, color=MUTED))
    f.append(line(35, 102, 255, 102, color="#c8ebd8"))

    f.append(rect(35, 115, 220, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(145, 132, "1. Важка задача", size=11, color=INK, bold=True))
    f.append(text(145, 147, "(file IO, bcrypt, JSON)", size=9, color=MUTED))

    f.append(rect(35, 175, 220, 42, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(145, 192, "4. Сповіщення в epoll!", size=11, color=FIELD, bold=True))
    f.append(text(145, 207, "Виконати колбек у Loop", size=9, color=INK))

    f.append(text(145, 245, "Обслуговує сокети", size=10, color=FIELD))
    f.append(text(145, 260, "без затримок і зависань", size=10, color=FIELD))

    # Передача в чергу робіт
    f.append(arrow(255, 136, 320, 136, color=LINE, sw=1.8))
    f.append(text(287, 126, "enqueue", size=10, color=INK))

    # Пул потоків робітників
    f.append(rect(320, 50, 240, 230, fill="#fdf8e6", stroke="#d35400", sw=1.5, rx=8))
    f.append(text(440, 75, "Пул робітників (Worker Pool)", size=13, color="#d35400", bold=True))
    f.append(text(440, 93, "libuv threadpool / workers", size=10, color=MUTED))
    f.append(line(335, 102, 545, 102, color="#f5d7b5"))

    f.append(rect(335, 115, 210, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(440, 132, "Черга фонових справ", size=11, color=INK, bold=True))
    f.append(text(440, 147, "[ file read, crypto ]", size=9, color=MUTED))

    f.append(rect(335, 170, 210, 45, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    f.append(text(440, 188, "2. Потік виконує:", size=10, color=POS, bold=True))
    f.append(text(440, 204, "Блокуючий read()...", size=10, color=INK))

    f.append(rect(335, 225, 210, 45, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(440, 243, "3. Запис у дескриптор:", size=10, color=INK, bold=True))
    f.append(text(440, 258, "write(eventfd, &1, 8)", size=10, color=NEG, bold=True))

    # Сигнальний міст (eventfd / pipe)
    f.append(arrow(545, 247, 610, 247, color=NEG, sw=1.8))

    # Канал сповіщення
    f.append(rect(610, 50, 190, 230, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(705, 75, "Сигнальний канал", size=13, color=NEG, bold=True))
    f.append(text(705, 93, "eventfd / self-pipe", size=10, color=MUTED))
    f.append(line(625, 102, 785, 102, color='#c5d8fb'))

    f.append(rect(625, 120, 160, 50, fill='#ffffff', stroke=NEG, sw=1.2, rx=4))
    f.append(text(705, 142, "eventfd > 0", size=11, color=NEG, bold=True))
    f.append(text(705, 158, "READY TO READ", size=10, color=FIELD, bold=True))


    # Return arrow
    f.append(arrow(705, 180, 705, 275, color=FIELD, sw=1.8))
    f.append(line(705, 275, 145, 275, color=FIELD, sw=1.8))
    f.append(arrow(145, 275, 145, 220, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "worker-pool-offloading.svg"), W, H, *f)



def main():
    fig_thread_per_conn_vs_event_loop()
    fig_event_loop_phases()
    fig_timer_demux_coordination()
    fig_worker_pool_offloading()
    print("Ready")


if __name__ == '__main__':
    main()
