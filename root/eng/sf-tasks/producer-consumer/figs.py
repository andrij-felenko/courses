# -*- coding: utf-8 -*-
"""Фігури до теми «Патерн Виробник–Споживач (Producer–Consumer)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей
PROD_FILL   = "#eaf2fd"
PROD_LINE   = "#2457d6"
CONS_FILL   = "#fef5e7"
CONS_LINE   = "#d35400"
QUEUE_FILL  = "#eafaf1"
QUEUE_LINE  = "#27ae60"
SLOT_FILL   = "#2ecc71"
EMPTY_FILL  = "#f4f6f8"
SYNC_FILL   = "#fdf2e9"
SYNC_LINE   = "#e67e22"
WARN_FILL   = "#fff6e0"
WARN_LINE   = "#caa24a"
FAIL_FILL   = "#fdecea"
FAIL_LINE   = "#c0392b"
CACHE_FILL  = "#f3e5f5"
CACHE_LINE  = "#8e24aa"

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5, rx=6):
    """Прямокутник із підписом по центру; багаторядковий через список або \\n."""
    if isinstance(s, str) and "\n" in s:
        s = s.split("\n")
    if isinstance(s, list):
        f.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, sw=sw, color=tcol, rx=rx))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx))
    fs = fit_font(s, w - 14, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))

def note(f, cx, y, w, lines, fill=WARN_FILL, stroke=WARN_LINE, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.35 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ── 1. Архітектура Виробник–Споживач ───────────────────────────────────────────
def fig_producer_consumer_architecture():
    W, H = 900, 430
    f = [text(W / 2, 28, "Архітектура патерну Виробник–Споживач з обмеженим буфером", size=16, bold=True)]
    f.append(text(W / 2, 48, "Розрив часової та просторової залежності між генерацією та обробкою даних",
                  size=11, color=MUTED, italic=True))

    # Виробники (зліва)
    f.append(rect(25, 75, 175, 260, fill="#f8faff", stroke=PROD_LINE, sw=1.8, rx=8))
    f.append(text(112, 100, "Виробники (Producers)", size=12, color=PROD_LINE, bold=True))
    f.append(text(112, 116, "Генерація задач / даних", size=10, color=MUTED))

    boxlabel(f, 40, 135, 145, 45, ["Потік Виробник #1", "push(item)"], fill=PROD_FILL, stroke=PROD_LINE, size=10, tcol=PROD_LINE)
    boxlabel(f, 40, 195, 145, 45, ["Потік Виробник #2", "push(item)"], fill=PROD_FILL, stroke=PROD_LINE, size=10, tcol=PROD_LINE)
    boxlabel(f, 40, 255, 145, 45, ["Потік Виробник #3", "push(item)"], fill=PROD_FILL, stroke=PROD_LINE, size=10, tcol=PROD_LINE)

    # Спільний буфер (посередині)
    f.append(rect(235, 75, 430, 260, fill="#f9fbf9", stroke=QUEUE_LINE, sw=2, rx=10))
    f.append(text(450, 100, "Спільний обмежений буфер (Bounded Queue FIFO)", size=13, color=QUEUE_LINE, bold=True))
    f.append(text(450, 118, "Ємність K елементів • Синхронізована черга", size=10, color=MUTED))

    # Комірки буфера
    slot_w, slot_h = 48, 55
    start_x, start_y = 265, 145
    slots_data = [
        ("0", "Зайнято", "#d5f5e3", QUEUE_LINE),
        ("1", "Зайнято", "#d5f5e3", QUEUE_LINE),
        ("2", "Зайнято", "#d5f5e3", QUEUE_LINE),
        ("3", "Зайнято", "#d5f5e3", QUEUE_LINE),
        ("4", "Вільно", "#f4f6f8", MUTED),
        ("5", "Вільно", "#f4f6f8", MUTED),
        ("6", "Вільно", "#f4f6f8", MUTED),
    ]

    for i, (idx, state, fill_c, stroke_c) in enumerate(slots_data):
        sx = start_x + i * (slot_w + 6)
        f.append(rect(sx, start_y, slot_w, slot_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=4))
        f.append(text(sx + slot_w / 2, start_y + 22, f"[{idx}]", size=10, color=INK, bold=True))
        f.append(text(sx + slot_w / 2, start_y + 42, state, size=9, color=stroke_c))

    # Покажчики Head і Tail
    f.append(arrow(start_x + 24, start_y - 20, start_x + 24, start_y - 3, color=CONS_LINE, sw=1.8))
    f.append(text(start_x + 24, start_y - 25, "head (вилучення)", size=10, color=CONS_LINE, bold=True))

    f.append(arrow(start_x + 4 * (slot_w + 6) + 24, start_y + slot_h + 20, start_x + 4 * (slot_w + 6) + 24, start_y + slot_h + 3, color=PROD_LINE, sw=1.8))
    f.append(text(start_x + 4 * (slot_w + 6) + 24, start_y + slot_h + 32, "tail (запис)", size=10, color=PROD_LINE, bold=True))

    # Блок синхронізації
    f.append(rect(255, 255, 390, 65, fill=SYNC_FILL, stroke=SYNC_LINE, sw=1.5, rx=6))
    f.append(text(450, 273, "Примітиви координації стану", size=11, color=SYNC_LINE, bold=True))
    f.append(text(320, 298, "м'ютекс: захист черги", size=9.5, color=INK))
    f.append(text(450, 298, "cv not_empty: є дані", size=9.5, color=CONS_LINE, bold=True))
    f.append(text(575, 298, "cv not_full: є місце", size=9.5, color=PROD_LINE, bold=True))

    # Споживачі (справа)
    f.append(rect(700, 75, 175, 260, fill="#fffaf5", stroke=CONS_LINE, sw=1.8, rx=8))
    f.append(text(787, 100, "Споживачі (Consumers)", size=12, color=CONS_LINE, bold=True))
    f.append(text(787, 116, "Паралельна обробка", size=10, color=MUTED))

    boxlabel(f, 715, 135, 145, 45, ["Потік Споживач #1", "item = pop()"], fill=CONS_FILL, stroke=CONS_LINE, size=10, tcol=CONS_LINE)
    boxlabel(f, 715, 195, 145, 45, ["Потік Споживач #2", "item = pop()"], fill=CONS_FILL, stroke=CONS_LINE, size=10, tcol=CONS_LINE)
    boxlabel(f, 715, 255, 145, 45, ["Потік Споживач #3", "item = pop()"], fill=CONS_FILL, stroke=CONS_LINE, size=10, tcol=CONS_LINE)

    # Стрілки передачі
    f.append(arrow(200, 180, 233, 180, color=PROD_LINE, sw=2))
    f.append(arrow(665, 180, 698, 180, color=CONS_LINE, sw=2))

    note(f, W / 2, 355, 840,
         ["Буфер розв'язує пікові коливання навантаження: виробник не чекає завершення обробки,",
          "а споживач засинає на умовній змінній not_empty за відсутності нових задач без витрат CPU."])
    render(os.path.join(IMG, "producer-consumer-architecture.svg"), W, H, *f)


# ── 2. Неблокувальний кільцевий буфер SPSC ─────────────────────────────────────
def fig_lock_free_spsc_ring():
    W, H = 900, 440
    f = [text(W / 2, 28, "Будова неблокувального кільцевого буфера SPSC (Lock-Free)", size=16, bold=True)]
    f.append(text(W / 2, 48, "Окремі кеш-лінії по 64 байти усувають False Sharing між ядрами процесора",
                  size=11, color=MUTED, italic=True))

    # Ліва кеш-лінія: Виробник (Tail)
    f.append(rect(30, 80, 245, 245, fill="#f8faff", stroke=PROD_LINE, sw=1.8, rx=8))
    f.append(text(152, 105, "Кеш-лінія Виробника (64 B)", size=11.5, color=PROD_LINE, bold=True))
    f.append(text(152, 122, "alignas(64) • Ядро CPU 0", size=10, color=MUTED))

    boxlabel(f, 45, 140, 215, 48, ["atomic<size_t> tail", "Індекс запису (мутує)"], fill=PROD_FILL, stroke=PROD_LINE, size=10.5, tcol=PROD_LINE)
    boxlabel(f, 45, 205, 215, 48, ["size_t cached_head", "Локальна копія head (кеш)"], fill="#ffffff", stroke=LINE, size=10)
    f.append(text(152, 285, "Оновлює tail через release", size=10, color=PROD_LINE, bold=True))
    f.append(text(152, 303, "Читає head лише коли буфер повний", size=9.5, color=MUTED))

    # Центр: Кільцевий масив у спільній пам'яті
    f.append(rect(305, 80, 290, 245, fill=QUEUE_FILL, stroke=QUEUE_LINE, sw=2, rx=8))
    f.append(text(450, 105, "Кільцевий масив слотів", size=12, color=QUEUE_LINE, bold=True))
    f.append(text(450, 122, "T buffer[N] • N = 2^k (побітова маска)", size=10, color=MUTED))

    # Слоти масиву
    slots = ["Slot 0", "Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5"]
    for i, sname in enumerate(slots):
        row = i // 2
        col = i % 2
        bx = 325 + col * 125
        by = 145 + row * 45
        is_occupied = (i >= 1 and i <= 3)
        fill_c = "#d5f5e3" if is_occupied else "#ffffff"
        strk_c = QUEUE_LINE if is_occupied else MUTED
        status = "Дані" if is_occupied else "Вільно"
        boxlabel(f, bx, by, 115, 36, [sname, status], fill=fill_c, stroke=strk_c, size=9.5)

    f.append(text(450, 295, "Індексація: i = tail & (N - 1)", size=10.5, color=QUEUE_LINE, bold=True))

    # Права кеш-лінія: Споживач (Head)
    f.append(rect(625, 80, 245, 245, fill="#fffaf5", stroke=CONS_LINE, sw=1.8, rx=8))
    f.append(text(747, 105, "Кеш-лінія Споживача (64 B)", size=11.5, color=CONS_LINE, bold=True))
    f.append(text(747, 122, "alignas(64) • Ядро CPU 1", size=10, color=MUTED))

    boxlabel(f, 640, 140, 215, 48, ["atomic<size_t> head", "Індекс читання (мутує)"], fill=CONS_FILL, stroke=CONS_LINE, size=10.5, tcol=CONS_LINE)
    boxlabel(f, 640, 205, 215, 48, ["size_t cached_tail", "Локальна копія tail (кеш)"], fill="#ffffff", stroke=LINE, size=10)
    f.append(text(747, 285, "Оновлює head через release", size=10, color=CONS_LINE, bold=True))
    f.append(text(747, 303, "Читає tail лише коли буфер порожній", size=9.5, color=MUTED))

    # Стрілки зв'язку
    f.append(arrow(275, 164, 303, 164, color=PROD_LINE, sw=1.8))
    f.append(arrow(623, 164, 597, 164, color=CONS_LINE, sw=1.8))

    note(f, W / 2, 355, 840,
         ["Кожне ядро пише лише у власну кеш-лінію — це виключає cache line bouncing за протоколом MESI.",
          "Локальне кешування чужого індексу зводить дорогі між'ядерні атомарні читання до абсолютного мінімуму."])
    render(os.path.join(IMG, "lock-free-spsc-ring.svg"), W, H, *f)


# ── 3. Стратегії обробки переповнення (Backpressure) ───────────────────────────
def fig_backpressure_strategies():
    W, H = 900, 440
    f = [text(W / 2, 28, "Стратегії поведінки при переповненні буфера (λ > μ)", size=16, bold=True)]
    f.append(text(W / 2, 48, "Вибір інженерної політики при тривалому перевищенні швидкості виробництва над споживанням",
                  size=11, color=MUTED, italic=True))

    col_w, col_h = 195, 250
    gap = 20
    start_x = 35
    top_y = 80

    strategies = [
        ("1. Блокуючий тиск", "Backpressure", PROD_FILL, PROD_LINE,
         ["Виробник засинає на", "умовній змінній", "not_full до звільнення", "слота споживачем.", "", "Гарантія: 0% втрат", "Ціна: уповільнення"]),

        ("2. Відкидання старих", "Drop Oldest", CONS_FILL, CONS_LINE,
         ["Новий запис стирає", "найстаріший елемент,", "зсуваючи head вперед.", "", "Застосування: відео,", "датчики, телеметрія", "Перевага: актуальність"]),

        ("3. Відкидання нових", "Drop Newest / Tail Drop", FAIL_FILL, FAIL_LINE,
         ["Новий пакет відкидається", "негайно, буфер лишається", "незмінним.", "", "Застосування: мережеві", "маршрутизатори,", "захист від перевантажень"]),

        ("4. Еластичний пул", "Work Stealing / Scale", QUEUE_FILL, QUEUE_LINE,
         ["Динамічне породження", "нових потоків-воркерів", "або передача задач у", "пул сусідніх ядер.", "", "Автомасштабування", "Ціна: витрати пам'яті"]),
    ]

    for i, (title, sub, fill_c, stroke_c, lines) in enumerate(strategies):
        bx = start_x + i * (col_w + gap)
        f.append(rect(bx, top_y, col_w, col_h, fill="#ffffff", stroke=stroke_c, sw=1.8, rx=8))
        f.append(rect(bx, top_y, col_w, 42, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        f.append(text(bx + col_w / 2, top_y + 18, title, size=11, color=stroke_c, bold=True))
        f.append(text(bx + col_w / 2, top_y + 34, sub, size=9.5, color=MUTED, italic=True))

        for li, line_text in enumerate(lines):
            is_bold = ("Гарантія:" in line_text or "Застосування:" in line_text or "Автомасштабування" in line_text)
            f.append(text(bx + col_w / 2, top_y + 70 + li * 20, line_text, size=9.5, color=INK, bold=is_bold))

    note(f, W / 2, 355, 840,
         ["Нескінченних буферів не існує: будь-яка черга без протитиску завершується аварійним збоєм OOM.",
          "Для надійних транзакцій обирають блокування; для потокового медіа та датчиків — відкидання найстаріших даних."])
    render(os.path.join(IMG, "backpressure-strategies.svg"), W, H, *f)


# ── 4. Коректна зупинка системи (Graceful Shutdown) ───────────────────────────
def fig_graceful_shutdown_flow():
    W, H = 900, 440
    f = [text(W / 2, 28, "Протокол коректної зупинки (Graceful Shutdown & Queue Drain)", size=16, bold=True)]
    f.append(text(W / 2, 48, "Як зупинити пул заблокованих споживачів без дедлоків, витоків ресурсів та втрати залишкових даних",
                  size=11, color=MUTED, italic=True))

    step_w, step_h = 185, 245
    gap = 25
    start_x = 35
    top_y = 80

    steps = [
        ("Крок 1: Сигнал", "Ініціація завершення", PROD_FILL, PROD_LINE,
         ["Виробник завершує", "роботу й виставляє", "прапорець:", "is_shutdown = true", "(або надсилає", "маркер Poison Pill)."]),

        ("Крок 2: Сповіщення", "Широкомовний сигнал", SYNC_FILL, SYNC_LINE,
         ["Виклик notify_all()", "на cv not_empty.", "Усі сплячі споживачі", "одночасно виходять", "зі стану сну на", "умовній змінній."]),

        ("Крок 3: Вичитка", "Вичерпання (Drain)", CONS_FILL, CONS_LINE,
         ["Споживачі НЕ виходять", "одразу: у циклі", "доки !queue.empty()", "вони опрацьовують усі", "залишкові задачі", "в буфері."]),

        ("Крок 4: Фінал", "Безпечний join()", QUEUE_FILL, QUEUE_LINE,
         ["Коли черга порожня й", "is_shutdown == true,", "потоки завершують", "функцію потоку.", "Головний потік робить", "thread.join()."]),
    ]

    for i, (title, sub, fill_c, stroke_c, lines) in enumerate(steps):
        bx = start_x + i * (step_w + gap)
        f.append(rect(bx, top_y, step_w, step_h, fill="#ffffff", stroke=stroke_c, sw=1.8, rx=8))
        f.append(rect(bx, top_y, step_w, 42, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        f.append(text(bx + step_w / 2, top_y + 18, title, size=11, color=stroke_c, bold=True))
        f.append(text(bx + step_w / 2, top_y + 34, sub, size=9.5, color=MUTED, italic=True))

        for li, line_text in enumerate(lines):
            is_code = ("is_shutdown" in line_text or "notify_all" in line_text or "!queue.empty" in line_text or "join()" in line_text)
            f.append(text(bx + step_w / 2, top_y + 75 + li * 22, line_text, size=9.5, color=stroke_c if is_code else INK, bold=is_code))

        if i < len(steps) - 1:
            arrow_x = bx + step_w + 3
            f.append(arrow(arrow_x, top_y + step_h / 2, arrow_x + gap - 6, top_y + step_h / 2, color=LINE, sw=1.8))

    note(f, W / 2, 355, 840,
         ["Грубе переривання (pthread_cancel/terminate) призводить до розірваних інваріантів та витоків дескрипторів.",
          "Коректний протокол гарантує 100% обробку накопичених у черзі повідомлень перед зупиненням процесу."])
    render(os.path.join(IMG, "graceful-shutdown-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_producer_consumer_architecture()
    fig_lock_free_spsc_ring()
    fig_backpressure_strategies()
    fig_graceful_shutdown_flow()
    print("Усі 4 фігури згенеровано успішно.")
