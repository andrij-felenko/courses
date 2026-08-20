# -*- coding: utf-8 -*-
"""Фігури до теми «Push-повідомлення як системний канал доставки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"
COOL = "#eaf0fd"
GOOD = "#e8f6ee"
WARN = "#fef3c7"


# ── 1. Вплив на радіомодем і батарею: опитування проти push-демона ─────────────
def cellular_battery_drain():
    W, H = 1080, 560
    f = []

    # ── Панель А: Наївне опитування багатьма застосунками ──
    yA = 40.0
    f.append(fitbox(30, yA, 1020, 230, "", fill="#ffffff", stroke="#d1d5db", sw=1.2))
    f.append(fitbox(45, yA + 15, 230, 36, "Наївне опитування (5 застосунків)", size=13, bold=True, fill=WARM, stroke=POS))

    f.append(text(290, yA + 26, "Кожен застосунок тримає власний сокет і шле періодичний ping для обходу NAT", size=11.5, anchor="start", color=MUTED))
    f.append(text(290, yA + 42, "Модем переходить у стан високого споживання (200–500 мА) і тримає «хвіст» активності 10–15 с", size=11, anchor="start", color=POS))

    # Вісь часу
    axY = yA + 130
    f.append(line(70, axY, 1010, axY, color="#9ca3af", sw=1.5))
    f.append(arrow(1005, axY, 1020, axY, color="#9ca3af", sw=1.5))
    f.append(text(1025, axY + 4, "t", size=12, bold=True, color="#4b5563"))

    # Сплески від 5 застосунків (несинхронізовані)
    pulses = [
        (100, 45, "Чат: ping", POS),
        (220, 40, "Пошта: poll", "#d97706"),
        (350, 50, "Банк: ping", "#059669"),
        (490, 45, "Таксі: poll", "#7c3aed"),
        (620, 40, "Новини: poll", "#db2777"),
        (760, 45, "Чат: ping", POS),
        (890, 40, "Пошта: poll", "#d97706"),
    ]

    for px, pw, label, col in pulses:
        # Активний стан передачі
        f.append(rect(px, axY - 50, pw, 50, fill=WARM, stroke=col, sw=1.5))
        f.append(text(px + pw / 2, axY - 56, label, size=10, color=col, bold=True))
        # Хвіст радіомодема (tail time)
        tail_w = 65
        f.append(rect(px + pw, axY - 30, tail_w, 30, fill="#fee2e2", stroke=POS, sw=1))
        f.append(text(px + pw + tail_w / 2, axY - 14, "хвіст RRC", size=9, color=POS))

    f.append(fitbox(70, yA + 160, 930, 48,
                    "Наслідок: радіомодем практично не переходить у режим сну (IDLE).\n"
                    "Батарея смартфона ємністю 4000 мА·год розряджається за 3–5 годин фонового очікування.",
                    size=12, fill="#fff1f2", stroke=POS, bold=True, color=POS))

    # ── Панель Б: Системний push-демон ──
    yB = 300.0
    f.append(fitbox(30, yB, 1020, 230, "", fill="#ffffff", stroke="#d1d5db", sw=1.2))
    f.append(fitbox(45, yB + 15, 230, 36, "Системний push-демон (ОС)", size=13, bold=True, fill=GOOD, stroke=FIELD))

    f.append(text(290, yB + 26, "Один спільний довготривалий TLS-канал на весь пристрій (apsd / GmsCore)", size=11.5, anchor="start", color=MUTED))
    f.append(text(290, yB + 42, "Усі процеси застосунків заморожені в RAM. Модем спить у стані низької потужності (IDLE < 1 мА)", size=11, anchor="start", color=FIELD))

    # Вісь часу
    bxY = yB + 130
    f.append(line(70, bxY, 1010, bxY, color="#9ca3af", sw=1.5))
    f.append(arrow(1005, bxY, 1020, bxY, color="#9ca3af", sw=1.5))
    f.append(text(1025, bxY + 4, "t", size=12, bold=True, color="#4b5563"))

    # Стан сну більшу частину часу (до і після пуша)
    f.append(rect(70, bxY - 18, 410, 18, fill="#f0fdf4", stroke=FIELD, sw=1))
    f.append(text(275, bxY - 5, "Глибокий сон радіомодема (IDLE: струм < 1 мА)", size=11, color=FIELD, bold=True))

    f.append(rect(585, bxY - 18, 415, 18, fill="#f0fdf4", stroke=FIELD, sw=1))
    f.append(text(790, bxY - 5, "Глибокий сон радіомодема (IDLE: струм < 1 мА)", size=11, color=FIELD, bold=True))

    # Єдине вхідне push-повідомлення
    in_x = 480
    f.append(rect(in_x, bxY - 50, 45, 50, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(text(in_x + 22, bxY - 56, "Вхідний Push", size=10.5, color=FIELD, bold=True))
    f.append(rect(in_x + 45, bxY - 30, 60, 30, fill=GOOD, stroke=FIELD, sw=1))
    f.append(text(in_x + 75, bxY - 14, "хвіст RRC", size=9, color=FIELD))

    f.append(fitbox(70, yB + 160, 930, 48,
                    "Виграш: модем прокидається лише за зовнішньою подією або рідкісним системним keep-alive (раз на 15–30 хв).\n"
                    "Автономність пристрою зростає до 24–48 годин без утрати миттєвої доставки сповіщень.",
                    size=12, fill=GOOD, stroke=FIELD, bold=True, color=FIELD))

    render(os.path.join(OUT, "cellular-battery-drain.svg"), W, H, *f,
           title="Енергоспоживання стільникового модема: наївне опитування проти системного демона")


# ── 2. Трикутник взаємодії та життєвий цикл push-повідомлення ─────────────────
def push_three_party_flow():
    W, H = 1080, 620
    f = []

    # Колони учасників
    col_w = 210
    col_h = 44
    xA = 60.0    # Застосунок
    xB = 320.0   # Системний демон
    xC = 580.0   # Шлюз push-служби
    xD = 840.0   # Бекенд застосунку

    f.append(fitbox(xA, 30, col_w, col_h, "Клієнтський застосунок\n(Користувацький процес)", size=12, bold=True, fill=COOL, stroke=NEG))
    f.append(fitbox(xB, 30, col_w, col_h, "Демон ОС на пристрої\n(apsd / GmsCore)", size=12, bold=True, fill="#e0e7ff", stroke="#4338ca"))
    f.append(fitbox(xC, 30, col_w, col_h, "Шлюз push-служби\n(APNs / FCM / WebPush)", size=12, bold=True, fill=WARN, stroke="#b45309"))
    f.append(fitbox(xD, 30, col_w, col_h, "Бекенд сервісу\n(Application Server)", size=12, bold=True, fill=GOOD, stroke=FIELD))

    # Вертикальні лінії життя
    y_top = 74.0
    y_bot = 570.0
    for x in (xA + col_w/2, xB + col_w/2, xC + col_w/2, xD + col_w/2):
        f.append(line(x, y_top, x, y_bot, color="#cbd5e1", sw=1.5, dash="4,4"))

    cxA = xA + col_w/2
    cxB = xB + col_w/2
    cxC = xC + col_w/2
    cxD = xD + col_w/2

    # Фаза 1: Реєстрація токена
    f.append(rect(40, 95, 1000, 200, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    f.append(text(55, 115, "ФАЗА 1. РЕЄСТРАЦІЯ ПРИСТРОЮ ТА ОБМІН ТОКЕНАМИ", size=11, bold=True, color="#475569", anchor="start"))

    # 1.1 Запит реєстрації
    f.append(arrow(cxA, 140, cxB, 140, color=NEG, sw=1.6))
    f.append(text((cxA + cxB)/2, 132, "1. registerForRemoteNotifications()", size=11, color=NEG, bold=True))

    # 1.2 Демон звертається до шлюзу
    f.append(arrow(cxB, 175, cxC, 175, color="#4338ca", sw=1.6))
    f.append(text((cxB + cxC)/2, 167, "2. Запит токена через системний TLS-канал", size=11, color="#4338ca"))

    # 1.3 Шлюз повертає Device Token
    f.append(arrow(cxC, 210, cxB, 210, color="#b45309", sw=1.6))
    f.append(text((cxB + cxC)/2, 202, "3. Генерація унікального Device Token", size=11, color="#b45309"))

    # 1.4 Демон передає токен у колбек застосунку
    f.append(arrow(cxB, 245, cxA, 245, color=NEG, sw=1.6))
    f.append(text((cxA + cxB)/2, 237, "4. didRegisterForRemoteNotifications(token)", size=11, color=NEG))

    # 1.5 Застосунок реєструє токен на своєму бекенді
    f.append(arrow(cxA, 280, cxD, 280, color=FIELD, sw=1.8))
    f.append(text((cxA + cxD)/2, 272, "5. HTTPS POST /api/register-device (user_id, device_token)", size=11.5, color=FIELD, bold=True))

    # Фаза 2: Відправка та доставка push
    f.append(rect(40, 315, 1000, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    f.append(text(55, 335, "ФАЗА 2. ВІДПРАВКА СПОВІЩЕННЯ ТА ДОСТАВКА НА ПРИСТРІЙ", size=11, bold=True, color="#475569", anchor="start"))

    # 2.1 Подія на бекенді та POST до шлюзу
    f.append(arrow(cxD, 370, cxC, 370, color=FIELD, sw=1.8))
    f.append(text((cxC + cxD)/2, 360, "6. HTTP/2 POST /3/device/{token} (JWT/OAuth2 + Payload)", size=11.5, color=FIELD, bold=True))

    # 2.2 Шлюз шле кадр у відкритий сокет демона
    f.append(arrow(cxC, 420, cxB, 420, color="#b45309", sw=1.8))
    f.append(text((cxB + cxC)/2, 410, "7. Доставка байтового кадру в постійний TLS-сокет пристрою", size=11, color="#b45309", bold=True))

    # 2.3 Диспетчеризація демоном: два шляхи
    f.append(arrow(cxB, 470, cxA, 470, color=NEG, sw=1.6))
    f.append(text((cxA + cxB)/2, 460, "8а. Фоновий пуш: пробудження процесу на ≤30 с", size=11, color=NEG))

    f.append(fitbox(cxB - 90, 495, 180, 42, "8б. Візуальний пуш:\nпоказ у Notification Center", size=11, fill="#fef08a", stroke="#ca8a04", bold=True))
    f.append(text(cxB, 550, "(код застосунку навіть не запускається)", size=10.5, color="#854d0e"))

    render(os.path.join(OUT, "push-three-party-flow.svg"), W, H, *f,
           title="Трикутник взаємодії: реєстрація токена та доставка push-повідомлення")


# ── 3. Наскрізне шифрування WebPush (RFC 8291) ────────────────────────────────
def webpush_encryption_flow():
    W, H = 1080, 560
    f = []

    # 3 блоки
    bW = 300
    bH = 460
    y0 = 60.0

    # Блок 1: Сервер застосунку (Application Server)
    xA = 40.0
    f.append(fitbox(xA, y0, bW, bH, "", fill="#ffffff", stroke=FIELD, sw=1.5))
    f.append(fitbox(xA + 15, y0 + 15, bW - 30, 38, "Сервер застосунку\n(Відправник)", size=13, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(xA + 15, y0 + 70, bW - 30, 40, "Відкритий текст:\nJSON { title, body, url }", size=11.5, fill=FILL, stroke=LINE))
    f.append(arrow(xA + bW/2, y0 + 110, xA + bW/2, y0 + 130, color=LINE, sw=1.5))

    f.append(fitbox(xA + 15, y0 + 130, bW - 30, 65, "ECDH на кривій P-256:\nСпільний секрет з публічним\nключем клієнта (p256dh)", size=11, fill="#ecfdf5", stroke=FIELD))
    f.append(arrow(xA + bW/2, y0 + 195, xA + bW/2, y0 + 215, color=LINE, sw=1.5))

    f.append(fitbox(xA + 15, y0 + 215, bW - 30, 65, "HKDF (auth secret + salt):\nВиведення сесійного ключа\nCEK (16 B) та Nonce (12 B)", size=11, fill="#ecfdf5", stroke=FIELD))
    f.append(arrow(xA + bW/2, y0 + 280, xA + bW/2, y0 + 300, color=LINE, sw=1.5))

    f.append(fitbox(xA + 15, y0 + 300, bW - 30, 65, "Шифрування AES-128-GCM:\nФормування бінарного запису\n[Salt || RS || IDLen || EphPub || Ciphertext]", size=11, fill="#fef3c7", stroke="#d97706", bold=True))
    f.append(arrow(xA + bW/2, y0 + 365, xA + bW/2, y0 + 385, color=LINE, sw=1.5))

    f.append(fitbox(xA + 15, y0 + 385, bW - 30, 55, "Запит RFC 8030:\nHTTP POST + VAPID заголовок\n(JWT, підписаний ES256)", size=11, fill=GOOD, stroke=FIELD))

    # Стрілка між Сервером і Шлюзом
    f.append(arrow(xA + bW, y0 + 220, xA + bW + 70, y0 + 220, color=POS, sw=2))
    f.append(text(xA + bW + 35, y0 + 205, "Шифротекст", size=11, color=POS, bold=True))
    f.append(text(xA + bW + 35, y0 + 240, "(AES-GCM)", size=10, color=MUTED))

    # Блок 2: Недовірений шлюз WebPush
    xB = xA + bW + 70
    f.append(fitbox(xB, y0, 260, bH, "", fill="#ffffff", stroke=POS, sw=1.5))
    f.append(fitbox(xB + 15, y0 + 15, 230, 38, "Шлюз WebPush (Недовірений)\n(Google FCM / Mozilla Autopush)", size=12, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(xB + 15, y0 + 90, 230, 110, "Перевірка VAPID JWT:\n• Ідентифікація відправника\n• Перевірка підпису відкритого ключа VAPID\n• Валідація прав на Endpoint", size=11, fill=FILL, stroke=LINE))

    f.append(fitbox(xB + 15, y0 + 230, 230, 120, "Шлюз бачить лише:\n• URL кінцевої точки (endpoint)\n• Зашифрований бінарний blob\n• TTL та терміновість (Urgency)\n\nВміст повідомлення шлюзу НЕВІДОМИЙ", size=11, fill="#fff1f2", stroke=POS, color=POS, bold=True))

    f.append(fitbox(xB + 15, y0 + 380, 230, 60, "Трансляція в сокет браузера:\nПередача шифротексту\nбез можливості розшифрувати", size=11, fill=FILL, stroke=LINE))

    # Стрілка між Шлюзом і Браузером
    f.append(arrow(xB + 260, y0 + 220, xB + 260 + 70, y0 + 220, color=POS, sw=2))
    f.append(text(xB + 260 + 35, y0 + 205, "Шифротекст", size=11, color=POS, bold=True))
    f.append(text(xB + 260 + 35, y0 + 240, "(AES-GCM)", size=10, color=MUTED))

    # Блок 3: Браузер клієнта
    xC = xB + 260 + 70
    f.append(fitbox(xC, y0, bW, bH, "", fill="#ffffff", stroke=NEG, sw=1.5))
    f.append(fitbox(xC + 15, y0 + 15, bW - 30, 38, "Клієнтський браузер\n(Service Worker)", size=13, bold=True, fill=COOL, stroke=NEG))

    f.append(fitbox(xC + 15, y0 + 70, bW - 30, 50, "Отримання бінарного кадру:\nВилучення Salt та EphPub\nіз заголовка запису", size=11, fill=FILL, stroke=LINE))
    f.append(arrow(xC + bW/2, y0 + 120, xC + bW/2, y0 + 140, color=LINE, sw=1.5))

    f.append(fitbox(xC + 15, y0 + 140, bW - 30, 65, "ECDH відновлення секрету:\nСпільний секрет із приватного\nключа підписки та EphPub", size=11, fill="#eff6ff", stroke=NEG))
    f.append(arrow(xC + bW/2, y0 + 205, xC + bW/2, y0 + 225, color=LINE, sw=1.5))

    f.append(fitbox(xC + 15, y0 + 225, bW - 30, 65, "HKDF виведення ключів:\nОбчислення ідентичного CEK\nта Nonce з auth secret клієнта", size=11, fill="#eff6ff", stroke=NEG))
    f.append(arrow(xC + bW/2, y0 + 290, xC + bW/2, y0 + 310, color=LINE, sw=1.5))

    f.append(fitbox(xC + 15, y0 + 310, bW - 30, 55, "Дешифрування AES-GCM:\nПеревірка тегу автентичності\nта відновлення відкритого тексту", size=11, fill=GOOD, stroke=FIELD, bold=True))
    f.append(arrow(xC + bW/2, y0 + 365, xC + bW/2, y0 + 385, color=LINE, sw=1.5))

    f.append(fitbox(xC + 15, y0 + 385, bW - 30, 55, "Подія push у Service Worker:\nevent.data.json() →\nregistration.showNotification()", size=11, fill=COOL, stroke=NEG, bold=True))

    render(os.path.join(OUT, "webpush-encryption-flow.svg"), W, H, *f,
           title="Наскрізне шифрування WebPush (RFC 8291): шлюз без доступу до даних")


if __name__ == "__main__":
    cellular_battery_drain()
    push_three_party_flow()
    webpush_encryption_flow()
    print("All figures generated successfully.")
