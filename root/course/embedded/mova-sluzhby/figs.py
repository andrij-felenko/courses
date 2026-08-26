# -*- coding: utf-8 -*-
"""Фігури для статті mova-sluzhby («Мова служби: чому не C»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── silicon-vs-cloud: вододіл середовищ MCU проти сервера ────────────────────
def fig_silicon_vs_cloud():
    W, H = 840, 390
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Вододіл середовищ: кремній мікроконтролера проти сервера", size=15, bold=True))

    # Лівий блок: Мікроконтролер
    bx1, by1, bw1, bh1 = 30, 55, 360, 305
    p.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx1, by1, bw1, 36, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 23, "Кремній мікроконтролера (STM32 / ESP32)", size=13, bold=True, color=POS))

    mcu_items = [
        ("Пам'ять:", "32–512 КБ RAM, статичні пули, без MMU"),
        ("Виконання:", "Bare-metal або RTOS, прямі регістри"),
        ("Час:", "Жорсткий детермінізм такту (мікросекунди)"),
        ("Ввід-вивід:", "Переривання, DMA, апаратні шини SPI/I2C"),
        ("Головний ризик:", "Фрагментація купи, вичерпання стека"),
        ("Ідеальна мова:", "C / C++ (повний контроль кожного байта)")
    ]
    cur_y = by1 + 60
    for title, desc in mcu_items:
        p.append(text(bx1 + 16, cur_y, title, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(bx1 + 16, cur_y + 16, desc, size=11, color=MUTED, anchor="start"))
        cur_y += 38

    # Правий блок: Хмарний сервер
    bx2, by2, bw2, bh2 = 450, 55, 360, 305
    p.append(rect(bx2, by2, bw2, bh2, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx2, by2, bw2, 36, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 23, "Хмарний сервер (Linux / x86-64 / ARM64)", size=13, bold=True, color=NEG))

    server_items = [
        ("Пам'ять:", "16–256 ГБ віртуальної RAM, пейджинг MMU"),
        ("Виконання:", "Простір користувача, планувальник ядра ОС"),
        ("Час:", "Стохастичні затримки мережі (RTT 10–100 мс)"),
        ("Ввід-вивід:", "Сокети, epoll/kqueue, дисковий асинхрон"),
        ("Головний ризик:", "Вразливості пам'яті під зовнішнім трафіком"),
        ("Ідеальна мова:", "Go / Rust (Memory safety, M:N конкурентність)")
    ]
    cur_y = by2 + 60
    for title, desc in server_items:
        p.append(text(bx2 + 16, cur_y, title, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(bx2 + 16, cur_y + 16, desc, size=11, color=MUTED, anchor="start"))
        cur_y += 38

    # Центральний роздільник
    p.append(line(420, 70, 420, 345, color=MUTED, sw=1.5, dash="4 4"))
    b_vs, _, _ = textbox(420, 207, "VS", size=12, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)
    p.append(b_vs)

    render(os.path.join(OUT, "silicon-vs-cloud.svg"), W, H, *p)


# ── concurrency-scaling: моделі паралелізму на 100 000 з'єднань ──────────────
def fig_concurrency_scaling():
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 28, "Масштабування 100 000 одночасних підключень: витрати ресурсів", size=15, bold=True))

    col_w = 245
    gap = 25
    x_start = 30
    card_h = 305
    top_y = 55

    # Варіант 1: Потік на з'єднання (C / pthread)
    x1 = x_start
    p.append(rect(x1, top_y, col_w, card_h, fill="#fff5f5", stroke=POS, sw=1.4, rx=6))
    p.append(rect(x1, top_y, col_w, 36, fill="#fed7d7", stroke=POS, sw=1.0, rx=6))
    p.append(text(x1 + col_w / 2, top_y + 23, "1. Потік на запит (C / pthread)", size=12, bold=True, color=POS))

    c_stats = [
        ("Стек на клієнта:", "2–8 МБ (потік ядра Linux)"),
        ("Пам'ять на 100k:", "200–800 ГБ RAM"),
        ("Перемикання:", "Ядро ОС (1–2 мкс на зміну)"),
        ("Поведінка ядра:", "Context switch thrashing"),
        ("Втрати CPU:", "До 80% часу на планування"),
        ("Висновок:", "Не масштабується для IoT")
    ]
    cur_y = top_y + 58
    for title, desc in c_stats:
        p.append(text(x1 + 12, cur_y, title, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(x1 + 12, cur_y + 15, desc, size=10.5, color=MUTED, anchor="start"))
        cur_y += 39

    # Варіант 2: Однопотоковий Event Loop (Node.js / Python)
    x2 = x1 + col_w + gap
    p.append(rect(x2, top_y, col_w, card_h, fill="#fefcbf", stroke="#b7791f", sw=1.4, rx=6))
    p.append(rect(x2, top_y, col_w, 36, fill="#fef08a", stroke="#b7791f", sw=1.0, rx=6))
    p.append(text(x2 + col_w / 2, top_y + 23, "2. Event Loop (Node / Python)", size=12, bold=True, color="#975a16"))

    node_stats = [
        ("Стек на клієнта:", "1 спільний стек + черга подій"),
        ("Пам'ять на 100k:", "~1.5–3.0 ГБ RAM"),
        ("Перемикання:", "Користувацький цикл подій"),
        ("Поведінка ядра:", "epoll / kqueue мультиплексування"),
        ("Втрати CPU:", "Блокування одного гальмує всіх"),
        ("Висновок:", "Чутливий до обчислень / GIL")
    ]
    cur_y = top_y + 58
    for title, desc in node_stats:
        p.append(text(x2 + 12, cur_y, title, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(x2 + 12, cur_y + 15, desc, size=10.5, color=MUTED, anchor="start"))
        cur_y += 39

    # Варіант 3: M:N Горутини / Асинхронність (Go / Rust)
    x3 = x2 + col_w + gap
    p.append(rect(x3, top_y, col_w, card_h, fill="#f0fff4", stroke=FIELD, sw=1.4, rx=6))
    p.append(rect(x3, top_y, col_w, 36, fill="#c6f6d5", stroke=FIELD, sw=1.0, rx=6))
    p.append(text(x3 + col_w / 2, top_y + 23, "3. M:N Горутини (Go / Rust Tokio)", size=12, bold=True, color=FIELD))

    go_stats = [
        ("Стек на клієнта:", "2–4 КБ (динамічний стек)"),
        ("Пам'ять на 100k:", "~250–450 МБ RAM"),
        ("Перемикання:", "Користувацький рантайм (M:N)"),
        ("Поведінка ядра:", "Netpoller поверх epoll у фоні"),
        ("Втрати CPU:", "Мінімальні (< 3% на планування)"),
        ("Висновок:", "Ідеально для 100k+ MQTT сесій")
    ]
    cur_y = top_y + 58
    for title, desc in go_stats:
        p.append(text(x3 + 12, cur_y, title, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(x3 + 12, cur_y + 15, desc, size=10.5, color=MUTED, anchor="start"))
        cur_y += 39

    render(os.path.join(OUT, "concurrency-scaling.svg"), W, H, *p)


# ── firmware-backend-pattern: розподіл обов'язків ────────────────────────────
def fig_firmware_backend_pattern():
    W, H = 840, 360
    p = []

    p.append(text(W / 2, 28, "Архітектурний розподіл зон відповідальності в IoT", size=15, bold=True))

    # Лівий блок: Прошивка на пристрої
    bx1, by1, bw1, bh1 = 30, 60, 240, 260
    p.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    p.append(rect(bx1, by1, bw1, 34, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 22, "Вузол (C / C++)", size=12.5, bold=True, color=POS))

    fw_lines = [
        "• Опитування АЦП та I2C/SPI",
        "• Фільтрація шумів датчиків",
        "• Контроль живлення та сон",
        "• Формування бінарного кадру",
        "• Фіксована пам'ять (RAM < 64 КБ)"
    ]
    cur_y = by1 + 58
    for l in fw_lines:
        p.append(text(bx1 + 12, cur_y, l, size=11, color=INK, anchor="start"))
        cur_y += 36

    # Середній блок: Транспорт
    bx2, by2, bw2, bh2 = 310, 110, 220, 160
    p.append(rect(bx2, by2, bw2, bh2, fill="#edf2f7", stroke=LINE, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 25, "Транспортний протокол", size=12, bold=True, color=INK))

    trans_lines = [
        "MQTT / TLS 1.3 або HTTP POST",
        "Компактний payload (CBOR / JSON)",
        "Автентифікація пристрою (mTLS)"
    ]
    cur_y = by2 + 55
    for l in trans_lines:
        p.append(text(bx2 + bw2 / 2, cur_y, l, size=10.5, color=MUTED))
        cur_y += 26

    # Стрілка від вузла до транспорту
    p.append(arrow(bx1 + bw1, 190, bx2, 190, color=LINE, sw=1.8))
    # Стрілка від транспорту до бекенду
    p.append(arrow(bx2 + bw2, 190, 570, 190, color=LINE, sw=1.8))

    # Правий блок: Хмарна служба
    bx3, by3, bw3, bh3 = 570, 60, 240, 260
    p.append(rect(bx3, by3, bw3, bh3, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    p.append(rect(bx3, by3, bw3, 34, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=6))
    p.append(text(bx3 + bw3 / 2, by3 + 22, "Служба (Go / Rust)", size=12.5, bold=True, color=FIELD))

    srv_lines = [
        "• Термінація TLS та безпека",
        "• Декодування та валідація JSON",
        "• Збереження у Time-Series DB",
        "• Сповіщення та бізнес-правила",
        "• 100k+ паралельних з'єднань"
    ]
    cur_y = by3 + 58
    for l in srv_lines:
        p.append(text(bx3 + 12, cur_y, l, size=11, color=INK, anchor="start"))
        cur_y += 36

    render(os.path.join(OUT, "firmware-backend-pattern.svg"), W, H, *p)


if __name__ == "__main__":
    fig_silicon_vs_cloud()
    fig_concurrency_scaling()
    fig_firmware_backend_pattern()
    print("Фігури успішно згенеровано.")
