# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_cookie_exchange():
    """Обмін HTTP-cookie: Set-Cookie у відповіді та Cookie у наступних запитах."""
    W, H = 940, 420
    frags = []
    frags.append(text(W / 2, 30, "Обмін HTTP-cookie: від заголовка відповіді до автоматичного повернення",
                      size=16, bold=True))

    # ── Клієнт (Браузер) ліворуч
    frags.append(rect(40, 70, 260, 310, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(170, 98, "Клієнт (Браузер)", size=14, bold=True))
    frags.append(text(170, 118, "Сховище cookie (Cookie Jar)", size=11, color=MUTED))

    c_box = rect(55, 140, 230, 95, fill=FILL, stroke=LINE, sw=1.2, rx=6)
    c_txt1 = text(170, 162, "Запис cookie:", size=11, bold=True, color=INK)
    c_txt2 = text(170, 182, "Ім'я: sid, Значення: k8d9...2a", size=10, color=INK)
    c_txt3 = text(170, 200, "Домен: example.com, Шлях: /", size=10, color=MUTED)
    c_txt4 = text(170, 218, "Secure, HttpOnly, SameSite=Lax", size=10, color=FIELD)
    frags += [c_box, c_txt1, c_txt2, c_txt3, c_txt4]

    c_note = textbox(170, 300, "Перевіряє атрибути перед\nкожним запитом і додає\nлише ім'я та значення",
                     size=11, min_w=230, fill="#f9fafb", stroke="#d1d5db")
    frags.append(c_note[0])

    # ── Сервер праворуч
    frags.append(rect(640, 70, 260, 310, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(770, 98, "Сервер (example.com)", size=14, bold=True))
    frags.append(text(770, 118, "Обробник запитів і сесій", size=11, color=MUTED))

    s_box = rect(655, 140, 230, 95, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6)
    s_txt1 = text(770, 165, "Автентифікація успішна", size=11, bold=True, color=FIELD)
    s_txt2 = text(770, 190, "Генерує sid = k8d9...2a", size=11, color=INK)
    s_txt3 = text(770, 212, "Формує директиви захисту", size=10, color=MUTED)
    frags += [s_box, s_txt1, s_txt2, s_txt3]

    s_note = textbox(770, 300, "Отримує лише sid=k8d9...2a;\nатрибути браузер назад\nніколи не відсилає",
                     size=11, min_w=230, fill="#f9fafb", stroke="#d1d5db")
    frags.append(s_note[0])

    # ── Стрілки обміну
    # 1. Запит входу
    frags.append(arrow(300, 105, 640, 105, color=MUTED, sw=1.5))
    frags.append(text(470, 95, "1. POST /login (пароль або токен)", size=11, color=MUTED))

    # 2. Відповідь із Set-Cookie
    frags.append(arrow(640, 160, 300, 160, color=FIELD, sw=2.2))
    frags.append(text(470, 150, "2. 200 OK + Set-Cookie: sid=k8d9...; Secure; HttpOnly; SameSite=Lax",
                      size=11, bold=True, color=FIELD))

    # 3. Наступний запит із Cookie
    frags.append(arrow(300, 255, 640, 255, color=INK, sw=2.2))
    frags.append(text(470, 245, "3. GET /profile + Cookie: sid=k8d9...2a (автоматично)",
                      size=11, bold=True, color=INK))

    # 4. Відповідь даних
    frags.append(arrow(640, 340, 300, 340, color=MUTED, sw=1.5))
    frags.append(text(470, 330, "4. 200 OK (дані профілю для користувача із сесії sid)", size=11, color=MUTED))

    frags.append(text(W / 2, 405, "Асиметрія: сервер задає всі атрибути, але браузер повертає тільки рядок «ім'я=значення»",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cookie-exchange.svg"), W, H, *frags)


def fig_samesite_modes():
    """Порівняння режимів SameSite: Strict, Lax та None для різних типів запитів."""
    W, H = 940, 390
    frags = []
    frags.append(text(W / 2, 30, "Поведінка атрибута SameSite при міжсайтових переходах",
                      size=16, bold=True))

    # Стовпці сценаріїв
    scenarios = [
        "Прямий перехід за лінком\n<a href='https://app.com'>\n(Top-level безпечний GET)",
        "Міжсайтова форма\n<form action='https://app.com/pay'\nmethod='POST'> (Мутація)",
        "Вбудований підресурс\n<img src='...'>, <iframe>,\nfetch() із чужого сайту"
    ]

    modes = [
        ("SameSite = Strict", "#c0392b", [("Блокується", False), ("Блокується", False), ("Блокується", False)]),
        ("SameSite = Lax (дефолт)", "#27ae60", [("Надсилається", True), ("Блокується", False), ("Блокується", False)]),
        ("SameSite = None (з Secure)", "#2457d6", [("Надсилається", True), ("Надсилається", True), ("Надсилається", True)])
    ]

    # Шапка таблиці
    frags.append(rect(40, 60, 220, 70, fill="#e5e7eb", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(150, 100, "Режим SameSite", size=13, bold=True))

    col_xs = [270, 490, 710]
    for idx, (title, cx) in enumerate(zip(scenarios, col_xs)):
        b, _, _ = textbox(cx + 105, 95, title, size=11, min_w=210, fill=FILL, stroke=LINE)
        frags.append(b)

    # Рядки
    row_ys = [155, 230, 305]
    for (m_title, m_color, m_results), ry in zip(modes, row_ys):
        # Заголовок режиму ліворуч
        frags.append(rect(40, ry - 25, 220, 58, fill=BG, stroke=LINE, sw=1.2, rx=6))
        frags.append(text(150, ry + 8, m_title, size=12, bold=True, color=m_color))

        # Комірки результатів
        for (res_text, is_sent), cx in zip(m_results, col_xs):
            bg_col = "#eafaf1" if is_sent else "#fdecea"
            brd_col = FIELD if is_sent else POS
            txt_col = FIELD if is_sent else POS
            sign = "✓ " if is_sent else "✗ "

            frags.append(rect(cx, ry - 25, 210, 58, fill=bg_col, stroke=brd_col, sw=1.2, rx=6))
            frags.append(text(cx + 105, ry + 8, sign + res_text, size=12, bold=True, color=txt_col))

    frags.append(text(W / 2, 375, "Lax захищає від CSRF у фоні та при POST-формах, але пропускає звичайний перехід користувача",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "samesite-modes.svg"), W, H, *frags)


def fig_cookie_scope_prefixes():
    """Область видимості cookie та захисні префікси __Host- і __Secure-."""
    W, H = 940, 410
    frags = []
    frags.append(text(W / 2, 30, "Межі видимості cookie та захист префіксами __Host- і __Secure-",
                      size=16, bold=True))

    # Верхній блок: Звичайна спадковість Domain vs Host-Only
    frags.append(rect(40, 65, 420, 280, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(250, 92, "Звичайні cookie: область дії Domain", size=13, bold=True))

    b1, _, _ = textbox(250, 138, "Без Domain (Host-Only):\nВидно ТІЛЬКИ на example.com\n(піддомени не мають доступу)",
                       size=11, min_w=390, fill="#eafaf1", stroke=FIELD)
    frags.append(b1)

    b2, _, _ = textbox(250, 215, "З Domain=example.com:\nВидно на example.com ТА ВСІХ піддоменах\n(api.example.com, blog.example.com)",
                       size=11, min_w=390, fill="#fdecea", stroke=POS)
    frags.append(b2)

    frags.append(text(250, 290, "Небезпека: зламаний піддомен може перетерти", size=10, color=POS, bold=True))
    frags.append(text(250, 308, "або нав'язати cookie для основного домену (cookie tossing)", size=10, color=POS))

    # Правий блок: Захисні префікси __Secure- та __Host-
    frags.append(rect(480, 65, 420, 280, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(690, 92, "Захищені префікси (RFC 6265bis)", size=13, bold=True))

    b3, _, _ = textbox(690, 140, "Префікс __Secure-name\n1. Вимагає обов'язкового прапорця Secure\n2. Приймається браузером ТІЛЬКИ через HTTPS",
                       size=11, min_w=390, fill=FILL, stroke=LINE)
    frags.append(b3)

    b4, _, _ = textbox(690, 235, "Префікс __Host-name (найсуворіший захист)\n1. Вимагає Secure + ТІЛЬКИ HTTPS\n2. ЗАБОРОНЯЄ атрибут Domain (тільки Host-Only!)\n3. Вимагає обов'язкового Path=/",
                       size=11, min_w=390, fill="#eafaf1", stroke=FIELD)
    frags.append(b4)

    frags.append(text(690, 315, "Жоден піддомен не зможе підмінити чи прочитати __Host- cookie",
                      size=10, color=FIELD, bold=True))

    frags.append(text(W / 2, 395, "Префікс __Host- гарантує, що cookie прив'язаний виключно до цього хоста та передається лише шифрованим каналом",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cookie-scope-prefixes.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_cookie_exchange()
    fig_samesite_modes()
    fig_cookie_scope_prefixes()
    print("Усі фігури згенеровано успішно.")
