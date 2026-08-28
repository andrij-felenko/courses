# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_T   = "#fdecea"
GREEN_T = "#f2faf5"
BLUE_T  = "#eaf0fd"
GREY_T  = "#f4f6f8"
AMBER_T = "#fef8e7"
AMBER   = "#d97706"


# ── 1. Три горизонти сприйняття одного оновлення ──────────────────────────────
def fig_release_notes_audiences():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 36, "Три горизонти сприйняття нотаток випуску", size=17, bold=True))

    # Центральний артефакт зверху: прошивка/пакет
    frags.append(fitbox(W / 2 - 240, 64, 480, 54,
                        "Один пакет оновлення (Firmware / Software Release v3.2.0)",
                        size=14, bold=True, fill=GREY_T, stroke=LINE, sw=2.0))

    # Три стрілки від центру до трьох колонок
    col_w = 340
    xs = [50, 420, 790]
    centers = [x + col_w / 2 for x in xs]

    for cx in centers:
        frags.append(arrow(W / 2, 118, cx, 165, color=LINE, sw=1.8))

    cols_data = [
        (xs[0], NEG, BLUE_T, "Власник / Користувач",
         "Питання: Що змінилося і що мені робити?",
         [
             "• Нові функціональні можливості",
             "• Зміни в поведінці приладу / UI",
             "• Обов'язкові ручні дії (перекалібрування)",
             "• Попередження про несумісність застосунку"
         ],
         "Фокус: споживча цінність та дії"),

        (xs[1], AMBER, AMBER_T, "Оператор парку / DevOps",
         "Питання: Як безпечно розгорнути та відкотити?",
         [
             "• Сумісність апаратних ревізій (PCB v1/v2)",
             "• Залежності завантажувача (Bootloader)",
             "• Міграція енергонезалежної пам'яті (NVM)",
             "• Матриця безпеки відкату (Rollback safety)"
         ],
         "Фокус: стабільність парку й процедури"),

        (xs[2], FIELD, GREEN_T, "Інтегратор API / SDK",
         "Питання: Де зламається мій код?",
         [
             "• Зміни сигнатур викликів та RPC",
             "• Зміни бінарних протоколів (CAN, Protobuf)",
             "• Застарілі функції (Deprecations)",
             "• Інструкції та приклади міграції коду"
         ],
         "Фокус: програмні контракти та ABI")
    ]

    for x, col, tint, title, subtitle, points, bottom_note in cols_data:
        frags.append(fitbox(x, 168, col_w, 46, title, size=15, bold=True, fill=tint, stroke=col, sw=2.2))
        frags.append(fitbox(x, 222, col_w, 42, subtitle, size=11.5, italic=True, fill=BG, stroke=col, sw=1.2))
        
        # Список пунктів
        py = 272
        for pt in points:
            frags.append(fitbox(x, py, col_w, 40, pt, size=12, fill=BG, stroke=MUTED, sw=1.0))
            py += 46

        frags.append(fitbox(x, 462, col_w, 42, bottom_note, size=12, bold=True, fill=tint, stroke=col, sw=1.5))

    render(os.path.join(IMG, 'release-notes-audiences.svg'), W, H, *frags)


# ── 2. Анатомія структури нотаток випуску ─────────────────────────────────────
def fig_release_notes_anatomy():
    W, H = 1180, 590
    frags = []
    frags.append(text(W / 2, 34, "Структурна анатомія промислового бюлетеня випуску", size=17, bold=True))

    sections = [
        (60,  50,  1060, 48,  GREY_T,  LINE,  1.8, "1. Метадані випуску (Версія SemVer, Дата, Цільова платформа, Мінімальний бутлоадер)", 13.5, True),
        (60,  116, 1060, 46,  BLUE_T,  NEG,   1.8, "2. Головні підсумки (Highlights: 2–3 ключові зміни, що визначають мету релізу)", 13.0, True),
        (60,  170, 1060, 58,  RED_T,   POS,   2.4, "3. ДІЇ ТА ЛАМКІ ЗМІНИ (Breaking Changes & Action Required — червона зона для оператора)", 13.5, True),
        (60,  236, 1060, 54,  AMBER_T, AMBER, 2.0, "4. Матриця сумісності та відкату (Rollback safety: чи дозволено даунгрейд Flash/NVM)", 13.0, True),
        (60,  298, 1060, 84,  BG,      LINE,  1.5, "5. Деталізований журнал компонентів (Firmware Core, Drivers, Network Stack, UI)\n   • Нові можливості (Features)\n   • Виправлення дефектів (Bug Fixes)", 12.5, False),
        (60,  390, 1060, 58,  RED_T,   POS,   2.0, "6. Бюлетені безпеки (Security Advisories: CVE, CVSS, пом'якшення без експлойт-інструкцій)", 13.0, True),
        (60,  456, 1060, 50,  GREEN_T, FIELD, 1.8, "7. Таблиця артефактів (Імена файлів, контрольні суми SHA-256, підписи SBOM)", 13.0, True),
    ]

    for x, y, w, h, fill, stroke, sw, title, fs, bold in sections:
        frags.append(fitbox(x, y, w, h, title, size=fs, bold=bold, fill=fill, stroke=stroke, sw=sw))

    frags.append(fitbox(60, 516, 1060, 50,
                        "Принцип побудови: від критичних ризиків і дій (зверху) до технічних деталей і гешів (знизу).",
                        size=12.5, bold=True, fill=GREY_T, stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, 'release-notes-anatomy.svg'), W, H, *frags)


# ── 3. Баланс розкриття інформації про безпеку ────────────────────────────────
def fig_security_disclosure_balance():
    W, H = 1180, 520
    frags = []
    frags.append(text(W / 2, 34, "Безпекові виправлення: межа між інформуванням та озброєнням", size=17, bold=True))

    cols = [
        (50, POS, RED_T, "Небезпечне замовчування",
         "«Bug fixes and security updates»",
         [
             "• Оператор не знає про рівень загрози",
             "• Оновлення відкладають на місяці",
             "• Немає CVE та оцінки ризику CVSS",
             "• Неможливо вжити заходи захисту"
         ],
         "Наслідок: вразливий парк лишається відкритим"),

        (420, FIELD, GREEN_T, "Інженерний баланс",
         "Відповідальне розкриття (CVD)",
         [
             "• Ідентифікатор CVE та скоринг CVSS",
             "• Опис зачепленої підсистеми",
             "• Умови прояву дефекту",
             "• Тимчасові компенсаційні заходи"
         ],
         "Наслідок: усвідомлене та безпечне оновлення"),

        (790, POS, RED_T, "Небезпечна деталізація",
         "Публікація робочого експлойту",
         [
             "• Покрокові інструкції експлуатації",
             "• Точні зміщення в пам'яті та шелкод",
             "• Готовий скрипт атаки до патчу парку",
             "• Порушення періоду ембарго"
         ],
         "Наслідок: миттєва зброя для зловмисників")
    ]

    cw = 340
    for x, col, tint, head, sub, pts, res in cols:
        frags.append(fitbox(x, 70, cw, 46, head, size=15, bold=True, fill=tint, stroke=col, sw=2.2))
        frags.append(fitbox(x, 122, cw, 38, sub, size=12, italic=True, fill=BG, stroke=col, sw=1.2))

        py = 168
        for pt in pts:
            frags.append(fitbox(x, py, cw, 42, pt, size=12, fill=BG, stroke=MUTED, sw=1.0))
            py += 48

        frags.append(fitbox(x, 370, cw, 50, res, size=12, bold=True, fill=tint, stroke=col, sw=1.6))

    frags.append(fitbox(50, 440, 1080, 56,
                        "Правило безпекових нотаток: дати оператору достатньо фактів для оцінки ризику та ізоляції,\n"
                        "але не давати зловмиснику готового вектора атаки до завершення оновлення парку.",
                        size=13, bold=True, fill=BLUE_T, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'security-disclosure-balance.svg'), W, H, *frags)


# ── 4. Конвеєр генерації з Conventional Commits ──────────────────────────────
def fig_conventional_commits_pipeline():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 34, "Автоматизований конвеєр: від Conventional Commits до нотаток", size=17, bold=True))

    # Зліва: вхідні коміти
    frags.append(fitbox(50, 68, 300, 42, "1. Git-коміти розробників", size=14, bold=True, fill=GREY_T, stroke=LINE, sw=1.8))
    commits = [
        ("feat(can)!: switch to CAN-FD 2Mbps", POS, RED_T),
        ("fix(adc): calibrate voltage offset", NEG, BLUE_T),
        ("fix(sec): CVE-2026-3012 buffer fix", POS, RED_T),
        ("chore(ci): update toolchain to GCC 14", MUTED, GREY_T),
        ("feat(ble): add battery telemetry", FIELD, GREEN_T),
    ]
    cy = 118
    for ctext, col, tint in commits:
        frags.append(fitbox(50, cy, 300, 36, ctext, size=11, bold=True, fill=tint, stroke=col, sw=1.2))
        cy += 42

    # Центр: Парсер та класифікатор у CI
    frags.append(fitbox(410, 120, 320, 200,
                        "2. Парсер конвеєра CI/CD\n\n"
                        "• Синтаксичний розбір префіксів\n"
                        "• Виявлення маркерів '!' та BREAKING\n"
                        "• Зв'язування з номерами CVE / тікетів\n"
                        "• Фільтрація внутрішніх chore/ci/test\n"
                        "• Групування за компонентами",
                        size=12.5, bold=True, fill=BLUE_T, stroke=NEG, sw=2.0))

    frags.append(arrow(350, 220, 410, 220, color=LINE, sw=2.0))

    # Справа: Розділи згенерованих нотаток
    frags.append(fitbox(790, 68, 340, 42, "3. Згенерований бюлетень", size=14, bold=True, fill=GREY_T, stroke=LINE, sw=1.8))
    sections_out = [
        ("🔴 Breaking Changes (мажорне підняття)", RED_T, POS),
        ("🔒 Security Advisories (CVE-2026-3012)", RED_T, POS),
        ("✨ Features (CAN-FD, BLE battery)", GREEN_T, FIELD),
        ("🐛 Bug Fixes (ADC calibration)", BLUE_T, NEG),
        ("🧹 Internal chore (відфільтровано)", GREY_T, MUTED),
    ]
    oy = 118
    for stext, tint, col in sections_out:
        frags.append(fitbox(790, oy, 340, 36, stext, size=11.5, bold=True, fill=tint, stroke=col, sw=1.4))
        oy += 42

    frags.append(arrow(730, 220, 790, 220, color=LINE, sw=2.0))

    # Нижній підсумок
    frags.append(fitbox(50, 460, 1080, 66,
                        "Conventional Commits перетворюють текст коміту на структуровані дані для релізного конвеєра.\n"
                        "Префікс визначає категорію, знак оклику сигналізує про ламку зміну, а нерелевантний шум відсікається автоматично.",
                        size=13, bold=True, fill=GREY_T, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, 'conventional-commits-pipeline.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_release_notes_audiences()
    fig_release_notes_anatomy()
    fig_security_disclosure_balance()
    fig_conventional_commits_pipeline()
    print("All figures generated successfully in", IMG)
