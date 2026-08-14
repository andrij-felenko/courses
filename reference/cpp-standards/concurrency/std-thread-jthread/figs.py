# -*- coding: utf-8 -*-
"""Фігури до теми «std::thread та std::jthread: управління потоками та скасування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Життєвий цикл std::thread та std::jthread ─────────────────────────────
def fig_thread_lifecycle():
    W, H = 940, 420
    f = []

    f.append(text(470, 35, "Життєвий цикл системного потоку та об'єктів std::thread / std::jthread", size=16, color=INK, anchor="middle", bold=True))

    # Початковий стан
    f.append(fitbox(40, 80, 220, 90, "std::thread t;\n(Порожній об'єкт)\njoinable() == false\nid() == std::thread::id()", size=11, fill="#f4f6f8", stroke=LINE))

    # Створення та активне виконання
    f.append(arrow(260, 125, 340, 125, color=NEG, sw=2))
    f.append(text(300, 115, "t(worker_func)", size=11, color=NEG, bold=True))

    f.append(fitbox(340, 80, 260, 90, "АКТИВНИЙ ПОТІК\njoinable() == true\nOS thread біжить паралельно\nt.get_id() != id()", size=12, fill="#e8f4fc", stroke=NEG))

    # Гілка 1: join()
    f.append(arrow(600, 100, 700, 70, color=FIELD, sw=2))
    f.append(text(650, 75, "t.join()", size=11, color=FIELD, bold=True))

    f.append(fitbox(700, 40, 200, 70, "Завершено та приєднано\nОС-ресурси звільнено\njoinable() == false", size=11, fill="#e8f6ee", stroke=FIELD))

    # Гілка 2: detach()
    f.append(arrow(600, 125, 700, 125, color=MUTED, sw=2))
    f.append(text(650, 115, "t.detach()", size=11, color=MUTED, bold=True))

    f.append(fitbox(700, 100, 200, 60, "Від'єднано (Background)\nC++ об'єкт не-joinable\nОС потім сама прибере", size=11, fill="#f4f6f8", stroke=MUTED))

    # Гілка 3: Небезпечна деструкція std::thread (розділені стрілки, щоб не перетинати напис)
    f.append(arrow(470, 170, 470, 192, color=POS, sw=2))
    f.append(text(470, 206, "~thread() при joinable() == true", size=11, color=POS, bold=True))
    f.append(arrow(470, 218, 470, 240, color=POS, sw=2))

    f.append(fitbox(320, 240, 300, 70, "КАТАСТРОФА: std::terminate()\nАварійне завершення всієї програми!\nРесурси потоку не збережено", size=12, fill="#fff0f0", stroke=POS))

    # Поведінка std::jthread для порівняння
    f.append(fitbox(40, 340, 860, 60, "Поведінка std::jthread у C++20 при деструкції:\n"
                                      "~jthread() автоматично робить:  1. request_stop()  ──►  2. join()  ──► Безпечне завершення без аварій", size=12, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'thread-lifecycle.svg'), W, H, *f, title="Життєвий цикл std::thread та std::jthread")


# ── 2. Порівняння поведінки при розгортанні стеку ────────────────────────────
def fig_jthread_raii_exception():
    W, H = 940, 410
    f = []

    f.append(text(470, 30, "Розгортання стеку (Stack Unwinding) при викиданні винятку", size=16, color=INK, anchor="middle", bold=True))

    # Сценарій: Програма викидає виняток усередині функції
    f.append(fitbox(50, 65, 840, 45, "Виклик функції з винятком: std::vector::at() кидає std::out_of_range ──► Початок unwind_stack()", size=12, fill="#fef5e7", stroke=POS))

    # Стовпчик std::thread
    f.append(text(240, 135, "std::thread (C++11)", size=14, color=POS, bold=True))
    f.append(fitbox(50, 150, 380, 200, "1. Знищення локальних змінних стеку\n"
                                        "2. Виклик деструктора ~thread()\n"
                                        "3. Перевірка прапорця: joinable() == true\n"
                                        "4. Виклик std::terminate()\n"
                                        "5. КРАШ: Програма падає миттєво!\n\n"
                                        "Потік ОС залишається сиротою в пам'яті", size=12, fill="#fff0f0", stroke=POS))

    # Стовпчик std::jthread
    f.append(text(700, 135, "std::jthread (C++20)", size=14, color=FIELD, bold=True))
    f.append(fitbox(510, 150, 380, 200, "1. Знищення локальних змінних стеку\n"
                                         "2. Виклик деструктора ~jthread()\n"
                                         "3. Автоматичний t.request_stop()\n"
                                         "4. Автоматичний блокуючий t.join()\n"
                                         "5. УСПІХ: Стек розгорнуто повністю!\n\n"
                                         "Виняток перехоплюється в catch(){...}", size=12, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 385, "std::jthread гарантує базову та сильну безпеку винятків за рахунок RAII", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'jthread-raii-exception.svg'), W, H, *f, title="Розгортання стеку та безпека винятків")


# ── 3. Архітектура кооперативного скасування ──────────────────────────────────
def fig_stop_token_architecture():
    W, H = 940, 420
    f = []

    f.append(text(470, 30, "Архітектура кооперативного скасування: std::stop_source, stop_token та stop_callback", size=16, color=INK, anchor="middle", bold=True))

    # Блок stop_source (Джерело)
    f.append(fitbox(40, 70, 250, 100, "std::stop_source\n(Головний потік)\n\nМетод: .request_stop()\nПеревірка: .stop_requested()", size=12, fill="#e8f4fc", stroke=NEG))

    # Спільний стан у пам'яті (Shared Stop State)
    f.append(fitbox(345, 70, 250, 100, "Спільний stop_state\n(Купа / Ref-counted)\n\n• Atomic bool stop_requested_\n• Список callback-функцій", size=12, fill="#fef5e7", stroke=POS))

    # Блок stop_token (Спостерігач)
    f.append(fitbox(650, 70, 250, 100, "std::stop_token\n(Робочий потік)\n\nПеревірка в циклі:\nst.stop_requested()", size=12, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(290, 120, 345, 120, color=NEG, sw=2))
    f.append(arrow(595, 120, 650, 120, color=FIELD, sw=2))

    # Сигнал та реакція (розділені стрілки, щоб не накладатись на текст)
    f.append(arrow(470, 170, 470, 188, color=POS, sw=2))
    f.append(text(470, 202, "Подія: Виклик request_stop() змінює прапорець на true", size=12, color=POS, bold=True, anchor="middle"))
    f.append(arrow(470, 214, 470, 236, color=POS, sw=2))

    # Два шляхи реагування
    f.append(fitbox(60, 240, 380, 130, "Шлях 1: Поллінг у робочому циклі\n\nwhile (!st.stop_requested()) {\n    do_chunk_of_work();\n}\n// Робочий потік коректно виходить з циклу", size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(500, 240, 380, 130, "Шлях 2: Асинхронний std::stop_callback\n\nstd::stop_callback cb(st, [&]{\n    socket.close(); // Сповіщає про переривання\n});\n// Викличуть негайно при настанні сигналу", size=11, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'stop-token-architecture.svg'), W, H, *f, title="Архітектура кооперативного скасування")


def main():
    fig_thread_lifecycle()
    fig_jthread_raii_exception()
    fig_stop_token_architecture()
    print("Усі фігури успішно згенеровано у", OUT)

if __name__ == '__main__':
    main()
