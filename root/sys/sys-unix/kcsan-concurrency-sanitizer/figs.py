# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#f8f9fa"
BORDER_GREY = "#b0bec5"
DARK_TEXT = "#263238"


def fig_kcsan_watchpoints():
    """Схема роботи механізму watchpoints та udelay затримки KCSAN."""
    W, H = 1200, 640
    p = []

    # Головний фоновий прямокутник
    p.append(rect(20, 20, 1160, 600, fill=GREY, stroke=BORDER_GREY, sw=1.5, rx=8))
    p.append(text(600, 55, "Механізм виявлення перегонів KCSAN (Watchpoint & Micro-Delay)", size=19, bold=True, color=DARK_TEXT))

    # Ліва частина: CPU 0 (Потік A)
    p.append(rect(50, 90, 350, 480, fill="#ffffff", stroke="#1565c0", sw=2, rx=6))
    p.append(rect(50, 90, 350, 45, fill="#bbdefb", stroke="#1565c0", sw=1.5, rx=6))
    p.append(text(225, 118, "CPU 0 (Потік A: Запис)", size=16, bold=True, color="#0d47a1"))

    p.append(rect(70, 150, 310, 55, fill="#e3f2fd", stroke="#1976d2", sw=1, rx=4))
    p.append(text(225, 172, "1. Доступ: *ptr = val", size=14, bold=True))
    p.append(text(225, 192, "Викликається __tsan_write4(ptr)", size=12, color="#1565c0"))

    p.append(rect(70, 220, 310, 65, fill="#bbdefb", stroke="#1565c0", sw=1, rx=4))
    p.append(text(225, 242, "2. Вибір за семплюванням", size=14, bold=True))
    p.append(text(225, 265, "Слот хеш-таблиці = hash(ptr)", size=12, color="#0d47a1"))

    p.append(rect(70, 300, 310, 75, fill="#fff9c4", stroke="#fbc02d", sw=1.5, rx=4))
    p.append(text(225, 323, "3. Активація Watchpoint", size=14, bold=True, color="#f57f17"))
    p.append(text(225, 345, "Запис [Addr|Size|WriteBit|ThreadID]", size=12, color="#f57f17"))
    p.append(text(225, 363, "у kcsan_watchpoints[slot]", size=11, color="#f57f17"))

    p.append(rect(70, 390, 310, 85, fill="#ffe0b2", stroke="#f57c00", sw=1.5, rx=4))
    p.append(text(225, 413, "4. Штучна затримка (udelay)", size=14, bold=True, color="#e65100"))
    p.append(text(225, 435, "Пауза ~80 мкс на CPU 0", size=13, bold=True, color="#e65100"))
    p.append(text(225, 458, "Розширення вікна перегонів!", size=12, color="#bf360c"))

    p.append(rect(70, 490, 310, 60, fill="#e8f5e9", stroke="#388e3c", sw=1, rx=4))
    p.append(text(225, 513, "5. Реальне виконання *ptr = val", size=13, bold=True, color="#1b5e20"))
    p.append(text(225, 533, "Очищення слота watchpoint", size=12, color="#2e7d32"))

    # Центральна частина: Хеш-таблиця Watchpoints
    p.append(rect(430, 90, 340, 480, fill="#ffffff", stroke="#7b1fa2", sw=2, rx=6))
    p.append(rect(430, 90, 340, 45, fill="#e1bee7", stroke="#7b1fa2", sw=1.5, rx=6))
    p.append(text(600, 118, "Таблиця KCSAN Watchpoints", size=16, bold=True, color="#4a148c"))

    p.append(rect(450, 150, 300, 45, fill="#f3e5f5", stroke="#8e24aa", sw=1, rx=4))
    p.append(text(600, 173, "Слот 0: [ Порожньо ]", size=13, color="#6a1b9a"))

    p.append(rect(450, 205, 300, 75, fill="#fff3e0", stroke="#e65100", sw=2, rx=4))
    p.append(text(600, 227, "Слот Hash(ptr): [ АКТИВНИЙ ]", size=14, bold=True, color="#e65100"))
    p.append(text(600, 248, "Адреса = ptr | Розмір = 4 B", size=12, color="#bf360c"))
    p.append(text(600, 266, "Тип = WRITE | CPU = 0", size=11, color="#bf360c"))

    p.append(rect(450, 290, 300, 40, fill="#f3e5f5", stroke="#8e24aa", sw=1, rx=4))
    p.append(text(470, 314, "Слот N: [ Порожньо ]", size=12, color="#6a1b9a", anchor="start"))

    p.append(rect(450, 350, 300, 200, fill=RED, stroke="#c62828", sw=2, rx=4))
    p.append(text(600, 375, "РЕЄСТРАЦІЯ СТАНУ ПЕРЕГОНІВ", size=14, bold=True, color="#b71c1c"))
    p.append(text(600, 403, "Збіг адреси: ptr == ptr", size=13, bold=True, color="#c62828"))
    p.append(text(600, 428, "Умова: Хоча б 1 доступ = WRITE", size=12, color="#b71c1c"))
    p.append(text(600, 453, "Отримано стеки викликів:", size=13, bold=True, color="#263238"))
    p.append(text(600, 478, "• CPU 0: update_counter+0x12", size=12, color="#37474f"))
    p.append(text(600, 498, "• CPU 1: read_counter+0x08", size=12, color="#37474f"))
    p.append(text(600, 520, "Дамп dmesg / kcsan report", size=12, bold=True, color="#b71c1c"))

    # Права частина: CPU 1 (Потік B)
    p.append(rect(800, 90, 350, 480, fill="#ffffff", stroke="#c62828", sw=2, rx=6))
    p.append(rect(800, 90, 350, 45, fill="#ffcdd2", stroke="#c62828", sw=1.5, rx=6))
    p.append(text(975, 118, "CPU 1 (Потік B: Читання/Запис)", size=16, bold=True, color="#b71c1c"))

    p.append(rect(820, 150, 310, 55, fill="#ffebee", stroke="#e53935", sw=1, rx=4))
    p.append(text(975, 172, "1. Одночасний доступ: r = *ptr", size=14, bold=True))
    p.append(text(975, 192, "Викликається __tsan_read4(ptr)", size=12, color="#c62828"))

    p.append(rect(820, 220, 310, 75, fill="#ffcdd2", stroke="#d32f2f", sw=1.5, rx=4))
    p.append(text(975, 243, "2. Перевірка Watchpoint-ів", size=14, bold=True, color="#b71c1c"))
    p.append(text(975, 265, "Пошук ptr у kcsan_watchpoints", size=12, color="#b71c1c"))
    p.append(text(975, 283, "Збіг знайдено під час udelay!", size=12, bold=True, color="#b71c1c"))

    p.append(rect(820, 310, 310, 75, fill="#fdecea", stroke="#c62828", sw=1.5, rx=4))
    p.append(text(975, 333, "3. Фіксація Конфлікту", size=14, bold=True, color="#b71c1c"))
    p.append(text(975, 355, "Формування двох стек-трейсів", size=12, color="#b71c1c"))
    p.append(text(975, 373, "Виклик kcsan_report()", size=12, bold=True, color="#b71c1c"))

    p.append(rect(820, 400, 310, 150, fill="#f5f5f5", stroke="#757575", sw=1, rx=4))
    p.append(text(975, 425, "Результат для розробника:", size=13, bold=True))
    p.append(text(975, 450, "Звіт у dmesg деталізує:", size=12, color="#424242"))
    p.append(text(975, 475, "1) Яку саме змінну зачеплено", size=12, color="#212121"))
    p.append(text(975, 498, "2) Які функції виконувалися", size=12, color="#212121"))
    p.append(text(975, 520, "3) Рекомендація: READ_ONCE", size=12, bold=True, color="#2e7d32"))

    # Стрілки
    p.append(arrow(380, 335, 450, 240, color="#f57c00", sw=2))
    p.append(arrow(820, 255, 750, 240, color="#c62828", sw=2))
    # Стрілка від активного слота до блоку реєстрації по правому краю х=720
    p.append(arrow(710, 280, 710, 350, color="#b71c1c", sw=2))

    render(os.path.join(IMG, 'kcsan-watchpoints.svg'), W, H, *p)


def fig_kcsan_architecture():
    """Схема архітектури інструментування компілятора та підсистеми KCSAN."""
    W, H = 1200, 600
    p = []

    # Головний контейнер
    p.append(rect(20, 20, 1160, 560, fill=GREY, stroke=BORDER_GREY, sw=1.5, rx=8))
    p.append(text(600, 55, "Архітектура інструментування коду та обробки доступів KCSAN", size=19, bold=True, color=DARK_TEXT))

    # Стовпчик 1: Початковий код і компілятор
    p.append(rect(50, 90, 340, 460, fill="#ffffff", stroke="#1565c0", sw=2, rx=6))
    p.append(rect(50, 90, 340, 45, fill="#bbdefb", stroke="#1565c0", sw=1.5, rx=6))
    p.append(text(220, 118, "Код ядра & Компілятор", size=16, bold=True, color="#0d47a1"))

    p.append(rect(70, 150, 300, 80, fill="#e3f2fd", stroke="#1976d2", sw=1, rx=4))
    p.append(text(220, 175, "Сирцевий C-код ядра", size=14, bold=True))
    p.append(text(220, 198, "• *ptr = val  (звичний доступ)", size=12, color="#1565c0"))
    p.append(text(220, 216, "• READ_ONCE(v), WRITE_ONCE(v)", size=12, color="#2e7d32"))

    p.append(rect(70, 250, 300, 100, fill="#e8eaf6", stroke="#3f51b5", sw=1, rx=4))
    p.append(text(220, 275, "GCC / Clang Plugin", size=14, bold=True, color="#1a237e"))
    p.append(text(220, 298, "-fsanitize=kernel-concurrency", size=12, color="#283593"))
    p.append(text(220, 318, "Автоматична вставка викликів", size=12, color="#283593"))
    p.append(text(220, 336, "__tsan_read* / __tsan_write*", size=12, bold=True, color="#1a237e"))

    p.append(rect(70, 370, 300, 160, fill="#f5f5f5", stroke="#616161", sw=1, rx=4))
    p.append(text(220, 395, "Генерований машинний код", size=14, bold=True))
    p.append(text(220, 420, "push rbp", size=12, color="#424242"))
    p.append(text(220, 440, "call __tsan_write4", size=12, bold=True, color="#c62828"))
    p.append(text(220, 460, "mov [rdi], eax", size=12, color="#424242"))
    p.append(text(220, 480, "pop rbp", size=12, color="#424242"))
    p.append(text(220, 505, "Кожен доступ проходить перевірку", size=11, color="#616161"))

    # Стовпчик 2: Ядро KCSAN (lib/kcsan/core.c)
    p.append(rect(430, 90, 340, 460, fill="#ffffff", stroke="#2e7d32", sw=2, rx=6))
    p.append(rect(430, 90, 340, 45, fill="#c8e6c9", stroke="#2e7d32", sw=1.5, rx=6))
    p.append(text(600, 118, "Підсистема KCSAN Core", size=16, bold=True, color="#1b5e20"))

    p.append(rect(450, 150, 300, 75, fill="#e8f5e9", stroke="#388e3c", sw=1, rx=4))
    p.append(text(600, 173, "kcsan_check_access()", size=14, bold=True, color="#1b5e20"))
    p.append(text(600, 195, "Швидкий фільтр лічильника", size=12, color="#2e7d32"))
    p.append(text(600, 213, "Семплювання 1 на N доступів", size=12, color="#2e7d32"))

    p.append(rect(450, 240, 300, 90, fill="#fff3e0", stroke="#f57c00", sw=1, rx=4))
    p.append(text(600, 263, "Перевірка Активних Вставка", size=14, bold=True, color="#e65100"))
    p.append(text(600, 285, "1) Встановлення watchpoint-а", size=12, color="#bf360c"))
    p.append(text(600, 305, "2) Запуск udelay() за потреби", size=12, color="#bf360c"))
    p.append(text(600, 320, "3) Порівняння значень (Value Change)", size=11, color="#bf360c"))

    p.append(rect(450, 345, 300, 185, fill="#ede7f6", stroke="#512da8", sw=1, rx=4))
    p.append(text(600, 370, "Анотації та Пропущення", size=14, bold=True, color="#311b92"))
    p.append(text(600, 395, "• data_race(...) -> пропуск", size=12, color="#4527a0"))
    p.append(text(600, 418, "• kcsan_disable_current()", size=12, color="#4527a0"))
    p.append(text(600, 440, "• ASSERT_EXCLUSIVE_WRITER()", size=12, bold=True, color="#283593"))
    p.append(text(600, 463, "• ASSERT_EXCLUSIVE_ACCESS()", size=12, bold=True, color="#283593"))
    p.append(text(600, 488, "Захист від false positives!", size=12, bold=True, color="#1b5e20"))

    # Стовпчик 3: Звітність і системні інтерфейси
    p.append(rect(810, 90, 340, 460, fill="#ffffff", stroke="#c62828", sw=2, rx=6))
    p.append(rect(810, 90, 340, 45, fill="#ffcdd2", stroke="#c62828", sw=1.5, rx=6))
    p.append(text(980, 118, "Звітність & Налаштування", size=16, bold=True, color="#b71c1c"))

    p.append(rect(830, 150, 300, 110, fill="#ffebee", stroke="#d32f2f", sw=1, rx=4))
    p.append(text(980, 175, "kcsan_report() Engine", size=14, bold=True, color="#b71c1c"))
    p.append(text(980, 198, "• Збір двох журналів unwind", size=12, color="#c62828"))
    p.append(text(980, 218, "• Друкування розгортки dmesg", size=12, color="#c62828"))
    p.append(text(980, 240, "• Рапортування через printk()", size=12, color="#c62828"))

    p.append(rect(830, 275, 300, 120, fill="#fff8e1", stroke="#ffa000", sw=1, rx=4))
    p.append(text(980, 300, "Sysfs / Boot parameters", size=14, bold=True, color="#ff6f00"))
    p.append(text(980, 323, "/sys/module/kcsan/parameters/", size=12, color="#ff6f00"))
    p.append(text(980, 345, "• udelay_task, udelay_interrupt", size=11, color="#424242"))
    p.append(text(980, 365, "• skip_watchpoints, verbose", size=11, color="#424242"))

    p.append(rect(830, 410, 300, 120, fill="#e0f2f1", stroke="#00897b", sw=1, rx=4))
    p.append(text(980, 435, "Інтеграція з KUnit", size=14, bold=True, color="#004d40"))
    p.append(text(980, 460, "lib/kcsan/kcsan-test.c", size=12, color="#00695c"))
    p.append(text(980, 483, "Автоматичні тести макросів", size=12, color="#00695c"))
    p.append(text(980, 505, "Перевірка під час CI/CD ядра", size=12, bold=True, color="#004d40"))

    # Стрілки
    p.append(arrow(370, 300, 450, 190, color="#1976d2", sw=2))
    p.append(arrow(750, 190, 830, 190, color="#2e7d32", sw=2))
    p.append(arrow(750, 310, 830, 330, color="#f57c00", sw=2))

    render(os.path.join(IMG, 'kcsan-architecture.svg'), W, H, *p)


if __name__ == "__main__":
    fig_kcsan_watchpoints()
    fig_kcsan_architecture()
    print("Successfully generated KCSAN figures in ./img/")
