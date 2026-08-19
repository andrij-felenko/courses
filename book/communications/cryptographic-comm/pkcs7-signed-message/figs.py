# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
C_DATA   = "#4b5563"     # Дані / корисне навантаження
C_DATAF  = "#f3f4f6"
C_SIG    = "#2457d6"     # Підпис / криптографія / SignerInfo
C_SIGF   = "#eaf0fd"
C_CERT   = "#27ae60"     # Сертифікати / Довіра / Валідація
C_CERTF  = "#eafaf0"
C_ATTR   = "#d97706"     # Атрибути / Метадані
C_ATTRF  = "#fef3c7"
C_WARN   = "#c0392b"     # Помилки / Небезпека / Відкликання
C_WARNF  = "#fdecea"


# ── 1. cms-content-hierarchy: Ієрархія типів контенту CMS/PKCS#7 ────────────
def fig_cms_content_hierarchy():
    W, H = 1080, 500
    p = []

    p.append(text(W / 2, 30, "Ієрархія типів вмісту ASN.1 ContentInfo (RFC 5652 / RFC 2315)", size=16, color=INK, bold=True))

    # Головний контейнер ContentInfo
    p.append(rect(40, 60, 1000, 70, fill="#ffffff", stroke=INK, sw=2, rx=8))
    p.append(text(540, 85, "ContentInfo (Універсальна оболонка)", size=15, color=INK, bold=True))
    p.append(text(540, 110, "contentType OBJECT IDENTIFIER (OID)  ||  content [0] EXPLICIT ANY DEFINED BY contentType", size=12, color=MUTED))

    # Стрілки розгалуження
    oids = [
        (120, "Data\n(id-data)", "1.2.840.113549.1.7.1", "Неструктуровані\nсирі байти\n(OCTET STRING)", C_DATAF, C_DATA),
        (290, "SignedData\n(id-signedData)", "1.2.840.113549.1.7.2", "Цифровий підпис,\nсертифікати,\nатрибути, CRL", C_SIGF, C_SIG),
        (460, "EnvelopedData\n(id-envelopedData)", "1.2.840.113549.1.7.3", "Зашифрований\nвміст + ключі\nодержувачів", C_ATTRF, C_ATTR),
        (630, "DigestedData\n(id-digestedData)", "1.2.840.113549.1.7.5", "Цілісність через\nкриптографічний\nгеш (без підпису)", C_DATAF, C_DATA),
        (800, "EncryptedData\n(id-encryptedData)", "1.2.840.113549.1.7.6", "Симетрично\nзашифровані дані\n(без ключів)", C_WARNF, C_WARN),
        (960, "AuthData\n(id-ct-authData)", "1.2.840.113549.1.9.16.1.2", "Автентифіковані\nдані через MAC\n(автентичність)", C_CERTF, C_CERT),
    ]

    for cx, title, oid_str, desc, fill_c, strk_c in oids:
        p.append(arrow(540, 130, cx, 175, color=LINE, sw=1.5))
        p.append(rect(cx - 75, 180, 150, 190, fill=fill_c, stroke=strk_c, sw=1.6, rx=6))
        p.append(fitbox(cx - 70, 190, 140, 44, title, size=12, fill=fill_c, stroke=strk_c, sw=0, bold=True))
        p.append(text(cx, 252, oid_str, size=9, color=MUTED))
        p.append(line(cx - 65, 264, cx + 65, 264, color=strk_c, sw=1, dash="3,3"))
        p.append(fitbox(cx - 70, 275, 140, 85, desc, size=11, fill=fill_c, stroke=strk_c, sw=0))

    # Нижня рекурсивна плашка
    p.append(fitbox(40, 400, 1000, 75, "Рекурсивна інкапсуляція: SignedData може містити всередині EnvelopedData (підписаний шифротекст),\nа EnvelopedData — SignedData (зашифрований підписаний документ у S/MIME).\nКожен рівень зберігає повну самоописовість завдяки власному заголовку ContentInfo.", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.5))

    render(os.path.join(OUT, "cms-content-hierarchy.svg"), W, H, *p)


# ── 2. signed-data-anatomy: Детальна анатомія структури SignedData ───────────
def fig_signed_data_anatomy():
    W, H = 1100, 620
    p = []

    p.append(text(W / 2, 28, "Анатомія структури SignedData (ASN.1 SEQUENCE у RFC 5652)", size=16, color=INK, bold=True))

    # Головна рамка SignedData
    p.append(rect(40, 50, 1020, 545, fill="#ffffff", stroke=C_SIG, sw=2, rx=8))
    p.append(text(550, 74, "SignedData ::= SEQUENCE", size=14, color=C_SIG, bold=True))

    # Поле 1: version
    p.append(fitbox(60, 95, 280, 50, "version CMSVersion\n(v1 = 1, v3 = 3 для CMS/RFC 5652)", size=12, fill=C_DATAF, stroke=C_DATA, sw=1.4))

    # Поле 2: digestAlgorithms
    p.append(fitbox(360, 95, 340, 50, "digestAlgorithms SET OF\nAlgorithmIdentifier (SHA-256, SHA-384)", size=12, fill=C_SIGF, stroke=C_SIG, sw=1.4))

    # Поле 3: encapContentInfo
    p.append(fitbox(720, 95, 320, 50, "encapContentInfo\nEncapsulatedContentInfo", size=12, fill=C_DATAF, stroke=C_DATA, sw=1.4))

    # Внутрішнє розгортання encapContentInfo
    p.append(rect(720, 155, 320, 95, fill=C_DATAF, stroke=C_DATA, sw=1.2, rx=6))
    p.append(text(880, 175, "eContentType (напр. id-data)", size=11, color=INK, bold=True))
    p.append(fitbox(730, 190, 300, 50, "eContent [0] EXPLICIT OCTET STRING\n(Вбудований payload або NULL у detached)", size=11, fill="#ffffff", stroke=C_DATA, sw=1))

    # Поле 4: certificates
    p.append(rect(60, 160, 310, 140, fill=C_CERTF, stroke=C_CERT, sw=1.4, rx=6))
    p.append(text(215, 182, "certificates [0] IMPLICIT CertificateSet", size=12, color=C_CERT, bold=True))
    p.append(fitbox(75, 195, 280, 42, "Кінцевий сертифікат підписувача\n(X.509 v3: відкритий ключ + суб'єкт)", size=11, fill="#ffffff", stroke=C_CERT, sw=1))
    p.append(fitbox(75, 245, 280, 42, "Проміжні сертифікати CA\n(Ланцюг довіри до Root CA)", size=11, fill="#ffffff", stroke=C_CERT, sw=1))

    # Поле 5: crls
    p.append(rect(390, 160, 310, 140, fill=C_WARNF, stroke=C_WARN, sw=1.4, rx=6))
    p.append(text(545, 182, "crls [1] IMPLICIT RevocationInfoChoices", size=12, color=C_WARN, bold=True))
    p.append(fitbox(405, 195, 280, 42, "Списки відкликаних сертифікатів (CRL)\nСерійні номери скомпрометованих ключів", size=11, fill="#ffffff", stroke=C_WARN, sw=1))
    p.append(fitbox(405, 245, 280, 42, "Відповіді OCSP (RFC 5652 / RFC 5940)\nАктуальний онлайн-статус валідності", size=11, fill="#ffffff", stroke=C_WARN, sw=1))

    # Поле 6: signerInfos (SignerInfo розгорнуто)
    p.append(rect(60, 320, 980, 255, fill=C_SIGF, stroke=C_SIG, sw=1.8, rx=6))
    p.append(text(550, 342, "signerInfos ::= SET OF SignerInfo (Контейнер підпису кожного автора)", size=13, color=C_SIG, bold=True))

    # Поля всередині SignerInfo
    p.append(fitbox(80, 360, 210, 85, "1. sid SignerIdentifier:\n• IssuerAndSerialNumber\n  (Видавець + серійний №)\n• SubjectKeyIdentifier (SKI)\n  (Геш відкритого ключа)", size=11, fill="#ffffff", stroke=C_SIG, sw=1.2))
    p.append(fitbox(305, 360, 170, 85, "2. digestAlgorithm:\nАлгоритм гешу\n(наприклад SHA-256)", size=11, fill="#ffffff", stroke=C_SIG, sw=1.2))
    p.append(fitbox(490, 360, 270, 85, "3. signedAttrs [0] IMPLICIT:\nSET OF Attribute (DER-кодовані!)\n• contentType (id-data)\n• messageDigest (SHA256(payload))\n• signingTime (UTC/Generalized)", size=11, fill=C_ATTRF, stroke=C_ATTR, sw=1.5))
    p.append(fitbox(775, 360, 245, 85, "4. signatureAlgorithm:\nАлгоритм шифрування підпису\n(rsaEncryption / ecdsa-sha256)", size=11, fill="#ffffff", stroke=C_SIG, sw=1.2))

    # Нижній ряд SignerInfo
    p.append(fitbox(80, 465, 430, 90, "5. signature SignatureValue (OCTET STRING):\nКриптографічний підпис над DER-байтами signedAttrs:\nσ = RSA_Sign_sk(DER(signedAttrs)) або ECDSA_Sign_sk(...)", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.6))
    p.append(fitbox(530, 465, 490, 90, "6. unsignedAttrs [1] IMPLICIT (Непідписані атрибути):\n• countersignature (Завірення нотаріусом / додатковий підпис)\n• id-aa-timeStampToken (Штамп точного часу за RFC 3161 TSA)", size=12, fill=C_ATTRF, stroke=C_ATTR, sw=1.5))

    render(os.path.join(OUT, "signed-data-anatomy.svg"), W, H, *p)


# ── 3. signature-verification-flow: Двоетапна верифікація підпису ────────────
def fig_signature_verification_flow():
    W, H = 1100, 560
    p = []

    p.append(text(W / 2, 28, "Двоетапний конвеєр перевірки підпису CMS/PKCS#7 з атрибутами", size=16, color=INK, bold=True))

    # Етап 1: Дайджест корисного навантаження
    p.append(rect(40, 60, 480, 210, fill="#ffffff", stroke=C_DATA, sw=1.6, rx=8))
    p.append(text(280, 85, "ЕТАП 1: Гешування вихідного тіла (Payload)", size=13, color=C_DATA, bold=True))
    p.append(fitbox(60, 105, 180, 65, "Payload Data\n(eContent або\nзовнішній файл)", size=12, fill=C_DATAF, stroke=C_DATA, sw=1.4))
    p.append(arrow(245, 137, 295, 137, color=C_DATA, sw=1.6))
    p.append(fitbox(300, 105, 90, 65, "SHA-256\n(Digest)", size=12, fill=C_SIGF, stroke=C_SIG, sw=1.4))
    p.append(arrow(395, 137, 445, 137, color=C_SIG, sw=1.6))
    p.append(fitbox(450, 105, 50, 65, "H₁", size=14, fill=C_ATTRF, stroke=C_ATTR, sw=1.8, bold=True))
    p.append(fitbox(60, 190, 440, 65, "Обчислюється дайджест H₁ = SHA256(Payload).\nЯкщо підпис відокремлений (detached), файл читається з диска або Flash.", size=11, fill=C_DATAF, stroke=C_DATA, sw=0))

    # Етап 2: Перевірка підписаних атрибутів
    p.append(rect(560, 60, 500, 210, fill="#ffffff", stroke=C_ATTR, sw=1.6, rx=8))
    p.append(text(810, 85, "ЕТАП 2: Звірка атрибута MessageDigest", size=13, color=C_ATTR, bold=True))
    p.append(fitbox(580, 105, 230, 75, "SignedAttributes (SET OF)\n• contentType: id-data\n• messageDigest: H_attr\n• signingTime: 2026-08-19", size=11, fill=C_ATTRF, stroke=C_ATTR, sw=1.5))
    p.append(fitbox(870, 105, 170, 75, "Порівняння дайджестів:\nЧи рівні H₁ == H_attr ?", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.6, bold=True))
    p.append(arrow(815, 142, 865, 142, color=C_CERT, sw=1.8))
    p.append(fitbox(580, 195, 460, 60, "Критична перевірка: якщо H₁ ≠ H_attr, тіло повідомлення було модифіковане,\nі процес верифікації негайно зупиняється з помилкою відхилення.", size=11, fill=C_WARNF, stroke=C_WARN, sw=1))

    # Етап 3: Криптографічна перевірка асиметричного підпису
    p.append(rect(40, 290, 1020, 240, fill=C_SIGF, stroke=C_SIG, sw=2, rx=8))
    p.append(text(550, 315, "ЕТАП 3: Верифікація асиметричного цифрового підпису над SignedAttributes", size=14, color=C_SIG, bold=True))

    p.append(fitbox(60, 340, 240, 80, "SignedAttributes\n(Канонічне DER-кодування\nз тегом 0x31 SET OF)", size=12, fill=C_ATTRF, stroke=C_ATTR, sw=1.5))
    p.append(arrow(305, 380, 355, 380, color=C_SIG, sw=1.8))

    p.append(fitbox(360, 340, 140, 80, "SHA-256\nH₂ = Hash(DER)", size=12, fill="#ffffff", stroke=C_SIG, sw=1.5))
    p.append(arrow(505, 380, 555, 380, color=C_SIG, sw=1.8))

    p.append(fitbox(560, 335, 230, 90, "Асиметрична верифікація:\nVerify(pk, H₂, SignatureValue)\n(RSA Decrypt / ECDSA Verify)", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.8, bold=True))

    p.append(fitbox(820, 335, 220, 90, "Сертифікат підписувача\nВідкритий ключ pk\nвитягується за sid\nз поля certificates", size=11, fill="#ffffff", stroke=C_CERT, sw=1.4))
    p.append(arrow(930, 430, 750, 415, color=C_CERT, sw=1.6))

    # Нижній висновок валідації
    p.append(fitbox(60, 445, 980, 70, "Чому саме двоетапно? Підпис накладається на атрибути, що зв'язує час підпису (SigningTime),\nідентичність контенту (MessageDigest) та тип даних (ContentType) в єдиний неподільний криптографічний доказ.\nКанонічне DER-сортування октетів у SET OF гарантує однаковий геш H₂ на будь-якій платформі.", size=12, fill="#ffffff", stroke=C_SIG, sw=1.4))

    render(os.path.join(OUT, "signature-verification-flow.svg"), W, H, *p)


# ── 4. attached-vs-detached: Вбудований проти відокремленого підпису ─────────
def fig_attached_vs_detached():
    W, H = 1080, 520
    p = []

    p.append(text(W / 2, 28, "Вбудований (Attached / Encapsulated) проти Відокремленого (Detached) підпису", size=16, color=INK, bold=True))

    # Ліва колонка: Attached
    p.append(rect(50, 60, 460, 390, fill="#ffffff", stroke=C_SIG, sw=1.8, rx=8))
    p.append(text(280, 88, "Вбудований підпис (Attached / Encapsulated)", size=14, color=C_SIG, bold=True))
    p.append(text(280, 108, "Файли .p7m, поштові вкладення S/MIME, PKCS#12", size=11, color=MUTED, italic=True))

    p.append(rect(80, 130, 400, 200, fill=C_SIGF, stroke=C_SIG, sw=1.4, rx=6))
    p.append(text(280, 152, "Єдиний файл повідомлення (ContentInfo)", size=12, color=C_SIG, bold=True))
    p.append(fitbox(100, 165, 360, 50, "eContent (ВБУДОВАНИЙ ПОВНІСТЮ)\nКорисне навантаження всередині OCTET STRING", size=11, fill=C_DATAF, stroke=C_DATA, sw=1.4))
    p.append(fitbox(100, 225, 360, 45, "Сертифікати X.509 + CRL + SignerInfo + Підпис", size=11, fill=C_CERTF, stroke=C_CERT, sw=1.4))
    p.append(fitbox(100, 275, 360, 45, "Підписані та непідписані атрибути", size=11, fill=C_ATTRF, stroke=C_ATTR, sw=1.4))

    p.append(fitbox(80, 345, 400, 90, "Властивості:\n• Все в одному контейнері — неможливо загубити підпис\n• Вимагає вилучення даних з ASN.1 перед обробкою\n• Не підходить для гігабайтних бінарників та прошивок", size=11, fill=C_DATAF, stroke=C_DATA, sw=1))

    # Права колонка: Detached
    p.append(rect(570, 60, 460, 390, fill="#ffffff", stroke=C_CERT, sw=1.8, rx=8))
    p.append(text(800, 88, "Відокремлений підпис (Detached Signature)", size=14, color=C_CERT, bold=True))
    p.append(text(800, 108, "Файли .p7s / .sig, UEFI Secure Boot, OTA-прошивки MCU", size=11, color=MUTED, italic=True))

    p.append(rect(600, 130, 180, 200, fill=C_DATAF, stroke=C_DATA, sw=1.4, rx=6))
    p.append(text(690, 155, "Оригінальний файл", size=12, color=C_DATA, bold=True))
    p.append(fitbox(615, 175, 150, 140, "firmware.bin\nабо vmlinuz\n\n(Незмінний,\nвиконується\nпрямо з Flash\nбез розбору)", size=11, fill="#ffffff", stroke=C_DATA, sw=1))

    p.append(rect(810, 130, 190, 200, fill=C_CERTF, stroke=C_CERT, sw=1.4, rx=6))
    p.append(text(905, 155, "Файл підпису .p7s", size=12, color=C_CERT, bold=True))
    p.append(fitbox(825, 175, 160, 45, "eContent = NULL\n(Тіло відсутнє)", size=11, fill=C_WARNF, stroke=C_WARN, sw=1.2, bold=True))
    p.append(fitbox(825, 225, 160, 45, "Certificates + CRL", size=11, fill="#ffffff", stroke=C_CERT, sw=1))
    p.append(fitbox(825, 275, 160, 45, "SignerInfo + Підпис", size=11, fill="#ffffff", stroke=C_SIG, sw=1))

    p.append(arrow(690, 335, 905, 335, color=C_SIG, sw=1.6))

    p.append(fitbox(600, 345, 400, 90, "Властивості:\n• Оригінальний бінарник залишається чистим і готовим до виконання\n• Нульові накладні витрати пам'яті на копіювання payload\n• Ідеально для мікроконтролерів із десятками кілобайтів RAM", size=11, fill=C_CERTF, stroke=C_CERT, sw=1))

    # Нижня плашка
    p.append(fitbox(50, 465, 980, 45, "Інженерний вибір: S/MIME та PKCS#12 обирають Attached для зручності транспортування; системне програмування (OTA, Linux kernel modules, Secure Boot) завжди обирає Detached для швидкості та збереження пам'яті.", size=12, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "attached-vs-detached.svg"), W, H, *p)


# ── 5. streaming-pipeline: Потоковий конвеєр верифікації на MCU / серверах ──
def fig_streaming_pipeline():
    W, H = 1080, 540
    p = []

    p.append(text(W / 2, 28, "Потокова однопрохідна верифікація (Streaming Single-Pass Pipeline)", size=16, color=INK, bold=True))

    # Вхідний потік
    p.append(fitbox(40, 70, 200, 70, "Вхідний потік даних\n(HTTP OTA / UART / мережа)\nЧастинами по 4–64 КБ", size=12, fill=C_DATAF, stroke=C_DATA, sw=1.6))
    p.append(arrow(245, 105, 315, 105, color=C_DATA, sw=2))

    # Розгалужувач потоку
    p.append(circle(335, 105, 18, fill=C_SIGF, stroke=C_SIG, sw=2))
    p.append(text(335, 110, "T", size=14, color=C_SIG, bold=True))

    # Гілка 1: Запис у Flash
    p.append(arrow(355, 95, 455, 75, color=C_DATA, sw=1.8))
    p.append(fitbox(460, 50, 240, 55, "Прямий запис у Flash пам'ять\n(Сектори OTA Bank B)", size=12, fill=C_DATAF, stroke=C_DATA, sw=1.4))

    # Гілка 2: Потоковий обчислювач SHA-256
    p.append(arrow(355, 115, 455, 135, color=C_SIG, sw=1.8))
    p.append(fitbox(460, 115, 240, 55, "Потоковий SHA-256 (SHA_Update)\nПотребує лише 108 байтів стану в RAM!", size=12, fill=C_SIGF, stroke=C_SIG, sw=1.6, bold=True))

    # З'єднання наприкінці потоку
    p.append(arrow(705, 142, 785, 142, color=C_SIG, sw=1.8))
    p.append(fitbox(790, 115, 240, 55, "Фінальний дайджест\nSHA_Final() → H_calc", size=12, fill=C_ATTRF, stroke=C_ATTR, sw=1.6))

    # Нижній блок перевірки заголовка CMS
    p.append(rect(40, 200, 990, 220, fill="#ffffff", stroke=C_CERT, sw=1.8, rx=8))
    p.append(text(535, 225, "Перевірка CMS Detached Signature на завершенні потоку (Stream EOF)", size=14, color=C_CERT, bold=True))

    p.append(fitbox(60, 245, 240, 65, "Підпис .p7s\n(Отриманий у заголовку\nабо окремим пакетом)", size=12, fill=C_SIGF, stroke=C_SIG, sw=1.4))
    p.append(arrow(305, 277, 365, 277, color=C_SIG, sw=1.6))

    p.append(fitbox(370, 245, 300, 65, "1. Звірка дайджестів:\nH_calc == SignerInfo.messageDigest\n2. Верифікація підпису відкритим ключем", size=12, fill=C_ATTRF, stroke=C_ATTR, sw=1.6))
    p.append(arrow(675, 277, 735, 277, color=C_CERT, sw=1.8))

    p.append(fitbox(740, 245, 270, 65, "Перевірка сертифіката\nпроти апаратного Root of Trust\n(Зашитий у OTP / ROM / TPM)", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.8, bold=True))

    # Перемикання прапорця завантаження
    p.append(fitbox(60, 335, 950, 70, "Результат: якщо всі перевірки успішні → бутлоадер встановлює прапорець BOOT_VALID у Flash metadata.\nЯкщо хоча б один біт пошкоджено або підпис недійсний → сектори OTA Bank B стираються,\nі система безпечно перезавантажується у попередню стабільну версію Bank A.", size=12, fill=C_CERTF, stroke=C_CERT, sw=1.5))

    # Нижня рамка пам'яті
    p.append(fitbox(40, 440, 990, 75, "Пам'ять: Повний розмір прошивки = 64 МБ, але оперативна пам'ять MCU (SRAM), задіяна для повної перевірки CMS,\nстановить менше 4 КБ (буфер читання ASN.1 + стан SHA-256 + відкритий ключ).", size=12, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "streaming-pipeline.svg"), W, H, *p)


fig_cms_content_hierarchy()
fig_signed_data_anatomy()
fig_signature_verification_flow()
fig_attached_vs_detached()
fig_streaming_pipeline()
print("All 5 figures generated successfully.")
