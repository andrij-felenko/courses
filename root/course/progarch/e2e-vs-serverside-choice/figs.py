# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_data_trust_boundary_tradeoff():
    """Порівняння меж довіри та доступу до відкритого тексту між Server-Side Encryption та End-to-End Encryption."""
    W, H = 1040, 480
    f = []

    # ── Секція 1: Server-Side Encryption (SSE) ──
    f.append(fitbox(520, 32, 400, 30, "1. Server-Side Encryption (SSE) — Хмара бачить відкритий текст", size=13, bold=True, fill=BG, stroke=MUTED, color=MUTED))
    
    # Клієнт
    f.append(fitbox(100, 100, 140, 60, "Клієнт\n(App)", size=13, bold=True, fill=BLUE_T, stroke=NEG))
    # Стрелка TLS
    f.append(arrow(170, 100, 260, 100))
    f.append(text(215, 88, "TLS", size=11, color=MUTED))

    # Межа довіри хмари (пунктир)
    f.append(line(260, 50, 260, 180, color=MUTED, sw=1.5, dash="5 4"))
    f.append(text(260, 42, "Межа хмари", size=10, color=MUTED, anchor="middle"))

    # Сервер застосунку + KMS
    f.append(fitbox(370, 100, 180, 70, "Сервер / RAM\n[Відкритий текст]\nAI · Пошук · Логи", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(600, 100, 130, 50, "KMS\n(KEK/DEK)", size=12, fill=NEUT, stroke=INK))
    f.append(line(460, 100, 535, 100, color=LINE, sw=1.5))

    # БД
    f.append(arrow(460, 115, 780, 115))
    f.append(fitbox(870, 100, 150, 60, "База даних\n[Зашифровано на диску]", size=12, fill=GREEN_T, stroke=FIELD))

    # Коментар під SSE
    f.append(text(520, 175, "Захищає від украдених дисків/дампів. Але зламаний сервер або інсайдер бачить відкритий текст.", size=11, color=MUTED))

    # Розділювальна лінія між SSE та E2E
    f.append(line(40, 210, 1000, 210, color="#d0d7de", sw=1.5))

    # ── Секція 2: End-to-End Encryption (E2E) ──
    f.append(fitbox(520, 235, 400, 30, "2. End-to-End Encryption (E2E) — Сервер бачить лише непрозорий шифротекст", size=13, bold=True, fill=BG, stroke=MUTED, color=MUTED))

    # Клієнт А (Ключ K)
    f.append(fitbox(100, 330, 150, 75, "Клієнт A / Пристрій\nКлюч K у RAM\n[Шифрує E2E]", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Стрелка до сервера
    f.append(arrow(175, 330, 360, 330))
    f.append(text(265, 315, "Шифротекст (E2E)", size=11, color=POS, bold=True))

    # Сервер застосунку (Осліплений)
    f.append(fitbox(480, 330, 210, 85, "Сервер Хмари\n[ОСЛІПЛЕНИЙ]\nТільки маршрутизація\nПошук і AI НЕ працюють!", size=12, bold=True, fill=RED_T, stroke=POS))

    # Стрелка до Клієнта Б
    f.append(arrow(585, 330, 790, 330))
    f.append(text(685, 315, "Шифротекст (E2E)", size=11, color=POS, bold=True))

    # Клієнт Б (Ключ K)
    f.append(fitbox(870, 330, 150, 75, "Клієнт B / Приймач\nКлюч K у RAM\n[Розшифровує E2E]", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Коментар під E2E
    f.append(text(520, 435, "Сервер повністю осліплений. Zero-Trust приватність, але фічі аналітики та пошуку на сервері мертві.", size=11, color=MUTED))

    render(os.path.join(OUT, 'data-trust-boundary-tradeoff.svg'), W, H, *f,
           title="Межі довіри: Server-Side Encryption проти End-to-End Encryption")


def fig_capability_matrix_split():
    """Таксономія архітектурних компромісів між SSE, Edge-обробкою та E2E."""
    W, H = 960, 420
    f = []

    f.append(fitbox(480, 30, 500, 34, "Компроміси можливостей за вибором шифрування", size=15, bold=True, fill=NEUT, stroke=INK))

    # Заголовки стовпчиків
    headers = [
        (80, 80, 200, "Властивість / Фіча"),
        (330, 80, 190, "Server-Side (SSE)"),
        (560, 80, 190, "Edge Hub + E2E"),
        (790, 80, 190, "Full End-to-End (E2E)"),
    ]
    for x, y, w, title in headers:
        f.append(fitbox(x + w/2, y + 18, w, 36, title, size=12, bold=True, fill=BG, stroke=INK))

    rows = [
        ("Повнотекстовий пошук", "Повний на сервері", "Локальний на хабі", "Неможливий на сервері"),
        ("AI аналітика відео", "Хмарні GPU / AI", "Локальний NPU хаба", "Тільки на пристрої"),
        ("Агрегація & Звіти", "Легка (SQL / OLAP)", "Складна / Стрімінг", "Неможлива"),
        ("Відновлення ключа", "Просте (KMS / Auth)", "За паролем / Escrow", "Втрата даних при втраті ключа"),
        ("Захист від інсайдера", "Ні (хмара бачить)", "Частковий (Edge)", "Повний (Zero-Trust)"),
    ]

    colors_sse = [GREEN_T, GREEN_T, GREEN_T, GREEN_T, RED_T]
    colors_edge = [BLUE_T, BLUE_T, BLUE_T, BLUE_T, GREEN_T]
    colors_e2e = [RED_T, RED_T, RED_T, RED_T, GREEN_T]

    for i, (feat, sse_v, edge_v, e2e_v) in enumerate(rows):
        cy = 145 + i * 50
        f.append(fitbox(180, cy, 200, 42, feat, size=12, bold=True, fill=NEUT, stroke="#c8ced6"))
        f.append(fitbox(425, cy, 190, 42, sse_v, size=11, fill=colors_sse[i], stroke=MUTED))
        f.append(fitbox(655, cy, 190, 42, edge_v, size=11, fill=colors_edge[i], stroke=MUTED))
        f.append(fitbox(885, cy, 190, 42, e2e_v, size=11, fill=colors_e2e[i], stroke=MUTED))

    render(os.path.join(OUT, 'capability-matrix-split.svg'), W, H, *f,
           title="Матриця компромісів: SSE, Edge та E2E")


def fig_dh_domain_crypto_split():
    """Схема розділення класів даних Digital Homes (DH) за режимами шифрування."""
    W, H = 1020, 440
    f = []

    f.append(fitbox(510, 32, 540, 34, "Розподіл класів даних Digital Homes (DH) за режимами криптозахисту", size=14, bold=True, fill=NEUT, stroke=INK))

    # Джерела даних ліворуч
    f.append(fitbox(130, 110, 200, 55, "Розумний замок\n[Команди відчинення]", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(130, 200, 200, 55, "Камера вітальні\n[Live-відеопотік]", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(130, 290, 200, 55, "Детекція руху\n[AI аналітика кадру]", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(130, 380, 200, 55, "Телеметрія & Білінг\n[Батарея, логи, рахунки]", size=12, bold=True, fill=BLUE_T, stroke=NEG))

    # Центральний шар — Вибір режиму та класифікація
    f.append(fitbox(460, 110, 240, 55, "Клас A1: Підписані команди\nE2E Integrity & ECDSA", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(460, 200, 240, 55, "Клас A2: Live Stream E2E\nWebRTC / DTLS-SRTP", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(460, 290, 240, 55, "Клас B: AI Detection\nEdge Hub / Hybrid SSE", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(460, 380, 240, 55, "Клас C: Телеметрія & БД\nServer-Side KMS Envelope", size=12, bold=True, fill=NEUT, stroke=MUTED))

    # Стрілки від джерел до класів
    f.append(arrow(230, 110, 340, 110))
    f.append(arrow(230, 200, 340, 200))
    f.append(arrow(230, 290, 340, 290))
    f.append(arrow(230, 380, 340, 380))

    # Правий шар — Наслідки для архітектури
    f.append(fitbox(820, 110, 240, 55, "Захист від спуфінгу\nХмара не створить ключ", size=11, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(820, 200, 240, 55, "Zero-Knowledge медіа\nХмара лише маршрутизує", size=11, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(820, 290, 240, 55, "Локальна аналітика\nабо доступ для Cloud AI", size=11, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(820, 380, 240, 55, "Шифрування дисків / БД\nПовнотекстовий пошук живий", size=11, fill=NEUT, stroke=MUTED))

    # Стрілки до наслідків
    f.append(arrow(580, 110, 700, 110))
    f.append(arrow(580, 200, 700, 200))
    f.append(arrow(580, 290, 700, 290))
    f.append(arrow(580, 380, 700, 380))

    render(os.path.join(OUT, 'dh-domain-crypto-split.svg'), W, H, *f,
           title="Класифікація даних Digital Homes та їх криптографічні режими")


if __name__ == "__main__":
    fig_data_trust_boundary_tradeoff()
    fig_capability_matrix_split()
    fig_dh_domain_crypto_split()
    print("Figures generated successfully.")
