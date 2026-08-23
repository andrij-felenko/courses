# -*- coding: utf-8 -*-
"""Фігури до теми «Вихід назовні як єдиний клас вузла»."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#dfe9fb"
GREEN_FILL = "#eafaf0"
GRAY_FILL = "#eceef1"
YELLOW_FILL = "#fff8e6"
RED_FILL = "#fdecea"


def fig_unified_class():
    """Три фасади виходу назовні (вебхуки, сповіщення, зовнішні API) та єдиний вузол."""
    W, H = 1280, 680
    frags = []
    frags.append(text(W / 2, 40, "Вихід назовні: три адресати — один архітектурний вузол",
                      size=18, bold=True, color=INK))

    # ── Ліворуч: три види вихідних вимог ──
    dests = [
        ("ВЕБХУК (машині)", "POST JSON · HMAC-підпис\nat-least-once · SLA мілісекунди", BLUE_FILL),
        ("СПОВІЩЕННЯ (людині)", "Push / SMS / Email · тихі години\nдайджести · пріоритет каналів", YELLOW_FILL),
        ("ЗОШНІШНЄ API (партнерові)", "REST / gRPC · OAuth / API-ключ\nтаймаути · ліміти викликів", GREEN_FILL),
    ]
    dy_starts = [120, 290, 460]
    for (title_str, desc_str, fill_c), y in zip(dests, dy_starts):
        box, bw, bh = textbox(190, y + 55, f"{title_str}\n{desc_str}",
                              size=12, bold=True, fill=fill_c, stroke=INK, min_w=280)
        frags.append(box)
        # стрілка від кожного до центру
        frags.append(arrow(190 + bw / 2 + 6, y + 55, 470, 345, color=INK, sw=1.8))

    # ── Центр: Єдиний Outbound Egress Node ──
    core_box, cw, ch = textbox(660, 345,
                               "ЄДИНИЙ ШАР ВИХОДУ (OUTBOUND EGRESS NODE)\n"
                               "1. Transactional Outbox (гарантія збереження наміру)\n"
                               "2. Egress Dispatcher & Dedup (генерування ключів)\n"
                               "3. Policy & Preferences Gate (підписки та тихі години)\n"
                               "4. Rate Limiter & Throttler (захист темпу й бюджету)\n"
                               "5. Transport & Circuit Breaker (ретраї з jitter + розмикач)\n"
                               "6. DLQ & Audit Log (мертва черга й трасування)",
                               size=12, bold=True, fill=GRAY_FILL, stroke=INK, sw=2, min_w=400)
    frags.append(core_box)

    # ── Праворуч: Зовнішній світ ──
    ext_box, ew, eh = textbox(1100, 345,
                              "ЗОШНІШНІ МЕРЕЖІ ТА ПАРТНЕРИ\n"
                              "Сервери партнерів (Webhooks)\n"
                              "Провайдери (APNs, FCM, Twilio)\n"
                              "Зовнішні платіжні / CRM API\n"
                              "― ― ― ― ― ― ― ― ― ― ― ―\n"
                              "Неконтрольовані лаг, падіння,\n"
                              "таймаути та дублікати",
                              size=12, bold=True, fill=RED_FILL, stroke=NEG, min_w=270)
    frags.append(arrow(660 + cw / 2 + 6, 345, 1100 - ew / 2 - 6, 345, color=INK, sw=2.2))
    frags.append(ext_box)

    frags.append(text(W / 2, 640,
                      "Адресат визначає формати й політики, але мережеві катастрофи та тактики стійкості ідентичні для всіх виходів.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "outbound-unified-class.svg"), W, H, *frags, title=None)


def fig_node_anatomy():
    """Шість шарів анатомії вихідного вузла."""
    W, H = 1320, 700
    frags = []
    frags.append(text(W / 2, 36, "Анатомія вихідного вузла: шість шарів захисту та стійкості",
                      size=18, bold=True, color=INK))

    layers = [
        ("1. Outbox БД", "Атомарний запис\nнаміру з подією", BLUE_FILL),
        ("2. Диспетчер", "Генерування id &\ndedup-ключів", YELLOW_FILL),
        ("3. Політики", "Преференси, підписка,\nтихі години", GREEN_FILL),
        ("4. Throttler", "Token bucket, темп\nта бюджети", YELLOW_FILL),
        ("5. Транспорт", "Circuit Breaker,\nretry з jitter", BLUE_FILL),
        ("6. DLQ & Лог", "Мертва черга,\nалерт і аудит", RED_FILL),
    ]

    xs = [120, 330, 540, 750, 960, 1170]
    y_center = 320
    bw, bh = 175, 110

    for i, ((title_s, desc_s, fill_c), x) in enumerate(zip(layers, xs)):
        box = fitbox(x - bw / 2, y_center - bh / 2, bw, bh,
                     f"{title_s}\n{desc_s}", size=12, bold=True, fill=fill_c, stroke=INK)
        frags.append(box)
        if i < len(xs) - 1:
            next_x = xs[i + 1]
            frags.append(arrow(x + bw / 2 + 4, y_center, next_x - bw / 2 - 4, y_center, color=INK, sw=2.0))

    # Додаткові пояснення під шарами
    explanations = [
        "Усуває dual-write\nпроблему",
        "Гарантує ідемпотентність\nотримувача",
        "Перевіряє право й\nбажання чути",
        "Захищає від шторму\nй перевитрат",
        "Ізолює падіння\nзовнішнього API",
        "Зберігає отруйні\nповідомлення",
    ]
    for x, exp in zip(xs, explanations):
        frags.append(text(x, y_center + bh / 2 + 35, exp, size=11, italic=True, color=MUTED))

    frags.append(text(W / 2, 650,
                      "Жодна вихідна доставка не торкається мережі напросту: потік іде крізь усі 6 шарів по черзі.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "outbound-node-anatomy.svg"), W, H, *frags, title=None)


def fig_dual_write_vs_outbox():
    """Пастка подвійного запису проти Transactional Outbox."""
    W, H = 1260, 680
    frags = []
    frags.append(text(W / 2, 38, "Пастка подвійного запису (Dual-Write) проти Transactional Outbox",
                      size=18, bold=True, color=INK))

    # ── Верхня частина: Пастка ──
    frags.append(text(150, 110, "НЕБЕЗПЕЧНО: Прямий виклик у транзакції (Dual-Write)",
                      size=14, bold=True, color=NEG))

    b1, _, _ = textbox(240, 190, "1. BEGIN SQL\nОновити стан у БД", size=12, bold=True, fill=BLUE_FILL, stroke=INK, min_w=200)
    b2, _, _ = textbox(570, 190, "2. HTTP POST назовні\n(вебхук / SMS / API)", size=12, bold=True, fill=RED_FILL, stroke=NEG, min_w=220)
    b3, _, _ = textbox(920, 190, "3. COMMIT SQL\nЗафіксувати транзакцію", size=12, bold=True, fill=GRAY_FILL, stroke=INK, min_w=200)

    frags.append(b1)
    frags.append(arrow(240 + 100 + 4, 190, 570 - 110 - 4, 190, color=INK, sw=1.8))
    frags.append(b2)
    frags.append(arrow(570 + 110 + 4, 190, 920 - 100 - 4, 190, color=INK, sw=1.8))
    frags.append(b3)

    frags.append(text(W / 2, 275,
                      "💥 Якщо крок 2 завис або впав — БД робить ROLLBACK, але HTTP POST ВЖЕ полетів! Дублювання грошей / SMS.\n"
                      "💥 Якщо крок 2 пройшов, а крок 3 впав — зовнішній світ отримав сповіщення про факт, якого немає в БД.",
                      size=12, bold=True, color=NEG))

    # Розділювач
    frags.append(line(80, 325, 1180, 325, color=MUTED, sw=1, dash="4,4"))

    # ── Нижня частина: Transactional Outbox ──
    frags.append(text(150, 360, "НАДІЙНО: Transactional Outbox + Асинхронний воркер",
                      size=14, bold=True, color=FIELD))

    ob1, _, _ = textbox(240, 460, "1. BEGIN SQL\nОновити стан БД +\nЗапис в outbox", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, min_w=200)
    ob2, _, _ = textbox(570, 460, "2. COMMIT SQL\nАтомарна фіксація\nподії та outbox", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, min_w=200)
    ob3, _, _ = textbox(920, 460, "3. Асинхронний воркер\nвичитує outbox та шле\nHTTP POST з retry", size=12, bold=True, fill=BLUE_FILL, stroke=INK, min_w=220)

    frags.append(ob1)
    frags.append(arrow(240 + 100 + 4, 460, 570 - 100 - 4, 460, color=INK, sw=1.8))
    frags.append(ob2)
    frags.append(arrow(570 + 100 + 4, 460, 920 - 110 - 4, 460, color=INK, sw=1.8))
    frags.append(ob3)

    frags.append(text(W / 2, 555,
                      "✓ Мережевий HTTP-виклик повністю винесено за межі SQL-транзакції.\n"
                      "✓ Намір відправки атомарний із бізнес-даними: або зберегли обоє, або жодного.",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "dual-write-vs-outbox.svg"), W, H, *frags, title=None)


def fig_push_pull_reconciliation():
    """Стратегія Push + Pull: ретраї проти періодичної звірки."""
    W, H = 1260, 650
    frags = []
    frags.append(text(W / 2, 40, "Стратегія Push + Pull: миттєвий пуш та фонова звірка",
                      size=18, bold=True, color=INK))

    # ── Шлях Push (активний) ──
    frags.append(text(120, 110, "1. Шлях PUSH (активний, швидкий, подійний)", size=14, bold=True, color=INK))
    p1, _, _ = textbox(250, 190, "Бізнес-подія\n(наприклад, замок відчинено)", size=12, bold=True, fill=BLUE_FILL, stroke=INK, min_w=220)
    p2, _, _ = textbox(630, 190, "Вихідний вузол (Egress)\nOutbox → Retry → HTTP POST", size=12, bold=True, fill=YELLOW_FILL, stroke=INK, min_w=240)
    p3, _, _ = textbox(1020, 190, "Приймач партнера\n(доставка за мілісекунди)", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, min_w=220)

    frags.append(p1)
    frags.append(arrow(250 + 110 + 4, 190, 630 - 120 - 4, 190, color=INK, sw=2.0))
    frags.append(p2)
    frags.append(arrow(630 + 120 + 4, 190, 1020 - 110 - 4, 190, color=INK, sw=2.0))
    frags.append(p3)

    # Зауваження щодо збою push
    frags.append(text(630, 260, "⚠️ При тривалому падінні мережі / сервісу push згасає (DLQ після max retries)",
                      size=12, italic=True, color=NEG))

    # Розділювач
    frags.append(line(80, 300, 1180, 300, color=MUTED, sw=1, dash="4,4"))

    # ── Шлях Pull (фонова звірка) ──
    frags.append(text(120, 340, "2. Шлях PULL (периодична фонова звірка / Reconciliation)", size=14, bold=True, color=INK))
    r1, _, _ = textbox(250, 430, "Cron-сканер звірки\n(раз на годину / добу)", size=12, bold=True, fill=GRAY_FILL, stroke=INK, min_w=220)
    r2, _, _ = textbox(630, 430, "Запит стану API партнера\nGET /v1/events / GET /status", size=12, bold=True, fill=BLUE_FILL, stroke=INK, min_w=240)
    r3, _, _ = textbox(1020, 430, "Порівняння станів\nВідновлення узгодженості", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, min_w=220)

    frags.append(r1)
    frags.append(arrow(250 + 110 + 4, 430, 630 - 120 - 4, 430, color=INK, sw=2.0))
    frags.append(r2)
    frags.append(arrow(630 + 120 + 4, 430, 1020 - 110 - 4, 430, color=INK, sw=2.0))
    frags.append(r3)

    frags.append(text(W / 2, 610,
                      "Push гарантує низьку латентність у 99.9% випадків. Pull гарантує остаточну узгодженість при 0.1% катастроф.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "push-pull-reconciliation.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_unified_class()
    fig_node_anatomy()
    fig_dual_write_vs_outbox()
    fig_push_pull_reconciliation()
    print("Figures generated successfully.")
