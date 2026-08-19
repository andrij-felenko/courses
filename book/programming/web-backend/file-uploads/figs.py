# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Буферизація проти потокового парсингу ──────────────────────────
def fig_multipart_stream():
    W, H = 880, 490
    frags = []
    frags.append(text(W / 2, 28, "Буферизація проти потокового парсингу multipart/form-data", size=16, bold=True))
    frags.append(text(W / 2, 48, "накопичення всього тіла в пам'яті (O(N)) проти кінцевого автомата на фіксованому буфері (O(1))",
                      size=12, color=MUTED, italic=True))

    frags.append(fitbox(180, 70, 520, 36,
                        "Вхідний HTTP-потік: POST multipart/form-data (100 паралельних завантажень по 500 МБ)",
                        size=11, fill=FILL, stroke=INK, sw=1.5))

    panels = [
        (35, POS, "Наївна буферизація (в оперативній пам'яті)", "#fdf2f2",
         [
             ("Сервер зчитує весь потік у пам'ять до кінця", "500 МБ на з'єднання"),
             ("100 активних клієнтів тримають пам'ять", "50 ГБ споживання RAM"),
             ("Затримка першого байту для обробки", "Повна тривалість мережі"),
             ("Наслідок: вичерпання RAM і падіння", "OOM Killer гасить бекенд")
         ],
         "Пам'ять: O(N · розмір)   ✗  Вразливість до DoS"),
        (455, FIELD, "Потоковий розбір (Streaming State Machine)", "#f0fdf4",
         [
             ("Фіксований буфер чанка в пам'яті", "64 КБ на з'єднання"),
             ("Кінцевий автомат шукає boundary", "Обробка байтів на льоту"),
             ("Потоковий запис у диск або S3", "Backpressure контролює потік"),
             ("100 активних клієнтів споживають", "Всього 6.4 МБ RAM")
         ],
         "Пам'ять: O(1)   ✓  Стабільність під будь-яким навантаженням")
    ]

    for px, col, header, resfill, rows, footer in panels:
        frags.append(rect(px, 120, 390, 345, fill=BG, stroke=col, sw=1.8))
        frags.append(text(px + 195, 145, header, size=12, bold=True, color=col))
        ry = 165
        for title, detail in rows:
            frags.append(fitbox(px + 15, ry, 360, 44, f"{title} — {detail}", size=10.5, fill=FILL, stroke=MUTED, sw=1.2))
            ry += 52
        frags.append(fitbox(px + 15, 385, 360, 60, footer, size=11.5, fill=resfill, stroke=col, sw=1.8, bold=True, color=col))

    render(os.path.join(IMG, "multipart-stream.svg"), W, H, *frags)


# ── Фігура 2: Direct-to-Cloud архітектура ────────────────────────────────────
def fig_direct_to_cloud():
    W, H = 880, 480
    frags = []
    frags.append(text(W / 2, 28, "Архітектура прямого завантаження в хмару (Direct-to-Cloud)", size=16, bold=True))
    frags.append(text(W / 2, 48, "розвантаження бекенду: трафік важких файлів іде напряму в S3/GCS через підписаний URL",
                      size=12, color=MUTED, italic=True))

    actors = [
        (40, 75, 200, 40, "Клієнт (Браузер / Додаток)", FILL, INK),
        (340, 75, 200, 40, "Бекенд (API Сервер)", FILL, INK),
        (640, 75, 200, 40, "Хмарне сховище (S3 / GCS)", FILL, INK),
    ]
    for ax, ay, aw, ah, label, f, s in actors:
        frags.append(rect(ax, ay, aw, ah, fill=f, stroke=s, sw=1.6))
        frags.append(text(ax + aw/2, ay + 25, label, size=12, bold=True, color=s))

    for cx in [140, 440, 740]:
        frags.append(f'<line x1="{cx}" y1="125" x2="{cx}" y2="445" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # Крок 1: Запит на квиток завантаження
    frags.append(arrow(140, 150, 440, 150, color=INK, sw=1.5))
    frags.append(text(290, 142, "1. POST /api/uploads/ticket (розмір, MIME, метадані)", size=10, color=INK))

    frags.append(fitbox(360, 168, 160, 32, "Перевірка прав + Pre-signed URL", size=9.5, fill="#fef3c7", stroke="#d97706", sw=1.2))

    # Крок 2: Відповідь із тимчасовим URL
    frags.append(arrow(440, 220, 140, 220, color=INK, sw=1.5))
    frags.append(text(290, 212, "2. Відповідь: 200 OK { upload_url, file_id, ttl: 900s }", size=10, color=INK))

    # Крок 3: Прямий upload у сховище
    frags.append(arrow(140, 275, 740, 275, color=FIELD, sw=2.0))
    frags.append(text(440, 265, "3. PUT https://s3.amazonaws.com/... (прямий потік байтів)", size=10.5, color=FIELD, bold=True))

    # Крок 4: Підтвердження від S3 клієнту
    frags.append(arrow(740, 330, 140, 330, color=MUTED, sw=1.3))
    frags.append(text(440, 322, "4. HTTP 200 OK від S3 (ETag об'єкта)", size=10, color=MUTED))

    # Крок 5: Повідомлення бекенду про завершення
    frags.append(arrow(140, 380, 440, 380, color=INK, sw=1.5))
    frags.append(text(290, 372, "5. POST /api/uploads/complete { file_id, etag }", size=10, color=INK))

    # Крок 6: Воркер бере в обробку
    frags.append(arrow(440, 415, 640, 415, color=NEG, sw=1.5))
    frags.append(text(540, 407, "6. Подія в чергу задач (постобробка)", size=10, color=NEG))

    render(os.path.join(IMG, "direct-to-cloud.svg"), W, H, *frags)


# ── Фігура 3: TUS Протокол і відновлення зв'язку ─────────────────────────────
def fig_tus_state_machine():
    W, H = 880, 490
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл протоколу відновлюваного завантаження TUS", size=16, bold=True))
    frags.append(text(W / 2, 48, "створення ресурсу, відправка частин через PATCH та узгодження зсуву після обриву",
                      size=12, color=MUTED, italic=True))

    frags.append(rect(60, 70, 200, 38, fill=FILL, stroke=INK, sw=1.5))
    frags.append(text(160, 94, "Клієнт (TUS Client)", size=12, bold=True))

    frags.append(rect(620, 70, 200, 38, fill=FILL, stroke=INK, sw=1.5))
    frags.append(text(720, 94, "TUS-сервер (Resumable Upload)", size=12, bold=True))

    frags.append(f'<line x1="160" y1="115" x2="160" y2="455" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')
    frags.append(f'<line x1="720" y1="115" x2="720" y2="455" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # Фаза 1: Створення сесії
    frags.append(arrow(160, 140, 720, 140, color=INK, sw=1.5))
    frags.append(text(440, 132, "1. POST /files (Upload-Length: 100000000, Tus-Resumable: 1.0.0)", size=10, color=INK))

    frags.append(arrow(720, 175, 160, 175, color=INK, sw=1.5))
    frags.append(text(440, 167, "2. 201 Created (Location: /files/upload_987, Upload-Offset: 0)", size=10, color=INK))

    # Фаза 2: Перший чанк
    frags.append(arrow(160, 215, 720, 215, color=FIELD, sw=1.8))
    frags.append(text(440, 207, "3. PATCH /files/upload_987 (Upload-Offset: 0, 40 МБ даних)", size=10, color=FIELD, bold=True))

    frags.append(arrow(720, 250, 160, 250, color=FIELD, sw=1.5))
    frags.append(text(440, 242, "4. 204 No Content (Upload-Offset: 41943040)", size=10, color=FIELD))

    # Аварія мережі
    frags.append(fitbox(220, 268, 440, 32, "МЕРЕЖЕВИЙ ЗБІЙ: Розрив TCP під час відправки наступного блоку", size=10, fill="#fee2e2", stroke=POS, sw=1.5, color=POS, bold=True))

    # Фаза 3: Відновлення зв'язку
    frags.append(arrow(160, 325, 720, 325, color=NEG, sw=1.5))
    frags.append(text(440, 317, "5. HEAD /files/upload_987 (Запит поточного зсуву)", size=10, color=NEG))

    frags.append(arrow(720, 360, 160, 360, color=NEG, sw=1.5))
    frags.append(text(440, 352, "6. 200 OK (Upload-Offset: 41943040, Upload-Length: 100000000)", size=10, color=NEG))

    # Фаза 4: Докачування решти
    frags.append(arrow(160, 400, 720, 400, color=FIELD, sw=1.8))
    frags.append(text(440, 392, "7. PATCH /files/upload_987 (Upload-Offset: 41943040, залишок 60 МБ)", size=10, color=FIELD, bold=True))

    frags.append(arrow(720, 435, 160, 435, color=FIELD, sw=1.5))
    frags.append(text(440, 427, "8. 204 No Content (Upload-Offset: 100000000 — Завантаження завершено)", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "tus-state-machine.svg"), W, H, *frags)


# ── Фігура 4: Пайплайн постобробки ───────────────────────────────────────────
def fig_processing_pipeline():
    W, H = 880, 480
    frags = []
    frags.append(text(W / 2, 28, "Асинхронний конвеєр постобробки та захисту файлів", size=16, bold=True))
    frags.append(text(W / 2, 48, "п'ять обов'язкових етапів ізоляції, очищення, оптимізації та дедуплікації",
                      size=12, color=MUTED, italic=True))

    stages = [
        (40, 80, 145, "1. Карантин", "S3 Quarantine Bucket",
         ["Тимчасове сховище", "Ізоляція від публіки", "TTL об'єкта 24 години"], "#fef3c7", "#d97706"),
        (205, 80, 145, "2. Валідація", "Magic Bytes & MIME",
         ["Аналіз сигнатури", "Відкидання розширень", "Перевірка розмірів"], "#e0e7ff", "#4338ca"),
        (370, 80, 145, "3. Антивірус", "ClamAV Scanner",
         ["Потокове сканування", "Евристичний аналіз", "Блокування макросів"], "#fee2e2", POS),
        (535, 80, 145, "4. Оптимізація", "WebP / AVIF Worker",
         ["Стрип EXIF/GPS", "Генерація thumbnail", "Асинхронне стиснення"], "#f3e8ff", "#7e22ce"),
        (700, 80, 145, "5. Фіналізація", "SHA-256 Storage",
         ["Дедуплікація хешу", "Перенесення в Prod S3", "Запис у базу даних"], "#ecfdf5", FIELD),
    ]

    for sx, sy, sw, header, sub, bullets, bgcol, strkcol in stages:
        frags.append(rect(sx, sy, sw, 300, fill=BG, stroke=strkcol, sw=1.6))
        frags.append(fitbox(sx + 5, sy + 10, sw - 10, 26, header, size=11, fill=bgcol, stroke=strkcol, sw=1.2, color=strkcol, bold=True))
        frags.append(text(sx + sw/2, sy + 52, sub, size=9.5, color=MUTED, italic=True))
        by = sy + 75
        for b in bullets:
            frags.append(fitbox(sx + 8, by, sw - 16, 36, b, size=9, fill=FILL, stroke=MUTED, sw=1.0))
            by += 44

    for ax in [188, 353, 518, 683]:
        frags.append(arrow(ax - 3, 220, ax + 14, 220, color=INK, sw=1.8))

    frags.append(fitbox(40, 400, 805, 52,
                        "Інваріант безпеки: будь-яка невдача (вірус, невідповідність сигнатури) миттєво видаляє об'єкт із карантину та повідомляє клієнта",
                        size=11, fill=FILL, stroke=INK, sw=1.5))

    render(os.path.join(IMG, "processing-pipeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_multipart_stream()
    fig_direct_to_cloud()
    fig_tus_state_machine()
    fig_processing_pipeline()
    print("Всі фігури згенеровано успішно.")
