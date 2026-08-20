# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектурні шляхи Fail-Open та Fail-Closed ───────────────────
def fig_fail_open_vs_closed():
    W, H = 1000, 560
    frags = []

    frags.append(text(500, 30, "Архітектурні шляхи обробки запитів: Fail-Open проти Fail-Closed", size=16, bold=True))

    # Клієнтський запит
    frags.append(rect(30, 240, 140, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(100, 268, "Клієнтський запит", size=12, bold=True, color=INK))
    frags.append(text(100, 290, "HTTP / gRPC", size=10, color=MUTED))

    # Шлюз перевірки (Checkpoint / Policy Enforcer)
    frags.append(rect(230, 210, 200, 130, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    frags.append(text(330, 236, "Шлюз перевірки", size=13, bold=True, color=INK))
    frags.append(text(330, 258, "(WAF / Auth / Billing)", size=11, color=MUTED))
    frags.append(rect(245, 275, 170, 50, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(330, 295, "Збій інспектора!", size=11, bold=True, color=POS))
    frags.append(text(330, 314, "Таймаут / 5xx / Падіння", size=10, color=POS))

    # Стрілка від клієнта до шлюзу
    frags.append(arrow(170, 275, 230, 275, color=LINE, sw=1.8))

    # ── Верхня гілка: Fail-Open ──
    frags.append(rect(490, 60, 480, 200, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(730, 88, "РЕЖИМ FAIL-OPEN (Відкриття на відмову)", size=13, bold=True, color=FIELD))
    frags.append(text(730, 108, "Пріоритет: ДОСТУПНІСТЬ (Availability > Security)", size=11, bold=True, color=FIELD))

    # Дії Fail-Open
    frags.append(rect(510, 125, 200, 115, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    frags.append(text(610, 148, "Пропуск запиту", size=11, bold=True, color=FIELD))
    frags.append(text(610, 170, "• X-Degraded: true", size=10, color=INK))
    frags.append(text(610, 190, "• Маршрут до бекенда", size=10, color=INK))
    frags.append(text(610, 212, "• Безперервний UX", size=10, color=MUTED))

    frags.append(rect(740, 125, 210, 115, fill="#ffffff", stroke="#d97706", sw=1, rx=5))
    frags.append(text(845, 148, "Тіньовий аудит (Shadow)", size=11, bold=True, color="#d97706"))
    frags.append(text(845, 170, "• Асинхронна черга DLQ", size=10, color=INK))
    frags.append(text(845, 190, "• Постфактум-аналіз", size=10, color=INK))
    frags.append(text(845, 212, "• Відкладена звірка", size=10, color=MUTED))

    # ── Нижня гілка: Fail-Closed ──
    frags.append(rect(490, 310, 480, 200, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(730, 338, "РЕЖИМ FAIL-CLOSED (Блокування на відмову)", size=13, bold=True, color=POS))
    frags.append(text(730, 358, "Пріоритет: ЦІЛІСНІСТЬ І БЕЗПЕКА (Integrity > Availability)", size=11, bold=True, color=POS))

    # Дії Fail-Closed
    frags.append(rect(510, 375, 200, 115, fill="#ffffff", stroke=POS, sw=1, rx=5))
    frags.append(text(610, 398, "Негайне відхилення", size=11, bold=True, color=POS))
    frags.append(text(610, 420, "• HTTP 403 / 503 / 422", size=10, color=INK))
    frags.append(text(610, 440, "• Захист інваріантів", size=10, color=INK))
    frags.append(text(610, 462, "• Нульовий ризик шахрайства", size=10, color=MUTED))

    frags.append(rect(740, 375, 210, 115, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    frags.append(text(845, 398, "Карантин та ізоляція", size=11, bold=True, color=INK))
    frags.append(text(845, 420, "• Запобігання витоку", size=10, color=INK))
    frags.append(text(845, 440, "• Блокування транзакції", size=10, color=INK))
    frags.append(text(845, 462, "• Оповіщення чергових", size=10, color=MUTED))

    # Зв'язуючі стрілки від шлюзу до гілок
    frags.append(arrow(430, 240, 490, 170, color=FIELD, sw=2))
    frags.append(text(445, 195, "Fail-Open", size=10, bold=True, color=FIELD))

    frags.append(arrow(430, 310, 490, 380, color=POS, sw=2))
    frags.append(text(445, 360, "Fail-Closed", size=10, bold=True, color=POS))

    return render(os.path.join(IMG, 'fail-open-vs-closed-architecture.svg'), W, H, *frags)


# ── Фігура 2: Матриця компромісів: Доступність проти Цілісності ───────────────
def fig_decision_matrix():
    W, H = 1000, 540
    frags = []

    frags.append(text(500, 28, "Матриця прийняття рішень: Вартість простою проти Ризику порушення цілісності", size=16, bold=True))

    # Осі координат
    ox, oy = 120, 460
    kw, kh = 820, 390

    # Фон квадрантів
    # Q1: Низька ціна простою, високий ризик (Top-Left) -> Суворий Fail-Closed
    frags.append(rect(ox, oy - kh, kw/2, kh/2, fill="#fef2f2", stroke="#fecaca", sw=1))
    # Q2: Висока ціна простою, високий ризик (Top-Right) -> Гібрид / Ескроу / Адаптивний
    frags.append(rect(ox + kw/2, oy - kh, kw/2, kh/2, fill="#fffbeb", stroke="#fde68a", sw=1))
    # Q3: Низька ціна простою, низький ризик (Bottom-Left) -> Спрощений Fail-Closed
    frags.append(rect(ox, oy - kh/2, kw/2, kh/2, fill="#f8fafc", stroke="#e2e8f0", sw=1))
    # Q4: Висока ціна простою, низький ризик (Bottom-Right) -> Чистий Fail-Open
    frags.append(rect(ox + kw/2, oy - kh/2, kw/2, kh/2, fill="#f0fdf4", stroke="#bbf7d0", sw=1))

    # Осі
    frags.append(arrow(ox, oy, ox + kw + 30, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy, ox, oy - kh - 30, color=LINE, sw=2))

    # Підписи осей
    frags.append(text(ox + kw - 30, oy + 32, "Вартість простою / Втрата доступності →", size=12, bold=True, color=INK, anchor="end"))
    frags.append(text(ox - 15, oy - kh - 15, "Ризик порушення безпеки та фінансових втрат →", size=12, bold=True, color=INK, anchor="start"))

    # Наповнення квадранта 1 (Top-Left: Суворий Fail-Closed)
    frags.append(text(ox + kw/4, oy - kh + 30, "СУВОРИЙ FAIL-CLOSED", size=13, bold=True, color=POS))
    frags.append(text(ox + kw/4, oy - kh + 52, "Повна зупинка при збої валідатора", size=10, color=MUTED))
    frags.append(rect(ox + 30, oy - kh + 70, 350, 95, fill="#ffffff", stroke=POS, sw=1, rx=5))
    frags.append(text(ox + 45, oy - kh + 92, "• Фінансові транзакції та кліринг (double-spend)", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh + 114, "• Криптографічні підписи та валідація mTLS", size=10, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh + 136, "• Регуляторний аудит-лог (не можна втратити)", size=10, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh + 154, "• Дозування в медичних та промислових АСУТП", size=10, color=POS, anchor="start"))

    # Наповнення квадранта 2 (Top-Right: Гібрид / Офлайн-ескроу)
    frags.append(text(ox + 3*kw/4, oy - kh + 30, "ГІБРИД / АДАПТИВНИЙ / ЕСКРОУ", size=13, bold=True, color="#d97706"))
    frags.append(text(ox + 3*kw/4, oy - kh + 52, "Fail-Open з обмеженням ризику (ліміти, скоринг)", size=10, color=MUTED))
    frags.append(rect(ox + kw/2 + 30, oy - kh + 70, 350, 95, fill="#ffffff", stroke="#d97706", sw=1, rx=5))
    frags.append(text(ox + kw/2 + 45, oy - kh + 92, "• Офлайн-авторизація дрібних оплат (транспорт, літаки)", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh + 114, "• WAF: пропуск перевірених сесій при перевантаженні", size=10, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh + 136, "• Токенізація з кешуванням відкликаних ключів", size=10, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh + 154, "• Білінговий овердрафт із кредитним лімітом", size=10, color="#d97706", anchor="start"))

    # Наповнення квадранта 3 (Bottom-Left: Спрощений Fail-Closed)
    frags.append(text(ox + kw/4, oy - kh/2 + 30, "СТАНДАРТНИЙ FAIL-CLOSED", size=13, bold=True, color=INK))
    frags.append(text(ox + kw/4, oy - kh/2 + 52, "Просте відхилення (не критично для виручки)", size=10, color=MUTED))
    frags.append(rect(ox + 30, oy - kh/2 + 70, 350, 95, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    frags.append(text(ox + 45, oy - kh/2 + 92, "• Адміністративні панелі та бек-офіс", size=10, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh/2 + 114, "• Нічні пакетні генератори звітів", size=10, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh/2 + 136, "• Допоміжні синхронізатори внутрішніх схем", size=10, color=INK, anchor="start"))
    frags.append(text(ox + 45, oy - kh/2 + 154, "• Деплой та конфігураційні пайплайни", size=10, color=MUTED, anchor="start"))

    # Наповнення квадранта 4 (Bottom-Right: Чистий Fail-Open)
    frags.append(text(ox + 3*kw/4, oy - kh/2 + 30, "ЧИСТИЙ FAIL-OPEN", size=13, bold=True, color=FIELD))
    frags.append(text(ox + 3*kw/4, oy - kh/2 + 52, "Максимальна доступність, фонове відновлення", size=10, color=MUTED))
    frags.append(rect(ox + kw/2 + 30, oy - kh/2 + 70, 350, 95, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    frags.append(text(ox + kw/2 + 45, oy - kh/2 + 92, "• Збір розподілених метрик і трейсів (OpenTelemetry)", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh/2 + 114, "• Рекомендаційні блоки та персоналізація", size=10, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh/2 + 136, "• Пошукові підказки (autocomplete)", size=10, color=INK, anchor="start"))
    frags.append(text(ox + kw/2 + 45, oy - kh/2 + 154, "• Кеш рекламних банерів та публічний контент", size=10, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'decision-matrix-tradeoff.svg'), W, H, *frags)


# ── Фігура 3: Адаптивний конвеєр деградації (Adaptive Fallback Pipeline) ─────
def fig_adaptive_fallback_pipeline():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 28, "Адаптивний конвеєр валідації та деградації (Resilient Policy Enforcement)", size=16, bold=True))

    # Крок 1: Вхідний запит
    frags.append(rect(30, 200, 130, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(95, 230, "Вхідний запит", size=12, bold=True, color=INK))
    frags.append(text(95, 252, "Контекст + Заголовки", size=10, color=MUTED))

    # Крок 2: Первинний валідатор з бюджетом часу
    frags.append(rect(200, 175, 170, 120, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(285, 200, "Первинний валідатор", size=12, bold=True, color=INK))
    frags.append(text(285, 222, "RPC / OPA / Auth", size=11, color=MUTED))
    frags.append(rect(215, 238, 140, 42, fill="#fffbeb", stroke="#d97706", sw=1, rx=4))
    frags.append(text(285, 256, "Бюджет часу: 15 ms", size=10, bold=True, color="#d97706"))
    frags.append(text(285, 272, "Запобіжник (Breaker)", size=9, color=MUTED))

    frags.append(arrow(160, 235, 200, 235, color=LINE, sw=1.8))

    # Гілка успіху первинного валідатора
    frags.append(arrow(285, 175, 285, 90, color=FIELD, sw=2))
    frags.append(rect(220, 60, 130, 30, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(285, 80, "Дозволено (200 OK)", size=11, bold=True, color=FIELD))

    # Крок 3: Селектор аварійної стратегії (Fallback Dispatcher)
    frags.append(rect(430, 175, 170, 120, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    frags.append(text(515, 202, "Диспетчер деградації", size=12, bold=True, color=POS))
    frags.append(text(515, 224, "(Fallback Dispatcher)", size=10, color=MUTED))
    frags.append(text(515, 250, "Таймаут / Помилка", size=10, bold=True, color=POS))
    frags.append(text(515, 272, "Аналіз класу політики", size=10, color=INK))

    frags.append(arrow(370, 235, 430, 235, color=POS, sw=2))
    frags.append(text(400, 222, "Збій", size=10, bold=True, color=POS))

    # Три виходи з Диспетчера:
    # 1. Застарілий кеш (Stale-while-error)
    frags.append(rect(670, 60, 300, 100, fill="#f0f9ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(820, 85, "1. Локальний кеш (Stale-if-error)", size=11, bold=True, color=NEG))
    frags.append(text(820, 108, "Читання локальної копії JWKS / ACL", size=10, color=INK))
    frags.append(text(820, 128, "Перевірка криптографії без мережі", size=10, color=MUTED))
    frags.append(text(820, 146, "Дозвіл за м'яким станом", size=10, color=NEG))

    frags.append(arrow(600, 200, 670, 110, color=NEG, sw=1.8))
    frags.append(text(620, 145, "Кеш є", size=9, bold=True, color=NEG))

    # 2. Fail-Open з тіньовим аудитом
    frags.append(rect(670, 190, 300, 110, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(820, 215, "2. Fail-Open + Shadow Audit", size=11, bold=True, color=FIELD))
    frags.append(text(820, 238, "Пропуск запиту до Upstream", size=10, color=INK))
    frags.append(text(820, 258, "Запис у фонову чергу DLQ для звірки", size=10, color=INK))
    frags.append(text(820, 280, "Додавання заголовка X-Fail-Open: 1", size=10, color=FIELD))

    frags.append(arrow(600, 235, 670, 235, color=FIELD, sw=1.8))
    frags.append(text(630, 222, "Non-critical", size=9, bold=True, color=FIELD))

    # 3. Fail-Closed з відхиленням
    frags.append(rect(670, 330, 300, 110, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(820, 355, "3. Fail-Closed + Відхилення", size=11, bold=True, color=POS))
    frags.append(text(820, 378, "Повернення HTTP 403 Forbidden / 503", size=10, color=INK))
    frags.append(text(820, 398, "Інкремент лічильника security_blocked", size=10, color=INK))
    frags.append(text(820, 420, "Гарантія збереження фінансових інваріантів", size=10, color=POS))

    frags.append(arrow(600, 270, 670, 370, color=POS, sw=1.8))
    frags.append(text(620, 335, "Critical/Auth", size=9, bold=True, color=POS))

    return render(os.path.join(IMG, 'adaptive-fallback-pipeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_fail_open_vs_closed()
    fig_decision_matrix()
    fig_adaptive_fallback_pipeline()
    print("All figures generated successfully.")
