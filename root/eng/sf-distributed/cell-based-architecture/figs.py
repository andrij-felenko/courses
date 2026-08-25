# -*- coding: utf-8 -*-
"""Фігури до теми «Комірки і штампи (Cell-based architecture / deployment stamps)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / ураження
COOL = "#eaf0fd"   # нейтральне / маршрутизація / запити
GOOD = "#e8f6ee"   # штатна робота / ізольована безпека
WARN = "#fef6e7"   # попередження / дренаж / прогрів


# ── 1. Порівняння радіуса ураження: спільний кластер проти комірок ───────────
def blast_radius_cellular():
    W, H = 1180, 580
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "РАДІУС УРАЖЕННЯ: єдиний спільний кластер проти коміркової архітектури",
                    size=14, bold=True, fill=COOL))

    # Ліва панель: Єдиний гігантський кластер
    f.append(rect(40, 80, 530, 470, fill=FILL, stroke=POS, sw=2, rx=8))
    f.append(text(305, 110, "ЄДИНИЙ КЛАСТЕР (100 000 ОРЕНДАРІВ)", size=13, color=POS, bold=True))
    f.append(text(305, 130, "Каскадний збій або отруйний запит руйнує всю систему", size=11, color=MUTED))

    # Спільний шар обчислень і БД
    f.append(rect(60, 150, 490, 180, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(305, 175, "Єдиний спільний пул серверів і монолітна база даних", size=12, bold=True))

    for i in range(8):
        x = 80 + (i % 4) * 115
        y = 195 + (i // 4) * 45
        f.append(rect(x, y, 105, 36, fill="#f8d7da", stroke=POS, sw=1.2, rx=4))
        f.append(text(x + 52, y + 22, "Зависло / OOM", size=9, color=POS, bold=True))

    f.append(text(305, 300, "Блокування таблиці в БД вичерпує пули з'єднань усіх сервісів", size=10, color=POS))
    f.append(text(305, 318, "Шторм повторних спроб (retry storm) добиває вцілілі репліки", size=10, color=POS))

    # Наслідки
    f.append(rect(60, 350, 490, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(305, 375, "Наслідки для бізнесу:", size=12, bold=True))

    f.append(rect(75, 395, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(145, 415, "Орендар А", size=11, bold=True))
    f.append(text(145, 432, "ВІДМОВА (503)", size=9, color=POS, bold=True))

    f.append(rect(235, 395, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(305, 415, "Орендар Б", size=11, bold=True))
    f.append(text(305, 432, "ВІДМОВА (503)", size=9, color=POS, bold=True))

    f.append(rect(395, 395, 140, 45, fill=WARM, stroke=POS, sw=1.2, rx=4))
    f.append(text(465, 415, "Орендар В...Я", size=11, bold=True))
    f.append(text(465, 432, "ВІДМОВА (503)", size=9, color=POS, bold=True))

    f.append(text(305, 475, "Катастрофа: 1 шкідливий запит зупиняє 100% бізнесу", size=11, color=POS, bold=True))
    f.append(text(305, 505, "Радіус ураження = 100% ОРЕНДАРІВ", size=13, color=POS, bold=True))

    # Права панель: Коміркова архітектура
    f.append(rect(610, 80, 530, 470, fill=FILL, stroke=FIELD, sw=2, rx=8))
    f.append(text(875, 110, "КОМІРКОВА АРХІТЕКТУРА (N = 10 КОМІРОК)", size=13, color=FIELD, bold=True))
    f.append(text(875, 130, "Повна ізоляція: кожна комірка містить весь стек сервісів і БД", size=11, color=MUTED))

    # Комірка 1 (Здорова)
    f.append(rect(630, 150, 490, 80, fill=GOOD, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(725, 175, "Комірка 1 (10 000 орендарів)", size=12, bold=True))
    f.append(text(725, 195, "Сервіси + БД + Кеш автономні", size=10, color=MUTED))
    f.append(rect(920, 165, 185, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    f.append(text(1012, 182, "100% ДОСТУПНІСТЬ", size=10, color=FIELD, bold=True))
    f.append(text(1012, 197, "Латентність: 18 мс", size=9, color=MUTED))

    # Комірка 2 (Здорова)
    f.append(rect(630, 240, 490, 80, fill=GOOD, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(725, 265, "Комірка 2 (10 000 орендарів)", size=12, bold=True))
    f.append(text(725, 285, "Сервіси + БД + Кеш автономні", size=10, color=MUTED))
    f.append(rect(920, 255, 185, 40, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    f.append(text(1012, 272, "100% ДОСТУПНІСТЬ", size=10, color=FIELD, bold=True))
    f.append(text(1012, 287, "Латентність: 19 мс", size=9, color=MUTED))

    # Комірка 3 (Аварійна)
    f.append(rect(630, 330, 490, 105, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(725, 355, "Комірка 3 (10 000 орендарів)", size=12, bold=True))
    f.append(text(725, 375, "Збій індексу / блокування БД", size=10, color=POS, bold=True))
    f.append(text(725, 395, "Аварія заблокована у межах комірки", size=9, color=POS))
    f.append(rect(920, 345, 185, 55, fill="#ffffff", stroke=POS, sw=1, rx=4))
    f.append(text(1012, 365, "УРАЖЕННЯ ЛОКАЛІЗОВАНЕ", size=9, color=POS, bold=True))
    f.append(text(1012, 383, "Постраждало: 10% клієнтів", size=9, color=POS))

    # Підсумок
    f.append(rect(630, 450, 490, 80, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(875, 475, "90 000 орендарів (90% системи) працюють без жодних деградацій", size=11, color=FIELD, bold=True))
    f.append(text(875, 505, "Радіус ураження = 1 / N = 10% ОРЕНДАРІВ", size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, "blast-radius-cellular.svg"), W, H, *f)


# ── 2. Топологія коміркової архітектури: Маршрутизатор і автономні штампи ────
def cellular_topology():
    W, H = 1180, 620
    f = []

    # Заголовок
    f.append(fitbox(40, 15, 1100, 40,
                    "ТОПОЛОГІЯ КОМІРКОВОЇ АРХІТЕКТУРИ: Тонкий маршрутизатор і автономні штампи",
                    size=14, bold=True, fill=COOL))

    # Вхідний трафік
    f.append(rect(430, 68, 320, 42, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(590, 94, "Вхідний Інтернет-трафік (Anycast / DNS / Edge CDN)", size=11, bold=True))

    # Стрілка вниз
    f.append(arrow(590, 110, 590, 135, color=LINE, sw=2))

    # Тонкий шар маршрутизації (Cell Router)
    f.append(rect(140, 135, 900, 90, fill=COOL, stroke=NEG, sw=2, rx=8))
    f.append(text(590, 158, "ШАР МАРШРУТИЗАЦІЇ КОМІРОК (CELL ROUTING LAYER)", size=13, color=NEG, bold=True))
    f.append(text(590, 178, "Безстатусний проксі (Envoy / eBPF / Nginx): вилучає Tenant ID та обирає цільову комірку", size=11, color=INK))
    f.append(text(590, 198, "Джерела правил: детерміноване хешування або кешований реєстр мапінгу (In-Memory Directory)", size=10, color=MUTED))

    # Стрілки маршрутизації до трьох комірок
    f.append(arrow(300, 225, 230, 275, color=NEG, sw=1.8))
    f.append(arrow(590, 225, 590, 275, color=NEG, sw=1.8))
    f.append(arrow(880, 225, 950, 275, color=NEG, sw=1.8))

    # Три автономні комірки (штампи)
    cells = [
        (40, "КОМІРКА 1 (ШТАМП A)", "Орендарі 1..10 000", GOOD, FIELD),
        (420, "КОМІРКА 2 (ШТАМП B)", "Орендарі 10 001..20 000", GOOD, FIELD),
        (800, "КОМІРКА N (ШТАМП N)", "Орендарі (N-1)·K..N·K", GOOD, FIELD)
    ]

    for cx, ctitle, csub, cfill, cstroke in cells:
        f.append(rect(cx, 275, 340, 320, fill=FILL, stroke=cstroke, sw=1.8, rx=8))
        f.append(rect(cx + 10, 285, 320, 45, fill=cfill, stroke=cstroke, sw=1.2, rx=6))
        f.append(text(cx + 170, 305, ctitle, size=12, color=cstroke, bold=True))
        f.append(text(cx + 170, 322, csub, size=10, color=MUTED))

        # Компоненти всередині комірки
        # 1. API Gateway
        f.append(rect(cx + 20, 340, 300, 38, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(cx + 170, 363, "Внутрішній API Gateway комірки", size=10, bold=True))

        # 2. App Services
        f.append(rect(cx + 20, 388, 300, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(cx + 170, 408, "Флот мікросервісів комірки", size=10, bold=True))
        f.append(text(cx + 170, 426, "Оплата · Каталог · Замовлення · Користувачі", size=9, color=MUTED))

        # 3. Storage & Queues
        f.append(rect(cx + 20, 448, 145, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(cx + 92, 473, "Виділена БД", size=10, bold=True))
        f.append(text(cx + 92, 492, "PostgreSQL / DB", size=9, color=MUTED))

        f.append(rect(cx + 175, 448, 145, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(cx + 247, 473, "Локальні черги", size=10, bold=True))
        f.append(text(cx + 247, 492, "Kafka / RabbitMQ", size=9, color=MUTED))

        # 4. Workers
        f.append(rect(cx + 20, 518, 300, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(cx + 170, 542, "Фонові обробники (In-Cell Workers)", size=10, bold=True))

        # Статус автономності
        f.append(text(cx + 170, 580, "Нуль спільних синхронних залежностей", size=9, color=cstroke, bold=True))

    render(os.path.join(OUT, "cellular-topology.svg"), W, H, *f)


# ── 3. Перемішане шардування комірок (Shuffle Sharding) ───────────────────────
def shuffle_sharding_grid():
    W, H = 1180, 580
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "ПЕРЕМІШАНЕ ШАРДУВАННЯ (SHUFFLE SHARDING): Комбінаторна ізоляція орендарів",
                    size=14, bold=True, fill=COOL))

    # Опис концепції
    f.append(rect(40, 75, 1100, 55, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(590, 98, "Загальний пул з N = 8 комірок. Кожен орендар отримує унікальну комбінацію з K = 2 комірок.", size=12, bold=True))
    f.append(text(590, 118, "Кількість унікальних віртуальних штампів: C(8, 2) = 8! / (2! · 6!) = 28 ізольованих комбінацій.", size=11, color=MUTED))

    # Стовпці 8 фізичних комірок
    cell_w = 115
    start_x = 90
    cell_x_coords = []
    for i in range(8):
        cx = start_x + i * 126
        cell_x_coords.append(cx)
        is_corrupted = (i == 2)  # Комірка 2 зазнала аварії
        cfill = WARM if is_corrupted else COOL
        cstroke = POS if is_corrupted else NEG
        f.append(rect(cx, 145, cell_w, 45, fill=cfill, stroke=cstroke, sw=1.5, rx=6))
        f.append(text(cx + cell_w / 2, 165, f"Комірка {i}", size=11, bold=True, color=cstroke))
        f.append(text(cx + cell_w / 2, 180, "АВАРІЯ (OOM)" if is_corrupted else "Норма", size=9, color=cstroke))

    # Рядки 4 різних орендарів
    tenants = [
        ("Орендар A", [0, 2], "Комбінація {0, 2}", WARM),
        ("Орендар Б", [1, 5], "Комбінація {1, 5}", GOOD),
        ("Орендар В", [2, 6], "Комбінація {2, 6}", WARM),
        ("Орендар Г", [3, 7], "Комбінація {3, 7}", GOOD)
    ]

    ty_start = 210
    for idx, (tname, assigned_cells, tcomb, tstatus_fill) in enumerate(tenants):
        ty = ty_start + idx * 80
        f.append(rect(40, ty, 1100, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))

        # Назва орендаря
        f.append(rect(55, ty + 12, 140, 46, fill=tstatus_fill, stroke=LINE, sw=1, rx=4))
        f.append(text(125, ty + 30, tname, size=11, bold=True))
        f.append(text(125, ty + 48, tcomb, size=9, color=MUTED))

        # Позначки на сітці комірок
        for ci in range(8):
            cx = cell_x_coords[ci]
            in_tenant = ci in assigned_cells
            if in_tenant:
                is_failed = (ci == 2)
                dot_fill = "#f8d7da" if is_failed else "#d4edda"
                dot_stroke = POS if is_failed else FIELD
                dot_label = "ЗБІЙ" if is_failed else "АКТИВНА"
                f.append(rect(cx + 10, ty + 12, cell_w - 20, 46, fill=dot_fill, stroke=dot_stroke, sw=1.5, rx=4))
                f.append(text(cx + cell_w / 2, ty + 38, dot_label, size=9, color=dot_stroke, bold=True))
            else:
                f.append(circle(cx + cell_w / 2, ty + 35, 4, fill="#e0e0e0", stroke="#cccccc", sw=1))

    # Нижній висновок
    f.append(rect(40, 535, 1100, 35, fill=GOOD, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(590, 557, "Комбінаторний захист: навіть при повному краху Комірки 2 ЖОДЕН клієнт не втрачає зв'язок повністю!", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "shuffle-sharding-grid.svg"), W, H, *f)


# ── 4. Життєвий цикл і скінченний автомат комірки (Cell Lifecycle) ───────────
def cell_lifecycle_fsm():
    W, H = 1180, 520
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "СКІНЧЕННИЙ АВТОМАТ ШТАМПУ РОЗГОРТАННЯ: Життєвий цикл комірки",
                    size=14, bold=True, fill=COOL))

    # П'ять станів
    states = [
        (60, 210, "1. PROVISIONING", "Розгортання IaC", "Виділення VM/Kube,\nстворення БД та шин", COOL, NEG),
        (280, 210, "2. WARMING", "Прогрів і канарка", "Прогрів кешу,\nтестовий трафік", WARN, "#d35400"),
        (510, 210, "3. ACTIVE", "Штатне обслуговування", "Прийом трафіку орендарів,\nвиконання SLA", GOOD, FIELD),
        (740, 210, "4. DRAINING", "Дренаж і виведення", "Зупинка нових сесій,\nзлив черг і міграція", WARN, "#d35400"),
        (960, 210, "5. TERMINATED", "Знищення ресурсів", "Видалення інфраструктури,\nархівація даних", WARM, POS)
    ]

    for sx, sy, stitle, ssub, sbody, sfill, sstroke in states:
        f.append(rect(sx, sy, 160, 150, fill=sfill, stroke=sstroke, sw=2, rx=8))
        f.append(text(sx + 80, sy + 28, stitle, size=11, color=sstroke, bold=True))
        f.append(text(sx + 80, sy + 48, ssub, size=10, bold=True))
        f.append(line(sx + 10, sy + 58, sx + 150, sy + 58, color=sstroke, sw=1, dash="3,3"))
        lines = sbody.split("\n")
        for li, ln in enumerate(lines):
            f.append(text(sx + 80, sy + 82 + li * 20, ln, size=9, color=INK))

    # Стрілки переходів
    # 1 -> 2
    f.append(arrow(220, 285, 275, 285, color=NEG, sw=2))
    f.append(text(250, 272, "IaC Ready", size=9, color=NEG, bold=True))

    # 2 -> 3
    f.append(arrow(440, 285, 505, 285, color=FIELD, sw=2))
    f.append(text(475, 272, "Health OK", size=9, color=FIELD, bold=True))

    # 3 -> 4
    f.append(arrow(670, 285, 735, 285, color="#d35400", sw=2))
    f.append(text(705, 272, "Drain Trigger", size=9, color="#d35400", bold=True))

    # 4 -> 5
    f.append(arrow(900, 285, 955, 285, color=POS, sw=2))
    f.append(text(930, 272, "Drained", size=9, color=POS, bold=True))

    # Зворотний перехід: 2 -> 5 (якщо прогрів провалився)
    f.append(line(360, 360, 360, 420, color=POS, sw=1.5))
    f.append(line(360, 420, 1040, 420, color=POS, sw=1.5))
    f.append(arrow(1040, 420, 1040, 365, color=POS, sw=1.5))
    f.append(text(650, 410, "Збій верифікації прогріву (Canary Failure) → Миттєве знищення", size=10, color=POS, bold=True))

    # Зворотний перехід: 4 -> 3 (скасування дренажу в разі помилки оператора)
    f.append(line(820, 210, 820, 150, color=MUTED, sw=1.5))
    f.append(line(820, 150, 590, 150, color=MUTED, sw=1.5))
    f.append(arrow(590, 150, 590, 205, color=MUTED, sw=1.5))
    f.append(text(705, 140, "Скасування дренажу (Rollback)", size=9, color=MUTED, bold=True))

    # Опис автоматизації знизу
    f.append(rect(40, 455, 1100, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(590, 475, "Автоматизація Control Plane: реєстрація нової комірки в роутерах відбувається ВИКЛЮЧНО після переходу в ACTIVE.", size=10, bold=True))
    f.append(text(590, 492, "При переході в DRAINING роутери миттєво припиняють направляти нових орендарів, дозволяючи поточним завершити роботу.", size=9, color=MUTED))

    render(os.path.join(OUT, "cell-lifecycle-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    blast_radius_cellular()
    cellular_topology()
    shuffle_sharding_grid()
    cell_lifecycle_fsm()
    print("Figures generated successfully.")
