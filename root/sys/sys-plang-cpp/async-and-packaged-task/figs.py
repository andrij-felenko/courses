# -*- coding: utf-8 -*-
"""Фігури до теми «async і packaged_task: запуск із результатом»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Режими запуску std::async ──────────────────────────────────────────
def fig_async_execution_modes():
    W, H = 940, 440
    f = []

    f.append(text(50, 40, "Режими виконання std::async: Негайне (async) проти Лінивого (deferred)", size=16, color=INK, anchor="start", bold=True))

    # Політика 1: std::launch::async
    f.append(text(50, 80, "Режим 1: std::launch::async (Окремий фоновий потік)", size=14, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(50, 100, 240, 90,
                    "Потік-викликач (Caller)\n"
                    "std::async(launch::async, fn)\n"
                    "• Негайно створює потік\n"
                    "• Повертає std::future<T>",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(295, 145, 365, 145, color=FIELD, sw=2))

    f.append(fitbox(370, 100, 260, 90,
                    "Фоновий потік (Worker Thread)\n"
                    "fn(args...) виконується паралельно\n"
                    "• Запис результату в Shared State\n"
                    "• Сигнал готовності майбутнього",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(635, 145, 705, 145, color=FIELD, sw=2))

    f.append(fitbox(710, 100, 180, 90,
                    "Споживач (Consumer)\n"
                    "future.get()\n"
                    "Отримує результат без затримки",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Політика 2: std::launch::deferred
    f.append(text(50, 230, "Режим 2: std::launch::deferred (Обчислення за вимогою у тому ж потоці)", size=14, color=POS, anchor="start", bold=True))

    f.append(fitbox(50, 250, 240, 90,
                    "Потік-викликач (Caller)\n"
                    "std::async(launch::deferred, fn)\n"
                    "• Потік НЕ створюється\n"
                    "• Функцію відкладено",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(arrow(295, 295, 365, 295, color=POS, sw=2))

    f.append(fitbox(370, 250, 260, 90,
                    "Стан очікування (Deferred State)\n"
                    "Функція виклику спарована з future,\n"
                    "але підвішена до першого .get()",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(635, 295, 705, 295, color=POS, sw=2))

    f.append(fitbox(710, 250, 180, 90,
                    "Споживач (Consumer)\n"
                    "future.get()\n"
                    "Синхронний виклик fn() прямо тут!",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(text(470, 395, "Комбінація (async | deferred) залишає вибір рантайму залежно від завантаження системи", size=11, color=MUTED))

    render(os.path.join(OUT, 'async-execution-modes.svg'), W, H, *f,
           title="Режими запуску std::async")


# ── 2. Блокування деструктора тимчасового future ─────────────────────────
def fig_future_destructor_blocking():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Пастка деструктора std::future при асинхронному виклику std::async", size=16, color=INK, anchor="start", bold=True))

    # Сценарій А: Збереження future (Паралельне виконання)
    f.append(text(50, 75, "Правильно: Збереження у змінну `auto fut = std::async(...)`", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 95, 410, 110,
                    "Потік 1: std::async(launch::async, task1);\n"
                    "Потік 2: std::async(launch::async, task2);\n"
                    "┌──────────────────────────────────────────────┐\n"
                    "│ Потоки працюють паралельно в тлі            │\n"
                    "│ fut1.get() і fut2.get() чекають лише в кінці  │\n"
                    "└──────────────────────────────────────────────┘",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(480, 95, 410, 110,
                    "Часова шкала (Паралельно):\n"
                    "Main:  [async1] ─── [async2] ────────────► fut.get()\n"
                    "Worker1: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (Завдання 1)\n"
                    "Worker2: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (Завдання 2)\n"
                    "Загальний час = max(T1, T2)",
                    size=11, fill="#f4f6f8", stroke=LINE))

    # Сценарій Б: Тимчасовий future (Послідовне блокування)
    f.append(text(50, 235, "Пастка: Виклик без збереження `std::async(...)` (тимчасовий об'єкт)", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 255, 410, 110,
                    "std::async(launch::async, task1); // Створює temp future\n"
                    "std::async(launch::async, task2); // Тимчасовий об'єкт!\n"
                    "┌──────────────────────────────────────────────┐\n"
                    "│ ~future() блокує потік у крапці з комою!     │\n"
                    "│ Друга задача не почнеться, поки перша не дге │\n"
                    "└──────────────────────────────────────────────┘",
                    size=11, fill="#fff0f0", stroke=NEG))

    f.append(fitbox(480, 255, 410, 110,
                    "Часова шкала (Послідовне блокування!):\n"
                    "Main:  [async1]──[wait T1]──[async2]──[wait T2]─►\n"
                    "Worker1: ▓▓▓▓▓▓▓▓▓▓\n"
                    "Worker2:           ▓▓▓▓▓▓▓▓▓▓\n"
                    "Загальний час = T1 + T2 (Паралельність втрачено!)",
                    size=11, fill="#fff0f0", stroke=NEG))

    f.append(text(470, 395, "Деструктор rvalue-future, поверненого з std::async, викликає ~future(), який чекає завершення потоку", size=11, color=MUTED))

    render(os.path.join(OUT, 'future-destructor-blocking.svg'), W, H, *f,
           title="Блокування деструктора тимчасового future")


# ── 3. Архітектура std::packaged_task ────────────────────────────────────
def fig_packaged_task_pipeline():
    W, H = 940, 440
    f = []

    f.append(text(50, 35, "Внутрішня структура та конвеєр даних std::packaged_task", size=16, color=INK, anchor="start", bold=True))

    # Ліва частина: Обгортка й Callable
    f.append(fitbox(50, 70, 250, 150,
                    "std::packaged_task<R(Args...)>\n"
                    "┌────────────────────────────┐\n"
                    "│ Wrapped Callable          │\n"
                    "│ (Lambda / Function / Bind) │\n"
                    "├────────────────────────────┤\n"
                    "│ Shared State Pointer       │\n"
                    "└────────────────────────────┘\n"
                    "• Move-only обгортка\n"
                    "• Відокремлює запуск від виклику",
                    size=11, fill="#eef2f7", stroke=LINE))

    f.append(arrow(305, 145, 365, 145, color=FIELD, sw=2))

    # Центральна частина: Shared State
    f.append(fitbox(370, 70, 250, 150,
                    "Спільний стан (Shared State)\n"
                    "┌────────────────────────────┐\n"
                    "│ State: Empty / Ready / Err │\n"
                    "├────────────────────────────┤\n"
                    "│ Storage for Return Value R │\n"
                    "│ or std::exception_ptr      │\n"
                    "├────────────────────────────┤\n"
                    "│ Mutex + Condition Variable │\n"
                    "└────────────────────────────┘",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(arrow(625, 145, 685, 145, color=FIELD, sw=2))

    # Права частина: std::future
    f.append(fitbox(690, 70, 200, 150,
                    "std::future<R>\n"
                    "┌────────────────────────────┐\n"
                    "│ Shared State Pointer       │\n"
                    "└────────────────────────────┘\n"
                    "Отримано через\n"
                    "task.get_future()\n\n"
                    "Метод .get() зчитує R\n"
                    "або перевикидає виняток",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Нижня частина: Виконання у потоці
    f.append(line(40, 245, 900, 245, color=MUTED, sw=1, dash="6 5"))

    f.append(text(50, 270, "Послідовність подій у часі:", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 290, 260, 100,
                    "1. Створення й підготовка\n"
                    "• Instantiation task(fn)\n"
                    "• fut = task.get_future()\n"
                    "• Move task в інший потік/чергу",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(340, 290, 260, 100,
                    "2. Виконання у Worker Thread\n"
                    "• Виклик task(args...)\n"
                    "• Обчислення R = fn(args)\n"
                    "• Запис R у Shared State",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(630, 290, 260, 100,
                    "3. Отримання у Consumer Thread\n"
                    "• fut.get() чекає готовності\n"
                    "• Забирає результат R\n"
                    "• Спільний стан звільняється",
                    size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'packaged-task-pipeline.svg'), W, H, *f,
           title="Архітектура std::packaged_task")


# ── 4. Інтеграція у пул потоків ──────────────────────────────────────────
def fig_thread_pool_integration():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Використання std::packaged_task у черзі задач пулу потоків", size=16, color=INK, anchor="start", bold=True))

    # Викликачі (Клієнти)
    f.append(fitbox(50, 75, 200, 160,
                    "Клієнтські потоки\n"
                    "┌──────────────────────────┐\n"
                    "│ pool.enqueue(fn1) ──► fut1│\n"
                    "│ pool.enqueue(fn2) ──► fut2│\n"
                    "│ pool.enqueue(fn3) ──► fut3│\n"
                    "└──────────────────────────┘\n"
                    "Упаковка функції в\n"
                    "packaged_task<R()> через\n"
                    "std::make_shared",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(255, 155, 315, 155, color=FIELD, sw=2))

    # Потокобезпечна Черга
    f.append(fitbox(320, 75, 280, 160,
                    "Потокобезпечна черга задач\n"
                    "std::queue<std::function<void()>>\n"
                    "┌──────────────────────────┐\n"
                    "│ [Task 3] [Task 2] [Task 1]│\n"
                    "└──────────────────────────┘\n"
                    "Синхронізація:\n"
                    "• std::mutex\n"
                    "• std::condition_variable",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(arrow(605, 155, 665, 155, color=POS, sw=2))

    # Робочі потоки
    f.append(fitbox(670, 75, 220, 160,
                    "Пул робочих потоків\n"
                    "Worker Threads (std::jthread)\n"
                    "┌──────────────────────────┐\n"
                    "│ Worker 1 ──► task()      │\n"
                    "│ Worker 2 ──► idle        │\n"
                    "│ Worker N ──► task()      │\n"
                    "└──────────────────────────┘\n"
                    "Витягують void() задачу,\n"
                    "викликають task()",
                    size=11, fill="#f4f6f8", stroke=LINE))

    # Результати
    f.append(line(40, 260, 900, 260, color=MUTED, sw=1, dash="6 5"))

    f.append(fitbox(50, 280, 840, 100,
                    "Перевага схем з std::packaged_task:\n"
                    "• Типи R та аргументів стираються до std::function<void()>\n"
                    "• Клієнт отримує чистий std::future<R> і чекає лише свій результат\n"
                    "• Пул потоків не знає про типи R чи аргументи — він просто викликає task()",
                    size=11, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, 'thread-pool-integration.svg'), W, H, *f,
           title="Інтеграція packaged_task у пул потоків")


def main():
    fig_async_execution_modes()
    fig_future_destructor_blocking()
    fig_packaged_task_pipeline()
    fig_thread_pool_integration()
    print("Фігури успішно згенеровано.")


if __name__ == '__main__':
    main()
