# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_same_origin_tuple():
    """Складові походження (Origin) та матриця відповідності SOP."""
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 28, "Анатомія походження (Origin) за RFC 6454 та правила ізоляції",
                      size=16, bold=True))

    # ── Верхній блок: Базове походження
    frags.append(rect(40, 55, 860, 95, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 78, "Еталонне походження: https://example.com:443/app/index.html", size=13, bold=True, color=INK))

    # Три компоненти
    frags.append(rect(60, 95, 230, 42, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(175, 114, "Схема (Протокол)", size=11, bold=True, color=FIELD))
    frags.append(text(175, 129, "https://", size=11, color=INK))

    frags.append(rect(320, 95, 300, 42, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(470, 114, "Хост (FQDN або IP)", size=11, bold=True, color=FIELD))
    frags.append(text(470, 129, "example.com", size=11, color=INK))

    frags.append(rect(650, 95, 230, 42, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(765, 114, "Порт (явний або неявний)", size=11, bold=True, color=FIELD))
    frags.append(text(765, 129, "443 (стандартний для https)", size=11, color=INK))

    # ── Нижній блок: Матриця перевірки походження
    frags.append(rect(40, 165, 860, 260, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(470, 190, "Порівняння цільових адрес із еталонним https://example.com:443", size=13, bold=True))

    rows = [
        ("https://example.com/api/v1/users", "Однакове (Same Origin)", "Шлях (/api/v1) не входить до складу походження", True),
        ("https://example.com:8443/data", "Різне (Cross-Origin)", "Порт не збігається (8443 != 443)", False),
        ("http://example.com/login", "Різне (Cross-Origin)", "Схема не збігається (http != https)", False),
        ("https://api.example.com/users", "Різне (Cross-Origin)", "Піддомен є окремим самостійним хостом", False),
        ("https://v2.example.com:443/auth", "Різне (Cross-Origin)", "Хост v2.example.com відрізняється від example.com", False)
    ]

    # Шапка таблиці
    frags.append(rect(55, 205, 340, 28, fill="#e5e7eb", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(225, 224, "Цільова адреса запиту", size=11, bold=True))

    frags.append(rect(405, 205, 180, 28, fill="#e5e7eb", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(495, 224, "Статус SOP", size=11, bold=True))

    frags.append(rect(595, 205, 290, 28, fill="#e5e7eb", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(740, 224, "Причина та вердикт браузера", size=11, bold=True))

    y_pos = 240
    for url, status, reason, is_same in rows:
        bg_col = "#eafaf1" if is_same else "#fdecea"
        brd_col = FIELD if is_same else POS
        txt_col = FIELD if is_same else POS
        sign = "✓ " if is_same else "✗ "

        frags.append(rect(55, y_pos, 340, 32, fill=FILL, stroke="#d1d5db", sw=1.0, rx=4))
        frags.append(text(65, y_pos + 20, url, size=10, color=INK, anchor="start"))

        frags.append(rect(405, y_pos, 180, 32, fill=bg_col, stroke=brd_col, sw=1.0, rx=4))
        frags.append(text(495, y_pos + 20, sign + status, size=10, bold=True, color=txt_col))

        frags.append(rect(595, y_pos, 290, 32, fill=FILL, stroke="#d1d5db", sw=1.0, rx=4))
        frags.append(text(605, y_pos + 20, reason, size=10, color=MUTED, anchor="start"))

        y_pos += 36

    frags.append(text(W / 2, 450, "Будь-яка розбіжність у схемі, хості або порті робить запит міжсайтовим і вимагає узгодження через CORS",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "same-origin-tuple.svg"), W, H, *frags)


def fig_cors_flow():
    """Порівняння простого (Simple) та попереднього (Preflighted) запитів CORS."""
    W, H = 940, 520
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл запитів CORS: простий проти перевіреного (Preflight)",
                      size=16, bold=True))

    # ── Ліва колонка: Простий запит (Simple Request)
    frags.append(rect(40, 55, 420, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(250, 80, "1. Простий запит (GET / POST / HEAD)", size=13, bold=True, color=FIELD))
    frags.append(text(250, 98, "Стандартні заголовки, тіло urlencoded/form-data/text", size=10, color=MUTED))

    # Клієнт - Сервер коробки
    frags.append(rect(60, 115, 110, 35, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(115, 137, "Браузер", size=11, bold=True))

    frags.append(rect(330, 115, 110, 35, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(385, 137, "Сервер API", size=11, bold=True))

    # Прямий запит
    frags.append(arrow(115, 175, 385, 175, color=FIELD, sw=2.0))
    frags.append(text(250, 165, "GET /items + Origin: https://app.com", size=10, bold=True, color=FIELD))

    # Виконання на сервері
    s1 = textbox(385, 230, "Сервер виконує запит\nі повертає відповідь\nразом із ACAO",
                 size=9, min_w=105, fill="#f9fafb", stroke="#d1d5db")
    frags.append(s1[0])

    # Відповідь сервера
    frags.append(arrow(385, 285, 115, 285, color=FIELD, sw=2.0))
    frags.append(text(250, 275, "200 OK + Access-Control-Allow-Origin: *", size=10, bold=True, color=FIELD))

    # Перевірка в браузері
    b1 = textbox(115, 360, "Браузер перевіряє ACAO:\n• збігається → віддає JS\n• помилка → ховає дані\n(але запит уже виконано!)",
                 size=9, min_w=105, fill="#eafaf1", stroke=FIELD)
    frags.append(b1[0])

    # ── Права колонка: Запит із попередньою перевіркою (Preflighted Request)
    frags.append(rect(480, 55, 420, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(690, 80, "2. Запит із Preflight (PUT, DELETE, JSON, Auth)", size=13, bold=True, color=POS))
    frags.append(text(690, 98, "Небезпечні методи, custom заголовки або application/json", size=10, color=MUTED))

    # Клієнт - Сервер коробки
    frags.append(rect(500, 115, 110, 35, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(555, 137, "Браузер", size=11, bold=True))

    frags.append(rect(770, 115, 110, 35, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(825, 137, "Сервер API", size=11, bold=True))

    # 1. Попередній OPTIONS
    frags.append(arrow(555, 175, 825, 175, color=MUTED, sw=1.5))
    frags.append(text(690, 165, "OPTIONS /users + ACR-Method: DELETE", size=10, bold=True, color=MUTED))

    # 2. Дозвіл OPTIONS
    frags.append(arrow(825, 220, 555, 220, color=MUTED, sw=1.5))
    frags.append(text(690, 210, "204 No Content + Allow-Methods: DELETE", size=10, bold=True, color=MUTED))

    # 3. Фактичний запит
    frags.append(arrow(555, 275, 825, 275, color=POS, sw=2.0))
    frags.append(text(690, 265, "DELETE /users/42 + Origin: https://app.com", size=10, bold=True, color=POS))

    # 4. Фактична відповідь
    frags.append(arrow(825, 330, 555, 330, color=POS, sw=2.0))
    frags.append(text(690, 320, "200 OK + Access-Control-Allow-Origin", size=10, bold=True, color=POS))

    # Перевірка Preflight
    b2 = textbox(690, 395, "Якщо OPTIONS відхилено або сервер повернув 403/404,\nбраузер ВЗАГАЛІ НЕ ВІДПРАВЛЯЄ основний DELETE-запит",
                 size=9, min_w=390, fill="#fdecea", stroke=POS)
    frags.append(b2[0])

    frags.append(text(W / 2, 498, "Preflight захищає застарілі бекенди від неочікуваних мутацій, тоді як прості запити виконуються негайно",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cors-flow.svg"), W, H, *frags)


def fig_cors_security_boundaries():
    """Безпекові межі CORS: куки, Origin reflection та заголовок Vary."""
    W, H = 940, 480
    frags = []
    frags.append(text(W / 2, 28, "Безпекові пастки CORS: облікові дані, дзеркалення Origin та кеш",
                      size=16, bold=True))

    # ── Лівий блок: Пастка дзеркалення Origin
    frags.append(rect(40, 55, 420, 380, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(250, 82, "Небезпечний патерн: сліпе дзеркалення", size=13, bold=True, color=POS))

    box1 = textbox(250, 130, "Вхідний запит від зловмисника:\nOrigin: https://evil-attacker.com\nCookie: session_id=secret123",
                   size=10, min_w=380, fill="#fdecea", stroke=POS)
    frags.append(box1[0])

    box2 = textbox(250, 220, "Вразлива конфігурація сервера:\nACAO: req.headers['Origin'] (динамічно)\nAccess-Control-Allow-Credentials: true",
                   size=10, min_w=380, fill="#fdecea", stroke=POS)
    frags.append(box2[0])

    box3 = textbox(250, 320, "Катастрофічний наслідок:\nБудь-який сайт у світі може прочитати\nперсональні дані та приватні API жертви,\nповністю обійшовши захист SOP!",
                   size=10, min_w=380, fill="#fdecea", stroke=POS)
    frags.append(box3[0])

    frags.append(text(250, 405, "Сліпе копіювання Origin зводить безпеку нанівець", size=10, bold=True, color=POS))

    # ── Правий блок: Безпечна архітектура та кешування
    frags.append(rect(480, 55, 420, 380, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(690, 82, "Безпечний патерн: білий список і Vary", size=13, bold=True, color=FIELD))

    box4 = textbox(690, 130, "Сувора валідація білого списку (Whitelist):\norigins = {'https://app.example.com', ...}\nПеревірка точного збігу FQDN та схеми",
                   size=10, min_w=380, fill="#eafaf1", stroke=FIELD)
    frags.append(box4[0])

    box5 = textbox(690, 220, "Заборона конфлікту * та Credentials:\nЯкщо потрібні Cookie/Auth-заголовки,\nзначення '*' суворо ЗАБОРОНЕНО специфікацією",
                   size=10, min_w=380, fill="#eafaf1", stroke=FIELD)
    frags.append(box5[0])

    box6 = textbox(690, 320, "Захист кешу через заголовок Vary: Origin:\nЗапобігає отруєнню спільних CDN/проксі кешів,\nде відповідь для сайту A могла б помилково\nвіддатися сайту B з чужим заголовком ACAO",
                   size=10, min_w=380, fill="#eafaf1", stroke=FIELD)
    frags.append(box6[0])

    frags.append(text(690, 405, "Vary: Origin є обов'язковим при динамічному ACAO", size=10, bold=True, color=FIELD))

    frags.append(text(W / 2, 458, "CORS — це не файрвол; заголовок Access-Control-Allow-Origin керує лише дозволом браузеру показати дані скрипту",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cors-security-boundaries.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_same_origin_tuple()
    fig_cors_flow()
    fig_cors_security_boundaries()
    print("Усі фігури для CORS успішно згенеровано.")
