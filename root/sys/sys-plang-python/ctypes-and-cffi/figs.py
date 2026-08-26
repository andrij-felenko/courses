# -*- coding: utf-8 -*-
"""Генератор архітектурних діаграм для теми ctypes-and-cffi."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, text, mtext, line, arrow, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_ctypes_libffi():
    """Діаграма 1: Архітектура динамічного виклику ctypes через libffi."""
    w, h = 820, 480
    frags = []

    # Заголовок
    frags.append(text(410, 28, "Динамічний виклик ctypes: від об'єкта Python до машинних регістрів C", size=15, bold=True))

    # Стовпець 1: Рівень інтерпретатора Python
    frags.append(rect(30, 60, 220, 390, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(140, 85, "Простір Python (CPython)", size=13, bold=True, color=NEG))
    
    frags.append(fitbox(45, 110, 190, 65, "Python Objects\n(int, float, bytes, list)", size=12, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(45, 205, 190, 75, "ctypes Types Wrapper\n(c_int, c_double, POINTER)\nМаршалінг у C-структури", size=11, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(45, 310, 190, 65, "CDLL / WinDLL Object\nАдреса символу (dlsym)", size=12, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(45, 395, 190, 45, "Відпускання GIL\n(PyEval_SaveThread)", size=11, fill="#fef2f2", stroke=POS))

    # Стовпець 2: Механізм libffi
    frags.append(rect(290, 60, 240, 390, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(410, 85, "Ядро FFI (libffi)", size=13, bold=True, color=FIELD))

    frags.append(fitbox(305, 110, 210, 70, "ffi_cif (Call Interface)\n• Тип повернення\n• Масив типів аргументів\n• ABI (cdecl, sysv, win64)", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(305, 210, 210, 70, "ffi_prep_cif()\nРозрахунок зсувів, вирівнювання\nта розміру стекового кадру", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(305, 310, 210, 120, "ffi_call() / Трамплін\n1. Розкладка значень у регістри\n   (RDI, RSI, RDX, XMM0...)\n2. Запис залишку в стек процесу\n3. Машинна інструкція call", size=11, fill="#f0fdf4", stroke=FIELD))

    # Стовпець 3: Цільова нативна бібліотека
    frags.append(rect(570, 60, 220, 390, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(680, 85, "Нативна C/C++ бібліотека", size=13, bold=True, color=POS))

    frags.append(fitbox(585, 110, 190, 75, "Динамічна бібліотека\n.so / .dll / .dylib\n(Завантажена через dlopen)", size=12, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(585, 210, 190, 85, "Цільова C-функція\nВиконання нативного коду\nбез знання про Python\n(Апаратна швидкодія)", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(585, 325, 190, 105, "Повернення результату\nРегістри RAX / XMM0\n→ Конвертація у ffi_call\n→ Зворотний маршалінг\n→ Захоплення GIL", size=11, fill="#fef2f2", stroke=POS))

    # Стрілки між компонентами
    frags.append(arrow(140, 175, 140, 205, color=LINE, sw=1.5))
    frags.append(arrow(140, 280, 140, 310, color=LINE, sw=1.5))
    frags.append(arrow(140, 375, 140, 395, color=LINE, sw=1.5))

    frags.append(arrow(235, 245, 305, 245, color=LINE, sw=1.5))
    frags.append(arrow(410, 180, 410, 210, color=LINE, sw=1.5))
    frags.append(arrow(410, 280, 410, 310, color=LINE, sw=1.5))

    frags.append(arrow(515, 370, 585, 250, color=LINE, sw=1.8))
    frags.append(arrow(680, 295, 680, 325, color=LINE, sw=1.5))
    frags.append(arrow(585, 380, 235, 415, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "ctypes-libffi-call.svg"), w, h, *frags)


def fig_cffi_modes():
    """Діаграма 2: Порівняння 4 режимів cffi: ABI vs API, In-line vs Out-of-line."""
    w, h = 840, 500
    frags = []

    frags.append(text(420, 28, "Матриця архітектурних режимів cffi: ABI проти API", size=15, bold=True))

    # Заголовки колонок і рядків
    frags.append(fitbox(160, 55, 310, 35, "Режим ABI (двійковий інтерфейс / libffi)", size=12, bold=True, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(490, 55, 320, 35, "Режим API (компіляція C-коду розширення)", size=12, bold=True, fill="#f0fdf4", stroke=FIELD))

    frags.append(fitbox(20, 100, 120, 175, "In-line\n(Динамічно під\nчас імпорту)", size=12, bold=True, fill="#f8fafc", stroke=MUTED))
    frags.append(fitbox(20, 295, 120, 185, "Out-of-line\n(Попередня збірка\nу .whl / .so)", size=12, bold=True, fill="#f8fafc", stroke=MUTED))

    # Квадрант 1: ABI In-line
    frags.append(rect(160, 100, 310, 175, fill="#ffffff", stroke=NEG, sw=1.5))
    frags.append(text(315, 122, "ABI In-line (Швидкий прототип)", size=11, bold=True, color=NEG))
    frags.append(mtext(315, 148, "• ffi.cdef() парсить C-типи під час запуску\n• ffi.dlopen(\"lib.so\") динамічно вантажить бібліотеку\n• Виклики через динамічний libffi\n• Ризик: помилки розкладки структур при зсувах полів\n• Накладні витрати: 80–120 нс на виклик", size=10, anchor="middle", lh=1.35))

    # Квадрант 2: API In-line
    frags.append(rect(490, 100, 320, 175, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(650, 122, "API In-line (Рідкісний режим)", size=11, bold=True, color=FIELD))
    frags.append(mtext(650, 148, "• ffi.cdef() + ffi.set_source()\n• Викликає C-компілятор у фоні під час імпорту\n• Генерує тимчасовий C-extension модуль\n• Гарантує відповідність системним заголовкам\n• Мінус: затримка старту програми (компіляція)", size=10, anchor="middle", lh=1.35))

    # Квадрант 3: ABI Out-of-line
    frags.append(rect(160, 295, 310, 185, fill="#ffffff", stroke=NEG, sw=1.5))
    frags.append(text(315, 318, "ABI Out-of-line (Без компілятора C)", size=11, bold=True, color=NEG))
    frags.append(mtext(315, 344, "• Скрипт збірки компілює лише C-декларації у Python\n• Імпорт згенерованого модуля без парсингу cdef\n• ffi.dlopen() під час виконання\n• Плюс: не потребує gcc/clang на кінцевому сервері\n• Мінус: зберігаються накладні витрати libffi", size=10, anchor="middle", lh=1.35))

    # Квадрант 4: API Out-of-line
    frags.append(rect(490, 295, 320, 185, fill="#f0fdf4", stroke=FIELD, sw=2))
    frags.append(text(650, 318, "API Out-of-line (Промисловий еталон ⭐)", size=11, bold=True, color=FIELD))
    frags.append(mtext(650, 344, "• ffibuilder.compile() під час wheel-пакування\n• Генерує нативний C-код без посередництва libffi\n• Прямий виклик функцій через вказівники нативного C\n• Безпека: перевірка макросів, enum і struct компілятором\n• Максимальна швидкість: 5–15 нс на виклик", size=10, anchor="middle", lh=1.35))

    render(os.path.join(IMG_DIR, "cffi-modes-comparison.svg"), w, h, *frags)


def fig_memory_and_gil():
    """Діаграма 3: Керування пам'яттю, життєвий цикл з ffi.gc() та поведінка GIL."""
    w, h = 840, 470
    frags = []

    frags.append(text(420, 28, "Керування пам'яттю, протокол буфера та життєвий цикл GIL", size=15, bold=True))

    # Секція 1: Пам'ять Python та Нульове копіювання
    frags.append(rect(30, 60, 360, 385, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(210, 85, "Простір пам'яті Python і Zero-Copy", size=13, bold=True, color=NEG))

    frags.append(fitbox(45, 105, 330, 65, "Об'єкти Python з підтримкою буфера\nbytes, bytearray, memoryview, numpy.ndarray\n(У купі CPython, керованій GC)", size=11, fill="#eef2ff", stroke=NEG))
    
    frags.append(fitbox(45, 195, 330, 70, "ffi.from_buffer() / ctypes.from_buffer()\nПряме отримання сирого вказівника на пам'ять\nБЕЗ копіювання даних (Нульове копіювання / Zero-Copy)", size=11, fill="#f0fdf4", stroke=FIELD))
    
    frags.append(fitbox(45, 290, 330, 65, "Автоматичне очищення C-ресурсів\nptr = ffi.gc(c_alloc(), free_func)\nПрив'язка C-деструктора до фіналізатора Python", size=11, fill="#fef2f2", stroke=POS))

    frags.append(fitbox(45, 375, 330, 55, "Захист від Use-After-Free:\nffi.gc гарантує звільнення пам'яті лише коли\nвсі Python-посилання зникають", size=10, fill="#ffffff", stroke=MUTED))

    frags.append(arrow(210, 170, 210, 195, color=LINE, sw=1.5))
    frags.append(arrow(210, 265, 210, 290, color=LINE, sw=1.5))
    frags.append(arrow(210, 355, 210, 375, color=LINE, sw=1.5))

    # Секція 2: Потоки та GIL
    frags.append(rect(430, 60, 380, 385, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(620, 85, "Виконання C-коду та синхронізація GIL", size=13, bold=True, color=FIELD))

    frags.append(fitbox(445, 105, 350, 65, "1. Потік у Python (Володіє GIL)\nВиклик ffi_call або C-розширення\nПідготовка сирих аргументів C", size=11, fill="#eef2ff", stroke=NEG))

    frags.append(fitbox(445, 190, 350, 60, "2. Відпускання GIL: PyEval_SaveThread()\nІнші потоки Python вільно виконують байткод\nна інших ядрах процесора", size=11, fill="#fef2f2", stroke=POS))

    frags.append(fitbox(445, 270, 350, 65, "3. Обчислення в нативному C/C++ коді\nТривала математика, блокувальний I/O\nПаралельність на рівні ядра ОС", size=11, fill="#f0fdf4", stroke=FIELD))

    frags.append(fitbox(445, 355, 350, 75, "4. Повернення та захоплення GIL\nPyEval_RestoreThread()\n(У разі C-callback: PyGILState_Ensure()\nперед викликом Python-коду)", size=11, fill="#eef2ff", stroke=NEG))

    frags.append(arrow(620, 170, 620, 190, color=LINE, sw=1.5))
    frags.append(arrow(620, 250, 620, 270, color=LINE, sw=1.5))
    frags.append(arrow(620, 335, 620, 355, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "memory-and-gil-flow.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_ctypes_libffi()
    fig_cffi_modes()
    fig_memory_and_gil()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
