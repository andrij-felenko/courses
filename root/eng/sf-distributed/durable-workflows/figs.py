# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Durable workflows».
Використовує спільну бібліотеку svgkit з каталогу scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_durable_execution_concept():
    """Порівняння традиційного ненадійного виконання та Durable Execution."""
    w, h = 900, 440
    frags = []

    # Ліва колонка: Класичне виконання
    frags.append(fitbox(20, 15, 415, 410, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(227, 45, "Традиційне виконання (Volatile State)", size=13, color=POS, bold=True))

    frags.append(textbox(227, 90, "Пам'ять процесу (Стек / Купа)\nЛокальні змінні та виклики", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=280)[0])

    frags.append(textbox(227, 185, "Аварія / Перезавантаження вузла\n(OOM, перезапуск пода, мережевий збій)", size=11, pad=8, fill="#fdecea", stroke=POS, min_w=280)[0])

    frags.append(arrow(227, 120, 227, 155, color=POS, sw=1.5))
    frags.append(arrow(227, 215, 227, 250, color=POS, sw=1.5))

    frags.append(fitbox(40, 260, 375, 145,
                         "Наслідки збою в класичних системах:\n"
                         "• Стек викликів і стан змінних повністю знищено\n"
                         "• Ручний розбір статусу через таблиці БД (status='...')\n"
                         "• Ризик дублювання оплат або втрати кроків\n"
                         "• Складні розриви логіки на десятки мікросервісів",
                         size=11, pad=8, fill="#ffffff", stroke="#e0b4b0", sw=1.2, color=INK))

    # Права колонка: Durable Execution
    frags.append(fitbox(465, 15, 415, 410, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(672, 45, "Durable Execution (Незнищенний процес)", size=13, color=FIELD, bold=True))

    frags.append(textbox(672, 90, "Звичайний імперативний код\n(послідовні виклики, цикли, try/catch)", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=280)[0])

    frags.append(textbox(672, 185, "Журнал подій (Event History)\nФіксація кожного завершеного кроку", size=11, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=280)[0])

    frags.append(arrow(672, 120, 672, 155, color=FIELD, sw=1.5))
    frags.append(arrow(672, 215, 672, 250, color=FIELD, sw=1.5))

    frags.append(fitbox(485, 260, 375, 145,
                         "Властивості незнищенного процесу:\n"
                         "• Після аварії код відновлюється з точного місця паузи\n"
                         "• Жодних подвійних списань чи повторних побічних дій\n"
                         "• Стан, локальні змінні й черговість гарантовані рушієм\n"
                         "• Процес може тривати місяцями без утримання пам'яті",
                         size=11, pad=8, fill="#ffffff", stroke="#a3d9b8", sw=1.2, color=INK))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '%s\n</svg>' % (w, h, w, h, "\n".join(frags)))
    with open(os.path.join(OUT_DIR, "durable-execution-concept.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig_event_sourcing_replay():
    """Схема роботи детермінованого відтворення (Deterministic Replay)."""
    w, h = 920, 480
    frags = []

    # Верхній блок: Історія подій
    frags.append(fitbox(20, 15, 880, 120, "", fill="#f9fafb", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(460, 40, "Незмінний журнал історії подій (Event History у сховищі)", size=12, color=INK, bold=True))

    frags.append(textbox(130, 80, "1. WorkflowStarted\n(Вхідні аргументи)", size=10, pad=6, fill="#ffffff", stroke=LINE, min_w=150)[0])
    frags.append(textbox(350, 80, "2. ActivityCompleted\n(Платіж: успіх $100)", size=10, pad=6, fill="#e8f8f0", stroke=FIELD, min_w=160)[0])
    frags.append(textbox(580, 80, "3. ActivityCompleted\n(Склад: резерв ID=42)", size=10, pad=6, fill="#e8f8f0", stroke=FIELD, min_w=160)[0])
    frags.append(textbox(800, 80, "4. ActivityScheduled\n(Доставка кур'єром)", size=10, pad=6, fill="#fff3e0", stroke=POS, min_w=150)[0])

    frags.append(arrow(210, 80, 260, 80, color=LINE, sw=1.5))
    frags.append(arrow(440, 80, 490, 80, color=LINE, sw=1.5))
    frags.append(arrow(670, 80, 715, 80, color=LINE, sw=1.5))

    # Середній блок: Перезапуск воркера
    frags.append(textbox(460, 175, "Аварія попереднього вузла -> Новий воркер підхоплює задачу і читає історію", size=11, pad=8, fill="#fdecea", stroke=POS, min_w=620)[0])
    frags.append(arrow(460, 135, 460, 155, color=POS, sw=1.5))
    frags.append(arrow(460, 195, 460, 220, color=FIELD, sw=1.5))

    # Нижній блок: Фази детермінованого відтворення
    frags.append(fitbox(20, 230, 880, 230, "", fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(460, 255, "Виконання коду функції Workflow у пам'яті нового воркера", size=12, color=INK, bold=True))

    frags.append(textbox(170, 310, "Крок 1: charge(100)\nРезультат береться з історії!\nРеальний API НЕ викликається", size=10, pad=6, fill="#f4faf6", stroke=FIELD, min_w=210)[0])
    frags.append(textbox(460, 310, "Крок 2: reserve(item)\nРезультат береться з історії!\nБД складу НЕ чіпається", size=10, pad=6, fill="#f4faf6", stroke=FIELD, min_w=210)[0])
    frags.append(textbox(750, 310, "Крок 3: dispatchOrder()\nЗапису в історії немає!\nВідправка нової задачі у чергу", size=10, pad=6, fill="#fff8e1", stroke=POS, min_w=210)[0])

    frags.append(arrow(280, 310, 350, 310, color=FIELD, sw=1.5))
    frags.append(arrow(570, 310, 640, 310, color=POS, sw=1.5))

    frags.append(fitbox(40, 375, 840, 65,
                         "Принцип Replay:\n"
                         "Воркер повторно проганяє детермінований код від початку. Усі минулі кроки миттєво підставляються\n"
                         "з журналу історії без зовнішніх викликів, доки виконання не досягне актуальної межі (frontier).",
                         size=11, pad=6, fill="#f9fafb", stroke=MUTED, sw=1.0, color=INK))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '%s\n</svg>' % (w, h, w, h, "\n".join(frags)))
    with open(os.path.join(OUT_DIR, "event-sourcing-replay.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig_workflow_activity_topology():
    """Топологія платформи: клієнт, рушій координації, workflow-воркери та activity-воркери."""
    w, h = 900, 460
    frags = []

    # Клієнт
    frags.append(textbox(100, 230, "Клієнтський сервіс\n(Start / Signal / Query)", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=150)[0])

    # Центральний рушій (Orchestration Service)
    frags.append(fitbox(235, 30, 320, 400, "", fill="#f9fafb", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(395, 60, "Рушій координації (Orchestrator)", size=13, color=INK, bold=True))

    frags.append(textbox(395, 115, "Журнал історії подій\n(Event History DB)", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=240)[0])
    frags.append(textbox(395, 195, "Таймери та планувальник\n(Durable Timers & Shards)", size=11, pad=6, fill="#ffffff", stroke=LINE, min_w=240)[0])
    frags.append(textbox(395, 275, "Черги задач Workflow\n(Workflow Task Queues)", size=11, pad=6, fill="#e8f8f0", stroke=FIELD, min_w=240)[0])
    frags.append(textbox(395, 355, "Черги задач Activity\n(Activity Task Queues)", size=11, pad=6, fill="#fff3e0", stroke=POS, min_w=240)[0])

    # Стрілка від клієнта до рушія
    frags.append(arrow(180, 230, 230, 230, color=LINE, sw=1.5))

    # Праві воркери: Workflow Workers
    frags.append(fitbox(610, 30, 270, 185, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(745, 60, "Workflow Workers", size=12, color=FIELD, bold=True))
    frags.append(textbox(745, 110, "Детермінована логіка\n(Керування потоком, таймери)\nСувора ізоляція: без прямого I/O", size=10, pad=6, fill="#ffffff", stroke=FIELD, min_w=230)[0])
    frags.append(textbox(745, 175, "Опитування: Workflow Task Queue", size=10, pad=4, fill="#e8f8f0", stroke=FIELD, min_w=230)[0])

    # Праві воркери: Activity Workers
    frags.append(fitbox(610, 245, 270, 185, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(745, 275, "Activity Workers", size=12, color=POS, bold=True))
    frags.append(textbox(745, 325, "Побічні ефекти (Side Effects)\n(REST API, SQL, платежі, SMS)\nПовтори при збоях, Heartbeat", size=10, pad=6, fill="#ffffff", stroke=POS, min_w=230)[0])
    frags.append(textbox(745, 390, "Опитування: Activity Task Queue", size=10, pad=4, fill="#fdecea", stroke=POS, min_w=230)[0])

    # Стрілки між чергами та воркерами
    frags.append(arrow(520, 275, 605, 175, color=FIELD, sw=1.5))
    frags.append(arrow(520, 355, 605, 390, color=POS, sw=1.5))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '%s\n</svg>' % (w, h, w, h, "\n".join(frags)))
    with open(os.path.join(OUT_DIR, "workflow-activity-topology.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def fig_activity_timeouts_and_heartbeats():
    """Чотири виміри таймаутів Activity у розподілених незнищенних процесах."""
    w, h = 920, 430
    frags = []

    # Загальний фон і таймлайн
    frags.append(fitbox(20, 15, 880, 400, "", fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(460, 45, "Чотири виміри таймаутів для надійного виконання Activity", size=13, color=INK, bold=True))

    # Головна шкала Schedule-To-Close
    frags.append(fitbox(50, 80, 820, 45, "Schedule-To-Close Timeout: Загальний бюджет часу на виконання (включно з усіма повторами)", size=11, pad=6, fill="#eef2ff", stroke="#3f51b5", sw=1.5, color="#1a237e"))

    # Етап 1: Черга (Schedule-To-Start)
    frags.append(fitbox(50, 150, 180, 90, "Schedule-To-Start\nОчікування в черзі\n(вільний воркер\nне бере задачу)", size=10, pad=6, fill="#fff8e1", stroke="#ffa000", sw=1.2, color=INK))

    # Етап 2: Спроба 1 (Падіння)
    frags.append(fitbox(245, 150, 210, 90, "Спроба 1 (Start-To-Close)\nВиконання коду...\nПомилка мережі (503)", size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    # Етап 3: Пауза Backoff
    frags.append(fitbox(470, 150, 110, 90, "Retry\nBackoff\n(Пауза)", size=10, pad=6, fill="#f5f5f5", stroke=MUTED, sw=1.2, color=INK))

    # Етап 4: Спроба 2 (Успіх)
    frags.append(fitbox(595, 150, 275, 90, "Спроба 2 (Start-To-Close)\nВиконання на іншому воркері...\nУспішний результат!", size=10, pad=6, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=INK))

    # Heartbeat таймаут для довгих задач
    frags.append(fitbox(50, 265, 820, 125, "", fill="#f9fafb", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(460, 290, "Heartbeat Timeout: Контроль живості для тривалих задач (хвилини/години)", size=12, color=INK, bold=True))

    frags.append(textbox(200, 335, "Воркер надсилає пульс (Heartbeat)\nкожні 10 секунд разом із прогресом", size=10, pad=6, fill="#ffffff", stroke=FIELD, min_w=260)[0])
    frags.append(textbox(640, 335, "Якщо пульс відсутній > Heartbeat Timeout,\nрушій миттєво перезапускає задачу на іншому вузлі", size=10, pad=6, fill="#ffffff", stroke=POS, min_w=280)[0])

    frags.append(arrow(340, 335, 480, 335, color=LINE, sw=1.5))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '%s\n</svg>' % (w, h, w, h, "\n".join(frags)))
    with open(os.path.join(OUT_DIR, "activity-timeouts-and-heartbeats.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    fig_durable_execution_concept()
    fig_event_sourcing_replay()
    fig_workflow_activity_topology()
    fig_activity_timeouts_and_heartbeats()
    print("All figures successfully generated in %s" % OUT_DIR)
