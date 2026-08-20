# -*- coding: utf-8 -*-
"""Генератор діаграм для теми offline-first-client."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')


def fig_offline_vs_online():
    """Порівняння Online-First та Offline-First архітектур."""
    w, h = 820, 360
    frags = []

    # Заголовок
    frags.append(text(w / 2, 25, "Порівняння архітектур: Онлайн-перший проти Офлайн-першого", size=16, bold=True))

    # Ліва колонка: Online-First
    col1_x, col1_w = 30, 365
    frags.append(rect(col1_x, 45, col1_w, 295, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    frags.append(text(col1_x + col1_w / 2, 70, "Онлайн-перший підхід (Online-First)", size=14, color=POS, bold=True))
    frags.append(text(col1_x + col1_w / 2, 88, "Мережа як обов'язкова передумова дії", size=11, color=MUTED, italic=True))

    # Блоки лівої колонки
    frags.append(fitbox(col1_x + 30, 105, 305, 45, "Інтерфейс користувача (UI)\nКлік / Ввід тексту", size=12, fill="#ffffff", stroke=LINE))
    frags.append(arrow(col1_x + 182, 150, col1_x + 182, 175, color=POS, sw=1.8))
    frags.append(text(col1_x + 182, 168, "HTTP POST / Блокування", size=10, color=POS, bold=True, anchor="middle"))

    frags.append(fitbox(col1_x + 30, 180, 305, 50, "Мережевий транспорт (RPC / REST)\nСпінер очікування (Spinner)", size=12, fill="#fff0f0", stroke=POS))
    frags.append(arrow(col1_x + 182, 230, col1_x + 182, 255, color=LINE, sw=1.8))

    frags.append(fitbox(col1_x + 30, 260, 305, 45, "База даних сервера\nЄдине джерело правди", size=12, fill="#ffffff", stroke=LINE))
    frags.append(text(col1_x + col1_w / 2, 325, "Збій мережі = зависання UI та втрата вводу", size=11, color=POS, bold=True))

    # Права колонка: Offline-First
    col2_x, col2_w = 425, 365
    frags.append(rect(col2_x, 45, col2_w, 295, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col2_x + col2_w / 2, 70, "Офлайн-перший підхід (Offline-First)", size=14, color=FIELD, bold=True))
    frags.append(text(col2_x + col2_w / 2, 88, "Локальна база — правда, мережа — транспорт", size=11, color=MUTED, italic=True))

    # Блоки правої колонки
    frags.append(fitbox(col2_x + 30, 105, 305, 45, "Інтерфейс користувача (UI)\nМиттєвий відгук (0 мс)", size=12, fill="#ffffff", stroke=LINE))
    frags.append(arrow(col2_x + 182, 150, col2_x + 182, 175, color=FIELD, sw=1.8))
    frags.append(text(col2_x + 182, 168, "Локальний запис (Транзакція)", size=10, color=FIELD, bold=True, anchor="middle"))

    frags.append(fitbox(col2_x + 30, 180, 305, 50, "Локальна БД (IndexedDB / SQLite)\n+ Черга мутацій (Outbox Queue)", size=12, fill="#eef8f2", stroke=FIELD))
    frags.append(arrow(col2_x + 182, 230, col2_x + 182, 255, color=LINE, sw=1.8))
    frags.append(text(col2_x + 182, 248, "Асинхронна реплікація", size=10, color=MUTED, italic=True, anchor="middle"))

    frags.append(fitbox(col2_x + 30, 260, 305, 45, "Шлюз синхронізації та Серверна БД\nУзгодження копій (Reconciliation)", size=12, fill="#ffffff", stroke=LINE))
    frags.append(text(col2_x + col2_w / 2, 325, "Збій мережі = звичайна робота з локальною чергою", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "offline-vs-online-architecture.svg"), w, h, *frags)


def fig_mutation_outbox_lifecycle():
    """Життєвий цикл мутації в черзі вихідних повідомлень (Outbox)."""
    w, h = 820, 340
    frags = []

    frags.append(text(w / 2, 25, "Життєвий цикл мутації в черзі клієнта (Mutation Outbox)", size=16, bold=True))

    # Стан 1: Створення й PENDING
    frags.append(fitbox(30, 70, 160, 60, "PENDING\nЗаписано в Outbox\nОптимістичний стан", size=12, fill="#fdf8e2", stroke="#d4a017"))

    # Стрілка 1 -> 2
    frags.append(arrow(190, 100, 260, 100, color=LINE, sw=1.8))
    frags.append(text(225, 90, "Відправка", size=10, color=MUTED, bold=True))

    # Стан 2: IN_FLIGHT
    frags.append(fitbox(260, 70, 160, 60, "IN_FLIGHT\nЗапит летить у мережі\nТаймер таймауту", size=12, fill="#eaf0fd", stroke=NEG))

    # Стрілка 2 -> 3 (Успіх ACK)
    frags.append(arrow(420, 100, 500, 100, color=FIELD, sw=1.8))
    frags.append(text(460, 90, "200 OK / ACK", size=10, color=FIELD, bold=True))

    # Стан 3: COMMITTED
    frags.append(fitbox(500, 70, 160, 60, "COMMITTED\nПідтверджено сервером\nОчищення з черги", size=12, fill="#eef8f2", stroke=FIELD))

    # Стрілка 2 -> 4 (Мережева помилка / 5xx)
    frags.append(arrow(340, 130, 340, 200, color=POS, sw=1.8))
    frags.append(text(348, 165, "Мережевий обрив / 5xx", size=10, color=POS, bold=True, anchor="start"))

    # Стан 4: RETRY_BACKOFF
    frags.append(fitbox(260, 200, 160, 60, "RETRY_BACKOFF\nЕкспоненційний відступ\n+ Random Jitter", size=12, fill="#fdecea", stroke=POS))

    # Стрілка 4 -> 1 (Повернення на повтор)
    frags.append(line(260, 230, 110, 230, color=LINE, sw=1.5, dash="4,4"))
    frags.append(arrow(110, 230, 110, 130, color=LINE, sw=1.8))
    frags.append(text(185, 220, "Сплив таймер паузи", size=10, color=MUTED, bold=True))

    # Стан 5: CONFLICT / ROLLBACK
    frags.append(fitbox(500, 200, 160, 60, "CONFLICT / ROLLBACK\nВідхилено бізнес-правилом\nВідкат оптимізму", size=12, fill="#fff0f0", stroke=POS))

    # Стрілка 2 -> 5 (Відхилення 4xx / Конфлікт)
    frags.append(arrow(390, 130, 520, 200, color=POS, sw=1.8))
    frags.append(text(480, 160, "409 Conflict / 422", size=10, color=POS, bold=True, anchor="start"))

    # Пояснення внизу
    frags.append(text(w / 2, 315, "Інваріант: мутація видаляється з черги ЛИШЕ після підтвердження сервером або остаточного відкату", size=11, color=INK, italic=True))

    render(os.path.join(OUT_DIR, "mutation-outbox-lifecycle.svg"), w, h, *frags)


def fig_sync_two_phase():
    """Двофазна реконсиляція: вивантаження мутацій (Push) та отримання дельт (Pull)."""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 25, "Двофазне узгодження: Push локальних мутацій і Pull віддалених дельт", size=16, bold=True))

    # Вертикальні лінії учасників
    c_x, s_x = 220, 620
    frags.append(fitbox(c_x - 90, 48, 180, 42, "Клієнт (Client Sync Engine)\nЛокальна БД + Outbox", size=11, fill="#eef8f2", stroke=FIELD))
    frags.append(fitbox(s_x - 90, 48, 180, 42, "Сервер (Replication Gateway)\nСерверний журнал подій", size=11, fill="#eaf0fd", stroke=NEG))

    frags.append(line(c_x, 90, c_x, 380, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(s_x, 90, s_x, 380, color=MUTED, sw=1.5, dash="4,4"))

    # Фаза 1: Push
    frags.append(rect(30, 105, 780, 120, fill="#fafafa", stroke="#e0e0e0", sw=1, rx=6))
    frags.append(text(45, 125, "Фаза 1: Вивантаження черги мутацій (Push Local Changes)", size=11, color=FIELD, bold=True, anchor="start"))

    frags.append(arrow(c_x, 155, s_x, 155, color=LINE, sw=1.8))
    frags.append(text((c_x + s_x) / 2, 145, "POST /sync/push { client_id, mutations: [M1, M2], base_seq: 140 }", size=11, color=INK, bold=True))

    frags.append(arrow(s_x, 205, c_x, 205, color=FIELD, sw=1.8))
    frags.append(text((c_x + s_x) / 2, 195, "200 OK { acknowledged: [M1_id, M2_id], server_seq: 142 }", size=11, color=FIELD, bold=True))

    # Фаза 2: Pull
    frags.append(rect(30, 240, 780, 130, fill="#fafafa", stroke="#e0e0e0", sw=1, rx=6))
    frags.append(text(45, 260, "Фаза 2: Затягування чужих змін (Pull Remote Changes)", size=11, color=NEG, bold=True, anchor="start"))

    frags.append(arrow(c_x, 290, s_x, 290, color=LINE, sw=1.8))
    frags.append(text((c_x + s_x) / 2, 280, "GET /sync/pull?since_seq=140&client_id=C1", size=11, color=INK, bold=True))

    frags.append(arrow(s_x, 340, c_x, 340, color=NEG, sw=1.8))
    frags.append(text((c_x + s_x) / 2, 330, "200 OK { deltas: [Δ_User2, Δ_User3], new_seq: 145, has_more: false }", size=11, color=NEG, bold=True))

    # Підсумок
    frags.append(text(w / 2, 400, "Результат: локальний стан узгоджено з сервером, черга очищена від підтверджених операцій", size=11, color=INK, italic=True))

    render(os.path.join(OUT_DIR, "sync-two-phase-reconciliation.svg"), w, h, *frags)


def fig_conflict_resolution_spectrum():
    """Спектр стратегій розв'язання конфліктів у реплікації."""
    w, h = 820, 290
    frags = []

    frags.append(text(w / 2, 25, "Спектр стратегій розв'язання конфліктів реплікації", size=16, bold=True))

    # Вісь складності та збереження даних
    frags.append(arrow(50, 60, 770, 60, color=LINE, sw=2))
    frags.append(text(760, 50, "Точність збереження наміру та складність моделі →", size=11, color=MUTED, bold=True, anchor="end"))

    # 4 блоки стратегій
    bw, bh = 175, 170
    y_box = 80

    # Стратегія 1: LWW
    frags.append(fitbox(40, y_box, bw, bh,
        "1. Last-Write-Wins (LWW)\n\n"
        "• Фізичний годинник (NTP)\n"
        "• Більший timestamp перемагає\n"
        "• Перевага: простота\n"
        "• Плата: втрата правок при\n"
        "дрейфі годинника або гонках",
        size=11, fill="#fff5f5", stroke=POS))

    # Стратегія 2: 3-Way Merge
    frags.append(fitbox(230, y_box, bw, bh,
        "2. Три-стороннє злиття\n\n"
        "• Звіряння Base + Our + Their\n"
        "• Автозлиття непересічних полів\n"
        "• Перевага: зрозуміла модель\n"
        "• Плата: блокування при\n"
        "перетині правок в одному полі",
        size=11, fill="#fdf8e2", stroke="#d4a017"))

    # Стратегія 3: Векторні годинники
    frags.append(fitbox(420, y_box, bw, bh,
        "3. Версійні вектори\n\n"
        "• Причинний порядок V₁ < V₂\n"
        "• Детекція паралельності V₁ || V₂\n"
        "• Перевага: точне виявлення колізій\n"
        "• Плата: збереження множинних\n"
        "версій (siblings / MV-register)",
        size=11, fill="#eaf0fd", stroke=NEG))

    # Стратегія 4: CRDTs
    frags.append(fitbox(610, y_box, bw, bh,
        "4. Безконфліктні типи (CRDT)\n\n"
        "• Комутативні напівґратки (⊔)\n"
        "• Детерміністичне автозлиття\n"
        "• Перевага: 100% збіжність без втрат\n"
        "• Плата: оверхед на метадані\n"
        "та надгробки (tombstones)",
        size=11, fill="#eef8f2", stroke=FIELD))

    # Підпис знизу
    frags.append(text(w / 2, 275, "Вибір стратегії залежить від гранулярності даних: LWW для профілю, 3-Way для форм, CRDT для спільного тексту", size=11, color=INK, italic=True))

    render(os.path.join(OUT_DIR, "conflict-resolution-spectrum.svg"), w, h, *frags)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    fig_offline_vs_online()
    fig_mutation_outbox_lifecycle()
    fig_sync_two_phase()
    fig_conflict_resolution_spectrum()
    print("Згенеровано 4 фігури в img/")
