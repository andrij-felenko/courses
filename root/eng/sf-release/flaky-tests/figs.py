# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#fdecea"
COLD = "#eef4ff"
GRN  = "#eafaf1"
WARN = "#fff8e1"
PURP = "#f3e8ff"


# ── Фігура 1: Зростання ймовірності збою тестового набору ────────────────────
def fig_flaky_probability_growth():
    W, H = 1080, 500
    frags = []

    frags.append(text(W / 2, 32, "Вплив миготливих тестів на стабільність тестового набору в CI", size=17, bold=True))

    PW, PH = 490, 410
    PY = 60

    # Панель 1: Математична крива ймовірності
    p1_x = 35
    frags.append(rect(p1_x, PY, PW, PH, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(p1_x + PW / 2, PY + 26, "Імовірність хибного збою набору: P(збій) = 1 - (1 - p)ᴺ", size=14, bold=True))
    frags.append(line(p1_x + 20, PY + 40, p1_x + PW - 20, PY + 40, color=MUTED, sw=1))

    # Вісь графіка
    gx, gy, gw, gh = p1_x + 65, PY + 330, 390, 240
    frags.append(line(gx, gy, gx + gw, gy, color=LINE, sw=1.5))
    frags.append(line(gx, gy, gx, gy - gh, color=LINE, sw=1.5))

    # Підписи осей
    frags.append(text(gx + gw / 2, gy + 32, "Кількість тестів у наборі (N)", size=11, bold=True))
    frags.append(text(gx - 35, gy - gh / 2, "P(збій)", size=11, bold=True, anchor="middle"))

    # Позначки осі Y
    for pct, y_offset in [(0, 0), (25, 60), (50, 120), (75, 180), (100, 240)]:
        y_pos = gy - y_offset
        frags.append(line(gx - 5, y_pos, gx, y_pos, color=MUTED, sw=1))
        frags.append(text(gx - 10, y_pos + 4, f"{pct}%", size=10, color=MUTED, anchor="end"))
        if pct > 0:
            frags.append(line(gx, y_pos, gx + gw, y_pos, color="#e5e7eb", sw=1, dash="3 3"))

    # Позначки осі X
    for n_val, x_offset in [(0, 0), (100, 78), (200, 156), (300, 234), (400, 312), (500, 390)]:
        x_pos = gx + x_offset
        frags.append(line(x_pos, gy, x_pos, gy + 5, color=MUTED, sw=1))
        frags.append(text(x_pos, gy + 18, str(n_val), size=10, color=MUTED))

    # Криві для різних значень p
    # p = 1.0% (червона)
    pts_p10 = []
    for n in range(0, 501, 20):
        val = 1.0 - (1.0 - 0.01) ** n
        pts_p10.append(f"{gx + n * 0.78:.1f},{gy - val * 240:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_p10)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # p = 0.5% (помаранчева)
    pts_p05 = []
    for n in range(0, 501, 20):
        val = 1.0 - (1.0 - 0.005) ** n
        pts_p05.append(f"{gx + n * 0.78:.1f},{gy - val * 240:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_p05)}" fill="none" stroke="#d97706" stroke-width="2"/>')

    # p = 0.1% (зелена)
    pts_p01 = []
    for n in range(0, 501, 20):
        val = 1.0 - (1.0 - 0.001) ** n
        pts_p01.append(f"{gx + n * 0.78:.1f},{gy - val * 240:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_p01)}" fill="none" stroke="{FIELD}" stroke-width="2"/>')

    # Легенда кривих
    frags.append(rect(p1_x + 220, PY + 55, 235, 75, fill="#fafafa", stroke=MUTED, sw=1, rx=4))
    frags.append(line(p1_x + 230, PY + 72, p1_x + 255, PY + 72, color=POS, sw=2.5))
    frags.append(text(p1_x + 265, PY + 76, "p = 1.0% (N=100 → 63.4% збоїв)", size=10, bold=True, anchor="start", color=POS))

    frags.append(line(p1_x + 230, PY + 92, p1_x + 255, PY + 92, color="#d97706", sw=2))
    frags.append(text(p1_x + 265, PY + 96, "p = 0.5% (N=100 → 39.4% збоїв)", size=10, bold=True, anchor="start", color="#d97706"))

    frags.append(line(p1_x + 230, PY + 112, p1_x + 255, PY + 112, color=FIELD, sw=2))
    frags.append(text(p1_x + 265, PY + 116, "p = 0.1% (N=500 → 39.3% збоїв)", size=10, bold=True, anchor="start", color=FIELD))

    # Панель 2: Наслідки для команди інженерів
    p2_x = 555
    frags.append(rect(p2_x, PY, PW, PH, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(p2_x + PW / 2, PY + 26, "Ефект знецінення та наслідки деградації CI", size=14, bold=True))
    frags.append(line(p2_x + 20, PY + 40, p2_x + PW - 20, PY + 40, color=MUTED, sw=1))

    stages = [
        ("Хибні спрацьовування", "1–2 миготливі тести руйнують стабільність усього пайплайну", WARN, "#d97706"),
        ("Ефект «Хлопчик і вовки»", "Інженери звикають до червоного CI і перезапускають без перевірки", HOT, POS),
        ("Пропуск справжніх регресій", "Реальні баги зливаються в реліз під виглядом чергового «флейка»", HOT, POS),
        ("Параліч розробки", "Час команди витрачається на ручні перезапуски та суперечки зі стендом", PURP, "#7c3aed")
    ]

    sy = PY + 60
    for title_s, desc_s, fill_c, strk_c in stages:
        frags.append(rect(p2_x + 25, sy, PW - 50, 70, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        frags.append(text(p2_x + 40, sy + 25, title_s, size=12, bold=True, color=strk_c, anchor="start"))
        frags.append(text(p2_x + 40, sy + 48, desc_s, size=10, color=INK, anchor="start"))
        sy += 85

    render(os.path.join(IMG, "flaky-probability-growth.svg"), W, H, *frags)


# ── Фігура 2: Джерела апаратного шуму та збоїв на HIL-стенді ─────────────────
def fig_hil_hardware_noise_sources():
    W, H = 1080, 560
    frags = []

    frags.append(text(W / 2, 32, "Фізичні першопричини нестабільності тестів на HIL-стендах", size=17, bold=True))

    cards = [
        (35, 65, 490, 225, "1. Брязкіт контактів реле (Contact Bounce)",
         ["Механічні контакти пружно вібрують 2–15 мс після замикання.",
          "Генерується пачка мікроімпульсів замість чистого фронту 0→1.",
          "Якщо тест зчитує GPIO у цьому вікні, результат випадковий.",
          "Лікування: апаратний RC-фільтр або програмний антибрязкіт."],
         WARN, "#d97706"),

        (555, 65, 490, 225, "2. Просідання напруги живлення (Voltage Sag)",
         ["Комутація реле чи моторів створює імпульсний струм до 2–5 А.",
          "Напруга живлення MCU короткочасно просідає нижче порогу BOR.",
          "Спричиняє спонтанний перезапуск MCU або збій вимірювань АЦП.",
          "Лікування: роздільні лінії живлення, блокувальні конденсатори."],
         HOT, POS),

        (35, 310, 490, 225, "3. Плаваючий логічний рівень (Floating Pin / Hi-Z)",
         ["Вхідний пін без підтяжки (Pull-Up/Down) ловить наведення 50 Гц.",
          "Потенціал коливається поблизу порогу перемикання тригера Шмітта.",
          "Тест бачить серію фальшивих спрацьовувань переривань.",
          "Лікування: жорсткі зовнішні резистори підтяжки 4.7–10 кОм."],
         COLD, NEG),

        (555, 310, 490, 225, "4. Переповнення буферів UART (Buffer Overflow)",
         ["Швидкість 115200 бод = 1 байт кожні 86.8 мкс.",
          "Тривале блокування переривань у RTOS (>5 мс) затирає кільцевий буфер.",
          "Тестовий фреймворк отримує битий JSON/ASCII-пакет телеметрії.",
          "Лікування: DMA-прийом, апаратний контроль потоку RTS/CTS."],
         PURP, "#7c3aed")
    ]

    for x, y, w, h, title_c, bullets, fill_c, strk_c in cards:
        frags.append(rect(x, y, w, h, fill=fill_c, stroke=strk_c, sw=1.5, rx=8))
        frags.append(text(x + 20, y + 30, title_c, size=13, bold=True, color=strk_c, anchor="start"))
        frags.append(line(x + 20, y + 44, x + w - 20, y + 44, color=strk_c, sw=1))

        by = y + 72
        for b in bullets:
            frags.append(circle(x + 30, by - 4, 3, fill=strk_c, stroke=strk_c))
            frags.append(text(x + 42, by, b, size=11, color=INK, anchor="start"))
            by += 36

    render(os.path.join(IMG, "hil-hardware-noise-sources.svg"), W, H, *frags)


# ── Фігура 3: Фіксована затримка sleep проти асинхронного опитування ─────────
def fig_async_polling_vs_sleep():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 32, "Порівняння підходів: фіксована затримка проти активного опитування", size=17, bold=True))

    PW, PH = 490, 435
    PY = 60

    # Панель 1: Фіксований sleep()
    p1_x = 35
    frags.append(rect(p1_x, PY, PW, PH, fill=BG, stroke=POS, sw=2, rx=8))
    frags.append(text(p1_x + PW / 2, PY + 26, "Крихкий підхід: sleep(100 ms)", size=14, bold=True, color=POS))
    frags.append(line(p1_x + 20, PY + 40, p1_x + PW - 20, PY + 40, color=MUTED, sw=1))

    # Шкала часу 1
    t1_x, t1_y, t1_w = p1_x + 40, PY + 100, 410
    frags.append(line(t1_x, t1_y, t1_x + t1_w, t1_y, color=LINE, sw=2))
    frags.append(arrow(t1_x + t1_w - 10, t1_y, t1_x + t1_w, t1_y, color=LINE, sw=2))
    frags.append(text(t1_x + t1_w, t1_y + 18, "Час (t)", size=10, color=MUTED, anchor="end"))

    # Подія запуску
    frags.append(circle(t1_x + 30, t1_y, 5, fill=NEG, stroke=LINE))
    frags.append(text(t1_x + 30, t1_y - 12, "Команда дії", size=10, bold=True))

    # Сліпий інтервал очікування
    frags.append(rect(t1_x + 30, t1_y - 8, 220, 16, fill=WARN, stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(t1_x + 140, t1_y - 14, "Сліпий sleep(100 ms)", size=10, bold=True, color="#d97706"))

    # Точка assert
    frags.append(line(t1_x + 250, t1_y - 30, t1_x + 250, t1_y + 30, color=POS, sw=2, dash="4 3"))
    frags.append(text(t1_x + 250, t1_y + 45, "Точка assert_true()", size=11, bold=True, color=POS))

    # Реальне настання події при джитері
    frags.append(circle(t1_x + 290, t1_y, 6, fill=HOT, stroke=POS))
    frags.append(text(t1_x + 290, t1_y - 14, "Подія готова (t=115 ms)", size=10, bold=True, color=POS))
    frags.append(text(t1_x + 290, t1_y - 28, "Через джитер RTOS!", size=9, color=POS, italic=True))

    res1, _, _ = textbox(p1_x + PW / 2, PY + 240,
                         "Результат: МИГОТЛИВИЙ ЗБІЙ ТЕСТУ\n"
                         "Перевірка виконується до того, як асинхронний\n"
                         "процес встиг завершитися через навантаження CPU.",
                         size=11, fill=HOT, stroke=POS, bold=True, pad=8)
    frags.append(res1)

    c1, _, _ = textbox(p1_x + PW / 2, PY + 365,
                       "Псевдокод крихкого тесту:\n"
                       "send_command_async();\n"
                       "thread_sleep(100); // надія на фіксований таймінг\n"
                       "assert_eq(device.state, STATE_READY);",
                       size=10, fill=FILL, stroke=LINE, pad=8)
    frags.append(c1)

    # Панель 2: Активне опитування
    p2_x = 555
    frags.append(rect(p2_x, PY, PW, PH, fill=BG, stroke=FIELD, sw=2, rx=8))
    frags.append(text(p2_x + PW / 2, PY + 26, "Надійний підхід: wait_until(cond, timeout)", size=14, bold=True, color=FIELD))
    frags.append(line(p2_x + 20, PY + 40, p2_x + PW - 20, PY + 40, color=MUTED, sw=1))

    # Шкала часу 2
    t2_x, t2_y, t2_w = p2_x + 40, PY + 100, 410
    frags.append(line(t2_x, t2_y, t2_x + t2_w, t2_y, color=LINE, sw=2))
    frags.append(arrow(t2_x + t2_w - 10, t2_y, t2_x + t2_w, t2_y, color=LINE, sw=2))
    frags.append(text(t2_x + t2_w, t2_y + 18, "Час (t)", size=10, color=MUTED, anchor="end"))

    # Подія запуску
    frags.append(circle(t2_x + 30, t2_y, 5, fill=NEG, stroke=LINE))
    frags.append(text(t2_x + 30, t2_y - 12, "Команда дії", size=10, bold=True))

    # Кроки опитування
    for px_offset in [70, 110, 150, 190, 230, 270]:
        frags.append(line(t2_x + px_offset, t2_y - 8, t2_x + px_offset, t2_y + 8, color=MUTED, sw=1.5))

    frags.append(text(t2_x + 170, t2_y - 16, "Опитування кожні 10 ms", size=10, color=MUTED))

    # Успішне фіксування події
    frags.append(circle(t2_x + 270, t2_y, 6, fill=GRN, stroke=FIELD))
    frags.append(text(t2_x + 270, t2_y - 14, "Спрацював предикат (t=115 ms)", size=10, bold=True, color=FIELD))
    frags.append(text(t2_x + 270, t2_y + 24, "Миттєве продовження!", size=9, bold=True, color=FIELD))

    # Ліміт тайм-ауту
    frags.append(line(t2_x + 370, t2_y - 25, t2_x + 370, t2_y + 25, color="#d97706", sw=1.5, dash="4 3"))
    frags.append(text(t2_x + 370, t2_y + 40, "Timeout (500 ms)", size=10, bold=True, color="#d97706"))

    res2, _, _ = textbox(p2_x + PW / 2, PY + 240,
                         "Результат: 100% СТАБІЛЬНИЙ ТЕСТ\n"
                         "Тест не залежить від джитеру, не витрачає зайвий час,\n"
                         "а в разі реального зависання падає за тайм-аутом.",
                         size=11, fill=GRN, stroke=FIELD, bold=True, pad=8)
    frags.append(res2)

    c2, _, _ = textbox(p2_x + PW / 2, PY + 365,
                       "Псевдокод надійного тесту:\n"
                       "send_command_async();\n"
                       "wait_until([&]() { return device.state == STATE_READY; },\n"
                       "           timeout=500, interval=10);",
                       size=10, fill=FILL, stroke=LINE, pad=8)
    frags.append(c2)

    render(os.path.join(IMG, "async-polling-vs-sleep.svg"), W, H, *frags)


# ── Фігура 4: Кінцевий автомат карантину та життєвого циклу тестів ───────────
def fig_quarantine_lifecycle_fsm():
    W, H = 1080, 540
    frags = []

    frags.append(text(W / 2, 32, "Кінцевий автомат системи автоматичного карантину миготливих тестів у CI", size=17, bold=True))

    # Стан 1: Активний (Блокуючий)
    s1_x, s1_y = 150, 160
    b1, w1, h1 = textbox(s1_x, s1_y, "АКТИВНИЙ ТЕСТ\n(Active / Blocking)\nБлокує злиття PR у разі збою", size=12, fill=GRN, stroke=FIELD, sw=2, bold=True, pad=12)
    frags.append(b1)

    # Стан 2: Під підозрою
    s2_x, s2_y = 540, 160
    b2, w2, h2 = textbox(s2_x, s2_y, "ПІД ПІДОЗРОЮ\n(Suspected Flaky)\nПовторний прогін 3–5 разів", size=12, fill=WARN, stroke="#d97706", sw=2, bold=True, pad=12)
    frags.append(b2)

    # Стан 3: Карантин (Неблокуючий)
    s3_x, s3_y = 930, 160
    b3, w3, h3 = textbox(s3_x, s3_y, "КАРАНТИН\n(Quarantined)\nВиконується, але НЕ блокує PR", size=12, fill=HOT, stroke=POS, sw=2, bold=True, pad=12)
    frags.append(b3)

    # Стан 4: Верифікація виправлення
    s4_x, s4_y = 540, 410
    b4, w4, h4 = textbox(s4_x, s4_y, "ВЕРИФІКАЦІЯ ВИПРАВЛЕННЯ\n(Verification Pool)\nСтрес-перевірка: 500 чистих прогонів", size=12, fill=COLD, stroke=NEG, sw=2, bold=True, pad=12)
    frags.append(b4)

    # Переходи між станами
    # 1 -> 2: Збій тесту
    frags.append(arrow(s1_x + w1 / 2, s1_y, s2_x - w2 / 2, s2_y, color="#d97706", sw=2))
    frags.append(text((s1_x + s2_x) / 2, s1_y - 14, "Перший збій тесту", size=10, bold=True, color="#d97706"))

    # 2 -> 1: Успішний повтор (одиничний збій не підтвердився)
    frags.append(arrow(s2_x - w2 / 2, s2_y + 20, s1_x + w1 / 2, s1_y + 20, color=FIELD, sw=1.5))
    frags.append(text((s1_x + s2_x) / 2, s1_y + 36, "3/3 успішні повтори", size=10, color=FIELD))

    # 2 -> 3: Підтвердження нестабільності (Pass-Fail flip)
    frags.append(arrow(s2_x + w2 / 2, s2_y, s3_x - w3 / 2, s3_y, color=POS, sw=2))
    frags.append(text((s2_x + s3_x) / 2, s2_y - 14, "Миготіння (1 Pass + 1 Fail)", size=10, bold=True, color=POS))

    # 3 -> 4: Створення фіксу / патчу
    frags.append(arrow(s3_x, s3_y + h3 / 2, s4_x + w4 / 2, s4_y, color=NEG, sw=2))
    frags.append(text(s3_x - 30, (s3_y + s4_y) / 2 + 10, "Інженер задеплоїв фікс", size=10, bold=True, color=NEG, anchor="end"))

    # 4 -> 1: Успішна верифікація (500 прогонів без збоїв)
    frags.append(arrow(s4_x - w4 / 2, s4_y, s1_x, s1_y + h1 / 2, color=FIELD, sw=2))
    frags.append(text(s1_x + 30, (s1_y + s4_y) / 2 + 10, "500/500 успішних прогонів\n(Повернення в стрій)", size=10, bold=True, color=FIELD, anchor="start"))

    # 4 -> 3: Збій під час верифікації
    frags.append(arrow(s4_x + 100, s4_y - h4 / 2, s3_x - 50, s3_y + h3 / 2, color=POS, sw=1.5))
    frags.append(text(s4_x + 180, s4_y - 80, "Хоча б 1 збій у 500 тестах", size=10, color=POS))

    # Правило безпеки внизу
    rule_box, _, _ = textbox(W / 2, 495, "Золоте правило карантину: тест ізолюється від блокування пайплайну розробників,\nале формує обов'язковий дефект у трекері та продовжує виконуватися у фоновому стендовому контурі.", size=11, fill="#fafafa", stroke=MUTED, pad=8)
    frags.append(rule_box)

    render(os.path.join(IMG, "quarantine-lifecycle-fsm.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_flaky_probability_growth()
    fig_hil_hardware_noise_sources()
    fig_async_polling_vs_sleep()
    fig_quarantine_lifecycle_fsm()
    print("Всі фігури згенеровано успішно.")
