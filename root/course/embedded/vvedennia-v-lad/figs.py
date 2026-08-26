# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_trust_triangle():
    # Трикутник довіри під час введення в лад:
    # Завод (IDevID, Factory CA) <---> Мобільний конфігуратор (PoP / QR) <---> Хмарний сервер (LDevID, Tenant PKI)
    W, H = 820, 480
    p = []

    dev_x, dev_y = 150, 370
    app_x, app_y = 410, 110
    cld_x, cld_y = 670, 370

    # 1. Фонова сітка взаємодії
    p.append(rect(dev_x - 120, dev_y - 65, 240, 130, fill="#f9fbfd", stroke=FIELD, sw=2, rx=8))
    p.append(text(dev_x, dev_y - 38, "IoT-Пристрій", size=15, color=FIELD, bold=True))
    p.append(text(dev_x, dev_y - 16, "Заводський IDevID + чіп SE", size=11, color=INK))
    p.append(text(dev_x, dev_y + 4, "Приватний ключ у eFuse", size=11, color=MUTED))
    p.append(text(dev_x, dev_y + 24, "Proof of Possession (PoP)", size=11, color=POS, bold=True))
    p.append(text(dev_x, dev_y + 44, "Стан: з коробки", size=10, color=MUTED, italic=True))

    p.append(rect(app_x - 130, app_y - 65, 260, 130, fill="#fdfbf7", stroke=NEG, sw=2, rx=8))
    p.append(text(app_x, app_y - 38, "Конфігуратор (Смартфон)", size=15, color=NEG, bold=True))
    p.append(text(app_x, app_y - 16, "Зчитує QR-код / BLE сканує", size=11, color=INK))
    p.append(text(app_x, app_y + 4, "Має доступ до локального Wi-Fi", size=11, color=MUTED))
    p.append(text(app_x, app_y + 24, "Автентифікований у Хмарі", size=11, color=FIELD, bold=True))
    p.append(text(app_x, app_y + 44, "Тимчасовий посередник", size=10, color=MUTED, italic=True))

    p.append(rect(cld_x - 120, cld_y - 65, 240, 130, fill="#fbf9fe", stroke=LINE, sw=2, rx=8))
    p.append(text(cld_x, cld_y - 38, "Хмарний Сервіс (IoT Core)", size=15, color=LINE, bold=True))
    p.append(text(cld_x, cld_y - 16, "Перевіряє Factory CA ланцюг", size=11, color=INK))
    p.append(text(cld_x, cld_y + 4, "Реєструє власника (Claiming)", size=11, color=MUTED))
    p.append(text(cld_x, cld_y + 24, "Випускає робочий LDevID", size=11, color=NEG, bold=True))
    p.append(text(cld_x, cld_y + 44, "Кінцева точка довіри", size=10, color=MUTED, italic=True))

    # Зв'язки між вузлами
    # Зв'язок 1: Смартфон <-> Пристрій (Локальний BLE / SoftAP з PAKE/PoP)
    # Розбиваємо лінію на два сегменти над і під рамкою-підписом, щоб не було перетинів
    p.append(line(340, 175, 285, 205, color=NEG, sw=2))
    p.append(arrow(215, 245, 175, 305, color=NEG, sw=2))
    b1, _, _ = textbox(250, 225, "1 · Локальний місток (BLE / SoftAP)\nPAKE-рукостискання за QR-секретом\nПередача Wi-Fi SSID/PSK", size=10, pad=6, fill="#ffffff", stroke=NEG, color=NEG, bold=True)
    p.append(b1)

    # Зв'язок 2: Смартфон <-> Хмара (Claiming Token / User Intent)
    # Розбиваємо лінію на два сегменти над і під рамкою-підписом
    p.append(line(480, 175, 535, 205, color=LINE, sw=2))
    p.append(arrow(605, 245, 645, 305, color=LINE, sw=2))
    b2, _, _ = textbox(570, 225, "2 · Заявка на володіння (Claiming)\nТокен прив'язки до акаунта\nРеєстрація UID у базі флоту", size=10, pad=6, fill="#ffffff", stroke=LINE, color=LINE, bold=True)
    p.append(b2)

    # Зв'язок 3: Пристрій <-> Хмара (Прямий робочий TLS через домашню мережу)
    # Лінія розбита на 2 частини навколо центрального напису
    p.append(line(dev_x + 120, dev_y, 280, dev_y, color=FIELD, sw=2.2))
    p.append(arrow(540, cld_y, cld_x - 120, cld_y, color=FIELD, sw=2.2))
    b3, _, _ = textbox(410, 370, "3 · Прямий TLS-канал через домашню мережу\nВзаємна mTLS автентифікація: IDevID -> CSR -> LDevID\nПовноцінний робочий обмін даними (MQTT/HTTPS)", size=10, pad=8, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)
    p.append(b3)

    render(os.path.join(IMG, 'trust-triangle-bootstrap.svg'), W, H, *p,
           title="Трикутник довіри: від розриву ефіру до підтвердженого володіння")


def fig_claiming_mitigation():
    # Порівняння: незахищена прив'язка (вразлива до перехоплення) проти захищеної (Proof of Possession + Token)
    W, H = 840, 430
    p = []

    # Ліва колонка: Наївна вразлива схема (Front-running claiming)
    p.append(rect(20, 50, 385, 360, fill="#fdf7f7", stroke=POS, sw=1.8, rx=8))
    p.append(text(212, 80, "ВРАЗЛИВО: Відкрита прив'язка", size=14, color=POS, bold=True))
    p.append(text(212, 102, "Пристрій кричить серійник у відкритий ефір", size=11, color=MUTED))

    p.append(textbox(212, 145, "1 · Пристрій підняв відкриту точку:\n«Datchyk-84B2» (UID відкрито в ефірі)", size=10, pad=5, fill="#ffffff", stroke=POS, color=POS)[0])
    p.append(textbox(212, 215, "2 · Зловмисник поруч перехоплює UID\nі першим шле запит Claiming у Хмару:\n«Цей серійник мій, ось мій Account_ID»", size=10, pad=5, fill="#ffffff", stroke=POS, color=POS)[0])
    p.append(textbox(212, 290, "3 · Хмара прив'язує датчик до чужого акаунта!\nСправжній власник отримує помилку:\n«Пристрій уже зареєстровано»", size=10, pad=5, fill="#ffffff", stroke=POS, color=POS)[0])
    p.append(textbox(212, 365, "Результат: крадіжка пристрою зловмисником\nі блокування доступу для покупця", size=10, pad=5, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # Права колонка: Захищений протокол (PoP + Підписаний челендж)
    p.append(rect(435, 50, 385, 360, fill="#f7fbf8", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(627, 80, "ЗАХИЩЕНО: Автентифікація PoP + Челендж", size=14, color=FIELD, bold=True))
    p.append(text(627, 102, "Фізичний секрет + криптографічний доказ", size=11, color=MUTED))

    p.append(textbox(627, 145, "1 · Власник сканує QR на корпусі:\nUID + Одноразовий PIN (Proof of Possession)\nЕфіром летить лише PAKE-рукостискання", size=10, pad=5, fill="#ffffff", stroke=FIELD, color=FIELD)[0])
    p.append(textbox(627, 215, "2 · Смартфон шле в Хмару одноразовий Nonce;\nХмара видає тимчасовий Claiming-квиток,\nприв'язаний до токена авторизації власника", size=10, pad=5, fill="#ffffff", stroke=FIELD, color=FIELD)[0])
    p.append(textbox(627, 290, "3 · Пристрій підписує Nonce приватним IDevID;\nХмара звіряє підпис із заводським Factory CA\nі передає робочий сертифікат LDevID", size=10, pad=5, fill="#ffffff", stroke=FIELD, color=FIELD)[0])
    p.append(textbox(627, 365, "Результат: криптографічна гарантія власності,\nстійкість до прослуховування та підміни", size=10, pad=5, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(IMG, 'claiming-attack-mitigation.svg'), W, H, *p,
           title="Анатомія загрози: чому ідентифікатор без доказу володіння веде до захоплення")


def fig_onboarding_fsm():
    # Скінченний автомат процесу введення в лад: стани та переходи
    W, H = 840, 520
    p = []

    states = [
        ("1 · FACTORY_RESET", "Чистий аркуш: IDevID у чіпі,\nнемає мережевих паролів", 120, 110, MUTED),
        ("2 · CHANNEL_ACTIVE", "Увімкнено BLE / SoftAP,\nочікування підключення", 370, 110, NEG),
        ("3 · AUTHENTICATING", "PAKE-обмін ключами,\nперевірка PIN з QR-коду", 640, 110, POS),
        ("4 · NET_CONNECTING", "Отримано Wi-Fi SSID/PSK,\nспроба зв'язку з роутером", 640, 310, NEG),
        ("5 · CLOUD_BOOTSTRAP", "Генерація CSR, запит до хмари,\nверифікація IDevID -> LDevID", 370, 310, FIELD),
        ("6 · OPERATIONAL_CLAIMED", "Робочий режим: конфіг-канал\nназавжди заблоковано", 120, 310, FIELD),
    ]

    for title, desc, cx, cy, col in states:
        p.append(rect(cx - 100, cy - 45, 200, 90, fill="#ffffff", stroke=col, sw=2, rx=6))
        p.append(text(cx, cy - 20, title, size=11, color=col, bold=True))
        p.append(mtext(cx, cy + 4, desc, size=9.5, color=INK, lh=1.25))

    # Стрілки переходів
    # 1 -> 2
    p.append(arrow(220, 110, 270, 110, color=LINE, sw=1.8))
    p.append(text(245, 98, "Старт", size=9, color=MUTED, bold=True))

    # 2 -> 3
    p.append(arrow(470, 110, 540, 110, color=LINE, sw=1.8))
    p.append(text(505, 98, "Клієнт під'єднався", size=9, color=MUTED, bold=True))

    # 3 -> 4
    p.append(arrow(640, 155, 640, 265, color=LINE, sw=1.8))
    p.append(text(645, 210, "PoP валідний +\nSSID/PSK прийнято", size=9, color=MUTED, anchor="left"))

    # 4 -> 5
    p.append(arrow(540, 310, 470, 310, color=LINE, sw=1.8))
    p.append(text(505, 298, "Wi-Fi OK (IP є)", size=9, color=MUTED, bold=True))

    # 5 -> 6
    p.append(arrow(270, 310, 220, 310, color=FIELD, sw=2.2))
    p.append(text(245, 298, "LDevID отримано", size=9, color=FIELD, bold=True))

    # Відкатні переходи при помилках
    # 4 -> 2 (Помилка Wi-Fi пароля -> повернення в очікування конфігурації)
    p.append(line(640, 355, 640, 430, color=POS, sw=1.5, dash="3 3"))
    p.append(line(640, 430, 370, 430, color=POS, sw=1.5, dash="3 3"))
    p.append(arrow(370, 430, 370, 155, color=POS, sw=1.5))
    p.append(textbox(505, 430, "Помилка асоціації Wi-Fi (таймаут / хибний пароль)\nЗвіт клієнту + повтор введення", size=9, pad=5, fill="#fff5f5", stroke=POS, color=POS)[0])

    # Скидання до заводських (Factory Reset)
    p.append(line(120, 265, 120, 155, color=MUTED, sw=1.5, dash="3 3"))
    p.append(arrow(120, 180, 120, 155, color=MUTED, sw=1.5))
    p.append(text(110, 210, "Утримання кнопки\nFactory Reset 10s", size=9, color=MUTED, anchor="right"))

    render(os.path.join(IMG, 'onboarding-state-machine.svg'), W, H, *p,
           title="Автомат станів введення в лад: від початкового сканування до робочого замка")


def fig_zero_touch_fido():
    # Промисловий Zero-Touch Onboarding (FDO): Rendezvous Server + Ownership Voucher
    W, H = 840, 460
    p = []

    mfg_x = 120
    dev_x = 300
    rv_x  = 520
    own_x = 720

    # 4 вертикальні доріжки
    p.append(rect(mfg_x - 55, 45, 110, 45, fill="#fdfbf7", stroke=LINE, sw=1.5, rx=6))
    p.append(text(mfg_x, 72, "Виробник", size=12, color=LINE, bold=True))

    p.append(rect(dev_x - 55, 45, 110, 45, fill="#f7fbf8", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(dev_x, 72, "Новий Пристрій", size=12, color=FIELD, bold=True))

    p.append(rect(rv_x - 65, 45, 130, 45, fill="#fdf7fd", stroke=POS, sw=1.5, rx=6))
    p.append(text(rv_x, 72, "Сервер Рандеву", size=12, color=POS, bold=True))

    p.append(rect(own_x - 65, 45, 130, 45, fill="#f4f8fe", stroke=NEG, sw=1.5, rx=6))
    p.append(text(own_x, 72, "Хмара Власника", size=12, color=NEG, bold=True))

    p.append(line(mfg_x, 90, mfg_x, 420, color=LINE, sw=1, dash="2 4"))
    p.append(line(dev_x, 90, dev_x, 420, color=FIELD, sw=1, dash="2 4"))
    p.append(line(rv_x,  90, rv_x,  420, color=POS, sw=1, dash="2 4"))
    p.append(line(own_x, 90, own_x, 420, color=NEG, sw=1, dash="2 4"))

    # Етап 1: Виробництво та ваучер власності
    y1 = 130
    p.append(arrow(mfg_x, y1, own_x, y1, color=LINE, sw=1.8))
    p.append(textbox((mfg_x + own_x) / 2, y1 - 2, "1 · Передача Ваучера власності (Ownership Voucher)\nЦифровий ланцюг підписів від конвеєра до кінцевого покупця", size=9.5, pad=5, fill="#ffffff", stroke=LINE, color=LINE)[0])

    # Етап 2: Реєстрація очікування власником у Сервері Рандеву
    y2 = 200
    p.append(arrow(own_x, y2, rv_x, y2, color=NEG, sw=1.8))
    p.append(textbox((rv_x + own_x) / 2, y2 - 2, "2 · Реєстрація ваучера в Рандеву\nВласник вказує URL свого Cloud IoT Core", size=9.5, pad=5, fill="#ffffff", stroke=NEG, color=NEG)[0])

    # Етап 3: Перше увімкнення пристрою (підключення кабелю Ethernet / стільникового модема)
    y3 = 270
    p.append(arrow(dev_x, y3, rv_x, y3, color=FIELD, sw=1.8))
    p.append(textbox((dev_x + rv_x) / 2, y3 - 2, "3 · Пристрій звертається до Рандеву\nАвтентифікація через IDevID-сертифікат", size=9.5, pad=5, fill="#ffffff", stroke=FIELD, color=FIELD)[0])

    # Етап 4: Перенаправлення до власника
    y4 = 330
    p.append(arrow(rv_x, y4, dev_x, y4, color=POS, sw=1.8))
    p.append(textbox((dev_x + rv_x) / 2, y4 - 2, "4 · Рандеву повертає координати Власника\nПеренаправлення на цільовий Cloud Endpoint", size=9.5, pad=5, fill="#ffffff", stroke=POS, color=POS)[0])

    # Етап 5: Завершальне пряме рукостискання та робоча конфігурація
    y5 = 390
    p.append(arrow(dev_x, y5, own_x, y5, color=FIELD, sw=2.2))
    p.append(textbox((dev_x + own_x) / 2, y5 - 2, "5 · Пряма взаємна mTLS автентифікація з Хмарою Власника\nЗавантаження робочого LDevID, конфігурації та ключів шифрування", size=9.5, pad=6, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(IMG, 'zero-touch-fido.svg'), W, H, *p,
           title="Промисловий Zero-Touch Onboarding: як тисячі пристроїв входять у парк без смартфона")


if __name__ == '__main__':
    fig_trust_triangle()
    fig_claiming_mitigation()
    fig_onboarding_fsm()
    fig_zero_touch_fido()
    print("All figures generated successfully.")
