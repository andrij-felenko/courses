# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. lorawan-topology: «Зірка зірок» ─────────────────────────────────────────
def fig_topology():
    W, H = 860, 420
    p = []

    # Колонка 1: Кінцеві пристрої (End Devices)
    p.append(text(90, 35, "Кінцеві пристрої", size=13, color=INK, bold=True))
    p.append(text(90, 52, "(End Devices)", size=11, color=MUTED))

    p.append(fitbox(20, 80, 140, 55, "Датчик вологи\n(Class A, Батарея)", size=11, fill="#f4f6f8", stroke=LINE))
    p.append(fitbox(20, 160, 140, 55, "Лічильник газу\n(Class A, Батарея)", size=11, fill="#f4f6f8", stroke=LINE))
    p.append(fitbox(20, 240, 140, 55, "Вуличне світло\n(Class B, Реле)", size=11, fill="#f4f6f8", stroke=LINE))
    p.append(fitbox(20, 320, 140, 55, "Клапан тиску\n(Class C, 220 В)", size=11, fill="#f4f6f8", stroke=LINE))

    # Радіоканал LoRa RF
    p.append(text(215, 35, "Радіоефір ISM", size=12, color=NEG, bold=True))
    p.append(text(215, 52, "(LoRa 868 / 915 МГц)", size=10, color=MUTED))

    # Хвилі / стрілки від пристроїв до шлюзів
    for y_dev in [107, 187, 267, 347]:
        p.append(arrow(165, y_dev, 260, 145, color=NEG, sw=1.3))
        p.append(arrow(165, y_dev, 260, 285, color=NEG, sw=1.3))

    # Колонка 2: Шлюзи (Gateways)
    p.append(text(320, 35, "Базові станції", size=13, color=INK, bold=True))
    p.append(text(320, 52, "(Шлюзи / Concentrators)", size=11, color=MUTED))

    p.append(fitbox(265, 110, 120, 75, "Шлюз 1 (SX1302)\nПрозорий ретранслятор\nUDP / Basic Station", size=10, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(265, 250, 120, 75, "Шлюз 2 (SX1303)\nПрозорий ретранслятор\nUDP / Basic Station", size=10, fill="#eaf0fd", stroke=NEG))

    # IP Backhaul
    p.append(arrow(390, 147, 465, 200, color=LINE, sw=1.5))
    p.append(arrow(390, 287, 465, 220, color=LINE, sw=1.5))
    p.append(text(428, 170, "IP / 4G / Eth", size=10, color=MUTED, bold=True))

    # Колонка 3: Network Server
    p.append(text(535, 35, "Мережевий сервер", size=13, color=INK, bold=True))
    p.append(text(535, 52, "(Network Server, NS)", size=11, color=MUTED))

    p.append(fitbox(470, 110, 130, 215, "Network Server (NS)\n\n• Дедуплікація копій\n• Перевірка MIC (NwkSKey)\n• Керування ADR\n• Маршрутизація Downlink\n• Планування RX1 / RX2\n• Облік лічильників FCnt", size=10, fill="#eef6ef", stroke=FIELD))

    # Зв'язок NS з Join Server та Application Server
    p.append(arrow(605, 160, 685, 135, color=POS, sw=1.5))
    p.append(arrow(605, 260, 685, 285, color=FIELD, sw=1.5))

    # Колонка 4: Join Server & Application Server
    p.append(text(765, 35, "Сервери безпеки й додатків", size=13, color=INK, bold=True))
    p.append(text(765, 52, "(JS та Application Server)", size=11, color=MUTED))

    p.append(fitbox(690, 95, 150, 95, "Join Server (JS)\n\n• Збереження AppKey / NwkKey\n• Обробка Join-Request\n• Генерація NwkSKey / AppSKey\n• Автентифікація OTAA", size=9.5, fill="#fdecea", stroke=POS))

    p.append(fitbox(690, 235, 150, 120, "Application Server (AS)\n\n• Збереження AppSKey\n• Розшифрування FRMPayload\n• Конвертація корисних даних\n• Інтеграція: MQTT / HTTP API\n• Передача на Дашборд / БД", size=9.5, fill="#eef6ef", stroke=FIELD))

    render(os.path.join(OUT, "lorawan-topology.svg"), W, H, *p,
           title="Архітектура мережі LoRaWAN: топологія «зірка зірок»")


# ── 2. class-abc-timing: Часові діаграми Class A, B, C ─────────────────────────
def fig_class_timing():
    W, H = 860, 430
    p = []

    # Часова шкала Class A
    p.append(text(30, 45, "Class A (Найнижче споживання, двонаправлений зв'язок за ініціативою вузла):", size=12, color=INK, bold=True, anchor="start"))

    # TX Uplink
    p.append(rect(140, 70, 60, 35, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(170, 92, "TX Uplink", size=10, color=POS, bold=True))

    # Затримка RECEIVE_DELAY1 (1.0 с)
    p.append(rect(205, 78, 110, 18, fill="#f4f6f8", stroke=MUTED, sw=1, rx=2))
    p.append(text(260, 91, "RECEIVE_DELAY1 (1 с)", size=9, color=MUTED))

    # Вікно RX1
    p.append(rect(320, 70, 50, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(345, 92, "RX1", size=10, color=NEG, bold=True))

    # Затримка до RX2 (1.0 с)
    p.append(rect(375, 78, 110, 18, fill="#f4f6f8", stroke=MUTED, sw=1, rx=2))
    p.append(text(430, 91, "RECEIVE_DELAY2 (2 с)", size=9, color=MUTED))

    # Вікно RX2
    p.append(rect(490, 70, 50, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(515, 92, "RX2", size=10, color=NEG, bold=True))

    # Сон
    p.append(rect(545, 78, 280, 18, fill="#e2e8f0", stroke=MUTED, sw=1, rx=2))
    p.append(text(685, 91, "Глибокий сон (Deep Sleep, споживання ~1–2 мкА)", size=9.5, color=MUTED, italic=True))

    p.append(line(50, 125, 830, 125, color=LINE, sw=0.8, dash="4 4"))

    # Часова шкала Class B
    p.append(text(30, 155, "Class B (Синхронізовані за маячками Beacon періодичні слоти прийому):", size=12, color=INK, bold=True, anchor="start"))

    # Маяк 1 (Beacon)
    p.append(rect(100, 180, 50, 35, fill="#fff3cd", stroke="#e0a800", sw=1.5, rx=3))
    p.append(text(125, 202, "Beacon", size=10, color="#856404", bold=True))

    # Ping Slots
    p.append(rect(220, 180, 45, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(242, 202, "Ping", size=9.5, color=NEG, bold=True))

    p.append(rect(340, 180, 45, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(362, 202, "Ping", size=9.5, color=NEG, bold=True))

    # TX Uplink у Class B
    p.append(rect(450, 180, 55, 35, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(477, 202, "TX (A)", size=10, color=POS, bold=True))

    # RX1 / RX2 після передачі
    p.append(rect(530, 180, 35, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(547, 202, "RX1", size=9, color=NEG, bold=True))

    p.append(rect(590, 180, 35, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(607, 202, "RX2", size=9, color=NEG, bold=True))

    # Маяк 2 (через 128 с)
    p.append(rect(730, 180, 50, 35, fill="#fff3cd", stroke="#e0a800", sw=1.5, rx=3))
    p.append(text(755, 202, "Beacon", size=10, color="#856404", bold=True))

    p.append(text(440, 232, "← Інтервал між маячками T_beacon = 128 секунд (GPS-синхронізація шлюзів) →", size=9.5, color=MUTED, italic=True))

    p.append(line(50, 255, 830, 255, color=LINE, sw=0.8, dash="4 4"))

    # Часова шкала Class C
    p.append(text(30, 285, "Class C (Постійно відкритий приймач, нульова затримка Downlink, живлення від мережі):", size=12, color=INK, bold=True, anchor="start"))

    # Безперервний RX2
    p.append(rect(100, 310, 120, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(160, 332, "RX2 (Постійно)", size=10, color=NEG, bold=True))

    # TX Uplink
    p.append(rect(225, 310, 55, 35, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(252, 332, "TX", size=10, color=POS, bold=True))

    # RX2 до RX1
    p.append(rect(285, 310, 45, 35, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    p.append(text(307, 332, "RX2", size=9, color=NEG))

    # RX1
    p.append(rect(335, 310, 45, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(357, 332, "RX1", size=9.5, color=NEG, bold=True))

    # Відновлення RX2
    p.append(rect(385, 310, 440, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(605, 332, "RX2 (Постійне прослуховування частоти 869.525 МГц SF9)", size=10, color=NEG, bold=True))

    # Підсумок у нижній панелі
    p.append(rect(50, 370, 760, 40, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(430, 395, "Баланс: Class A (роки від батареї) ↔ Class B (затримка секунди) ↔ Class C (миттєвий зв'язок, струм ~12 мА)", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "class-abc-timing.svg"), W, H, *p,
           title="Часові діаграми вікон прийому для класів пристроїв LoRaWAN")


# ── 3. otaa-join-procedure: Активація OTAA ─────────────────────────────────────
def fig_otaa_join():
    W, H = 860, 450
    p = []

    # Вертикальні осі учасників
    p.append(text(120, 35, "Кінцевий пристрій", size=13, color=INK, bold=True))
    p.append(text(120, 52, "(End Device)", size=11, color=MUTED))

    p.append(text(380, 35, "Шлюз / Базова станція", size=13, color=INK, bold=True))
    p.append(text(380, 52, "(Gateway / Concentrator)", size=11, color=MUTED))

    p.append(text(600, 35, "Мережевий сервер", size=13, color=INK, bold=True))
    p.append(text(600, 52, "(Network Server, NS)", size=11, color=MUTED))

    p.append(text(780, 35, "Join Server", size=13, color=INK, bold=True))
    p.append(text(780, 52, "(JS / Auth)", size=11, color=MUTED))

    p.append(line(120, 65, 120, 410, color=LINE, sw=1.5))
    p.append(line(380, 65, 380, 410, color=LINE, sw=1.5))
    p.append(line(600, 65, 600, 410, color=LINE, sw=1.5))

    # Вісь JS розривається довкола блоку обробки
    p.append(line(780, 65, 780, 150, color=LINE, sw=1.5))
    p.append(line(780, 260, 780, 410, color=LINE, sw=1.5))

    # 1. Join-Request від вузла до шлюзу
    p.append(arrow(120, 95, 380, 115, color=POS, sw=1.6))
    p.append(fitbox(150, 80, 200, 28, "1. Join-Request (RF ISM)", size=10, fill="#fdecea", stroke=POS, bold=True))

    # Пересилання від шлюзу до NS
    p.append(arrow(380, 115, 600, 130, color=POS, sw=1.5))
    p.append(text(490, 122, "IP: Forward Join-Req", size=9.5, color=POS))

    # Пересилання від NS до JS
    p.append(arrow(600, 130, 780, 145, color=POS, sw=1.5))
    p.append(text(690, 137, "Auth Req", size=9.5, color=POS))

    # Блок обробки на Join Server (з чистим відступом)
    p.append(fitbox(695, 155, 160, 100, "Обробка в JS:\n1. Перевірка DevNonce\n2. Розрахунок MIC з AppKey\n3. Генерація AppNonce\n4. Деривація NwkSKey / AppSKey\n5. Шифрування Join-Accept", size=9.5, fill="#fdecea", stroke=POS))

    # 2. Join-Accept від JS до NS
    p.append(arrow(780, 275, 600, 290, color=FIELD, sw=1.5))
    p.append(text(690, 282, "Join-Accept + NwkSKey", size=9.5, color=FIELD, bold=True))

    # Від NS до Gateway (планування TX у вікні RX1/RX2)
    p.append(arrow(600, 290, 380, 310, color=FIELD, sw=1.5))
    p.append(text(490, 300, "Schedule TX (RX1/RX2)", size=9.5, color=FIELD))

    # Від Gateway до End Device (радіоканал)
    p.append(arrow(380, 310, 120, 335, color=FIELD, sw=1.6))
    p.append(fitbox(150, 318, 200, 28, "2. Join-Accept (Зашифровано AppKey)", size=9.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Блок обробки на пристрої (розриває вісь вузла або зсунуто вбік)
    p.append(fitbox(20, 350, 200, 80, "Деривація в пристрої:\n• Дешифрування Join-Accept\n• Збереження DevAddr, NetID\n• NwkSKey = AES(AppKey, 0x01...)\n• AppSKey = AES(AppKey, 0x02...)", size=9.5, fill="#eef6ef", stroke=FIELD))

    # Блок підсумку
    p.append(fitbox(240, 365, 520, 55, "Результат OTAA:\nВузол і сервери узгодили динамічну 32-бітну адресу DevAddr та сесійні ключі NwkSKey і AppSKey.\nЛічильники FCntUp і FCntDown скинуті в 0. Пристрій готовий до передачі даних.", size=9.5, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, "otaa-join-procedure.svg"), W, H, *p,
           title="Процедура активації пристрою OTAA та деривація сесійних ключів")


# ── 4. lorawan-frame-security: Структура кадру та криптографія ─────────────────
def fig_frame_security():
    W, H = 860, 430
    p = []

    # Верхній рівень: PHYPayload
    p.append(text(430, 40, "Загальна структура кадру LoRaWAN PHYPayload:", size=13, color=INK, bold=True))

    # Поля PHYPayload
    p.append(rect(40, 60, 110, 45, fill="#fff3cd", stroke="#e0a800", sw=1.5, rx=3))
    p.append(text(95, 80, "MHDR (1 Б)", size=11, color="#856404", bold=True))
    p.append(text(95, 95, "Тип кадру, версія", size=9.5, color=MUTED))

    p.append(rect(155, 60, 550, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(430, 80, "MACPayload (7 .. 250 байтів) — Заголовок FHDR, Порт та Дані", size=11, color=NEG, bold=True))
    p.append(text(430, 95, "FHDR (7..23 Б) | FPort (0..1 Б) | FRMPayload (0..N Б)", size=9.5, color=MUTED))

    p.append(rect(710, 60, 110, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(765, 80, "MIC (4 Б)", size=11, color=POS, bold=True))
    p.append(text(765, 95, "Код цілісності", size=9.5, color=MUTED))

    # Деталізація MACPayload
    p.append(text(430, 135, "Розгортання полів MACPayload:", size=12, color=INK, bold=True))

    # FHDR поля
    p.append(rect(60, 150, 100, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=3))
    p.append(text(110, 168, "DevAddr (4 Б)", size=10, color=INK, bold=True))
    p.append(text(110, 183, "Адреса вузла", size=9.5, color=MUTED))

    p.append(rect(165, 150, 100, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=3))
    p.append(text(215, 168, "FCtrl (1 Б)", size=10, color=INK, bold=True))
    p.append(text(215, 183, "ADR, ACK, FOptsLen", size=9.5, color=MUTED))

    p.append(rect(270, 150, 100, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=3))
    p.append(text(320, 168, "FCnt (2 Б)", size=10, color=INK, bold=True))
    p.append(text(320, 183, "Лічильник кадру", size=9.5, color=MUTED))

    p.append(rect(375, 150, 110, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=3))
    p.append(text(430, 168, "FOpts (0..15 Б)", size=10, color=INK, bold=True))
    p.append(text(430, 183, "MAC-команди", size=9.5, color=MUTED))

    p.append(rect(490, 150, 80, 42, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=3))
    p.append(text(530, 168, "FPort (1 Б)", size=10, color="#856404", bold=True))
    p.append(text(530, 183, "0: MAC / 1+: App", size=9.5, color=MUTED))

    p.append(rect(575, 150, 225, 42, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(687, 168, "FRMPayload (Зашифровано AES-CTR)", size=10, color=FIELD, bold=True))
    p.append(text(687, 183, "Корисні дані датчика / додатку", size=9.5, color=MUTED))

    # Дворівневий криптографічний захист
    p.append(text(430, 225, "Дворівневе розділення криптографічних ключів:", size=12, color=INK, bold=True))

    # Рівень 1: Автентифікація мережі (NwkSKey)
    p.append(fitbox(50, 245, 360, 130, "1. Рівень мережі: Цілісність кадру (NwkSKey)\n\n• Блок B0 (DevAddr, FCnt, Len, Dir)\n• Алгоритм: AES-CMAC над (B0 | MHDR | MACPayload)\n• Результат: 4-байтний підпис MIC\n• Захищає від: підробки кадру, спотворення адрес,\n  повтору старих пакетів (Replay Attack)", size=9.5, fill="#fdecea", stroke=POS))

    # Рівень 2: Конфіденційність додатку (AppSKey)
    p.append(fitbox(450, 245, 360, 130, "2. Рівень додатку: Шифрування даних (AppSKey)\n\n• Блоки Ai (DevAddr, FCnt, BlockIndex i)\n• Алгоритм: AES-128 в режимі CTR (потоковий гаммувальний)\n• Результат: FRMPayload = Plaintext ⊕ AES(AppSKey, Ai)\n• Захищає від: перехоплення та читання даних\n  (Мережевий сервер NS не бачить вмісту FRMPayload)", size=9.5, fill="#eef6ef", stroke=FIELD))

    # Підсумковий рядок
    p.append(rect(50, 385, 760, 32, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(430, 405, "Наскрізна ізоляція: NS перевіряє MIC і керує мережею, але розшифрувати дані може лише Application Server.", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "lorawan-frame-security.svg"), W, H, *p,
           title="Структура кадру LoRaWAN MAC та схема дворівневого криптозахисту")


# ── 5. adr-state-machine: Алгоритм ADR ─────────────────────────────────────────
def fig_adr_state_machine():
    W, H = 860, 420
    p = []

    # Заголовок та підписи колонок
    p.append(text(230, 35, "Оптимізація на стороні сервера (NS)", size=13, color=FIELD, bold=True))
    p.append(text(650, 35, "Захисний відкат на стороні вузла (Node)", size=13, color=POS, bold=True))

    p.append(line(430, 45, 430, 375, color=MUTED, sw=1.2, dash="4 4"))

    # Серверна гілка ADR
    p.append(fitbox(40, 65, 360, 60, "1. Збір статистики SNR:\nNetwork Server збирає історію SNR за останні 20 пакетів.\nВизначається максимальне значення: max(SNR).", size=9.5, fill="#f4f6f8", stroke=LINE))

    p.append(arrow(220, 125, 220, 155, color=FIELD, sw=1.5))

    p.append(fitbox(40, 155, 360, 75, "2. Розрахунок запасу SNR_margin:\nSNR_margin = max(SNR) − SNR_req(DR) − Device_Margin (10 дБ)\nКількість кроків покращення: N_steps = floor(SNR_margin / 3 дБ).", size=9.5, fill="#eef6ef", stroke=FIELD))

    p.append(arrow(220, 230, 220, 260, color=FIELD, sw=1.5))

    p.append(fitbox(40, 260, 360, 95, "3. Застосування кроків (LinkADRReq):\n• Крок 1: Зменшення SF (SF12 → SF11 → ... → SF7) → скорочення ToA.\n• Крок 2: Зниження TX Power (14 дБм → 12 → ... → 2 дБм) → економія батареї.\n• Сервер надсилає команду LinkADRReq у найближчому Downlink.", size=9.5, fill="#eef6ef", stroke=FIELD))

    # Клієнтська гілка ADR (Втрата зв'язку та відновлення)
    p.append(fitbox(460, 65, 360, 60, "1. Підрахунок пакетів без підтвердження:\nПристрій інкрементує лічильник ADR_ACK_CNT.\nЯкщо за 64 пакети немає Downlink — виставляється біт ADRACKReq.", size=9.5, fill="#f4f6f8", stroke=LINE))

    p.append(arrow(640, 125, 640, 155, color=POS, sw=1.5))

    p.append(fitbox(460, 155, 360, 75, "2. Очікування відповіді (ADR_ACK_DELAY):\nЯкщо за наступні 32 пакети Downlink так і не отримано:\nПристрій перемикає потужність передавача TX Power на максимум (+14 дБм).", size=9.5, fill="#fdecea", stroke=POS))

    p.append(arrow(640, 230, 640, 260, color=POS, sw=1.5))

    p.append(fitbox(460, 260, 360, 95, "3. Покрокове підвищення коефіцієнта розширення:\n• Кожні наступні 32 передачі SF збільшується на 1 (SF7 → SF8 → ... → SF12).\n• Якщо досягнуто SF12 і зв'язку немає — скидання на базові канали (868.1–868.5).\n• Досягається максимальна дальність для відновлення контакту.", size=9.5, fill="#fdecea", stroke=POS))

    # Нижній висновок
    p.append(rect(40, 375, 780, 35, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(430, 397, "Баланс ADR: мінімальний час у ефірі та найнижче споживання в нормі + надійний автоматичний вихід із глухого кута.", size=9.5, color=INK, bold=True))

    render(os.path.join(OUT, "adr-state-machine.svg"), W, H, *p,
           title="Алгоритм динамічного керування швидкістю (ADR) та аварійного відновлення зв'язку")


def main():
    fig_topology()
    fig_class_timing()
    fig_otaa_join()
    fig_frame_security()
    fig_adr_state_machine()
    print("Усі 5 фігур успішно згенеровано у ./img/")

if __name__ == "__main__":
    main()
