# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Тріада особистості пристрою ──────────────────────────────────
def fig_device_identity_triad():
    W, H = 880, 500
    p = []
    
    # Заголовок
    p.append(text(W/2, 35, "Тріада особистості пристрою: Ідентифікатор, Ключ, Сертифікат", size=16, color=INK, bold=True))
    
    # Три стовпчики / рівні
    col_w = 260
    h_box = 245
    y_top = 65
    
    # 1. Апаратний ідентифікатор
    x1 = 30
    p.append(rect(x1, y_top, col_w, h_box, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, rx=8))
    p.append(text(x1 + col_w/2, y_top + 28, "1. Апаратний ідентифікатор", size=13, color=INK, bold=True))
    p.append(text(x1 + col_w/2, y_top + 48, "(UID / Chip Serial)", size=11, color=MUTED, bold=True))
    p.append(line(x1 + 15, y_top + 62, x1 + col_w - 15, y_top + 62, color="#bdc3c7", sw=1))
    p.append(text(x1 + 15, y_top + 85, "• Роль: публічне ім'я («Хто я»)", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 110, "• Властивість: відкритий, незмінний", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 135, "• Носій: eFuse, лазерні перемички", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 160, "• Загроза: клонування та підробка", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 15, y_top + 182, "  (самого серійника недостатньо)", size=10, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x1 + 25, y_top + 205, col_w - 50, 26, fill="#eaecee", stroke="#bdc3c7", sw=1, rx=4))
    p.append(text(x1 + col_w/2, y_top + 222, "ПАСИВНА НАЗВА", size=11, color=NEG, bold=True))

    # 2. Криптографічний секрет
    x2 = 310
    p.append(rect(x2, y_top, col_w, h_box, fill="#eaf2f8", stroke=NEG, sw=1.8, rx=8))
    p.append(text(x2 + col_w/2, y_top + 28, "2. Приватний ключ", size=13, color=NEG, bold=True))
    p.append(text(x2 + col_w/2, y_top + 48, "(Hardware Private Key / UDS)", size=11, color=MUTED, bold=True))
    p.append(line(x2 + 15, y_top + 62, x2 + col_w - 15, y_top + 62, color="#a9cce3", sw=1))
    p.append(text(x2 + 15, y_top + 85, "• Роль: доказ володіння секретом", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 110, "• Властивість: суворо таємний", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 135, "• Носій: Secure Element, PUF", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 160, "• Захист: ніколи не виходить назовні", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 15, y_top + 182, "  (підпис генерується всередині)", size=10, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x2 + 25, y_top + 205, col_w - 50, 26, fill="#d4e6f1", stroke="#a9cce3", sw=1, rx=4))
    p.append(text(x2 + col_w/2, y_top + 222, "АКТИВНИЙ ДОКАЗ", size=11, color=NEG, bold=True))

    # 3. Сертифікат X.509
    x3 = 590
    p.append(rect(x3, y_top, col_w, h_box, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x3 + col_w/2, y_top + 28, "3. Цифровий сертифікат", size=13, color=FIELD, bold=True))
    p.append(text(x3 + col_w/2, y_top + 48, "(X.509 DevID Certificate)", size=11, color=MUTED, bold=True))
    p.append(line(x3 + 15, y_top + 62, x3 + col_w - 15, y_top + 62, color="#a9dfbf", sw=1))
    p.append(text(x3 + 15, y_top + 85, "• Роль: зв'язування особи й ключа", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 110, "• Властивість: публічний документ", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 135, "• Підписант: Довірений CA заводу", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 160, "• Вміст: UID в SAN + Відкритий ключ", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 15, y_top + 182, "  (гарантія справжності від третьої CA)", size=10, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x3 + 25, y_top + 205, col_w - 50, 26, fill="#d5f5e3", stroke="#a9dfbf", sw=1, rx=4))
    p.append(text(x3 + col_w/2, y_top + 222, "ДОВІРЧА ПОРУКА", size=11, color=FIELD, bold=True))

    # Нижній блок: Як вони взаємодіють у протоколі
    y_bot = 335
    w_bot = 820
    p.append(rect(30, y_bot, w_bot, 140, fill="#ffffff", stroke="#2c3e50", sw=1.4, rx=8))
    p.append(text(W/2, y_bot + 26, "Механізм криптографічної перевірки автентичності (Challenge-Response)", size=13, color=INK, bold=True))
    
    # Кроки перевірки
    p.append(text(50, y_bot + 58, "1. Сервер надсилає випадковий виклик (Nonce / TLS Handshake Challenge)", size=11.5, color=INK, anchor="start"))
    p.append(text(50, y_bot + 84, "2. Пристрій обчислює підпис: Sig = Sign(PrivKey, Nonce) всередині апаратного чипа", size=11.5, color=NEG, bold=True, anchor="start"))
    p.append(text(50, y_bot + 110, "3. Сервер перевіряє: Verify(Cert.PubKey, Nonce, Sig) == OK та валідує ланцюжок CA", size=11.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "device-identity-triad.svg"), W, H, *p,
           title="Тріада особистості пристрою: Ідентифікатор, Ключ, Сертифікат")


# ── Фігура 2: Ієрархія IEEE 802.1AR DevID та життєвий цикл ─────────────────
def fig_devid_hierarchy_and_lifecycle():
    W, H = 940, 500
    p = []
    
    p.append(text(W/2, 30, "Ієрархія ідентичностей IEEE 802.1AR: Заводський IDevID та Експлуатаційний LDevID", size=15, color=INK, bold=True))

    # Ліва колонка: IDevID (Завод)
    x_l = 30
    w_col = 390
    p.append(rect(x_l, 60, w_col, 415, fill="#fdfefe", stroke="#2980b9", sw=1.6, rx=10))
    p.append(rect(x_l + 10, 70, w_col - 20, 35, fill="#ebf5fb", stroke="#2980b9", sw=1, rx=6))
    p.append(text(x_l + w_col/2, 92, "Initial Device Identifier (IDevID)", size=13, color="#1b4f72", bold=True))
    
    p.append(text(x_l + 20, 130, "• Створюється: На заводі виробника (OEM)", size=11.5, color=INK, anchor="start"))
    p.append(text(x_l + 20, 155, "• Приватний ключ: Невитягуваний, у Secure Element", size=11.5, color=INK, anchor="start"))
    p.append(text(x_l + 20, 180, "• Сертифікат: Підписаний кореневим CA виробника", size=11.5, color=INK, anchor="start"))
    p.append(text(x_l + 20, 205, "• Термін дії: Необмежений (на весь час життя чипа)", size=11.5, color=INK, anchor="start"))
    p.append(text(x_l + 20, 230, "• Атрибути: SAN містить HardwareModuleName / UID", size=11.5, color=INK, anchor="start"))
    p.append(text(x_l + 20, 255, "• Можливість зміни: Фізично заблоковано від перезапису", size=11.5, color=POS, bold=True, anchor="start"))
    
    # Блок застосування IDevID
    p.append(rect(x_l + 15, 285, w_col - 30, 175, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(x_l + w_col/2, 310, "Основне призначення IDevID:", size=11.5, color=INK, bold=True))
    p.append(text(x_l + 25, 338, "1. Доказ автентичності апаратури при постачанні", size=10.5, color=INK, anchor="start"))
    p.append(text(x_l + 25, 366, "2. Захист від клонування та підробки плат", size=10.5, color=INK, anchor="start"))
    p.append(text(x_l + 25, 394, "3. Первинний безпечний онбординг (Bootstrap mTLS)", size=10.5, color=NEG, bold=True, anchor="start"))
    p.append(text(x_l + 25, 420, "   через протоколи EST (RFC 7030) або BRSKI", size=10.5, color=MUTED, anchor="start"))

    # Права колонка: LDevID (Оператор / Користувач)
    x_r = 520
    p.append(rect(x_r, 60, w_col, 415, fill="#fdfefe", stroke="#27ae60", sw=1.6, rx=10))
    p.append(rect(x_r + 10, 70, w_col - 20, 35, fill="#eafaf1", stroke="#27ae60", sw=1, rx=6))
    p.append(text(x_r + w_col/2, 92, "Local Device Identifier (LDevID)", size=13, color="#145a32", bold=True))
    
    p.append(text(x_r + 20, 130, "• Створюється: Під час впровадження у мережу", size=11.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 155, "• Приватний ключ: Згенерований чипом або оператором", size=11.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 180, "• Сертифікат: Підписаний внутрішнім Enterprise CA", size=11.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 205, "• Термін дії: Обмежений (наприклад, 90 днів / 1 рік)", size=11.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 230, "• Атрибути: Локальне доменне ім'я, роль пристрою", size=11.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 255, "• Можливість зміни: Регулярне поновлення за EST", size=11.5, color=FIELD, bold=True, anchor="start"))
    
    # Блок застосування LDevID
    p.append(rect(x_r + 15, 285, w_col - 30, 175, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(x_r + w_col/2, 310, "Основне призначення LDevID:", size=11.5, color=INK, bold=True))
    p.append(text(x_r + 25, 338, "1. Щоденна робота у внутрішній мережі", size=10.5, color=INK, anchor="start"))
    p.append(text(x_r + 25, 366, "2. Мережевий доступ 802.1X (RADIUS / EAP-TLS)", size=10.5, color=INK, anchor="start"))
    p.append(text(x_r + 25, 394, "3. Робота з брокером MQTT / IoT Gateway", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x_r + 25, 420, "4. Відкликання сертифіката без блокування чипа", size=10.5, color=MUTED, anchor="start"))

    # Центральна область переходу (між x=420 та x=520)
    p.append(arrow(x_l + w_col + 10, 220, x_r - 10, 220, color="#d35400", sw=2.2))
    p.append(rect(430, 180, 80, 32, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=4))
    p.append(text(470, 196, "Онбординг", size=10, color="#b9770e", bold=True))
    p.append(text(470, 208, "(EST / BRSKI)", size=9, color="#b9770e"))

    render(os.path.join(OUT, "devid-hierarchy-and-lifecycle.svg"), W, H, *p,
           title="Ієрархія ідентичностей IEEE 802.1AR: IDevID та LDevID")


# ── Фігура 3: Архітектури зберігання ключів ────────────────────────────────
def fig_hardware_root_of_trust_storage():
    W, H = 880, 480
    p = []
    
    p.append(text(W/2, 30, "Архітектури апаратного зберігання криптографічних секретів пристрою", size=15, color=INK, bold=True))

    w_box = 260
    h_box = 400
    y_top = 60
    
    # 1. Дискретний Secure Element
    x1 = 30
    p.append(rect(x1, y_top, w_box, h_box, fill="#ffffff", stroke="#2980b9", sw=1.5, rx=8))
    p.append(rect(x1 + 10, y_top + 10, w_box - 20, 32, fill="#ebf5fb", stroke="#2980b9", sw=1, rx=5))
    p.append(text(x1 + w_box/2, y_top + 32, "Дискретний Secure Element", size=12, color="#1b4f72", bold=True))
    p.append(text(x1 + w_box/2, y_top + 58, "(ATECC608, Optiga Trust M)", size=10.5, color=MUTED, bold=True))
    p.append(line(x1 + 15, y_top + 70, x1 + w_box - 15, y_top + 70, color="#d4e6f1", sw=1))
    
    p.append(text(x1 + 15, y_top + 95, "• Окремий загартований чип", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 120, "• Інтерфейс: I2C / SPI з шифруванням", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 145, "• Апаратні акселератори ECC/RSA", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 170, "• Фізичний активний екран (Mesh)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x1 + 15, y_top + 195, "• Захист від DPA / зондування / збоїв", size=11, color=FIELD, bold=True, anchor="start"))
    
    p.append(rect(x1 + 15, y_top + 230, w_box - 30, 150, fill="#f4f6f8", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(x1 + w_box/2, y_top + 250, "Особливість безпеки:", size=11, color=INK, bold=True))
    p.append(text(x1 + 25, y_top + 275, "Приватний ключ фізично замкнений", size=10, color=NEG, bold=True, anchor="start"))
    p.append(text(x1 + 25, y_top + 295, "всередині захищеної EEPROM/Flash.", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 25, y_top + 320, "Головний процесор віддає хеш,", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 25, y_top + 340, "а назад отримує лише підпис (R, S).", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x1 + 25, y_top + 365, "Ключ не потрапляє в RAM MCU.", size=10, color=MUTED, italic=True, anchor="start"))

    # 2. MCU TrustZone / Захищена зона
    x2 = 310
    p.append(rect(x2, y_top, w_box, h_box, fill="#ffffff", stroke="#8e44ad", sw=1.5, rx=8))
    p.append(rect(x2 + 10, y_top + 10, w_box - 20, 32, fill="#f4ecf7", stroke="#8e44ad", sw=1, rx=5))
    p.append(text(x2 + w_box/2, y_top + 32, "MCU ARM TrustZone-M", size=12, color="#512e5f", bold=True))
    p.append(text(x2 + w_box/2, y_top + 58, "(STM32H5/U5, NXP LPC55S)", size=10.5, color=MUTED, bold=True))
    p.append(line(x2 + 15, y_top + 70, x2 + w_box - 15, y_top + 70, color="#e8daef", sw=1))
    
    p.append(text(x2 + 15, y_top + 95, "• Логічна ізоляція ядра MCU", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 120, "• Secure vs Non-Secure світи (SAU)", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 145, "• Ключі в одноразових eFuse", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 170, "• Виклики через Secure Gateway (SG)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 15, y_top + 195, "• Апаратне блокування JTAG/SWD", size=11, color=FIELD, bold=True, anchor="start"))
    
    p.append(rect(x2 + 15, y_top + 230, w_box - 30, 150, fill="#f4f6f8", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(x2 + w_box/2, y_top + 250, "Особливість безпеки:", size=11, color=INK, bold=True))
    p.append(text(x2 + 25, y_top + 275, "Один кристал містить і логіку,", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 25, y_top + 295, "і криптографічні секрети.", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 25, y_top + 320, "Економія на BOM, але вищі вимоги", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 25, y_top + 340, "до захисту від багів прошивки", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 25, y_top + 365, "та атак побічними каналами.", size=10, color=MUTED, italic=True, anchor="start"))

    # 3. SRAM PUF
    x3 = 590
    p.append(rect(x3, y_top, w_box, h_box, fill="#ffffff", stroke="#27ae60", sw=1.5, rx=8))
    p.append(rect(x3 + 10, y_top + 10, w_box - 20, 32, fill="#eafaf1", stroke="#27ae60", sw=1, rx=5))
    p.append(text(x3 + w_box/2, y_top + 32, "Апаратний SRAM PUF", size=12, color="#145a32", bold=True))
    p.append(text(x3 + w_box/2, y_top + 58, "(Physically Unclonable Function)", size=10.5, color=MUTED, bold=True))
    p.append(line(x3 + 15, y_top + 70, x3 + w_box - 15, y_top + 70, color="#d5f5e3", sw=1))
    
    p.append(text(x3 + 15, y_top + 95, "• «Відбиток пальця» кремнію", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 120, "• Стан комірок SRAM при старті", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 145, "• Ключ НЕ записаний у Flash/NVM", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 15, y_top + 170, "• Fuzzy Extractor (коди BCH)", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 195, "• Знищення ключа при вимкненні", size=11, color=FIELD, bold=True, anchor="start"))
    
    p.append(rect(x3 + 15, y_top + 230, w_box - 30, 150, fill="#f4f6f8", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(x3 + w_box/2, y_top + 250, "Особливість безпеки:", size=11, color=INK, bold=True))
    p.append(text(x3 + 25, y_top + 275, "У вимкненому стані ключ фізично", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 25, y_top + 295, "відсутній на платі! Його не можна", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 25, y_top + 320, "витягти мікроскопом чи зчитати", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 25, y_top + 340, "з дампа пам'яті. Реконструюється", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 25, y_top + 365, "динамічно тільки при живленні.", size=10, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(OUT, "hardware-root-of-trust-storage.svg"), W, H, *p,
           title="Архітектури апаратного зберігання криптографічних секретів пристрою")


# ── Фігура 4: Послідовність онбордингу EST та mTLS ─────────────────────────
def fig_est_enrollment_and_mtls_flow():
    W, H = 880, 560
    p = []
    
    p.append(text(W/2, 30, "Послідовність онбордингу пристрою за протоколом EST (RFC 7030)", size=15, color=INK, bold=True))

    x_dev = 150.0
    x_est = 450.0
    x_ca  = 750.0

    # Вертикальні лінії
    p.append(line(x_dev, 75, x_dev, 510, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(x_est, 75, x_est, 510, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(x_ca, 75, x_ca, 510, color=MUTED, sw=1.5, dash="4 4"))

    # Заголовки акторів
    p.append(rect(x_dev - 75, 45, 150, 36, fill="#ebf5fb", stroke="#2980b9", sw=1.2, rx=5))
    p.append(text(x_dev, 61, "IoT Пристрій", size=11, color="#1b4f72", bold=True))
    p.append(text(x_dev, 73, "(IDevID в SE)", size=9.5, color=MUTED))

    p.append(rect(x_est - 75, 45, 150, 36, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=5))
    p.append(text(x_est, 61, "EST Сервер / RA", size=11, color="#b9770e", bold=True))
    p.append(text(x_est, 73, "(Enrollment Proxy)", size=9.5, color=MUTED))

    p.append(rect(x_ca - 75, 45, 150, 36, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=5))
    p.append(text(x_ca, 61, "Корпоративний CA", size=11, color="#145a32", bold=True))
    p.append(text(x_ca, 73, "(Enterprise PKI)", size=9.5, color=MUTED))

    # Фаза 1: mTLS рукостискання
    y1 = 115
    p.append(rect(50, y1 - 15, 780, 48, fill="#f4f6f8", stroke="#aab7b8", sw=1, rx=6))
    p.append(text(W/2, y1 - 2, "Фаза 1: mTLS рукостискання на базі заводського сертифіката IDevID", size=11, color=NEG, bold=True))
    p.append(arrow(x_dev, y1 + 18, x_est, y1 + 18, color=NEG, sw=1.8))
    p.append(text((x_dev + x_est)/2, y1 + 12, "mTLS: Клієнт пред'являє IDevID + ClientCertificateVerify", size=10, color=NEG, bold=True))

    # Крок 2: Отримання кореневих сертифікатів
    y2 = 195
    p.append(arrow(x_dev, y2, x_est, y2, color=INK, sw=1.6))
    p.append(text((x_dev + x_est)/2, y2 - 7, "1. GET /.well-known/est/cacerts", size=10.5, color=INK, bold=True))
    
    y2_ret = y2 + 35
    p.append(arrow(x_est, y2_ret, x_dev, y2_ret, color=FIELD, sw=1.6))
    p.append(text((x_dev + x_est)/2, y2_ret - 7, "2. 200 OK (PKCS#7 з ланцюжком CA сертифікатів)", size=10, color=FIELD, bold=True))

    # Крок 3: Локальна генерація пари ключів LDevID
    y3 = 270
    p.append(rect(x_dev - 70, y3 - 12, 140, 28, fill="#d4efdf", stroke="#27ae60", sw=1.2, rx=4))
    p.append(text(x_dev, y3 + 5, "Генерація пари LDevID", size=10, color="#145a32", bold=True))

    # Крок 4: Відправлення CSR
    y4 = 325
    p.append(arrow(x_dev, y4, x_est, y4, color=INK, sw=1.6))
    p.append(text((x_dev + x_est)/2, y4 - 7, "3. POST /.well-known/est/simpleenroll (CSR / PKCS#10)", size=10.5, color=INK, bold=True))

    # Крок 5: Перевірка EST сервером та запит до CA
    y5 = 370
    p.append(arrow(x_est, y5, x_ca, y5, color="#8e44ad", sw=1.6))
    p.append(text((x_est + x_ca)/2, y5 - 7, "4. Валідація IDevID та запит сертифіката", size=10, color="#8e44ad", bold=True))
    
    y5_ret = y5 + 35
    p.append(arrow(x_ca, y5_ret, x_est, y5_ret, color="#8e44ad", sw=1.6))
    p.append(text((x_est + x_ca)/2, y5_ret - 7, "5. Підписаний LDevID сертифікат", size=10, color="#8e44ad", bold=True))

    # Крок 6: Відповідь клієнту
    y6 = 445
    p.append(arrow(x_est, y6, x_dev, y6, color=FIELD, sw=1.8))
    p.append(text((x_dev + x_est)/2, y6 - 7, "6. 200 OK (PKCS#7 з новим LDevID сертифікатом)", size=10.5, color=FIELD, bold=True))

    # Крок 7: Експлуатаційна фаза
    y7 = 495
    p.append(rect(50, y7 - 10, 780, 40, fill="#eafaf1", stroke="#27ae60", sw=1.4, rx=6))
    p.append(text(W/2, y7 + 6, "Фаза 2: Щоденна експлуатація через LDevID mTLS (IoT Hub / MQTT / 802.1X)", size=11, color="#145a32", bold=True))
    p.append(text(W/2, y7 + 22, "IDevID більше не використовується; поновлення сертифіката через /simplereenroll", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "est-enrollment-and-mtls-flow.svg"), W, H, *p,
           title="Послідовність онбордингу пристрою за протоколом EST (RFC 7030)")


if __name__ == "__main__":
    fig_device_identity_triad()
    fig_devid_hierarchy_and_lifecycle()
    fig_hardware_root_of_trust_storage()
    fig_est_enrollment_and_mtls_flow()
    print("Всі 4 фігури успішно згенеровано.")
