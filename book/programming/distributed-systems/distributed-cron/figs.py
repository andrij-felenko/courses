# -*- coding: utf-8 -*-
"""Фігури до теми «Розподілений cron»."""
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


# ── 1. Три режими відмови наївного cron у кластері ───────────────────────────
def fig_cron_failure_modes():
    W, H = 1060, 420
    f = []

    # Колонка 1: Єдина точка відмови (SPOF)
    x1, y1, w_col, h_col = 30.0, 40.0, 310.0, 350.0
    f.append(rect(x1, y1, w_col, h_col, fill=FILL, stroke=LINE, sw=1.2))
    f.append(fitbox(x1 + 10, y1 + 10, w_col - 20, 40, "1. Єдиний сервер із crond\n(Single Point of Failure)", size=12, bold=True, fill=COOL))
    f.append(fitbox(x1 + 20, y1 + 65, w_col - 40, 50, "Сервер А: виконує crond\n(розклад 00:00 UTC)", size=11, fill="#ffffff"))
    f.append(arrow(x1 + w_col/2, y1 + 120, x1 + w_col/2, y1 + 155, color=POS))
    f.append(fitbox(x1 + 20, y1 + 160, w_col - 40, 55, "АВАРІЯ СЕРВЕРА А\n(Kernel panic / OOM о 23:50)", size=11, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(arrow(x1 + w_col/2, y1 + 220, x1 + w_col/2, y1 + 255, color=POS))
    f.append(fitbox(x1 + 20, y1 + 260, w_col - 40, 75, "НАСЛІДОК: Повний пропуск\nЗадачі 00:00 не запущені.\nБекапи та білінг мовчки втрачені,\nнемає кому підхопити роботу.", size=10.5, color=POS, fill=WARM, stroke=POS))

    # Колонка 2: Дублювання запуску на репліках
    x2 = 375.0
    f.append(rect(x2, y1, w_col, h_col, fill=FILL, stroke=LINE, sw=1.2))
    f.append(fitbox(x2 + 10, y1 + 10, w_col - 20, 40, "2. Неузгоджені репліки\n(Шторм дублікатів)", size=12, bold=True, fill=COOL))
    f.append(fitbox(x2 + 15, y1 + 65, 85, 45, "Под 1\ncrond", size=10, fill="#ffffff"))
    f.append(fitbox(x2 + 110, y1 + 65, 90, 45, "Под 2\ncrond", size=10, fill="#ffffff"))
    f.append(fitbox(x2 + 210, y1 + 65, 85, 45, "Под N\ncrond", size=10, fill="#ffffff"))
    f.append(arrow(x2 + w_col/2, y1 + 120, x2 + w_col/2, y1 + 155, color=POS))
    f.append(fitbox(x2 + 20, y1 + 160, w_col - 40, 55, "ОДНОЧАСНИЙ СТАРТ О 00:00\nУсі N подів одночасно\nзапускають ту саму задачу", size=11, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(arrow(x2 + w_col/2, y1 + 220, x2 + w_col/2, y1 + 255, color=POS))
    f.append(fitbox(x2 + 20, y1 + 260, w_col - 40, 75, "НАСЛІДОК: Руйнування даних\nN-кратне списання коштів,\nперевантаження бази блокуваннями,\nстан гонитви у сховищі.", size=10.5, color=POS, fill=WARM, stroke=POS))

    # Колонка 3: Дрейф годинника та паузи процесу
    x3 = 720.0
    f.append(rect(x3, y1, w_col, h_col, fill=FILL, stroke=LINE, sw=1.2))
    f.append(fitbox(x3 + 10, y1 + 10, w_col - 20, 40, "3. Дрейф часу та GC-паузи\n(Невидимі зсуви вікна)", size=12, bold=True, fill=COOL))
    f.append(fitbox(x3 + 20, y1 + 65, w_col - 40, 50, "sleep(60) у циклі планувальника\n(розрахунок на точний час)", size=11, fill="#ffffff"))
    f.append(arrow(x3 + w_col/2, y1 + 120, x3 + w_col/2, y1 + 155, color=POS))
    f.append(fitbox(x3 + 20, y1 + 160, w_col - 40, 55, "ЗСУВ NTP АБО ПАУЗА GC\nСтрибок годинника на 65 с або\nзависання VM у свопі", size=11, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(arrow(x3 + w_col/2, y1 + 220, x3 + w_col/2, y1 + 255, color=POS))
    f.append(fitbox(x3 + 20, y1 + 260, w_col - 40, 75, "НАСЛІДОК: Втрата вікна запуску\nПеревірка `min == 0` пропускається.\nЗадача чекає наступної доби\nабо запускається із запізненням.", size=10.5, color=POS, fill=WARM, stroke=POS))

    render(os.path.join(OUT, "cron-failure-modes.svg"), W, H, *f)


# ── 2. Архітектура розподіленого планувальника ───────────────────────────────
def fig_sharded_time_wheel():
    W, H = 1060, 480
    f = []

    # Рівень 1: Вхідні задачі та Шардинг
    f.append(fitbox(40, 30, 240, 50, "Реєстр періодичних задач\n(Job Definition Store)", size=12, bold=True, fill=COOL))
    f.append(arrow(280, 55, 360, 55, color=LINE))
    f.append(text(320, 45, "Hash(JobID)", size=10, color=MUTED))

    # Консистентне кільце
    f.append(rect(360, 20, 330, 80, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(525, 42, "Консистентне кільце розподілу (Hash Ring)", size=11.5, bold=True))
    f.append(fitbox(375, 52, 90, 38, "Шард 0..31\nВузол 1", size=10, fill=GOOD))
    f.append(fitbox(480, 52, 90, 38, "Шард 32..63\nВузол 2", size=10, fill=GOOD))
    f.append(fitbox(585, 52, 90, 38, "Шард 64..95\nВузол 3", size=10, fill=GOOD))

    # Координатор консенсусу
    f.append(fitbox(750, 30, 270, 60, "Координатор кластера (etcd / Raft)\nОренда ліз на володіння шардами\nта виявлення відмов планувальників", size=10.5, fill=WARN, stroke=LINE))
    f.append(arrow(690, 55, 750, 55, color=MUTED))

    # Стрілка вниз до Площини Управління (Планувальників)
    f.append(arrow(525, 100, 525, 140, color=LINE))
    f.append(text(525, 125, "Призначення шарду з лізою володіння", size=10, color=MUTED))

    # Рівень 2: Площина Управління (Планувальник із Часовим Колесом)
    f.append(rect(40, 140, 980, 150, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(530, 162, "ПЛОЩИНА УПРАВЛІННЯ: Вузол планувальника (Control Plane / Scheduler Instance)", size=12, bold=True))

    # Блоки всередині планувальника
    f.append(fitbox(60, 175, 230, 100, "Журнал стану шарду (WAL)\nЗбереження точок запуску\nта розрахунок next_run_utc\n(надійний стан на диску)", size=10.5, fill=COOL))
    f.append(arrow(290, 225, 340, 225, color=LINE))

    f.append(fitbox(340, 175, 380, 100, "Ієрархічне Часове Колесо (Timing Wheel)\nO(1) додавання таймерів та O(1) перехід по такті\nКолесо секунд (0..59) → Колесо хвилин (0..59) → Днів\nСпрацьовує по монотонному тіку таймера", size=10.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(720, 225, 770, 225, color=LINE))

    f.append(fitbox(770, 175, 230, 100, "Генератор тригерів (Dispatcher)\nДодає Monotonic Fencing Epoch\nта формує подію виконання\n(Trigger Event)", size=10.5, fill=COOL))

    # Стрілка вниз до Черги повідомлень
    f.append(arrow(530, 290, 530, 330, color=LINE))
    f.append(text(530, 315, "Асинхронний диспатч тригерів (Idempotency Key = JobID + SlotUTC)", size=10, color=MUTED))

    # Рівень 3: Надійна Черга Повідомлень
    f.append(rect(40, 330, 980, 45, fill=COOL, stroke=LINE, sw=1.2))
    f.append(text(530, 357, "Шина задач / Розподілена черга (Message Broker: Kafka / RabbitMQ / SQS)", size=11.5, bold=True))

    # Стрілки вниз до Воркерів
    f.append(arrow(200, 375, 200, 410, color=LINE))
    f.append(arrow(530, 375, 530, 410, color=LINE))
    f.append(arrow(860, 375, 860, 410, color=LINE))

    # Рівень 4: Площина Даних (Воркери-Виконавці)
    f.append(fitbox(60, 410, 280, 55, "Воркер 1 (Data Plane)\nПеревірка Fencing Token >= MaxSeen\nта виконання бізнес-коду", size=10.5, fill=GOOD))
    f.append(fitbox(390, 410, 280, 55, "Воркер 2 (Data Plane)\nІдемпотентний запис у БД\nта підтвердження (ACK) у чергу", size=10.5, fill=GOOD))
    f.append(fitbox(720, 410, 280, 55, "Воркер K (Data Plane)\nОбробка повторів (Retries)\nта звіт про завершення", size=10.5, fill=GOOD))

    render(os.path.join(OUT, "sharded-time-wheel-architecture.svg"), W, H, *f)


# ── 3. Шкала часу лізи, огорожі та політики пропусків (Misfire) ─────────────
def fig_fencing_and_misfire():
    W, H = 1060, 490
    f = []

    # Верхня секція: Токени огорожі при зміні лідера
    f.append(rect(30, 20, 1000, 220, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(530, 42, "Часова шкала: Зміна планувальника, лізи та захист токеном огорожі (Fencing Token)", size=12, bold=True))

    # Вісь часу
    f.append(line(70, 120, 990, 120, color=LINE, sw=1.5))
    f.append(arrow(980, 120, 1000, 120, color=LINE))
    f.append(text(990, 140, "Час t", size=10, color=MUTED))

    # Подія 1: Планувальник 1 утримує лізу
    f.append(fitbox(80, 60, 220, 45, "Планувальник 1\nЛіза чинна (Epoch = 41)", size=10.5, fill=GOOD))
    f.append(line(190, 105, 190, 135, color=LINE, sw=1.2))
    f.append(circle(190, 120, 4, fill=FIELD))
    f.append(text(190, 145, "t=0: Диспатч (Epoch=41)", size=10))

    # Подія 2: GC-пауза Планувальника 1
    f.append(fitbox(330, 60, 200, 45, "GC-ПАУЗА Планувальника 1\n(процес зависає на 20 с)", size=10.5, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(line(430, 105, 430, 135, color=POS, sw=1.2))
    f.append(circle(430, 120, 4, fill=POS))
    f.append(text(430, 145, "t=10: Спливання лізи TTL", size=10, color=POS))

    # Подія 3: Планувальник 2 перехоплює шард
    f.append(fitbox(560, 60, 220, 45, "Планувальник 2 бере шард\nНова ліза (Epoch = 42)", size=10.5, fill=GOOD))
    f.append(line(670, 105, 670, 135, color=LINE, sw=1.2))
    f.append(circle(670, 120, 4, fill=FIELD))
    f.append(text(670, 145, "t=12: Диспатч (Epoch=42)", size=10))

    # Подія 4: Запізнілий пакет від Планувальника 1 відхилено
    f.append(fitbox(800, 60, 190, 45, "Запізнілий тригер Epoch=41\nВІДХИЛЕНО воркером!", size=10.5, bold=True, color=POS, fill=WARM, stroke=POS))
    f.append(line(895, 105, 895, 135, color=POS, sw=1.2))
    f.append(circle(895, 120, 4, fill=POS))
    f.append(text(895, 145, "t=22: Відхилено (41 < 42)", size=10, color=POS))

    # Пояснення під шкалою
    f.append(fitbox(80, 170, 900, 55, "Правило огорожі: Воркер фіксує найвищу епоху MaxSeen=42. Коли запізнілий сигнал від зомбі-планувальника 1\nз епохою 41 прибуває до системи, він безумовно відкидається, запобігаючи повторному запуску задачі.", size=10.5, fill=FILL))

    # Нижня секція: Політики пропусків (Misfire Policies)
    f.append(rect(30, 255, 1000, 215, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(530, 275, "Політики обробки пропущених запусків (Misfire Policies) після відновлення від збою", size=12, bold=True))

    # Вікно збою
    f.append(fitbox(60, 300, 240, 45, "Вікно простою системи (Outage)\nПропущено точки: 02:00, 02:15, 02:30", size=10, fill=WARM, stroke=POS))

    # Політика 1: Catch-Up (Fire All)
    f.append(fitbox(330, 300, 670, 45, "1. FireAndProceed (Catch-Up / Наздогнати всі):\nПослідовно запускає всі 3 пропущені ітерації (02:00, 02:15, 02:30). Обов'язково для фінансового білінгу та агрегації.", size=10, fill=GOOD))

    # Політика 2: Fire Once Now
    f.append(fitbox(330, 355, 670, 45, "2. FireOnceNow (Запустити один раз зараз):\nІгнорує кількість пропусків і запускає рівно 1 наздоганяючу ітерацію, далі за розкладом. Для прогріву кешу та синхронізації.", size=10, fill=COOL))

    # Політика 3: Skip / Ignore
    f.append(fitbox(330, 410, 670, 45, "3. IgnoreMisfires / Skip (Пропустити всі втрачені):\nСкидає всі пропущені запуски і чекає наступного штатного слота (02:45). Для збору телеметрії та живих сповіщень.", size=10, fill=FILL))

    render(os.path.join(OUT, "fencing-and-misfire-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cron_failure_modes()
    fig_sharded_time_wheel()
    fig_fencing_and_misfire()
    print("All figures generated successfully.")
