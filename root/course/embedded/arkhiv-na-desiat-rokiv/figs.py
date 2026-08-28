# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. archive-pillars: 4 опори холодного архіву ─────────────────────────────
def fig_archive_pillars():
    W, H = 960, 520
    p = []

    # Верхній дах / Ціль
    top_w, top_h = 880, 60
    tx, ty = (W - top_w) / 2, 25
    p.append(rect(tx, ty, top_w, top_h, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    p.append(text(W / 2, ty + 26, "ЦІЛЬ: Гарантована збірка біт-у-біт і сертифікований випуск патча через 10–15 років",
                  size=14, color=FIELD, bold=True))
    p.append(text(W / 2, ty + 46, "Незмінність артефактів, середовища, ключів та апаратної документації без доступу до інтернету",
                  size=11.5, color=MUTED))

    # 4 колони
    cols = [
        ("1. Джерела й код",
         ["• Повний Git-репозиторій", "• Усі сабмодулі та SDK", "• Заморожені залежності", "• Скрипти збірки й тести", "• Точні SHA-1 / SHA-256"],
         "#e9eefb", NEG),
        ("2. Тулчейн і VM",
         ["• Образ VM / контейнера", "• Компілятор і компонувальник", "• Бібліотеки (libc, RTOS)", "• Ліцензії та емулятори", "• Зафіксована версія ОС"],
         "#fdf0e6", "#c07a2e"),
        ("3. Ключі й секрети",
         ["• Кореневі ключі підпису", "• Сертифікати Secure Boot", "• Схеми депонування", "• Розділення часток (Shamir)", "• Протокол церемонії ключів"],
         "#fdecea", POS),
        ("4. Залізо й документи",
         ["• Схеми, Gerber, BOM", "• Даташити й errata чіпів", "• Креслення тест-джигів", "• Прошивальні інструкції", "• Протоколи сертифікації"],
         "#f3eefb", "#7d3c98"),
    ]

    cw, ch = 205, 270
    gap = 20
    start_x = (W - (4 * cw + 3 * gap)) / 2
    col_y = 110

    for i, (head, lines, fill, stroke) in enumerate(cols):
        cx = start_x + i * (cw + gap)
        # З'єднувальна стрілка від колони до даху
        p.append(line(cx + cw / 2, col_y, cx + cw / 2, ty + top_h, color=stroke, sw=1.8))

        # Тіло колони
        p.append(rect(cx, col_y, cw, ch, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(rect(cx, col_y, cw, 36, fill=stroke, stroke=stroke, sw=1.8, rx=8))
        # Маскуємо нижні кути шапки
        p.append(rect(cx, col_y + 20, cw, 16, fill=stroke, stroke=stroke, sw=0, rx=0))
        p.append(text(cx + cw / 2, col_y + 23, head, size=12.5, color="#ffffff", bold=True))

        for j, ln in enumerate(lines):
            p.append(text(cx + 12, col_y + 62 + j * 42, ln, size=11, color=INK, anchor="start"))

        # З'єднувальна лінія від фундаменту до колони
        p.append(line(cx + cw / 2, col_y + ch, cx + cw / 2, 410, color=stroke, sw=1.8))

    # Нижній фундамент
    bot_w, bot_h = 880, 70
    bx, by = (W - bot_w) / 2, 410
    p.append(rect(bx, by, bot_w, bot_h, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    p.append(text(W / 2, by + 26, "ФУНДАМЕНТ: Фізичне довготривале збереження за правилом 3-2-1",
                  size=13.5, color=INK, bold=True))
    p.append(text(W / 2, by + 50, "Оптичні M-DISC + Стрічки LTO + Холодні WORM-сховища у географічно рознесених сейфах",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "archive-pillars.svg"), W, H, *p,
           title="Чотири обов'язкові опори холодного архіву вбудованого виробу")


# ── 2. bit-rot-timeline: хронологія деградації без архіву ─────────────────────
def fig_bit_rot_timeline():
    W, H = 960, 430
    p = []

    y_axis = 200
    p.append(line(50, y_axis, 910, y_axis, color=LINE, sw=2))
    p.append(text(910, y_axis - 12, "Час експлуатації виробу →", size=11, color=MUTED, anchor="end"))

    events = [
        (80, "0 років", "Реліз виробу",
         ["• Золота збірка у CI", "• Робочі стенди інженерів", "• Доступні всі сервери"],
         FIELD, -1),
        (260, "2 роки", "Перші втрати",
         ["• Зовнішні 404 на репозиторії", "• Провідний розробник пішов", "• Змінились URL-адреси SDK"],
         "#c07a2e", 1),
        (460, "5 років", "Руйнування тулчейну",
         ["• Нова ОС хоста ламає білдер", "• Зламався USB-донгл ліцензії", "• Вендор видалив errata чіпа"],
         POS, -1),
        (670, "8 років", "Криптографічний глухий кут",
         ["• Загублено ключ Secure Boot", "• Сплив строк Root CA", "• Новий GCC дає інший бінарник"],
         POS, 1),
        (870, "10+ років", "Повний колапс",
         ["• 0% шансів зібрати патч", "• Втрата сертифікації", "• Мільйонні відкликання в полі"],
         POS, -1),
    ]

    for x, yr, title, items, color, side in events:
        # Точка на осі
        p.append(circle(x, y_axis, 7, fill="#ffffff", stroke=color, sw=2.5))
        p.append(text(x, y_axis + (18 if side < 0 else -10), yr, size=11.5, color=color, bold=True))

        # Виносний блок
        bw, bh = 160, 110
        bx = x - bw / 2
        by = (y_axis - bh - 32) if side < 0 else (y_axis + 32)

        # Лінія виноски
        p.append(line(x, y_axis + (7 * side), x, by + (bh if side < 0 else 0), color=color, sw=1.5, dash="3,3"))

        p.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=color, sw=1.5, rx=6))
        p.append(rect(bx, by, bw, 24, fill=color, stroke=color, sw=1.5, rx=6))
        p.append(rect(bx, by + 14, bw, 10, fill=color, stroke=color, sw=0, rx=0))
        p.append(text(x, by + 16, title, size=10.5, color="#ffffff", bold=True))

        for k, it in enumerate(items):
            p.append(text(bx + 6, by + 40 + k * 22, it, size=9.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "bit-rot-timeline.svg"), W, H, *p,
           title="Хронологія деградації середовища розробки за відсутності холодного архіву")


# ── 3. cold-archive-lifecycle: життєвий цикл і регламент архіву ──────────────
def fig_cold_archive_lifecycle():
    W, H = 960, 400
    p = []

    steps = [
        ("1. Заморозка релізу", "Створення золотого образу,\nпакування VM/контейнера,\nхешування SHA-256 артефактів", NEG),
        ("2. Запис на 3-2-1 носії", "LTO-стрічка + диск M-DISC +\nізольоване WORM-сховище\nу двох локаціях", "#2e7d32"),
        ("3. Щорічний скрабінг", "Автоматична звірка хешів,\nвиявлення пошкоджень бітів,\nперезапис за потреби", "#c07a2e"),
        ("4. Пожежне тренування", "Розгортання на чистому ПК,\nзбірка з нуля, звірка\nбіт-у-біт із золотим образом", "#7d3c98"),
        ("5. Сертифікований патч", "Внесення екстреної правки,\nпідпис релізним ключем,\nпрошивка парку в полі", POS),
    ]

    bw, bh = 160, 150
    gap = 28
    start_x = (W - (5 * bw + 4 * gap)) / 2
    cy = 130

    for i, (title, desc, stroke) in enumerate(steps):
        x = start_x + i * (bw + gap)
        p.append(rect(x, cy, bw, bh, fill="#fcfdfe", stroke=stroke, sw=2, rx=8))
        p.append(rect(x, cy, bw, 32, fill=stroke, stroke=stroke, sw=2, rx=8))
        p.append(rect(x, cy + 18, bw, 14, fill=stroke, stroke=stroke, sw=0, rx=0))
        p.append(text(x + bw / 2, cy + 21, title, size=11, color="#ffffff", bold=True))

        lines = desc.split("\n")
        for j, ln in enumerate(lines):
            p.append(text(x + bw / 2, cy + 58 + j * 24, ln, size=10, color=INK))

        # Стрілка переходу
        if i < 4:
            p.append(arrow(x + bw + 4, cy + bh / 2, x + bw + gap - 4, cy + bh / 2, color=LINE, sw=1.8))

    # Зворотна стрілка регулярного циклу контролю (від кроку 4 до кроку 3)
    p.append('<path d="M 685 295 L 685 340 L 460 340 L 460 295" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' % MUTED)
    p.append(text(572, 360, "Регулярний цикл підтримки (щорічно / кожні 2 роки)", size=11, color=MUTED, bold=True))

    render(os.path.join(OUT, "cold-archive-lifecycle.svg"), W, H, *p,
           title="Регламент підтримки холодного архіву: від заморозки до екстреного випуску")


# ── 4. reproducible-build-chain: детермінований конвеєр збірки ────────────────
def fig_reproducible_build_chain():
    W, H = 960, 420
    p = []

    # Блок 1: Вхідні дані
    p.append(rect(30, 90, 200, 240, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(130, 118, "ВХІДНІ АРТЕФАКТИ", size=12, color=INK, bold=True))
    p.append(line(45, 130, 215, 130, color=LINE, sw=1))
    inputs = [
        "• Git комміт / субмодулі",
        "• Заморожений toolchain",
        "• Образ контейнера (OCI)",
        "• Фіксований sysroot / RTOS",
        "• Скрипти збірки (CMake)"
    ]
    for i, it in enumerate(inputs):
        p.append(text(45, 160 + i * 32, it, size=10.5, color=INK, anchor="start"))

    p.append(arrow(235, 210, 275, 210, color=LINE, sw=2))

    # Блок 2: Фільтри детермінізму
    p.append(rect(280, 60, 360, 300, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    p.append(text(460, 90, "БАР'ЄРИ ДЕТЕРМІНІЗМУ (ISO / IEC)", size=13, color=FIELD, bold=True))
    p.append(line(300, 105, 620, 105, color=FIELD, sw=1))

    filters = [
        ("SOURCE_DATE_EPOCH", "Фіксація часу замість __DATE__ / __TIME__"),
        ("-fdebug-prefix-map", "Очищення абсолютних шляхів хоста в DWARF"),
        ("LC_ALL=C, TZ=UTC", "Усунення впливу мови та часового поясу"),
        ("Стабільне сортування", "Детермінований порядок лінкування об'єктів"),
        ("Фіксовані прапорці", "Заборона -O3 без фіксації версії компілятора"),
    ]
    for i, (name, note) in enumerate(filters):
        fy = 125 + i * 46
        p.append(rect(295, fy, 330, 38, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
        p.append(text(305, fy + 16, name, size=10.5, color=INK, anchor="start", bold=True))
        p.append(text(305, fy + 30, note, size=9.5, color=MUTED, anchor="start"))

    p.append(arrow(645, 210, 685, 210, color=LINE, sw=2))

    # Блок 3: Результат
    p.append(rect(690, 90, 240, 240, fill="#e9eefb", stroke=NEG, sw=2, rx=8))
    p.append(text(810, 118, "РЕЗУЛЬТАТ ЗБІРКИ", size=12, color=NEG, bold=True))
    p.append(line(705, 130, 915, 130, color=NEG, sw=1))

    outputs = [
        "Збірка 2026 року:",
        "SHA-256: e3b0c442...a5c1",
        "",
        "Збірка 2038 року (з архіву):",
        "SHA-256: e3b0c442...a5c1",
        "",
        "✓ 100% ЗБІГ БІТ-У-БІТ",
        "✓ Не потрібна ресертифікація"
    ]
    for i, it in enumerate(outputs):
        is_bold = "✓" in it or "Збірка" in it
        col = FIELD if "✓" in it else (NEG if "SHA-256" in it else INK)
        p.append(text(705, 155 + i * 22, it, size=10, color=col, anchor="start", bold=is_bold))

    render(os.path.join(OUT, "reproducible-build-chain.svg"), W, H, *p,
           title="Детермінований конвеєр збірки для гарантії побітового збігу прошивки")


if __name__ == "__main__":
    fig_archive_pillars()
    fig_bit_rot_timeline()
    fig_cold_archive_lifecycle()
    fig_reproducible_build_chain()
    print("All figures generated successfully.")
