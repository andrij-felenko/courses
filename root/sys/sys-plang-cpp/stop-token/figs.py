# -*- coding: utf-8 -*-
"""Фігури до теми «std::stop_token: кооперативне скасування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Триєдина архітектура stop_token ─────────────────────────────────────────
def fig_stop_token_architecture():
    W, H = 960, 450
    f = []

    f.append(text(480, 32, "Триєдина архітектура кооперативного скасування: stop_source, stop_token та stop_callback", size=16, color=INK, anchor="middle", bold=True))

    # Лівий блок: stop_source (Ініціатор)
    f.append(fitbox(40, 70, 240, 130, "std::stop_source\n(Ініціатор скасування)\n\n• request_stop()\n• get_token()\n• stop_requested()\n• stop_possible()", size=12, fill="#e8f4fc", stroke=NEG))

    # Центральний блок: Спільний стан stop_state
    f.append(fitbox(340, 60, 280, 150, "Спільний стан (stop_state)\n[Блок керування блок у купі]\n\n• std::atomic<uint64_t> ref_count\n• std::atomic<bool> stop_flag\n• std::atomic<thread_id> caller\n• Список callback-підписників", size=11, fill="#fef5e7", stroke=POS))

    # Правий блок: stop_token (Спостерігач)
    f.append(fitbox(680, 70, 240, 130, "std::stop_token\n(Спостерігач / Read-only)\n\n• stop_requested()\n• stop_possible()\n• Передається у робітника\n  за значенням (копія)", size=12, fill="#e8f6ee", stroke=FIELD))

    # Зв'язки між джерелом, станом і токеном
    f.append(arrow(280, 135, 340, 135, color=NEG, sw=2))
    f.append(arrow(680, 135, 620, 135, color=FIELD, sw=2))

    # Нижній блок: stop_callback (Підписник)
    f.append(fitbox(260, 270, 440, 140, "std::stop_callback<Callback>\n(RAII-підписка на подію скасування)\n\n1. Конструктор: реєструє лямбду у списку stop_state\n2. Якщо скасовано заздалегідь: негайно викликає лямбду у поточному потоці\n3. Деструктор: безпечно вилучає лямбду зі списку або чекає завершення виклику", size=11, fill="#f4f6f8", stroke=LINE))

    # Стрілка від stop_state до stop_callback
    f.append(arrow(480, 210, 480, 270, color=POS, sw=2))

    # Додаткові блоки взаємодії
    f.append(fitbox(40, 270, 190, 140, "Поллінг у циклі:\n\nwhile (!st.stop_requested()) {\n    process_batch();\n}\n\nЧисте завершення", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(730, 270, 190, 140, "Асинхронний тригер:\n\nstop_callback cb(st, [&]{\n    socket.close();\n    cv.notify_all();\n});\nРозблокування I/O", size=11, fill="#fef5e7", stroke=POS))

    f.append(arrow(730, 340, 700, 340, color=POS, sw=1.5))
    f.append(arrow(230, 340, 260, 340, color=FIELD, sw=1.5))

    render(os.path.join(OUT, 'stop-token-architecture.svg'), W, H, *f, title="Архітектура stop_token")


# ── 2. Синхронізація та вирішення гонок у stop_callback ────────────────────────
def fig_stop_callback_races():
    W, H = 960, 450
    f = []

    f.append(text(480, 32, "Синхронізація та вирішення гонок даних у stop_callback", size=16, color=INK, anchor="middle", bold=True))

    # Сценарій 1: request_stop під час зареєстрованого колбека
    f.append(fitbox(40, 70, 270, 340, "Сценарій 1: Нормальний виклик\n\nПотік A: конструює stop_callback\n└── Додає вузол у список стану\n\nПотік B: викликає request_stop()\n├── Атомарно встановлює прапорець\n├── Захоплює список колбеків\n└── Синхронно виконує колбек\n    безпосередньо в Потоці B!\n\nГарантія: Виконання відбувається\nрівно один раз (exact-once).", size=11, fill="#e8f4fc", stroke=NEG))

    # Сценарій 2: Реєстрація після request_stop
    f.append(fitbox(345, 70, 270, 340, "Сценарій 2: Пізня реєстрація\n\nПотік B: уже викликав request_stop()\n└── Стан: stop_requested == true\n\nПотік A: конструює stop_callback\n├── Читає атомарний прапорець\n├── Бачить, що сигнал уже надійшов\n└── Негайно викликає колбек\n    у Потоці A під час конструювання!\n\nГарантія: Сигнал не губиться,\nнавіть якщо прийшов раніше.", size=11, fill="#e8f6ee", stroke=FIELD))

    # Сценарій 3: Деструкція під час паралельного виконання
    f.append(fitbox(650, 70, 270, 340, "Сценарій 3: Конкурентна деструкція\n\nПотік B: виконує callback у request_stop()\nПотік A: виходить зі скоупу ~stop_callback()\n\nСинхронізація в деструкторі:\n├── Перевіряє ID виконуючого потоку\n├── Якщо це Потік B: деструктор Потоку A\n│   БЛОКУЄТЬСЯ до завершення колбека\n└── Лише після цього звільняє пам'ять!\n\nГарантія: Жодних use-after-free\nдля захоплених локальних змінних.", size=11, fill="#fef5e7", stroke=POS))

    render(os.path.join(OUT, 'stop-callback-races.svg'), W, H, *f, title="Вирішення гонок у stop_callback")


# ── 3. Переривання блокуючих очікувань у condition_variable_any ───────────────
def fig_interruptible_cv_wait():
    W, H = 960, 440
    f = []

    f.append(text(480, 32, "Переривання очікування в std::condition_variable_any за допомогою stop_token", size=16, color=INK, anchor="middle", bold=True))

    # Крок 1: Вхід у wait
    f.append(fitbox(40, 70, 260, 90, "Крок 1: Вхід у wait()\n\ncv.wait(lock, stoken, [&]{\n    return !queue.empty();\n});\nПотік тримає захоплений lock.", size=11, fill="#e8f4fc", stroke=NEG))

    # Крок 2: Реєстрація внутрішнього колбека
    f.append(fitbox(350, 70, 260, 90, "Крок 2: Внутрішній stop_callback\n\nРеєструється тимчасовий колбек:\nstop_callback cb(stoken, [&]{\n    cv.notify_all();\n});", size=11, fill="#fef5e7", stroke=POS))

    # Крок 3: Засинання
    f.append(fitbox(660, 70, 260, 90, "Крок 3: Атомарне засинання\n\nПеревірка predicate() == false.\nВідпускання lock та перехід\nу стан очікування ОС.", size=11, fill="#f4f6f8", stroke=LINE))

    # Стрілки верхнього ряду
    f.append(arrow(300, 115, 350, 115, color=LINE, sw=2))
    f.append(arrow(610, 115, 660, 115, color=LINE, sw=2))

    # Подія переривання (Потік-джерело)
    f.append(fitbox(40, 220, 880, 65, "ПОДІЯ СКАСУВАННЯ: Головний потік викликає stop_source.request_stop()\n──► Спрацьовує stop_callback ──► Викликається cv.notify_all() ──► Сплячий потік миттєво прокидається!", size=12, fill="#fff0f0", stroke=POS))

    # Крок 4: Пробудження та завершення
    f.append(fitbox(150, 320, 310, 90, "Крок 4: Захоплення lock\n\nПотік знову захоплює lock,\nзнищує тимчасовий stop_callback\nта перевіряє умову виходу.", size=11, fill="#e8f4fc", stroke=NEG))

    f.append(fitbox(500, 320, 310, 90, "Крок 5: Повернення з wait()\n\nПовертає значення предиката.\nЯкщо stoken.stop_requested() == true,\nпотік коректно завершує роботу.", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(460, 365, 500, 365, color=FIELD, sw=2))

    render(os.path.join(OUT, 'interruptible-cv-wait.svg'), W, H, *f, title="Переривання condition_variable_any")


def main():
    fig_stop_token_architecture()
    fig_stop_callback_races()
    fig_interruptible_cv_wait()
    print("Усі фігури успішно згенеровано у", OUT)


if __name__ == '__main__':
    main()
