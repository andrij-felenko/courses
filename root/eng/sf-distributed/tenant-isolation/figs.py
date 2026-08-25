# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Мультиарендність та ізоляція орендарів'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_isolation_models():
    """Фігура 1: Спектр моделей мультиарендності — Silo, Bridge/Hybrid та Pool."""
    w, h = 860, 410
    frags = []

    frags.append(text(w / 2, 26, "Спектр архітектурних моделей ізоляції орендарів (Multi-Tenant Models)", size=15, bold=True))

    # 1. Silo Model (Повна фізична/інфраструктурна ізоляція)
    frags.append(rect(20, 50, 255, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(147, 74, "1. Silo Model (Силос)", size=13, bold=True, color=INK))
    frags.append(text(147, 90, "Окремий стек на кожного клієнта", size=10, color=MUTED))

    # Орендар А
    frags.append(rect(32, 105, 231, 105, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(147, 122, "Контур Орендаря А (Tenant A)", size=10, bold=True, color=NEG))
    frags.append(rect(42, 132, 211, 32, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    frags.append(text(147, 152, "Compute: ВМ / Pod A", size=10, bold=True, color=NEG))
    frags.append(rect(42, 168, 211, 32, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(147, 188, "Storage: Окрема БД A", size=10, bold=True, color=FIELD))

    # Орендар B
    frags.append(rect(32, 220, 231, 105, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(147, 237, "Контур Орендаря B (Tenant B)", size=10, bold=True, color=POS))
    frags.append(rect(42, 247, 211, 32, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(147, 267, "Compute: ВМ / Pod B", size=10, bold=True, color=POS))
    frags.append(rect(42, 283, 211, 32, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(147, 303, "Storage: Окрема БД B", size=10, bold=True, color=FIELD))

    frags.append(text(147, 345, "Ізоляція: Максимальна", size=10, bold=True, color=FIELD))
    frags.append(text(147, 362, "Ціна інфраструктури: Висока", size=10, color=POS))
    frags.append(text(147, 377, "Утилізація: Низька (простої)", size=9, color=MUTED))

    # 2. Bridge / Hybrid Model (Гібридна модель)
    frags.append(rect(300, 50, 255, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(427, 74, "2. Bridge Model (Гібрид)", size=13, bold=True, color=INK))
    frags.append(text(427, 90, "Спільний compute, розділений storage", size=10, color=MUTED))

    # Спільний Compute
    frags.append(rect(312, 105, 231, 75, fill="#fff7ed", stroke="#f97316", sw=1.2, rx=6))
    frags.append(text(427, 124, "Спільний stateless-шар", size=10, bold=True, color="#c2410c"))
    frags.append(rect(322, 134, 211, 36, fill="#ffffff", stroke="#f97316", sw=1, rx=4))
    frags.append(text(427, 149, "Пул веб-серверів / Pods", size=10, bold=True, color=INK))
    frags.append(text(427, 162, "Маршрутизація за Tenant Context", size=9, color=MUTED))

    frags.append(arrow(380, 185, 365, 215, color=LINE, sw=1.2))
    frags.append(arrow(475, 185, 490, 215, color=LINE, sw=1.2))

    # Розділений Storage
    frags.append(rect(312, 220, 231, 105, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(427, 237, "Розділені сховища даних", size=10, bold=True, color=INK))
    frags.append(rect(322, 247, 100, 68, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    frags.append(text(372, 270, "БД / Схема", size=10, bold=True, color=NEG))
    frags.append(text(372, 286, "Tenant A", size=10, bold=True, color=NEG))
    frags.append(text(372, 301, "(Виділено)", size=9, color=MUTED))

    frags.append(rect(433, 247, 100, 68, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(483, 270, "БД / Схема", size=10, bold=True, color=POS))
    frags.append(text(483, 286, "Tenant B", size=10, bold=True, color=POS))
    frags.append(text(483, 301, "(Виділено)", size=9, color=MUTED))

    frags.append(text(427, 345, "Ізоляція даних: Висока", size=10, bold=True, color=FIELD))
    frags.append(text(427, 362, "Ціна compute: Оптимальна", size=10, color=FIELD))
    frags.append(text(427, 377, "Підтримка схем: Помірна складність", size=9, color=MUTED))

    # 3. Pool Model (Спільна інфраструктура з логічною ізоляцією)
    frags.append(rect(580, 50, 260, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(710, 74, "3. Pool Model (Пул)", size=13, bold=True, color=INK))
    frags.append(text(710, 90, "Спільний compute та спільний storage", size=10, color=MUTED))

    # Спільний Compute
    frags.append(rect(592, 105, 236, 75, fill="#fff7ed", stroke="#f97316", sw=1.2, rx=6))
    frags.append(text(710, 124, "Спільний stateless-шар", size=10, bold=True, color="#c2410c"))
    frags.append(rect(602, 134, 216, 36, fill="#ffffff", stroke="#f97316", sw=1, rx=4))
    frags.append(text(710, 149, "Пул мікросервісів", size=10, bold=True, color=INK))
    frags.append(text(710, 162, "Контекст орендаря в пам'яті запиту", size=9, color=MUTED))

    frags.append(arrow(710, 185, 710, 215, color=LINE, sw=1.4))

    # Спільний Storage
    frags.append(rect(592, 220, 236, 105, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(710, 237, "Спільна база даних та кеш", size=10, bold=True, color=INK))
    frags.append(rect(602, 247, 216, 68, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(710, 265, "Таблиці зі стовпчиком tenant_id", size=10, bold=True, color=FIELD))
    frags.append(text(710, 281, "Захист через Row-Level Security (RLS)", size=9, color=INK))
    frags.append(text(710, 297, "і тенанто-залежні префікси ключів", size=9, color=MUTED))

    frags.append(text(710, 345, "Ефективність ресурсів: Максимальна", size=10, bold=True, color=FIELD))
    frags.append(text(710, 362, "Ціна інфраструктури: Мінімальна", size=10, color=FIELD))
    frags.append(text(710, 377, "Ризик витоку: Потребує суворого RLS", size=9, color=POS))

    return render(os.path.join(OUT, "isolation-models-spectrum.svg"), w, h, *frags)


def fig_noisy_neighbor():
    """Фігура 2: Проблема галасливого сусіда та механізм чесного планування (Fair Queuing)."""
    w, h = 860, 420
    frags = []

    frags.append(text(w / 2, 26, "Проблема «галасливого сусіда» (Noisy Neighbor) та чесний розподіл ресурсів", size=15, bold=True))

    # Ліва частина: Неізольована черга FIFO (Starvation)
    frags.append(rect(20, 50, 395, 350, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(217, 75, "Без ізоляції: Монополізація спільної черги FIFO", size=12, bold=True, color=POS))

    # Вхідні потоки
    frags.append(rect(35, 95, 160, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(115, 112, "Tenant A (Галасливий)", size=10, bold=True, color=POS))
    frags.append(text(115, 126, "1000 запитів / сек", size=9, color=POS))

    frags.append(rect(235, 95, 165, 40, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(317, 112, "Tenant B (Звичайний)", size=10, bold=True, color=NEG))
    frags.append(text(317, 126, "10 запитів / сек", size=9, color=NEG))

    frags.append(arrow(115, 138, 175, 165, color=POS, sw=1.5))
    frags.append(arrow(317, 138, 260, 165, color=NEG, sw=1.5))

    # Черга FIFO
    frags.append(rect(35, 170, 365, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(217, 187, "Спільна черга обробки (FIFO Buffer)", size=10, bold=True, color=INK))

    # Елементи черги: A A A A A B A A
    colors = [(POS, "#fdecea", "A"), (POS, "#fdecea", "A"), (POS, "#fdecea", "A"),
              (POS, "#fdecea", "A"), (POS, "#fdecea", "A"), (NEG, "#eaf0fd", "B"),
              (POS, "#fdecea", "A"), (POS, "#fdecea", "A")]
    for idx, (stroke_c, fill_c, label_c) in enumerate(colors):
        frags.append(rect(45 + idx * 43, 197, 37, 32, fill=fill_c, stroke=stroke_c, sw=1.2, rx=3))
        frags.append(text(45 + idx * 43 + 18, 218, label_c, size=11, bold=True, color=stroke_c))

    frags.append(arrow(217, 245, 217, 275, color=LINE, sw=1.5))

    # Пул воркерів
    frags.append(rect(35, 280, 365, 60, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    frags.append(text(217, 300, "Спільний пул потоків / воркерів", size=10, bold=True, color=POS))
    frags.append(text(217, 316, "99% ресурсів зайнято запитами орендаря A", size=9, color=POS))
    frags.append(text(217, 330, "Затримка Tenant B зростає з 20 мс до 15000 мс (Голодування)", size=9, bold=True, color=POS))

    frags.append(rect(35, 350, 365, 38, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(217, 366, "Наслідок: Каскадна відмова та порушення SLA", size=10, bold=True, color=POS))
    frags.append(text(217, 379, "для всіх добросовісних сусідів по вузлу", size=9, color=MUTED))

    # Права частина: Ізоляція через Fair Queuing / Token Bucket
    frags.append(rect(445, 50, 395, 350, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(642, 75, "З ізоляцією: Fair Queuing + Ліміти на орендаря", size=12, bold=True, color=FIELD))

    # Вхідні черги на орендаря
    frags.append(rect(460, 95, 175, 75, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    frags.append(text(547, 113, "Черга Tenant A (Ліміт 100)", size=10, bold=True, color=POS))
    for i in range(4):
        frags.append(rect(470 + i * 38, 124, 32, 28, fill="#fdecea", stroke=POS, sw=1, rx=3))
        frags.append(text(470 + i * 38 + 16, 142, "A", size=10, bold=True, color=POS))
    frags.append(text(547, 162, "Скидання залишку (429 Too Many Requests)", size=9, color=POS))

    frags.append(rect(650, 95, 175, 75, fill="#ffffff", stroke=NEG, sw=1.2, rx=5))
    frags.append(text(737, 113, "Черга Tenant B (Норма 10)", size=10, bold=True, color=NEG))
    frags.append(rect(712, 124, 50, 28, fill="#eaf0fd", stroke=NEG, sw=1, rx=3))
    frags.append(text(737, 142, "B (1)", size=10, bold=True, color=NEG))
    frags.append(text(737, 162, "Миттєве проходження без затримок", size=9, color=FIELD))

    # Арбітр / Диспетчер DRR
    frags.append(rect(460, 185, 365, 55, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(642, 203, "Диспетчер чесного планування (DRR / WFQ)", size=10, bold=True, color=FIELD))
    frags.append(text(642, 218, "Круговий огляд черг із дефіцитними квантами (квотами)", size=9, color=INK))
    frags.append(text(642, 231, "Гарантує справедливий доступ до процесора кожному клієнту", size=9, color=MUTED))

    frags.append(arrow(547, 172, 547, 183, color=POS, sw=1.2))
    frags.append(arrow(737, 172, 737, 183, color=NEG, sw=1.2))
    frags.append(arrow(642, 243, 642, 268, color=FIELD, sw=1.5))

    # Пул воркерів праворуч
    frags.append(rect(460, 275, 365, 65, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(642, 294, "Збалансований пул воркерів", size=10, bold=True, color=INK))
    frags.append(rect(475, 305, 160, 26, fill="#fdecea", stroke=POS, sw=1, rx=3))
    frags.append(text(555, 322, "Виділена квота A (50%)", size=9, color=POS))
    frags.append(rect(650, 305, 160, 26, fill="#eaf0fd", stroke=NEG, sw=1, rx=3))
    frags.append(text(730, 322, "Виділена квота B (50%)", size=9, color=NEG))

    frags.append(rect(460, 350, 365, 38, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(642, 366, "Результат: Стабільний SLA для Tenant B", size=10, bold=True, color=FIELD))
    frags.append(text(642, 379, "Затримка Tenant B залишається <= 20 мс під будь-яким піком", size=9, color=FIELD))

    return render(os.path.join(OUT, "noisy-neighbor-mitigation.svg"), w, h, *frags)


def fig_tenant_context():
    """Фігура 3: Наскрізне проходження контексту орендаря (Tenant Context Propagation)."""
    w, h = 860, 420
    frags = []

    frags.append(text(w / 2, 26, "Наскрізний життєвий цикл контексту орендаря (Tenant Context Lifecycle)", size=15, bold=True))

    # Крок 1: Клієнт та ідентифікація
    frags.append(rect(20, 55, 185, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(112, 80, "1. Вхідний запит", size=12, bold=True, color=INK))

    frags.append(rect(30, 98, 165, 80, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(112, 118, "Джерела Tenant ID:", size=10, bold=True, color=INK))
    frags.append(text(112, 134, "• Субдомен: acme.app.io", size=9, color=MUTED))
    frags.append(text(112, 149, "• JWT Claim: tid=t-901", size=9, color=NEG))
    frags.append(text(112, 164, "• Заголовок: X-Tenant-ID", size=9, color=MUTED))

    frags.append(rect(30, 190, 165, 190, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=5))
    frags.append(text(112, 210, "Перевірка автентичності", size=10, bold=True, color=NEG))
    frags.append(text(112, 230, "Шлюз перевіряє підпис", size=9, color=INK))
    frags.append(text(112, 245, "JWT відкритою парою", size=9, color=INK))
    frags.append(text(112, 260, "ключів (JWKS).", size=9, color=INK))
    frags.append(text(112, 285, "Захист від підміни:", size=9, bold=True, color=POS))
    frags.append(text(112, 302, "Заголовок клієнта", size=9, color=POS))
    frags.append(text(112, 317, "перезаписується", size=9, color=POS))
    frags.append(text(112, 332, "значенням із токена!", size=9, bold=True, color=POS))
    frags.append(text(112, 357, "tenant_id = 't-901'", size=10, bold=True, color=FIELD))

    frags.append(arrow(207, 225, 233, 225, color=LINE, sw=1.8))

    # Крок 2: API Gateway & Rate Limiting
    frags.append(rect(235, 55, 185, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(327, 80, "2. API Gateway", size=12, bold=True, color=INK))

    frags.append(rect(245, 98, 165, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(327, 118, "Квоти та ліміти", size=10, bold=True, color=INK))
    frags.append(text(327, 136, "Token Bucket у Redis", size=9, color=MUTED))
    frags.append(text(327, 153, "Ключ: ratelimit:t-901", size=9, bold=True, color=NEG))
    frags.append(text(327, 172, "Поточний залишок: 450", size=9, color=FIELD))
    frags.append(text(327, 190, "Ліміт: 1000 req/min", size=9, color=MUTED))
    frags.append(text(327, 206, "Статус: Дозволено (200)", size=9, bold=True, color=FIELD))

    frags.append(rect(245, 230, 165, 150, fill="#fff7ed", stroke="#f97316", sw=1.2, rx=5))
    frags.append(text(327, 250, "Ін'єкція контексту", size=10, bold=True, color="#c2410c"))
    frags.append(text(327, 270, "Додавання метаданих:", size=9, color=INK))
    frags.append(text(327, 288, "• X-Tenant-Id: t-901", size=9, bold=True, color=INK))
    frags.append(text(327, 305, "• Baggage: tid=t-901", size=9, color=MUTED))
    frags.append(text(327, 323, "• traceparent (W3C)", size=9, color=MUTED))
    frags.append(text(327, 345, "Маршрутизація у комірку", size=9, bold=True, color=INK))
    frags.append(text(327, 362, "Cell #2 (Sharded Pool)", size=9, color=FIELD))

    frags.append(arrow(422, 225, 448, 225, color=LINE, sw=1.8))

    # Крок 3: Мікросервіси та проміжне ПЗ
    frags.append(rect(450, 55, 185, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(542, 80, "3. Мікросервіси", size=12, bold=True, color=INK))

    frags.append(rect(460, 98, 165, 130, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(542, 118, "Middleware перехоплювач", size=10, bold=True, color=INK))
    frags.append(text(542, 136, "Вичитує X-Tenant-Id", size=9, color=MUTED))
    frags.append(text(542, 154, "Зберігає в ThreadLocal", size=9, bold=True, color=NEG))
    frags.append(text(542, 172, "або Go context.Context", size=9, color=NEG))
    frags.append(text(542, 192, "При фонових задачах:", size=9, bold=True, color=POS))
    frags.append(text(542, 210, "Передається в payload!", size=9, color=POS))

    frags.append(rect(460, 240, 165, 140, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(542, 260, "Кешування з ізоляцією", size=10, bold=True, color=FIELD))
    frags.append(text(542, 280, "Префікс ключів Redis:", size=9, color=INK))
    frags.append(text(542, 298, "t:t-901:orders:1044", size=9, bold=True, color=FIELD))
    frags.append(text(542, 320, "Запобігає витоку між", size=9, color=INK))
    frags.append(text(542, 335, "орендарями при однакових", size=9, color=INK))
    frags.append(text(542, 350, "внутрішніх ID сутностей", size=9, color=MUTED))
    frags.append(text(542, 365, "у спільній пам'яті кешу", size=9, color=MUTED))

    frags.append(arrow(637, 225, 663, 225, color=LINE, sw=1.8))

    # Крок 4: База даних та RLS
    frags.append(rect(665, 55, 175, 340, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(752, 80, "4. База даних (RLS)", size=12, bold=True, color=INK))

    frags.append(rect(675, 98, 155, 115, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    frags.append(text(752, 118, "Встановлення сесії", size=10, bold=True, color=INK))
    frags.append(text(752, 136, "Перед SQL-запитом:", size=9, color=MUTED))
    frags.append(text(752, 155, "SET LOCAL", size=9, bold=True, color=NEG))
    frags.append(text(752, 170, "app.current_tenant", size=9, bold=True, color=NEG))
    frags.append(text(752, 185, "= 't-901';", size=9, bold=True, color=NEG))
    frags.append(text(752, 201, "(Діє лише в транзакції)", size=9, color=MUTED))

    frags.append(rect(675, 225, 155, 155, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(752, 245, "Row-Level Security", size=10, bold=True, color=FIELD))
    frags.append(text(752, 265, "Двигун СУБД автоматично", size=9, color=INK))
    frags.append(text(752, 278, "додає предикат:", size=9, color=INK))
    frags.append(text(752, 298, "WHERE tenant_id =", size=9, bold=True, color=FIELD))
    frags.append(text(752, 313, "current_setting(...)", size=9, bold=True, color=FIELD))
    frags.append(text(752, 335, "Неможливо обійти", size=9, bold=True, color=POS))
    frags.append(text(752, 350, "через баги в ORM", size=9, color=POS))
    frags.append(text(752, 365, "чи сирі SQL-запити!", size=9, color=POS))

    return render(os.path.join(OUT, "tenant-context-propagation.svg"), w, h, *frags)


def fig_cell_architecture():
    """Фігура 4: Коміркова архітектура (Cell-Based Architecture) для обмеження радіуса ураження."""
    w, h = 860, 400
    frags = []

    frags.append(text(w / 2, 26, "Коміркова архітектура (Cell-Based Architecture) для ізоляції збоїв", size=15, bold=True))

    # Глобальний роутер зверху
    frags.append(rect(220, 50, 420, 50, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=6))
    frags.append(text(430, 70, "Глобальний маршрутизатор орендарів (Cell Router / Gateway)", size=12, bold=True, color="#c2410c"))
    frags.append(text(430, 88, "Таблиця відображення: Tenant ID -> Номер автономної комірки (Cell)", size=10, color=INK))

    frags.append(arrow(310, 102, 160, 138, color=LINE, sw=1.5))
    frags.append(arrow(430, 102, 430, 138, color=LINE, sw=1.5))
    frags.append(arrow(550, 102, 700, 138, color=LINE, sw=1.5))

    # Комірка 1 (Здорова)
    frags.append(rect(20, 140, 255, 235, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(147, 164, "Комірка 1 (Cell #1)", size=12, bold=True, color=FIELD))
    frags.append(text(147, 180, "Орендарі: #1 .. #500", size=10, bold=True, color=INK))

    frags.append(rect(35, 195, 225, 42, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(147, 212, "Stateless Compute Cluster", size=10, bold=True, color=FIELD))
    frags.append(text(147, 226, "Власні Pods, Ingress, HPA", size=9, color=MUTED))

    frags.append(rect(35, 245, 225, 42, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(147, 262, "Автономний шар даних", size=10, bold=True, color=FIELD))
    frags.append(text(147, 276, "Окремий PostgreSQL + Redis", size=9, color=MUTED))

    frags.append(rect(35, 298, 225, 62, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(147, 316, "Стан: СТАБІЛЬНИЙ", size=10, bold=True, color=FIELD))
    frags.append(text(147, 332, "Навантаження: 42% CPU", size=9, color=MUTED))
    frags.append(text(147, 348, "Повна незалежність від інших комірок", size=9, color=FIELD))

    # Комірка 2 (Збій/Галасливий сусід - локалізовано!)
    frags.append(rect(300, 140, 260, 235, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(430, 164, "Комірка 2 (Cell #2) — ЗБІЙ!", size=12, bold=True, color=POS))
    frags.append(text(430, 180, "Орендарі: #501 .. #1000", size=10, bold=True, color=POS))

    frags.append(rect(315, 195, 230, 42, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(430, 212, "Перевантаження пулу воркерів", size=10, bold=True, color=POS))
    frags.append(text(430, 226, "Атака / сплеск орендаря #742", size=9, color=POS))

    frags.append(rect(315, 245, 230, 42, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(430, 262, "БД вичерпала ліміт з'єднань", size=10, bold=True, color=POS))
    frags.append(text(430, 276, "Локалізовано в межах комірки", size=9, color=POS))

    frags.append(rect(315, 298, 230, 62, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(430, 316, "Радіус ураження: ОБМЕЖЕНИЙ", size=10, bold=True, color=POS))
    frags.append(text(430, 332, "Постраждало: лише 25% клієнтів", size=9, bold=True, color=POS))
    frags.append(text(430, 348, "Решта 75% клієнтів працюють без лагів!", size=9, bold=True, color=FIELD))

    # Комірка 3 (Здорова)
    frags.append(rect(585, 140, 255, 235, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(712, 164, "Комірка 3 (Cell #3)", size=12, bold=True, color=FIELD))
    frags.append(text(712, 180, "Орендарі: #1001 .. #1500", size=10, bold=True, color=INK))

    frags.append(rect(600, 195, 225, 42, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(712, 212, "Stateless Compute Cluster", size=10, bold=True, color=FIELD))
    frags.append(text(712, 226, "Власні Pods, Ingress, HPA", size=9, color=MUTED))

    frags.append(rect(600, 245, 225, 42, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(712, 262, "Автономний шар даних", size=10, bold=True, color=FIELD))
    frags.append(text(712, 276, "Окремий PostgreSQL + Redis", size=9, color=MUTED))

    frags.append(rect(600, 298, 225, 62, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(712, 316, "Стан: СТАБІЛЬНИЙ", size=10, bold=True, color=FIELD))
    frags.append(text(712, 332, "Навантаження: 38% CPU", size=9, color=MUTED))
    frags.append(text(712, 348, "Повна незалежність від інших комірок", size=9, color=FIELD))

    return render(os.path.join(OUT, "cell-based-tenancy.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація SVG-фігур для теми tenant-isolation...")
    fig_isolation_models()
    fig_noisy_neighbor()
    fig_tenant_context()
    fig_cell_architecture()
    print("Всі фігури згенеровано успішно.")
