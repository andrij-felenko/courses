# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_cmd_network_anomalies():
    # Фігура 1: Три мережеві пастки дистанційного керування
    W, H = 860, 500
    p = []

    # Три колонки
    cols = [
        {"x": 150, "title": "1. Втрата зворотного квитка", "col": POS},
        {"x": 430, "title": "2. Залп черги після сну", "col": NEG},
        {"x": 710, "title": "3. Транспортний ≠ Бізнес ACK", "col": FIELD},
    ]

    for c in cols:
        p.append(fitbox(c["x"] - 130, 45, 260, 36, c["title"], size=13, bold=True, stroke=c["col"], fill="#fcfcfc"))

    # Панель 1: Втрата зворотного квитка (Lost Return ACK)
    p.append(line(70, 100, 70, 440, color=MUTED, sw=1, dash="3 3"))
    p.append(line(230, 100, 230, 440, color=MUTED, sw=1, dash="3 3"))
    p.append(text(70, 95, "Сервер", size=11, bold=True, color=INK))
    p.append(text(230, 95, "Пристрій", size=11, bold=True, color=INK))

    p.append(arrow(70, 130, 230, 150, color=INK, sw=1.5))
    p.append(fitbox(80, 125, 140, 24, "Команда 1: «Увімкнути»", size=10, bold=True, stroke=INK, fill="#ffffff"))

    p.append(fitbox(175, 165, 105, 26, "Реле: КЛІК (УВІМК)", size=10, bold=True, stroke=FIELD, fill="#eafaf0"))

    p.append(arrow(230, 205, 130, 220, color=POS, sw=1.5))
    p.append(fitbox(95, 215, 75, 22, "ACK втрачено", size=10, bold=True, stroke=POS, fill="#fdecea", color=POS))
    p.append(line(125, 215, 135, 225, color=POS, sw=2))
    p.append(line(135, 215, 125, 225, color=POS, sw=2))

    p.append(fitbox(40, 250, 115, 26, "Таймаут сервера 5 с", size=10, bold=True, stroke=POS, fill="#fff3f0"))

    p.append(arrow(70, 290, 230, 310, color=POS, sw=1.5))
    p.append(fitbox(80, 285, 140, 24, "Повтор: «Увімкнути»", size=10, bold=True, stroke=POS, fill="#fff3f0"))

    p.append(fitbox(150, 335, 145, 38, "Без токена: повторний КЛІК\n(руйнівний дублікат!)", size=10, bold=True, stroke=POS, fill="#fdecea", color=POS))
    p.append(fitbox(150, 388, 145, 38, "З токеном: КЛІК пропущено,\nповторено збережений ACK", size=10, bold=True, stroke=FIELD, fill="#eafaf0", color=FIELD))

    # Панель 2: Черга під час сну (Deep Sleep Queue Burst)
    p.append(fitbox(310, 100, 240, 38, "Пристрій у глибокому сні\n(Wi-Fi / NB-IoT / LoRaWAN)", size=10, bold=True, stroke=MUTED, fill="#f0f2f5"))

    p.append(fitbox(310, 150, 240, 80, "Черга брокера / шлюзу:\n1. 10:00 — «Відкрити клапан»\n2. 10:05 — «Закрити клапан»\n3. 10:15 — «Відкрити на 50%»\n4. 10:40 — «АВАРІЙНИЙ СТОП»", size=10, stroke=NEG, fill="#ffffff"))

    p.append(arrow(430, 240, 430, 275, color=NEG, sw=2))
    p.append(fitbox(320, 285, 220, 28, "Пробудження: залп 4 команд!", size=10, bold=True, stroke=NEG, fill="#eaf0fd", color=NEG))

    p.append(fitbox(310, 330, 240, 95, "Без перевірки TTL:\nвиконання всіх 4 застарілих дій\n(клапан смикається туди-сюди!)\n\nЗ перевіркою TTL:\nкоманди 1–3 прострочено (DROP),\nвиконується лише аварійний стоп", size=10, bold=True, stroke=FIELD, fill="#eafaf0"))

    # Панель 3: Транспортний ACK vs Бізнес ACK
    p.append(fitbox(580, 100, 260, 52, "Клієнт шле команду в MQTT / HTTP\n`POST /api/v1/device/door/open`\n(рівень транспорту: QoS 1 / TCP)", size=10, stroke=INK, fill="#ffffff"))

    p.append(arrow(710, 160, 710, 190, color=FIELD, sw=1.5))
    p.append(fitbox(580, 200, 260, 48, "Транспортний ACK (PUBACK / 200 OK):\n«Пакет осів у буфері брокера»\n(залізо ще навіть не знає про нього!)", size=10, bold=True, stroke=MUTED, fill="#f4f6f8"))

    p.append(arrow(710, 255, 710, 285, color=FIELD, sw=1.5))
    p.append(fitbox(580, 295, 260, 52, "Етап 1: Квиток отримання (Phase 1 ACK)\n«Пристрій розібрав команду,\nперевірив TTL і взяв у чергу»", size=10, bold=True, stroke=NEG, fill="#eaf0fd"))

    p.append(arrow(710, 355, 710, 385, color=FIELD, sw=1.5))
    p.append(fitbox(580, 395, 260, 52, "Етап 2: Квиток виконання (Phase 2 ACK)\n«Кінцевик спрацював, мотор спинено,\nрезультат: SUCCESS (або FAULT)»", size=10, bold=True, stroke=FIELD, fill="#eafaf0"))

    render(os.path.join(IMG, 'cmd-network-anomalies.svg'), W, H, *p,
           title="Мережеві аномалії: втрата квитків, сон пристрою та розрив між транспортом і залізом")


def fig_cmd_lifecycle_fsm():
    # Фігура 2: Повний життєвий цикл команди (Command Lifecycle FSM)
    W, H = 860, 500
    p = []

    x_created = 110
    x_queued = 265
    x_dispatched = 420
    x_exec = 595

    y_main = 145

    p.append(fitbox(x_created - 60, y_main - 28, 120, 56, "CREATED\nСтворено сервером\n(UUID, Token, TTL)", size=10, bold=True, stroke=INK, fill="#f4f6f8"))
    p.append(arrow(x_created + 63, y_main, x_queued - 63, y_main, color=INK, sw=1.8))

    p.append(fitbox(x_queued - 60, y_main - 28, 120, 56, "QUEUED\nУ черзі шлюзу\n(очікує лінк / сон)", size=10, bold=True, stroke=NEG, fill="#eaf0fd"))
    p.append(arrow(x_queued + 63, y_main, x_dispatched - 63, y_main, color=NEG, sw=1.8))

    p.append(fitbox(x_dispatched - 60, y_main - 28, 120, 56, "DISPATCHED\nВідправлено в ефір\n(пакет у польоті)", size=10, bold=True, stroke=NEG, fill="#eaf0fd"))
    p.append(arrow(x_dispatched + 63, y_main, x_exec - 73, y_main, color=FIELD, sw=1.8))

    # Фаза 1 ACK
    p.append(fitbox(440, 42, 260, 40, "Фаза 1: ACK_RECEIVED (Квиток прийому)\nПеревірено CRC, підпис, токен і TTL", size=10, bold=True, stroke=NEG, fill="#eaf0fd"))
    p.append(arrow(x_exec, y_main - 30, 560, 85, color=NEG, sw=1.5))

    p.append(fitbox(x_exec - 70, y_main - 28, 140, 56, "EXECUTING\nВиконується залізом\n(мотор, реле, сенсор)", size=10, bold=True, stroke=FIELD, fill="#eafaf0"))

    # Фінальні стани
    x_term = 765
    y_succ = 75
    y_fail = 180
    y_exp = 300

    p.append(arrow(x_exec + 73, y_main - 10, x_term - 73, y_succ + 10, color=FIELD, sw=1.8))
    p.append(fitbox(x_term - 70, y_succ - 28, 140, 56, "SUCCEEDED\nУспішно завершено\n(ACK_COMPLETED)", size=10, bold=True, stroke=FIELD, fill="#eafaf0", color=FIELD))

    p.append(arrow(x_exec + 73, y_main + 10, x_term - 73, y_fail - 10, color=POS, sw=1.8))
    p.append(fitbox(x_term - 70, y_fail - 28, 140, 56, "FAILED\nАпаратна похибка\n(ACK_FAILED + код)", size=10, bold=True, stroke=POS, fill="#fdecea", color=POS))

    # EXPIRED
    p.append(fitbox(x_term - 70, y_exp - 28, 140, 56, "EXPIRED\nПрострочено за TTL\n(ACK_EXPIRED)", size=10, bold=True, stroke=MUTED, fill="#fff3f0", color=POS))

    p.append(arrow(x_queued, y_main + 30, x_term - 75, y_exp + 10, color=POS, sw=1.5))
    p.append(fitbox(230, 245, 180, 26, "TTL минув у черзі брокера", size=10, bold=True, stroke=POS, fill="#ffffff"))

    p.append(arrow(x_exec, y_main + 30, x_term - 75, y_exp - 10, color=POS, sw=1.5))
    p.append(fitbox(530, 245, 180, 26, "Перевищено таймаут виконання", size=10, bold=True, stroke=POS, fill="#ffffff"))

    # Нижня панель: Two-Phase ACK
    p.append(rect(40, 375, 780, 105, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(430, 395, "Двофазне квитування: чітке розмежування обов'язків", size=12, bold=True, color=INK))

    p.append(fitbox(55, 410, 360, 58, "Фаза 1: ACK прийняття (транспортна гарантія)\n• Захищає сервер від повторних перевідправок у мережу\n• Підтверджує, що пристрій живий і зафіксував токен", size=10, stroke=NEG, fill="#eaf0fd"))

    p.append(fitbox(430, 410, 375, 58, "Фаза 2: ACK результату (фізична гарантія)\n• Передає статус кінцевиків, виміряні величини або код аварії\n• Дозволяє бізнес-логіці оновити актуальний стан у хмарі", size=10, stroke=FIELD, fill="#eafaf0"))

    render(os.path.join(IMG, 'cmd-lifecycle-fsm.svg'), W, H, *p,
           title="Скінченний автомат станів команди та архітектура двофазного квитування")


def fig_cmd_idempotency_ring():
    # Фігура 3: Кільцевий буфер ідемпотентності та дедуплікація
    W, H = 860, 480
    p = []

    p.append(fitbox(35, 140, 200, 90, "Вхідний пакет команди:\n• Command: RELAY_ON\n• Token: 0x8F3A2B1C\n• Nonce: 1042\n• TTL: 30 s", size=10, bold=True, stroke=INK, fill="#f4f6f8"))

    p.append(arrow(240, 185, 305, 185, color=INK, sw=2))
    p.append(fitbox(240, 145, 80, 28, "Пошук токена\nв кеші", size=9, bold=True, stroke=INK, fill="#ffffff"))

    # Кільцевий буфер
    p.append(rect(310, 65, 250, 250, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(435, 88, "Кільцевий буфер ідемпотентності", size=11, bold=True, color=INK))
    p.append(text(435, 105, "(Idempotency Ring Buffer / RAM)", size=10, color=MUTED))

    slots = [
        {"idx": "[0]", "tok": "0x11A204BF", "st": "DONE (OK)", "col": MUTED},
        {"idx": "[1]", "tok": "0x8F3A2B1C", "st": "DONE (OK) ★", "col": FIELD},
        {"idx": "[2]", "tok": "0x4C99E012", "st": "EXECUTING", "col": NEG},
        {"idx": "[3]", "tok": "0x00000000", "st": "FREE", "col": MUTED},
    ]

    sy = 120
    for s in slots:
        bg = "#eafaf0" if "★" in s["st"] else "#f8f9fa"
        p.append(fitbox(320, sy, 230, 30, f"{s['idx']} Tok: {s['tok']} → {s['st']}", size=10, bold=True, stroke=s["col"], fill=bg, color=s["col"]))
        sy += 38

    p.append(text(435, 292, "Вказівник перезапису: найстаріший слот", size=9, color=MUTED))

    # Розгалуження праворуч
    p.append(arrow(565, 160, 645, 110, color=FIELD, sw=1.8))
    p.append(fitbox(650, 65, 195, 90, "ТОКЕН ЗНАЙДЕНО (Дублікат):\n1. Залізо НЕ чіпаємо!\n(реле не смикається вдруге)\n2. Миттєво повертаємо збережену\nвідповідь: ACK_COMPLETED", size=9, bold=True, stroke=FIELD, fill="#eafaf0", color=FIELD))

    p.append(arrow(565, 205, 645, 255, color=NEG, sw=1.8))
    p.append(fitbox(650, 210, 195, 90, "НОВИЙ ТОКЕН:\n1. Запис токена в слот буфера\n2. Стан = EXECUTING\n3. Фізичне спрацювання реле\n4. Оновлення стану = DONE\n5. Відправка ACK_COMPLETED", size=9, bold=True, stroke=NEG, fill="#eaf0fd", color=NEG))

    # Нижня плашка
    p.append(rect(35, 345, 790, 110, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(430, 368, "Захист від накопичення та розмноження побічних ефектів", size=12, bold=True, color=INK))

    p.append(fitbox(50, 385, 365, 58, "Неідемпотентна дія («Змінити стан на протилежний»)\nБез токена: реле вмикається і вимикається 5 разів\nчерез мережеві ретраї при поганому радіозв'язку.", size=10, stroke=POS, fill="#fdecea"))

    p.append(fitbox(430, 385, 380, 58, "Ідемпотентна дія («Увімкнути з токеном 0x8F3A2B1C»)\nЗ токеном: реле спрацьовує РІВНО ОДИН РАЗ.\nУсі 4 дублікати повертають успіх з кешу без повторного удару.", size=10, stroke=FIELD, fill="#eafaf0"))

    render(os.path.join(IMG, 'cmd-idempotency-ring.svg'), W, H, *p,
           title="Кільцевий буфер ідемпотентності: дедуплікація та кешування відповідей")


def fig_cmd_ttl_timeline():
    # Фігура 4: Механіка Time-To-Live (TTL) та детекція застарілих сигналів
    W, H = 860, 440
    p = []

    p.append(line(80, 70, 780, 70, color=INK, sw=2))
    p.append(arrow(770, 70, 790, 70, color=INK, sw=2))
    p.append(text(780, 55, "Час (t)", size=11, bold=True, color=INK))

    ticks = [
        {"x": 100, "t": "t₀ = 0 с", "lbl": "Створення команди\n(TTL = 30 с, дедлайн t₀+30)"},
        {"x": 310, "t": "t₁ = 10 с", "lbl": "Прийом пристроєм\n(Залишок TTL = 20 с > 0 → OK)"},
        {"x": 530, "t": "t₂ = 30 с", "lbl": "МЕЖА TTL (Дедлайн)\nПісля цього — заборона дії"},
        {"x": 720, "t": "t₃ = 45 с", "lbl": "Запізніле пробудження\n(TTL вичерпано → DROP)"},
    ]

    for tk in ticks:
        p.append(line(tk["x"], 62, tk["x"], 78, color=INK, sw=2))
        p.append(text(tk["x"], 95, tk["t"], size=10, bold=True, color=INK))
        p.append(fitbox(tk["x"] - 80, 110, 160, 40, tk["lbl"], size=9, stroke=MUTED, fill="#ffffff"))

    # Сценарій А
    p.append(rect(50, 175, 760, 110, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(170, 200, "Сценарій А: Виконання в межах TTL", size=11, bold=True, color=FIELD))

    p.append(line(310, 225, 480, 225, color=FIELD, sw=6))
    p.append(fitbox(310, 240, 170, 28, "Виконання: 10 с ... 18 с (< 30 с)", size=9, bold=True, stroke=FIELD, fill="#ffffff", color=FIELD))
    p.append(fitbox(500, 215, 200, 50, "РЕЗУЛЬТАТ: УСПІХ\nКлапан відкрито вчасно,\nACK_COMPLETED відправлено", size=10, bold=True, stroke=FIELD, fill="#eafaf0"))

    # Сценарій Б
    p.append(rect(50, 305, 760, 115, fill="#fff7f7", stroke=POS, sw=1.5, rx=8))
    p.append(text(190, 330, "Сценарій Б: Скасування застарілої команди", size=11, bold=True, color=POS))

    p.append(line(310, 355, 720, 355, color=POS, sw=2, dash="4 4"))
    p.append(fitbox(310, 370, 200, 36, "Затримка в радіомережі / сон МК\n(спроба старту на t₃ = 45 с)", size=9, bold=True, stroke=POS, fill="#ffffff", color=POS))

    p.append(fitbox(530, 350, 260, 52, "РЕЗУЛЬТАТ: ВІДХИЛЕНО (EXPIRED)\nПеревірка: Now(45 с) > Deadline(30 с)!\nФізичну дію заблоковано, емітовано ACK_EXPIRED", size=9, bold=True, stroke=POS, fill="#fdecea", color=POS))

    render(os.path.join(IMG, 'cmd-ttl-timeline.svg'), W, H, *p,
           title="Часова лінія перевірки строку дії (TTL) та блокування застарілих сигналів керування")


def main():
    fig_cmd_network_anomalies()
    fig_cmd_lifecycle_fsm()
    fig_cmd_idempotency_ring()
    fig_cmd_ttl_timeline()
    print("Done generating figures for komanda-prystroiu")


if __name__ == '__main__':
    main()
