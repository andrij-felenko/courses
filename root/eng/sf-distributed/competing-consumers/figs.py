# -*- coding: utf-8 -*-
"""Фігури до теми «Конкурентні споживачі: паралельна обробка, балансування, лізи та відмови»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / втрата / аварія
COOL = "#eaf0fd"   # нейтральне пояснення / структура
GOOD = "#e8f6ee"   # успіх / надійність
WARN = "#fef9e7"   # застереження / черга / очікування


# ── 1. Архітектура патерну конкуруючих споживачів ─────────────────────────────
def competing_consumers_architecture():
    W, H = 1120, 480
    f = []

    # Тло для брокера
    f.append(rect(310, 30, 440, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(530, 60, "Брокер повідомлень (Message Broker)", size=14, bold=True, color="#334155"))

    # Продюсери ліворуч
    f.append(fitbox(30, 110, 190, 60, "Продюсер A\n(HTTP API / Web)", size=12, bold=True, fill=COOL))
    f.append(fitbox(30, 240, 190, 60, "Продюсер B\n(Background Job)", size=12, bold=True, fill=COOL))

    # Стрілки від продюсерів до черги
    f.append(arrow(220, 140, 340, 180, color=LINE, sw=1.6))
    f.append(text(280, 150, "Publish", size=11, color=MUTED, bold=True))
    f.append(arrow(220, 270, 340, 220, color=LINE, sw=1.6))
    f.append(text(280, 255, "Publish", size=11, color=MUTED, bold=True))

    # Спільна черга всередині брокера
    f.append(rect(340, 110, 380, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(530, 135, "Спільна черга (Shared Queue / Channel)", size=13, bold=True, color=INK))

    # Елементи повідомлень у черзі
    msgs = [("M5", 360), ("M4", 420), ("M3", 480), ("M2", 540), ("M1", 600)]
    for label, mx in msgs:
        f.append(rect(mx, 155, 50, 40, fill=WARN, stroke=LINE, sw=1.3, rx=4))
        f.append(text(mx + 25, 180, label, size=12, bold=True, color=INK))
    f.append(arrow(660, 175, 700, 175, color=FIELD, sw=1.8))
    f.append(text(530, 215, "← Буфер FIFO (готова до видачі черга) ←", size=11, color=MUTED, italic=True))
    f.append(text(530, 245, "Диспетчер брокера: роздає повідомлення рівно одному воркеру", size=11, color=INK))

    # Мертва черга (DLQ) всередині брокера
    f.append(rect(340, 320, 380, 105, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(530, 345, "Мертва черга (Dead Letter Queue — DLQ)", size=12, bold=True, color=POS))
    f.append(fitbox(360, 360, 340, 48, "Отруйні повідомлення (перевищено ліміт спроб)\nЗбереження для ручного аудиту й виправлення", size=11, fill="#ffe3e3", stroke=POS))

    # Споживачі (воркери) праворуч
    workers = [
        (830, 70, "Воркер 1 (Інстанс A)\n[Обробка M1] ⚡", GOOD, FIELD),
        (830, 180, "Воркер 2 (Інстанс B)\n[Обробка M2] ⚡", GOOD, FIELD),
        (830, 290, "Воркер 3 (Інстанс C)\n[Вільний / Очікує]", COOL, LINE),
    ]

    for wx, wy, wtext, wfill, wstroke in workers:
        f.append(fitbox(wx, wy, 240, 60, wtext, size=12, bold=True, fill=wfill, stroke=wstroke))

    # Роздача повідомлень
    f.append(arrow(720, 160, 830, 100, color=FIELD, sw=1.6))
    f.append(text(780, 120, "M1", size=11, color=FIELD, bold=True))

    f.append(arrow(720, 180, 830, 210, color=FIELD, sw=1.6))
    f.append(text(780, 185, "M2", size=11, color=FIELD, bold=True))

    # Зворотний зв'язок: ACK / NACK
    f.append(arrow(830, 120, 720, 140, color=FIELD, sw=1.4))
    f.append(text(775, 148, "ACK (успіх)", size=10, color=FIELD, bold=True))

    f.append(arrow(830, 230, 720, 350, color=POS, sw=1.4))
    f.append(text(790, 275, "NACK → DLQ", size=10, color=POS, bold=True))

    # Підсумок унизу
    f.append(fitbox(30, 440, 1060, 35,
                    "Патерн Competing Consumers: спільна черга дозволяє горизонтально масштабувати пул воркерів без зміни продюсерів.",
                    size=12, fill=WARN, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'competing-consumers-architecture.svg'), W, H, *f)


# ── 2. Point-to-Point черга проти логів із партиціями (Kafka) ─────────────────
def point_to_point_vs_partitioned():
    W, H = 1140, 500
    f = []

    # Ліва колонка: Point-to-Point (RabbitMQ / SQS)
    f.append(rect(30, 30, 520, 420, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(290, 60, "1. Point-to-Point Queue (RabbitMQ / AWS SQS)", size=13, bold=True, color=INK))

    # Черга ліворуч
    f.append(rect(60, 90, 460, 80, fill=COOL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(290, 115, "Єдина спільна черга (Shared Queue)", size=12, bold=True))
    for i, (m, mx) in enumerate([("M4", 120), ("M3", 190), ("M2", 260), ("M1", 330), ("M0", 400)]):
        f.append(rect(mx, 125, 50, 32, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(mx + 25, 146, m, size=11, bold=True))

    # Воркери під чергою
    w_p2p = [
        (60, 200, "Воркер 1\n(Швидкий)", GOOD),
        (180, 200, "Воркер 2\n(Повільний)", WARN),
        (300, 200, "Воркер 3\n(Швидкий)", GOOD),
        (420, 200, "Воркер 4\n(Новий)", GOOD),
    ]
    for wx, wy, wt, wf in w_p2p:
        f.append(fitbox(wx, wy, 100, 60, wt, size=11, bold=True, fill=wf))

    f.append(arrow(220, 170, 110, 200, color=LINE, sw=1.3))
    f.append(arrow(270, 170, 230, 200, color=LINE, sw=1.3))
    f.append(arrow(320, 170, 350, 200, color=LINE, sw=1.3))
    f.append(arrow(370, 170, 470, 200, color=LINE, sw=1.3))

    f.append(fitbox(50, 280, 480, 150,
                    "Властивості Point-to-Point моделі:\n"
                    "• Одиниця роздачі — Окреме повідомлення.\n"
                    "• Балансування — Динамічне: швидкі воркери забирають більше задач.\n"
                    "• Масштабування — Необмежене: додавання 5-го воркера миттєво піднімає throughput.\n"
                    "• Порядок — Строгий FIFO руйнується при паралельній обробці.\n"
                    "• Ціна — Витрати брокера на стан кожного In-Flight повідомлення.",
                    size=11, fill="#f8fafc", stroke="#cbd5e1"))

    # Права колонка: Partitioned Log (Kafka / Pulsar)
    f.append(rect(590, 30, 520, 420, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(850, 60, "2. Partitioned Log (Apache Kafka / Pulsar)", size=13, bold=True, color=INK))

    # Партиції
    parts = [
        ("Партиція 0 [M0, M3, M6]", 700, 95, GOOD),
        ("Партиція 1 [M1, M4, M7]", 700, 130, GOOD),
        ("Партиція 2 [M2, M5, M8]", 700, 165, GOOD),
    ]
    for pt, px, py, pf in parts:
        f.append(fitbox(620, py, 230, 28, pt, size=10, bold=True, fill=COOL))

    # Воркери Consumer Group
    w_kafka = [
        (900, 95, "Споживач 1 (P0)", GOOD),
        (900, 130, "Споживач 2 (P1)", GOOD),
        (900, 165, "Споживач 3 (P2)", GOOD),
        (900, 205, "Споживач 4 (IDLE!)", WARM),
    ]
    for wx, wy, wt, wf in w_kafka:
        f.append(fitbox(wx, wy, 180, 28, wt, size=10, bold=True, fill=wf))

    f.append(arrow(850, 109, 900, 109, color=LINE, sw=1.3))
    f.append(arrow(850, 144, 900, 144, color=LINE, sw=1.3))
    f.append(arrow(850, 179, 900, 179, color=LINE, sw=1.3))
    f.append(line(850, 219, 890, 219, color=POS, sw=1.3, dash="3,3"))
    f.append(text(870, 214, "✖", size=12, color=POS, bold=True))

    f.append(fitbox(610, 280, 480, 150,
                    "Властивості Partitioned Log моделі:\n"
                    "• Одиниця роздачі — Ціла партиція (Partition).\n"
                    "• Стеля масштабування — Max воркерів = Кількість партицій (4-й воркер простоює).\n"
                    "• Балансування — Статичне: важка партиція перевантажує одного споживача.\n"
                    "• Порядок — Строгий порядок у межах кожного ключа/партиції.\n"
                    "• Ціна — Мінімальна: брокер зберігає лише числовий offset консюмер-групи.",
                    size=11, fill="#f8fafc", stroke="#cbd5e1"))

    # Підсумок
    f.append(fitbox(30, 460, 1080, 30,
                    "Ключова різниця: черга конкуруючих споживачів розподіляє окремі задачі (дрібне зерно), а журнал партицій — цілі потоки даних.",
                    size=11, fill=WARN, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'point-to-point-vs-partitioned.svg'), W, H, *f)


# ── 3. Таймаут видимості та гонитва оренди (Visibility Timeout Race) ─────────
def visibility_timeout_race():
    W, H = 1120, 490
    f = []

    # Три сценарії часової шкали
    scenarios = [
        (30, "Сценарій 1: Штатне завершення (Успішний ACK)", 65),
        (30, "Сценарій 2: Аварія воркера і повторна видача за таймаутом", 195),
        (30, "Сценарій 3: Задовга обробка без продовження лізи (Подвійна обробка!)", 325),
    ]

    for sx, title, sy in scenarios:
        f.append(rect(sx, sy, 1060, 115, fill="#ffffff", stroke=LINE, sw=1.3, rx=6))
        f.append(text(sx + 20, sy + 22, title, size=12, bold=True, anchor="start", color=INK))
        # Вісь часу
        f.append(line(sx + 40, sy + 75, sx + 1020, sy + 75, color=MUTED, sw=1.2))
        f.append(arrow(sx + 1010, sy + 75, sx + 1030, sy + 75, color=MUTED, sw=1.2))
        f.append(text(sx + 1040, sy + 78, "Час (t)", size=10, color=MUTED, italic=True))

    # Сценарій 1 деталі
    s1_y = 65
    f.append(fitbox(50, s1_y + 45, 140, 24, "Отримано (t=0)", size=10, bold=True, fill=COOL))
    f.append(rect(200, s1_y + 40, 260, 14, fill="#e0e7ff", stroke=LINE, sw=1))
    f.append(text(330, s1_y + 51, "Таймаут видимості (30 с)", size=9, bold=True))
    f.append(rect(200, s1_y + 60, 130, 14, fill=GOOD, stroke=FIELD, sw=1))
    f.append(text(265, s1_y + 71, "Обробка (12 с)", size=9, color=FIELD, bold=True))
    f.append(fitbox(340, s1_y + 82, 110, 24, "ACK (t=12 с)", size=10, bold=True, fill=GOOD))
    f.append(text(650, s1_y + 60, "✔ Повідомлення видалено з черги. Безпечно й чисто.", size=11, color=FIELD, bold=True))

    # Сценарій 2 деталі
    s2_y = 195
    f.append(fitbox(50, s2_y + 45, 140, 24, "Отримано Воркером 1", size=10, bold=True, fill=COOL))
    f.append(rect(200, s2_y + 40, 260, 14, fill="#e0e7ff", stroke=LINE, sw=1))
    f.append(text(330, s2_y + 51, "Таймаут видимості (30 с)", size=9, bold=True))
    f.append(rect(200, s2_y + 60, 80, 14, fill=WARM, stroke=POS, sw=1))
    f.append(text(240, s2_y + 71, "Збій (t=8 с) ⚡", size=9, color=POS, bold=True))
    f.append(line(460, s2_y + 35, 460, s2_y + 85, color=POS, sw=1.5, dash="3,3"))
    f.append(text(460, s2_y + 102, "t=30 с: ліза минула", size=9, color=POS, bold=True))
    f.append(fitbox(480, s2_y + 45, 160, 24, "Видача Воркеру 2 (t=30 с)", size=10, bold=True, fill=WARN))
    f.append(rect(650, s2_y + 60, 110, 14, fill=GOOD, stroke=FIELD, sw=1))
    f.append(text(705, s2_y + 71, "Обробка (10 с)", size=9, color=FIELD, bold=True))
    f.append(fitbox(770, s2_y + 45, 100, 24, "ACK (t=40 с)", size=10, bold=True, fill=GOOD))

    # Сценарій 3 деталі
    s3_y = 325
    f.append(fitbox(50, s3_y + 45, 140, 24, "Воркер 1: Старт", size=10, bold=True, fill=COOL))
    f.append(rect(200, s3_y + 40, 260, 14, fill="#e0e7ff", stroke=LINE, sw=1))
    f.append(text(330, s3_y + 51, "Таймаут видимості (30 с)", size=9, bold=True))
    f.append(rect(200, s3_y + 60, 360, 14, fill=WARN, stroke=LINE, sw=1))
    f.append(text(380, s3_y + 71, "Довга обробка Воркера 1 (триває 45 с)", size=9, bold=True))
    f.append(line(460, s3_y + 30, 460, s3_y + 85, color=POS, sw=1.8, dash="3,3"))
    f.append(text(460, s3_y + 25, "Таймаут минув! Повідомлення знову видиме", size=9, color=POS, bold=True))
    f.append(fitbox(480, s3_y + 82, 170, 24, "Воркер 2: Забирає задачу!", size=9, bold=True, fill=WARM))
    f.append(rect(660, s3_y + 60, 130, 14, fill=WARM, stroke=POS, sw=1))
    f.append(text(725, s3_y + 71, "Воркер 2 обробляє", size=9, color=POS, bold=True))
    f.append(fitbox(810, s3_y + 45, 200, 44, "ПОДВІЙНА ОБРОБКА!\n(Потрібен Heartbeat / Lease Renew)", size=9, bold=True, fill=WARM, stroke=POS))

    # Підсумок
    f.append(fitbox(30, 450, 1060, 32,
                    "Лізинг вимагає продовження оренди (Heartbeat / ChangeMessageVisibility) для довгих задач, інакше гарантія at-least-once створить паралельний дублікат.",
                    size=11, fill=WARN, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'visibility-timeout-race.svg'), W, H, *f)


# ── 4. Prefetch і пастка голодування (Prefetch Starvation) ────────────────────
def prefetch_starvation():
    W, H = 1120, 460
    f = []

    # Ліва частина: Небезпека високого prefetch
    f.append(rect(30, 30, 520, 390, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(290, 58, "1. Жадібний Prefetch (prefetch = 10)", size=13, bold=True, color=POS))

    # Воркер 1 (заблокований)
    f.append(rect(50, 85, 480, 130, fill=WARM, stroke=POS, sw=1.3, rx=6))
    f.append(text(150, 110, "Воркер 1 (Отримав 10 задач):", size=11, bold=True, color=POS))
    f.append(fitbox(60, 125, 140, 75, "Задача 1 (Важка)\nЧас: 30 секунд\n[Виконується... ⚙️]", size=10, bold=True, fill="#ffcccc", stroke=POS))
    f.append(fitbox(210, 125, 305, 75, "Задачі 2..10 (Легкі, по 0.1 с кожна)\nЗаблоковані в локальному буфері Воркера 1!\nЧас очікування у черзі: > 30 секунд", size=10, fill="#ffffff", stroke=LINE))

    # Воркер 2 (голодує)
    f.append(rect(50, 230, 480, 75, fill="#f8fafc", stroke=LINE, sw=1.3, rx=6))
    f.append(text(150, 255, "Воркер 2 (Вільний):", size=11, bold=True, color=MUTED))
    f.append(fitbox(210, 245, 305, 48, "ГОЛОДУВАННЯ (Starvation) 🛑\nПростоює, бо всі задачі забрав Воркер 1", size=10, bold=True, fill="#fff5f5", stroke=POS))

    f.append(fitbox(50, 320, 480, 85,
                    "Наслідок жадібного prefetch:\n"
                    "• Швидкі задачі чекають за спиною важкої.\n"
                    "• Неефективне використання CPU інших серверів.\n"
                    "• Загальний час обробки пакету: 31 секунда.",
                    size=10, fill="#fff5f5", stroke=POS))

    # Права частина: Оптимальний Prefetch (QoS = 1)
    f.append(rect(570, 30, 520, 390, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(830, 58, "2. Справедливий Prefetch (prefetch = 1)", size=13, bold=True, color=FIELD))

    # Воркер 1
    f.append(rect(590, 85, 480, 100, fill=GOOD, stroke=FIELD, sw=1.3, rx=6))
    f.append(text(700, 110, "Воркер 1 (prefetch=1):", size=11, bold=True, color=FIELD))
    f.append(fitbox(600, 125, 455, 45, "Задача 1 (Важка, 30 с) — обробляється окремо", size=10, bold=True, fill="#ffffff", stroke=FIELD))

    # Воркер 2
    f.append(rect(590, 200, 480, 105, fill=GOOD, stroke=FIELD, sw=1.3, rx=6))
    f.append(text(700, 225, "Воркер 2 (prefetch=1):", size=11, bold=True, color=FIELD))
    f.append(fitbox(600, 240, 455, 52, "Послідовно забирає Задачі 2, 3, 4 ... 10 з черги брокера!\nУсі 9 швидких задач виконано за 0.9 секунди!", size=10, bold=True, fill="#d1fae5", stroke=FIELD))

    f.append(fitbox(590, 320, 480, 85,
                    "Результат справедливого розподілу:\n"
                    "• Жодна легка задача не заблокована важкою.\n"
                    "• 100% завантаження всіх доступних воркерів.\n"
                    "• Загальний час скорочено з 31 с до 30 с (легкі готові за 1 с).",
                    size=10, fill="#ecfdf5", stroke=FIELD))

    # Підсумок
    f.append(fitbox(30, 430, 1060, 24,
                    "Правило: для неоднорідних за часом задач встановлюйте prefetch=1 (QoS); більший prefetch доцільний лише для однорідних мікрозадач.",
                    size=10, fill=WARN, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'prefetch-starvation.svg'), W, H, *f)


if __name__ == "__main__":
    competing_consumers_architecture()
    point_to_point_vs_partitioned()
    visibility_timeout_race()
    prefetch_starvation()
    print("All figures generated successfully.")
