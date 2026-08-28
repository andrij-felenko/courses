# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра канону
LEGAL_BLUE = "#1f497d"
LEGAL_BG = "#eef4fb"
COPYLEFT_GREEN = "#236932"
COPYLEFT_BG = "#eaf5ec"
COMMERCIAL_ORANGE = "#a64b18"
COMMERCIAL_BG = "#fcf0e8"
FAIL_RED = "#9c2626"
FAIL_BG = "#fbeeed"
PURPLE = "#5b328a"
PURPLE_BG = "#f4eefb"

def polygon(points, fill=LINE, stroke="none", sw=0):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts, fill, stroke, sw)

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    extra = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, extra)


# ── 1. dco-vs-cla-ip-flow: Потоки прав інтелектуальної власності ──────────────
def fig_dco_vs_cla_ip_flow():
    W, H = 900, 500
    p = []

    p.append(text(W / 2, 28, "Порівняння розподілу прав: DCO vs CLA vs Передача прав (FSF)", size=15, color=INK, bold=True))

    col_w = 265
    col_gap = 25
    x0 = 35

    # Колонка 1: DCO
    x = x0
    p.append(rect(x, 55, col_w, 415, fill=COPYLEFT_BG, stroke=COPYLEFT_GREEN, sw=1.8, rx=10))
    p.append(text(x + col_w / 2, 82, "DCO (Signed-off-by)", size=13, color=COPYLEFT_GREEN, bold=True))
    p.append(text(x + col_w / 2, 100, "Децентралізована модель", size=10, color=MUTED, italic=True))
    p.append(line(x + 15, 112, x + col_w - 15, 112, color=COPYLEFT_GREEN, sw=1, dash="4 3"))

    # Блок автора DCO
    p.append(rect(x + 15, 125, col_w - 30, 75, fill=BG, stroke=COPYLEFT_GREEN, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 148, "Розробник (Автор)", size=11.5, color=INK, bold=True))
    p.append(text(x + col_w / 2, 168, "Зберігає 100% майнових прав", size=10, color=COPYLEFT_GREEN, bold=True))
    p.append(text(x + col_w / 2, 185, "Підтверджує чистоту походження", size=10, color=MUTED))

    # Стрілка
    p.append(line(x + col_w / 2, 200, x + col_w / 2, 238, color=COPYLEFT_GREEN, sw=2))
    p.append(polygon([(x + col_w / 2, 248), (x + col_w / 2 - 5, 238), (x + col_w / 2 + 5, 238)], fill=COPYLEFT_GREEN))
    p.append(text(x + col_w / 2 + 8, 224, "Ліцензія проєкту", size=10, color=COPYLEFT_GREEN, anchor="start", bold=True))

    # Блок проєкту DCO
    p.append(rect(x + 15, 250, col_w - 30, 90, fill=BG, stroke=COPYLEFT_GREEN, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 273, "Спільний репозиторій", size=11.5, color=INK, bold=True))
    p.append(text(x + col_w / 2, 293, "Мозаїка з тисяч копірайтів", size=10, color=INK))
    p.append(text(x + col_w / 2, 310, "Зміна ліцензії: вимагає 100%", size=10, color=FAIL_RED, bold=True))
    p.append(text(x + col_w / 2, 326, "згоди всіх контриб'юторів", size=10, color=FAIL_RED))

    # Підсумок DCO
    p.append(rect(x + 15, 355, col_w - 30, 95, fill="#e1f0e4", stroke=COPYLEFT_GREEN, sw=1, rx=6))
    p.append(text(x + col_w / 2, 376, "Властивості для бізнесу:", size=10, color=COPYLEFT_GREEN, bold=True))
    p.append(text(x + 25, 396, "• Нульовий юридичний бар'єр", size=10, color=INK, anchor="start"))
    p.append(text(x + 25, 414, "• Неможливо закрити код", size=10, color=INK, anchor="start"))
    p.append(text(x + 25, 432, "• Приклади: Linux, CNCF, Git", size=10, color=MUTED, anchor="start"))


    # Колонка 2: CLA
    x = x0 + col_w + col_gap
    p.append(rect(x, 55, col_w, 415, fill=COMMERCIAL_BG, stroke=COMMERCIAL_ORANGE, sw=1.8, rx=10))
    p.append(text(x + col_w / 2, 82, "CLA (Contributor Agreement)", size=13, color=COMMERCIAL_ORANGE, bold=True))
    p.append(text(x + col_w / 2, 100, "Централізоване ліцензування", size=10, color=MUTED, italic=True))
    p.append(line(x + 15, 112, x + col_w - 15, 112, color=COMMERCIAL_ORANGE, sw=1, dash="4 3"))

    # Блок автора CLA
    p.append(rect(x + 15, 125, col_w - 30, 75, fill=BG, stroke=COMMERCIAL_ORANGE, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 148, "Розробник (Автор)", size=11.5, color=INK, bold=True))
    p.append(text(x + col_w / 2, 168, "Зберігає формальний копірайт", size=10, color=INK))
    p.append(text(x + col_w / 2, 185, "Але підписує безвідкличну CLA", size=10, color=COMMERCIAL_ORANGE, bold=True))

    # Стрілка
    p.append(line(x + col_w / 2, 200, x + col_w / 2, 238, color=COMMERCIAL_ORANGE, sw=2))
    p.append(polygon([(x + col_w / 2, 248), (x + col_w / 2 - 5, 238), (x + col_w / 2 + 5, 238)], fill=COMMERCIAL_ORANGE))
    p.append(text(x + col_w / 2 + 8, 224, "Широкі права реліцензування", size=10, color=COMMERCIAL_ORANGE, anchor="start", bold=True))

    # Блок вендора CLA
    p.append(rect(x + 15, 250, col_w - 30, 90, fill=BG, stroke=COMMERCIAL_ORANGE, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 273, "Власник проєкту (Вендор/Фонд)", size=11, color=INK, bold=True))
    p.append(text(x + col_w / 2, 293, "Має право змінювати ліцензію", size=10, color=COMMERCIAL_ORANGE, bold=True))
    p.append(text(x + col_w / 2, 310, "Може продавати закриті ліцензії", size=10, color=INK))
    p.append(text(x + col_w / 2, 326, "чи перевести код на BSL/SSPL", size=10, color=MUTED))

    # Підсумок CLA
    p.append(rect(x + 15, 355, col_w - 30, 95, fill="#fae6d8", stroke=COMMERCIAL_ORANGE, sw=1, rx=6))
    p.append(text(x + col_w / 2, 376, "Властивості для бізнесу:", size=10, color=COMMERCIAL_ORANGE, bold=True))
    p.append(text(x + 25, 396, "• Дозволяє подвійне ліцензування", size=10, color=INK, anchor="start"))
    p.append(text(x + 25, 414, "• Високий бар'єр для контриб'юторів", size=10, color=FAIL_RED, anchor="start"))
    p.append(text(x + 25, 432, "• Приклади: Apache, Canonical, Meta", size=10, color=MUTED, anchor="start"))


    # Колонка 3: FSF Copyright Assignment
    x = x0 + (col_w + col_gap) * 2
    p.append(rect(x, 55, col_w, 415, fill=LEGAL_BG, stroke=LEGAL_BLUE, sw=1.8, rx=10))
    p.append(text(x + col_w / 2, 82, "Copyright Assignment (FSF)", size=13, color=LEGAL_BLUE, bold=True))
    p.append(text(x + col_w / 2, 100, "Повна передача майнових прав", size=10, color=MUTED, italic=True))
    p.append(line(x + 15, 112, x + col_w - 15, 112, color=LEGAL_BLUE, sw=1, dash="4 3"))

    # Блок автора FSF
    p.append(rect(x + 15, 125, col_w - 30, 75, fill=BG, stroke=LEGAL_BLUE, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 148, "Розробник (Автор)", size=11.5, color=INK, bold=True))
    p.append(text(x + col_w / 2, 168, "Відчужує майнові права", size=10, color=FAIL_RED, bold=True))
    p.append(text(x + col_w / 2, 185, "Лишається лише авторство", size=10, color=MUTED))

    # Стрілка
    p.append(line(x + col_w / 2, 200, x + col_w / 2, 238, color=LEGAL_BLUE, sw=2))
    p.append(polygon([(x + col_w / 2, 248), (x + col_w / 2 - 5, 238), (x + col_w / 2 + 5, 238)], fill=LEGAL_BLUE))
    p.append(text(x + col_w / 2 + 8, 224, "Юридичне відчуження прав", size=10, color=LEGAL_BLUE, anchor="start", bold=True))

    # Блок FSF
    p.append(rect(x + 15, 250, col_w - 30, 90, fill=BG, stroke=LEGAL_BLUE, sw=1.2, rx=6))
    p.append(text(x + col_w / 2, 273, "Єдиний власник (FSF / Фонд)", size=11, color=INK, bold=True))
    p.append(text(x + col_w / 2, 293, "100% копірайту в одних руках", size=10, color=LEGAL_BLUE, bold=True))
    p.append(text(x + col_w / 2, 310, "Захищає копілефт у судах", size=10, color=INK))
    p.append(text(x + col_w / 2, 326, "від імені єдиного правовласника", size=10, color=MUTED))

    # Підсумок FSF
    p.append(rect(x + 15, 355, col_w - 30, 95, fill="#e2edf8", stroke=LEGAL_BLUE, sw=1, rx=6))
    p.append(text(x + col_w / 2, 376, "Властивості для бізнесу:", size=10, color=LEGAL_BLUE, bold=True))
    p.append(text(x + 25, 396, "• Максимальний судовий захист GPL", size=10, color=INK, anchor="start"))
    p.append(text(x + 25, 414, "• Максимальна бюрократія паперів", size=10, color=FAIL_RED, anchor="start"))
    p.append(text(x + 25, 432, "• Приклади: GNU GCC, Emacs, Bash", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "dco-vs-cla-ip-flow.svg"), W, H, *p,
           title="Потоки прав інтелектуальної власності: DCO vs CLA vs FSF Assignment")


# ── 2. dual-licensing-matrix: Бізнес-модель подвійного ліцензування ──────────
def fig_dual_licensing_matrix():
    W, H = 880, 480
    p = []

    p.append(text(W / 2, 28, "Архітектура подвійного ліцензування: Копілефтний важіль (Dual Licensing)", size=15, color=INK, bold=True))

    # Центральний вузол: єдина кодова база
    cx, cy, cw, ch = W / 2 - 170, 58, 340, 82
    p.append(rect(cx, cy, cw, ch, fill=PURPLE_BG, stroke=PURPLE, sw=2, rx=10))
    p.append(text(W / 2, cy + 25, "Єдина кодова база продукту", size=13, color=PURPLE, bold=True))
    p.append(text(W / 2, cy + 46, "100% майнових прав належить вендору", size=10.5, color=INK, bold=True))
    p.append(text(W / 2, cy + 65, "(Власний штат + обов'язкова CLA для контриб'юторів)", size=10, color=MUTED, italic=True))

    # Дві розбіжні стрілки вниз
    p.append(path("M 350 140 L 220 200", stroke=COPYLEFT_GREEN, sw=2.5, fill="none"))
    p.append(polygon([(215, 203), (228, 197), (222, 190)], fill=COPYLEFT_GREEN))
    p.append(text(210, 160, "Гілка 1: Відкритий випуск", size=10.5, color=COPYLEFT_GREEN, bold=True))

    p.append(path("M 530 140 L 660 200", stroke=COMMERCIAL_ORANGE, sw=2.5, fill="none"))
    p.append(polygon([(665, 203), (658, 190), (652, 197)], fill=COMMERCIAL_ORANGE))
    p.append(text(670, 160, "Гілка 2: Комерційний випуск", size=10.5, color=COMMERCIAL_ORANGE, bold=True))

    # Ліва колонка: Open Source Copyleft
    lx, lw = 35, 380
    p.append(rect(lx, 210, lw, 245, fill=COPYLEFT_BG, stroke=COPYLEFT_GREEN, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, 235, "Строга копілефтна ліцензія (GPLv3 / AGPLv3)", size=12, color=COPYLEFT_GREEN, bold=True))
    p.append(line(lx + 15, 248, lx + lw - 15, 248, color=COPYLEFT_GREEN, sw=1, dash="4 3"))

    items_left = [
        ("Ціна:", "0 грн (Безкоштовно у вихідному коді)"),
        ("Умова взаємності:", "Увесь похідний код мусить бути відкритим під GPL"),
        ("Мережевий ефект (AGPL):", "Використання як SaaS вимагає відкриття бекенду"),
        ("Цільова аудиторія:", "Опенсорс-спільнота, науковці, некомерційні проєкти"),
        ("Бізнес-ефект:", "Створює широке визнання та формує ринковий стандарт")
    ]
    for i, (k, v) in enumerate(items_left):
        yy = 268 + i * 35
        p.append(text(lx + 18, yy, k, size=10, color=COPYLEFT_GREEN, bold=True, anchor="start"))
        p.append(text(lx + 18, yy + 14, v, size=9.5, color=INK, anchor="start"))

    # Права колонка: Commercial OEM
    rx, rw = W - 35 - 380, 380
    p.append(rect(rx, 210, rw, 245, fill=COMMERCIAL_BG, stroke=COMMERCIAL_ORANGE, sw=1.8, rx=10))
    p.append(text(rx + rw / 2, 235, "Комерційна ліцензія (Proprietary OEM / SaaS)", size=12, color=COMMERCIAL_ORANGE, bold=True))
    p.append(line(rx + 15, 248, rx + rw - 15, 248, color=COMMERCIAL_ORANGE, sw=1, dash="4 3"))

    items_right = [
        ("Ціна:", "Платна підписка або роялті за кожну копію"),
        ("Звільнення від GPL:", "Дозвіл вбудовувати у закриті пропрієтарні пристрої"),
        ("Комерційна таємниця:", "Немає зобов'язання оприлюднювати власний код"),
        ("Цільова аудиторія:", "Корпорації, вендори заліза, хмарні провайдери"),
        ("Бізнес-ефект:", "Пряма монетизація розробки компанії-власника")
    ]
    for i, (k, v) in enumerate(items_right):
        yy = 268 + i * 35
        p.append(text(rx + 18, yy, k, size=10, color=COMMERCIAL_ORANGE, bold=True, anchor="start"))
        p.append(text(rx + 18, yy + 14, v, size=9.5, color=INK, anchor="start"))

    # Міст-важіль між ними
    p.append(rect(W / 2 - 50, 315, 100, 52, fill=FAIL_BG, stroke=FAIL_RED, sw=1.5, rx=6))
    p.append(text(W / 2, 332, "Копілефтний важіль", size=9.5, color=FAIL_RED, bold=True))
    p.append(text(W / 2, 347, "Хто не ділиться кодом,", size=9, color=INK))
    p.append(text(W / 2, 359, "той купує OEM", size=9, color=FAIL_RED, bold=True))

    render(os.path.join(OUT, "dual-licensing-matrix.svg"), W, H, *p,
           title="Матриця подвійного ліцензування: копілефт та комерційні винятки")


# ── 3. sco-linux-provenance-chain: Ланцюг походження коду в Linux ─────────────
def fig_sco_linux_provenance_chain():
    W, H = 860, 440
    p = []

    p.append(text(W / 2, 26, "Ланцюг перевіреного походження коду (DCO Provenance Chain) в ядрі Linux", size=14, color=INK, bold=True))

    nodes = [
        ("1. Автор патча", "Розробник (Contributor)", "Signed-off-by: Ivan Petrenko <ivan@dev.org>", "Стверджує DCO 1.1: код власний або з чистою відкритою ліцензією"),
        ("2. Мейнтейнер драйвера", "Subsystem Maintainer", "Signed-off-by: Driver Lead <lead@kernel.org>", "Перевірив архітектуру та юридичну здатність автора передавати код"),
        ("3. Керівник підсистеми", "Area Maintainer (Greg K-H)", "Signed-off-by: Greg K-H <gregkh@kernel.org>", "Інтегрує в підсистему (USB/PCI) та підтверджує перевірений ланцюг"),
        ("4. Головний мейнтейнер", "Linus Torvalds", "Signed-off-by: Linus Torvalds <torvalds@osdl.org>", "Фінальне злиття в upstream master; незламний юридичний аудит-трейл")
    ]

    bw = 780
    bh = 66
    bx = 40

    for i, (step, title, sign, desc) in enumerate(nodes):
        by = 55 + i * 92
        p.append(rect(bx, by, bw, bh, fill=LEGAL_BG if i < 3 else COPYLEFT_BG,
                      stroke=LEGAL_BLUE if i < 3 else COPYLEFT_GREEN, sw=1.6, rx=8))
        
        # Бейдж кроку
        p.append(rect(bx + 12, by + 12, 160, 42, fill=BG, stroke=LEGAL_BLUE if i < 3 else COPYLEFT_GREEN, sw=1.2, rx=5))
        p.append(text(bx + 92, by + 28, step, size=10.5, color=INK, bold=True))
        p.append(text(bx + 92, by + 44, title, size=9.5, color=MUTED))

        # Трейлер і опис
        p.append(text(bx + 190, by + 28, sign, size=10.5, color=PURPLE, bold=True, anchor="start"))
        p.append(text(bx + 190, by + 48, desc, size=10, color=INK, anchor="start"))

        # Стрілка до наступного блоку
        if i < 3:
            sy = by + bh
            p.append(line(W / 2, sy, W / 2, sy + 22, color=LEGAL_BLUE, sw=2))
            p.append(polygon([(W / 2, sy + 25), (W / 2 - 5, sy + 17), (W / 2 + 5, sy + 17)], fill=LEGAL_BLUE))

    render(os.path.join(OUT, "sco-linux-provenance-chain.svg"), W, H, *p,
           title="Ланцюг походження DCO Signed-off-by в ядрі Linux")


# ── 4. dco-ci-verification-pipeline: Конвеєр CI для перевірки DCO ────────────
def fig_dco_ci_verification_pipeline():
    W, H = 900, 470
    p = []

    p.append(text(W / 2, 26, "Автоматизований конвеєр перевірки DCO та підписів у CI/CD", size=14, color=INK, bold=True))

    # Крок 1: Відкриття PR
    x1, y1, w1, h1 = 30, 75, 175, 120
    p.append(rect(x1, y1, w1, h1, fill=BG, stroke=INK, sw=1.5, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 24, "1. Pull Request / Push", size=11, color=INK, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 44, "Webhook надсилає подію", size=9.5, color=MUTED))
    p.append(text(x1 + w1 / 2, y1 + 64, "Список нових комітів", size=9.5, color=INK))
    p.append(text(x1 + w1 / 2, y1 + 84, "GIT_AUTHOR_EMAIL", size=9.5, color=PURPLE, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 104, "Тіло commit message", size=9.5, color=PURPLE))

    # Стрілка 1 -> 2
    p.append(line(x1 + w1, y1 + h1 / 2, x1 + w1 + 35, y1 + h1 / 2, color=INK, sw=1.8))
    p.append(polygon([(x1 + w1 + 40, y1 + h1 / 2), (x1 + w1 + 32, y1 + h1 / 2 - 4), (x1 + w1 + 32, y1 + h1 / 2 + 4)], fill=INK))

    # Крок 2: DCO Verifier Bot
    x2, y2, w2, h2 = x1 + w1 + 40, 60, 290, 150
    p.append(rect(x2, y2, w2, h2, fill=PURPLE_BG, stroke=PURPLE, sw=2, rx=10))
    p.append(text(x2 + w2 / 2, y2 + 25, "2. DCO Verifier Engine (CI Bot)", size=12, color=PURPLE, bold=True))
    p.append(line(x2 + 15, y2 + 35, x2 + w2 - 15, y2 + 35, color=PURPLE, sw=1, dash="3 2"))
    checks = [
        "• Парсинг трейлерів git interpret-trailers",
        "• Вилучення рядка Signed-off-by: Name <email>",
        "• Перевірка: Email автора == Email у Sign-off",
        "• Валідація співавторів Co-authored-by",
        "• Перевірка криптографічного GPG-підпису"
    ]
    for i, c in enumerate(checks):
        p.append(text(x2 + 16, y2 + 54 + i * 18, c, size=9.5, color=INK, anchor="start"))

    # Розгалуження результату
    # Вгору-вправо -> Успіх
    p.append(path("M 535 110 L 600 110 L 600 100 L 650 100", stroke=COPYLEFT_GREEN, sw=2, fill="none"))
    p.append(polygon([(655, 100), (647, 96), (647, 104)], fill=COPYLEFT_GREEN))
    p.append(text(595, 88, "Коміти валідні", size=9.5, color=COPYLEFT_GREEN, bold=True))

    # Вниз-вправо -> Помилка
    p.append(path("M 535 160 L 600 160 L 600 270 L 650 270", stroke=FAIL_RED, sw=2, fill="none"))
    p.append(polygon([(655, 270), (647, 266), (647, 274)], fill=FAIL_RED))
    p.append(text(595, 215, "Порушення DCO", size=9.5, color=FAIL_RED, bold=True))

    # Крок 3A: Успіх (Green Check)
    x3a, y3a, w3a, h3a = 655, 50, 215, 115
    p.append(rect(x3a, y3a, w3a, h3a, fill=COPYLEFT_BG, stroke=COPYLEFT_GREEN, sw=1.8, rx=8))
    p.append(text(x3a + w3a / 2, y3a + 25, "3A. Статус: УСПІШНО", size=11, color=COPYLEFT_GREEN, bold=True))
    p.append(text(x3a + w3a / 2, y3a + 48, "Зелений чек у GitHub/GitLab", size=10, color=INK))
    p.append(text(x3a + w3a / 2, y3a + 68, "Комплаєнс підтверджено", size=9.5, color=MUTED))
    p.append(text(x3a + w3a / 2, y3a + 90, "Дозвіл на злиття (Merge Allowed)", size=10, color=COPYLEFT_GREEN, bold=True))

    # Крок 3B: Блокування (Red X)
    x3b, y3b, w3b, h3b = 655, 215, 215, 140
    p.append(rect(x3b, y3b, w3b, h3b, fill=FAIL_BG, stroke=FAIL_RED, sw=1.8, rx=8))
    p.append(text(x3b + w3b / 2, y3b + 25, "3B. Статус: ЗАБЛОКОВАНО", size=11, color=FAIL_RED, bold=True))
    p.append(text(x3b + w3b / 2, y3b + 46, "Червоний хрестик у PR", size=10, color=INK))
    p.append(text(x3b + w3b / 2, y3b + 66, "Бот публікує інструкцію виправлення:", size=9.5, color=FAIL_RED))
    p.append(text(x3b + w3b / 2, y3b + 88, "git commit --amend -s", size=9.5, color=PURPLE, bold=True))
    p.append(text(x3b + w3b / 2, y3b + 106, "git push --force-with-lease", size=9.5, color=PURPLE, bold=True))
    p.append(text(x3b + w3b / 2, y3b + 125, "Merge заблоковано до фіксу", size=9.5, color=FAIL_RED))

    # Нижня інформаційна панель
    p.append(rect(30, 375, W - 60, 75, fill="#f8f9fa", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(50, 398, "Чому перевірку DCO виконують автоматично в CI:", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(50, 418, "• Усуває людський фактор: рецензент не забуде перевірити юридичний підпис серед 50 файлів коду.", size=10, color=MUTED, anchor="start"))
    p.append(text(50, 436, "• Захищає репозиторій від потрапляння неліцензованого або чужого закритого коду на етапі шлюзу злиття.", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "dco-ci-verification-pipeline.svg"), W, H, *p,
           title="Конвеєр автоматизованої перевірки DCO та комплаєнсу у CI/CD")


if __name__ == "__main__":
    fig_dco_vs_cla_ip_flow()
    fig_dual_licensing_matrix()
    fig_sco_linux_provenance_chain()
    fig_dco_ci_verification_pipeline()
    print("Всі фігури згенеровано успішно у ./img")
