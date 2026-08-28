# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Етапи канаркового розгортання та спрацювання Kill Switch ─────────
def fig_canary_rollout_stages():
    W, H = 1000, 560
    frags = []

    frags.append(text(500, 25, "Етапи поетапного розгортання, аналіз аномалій (ACA) та аварійний Kill Switch",
                      size=15, bold=True, color=INK))

    # Фаза 1: 1% Canary
    b1 = rect(40, 65, 200, 220, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6)
    frags.append(b1)
    frags.append(text(140, 90, "Фаза 1: 1% Canary", size=13, bold=True, color=NEG))
    frags.append(text(140, 110, "Мінімальний радіус ураження", size=10, italic=True, color=MUTED))
    frags.append(rect(55, 130, 170, 45, fill="#ffffff", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(140, 148, "1% трафіку на v2.0", size=11, bold=True, color=INK))
    frags.append(text(140, 165, "99% трафіку на v1.0", size=10, color=MUTED))
    frags.append(text(140, 200, "Період прогріву: 15 хв", size=10, bold=False, color=INK))
    frags.append(text(140, 220, "Синтетичні зонди OK", size=10, color=FIELD))
    frags.append(text(140, 240, "SLI: Помилки < 0.01%", size=10, color=FIELD))
    frags.append(text(140, 265, "Автоматичний перехід →", size=10, bold=True, color=NEG))

    # Стрілка 1 -> 2
    frags.append(arrow(240, 175, 275, 175, color=INK, sw=1.8))

    # Фаза 2: 10% Staged
    b2 = rect(280, 65, 200, 220, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6)
    frags.append(b2)
    frags.append(text(380, 90, "Фаза 2: 10% Staged", size=13, bold=True, color=FIELD))
    frags.append(text(380, 110, "Статистична вибірка ACA", size=10, italic=True, color=MUTED))
    frags.append(rect(295, 130, 170, 45, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(380, 148, "10% трафіку на v2.0", size=11, bold=True, color=INK))
    frags.append(text(380, 165, "90% трафіку на v1.0", size=10, color=MUTED))
    frags.append(text(380, 200, "Тест Манна-Вітні: p > 0.05", size=10, color=INK))
    frags.append(text(380, 220, "Затримка p99: +1.2 мс (Норма)", size=10, color=FIELD))
    frags.append(text(380, 240, "Вичерпання бюджету: 0%", size=10, color=FIELD))
    frags.append(text(380, 265, "Автоматичний перехід →", size=10, bold=True, color=FIELD))

    # Стрілка 2 -> 3
    frags.append(arrow(480, 175, 515, 175, color=INK, sw=1.8))

    # Фаза 3: 50% Mixed Fleet (Аномалія)
    b3 = rect(520, 65, 210, 220, fill="#fff1f2", stroke=POS, sw=2.0, rx=6)
    frags.append(b3)
    frags.append(text(625, 90, "Фаза 3: 50% Mixed Fleet", size=13, bold=True, color=POS))
    frags.append(text(625, 110, "Критична точка стійкості", size=10, italic=True, color=MUTED))
    frags.append(rect(535, 130, 180, 45, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(625, 148, "50% v2.0 | 50% v1.0", size=11, bold=True, color=POS))
    frags.append(text(625, 165, "Виявлено сплеск затримок!", size=10, bold=True, color=POS))
    frags.append(text(625, 200, "Аномалія: Витік пам'яті", size=10, bold=True, color=POS))
    frags.append(text(625, 220, "Затримка p99: 450 мс (+380%)", size=10, color=POS))
    frags.append(text(625, 240, "Burn Rate бюджету = 14.2x", size=10, bold=True, color=POS))
    frags.append(text(625, 265, "ТРИГЕР ЗУПИНКИ!", size=11, bold=True, color=POS))

    # Стрілка вниз до аварійного блоку
    frags.append(arrow(625, 285, 625, 330, color=POS, sw=2.5))

    # Блок Аварійного Світча (Kill Switch)
    b_kill = rect(280, 330, 680, 200, fill="#fef2f2", stroke=POS, sw=2.0, rx=8)
    frags.append(b_kill)
    frags.append(text(620, 355, "РЕЖИМ ЕКСТРЕНОЇ ЗУПИНКИ ТА ЛОКАЛІЗАЦІЇ (KILL SWITCH)", size=13, bold=True, color=POS))

    # Дії аварійного сценарію
    action1, _, _ = textbox(410, 410, "1. L7 Маршрутизатор (Envoy/ALB):\nМиттєве скидання ваги v2.0 → 0%\nВесь вхідний потік повертається на v1.0",
                            size=10, bold=False, fill="#ffffff", stroke=POS, sw=1.0, pad=6)
    action2, _, _ = textbox(630, 410, "2. Дренаж вузлів (Graceful Drain):\nТайм-аут завершення сокетів: 30 с\nЗаборона нових клієнтських викликів",
                            size=10, bold=False, fill="#ffffff", stroke=POS, sw=1.0, pad=6)
    action3, _, _ = textbox(840, 410, "3. Fencing Token & Епоха:\nІнкремент епохи консенсусу\nБлокування мутацій від v2.0 у БД",
                            size=10, bold=False, fill="#ffffff", stroke=POS, sw=1.0, pad=6)
    frags.append(action1)
    frags.append(action2)
    frags.append(action3)

    # Статус парку
    status_box, _, _ = textbox(620, 490, "Стан парку після зупинки: 50% вузлів v2.0 ізольовано для діагностики (Core Dump / Heap Profiling)\nРобочий продакшн стабілізовано на 100% v1.0 без деградації клієнтських операцій",
                               size=10, bold=True, fill="#ffffff", stroke="#7e22ce", sw=1.2, pad=8)
    frags.append(status_box)

    # Лівий блок: Моніторинг та телеметрія
    b_mon = rect(40, 330, 210, 200, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8)
    frags.append(b_mon)
    frags.append(text(145, 355, "Контролер телеметрії", size=12, bold=True, color=INK))
    frags.append(text(145, 380, "• Prometheus / OpenTelemetry", size=10, color=INK))
    frags.append(text(145, 405, "• Sliding Window Burn Rate", size=10, color=INK))
    frags.append(text(145, 430, "• Автоматичний валідатор SLI", size=10, color=INK))
    frags.append(text(145, 455, "• Deadman's Switch зонд", size=10, color=INK))
    frags.append(text(145, 495, "Опитування кожні 2 с", size=10, italic=True, color=MUTED))

    # Стрілка від моніторингу до Kill switch
    frags.append(arrow(250, 430, 280, 430, color=POS, sw=2.0))

    render(os.path.join(IMG, 'canary-rollout-stages.svg'), W, H, *frags,
           title="Етапи канаркового розгортання та механізм Kill Switch")


# ── Фігура 2: Зворотна та пряма сумісність у змішаному парку (Mixed Fleet) ───
def fig_mixed_fleet_protocol_compatibility():
    W, H = 1000, 560
    frags = []

    frags.append(text(500, 25, "Взаємодія у змішаному парку (Mixed Fleet): сумісність протоколів та ізоляція стану",
                      size=15, bold=True, color=INK))

    # Ліва частина: Вузол v1.0 (Legacy)
    v1_box = rect(50, 70, 380, 230, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8)
    frags.append(v1_box)
    frags.append(text(240, 95, "ВУЗОЛ СТАРОЇ ВЕРСІЇ (v1.0)", size=13, bold=True, color=NEG))
    frags.append(text(240, 115, "Парк оновлено на 50% — працює паралельно з v2.0", size=10, italic=True, color=MUTED))

    p1, _, _ = textbox(240, 160, "Схема повідомлення v1:\n• tag 1: transaction_id (uint64)\n• tag 2: amount_cents (uint64)\n• tag 3: timestamp (uint64)",
                       size=10, bold=False, fill="#ffffff", stroke=NEG, sw=1.0, pad=6)
    p2, _, _ = textbox(240, 245, "Обробка невідомих полів:\nЗбереження unknown fields у бінарному буфері\nЗапобігання втраті даних при транзиті через v1",
                       size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    frags.append(p1)
    frags.append(p2)

    # Права частина: Вузол v2.0 (Canary)
    v2_box = rect(570, 70, 380, 230, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8)
    frags.append(v2_box)
    frags.append(text(760, 95, "ВУЗОЛ НОВОЇ ВЕРСІЇ (v2.0)", size=13, bold=True, color=FIELD))
    frags.append(text(760, 115, "Канаркова ревізія з розширеним бінарним контрактом", size=10, italic=True, color=MUTED))

    p3, _, _ = textbox(760, 160, "Схема повідомлення v2 (Розширена):\n• tag 1: transaction_id (uint64)\n• tag 2: amount_cents (uint64)\n• tag 3: timestamp (uint64)\n• tag 4: currency_code (string, OPTIONAL)\n• tag 5: trace_context (bytes, OPTIONAL)",
                       size=10, bold=False, fill="#ffffff", stroke=FIELD, sw=1.0, pad=6)
    p4, _, _ = textbox(760, 255, "Пряма сумісність (Forward Compatibility):\nОбов'язкові дефолтні значення для відсутніх полів v1\nОбробка запитів від клієнтів зі старою схемою",
                       size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    frags.append(p3)
    frags.append(p4)

    # Двосторонні мережеві зв'язки RPC між v1 та v2
    frags.append(arrow(430, 140, 570, 140, color=NEG, sw=2.0))
    frags.append(text(500, 130, "RPC v1 → v2 (Forward)", size=10, bold=True, color=NEG))

    frags.append(arrow(570, 190, 430, 190, color=FIELD, sw=2.0))
    frags.append(text(500, 205, "RPC v2 → v1 (Backward)", size=10, bold=True, color=FIELD))

    # Середня нижня частина: Шар Консенсусу та Епох (Fencing Token)
    fence_box = rect(50, 330, 430, 195, fill="#fff9e6", stroke="#d97706", sw=1.8, rx=8)
    frags.append(fence_box)
    frags.append(text(265, 355, "МЕХАНІЗМ ЗАПОБІГАННЯ SPLIT-BRAIN", size=12, bold=True, color="#d97706"))
    frags.append(text(265, 375, "Розподілений консенсус (Raft / Lease / Fencing)", size=10, italic=True, color=MUTED))

    f1, _, _ = textbox(265, 430, "• Генераційні токени (Epoch Fencing Tokens)\n• Кожен запис супроводжується номером релізу\n• Вузли старої епохи автоматично відхиляються\n• Захист від подвійної обробки транзакцій",
                       size=10, bold=False, fill="#ffffff", stroke="#d97706", sw=1.0, pad=6)
    frags.append(f1)
    frags.append(text(265, 500, "Ідемпотентність операцій за ключем UUIDv7", size=10, bold=True, color=INK))

    # Права нижня частина: Спільна СУБД та Expand-Contract
    db_box = rect(520, 330, 430, 195, fill="#faf5ff", stroke="#7e22ce", sw=1.8, rx=8)
    frags.append(db_box)
    frags.append(text(735, 355, "СУМІСНІСТЬ СХЕМИ СУБД (EXPAND-CONTRACT)", size=12, bold=True, color="#7e22ce"))
    frags.append(text(735, 375, "Спільна база даних при частковому розгортанні", size=10, italic=True, color=MUTED))

    d1, _, _ = textbox(735, 430, "• Фаза Expand: нові стовпці NULLable з тригерами\n• Подвійний запис (Dual-Write) у старі та нові поля\n• Старі вузли v1 не ламаються при читанні рядків\n• У разі зупинки кампанії відкат не потребує DDL",
                       size=10, bold=False, fill="#ffffff", stroke="#7e22ce", sw=1.0, pad=6)
    frags.append(d1)
    frags.append(text(735, 500, "Безпечна зупинка без пошкодження реляційного стану", size=10, bold=True, color=INK))

    # Зв'язки до бази даних
    frags.append(arrow(240, 300, 240, 330, color=INK, sw=1.5))
    frags.append(arrow(760, 300, 760, 330, color=INK, sw=1.5))

    render(os.path.join(IMG, 'mixed-fleet-protocol-compatibility.svg'), W, H, *frags,
           title="Сумісність протоколів та схема даних у змішаному парку")


if __name__ == '__main__':
    fig_canary_rollout_stages()
    fig_mixed_fleet_protocol_compatibility()
