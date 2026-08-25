# -*- coding: utf-8 -*-
"""Фігури до теми «Криптографія з відкритим ключем: ключі, підпис, ланцюг сертифікатів»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT_BLUE   = "#eef4fb"
SOFT_GREEN  = "#eaf7ee"
SOFT_ORANGE = "#fdf3e6"
SOFT_RED    = "#fdecea"
SOFT_PURPLE = "#f4eefb"
BORDER_BLUE = "#b8d2ee"
BORDER_GRN  = "#a8e0b6"
BORDER_ORG  = "#f0d5b0"
BORDER_RED  = "#f3b8b2"
BORDER_PRP  = "#d7c0ee"

def box(cx, cy, s, size=13, fill=FILL, bold=False, stroke=LINE):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Асиметрична парадигма: секретний капкан і відкритий замок
# ─────────────────────────────────────────────────────────────────────────────
def fig_asymmetric_paradigm():
    W, H = 1000, 480
    f = []

    f.append(text(W / 2, 32, "Асиметрична модель: розділення повноважень шифрування та підпису", size=15, bold=True))

    # Ліва колонка: Генерація пари та відкритий канал
    f.append(rect(40, 65, 420, 380, fill=SOFT_BLUE, stroke=BORDER_BLUE, rx=8))
    f.append(text(250, 95, "Власник ключів (Аліса)", size=14, bold=True, color=NEG))

    gen_box, _, _ = box(250, 150, "Генератор пари ключів\nОдностороння функція з секретом (Trapdoor)", size=12, fill="#ffffff", stroke=BORDER_BLUE)
    f.append(gen_box)

    f.append(arrow(250, 185, 140, 240, color=POS))
    f.append(arrow(250, 185, 360, 240, color=FIELD))

    sk_box, _, _ = box(140, 275, "Таємний ключ (sk)\nЗберігається в таємниці\n(HSM, TPM, закритий файл)\n\n• Розшифрування\n• Створення підпису", size=11, fill=SOFT_RED, stroke=BORDER_RED, bold=True)
    f.append(sk_box)

    pk_box, _, _ = box(360, 275, "Відкритий ключ (pk)\nПублікується відкрито\n(DNS, сертифікат, каталог)\n\n• Зашифрування\n• Перевірка підпису", size=11, fill=SOFT_GREEN, stroke=BORDER_GRN, bold=True)
    f.append(pk_box)

    f.append(text(250, 420, "Математичний капкан: sk → pk обчислюється легко,\nале pk → sk обчислювально неможливо", size=11, color=MUTED))

    # Права колонка: Відкрита мережа та користувач (Боб)
    f.append(rect(520, 65, 440, 380, fill=SOFT_ORANGE, stroke=BORDER_ORG, rx=8))
    f.append(text(740, 95, "Відкритий зв'язок (Боб і Мережа)", size=14, bold=True, color=POS))

    c1, _, _ = box(740, 160, "Операція 1: Конфіденційність (Шифрування)\nБоб бере відкритий ключ Аліси pk:\nШифротекст = Encrypt(pk, Повідомлення)\nЛише Аліса може розкрити: Повідомлення = Decrypt(sk, Шифротекст)", size=11, fill="#ffffff", stroke=BORDER_ORG)
    f.append(c1)

    c2, _, _ = box(740, 280, "Операція 2: Автентичність (Цифровий підпис)\nАліса підписує своїм таємним ключем sk:\nПідпис = Sign(sk, Геш_Повідомлення)\nБудь-хто перевіряє через pk: Verify(pk, Геш, Підпис) == OK", size=11, fill="#ffffff", stroke=BORDER_ORG)
    f.append(c2)

    f.append(text(740, 410, "Передавання через незахищений канал: відсутня потреба\nпопередньо узгоджувати спільний таємний пароль", size=11, color=MUTED))

    render(os.path.join(OUT, 'asymmetric-paradigm.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Повний цикл цифрового підпису: Sign і Verify
# ─────────────────────────────────────────────────────────────────────────────
def fig_digital_signature_flow():
    W, H = 1100, 520
    f = []

    f.append(text(W / 2, 30, "Механізм цифрового підпису: гешування, створення та перевірка", size=15, bold=True))

    # Верхній блок: Відправник (Створення підпису)
    f.append(rect(40, 60, 1020, 185, fill=SOFT_RED, stroke=BORDER_RED, rx=8))
    f.append(text(120, 85, "СТВОРЕННЯ (Sign)", size=13, bold=True, color=POS))

    b_msg, _, _ = box(150, 145, "Вихідне повідомлення (M)\n(довільного розміру)", size=11, fill="#ffffff")
    f.append(b_msg)

    f.append(arrow(245, 145, 330, 145, color=LINE))
    f.append(text(287, 135, "SHA-256", size=10, color=MUTED))

    b_hash, _, _ = box(420, 145, "Криптографічний геш h\n(фіксовані 256 бітів:\nнезворотний, унікальний)", size=11, fill=SOFT_ORANGE, stroke=BORDER_ORG)
    f.append(b_hash)

    f.append(arrow(515, 145, 600, 145, color=LINE))

    b_sk, _, _ = box(700, 95, "Таємний ключ (sk)\n(відомий тільки автору)", size=11, fill="#ffffff", stroke=POS, bold=True)
    f.append(b_sk)
    f.append(arrow(700, 120, 700, 145, color=POS))

    b_sign, _, _ = box(700, 165, "Асиметричне перетворення\nПідпис σ = Sign(sk, h)", size=11, fill=SOFT_PURPLE, stroke=BORDER_PRP)
    f.append(b_sign)

    f.append(arrow(805, 165, 890, 165, color=LINE))

    b_pkg, _, _ = box(970, 150, "Пакет передавання:\n[ Повідомлення M ]\n[ Цифровий підпис σ ]", size=11, fill="#ffffff", stroke=LINE, bold=True)
    f.append(b_pkg)

    # Канал передавання
    f.append(arrow(970, 245, 970, 280, color=MUTED, sw=2.0))
    f.append(text(920, 265, "Мережа", size=11, color=MUTED))

    # Нижній блок: Отримувач (Перевірка підпису)
    f.append(rect(40, 280, 1020, 215, fill=SOFT_GREEN, stroke=BORDER_GRN, rx=8))
    f.append(text(125, 305, "ПЕРЕВІРКА (Verify)", size=13, bold=True, color=FIELD))

    b_rx_m, _, _ = box(150, 360, "Отримане повідомлення M'", size=11, fill="#ffffff")
    f.append(b_rx_m)

    f.append(arrow(245, 360, 330, 360, color=LINE))
    f.append(text(287, 350, "SHA-256", size=10, color=MUTED))

    b_rx_h, _, _ = box(420, 360, "Обчислений геш h'\n= SHA-256(M')", size=11, fill=SOFT_ORANGE, stroke=BORDER_ORG)
    f.append(b_rx_h)

    b_rx_sig, _, _ = box(150, 445, "Отриманий підпис σ", size=11, fill="#ffffff")
    f.append(b_rx_sig)

    b_pk, _, _ = box(420, 445, "Відкритий ключ автора (pk)\n(отриманий із сертифіката)", size=11, fill="#ffffff", stroke=FIELD, bold=True)
    f.append(b_pk)

    f.append(arrow(230, 445, 310, 445, color=LINE))
    f.append(arrow(530, 445, 620, 445, color=LINE))

    b_verify, _, _ = box(710, 445, "Алгоритм перевірки:\nВідновлення геша h_ver = Dec(pk, σ)\n(або перевірка рівняння кривої)", size=11, fill=SOFT_PURPLE, stroke=BORDER_PRP)
    f.append(b_verify)

    f.append(arrow(515, 360, 780, 360, color=LINE))
    f.append(arrow(780, 360, 850, 395, color=LINE))
    f.append(arrow(800, 445, 850, 415, color=LINE))

    b_cmp, _, _ = box(930, 405, "Порівняння h' == h_ver:\n✓ OK: Цілісність + Авторство\n✗ FAIL: Підробка чи спотворення", size=11, fill="#ffffff", stroke=FIELD, bold=True)
    f.append(b_cmp)

    render(os.path.join(OUT, 'digital-signature-flow.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Анатомія сертифіката X.509 v3 (ASN.1 DER)
# ─────────────────────────────────────────────────────────────────────────────
def fig_x509_certificate_structure():
    W, H = 1060, 580
    f = []

    f.append(text(W / 2, 28, "Структура цифрового сертифіката X.509 v3 (RFC 5280)", size=15, bold=True))

    # Головний контейнер Certificate SEQUENCE
    f.append(rect(40, 50, 980, 505, fill="#f8fafc", stroke=LINE, rx=8, sw=2.0))
    f.append(text(180, 75, "Certificate (ASN.1 SEQUENCE)", size=13, bold=True))

    # TBSCertificate (To Be Signed)
    f.append(rect(65, 95, 930, 345, fill=SOFT_BLUE, stroke=BORDER_BLUE, rx=6))
    f.append(text(240, 120, "1. TBSCertificate (Тіло даних, що підписуються)", size=13, bold=True, color=NEG))

    fields = [
        ("Version", "v3 (значення 0x02) — відкриває підтримку розширень"),
        ("SerialNumber", "Унікальний цілочисельний номер у межах видавця (до 20 байтів)"),
        ("SignatureAlgorithm", "Ідентифікатор алгоритму підпису (наприклад, ecdsa-with-SHA256 OID)"),
        ("Issuer DN", "Відмітне ім'я засвідчувального центру (C=UA, O=National CA, CN=Root CA)"),
        ("Validity", "Часове вікно чинності: [NotBefore: UTCtime, NotAfter: UTCtime]"),
        ("Subject DN", "Відмітне ім'я власника сертифіката (CN=api.service.gov.ua)"),
        ("SubjectPublicKeyInfo", "Відкритий ключ власника + алгоритм (OID id-ecPublicKey, крива secp256r1)"),
    ]

    y = 148
    for name, desc in fields:
        b_f, _, _ = box(200, y, name, size=11, fill="#ffffff", stroke=BORDER_BLUE, bold=True)
        f.append(b_f)
        f.append(text(295, y + 4, desc, size=11, color=INK, anchor="start"))
        y += 26

    # Розширення X.509 Extensions
    f.append(rect(85, 335, 890, 92, fill="#ffffff", stroke=BORDER_BLUE, rx=4))
    f.append(text(165, 355, "Extensions [v3]:", size=11, bold=True, color=NEG))

    exts = [
        ("Basic Constraints", "CA: FALSE, pathLen: none (визначає, чи може бути центром видачі)"),
        ("Key Usage", "digitalSignature, keyEncipherment (критичні прапорці дозволених операцій)"),
        ("Subject Alt Name (SAN)", "DNS:api.service.gov.ua, DNS:service.gov.ua (дійсні доменні імена)"),
        ("AIA / CRL Distribution", "URI для перевірки статусу: OCSP Responder URL + CRL HTTP URL"),
    ]
    y_ext = 375
    for ename, edesc in exts:
        f.append(text(105, y_ext, "• " + ename + ":", size=10, bold=True, anchor="start"))
        f.append(text(275, y_ext, edesc, size=10, color=MUTED, anchor="start"))
        y_ext += 17

    # Поля підпису (поза TBS)
    f.append(rect(65, 455, 930, 85, fill=SOFT_RED, stroke=BORDER_RED, rx=6))
    f.append(text(220, 480, "2. SignatureAlgorithm & SignatureValue", size=13, bold=True, color=POS))

    b_sa, _, _ = box(230, 510, "SignatureAlgorithm: ecdsa-with-SHA256", size=11, fill="#ffffff", stroke=BORDER_RED)
    f.append(b_sa)

    b_sv, _, _ = box(680, 510, "SignatureValue: BIT STRING (криптографічний підпис видавця\nнад бінарним ASN.1 DER представленням TBSCertificate)", size=11, fill="#ffffff", stroke=BORDER_RED, bold=True)
    f.append(b_sv)

    render(os.path.join(OUT, 'x509-certificate-structure.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Ланцюг довіри PKI: Root CA -> Intermediate CA -> Leaf
# ─────────────────────────────────────────────────────────────────────────────
def fig_trust_chain_hierarchy():
    W, H = 1080, 520
    f = []

    f.append(text(W / 2, 28, "Ієрархія PKI та перевірка ланцюга довіри (Trust Chain)", size=15, bold=True))

    # Рівень 1: Root CA
    f.append(rect(40, 55, 460, 125, fill=SOFT_PURPLE, stroke=BORDER_PRP, rx=8))
    f.append(text(270, 78, "1. Кореневий центр (Root CA)", size=13, bold=True, color=INK))
    f.append(mtext(270, 98, [
        "Subject: DigiCert Global Root G2",
        "Issuer: DigiCert Global Root G2 (Самопідписаний)",
        "BasicConstraints: CA=TRUE (без обмеження довжини)"
    ], size=10, color=MUTED, lh=1.25))
    f.append(text(270, 160, "Відкритий ключ: Root_PK (зашитий у сховище довіри ОС)", size=11, bold=True, color=POS))

    # Сховище ОС праворуч
    f.append(rect(580, 55, 460, 125, fill=SOFT_GREEN, stroke=BORDER_GRN, rx=8))
    f.append(text(810, 78, "Локальне сховище довіри клієнта (Trust Store)", size=12, bold=True, color=FIELD))
    f.append(mtext(810, 100, [
        "Операційна система / Браузер містить ~150 кореневих ключів.",
        "Клієнт безумовно довіряє Root_PK, якщо його відбиток (геш)",
        "байт-у-байт збігається із записом у сховищі."
    ], size=10, color=INK, lh=1.3))

    f.append(arrow(580, 118, 500, 118, color=FIELD, sw=2.0))
    b_anchor, _, _ = box(540, 95, "Якір довіри", size=10, fill=SOFT_GREEN, stroke=BORDER_GRN, bold=True)
    f.append(b_anchor)

    # Стрілка вниз до Intermediate
    f.append(arrow(270, 180, 270, 220, color=POS, sw=2.0))
    f.append(text(400, 202, "Підписано таємним ключем Root_SK", size=10, color=POS, bold=True))

    # Рівень 2: Intermediate CA
    f.append(rect(40, 220, 460, 125, fill=SOFT_BLUE, stroke=BORDER_BLUE, rx=8))
    f.append(text(270, 243, "2. Проміжний центр (Intermediate CA)", size=13, bold=True, color=NEG))
    f.append(mtext(270, 263, [
        "Subject: DigiCert TLS RSA SHA256 2020 CA1",
        "Issuer: DigiCert Global Root G2",
        "BasicConstraints: CA=TRUE, pathLenConstraint=0"
    ], size=10, color=MUTED, lh=1.25))
    f.append(text(270, 325, "Відкритий ключ: Interm_PK (перевіряється через Root_PK)", size=11, bold=True, color=NEG))

    # Пояснення праворуч для Intermediate
    f.append(rect(580, 220, 460, 125, fill="#ffffff", stroke=LINE, rx=8))
    f.append(text(810, 245, "Навіщо потрібен проміжний рівень:", size=11, bold=True))
    f.append(mtext(810, 268, [
        "Кореневий ключ Root_SK лежить в офлайн-сейфі (Cold Storage).",
        "Щоденну масову видачу сертифікатів ведуть проміжні центри.",
        "У разі компрометації відкликається лише Intermediate CA,",
        "а не глобальний якір довіри всієї операційної системи."
    ], size=10, color=MUTED, lh=1.3))

    # Стрілка вниз до Leaf
    f.append(arrow(270, 345, 270, 385, color=NEG, sw=2.0))
    f.append(text(405, 367, "Підписано таємним ключем Interm_SK", size=10, color=NEG, bold=True))

    # Рівень 3: Leaf Certificate
    f.append(rect(40, 385, 460, 115, fill=SOFT_ORANGE, stroke=BORDER_ORG, rx=8))
    f.append(text(270, 408, "3. Кінцевий сертифікат сервера (Leaf / End-Entity)", size=13, bold=True, color=POS))
    f.append(mtext(270, 428, [
        "Subject: CN=api.service.gov.ua, SAN=api.service.gov.ua",
        "Issuer: DigiCert TLS RSA SHA256 2020 CA1",
        "BasicConstraints: CA=FALSE (кінцевий вузол)"
    ], size=10, color=MUTED, lh=1.25))
    f.append(text(270, 485, "Відкритий ключ: Server_PK (використовується в TLS)", size=11, bold=True, color=FIELD))

    # Пояснення праворуч для Leaf
    f.append(rect(580, 385, 460, 115, fill=SOFT_GREEN, stroke=BORDER_GRN, rx=8))
    f.append(text(810, 410, "Результат верифікації клієнтом:", size=11, bold=True, color=FIELD))
    f.append(mtext(810, 432, [
        "1. Домен у запиті збігається із розширенням SAN сертифіката.",
        "2. Поточний час перебуває у межах [NotBefore, NotAfter].",
        "3. Математичний ланцюг підписів перевірено крок за кроком.",
        "4. Вершину ланцюга знайдено у локальному сховищі довіри."
    ], size=10, color=INK, lh=1.3))

    render(os.path.join(OUT, 'trust-chain-hierarchy.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Механізми відкликання: CRL vs OCSP vs OCSP Stapling
# ─────────────────────────────────────────────────────────────────────────────
def fig_revocation_mechanisms():
    W, H = 1140, 520
    f = []

    f.append(text(W / 2, 28, "Порівняння механізмів відкликання: CRL, OCSP та OCSP Stapling", size=15, bold=True))

    col_w = 335
    x1, x2, x3 = 45, 402, 760

    # Варіант 1: CRL
    f.append(rect(x1, 55, col_w, 445, fill=SOFT_RED, stroke=BORDER_RED, rx=8))
    f.append(text(x1 + col_w / 2, 82, "1. CRL (Списки відкликання)", size=13, bold=True, color=POS))
    f.append(text(x1 + col_w / 2, 102, "RFC 5280: Періодичні чорні списки", size=10, color=MUTED))

    b1, _, _ = box(x1 + col_w / 2, 160, "Клієнт завантажує повний файл\nз номерами всіх відкликаних\nсертифікатів засвідчувального центру", size=11, fill="#ffffff", stroke=BORDER_RED)
    f.append(b1)

    f.append(text(x1 + 15, 222, "Властивості та недоліки:", size=11, bold=True, anchor="start"))
    f.append(mtext(x1 + 15, 242, [
        "• Розмір файлу: від сотень КБ до десятків МБ",
        "• Період оновлення: 24–72 години",
        "• Затримка виявлення: якщо ключ вкрадено",
        "  сьогодні, у CRL він з'явиться лише завтра",
        "• Величезний мережевий трафік на мобільних"
    ], size=10, color=INK, anchor="start", lh=1.35))

    f.append(rect(x1 + 15, 385, col_w - 30, 85, fill="#ffffff", stroke=BORDER_RED, rx=4))
    f.append(text(x1 + col_w / 2, 412, "Оцінка: Застарілий підхід", size=11, bold=True, color=POS))
    f.append(text(x1 + col_w / 2, 440, "Створює трафіковий колапс при масштабуванні", size=10, color=MUTED))

    # Варіант 2: Онлайн OCSP
    f.append(rect(x2, 55, col_w, 445, fill=SOFT_ORANGE, stroke=BORDER_ORG, rx=8))
    f.append(text(x2 + col_w / 2, 82, "2. OCSP (Онлайн-запит)", size=13, bold=True, color=POS))
    f.append(text(x2 + col_w / 2, 102, "RFC 6960: Точковий HTTP-запит", size=10, color=MUTED))

    b2, _, _ = box(x2 + col_w / 2, 160, "Клієнт надсилає запит до OCSP Responder:\n«Чи чинний сертифікат № 4A9F?»\nОтримує підписану відповідь: Good/Revoked", size=11, fill="#ffffff", stroke=BORDER_ORG)
    f.append(b2)

    f.append(text(x2 + 15, 222, "Властивості та недоліки:", size=11, bold=True, anchor="start"))
    f.append(mtext(x2 + 15, 242, [
        "• Компактний обмін даними (кілька сотень байтів)",
        "• Актуальність перевірки в реальному часі",
        "• Затримка з'єднання: +1 додатковий RTT до CA",
        "• Витік приватності: центр бачить IP-адресу",
        "  користувача і всі сайти, які той відкриває!",
        "• Збій резолвера: блокує або засліплює перевірку"
    ], size=10, color=INK, anchor="start", lh=1.35))

    f.append(rect(x2 + 15, 385, col_w - 30, 85, fill="#ffffff", stroke=BORDER_ORG, rx=4))
    f.append(text(x2 + col_w / 2, 412, "Оцінка: Проблема приватності", size=11, bold=True, color=POS))
    f.append(text(x2 + col_w / 2, 440, "Зливає історію вебперегляду сторонньому серверу", size=10, color=MUTED))

    # Варіант 3: OCSP Stapling
    f.append(rect(x3, 55, col_w, 445, fill=SOFT_GREEN, stroke=BORDER_GRN, rx=8))
    f.append(text(x3 + col_w / 2, 82, "3. OCSP Stapling (Пришивання)", size=13, bold=True, color=FIELD))
    f.append(text(x3 + col_w / 2, 102, "RFC 6066 / TLS CertificateStatus", size=10, color=MUTED))

    b3, _, _ = box(x3 + col_w / 2, 160, "Сервер сам періодично опитує OCSP Responder,\nкешує підписаний CA статус і прикріплює його\nбезпосередньо у TLS Handshake клієнту", size=11, fill="#ffffff", stroke=BORDER_GRN)
    f.append(b3)

    f.append(text(x3 + 15, 222, "Властивості та переваги:", size=11, bold=True, anchor="start"))
    f.append(mtext(x3 + 15, 242, [
        "• 0 додаткових мережевих запитів для клієнта",
        "• 0 витоку приватності: CA не бачить користувача",
        "• Підпис CA унеможливлює підробку сервером",
        "• Захист від відкату часу через позначки часу",
        "• Розширення Must-Staple блокує спроби обходу"
    ], size=10, color=INK, anchor="start", lh=1.35))

    f.append(rect(x3 + 15, 385, col_w - 30, 85, fill="#ffffff", stroke=BORDER_GRN, rx=4))
    f.append(text(x3 + col_w / 2, 412, "Оцінка: Сучасний золотий стандарт", size=11, bold=True, color=FIELD))
    f.append(text(x3 + col_w / 2, 440, "Максимальна швидкість, приватність і безпека", size=10, color=MUTED))

    render(os.path.join(OUT, 'revocation-mechanisms.svg'), W, H, *f)


if __name__ == "__main__":
    fig_asymmetric_paradigm()
    fig_digital_signature_flow()
    fig_x509_certificate_structure()
    fig_trust_chain_hierarchy()
    fig_revocation_mechanisms()
    print("Всі фігури згенеровано успішно.")
