# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Життєвий цикл часткового запиту Range і відповіді 206 ───────────
def fig_range_lifecycle():
    W, H = 880, 480
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл HTTP Range-запиту: зріз байтів без передачі всього файлу", size=16, bold=True))
    frags.append(text(W / 2, 48, "клієнт запитує точний діапазон байтів, сервер повертає статус 206 Partial Content та Content-Range",
                      size=12, color=MUTED, italic=True))

    # Схема ресурсу 50 МБ
    frags.append(rect(60, 75, 760, 50, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(rect(60, 75, 140, 50, fill="#e2e8f0", stroke="none", rx=0))
    frags.append(rect(200, 75, 180, 50, fill="#dbeafe", stroke=NEG, sw=2, rx=0))
    frags.append(rect(380, 75, 440, 50, fill="#e2e8f0", stroke="none", rx=0))

    frags.append(text(130, 105, "0 .. 1 048 575 (1 МБ)", size=11, color=MUTED))
    frags.append(text(290, 100, "Запитаний діапазон: 1 048 576 .. 2 097 151", size=11, bold=True, color=NEG))
    frags.append(text(290, 116, "Розмір: 1 МБ (1 048 576 байтів)", size=10.5, color=NEG))
    frags.append(text(600, 105, "2 097 152 .. 52 428 799 (решта 48 МБ не зчитується з диска)", size=11, color=MUTED))

    # Ліва панель: Клієнт
    frags.append(rect(60, 150, 360, 305, fill=BG, stroke=NEG, sw=1.8, rx=6))
    frags.append(text(240, 175, "Запит клієнта (HTTP Request)", size=13, bold=True, color=NEG))

    frags.append(fitbox(75, 195, 330, 38, "GET /media/video.mp4 HTTP/1.1", size=11, fill="#eff6ff", stroke=NEG, sw=1.2, bold=True))
    frags.append(fitbox(75, 240, 330, 38, "Host: cdn.example.com", size=11, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(75, 285, 330, 48, "Range: bytes=1048576-2097151\n(запит діапазону [start-end] включно)", size=10.5, fill="#fef3c7", stroke="#d97706", sw=1.5, bold=True))
    frags.append(fitbox(75, 340, 330, 38, "User-Agent: MediaStreamer/2.0", size=11, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(75, 385, 330, 55, "Результат: запитано рівно 1 048 576 байтів\n(зміщення 1 МБ від початку файлу)", size=10.5, fill="#f0fdf4", stroke=FIELD, sw=1.2))

    # Стрілка між клієнтом і сервером
    frags.append(arrow(425, 290, 455, 290, color=LINE, sw=2))

    # Права панель: Сервер
    frags.append(rect(460, 150, 360, 305, fill=BG, stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(640, 175, "Відповідь сервера (HTTP Response)", size=13, bold=True, color=FIELD))

    frags.append(fitbox(475, 195, 330, 38, "HTTP/1.1 206 Partial Content", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True))
    frags.append(fitbox(475, 240, 330, 44, "Content-Range: bytes 1048576-2097151/52428800\n(діапазон та повний розмір ресурсу)", size=10.5, fill="#eff6ff", stroke=NEG, sw=1.2, bold=True))
    frags.append(fitbox(475, 290, 330, 38, "Content-Length: 1048576 (розмір тіла відповіді)", size=10.5, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(475, 335, 330, 38, "Content-Type: video/mp4", size=11, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(475, 380, 330, 60, "Accept-Ranges: bytes\n(підтвердження підтримки байтових зрізів)\n+ Тіло: двійковий зріз 1 048 576 байтів", size=10.5, fill="#f0fdf4", stroke=FIELD, sw=1.2, bold=True))

    render(os.path.join(IMG, "range-lifecycle.svg"), W, H, *frags)


# ── Фігура 2: Дерево умовного запиту If-Range ─────────────────────────────────
def fig_if_range_condition():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 28, "Умовне докачування через заголовок If-Range", size=16, bold=True))
    frags.append(text(W / 2, 48, "захист від пошкодження файлу при склеюванні частин з різних версій ресурсу",
                      size=12, color=MUTED, italic=True))

    # Клієнт надсилає запит
    frags.append(rect(190, 75, 500, 65, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(440, 98, "Клієнт надсилає запит на докачування:", size=12, bold=True))
    frags.append(text(440, 122, 'Range: bytes=5242880-  |  If-Range: "v1.2-hash98a"', size=11, bold=True, color=NEG))

    # Стрілка вниз до перевірки
    frags.append(arrow(440, 140, 440, 175, color=LINE, sw=2))

    # Блок перевірки на сервері (ромбоподібна логіка у прямокутнику)
    frags.append(rect(240, 175, 400, 60, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(440, 200, "Сервер порівнює валідатор If-Range:", size=12, bold=True, color="#d97706"))
    frags.append(text(440, 220, "Чи збігається сильний ETag або Last-Modified файлу?", size=11))

    # Стрілка вліво: Збіг (Успіх)
    frags.append(arrow(320, 235, 230, 280, color=FIELD, sw=2))
    frags.append(text(240, 255, "ТАК (файл той самий)", size=11, bold=True, color=FIELD))

    # Стрілка вправо: Зміна (Невідповідність)
    frags.append(arrow(560, 235, 650, 280, color=POS, sw=2))
    frags.append(text(640, 255, "НІ (файл оновився)", size=11, bold=True, color=POS))

    # Ліва картка: 206 Partial Content
    frags.append(rect(40, 285, 380, 195, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(230, 312, "✓ Успішне докачування (206 Partial Content)", size=12, bold=True, color=FIELD))
    frags.append(fitbox(55, 330, 350, 38, "HTTP/1.1 206 Partial Content", size=11, fill=BG, stroke=FIELD, sw=1.2, bold=True))
    frags.append(fitbox(55, 375, 350, 44, "Content-Range: bytes 5242880-10485759/10485760\nТіло: рівно друга половина файлу (5 МБ)", size=10.5, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(55, 425, 350, 44, "Клієнт дописує отриманий зріз до наявних 5 МБ.\nЦілісність даних збережена.", size=10.5, fill="#dcfce7", stroke=FIELD, sw=1.2))

    # Права картка: 200 OK
    frags.append(rect(460, 285, 380, 195, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(650, 312, "✗ Автоматичний перезапуск (200 OK)", size=12, bold=True, color=POS))
    frags.append(fitbox(475, 330, 350, 38, "HTTP/1.1 200 OK (нова версія)", size=11, fill=BG, stroke=POS, sw=1.2, bold=True))
    frags.append(fitbox(475, 375, 350, 44, "Content-Length: 12582912 | ETag: \"v2.0-newhash\"\nТіло: увесь новий файл з 0-го байта (12 МБ)", size=10.5, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(475, 425, 350, 44, "Клієнт перезаписує файл заново.\nЗапобігає пошкодженню файлу з різних частин.", size=10.5, fill="#fee2e2", stroke=POS, sw=1.2))

    render(os.path.join(IMG, "if-range-condition.svg"), W, H, *frags)


# ── Фігура 3: Структура multipart/byteranges ─────────────────────────────────
def fig_multipart_byteranges():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 28, "Анатомія відповіді з кількома діапазонами: multipart/byteranges", size=16, bold=True))
    frags.append(text(W / 2, 48, "передача кількох розрізнених зрізів байтів в одному HTTP-з'єднанні через MIME-межі",
                      size=12, color=MUTED, italic=True))

    # Запит
    frags.append(rect(60, 75, 760, 55, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(440, 97, "Клієнт запитує 3 розрізнені зрізи:", size=11.5, bold=True, color=NEG))
    frags.append(text(440, 117, "GET /archive.tar HTTP/1.1  |  Range: bytes=0-499, 1500-1999, 8000-8499", size=11, bold=True))

    # Відповідь: контейнер multipart
    frags.append(rect(60, 145, 760, 335, fill=BG, stroke=LINE, sw=1.5, rx=6))

    # Головні заголовки
    frags.append(fitbox(75, 160, 730, 42,
                         "HTTP/1.1 206 Partial Content\nContent-Type: multipart/byteranges; boundary=THIS_STRING_SEPARATES",
                         size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True))

    # 3 блоки частин
    parts = [
        (75, 215, 235, "Частина 1: 0..499 (500 байтів)", "--THIS_STRING_SEPARATES\nContent-Type: application/x-tar\nContent-Range: bytes 0-499/100000\n\n[500 сирих байтів файлу]"),
        (322, 215, 235, "Частина 2: 1500..1999 (500 байтів)", "--THIS_STRING_SEPARATES\nContent-Type: application/x-tar\nContent-Range: bytes 1500-1999/100000\n\n[500 сирих байтів файлу]"),
        (570, 215, 235, "Частина 3: 8000..8499 (500 байтів)", "--THIS_STRING_SEPARATES\nContent-Type: application/x-tar\nContent-Range: bytes 8000-8499/100000\n\n[500 сирих байтів файлу]")
    ]

    for px, py, pw, header, content in parts:
        frags.append(rect(px, py, pw, 205, fill="#f8fafc", stroke=NEG, sw=1.2, rx=4))
        frags.append(text(px + pw / 2, py + 20, header, size=11, bold=True, color=NEG))
        frags.append(fitbox(px + 10, py + 35, pw - 20, 155, content, size=10, fill=BG, stroke=MUTED, sw=1))

    # Фінальна межа
    frags.append(fitbox(75, 430, 730, 36,
                         "--THIS_STRING_SEPARATES--  (фінальний роздільник із двома дефісами в кінці)",
                         size=11, fill="#fef3c7", stroke="#d97706", sw=1.5, bold=True))

    render(os.path.join(IMG, "multipart-byteranges.svg"), W, H, *frags)


# ── Фігура 4: Range DoS атака та алгоритм коалесценції ─────────────────────────
def fig_range_dos_coalescing():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 28, "Вразливість Range DoS (Apache Killer) та захист через коалесценцію", size=16, bold=True))
    frags.append(text(W / 2, 48, "шкідливий запит десятків тисяч зрізів проти дедуплікації та об'єднання діапазонів на сервері",
                      size=12, color=MUTED, italic=True))

    # Ліва колонка: Атака
    frags.append(rect(40, 75, 385, 395, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(232, 102, "Атака: Перевантаження діапазонами (CVE-2011-3192)", size=11.5, bold=True, color=POS))

    frags.append(fitbox(55, 120, 355, 55, "Range: bytes=0-,5-1,5-2,5-3,5-4,...\n(зловмисник передає тисячі перекритих зрізів)", size=10.5, fill=BG, stroke=POS, sw=1.2, bold=True))
    frags.append(fitbox(55, 185, 355, 45, "Сервер генерує тисячі MIME-заголовків\nрозмір відповіді в 100 разів більший за файл", size=10, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(55, 240, 355, 55, "Диск виконує тисячі випадкових seek()\nоперативна пам'ять вичерпується буферами MIME", size=10, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(55, 305, 355, 45, "Наслідок: 100% завантаження CPU і RAM\nробочі процеси вебсервера блокуються", size=10, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(55, 360, 355, 95, "Підсумок наївного сервера:\n✗ Повне вичерпання ресурсів пам'яті\n✗ Відмова в обслуговуванні легітимних клієнтів", size=11, fill="#fee2e2", stroke=POS, sw=1.5, bold=True, color=POS))

    # Права колонка: Захист
    frags.append(rect(455, 75, 385, 395, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(647, 102, "Захист: Валідація та коалесценція (Range Coalescing)", size=11.5, bold=True, color=FIELD))

    frags.append(fitbox(470, 120, 355, 50, "1. Ліміт кількості діапазонів (Max Ranges)\nNGINX: max 1 range, Apache: max 5-10 ranges", size=10.5, fill=BG, stroke=FIELD, sw=1.2, bold=True))
    frags.append(fitbox(470, 180, 355, 50, "2. Сортування та злиття (Coalescing)\n[0..100] + [50..200] автоматично зливаються в [0..200]", size=10.5, fill=BG, stroke=FIELD, sw=1.2, bold=True))
    frags.append(fitbox(470, 240, 355, 50, "3. Відкидання некоректних діапазонів\nstart > end або start >= total → 416 Range Not Satisfiable", size=10.5, fill=BG, stroke=FIELD, sw=1.2, bold=True))
    frags.append(fitbox(470, 300, 355, 50, "4. Поріг накладних витрат MIME\nякщо розмір MIME перевищує виграш — повернення 200 OK", size=10.5, fill=BG, stroke=FIELD, sw=1.2, bold=True))
    frags.append(fitbox(470, 360, 355, 95, "Підсумок захищеного сервера:\n✓ Стабільне споживання O(1) ресурсів\n✓ Повний захист від атак вичерпання пам'яті", size=11, fill="#dcfce7", stroke=FIELD, sw=1.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "range-dos-coalescing.svg"), W, H, *frags)


# ── Фігура 5: Перемотування відео через MP4 moov і байтові діапазони ───────────
def fig_media_seeking_moov():
    W, H = 880, 480
    frags = []
    frags.append(text(W / 2, 28, "Перемотування медіа: індексація MP4 moov та байтові діапазони", size=16, bold=True))
    frags.append(text(W / 2, 48, "браузер зчитує метадані з початку файлу, обчислює зміщення кадру і запитує потрібний зріз",
                      size=12, color=MUTED, italic=True))

    # Схема файлу MP4 2 ГБ
    frags.append(rect(60, 75, 760, 50, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(rect(60, 75, 120, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    frags.append(rect(180, 75, 340, 50, fill="#e2e8f0", stroke="none", rx=0))
    frags.append(rect(520, 75, 150, 50, fill="#dbeafe", stroke=NEG, sw=2, rx=0))
    frags.append(rect(670, 75, 150, 50, fill="#e2e8f0", stroke="none", rx=0))

    frags.append(text(120, 100, "moov atom (1.2 МБ)", size=11, bold=True, color="#d97706"))
    frags.append(text(120, 116, "індекс таймкодів", size=9.5, color="#d97706"))
    frags.append(text(350, 105, "mdat: відеокадри (0 .. 45 хв)", size=11, color=MUTED))
    frags.append(text(595, 100, "Ключовий кадр 45:00", size=11, bold=True, color=NEG))
    frags.append(text(595, 116, "зсув: 1 250 000 000", size=9.5, color=NEG))
    frags.append(text(745, 105, "mdat: решта (46..90 хв)", size=10.5, color=MUTED))

    # Крок 1: Отримання метаданих
    frags.append(rect(60, 145, 360, 310, fill=BG, stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(240, 170, "Крок 1: Ініціалізація та пошук moov", size=12, bold=True, color="#d97706"))

    frags.append(fitbox(75, 190, 330, 48, "Запит перших 64 КБ:\nGET /video.mp4  |  Range: bytes=0-65535", size=10.5, fill="#fffbeb", stroke="#d97706", sw=1.2, bold=True))
    frags.append(fitbox(75, 245, 330, 48, "Якщо moov на початку (qt-faststart):\nбраузер миттєво отримує таблицю семплів stbl", size=10.5, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(75, 300, 330, 48, "Якщо moov у хвості (без faststart):\nRange: bytes=-1048576 (читання останнього 1 МБ)", size=10.5, fill="#fee2e2", stroke=POS, sw=1.2))
    frags.append(fitbox(75, 355, 330, 85, "Результат:\nПлеєр знає тривалість, роздільність та\nпобайтну карту всіх ключових кадрів (GOP).\nВідео готове до миттєвого старту.", size=10.5, fill="#fef3c7", stroke="#d97706", sw=1.2, bold=True))

    # Стрілка переходу
    frags.append(arrow(425, 300, 455, 300, color=LINE, sw=2))

    # Крок 2: Перемотування користувача
    frags.append(rect(460, 145, 360, 310, fill=BG, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(640, 170, "Крок 2: Стрибок на 45:00 (Seek)", size=12, bold=True, color=NEG))

    frags.append(fitbox(475, 190, 330, 48, "Користувач перетягує повзунок на 45:00:\nПлеєр шукає найближчий I-frame у таблиці stss", size=10.5, fill="#eff6ff", stroke=NEG, sw=1.2, bold=True))
    frags.append(fitbox(475, 245, 330, 48, "Обчислення байтового зсуву в таблиці stco:\nI-frame на 45:00 розташований за зсувом 1 250 000 000", size=10.5, fill=FILL, stroke=MUTED, sw=1))
    frags.append(fitbox(475, 300, 330, 48, "Запит точного зрізу кадру:\nGET /video.mp4  |  Range: bytes=1250000000-", size=10.5, fill="#eff6ff", stroke=NEG, sw=1.5, bold=True))
    frags.append(fitbox(475, 355, 330, 85, "Результат:\n✗ Не потрібно завантажувати перші 1.2 ГБ\n✓ Відео починає грати з 45:00 за 50 мс\n✓ Економія 99% мережевого трафіку", size=10.5, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "media-seeking-moov.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_range_lifecycle()
    fig_if_range_condition()
    fig_multipart_byteranges()
    fig_range_dos_coalescing()
    fig_media_seeking_moov()
    print("All figures generated successfully.")
