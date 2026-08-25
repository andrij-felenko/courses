# -*- coding: utf-8 -*-
"""Фігури до теми «Умовна змінна» (reference/cpp-standards/concurrency/condition-variable)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BG_COLOR = "#f8f9fa"
LOCK_FILL = "#eef6fc"
LOCK_STROKE = "#1d70b8"
SLEEP_FILL = "#f3f2f1"
SLEEP_STROKE = "#505a5f"
SIGNAL_FILL = "#eaf7ee"
SIGNAL_STROKE = "#28a745"
WARN_FILL = "#fdf0ed"
WARN_STROKE = "#d4351c"

# ── 1. Атомарність операції wait() ──────────────────────────────────────────
def fig_cv_atomic_wait_flow():
    W, H = 860, 420
    f = []

    # Заголовок / фон
    f.append(text(W / 2, 30, "Послідовність виконання std::condition_variable::wait(lock, pred)", size=16, bold=True, color="#0b0c0c"))

    # Блоки krok за кроком
    b1, w1, h1 = textbox(130, 110, ["1. Захоплення м'ютекса", "lock.lock()", "Потік володіє м'ютексом"], size=13, fill=LOCK_FILL, stroke=LOCK_STROKE, min_w=170)
    b2, w2, h2 = textbox(370, 110, ["2. Перевірка предиката", "if (pred()) return;", "Предикат хибний → чекаємо"], size=13, fill=LOCK_FILL, stroke=LOCK_STROKE, min_w=170)
    b3, w3, h3 = textbox(610, 110, ["3. Атомарний перехід", "Основа механізму CV"], size=13, fill=WARN_FILL, stroke=WARN_STROKE, min_w=170)
    f += [b1, b2, b3]

    # Стрілки верхнього ряду
    f.append(arrow(130 + w1 / 2, 110, 370 - w2 / 2, 110, color=LOCK_STROKE))
    f.append(arrow(370 + w2 / 2, 110, 610 - w3 / 2, 110, color=LOCK_STROKE))

    # Нижні деталі кроку 3 та далі
    b4, w4, h4 = textbox(610, 260, ["Атомарно:", "а) Відпускає м'ютекс", "б) Стає в чергу ОС"], size=13, fill=SLEEP_FILL, stroke=SLEEP_STROKE, min_w=170)
    b5, w5, h5 = textbox(370, 260, ["4. Сигнал & Пробудження", "notify_one() / notify_all()", "Потік виходить зі сну"], size=13, fill=SIGNAL_FILL, stroke=SIGNAL_STROKE, min_w=170)
    b6, w6, h6 = textbox(130, 260, ["5. Повторне захоплення", "lock.lock() всередині wait", "Знову перевірка pred()!"], size=13, fill=LOCK_FILL, stroke=LOCK_STROKE, min_w=170)
    f += [b4, b5, b6]

    # Зв'язки нижнього ряду
    f.append(arrow(610, 110 + h3 / 2, 610, 260 - h4 / 2, color=WARN_STROKE))
    f.append(arrow(610 - w4 / 2, 260, 370 + w5 / 2, 260, color=SIGNAL_STROKE))
    f.append(arrow(370 - w5 / 2, 260, 130 + w6 / 2, 260, color=LOCK_STROKE))

    # Стрілка петлі назад на крок 2
    f.append(arrow(130, 260 - h6 / 2, 370 - w2 / 2 + 20, 110 + h2 / 2, color=LOCK_STROKE))
    f.append(text(210, 175, "Цикл while(!pred)", size=12, bold=True, color=LOCK_STROKE))

    f.append(text(W / 2, 385, "Атомарність виключно запобігає втраті сигналу (lost wakeup race condition)", size=13, color=MUTED))

    render(os.path.join(IMG, "cv-atomic-wait-flow.svg"), W, H, *f, title="Схема атомарного очікування на умовній змінній")


# ── 2. Хібувальне пробудження (Spurious Wakeup) ───────────────────────────────
def fig_spurious_wakeup_timeline():
    W, H = 840, 340
    f = []

    f.append(text(W / 2, 30, "Чому перевірка предиката в циклі while є обов'язковою", size=16, bold=True, color="#0b0c0c"))

    # Дві лінії потоків
    # Потік А (Споживач)
    f.append(text(120, 90, "Потік A (Wait)", size=14, bold=True, color=LOCK_STROKE))
    f.append(line(210, 90, 780, 90, color=LOCK_STROKE, sw=2))

    # Потік B (Побічний / Сигнал)
    f.append(text(120, 210, "Потік B (Spurious)", size=14, bold=True, color=WARN_STROKE))
    f.append(line(210, 210, 780, 210, color=WARN_STROKE, sw=2))

    # Події на часовій осі
    t1, _, _ = textbox(280, 90, ["wait()", "сон"], size=12, fill=SLEEP_FILL, stroke=SLEEP_STROKE, min_w=90)
    t2, _, _ = textbox(460, 210, ["Сигнал ОС / EINTR", "без notify"], size=12, fill=WARN_FILL, stroke=WARN_STROKE, min_w=120)
    t3, _, _ = textbox(540, 90, ["Пробудження!", "pred == false"], size=12, fill=WARN_FILL, stroke=WARN_STROKE, min_w=120)
    t4, _, _ = textbox(700, 90, ["Знову в сон", "якщо while"], size=12, fill=SIGNAL_FILL, stroke=SIGNAL_STROKE, min_w=110)
    f += [t1, t2, t3, t4]

    # Стрілка впливу пробудження
    f.append(arrow(460, 210 - 25, 540 - 20, 90 + 25, color=WARN_STROKE))
    f.append(arrow(540 + 60, 90, 700 - 55, 90, color=SIGNAL_STROKE))

    f.append(text(W / 2, 305, "Потік може прокинутися від переривання ОС або хаш-колізії futex без виклику notify()", size=13, color=MUTED))

    render(os.path.join(IMG, "spurious-wakeup-timeline.svg"), W, H, *f, title="Хронологія фіктивного пробудження")


# ── 3. notify_one проти notify_all ───────────────────────────────────────────
def fig_notify_one_vs_all():
    W, H = 880, 360
    f = []

    f.append(text(W / 2, 30, "Порівняння notify_one() та notify_all()", size=16, bold=True, color="#0b0c0c"))

    # Ліва панель: notify_one
    p1, pw1, ph1 = textbox(220, 190, [
        "notify_one()",
        "• Пробуджує 1 потік з черги",
        "• Мінімальна контенція",
        "• Для точкових ресурсів",
        "• Ризик: пропуск якщо потік заснув"
    ], size=13, fill=SIGNAL_FILL, stroke=SIGNAL_STROKE, min_w=360)

    # Права панель: notify_all
    p2, pw2, ph2 = textbox(660, 190, [
        "notify_all()",
        "• Пробуджує всі потоки в черзі",
        "• Thundering Herd (шторм)",
        "• Для масових подій (stop/barrier)",
        "• Контенція за м'ютекс при старті"
    ], size=13, fill=WARN_FILL, stroke=WARN_STROKE, min_w=360)

    f += [p1, p2]

    f.append(text(W / 2, 335, "ОС Linux використовує FUTEX_CMP_REQUEUE для мінімізації контенції при notify_all()", size=13, color=MUTED))

    render(os.path.join(IMG, "notify-one-vs-all.svg"), W, H, *f, title="notify_one проти notify_all")


# ── 4. Futex та взаємодія з ядром ────────────────────────────────────────────
def fig_cv_futex_interaction():
    W, H = 860, 380
    f = []

    f.append(text(W / 2, 30, "Архітектура std::condition_variable над sys_futex у Linux", size=16, bold=True, color="#0b0c0c"))

    b_app, wa, ha = textbox(220, 120, ["Користувацький простір", "std::condition_variable", "std::unique_lock<std::mutex>"], size=13, fill=LOCK_FILL, stroke=LOCK_STROKE, min_w=280)
    b_pth, wp, hp = textbox(640, 120, ["POSIX Threads (libpthread)", "pthread_cond_wait()", "pthread_cond_signal()"], size=13, fill=LOCK_FILL, stroke=LOCK_STROKE, min_w=280)

    b_ker, wk, hk = textbox(430, 260, ["Простір ядра Linux (Kernel)", "sys_futex(addr, FUTEX_WAIT, val, timeout)", "sys_futex(addr, FUTEX_WAKE, count)", "Черги сну й хеш-таблиця futex_hash_bucket"], size=13, fill=SIGNAL_FILL, stroke=SIGNAL_STROKE, min_w=580)

    f += [b_app, b_pth, b_ker]

    f.append(arrow(220 + wa / 2, 120, 640 - wp / 2, 120, color=LOCK_STROKE))
    f.append(text(430, 100, "обгортка C++11", size=12, color=MUTED))

    f.append(arrow(220, 120 + ha / 2, 430 - 100, 260 - hk / 2, color=LOCK_STROKE))
    f.append(arrow(640, 120 + hp / 2, 430 + 100, 260 - hk / 2, color=LOCK_STROKE))

    f.append(text(W / 2, 350, "futex комбінує атомарне слово в user-space із системним викликом ядра лише за потреби сну", size=13, color=MUTED))

    render(os.path.join(IMG, "cv-futex-interaction.svg"), W, H, *f, title="Взаємодія std::condition_variable із ядром Linux через futex")


if __name__ == "__main__":
    fig_cv_atomic_wait_flow()
    fig_spurious_wakeup_timeline()
    fig_notify_one_vs_all()
    fig_cv_futex_interaction()
    print("Всі 4 фігури згенеровано успішно.")
