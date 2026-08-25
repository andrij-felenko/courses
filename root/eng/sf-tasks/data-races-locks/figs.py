# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# Кольори
C_CORE1 = "#2457d6"   # Ядро 1 / Потік A
C_CORE2 = "#c0392b"   # Ядро 2 / Потік B
C_LOCK  = "#27ae60"   # Замок / Успішне блокування
C_WAIT  = "#e08a1e"   # Очікування / Сплячка
C_MEM   = "#6b7280"   # Пам'ять / Кеш

# ── Фігура 1: Перегони даних на апаратному рівні ─────────────────────────────
def fig_data_race_hardware():
    W, H = 780, 370
    frags = []

    # Спільна пам'ять RAM унизу
    ram_box = fitbox(240, 280, 300, 60, "Спільна оперативна пам'ять (RAM)\nБаланс: balance = 100",
                     fill="#eef2f7", stroke="#4b5563", sw=2, size=13, bold=True)
    frags.append(ram_box)

    # Ліва колонка — Ядро 1 (Потік A)
    k1_title = fitbox(40, 55, 290, 36, "Ядро 1 (Потік A): balance += 50",
                      fill="#edf2fc", stroke=C_CORE1, sw=1.5, size=13, bold=True, color=C_CORE1)
    frags.append(k1_title)

    k1_steps = [
        "1. Читання balance (100) у регістр R1",
        "2. Обчислення: R1 = 100 + 50 = 150",
        "3. Запис 150 назад у balance"
    ]
    for i, s in enumerate(k1_steps):
        frags.append(fitbox(40, 100 + i*44, 290, 36, s, fill="#f8fafc", stroke="#94a3b8", sw=1, size=12))

    # Права колонка — Ядро 2 (Потік B)
    k2_title = fitbox(450, 55, 290, 36, "Ядро 2 (Потік B): balance += 30",
                      fill="#fdf2f2", stroke=C_CORE2, sw=1.5, size=13, bold=True, color=C_CORE2)
    frags.append(k2_title)

    k2_steps = [
        "1. Читання balance (100) у регістр R2",
        "2. Обчислення: R2 = 100 + 30 = 130",
        "3. Запис 130 поверх результату Ядра 1"
    ]
    for i, s in enumerate(k2_steps):
        frags.append(fitbox(450, 100 + i*44, 290, 36, s, fill="#f8fafc", stroke="#94a3b8", sw=1, size=12))

    # Стрілки з'єднання (читання з RAM до ядер)
    frags.append(line(260, 280, 200, 140, color=C_CORE1, sw=1.5, dash="4 3"))
    frags.append(text(150, 220, "Читає 100", size=11, color=C_CORE1, bold=True))

    frags.append(line(520, 280, 580, 140, color=C_CORE2, sw=1.5, dash="4 3"))
    frags.append(text(630, 220, "Читає 100", size=11, color=C_CORE2, bold=True))

    # Запис 150 (Ядро 1)
    frags.append(arrow(185, 235, 280, 280, color=C_CORE1, sw=1.8))

    # Запис 130 (Ядро 2, затирає 150)
    frags.append(arrow(595, 235, 500, 280, color=C_CORE2, sw=2.0))

    # Підсумок у центрі
    res_box = fitbox(250, 150, 280, 56, "Втрачене оновлення!\nЗамість 180 у пам'яті опинилося 130",
                     fill="#fee2e2", stroke=POS, sw=2, size=12, bold=True, color=POS)
    frags.append(res_box)

    render(os.path.join(OUT, 'data-race-hardware.svg'), W, H, *frags,
           title="Перегони даних: несинхронізований доступ двох ядер до спільної комірки")


# ── Фігура 2: Часова шкала замка і бар'єр синхронізації ──────────────────────
def fig_mutex_timeline():
    W, H = 780, 340
    frags = []

    # Вісь часу
    x0, y_t = 60, 300
    frags.append(arrow(x0, y_t, W - 40, y_t, color=INK, sw=1.5))
    frags.append(text(W - 30, y_t + 4, "Час t", size=12, color=INK, anchor="start", bold=True))

    # Доріжка Потоку A (y = 85)
    yA = 85
    frags.append(text(120, yA + 5, "Потік A", size=13, color=C_CORE1, bold=True, anchor="end"))
    frags.append(line(130, yA, 720, yA, color="#e2e8f0", sw=2))

    # Доріжка Потоку B (y = 195)
    yB = 195
    frags.append(text(120, yB + 5, "Потік B", size=13, color=C_CORE2, bold=True, anchor="end"))
    frags.append(line(130, yB, 720, yB, color="#e2e8f0", sw=2))

    # Потік A: lock() у t=1, робота t=1..4, unlock() у t=4
    xA_start, xA_end = 150, 380
    frags.append(rect(xA_start, yA - 16, xA_end - xA_start, 32, fill="#dcfce7", stroke=C_LOCK, sw=2, rx=4))
    frags.append(text((xA_start + xA_end)/2, yA + 5, "Критична секція A (замок захоплено)", size=12, color="#166534", bold=True))

    # Потік B: lock() у t=2, блокування до t=4, критична секція t=4..7
    xB_req = 240
    xB_wake = 390
    xB_end = 650

    # Блокований відрізок Потоку B (очікування / сон)
    frags.append(rect(xB_req, yB - 16, xB_wake - xB_req, 32, fill="#fef3c7", stroke=C_WAIT, sw=1.5, rx=4))
    frags.append(text((xB_req + xB_wake)/2, yB + 5, "Блокований (спить в ОС)", size=11, color="#92400e", bold=True))

    # Критична секція B
    frags.append(rect(xB_wake, yB - 16, xB_end - xB_wake, 32, fill="#fee2e2", stroke=C_CORE2, sw=2, rx=4))
    frags.append(text((xB_wake + xB_end)/2, yB + 5, "Критична секція B (замок захоплено)", size=12, color="#991b1b", bold=True))

    # Стрілка блокування Потоку B при спробі lock()
    frags.append(arrow(xB_req, yB - 22, xB_req, yB - 16, color=C_WAIT, sw=1.5))
    frags.append(text(xB_req, yB - 26, "mutex.lock()", size=11, color=C_WAIT, bold=True))

    # Стрілка звільнення unlock() від Потоку A до пробудження B (xA_end=380, xB_wake=390)
    frags.append(arrow(xA_end, yA + 16, xB_wake, yB - 16, color=C_LOCK, sw=2.2))

    # Текст ліворуч від стрілки синхронізації
    sync_box = fitbox(150, 125, 215, 44, "Синхронізація (happens-before)\nУсі записи A стають видимими для B",
                      fill="#f0fdf4", stroke=C_LOCK, sw=1.5, size=10, bold=True, color="#15803d")
    frags.append(sync_box)

    # Підписи операцій
    frags.append(text(xA_start, yA - 24, "mutex.lock()", size=11, color=C_LOCK, bold=True))
    frags.append(text(xA_end, yA - 24, "mutex.unlock()", size=11, color=C_LOCK, bold=True))
    frags.append(text(xB_end, yB + 30, "mutex.unlock()", size=11, color=C_CORE2, bold=True))

    render(os.path.join(OUT, 'mutex-lock-unlock-timeline.svg'), W, H, *frags,
           title="Взаємне виключення та зв'язок «happens-before» через замок")


# ── Фігура 3: Швидкий і повільний шляхи замка (Futex / Гібридний замок) ──────
def fig_futex_paths():
    W, H = 780, 390
    frags = []

    # Початок: Виклик lock()
    frags.append(fitbox(270, 50, 240, 36, "Виклик mutex.lock()", fill="#f1f5f9", stroke="#334155", sw=2, size=13, bold=True))

    # Атомарний CAS
    frags.append(arrow(390, 86, 390, 115, color=INK, sw=1.5))
    frags.append(fitbox(240, 115, 300, 46, "Атомарний CAS(state, 0, 1)\nПеревірка та зміна 0 → 1",
                        fill="#eff6ff", stroke=NEG, sw=2, size=12, bold=True, color=NEG))

    # Розгалуження: Успіх (Швидкий шлях)
    frags.append(arrow(240, 138, 120, 138, color=C_LOCK, sw=2))
    frags.append(text(175, 128, "Успіх (було 0)", size=11, color=C_LOCK, bold=True))

    fast_box = fitbox(20, 195, 210, 80, "ШВИДКИЙ ШЛЯХ (Fast Path)\n\n• Простір користувача\n• Без системних викликів\n• Час: ~10-15 нс",
                      fill="#f0fdf4", stroke=C_LOCK, sw=2, size=11, bold=True, color="#166534")
    frags.append(fast_box)
    frags.append(arrow(120, 138, 120, 195, color=C_LOCK, sw=2))

    # Розгалуження: Невдача (Повільний шлях)
    frags.append(arrow(540, 138, 660, 138, color=POS, sw=2))
    frags.append(text(605, 128, "Зайнято (було 1)", size=11, color=POS, bold=True))

    slow_box = fitbox(550, 195, 210, 140, "ПОВІЛЬНИЙ ШЛЯХ (Slow Path)\n\n1. futex(FUTEX_WAIT)\n2. Перехід у простір ядра\n3. Потік стає у чергу сну\n4. Перемикання контексту\n• Час: ~1-5 мкс",
                      fill="#fef2f2", stroke=POS, sw=2, size=11, bold=True, color="#991b1b")
    frags.append(slow_box)
    frags.append(arrow(660, 138, 660, 195, color=POS, sw=2))

    # Вхід у критичну секцію
    cs_box = fitbox(240, 315, 300, 45, "ВХІД У КРИТИЧНУ СЕКЦІЮ\n(Виконання захищеного коду)",
                    fill="#fefce8", stroke="#ca8a04", sw=2, size=12, bold=True, color="#854d0e")
    frags.append(cs_box)

    frags.append(arrow(120, 275, 240, 335, color=C_LOCK, sw=1.8))
    frags.append(arrow(660, 335, 540, 335, color=C_WAIT, sw=1.8))
    frags.append(text(640, 355, "Пробудження після futex wake", size=10, color=C_WAIT, bold=True))

    render(os.path.join(OUT, 'futex-fast-slow-path.svg'), W, H, *frags,
           title="Анатомія сучасного замка: швидкий шлях у просторі користувача та повільний у ядрі")


# ── Фігура 4: Грубозернисте проти Дрібнозернистого блокування ───────────────
def fig_coarse_vs_fine():
    W, H = 780, 350
    frags = []

    # Ліва половина: Грубозернисте (Coarse-grained)
    frags.append(fitbox(30, 55, 340, 34, "Грубозернистий замок (Один замок на все)",
                        fill="#fef2f2", stroke=POS, sw=1.5, size=12, bold=True, color=POS))

    c_box = rect(40, 100, 320, 170, fill="#fafaf9", stroke="#78716c", sw=1.5, rx=6)
    frags.append(c_box)
    frags.append(text(200, 122, "Спільна структура даних (наприклад, Хеш-таблиця)", size=11, color=MUTED, bold=True))

    # Один великий замок
    frags.append(fitbox(60, 135, 280, 34, "Глобальний замок (global_mutex)", fill="#fee2e2", stroke=POS, sw=2, size=12, bold=True, color="#991b1b"))

    # Секції всередині
    for i in range(4):
        frags.append(fitbox(55 + i*70, 185, 62, 35, f"Бакет {i+1}", fill="#f1f5f9", stroke="#cbd5e1", sw=1, size=11))

    frags.append(fitbox(40, 280, 320, 46, "Вузьке місце (Bottleneck):\nУсі 4 ядра чекають у черзі навіть для різних бакетів",
                        fill="#fff1f2", stroke=POS, sw=1, size=11, bold=True, color="#be123c"))

    # Права половина: Дрібнозернисте (Fine-grained)
    frags.append(fitbox(410, 55, 340, 34, "Дрібнозернисті замки (Окремий замок на секцію)",
                        fill="#f0fdf4", stroke=C_LOCK, sw=1.5, size=12, bold=True, color="#166534"))

    f_box = rect(420, 100, 320, 170, fill="#fafaf9", stroke="#78716c", sw=1.5, rx=6)
    frags.append(f_box)
    frags.append(text(580, 122, "Спільна структура даних (Хеш-таблиця зі смугами)", size=11, color=MUTED, bold=True))

    # 4 окремі замки
    for i in range(4):
        bx = 430 + i*74
        frags.append(fitbox(bx, 135, 68, 30, f"Замок {i+1}", fill="#dcfce7", stroke=C_LOCK, sw=1.5, size=10, bold=True, color="#15803d"))
        frags.append(fitbox(bx, 175, 68, 45, f"Бакет {i+1}\nДані", fill="#f1f5f9", stroke="#cbd5e1", sw=1, size=10))

    frags.append(fitbox(420, 280, 320, 46, "Паралельне виконання:\nПотоки працюють з різними бакетами одночасно без затримок",
                        fill="#f0fdf4", stroke=C_LOCK, sw=1, size=11, bold=True, color="#15803d"))

    render(os.path.join(OUT, 'coarse-vs-fine-locking.svg'), W, H, *frags,
           title="Гранулярність замків: грубозернисте блокування проти дрібнозернистого")


if __name__ == '__main__':
    fig_data_race_hardware()
    fig_mutex_timeline()
    fig_futex_paths()
    fig_coarse_vs_fine()
    print("Згенеровано 4 фігури в", OUT)
