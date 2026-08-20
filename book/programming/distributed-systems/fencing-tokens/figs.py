# -*- coding: utf-8 -*-
"""Фігури до теми «Fencing-токени розподілених блокувань»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / конфлікт / відхилення
COOL = "#eaf0fd"   # клієнт / нейтральний блок
GOOD = "#e8f6ee"   # успіх / захищене сховище
WARN = "#fef9e7"   # таймер / попередження / координатор


# ── 1. Небезпека без токенів: запізнілий запис руйнує стан ─────────────────────
def fig_fencing_race_condition():
    W, H = 1060, 560
    f = []

    x1 = 180.0  # Клієнт 1
    xS = 530.0  # Координатор замків і Сховище
    x2 = 880.0  # Клієнт 2

    # Заголовки сутностей
    f.append(fitbox(x1 - 120, 20, 240, 50, "Клієнт 1 (Воркер A)\n[отримує замок]", size=13, bold=True, fill=COOL))
    f.append(fitbox(xS - 130, 20, 260, 50, "Координатор і Сховище\n[без перевірки токенів]", size=13, bold=True, fill=FILL))
    f.append(fitbox(x2 - 120, 20, 240, 50, "Клієнт 2 (Воркер B)\n[перехоплює замок]", size=13, bold=True, fill=COOL))

    yP_start = 175.0
    yP_end = 385.0

    # Вертикальні лінії життя (пунктир із розривами під плашки)
    f.append(line(x1, 75, x1, yP_start - 5, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(x1, yP_end + 5, x1, 520, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(xS, 75, xS, 230, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 270, xS, 365, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 400, xS, 470, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 510, xS, 530, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(x2, 75, x2, 520, color=LINE, sw=1.5, dash="4,4"))

    # Подія 1: Клієнт 1 отримує замок (t = 0)
    y1 = 100.0
    f.append(arrow(x1, y1, xS, y1 + 18, color=FIELD))
    f.append(text((x1 + xS) / 2, y1 - 6, "1. Запит: Захопити замок (TTL = 10 с)", size=11.5, color=FIELD, bold=True))

    y2 = 135.0
    f.append(arrow(xS, y2, x1, y2 + 18, color=FIELD))
    f.append(text((x1 + xS) / 2, y2 - 6, "2. Замок надано Клієнту 1 (TTL = 10 с)", size=11.5, color=FIELD))

    # Подія 2: Клієнт 1 зависає у GC / swap
    f.append(fitbox(x1 - 85, yP_start, 170, yP_end - yP_start,
                    "ПАУЗА ПРОЦЕСУ\n(Stop-the-world GC,\nсвоп або VM-лаг)\nтривалість 18 с",
                    size=11, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    # Ліза спливає на координаторі (t = 10 с)
    yExp = 250.0
    f.append(circle(xS, yExp, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(fitbox(xS - 110, yExp - 16, 220, 32, "t = 10 с: Ліза Клієнта 1 спливла", size=11, bold=True, fill=WARN, stroke=POS, sw=1.2))

    # Подія 3: Клієнт 2 бере замок (t = 11 с)
    y3 = 295.0
    f.append(arrow(x2, y3, xS, y3 + 18, color=NEG))
    f.append(text((xS + x2) / 2, y3 - 6, "3. Запит замка від Клієнта 2", size=11.5, color=NEG, bold=True))

    y4 = 330.0
    f.append(arrow(xS, y4, x2, y4 + 18, color=NEG))
    f.append(text((xS + x2) / 2, y4 - 6, "4. Замок надано Клієнту 2", size=11.5, color=NEG))

    # Подія 4: Клієнт 2 записує дані у сховище (t = 13 с)
    y5 = 370.0
    f.append(arrow(x2, y5, xS, y5 + 18, color=NEG))
    f.append(text((xS + x2) / 2, y5 - 6, "5. write(balance = $6500) від Клієнта 2", size=11.5, color=NEG, bold=True))

    y5_ack = 390.0
    f.append(fitbox(xS - 115, y5_ack - 10, 230, 24, "Запис прийнято: balance = $6500", size=10.5, bold=True, fill=GOOD, stroke=FIELD))

    # Подія 5: Клієнт 1 прокидається і надсилає застарілий запис (t = 18 с)
    y6 = 475.0
    f.append(arrow(x1, y6, xS, y6 + 18, color=POS))
    f.append(text((x1 + xS) / 2, y6 - 6, "6. Запізнілий write(balance = $3000) від Клієнта 1", size=11.5, color=POS, bold=True))

    # Катастрофа: затирання стану
    yCrit = 495.0
    f.append(fitbox(xS - 130, yCrit, 260, 48,
                    "КАТАСТРОФА: стан $6500 затерто на $3000!\nСховище не знало, що ліза спливла",
                    size=10.5, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    render(os.path.join(OUT, "fencing-race-condition.svg"), W, H, "".join(f),
           title="Порушення взаємного виключення через паузу процесу (без токенів огорожі)")


# ── 2. Захист токенами огорожі: сховище відсікає старий токен ──────────────────
def fig_fencing_token_validation():
    W, H = 1060, 580
    f = []

    x1 = 180.0  # Клієнт 1
    xS = 530.0  # Сховище (з валідацією токенів)
    x2 = 880.0  # Клієнт 2

    # Заголовки сутностей
    f.append(fitbox(x1 - 120, 20, 240, 50, "Клієнт 1 (Воркер A)\n[токен = 34]", size=13, bold=True, fill=COOL))
    f.append(fitbox(xS - 140, 20, 280, 50, "Спільне сховище даних\n[max_token_seen]", size=13, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(x2 - 120, 20, 240, 50, "Клієнт 2 (Воркер B)\n[токен = 35]", size=13, bold=True, fill=COOL))

    yP_start = 175.0
    yP_end = 385.0

    # Вертикальні лінії
    f.append(line(x1, 75, x1, yP_start - 5, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(x1, yP_end + 5, x1, 540, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(xS, 75, xS, 230, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 270, xS, 365, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 425, xS, 470, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(xS, 525, xS, 545, color=LINE, sw=1.5, dash="4,4"))

    f.append(line(x2, 75, x2, 540, color=LINE, sw=1.5, dash="4,4"))

    # Подія 1: Клієнт 1 отримує замок із токеном 34
    y1 = 100.0
    f.append(fitbox((x1 + xS) / 2 - 140, y1 - 15, 280, 30, "1. Координатор видав замок з токеном = 34", size=11, bold=True, fill=WARN, stroke=FIELD))
    f.append(arrow(xS, y1 + 18, x1, y1 + 18, color=FIELD))

    # Подія 2: Клієнт 1 зависає
    f.append(fitbox(x1 - 85, yP_start, 170, yP_end - yP_start,
                    "ПАУЗА ПРОЦЕСУ\n(Stop-the-world GC)\nтривалість 18 с",
                    size=11, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    # Ліза спливає на координаторі
    yExp = 250.0
    f.append(circle(xS, yExp, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(fitbox(xS - 110, yExp - 16, 220, 32, "t = 10 с: Ліза токена 34 спливла", size=11, bold=True, fill=WARN, stroke=POS, sw=1.2))

    # Подія 3: Клієнт 2 бере замок з токеном 35
    y3 = 295.0
    f.append(fitbox((xS + x2) / 2 - 140, y3 - 15, 280, 30, "2. Координатор видав замок з токеном = 35", size=11, bold=True, fill=WARN, stroke=NEG))
    f.append(arrow(xS, y3 + 18, x2, y3 + 18, color=NEG))

    # Подія 4: Клієнт 2 надсилає запис із токеном 35
    y5 = 370.0
    f.append(arrow(x2, y5, xS, y5 + 18, color=NEG))
    f.append(text((xS + x2) / 2, y5 - 6, "3. write(balance = $6500, token = 35)", size=11.5, color=NEG, bold=True))

    y5_box = 395.0
    f.append(fitbox(xS - 135, y5_box, 270, 40,
                    "Сховище: 35 >= 0 -> ПРИЙНЯТО\nВстановлено: max_token = 35, data = $6500",
                    size=10.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Подія 5: Клієнт 1 прокидається і надсилає запис із токеном 34
    y6 = 475.0
    f.append(arrow(x1, y6, xS, y6 + 18, color=POS))
    f.append(text((x1 + xS) / 2, y6 - 6, "4. write(balance = $3000, token = 34)", size=11.5, color=POS, bold=True))

    # Відхилення через огорожу
    yRej = 498.0
    f.append(fitbox(xS - 145, yRej, 290, 42,
                    "ОГОРОЖА: 34 < 35 -> ВІДХИЛЕНО!\nПомилка: STALE_FENCING_TOKEN",
                    size=11, bold=True, color=POS, fill=WARM, stroke=POS, sw=1.8))

    render(os.path.join(OUT, "fencing-token-validation.svg"), W, H, "".join(f),
           title="Захист цілісності даних через валідацію токенів огорожі на стороні сховища")


# ── 3. Загальна архітектура: Координатор, Клієнти та Бар'єр сховища ────────────
def fig_fencing_epoch_architecture():
    W, H = 1040, 520
    f = []

    # 1. Верхній рівень: Координатор консенсусу (Raft / etcd / ZooKeeper)
    f.append(rect(80, 40, 880, 110, fill=WARN, stroke=LINE, sw=1.8, rx=8))
    f.append(text(520, 68, "Розподілений координатор замків (etcd / ZooKeeper / Raft)", size=15, bold=True, color=INK))
    f.append(fitbox(110, 85, 380, 50, "Атомарний лічильник покоління (Epoch Generator)\nМонотонна послідовність: T_{n+1} > T_n", size=11.5, fill=BG, stroke=LINE))
    f.append(fitbox(550, 85, 380, 50, "Оренда з тайм-аутом (Lease Engine)\nВидача прав: Grant { client_id, token, ttl }", size=11.5, fill=BG, stroke=LINE))

    # Стрілки від Координатора до Клієнтів
    f.append(arrow(300, 150, 240, 205, color=FIELD, sw=2.0))
    f.append(text(210, 180, "grant(token = 42)", size=11, color=FIELD, bold=True))

    f.append(arrow(740, 150, 800, 205, color=POS, sw=2.0))
    f.append(text(830, 180, "старий token = 41", size=11, color=POS, bold=True))

    # 2. Середній рівень: Два воркери (Активний і Зомбі після паузи)
    f.append(rect(80, 210, 360, 105, fill=GOOD, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(260, 235, "Активний лідер (Воркер 2)", size=13.5, bold=True, color=FIELD))
    f.append(fitbox(95, 250, 330, 52, "Поточний дійсний токен: T = 42\nФормує запит: MutationRequest { data, token=42 }", size=11, fill=BG, stroke=FIELD))

    f.append(rect(600, 210, 360, 105, fill=WARM, stroke=POS, sw=1.8, rx=8))
    f.append(text(780, 235, "Зомбі-воркер (Воркер 1 після GC)", size=13.5, bold=True, color=POS))
    f.append(fitbox(615, 250, 330, 52, "Застарілий токен у пам'яті: T = 41\nФормує запізнілий: MutationRequest { data, token=41 }", size=11, fill=BG, stroke=POS))

    # Стрілки від Клієнтів до Сховища
    f.append(arrow(260, 315, 360, 375, color=FIELD, sw=2.0))
    f.append(text(260, 352, "RPC: write(T=42)", size=11.5, color=FIELD, bold=True))

    f.append(arrow(780, 315, 680, 375, color=POS, sw=2.0))
    f.append(text(790, 352, "RPC: write(T=41)", size=11.5, color=POS, bold=True))

    # 3. Нижній рівень: Сховище даних із бар'єром перевірки
    f.append(rect(80, 380, 880, 115, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    f.append(text(520, 405, "Спільне сховище (SQL DB / Key-Value / Fencing Proxy)", size=15, bold=True, color=INK))

    f.append(fitbox(110, 420, 390, 62, "Бар'єр валідації (Fencing Filter)\nif token >= highest_token:\n    highest_token = token; apply_write()\nelse: reject(STALE_TOKEN)", size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    f.append(fitbox(540, 420, 390, 62, "Сховище стану (State Store)\nhighest_token_seen: 42\nЗахищений запис: успішно зафіксовано\nЗапізнілий запис: відкинуто на бар'єрі", size=11, fill=BG, stroke=LINE))

    render(os.path.join(OUT, "fencing-epoch-architecture.svg"), W, H, "".join(f),
           title="Наскрізна архітектура взаємного виключення через токени огорожі")


if __name__ == "__main__":
    fig_fencing_race_condition()
    fig_fencing_token_validation()
    fig_fencing_epoch_architecture()
    print("Всі 3 фігури згенеровано успішно.")
