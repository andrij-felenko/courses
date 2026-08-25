# -*- coding: utf-8 -*-
"""Фігури до теми «OAuth 2.0: делегований доступ».
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


# ── 1. Проблема передачі пароля проти делегованого доступу ───────────────────
def fig_delegation_problem():
    W, H = 960, 430
    f = [text(W / 2, 28, "Антипатерн спільного пароля проти моделі токенів OAuth 2.0", size=16, bold=True)]

    # --- Ліва частина: Антипатерн спільного пароля ---
    lx = 30
    f.append(rect(lx, 55, 430, 350, fill="#fdf2f2", stroke=POS, sw=1.8, rx=12))
    f.append(text(lx + 215, 84, "АНТИПАТЕРН: ПЕРЕДАЧА ПАРОЛЯ", size=13, color=POS, bold=True))

    f.append(fitbox(lx + 25, 105, 380, 52,
                    "Користувач віддає сторонній програмі\nсвій майстер-логін і пароль",
                    size=12, fill=BG, stroke=POS, sw=1.3, color=INK))

    f.append(arrow(lx + 215, 162, lx + 215, 192, color=POS, sw=1.8))

    f.append(fitbox(lx + 25, 196, 380, 52,
                    "Стороння програма зберігає пароль у себе\nі звертається до сервера від імені власника",
                    size=12, fill=BG, stroke=POS, sw=1.3, color=INK))

    f.append(text(lx + 215, 275, "НАСЛІДКИ ТА ВРАЗЛИВОСТІ:", size=11.5, color=POS, bold=True))
    f.append(fitbox(lx + 25, 288, 380, 102,
                    "• Немає меж доступу: клієнт бачить і видаляє все\n"
                    "• Немає вибіркового відкликання: треба міняти пароль\n"
                    "• Витік у клієнта компрометує весь акаунт\n"
                    "• Привчає користувачів вводити паролі будь-де",
                    size=11, fill="#fff5f5", stroke=POS, sw=1.2, color=INK))

    # --- Права частина: Делегований доступ через токени ---
    rx = 500
    f.append(rect(rx, 55, 430, 350, fill="#f2f8f4", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(rx + 215, 84, "OAUTH 2.0: ДЕЛЕГОВАНИЙ ДОСТУП", size=13, color=FIELD, bold=True))

    f.append(fitbox(rx + 25, 105, 380, 52,
                    "Користувач логіниться ТІЛЬКИ на сервері авторизації\nі дає згоду на конкретну дію (scope)",
                    size=12, fill=BG, stroke=FIELD, sw=1.3, color=INK))

    f.append(arrow(rx + 215, 162, rx + 215, 192, color=FIELD, sw=1.8))

    f.append(fitbox(rx + 25, 196, 380, 52,
                    "Клієнт отримує лише тимчасовий токен доступу;\nпароль користувача йому не відкривається",
                    size=12, fill=BG, stroke=FIELD, sw=1.3, color=INK))

    f.append(text(rx + 215, 275, "ЗАХИСНІ МЕХАНІЗМИ:", size=11.5, color=FIELD, bold=True))
    f.append(fitbox(rx + 25, 288, 380, 102,
                    "• Суворі межі (scope): тільки дозволені операції\n"
                    "• Швидке точкове відкликання окремого токена\n"
                    "• Обмежений час дії токена (5-60 хвилин)\n"
                    "• Пароль залишається виключно у власника",
                    size=11, fill="#f6fcf8", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(IMG, "delegation-problem.svg"), W, H, *f)


# ── 2. Повний потік Authorization Code з PKCE ────────────────────────────────
def fig_auth_code_pkce_flow():
    W, H = 980, 540
    f = [text(W / 2, 26, "Потік Authorization Code з перевіркою PKCE (RFC 7636)", size=16, bold=True)]

    # 4 вертикальні доріжки (ролі)
    cols = [
        (40,  170, "Користувач\n(Браузер)", NEG),
        (280, 170, "Клієнт\n(Застосунок)", AMBER),
        (530, 190, "Сервер авторизації\n(/authorize, /token)", FIELD),
        (780, 160, "Сервер ресурсів\n(API даних)", PURPLE),
    ]

    for x, w, lbl, col in cols:
        f.append(rect(x, 48, w, 44, fill=BG, stroke=col, sw=1.8, rx=6))
        lines = lbl.split("\n")
        if len(lines) == 1:
            f.append(text(x + w / 2, 75, lines[0], size=12, color=col, bold=True))
        else:
            f.append(text(x + w / 2, 66, lines[0], size=11.5, color=col, bold=True))
            f.append(text(x + w / 2, 83, lines[1], size=10, color=MUTED))
        # вертикальна вісь
        cx = x + w / 2
        f.append(line(cx, 94, cx, 510, color="#d0d5dd", sw=1.5, dash="4 4"))

    u_cx = 40 + 85
    c_cx = 280 + 85
    a_cx = 530 + 95
    r_cx = 780 + 80

    # Крок 1: Генерація PKCE та старт
    y1 = 125
    f.append(fitbox(c_cx - 85, y1 - 18, 170, 36,
                    "Генерує verifier\nі challenge = SHA256",
                    size=10.5, fill="#fffdf2", stroke=AMBER, sw=1.2))

    # Крок 2: Перенаправлення на /authorize
    y2 = 175
    f.append(arrow(c_cx, y2, u_cx, y2, color=NEG, sw=1.6))
    f.append(text((c_cx + u_cx) / 2, y2 - 7, "1. 302 Редирект на /authorize", size=10.5, color=INK, bold=True))
    f.append(arrow(u_cx, y2 + 22, a_cx, y2 + 22, color=NEG, sw=1.6))
    f.append(text((u_cx + a_cx) / 2, y2 + 15, "2. GET /authorize?challenge=...&state=...", size=10, color=MUTED))

    # Крок 3: Вхід та згода
    y3 = 238
    f.append(fitbox(a_cx - 100, y3 - 18, 200, 36,
                    "Автентифікація користувача\nй підтвердження прав (Consent)",
                    size=10.5, fill="#f2fbf4", stroke=FIELD, sw=1.2))

    # Крок 4: Редирект з auth_code
    y4 = 295
    f.append(arrow(a_cx, y4, u_cx, y4, color=FIELD, sw=1.6))
    f.append(text((a_cx + u_cx) / 2, y4 - 7, "3. 302 Редирект на redirect_uri?code=XYZ&state=...", size=10.5, color=INK, bold=True))
    f.append(arrow(u_cx, y4 + 22, c_cx, y4 + 22, color=NEG, sw=1.6))
    f.append(text((u_cx + c_cx) / 2, y4 + 15, "4. Браузер повертає код клієнту", size=10, color=MUTED))

    # Роздільник каналів (Front-channel vs Back-channel)
    f.append(rect(20, 342, 940, 24, fill="#f8f9fa", stroke="#e0e0e0", sw=1, rx=4))
    f.append(text(W / 2, 358, "▲ ВІДКРИТИЙ КАНАЛ (Front-Channel)   │   ПРЯМИЙ TLS КАНАЛ (Back-Channel) ▼", size=10.5, color=MUTED, bold=True))

    # Крок 5: Прямий обмін на токен (POST /token)
    y5 = 395
    f.append(arrow(c_cx, y5, a_cx, y5, color=AMBER, sw=1.8))
    f.append(text((c_cx + a_cx) / 2, y5 - 7, "5. POST /token { code, code_verifier, client_secret }", size=10.5, color=INK, bold=True))

    y6 = 430
    f.append(arrow(a_cx, y6, c_cx, y6, color=FIELD, sw=1.8))
    f.append(text((a_cx + c_cx) / 2, y6 - 7, "6. Відповідь: { access_token, refresh_token }", size=10.5, color=FIELD, bold=True))

    # Крок 6: Запит до API
    y7 = 475
    f.append(arrow(c_cx, y7, r_cx, y7, color=PURPLE, sw=1.8))
    f.append(text((c_cx + r_cx) / 2, y7 - 7, "7. GET /api/data  [Authorization: Bearer <access_token>]", size=10.5, color=PURPLE, bold=True))

    y8 = 502
    f.append(arrow(r_cx, y8, c_cx, y8, color=PURPLE, sw=1.8))
    f.append(text((r_cx + c_cx) / 2, y8 - 7, "8. Захищені ресурси (200 OK)", size=10, color=MUTED))

    render(os.path.join(IMG, "auth-code-pkce-flow.svg"), W, H, *f)


# ── 3. Криптографічний механізм PKCE ─────────────────────────────────────────
def fig_pkce_mechanism():
    W, H = 940, 420
    f = [text(W / 2, 28, "Криптографічний захист коду авторизації через PKCE", size=16, bold=True)]

    # Фаза 1: Підготовка клієнта
    f.append(rect(30, 60, 260, 180, fill="#fffef5", stroke=AMBER, sw=1.6, rx=10))
    f.append(text(160, 85, "1. КЛІЄНТ ГЕНЕРУЄ ПАРУ", size=12, color=AMBER, bold=True))
    f.append(fitbox(45, 102, 230, 48,
                    "code_verifier:\nвипадковий рядок 43-128 симв.",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))
    f.append(arrow(160, 154, 160, 172, color=AMBER, sw=1.5))
    f.append(fitbox(45, 176, 230, 48,
                    "code_challenge:\nBASE64URL( SHA256(verifier) )",
                    size=10.5, fill=BG, stroke=AMBER, sw=1.2))

    # Фаза 2: /authorize
    f.append(arrow(295, 190, 450, 190, color=AMBER, sw=1.8))
    f.append(text(372, 180, "надсилає challenge", size=10.5, color=INK, bold=True))

    f.append(rect(455, 60, 455, 150, fill="#f2f8f4", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(682, 85, "2. СЕРВЕР АВТОРИЗАЦІЇ ЗБЕРІГАЄ CHALLENGE", size=12, color=FIELD, bold=True))
    f.append(fitbox(475, 105, 415, 42,
                    "Зберігає пару: { code: \"XYZ\", challenge: \"E9Melb…\", method: \"S256\" }",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))
    f.append(fitbox(475, 154, 415, 42,
                    "Повертає клієнту code=\"XYZ\" через редирект браузера",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))

    # Фаза 3: Пастка для зловмисника
    f.append(rect(30, 260, 400, 140, fill="#fdf2f2", stroke=POS, sw=1.6, rx=10))
    f.append(text(230, 285, "3. ЗЛОВМИСНИК ПЕРЕХОПЛЮЄ CODE", size=12, color=POS, bold=True))
    f.append(fitbox(45, 302, 370, 42,
                    "Перехопив code=\"XYZ\" у браузері або custom URI scheme",
                    size=11, fill=BG, stroke=POS, sw=1.2))
    f.append(text(230, 362, "Але verifier зловмисник НЕ знає і обчислити не може!", size=10.5, color=POS, bold=True))
    f.append(text(230, 382, "(односторонній хеш SHA-256 незворотний)", size=10, color=MUTED, italic=True))

    # Фаза 4: Перевірка на /token
    f.append(rect(455, 230, 455, 170, fill="#f6f9fc", stroke=NEG, sw=1.6, rx=10))
    f.append(text(682, 255, "4. ЗВІРКА ПРИ ОБМІНІ НА /token", size=12, color=NEG, bold=True))
    f.append(fitbox(475, 272, 415, 46,
                    "Чесний клієнт шле: code=\"XYZ\" + code_verifier=\"...\n"
                    "Сервер обчислює SHA-256(отриманий verifier)",
                    size=10.5, fill=BG, stroke=NEG, sw=1.2))
    f.append(fitbox(475, 326, 415, 60,
                    "SHA256(verifier) == збережений challenge → видати токен ✓\n"
                    "Немає verifier або хеш не зійшовся → 400 Bad Request ✗",
                    size=11, fill="#eef4fa", stroke=NEG, sw=1.2, color=INK))

    render(os.path.join(IMG, "pkce-mechanism.svg"), W, H, *f)


# ── 4. Життєвий цикл токенів і ротація Refresh Token ─────────────────────────
def fig_token_lifecycle():
    W, H = 940, 430
    f = [text(W / 2, 28, "Життєвий цикл Access Token та ротація Refresh Token", size=16, bold=True)]

    # --- Звичайна робота: короткоживучий Access Token ---
    f.append(rect(30, 60, 420, 160, fill="#f2f8f4", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(240, 85, "АКТИВНИЙ ДОСТУП (Access Token)", size=12, color=FIELD, bold=True))
    f.append(fitbox(50, 102, 380, 46,
                    "Access Token (дійсний 15 хв):\nклієнт надсилає до Resource Server у кожному запиті",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))
    f.append(fitbox(50, 156, 380, 48,
                    "Через 15 хв токен стає недійсним (401 Expired);\nвитік небезпечний лише короткий час",
                    size=11, fill="#f6fcf8", stroke=FIELD, sw=1.2))

    # Стрілка оновлення
    f.append(arrow(240, 224, 240, 258, color=AMBER, sw=1.8))
    f.append(text(240, 245, "POST /token { refresh_token }", size=10.5, color=AMBER, bold=True))

    # --- Ротація Refresh Token ---
    f.append(rect(30, 265, 420, 145, fill="#fffef5", stroke=AMBER, sw=1.6, rx=10))
    f.append(text(240, 290, "РОТАЦІЯ REFRESH TOKEN (Rotation)", size=12, color=AMBER, bold=True))
    f.append(fitbox(50, 308, 380, 46,
                    "Сервер видає: новий Access Token + новий Refresh Token;\nстарий Refresh Token негайно інвалідується",
                    size=11, fill=BG, stroke=AMBER, sw=1.2))
    f.append(fitbox(50, 360, 380, 38,
                    "Кожен токен оновлення строго одноразовий!",
                    size=11, fill="#fffaf0", stroke=AMBER, sw=1.2, color=INK))

    # --- Права частина: Виявлення витоку (Reuse Detection) ---
    f.append(rect(480, 60, 430, 350, fill="#fdf2f2", stroke=POS, sw=1.7, rx=12))
    f.append(text(695, 88, "ВИЯВЛЕННЯ ВИТОКУ (Reuse Detection)", size=13, color=POS, bold=True))

    f.append(fitbox(505, 110, 380, 56,
                    "Сценарій: зловмисник викрав старий Refresh Token\nі пробує використати його для отримання доступу",
                    size=11.5, fill=BG, stroke=POS, sw=1.3, color=INK))

    f.append(arrow(695, 172, 695, 202, color=POS, sw=1.8))

    f.append(fitbox(505, 206, 380, 56,
                    "Сервер бачить запит з уже погашеним токеном:\nце маркер компрометації ланцюжка сесії!",
                    size=11.5, fill=BG, stroke=POS, sw=1.3, color=INK))

    f.append(arrow(695, 268, 695, 298, color=POS, sw=1.8))

    f.append(fitbox(505, 302, 380, 88,
                    "РЕАКЦІЯ БЕЗПЕКИ СЕРВЕРА:\n"
                    "• Негайно блокує всі токени цієї родини (family)\n"
                    "• Примусово розриває активну сесію\n"
                    "• Вимагає у користувача повну повторну автентифікацію",
                    size=11, fill="#fff5f5", stroke=POS, sw=1.3, color=POS))

    render(os.path.join(IMG, "token-lifecycle.svg"), W, H, *f)


if __name__ == "__main__":
    fig_delegation_problem()
    fig_auth_code_pkce_flow()
    fig_pkce_mechanism()
    fig_token_lifecycle()
    print("Усі 4 фігури успішно згенеровано.")
