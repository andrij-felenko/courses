# -*- coding: utf-8 -*-
"""Фігури до теми «Веб-сервер на МК».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"   # тепле виділення


# ── 1. Суть: МК сам віддає сторінку браузерові ────────────────────────────────
# Ідея: телефон/браузер шле HTTP-запит по Wi-Fi; МК сам збирає відповідь і віддає.
# Жодного зовнішнього сервера в інтернеті — пристрій і є сервер.
def fig_idea():
    W, H = 760, 280
    f = [text(W / 2, 26, "Веб-сервер на МК: пристрій сам віддає сторінку", size=15, bold=True)]

    by, bh = 92, 96
    # клієнт — браузер/телефон
    cx, cw = 50, 232
    f.append(rect(cx, by, cw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(cx + cw / 2, by + 26, "БРАУЗЕР / ТЕЛЕФОН", size=12, color=NEG, bold=True))
    f.append(mtext(cx + cw / 2, by + 52, ["вводиш 192.168.4.1", "клікаєш кнопки"], size=10, color=INK))

    # сервер — сам МК
    sx, sw = 478, 232
    f.append(rect(sx, by, sw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(sx + sw / 2, by + 26, "МІКРОКОНТРОЛЕР", size=12, color=FIELD, bold=True))
    f.append(mtext(sx + sw / 2, by + 52, ["ESP32 = і пристрій,", "і веб-сервер водночас"], size=10, color=INK))

    midy = by + bh / 2
    f.append(arrow(cx + cw + 4, midy - 13, sx - 4, midy - 13, color=AMBER, sw=2.2))
    f.append(text((cx + cw + sx) / 2, midy - 19, "HTTP-запит: GET /", size=9.5, color=AMBER, bold=True))
    f.append(arrow(sx - 4, midy + 15, cx + cw + 4, midy + 15, color=POS, sw=2.2))
    f.append(text((cx + cw + sx) / 2, midy + 33, "відповідь: HTML / JSON", size=9.5, color=POS, bold=True))

    f.append(text(W / 2, H - 14,
                  "жодного сервера в інтернеті — сам пристрій і є сервер",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ── 2. Шлях одного запиту крізь сервер ────────────────────────────────────────
# Ідея: запит приходить у сокет → сервер читає рядок «GET /led» → шукає в таблиці
# хендлер за шляхом → хендлер виконується й пише відповідь назад у сокет.
def fig_request():
    W, H = 760, 300
    f = [text(W / 2, 26, "Шлях одного запиту крізь сервер", size=15, bold=True)]

    steps = [
        ("1", "запит у сокет\nGET /led", NEG),
        ("2", "сервер читає\nметод і шлях", AMBER),
        ("3", "шукає в таблиці\nхендлер /led", FIELD),
        ("4", "хендлер виконав\nі зібрав текст", FIELD),
        ("5", "відповідь назад\nу той самий сокет", POS),
    ]
    n = len(steps)
    cw, gap = 122, 19
    x = (W - (cw * n + gap * (n - 1))) / 2
    cy, ch = 84, 128
    prev = None
    for num, label, col in steps:
        f.append(rect(x, cy, cw, ch, fill="#fbfbfb", stroke=col, sw=1.8, rx=12))
        f.append(circle(x + cw / 2, cy + 28, 15, fill="#fbfbfb", stroke=col, sw=2))
        f.append(text(x + cw / 2, cy + 33, num, size=13, color=col, bold=True))
        f.append(mtext(x + cw / 2, cy + 66, label.split("\n"), size=9.6, color=INK))
        if prev is not None:
            f.append(arrow(prev, cy + ch / 2, x - 4, cy + ch / 2, color=INK, sw=1.6))
        prev = x + cw
        x += cw + gap

    f.append(text(W / 2, H - 14,
                  "сервер — це петля «прийми запит → знайди хендлер → віддай відповідь»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "request.svg"), W, H, *f)


# ── 3. Таблиця маршрутів: шлях → хендлер ──────────────────────────────────────
# Ідея: сервер тримає список «(метод, шлях) → функція»; за збігом кличе свою.
def fig_routes():
    W, H = 760, 300
    f = [text(W / 2, 26, "Таблиця маршрутів: за шляхом — своя функція", size=15, bold=True)]

    rows = [
        ("GET  /", "віддати головну HTML-сторінку", FIELD),
        ("GET  /state", "зібрати показання → віддати JSON", NEG),
        ("POST /led", "прочитати тіло → перемкнути світлодіод", AMBER),
    ]
    kx, kw = 56, 180
    dx, dw = kx + kw + 26, 442
    y = 64
    for key, note, col in rows:
        f.append(rect(kx, y, kw, 54, fill="#1b1f24", stroke=col, sw=1.8, rx=9))
        f.append(text(kx + kw / 2, y + 32, key, size=12.5, color="#cfe8cf", bold=True))
        f.append(arrow(kx + kw + 4, y + 27, dx - 4, y + 27, color=INK, sw=1.6))
        f.append(fitbox(dx, y, dw, 54, note, size=11, color=INK, fill="#f7f7f7", stroke=col, sw=1.2, rx=9))
        y += 70

    f.append(text(W / 2, H - 12,
                  "один шлях = один URI-хендлер; решта шляхів дають 404",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "routes.svg"), W, H, *f)


# ── 4. Дві ролі відповіді: статика з файлів і живий JSON ──────────────────────
# Ідея: «обличчя» (HTML/CSS/JS) лежить готовим у файловій системі й віддається як є;
# «дані» (показання) збираються на льоту в JSON під кожен запит.
def fig_static_json():
    W, H = 760, 300
    f = [text(W / 2, 26, "Дві ролі відповіді: статика й живі дані", size=15, bold=True)]

    lx, lw = 40, 330
    rx, rw = 410, 330
    by, bh = 60, 196
    f.append(rect(lx, by, lw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, by + 26, "СТАТИКА — обличчя", size=12, color=FIELD, bold=True))
    for i, s in enumerate(["• HTML, CSS, картинки, скрипт",
                           "• лежать готовими у файловій",
                           "  системі (SPIFFS / LittleFS)",
                           "• віддаються байт-у-байт як є",
                           "• не змінюються від запиту"]):
        f.append(text(lx + 16, by + 56 + i * 28, s, size=10.2, color=INK, anchor="start"))

    f.append(rect(rx, by, rw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(rx + rw / 2, by + 26, "ДАНІ — живий JSON", size=12, color=NEG, bold=True))
    for i, s in enumerate(["• показання давачів, стани",
                           "• збираються на льоту під",
                           "  кожен запит до /state",
                           "• щоразу свіже число",
                           '• {"temp":24.3,"led":true}']):
        f.append(text(rx + 16, by + 56 + i * 28, s, size=10.2, color=INK, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "обличчя готове наперед; дані народжуються щоразу заново",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "static-json.svg"), W, H, *f)


# ── 5. Межі: де веб-сервер на МК доречний, а де ні ────────────────────────────
# Ідея: дві колонки — для чого МК-сервер створений (локальне, кілька клієнтів)
# і де він пасує (публічний хостинг, тисячі з'єднань).
def fig_limits():
    W, H = 760, 318
    f = [text(W / 2, 26, "Межі: для чого МК-сервер, а для чого ні", size=15, bold=True)]

    lx, lw = 40, 330
    rx, rw = 410, 330
    by, bh = 60, 210
    f.append(rect(lx, by, lw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, by + 26, "Для цього він і є", size=12, color=FIELD, bold=True))
    for i, s in enumerate(["• портал налаштування Wi-Fi",
                           "• керування пристроєм із телефона",
                           "• моніторинг показань у браузері",
                           "• усе локально, кілька клієнтів",
                           "• без окремого застосунку"]):
        f.append(text(lx + 16, by + 56 + i * 32, s, size=10.2, color=INK, anchor="start"))

    f.append(rect(rx, by, rw, bh, fill="#fbfbfb", stroke=POS, sw=1.8, rx=10))
    f.append(text(rx + rw / 2, by + 26, "Не для цього", size=12, color=POS, bold=True))
    for i, s in enumerate(["• публічний хостинг сайту в інтернет",
                           "• тисячі одночасних з'єднань",
                           "• важкі сторінки й великий трафік",
                           "• мало пам'яті — кілька сокетів",
                           "• HTTPS дається тяжко"]):
        f.append(text(rx + 16, by + 56 + i * 32, s, size=10.2, color=INK, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "це локальний пульт пристрою, а не майданчик для світу",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "limits.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_request()
    fig_routes()
    fig_static_json()
    fig_limits()
    print("OK: 5 figures ->", IMG)
