# -*- coding: utf-8 -*-
"""Фігури до теми «OpenID Connect: єдиний вхід поверх OAuth 2.0».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER  = "#b08900"
GRAY   = "#9aa0a6"
PURPLE = "#7b1fa2"


# ── 1. Атака підміни токена (Confused Deputy / Pseudo-authentication) ────────
def fig_pseudo_auth_attack():
    W, H = 960, 480
    f = [text(W / 2, 28, "Атака підміни токена при використанні «голого» OAuth 2.0 для автентифікації", size=16, bold=True)]

    # Колонка 1: Зловмисник та його застосунок
    f.append(rect(40, 56, 260, 400, fill="#fdf2f2", stroke=POS, sw=1.6, rx=8))
    f.append(text(170, 84, "1. Зловмисник (Attacker)", size=14, color=POS, bold=True))
    f.append(fitbox(56, 102, 228, 92,
                    "Отримує легітимний\naccess_token для СВОГО\nдодатка «AttackerApp»\nвід спільного IdP",
                    size=12, fill="#ffffff", stroke=POS, sw=1.2))
    f.append(fitbox(56, 210, 228, 100,
                    "Підсовує цей токен\nжертві або вразливому\nклієнту «VictimApp»\nпід час входу",
                    size=12, fill="#ffffff", stroke=POS, sw=1.2))
    f.append(fitbox(56, 326, 228, 114,
                    "Токен валідний і виданий IdP,\nале виданий ДЛЯ ІНШОГО\nдодатка! Голий OAuth\nне має поля audience для клієнта",
                    size=11, fill="#ffffff", stroke=POS, sw=1.2, color=POS))

    # Стрілка передачі токена вразливому клієнту
    f.append(arrow(300, 260, 345, 260, color=POS, sw=2.0))
    f.append(text(322, 250, "Токен", size=11, color=POS, bold=True))

    # Колонка 2: Вразливий клієнт (Victim Client / Relying Party)
    f.append(rect(350, 56, 260, 400, fill="#f4f7fe", stroke=NEG, sw=1.6, rx=8))
    f.append(text(480, 84, "2. Вразливий клієнт", size=14, color=NEG, bold=True))
    f.append(fitbox(366, 102, 228, 86,
                    "Отримує чужий access_token\nі не може перевірити,\nдля кого його виписано",
                    size=12, fill="#ffffff", stroke=NEG, sw=1.2))
    f.append(fitbox(366, 204, 228, 110,
                    "Робить запит /userinfo\nіз цим токеном до IdP:\n«Хто власник токена?»",
                    size=12, fill="#ffffff", stroke=NEG, sw=1.2))
    f.append(fitbox(366, 330, 228, 110,
                    "ПОМИЛКА:\nСтворює сесію для жертви\nна основі чужого токена!\nЗловмисник захоплює акаунт",
                    size=11, fill="#ffffff", stroke=POS, sw=1.4, color=POS))

    # Стрілка запиту до IdP
    f.append(arrow(610, 240, 655, 240, color=LINE, sw=1.8))
    f.append(text(632, 230, "GET /userinfo", size=10, color=INK))
    # Стрілка відповіді від IdP
    f.append(arrow(655, 275, 610, 275, color=FIELD, sw=1.8))
    f.append(text(632, 292, "{sub, email}", size=10, color=FIELD, bold=True))

    # Колонка 3: Сервер авторизації / Ресурс (IdP / UserInfo)
    f.append(rect(660, 56, 260, 400, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(790, 84, "3. Провайдер (IdP)", size=14, color=FIELD, bold=True))
    f.append(fitbox(676, 102, 228, 92,
                    "Сервер авторизації:\nчесно перевіряє токен,\nбачить, що він дійсний\nі не прострочений",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(676, 210, 228, 100,
                    "Кінцева точка /userinfo:\nповертає профіль того,\nхто авторизував токен,\nне знаючи, хто питає",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(676, 326, 228, 114,
                    "ВИСНОВОК:\nAccess token — це дозвіл на доступ,\nа не доказ особи для клієнта!\nOIDC вирішує це через ID Token",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(IMG, "pseudo-auth-attack.svg"), W, H, *f)


# ── 2. Розподіл обов'язків: ID Token vs Access Token ───────────────────────────
def fig_tokens_separation():
    W, H = 960, 430
    f = [text(W / 2, 28, "Два токени — дві різні адреси та різні обов'язки", size=16, bold=True)]

    # Ліва половина: ID Token
    f.append(rect(40, 54, 425, 356, fill="#f4f7fe", stroke=NEG, sw=1.8, rx=8))
    f.append(text(252, 84, "ID Token (Посвідчення особи)", size=15, color=NEG, bold=True))
    f.append(fitbox(56, 100, 393, 48,
                    "ПРИЗНАЧЕННЯ: для Клієнта (Relying Party)",
                    size=12, fill="#ffffff", stroke=NEG, sw=1.3, bold=True, color=NEG))

    f.append(fitbox(56, 156, 393, 106,
                    "Формат: Завжди підписаний JWT (JWS/JWE)\n"
                    "Читач: Тільки клієнтський застосунок\n"
                    "Мета: Довести клієнту факт автентифікації користувача\n"
                    "Ключове поле: aud = client_id клієнта",
                    size=11.5, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(56, 270, 393, 126,
                    "Типовий вміст навантаження (payload):\n"
                    "{\n"
                    "  \"iss\": \"https://accounts.example.com\",\n"
                    "  \"sub\": \"usr-98124\",\n"
                    "  \"aud\": \"my-web-app-client-id\",\n"
                    "  \"exp\": 1735732800, \"nonce\": \"r8x2k1\"\n"
                    "}",
                    size=11, fill="#ffffff", stroke=NEG, sw=1.2, color=INK))

    # Права половина: Access Token
    f.append(rect(495, 54, 425, 356, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(707, 84, "Access Token (Ключ доступу до API)", size=15, color=FIELD, bold=True))
    f.append(fitbox(511, 100, 393, 48,
                    "ПРИЗНАЧЕННЯ: для Сервера ресурсів (Resource Server / API)",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.3, bold=True, color=FIELD))

    f.append(fitbox(511, 156, 393, 106,
                    "Формат: Непрозорий рядок (opaque) або внутрішній JWT\n"
                    "Читач: Сервер ресурсів (API), клієнт НЕ розбирає його\n"
                    "Мета: Надати авторизований доступ до ресурсів (scope)\n"
                    "Ключове поле: aud = https://api.example.com",
                    size=11.5, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(511, 270, 393, 126,
                    "Типовий вміст або використання:\n"
                    "Клієнт додає токен у HTTP-заголовок запиту:\n"
                    "Authorization: Bearer dGVzdC1hY2Nlc3MtdG9rZW4...\n\n"
                    "API перевіряє скоупи (openid, profile, email)\n"
                    "і віддає запитані ресурси користувача",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(IMG, "tokens-separation.svg"), W, H, *f)


# ── 3. Повний цикл Authorization Code Flow з PKCE ─────────────────────────────
def fig_oidc_code_flow_pkce():
    W, H = 960, 520
    f = [text(W / 2, 26, "OpenID Connect: Authorization Code Flow з розширенням PKCE", size=16, bold=True)]

    # Чотири колони-учасники
    cols = [
        (110, "Браузер (User Agent)", "#555555"),
        (350, "Клієнт (Relying Party)", NEG),
        (610, "Сервер авторизації (OP)", FIELD),
        (850, "Сервер ресурсів (UserInfo)", PURPLE),
    ]

    # Вертикальні лінії життя
    for cx, label, col in cols:
        f.append(rect(cx - 95, 48, 190, 34, fill="#ffffff", stroke=col, sw=1.6, rx=6))
        f.append(text(cx, 70, label, size=12, color=col, bold=True))
        f.append(line(cx, 82, cx, 500, color=GRAY, sw=1.2, dash="4,4"))

    # Крок 1: Генерація PKCE та початок входу
    f.append(fitbox(250, 96, 200, 34, "1. Генерує verifier, challenge,\nstate та nonce", size=10, fill="#f4f7fe", stroke=NEG))
    f.append(arrow(350, 140, 110, 140, color=LINE, sw=1.6))
    f.append(text(230, 134, "Redirect: /authorize?code_challenge=...", size=10, color=INK))

    # Крок 2: Перехід до OP
    f.append(arrow(110, 168, 610, 168, color=LINE, sw=1.6))
    f.append(text(360, 162, "2. GET /authorize (scope=openid, challenge, state, nonce)", size=10, color=INK))

    # Крок 3: Автентифікація користувача в OP
    f.append(fitbox(510, 184, 200, 34, "3. Вхід (пароль, MFA)\nта згода (consent)", size=10, fill="#f6fbf7", stroke=FIELD))

    # Крок 4: Повернення з кодом через браузер
    f.append(arrow(610, 230, 110, 230, color=LINE, sw=1.6))
    f.append(text(360, 224, "4. Redirect: /callback?code=AUTH_CODE&state=...", size=10, color=INK))
    f.append(arrow(110, 258, 350, 258, color=LINE, sw=1.6))
    f.append(text(230, 252, "GET /callback?code=...&state=...", size=10, color=INK))

    # Крок 5: Прямий обмін коду на токени (Back-channel)
    f.append(arrow(350, 298, 610, 298, color=NEG, sw=1.9))
    f.append(text(480, 290, "5. POST /token (code + code_verifier + secret)", size=10.5, color=NEG, bold=True))

    # Крок 6: Відповідь із токенами
    f.append(fitbox(510, 314, 200, 34, "6. Перевірка code_verifier\n= SHA256(challenge)", size=10, fill="#f6fbf7", stroke=FIELD))
    f.append(arrow(610, 360, 350, 360, color=FIELD, sw=1.9))
    f.append(text(480, 352, "Відповідь: { id_token, access_token }", size=10.5, color=FIELD, bold=True))

    # Крок 7: Валідація ID-токена та запит профілю
    f.append(fitbox(250, 376, 200, 36, "7. Валідація ID-токена:\nпідпис, iss, aud, nonce, exp", size=10, fill="#f4f7fe", stroke=NEG))
    f.append(arrow(350, 426, 850, 426, color=PURPLE, sw=1.6))
    f.append(text(600, 420, "8. GET /userinfo (Authorization: Bearer access_token)", size=10, color=PURPLE))

    f.append(arrow(850, 460, 350, 460, color=PURPLE, sw=1.6))
    f.append(text(600, 454, "Профіль: { sub, name, email, email_verified }", size=10, color=PURPLE))

    # Крок 9: Створення локальної сесії
    f.append(arrow(350, 488, 110, 488, color=FIELD, sw=1.8))
    f.append(text(230, 482, "9. Set-Cookie: session_id=...", size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "oidc-code-flow-pkce.svg"), W, H, *f)


# ── 4. Конвеєр валідації ID-токена ───────────────────────────────────────────
def fig_id_token_validation_pipeline():
    W, H = 960, 460
    f = [text(W / 2, 28, "Конвеєр криптографічної та логічної перевірки ID-токена клієнтом", size=16, bold=True)]

    steps = [
        (40,  54,  260, 106, "1. Перевірка алгоритму", "Заголовок JWT: alg ∈ [RS256, ES256]\nЗаборона alg=\"none\" та HS256\nОтримання kid (Key ID)", FIELD),
        (350, 54,  260, 106, "2. Отримання публ. ключа", "Пошук kid у кеші JWKS\nЯкщо kid новий — оновлення JWKS\nВитягнення відкритого ключа RSA/EC", FIELD),
        (660, 54,  260, 106, "3. Перевірка підпису", "Криптографічна звірка:\nVerify(header.payload, sig, pubKey)\nЗахист від модифікації даних", FIELD),

        (40,  200, 260, 106, "4. Перевірка видавця (iss)", "Поле iss у токені ПОВИННО\nточно збігатися з Issuer URL\nз .well-known/openid-configuration", NEG),
        (350, 200, 260, 106, "5. Перевірка аудиторії (aud)", "Поле aud ПОВИННО містити\nclient_id цього клієнта\nЗахист від підміни токена іншим RP", NEG),
        (660, 200, 260, 106, "6. Час дії (exp, iat, nbf)", "exp > поточний час (не протух)\niat <= поточний час (з урахуванням\nдопуску годинника 1-2 хвилини)", NEG),

        (40,  344, 260, 96,  "7. Перевірка Nonce", "nonce у токені == nonce, що був\nзбережений у сесії клієнта\nЗахист від повтору запиту (replay)", POS),
        (350, 344, 260, 96,  "8. Перевірка хешу (at_hash)", "Якщо є access_token:\nat_hash == B64URL(LEFT_HALF(\nSHA256(access_token)))", POS),
        (660, 344, 260, 96,  "9. Успіх: створення сесії", "Користувач автентифікований!\nВитягнення sub та профілю,\nвидача локального session cookie", POS),
    ]

    for x, y, w, h, title_s, body_s, col in steps:
        f.append(rect(x, y, w, h, fill="#ffffff", stroke=col, sw=1.6, rx=8))
        f.append(rect(x, y, w, 28, fill=col, stroke=col, sw=1.6, rx=6))
        f.append(text(x + w / 2, y + 19, title_s, size=11.5, color="#ffffff", bold=True))
        f.append(fitbox(x + 6, y + 32, w - 12, h - 38, body_s, size=11, fill="#ffffff", stroke="#ffffff", color=INK))

    # Стрілки між етапами
    f.append(arrow(300, 107, 348, 107, color=LINE, sw=1.6))
    f.append(arrow(610, 107, 658, 107, color=LINE, sw=1.6))

    f.append(arrow(790, 160, 790, 180, color=LINE, sw=1.6))
    f.append(line(790, 180, 170, 180, color=LINE, sw=1.6))
    f.append(arrow(170, 180, 170, 198, color=LINE, sw=1.6))

    f.append(arrow(300, 253, 348, 253, color=LINE, sw=1.6))
    f.append(arrow(610, 253, 658, 253, color=LINE, sw=1.6))

    f.append(arrow(790, 306, 790, 326, color=LINE, sw=1.6))
    f.append(line(790, 326, 170, 326, color=LINE, sw=1.6))
    f.append(arrow(170, 326, 170, 342, color=LINE, sw=1.6))

    f.append(arrow(300, 392, 348, 392, color=LINE, sw=1.6))
    f.append(arrow(610, 392, 658, 392, color=LINE, sw=1.6))

    render(os.path.join(IMG, "id-token-validation-pipeline.svg"), W, H, *f)


# ── 5. Динамічне виявлення (Discovery) та ротація ключів через JWKS ──────────
def fig_discovery_jwks_rotation():
    W, H = 960, 440
    f = [text(W / 2, 28, "Динамічне виявлення конфігурації та безпечна ротація ключів через JWKS", size=16, bold=True)]

    # Ліва сторона: Клієнт (RP) і кеш
    f.append(rect(40, 56, 410, 360, fill="#f4f7fe", stroke=NEG, sw=1.6, rx=8))
    f.append(text(245, 84, "Клієнт (Relying Party)", size=14, color=NEG, bold=True))

    f.append(fitbox(56, 102, 378, 68,
                    "1. Завантажує метадані при старті:\nGET https://idp.com/.well-known/openid-configuration\nДізнається jwks_uri, token_endpoint тощо",
                    size=11.5, fill="#ffffff", stroke=NEG, sw=1.2))

    f.append(fitbox(56, 184, 378, 96,
                    "2. Кеш відкритих ключів (JWKS Cache):\n"
                    "  key-2026-01  →  RSA Public Key A (активний)\n"
                    "  key-2025-12  →  RSA Public Key B (старий)\n"
                    "TTL кешу: 24 години (з повагою до Cache-Control)",
                    size=11, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(56, 294, 378, 108,
                    "3. Обробка ротації при отриманні токена:\n"
                    "• Приходить ID-токен із новим kid=\"key-2026-02\"\n"
                    "• Якщо kid немає в кеші → одиночний запит до jwks_uri\n"
                    "• Оновлення кешу → успішна валідація підпису",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4, color=INK))

    # Права сторона: OpenID Provider і сховище ключів
    f.append(rect(510, 56, 410, 360, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(715, 84, "OpenID Provider (IdP)", size=14, color=FIELD, bold=True))

    f.append(fitbox(526, 102, 378, 86,
                    "Ендпоінт JWKS:\nGET https://idp.com/.well-known/jwks.json\nПовертає набір публічних ключів (keys array)\nіз параметрами kty, alg, use, kid, n, e",
                    size=11.5, fill="#ffffff", stroke=FIELD, sw=1.2))

    f.append(fitbox(526, 202, 378, 96,
                    "Процес ротації ключів на стороні IdP:\n"
                    "1. Генерація нового ключа (kid: key-2026-02)\n"
                    "2. Публікація нового ключа в JWKS заздалегідь\n"
                    "3. Початок підписання нових токенів новим ключем",
                    size=11, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(526, 312, 378, 90,
                    "Граціозне виведення старого ключа:\n"
                    "Старий ключ (key-2026-01) лишається в JWKS ще деякий час,\n"
                    "доки не спливе термін дії всіх раніше виданих токенів",
                    size=11, fill="#ffffff", stroke=AMBER, sw=1.3, color=INK))

    # Стрілки між клієнтом і провайдером
    f.append(arrow(450, 136, 508, 136, color=LINE, sw=1.8))
    f.append(arrow(508, 357, 450, 357, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "discovery-jwks-rotation.svg"), W, H, *f)


# ── 6. Публічний та попарний (Pairwise) ідентифікатори суб'єкта ────────────────
def fig_pairwise_vs_public_sub():
    W, H = 960, 420
    f = [text(W / 2, 28, "Публічний (Public) vs Попарний (Pairwise) ідентифікатор суб'єкта sub", size=16, bold=True)]

    # Ліва частина: Public Sub (загроза приватності)
    f.append(rect(40, 54, 425, 346, fill="#fdf2f2", stroke=POS, sw=1.6, rx=8))
    f.append(text(252, 82, "Публічний суб'єкт (Public Subject)", size=14, color=POS, bold=True))
    f.append(fitbox(56, 100, 393, 46,
                    "sub однаковий для всіх застосунків у світі",
                    size=12, fill="#ffffff", stroke=POS, sw=1.2, color=POS, bold=True))

    f.append(fitbox(56, 158, 393, 110,
                    "Користувач Alice (ID: 48201) логіниться:\n"
                    "• Сайт A (Магазин):      sub = \"usr-48201\"\n"
                    "• Сайт B (Форум):        sub = \"usr-48201\"\n"
                    "• Сайт C (Медпортал): sub = \"usr-48201\"",
                    size=11.5, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(56, 280, 393, 106,
                    "НАСЛІДОК ДЛЯ ПРИВАТНОСТІ:\n"
                    "Сайти A, B і C можуть об'єднати бази даних\n"
                    "й повністю відстежити активність та профіль Аліси\n"
                    "в усьому інтернеті без її згоди",
                    size=11, fill="#ffffff", stroke=POS, sw=1.3, color=POS))

    # Права частина: Pairwise Sub (захист приватності)
    f.append(rect(495, 54, 425, 346, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(707, 82, "Попарний суб'єкт (Pairwise Subject)", size=14, color=FIELD, bold=True))
    f.append(fitbox(511, 100, 393, 46,
                    "sub унікальний для кожного домену/клієнта",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD, bold=True))

    f.append(fitbox(511, 158, 393, 110,
                    "Формула: sub = HMAC_SHA256(user_id + sector_id, secret)\n"
                    "• Сайт A (shop.com):     sub = \"a9f4c81...\"\n"
                    "• Сайт B (forum.org):    sub = \"b2e710d...\"\n"
                    "• Сайт C (health.net):   sub = \"c503fa9...\"",
                    size=11.5, fill="#ffffff", stroke=GRAY, sw=1.0))

    f.append(fitbox(511, 280, 393, 106,
                    "ПЕРЕВАГА ДЛЯ ПРИВАТНОСТІ:\n"
                    "Сайти A, B і C бачать геть різні ідентифікатори.\n"
                    "Неможливо скорелювати дії користувача між різними\n"
                    "сервісами, доки користувач сам не розкриє зв'язок",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3, color=FIELD))

    render(os.path.join(IMG, "pairwise-vs-public-sub.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pseudo_auth_attack()
    fig_tokens_separation()
    fig_oidc_code_flow_pkce()
    fig_id_token_validation_pipeline()
    fig_discovery_jwks_rotation()
    fig_pairwise_vs_public_sub()
    print("All 6 figures generated successfully in ./img/")

