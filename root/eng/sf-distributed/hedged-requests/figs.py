# -*- coding: utf-8 -*-
"""Фігури до теми «Хеджовані запити»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / зависання / вичерпання / відхилення
COOL = "#eaf0fd"   # нейтральне / запити / клієнт
GOOD = "#e8f6ee"   # успіх / швидка відповідь / захист
ACCENT = "#fef9e7" # підсвічування / таймери / затримка


# ── 1. Часова діаграма: послідовний повтор проти відкладеного геджування ───────
def hedged_timeline():
    W, H = 1180, 640
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "СТРАТЕГІЇ БОРОТЬБИ ІЗ ЗАТРИМКОЮ: послідовний ретрай, паралельне дублювання та відкладений гедж",
                    size=13, bold=True, fill=COOL))

    # Секція 1: Звичайний послідовний ретрай за таймаутом
    f.append(rect(40, 80, 1100, 150, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(60, 105, "1. Послідовний повтор за таймаутом (Sequential Retry)", size=12, bold=True, anchor="start"))
    f.append(text(60, 125, "Чекаємо повного вичерпання таймауту (200 мс), перш ніж зробити другу спробу", size=11, color=MUTED, anchor="start"))

    # Вісь часу 1
    f.append(line(240, 185, 1060, 185, color=LINE, sw=1.5))
    f.append(circle(240, 185, 4, fill=INK, stroke=INK))
    f.append(text(240, 205, "t = 0", size=10, color=MUTED))

    # Спроба 1 (зависає на таймауті)
    f.append(rect(240, 145, 480, 30, fill=WARM, stroke=POS, sw=1.2))
    f.append(text(480, 164, "Спроба 1: зависла (чекаємо таймаут 200 мс)", size=10.5, color=POS, bold=True))
    f.append(circle(720, 185, 4, fill=POS, stroke=POS))
    f.append(text(720, 205, "t = 200 мс (Timeout)", size=10, color=POS))

    # Спроба 2 (ретрай)
    f.append(rect(720, 145, 120, 30, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text(780, 164, "Спроба 2 (15 мс)", size=10.5, color=FIELD, bold=True))
    f.append(circle(840, 185, 4, fill=FIELD, stroke=FIELD))
    f.append(text(840, 205, "t = 215 мс (Успіх)", size=10, color=FIELD, bold=True))

    f.append(fitbox(890, 140, 230, 40, "Сумарний час: 215 мс\nКористувач чекав таймаут", size=10.5, fill=WARM, stroke=POS))

    # Секція 2: Агресивне паралельне дублювання
    f.append(rect(40, 245, 1100, 155, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(60, 270, "2. Агресивне подвійне надсилання (Eager Dual-Send)", size=12, bold=True, anchor="start"))
    f.append(text(60, 290, "Надсилаємо запит одночасно на 2 репліки при кожному виклику: +100% трафіку і роботи CPU", size=11, color=MUTED, anchor="start"))

    # Вісь часу 2
    f.append(line(240, 360, 1060, 360, color=LINE, sw=1.5))
    f.append(circle(240, 360, 4, fill=INK, stroke=INK))
    f.append(text(240, 380, "t = 0", size=10, color=MUTED))

    f.append(rect(240, 310, 480, 22, fill=WARM, stroke=POS, sw=1.0))
    f.append(text(480, 325, "Репліка A: повільна (800 мс)", size=10, color=POS))

    f.append(rect(240, 335, 120, 22, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text(300, 350, "Репліка B: швидка (15 мс)", size=10, color=FIELD, bold=True))
    f.append(circle(360, 360, 4, fill=FIELD, stroke=FIELD))
    f.append(text(360, 380, "t = 15 мс (Успіх)", size=10, color=FIELD, bold=True))

    f.append(fitbox(890, 305, 230, 40, "Сумарний час: 15 мс\nАЛЕ: +100% навантаження", size=10.5, fill=WARM, stroke=POS))

    # Секція 3: Відкладений геджований запит
    f.append(rect(40, 415, 1100, 205, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(60, 440, "3. Відкладений геджований запит (Delayed Hedged Request) — ОПТИМУМ", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(60, 460, "Репліка 1 стартує в t = 0. Якщо немає відповіді до P95 (20 мс), надсилаємо Репліку 2. Хто перший — перемагає.", size=11, color=INK, anchor="start"))

    # Вісь часу 3
    f.append(line(240, 560, 1060, 560, color=LINE, sw=1.5))
    f.append(circle(240, 560, 4, fill=INK, stroke=INK))
    f.append(text(240, 580, "t = 0", size=10, color=MUTED))

    # Репліка 1 (старт t=0)
    f.append(rect(240, 480, 280, 24, fill=WARM, stroke=POS, sw=1.0))
    f.append(text(340, 496, "Репліка 1 (GC-пауза)", size=10, color=POS))

    # Пауза очікування P95 (лінія від низу блоку Репліки 1 до осі)
    f.append(line(400, 505, 400, 560, color=NEG, sw=1.4, dash="3,3"))
    f.append(circle(400, 560, 4, fill=NEG, stroke=NEG))
    f.append(text(400, 580, "t = 20 мс (P95 поріг)", size=10, color=NEG, bold=True))

    # Гедж-запит (Репліка 2)
    f.append(rect(400, 510, 120, 24, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(460, 526, "Гедж: Репліка 2 (15 мс)", size=10, color=FIELD, bold=True))

    # Фініш Репліки 2
    f.append(circle(520, 560, 4, fill=FIELD, stroke=FIELD))
    f.append(text(520, 580, "t = 35 мс (Фініш)", size=10, color=FIELD, bold=True))

    # Скасування Репліки 1
    f.append(arrow(520, 510, 520, 480, color=POS, sw=1.5))
    f.append(text(600, 496, "Cancel Репліки 1", size=9.5, color=POS, bold=True, anchor="start"))

    f.append(fitbox(770, 480, 350, 75,
                    "Сумарний час: 35 мс замість 215 мс чи 800 мс!\n"
                    "Додатковий трафік: лише ~5% (спрацьовує тільки для найповільніших 5% запитів)",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, 'hedged-timeline.svg'), W, H, *f)


# ── 2. Відсікання хвоста розподілу затримок ───────────────────────────────────
def tail_distribution_clipping():
    W, H = 1180, 580
    f = []

    # Заголовок
    f.append(fitbox(40, 20, 1100, 44,
                    "РОЗПОДІЛ ЗАТРИМОК: як геджування відсікає довгий хвіст (P99 та P99.9)",
                    size=13, bold=True, fill=COOL))

    # Ліва панель: Базовий розподіл із довгим хвостом
    f.append(rect(40, 80, 530, 460, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(305, 110, "Без геджування: важкий хвіст викидів", size=13, bold=True, color=POS))

    # Осі графіка зліва
    f.append(line(90, 450, 530, 450, color=LINE, sw=1.5))
    f.append(line(90, 450, 90, 160, color=LINE, sw=1.5))
    f.append(text(520, 470, "Час (мс)", size=10, color=MUTED, anchor="end"))
    f.append(text(85, 150, "Щільність f(t)", size=10, color=MUTED, anchor="start"))

    # Крива зліва (дзвін P50 + довгий хвіст)
    path_raw = (
        "M 90 450 "
        "C 120 440, 130 200, 160 200 "
        "C 190 200, 210 390, 260 410 "
        "C 320 430, 420 440, 520 448"
    )
    f.append(f'<path d="{path_raw}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначки перцентилів зліва
    f.append(line(160, 200, 160, 450, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(160, 468, "P50\n(10 мс)", size=9.5, anchor="middle"))

    f.append(line(260, 410, 260, 450, color=NEG, sw=1.0, dash="3,3"))
    f.append(text(260, 468, "P95\n(25 мс)", size=9.5, anchor="middle", color=NEG))

    f.append(line(380, 435, 380, 450, color=POS, sw=1.2, dash="3,3"))
    f.append(text(380, 468, "P99\n(120 мс)", size=9.5, anchor="middle", color=POS))

    f.append(line(480, 445, 480, 450, color=POS, sw=1.2, dash="3,3"))
    f.append(text(480, 468, "P99.9\n(500 мс)", size=9.5, anchor="middle", color=POS))

    # Виділення хвоста
    f.append(fitbox(310, 240, 230, 70,
                    "ВАЖКИЙ ХВІСТ:\nGC-паузи, дискові черги,\nконкуренція потоків CPU,\nвтрати TCP-пакетів",
                    size=10.5, fill=WARM, stroke=POS))

    # Права панель: З геджуванням на порозі P95
    f.append(rect(610, 80, 530, 460, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(875, 110, "З геджуванням (поріг t_h = P95): хвіст зрізано", size=13, bold=True, color=FIELD))

    # Осі графіка справа
    f.append(line(660, 450, 1100, 450, color=LINE, sw=1.5))
    f.append(line(660, 450, 660, 160, color=LINE, sw=1.5))
    f.append(text(1090, 470, "Час (мс)", size=10, color=MUTED, anchor="end"))
    f.append(text(655, 150, "Щільність f_H(t)", size=10, color=MUTED, anchor="start"))

    # Крива справа (дзвін P50 + другий менший сплеск від геджу біля P95 + P50, хвіст після 50 мс нульовий)
    path_hedged = (
        "M 660 450 "
        "C 690 440, 700 200, 730 200 "
        "C 760 200, 780 400, 820 415 "
        "C 840 400, 860 380, 880 420 "
        "C 900 445, 950 450, 1090 450"
    )
    f.append(f'<path d="{path_hedged}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Позначки справа
    f.append(line(730, 200, 730, 450, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(730, 468, "P50\n(10 мс)", size=9.5, anchor="middle"))

    f.append(line(830, 415, 830, 450, color=NEG, sw=1.2, dash="3,3"))
    f.append(text(830, 468, "Поріг t_h\n(25 мс)", size=9.5, anchor="middle", color=NEG))

    f.append(line(880, 420, 880, 450, color=FIELD, sw=1.4, dash="3,3"))
    f.append(text(880, 468, "Новий P99\n(35 мс)", size=9.5, anchor="middle", color=FIELD, bold=True))

    f.append(line(930, 448, 930, 450, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text(930, 468, "P99.9\n(50 мс)", size=9.5, anchor="middle", color=FIELD))

    f.append(fitbox(880, 240, 230, 70,
                    "ЕФЕКТ ЗРІЗАННЯ:\nГедж на 25-й мс виконується\nза типові 10 мс. P99 стає\n25 + 10 = 35 мс замість 120 мс!",
                    size=10.5, fill="#ffffff", stroke=FIELD, sw=1.2))

    render(os.path.join(OUT, 'tail-distribution-clipping.svg'), W, H, *f)


# ── 3. Петля ампліфікації: небезпека геджування без лімітів ───────────────────
def hedged_amplification_loop():
    W, H = 1180, 600
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "ПЕТЛЯ МЕТАСТАБІЛЬНОЇ ВІДМОВИ: як неконтрольоване геджування перетворює легке перевантаження на колапс",
                    size=13, bold=True, fill=WARM, stroke=POS))

    # Блок 1: Початковий сплеск / уповільнення
    f.append(textbox(240, 160, "1. Початкове сповільнення сервісу\n(база на 80% CPU або мережевий дрижак)\nЗатримка P50 зростає з 10 мс до 30 мс",
                     size=11.5, pad=12, fill=FILL, stroke=LINE)[0])

    # Стрілка 1 -> 2
    f.append(arrow(410, 160, 520, 160, color=POS, sw=2.0))
    f.append(text(465, 148, "t > t_h (25 мс)", size=10, color=POS, bold=True))

    # Блок 2: Спрацьовування геджу
    f.append(textbox(690, 160, "2. Масовий запуск гедж-запитів\nЗамість 5% запитів поріг перевищують 80%!\nКлієнти починають масово дублювати RPC",
                     size=11.5, pad=12, fill=WARM, stroke=POS)[0])

    # Стрілка 2 -> 3
    f.append(arrow(690, 215, 690, 310, color=POS, sw=2.0))
    f.append(text(760, 260, "+80% нового трафіку", size=10, color=POS, bold=True))

    # Блок 3: Перевантаження бекенду
    f.append(textbox(690, 370, "3. Ампліфікація навантаження бекенду\nЧерги задач зростають, потоки вичерпуються.\nСервери витрачають CPU на виконання дублів",
                     size=11.5, pad=12, fill=WARM, stroke=POS)[0])

    # Стрілка 3 -> 4
    f.append(arrow(520, 370, 410, 370, color=POS, sw=2.0))
    f.append(text(465, 358, "Черги ростуть", size=10, color=POS, bold=True))

    # Блок 4: Ескалація затримок
    f.append(textbox(240, 370, "4. Затримка злітає до секунд\nТепер 100% запитів перевищують поріг t_h!\nКожен запит надсилає по 2-3 дублі",
                     size=11.5, pad=12, fill=WARM, stroke=POS, sw=2.0)[0])

    # Стрілка зворотної петлі: 4 -> 1
    f.append(arrow(240, 310, 240, 215, color=POS, sw=2.5))
    f.append(text(150, 260, "ПЕТЛЯ ЗАКРИЛАСЯ\n(Повний колапс)", size=10.5, color=POS, bold=True))

    # Нижній пояснювальний блок
    f.append(fitbox(40, 480, 1100, 90,
                    "ЗАХИСТ: геджування КАТЕГОРИЧНО заборонено вмикати без бюджету токенів (Token Bucket) та вимикача (Circuit Breaker).\n"
                    "Якщо частка гедж-запитів досягає встановленого ліміту (наприклад, 10% від вхідного потоку),\n"
                    "клієнт припиняє надсилати дублі й чекає природної відповіді першої спроби.",
                    size=12, fill=GOOD, stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, 'hedged-amplification-loop.svg'), W, H, *f)


# ── 4. Бюджет токенів для безпечного геджування ───────────────────────────────
def token_bucket_hedge_budget():
    W, H = 1180, 540
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "ЗАХИСНИЙ МЕХАНІЗМ: бюджет токенів (Token Bucket) обмежує частку геджування до 10%",
                    size=13, bold=True, fill=COOL))

    # Ліва частина: Вхідний потік
    f.append(rect(40, 90, 260, 410, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(170, 120, "Вхідний потік запитів", size=13, bold=True))
    f.append(text(170, 140, "100 запитів / сек", size=11, color=MUTED))

    for i in range(4):
        y = 175 + i * 75
        f.append(rect(55, y, 230, 45, fill=COOL, stroke=NEG, sw=1.2))
        f.append(text(170, y + 27, f"Запит #{i+1} (Основний)", size=11, color=NEG, bold=True))

    # Стрілка наповнення токенів
    f.append(arrow(300, 200, 420, 200, color=FIELD, sw=1.8))
    f.append(text(360, 185, "+0.1 токена за кожен\nосновний успішний запит", size=9.5, color=FIELD, bold=True))

    # Центральна частина: Відро токенів
    f.append(rect(430, 90, 320, 410, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(590, 120, "Бюджет токенів (Token Bucket)", size=13, bold=True, color=FIELD))
    f.append(text(590, 140, "Максимум токенів: 10 (квота 10%)", size=11, color=MUTED))

    # Відро
    f.append(rect(470, 170, 240, 240, fill="#ffffff", stroke=FIELD, sw=2.0, rx=10))
    f.append(text(590, 200, "Вміст відра:", size=11, color=MUTED))

    # Токени всередині
    for idx, (tx, ty) in enumerate([(520, 240), (590, 240), (660, 240), (555, 300), (625, 300)]):
        f.append(circle(tx, ty, 20, fill=ACCENT, stroke=LINE, sw=1.2))
        f.append(text(tx, ty + 5, "1 Т", size=11, bold=True))

    f.append(text(590, 360, "Наявні токени дозволяють\nзапустити гедж негайно", size=10.5, color=FIELD, bold=True))

    # Права частина: Рішення про запуск геджу
    f.append(rect(790, 90, 350, 410, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(965, 120, "Перевірка перед геджем", size=13, bold=True))
    f.append(text(965, 140, "Минуло t_h = 25 мс без відповіді", size=11, color=MUTED))

    # Гілка 1: Токен є -> Пускаємо гедж
    f.append(rect(810, 175, 310, 130, fill=GOOD, stroke=FIELD, sw=1.4))
    f.append(text(965, 205, "Сценарій А: Токен є в наявності", size=11.5, bold=True, color=FIELD))
    f.append(text(965, 230, "1. Списуємо 1 токен з відра\n2. Відправляємо Репліку 2 (гедж)\n3. Хвіст затримки успішно зрізано!", size=10.5))

    # Гілка 2: Токенів нема -> Заборона
    f.append(rect(810, 335, 310, 140, fill=WARM, stroke=POS, sw=1.4))
    f.append(text(965, 365, "Сценарій Б: Відро порожнє (ліміт)", size=11.5, bold=True, color=POS))
    f.append(text(965, 395, "1. Гедж ЗАБЛОКОВАНО\n2. Чекаємо відповіді Репліки 1\n3. Захист кластера від перевантаження!", size=10.5, color=POS))

    # Стрілки від відра до сценаріїв
    f.append(arrow(750, 240, 810, 240, color=FIELD, sw=1.6))
    f.append(arrow(750, 400, 810, 400, color=POS, sw=1.6))

    render(os.path.join(OUT, 'token-bucket-hedge-budget.svg'), W, H, *f)


if __name__ == "__main__":
    hedged_timeline()
    tail_distribution_clipping()
    hedged_amplification_loop()
    token_bucket_hedge_budget()
    print("Всі 4 фігури згенеровано успішно.")
