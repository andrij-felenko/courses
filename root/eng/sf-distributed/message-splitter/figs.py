# -*- coding: utf-8 -*-
"""Фігури теми «Розділювач повідомлень (Message Splitter)». Вивід — ./img/*.svg"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"


# ── 1. composite-vs-split-pipeline: Монолітна обробка проти декомпозиції ────
def fig_composite_vs_split():
    W, H = 940, 480
    f = []

    # Верхня панель: Монолітна обробка (блокування та спільна відмова)
    f.append(rect(15, 15, 910, 215, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(470, 38, "Монолітна обробка складеного пакета (Head-of-Line Blocking & спільна відмова)", size=13, bold=True, color=POS))

    b1, _, _ = textbox(115, 125, "Складений пакет\n10 000 замовлень\n(120 МБ JSON/XML)", size=11, bold=True, min_w=150, fill=FILL, stroke=LINE)
    f.append(b1)

    f.append(arrow(200, 125, 275, 125, color=LINE, sw=1.8))
    f.append(text(237, 115, "Потік", size=10, color=MUTED))

    b2, _, _ = textbox(415, 125, "Монолітний воркер\nПослідовний розбір у циклі\nПам'ять: 1.8 ГБ (DOM Tree)\nЧас виконання: 180 с\n✗ Помилка на 4 999-му елементі!", size=10.5, bold=True, min_w=220, fill=RED_F, stroke=POS, sw=1.6)
    f.append(b2)

    f.append(arrow(535, 125, 610, 125, color=POS, sw=1.8))
    f.append(text(572, 115, "Відкат", size=10, color=POS))

    b3, _, _ = textbox(760, 125, "Колапс системи:\n• Простій черги (Head-of-Line)\n• Нульовий паралелізм воркерів\n• Спільна відмова всіх 10 000 задач\n• Повторний прогін усього файлу", size=10.5, min_w=230, fill=WARN_F, stroke="#d35400")
    f.append(b3)

    # Нижня панель: Декомпозиція через Message Splitter
    f.append(rect(15, 245, 910, 220, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(470, 268, "Декомпозиція через Message Splitter (Паралелізм, ізоляція та нульова затримка)", size=13, bold=True, color=FIELD))

    b4, _, _ = textbox(115, 360, "Складений пакет\n10 000 замовлень\nВхідний канал\n(orders.bulk)", size=11, bold=True, min_w=150, fill=FILL, stroke=LINE)
    f.append(b4)

    f.append(arrow(200, 360, 265, 360, color=LINE, sw=1.8))

    b5, _, _ = textbox(365, 360, "Message Splitter\nПотоковий SAX/Span розбір\nO(1) пам'ять (64 КБ)\nІн'єкція метаданих:\nCorrID + SeqNum + Total", size=10.5, bold=True, min_w=170, fill=GREEN_F, stroke=FIELD, sw=1.8)
    f.append(b5)

    # Розгалуження на воркери
    f.append(arrow(460, 330, 545, 310, color=FIELD, sw=1.5))
    f.append(arrow(460, 360, 545, 360, color=FIELD, sw=1.5))
    f.append(arrow(460, 390, 545, 410, color=FIELD, sw=1.5))

    bw1, _, _ = textbox(625, 310, "Воркер 1 (Оплата)", size=10, min_w=135, pad=4, fill=BLUE_F, stroke=NEG)
    bw2, _, _ = textbox(625, 360, "Воркер 2 (Склад)", size=10, min_w=135, pad=4, fill=BLUE_F, stroke=NEG)
    bw3, _, _ = textbox(625, 410, "Воркер N (Фрод)", size=10, min_w=135, pad=4, fill=BLUE_F, stroke=NEG)
    f.extend([bw1, bw2, bw3])

    f.append(arrow(700, 310, 745, 335, color=FIELD, sw=1.2))
    f.append(arrow(700, 360, 745, 360, color=FIELD, sw=1.2))
    f.append(arrow(700, 410, 745, 385, color=FIELD, sw=1.2))

    b6, _, _ = textbox(825, 360, "Переваги:\n• 100x прискорення\n• Ізоляція збоїв (DLQ)\n• Горизонтальний масштаб\n• Наскрізний протитиск", size=10.5, min_w=135, fill=GREEN_F, stroke=FIELD)
    f.append(b6)

    render(out("composite-vs-split-pipeline.svg"), W, H, *f)


# ── 2. splitter-anatomy-correlation: Структура декомпозиції та заголовки ───
def fig_splitter_anatomy():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Анатомія декомпозиції: ін'єкція кореляційних заголовків та ізоляція елементів", size=14, bold=True, color=INK))

    # 1. Вхідний складений конверт
    f.append(rect(20, 60, 240, 375, fill=GRAY_F, stroke=LINE, sw=1.5, rx=8))
    f.append(text(140, 85, "Складений конверт (Batch)", size=12, bold=True, color=INK))

    b_h, _, _ = textbox(140, 140, "Заголовки пакета:\nmsg_id: 'pkg-9841'\ntraceparent: '00-4bf9...'\nsource: 'checkout'", size=10, min_w=205, fill=FILL, stroke=MUTED)
    b_i1, _, _ = textbox(140, 220, "Елемент 1:\n{ item_id: 'ITM-01',\n  qty: 2, price: 45.0 }", size=10, min_w=205, fill=GREEN_F, stroke=FIELD)
    b_i2, _, _ = textbox(140, 295, "Елемент 2:\n{ item_id: 'ITM-02',\n  qty: 1, price: 120.0 }", size=10, min_w=205, fill=GREEN_F, stroke=FIELD)
    b_in, _, _ = textbox(140, 375, "Елемент N:\n{ item_id: 'ITM-N',\n  qty: 5, price: 12.5 }", size=10, min_w=205, fill=GREEN_F, stroke=FIELD)
    f.extend([b_h, b_i1, b_i2, b_in])

    # Стрілка в спліттер
    f.append(arrow(265, 245, 335, 245, color=FIELD, sw=2.2))

    # 2. Розділювач
    b_sp, _, _ = textbox(445, 245, "Message Splitter\n\n1. Потоковий розбір\n2. CorrID = pkg-9841\n3. SeqNum: 1..N\n4. SeqSize: N\n5. Успадкування trace\n6. Публікація в чергу", size=10.5, bold=True, min_w=175, pad=8, fill=GREEN_F, stroke=FIELD, sw=2.0)
    f.append(b_sp)

    # Стрілки на вихід
    f.append(arrow(540, 185, 605, 125, color=FIELD, sw=1.8))
    f.append(arrow(540, 245, 605, 245, color=FIELD, sw=1.8))
    f.append(arrow(540, 305, 605, 365, color=FIELD, sw=1.8))

    # 3. Вихідні атомарні повідомлення
    b_m1, _, _ = textbox(765, 125, "Атомарне повідомлення 1/N\nCorrID: 'pkg-9841' | Seq: 1 | Total: N\ntraceparent: '00-4bf9...-span01'\nPayload: { item_id: 'ITM-01', qty: 2, price: 45.0 }", size=10, min_w=280, fill=BLUE_F, stroke=NEG)

    b_m2, _, _ = textbox(765, 245, "Атомарне повідомлення 2/N\nCorrID: 'pkg-9841' | Seq: 2 | Total: N\ntraceparent: '00-4bf9...-span02'\nPayload: { item_id: 'ITM-02', qty: 1, price: 120.0 }", size=10, min_w=280, fill=BLUE_F, stroke=NEG)

    b_mn, _, _ = textbox(765, 365, "Атомарне повідомлення N/N\nCorrID: 'pkg-9841' | Seq: N | Total: N\ntraceparent: '00-4bf9...-spanN'\nPayload: { item_id: 'ITM-N', qty: 5, price: 12.5 }", size=10, min_w=280, fill=BLUE_F, stroke=NEG)
    f.extend([b_m1, b_m2, b_mn])

    render(out("splitter-anatomy-correlation.svg"), W, H, *f)


# ── 3. streaming-vs-buffering: Буферизація проти потокового розбору ─────────
def fig_streaming_vs_buffering():
    W, H = 940, 440
    f = []

    f.append(text(470, 30, "Порівняння стратегій парсингу: повна буферизація проти потокового розбору", size=14, bold=True, color=INK))

    # Ліва половина: DOM / Буферизація
    f.append(rect(15, 55, 445, 365, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(237, 80, "Повна буферизація в пам'яті (DOM Tree)", size=12.5, bold=True, color=POS))

    b1, _, _ = textbox(237, 130, "Вхідний пакет (100 МБ JSON/XML)\nПовне читання у пам'ять процесу", size=10.5, min_w=380, fill=FILL, stroke=LINE)
    f.append(b1)

    f.append(arrow(237, 165, 237, 195, color=POS, sw=1.8))

    b2, _, _ = textbox(237, 240, "Побудова AST / Об'єктного дерева:\n• Мільйони вузлів та DTO-об'єктів\n• Використання RAM: 600–900 МБ (O(N))\n• GC-паузи (Stop-the-world 1.5–3.5 с)", size=10.5, bold=True, min_w=380, fill=RED_F, stroke=POS)
    f.append(b2)

    f.append(arrow(237, 290, 237, 320, color=POS, sw=1.8))

    b3, _, _ = textbox(237, 365, "Ризики: Out-Of-Memory при сплесках трафіку,\nвеличезна латентність до відправки першого елемента", size=10, min_w=380, fill=WARN_F, stroke="#d35400")
    f.append(b3)

    # Права половина: Streaming / Zero-Copy
    f.append(rect(480, 55, 445, 365, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(702, 80, "Потоковий розбір (StAX / SAX / Zero-Copy Span)", size=12.5, bold=True, color=FIELD))

    b4, _, _ = textbox(702, 130, "Вхідний потік байтів через Socket / mmap\nФіксований буфер кільця (64 КБ)", size=10.5, min_w=380, fill=FILL, stroke=LINE)
    f.append(b4)

    f.append(arrow(702, 165, 702, 195, color=FIELD, sw=1.8))

    b5, _, _ = textbox(702, 240, "Ітеративне виділення токенів:\n• Нульове зайве виділення пам'яті (Zero-Copy)\n• Використання RAM: O(1) (~64 КБ стабільно)\n• Миттєва емісія елемента №1 (< 1 мс)", size=10.5, bold=True, min_w=380, fill=GREEN_F, stroke=FIELD)
    f.append(b5)

    f.append(arrow(702, 290, 702, 320, color=FIELD, sw=1.8))

    b6, _, _ = textbox(702, 365, "Переваги: Необмежений розмір пакета (10+ ГБ),\nстабільний SLA, природний протитиск (Backpressure)", size=10, min_w=380, fill=BLUE_F, stroke=NEG)
    f.append(b6)

    render(out("streaming-vs-buffering-splitter.svg"), W, H, *f)


# ── 4. failure-modes-atomicity: Механіка збоїв та ідемпотентність ────────────
def fig_failure_modes():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Механіка збоїв і відновлення: часткова публікація, транзакції та ідемпотентність", size=14, bold=True, color=INK))

    # Верхня панель: Сценарій аварії
    f.append(rect(15, 55, 910, 165, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(470, 76, "Сценарій збою: аварійне завершення спліттера на елементі K (350 з 1000)", size=12.5, bold=True, color=POS))

    b1, _, _ = textbox(145, 140, "Спліттер публікує:\nЕлементи 1..350 -> OK\nЕлемент 351 -> КРАХ!\n352..1000 -> Не надіслано", size=10, min_w=200, fill=FILL, stroke=LINE)
    f.append(b1)

    f.append(arrow(255, 140, 325, 140, color=POS, sw=1.8))

    b2, _, _ = textbox(470, 140, "Стан системи після перезапуску:\n• Перші 350 уже споживаються воркерами\n• Брокер повертає весь вхідний пакет на повтор\n• Спліттер починає розбір наново з 1-го елемента", size=10, bold=True, min_w=250, fill=RED_F, stroke=POS)
    f.append(b2)

    f.append(arrow(605, 140, 675, 140, color=POS, sw=1.8))

    b3, _, _ = textbox(795, 140, "Загроза:\nДублювання 1..350\nПодвійне списання коштів\nПорушення цілісності", size=10, min_w=190, fill=WARN_F, stroke="#d35400")
    f.append(b3)

    # Нижня панель: Дворівневий захист
    f.append(rect(15, 235, 910, 205, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(470, 258, "Дворівневий захист: транзакційний брокер та ідемпотентний фільтр споживача", size=12.5, bold=True, color=FIELD))

    b4, _, _ = textbox(245, 345, "Рівень 1: Транзакційна сесія брокера (Kafka / AMQP):\n• begin_transaction()\n• Публікація всіх 1 000 елементів у транзакції\n• commit_transaction() або abort()\nРезультат: споживачі бачать або всі 1 000, або 0", size=10, min_w=400, fill=GREEN_F, stroke=FIELD, sw=1.5)
    f.append(b4)

    b5, _, _ = textbox(695, 345, "Рівень 2: Ідемпотентність споживача (Redis / SQL):\n• Ключ: CorrID + ':' + SequenceNum\n• SET key NX EX 86400 (Атомарний запис)\n• Якщо ключ є -> ACK без повторної бізнес-дії\nРезультат: повна стійкість до повторів", size=10, min_w=400, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(b5)

    render(out("failure-modes-atomicity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_composite_vs_split()
    fig_splitter_anatomy()
    fig_streaming_vs_buffering()
    fig_failure_modes()
    print("Усі 4 фігури успішно згенеровано.")
