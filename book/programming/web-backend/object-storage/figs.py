# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Порівняння парадигм зберігання даних ───────────────────────────
def fig_storage_paradigms():
    W, H = 900, 480
    frags = []
    frags.append(text(W / 2, 28, "Порівняння парадигм зберігання: блокове, файлове та об'єктне", size=16, bold=True))
    frags.append(text(W / 2, 48, "структура організації, інтерфейс доступу, метадані та межі масштабування",
                      size=12, color=MUTED, italic=True))

    columns = [
        (30, "Блокове сховище (Block)", "SAN / NVMe / AWS EBS", "#1e3a8a", "#eff6ff",
         [
             ("Одиниця даних", "Фіксовані сектори (блоки 4–64 КБ)"),
             ("Адресація", "LBA (Logical Block Address) / LUN"),
             ("Метадані", "Відсутні (лише сирі байти)"),
             ("Інтерфейс", "NVMe-oF, iSCSI, Fibre Channel"),
             ("Керування", "Операційна система монтує диск"),
             ("Особливість", "Низька затримка (<1 мс), високий IOPS"),
             ("Масштаб", "Обмежений розміром одного тому")
         ],
         "Сфера: бази даних, системні диски ОС"),

        (320, "Файлове сховище (File)", "NAS / NFS / SMB / CephFS", "#065f46", "#ecfdf5",
         [
             ("Одиниця даних", "Файли в ієрархії каталогів"),
             ("Адресація", "Ієрархічний шлях (/a/b/c/file.txt)"),
             ("Метадані", "Фіксовані POSIX (inode, права, mtime)"),
             ("Інтерфейс", "POSIX API (open, read, write, seek)"),
             ("Керування", "Спільне мережеве монтування (NFS)"),
             ("Особливість", "Блокування файлів, дерево каталогів"),
             ("Масштаб", "Глухий кут на мільйонах файлів")
         ],
         "Сфера: спільні мережеві теки, legacy"),

        (610, "Об'єктне сховище (Object)", "AWS S3 / GCS / Ceph RGW / MinIO", "#92400e", "#fffbeb",
         [
             ("Одиниця даних", "Незмінні блоби (WORM)"),
             ("Адресація", "Плаский простір: Bucket + Key"),
             ("Метадані", "Довільні ключ-значення (x-amz-meta-*)"),
             ("Інтерфейс", "HTTP REST API (GET, PUT, DELETE)"),
             ("Керування", "Мережевий сервіс без монтування"),
             ("Особливість", "Кодування стиранням, Presigned URL"),
             ("Масштаб", "Необмежений петабайтний масштаб")
         ],
         "Сфера: веб-медіа, бекапи, Data Lake")
    ]

    for px, title, subtitle, col, bgcol, rows, footer in columns:
        frags.append(rect(px, 72, 260, 390, fill=bgcol, stroke=col, sw=1.6))
        frags.append(text(px + 130, 94, title, size=12, bold=True, color=col))
        frags.append(text(px + 130, 110, subtitle, size=10, color=MUTED, italic=True))
        frags.append(line(px + 10, 120, px + 250, 120, color=col, sw=1.0))

        ry = 132
        for lbl, val in rows:
            frags.append(fitbox(px + 10, ry, 240, 32, f"{lbl}: {val}", size=9.5, fill=BG, stroke=MUTED, sw=1.0))
            ry += 38

        frags.append(fitbox(px + 10, 408, 240, 42, footer, size=10, fill=BG, stroke=col, sw=1.4, bold=True, color=col))

    render(os.path.join(IMG, "storage-paradigms.svg"), W, H, *frags)


# ── Фігура 2: Кодування стиранням (Erasure Coding) ───────────────────────────
def fig_erasure_coding():
    W, H = 900, 480
    frags = []
    frags.append(text(W / 2, 28, "Кодування стиранням (Erasure Coding) за схемою RS(4+2)", size=16, bold=True))
    frags.append(text(W / 2, 48, "розбиття об'єкта на K=4 шарди даних та M=2 шарди парності з розподілом по зонах доступності",
                      size=12, color=MUTED, italic=True))

    # Вихідний об'єкт
    frags.append(fitbox(200, 70, 500, 40, "Вхідний об'єкт: video.mp4 (розмір 64 МБ, Payload)", size=12, fill=FILL, stroke=INK, sw=1.8, bold=True))

    frags.append(arrow(320, 110, 220, 155, color=INK, sw=1.5))
    frags.append(arrow(450, 110, 450, 155, color=INK, sw=1.5))
    frags.append(arrow(580, 110, 680, 155, color=INK, sw=1.5))

    # Блок кодування
    frags.append(fitbox(150, 155, 600, 34, "Матриця генератора Вандермонда GF(2⁸): обчислення K=4 чанків даних і M=2 чанків парності", size=10.5, fill="#fef3c7", stroke="#d97706", sw=1.4, bold=True, color="#92400e"))

    # 6 шардів
    shards = [
        (35, 230, "Шард D1 (16 МБ)", "Зона AZ-1 / Вузол 1", "#2563eb", "#eff6ff", "✓ Доступний"),
        (175, 230, "Шард D2 (16 МБ)", "Зона AZ-1 / Вузол 2", "#dc2626", "#fef2f2", "✗ ЗБІЙ ДИСКА"),
        (315, 230, "Шард D3 (16 МБ)", "Зона AZ-2 / Вузол 3", "#2563eb", "#eff6ff", "✓ Доступний"),
        (455, 230, "Шард D4 (16 МБ)", "Зона AZ-2 / Вузол 4", "#2563eb", "#eff6ff", "✓ Доступний"),
        (595, 230, "Парність P1 (16 МБ)", "Зона AZ-3 / Вузол 5", "#dc2626", "#fef2f2", "✗ МЕРЕЖЕВИЙ РОЗРИВ"),
        (735, 230, "Парність P2 (16 МБ)", "Зона AZ-3 / Вузол 6", "#059669", "#ecfdf5", "✓ Доступний")
    ]

    for sx, sy, title, loc, col, bgcol, status in shards:
        frags.append(rect(sx, sy, 130, 110, fill=bgcol, stroke=col, sw=1.5))
        frags.append(text(sx + 65, sy + 22, title, size=10.5, bold=True, color=col))
        frags.append(text(sx + 65, sy + 44, loc, size=9.5, color=MUTED))
        frags.append(line(sx + 8, sy + 58, sx + 122, sy + 58, color=col, sw=0.8))
        frags.append(fitbox(sx + 8, sy + 68, 114, 30, status, size=9.5, fill=BG, stroke=col, sw=1.2, bold=True, color=col))

    # Стрілки збору
    for sx in [100, 380, 520, 800]:
        frags.append(arrow(sx, 340, 450, 395, color="#059669", sw=1.4))

    # Реконструкція
    frags.append(fitbox(150, 395, 600, 68,
                        "Відновлення: вичитано 4 будь-які шарди (D1, D3, D4, P2) з 6\n"
                        "Інверсія матриці підпростору повністю відновлює втрачені D2 та P1 без втрати даних.\n"
                        "Накладні витрати пам'яті: лише 50% (коефіцієнт 1.5× замість 3.0× при 3-кратній реплікації).",
                        size=10.5, fill="#ecfdf5", stroke="#059669", sw=1.6, bold=True, color="#065f46"))

    render(os.path.join(IMG, "erasure-coding-shards.svg"), W, H, *frags)


# ── Фігура 3: Патерн Valet Key та Presigned URL ──────────────────────────────
def fig_presigned_valet_key():
    W, H = 880, 470
    frags = []
    frags.append(text(W / 2, 28, "Архітектура Presigned URL (патерн Valet Key)", size=16, bold=True))
    frags.append(text(W / 2, 48, "делегування операцій запису та читання напряму в об'єктне сховище без навантаження на бекенд",
                      size=12, color=MUTED, italic=True))

    actors = [
        (40, 75, 200, 40, "Клієнт (Web / Mobile App)", FILL, INK),
        (340, 75, 200, 40, "API-сервер (Бекенд)", FILL, INK),
        (640, 75, 200, 40, "Об'єктне сховище (S3 / GCS)", FILL, INK),
    ]
    for ax, ay, aw, ah, label, f, s in actors:
        frags.append(rect(ax, ay, aw, ah, fill=f, stroke=s, sw=1.6))
        frags.append(text(ax + aw/2, ay + 25, label, size=12, bold=True, color=s))

    for cx in [140, 440, 740]:
        frags.append(f'<line x1="{cx}" y1="125" x2="{cx}" y2="445" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # Крок 1: Запит дозволу
    frags.append(arrow(140, 150, 440, 150, color=INK, sw=1.5))
    frags.append(text(290, 142, "1. POST /api/v1/files/ticket { filename, size, mime }", size=10, color=INK))

    # Обчислення HMAC на бекенді
    frags.append(fitbox(350, 168, 180, 32, "Перевірка прав + SigV4 HMAC", size=9.5, fill="#fef3c7", stroke="#d97706", sw=1.2))

    # Крок 2: Відповідь з підписаним URL
    frags.append(arrow(440, 220, 140, 220, color=INK, sw=1.5))
    frags.append(text(290, 212, "2. 200 OK { presigned_url, ttl: 900s, file_id }", size=10, color=INK))

    # Крок 3: Прямий аплоад клієнтом
    frags.append(arrow(140, 275, 740, 275, color=FIELD, sw=2.0))
    frags.append(text(440, 265, "3. PUT https://bucket.s3.amazonaws.com/uuid?X-Amz-Signature=... (двійковий блоб 500 МБ)", size=10, color=FIELD, bold=True))

    # Крок 4: S3 перевіряє підпис і зберігає
    frags.append(arrow(740, 325, 140, 325, color=MUTED, sw=1.3))
    frags.append(text(440, 317, "4. 200 OK (ETag: \"d41d8cd98f00b204e9800998ecf8427e\")", size=10, color=MUTED))

    # Крок 5: Асинхронна подія
    frags.append(arrow(740, 380, 440, 380, color=NEG, sw=1.6))
    frags.append(text(590, 372, "5. S3 Event Notification: s3:ObjectCreated:Put (SQS / Webhook)", size=9.5, color=NEG, bold=True))

    # Крок 6: Воркер бекенду фіксує запис
    frags.append(fitbox(350, 400, 180, 34, "Постобробка та запис у БД", size=9.5, fill="#f0fdf4", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, "presigned-valet-key.svg"), W, H, *frags)


# ── Фігура 4: Життєвий цикл Multipart Upload ─────────────────────────────────
def fig_multipart_lifecycle():
    W, H = 900, 490
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл багаточастинного завантаження (Multipart Upload)", size=16, bold=True))
    frags.append(text(W / 2, 48, "ініціалізація сесії, паралельне передавання частин зі своїми ETag та фінальна збірка маніфесту",
                      size=12, color=MUTED, italic=True))

    frags.append(rect(60, 70, 220, 38, fill=FILL, stroke=INK, sw=1.5))
    frags.append(text(170, 94, "Клієнт / SDK", size=12, bold=True))

    frags.append(rect(620, 70, 220, 38, fill=FILL, stroke=INK, sw=1.5))
    frags.append(text(730, 94, "S3 / Об'єктне сховище", size=12, bold=True))

    frags.append(f'<line x1="170" y1="115" x2="170" y2="465" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')
    frags.append(f'<line x1="730" y1="115" x2="730" y2="465" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # Фаза 1: CreateMultipartUpload
    frags.append(arrow(170, 140, 730, 140, color=INK, sw=1.5))
    frags.append(text(450, 132, "1. POST /bucket/video.mp4?uploads (Ініціалізація завантаження)", size=10, color=INK))

    frags.append(arrow(730, 175, 170, 175, color=INK, sw=1.5))
    frags.append(text(450, 167, "2. 200 OK: <InitiateMultipartUploadResult><UploadId>abc123xyz</UploadId>", size=9.5, color=INK))

    # Фаза 2: Parallel UploadPart
    frags.append(arrow(170, 215, 730, 215, color=FIELD, sw=1.8))
    frags.append(text(450, 207, "3. PUT /bucket/video.mp4?partNumber=1&uploadId=abc123xyz (Чанк 1: 10 МБ)", size=10, color=FIELD, bold=True))
    frags.append(arrow(730, 245, 170, 245, color=FIELD, sw=1.5))
    frags.append(text(450, 237, "4. 200 OK (ETag: \"hash_1\")", size=9.5, color=FIELD))

    frags.append(arrow(170, 280, 730, 280, color=FIELD, sw=1.8))
    frags.append(text(450, 272, "5. PUT /bucket/video.mp4?partNumber=2&uploadId=abc123xyz (Чанк 2: 10 МБ, паралельно)", size=10, color=FIELD, bold=True))
    frags.append(arrow(730, 310, 170, 310, color=FIELD, sw=1.5))
    frags.append(text(450, 302, "6. 200 OK (ETag: \"hash_2\")", size=9.5, color=FIELD))

    # Фаза 3: CompleteMultipartUpload
    frags.append(arrow(170, 355, 730, 355, color="#7c3aed", sw=1.8))
    frags.append(text(450, 347, "7. POST /bucket/video.mp4?uploadId=abc123xyz (Маніфест: [(1, hash_1), (2, hash_2)])", size=9.5, color="#7c3aed", bold=True))

    frags.append(fitbox(340, 375, 220, 32, "Склеювання метаданих об'єкта", size=9.5, fill="#f5f3ff", stroke="#7c3aed", sw=1.2))

    frags.append(arrow(730, 425, 170, 425, color="#7c3aed", sw=1.8))
    frags.append(text(450, 417, "8. 200 OK: <CompleteMultipartUploadResult><ETag>\"composite_hash-2\"</ETag>", size=9.5, color="#7c3aed", bold=True))

    # Аварійне прибирання
    frags.append(fitbox(200, 440, 500, 24, "Правило життєвого циклу: AbortIncompleteMultipartUpload через 7 днів очищує кинуті частини", size=9.5, fill="#fee2e2", stroke=POS, sw=1.2, color=POS))

    render(os.path.join(IMG, "multipart-lifecycle.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_storage_paradigms()
    fig_erasure_coding()
    fig_presigned_valet_key()
    fig_multipart_lifecycle()
    print("All figures generated successfully.")
