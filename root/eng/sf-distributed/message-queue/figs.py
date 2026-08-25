# -*- coding: utf-8 -*-
"""Фігури до теми «Черга повідомлень (point-to-point)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / відхилення
COOL = "#eaf0fd"   # нейтральне / структура / повідомлення
GOOD = "#e8f6ee"   # успіх / надійність / ACK
WARN = "#fef9e7"   # застереження / тайм-аут / DLQ
ACCENT = "#2457d6" # синій акцент


# ── 1. Архітектура Point-to-Point: буферизація та конкурентні споживачі ──────
def p2p_queue_architecture():
    W, H = 1080, 480
    f = []

    # Загальний заголовок і фон
    f.append(rect(20, 15, 1040, 445, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))

    # Секція продюсерів (ліворуч)
    f.append(rect(40, 50, 200, 320, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(140, 80, "Продюсери (Виробники)", size=13, bold=True, color=INK))
    f.append(fitbox(60, 110, 160, 55, "Web API Сервіс\n(Реєстрація замовлень)", size=11.5, bold=True, fill=COOL))
    f.append(fitbox(60, 195, 160, 55, "Cron Планувальник\n(Генерація звітів)", size=11.5, bold=True, fill=COOL))
    f.append(fitbox(60, 280, 160, 55, "Платіжний шлюз\n(Події транзакцій)", size=11.5, bold=True, fill=COOL))

    # Напис над стрілками публікації
    f.append(text(285, 120, "Публікація (enqueue)", size=10.5, color=MUTED, italic=True))

    # Стрілки від продюсерів до черги
    f.append(arrow(220, 137, 320, 195, color=LINE, sw=1.6))
    f.append(arrow(220, 222, 320, 215, color=LINE, sw=1.6))
    f.append(arrow(220, 307, 320, 235, color=LINE, sw=1.6))

    # Центральна секція: Брокер і черга (FIFO буфер)
    f.append(rect(330, 50, 380, 320, fill=WARN, stroke=LINE, sw=1.5, rx=8))
    f.append(text(520, 80, "Брокер черги повідомлень (Queue)", size=13.5, bold=True, color=INK))
    f.append(text(520, 102, "Буфер у пам'яті + Стійкий журнал на диску (WAL)", size=11, color=MUTED, italic=True))

    # Пакет повідомлень у черзі
    f.append(fitbox(350, 130, 340, 170, "", fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(520, 152, "Черга FIFO: вхідний буфер завдань", size=12, bold=True, color=INK))

    # Повідомлення в черзі (слоти)
    f.append(fitbox(365, 170, 68, 45, "Task #5\n(Новий)", size=10, bold=True, fill=COOL))
    f.append(fitbox(440, 170, 68, 45, "Task #4\n(Новий)", size=10, bold=True, fill=COOL))
    f.append(fitbox(515, 170, 68, 45, "Task #3\n(Новий)", size=10, bold=True, fill=COOL))
    f.append(fitbox(590, 170, 85, 45, "Task #2\n(В оренді)", size=10, bold=True, fill=WARN))

    # Індикатор стану черги
    f.append(fitbox(365, 230, 310, 55, "Станція диспетчеризації (Point-to-Point):\nКожне повідомлення видається РІВНО ОДНОМУ воркеру", size=10.5, color=INK, fill="#f8fafc"))

    # Секція диску/WAL під чергою
    f.append(fitbox(350, 310, 340, 45, "💾 Журнал випереджального запису (WAL на SSD)\nПовідомлення захищені від раптового знеструмлення брокера", size=10, fill="#f1f5f9"))

    # Стрілки від черги до воркерів
    f.append(arrow(710, 170, 810, 137, color=LINE, sw=1.6))
    f.append(arrow(710, 215, 810, 222, color=LINE, sw=1.6))
    f.append(arrow(710, 260, 810, 307, color=LINE, sw=1.6))
    f.append(text(760, 120, "Видача (dequeue)", size=10.5, color=MUTED, italic=True))

    # Зворотна стрілка підтвердження ACK
    f.append(arrow(810, 160, 710, 190, color=FIELD, sw=1.6))
    f.append(text(760, 210, "ACK (готово)", size=10.5, color=FIELD, bold=True))

    # Секція споживачів (праворуч)
    f.append(rect(820, 50, 220, 320, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(930, 80, "Пул воркерів (Consumers)", size=13, bold=True, color=INK))
    f.append(fitbox(840, 110, 180, 55, "Воркер A (Зайнятий)\nОбробляє Task #1 → ACK", size=11, bold=True, fill=GOOD))
    f.append(fitbox(840, 195, 180, 55, "Воркер B (Зайнятий)\nОбробляє Task #2", size=11, bold=True, fill=WARN))
    f.append(fitbox(840, 280, 180, 55, "Воркер C (Вільний)\nЧекає на Task #3 (prefetch)", size=11, bold=True, fill=COOL))

    # Пояснювальний підсумок знизу
    f.append(fitbox(40, 385, 1000, 60,
                    "Головний інваріант Point-to-Point: попри наявність кількох споживачів у пулі, "
                    "кожне повідомлення дістається лише одному виконавцю. Після успішного підтвердження (ACK) "
                    "повідомлення назавжди видаляється з черги.",
                    size=12, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'p2p-queue-architecture.svg'), W, H, *f)


# ── 2. Життєвий цикл повідомлення: скінченний автомат станів ───────────────────
def message_lifecycle_states():
    W, H = 1100, 500
    f = []

    f.append(rect(20, 15, 1060, 465, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(550, 45, "Скінченний автомат станів повідомлення в точці-точці", size=15, bold=True, color=INK))

    # Стан 1: Вхід / Ready (Очікує в черзі)
    f.append(fitbox(50, 160, 180, 100, "1. ГОТОВЕ (Ready)\n\nПовідомлення записане\nв буфер і чекає\nна вільного споживача", size=11.5, bold=True, fill=COOL, stroke=ACCENT, sw=2))

    # Стрілка публікації
    f.append(arrow(50, 100, 140, 160, color=LINE, sw=1.6))
    f.append(text(75, 120, "Публікація\n(publish)", size=11, color=INK, bold=True))

    # Перехід Ready -> In-Flight
    f.append(arrow(230, 210, 370, 210, color=LINE, sw=1.8))
    f.append(text(300, 195, "Оренда / Видача", size=11, bold=True, color=INK))
    f.append(text(300, 230, "acquire / consume", size=10, color=MUTED, italic=True))

    # Стан 2: In-Flight (В оренді / Невидиме для інших)
    f.append(fitbox(370, 150, 220, 120, "2. В ОБРОБЦІ (In-Flight)\n\nПовідомлення заблоковане\n(Visibility Timeout).\nІнші воркери його не бачать", size=11.5, bold=True, fill=WARN, stroke="#d97706", sw=2))

    # Успішна гілка: In-Flight -> ACK (Deleted)
    f.append(arrow(590, 190, 780, 130, color=FIELD, sw=2))
    f.append(text(685, 140, "Успіх: ACK", size=12, bold=True, color=FIELD))
    f.append(text(685, 160, "Роботу завершено", size=10.5, color=MUTED))

    # Стан 3: Видалено (ACK)
    f.append(fitbox(780, 85, 260, 90, "3. ПІДТВЕРДЖЕНО (Acked)\n\nПовідомлення видаляється\nіз пам'яті та диску.\n(Кінцевий стан)", size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    # Неуспішна гілка: In-Flight -> NACK / Таймаут оренди
    f.append(arrow(480, 270, 480, 360, color=POS, sw=1.8))
    f.append(text(545, 305, "Помилка (NACK) або\nТаймаут оренди", size=11, bold=True, color=POS))

    # Блок перевірки спроб
    f.append(fitbox(380, 360, 200, 70, "Перевірка ліміту спроб\n(Delivery Attempts)", size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.4))

    # Повернення в чергу (спроб < ліміту)
    f.append(line(380, 395, 140, 395, color=ACCENT, sw=1.6))
    f.append(arrow(140, 395, 140, 260, color=ACCENT, sw=1.6))
    f.append(text(250, 415, "Спроб < MAX: requeue / redelivery (з бекофом)", size=11, bold=True, color=ACCENT))

    # Відправка в DLQ (спроб >= ліміту)
    f.append(arrow(580, 395, 780, 395, color=POS, sw=2))
    f.append(text(680, 380, "Спроб ≥ MAX", size=11, bold=True, color=POS))

    # Стан 4: Dead Letter Queue
    f.append(fitbox(780, 350, 260, 90, "4. МЕРТВА ЧЕРГА (DLQ)\n\nОтруйне повідомлення (Poison Pill)\nізольовано для аналізу інженерами.\n(Кінцевий стан)", size=11.5, bold=True, fill=WARM, stroke=POS, sw=2))

    render(os.path.join(OUT, 'message-lifecycle-states.svg'), W, H, *f)


# ── 3. Порівняння трьох парадигм обміну повідомленнями ─────────────────────────
def queue_vs_pubsub_vs_log():
    W, H = 1140, 520
    f = []

    f.append(rect(20, 15, 1100, 485, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(570, 45, "Три парадигми асинхронного обміну: Черга, Pub/Sub та Журнал подій", size=15, bold=True, color=INK))

    cols = [
        (40.0, 370.0, "1. Черга (Point-to-Point)",
         "RabbitMQ, SQS, ActiveMQ\n\n"
         "• Модель: 1 повідомлення → 1 воркер\n"
         "• Споживання: Конкурентний розбір черги\n"
         "• Стан: Зберігається на брокері\n"
         "• Видалення: Одразу після підтвердження (ACK)\n"
         "• Повторне читання: НЕМОЖЛИВЕ\n\n"
         "Призначення: розподіл важких задач,\nбуферизація піків, бекенд-обробка.",
         COOL, ACCENT),

        (390.0, 720.0, "2. Тема (Publish / Subscribe)",
         "Redis Pub/Sub, SNS, Google Pub/Sub\n\n"
         "• Модель: 1 повідомлення → N підписників\n"
         "• Споживання: Fan-out розсилка кожному\n"
         "• Стан: Ефемерний (без стану підписників)\n"
         "• Збереження: Зникає одразу після розсилки\n"
         "• Повторне читання: НЕМОЖЛИВЕ\n\n"
         "Призначення: розсилка сповіщень,\nінвалідація кешів, чати, телеметрія.",
         WARN, "#d97706"),

        (740.0, 1070.0, "3. Журнал подій (Event Log)",
         "Apache Kafka, Apache Pulsar\n\n"
         "• Модель: Незмінний потік подій (Append-only)\n"
         "• Споживання: Зсуви (Offset) ведуть клієнти\n"
         "• Стан: Клієнти самі фіксують свій прогрес\n"
         "• Збереження: Дні/місяці за часом або обсягом\n"
         "• Повторне читання: ПОВНОЦІННЕ (Replay)\n\n"
         "Призначення: Event Sourcing, потокова\nаналітика, спільна історія фактів.",
         GOOD, FIELD),
    ]

    for x0, x1, title, body, fill_c, stroke_c in cols:
        mid = (x0 + x1) / 2
        f.append(rect(x0, 70, x1 - x0, 360, fill=fill_c, stroke=stroke_c, sw=1.6, rx=8))
        f.append(text(mid, 100, title, size=13.5, bold=True, color=INK))
        f.append(line(x0 + 15, 115, x1 - 15, 115, color=MUTED, sw=1.1))

        lines = body.split("\n")
        f.append(mtext(mid, 138, lines, size=11.5, color=INK, lh=1.35))

    # Спільний підсумок
    f.append(fitbox(40, 440, 1030, 45,
                    "Ключова різниця: Черга знищує повідомлення після виконання завдання одним виконавцем; "
                    "Pub/Sub копіює його всім активним слухачам; Журнал зберігає факти назавжди для багатьох систем.",
                    size=12, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'queue-vs-pubsub-vs-log.svg'), W, H, *f)


# ── 4. Крива Кінгмана: нелінійний вибух затримки при наближенні утилізації до 100% ─
def kingman_utilization_curve():
    W, H = 1060, 520
    f = []

    f.append(rect(20, 15, 1020, 485, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(530, 45, "Крива Кінгмана: нелінійне зростання часу очікування в черзі W_q", size=15, bold=True, color=INK))

    # Координатні осі
    ox, oy = 120, 410
    axis_w, axis_h = 800, 310

    # Вертикальні розділові смуги зон (лінії замість прямокутників, щоб уникнути накладання)
    z1_end_x = ox + 0.70 * axis_w
    z2_end_x = ox + 0.85 * axis_w

    f.append(line(z1_end_x, oy, z1_end_x, oy - axis_h, color="#27ae60", sw=1.5, dash="6,4"))
    f.append(line(z2_end_x, oy, z2_end_x, oy - axis_h, color="#c0392b", sw=1.5, dash="6,4"))

    # Підписи зон зверху
    f.append(text((ox + z1_end_x) / 2, oy - axis_h + 20, "Зона стійкості (ρ < 0.7)", size=11.5, bold=True, color=FIELD))
    f.append(text((ox + z1_end_x) / 2, oy - axis_h + 38, "Затримка стабільна, черга не росте", size=10, color=MUTED))

    f.append(text((z1_end_x + z2_end_x) / 2, oy - axis_h + 20, "Зона ризику", size=11.5, bold=True, color="#b45309"))

    f.append(text((z2_end_x + ox + axis_w) / 2, oy - axis_h + 20, "Колапс черги (ρ > 0.85)", size=11.5, bold=True, color=POS))
    f.append(text((z2_end_x + ox + axis_w) / 2, oy - axis_h + 38, "W_q → ∞ (вибух затримки)", size=10, color=POS))

    # Горизонтальні лінії сітки
    f.append(line(ox, oy - axis_h * 0.5, ox + axis_w, oy - axis_h * 0.5, color="#e2e8f0", sw=1.0, dash="4,4"))
    f.append(line(ox, oy - axis_h * 0.25, ox + axis_w, oy - axis_h * 0.25, color="#e2e8f0", sw=1.0, dash="4,4"))

    # Осі координат
    f.append(line(ox, oy, ox + axis_w + 30, oy, color=INK, sw=1.8))  # X
    f.append(line(ox, oy, ox, oy - axis_h - 20, color=INK, sw=1.8))  # Y

    # Підписи осей
    f.append(text(ox + axis_w / 2, oy + 45, "Коефіцієнт утилізації черги: ρ = λ / μ (Навантаження системи)", size=12.5, bold=True, color=INK))
    f.append(text(ox - 50, oy - axis_h / 2, "Час очікування\nв черзі (W_q)", size=12, bold=True, color=INK))

    # Поділки на осі X (утилізація)
    ticks_x = [
        (0.0, "0%"),
        (0.5, "50%"),
        (0.7, "70%"),
        (0.8, "80%"),
        (0.9, "90%"),
        (0.95, "95%"),
        (0.99, "99%"),
    ]

    for val, label in ticks_x:
        px = ox + val * axis_w
        f.append(line(px, oy, px, oy + 6, color=INK, sw=1.4))
        f.append(text(px, oy + 22, label, size=11, color=INK))

    # Малювання кривої Кінгмана: W_q ~ rho / (1 - rho)
    curve_pts = []
    steps = 80
    for i in range(steps + 1):
        rho = (i / steps) * 0.965
        px = ox + rho * axis_w
        norm_y = (rho / (1.0 - rho)) * 0.10
        clamped_y = min(norm_y * axis_h, axis_h)
        py = oy - clamped_y
        curve_pts.append((px, py))

    # Створюємо лінії між точками кривої
    for j in range(len(curve_pts) - 1):
        p1 = curve_pts[j]
        p2 = curve_pts[j + 1]
        f.append(line(p1[0], p1[1], p2[0], p2[1], color=POS, sw=3.0))

    # Точки на кривій із підписами
    # Точка 1: 50% утилізації
    px50 = ox + 0.5 * axis_w
    py50 = oy - (0.5 / 0.5) * 0.10 * axis_h
    f.append(circle(px50, py50, 5, fill=FIELD, stroke=INK, sw=1.5))
    f.append(textbox(px50 - 50, py50 - 25, "ρ = 50%: W_q ≈ 1×", size=10, bold=True, fill=GOOD)[0])

    # Точка 2: 80% утилізації
    px80 = ox + 0.8 * axis_w
    py80 = oy - (0.8 / 0.2) * 0.10 * axis_h
    f.append(circle(px80, py80, 5, fill="#d97706", stroke=INK, sw=1.5))
    f.append(textbox(px80 - 55, py80 - 25, "ρ = 80%: W_q ≈ 4×", size=10, bold=True, fill=WARN)[0])

    # Точка 3: 95% утилізації
    px95 = ox + 0.95 * axis_w
    py95 = oy - (0.95 / 0.05) * 0.10 * axis_h
    f.append(circle(px95, py95, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(textbox(px95 - 70, py95 - 25, "ρ = 95%: W_q ≈ 19× !", size=10.5, bold=True, fill=WARM)[0])

    # Пояснювальний висновок
    f.append(fitbox(40, 455, 980, 35,
                    "Практичний висновок: спроба завантажити чергу вище 80–85 % призводить до лавинного росту часу очікування, "
                    "навіть якщо середня швидкість надходження формально не перевищує потужність воркерів.",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'kingman-utilization-curve.svg'), W, H, *f)


if __name__ == "__main__":
    p2p_queue_architecture()
    message_lifecycle_states()
    queue_vs_pubsub_vs_log()
    kingman_utilization_curve()
    print("All figures generated successfully.")
