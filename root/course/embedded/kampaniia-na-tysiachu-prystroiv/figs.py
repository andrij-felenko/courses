# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. canary-rollout-stages: Хвилі оновлення (1% -> 5% -> 25% -> 100%) ───────
def fig_canary_stages():
    W, H = 960, 480
    p = []

    stages = [
        ("Фаза 0: Лабораторія", "Когорта: 0.1% (1 шт)\nGolden Device / HIL\nПеревірка bootloader\nБазовий димовий тест", "#f4f6f8", LINE),
        ("Фаза 1: Канарка 1%", "Когорта: 1% (10 шт)\nРізні типи мереж\nВікно: 24 години\nТригер: >= 1 збій", "#eaf0fd", NEG),
        ("Фаза 2: Пілот 5%", "Когорта: 5% (50 шт)\nРеальне навантаження\nВікно: 48 годин\nТригер: > 2% збоїв", "#fdf6ed", "#b86200"),
        ("Фаза 3: Масштаб 25%", "Когорта: 25% (250 шт)\nСтатистичне покриття\nПеревірка CDN каналу\nТригер: > 1% збоїв", "#f6eefb", "#7b2cbf"),
        ("Фаза 4: Повний парк", "Когорта: 100% (1000 шт)\nРозгортання на всіх\nРандомізований джитер\nЗалишковий моніторинг", "#eef7ee", FIELD),
    ]

    bw, bh = 168, 220
    xs = [20, 210, 400, 590, 780]
    y = 90

    for i, (title, details, fill_c, stroke_c) in enumerate(stages):
        x = xs[i]
        p.append(rect(x, y, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        p.append(text(x + bw / 2, y + 24, title, size=11, color=stroke_c, bold=True))
        p.append(line(x + 10, y + 36, x + bw - 10, y + 36, color=stroke_c, sw=1))
        p.append(mtext(x + bw / 2, y + 60, details, size=10, color=INK, lh=1.35))

        if i < 4:
            p.append(arrow(x + bw + 2, y + bh / 2, xs[i+1] - 4, y + bh / 2, color=LINE, sw=2))
            p.append(text(x + bw + 11, y + bh / 2 - 14, "G%d" % (i + 1), size=10, color=MUTED, bold=True))

    # Нижній блок: Автоматичний Abort & Rollback
    ab_y = 350
    p.append(rect(20, ab_y, 920, 95, fill="#fdf0ed", stroke=POS, sw=1.8, rx=8))
    p.append(text(480, ab_y + 24, "АВТОМАТИЧНИЙ АВАРІЙНИЙ СТОП (ABORT TRIGGER) ТА ВІДКАТ", size=12, color=POS, bold=True))
    abort_desc = (
        "• Перевищення порогу помилок (SLO) на будь-якій фазі негайно зупиняє розгортання для решти парку.\n"
        "• Пристрої з поточної когорти повертаються на стабільний Bank A через апаратний Watchdog або команду бекенду.\n"
        "• Парк переходить у безпечний заморожений стан: аналіз телеметрії збоїв без ризику заблокувати всі 1000 вузлів."
    )
    p.append(mtext(480, ab_y + 46, abort_desc, size=10, color=INK, lh=1.35))

    render(os.path.join(OUT, "canary-rollout-stages.svg"), W, H, *p,
           title="Поетапне канаркове розгортання (1% -> 5% -> 25% -> 100%) із воротами якості")


# ── 2. thundering-herd-jitter: Синхронний пік проти розподіленого джитера ──────
def fig_thundering_herd_jitter():
    W, H = 940, 460
    p = []

    # Лівий графік: Без джитера (Thundering Herd)
    lx, ly, lw, lh = 40, 70, 410, 340
    p.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 25, "Синхронний старт (Thundering Herd)", size=12, color=POS, bold=True))

    # Вісі
    p.append(line(lx + 45, ly + 270, lx + lw - 25, ly + 270, color=LINE, sw=1.5))
    p.append(line(lx + 45, ly + 270, lx + 45, ly + 65, color=LINE, sw=1.5))
    p.append(text(lx + lw - 20, ly + 286, "Час (t)", size=10, color=MUTED, anchor="end"))
    p.append(text(lx + 40, ly + 60, "RPS / Смуга", size=10, color=MUTED, anchor="start"))

    # Пік навантаження
    p.append(rect(lx + 65, ly + 80, 50, 190, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append(text(lx + 90, ly + 140, "1000 запитів\nза 5 секунд!", size=10, color=POS, bold=True))

    # Лінія ліміту сервера
    p.append(line(lx + 45, ly + 180, lx + lw - 25, ly + 180, color=POS, sw=1.5, dash="4,4"))
    p.append(text(lx + lw - 30, ly + 172, "Стеля пропускної здатності", size=9.5, color=POS, anchor="end"))

    # Наслідки ліворуч
    l_desc = (
        "• Вичерпання пулу TLS-з'єднань бекенду\n"
        "• Колапс локальних стільникових базових станцій\n"
        "• Масові таймаути HTTP 504 та обриви сесій\n"
        "• Шквал повторних запитів (Retry Storm)"
    )
    p.append(mtext(lx + 50, ly + 295, l_desc, size=9.5, color=INK, anchor="start", lh=1.3))

    # Правий графік: З рандомізованим вікном (Uniform Jitter)
    rx, ry, rw, rh = 490, 70, 410, 340
    p.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 25, "Згладжене вікно (Random Jitter)", size=12, color=FIELD, bold=True))

    # Вісі
    p.append(line(rx + 45, ry + 270, rx + rw - 25, ry + 270, color=LINE, sw=1.5))
    p.append(line(rx + 45, ry + 270, rx + 45, ry + 65, color=LINE, sw=1.5))
    p.append(text(rx + rw - 20, ry + 286, "Час (t)", size=10, color=MUTED, anchor="end"))
    p.append(text(rx + 40, ry + 60, "RPS / Смуга", size=10, color=MUTED, anchor="start"))

    # Згладжене навантаження
    p.append(rect(rx + 65, ry + 210, 300, 60, fill="#eef7ee", stroke=FIELD, sw=2, rx=4))
    p.append(text(rx + 215, ry + 242, "Рівномірний розподіл: ~5-10 запитів/хв", size=10, color=FIELD, bold=True))

    # Лінія ліміту сервера праворуч
    p.append(line(rx + 45, ry + 180, rx + rw - 25, ry + 180, color=POS, sw=1.5, dash="4,4"))
    p.append(text(rx + rw - 30, ry + 172, "Стеля пропускної здатності", size=9.5, color=POS, anchor="end"))

    # Наслідки праворуч
    r_desc = (
        "• Кожен пристрій обирає затримку: t = Uniform(0, T_window)\n"
        "• Передбачуване навантаження на сервер і CDN\n"
        "• Відсутність перевантаження батарей і радіотракту\n"
        "• Плавне споживання трафіку без черг і відмов"
    )
    p.append(mtext(rx + 50, ry + 295, r_desc, size=9.5, color=INK, anchor="start", lh=1.3))

    render(os.path.join(OUT, "thundering-herd-jitter.svg"), W, H, *p,
           title="Проблема «громового стада» проти згладжування навантаження рандомізованим джитером")


# ── 3. device-update-fsm: Скінченний автомат стану пристрою ──────────────────
def fig_device_fsm():
    W, H = 960, 490
    p = []

    # 5 основних вузлів автомата
    nodes = [
        (60, 100, 140, 75, "IDLE", "Очікування перевірки\nПеріодичний поллінг", "#f4f6f8", LINE),
        (260, 100, 140, 75, "COHORT_WAIT", "Рандомізована затримка\nt = Uniform(0, T_max)", "#eaf0fd", NEG),
        (460, 100, 140, 75, "DOWNLOADING", "Посекційне завантаження\nПеревірка SHA-256 / Ed25519", "#fdf6ed", "#b86200"),
        (660, 100, 140, 75, "FLASH_STAGED", "Запис у неактивний Bank B\nВстановлення boot-прапорця", "#f6eefb", "#7b2cbf"),
        (860, 100, 80, 75, "REBOOT", "Перезапуск у\nновий образ", "#f4f6f8", LINE),
    ]

    for x, y, w, h, title, desc, fill_c, stroke_c in nodes:
        p.append(rect(x, y, w, h, fill=fill_c, stroke=stroke_c, sw=2, rx=6))
        p.append(text(x + w / 2, y + 22, title, size=11, color=stroke_c, bold=True))
        p.append(mtext(x + w / 2, y + 42, desc, size=9.5, color=INK, lh=1.25))

    # Стрілки верхнього ряду
    p.append(arrow(200, 137, 256, 137, color=LINE, sw=1.8))
    p.append(arrow(400, 137, 456, 137, color=LINE, sw=1.8))
    p.append(arrow(600, 137, 656, 137, color=LINE, sw=1.8))
    p.append(arrow(800, 137, 856, 137, color=LINE, sw=1.8))

    # Нижні вузли верифікації та результату
    # Вузол 6: TESTING_HEALTH (випробувальний термін)
    p.append(rect(660, 270, 180, 85, fill="#fff9db", stroke="#f59f00", sw=2, rx=6))
    p.append(text(750, 292, "TESTING_HEALTH", size=11, color="#d97706", bold=True))
    p.append(mtext(750, 312, "Канарковий період (напр. 30 хв)\nСамодіагностика сенсорів\nУспішний зв'язок із сервером", size=9.5, color=INK, lh=1.25))

    # Стрілка від REBOOT до TESTING_HEALTH
    p.append(arrow(900, 175, 760, 266, color=LINE, sw=1.8))

    # Вузол 7: COMMITTED (успіх)
    p.append(rect(340, 270, 160, 85, fill="#eef7ee", stroke=FIELD, sw=2, rx=6))
    p.append(text(420, 292, "COMMITTED", size=11, color=FIELD, bold=True))
    p.append(mtext(420, 312, "Фіксація Bank B постійним\nСкидання лічильника спроб\nЗвіт про успіх на бекенд", size=9.5, color=INK, lh=1.25))

    # Стрілка від TESTING_HEALTH до COMMITTED
    p.append(arrow(660, 312, 504, 312, color=FIELD, sw=2))
    p.append(text(582, 302, "Тести пройдено", size=9.5, color=FIELD, bold=True))

    # Стрілка повернення з COMMITTED в IDLE
    p.append(arrow(340, 312, 130, 179, color=MUTED, sw=1.5))
    p.append(text(210, 260, "Готовий до нових задач", size=9, color=MUTED))

    # Вузол 8: ROLLBACK (аварійний відкат)
    p.append(rect(480, 390, 200, 80, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(text(580, 412, "ROLLBACK_BANK_A", size=11, color=POS, bold=True))
    p.append(mtext(580, 432, "Апаратний WDT / Panic Hook\nПовернення на старий образ\nЗвіт про збій (Crash Report)", size=9.5, color=INK, lh=1.25))

    # Стрілка з TESTING_HEALTH до ROLLBACK
    p.append(arrow(750, 355, 684, 400, color=POS, sw=2))
    p.append(text(745, 385, "Збій / WDT reset", size=9.5, color=POS, bold=True))

    # Стрілка повернення з ROLLBACK в IDLE
    p.append(arrow(480, 430, 90, 179, color=POS, sw=1.5))
    p.append(text(240, 430, "Блокування оновлення до нового релізу", size=9, color=POS))

    render(os.path.join(OUT, "device-update-fsm.svg"), W, H, *p,
           title="Скінченний автомат стану прошивки: завантаження, випробувальний термін і відкат")


if __name__ == "__main__":
    fig_canary_stages()
    fig_thundering_herd_jitter()
    fig_device_fsm()
    print("OK: figures generated ->", OUT)
