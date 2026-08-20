# -*- coding: utf-8 -*-
"""Фігури до теми «OAuth 2.0 і OpenID Connect».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PURPLE = "#7b1fa2"


# ── 1. Парольний антипатерн проти делегованого доступу ─────────────────────────
def fig_delegation_problem():
    W, H = 940, 430
    f = [text(W / 2, 28, "Парольний антипатерн проти делегованого доступу", size=16, bold=True)]

    # ── Ліва колонка: передача пароля (небезпечно) ──
    lx = 24
    f.append(rect(lx, 50, 430, 360, fill="#fffdfa", stroke=POS, sw=1.8, rx=12))
    f.append(text(lx + 215, 76, "Парольний антипатерн: довіра пароля клієнту", size=13, color=POS, bold=True))

    # Клієнт
    f.append(rect(lx + 20, 110, 110, 64, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(lx + 75, 136, "Сторонній", size=12, color=INK, bold=True))
    f.append(text(lx + 75, 156, "застосунок", size=11, color=MUTED))

    # Користувач
    f.append(rect(lx + 160, 110, 110, 64, fill="#fdf0ee", stroke=POS, sw=1.6, rx=8))
    f.append(text(lx + 215, 136, "Користувач", size=12, color=POS, bold=True))
    f.append(text(lx + 215, 156, "віддає логін+пароль", size=10, color=POS, italic=True))

    # Сервер
    f.append(rect(lx + 300, 110, 110, 64, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(lx + 355, 136, "Сервер", size=12, color=INK, bold=True))
    f.append(text(lx + 355, 156, "з даними", size=11, color=MUTED))

    f.append(arrow(lx + 215, 174, lx + 75, 174, color=POS, sw=1.6))
    f.append(arrow(lx + 75, 186, lx + 355, 186, color=POS, sw=1.6))
    f.append(text(lx + 215, 206, "клієнт входить під іменем користувача", size=10.5, color=POS, italic=True))

    # Вади
    f.append(fitbox(lx + 20, 226, 390, 38,
                    "− Необмежені права: клієнт має доступ до ВСІХ даних акаунта",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.3, color=INK))
    f.append(fitbox(lx + 20, 270, 390, 38,
                    "− Неможливо відкликати доступ без повної зміни пароля",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.3, color=INK))
    f.append(fitbox(lx + 20, 314, 390, 38,
                    "− Злам стороннього застосунку розкриває головний пароль",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.3, color=INK))
    f.append(fitbox(lx + 20, 358, 390, 38,
                    "− Клієнт мусить зберігати пароль у відкритому вигляді",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.3, color=INK))

    # ── Права колонка: делегування через токен ──
    rx = 486
    f.append(rect(rx, 50, 430, 360, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(rx + 215, 76, "OAuth 2.0: делегований доступ за токеном", size=13, color=FIELD, bold=True))

    # Клієнт
    f.append(rect(rx + 20, 110, 104, 64, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(rx + 72, 136, "Сторонній", size=12, color=INK, bold=True))
    f.append(text(rx + 72, 156, "застосунок", size=11, color=MUTED))

    # Сервер авторизації
    f.append(rect(rx + 154, 110, 122, 64, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(rx + 215, 134, "Сервер", size=12, color=FIELD, bold=True))
    f.append(text(rx + 215, 154, "авторизації", size=11, color=FIELD, bold=True))

    # Сервер ресурсів
    f.append(rect(rx + 306, 110, 104, 64, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(rx + 358, 136, "Сервер", size=12, color=INK, bold=True))
    f.append(text(rx + 358, 156, "ресурсів (API)", size=11, color=MUTED))

    f.append(arrow(rx + 72, 174, rx + 215, 174, color=FIELD, sw=1.6))
    f.append(arrow(rx + 72, 186, rx + 358, 186, color=FIELD, sw=1.6))
    f.append(text(rx + 215, 206, "клієнт пред'являє лише обмежений токен", size=10.5, color=FIELD, italic=True))

    # Переваги
    f.append(fitbox(rx + 20, 226, 390, 38,
                    "+ Принцип найменших привілеїв: доступ лише до дозволених scopes",
                    size=11.5, fill="#eef7f0", stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(rx + 20, 270, 390, 38,
                    "+ Миттєве відкликання окремого токена без шкоди для пароля",
                    size=11.5, fill="#eef7f0", stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(rx + 20, 314, 390, 38,
                    "+ Пароль вводиться виключно на домені сервера авторизації",
                    size=11.5, fill="#eef7f0", stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(rx + 20, 358, 390, 38,
                    "+ Токен має короткий строк дії (TTL) та чітку аудиторію",
                    size=11.5, fill="#eef7f0", stroke=FIELD, sw=1.3, color=INK))

    render(os.path.join(IMG, "delegation-problem.svg"), W, H, *f)


# ── 2. Чотири ролі в архітектурі OAuth 2.0 / OIDC ──────────────────────────────
def fig_roles_quadrant():
    W, H = 940, 460
    f = [text(W / 2, 28, "Чотири ролі в архітектурі OAuth 2.0 та OpenID Connect", size=16, bold=True)]

    # 1. Власник ресурсу (зверху ліворуч)
    f.append(rect(40, 60, 400, 160, fill="#fffdfa", stroke=AMBER, sw=1.8, rx=12))
    f.append(text(240, 88, "Власник ресурсу (Resource Owner)", size=13, color=AMBER, bold=True))
    f.append(fitbox(56, 102, 368, 104,
                    "Людина, якій належать дані (профіль, фото, контакти).\n"
                    "• Автентифікується на сервері авторизації;\n"
                    "• Переглядає запитувані права (scopes);\n"
                    "• Надає згоду (consent) на делегування доступу.",
                    size=11.5, fill=BG, stroke=GRAY, sw=1.2))

    # 2. Клієнт (знизу ліворуч)
    f.append(rect(40, 250, 400, 180, fill="#f4f7fe", stroke=NEG, sw=1.8, rx=12))
    f.append(text(240, 276, "Клієнт (Client Application)", size=13, color=NEG, bold=True))
    f.append(fitbox(56, 290, 368, 126,
                    "Застосунок, який бажає діяти від імені користувача.\n"
                    "• Конфіденційний: бекенд із таємним client_secret;\n"
                    "• Публічний: SPA у браузері або мобільний застосунок;\n"
                    "• Отримує токени та використовує їх для викликів API.",
                    size=11.5, fill=BG, stroke=GRAY, sw=1.2))

    # 3. Сервер авторизації / IdP (зверху праворуч)
    f.append(rect(500, 60, 400, 160, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(700, 88, "Сервер авторизації / IdP (Auth Server)", size=13, color=FIELD, bold=True))
    f.append(fitbox(516, 102, 368, 104,
                    "Центральний довірений вузол автентифікації.\n"
                    "• Перевіряє особу користувача (пароль, MFA);\n"
                    "• Запитує згоду та видає авторизаційний код;\n"
                    "• Генерує та підписує токени (access, id, refresh).",
                    size=11.5, fill=BG, stroke=GRAY, sw=1.2))

    # 4. Сервер ресурсів / API (знизу праворуч)
    f.append(rect(500, 250, 400, 180, fill="#fbf8ff", stroke=PURPLE, sw=1.8, rx=12))
    f.append(text(700, 276, "Сервер ресурсів (Resource Server / API)", size=13, color=PURPLE, bold=True))
    f.append(fitbox(516, 290, 368, 126,
                    "Сервер, що зберігає цільові дані й захищений API.\n"
                    "• Приймає HTTP-запити із заголовком Authorization;\n"
                    "• Перевіряє валідність та підпис access_token;\n"
                    "• Звіряє scopes із потрібними дозволами на дію.",
                    size=11.5, fill=BG, stroke=GRAY, sw=1.2))

    # Сполучні стрілки між квадрантами
    f.append(arrow(240, 220, 240, 248, color=GRAY, sw=1.5))
    f.append(arrow(700, 220, 700, 248, color=GRAY, sw=1.5))
    f.append(arrow(440, 140, 498, 140, color=GRAY, sw=1.5))
    f.append(arrow(440, 340, 498, 340, color=GRAY, sw=1.5))

    render(os.path.join(IMG, "roles-quadrant.svg"), W, H, *f)


# ── 3. Потік коду авторизації з розширенням PKCE ──────────────────────────────
def fig_auth_code_pkce_flow():
    W, H = 960, 520
    f = [text(W / 2, 26, "Повний потік авторизаційного коду з PKCE (Authorization Code + PKCE)", size=15, bold=True)]

    # Колонки учасників
    cols = [
        (100, "Користувач\n(Браузер)", "#fffdfa", AMBER),
        (350, "Клієнтський\nзастосунок", "#f4f7fe", NEG),
        (620, "Сервер авторизації\n(Auth Server / IdP)", "#eef7f0", FIELD),
        (870, "Сервер ресурсів\n(API)", "#fbf8ff", PURPLE),
    ]

    for cx, label, fill, col in cols:
        f.append(rect(cx - 75, 48, 150, 44, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(mtext(cx, 63, label, size=11, color=col, bold=True))
        f.append(line(cx, 94, cx, 490, color=GRAY, sw=1.2, dash="4 4"))

    # Фронт-канал (виділена зона)
    f.append(rect(16, 102, 928, 192, fill="#fdfcf7", stroke=AMBER, sw=1.2, rx=10))
    f.append(text(200, 120, "ФРОНТ-КАНАЛ (через браузер користувача)", size=10.5, color=AMBER, bold=True))

    # Крок 1: Клієнт генерує verifier/challenge і редіректить користувача
    f.append(fitbox(270, 126, 160, 32, "code_verifier\nchallenge = SHA256(v)", size=9.5, fill=BG, stroke=NEG, sw=1.1))
    f.append(arrow(350, 168, 618, 168, color=INK, sw=1.4))
    f.append(text(485, 162, "1. GET /authorize?response_type=code&code_challenge=...&state=...", size=10, color=INK))

    # Крок 2: Вхід і згода
    f.append(arrow(620, 200, 102, 200, color=FIELD, sw=1.4))
    f.append(text(360, 194, "2. Форма автентифікації та екран надання дозволів (Consent)", size=10, color=FIELD))

    f.append(arrow(100, 230, 618, 230, color=INK, sw=1.4))
    f.append(text(360, 224, "3. Користувач підтверджує особу й дозволи", size=10, color=INK))

    # Крок 3: Редірект із кодом
    f.append(arrow(620, 262, 352, 262, color=FIELD, sw=1.4))
    f.append(text(485, 256, "4. 302 Redirect: /callback?code=AUTH_CODE&state=...", size=10, color=FIELD, bold=True))

    # Бек-канал (виділена зона)
    f.append(rect(16, 306, 928, 190, fill="#f6f9fc", stroke=NEG, sw=1.2, rx=10))
    f.append(text(200, 324, "БЕК-КАНАЛ (прямий захищений HTTPS між серверами)", size=10.5, color=NEG, bold=True))

    # Крок 4: Обмін коду на токени
    f.append(arrow(350, 348, 618, 348, color=NEG, sw=1.5))
    f.append(text(485, 342, "5. POST /token (code + code_verifier + client_secret)", size=10, color=NEG, bold=True))

    # Перевірка на сервері авторизації
    f.append(fitbox(540, 362, 160, 26, "Звірка: SHA256(verifier) == challenge", size=9.5, fill=BG, stroke=FIELD, sw=1.1))

    f.append(arrow(620, 404, 352, 404, color=FIELD, sw=1.5))
    f.append(text(485, 398, "6. Відповідь: { access_token, id_token, refresh_token }", size=10, color=FIELD, bold=True))

    # Крок 5: Запит до API
    f.append(arrow(350, 444, 868, 444, color=PURPLE, sw=1.5))
    f.append(text(610, 438, "7. GET /api/resource (Authorization: Bearer <access_token>)", size=10, color=PURPLE))

    f.append(arrow(870, 472, 352, 472, color=PURPLE, sw=1.5))
    f.append(text(610, 466, "8. Захищені дані ресурсу (200 OK + JSON)", size=10, color=PURPLE))

    render(os.path.join(IMG, "auth-code-pkce-flow.svg"), W, H, *f)


# ── 4. Тріада токенів: Access Token, ID Token, Refresh Token ──────────────────
def fig_token_triad():
    W, H = 940, 440
    f = [text(W / 2, 28, "Тріада токенів у сучасній архітектурі OIDC та OAuth 2.0", size=16, bold=True)]

    # 1. ID Token
    f.append(rect(24, 60, 280, 350, fill="#eef2fb", stroke=NEG, sw=1.8, rx=11))
    f.append(text(164, 88, "ID Token (Ідентичність)", size=13, color=NEG, bold=True))
    f.append(text(164, 108, "Для кого: КЛІЄНТСЬКИЙ ЗАСТОСУНОК", size=10, color=NEG, bold=True))
    f.append(fitbox(38, 122, 252, 80,
                    "Формат: Завжди підписаний JWT.\n"
                    "Питання: ХТО цей користувач?\n"
                    "Призначення: Доказ успішної автентифікації.",
                    size=11, fill=BG, stroke=GRAY, sw=1.2))
    f.append(fitbox(38, 214, 252, 110,
                    "Ключові твердження (claims):\n"
                    "• sub: унікальний ID особи\n"
                    "• iss: URL провайдера (IdP)\n"
                    "• aud: client_id застосунку\n"
                    "• exp / iat: строк дії та час видачі\n"
                    "• nonce: захист від повтору",
                    size=10.5, fill=BG, stroke=NEG, sw=1.2))
    f.append(fitbox(38, 336, 252, 60,
                    "⚠️ Ніколи не надсилається до ресурсного API як дозвіл!",
                    size=10.5, fill="#fdecea", stroke=POS, sw=1.2, color=POS, bold=True))

    # 2. Access Token
    f.append(rect(330, 60, 280, 350, fill="#fbf8ff", stroke=PURPLE, sw=1.8, rx=11))
    f.append(text(470, 88, "Access Token (Доступ)", size=13, color=PURPLE, bold=True))
    f.append(text(470, 108, "Для кого: СЕРВЕР РЕСУРСІВ (API)", size=10, color=PURPLE, bold=True))
    f.append(fitbox(344, 122, 252, 80,
                    "Формат: JWT або Opaque (посилання).\n"
                    "Питання: ЩО дозволено робити?\n"
                    "Призначення: Авторизація запитів до API.",
                    size=11, fill=BG, stroke=GRAY, sw=1.2))
    f.append(fitbox(344, 214, 252, 110,
                    "Ключові властивості:\n"
                    "• scope: read:photos write:orders\n"
                    "• aud: ідентифікатор API\n"
                    "• exp: короткий TTL (5–60 хв)\n"
                    "• Передається в заголовку:\n"
                    "  Authorization: Bearer <token>",
                    size=10.5, fill=BG, stroke=PURPLE, sw=1.2))
    f.append(fitbox(344, 336, 252, 60,
                    "✓ Клієнт ставиться як до «чорної скриньки» (Bearer).",
                    size=10.5, fill="#f6fbf7", stroke=FIELD, sw=1.2, color=FIELD, bold=True))

    # 3. Refresh Token
    f.append(rect(636, 60, 280, 350, fill="#fffdfa", stroke=AMBER, sw=1.8, rx=11))
    f.append(text(776, 88, "Refresh Token (Оновлення)", size=13, color=AMBER, bold=True))
    f.append(text(776, 108, "Для кого: СЕРВЕР АВТОРИЗАЦІЇ", size=10, color=AMBER, bold=True))
    f.append(fitbox(650, 122, 252, 80,
                    "Формат: Зазвичай довгий opaque-рядок.\n"
                    "Питання: Як поновити сесію без вводу пароля?\n"
                    "Призначення: Отримання свіжих токенів.",
                    size=11, fill=BG, stroke=GRAY, sw=1.2))
    f.append(fitbox(650, 214, 252, 110,
                    "Ключові властивості:\n"
                    "• Довгий TTL (дні, місяці)\n"
                    "• Зберігається у безпечному сховищі\n"
                    "• Підлягає ротації при кожному використанні (Rotation)\n"
                    "• Негайно анулюється при виході",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))
    f.append(fitbox(650, 336, 252, 60,
                    "🔒 Знищує старий токен при видачі нового (Token Rotation).",
                    size=10.5, fill="#fff8e7", stroke=AMBER, sw=1.2, color=AMBER, bold=True))

    render(os.path.join(IMG, "token-triad.svg"), W, H, *f)


# ── 5. Криптографічний замок PKCE ─────────────────────────────────────────────
def fig_pkce_lock():
    W, H = 940, 420
    f = [text(W / 2, 28, "Криптографічний замок PKCE проти перехоплення коду", size=16, bold=True)]

    # 1. Генерація на клієнті
    f.append(rect(30, 60, 260, 330, fill="#f4f7fe", stroke=NEG, sw=1.7, rx=10))
    f.append(text(160, 88, "1. Клієнт створює секрет", size=12.5, color=NEG, bold=True))
    f.append(fitbox(46, 106, 228, 80,
                    "code_verifier:\nвипадковий рядок 43..128 симв.\n(висока ентропія)",
                    size=11, fill=BG, stroke=GRAY, sw=1.2))
    f.append(fitbox(46, 198, 228, 80,
                    "code_challenge:\nBASE64URL(SHA256(verifier))\n(односторонній хеш)",
                    size=11, fill=BG, stroke=FIELD, sw=1.3))
    f.append(fitbox(46, 290, 228, 80,
                    "Клієнт ховає verifier у пам'яті,\nа challenge надсилає у запиті /authorize",
                    size=10.5, fill="#eef7f0", stroke=FIELD, sw=1.2))

    # 2. Що бачить зловмисник
    f.append(rect(330, 60, 280, 330, fill="#fffdfa", stroke=POS, sw=1.7, rx=10))
    f.append(text(470, 88, "2. Перехоплення у фронт-каналі", size=12.5, color=POS, bold=True))
    f.append(fitbox(346, 106, 248, 80,
                    "Зловмисник перехоплює:\n• code_challenge (з URL)\n• code (з редіректу)",
                    size=11, fill="#fdecea", stroke=POS, sw=1.2, color=POS))
    f.append(fitbox(346, 198, 248, 80,
                    "Але зловмисник НЕ знає\nоригінальний code_verifier!",
                    size=11.5, fill=BG, stroke=POS, sw=1.2, color=POS, bold=True))
    f.append(fitbox(346, 290, 248, 80,
                    "Відновити verifier із challenge\nнеможливо, бо SHA-256 незворотний.",
                    size=10.5, fill="#fdf0ee", stroke=POS, sw=1.2, color=INK))

    # 3. Перевірка на сервері авторизації
    f.append(rect(650, 60, 260, 330, fill="#eef7f0", stroke=FIELD, sw=1.7, rx=10))
    f.append(text(780, 88, "3. Валідація на /token", size=12.5, color=FIELD, bold=True))
    f.append(fitbox(666, 106, 228, 80,
                    "Клієнт надсилає verifier\nна бекенд-ендпоінт /token",
                    size=11, fill=BG, stroke=GRAY, sw=1.2))
    f.append(fitbox(666, 198, 228, 80,
                    "Сервер рахує:\nSHA256(надісланий verifier)\nі звіряє з збереженим challenge",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))
    f.append(fitbox(666, 290, 228, 80,
                    "✓ Збіглося → видати токени.\n✗ Зловмисник без verifier → 400 Bad Request.",
                    size=10.5, fill="#eef7f0", stroke=FIELD, sw=1.3, color=FIELD, bold=True))

    # Стрілки між етапами
    f.append(arrow(290, 238, 326, 238, color=GRAY, sw=1.5))
    f.append(arrow(610, 238, 646, 238, color=GRAY, sw=1.5))

    render(os.path.join(IMG, "pkce-cryptographic-lock.svg"), W, H, *f)


# ── 6. Шари OAuth 2.0 та OpenID Connect ───────────────────────────────────────
def fig_oauth_vs_oidc_stack():
    W, H = 940, 420
    f = [text(W / 2, 28, "Співвідношення протоколів: OpenID Connect як шар ідентичності над OAuth 2.0", size=15, bold=True)]

    # Верхній шар: OpenID Connect 1.0
    f.append(rect(60, 60, 820, 140, fill="#eef2fb", stroke=NEG, sw=2, rx=12))
    f.append(text(470, 88, "OpenID Connect 1.0 (Автентифікація та Профіль)", size=14, color=NEG, bold=True))
    f.append(fitbox(80, 104, 240, 80,
                    "ID Token (JWT)\n• sub, iss, aud, exp\n• nonce, auth_time",
                    size=11, fill=BG, stroke=NEG, sw=1.2))
    f.append(fitbox(350, 104, 240, 80,
                    "Стандартні Scopes:\nopenid, profile, email,\naddress, phone",
                    size=11, fill=BG, stroke=NEG, sw=1.2))
    f.append(fitbox(620, 104, 240, 80,
                    "Ендпоінти OIDC:\n• /.well-known/openid-conf\n• /userinfo\n• /jwks.json",
                    size=11, fill=BG, stroke=NEG, sw=1.2))

    # Стрілка надбудови
    f.append(arrow(470, 202, 470, 228, color=MUTED, sw=1.8))
    f.append(text(470, 220, "надбудований над ↓", size=10, color=MUTED, italic=True))

    # Нижній шар: OAuth 2.0 Framework
    f.append(rect(60, 236, 820, 150, fill="#fffdfa", stroke=AMBER, sw=2, rx=12))
    f.append(text(470, 262, "OAuth 2.0 Framework · RFC 6749 (Делегована авторизація)", size=14, color=AMBER, bold=True))
    f.append(fitbox(80, 280, 240, 90,
                    "Потоки надання прав:\n• Authorization Code (+ PKCE)\n• Client Credentials\n• Refresh Token Grant",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))
    f.append(fitbox(350, 280, 240, 90,
                    "Токени та безпека:\n• access_token (Bearer)\n• refresh_token\n• scope (довільні рядки)",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))
    f.append(fitbox(620, 280, 240, 90,
                    "Базові ендпоінти:\n• /authorize (фронт-канал)\n• /token (бек-канал)\n• /revoke, /introspect",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))

    render(os.path.join(IMG, "oauth-vs-oidc-stack.svg"), W, H, *f)


if __name__ == "__main__":
    fig_delegation_problem()
    fig_roles_quadrant()
    fig_auth_code_pkce_flow()
    fig_token_triad()
    fig_pkce_lock()
    fig_oauth_vs_oidc_stack()
    print("OK: 6 фігур згенеровано у", IMG)
