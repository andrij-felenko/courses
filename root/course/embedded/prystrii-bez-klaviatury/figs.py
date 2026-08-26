# -*- coding: utf-8 -*-
"""Фігури до теми «Пристрій без клавіатури: SoftAP і BLE-провізіонування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Проблема безклавіатурного пристрою (Headless IoT) ───────────────────────
def fig_provisioning_problem():
    W, H = 820, 360
    f = [text(W / 2, 28,
              "Дилема «пристрою з коробки»: передача облікових даних Wi-Fi без клавіатури",
              size=15, bold=True)]

    # Лівий блок: Смартфон (користувач знає SSID і пароль)
    b_phone, _, _ = textbox(150, 140,
                            "Смартфон користувача\n• Має екран і клавіатуру\n• Підключений до домашньої мережі\n• Знає SSID: «Home-Net»\n• Знає пароль WPA2/WPA3",
                            size=12, fill="#eaf0fd", stroke=NEG, pad=12)
    f.append(b_phone)

    # Правий блок: Безклавіатурний пристрій (Headless IoT)
    b_mcu, _, _ = textbox(670, 140,
                          "Безклавіатурний IoT-вузол\n• Немає дисплея і клавіатури\n• Чистий NVS-флеш з заводу\n• Є лише антена 2.4 ГГц і МК\n• Не знає імені й пароля мережі",
                          size=12, fill="#fdecea", stroke=POS, pad=12)
    f.append(b_mcu)

    # Центральний блок: Домашній роутер
    b_ap, _, _ = textbox(410, 270,
                         "Домашня точка доступу (Wi-Fi AP)\nВимагає 4-стороннє рукостискання WPA2/WPA3\nі правильний пароль для надання доступу",
                         size=11.5, fill="#f4f6f8", stroke=LINE, pad=10)
    f.append(b_ap)

    # Стрілка з питанням між смартфоном і МК
    f.append(line(275, 140, 525, 140, color=POS, sw=2, dash="6,4"))
    b_q, _, _ = textbox(400, 140,
                        "Як передати SSID + пароль?\n— Ефір відкритий для прослуховування\n— Немає спільного секрету",
                        size=11, fill="#fff9db", stroke="#f59f00", pad=8)
    f.append(b_q)

    # Стрілки від пристроїв до AP
    f.append(arrow(220, 210, 310, 250, color=NEG, sw=1.5))
    f.append(text(240, 245, "Вже в мережі", size=10.5, color=NEG, bold=True))

    f.append(arrow(590, 210, 510, 250, color=MUTED, sw=1.5))
    f.append(text(575, 245, "Не може під'єднатися", size=10.5, color=POS, bold=True))

    render(os.path.join(IMG, "provisioning-problem.svg"), W, H, *f)


# ── 2. Метод SoftAP: Архітектура та послідовність ──────────────────────────────
def fig_softap_flow():
    W, H = 840, 420
    f = [text(W / 2, 28,
              "Провізіонування через SoftAP: підняття тимчасової мережі та HTTP API",
              size=15, bold=True)]

    # Крок 1: Підняття SoftAP
    b1, _, _ = textbox(150, 100,
                       "1. Старт SoftAP на МК\n• SSID: «Device-Setup-XXXX»\n• IP: 192.168.4.1\n• DHCP + DNS Captive Portal\n• Локальний HTTP-сервер",
                       size=11.5, fill="#f4f6f8", stroke=LINE, pad=10)
    f.append(b1)

    # Крок 2: Підключення телефона
    b2, _, _ = textbox(420, 100,
                       "2. Перемикання телефона\n• Від'єднується від домашньої AP\n• Під'єднується до «Device-Setup»\n• Отримує IP 192.168.4.2 від МК\n• Відкриває веб-форму або REST",
                       size=11.5, fill="#eaf0fd", stroke=NEG, pad=10)
    f.append(b2)

    # Крок 3: Передача облікових даних
    b3, _, _ = textbox(690, 100,
                       "3. Відправка конфігурації\n• HTTP POST /api/wifi-config\n• JSON: {ssid:..., password:...}\n• МК тестує з'єднання як станція\n• Збереження в NVS флеш",
                       size=11.5, fill="#eafaf1", stroke=FIELD, pad=10)
    f.append(b3)

    # Стрілки між кроками
    f.append(arrow(260, 100, 305, 100, color=LINE, sw=1.6))
    f.append(arrow(535, 100, 575, 100, color=LINE, sw=1.6))

    # Нижній блок: Підводні камені та вразливості SoftAP
    f.append(line(50, 205, 790, 205, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(W / 2, 225, "Вразливості та системні пастки методу SoftAP", size=13.5, bold=True, color=POS))

    bp1, _, _ = textbox(210, 310,
                        "Втрата мобільного інтернету\nAndroid/iOS бачать «No Internet»\nі примусово перемикають запити\nна стільникову мережу 4G/LTE,\nскидаючи підключення до МК",
                        size=11, fill="#fdecea", stroke=POS, pad=10)
    f.append(bp1)

    bp2, _, _ = textbox(490, 310,
                        "Відкритий радіоефір\nЯкщо SoftAP без пароля, весь\nтрафік HTTP POST іде відкритим текстом.\nСусідній сніфер 802.11 перехоплює\nдомашній пароль WPA2 роутера",
                        size=11, fill="#fdecea", stroke=POS, pad=10)
    f.append(bp2)

    bp3, _, _ = textbox(730, 310,
                        "Пам'ять і ресурси МК\nПотрібно одночасно тримати\nWi-Fi AP стек, DHCP-сервер,\nDNS-спуфер і парсер HTTP,\nщо забирає до 40 КБ RAM",
                        size=11, fill="#fff9db", stroke="#f59f00", pad=10)
    f.append(bp3)

    render(os.path.join(IMG, "softap-flow.svg"), W, H, *f)


# ── 3. BLE-провізіонування та безпечний канал Protocomm ────────────────────────
def fig_ble_protocomm_handshake():
    W, H = 840, 460
    f = [text(W / 2, 28,
              "BLE-провізіонування: захищений сеанс Curve25519 + AES-GCM через GATT",
              size=15, bold=True)]

    # Дві вертикальні лінії: Смартфон (Client) та IoT МК (Server)
    cx_phone, cx_mcu = 180, 660
    top_y, bot_y = 70, 410
    f.append(line(cx_phone, top_y, cx_phone, bot_y, color=MUTED, sw=1.5))
    f.append(line(cx_mcu, top_y, cx_mcu, bot_y, color=MUTED, sw=1.5))

    b_cl, _, _ = textbox(cx_phone, top_y - 12, "Смартфон (GATT Client)", size=12, bold=True,
                         fill="#eaf0fd", stroke=NEG, pad=8)
    b_srv, _, _ = textbox(cx_mcu, top_y - 12, "IoT-пристрій (GATT Server)", size=12, bold=True,
                          fill="#eafaf1", stroke=FIELD, pad=8)
    f.append(b_cl); f.append(b_srv)

    # 1. Реклама і з'єднання
    f.append(arrow(cx_mcu, 100, cx_phone, 100, color=MUTED, sw=1.4))
    f.append(text(420, 90, "1. BLE Advertisement («PROV_DEVICE_1234») + GATT Connect", size=11, color=INK))

    # 2. Рукостискання Curve25519 (Security 1 / Security 2)
    f.append(arrow(cx_phone, 155, cx_mcu, 155, color=NEG, sw=1.6))
    f.append(text(420, 145, "2. Endpoint «prov-session»: Client Public Key (Curve25519)", size=11, color=NEG, bold=True))

    f.append(arrow(cx_mcu, 210, cx_phone, 210, color=FIELD, sw=1.6))
    f.append(text(420, 200, "3. Device Public Key + Device Random Nonce (Salt)", size=11, color=FIELD, bold=True))

    # Блок обчислення спільного ключа з PoP
    b_key, _, _ = textbox(420, 260,
                          "Обчислення спільного секрету:\nShared Key = ECDH(Curve25519) + Proof of Possession (QR-код PIN)\nВиведення сесійного ключа AES-256-GCM через HKDF-SHA256",
                          size=11, fill="#fff9db", stroke="#f59f00", pad=8)
    f.append(b_key)

    # 4. Сканування ефіру через зашифрований канал
    f.append(arrow(cx_phone, 320, cx_mcu, 320, color=LINE, sw=1.4))
    f.append(text(420, 310, "4. Endpoint «prov-scan»: Запит списку мереж (Encrypted)", size=11, color=INK))

    f.append(arrow(cx_mcu, 355, cx_phone, 355, color=LINE, sw=1.4))
    f.append(text(420, 345, "5. Список знайдених AP + рівні RSSI (Encrypted Protobuf)", size=11, color=INK))

    # 5. Передача конфігурації
    f.append(arrow(cx_phone, 400, cx_mcu, 400, color=POS, sw=1.8))
    f.append(text(420, 390, "6. Endpoint «prov-config»: Зашифровані SSID + Passphrase (AES-GCM)", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "ble-protocomm-handshake.svg"), W, H, *f)


# ── 4. SmartConfig та WPS: Приховані канали й вразливості ───────────────────────
def fig_smartconfig_sidechannel():
    W, H = 840, 400
    f = [text(W / 2, 28,
              "SmartConfig і WPS: чому приховані канали та PIN-коди пішли в минуле",
              size=15, bold=True)]

    # Ліва половина: SmartConfig (Side channel via packet length)
    f.append(rect(20, 55, 385, 325, fill="#fdfefe", stroke=MUTED, sw=1.2))
    f.append(text(212, 80, "SmartConfig (ESP-Touch / SimpleLink)", size=13, bold=True, color=NEG))

    b_sc1, _, _ = textbox(212, 135,
                          "Смартфон транслює UDP Broadcast\nКорисні дані всередині пакетів зашифровані\nдомашнім роутером (WPA2), але...",
                          size=10.5, fill="#f4f6f8", stroke=LINE, pad=8)
    f.append(b_sc1)

    b_sc2, _, _ = textbox(212, 220,
                          "Прихований канал: довжина кадру 802.11\nМК у режимі Promiscuous Mode сніфить ефір:\nДовжина пакета = Символ пароля\nПакет 1: 128 байт ('W'), Пакет 2: 145 байт ('i')",
                          size=10.5, fill="#fff9db", stroke="#f59f00", pad=8)
    f.append(b_sc2)

    b_sc3, _, _ = textbox(212, 320,
                          "Чому вмирає:\n• 5 ГГц смартфон не бачить 2.4 ГГц чип\n• AP Client Isolation блокує broadcast\n• Сторонній трафік ламає послідовність",
                          size=10.5, fill="#fdecea", stroke=POS, pad=8)
    f.append(b_sc3)

    # Права половина: WPS PIN & Pixie Dust
    f.append(rect(435, 55, 385, 325, fill="#fdfefe", stroke=MUTED, sw=1.2))
    f.append(text(627, 80, "WPS (Wi-Fi Protected Setup PIN)", size=13, bold=True, color=POS))

    b_wps1, _, _ = textbox(627, 135,
                           "8-значний PIN на роутері\nПротокол фатально розбиває перевірку PIN\nна дві окремі незалежні частини:",
                           size=10.5, fill="#f4f6f8", stroke=LINE, pad=8)
    f.append(b_wps1)

    b_wps2, _, _ = textbox(627, 220,
                           "Вразливість 10 000 + 1 000 спроб:\n• Перші 4 цифри: 10^4 = 10 000 варіантів\n• Наступні 3 цифри (+1 CRC): 10^3 = 1 000 варіантів\nРазом: 11 000 спроб замість 100 000 000!",
                           size=10.5, fill="#fdecea", stroke=POS, pad=8)
    f.append(b_wps2)

    b_wps3, _, _ = textbox(627, 320,
                           "Атака Pixie Dust (2014):\nЧерез слабкий генератор випадкових чисел PRNG\nу чипах роутерів PIN обчислюється офлайн\nменш ніж за 1 секунду! WPS вимкнено скрізь",
                           size=10.5, fill="#fdecea", stroke=POS, pad=8)
    f.append(b_wps3)

    render(os.path.join(IMG, "smartconfig-sidechannel.svg"), W, H, *f)


# ── 5. Скінченний автомат провізіонування (Provisioning FSM) ───────────────────
def fig_provisioning_fsm():
    W, H = 840, 480
    f = [text(W / 2, 28,
              "Скінченний автомат процесу ініціалізації: валідація, збереження та відкат",
              size=15, bold=True)]

    # Стани FSM
    # 1. СТАРТ / Читання NVS
    b_boot, _, _ = textbox(130, 90,
                           "STATE_INIT\nЧитання NVS флеш",
                           size=11.5, fill="#f4f6f8", stroke=LINE, pad=8)
    f.append(b_boot)

    # 2. Спроба підключення за збереженим
    b_conn, _, _ = textbox(420, 90,
                           "STATE_CONNECT_SAVED\nСпроба входу в AP за NVS",
                           size=11.5, fill="#eaf0fd", stroke=NEG, pad=8)
    f.append(b_conn)

    # 3. Робочий режим
    b_op, _, _ = textbox(720, 90,
                         "STATE_OPERATIONAL\nМережа активна (Station OK)",
                         size=11.5, fill="#eafaf1", stroke=FIELD, pad=8)
    f.append(b_op)

    # 4. Режим провізіонування
    b_prov, _, _ = textbox(240, 240,
                           "STATE_PROVISIONING_ACTIVE\nЗапуск BLE / SoftAP реклами\nОчікування облікових даних",
                           size=11.5, fill="#fff9db", stroke="#f59f00", pad=10)
    f.append(b_prov)

    # 5. Валідація з'єднання
    b_val, _, _ = textbox(600, 240,
                          "STATE_VALIDATING_STATION\nТестове підключення до AP:\n4-way handshake + DHCP IP test",
                          size=11.5, fill="#eaf0fd", stroke=NEG, pad=10)
    f.append(b_val)

    # 6. Відкат / Помилка
    b_fail, _, _ = textbox(420, 390,
                           "STATE_PROV_FAILED (Fallback)\nПовідомлення клієнту: «AUTH_FAIL»\nВідкат до попереднього стану / Таймаут",
                           size=11.5, fill="#fdecea", stroke=POS, pad=10)
    f.append(b_fail)

    # Переходи і стрілки
    # INIT -> CONNECT_SAVED (є дані)
    f.append(arrow(200, 90, 320, 90, color=LINE, sw=1.5))
    f.append(text(260, 80, "Є NVS дані", size=10, color=MUTED))

    # INIT -> PROV_ACTIVE (NVS порожній)
    f.append(arrow(130, 120, 180, 200, color=LINE, sw=1.5))
    f.append(text(125, 170, "Порожній NVS", size=10, color=POS))

    # CONNECT_SAVED -> OPERATIONAL (успіх)
    f.append(arrow(525, 90, 615, 90, color=FIELD, sw=1.8))
    f.append(text(570, 80, "IP отримано", size=10, color=FIELD, bold=True))

    # CONNECT_SAVED -> PROV_ACTIVE (невдача підключення після N спроб)
    f.append(arrow(380, 120, 300, 200, color=POS, sw=1.5))
    f.append(text(370, 160, "Невдача (3 спроби)", size=10, color=POS))

    # PROV_ACTIVE -> VALIDATING (отримано нові дані)
    f.append(arrow(365, 240, 465, 240, color=LINE, sw=1.6))
    f.append(text(415, 230, "RX: SSID + Pass", size=10, color=INK, bold=True))

    # VALIDATING -> OPERATIONAL (валідація успішна: зберегти в NVS)
    f.append(arrow(640, 200, 700, 125, color=FIELD, sw=1.8))
    f.append(text(710, 180, "Успіх: Запис NVS", size=10, color=FIELD, bold=True))

    # VALIDATING -> PROV_FAILED (помилка пароля / не знайдено AP)
    f.append(arrow(560, 285, 480, 350, color=POS, sw=1.6))
    f.append(text(555, 330, "Помилка автентифікації", size=10, color=POS))

    # PROV_FAILED -> PROV_ACTIVE (повторне очікування від користувача)
    f.append(arrow(360, 360, 270, 285, color=MUTED, sw=1.5))
    f.append(text(285, 340, "Нова спроба", size=10, color=MUTED))

    # Кнопка апаратного скидання (Factory Reset)
    f.append(line(720, 125, 720, 450, color=POS, sw=1.4, dash="4,4"))
    f.append(line(720, 450, 180, 450, color=POS, sw=1.4, dash="4,4"))
    f.append(arrow(180, 450, 180, 285, color=POS, sw=1.4))
    f.append(text(450, 465, "Апаратна кнопка: Factory Reset (утримування 5 с) → Очищення NVS → Примусовий PROV",
                  size=10.5, color=POS, bold=True))

    render(os.path.join(IMG, "provisioning-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_provisioning_problem()
    fig_softap_flow()
    fig_ble_protocomm_handshake()
    fig_smartconfig_sidechannel()
    fig_provisioning_fsm()
    print("All figures generated successfully.")
