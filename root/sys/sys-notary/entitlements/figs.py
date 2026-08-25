# -*- coding: utf-8 -*-
"""Фігури теми «Ентайтлменти». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"
AMBFILL = "#fef9e7"
AMBCOL  = "#d4ac0d"


# ── 1. Три брами контролю: Автентифікація, Авторизація, Ентайтлменти ───────────
def fig_authn_authz_entitlements():
    W, H = 1040, 380
    f = []

    # Відвідувач / запит
    b0, w0, h0 = textbox(80, 190, "HTTP-запит\nвід клієнта", size=13, fill=FILL, stroke=MUTED, pad=10)
    f.append(b0)

    # Брама 1: Автентифікація
    b1, w1, h1 = textbox(270, 190, "Брама 1\nАВТЕНТИФІКАЦІЯ\n«Хто звертається?»\n\nСуб'єкт: Користувач\n(JWT, сесія, API-ключ)",
                         size=12, fill=BLUFILL, stroke=NEG, sw=2, pad=12)
    f.append(b1)

    # Брама 2: Авторизація
    b2, w2, h2 = textbox(540, 190, "Брама 2\nАВТОРИЗАЦІЯ (RBAC)\n«Що йому дозволено?»\n\nСуб'єкт: Роль у команді\n(admin, editor, viewer)",
                         size=12, fill=GRNFILL, stroke=FIELD, sw=2, pad=12)
    f.append(b2)

    # Брама 3: Ентайтлменти
    b3, w3, h3 = textbox(820, 190, "Брама 3\nЕНТАЙТЛМЕНТИ\n«За що заплачено?»\n\nСуб'єкт: Організація / Тариф\n(функції, ліміти, квоти)",
                         size=12, fill=AMBFILL, stroke=AMBCOL, sw=2, pad=12)
    f.append(b3)

    # Стрілки між брамами
    f.append(arrow(80 + w0 / 2 + 4, 190, 270 - w1 / 2 - 6, 190))
    f.append(arrow(270 + w1 / 2 + 6, 190, 540 - w2 / 2 - 6, 190))
    f.append(arrow(540 + w2 / 2 + 6, 190, 820 - w3 / 2 - 6, 190))

    # Стрілка на вихід у бізнес-логіку
    f.append(arrow(820 + w3 / 2 + 6, 190, 1000, 190))
    f.append(text(980, 165, "Виконання", size=11, color=MUTED, anchor="middle"))

    # Позначки статусних відповідей на відмову під кожною брамою
    f.append(fitbox(200, 310, 140, 45, "Відмова: 401\nUnauthorized", size=11, fill=REDFILL, stroke=POS))
    f.append(line(270, 190 + h1 / 2, 270, 310, color=POS, sw=1.2, dash="3,3"))

    f.append(fitbox(470, 310, 140, 45, "Відмова: 403\nForbidden (RBAC)", size=11, fill=REDFILL, stroke=POS))
    f.append(line(540, 190 + h2 / 2, 540, 310, color=POS, sw=1.2, dash="3,3"))

    f.append(fitbox(750, 310, 140, 45, "Відмова: 402 / 403\nPayment Required", size=11, fill=REDFILL, stroke=POS))
    f.append(line(820, 190 + h3 / 2, 820, 310, color=POS, sw=1.2, dash="3,3"))

    render(out("authn-authz-entitlements.svg"), W, H, *f,
           title="Три незалежні брами контролю: особа, роль у команді та комерційний договір")


# ── 2. Конвеєр резолюції: від тарифу до зліпка ────────────────────────────────
def fig_entitlement_resolution_pipeline():
    W, H = 1040, 440
    f = []

    # 4 вхідні блоки зліва
    inputs = [
        (60, "Базовий тарифний план\n(Free, Starter, Pro, Enterprise)", FILL, LINE),
        (140, "Докуповані модулі (Add-ons)\n(+10 місць, пакет аудиту, виділений IP)", FILL, LINE),
        (220, "Індивідуальні винятки (Overrides)\n(Enterprise-контракт, спец-ліміт)", FILL, LINE),
        (300, "Стан оплати / Тріал\n(Active, Past-due, Trialing)", AMBFILL, AMBCOL),
    ]

    for y, label, fill, stroke in inputs:
        b, w, h = textbox(210, y, label, size=11, fill=fill, stroke=stroke, pad=8, min_w=340)
        f.append(b)
        f.append(arrow(210 + w / 2 + 4, y, 465, 180, color=LINE, sw=1.3))

    # Центральний блок — Компілятор / Рушій резолюції
    engine_box = fitbox(470, 90, 190, 180,
                        "РУШІЙ РЕЗОЛЮЦІЇ\n(Entitlement Engine)\n\n"
                        "1. Злиття шарів (merge)\n"
                        "2. Застосування винятків\n"
                        "3. Коригування за статусом\n"
                        "4. Розрахунок версії/хешу",
                        size=11, fill=BLUFILL, stroke=NEG, sw=2, pad=10)
    f.append(engine_box)

    # Вихідний блок — Ефективний незмінний зліпок
    snap_box = fitbox(730, 75, 270, 210,
                      "ЕФЕКТИВНИЙ ЗЛІПОК\n(Effective Entitlements Snapshot)\n\n"
                      "tenant_id: \"org_982\"\n"
                      "version: 14 (hash: 0xa4f1)\n"
                      "features: { sso: true, audit: true }\n"
                      "limits: { max_seats: 50 }\n"
                      "quotas: { api_calls: 500000/mo }\n"
                      "status: \"active\"",
                      size=11, fill=GRNFILL, stroke=FIELD, sw=2, pad=10)
    f.append(snap_box)

    f.append(arrow(660, 180, 725, 180, color=FIELD, sw=2))

    # Нижні сховища розподілу
    f.append(arrow(865, 285, 865, 345, color=LINE, sw=1.5))
    cache_box = fitbox(710, 350, 310, 65,
                       "Швидке поширення та кешування:\n"
                       "• L1: локальна пам'ять процесу (TTL 30с)\n"
                       "• L2: розподілений Redis-кеш (атомарна інвалідація)",
                       size=11, fill=FILL, stroke=MUTED, pad=8)
    f.append(cache_box)

    render(out("entitlement-resolution-pipeline.svg"), W, H, *f,
           title="Конвеєр резолюції: шари комерційного контракту компілюються в незмінний зліпок")


# ── 3. Перевірка на гарячому шляху: два канали перевірки ─────────────────────
def fig_hotpath_evaluation_flow():
    W, H = 1040, 400
    f = []

    # Запит
    b_req, w_req, h_req = textbox(75, 140, "API-запит\n(HTTP/gRPC)", size=12, fill=FILL, stroke=MUTED)
    f.append(b_req)
    f.append(arrow(75 + w_req / 2 + 4, 140, 185, 140, color=LINE, sw=1.5))

    # Middleware перевірки
    f.append(fitbox(190, 85, 160, 110, "ШЛЮЗ / MIDDLEWARE\n\nВитягує tenant_id\nіз токена/сесії;\nвизначає тип вимоги", size=10, fill=FILL, stroke=LINE, pad=8))

    # Розгалуження на два шляхи
    f.append(arrow(350, 115, 420, 70, color=NEG, sw=1.6))
    f.append(text(385, 85, "Булеве право", size=10, color=NEG, anchor="middle"))

    f.append(arrow(350, 165, 420, 195, color=FIELD, sw=1.6))
    f.append(text(385, 190, "Метрична квота", size=10, color=FIELD, anchor="middle"))

    # Канал 1: Булевий шлюз (Швидкий шлях)
    f.append(fitbox(425, 30, 270, 80,
                    "КАНАЛ 1: БУЛЕВИЙ ШЛЮЗ (SSO, Export)\n"
                    "Читання з L1 пам'яті / Redis:\n"
                    "features[sso] == true ?\n"
                    "Затримка: < 0.1 мс (in-memory)",
                    size=10, fill=BLUFILL, stroke=NEG, sw=1.5))

    # Канал 2: Метрична квота (Лічильник)
    f.append(fitbox(425, 160, 270, 80,
                    "КАНАЛ 2: МЕТРИЧНА КВОТА (API, трафік)\n"
                    "Атомарний Check-and-Reserve у Redis:\n"
                    "current_usage + requested <= limit ?\n"
                    "Затримка: 0.5–1.5 мс",
                    size=10, fill=GRNFILL, stroke=FIELD, sw=1.5))

    # Канал 1 -> Відмова (403)
    f.append(arrow(695, 50, 765, 50, color=POS, sw=1.4))
    f.append(fitbox(770, 30, 250, 42, "403 Forbidden\n{ error: \"feature_not_in_plan\" }", size=10, fill=REDFILL, stroke=POS))

    # Канал 2 -> Відмова (402) прямо під каналом 2
    f.append(arrow(560, 240, 560, 295, color=POS, sw=1.4))
    f.append(fitbox(425, 300, 270, 45, "402 Payment Required\n{ error: \"quota_exceeded\" }", size=10, fill=REDFILL, stroke=POS))

    # Канал 1 (так) & Канал 2 (так) -> Бізнес-логіка
    f.append(arrow(695, 85, 765, 120, color=FIELD, sw=1.6))
    f.append(arrow(695, 185, 765, 150, color=FIELD, sw=1.6))

    f.append(fitbox(770, 105, 250, 95,
                    "ВИКОНАННЯ ОБРОБНИКА\n(Business Logic)\n\n"
                    "Генерація відповіді;\n"
                    "Асинхронний еміт події\n"
                    "у чергу обліку (metering)",
                    size=10, fill=GRNFILL, stroke=FIELD, sw=2))

    # Фоновий агрегатор під бізнес-логікою
    f.append(line(895, 200, 895, 260, color=MUTED, sw=1.2, dash="3,3"))
    f.append(arrow(895, 260, 895, 275, color=MUTED, sw=1.2))
    f.append(fitbox(760, 280, 270, 48, "Фоновий білінг та агрегація метрик\n(асинхронне списання квот)", size=10, fill=FILL, stroke=MUTED))

    render(out("hotpath-evaluation-flow.svg"), W, H, *f,
           title="Обробка на гарячому шляху: розділення булевих шлюзів та обліку метричних квот")


# ── 4. Життєвий цикл підписки та пільгові періоди (Dunning) ───────────────────
def fig_grace_period_dunning_lifecycle():
    W, H = 1040, 390
    f = []

    states = [
        (130, 160, "ACTIVE\n(Нормальний стан)\n\nПовний доступ;\nусі функції відкриті", GRNFILL, FIELD, "Повна норма"),
        (390, 160, "PAST DUE\n(Пільговий період 7-14 днів)\n\nДоступ відкрито;\nбанери про помилку картки;\nспроби повторного списання", AMBFILL, AMBCOL, "Помилка оплати"),
        (660, 160, "RESTRICTED / SUSPENDED\n(Заблоковано запис)\n\nТільки читання (read-only);\nстворення заблоковано;\n402 Payment Required на запис", REDFILL, POS, "Пільгу вичерпано"),
        (920, 160, "CHURNED / ARCHIVED\n(Деактивовано)\n\nПовне блокування;\nзбереження даних за SLA;\nвидалення після терміну", FILL, MUTED, "Скасування / Churn"),
    ]

    for cx, cy, label, fill, stroke, note in states:
        b, w, h = textbox(cx, cy, label, size=11, fill=fill, stroke=stroke, sw=2, pad=10, min_w=195)
        f.append(b)

    # Стрілки переходів
    f.append(arrow(230, 160, 290, 160, color=AMBCOL, sw=1.8))
    f.append(text(260, 145, "Невдалий платіж", size=9, color=AMBCOL, anchor="middle"))

    f.append(arrow(490, 160, 560, 160, color=POS, sw=1.8))
    f.append(text(525, 145, "Сплив пільговий час", size=9, color=POS, anchor="middle"))

    f.append(arrow(760, 160, 820, 160, color=MUTED, sw=1.8))
    f.append(text(790, 145, "Не сплачено > 30д", size=9, color=MUTED, anchor="middle"))

    # Зворотні стрілки успішного відновлення оплати
    f.append(arrow(390, 240, 200, 240, color=FIELD, sw=1.5))
    f.append(text(295, 255, "Успішне списання (Self-heal)", size=10, color=FIELD, anchor="middle"))

    f.append(arrow(660, 290, 160, 290, color=FIELD, sw=1.5))
    f.append(text(410, 305, "Оновлення платіжних даних клієнтом", size=10, color=FIELD, anchor="middle"))

    # Пояснення внизу
    f.append(fitbox(150, 340, 740, 38,
                    "Принцип м'якого згасання: збій транзакції не має ламати роботу користувача миттєво",
                    size=11, bold=True, fill=FILL, stroke=MUTED, pad=6))

    render(out("grace-period-dunning-lifecycle.svg"), W, H, *f,
           title="Життєвий цикл стану підписки: плавний перехід між пільговим періодом та блокуванням")


if __name__ == "__main__":
    fig_authn_authz_entitlements()
    fig_entitlement_resolution_pipeline()
    fig_hotpath_evaluation_flow()
    fig_grace_period_dunning_lifecycle()
    print("All figures generated successfully.")
