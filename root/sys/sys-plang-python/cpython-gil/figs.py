# -*- coding: utf-8 -*-
"""Генератор архітектурних діаграм для теми cpython-gil."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, fitbox, rect, text, mtext, line, arrow,
    INK, MUTED, LINE, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_gil_architecture():
    """Діаграма 1: Архітектура GIL та цикл виконання байткоду в CPython."""
    w, h = 840, 490
    frags = []

    # Заголовок
    frags.append(text(420, 26, "Архітектура Global Interpreter Lock (GIL) у CPython", size=15, bold=True))

    # Стовпець 1: Системні потоки ОС
    frags.append(rect(25, 55, 230, 410, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(140, 80, "Потоки ОС (pthread / Win32)", size=12, bold=True, color=NEG))

    frags.append(fitbox(40, 105, 200, 70, "Потік 1 (Thread-1)\nВиконує Python-код\nУтримує GIL [АКТИВНИЙ]", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(40, 195, 200, 75, "Потік 2 (Thread-2)\nCPU-bound обчислення\nОчікує на gil_mutex / cond\n[ЗАБЛОКОВАНИЙ]", size=11, fill="#f8fafc", stroke=MUTED))
    frags.append(fitbox(40, 290, 200, 75, "Потік 3 (Thread-3)\nМережевий сокет / I/O\nВідпустив GIL (SaveThread)\n[НЕБЛОКОВАНИЙ I/O]", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(40, 385, 200, 65, "Потік 4 (Thread-4)\nC/C++ розширення\nВідпустив GIL (AllowThreads)\n[ПАРАЛЕЛЬНИЙ CPU]", size=11, fill="#fef2f2", stroke=POS))

    # Стовпець 2: Ядро CPython та структура GIL
    frags.append(rect(280, 55, 275, 410, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(417, 80, "Структура GIL (_gil_runtime_state)", size=12, bold=True, color=POS))

    frags.append(fitbox(295, 105, 245, 95, "gil_mutex (М'ютекс ядра)\n• PyMUTEX_T системний замок\n• locked = 1 (зайнятий Потоком 1)\n• last_holder = ThreadState-1", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(295, 220, 245, 110, "switch_cond & switch_interval\n• PyCOND_T умовна змінна\n• sys.getswitchinterval() = 5 мс\n• Таймер примусового запиту:\n  gil_drop_request = 1", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(295, 350, 245, 95, "eval_breaker & ceval loop\n• Сигнальний прапорець перевірки\n• drop_gil() на межі інструкцій\n• Безпечна точка перемикання", size=11, fill="#fef2f2", stroke=POS))

    # Стовпець 3: Віртуальна машина та апаратні ядра
    frags.append(rect(580, 55, 235, 410, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(697, 80, "Виконання на CPU Cores", size=12, bold=True, color=FIELD))

    frags.append(fitbox(595, 105, 205, 75, "Ядро CPU 0\n_PyEval_EvalFrameDefault()\nВиконання байткоду CPython\n[100% завантаження ядра]", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(595, 200, 205, 70, "Ядро CPU 1\nПростій у futex / mutex wait\n[0% корисної роботи в CPython]", size=11, fill="#f8fafc", stroke=MUTED))
    frags.append(fitbox(595, 290, 205, 75, "Ядро CPU 2 / ОС I/O\nСистемний виклик read/epoll\nПрацює в фоні без GIL\n[Апаратне I/O]", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(595, 385, 205, 65, "Ядро CPU 3\nНативний C++/Rust код\nПаралельний SIMD/OpenMP\n[100% нативного CPU]", size=11, fill="#fef2f2", stroke=POS))

    # Стрілки
    frags.append(arrow(240, 140, 295, 140, color=LINE, sw=1.5))
    frags.append(arrow(240, 230, 295, 250, color=LINE, sw=1.5))
    frags.append(arrow(540, 140, 595, 140, color=LINE, sw=1.5))
    frags.append(arrow(240, 325, 595, 325, color=FIELD, sw=1.8))
    frags.append(arrow(240, 415, 595, 415, color=POS, sw=1.8))

    render(os.path.join(IMG_DIR, "gil-mutex-architecture.svg"), w, h, *frags)


def fig_gil_thrashing():
    """Діаграма 2: Конкуренція за GIL та явище GIL Thrashing на багатоядерних процесорах."""
    w, h = 840, 470
    frags = []

    frags.append(text(420, 26, "Хронологія GIL Thrashing: конфлікт ядер і втрата квантів часу", size=15, bold=True))

    # Шкала часу
    frags.append(line(50, 60, 790, 60, color=LINE, sw=2))
    frags.append(text(760, 50, "Час (t)", size=11, bold=True, color=MUTED))

    # Доріжка Ядра 0 (Потік 1)
    frags.append(fitbox(30, 80, 140, 50, "Ядро 0\n(Потік 1 CPU-bound)", size=11, bold=True, fill="#eef2ff", stroke=NEG))
    frags.append(rect(180, 80, 220, 50, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(text(290, 108, "Виконує байткод під GIL (5 мс)", size=10, bold=True, color=NEG))

    frags.append(rect(410, 80, 40, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(430, 108, "drop", size=9, bold=True, color=POS))

    frags.append(rect(460, 80, 200, 50, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(text(560, 108, "Миттєво перехоплює GIL знову!", size=10, bold=True, color=NEG))

    frags.append(rect(670, 80, 130, 50, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(text(735, 108, "Продовжує роботу", size=10, color=NEG))

    # Доріжка Ядра 1 (Потік 2)
    frags.append(fitbox(30, 160, 140, 50, "Ядро 1\n(Потік 2 CPU-bound)", size=11, bold=True, fill="#f8fafc", stroke=MUTED))
    frags.append(rect(180, 160, 220, 50, fill="#f1f5f9", stroke=MUTED, sw=1))
    frags.append(text(290, 188, "Спить у futex_wait (очікує 5 мс)", size=10, color=MUTED))

    frags.append(rect(410, 160, 110, 50, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(465, 188, "Пробудження ОС (~50 мкс)", size=9, bold=True, color="#b45309"))

    frags.append(rect(530, 160, 130, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(595, 188, "Замок зайнятий! Спить", size=9, bold=True, color=POS))

    frags.append(rect(670, 160, 130, 50, fill="#f1f5f9", stroke=MUTED, sw=1))
    frags.append(text(735, 188, "Спить у futex_wait", size=10, color=MUTED))

    # Стрілки взаємодії
    frags.append(arrow(400, 110, 410, 165, color=POS, sw=1.5))
    frags.append(arrow(430, 80, 470, 80, color=POS, sw=1.5))
    frags.append(arrow(530, 160, 560, 130, color=POS, sw=1.5))

    # Пояснювальний блок знизу
    frags.append(rect(30, 240, 780, 205, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(420, 265, "Чому виникає сповільнення багатопотокового CPU-bound коду:", size=12, bold=True, color=INK))

    frags.append(fitbox(45, 285, 230, 140, "1. Асиметрія кешу\nМ'ютекс gil_mutex перебуває\nу L1/L2 кеші Ядра 0.\nЯдро 0 повторно захоплює\nйого за лічені наносекунди,\nперш ніж Ядро 1 прокинеться.", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(fitbox(295, 285, 240, 140, "2. Затримка планувальника\nПеремикання контексту ОС між\nядрами займає 20–80 мкс.\nПотік 2 прокидається запізно,\nбачить GIL зайнятим і знову\nініціює системний виклик сну.", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(fitbox(555, 285, 240, 140, "3. Наслідки Thrashing\n• Мільйони марних futex-викликів\n• Постійні промахи кешу (MESI)\n• Деградація швидкодії на 20–50%\nпорівняно з одним потоком!", size=10, fill="#fff1f2", stroke=POS))

    render(os.path.join(IMG_DIR, "gil-thrashing-multicore.svg"), w, h, *frags)


def fig_shared_memory_ipc():
    """Діаграма 3: Порівняння передачі даних через IPC Queue проти Shared Memory."""
    w, h = 840, 480
    frags = []

    frags.append(text(420, 26, "Моделі пам'яті між процесами: multiprocessing.Queue проти SharedMemory", size=15, bold=True))

    # Панель зліва: IPC Queue (Pickle)
    frags.append(rect(25, 55, 380, 400, fill="#fff1f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(215, 80, "Модель 1: multiprocessing.Queue / Pipe (Pickle)", size=12, bold=True, color=POS))

    frags.append(fitbox(45, 105, 340, 60, "Процес 1 (Купа процесу 1)\nОб'єкт телеметрії / Масив NumPy (100 МБ)", size=11, fill="#ffffff", stroke=POS))
    frags.append(fitbox(45, 180, 340, 65, "pickle.dumps() Серіалізація\nПеретворення об'єкта в потік байтів\n[Високе навантаження CPU + копія в ОЗП]", size=10, fill="#ffffff", stroke=POS))
    frags.append(fitbox(45, 260, 340, 65, "Системний канал (Pipe / Socket Buffer)\nКопіювання байтів через ядро ОС (kernel space)\n[Обмеження буфера пайпа: 64 КБ]", size=10, fill="#ffffff", stroke=POS))
    frags.append(fitbox(45, 340, 340, 65, "pickle.loads() Десеріалізація у Процесі 2\nСтворення дублікатів об'єктів у новій купі\n[Загалом 3x копіювання пам'яті]", size=10, fill="#ffffff", stroke=POS))

    frags.append(arrow(215, 165, 215, 180, color=POS, sw=1.5))
    frags.append(arrow(215, 245, 215, 260, color=POS, sw=1.5))
    frags.append(arrow(215, 325, 215, 340, color=POS, sw=1.5))

    # Панель справа: Shared Memory (Zero-copy)
    frags.append(rect(435, 55, 380, 400, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(625, 80, "Модель 2: SharedMemory / POSIX shm (Zero-Copy)", size=12, bold=True, color=FIELD))

    frags.append(fitbox(455, 105, 340, 65, "Процес 1 (Адресний простір 1)\nІніціалізація SharedMemory(create=True)\nСтворення numpy.ndarray над спільним буфером", size=10, fill="#ffffff", stroke=FIELD))
    frags.append(fitbox(455, 195, 340, 110, "Спільний сегмент пам'яті ОС (POSIX shm)\n/dev/shm або CreateFileMapping\nФізичні сторінки ОЗП відображені в таблиці\nсторінок обох процесів (Shared Page Table)\n[0 байтів копіювання, 0 накладних витрат]", size=10, fill="#ffffff", stroke=FIELD))
    frags.append(fitbox(455, 330, 340, 65, "Процес 2 (Адресний простір 2)\nПідключення SharedMemory(name=shm.name)\nПряме читання/запис без десеріалізації", size=10, fill="#ffffff", stroke=FIELD))
    frags.append(fitbox(455, 405, 340, 35, "Швидкодія: миттєвий доступ на швидкості ОЗП ⭐", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    frags.append(arrow(625, 170, 625, 195, color=FIELD, sw=1.5))
    frags.append(arrow(625, 305, 625, 330, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "multiprocessing-shared-memory.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_gil_architecture()
    fig_gil_thrashing()
    fig_shared_memory_ipc()
    print("Усі фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
