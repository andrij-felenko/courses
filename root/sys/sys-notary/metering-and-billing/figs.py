# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Повний конвеєр metering і billing ─────────────────────────────
def fig_metering_architecture():
    W, H = 940, 520
    frags = []
    frags.append(text(W / 2, 28, "Архітектурний конвеєр: від виклику API до фінансового балансу", size=16, bold=True))
    frags.append(text(W / 2, 48, "розділення швидкого шляху запиту, асинхронного обліку й незмінного фінансового реєстру",
                      size=12, color=MUTED, italic=True))

    # Верхній контур: Швидкий шлях (Клієнт -> Шлюз -> Кеш лімітів)
    frags.append(rect(30, 70, 880, 86, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(120, 92, "ШВИДКИЙ ШЛЯХ (Синхронний, < 2 мс)", size=11, bold=True, color=MUTED, anchor="start"))

    frags.append(fitbox(50, 102, 160, 42, "Клієнт / SDK\nAPI-запит", size=12, fill=FILL, stroke=INK, sw=1.5))
    frags.append(arrow(210, 123, 270, 123, color=LINE, sw=1.6))
    frags.append(text(240, 115, "запит", size=10, color=MUTED))

    frags.append(fitbox(270, 102, 210, 42, "API Gateway / Сервіс\nперевірка квоти й виконання", size=12, fill=FILL, stroke=INK, sw=1.5))
    
    frags.append(arrow(480, 123, 560, 123, color=LINE, sw=1.6))
    frags.append(arrow(560, 131, 480, 131, color=LINE, sw=1.6))
    frags.append(text(520, 115, "квота?", size=10, color=MUTED))

    frags.append(fitbox(560, 102, 200, 42, "Кеш лімітів (Redis)\nsoft/hard квоти й холди", size=12, fill="#eaf0fd", stroke=NEG, sw=1.5))

    # Стрілка скидання події в асинхронний конвеєр
    frags.append(arrow(375, 144, 375, 185, color=POS, sw=1.8))
    frags.append(text(395, 168, "асинхронна подія", size=10, color=POS, bold=True, anchor="start"))

    # Нижній контур: 4 етапи асинхронного конвеєра
    frags.append(rect(30, 190, 880, 305, fill="#fbfcfd", stroke=INK, sw=1.5, rx=8))
    frags.append(text(120, 212, "АСИНХРОННИЙ КОНВЕЄР ОБЛІКУ ТА ТАРИФІКАЦІЇ (Loss-intolerant, Event-driven)", size=11, bold=True, color=INK, anchor="start"))

    # Етап 1: Прийом (Ingest & Dedup)
    frags.append(rect(45, 230, 195, 160, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    frags.append(text(142, 252, "1. Прийом і дедуп", size=12, bold=True, color=INK))
    frags.append(fitbox(55, 265, 175, 36, "Event Collector\nHTTP/gRPC черга", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(55, 308, 175, 36, "Брокер повідомлень\nKafka / JetStream / WAL", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(55, 351, 175, 30, "Idempotency-фільтр", size=10, fill="#fdecea", stroke=POS, sw=1.2))

    frags.append(arrow(240, 310, 265, 310, color=LINE, sw=1.6))

    # Етап 2: Агрегація (Aggregation)
    frags.append(rect(265, 230, 195, 160, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    frags.append(text(362, 252, "2. Агрегація у вікнах", size=12, bold=True, color=INK))
    frags.append(fitbox(275, 265, 175, 36, "Stream Aggregator\ntumbling / sliding вікна", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(275, 308, 175, 36, "Колонкове сховище\nClickHouse / Timescale", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(275, 351, 175, 30, "Згортки за метриками", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2))

    frags.append(arrow(460, 310, 485, 310, color=LINE, sw=1.6))

    # Етап 3: Тарифікація (Rating)
    frags.append(rect(485, 230, 195, 160, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    frags.append(text(582, 252, "3. Рушій тарифікації", size=12, bold=True, color=INK))
    frags.append(fitbox(495, 265, 175, 36, "Прайс-плани й тарифи\nверсіоновані правила", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(495, 308, 175, 36, "Градуйований розрахунок\nпакети, overage, знижки", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(495, 351, 175, 30, "Метрики → Гроші", size=10, fill="#fdecea", stroke=POS, sw=1.2))

    frags.append(arrow(680, 310, 705, 310, color=LINE, sw=1.6))

    # Етап 4: Фінансовий реєстр та інвойси (Ledger & Invoicing)
    frags.append(rect(705, 230, 195, 160, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    frags.append(text(802, 252, "4. Фінансовий реєстр", size=12, bold=True, color=INK))
    frags.append(fitbox(715, 265, 175, 36, "Double-Entry Ledger\nнезмінні дебет / кредит", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(715, 308, 175, 36, "Генератор інвойсів\nзакриття розрахунків", size=10, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(715, 351, 175, 30, "Платіжні шлюзи", size=10, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # Зворотний зв'язок: оновлення кешу лімітів
    frags.append(arrow(760, 410, 760, 460, color=NEG, sw=1.6))
    frags.append(line(760, 460, 660, 460, color=NEG, sw=1.6))
    frags.append(arrow(660, 460, 660, 144, color=NEG, sw=1.6))
    frags.append(fitbox(550, 442, 200, 32, "Синхронізація залишку й лімітів", size=10, fill="#eaf0fd", stroke=NEG, sw=1.2))

    render(os.path.join(IMG, "metering-architecture.svg"), W, H, *frags)


# ── Фігура 2: Пошарова (Graduated) проти блокової (Volume) тарифікації ──────
def fig_graduated_vs_volume():
    W, H = 860, 440
    frags = []
    frags.append(text(W / 2, 28, "Пошарова (Tiered / Graduated) проти блокової (Volume) тарифікації", size=16, bold=True))
    frags.append(text(W / 2, 48, "чому блоковий тариф створює згубний стрибок вартості при переході межі",
                      size=12, color=MUTED, italic=True))

    # Ліва панель: Блокова тарифікація (Volume)
    frags.append(rect(40, 70, 370, 345, fill=BG, stroke=POS, sw=1.6, rx=8))
    frags.append(text(225, 96, "Блокова тарифікація (Volume)", size=14, bold=True, color=POS))
    frags.append(text(225, 116, "ціна за одиницю падає для ВСЬОГО обсягу", size=11, color=MUTED))

    # Графік блоковий
    frags.append(line(80, 310, 370, 310, color=LINE, sw=1.4))
    frags.append(line(80, 310, 80, 140, color=LINE, sw=1.4))
    frags.append(text(360, 325, "Одиниці", size=10, color=MUTED, anchor="end"))
    frags.append(text(75, 145, "Сума $", size=10, color=MUTED, anchor="end"))

    # Ступені блокового графіка
    frags.append(line(80, 310, 200, 210, color=POS, sw=2.2))
    frags.append(line(200, 210, 200, 270, color=POS, sw=1.5, dash="4,3"))
    frags.append(circle(200, 210, 4, fill=BG, stroke=POS, sw=2))
    frags.append(circle(200, 270, 4, fill=POS, stroke=POS, sw=2))
    frags.append(line(200, 270, 350, 180, color=POS, sw=2.2))

    frags.append(text(200, 325, "10 000 шт", size=10, color=MUTED))
    frags.append(text(210, 235, "Стрибок вниз!\n9 999 = $100\n10 001 = $70", size=10, color=POS, bold=True, anchor="start"))

    frags.append(fitbox(55, 340, 340, 60,
                         "Аномалія стимулів:\nкористувачеві вигідно «накрутити» зайві виклики,\nщоб заплатити менше за весь місяць.",
                         size=11, fill="#fdecea", stroke=POS, sw=1.2))

    # Права панель: Пошарова тарифікація (Graduated)
    frags.append(rect(450, 70, 370, 345, fill=BG, stroke=FIELD, sw=1.6, rx=8))
    frags.append(text(635, 96, "Пошарова тарифікація (Graduated / Tiered)", size=14, bold=True, color=FIELD))
    frags.append(text(635, 116, "дешевша ціна діє ТІЛЬКИ на перевищення", size=11, color=MUTED))

    # Графік пошаровий
    frags.append(line(490, 310, 780, 310, color=LINE, sw=1.4))
    frags.append(line(490, 310, 490, 140, color=LINE, sw=1.4))
    frags.append(text(770, 325, "Одиниці", size=10, color=MUTED, anchor="end"))
    frags.append(text(485, 145, "Сума $", size=10, color=MUTED, anchor="end"))

    # Неперервна ламана лінія
    frags.append(line(490, 310, 610, 210, color=FIELD, sw=2.2))
    frags.append(circle(610, 210, 4, fill=FIELD, stroke=FIELD, sw=2))
    frags.append(line(610, 210, 760, 160, color=FIELD, sw=2.2))

    frags.append(text(610, 325, "10 000 шт", size=10, color=MUTED))
    frags.append(text(620, 210, "Зміна кута нахилу\nперші 10k по $0.01\nнаступні по $0.007", size=10, color=FIELD, bold=True, anchor="start"))

    frags.append(fitbox(465, 340, 340, 60,
                         "Монотонна справедливість:\nкожна наступна одиниця завжди додає до суми,\nкрива гладка, жодних стрибків чи аномалій.",
                         size=11, fill="#eafaf1", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, "graduated-vs-volume.svg"), W, H, *frags)


# ── Фігура 3: Подвійний бухгалтерський запис у білінгу ───────────────────────
def fig_ledger_double_entry():
    W, H = 880, 460
    frags = []
    frags.append(text(W / 2, 28, "Подвійний бухгалтерський запис у білінговому реєстрі (Double-Entry)", size=16, bold=True))
    frags.append(text(W / 2, 48, "сума дебетів завжди дорівнює сумі кредитів; баланс — це згортка незмінних проведень",
                      size=12, color=MUTED, italic=True))

    # Сценарій: Поповнення на $100 і споживання API на $35
    frags.append(fitbox(50, 70, 780, 40,
                        "Подія 1: Клієнт поповнює баланс на $100  |  Подія 2: Використано обчислень API на $35",
                        size=12, fill=FILL, stroke=INK, sw=1.5, bold=True))

    # Т-рахунки
    # Рахунок 1: Cash / Payment Gateway (Активи)
    frags.append(rect(40, 130, 240, 210, fill=BG, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(160, 155, "Активи: Платіжний шлюз", size=12, bold=True, color=INK))
    frags.append(line(50, 168, 270, 168, color=LINE, sw=1.3))
    frags.append(line(160, 168, 160, 310, color=LINE, sw=1.0))
    frags.append(text(105, 185, "Дебет (+)", size=11, bold=True, color=FIELD))
    frags.append(text(215, 185, "Кредит (−)", size=11, bold=True, color=MUTED))
    frags.append(text(105, 210, "① $100.00", size=11, color=FIELD))
    frags.append(fitbox(50, 285, 220, 42, "Баланс рахунку:\n+$100.00 (гроші зайшли)", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2))

    # Рахунок 2: Customer Prepaid Balance (Зобов'язання / Liabilities)
    frags.append(rect(320, 130, 240, 210, fill=BG, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(440, 155, "Зобов'язання: Депозит клієнта", size=12, bold=True, color=INK))
    frags.append(line(330, 168, 550, 168, color=LINE, sw=1.3))
    frags.append(line(440, 168, 440, 310, color=LINE, sw=1.0))
    frags.append(text(385, 185, "Дебет (−)", size=11, bold=True, color=POS))
    frags.append(text(495, 185, "Кредит (+)", size=11, bold=True, color=NEG))
    frags.append(text(495, 210, "① $100.00", size=11, color=NEG))
    frags.append(text(385, 235, "② $35.00", size=11, color=POS))
    frags.append(fitbox(330, 285, 220, 42, "Залишок зобов'язання:\n$65.00 (доступно клієнту)", size=10, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # Рахунок 3: Earned Revenue (Дохід / Revenue)
    frags.append(rect(600, 130, 240, 210, fill=BG, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(720, 155, "Доходи: Визнаний виторг", size=12, bold=True, color=INK))
    frags.append(line(610, 168, 830, 168, color=LINE, sw=1.3))
    frags.append(line(720, 168, 720, 310, color=LINE, sw=1.0))
    frags.append(text(665, 185, "Дебет (−)", size=11, bold=True, color=MUTED))
    frags.append(text(775, 185, "Кредит (+)", size=11, bold=True, color=FIELD))
    frags.append(text(775, 210, "② $35.00", size=11, color=FIELD))
    frags.append(fitbox(610, 285, 220, 42, "Зароблений дохід:\n+$35.00 (надані послуги)", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2))

    # Фундаментальне рівняння
    frags.append(fitbox(50, 360, 780, 75,
                        "Інваріант реєстру: ∑ Дебетів ≡ ∑ Кредитів  (① $100 = $100;  ② $35 = $35)\n"
                        "Жодного прямого UPDATE таблиці рахунків: будь-яка зміна балансу — це незмінний рядок журналу,\n"
                        "а фінансовий аудит завжди зводить дебет і кредит у нуль.",
                        size=11, fill="#fdfefe", stroke=INK, sw=1.5, bold=True))

    render(os.path.join(IMG, "ledger-double-entry.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_metering_architecture()
    fig_graduated_vs_volume()
    fig_ledger_double_entry()
    print("Figures generated successfully.")
