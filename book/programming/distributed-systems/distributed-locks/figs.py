# -*- coding: utf-8 -*-
"""Фігури до теми «Розподілені замки й лізи»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / конфлікт
COOL = "#eaf0fd"   # нейтральний блок / інфо
GOOD = "#e8f6ee"   # успіх / захищено
WARN = "#fef9e7"   # попередження / таймер


# ── 1. Небезпека паузи процесу: порушення виключності без огорожі ─────────────
def fig_lock_pause_split():
    W, H = 1080, 560
    f = []

    x1 = 180.0  # Клієнт 1
    xS = 540.0  # Сервер замків / Сховище
    x2 = 900.0  # Клієнт 2

    # Заголовки сутностей
    f.append(fitbox(x1 - 120, 20, 240, 50, "Клієнт 1\n(отримує замок)", size=13, bold=True, fill=COOL))
    f.append(fitbox(xS - 120, 20, 240, 50, "Сервер замків і Сховище\n(замок TTL = 10 с)", size=13, bold=True, fill=FILL))
    f.append(fitbox(x2 - 120, 20, 240, 50, "Клієнт 2\n(перехоплює замок)", size=13, bold=True, fill=COOL))

    yP_start = 180.0
    yP_end = 390.0

    # Вертикальні лінії часу (розриваємо навколо боксів, щоб лінія не перетинала написи)
    f.append(line(x1, 80, x1, yP_start - 5, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(x1, yP_end + 5, x1, 520, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(xS, 80, xS, 235, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 275, xS, 370, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 405, xS, 475, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(x2, 80, x2, 520, color=LINE, sw=1.5, dash="4,4"))

    # Подія 1: Клієнт 1 бере замок (t = 0)
    y1 = 110.0
    f.append(arrow(x1, y1, xS, y1 + 20, color=FIELD))
    f.append(text((x1 + xS) / 2, y1 - 6, "1. Запит: Захопити замок (TTL 10 с)", size=11.5, color=FIELD, bold=True))

    y2 = 145.0
    f.append(arrow(xS, y2, x1, y2 + 20, color=FIELD))
    f.append(text((x1 + xS) / 2, y2 - 6, "2. Замок надано на 10 с", size=11.5, color=FIELD))

    # Подія 2: Клієнт 1 зависає в GC-паузі
    f.append(fitbox(x1 - 75, yP_start, 150, yP_end - yP_start,
                    "ПАУЗА ПРОЦЕСУ\n(Stop-the-world GC,\nсвопінг або VM-лаг)\nтривалість 15 с",
                    size=11, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    # Ліза спливає на сервері (t = 10 с)
    yExp = 255.0
    f.append(circle(xS, yExp, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(fitbox(xS - 140, yExp - 16, 280, 32, "Ліза Клієнта 1 спливла (час вийшов)", size=11, bold=True, fill=WARM))

    # Подія 3: Клієнт 2 бере той самий замок
    y3 = 290.0
    f.append(arrow(x2, y3, xS, y3 + 20, color=FIELD))
    f.append(text((x2 + xS) / 2, y3 - 6, "3. Запит замка", size=11.5, color=FIELD, bold=True))

    y4 = 325.0
    f.append(arrow(xS, y4, x2, y4 + 20, color=FIELD))
    f.append(text((x2 + xS) / 2, y4 - 6, "4. Замок надано Клієнту 2", size=11.5, color=FIELD))

    # Подія 4: Клієнт 2 пише у сховище
    y5 = 360.0
    f.append(arrow(x2, y5, xS, y5 + 20, color=FIELD))
    f.append(text((x2 + xS) / 2, y5 - 6, "5. Запис даних (Клієнт 2)", size=11.5, color=FIELD))
    f.append(fitbox(xS - 90, y5 + 15, 180, 26, "Запис Клієнта 2 успішний", size=11, bold=True, fill=GOOD))

    # Подія 5: Клієнт 1 прокидається і пише застарілі дані!
    y6 = 430.0
    f.append(arrow(x1, y6, xS, y6 + 25, color=POS, sw=2.2))
    f.append(mtext((x1 + xS) / 2, y6 - 8, "6. Запізнілий запис Клієнта 1\n(вважає, що замок досі його!)", size=11.5, color=POS, bold=True))

    # Катастрофа у сховищі
    yCrash = 485.0
    f.append(fitbox(xS - 220, yCrash, 440, 52, "КОНФЛІКТ І ПОРУШЕННЯ ЦІЛІСНОСТІ!\nСховище перезаписане застарілими даними", size=12, bold=True, fill=WARM))

    render(os.path.join(OUT, "lock-pause-split.svg"), W, H, "".join(f))


# ── 2. Огорожа (Fencing Tokens): захист сховища від запізнілих записів ────────
def fig_fencing_token():
    W, H = 1080, 560
    f = []

    x1 = 180.0
    xS = 540.0
    x2 = 900.0

    f.append(fitbox(x1 - 120, 20, 240, 50, "Клієнт 1\n(токен огорожі: 34)", size=13, bold=True, fill=COOL))
    f.append(fitbox(xS - 130, 20, 260, 50, "Сервер замків і Сховище\n(контроль версії токена)", size=13, bold=True, fill=FILL))
    f.append(fitbox(x2 - 120, 20, 240, 50, "Клієнт 2\n(токен огорожі: 35)", size=13, bold=True, fill=COOL))

    yP_start = 150.0
    yP_end = 360.0

    # Вертикальні лінії часу (розриваємо навколо боксів)
    f.append(line(x1, 80, x1, yP_start - 5, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(x1, yP_end + 5, x1, 520, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(xS, 80, xS, 280, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 340, xS, 435, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(x2, 80, x2, 520, color=LINE, sw=1.5, dash="4,4"))

    # 1. Видача токена 34
    y1 = 110.0
    f.append(arrow(xS, y1, x1, y1 + 20, color=FIELD))
    f.append(text((x1 + xS) / 2, y1 - 6, "Замок надано, токен = 34", size=11.5, color=FIELD, bold=True))

    # Клієнт 1 зависає
    f.append(fitbox(x1 - 75, yP_start, 150, yP_end - yP_start,
                    "ПАУЗА ПРОЦЕСУ\n(тривалість перевищує\nстрок лізи)",
                    size=11, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    # 2. Клієнт 2 отримує токен 35
    y2 = 210.0
    f.append(arrow(xS, y2, x2, y2 + 20, color=FIELD))
    f.append(text((x2 + xS) / 2, y2 - 6, "Замок надано, токен = 35", size=11.5, color=FIELD, bold=True))

    # 3. Клієнт 2 записує дані з токеном 35
    y3 = 260.0
    f.append(arrow(x2, y3, xS, y3 + 20, color=FIELD))
    f.append(text((x2 + xS) / 2, y3 - 6, "Запис (токен = 35)", size=11.5, color=FIELD))

    y3_check = 295.0
    f.append(fitbox(xS - 145, y3_check, 290, 36, "Сховище: 35 > 0 → ПРИЙНЯТО\n(максимальний токен = 35)", size=11, bold=True, fill=GOOD))

    # 4. Клієнт 1 прокидається і надсилає запізнілий запис із токеном 34
    y4 = 400.0
    f.append(arrow(x1, y4, xS, y4 + 25, color=POS, sw=2.0))
    f.append(text((x1 + xS) / 2, y4 - 6, "Запізнілий запис (токен = 34)", size=11.5, color=POS, bold=True))

    # 5. Сховище відхиляє токен 34
    y5_reject = 445.0
    f.append(fitbox(xS - 180, y5_reject, 360, 56, "Сховище: 34 < 35 → ВІДХИЛЕНО!\nЗастарілий запис заблоковано огорожею.\nЦілісність даних збережено.", size=11.5, bold=True, fill=GOOD))

    render(os.path.join(OUT, "fencing-token.svg"), W, H, "".join(f))


# ── 3. Порівняння: Кеш-замок проти Консенсусного замка ────────────────────────
def fig_consensus_vs_cache_lock():
    W, H = 1080, 520
    f = []

    # Ліва колонка: Кеш-замок (Redis / Memcached)
    f.append(fitbox(40, 25, 470, 55, "КЕШ-ЗАМОК (Redis / SETNX / Redlock)\nОрієнтація: Швидкість та ефективність", size=13, bold=True, fill=WARN))

    yL = 100.0
    f.append(rect(40, yL, 470, 390, fill=FILL, stroke=MUTED, sw=1.5, rx=8))

    items_cache = [
        ("Призначення", "Захист від дублювання роботи (ефективність)", GOOD),
        ("Механізм", "Ключ із TTL + перевірка випадкового значення (Lua)", COOL),
        ("Слабке місце", "Асинхронна реплікація: втрата замка при аварії майстра", WARM),
        ("Годинник", "Спирається на локальний настінний/монотонний час", WARM),
        ("Наслідок збою", "Можливий одночасний доступ двох клієнтів", WARM),
        ("Ціна відмови", "Низька (повторний розрахунок, зайвий лист)", GOOD),
    ]

    for i, (k, v, bg) in enumerate(items_cache):
        yy = yL + 15 + i * 60
        f.append(fitbox(55, yy, 440, 48, f"{k}: {v}", size=11.5, bold=False, fill=bg))

    # Права колонка: Консенсусний замок (etcd / ZooKeeper / Chubby)
    f.append(fitbox(570, 25, 470, 55, "КОНСЕНСУСНИЙ ЗАМОК (etcd / ZooKeeper)\nОрієнтація: Строга коректність і лінеаризовність", size=13, bold=True, fill=COOL))

    yR = 100.0
    f.append(rect(570, yR, 470, 390, fill=FILL, stroke=MUTED, sw=1.5, rx=8))

    items_cons = [
        ("Призначення", "Запобігання псуванню даних (строга коректність)", GOOD),
        ("Механізм", "Ефемерні вузли, Raft/Paxos-кворум, лізи з KeepAlive", GOOD),
        ("Стійкість", "Переживає падіння лідера без втрати інформації", GOOD),
        ("Огорожа", "Монотонні лічильники (zxid, revision) для ресурсів", GOOD),
        ("Черга очікування", "Спостереження (Watch) без штурму опитуванням", GOOD),
        ("Ціна", "Вища латентність (RTP consensus round-trips)", COOL),
    ]

    for i, (k, v, bg) in enumerate(items_cons):
        yy = yR + 15 + i * 60
        f.append(fitbox(585, yy, 440, 48, f"{k}: {v}", size=11.5, bold=False, fill=bg))

    render(os.path.join(OUT, "consensus-vs-cache-lock.svg"), W, H, "".join(f))


# ── 4. Часова шкала лізи: сторожовий таймер та безпечне вікно ─────────────────
def fig_lease_timeline():
    W, H = 1080, 520
    f = []

    x0 = 80.0
    x_end = 1000.0
    span = x_end - x0

    # Шкала сервера (Ліза тривалістю L)
    yS = 130.0
    f.append(fitbox(x0, yS - 80, 260, 40, "Шкала сервера (період лізи L = 10 с)", size=12, bold=True, fill=COOL))

    # Смуга лізи на сервері
    f.append(rect(x0, yS, span * 0.7, 36, fill=GOOD, stroke=FIELD, sw=1.6, rx=4))
    f.append(text(x0 + (span * 0.7) / 2, yS + 23, "Чинна ліза на сервері (0 ... 10 с)", size=12.5, bold=True))

    f.append(rect(x0 + span * 0.7, yS, span * 0.3, 36, fill=WARM, stroke=POS, sw=1.6, rx=4))
    f.append(text(x0 + span * 0.85, yS + 23, "Ліза спливла (замок вільний)", size=12, color=POS, bold=True))

    # Поділки на шкалі сервера
    f.append(line(x0, yS - 6, x0, yS + 42, color=LINE, sw=2))
    f.append(text(x0, yS + 58, "t = 0", size=11))

    f.append(line(x0 + span * 0.7, yS - 6, x0 + span * 0.7, yS + 42, color=POS, sw=2))
    f.append(text(x0 + span * 0.7, yS + 58, "t = L (10 с)", size=11, color=POS, bold=True))

    # Шкала клієнта (Безпечне вікно + Фонове оновлення)
    yC = 300.0
    f.append(fitbox(x0, yC - 80, 320, 40, "Шкала клієнта (робота та подовження)", size=12, bold=True, fill=COOL))

    # Затримка отримання відповіді мережею (RTT / 2)
    x_ack = x0 + span * 0.08
    f.append(rect(x0, yC, span * 0.08, 36, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text((x0 + x_ack) / 2, yC + 22, "RTT/2", size=10.5, color=MUTED))

    # Безпечне вікно виконання (Safe Window)
    x_safe_end = x0 + span * 0.52
    f.append(rect(x_ack, yC, x_safe_end - x_ack, 36, fill=GOOD, stroke=FIELD, sw=1.6, rx=4))
    f.append(mtext((x_ack + x_safe_end) / 2, yC + 15, "Безпечне вікно виконання W_safe\n(дозволено критичну секцію)", size=11, bold=True))

    # Вікно оновлення сторожем (Watchdog Renewal)
    x_renew = x0 + span * 0.25
    f.append(arrow(x_renew, yC + 50, x_renew, yC + 38, color=FIELD, sw=2))
    f.append(fitbox(x_renew - 90, yC + 55, 180, 40, "Тик сторожа (T = L/3)\nЗапит подовження лізи", size=11, bold=True, fill=WARN))

    # Небезпечна зона після виходу з безпечного вікна
    f.append(rect(x_safe_end, yC, (x0 + span * 0.7) - x_safe_end, 36, fill=WARM, stroke=POS, sw=1.6, rx=4))
    f.append(mtext((x_safe_end + (x0 + span * 0.7)) / 2, yC + 15, "Небезпечна зона\n(дрейф годинника + RTT)", size=10.5, color=POS, bold=True))

    # Пояснення знизу
    f.append(fitbox(x0, 430, span, 60,
                    "Правило надійності: Клієнт виконує роботу лише у межах безпечного вікна W_safe.\n"
                    "Сторожовий таймер оновлює лізу завчасно (кожні L/3), не чекаючи вичерпання строку.",
                    size=12, bold=False, fill=FILL))

    render(os.path.join(OUT, "lease-timeline.svg"), W, H, "".join(f))


if __name__ == "__main__":
    fig_lock_pause_split()
    fig_fencing_token()
    fig_consensus_vs_cache_lock()
    fig_lease_timeline()
    print("All figures generated successfully.")
