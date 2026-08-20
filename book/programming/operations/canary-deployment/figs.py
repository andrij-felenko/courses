# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектура канаркового розгортання та кільце ACA ──────────────
def fig_canary_architecture():
    W, H = 960, 500
    frags = []

    # Клієнтський трафік
    client_box, cw, ch = textbox(110, 190, "Клієнтський потік\n(HTTP / gRPC запити)", size=12, bold=True,
                                 fill="#f3f4f6", stroke=INK, sw=1.6, pad=10)
    frags.append(client_box)

    # Ingress / Service Mesh шлюз
    gw_box, gw_w, gw_h = textbox(300, 190, "L7 Проксі / Шлюз\n(Envoy / Ingress Router)\nЗважене розщеплення", size=12, bold=True,
                                 fill="#eef4ff", stroke=NEG, sw=2, pad=12)
    frags.append(gw_box)

    # Стрілка Клієнт -> Шлюз
    frags.append(arrow(185, 190, 220, 190, color=INK, sw=1.8))
    frags.append(text(202, 178, "100%", size=11, color=MUTED, bold=True))

    # Стабільний пул (v1)
    prod_box, pw, ph = textbox(560, 110, "Стабільний пул (v1 Baseline)\n98% живого навантаження\nПеревірена версія", size=12, bold=True,
                               fill="#f6faf7", stroke=FIELD, sw=2, pad=12)
    frags.append(prod_box)

    # Канарковий пул (v2)
    canary_box, can_w, can_h = textbox(560, 270, "Канарковий пул (v2 Candidate)\n2% тестового навантаження\nНова версія під наглядом", size=12, bold=True,
                                       fill="#fff9e6", stroke="#d97706", sw=2, pad=12)
    frags.append(canary_box)

    # Маршрутизація від шлюзу до v1 та v2
    frags.append(arrow(380, 170, 440, 125, color=FIELD, sw=2))
    frags.append(text(400, 138, "98% трафіку", size=11, color=FIELD, bold=True))

    frags.append(arrow(380, 210, 440, 255, color="#d97706", sw=2))
    frags.append(text(400, 248, "2% трафіку", size=11, color="#d97706", bold=True))

    # Сховище телеметрії (Prometheus / TSDB)
    metrics_box, mw, mh = textbox(810, 190, "Сервер телеметрії\n(Prometheus / OpenTelemetry)\nЗбір RED-метрик і затримок", size=12, bold=True,
                                  fill="#f9fafb", stroke=INK, sw=1.6, pad=10)
    frags.append(metrics_box)

    # Потоки телеметрії від v1 та v2 до сховища
    frags.append(arrow(680, 110, 730, 170, color=FIELD, sw=1.6))
    frags.append(arrow(680, 270, 730, 210, color="#d97706", sw=1.6))
    frags.append(text(715, 135, "Метрики v1", size=10, color=FIELD))
    frags.append(text(715, 255, "Метрики v2", size=10, color="#d97706"))

    # Контролер автоматизованого аналізу (ACA Engine)
    aca_box, acaw, acah = textbox(560, 420, "Контролер ACA (Automated Canary Analysis)\nСтатистичне порівняння (Mann-Whitney U, Z-тест)\nОцінка індикаторів SLI / SLO", size=12, bold=True,
                                  fill="#fdf2f8", stroke="#be185d", sw=2, pad=12)
    frags.append(aca_box)

    # Зв'язок Сховище телеметрії -> ACA
    frags.append(line(810, 245, 810, 420, color="#be185d", sw=1.8, dash="4,3"))
    frags.append(arrow(810, 420, 725, 420, color="#be185d", sw=1.8))
    frags.append(text(795, 340, "Запит метрик (PromQL)", size=10, color="#be185d", bold=True))

    # Зворотний зв'язок: Промоція або Відкіт
    frags.append(line(395, 420, 300, 420, color="#b91c1c", sw=2))
    frags.append(arrow(300, 420, 300, 255, color="#b91c1c", sw=2))
    frags.append(text(340, 405, "Рішення: Збільшити вагу або Аварійний відкіт до 0%", size=10, color="#b91c1c", bold=True))

    render(os.path.join(IMG, 'canary-architecture.svg'), W, H, *frags,
           title="Архітектура канаркового розгортання та контур автоматизованого аналізу")


# ── Фігура 2: Трикогортне порівняння (Baseline vs Canary vs Legacy) ──────────
def fig_three_cohort_baseline():
    W, H = 960, 460
    frags = []

    # 1. Застарілий продакшен
    legacy_box, lw, lh = textbox(170, 140, "Старий продакшен (v1)\nЧас роботи: 45 днів\nПрогрітий JIT, гарячий кеш,\nнакопичена фрагментація", size=11, bold=True,
                                 fill="#f3f4f6", stroke="#9ca3af", sw=1.5, pad=10)
    frags.append(legacy_box)

    # 2. Контрольний бейзлайн (Baseline v1)
    base_box, bw, bh = textbox(480, 140, "Контрольний бейзлайн (v1)\nЧас роботи: 5 хвилин\nСвіжий процес старої версії,\nхолодний кеш і однаковий старт", size=11, bold=True,
                               fill="#eef4ff", stroke=NEG, sw=2, pad=10)
    frags.append(base_box)

    # 3. Канарка (Canary v2)
    can_box, cw2, ch2 = textbox(790, 140, "Канарковий кандидат (v2)\nЧас роботи: 5 хвилин\nСвіжий процес нової версії,\nхолодний кеш і однаковий старт", size=11, bold=True,
                                fill="#fff9e6", stroke="#d97706", sw=2, pad=10)
    frags.append(can_box)

    # Помилкове порівняння
    frags.append(line(280, 90, 680, 90, color="#b91c1c", sw=1.6, dash="3,3"))
    frags.append(text(480, 75, "ПОМИЛКОВЕ ПОРІВНЯННЯ: хибні тривоги через прогрів і вік подів", size=10, color="#b91c1c", bold=True))

    # Коректне трикогортне порівняння
    frags.append(arrow(480, 210, 480, 270, color=NEG, sw=2))
    frags.append(arrow(790, 210, 790, 270, color="#d97706", sw=2))
    frags.append(arrow(480, 270, 635, 330, color=NEG, sw=2))
    frags.append(arrow(790, 270, 635, 330, color="#d97706", sw=2))

    # Блок порівняння
    comp_box, comp_w, comp_h = textbox(635, 370, "Коректний арбітраж: Baseline (v1) проти Canary (v2)\n• Однакове апаратне забезпечення та час життя інстансів\n• Однаковий стан локальних кешів та JIT-компіляції\n• Різниця в метриках зумовлена виключно змінами в коді", size=11, bold=True,
                                       fill="#f6faf7", stroke=FIELD, sw=2, pad=12)
    frags.append(comp_box)

    render(os.path.join(IMG, 'three-cohort-baseline.svg'), W, H, *frags,
           title="Трикогортне порівняння: усунення хибних тривог через ізольований бейзлайн")


# ── Фігура 3: Багатоступеневий графік прогресивної доставки ───────────────────
def fig_progressive_rollout_stages():
    W, H = 960, 440
    frags = []

    steps = [
        ("Етап 0", "Внутрішній тест", "0% для людей\nМаршрутизація\nза заголовком", "#6b7280", 90),
        ("Етап 1", "Канарка 1%", "1% трафіку\nВитримка: 10 хв\nЗахист ядра", "#d97706", 260),
        ("Етап 2", "Канарка 5%", "5% трафіку\nВитримка: 15 хв\nЗбір p99 затримок", "#2563eb", 430),
        ("Етап 3", "Канарка 25%", "25% трафіку\nВитримка: 30 хв\nТест БД", "#7c3aed", 600),
        ("Етап 4", "Канарка 50%", "50% трафіку\nВитримка: 30 хв\nБізнес-метрики", "#059669", 770),
        ("Етап 5", "Промоція 100%", "100% трафіку\nЗгортання v1\nРеліз успішний", FIELD, 900)
    ]

    for i in range(len(steps) - 1):
        x1 = steps[i][4]
        x2 = steps[i+1][4]
        frags.append(arrow(x1 + 45, 140, x2 - 45, 140, color=INK, sw=1.8))

    for tag, name, desc, color, x in steps:
        box, bw, bh = textbox(x, 140, f"{tag}: {name}\n{desc}", size=10, bold=True,
                              fill="#ffffff", stroke=color, sw=1.8, pad=8)
        frags.append(box)

    # Лінія аварійного відкочування
    frags.append(line(130, 240, 860, 240, color="#b91c1c", sw=2, dash="4,4"))
    for _, _, _, _, x in steps[1:5]:
        frags.append(arrow(x, 200, x, 240, color="#b91c1c", sw=1.6))

    abort_box, abw, abh = textbox(480, 340, "Аварійне скасування релізу (Fast Rollback на будь-якому кроці)\nПри перевищенні порогу помилок або затримок:\n1. Вага канарки миттєво падає до 0%\n2. 100% трафіку повертається на стабільний v1\n3. Канаркові поди ізолюються для аналізу пам'яті та логів", size=11, bold=True,
                                  fill="#fee2e2", stroke="#b91c1c", sw=2, pad=12)
    frags.append(abort_box)
    frags.append(arrow(480, 240, 480, 285, color="#b91c1c", sw=2))

    render(os.path.join(IMG, 'progressive-rollout-stages.svg'), W, H, *frags,
           title="Багатоступеневий графік прогресивної доставки та шлюзи відкочування")


# ── Фігура 4: Статистичний арбітраж та матриця прийняття рішень ───────────────
def fig_statistical_decision_matrix():
    W, H = 960, 480
    frags = []

    # Вхідні метрики
    m1_box, m1w, m1h = textbox(130, 90, "RED-метрики сервісу\nЧастота помилок 5xx\nЗатримки p50, p95, p99", size=10, bold=True,
                               fill="#f3f4f6", stroke=INK, sw=1.5, pad=8)
    frags.append(m1_box)

    m2_box, m2w, m2h = textbox(130, 200, "Системні ресурси\nCPU, пам'ять (витоки)\nПаузи збирача сміття GC", size=10, bold=True,
                               fill="#f3f4f6", stroke=INK, sw=1.5, pad=8)
    frags.append(m2_box)

    m3_box, m3w, m3h = textbox(130, 310, "Бізнес-показники\nУспішні транзакції\nКількість замовлень / кошиків", size=10, bold=True,
                               fill="#f3f4f6", stroke=INK, sw=1.5, pad=8)
    frags.append(m3_box)

    # Статистичні методи
    stat_box, stw, sth = textbox(410, 200, "Статистичний процесор\n• Mann-Whitney U test (затримки)\n• Z-test двох пропорцій (помилки)\n• Довірчі інтервали та ваги", size=11, bold=True,
                                 fill="#eef4ff", stroke=NEG, sw=2, pad=12)
    frags.append(stat_box)

    frags.append(arrow(215, 90, 310, 170, color=INK, sw=1.6))
    frags.append(arrow(215, 200, 310, 200, color=INK, sw=1.6))
    frags.append(arrow(215, 310, 310, 230, color=INK, sw=1.6))

    # Обчислення зведеного балу (Score)
    score_box, scw, sch = textbox(650, 200, "Зведений бал (Score 0–100)\nЗважена сума успішних тестів\nКритичні метрики мають вагу 100", size=11, bold=True,
                                  fill="#fdf2f8", stroke="#be185d", sw=2, pad=10)
    frags.append(score_box)
    frags.append(arrow(510, 200, 565, 200, color=NEG, sw=2))

    # 3 гілки результату
    frags.append(arrow(735, 175, 790, 100, color=FIELD, sw=2))
    frags.append(text(760, 125, "Бал ≥ 80", size=10, color=FIELD, bold=True))

    frags.append(arrow(735, 200, 790, 200, color="#d97706", sw=2))
    frags.append(text(760, 188, "60 ≤ Бал < 80", size=10, color="#d97706", bold=True))

    frags.append(arrow(735, 225, 790, 300, color="#b91c1c", sw=2))
    frags.append(text(760, 275, "Бал < 60", size=10, color="#b91c1c", bold=True))

    # Результати
    pass_box, psw, psh = textbox(875, 100, "ПРОМОЦІЯ (Pass)\nПерехід на наступний\nвідсоток трафіку", size=10, bold=True,
                                 fill="#f6faf7", stroke=FIELD, sw=1.8, pad=8)
    frags.append(pass_box)

    wait_box, wtw, wth = textbox(875, 200, "ПАУЗА (Marginal)\nПовторне спостереження\nбез зміни ваги", size=10, bold=True,
                                 fill="#fff9e6", stroke="#d97706", sw=1.8, pad=8)
    frags.append(wait_box)

    fail_box, flw, flh = textbox(875, 300, "ВІДКІТ (Rollback)\nМиттєве зняття ваги\nта запуск алерту", size=10, bold=True,
                                 fill="#fee2e2", stroke="#b91c1c", sw=1.8, pad=8)
    frags.append(fail_box)

    render(os.path.join(IMG, 'statistical-decision-matrix.svg'), W, H, *frags,
           title="Матриця прийняття рішень автоматизованого статистичного аналізу")


if __name__ == '__main__':
    fig_canary_architecture()
    fig_three_cohort_baseline()
    fig_progressive_rollout_stages()
    fig_statistical_decision_matrix()
    print("Всі фігури згенеровано успішно.")
