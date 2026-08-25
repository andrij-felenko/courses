# -*- coding: utf-8 -*-
"""Фігури теми «Квитанція в камері схову (Claim Check)». Вивід — ./img/*.svg"""
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


# ── 1. claim-check-architecture: Архітектура та потік даних ──────────────────
def fig_claim_check_architecture():
    W, H = 960, 460
    f = []

    f.append(text(480, 28, "Архітектура Claim Check: поділ на легкий потік керування і важкий стан", size=14, bold=True, color=INK))

    # Видавець (Producer)
    b_p, _, _ = textbox(110, 240, "Видавець (Producer)\nГенерує важкий звіт\n(Розмір: 45 МБ)\n1. Розділяє метадані й тіло\n2. Зберігає тіло у S3\n3. Отримує ключ сховища\n4. Публікує легку квитанцію", size=10, bold=True, min_w=170, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(b_p)

    # Об'єктне сховище (Object Store / S3 / MinIO) зверху
    f.append(rect(330, 55, 290, 130, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(475, 80, "Об'єктне сховище (S3 / Blob Storage)", size=11, bold=True, color=FIELD))
    f.append(text(475, 105, "Зберігання незмінного стану (Payload)", size=9.5, color=INK))
    f.append(text(475, 125, "Key: 'payloads/2026/08/msg-981.bin'", size=9.5, color=MUTED))
    f.append(text(475, 145, "SHA-256: 7f83b165... | Розмір: 45.0 МБ", size=9.5, color=MUTED))
    f.append(text(475, 165, "Дешеве зберігання на NVMe/HDD сховища", size=9.5, color=FIELD))

    # Брокер повідомлень (Message Broker) знизу
    f.append(rect(330, 260, 290, 170, fill=WARN_F, stroke="#d35400", sw=1.5, rx=8))
    f.append(text(475, 285, "Брокер повідомлень (Kafka / RabbitMQ / SQS)", size=11, bold=True, color="#d35400"))
    f.append(text(475, 310, "Легкий конверт події (Квитанція, 420 байтів):", size=9.5, bold=True, color=INK))
    f.append(text(475, 332, "event_type: 'ReportGenerated'", size=9, color=INK))
    f.append(text(475, 350, "claim_id: 'clm-981-a7f4'", size=9, color=INK))
    f.append(text(475, 368, "storage_uri: 's3://bucket/payloads/...'", size=9, color=INK))
    f.append(text(475, 386, "content_sha256: '7f83b165...'", size=9, color=INK))
    f.append(text(475, 408, "Буфери брокера вільні | 0 блокувань черги", size=9.5, bold=True, color=FIELD))

    # Стрілки від Продюсера
    f.append(arrow(180, 195, 325, 120, color=FIELD, sw=1.8))
    f.append(text(230, 145, "1. PUT payload (45 МБ)", size=9.5, bold=True, color=FIELD))

    f.append(arrow(325, 140, 200, 215, color=FIELD, sw=1.5))
    f.append(text(275, 188, "2. Key & ETag ACK", size=9, color=FIELD))

    f.append(arrow(195, 280, 325, 330, color="#d35400", sw=1.8))
    f.append(text(250, 320, "3. Publish Ticket (420 B)", size=9.5, bold=True, color="#d35400"))

    # Споживач А (Фільтр / Аудитор)
    b_ca, _, _ = textbox(825, 140, "Споживач А (Фільтр / Аудит)\nЧитає лише метадані квитанції\n(Тип події, автор, мітка часу)\nТіло НЕ завантажується!\n0 МБ трафіку сховища\nЗатримка: < 1 мілісекунди", size=9.5, min_w=190, fill=GREEN_F, stroke=FIELD, sw=1.4)
    f.append(b_ca)

    # Споживач Б (Аналітичний воркер)
    b_cb, _, _ = textbox(825, 345, "Споживач Б (Аналітика / Обробник)\n1. Отримує квитанцію з брокера\n2. Виконує GET у S3 за URI\n3. Перевіряє SHA-256 хеш\n4. Обробляє 45 МБ даних у RAM\nЗавантаження лише за потребою", size=9.5, bold=True, min_w=200, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(b_cb)

    # Стрілки від Брокера до Споживачів
    f.append(arrow(625, 310, 725, 160, color="#d35400", sw=1.5))
    f.append(text(695, 220, "Квитанція (420 B)", size=9, color="#d35400"))

    f.append(arrow(625, 360, 720, 350, color="#d35400", sw=1.5))
    f.append(text(675, 375, "Квитанція", size=9, color="#d35400"))

    # Стрілка від Сховища до Споживача Б
    f.append(arrow(625, 120, 770, 275, color=FIELD, sw=1.8))
    f.append(text(725, 195, "4. GET payload (45 МБ)", size=9.5, bold=True, color=FIELD))

    render(out("claim-check-architecture.svg"), W, H, *f)


# ── 2. claim-check-lifecycle-gc: Життєвий цикл та прибирання сміття ──────────
def fig_claim_check_lifecycle():
    W, H = 960, 430
    f = []

    f.append(text(480, 26, "Життєвий цикл стану Claim Check та стратегії прибирання сміття (Garbage Collection)", size=13.5, bold=True, color=INK))

    # Колонка 1: Створення та випередження
    f.append(rect(15, 55, 215, 355, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(122, 80, "1. Збереження стану", size=11, bold=True, color=INK))
    b_st1, _, _ = textbox(122, 140, "Генерація блоба\nРозрахунок SHA-256\nСтворення ключа CAS:\nsha256(payload)", size=9.5, min_w=185, fill=FILL, stroke=MUTED)
    b_st2, _, _ = textbox(122, 245, "Синхронний PUT у S3\nУВАГА:\nпублікувати квитанцію\nдо отримання HTTP 200\nінакше гонка 404 Not Found!", size=9.5, bold=True, min_w=185, fill=RED_F, stroke=POS, sw=1.4)
    b_st3, _, _ = textbox(122, 350, "Отримання ETag\nФормування квитанції\nз лімітом TTL", size=9.5, min_w=185, fill=GREEN_F, stroke=FIELD)
    f.extend([b_st1, b_st2, b_st3])

    f.append(arrow(235, 205, 260, 205, color=LINE, sw=1.8))

    # Колонка 2: Транзит та споживання
    f.append(rect(265, 55, 215, 355, fill=GRAY_F, stroke=LINE, sw=1.2, rx=6))
    f.append(text(372, 80, "2. Черга та читання", size=11, bold=True, color=INK))
    b_tr1, _, _ = textbox(372, 140, "Публікація в брокер\n(Kafka / RabbitMQ)\nРозмір: сотні байтів\nВисока швидкість", size=9.5, min_w=185, fill=WARN_F, stroke="#d35400")
    b_tr2, _, _ = textbox(372, 245, "Вичитка споживачем\nПеревірка фільтрів.\nЯкщо потрібно тіло:\nGET s3://bucket/key", size=9.5, min_w=185, fill=BLUE_F, stroke=NEG)
    b_tr3, _, _ = textbox(372, 350, "Верифікація цілісності:\nsha256(data) ==\nclaim.content_sha256\nІдемпотентна обробка", size=9.5, bold=True, min_w=185, fill=GREEN_F, stroke=FIELD)
    f.extend([b_tr1, b_tr2, b_tr3])

    f.append(arrow(485, 205, 510, 205, color=LINE, sw=1.8))

    # Колонка 3: Три стратегії очищення (Garbage Collection)
    f.append(rect(515, 55, 430, 355, fill=GRAY_F, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(730, 80, "3. Стратегії інвалідації та прибирання сміття (GC)", size=11.5, bold=True, color=FIELD))

    # Стратегія А: Авто-TTL
    b_gc1, _, _ = textbox(730, 135, "А. Політика життєвого циклу сховища (S3 Lifecycle TTL)\nБакет автоматично видаляє об'єкти через N днів (наприклад, 7 днів).\nНайпростіша та найнадійніша схема: блоби-сироти видаляються автоматично.", size=9, min_w=395, pad=6, fill=GREEN_F, stroke=FIELD)

    # Стратегія Б: Явне видалення останнім споживачем
    b_gc2, _, _ = textbox(730, 225, "Б. Видалення споживачем (Explicit Consumer Cleanup)\nСпоживач надсилає DELETE у сховище після успішного збереження результату.\nНебезпека: при багатьох підписниках (Pub/Sub) перший споживач\nвидалить дані, зламавши обробку для інших підписників!", size=9, min_w=395, pad=6, fill=RED_F, stroke=POS)

    # Стратегія В: Асенізатор за Tombstone подіями
    b_gc3, _, _ = textbox(730, 330, "В. Демон-асенізатор (Janitor / Tombstone Compaction)\nСпоживачі публікують подію завершення 'TaskCompleted' у службовий топік.\nОкремий фоновий сервіс зіставляє підтвердження і видаляє блоб з S3,\nколи всі зареєстровані споживачі відзвітували про успіх.", size=9, min_w=395, pad=6, fill=BLUE_F, stroke=NEG)

    f.extend([b_gc1, b_gc2, b_gc3])

    render(out("claim-check-lifecycle-gc.svg"), W, H, *f)


# ── 3. inline-vs-claim-check-tradeoff: Порівняння та компроміси ─────────────
def fig_inline_vs_claim_check_tradeoff():
    W, H = 960, 440
    f = []

    f.append(text(480, 26, "Компроміси архітектури: пряма передача (Inline) проти Claim Check", size=13.5, bold=True, color=INK))

    # Ліва колонка: Inline (пряме повідомлення через брокер)
    f.append(rect(15, 55, 455, 365, fill=GRAY_F, stroke=POS, sw=1.4, rx=8))
    f.append(text(242, 80, "Пряма передача в брокер (Inline Payload)", size=12, bold=True, color=POS))

    b_in1, _, _ = textbox(242, 130, "Затримка p99: Мінімальна (0.5 – 2 мс)\nНемає додаткових мережевих звернень до зовнішніх баз чи S3", size=9.5, min_w=415, fill=GREEN_F, stroke=FIELD)
    b_in2, _, _ = textbox(242, 205, "Використання RAM брокера: Критичне\n10 000 повідомлень по 20 МБ = 200 ГБ буферів JVM/ОС\nРизик аварійного завершення OOM Kill та тривалих GC-пауз", size=9.5, min_w=415, fill=RED_F, stroke=POS)
    b_in3, _, _ = textbox(242, 285, "Трафік при 1:N розсилці (Pub/Sub): Неефективний\nДля 10 підписників брокер пересилає 10 x 20 МБ = 200 МБ через NIC,\nнавіть якщо 9 підписників лише фільтрують подію за заголовком", size=9.5, min_w=415, fill=RED_F, stroke=POS)
    b_in4, _, _ = textbox(242, 365, "Оптимально для: Дрібних подій (< 64–256 КБ),\nсенсорної телеметрії, транзакційних повідомлень стану", size=9.5, bold=True, min_w=415, fill=FILL, stroke=LINE)
    f.extend([b_in1, b_in2, b_in3, b_in4])

    # Права колонка: Claim Check
    f.append(rect(490, 55, 455, 365, fill=GRAY_F, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(717, 80, "Шаблон квитанції (Claim Check Pattern)", size=12, bold=True, color=FIELD))

    b_cc1, _, _ = textbox(717, 130, "Затримка p99: Вища (25 – 80 мс)\nДодає 2 HTTP-запити через мережу (PUT у сховище + GET споживачем)", size=9.5, min_w=415, fill=WARN_F, stroke="#d35400")
    b_cc2, _, _ = textbox(717, 205, "Використання RAM брокера: Мінімальне\nУ черзі знаходяться лише дескриптори по 400 байтів.\nБрокер стабільно тримає мільйони повідомлень у пам'яті", size=9.5, min_w=415, fill=GREEN_F, stroke=FIELD)
    b_cc3, _, _ = textbox(717, 285, "Трафік при 1:N розсилці (Pub/Sub): Оптимальний\nБрокер пересилає лише 10 x 400 Б = 4 КБ.\nТіло 20 МБ завантажує виключно 1 зацікавлений воркер", size=9.5, min_w=415, fill=GREEN_F, stroke=FIELD)
    b_cc4, _, _ = textbox(717, 365, "Оптимально для: Важких блобів (медіа, PDF, XML-вивантаження,\nнавчальні матриці ML), пакетів > 256 КБ, аудіо/відео фрагментів", size=9.5, bold=True, min_w=415, fill=GREEN_F, stroke=FIELD)
    f.extend([b_cc1, b_cc2, b_cc3, b_cc4])

    render(out("inline-vs-claim-check-tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_claim_check_architecture()
    fig_claim_check_lifecycle()
    fig_inline_vs_claim_check_tradeoff()
    print("Усі фігури Claim Check успішно згенеровано.")
