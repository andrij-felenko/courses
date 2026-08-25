# -*- coding: utf-8 -*-
"""Фігури теми «Токени й заголовки автентифікації». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. auth-schemes-comparison: порівняння трьох схем передачі креденціалів ──
def fig_auth_schemes():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, 980, 460, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 40, "Схеми передачі облікових даних у HTTP-заголовках", size=15, bold=True, color=INK))

    col_w = 305
    xs = [30, 347, 665]

    # Стовпець 1: Basic Authentication
    x1 = xs[0]
    f.append(rect(x1, 65, col_w, 385, fill=FILL, stroke=POS, sw=1.5, rx=6))
    f.append(text(x1 + col_w/2, 95, "HTTP Basic Auth", size=13, bold=True, color=POS))
    f.append(text(x1 + col_w/2, 115, "RFC 7617 (успадковано від RFC 1945)", size=10, color=MUTED, italic=True))

    b1, _, _ = textbox(x1 + col_w/2, 160, "Заголовок:\nAuthorization: Basic dXNlcjpwYXNz\n(Base64 від «user:password»)",
                       size=10, min_w=col_w - 24, pad=8, fill=BG, stroke=LINE)
    f.append(b1)

    f.append(text(x1 + 16, 215, "Механізм:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x1 + 16, 235, "• Сирий пароль у кожному запиті", size=10, anchor="start", color=INK))
    f.append(text(x1 + 16, 255, "• Base64 — не шифрування!", size=10, anchor="start", color=POS, bold=True))
    f.append(text(x1 + 16, 275, "• Сервер перевіряє хеш у БД щоразу", size=10, anchor="start", color=INK))

    f.append(text(x1 + 16, 310, "Переваги та недоліки:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x1 + 16, 330, "✓ Гранично простий у реалізації", size=10, anchor="start", color=FIELD))
    f.append(text(x1 + 16, 350, "✗ Пароль постійно зберігається в клієнті", size=10, anchor="start", color=POS))
    f.append(text(x1 + 16, 370, "✗ Неможливо відкликати сесію без зміни пароля", size=10, anchor="start", color=POS))
    f.append(text(x1 + 16, 390, "✗ Немає гранулярних прав (scopes)", size=10, anchor="start", color=POS))
    f.append(text(x1 + col_w/2, 430, "Застосування: внутрішні утиліти, legacy", size=10, bold=True, color=MUTED))

    # Стовпець 2: API Keys
    x2 = xs[1]
    f.append(rect(x2, 65, col_w, 385, fill=FILL, stroke=NEG, sw=1.5, rx=6))
    f.append(text(x2 + col_w/2, 95, "API Keys (Ключі API)", size=13, bold=True, color=NEG))
    f.append(text(x2 + col_w/2, 115, "Де-факто стандарт machine-to-machine", size=10, color=MUTED, italic=True))

    b2, _, _ = textbox(x2 + col_w/2, 160, "Заголовок:\nX-API-Key: ak_live_9f82b7c4d1\n(або Authorization: ApiKey ...)",
                       size=10, min_w=col_w - 24, pad=8, fill=BG, stroke=LINE)
    f.append(b2)

    f.append(text(x2 + 16, 215, "Механізм:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x2 + 16, 235, "• Довгий криптостійкий псевдовипадковий ключ", size=10, anchor="start", color=INK))
    f.append(text(x2 + 16, 255, "• Прив'язаний до акаунту або сервісу", size=10, anchor="start", color=INK))
    f.append(text(x2 + 16, 275, "• Пошук у сховищі ключів / пам'яті шлюзу", size=10, anchor="start", color=INK))

    f.append(text(x2 + 16, 310, "Переваги та недоліки:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x2 + 16, 330, "✓ Не розкриває головний пароль обліковки", size=10, anchor="start", color=FIELD))
    f.append(text(x2 + 16, 350, "✓ Легко прив'язати до rate-limit лімітів", size=10, anchor="start", color=FIELD))
    f.append(text(x2 + 16, 370, "✗ Статичний: витік вимагає ручної ротації", size=10, anchor="start", color=POS))
    f.append(text(x2 + 16, 390, "✗ Безстроковий або має дуже тривалий TTL", size=10, anchor="start", color=POS))
    f.append(text(x2 + col_w/2, 430, "Застосування: B2B API, CLI, автоматизація", size=10, bold=True, color=MUTED))

    # Стовпець 3: Bearer Tokens (OAuth 2.0 / JWT)
    x3 = xs[2]
    f.append(rect(x3, 65, col_w, 385, fill=FILL, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(x3 + col_w/2, 95, "Bearer Token (OAuth 2.0 / JWT)", size=13, bold=True, color=FIELD))
    f.append(text(x3 + col_w/2, 115, "RFC 6750, RFC 7519", size=10, color=MUTED, italic=True))

    b3, _, _ = textbox(x3 + col_w/2, 160, "Заголовок:\nAuthorization: Bearer eyJhbGciOi...\n(Access Token: криптопідпис + claims)",
                       size=10, min_w=col_w - 24, pad=8, fill=BG, stroke=LINE)
    f.append(b3)

    f.append(text(x3 + 16, 215, "Механізм:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x3 + 16, 235, "• Короткоживучий токен (TTL = 5–15 хв)", size=10, anchor="start", color=INK))
    f.append(text(x3 + 16, 255, "• Автономна перевірка підпису на шлюзі", size=10, anchor="start", color=INK))
    f.append(text(x3 + 16, 275, "• Оновлюється через Refresh Token", size=10, anchor="start", color=INK))

    f.append(text(x3 + 16, 310, "Переваги та недоліки:", size=11, bold=True, anchor="start", color=INK))
    f.append(text(x3 + 16, 330, "✓ Мінімальне вікно компрометації", size=10, anchor="start", color=FIELD))
    f.append(text(x3 + 16, 350, "✓ Тонкі права (scopes), ідентичність у payload", size=10, anchor="start", color=FIELD))
    f.append(text(x3 + 16, 370, "✓ Без запитів до бази на кожен HTTP-виклик", size=10, anchor="start", color=FIELD))
    f.append(text(x3 + 16, 390, "✗ Вимагає клієнтської логіки оновлення", size=10, anchor="start", color=MUTED))
    f.append(text(x3 + col_w/2, 430, "Застосування: SPA, мобільні клієнти, мікросервіси", size=10, bold=True, color=MUTED))

    render(out("auth-schemes-comparison.svg"), W, H, *f,
           title="Порівняння схем передачі автентифікаційних даних у HTTP-заголовках")


# ── 2. token-lifecycle-and-refresh: таймлайн автентифікації та рефрешу ───────
def fig_token_lifecycle():
    W, H = 1000, 520
    f = []

    f.append(rect(10, 10, 980, 500, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 38, "Життєвий цикл пари Access/Refresh токенів та автоматичне оновлення", size=14, bold=True, color=INK))

    x_c = 150
    x_r = 500
    x_a = 850

    bc, _, _ = textbox(x_c, 75, "Клієнтський застосунок\n(HTTP Interceptor)", size=11, bold=True, min_w=170, pad=6, fill=BLUE_F, stroke=NEG)
    br, _, _ = textbox(x_r, 75, "Ресурсний сервер\n(API Gateway / Data)", size=11, bold=True, min_w=170, pad=6, fill=GREEN_F, stroke=FIELD)
    ba, _, _ = textbox(x_a, 75, "Сервер авторизації\n(OAuth2 Token Endpoint)", size=11, bold=True, min_w=170, pad=6, fill=WARN_F, stroke=POS)
    f.append(bc); f.append(br); f.append(ba)

    f.append(line(x_c, 110, x_c, 480, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x_r, 110, x_r, 480, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x_a, 110, x_a, 480, color=MUTED, sw=1, dash="4,4"))

    # Крок 1: Первинна авторизація
    y1 = 140
    f.append(arrow(x_c, y1, x_a, y1, color=NEG, sw=1.5))
    f.append(text((x_c + x_a)/2, y1 - 8, "1. POST /oauth/token (креденціали або Auth Code)", size=10, bold=True, color=NEG))

    y2 = 175
    f.append(arrow(x_a, y2, x_c, y2, color=FIELD, sw=1.5))
    f.append(text((x_c + x_a)/2, y2 - 8, "2. 200 OK: { access_token_1 (exp: 15m), refresh_token_1 (exp: 30d) }", size=10, bold=True, color=FIELD))

    # Крок 2: Звичайний виклик API
    y3 = 220
    f.append(arrow(x_c, y3, x_r, y3, color=INK, sw=1.5))
    f.append(text((x_c + x_r)/2, y3 - 8, "3. GET /api/orders (Authorization: Bearer access_token_1)", size=10, color=INK))

    y4 = 250
    f.append(arrow(x_r, y4, x_c, y4, color=FIELD, sw=1.5))
    f.append(text((x_c + x_r)/2, y4 - 8, "4. 200 OK (дані замовлень)", size=10, color=FIELD))

    # Маркер завершення терміну дії
    y_exp = 285
    f.append(rect(60, y_exp - 12, 880, 24, fill=RED_F, stroke=POS, sw=1, rx=4))
    f.append(text(500, y_exp + 4, "⏰ Минуло 15 хвилин: access_token_1 прострочився (expired)", size=10, bold=True, color=POS))

    # Крок 3: Запит із застарілим токеном і 401
    y5 = 330
    f.append(arrow(x_c, y5, x_r, y5, color=POS, sw=1.5))
    f.append(text((x_c + x_r)/2, y5 - 8, "5. GET /api/profile (Bearer access_token_1)", size=10, color=POS))

    y6 = 360
    f.append(arrow(x_r, y6, x_c, y6, color=POS, sw=1.5))
    f.append(text((x_c + x_r)/2, y6 - 8, "6. 401 Unauthorized (WWW-Authenticate: error=\"invalid_token\")", size=10, bold=True, color=POS))

    # Крок 4: Автоматичне оновлення токена
    y7 = 400
    f.append(arrow(x_c, y7, x_a, y7, color=NEG, sw=1.5))
    f.append(text((x_c + x_a)/2, y7 - 8, "7. POST /oauth/token { grant_type: \"refresh_token\", refresh_token_1 }", size=10, bold=True, color=NEG))

    y8 = 430
    f.append(arrow(x_a, y8, x_c, y8, color=FIELD, sw=1.5))
    f.append(text((x_c + x_a)/2, y8 - 8, "8. 200 OK: { access_token_2, refresh_token_2 (ротація) }", size=10, bold=True, color=FIELD))

    # Крок 5: Прозорий повтор оригінального запиту
    y9 = 465
    f.append(arrow(x_c, y9, x_r, y9, color=FIELD, sw=1.5))
    f.append(text((x_c + x_r)/2, y9 - 8, "9. Повтор: GET /api/profile (Bearer access_token_2) ➔ 200 OK", size=10, bold=True, color=FIELD))

    render(out("token-lifecycle-and-refresh.svg"), W, H, *f,
           title="Життєвий цикл пари Access/Refresh токенів та автоматичне оновлення на клієнті")


# ── 3. concurrent-refresh-mutex: гонитва запитів проти клієнтського м'ютекса ─
def fig_concurrent_refresh():
    W, H = 1040, 470
    f = []

    f.append(rect(10, 10, 1020, 450, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(520, 38, "Конкурентні запити: катастрофа подвійного рефрешу проти клієнтського м'ютекса", size=14, bold=True, color=INK))

    # Ліва колонка: Без синхронізації
    f.append(rect(25, 60, 480, 380, fill=FILL, stroke=POS, sw=1.5, rx=6))
    f.append(text(265, 88, "Без синхронізації: паралельний 401 і крах", size=12, bold=True, color=POS))

    t_box1, _, _ = textbox(110, 140, "Потік 1:\nGET /api/cart\n(Отримує 401)", size=9.5, min_w=110, pad=6, fill=RED_F, stroke=POS)
    t_box2, _, _ = textbox(110, 215, "Потік 2:\nGET /api/user\n(Отримує 401)", size=9.5, min_w=110, pad=6, fill=RED_F, stroke=POS)
    t_box3, _, _ = textbox(110, 290, "Потік 3:\nGET /api/feed\n(Отримує 401)", size=9.5, min_w=110, pad=6, fill=RED_F, stroke=POS)
    f.append(t_box1); f.append(t_box2); f.append(t_box3)

    auth_box1, _, _ = textbox(380, 215, "Auth Server\n\n• Рефреш 1: Оновлено\n• Рефреш 2: Помилка! R1 спалено\n• Виявлено атаку Replay!\n• ➔ Сесію заблоковано",
                              size=9, min_w=170, pad=6, fill=BG, stroke=POS)
    f.append(auth_box1)

    f.append(arrow(170, 140, 290, 190, color=POS, sw=1.2))
    f.append(arrow(170, 215, 290, 215, color=POS, sw=1.2))
    f.append(arrow(170, 290, 290, 240, color=POS, sw=1.2))

    f.append(text(265, 360, "✗ Усі три потоки паралельно слали Refresh_Token_1", size=10, bold=True, color=POS))
    f.append(text(265, 380, "✗ Ротація токенів розцінила другий рефреш як крадіжку", size=9.5, color=POS))
    f.append(text(265, 400, "✗ Сесію розірвано, користувача викинуло на Login", size=9.5, bold=True, color=POS))

    # Права колонка: Із м'ютексом та чергою запитів
    f.append(rect(535, 60, 480, 380, fill=FILL, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(775, 88, "З м'ютексом: Single-Flight Refresh + черга", size=12, bold=True, color=FIELD))

    p1_box, _, _ = textbox(620, 140, "Потік 1 (Winner):\nЗахопив Mutex\n➔ Шле POST /refresh", size=9.5, min_w=125, pad=6, fill=GREEN_F, stroke=FIELD)
    p23_box, _, _ = textbox(620, 220, "Потоки 2 та 3:\nЗаблоковані на CV\nЧекають нового токена", size=9.5, min_w=125, pad=6, fill=BLUE_F, stroke=NEG)
    f.append(p1_box); f.append(p23_box)

    auth_box2, _, _ = textbox(890, 140, "Auth Server\n\n• 1 запит на рефреш\n• Повертає Token 2\n• Успішна ротація",
                              size=9, min_w=140, pad=6, fill=BG, stroke=FIELD)
    f.append(auth_box2)

    f.append(arrow(690, 140, 810, 140, color=FIELD, sw=1.5))
    f.append(arrow(810, 160, 690, 160, color=FIELD, sw=1.5))

    retry_box, _, _ = textbox(775, 305, "Потоки 1, 2, 3 прокидаються, беруть новий Access Token 2\nта прозоро повторюють свої оригінальні API-запити",
                              size=9.5, min_w=420, pad=8, fill=GREEN_F, stroke=FIELD)
    f.append(retry_box)

    f.append(arrow(620, 255, 660, 285, color=FIELD, sw=1.2))
    f.append(arrow(620, 175, 660, 285, color=FIELD, sw=1.2))

    f.append(text(775, 375, "✓ Лише ОДИН мережевий запит на оновлення токена", size=10, bold=True, color=FIELD))
    f.append(text(775, 395, "✓ Нуль помилок авторизації, UI не помічає затримки", size=9.5, color=FIELD))

    render(out("concurrent-refresh-mutex.svg"), W, H, *f,
           title="Конкурентні запити: запобігання гонитві оновлення токенів через м'ютекс")


if __name__ == "__main__":
    fig_auth_schemes()
    fig_token_lifecycle()
    fig_concurrent_refresh()
    print("OK: generated 3 figures in", IMG)
