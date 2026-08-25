# -*- coding: utf-8 -*-
"""Фігури до теми «Poison message / карантин»."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / помилка / отруйне повідомлення
COOL = "#eaf0fd"   # структура / шина / буфер / інспекція
GOOD = "#e8f6ee"   # успіх / валідне повідомлення / відновлення
WARN = "#fef9e7"   # застереження / спроби повтору / карантин
PANEL = "#f8fafc"  # панель-тло


# ── 1. Анатомія та класифікація отруйних повідомлень ──────────────────────────
def fig_poison_anatomy():
    W, H = 1180, 520
    f = []

    # Загальне тло контуру
    f.append(rect(15, 15, 1150, 490, fill=PANEL, stroke="#cbd5e1", sw=1.5, rx=10))
    f.append(text(590, 42, "Таксономія та руйнівний вплив отруйних повідомлень (Poison Messages)", size=15, bold=True, color="#1e293b"))

    # 5 категорій отрут у вигляді колонок
    cols = [
        ("1. Структурна отрута\n(Syntactic / Byte Level)",
         "• Битий потік байтів / невалідний UTF-8\n• Синтаксично зламаний JSON/Protobuf\n• Пошкоджені заголовки та магічні байти\n• Помилка десеріалізації на рівні парсера",
         "Симптом: Миттєвий виняток парсингу\n(JsonParseException, DecodeError)",
         WARM, POS),
        ("2. Розрив схеми даних\n(Schema Evolution Gap)",
         "• Відсутність обов'язкового поля\n• Зміна типу (рядок замість масиву чисел)\n• Невідомий варіант enum без fallback\n• Невідповідність версії Schema Registry",
         "Симптом: Помилка валідації моделі\n(SchemaMismatch, ValidationError)",
         WARN, "#b45309"),
        ("3. Семантична отрута\n(Domain Invariant Trap)",
         "• Від'ємна сума грошової транзакції\n• Ділення на нуль у формулі тарифу\n• Циклічні посилання в дереві сутностей\n• Неприпустимий перехід кінцевого автомата",
         "Симптом: Порушення бізнес-інваріанта\n(InvariantViolationException)",
         COOL, NEG),
        ("4. Ресурсна пастка\n(Algorithmic / Resource DoS)",
         "• Zip Bomb / XML Entity Expansion (Billion Laughs)\n• ReDoS: регулярний вираз із бектрекінгом\n• Запит буфера на 4 ГБ за довжиною заголовка\n• Безкінечний цикл у бізнес-алгоритмі",
         "Симптом: 100% CPU lockup або OOM\n(OutOfMemoryError, CPU Starvation)",
         WARM, POS),
        ("5. Фатальна аварія ядра\n(Runtime Crash / Panic)",
         "• Розіменування nullptr у нативному C/C++ FFI\n• SIGSEGV / Stack Overflow / Panic у рантаймі\n• Взаємне блокування потоків (Deadlock)\n• Миттєве падіння операційної системи процесу",
         "Симптом: Аварійна загибель воркера\n(CrashLoopBackOff, SIGSEGV, SIGKILL)",
         "#fee2e2", "#991b1b")
    ]

    col_w = 216
    col_gap = 14
    start_x = 30

    for i, (head, body, symptom, bg_color, border_color) in enumerate(cols):
        cx = start_x + i * (col_w + col_gap)

        # Картка категорії
        f.append(rect(cx, 65, col_w, 420, fill="#ffffff", stroke=border_color, sw=1.6, rx=8))

        # Заголовок колонки
        f.append(fitbox(cx + 6, 75, col_w - 12, 54, head, size=11, bold=True, fill=bg_color, stroke=border_color))

        # Опис механізму
        f.append(fitbox(cx + 6, 138, col_w - 12, 195, body, size=10, pad=6, fill="#fafafa", stroke="#e2e8f0"))

        # Блок симптому / наслідку
        f.append(rect(cx + 6, 342, col_w - 12, 75, fill=bg_color, stroke=border_color, sw=1.2, rx=6))
        f.append(fitbox(cx + 8, 345, col_w - 16, 68, symptom, size=9.5, bold=True, fill=bg_color, stroke="none", color=border_color))

        # Статус традиційного повтору
        f.append(rect(cx + 6, 425, col_w - 12, 50, fill="#1e293b", stroke="none", rx=6))
        f.append(fitbox(cx + 8, 428, col_w - 16, 44, "Звичайний Retry:\n100% ДЕТЕРМІНОВАНИЙ ЗБІЙ", size=9, bold=True, fill="#1e293b", stroke="none", color="#fca5a5"))

    render(os.path.join(OUT, "poison-anatomy-and-classification.svg"), W, H, *f)


# ── 2. Архітектура карантину: ізоляція, діагностика та тріаж ──────────────────
def fig_quarantine_architecture():
    W, H = 1180, 560
    f = []

    # Контур основної системи
    f.append(rect(15, 15, 760, 530, fill=PANEL, stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(395, 42, "Контур виконання та автоматичної ізоляції (Execution & Quarantine)", size=14, bold=True, color="#1e293b"))

    # Джерело повідомлень
    f.append(fitbox(35, 75, 140, 65, "Основна черга\nабо топік\n(Primary Stream)", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(arrow(175, 107, 225, 107, color=LINE, sw=1.6))
    f.append(text(200, 97, "Fetch", size=10, color=MUTED, bold=True))

    # Консюмер та сендбокс-обробник
    f.append(rect(225, 65, 290, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(370, 88, "Воркер зі сторожовим таймером", size=12, bold=True, color=INK))

    f.append(fitbox(240, 102, 260, 48, "1. Ingress Filter & Schema Validation\n(Швидка синтаксична перевірка)", size=10, fill=COOL, stroke="#93c5fd"))
    f.append(fitbox(240, 158, 260, 58, "2. Isolated Execution Sandbox\n• Watchdog Deadline (таймаут CPU)\n• Panic / Signal Interceptor (перехоплення)", size=10, fill=WARN, stroke="#fcd34d"))
    f.append(fitbox(240, 224, 260, 58, "3. Attempt Tracker & Failure Classifier\n• Transient (Мережа) vs Deterministic (Отрута)\n• Delivery Counter: N з MAX_RETRIES", size=10, fill="#faf5ff", stroke="#d8b4fe"))

    # Успішна гілка
    f.append(arrow(515, 126, 585, 126, color=FIELD, sw=1.8))
    f.append(text(550, 116, "ACK", size=11, color=FIELD, bold=True))
    f.append(fitbox(585, 95, 170, 60, "Успішна фіксація\n(Commit Offset / ACK)\nДалі за конвеєром", size=10.5, bold=True, fill=GOOD, stroke=FIELD))

    # Гілка перехідного збою (Retry Backoff)
    f.append(arrow(515, 253, 585, 253, color="#d97706", sw=1.6))
    f.append(text(550, 243, "NACK", size=10, color="#d97706", bold=True))
    f.append(fitbox(585, 225, 170, 60, "Retry з затримкою\n(Backoff + Jitter)\nЛише для перехідних збоїв", size=10, bold=True, fill=WARN, stroke="#d97706"))

    # Гілка негайного/порогового карантину
    f.append(arrow(370, 295, 370, 345, color=POS, sw=2.0))
    f.append(text(380, 325, "Фатальний дефект АБО attempts ≥ Limit", size=10, color=POS, bold=True, anchor="start"))

    # Блок збагачення конверта
    f.append(rect(140, 345, 460, 75, fill="#fff1f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(370, 368, "Формування діагностичного конверта карантину (Quarantine Envelope)", size=11, bold=True, color=POS))
    f.append(fitbox(150, 376, 440, 38,
                    "Payload + Headers + SHA-256 + Stacktrace + Exception Class + Host ID + Timestamp",
                    size=9.5, fill="#ffe4e6", stroke="none", color="#881337"))

    # Сховище карантину (Quarantine Storage)
    f.append(arrow(370, 420, 370, 450, color=POS, sw=1.8))
    f.append(rect(140, 450, 460, 80, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    f.append(text(370, 473, "Сховище карантину (Quarantine Store / Parking Lot)", size=12, bold=True, color=POS))
    f.append(fitbox(150, 482, 440, 40,
                    "Ізольований топік / Dead Letter DB: стан QUARANTINED, не блокує основний потік",
                    size=10, fill=PANEL, stroke="#cbd5e1"))

    # Права панель: Контур тріажу та операційного лікування (Triage & Ops)
    f.append(rect(795, 15, 370, 530, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(980, 42, "Контур тріажу та утилізації (Ops & Triage)", size=14, bold=True, color="#1e293b"))

    # Кроки тріажу
    triage_steps = [
        ("1. Моніторинг та алертинг",
         "• Quarantine Influx Rate > 0\n• Кластерний сплеск отрути (Poison Burst)\n• Активація аварійного Circuit Breaker",
         WARM, POS),
        ("2. Інспекція та діагностика",
         "• Web UI / CLI для перегляду стектейсу\n• Порівняння схеми та тіла повідомлення\n• Локалізація багу в коді або продюсері",
         COOL, LINE),
        ("3. Лікування та модифікація",
         "• Payload Mutation (виправлення дефектних полів)\n• Деплой хотфіксу споживача\n• Оновлення Schema Registry",
         WARN, "#b45309"),
        ("4. Безпечний Redrive (Drain)",
         "• Canary Replay (прогін 1 екземпляра)\n• Rate-Limited повторне введення в чергу\n• Permanent Drop (утилізація з аудитом)",
         GOOD, FIELD)
    ]

    for j, (st_title, st_body, bg_c, str_c) in enumerate(triage_steps):
        sy = 70 + j * 115
        f.append(rect(810, sy, 340, 102, fill=bg_c, stroke=str_c, sw=1.3, rx=6))
        f.append(text(822, sy + 22, st_title, size=11, bold=True, color=INK, anchor="start"))
        f.append(fitbox(820, sy + 30, 320, 64, st_body, size=9.5, pad=4, fill="#ffffff", stroke="none"))

    render(os.path.join(OUT, "quarantine-architecture-and-triage.svg"), W, H, *f)


# ── 3. Блокування початку черги проти ізоляції в партиціях ─────────────────────
def fig_quarantine_partition_hol():
    W, H = 1180, 500
    f = []

    # Верхня половина: БЕЗ карантину (Катастрофа Head-of-Line Blocking)
    f.append(rect(15, 15, 1150, 225, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(590, 38, "Без карантину в журналі подій (Kafka / Pulsar): параліч партиції (Head-of-Line Blocking)", size=13, bold=True, color=POS))

    # Стрічка партиції
    f.append(text(120, 70, "Партиція #0:", size=11, bold=True, color=INK, anchor="start"))

    offsets_bad = [
        ("Offset 101\nВалідне", GOOD, FIELD),
        ("Offset 102\nВалідне", GOOD, FIELD),
        ("Offset 103\n🔥 OTРУТА", "#fee2e2", POS),
        ("Offset 104\nВалідне", "#e2e8f0", "#94a3b8"),
        ("Offset 105\nВалідне", "#e2e8f0", "#94a3b8"),
        ("Offset 106\nВалідне", "#e2e8f0", "#94a3b8"),
    ]

    for idx, (lbl, bg_col, bdr_col) in enumerate(offsets_bad):
        bx = 120 + idx * 110
        f.append(fitbox(bx, 85, 98, 55, lbl, size=10, bold=True, fill=bg_col, stroke=bdr_col))

    # Воркер у циклі збою
    f.append(fitbox(820, 80, 320, 68,
                    "Воркер завис на Offset 103:\n• Виняток / Crash при читанні\n• Offset НЕ фіксується (Commit blocked)\n• 100% затримка (Lag) для Offset 104..106",
                    size=10, bold=True, fill="#ffffff", stroke=POS))

    f.append(arrow(400, 140, 820, 114, color=POS, sw=1.6))
    f.append(text(600, 175, "НАСЛІДОК: Повний простой партиції для всіх користувачів через єдиний дефектний запис", size=11, bold=True, color=POS))

    # Нижня половина: З карантином (Ізоляція та вільний рух потоку)
    f.append(rect(15, 255, 1150, 230, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(590, 278, "З карантином (Sidecar Quarantine Topic): безперервне просування зміщення", size=13, bold=True, color=FIELD))

    f.append(text(120, 310, "Партиція #0:", size=11, bold=True, color=INK, anchor="start"))

    offsets_good = [
        ("Offset 101\n✓ Оброблено", GOOD, FIELD),
        ("Offset 102\n✓ Оброблено", GOOD, FIELD),
        ("Offset 103\n⚡ В карантин", WARN, "#d97706"),
        ("Offset 104\n✓ Оброблено", GOOD, FIELD),
        ("Offset 105\n✓ Оброблено", GOOD, FIELD),
        ("Offset 106\n▶ В обробці", COOL, NEG),
    ]

    for idx, (lbl, bg_col, bdr_col) in enumerate(offsets_good):
        bx = 120 + idx * 110
        f.append(fitbox(bx, 325, 98, 55, lbl, size=10, bold=True, fill=bg_col, stroke=bdr_col))

    # Маршрутизація в бічний топік карантину
    f.append(arrow(390, 380, 390, 420, color=POS, sw=1.6))
    f.append(fitbox(280, 420, 220, 50, "Топік карантину (Quarantine Topic)\n[Offset 103: збережено контекст]", size=9.5, bold=True, fill="#fff1f2", stroke=POS))

    # Воркер з вільним просуванням
    f.append(fitbox(820, 320, 320, 68,
                    "Воркер фіксує Commit Offset 103:\n• Отруйне повідомлення здубльовано в карантин\n• Зміщення успішно пересунуто вперед\n• Здорові повідомлення 104..106 обробляються миттєво",
                    size=10, bold=True, fill="#ffffff", stroke=FIELD))

    f.append(arrow(780, 354, 820, 354, color=FIELD, sw=1.6))
    f.append(text(640, 445, "РЕЗУЛЬТАТ: Нульовий простий партиції, SLA збережено, інцидент ізольовано в бекграунді", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "quarantine-partition-head-of-line.svg"), W, H, *f)


if __name__ == "__main__":
    fig_poison_anatomy()
    fig_quarantine_architecture()
    fig_quarantine_partition_hol()
    print("Фігури успішно згенеровано у %s" % OUT)
