# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. captive-portal-flow: діаграма послідовності викликів від підключення до UI ──
def fig_captive_portal_flow():
    W, H = 940, 560
    p = []

    # Колони учасників: Смартфон (Клієнт), DNS-сервер SoftAP, HTTP-сервер SoftAP
    x_cli = 140
    x_dns = 470
    x_http = 800

    # Шапки сутностей
    p.append(fitbox(x_cli - 90, 20, 180, 44, "Смартфон\n(iOS / Android / Win)", size=12, bold=True, fill="#e9eefb", stroke=NEG))
    p.append(fitbox(x_dns - 90, 20, 180, 44, "DNS Catch-all\n(UDP :53, SoftAP)", size=12, bold=True, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(x_http - 90, 20, 180, 44, "HTTP-сервер\n(TCP :80, SoftAP)", size=12, bold=True, fill="#fdf0e6", stroke="#c07a2e"))

    # Вертикальні лінії життя (lifelines)
    y_start = 64
    y_end = 530
    p.append(line(x_cli, y_start, x_cli, y_end, color="#c0c6d0", sw=1.5, dash="4,4"))
    p.append(line(x_dns, y_start, x_dns, y_end, color="#c0c6d0", sw=1.5, dash="4,4"))
    p.append(line(x_http, y_start, x_http, y_end, color="#c0c6d0", sw=1.5, dash="4,4"))

    steps = [
        # (y, from_x, to_x, label, sublabel, color, is_resp)
        (110, x_cli, x_dns, "1. DNS Query: A captive.apple.com", "Клієнт перевіряє доступ до інтернету", NEG, False),
        (160, x_dns, x_cli, "2. DNS Answer: IP = 192.168.4.1", "Catch-all повертає IP власного сервера", FIELD, True),
        (220, x_cli, x_http, "3. HTTP GET /hotspot-detect.html", "Host: captive.apple.com", NEG, False),
        (275, x_http, x_cli, "4. HTTP 302 Found (Location: /setup)", "Перехоплення: замість Success — редирект", POS, True),
        (335, x_cli, x_http, "5. HTTP GET /setup", "Запит сторінки конфігурації у WebSheet", NEG, False),
        (390, x_http, x_cli, "6. HTTP 200 OK (index.html.gz)", "Content-Encoding: gzip (SPA інтерфейс)", FIELD, True),
        (450, x_cli, x_http, "7. HTTP POST /api/save (SSID, Pass)", "Передача параметрів домашньої Wi-Fi", NEG, False),
        (500, x_http, x_cli, "8. HTTP 200 OK -> Перезапуск вузла", "Збереження в NVS та рестарт у STA", FIELD, True),
    ]

    for y, x1, x2, msg, sub, col, is_resp in steps:
        dash = "3,3" if is_resp else None
        p.append(line(x1, y, x2, y, color=col, sw=1.8, dash=dash))
        # стрілка на кінці
        dx = -8 if x2 < x1 else 8
        p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' %
                 (x2, y, x2 - dx, y - 4, x2 - dx, y + 4, col))
        
        # текст над стрілкою
        mx = (x1 + x2) / 2
        p.append(text(mx, y - 10, msg, size=11, color=INK, bold=True))
        p.append(text(mx, y + 14, sub, size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "captive-portal-flow.svg"), W, H, *p,
           title="Послідовність перехоплення трафіку та відкриття Captive Portal")


# ── 2. dns-header-structure: анатомія DNS-пакета перехоплення (UDP 53) ────────
def fig_dns_header_structure():
    W, H = 940, 480
    p = []

    # Загальний заголовок і блоки
    p.append(text(W / 2, 48, "Анатомія UDP-пакета DNS: Запит клієнта проти Відповіді-пастки", size=15, bold=True, color=INK))

    # Секція Заголовка (12 байтів)
    p.append(fitbox(40, 75, 420, 170, "", fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    p.append(text(250, 98, "DNS Header запиту (12 байтів)", size=13, bold=True, color=NEG))
    p.append(fitbox(55, 115, 190, 36, "Transaction ID: 0xABCD", size=11, fill="#e9eefb", stroke=NEG))
    p.append(fitbox(255, 115, 190, 36, "Flags: 0x0100 (Standard Query)", size=11, fill="#e9eefb", stroke=NEG))
    p.append(fitbox(55, 160, 190, 36, "QDCOUNT: 1 (Одне питання)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(255, 160, 190, 36, "ANCOUNT: 0 (Немає відповідей)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(55, 202, 190, 30, "NSCOUNT: 0", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(255, 202, 190, 30, "ARCOUNT: 0", size=10, fill="#ffffff", stroke=MUTED))

    # Заголовок Відповіді
    p.append(fitbox(480, 75, 420, 170, "", fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    p.append(text(690, 98, "DNS Header відповіді Spoof (12 байтів)", size=13, bold=True, color=FIELD))
    p.append(fitbox(495, 115, 190, 36, "Transaction ID: 0xABCD (Збігається)", size=11, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(695, 115, 190, 36, "Flags: 0x8180 (Response, NoErr)", size=11, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(495, 160, 190, 36, "QDCOUNT: 1 (Копія питання)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(695, 160, 190, 36, "ANCOUNT: 1 (Одна відповідь)", size=11, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(495, 202, 190, 30, "NSCOUNT: 0", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(695, 202, 190, 30, "ARCOUNT: 0", size=10, fill="#ffffff", stroke=MUTED))

    # Секції Question та Answer
    p.append(fitbox(40, 260, 860, 80, "", fill="#ffffff", stroke="#94a3b8", sw=1.5))
    p.append(text(160, 285, "Question Section:", size=12, bold=True, color=INK))
    p.append(fitbox(270, 272, 280, 28, "QNAME: \x07captive\x05apple\x03com\x00", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(fitbox(565, 272, 145, 28, "QTYPE: 0x0001 (A)", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(fitbox(725, 272, 160, 28, "QCLASS: 0x0001 (IN)", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(text(470, 325, "Змінна довжина імені у форматі міток (довжина + байти рядка) + нульовий байт завершення", size=10.5, color=MUTED))

    # Секція Answer (Resource Record), що дописується мікроконтролером
    p.append(fitbox(40, 355, 860, 105, "", fill="#fdfaf3", stroke=POS, sw=1.8))
    p.append(text(200, 380, "Доданий Answer Section (16 байтів):", size=12, bold=True, color=POS))
    
    p.append(fitbox(55, 395, 120, 32, "NAME: 0xC00C\n(Вказівник на QNAME)", size=9.5, fill="#ffffff", stroke=POS))
    p.append(fitbox(185, 395, 100, 32, "TYPE: 0x0001\n(IPv4 A)", size=9.5, fill="#ffffff", stroke=LINE))
    p.append(fitbox(295, 395, 100, 32, "CLASS: 0x0001\n(Internet IN)", size=9.5, fill="#ffffff", stroke=LINE))
    p.append(fitbox(405, 395, 110, 32, "TTL: 0x0000000A\n(10 секунд)", size=9.5, fill="#ffffff", stroke=LINE))
    p.append(fitbox(525, 395, 110, 32, "RDLENGTH: 0x0004\n(4 байти IPv4)", size=9.5, fill="#ffffff", stroke=LINE))
    p.append(fitbox(645, 395, 240, 32, "RDATA: 192.168.4.1 (0xC0A80401)\n(Власна IP-адреса SoftAP)", size=9.5, fill="#eef6ef", stroke=FIELD, bold=True))

    p.append(text(470, 448, "Фіксований блок RR дописується у вихідний буфер запиту без виділення динамічної пам'яті", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "dns-header-structure.svg"), W, H, *p,
           title="Структура DNS-пакета перехоплення та формування Answer RR")


# ── 3. spa-flash-pipeline: підготовка та роздача веб-ресурсів із флеш-пам'яті ──
def fig_spa_flash_pipeline():
    W, H = 940, 420
    p = []

    bw = 190
    bh = 220
    y_box = 100

    cols = [
        (45, "1. Єдиний SPA-файл", "index.html (~18 КБ)\n\n• Ванільний HTML5\n• Вбудований CSS\n• Вбудований JS\n• Жодних CDN / npm\n• fetch() до /api/*", "#f8fafc", LINE),
        (275, "2. GZIP-стиснення", "index.html.gz (~4 КБ)\n\n• Рівень: gzip -9\n• Стиснення: ~78%\n• Усунення дублів\n  у тексті та тегах\n• Робота на ПК розробника", "#e9eefb", NEG),
        (505, "3. Розміщення у Flash", "const uint8_t index_html_gz[]\n\n• Секція: .rodata\n• Зберігається у Flash\n• Споживання RAM: 0 байт\n• Вбудовано в прошивку\n• Довжина: index_html_gz_len", "#fdf0e6", "#c07a2e"),
        (735, "4. Zero-Copy віддача", "HTTP Response\n\n• 200 OK\n• Type: text/html\n• Encoding: gzip\n• Пряма передача з Flash\n  у TCP буфер LWIP\n• Швидкість: < 10 мс", "#eef6ef", FIELD),
    ]

    for x, title, desc, fill, stroke in cols:
        p.append(rect(x, y_box, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(fitbox(x + 10, y_box + 12, bw - 20, 32, title, size=12, bold=True, fill="#ffffff", stroke=stroke))
        p.append(mtext(x + bw / 2, y_box + 70, desc, size=11, color=INK, lh=1.35))

    # Стрілки між етапами
    p.append(arrow(238, y_box + bh / 2, 272, y_box + bh / 2, color=INK, sw=2))
    p.append(arrow(468, y_box + bh / 2, 502, y_box + bh / 2, color=INK, sw=2))
    p.append(arrow(698, y_box + bh / 2, 732, y_box + bh / 2, color=INK, sw=2))

    # Підписи під стрілками
    p.append(text(255, y_box + bh / 2 + 25, "gzip -9", size=10, color=NEG, bold=True))
    p.append(text(485, y_box + bh / 2 + 25, "bin2c", size=10, color="#c07a2e", bold=True))
    p.append(text(715, y_box + bh / 2 + 25, "send()", size=10, color=FIELD, bold=True))

    # Нижня плашка висновку
    p.append(fitbox(45, 345, 880, 50, "Результат: повноцінний сучасний адаптивний веб-інтерфейс займає лише 4 КБ Flash-пам'яті і не навантажує оперативну пам'ять мікроконтролера розпакуванням", size=11, bold=True, fill="#f0fdf4", stroke=FIELD))

    render(os.path.join(OUT, "spa-flash-pipeline.svg"), W, H, *p,
           title="Конвеєр підготовки та роздачі SPA-ресурсів з Flash-пам'яті")


# ── 4. state-machine-config: автомат станів життєвого циклу Wi-Fi ────────────
def fig_state_machine_config():
    W, H = 940, 460
    p = []

    p.append(fitbox(60, 75, 180, 60, "BOOT / INIT\nЧитання конфігурації NVS", size=11.5, bold=True, fill="#f8fafc", stroke=LINE))
    p.append(fitbox(380, 75, 180, 60, "STA_CONNECTING\nСпроба з'єднання з AP", size=11.5, bold=True, fill="#e9eefb", stroke=NEG))
    p.append(fitbox(700, 75, 180, 60, "STA_OPERATIONAL\nРобочий режим (IoT/Data)", size=11.5, bold=True, fill="#eef6ef", stroke=FIELD))
    p.append(fitbox(350, 290, 240, 75, "AP_CAPTIVE_PORTAL\nSoftAP + DNS-пастка + HTTP\n(Очікування налаштувань)", size=11.5, bold=True, fill="#fdf0e6", stroke=POS))

    # Переходи (стрілки з написами)
    p.append(arrow(240, 105, 375, 105, color=NEG, sw=1.8))
    p.append(text(310, 92, "NVS має SSID", size=10, color=NEG, bold=True))

    p.append(arrow(150, 135, 370, 290, color=POS, sw=1.8))
    p.append(text(210, 220, "NVS порожній або\nзатиснуто кнопку", size=9.5, color=POS, bold=True))

    p.append(arrow(560, 105, 695, 105, color=FIELD, sw=1.8))
    p.append(text(630, 92, "IP отримано (DHCP)", size=10, color=FIELD, bold=True))

    p.append(arrow(470, 135, 470, 285, color=POS, sw=1.8))
    p.append(text(550, 210, "Помилка / Таймаут\n(3 невдалі спроби)", size=9.5, color=POS, bold=True))

    p.append(arrow(350, 325, 150, 140, color=FIELD, sw=1.8))
    p.append(text(180, 290, "POST /api/save OK\n-> Запис NVS -> Рестарт", size=9.5, color=FIELD, bold=True))

    p.append('<path d="M 790 135 C 790 325, 660 330, 595 330" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4" marker-end="url(#arrow)"/>' % MUTED)
    p.append(text(760, 250, "Втрата мережі > 5 хв\nабо кнопка скидання", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "state-machine-config.svg"), W, H, *p,
           title="Автомат станів: перехід між Captive Portal та робочим клієнтським режимом")


if __name__ == "__main__":
    fig_captive_portal_flow()
    fig_dns_header_structure()
    fig_spa_flash_pipeline()
    fig_state_machine_config()
    print("All figures generated successfully.")
