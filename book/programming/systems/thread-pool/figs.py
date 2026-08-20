# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
CYAN = "#00838f"
ORANGE = "#d35400"


# ── 1. thread-pool-architecture: Загальна будова пулу потоків ────────────────
def fig_thread_pool_architecture():
    W, H = 880, 430
    p = []

    # Тло та секції
    # 1. Джерело завдань (Producers)
    p.append(rect(40, 60, 160, 310, fill="#f4f7fb", stroke=NEG, sw=1.8, rx=10))
    p.append(text(120, 90, "Потоки-клієнти", size=13, color=NEG, bold=True))
    p.append(text(120, 110, "(Producers / Виробники)", size=10, color=MUTED, italic=True))

    clients = ["Запит від мережі", "Таймерна подія", "Фоновий розрахунок", "Подія інтерфейсу"]
    cy = 135
    for c in clients:
        p.append(rect(55, cy, 130, 34, fill="#ffffff", stroke="#c8d6e5", sw=1.2, rx=6))
        p.append(text(120, cy + 21, c, size=11, color=INK))
        cy += 46

    p.append(arrow(200, 215, 270, 215, color=NEG, sw=2.2))
    p.append(text(235, 202, "submit()", size=11, color=NEG, bold=True))

    # 2. Черга завдань (Task Queue)
    p.append(rect(275, 60, 260, 310, fill="#fdfbf7", stroke=ORANGE, sw=1.8, rx=10))
    p.append(text(405, 90, "Обмежена черга завдань", size=13, color=ORANGE, bold=True))
    p.append(text(405, 110, "Mutex + Condition Variables", size=10, color=MUTED, italic=True))

    # Завдання в черзі
    tasks = ["Завдання #4", "Завдання #3", "Завдання #2", "Завдання #1 (голова)"]
    qy = 135
    for i, tname in enumerate(tasks):
        fill_col = "#fdeed9" if i == 3 else "#ffffff"
        stroke_col = ORANGE if i == 3 else "#e0b88f"
        p.append(rect(295, qy, 220, 34, fill=fill_col, stroke=stroke_col, sw=1.4, rx=6))
        p.append(text(405, qy + 21, tname, size=11, color=INK, bold=(i == 3)))
        qy += 46

    # Політика переповнення черги
    p.append(rect(295, 320, 220, 36, fill="#fbe9e7", stroke=POS, sw=1.2, rx=6))
    p.append(text(405, 342, "Переповнення: Backpressure / Reject", size=10, color=POS, bold=True))

    p.append(arrow(535, 215, 605, 215, color=FIELD, sw=2.2))
    p.append(text(570, 202, "pop()", size=11, color=FIELD, bold=True))

    # 3. Пул потоків-робітників (Worker Threads)
    p.append(rect(610, 60, 230, 310, fill="#f2faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(725, 90, "Потоки-робітники (Pool)", size=13, color=FIELD, bold=True))
    p.append(text(725, 110, "Фіксована кількість N_threads", size=10, color=MUTED, italic=True))

    workers = [
        ("Робітник #1", "Обчислення (Ядро 0)", POS),
        ("Робітник #2", "Очікування I/O (Ядро 1)", CYAN),
        ("Робітник #3", "Обчислення (Ядро 2)", POS),
        ("Робітник #4", "Спить (чекає задачу)", MUTED),
    ]
    wy = 135
    for wname, wstat, col in workers:
        p.append(rect(625, wy, 200, 34, fill="#ffffff", stroke=col, sw=1.4, rx=6))
        p.append(text(675, wy + 21, wname, size=11, color=INK, bold=True))
        p.append(text(775, wy + 21, wstat.split()[0], size=10, color=col, bold=True))
        wy += 46

    p.append(rect(625, 320, 200, 36, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(725, 342, "Завершення: Drain / Graceful Stop", size=10, color=FIELD, bold=True))

    # Загальний підпис унизу
    p.append(text(W / 2, H - 18, "Клієнти ставлять задачі в синхронізовану чергу; постійні потоки витягують і виконують їх без створення нових потоків ОС", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thread-pool-architecture.svg"), W, H, *p,
           title="Архітектура пулу потоків")


# ── 2. latency-vs-utilization: Залежність затримки від завантаження системи ────
def fig_latency_vs_utilization():
    W, H = 840, 420
    p = []

    # Осі координат графіка
    ox, oy = 90, 330
    gw, gh = 470, 250

    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    # Стрілки осей
    p.append(arrow(ox + gw - 5, oy, ox + gw + 15, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - gh + 5, ox, oy - gh - 15, color=LINE, sw=1.8))

    # Підписи осей
    p.append(text(ox + gw - 20, oy + 28, "Завантаження системи (ρ)", size=11, color=INK, bold=True))
    p.append(text(ox - 45, oy - gh + 20, "Час відгуку (T)", size=11, color=INK, bold=True))

    # Поділки осі X
    ticks_x = [(0.0, "0%"), (0.5, "50%"), (0.7, "70%"), (0.8, "80%"), (0.9, "90%"), (1.0, "100%")]
    for val, label in ticks_x:
        tx = ox + val * (gw - 40)
        p.append(line(tx, oy, tx, oy + 6, color=MUTED, sw=1.2))
        p.append(text(tx, oy + 20, label, size=10, color=MUTED))
        if val > 0 and val < 1.0:
            p.append(line(tx, oy, tx, oy - gh + 20, color="#eceff1", sw=1.0, dash="3,3"))

    # Зона оптимуму (70-80%)
    opt_x1 = ox + 0.68 * (gw - 40)
    opt_x2 = ox + 0.82 * (gw - 40)
    p.append(rect(opt_x1, oy - gh + 30, opt_x2 - opt_x1, gh - 30, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text((opt_x1 + opt_x2) / 2, oy - gh + 50, "Оптимальна", size=11, color=FIELD, bold=True))
    p.append(text((opt_x1 + opt_x2) / 2, oy - gh + 66, "робоча зона", size=10, color=FIELD))

    # Крива затримки (hockey stick)
    pts = [
        (0.0, 0.08), (0.2, 0.10), (0.4, 0.13), (0.5, 0.16),
        (0.6, 0.20), (0.7, 0.27), (0.75, 0.33), (0.8, 0.42),
        (0.85, 0.58), (0.9, 0.82), (0.93, 1.0)
    ]
    svg_pts = []
    for u, lat in pts:
        px = ox + u * (gw - 40)
        py = oy - lat * (gh - 30)
        svg_pts.append((px, py))

    # Побудова плавної полілінії
    path_d = ["M %.1f,%.1f" % svg_pts[0]]
    for px, py in svg_pts[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path_d), POS))

    # Точка вибуху затримки (Knee of the curve)
    knee_x = ox + 0.85 * (gw - 40)
    knee_y = oy - 0.58 * (gh - 30)
    p.append(circle(knee_x, knee_y, 5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(line(knee_x + 4, knee_y - 4, knee_x + 22, knee_y - 22, color=POS, sw=1.4))
    p.append(text(knee_x + 26, knee_y - 26, "Згин кривої (Knee)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(knee_x + 26, knee_y - 12, "ρ > 85%: ріст черги", size=9, color=MUTED, anchor="start"))

    # Права колонка з поясненнями трьох зон
    cx, cy_box, cw = 590, 80, 220
    # Зона 1: Недовантаження
    p.append(rect(cx, cy_box, cw, 70, fill="#f4f6f9", stroke=NEG, sw=1.4, rx=6))
    p.append(text(cx + 12, cy_box + 20, "1. Недовантаження (ρ < 50%)", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(cx + 12, cy_box + 38, "Потоків замало або задач мало.", size=10, color=INK, anchor="start"))
    p.append(text(cx + 12, cy_box + 54, "Обчислювальні ресурси пустують.", size=10, color=MUTED, anchor="start"))

    # Зона 2: Оптимум
    cy_box += 85
    p.append(rect(cx, cy_box, cw, 70, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(cx + 12, cy_box + 20, "2. Оптимум (ρ ≈ 70–80%)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(cx + 12, cy_box + 38, "Висока пропускна здатність,", size=10, color=INK, anchor="start"))
    p.append(text(cx + 12, cy_box + 54, "передбачуваний низький час відгуку.", size=10, color=MUTED, anchor="start"))

    # Зона 3: Насичення й колапс
    cy_box += 85
    p.append(rect(cx, cy_box, cw, 70, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    p.append(text(cx + 12, cy_box + 20, "3. Насичення (ρ > 85–90%)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(cx + 12, cy_box + 38, "Вибухове накопичення в черзі,", size=10, color=INK, anchor="start"))
    p.append(text(cx + 12, cy_box + 54, "деградація пам'яті та тайм-аути.", size=10, color=MUTED, anchor="start"))

    # Нижній підпис
    p.append(text(W / 2, H - 15, "За законом масового обслуговування при наближенні завантаження до 100% затримка прямує до нескінченності", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "latency-vs-utilization.svg"), W, H, *p,
           title="Залежність затримки від завантаження системи")


# ── 3. work-stealing-vs-centralized: Централізована черга проти Work-Stealing ─
def fig_work_stealing_vs_centralized():
    W, H = 860, 420
    p = []

    # Ліва половина: Централізована черга
    p.append(rect(40, 50, 370, 325, fill="#fcfdfe", stroke=NEG, sw=1.8, rx=10))
    p.append(text(225, 78, "Централізована черга (Central Queue)", size=13, color=NEG, bold=True))
    p.append(text(225, 96, "Єдиний замок (Mutex) на всі потоки", size=10, color=MUTED, italic=True))

    # Єдина черга
    p.append(rect(80, 120, 290, 42, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(225, 145, "Спільна черга завдань (Mutex)", size=11, color=POS, bold=True))

    # Конкуренція - плашка по центру
    p.append(rect(100, 180, 250, 28, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    p.append(text(225, 198, "Конкуренція за замок (Lock Contention)", size=10, color=POS, bold=True))

    # Стрілки конкуренції від робітників до плашки і далі до черги
    p.append(arrow(225, 180, 225, 164, color=POS, sw=1.8))
    p.append(line(95, 235, 160, 208, color=POS, sw=1.4))
    p.append(line(175, 235, 200, 208, color=POS, sw=1.4))
    p.append(line(255, 235, 250, 208, color=POS, sw=1.4))
    p.append(line(335, 235, 290, 208, color=POS, sw=1.4))

    # Потоки-робітники
    wx_start = 65
    for i in range(4):
        p.append(rect(wx_start, 235, 70, 50, fill="#ffffff", stroke=NEG, sw=1.3, rx=6))
        p.append(text(wx_start + 35, 256, "Потік %d" % (i + 1), size=10, color=INK, bold=True))
        p.append(text(wx_start + 35, 272, "Ядро %d" % i, size=9, color=MUTED))
        wx_start += 82

    p.append(text(225, 315, "Вузьке місце: при N > 8–16 потоків", size=10, color=POS, bold=True))
    p.append(text(225, 332, "час блокування перевищує корисну роботу", size=10, color=MUTED))

    # Права половина: Work-Stealing
    p.append(rect(450, 50, 370, 325, fill="#f8fcf9", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(635, 78, "Крадіжка роботи (Work-Stealing)", size=13, color=FIELD, bold=True))
    p.append(text(635, 96, "Окремий Deque для кожного потоку", size=10, color=MUTED, italic=True))

    # Колонки робітників з власними чергами
    dwx = 475
    for i in range(3):
        # Дек робітника
        p.append(rect(dwx, 120, 95, 110, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
        p.append(text(dwx + 47, 140, "Deque %d" % (i + 1), size=10, color=FIELD, bold=True))
        p.append(rect(dwx + 10, 155, 75, 20, fill="#e8f8f5", stroke="#a3e4d7", sw=1.0, rx=3))
        p.append(text(dwx + 47, 169, "Задача A", size=9, color=INK))
        p.append(rect(dwx + 10, 180, 75, 20, fill="#e8f8f5", stroke="#a3e4d7", sw=1.0, rx=3))
        p.append(text(dwx + 47, 194, "Задача B", size=9, color=INK))
        p.append(text(dwx + 47, 218, "Хвіст: LIFO", size=9, color=MUTED))

        # Потік під деком
        p.append(arrow(dwx + 47, 235, dwx + 47, 255, color=FIELD, sw=1.5))
        p.append(rect(dwx, 260, 95, 45, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
        p.append(text(dwx + 47, 280, "Потік %d" % (i + 1), size=10, color=INK, bold=True))
        p.append(text(dwx + 47, 296, "Працює локально", size=9, color=MUTED))

        dwx += 115

    # Стрілка крадіжки роботи (Steal) від Потоку 3 до Deque 1
    p.append(arrow(705, 260, 580, 135, color=ORANGE, sw=2.0))
    p.append(text(660, 175, "Steal (Голова: FIFO)", size=10, color=ORANGE, bold=True))

    p.append(text(635, 335, "Немає єдиного замка: потоки не блокують", size=10, color=FIELD, bold=True))
    p.append(text(635, 352, "один одного і масштабуються на сотні ядер", size=10, color=MUTED))

    # Загальний підпис
    p.append(text(W / 2, H - 15, "Централізована черга страждає від конкуренції за замок; Work-Stealing ізолює черги й краде лише коли потік спорожнів", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "work-stealing-vs-centralized.svg"), W, H, *p,
           title="Централізована черга проти Work-Stealing")


if __name__ == "__main__":
    fig_thread_pool_architecture()
    fig_latency_vs_utilization()
    fig_work_stealing_vs_centralized()
    print("All figures generated successfully.")
