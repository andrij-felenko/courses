# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
WARM       = "#b8860b"
CYAN_FILL  = "#e6f7ff"
CYAN       = "#0077b6"


# ── 1. Порівняння криптографічних алгоритмів ключів у SSH ────────────────────
def fig_ssh_crypto_algorithms():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 45, 1100, 58,
                    "Криптографічні алгоритми ключів SSH: математична основа, стійкість і ризики",
                    size=16, fill=FILL, stroke=LINE, bold=True))

    COLS = [
        (50, 340, "Ed25519 (Сучасний канон)", GREEN_FILL, FIELD),
        (430, 340, "ECDSA (NIST P-256 / P-384)", WARM_FILL, WARM),
        (810, 340, "RSA (3072–4096 біт)", BLUE_FILL, NEG),
    ]

    for x, w, col_title, fill, stroke in COLS:
        p.append(fitbox(x, 120, w, 44, col_title, size=14, fill=fill, stroke=stroke, bold=True))

    rows_ed25519 = [
        ("Основа:", "Скручена крива Едвардса (Curve25519) над полем 2^255 - 19"),
        ("Розмір ключа:", "Публічний: 32 байти · Підпис: 64 байти"),
        ("Підпис:", "Детерміністичний: nonce обчислюється як SHA-512(k_priv || msg)"),
        ("Стійкість до атак:", "Арифметика за сталий час (constant-time) — захист від timing"),
        ("Генератор чисел:", "Не залежить від генератора випадкових чисел під час підпису"),
        ("Вердикт:", "Рекомендований вибір за замовчуванням у сучасному OpenSSH"),
    ]

    rows_ecdsa = [
        ("Основа:", "Криві Вейєрштрасса за стандартом NIST (P-256 / secp256r1)"),
        ("Розмір ключа:", "Публічний: 64 байти · Підпис: 64 байти"),
        ("Підпис:", "Недетерміністичний: вимагає унікального випадкового числа k"),
        ("Стійкість до атак:", "Фатальна вразливість: повтор k розкриває закритий ключ"),
        ("Генератор чисел:", "Недовіра до походження коефіцієнтів NIST (Dual_EC_DRBG слід)"),
        ("Вердикт:", "Допустимий лише за вимогами регуляторів (FIPS), ризикований"),
    ]

    rows_rsa = [
        ("Основа:", "Факторизація добутку двох великих простих чисел (n = p * q)"),
        ("Розмір ключа:", "Публічний/підпис: 384–512 байтів (для ключів 3072–4096 біт)"),
        ("Підпис:", "PKCS#1 v1.5 або PSS; ssh-rsa (SHA-1) заблоковано в OpenSSH 8.8+"),
        ("Стійкість до атак:", "Вразливий до timing-атак без blinding; повільна генерація"),
        ("Генератор чисел:", "Потребує багато ентропії для пошуку простих чисел"),
        ("Вердикт:", "Legacy: безпечний лише з розміром >= 3072 біт та rsa-sha2-512"),
    ]

    y = 175
    RH = 70
    for title, desc in rows_ed25519:
        p.append(fitbox(50, y, 340, RH, f"{title}\n{desc}", size=11, fill=GREEN_FILL, stroke=FIELD))
        y += RH + 8

    y = 175
    for title, desc in rows_ecdsa:
        p.append(fitbox(430, y, 340, RH, f"{title}\n{desc}", size=11, fill=WARM_FILL, stroke=WARM))
        y += RH + 8

    y = 175
    for title, desc in rows_rsa:
        p.append(fitbox(810, y, 340, RH, f"{title}\n{desc}", size=11, fill=BLUE_FILL, stroke=NEG))
        y += RH + 8

    p.append(fitbox(50, 650, 1100, 48,
                    "Застарілий алгоритм DSA (1024-біт, SHA-1) повністю видалений з OpenSSH через слабку стійкість та вразливість до витоку k",
                    size=12, fill=RED_FILL, stroke=POS, bold=True))

    render(os.path.join(IMG, 'ssh-crypto-algorithms.svg'), W, H, *p, title="Криптографічні алгоритми ключів у SSH")


# ── 2. Внутрішня структура нового формату ключів OpenSSH ────────────────────
def fig_ssh_key_file_format():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 45, 1100, 56,
                    "Анатомія нового двійкового формату приватного ключа OpenSSH з захистом KDF bcrypt",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # Header / Envelope
    p.append(fitbox(50, 115, 1100, 46,
                    "-----BEGIN OPENSSH PRIVATE KEY----- (Base64 обгортка)  |  Магічний заголовок: 'openssh-key-v1\\0'",
                    size=13, fill=CYAN_FILL, stroke=CYAN, bold=True))

    # Unencrypted header fields
    p.append(fitbox(50, 175, 345, 160,
                    "Відкритий заголовок метаданих:\n\n"
                    "• cipher_name: 'aes256-ctr' / 'none'\n"
                    "• kdf_name: 'bcrypt' / 'none'\n"
                    "• kdf_options: salt (16 байт) + rounds (число)\n"
                    "• num_keys: кількість ключів у файлі (1)",
                    size=12, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(410, 175, 345, 160,
                    "Відкритий публічний ключ:\n\n"
                    "• string: 'ssh-ed25519'\n"
                    "• string: 32 байти публічного ключа\n\n"
                    "(Зручно для ssh-agent без потреби\n"
                    "розшифровувати закрите тіло ключа)",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(770, 175, 380, 160,
                    "Зашифроване тіло приватного ключа:\n\n"
                    "• Шифрується шифром AES-256-CTR або ChaCha20\n"
                    "• Ключ шифрування генерується через KDF:\n"
                    "  key, iv = bcrypt_pbkdf(passphrase, salt, rounds)\n"
                    "• Параметр -a 100 задає 100 раундів KDF",
                    size=12, fill=RED_FILL, stroke=POS))

    # Inner decrypted payload
    p.append(fitbox(50, 350, 1100, 42,
                    "Розшифрований вміст (Payload приватного ключа у пам'яті):",
                    size=13, fill=FILL, stroke=LINE, bold=True))

    inner_cols = [
        (50, 200, "checkint1 & checkint2", "2 x uint32\n\nЯкщо після дешифрування\ncheckint1 == checkint2,\nпарольна фраза вірна", CYAN_FILL, CYAN),
        (270, 210, "key_type", "string\n\n'ssh-ed25519'\n(мусить збігатися з\nвідкритим заголовком)", GREEN_FILL, FIELD),
        (500, 260, "public_key & private_key", "bytes\n\nПублічний ключ (32 байти)\nта закритий ключ\n(32 байти seed + 32 байти pub)", GREEN_FILL, FIELD),
        (780, 200, "comment", "string\n\nКоментар користувача:\nuser@workstation або\nопис призначення ключа", WARM_FILL, WARM),
        (1000, 150, "padding", "1..8 байтів\n\nВирівнювання\nрозміру під блок шифру\n(байти 1, 2, 3...)", FILL, LINE),
    ]

    for x, w, title, desc, fill, stroke in inner_cols:
        p.append(fitbox(x, 405, w, 180, f"{title}\n\n{desc}", size=11, fill=fill, stroke=stroke))

    p.append(fitbox(50, 605, 1100, 75,
                    "Захист від перебору: застарілий формат PEM/OpenSSL використовував швидкі хеші MD5/SHA1 (мільйони спроб/сек на GPU).\n"
                    "Новий KDF bcrypt із параметром -a 100 змушує виконувати мільйони ітерацій Blowfish, роблячи офлайн-брутфорс непідйомним.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'ssh-key-file-format.svg'), W, H, *p, title="Структура двійкового формату приватного ключа OpenSSH")


# ── 3. Авторизація клієнта та обмеження authorized_keys ──────────────────────
def fig_authorized_keys_flow():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 40, 1100, 56,
                    "Механізм автентифікації клієнта за ключем та конвеєр обмежень в authorized_keys",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # Left: Client
    p.append(fitbox(50, 115, 280, 480,
                    "Клієнт SSH (ssh user@host)\n\n"
                    "1. Оголошення відкритого ключа:\n"
                    "SSH_MSG_USERAUTH_REQUEST\n"
                    "(publickey, id_ed25519.pub)\n\n"
                    "2. Сервер надсилає Challenge\n"
                    "(Session ID + підписані дані)\n\n"
                    "3. Клієнт підписує закритим ключем:\n"
                    "sig = Ed25519_Sign(priv_key, challenge)\n\n"
                    "4. Відправка підпису серверу:\n"
                    "SSH_MSG_USERAUTH_REQUEST\n"
                    "(згенерований підпис sig)\n\n"
                    "Клієнт НІКОЛИ не передає\nзакритий ключ мережею!",
                    size=12, fill=CYAN_FILL, stroke=CYAN))

    # Center: Server File & StrictModes Check
    p.append(fitbox(360, 115, 360, 480,
                    "Сервер SSH: Перевірка прав та ключів\n\n"
                    "Крок 1: StrictModes (права у VFS):\n"
                    "• ~/.ssh має права 0700, власник UID\n"
                    "• authorized_keys має 0600, власник UID\n"
                    "• /home/user не має права w для group/other\n"
                    "Якщо права слабкі -> відмова в доступі!\n\n"
                    "Крок 2: Пошук ключа:\n"
                    "Читання рядків ~/.ssh/authorized_keys\n"
                    "Звірка публічного ключа з запитом\n\n"
                    "Крок 3: Криптографічна перевірка:\n"
                    "Ed25519_Verify(pub_key, challenge, sig)\n"
                    "Підпис валідний -> ключ підтверджено",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Right: Restrictions Evaluation
    p.append(fitbox(750, 115, 400, 480,
                    "Сервер: Застосування опцій authorized_keys\n\n"
                    "Перевірка мережевих обмежень:\n"
                    "• from=\"192.168.1.0/24\" -> звірка IP клієнта\n"
                    "  (якщо IP поза діапазоном -> EPERM)\n\n"
                    "Блокування небажаних каналів:\n"
                    "• no-port-forwarding -> заборона TCP тунелів\n"
                    "• no-X11-forwarding -> заборона X11 сесій\n"
                    "• no-agent-forwarding -> заборона прокидання ssh-agent\n"
                    "• no-pty -> заборона виділення псевдотермінала\n\n"
                    "Примусова команда (Forced Command):\n"
                    "• command=\"/usr/local/bin/backup.sh\"\n"
                    "  Оригінальна команда клієнта зберігається\n  у змінній SSH_ORIGINAL_COMMAND",
                    size=12, fill=WARM_FILL, stroke=WARM))

    # Bottom summary
    p.append(fitbox(50, 615, 1100, 65,
                    "Сучасний канон: використання опції 'restrict' вмикає повну ізоляцію за замовчуванням (вимикає pty, порти, агент, X11, user-rc), "
                    "після чого дозволяються лише потрібні дії: restrict,command=\"/opt/app/sync.sh\",from=\"10.0.0.0/8\"",
                    size=12, fill=BLUE_FILL, stroke=NEG, bold=True))

    render(os.path.join(IMG, 'authorized-keys-flow.svg'), W, H, *p, title="Механіка авторизації та обмежувальні опції authorized_keys")


# ── 4. Скінченний автомат перевірки host key за моделлю TOFU ─────────────────
def fig_ssh_tofu_mitm_matrix():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 40, 1100, 56,
                    "Модель довіри до сервера: TOFU (Trust On First Use) та розпізнавання атак MITM",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # State machine steps
    p.append(fitbox(50, 115, 320, 100,
                    "Клієнт підключається до сервера\n\nСервер надсилає свій Host Public Key\nпід час обміну ключами (KEX)",
                    size=13, fill=CYAN_FILL, stroke=CYAN, bold=True))

    p.append(fitbox(440, 115, 320, 100,
                    "Пошук хоста у файлі\n~/.ssh/known_hosts\n(порівняння hostname/IP або хешу)",
                    size=13, fill=FILL, stroke=LINE, bold=True))

    p.append(arrow(370, 165, 440, 165, color=LINE))

    # Three branches
    # Branch 1: Key matches
    p.append(arrow(600, 215, 210, 280, color=FIELD))
    p.append(fitbox(50, 280, 320, 220,
                    "Сценарій 1: Ключ збігається\n(Status: Known & Valid)\n\n"
                    "• Відбиток хоста знайдено в known_hosts\n"
                    "• Публічний ключ повністю ідентичний\n\n"
                    "Результат: З'єднання дозволено автоматично без жодних запитів.\nСеанс безпечно зашифровано.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Branch 2: Host unknown (First contact)
    p.append(arrow(600, 215, 600, 280, color=WARM))
    p.append(fitbox(440, 280, 320, 220,
                    "Сценарій 2: Перше підключення\n(Status: Unknown Host - TOFU)\n\n"
                    "• Запис про хост відсутній\n"
                    "• Інтерактивне попередження:\n"
                    "  'Are you sure you want to continue?'\n"
                    "• Користувач підтверджує (yes)\n\n"
                    "Результат: Відбиток записується у ~/.ssh/known_hosts на майбутнє.",
                    size=12, fill=WARM_FILL, stroke=WARM))

    # Branch 3: Key mismatch (MITM alert)
    p.append(arrow(600, 215, 990, 280, color=POS))
    p.append(fitbox(830, 280, 320, 220,
                    "Сценарій 3: Ключ НЕ збігається!\n(Status: Key Mismatch / MITM)\n\n"
                    "• У known_hosts записано один ключ,\n  а сервер надав інший!\n"
                    "• ТРИВОГА: 'REMOTE HOST IDENTIFICATION HAS CHANGED!'\n\n"
                    "Результат: З'єднання МИТТЄВО БЛОКУЄТЬСЯ для захисту від Man-in-the-Middle.",
                    size=12, fill=RED_FILL, stroke=POS, bold=True))

    # Privacy & Rotation bar
    p.append(fitbox(50, 525, 540, 140,
                    "Конфіденційність клієнта (HashKnownHosts):\n\n"
                    "Опція 'HashKnownHosts yes' замінює відкриті імена серверів на HMAC-SHA1:\n"
                    "|1|base64_salt|base64_hash ssh-ed25519 AAAA...\n"
                    "При викраденні файлу зловмисник не бачить списку відвідуваних серверів.",
                    size=12, fill=CYAN_FILL, stroke=CYAN))

    p.append(fitbox(610, 525, 540, 140,
                    "Ротація ключів сервера (UpdateHostKeys):\n\n"
                    "Опція 'UpdateHostKeys yes' дозволяє серверу надсилати нові хост-ключі\n"
                    "під час вже встановленого та довіреного сеансу. Клієнт автоматично додає їх\n"
                    "у known_hosts, уникаючи ручних помилок інженерів при плановій зміні ключів.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'ssh-tofu-mitm-matrix.svg'), W, H, *p, title="Модель перевірки хоста за принципом TOFU та матриця станів")


# ── 5. Масштабування довіри: SSH Certificate Authority (CA) ─────────────────
def fig_ssh_ca_infrastructure():
    W, H = 1200, 720
    p = []

    p.append(fitbox(50, 40, 1100, 56,
                    "Масштабування довіри: Інфраструктура SSH Certificate Authority (Host CA та User CA)",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # Host CA branch (left)
    p.append(fitbox(50, 115, 530, 250,
                    "Host CA (Довіра клієнтів до сотень серверів)\n\n"
                    "1. Центр сертифікації підписує хост-ключі серверів:\n"
                    "   ssh-keygen -s host_ca -I srv1 -h -n srv1.prod,10.0.1.5 /etc/ssh/ssh_host_ed25519_key.pub\n"
                    "   -> генерує ssh_host_ed25519_key-cert.pub\n\n"
                    "2. Сервер віддає сертифікат клієнтам (HostCertificate)\n\n"
                    "3. Клієнт має лише ОДИН запис у ~/.ssh/known_hosts:\n"
                    "   @cert-authority *.prod.company.com ssh-ed25519 AAAAC3Nza...\n\n"
                    "Результат: Нуль запитів TOFU при додаванні нових 10,000 серверів!",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # User CA branch (right)
    p.append(fitbox(620, 115, 530, 250,
                    "User CA (Довіра серверів до тисяч користувачів)\n\n"
                    "1. Центр сертифікації підписує публічний ключ інженера:\n"
                    "   ssh-keygen -s user_ca -I alice -n ubuntu,deploy -V +8h id_ed25519.pub\n"
                    "   -> генерує id_ed25519-cert.pub з часом життя 8 годин та списком principals\n\n"
                    "2. Сервери мають у /etc/ssh/sshd_config директиву:\n"
                    "   TrustedUserCAKeys /etc/ssh/user_ca.pub\n\n"
                    "Результат: Не потрібно розгортати authorized_keys по серверах!\nДоступ автоматично зникає через 8 годин.",
                    size=12, fill=BLUE_FILL, stroke=NEG))

    # Center Comparison: SSH CA vs X.509
    p.append(fitbox(50, 385, 1100, 170,
                    "Чому SSH сертифікати кардинально відрізняються від TLS / X.509 (HTTPS):\n\n"
                    "• Проста двійкова структура: відсутність складного ASN.1/DER парсингу (джерело вразливостей в OpenSSL)\n"
                    "• Відсутність ланцюжків довіри: підпис виконується безпосередньо кореневим CA без проміжних центрів\n"
                    "• Вбудовані поля авторизації: principals (дозволені логіни), critical options (force-command), extensions\n"
                    "• Коротка валідація (TTL): сертифікати діють від годин до діб, що усуває потребу в онлайн-OCSP",
                    size=12, fill=WARM_FILL, stroke=WARM))

    # Revocation with KRL
    p.append(fitbox(50, 575, 1100, 100,
                    "Механізм відкликання компрометованих ключів (KRL — Key Revocation List):\n\n"
                    "При викраденні приватного ключа до закінчення TTL сертифіката CA генерує список відкликання:\n"
                    "ssh-keygen -k -f /etc/ssh/revoked_keys -u cert_to_revoke.pub\n"
                    "Директива 'RevokedKeys /etc/ssh/revoked_keys' у sshd_config блокує відкликані сертифікати миттєво.",
                    size=12, fill=CYAN_FILL, stroke=CYAN))

    render(os.path.join(IMG, 'ssh-ca-infrastructure.svg'), W, H, *p, title="Архітектура довіри на базі SSH Certificate Authority")


def main():
    fig_ssh_crypto_algorithms()
    fig_ssh_key_file_format()
    fig_authorized_keys_flow()
    fig_ssh_tofu_mitm_matrix()
    fig_ssh_ca_infrastructure()
    print("All figures generated successfully.")

if __name__ == '__main__':
    main()
