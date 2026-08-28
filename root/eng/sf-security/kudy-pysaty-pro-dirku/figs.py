# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Наскрізний потік повідомлення про вразливість ─────────────────
def fig_vulnerability_reporting_flow():
    W, H = 960, 520
    p = []

    p.append(text(W/2, 32, "Наскрізний життєвий цикл повідомлення про вразливість", size=16, color=INK, bold=True))

    # 4 етапи (горизонтальні кроки)
    steps = [
        ("1. Виявлення й розвідка", [
            "• Дослідник знаходить дефект",
            "• Читає /.well-known/security.txt",
            "• Перевіряє Safe Harbor і межі",
            "• Отримує відкритий ключ PGP"
        ], "#eaf2f8", NEG),
        ("2. Безпечне надсилання", [
            "• Формування PoC та опису",
            "• Шифрування на ключ PSIRT",
            "• Відправка на security@",
            "• Автоматичний прийом у чергу"
        ], "#fef9e7", "#b7950b"),
        ("3. Тріаж та валідація", [
            "• SLA: перша відповідь <= 24 год",
            "• Відтворення вади в стенді",
            "• Оцінка критичності (CVSS)",
            "• Передача в інженерну команду"
        ], "#ebf5fb", "#2980b9"),
        ("4. Виправлення й реліз", [
            "• Розробка та тестування патчу",
            "• Резервування номера CVE",
            "• Публікація бюлетеня безпеки",
            "• Виплата винагороди (Bounty)"
        ], "#eafaf1", FIELD)
    ]

    col_w = 210
    col_gap = 26
    start_x = 24
    y_top = 65
    h_col = 220

    for i, (title_s, items, bg_col, stroke_col) in enumerate(steps):
        cx = start_x + i * (col_w + col_gap)
        p.append(rect(cx, y_top, col_w, h_col, fill=bg_col, stroke=stroke_col, sw=1.6, rx=8))
        p.append(rect(cx + 8, y_top + 8, col_w - 16, 32, fill="#ffffff", stroke=stroke_col, sw=1, rx=4))
        p.append(text(cx + col_w/2, y_top + 29, title_s, size=12, color=stroke_col, bold=True))

        for j, itm in enumerate(items):
            p.append(text(cx + 12, y_top + 65 + j * 36, itm, size=10.5, color=INK, anchor="start"))

        if i < len(steps) - 1:
            arr_x1 = cx + col_w + 3
            arr_x2 = cx + col_w + col_gap - 3
            arr_y = y_top + h_col/2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=1.6))

    # Нижній блок: Розподіл відповідальності та взаємні зобов'язання
    y_bot = 310
    w_bot = 912
    h_bot = 185
    p.append(rect(start_x, y_bot, w_bot, h_bot, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    p.append(text(W/2, y_bot + 26, "Взаємні юридичні та операційні гарантії сторін", size=13, color=INK, bold=True))

    # Дві половини внизу
    w_half = 430
    # Ліва: Зобов'язання дослідника
    p.append(rect(start_x + 16, y_bot + 42, w_half, 125, fill="#fdfefe", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(start_x + 16 + w_half/2, y_bot + 62, "Зобов'язання дослідника (Good-Faith Research)", size=11.5, color=NEG, bold=True))
    p.append(text(start_x + 28, y_bot + 86, "• Не знищувати дані користувачів і не порушувати роботу сервісу (No DoS)", size=10, color=INK, anchor="start"))
    p.append(text(start_x + 28, y_bot + 108, "• Діяти суворо в межах оголошеного скоупу (In-Scope активи)", size=10, color=INK, anchor="start"))
    p.append(text(start_x + 28, y_bot + 130, "• Зберігати ембарго до узгодженої дати релізу (Coordinated Disclosure)", size=10, color=INK, anchor="start"))
    p.append(text(start_x + 28, y_bot + 152, "• Надавати мінімально необхідний PoC без масового викачування даних", size=10, color=INK, anchor="start"))

    # Права: Зобов'язання організації
    p.append(rect(start_x + w_half + 36, y_bot + 42, w_half, 125, fill="#fdfefe", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(start_x + w_half + 36 + w_half/2, y_bot + 62, "Зобов'язання компанії (Safe Harbor & PSIRT)", size=11.5, color=FIELD, bold=True))
    p.append(text(start_x + w_half + 48, y_bot + 86, "• Повна правова амністія (відмова від судових позовів за CFAA / DMCA)", size=10, color=INK, anchor="start"))
    p.append(text(start_x + w_half + 48, y_bot + 108, "• Суворе дотримання SLA обробки: відповідь за 24 год, тріаж за 3 дні", size=10, color=INK, anchor="start"))
    p.append(text(start_x + w_half + 48, y_bot + 130, "• Прозорий статус усунення вади та залучення до перевірки патчу", size=10, color=INK, anchor="start"))
    p.append(text(start_x + w_half + 48, y_bot + 152, "• Публічна подяка в бюлетені (Hall of Fame) та виплата Bug Bounty", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "vulnerability-reporting-flow.svg"), W, H, *p,
           title="Наскрізний життєвий цикл повідомлення про вразливість")


# ── Фігура 2: Структура файлу security.txt (RFC 9116) ──────────────────────
def fig_security_txt_structure():
    W, H = 940, 520
    p = []

    p.append(text(W/2, 32, "Анатомія файлу security.txt (RFC 9116) та цифровий підпис", size=16, color=INK, bold=True))

    # Ліва колонка: Текстовий вміст файлу
    x_l = 25
    w_l = 440
    h_box = 445
    y_top = 55

    p.append(rect(x_l, y_top, w_l, h_box, fill="#1c2833", stroke="#2c3e50", sw=1.5, rx=8))
    p.append(rect(x_l + 10, y_top + 10, w_l - 20, 30, fill="#2c3e50", stroke="#34495e", sw=1, rx=4))
    p.append(text(x_l + w_l/2, y_top + 30, "/.well-known/security.txt (Plaintext / PGP Signed)", size=12, color="#ecf0f1", bold=True))

    lines_code = [
        ("-----BEGIN PGP SIGNED MESSAGE-----", "#7f8c8d", False),
        ("Hash: SHA512", "#7f8c8d", False),
        ("", "#ffffff", False),
        ("# Обов'язкові директиви RFC 9116", "#5dade2", True),
        ("Contact: mailto:security@example.com", "#2ecc71", True),
        ("Contact: https://bounty.example.com/report", "#2ecc71", True),
        ("Expires: 2027-04-15T00:00:00.000Z", "#e74c3c", True),
        ("", "#ffffff", False),
        ("# Опційні директиви безпеки", "#5dade2", True),
        ("Encryption: https://example.com/pgp-key.txt", "#f39c12", False),
        ("Canonical: https://example.com/.well-known/security.txt", "#f39c12", False),
        ("Policy: https://example.com/security/policy", "#f39c12", False),
        ("Acknowledgments: https://example.com/hall-of-fame", "#f39c12", False),
        ("Preferred-Languages: uk, en", "#f39c12", False),
        ("Hiring: https://example.com/jobs/security", "#f39c12", False),
        ("", "#ffffff", False),
        ("-----BEGIN PGP SIGNATURE-----", "#7f8c8d", False),
        ("iQIzBAEBCgAdFiEEz4...", "#7f8c8d", False),
        ("-----END PGP SIGNATURE-----", "#7f8c8d", False)
    ]

    for idx, (code_line, col, is_b) in enumerate(lines_code):
        if code_line:
            p.append(text(x_l + 18, y_top + 62 + idx * 19, code_line, size=9.5, color=col, anchor="start", bold=is_b))

    # Права колонка: Розбір директив і правила валідації
    x_r = 485
    w_r = 430

    cards = [
        ("Обов'язкові поля: Contact та Expires", [
            "• Contact: URI точки входу (mailto: або https:// порталу).",
            "• Expires: дата закінчення валідності в ISO 8601.",
            "• Якщо дата Expires минула — сканери й клієнти зобов'язані",
            "  відкинути файл як застарілий та ненадійний."
        ], "#eafaf1", FIELD),
        ("Криптографічні директиви: Encryption & Canonical", [
            "• Encryption: посилання на відкритий PGP-ключ команди.",
            "• Canonical: запобігає підміні файлу на дзеркалах/CDN.",
            "• Дозволяє безпечно надіслати 0-day без витоку на поштових",
            "  серверах проміжних транзитних провайдерів (MTA)."
        ], "#ebf5fb", NEG),
        ("Політика розкриття та Safe Harbor: Policy", [
            "• Policy: посилання на правила тестування й рамки захисту.",
            "• Гарантує досліднику захист від кримінального переслідування,",
            "  якщо він діє добросовісно та не завдає шкоди інфраструктурі."
        ], "#fef9e7", "#d35400")
    ]

    y_cur = y_top
    for card_title, card_items, bg_c, strk_c in cards:
        h_card = 135
        p.append(rect(x_r, y_cur, w_r, h_card, fill=bg_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(x_r + 14, y_cur + 24, card_title, size=12, color=strk_c, bold=True, anchor="start"))
        for k, itm in enumerate(card_items):
            p.append(text(x_r + 14, y_cur + 48 + k * 21, itm, size=10, color=INK, anchor="start"))
        y_cur += h_card + 20

    render(os.path.join(OUT, "security-txt-structure.svg"), W, H, *p,
           title="Анатомія файлу security.txt (RFC 9116) та цифровий підпис")


# ── Фігура 3: Життєвий цикл репорту в PSIRT та шкала SLA ────────────────────
def fig_psirt_triage_lifecycle():
    W, H = 940, 500
    p = []

    p.append(text(W/2, 32, "Хронологія тріажу вразливості в PSIRT: таймери та межі SLA", size=16, color=INK, bold=True))

    # Горизонтальна часова шкала
    y_line = 140
    p.append(line(50, y_line, 890, y_line, color=LINE, sw=3))

    milestones = [
        (90, "T = 0", "Отримання репорту", "Шифрований лист / веб-форма", "#34495e"),
        (250, "T <= 24 год", "Первинна відповідь", "SLA: підтвердження прийому", NEG),
        (430, "T <= 3 дні", "Тріаж і валідація", "Відтворення PoC, скоринг CVSS", "#8e44ad"),
        (630, "T <= 14–60 дн", "Розробка патчу", "Фікс, регресійні тести, білд", POS),
        (830, "T <= 90 днів", "Реліз і розкриття", "CVE, бюлетень, виплата Bounty", FIELD)
    ]

    for mx, t_tag, m_title, m_sub, col in milestones:
        # Точка на лінії
        p.append(circle(mx, y_line, 8, fill=col, stroke="#ffffff", sw=2))
        # Текст зверху лінії
        p.append(text(mx, y_line - 32, t_tag, size=13, color=col, bold=True))
        p.append(text(mx, y_line - 14, m_title, size=11, color=INK, bold=True))
        # Стрілочка вниз
        p.append(line(mx, y_line + 10, mx, y_line + 40, color=col, sw=1.5, dash="3,3"))

    # Блоки опису операційних фаз унизу
    y_boxes = 195
    h_b = 270
    w_b = 200
    gap_b = 18
    start_bx = 40

    box_data = [
        ("Фаза 1: Прийом (Intake)", [
            "• Автоматична декрипція PGP",
            "• Перевірка дублікатів",
            "• Відсіювання спаму сканерів",
            "• Відкриття приватного тікета",
            "• Відправка Researcher ID"
        ], "#eaf2f8", NEG),
        ("Фаза 2: Відтворення (Triage)", [
            "• Підняття вразливої конфігурації",
            "• Перевірка експлуатабельності",
            "• Розрахунок базового CVSS v3.1",
            "• Призначення інженера-власника",
            "• Погодження скоупу впливу"
        ], "#f4ecf7", "#8e44ad"),
        ("Фаза 3: Виправлення (Remediation)", [
            "• Розробка ізольованого патчу",
            "• Backport на підтримувані LTS",
            "• Статичний та динамічний аудит",
            "• Строки за рівнем загрози:",
            "  - Critical: <= 14 днів",
            "  - High: <= 30 днів",
            "  - Med / Low: <= 60–90 днів"
        ], "#fdedec", POS),
        ("Фаза 4: Публікація (Release)", [
            "• Отримання номера CVE у CNA",
            "• Узгодження тексту Advisory",
            "• Одночасний випуск патчу й опису",
            "• Оновлення Hall of Fame",
            "• Нарахування винагороди"
        ], "#eafaf1", FIELD)
    ]

    for i, (b_title, b_lines, bg_c, strk_c) in enumerate(box_data):
        bx = start_bx + i * (w_b + gap_b)
        p.append(rect(bx, y_boxes, w_b, h_b, fill=bg_c, stroke=strk_c, sw=1.4, rx=6))
        p.append(rect(bx + 6, y_boxes + 6, w_b - 12, 28, fill="#ffffff", stroke=strk_c, sw=1, rx=4))
        p.append(text(bx + w_b/2, y_boxes + 25, b_title, size=10.5, color=strk_c, bold=True))

        for j, ln in enumerate(b_lines):
            is_bold = "Critical" in ln or "High" in ln
            p.append(text(bx + 10, y_boxes + 55 + j * 26, ln, size=9.5, color=INK, anchor="start", bold=is_bold))

    render(os.path.join(OUT, "psirt-triage-lifecycle.svg"), W, H, *p,
           title="Хронологія тріажу вразливості в PSIRT: таймери та межі SLA")


# ── Фігура 4: Межі Safe Harbor: Що дозволено й заборонено ───────────────────
def fig_safe_harbor_boundaries():
    W, H = 940, 500
    p = []

    p.append(text(W/2, 32, "Правові та технічні межі Safe Harbor: Дозволене та Заборонене", size=16, color=INK, bold=True))

    col_w = 425
    h_col = 415
    y_top = 58

    # Ліва колонка: In-Scope / Дозволені дії (Зелена)
    x_l = 30
    p.append(rect(x_l, y_top, col_w, h_col, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    p.append(rect(x_l + 12, y_top + 12, col_w - 24, 34, fill="#27ae60", stroke=FIELD, sw=1, rx=4))
    p.append(text(x_l + col_w/2, y_top + 34, "ДОЗВОЛЕНО / В МЕЖАХ ЗАХИСТУ (IN-SCOPE)", size=12, color="#ffffff", bold=True))

    in_scope_items = [
        ("Авторизовані цілі й сервіси", [
            "• Домени, API-шлюзи та мобільні додатки, явно вказані у VDP.",
            "• Прошивки власних фізичних пристроїв користувача."
        ]),
        ("Добросовісні методи дослідження", [
            "• Створення тестових акаунтів для перевірки розмежування прав.",
            "• Демонстрація виконання коду за допомогою безпечних команд",
            "  (наприклад, id, whoami, читання власного тестового запису).",
            "• Аналіз бінарного коду та реверс-інжиніринг прошивки."
        ]),
        ("Юридичні гарантії Safe Harbor", [
            "• Відмова компанії від позовів щодо несанкціонованого доступу.",
            "• Неподання скарг за статтями про злам комп'ютерних систем.",
            "• Дозвіл на обхід технічних засобів захисту (DMCA Safe Harbor)."
        ])
    ]

    y_cur = y_top + 60
    for block_title, lines_arr in in_scope_items:
        p.append(text(x_l + 16, y_cur, block_title, size=11, color="#196f3d", bold=True, anchor="start"))
        y_cur += 18
        for itm in lines_arr:
            p.append(text(x_l + 16, y_cur, itm, size=9.5, color=INK, anchor="start"))
            y_cur += 18
        y_cur += 8

    # Права колонка: Out-of-Scope / Заборонені дії (Червона)
    x_r = 485
    p.append(rect(x_r, y_top, col_w, h_col, fill="#fdedec", stroke=POS, sw=1.8, rx=8))
    p.append(rect(x_r + 12, y_top + 12, col_w - 24, 34, fill="#c0392b", stroke=POS, sw=1, rx=4))
    p.append(text(x_r + col_w/2, y_top + 34, "СУВОРО ЗАБОРОНЕНО (OUT-OF-SCOPE / ЗЛАМ)", size=12, color="#ffffff", bold=True))

    out_scope_items = [
        ("Руйнівні та деструктивні атаки", [
            "• Атаки типу «Відмова в обслуговуванні» (DoS/DDoS) або стрес-тести.",
            "• Знищення, підміна чи видалення реальних даних користувачів.",
            "• Масове вивантаження конфіденційної інформації (Data Exfiltration)."
        ]),
        ("Атаки на людей та треті сторони", [
            "• Соціальна інженерія, фішинг або підкуп співробітників компанії.",
            "• Фізичне проникнення в офіси, дата-центри або складські приміщення.",
            "• Дослідження сторонніх хмарних провайдерів (AWS, Azure, SaaS)."
        ]),
        ("Шантаж та недобросовісна поведінка", [
            "• Вимагання викупу чи погрози передчасного зливу 0-day.",
            "• Продаж інформації про вразливість брокерам експлойтів на чорному ринку.",
            "• Публікація деталей вади до закінчення погодженого терміну розкриття."
        ])
    ]

    y_cur = y_top + 60
    for block_title, lines_arr in out_scope_items:
        p.append(text(x_r + 16, y_cur, block_title, size=11, color="#922b21", bold=True, anchor="start"))
        y_cur += 18
        for itm in lines_arr:
            p.append(text(x_r + 16, y_cur, itm, size=9.5, color=INK, anchor="start"))
            y_cur += 18
        y_cur += 8

    render(os.path.join(OUT, "safe-harbor-boundaries.svg"), W, H, *p,
           title="Правові та технічні межі Safe Harbor: Дозволене та Заборонене")


if __name__ == "__main__":
    fig_vulnerability_reporting_flow()
    fig_security_txt_structure()
    fig_psirt_triage_lifecycle()
    fig_safe_harbor_boundaries()
    print("Всі 4 фігури згенеровано успішно.")
