# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Шторм повторів проти експоненційного відступу з джитером ───────
def fig_retry_storm_avalanche():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Динаміка навантаження під час 500-мс збою: наївні повтори проти джитера", size=16, bold=True))

    # Ліва панель: Наївні повтори (Шторм повторів)
    frags.append(rect(40, 60, 440, 430, fill="#fdfbfb", stroke=POS, sw=1.5, rx=8))
    frags.append(text(260, 90, "Наївні негайні повтори (Retry Storm)", size=14, bold=True, color=POS))

    # Графік навантаження зліва
    frags.append(line(80, 420, 440, 420, color=LINE, sw=1.5))  # вісь X (час)
    frags.append(line(80, 420, 80, 130, color=LINE, sw=1.5))   # вісь Y (RPS)
    frags.append(text(430, 440, "Час (с)", size=11, color=MUTED, anchor="end"))
    frags.append(text(75, 125, "Запитів/с", size=11, color=MUTED, anchor="end"))

    # Лінія граничної ємності
    frags.append(line(80, 260, 440, 260, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(435, 252, "Ємність бекенда (10k)", size=10, color=MUTED, anchor="end"))

    # Збійний інтервал (сіра смуга)
    frags.append(rect(140, 130, 60, 290, fill="#fee2e2", stroke="none"))
    frags.append(text(170, 150, "Збій 500мс", size=10, bold=True, color=POS))

    # Траєкторія навантаження зліва (лавиноподібний пік)
    storm_path = "M 80 260 L 140 260 L 170 360 L 200 140 L 230 135 L 280 130 L 440 130"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (storm_path, POS))

    frags.append(box(290, 320, "Лавина повторів:\n10k -> 25k -> 35k RPS\nПереповнення черг сокетів\nКаскадний колапс системи", size=11, bold=True, fill="#fff5f5", stroke=POS, min_w=180))


    # Права панель: Експоненційний відступ з джитером
    frags.append(rect(520, 60, 440, 430, fill="#fbfdfb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(740, 90, "Експоненційний відступ + Full Jitter", size=14, bold=True, color=FIELD))

    # Графік навантаження справа
    frags.append(line(560, 420, 920, 420, color=LINE, sw=1.5))
    frags.append(line(560, 420, 560, 130, color=LINE, sw=1.5))
    frags.append(text(910, 440, "Час (с)", size=11, color=MUTED, anchor="end"))
    frags.append(text(555, 125, "Запитів/с", size=11, color=MUTED, anchor="end"))

    # Лінія граничної ємності
    frags.append(line(560, 260, 920, 260, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(915, 252, "Ємність бекенда (10k)", size=10, color=MUTED, anchor="end"))

    # Збійний інтервал
    frags.append(rect(620, 130, 60, 290, fill="#fef3c7", stroke="none"))
    frags.append(text(650, 150, "Збій 500мс", size=10, bold=True, color="#d97706"))

    # Траєкторія навантаження справа (плавне розсіювання)
    smooth_path = "M 560 260 L 620 260 L 650 360 L 680 280 L 740 250 L 800 258 L 920 260"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (smooth_path, FIELD))

    frags.append(box(770, 320, "Рівномірне розсіювання:\nВідкладені спроби з шумом\nНавантаження не перевищує ємність\nШвидке відновлення бекенда", size=11, bold=True, fill="#f0fdf4", stroke=FIELD, min_w=200))

    return render(os.path.join(IMG, 'retry-storm-avalanche.svg'), W, H, *frags)


# ── Фігура 2: Порівняння стратегій відступу (Без джитера, Full Jitter, Equal Jitter) ──
def fig_backoff_jitter_strategies():
    W, H = 1000, 540
    frags = []

    frags.append(text(500, 30, "Часовий розподіл повторних спроб: подолання синхронізації клієнтів", size=16, bold=True))

    # Стратегія 1: Без джитера (Синхронні імпульси)
    frags.append(rect(40, 60, 920, 135, fill="#fdf8f8", stroke=POS, sw=1.2, rx=6))
    frags.append(text(60, 85, "1. Експоненційний відступ без джитера: t = min(t_max, t_0 · 2^i)", size=12, bold=True, color=POS, anchor="start"))
    frags.append(line(80, 145, 900, 145, color=LINE, sw=1.5))
    frags.append(text(80, 170, "t = 0 (Збій)", size=10, color=MUTED))
    frags.append(text(240, 170, "+1.0 с (Спроба 1)", size=10, color=POS))
    frags.append(text(460, 170, "+2.0 с (Спроба 2)", size=10, color=POS))
    frags.append(text(780, 170, "+4.0 с (Спроба 3)", size=10, color=POS))

    # Сплески навантаження
    for x in (240, 460, 780):
        frags.append(line(x, 145, x, 105, color=POS, sw=3))
        frags.append(circle(x, 105, 4, fill=POS, stroke=POS))
    frags.append(text(510, 115, "Синхронізовані імпульси: 100% клієнтів б'ють одночасно", size=10, color=POS, bold=True))

    # Стратегія 2: Full Jitter
    frags.append(rect(40, 210, 920, 145, fill="#f8fdf9", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(60, 235, "2. Full Jitter: t = random(0, min(t_max, t_0 · 2^i))", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(line(80, 305, 900, 305, color=LINE, sw=1.5))
    frags.append(text(80, 330, "t = 0", size=10, color=MUTED))

    # Розсіяні точки Full Jitter
    fj_points_1 = [100, 130, 160, 190, 220, 240]
    fj_points_2 = [260, 310, 350, 390, 430, 470]
    fj_points_3 = [500, 560, 620, 680, 740, 800, 860]
    for x in fj_points_1 + fj_points_2 + fj_points_3:
        frags.append(line(x, 305, x, 280, color=FIELD, sw=1.5))
        frags.append(circle(x, 280, 3, fill=FIELD, stroke=FIELD))
    frags.append(text(510, 260, "Повне розсіювання: рівномірний потік без піків навантаження", size=10, color=FIELD, bold=True))

    # Стратегія 3: Equal Jitter
    frags.append(rect(40, 370, 920, 145, fill="#f8fafc", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(60, 395, "3. Equal Jitter: t = (v / 2) + random(0, v / 2), де v = min(t_max, t_0 · 2^i)", size=12, bold=True, color=NEG, anchor="start"))
    frags.append(line(80, 465, 900, 465, color=LINE, sw=1.5))
    frags.append(text(80, 490, "t = 0", size=10, color=MUTED))

    # Точки Equal Jitter (гарантований відступ + шум)
    ej_points_1 = [160, 180, 200, 220, 240]
    ej_points_2 = [360, 390, 410, 440, 470]
    ej_points_3 = [640, 680, 720, 760, 800]
    for x in ej_points_1 + ej_points_2 + ej_points_3:
        frags.append(line(x, 465, x, 440, color=NEG, sw=1.5))
        frags.append(circle(x, 440, 3, fill=NEG, stroke=NEG))
    frags.append(text(510, 420, "Гарантована базова затримка + розсіювання другої половини інтервалу", size=10, color=NEG, bold=True))

    return render(os.path.join(IMG, 'backoff-jitter-strategies.svg'), W, H, *frags)


# ── Фігура 3: Каскадне множення повторів (Retry Amplification) ────────────────
def fig_retry_amplification_tree():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Каскадне множення запитів у ланцюжку сервісів (Retry Amplification)", size=16, bold=True))

    # Сервіс А (Клієнт / Шлюз)
    frags.append(box(120, 260, "API Gateway / Сервіс A\n(max_retries = 3)", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=150))
    frags.append(text(120, 190, "1 вхідний запит", size=11, bold=True, color=FIELD))

    # Сервіс B
    frags.append(box(380, 140, "Сервіс B1\n(max_retries = 3)", size=10, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=130))
    frags.append(box(380, 260, "Сервіс B2\n(max_retries = 3)", size=10, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=130))
    frags.append(box(380, 380, "Сервіс B3\n(max_retries = 3)", size=10, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=130))

    # Стрілки A -> B
    frags.append(arrow(200, 250, 310, 150, color=LINE, sw=1.5))
    frags.append(arrow(200, 260, 310, 260, color=LINE, sw=1.5))
    frags.append(arrow(200, 270, 310, 370, color=LINE, sw=1.5))
    frags.append(text(250, 210, "3 спроби", size=10, color=MUTED))

    # Сервіс C
    frags.append(box(640, 260, "Шар сервісу C\n(Кожен екземпляр робить 3 повтори)\nРазом: 3 · 3 = 9 запитів", size=11, bold=True, fill="#fee2e2", stroke=POS, min_w=190))

    # Стрілки B -> C
    frags.append(arrow(450, 145, 540, 240, color=POS, sw=1.2))
    frags.append(arrow(450, 260, 540, 260, color=POS, sw=1.2))
    frags.append(arrow(450, 375, 540, 280, color=POS, sw=1.2))

    # Сервіс D (Бекенд / База даних)
    frags.append(box(880, 260, "Сервіс D (БД / Платежі)\nЗбійний вузол\nОтримує: 3^3 = 27 запитів!", size=11, bold=True, fill="#fef2f2", stroke=POS, min_w=180))

    frags.append(arrow(740, 260, 785, 260, color=POS, sw=2.5))
    frags.append(text(760, 240, "27 запитів", size=11, bold=True, color=POS))

    # Пояснення захисту знизу
    frags.append(rect(80, 440, 840, 60, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(500, 465, "Захист Retry Budget: дозволяти повтори лише на межі системи або обмежувати 10% бюджету.", size=11, bold=True, color=FIELD))
    frags.append(text(500, 485, "Глибинні шари повертають помилку негайно, уникаючи експоненційного множення R^N.", size=10, color=MUTED))

    return render(os.path.join(IMG, 'retry-amplification-tree.svg'), W, H, *frags)


# ── Фігура 4: Механізм токенного кошика для бюджету повторів ──────────────────
def fig_retry_budget_token_bucket():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 30, "Бюджет повторів: регулювання лавини через токенний кошик (Token Bucket)", size=16, bold=True))

    # Потік успішних запитів (Поповнення)
    frags.append(box(160, 120, "Успішна відповідь (200 OK)\nНадходить від бекенда", size=11, bold=True, fill="#f0fdf4", stroke=FIELD, min_w=180))
    frags.append(arrow(160, 160, 160, 220, color=FIELD, sw=2))
    frags.append(text(250, 190, "+0.1 токена (10% бюджет)", size=10, bold=True, color=FIELD))

    # Токенний кошик у центрі
    frags.append(rect(80, 230, 380, 190, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(270, 260, "Токенний кошик клієнта (Retry Budget)", size=13, bold=True, color=NEG))
    frags.append(text(270, 290, "Поточний баланс: 15.4 / 100.0 токенів", size=11, color=INK))
    frags.append(text(270, 320, "Максимальна місткість (Cap): 100", size=10, color=MUTED))
    frags.append(text(270, 350, "Ковзне вікно (наприклад, останні 10 с)", size=10, color=MUTED))
    frags.append(text(270, 385, "Гарантія: повтори ≤ 10% від загального трафіку", size=10, bold=True, color=FIELD))

    # Подія збою (Спроба списання)
    frags.append(box(680, 120, "Тимчасовий збій (503 / Timeout)\nКлієнт хоче повторити запит", size=11, bold=True, fill="#fff5f5", stroke=POS, min_w=200))
    frags.append(arrow(680, 160, 680, 220, color=POS, sw=2))

    # Блок перевірки умови
    frags.append(box(680, 260, "Перевірка балансу:\nТокенів >= 1.0 ?", size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=160))

    # Гілка ТАК (Дозвіл)
    frags.append(arrow(770, 260, 860, 260, color=FIELD, sw=2))
    frags.append(text(810, 250, "ТАК", size=10, bold=True, color=FIELD))
    frags.append(box(920, 260, "Виконати повтор\n(-1.0 токен)", size=10, bold=True, fill="#f0fdf4", stroke=FIELD, min_w=100))

    # Гілка НІ (Бюджет вичерпано)
    frags.append(arrow(680, 305, 680, 380, color=POS, sw=2))
    frags.append(text(710, 345, "НІ (0 токенів)", size=10, bold=True, color=POS))
    frags.append(box(680, 420, "Fast-Fail: Негайне повернення помилки\nЗахист бекенда від лавинного колапсу", size=11, bold=True, fill="#fee2e2", stroke=POS, min_w=230))

    # Зв'язок кошика з перевіркою
    frags.append(line(460, 260, 590, 260, color=NEG, sw=1.5, dash="4 4"))
    frags.append(text(525, 245, "Запит токена", size=10, color=NEG))

    return render(os.path.join(IMG, 'retry-budget-token-bucket.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_retry_storm_avalanche()
    fig_backoff_jitter_strategies()
    fig_retry_amplification_tree()
    fig_retry_budget_token_bucket()
    print("All figures generated successfully.")
