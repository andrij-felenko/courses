# -*- coding: utf-8 -*-
"""Фігури до теми «Перебірки (bulkhead)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / зависання / вичерпання
COOL = "#eaf0fd"   # нейтральне / запити
GOOD = "#e8f6ee"   # успіх / захищена зона
WARN = "#fef6e7"   # попередження / черга


# ── 1. Порівняння: спільний пул проти ізоляції перебірками ─────────────────────
def blast_radius_containment():
    W, H = 1180, 580
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "РАДІУС УРАЖЕННЯ: спільний пул потоків проти перебірок (Bulkhead)",
                    size=14, bold=True, fill=COOL))

    # Ліва панель: Без перебірок (Спільний пул)
    f.append(rect(40, 80, 530, 470, fill=FILL, stroke=POS, sw=2, rx=8))
    f.append(text(305, 110, "БЕЗ ПЕРЕБІРОК: СПІЛЬНИЙ ПУЛ (100 ПОТОКІВ)", size=13, color=POS, bold=True))
    f.append(text(305, 130, "Повільна залежність вичерпує 100% ресурсів процесу", size=11, color=MUTED))

    # Спільний пул
    f.append(rect(60, 150, 490, 190, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(305, 175, "Єдиний спільний пул обробників (Tomcat / Netty / Worker Pool)", size=12, bold=True))

    # Зайняті потоки
    for i in range(8):
        x = 80 + (i % 4) * 115
        y = 195 + (i // 4) * 45
        f.append(rect(x, y, 105, 36, fill="#f8d7da", stroke=POS, sw=1.2, rx=4))
        f.append(text(x + 52, y + 22, "Зависло (Реком.)", size=9, color=POS, bold=True))

    f.append(text(305, 310, "95 із 100 потоків заблоковані очікуванням рекомендацій (латентність 5 с)", size=10, color=POS))
    f.append(text(305, 328, "5 потоків обробляють чергу, яка миттєво переповнюється", size=10, color=POS))

    # Наслідок на інші гілки
    f.append(rect(60, 360, 490, 170, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(305, 385, "Стан критичних бізнес-операцій:", size=12, bold=True))

    f.append(rect(75, 405, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(145, 425, "Оплата / Checkout", size=11, bold=True))
    f.append(text(145, 442, "ВІДМОВА (504 Timeout)", size=9, color=POS, bold=True))

    f.append(rect(235, 405, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(305, 425, "Авторизація / Вхід", size=11, bold=True))
    f.append(text(305, 442, "ВІДМОВА (504 Timeout)", size=9, color=POS, bold=True))

    f.append(rect(395, 405, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(465, 425, "Health Check", size=11, bold=True))
    f.append(text(465, 442, "ВІДМОВА (Вузол убито)", size=9, color=POS, bold=True))

    f.append(text(305, 485, "Катастрофа: відмова 1 другорядного сервісу вбиває 100% системи", size=11, color=POS, bold=True))
    f.append(text(305, 510, "Радіус ураження = ВСЯ ПРОГРАМА", size=12, color=POS, bold=True))

    # Права панель: З перебірками (Bulkhead)
    f.append(rect(610, 80, 530, 470, fill=FILL, stroke=FIELD, sw=2, rx=8))
    f.append(text(875, 110, "З ПЕРЕБІРКАМИ: ІЗОЛЬОВАНІ ВІДСІКИ", size=13, color=FIELD, bold=True))
    f.append(text(875, 130, "Квоти та ліміти строго розмежовують бюджет ресурсів", size=11, color=MUTED))

    # Відсік 1: Оплата
    f.append(rect(630, 150, 490, 85, fill=GOOD, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(720, 175, "Перебірка Оплати", size=12, bold=True))
    f.append(text(720, 195, "Ліміт: 40 потоків | Зайнято: 12", size=10, color=MUTED))
    f.append(rect(910, 165, 190, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    f.append(text(1005, 182, "100% ДОСТУПНІСТЬ", size=10, color=FIELD, bold=True))
    f.append(text(1005, 197, "Латентність: 35 мс (Норма)", size=9, color=MUTED))

    # Відсік 2: Каталог / Авторизація
    f.append(rect(630, 245, 490, 85, fill=GOOD, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(720, 270, "Перебірка Каталогу", size=12, bold=True))
    f.append(text(720, 290, "Ліміт: 40 потоків | Зайнято: 18", size=10, color=MUTED))
    f.append(rect(910, 260, 190, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    f.append(text(1005, 277, "100% ДОСТУПНІСТЬ", size=10, color=FIELD, bold=True))
    f.append(text(1005, 292, "Латентність: 15 мс (Норма)", size=9, color=MUTED))

    # Відсік 3: Рекомендації (Затоплений)
    f.append(rect(630, 340, 490, 110, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(720, 365, "Перебірка Рекомендацій", size=12, bold=True))
    f.append(text(720, 385, "Ліміт: 20 потоків | Зайнято: 20", size=10, color=POS, bold=True))
    f.append(text(720, 405, "Черга повна (10/10) → Скидання 429/Fallback", size=9, color=POS))
    f.append(rect(910, 355, 190, 60, fill="#ffffff", stroke=POS, sw=1, rx=4))
    f.append(text(1005, 373, "ДЕГРАДАЦІЯ ЛОКАЛІЗОВАНА", size=9, color=POS, bold=True))
    f.append(text(1005, 390, "Повертає кеш / пустий блок", size=9, color=MUTED))
    f.append(text(1005, 406, "Надлишок відсікається миттєво", size=9, color=POS))

    # Підсумок
    f.append(rect(630, 465, 490, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(875, 490, "Головний бізнес захищено: аварія не виходить за межі свого відсіку", size=11, color=FIELD, bold=True))
    f.append(text(875, 512, "Радіус ураження = РІВНО 1 СУБКОМПОНЕНТ", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'blast-radius-containment.svg'), W, H, *f)


# ── 2. Чотири архітектурні рівні ізоляції перебірками ─────────────────────────
def bulkhead_levels():
    W, H = 1180, 600
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "ІЄРАРХІЯ ПЕРЕБІРОК: 4 РІВНІ ІЗОЛЯЦІЇ РЕСУРСІВ У РОЗПОДІЛЕНІЙ СИСТЕМІ",
                    size=14, bold=True, fill=COOL))

    levels = [
        ("РІВЕНЬ 1: Внутрішньопроцесна конкурентність",
         "Семафори, окремі пули потоків (Thread Pools), обмежені черги (Bounded Queues)",
         "Захищає процесорні потоки програми, пам'ять викликів та черги завдань від захоплення одним повільним клієнтом чи ендпоінтом.",
         GOOD, FIELD),
        ("РІВЕНЬ 2: Пули спільних ресурсів",
         "Окремі пули з'єднань до БД (Read-only vs Read-Write vs Batch), клієнтські пули HTTP/gRPC сокетів",
         "Запобігає ситуації, коли важкий аналітичний звіт вичерпує всі доступні з'єднання з Postgres, блокуючи транзакції клієнтів.",
         COOL, NEG),
        ("РІВЕНЬ 3: Процеси операційної системи та контейнери",
         "Linux cgroups v2 (cpu.max, memory.max, io.max), обмеження пам'яті контейнерів (K8s limits)",
         "Ізолює ресурси ОС: витік пам'яті (OOM) або нескінченний цикл в одному сервісі не вбиває сусідні процеси на тому ж фізичному вузлі.",
         WARN, "#d97706"),
        ("РІВЕНЬ 4: Інфраструктурні комірки та фізичні зони",
         "Cell-based Architecture, Swimlanes, відмовостійкі зони (Multi-AZ / Multi-Region), шардинг орендарів",
         "Повний фізичний та мережевий поділ клієнтів на ізольовані інстанси: масштабний збій у комірці А фізично не торкається комірки Б.",
         "#f3e8ff", "#7c3aed")
    ]

    for idx, (title, sub, desc, bg_col, border_col) in enumerate(levels):
        y = 80 + idx * 120
        # Рамка рівня
        f.append(rect(40, y, 1100, 105, fill=bg_col, stroke=border_col, sw=1.8, rx=8))

        # Ліва колонка: Назва та технології
        f.append(text(70, y + 30, title, size=13, color=border_col, bold=True, anchor="start"))
        f.append(text(70, y + 54, f"Механізми: {sub}", size=11, color=INK, bold=True, anchor="start"))
        f.append(text(70, y + 80, desc, size=11, color=MUTED, anchor="start"))

        # Права колонка: Іконка / мітка ізоляції
        f.append(rect(950, y + 20, 165, 65, fill="#ffffff", stroke=border_col, sw=1.2, rx=6))
        f.append(text(1032, y + 46, f"Ізоляція L{idx+1}", size=12, color=border_col, bold=True))
        f.append(text(1032, y + 68, "Бар'єр відмов", size=10, color=MUTED))

    render(os.path.join(OUT, 'bulkhead-levels.svg'), W, H, *f)


# ── 3. Порівняння: Пул потоків проти Семафора ──────────────────────────────────
def threadpool_vs_semaphore():
    W, H = 1180, 560
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "МЕХАНІЗМИ ІЗОЛЯЦІЇ: ПУЛ ПОТОКІВ (THREAD POOL) ПРОТИ СЕМАФОРА (SEMAPHORE)",
                    size=14, bold=True, fill=COOL))

    # Лівий бік: Ізоляція пулом потоків
    f.append(rect(40, 80, 530, 450, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(305, 110, "ІЗОЛЯЦІЯ ПУЛОМ ПОТОКІВ (THREAD POOL)", size=13, bold=True))
    f.append(text(305, 130, "Повна асинхронна ізоляція виконання в окремому пулі", size=11, color=MUTED))

    # Схема пулу
    f.append(rect(60, 150, 490, 160, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(150, 175, "Вхідна черга (Queue)", size=11, bold=True))
    for i in range(4):
        f.append(rect(80 + i * 40, 195, 32, 45, fill=COOL, stroke=NEG, sw=1, rx=3))
        f.append(text(96 + i * 40, 222, f"Q{i+1}", size=10))

    f.append(arrow(250, 217, 300, 217, color=LINE, sw=1.5))

    f.append(text(410, 175, "Виділені потоки (Workers)", size=11, bold=True))
    for i in range(3):
        f.append(rect(340 + i * 55, 195, 48, 45, fill=GOOD, stroke=FIELD, sw=1, rx=3))
        f.append(text(364 + i * 55, 222, f"T{i+1}", size=10, bold=True))

    f.append(text(305, 285, "Запит віддається воркеру; викликаючий потік вільний", size=10, color=FIELD, bold=True))

    # Властивості пулу
    f.append(rect(60, 325, 490, 185, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    f.append(text(80, 350, "+ Можливість жорсткого таймауту (переривання потоку)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 375, "+ Асинхронне виконання (non-blocking для клієнта)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 400, "+ Захист від блокування процесорного стека", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(80, 435, "− Високі накладні витрати пам'яті (стек ~1 МБ на потік)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(80, 460, "− Перемикання контексту ОС (Context Switch Overhead)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(80, 485, "− Втрата локальності потоку (ThreadLocal втрачається)", size=11, color=POS, bold=True, anchor="start"))

    # Правий бік: Семафор / Лімітер конкурентності
    f.append(rect(610, 80, 530, 450, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(875, 110, "СЕМАФОРНИЙ ЛІМІТЕР (SEMAPHORE BULKHEAD)", size=13, bold=True))
    f.append(text(875, 130, "Синхронне обмеження паралельних запитів на поточному потоці", size=11, color=MUTED))

    # Схема семафора
    f.append(rect(630, 150, 490, 160, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(rect(730, 180, 290, 75, fill=COOL, stroke=NEG, sw=1.4, rx=6))
    f.append(text(875, 205, "Атомарний лічильник (Permits)", size=12, bold=True))
    f.append(text(875, 230, "Активні запити: N ≤ MaxPermits (напр. 20/20)", size=11, color=NEG, bold=True))

    f.append(text(875, 285, "Виконується прямо на вході без черги і перемикання контексту", size=10, color=NEG, bold=True))

    # Властивості семафора
    f.append(rect(630, 325, 490, 185, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    f.append(text(650, 350, "+ Нульові накладні витрати пам'яті (лише 1 atomic int)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(650, 375, "+ Нуль перемикань контексту (максимальна швидкість)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(650, 400, "+ Ідеально для неблокуючих async/event-loop систем", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(650, 435, "− Виконується на викликаючому потоці (блокує його)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(650, 460, "− Неможливо примусово вбити завислий сокет без ОС", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(650, 485, "− Немає черги очікування (лише tryAcquire або миттєва відмова)", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, 'threadpool-vs-semaphore.svg'), W, H, *f)


# ── 4. Дилема розділення ресурсів: Resource Stranding ─────────────────────────
def resource_stranding():
    W, H = 1180, 540
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "ДИЛЕМА ПЕРЕБІРОК: НАДЛИШКОВА ФРАГМЕНТАЦІЯ ТА ЗАМОРОЖЕНІ РЕСУРСИ (RESOURCE STRANDING)",
                    size=14, bold=True, fill=COOL))

    # Лівий блок: Спільний пул (висока утилізація, але ризик колапсу)
    f.append(rect(40, 80, 350, 430, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(215, 110, "СПІЛЬНИЙ ПУЛ (0 ПЕРЕБІРОК)", size=12, bold=True))
    f.append(text(215, 130, "Висока утилізація, 0 ізоляції", size=10, color=MUTED))

    f.append(rect(60, 150, 310, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(rect(80, 170, 270, 80, fill="#d1e7dd", stroke=FIELD, sw=1, rx=4))
    f.append(text(215, 205, "Ефективність: 92% CPU", size=12, color=FIELD, bold=True))
    f.append(text(215, 225, "Ресурси діляться динамічно", size=10, color=MUTED))

    f.append(rect(80, 265, 270, 50, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(215, 285, "Ризик каскадної відмови: КРИТИЧНИЙ", size=10, color=POS, bold=True))
    f.append(text(215, 302, "Один паразит топить увесь корабель", size=9, color=POS))

    f.append(text(215, 360, "Висновок:", size=11, bold=True))
    f.append(text(215, 385, "Ідеально дешево за ресурсами,", size=10))
    f.append(text(215, 405, "але катастрофічно крихко.", size=10))

    # Середній блок: Занадто дрібні перебірки (Resource Stranding)
    f.append(rect(415, 80, 350, 430, fill=FILL, stroke=POS, sw=1.5, rx=8))
    f.append(text(590, 110, "ДРІБНІ СТАТИЧНІ ПЕРЕБІРКИ", size=12, color=POS, bold=True))
    f.append(text(590, 130, "Повна ізоляція, але втрата ємності", size=10, color=MUTED))

    # Схема Stranding
    f.append(rect(435, 150, 310, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))

    f.append(rect(450, 165, 280, 40, fill=WARM, stroke=POS, sw=1, rx=3))
    f.append(text(590, 181, "Відсік А: 100% (Переповнено, ДРОП)", size=9, color=POS, bold=True))
    f.append(text(590, 196, "Клієнти дістають HTTP 429", size=9, color=POS))

    f.append(rect(450, 215, 280, 40, fill=GOOD, stroke=FIELD, sw=1, rx=3))
    f.append(text(590, 231, "Відсік Б: 5% (Простоює 95% ресурсів)", size=9, color=FIELD, bold=True))
    f.append(text(590, 246, "Заморожена ємність (Stranded)", size=9, color=MUTED))

    f.append(rect(450, 265, 280, 40, fill=GOOD, stroke=FIELD, sw=1, rx=3))
    f.append(text(590, 281, "Відсік В: 10% (Простоює 90% ресурсів)", size=9, color=FIELD, bold=True))
    f.append(text(590, 296, "Заморожена ємність (Stranded)", size=9, color=MUTED))

    f.append(text(590, 360, "Проблема Resource Stranding:", size=11, color=POS, bold=True))
    f.append(text(590, 385, "Сервери завантажені лише на 35%,", size=10))
    f.append(text(590, 405, "але сервіс уже відхиляє користувачів,", size=10))
    f.append(text(590, 425, "бо квота А жорстко заблокована.", size=10))

    # Правий блок: Оптимальний баланс (Адаптивні перебірки)
    f.append(rect(790, 80, 350, 430, fill=FILL, stroke=FIELD, sw=2, rx=8))
    f.append(text(965, 110, "АДАПТИВНІ ПЕРЕБІРКИ (БАЛАНС)", size=12, color=FIELD, bold=True))
    f.append(text(965, 130, "Динамічні квоти + базовий резерв", size=10, color=MUTED))

    f.append(rect(810, 150, 310, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(rect(830, 170, 270, 60, fill=GOOD, stroke=FIELD, sw=1, rx=4))
    f.append(text(965, 195, "Гарантований мінімум (Floor)", size=11, color=FIELD, bold=True))
    f.append(text(965, 215, "Кожен орендар має захищений відсік", size=9, color=MUTED))

    f.append(rect(830, 240, 270, 70, fill=COOL, stroke=NEG, sw=1, rx=4))
    f.append(text(965, 265, "Спільний еластичний буфер (Burst)", size=11, color=NEG, bold=True))
    f.append(text(965, 285, "Займається за наявності вільних сил", size=9, color=MUTED))
    f.append(text(965, 301, "Швидко відбирається при дефіциті", size=9, color=NEG))

    f.append(text(965, 360, "Результат:", size=11, color=FIELD, bold=True))
    f.append(text(965, 385, "Захист від каскадного падіння 100%,", size=10))
    f.append(text(965, 405, "утилізація інфраструктури 80-85%,", size=10))
    f.append(text(965, 425, "відсутність мертвого простою.", size=10))

    render(os.path.join(OUT, 'resource-stranding.svg'), W, H, *f)


if __name__ == '__main__':
    blast_radius_containment()
    bulkhead_levels()
    threadpool_vs_semaphore()
    resource_stranding()
    print("Всі 4 фігури згенеровано успішно.")
