# -*- coding: utf-8 -*-
"""Фігури до теми «М'ютекс і RAII-замки» (reference/cpp-standards/concurrency/mutex-and-raii-locks)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FREEZE_FILL = "#fdecea"
OPEN_FILL   = "#eaf7ee"
BLUE_FILL   = "#eaf0fd"


# ── 1. Порівняння ручного керування м'ютексом та RAII ────────────────────────
def fig_raii_flow():
    W, H = 940, 420
    f = []

    f.append(text(250, 40, "Ручне керування (C-style / pthreads)", size=15, bold=True, color=POS))
    f.append(text(690, 40, "Автоматичне керування (C++ RAII)", size=15, bold=True, color=FIELD))

    # Стовпчик 1: Ручне керування
    b1, w1, _ = textbox(250, 95, "pthread_mutex_lock(&m);", size=13, pad=10, fill=FILL)
    b2, w2, _ = textbox(250, 165, "Обчислення / робота з ресурсом", size=13, pad=10, fill=FILL)
    b3, w3, _ = textbox(160, 245, ["Виняткова ситуація", "або early return"], size=12, pad=10, fill=FREEZE_FILL, stroke=POS)
    b4, w4, _ = textbox(340, 245, "pthread_mutex_unlock(&m);", size=12, pad=10, fill=OPEN_FILL, stroke=FIELD)
    b5, w5, _ = textbox(160, 340, ["Витік замка!", "Deadlock для інших ниток"], size=13, pad=11, fill=FREEZE_FILL, stroke=POS, sw=2)

    f += [b1, b2, b3, b4, b5]
    f.append(arrow(250, 115, 250, 145))
    f.append(arrow(220, 185, 160, 222, color=POS, sw=1.8))
    f.append(arrow(280, 185, 340, 222, color=FIELD, sw=1.8))
    f.append(arrow(160, 268, 160, 318, color=POS, sw=2))

    # Стовпчик 2: RAII
    r1, rw1, _ = textbox(690, 95, "std::scoped_lock lock(m);", size=13, pad=10, fill=BLUE_FILL, stroke=NEG)
    r2, rw2, _ = textbox(690, 165, "Обчислення / робота з ресурсом", size=13, pad=10, fill=FILL)
    r3, rw3, _ = textbox(600, 245, ["Виняткова ситуація", "або early return"], size=12, pad=10, fill=FREEZE_FILL, stroke=POS)
    r4, rw4, _ = textbox(780, 245, "Нормальне завершення", size=12, pad=10, fill=OPEN_FILL, stroke=FIELD)
    r5, rw5, _ = textbox(690, 340, ["Деструктор lock розгортається ЗАВЖДИ:", "m.unlock() гарантовано викликано!"], size=13, pad=11, fill=OPEN_FILL, stroke=FIELD, sw=2)

    f += [r1, r2, r3, r4, r5]
    f.append(arrow(690, 115, 690, 145))
    f.append(arrow(660, 185, 600, 222, color=POS, sw=1.8))
    f.append(arrow(720, 185, 780, 222, color=FIELD, sw=1.8))
    f.append(arrow(600, 268, 660, 318, color=FIELD, sw=2))
    f.append(arrow(780, 268, 720, 318, color=FIELD, sw=2))

    f.append(line(470, 30, 470, 390, color=MUTED, sw=1, dash="4 4"))

    render(os.path.join(IMG, "raii-lock-guard-flow.svg"), W, H, *f,
           title="Порівняння ручного розблокування та автоматичного розгортання RAII")


# ── 2. Порівняння типів RAII-обгорток ─────────────────────────────────────────
def fig_lock_types():
    W, H = 960, 360
    f = []

    cols = [(25, 170), (205, 170), (385, 190), (585, 180), (775, 160)]
    heads = ["Тип обгортки", "Стандарт", "Кількість м'ютексів", "Гнучкість / Операції", "Рекомендація"]

    for (x, w), h in zip(cols, heads):
        f.append(fitbox(x, 40, w, 36, h, size=13, bold=True, fill="#eef1f5", stroke=MUTED))

    rows = [
        ("std::lock_guard", "C++11", "1 м'ютекс", "Строгий scope, без unlock", "Застарів (замінений scoped_lock)"),
        ("std::unique_lock", "C++11", "1 м'ютекс", "Movable, defer, try_lock, CV", "Для condition_variable і відкладеного lock"),
        ("std::scoped_lock", "C++17", "1 або більше", "Deadlock avoidance, CTAD", "Основний вибір за замовчуванням"),
        ("std::shared_lock", "C++14/17", "1 (shared)", "Читацьке захоплення (shared)", "Для багатьох читачів і одного писця"),
    ]

    y = 86
    for t1, t2, t3, t4, t5 in rows:
        is_main = "scoped_lock" in t1
        bg_col = BLUE_FILL if is_main else FILL
        strk = NEG if is_main else LINE

        f.append(fitbox(cols[0][0], y, cols[0][1], 58, t1, size=13, bold=True, fill=bg_col, stroke=strk))
        f.append(fitbox(cols[1][0], y, cols[1][1], 58, t2, size=13, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[2][0], y, cols[2][1], 58, t3, size=13, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[3][0], y, cols[3][1], 58, t4, size=12, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[4][0], y, cols[4][1], 58, t5, size=12, fill=OPEN_FILL if is_main else BG, stroke=FIELD if is_main else MUTED))
        y += 64

    f.append(text(W / 2, 345, "З появою C++17 std::scoped_lock є стандартним вибором як для одного, так і для багатьох м'ютексів", size=12, color=MUTED))

    render(os.path.join(IMG, "lock-types-comparison.svg"), W, H, *f,
           title="Порівняльна характеристика RAII-замків стандартної бібліотеки")


# ── 3. Схема дедлоку та його розв'язання ─────────────────────────────────────
def fig_deadlock_order():
    W, H = 940, 380
    f = []

    f.append(text(240, 35, "Взаємне блокування (Deadlock)", size=15, bold=True, color=POS))
    f.append(text(700, 35, "Безпечна синхронізація через scoped_lock", size=15, bold=True, color=FIELD))

    # Сліпий кут (Deadlock)
    t1, _, _ = textbox(140, 95, "Потік A", size=14, bold=True, pad=10, fill=FILL)
    t2, _, _ = textbox(340, 95, "Потік B", size=14, bold=True, pad=10, fill=FILL)

    m1, _, _ = textbox(140, 200, ["М'ютекс M1", "захоплено Потоком A"], size=12, pad=10, fill=FREEZE_FILL, stroke=POS)
    m2, _, _ = textbox(340, 200, ["М'ютекс M2", "захоплено Потоком B"], size=12, pad=10, fill=FREEZE_FILL, stroke=POS)

    f += [t1, t2, m1, m2]

    f.append(arrow(140, 115, 140, 170, color=POS, sw=2))
    f.append(arrow(340, 115, 340, 170, color=POS, sw=2))

    # Перехресні очікування
    f.append(arrow(140, 230, 340, 230, color=POS, sw=2))
    f.append(arrow(340, 245, 140, 245, color=POS, sw=2))

    f.append(text(240, 222, "A чекає на M2", size=12, color=POS, bold=True))
    f.append(text(240, 260, "B чекає на M1", size=12, color=POS, bold=True))

    lbl_deadlock, _, _ = textbox(240, 320, ["Взаємний замок!", "Обидва потоки заблоковані назавжди"], size=13, pad=10, fill=FREEZE_FILL, stroke=POS, sw=2)
    f.append(lbl_deadlock)

    # Розв'язок (scoped_lock)
    sa, _, _ = textbox(700, 95, "std::scoped_lock lock(m1, m2);", size=13, bold=True, pad=11, fill=BLUE_FILL, stroke=NEG)
    sb, _, _ = textbox(700, 200, ["Алгоритм std::lock / deadlock-free:", "впорядкування або спроба + відкат"], size=13, pad=11, fill=FILL)
    sc, _, _ = textbox(700, 320, ["Атомарне захоплення обох м'ютексів:", "Дедлок технічно неможливий"], size=13, pad=11, fill=OPEN_FILL, stroke=FIELD, sw=2)

    f += [sa, sb, sc]

    f.append(arrow(700, 120, 700, 170, color=FIELD, sw=2))
    f.append(arrow(700, 230, 700, 290, color=FIELD, sw=2))

    f.append(line(470, 25, 470, 360, color=MUTED, sw=1, dash="4 4"))

    render(os.path.join(IMG, "deadlock-order.svg"), W, H, *f,
           title="Механіка виникнення взаємного блокування та його відвернення")


# ── 4. Часова шкала еволюції синхронізації в C++ ────────────────────────────
def fig_mutex_timeline():
    W = 1040
    rows = [
        ("C++98 / C++03", ["Відсутність стандартних ниток і м'ютексів у мові.",
                           "Використання платформозалежних POSIX Threads (pthread_mutex_t) або Win32 API."]),
        ("C++11", ["Перший стандарт багатонитвовості: std::mutex, std::recursive_mutex, std::timed_mutex.",
                   "Впровадження RAII-замків std::lock_guard та std::unique_lock, а також std::lock()."]),
        ("C++14", ["Додано std::shared_timed_mutex та std::shared_lock для Read-Write замків."]),
        ("C++17", ["Універсальний std::scoped_lock (із підтримкою CTAD) та легший std::shared_mutex."]),
        ("C++20", ["Семафори (std::counting_semaphore), бар'єри (std::barrier) та std::jthread із RAII."]),
    ]
    step = 82
    y0 = 100
    H = y0 + (len(rows) - 1) * step + 80
    f = [line(230, y0 - 30, 230, y0 + (len(rows) - 1) * step + 30, color=MUTED, sw=2)]

    for i, (when, lines) in enumerate(rows):
        y = y0 + i * step
        is_c17 = "C++17" in when
        box, bw, bh = textbox(630, y, lines, size=13, pad=12,
                              fill=BLUE_FILL if is_c17 else FILL,
                              stroke=NEG if is_c17 else LINE, min_w=720)
        f.append(box)
        f.append(circle(230, y, 7, fill=BG, stroke=POS if not is_c17 else NEG, sw=2.5))
        f.append(text(205, y + 5, when, size=13, anchor="end", bold=True))

    f.append(text(W / 2, H - 30,
                  "Еволюція C++ прямує від сирих системних викликів до безпечних RAII-обгорток із гарантією на рівні типів",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "mutex-timeline.svg"), W, H, *f,
           title="Хронологія розвитку засобів взаємного виключення в стандартах C++")


if __name__ == "__main__":
    fig_raii_flow()
    fig_lock_types()
    fig_deadlock_order()
    fig_mutex_timeline()
    print("ok:", os.listdir(IMG))
