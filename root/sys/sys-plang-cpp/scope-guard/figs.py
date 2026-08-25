# -*- coding: utf-8 -*-
"""Фігури до теми «Охоронець області: відкат через деструктор»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HEAD = "#eceff3"
OK   = "#e8f6ee"
WARN = "#fff7e6"
HOT  = "#fdecea"


# ── 1. Розгортання стека: прямий порядок реєстрації та зворотний порядок відкату ──
def fig_scope_guard_unwinding():
    W, H = 1000, 520
    f = []

    # Заголовок лівої колонки (вхід) та правої (вихід)
    f.append(fitbox(50, 40, 420, 44, "Прямий хід: реєстрація дій (вхід у блок)", size=13, fill=HEAD, color=MUTED, bold=True))
    f.append(fitbox(530, 40, 420, 44, "Зворотний хід: спрацювання деструкторів (вихід)", size=13, fill=HEAD, color=MUTED, bold=True))

    # Ліва колонка: кроки реєстрації
    f.append(fitbox(50, 100, 420, 64, "1. Створено тимчасовий файл\n→ зареєстровано Guard 1: видалити файл", size=12, fill=BG))
    f.append(fitbox(50, 180, 420, 64, "2. Виділено системний буфер\n→ зареєстровано Guard 2: звільнити пам'ять", size=12, fill=BG))
    f.append(fitbox(50, 260, 420, 64, "3. Змінено прапорець транзакції\n→ зареєстровано Guard 3: скинути прапорець", size=12, fill=BG))
    f.append(fitbox(50, 340, 420, 64, "4. Збій мережі / кинуто виняток!\nОбчислення переривається, починається розгортання", size=12, fill=HOT, color=NEG, bold=True))

    # Стрілки зверху вниз для лівої колонки
    f.append(arrow(260, 164, 260, 180, color=FIELD))
    f.append(arrow(260, 244, 260, 260, color=FIELD))
    f.append(arrow(260, 324, 260, 340, color=NEG))

    # Права колонка: розгортання у зворотному порядку (LIFO)
    f.append(fitbox(530, 100, 420, 64, "Крок 3: ~Guard 1()\nВидалення тимчасового файлу з диска", size=12, fill=OK))
    f.append(fitbox(530, 180, 420, 64, "Крок 2: ~Guard 2()\nЗвільнення виділеної оперативної пам'яті", size=12, fill=OK))
    f.append(fitbox(530, 260, 420, 64, "Крок 1: ~Guard 3()\nВідновлення вихідного стану прапорця", size=12, fill=OK))
    f.append(fitbox(530, 340, 420, 64, "Початок розгортання стека (LIFO)\nДеструктори автоматичних об'єктів кличуться назад", size=12, fill=WARN, color=MUTED, bold=True))

    # Стрілки знизу вгору для правої колонки
    f.append(arrow(740, 340, 740, 324, color=POS))
    f.append(arrow(740, 260, 740, 244, color=POS))
    f.append(arrow(740, 180, 740, 164, color=POS))

    # Зв'язок між збоєм і початком розгортання
    f.append(arrow(470, 372, 530, 372, color=NEG))

    # Пояснювальний підпис внизу
    f.append(fitbox(50, 430, 900, 54, "Об'єкти на стеку знищуються у порядку, строго протилежному до їх створення.\nКожен охоронець скасовує рівно свій крок, гарантуючи повний відкат до вихідного стану.", size=12, fill=FILL, color=MUTED))

    render(os.path.join(OUT, 'scope-guard-unwinding.svg'), W, H, *f,
           title="Порядок виконання дій при розгортанні стека")


# ── 2. Лічильник std::uncaught_exceptions() і різновиди охоронців ─────────────
def fig_uncaught_exceptions_counter():
    W, H = 1000, 530
    f = []

    cols = [(50, 260, "Різновид охоронця"),
            (330, 340, "Умова спрацювання в деструкторі"),
            (690, 260, "Коли застосовується")]
    for x, w, name in cols:
        f.append(fitbox(x, 40, w, 44, name, size=13, fill=HEAD, color=MUTED, bold=True))

    rows = [
        (100, "SCOPE_EXIT\nstd::scope_exit", "uncaught_exceptions() >= 0\n(виконується ЗАВЖДИ, якщо активний)",
         "Звільнення ресурсів, зняття блокувань, закриття дескрипторів", OK),
        (200, "SCOPE_FAIL\nstd::scope_fail", "uncaught_exceptions() > uncaught_on_entry\n(лише коли вилітає НОВИЙ виняток)",
         "Відкат транзакції, видалення сміття після збою, запис логу помилки", HOT),
        (300, "SCOPE_SUCCESS\nstd::scope_success", "uncaught_exceptions() <= uncaught_on_entry\n(лише при УСПІШНОМУ виході)",
         "Фіксація транзакції (commit), оновлення кешу, сповіщення підписників", OK),
    ]
    for y, kind, cond, when, tint in rows:
        f.append(fitbox(50, y, 260, 80, kind, size=13, fill=BG, bold=True))
        f.append(fitbox(330, y, 340, 80, cond, size=12, fill=tint))
        f.append(fitbox(690, y, 260, 80, when, size=12, fill=FILL))

    f.append(fitbox(50, 410, 900, 80,
                    "Механізм C++17 std::uncaught_exceptions() повертає кількість активних винятків у поточному потоці.\n"
                    "Запам'ятовуючи це число під час конструювання, охоронець безпомилково розрізняє нормальний вихід\n"
                    "і розгортання стека навіть у разі вкладеної обробки помилок всередині деструкторів.",
                    size=12, fill=HEAD, color=INK))

    render(os.path.join(OUT, 'uncaught-exceptions-counter.svg'), W, H, *f,
           title="Різновиди охоронців та їхня логіка спрацювання")


# ── 3. std::unique_ptr проти scope_guard ─────────────────────────────────────
def fig_unique_ptr_vs_scope_guard():
    W, H = 1000, 540
    f = []

    cols = [(50, 220, "Критерій"),
            (290, 320, "std::unique_ptr<T, Deleter>"),
            (630, 320, "std::scope_exit<EF> / ScopeGuard")]
    for x, w, name in cols:
        f.append(fitbox(x, 40, w, 44, name, size=13, fill=HEAD, color=MUTED, bold=True))

    rows = [
        (100, "Що зберігає", "Вказівник або дескриптор ресурсу (T*)", "Довільний виконуваний об'єкт (лямбда, функтор)", FILL),
        (175, "У чому суть володіння", "Володіння дискретним об'єктом у пам'яті / ОС", "Керування виконанням відкладеної дії у потоці", FILL),
        (250, "Умова виклику очищення", "Вказівник не дорівнює nullptr", "Прапорець active == true (та стан винятків)", OK),
        (325, "Скасування / передача", "release() повертає T* і обнуляє поле", "release() / dismiss() скидає прапорець active", OK),
        (400, "Типове призначення", "Керування пам'яттю, файловими дескрипторами, сокетами", "Транзакційні відкати, зміна стану змінних, закриття блоків", WARN),
    ]
    for y, crit, uptr, sguard, tint in rows:
        f.append(fitbox(50, y, 220, 60, crit, size=12, fill=HEAD, bold=True))
        f.append(fitbox(290, y, 320, 60, uptr, size=12, fill=BG))
        f.append(fitbox(630, y, 320, 60, sguard, size=12, fill=tint))

    f.append(fitbox(50, 475, 900, 42,
                    "unique_ptr керує адресою об'єкта; scope_guard керує виконанням дії на межі області видимості.",
                    size=12, fill=FILL, color=MUTED))

    render(os.path.join(OUT, 'unique-ptr-vs-scope-guard.svg'), W, H, *f,
           title="Порівняння std::unique_ptr та scope_guard")


if __name__ == '__main__':
    fig_scope_guard_unwinding()
    fig_uncaught_exceptions_counter()
    fig_unique_ptr_vs_scope_guard()
    print("All figures generated successfully.")
