# -*- coding: utf-8 -*-
"""Фігури до теми «thread_local: стан, приватний для потоку»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Фізична розкладка пам'яті TLS: TCB, сегментний регістр FS та секції .tdata/.tbss ──
def fig_tls_memory_layout():
    W, H = 940, 480
    f = []

    f.append(text(470, 30, "Фізична організація пам'яті Thread-Local Storage (TLS) в x86-64 / ELF", size=16, color=INK, anchor="middle", bold=True))

    # Спільний образ бінарного модуля (ELF Binary / Shared Object)
    f.append(text(210, 65, "Шаблон ініціалізації у файлі ELF", size=13, color=MUTED, bold=True))
    f.append(fitbox(40, 80, 340, 60, "Секція .tdata (ініціалізовані TLS-змінні)\nКопіюється як байтовий зліпок у кожен новий потік", size=11, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(40, 150, 340, 60, "Секція .tbss (неініціалізовані TLS-змінні)\nРезервує розмір у RAM; занулюється при створенні потоку", size=11, fill="#f4f6f8", stroke=LINE))

    # Системний виклик clone / створення потоку
    f.append(arrow(380, 145, 480, 145, color=FIELD, sw=2))
    f.append(text(430, 135, "pthread_create()", size=10, color=FIELD, bold=True))

    # Потік 1 (Thread 1)
    f.append(text(690, 65, "Пам'ять Потоку 1 (Thread 1 Context)", size=13, color=NEG, bold=True))
    f.append(fitbox(500, 80, 380, 50, "Статичний TLS-блок: Зліпок .tdata + Занулений .tbss\n[ thread_local int counter = 42; ] (Адреса = %fs:offset)", size=11, fill="#e8f4fc", stroke=NEG))
    f.append(fitbox(500, 140, 380, 50, "TCB (Thread Control Block) та Thread Pointer (TP)\nСегментний регістр %fs вказує на базу TCB потоку 1", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(500, 200, 380, 50, "DTV (Dynamic Thread Vector)\nМасив вказівників на динамічні TLS-модулі (dlopen)", size=11, fill="#fef5e7", stroke=POS))

    # Зв'язок регістру FS
    f.append(line(500, 165, 460, 165, color=FIELD, sw=2))
    f.append(line(460, 165, 460, 105, color=FIELD, sw=2))
    f.append(arrow(460, 105, 495, 105, color=FIELD, sw=2))
    f.append(text(430, 95, "%fs:offset", size=10, color=FIELD, bold=True))

    # Потік 2 (Thread 2) - незалежна копія
    f.append(text(690, 280, "Пам'ять Потоку 2 (Thread 2 Context)", size=13, color=POS, bold=True))
    f.append(fitbox(500, 295, 380, 50, "Ізольований TLS-блок: Окремий зліпок .tdata + .tbss\n[ counter = 42 ] (Зміна в Потоці 1 не впливає на Потік 2)", size=11, fill="#fff0f0", stroke=POS))
    f.append(fitbox(500, 355, 380, 50, "TCB Потоку 2: Сегментний регістр %fs потоку 2\nВказує на незалежну фізичну сторінку пам'яті", size=11, fill="#e8f6ee", stroke=FIELD))

    # Підсумок ізоляції
    f.append(fitbox(40, 420, 860, 45, "Ключовий принцип: Кожен потік володіє власним TCB та унікальним зміщенням у регістрі %fs / %gs.\nНульові блокування (Lock-Free) та відсутність кеш-контеншну між ядрами CPU.", size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'tls-memory-layout.svg'), W, H, *f, title="Фізична організація пам'яті TLS")


# ── 2. Чотири моделі адресації TLS у компіляторах та ELF ─────────────────────
def fig_tls_access_models():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Моделі адресації Thread-Local Storage (ELF / x86-64)", size=16, color=INK, anchor="middle", bold=True))

    # Стовпчик 1: Local Exec
    f.append(fitbox(40, 65, 200, 60, "Local Exec (LE)\n-ftls-model=local-exec", size=12, fill="#e8f6ee", stroke=FIELD, bold=True))
    f.append(fitbox(40, 135, 200, 180, "Де застосовується:\nВиконуваний файл (main binary),\nсимвол не експортується назовні.\n\nАсемблерний код (1 інструкція):\nmovq %fs:-32, %rax\n\nЦіна доступу:\nНайшвидша (0 викликів функцій,\n0 звернень до таблиці GOT)", size=10, fill="#f4f6f8", stroke=LINE))

    # Стовпчик 2: Initial Exec
    f.append(fitbox(260, 65, 200, 60, "Initial Exec (IE)\n-ftls-model=initial-exec", size=12, fill="#e8f4fc", stroke=NEG, bold=True))
    f.append(fitbox(260, 135, 200, 180, "Де застосовується:\nСпільні бібліотеки (.so),\nзавантажені при старті програми.\n\nАсемблерний код (2 інструкції):\nmovq var@gottpoff(%rip), %rax\nmovq %fs:(%rax), %rax\n\nЦіна доступу:\n1 непряме читання з GOT,\nбез виклику runtime-функції", size=10, fill="#f4f6f8", stroke=LINE))

    # Стовпчик 3: Local Dynamic
    f.append(fitbox(480, 65, 200, 60, "Local Dynamic (LD)\n-ftls-model=local-dynamic", size=12, fill="#fef5e7", stroke=POS, bold=True))
    f.append(fitbox(480, 135, 200, 180, "Де застосовується:\nСпільні бібліотеки (.so) з кількома\nлокальними TLS-змінними.\n\nАсемблерний код:\nleaq var@tlsld(%rip), %rdi\ncall __tls_get_addr@PLT\nleaq var@dtpoff(%rax), %rcx\n\nЦіна доступу:\n1 виклик на модуль, зміщення\nдо змінних обчислюються локально", size=10, fill="#f4f6f8", stroke=LINE))

    # Стовпчик 4: General Dynamic
    f.append(fitbox(700, 65, 200, 60, "General Dynamic (GD)\n-ftls-model=global-dynamic", size=12, fill="#fff0f0", stroke=POS, bold=True))
    f.append(fitbox(700, 135, 200, 180, "Де застосовується:\nЕкспортовані символи бібліотек,\nзавантаження через dlopen().\n\nАсемблерний код:\nleaq var@tlsgd(%rip), %rdi\ncall __tls_get_addr@PLT\nmovq (%rax), %rax\n\nЦіна доступу:\nНайповільніша (повний виклик\n__tls_get_addr на кожне звернення)", size=10, fill="#f4f6f8", stroke=LINE))

    # Шкала продуктивності
    f.append(fitbox(40, 335, 860, 45, "Linker Relaxation: При статичній лінковці компонувальник автоматично оптимізує GD ──► IE ──► LE", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(40, 390, 860, 45, "Продуктивність: Local Exec (1 такт CPU)  ◄────────  General Dynamic (десятки тактів + виклик функції)", size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'tls-access-models.svg'), W, H, *f, title="Моделі адресації TLS в ELF")


# ── 3. Життєвий цикл thread_local: Ініціалізація та деструкція через __cxa_thread_atexit ──
def fig_thread_local_lifecycle():
    W, H = 940, 440
    f = []

    f.append(text(470, 30, "Життєвий цикл thread_local об'єкта: від виділення до деструктора", size=16, color=INK, anchor="middle", bold=True))

    # Стадія 1: Створення потоку
    f.append(fitbox(40, 70, 240, 80, "1. Створення потоку ОС\npthread_create() / std::jthread\n\nВиділення пам'яті під TCB\nта статичний сегмент TLS", size=11, fill="#e8f4fc", stroke=NEG))

    f.append(arrow(280, 110, 340, 110, color=NEG, sw=2))

    # Стадія 2: Ініціалізація (розгалуження)
    f.append(fitbox(340, 70, 260, 80, "2. Ініціалізація змінної\n\nconstinit: миттєво при старті\nДинамічна: ліниво при першому\nзверненні потоку (__tls_guard)", size=11, fill="#fef5e7", stroke=POS))

    f.append(arrow(600, 110, 660, 110, color=FIELD, sw=2))

    # Стадія 3: Реєстрація деструктора
    f.append(fitbox(660, 70, 240, 80, "3. Реєстрація деструктора\n\n__cxa_thread_atexit(\n  ~MyClass,\n  &instance,\n  &__dso_handle\n)", size=11, fill="#e8f6ee", stroke=FIELD))

    # Стрілка вниз до роботи
    f.append(arrow(780, 150, 780, 190, color=FIELD, sw=2))

    # Стадія 4: Робота потоку
    f.append(fitbox(500, 190, 380, 60, "4. Активна робота потоку\nЧитання та запис у thread_local змінну\nПовна ізоляція: 0 блокувань, 0 гонок даних", size=11, fill="#f4f6f8", stroke=LINE))

    # Стрілка вниз до завершення потоку
    f.append(arrow(690, 250, 690, 290, color=POS, sw=2))

    # Стадія 5: Завершення потоку та деструкція
    f.append(fitbox(40, 290, 840, 70, "5. Завершення виконання функції потоку (Thread Exit)\n\nC++ Runtime розгортає внутрішній список зареєстрованих деструкторів:\nВиклик деструкторів у ЗВОРОТНОМУ порядку створення  ──►  Звільнення TLS-пам'яті ОС", size=11, fill="#fff0f0", stroke=POS))

    # Попередження про пастки
    f.append(fitbox(40, 375, 840, 45, "Увага: std::exit() НЕ викликає деструктори thread_local для інших потоків! Тільки завершення функції потоку гарантує очищення.", size=11, fill="#fef5e7", stroke=POS))

    render(os.path.join(OUT, 'thread-local-lifecycle.svg'), W, H, *f, title="Життєвий цикл thread_local")


def main():
    fig_tls_memory_layout()
    fig_tls_access_models()
    fig_thread_local_lifecycle()
    print("Усі фігури для thread-local успішно згенеровано у", OUT)

if __name__ == '__main__':
    main()
