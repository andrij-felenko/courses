# -*- coding: utf-8 -*-
"""Фігури до теми «Реплікаційний лаг і сесійні гарантії»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # аномалія / застарілий стан / помилка
COOL = "#eaf0fd"   # нейтральне пояснення / заголовки
GOOD = "#e8f6ee"   # актуальний стан / правильна поведінка
WARN_BG = "#fff9db" # очікування / перевірка


# ── 1. Часова шкала реплікаційного лагу та виникнення аномалій ───────────────
def replication_lag_timeline():
    W, H = 1160, 640
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 34, "Фізична природа реплікаційного лагу та виникнення аномалій читання",
                  size=16, bold=True))

    x0, x1 = 260.0, 1100.0
    span = x1 - x0

    # ── Доріжка 1: Primary (Лідер)
    yP = 100.0
    f.append(fitbox(30, yP - 28, 200, 56, "PRIMARY (ЛІДЕР)\nприймає всі записи", size=12, bold=True, fill=COOL))
    f.append(line(x0, yP, x1, yP, color=LINE, sw=2.0))
    f.append(arrow(x1 - 10, yP, x1 + 15, yP, color=LINE, sw=2.0))
    f.append(text(x1 + 30, yP + 4, "t", size=13, italic=True))

    # Подія запису на Primary
    t_w = x0 + span * 0.12
    f.append(circle(t_w, yP, 7, fill=POS, stroke=POS, sw=2))
    f.append(arrow(t_w, yP - 40, t_w, yP - 10, color=POS, sw=2.0))
    f.append(text(t_w, yP - 48, "Запис W1 (LSN 4120)", size=12, color=POS, bold=True))
    f.append(text(t_w, yP + 22, "t = 100 мс", size=11, color=MUTED))

    # ── Доріжка 2: Replica 1 (Швидка репліка)
    yR1 = 270.0
    f.append(fitbox(30, yR1 - 28, 200, 56, "REPLICA 1\nлаг Δt = 300 мс", size=12, bold=True, fill=COOL))
    f.append(line(x0, yR1, x1, yR1, color=LINE, sw=2.0))
    f.append(arrow(x1 - 10, yR1, x1 + 15, yR1, color=LINE, sw=2.0))
    f.append(text(x1 + 30, yR1 + 4, "t", size=13, italic=True))

    # Передача WAL до Replica 1
    t_r1_apply = t_w + span * 0.32
    f.append(line(t_w + 10, yP + 12, t_r1_apply - 10, yR1 - 14, color=FIELD, sw=2.0, dash="5,4"))
    f.append(arrow(t_r1_apply - 20, yR1 - 24, t_r1_apply, yR1 - 12, color=FIELD, sw=2.0))

    # Стан Replica 1 до і після apply
    f.append(rect(x0, yR1 - 12, t_r1_apply - x0, 24, fill=WARM, stroke=POS, sw=1.2))
    f.append(text((x0 + t_r1_apply) / 2, yR1 + 4, "Старий стан (LSN 4119)", size=11, color=POS))
    f.append(rect(t_r1_apply, yR1 - 12, x1 - t_r1_apply, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_r1_apply + x1) / 2, yR1 + 4, "Свіжий стан (LSN 4120)", size=11, color=FIELD))

    # Подія читання R1 (порушення Read-Your-Writes) - знизу під Replica 1
    t_read1 = t_w + span * 0.16
    f.append(arrow(t_read1, yR1 + 40, t_read1, yR1 + 14, color=POS, sw=2.0))
    b1, _, _ = textbox(t_read1 + 50, yR1 + 60, "Читання R1 (не бачить W1!)\nАномалія: порушення RYW",
                       size=10.5, pad=5, fill=WARM, stroke=POS, sw=1.5, color=POS, bold=True)
    f.append(b1)

    # Подія читання R2 (успішне читання з Replica 1) - зверху над Replica 1
    t_read2 = t_r1_apply + span * 0.14
    f.append(arrow(t_read2, yR1 - 40, t_read2, yR1 - 14, color=FIELD, sw=2.0))
    b2, _, _ = textbox(t_read2, yR1 - 60, "Читання R2 (LSN 4120)\nСвіжі актуальні дані",
                       size=10.5, pad=5, fill=GOOD, stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    f.append(b2)

    # ── Доріжка 3: Replica 2 (Повільна репліка)
    yR2 = 450.0
    f.append(fitbox(30, yR2 - 28, 200, 56, "REPLICA 2\nлаг Δt = 700 мс", size=12, bold=True, fill=COOL))
    f.append(line(x0, yR2, x1, yR2, color=LINE, sw=2.0))
    f.append(arrow(x1 - 10, yR2, x1 + 15, yR2, color=LINE, sw=2.0))
    f.append(text(x1 + 30, yR2 + 4, "t", size=13, italic=True))

    t_r2_apply = t_w + span * 0.72
    # Передача WAL до Replica 2 ведеться від Replica 1
    f.append(line(t_r1_apply + 20, yR1 + 14, t_r2_apply - 10, yR2 - 14, color=MUTED, sw=1.8, dash="4,4"))
    f.append(arrow(t_r2_apply - 20, yR2 - 24, t_r2_apply, yR2 - 12, color=MUTED, sw=1.8))

    f.append(rect(x0, yR2 - 12, t_r2_apply - x0, 24, fill=WARM, stroke=POS, sw=1.2))
    f.append(text((x0 + t_r2_apply) / 2, yR2 + 4, "Старий стан (LSN 4119)", size=11, color=POS))
    f.append(rect(t_r2_apply, yR2 - 12, x1 - t_r2_apply, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_r2_apply + x1) / 2, yR2 + 4, "Свіжий стан (LSN 4120)", size=11, color=FIELD))

    # Подія читання R3 (відкіт часу назад при перемиканні на Replica 2 знизу від Replica 2)
    t_read3 = t_read2 + span * 0.16
    f.append(arrow(t_read3, yR2 + 40, t_read3, yR2 + 14, color=POS, sw=2.0))
    b3, _, _ = textbox(t_read3 + 60, yR2 + 60, "Читання R3 (повернувся LSN 4119)\nАномалія: немонотонне читання",
                       size=10.5, pad=5, fill=WARM, stroke=POS, sw=1.5, color=POS, bold=True)
    f.append(b3)

    # Пояснювальний підсумок знизу
    f.append(fitbox(W / 2 - 440, 565, 880, 42,
                    "Лаг не є сталою: різні репліки відстають на різний час. Без сесійного контролю клієнт спостерігає відкати та зникнення власних правок.",
                    size=12, bold=False, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, "replication-lag-timeline.svg"), W, H, *f)


# ── 2. Таксономія чотирьох сесійних гарантій ─────────────────────────────────
def session_guarantees_taxonomy():
    W, H = 1160, 620
    f = []

    f.append(text(W / 2, 34, "Чотири сесійні гарантії узгодженості (модель Террі, Xerox PARC)",
                  size=16, bold=True))

    col_w = 540.0
    row_h = 240.0
    x_left = 30.0
    x_right = 590.0
    y_top = 65.0
    y_bot = 335.0

    # 1. Read-Your-Writes
    f.append(rect(x_left, y_top, col_w, row_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(rect(x_left, y_top, col_w, 36, fill=COOL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_left + col_w / 2, y_top + 23, "1. Читай власні записи (Read-Your-Writes / RYW)",
                  size=13, bold=True))

    t1 = ("Гарантія: Клієнт завжди бачить власні попередні записи в усіх наступних читаннях.\n\n"
          "Сценарій без гарантії: Користувач оновив біографію, оновив сторінку й бачить старий текст.\n"
          "Він надсилає форму повторно, створюючи дублікати й плутанину.\n\n"
          "Формально: W_k(x) <_session R_m(x) => R_m повертає версію x >= версії від W_k.")
    f.append(fitbox(x_left + 15, y_top + 48, col_w - 30, row_h - 60, t1, size=11.5, fill="#ffffff", stroke=FIELD))

    # 2. Monotonic Reads
    f.append(rect(x_right, y_top, col_w, row_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(rect(x_right, y_top, col_w, 36, fill=COOL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_right + col_w / 2, y_top + 23, "2. Монотонне читання (Monotonic Reads / MR)",
                  size=13, bold=True))

    t2 = ("Гарантія: Наступні читання клієнта ніколи не повертають старіший стан, ніж уже бачений.\n\n"
          "Сценарій без гарантії: Перший запит прочитав 10 коментарів з актуальної репліки R1.\n"
          "Наступний запит потрапив на відсталу репліку R2 — 3 коментарі раптом «зникли».\n\n"
          "Формально: R_k(x) повернуло версію v_1 => для будь-якого R_m(x) пізніше у сесії версія v_2 >= v_1.")
    f.append(fitbox(x_right + 15, y_top + 48, col_w - 30, row_h - 60, t2, size=11.5, fill="#ffffff", stroke=FIELD))

    # 3. Monotonic Writes
    f.append(rect(x_left, y_bot, col_w, row_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(rect(x_left, y_bot, col_w, 36, fill=COOL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_left + col_w / 2, y_bot + 23, "3. Монотонний запис (Monotonic Writes / MW)",
                  size=13, bold=True))

    t3 = ("Гарантія: Записи одного клієнта застосовуються на всіх репліках у порядку їх надсилання.\n\n"
          "Сценарій без гарантії: Запис W1 (створити замовлення) і запис W2 (скасувати його).\n"
          "Якщо W2 застосується раніше за W1, скасування впаде з помилкою, а потім створиться вічне замовлення.\n\n"
          "Формально: W_k <_session W_m => на будь-якому вузлі W_k виконується перед W_m.")
    f.append(fitbox(x_left + 15, y_bot + 48, col_w - 30, row_h - 60, t3, size=11.5, fill="#ffffff", stroke=FIELD))

    # 4. Writes-Follow-Reads
    f.append(rect(x_right, y_bot, col_w, row_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(rect(x_right, y_bot, col_w, 36, fill=COOL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_right + col_w / 2, y_bot + 23, "4. Запис слідує за читанням (Writes-Follow-Reads / WFR)",
                  size=13, bold=True))

    t4 = ("Гарантія: Якщо клієнт прочитав стан V і зробив запис W, W упорядковується після всіх записів у V.\n\n"
          "Сценарій без гарантії: Аліса прочитала пост і написала відповідь «Погоджуюсь». Боб бачить\n"
          "відповідь Аліси на іншій репліці, де сам початковий пост ще не з'явився (відповідь у нікуди).\n\n"
          "Формально: R_k(x) спостерігав W_prev => для будь-якого наступного W_m маємо W_prev < W_m.")
    f.append(fitbox(x_right + 15, y_bot + 48, col_w - 30, row_h - 60, t4, size=11.5, fill="#ffffff", stroke=FIELD))

    # Нижня плашка
    f.append(fitbox(W / 2 - 450, 585, 900, 26,
                    "Сесійні гарантії ізолюють очікування одного клієнта без потреби блокувати всю систему глобальним консенсусом.",
                    size=12, bold=True, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, "session-guarantees-taxonomy.svg"), W, H, *f)


# ── 3. Маршрутизація з причинними маркерами (Causal LSN Tokens) ──────────────
def causal_tokens_routing():
    W, H = 1180, 580
    f = []

    f.append(text(W / 2, 32, "Маршрутизація сесійних запитів за допомогою LSN-маркерів (Causal Tokens)",
                  size=16, bold=True))

    # Клієнт зліва
    x_client = 120.0
    f.append(rect(30, 80, 180, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_client, 110, "КЛІЄНТСЬКА СЕСІЯ", size=13, bold=True))
    f.append(text(x_client, 130, "(Браузер / Мобільний додаток)", size=11, color=MUTED))

    f.append(rect(45, 160, 150, 80, fill=GOOD, stroke=FIELD, sw=1.4, rx=6))
    f.append(mtext(x_client, 185, ["Сесійний стан:", "min_lsn = 5042", "last_write = t_0"], size=11, bold=True))

    f.append(rect(45, 270, 150, 90, fill=COOL, stroke=LINE, sw=1.2, rx=6))
    f.append(mtext(x_client, 295, ["Запити несуть токен:", "Cookie: min_lsn=5042", "або X-Session-LSN"], size=10.5))

    # Шлюз по центру
    x_gw = 460.0
    f.append(rect(360, 80, 200, 390, fill=COOL, stroke=LINE, sw=1.8, rx=8))
    f.append(text(x_gw, 110, "API-ШЛЮЗ / МАРШРУТИЗАТОР", size=13, bold=True))
    f.append(text(x_gw, 130, "Сесійний диспетчер", size=11, color=MUTED))

    # Логіка шлюзу
    f.append(rect(375, 160, 170, 120, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    f.append(mtext(x_gw, 185, ["1. Запис (POST/PUT):", "   -> Завжди на Primary", "   -> Отримує commit LSN", "   -> Оновлює токен клієнта"], size=11))

    f.append(rect(375, 300, 170, 150, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    f.append(mtext(x_gw, 325, ["2. Читання (GET):", "   -> Перевіряє min_lsn", "   -> Фільтрує репліки:", "      applied_lsn >= min_lsn", "   -> Якщо відстають:", "      чекає або на Primary"], size=11))

    # Вузли бази даних справа
    x_db = 940.0

    # 1. Primary
    y_p = 135.0
    f.append(rect(780, y_p - 45, 320, 90, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x_db, y_p - 20, "PRIMARY ВУЗОЛ (Лідер)", size=13, bold=True, color=FIELD))
    f.append(mtext(x_db, y_p + 10, ["Поточний стан: LSN = 5042", "Приймає записи та генерує WAL"], size=11))

    # 2. Replica A (Актуальна)
    y_ra = 275.0
    f.append(rect(780, y_ra - 45, 320, 90, fill=GOOD, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x_db, y_ra - 20, "REPLICA 1 (Актуальна)", size=13, bold=True, color=FIELD))
    f.append(mtext(x_db, y_ra + 10, ["applied_lsn = 5042 (>= min_lsn 5042)", "✓ ДОЗВОЛЕНО для читання RYW"], size=11, color=FIELD))

    # 3. Replica B (Відстала)
    y_rb = 415.0
    f.append(rect(780, y_rb - 45, 320, 90, fill=WARM, stroke=POS, sw=1.5, rx=8))
    f.append(text(x_db, y_rb - 20, "REPLICA 2 (Відстає на 450 мс)", size=13, bold=True, color=POS))
    f.append(mtext(x_db, y_rb + 10, ["applied_lsn = 5038 (< min_lsn 5042)", "✗ ВІДХИЛЕНО або пауза WAIT_FOR_LSN"], size=11, color=POS))

    # Стрілки взаємодії
    # Клієнт -> Шлюз (Запис)
    f.append(arrow(210, 180, 360, 180, color=POS, sw=2.0))
    f.append(text(285, 170, "1. POST (write)", size=11, color=POS, bold=True))

    # Шлюз -> Primary
    f.append(arrow(560, 150, 780, 150, color=POS, sw=2.0))
    f.append(text(670, 140, "2. Commit", size=11, color=POS, bold=True))

    # Primary -> Шлюз (commit LSN)
    f.append(arrow(780, 180, 560, 180, color=FIELD, sw=1.8))
    f.append(text(670, 195, "3. LSN = 5042", size=11, color=FIELD, bold=True))

    # Шлюз -> Клієнт (Set-Cookie)
    f.append(arrow(360, 220, 210, 220, color=FIELD, sw=1.8))
    f.append(text(285, 235, "4. Token min_lsn=5042", size=11, color=FIELD, bold=True))

    # Клієнт -> Шлюз (Читання з токеном)
    f.append(arrow(210, 350, 360, 350, color=NEG, sw=2.0))
    f.append(text(285, 340, "5. GET (min_lsn=5042)", size=11, color=NEG, bold=True))

    # Шлюз -> Replica 1
    f.append(arrow(560, 320, 780, 275, color=FIELD, sw=2.0))
    f.append(text(670, 285, "6a. Маршрутизація на R1", size=11, color=FIELD, bold=True))

    # Шлюз -/- Replica 2
    f.append(line(560, 370, 780, 415, color=POS, sw=1.8, dash="4,4"))
    f.append(text(670, 410, "6b. Блокування читання R2", size=11, color=POS, bold=True))

    # Підсумок знизу
    f.append(fitbox(W / 2 - 460, 505, 920, 48,
                    "Токен прив'язує читання до монотонного номеру журналу (LSN/GTID), гарантуючи сесійні властивості без необхідності направляти всі запити на Primary.",
                    size=12, bold=False, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, "causal-tokens-routing.svg"), W, H, *f)


if __name__ == '__main__':
    replication_lag_timeline()
    session_guarantees_taxonomy()
    causal_tokens_routing()
    print("Всі 3 фігури згенеровано успішно.")
