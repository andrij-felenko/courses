# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ENC   = "#c0392b"      # зашифроване — гаряче/червоне
ENCF  = "#fdecea"
AUTH  = "#2457d6"      # автентифікація — синє
AUTHF = "#eaf0fd"
CLR   = "#4b5563"      # відкритий заголовок — нейтральний
CLRF  = "#f3f4f6"
OK    = "#27ae60"      # спільне/перевірене — зелене
OKF   = "#eafaf0"
WARN  = "#d97706"      # застереження/спеціальні прапорці
WARNF = "#fef3c7"


# ── 1. srtp-packet-layout: структура пакета SRTP і межі захисту ───────────────
def fig_srtp_packet_layout():
    W, H = 1000, 460
    p = []

    # Заголовок блоків пакета
    p.append(fitbox(40, 20, 920, 40,
                    "Структура пакета SRTP (RFC 3711) і розмежування шифрування та автентифікації",
                    size=14, bold=True, fill=CLRF, stroke=LINE, sw=1.5))

    # Складові частини пакета (y=80, h=90)
    p.append(fitbox(40, 80, 180, 90,
                    "RTP Header (12 Б)\n• V, P, X, CC, M, PT\n• Sequence Number\n• Timestamp, SSRC",
                    size=11, fill=CLRF, stroke=LINE, sw=1.8, color=CLR))

    p.append(fitbox(230, 80, 130, 90,
                    "RTP Ext (опція)\n• Profile data\n• Гучність звуку\n• Поворот кадру",
                    size=11, fill=CLRF, stroke=LINE, sw=1.8, color=CLR))

    p.append(fitbox(370, 80, 370, 90,
                    "RTP Payload (корисне навантаження)\nЗашифровано блоковим шифром AES-CTR / AES-f8\nАудіо (Opus, G.711) або відео (H.264, VP9, AV1)",
                    size=11, fill=ENCF, stroke=ENC, sw=1.8, color=ENC))

    p.append(fitbox(750, 80, 60, 90,
                    "MKI\n(опц.)",
                    size=11, fill=WARNF, stroke=WARN, sw=1.8, color=WARN))

    p.append(fitbox(820, 80, 140, 90,
                    "Auth Tag (4–10 Б)\nHMAC-SHA1-80 / 32\nабо тег AEAD (16 Б)\n(контроль цілісності)",
                    size=11, fill=AUTHF, stroke=AUTH, sw=1.8, color=AUTH))

    # Дужка шифрування (Payload: x=370..740)
    y_enc = 200
    p.append(line(370, y_enc, 740, y_enc, color=ENC, sw=2))
    p.append(line(370, y_enc - 6, 370, y_enc + 6, color=ENC, sw=2))
    p.append(line(740, y_enc - 6, 740, y_enc + 6, color=ENC, sw=2))
    p.append(fitbox(370, y_enc + 15, 370, 44,
                    "Область ШИФРУВАННЯ: тільки тіло корисного навантаження\n(заголовки відкриті для маршрутизаторів SFU та буферів джитера)",
                    size=11, fill=ENCF, stroke=ENC, sw=1.2, color=ENC))

    # Дужка автентифікації (Header + Ext + Payload + MKI: x=40..810)
    y_auth = 295
    p.append(line(40, y_auth, 810, y_auth, color=AUTH, sw=2))
    p.append(line(40, y_auth - 6, 40, y_auth + 6, color=AUTH, sw=2))
    p.append(line(810, y_auth - 6, 810, y_auth + 6, color=AUTH, sw=2))
    p.append(fitbox(40, y_auth + 15, 770, 52,
                    "Область АВТЕНТИФІКАЦІЇ (HMAC-SHA1): заголовок + розширення + шифротекст + ROC\n"
                    "Тег обчислюється поверх шифротексту (Encrypt-then-MAC), захищаючи послідовність і підміну",
                    size=11, fill=AUTHF, stroke=AUTH, sw=1.2, color=AUTH))

    # Стрілка від автентифікації до тега
    p.append(arrow(815, y_auth + 20, 890, 175, color=AUTH, sw=2))

    render(os.path.join(OUT, "srtp-packet-layout.svg"), W, H, *p)


# ── 2. srtp-kdf-pipeline: генерація сесійних ключів через PRF на базі AES ──────
def fig_srtp_kdf_pipeline():
    W, H = 1000, 460
    p = []

    # Верх: майстер-ключ і майстер-сіль
    p.append(fitbox(60, 25, 410, 60,
                    "Master Key (128 / 192 / 256 бітів)\nТаємний ключ довготривалої сесії",
                    size=13, bold=True, fill=OKF, stroke=OK, sw=1.8, color=INK))

    p.append(fitbox(530, 25, 410, 60,
                    "Master Salt (112 бітів)\nКриптографічна сіль проти колізій і райдужних таблиць",
                    size=13, bold=True, fill=WARNF, stroke=WARN, sw=1.8, color=INK))

    # Стрілки до центрального блоку
    p.append(arrow(265, 85, 380, 125, color=OK, sw=2))
    p.append(arrow(735, 85, 620, 125, color=WARN, sw=2))

    # Центральний блок: формула KDF
    p.append(fitbox(60, 125, 880, 95,
                    "KDF (Key Derivation Function на базі AES-CTR PRF)\n"
                    "IV = (Master_Salt ⊕ (Label || (Index ÷ KDR))) · 2¹⁶\n"
                    "Key_Stream = AES_MasterKey(IV || 0) || AES_MasterKey(IV || 1) ...\n"
                    "де Label: 0x00 = SRTP Encrypt, 0x01 = SRTP Auth, 0x02 = SRTP Salt (0x03..0x05 для SRTCP)",
                    size=12, fill=CLRF, stroke=LINE, sw=1.8, color=INK))

    # Стрілки від KDF до ключів
    p.append(arrow(200, 220, 200, 275, color=ENC, sw=2))
    p.append(arrow(500, 220, 500, 275, color=AUTH, sw=2))
    p.append(arrow(800, 220, 800, 275, color=WARN, sw=2))

    # Вихідні сесійні ключі
    p.append(fitbox(60, 275, 275, 120,
                    "SRTP Encryption Key (k_e)\n• Розмір: 128 / 256 бітів\n• Label = 0x00\n• Для гами AES-CTR / f8 payload",
                    size=11, fill=ENCF, stroke=ENC, sw=1.8, color=ENC))

    p.append(fitbox(365, 275, 275, 120,
                    "SRTP Authentication Key (k_a)\n• Розмір: 160 бітів (SHA-1)\n• Label = 0x01\n• Для HMAC-SHA1 тега цілісності",
                    size=11, fill=AUTHF, stroke=AUTH, sw=1.8, color=AUTH))

    p.append(fitbox(670, 275, 270, 120,
                    "SRTP Salting Key (k_s)\n• Розмір: 112 бітів\n• Label = 0x02\n• Для змішування з SSRC та Index в IV",
                    size=11, fill=WARNF, stroke=WARN, sw=1.8, color=WARN))

    render(os.path.join(OUT, "srtp-kdf-pipeline.svg"), W, H, *p)


# ── 3. roc-packet-index: 48-бітний індекс пакета та Rollover Counter ─────────
def fig_roc_packet_index():
    W, H = 1000, 460
    p = []

    # Верх: розгортання SEQ у 48-бітний Index
    p.append(fitbox(50, 20, 900, 48,
                    "Розгортання 16-бітного SEQ у 48-бітний Packet Index (i = 2¹⁶ · ROC + SEQ)\n"
                    "Запобігає колізіям IV у шифрі AES-CTR при переповненні лічильника через кожні 65 536 пакетів",
                    size=12, bold=True, fill=OKF, stroke=OK, sw=1.8, color=INK))

    # Схема складання індексу
    p.append(fitbox(50, 95, 420, 60,
                    "Rollover Counter (ROC, 32 біти)\nЗберігається локально отримувачем (не передається в мережу!)",
                    size=12, fill=AUTHF, stroke=AUTH, sw=1.8, color=AUTH))

    p.append(fitbox(530, 95, 420, 60,
                    "Sequence Number (SEQ, 16 бітів)\nПередається у заголовку кожного пакета RTP",
                    size=12, fill=WARNF, stroke=WARN, sw=1.8, color=WARN))

    p.append(arrow(260, 155, 360, 195, color=AUTH, sw=2))
    p.append(arrow(740, 155, 640, 195, color=WARN, sw=2))

    p.append(fitbox(150, 195, 700, 50,
                    "48-бітний абсолютний індекс пакета i = (ROC << 16) | SEQ\n"
                    "Гарантує унікальність пари (Key, IV) для 2⁴⁸ пакетів (~280 трильйонів пакетів)",
                    size=12, fill=CLRF, stroke=LINE, sw=1.8, color=INK))

    # Нижній блок: обробка на межі переповнення та ковзне вікно (Replay Window)
    p.append(fitbox(50, 275, 900, 130,
                    "Автоматичне відновлення ROC при порушенні порядку доставки (Out-of-Order):\n"
                    "• Якщо s_l < 32768 і SEQ - s_l > 32768 (запізнілий пакет з попередньої епохи) → ROC_est = ROC - 1\n"
                    "• Якщо s_l >= 32768 і s_l - SEQ > 32768 (перехід через 65535 → 0) → ROC_est = ROC + 1 (після перевірки тега ROC = ROC + 1)\n"
                    "• Replay Protection Window: бітова маска 64/128 пакетів захищає від атак повторного відтворення",
                    size=11, fill=FILL, stroke=LINE, sw=1.5, color=INK))

    render(os.path.join(OUT, "roc-packet-index.svg"), W, H, *p)


# ── 4. dtls-srtp-handshake: узгодження ключів DTLS-SRTP та потік медіа ─────────
def fig_dtls_srtp_handshake():
    W, H = 1000, 520
    p = []

    # Колонка Аліси і Боба (центри x=140 і x=860)
    p.append(fitbox(50, 20, 180, 45, "Клієнт A\n(WebRTC / SIP)", size=12, bold=True, fill=CLRF, stroke=LINE, sw=1.8))
    p.append(fitbox(770, 20, 180, 45, "Клієнт B\n(або Медіасервер SFU)", size=12, bold=True, fill=CLRF, stroke=LINE, sw=1.8))

    # Пунктирні лінії життя (сегменти між блоками, щоб лінія не перетинала написи)
    p.append(line(140, 65, 140, 265, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(140, 315, 140, 500, color=MUTED, sw=1.5, dash="4 4"))

    p.append(line(860, 65, 860, 265, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(860, 315, 860, 500, color=MUTED, sw=1.5, dash="4 4"))

    # Фаза 1: Сигналізація (SDP Offer / Answer з відбитком сертифіката)
    y1 = 95
    p.append(arrow(150, y1, 850, y1, color=WARN, sw=1.8))
    p.append(fitbox(250, y1 - 25, 500, 24,
                    "1. Сигналізація SDP (HTTPS / WSS / SIP): a=fingerprint:sha-256 ...",
                    size=11, fill=WARNF, stroke=WARN, sw=1.2, color=WARN))

    # Фаза 2: DTLS Handshake з розширенням use_srtp
    y2 = 155
    p.append(arrow(150, y2, 850, y2, color=AUTH, sw=1.8))
    p.append(fitbox(250, y2 - 25, 500, 24,
                    "2. DTLS 1.2 / 1.3 ClientHello (розширення use_srtp: SRTP_AES128_CM_HMAC_SHA1_80)",
                    size=11, fill=AUTHF, stroke=AUTH, sw=1.2, color=AUTH))

    y3 = 215
    p.append(arrow(850, y3, 150, y3, color=AUTH, sw=1.8))
    p.append(fitbox(250, y3 - 25, 500, 24,
                    "3. DTLS ServerHello, Certificate, KeyExchange, Finished",
                    size=11, fill=AUTHF, stroke=AUTH, sw=1.2, color=AUTH))

    # Фаза 3: Експорт ключів SRTP (RFC 5705)
    y4 = 265
    p.append(fitbox(50, y4, 180, 50, "RFC 5705 Exporter:\nвитягує Master Key", size=10, fill=OKF, stroke=OK, sw=1.5))
    p.append(fitbox(770, y4, 180, 50, "RFC 5705 Exporter:\nвитягує Master Key", size=10, fill=OKF, stroke=OK, sw=1.5))

    p.append(fitbox(250, y4, 500, 50,
                    "Локальне виведення ключів (Zero Knowledge для сигналізації!)\n"
                    "Пряме генерування симетричних ключів SRTP з DTLS master_secret",
                    size=11, fill=OKF, stroke=OK, sw=1.2, color=OK))

    # Фаза 4: Потік медіа SRTP / SRTCP
    y5 = 370
    p.append(arrow(150, y5, 850, y5, color=ENC, sw=2.2))
    p.append(fitbox(250, y5 - 25, 500, 24,
                    "4. SRTP Media (UDP): Зашифрований аудіо/відео потік (AES-CTR + HMAC-SHA1)",
                    size=11, fill=ENCF, stroke=ENC, sw=1.5, color=ENC))

    y6 = 440
    p.append(arrow(850, y6, 150, y6, color=ENC, sw=2.2))
    p.append(fitbox(250, y6 - 25, 500, 24,
                    "5. SRTCP Control (UDP): Зашифрована телеметрія та зворотний зв'язок якості",
                    size=11, fill=ENCF, stroke=ENC, sw=1.5, color=ENC))

    render(os.path.join(OUT, "dtls-srtp-handshake.svg"), W, H, *p)


if __name__ == "__main__":
    fig_srtp_packet_layout()
    fig_srtp_kdf_pipeline()
    fig_roc_packet_index()
    fig_dtls_srtp_handshake()
    print("All figures generated successfully.")
