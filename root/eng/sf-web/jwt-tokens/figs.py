# -*- coding: utf-8 -*-
"""Фігури до теми «JWT і сесії без стану».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"


# ── 1. Будова JWT: три частини через крапку ───────────────────────────────────
# Ідея: заголовок і навантаження — відкритий base64url-JSON; підпис рахують
# від них двох разом із таємним ключем.
def fig_anatomy():
    W, H = 960, 412
    f = [text(W / 2, 30, "Будова JWT: заголовок · навантаження · підпис", size=16, bold=True)]

    # --- рядок токена: три кольорові шматки через крапку ---
    ytop = 58
    chunks = [
        (40,  262, "eyJhbGciOiJIUzI1Ni…", "ЗАГОЛОВОК", FIELD, "#eef7f0"),
        (326, 222, "eyJzdWIiOiI0Mi…",     "НАВАНТАЖЕННЯ", NEG, "#eef2fb"),
        (580, 336, "3Vk8pR2mF1n7hQ4w…",   "ПІДПИС",    POS,   "#fdecea"),
    ]
    for x, w, body, lbl, col, fill in chunks:
        f.append(text(x + w / 2, ytop, lbl, size=11, color=col, bold=True))
        f.append(rect(x, ytop + 12, w, 40, fill=fill, stroke=col, sw=1.9, rx=8))
        f.append(text(x + w / 2, ytop + 38, body, size=12.5, color=INK))
    # крапки-роздільники між шматками
    f.append(text(311, ytop + 42, ".", size=26, color=MUTED, bold=True))
    f.append(text(565, ytop + 42, ".", size=26, color=MUTED, bold=True))

    # --- розкодовані панелі ---
    ydec = 148
    f.append(fitbox(40, ydec, 262, 82,
                    '{ "alg": "HS256",\n  "typ": "JWT" }',
                    size=13, fill="#f6fbf7", stroke=FIELD, sw=1.5))
    f.append(text(40 + 131, ydec + 100, "читається без ключа", size=10.5, color=MUTED, italic=True))

    f.append(fitbox(326, ydec, 302, 82,
                    '{ "sub": "42",\n  "role": "admin",\n  "exp": 1735732800 }',
                    size=13, fill="#f4f7fe", stroke=NEG, sw=1.5))
    f.append(text(326 + 151, ydec + 100, "теж читається без ключа — таємниць сюди не кладуть",
                  size=10.5, color=MUTED, italic=True))

    f.append(fitbox(662, ydec, 254, 82,
                    "тег, а не шифр:\nзмінити вміст можна,\nпідробити тег — ні",
                    size=12, fill="#fdf0ee", stroke=POS, sw=1.5, color=INK))

    # --- формула підпису внизу + стрілка вгору до шматка «ПІДПИС» ---
    fx, fy, fw, fh = 150, 322, 640, 52
    f.append(rect(fx, fy, fw, fh, fill="#fffdf6", stroke=AMBER, sw=1.8, rx=10))
    f.append(text(fx + fw / 2, fy + 21, "підпис = HMAC-SHA256( заголовок . навантаження ,  🔑 таємний ключ )",
                  size=13, color=INK, bold=True))
    f.append(text(fx + fw / 2, fy + 40, "той самий ключ рахує тег і перевіряє його — без ключа тега не буде",
                  size=10.5, color=MUTED, italic=True))
    # стрілка від формули вгору до шматка «ПІДПИС»
    f.append(arrow(748, fy, 748, ytop + 54, color=AMBER, sw=1.8))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Перевірка ловить підробку ──────────────────────────────────────────────
# Ідея: сервер перераховує тег від отриманого навантаження; змінене навантаження
# дає інший тег, старий підпис не пасує → відмова.
def fig_tamper():
    W, H = 900, 432
    f = [text(W / 2, 30, "Перевірка ловить підробку", size=16, bold=True)]

    # --- зловмисник ліворуч ---
    ax = 30
    f.append(rect(ax, 70, 250, 130, fill="#fdf0ee", stroke=POS, sw=1.7, rx=10))
    f.append(text(ax + 125, 96, "зловмисник", size=12.5, color=POS, bold=True))
    f.append(text(ax + 125, 122, 'role: "user" → "admin"', size=12, color=INK))
    f.append(text(ax + 125, 146, "підпис лишив старий", size=11, color=MUTED, italic=True))
    f.append(text(ax + 125, 170, "(ключа він не має)", size=11, color=MUTED, italic=True))

    # надісланий токен
    f.append(fitbox(ax + 6, 214, 238, 46,
                    'header . НОВИЙ payload . 3Vk8…',
                    size=11.5, fill=BG, stroke=GRAY, sw=1.4))
    f.append(text(ax + 125, 280, "надсилає серверу →", size=11, color=MUTED, italic=True))

    # --- сервер праворуч: перерахунок ---
    sx = 470
    f.append(rect(sx, 70, 400, 210, fill="#f6fbf7", stroke=FIELD, sw=1.7, rx=12))
    f.append(text(sx + 200, 96, "сервер перераховує тег своїм ключем", size=12.5, color=FIELD, bold=True))

    f.append(fitbox(sx + 24, 116, 352, 40,
                    "тег у токені (від старого payload):   3Vk8pR2mF1n7hQ4w…",
                    size=11.5, fill=BG, stroke=GRAY, sw=1.3, color=INK))
    f.append(fitbox(sx + 24, 168, 352, 40,
                    "очікуваний (від НОВОГО payload):    9Ht0aQ7cX2dLmR5p…",
                    size=11.5, fill=BG, stroke=NEG, sw=1.3, color=INK))
    f.append(text(sx + 200, 240, "3Vk8… ≠ 9Ht0…   —   теги різні", size=13, color=POS, bold=True))

    # стрілка зловмисник → сервер
    f.append(arrow(ax + 250, 237, sx - 6, 175, color=GRAY, sw=1.7))

    # --- підсумок: відмова ---
    f.append(rect(sx + 60, 316, 280, 62, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(sx + 200, 342, "401 — токен відхилено", size=14, color=POS, bold=True))
    f.append(text(sx + 200, 364, "сервер нічого про токен не пам'ятав", size=10.5, color=MUTED, italic=True))
    f.append(arrow(sx + 200, 284, sx + 200, 314, color=POS, sw=1.9))

    render(os.path.join(IMG, "tamper.svg"), W, H, *f)


# ── 3. Становий проти безстанового: ціна вибору ───────────────────────────────
# Ідея: сесія тримає стан у спільному сховищі (дорожче вшир, зате гаситься миттєво);
# JWT стану на гарячому шляху не тримає (масштаб дешевий, зате відкликати наперед нема як).
def fig_stateful_stateless():
    W, H = 920, 440
    f = [text(W / 2, 30, "Дві ціни одного вибору", size=16, bold=True)]

    # ── лівий бік: становий ──
    lx = 24
    f.append(rect(lx, 52, 430, 356, fill="#fffdf6", stroke=AMBER, sw=1.7, rx=12))
    f.append(text(lx + 215, 76, "серверна сесія — стан на сервері", size=13, color=AMBER, bold=True))

    # клієнт із номерком
    f.append(rect(lx + 24, 120, 96, 60, fill="#fbfbfb", stroke=INK, sw=1.6, rx=8))
    f.append(text(lx + 72, 146, "клієнт", size=11.5, color=INK, bold=True))
    f.append(text(lx + 72, 167, "номерок", size=10.5, color=MUTED, italic=True))

    # сервер
    f.append(rect(lx + 168, 120, 110, 60, fill="#eef2fb", stroke=NEG, sw=1.6, rx=9))
    f.append(text(lx + 223, 154, "сервер", size=12, color=NEG, bold=True))

    # спільне сховище сесій
    f.append(rect(lx + 314, 112, 96, 76, fill="#f0f2f5", stroke=INK, sw=1.6, rx=9))
    f.append(text(lx + 362, 140, "спільне", size=11, color=INK, bold=True))
    f.append(text(lx + 362, 160, "сховище", size=11, color=INK, bold=True))
    f.append(text(lx + 362, 178, "сесій", size=11, color=INK, bold=True))

    f.append(arrow(lx + 120, 150, lx + 166, 150, color=GRAY, sw=1.6))
    f.append(arrow(lx + 278, 150, lx + 312, 150, color=GRAY, sw=1.6))
    f.append(text(lx + 215, 210, "кожен запит — пошук у сховищі", size=10.5, color=MUTED, italic=True))

    # плата й виграш
    f.append(fitbox(lx + 24, 244, 384, 44,
                    "− масштаб вшир: сховище треба ділити на всі сервери",
                    size=12, fill="#fdf0ee", stroke=POS, sw=1.4, color=INK))
    f.append(fitbox(lx + 24, 300, 384, 44,
                    "+ погасити сесію: стерти запис — миттєво",
                    size=12, fill="#f6fbf7", stroke=FIELD, sw=1.4, color=INK))
    f.append(text(lx + 215, 372, "✓ вигнати користувача одразу", size=11.5, color=FIELD, bold=True))

    # ── правий бік: без стану ──
    rx = 476
    f.append(rect(rx, 52, 420, 356, fill="#f6fbf7", stroke=FIELD, sw=1.7, rx=12))
    f.append(text(rx + 210, 76, "JWT — стану на гарячому шляху немає", size=13, color=FIELD, bold=True))

    # клієнт із токеном
    f.append(rect(rx + 20, 116, 104, 66, fill="#fbfbfb", stroke=INK, sw=1.6, rx=8))
    f.append(text(rx + 72, 142, "клієнт", size=11.5, color=INK, bold=True))
    f.append(text(rx + 72, 164, "+ токен", size=10.5, color=FIELD, bold=True))

    # три однакові сервери, кожен перевіряє сам
    for i, y in enumerate((104, 158, 212)):
        f.append(rect(rx + 200, y, 140, 44, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=9))
        f.append(text(rx + 270, y + 27, "сервер %d" % (i + 1), size=11.5, color=INK, bold=True))
        f.append(arrow(rx + 124, 152, rx + 198, y + 22, color=FIELD, sw=1.5))
        f.append(text(rx + 352, y + 27, "✓", size=15, color=FIELD, bold=True))
    f.append(text(rx + 210, 250, "перевіряє підпис ключем — без сховища", size=10.5, color=MUTED, italic=True))

    # плата й виграш
    f.append(fitbox(rx + 18, 274, 384, 40,
                    "+ масштаб вшир: будь-який сервер обслужить будь-кого",
                    size=12, fill="#f6fbf7", stroke=FIELD, sw=1.4, color=INK))
    f.append(fitbox(rx + 18, 322, 384, 40,
                    "− відкликати наперед виданий токен — нема як",
                    size=12, fill="#fdf0ee", stroke=POS, sw=1.4, color=INK))
    f.append(text(rx + 210, 386, "чекай, поки exp сам протухне", size=11.5, color=POS, bold=True))

    render(os.path.join(IMG, "stateful-stateless.svg"), W, H, *f)


# ── 4. Хроніка: від першого чорновика до найкращих практик ────────────────────
# Ідея історії: вразливості McLean (31 бер. 2015) з'явилися РАНІШЕ, ніж стандарт
# став остаточним (трав. 2015) — бібліотеки ламали ще недописану специфікацію.
def fig_timeline():
    W, H = 1080, 384
    f = [text(W / 2, 30, "Хроніка JWT: чорновик · застосування · вразливості · стандарт",
              size=16, bold=True)]

    base = 200                       # висота головної лінії часу
    x0, x1 = 46, 1034
    f.append(line(x0, base, x1, base, color=INK, sw=2.2))
    f.append(arrow(x1 - 2, base, x1 + 4, base, color=INK, sw=2.2))

    # (x, дата, назва, «above»?, колір крапки, колір рамки)
    nodes = [
        (95,  "груд. 2010",  "перший чорновик JWT\n(draft-jones-…-00)",           True,  INK,   GRAY),
        (270, "2012",        "OAuth 2.0\n(RFC 6749)",                              False, INK,   GRAY),
        (452, "лют. 2014",   "OpenID Connect 1.0\nID-токен — це JWT",              True,  INK,   NEG),
        (632, "31 бер. 2015","T. McLean:\nalg:none + RS256→HS256",                 False, POS,   POS),
        (812, "трав. 2015",  "сімейство JOSE + JWT\nRFC 7515–7520",                True,  FIELD, FIELD),
        (985, "лют. 2020",   "RFC 8725 / BCP 225\nнайкращі практики",              False, INK,   FIELD),
    ]
    for x, date, title, above, dot, box in nodes:
        f.append(circle(x, base, 6.5, fill=dot, stroke=dot, sw=1.5))
        if above:
            f.append(line(x, base - 6, x, 142, color=GRAY, sw=1.4))
            f.append(text(x, 128, date, size=12, color=INK, bold=True))
            f.append(fitbox(x - 84, 60, 168, 52, title, size=11.5,
                            fill=BG, stroke=box, sw=1.6, color=INK))
        else:
            f.append(line(x, base + 6, x, 258, color=GRAY, sw=1.4))
            f.append(text(x, 278, date, size=12, color=INK, bold=True))
            f.append(fitbox(x - 84, 292, 168, 52, title, size=11.5,
                            fill=BG, stroke=box, sw=1.6, color=INK))

    # брекет «≈6 тижнів» між McLean і фінальними RFC
    by = 178
    f.append(line(632, by, 812, by, color=POS, sw=1.5, dash="4 3"))
    f.append(line(632, by, 632, base - 8, color=POS, sw=1.2, dash="4 3"))
    f.append(line(812, by, 812, base - 8, color=POS, sw=1.2, dash="4 3"))
    f.append(text(722, by - 8, "≈ 6 тижнів: бібліотеки ламали ще недописаний стандарт",
                  size=11, color=POS, italic=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── 5. Сімейство JOSE, а JWT — його застосування ──────────────────────────────
# Ідея: JWT не окремий винахід, а надбудова над JWS; усі спираються на словник
# алгоритмів JWA — саме там стандарт і завів фатальний «none».
def fig_jose_family():
    W, H = 980, 452
    f = [text(W / 2, 30, "Сімейство JOSE, а JWT — його застосування", size=16, bold=True)]

    # JWT — зірка нагорі, над JWS
    f.append(rect(120, 62, 264, 64, fill="#eef7f0", stroke=FIELD, sw=2, rx=11))
    f.append(text(252, 88, "JWT — веб-токен · RFC 7519", size=13, color=FIELD, bold=True))
    f.append(text(252, 110, "= JWS, чиє навантаження — JSON-твердження", size=10.5, color=MUTED, italic=True))

    # три члени сімейства
    members = [
        (150, "JWS", "RFC 7515", "підпис", NEG),
        (490, "JWE", "RFC 7516", "шифрування", AMBER),
        (730, "JWK", "RFC 7517", "ключі", INK),
    ]
    for cx, name, rfc, role, col in members:
        f.append(rect(cx - 100, 196, 200, 74, fill=BG, stroke=col, sw=1.8, rx=10))
        f.append(text(cx, 224, name, size=15, color=col, bold=True))
        f.append(text(cx, 246, rfc, size=11.5, color=INK))
        f.append(text(cx, 263, role, size=11, color=MUTED, italic=True))

    # стрілка JWT → JWS
    f.append(arrow(252, 126, 210, 194, color=FIELD, sw=1.9))
    f.append(text(300, 162, "підписане", size=10.5, color=MUTED, italic=True))
    f.append(text(300, 177, "навантаження", size=10.5, color=MUTED, italic=True))

    # база JWA під усіма трьома
    f.append(rect(50, 312, 760, 58, fill="#fffdf6", stroke=AMBER, sw=1.8, rx=11))
    f.append(text(430, 336, "JWA — спільний словник алгоритмів · RFC 7518", size=13, color=AMBER, bold=True))
    f.append(text(430, 356, "HS256 · RS256 · ES256 · … і фатальний «none»", size=11, color=INK))
    for cx in (150, 490, 730):
        f.append(arrow(cx, 312, cx, 272, color=AMBER, sw=1.5))

    # підпис-висновок
    f.append(text(430, 402, "усі шість — травень 2015; JWT не замінює JOSE, а стоїть на ньому",
                  size=12, color=MUTED, italic=True))
    f.append(text(430, 424, "«none» жив у самому реєстрі алгоритмів — звідти й вразливість",
                  size=11, color=POS, italic=True))

    render(os.path.join(IMG, "jose-family.svg"), W, H, *f)


# ── 6. Дві атаки, один замок: пінінг алгоритму ────────────────────────────────
# Ідея: обидві підробки (alg:none і плутанина RS256→HS256) націлені на те, щоб
# перевіряч узяв алгоритм із заголовка; перевіряч, що бере alg і ключ із конфігу,
# відкидає обидві на першому ж рядку.
def fig_two_attacks():
    W, H = 980, 486
    f = [text(W / 2, 30, "Дві атаки, один замок: алгоритм беруть із конфігу, не з токена",
              size=15, bold=True)]

    # ── ліва колонка: дві підроблені записки ──
    ax, ay, aw, ah = 26, 64, 356, 150
    f.append(rect(ax, ay, aw, ah, fill="#fdf0ee", stroke=POS, sw=1.8, rx=11))
    f.append(text(ax + aw / 2, ay + 24, "Атака 1 — alg: none", size=13, color=POS, bold=True))
    f.append(fitbox(ax + 16, ay + 36, aw - 32, 30, 'header = { "alg": "none" }',
                    size=12, fill=BG, stroke=GRAY, sw=1.3, color=INK))
    f.append(fitbox(ax + 16, ay + 72, aw - 32, 30, 'payload = { "role": "admin" }',
                    size=12, fill=BG, stroke=GRAY, sw=1.3, color=INK))
    f.append(fitbox(ax + 16, ay + 108, aw - 32, 30, "signature = (порожня)",
                    size=12, fill=BG, stroke=POS, sw=1.3, color=INK))

    bx, by, bw, bh = 26, 250, 356, 202
    f.append(rect(bx, by, bw, bh, fill="#fdf0ee", stroke=POS, sw=1.8, rx=11))
    f.append(text(bx + bw / 2, by + 24, "Атака 2 — плутанина RS256 → HS256", size=12.5, color=POS, bold=True))
    f.append(fitbox(bx + 16, by + 36, bw - 32, 30, 'header = { "alg": "HS256" }',
                    size=12, fill=BG, stroke=GRAY, sw=1.3, color=INK))
    f.append(fitbox(bx + 16, by + 72, bw - 32, 30, 'payload = { "role": "admin" }',
                    size=12, fill=BG, stroke=GRAY, sw=1.3, color=INK))
    f.append(fitbox(bx + 16, by + 108, bw - 32, 30, "signature = HMAC( відкритий ключ , msg )",
                    size=11.5, fill=BG, stroke=POS, sw=1.3, color=INK))
    f.append(fitbox(bx + 16, by + 150, bw - 32, 34, "секрет = відкритий ключ,\nвін відомий усім",
                    size=11, fill="#fbeae7", stroke=POS, sw=1.2, color=MUTED))

    # ── центр: замок (пінінг) ──
    gx, gy, gw, gh = 452, 92, 218, 316
    f.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=13))
    f.append(text(gx + gw / 2, gy + 28, "перевіряч: пінінг", size=13, color=FIELD, bold=True))
    f.append(fitbox(gx + 14, gy + 44, gw - 28, 52, "очікуваний alg —\nіз КОНФІГУ (напр. HS256)",
                    size=11, fill=BG, stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(gx + 14, gy + 106, gw - 28, 52, "ключ — теж із конфігу,\nа не з токена",
                    size=11, fill=BG, stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(gx + 14, gy + 168, gw - 28, 52, "alg із заголовка\nІГНОРУЄМО",
                    size=11, fill=BG, stroke=FIELD, sw=1.3, color=INK))
    f.append(fitbox(gx + 14, gy + 230, gw - 28, 52, "звірка підпису —\nсталого часу",
                    size=11, fill=BG, stroke=FIELD, sw=1.3, color=INK))

    # стрілки атак у замок
    f.append(arrow(ax + aw, ay + ah / 2, gx - 4, gy + 70, color=POS, sw=1.9))
    f.append(arrow(bx + bw, by + 100, gx - 4, gy + 244, color=POS, sw=1.9))

    # ── праворуч: дві відмови ──
    rxx = 736
    f.append(rect(rxx, 118, 218, 96, fill="#fdecea", stroke=POS, sw=1.9, rx=11))
    f.append(text(rxx + 109, 148, "alg ≠ очікуваний", size=12.5, color=POS, bold=True))
    f.append(text(rxx + 109, 170, "«none» — не HS256", size=11, color=INK))
    f.append(text(rxx + 109, 196, "✗ 401 — відхилено", size=12.5, color=POS, bold=True))
    f.append(arrow(gx + gw, gy + 70, rxx - 4, 166, color=FIELD, sw=1.9))

    f.append(rect(rxx, 288, 218, 118, fill="#fdecea", stroke=POS, sw=1.9, rx=11))
    f.append(text(rxx + 109, 316, "HS256 ≠ очікуваний", size=11.5, color=POS, bold=True))
    f.append(text(rxx + 109, 336, "або: наш секрет", size=11, color=INK))
    f.append(text(rxx + 109, 356, "≠ відкритий ключ", size=11, color=INK))
    f.append(text(rxx + 109, 382, "✗ 401 — відхилено", size=12.5, color=POS, bold=True))
    f.append(arrow(gx + gw, gy + 244, rxx - 4, 344, color=FIELD, sw=1.9))

    render(os.path.join(IMG, "two-attacks.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_tamper()
    fig_stateful_stateless()
    fig_timeline()
    fig_jose_family()
    fig_two_attacks()
    print("OK: 6 фігур у", IMG)
