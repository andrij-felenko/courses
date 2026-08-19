# -*- coding: utf-8 -*-
"""Фігури до теми «latch, barrier і counting_semaphore» (reference/cpp-standards/concurrency/latch-barrier-semaphore)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── Палітра кольорів ────────────────────────────────────────────────────────
BG_PANEL    = "#f4f6f8"
LATCH_FILL  = "#eef6fc"
LATCH_LINE  = "#1d70b8"
BARRIER_FILL= "#fdf2e9"
BARRIER_LINE= "#d35400"
SEM_FILL    = "#eafaf1"
SEM_LINE    = "#27ae60"
KERNEL_FILL = "#fbeee6"
KERNEL_LINE = "#c0392b"
USER_FILL   = "#ebf5fb"
USER_LINE   = "#2980b9"
MUTED_TXT   = "#566573"

# ── 1. Порівняння трьох примітивів синхронізації ────────────────────────────
def fig_sync_primitives_comparison():
    W, H = 960, 460
    f = []

    f.append(text(W / 2, 28, "Три моделі координації потоків у C++20", size=16, bold=True, color=INK))

    # Колонка 1: std::latch
    c1_x = 170
    f.append(rect(c1_x - 140, 55, 280, 370, fill=LATCH_FILL, stroke=LATCH_LINE, sw=1.5, rx=8))
    f.append(text(c1_x, 82, "std::latch", size=15, bold=True, color=LATCH_LINE))
    f.append(text(c1_x, 102, "Одноразовий лічильник", size=12, italic=True, color=MUTED_TXT))

    b_l1, _, _ = textbox(c1_x, 145, ["Потік 1: count_down()", "Потік 2: count_down()", "Потік 3: count_down()"], size=12, fill="#ffffff", stroke=LATCH_LINE, min_w=240)
    b_l2, _, _ = textbox(c1_x, 235, ["Лічильник: N → 0", "Ворота зачинені, поки > 0"], size=12, fill="#ffffff", stroke=LATCH_LINE, min_w=240)
    b_l3, _, _ = textbox(c1_x, 325, ["Потік-майстер: wait()", "Миттєве відкриття для всіх"], size=12, fill="#ffffff", stroke=LATCH_LINE, min_w=240)
    f += [b_l1, b_l2, b_l3]
    f.append(arrow(c1_x, 175, c1_x, 210, color=LATCH_LINE))
    f.append(arrow(c1_x, 260, c1_x, 300, color=LATCH_LINE))
    f.append(text(c1_x, 400, "Одноразовий: не можна скинути", size=11, bold=True, color=LATCH_LINE))

    # Колонка 2: std::barrier
    c2_x = 480
    f.append(rect(c2_x - 140, 55, 280, 370, fill=BARRIER_FILL, stroke=BARRIER_LINE, sw=1.5, rx=8))
    f.append(text(c2_x, 82, "std::barrier", size=15, bold=True, color=BARRIER_LINE))
    f.append(text(c2_x, 102, "Багаторазовий фазовий бар'єр", size=12, italic=True, color=MUTED_TXT))

    b_b1, _, _ = textbox(c2_x, 145, ["Фаза K: потоки обчислюють", "виклик arrive_and_wait()"], size=12, fill="#ffffff", stroke=BARRIER_LINE, min_w=240)
    b_b2, _, _ = textbox(c2_x, 235, ["Completion Function", "Один потік: swap / підсумок"], size=12, fill="#ffffff", stroke=BARRIER_LINE, min_w=240)
    b_b3, _, _ = textbox(c2_x, 325, ["Фаза K+1: усі розблоковані", "Автоскидання лічильника"], size=12, fill="#ffffff", stroke=BARRIER_LINE, min_w=240)
    f += [b_b1, b_b2, b_b3]
    f.append(arrow(c2_x, 175, c2_x, 210, color=BARRIER_LINE))
    f.append(arrow(c2_x, 260, c2_x, 300, color=BARRIER_LINE))
    f.append(text(c2_x, 400, "Циклічний: фази 0, 1, 2, ...", size=11, bold=True, color=BARRIER_LINE))

    # Колонка 3: std::counting_semaphore
    c3_x = 790
    f.append(rect(c3_x - 140, 55, 280, 370, fill=SEM_FILL, stroke=SEM_LINE, sw=1.5, rx=8))
    f.append(text(c3_x, 82, "std::counting_semaphore", size=15, bold=True, color=SEM_LINE))
    f.append(text(c3_x, 102, "Лічильник дозволів (Permits)", size=12, italic=True, color=MUTED_TXT))

    b_s1, _, _ = textbox(c3_x, 145, ["Пул ресурсів (К дозволів)", "Потік X: acquire() [−1]"], size=12, fill="#ffffff", stroke=SEM_LINE, min_w=240)
    b_s2, _, _ = textbox(c3_x, 235, ["Лічильник: K > 0 дозволено", "Лічильник == 0 → потік спить"], size=12, fill="#ffffff", stroke=SEM_LINE, min_w=240)
    b_s3, _, _ = textbox(c3_x, 325, ["Потік Y: release() [+1]", "Будить очікуючий потік"], size=12, fill="#ffffff", stroke=SEM_LINE, min_w=240)
    f += [b_s1, b_s2, b_s3]
    f.append(arrow(c3_x, 175, c3_x, 210, color=SEM_LINE))
    f.append(arrow(c3_x, 260, c3_x, 300, color=SEM_LINE))
    f.append(text(c3_x, 400, "Без власника: потік А бере, Б віддає", size=11, bold=True, color=SEM_LINE))

    render(os.path.join(IMG, "sync-primitives-comparison.svg"), W, H, *f, title="Порівняння latch, barrier та counting_semaphore")


# ── 2. Життєвий цикл та внутрішня механіка std::latch ───────────────────────
def fig_latch_lifecycle_flow():
    W, H = 900, 380
    f = []

    f.append(text(W / 2, 28, "Хронологія зменшення лічильника std::latch", size=16, bold=True, color=INK))

    # Стан 1: Ініціалізація
    b1, w1, h1 = textbox(160, 110, ["std::latch work_done(3)", "Лічильник = 3", "Ворота зачинені"], size=12, fill=LATCH_FILL, stroke=LATCH_LINE, min_w=210)

    # Стан 2: Декременти
    b2, w2, h2 = textbox(450, 110, ["Потоки 1, 2, 3 завершують задачі", "work_done.count_down()", "Атомарний декремент (3→2→1→0)"], size=12, fill=LATCH_FILL, stroke=LATCH_LINE, min_w=250)

    # Стан 3: Відкриття
    b3, w3, h3 = textbox(750, 110, ["Лічильник = 0", "Ворота відчинено назавжди!", "notify_all() для сплячих"], size=12, fill=SEM_FILL, stroke=SEM_LINE, min_w=210)
    f += [b1, b2, b3]

    f.append(arrow(160 + w1 / 2, 110, 450 - w2 / 2, 110, color=LATCH_LINE))
    f.append(arrow(450 + w2 / 2, 110, 750 - w3 / 2, 110, color=SEM_LINE))

    # Нижній рівень: Потік-спостерігач
    b4, w4, h4 = textbox(300, 260, ["Головний потік: wait()", "Лічильник > 0 → сон у futex", "Нуль навантаження на процесор"], size=12, fill=BG_PANEL, stroke=LINE, min_w=240)
    b5, w5, h5 = textbox(750, 260, ["Головний потік прокидається", "Продовження виконання", "Наступні wait() — миттєві (0 нс)"], size=12, fill=SEM_FILL, stroke=SEM_LINE, min_w=240)
    f += [b4, b5]

    f.append(arrow(300, 110 + h1 / 2, 300, 260 - h4 / 2, color=LINE))
    f.append(text(310, 185, "Блокування у wait()", size=11, color=MUTED_TXT, anchor="start"))

    f.append(arrow(750, 110 + h3 / 2, 750, 260 - h5 / 2, color=SEM_LINE))
    f.append(text(760, 185, "Розблокування", size=11, bold=True, color=SEM_LINE, anchor="start"))

    f.append(text(W / 2, 350, "Особливість: після досягнення нуля стан незворотний, скидання не існує", size=12, italic=True, color=MUTED_TXT))

    render(os.path.join(IMG, "latch-lifecycle-flow.svg"), W, H, *f, title="Життєвий цикл std::latch")


# ── 3. Фазовий цикл std::barrier ───────────────────────────────────────────
def fig_barrier_phase_cycle():
    W, H = 920, 420
    f = []

    f.append(text(W / 2, 28, "Фазовий перехід та Completion Step у std::barrier", size=16, bold=True, color=INK))

    # Крок 1: Обчислення
    b1, w1, h1 = textbox(170, 120, ["1. Обчислення фази K", "Потоки T0..TN-1 працюють", "Паралельна обробка смуг"], size=12, fill=BARRIER_FILL, stroke=BARRIER_LINE, min_w=220)

    # Крок 2: Прибуття
    b2, w2, h2 = textbox(460, 120, ["2. Прибуття до бар'єра", "arrive_and_wait()", "Очікують останнього учасника"], size=12, fill=BARRIER_FILL, stroke=BARRIER_LINE, min_w=220)

    # Крок 3: Completion Callback
    b3, w3, h3 = textbox(750, 120, ["3. Completion Step", "Виконується РІВНО ОДИН раз", "Обмін буферів / логування"], size=12, fill="#fef9e7", stroke="#f39c12", min_w=220)
    f += [b1, b2, b3]

    f.append(arrow(170 + w1 / 2, 120, 460 - w2 / 2, 120, color=BARRIER_LINE))
    f.append(arrow(460 + w2 / 2, 120, 750 - w3 / 2, 120, color=BARRIER_LINE))

    # Крок 4: Перехід у фазу K+1
    b4, w4, h4 = textbox(750, 270, ["4. Зміна фази: K → K+1", "Лічильник оновлено на N", "Усі потоки розблоковані"], size=12, fill=SEM_FILL, stroke=SEM_LINE, min_w=220)

    # Крок 5: Наступна ітерація
    b5, w5, h5 = textbox(170, 270, ["5. Початок фази K+1", "Потоки читають новий стан", "Повторення ітераційного циклу"], size=12, fill=BARRIER_FILL, stroke=BARRIER_LINE, min_w=220)
    f += [b4, b5]

    f.append(arrow(750, 120 + h3 / 2, 750, 270 - h4 / 2, color=SEM_LINE))
    f.append(arrow(750 - w4 / 2, 270, 170 + w5 / 2, 270, color=BARRIER_LINE))
    f.append(arrow(170, 270 - h5 / 2, 170, 120 + h1 / 2, color=BARRIER_LINE))

    f.append(text(460, 255, "Автоматичне повернення на новий цикл", size=12, bold=True, color=BARRIER_LINE))

    f.append(text(W / 2, 385, "Гарантія: жоден потік не увійде у фазу K+1, доки Completion Callback не завершиться", size=12, italic=True, color=MUTED_TXT))

    render(os.path.join(IMG, "barrier-phase-cycle.svg"), W, H, *f, title="Фазовий цикл std::barrier")


# ── 4. Архітектура швидкого шляху (Futex / WaitOnAddress) ───────────────────
def fig_futex_fast_path():
    W, H = 940, 440
    f = []

    f.append(text(W / 2, 28, "Швидкий шлях (User-Space) проти Системного виклику (Kernel)", size=16, bold=True, color=INK))

    # Область простору користувача
    f.append(rect(40, 60, 860, 150, fill=USER_FILL, stroke=USER_LINE, sw=1.5, rx=8))
    f.append(text(60, 85, "Простір користувача (User Space) — Швидкий шлях (Fast Path)", size=13, bold=True, color=USER_LINE, anchor="start"))

    b_u1, _, _ = textbox(240, 135, ["Атомарна операція", "fetch_sub() / fetch_add()", "Апаратна інструкція процесора"], size=12, fill="#ffffff", stroke=USER_LINE, min_w=240)
    b_u2, _, _ = textbox(570, 135, ["Умова виконана?", "Лічильник дозволяє продовжити", "0 системних викликів!"], size=12, fill="#ffffff", stroke=USER_LINE, min_w=240)
    b_u3, _, _ = textbox(810, 135, ["Миттєвий вихід", "Затримка: 1-3 нс"], size=12, fill=SEM_FILL, stroke=SEM_LINE, min_w=140)
    f += [b_u1, b_u2, b_u3]

    f.append(arrow(240 + 120, 135, 570 - 120, 135, color=USER_LINE))
    f.append(arrow(570 + 120, 135, 810 - 70, 135, color=SEM_LINE))
    f.append(text(690, 120, "ТАК", size=11, bold=True, color=SEM_LINE))

    # Стрілка переходу в ядро
    f.append(arrow(570, 170, 570, 250, color=KERNEL_LINE, sw=2))
    f.append(text(585, 215, "НІ (потрібно спати)", size=11, bold=True, color=KERNEL_LINE, anchor="start"))

    # Область ядра ОС
    f.append(rect(40, 240, 860, 150, fill=KERNEL_FILL, stroke=KERNEL_LINE, sw=1.5, rx=8))
    f.append(text(60, 265, "Простір ядра (Kernel Space) — Повільний шлях (Slow Path)", size=13, bold=True, color=KERNEL_LINE, anchor="start"))

    b_k1, _, _ = textbox(240, 325, ["Системний виклик ОС", "Linux: sys_futex(FUTEX_WAIT)", "Windows: WaitOnAddress()"], size=12, fill="#ffffff", stroke=KERNEL_LINE, min_w=240)
    b_k2, _, _ = textbox(570, 325, ["Черга очікування ядра", "Потік знято з виконання", "0% утилізації процесора"], size=12, fill="#ffffff", stroke=KERNEL_LINE, min_w=240)
    b_k3, _, _ = textbox(810, 325, ["Пробудження", "FUTEX_WAKE / Wake", "Затримка: 1.5-2 мкс"], size=12, fill="#ffffff", stroke=KERNEL_LINE, min_w=140)
    f += [b_k1, b_k2, b_k3]

    f.append(arrow(570 - 120, 325, 240 + 120, 325, color=KERNEL_LINE))
    f.append(arrow(570 + 120, 325, 810 - 70, 325, color=KERNEL_LINE))

    f.append(text(W / 2, 415, "Примітиви C++20 уникають ядра у 99% випадків, звертаючись до futex лише при реальній блокаді", size=12, italic=True, color=MUTED_TXT))

    render(os.path.join(IMG, "futex-fast-path-architecture.svg"), W, H, *f, title="Архітектура швидкого шляху futex")


if __name__ == "__main__":
    fig_sync_primitives_comparison()
    fig_latch_lifecycle_flow()
    fig_barrier_phase_cycle()
    fig_futex_fast_path()
    print("All figures generated successfully.")
